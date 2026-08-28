def lint(d: Decision, history: list[Window]) -> list[str]:
    warn: list[str] = []
    if not d.uncertainty.strip():
        warn.append("невизначеність не названо — це прокрастинація, не відкладання")
    if len(d.options) < 2:
        warn.append("менше двох живих опцій — вибір уже зроблено за замовчуванням")
    if not d.trigger.conditions:
        warn.append("тригер без умов — спрацює будь-коли")
    if d.trigger.lead_weeks <= 0:
        warn.append("lead_weeks ≤ 0: стріляємо на пробитому порозі — спізнимось на час втілення")
    for c in d.trigger.conditions:
        no_band = c.fire_at < c.arm_at if c.direction == "rising" else c.fire_at > c.arm_at
        if no_band:
            warn.append(f"{c.signal}: fire по той бік arm — смуги гістерезису немає")
    # «Тригер, що не спрацює ніколи»: чи хоч раз спрацював би на історії?
    if history and not any(is_firing(d.trigger, w) for w in history):
        warn.append("на всій історії тригер не спрацював би жодного разу — поріг недосяжний?")
    return warn
