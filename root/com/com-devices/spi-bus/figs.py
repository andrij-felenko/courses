# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUEFILL = "#dfe7fb"   # «1»-комірка регістра


def bitcells(x, y, bits, cell=26, h=30):
    """Рядок бітових комірок: «1» синім, «0» сірим. Повертає (фрагмент, права межа)."""
    out = []
    for i, b in enumerate(bits):
        bx = x + i * cell
        if b:
            out.append(rect(bx, y, cell, h, fill=BLUEFILL, stroke=NEG, sw=1.4, rx=0))
            out.append(text(bx + cell / 2, y + h / 2 + 4.5, "1", size=13, color=NEG, bold=True))
        else:
            out.append(rect(bx, y, cell, h, fill=BG, stroke=MUTED, sw=1.4, rx=0))
            out.append(text(bx + cell / 2, y + h / 2 + 4.5, "0", size=13, color=MUTED, bold=True))
    return "".join(out), x + len(bits) * cell


# ── lines: чотири лінії й ролі (ведучий ↔ ведений) ────────────────────────────
# Ідея: дві коробки (ведучий/ведений) і чотири іменовані лінії між ними; колір
# показує напрям (MOSI «туди», MISO «звідти», SCK/CS — від ведучого).

def fig_lines():
    W, H = 700, 320
    p = []
    mx, my, bw, bh = 70, 96, 150, 150
    sx = W - 70 - bw
    p.append(rect(mx, my, bw, bh, fill="#eef6ef", stroke=FIELD, sw=2))
    p.append(text(mx + bw / 2, my + 26, "ВЕДУЧИЙ", size=14, color=FIELD, bold=True))
    p.append(text(mx + bw / 2, my + 44, "(master)", size=11, color=MUTED, italic=True))
    p.append(rect(sx, my, bw, bh, fill=FILL, stroke=INK, sw=2))
    p.append(text(sx + bw / 2, my + 26, "ВЕДЕНИЙ", size=14, color=INK, bold=True))
    p.append(text(sx + bw / 2, my + 44, "(slave)", size=11, color=MUTED, italic=True))

    lines = [
        ("SCK",  "такт",              my + 78,  INK,   1),
        ("MOSI", "дані туди",         my + 104, POS,   1),
        ("MISO", "дані звідти",       my + 130, FIELD, -1),
        ("CS",   "вибір (0 = обрано)", my + 154, NEG,  1),
    ]
    for name, role, ly, col, direction in lines:
        if direction > 0:
            p.append(arrow(mx + bw, ly, sx, ly, color=col, sw=2))
        else:
            p.append(arrow(sx, ly, mx + bw, ly, color=col, sw=2))
        p.append(text(W / 2, ly - 6, name, size=12, color=col, bold=True))
        p.append(text(W / 2, ly + 14, role, size=9.5, color=MUTED, italic=True))

    p.append(text(W / 2, H - 18,
                  "три лінії спільні для всіх ведених; CS — окрема на кожного",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "lines.svg"), W, H, *p,
           title="Чотири лінії SPI: хто з ким говорить")


# ── shift-ring: два зсувні регістри в кільці ──────────────────────────────────
# Ідея: регістр ведучого + регістр веденого зведені в одне кільце; MOSI несе біт
# з ведучого у веденого, MISO — назад; SCK зсуває обидва синхронно.

