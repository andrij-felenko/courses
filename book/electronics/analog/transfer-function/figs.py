# -*- coding: utf-8 -*-
"""Фігури до базової статті «Передавальна функція» (transfer-function).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

WIRE = "#cf8b5e"   # тепла мідь для сигнальних ліній


# ── 1. Чорна скриня: вхід × H = вихід ────────────────────────────────────────
def fig_blackbox():
    W, H = 820, 360
    f = [text(W / 2, 30, "Передавальна функція — один множник між входом і виходом", size=17, bold=True),
         text(W / 2, 52, "що коло робить із синусоїдою частоти ω: множить амплітуду й повертає фазу",
              size=12, color=MUTED, italic=True)]

    cy = 190
    # вхідна стрілка-фазор
    inx = 150
    f.append(text(inx, cy - 70, "вхід X(ω)", size=13, bold=True, color=NEG))
    f.append(line(inx, cy, inx + 55, cy - 38, color=NEG, sw=3))   # коротка похила стрілка
    f.append(circle(inx, cy, 4, fill=NEG, stroke=NEG))
    f.append(text(inx, cy + 30, "амплітуда A\nфаза 0", size=11, color=MUTED))
    # вхідна сигнальна лінія в скриню
    box_x, box_w = 290, 240
    f.append(line(inx + 60, cy, box_x, cy, color=WIRE, sw=2.6))

    # сама скриня (зелене поле — «коло»)
    f.append(rect(box_x, cy - 55, box_w, 110, fill="#eaf6ee", stroke=FIELD, sw=2.2))
    f.append(text(box_x + box_w / 2, cy - 16, "H(ω)", size=26, bold=True, color=INK))
    f.append(text(box_x + box_w / 2, cy + 14, "лінійне коло", size=12, color=INK, bold=True))
    f.append(text(box_x + box_w / 2, cy + 34, "(фільтр, підсилювач, кабель…)", size=11, color=MUTED))

    # вихідна лінія
    outx = box_x + box_w + 70
    f.append(line(box_x + box_w, cy, outx, cy, color=WIRE, sw=2.6))
    # вихідна стрілка-фазор: довша й повернута (×|H|, −φ)
    f.append(text(outx + 35, cy - 70, "вихід Y = H·X", size=13, bold=True, color=POS))
    f.append(line(outx, cy, outx + 78, cy - 18, color=POS, sw=3))  # довша, менш задерта
    f.append(circle(outx, cy, 4, fill=POS, stroke=POS))
    f.append(text(outx + 30, cy + 30, "× |H| (розтяг)\n− φ (поворот)", size=11, color=MUTED))

    # підпис-формула знизу
    f.append(text(W / 2, 325, "Y(ω) = H(ω) · X(ω)   —   множення комплексних чисел: |Y|=|H|·|X|,  кут Y = кут X + кут H",
                  size=12.5, bold=True))
    render(os.path.join(IMG, "blackbox.svg"), W, H, *f)


# ── 2. Чому функція існує: важка згортка в часі → легке множення в s/jω ───────
def fig_trick():
    W, H = 820, 380
    f = [text(W / 2, 30, "Навіщо H: важку дію в часі замінюємо множенням", size=17, bold=True),
         text(W / 2, 52, "диференціювати й згортати важко — множити дроби легко",
              size=12, color=MUTED, italic=True)]

    # ліва панель — час
    lx, lw = 60, 320
    f.append(rect(lx, 90, lw, 220, fill=BG, stroke=LINE, sw=1.6))
    f.append(text(lx + lw / 2, 116, "у часі t", size=14, bold=True))
    f.append(text(lx + lw / 2, 140, "коло описане диференціальним рівнянням", size=11.5, color=MUTED))
    f.append(text(lx + lw / 2, 178, "i = C · dv/dt,   v = L · di/dt", size=13, bold=True, color=INK))
    f.append(text(lx + lw / 2, 214, "вихід = вхід ⊛ h(t)", size=13, bold=True, color=POS))
    f.append(text(lx + lw / 2, 236, "(згортка — інтеграл добутків)", size=11, color=MUTED))
    f.append(text(lx + lw / 2, 286, "розв'язувати ВАЖКО", size=12.5, bold=True, color=POS))

    # стрілка-міст: підстановка d/dt → jω (або s)
    ax = lx + lw + 18
    f.append(arrow(ax, 200, ax + 64, 200, color=FIELD, sw=2.6))
    f.append(text(ax + 32, 184, "d/dt → jω", size=12, bold=True, color=FIELD))
    f.append(text(ax + 32, 230, "(одна\nпідстановка)", size=10.5, color=MUTED))

    # права панель — частота
    rx = ax + 80
    rw = W - rx - 40
    f.append(rect(rx, 90, rw, 220, fill="#eaf6ee", stroke=FIELD, sw=1.8))
    f.append(text(rx + rw / 2, 116, "на частоті ω", size=14, bold=True))
    f.append(text(rx + rw / 2, 140, "коло описане алгебраїчним дробом", size=11.5, color=MUTED))
    f.append(text(rx + rw / 2, 178, "Z_C = 1/(jωC),   Z_L = jωL", size=12.5, bold=True, color=INK))
    f.append(text(rx + rw / 2, 214, "Y = H(jω) · X", size=14, bold=True, color=FIELD))
    f.append(text(rx + rw / 2, 236, "(просте множення)", size=11, color=MUTED))
    f.append(text(rx + rw / 2, 286, "розв'язувати ЛЕГКО", size=12.5, bold=True, color=FIELD))

    f.append(text(W / 2, 350, "H(jω) — це і є коло, переписане мовою, де похідна стала множником jω",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "trick.svg"), W, H, *f)


# ── 3. Каскад: дроби перемножуються, децибели додаються ──────────────────────
def fig_cascade():
    W, H = 820, 330
    f = [text(W / 2, 30, "Каскад: передавальні функції перемножуються", size=17, bold=True),
         text(W / 2, 52, "увесь тракт — один дріб H = H₁·H₂·H₃ (за умови, що каскади не вантажать один одного)",
              size=12, color=MUTED, italic=True)]

    cy = 165
    blocks = [("H₁", "розділовий\nконденсатор", "+20 дБ/дек\nунизу"),
              ("H₂", "підсилювач\n×100", "+40 дБ"),
              ("H₃", "RC на\nвиході", "−20 дБ/дек\nуверху")]
    bw, gap = 165, 35
    x0 = (W - (3 * bw + 2 * gap)) / 2
    # вхідна лінія
    f.append(line(x0 - 50, cy, x0, cy, color=WIRE, sw=2.6))
    f.append(text(x0 - 50, cy - 14, "вхід", size=12, bold=True, color=NEG, anchor="start"))
    for i, (h, what, eff) in enumerate(blocks):
        bx = x0 + i * (bw + gap)
        f.append(rect(bx, cy - 45, bw, 90, fill="#eaf6ee", stroke=FIELD, sw=2))
        f.append(text(bx + bw / 2, cy - 18, h, size=22, bold=True, color=INK))
        f.append(mtext(bx + bw / 2, cy + 6, what.split("\n"), size=11.5, color=INK, bold=True, lh=1.25))
        f.append(mtext(bx + bw / 2, cy + 60, eff.split("\n"), size=10.5, color=MUTED, lh=1.2))
        if i < 2:
            f.append(line(bx + bw, cy, bx + bw + gap, cy, color=WIRE, sw=2.6))
    # вихідна лінія
    lastx = x0 + 3 * bw + 2 * gap
    f.append(line(lastx, cy, lastx + 50, cy, color=WIRE, sw=2.6))
    f.append(text(lastx + 50, cy - 14, "вихід", size=12, bold=True, color=POS, anchor="end"))

    f.append(text(W / 2, 280, "H = H₁ · H₂ · H₃    ⟹    у децибелах:  G = G₁ + G₂ + G₃",
                  size=13.5, bold=True))
    f.append(text(W / 2, 304, "тому характеристики каскадів на діаграмі Боде просто додаються лінійкою",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "cascade.svg"), W, H, *f)


if __name__ == "__main__":
    fig_blackbox()
    fig_trick()
    fig_cascade()
    print("OK: 3 SVG -> img/")
