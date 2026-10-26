"""Build the publishable Philosophy × Pop Culture explorer dataset.

Reads the completed reverse-index data and local EPUBs, then writes only a compact
JSON graph and normalized cover thumbnails under knowledge-base/popcult-index/.
The source EPUBs and extracted chapter text remain outside the published site.
Courses (university lecture catalog) come from courses.json in this folder and are
merged in as the top-level "courses" section (dataset version 2).
"""
from __future__ import annotations

import argparse
import io
import json
import os
import posixpath
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote

from epub_lib import NS, safe_fromstring

BASE = Path(r"B:\ai_philosophy\scratchpad\popcult_index").resolve()
REPO = Path(r"B:\ai_philosophy").resolve()
EPUB_DIR = (REPO / "philosophy_pop_culture" / "epub").resolve()
OUT_DIR = (REPO / "knowledge-base" / "popcult-index").resolve()
COVER_DIR = (OUT_DIR / "covers").resolve()
DATA_PATH = (OUT_DIR / "data.json").resolve()
COURSES_PATH = (BASE / "courses.json").resolve()
LECTURES_DIR = (BASE / "course_lectures").resolve()

COURSE_LINK_FIELDS = ("video", "transcript", "notes", "reading", "syllabus")
COURSE_TIERS = ("A", "B", "C")

MAX_IMAGE_BYTES = 25 * 1024 * 1024
COVER_SIZE = (480, 720)
RASTER_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def inside(base: Path, candidate: Path) -> Path:
    base = base.resolve()
    candidate = candidate.resolve()
    if os.path.commonpath([str(base), str(candidate)]) != str(base):
        raise ValueError(f"path escapes {base}: {candidate}")
    return candidate


def book_title(raw: str) -> str:
    return re.sub(r"^\d+\s*-\s*", "", raw).strip()


def book_id(raw: str, used: set[str]) -> str:
    match = re.match(r"^(\d+)", raw)
    base = match.group(1) if match else re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")[:48]
    value = base or "book"
    suffix = 2
    while value in used:
        value = f"{base}-{suffix}"
        suffix += 1
    used.add(value)
    return value


def zip_member(opf_dir: str, href: str) -> str | None:
    value = unquote((href or "").split("#", 1)[0]).replace("\\", "/")
    joined = posixpath.normpath(posixpath.join(opf_dir, value))
    if not value or joined.startswith("../") or joined.startswith("/"):
        return None
    return joined


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def manifest_with_opf(zf: zipfile.ZipFile):
    root = safe_fromstring(zf.read("META-INF/container.xml"))
    rootfile = next(root.iter("{%s}rootfile" % NS["ocf"]), None)
    if rootfile is None or not rootfile.get("full-path"):
        raise ValueError("EPUB has no OPF rootfile")
    opf_path = rootfile.get("full-path").replace("\\", "/")
    if opf_path.startswith("/") or ".." in opf_path.split("/"):
        raise ValueError("unsafe OPF path")
    opf_dir = opf_path.rsplit("/", 1)[0] + "/" if "/" in opf_path else ""
    opf_root = safe_fromstring(zf.read(opf_path))
    manifest = {}
    for item in opf_root.iter("{%s}item" % NS["opf"]):
        iid = item.get("id") or ""
        member = zip_member(opf_dir, item.get("href") or "")
        if iid and member:
            manifest[iid] = {
                "member": member,
                "media": (item.get("media-type") or "").lower(),
                "properties": (item.get("properties") or "").lower(),
            }
    return opf_root, manifest, opf_dir


def html_image_member(zf: zipfile.ZipFile, member: str) -> str | None:
    try:
        raw = zf.read(member)
    except (KeyError, RuntimeError):
        return None
    if len(raw) > 2 * 1024 * 1024:
        return None
    text = raw.decode("utf-8", "replace")
    match = re.search(r"<(?:img|image)[^>]+(?:src|href|xlink:href)=[\"']([^\"']+)", text, re.I)
    if not match:
        return None
    parent = member.rsplit("/", 1)[0] + "/" if "/" in member else ""
    return zip_member(parent, match.group(1))


