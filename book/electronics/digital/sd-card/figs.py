# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── inside-sd: усередині картки — NAND-кристали + контролер, назовні прості сектори ──
# Ідея: корпус ховає капризну NAND за контролером; зовні — рівний масив секторів.

def fig_inside_sd():
    W, H = 760, 420
    p = []
    p.append(text(W / 2, 30, "Усередині SD-картки: NAND + контролер", size=17, bold=True))

    # корпус картки
    cx0, cy0, cw, ch = 60, 60, 430, 320
    p.append(rect(cx0, cy0, cw, ch, fill="#fbfbfd", stroke=LINE, sw=2, rx=14))
    p.append(text(cx0 + 14, cy0 + 26, "корпус картки", size=12, color=MUTED, anchor="start", italic=True))

    # NAND-кристали (гори комірок)
    nx, ny = cx0 + 30, cy0 + 56
    for i in range(3):
        bx = nx + i * 18
        by = ny + i * 14
        p.append(rect(bx, by, 150, 120, fill="#eef4ff", stroke="#c9d6f0", sw=1.4, rx=6))
    p.append(text(nx + 95, ny + 150, "NAND-кристали", size=13, bold=True, color=NEG))
    p.append(text(nx + 95, ny + 172, "(дефекти, сторінки,", size=11, color=MUTED))
    p.append(text(nx + 95, ny + 188, "знос)", size=11, color=MUTED))

    # контролер
    kx, ky, kw, kh = cx0 + 250, cy0 + 70, 150, 200
    p.append(rect(kx, ky, kw, kh, fill="#eafaf0", stroke=FIELD, sw=2, rx=8))
    p.append(text(kx + kw / 2, ky + 26, "контролер", size=13, bold=True, color=FIELD))
    for i, ln in enumerate(["ECC", "ховає дефекти", "відображає", "сектори→сторінки", "рознос зносу"]):
        p.append(text(kx + kw / 2, ky + 54 + i * 26, ln, size=11, color=INK))

    # стрілка NAND ↔ контролер
    p.append(arrow(nx + 168, ny + 60, kx - 4, ky + 90, color=LINE, sw=1.6))

    # назовні — прості сектори
    sx, sy = 540, 110
    p.append(text(sx + 90, sy - 18, "назовні: блокова пам'ять", size=13, bold=True))
    for i in range(6):
        by = sy + i * 34
        p.append(rect(sx, by, 180, 28, fill=FILL, stroke=LINE, sw=1.2, rx=4))
        p.append(text(sx + 90, by + 19, "сектор %d  ·  512 Б" % i, size=11, color=INK))
    # стрілка контролер → сектори
    p.append(arrow(kx + kw + 4, ky + 100, sx - 6, sy + 70, color=LINE, sw=1.8))
    p.append(text((kx + kw + sx) / 2, ky + 84, "«читай/пиши", size=10, color=MUTED))
    p.append(text((kx + kw + sx) / 2, ky + 98, "сектор N»", size=10, color=MUTED))

    render(os.path.join(OUT, "inside-sd.svg"), W, H, *p)


# ── two-modes: SPI (одна лінія в бік) проти нативного SD (4 лінії даних) ──
# Ідея: один чіп, два протоколи — простота всюди проти швидкості з апаратним хостом.

def fig_two_modes():
    W, H = 760, 380
    p = []
    p.append(text(W / 2, 30, "Два способи говорити з карткою", size=17, bold=True))

    def card(cx, cy):
        p.append(rect(cx, cy, 120, 96, fill="#fbfbfd", stroke=LINE, sw=1.8, rx=10))
        p.append(text(cx + 60, cy + 54, "SD", size=20, bold=True, color=INK))

    def host(cx, cy, label):
        p.append(rect(cx, cy, 150, 96, fill=FILL, stroke=LINE, sw=1.6, rx=8))
        p.append(mtext(cx + 75, cy + 44, label, size=12, bold=True))

    # ── SPI зверху ──
    hy = 70
    host(70, hy, "будь-який МК")
    card(560, hy)
    p.append(text(W / 2, hy - 8, "SPI-режим", size=14, bold=True, color=NEG))
    spi = [("такт", "#888"), ("дані → картці", NEG), ("дані ← картки", NEG), ("вибір", "#888")]
    for i, (lab, col) in enumerate(spi):
        yy = hy + 18 + i * 18
        p.append(line(220, yy, 560, yy, color=col, sw=1.6))
        p.append(text(390, yy - 4, lab, size=10, color=col))
    p.append(text(W / 2, hy + 116, "по одній лінії даних у бік · одиниці МБ/с · має кожен чіп",
                  size=11, color=MUTED))

    # ── нативний SD знизу ──
    hy2 = 240
    host(70, hy2, "МК з SD-host\nконтролером")
    card(560, hy2)
    p.append(text(W / 2, hy2 - 8, "нативний SD-режим", size=14, bold=True, color=POS))
    p.append(line(220, hy2 + 16, 560, hy2 + 16, color="#888", sw=1.6))
    p.append(text(390, hy2 + 12, "командна", size=10, color="#888"))
    for i in range(4):
        yy = hy2 + 34 + i * 14
        p.append(line(220, yy, 560, yy, color=POS, sw=1.8))
    p.append(text(390, hy2 + 34 + 4 * 14 + 4, "4 лінії даних паралельно", size=10, color=POS))
    p.append(text(W / 2, hy2 + 116, "десятки-сотні МБ/с · потрібен апаратний хост",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "two-modes.svg"), W, H, *p)


