# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_three_interfaces():
    """Три способи довезти пікселі з камери в МК: DVP, MIPI-CSI, SPI+буфер."""
    W, H = 960, 560
    parts = [text(W / 2, 30, "Три способи довезти пікселі з камери в мікроконтролер", size=18, bold=True)]

    col_w = 300
    x0 = 20
    gap = 5
    xs = [x0, x0 + col_w + gap, x0 + 2 * (col_w + gap)]
    top = 70
    sensor_h = 44
    mcu_y = 470
    mcu_h = 54

    titles = ["DVP — паралельна", "MIPI-CSI — послідовна диференційна", "SPI + буфер"]
    tcol = [NEG, FIELD, "#c96a1b"]

    for i, x in enumerate(xs):
        # рамка колонки
        parts.append(rect(x, top - 34, col_w, 470, fill="#fbfcfe", stroke="#e3e8ef", sw=1.2, rx=10))
        parts.append(fitbox(x + 12, top - 28, col_w - 24, 30, titles[i], size=13, bold=True,
                            fill="none", stroke="none", color=tcol[i]))
        # сенсор згори
        parts.append(fitbox(x + col_w / 2 - 90, top + 12, 180, sensor_h, "матриця (сенсор)",
                            size=12, bold=True, fill="#eef2f9", stroke=MUTED, sw=1.4))
        # МК знизу
        parts.append(fitbox(x + col_w / 2 - 90, mcu_y, 180, mcu_h, "мікроконтролер",
                            size=12, bold=True, fill="#eef2f9", stroke=MUTED, sw=1.4))

    # вертикальний дріт, що РОЗІРВАНИЙ навколо смуги нижнього напису [gap_top..gap_bot]
    # (щоб пунктир не різав текст-присуд): малюємо два сегменти обабіч смуги.
    def vwire(lx, y1, y2, color, sw, gap=None):
        if gap and gap[0] > y1 and gap[1] < y2:
            parts.append(line(lx, y1, lx, gap[0], color=color, sw=sw))
            parts.append(line(lx, gap[1], lx, y2, color=color, sw=sw))
        else:
            parts.append(line(lx, y1, lx, y2, color=color, sw=sw))

    # ── DVP: багато паралельних ліній + окремий I2C ──
    x = xs[0]
    cxc = x + col_w / 2
    sy = top + 12 + sensor_h
    my = mcu_y
    dvp_gap = (my - 132 - 4, my - 132 + 46 + 4)   # смуга нижнього напису DVP
    # 8 ліній даних як джгут
    bus_left = cxc - 78
    for k in range(8):
        lx = bus_left + k * 20
        vwire(lx, sy, my, "#9aa5b5", 2, gap=dvp_gap)
    parts.append(text(cxc, (sy + my) / 2 - 40, "D0..D7", size=12, bold=True, color=NEG))
    parts.append(text(cxc, (sy + my) / 2 - 22, "(8 дротів даних)", size=10.5, color=MUTED))
    # керуючі: PCLK VSYNC HREF праворуч
    ctrl_x = x + col_w - 46
    for k, nm in enumerate(["PCLK", "VSYNC", "HREF"]):
        ly = sy + 30 + k * 22
        parts.append(text(ctrl_x, ly, nm, size=10.5, color="#c0392b", anchor="middle"))
    parts.append(line(ctrl_x, sy + 96, ctrl_x, my, color="#c0392b", sw=1.6))
    parts.append(line(ctrl_x, sy, ctrl_x, sy + 20, color="#c0392b", sw=1.6))
    # XCLK ліворуч (МК → сенсор)
    xcl_x = x + 40
    parts.append(arrow(xcl_x, my, xcl_x, sy, color=INK, sw=1.6))
    parts.append(text(xcl_x + 4, (sy + my) / 2, "XCLK", size=10.5, color=INK, anchor="start"))
    parts.append(fitbox(x + 14, my - 132, col_w - 28, 46,
                        "МК ловить кожен піксель\nна льоту → потрібен DMA",
                        size=11.5, fill="#eaf0fd", stroke=NEG, sw=1.4))

    # ── MIPI-CSI: 1-2 диференційні пари + PHY ──
    x = xs[1]
    cxc = x + col_w / 2
    sy = top + 12 + sensor_h
    my = mcu_y
    mipi_gap = (my - 132 - 4, my - 132 + 46 + 4)   # смуга нижнього напису MIPI
    # PHY-блок біля МК
    parts.append(fitbox(cxc - 70, my - 74, 140, 40, "MIPI-приймач (PHY)", size=10.5,
                        fill="#e8f7ee", stroke=FIELD, sw=1.4))
    # дві диференційні пари (data + clock) — розірвані навколо смуги напису
    def dpair(px, label, col):
        vwire(px, sy, my - 74, col, 2, gap=mipi_gap)
        vwire(px + 7, sy, my - 74, col, 2, gap=mipi_gap)
        parts.append(text(px + 3.5, sy - 6, label, size=10, color=col, anchor="middle"))
    dpair(cxc - 44, "D+/−", FIELD)
    dpair(cxc + 40, "CLK±", "#1f8f4e")
    parts.append(text(cxc, (sy + my) / 2 - 6, "серіалізований", size=11, bold=True, color=FIELD))
    parts.append(text(cxc, (sy + my) / 2 + 12, "потік бітів", size=11, bold=True, color=FIELD))
    parts.append(fitbox(x + 14, my - 132, col_w - 28, 46,
                        "мало дротів, дуже швидко —\nале треба апаратний PHY на МК",
                        size=11.5, fill="#e8f7ee", stroke=FIELD, sw=1.4))

    # ── SPI + буфер: буферна мікросхема між сенсором і МК ──
    x = xs[2]
    cxc = x + col_w / 2
    sy = top + 12 + sensor_h
    my = mcu_y
    buf_y = sy + 40
    parts.append(fitbox(cxc - 78, buf_y, 156, 52, "буфер-контролер\n(FIFO-кадр)", size=11, bold=True,
                        fill="#fff3e6", stroke="#c96a1b", sw=1.6))
    # сенсор → буфер: короткий паралельний джгут (сховано в модулі)
    for k in range(5):
        lx = cxc - 40 + k * 20
        parts.append(line(lx, sy, lx, buf_y, color="#c9b18f", sw=1.8))
    parts.append(mtext(cxc + 96, (sy + buf_y) / 2 - 4, ["DVP", "(усередині)"],
                       size=9.5, color=MUTED, anchor="middle"))
    spi_gap = (my - 120 - 4, my - 120 + 46 + 4)   # смуга нижнього напису SPI
    # буфер → МК: 4 лінії SPI — розірвані навколо смуги напису
    for k, nm in enumerate(["SCLK", "MOSI", "MISO", "CS"]):
        lx = cxc - 30 + k * 20
        vwire(lx, buf_y + 52, my, "#c96a1b", 2, gap=spi_gap)
    # підпис ПРАВОРУЧ від джгута SPI (дроти на 750..810), щоб дроти не різали напис
    parts.append(text(cxc + 42, buf_y + 82, "SPI: 4 дроти", size=11, bold=True,
                      color="#c96a1b", anchor="start"))
    parts.append(fitbox(x + 14, my - 120, col_w - 28, 46,
                        "МК не поспішає: кадр чекає\nв буфері, читаєш коли зручно",
                        size=11.5, fill="#fff3e6", stroke="#c96a1b", sw=1.4))

    render(os.path.join(OUT, "three-interfaces.svg"), W, H, *parts)