def cover_candidate(zf: zipfile.ZipFile) -> str | None:
    opf_root, manifest, opf_dir = manifest_with_opf(zf)
    names = set(zf.namelist())
    candidates = []

    # EPUB 3: explicit cover-image property.
    for item in manifest.values():
        if "cover-image" in item["properties"]:
            candidates.append(item["member"])

    # EPUB 2: <meta name="cover" content="manifest-id">.
    for element in opf_root.iter():
        if local_name(element.tag) == "meta" and (element.get("name") or "").lower() == "cover":
            item = manifest.get(element.get("content") or "")
            if item:
                candidates.append(item["member"])

    # Guide references may point directly to an image or to a cover XHTML page.
    for element in opf_root.iter():
        if local_name(element.tag) != "reference" or "cover" not in (element.get("type") or "").lower():
            continue
        member = zip_member(opf_dir, element.get("href") or "")
        if member:
            candidates.append(member)
            nested = html_image_member(zf, member)
            if nested:
                candidates.append(nested)

    # Common manifest ids/filenames, then a size-based raster fallback.
    for iid, item in manifest.items():
        haystack = (iid + " " + item["member"]).lower()
        if re.search(r"(?:^|[/_.-])(front[-_ ]?)?cover(?:[/_.-]|$)", haystack):
            candidates.append(item["member"])

    raster = [item["member"] for item in manifest.values() if item["media"] in RASTER_TYPES]
    raster.sort(key=lambda name: zf.getinfo(name).file_size if name in names else 0, reverse=True)
    candidates.extend(raster)

    seen = set()
    for member in candidates:
        if not member or member in seen:
            continue
        seen.add(member)
        if member not in names:
            continue
        if zf.getinfo(member).file_size > MAX_IMAGE_BYTES:
            continue
        if posixpath.splitext(member.lower())[1] not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            nested = html_image_member(zf, member)
            if nested and nested in names:
                return nested
            continue
        return member
    return None


def save_cover(epub_path: Path, bid: str) -> str | None:
    try:
        with zipfile.ZipFile(epub_path) as zf:
            member = cover_candidate(zf)
            if not member:
                return None
            raw = zf.read(member)
        try:
            from PIL import Image, ImageOps
            with Image.open(io.BytesIO(raw)) as image:
                image = ImageOps.exif_transpose(image)
                if image.mode not in ("RGB", "RGBA"):
                    image = image.convert("RGB")
                if image.mode == "RGBA":
                    background = Image.new("RGB", image.size, "white")
                    background.paste(image, mask=image.getchannel("A"))
                    image = background
                image.thumbnail(COVER_SIZE, Image.Resampling.LANCZOS)
                target = inside(COVER_DIR, COVER_DIR / f"{bid}.webp")
                image.save(target, "WEBP", quality=82, method=6)
                return target.relative_to(REPO).as_posix()
        except (ImportError, OSError, ValueError):
            ext = posixpath.splitext(member.lower())[1]
            if ext == ".jpeg":
                ext = ".jpg"
            target = inside(COVER_DIR, COVER_DIR / f"{bid}{ext}")
            target.write_bytes(raw)
            return target.relative_to(REPO).as_posix()
    except (OSError, zipfile.BadZipFile, KeyError, ValueError, RuntimeError):
        return None


