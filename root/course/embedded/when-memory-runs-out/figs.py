# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── escalation: спершу видавити SRAM, аж потім виносити назовні ────────────────
# Ідея: зовнішня пам'ять — останній крок. Спершу прибрати симптоми (переповнення
# стека, фрагментація) дешевими засобами; коли й це не рятує — у зовнішній чип.

def fig_escalation():
    W, H = 780, 300
    p = []
    # три кроки зліва направо, кожен трохи вище — відчуття «сходів угору»
    steps = [
        (130, 200, "СИМПТОМ:\nбракує SRAM", "переповнення стека,\nфрагментація купи,\nкраш", POS, "#fdecea"),
        (390, 150, "ВИДАВИТИ наявну\n(перша лінія)", "статичні буфери,\nпули, обробка\nпотоком", FIELD, "#eafaf0"),
        (650, 100, "ВИНЕСТИ назовні\n(останній крок)", "робоче → PSRAM,\nсховище → Flash", NEG, "#eef4ff"),
    ]
    centers = []
    for cx, cy, head, body, col, fill in steps:
        h, hw, hh = textbox(cx, cy, head, size=11, bold=True, color=col,
                            fill=fill, stroke=col, sw=1.8)
        p.append(h)
        p.append(mtext(cx, cy + hh / 2 + 16, body, size=9, color=MUTED))
        centers.append((cx, cy, hw, hh))
    # стрілки від правого краю одного кроку до лівого краю наступного
    for i in range(2):
        x1 = centers[i][0] + centers[i][2] / 2
        y1 = centers[i][1]
        x2 = centers[i + 1][0] - centers[i + 1][2] / 2
        y2 = centers[i + 1][1]
        p.append(arrow(x1 + 4, y1, x2 - 4, y2, color=INK, sw=1.8))

    p.append(text(W / 2, H - 16, "зовнішня пам'ять — не перший крок, а останній: спершу видави все з наявної SRAM",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "escalation.svg"), W, H, *p,
           title="Коли SRAM закінчується: від симптому до зовнішнього чипа")


# ── appetite: апетит задач (лог-шкала) проти стелі вбудованої SRAM ─────────────
# Ідея: стовпці потреб у байтах на лог-осі; червоний пунктир — типова стеля
# SRAM мікроконтролера. Видно, що більшість задач пробиває стелю наскрізь.

def fig_appetite():
    W, H = 760, 420
    bx, by = 70, 330                 # лівий-нижній кут поля стовпців
    bw, bh = 640, 270                # ширина поля, висота під стовпці
    p = []

    # лог-шкала від 1 КБ до 1 МБ (10^0 .. 10^3 КБ)
    lo_kb, hi_kb = 1.0, 1024.0
    def ypos(kb):                    # КБ → y (лог)
        t = (math.log10(kb) - math.log10(lo_kb)) / (math.log10(hi_kb) - math.log10(lo_kb))
        return by - t * bh

    # горизонтальні лінії-десятки + підписи зліва
    for kb, lab in [(1, "1 КБ"), (10, "10 КБ"), (100, "100 КБ"), (1024, "1 МБ")]:
        gy = ypos(kb)
        p.append(line(bx, gy, bx + bw, gy, color="#e4e8ee", sw=1.0))
        p.append(text(bx - 8, gy + 4, lab, size=10, color=MUTED, anchor="end"))

    # осі
    p.append(line(bx, by, bx + bw, by, color=INK, sw=1.6))
    p.append(line(bx, by, bx, by - bh, color=INK, sw=1.6))

    # стовпці потреб
    bars = [
        ("екран\n160×128", 40, "#cfe0f5"),
        ("екран\n320×240", 150, "#9fc0ea"),
        ("стерео\n1 с", 176, "#dff0df"),
        ("логи\nза хв", 30, "#f6efd6"),
        ("камера\n640×480", 900, "#f3dede"),
    ]
    n = len(bars)
    slot = bw / n
    cw = slot * 0.52
    for i, (lab, kb, fill) in enumerate(bars):
        cx = bx + slot * (i + 0.5)
        top = ypos(kb)
        p.append(rect(cx - cw / 2, top, cw, by - top, fill=fill, stroke=INK, sw=1.3, rx=0))
        # значення над стовпцем
        val = ("%d КБ" % kb) if kb < 1024 else "≈1 МБ"
        if kb >= 700:
            val = "≈0.9 МБ"
        p.append(text(cx, top - 7, val, size=10, color=INK, bold=True))
        # підпис під віссю
        p.append(mtext(cx, by + 18, lab, size=10, color=INK))

    # червоний пунктир — стеля SRAM (≈256 КБ як орієнтир «у кращому разі»)
    ceil_kb = 256.0
    cy = ypos(ceil_kb)
    p.append(line(bx, cy, bx + bw, cy, color=POS, sw=2.2, dash="8 5"))
    box = textbox(bx + bw - 96, cy - 16, "стеля SRAM\n(сотні КБ)", size=10,
                  bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.4)[0]
    p.append(box)

    p.append(text(W / 2, H - 14, "більшість задач пробиває стелю SRAM наскрізь (вісь байтів — логарифмічна)",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "appetite.svg"), W, H, *p,
           title="Апетит реальних задач проти вбудованої SRAM")


