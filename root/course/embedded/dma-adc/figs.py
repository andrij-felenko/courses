# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── chain: таймер → АЦП → DMA → кільцевий буфер → ISR → задача ────────────────
# Ідея: показати, що ядро не торкається жодного окремого виміру — увесь шлях
# семпла від темпу до буфера апаратний, а ядро вмикається лише на готовий блок.

def fig_chain():
    W, H = 760, 300
    p = []
    y = 110
    bw, bh = 116, 64
    gap = 12
    x = 28
    boxes = [
        ("таймер\nтемп f_s", "#eaf0fd", NEG),
        ("АЦП\nкод вибірки", "#fff9e6", "#8a6200"),
        ("DMA\nперенос слова", "#d4edda", FIELD),
        ("кільцевий\nбуфер у SRAM", FILL, MUTED),
        ("задача RTOS\nобробка блоку", "#eaf0fd", NEG),
    ]
    edge = []
    for i, (lab, fill, col) in enumerate(boxes):
        p.append(fitbox(x, y - bh / 2, bw, bh, lab, size=12, fill=fill, stroke=col, sw=2, bold=True))
        edge.append((x, x + bw))
        if i > 0:
            p.append(arrow(edge[i - 1][1] + 1, y, x - 1, y, color=INK, sw=1.8))
        x += bw + gap

    # підписи на стрілках — що саме передається
    cap = ["тік 1/f_s", "DMA-запит\nна семпл", "слово в слот", "half/full ISR"]
    for i, c in enumerate(cap):
        mx = (edge[i][1] + edge[i + 1][0]) / 2
        p.append(mtext(mx, y + bh / 2 + 18, c, size=9, color=MUTED))

    # нижня плашка: де вмикається ядро
    p.append(line(edge[2][0], y + bh / 2 + 46, edge[4][1], y + bh / 2 + 46, color="#cbd5e1", sw=1.0))
    note, nw, nh = textbox(W / 2, 244, "ядро вмикається раз на блок, а не на кожен вимір",
                           size=12, color=INK, fill="#eafaf0", stroke=FIELD, sw=1.6, bold=True)
    p.append(note)
    # дужка над апаратною частиною
    hx0, hx1 = edge[0][0], edge[2][1]
    p.append(line(hx0, 64, hx1, 64, color=POS, sw=1.4))
    p.append(line(hx0, 64, hx0, 70, color=POS, sw=1.4))
    p.append(line(hx1, 64, hx1, 70, color=POS, sw=1.4))
    p.append(text((hx0 + hx1) / 2, 58, "усе апаратно — без ядра", size=11, color=POS, bold=True))

    render(os.path.join(OUT, "chain.svg"), W, H, *p,
           title="Безперервний потік: темп → вибірка → перенос → буфер → задача")


# ── sample-word: бітові поля одного слова потоку (код + канал) ─────────────────
# Ідея: семпл у потоці — не голе 12-бітне число, а слово, де поряд лежать код
# вимірювання й номер каналу; ядро розкладає масив таких слів формулою.

def fig_sample_word():
    W, H = 700, 280
    p = []
    bx, by = 70, 96
    cell = 36
    bh = 56
    # 16 клітинок зліва направо: біти 15..0
    labels = list(range(15, -1, -1))
    for i, b in enumerate(labels):
        x = bx + i * cell
        if b <= 11:
            fill, col = "#eaf0fd", NEG          # код 0..11
        else:
            fill, col = "#fdecea", POS          # канал 12..15
        p.append(rect(x, by, cell, bh, fill=fill, stroke=col, sw=1.4, rx=0))
        p.append(text(x + cell / 2, by + bh + 14, str(b), size=9, color=MUTED))

    # підписи груп
    p.append(line(bx, by - 10, bx + 12 * cell, by - 10, color=NEG, sw=1.6))
    p.append(text(bx + 6 * cell, by - 16, "val : 12  — код 0..4095", size=12, color=NEG, bold=True))
    p.append(line(bx + 12 * cell, by - 10, bx + 16 * cell, by - 10, color=POS, sw=1.6))
    p.append(text(bx + 14 * cell, by - 16, "channel : 4", size=11, color=POS, bold=True))

    # формула розпакування внизу
    f, fw, fh = textbox(W / 2, 224, "Vin = код × Vref / (2¹² − 1)",
                        size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=1.6, pad=12)
    p.append(f)
    p.append(text(W / 2, 256, "ядро розкладає масив таких слів у пари (канал, вольти)",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "sample-word.svg"), W, H, *p,
           title="Одне слово потоку: код вибірки + номер каналу в бітових полях")


