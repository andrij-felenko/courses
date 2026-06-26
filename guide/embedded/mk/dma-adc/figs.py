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


if __name__ == "__main__":
    fig_chain()
    fig_sample_word()
    fig_wakeup()
    print("OK: figures written to", OUT)
