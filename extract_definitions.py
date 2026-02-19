#!/usr/bin/env python3
"""
Hobbes Dictionary Extractor
Extracts definitions from On Man.pdf (Leviathan, Part I) using Claude Sonnet.
Outputs a CSV with: term, definition, chapter, page_number, cross_refs, context
"""

import os
import json
import csv
import re
import sys
import fitz  # PyMuPDF
import anthropic

PDF_PATH = "/Users/Chester2/Documents/Documents/projects/HobbesDictionary/On Man.pdf"
OUTPUT_CSV = "/Users/Chester2/Documents/Documents/projects/HobbesDictionary/hobbes_dictionary.csv"

# Chapter boundaries: (chapter_num, chapter_title, start_pdf_page [1-indexed], end_pdf_page [1-indexed inclusive])
CHAPTERS = [
    ("I",    "Of Sense",                                           2,   3),
    ("II",   "Of Imagination",                                     4,   8),
    ("III",  "Of the Consequence or Train of Imaginations",        9,  13),
    ("IV",   "Of Speech",                                         14,  22),
    ("V",    "Of Reason and Science",                             23,  29),
    ("VI",   "Of the Interior Beginnings of Voluntary Motions",   30,  39),
    ("VII",  "Of the Ends or Resolutions of Discourse",           40,  42),
    ("VIII", "Of the Virtues Commonly Called Intellectual",        43,  54),
    ("IX",   "Of the Several Subjects of Knowledge",              55,  56),
    ("X",    "Of Power, Worth, Dignity, Honour, and Worthiness",  57,  64),
    ("XI",   "Of the Difference of Manners",                      65,  71),
    ("XII",  "Of Religion",                                       72,  85),
    ("XIII", "Of the Natural Condition of Mankind",               85,  89),
    ("XIV",  "Of the First and Second Natural Laws and Contracts", 90, 100),
    ("XV",   "Of Other Laws of Nature",                          101, 113),
    ("XVI",  "Of Persons, Authors, and Things Personated",        114, 118),
]

SYSTEM_PROMPT = """You are a meticulous scholar of Thomas Hobbes' Leviathan (1651 original edition).
Your task: identify EVERY term that Hobbes explicitly or implicitly defines in the chapter text.
Be exhaustive — Hobbes treats definitions as the foundation of science, so err on the side of inclusion.

SIGNALS THAT A TERM IS BEING DEFINED:
1. ALL CAPS terms at their first major appearance (e.g., SENSE, IMAGINATION, ENDEAVOUR)
2. Explicit formulas: "is called", "is nothing but", "I call", "By X I mean/understand", "properly is", "properly signifieth", "is properly", "we call", "which we call"
3. Marginal annotations in the text (appear as short labels at the start of paragraphs or inline — these name the concept being defined in that paragraph)
4. Latin terms followed by English explanations
5. SEQUENCES of definitions — Hobbes often defines many related terms in rapid succession. Capture every item, including:
   - The passion sequences in Chapter VI (appetite, desire, love, aversion, hate, joy, grief, pleasure, pain, fear, courage, anger, hope, despair, trust, diffidence, indignation, benevolence, covetousness, ambition, pusillanimity, magnanimity, valour, liberality, and many more)
   - The honour/dishonour sequences in Chapter X (every act that is defined as honouring or dishonouring)
   - The power types in Chapter X (natural power, instrumental power, etc.)
   - The virtue/vice and intellectual virtue sequences in Chapter VIII
   - The law of nature sequences in Chapters XIV and XV (every numbered or named law)
   - Any other sequence where Hobbes enumerates and defines multiple related concepts
6. Conceptual distinctions where Hobbes differentiates two closely related terms (e.g. counsel vs command, sign vs token)
7. Terms that receive a full paragraph of explanation even without an explicit "is called" formula

PAGE NUMBERS: The running headers look like "Chap. 6. 39" (chapter, then page number) or "Part i. 66".
Extract the page number as the last number in such a header nearest to where the definition appears.
If only bracket numbers like [23] are available, use those.

Return a JSON array of objects. Each object must have exactly these keys:
- "term": Title Case name of the defined concept (e.g. "Sense", "Right of Nature")
- "definition": Direct quote of Hobbes's definition (the actual sentence(s) he uses; keep it faithful to the text)
- "page_number": string, the editor's running-header page number nearest this definition
- "context": brief scholarly note — e.g. "first of a sequence of passion definitions", "contrasted with Counsel", "foundation for the argument on natural law", "marginal label: Power"

Return ONLY the JSON array, no other text."""