# ── framebuffer: звідки беруться байти кадру ───────────────────────────────────
# Ідея: обсяг = (байтів/піксель) × (пікселів); один кадр 320×240 RGB565 ≈ 150 КБ,
# другий буфер для плавності подвоює до 300 КБ.

def fig_framebuffer():
    W, H = 720, 340
    p = []
    cx = W / 2

    # формула вгорі
    f, fw, fh = textbox(cx, 70, "обсяг кадру = (байтів/піксель) × (пікселів)",
                        size=14, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=14)
    p.append(f)

    # ліворуч — піксель = 2 байти (RGB565)
    px_x = 170
    p.append(text(px_x, 150, "RGB565: 2 Б/піксель", size=12, color=INK, bold=True))
    seg_y = 168
    parts = [("R", 5, "#f3dede"), ("G", 6, "#dff0df"), ("B", 5, "#cfe0f5")]
    sx = px_x - 80
    unit = 11
    for lab, bits, fill in parts:
        w = bits * unit
        p.append(rect(sx, seg_y, w, 26, fill=fill, stroke=INK, sw=1.2, rx=0))
        p.append(text(sx + w / 2, seg_y + 18, "%s·%d" % (lab, bits), size=10, color=INK))
        sx += w
    p.append(text(px_x, seg_y + 48, "5 + 6 + 5 = 16 біт = 2 Б", size=10, color=MUTED))

    # праворуч — обчислення обсягу
    calc_x = 470
    p.append(line(W * 0.5 + 10, 130, W * 0.5 + 10, 300, color="#e4e8ee", sw=1.2))
    lines = [
        ("320 × 240", "= 76 800 пікселів"),
        ("× 2 Б", "= 153 600 Б ≈ 150 КБ"),
        ("× 2 буфери", "= 300 КБ"),
    ]
    ly = 150
    cols = [FIELD, NEG, POS]
    for i, (a, b) in enumerate(lines):
        p.append(text(calc_x, ly, a, size=13, color=INK, anchor="start", bold=True))
        p.append(text(calc_x + 110, ly, b, size=12, color=cols[i], anchor="start"))
        ly += 40

    # підпис подвійної буферизації
    p.append(text(calc_x, ly + 4, "другий буфер — щоб око не ловило", size=10,
                  color=MUTED, anchor="start"))
    p.append(text(calc_x, ly + 20, "напівдомальований кадр", size=10,
                  color=MUTED, anchor="start"))

    p.append(text(W / 2, H - 14, "один кадр уже 150 КБ; плавна анімація — 300 КБ, за межею SRAM",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "framebuffer.svg"), W, H, *p,
           title="Звідки беруться байти кадру дисплея")


# ── three-loads: три навантаження → дві різні пам'яті ──────────────────────────
# Ідея: кадри й аудіо тягнуть до швидкої робочої RAM; логи — до ємного нелеткого
# сховища. Одна пам'ять обидві потреби не закриє.

def fig_three_loads():
    W, H = 740, 360
    p = []

    # три джерела зліва
    src_x = 130
    srcs = [
        (90, "кадри\nдисплея", "#cfe0f5"),
        (175, "буфери\nаудіо", "#dff0df"),
        (270, "логи й\nзаписи", "#f6efd6"),
    ]
    for sy, lab, fill in srcs:
        b, bw, bh = textbox(src_x, sy, lab, size=11, bold=True, fill=fill, stroke=INK, sw=1.5)
        p.append(b)

    # два призначення справа
    ram_x, ram_y = 580, 130
    sto_x, sto_y = 580, 270
    ram, rw, rh = textbox(ram_x, ram_y, "швидка робоча RAM\nвеликий обсяг · миттєвий доступ\nнелеткість НЕ потрібна",
                          size=11, bold=True, color=NEG, fill="#eef4ff", stroke=NEG, sw=1.8)
    sto, sw_, sh = textbox(sto_x, sto_y, "ємне нелетке сховище\nмегабайти · мусить пережити збій\nзапис рідший за читання",
                           size=11, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.8)

    # стрілки: кадри+аудіо → RAM; логи → сховище
    p.append(arrow(src_x + 52, 90, ram_x - rw / 2, ram_y - 14, color=NEG, sw=1.8))
    p.append(arrow(src_x + 52, 175, ram_x - rw / 2, ram_y + 14, color=NEG, sw=1.8))
    p.append(arrow(src_x + 52, 270, sto_x - sw_ / 2, sto_y, color=FIELD, sw=1.8))
    p.append(ram)
    p.append(sto)

    p.append(text(W / 2, H - 16, "одна пам'ять не буває водночас і блискавично-швидкою, і дешево-ємною, і нелеткою",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "three-loads.svg"), W, H, *p,
           title="Три навантаження — дві різні пам'яті")


