# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Ініціалізація контролера дисплея»
(+ вставки proj-init-driver, hist-magic-numbers).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
TFT  = "#1f78b4"
GOLD = "#b9770e"
OK   = "#27ae60"
COLD = "#5b6b7a"


# ── 1. Стани контролера: від reset до живого екрана ──────────────────────────
def fig_states():
    W, H = 760, 300
    f = [text(W / 2, 28, "Контролер прокидається не там, де потрібно", size=16, bold=True)]

    states = [
        (60,  "RESET",        "регістри в дефолті\nпам'ять — сміття", POS,  "#fdecea"),
        (300, "СОН",          "матриця знеструмлена\nекран темний",   GOLD, "#fff8e6"),
        (540, "ЖИВИЙ",        "освіження йде\nпікселі видно",          OK,   "#eafaf0"),
    ]
    bx = 170
    for x, name, note, col, fill in states:
        f.append(rect(x, 96, bx, 96, fill=fill, stroke=col, sw=2))
        f.append(text(x + bx / 2, 126, name, size=14, color=col, bold=True))
        f.append(mtext(x + bx / 2, 150, note, size=10, color=MUTED, lh=1.3))

    f.append(arrow(60 + bx, 144, 300, 144, color=INK, sw=2.2))
    f.append(text((60 + bx + 300) / 2, 132, "sleep-out", size=10, color=INK, italic=True))
    f.append(arrow(300 + bx, 144, 540, 144, color=INK, sw=2.2))
    f.append(text((300 + bx + 540) / 2, 132, "display-on", size=10, color=INK, italic=True))

    f.append(text(W / 2, 238,
                  "після подачі живлення екран НЕ показує нічого — і це нормальний, очікуваний стан",
                  size=11, color=INK))
    f.append(text(W / 2, 268,
                  "робота прошивки — провести контролер цими сходинками в правильному порядку",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "states.svg"), W, H, *f)


