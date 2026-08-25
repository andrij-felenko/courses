# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN = "#caa24a"
WARNBG = "#fff6e0"


# ── preflight-gate: чеклист як брама на точці неповернення ─────────────────────
# Ідея: підготовка ліворуч → всі умови зводяться логічним І в один вирок
# (вертикальна брама посередині) → небезпечний режим праворуч. Провал бодай
# однієї умови тримає браму зачиненою. Показуємо: список умов → І → замок/брама
# → «поїхали», а знизу — стрілка «дороги назад нема».
def fig_preflight_gate():
    W, H = 900, 470
    p = []

    # ── ліва зона: підготовка + список умов ──
    lx, ltop, lw, lh = 30, 70, 300, 340
    p.append(rect(lx, ltop, lw, lh, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    p.append(text(lx + lw / 2, ltop + 26, "Підготовка", size=14, color=FIELD, bold=True))
    p.append(text(lx + lw / 2, ltop + 45, "готовність підсистем", size=10, color=MUTED, italic=True))
    p.append(line(lx + 16, ltop + 56, lx + lw - 16, ltop + 56, color=FIELD, sw=1, dash="4 3"))

    conds = [
        ("живлення", True),
        ("фікс GPS", True),
        ("компас", True),
        ("зв'язок з RC", False),   # ця умова НЕ виконана — тримає браму
        ("давачі IMU", True),
    ]
    row_y = []
    for i, (name, ok) in enumerate(conds):
        y = ltop + 74 + i * 50
        row_y.append(y + 21)
        col = FIELD if ok else POS
        bg = BG if ok else "#fdecea"
        p.append(rect(lx + 16, y, lw - 32, 40, fill=bg, stroke=col, sw=1.4, rx=8))
        if ok:
            p.append(text(lx + 34, y + 26, "✓", size=17, color=FIELD, bold=True, anchor="middle"))
        else:
            p.append(text(lx + 34, y + 26, "✗", size=17, color=POS, bold=True, anchor="middle"))
        p.append(text(lx + 54, y + 25, name, size=12, color=INK, bold=not ok, anchor="start"))

    # ── брама посередині: логічне І ──
    gx = lx + lw + 78          # центр брами по X
    gtop, gbot = ltop + 20, ltop + lh - 20
    # стовп брами
    p.append(rect(gx - 26, gtop, 52, gbot - gtop, fill="#f0f0f2", stroke=INK, sw=2, rx=10))
    p.append(text(gx, (gtop + gbot) / 2 - 8, "І", size=30, color=INK, bold=True))  # І
    p.append(text(gx, (gtop + gbot) / 2 + 20, "усі", size=11, color=MUTED))
    p.append(text(gx, (gtop + gbot) / 2 + 34, "умови", size=11, color=MUTED))
    # лінії від кожної умови до брами
    for i, (y, (_, ok)) in enumerate(zip(row_y, conds)):
        col = FIELD if ok else POS
        p.append(line(lx + lw, y, gx - 26, (gtop + gbot) / 2, color=col, sw=1.4,
                      dash=None if ok else "5 4"))
    # замок на брамі (зачинена, бо є червона умова)
    lock_y = gtop - 4
    p.append(rect(gx - 12, lock_y, 24, 20, fill="#fdecea", stroke=POS, sw=2, rx=4))
    p.append('<path d="M%.1f %.1f a8 8 0 0 1 16 0 v6 h-4 v-6 a4 4 0 0 0 -8 0 v6 h-4 z" fill="none" stroke="%s" stroke-width="2"/>' % (gx - 8, lock_y, POS))

    # ── права зона: небезпечний режим ──
    rx0, rtop, rw, rh = W - 30 - 250, 70, 250, 340
    p.append(rect(rx0, rtop, rw, rh, fill="#fbeeee", stroke=POS, sw=2, rx=12))
    p.append(text(rx0 + rw / 2, rtop + 26, "Небезпечний режим", size=13, color=POS, bold=True))
    p.append(text(rx0 + rw / 2, rtop + 45, "зброєно, мотори живі", size=10, color=MUTED, italic=True))
    p.append(line(rx0 + 16, rtop + 56, rx0 + rw - 16, rtop + 56, color=POS, sw=1, dash="4 3"))
    b2, w2, h2 = textbox(rx0 + rw / 2, rtop + rh / 2 - 10,
                         "старт дозволено\n⇔\nкожна умова\nвиконана", size=12,
                         fill=BG, stroke=POS, sw=1.5, pad=14, color=INK)
    p.append(b2)
    p.append(text(rx0 + rw / 2, rtop + rh - 26, "пускають лише при", size=10, color=MUTED, italic=True))
    p.append(text(rx0 + rw / 2, rtop + rh - 12, "повному «зелено»", size=10, color=MUTED, italic=True))

    # стрілка від брами до правої зони (перекреслена — зачинено)
    ay = (gtop + gbot) / 2
    p.append(line(gx + 26, ay, rx0 - 6, ay, color=MUTED, sw=1.8, dash="6 5"))
    p.append(text((gx + 26 + rx0) / 2, ay - 10, "зачинено", size=10, color=POS, italic=True))
    p.append(text((gx + 26 + rx0) / 2, ay + 20, "1 умова ✗", size=9.5, color=POS))

    # нижня підпис-стрічка: дороги назад нема
    p.append(text(W / 2, H - 16,
                  "провал бодай однієї умови тримає браму зачиненою; після брами дороги назад нема",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "preflight-gate.svg"), W, H, *p,
           title="Передпольотний чеклист — брама на точці неповернення")


# ── checklist-lineage: одна ідея, що переходить з галузі в галузь ─────────────
# Ідея: інваріант «формалізуй перевірку, не довіряй пам'яті» народжується в
# авіації (1935) і мігрує далі — медицина (2009), розробка ПЗ. Показуємо
# горизонтальну вісь часу з чотирма станціями; над кожною — короткий факт;
# наскрізна стрічка внизу тримає той самий незмінний принцип.
def fig_checklist_lineage():
    W, H = 900, 430
    p = []

    axis_y = 250
    x0, x1 = 90, W - 90
    p.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.5))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
             % (x1, axis_y - 7, x1 + 14, axis_y, x1, axis_y + 7, INK))

    # станції: (частка по осі, рік, заголовок, факт-рядки, колір-акцент)
    stations = [
        (0.00, "1935", "Райт-Філд", ["крах Model 299:", "забутий gust lock", "→ перший чеклист"], POS),
        (0.34, "1935+", "Авіація", ["12 машин —", "1.8 млн миль", "без аварій"], FIELD),
        (0.68, "2009", "Медицина", ["чеклист ВООЗ:", "смертність", "1.5% → 0.8%"], NEG),
        (1.00, "нині", "Код", ["preflight_check()", "перед точкою", "неповернення"], INK),
    ]

    for frac, year, head, facts, col in stations:
        x = x0 + (x1 - x0) * frac
        # вузол на осі
        p.append(circle(x, axis_y, 9, fill=BG, stroke=col, sw=3))
        p.append(circle(x, axis_y, 3.2, fill=col, stroke=col, sw=1))
        # рік — під віссю
        p.append(text(x, axis_y + 30, year, size=14, color=col, bold=True))
        # картка факту — над віссю
        box, bw, bh = textbox(x, axis_y - 78, head + "\n" + "\n".join(facts),
                              size=11.5, fill=BG, stroke=col, sw=1.6, pad=11, color=INK, rx=10)
        # перший рядок (заголовок) робимо жирним окремо: перекладаємо textbox на fitbox важко,
        # тож лишаємо єдиним блоком, але заголовок виділяємо кольором через окремий text зверху
        p.append(box)
        # тонка ніжка від картки до вузла
        p.append(line(x, axis_y - 78 + bh / 2, x, axis_y - 9, color=col, sw=1.2, dash="3 3"))

    # наскрізна стрічка внизу: незмінний принцип
    ribbon_y = axis_y + 86
    b, bw, bh = textbox(W / 2, ribbon_y,
                        "той самий інваріант: «формалізуй перевірку — не довіряй пам'яті»",
                        size=13, fill="#eef6ef", stroke=FIELD, sw=1.6, pad=13, color=INK, rx=12)
    p.append(b)
    # стрілки уздовж — ідея тече зліва направо крізь галузі
    p.append(text(W / 2, ribbon_y + bh / 2 + 22,
                  "галузь міняється — принцип ні", size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "checklist-lineage.svg"), W, H, *p,
           title="Родовід чеклиста: злітна смуга → операційна → код")


if __name__ == "__main__":
    fig_preflight_gate()
    fig_checklist_lineage()
    print("OK: figures written to", OUT)
