# owner_of(шлях) -> контекст за найдовшим коренем і сам сканер import-ів —
# ті самі, що в загальній перевірці; тут лише DH-вирок поверх знайдених ребер.
def verdict(frm, to, target):
    if frm == to:
        return None                              # всередині контексту — вільно
    dst = MAP.get(to)
    if dst is None:
        return None                              # зовнішній пакет — окрема перевірка (див. пастки)
    pair_ok = dst.get("open") or to in MAP[frm]["allow"]
    if not pair_ok:
        return f"неоголошене ребро {frm} → {to}"
    if not target.startswith(dst["pub"]):
        return f"{frm} тягне НУТРОЩІ {to}: {target} (лише {dst['pub']})"
    return None

def audit(imports, owner_of):                     # imports: [(файл-джерело, ціль-модуль), …]
    bad = []
    for from_file, target in imports:
        frm, to = owner_of(from_file), owner_of(target)
        if frm is None or to is None:
            continue                              # поза мапою — не наша межа
        v = verdict(frm, to, target)
        if v:
            bad.append(v)
        if MAP.get(to, {}).get("isolated") and frm != to:  # окремі шляхи: у video не входить ніхто ЗЗОВНІ
            bad.append(f"окремі шляхи порушено: {frm} → {to}")
        if frm in ("events", "ids") and to != frm:  # шина й ядро мусять бути листками
            bad.append(f"{frm} має бути листком, а тягне {to}")
    return bad

def main(imports, owner_of):
    bad = audit(imports, owner_of)
    if not bad:
        print("мапа DH тримається")
        return 0
    print("АРХІТЕКТУРНІ ПОРУШЕННЯ DH:")
    for b in bad:
        print("  " + b)
    return 1                                       # exit 1 → крок CI червоний → merge заблоковано
