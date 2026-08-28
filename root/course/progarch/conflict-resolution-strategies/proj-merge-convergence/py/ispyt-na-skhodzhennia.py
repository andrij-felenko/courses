import random

def lww_key(s):
    return "∅" if s is None else (tuple(sorted(s["val"])), s["ts"], s["node"])
def sib_key(s):
    return tuple(sorted((tuple(sorted(v["list"])), tuple(sorted(v["vv"].items()))) for v in s))
def _dump(m):
    return tuple(sorted((e, tuple(sorted(t))) for e, t in m.items()))
def or_key(s):
    return (_dump(s["add"]), _dump(s["rem"]))

def converge(merge, empty, frags, key, replicas=1000):
    seen = set()
    for _ in range(replicas):
        repeats = random.sample(frags, k=random.randint(0, len(frags)))
        order = frags + repeats
        random.shuffle(order)                     # випадковий порядок + повтори
        st = empty
        for f in order:
            st = merge(st, f)
        seen.add(key(st))
    return len(seen)                              # 1 ⟺ усі репліки зійшлися

assert converge(lww_merge, None, lww_frags, lww_key) == 1, "LWW не зійшовся"
assert converge(sib_merge, [],   sib_frags, sib_key) == 1, "двійники не зійшлися"
assert converge(or_merge, {"add": {}, "rem": {}}, or_frags, or_key) == 1, "OR-Set не зійшовся"
