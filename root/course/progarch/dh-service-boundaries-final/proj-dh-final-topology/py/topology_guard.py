# arch/topology_guard.py — сторож фінальної топології DH. Валить збірку на ТРЬОХ зрадах.
# Джерело правди — DEPLOYMENTS і SEAMS; тут лише вирок над знайденим у коді.
from collections import defaultdict
from topology import DEPLOYMENTS, SEAMS

DECLARED = {(s["from"], s["to"]): s["style"] for s in SEAMS}          # шов → стиль
KNOWN_DBS = {d["db"] for d in DEPLOYMENTS.values() if d.get("db")}

# Сканер уже пройшов код кожного сервіса й дав чотири списки знайденого:
#   calls   = [(сервіс, ціль)]   ← rpc.call("<ціль>")        — СИНХРОННИЙ шов
#   pubs    = [(сервіс, топік)]  ← bus.publish("<топік>")    — асинхронний
#   subs    = [(сервіс, топік)]  ← bus.subscribe("<топік>")
#   db_refs = [(сервіс, база)]   ← DSN / "<база>."           — доступ до бази

def observed(scan):
    """Синхронне ребро видно на місці виклику; асинхронне ВІДНОВЛЮЄМО як
       'продюсери × споживачі топіка' — бо продюсер називає ТОПІК, не ціль."""
    edges = [(frm, to, "sync") for frm, to in scan["calls"]]
    pubs_by_topic = defaultdict(list)
    for dep, topic in scan["pubs"]:
        pubs_by_topic[topic].append(dep)
    for sub, topic in scan["subs"]:
        for pub in pubs_by_topic[topic]:
            if pub != sub:
                edges.append((pub, sub, "async"))                    # ребро pub → sub
    return edges

def violations(scan):
    bad, edges = [], observed(scan)
    for frm, to, kind in edges:                                      # 1) РЕБРО ПОЗА МАПОЮ
        if (frm, to) not in DECLARED:
            bad.append(f"ребро поза мапою: {frm} -> {to} ({kind})")
    for dep, db in scan["db_refs"]:                                  # 2) ЧУЖА БАЗА
        if db in KNOWN_DBS and DEPLOYMENTS.get(dep, {}).get("db") != db:
            bad.append(f"чужа база: {dep} читає {db} (володіє нею інший сервіс)")
    for frm, to, kind in edges:                                      # 3) СТИЛЬ ЗРАДЖЕНО
        if kind == "sync" and DECLARED.get((frm, to)) == "async":
            bad.append(f"шов {frm} -> {to} оголошено асинхронним, а зустрів синхронний rpc.call")
    return bad

def main(scan):
    bad = violations(scan)
    if not bad:
        print("топологія DH тримається")
        return 0
    print("ЗРАДА ТОПОЛОГІЇ DH:")
    for b in bad:
        print("  " + b)
    return 1                        # exit 1 → CI кожного сервіса червоний → merge заблоковано