# ── 2. Анатомія init-послідовності: команда · аргументи · затримка ───────────
def fig_anatomy():
    W, H = 760, 410
    f = [text(W / 2, 28, "Анатомія послідовності ініціалізації", size=16, bold=True)]

    rows = [
        ("апаратний reset",  "ніжка RST ↓↑",       "+120 мс", COLD,
         "змити будь-який старий стан"),
        ("SWRESET 0x01",     "—",                  "+150 мс", COLD,
         "програмне скидання логіки"),
        ("SLPOUT 0x11",      "—",                  "+120 мс", GOLD,
         "розбудити живлення матриці"),
        ("COLMOD 0x3A",      "0x55 (RGB565)",      "+10 мс",  TFT,
         "скільки байтів на піксель"),
        ("MADCTL 0x36",      "0x00 (орієнтація)",  "—",       TFT,
         "поворот, дзеркало, RGB/BGR"),
        ("гама + інверсія",  "вектор констант",    "—",       TFT,
         "відтінки й полярність панелі"),
        ("DISPON 0x29",      "—",                  "+20 мс",  OK,
         "увімкнути показ — аж тепер"),
    ]
    x, y0, w, rh = 60, 64, 640, 44
    # шапка-стовпці
    f.append(text(x + 18,  y0 - 6, "крок",     size=10, color=MUTED, anchor="start", bold=True))
    f.append(text(x + 268, y0 - 6, "аргументи", size=10, color=MUTED, anchor="start", bold=True))
    f.append(text(x + 430, y0 - 6, "пауза",    size=10, color=MUTED, anchor="start", bold=True))
    for i, (cmd, arg, delay, col, why) in enumerate(rows):
        yy = y0 + i * (rh + 4)
        f.append(rect(x, yy, w, rh, fill=FILL, stroke=col, sw=1.6))
        f.append(text(x + 18,  yy + 20, cmd, size=11.5, color=col, bold=True, anchor="start"))
        f.append(text(x + 18,  yy + 36, why, size=9, color=MUTED, anchor="start", italic=True))
        f.append(text(x + 268, yy + 27, arg, size=10.5, color=INK, anchor="start"))
        dc = POS if delay != "—" else MUTED
        f.append(text(x + 430, yy + 27, delay, size=10.5, color=dc, anchor="start", bold=(delay != "—")))

    f.append(text(W / 2, 392,
                  "червона пауза — НЕ ввічливість, а час, потрібний кремнію; пропустиш — біла пляма",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 3. Чому затримка обов'язкова: команда випереджає готовність ──────────────
def fig_timing():
    W, H = 760, 320
    f = [text(W / 2, 28, "Чому між кроками — пауза", size=16, bold=True)]

    # вісь часу
    y = 120
    f.append(line(60, y, 700, y, color=INK, sw=2))
    f.append(arrow(680, y, 702, y, color=INK, sw=2))
    f.append(text(700, y + 20, "час", size=10, color=MUTED, anchor="end", italic=True))

    # подія: надіслали SLPOUT
    f.append(line(150, y - 40, 150, y + 10, color=GOLD, sw=2))
    f.append(text(150, y - 48, "SLPOUT надіслано", size=10, color=GOLD, bold=True))

    # смуга «кремній ще піднімає живлення»
    f.append(rect(150, y - 18, 300, 16, fill="#fff3e0", stroke=GOLD, sw=1.4))
    f.append(text(300, y - 6, "насос заряду піднімає напругу матриці ~120 мс",
                  size=9.5, color=GOLD))

    # точка готовності
    f.append(line(450, y - 40, 450, y + 10, color=OK, sw=2))
    f.append(text(450, y - 48, "матриця готова", size=10, color=OK, bold=True))

    # дві стрілки наступної команди: рано (червоне) і вчасно (зелене)
    f.append(arrow(250, y + 60, 250, y + 12, color=POS, sw=2))
    f.append(text(250, y + 78, "команда РАНО", size=10, color=POS, bold=True))
    f.append(text(250, y + 94, "загубиться — біла пляма", size=9, color=POS, italic=True))

    f.append(arrow(540, y + 60, 540, y + 12, color=OK, sw=2))
    f.append(text(540, y + 78, "команда ВЧАСНО", size=10, color=OK, bold=True))
    f.append(text(540, y + 94, "після паузи — спрацює", size=9, color=OK, italic=True))

    f.append(text(W / 2, 280,
                  "контролер приймає байт одразу, але живлення матриці наростає поступово",
                  size=11, color=INK))
    f.append(text(W / 2, 304,
                  "datasheet дає мінімальні паузи — поважай їх, інакше виходиш на несформоване залізо",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "timing.svg"), W, H, *f)


# ── 4. MADCTL: один регістр орієнтації крутить увесь кадр ────────────────────
def fig_madctl():
    W, H = 760, 320
    f = [text(W / 2, 28, "MADCTL: орієнтація і порядок кольору — один байт", size=15.5, bold=True)]

    # центральний байт із бітами
    bx, by = 300, 70
    f.append(rect(bx, by, 160, 40, fill=FILL, stroke=TFT, sw=2))
    f.append(text(bx + 80, by + 26, "MADCTL 0x36", size=12, color=TFT, bold=True))

    bits = [
        ("MY", "рядки ↕"),
        ("MX", "стовпці ↔"),
        ("MV", "поміняти осі"),
        ("ML", "порядок розгортки"),
        ("RGB", "RGB ↔ BGR"),
        ("MH", "дзеркало рядка"),
    ]
    x, y0, w, rh = 110, 150, 250, 26
    for i, (b, what) in enumerate(bits):
        yy = y0 + i * (rh + 2)
        f.append(rect(x, yy, w, rh, fill="#eef4f8", stroke=COLD, sw=1.3))
        f.append(text(x + 14, yy + 18, b, size=10.5, color=TFT, bold=True, anchor="start"))
        f.append(text(x + 70, yy + 18, what, size=10, color=MUTED, anchor="start"))
    f.append(arrow(bx + 40, by + 40, x + w / 2, y0 - 6, color=INK, sw=1.6))

    # праворуч: наслідок — той самий код, інший поворот
    f.append(rect(440, 150, 280, 130, fill="#eafaf0", stroke=OK, sw=1.8))
    f.append(mtext(580, 188,
                   "наслідок: той самий код малювання\nпрацює при будь-якому\nфізичному повороті панелі\nв корпусі — крутиш не код,\nа один регістр",
                   size=10.5, color=INK, lh=1.35))

    f.append(text(W / 2, 304,
                  "плутанина RGB/BGR — найчастіша причина «кольори інвертовані»: це біт MADCTL, не панель",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "madctl.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури вставки proj-init-driver
# ════════════════════════════════════════════════════════════════════════════

# ── 5. Формат запису команди в таблиці-даних (байтовий розклад) ──────────────
def fig_record():
    W, H = 760, 360
    f = [text(W / 2, 28, "Один запис таблиці = один крок ініціалізації", size=16, bold=True)]

    # стрічка байтів
    cells = [
        ("cmd",     "0x11",  TFT,  "#eef4f8", "код команди"),
        ("n_args",  "0x00",  COLD, "#eef1f4", "скільки\nбайтів далі"),
        ("delay",   "120",   GOLD, "#fff8e6", "пауза\nпісля, мс"),
    ]
    x0, y0, cw, ch = 120, 70, 150, 60
    for i, (name, val, col, fill, note) in enumerate(cells):
        x = x0 + i * (cw + 6)
        f.append(rect(x, y0, cw, ch, fill=fill, stroke=col, sw=2))
        f.append(text(x + cw / 2, y0 + 24, name, size=12, color=col, bold=True))
        f.append(text(x + cw / 2, y0 + 46, val, size=13, color=INK, bold=True))
        f.append(mtext(x + cw / 2, y0 + ch + 18, note, size=9.5, color=MUTED, lh=1.2))

    # приклад із аргументами
    yy = 210
    f.append(text(W / 2, yy - 14, "а запис із аргументами розгортається так:", size=11, color=INK))
    ex = [
        ("0x3A", TFT,  "cmd\nCOLMOD"),
        ("0x01", COLD, "n_args\n= 1"),
        ("0",    GOLD, "delay\n= 0"),
        ("0x55", OK,   "арг 0\nRGB565"),
    ]
    x0 = 150; cw = 110
    for i, (val, col, note) in enumerate(ex):
        x = x0 + i * (cw + 6)
        fill = "#eafaf0" if i == 3 else FILL
        f.append(rect(x, yy, cw, 44, fill=fill, stroke=col, sw=1.8))
        f.append(text(x + cw / 2, yy + 27, val, size=12, color=INK, bold=True))
        f.append(mtext(x + cw / 2, yy + 62, note, size=9, color=col, lh=1.2))

    f.append(text(W / 2, 326,
                  "уся послідовність — масив таких записів у флеші; інтерпретатор прокручує його згори вниз",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "record.svg"), W, H, *f)


# ── 6. Одна машина — різні панелі: інтерпретатор живить таблиці ──────────────
def fig_one_machine():
    W, H = 760, 360
    f = [text(W / 2, 28, "Одна машина-інтерпретатор, різні таблиці", size=16, bold=True)]

    # дві таблиці зліва
    tabs = [
        (70,  "таблиця ST7789", TFT,  "MADCTL 0x08\nINVON  0x21\nNORON  0x13"),
        (70,  "таблиця ILI9341", GOLD, "MADCTL 0x48\nINVOFF 0x20\n+ вектори\nживлення"),
    ]
    ty = 70
    for i, (x, name, col, body) in enumerate(tabs):
        yy = ty + i * 110
        f.append(rect(x, yy, 200, 96, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + 100, yy + 22, name, size=11.5, color=col, bold=True))
        f.append(mtext(x + 100, yy + 42, body, size=9.5, color=MUTED, lh=1.25))

    # інтерпретатор у центрі
    cx, cyb = 330, 120
    f.append(rect(cx, cyb, 180, 120, fill="#eef4f8", stroke=INK, sw=2.2))
    f.append(text(cx + 90, cyb + 26, "run_init_table()", size=12, color=INK, bold=True))
    f.append(mtext(cx + 90, cyb + 50,
                   "прокрутити записи\nтримати D/C і CS\nвідпрацювати паузи\nловити збій шини",
                   size=9.5, color=MUTED, lh=1.3))

    f.append(arrow(270, ty + 48, cx, cyb + 40, color=INK, sw=1.8))
    f.append(arrow(270, ty + 110 + 48, cx, cyb + 80, color=INK, sw=1.8))

    # панелі справа
    pans = [
        (600, "ST7789",  OK),
        (600, "ILI9341", OK),
    ]
    for i, (x, name, col) in enumerate(pans):
        yy = 90 + i * 100
        f.append(rect(x, yy, 110, 70, fill="#eafaf0", stroke=col, sw=1.8))
        f.append(text(x + 55, yy + 30, name, size=12, color=col, bold=True))
        f.append(text(x + 55, yy + 52, "оживає", size=9.5, color=MUTED, italic=True))
    f.append(arrow(cx + 180, cyb + 35, 600, 125, color=INK, sw=1.8))
    f.append(arrow(cx + 180, cyb + 85, 600, 225, color=INK, sw=1.8))

    f.append(text(W / 2, 320,
                  "код інтерпретатора не змінюється — змінюється лише таблиця-даних під панель",
                  size=11, color=INK))
    f.append(text(W / 2, 344,
                  "нова панель = новий масив байтів, а не новий драйвер",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "one_machine.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури вставки hist-magic-numbers
# ════════════════════════════════════════════════════════════════════════════

# ── 7. Звідки беруться магічні числа: ланцюг рук ─────────────────────────────
def fig_provenance():
    W, H = 780, 360
    f = [text(W / 2, 28, "Звідки беруться «магічні числа»: ланцюг рук", size=16, bold=True)]

    nodes = [
        (140, "Виробник\nкремнію", "ILITEK · Sitronix ·\nGalaxycore",
         "знає КОЖЕН біт,\nале мовчить (NDA)", POS, "#fdecea"),
        (390, "Виробник\nпанелі", "BuyDisplay · EastRising ·\nбезіменна фабрика",
         "дає init-код таблицею,\nсам пояснень не має", GOLD, "#fff8e6"),
        (640, "Спільнота\n(бібліотеки)", "Adafruit · TFT_eSPI ·\nlvgl · u8g2",
         "копіює числа як є,\nревершить решту", OK, "#eafaf0"),
    ]
    bw, by, bh = 210, 80, 150
    for cx, title, who, note, col, fill in nodes:
        x = cx - bw / 2
        f.append(rect(x, by, bw, bh, fill=fill, stroke=col, sw=2))
        f.append(mtext(cx, by + 26, title, size=13, color=col, bold=True, lh=1.2))
        f.append(mtext(cx, by + 76, who, size=9.5, color=INK, lh=1.3))
        f.append(mtext(cx, by + 118, note, size=9.5, color=MUTED, lh=1.3))

    # стрілки з підписом «що передають»
    ax1a, ax1b = 140 + bw / 2, 390 - bw / 2
    f.append(arrow(ax1a, by + bh / 2, ax1b, by + bh / 2, color=INK, sw=2.2))
    f.append(text((ax1a + ax1b) / 2, by + bh / 2 - 10, "готова таблиця", size=9.5, color=INK, italic=True))
    f.append(text((ax1a + ax1b) / 2, by + bh / 2 + 16, "без пояснень", size=9, color=MUTED, italic=True))

    ax2a, ax2b = 390 + bw / 2, 640 - bw / 2
    f.append(arrow(ax2a, by + bh / 2, ax2b, by + bh / 2, color=INK, sw=2.2))
    f.append(text((ax2a + ax2b) / 2, by + bh / 2 - 10, "ті самі байти", size=9.5, color=INK, italic=True))
    f.append(text((ax2a + ax2b) / 2, by + bh / 2 + 16, "у git назавжди", size=9, color=MUTED, italic=True))

    f.append(text(W / 2, 290,
                  "пояснення лишається на першому щаблі — і вниз ланцюгом НЕ передається",
                  size=11, color=INK))
    f.append(text(W / 2, 320,
                  "тому число «працює», та чому саме таке — не знає вже ніхто, хто його копіює",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "provenance.svg"), W, H, *f)


# ── 8. Угода 0x80: лічильник аргументів ховає прапорець паузи ────────────────
def fig_delay_flag():
    W, H = 780, 430
    f = [text(W / 2, 28, "Угода 0x80: лічильник аргументів ховає прапорець паузи", size=15, bold=True)]

    # 8 бітів байта-лічильника
    bx, by, cell = 250, 58, 36
    for i in range(8):
        x = bx + i * cell
        col = POS if i == 0 else TFT
        fill = "#fdecea" if i == 0 else "#eef4f8"
        f.append(rect(x, by, cell, cell, fill=fill, stroke=col, sw=1.8, rx=3))
        f.append(text(x + cell / 2, by + 23, "1" if i == 0 else "n", size=13, color=col, bold=True))
    # дужки знизу: біт7 проти бітів0..6
    f.append(line(bx + 2, by + cell + 8, bx + cell - 2, by + cell + 8, color=POS, sw=2))
    f.append(text(bx + cell / 2, by + cell + 26, "біт 7", size=10, color=POS, bold=True))
    f.append(text(bx + cell / 2, by + cell + 42, "0x80 = чекати", size=8.5, color=MUTED))
    f.append(line(bx + cell + 2, by + cell + 8, bx + 8 * cell - 2, by + cell + 8, color=TFT, sw=2))
    f.append(text(bx + cell * 4.5, by + cell + 26, "біти 0..6", size=10, color=TFT, bold=True))
    f.append(text(bx + cell * 4.5, by + cell + 42, "число аргументів (& 0x7F)", size=8.5, color=MUTED))

    # масив-таблиця: приклад чотирьох записів
    y0 = 196
    f.append(text(W / 2, y0 - 12, "той самий масив тримає команди, аргументи й паузи поспіль",
                  size=11, color=INK))
    rows = [
        ("0x11,", "0x80,", "",                        "SLPOUT + пауза (біт7=1)", GOLD),
        ("0x3A,", "0x01,", "0x55,",                   "COLMOD, 1 аргумент",       TFT),
        ("0xE0,", "0x0F,", "0x31, 0x2B, … (15 байт)", "гама+, 15 аргументів",     COLD),
        ("0x29,", "0x80,", "",                        "DISPON + пауза (біт7=1)",  OK),
    ]
    x, w, rh = 80, 620, 38
    f.append(text(x + 14,  y0 + 6, "cmd",       size=9, color=MUTED, anchor="start", bold=True))
    f.append(text(x + 100, y0 + 6, "лічильник", size=9, color=MUTED, anchor="start", bold=True))
    f.append(text(x + 210, y0 + 6, "аргументи", size=9, color=MUTED, anchor="start", bold=True))
    for i, (c, cnt, args, note, col) in enumerate(rows):
        yy = y0 + 14 + i * (rh + 4)
        f.append(rect(x, yy, w, rh, fill=FILL, stroke=col, sw=1.5))
        f.append(text(x + 14,  yy + 24, c,    size=12, color=col, bold=True, anchor="start"))
        cc = POS if cnt == "0x80," else INK
        f.append(text(x + 100, yy + 24, cnt,  size=12, color=cc, bold=(cnt == "0x80,"), anchor="start"))
        f.append(text(x + 210, yy + 24, args, size=11, color=INK, anchor="start"))
        f.append(text(x + 420, yy + 24, note, size=9.5, color=MUTED, anchor="start", italic=True))

    f.append(text(W / 2, 410,
                  "інтерпретатор прокручує масив: лічильник каже, скільки байтів пропустити, біт 7 — чи чекати",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "delay_flag.svg"), W, H, *f)


if __name__ == "__main__":
    fig_states()
    fig_anatomy()
    fig_timing()
    fig_madctl()
    fig_record()
    fig_one_machine()
    fig_provenance()
    fig_delay_flag()
    print("OK: 8 figures ->", IMG)
