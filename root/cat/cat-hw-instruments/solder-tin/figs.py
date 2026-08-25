# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Припій / олово» (розхідник).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

METAL = "#9aa4ad"   # тіло припою (сірий метал)
METAL_D = "#6b7480"  # темніша грань металу
FLUX  = "#c8922e"   # каніфольна серцевина (бурштин)
SPOOL = "#3b4048"   # котушка


# ── 1. Розріз дроту: метал-трубка з каналами флюсу всередині ──────────────────
def fig_cross_section():
    W, H = 940, 500
    f = [text(W / 2, 30, "Розріз монтажного припою-дроту: флюс СХОВАНИЙ усередині металу",
              size=15.5, bold=True)]

    # --- ліворуч: суцільний дріт (без флюсу) для контрасту ---
    lx, ly = 210, 250
    f.append(rect(lx - 150, ly - 150, 300, 300, fill="#fafbfc", stroke=MUTED, sw=1.6, rx=12))
    f.append(text(lx, ly - 165, "суцільний (solid) — БЕЗ флюсу", size=12, bold=True, color=MUTED))
    f.append(circle(lx, ly, 92, fill=METAL, stroke=METAL_D, sw=3))
    # блік
    f.append('<path d="M %.1f %.1f A 92 92 0 0 1 %.1f %.1f" fill="none" stroke="#c3cad1" stroke-width="7" stroke-linecap="round"/>'
             % (lx - 55, ly - 62, lx + 30, ly - 84))
    f.append(text(lx, ly + 5, "суцільний метал", size=12, bold=True, color="#2b3138"))
    f.append(mtext(lx, ly + 118, ["флюс треба мазати ОКРЕМО", "(годиться для дроту, лудіння бака)"],
                   size=10.5, color=MUTED, lh=1.25))

    # --- праворуч: дріт із флюсовою серцевиною (в розрізі — канали) ---
    rx, ry = 690, 250
    f.append(rect(rx - 155, ry - 150, 310, 300, fill="#fffdf7", stroke=FLUX, sw=1.8, rx=12))
    f.append(text(rx, ry - 165, "з флюсовою серцевиною (flux-core)", size=12, bold=True, color="#8a6420"))
    f.append(circle(rx, ry, 92, fill=METAL, stroke=METAL_D, sw=3))
    f.append('<path d="M %.1f %.1f A 92 92 0 0 1 %.1f %.1f" fill="none" stroke="#c3cad1" stroke-width="7" stroke-linecap="round"/>'
             % (rx - 55, ry - 62, rx + 30, ry - 84))
    # кілька каналів флюсу (типова багатожильна серцевина)
    for ang in range(0, 360, 60):
        t = math.radians(ang)
        cxf = rx + 44 * math.cos(t)
        cyf = ry + 44 * math.sin(t)
        f.append(circle(cxf, cyf, 13, fill=FLUX, stroke="#a5761f", sw=1.4))
    f.append(circle(rx, ry, 14, fill=FLUX, stroke="#a5761f", sw=1.4))
    # виносна підпис-стрілка на канал (у вільне поле під колом)
    f.append(line(rx + 44, ry + 44 * math.sin(math.radians(60)), rx + 120, ry + 96, color="#a5761f", sw=1.6))
    f.append(mtext(rx + 122, ry + 100, ["канали", "флюсу"], size=10.5, bold=True, color="#8a6420", anchor="start"))
    f.append(text(rx, ry - 108, "метал", size=10.5, bold=True, color="#2b3138"))

    b, _, _ = textbox(W / 2, 470,
                      "Той самий сплав, але справа крізь пруток проходять тонкі канали каніфолі. Торкнув гарячий шов — "
                      "серцевина плавиться ПЕРШОЮ,\nзнімає окис, і слідом натікає метал. Ось чому монтажним дротом паяють "
                      "БЕЗ окремого флюсу, а суцільним — треба мазати флюс самому.",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "cross-section.svg"), W, H, *f)


