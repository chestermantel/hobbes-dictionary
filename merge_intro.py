#!/usr/bin/env python3
"""Merge Introduction definitions into hobbes_dictionary.csv, recompute cross-refs."""
import json, csv, re

BASE = "/Users/Chester2/Documents/Documents/projects/HobbesDictionary"
CSV_PATH = f"{BASE}/hobbes_dictionary.csv"

INTRO_DEFS = [
  {
    "term": "Nature",
    "definition": "NATURE (the Art whereby God hath made and governes the World) is by the Art of man, as in many other things, so in this also imitated, that it can make an Artificial Animal.",
    "page_number": "1",
    "context": "Opening definition by parenthetical gloss; Hobbes equates Nature with divine Art, establishing the Nature/Art analogy that structures the whole work",
    "chapter_num": "Intro",
    "chapter_title": "The Introduction"
  },
  {
    "term": "Life",
    "definition": "For seeing life is but a motion of Limbs, the begining whereof is in some principall part within",
    "page_number": "1",
    "context": "Reductive materialist definition of life as mechanical motion; grounds the analogy between natural organisms and artificial engines",
    "chapter_num": "Intro",
    "chapter_title": "The Introduction"
  },
  {
    "term": "Automata",
    "definition": "all Automata (Engines that move themselves by springs and wheeles as doth a watch) have an artificiall life",
    "page_number": "1",
    "context": "Parenthetical definition of automata as self-moving engines; used to argue that artificial machines can possess artificial life",
    "chapter_num": "Intro",
    "chapter_title": "The Introduction"
  },
  {
    "term": "Artificial Life",
    "definition": "For seeing life is but a motion of Limbs, the begining whereof is in some principall part within; why may we not say, that all Automata (Engines that move themselves by springs and wheeles as doth a watch) have an artificiall life?",
    "page_number": "1",
    "context": "Hobbes extends the definition of life-as-motion to mechanical engines; defines artificial life as self-generated mechanical motion",
    "chapter_num": "Intro",
    "chapter_title": "The Introduction"
  },
  {
    "term": "Leviathan",
    "definition": "by Art is created that great LEVIATHAN called a COMMON-WEALTH, or STATE, (in latine CIVITAS) which is but an Artificiall Man; though of greater stature and strength than the Naturall, for whose protection and defence it was intended",
    "page_number": "1",
    "context": "Central definition of the Commonwealth; the three names Leviathan, Commonwealth, and State (Civitas) are treated as co-referential",
    "chapter_num": "Intro",
    "chapter_title": "The Introduction"
  },
  {
    "term": "Sovereignty (as Artificial Soul)",
    "definition": "the Soveraignty is an Artificiall Soul, as giving life and motion to the whole body",
    "page_number": "1",
    "context": "Defines Sovereignty by analogy with the soul in the natural body; sovereignty is the animating principle of the Commonwealth",
    "chapter_num": "Intro",
    "chapter_title": "The Introduction"
  },
  {
    "term": "Reward and Punishment (as Nerves)",
    "definition": "Reward and Punishment (by which fastned to the seate of the Soveraignty, every joynt and member is moved to performe his duty) are the Nerves, that do the same in the Body Naturall",
    "page_number": "1",
    "context": "Defines reward and punishment by analogy with the nerves; they motivate every member to perform their duty",
    "chapter_num": "Intro",
    "chapter_title": "The Introduction"
  },
  {
    "term": "Salus Populi",
    "definition": "Salus Populi (the peoples safety) its Businesse",
    "page_number": "1",
    "context": "Latin term immediately glossed in English; defines the end or business of the commonwealth as the safety of the people",
    "chapter_num": "Intro",
    "chapter_title": "The Introduction"
  },
  {
    "term": "Equity and Laws (as Artificial Reason and Will)",
    "definition": "Equity and Lawes, an artificiall Reason and Will",
    "page_number": "1",
    "context": "Defines equity and laws together by analogy with reason and will; identifies positive law with the rational faculty of the artificial man",
    "chapter_num": "Intro",
    "chapter_title": "The Introduction"
  },
  {
    "term": "Concord (as Health)",
    "definition": "Concord, Health",
    "page_number": "1",
    "context": "Terse analogical definition equating civic concord with the health of the natural body",
    "chapter_num": "Intro",
    "chapter_title": "The Introduction"
  },
  {
    "term": "Sedition (as Sickness)",
    "definition": "Sedition, Sicknesse",
    "page_number": "1",
    "context": "Terse analogical definition equating sedition with bodily sickness; contrasted with Concord/Health",
    "chapter_num": "Intro",
    "chapter_title": "The Introduction"
  },
  {
    "term": "Civil War (as Death of the Commonwealth)",
    "definition": "and Civill war, Death",
    "page_number": "1",
    "context": "Terse analogical definition equating civil war with the death of the natural body; final term in the Commonwealth-body series",
    "chapter_num": "Intro",
    "chapter_title": "The Introduction"
  },
  {
    "term": "Pacts and Covenants (as Fiat)",
    "definition": "the Pacts and Covenants, by which the parts of this Body Politique were at first made, set together, and united, resemble that Fiat, or the Let us make man, pronounced by God in the Creation.",
    "page_number": "1",
    "context": "Defines pacts and covenants as the generative act of the Commonwealth, analogous to God's creative fiat",
    "chapter_num": "Intro",
    "chapter_title": "The Introduction"
  },
  {
    "term": "Nosce Teipsum",
    "definition": "Nosce teipsum, Read thy self: which was not meant, as it is now used, to countenance, either the barbarous state of men in power, towards their inferiors; or to encourage men of low degree, to a sawcie behaviour towards their betters; But to teach us, that for the similitude of the thoughts, and Passions of one man, to the thoughts, and Passions of another, whosoever looketh into himself, and considereth what he doth, when he does think, opine, reason, hope, feare, &c, and upon what grounds; he shall thereby read and know, what are the thoughts, and Passions of all other men, upon the like occasions.",
    "page_number": "2",
    "context": "Hobbes redefines the classical maxim 'know thyself' as an introspective method for understanding universal human nature; his epistemological foundation for the science of man",
    "chapter_num": "Intro",
    "chapter_title": "The Introduction"
  },
  {
    "term": "Passions (Universality of)",
    "definition": "I say the similitude of Passions, which are the same in all men, desire, feare, hope, &c; not the similitude of the objects of the Passions, which are the things desired, feared, hoped, &c: for these the constitution individuall, and particular education do so vary",
    "page_number": "2",
    "context": "Hobbes draws a precise distinction between passions themselves (universal) and their objects (particular); the universality of passion grounds self-knowledge of others",
    "chapter_num": "Intro",
    "chapter_title": "The Introduction"
  }
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


# Load existing
print("Loading existing CSV...")
existing = []
with open(CSV_PATH, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        existing.append(dict(row))
print(f"  {len(existing)} existing entries")

# Build new intro entries
new_entries = []
for e in INTRO_DEFS:
    new_entries.append({
        "term":        e["term"],
        "definition":  e["definition"],
        "chapter":     f"Chapter {e['chapter_num']}: {e['chapter_title']}",
        "page_number": e["page_number"],
        "cross_refs":  "",
        "context":     e["context"],
    })

print(f"  Adding {len(new_entries)} Introduction entries")

# Intro goes at the front
all_defs = new_entries + existing
print(f"Total: {len(all_defs)}")

print("Recomputing cross-references...")
all_defs = add_cross_refs(all_defs)

fieldnames = ["term", "definition", "chapter", "page_number", "cross_refs", "context"]
with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(all_defs)

print(f"Done — {len(all_defs)} total definitions.")
