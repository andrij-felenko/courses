# -*- coding: utf-8 -*-
"""Фігури до статті «Макетна плата (міні)». Запуск: python figs.py — пише у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

COL_HI = "#eaf3ff"   # підсвітка однієї з'єднаної колонки
CLIP   = "#9aa4b2"   # метал пружинного контакту
WIRE   = "#c78a2b"   # мідна ніжка/дріт


def fig_topology():
    """Внутрішня топологія 170-точкової міні-плати: 17 колонок по 5 з'єднаних дірок,
    розрізаних центральною канавкою на верхню й нижню половини; РЕЙОК живлення НЕМА."""
    W, H = 760, 486
    frags = []

    nc = 17            # колонок
    x0 = 70            # ліва дірка
    step = 36          # крок між колонками (px, візуальний — не 2.54 мм)
    r = 6              # радіус дірки
    top_y = [110, 138, 166, 194, 222]     # 5 дірок верхньої половини
    bot_y = [300, 328, 356, 384, 412]     # 5 дірок нижньої половини

    # корпус плати
    frags.append(rect(40, 78, W - 80, H - 118, fill="#fbfcfd", stroke=INK, sw=2, rx=12))

    # підсвітити одну колонку (напр. 5-ту) як приклад «одна колонка = один вузол»
    hc = 4  # індекс підсвіченої колонки (0-based) -> 5-та
    hx = x0 + hc * step
    frags.append(rect(hx - 15, 96, 30, 140, fill=COL_HI, stroke=NEG, sw=1.5, rx=8))
    frags.append(rect(hx - 15, 288, 30, 140, fill=COL_HI, stroke=NEG, sw=1.5, rx=8))

    # верхня й нижня банки дірок
    for c in range(nc):
        x = x0 + c * step
        for y in top_y:
            frags.append(circle(x, y, r, fill=BG, stroke=MUTED, sw=1.4))
        for y in bot_y:
            frags.append(circle(x, y, r, fill=BG, stroke=MUTED, sw=1.4))

    # вертикальні зв'язки всередині кожної колонки (те, що електрично сполучено)
    for c in range(nc):
        x = x0 + c * step
        col = NEG if c == hc else "#c3ccd6"
        sw = 2.4 if c == hc else 1.6
        frags.append(line(x, top_y[0], x, top_y[-1], color=col, sw=sw))
        frags.append(line(x, bot_y[0], x, bot_y[-1], color=col, sw=sw))

    # центральна канавка
    gy = (top_y[-1] + bot_y[0]) / 2
    frags.append(rect(52, gy - 13, W - 104, 26, fill="#eef1f4", stroke=MUTED, sw=1.2, rx=4))
    frags.append(text(W / 2, gy + 5, "центральна канавка (розрив)", size=13, color=MUTED, italic=True))

    # підписи половин
    frags.append(text(W - 52, 100, "верхня половина", size=12, color=MUTED, anchor="end"))
    frags.append(text(W - 52, 285, "нижня половина", size=12, color=MUTED, anchor="end"))

    # виноска до підсвіченої колонки
    b, bw, bh = textbox(hx, 452, "ці 5 дірок — один вузол\n(з'єднані між собою)",
                        size=13, color=NEG, stroke=NEG, fill=COL_HI, pad=9)
    frags.append(line(hx, 236, hx, 452 - bh / 2, color=NEG, sw=1.4, dash="4 3"))
    frags.append(b)

    # прямо сказати про відсутність рейок
    note, nw, nh = textbox(W / 2, 55, "рейок живлення обабіч НЕМА — лише короткі колонки",
                           size=13, bold=True, color=POS, stroke=POS, fill="#fdecea", pad=9)
    frags.append(note)

    render(os.path.join(OUT, 'topology.svg'), W, H, *frags,
           title="Що з чим з'єднано в міні-платі (170 точок)")


def fig_clip():
    """Розріз однієї дірки: пружинний металевий контакт (кліп) затискає ніжку.
    Показує, ЧОМУ тримає без паяння і чому крок 2.54 мм."""
    W, H = 740, 430
    frags = []

    # ── ліворуч: розріз клітинки з пружинним кліпом ──
    lx, ly, lw, lh = 60, 90, 300, 250
    frags.append(rect(lx, ly, lw, lh, fill="#fbfcfd", stroke=INK, sw=2, rx=10))
    frags.append(text(lx + lw / 2, ly - 12, "розріз однієї дірки", size=14, bold=True))

    # пластиковий корпус (масив), верхня поверхня з діркою
    top_surf = ly + 40
    frags.append(rect(lx + 20, top_surf, lw - 40, 18, fill="#e7ebef", stroke=MUTED, sw=1.2, rx=3))
    # отвір у поверхні
    hole_cx = lx + lw / 2
    frags.append(rect(hole_cx - 9, top_surf - 1, 18, 20, fill=BG, stroke=MUTED, sw=1.2, rx=2))

    # дріт/ніжка входить у дірку
    wtop = ly + 8
    frags.append(line(hole_cx, wtop, hole_cx, top_surf + 118, color=WIRE, sw=6))
    frags.append(circle(hole_cx, wtop, 4, fill=WIRE, stroke=WIRE, sw=1))

    # пружинний кліп — дві вигнуті «щоки», що тиснуть на ніжку
    clip_top = top_surf + 30
    clip_bot = top_surf + 120
    # ліва щока
    frags.append('<path d="M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" '
                 'fill="none" stroke="%s" stroke-width="5"/>'
                 % (hole_cx - 24, clip_top, hole_cx - 24, clip_top + 30,
                    hole_cx - 7, clip_top + 30, hole_cx - 7, clip_bot, CLIP))
    # права щока
    frags.append('<path d="M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" '
                 'fill="none" stroke="%s" stroke-width="5"/>'
                 % (hole_cx + 24, clip_top, hole_cx + 24, clip_top + 30,
                    hole_cx + 7, clip_top + 30, hole_cx + 7, clip_bot, CLIP))
    # спільна основа кліпа
    frags.append(line(hole_cx - 24, clip_top, hole_cx + 24, clip_top, color=CLIP, sw=5))

    # стрілки тиску щік на ніжку
    frags.append(arrow(hole_cx - 20, clip_bot - 18, hole_cx - 9, clip_bot - 18, color=POS, sw=2))
    frags.append(arrow(hole_cx + 20, clip_bot - 18, hole_cx + 9, clip_bot - 18, color=POS, sw=2))

    # підписи ліворуч (поза лініями)
    frags.append(text(lx + 14, wtop + 6, "ніжка", size=12, color=WIRE, anchor="start", bold=True))
    b1, b1w, b1h = textbox(lx + 232, clip_top + 6, "пружинна\nщока", size=12, color=INK,
                           stroke=CLIP, fill="#f0f2f5", pad=7)
    frags.append(b1)
    frags.append(text(lx + lw / 2, clip_bot + 26, "щоки тиснуть → тримає без паяння",
                      size=12, color=POS, bold=True))

    # ── праворуч: крок 2.54 мм і чому він ──
    rx, ry = 430, 120
    dot = 8
    pitch = 62
    ys = ry
    xs = [rx, rx + pitch, rx + 2 * pitch, rx + 3 * pitch]
    for x in xs:
        frags.append(circle(x, ys, dot, fill=BG, stroke=INK, sw=1.6))
        frags.append(circle(x, ys + 90, dot, fill=BG, stroke=INK, sw=1.6))
    # розмірна лінія кроку
    frags.append(line(xs[0], ys - 34, xs[1], ys - 34, color=NEG, sw=1.6))
    frags.append(line(xs[0], ys - 40, xs[0], ys - 28, color=NEG, sw=1.6))
    frags.append(line(xs[1], ys - 40, xs[1], ys - 28, color=NEG, sw=1.6))
    frags.append(text((xs[0] + xs[1]) / 2, ys - 44, "2.54 мм = 0.1″",
                      size=13, color=NEG, bold=True))

    # ніжки DIP-корпусу, що точно лягають у два ряди
    chip_x = rx - 6
    chip_w = 3 * pitch + 12
    frags.append(rect(chip_x, ys + 24, chip_w, 42, fill="#dfe4ea", stroke=INK, sw=1.6, rx=5))
    frags.append(text(rx + 3 * pitch / 2, ys + 50, "корпус DIP", size=12, color=INK))
    for x in xs:
        frags.append(line(x, ys + 8, x, ys + 24, color=WIRE, sw=4))     # верхні ніжки в дірки
        frags.append(line(x, ys + 66, x, ys + 82, color=WIRE, sw=4))    # нижні ніжки в дірки

    b2, b2w, b2h = textbox(rx + 3 * pitch / 2, ys + 150,
                           "той самий крок, що й у ніжок мікросхем —\nтому DIP сідає точно в дірки",
                           size=12, color=INK, stroke=MUTED, fill="#f0f2f5", pad=8)
    frags.append(b2)
    frags.append(text(rx + 3 * pitch / 2, ry - 66, "крок сітки", size=14, bold=True))

    render(os.path.join(OUT, 'clip-pitch.svg'), W, H, *frags,
           title="Чому тримає без паяння і чому крок саме 2.54 мм")


def fig_history():
    """Три епохи макетки в один ряд: дерев'яна дошка з цвяхами (1920-ті) →
    пружинна плата Томпсона (Lucite, 1960/1963) → сітка 0.1″ Портуґала (1971/1973),
    що збіглася з ніжками DIP. Наголос: саме крок 0.1″ зробив макетку сучасною."""
    W, H = 900, 430
    frags = []

    # три панелі-епохи
    pw, ph = 250, 250
    py = 92
    gap = (W - 3 * pw) / 4
    xs = [gap + i * (pw + gap) for i in range(3)]

    titles = ["1920-ті", "1960 → 1963", "1971 → 1973"]
    caps = ["дерев'яна\nхлібна дошка", "пружинна плата\n(О. Томпсон, DeVry)",
            "сітка 0.1″\n(Р. Портуґал, E&L)"]

    for i, x in enumerate(xs):
        frags.append(rect(x, py, pw, ph, fill="#fbfcfd", stroke=INK, sw=2, rx=10))
        frags.append(text(x + pw / 2, py - 14, titles[i], size=15, bold=True))

    # ── панель 1: дошка з цвяхами, дріт накручено, деталь зверху ──
    x = xs[0]
    bd_x, bd_y, bd_w, bd_h = x + 24, py + 60, pw - 48, 120
    frags.append(rect(bd_x, bd_y, bd_w, bd_h, fill="#e6d3ad", stroke="#a9834a", sw=2, rx=6))
    # текстура дерева
    for k in range(1, 4):
        yy = bd_y + k * bd_h / 4
        frags.append(line(bd_x + 6, yy, bd_x + bd_w - 6, yy, color="#cdb583", sw=1))
    # цвяхи (голівки) + дріт від цвяха до цвяха
    nails = [(bd_x + 34, bd_y + 34), (bd_x + 120, bd_y + 34),
             (bd_x + 70, bd_y + 88), (bd_x + 160, bd_y + 88)]
    frags.append(line(nails[0][0], nails[0][1], nails[1][0], nails[1][1], color=WIRE, sw=3))
    frags.append(line(nails[1][0], nails[1][1], nails[3][0], nails[3][1], color=WIRE, sw=3))
    frags.append(line(nails[0][0], nails[0][1], nails[2][0], nails[2][1], color=WIRE, sw=3))
    for (nx, ny) in nails:
        frags.append(circle(nx, ny, 5, fill="#7a7f87", stroke=INK, sw=1.4))
    frags.append(text(x + pw / 2, py + ph - 46, caps[0].split("\n")[0], size=13, color=INK))
    frags.append(text(x + pw / 2, py + ph - 28, caps[0].split("\n")[1], size=13, color=INK))

    # ── панель 2: прозора плата з пружинними щоками, БЕЗ єдиного кроку ──
    x = xs[1]
    bd_x, bd_y, bd_w, bd_h = x + 24, py + 56, pw - 48, 124
    frags.append(rect(bd_x, bd_y, bd_w, bd_h, fill="#e9f3f6", stroke="#79a7b4", sw=2, rx=6))
    # кілька пар щік різного, НЕ уніфікованого розташування
    pairs = [(bd_x + 42, bd_y + 40), (bd_x + 120, bd_y + 40), (bd_x + 80, bd_y + 92)]
    for (cx, cy) in pairs:
        frags.append(line(cx - 12, cy, cx - 4, cy + 20, color=CLIP, sw=4))
        frags.append(line(cx + 12, cy, cx + 4, cy + 20, color=CLIP, sw=4))
        frags.append(line(cx, cy - 14, cx, cy + 4, color=WIRE, sw=4))  # ніжка
    frags.append(text(x + pw / 2, py + ph - 46, caps[1].split("\n")[0], size=13, color=INK))
    frags.append(text(x + pw / 2, py + ph - 28, caps[1].split("\n")[1], size=13, color=INK))

    # ── панель 3: рівна сітка 0.1″, DIP лягає ніжками точно в дірки ──
    x = xs[2]
    bd_x, bd_y, bd_w, bd_h = x + 24, py + 56, pw - 48, 124
    frags.append(rect(bd_x, bd_y, bd_w, bd_h, fill="#f6f8fa", stroke=MUTED, sw=2, rx=6))
    gx0, gy0, gp = bd_x + 30, bd_y + 34, 24
    ncols = 6
    grid_x = [gx0 + c * gp for c in range(ncols)]
    grid_y = [gy0, gy0 + 56]
    for gy in grid_y:
        for gx in grid_x:
            frags.append(circle(gx, gy, 4, fill=BG, stroke=INK, sw=1.3))
    # корпус DIP зверху, ніжки в два ряди точно в дірки
    dip_x = grid_x[0] - 6
    dip_w = (ncols - 1) * gp + 12
    frags.append(rect(dip_x, gy0 + 18, dip_w, 20, fill="#dfe4ea", stroke=INK, sw=1.5, rx=4))
    for gx in grid_x:
        frags.append(line(gx, gy0 + 4, gx, gy0 + 18, color=WIRE, sw=3))
        frags.append(line(gx, gy0 + 38, gx, gy0 + 52, color=WIRE, sw=3))
    # розмір кроку
    frags.append(line(grid_x[0], gy0 - 16, grid_x[1], gy0 - 16, color=NEG, sw=1.5))
    frags.append(text((grid_x[0] + grid_x[1]) / 2, gy0 - 20, "0.1″", size=11, color=NEG, bold=True))
    frags.append(text(x + pw / 2, py + ph - 46, caps[2].split("\n")[0], size=13, color=INK))
    frags.append(text(x + pw / 2, py + ph - 28, caps[2].split("\n")[1], size=13, color=INK))

    # стрілки-переходи між панелями
    for i in range(2):
        ax1 = xs[i] + pw + 6
        ax2 = xs[i + 1] - 6
        frags.append(arrow(ax1, py + ph / 2, ax2, py + ph / 2, color=MUTED, sw=2.2))

    # нижній наголос
    note, nw, nh = textbox(W / 2, py + ph + 40,
                           "поворот зробила не «безпаяльність» (вона вже була), а СІТКА 0.1″ —"
                           "\nсаме вона збіглася з ніжками DIP-мікросхем",
                           size=13, bold=True, color=POS, stroke=POS, fill="#fdecea", pad=10)
    frags.append(note)

    render(os.path.join(OUT, 'history.svg'), W, H, *frags,
           title="Три епохи макетки: від дошки з цвяхами до сітки 0.1″")


if __name__ == '__main__':
    fig_topology()
    fig_clip()
    fig_history()
    print('OK: topology.svg, clip-pitch.svg, history.svg')
