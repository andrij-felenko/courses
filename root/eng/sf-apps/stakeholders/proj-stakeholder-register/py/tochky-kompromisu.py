from collections import defaultdict

@dataclass
class Tradeoff:
    param: str
    up_attr: Attr
    up_who: str
    down_attr: Attr
    down_who: str

def tradeoff_points(reg: list[Stakeholder], params: list[Parameter]) -> list[Tradeoff]:
    # Один прохід: групуємо ЛИШЕ високовагомих за їхньою турботою.
    by_concern: dict[Attr, list[Stakeholder]] = defaultdict(list)
    for s in reg:
        if salience_score(s) >= HIGH_SALIENCE:
            by_concern[s.concern].append(s)

    out: list[Tradeoff] = []
    for p in params:
        up   = [x for x in p.pushes if x.dir > 0]  # хто виграє від параметра
        down = [x for x in p.pushes if x.dir < 0]  # хто програє
        for u in up:
            for d in down:                          # лише ПРОТИЛЕЖНІ знаки
                for su in by_concern.get(u.attr, ()):
                    for sd in by_concern.get(d.attr, ()):
                        if su.name == sd.name:
                            continue                # не зіштовхуй людину з нею ж
                        out.append(Tradeoff(p.name, u.attr, su.name, d.attr, sd.name))
    return out
