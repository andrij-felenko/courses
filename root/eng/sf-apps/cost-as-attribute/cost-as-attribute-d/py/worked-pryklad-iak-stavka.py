def annuity_factor(r, years=5):
    # A(r) = сума 1/(1+r)^t за t=1..years — згортає рівний річний потік у теперішню суму
    return sum(1 / (1 + r) ** t for t in range(1, years + 1))

def pv_build(r):   # 150 наперед + 20/рік підтримки
    return 150 + 20 * annuity_factor(r)

def pv_buy(r):     # 60/рік підписки, нічого наперед
    return 60 * annuity_factor(r)

for r in (0.10, 0.35):
    b, s = pv_build(r), pv_buy(r)
    winner = "збудувати" if b < s else "купити"
    print(f"r={r:.0%}: build={b:.1f}  buy={s:.1f}  → {winner}")
