# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MONO = "'Consolas', 'DejaVu Sans Mono', 'Courier New', monospace"


# ── допоміжне: цифровий рівень-меандр із заданих сегментів ────────────────────
def wave(x0, yhi, ylo, segs, color=INK, sw=2.2):
    """segs — список (ширина, рівень 0/1). Малює лінію рівнів зліва направо."""
    pts = []
    x = x0
    cur = None
    for w, lvl in segs:
        y = yhi if lvl else ylo
        if cur is None:
            pts.append((x, y))
        else:
            pts.append((x, cur))   # вертикальний перехід
            pts.append((x, y))
        pts.append((x + w, y))
        cur = y
        x += w
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (s, color, sw))


def bus_valid(x0, yhi, ylo, w_pre, w_val, w_post, color=INK, sw=2.2, label="", lab_col=None):
    """Шина: невизначено (тонка «X») → дійсне значення (розкрита «капсула») → невизначено."""
    ymid = (yhi + ylo) / 2
    out = []
    # ліва невизначеність
    out.append(line(x0, ymid, x0 + w_pre, ymid, color=MUTED, sw=1.3, dash="3 3"))
    xa = x0 + w_pre
    # перехрестя-відкриття
    out.append(line(xa, ymid, xa + 8, yhi, color=color, sw=sw))
    out.append(line(xa, ymid, xa + 8, ylo, color=color, sw=sw))
    xb = xa + w_val
    out.append(line(xa + 8, yhi, xb - 8, yhi, color=color, sw=sw))
    out.append(line(xa + 8, ylo, xb - 8, ylo, color=color, sw=sw))
    out.append(line(xb, ymid, xb - 8, yhi, color=color, sw=sw))
    out.append(line(xb, ymid, xb - 8, ylo, color=color, sw=sw))
    if label:
        out.append(text((xa + xb) / 2, ymid + 5, label, size=11.5,
                        color=lab_col or color, bold=True))
    # права невизначеність
    out.append(line(xb, ymid, xb + w_post, ymid, color=MUTED, sw=1.3, dash="3 3"))
    return "".join(out)


def chip(x, y, w, h, label, sub="", fill="#23262b"):
    out = rect(x, y, w, h, fill=fill, stroke="#0c0e10", sw=1.5, rx=5)
    out += text(x + w / 2, y + h / 2 - (6 if sub else -4), label, size=12, color="#e9e9e9", bold=True)
    if sub:
        out += text(x + w / 2, y + h / 2 + 13, sub, size=9.5, color="#a9adb3", italic=True)
    return out