# ── wakeup: та сама частота семплів — у сотні разів менше пробуджень ядра ──────
# Ідея: порівняти густу гребінку переривань analogRead із рідкими мітками
# «пів-буфера» при АЦП+DMA на тому самому потоці.

def fig_wakeup():
    W, H = 700, 300
    p = []
    x0, x1 = 70, 640

    # верх: analogRead — густа гребінка
    yA = 96
    p.append(text(x0, yA - 30, "analogRead у циклі: переривання на кожен вимір",
                  size=12, color=POS, anchor="start", bold=True))
    p.append(line(x0, yA, x1, yA, color=INK, sw=1.6))
    nA = 48
    for i in range(nA + 1):
        x = x0 + i * (x1 - x0) / nA
        p.append(line(x, yA - 12, x, yA, color=POS, sw=1.4))
    p.append(text(x1, yA - 18, "густо", size=11, color=POS, anchor="end"))

    # низ: АЦП+DMA — рідкі мітки (пів-буфера)
    yB = 196
    p.append(text(x0, yB - 30, "АЦП + DMA: один сигнал на пів-буфера",
                  size=12, color=FIELD, anchor="start", bold=True))
    p.append(line(x0, yB, x1, yB, color=INK, sw=1.6))
    nB = 4
    for i in range(nB + 1):
        x = x0 + i * (x1 - x0) / nB
        p.append(line(x, yB - 18, x, yB, color=FIELD, sw=2.4))
        if i < nB:
            mid = x0 + (i + 0.5) * (x1 - x0) / nB
            p.append(text(mid, yB + 18, "пів-буфера", size=9, color=MUTED))
    p.append(text(x1, yB - 24, "рідко", size=11, color=FIELD, anchor="end"))

    p.append(text(W / 2, 264, "той самий потік — на два-три порядки менше переривань",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "wakeup.svg"), W, H, *p,
           title="Та сама частота вибірок — у сотні разів менше пробуджень ядра")


# ── gdma-ring: кільце DMA-дескрипторів (DW0/DW1/DW2, біт owner, EOF по колу) ───
# Ідея (детальна): показати, ЩО насправді робить «кільцевий буфер» на рівні
# заліза — не один масив, а замкнене кільце дескрипторів, кожен із яких віддає
# власність (owner) то контролеру, то ядру, і suc_eof по колу вертає на початок.

def fig_gdma_ring():
    W, H = 760, 380
    p = []
    cx, cy = 300, 200
    r = 118
    n = 4
    bw, bh = 150, 74
    import math as _m
    centers = []
    for i in range(n):
        a = -_m.pi / 2 + i * 2 * _m.pi / n
        centers.append((cx + r * _m.cos(a), cy + r * _m.sin(a)))

    # стрілки по колу (за годинниковою) — «next descriptor»
    for i in range(n):
        x0c, y0c = centers[i]
        x1c, y1c = centers[(i + 1) % n]
        # тягнемо від краю поточного до краю наступного
        dx, dy = x1c - x0c, y1c - y0c
        d = _m.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        sx, sy = x0c + ux * (bw / 2 + 6), y0c + uy * (bh / 2 - 4)
        ex, ey = x1c - ux * (bw / 2 + 6), y1c - uy * (bh / 2 - 4)
        p.append(arrow(sx, sy, ex, ey, color=NEG, sw=1.8))

    labels = [
        ("дескриптор 0", "buf[0]", "owner=DMA", FIELD, "#d4edda"),
        ("дескриптор 1", "buf[1]", "owner=CPU", POS, "#fdecea"),
        ("дескриптор 2", "buf[2]", "owner=DMA", FIELD, "#d4edda"),
        ("дескриптор 3", "buf[3]", "owner=DMA", FIELD, "#d4edda"),
    ]
    for i, (t1, t2, t3, col, fl) in enumerate(labels):
        x0c, y0c = centers[i]
        p.append(fitbox(x0c - bw / 2, y0c - bh / 2, bw, bh,
                        t1 + "\n" + t2 + "  ·  " + t3,
                        size=12, fill=fl, stroke=col, sw=2, bold=True))

    # підпис у центрі — suc_eof вертає на 0
    p.append(text(cx, cy - 8, "suc_eof", size=12, color=MUTED, bold=True))
    p.append(text(cx, cy + 10, "останній →", size=10, color=MUTED))
    p.append(text(cx, cy + 24, "знову на 0", size=10, color=MUTED))

    # права колонка: розкладка одного дескриптора (три слова)
    dx0 = 508
    p.append(text(dx0 + 110, 66, "один дескриптор = 3 слова", size=12, color=INK, bold=True))
    rows = [
        ("DW0", "owner · suc_eof · size[11:0]", "#eaf0fd"),
        ("DW1", "адреса буфера (внутрішня RAM)", "#f6f4ec"),
        ("DW2", "адреса наступного дескриптора", "#f6f4ec"),
    ]
    ry = 92
    for tag, desc, fl in rows:
        p.append(rect(dx0, ry, 60, 44, fill="#fff", stroke=INK, sw=1.4))
        p.append(text(dx0 + 30, ry + 27, tag, size=12, color=INK, bold=True))
        p.append(fitbox(dx0 + 66, ry, 178, 44, desc, size=10, fill=fl, stroke=MUTED, sw=1.2))
        ry += 54

    note, _, _ = textbox(dx0 + 122, 292,
                         "owner=1 → черга DMA;\nowner=0 → ядро читає",
                         size=11, color=INK, fill="#eafaf0", stroke=FIELD, sw=1.4, bold=True)
    p.append(note)

    render(os.path.join(OUT, "gdma-ring.svg"), W, H, *p,
           title="Кільце DMA-дескрипторів: власність ходить між DMA і ядром")