def fig_dvp_timing():
    """Часова діаграма DVP: чому це «пожежний шланг» пікселів."""
    W, H = 940, 470
    parts = [text(W / 2, 28, "DVP зблизька: сигнали, що біжать разом із пікселями", size=18, bold=True)]

    x0 = 150
    xe = 900
    lane_h = 46
    y = 70
    labels = ["VSYNC", "HREF", "PCLK", "D[7:0]"]
    for i, lab in enumerate(labels):
        yy = y + i * (lane_h + 14)
        parts.append(text(x0 - 12, yy + lane_h / 2 + 4, lab, size=12.5, bold=True, anchor="end",
                          color="#c0392b" if lab != "D[7:0]" else NEG))
        parts.append(line(x0, yy + lane_h, xe, yy + lane_h, color="#dfe4ea", sw=1))

    def hi(v):
        return v

    # VSYNC: низький під час кадру (активний), сплеск між кадрами
    yy = y
    base = yy + lane_h
    topl = yy + 6
    seg = [(x0, base), (x0 + 30, base), (x0 + 30, topl), (x0 + 70, topl),
           (x0 + 70, base), (xe - 40, base), (xe - 40, topl), (xe, topl)]
    parts.append(_poly(seg, "#c0392b"))
    parts.append(text((x0 + 70 + xe - 40) / 2, base + 0, "", size=10))
    parts.append(text((x0 + 70 + xe - 40) / 2, yy + lane_h - 8, "кадр активний (VSYNC низький)",
                      size=10.5, color=MUTED))

    # HREF: пачки рядків
    yy = y + (lane_h + 14)
    base = yy + lane_h
    topl = yy + 6
    pts = [(x0, base)]
    rx = x0 + 90
    for r in range(6):
        pts += [(rx, base), (rx, topl), (rx + 70, topl), (rx + 70, base)]
        rx += 110
    pts += [(xe, base)]
    parts.append(_poly(pts, "#c0392b"))
    parts.append(text(x0 + 125, topl - 6, "рядок", size=10, color=MUTED, anchor="middle"))
    parts.append(text(x0 + 235, base + 12, "проміжок між рядками", size=10, color=MUTED, anchor="middle"))

    # PCLK: щільні імпульси (лише під активним рядком показати густо)
    yy = y + 2 * (lane_h + 14)
    base = yy + lane_h
    topl = yy + 8
    pts = [(x0, base)]
    px = x0 + 90
    for c in range(30):
        pts += [(px, base), (px, topl), (px + 8, topl), (px + 8, base)]
        px += 16
    pts += [(xe, base)]
    parts.append(_poly(pts, "#c0392b"))
    parts.append(text((x0 + xe) / 2, topl - 4, "кожен фронт PCLK = новий піксель на D[7:0]",
                      size=10.5, color=MUTED, anchor="middle"))

    # D[7:0]: байти, що змінюються щотакту
    yy = y + 3 * (lane_h + 14)
    base = yy + lane_h
    mid = yy + lane_h / 2
    parts.append(line(x0, mid, xe, mid, color=NEG, sw=1.2, dash="2,3"))
    bx = x0 + 90
    vals = ["B1", "B2", "B3", "B4", "B5", "…"]
    for k in range(6):
        parts.append(rect(bx, yy + 8, 100, lane_h - 16, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
        parts.append(text(bx + 50, mid + 4, vals[k], size=11, bold=True, color=NEG))
        bx += 108

    parts.append(fitbox(180, 420, 580, 40,
                        "PCLK біжить мільйони разів на секунду — МК фізично не встигне читати ногами;"
                        " байти забирає DMA",
                        size=11.5, fill="#eaf0fd", stroke=NEG, sw=1.5))
    render(os.path.join(OUT, "dvp-timing.svg"), W, H, *parts)


def _poly(pts, color, sw=2.2):
    d = "M " + " L ".join("%.1f %.1f" % (x, yv) for x, yv in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


def fig_decision_map():
    """Який інтерфейс обрати: за ногами, швидкістю, залізом МК."""
    W, H = 940, 430
    parts = [text(W / 2, 28, "Який інтерфейс обрати під свій мікроконтролер", size=18, bold=True)]

    cols = ["", "DVP", "MIPI-CSI", "SPI + буфер"]
    rows = [
        ("Дротів до МК", "~11–16", "3–7", "4"),
        ("Швидкість", "середня", "дуже висока", "низька"),
        ("Що треба від МК", "DMA-захоплення\n(DCMI / I2S)", "апаратний\nMIPI-приймач", "звичайний\nSPI"),
        ("Тягне дешевий МК", "лише з DMA", "майже ніколи", "так, будь-який"),
        ("Типове застосування", "ESP32-CAM,\nSTM32 + OV2640", "SoC, Raspberry Pi,\nтелефони", "Arduino,\nдрібні МК"),
    ]
    colcol = [INK, NEG, FIELD, "#c96a1b"]

    x0 = 40
    y0 = 62
    wlab = 210
    wc = (W - 2 * x0 - wlab) / 3
    rh = 60

    # заголовок
    for j, c in enumerate(cols):
        if j == 0:
            continue
        cx = x0 + wlab + (j - 1) * wc
        parts.append(fitbox(cx + 3, y0, wc - 6, 34, c, size=13, bold=True,
                            fill="#f2f5fa", stroke=colcol[j], sw=1.6, color=colcol[j]))
    # рядки
    for i, r in enumerate(rows):
        ry = y0 + 40 + i * rh
        parts.append(fitbox(x0, ry, wlab - 6, rh - 6, r[0], size=11.5, bold=True,
                            fill="#f7f9fc", stroke="#e3e8ef", sw=1.2))
        for j in range(3):
            cx = x0 + wlab + j * wc
            parts.append(fitbox(cx + 3, ry, wc - 6, rh - 6, r[j + 1], size=11,
                                fill=BG, stroke="#e3e8ef", sw=1.2, color=colcol[j + 1]))

    render(os.path.join(OUT, "decision-map.svg"), W, H, *parts)


def fig_arducam_before_after():
    """Три покоління спроб дати Arduino камеру: голий DVP → FIFO-модуль → ArduChip за SPI."""
    W, H = 980, 470
    parts = [text(W / 2, 28, "Три спроби дати простому Arduino камеру", size=18, bold=True)]

    col_w = 300
    x0 = 25
    gap = 12
    xs = [x0, x0 + col_w + gap, x0 + 2 * (col_w + gap)]
    top = 74
    body_h = 340

    heads = [
        ("голий DVP (до ~2012)", POS),
        ("сенсор + FIFO-мікросхема", "#c96a1b"),
        ("ArduChip за SPI (2012)", FIELD),
    ]
    verdicts = [
        ("захлинається:\nкадр не встигнути", "#fdecea", POS),
        ("буфер тримає кадр —\nале назовні досі\nпаралель + біт-бенґ", "#fff3e6", "#c96a1b"),
        ("одна мікросхема ловить\nкадр, віддає по 4 SPI —\nзаводиться будь-де", "#eafaf0", FIELD),
    ]

    for i, x in enumerate(xs):
        parts.append(rect(x, top - 34, col_w, body_h + 34, fill="#fbfcfe",
                          stroke="#e3e8ef", sw=1.2, rx=10))
        parts.append(fitbox(x + 10, top - 30, col_w - 20, 28, heads[i][0], size=12.5,
                            bold=True, fill="none", stroke="none", color=heads[i][1]))
        # сенсор згори кожної колонки
        parts.append(fitbox(x + col_w / 2 - 74, top + 10, 148, 38, "матриця OV7670",
                            size=11, bold=True, fill="#eef2f9", stroke=MUTED, sw=1.4))

    mcu_y = top + 232
    mcu_h = 46

    def mcu(x, label, col, fill):
        parts.append(fitbox(x + col_w / 2 - 82, mcu_y, 164, mcu_h, label, size=10.5,
                            bold=True, fill=fill, stroke=col, sw=1.5))

    # ── 1. голий DVP: багато ліній прямо в МК, який не тягне ──
    x = xs[0]
    cxc = x + col_w / 2
    sy = top + 48
    for k in range(8):
        lx = cxc - 70 + k * 20
        parts.append(line(lx, sy, lx, mcu_y, color="#c0392b", sw=1.8))
    parts.append(text(cxc, (sy + mcu_y) / 2, "8+ дротів DVP", size=11, bold=True, color=POS))
    parts.append(text(cxc, (sy + mcu_y) / 2 + 17, "на швидкості PCLK", size=10, color=MUTED))
    mcu(x, "Arduino Uno (ATmega328)", POS, "#fdecea")

    # ── 2. FIFO-модуль: сенсор→FIFO паралель, FIFO→МК теж паралель ──
    x = xs[1]
    cxc = x + col_w / 2
    sy = top + 48
    fifo_y = sy + 66
    parts.append(fitbox(cxc - 76, fifo_y, 152, 46, "FIFO AL422B\n(384 КБ)", size=10.5,
                        bold=True, fill="#fff3e6", stroke="#c96a1b", sw=1.5))
    for k in range(5):
        lx = cxc - 40 + k * 20
        parts.append(line(lx, sy, lx, fifo_y, color="#c9a06a", sw=1.7))
    for k in range(8):
        lx = cxc - 70 + k * 20
        parts.append(line(lx, fifo_y + 46, lx, mcu_y, color="#c96a1b", sw=1.7))
    # підпис ПРАВОРУЧ від джгута (джгут доходить до cxc+90), щоб дроти не різали напис
    parts.append(text(cxc + 78, (fifo_y + 46 + mcu_y) / 2, "досі", size=10.5,
                      bold=True, color="#c96a1b", anchor="start"))
    parts.append(text(cxc + 78, (fifo_y + 46 + mcu_y) / 2 + 15, "10+ ніжок", size=10.5,
                      bold=True, color="#c96a1b", anchor="start"))
    mcu(x, "Arduino (біт-бенґ ногами)", "#c96a1b", "#fff3e6")

    # ── 3. ArduChip: усе сховано, назовні 4 дроти SPI ──
    x = xs[2]
    cxc = x + col_w / 2
    sy = top + 48
    chip_y = sy + 60
    parts.append(fitbox(cxc - 84, chip_y, 168, 52, "ArduChip\n(CPLD EPM240)", size=10.5,
                        bold=True, fill="#eafaf0", stroke=FIELD, sw=1.7))
    for k in range(5):
        lx = cxc - 40 + k * 20
        parts.append(line(lx, sy, lx, chip_y, color="#7fbf9a", sw=1.6))
    parts.append(text(cxc + 104, (sy + chip_y) / 2, "DVP", size=9.5, color=MUTED))
    parts.append(text(cxc + 104, (sy + chip_y) / 2 + 13, "(сховано)", size=9, color=MUTED))
    for k, nm in enumerate(["SCLK", "MOSI", "MISO", "CS"]):
        lx = cxc - 30 + k * 20
        parts.append(line(lx, chip_y + 52, lx, mcu_y, color=FIELD, sw=2))
    # підпис ПРАВОРУЧ від 4 SPI-дротів (останній дріт на cxc+30), щоб не різало напис
    parts.append(text(cxc + 42, (chip_y + 52 + mcu_y) / 2 + 4, "4 дроти", size=11,
                      bold=True, color=FIELD, anchor="start"))
    parts.append(text(cxc + 42, (chip_y + 52 + mcu_y) / 2 + 20, "SPI", size=11,
                      bold=True, color=FIELD, anchor="start"))
    mcu(x, "будь-який МК, аж до Uno", FIELD, "#eafaf0")

    # присуд знизу
    for i, x in enumerate(xs):
        txt, fill, col = verdicts[i]
        parts.append(fitbox(x + 14, mcu_y + mcu_h + 12, col_w - 28, 56, txt,
                            size=10.5, fill=fill, stroke=col, sw=1.4, color=col))

    render(os.path.join(OUT, "arducam-before-after.svg"), W, H, *parts)


def fig_mipi_timeline():
    """Як індустрія телефонів домовлялася на спільному камерному інтерфейсі:
    OMAPI(2002) → засновники(2003) → 39 компаній(2004) → CSI-2 v1.0(2005)."""
    W, H = 980, 430
    parts = [text(W / 2, 30, "Змова про спільний камерний інтерфейс: чотири кроки", size=18, bold=True)]

    # Головна вісь часу
    axis_y = 150
    box_w = 214
    x_left, x_right = 130, W - 130
    parts.append(line(60, axis_y, W - 40, axis_y, color=MUTED, sw=2.5))
    parts.append(arrow(W - 42, axis_y, W - 20, axis_y, color=MUTED, sw=2.5))

    # Чотири віхи: (частка позиції, рік, заголовок, підпис під віссю, колір)
    miles = [
        (0.00, "кін. 2002", "OMAPI",       "ST + TI: перше зерно —\nодин інтерфейс до\nпроцесора застосунків", MUTED),
        (0.33, "лип. 2003", "MIPI Alliance","засновники: ST · TI ·\nARM · Nokia —\nвесь ланцюг за столом", NEG),
        (0.66, "лют. 2004", "39 компаній",  "+Intel, Motorola в раду;\nSamsung, Philips, Nvidia…\nконсенсус галузі", "#c96a1b"),
        (1.00, "лис. 2005", "CSI-2 v1.0",   "камерна шина народилась —\nбагатошарова, поверх\nфізичного D-PHY", FIELD),
    ]

    for frac, year, head, sub, col in miles:
        cx = x_left + frac * (x_right - x_left)
        parts.append(circle(cx, axis_y, 9, fill=col, stroke=BG, sw=2.5))
        parts.append(line(cx, axis_y - 9, cx, axis_y - 44, color=col, sw=1.6, dash="3 3"))
        # рік і заголовок над віссю
        parts.append(text(cx, axis_y - 66, year, size=12, color=MUTED))
        parts.append(text(cx, axis_y - 48, head, size=14, bold=True, color=col))
        # опис під віссю у рамці (тримаємо в межах полотна)
        bx = min(max(cx - box_w / 2, 8), W - box_w - 8)
        parts.append(fitbox(bx, axis_y + 24, box_w, 70, sub, size=10.5,
                            fill="#fbfcfe", stroke=col, sw=1.4, color=INK))

    # Нижній підпис-висновок
    parts.append(fitbox(x_left, H - 44, x_right - x_left, 30,
                        "рушій — не швидкість, а втома від фрагментації: спільна цегла однакового розміру вигідна всім",
                        size=12, bold=True, fill="#eef7f0", stroke=FIELD, color="#1f7a46"))

    render(os.path.join(OUT, "mipi-timeline.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_three_interfaces()
    fig_dvp_timing()
    fig_decision_map()
    fig_arducam_before_after()
    fig_mipi_timeline()
    print("done")
