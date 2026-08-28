MARKER = re.compile(r"DEBT\((DH-\d+)\)")          # # DEBT(DH-014) — саме мітка, не слово


def scan_markers(root: Path):
    out = []
    for f in root.rglob("*"):
        if f.suffix not in (".py", ".sql"):
            continue
        for i, ln in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in MARKER.finditer(ln):
                out.append((m.group(1), f"{f.relative_to(root).as_posix()}:{i}"))
    return out
