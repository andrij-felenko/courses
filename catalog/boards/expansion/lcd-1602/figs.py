# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Символьний дисплей LCD 1602A».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Анатомія: скло з клітинками + HD44780 + три пам'яті ─────────────────────
def fig_lcd_anatomy():
    W, H = 860, 470
    f = [text(W / 2, 30, "Усередині 1602A: контролер із трьома пам'ятями керує склом",
              size=16, bold=True)]

    # Мікроконтролер зліва
    mcx, mcy = 90, 235
    f.append(rect(mcx - 52, mcy - 45, 104, 90, fill="#eef2f8", stroke=INK, sw=1.7, rx=10))
    f.append(text(mcx, mcy - 8, "Мікро-", size=12, bold=True))
    f.append(text(mcx, mcy + 10, "контролер", size=12, bold=True))

    # стрілка з підписом «код символу»
    f.append(arrow(mcx + 52, mcy, 250, mcy, color=NEG, sw=2.4))
    f.append(text((mcx + 52 + 250) / 2, mcy - 12, "код символу", size=11, bold=True, color=NEG))
    f.append(text((mcx + 52 + 250) / 2, mcy + 22, "(напр. 65 = «A»)", size=9.5, color=MUTED))

    # Межа контролера/плати
    bx, by, bw, bh = 250, 70, 360, 330
    f.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke=MUTED, sw=1.6, rx=12))
    f.append(text(bx + 92, by + 22, "контролер HD44780", size=12, bold=True, color=MUTED))

    # три пам'яті — три акуратні блоки в колонку
    memx = bx + 100
    def mem(cy, tag, name, desc, col, fill):
        w, h = 190, 62
        f.append(rect(memx - w / 2, cy - h / 2, w, h, fill=fill, stroke=col, sw=1.7, rx=8))
        f.append(text(memx, cy - 14, tag, size=12, bold=True, color=col))
        f.append(text(memx, cy + 4, name, size=9.5, color=INK))
        f.append(text(memx, cy + 20, desc, size=9, color=MUTED))

    mem(by + 78, "DDRAM", "що зараз на екрані", "80 комірок-символів", NEG, "#eaf0fd")
    mem(by + 165, "CGROM", "заводські картинки", "~200 готових знаків", POS, "#fdecea")
    mem(by + 252, "CGRAM", "ваші символи", "до 8 власних 5×8", FIELD, "#eef6ef")

    # Скло праворуч — сітка клітинок 16×2 (спрощено 8×2 показові)
    gx, gy = 660, 150
    cols, rows = 8, 2
    cw, ch = 20, 28
    f.append(text(gx + cols * cw / 2, gy - 16, "скло: клітинки 16×2", size=11, bold=True))
    demo = ["HELLO 42", "T=23.5 C"]
    for r in range(rows):
        for c in range(cols):
            cx0 = gx + c * cw
            cy0 = gy + r * (ch + 6)
            f.append(rect(cx0, cy0, cw - 3, ch, fill="#dfe8dd", stroke=FIELD, sw=1.0, rx=2))
            ch_txt = demo[r][c] if c < len(demo[r]) else ""
            if ch_txt.strip():
                f.append(text(cx0 + (cw - 3) / 2, cy0 + ch - 8, ch_txt, size=13, bold=True, color="#1e5631"))

    # стрілка від пам'ятей до скла: «запалює крапки»
    f.append(arrow(bx + bw, by + 165, gx - 6, gy + ch, color=FIELD, sw=2.2))
    f.append(text((bx + bw + gx) / 2 + 6, by + 150, "запалює", size=10, color=FIELD, bold=True))
    f.append(text((bx + bw + gx) / 2 + 6, by + 166, "крапки", size=10, color=FIELD, bold=True))

    b, _, _ = textbox(W / 2, 445,
                      "плата не малює букви — лише передає їхні коди; уся робота з крапками у контролері",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "lcd-anatomy.svg"), W, H, *f)


