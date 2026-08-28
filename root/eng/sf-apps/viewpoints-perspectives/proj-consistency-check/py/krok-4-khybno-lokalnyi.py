@dataclass
class FalseLocal:
    frm: str
    to: str
    why: str

def check_false_local(desc: Description,
                      groups: list[list[Manifestation]]) -> list[FalseLocal]:
    # функц. елемент → його вузли розгортання (через групу відповідностей)
    info: dict[str, tuple[list[str], str]] = {}
    for group in groups:
        fe = next((m for m in group if m.view == "functional"), None)
        dep = next((m for m in group if m.view == "deployment"), None)
        if fe is not None:
            nodes = desc.deployment.hosts.get(dep.id, []) if dep else []
            info[fe.id] = (nodes, fe.label)

    # мережеві зв'язки в обидва боки — для O(1) перевірки «чи є мережа»
    linked: set[tuple[str, str]] = set()
    for x, y in desc.deployment.links:
        linked.add((x, y)); linked.add((y, x))

    def crosses(a: list[str], b: list[str]) -> bool:
        return any(na != nb and (na, nb) in linked for na in a for nb in b)

    bad: list[FalseLocal] = []
    for call in desc.calls:
        if call.kind != "local":                         # перевіряємо лише заявлені local
            continue
        a = info.get(call.frm); b = info.get(call.to)
        if a is None or b is None:
            continue
        (a_nodes, a_lbl), (b_nodes, b_lbl) = a, b
        if len(b_nodes) > 1:
            bad.append(FalseLocal(a_lbl, b_lbl,
                f"ціль реплікована на {len(b_nodes)} вузли — виклик іде через балансувальник (мережа)"))
        elif crosses(a_nodes, b_nodes):
            bad.append(FalseLocal(a_lbl, b_lbl, "кінці на різних вузлах, з'єднаних мережею"))
    return bad
