#!/usr/bin/env python3
"""
Merge Books II-IV definitions into hobbes_dictionary.csv, recompute cross-refs.
"""
import json, csv, re, sys

BASE = "/Users/Chester2/Documents/Documents/projects/HobbesDictionary"
CSV_PATH = f"{BASE}/hobbes_dictionary.csv"

AGENT_FILES = [
    "/private/tmp/claude-504/-Users-Chester2/tasks/a721b0e.output",  # Ch XVII-XXIII
    "/private/tmp/claude-504/-Users-Chester2/tasks/a51813a.output",  # Ch XXIV-XXXI
    "/private/tmp/claude-504/-Users-Chester2/tasks/ad8eaff.output",  # Ch XXXII-XLII
    "/private/tmp/claude-504/-Users-Chester2/tasks/a5e41ab.output",  # Ch XLIV-XLVII
]


def extract_json_from_agent_output(filepath):
    """Parse JSONL agent output file and extract the last assistant text block."""
    last_text = None
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            # Format: {type:"message", message:{role:"assistant", content:[{type:"text",text:"..."}]}}
            msg = obj.get("message", {})
            if msg.get("role") == "assistant":
                content = msg.get("content", [])
                for block in content:
                    if block.get("type") == "text":
                        last_text = block["text"]
    return last_text or ""


def extract_json_array(text):
    """Find and parse the JSON array from agent text using bracket-depth parser."""
    # Find start of JSON array
    start = text.find("[")
    if start == -1:
        return []
    candidate = text[start:]
    depth = 0
    in_str = False
    escape = False
    end = -1
    for i, ch in enumerate(candidate):
        if escape:
            escape = False
            continue
        if ch == "\\" and in_str:
            escape = True
            continue
        if ch == '"' and not escape:
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        return []
    try:
        return json.loads(candidate[: end + 1])
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        return []


def add_cross_refs(all_definitions):
    """Word-boundary match all terms against all definitions."""
    all_terms = [(d["term"], d["term"].lower()) for d in all_definitions]
    # Sort by length desc to prefer longer matches
    all_terms.sort(key=lambda x: -len(x[1]))

    for defn in all_definitions:
        def_text = defn.get("definition", "").lower()
        refs = []
        for term_original, term_lower in all_terms:
            if term_lower == defn["term"].lower():
                continue
            pattern = r"\b" + re.escape(term_lower) + r"\b"
            if re.search(pattern, def_text):
                refs.append(term_original)
        defn["cross_refs"] = "; ".join(sorted(refs)) if refs else ""
    return all_definitions


# ── Load existing Book I definitions ─────────────────────────────────────────
print("Loading existing CSV...")
existing = []
with open(CSV_PATH, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        existing.append(dict(row))
print(f"  {len(existing)} existing Book I entries")

# ── Parse agent outputs ───────────────────────────────────────────────────────
new_defs = []
for filepath in AGENT_FILES:
    print(f"\nParsing {filepath.split('/')[-1]}...")
    text = extract_json_from_agent_output(filepath)
    if not text:
        print(f"  WARNING: no assistant text found in {filepath}")
        continue
    entries = extract_json_array(text)
    print(f"  Extracted {len(entries)} definitions")

    for e in entries:
        chapter_num   = e.get("chapter_num", "?")
        chapter_title = e.get("chapter_title", "")
        chapter_str   = f"Chapter {chapter_num}: {chapter_title}"
        new_defs.append({
            "term":          e.get("term", ""),
            "definition":    e.get("definition", ""),
            "chapter":       chapter_str,
            "page_number":   str(e.get("page_number", "")),
            "cross_refs":    "",   # will be recomputed
            "context":       e.get("context", ""),
        })

print(f"\nNew definitions from Books II-IV: {len(new_defs)}")

# ── Combine and recompute cross-refs ─────────────────────────────────────────
all_defs = existing + new_defs
print(f"Total definitions: {len(all_defs)}")

print("Recomputing cross-references for all entries...")
all_defs = add_cross_refs(all_defs)

# ── Write CSV ─────────────────────────────────────────────────────────────────
fieldnames = ["term", "definition", "chapter", "page_number", "cross_refs", "context"]
with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(all_defs)

print(f"CSV written: {CSV_PATH}")
print(f"Done — {len(all_defs)} total definitions across all books.")
