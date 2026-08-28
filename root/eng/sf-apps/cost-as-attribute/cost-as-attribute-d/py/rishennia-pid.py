# (ймовірність, вартість крихкого, вартість стійкого) за сценаріями навантаження, тис. $
scenarios = [
    ("низьке",     0.3,  8, 12),
    ("очікуване",  0.5, 10, 14),
    ("високе",     0.2, 60, 22),   # крихкий падає й тягне аварійні витрати
]
exp_fragile = sum(p * f for _, p, f, _ in scenarios)
exp_robust  = sum(p * r for _, p, _, r in scenarios)
worst_fragile = max(f for _, _, f, _ in scenarios)
worst_robust  = max(r for _, _, _, r in scenarios)
print(f"очікувана:  крихкий={exp_fragile:.1f}  стійкий={exp_robust:.1f}")
print(f"найгірша:   крихкий={worst_fragile}     стійкий={worst_robust}")
