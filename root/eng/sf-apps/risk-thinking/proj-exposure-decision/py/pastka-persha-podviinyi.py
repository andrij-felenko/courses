from dataclasses import dataclass

@dataclass
class Risk:
    name: str
    p: float
    loss: float
    group: int = 0   # 0 = незалежний; однакове ненульове = зчеплені між собою

# Експозиція варіанта з урахуванням зчеплення.
# Незалежні ризики додаємо як є. Кожну групу зчеплених згортаємо в ОДИН
# доданок: ймовірність «спрацював хоч один» = 1 − Π(1 − p_i),
# а втрата — найбільша в групі (спільна скеля коштує стільки, скільки
# коштує найгірший її прояв, а не сума проявів того самого лиха).
def total_exposure_grouped(v: Variant) -> float:
    sum_ = 0.0
    # спочатку незалежні
    for r in v.risks:
        if r.group == 0:
            sum_ += exposure(r)

    # тепер групи: збираємо номери груп, що реально трапилися
    groups = {r.group for r in v.risks if r.group != 0}
    for g in groups:
        p_none = 1.0    # ймовірність, що ЖОДЕН у групі не спрацював
        max_loss = 0.0  # найбільша втрата в групі
        for r in v.risks:
            if r.group == g:
                p_none *= (1.0 - r.p)
                max_loss = max(max_loss, r.loss)
        p_any = 1.0 - p_none   # об'єднання, не сума
        sum_ += p_any * max_loss
    return sum_
