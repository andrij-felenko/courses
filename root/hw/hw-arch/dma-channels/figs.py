# -*- coding: utf-8 -*-
"""Фігури до теми «Канали й дескриптори DMA» та її вставки proj-descriptors.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Імена файлів — slug-only, без номерів. Заголовки фігур — без «Рис.» і номерів
(підпис дає сам Markdown).
Стаття: channels, descriptor-list, bus-arbitration.
Вставка ⚙️ proj-descriptors: descriptor-chain, sg-vs-naive.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

WARM = "#c0a020"   # жовтий акцент
AUD  = "#8e44ad"   # фіолетовий — аудіо-канал


# ── Стаття, фіг.1: пул каналів усередині одного контролера ──────────────────
def fig_channels():
    W, H = 760, 380
    f = [text(W / 2, 28, "Один контролер DMA — пул незалежних каналів", size=16, bold=True)]

    # Рамка контролера
    f.append(rect(60, 70, 360, 260, fill="#f9fafb", stroke=LINE, sw=1.8, rx=10))
    f.append(text(240, 92, "Контролер DMA (GDMA)", size=13, bold=True, color=INK))

    # Три канали — кожен зі своїм набором регістрів
    chans = [
        (118, "Канал 0", "src: АЦП\ndst: буфер RAM\nlen: 512", FIELD, "#eef6ef"),
        (200, "Канал 1", "src: кадр RAM\ndst: дисплей-шина\nlen: 153600", NEG, "#eaf0fd"),
        (282, "Канал 2", "src: мікрофон I2S\ndst: буфер RAM\nlen: 256", AUD, "#f4eaf8"),
    ]
    for y, name, regs, col, fill in chans:
        f.append(rect(80, y, 200, 40, fill=fill, stroke=col, sw=1.6))
        f.append(text(96, y + 16, name, size=12, bold=True, color=col, anchor="start"))
        f.append(text(96, y + 31, regs.replace("\n", " · "), size=9, color=MUTED, anchor="start"))

    # Спільний арбітр + шина
    f.append(rect(300, 110, 100, 180, fill="#fff6e0", stroke=WARM, sw=1.8))
    f.append(fitbox(300, 110, 100, 180, "Арбітр\nшини\n(спільний\nна всі\nканали)",
                    size=11, fill="#fff6e0", stroke=WARM, color=INK, bold=True))

    # Стрілки каналів до арбітра
    for y, *_ in chans:
        f.append(arrow(280, y + 20, 300, 200, color=MUTED, sw=1.3))

    # Шина праворуч
    f.append(arrow(400, 200, 470, 200, sw=2.2))
    f.append(rect(470, 90, 230, 220, fill="#f4f6f8", stroke=LINE, sw=1.8, rx=10))
    f.append(text(585, 112, "Спільна шина й пам'ять", size=12, bold=True))
    f.append(rect(498, 134, 174, 36, fill="#eef6ef", stroke=FIELD, sw=1.4))
    f.append(fitbox(498, 134, 174, 36, "буфер АЦП", size=11, fill="#eef6ef", stroke=FIELD, color=INK))
    f.append(rect(498, 184, 174, 36, fill="#eaf0fd", stroke=NEG, sw=1.4))
    f.append(fitbox(498, 184, 174, 36, "кадр дисплея", size=11, fill="#eaf0fd", stroke=NEG, color=INK))
    f.append(rect(498, 234, 174, 36, fill="#f4eaf8", stroke=AUD, sw=1.4))
    f.append(fitbox(498, 234, 174, 36, "буфер аудіо", size=11, fill="#f4eaf8", stroke=AUD, color=INK))

    f.append(text(W / 2, 360,
                  "Кожен канал зберігає власні src/dst/len — потоки не плутаються; "
                  "шину ділить один арбітр.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "channels.svg"), W, H, *f)


# ── Стаття, фіг.2: анатомія дескриптора й кільце ────────────────────────────
def fig_descriptor_list():
    W, H = 780, 420
    f = [text(W / 2, 26, "Дескриптор і зв'язаний список (кільце ping-pong)", size=16, bold=True)]

    # Один дескриптор крупно — анатомія полів
    dx, dy, dw, dh = 60, 70, 250, 250
    f.append(rect(dx, dy, dw, dh, fill="#f4f6f8", stroke=LINE, sw=2, rx=8))
    f.append(text(dx + dw / 2, dy + 22, "Один дескриптор", size=13, bold=True))
    rows = [
        ("owner", "1 = DMA, 0 = CPU", POS),
        ("eof", "1 = кінець → переривання", FIELD),
        ("length", "скільки байтів передати", INK),
        ("size", "місткість буфера", MUTED),
        ("buf →", "адреса даних у RAM", NEG),
        ("next →", "наступний вузол", WARM),
    ]
    ry = dy + 44
    for name, desc, col in rows:
        f.append(rect(dx + 14, ry, dw - 28, 30, fill=BG, stroke=col, sw=1.4))
        f.append(text(dx + 24, ry + 19, name, size=11, bold=True, color=col, anchor="start"))
        f.append(text(dx + 108, ry + 19, desc, size=9, color=MUTED, anchor="start"))
        ry += 36

    # Кільце з двох вузлів праворуч (ping-pong)
    cx = 560
    a_y, b_y = 110, 300
    for (yy, name, buf, col, fill) in [(a_y, "вузол A", "buf → buf_a", NEG, "#eaf0fd"),
                                       (b_y, "вузол B", "buf → buf_b", FIELD, "#eef6ef")]:
        f.append(rect(cx - 90, yy - 34, 180, 68, fill=fill, stroke=col, sw=1.8, rx=8))
        f.append(text(cx, yy - 14, name, size=12, bold=True, color=col))
        f.append(text(cx, yy + 4, buf, size=10, color=MUTED))
        f.append(text(cx, yy + 20, "eof=1 · owner=1", size=9, color=MUTED))

    # next: A → B → A (кільце)
    f.append(arrow(cx + 70, a_y + 20, cx + 70, b_y - 36, color=WARM, sw=1.8))
    f.append(text(cx + 86, (a_y + b_y) / 2, "next", size=10, color=WARM, anchor="start", italic=True))
    f.append(arrow(cx - 70, b_y - 36, cx - 70, a_y + 20, color=WARM, sw=1.8))
    f.append(text(cx - 120, (a_y + b_y) / 2, "next", size=10, color=WARM, anchor="start", italic=True))
    f.append(text(cx, 392, "next останнього → перший: кільце,\nяким DMA крутиться без зупину",
                  size=10, color=MUTED))

    # next першого дескриптора зліва → кільце
    f.append(arrow(dx + dw, dy + dh - 40, cx - 90, a_y, color=MUTED, sw=1.3))

    render(os.path.join(IMG, "descriptor-list.svg"), W, H, *f)


# ── Стаття, фіг.3: арбітраж шини за пріоритетом ─────────────────────────────
def fig_bus_arbitration():
    W, H = 760, 400
    f = [text(W / 2, 26, "Арбітраж шини: пріоритет вирішує чергу, а не пропускну здатність",
              size=15, bold=True)]

    # Два канали підняли запит
    f.append(rect(60, 70, 220, 56, fill="#f4eaf8", stroke=AUD, sw=1.8))
    f.append(fitbox(60, 70, 220, 56, "Канал аудіо — запит\nпріоритет HIGH",
                    size=12, fill="#f4eaf8", stroke=AUD, color=INK, bold=True))
    f.append(rect(60, 150, 220, 56, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(fitbox(60, 150, 220, 56, "Канал дисплея — запит\nпріоритет LOW",
                    size=12, fill="#eaf0fd", stroke=NEG, color=INK))

    # Арбітр
    f.append(rect(330, 96, 110, 84, fill="#fff6e0", stroke=WARM, sw=2, rx=8))
    f.append(fitbox(330, 96, 110, 84, "Арбітр:\nпропускає\nвищий", size=12,
                    fill="#fff6e0", stroke=WARM, color=INK, bold=True))
    f.append(arrow(280, 98, 330, 120, color=AUD, sw=2))
    f.append(arrow(280, 178, 330, 156, color=NEG, sw=1.4, ))
    f.append(text(305, 200, "притримано", size=9, color=NEG))

    # Шина пропущена аудіо
    f.append(arrow(440, 138, 500, 138, sw=2.2))
    f.append(text(470, 128, "пропущено", size=9, color=AUD))

    # Смуга пропускної здатності
    bx, by, bw, bh = 500, 110, 210, 56
    f.append(rect(bx, by, bw, bh, fill=BG, stroke=LINE, sw=1.6))
    seg_core = int(bw * 0.25)
    seg_disp = int(bw * 0.06)
    seg_aud  = int(bw * 0.003 * 50)  # ледь видно
    f.append(rect(bx, by, seg_core, bh, fill="#f0f0f0", stroke=MUTED, sw=0.8))
    f.append(rect(bx + seg_core, by, seg_disp, bh, fill="#eaf0fd", stroke=NEG, sw=0.8))
    f.append(text(bx + bw / 2, by - 6, "Смуга шини (≈ 80 МБ/с)", size=10, color=MUTED))
    f.append(text(bx + seg_core / 2, by + bh / 2 + 4, "ядро", size=9, color=MUTED))
    f.append(text(bx + bw - 40, by + bh / 2 + 4, "запас", size=9, color=FIELD))

    # Підпис-висновок: пріоритет vs пропускна здатність
    f.append(rect(60, 250, 650, 90, fill="#f9fafb", stroke=LINE, sw=1.4, rx=8))
    f.append(fitbox(60, 250, 650, 44,
                    "Пріоритет = ПОРЯДОК у черзі: вищий канал отримує шину першим.",
                    size=12, fill="#f9fafb", stroke="none", color=INK, bold=True))
    f.append(fitbox(60, 296, 650, 40,
                    "Якщо сумарний трафік > смуги шини — жоден пріоритет не врятує: "
                    "нижчий канал голодуватиме.",
                    size=12, fill="#f9fafb", stroke="none", color=POS))

    f.append(text(W / 2, 372,
                  "Високий пріоритет аудіо тримає затримку малою; дисплей терпить кілька мікросекунд.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "bus-arbitration.svg"), W, H, *f)


# ── Вставка ⚙️, фіг.1: ланцюг дескрипторів (scatter-gather) ─────────────────
def fig_descriptor_chain():
    W, H = 820, 480
    f = [text(W / 2, 26, "Дескриптори як вузли однозв'язного списку в RAM", size=16, bold=True)]

    # Ліва рамка: дескриптори
    f.append(rect(40, 50, 330, 390, fill="#f9fafb", stroke=MUTED, sw=1.0, rx=10))
    f.append(text(205, 72, "RAM (дескриптори)", size=12, bold=True, color=MUTED))

    nodes = [
        (62, "desc[0]", "buf → hdr", "length=64", "owner=1", "eof=0", "next →", LINE, "#f4f6f8"),
        (192, "desc[1]", "buf → body", "length=512", "owner=1", "eof=0", "next →", LINE, "#f4f6f8"),
        (322, "desc[2]  (eof=1)", "buf → crc", "length=4", "owner=1", "eof=1", "next=0", FIELD, "#e8f8ee"),
    ]
    for (ny, title_, b, l, o, e, nx, col, fill) in nodes:
        f.append(rect(100, ny, 200, 96, fill=fill, stroke=col, sw=2.0))
        f.append(text(200, ny + 15, title_, size=12, bold=True, color=col))
        f.append(line(106, ny + 22, 294, ny + 22, color=col, sw=1.0))
        eof_col = FIELD if e == "eof=1" else MUTED
        nx_col = FIELD if nx == "next=0" else MUTED
        for i, (txt, c) in enumerate([(b, MUTED), (l, MUTED), (o, MUTED), (e, eof_col), (nx, nx_col)]):
            bold = c == FIELD
            f.append(text(200, ny + 34 + i * 13, txt, size=10, color=c, bold=bold))

    # next-стрілки desc0→1, desc1→2
    for y0, y1 in [(62, 192), (192, 322)]:
        f.append(line(300, y0 + 82, 318, y0 + 82, color=INK, sw=1.8))
        f.append(line(318, y0 + 82, 318, y1 + 14, color=INK, sw=1.8))
        f.append(arrow(318, y1 + 14, 300, y1 + 14, color=INK, sw=1.8))
        f.append(text(334, (y0 + 82 + y1 + 14) / 2, "next", size=10, color=MUTED, anchor="start", italic=True))

    f.append(line(240, 418, 240, 438, color=FIELD, sw=1.8))
    box, _, _ = textbox(258, 454, "next=0 (NULL)", size=10, fill="#e8f8ee", stroke=FIELD, color=INK)
    f.append(box)

    # Права рамка: розкидані буфери
    f.append(rect(470, 50, 310, 400, fill="#fdf8f0", stroke="#c8a060", sw=1.0, rx=10))
    f.append(text(625, 72, "Інші місця RAM (розкидані буфери)", size=12, bold=True, color="#a07030"))
    bufs = [(516, 72, 590, "hdr", "64 байти заголовок"),
            (566, 232, 640, "body", "512 байтів навантаження"),
            (486, 362, 560, "crc", "4 байти CRC")]
    for (bx, by, tcx, name, sub) in bufs:
        f.append(rect(bx, by, 148, 56, fill="#fff8e8", stroke="#c8a060", sw=1.5))
        f.append(text(tcx, by + 22, name, size=13, bold=True, color="#7a5000"))
        f.append(text(tcx, by + 40, sub, size=9, color=MUTED))

    # buf-стрілки (пунктир) desc→буфер
    for (y, bx, byc) in [(94, 516, 100), (224, 566, 260), (354, 486, 390)]:
        f.append(line(300, y, 440, y, color=MUTED, sw=1.4, dash="5,4"))
        f.append(line(440, y, 440, byc, color=MUTED, sw=1.4, dash="5,4"))
        f.append(arrow(440, byc, bx, byc, color=MUTED, sw=1.4))

    # DMA старт у перший вузол (рамка внизу ліворуч, стрілка вгору в desc[0])
    box, _, _ = textbox(90, 462, "DMA старт", size=11,
                        fill="#fdecea", stroke=POS, color=INK)
    f.append(box)
    f.append(arrow(90, 446, 120, 158, color=POS, sw=1.6))

    # IRQ після eof
    f.append(line(300, 370, 376, 370, color=FIELD, sw=1.8, dash="4,3"))
    f.append(arrow(376, 405, 440, 405, color=FIELD, sw=1.8))
    box, _, _ = textbox(492, 370, "IRQ\n(одне переривання)", size=11, fill="#e8f8ee", stroke=FIELD, color=INK)
    f.append(box)

    render(os.path.join(IMG, "descriptor-chain.svg"), W, H, *f)


# ── Вставка ⚙️, фіг.2: наївний шлях проти scatter-gather ────────────────────
def fig_sg_vs_naive():
    W, H = 800, 420
    f = [text(W / 2, 26, "Наївна склейка проти scatter-gather", size=16, bold=True)]

    # Лівий стовпець: наївний шлях
    f.append(text(200, 60, "Наївно: спершу склеїти копіюванням", size=13, bold=True, color=POS))
    bufs = [("hdr", "#fff8e8"), ("body", "#fff8e8"), ("crc", "#fff8e8")]
    bx = 60
    for name, fill in bufs:
        f.append(rect(bx, 80, 80, 40, fill=fill, stroke="#c8a060", sw=1.4))
        f.append(text(bx + 40, 104, name, size=11, color="#7a5000", bold=True))
        bx += 96
    # стрілка «копія ядром»
    f.append(arrow(200, 130, 200, 168, color=POS, sw=2))
    f.append(text(216, 152, "копія ядром (такти CPU!)", size=10, color=POS, anchor="start"))
    f.append(rect(80, 172, 240, 40, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(fitbox(80, 172, 240, 40, "один великий буфер (склеєно)", size=11,
                    fill="#fdecea", stroke=POS, color=INK))
    f.append(arrow(200, 214, 200, 250, sw=2))
    f.append(rect(80, 254, 240, 36, fill="#eef6ef", stroke=FIELD, sw=1.6))
    f.append(fitbox(80, 254, 240, 36, "DMA: один блок", size=11, fill="#eef6ef", stroke=FIELD, color=INK))
    f.append(text(200, 320, "Ядро вже витратило такти на склейку —\nрівно те, від чого DMA рятував.",
                  size=11, color=POS))

    # Розділювач
    f.append(line(410, 50, 410, 360, color=MUTED, sw=1.2, dash="4,4"))

    # Правий стовпець: scatter-gather
    f.append(text(600, 60, "Scatter-gather: DMA сама обходить ланцюг", size=13, bold=True, color=FIELD))
    bx = 470
    cols = ["#fff8e8", "#fff8e8", "#e8f8ee"]
    for i, (name, _) in enumerate(bufs):
        f.append(rect(bx, 80, 80, 40, fill=cols[i], stroke="#c8a060", sw=1.4))
        f.append(text(bx + 40, 104, name, size=11, color="#7a5000", bold=True))
        bx += 96
    # дескриптори під буферами
    bx = 470
    for i in range(3):
        f.append(rect(bx, 150, 80, 34, fill="#f4f6f8", stroke=LINE, sw=1.4))
        f.append(text(bx + 40, 171, "desc[%d]" % i, size=10, color=INK))
        f.append(line(bx + 40, 120, bx + 40, 150, color=MUTED, sw=1.2, dash="3,3"))
        if i < 2:
            f.append(arrow(bx + 80, 167, bx + 96, 167, color=WARM, sw=1.6))
        bx += 96
    f.append(arrow(710, 184, 710, 220, color=FIELD, sw=2))
    f.append(rect(490, 224, 240, 36, fill="#eef6ef", stroke=FIELD, sw=1.6))
    f.append(fitbox(490, 224, 240, 36, "DMA: обхід по next, один потік", size=11,
                    fill="#eef6ef", stroke=FIELD, color=INK))
    f.append(text(600, 320, "Жодного копіювання й жодного пробудження\nядра між шматками — одне переривання на eof.",
                  size=11, color=FIELD))

    f.append(text(W / 2, 392,
                  "Список вузлів прибирає і зайву копію, і зайві переривання.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "sg-vs-naive.svg"), W, H, *f)


if __name__ == "__main__":
    fig_channels()
    fig_descriptor_list()
    fig_bus_arbitration()
    fig_descriptor_chain()
    fig_sg_vs_naive()
    print("OK: 5 фігур у", IMG)
