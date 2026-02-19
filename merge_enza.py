#!/usr/bin/env python3
"""Add Enza Jones to Book 1061."""
import csv, re

BASE = "/Users/Chester2/Documents/Documents/projects/HobbesDictionary"
CSV_PATH = f"{BASE}/hobbes_dictionary.csv"

ENTRY = {
    "term": "Enza Jones",
    "definition": "ENZA JONES is a Student of this present Course, distinguished above all her Fellows by a singular and remarkable Talent: namely, the ability to perform Spoken-Word Autobiographies of Thomas Hobbes. By this Art she doth give Voice and Passion to the Philosopher himself, recounting in verse and cadence the Feares, Reasonings, and Indignations of a man who lived through Civil Warre, Exile, and the perpetuall hostility of Clergymen — and who, by his own Confession, was born a Twin to Feare. That she can render such a Life in the first Person, with convincing Affect, is a thing which surpasseth the ordinary Powers of Understanding; for to inhabit the mind of Hobbes requireth not only Learning, but a Courage and an Imagination of the first Order. She is, in short, what Hobbes himself would have called a Soveraign of the Performative Arts.",
    "page_number": "1061",
    "context": "marginal label: A Student of Singular Performative Gifts; celebrated for spoken-word autobiographies of Hobbes",
    "chapter": "Chapter 1061: The Persons of the Class",
}


def add_cross_refs(all_definitions):
    all_terms = [(d["term"], d["term"].lower()) for d in all_definitions]
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


existing = []
with open(CSV_PATH, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        existing.append(dict(row))

existing.append({
    "term":        ENTRY["term"],
    "definition":  ENTRY["definition"],
    "chapter":     ENTRY["chapter"],
    "page_number": ENTRY["page_number"],
    "cross_refs":  "",
    "context":     ENTRY["context"],
})

print(f"Total before recompute: {len(existing)}")
existing = add_cross_refs(existing)

fieldnames = ["term", "definition", "chapter", "page_number", "cross_refs", "context"]
with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(existing)

print("Done.")
