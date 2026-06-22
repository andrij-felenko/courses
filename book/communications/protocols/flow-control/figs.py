# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── overrun: один регістр — новий байт затирає непрочитаний старий ─────────────
# Ідея: байти прибувають за розкладом передавача; поки CPU застряг, наступний
# байт лягає в той самий єдиний регістр і затирає попередній — тихий збій.

def fig_overrun():
    W, H = 760, 360
    p = []
    axis_y = 250
    p.append(arrow(120, axis_y, 660, axis_y, color=INK, sw=1.8))
    p.append(text(672, axis_y + 4, "час", size=12, color=MUTED, anchor="start", italic=True))

    cols = [("B0", 150), ("B1", 290), ("B2", 430), ("B3", 570)]
    for lab, x in cols:
        p.append(rect(x - 18, 120, 36, 30, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=4))
        p.append(text(x, 141, lab, size=12, color=NEG, bold=True))
        p.append(line(x, 152, x, axis_y - 4, color=NEG, sw=1.4, dash="3 3"))
        p.append(text(x, 112, "прийшов", size=9.5, color=MUTED))

    p.append(rect(150, 290, 280, 30, fill="#fdecea", stroke=POS, sw=1.6, rx=5))
    p.append(text(290, 310, "CPU застряг у довгій операції", size=11.5, color=POS, bold=True))
    p.append(text(150, 340, "прочитав B0", size=10.5, color=FIELD, anchor="start"))

    p.append(text(290, 200, "✗ B1 затерто", size=12, color=POS, bold=True))
    p.append(text(290, 216, "(B2 ліг на його місце)", size=10, color=POS))

    box, _, _ = textbox(W / 2, 344, "Приймальний регістр тримає лише ОДИН байт: не встиг прочитати — наступний затирає.",
                        size=11.5, bold=True, fill="#f4f6f8", stroke=MUTED, sw=1.4, min_w=700)
    p.append(box)

    render(os.path.join(OUT, "overrun.svg"), W, H, *p,
           title="Без буфера новий байт перезаписує непрочитаний старий")


# ── fifo: апаратна черга поглинає короткий сплеск ──────────────────────────────
# Ідея: замість одного регістра — невелика черга комірок; нові байти стають у
# хвіст, CPU забирає з голови, тож не мусить ловити кожен «у момент».