def fig_shift_ring():
    W, H = 700, 300
    p = []
    cell, h = 26, 32
    y = 120
    mbits = [1, 0, 1, 0, 0, 1, 0, 1]
    sbits = [0, 0, 1, 1, 1, 1, 0, 0]
    mx = 70
    mfrag, mr = bitcells(mx, y, mbits, cell, h)
    p.append(mfrag)
    p.append(text(mx + 4 * cell, y - 10, "регістр ВЕДУЧОГО", size=11, color=FIELD, bold=True))
    sx = mr + 70
    sfrag, sr = bitcells(sx, y, sbits, cell, h)
    p.append(sfrag)
    p.append(text(sx + 4 * cell, y - 10, "регістр ВЕДЕНОГО", size=11, color=INK, bold=True))

    # MOSI: правий край ведучого → лівий край веденого
    p.append(arrow(mr, y + h / 2, sx, y + h / 2, color=POS, sw=2.2))
    p.append(text((mr + sx) / 2, y - 6, "MOSI", size=11, color=POS, bold=True))

    # MISO: правий край веденого → петлею знизу → лівий край ведучого
    yb = y + h + 46
    p.append(line(sr, y + h / 2, sr + 16, y + h / 2, color=FIELD, sw=2.2))
    p.append(line(sr + 16, y + h / 2, sr + 16, yb, color=FIELD, sw=2.2))
    p.append(line(sr + 16, yb, mx - 16, yb, color=FIELD, sw=2.2))
    p.append(line(mx - 16, yb, mx - 16, y + h / 2, color=FIELD, sw=2.2))
    p.append(arrow(mx - 16, y + h / 2, mx, y + h / 2, color=FIELD, sw=2.2))
    p.append(text((mx + sr) / 2, yb + 16, "MISO (біт веденого повертається у ведучого)",
                  size=11, color=FIELD, bold=True))

    p.append(text(W / 2, H - 26,
                  "SCK цокає → обидва регістри зсуваються на один біт водночас",
                  size=12, color=NEG, bold=True))
    render(os.path.join(OUT, "shift-ring.svg"), W, H, *p,
           title="Серце SPI: одне кільце з двох зсувних регістрів")


# ── exchange: за 8 тактів байти міняються місцями ─────────────────────────────
# Ідея: до обміну у ведучого 0xA5, у веденого 0x3C; після 8 тактів регістри
# повністю прокрутилися — байти помінялися. Передав = прийняв за ту саму операцію.

def fig_exchange():
    W, H = 700, 320
    p = []
    cell, h = 24, 28
    A5 = [1, 0, 1, 0, 0, 1, 0, 1]   # 0xA5
    C3 = [0, 0, 1, 1, 1, 1, 0, 0]   # 0x3C
    mx, sx = 70, 380

    p.append(text(mx + 4 * cell, 86, "ДО обміну", size=12, color=INK, bold=True))
    f1, _ = bitcells(mx, 100, A5, cell, h); p.append(f1)
    p.append(text(mx + 4 * cell, 148, "ведучий = 0xA5", size=11, color=FIELD, bold=True))
    f2, _ = bitcells(sx, 100, C3, cell, h); p.append(f2)
    p.append(text(sx + 4 * cell, 148, "ведений = 0x3C", size=11, color=INK, bold=True))

    p.append(arrow(W / 2 - 50, 188, W / 2 + 50, 188, color=NEG, sw=2.6))
    p.append(text(W / 2, 180, "8 тактів SCK", size=12, color=NEG, bold=True))

    p.append(text(mx + 4 * cell, 224, "ПІСЛЯ обміну", size=12, color=INK, bold=True))
    f3, _ = bitcells(mx, 238, C3, cell, h); p.append(f3)
    p.append(text(mx + 4 * cell, 286, "ведучий = 0x3C", size=11, color=FIELD, bold=True))
    f4, _ = bitcells(sx, 238, A5, cell, h); p.append(f4)
    p.append(text(sx + 4 * cell, 286, "ведений = 0xA5", size=11, color=INK, bold=True))

    p.append(text(W / 2, H - 14,
                  "за одну операцію ведучий і надіслав свій байт, і прийняв байт веденого",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "exchange.svg"), W, H, *p,
           title="Обмін байтом: після 8 тактів байти помінялися місцями")