# ════════════════════════════════════════════════════════════════════════════
# Фіг.1 — топологія: проста внутрішня шина ↔ FMC ↔ ніжки ↔ зовнішні мікросхеми
# ════════════════════════════════════════════════════════════════════════════
def fig_topology():
    W, H = 1000, 470
    p = []

    # ── ядро (ліворуч) ──
    p.append(rect(70, 150, 150, 120, fill="#eef2fb", stroke=NEG, sw=2, rx=8))
    p.append(text(145, 186, "Ядро", size=14, color=NEG, bold=True))
    p.append(text(145, 208, "Cortex-M", size=11, color=INK))
    p.append('<text x="145.0" y="238.0" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle">*ptr = 0x1234;</text>' % (MONO, INK))
    p.append(text(145, 258, "просто запис за адресою", size=9.5, color=MUTED, italic=True))

    # проста внутрішня шина
    p.append(arrow(220, 210, 300, 210, color=INK, sw=2.2))
    p.append(text(260, 200, "проста", size=10, color=INK, bold=True))
    p.append(text(260, 246, "внутрішня\nшина ядра".split("\n")[0], size=9.5, color=MUTED))
    p.append(text(260, 258, "адреса+дані", size=9.5, color=MUTED, italic=True))

    # ── FMC (посередині) ──
    p.append(rect(300, 120, 190, 180, fill="#f3f7f3", stroke=FIELD, sw=2.4, rx=10))
    p.append(text(395, 150, "FMC / FSMC", size=15, color=FIELD, bold=True))
    p.append(text(395, 170, "апаратний блок у МК", size=10, color=INK, italic=True))
    for k, s in enumerate(["дешифрує адресу → NEx",
                            "виставляє A, D на ніжки",
                            "смикає NWE / NOE",
                            "відлічує такти HCLK"]):
        p.append(text(314, 196 + k * 22, "• " + s, size=10.5, color=INK, anchor="start"))

    # шина зовнішніх ніжок (жмут)
    p.append(arrow(490, 210, 590, 210, color=POS, sw=2.4))
    p.append(text(540, 198, "ніжки МК", size=10.5, color=POS, bold=True))
    for k, lab in enumerate(["NEx", "A[25:0]", "D[15:0]", "NWE·NOE·NADV"]):
        p.append(text(540, 234 + k * 15, lab, size=9.5, color=MUTED, italic=True))

    # ── зовнішні мікросхеми (праворуч) ──
    p.append(chip(600, 120, 150, 66, "SRAM / PSRAM", "статична пам'ять"))
    p.append(chip(600, 208, 150, 66, "NOR Flash", "код/дані"))
    p.append(rect(600, 296, 150, 66, fill="#3a2a55", stroke="#000", sw=1.5, rx=5))
    p.append(text(675, 322, "дисплей", size=12, color="#e9e9e9", bold=True))
    p.append(text(675, 340, "паралельний 8080", size=9.5, color="#c8b6e6", italic=True))

    # спільна шина до трьох цілей
    p.append(line(590, 153, 590, 329, color=POS, sw=2.0))
    for yy in (153, 241, 329):
        p.append(arrow(590, yy, 600, yy, color=POS, sw=1.8))

    p.append(text(W / 2, 410,
                  "Ядро робить звичайний запис за адресою — а FMC перетворює його на смикання ніжок:",
                  size=12.5, color=INK, bold=True))
    p.append(text(W / 2, 432,
                  "піднімає потрібний NEx, кладе адресу й дані на шину, дає імпульс NWE — і зовні "
                  "з'являється цикл шини пам'яті.",
                  size=12, color=INK))
    p.append(text(W / 2, 452,
                  "Для програми зовнішня мікросхема — просто ще один діапазон адрес.",
                  size=11.5, color=FIELD, italic=True))

    render(os.path.join(OUT, "topology.svg"), W, H, *p,
           title="FMC/FSMC: місток між простою шиною ядра і ніжками зовнішньої пам'яті")