def load_courses(taxonomy: dict | None = None) -> dict:
    taxonomy = taxonomy or json.loads((BASE / "taxonomy.json").read_text(encoding="utf-8"))
    raw = json.loads(COURSES_PATH.read_text(encoding="utf-8"))
    courses: dict[str, dict] = {}
    for record in raw:
        cid = record.get("id") or ""
        tier = record.get("tier") or ""
        if not cid or not record.get("title") or not record.get("university"):
            raise ValueError(f"course record missing id/title/university: {record!r}")
        if tier not in COURSE_TIERS:
            raise ValueError(f"course {cid}: unknown tier {tier!r}")
        if cid in courses:
            raise ValueError(f"course {cid}: duplicate id")
        concept_slugs = list(dict.fromkeys(record.get("concepts", [])))
        philosopher_slugs = list(dict.fromkeys(record.get("philosophers", [])))
        unknown = [s for s in concept_slugs if s not in taxonomy["concepts"]]
        unknown += [s for s in philosopher_slugs if s not in taxonomy["philosophers"]]
        if unknown:
            raise ValueError(f"course {cid}: unknown taxonomy slugs {unknown}")
        links = {field: record[field] for field in COURSE_LINK_FIELDS if record.get(field)}
        if not links:
            raise ValueError(f"course {cid}: no public links at all")
        courses[cid] = {
            "title": record["title"],
            "university": record["university"],
            "instructor": record.get("instructor", ""),
            "year": record.get("year", ""),
            "tier": tier,
            "format": record.get("format", ""),
            "extent": record.get("extent", ""),
            "tags": list(record.get("tags", [])),
            "description": record.get("description", ""),
            "concepts": concept_slugs,
            "philosophers": philosopher_slugs,
            "links": links,
            "source": record.get("source", ""),
            "remarks": record.get("remarks", ""),
        }
    return courses


def load_lectures(cid: str, taxonomy: dict) -> list:
    path = inside(LECTURES_DIR, LECTURES_DIR / f"{cid}.json")
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("course") != cid:
        raise ValueError(f"course_lectures/{cid}.json: course field is {payload.get('course')!r}")
    rows = []
    for item in payload.get("lectures", []):
        n = int(item["n"])
        kind = item.get("kind", "lecture")
        concepts = list(dict.fromkeys(item.get("concepts", [])))
        philosophers = list(dict.fromkeys(item.get("philosophers", [])))
        unknown = [s for s in concepts if s not in taxonomy["concepts"]]
        unknown += [s for s in philosophers if s not in taxonomy["philosophers"]]
        if unknown:
            raise ValueError(f"course {cid} lecture {n}: unknown taxonomy slugs {unknown}")
        summary = item.get("summary", "")
        if kind == "lecture" and not summary.strip():
            raise ValueError(f"course {cid} lecture {n}: empty summary on a lecture")
        rows.append({
            "n": n,
            "title": item.get("title") or f"Lecture {n}",
            "kind": kind,
            "summary": summary,
            "concepts": concepts,
            "philosophers": philosophers,
        })
    rows.sort(key=lambda row: row["n"])
    return rows