# ── 2. Ландшафт сплавів: точка плавлення / пастоподібний інтервал ─────────────
def fig_alloys():
    W, H = 980, 560
    f = [text(W / 2, 30, "Сплави припою: де плавиться і чи є «кашоподібний» інтервал",
              size=15.5, bold=True)]

    # спільна шкала температур; вісь ВНИЗУ, рядки сплавів — вище неї
    gx0, gx1 = 300, 900
    axis_y = 452
    tmin, tmax = 178, 232
    def tx(temp):
        return gx0 + (temp - tmin) / (tmax - tmin) * (gx1 - gx0)

    # рядки сплавів (добре рознесені по вертикалі): назва, солідус, лідус, колір, примітка
    rows = [
        ("Sn63 Pb37",     183, 183, POS,       "евтектика — плавиться РІЗКО, в одній точці"),
        ("Sn60 Pb40",     183, 190, "#d1622e", "інтервал ~7°: майже як евтектика"),
        ("SAC305",        217, 220, FIELD,     "безсвинцевий стандарт SMD, інтервал ~3°"),
        ("Sn99.3 Cu0.7",  227, 227, NEG,       "безсвинцевий, евтектичний, але гарячий"),
    ]
    row_top = 92
    row_gap = 78
    # вертикальні гридлайни на кожні 10° — на всю висоту поля рядків (не крізь текст: текст рядків ліворуч від gx0)
    grid_top = row_top - 16
    grid_bot = axis_y
    for temp in range(180, 231, 10):
        xx = tx(temp)
        f.append(line(xx, grid_top, xx, grid_bot, color="#e6e9ee", sw=1))

    for i, (name, sol, liq, col, note) in enumerate(rows):
        yy = row_top + i * row_gap
        # назва сплаву — ліворуч від поля гридлайнів (простір чистий)
        f.append(text(gx0 - 30, yy - 4, name, size=13, bold=True, color=col, anchor="end"))
        # примітка — окремим рядком під назвою, теж ліворуч (не лізе в поле бруска)
        f.append(text(gx0 - 30, yy + 15, note, size=9.5, color="#5a6068", anchor="end"))
        if sol == liq:
            # евтектика — жирна крапля в точці + число над нею
            f.append(circle(tx(sol), yy, 9, fill=col, stroke=INK, sw=1.5))
            f.append(text(tx(sol), yy - 18, "%d °C" % sol, size=11, bold=True, color=col))
        else:
            # інтервал солідус..лідус — брусок; числа солідуса/лідуса по краях, ЗБОКУ (не над лінією)
            bx0, bx1 = tx(sol), tx(liq)
            f.append(rect(bx0, yy - 9, bx1 - bx0, 18, fill=col, stroke=INK, sw=1.3, rx=4))
            f.append(text(bx0 - 6, yy + 4, "%d" % sol, size=10.5, bold=True, color=col, anchor="end"))
            f.append(text(bx1 + 6, yy + 4, "%d °C" % liq, size=10.5, bold=True, color=col, anchor="start"))

    # вісь температур унизу
    f.append(line(gx0, axis_y, gx1, axis_y, color=INK, sw=2))
    for temp in range(180, 231, 10):
        xx = tx(temp)
        f.append(line(xx, axis_y, xx, axis_y + 7, color=MUTED, sw=1.3))
        f.append(text(xx, axis_y + 22, "%d" % temp, size=10.5, color=MUTED))
    f.append(text((gx0 + gx1) / 2, axis_y + 42, "температура, °C", size=11.5, bold=True))

    b, _, _ = textbox(W / 2, 526,
                      "Свинцевий Sn63Pb37 — єдина точка 183 °C: тверде↔рідке миттєво, тому шов не «пливе» й застигає блискучим. "
                      "Безсвинцеві гарячіші\n(≈217–227 °C) і примхливіші. Що ширший брусок інтервалу між солідусом і лідусом, "
                      "то легше ворухнути шов напівм'яким і дістати тьмяний «холодний».",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "alloys.svg"), W, H, *f)


