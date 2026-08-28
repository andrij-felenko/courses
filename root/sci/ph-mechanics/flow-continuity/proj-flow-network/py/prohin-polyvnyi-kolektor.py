LPM = 1.0 / 60000.0                        # л/хв → м³/с (лише для розміру)

demand = {"C1": 10.0, "C2": 6.0, "C3": 4.0}          # л/хв, що забирає кожен вихід
supply = {n: -q for n, q in demand.items()}          # стоки — від'ємні
supply["P"] = -sum(supply.values())                  # джерело подає рівно суму → +20

branches = [("P", "J1"), ("J1", "C1"), ("J1", "J2"), ("J2", "C2"), ("J2", "C3")]
flow = solve_flow_network(branches, supply)

for u, v in branches:
    q = flow[(u, v)]
    A, d = size_round(q * LPM, 1.5)                   # цільова швидкість 1.5 м/с
    print(f"{u}→{v}: Q = {q:4.1f} л/хв   ⌀ = {d*1000:5.1f} мм")