def build(data_only: bool = False) -> dict:
    merged = json.loads((BASE / "merged_index.json").read_text(encoding="utf-8"))
    taxonomy = json.loads((BASE / "taxonomy.json").read_text(encoding="utf-8"))
    intros = json.loads((BASE / "intros.json").read_text(encoding="utf-8"))
    book_intros = json.loads((BASE / "book_intros.json").read_text(encoding="utf-8"))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    COVER_DIR.mkdir(parents=True, exist_ok=True)

    used_ids = set()
    raw_to_id = {raw: book_id(raw, used_ids) for raw in sorted(merged["chapters"])}
    expected_book_ids = set(raw_to_id.values())
    actual_book_ids = set(book_intros)
    if actual_book_ids != expected_book_ids:
        missing = sorted(expected_book_ids - actual_book_ids)
        extra = sorted(actual_book_ids - expected_book_ids)
        raise ValueError(f"book intro key mismatch; missing={missing}; extra={extra}")
    epub_by_stem = {p.stem: p for p in EPUB_DIR.glob("*.epub")}
    existing_covers: dict[str, str | None] = {}
    if data_only:
        if not DATA_PATH.exists():
            raise ValueError("--data-only needs an existing data.json to reuse covers from")
        existing_payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        existing_covers = {bid: book.get("cover") for bid, book in existing_payload["books"].items()}

    books = {}
    concept_refs = defaultdict(list)
    philosopher_refs = defaultdict(list)
    cooccurrence = defaultdict(Counter)
    cover_count = 0

    for raw, bid in raw_to_id.items():
        chapter_rows = []
        domain_counts = Counter()
        for number in sorted(merged["chapters"][raw], key=int):
            record = merged["chapters"][raw][number]
            concepts = list(dict.fromkeys(record.get("concepts", [])))
            philosophers = list(dict.fromkeys(record.get("philosophers", [])))
            unknown_concepts = [slug for slug in concepts if slug not in taxonomy["concepts"]]
            unknown_philosophers = [slug for slug in philosophers if slug not in taxonomy["philosophers"]]
            if unknown_concepts or unknown_philosophers:
                raise ValueError(
                    f"{raw} chapter {number}: unknown concepts {unknown_concepts}; "
                    f"unknown philosophers {unknown_philosophers}"
                )
            for concept in concepts:
                domain = taxonomy["concepts"].get(concept, {}).get("dom")
                if domain:
                    domain_counts[domain] += 1
                concept_refs[concept].append([bid, int(number)])
                for other in concepts:
                    if other != concept:
                        cooccurrence[concept][other] += 1
            for philosopher in philosophers:
                domain = taxonomy["philosophers"].get(philosopher, {}).get("dom")
                if domain:
                    domain_counts[domain] += 1
                philosopher_refs[philosopher].append([bid, int(number)])
            chapter_rows.append({
                "n": int(number),
                "title": record.get("title") or f"Chapter {number}",
                "kind": record.get("kind", "chapter"),
                "done": bool(record.get("done")),
                "concepts": concepts,
                "philosophers": philosophers,
                "relation": record.get("relation", ""),
            })

        cover = existing_covers.get(bid) if data_only else (save_cover(epub_by_stem[raw], bid) if raw in epub_by_stem else None)
        if cover:
            cover_count += 1
        books[bid] = {
            "title": book_title(raw),
            "source": raw,
            "intro": book_intros[bid].strip(),
            "cover": cover,
            "domains": [d for d, _ in domain_counts.most_common(3)],
            "chapters": chapter_rows,
        }

    domains = {
        slug: {"name": item["n"]}
        for slug, item in taxonomy["domains"].items()
    }
    concepts = {}
    for slug, item in taxonomy["concepts"].items():
        refs = sorted(concept_refs.get(slug, []), key=lambda ref: (books[ref[0]]["title"].lower(), ref[1]))
        concepts[slug] = {
            "name": item["n"],
            "intro": intros.get(slug, ""),
            "domain": item["dom"],
            "philosopher": item.get("p") or None,
            "chapters": refs,
            "related": [[other, count] for other, count in cooccurrence[slug].most_common(8)],
        }

    philosophers = {}
    for slug, item in taxonomy["philosophers"].items():
        refs = sorted(philosopher_refs.get(slug, []), key=lambda ref: (books[ref[0]]["title"].lower(), ref[1]))
        concepts_for_philosopher = [
            [concept_slug, len(concept_refs.get(concept_slug, []))]
            for concept_slug, concept in taxonomy["concepts"].items()
            if concept.get("p") == slug
        ]
        concepts_for_philosopher.sort(key=lambda row: (-row[1], concepts[row[0]]["name"].lower()))
        philosophers[slug] = {
            "name": item["n"],
            "dates": item.get("d", ""),
            "intro": intros.get("phil:" + slug, ""),
            "domain": item["dom"],
            "concepts": concepts_for_philosopher,
            "chapters": refs,
        }

    courses = load_courses(taxonomy)
    for cid, course in courses.items():
        lectures = load_lectures(cid, taxonomy)
        course["lectures"] = lectures
        # Course-level bindings are the union of what its lectures teach.
        course["concepts"] = list(dict.fromkeys(
            slug for lecture in lectures for slug in lecture["concepts"]))
        course["philosophers"] = list(dict.fromkeys(
            slug for lecture in lectures for slug in lecture["philosophers"]))
    course_order = lambda cid: (courses[cid]["university"].lower(), courses[cid]["title"].lower())
    concept_course_refs = defaultdict(list)
    philosopher_course_refs = defaultdict(list)
    for cid, course in courses.items():
        for lecture in course["lectures"]:
            for slug in lecture["concepts"]:
                concept_course_refs[slug].append([cid, lecture["n"]])
            for slug in lecture["philosophers"]:
                philosopher_course_refs[slug].append([cid, lecture["n"]])
    for slug, concept in concepts.items():
        concept["courses"] = sorted(concept_course_refs.get(slug, []), key=lambda ref: (course_order(ref[0]), ref[1]))
    for slug, philosopher in philosophers.items():
        philosopher["courses"] = sorted(philosopher_course_refs.get(slug, []), key=lambda ref: (course_order(ref[0]), ref[1]))

    progress = dict(merged["progress"])
    progress["covers"] = cover_count
    progress["courses"] = len(courses)
    payload = {
        "version": 3,
        "stats": progress,
        "domains": domains,
        "books": books,
        "concepts": concepts,
        "philosophers": philosophers,
        "courses": courses,
    }
    return payload