# ── timeline: дорога до DRAM (ферит → 1T-комірка → перемога) ───────────────────
# Ідея: думка 1966-го дозріла не вмить; масова DRAM (1103) пішла НЕ на комірці
# Деннарда, а 1T перемогла лише в середині 1970-х, коли дозрів техпроцес.

def fig_timeline():
    W, H = 820, 300
    p = []
    ax, ay = 50, 150
    aw = 720
    p.append(line(ax, ay, ax + aw, ay, color=INK, sw=2.2))
    p.append(arrow(ax + aw - 1, ay, ax + aw + 1, ay, color=INK, sw=2.2))

    nodes = [
        (0.04, "до 1968", "ферит\nруками", MUTED, "#efefef", True),
        (0.24, "1966", "епіфанія:\nодин транзистор?", FIELD, "#eafaf0", False),
        (0.46, "1967–68", "патент IBM\nUS 3 387 286", NEG, "#eef4ff", True),
        (0.68, "жовт. 1970", "Intel 1103:\nперша масова DRAM\n(3T, не Деннард)", POS, "#fdecea", False),
        (0.92, "сер. 1970-х", "1T перемагає\n(4 Кбіт) — донині", FIELD, "#eafaf0", True),
    ]
    for t, year, lab, col, fill, above in nodes:
        x = ax + t * aw
        p.append(circle(x, ay, 6, fill=col, stroke=col, sw=2))
        p.append(text(x, ay + (24 if not above else -52) + (0 if above else 0), year,
                      size=11, color=col, bold=True))
        by = ay - 96 if above else ay + 36
        b, bw, bh = textbox(x, by, lab, size=10, color=INK, fill=fill, stroke=col, sw=1.4)
        # лінія від вузла до рамки
        p.append(line(x, ay, x, by + (bh / 2 if above else -bh / 2), color=col, sw=1.2))
        p.append(b)

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Дорога до DRAM: від феритів до однотранзисторної комірки")


# ── cell: комірка Деннарда (1 транзистор + 1 конденсатор) ──────────────────────
# Ідея: біт = заряд у конденсаторі; транзистор лише ВІДЧИНЯЄ доступ. Ліворуч —
# запис «1», праворуч — зберігання (ключ зачинено, заряд помалу тече).