# ── 3. Як читати котушку: розшифровка маркування ──────────────────────────────
def fig_label():
    W, H = 940, 520
    f = [text(W / 2, 30, "Як прочитати котушку припою: усе, що треба знати, — на етикетці",
              size=15.5, bold=True)]

    # котушка схематично ліворуч
    sx, sy = 200, 250
    f.append(circle(sx, sy, 130, fill=SPOOL, stroke=INK, sw=2))          # щока котушки
    f.append(circle(sx, sy, 128, fill="none", stroke="#5b616b", sw=1))
    f.append(circle(sx, sy, 40, fill="#20242a", stroke=INK, sw=1.6))     # маточина
    f.append(circle(sx, sy, 12, fill="#0f1216", stroke=INK, sw=1))       # отвір
    # намотаний дріт (кільце металу між маточиною і краєм)
    f.append('<circle cx="%.1f" cy="%.1f" r="86" fill="none" stroke="%s" stroke-width="70" stroke-opacity="0.9"/>'
             % (sx, sy, METAL))
    for r in range(52, 118, 7):
        f.append(circle(sx, sy, r, fill="none", stroke=METAL_D, sw=0.6))
    f.append(text(sx, sy - 150, "котушка з дротом", size=11.5, bold=True, color=MUTED))

    # етикетка праворуч — рамка з рядками маркування
    ex, ey, ew, eh = 470, 108, 420, 300
    f.append(rect(ex, ey, ew, eh, fill="#fffdf6", stroke=FLUX, sw=2, rx=10))
    f.append(text(ex + ew / 2, ey + 28, "ЕТИКЕТКА", size=12, bold=True, color="#8a6420"))
    f.append(line(ex + 20, ey + 40, ex + ew - 20, ey + 40, color="#e0cfa0", sw=1.2))

    # рядки: код → що означає
    label_rows = [
        ("Sn60 Pb40", "сплав: 60 % олова, 40 % свинцю", POS),
        ("Ø 0.8 мм", "діаметр дроту", NEG),
        ("Flux 2.0 %", "частка каніфолі в серцевині", "#8a6420"),
        ("Rosin / RMA", "тип флюсу (мʼяко активований)", FIELD),
        ("100 g", "маса дроту на котушці", MUTED),
    ]
    ry = ey + 66
    for code, mean, col in label_rows:
        f.append(text(ex + 30, ry, code, size=13, bold=True, color=col, anchor="start"))
        f.append(text(ex + 190, ry, "→  " + mean, size=10.5, color="#3a4048", anchor="start"))
        ry += 44

    b, _, _ = textbox(W / 2, 486,
                      "П'ять чисел вирішують усе: сплав (Sn/Pb — свинцевий чи ні), діаметр (тонкий для дрібного, "
                      "товстий для великого),\nчастка й тип флюсу (для новачка — свинцевий Sn60/63 + no-clean або RMA). "
                      "Решта на етикетці — маса й виробник.",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "label.svg"), W, H, *f)


