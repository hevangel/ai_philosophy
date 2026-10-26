"""Convert downloaded YouTube caption VTTs into corpus-standard markdown.

Input:  data/philosophy_readings/youtube/<video_id>.<lang>.vtt (auto or manual subs)
        sratchpad/textbook_index/carneades_videos.txt  ("id|title" lines)
Output: data/philosophy_readings/youtube/<id> - <title>.md, VTT deleted on success.

Auto-caption VTTs use rolling cues — the last text line of each cue is the new
content, so we keep exactly that per cue and skip tag-bearing lines.
"""
import re
from pathlib import Path

YT_DIR = Path(r"B:\ai_philosophy\data\philosophy_readings\youtube")
LIST_PATH = Path(r"B:\ai_philosophy\sratchpad\textbook_index\carneades_videos.txt")
BAD_FN = re.compile(r'[<>:"/\\|?*]')


def checked_path(base, rel):
    p = (base / rel).resolve()
    b = base.resolve()
    import os
    if p.anchor != b.anchor or not (str(p) == str(b)
                                    or str(p).startswith(str(b) + os.sep)):
        raise ValueError("resolved path outside allowed root: %s" % p)
    return p


def sanitize(title):
    t = BAD_FN.sub(" ", title)
    return re.sub(r"\s+", " ", t).strip().strip(".")[:120].rstrip() or "untitled"


def cue_texts(vtt):
    """Yield the new text of each caption cue."""
    lines = vtt.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if "-->" in line:
            # cue body: following lines until blank
            j = i + 1
            body = []
            while j < n and lines[j].strip():
                text = lines[j].strip()
                if "<" not in text and "&gt;" not in text:
                    body.append(text)
                j += 1
            if body:
                yield body[-1]
            i = j
        else:
            i += 1


def dedupe_rolling(parts):
    """Auto-subs repeat partial text across cues; drop consecutive duplicates
    and lines fully contained in their predecessor."""
    out = []
    for p in parts:
        if out and (p == out[-1] or p in out[-1]):
            continue
        if out and out[-1] in p and len(p) <= len(out[-1]) + 40:
            out[-1] = p
            continue
        out.append(p)
    return out


def main():
    titles = {}
    for line in LIST_PATH.read_text(encoding="utf-8").splitlines():
        if "|" in line:
            vid, title = line.split("|", 1)
            titles[vid] = title.strip()

    md_files = stub_files = 0
    for vtt in sorted(YT_DIR.glob("*.vtt")):
        vid = vtt.name.split(".")[0]
        try:
            parts = list(cue_texts(vtt.read_text(encoding="utf-8", errors="replace")))
            text = " ".join(dedupe_rolling(parts))
            text = re.sub(r"[ \t]+", " ", text).strip()
            if len(text) < 200:
                # near-empty captions — keep as stub rather than drop
                header_note = ("\n\n*(Auto-captions were unavailable or nearly"
                               " empty for this video; no transcript text.)*\n")
                body = header_note
                stub_files += 1
            else:
                paras = []
                words = text.split(" ")
                for k in range(0, len(words), 90):
                    paras.append(" ".join(words[k:k + 90]))
                body = "\n\n".join(paras) + "\n"
                md_files += 1
            title = sanitize(titles.get(vid, vid))
            out = checked_path(YT_DIR, f"{vid} - {title}.md")
            out.write_text(
                "# %s\n\n*Carneades.org — https://www.youtube.com/watch?v=%s"
                " (auto-generated captions)*\n\n%s" % (
                    titles.get(vid, vid), vid, body),
                encoding="utf-8")
            vtt.unlink()
        except Exception as e:
            print("ERROR %s: %r" % (vid, e))
    print("converted: %d transcripts, %d empty-caption stubs, %d left"
          % (md_files, stub_files, len(list(YT_DIR.glob('*.vtt')))))


if __name__ == "__main__":
    main()