# ── deadline: перегони «DMA наповнює» ↔ «задача спорожнює», лінія дедлайну ─────
# Ідея (детальна): показати числовий сенс подвійного буфера як ДЕДЛАЙН —
# задача мусить спорожнити половину раніше, ніж DMA наповнить сусідню; якщо ні —
# overrun: DMA доганяє ще не прочитану комірку.

def fig_deadline():
    W, H = 760, 340
    p = []
    x0, x1 = 70, 690
    span = x1 - x0
    # два періоди half-заповнення
    t_half = span / 2

    # верх: DMA заповнює A, потім B (безперервно, рівно)
    yD = 96
    p.append(text(x0, yD - 26, "DMA наповнює половину за t_half (рівно, апаратно)",
                  size=12, color=NEG, anchor="start", bold=True))
    p.append(rect(x0, yD, t_half, 30, fill="#eaf0fd", stroke=NEG, sw=1.6))
    p.append(text(x0 + t_half / 2, yD + 20, "пише A", size=11, color=NEG, bold=True))
    p.append(rect(x0 + t_half, yD, t_half, 30, fill="#dce6fb", stroke=NEG, sw=1.6))
    p.append(text(x0 + t_half + t_half / 2, yD + 20, "пише B", size=11, color=NEG, bold=True))

    # дедлайн-лінія: кінець заповнення A = дедлайн обробки A
    xd = x0 + t_half
    p.append(line(xd, yD - 6, xd, 250, color=POS, sw=1.8, dash="5,4"))
    p.append(text(xd, 262, "дедлайн: A має бути прочитана", size=11, color=POS, bold=True))

    # низ (успіх): задача читає A за t_proc < t_half
    yT = 176
    p.append(text(x0, yT - 26, "Задача обробляє половину за t_proc",
                  size=12, color=FIELD, anchor="start", bold=True))
    tp = t_half * 0.62
    p.append(rect(x0 + t_half, yT, tp, 26, fill="#d4edda", stroke=FIELD, sw=1.6))
    p.append(text(x0 + t_half + tp / 2, yT + 18, "читає A", size=11, color=FIELD, bold=True))
    # запас
    p.append(line(x0 + t_half + tp, yT + 13, x0 + 2 * t_half, yT + 13, color=MUTED, sw=1.2, dash="3,3"))
    p.append(text(x0 + t_half + tp + (t_half - tp) / 2, yT - 4, "запас", size=10, color=MUTED, italic=True))

    p.append(text(W / 2, 300, "умова без втрат:  t_proc < t_half  =  (N/2) / f_s",
                  size=13, color=INK, bold=True))
    p.append(text(W / 2, 322, "не встиг до пунктиру → overrun: DMA перезаписує ще не прочитану комірку",
                  size=11, color=POS, italic=True))

    render(os.path.join(OUT, "deadline.svg"), W, H, *p,
           title="Подвійний буфер як дедлайн: спорожнити раніше, ніж наповниться сусід")