# ── 2. Дві шини: 8-бітна (11 ніжок) проти 4-бітної (6 ніжок) ───────────────────
def fig_bus_4bit_8bit():
    W, H = 820, 470
    f = [text(W / 2, 30, "Дві шини до дисплея: цілий байт чи двома напівбайтами",
              size=16, bold=True)]

    cw = 350
    lx, rx = 45, W - 45 - cw
    topY = 58
    boxH = 330

    def panel(px, title, sub, accent, fill, datalines, note, pincount):
        f.append(rect(px, topY, cw, boxH, fill=fill, stroke=accent, sw=1.8, rx=10))
        f.append(text(px + cw / 2, topY + 26, title, size=14, bold=True, color=accent))
        f.append(text(px + cw / 2, topY + 45, sub, size=10.5, color=MUTED))

        # МК ліворуч, дисплей праворуч
        mx = px + 52
        dx = px + cw - 52
        my = topY + 150
        f.append(rect(mx - 34, my - 55, 68, 110, fill=BG, stroke=INK, sw=1.6, rx=8))
        f.append(text(mx, my - 4, "МК", size=12, bold=True))
        f.append(rect(dx - 34, my - 55, 68, 110, fill=BG, stroke=INK, sw=1.6, rx=8))
        f.append(text(dx, my - 6, "LCD", size=12, bold=True))
        f.append(text(dx, my + 12, "1602A", size=9, color=MUTED))

        # лінії даних
        n = len(datalines)
        y0 = my - (n - 1) * 15 / 2
        for i, (lbl, col) in enumerate(datalines):
            ly = y0 + i * 15
            f.append(line(mx + 34, ly, dx - 34, ly, color=col, sw=2.0))
            f.append(text(px + cw / 2, ly - 4, lbl, size=9, color=col, bold=True))

        # підсумок: скільки виводів
        f.append(text(px + cw / 2, topY + boxH - 52, note, size=10.5, color=INK, italic=True))
        pb, _, _ = textbox(px + cw / 2, topY + boxH - 24, pincount,
                           size=12, fill=BG, stroke=accent, bold=True)
        f.append(pb)

    panel(lx, "8-бітний режим", "усі лінії D0–D7 задіяні", NEG, "#eef2f8",
          [("D0..D3", INK), ("D4..D7", INK),
           ("RS", MUTED), ("RW", MUTED), ("E", POS)],
          "байт іде цілком за один строб E",
          "потрібно 11 виводів")

    panel(rx, "4-бітний режим", "лише старші D4–D7", FIELD, "#eef6ef",
          [("D4..D7", FIELD),
           ("RS", MUTED), ("RW", MUTED), ("E", POS)],
          "байт — двома напівбайтами, два строби E",
          "потрібно 6 виводів")

    b, _, _ = textbox(W / 2, 452,
                      "видимої різниці у швидкості немає — на практиці беруть 4-бітний, аби заощадити ніжки",
                      size=11.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "bus-4bit-8bit.svg"), W, H, *f)