# ── 4. Олов'яна чума: β-олово ↔ α-олово при 13.2 °C (для hist-вставки) ────────
def fig_tin_pest():
    W, H = 980, 560
    f = [text(W / 2, 30, "Олов'яна чума: те саме олово, дві кристалічні форми",
              size=15.5, bold=True)]

    # горизонтальна вісь температури з порогом 13.2 °C посередині
    ax_y = 168
    gx0, gx1 = 90, 890
    tmin, tmax = -50, 60
    def tx(t):
        return gx0 + (t - tmin) / (tmax - tmin) * (gx1 - gx0)

    thr = tx(13.2)
    # холодна ліва зона / тепла права зона (легка заливка)
    f.append(rect(gx0, ax_y - 44, thr - gx0, 44, fill="#eaf0fd", stroke="none", rx=0))
    f.append(rect(thr, ax_y - 44, gx1 - thr, 44, fill="#fdecea", stroke="none", rx=0))
    f.append(line(gx0, ax_y, gx1, ax_y, color=INK, sw=2))
    for t in range(-50, 61, 10):
        xx = tx(t)
        f.append(line(xx, ax_y, xx, ax_y + 7, color=MUTED, sw=1.2))
        f.append(text(xx, ax_y + 22, "%d" % t, size=10, color=MUTED))
    f.append(text((gx0 + gx1) / 2, ax_y + 42, "температура, °C", size=11, bold=True))

    # поріг рівноваги 13.2 °C
    f.append(line(thr, ax_y - 52, thr, ax_y + 8, color=INK, sw=1.8, dash="5 4"))
    f.append(text(thr, ax_y - 60, "13.2 °C — рівновага", size=11, bold=True))
    # напрямки перетворення (стрілки над зонами, добре рознесені від порога)
    f.append(mtext(tx(-30), ax_y - 22, ["нижче — стійке СІРЕ", "(β → α, повільно)"],
                   size=10.5, bold=True, color=NEG, lh=1.2))
    f.append(mtext(tx(38), ax_y - 22, ["вище — стійке БІЛЕ", "(α → β)"],
                   size=10.5, bold=True, color=POS, lh=1.2))

    # два «зразки» під віссю: біле β (щільний метал) і сіре α (розсипаний порошок)
    by = 360
    # ліворуч — біле β-олово: суцільний блок
    bx = 250
    f.append(text(bx, by - 96, "β-олово (біле)", size=13, bold=True, color="#2b3138"))
    f.append(rect(bx - 70, by - 70, 140, 140, fill=METAL, stroke=METAL_D, sw=3, rx=8))
    f.append('<path d="M %.1f %.1f L %.1f %.1f" stroke="#c3cad1" stroke-width="6" stroke-linecap="round"/>'
             % (bx - 52, by - 50, bx + 40, by - 50))
    f.append(mtext(bx, by + 96, ["щільне, ковке, блискуче", "7.31 г/см³ · тетрагональне"],
                   size=10, color=MUTED, lh=1.25))

    # стрілка перетворення між зразками
    f.append(arrow(bx + 92, by, bx + 232, by, color=INK, sw=2.2))
    f.append(mtext((bx + 92 + bx + 232) / 2, by - 30, ["на морозі", "розпад"],
                   size=10.5, bold=True, color=NEG, lh=1.2))
    f.append(text((bx + 92 + bx + 232) / 2, by + 40, "+27 % об'єму", size=11, bold=True, color=POS))

    # праворуч — сіре α-олово: розсип «крупинок»
    ax = bx + 324
    f.append(text(ax, by - 96, "α-олово (сіре)", size=13, bold=True, color="#2b3138"))
    import random
    random.seed(7)
    # контур насипу
    f.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f Q %.1f %.1f %.1f %.1f Z" '
             'fill="#d7dbe0" stroke="#9aa0a8" stroke-width="1.6"/>'
             % (ax - 82, by + 66, ax, by - 40, ax + 82, by + 66, ax, by + 78, ax - 82, by + 66))
    for _ in range(70):
        gx = ax + random.uniform(-72, 72)
        gy = by + random.uniform(-28, 60)
        # тримати крупинки всередині трикутного насипу (грубо)
        if abs(gx - ax) / 72 + (by + 66 - gy) / 100 < 1.05:
            f.append(circle(gx, gy, random.uniform(2.2, 4.2), fill="#aeb4bc", stroke="#8c929b", sw=0.6))
    f.append(mtext(ax, by + 96, ["крихкий сірий порошок", "5.77 г/см³ · кубічне (як алмаз)"],
                   size=10, color=MUTED, lh=1.25))

    b, _, _ = textbox(W / 2, 522,
                      "Це не корозія й не бруд: атоми олова просто перебудовуються в іншу ґратку, менш щільну. "
                      "Об'єм зростає на чверть,\nметал тріскає й обертається на порох. Домішки (свинець, вісмут, сурма) "
                      "цей перехід сильно гальмують — тому реальний припій ним майже не хворіє.",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "tin-pest.svg"), W, H, *f)


if __name__ == "__main__":
    fig_cross_section()
    fig_alloys()
    fig_label()
    fig_tin_pest()
    print("OK: 4 figures ->", IMG)
