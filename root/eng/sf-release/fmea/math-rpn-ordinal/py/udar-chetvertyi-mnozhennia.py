from collections import defaultdict

by = defaultdict(list)
for s in range(1, 11):
    for o in range(1, 11):
        for d in range(1, 11):
            by[s * o * d].append((s, o, d))

for v in (60, 144, 240):
    ss = [t[0] for t in by[v]]
    shapes = sorted({tuple(sorted(t)) for t in by[v]})
    print(f"RPN={v}: {len(by[v])} трійок, тяжкість S={min(ss)}…{max(ss)}, набори {shapes}")

# RPN=60:  24 трійки, тяжкість S=1…10, набори [(1,6,10),(2,3,10),(2,5,6),(3,4,5)]
# RPN=144: 18 трійок, тяжкість S=2…9,  набори [(2,8,9),(3,6,8),(4,4,9),(4,6,6)]
# RPN=240: 18 трійок, тяжкість S=3…10, набори [(3,8,10),(4,6,10),(5,6,8)]
