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
      white-space: nowrap; text-decoration: none; flex-shrink: 0;
    }
    .site-title:hover { color: #fff; }
    .header-sep { color: #3a5070; flex-shrink: 0; }
    .breadcrumb {
      display: flex; align-items: center; gap: .4rem;
      font-size: .8rem; color: #8899aa; flex-wrap: wrap; flex: 1;
      overflow: hidden;
    }
    .breadcrumb a { color: #aabbcc; text-decoration: none; white-space: nowrap; }
    .breadcrumb a:hover { color: #fff; text-decoration: underline; }
    .breadcrumb .sep { color: #4a6080; }
    .breadcrumb span { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    /* ── Search ── */
    .search-wrap {
      position: relative; flex-shrink: 0;
    }
    .search-input {
      background: rgba(255,255,255,.12);
      border: 1px solid rgba(255,255,255,.2);
      border-radius: 4px;
      color: white; font-size: .82rem; font-family: inherit;
      padding: .35rem .7rem .35rem 1.9rem;
      width: 200px; outline: none;
      transition: all .2s;
    }
    .search-input::placeholder { color: rgba(255,255,255,.4); }
    .search-input:focus {
      background: rgba(255,255,255,.18);
      border-color: rgba(255,255,255,.4);
      width: 240px;
    }
    .search-icon {
      position: absolute; left: .55rem; top: 50%; transform: translateY(-50%);
      color: rgba(255,255,255,.4); font-size: .8rem; pointer-events: none;
    }
    .search-dropdown {
      display: none;
      position: absolute; top: calc(100% + 4px); right: 0;
      background: white; border: 1px solid var(--border-dk);
      border-radius: 4px; box-shadow: 0 6px 20px rgba(0,0,0,.18);
      min-width: 300px; max-width: 400px;
      max-height: 360px; overflow-y: auto;
      z-index: 200;
    }
    .search-dropdown.open { display: block; }
    .search-result {
      display: block; padding: .55rem .85rem;
      text-decoration: none; border-bottom: 1px solid #eee;
      cursor: pointer; transition: background .1s;
    }
    .search-result:last-child { border-bottom: none; }
    .search-result:hover, .search-result.focused { background: var(--parchment-dk); }
    .sr-term { font-size: .88rem; color: var(--navy); }
    .sr-term mark { background: none; color: var(--brown); font-weight: bold; }
    .sr-chapter { font-size: .72rem; color: var(--text-lt); font-style: italic; margin-top: .1rem; }
    .search-no-results {
      padding: .7rem .85rem; font-size: .82rem; color: var(--text-lt); font-style: italic;
    }

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
      margin-bottom: .75rem;
    }
    .def-body a.term-link {
      color: var(--brown); text-decoration: underline;
      text-decoration-style: dotted; text-decoration-color: #c09a80;
    }
    .def-body a.term-link:hover {
      text-decoration-style: solid; color: var(--brown-lt);
    }
    /* Compact context — just a small footnote line */
    .def-context {
      font-size: .75rem; color: var(--text-lt); font-style: italic;
      padding-left: .75rem; border-left: 2px solid var(--border);
      line-height: 1.4;
    }

    /* ── See Also ── */
    .see-also { margin-top: 1.75rem; padding-top: 1.1rem; border-top: 1px solid var(--border); }
    .see-also h3 {
      font-size: .72rem; text-transform: uppercase; letter-spacing: .1em;
      color: var(--text-lt); margin-bottom: .6rem; font-weight: normal;
    }
    .see-also-links { display: flex; flex-wrap: wrap; gap: .4rem; }
    .see-also-link {
      display: inline-block; padding: .25rem .6rem;
      background: white; border: 1px solid var(--border-dk);
      color: var(--navy); text-decoration: none; font-size: .78rem;
      border-radius: 2px; transition: all .15s;
    }
    .see-also-link:hover { background: var(--navy); color: white; border-color: var(--navy); }

    /* ── Misc ── */
    @media (max-width: 680px) {
      main { padding: 1rem; }
      .chapter-grid { grid-template-columns: 1fr; }
      .term-heading { font-size: 1.5rem; }
      .search-input { width: 130px; }
      .search-input:focus { width: 160px; }
      .search-dropdown { min-width: 240px; }
    }
  </style>
</head>
<body>

<header>
  <div class="header-inner">
    <a class="site-title" href="#/">Hobbes Dictionary</a>
    <span class="header-sep">|</span>
    <nav class="breadcrumb" id="breadcrumb"></nav>
    <div class="search-wrap">
      <span class="search-icon">&#9906;</span>
      <input class="search-input" id="search-input" type="text"
             placeholder="Search terms&hellip;" autocomplete="off" spellcheck="false">
      <div class="search-dropdown" id="search-dropdown"></div>
    </div>
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

const CHAPTER_ORDER = [
  'Intro',
  'I','II','III','IV','V','VI','VII','VIII','IX','X',
  'XI','XII','XIII','XIV','XV','XVI',
  'XVII','XVIII','XIX','XX','XXI','XXII','XXIII','XXIV','XXV',
  'XXVI','XXVII','XXVIII','XXIX','XXX','XXXI',
  'XXXII','XXXIII','XXXIV','XXXV','XXXVI','XXXVII','XXXVIII','XXXIX','XL','XLI','XLII','XLIII',
  'XLIV','XLV','XLVI','XLVII',
  '1061'
];
const BOOK_RANGES = {
  'I':   ['Intro','I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV','XVI'],
  'II':  ['XVII','XVIII','XIX','XX','XXI','XXII','XXIII','XXIV','XXV','XXVI','XXVII','XXVIII','XXIX','XXX','XXXI'],
  'III': ['XXXII','XXXIII','XXXIV','XXXV','XXXVI','XXXVII','XXXVIII','XXXIX','XL','XLI','XLII','XLIII'],
  'IV':  ['XLIV','XLV','XLVI','XLVII'],
  '1061': ['1061'],
};
const BOOK_TITLES = { 'I':'Of Man', 'II':'Of Commonwealth', 'III':'Of a Christian Commonwealth', 'IV':'Of the Kingdom of Darkness', '1061':'Of the Class' };

function chapterIdx(ch) {
  const m = ch.match(/Chapter ([IVXLCDM]+|Intro|\d+):/);
  return m ? CHAPTER_ORDER.indexOf(m[1]) : 999;
}
function chapterRoman(ch) {
  const m = ch.match(/Chapter ([IVXLCDM]+|Intro|\d+):/); return m ? m[1] : '';
}
function chapterTitle(ch) {
  const m = ch.match(/Chapter (?:[IVXLCDM]+|Intro|\d+): (.+)/); return m ? m[1] : ch;
}
function bookOfChapter(roman) {
  for (const [b, chs] of Object.entries(BOOK_RANGES)) {
    if (chs.includes(roman)) return b;
  }
  return 'I';
}
function makeSlug(t) {
  return t.toLowerCase().replace(/[^\w\s-]/g,'').replace(/\s+/g,'-').replace(/-+/g,'-').replace(/^-|-$/g,'');
}
function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function escRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'); }

// ── Indexes ──────────────────────────────────────────────────────────────────
const slugIndex  = {};   // slug → [entries]
const chapters   = {};   // chapter string → [entries]

for (const e of DATA.entries) {
  if (!slugIndex[e.slug]) slugIndex[e.slug] = [];
  slugIndex[e.slug].push(e);
  if (!chapters[e.chapter]) chapters[e.chapter] = [];
  chapters[e.chapter].push(e);
}

const sortedChapters = Object.keys(chapters).sort((a,b) => chapterIdx(a) - chapterIdx(b));

// Flat sorted list of unique terms for search
const searchTerms = Object.entries(slugIndex).map(([slug, arr]) => ({
  slug,
  term:    arr[0].term,
  chapter: arr[0].chapter,
})).sort((a,b) => a.term.localeCompare(b.term));

// ── Search ───────────────────────────────────────────────────────────────────
const searchInput    = document.getElementById('search-input');
const searchDropdown = document.getElementById('search-dropdown');
let focusedIdx = -1;

function showSearch(query) {
  const q = query.trim().toLowerCase();
  if (!q) { closeSearch(); return; }

  // Rank: starts-with > contains, term name first, then definition
  const results = [];
  for (const t of searchTerms) {
    const tl = t.term.toLowerCase();
    if (tl.startsWith(q))      results.push({...t, rank: 0});
    else if (tl.includes(q))   results.push({...t, rank: 1});
  }
  results.sort((a,b) => a.rank - b.rank || a.term.localeCompare(b.term));
  const top = results.slice(0, 12);

  focusedIdx = -1;
  if (!top.length) {
    searchDropdown.innerHTML = `<div class="search-no-results">No terms found</div>`;
  } else {
    searchDropdown.innerHTML = top.map((r, i) => {
      const hl = esc(r.term).replace(
        new RegExp('(' + escRe(esc(q)) + ')', 'gi'),
        '<mark>$1</mark>'
      );
      const chRoman = chapterRoman(r.chapter);
      const bk = bookOfChapter(chRoman);
      return `<a class="search-result" href="#/term/${encodeURIComponent(r.slug)}" data-i="${i}">
        <div class="sr-term">${hl}</div>
        <div class="sr-chapter">Book ${bk} &middot; Ch. ${chRoman}: ${esc(chapterTitle(r.chapter))}</div>
      </a>`;
    }).join('');
  }
  searchDropdown.classList.add('open');
}

function closeSearch() {
  searchDropdown.classList.remove('open');
  focusedIdx = -1;
}

searchInput.addEventListener('input', () => showSearch(searchInput.value));
searchInput.addEventListener('focus', () => { if (searchInput.value) showSearch(searchInput.value); });

searchInput.addEventListener('keydown', e => {
  const items = searchDropdown.querySelectorAll('.search-result');
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    focusedIdx = Math.min(focusedIdx + 1, items.length - 1);
    items.forEach((el, i) => el.classList.toggle('focused', i === focusedIdx));
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    focusedIdx = Math.max(focusedIdx - 1, -1);
    items.forEach((el, i) => el.classList.toggle('focused', i === focusedIdx));
  } else if (e.key === 'Enter') {
    if (focusedIdx >= 0 && items[focusedIdx]) {
      window.location.href = items[focusedIdx].href;
      searchInput.value = ''; closeSearch();
    }
  } else if (e.key === 'Escape') {
    closeSearch(); searchInput.blur();
  }
});

document.addEventListener('click', e => {
  if (!e.target.closest('.search-wrap')) closeSearch();
});

searchDropdown.addEventListener('click', () => {
  searchInput.value = ''; closeSearch();
});

// ── Routing ───────────────────────────────────────────────────────────────────
window.addEventListener('hashchange', render);
window.addEventListener('DOMContentLoaded', render);

function render() {
  const hash = window.location.hash.slice(1) || '/';
  const parts = hash.split('/').filter(Boolean);
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  closeSearch();

  if (!parts.length || parts[0] === '') return showHome();
  if (parts[0] === 'book')    return showBook(parts[1] || 'I');
  if (parts[0] === 'chapter') return showChapter(decodeURIComponent(parts[1] || ''));
  if (parts[0] === 'term')    return showTerm(decodeURIComponent(parts.slice(1).join('/')));
  showHome();
}

// ── Pages ─────────────────────────────────────────────────────────────────────
function showHome() {
  setBreadcrumb([]);
  const total = DATA.entries.length;
  const books = ['I','II','III','IV','1061'].map(b => {
    const range = BOOK_RANGES[b];
    const count = range.reduce((n, r) => {
      const ch = sortedChapters.find(c => chapterRoman(c) === r);
      return n + (ch ? chapters[ch].length : 0);
    }, 0);
    const enabled = count > 0;
    return `<a class="book-card${enabled ? '' : ' disabled'}" ${enabled ? `href="#/book/${b}"` : ''}>
      <h3>Book ${b}</h3>
      <p class="book-sub">${BOOK_TITLES[b]}</p>
      <p class="book-count">${count ? `${count} definitions` : 'Not yet loaded'}</p>
    </a>`;
  }).join('');

  const p = document.getElementById('page-home');
  p.innerHTML = `
    <h1 class="page-title">Hobbes Dictionary</h1>
    <p class="page-subtitle">Definitions from <em>Leviathan</em> (1651) &mdash; Select a book</p>
    <div class="book-grid">${books}</div>`;
  p.classList.add('active');
}

function showBook(book) {
  const title = BOOK_TITLES[book] || '';
  const range = BOOK_RANGES[book] || [];
  const chs = sortedChapters.filter(c => range.includes(chapterRoman(c)));
  const total = chs.reduce((n, c) => n + chapters[c].length, 0);

  setBreadcrumb([{label:`Book ${book}: ${title}`, href:`/book/${book}`}]);
  const p = document.getElementById('page-book');
  p.innerHTML = `
    <a class="back-btn" href="#/">← Books</a>
    <h1 class="page-title">Book ${book}: ${esc(title)}</h1>
    <p class="page-subtitle">${total} definitions across ${chs.length} chapters</p>
    <div class="chapter-grid">
      ${chs.map(ch => `
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
  const book = bookOfChapter(roman);
  const title = chapterTitle(chStr);
  const ents  = chapters[chStr];

  setBreadcrumb([
    {label:`Book ${book}`, href:`/book/${book}`},
    {label:`Ch. ${roman}: ${title}`, href:`/chapter/${roman}`}
  ]);
  const p = document.getElementById('page-chapter');
  p.innerHTML = `
    <a class="back-btn" href="#/book/${book}">← Book ${book}: ${esc(BOOK_TITLES[book])}</a>
    <h1 class="page-title">Chapter ${roman}</h1>
    <p class="page-subtitle">${esc(title)} &middot; ${ents.length} definitions</p>
    <ul class="def-list">
      ${ents.map(e => `
        <li><a class="def-item" href="#/term/${encodeURIComponent(e.slug)}">
          <div class="def-term">${esc(e.term)}</div>
          <div class="def-preview">${esc(e.definition.slice(0,130))}${e.definition.length>130?'&hellip;':''}</div>
        </a></li>`).join('')}
    </ul>`;
  p.classList.add('active');
}

function showTerm(slug) {
  const ents = slugIndex[slug];
  if (!ents) return showHome();
  const first  = ents[0];
  const roman  = chapterRoman(first.chapter);
  const book   = bookOfChapter(roman);
  const title  = chapterTitle(first.chapter);
  const allRefs = [...new Set(ents.flatMap(e => e.cross_refs))].sort();

  setBreadcrumb([
    {label:`Book ${book}`, href:`/book/${book}`},
    {label:`Ch. ${roman}`, href:`/chapter/${roman}`},
    {label:first.term, href:`/term/${slug}`}
  ]);

  const blocksHtml = ents.map(e => {
    const chRoman = chapterRoman(e.chapter);
    // Compact context: strip redundant prefixes, trim
    const ctx = compactContext(e.context);
    return `
      <div class="def-block">
        <div class="def-chapter-label">
          <span><a href="#/chapter/${chRoman}">Chapter ${chRoman}: ${esc(chapterTitle(e.chapter))}</a></span>
          <span>p.&nbsp;${esc(e.page_number)}</span>
        </div>
        <div class="def-body">${linkify(e.definition, e.cross_refs)}</div>
        ${ctx ? `<div class="def-context">${esc(ctx)}</div>` : ''}
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
            : '';
        }).join('')}
      </div>
    </div>` : '';

  const multiNote = ents.length > 1
    ? `<p class="page-subtitle">Defined in ${ents.length} chapters</p>` : '';

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

// ── Compact context ───────────────────────────────────────────────────────────
function compactContext(ctx) {
  if (!ctx) return '';
  // Strip verbose prefixes, keep the substance
  return ctx
    .replace(/^marginal label:\s*['"]?/i, '')
    .replace(/['"]?\s*[;\-—]\s*/, ' — ')
    .replace(/;\s*/g, ' · ')
    .replace(/^['"]|['"]$/g, '')
    .trim();
}

// ── Linkify definition text ───────────────────────────────────────────────────
function linkify(text, refs) {
  if (!refs || !refs.length) return esc(text);
  const sorted = [...refs].sort((a,b) => b.length - a.length);
  const spans = [];
  for (const ref of sorted) {
    const rx = new RegExp('\\b' + escRe(ref) + '\\b', 'gi');
    let m;
    while ((m = rx.exec(text)) !== null) {
      const s = m.index, e = s + m[0].length;
      if (!spans.some(x => s < x.end && e > x.start))
        spans.push({start:s, end:e, matched:m[0], ref});
    }
  }
  if (!spans.length) return esc(text);
  spans.sort((a,b) => a.start - b.start);
  let out = '', last = 0;
  for (const {start, end, matched, ref} of spans) {
    out += esc(text.slice(last, start));
    const sl = makeSlug(ref);
    out += slugIndex[sl]
      ? `<a class="term-link" href="#/term/${encodeURIComponent(sl)}">${esc(matched)}</a>`
      : esc(matched);
    last = end;
  }
  return out + esc(text.slice(last));
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
print(f"  {len(entries)} entries · {len(set(e['slug'] for e in entries))} unique terms · {len(set(e['chapter'] for e in entries))} chapters")