# ── chip-select: вибір веденого лінією CS ─────────────────────────────────────
# Ідея: три ведені на спільних SCK/MOSI/MISO; ведучий опускає CS лише одного —
# той активний, решта бачать CS=1, мовчать і відпускають MISO у high-Z.

def fig_chip_select():
    W, H = 700, 330
    p = []
    mx, my, bw, bh = 60, 120, 130, 90
    p.append(rect(mx, my, bw, bh, fill="#eef6ef", stroke=FIELD, sw=2))
    p.append(text(mx + bw / 2, my + bh / 2 - 6, "ВЕДУЧИЙ", size=13, color=FIELD, bold=True))
    p.append(text(mx + bw / 2, my + bh / 2 + 12, "(master)", size=10, color=MUTED, italic=True))

    busx = mx + bw + 40
    # спільна шина SCK/MOSI/MISO — вертикаль
    p.append(line(busx, 90, busx, 290, color=MUTED, sw=2))
    p.append(text(busx, 78, "SCK · MOSI · MISO (спільні)", size=10, color=MUTED, anchor="middle", bold=True))
    p.append(arrow(mx + bw, my + bh / 2, busx, my + bh / 2, color=MUTED, sw=1.8))

    sx = busx + 60
    slaves = [
        (95,  "ведений A", True),
        (180, "ведений B", False),
        (265, "ведений C", False),
    ]
    for sy, lab, active in slaves:
        col = FIELD if active else MUTED
        fill = "#eef6ef" if active else BG
        p.append(rect(sx, sy - 22, 150, 44, fill=fill, stroke=col, sw=1.8))
        p.append(text(sx + 75, sy - 2, lab, size=12, color=col, bold=True))
        st = "CS = 0 → активний" if active else "CS = 1 → мовчить, MISO у Z"
        p.append(text(sx + 75, sy + 14, st, size=9, color=col))
        p.append(line(busx, sy, sx, sy, color=MUTED, sw=1.4))
        # окрема CS від ведучого до кожного
        cscol = NEG if active else MUTED
        p.append(line(mx + bw / 2, my + bh, mx + bw / 2, 300 - 0, color=BG, sw=0.1))  # no-op spacer
    # окремі лінії CS (намалюємо знизу, щоб показати «N ліній CS»)
    p.append(text(W / 2, H - 14, "на N ведених треба N окремих ліній CS — ціна простого вибору",
                  size=11, color=MUTED, italic=True))
    p.append(text(sx + 75, 300, "обрано лише A — говорить один", size=10, color=NEG, bold=True))
    render(os.path.join(OUT, "chip-select.svg"), W, H, *p,
           title="Без адрес: вибір веденого лінією CS")


# ── push-pull: двотактний вихід проти відкритого колектора ────────────────────
# Ідея: SPI активно жене лінію в обидва боки (різкі фронти, десятки МГц);
# I2C тягне вгору лише підтяжкою (повільний RC-підйом — стеля швидкості).

