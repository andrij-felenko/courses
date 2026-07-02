# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: розрив — вузька адреса проти великої зовнішньої пам'яті ────────
def fig_gap():
    W, H = 720, 380
    frags = []
    frags.append(text(W/2, 30, "Адресний простір менший за наявну пам'ять", size=17, bold=True))

    # Ліворуч: адресний простір ядра (64 КБ)
    ax, ay, aw, ah = 70, 70, 150, 260
    frags.append(rect(ax, ay, aw, ah, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(ax+aw/2, ay-12, "що ядро вміє назвати", size=13, color=NEG, bold=True))
    frags.append(text(ax+aw/2, ay+ah/2-8, "64 КБ", size=22, bold=True))
    frags.append(text(ax+aw/2, ay+ah/2+16, "16-бітна адреса", size=12, color=MUTED))
    frags.append(text(ax+aw/2, ay+ah-14, "0x0000 … 0xFFFF", size=11, color=MUTED))

    # Праворуч: наявна пам'ять (2 МБ) — набагато вища смуга
    bx, by, bw = 470, 60, 180
    bh = 290
    frags.append(rect(bx, by, bw, bh, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(bx+bw/2, by-12, "що фізично встановлено", size=13, color=POS, bold=True))
    frags.append(text(bx+bw/2, by+bh/2-8, "2 МБ", size=24, bold=True))
    frags.append(text(bx+bw/2, by+bh/2+18, "мікросхеми пам'яті", size=12, color=MUTED))

    # Стрілка-розрив між ними
    frags.append(text((ax+aw+bx)/2, 175, "×32", size=26, color=POS, bold=True))
    frags.append(text((ax+aw+bx)/2, 205, "не влазить", size=13, color=MUTED))
    frags.append(line(ax+aw+8, 235, bx-8, 235, color=MUTED, sw=1.5, dash="5,4"))
    frags.append(text((ax+aw+bx)/2, 255, "адрес бракує,", size=12, color=INK))
    frags.append(text((ax+aw+bx)/2, 272, "щоб дотягтися", size=12, color=INK))

    render(os.path.join(OUT, 'gap.svg'), W, H, *frags)


# ── Фігура 2: вікно й перемикач банків ──────────────────────────────────────
def fig_window():
    W, H = 760, 470
    frags = []
    frags.append(text(W/2, 28, "Одне вікно — багато банків за перемикачем", size=17, bold=True))

    # Ліворуч: адресний простір ядра з нерухомою частиною і вікном
    ax, aw = 60, 190
    ay, ah = 70, 340
    frags.append(text(ax+aw/2, ay-12, "адресний простір ядра", size=13, bold=True))
    # нерухома частина
    fix_h = 210
    frags.append(rect(ax, ay, aw, fix_h, fill="#f4f6f8", stroke=LINE, sw=1.5))
    frags.append(text(ax+aw/2, ay+fix_h/2-8, "нерухома пам'ять", size=13))
    frags.append(text(ax+aw/2, ay+fix_h/2+14, "код, змінні, I/O", size=11, color=MUTED))
    # вікно (аперутра)
    wy = ay + fix_h
    wh = ah - fix_h
    frags.append(rect(ax, wy, aw, wh, fill="#e9f9ef", stroke=FIELD, sw=2.5))
    frags.append(text(ax+aw/2, wy+wh/2-8, "ВІКНО", size=16, color=FIELD, bold=True))
    frags.append(text(ax+aw/2, wy+wh/2+14, "16 КБ", size=12, color=MUTED))
    frags.append(text(ax+aw/2, wy+wh+16, "0xC000 … 0xFFFF", size=11, color=MUTED))

    # Регістр-перемикач
    rx, ry, rw, rh = 300, 250, 150, 56
    frags.append(rect(rx, ry, rw, rh, fill="#fff6e6", stroke="#b8860b", sw=2))
    frags.append(text(rx+rw/2, ry-8, "регістр вибору банку", size=12, color="#8a6d00", bold=True))
    frags.append(text(rx+rw/2, ry+rh/2+6, "BANK = 2", size=17, bold=True))
    frags.append(arrow(ax+aw+6, wy+wh/2, rx-6, ry+rh/2))

    # Праворуч: стос банків у зовнішній пам'яті
    bx, bw = 560, 150
    by0, bhh, gap = 66, 52, 12
    labels = ["банк 0", "банк 1", "банк 2", "банк 3", "…"]
    frags.append(text(bx+bw/2, by0-14, "зовнішня пам'ять", size=13, bold=True))
    for i, lb in enumerate(labels):
        yy = by0 + i*(bhh+gap)
        chosen = (i == 2)
        fill = "#e9f9ef" if chosen else "#f4f6f8"
        stroke = FIELD if chosen else LINE
        sw = 2.5 if chosen else 1.4
        frags.append(rect(bx, yy, bw, bhh, fill=fill, stroke=stroke, sw=sw))
        frags.append(text(bx+bw/2, yy+bhh/2+5, lb, size=14,
                          bold=chosen, color=(FIELD if chosen else INK)))
    # стрілка від регістра до обраного банку
    chosen_y = by0 + 2*(bhh+gap) + bhh/2
    frags.append(arrow(rx+rw+6, ry+rh/2, bx-6, chosen_y, color=FIELD))
    # зв'язок обраного банку у вікно
    frags.append(text((ax+aw+bx)/2, 400, "у вікні видно той банк,", size=12, color=INK))
    frags.append(text((ax+aw+bx)/2, 418, "що обрав регістр", size=12, color=INK))

    render(os.path.join(OUT, 'window.svg'), W, H, *frags)


# ── Фігура 3: MMU-переклад проти вікна банків ───────────────────────────────
def fig_mmu_vs_window():
    W, H = 760, 430
    frags = []
    frags.append(text(W/2, 26, "Дві відповіді на брак адрес", size=17, bold=True))

    # Ліва панель: MMU — прозорий переклад кожної адреси
    lx = 40
    frags.append(text(lx+170, 60, "MMU: переклад кожної адреси", size=14, bold=True, anchor="middle"))
    frags.append(rect(lx, 74, 340, 300, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    # віртуальна адреса
    frags.append(rect(lx+24, 110, 130, 44, fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(text(lx+24+65, 110+27, "адреса від", size=12))
    frags.append(text(lx+24+65, 110+27+15, "програми", size=12))
    # блок MMU
    frags.append(rect(lx+120, 190, 100, 50, fill="#fff6e6", stroke="#b8860b", sw=2))
    frags.append(text(lx+120+50, 190+22, "MMU", size=14, bold=True))
    frags.append(text(lx+120+50, 190+40, "таблиця", size=11, color=MUTED))
    # фізична адреса
    frags.append(rect(lx+186, 300, 130, 44, fill="#fdecea", stroke=POS, sw=1.8))
    frags.append(text(lx+186+65, 300+27, "справжня", size=12))
    frags.append(text(lx+186+65, 300+27+15, "адреса в RAM", size=12))
    frags.append(arrow(lx+89, 154, lx+150, 188))
    frags.append(arrow(lx+180, 240, lx+240, 298))
    frags.append(text(lx+170, 366, "залізо, автоматично, на кожен доступ", size=11, color=MUTED, anchor="middle"))

    # Права панель: вікно банків — вручну, лише для одного региону
    rx = 400
    frags.append(text(rx+180, 60, "Вікно: підміна вручну", size=14, bold=True, anchor="middle"))
    frags.append(rect(rx, 74, 340, 300, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    # фіксоване вікно
    frags.append(rect(rx+30, 120, 120, 50, fill="#e9f9ef", stroke=FIELD, sw=2.2))
    frags.append(text(rx+30+60, 120+22, "вікно", size=13, color=FIELD, bold=True))
    frags.append(text(rx+30+60, 120+40, "нерухоме", size=11, color=MUTED))
    # три банки
    for i in range(3):
        yy = 110 + i*54
        chosen = (i == 1)
        frags.append(rect(rx+210, yy, 100, 44,
                          fill=("#e9f9ef" if chosen else "#f4f6f8"),
                          stroke=(FIELD if chosen else LINE),
                          sw=(2.2 if chosen else 1.3)))
        frags.append(text(rx+210+50, yy+27, "банк %d" % i, size=12,
                          bold=chosen, color=(FIELD if chosen else INK)))
    frags.append(arrow(rx+210, 110+54+22, rx+152, 145, color=FIELD))
    frags.append(text(rx+180, 300, "код сам пише в регістр,", size=12, anchor="middle"))
    frags.append(text(rx+180, 318, "щоб змінити банк у вікні", size=12, anchor="middle"))
    frags.append(text(rx+180, 366, "видно лише один банк за раз", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, 'mmu-vs-window.svg'), W, H, *frags)


# ── Фігура 4 (hist): два родоводи, що б'ють в одну межу ─────────────────────
def fig_two_lineages():
    W, H = 900, 500
    frags = []
    frags.append(text(W/2, 30, "Дві відповіді на брак адрес — два окремі родоводи", size=17, bold=True))

    # спільна межа посередині — жовтий пояс на всю ширину
    band_y = 250
    body, bw, bh = textbox(W/2, band_y, "спільна межа: адрес менше, ніж пам'яті",
                           size=13, pad=9, fill="#fff6e6", stroke="#b8860b", sw=1.8, bold=True, color="#8a6d00")
    frags.append(body)

    # спільна часова шкала 1960 → 1990 (одна для обох доріжок)
    x0, x1 = 90, 830
    T0, T1 = 1960, 1990
    def px(t):
        return x0 + (t - T0) * (x1 - x0) / (T1 - T0)

    y_top = 150     # доріжка MMU — над поясом (він давніший)
    y_bot = 350     # доріжка банків — під поясом
    frags.append(line(x0, y_top, x1, y_top, color=NEG, sw=2))
    frags.append(line(x0, y_bot, x1, y_bot, color=POS, sw=2))
    frags.append(text(x0-6, 66, "MMU та віртуальна пам'ять (мейнфрейми)", size=13, bold=True, color=NEG, anchor="start"))
    frags.append(text(x0-6, 452, "перемикання банків (мікромашини)", size=13, bold=True, color=POS, anchor="start"))
    # позначки-десятиліття на шкалі
    for t in (1960, 1970, 1980, 1990):
        frags.append(text(px(t), band_y-2, str(t), size=11, color=MUTED))

    # доріжка MMU (над поясом): три події 1961–1964 стоять близько на шкалі —
    # крапки лишаємо на реальних роках, а рамки-підписи розводимо по горизонталі,
    # щоб не злипалися, і з'єднуємо тонкою лінією-виноскою.
    mmu = [
        (1961, "Burroughs B5000\nсегменти\n(комерційна)", px(1961)-40),
        (1962, "Atlas\nдемандне\nсторінкування", px(1962)+95),
        (1964, "GE-645 (Multics)\nсегм.+стор.\n+ асоц. пам'ять", px(1964)+235),
    ]
    for t, label, lx in mmu:
        x = px(t)
        frags.append(circle(x, y_top, 6, fill="#eaf0fd", stroke=NEG, sw=2))
        by = y_top-64
        frags.append(line(x, y_top-6, lx, by+22, color=NEG, sw=1.0))
        frags.append(text(lx, by-18, str(int(t)), size=12, bold=True, color=NEG))
        body, bw, bh = textbox(lx, by, label, size=11, pad=6, fill="#eaf0fd", stroke=NEG, sw=1.2, color=INK)
        frags.append(body)

    # доріжка банків (під поясом): підписи вниз; 1981 і 1982 стоять поруч —
    # розводимо їх у два ряди по висоті, щоб рамки не злипалися.
    banks = [
        (1977, "Cromemco\n8×64 КБ", 0),
        (1981, "Atari 2600\nAsteroids", 0),
        (1982, "Commodore 64\nRAM під ROM", 1),
        (1985, "LIM EMS\nМБ крізь 64 КБ", 0),
        (1989, "Game Boy\nMBC", 0),
    ]
    for t, label, row in banks:
        x = px(t)
        frags.append(circle(x, y_bot, 6, fill="#fdecea", stroke=POS, sw=2))
        frags.append(text(x, y_bot+28, str(int(t)), size=12, bold=True, color=POS))
        by = y_bot + (58 if row == 0 else 108)
        frags.append(line(x, y_bot+6, x, by-18, color=POS, sw=1.0))
        body, bw, bh = textbox(x, by, label, size=11, pad=6, fill="#fdecea", stroke=POS, sw=1.2, color=INK)
        frags.append(body)

    render(os.path.join(OUT, 'two-lineages.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_gap()
    fig_window()
    fig_mmu_vs_window()
    fig_two_lineages()
    print("figures written to", OUT)
