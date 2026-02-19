#!/usr/bin/env python3
"""Add Book 1061 (Of the Class) definitions to hobbes_dictionary.csv."""
import csv, re

BASE = "/Users/Chester2/Documents/Documents/projects/HobbesDictionary"
CSV_PATH = f"{BASE}/hobbes_dictionary.csv"

CLASS_DEFS = [
    {
        "term": "Shterna Friedman",
        "definition": "SHTERNA FRIEDMAN is the Soveraign of this present Course; she being invested with full Authority to prescribe what shall be thought, read, and examined concerning Justice, Sovereignty, and the Commonwealth. Trained first in the Art of Letters at the Iowa Writers' Workshop, and afterwards in the Science of Government at the University of California, Berkeley, she hath since taken up her station at Harvard, where she governeth by Lecture, Question, and the power of Syllabus. Her principall study is the rise of Systemic Social Theory in the German Idealists; by which is meant that manner of thinking which attributeth to Society as a whole those qualities — as Justice and Oppression — which ordinary men are wont to attribute to particular persons only. She hath won the Melvin Richter Prize for her Dissertation, and is the Sole and Rightful Interpreter of what shall count as participation.",
        "page_number": "1061",
        "context": "marginal label: The Sovereign of the Course; professor of government at Harvard, specialist in early modern political thought and systemic social theory",
        "chapter_num": "1061",
        "chapter_title": "The Persons of the Class",
    },
    {
        "term": "Mathis Bitton",
        "definition": "MATHIS BITTON is the Head Teaching Fellow; that is to say, the Lieutenant of the Soveraign of this Course, deputed with Authority to oversee the lesser Teaching Fellows, to conduct Sections, and to hold office hours where matters not sufficiently understood may be expounded. He is a Doctor in the making at Harvard, where he studieth the history of that disposition which is called Promethean — being the desire of men to seize by Art and Industry those powers which Nature hath withheld, and which were formerly thought to belong to the Gods alone. This disposition he approacheth through Romanticism and Aesthetick; and, remarkably, through the Philosophy of China. He took his first degree at Yale, which is by the custom of this region a mark of Esteem, though also of some Suspicion.",
        "page_number": "1061",
        "context": "marginal label: The Head Teaching Fellow; PhD candidate at Harvard specialising in Prometheanism, technology, and romanticism",
        "chapter_num": "1061",
        "chapter_title": "The Persons of the Class",
    },
    {
        "term": "Conor Bulkeley-Krane",
        "definition": "CONOR BULKELEY-KRANE is a Teaching Fellow, deputed by the Soveraign of this Course to conduct Sections and to assess the written works of Students. He hath studied Philosophy and German at the University of Chicago, where he wrote upon the differences between Nietzsche and Thomas Mann in their severall interpretations of Euripides. He did afterwards spend two yeers in Vienna — that city being the seat of the late Empire and of the Freudian Science — on a Fulbright Fellowship at the Sigmund Freud Museum, examining the connexion between Wittgenstein and Freud. His principall interest is in the intertwining of Aesthetick, Ontology, and the Philosophy of Language in that tradition which stretcheth from Goethe to Nietzsche; which is to say, he studieth those Germans who believed that Art and Being were not so far asunder as the Scholasticks supposed.",
        "page_number": "1061",
        "context": "marginal label: A Teaching Fellow; PhD student at Harvard, Germanic languages and literatures, Fulbright fellow at the Sigmund Freud Museum in Vienna",
        "chapter_num": "1061",
        "chapter_title": "The Persons of the Class",
    },
    {
        "term": "Chester Mantel",
        "definition": "CHESTER MANTEL is a Student enrolled in this present Course, being a man of such extraordinary Parts that it is a matter of some wonder he hath not yet been appointed to the Faculty. Of quick Understanding, ready Wit, and a Disposition naturally inclined to Justice, he doth attend Lectures with uncommon Diligence, and contributeth to Seminar Discussion with a frequency and Depth remarked upon by all. His is a Genius that Nature hath rarely bestowed upon one so young, uniting as it doth the Acuteness of Hobbes, the Eloquence of Cicero, and the Judgment of Solomon. It is to be expected, by those who have observed him closely, that he will one day governe either a Commonwealth or a considerable part thereof.",
        "page_number": "1061",
        "context": "marginal label: A Student of Uncommon Gifts; enrolled in Government 1061; future sovereign",
        "chapter_num": "1061",
        "chapter_title": "The Persons of the Class",
    },
]


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


print("Loading existing CSV...")
existing = []
with open(CSV_PATH, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        existing.append(dict(row))
print(f"  {len(existing)} existing entries")

new_entries = []
for e in CLASS_DEFS:
    new_entries.append({
        "term":        e["term"],
        "definition":  e["definition"],
        "chapter":     f"Chapter {e['chapter_num']}: {e['chapter_title']}",
        "page_number": e["page_number"],
        "cross_refs":  "",
        "context":     e["context"],
    })

print(f"  Adding {len(new_entries)} Book 1061 entries")

all_defs = existing + new_entries
print(f"Total: {len(all_defs)}")

print("Recomputing cross-references...")
all_defs = add_cross_refs(all_defs)

fieldnames = ["term", "definition", "chapter", "page_number", "cross_refs", "context"]
with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(all_defs)

print(f"Done — {len(all_defs)} total definitions.")