# ── 3. Розводка пін-у-пін: 1602A ↔ Arduino (4-бітний режим) ────────────────────
def fig_lcd_wiring():
    W, H = 880, 620
    f = [text(W / 2, 30, "Розводка 1602A до мікроконтролера (4-бітний режим)",
              size=16, bold=True)]

    # Дисплей ліворуч: колонка з ніжками
    lx = 70
    pins = [
        ("1 VSS", "GND", INK),
        ("2 VDD", "+5 В", POS),
        ("3 VO", "повзунок 10 кОм", FIELD),
        ("4 RS", "вивід (D8)", NEG),
        ("5 RW", "GND", INK),
        ("6 E", "вивід (D9)", POS),
        ("11 D4", "D4", NEG),
        ("12 D5", "D5", NEG),
        ("13 D6", "D6", NEG),
        ("14 D7", "D7", NEG),
        ("15 A", "+5 В через R", POS),
        ("16 K", "GND", INK),
    ]
    n = len(pins)
    rowH = 36
    top = 70
    boxW = 150
    # корпус дисплея
    f.append(rect(lx - 12, top - 14, boxW + 24, n * rowH + 20, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(lx + boxW / 2, top - 24, "LCD 1602A", size=12, bold=True, color="#1e5631"))

    # права колонка — куди йде
    rx = lx + boxW + 250
    f.append(rect(rx - 12, top - 14, 200, n * rowH + 20, fill="#eef2f8", stroke=INK, sw=1.6, rx=10))
    f.append(text(rx + 90, top - 24, "Arduino (приклад)", size=12, bold=True))

    for i, (pin, dest, col) in enumerate(pins):
        y = top + i * rowH + rowH / 2
        # ніжка дисплея
        f.append(text(lx + 4, y + 4, pin, size=11, bold=True, anchor="start"))
        # точка виходу
        px_out = lx + boxW
        f.append(circle(px_out, y, 3.5, fill=col, stroke=col, sw=1))
        # призначення праворуч
        f.append(text(rx + 6, y + 4, dest, size=10.5, color=col, anchor="start", bold=True))
        px_in = rx
        f.append(circle(px_in, y, 3.5, fill=col, stroke=col, sw=1))
        # з'єднання
        f.append(line(px_out, y, px_in, y, color=col, sw=1.8))

    # потенціометр — окрема пояснювальна вставка внизу ліворуч від зв'язків VO
    poty = top + 2 * rowH + rowH / 2  # рядок VO (індекс 2)
    # маленький значок дільника біля VO-призначення
    ptx = (px_out + rx) / 2
    f.append(text(ptx, poty - 12, "потенціометр", size=9, color=FIELD, bold=True))

    # Легенда-нота
    b1, w1, h1 = textbox(W / 2, H - 66,
                         "VO — тільки через потенціометр (крайні ніжки: +5 В і GND); RW на землі — лише запис",
                         size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b1)
    b2, _, _ = textbox(W / 2, H - 30,
                       "A (підсвітка) — через струмообмежувальний резистор, якщо його немає на платі; D0–D3 не під'єднані",
                       size=11, fill=FILL, stroke=LINE)
    f.append(b2)
    render(os.path.join(IMG, "lcd-wiring.svg"), W, H, *f)


# ── 4. Родовід HD44780: оригінал задав інтерфейс, копії його повторюють ────────
def fig_hd44780_lineage():
    W, H = 900, 540
    f = [text(W / 2, 32, "Стандартом став не чип Hitachi, а його інтерфейс",
              size=16, bold=True)]

    # Оригінал зверху по центру
    ox, oy = W / 2, 108
    ow, oh = 260, 74
    f.append(rect(ox - ow / 2, oy - oh / 2, ow, oh, fill="#eef2f8", stroke=NEG, sw=2.2, rx=12))
    f.append(text(ox, oy - 12, "HD44780", size=17, bold=True, color=NEG))
    f.append(text(ox, oy + 9, "Hitachi, середина-кінець 1980-х", size=10, color=MUTED))
    f.append(text(ox, oy + 25, "(оригінал знято з випуску)", size=9, color=MUTED, italic=True))

    # Що саме він задав — три «гени» стандарту, вузька смуга під оригіналом
    genes = ["набір команд", "розкладка ніжок", "часова діаграма"]
    gy = 214
    gw, gap = 200, 24
    total = len(genes) * gw + (len(genes) - 1) * gap
    gx0 = (W - total) / 2
    # підпис зсунуто вліво від центрального трунка, щоб стрілка не різала напис
    f.append(text(gx0, gy - 22, "задав інтерфейс:", size=11, bold=True, color=INK, anchor="end"))
    gene_cx = []
    for i, g in enumerate(genes):
        cx = gx0 + i * (gw + gap) + gw / 2
        gene_cx.append(cx)
        f.append(rect(cx - gw / 2, gy, gw, 40, fill="#f0f4fb", stroke=NEG, sw=1.4, rx=8))
        f.append(text(cx, gy + 25, g, size=12, bold=True, color=INK))
    # стрілка від оригіналу до смуги «генів»
    f.append(arrow(ox, oy + oh / 2, ox, gy - 8, color=NEG, sw=2.2))

    # Копії внизу — п'ять карток, кожна повторює той самий інтерфейс
    clones = [
        ("KS0066", "Samsung", "Корея"),
        ("ST7066", "Sitronix", "Тайвань"),
        ("SPLC780", "Sunplus", "Тайвань"),
        ("AIP31066", "Wuxi i-Core", "Китай"),
        ("WS0010", "Winstar", "Тайвань"),
    ]
    cy = 408
    cw2, cgap = 150, 18
    tot2 = len(clones) * cw2 + (len(clones) - 1) * cgap
    cx0 = (W - tot2) / 2
    # підпис — ліворуч від центрального трунка (anchor=start), щоб вертикальна
    # стрілка не різала напис; трунк іде рівно центром у проміжку між ним і картками
    f.append(text(cx0, cy - 50, "той самий інтерфейс повторюють копії — прямі замінники:",
                  size=11, bold=True, color=FIELD, anchor="start"))
    # роздавальна шина: одна стрілка вниз від «генів» → горизонтальний рейл у чистому
    # проміжку (нижче підпису, вище карток) → короткі вертикальні спуски в кожну картку.
    railY = cy - 20
    f.append(arrow(gene_cx[1], gy + 40, gene_cx[1], railY, color=FIELD, sw=1.6))
    card_cx = [cx0 + i * (cw2 + cgap) + cw2 / 2 for i in range(len(clones))]
    f.append(line(card_cx[0], railY, card_cx[-1], railY, color=FIELD, sw=1.6))
    for i, (chip, mfr, land) in enumerate(clones):
        cx = card_cx[i]
        f.append(arrow(cx, railY, cx, cy - 2, color=FIELD, sw=1.3))
        f.append(rect(cx - cw2 / 2, cy, cw2, 78, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=10))
        f.append(text(cx, cy + 24, chip, size=13, bold=True, color="#1e5631"))
        f.append(text(cx, cy + 45, mfr, size=10.5, color=INK))
        f.append(text(cx, cy + 63, land, size=9, color=MUTED))

    b, _, _ = textbox(W / 2, 520,
                      "оригінал помер — формат живе: надто багато всього на нього спирається",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "hd44780-lineage.svg"), W, H, *f)