# ── jitter-src: де DMA прибирає тремтіння, а де ні (софт vs апертура) ──────────
# Ідея (детальна): jitter має ДВА джерела. Софтовий (analogRead) — великий,
# DMA його прибирає; апертурний (тактовий генератор + S/H) — малий, лишається.
# DMA не робить крок ідеальним, лише переносить межу точності на кварц.

def fig_jitter_src():
    W, H = 720, 330
    p = []
    x0, x1 = 60, 660
    ticks = 8
    step = (x1 - x0) / ticks

    # ідеальна сітка
    yG = 300
    for i in range(ticks + 1):
        x = x0 + i * step
        p.append(line(x, yG - 8, x, yG, color="#cbd5e1", sw=1.0))
    p.append(text(x1, yG + 16, "ідеальний крок 1/f_s", size=10, color=MUTED, anchor="end"))

    # верх: софтовий джиттер — великий розкид міток
    yA = 108
    p.append(text(x0, yA - 28, "analogRead: софтовий джиттер — ядро відволікається",
                  size=12, color=POS, anchor="start", bold=True))
    p.append(line(x0, yA, x1, yA, color=INK, sw=1.4))
    off = [0, 0.32, -0.18, 0.5, 0.12, -0.35, 0.44, -0.1, 0.0]
    for i in range(ticks + 1):
        x = x0 + i * step + off[i] * step * 0.9
        p.append(line(x, yA - 14, x, yA, color=POS, sw=1.8))
        xi = x0 + i * step
        p.append(line(xi, yA, xi, yG, color="#e5e7eb", sw=0.8, dash="2,3"))
    p.append(text(x1, yA - 20, "великий розкид", size=10, color=POS, anchor="end"))

    # низ: DMA — крок від кварцу, лишається тільки апертурний джиттер
    yB = 200
    p.append(text(x0, yB - 28, "АЦП+DMA: крок від кварцу, лишається лише апертурний джиттер",
                  size=12, color=FIELD, anchor="start", bold=True))
    p.append(line(x0, yB, x1, yB, color=INK, sw=1.4))
    offb = [0, 0.03, -0.02, 0.04, -0.03, 0.02, -0.02, 0.03, 0.0]
    for i in range(ticks + 1):
        x = x0 + i * step + offb[i] * step
        p.append(line(x, yB - 14, x, yB, color=FIELD, sw=1.8))
    p.append(text(x1, yB - 20, "майже на сітці", size=10, color=FIELD, anchor="end"))

    render(os.path.join(OUT, "jitter-src.svg"), W, H, *p,
           title="Два джерела тремтіння: софтове DMA прибирає, апертурне лишає")


# ── scan-skew: багатоканальне сканування — часовий зсув між каналами ──────────
# Ідея (детальна): у scan-режимі канали міряються ПО ЧЕРЗІ, тож у «одному кадрі»
# вибірки різних каналів зняті в різні моменти — між CH0 і CH2 є реальний зсув Δt.

def fig_scan_skew():
    W, H = 720, 300
    p = []
    x0 = 70
    slot = 82
    chans = ["CH0", "CH1", "CH2", "CH0", "CH1", "CH2"]
    cols = {"CH0": ("#eaf0fd", NEG), "CH1": ("#fff9e6", "#8a6200"), "CH2": ("#d4edda", FIELD)}
    y = 110
    bh = 52
    for i, ch in enumerate(chans):
        x = x0 + i * slot
        fl, col = cols[ch]
        p.append(fitbox(x, y, slot - 10, bh, ch, size=13, fill=fl, stroke=col, sw=1.8, bold=True))
        # мітка часу вибірки
        p.append(line(x + (slot - 10) / 2, y + bh, x + (slot - 10) / 2, y + bh + 12, color=MUTED, sw=1.0))
        p.append(text(x + (slot - 10) / 2, y + bh + 26, "t%d" % i, size=10, color=MUTED))

    # рамка «один кадр сканування» навколо перших трьох
    fx0 = x0 - 4
    fx1 = x0 + 3 * slot - 10 + 4
    p.append(rect(fx0, y - 14, fx1 - fx0, bh + 28, fill="none", stroke=INK, sw=1.4, rx=8))
    p.append(text((fx0 + fx1) / 2, y - 22, "один кадр (CH0..CH2)", size=11, color=INK, bold=True))

    # стрілка зсуву Δt між CH0 і CH2 у кадрі
    a0 = x0 + (slot - 10) / 2
    a2 = x0 + 2 * slot + (slot - 10) / 2
    yy = y + bh + 44
    p.append(arrow(a0, yy, a2, yy, color=POS, sw=1.6))
    p.append(arrow(a2, yy, a0, yy, color=POS, sw=1.6))
    p.append(text((a0 + a2) / 2, yy - 6, "Δt = 2 / f_s — зсув між каналами в кадрі", size=11, color=POS, bold=True))

    p.append(text(W / 2, 268, "канали зняті НЕ одночасно: у частотному аналізі це фазовий зсув",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "scan-skew.svg"), W, H, *p,
           title="Сканування каналів по черзі: часовий зсув усередині кадру")