def fig_cell():
    W, H = 740, 320
    p = []

    def cell(cx, cy, title, col, charged, leaking):
        out = []
        # лінія рядка (word line) — керує ключем
        wl_y = cy - 60
        out.append(line(cx - 90, wl_y, cx + 90, wl_y, color=col, sw=2.0))
        out.append(text(cx - 96, wl_y + 4, "рядок", size=9, color=col, anchor="end"))
        # транзистор-ключ (спрощено — прямокутник «ключ»)
        out.append(fitbox(cx - 26, cy - 44, 52, 30, "ключ", size=10, fill="#f4f6f8",
                          stroke=INK, sw=1.6, bold=True))
        out.append(line(cx, wl_y, cx, cy - 44, color=col, sw=1.6))   # затвор від рядка
        # лінія стовпця (bit line) — підводить заряд зверху до ключа
        out.append(line(cx, cy - 90, cx, cy - 44, color=MUTED, sw=1.6))
        out.append(text(cx + 6, cy - 84, "стовпець", size=9, color=MUTED, anchor="start"))
        # конденсатор під ключем (дві пластини)
        out.append(line(cx, cy - 14, cx, cy + 4, color=INK, sw=1.6))
        out.append(line(cx - 20, cy + 4, cx + 20, cy + 4, color=INK, sw=2.6))     # верхня пластина
        out.append(line(cx - 20, cy + 14, cx + 20, cy + 14, color=INK, sw=2.6))   # нижня пластина
        out.append(line(cx, cy + 14, cx, cy + 30, color=INK, sw=1.6))
        out.append(line(cx - 12, cy + 30, cx + 12, cy + 30, color=INK, sw=2.0))   # земля
        out.append(line(cx - 8, cy + 34, cx + 8, cy + 34, color=INK, sw=1.6))
        out.append(line(cx - 4, cy + 38, cx + 4, cy + 38, color=INK, sw=1.4))
        # заряд у «відерці»
        if charged:
            out.append(plus(cx - 9, cy + 9, r=5))
            out.append(plus(cx + 9, cy + 9, r=5))
        # витік
        if leaking:
            out.append(text(cx + 34, cy + 10, "тече →", size=9, color=POS, anchor="start"))
            out.append(line(cx + 20, cy + 9, cx + 30, cy + 9, color=POS, sw=1.2, dash="3 3"))
        out.append(mtext(cx, cy + 70, title, size=11, color=col, bold=True))
        return out

    p += cell(210, 140, "запис «1»: ключ відчинено,\nзаряд заливається", FIELD, True, False)
    p += cell(540, 140, "зберігання: ключ зачинено,\nзаряд замкнено (й помалу тече)", POS, True, True)

    # роздільник
    p.append(line(W / 2, 70, W / 2, 230, color="#e4e8ee", sw=1.4))

    p.append(text(W / 2, H - 16, "біт — це заряд у конденсаторі; транзистор лише на мить відчиняє до нього доступ",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "cell.svg"), W, H, *p,
           title="Комірка Деннарда: один транзистор-ключ + один конденсатор")


# ── compare: 6T → 3T → 1T (перегони «менше деталей на біт») ─────────────────────
# Ідея: що менше транзисторів на біт, то щільніше й дешевше; 1T зрештою перемогла.

def fig_compare():
    W, H = 780, 320
    p = []
    cols_x = [160, 390, 620]
    cells = [
        ("6T", "SRAM-засувка", "тримає біт сама,\nшвидка, не тече —\nта велика й дорога\n(сьогодні: кеш)", MUTED, "#efefef"),
        ("3T", "комірка Honeywell", "компроміс: заряд\nна затворі, читання\nнеруйнівне —\nIntel 1103", NEG, "#eef4ff"),
        ("1T1C", "комірка Деннарда", "ключ + конденсатор,\nнайщільніша й\nнайдешевша —\nціною регенерації", FIELD, "#eafaf0"),
    ]
    for i, (tag, name, body, col, fill) in enumerate(cells):
        cx = cols_x[i]
        # велике тег-коло з числом транзисторів
        p.append(circle(cx, 95, 34, fill=fill, stroke=col, sw=2.4))
        p.append(text(cx, 101, tag, size=16, color=col, bold=True))
        p.append(text(cx, 150, name, size=11, color=INK, bold=True))
        p.append(fitbox(cx - 95, 165, 190, 96, body, size=10, fill=BG, stroke=col, sw=1.4))
        if i < 2:
            p.append(arrow(cols_x[i] + 100, 95, cols_x[i + 1] - 38, 95, color=INK, sw=1.8))

    p.append(text(W / 2, H - 14, "менше транзисторів на біт → більше бітів на кристал → дешевший біт; тому 1T і перемогла",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "compare.svg"), W, H, *p,
           title="Перегони «менше деталей на біт»: 6 → 3 → 1 транзистор")


# ── two-prices: руйнівне читання + регенерація ────────────────────────────────
# Ідея: обидві «ціни» DRAM ростуть із тендітності заряду. Ліворуч — читання
# спорожнює комірку (треба відновити). Праворуч — заряд сам тече (треба
# періодична регенерація).

