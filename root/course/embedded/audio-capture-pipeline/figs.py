# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── pipeline: увесь тракт захоплення як один конвеєр ───────────────────────────
# Ідея: показати п'ять станцій одним ланцюгом і підписати, ХТО тримає темп на
# кожному стику. Ліва половина — залізо (наш темп задають ЗЗОВНІ), права —
# пам'ять і код (тут темп уже задаємо МИ). Точка переходу — DMA-кільце.

def fig_pipeline():
    W, H = 720, 300
    p = []
    cy = 120
    stations = [
        ("мембрана", "звук →\nнапруга", "#eafaf0", FIELD),
        ("фронт-енд", "АЦП/сигма-\nдельта", "#eef4ff", NEG),
        ("шина", "I2S / АЦП /\nPDM", FILL, INK),
        ("DMA", "кільце\nв RAM", "#f2ecf8", "#8a5fb0"),
        ("буфер", "готовий\nблок", "#fff7e6", "#b8860b"),
    ]
    n = len(stations)
    bw, bh, gap = 108, 66, 26
    total = n * bw + (n - 1) * gap
    x = (W - total) / 2
    edges = []
    for i, (top, sub, fill, st) in enumerate(stations):
        p.append(fitbox(x, cy - bh / 2, bw, bh, top + "\n" + sub, size=11, bold=True,
                        fill=fill, stroke=st, sw=1.7))
        edges.append((x, x + bw))
        if i:
            p.append(arrow(edges[i - 1][1] + 2, cy, x - 2, cy, color=INK, sw=1.9))
        x += bw + gap

    # межа: залізо тримає темп ЗЛІВА, код — СПРАВА; риса між шиною і DMA-кільцем
    mid = (edges[2][1] + edges[3][0]) / 2
    p.append(line(mid, cy - bh / 2 - 34, mid, cy + bh / 2 + 40, color=MUTED, sw=1.2, dash="5 4"))
    p.append(text((edges[0][0] + edges[2][1]) / 2, cy - bh / 2 - 40,
                  "темп задає ЗАЛІЗО — паузи немає", size=10, color=NEG, italic=True))
    p.append(text((edges[3][0] + edges[4][1]) / 2, cy - bh / 2 - 40,
                  "темп задаємо МИ — код читає блоками", size=10, color=FIELD, italic=True))

    # знизу — що тече по стрілках
    p.append(text(edges[0][1] + gap / 2, cy + bh / 2 + 18, "аналог", size=9, color=MUTED))
    p.append(text(edges[1][1] + gap / 2, cy + bh / 2 + 18, "біти", size=9, color=MUTED))
    p.append(text(edges[2][1] + gap / 2, cy + bh / 2 + 18, "слова", size=9, color=MUTED))
    p.append(text(edges[3][1] + gap / 2, cy + bh / 2 + 18, "блок", size=9, color=MUTED))

    p.append(text(W / 2, cy + bh / 2 + 70,
                  "конвеєр захоплення: від коливання повітря до масиву чисел, який можна обробити",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "pipeline.svg"), W, H, *p,
           title="Захоплення звуку — один наскрізний конвеєр із п'яти станцій")


# ── sources: три способи дати конвеєру перше число ────────────────────────────
# Ідея: три входи-джерела показати поряд у трьох колонках і чесно зіставити, що
# кожне віддає МК і скільки роботи лишає на його плечах. Головна вісь — "де
# стоїть АЦП": у мікрофоні (I2S), у самому МК (аналог), чи це 1-бітний PDM,
# який МК ще мусить перетворити фільтром.

def fig_sources():
    W, H = 720, 330
    p = []
    cols = [
        ("I2S-мікрофон", "#eafaf0", FIELD,
         ["АЦП — у мікрофоні", "віддає готові", "24-бітні слова PCM",
          "МК лише забирає", "просто й чисто"]),
        ("аналог + АЦП МК", "#eef4ff", NEG,
         ["АЦП — у самому МК", "потрібен підсилювач", "і опорна напруга",
          "чутливий до завад", "гнучко, але морочливо"]),
        ("PDM-мікрофон", "#f2ecf8", "#8a5fb0",
         ["1-бітний потік", "МК мусить фільтром", "перетворити на PCM",
          "економить піни", "лишає роботу МК"]),
    ]
    n = len(cols)
    cw, gap = 200, 24
    total = n * cw + (n - 1) * gap
    x0 = (W - total) / 2
    for i, (title, fill, st, lines) in enumerate(cols):
        x = x0 + i * (cw + gap)
        # шапка колонки
        p.append(fitbox(x, 60, cw, 46, title, size=13, bold=True, fill=fill, stroke=st, sw=1.8))
        # рядки
        y = 128
        for ln in lines:
            p.append(text(x + cw / 2, y, ln, size=11, color=INK))
            y += 32
    p.append(text(W / 2, 300,
                  "де стоїть перетворювач, те й вирішує, скільки роботи лишиться мікроконтролеру",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "sources.svg"), W, H, *p,
           title="Три джерела звуку: хто робить перетворення в число")


# ── latency: розмір блоку — торг між затримкою і накладними ────────────────────
# Ідея: одна вісь часу. Малий блок — короткий крок затримки, але часто смикає
# ядро (накладні). Великий блок — затримка росте, зате ядро дихає. Формула
# T = N / f_s прив'язує число відліків до реального часу.

