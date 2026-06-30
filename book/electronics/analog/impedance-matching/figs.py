# -*- coding: utf-8 -*-
"""Фігури до статті «Узгодження опорів» (book/electronics/analog/impedance-matching).
Фігури:
  three-goals.svg — головна думка: один стик, три різні мети → три різні правила
  reflection.svg  — мета 2: неузгоджений кінець лінії дає відлуння, узгоджений — ні
  bridging.svg    — мета 3: низький вихід у високий вхід → майже вся напруга доходить
  power-vs-eff.svg — вставка hist: помилка Джоуля — максимум потужності ≠ максимум ККД
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ────────────────────────────────────────────────────────
def src_box(x, y, w, h, lab, sub):
    """Прямокутник-джерело з вихідним опором."""
    out = [rect(x, y, w, h, fill="#fdecea", stroke=POS, sw=2, rx=8),
           text(x + w / 2, y + h / 2 - 4, lab, size=13, color=POS, bold=True),
           text(x + w / 2, y + h / 2 + 14, sub, size=11, color=MUTED)]
    return "".join(out)


def load_box(x, y, w, h, lab, sub, col):
    out = [rect(x, y, w, h, fill="#eef7f0", stroke=col, sw=2, rx=8),
           text(x + w / 2, y + h / 2 - 4, lab, size=13, color=col, bold=True),
           text(x + w / 2, y + h / 2 + 14, sub, size=11, color=MUTED)]
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 1. three-goals.svg — три мети, три правила для одного стику
# ════════════════════════════════════════════════════════════════════════════
def fig_three_goals():
    W, H = 720, 470
    f = []
    f.append(text(W / 2, 34, "Один стик джерело → навантаження, три різні мети", size=16, bold=True))

    rows = [
        # (y-центр ряду, мета, правило+формула, колір, підпис-навантаження)
        (110, "максимум потужності", "опори РІВНІ:  R_н = R_дж", POS, "R_н = R_дж"),
        (230, "немає відлуння в лінії", "опір = опору лінії:  R_н = Z₀", NEG, "R_н = Z₀"),
        (350, "ціла напруга сигналу", "вхід ≫ виходу:  R_н ≫ R_дж", FIELD, "R_н ≫ R_дж"),
    ]

    sx, sw, sh = 60, 92, 52
    lx, lw = 470, 150          # навантаження тягнеться до 620 — у межах 720
    for cy, goal, rule, col, lsub in rows:
        y = cy - sh / 2
        # мета — над стиком, по центру прольоту
        f.append(text((sx + sw + lx) / 2, y - 14, goal, size=13, color=col, bold=True))
        # джерело
        f.append(src_box(sx, y, sw, sh, "джерело", "R_дж"))
        # провід зі стрілкою сигналу
        f.append(arrow(sx + sw, cy, lx - 4, cy, color=col, sw=2.6))
        # правило+формула — під стрілкою
        f.append(text((sx + sw + lx) / 2, cy + 22, rule, size=11, color=MUTED))
        # навантаження
        f.append(load_box(lx, y, lw, sh, "навантаження", lsub, col))

    # підпис-висновок унизу
    body, w0, h0 = textbox(W / 2, 440,
                           "«Узгодити» не означає «зрівняти» — означає припасувати співвідношення опорів під мету",
                           size=12, color=INK, fill=FILL, stroke=MUTED)
    f.append(body)
    render(os.path.join(IMG, "three-goals.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. reflection.svg — відлуння на неузгодженому кінці vs тиша на узгодженому
# ════════════════════════════════════════════════════════════════════════════
def fig_reflection():
    W, H = 720, 420
    f = []
    f.append(text(W / 2, 32, "Кінець лінії: узгоджений поглинає, неузгоджений відбиває", size=15, bold=True))

    x0, x1 = 90, 560

    # ── Верх: неузгоджено ──
    yA = 130
    f.append(text(x0 - 6, yA - 54, "R_н ≠ Z₀  —  частина хвилі вертається відлунням", size=12, color=POS, bold=True, anchor="start"))
    # лінія (дві паралельні риски — провід-лінія)
    f.append(line(x0, yA, x1, yA, color=INK, sw=2.2))
    # пряма хвиля →
    f.append(arrow(x0 + 30, yA - 14, x0 + 150, yA - 14, color=NEG, sw=2.4))
    f.append(text(x0 + 90, yA - 22, "пряма", size=11, color=NEG, anchor="middle"))
    # відбита хвиля ← (від кінця назад)
    f.append(arrow(x1 - 30, yA + 18, x1 - 150, yA + 18, color=POS, sw=2.4))
    f.append(text(x1 - 90, yA + 32, "відбита (луна)", size=11, color=POS, anchor="middle"))
    # навантаження-обрив (≠Z0)
    f.append(rect(x1, yA - 26, 70, 52, fill="#fdecea", stroke=POS, sw=2, rx=6))
    f.append(text(x1 + 35, yA - 4, "R_н", size=12, color=POS, bold=True))
    f.append(text(x1 + 35, yA + 14, "≠ Z₀", size=11, color=MUTED))
    # «дзвінкий» фронт праворуч від мети
    f.append(text(x0 + 235, yA - 14, "Γ ≠ 0  →  фронт «дзвенить»", size=11, color=POS, anchor="middle"))

    # ── Низ: узгоджено ──
    yB = 290
    f.append(text(x0 - 6, yB - 54, "R_н = Z₀  —  хвиля повністю поглинається, відлуння немає", size=12, color=FIELD, bold=True, anchor="start"))
    f.append(line(x0, yB, x1, yB, color=INK, sw=2.2))
    f.append(arrow(x0 + 30, yB - 14, x0 + 200, yB - 14, color=NEG, sw=2.4))
    f.append(text(x0 + 115, yB - 22, "пряма", size=11, color=NEG, anchor="middle"))
    # лінія всередину навантаження «гасне»
    f.append(rect(x1, yB - 26, 70, 52, fill="#eef7f0", stroke=FIELD, sw=2, rx=6))
    f.append(text(x1 + 35, yB - 4, "R_н", size=12, color=FIELD, bold=True))
    f.append(text(x1 + 35, yB + 14, "= Z₀", size=11, color=MUTED))
    f.append(text(x0 + 300, yB + 22, "Γ = 0  →  лінія «прозора», VSWR = 1", size=11, color=FIELD, anchor="middle"))

    # формула коефіцієнта відбиття внизу
    body, w0, h0 = textbox(W / 2, 392,
                           "Γ = (R_н − Z₀) / (R_н + Z₀)   —   нуль рівно тоді, коли R_н = Z₀",
                           size=12, color=INK, fill="#eaf0fd", stroke=NEG)
    f.append(body)
    render(os.path.join(IMG, "reflection.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. bridging.svg — дільник: низький вихід у високий вхід → майже вся напруга
# ════════════════════════════════════════════════════════════════════════════
def fig_bridging():
    W, H = 660, 420
    f = []
    f.append(text(W / 2, 32, "Мостове під'єднання: вхід ≫ виходу → напруга доходить ціла", size=15, bold=True))

    # вертикальний дільник: джерело U зверху, R_дж послідовно, R_н на землю
    topx = 200
    top_y = 80
    midy = 200          # вузол між R_дж і R_н (тут «знімаємо» сигнал)
    boty = 330

    # шина джерела зверху
    f.append(text(topx, top_y - 16, "U джерела", size=12, color=INK, bold=True))
    f.append(circle(topx, top_y, 4, fill=INK, stroke=INK))

    # верхнє плече — вертикальний резистор R_дж
    f.append(_resistor_v(topx, top_y, midy, "R_дж (малий)", POS, side="left"))
    # вузол виходу
    f.append(circle(topx, midy, 4, fill=INK, stroke=INK))
    # відведення сигналу праворуч від вузла
    f.append(line(topx, midy, topx + 150, midy, color=FIELD, sw=2.4))
    f.append(arrow(topx + 150, midy, topx + 190, midy, color=FIELD, sw=2.4))
    f.append(text(topx + 205, midy + 4, "сигнал на вхід", size=12, color=FIELD, bold=True, anchor="start"))
    # нижнє плече — R_н (вхідний опір приймача), великий
    f.append(_resistor_v(topx, midy, boty, "R_н (великий)", FIELD, side="left"))
    # земля
    f.append(line(topx, boty, topx, boty + 8, color=INK, sw=1.8))
    f.append(line(topx - 14, boty + 8, topx + 14, boty + 8, color=INK, sw=2.4))
    f.append(line(topx - 9, boty + 13, topx + 9, boty + 13, color=INK, sw=2.0))
    f.append(line(topx - 4, boty + 18, topx + 4, boty + 18, color=INK, sw=1.8))

    # пояснення-стрілки праворуч
    body, w0, h0 = textbox(topx + 300, 150,
                           "R_н набагато\nбільший за R_дж →\nмайже вся напруга\nосідає на R_н",
                           size=12, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)

    # числовий рядок унизу
    body2, w2, h2 = textbox(W / 2, 392,
                            "10 кОм у 1 МОм:  частка = 1М/(10к+1М) = 0.99  →  доходить 99 %   (а рівні опори дали б лише 50 %)",
                            size=11, color=INK, fill=FILL, stroke=MUTED)
    f.append(body2)
    render(os.path.join(IMG, "bridging.svg"), W, H, *f)


def _resistor_v(x, y0, y1, label, col, side="left"):
    """Вертикальний резистор-зигзаг між (x,y0) та (x,y1)."""
    out = []
    n = 6
    seg = (y1 - y0) / (n + 2)
    amp = 7
    out.append(line(x, y0, x, y0 + seg, color=col, sw=1.8))
    yy = y0 + seg
    for i in range(n):
        nx = x + (amp if i % 2 == 0 else -amp)
        out.append(line(x if i == 0 else (x - amp if i % 2 == 1 else x + amp),
                        yy, nx, yy + seg, color=col, sw=1.8))
        yy += seg
    out.append(line(x + (amp if (n - 1) % 2 == 0 else -amp), yy, x, yy + seg, color=col, sw=1.8))
    out.append(line(x, yy + seg, x, y1, color=col, sw=1.8))
    lx = x - 18 if side == "left" else x + 18
    an = "end" if side == "left" else "start"
    out.append(text(lx, (y0 + y1) / 2 + 4, label, size=12, color=col, bold=True, anchor=an))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 4. power-vs-eff.svg — вставка hist: дві криві на одній осі.
#    Потужність у навантаженні має ГОРБ при R_н = R_дж (там ККД лише 50%).
#    ККД росте монотонно до 100% у міру того, як R_н ≫ R_дж.
#    Це й є пастка, у яку впав Джоуль: максимум потужності ≠ максимум ефективності.
# ════════════════════════════════════════════════════════════════════════════
def fig_power_vs_eff():
    import math
    W, H = 720, 470
    f = []
    f.append(text(W / 2, 32, "Чому Джоуль помилився: потужність і ККД — дві різні криві", size=16, bold=True))

    # осі графіка
    ox, oy = 95, 380          # початок координат (лівий низ)
    ax_w, ax_h = 520, 290     # довжина осей
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2.0))          # X
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2.0))          # Y
    f.append(text(ox + ax_w / 2, oy + 40, "опір навантаження R_н  (у частках R_дж)", size=12, color=INK))
    f.append(text(ox + ax_w, oy + 20, "R_н / R_дж →", size=11, color=MUTED, anchor="end"))

    # вісь X: відношення k = R_н/R_дж від 0.05 до 8 (лог-подібний крок зручніший очам,
    # але лишимо лінійним 0..8 — горб біля 1 видно добре)
    kmin, kmax = 0.0, 8.0
    def X(k):
        return ox + (k - kmin) / (kmax - kmin) * ax_w
    def Y(frac):                  # frac 0..1 → висота
        return oy - frac * ax_h

    # сітка по X (позначки 1, 2, 4, 8 · R_дж)
    for k in (1, 2, 4, 8):
        f.append(line(X(k), oy, X(k), oy - 4, color=INK, sw=1.4))
        f.append(text(X(k), oy + 16, ("R_дж" if k == 1 else "%d·R_дж" % k), size=10, color=MUTED))
    # горизонтальні пунктири 50% і 100%
    f.append(line(ox, Y(0.5), ox + ax_w, Y(0.5), color=MUTED, sw=1.0, dash="4 4"))
    f.append(text(ox - 8, Y(0.5) + 4, "50%", size=10, color=MUTED, anchor="end"))
    f.append(line(ox, Y(1.0), ox + ax_w, Y(1.0), color=MUTED, sw=1.0, dash="4 4"))
    f.append(text(ox - 8, Y(1.0) + 4, "100%", size=10, color=MUTED, anchor="end"))

    # ── крива потужності у навантаженні (нормована: максимум = 1 при k=1) ──
    # P_н(k) ∝ k/(1+k)²,  максимум при k=1 дає 1/4 → нормуємо ×4
    pts_p = []
    k = 0.02
    while k <= kmax:
        p = 4.0 * k / (1.0 + k) ** 2
        pts_p.append((X(k), Y(p)))
        k += 0.04
    f.append(_polyline(pts_p, POS, 2.8))
    # горб
    f.append(circle(X(1.0), Y(1.0), 4.5, fill=POS, stroke=POS))
    f.append(text(X(1.0), Y(1.0) - 12, "максимум потужності", size=11, color=POS, bold=True))
    f.append(text(X(1.0) + 6, Y(1.0) + 18, "тут R_н = R_дж", size=10, color=POS, anchor="start"))

    # ── крива ККД: η(k) = k/(1+k), росте монотонно до 1 ──
    pts_e = []
    k = 0.02
    while k <= kmax:
        e = k / (1.0 + k)
        pts_e.append((X(k), Y(e)))
        k += 0.04
    f.append(_polyline(pts_e, FIELD, 2.8))
    # точка ККД у момент максимуму потужності — рівно 50%
    f.append(circle(X(1.0), Y(0.5), 4.5, fill=FIELD, stroke=FIELD))
    f.append(text(X(1.0) + 10, Y(0.5) - 8, "ККД саме тут = 50%", size=10, color=FIELD, bold=True, anchor="start"))
    # куди тягне ефективність
    f.append(text(X(7.2), Y(0.90) - 8, "ККД → 100%", size=11, color=FIELD, bold=True, anchor="end"))
    f.append(text(X(7.2), Y(0.90) + 8, "(коли R_дж → 0)", size=10, color=MUTED, anchor="end"))

    # легенда — праворуч унизу, де обидві криві вже розійшлися й місця вдосталь
    lgx, lgy = ox + 232, oy - 96
    f.append(line(lgx, lgy, lgx + 30, lgy, color=POS, sw=3))
    f.append(text(lgx + 36, lgy + 4, "потужність у навантаженні (з горбом)", size=11, color=POS, anchor="start"))
    f.append(line(lgx, lgy + 22, lgx + 30, lgy + 22, color=FIELD, sw=3))
    f.append(text(lgx + 36, lgy + 26, "ККД — частка корисної потужності", size=11, color=FIELD, anchor="start"))

    # підпис-висновок унизу
    body, w0, h0 = textbox(W / 2, 442,
                           "Точка максимуму потужності й точка високого ККД — РІЗНІ. Сплутати їх — і є помилка Джоуля.",
                           size=12, color=INK, fill=FILL, stroke=MUTED)
    f.append(body)
    render(os.path.join(IMG, "power-vs-eff.svg"), W, H, *f)


def _polyline(pts, col, sw):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (d, col, sw))


if __name__ == "__main__":
    fig_three_goals()
    fig_reflection()
    fig_bridging()
    fig_power_vs_eff()
    print("OK: 4 фігури у", IMG)