def validate(payload: dict) -> None:
    errors = []
    for slug, concept in payload["concepts"].items():
        if concept["domain"] not in payload["domains"]:
            errors.append(f"concept {slug}: unknown domain")
        if concept["philosopher"] and concept["philosopher"] not in payload["philosophers"]:
            errors.append(f"concept {slug}: unknown philosopher")
        for bid, number in concept["chapters"]:
            if bid not in payload["books"] or not any(c["n"] == number and slug in c["concepts"] for c in payload["books"][bid]["chapters"]):
                errors.append(f"concept {slug}: broken chapter ref {bid}:{number}")
    for slug, philosopher in payload["philosophers"].items():
        for bid, number in philosopher["chapters"]:
            if bid not in payload["books"] or not any(c["n"] == number and slug in c["philosophers"] for c in payload["books"][bid]["chapters"]):
                errors.append(f"philosopher {slug}: broken chapter ref {bid}:{number}")
    for cid, course in payload["courses"].items():
        if course["tier"] not in COURSE_TIERS:
            errors.append(f"course {cid}: unknown tier")
        if not course["links"]:
            errors.append(f"course {cid}: no public links")
        lecture_by_n = {lecture["n"]: lecture for lecture in course["lectures"]}
        for slug in course["concepts"]:
            refs = [ref for ref in payload["concepts"].get(slug, {}).get("courses", []) if ref[0] == cid]
            if not refs or not all(ref[1] in lecture_by_n and slug in lecture_by_n[ref[1]]["concepts"] for ref in refs):
                errors.append(f"course {cid}: concept {slug} missing/broken lecture ref")
        for slug in course["philosophers"]:
            refs = [ref for ref in payload["philosophers"].get(slug, {}).get("courses", []) if ref[0] == cid]
            if not refs or not all(ref[1] in lecture_by_n and slug in lecture_by_n[ref[1]]["philosophers"] for ref in refs):
                errors.append(f"course {cid}: philosopher {slug} missing/broken lecture ref")
    for slug, concept in payload["concepts"].items():
        for ref in concept["courses"]:
            cid, n = ref
            if cid not in payload["courses"] or slug not in payload["courses"][cid]["concepts"]:
                errors.append(f"concept {slug}: broken course ref {cid}:{n}")
    for slug, philosopher in payload["philosophers"].items():
        for ref in philosopher["courses"]:
            cid, n = ref
            if cid not in payload["courses"] or slug not in payload["courses"][cid]["philosophers"]:
                errors.append(f"philosopher {slug}: broken course ref {cid}:{n}")
    if errors:
        raise ValueError("\n".join(errors[:50]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the explorer dataset (data.json + covers).")
    parser.add_argument("--data-only", action="store_true",
                        help="reuse existing cover images from the current data.json instead of re-reading the EPUBs")
    args = parser.parse_args()
    payload = build(data_only=args.data_only)
    validate(payload)
    DATA_PATH.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    stats = payload["stats"]
    print(json.dumps({
        "books": len(payload["books"]),
        "chapters": sum(len(book["chapters"]) for book in payload["books"].values()),
        "concepts": len(payload["concepts"]),
        "philosophers": len(payload["philosophers"]),
        "courses": len(payload["courses"]),
        "covers": stats["covers"],
        "data_bytes": DATA_PATH.stat().st_size,
    }, indent=2))


if __name__ == "__main__":
    main()