def fig_two_prices():
    W, H = 760, 340
    p = []

    # ── ліва панель: читання РУЙНУЄ ──
    lx = 190
    p.append(text(lx, 70, "читання РУЙНУЄ біт", size=12, color=POS, bold=True))
    p.append(fitbox(lx - 60, 90, 120, 40, "комірка\n(заряд)", size=10, fill="#eafaf0",
                    stroke=INK, sw=1.5, bold=True))
    p.append(arrow(lx, 132, lx, 168, color=POS, sw=1.8))
    p.append(text(lx + 8, 152, "заряд стікає в лінію", size=9, color=POS, anchor="start"))
    p.append(fitbox(lx - 70, 168, 140, 40, "підсилювач\n«чує» 1", size=10, fill="#eef4ff",
                    stroke=INK, sw=1.5, bold=True))
    p.append(arrow(lx, 210, lx, 246, color=NEG, sw=1.8))
    p.append(text(lx + 8, 230, "негайно дозаписати", size=9, color=NEG, anchor="start"))
    p.append(fitbox(lx - 70, 246, 140, 40, "ВІДНОВИТИ\nзаряд назад", size=10, fill="#eef4ff",
                    stroke=NEG, sw=1.6, bold=True))

    # роздільник
    p.append(line(W / 2, 60, W / 2, 290, color="#e4e8ee", sw=1.4))

    # ── права панель: заряд ТЕЧЕ з часом ──
    ox, oy = 430, 250
    aw, ah = 280, 150
    p.append(text(ox + aw / 2, 70, "заряд САМ тече з часом", size=12, color=POS, bold=True))
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))       # вісь часу
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.6))       # вісь рівня
    p.append(text(ox + aw, oy + 16, "час", size=10, color=INK, italic=True))
    p.append(text(ox - 8, oy - ah + 4, "рівень", size=9, color=MUTED, anchor="end"))
    # поріг
    thr = oy - ah * 0.4
    p.append(line(ox, thr, ox + aw, thr, color=MUTED, sw=1.2, dash="5 4"))
    p.append(text(ox + aw + 2, thr + 4, "поріг", size=9, color=MUTED, anchor="start"))
    # пилкоподібний спад із регенерацією (зелені точки — поновлення)
    full = oy - ah * 0.9
    seg = aw / 4
    pts = []
    for k in range(4):
        x0 = ox + k * seg
        pts.append((x0, full))
        pts.append((x0 + seg, oy - ah * 0.45))
    poly = []
    for k in range(4):
        x0 = ox + k * seg
        poly.append("%.1f,%.1f" % (x0, full))
        poly.append("%.1f,%.1f" % (x0 + seg, oy - ah * 0.45))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>'
             % (" ".join(poly), POS))
    for k in range(1, 4):
        x0 = ox + k * seg
        p.append(circle(x0, full, 4, fill=FIELD, stroke=FIELD, sw=1))
    p.append(text(ox + aw / 2, oy - ah - 6, "регенерація (зелене) дозаряджає, поки не пізно",
                  size=9, color=FIELD))

    p.append(text(W / 2, H - 14, "обидві ціни — пряма плата за те, що комірка така дешева й крихітна",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "two-prices.svg"), W, H, *p,
           title="Дві ціни за дешевизну однотранзисторної комірки")


# ── lineage: три різні внески (ідея / перший чип / перемога) ───────────────────
# Ідея: «винайшов DRAM» розкладається на три необхідні, але різні заслуги.

def fig_lineage():
    W, H = 800, 300
    p = []
    cols_x = [170, 400, 630]
    items = [
        ("ІДЕЯ й ПАТЕНТ", "Деннард, IBM\n1966–68", "найдешевша\nкомірка 1T1C;\nUS 3 387 286", NEG, "#eef4ff"),
        ("ПЕРШИЙ МАСОВИЙ ЧИП", "Реджіц·Проебстінг\n(Honeywell) + Карп (Intel)", "1103 (1970) — на 3T,\nбо легше виготовити", POS, "#fdecea"),
        ("ПЕРЕМОГА 1T", "уся галузь\nсер. 1970-х", "техпроцес дозрів —\n4 Кбіт беруть 1T,\nстандарт донині", FIELD, "#eafaf0"),
    ]
    for i, (head, who, body, col, fill) in enumerate(items):
        cx = cols_x[i]
        p.append(fitbox(cx - 100, 70, 200, 30, head, size=11, fill=fill, stroke=col, sw=2, bold=True, color=col))
        p.append(mtext(cx, 124, who, size=11, color=INK, bold=True))
        p.append(fitbox(cx - 100, 150, 200, 80, body, size=10, fill=BG, stroke=col, sw=1.3))
        if i < 2:
            p.append(text(cols_x[i] + 105, 95, "≠", size=18, color=INK, bold=True))

    p.append(text(W / 2, H - 16, "«придумати найкращу комірку» ≠ «першим випустити DRAM» ≠ «дотягнути її до серії» — велике зроблено гуртом",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "lineage.svg"), W, H, *p,
           title="Чий це винахід: три різні внески")


if __name__ == "__main__":
    fig_escalation()
    fig_appetite()
    fig_framebuffer()
    fig_three_loads()
    fig_timeline()
    fig_cell()
    fig_compare()
    fig_two_prices()
    fig_lineage()
    print("OK: figures written to", OUT)