def fig_push_pull():
    W, H = 700, 300
    p = []
    midx = W / 2

    def edge_panel(cx, title, col, slow):
        out = []
        ax0, ax1 = cx - 110, cx + 110
        ay0, ay1 = 110, 220               # рівні 1 / 0
        out.append(text(cx, 86, title, size=12, color=col, bold=True))
        out.append(line(ax0 - 6, ay1, ax1 + 6, ay1, color=MUTED, sw=1.2))  # рівень 0
        out.append(line(ax0 - 6, ay0, ax1 + 6, ay0, color=MUTED, sw=1.2, dash="3 4"))  # рівень 1
        out.append(text(ax0 - 12, ay0 + 4, "1", size=10, color=MUTED, anchor="end"))
        out.append(text(ax0 - 12, ay1 + 4, "0", size=10, color=MUTED, anchor="end"))
        x0 = cx - 70
        if slow:
            # повільний RC-підйом: експонента
            pts = ["%.1f,%.1f" % (ax0, ay1)]
            import math
            for i in range(0, 81):
                t = i / 80.0
                yv = ay1 - (ay1 - ay0) * (1 - math.exp(-3.0 * t))
                pts.append("%.1f,%.1f" % (x0 + t * 120, yv))
            out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                       % (" ".join(pts), col))
            out.append(text(cx, 248, "пасивний RC-підйом — повільно", size=10, color=col))
        else:
            # різкий фронт
            out.append(line(ax0, ay1, x0, ay1, color=col, sw=2.6))
            out.append(line(x0, ay1, x0, ay0, color=col, sw=2.6))
            out.append(line(x0, ay0, ax1, ay0, color=col, sw=2.6))
            out.append(text(cx, 248, "активний фронт — різко", size=10, color=col))
        return out

    p += edge_panel(midx - 175, "SPI: двотактний (push-pull)", FIELD, slow=False)
    p += edge_panel(midx + 175, "I2C: відкритий колектор + підтяжка", POS, slow=True)
    p.append(line(midx, 100, midx, 240, color="#dddddd", sw=1.2, dash="4 4"))

    p.append(text(W / 2, H - 16,
                  "різкі фронти SPI → десятки МГц; повільний підйом I2C → стеля в сотні кГц",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "push-pull.svg"), W, H, *p,
           title="Чому SPI швидкий: активні фронти проти підтяжки")


# ── minimal: мінімум церемоній проти службових I2C ────────────────────────────
# Ідея: у I2C байт оточений S/адреса/ACK/P; у SPI — лише CS↓, байти, CS↑.
# Корисна частка близька до 100%, бо немає 9-го такту ACK і службових байтів.

def fig_minimal():
    W, H = 700, 300
    p = []
    bx, bw, h = 70, 560, 40

    # I2C рядок
    yi = 110
    p.append(text(bx, yi - 14, "I2C: корисний байт обвішаний службовими", size=11, color=POS, anchor="start", bold=True))
    i2c = [("S", 0.6, "#f3dede"), ("адреса", 1.6, "#f6efd6"), ("ACK", 0.6, "#f3dede"),
           ("ДАНІ", 2.0, "#dff0df"), ("ACK", 0.6, "#f3dede"), ("ДАНІ", 2.0, "#dff0df"),
           ("ACK", 0.6, "#f3dede"), ("P", 0.6, "#f3dede")]
    tot = sum(w for _, w, _ in i2c)
    x = bx
    for lab, w, fill in i2c:
        ww = bw * w / tot
        p.append(rect(x, yi, ww, h, fill=fill, stroke=INK, sw=1.2, rx=0))
        p.append(text(x + ww / 2, yi + h / 2 + 4, lab, size=9, color=INK, bold=(lab == "ДАНІ")))
        x += ww

    # SPI рядок
    ys = 210
    p.append(text(bx, ys - 14, "SPI: лише CS, тоді самі байти", size=11, color=FIELD, anchor="start", bold=True))
    spi = [("CS↓", 0.6, "#dfe7fb"), ("ДАНІ", 2.0, "#dff0df"), ("ДАНІ", 2.0, "#dff0df"),
           ("ДАНІ", 2.0, "#dff0df"), ("CS↑", 0.6, "#dfe7fb")]
    tot2 = sum(w for _, w, _ in spi)
    x = bx
    for lab, w, fill in spi:
        ww = bw * w / tot2
        p.append(rect(x, ys, ww, h, fill=fill, stroke=INK, sw=1.2, rx=0))
        p.append(text(x + ww / 2, ys + h / 2 + 4, lab, size=9, color=INK, bold=(lab == "ДАНІ")))
        x += ww

    p.append(text(W / 2, H - 16,
                  "ні адрес, ні ACK на кожен байт, ні старт-стопу → 8 тактів = 8 біт даних",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "minimal.svg"), W, H, *p,
           title="Мінімум церемоній: корисна частка близька до 100%")