# ── speed-classes: клас = гарантований мінімум запису проти потреб застосувань ──
# Ідея: стовпчики класів і горизонтальні пороги потреб (Full HD, 4K, 8K).

def fig_speed_classes():
    W, H = 760, 420
    p = []
    p.append(text(W / 2, 30, "Клас швидкості — гарантований мінімум запису", size=17, bold=True))

    ox, oy = 90, 350          # початок осей
    aw, ah = 600, 280
    p.append(line(ox, oy, ox, oy - ah - 10, color=INK, sw=1.6))
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox - 52, oy - ah, "МБ/с", size=11, color=INK, anchor="start"))

    vmax = 95.0
    def yv(v):
        return oy - (v / vmax) * ah

    # сітка по 30
    for v in (30, 60, 90):
        p.append(line(ox, yv(v), ox + aw, yv(v), color="#e5e7eb", sw=1.0))
        p.append(text(ox - 8, yv(v) + 4, str(v), size=10, color=MUTED, anchor="end"))

    # стовпчики класів (гарантований мінімум)
    classes = [("Class 10\nU1", 10), ("U3\nV30", 30), ("V60", 60), ("V90", 90)]
    bw = 70
    gap = (aw - len(classes) * bw) / (len(classes) + 1)
    for i, (lab, v) in enumerate(classes):
        bx = ox + gap + i * (bw + gap)
        p.append(rect(bx, yv(v), bw, oy - yv(v), fill="#eef4ff", stroke=NEG, sw=1.4, rx=4))
        p.append(text(bx + bw / 2, yv(v) - 8, "≥%d" % v, size=11, bold=True, color=NEG))
        p.append(mtext(bx + bw / 2, oy + 20, lab, size=10, color=INK))

    # горизонтальні пороги потреб
    needs = [("Full HD ≈ 6", 6, FIELD), ("4K ≈ 30", 30, POS), ("4K 60к/с, 8K ≈ 60-90", 75, POS)]
    for lab, v, col in needs:
        p.append(line(ox, yv(v), ox + aw, yv(v), color=col, sw=1.5, dash="6 4"))
        p.append(text(ox + aw + 4, yv(v) + 4, lab, size=10, color=col, anchor="start"))

    render(os.path.join(OUT, "speed-classes.svg"), W, H, *p)


# ════════════ фігури вставки hist-sd-card-wars ════════════

# ── timeline: десять років змагання форматів карток ──
# Ідея: вертикальна шкала років з подіями кожного «табору» війни.

def fig_timeline():
    W, H = 820, 660
    p = []
    p.append(text(W / 2, 30, "Десять років війни форматів карток пам'яті", size=17, bold=True))

    ax = 140
    ytop, ybot = 70, 600
    p.append(line(ax, ytop, ax, ybot, color=INK, sw=2))

    events = [
        (1994, "CompactFlash (SanDisk):\nвелика, міцна, з контролером", NEG),
        (1995, "SmartMedia (Toshiba):\nгола NAND, без контролера", POS),
        (1997, "MMC (SanDisk·Siemens·Nokia):\nкрихітна, для телефонів", FIELD),
        (1998, "Memory Stick (Sony):\nзакритий фірмовий формат", "#8e44ad"),
        (1999, "SD (SanDisk·Panasonic·Toshiba):\nвідкритий стандарт, SD Association", INK),
        (2003, "SD виходить уперед\nза часткою ринку", INK),
        (2005, "microSD вростає\nу смартфони — кінець війни", INK),
    ]
    n = len(events)
    for i, (yr, lab, col) in enumerate(events):
        yy = ytop + 20 + i * ((ybot - ytop - 40) / (n - 1))
        p.append(circle(ax, yy, 7, fill=col, stroke=col, sw=1.5))
        p.append(text(ax - 18, yy + 5, str(yr), size=13, bold=True, color=col, anchor="end"))
        p.append(mtext(ax + 22, yy - 2, lab, size=12, color=INK, anchor="start"))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p)


# ── controller: гола NAND проти «NAND + контролер» ──
# Ідея: поділ, що визначив війну — хто робить брудну роботу з NAND.