# ════════════════════════════════════════════════════════════════════════════
# Фіг.2 — асинхронний цикл запису: NEx, A, D, NWE й фази ADDSET/DATAST/ADDHLD
# ════════════════════════════════════════════════════════════════════════════
def fig_write_timing():
    W, H = 1000, 470
    p = []
    x0 = 170
    hi, lo = 96, 128           # рівні для NEx/NWE
    row = 84

    # спільні межі фаз (у px від x0)
    w_lead = 40                # NEx уже низький до старту адреси
    addset = 90                # ADDSET: адреса встановилась, NWE ще високий
    datast = 150               # DATAST: NWE низький, дані дійсні
    hold   = 70                # ADDHLD: NWE знявся, дані ще тримаються
    tail   = 40
    t_astart = x0 + w_lead
    t_we_lo  = t_astart + addset
    t_we_hi  = t_we_lo + datast
    t_end    = t_we_hi + hold

    def rowlabel(y, s, col):
        p.append(text(x0 - 14, y + 5, s, size=12, color=col, anchor="end", bold=True))

    # ── NEx (chip select), активний-низький: 1 → 0 (старт адреси) → 1 (кінець) ──
    y = 96
    rowlabel(y, "~NEx", POS)
    p.append(wave(x0, y - 22, y,
                  [(w_lead, 1), (addset + datast + hold, 0), (tail, 1)], color=POS))

    # ── Адреса + RS ──
    y2 = 96 + row
    rowlabel(y2, "A / RS", NEG)
    p.append(bus_valid(x0, y2 - 22, y2, w_lead, addset + datast + hold, tail,
                       color=NEG, label="адреса дійсна", lab_col=NEG))

    # ── NWE (строб запису), активний-низький ──
    y3 = 96 + 2 * row
    rowlabel(y3, "~NWE", INK)
    p.append(wave(x0, y3 - 22, y3,
                  [(w_lead + addset, 1), (datast, 0), (hold + tail, 1)], color=INK, sw=2.4))

    # ── Дані (пише ядро) ──
    y4 = 96 + 3 * row
    rowlabel(y4, "D[15:0]", FIELD)
    p.append(bus_valid(x0, y4 - 22, y4, w_lead + addset - 10, datast + hold + 10, tail,
                       color=FIELD, label="дані ядра", lab_col=FIELD))

    # ── вертикальні напрямні фаз ──
    top, bot = 66, 96 + 3 * row + 14
    for xx in (t_astart, t_we_lo, t_we_hi, t_end):
        p.append(line(xx, top, xx, bot, color="#d7dbe0", sw=1.1, dash="4 4"))

    # ── позначки фаз ──
    def phase(xa, xb, lab, col):
        ymid = 300
        p.append(line(xa, ymid, xb, ymid, color=col, sw=1.4))
        p.append(line(xa, ymid - 5, xa, ymid + 5, color=col, sw=1.4))
        p.append(line(xb, ymid - 5, xb, ymid + 5, color=col, sw=1.4))
        p.append(text((xa + xb) / 2, ymid - 8, lab, size=11, color=col, bold=True))

    phase(t_astart, t_we_lo, "ADDSET", NEG)
    phase(t_we_lo, t_we_hi, "DATAST", INK)
    phase(t_we_hi, t_end, "ADDHLD", MUTED)
    p.append(text(t_we_hi, 318, "фронт ↑NWE ловить дані", size=10, color=POS, anchor="middle", italic=True))
    p.append('<line x1="%.1f" y1="322" x2="%.1f" y2="342" stroke="%s" stroke-width="1.4" '
             'marker-end="url(#arrow)"/>' % (t_we_hi, t_we_hi, POS))

    p.append(text(W / 2, 380,
                  "Кожен відрізок — ціле число тактів HCLK, задане в регістрі таймінгу банку.",
                  size=12.5, color=INK, bold=True))
    p.append(text(W / 2, 402,
                  "ADDSET — скільки чекати, поки адреса вляжеться, перш ніж опустити ~NWE; "
                  "DATAST — доки тримати ~NWE (і дані);",
                  size=12, color=INK))
    p.append(text(W / 2, 422,
                  "мікросхема-пам'ять фіксує дані на висхідному фронті ~NWE. Замало тактів — "
                  "чіп не встиг, у пам'ять ляже сміття.",
                  size=12, color=INK))
    p.append(text(W / 2, 446,
                  "Ці числа підбирають під конкретну мікросхему: швидшій вистачає 1–2 такти, "
                  "повільнішій треба більше.",
                  size=11.5, color=FIELD, italic=True))

    render(os.path.join(OUT, "write-timing.svg"), W, H, *p,
           title="Асинхронний цикл запису: як FMC розкладає одне «*ptr = x» у часі")