def fig_latency():
    W, H = 720, 320
    p = []
    tx0, tx1 = 110, 660
    span = tx1 - tx0

    # верх: малий блок — часті вмикання ядра, коротка затримка
    y1 = 100
    p.append(text(tx0 - 12, y1 + 4, "малий блок", size=11, color=NEG, anchor="end", bold=True))
    p.append(line(tx0, y1, tx1, y1, color=INK, sw=1.2))
    k = 8
    for i in range(k):
        x = tx0 + span * i / k
        p.append(rect(x, y1 - 13, span / k - 3, 26, fill="#eef4ff", stroke=NEG, sw=1.1))
    p.append(text(tx0 + span / (2 * k), y1 - 24, "256", size=9, color=NEG))
    p.append(text(tx0 + span / 2, y1 + 34, "затримка мала (16 мс), але ядро смикають часто",
                  size=10, color=NEG, italic=True))

    # низ: великий блок — рідше, зате затримка більша
    y2 = 200
    p.append(text(tx0 - 12, y2 + 4, "великий блок", size=11, color=FIELD, anchor="end", bold=True))
    p.append(line(tx0, y2, tx1, y2, color=INK, sw=1.2))
    k2 = 3
    for i in range(k2):
        x = tx0 + span * i / k2
        p.append(rect(x, y2 - 13, span / k2 - 4, 26, fill="#eafaf0", stroke=FIELD, sw=1.1))
    p.append(text(tx0 + span / (2 * k2), y2 - 24, "1024", size=9, color=FIELD))
    p.append(text(tx0 + span / 2, y2 + 34, "ядро дихає вільніше, зате затримка більша (64 мс)",
                  size=10, color=FIELD, italic=True))

    p.append(text(W / 2, 272, "час одного блоку:  T = N / f_s   (N — відліків, f_s — частота)",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 300, "для f_s = 16 кГц:  256 → 16 мс,  1024 → 64 мс",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "latency.svg"), W, H, *p,
           title="Розмір блоку: торг між затримкою і навантаженням на ядро")


# ── rates: звідки взялося 44 100 — дві відеосистеми сходяться в одне число ──────
# Ідея вставки hist-audio-rates: показати, що 44 100 — не акустичне число, а
# спільне кратне двох відеосистем. Дві незалежні гілки арифметики (PAL і чорно-
# білий NTSC) стікаються в ту саму цифру 44 100 — ось звідки де-факто стандарт.

def fig_rates():
    W, H = 720, 340
    p = []
    joinx = W / 2            # де сходяться дві гілки
    joiny = 250
    # спільний вузол — 44 100
    p.append(fitbox(joinx - 78, joiny - 30, 156, 60,
                    "44 100\nвідліків/с", size=15, bold=True,
                    fill="#fff7e6", stroke="#b8860b", sw=2.0))

    # ліва гілка — PAL
    lx = 150
    p.append(fitbox(lx - 70, 60, 140, 46, "PAL\n(Європа)", size=12, bold=True,
                    fill="#eef4ff", stroke=NEG, sw=1.7))
    p.append(text(lx, 132, "294 активні рядки", size=11, color=INK))
    p.append(text(lx, 156, "× 50 півкадрів/с", size=11, color=INK))
    p.append(text(lx, 180, "× 3 відліки в рядку", size=11, color=INK))
    p.append(line(lx - 92, 196, lx + 92, 196, color=NEG, sw=1.2))
    p.append(text(lx, 216, "= 44 100", size=12, color=NEG, bold=True))
    p.append(arrow(lx + 20, 224, joinx - 82, joiny - 6, color=NEG, sw=1.8))

    # права гілка — чорно-білий NTSC
    rx = W - 150
    p.append(fitbox(rx - 70, 60, 140, 46, "NTSC ч/б\n(США)", size=12, bold=True,
                    fill="#eafaf0", stroke=FIELD, sw=1.7))
    p.append(text(rx, 132, "245 активних рядків", size=11, color=INK))
    p.append(text(rx, 156, "× 60 півкадрів/с", size=11, color=INK))
    p.append(text(rx, 180, "× 3 відліки в рядку", size=11, color=INK))
    p.append(line(rx - 92, 196, rx + 92, 196, color=FIELD, sw=1.2))
    p.append(text(rx, 216, "= 44 100", size=12, color=FIELD, bold=True))
    p.append(arrow(rx - 20, 224, joinx + 82, joiny - 6, color=FIELD, sw=1.8))

    p.append(text(W / 2, joiny + 52,
                  "одне число, що влазить у ОБИДВІ відеосистеми — тому його й узяли",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "rates.svg"), W, H, *p,
           title="Звідки 44 100: спільне кратне PAL і NTSC, а не акустика")


# ── clock-domains: два часові домени й нерівність бюджету ──────────────────────
# Ідея (детальна): формалізувати межу з базової як ДВА тактові домени. Ліворуч
# домен заліза (такт f_s, писар DMA), праворуч домен коду (задача-споживач).
# Кільце з M буферів — єдиний місток. Внизу — нерівність, що тримає все: час
# обробки блоку мусить бути НЕ БІЛЬШИЙ за час його наповнення, інакше overrun.