def fig_controller():
    W, H = 820, 470
    p = []
    p.append(text(W / 2, 30, "Гола NAND проти «NAND + контролер»", size=17, bold=True))

    # ── ліворуч: гола NAND (SmartMedia, xD) ──
    lx = 60
    p.append(text(lx + 150, 64, "гола NAND  (SmartMedia, xD)", size=13, bold=True, color=POS))
    p.append(rect(lx + 70, 80, 160, 70, fill="#eef4ff", stroke="#c9d6f0", sw=1.4, rx=6))
    p.append(text(lx + 150, 120, "лише чип NAND", size=12, color=NEG))
    # пристрій мусить усе сам
    p.append(rect(lx, 200, 300, 180, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    p.append(text(lx + 150, 224, "пристрій робить усе сам:", size=12, bold=True, color=POS))
    for i, ln in enumerate(["облік зносу", "обхід битих комірок", "корекція помилок (ECC)",
                            "знати точну будову чипа", "новий NAND → стара камера", "вже не розуміє"]):
        p.append(text(lx + 150, 250 + i * 21, ln, size=11, color=INK))
    p.append(arrow(lx + 150, 154, lx + 150, 196, color=POS, sw=1.6))

    # ── праворуч: NAND + контролер (CF, SD) ──
    rx = 460
    p.append(text(rx + 150, 64, "NAND + контролер  (CF, SD)", size=13, bold=True, color=FIELD))
    p.append(rect(rx + 70, 80, 160, 60, fill="#eef4ff", stroke="#c9d6f0", sw=1.4, rx=6))
    p.append(text(rx + 150, 116, "чип NAND", size=12, color=NEG))
    p.append(rect(rx + 50, 162, 200, 60, fill="#eafaf0", stroke=FIELD, sw=2, rx=8))
    p.append(text(rx + 150, 188, "контролер бере", size=12, bold=True, color=FIELD))
    p.append(text(rx + 150, 206, "всю роботу на себе", size=11, color=INK))
    p.append(arrow(rx + 150, 144, rx + 150, 158, color=LINE, sw=1.6))
    # назовні простий диск
    p.append(rect(rx + 50, 270, 200, 90, fill=FILL, stroke=LINE, sw=1.6, rx=8))
    p.append(text(rx + 150, 296, "назовні: простий", size=12, bold=True))
    p.append(text(rx + 150, 316, "«диск» із секторами;", size=11, color=INK))
    p.append(text(rx + 150, 334, "новий чип картка", size=11, color=INK))
    p.append(text(rx + 150, 350, "ховає сама", size=11, color=INK))
    p.append(arrow(rx + 150, 226, rx + 150, 266, color=FIELD, sw=1.6))

    p.append(text(W / 2, 408, "Контролер коштує копійки — а робить картку самодостатньою й сумісною наперед.",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "controller.svg"), W, H, *p)


# ── why-sd: підсумкова матриця — жоден не виграв за всіма осями ──
# Ідея: рядки = формати, стовпці = осі ринку; SD «досить добра в кожній».

def fig_why_sd():
    W, H = 840, 440
    p = []
    p.append(text(W / 2, 30, "Чому перемогла саме SD: найкращий компроміс", size=17, bold=True))

    cols = ["малий\nрозмір", "контролер\nу картці", "захист\nзапису", "відкритий\nстандарт"]
    rows = [
        ("CompactFlash", ["−", "+", "−", "±"]),
        ("SmartMedia",   ["+", "−", "−", "±"]),
        ("Memory Stick", ["+", "+", "+", "−"]),
        ("SD",           ["+", "+", "+", "±"]),
    ]
    x0, y0 = 60, 90
    name_w = 170
    cw = 140
    rh = 64
    # шапка стовпців
    for j, c in enumerate(cols):
        cxx = x0 + name_w + j * cw + cw / 2
        p.append(mtext(cxx, y0 - 8, c, size=12, bold=True, color=MUTED))
    # рядки
    for i, (name, cells) in enumerate(rows):
        yy = y0 + i * rh
        hot = (name == "SD")
        p.append(rect(x0, yy, name_w, rh - 8,
                      fill="#eafaf0" if hot else FILL, stroke=FIELD if hot else LINE,
                      sw=2 if hot else 1.4, rx=6))
        p.append(text(x0 + name_w / 2, yy + (rh - 8) / 2 + 5, name, size=13,
                      bold=hot, color=FIELD if hot else INK))
        for j, v in enumerate(cells):
            cxx = x0 + name_w + j * cw + cw / 2
            cyy = yy + (rh - 8) / 2
            if v == "+":
                p.append(plus(cxx, cyy, r=12))
            elif v == "−":
                p.append(minus(cxx, cyy, r=12))
            else:  # ±
                p.append(circle(cxx, cyy, 12, fill="#fff7e6", stroke="#d39e00", sw=2))
                p.append(text(cxx, cyy + 5, "±", size=15, bold=True, color="#d39e00"))

    p.append(text(W / 2, y0 + len(rows) * rh + 24,
                  "Жоден формат не виграв за всіма осями. SD — досить добра в кожній.",
                  size=12, color=MUTED))
    p.append(text(W / 2, y0 + len(rows) * rh + 44,
                  "± = відкритість «частково»: ліцензія платна, та доступна всім.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "why-sd.svg"), W, H, *p)


if __name__ == "__main__":
    fig_inside_sd()
    fig_two_modes()
    fig_speed_classes()
    fig_timeline()
    fig_controller()
    fig_why_sd()
    print("figs: OK")