# ════════════════════════════════════════════════════════════════════════════
# Фіг.3 — адресна мапа: вікно 0x6000_0000 ділиться A[27:26] на NE1..NE4
# ════════════════════════════════════════════════════════════════════════════
def fig_memmap():
    W, H = 1000, 470
    p = []

    # ── стовпчик адрес (ліворуч): банк NOR/PSRAM = 4 підвікна по 64 МБ ──
    bx, bw = 120, 210
    top = 90
    seg_h = 74
    regions = [
        ("0x6000_0000", "NE1", "00", "SRAM / PSRAM", NEG),
        ("0x6400_0000", "NE2", "01", "NOR Flash", FIELD),
        ("0x6800_0000", "NE3", "10", "дисплей (8080)", "#6a3fb5"),
        ("0x6C00_0000", "NE4", "11", "вільно", MUTED),
    ]
    for i, (addr, ne, bits, dev, col) in enumerate(regions):
        y = top + i * seg_h
        p.append(rect(bx, y, bw, seg_h - 8, fill="#f7f9fb", stroke=col, sw=2, rx=6))
        p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
                 'text-anchor="start" font-weight="700">%s</text>'
                 % (bx + 12, y + 26, MONO, INK, addr))
        p.append(text(bx + 12, y + 46, "64 МБ · " + dev, size=11, color=col, anchor="start", bold=True))
        # права мітка ~NEx
        p.append(rect(bx + bw + 30, y + 8, 66, 34, fill=BG, stroke=col, sw=1.8, rx=5))
        p.append(text(bx + bw + 63, y + 30, "~" + ne, size=12, color=col, bold=True))
        p.append(arrow(bx + bw, y + 25, bx + bw + 30, y + 25, color=col, sw=1.6))
        # біти A[27:26]
        p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
                 'text-anchor="start">A[27:26]=%s</text>'
                 % (bx + bw + 108, y + 30, MONO, col, bits))

    p.append(text(bx + bw / 2, top - 14, "Банк NOR/PSRAM (256 МБ)", size=12, color=INK, bold=True))

    # ── розклад біта адреси (праворуч унизу) ──
    ry = 396
    p.append(text(548, 108, "Адреса розпадається на поля:", size=13, color=INK, anchor="start", bold=True))
    fields = [
        ("31…28", "0110", "= 0x6 → зовнішня\nпам'ять узагалі", POS, 138),
        ("27…26", "xx", "→ який ~NEx\n(1 з 4)", "#6a3fb5", 108),
        ("25…0", "……", "→ комірка\nвсередині чіпа", NEG, 138),
    ]
    fx = 548
    fy = 130
    for name, val, note, col, w in fields:
        p.append(rect(fx, fy, w, 54, fill="#fbfdff", stroke=col, sw=2, rx=8))
        p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
                 'text-anchor="middle" font-weight="700">A[%s]</text>'
                 % (fx + w / 2, fy + 22, MONO, col, name))
        p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
                 'text-anchor="middle">%s</text>' % (fx + w / 2, fy + 44, MONO, INK, val))
        lines = note.split("\n")
        for k, ln in enumerate(lines):
            p.append(text(fx + w / 2, fy + 78 + k * 16, ln, size=10.5, color=col))
        fx += w + 16

    p.append(rect(548, 250, fx - 548 - 16, 66, fill="#f3f7f3", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(564, 274, "Це та сама каскадна дешифрація, що на будь-якій шині:", size=12,
                  color=INK, anchor="start", bold=True))
    p.append(text(564, 294, "старші біти вибирають мікросхему (піднімають один ~NEx),",
                  size=11.5, color=INK, anchor="start"))
    p.append(text(564, 310, "молодші йдуть усередину неї на вибір комірки.",
                  size=11.5, color=INK, anchor="start"))

    p.append(text(W / 2, ry,
                  "Вся зовнішня пам'ять живе від 0x6000_0000; чотири підвікна по 64 МБ — "
                  "це чотири окремі мікросхеми, кожна зі своїм ~NEx.",
                  size=12, color=INK))
    p.append(text(W / 2, ry + 22,
                  "Записав за адресою 0x6800_0000 — активувався ~NE3, і цикл пішов саме до дисплея.",
                  size=11.5, color="#6a3fb5", bold=True))

    render(os.path.join(OUT, "memmap.svg"), W, H, *p,
           title="Адресна мапа FMC: одне вікно, поділене на чотири вибірки кристала")


# ════════════════════════════════════════════════════════════════════════════
# Фіг.H1 — той самий запис двома мовами: 8080 (окремий ~WR) vs 6800 (R/W + E)
#          (для вставки hist-parallel-bus.md)
# ════════════════════════════════════════════════════════════════════════════
def fig_two_cycles():
    W, H = 940, 470
    p = []
    midx = W / 2
    p.append(line(midx, 70, midx, H - 60, color="#d7dbe0", sw=1.4, dash="5 6"))

    p.append(text(W * 0.25, 48, "8080: два окремі строби ~RD і ~WR", size=14, color=NEG, bold=True))
    p.append(text(W * 0.75, 48, "6800: рівень R/W + спільний строб E", size=14, color=FIELD, bold=True))

    row = 82

    def panel(labx, trkx, trkw):
        # геометрія «вікна» активності
        a = trkx + trkw * 0.14   # адреса/CS вже стоять
        b = trkx + trkw * 0.36   # строб починає активну фазу
        c = trkx + trkw * 0.70   # завершення обміну (захоплення)
        d = trkx + trkw * 0.90   # CS/адреса знімаються
        return a, b, c, d

    def rowlabel(labx, y, s, col):
        p.append(text(labx, y + 5, s, size=12.5, color=col, anchor="end", bold=True))

    # ── ЛІВА панель: 8080 ──
    lx = 30
    llab = 120
    ltrk = 128
    ltrw = midx - 46 - ltrk
    a, b, c, d = panel(llab, ltrk, ltrw)

    # A/~CS
    y = 96
    rowlabel(llab, y - 11, "A / ~CS", NEG)
    p.append(wave(ltrk, y - 22, y, [(a - ltrk, 1), (d - a, 0), (ltrk + ltrw - d, 1)], color=NEG))
    # ~WR (єдиний активний строб — запис)
    y2 = 96 + row
    rowlabel(llab, y2 - 11, "~WR", POS)
    p.append(wave(ltrk, y2 - 22, y2, [(b - ltrk, 1), (c - b, 0), (ltrk + ltrw - c, 1)], color=POS, sw=2.6))
    p.append(arrow(c, y2 + 20, c, y2 + 4, color=POS, sw=1.8))
    p.append(text(c, y2 + 36, "фронт ~WR", size=10, color=POS))
    p.append(text(c, y2 + 50, "фіксує дані", size=10, color=POS))
    # ~RD лежить пасивно
    y3 = 96 + 2 * row
    rowlabel(llab, y3 - 11, "~RD", MUTED)
    p.append(wave(ltrk, y3 - 22, y3, [(ltrw, 1)], color=MUTED, sw=1.8))
    p.append(text((ltrk + ltrw + ltrk) / 2, y3 - 26, "лишається високим (не читаємо)", size=10, color=MUTED, italic=True))
    # D
    y4 = 96 + 3 * row
    rowlabel(llab, y4 - 11, "D[..]", INK)
    p.append(bus_valid(ltrk, y4 - 22, y4, b - ltrk - 6, c - b + 6, ltrk + ltrw - c,
                       color=NEG, label="дані ядра", lab_col=NEG))

    # ── ПРАВА панель: 6800 ──
    rlab = midx + 118
    rtrk = midx + 126
    rtrw = (W - 30) - rtrk
    a, b, c, d = panel(rlab, rtrk, rtrw)

    # A/~CS
    rowlabel(rlab, 96 - 11, "A / ~CS", NEG)
    p.append(wave(rtrk, 96 - 22, 96, [(a - rtrk, 1), (d - a, 0), (rtrk + rtrw - d, 1)], color=NEG))
    # R/W (рівень — тримається низько весь цикл = запис)
    yr = 96 + row
    rowlabel(rlab, yr - 11, "R/W", INK)
    p.append(wave(rtrk, yr - 22, yr, [(a - rtrk, 1), (d - a, 0), (rtrk + rtrw - d, 1)], color=INK, sw=2.4))
    p.append(text((a + d) / 2, yr - 26, "= 0 весь цикл (це РІВЕНЬ, не строб)", size=10, color=INK, italic=True))
    # E (спільний строб-дозвіл)
    ye = 96 + 2 * row
    rowlabel(rlab, ye - 11, "E", FIELD)
    p.append(wave(rtrk, ye, ye - 22, [(b - rtrk, 0), (c - b, 1), (rtrk + rtrw - c, 0)], color=FIELD, sw=2.6))
    p.append(arrow(c, ye + 20, c, ye + 4, color=FIELD, sw=1.8))
    p.append(text(c, ye + 36, "спад E", size=10, color=FIELD))
    p.append(text(c, ye + 50, "завершує обмін", size=10, color=FIELD))
    # D
    yd = 96 + 3 * row
    rowlabel(rlab, yd - 11, "D[..]", INK)
    p.append(bus_valid(rtrk, yd - 22, yd, b - rtrk - 6, c - b + 6, rtrk + rtrw - c,
                       color=FIELD, label="дані ядра", lab_col=FIELD))

    p.append(text(W * 0.25, H - 34,
                  "напрямок каже те, ЯКИЙ зі стробів смикнувся; читання — той самий малюнок на ~RD",
                  size=11, color=MUTED, italic=True))
    p.append(text(W * 0.75, H - 34,
                  "напрямок каже РІВЕНЬ R/W; і читання, і запис відкриває той самий строб E",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "two-cycles.svg"), W, H, *p,
           title="Один запис двома мовами: 8080 смикає окремий ~WR, 6800 тримає R/W і дає імпульс E")


# ════════════════════════════════════════════════════════════════════════════
# Фіг.H2 — родовід: дві шини 1974 → «8080/6800-режим» дисплеїв → FMC вміє обидва
# ════════════════════════════════════════════════════════════════════════════
def fig_lineage():
    W, H = 920, 430
    p = []
    xL, xR = W * 0.27, W * 0.73

    def node(cx, cy, s, col, fillc, bold=True, size=13):
        b, w, h = textbox(cx, cy, s, size=size, pad=12, fill=fillc, stroke=col, sw=2, color=col, bold=bold)
        p.append(b)
        return w, h

    w1, h1 = node(xL, 56, "Intel 8080\nквітень 1974", NEG, "#eef2fb")
    w2, h2 = node(xR, 56, "Motorola 6800\nберезень 1974", FIELD, "#f3f7f3")

    sw1, sh1 = node(xL, 158, "дві лінії: ~RD і ~WR\n(окремі строби)", NEG, BG, bold=False, size=12.5)
    sw2, sh2 = node(xR, 158, "R/W (рівень) + E (строб)\nодна лінія напрямку", FIELD, BG, bold=False, size=12.5)
    p.append(arrow(xL, 56 + h1 / 2 + 3, xL, 158 - sh1 / 2 - 3, color=NEG, sw=2))
    p.append(arrow(xR, 56 + h2 / 2 + 3, xR, 158 - sh2 / 2 - 3, color=FIELD, sw=2))

    mw1, mh1 = node(xL, 262, "«8080-режим»\nконтролерів дисплеїв", NEG, "#eef2fb", size=12.5)
    mw2, mh2 = node(xR, 262, "«6800-режим»\nконтролерів дисплеїв", FIELD, "#f3f7f3", size=12.5)
    p.append(arrow(xL, 158 + sh1 / 2 + 3, xL, 262 - mh1 / 2 - 3, color=NEG, sw=2))
    p.append(arrow(xR, 158 + sh2 / 2 + 3, xR, 262 - mh2 / 2 - 3, color=FIELD, sw=2))

    fw, fh = node(W / 2, 372, "STM32 FMC / FSMC\nуміє ОБИДВА режими", INK, FILL, size=13.5)
    p.append(arrow(xL, 262 + mh1 / 2 + 3, W / 2 - fw / 2 - 6, 372 - 6, color=NEG, sw=2))
    p.append(arrow(xR, 262 + mh2 / 2 + 3, W / 2 + fw / 2 + 6, 372 - 6, color=FIELD, sw=2))

    render(os.path.join(OUT, "lineage.svg"), W, H, *p,
           title="Дві процесорні шини 1974 року дожили як два режими контролерів дисплеїв")


# ════════════════════════════════════════════════════════════════════════════
# Фіг.P1 (вставка proj-fmc-lcd) — числа даташита дисплея → такти HCLK у FMC
# ════════════════════════════════════════════════════════════════════════════
def fig_lcd_timing():
    W, H = 1000, 520
    p = []

    # ── верх: три числа даташита ILI9341 (8080-запис) ──
    p.append(text(W / 2, 60, "Даташит ILI9341 (режим 8080, цикл запису) — три числа в наносекундах:",
                  size=13.5, color=INK, bold=True))
    ds = [
        ("tWRL", "≥ 15 нс", "~WR низький", POS),
        ("tWRH", "≥ 15 нс", "~WR високий", NEG),
        ("tWC", "≥ 66 нс", "повний цикл", FIELD),
    ]
    bx, bw, gap = 150, 200, 40
    for i, (nm, val, note, col) in enumerate(ds):
        x = bx + i * (bw + gap)
        p.append(rect(x, 78, bw, 74, fill="#fbfdff", stroke=col, sw=2.2, rx=9))
        p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="15" fill="%s" '
                 'text-anchor="middle" font-weight="700">%s</text>' % (x + bw / 2, 104, MONO, col, nm))
        p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="15" fill="%s" '
                 'text-anchor="middle">%s</text>' % (x + bw / 2, 127, MONO, INK, val))
        p.append(text(x + bw / 2, 145, note, size=10, color=col))

    # ── стрілка «ділимо на період HCLK» ──
    p.append(arrow(W / 2, 160, W / 2, 200, color=INK, sw=2))
    p.append('<text x="%.1f" y="184" font-family="%s" font-size="12.5" fill="%s" '
             'text-anchor="start" font-weight="700"> ÷ період HCLK (168 МГц → 5.95 нс), '
             'округлити ВГОРУ</text>' % (W / 2 + 8, MONO, POS))

    # ── низ: цикл, розкладений на такти HCLK ──
    x0 = 150
    tick = 42
    y_we = 300
    addset_n, datast_n = 8, 3
    total_n = addset_n + datast_n + 1

    for k in range(total_n + 1):
        xx = x0 + k * tick
        p.append(line(xx, 250, xx, 360, color="#e2e5ea", sw=1.0))
    for k in range(total_n):
        xx = x0 + k * tick
        p.append(text(xx + tick / 2, 246, str(k + 1), size=9, color=MUTED))
    p.append(text(x0 + total_n * tick / 2, 232,
                  "такти HCLK (5.95 нс кожен)", size=10.5, color=MUTED, italic=True))

    x_lo = x0 + addset_n * tick
    x_hi = x_lo + datast_n * tick
    x_end = x0 + total_n * tick
    p.append(text(x0 - 14, y_we - 4, "~WR", size=12, color=INK, anchor="end", bold=True))
    p.append(wave(x0, y_we - 26, y_we,
                  [(addset_n * tick, 1), (datast_n * tick, 0), (tick, 1)], color=INK, sw=2.6))

    def phase(xa, xb, lab, col, yy=330):
        p.append(line(xa, yy, xb, yy, color=col, sw=1.5))
        p.append(line(xa, yy - 5, xa, yy + 5, color=col, sw=1.5))
        p.append(line(xb, yy - 5, xb, yy + 5, color=col, sw=1.5))
        p.append(text((xa + xb) / 2, yy - 7, lab, size=11, color=col, bold=True))

    phase(x0, x_lo, "ADDSET = 8", NEG)
    phase(x_lo, x_hi, "DATAST = 3", POS)
    p.append(text((x_lo + x_hi) / 2, 384, "DATAST покриває tWRL", size=10.5, color=POS, italic=True))
    p.append(line(x0, 404, x_end, 404, color=FIELD, sw=1.6))
    p.append(line(x0, 399, x0, 409, color=FIELD, sw=1.6))
    p.append(line(x_end, 399, x_end, 409, color=FIELD, sw=1.6))
    p.append(text((x0 + x_end) / 2, 397,
                  "повний цикл ≈ (8+3+1)×5.95 ≈ 71 нс ≥ tWC = 66 нс", size=11, color=FIELD, bold=True))

    p.append(text(W / 2, 442,
                  "Пастка: візьмеш такти «упритул» під tWRL (DATAST=3), забувши про tWC — "
                  "окремий імпульс наче правильний,", size=11.5, color=INK))
    p.append(text(W / 2, 461,
                  "а повний цикл закороткий. Команди старту пройдуть (між ними код зволікає), "
                  "а швидке заливання — в артефактах.", size=11.5, color=INK))
    p.append(text(W / 2, 486,
                  "Лік: ADDSET дотягує повну тривалість до tWC. Швидше даташит не дозволяє, "
                  "повільніше — лише мляво малює.", size=11.5, color=FIELD, italic=True))

    render(os.path.join(OUT, "lcd-timing.svg"), W, H, *p,
           title="Від наносекунд даташита дисплея — до тактів FMC")


if __name__ == "__main__":
    fig_topology()
    fig_write_timing()
    fig_memmap()
    fig_two_cycles()
    fig_lineage()
    fig_lcd_timing()
    print("OK: figures written to", OUT)
