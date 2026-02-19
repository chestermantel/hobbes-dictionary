#!/usr/bin/env python3
"""Build the Hobbes Dictionary website from hobbes_dictionary.csv -> index.html"""

import csv, json, re, os

BASE = "/Users/Chester2/Documents/Documents/projects/HobbesDictionary"

def make_slug(term):
    s = term.lower()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'\s+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')

entries = []
with open(f"{BASE}/hobbes_dictionary.csv", encoding='utf-8') as f:
    for row in csv.DictReader(f):
        entries.append({
            'term':        row['term'],
            'slug':        make_slug(row['term']),
            'definition':  row['definition'],
            'chapter':     row['chapter'],
            'page_number': row['page_number'],
            'cross_refs':  [r.strip() for r in row['cross_refs'].split(';') if r.strip()],
            'context':     row['context'],
        })

data_json = json.dumps({'entries': entries}, ensure_ascii=False)

# ── HTML ─────────────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hobbes Dictionary — Leviathan</title>
  <style>
    :root {
      --parchment:    #faf8f3;
      --parchment-dk: #f0ebe0;
      --navy:         #1e2d4a;
      --navy-lt:      #2a4068;
      --brown:        #7a3e20;
      --brown-lt:     #a05a38;
      --text:         #2a1f1a;
      --text-lt:      #5a4a40;
      --border:       #d4c4a8;
      --border-dk:    #b8a888;
      --gold:         #c8a84a;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: Georgia, 'Times New Roman', serif;
      background: var(--parchment);
      color: var(--text);
      min-height: 100vh;
    }

    /* ── Header ── */
    header {
      background: var(--navy);
      color: white;
      position: sticky; top: 0; z-index: 100;
      box-shadow: 0 2px 8px rgba(0,0,0,.35);
    }
    .header-inner {
      max-width: 960px; margin: 0 auto;
      padding: 0 1.5rem;
      display: flex; align-items: center; height: 54px; gap: 1rem;
    }
    .site-title {
      font-size: 1rem; font-weight: normal;
      letter-spacing: .06em; color: var(--gold);
      white-space: nowrap; text-decoration: none;
    }
    .site-title:hover { color: #fff; }
    .header-sep { color: #3a5070; flex-shrink: 0; }
    .breadcrumb {
      display: flex; align-items: center; gap: .4rem;
      font-size: .8rem; color: #8899aa; flex-wrap: wrap;
    }
    .breadcrumb a { color: #aabbcc; text-decoration: none; }
    .breadcrumb a:hover { color: #fff; text-decoration: underline; }
    .breadcrumb .sep { color: #4a6080; }

    /* ── Layout ── */
    main { max-width: 960px; margin: 0 auto; padding: 2rem 1.5rem; }
    .page { display: none; }
    .page.active { display: block; }

    /* ── Typography ── */
    .page-title {
      font-size: 1.75rem; color: var(--navy); font-weight: normal;
      margin-bottom: .4rem;
    }
    .page-subtitle {
      color: var(--text-lt); font-size: .9rem; font-style: italic;
      margin-bottom: 2rem;
    }
    .back-btn {
      display: inline-flex; align-items: center; gap: .35rem;
      color: var(--text-lt); font-size: .82rem; text-decoration: none;
      margin-bottom: 1.5rem; transition: color .15s;
    }
    .back-btn:hover { color: var(--navy); }

    /* ── Book cards ── */
    .book-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 1rem; margin-top: 1rem;
    }
    .book-card {
      background: white; border: 1px solid var(--border);
      border-top: 4px solid var(--navy);
      padding: 1.2rem; text-decoration: none; display: block;
      transition: all .2s;
    }
    .book-card:not(.disabled):hover {
      border-top-color: var(--brown);
      box-shadow: 0 4px 14px rgba(0,0,0,.12);
      transform: translateY(-2px);
    }
    .book-card.disabled { opacity: .42; cursor: default; }
    .book-card h3 { font-size: 1rem; color: var(--navy); margin-bottom: .3rem; }
    .book-card .book-sub { font-size: .8rem; color: var(--text-lt); font-style: italic; }
    .book-card .book-count { font-size: .75rem; color: var(--navy-lt); margin-top: .6rem; }

    /* ── Chapter grid ── */
    .chapter-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
      gap: .6rem;
    }
    .chapter-card {
      background: white; border: 1px solid var(--border);
      border-left: 3px solid var(--navy);
      padding: .85rem 1rem; text-decoration: none;
      display: flex; align-items: baseline; gap: .65rem;
      transition: all .15s;
    }
    .chapter-card:hover { border-left-color: var(--brown); background: var(--parchment-dk); }
    .chapter-num { font-size: .72rem; color: var(--text-lt); min-width: 2.8rem; font-style: italic; }
    .chapter-title { flex: 1; font-size: .88rem; color: var(--navy); }
    .chapter-count {
      font-size: .72rem; color: var(--text-lt);
      background: var(--parchment-dk); padding: .1rem .45rem;
      border-radius: 10px; white-space: nowrap;
    }

    /* ── Definition list ── */
    .def-list { list-style: none; }
    .def-item {
      background: white; border: 1px solid var(--border);
      border-left: 3px solid transparent;
      margin-bottom: .45rem; padding: .7rem 1rem;
      text-decoration: none; display: block;
      transition: all .15s;
    }
    .def-item:hover { border-left-color: var(--brown); background: var(--parchment-dk); }
    .def-term { font-size: .95rem; color: var(--navy); font-weight: bold; }
    .def-preview {
      font-size: .78rem; color: var(--text-lt); margin-top: .2rem;
      font-style: italic; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }

    /* ── Term detail ── */
    .def-detail { max-width: 700px; }
    .term-heading {
      font-size: 2rem; color: var(--navy); font-weight: normal;
      border-bottom: 2px solid var(--border); padding-bottom: .5rem;
      margin-bottom: 1.25rem;
    }

    /* one definition block */
    .def-block { margin-bottom: 2rem; }
    .def-block + .def-block {
      border-top: 1px solid var(--border); padding-top: 1.75rem;
    }
    .def-chapter-label {
      font-size: .78rem; color: var(--text-lt); margin-bottom: .9rem;
      display: flex; gap: 1.2rem; flex-wrap: wrap;
    }
    .def-chapter-label a { color: var(--navy-lt); text-decoration: none; }
    .def-chapter-label a:hover { text-decoration: underline; }
    .def-body {
      font-size: 1.05rem; line-height: 1.8; color: var(--text);
      margin-bottom: 1rem;
    }
    .def-body a.term-link {
      color: var(--brown); text-decoration: underline;
      text-decoration-style: dotted; text-decoration-color: #c09a80;
    }
    .def-body a.term-link:hover {
      text-decoration-style: solid; color: var(--brown-lt);
    }
    .def-context {
      background: var(--parchment-dk); border-left: 3px solid var(--border-dk);
      padding: .55rem .85rem; font-size: .82rem; color: var(--text-lt);
      font-style: italic;
    }

    /* ── See Also ── */
    .see-also { margin-top: 2rem; padding-top: 1.25rem; border-top: 1px solid var(--border); }
    .see-also h3 {
      font-size: .75rem; text-transform: uppercase; letter-spacing: .1em;
      color: var(--text-lt); margin-bottom: .65rem; font-weight: normal;
    }
    .see-also-links { display: flex; flex-wrap: wrap; gap: .45rem; }
    .see-also-link {
      display: inline-block; padding: .28rem .65rem;
      background: white; border: 1px solid var(--border-dk);
      color: var(--navy); text-decoration: none; font-size: .8rem;
      border-radius: 2px; transition: all .15s;
    }
    .see-also-link:hover { background: var(--navy); color: white; border-color: var(--navy); }

    /* ── Misc ── */
    .tag-context {
      font-size: .72rem; color: var(--text-lt);
      background: var(--parchment-dk); border: 1px solid var(--border);
      padding: .1rem .4rem; border-radius: 2px; margin-left: .4rem;
    }
    .empty { text-align: center; color: var(--text-lt); padding: 3rem; font-style: italic; }
    @media (max-width: 600px) {
      main { padding: 1rem; }
      .chapter-grid { grid-template-columns: 1fr; }
      .term-heading { font-size: 1.5rem; }
    }
  </style>
</head>
<body>

<header>
  <div class="header-inner">
    <a class="site-title" href="#/">Hobbes Dictionary</a>
    <span class="header-sep">|</span>
    <nav class="breadcrumb" id="breadcrumb"></nav>
  </div>
</header>

<main>
  <div id="page-home"    class="page"></div>
  <div id="page-book"    class="page"></div>
  <div id="page-chapter" class="page"></div>
  <div id="page-term"    class="page"></div>
</main>

<script>
// ── Data ─────────────────────────────────────────────────────────────────────
const DATA = DATAPLACEHOLDER;

const CHAPTER_ORDER = ['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV','XVI'];

function chapterIdx(ch) {
  const m = ch.match(/Chapter ([IVXLCDM]+):/);
  return m ? CHAPTER_ORDER.indexOf(m[1]) : 99;
}
function chapterRoman(ch) {
  const m = ch.match(/Chapter ([IVXLCDM]+):/); return m ? m[1] : '';
}
function chapterTitle(ch) {
  const m = ch.match(/Chapter [IVXLCDM]+: (.+)/); return m ? m[1] : ch;
}
function makeSlug(t) {
  return t.toLowerCase().replace(/[^\w\s-]/g,'').replace(/\s+/g,'-').replace(/-+/g,'-').replace(/^-|-$/g,'');
}
function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function escRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'); }

// ── Indexes ──────────────────────────────────────────────────────────────────
// slug → [entries] (may have multiple definitions per term)
const slugIndex = {};
// chapter string → [entries] in original CSV order
const chapters = {};

for (const e of DATA.entries) {
  if (!slugIndex[e.slug]) slugIndex[e.slug] = [];
  slugIndex[e.slug].push(e);
  if (!chapters[e.chapter]) chapters[e.chapter] = [];
  chapters[e.chapter].push(e);
}

const sortedChapters = Object.keys(chapters).sort((a,b) => chapterIdx(a) - chapterIdx(b));

// ── Routing ───────────────────────────────────────────────────────────────────
function navigate(path) { window.location.hash = '#' + path; }

window.addEventListener('hashchange', render);
window.addEventListener('DOMContentLoaded', render);

function render() {
  const hash = window.location.hash.slice(1) || '/';
  const parts = hash.split('/').filter(Boolean);
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

  if (!parts.length || parts[0] === '') return showHome();
  if (parts[0] === 'book')    return showBook(parts[1] || 'I');
  if (parts[0] === 'chapter') return showChapter(decodeURIComponent(parts[1] || ''));
  if (parts[0] === 'term')    return showTerm(decodeURIComponent(parts.slice(1).join('/')));
  showHome();
}

// ── Pages ─────────────────────────────────────────────────────────────────────
function showHome() {
  setBreadcrumb([]);
  const p = document.getElementById('page-home');
  p.innerHTML = `
    <h1 class="page-title">Hobbes Dictionary</h1>
    <p class="page-subtitle">Definitions from <em>Leviathan</em> (1651) — Select a book</p>
    <div class="book-grid">
      <a class="book-card" href="#/book/I">
        <h3>Book I</h3>
        <p class="book-sub">Of Man</p>
        <p class="book-count">${DATA.entries.length} definitions &middot; 16 chapters</p>
      </a>
      <div class="book-card disabled">
        <h3>Book II</h3><p class="book-sub">Of Commonwealth</p>
        <p class="book-count">Upload PDF to enable</p>
      </div>
      <div class="book-card disabled">
        <h3>Book III</h3><p class="book-sub">Of a Christian Commonwealth</p>
        <p class="book-count">Upload PDF to enable</p>
      </div>
      <div class="book-card disabled">
        <h3>Book IV</h3><p class="book-sub">Of the Kingdom of Darkness</p>
        <p class="book-count">Upload PDF to enable</p>
      </div>
    </div>`;
  p.classList.add('active');
}

function showBook(book) {
  setBreadcrumb([{label:'Book I: Of Man', href:'/book/I'}]);
  const p = document.getElementById('page-book');
  p.innerHTML = `
    <a class="back-btn" href="#/">← Books</a>
    <h1 class="page-title">Book I: Of Man</h1>
    <p class="page-subtitle">${DATA.entries.length} definitions across 16 chapters</p>
    <div class="chapter-grid">
      ${sortedChapters.map(ch => `
        <a class="chapter-card" href="#/chapter/${chapterRoman(ch)}">
          <span class="chapter-num">Ch.&nbsp;${chapterRoman(ch)}</span>
          <span class="chapter-title">${esc(chapterTitle(ch))}</span>
          <span class="chapter-count">${chapters[ch].length}</span>
        </a>`).join('')}
    </div>`;
  p.classList.add('active');
}

function showChapter(roman) {
  const chStr = sortedChapters.find(c => chapterRoman(c) === roman);
  if (!chStr) return showHome();
  const entries = chapters[chStr];
  const title = chapterTitle(chStr);
  setBreadcrumb([
    {label:'Book I', href:'/book/I'},
    {label:`Ch. ${roman}: ${title}`, href:`/chapter/${roman}`}
  ]);
  const p = document.getElementById('page-chapter');
  p.innerHTML = `
    <a class="back-btn" href="#/book/I">← Book I: Of Man</a>
    <h1 class="page-title">Chapter ${roman}</h1>
    <p class="page-subtitle">${esc(title)} &middot; ${entries.length} definitions</p>
    <ul class="def-list">
      ${entries.map(e => `
        <li><a class="def-item" href="#/term/${encodeURIComponent(e.slug)}">
          <div class="def-term">${esc(e.term)}</div>
          <div class="def-preview">${esc(e.definition.slice(0,130))}${e.definition.length>130?'&hellip;':''}</div>
        </a></li>`).join('')}
    </ul>`;
  p.classList.add('active');
}

function showTerm(slug) {
  const entries = slugIndex[slug];
  if (!entries) return showHome();

  // Use first entry for breadcrumb
  const first = entries[0];
  const roman = chapterRoman(first.chapter);
  const title  = chapterTitle(first.chapter);
  setBreadcrumb([
    {label:'Book I', href:'/book/I'},
    {label:`Ch. ${roman}`, href:`/chapter/${roman}`},
    {label: first.term, href:`/term/${slug}`}
  ]);

  // Collect all unique cross_refs across all definitions of this term
  const allRefs = [...new Set(entries.flatMap(e => e.cross_refs))].sort();

  const blocksHtml = entries.map(e => {
    const chRoman = chapterRoman(e.chapter);
    const linked  = linkify(e.definition, e.cross_refs);
    return `
      <div class="def-block">
        <div class="def-chapter-label">
          <span><a href="#/chapter/${chRoman}">Chapter ${chRoman}: ${esc(chapterTitle(e.chapter))}</a></span>
          <span>Page ${esc(e.page_number)}</span>
        </div>
        <div class="def-body">${linked}</div>
        ${e.context ? `<div class="def-context">${esc(e.context)}</div>` : ''}
      </div>`;
  }).join('');

  const seeAlso = allRefs.length ? `
    <div class="see-also">
      <h3>See Also</h3>
      <div class="see-also-links">
        ${allRefs.map(ref => {
          const rs = makeSlug(ref);
          return slugIndex[rs]
            ? `<a class="see-also-link" href="#/term/${encodeURIComponent(rs)}">${esc(ref)}</a>`
            : `<span class="see-also-link" style="opacity:.4">${esc(ref)}</span>`;
        }).join('')}
      </div>
    </div>` : '';

  // If multiple definitions, show how many
  const multiNote = entries.length > 1
    ? `<p class="page-subtitle">Defined in ${entries.length} chapters</p>` : '';

  const p = document.getElementById('page-term');
  p.innerHTML = `
    <a class="back-btn" href="#/chapter/${roman}">← ${esc(title)}</a>
    <div class="def-detail">
      <h1 class="term-heading">${esc(first.term)}</h1>
      ${multiNote}
      ${blocksHtml}
      ${seeAlso}
    </div>`;
  p.classList.add('active');
  window.scrollTo(0, 0);
}

// ── Linkify ───────────────────────────────────────────────────────────────────
function linkify(text, refs) {
  if (!refs || !refs.length) return esc(text);

  // Sort longest first so multi-word terms match before their components
  const sorted = [...refs].sort((a,b) => b.length - a.length);
  const spans = [];  // {start, end, ref}

  for (const ref of sorted) {
    const rx = new RegExp('\\b' + escRe(ref) + '\\b', 'gi');
    let m;
    while ((m = rx.exec(text)) !== null) {
      const s = m.index, e = s + m[0].length;
      if (!spans.some(x => s < x.end && e > x.start)) {
        spans.push({start:s, end:e, matched:m[0], ref});
      }
    }
  }

  if (!spans.length) return esc(text);
  spans.sort((a,b) => a.start - b.start);

  let out = '', last = 0;
  for (const {start, end, matched, ref} of spans) {
    out += esc(text.slice(last, start));
    const sl = makeSlug(ref);
    if (slugIndex[sl]) {
      out += `<a class="term-link" href="#/term/${encodeURIComponent(sl)}">${esc(matched)}</a>`;
    } else {
      out += esc(matched);
    }
    last = end;
  }
  out += esc(text.slice(last));
  return out;
}

// ── Breadcrumb ────────────────────────────────────────────────────────────────
function setBreadcrumb(items) {
  const nav = document.getElementById('breadcrumb');
  if (!items.length) { nav.innerHTML = ''; return; }
  nav.innerHTML = items.map((item, i) =>
    i < items.length - 1
      ? `<a href="#${item.href}">${esc(item.label)}</a><span class="sep">›</span>`
      : `<span>${esc(item.label)}</span>`
  ).join('');
}
</script>
</body>
</html>
"""

HTML = HTML.replace('DATAPLACEHOLDER', data_json)

out_path = f"{BASE}/index.html"
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f"Built {out_path}")
print(f"  {len(entries)} entries  |  {len(set(e['slug'] for e in entries))} unique terms  |  {len(set(e['chapter'] for e in entries))} chapters")