# ── sample-formats: TYPE1 (16 біт) vs TYPE2 (32 біти) поряд ────────────────────
# Ідея (вставка): показати обидва слова вибірки в одному масштабі — 16-бітне
# TYPE1 (data:12 + channel:4, без unit) і 32-бітне TYPE2 (data:12 + резерв +
# channel + unit + резерв). Видно, ЧОМУ unit-біт живе лише в широкому слові:
# у 16 бітах місця під нього просто немає.

def _bitrow(p, x0, y, cell, bh, spans):
    """Намалювати рядок бітових полів. spans = [(ширина, підпис, fill, col), ...]
    зліва (старші біти) направо; повертає праву межу рядка."""
    x = x0
    for w, lab, fill, col in spans:
        ww = w * cell
        p.append(rect(x, y, ww, bh, fill=fill, stroke=col, sw=1.4, rx=0))
        # напис поля всередині, якщо влазить; шрифт підбирає fitbox неявно
        fs = fit_font(lab, ww - 6, 11, bold=True)
        p.append(text(x + ww / 2, y + bh / 2 + fs * 0.35, lab, size=fs, color=col, bold=True))
        x += ww
    return x


def fig_sample_formats():
    W, H = 760, 430
    p = []
    cell = 20                     # ширина одного біта в px (32 біти × 20 = 640)
    x0 = 60
    bh = 46

    # ── TYPE1: 16-бітне слово (ESP32 / ESP32-S2), RESULT_BYTES = 2 ──
    yT1 = 92
    p.append(text(x0, yT1 - 26, "TYPE1  ·  uint16_t  ·  SOC_ADC_DIGI_RESULT_BYTES = 2",
                  size=13, color=INK, anchor="start", bold=True))
    # 16 біт займають ліві 16 клітинок; праву половину лишаємо порожньою (нема слова)
    _bitrow(p, x0, yT1, cell, bh, [
        (4, "channel:4", "#fdecea", POS),
        (12, "data:12  (код 0..4095)", "#eaf0fd", NEG),
    ])
    # мітка «цих бітів просто немає»
    ghost_x = x0 + 16 * cell
    p.append(rect(ghost_x, yT1, 16 * cell, bh, fill="#f4f6f8", stroke="#cbd5e1", sw=1.2, rx=0))
    p.append(text(ghost_x + 8 * cell, yT1 + bh / 2 + 4, "цих 16 бітів немає — слово вужче",
                  size=11, color=MUTED, italic=True))
    p.append(text(x0, yT1 + bh + 18, "ESP32, ESP32-S2  ·  unit-біта нема: DMA лише на ADC1",
                  size=11, color=MUTED, anchor="start"))

    # ── TYPE2: 32-бітне слово (S3 / C3 / C6 …), RESULT_BYTES = 4 ──
    yT2 = 230
    p.append(text(x0, yT2 - 26, "TYPE2  ·  uint32_t  ·  SOC_ADC_DIGI_RESULT_BYTES = 4",
                  size=13, color=INK, anchor="start", bold=True))
    _bitrow(p, x0, yT2, cell, bh, [
        (14, "reserved:14", "#f4f6f8", MUTED),
        (1, "u", "#eafaf0", FIELD),
        (4, "channel:4", "#fdecea", POS),
        (1, "r", "#f4f6f8", MUTED),
        (12, "data:12  (код 0..4095)", "#eaf0fd", NEG),
    ])
    p.append(text(x0, yT2 + bh + 18,
                  "ESP32-S3/C3/C6/H2/P4  ·  u = unit: 0=ADC1, 1=ADC2 — місце під нього є",
                  size=11, color=MUTED, anchor="start"))

    # виноска на unit-біт (він стоїть після reserved:14, тобто над 15-ю клітинкою)
    ux = x0 + 14 * cell + cell / 2
    p.append(line(ux, yT2, ux, yT2 - 12, color=FIELD, sw=1.6))
    p.append(text(ux, yT2 - 16, "unit", size=10, color=FIELD, bold=True))

    # спільний висновок унизу
    concl, cw, ch = textbox(W / 2, 372,
                            "код і канал — в обох; unit розрізняє ADC1/ADC2 лише там, де слово 32-бітне",
                            size=12, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.6, pad=12)
    p.append(concl)
    p.append(text(W / 2, 406, "молодші 12 бітів — завжди код вибірки; решта розкладки залежить від класу формату",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "sample-formats.svg"), W, H, *p,
           title="Два формати слова вибірки: вузьке TYPE1 і широке TYPE2")