def fig_clock_domains():
    W, H = 760, 360
    p = []
    # дві коробки-домени
    lx, rx, by, bw, bh = 60, 430, 70, 270, 150
    p.append(rect(lx, by, bw, bh, fill="#eef4ff", stroke=NEG, sw=1.8))
    p.append(rect(rx, by, bw, bh, fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(text(lx + bw / 2, by + 24, "домен ЗАЛІЗА", size=13, color=NEG, bold=True))
    p.append(text(lx + bw / 2, by + 44, "такт f_s, писар — DMA", size=10, color=MUTED, italic=True))
    p.append(text(rx + bw / 2, by + 24, "домен КОДУ", size=13, color=FIELD, bold=True))
    p.append(text(rx + bw / 2, by + 44, "задача-споживач, читач", size=10, color=MUTED, italic=True))
    # усередині лівого — писар суне безперервно
    p.append(text(lx + bw / 2, by + 78, "відлік → відлік → відлік", size=11, color=INK))
    p.append(text(lx + bw / 2, by + 100, "паузи НЕМАЄ", size=11, color=NEG, bold=True))
    p.append(text(lx + bw / 2, by + 126, "переповнить — старе затре", size=10, color=MUTED))
    # усередині правого — читач пачками
    p.append(text(rx + bw / 2, by + 78, "забрав блок → обробив", size=11, color=INK))
    p.append(text(rx + bw / 2, by + 100, "у ВЛАСНОМУ темпі", size=11, color=FIELD, bold=True))
    p.append(text(rx + bw / 2, by + 126, "спізнився — розрив у звуці", size=10, color=MUTED))

    # кільце з M буферів — місток посередині
    cx = W / 2
    ring_y = by + bh / 2
    labels = ["A", "B", "C"]
    fills = ["#fff7e6", "#f2ecf8", "#fff7e6"]
    n = len(labels)
    r = 20
    for i, (lab, fl) in enumerate(zip(labels, fills)):
        yy = ring_y - (n - 1) * 30 / 1 / 2 + i * 30
        p.append(circle(cx, yy, r, fill=fl, stroke="#8a5fb0", sw=1.6))
        p.append(text(cx, yy + 5, lab, size=12, color="#8a5fb0", bold=True))
    p.append(text(cx, by - 8, "кільце з M буферів", size=11, color="#8a5fb0", bold=True))
    # стрілки: DMA пише в кільце (зліва), задача читає з кільця (справа)
    p.append(arrow(lx + bw + 3, ring_y - 30, cx - r - 4, ring_y - 30, color=NEG, sw=1.8))
    p.append(arrow(cx + r + 4, ring_y + 30, rx - 3, ring_y + 30, color=FIELD, sw=1.8))
    p.append(text((lx + bw + cx - r) / 2, ring_y - 38, "пише", size=9, color=NEG))
    p.append(text((cx + r + rx) / 2, ring_y + 22, "читає", size=9, color=FIELD))

    # нерівність-бюджет унизу
    p.append(text(W / 2, by + bh + 46,
                  "умова без розривів:   T_обробки  ≤  T_блоку = N / f_s",
                  size=14, color=INK, bold=True))
    p.append(text(W / 2, by + bh + 72,
                  "спізнивсь на цей бюджет — DMA дожене читача → overrun (втрата даних)",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "clock-domains.svg"), W, H, *p,
           title="Два тактові домени: залізо пише, код читає, кільце — місток")


# ── i2s-slot: як 24-бітний відлік лежить у 32-бітному слоті I2S ────────────────
# Ідея (детальна): показати НА РІВНІ БІТІВ, чому сире 32-бітне слово з I2S не
# дорівнює числу-відліку. Відлік вирівняний по старшому біту (MSB-first), сидить
# у старших 24 бітах 32-бітного слота; є зсув на 1 такт від WS; молодші біти —
# сміття/нулі. Щоб дістати int16 — АРИФМЕТИЧНИЙ зсув праворуч на 16.

def fig_i2s_slot():
    W, H = 780, 360
    p = []
    x0, y0 = 90, 120
    cellw, cellh = 18, 36
    # 32 клітинки-біти: старші 24 — корисний відлік, молодші 8 — нулі/шум
    for b in range(32):
        x = x0 + b * cellw
        if b < 24:
            fl, stk = "#eafaf0", FIELD
        else:
            fl, stk = "#f4f6f8", MUTED
        p.append(rect(x, y0, cellw, cellh, fill=fl, stroke=stk, sw=1.0, rx=2))
    grid_r = x0 + 32 * cellw
    # підписи країв (над сіткою, з відступом — лінії сітки їх не торкаються)
    p.append(text(x0, y0 - 46, "MSB (біт 31)", size=10, color=INK, anchor="start"))
    p.append(text(grid_r, y0 - 46, "LSB (біт 0)", size=10, color=INK, anchor="end"))

    # WS-зсув — окремим рядком ЩЕ ВИЩЕ, дві мітки рознесені по краях, без перетину
    p.append(text(x0, y0 - 70, "WS-фронт", size=9, color=NEG, anchor="start"))
    p.append(text(grid_r, y0 - 70, "перший біт слова — через 1 такт SCK", size=9, color=FIELD, anchor="end"))
    # короткі вертикальні позначки НИЖЧЕ рядка тексту, не крізь нього
    p.append(line(x0, y0 - 56, x0, y0 - 50, color=NEG, sw=1.2))
    p.append(line(x0 + cellw, y0 - 56, x0 + cellw, y0 - 50, color=FIELD, sw=1.2))

    # дужки-підписи ПІД сіткою: лінія-дужка й підпис на РІЗНИХ рядках (лінія не ріже текст)
    yb = y0 + cellh + 14
    p.append(line(x0 + 2, yb, x0 + 24 * cellw - 2, yb, color=FIELD, sw=1.8))
    p.append(line(x0 + 24 * cellw + 2, yb, grid_r - 2, yb, color=MUTED, sw=1.8))
    p.append(text(x0 + 12 * cellw, yb + 20, "корисний 24-бітний відлік (старші біти)",
                  size=11, color=FIELD, bold=True))
    p.append(text(x0 + 28 * cellw, yb + 20, "нулі / шум", size=10, color=MUTED))

    # витяг int16 — арифметичний зсув (окремий блок унизу, з великим відступом)
    yq = yb + 60
    p.append(text(W / 2, yq, "дістати int16:   s16 = (int16_t)((int32_t)raw >> 16)",
                  size=13, color=INK, bold=True))
    p.append(text(W / 2, yq + 24,
                  "зсув АРИФМЕТИЧНИЙ (знаковий): інакше від'ємні відліки стануть велетенськими додатними",
                  size=10, color=POS, italic=True))
    render(os.path.join(OUT, "i2s-slot.svg"), W, H, *p,
           title="Сире слово I2S ≠ число: відлік вирівняний по MSB у 32-бітному слоті")


# ── pdm-decimate: 1-бітний потік → фільтр → проріджування → PCM ────────────────
# Ідея (детальна): показати, чому PDM-код НЕ схожий на I2S-код. Мікрофон гатить
# 1-бітний потік на f_pdm = D·f_s; ядро мусить пропустити його через ФНЧ
# (усереднення/CIC), а тоді ПРОРІДИТИ в D разів, щоб дістати PCM на f_s.

def fig_pdm_decimate():
    W, H = 760, 320
    p = []
    cy = 150
    # блоки ланцюга
    blocks = [
        ("PDM-мікрофон", "1-бітний потік\nf_pdm = D · f_s", "#f2ecf8", "#8a5fb0"),
        ("ФНЧ / CIC", "усереднює біти,\nрубає шум угорі", "#eef4ff", NEG),
        ("проріджування", "лишити кожен\nD-тий результат", "#fff7e6", "#b8860b"),
        ("PCM-відлік", "багатобітне\nчисло на f_s", "#eafaf0", FIELD),
    ]
    n = len(blocks)
    bw, bh, gap = 150, 74, 34
    total = n * bw + (n - 1) * gap
    x = (W - total) / 2
    edges = []
    for i, (top, sub, fl, st) in enumerate(blocks):
        p.append(fitbox(x, cy - bh / 2, bw, bh, top + "\n" + sub, size=11, bold=True,
                        fill=fl, stroke=st, sw=1.7))
        edges.append((x, x + bw))
        if i:
            p.append(arrow(edges[i - 1][1] + 3, cy, x - 3, cy, color=INK, sw=1.8))
        x += bw + gap
    # приклад-число під потоком
    p.append(text(edges[0][1] + gap / 2, cy - bh / 2 - 14, "×64", size=10, color="#8a5fb0", bold=True))
    p.append(text(edges[2][0] + bw / 2, cy + bh / 2 + 20, "÷ D", size=11, color="#b8860b", bold=True))
    p.append(text(W / 2, cy + bh / 2 + 58,
                  "приклад:  f_pdm = 3.072 МГц,  D = 64  →  f_s = 48 кГц",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, cy + bh / 2 + 82,
                  "фільтр ОБОВʼЯЗКОВО перед проріджуванням — інакше шум складеться назад у смугу",
                  size=10, color=POS, italic=True))
    render(os.path.join(OUT, "pdm-decimate.svg"), W, H, *p,
           title="PDM → PCM: усереднити 1-бітний потік, тоді проріджити в D разів")


# ── dc-pole: фільтр-«текучий інтегратор» прибирання постійного зсуву ───────────
# Ідея (детальна): показати механіку DC-блокера з базової як частотну відповідь
# ФВЧ і як роль коефіцієнта зсуву (1/2^k). Ліворуч — відповідь: гасить 0 Гц,
# пропускає високе; праворуч — формула зрізу й час усталення від k.

def fig_dc_pole():
    W, H = 760, 330
    p = []
    # ─ ліворуч: АЧХ ФВЧ ─
    ax0, ay0, aw, ah = 70, 90, 300, 150
    p.append(line(ax0, ay0 + ah, ax0 + aw, ay0 + ah, color=INK, sw=1.4))   # вісь X (частота)
    p.append(line(ax0, ay0, ax0, ay0 + ah, color=INK, sw=1.4))              # вісь Y (підсилення)
    p.append(text(ax0 + aw, ay0 + ah + 16, "частота", size=10, color=MUTED, anchor="end"))
    p.append(text(ax0 - 6, ay0 + 4, "1", size=10, color=MUTED, anchor="end"))
    p.append(text(ax0 - 6, ay0 + ah, "0", size=10, color=MUTED, anchor="end"))
    # крива ФВЧ: 0 на 0 Гц, плавно до 1
    import math
    pts = []
    for i in range(0, 81):
        fx = i / 80.0
        g = fx / (fx + 0.12)           # схоже на ФВЧ першого порядку
        px = ax0 + fx * aw
        py = ay0 + ah - g * ah
        pts.append("%.1f,%.1f" % (px, py))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), FIELD))
    # позначити зріз fc
    fcx = ax0 + 0.12 * aw
    p.append(line(fcx, ay0 + ah, fcx, ay0 + ah - 0.5 * ah, color=NEG, sw=1.2, dash="4 3"))
    p.append(text(fcx + 4, ay0 + ah - 0.5 * ah - 6, "f_c", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(ax0 + 4, ay0 - 8, "постійний зсув (0 Гц) — у нуль", size=9, color=MUTED, anchor="start"))
    p.append(text(ax0 + aw / 2, ay0 + ah + 34, "гасить дрейф, пропускає звук", size=10, color=FIELD, italic=True))

    # ─ праворуч: формула зрізу й час усталення ─
    rx0 = 430
    p.append(text(rx0, 110, "текучий інтегратор:", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(rx0, 138, "bias += (x − bias) >> k", size=13, color=INK, anchor="start"))
    p.append(text(rx0, 176, "зріз:   f_c ≈ f_s / (2π · 2^k)", size=13, color=NEG, bold=True, anchor="start"))
    p.append(text(rx0, 210, "більший k → нижчий зріз,", size=11, color=MUTED, anchor="start"))
    p.append(text(rx0, 230, "повільніше усталення (τ ≈ 2^k / f_s)", size=11, color=MUTED, anchor="start"))
    p.append(text(rx0, 262, "k=10, f_s=16 кГц → f_c ≈ 2.5 Гц", size=11, color=INK, bold=True, anchor="start"))
    render(os.path.join(OUT, "dc-pole.svg"), W, H, *p,
           title="Прибирання зсуву — ФВЧ першого порядку: коефіцієнт 1/2^k задає зріз")


# ── pole-zero: z-площина DC-блокера — нуль у z=1, полюс трохи всередині ────────
# Ідея (math-вставка): показати, ЧОМУ це ФВЧ, геометрично. Передавальна
# H(z) = (1 − z⁻¹) / (1 − (1−α)z⁻¹): нуль рівно в z=1 (тобто на 0 Гц підсилення
# = 0), полюс у z = 1−α — трохи всередині кола, майже там-таки. Зазор між ними
# (= α) і є смуга, яку фільтр давить; поза ним модуль ≈ 1.

def fig_pole_zero():
    import math
    W, H = 720, 430
    p = []
    # ─ ліворуч: одиничне коло з нулем і полюсом ─
    cx, cy, R = 200, 210, 128
    p.append(circle(cx, cy, R, fill="#fbfcfe", stroke=MUTED, sw=1.4))
    # осі Re/Im
    p.append(line(cx - R - 26, cy, cx + R + 26, cy, color="#c9ced6", sw=1.1))
    p.append(line(cx, cy - R - 26, cx, cy + R + 30, color="#c9ced6", sw=1.1))
    p.append(text(cx + R + 30, cy + 4, "Re", size=10, color=MUTED, anchor="start"))
    p.append(text(cx + 6, cy - R - 30, "Im", size=10, color=MUTED, anchor="start"))
    p.append(text(cx, cy + 16, "0", size=9, color=MUTED))
    p.append(text(cx + R, cy + 16, "+1", size=9, color=MUTED))
    p.append(text(cx - R, cy + 16, "−1", size=9, color=MUTED))
    # для наочності беремо перебільшене α, щоб полюс і нуль було видно окремо
    a_show = 0.16
    zx = cx + R                    # нуль у z=+1 (на колі)
    px = cx + R * (1 - a_show)     # полюс у z=1−α (трохи всередині)
    # нуль ○ у z=1
    p.append(circle(zx, cy, 7, fill="none", stroke=POS, sw=2.4))
    p.append(text(zx + 6, cy - 58, "нуль  z=1", size=11, color=POS, bold=True, anchor="middle"))
    p.append(text(zx + 6, cy - 44, "(0 Гц → 0)", size=9, color=POS, anchor="middle"))
    p.append(line(zx, cy - 38, zx, cy - 10, color=POS, sw=1.0, dash="2 3"))
    # полюс × у z=1−α
    s = 6
    p.append(line(px - s, cy - s, px + s, cy + s, color=NEG, sw=2.6))
    p.append(line(px - s, cy + s, px + s, cy - s, color=NEG, sw=2.6))
    p.append(text(px - 6, cy + 34, "полюс", size=11, color=NEG, bold=True, anchor="middle"))
    p.append(text(px - 6, cy + 49, "z=1−α", size=10, color=NEG, anchor="middle"))
    p.append(line(px, cy + 10, px, cy + 24, color=NEG, sw=1.0, dash="2 3"))
    # зазор між ними = α (кронштейн НИЖЧЕ осі, окремо від написів нуля)
    gy = cy + 74
    p.append(line(px, gy - 8, px, gy, color="#9aa0aa", sw=1.0))
    p.append(line(zx, gy - 8, zx, gy, color="#9aa0aa", sw=1.0))
    p.append(line(px, gy, zx, gy, color="#9aa0aa", sw=1.0))
    p.append(text((px + zx) / 2, gy + 14, "зазор = α", size=10, color=MUTED))
    p.append(text(cx, cy + R + 48, "нуль і полюс майже злиплись —", size=10, color=MUTED))
    p.append(text(cx, cy + R + 64, "різниця лише у вузькій смузі біля 0 Гц", size=10, color=MUTED))

    # ─ праворуч: точний модуль |H| проти наближення ─
    ax0, ay0, aw, ah = 430, 96, 250, 210
    p.append(line(ax0, ay0, ax0, ay0 + ah, color=MUTED, sw=1.3))
    p.append(line(ax0, ay0 + ah, ax0 + aw, ay0 + ah, color=MUTED, sw=1.3))
    p.append(text(ax0 - 8, ay0 + 6, "1", size=10, color=MUTED, anchor="end"))
    p.append(text(ax0 - 8, ay0 + ah, "0", size=10, color=MUTED, anchor="end"))
    p.append(text(ax0 - 8, ay0 + ah * 0.293, "0.707", size=9, color=MUTED, anchor="end"))
    p.append(line(ax0, ay0 + ah * 0.293, ax0 + aw, ay0 + ah * 0.293, color="#dfe3ea", sw=1.0, dash="4 3"))
    # частотна вісь у частках f_s (лог-подібно, до 0.02·f_s щоб зріз було видно)
    a = 0.16                        # те саме перебільшене α для видимості
    pts = []
    for i in range(0, 121):
        w = (i / 120.0) * 0.5 * math.pi   # ω від 0 до ~0.25·(2π) — вистачає
        # точний модуль однополюсного ФВЧ H(z)=(1−z⁻¹)/(1−(1−α)z⁻¹)
        num = math.sqrt((1 - math.cos(w))**2 + math.sin(w)**2)
        den = math.sqrt((1 - (1 - a) * math.cos(w))**2 + ((1 - a) * math.sin(w))**2)
        g = num / den
        pxp = ax0 + (i / 120.0) * aw
        pyp = ay0 + ah - g * ah
        pts.append("%.1f,%.1f" % (pxp, pyp))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), FIELD))
    # зріз: там, де модуль = 0.707
    # для точного фільтра ω_c розв'язується з рівняння; позначимо приблизну точку
    wc_frac = a / (0.5 * math.pi) / 1.0   # частка осі, груба мітка
    fcx = ax0 + min(0.5, a / (0.5 * math.pi)) * aw * 1.0
    # знайдемо піксель, де крива перетинає 0.707, чесно по точках
    cross = None
    for i in range(1, 121):
        w = (i / 120.0) * 0.5 * math.pi
        num = math.sqrt((1 - math.cos(w))**2 + math.sin(w)**2)
        den = math.sqrt((1 - (1 - a) * math.cos(w))**2 + ((1 - a) * math.sin(w))**2)
        g = num / den
        if g >= 0.70710678:
            cross = ax0 + (i / 120.0) * aw
            break
    if cross:
        p.append(line(cross, ay0 + ah, cross, ay0 + ah * 0.293, color=NEG, sw=1.2, dash="4 3"))
        p.append(text(cross + 4, ay0 + ah * 0.293 - 6, "f_c", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(ax0, ay0 - 10, "|H(f)| — точний модуль ФВЧ 1-го порядку", size=10, color=INK, anchor="start"))
    p.append(text(ax0 + aw / 2, ay0 + ah + 22, "частота →", size=10, color=MUTED))
    p.append(text(ax0 + aw / 2, ay0 + ah + 40, "від f_c і вище |H|≈1 — звук іде як є", size=10, color=FIELD, italic=True))
    render(os.path.join(OUT, "pole-zero.svg"), W, H, *p,
           title="DC-блокер на z-площині: нуль у z=1, полюс у z=1−α")


# ── dead-band: чому БЕЗ фіксованої коми фільтр сам додає шум ───────────────────
# Ідея (math-вставка): показати мертву зону цілочислового bias. Порівнюємо два
# треки bias при сталому вході x=500.5: 16.16 (bias плавно доповзає й СТОЇТЬ) і
# цілочисловий (bias не може стати на 500.5, тому вічно скаче 500↔501 — це шум,
# що фільтр САМ інжектує на кожному кроці).

def fig_dead_band():
    W, H = 720, 360
    p = []
    ax0, ay0, aw, ah = 70, 70, 600, 210
    # осі
    p.append(line(ax0, ay0, ax0, ay0 + ah, color=MUTED, sw=1.3))
    p.append(line(ax0, ay0 + ah, ax0 + aw, ay0 + ah, color=MUTED, sw=1.3))
    p.append(text(ax0 + aw / 2, ay0 + ah + 40, "крок n (час) →", size=11, color=MUTED))
    p.append(text(ax0 - 40, ay0 + ah / 2, "bias", size=11, color=MUTED))
    # рівень цілі x = 500.5 — між двома цілими
    base = ay0 + ah - 40
    y500 = base
    y501 = base - 40
    ytgt = (y500 + y501) / 2
    p.append(line(ax0, ytgt, ax0 + aw, ytgt, color="#c9ced6", sw=1.1, dash="5 4"))
    p.append(text(ax0 + aw + 4, ytgt + 4, "ціль 500.5", size=10, color=MUTED, anchor="start"))
    p.append(line(ax0, y500, ax0 + 10, y500, color="#dfe3ea", sw=1.0))
    p.append(line(ax0, y501, ax0 + 10, y501, color="#dfe3ea", sw=1.0))
    p.append(text(ax0 - 8, y500 + 4, "500", size=9, color=MUTED, anchor="end"))
    p.append(text(ax0 - 8, y501 + 4, "501", size=9, color=MUTED, anchor="end"))
    # 16.16: плавно доповзає до 500.5 і СТОЇТЬ
    import math
    pts = []
    for i in range(0, 61):
        t = i / 60.0
        val = 1.0 - math.exp(-3.2 * t)       # доповз від 0 (тут — від низу графіка)
        yy = base + 30 - val * (base + 30 - ytgt)
        xx = ax0 + t * aw
        pts.append("%.1f,%.1f" % (xx, yy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), FIELD))
    p.append(text(ax0 + aw - 4, ytgt - 10, "16.16: доповз і стоїть на 500.5", size=11, color=FIELD, bold=True, anchor="end"))
    # цілочисловий: доповзає, а далі вічний скач 500↔501
    pts2 = []
    for i in range(0, 61):
        t = i / 60.0
        xx = ax0 + t * aw
        if t < 0.42:
            val = 1.0 - math.exp(-3.4 * t)
            yy = base + 30 - val * (base + 30 - y500)
        else:
            yy = y500 if (i % 2 == 0) else y501     # limit-cycle: туди-сюди
        pts2.append("%.1f,%.1f" % (xx, yy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join(pts2), POS))
    p.append(text(ax0 + 8, y501 - 12, "ціле: не влучає в 500.5 → вічний скач 500↔501", size=11, color=POS, bold=True, anchor="start"))
    # підпис-висновок під графіком
    p.append(text(W / 2, ay0 + ah + 66,
                  "скач на ±1 відлік щокроку — це шум, який фільтр САМ додає до тиші",
                  size=11, color=INK, italic=True))
    render(os.path.join(OUT, "dead-band.svg"), W, H, *p,
           title="Мертва зона цілочислового bias: без дробу фільтр інжектує шум")


