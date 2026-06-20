# -*- coding: utf-8 -*-
"""Фігури до теми «NTC-термістор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

WARM = "#e08a3c"   # «тепло» — додатковий теплий відтінок


# ── 1. ЧОМУ опір падає: у напівпровіднику тепло вивільняє носії ──────────────
def fig_why_falls():
    W, H = 720, 360
    f = [text(W / 2, 26, "Чому опір NTC падає з нагрівом: тепло вивільняє носії заряду", size=16, bold=True)]

    def panel(x0, title, temp_lab, n_carriers, fill, note):
        f.append(rect(x0, 60, 280, 210, fill=fill, stroke=MUTED, sw=1.4, rx=8))
        f.append(text(x0 + 140, 84, title, size=13.5, bold=True, color=INK))
        f.append(text(x0 + 140, 104, temp_lab, size=12, color=MUTED))
        # ґратка атомів
        for r in range(3):
            for c in range(5):
                cx = x0 + 40 + c * 50
                cy = 135 + r * 38
                f.append(circle(cx, cy, 7, fill="#cfd8e2", stroke=MUTED, sw=1.1))
        # вільні носії — рухливі «−» (більше при нагріві)
        import random
        random.seed(1 if n_carriers < 6 else 2)
        for _ in range(n_carriers):
            cx = x0 + 34 + random.randint(0, 210)
            cy = 122 + random.randint(0, 96)
            f.append(minus(cx, cy, 7))
        b, _, _ = textbox(x0 + 140, 252, note, size=11, fill=BG, stroke=MUTED)
        f.append(b)

    panel(20, "Холодний", "низька t°  →  мало вільних носіїв", 3, "#eef2f8",
          "носіїв обмаль → струму\nтяжко → ОПІР ВЕЛИКИЙ")
    f.append(text(W / 2, 175, "нагрів", size=12, bold=True, color=WARM))
    f.append(arrow(W / 2 - 26, 190, W / 2 + 26, 190, color=WARM, sw=2.4))
    panel(420, "Гарячий", "висока t°  →  багато вільних носіїв", 11, "#fbeee6",
          "носіїв удосталь → струм\nіде легко → ОПІР МАЛИЙ")
    render(os.path.join(IMG, "why-resistance-falls.svg"), W, H, *f)


# ── 2. Крута експонента R(T) та що таке B-параметр ──────────────────────────
def fig_rt_curve():
    W, H = 720, 410
    f = [text(W / 2, 26, "Опір NTC падає круто й нелінійно — це експонента, не пряма", size=16, bold=True)]

    ox, oy = 86, 330           # початок координат
    ax_w, ax_h = 560, 250
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 42, "температура,  °C", size=12, color=INK))
    f.append(mtext(ox - 58, oy - ax_h / 2 - 6, ["опір", "(кОм)"], size=11.5, color=INK))

    # модель B-параметра, нормована на 10 кОм при 25 °C
    R25, B, T25 = 10000.0, 3950.0, 298.15
    def R_of(Tc):
        Tk = Tc + 273.15
        return R25 * math.exp(B * (1.0 / Tk - 1.0 / T25))

    temps = list(range(-20, 121, 2))
    Rs = [R_of(t) / 1000.0 for t in temps]      # кОм
    Rmax = max(Rs)
    def X(t):  return ox + (t - temps[0]) / (temps[-1] - temps[0]) * ax_w
    def Y(rk): return oy - rk / Rmax * (ax_h - 16)

    # позначки осей
    for t in (-20, 0, 25, 50, 75, 100, 120):
        f.append(line(X(t), oy, X(t), oy + 5, color=INK, sw=1.3))
        f.append(text(X(t), oy + 20, str(t), size=10.5, color=MUTED))
    for rk in (0, 20, 40, 60, 80):
        if rk <= Rmax:
            f.append(line(ox - 5, Y(rk), ox, Y(rk), color=INK, sw=1.3))
            f.append(text(ox - 16, Y(rk) + 4, str(rk), size=10.5, color=MUTED, anchor="end"))

    pts = " ".join("%.1f,%.1f" % (X(t), Y(r)) for t, r in zip(temps, Rs))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (pts, POS))

    # опорна точка 25 °C / 10 кОм
    f.append(line(X(25), oy, X(25), Y(10), color=MUTED, sw=1.1, dash="4,4"))
    f.append(line(ox, Y(10), X(25), Y(10), color=MUTED, sw=1.1, dash="4,4"))
    f.append(circle(X(25), Y(10), 4.5, fill=BG, stroke=POS, sw=2))
    b, _, _ = textbox(X(25) + 96, Y(10) - 6, "R₂₅ = 10 кОм\n(опорна точка)", size=11,
                      fill="#fdecea", stroke=POS)
    f.append(b)

    # підпис «крутість = B»
    b2, _, _ = textbox(ox + ax_w - 150, oy - ax_h + 36,
                       "крутість кривої\nзадає B-параметр\n(тут B ≈ 3950 K)",
                       size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b2)
    render(os.path.join(IMG, "rt-curve.svg"), W, H, *f)


# ── 3. Зчитування: дільник + АЦП ────────────────────────────────────────────
def fig_divider_adc():
    W, H = 720, 360
    f = [text(W / 2, 26, "Зчитування NTC: дільник перетворює опір у напругу для АЦП", size=16, bold=True)]

    # шина 3.3 В угорі, земля внизу
    topy, boty = 70, 300
    railx0, railx1 = 150, 430
    f.append(line(railx0, topy, railx1, topy, color=POS, sw=2.2))
    f.append(text(railx0 - 14, topy + 4, "3.3 В", size=12, bold=True, color=POS, anchor="end"))
    f.append(line(railx0, boty, railx1, boty, color=INK, sw=2.2))
    f.append(text(railx0 - 14, boty + 4, "GND", size=12, bold=True, color=INK, anchor="end"))

    midx = 290
    midy = (topy + boty) / 2
    # верхній резистор — опорний R
    f.append(rect(midx - 22, topy + 24, 44, 70, fill="#eef2f8", stroke=NEG, sw=1.8))
    f.append(text(midx, topy + 64, "R", size=15, bold=True, color=NEG))
    f.append(text(midx + 58, topy + 64, "опорний\n(сталий)", size=10.5, color=MUTED, anchor="middle"))
    f.append(mtext(midx + 58, topy + 56, ["опорний", "(сталий)"], size=10.5, color=MUTED))
    f.append(line(midx, topy, midx, topy + 24, color=INK, sw=1.6))
    # нижній — NTC
    f.append(rect(midx - 22, boty - 94, 44, 70, fill="#fbeee6", stroke=POS, sw=1.8))
    f.append(text(midx, boty - 54, "NTC", size=13, bold=True, color=POS))
    f.append(line(midx - 16, boty - 100, midx + 18, boty - 18, color=POS, sw=1.4))   # стрілка «змінний»
    f.append(arrow(midx + 8, boty - 30, midx + 20, boty - 14, color=POS, sw=1.4))
    f.append(line(midx, boty - 24, midx, boty, color=INK, sw=1.6))
    # середня точка → АЦП
    f.append(line(midx, midy, midx + 90, midy, color=INK, sw=1.6))
    f.append(circle(midx, midy, 4, fill=INK, stroke=INK, sw=1))
    f.append(rect(midx + 90, midy - 32, 96, 64, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
    f.append(mtext(midx + 138, midy - 4, ["АЦП", "→ число"], size=12.5, bold=True, color=INK))
    b, _, _ = textbox(midx + 50, midy - 44, "U_сер", size=11.5, fill=BG, stroke=MUTED, bold=True)
    f.append(b)

    # формула праворуч
    b2, _, _ = textbox(605, midy + 36,
                       "U_сер = 3.3 · NTC\n     ──────────\n      R + NTC",
                       size=11.5, fill=FILL, stroke=LINE)
    f.append(b2)
    f.append(text(W / 2, H - 16,
                  "опір падає → напруга на середній точці змінюється → АЦП читає число → рахуємо t°",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(IMG, "divider-adc.svg"), W, H, *f)


# ── 4. Самонагрів: струм гріє давач, давач бреше ────────────────────────────
def fig_self_heating():
    W, H = 720, 330
    f = [text(W / 2, 26, "Самонагрів: вимірювальний струм сам гріє NTC — і той бреше", size=16, bold=True)]

    cx, cy = 200, 175
    # NTC у центрі
    f.append(circle(cx, cy, 52, fill="#fbeee6", stroke=POS, sw=2))
    f.append(text(cx, cy + 6, "NTC", size=16, bold=True, color=POS))
    # струм входить
    f.append(arrow(cx - 130, cy, cx - 56, cy, color=NEG, sw=2.4))
    f.append(text(cx - 92, cy - 12, "струм I", size=12, bold=True, color=NEG))
    # тепло виходить (P = I²R)
    for ang in (-50, -20, 20, 50):
        a = math.radians(ang)
        x1 = cx + 56 * math.cos(a); y1 = cy + 56 * math.sin(a)
        x2 = cx + 96 * math.cos(a); y2 = cy + 96 * math.sin(a)
        f.append(arrow(x1, y1, x2, y2, color=WARM, sw=2))
    f.append(text(cx + 120, cy - 6, "тепло", size=12, bold=True, color=WARM))
    f.append(text(cx + 120, cy + 12, "P = I²·R", size=11.5, color=MUTED))

    # ланцюг причинності праворуч
    steps = [
        ("струм крізь NTC", NEG, "#eef2f8"),
        ("виділяє P = I²·R", WARM, "#fbeee6"),
        ("давач нагрівається", POS, "#fdecea"),
        ("показ ЗАВИЩЕНИЙ", POS, "#fdecea"),
    ]
    bx, by = 470, 70
    for i, (lab, col, fl) in enumerate(steps):
        y = by + i * 58
        b, _, _ = textbox(bx + 120, y, lab, size=12, fill=fl, stroke=col, bold=(i == 3))
        f.append(b)
        if i < len(steps) - 1:
            f.append(arrow(bx + 120, y + 16, bx + 120, y + 40, color=MUTED, sw=1.8))
    render(os.path.join(IMG, "self-heating.svg"), W, H, *f)


# ── 5. Дві ролі: точний вимір температури vs захист (обмеження кидка) ────────
def fig_where_works():
    W, H = 720, 350
    f = [text(W / 2, 26, "Той самий NTC — у двох ролях за різними його властивостями", size=16, bold=True)]

    # ── ліворуч: ВИМІР температури (мала потужність) ──
    x0 = 30
    f.append(rect(x0, 56, 320, 256, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(x0 + 160, 82, "Вимір температури", size=14, bold=True, color=INK))
    f.append(text(x0 + 160, 102, "беремо круту R(T), струм — крихітний", size=10.5, color=MUTED))
    f.append(mtext(x0 + 160, 140,
                   ["• висока чутливість біля кімнатної t°",
                    "• дешево, малий, швидкий",
                    "• самонагрів тримаємо мізерним",
                    "• вузький точний діапазон"],
                   size=11.5, color=INK, anchor="middle", lh=1.45))
    b, _, _ = textbox(x0 + 160, 282, "термостати · батареї · ЦП · погода",
                      size=11, fill=BG, stroke=FIELD)
    f.append(b)

    # ── праворуч: ЗАХИСТ (велика потужність, самонагрів — корисний) ──
    x1 = 370
    f.append(rect(x1, 56, 320, 256, fill="#fbeee6", stroke=POS, sw=1.8, rx=10))
    f.append(text(x1 + 160, 82, "Захист від кидка струму", size=14, bold=True, color=INK))
    f.append(text(x1 + 160, 102, "тут самонагрів — навмисний інструмент", size=10.5, color=MUTED))
    f.append(mtext(x1 + 160, 140,
                   ["• холодний при ввімкненні — опір ВЕЛИКИЙ",
                    "• обмежує кидок зарядки ємностей",
                    "• струм гріє його → опір ПАДАЄ",
                    "• далі майже не заважає"],
                   size=11.5, color=INK, anchor="middle", lh=1.45))
    b2, _, _ = textbox(x1 + 160, 282, "входи БЖ · підсвітка · двигуни",
                       size=11, fill=BG, stroke=POS)
    f.append(b2)
    render(os.path.join(IMG, "where-works.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_falls()
    fig_rt_curve()
    fig_divider_adc()
    fig_self_heating()
    fig_where_works()
    print("OK: 5 figures ->", IMG)
