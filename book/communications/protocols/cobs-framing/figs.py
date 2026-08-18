# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. framing-problem: проблема розділювача в потоці байтів ─────────────────
def fig_framing_problem():
    W, H = 840, 360
    p = []

    p.append(rect(15, 15, 810, 330, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))

    # Секція А: Наївний потік із нулем-розділювачем
    p.append(text(35, 45, "Необроблений двійковий потік (UART / RS-485):", size=13, color=INK, bold=True, anchor="start"))
    
    # Клітинки байтів
    cells_a = [
        ("0xAA", "#eaf0fd", NEG, "Дані"),
        ("0x00", "#fdecea", POS, "Нуль у float!"),
        ("0x42", "#eaf0fd", NEG, "Дані"),
        ("0x13", "#eaf0fd", NEG, "Дані"),
        ("0x00", "#eef6ef", FIELD, "Справжній кінець"),
        ("0x55", "#eaf0fd", NEG, "Дані 2"),
        ("0x77", "#eaf0fd", NEG, "Дані 2"),
    ]
    
    x0, y0, cw, ch = 35, 65, 78, 44
    for i, (val, fill_c, strk, lbl) in enumerate(cells_a):
        cx = x0 + i * (cw + 12)
        p.append(rect(cx, y0, cw, ch, fill=fill_c, stroke=strk, sw=1.5, rx=4))
        p.append(text(cx + cw/2, y0 + 26, val, size=13, color=INK, bold=True))
        p.append(text(cx + cw/2, y0 + ch + 18, lbl, size=10, color=strk, bold=True))

    # Хибне розбиття приймачем
    p.append(line(35 + cw + 6, y0 - 10, 35 + cw + 6, y0 + ch + 30, color=POS, sw=2, dash="4 3"))
    p.append(text(35 + cw + 6, y0 - 16, "Хибна межа кадру!", size=10.5, color=POS, bold=True))

    p.append(line(35 + 4*(cw + 12) + cw + 6, y0 - 10, 35 + 4*(cw + 12) + cw + 6, y0 + ch + 30, color=FIELD, sw=2))
    p.append(text(35 + 4*(cw + 12) + cw + 6, y0 - 16, "Реальна межа", size=10.5, color=FIELD, bold=True))

    # Секція Б: Наслідки байт-стаффінгу SLIP/PPP
    p.append(line(35, 175, 805, 175, color="#e1e4e8", sw=1.2))
    p.append(text(35, 205, "Класичний байт-стаффінг (SLIP / PPP): екранування подвоює байти", size=13, color=INK, bold=True, anchor="start"))

    slip_cells = [
        ("0xAA", "#eaf0fd", NEG, "Дані"),
        ("0xDB", "#fff3cd", "#e0a800", "ESC"),
        ("0xDC", "#fff3cd", "#e0a800", "ESC_NUL"),
        ("0x42", "#eaf0fd", NEG, "Дані"),
        ("0x13", "#eaf0fd", NEG, "Дані"),
        ("0xC0", "#eef6ef", FIELD, "END (0xC0)"),
    ]

    y1 = 225
    for i, (val, fill_c, strk, lbl) in enumerate(slip_cells):
        cx = x0 + i * (cw + 12)
        p.append(rect(cx, y1, cw, ch, fill=fill_c, stroke=strk, sw=1.5, rx=4))
        p.append(text(cx + cw/2, y1 + 26, val, size=13, color=INK, bold=True))
        p.append(text(cx + cw/2, y1 + ch + 18, lbl, size=10, color=strk, bold=True))

    # Коментар праворуч про роздуття буфера
    t_box, _, _ = textbox(660, 250, "Найгірший випадок SLIP:\nкожен байт 0x00/0xDB → 2 байти.\nРозмір буфера зростає до 200%!", size=10.5, pad=8, fill="#fff8e6", stroke="#d97706", sw=1.2, color="#92400e")
    p.append(t_box)

    render(os.path.join(OUT, "framing-problem.svg"), W, H, *p,
           title="Проблема виявлення меж кадру в двійковому потоці даних")


