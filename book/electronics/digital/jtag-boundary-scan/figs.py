# -*- coding: utf-8 -*-
"""Фігури до теми «JTAG і граничне сканування».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_boundary_cells():
    """Кільце комірок граничного сканування навколо ядра чипа."""
    W, H = 640, 470
    p = []
    # ядро чипа
    cx, cy = W / 2, H / 2 + 8
    core_w, core_h = 210, 150
    p.append(rect(cx - core_w / 2, cy - core_h / 2, core_w, core_h,
                  fill="#eef2f7", stroke=LINE, sw=2, rx=10))
    p.append(text(cx, cy - 6, "ЯДРО ЧИПА", size=16, bold=True))
    p.append(text(cx, cy + 16, "звичайна логіка", size=12, color=MUTED))

    # позиції комірок навколо ядра (кільце)
    ring_w, ring_h = 380, 300
    x0, y0 = cx - ring_w / 2, cy - ring_h / 2
    cell = 34
    # координати центрів комірок по колу (за годинниковою від лівого-верху)
    tops = [x0 + ring_w * f for f in (0.20, 0.42, 0.64, 0.86)]
    bots = tops
    lefts = [y0 + ring_h * f for f in (0.30, 0.62, 0.94)]
    rights = lefts
    cells = []
    for x in tops:
        cells.append((x, y0))                 # верх (ліворуч→праворуч)
    for y in rights:
        cells.append((x0 + ring_w, y))        # правий бік (згори→вниз)
    for x in reversed(bots):
        cells.append((x, y0 + ring_h))        # низ (праворуч→ліворуч)
    for y in reversed(lefts):
        cells.append((x0, y))                 # лівий бік (знизу→вгору)

    # ніжки: короткий штрих від кожної комірки назовні
    for (x, y) in cells:
        dx = 0 if abs(x - cx) < ring_w / 2 - 1 else (1 if x > cx else -1)
        dy = 0 if abs(y - cy) < ring_h / 2 - 1 else (1 if y > cy else -1)
        # штрих ніжки назовні
        p.append(line(x + dx * cell * 0.55, y + dy * cell * 0.55,
                      x + dx * (cell * 0.55 + 16), y + dy * (cell * 0.55 + 16),
                      color=MUTED, sw=2))

    # ланцюг між комірками (пунктир по колу)
    for i in range(len(cells)):
        a = cells[i]
        b = cells[(i + 1) % len(cells)]
        p.append(line(a[0], a[1], b[0], b[1], color=FIELD, sw=1.6, dash="4 4"))

    # самі комірки (поверх ланцюга)
    for (x, y) in cells:
        p.append(rect(x - cell / 2, y - cell / 2, cell, cell,
                      fill="#e8f6ee", stroke=FIELD, sw=1.8, rx=5))

    # TDI / TDO стрілки в кільце (лівий-верх кут)
    first = cells[0]
    last = cells[-1]
    p.append(arrow(x0 - 70, first[1] - 6, first[0] - cell / 2, first[1], color=NEG, sw=2))
    p.append(text(x0 - 74, first[1] - 12, "TDI", size=13, color=NEG, bold=True, anchor="end"))
    p.append(arrow(last[0] - cell / 2, last[1], x0 - 70, last[1] + 6, color=POS, sw=2))
    p.append(text(x0 - 74, last[1] + 22, "TDO", size=13, color=POS, bold=True, anchor="end"))

    # легенда
    bx = 14
    p.append(rect(bx, H - 42, 200, 30, fill="#e8f6ee", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(bx + 100, H - 22, "комірка граничного сканування", size=11))

    render(os.path.join(IMG, "boundary-cells.svg"), W, H, *p,
           title="Кільце комірок по межі кристала")


def fig_daisy_chain():
    """Гірлянда JTAG: TDO→TDI трьох чипів, спільні TCK і TMS."""
    W, H = 700, 360
    p = []
    chip_w, chip_h = 130, 90
    gap = 55
    total = 3 * chip_w + 2 * gap
    x0 = (W - total) / 2
    ytop = 70
    ycore = ytop + chip_h / 2
    names = ["чип 1", "чип 2", "чип 3"]
    xs = [x0 + i * (chip_w + gap) for i in range(3)]

    # шина TCK/TMS знизу — спільна
    ybus = ytop + chip_h + 70
    p.append(line(x0 - 40, ybus, x0 + total + 40, ybus, color=INK, sw=2.4))
    p.append(line(x0 - 40, ybus + 22, x0 + total + 40, ybus + 22, color=INK, sw=2.4))
    p.append(text(x0 - 46, ybus + 5, "TCK", size=13, bold=True, anchor="end"))
    p.append(text(x0 - 46, ybus + 27, "TMS", size=13, bold=True, anchor="end"))

    for i, x in enumerate(xs):
        p.append(rect(x, ytop, chip_w, chip_h, fill="#eef2f7", stroke=LINE, sw=2, rx=8))
        p.append(text(x + chip_w / 2, ycore + 5, names[i], size=15, bold=True))
        # відводи від шини до чипа
        p.append(line(x + chip_w * 0.35, ybus, x + chip_w * 0.35, ytop + chip_h, color=INK, sw=1.8))
        p.append(line(x + chip_w * 0.65, ybus + 22, x + chip_w * 0.65, ytop + chip_h, color=INK, sw=1.8))

    # нитка даних TDI→(TDO→TDI)→TDO
    p.append(arrow(x0 - 55, ycore, xs[0], ycore, color=NEG, sw=2.4))
    p.append(text(x0 - 58, ycore - 8, "TDI", size=13, color=NEG, bold=True, anchor="end"))
    for i in range(2):
        xa = xs[i] + chip_w
        xb = xs[i + 1]
        p.append(arrow(xa, ycore, xb, ycore, color=INK, sw=2.2))
        p.append(text((xa + xb) / 2, ycore - 8, "TDO→TDI", size=10, color=MUTED))
    p.append(arrow(xs[2] + chip_w, ycore, xs[2] + chip_w + 55, ycore, color=POS, sw=2.4))
    p.append(text(xs[2] + chip_w + 58, ycore - 8, "TDO", size=13, color=POS, bold=True))

    p.append(text(W / 2, H - 14, "дані течуть наскрізь через усі чипи; такт і режим — спільні",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "daisy-chain.svg"), W, H, *p,
           title="Гірлянда JTAG на чотирьох дротах")


def fig_probe_access():
    """Чому «ложе цвяхів» здалося: щуп дістає верхню площинку, але не кульку під BGA."""
    W, H = 700, 340
    p = []
    # дві сцени поруч: ліворуч — стара плата (доступ є), праворуч — BGA (доступу нема)
    pcb_y = 210
    pcb_h = 26

    # ── ЛІВОРУЧ: наскрізний вивід, площинка зверху ──
    lx = 175
    p.append(text(lx, 60, "1970-ті: ніжки й площинки зверху", size=14, bold=True))
    p.append(rect(lx - 130, pcb_y, 260, pcb_h, fill="#eef2f7", stroke=LINE, sw=1.6, rx=3))
    # корпус мікросхеми над платою
    p.append(rect(lx - 60, pcb_y - 78, 120, 60, fill="#e8f6ee", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(lx, pcb_y - 44, "чип", size=13, bold=True))
    # ніжки з боків, що приходять на верхні площинки
    for dx in (-52, -30, 30, 52):
        p.append(line(lx + dx, pcb_y - 18, lx + dx, pcb_y - 2, color=INK, sw=2))
        p.append(rect(lx + dx - 8, pcb_y - 4, 16, 6, fill="#f4c430", stroke=LINE, sw=1))
    # щуп-голка знизу тягнеться до нижньої сторони площинки (доступ Є)
    for dx in (-52, 52):
        p.append(line(lx + dx, pcb_y + pcb_h, lx + dx, pcb_y + pcb_h + 70, color=POS, sw=2.4))
        p.append(circle(lx + dx, pcb_y + pcb_h + 70, 4, fill=POS, stroke=POS, sw=1))
    p.append(text(lx, pcb_y + pcb_h + 96, "голка дістає контакт", size=12, color=FIELD, bold=True))

    # ── ПРАВОРУЧ: BGA, кульки під корпусом ──
    rx = 525
    p.append(text(rx, 60, "кінець 1980-х: кульки під корпусом (BGA)", size=14, bold=True))
    p.append(rect(rx - 130, pcb_y, 260, pcb_h, fill="#eef2f7", stroke=LINE, sw=1.6, rx=3))
    # корпус BGA сидить просто на платі
    p.append(rect(rx - 70, pcb_y - 60, 140, 60, fill="#e8f6ee", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(rx, pcb_y - 26, "чип (BGA)", size=13, bold=True))
    # кульки припою між дном корпусу й платою — сховані
    for dx in (-52, -30, -10, 10, 30, 52):
        p.append(circle(rx + dx, pcb_y - 4, 6, fill="#f4c430", stroke=LINE, sw=1))
    # щуп упирається в дно корпусу — доступу НЕМА
    p.append(line(rx, pcb_y + pcb_h, rx, pcb_y + pcb_h + 70, color=POS, sw=2.4, dash="5 4"))
    # перекреслений доступ
    p.append(line(rx - 12, pcb_y + pcb_h + 30, rx + 12, pcb_y + pcb_h + 54, color=POS, sw=3))
    p.append(line(rx + 12, pcb_y + pcb_h + 30, rx - 12, pcb_y + pcb_h + 54, color=POS, sw=3))
    p.append(text(rx, pcb_y + pcb_h + 96, "голці нікуди тицятися", size=12, color=POS, bold=True))

    render(os.path.join(IMG, "probe-access.svg"), W, H, *p,
           title="Куди зникли контакти: чому «ложе цвяхів» перестало діставати")


def fig_timeline():
    """Часова лінія народження JTAG: криза → група 1985 → стандарт 1990 → BSDL 1994."""
    W, H = 720, 300
    p = []
    ax_y = 150
    x0, x1 = 70, W - 40
    p.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2.4))
    # маркери-роки на спільній осі
    marks = [
        (0.02, "≈1985", "Криза тесту", "BGA й багатошарові плати\nховають контакти від щупа", -1),
        (0.30, "1985", "Група JTAG", "Philips · TI · IBM · HP · BT\nзводять підхід докупи", +1),
        (0.66, "1990", "IEEE 1149.1", "«Standard Test Access Port\nand Boundary-Scan Architecture»", -1),
        (0.86, "1994", "BSDL", "мова-опис вузла (на базі VHDL)\nдодана як 1149.1b", +1),
    ]
    for f, yr, head, body, side in marks:
        x = x0 + (x1 - x0) * f
        p.append(circle(x, ax_y, 7, fill=FIELD, stroke=INK, sw=2))
        p.append(text(x, ax_y + (26 if side < 0 else -14), yr, size=15, bold=True))
        by = ax_y + side * 66
        box, bw, bh = textbox(x, by, head, size=13, bold=True, fill="#e8f6ee",
                              stroke=FIELD, sw=1.6, min_w=110)
        p.append(box)
        # виносна лінія від осі до рамки
        edge = by + (bh / 2 if side < 0 else -bh / 2)
        p.append(line(x, ax_y + (7 if side < 0 else -7), x, edge, color=MUTED, sw=1.4, dash="3 3"))
        # пояснення дрібним під/над рамкою
        ey = by + (bh / 2 + 22 if side < 0 else -bh / 2 - 6)
        p.append(mtext(x, ey, body, size=10, color=MUTED))

    # спусковий гачок адопції — під віссю між 1990 і 1994
    xa = x0 + (x1 - x0) * 0.48
    p.append(text(xa, ax_y - 34, "1989: Intel 80486 виходить із JTAG на борту →",
                  size=11, color=POS, bold=True))
    p.append(line(xa - 150, ax_y - 28, xa + 150, ax_y - 28, color=POS, sw=1.2, dash="2 3"))

    render(os.path.join(IMG, "jtag-timeline.svg"), W, H, *p,
           title="Як народжувався JTAG")


if __name__ == "__main__":
    fig_boundary_cells()
    fig_daisy_chain()
    fig_probe_access()
    fig_timeline()
    print("OK: boundary-cells.svg, daisy-chain.svg, probe-access.svg, jtag-timeline.svg")