# ── 5. Власний символ у CGRAM: байт-рядок → рядок крапок (значок градуса) ───────
def fig_cgram_degree():
    W, H = 820, 500
    f = [text(W / 2, 30, "Власний символ у CGRAM: вісім байтів → картинка 5×8",
              size=16, bold=True)]

    # Малюнок градуса: 8 рядків по 5 біт (молодші 5 біт кожного байта)
    rows = [
        [0, 1, 1, 0, 0],
        [1, 0, 0, 1, 0],
        [1, 0, 0, 1, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]

    top = 84
    rowH = 44
    # Ліворуч — байти як двійкові літерали (значущі 5 біт кольорові)
    lx = 70
    f.append(text(lx + 88, top - 26, "байт у коді", size=12, bold=True, anchor="start"))
    f.append(text(lx + 88, top - 10, "старші 3 біти ігноруються", size=9,
                  color=MUTED, anchor="start"))

    # Праворуч — сітка крапок 5×8
    gx = 560
    cell = 40
    f.append(text(gx + 5 * cell / 2, top - 16, "клітинка 5×8 на склі", size=12, bold=True))

    bw = 15
    for r, bits in enumerate(rows):
        y = top + r * rowH
        cy = y + rowH / 2

        # двійковий літерал: 0b + 3 сірих старших нулі + 5 значущих біт
        f.append(text(lx, cy + 4, "0b", size=13, color=MUTED, anchor="start", bold=True))
        bx0 = lx + 30
        for k in range(3):
            f.append(text(bx0 + k * bw, cy + 4, "0", size=13, color="#b8bcc4",
                          anchor="middle"))
        for k, b in enumerate(bits):
            col = FIELD if b else MUTED
            f.append(text(bx0 + (3 + k) * bw, cy + 4, str(b), size=13,
                          color=col, bold=bool(b), anchor="middle"))

        # стрілка від літерала до рядка крапок
        f.append(arrow(bx0 + 8 * bw + 10, cy, gx - 8, cy, color=MUTED, sw=1.6))

        # рядок крапок 5×8 праворуч
        for k, b in enumerate(bits):
            x0 = gx + k * cell
            fill = "#1e5631" if b else "#e6ece6"
            f.append(rect(x0, y + 4, cell - 4, rowH - 8,
                          fill=fill, stroke=FIELD, sw=1.0, rx=3))

    b, _, _ = textbox(W / 2, H - 26,
                      "1 світить крапку, 0 гасить; createChar кладе ці 8 байтів у комірку 0–7, write(byte(n)) показує символ",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "cgram-degree.svg"), W, H, *f)