# ── 2. cobs-encoding-mechanism: принцип розбиття на блоки й покажчики ────────
def fig_cobs_encoding_mechanism():
    W, H = 840, 420
    p = []

    p.append(rect(15, 15, 810, 390, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))

    # Вихідне повідомлення
    p.append(text(35, 45, "1. Вхідний масив байтів із нулями (Payload):", size=13, color=INK, bold=True, anchor="start"))
    
    src_bytes = [
        ("0x22", "#ffffff", LINE),
        ("0x00", "#fdecea", POS),
        ("0x45", "#ffffff", LINE),
        ("0x67", "#ffffff", LINE),
        ("0x89", "#ffffff", LINE),
        ("0x00", "#fdecea", POS),
        ("0xAA", "#ffffff", LINE),
    ]

    x0, y0, cw, ch = 40, 60, 68, 38
    for i, (val, fill_c, strk) in enumerate(src_bytes):
        cx = x0 + i * (cw + 8)
        p.append(rect(cx, y0, cw, ch, fill=fill_c, stroke=strk, sw=1.4, rx=4))
        p.append(text(cx + cw/2, y0 + 24, val, size=12, color=INK, bold=True))
        if val == "0x00":
            p.append(text(cx + cw/2, y0 + ch + 14, "нуль", size=9.5, color=POS, bold=True))

    # Стрілка перетворення
    p.append(arrow(300, 128, 300, 152, color=MUTED, sw=1.6))
    p.append(text(315, 142, "Розбиття на блоки без нулів + префіксний покажчик зміщення", size=11, color=MUTED, italic=True, anchor="start"))

    # Закодоване повідомлення COBS
    p.append(text(35, 180, "2. Закодований кадр COBS (жодного нуля всередині тіла!):", size=13, color=INK, bold=True, anchor="start"))

    cobs_bytes = [
        ("0x02", "#eef6ef", FIELD, "Зсув +2"),
        ("0x22", "#ffffff", LINE, "Дані 1"),
        ("0x04", "#eef6ef", FIELD, "Зсув +4"),
        ("0x45", "#ffffff", LINE, "Дані 2"),
        ("0x67", "#ffffff", LINE, "Дані 2"),
        ("0x89", "#ffffff", LINE, "Дані 2"),
        ("0x02", "#eef6ef", FIELD, "Зсув +2"),
        ("0xAA", "#ffffff", LINE, "Дані 3"),
        ("0x00", "#fdecea", POS, "Маркер кінця"),
    ]

    y1 = 200
    for i, (val, fill_c, strk, lbl) in enumerate(cobs_bytes):
        cx = x0 + i * (cw + 8)
        p.append(rect(cx, y1, cw, ch, fill=fill_c, stroke=strk, sw=1.6, rx=4))
        p.append(text(cx + cw/2, y1 + 24, val, size=12, color=INK, bold=True))
        p.append(text(cx + cw/2, y1 + ch + 14, lbl, size=9, color=strk, bold=True))

    # Стрілки зв'язку покажчиків (Pointer Chaining)
    # 0x02 вказує на 0x04
    p.append(line(x0 + cw/2, y1 - 4, x0 + cw/2, y1 - 18, color=FIELD, sw=1.6))
    p.append(line(x0 + cw/2, y1 - 18, x0 + 2*(cw+8) + cw/2, y1 - 18, color=FIELD, sw=1.6))
    p.append(arrow(x0 + 2*(cw+8) + cw/2, y1 - 18, x0 + 2*(cw+8) + cw/2, y1 - 4, color=FIELD, sw=1.6))
    p.append(text(x0 + cw + 4, y1 - 24, "+2 байти", size=10, color=FIELD, bold=True))

    # 0x04 вказує на 0x02 (позиція 6)
    p.append(line(x0 + 2*(cw+8) + cw/2, y1 - 4, x0 + 2*(cw+8) + cw/2, y1 - 18, color=FIELD, sw=1.6))
    p.append(line(x0 + 2*(cw+8) + cw/2, y1 - 18, x0 + 6*(cw+8) + cw/2, y1 - 18, color=FIELD, sw=1.6))
    p.append(arrow(x0 + 6*(cw+8) + cw/2, y1 - 18, x0 + 6*(cw+8) + cw/2, y1 - 4, color=FIELD, sw=1.6))
    p.append(text(x0 + 4*(cw+8) + cw/2, y1 - 24, "+4 байти", size=10, color=FIELD, bold=True))

    # 0x02 вказує на маркер кінця 0x00 (позиція 8)
    p.append(line(x0 + 6*(cw+8) + cw/2, y1 - 4, x0 + 6*(cw+8) + cw/2, y1 - 18, color=FIELD, sw=1.6))
    p.append(line(x0 + 6*(cw+8) + cw/2, y1 - 18, x0 + 8*(cw+8) + cw/2, y1 - 18, color=FIELD, sw=1.6))
    p.append(arrow(x0 + 8*(cw+8) + cw/2, y1 - 18, x0 + 8*(cw+8) + cw/2, y1 - 4, color=FIELD, sw=1.6))
    p.append(text(x0 + 7*(cw+8) + cw/2, y1 - 24, "+2 байти", size=10, color=FIELD, bold=True))

    # Пояснення правила 0xFF
    p.append(line(35, 290, 805, 290, color="#e1e4e8", sw=1.2))
    p.append(text(35, 320, "Спеціальний випадок: блок із 254 байтів без нулів (Код 0xFF)", size=12.5, color=INK, bold=True, anchor="start"))
    
    t_rule, _, _ = textbox(420, 360, "Код 0xFF позначає 254 байти даних без подальшого відновлення нуля (максимальний блок).\nКод 0x01 позначає нуль байтів даних, за якими одразу відновлюється нуль (0x00 0x00 у вихідних даних).", size=10.5, pad=8, fill="#f4f6f8", stroke="#6b7280", sw=1.2, color=INK)
    p.append(t_rule)

    render(os.path.join(OUT, "cobs-encoding-mechanism.svg"), W, H, *p,
           title="Механізм кодування COBS та ланцюжок покажчиків зміщення")