EXTRACTION_PROMPT = """Chapter {chapter_num}: {chapter_title}

The text below comes from the 1651 edition of Hobbes's Leviathan, Part I (Of Man).
Running headers show the page number, e.g. "Chap. 6. 39" means page 39.
Bracket numbers like [23] are original 1651 page numbers.

Extract every defined term exhaustively. Pay special attention to any list or sequence where Hobbes defines multiple items in succession.

TEXT:
{text}

Return a JSON array only."""


def extract_chapter_text(doc, start_page, end_page):
    """Extract text from PDF pages (1-indexed), annotating each PDF page."""
    pages_text = []
    for page_num in range(start_page - 1, end_page):  # Convert to 0-indexed
        page = doc[page_num]
        text = page.get_text()
        pages_text.append(f"[PDF page {page_num + 1}]\n{text}")
    return "\n".join(pages_text)


def call_sonnet(client, chapter_num, chapter_title, text):
    """Send chapter text to Claude Sonnet for definition extraction."""
    prompt = EXTRACTION_PROMPT.format(
        chapter_num=chapter_num,
        chapter_title=chapter_title,
        text=text
    )

    print(f"  Calling Sonnet for Chapter {chapter_num}: {chapter_title}...")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fences if present
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)

    try:
        definitions = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  WARNING: JSON parse error for Chapter {chapter_num}: {e}")
        print(f"  Raw response (first 800 chars): {raw[:800]}")
        definitions = []

    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    # Sonnet pricing: $3/M input, $15/M output
    cost = (input_tokens * 3.0 + output_tokens * 15.0) / 1_000_000
    print(f"  -> {len(definitions)} definitions | {input_tokens}in / {output_tokens}out tokens | ~${cost:.4f}")

    return definitions


def add_cross_refs(all_definitions):
    """
    Post-process: for each definition's text, find which other defined terms appear in it.
    Uses whole-word matching, case-insensitive.
    """
    all_terms = [(d["term"], d["term"].lower()) for d in all_definitions]

    for defn in all_definitions:
        def_text = defn.get("definition", "").lower()
        refs = []
        for term_original, term_lower in all_terms:
            if term_lower == defn["term"].lower():
                continue
            pattern = r'\b' + re.escape(term_lower) + r'\b'
            if re.search(pattern, def_text):
                refs.append(term_original)
        defn["cross_refs"] = "; ".join(sorted(refs)) if refs else ""

    return all_definitions


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    doc = fitz.open(PDF_PATH)
    print(f"Opened: {PDF_PATH} ({len(doc)} pages total)")
    print(f"Processing {len(CHAPTERS)} chapters...\n")

    all_definitions = []
    total_cost_est = 0.0

    for chapter_num, chapter_title, start_page, end_page in CHAPTERS:
        print(f"Chapter {chapter_num}: {chapter_title} (PDF pages {start_page}-{end_page})")
        text = extract_chapter_text(doc, start_page, end_page)
        definitions = call_sonnet(client, chapter_num, chapter_title, text)

        for defn in definitions:
            defn["chapter_num"] = chapter_num
            defn["chapter_title"] = chapter_title
            defn["chapter"] = f"Chapter {chapter_num}: {chapter_title}"

        all_definitions.extend(definitions)

    print(f"\n{'='*60}")
    print(f"Total definitions extracted: {len(all_definitions)}")

    print("Computing cross-references...")
    all_definitions = add_cross_refs(all_definitions)

    fieldnames = ["term", "definition", "chapter", "page_number", "cross_refs", "context"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_definitions)

    print(f"CSV written to: {OUTPUT_CSV}")
    print(f"Done! {len(all_definitions)} definitions across {len(CHAPTERS)} chapters.")


if __name__ == "__main__":
    main()
