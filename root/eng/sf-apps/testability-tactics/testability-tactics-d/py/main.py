# Велика DRR: 1001 входів → 3 виходи. Дефект на межі невидимий майже завжди.
def risk_level(score: int) -> str:          # score ∈ 0..1000
    if score < 300:
        return "low"
    if score < 710:                          # ЗАДУМАНО 700 — зсунуто на 10
        return "medium"
    return "high"

# Випадковий тест майже певно дасть «medium»==«medium» або «high»==«high»:
# дефект проявляється лише на 10 балах зі щілини [700, 710).