# ── boxcar-droop: чому просте усереднення завалює верх смуги ───────────────────
# Ідея (proj-pdm-decimation): показати ЧАСТОТНУ відповідь одноблокового
# усереднення — sinc. Нулі стоять на кратних f_pdm/D; ПЕРШИЙ нуль лягає на краю
# смуги, куди складеться аліас. Але ще ДО нуля крива вже помітно осідає — це
# «завал» (droop): корисні високі частоти гасяться сильніше за низькі. Права
# частина: каскад N усереднень робить стінку крутішою (краще ловить аліас), але
# й завал глибшим — звідси потреба в компенсаторі.

def fig_boxcar_droop():
    W, H = 760, 360
    import math
    p = []
    ax0, ay0, aw, ah = 80, 84, 600, 176

    p.append(line(ax0, ay0 + ah, ax0 + aw, ay0 + ah, color=INK, sw=1.4))
    p.append(line(ax0, ay0, ax0, ay0 + ah, color=INK, sw=1.4))
    p.append(text(ax0 - 8, ay0 + 6, "1", size=10, color=MUTED, anchor="end"))
    p.append(text(ax0 - 8, ay0 + ah, "0", size=10, color=MUTED, anchor="end"))
    p.append(text(ax0 + aw, ay0 + ah + 30, "частота  (частка від f_pdm)", size=10, color=MUTED, anchor="end"))

    D_show = 6.0
    def sinc_mag(fx, stages):
        if fx == 0:
            m = 1.0
        else:
            num = math.sin(math.pi * D_show * fx)
            den = D_show * math.sin(math.pi * fx)
            m = abs(num / den) if abs(den) > 1e-9 else 1.0
        return m ** stages

    def curve(stages, color, sw):
        pts = []
        for i in range(0, 601):
            fx = 0.5 * i / 600.0
            m = sinc_mag(fx, stages)
            px = ax0 + (fx / 0.5) * aw
            py = ay0 + ah - m * ah
            pts.append("%.1f,%.1f" % (px, py))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                % (" ".join(pts), color, sw))

    band_x = ax0 + ((1.0 / D_show / 2) / 0.5) * aw
    p.append(rect(ax0, ay0, band_x - ax0, ah, fill="#eafaf0", stroke="none", sw=0))
    p.append(text((ax0 + band_x) / 2, ay0 - 12, "корисна смуга", size=10, color=FIELD, bold=True))

    null_x = ax0 + ((1.0 / D_show) / 0.5) * aw
    p.append(line(null_x, ay0, null_x, ay0 + ah, color=NEG, sw=1.2, dash="4 3"))
    p.append(text(null_x + 5, ay0 + 16, "1-й нуль: f_pdm/D", size=10, color=NEG, anchor="start"))
    p.append(text(null_x + 5, ay0 + 32, "сюди складеться аліас", size=9, color=NEG, anchor="start"))

    p.append(curve(1, FIELD, 2.4))
    p.append(curve(4, POS, 2.0))
    droop_m1 = sinc_mag(1.0 / D_show / 2, 1)
    dy = ay0 + ah - droop_m1 * ah
    p.append(circle(band_x, dy, 3.5, fill=BG, stroke=FIELD, sw=1.6))
    p.append(text(band_x + 8, dy - 8, "верх смуги вже осів", size=9, color=FIELD, anchor="start"))

    p.append(line(ax0 + 20, ay0 + ah + 52, ax0 + 50, ay0 + ah + 52, color=FIELD, sw=2.4))
    p.append(text(ax0 + 56, ay0 + ah + 56, "одне усереднення (N=1): стінка полога, завал м'який",
                  size=10, color=INK, anchor="start"))
    p.append(line(ax0 + 20, ay0 + ah + 74, ax0 + 50, ay0 + ah + 74, color=POS, sw=2.4))
    p.append(text(ax0 + 56, ay0 + ah + 78, "каскад N=4: стінка крутіша (краще ловить аліас), зате завал глибший",
                  size=10, color=INK, anchor="start"))
    render(os.path.join(OUT, "boxcar-droop.svg"), W, H, *p,
           title="Усереднення — це sinc: нулі на f_pdm/D, а верх смуги вже завалений")


