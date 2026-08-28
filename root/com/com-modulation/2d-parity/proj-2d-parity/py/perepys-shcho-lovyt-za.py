from itertools import combinations

cells = [(r, c) for r in range(5) for c in range(5)]
W0 = encode(DATA)

for weight in range(0, 5):
    t = {"CLEAN": 0, "FIXED_ok": 0, "FIXED_wrong": 0, "DETECTED": 0}
    for pat in combinations(cells, weight):
        verdict, out, loc = decode(corrupt(W0, pat))
        if verdict == FIXED:
            t["FIXED_ok" if out == W0 else "FIXED_wrong"] += 1
        else:
            t[verdict] += 1
    print("  вага %d: усього %5d | CLEAN %3d | виправлено-вірно %5d | ХИБНО %4d | виявлено %5d"
          % (weight, sum(t.values()), t["CLEAN"], t["FIXED_ok"], t["FIXED_wrong"], t["DETECTED"]))
