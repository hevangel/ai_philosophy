# PhilArchive tailoring notes

- Formats: PDF only (per venues.json). DOCX kept as source of the PDF.
- Anonymized: NO — deposit carries the author byline (Horace Chan) and is made under the
  owner's PhilPapers account. The EUJAP copy stays blinded.
- Reply relation: subtitle "A Reply to Jordan MacKenzie on AI and Valuing Practices" +
  target record philarchive.org/rec/MACFAL-5 (MacKenzie 2026). Indicate the relation on the
  submission form; the abstract also frames the reply.
- Policy check: no stated AI policy (venues.json, checked 2026-10-13). Disclosure statement
  included anyway per pipeline standing rule; the manuscript carries an Acknowledgements
  section disclosing substantial AI assistance (transparency in the public artifact).
- §7 notation: the draft's LaTeX display equations were converted to plain-text notation
  (V_reading(A, M) > V_reading(A, H)) because the pipeline's pandoc setup does not parse
  \( \) / \[ \] math (verified by test conversion 2026-10-14: subscripts were dropped).
- Word count: 7,080 body / 7,239 with references. PhilArchive has no limit.
- PDF produced via Word COM export (md_to_docx.py --pdf), 2026-10-14 (v3).
- v3 replaces v2 (owner's new version, 2026-10-14): retitled 'The Summit Is Not the Climb...',
  four-values framework moved to §2, new §8 'Recognition Without Ratification',
  E/G/T formalization added in §3, Wimsatt & Beardsley reference removed (uncited in v3).
