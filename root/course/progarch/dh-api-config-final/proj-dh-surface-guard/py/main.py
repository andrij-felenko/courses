# Sig:   {"kind":"scalar","type":"number"} | {"kind":"enum","open":True,"values":[...]}
# Field: {"sig": Sig, "required": bool};   Surface: dict[str, Field]

def break_of(base: dict, cur: dict) -> str | None:
    if base["required"] and not cur["required"]:
        return "поле більше не гарантоване (було обовʼязкове)"
    b, c = base["sig"], cur["sig"]
    if b["kind"] != c["kind"]:
        return f"тип змінив природу: {b['kind']} → {c['kind']}"
    if b["kind"] == "scalar" and b["type"] != c["type"]:
        return f"тип поля: {b['type']} → {c['type']}"
    if b["kind"] == "enum":
        removed = [v for v in b["values"] if v not in c["values"]]
        if removed:
            return "зникло значення переліку: " + ", ".join(removed)
        added = [v for v in c["values"] if v not in b["values"]]
        if added and not b["open"]:
            return "новий стан у ЗАКРИТОМУ переліку: " + ", ".join(added)
        if b["open"] and not c["open"]:
            return "відкритий перелік став закритим"
    return None

def diff_surface(base: dict, cur: dict, deprecated: set[str]) -> list[dict]:
    out = []
    for path, bf in base.items():
        if path not in cur:
            if path not in deprecated:
                out.append({"path": path, "reason": "поле зникло без запису про деприкейшн"})
            continue                       # є запис → кероване вилучення
        why = break_of(bf, cur[path])
        if why:
            out.append({"path": path, "reason": why})
    return out