# ── 3. cobs-vs-slip-overhead: порівняння накладних витрат COBS та SLIP ────────
def fig_cobs_vs_slip_overhead():
    W, H = 840, 380
    p = []

    p.append(rect(15, 15, 810, 350, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))

    # Вісь X та Y графіка
    ox, oy = 90, 300
    gw, gh = 680, 220

    # Сітка
    for y_step in [0, 50, 100, 150, 200]:
        y_pos = oy - (y_step / 200.0) * gh
        p.append(line(ox, y_pos, ox + gw, y_pos, color="#e9ecef", sw=1))
        p.append(text(ox - 10, y_pos + 4, "%d%%" % y_step, size=10, color=MUTED, anchor="end"))

    # Осі
    p.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    p.append(line(ox, oy, ox, oy - gh - 15, color=LINE, sw=1.8))
    p.append(arrow(ox + gw, oy, ox + gw + 15, oy, color=LINE, sw=1.8))
    p.append(arrow(ox, oy - gh - 10, ox, oy - gh - 25, color=LINE, sw=1.8))

    p.append(text(ox + gw + 20, oy + 4, "Розмір N (байт)", size=11, color=INK, anchor="start", bold=True))
    p.append(text(ox - 10, oy - gh - 30, "Оверхед (%)", size=11, color=INK, anchor="start", bold=True))

    # Підписи осі X
    x_ticks = [
        (0, "0"),
        (100, "100"),
        (254, "254"),
        (500, "500"),
        (1000, "1000"),
        (1500, "1500"),
    ]
    for x_val, x_lbl in x_ticks:
        xp = ox + (x_val / 1500.0) * gw
        p.append(line(xp, oy, xp, oy + 5, color=LINE, sw=1.2))
        p.append(text(xp, oy + 18, x_lbl, size=10, color=MUTED, anchor="middle"))

    # Крива SLIP worst-case (100% надлишок, горизонтальна пряма на 100%)
    y_slip_worst = oy - (100.0 / 200.0) * gh
    p.append(line(ox + 5, y_slip_worst, ox + gw, y_slip_worst, color=POS, sw=2.2, dash="6 4"))
    p.append(text(ox + gw - 80, y_slip_worst - 10, "SLIP / PPP (Найгірший: +100%)", size=11, color=POS, bold=True, anchor="end"))

    # Крива SLIP середній випадок (~1.5% надлишок для випадкових даних)
    y_slip_avg = oy - (1.5 / 200.0) * gh
    p.append(line(ox + 5, y_slip_avg - 2, ox + gw, y_slip_avg - 2, color="#d97706", sw=1.8, dash="3 3"))
    p.append(text(ox + gw - 80, y_slip_avg - 14, "SLIP / PPP (Випадкові дані: ~1.5%)", size=10, color="#d97706", bold=True, anchor="end"))

    # Крива COBS worst-case (1 байт на 254 байти = ~0.4%, плюс 1 байт на початку)
    # N=1 -> 1 байт оверхеду (100%), N=10 -> 10%, N=254 -> 0.39%, N=500 -> 0.4%, N=1500 -> 0.4%
    cobs_pts = []
    for n in [1, 2, 5, 10, 20, 50, 100, 254, 500, 750, 1000, 1250, 1500]:
        oh_pct = ( (1.0 + (n // 254)) / float(n) ) * 100.0
        val_y = min(oh_pct, 190.0)
        xp = ox + (n / 1500.0) * gw
        yp = oy - (val_y / 200.0) * gh
        cobs_pts.append((xp, yp))

    for i in range(len(cobs_pts) - 1):
        p.append(line(cobs_pts[i][0], cobs_pts[i][1], cobs_pts[i+1][0], cobs_pts[i+1][1], color=FIELD, sw=2.5))

    p.append(text(ox + 420, oy - 22, "COBS: Гарантований максимум ≤ 0.4% (при N ≥ 254)", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(circle(ox + (254 / 1500.0) * gw, oy - (0.3937 / 200.0) * gh, 4, fill=FIELD, stroke=INK, sw=1.2))

    render(os.path.join(OUT, "cobs-vs-slip-overhead.svg"), W, H, *p,
           title="Порівняння відносних накладних витрат COBS та SLIP/PPP")


# ── 4. cobs-r-optimization: оптимізація COBS/R ───────────────────────────────
def fig_cobs_r_optimization():
    W, H = 840, 360
    p = []

    p.append(rect(15, 15, 810, 330, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))

    p.append(text(35, 45, "Оптимізація COBS/R (COBS Reduced): усунення кінцевого байта оверхеду", size=13, color=INK, bold=True, anchor="start"))

    # Варіант 1: Стандартний COBS
    p.append(text(35, 80, "Стандартний COBS (додає 1 байт на початку останнього блоку):", size=11.5, color=MUTED, bold=True, anchor="start"))
    
    std_cells = [
        ("0x03", "#eef6ef", FIELD, "Код 1"),
        ("0x11", "#ffffff", LINE, "Дані"),
        ("0x22", "#ffffff", LINE, "Дані"),
        ("0x03", "#eef6ef", FIELD, "Код 2 (+1 байт!)"),
        ("0x33", "#ffffff", LINE, "Дані"),
        ("0x44", "#ffffff", LINE, "Останній байт"),
        ("0x00", "#fdecea", POS, "Розділювач"),
    ]

    x0, y0, cw, ch = 40, 95, 85, 40
    for i, (val, fill_c, strk, lbl) in enumerate(std_cells):
        cx = x0 + i * (cw + 12)
        p.append(rect(cx, y0, cw, ch, fill=fill_c, stroke=strk, sw=1.5, rx=4))
        p.append(text(cx + cw/2, y0 + 25, val, size=12, color=INK, bold=True))
        p.append(text(cx + cw/2, y0 + ch + 15, lbl, size=9.5, color=strk, bold=True))

    p.append(line(35, 175, 805, 175, color="#e1e4e8", sw=1.2))

    # Варіант 2: COBS/R
    p.append(text(35, 205, "COBS/R: значення останнього байта (0x44) > довжина блоку (2) → код не потрібен!", size=11.5, color=FIELD, bold=True, anchor="start"))

    r_cells = [
        ("0x03", "#eef6ef", FIELD, "Код 1"),
        ("0x11", "#ffffff", LINE, "Дані"),
        ("0x22", "#ffffff", LINE, "Дані"),
        ("0x44", "#fff3cd", "#d97706", "Останній байт замість коду!"),
        ("0x33", "#ffffff", LINE, "Дані"),
        ("0x00", "#fdecea", POS, "Розділювач"),
    ]

    y1 = 220
    for i, (val, fill_c, strk, lbl) in enumerate(r_cells):
        cx = x0 + i * (cw + 12)
        p.append(rect(cx, y1, cw, ch, fill=fill_c, stroke=strk, sw=1.5, rx=4))
        p.append(text(cx + cw/2, y1 + 25, val, size=12, color=INK, bold=True))
        p.append(text(cx + cw/2, y1 + ch + 15, lbl, size=9.5, color=strk, bold=True))

    t_box, _, _ = textbox(520, 310, "Економія COBS/R: якщо значення останнього байта масиву перевищує довжину фінального блоку,\nбайт-покажчик не додається, а довжина обчислюється автоматично за позицією кінцевого 0x00.", size=10, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.2, color="#1b4332")
    p.append(t_box)

    render(os.path.join(OUT, "cobs-r-optimization.svg"), W, H, *p,
           title="Оптимізація кадрування COBS/R у кінцевому блоці")


# ── 5. streaming-fsm: автомат станів потокового декодера ─────────────────────
def fig_streaming_fsm():
    W, H = 840, 380
    p = []

    p.append(rect(15, 15, 810, 350, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(35, 45, "Скінченний автомат потокового декодера COBS (байт-за-байтом):", size=13, color=INK, bold=True, anchor="start"))

    # Стани
    # Стан 1: HUNT_DELIM
    s1, _, _ = textbox(130, 160, "ОЧІКУВАННЯ\nРОЗДІЛЮВАЧА\n(Синхронізація)", size=11, pad=12, fill="#fdecea", stroke=POS, sw=1.8, color=POS, bold=True)
    p.append(s1)

    # Стан 2: READ_CODE
    s2, _, _ = textbox(390, 160, "ЧИТАННЯ\nПОКАЖЧИКА\n(Offset Code)", size=11, pad=12, fill="#fff3cd", stroke="#d97706", sw=1.8, color="#92400e", bold=True)
    p.append(s2)

    # Стан 3: READ_DATA
    s3, _, _ = textbox(680, 160, "ЗБИРАННЯ\nДАНИХ БЛОКУ\n(Лічильник N > 0)", size=11, pad=12, fill="#eaf0fd", stroke=NEG, sw=1.8, color=NEG, bold=True)
    p.append(s3)

    # Переходи
    # Початок / скидання
    p.append(arrow(40, 160, 60, 160, color=LINE, sw=1.6))
    p.append(text(50, 145, "Старт", size=10, color=MUTED, bold=True))

    # s1 -> s2 (отримано 0x00)
    p.append(arrow(200, 140, 320, 140, color=FIELD, sw=1.8))
    p.append(text(260, 128, "Байт == 0x00 (Межа)", size=10, color=FIELD, bold=True))

    # s2 -> s3 (код > 0x01)
    p.append(arrow(460, 140, 600, 140, color=NEG, sw=1.8))
    p.append(text(530, 128, "Код > 0x01 (Дані є)", size=10, color=NEG, bold=True))

    # s2 -> s2 (код == 0x01: нуль даних, вставка 0x00)
    p.append(line(390, 205, 390, 245, color="#d97706", sw=1.6))
    p.append(line(390, 245, 350, 245, color="#d97706", sw=1.6))
    p.append(line(350, 245, 350, 205, color="#d97706", sw=1.6))
    p.append(arrow(350, 205, 360, 195, color="#d97706", sw=1.6))
    p.append(text(370, 260, "Код == 0x01 (Вставити 0x00)", size=9.5, color="#d97706", bold=True))

    # s3 -> s3 (читання байта даних)
    p.append(line(680, 115, 680, 80, color=NEG, sw=1.6))
    p.append(line(680, 80, 740, 80, color=NEG, sw=1.6))
    p.append(line(740, 80, 740, 115, color=NEG, sw=1.6))
    p.append(arrow(740, 115, 715, 125, color=NEG, sw=1.6))
    p.append(text(710, 68, "Байт != 0x00 (--N)", size=9.5, color=NEG, bold=True))

    # s3 -> s2 (блок завершено)
    p.append(arrow(600, 180, 460, 180, color=FIELD, sw=1.8))
    p.append(text(530, 195, "N == 0 (Вставити 0x00 якщо Code < 0xFF)", size=9.5, color=FIELD, bold=True))

    # s3 / s2 -> s1 (помилка: неочікуваний 0x00 або помилка кадру)
    p.append(line(680, 205, 680, 310, color=POS, sw=1.6))
    p.append(line(680, 310, 130, 310, color=POS, sw=1.6))
    p.append(arrow(130, 310, 130, 215, color=POS, sw=1.6))
    p.append(text(410, 325, "Неочікуваний 0x00 під час збору даних (Помилка кадрування → Скидання)", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "streaming-fsm.svg"), W, H, *p,
           title="Автомат станів потокового декодера COBS")


if __name__ == "__main__":
    fig_framing_problem()
    fig_cobs_encoding_mechanism()
    fig_cobs_vs_slip_overhead()
    fig_cobs_r_optimization()
    fig_streaming_fsm()
    print("Всі фігури згенеровано успішно.")
