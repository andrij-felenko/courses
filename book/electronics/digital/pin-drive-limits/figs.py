# -*- coding: utf-8 -*-
"""Фігури до математичної вставки теми «Навантажувальна здатність і захист ніжки».
Покриває дві фігури, на які посилається math-pin-budget.md:
  two-budgets.svg  — дві межі заразом: кожна ніжка ≤ ~20 мА і сума всіх ≤ межа чипа
  led-color.svg    — резистор світлодіода за кольором (червоний/зелений/синій)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Увага: інші 6 SVG у ./img/ належать СТАТТІ теми (pin-drive-limits.md) і
згенеровані окремо; цей файл їх не чіпає."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: two-budgets.svg ───────────────────────────────────────────────
# Дві межі заразом: ліворуч «розетки» (кожна ніжка ≤ ~20 мА),
# праворуч «головний автомат» (сума всіх ніжок ≤ межа живлення чипа).
def fig_two_budgets():
    W, H = 860, 360
    f = [text(W / 2, 30, "Два бюджети струму: окрема ніжка й увесь чип", size=17, bold=True)]
    f.append(text(W / 2, 52, "як розетка й головний автомат — тримати треба обидві межі заразом",
                  size=12, color=MUTED, italic=True))

    # ── ліва панель: бюджет ніжки («розетки») ──
    Lx, Ly, Lw, Lh = 30, 74, 400, 210
    f.append(rect(Lx, Ly, Lw, Lh, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=10))
    f.append(text(Lx + Lw / 2, Ly + 24, "бюджет ніжки («розетка»)", size=13, color=NEG, bold=True))

    bar_x, bar_w = Lx + 150, 190          # шкала струму однієї ніжки
    safe_w = bar_w * 20.0 / 40.0          # ~20 мА із стелі 40 мА
    for i in range(4):
        y = Ly + 52 + i * 34
        f.append(text(Lx + 24, y + 4, "ніжка %d" % i, size=11, color=INK, anchor="start"))
        f.append(rect(bar_x, y - 9, bar_w, 18, fill="#ffffff", stroke=NEG, sw=1.2, rx=3))
        f.append(rect(bar_x, y - 9, safe_w, 18, fill="#cdddff", stroke=NEG, sw=0, rx=3))
        f.append(text(bar_x + bar_w + 6, y + 4, "≤ ~20 мА", size=10, color=NEG, bold=True, anchor="start"))
    f.append(text(Lx + Lw / 2, Ly + Lh - 14, "кожна окремо — не більш як ~20 мА (стеля 40)",
                  size=10, color=MUTED))

    # ── права панель: бюджет чипа («автомат») ──
    Rx, Ry, Rw, Rh = 460, 74, 370, 210
    f.append(rect(Rx, Ry, Rw, Rh, fill="#fff6e0", stroke="#b5732e", sw=1.6, rx=10))
    f.append(text(Rx + Rw / 2, Ry + 24, "бюджет чипа («автомат»)", size=13, color="#8a5a1d", bold=True))
    f.append(text(Rx + Rw / 2, Ry + 64, "Σ усіх ніжок", size=15, color=INK, bold=True))
    f.append(text(Rx + Rw / 2, Ry + 92, "≤ межа живлення чипа", size=12, color="#8a5a1d", bold=True))
    f.append(fitbox(Rx + 26, Ry + 116, Rw - 52, 38,
                    "8 світлодіодів × 10 мА = 80 мА\nчерез спільні VDD / GND",
                    size=11, fill="#ffffff", stroke="#e6d2b0", color=INK))
    f.append(text(Rx + Rw / 2, Ry + Rh - 14, "забагато → притишити струм або взяти драйвер",
                  size=10, color=POS, bold=True))

    f.append(text(W / 2, H - 16,
                  "Мало, щоб кожна ніжка була в межах — їхня СУМА теж мусить уміститися.",
                  size=11, color=INK, bold=True))
    render(os.path.join(IMG, "two-budgets.svg"), W, H, *f)


# ── Фігура 2: led-color.svg ─────────────────────────────────────────────────
# Резистор світлодіода за кольором: однаковий струм 10 мА на 3.3 В,
# але різний Vf → різний запас. Синій/білий на 3.3 В тісні.
def fig_led_color():
    W, H = 860, 380
    f = [text(W / 2, 30, "Резистор світлодіода за кольором: R = (V_ніжки − V_LED) / I", size=16, bold=True)]
    f.append(text(W / 2, 52, "однаковий струм 10 мА на 3.3 В — та різний V_LED дає різний запас",
                  size=12, color=MUTED, italic=True))

    # ── шапка таблиці ──
    cols = [(150, "колір"), (360, "V_LED (Vf)"), (580, "R для 10 мА на 3.3 В"), (770, "запас")]
    head_y = 80
    f.append(rect(70, head_y - 18, 730, 28, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=6))
    for cx, lab in cols:
        f.append(text(cx, head_y + 1, lab, size=11, color=NEG, bold=True))

    # ── рядки таблиці ──
    rows = [
        ("червоний",        "2.0 В", "130 Ом", "добрий", FIELD),
        ("зелений / жовтий", "2.1 В", "120 Ом", "добрий", FIELD),
        ("синій / білий",    "3.0 В",  "30 Ом", "МАЛИЙ",  POS),
    ]
    for i, (name, vf, r, mark, mc) in enumerate(rows):
        y = head_y + 36 + i * 34
        if i % 2 == 0:
            f.append(rect(70, y - 17, 730, 30, fill="#f7f9fc", stroke="#e2e8f0", sw=1.0, rx=4))
        f.append(text(cols[0][0], y + 2, name, size=11, color=INK))
        f.append(text(cols[1][0], y + 2, vf, size=11, color=INK))
        f.append(text(cols[2][0], y + 2, r, size=11, color=INK))
        f.append(text(cols[3][0], y + 2, mark, size=11, color=mc, bold=True))

    # ── висновок-рамка ──
    by = head_y + 36 + 3 * 34 + 8
    f.append(fitbox(110, by, 640, 84,
                    "Синій / білий мають V_LED близьке до 3.3 В — на резистор лишається крихта.\n"
                    "Тоді струм дуже чутливий до розкиду Vf: трохи більший Vf — LED ледь жевріє,\n"
                    "трохи менший — перевантаження. На 3.3 В сині/білі капризні, комфортніше від 5 В.",
                    size=11, fill="#fbecec", stroke=POS, color=INK))
    render(os.path.join(IMG, "led-color.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_budgets()
    fig_led_color()
    print("OK: two-budgets, led-color -> img/")
