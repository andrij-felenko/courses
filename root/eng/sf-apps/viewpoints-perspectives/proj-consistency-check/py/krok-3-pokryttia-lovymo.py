@dataclass
class Orphan:
    element: str
    missing: list[View]

def check_coverage(groups: list[list[Manifestation]],
                   required: list[View]) -> list[Orphan]:
    orphans: list[Orphan] = []
    for group in groups:
        fe = next((m for m in group if m.view == "functional"), None)
        if fe is None:                                   # група без функц. елемента — не тут
            continue
        views = {m.view for m in group}
        missing = [v for v in required if v not in views]  # ← обхід required × ця група
        if missing:
            orphans.append(Orphan(fe.label, missing))
    return orphans