# ── character: портрет SPI одним поглядом ─────────────────────────────────────
# Ідея: дві колонки — сильні сторони проти ціни; стислий «характер» шини.

def fig_character():
    W, H = 700, 320
    p = []
    colw = 290
    lx, rx = 40, W - 40 - colw

    p.append(rect(lx, 70, colw, 220, fill="#eef6ef", stroke=FIELD, sw=2))
    p.append(text(lx + colw / 2, 96, "Сильні сторони", size=13, color=FIELD, bold=True))
    pros = ["швидкість — десятки МГц", "повний дуплекс (туди й назад)",
            "простий протокол, мала затримка", "без адрес і підтяжок"]
    for i, s in enumerate(pros):
        p.append(text(lx + 18, 128 + i * 34, "+ " + s, size=11.5, color=INK, anchor="start"))

    p.append(rect(rx, 70, colw, 220, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(rx + colw / 2, 96, "Ціна", size=13, color=POS, bold=True))
    cons = ["більше дротів: 3 + CS на кожного", "немає вбудованого контролю помилок",
            "на короткі відстані (на платі)", "немає стандарту на формат пакета"]
    for i, s in enumerate(cons):
        p.append(text(rx + 18, 128 + i * 34, "− " + s, size=11.5, color=INK, anchor="start"))

    p.append(text(W / 2, H - 16,
                  "швидкість і близькість на платі — за рахунок дротів і відсутності перевірок",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "character.svg"), W, H, *p,
           title="Характер SPI одним поглядом")


# ── hist-timeline: походження SPI поряд із Microwire та I2C ────────────────────
# Ідея: три синхронні шини народилися майже водночас у трьох різних компаній;
# SPI — від Motorola (6805 → 68HC11), формалізована AN991 1987.

def fig_hist_timeline():
    W, H = 700, 300
    p = []
    ax0, ax1, ay = 70, W - 40, 150
    p.append(line(ax0, ay, ax1, ay, color=INK, sw=1.8))
    p.append(arrow(ax1 - 1, ay, ax1 + 1, ay, color=INK, sw=1.8))
    # шкала років
    years = [1980, 1983, 1987, 1990, 2002]
    span0, span1 = 1979.0, 2003.0
    def xof(y): return ax0 + (y - span0) / (span1 - span0) * (ax1 - 30 - ax0)
    for y in years:
        x = xof(y)
        p.append(line(x, ay - 5, x, ay + 5, color=MUTED, sw=1.4))
        p.append(text(x, ay + 20, str(y), size=10, color=MUTED))

    events = [
        (1983, -1, "Motorola: SPI у\nродині 6805", FIELD),
        (1987, 1, "AN991 — фактичний\nопис протоколу", NEG),
        (2002, -1, "остання редакція\nAN991 (вже NXP)", MUTED),
    ]
    for y, side, lab, col in events:
        x = xof(y)
        dy = -54 if side < 0 else 46
        p.append(line(x, ay, x, ay + dy, color=col, sw=1.4, dash="3 3"))
        b = fitbox(x - 75, ay + dy + (-34 if side < 0 else 0), 150, 34, lab,
                   size=10, fill=BG, stroke=col, sw=1.5, color=col, bold=True)
        p.append(b)

    p.append(text(W / 2, H - 26,
                  "паралельно: Microwire (National Semiconductor) — напівдуплексний предок;",
                  size=10.5, color=MUTED, italic=True))
    p.append(text(W / 2, H - 10,
                  "I2C (Philips, 1982) — інша відповідь на ту саму потребу зв'язати чіпи",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Звідки SPI: Motorola, початок 1980-х")


if __name__ == "__main__":
    fig_lines()
    fig_shift_ring()
    fig_exchange()
    fig_chip_select()
    fig_push_pull()
    fig_minimal()
    fig_character()
    fig_hist_timeline()
    print("OK: figures written to", OUT)
