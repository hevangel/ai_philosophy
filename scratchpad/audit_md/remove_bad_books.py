"""Remove wrong/duplicate books from the corpus pipeline state:
  025 - file was Grant Maxwell's 'How Does It Feel?' (wrong book, not the
        Open Court 'The Beatles and Philosophy'; not available on the mirror)
  242 - byte-identical duplicate of 224 (same book listed twice in the
        bibliography under two titles)

Removes: manifest entry, units + notes, markdown folder, epub (backed up to
scratchpad/audit_md/bad_epubs/), explorer cover webp.
"""
import json
import shutil
from pathlib import Path

ROOT = Path(r"B:\ai_philosophy\data\philosophy_pop_culture").resolve()
BASE = Path(r"B:\ai_philosophy\scratchpad\popcult_index").resolve()
COVERS = Path(r"B:\ai_philosophy\knowledge-base\popcult-index\covers").resolve()
BAD = Path(r"B:\ai_philosophy\scratchpad\audit_md\bad_epubs").resolve()
MANIFEST = BASE / "full_manifest.json"

REMOVE = ["025", "242"]


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for num in REMOVE:
        book = next((b["book"] for b in manifest if b["book"].startswith(num + " - ")), None)
        if book is None:
            print(f"{num}: not in manifest")
            continue
        manifest = [b for b in manifest if b["book"] != book]
        # units + notes
        for p in sorted((BASE / "units").glob("u*.json")):
            u = json.loads(p.read_text(encoding="utf-8"))
            if u.get("book") == book:
                (BASE / "notes" / p.name).unlink(missing_ok=True)
                p.unlink()
                print(f"{num}: removed {p.stem}")
        # markdown folder
        md = ROOT / "markdown" / book
        if md.exists():
            shutil.rmtree(md)
            print(f"{num}: removed markdown folder")
        # epub (backup first)
        ep = ROOT / "epub" / (book + ".epub")
        if ep.exists():
            if not (BAD / ep.name).exists():
                shutil.copy2(ep, BAD / ep.name)
            ep.unlink()
            print(f"{num}: epub backed up + removed")
        # explorer cover
        cov = COVERS / f"{num}.webp"
        if cov.exists():
            cov.unlink()
            print(f"{num}: cover removed")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print("manifest books:", len(manifest))


if __name__ == "__main__":
    main()
