CMP = {">": lambda a, b: a > b, ">=": lambda a, b: a >= b,
       "<": lambda a, b: a < b, "<=": lambda a, b: a <= b}


def check_sync(markers, journal):
    out = []
    by_id = {d.id: d for d in journal}
    marked = {mid for mid, _ in markers}

    for mid, at in markers:                          # напрям 1: маркер → запис
        d = by_id.get(mid)
        if d is None:
            out.append((mid, f"маркер у {at} без запису в журналі"))
        elif d.state == "closed":
            out.append((mid, f"маркер у {at} на ЗАКРИТОМУ записі — прибрати з коду"))
    for d in journal:                                # напрям 2: відкритий запис → маркер
        if d.state != "open":
            continue
        if d.id not in marked:
            out.append((d.id, "відкритий запис без жодного маркера в коді"))
        if not d.owner.strip():
            out.append((d.id, "відкритий борг без власника"))
    return out


def check_overdue(journal, metrics):
    out = []
    for d in journal:
        if d.state != "open":
            continue
        for c in d.trigger:
            if c.metric not in metrics:              # метрики нема у знімку → перевірити НЕ можемо
                out.append((d.id, f'тригер зважає на метрику "{c.metric}", якої нема у знімку — перевірити нема як'))
            elif CMP[c.op](metrics[c.metric], c.threshold):  # тригер став правдою, борг відкритий → прострочено
                out.append((d.id, f"ПРОСТРОЧЕНО: {c.metric}={metrics[c.metric]} {c.op} {c.threshold} — гасити (власник: {d.owner or '—'})"))
    return out
