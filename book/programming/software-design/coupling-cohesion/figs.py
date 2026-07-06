# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Дві драбини: зв'язність (вгору) і зчеплення (вниз) ───────────────────────
def fig_two_ladders():
    W, H = 980, 620
    frags = []
    rung_h = 54
    box_w = 320
    top = 96

    # Правило згори по центру
    rule, rw, rh = textbox(W / 2, 52, "Мета: висока зв'язність, слабке зчеплення",
                           size=15, bold=True, fill="#eef4ff", stroke=INK, sw=1.8, pad=12)
    frags.append(rule)

    # ── ЛІВА драбина: зв'язність (згори найкраща → внизу найгірша) ──
    lx = 56
    frags.append(text(lx + box_w / 2, top - 14, "Зв'язність — тягнути ВГОРУ",
                      size=14, bold=True, anchor="middle"))
    cohesion = [  # зверху вниз: найкраща → найгірша
        ("Функційна", "одне чітке завдання", FIELD),
        ("Послідовна", "вихід → вхід наступного", FIELD),
        ("Комунікаційна", "ті самі дані", "#5aa469"),
        ("Процедурна", "спільний порядок кроків", MUTED),
        ("Часова", "робиться в один час", MUTED),
        ("Логічна", "схожі за категорією", POS),
        ("Випадкова", "не пов'язане нічим", POS),
    ]
    for i, (nm, desc, col) in enumerate(cohesion):
        yy = top + i * (rung_h + 8)
        frags.append(rect(lx, yy, box_w, rung_h,
                          fill="#f2faf5" if col == FIELD else FILL, stroke=col, sw=1.6, rx=7))
        frags.append(text(lx + 16, yy + 23, nm, size=13, bold=True, color=INK, anchor="start"))
        frags.append(text(lx + 16, yy + 42, desc, size=11, color=MUTED, anchor="start"))
    ay = top + len(cohesion) * (rung_h + 8)
    frags.append(arrow(lx - 22, ay - 8, lx - 22, top + 8, color=FIELD, sw=2.4))
    frags.append(text(lx - 40, (top + ay) / 2, "краще", size=11, bold=True,
                      color=FIELD, anchor="middle"))

    # роздільник
    frags.append(line(W / 2, top - 34, W / 2, H - 22, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ПРАВА драбина: зчеплення (згори найгірше → внизу найкраще) ──
    rx = W / 2 + 40
    frags.append(text(rx + box_w / 2, top - 14, "Зчеплення — тягнути ВНИЗ",
                      size=14, bold=True, anchor="middle"))
    coupling = [  # зверху вниз: найгірше → найкраще
        ("За вмістом", "лізе в чужі нутрощі", POS),
        ("Спільне", "спільна глобальна змінна", POS),
        ("Зовнішнє", "нав'язаний формат / протокол", MUTED),
        ("Керівне", "прапорець-команда чужій логіці", MUTED),
        ("За зліпком", "ціла структура заради двох полів", "#5aa469"),
        ("За даними", "лише потрібні параметри", FIELD),
    ]
    for i, (nm, desc, col) in enumerate(coupling):
        yy = top + i * (rung_h + 8)
        frags.append(rect(rx, yy, box_w, rung_h,
                          fill="#f2faf5" if col == FIELD else FILL, stroke=col, sw=1.6, rx=7))
        frags.append(text(rx + 16, yy + 23, nm, size=13, bold=True, color=INK, anchor="start"))
        frags.append(text(rx + 16, yy + 42, desc, size=11, color=MUTED, anchor="start"))
    ay2 = top + len(coupling) * (rung_h + 8)
    frags.append(arrow(rx + box_w + 22, top + 8, rx + box_w + 22, ay2 - 8, color=FIELD, sw=2.4))
    frags.append(text(rx + box_w + 40, (top + ay2) / 2, "краще", size=11, bold=True,
                      color=FIELD, anchor="middle"))

    render(os.path.join(IMG, 'two-ladders.svg'), W, H, *frags,
           title="Дві осі: зв'язність усередині, зчеплення назовні")


# ── Драбина зчеплюваності: статичні знизу → динамічні вгорі ──────────────────
def fig_connascence_ladder():
    W, H = 860, 720
    frags = []
    box_w = 560
    box_h = 50
    gap = 12
    left = 160
    bottom = H - 60

    # Щаблі знизу вгору: (назва, пояснення, статична?)
    rungs = [
        ("За іменем (name)", "домовитися про НАЗВУ — foo()", True),
        ("За типом (type)", "домовитися про ТИП сутності", True),
        ("За змістом (meaning)", "домовитися про ЗНАЧЕННЯ — status==3", True),
        ("За позицією (position)", "домовитися про ПОРЯДОК аргументів", True),
        ("За алгоритмом (algorithm)", "домовитися про однаковий АЛГОРИТМ", True),
        ("За виконанням (execution)", "важливий ПОРЯДОК виконання", False),
        ("За часом (timing)", "важливий ЧАС / одночасність", False),
        ("За значенням (value)", "значення мусять лишатися УЗГОДЖЕНИМИ", False),
        ("За ідентичністю (identity)", "той САМИЙ об'єкт (не рівний)", False),
    ]

    stat_col = "#f2faf5"   # статичні — спокійна зелена заливка
    dyn_col = "#fdecea"    # динамічні — гаряча заливка
    n = len(rungs)
    # y-координата верхнього краю щабля i (i=0 внизу)
    def yy(i):
        return bottom - box_h - i * (box_h + gap)

    # межа "лише під час виконання" між статичними (0..4) і динамічними (5..8)
    border_y = (yy(4) + yy(5) + box_h) / 2
    frags.append(line(left - 24, border_y, left + box_w + 20, border_y,
                      color=POS, sw=2.0, dash="7,5"))
    frags.append(text(left + box_w / 2, border_y - 8,
                      "нижче — видно з тексту коду · вище — лише під час виконання",
                      size=11, bold=True, color=POS))

    for i, (nm, desc, static) in enumerate(rungs):
        y = yy(i)
        fill = stat_col if static else dyn_col
        stroke = FIELD if static else POS
        frags.append(rect(left, y, box_w, box_h, fill=fill, stroke=stroke, sw=1.6, rx=7))
        frags.append(text(left + 16, y + 22, nm, size=13, bold=True, color=INK, anchor="start"))
        frags.append(text(left + 16, y + 40, desc, size=11, color=MUTED, anchor="start"))

    # ліва велика стрілка "сильніше вгору"
    frags.append(arrow(left - 46, bottom - 6, left - 46, yy(n - 1) + 6, color=INK, sw=2.6))
    frags.append(text(left - 74, (bottom + yy(n - 1)) / 2, "сильніше",
                      size=13, bold=True, color=INK, anchor="middle"))
    frags.append(text(left - 74, (bottom + yy(n - 1)) / 2 + 18, "тісніше",
                      size=11, color=MUTED, anchor="middle"))

    # підписи полюсів
    frags.append(text(left + box_w / 2, bottom + 34,
                      "найслабше — розірвати легко (перейменувати)",
                      size=12, color=FIELD, bold=True))
    frags.append(text(left + box_w / 2, yy(n - 1) - 14,
                      "найтісніше — розірвати найважче",
                      size=12, color=POS, bold=True))

    render(os.path.join(IMG, 'connascence-ladder.svg'), W, H, *frags,
           title="Драбина зчеплюваності: від найслабшої до найтіснішої")


if __name__ == "__main__":
    fig_two_ladders()
    fig_connascence_ladder()
    print("figures written to", IMG)