def fig_fifo():
    W, H = 760, 300
    p = []
    n, cw, ch = 8, 56, 46
    x0, y = 150, 120
    filled = 5
    for i in range(n):
        x = x0 + i * cw
        fill = "#eaf0fd" if i < filled else BG
        st = NEG if i < filled else MUTED
        p.append(rect(x, y, cw, ch, fill=fill, stroke=st, sw=1.6, rx=4))
        if i < filled:
            p.append(text(x + cw / 2, y + ch / 2 + 5, "B%d" % i, size=12, color=NEG, bold=True))

    p.append(arrow(x0 - 24, y + ch / 2, x0 - 4, y + ch / 2, color=INK, sw=1.8))
    p.append(text(x0 - 28, y + ch / 2 - 12, "лінія →", size=10.5, color=MUTED, anchor="end"))
    p.append(text(x0 + cw / 2, y - 14, "хвіст (пише UART)", size=10.5, color=POS, bold=True))

    rx = x0 + n * cw
    p.append(arrow(rx + 4, y + ch / 2, rx + 24, y + ch / 2, color=INK, sw=1.8))
    p.append(text(rx + 28, y + ch / 2 + 4, "CPU", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(rx - cw / 2, y - 14, "голова (читає CPU)", size=10.5, color=FIELD, bold=True, anchor="end"))

    box, _, _ = textbox(W / 2, 240,
                        "Глибина невелика: типово 16 байт (UART 16550), у ESP32 — 128. Фора є, та скінченна.",
                        size=11.5, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.4, min_w=700)
    p.append(box)

    render(os.path.join(OUT, "fifo.svg"), W, H, *p,
           title="Апаратний FIFO: черга в периферії поглинає короткий сплеск")


# ── pipeline: два рівні — FIFO у периферії та кільцевий буфер у RAM ────────────
# Ідея: переривання перекладає байти з малого апаратного FIFO у великий буфер у
# пам'яті; застосунок читає вже з нього — тож майже ніколи не «ловить момент».

def fig_pipeline():
    W, H = 820, 250
    p = []
    y = 120
    bh = 56
    blocks = [
        ("лінія", 60, 70, BG, MUTED),
        ("апаратний\nFIFO\n(малий)", 165, 110, "#eaf0fd", NEG),
        ("переривання\nперекладає", 320, 120, "#fdecea", POS),
        ("кільцевий\nбуфер у RAM\n(великий)", 485, 130, "#eef6ef", FIELD),
        ("Serial.read()\nу застосунку", 670, 130, "#f4f6f8", INK),
    ]
    centers = []
    x = 0
    for lab, bx, bw, fill, col in blocks:
        p.append(fitbox(bx, y - bh / 2, bw, bh, lab, size=11, fill=fill, stroke=col, sw=1.6, bold=True, color=col))
        centers.append((bx, bx + bw))
    for i in range(1, len(centers)):
        p.append(arrow(centers[i - 1][1] + 2, y, centers[i][0] - 2, y, color=INK, sw=1.7))

    p.append(text(W / 2, 200, "Драйвер ховає від коду і FIFO, і переривання — читаєш уже з великого буфера в RAM.",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "pipeline.svg"), W, H, *p,
           title="Два рівні буферизації: апаратний FIFO і кільцевий буфер у RAM")


# ── ring: кільцевий буфер, покажчики head і tail ──────────────────────────────
# Ідея: масив «по колу»; head пише (переривання), tail читає (застосунок); між
# ними — непрочитані байти; head наздогнав tail — повний, tail догнав head — порожній.

def fig_ring():
    import math
    W, H = 820, 440
    cx, cy, R = 360, 250, 130
    p = []
    n = 12
    filled = set([7, 8, 9, 10, 11, 0])      # сектор непрочитаних між tail і head
    for i in range(n):
        a = -math.pi / 2 + 2 * math.pi * i / n
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        if i in filled:
            p.append(circle(x, y, 22, fill="#eaf0fd", stroke=NEG, sw=1.8))
        else:
            p.append(circle(x, y, 22, fill=BG, stroke=MUTED, sw=1.8))

    # head — куди пише переривання (перша порожня за непрочитаними)
    ah = -math.pi / 2 + 2 * math.pi * 1 / n
    hx, hy = cx + R * math.cos(ah), cy + R * math.sin(ah)
    p.append(arrow(hx + 56, hy - 30, hx + 26, hy - 8, color=POS, sw=2.2))
    p.append(text(hx + 60, hy - 36, "head — пише переривання", size=11, color=POS, bold=True, anchor="start"))

    # tail — звідки читає застосунок
    at = -math.pi / 2 + 2 * math.pi * 7 / n
    tx, ty = cx + R * math.cos(at), cy + R * math.sin(at)
    p.append(arrow(tx - 56, ty + 30, tx - 26, ty + 8, color=FIELD, sw=2.2))
    p.append(text(tx - 60, ty + 38, "tail — читає застосунок", size=11, color=FIELD, bold=True, anchor="end"))

    p.append(text(cx, cy - 6, "непрочитані", size=12, color=NEG, bold=True))
    p.append(text(cx, cy + 12, "байти", size=12, color=NEG, bold=True))

    bx = 610
    p.append(rect(bx, 150, 200, 64, fill="#f4f6f8", stroke=MUTED, sw=1.3, rx=8))
    p.append(text(bx + 12, 176, "head == tail → порожній", size=11, color=INK, anchor="start", bold=True))
    p.append(text(bx + 12, 198, "head наздогнав tail → повний", size=11, color=POS, anchor="start", bold=True))

    box, _, _ = textbox(W / 2, 410,
                        "«Кільце»: після останньої комірки покажчик стрибає на першу — пам'ять по колу.",
                        size=11.5, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.4, min_w=720)
    p.append(box)

    render(os.path.join(OUT, "ring.svg"), W, H, *p,
           title="Кільцевий буфер: покажчики head (пише) і tail (читає)")


# ── rtscts: апаратне керування потоком RTS/CTS ────────────────────────────────
# Ідея: дві лінії навхрест; приймач знімає RTS, передавач бачить це на CTS і
# затихає в межах байта — робить апаратура, без участі програми.

def fig_rtscts():
    W, H = 820, 360
    p = []
    # дві коробки
    p.append(rect(70, 90, 150, 160, fill="#fbfbfb", stroke=INK, sw=2.0, rx=12))
    p.append(text(145, 116, "Пристрій A", size=13.5, color=INK, bold=True))
    p.append(text(145, 134, "(передавач)", size=10, color=MUTED))
    p.append(rect(600, 90, 150, 160, fill="#fbfbfb", stroke=INK, sw=2.0, rx=12))
    p.append(text(675, 116, "Пристрій B", size=13.5, color=INK, bold=True))
    p.append(text(675, 134, "(приймач)", size=10, color=MUTED))

    rows = [("TX", POS, 165), ("RX", NEG, 195), ("RTS", "#b08900", 225)]
    # позначки на портах
    labels = [("TX", POS, 165), ("RX", NEG, 195), ("RTS", "#b08900", 225)]
    for lab, col, y in labels:
        p.append(text(226, y + 4, lab, size=11, color=col, anchor="start", bold=True))
        p.append(text(594, y + 4, "CTS" if lab in ("TX",) else ("TX" if lab == "RX" else "RTS"),
                      size=11, color=col, anchor="end", bold=True))
    # лінії навхрест: A.TX→B.RX, B.TX→A.RX, B.RTS→A.CTS, A.RTS→B.CTS
    p.append(line(220, 165, 600, 195, color=POS, sw=2))      # A.TX → B.RX
    p.append(line(600, 165, 220, 195, color=NEG, sw=2))      # B.TX → A.RX
    p.append(line(600, 225, 220, 225, color="#b08900", sw=2.2))  # B.RTS → A.CTS (керування)
    p.append(text(410, 150, "дані навхрест (TX↔RX)", size=10.5, color=MUTED, bold=True))
    p.append(text(410, 246, "B.RTS → A.CTS: дозвіл/пауза + спільна земля", size=10.5, color="#b08900", bold=True))

    # сценарій
    p.append(text(70, 296, "B майже повний → знімає RTS;  A бачить це на CTS → затихає в межах байта-двох.",
                  size=11.5, color=INK, anchor="start", bold=True))
    box, _, _ = textbox(W / 2, 336,
                        "RTS/CTS — швидко й двійково-безпечно (керують лінії, не байти). Ціна — 2 зайві дроти.",
                        size=11.5, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.4, min_w=720)
    p.append(box)

    render(os.path.join(OUT, "rtscts.svg"), W, H, *p,
           title="Апаратне керування потоком: RTS/CTS окремими лініями")


# ── xonxoff: програмне керування потоком XON/XOFF ─────────────────────────────
# Ідея: «стоп»/«можна» їдуть не лініями, а байтами 0x13/0x11 у зворотному
# напрямку; нуль зайвих дротів, та ці два коди вже не можна слати як дані.

def fig_xonxoff():
    W, H = 820, 340
    p = []
    p.append(rect(70, 90, 150, 130, fill="#fbfbfb", stroke=INK, sw=2.0, rx=12))
    p.append(text(145, 120, "Передавач", size=13, color=INK, bold=True))
    p.append(rect(600, 90, 150, 130, fill="#fbfbfb", stroke=INK, sw=2.0, rx=12))
    p.append(text(675, 120, "Приймач", size=13, color=INK, bold=True))

    # дані вперед
    p.append(arrow(220, 145, 600, 145, color=NEG, sw=2))
    p.append(text(410, 138, "дані →", size=11, color=NEG, bold=True))

    # XOFF назад
    p.append(arrow(600, 178, 220, 178, color=POS, sw=2))
    p.append(text(410, 171, "XOFF (0x13) = «пауза»", size=11, color=POS, bold=True))
    # XON назад
    p.append(arrow(600, 206, 220, 206, color=FIELD, sw=2))
    p.append(text(410, 226, "XON (0x11) = «продовжуй»", size=11, color=FIELD, bold=True))

    box, _, _ = textbox(W / 2, 290,
                        "Плюс — нуль зайвих дротів. Мінус фатальний для двійкових даних: байти 0x11 і 0x13 більше не можна слати як дані.",
                        size=11.5, bold=True, fill="#fdecea", stroke=POS, sw=1.4, min_w=740)
    p.append(box)

    render(os.path.join(OUT, "xonxoff.svg"), W, H, *p,
           title="Програмне керування потоком: XON/XOFF спецбайтами")


# ── watermark: зупиняти заздалегідь (верхній/нижній поріг) ─────────────────────
# Ідея: «стоп» подають не на 100%, а на верхньому порозі — лишаючи запас на
# байти, що вже в дорозі; «далі» — на нижньому. Гістерезис проти смикання.

def fig_watermark():
    W, H = 760, 360
    p = []
    bx, by, bw, bh = 130, 80, 100, 230
    p.append(rect(bx, by, bw, bh, fill=BG, stroke=INK, sw=2))
    # заповнення до ~85%
    fillh = bh * 0.85
    p.append(rect(bx, by + bh - fillh, bw, fillh, fill="#eaf0fd", stroke="none", sw=0))

    hi_y = by + bh * 0.25       # верхній поріг (75% заповнення)
    lo_y = by + bh * 0.62       # нижній поріг
    p.append(line(bx - 12, hi_y, bx + bw + 12, hi_y, color="#b08900", sw=2.2, dash="5 4"))
    p.append(text(bx + bw + 18, hi_y + 4, "верхній поріг → «стоп»", size=11, color="#b08900", anchor="start", bold=True))
    p.append(line(bx - 12, lo_y, bx + bw + 12, lo_y, color=FIELD, sw=2.2, dash="5 4"))
    p.append(text(bx + bw + 18, lo_y + 4, "нижній поріг → «далі»", size=11, color=FIELD, anchor="start", bold=True))

    p.append(text(bx + bw / 2, by + bh + 22, "буфер приймача", size=11.5, color=INK, bold=True))
    p.append(text(bx + bw + 18, by + 14, "запас зверху — на байти,", size=10, color=MUTED, anchor="start"))
    p.append(text(bx + bw + 18, by + 28, "що вже в дорозі після «стоп»", size=10, color=MUTED, anchor="start"))

    box, _, _ = textbox(W / 2, 338,
                        "Два пороги дають гістерезис — сигнали не смикаються щобайта. «Стоп» — заздалегідь.",
                        size=11.5, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.4, min_w=680)
    p.append(box)

    render(os.path.join(OUT, "watermark.svg"), W, H, *p,
           title="Зупиняти заздалегідь: водяний знак і байти в дорозі")


if __name__ == "__main__":
    fig_overrun()
    fig_fifo()
    fig_pipeline()
    fig_ring()
    fig_rtscts()
    fig_xonxoff()
    fig_watermark()
    print("OK: figures written to", OUT)
