import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: RSS проти лінійної суми ────────────────────────────────────────
# ЯДРО теми. Дві похибки 3 і 4 складають по-різному:
#  • найгірший випадок — лінійно: 3 + 4 = 7 (обидві промахнулися в один бік);
#  • незалежні — квадратично (RSS): √(3²+4²) = 5, бо вони «перпендикулярні»
#    й частково гасять одна одну.
# Геометрія прямокутного трикутника робить «чому √(Σσ²)» видимим: катети — це
# окремі похибки, гіпотенуза — їхня незалежна сума.

def fig_rss_vs_linear():
    W, H = 640, 470
    ox, oy = 150, 360        # початок координат (нижній лівий кут трикутника)
    sc = 42                  # пікселів на одиницю похибки
    a, b = 3.0, 4.0          # дві похибки (катети)
    c = math.hypot(a, b)     # = 5.0 — RSS

    parts = []

    # — лінійна (найгірший випадок): пряма лінія 3+4=7 уздовж однієї осі —
    # малюємо тонкою пунктирною шкалою праворуч, щоб порівняти довжини
    lin_x = 470
    lin_top = oy - (a + b) * sc
    parts.append(line(lin_x, oy, lin_x, lin_top, color=POS, sw=6))
    parts.append(line(lin_x - 10, oy - a * sc, lin_x + 10, oy - a * sc,
                      color=BG, sw=2))
    parts.append(text(lin_x + 22, oy - a * sc * 0.5 + 5, '3', size=15,
                      color=POS, anchor='start', bold=True))
    parts.append(text(lin_x + 22, oy - (a + b * 0.5) * sc + 5, '4', size=15,
                      color=POS, anchor='start', bold=True))
    parts.append(text(lin_x, lin_top - 16, '7', size=20, color=POS,
                      anchor='middle', bold=True))
    parts.append(text(lin_x, oy + 26, 'лінійно', size=14, color=POS,
                      anchor='middle', bold=True))
    parts.append(text(lin_x, oy + 46, '3 + 4', size=12, color=MUTED,
                      anchor='middle'))

    # — RSS (незалежні): прямокутний трикутник, катети 3 і 4, гіпотенуза 5 —
    Ax, Ay = ox, oy                      # прямий кут
    Bx, By = ox + b * sc, oy             # уздовж осі — катет 4 (червоний)
    Cx, Cy = ox, oy - a * sc             # вертикальний катет 3 (синій)
    # катет b (горизонтальний)
    parts.append(line(Ax, Ay, Bx, By, color=POS, sw=6))
    parts.append(text((Ax + Bx) / 2, Ay + 26, '4', size=16, color=POS,
                      anchor='middle', bold=True))
    # катет a (вертикальний)
    parts.append(line(Ax, Ay, Cx, Cy, color=NEG, sw=6))
    parts.append(text(Ax - 18, (Ay + Cy) / 2 + 5, '3', size=16, color=NEG,
                      anchor='end', bold=True))
    # гіпотенуза c
    parts.append(line(Cx, Cy, Bx, By, color=FIELD, sw=6))
    parts.append(text((Cx + Bx) / 2 + 16, (Cy + By) / 2 - 10, '5', size=20,
                      color=FIELD, anchor='middle', bold=True))
    # позначка прямого кута
    q = 14
    parts.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="1.5"/>'
                 % (Ax + q, Ay, Ax + q, Ay - q, Ax, Ay - q, MUTED))
    parts.append(text((Ax + Bx) / 2, Cy - 22, 'незалежні (RSS)', size=14,
                      color=FIELD, anchor='middle', bold=True))
    parts.append(text((Ax + Bx) / 2, Cy - 4, '√(3² + 4²)', size=12,
                      color=MUTED, anchor='middle'))

    title = 'Дві похибки 3 і 4: складати лінійно чи квадратично?'
    render(os.path.join(OUT, 'rss-vs-linear.svg'), W, H, *parts, title=title)


# ── Фігура 2: поширення похибки через формулу (важелі чутливості) ─────────────
# Показує, що внесок кожного джерела на виході зважений похідною (чутливістю):
# та сама похибка входу дає БІЛЬШИЙ внесок там, де функція крутіша.
# Метафора важеля: довге плече (велика чутливість) підсилює дрожання входу.

def fig_propagation():
    W, H = 660, 430
    parts = []

    # три входи зліва, кожен зі своєю похибкою σ; стрілки у «чорну скриньку» f
    bx, bw, bh = 300, 150, 150
    by = 150
    parts.append(rect(bx, by, bw, bh, fill='#eef6ef', stroke=FIELD, sw=2))
    parts.append(text(bx + bw / 2, by + bh / 2 - 8, 'f(x, y, z)', size=20,
                      bold=True, color=INK))
    parts.append(text(bx + bw / 2, by + bh / 2 + 16, 'формула', size=12,
                      color=MUTED))

    inputs = [
        ('x', 'σ_x', 70,  '×∂f/∂x', NEG),
        ('y', 'σ_y', 215, '×∂f/∂y', POS),
        ('z', 'σ_z', 360, '×∂f/∂z', NEG),
    ]
    iy = [110, 225, 340]
    for (lbl, sig, _, gain, col), yy in zip(inputs, iy):
        box, bwid, _h = textbox(110, yy, '%s ± %s' % (lbl, sig), size=14,
                                fill=FILL, stroke=col, sw=1.8)
        parts.append(box)
        parts.append(arrow(110 + bwid / 2 + 4, yy, bx - 6, by + bh / 2,
                           color=col, sw=1.8))
        # підпис «×чутливість» на стрілці
        mx = (110 + bwid / 2 + bx) / 2
        my = (yy + by + bh / 2) / 2 - 8
        parts.append(text(mx, my, gain, size=11, color=col, anchor='middle'))

    # вихід праворуч: підсумкова похибка σ_f
    obox, owid, _h = textbox(595, by + bh / 2, ['σ_f'], size=18,
                             fill='#eef6ef', stroke=FIELD, sw=2, min_w=64,
                             bold=True)
    parts.append(arrow(bx + bw + 6, by + bh / 2, 595 - owid / 2 - 6,
                       by + bh / 2, color=FIELD, sw=2))
    parts.append(obox)
    parts.append(text(595, by + bh / 2 + 44, 'підсумок', size=12,
                      color=MUTED, anchor='middle'))
    # формула поширення під схемою — як саме збирається σ_f
    parts.append(text(W / 2, 400,
                      'σ_f = √( (∂f/∂x·σ_x)² + (∂f/∂y·σ_y)² + (∂f/∂z·σ_z)² )',
                      size=15, color=INK, anchor='middle', bold=True))

    title = 'Поширення: кожне джерело зважене чутливістю ∂f/∂(·)'
    render(os.path.join(OUT, 'propagation.svg'), W, H, *parts, title=title)


if __name__ == '__main__':
    fig_rss_vs_linear()
    fig_propagation()
    print('OK: 2 figures ->', OUT)