# ── unpack-stride: чому sizeof бреше і чому крок беруть із константи чіпа ───────
# Ідея (вставка): та сама пам'ять, два трактування кроку. Хардкод «крок = 2»
# на TYPE2 читає кожне друге слово й ловить сміття між ними; крок із
# SOC_ADC_DIGI_RESULT_BYTES потрапляє рівно у кожну вибірку.

def fig_unpack_stride():
    W, H = 760, 360
    p = []
    x0 = 40
    byte = 30                      # ширина одного байта в px
    bh = 40
    nbytes = 16                    # показуємо 16 байтів пам'яті = 4 вибірки TYPE2

    # спільна стрічка байтів пам'яті (TYPE2: по 4 байти на вибірку)
    ymem = 128
    p.append(text(x0, ymem - 16, "пам'ять від DMA (формат TYPE2: 4 байти на вибірку)",
                  size=12, color=INK, anchor="start", bold=True))
    for i in range(nbytes):
        x = x0 + i * byte
        # межі вибірок кожні 4 байти — товщою лінією
        sample_start = (i % 4 == 0)
        fill = "#eaf0fd" if (i % 4 < 2) else "#eef2f7"
        p.append(rect(x, ymem, byte, bh, fill=fill, stroke="#9fb3d1", sw=1.2, rx=0))
        p.append(text(x + byte / 2, ymem + bh + 12, "B%d" % i, size=8, color=MUTED))
    # позначки справжніх меж вибірок
    for s in range(nbytes // 4):
        x = x0 + s * 4 * byte
        p.append(line(x, ymem - 4, x, ymem + bh + 4, color=INK, sw=2.0))
        p.append(text(x + 2 * byte, ymem - 4, "вибірка %d" % s, size=9, color=INK, bold=True))
    p.append(line(x0 + nbytes * byte, ymem - 4, x0 + nbytes * byte, ymem + bh + 4, color=INK, sw=2.0))

    # ── зверху: ХИБНИЙ крок 2 (sizeof вигаданого uint16_t union) ──
    ybad = 60
    p.append(text(x0, ybad - 8, "хибно: крок = 2 (sizeof чужого слова)", size=12, color=POS, anchor="start", bold=True))
    for k in range(6):
        x = x0 + k * 2 * byte + byte     # центр «прочитаного» слова
        col = FIELD if (k % 2 == 0) else POS
        p.append(arrow(x, ybad + 8, x, ymem - 6, color=col, sw=1.8))
    p.append(text(x0 + 11 * byte, ybad + 4, "кожне друге влучання — у сміття між вибірками",
                  size=10, color=POS, anchor="start"))

    # ── знизу: ПРАВИЛЬНИЙ крок = SOC_ADC_DIGI_RESULT_BYTES ──
    ygood = 232
    p.append(text(x0, ygood + 30, "правильно: крок = SOC_ADC_DIGI_RESULT_BYTES",
                  size=12, color=FIELD, anchor="start", bold=True))
    for s in range(nbytes // 4):
        x = x0 + s * 4 * byte + 2 * byte   # центр вибірки (перші 12 біт коду)
        p.append(arrow(x, ygood + 8, x, ymem + bh + 6, color=FIELD, sw=2.2))
    p.append(text(x0 + 2 * byte, ygood + 30 + 18, "кожне влучання — рівно в код вибірки",
                  size=10, color=FIELD, anchor="start"))

    p.append(text(W / 2, 336,
                  "та сама пам'ять; крок вирішує все — бери його з константи чіпа, не з sizeof вигаданого union",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "unpack-stride.svg"), W, H, *p,
           title="Крок масиву вирішує все: хардкод бреше, константа чіпа влучає")


if __name__ == "__main__":
    fig_chain()
    fig_sample_word()
    fig_wakeup()
    fig_gdma_ring()
    fig_deadline()
    fig_jitter_src()
    fig_scan_skew()
    fig_sample_formats()
    fig_unpack_stride()
    print("OK: figures written to", OUT)
