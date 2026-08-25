# -*- coding: utf-8 -*-
"""Фігури до теми «Break-сигнал UART».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

HI_Y = 130
LO_Y = 200


def _draw_waveform(f, x0, cells, bw, y_hi=HI_Y, y_lo=LO_Y, baseline_lab=True):
    """Малює часову діаграму за списком cells=[(label, value, color, sub)]."""
    centers = []
    x = x0
    prev_y = y_hi
    for lab, val, col, sub in cells:
        y = y_hi if val == 1 else y_lo
        if y != prev_y:
            f.append(line(x, prev_y, x, y, color=INK, sw=2.4))
        f.append(line(x, y, x + bw, y, color=INK, sw=2.4))
        cx = x + bw / 2.0
        centers.append(cx)
        if lab:
            f.append(text(cx, y_lo + 24, lab, size=11, color=col, bold=True))
        if sub is not None:
            yy = y_hi - 12 if val == 1 else y_lo + 38
            f.append(text(cx, yy, str(sub), size=10.5, color=MUTED))
        prev_y = y
        x += bw
    if prev_y != y_hi:
        f.append(line(x, prev_y, x, y_hi, color=INK, sw=2.4))
    f.append(line(x, y_hi, x + bw, y_hi, color=INK, sw=2.4))
    if baseline_lab:
        f.append(text(x0 - 12, y_hi + 4, "1 (Mark)", size=10, color=MUTED, anchor="end"))
        f.append(text(x0 - 12, y_lo + 4, "0 (Space)", size=10, color=MUTED, anchor="end"))
    return centers, x + bw


# ── 1. Звичайний кадр 8N1 проти сигналу Break ──────────────────────────────────
def fig_break_vs_frame():
    W, H = 880, 430
    f = [text(W / 2, 28, "Порівняння валідного кадру UART та стану Break на фізичній лінії", size=15, bold=True)]

    # 1. Валідний кадр (байт 0x55 = 01010101b)
    f.append(text(50, 64, "Валідний кадр 8N1 (наприклад, 0x55): обов'язкове повернення у «1» на стоп-біті", size=11.5, bold=True, color=FIELD))
    x0, bw = 90, 48
    cells_frame = [
        ("Спокій", 1, MUTED, None),
        ("СТАРТ", 0, POS, "0"),
        ("D0", 1, INK, "1"),
        ("D1", 0, INK, "0"),
        ("D2", 1, INK, "1"),
        ("D3", 0, INK, "0"),
        ("D4", 1, INK, "1"),
        ("D5", 0, INK, "0"),
        ("D6", 1, INK, "1"),
        ("D7", 0, INK, "0"),
        ("СТОП", 1, POS, "1"),
        ("Спокій", 1, MUTED, None),
    ]
    _draw_waveform(f, x0, cells_frame, bw, y_hi=90, y_lo=140)

    # Розділювач
    f.append(line(50, 195, W - 50, 195, color=MUTED, sw=1.0, dash="4,4"))

    # 2. Сигнал Break
    f.append(text(50, 225, "Сигнал Break: утримання лінії в «0» протягом ≥ 10–12 бітових інтервалів (порушення стоп-біта)", size=11.5, bold=True, color=NEG))
    cells_b = [
        ("Спокій", 1, MUTED, None),
        ("Старт", 0, NEG, "0"),
        ("D0 (0)", 0, INK, "0"),
        ("D1 (0)", 0, INK, "0"),
        ("D2 (0)", 0, INK, "0"),
        ("D3 (0)", 0, INK, "0"),
        ("D4 (0)", 0, INK, "0"),
        ("D5 (0)", 0, INK, "0"),
        ("D6 (0)", 0, INK, "0"),
        ("D7 (0)", 0, INK, "0"),
        ("СТОП (0!)", 0, NEG, "FE!"),
        ("Break...", 0, NEG, "0"),
    ]
    _draw_waveform(f, x0, cells_b, bw, y_hi=250, y_lo=300)

    # Виноска про помилку стоп-біта
    stop_x = x0 + 10 * bw + bw / 2
    f.append(line(stop_x, 305, stop_x, 340, color=NEG, sw=1.5))
    b, _, _ = textbox(stop_x, 370, "Стоп-біт відсутній: лінія лишається низькою\n→ фіксація Framing Error (FE) + Break (BI)", size=10, fill="#fdf2f2", stroke=NEG)
    f.append(b)

    render(os.path.join(IMG, "break-vs-frame.svg"), W, H, *f)


# ── 2. Механізм апаратної детекції Framing Error та Break ─────────────────────
def fig_framing_error_detection():
    W, H = 860, 400
    f = [text(W / 2, 28, "Апаратна детекція Break: передискретизація 16×, нульовий байт та помилка стоп-біта", size=15, bold=True)]

    x0, bw = 70, 60
    # Малюємо часову шкалу для одного кадру, що переходить у Break
    f.append(line(x0, 80, x0 + bw, 80, color=INK, sw=2.4))
    f.append(line(x0 + bw, 80, x0 + bw, 150, color=INK, sw=2.4))
    f.append(line(x0 + bw, 150, x0 + 11 * bw, 150, color=NEG, sw=3.0))

    f.append(text(x0 - 8, 84, "1", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 8, 154, "0", size=11, color=MUTED, anchor="end"))

    # Позначення бітових інтервалів
    bit_names = ["Спокій", "Старт", "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "Стоп"]
    for i in range(11):
        bx = x0 + i * bw
        f.append(line(bx, 70, bx, 160, color=MUTED, sw=0.8, dash="2,2"))
        if i < len(bit_names):
            f.append(text(bx + bw / 2, 64, bit_names[i], size=10.5, color=FIELD if i == 10 else INK, bold=True))

        # Точки семплювання приймачем (8-й такт із 16×)
        if i >= 1:
            sample_x = bx + bw / 2
            f.append(circle(sample_x, 150, 3.5, fill=NEG if i == 10 else POS, stroke=INK, sw=1.0))
            f.append(line(sample_x, 155, sample_x, 175, color=MUTED, sw=1.0))
            val_text = "0" if i < 10 else "0 (FE!)"
            f.append(text(sample_x, 188, val_text, size=9.5, color=NEG if i == 10 else INK))

    # Стрілка на спадному фронті
    f.append(line(x0 + bw, 115, x0 + bw - 20, 115, color=POS, sw=1.5))
    f.append(text(x0 + bw - 25, 118, "Спадний фронт запускає 16× лічильник", size=9.5, color=POS, bold=True, anchor="end"))

    # Блоки логіки приймача внизу
    b1, _, _ = textbox(190, 280, "Зсувний регістр приймача:\nПрийнято: 0b00000000 (байт 0x00)\nУсі біти даних = 0", size=10, fill="#f4f8fb", stroke=FIELD)
    f.append(b1)

    b2, _, _ = textbox(470, 280, "Контроль стоп-біта (10-й біт):\nВиявлено: рівень «0» замість «1»\n→ Встановлюється Framing Error (FE)", size=10, fill="#fdf2f2", stroke=NEG)
    f.append(b2)

    b3, _, _ = textbox(720, 280, "Класифікація UART:\n(Дані == 0x00) && (FE == 1)\n→ Встановлюється Break Detect (BI/LBD)", size=10, fill="#edf7ed", stroke=POS)
    f.append(b3)

    # Стрілки між блоками
    f.append(line(295, 280, 355, 280, color=INK, sw=1.5))
    f.append(line(585, 280, 625, 280, color=INK, sw=1.5))

    render(os.path.join(IMG, "framing-error-detection.svg"), W, H, *f)


# ── 3. Короткий проти довгого Break ───────────────────────────────────────────
def fig_short_vs_long_break():
    W, H = 840, 380
    f = [text(W / 2, 28, "Класифікація: короткий (Short Break) та довгий (Long Break) сигнали", size=15, bold=True)]

    # Лівий стовпчик: Short Break
    f.append(rect(40, 60, 360, 290, rx=8, fill="#fbfcff", stroke=FIELD, sw=1.5))
    f.append(text(220, 88, "Короткий Break (Short Break)", size=13, bold=True, color=FIELD))
    f.append(line(60, 102, 380, 102, color=MUTED, sw=1.0))

    short_items = [
        ("Тривалість:", "10–20 бітових інтервалів (зазвичай 11–13 Tbit)"),
        ("Призначення:", "Внутрішньопротокольна синхронізація кадрів"),
        ("Швидкість:", "Формується з прив'язкою до поточної швидкості baud"),
        ("Приклади:", "• DMX512: Break ≥ 88 мкс (початок пакета світла)\n• LIN-bus: Synch Break ≥ 13 бітів (синхронізація ведених)\n• RDM: розділення запитів та відповідей"),
        ("Наслідок:", "Скидає лічильник байтів, не зупиняючи зв'язок"),
    ]
    y = 125
    for title, val in short_items:
        f.append(text(60, y, title, size=10.5, bold=True, color=INK))
        lines_v = val.split('\n')
        for lv in lines_v:
            f.append(text(80 if lv.startswith('•') else 145, y, lv, size=10, color=MUTED if not lv.startswith('•') else INK))
            y += 18
        y += 6

    # Правий стовпчик: Long Break
    f.append(rect(440, 60, 360, 290, rx=8, fill="#fbfcff", stroke=POS, sw=1.5))
    f.append(text(620, 88, "Довгий Break (Long Break)", size=13, bold=True, color=POS))
    f.append(line(460, 102, 780, 102, color=MUTED, sw=1.0))

    long_items = [
        ("Тривалість:", "200–500 мс (сотні / тисячі бітових інтервалів)"),
        ("Призначення:", "Позасмугове системне керування та апаратний скид"),
        ("Швидкість:", "Не залежить від baud rate (абсолютний час)"),
        ("Приклади:", "• Linux Magic SysRq: аварійне відновлення ядра\n• ROM Bootloader: перехід MCU в режим ISP-прошивки\n• Модемне скидання: розрив зв'язку AT-модема"),
        ("Наслідок:", "Примусове переривання роботи процесора / ОС"),
    ]
    y = 125
    for title, val in long_items:
        f.append(text(460, y, title, size=10.5, bold=True, color=INK))
        lines_v = val.split('\n')
        for lv in lines_v:
            f.append(text(480 if lv.startswith('•') else 545, y, lv, size=10, color=MUTED if not lv.startswith('•') else INK))
            y += 18
        y += 6

    render(os.path.join(IMG, "short-vs-long-break.svg"), W, H, *f)


# ── 4. Break у промислових протоколах: DMX512 та LIN ──────────────────────────
def fig_dmx_lin_break():
    W, H = 880, 440
    f = [text(W / 2, 28, "Застосування Break у промислових протоколах: DMX512 та LIN-Bus", size=15, bold=True)]

    # 1. DMX512
    f.append(text(40, 62, "1. Протокол DMX512 (250 кбод, Tbit = 4.0 мкс): структура пакета керування світлом", size=12, bold=True, color=FIELD))

    dmx_y = 110
    f.append(rect(60, dmx_y - 25, 160, 45, rx=4, fill="#fde8e8", stroke=NEG, sw=1.5))
    f.append(text(140, dmx_y - 3, "Break (≥ 88 мкс)", size=11, bold=True, color=NEG))
    f.append(text(140, dmx_y + 12, "Лінія «0» (≥ 22 біти)", size=9.5, color=MUTED))

    f.append(rect(225, dmx_y - 25, 110, 45, rx=4, fill="#edf7ed", stroke=POS, sw=1.5))
    f.append(text(280, dmx_y - 3, "MAB (≥ 8 мкс)", size=11, bold=True, color=POS))
    f.append(text(280, dmx_y + 12, "Mark («1», ≥ 2 біти)", size=9.5, color=MUTED))

    f.append(rect(340, dmx_y - 25, 140, 45, rx=4, fill="#eef4fb", stroke=FIELD, sw=1.5))
    f.append(text(410, dmx_y - 3, "Start Code (0x00)", size=11, bold=True, color=FIELD))
    f.append(text(410, dmx_y + 12, "Кадр 8N2 (44 мкс)", size=9.5, color=MUTED))

    f.append(rect(485, dmx_y - 25, 160, 45, rx=4, fill="#fbfcff", stroke=INK, sw=1.2))
    f.append(text(565, dmx_y - 3, "Слот 1 (Яскравість)", size=10.5, bold=True, color=INK))
    f.append(text(565, dmx_y + 12, "Кадр 8N2 (0–255)", size=9.5, color=MUTED))

    f.append(text(665, dmx_y + 3, "...", size=16, bold=True, color=MUTED))

    f.append(rect(700, dmx_y - 25, 140, 45, rx=4, fill="#fbfcff", stroke=INK, sw=1.2))
    f.append(text(770, dmx_y - 3, "Слот 512", size=10.5, bold=True, color=INK))
    f.append(text(770, dmx_y + 12, "Останній канал", size=9.5, color=MUTED))

    f.append(line(40, 180, W - 40, 180, color=MUTED, sw=1.0, dash="4,4"))

    # 2. LIN Bus
    f.append(text(40, 215, "2. Автомобільна шина LIN (до 20 кбіт/с): заголовок кадру майстра (Header)", size=12, bold=True, color=POS))

    lin_y = 265
    f.append(rect(60, lin_y - 25, 180, 45, rx=4, fill="#fde8e8", stroke=NEG, sw=1.5))
    f.append(text(150, lin_y - 3, "Synch Break (≥ 13 бітів)", size=11, bold=True, color=NEG))
    f.append(text(150, lin_y + 12, "Домінантний рівень «0»", size=9.5, color=MUTED))

    f.append(rect(245, lin_y - 25, 120, 45, rx=4, fill="#edf7ed", stroke=POS, sw=1.5))
    f.append(text(305, lin_y - 3, "Delimiter (≥ 1 біт)", size=11, bold=True, color=POS))
    f.append(text(305, lin_y + 12, "Рецесивний «1»", size=9.5, color=MUTED))

    f.append(rect(370, lin_y - 25, 160, 45, rx=4, fill="#eef4fb", stroke=FIELD, sw=1.5))
    f.append(text(450, lin_y - 3, "Sync Field (0x55)", size=11, bold=True, color=FIELD))
    f.append(text(450, lin_y + 12, "Калібрування RC-такту", size=9.5, color=MUTED))

    f.append(rect(535, lin_y - 25, 140, 45, rx=4, fill="#fef6e7", stroke=POS, sw=1.5))
    f.append(text(605, lin_y - 3, "PID (Ідентифікатор)", size=11, bold=True, color=POS))
    f.append(text(605, lin_y + 12, "6 біт ID + 2 біти парності", size=9.5, color=MUTED))

    f.append(rect(680, lin_y - 25, 160, 45, rx=4, fill="#fbfcff", stroke=MUTED, sw=1.2))
    f.append(text(760, lin_y - 3, "Поле відповіді (Data)", size=10.5, color=MUTED))
    f.append(text(760, lin_y + 12, "1–8 байт від Slave", size=9.5, color=MUTED))

    b, _, _ = textbox(W / 2, 375, "В обох протоколах Break є єдиним маркером синхронізації: він гарантує, що всі ведені вузли\nскидають свої приймальні парсери в нульовий стан одночасно без додаткових сигнальних ліній.", size=10.5, fill="#f4f8fb", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "dmx-lin-break.svg"), W, H, *f)


# ── 5. Обробка Break у підсистемі TTY та ядрі Linux ────────────────────────────
def fig_termios_break_flow():
    W, H = 880, 410
    f = [text(W / 2, 28, "Маршрут обробки Break-сигналу в термінальному драйвері (termios / TTY)", size=15, bold=True)]

    # 1. Апаратне переривання
    b1, _, _ = textbox(130, 90, "Апаратний UART\nФіксація FE + 0x00\nIRQ: BI (Break Interrupt)", size=10.5, fill="#fde8e8", stroke=NEG)
    f.append(b1)

    # 2. Magic SysRq перевірка
    b2, _, _ = textbox(360, 90, "Драйвер ядра / serial_core\nПеревірка Magic SysRq\n(CONFIG_MAGIC_SYSRQ)", size=10.5, fill="#fef6e7", stroke=POS)
    f.append(b2)

    # Стрілка від UART до ядра
    f.append(line(210, 90, 275, 90, color=INK, sw=1.6))

    # Гілка SysRq
    f.append(line(360, 125, 360, 175, color=POS, sw=1.6))
    b_sysrq, _, _ = textbox(360, 210, "SysRq режим активовано!\nНаступний символ (b, s, u, t)\nвиконує аварійну дію ядра", size=10, fill="#fef0f0", stroke=NEG)
    f.append(b_sysrq)

    # Лінія далі до termios c_iflag
    f.append(line(445, 90, 520, 90, color=INK, sw=1.6))
    b3, _, _ = textbox(660, 90, "Підсистема termios (c_iflag)\nФільтрація та обробка Break", size=11, bold=True, fill="#eef4fb", stroke=FIELD)
    f.append(b3)

    # Три виходи з termios
    # 1. IGNBRK
    f.append(line(570, 120, 520, 290, color=INK, sw=1.4))
    b_ign, _, _ = textbox(510, 335, "IGNBRK = 1\nСигнал Break\nповністю ігнорується\n(викидається)", size=9.5, fill="#fbfcff", stroke=MUTED)
    f.append(b_ign)

    # 2. BRKINT
    f.append(line(660, 120, 660, 290, color=INK, sw=1.4))
    b_int, _, _ = textbox(660, 335, "BRKINT = 1\nСкидання черг TTY\n+ генерація сигналу\nSIGINT процесу", size=9.5, fill="#edf7ed", stroke=POS)
    f.append(b_int)

    # 3. PARMRK
    f.append(line(750, 120, 800, 290, color=INK, sw=1.4))
    b_mrk, _, _ = textbox(800, 335, "PARMRK = 1\nЕкранування у потік:\nвставляється 3 байти\n\\377 \\0 \\0", size=9.5, fill="#fbfcff", stroke=FIELD)
    f.append(b_mrk)

    render(os.path.join(IMG, "termios-break-flow.svg"), W, H, *f)


if __name__ == '__main__':
    fig_break_vs_frame()
    fig_framing_error_detection()
    fig_short_vs_long_break()
    fig_dmx_lin_break()
    fig_termios_break_flow()
    print("Усі фігури успішно згенеровано у ./img/")