# ── cic-structure: інтегратори на високій частоті, ÷D, гребінки на низькій ──────
# Ідея (proj-pdm-decimation): показати, ЧОМУ CIC дешевий. Ліворуч N інтеграторів
# крутяться на ПОВНІЙ f_pdm, але кожен — лише один додавач (накопичення).
# Посередині ÷D викидає зайве. Праворуч N гребінок працюють уже на НИЗЬКІЙ f_s,
# кожна — одне віднімання відкладеного відліку. Множень немає ніде.

def fig_cic_structure():
    W, H = 780, 300
    p = []
    cy = 120
    bw, bh = 96, 58

    ix = 74
    p.append(fitbox(ix, cy - bh / 2, bw, bh, "інтегратор\n(+)", size=12, bold=True,
                    fill="#eef4ff", stroke=NEG, sw=1.7))
    p.append(fitbox(ix + bw + 24, cy - bh / 2, bw, bh, "інтегратор\n(+)", size=12, bold=True,
                    fill="#eef4ff", stroke=NEG, sw=1.7))
    ix2r = ix + 2 * bw + 24
    dx = ix2r + 30
    p.append(fitbox(dx, cy - bh / 2, 66, bh, "÷ D", size=15, bold=True,
                    fill="#fff7e6", stroke="#b8860b", sw=1.9))
    dxr = dx + 66
    gx = dxr + 30
    p.append(fitbox(gx, cy - bh / 2, bw, bh, "гребінка\n(−)", size=12, bold=True,
                    fill="#eafaf0", stroke=FIELD, sw=1.7))
    p.append(fitbox(gx + bw + 24, cy - bh / 2, bw, bh, "гребінка\n(−)", size=12, bold=True,
                    fill="#eafaf0", stroke=FIELD, sw=1.7))
    gx2r = gx + 2 * bw + 24

    p.append(text(ix - 34, cy - 14, "1 біт", size=10, color="#8a5fb0", bold=True, anchor="middle"))
    p.append(arrow(ix - 22, cy, ix - 2, cy, color=INK, sw=1.8))
    p.append(arrow(ix + bw + 2, cy, ix + bw + 22, cy, color=INK, sw=1.8))
    p.append(arrow(ix2r + 2, cy, dx - 2, cy, color=INK, sw=1.8))
    p.append(arrow(dxr + 2, cy, gx - 2, cy, color=INK, sw=1.8))
    p.append(arrow(gx + bw + 2, cy, gx + bw + 22, cy, color=INK, sw=1.8))
    p.append(arrow(gx2r + 2, cy, gx2r + 22, cy, color=INK, sw=1.8))
    p.append(text(gx2r + 46, cy - 14, "PCM", size=10, color=FIELD, bold=True, anchor="middle"))

    yb = cy - bh / 2 - 24
    p.append(line(ix, yb, ix2r, yb, color=NEG, sw=1.6))
    p.append(text((ix + ix2r) / 2, yb - 8, "на ПОВНІЙ f_pdm — лише додавання", size=10, color=NEG, bold=True))
    p.append(line(gx, yb, gx2r, yb, color=FIELD, sw=1.6))
    p.append(text((gx + gx2r) / 2, yb - 8, "на НИЗЬКІЙ f_s — лише віднімання", size=10, color=FIELD, bold=True))

    p.append(text(W / 2, cy + bh / 2 + 40,
                  "жодного множення на всьому шляху — тільки + та −",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, cy + bh / 2 + 62,
                  "порядок навмисний: дорогі за темпом інтегратори прості; гребінки ставимо ПІСЛЯ ÷D",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "cic-structure.svg"), W, H, *p,
           title="CIC: інтегратори на f_pdm, ÷D, гребінки на f_s — без жодного множення")


if __name__ == "__main__":
    fig_pipeline()
    fig_sources()
    fig_latency()
    fig_rates()
    fig_clock_domains()
    fig_i2s_slot()
    fig_pdm_decimate()
    fig_dc_pole()
    fig_pole_zero()
    fig_dead_band()
    fig_boxcar_droop()
    fig_cic_structure()
    print("OK: figures written to", OUT)