# ── 6. Ініціалізаційна послідовність у 4-бітний режим ──────────────────────────
def fig_init_sequence():
    W, H = 940, 740
    f = [text(W / 2, 30, "Оживлення контролера: надійний шлях у 4-бітний режим",
              size=16, bold=True)]

    cx = 250
    boxW = 330
    boxH = 42
    top = 62
    gap = 18

    steps = [
        ("чекати >= 40 мс", "живлення встоялося, контролер очуняється", MUTED, "#f1f3f5"),
        ("напівбайт 0011", "пауза > 4.1 мс", NEG, "#eaf0fd"),
        ("напівбайт 0011", "пауза > 100 мкс", NEG, "#eaf0fd"),
        ("напівбайт 0011", "контролер точно у 8-бітному режимі", NEG, "#eaf0fd"),
        ("напівбайт 0010", "перемкнути у 4-бітний режим", POS, "#fdecea"),
        ("0x28  Function Set", "4 біти . 2 рядки . шрифт 5x8", FIELD, "#eef6ef"),
        ("0x08  Display OFF", "тихо налаштовуємось", FIELD, "#eef6ef"),
        ("0x01  Clear (~1.52 мс)", "стерти екран, курсор -> (0,0)", FIELD, "#eef6ef"),
        ("0x06  Entry Mode", "курсор рухається вправо", FIELD, "#eef6ef"),
        ("0x0C  Display ON", "екран увімкнено, курсор вимкнено", FIELD, "#eef6ef"),
    ]

    y = top
    prev_cy = None
    for i, (title, sub, col, fill) in enumerate(steps):
        cy = y + boxH / 2
        if prev_cy is not None:
            f.append(arrow(cx, prev_cy + boxH / 2, cx, y, color=MUTED, sw=1.7))
        f.append(rect(cx - boxW / 2, y, boxW, boxH, fill=fill, stroke=col, sw=1.7, rx=8))
        f.append(text(cx - boxW / 2 + 14, cy - 3, title, size=12, bold=True,
                      color=col, anchor="start"))
        f.append(text(cx - boxW / 2 + 14, cy + 13, sub, size=9, color=MUTED,
                      anchor="start"))
        prev_cy = cy
        y += boxH + gap

    # Праворуч — дві дужки-пояснення фаз
    rx = cx + boxW / 2 + 46
    y1a = top + (boxH + gap) * 1
    y1b = top + (boxH + gap) * 4 + boxH
    f.append(line(rx, y1a, rx, y1b, color=NEG, sw=2.2))
    f.append(line(rx, y1a, rx - 8, y1a, color=NEG, sw=2.2))
    f.append(line(rx, y1b, rx - 8, y1b, color=NEG, sw=2.2))
    b1, _, _ = textbox(rx + 120, (y1a + y1b) / 2,
                       "самі напівбайти,\nкожен зі стробом E",
                       size=10.5, fill="#eaf0fd", stroke=NEG, color=NEG)
    f.append(b1)

    y2a = top + (boxH + gap) * 5
    y2b = top + (boxH + gap) * 9 + boxH
    f.append(line(rx, y2a, rx, y2b, color=FIELD, sw=2.2))
    f.append(line(rx, y2a, rx - 8, y2a, color=FIELD, sw=2.2))
    f.append(line(rx, y2b, rx - 8, y2b, color=FIELD, sw=2.2))
    b2, _, _ = textbox(rx + 120, (y2a + y2b) / 2,
                       "повні байти:\nдва напівбайти\nна команду",
                       size=10.5, fill="#eef6ef", stroke=FIELD, color=FIELD)
    f.append(b2)

    b, _, _ = textbox(W / 2, H - 22,
                      "усе це згорнуто в один виклик lcd.begin(16, 2)",
                      size=11.5, fill=FILL, stroke=LINE, bold=True)
    f.append(b)
    render(os.path.join(IMG, "init-sequence.svg"), W, H, *f)


if __name__ == "__main__":
    fig_lcd_anatomy()
    fig_bus_4bit_8bit()
    fig_lcd_wiring()
    fig_hd44780_lineage()
    fig_cgram_degree()
    fig_init_sequence()
    print("OK: 6 figures ->", IMG)
