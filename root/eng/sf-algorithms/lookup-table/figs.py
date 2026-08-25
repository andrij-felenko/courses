# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def cell(x, y, w, h, s, size=13, fill=FILL, stroke=LINE, color=INK, bold=False):
    """Клітинка з текстом усередині."""
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.4, rx=4)
    out += text(x + w / 2.0, y + h / 2.0 + size * 0.35, s, size=size, color=color, bold=bold)
    return out


def fig_tradeoff_spectrum():
    """Спектр компромісу між обчисленням і пам'яттю."""
    W, H = 860, 360
    els = []

    # Заголовок
    els.append(text(W / 2.0, 32, "Спектр інженерного компромісу: обчислення проти пам'яті", size=16, bold=True))

    # Горизонтальна шкала
    els.append(line(70, 85, 790, 85, color=LINE, sw=3))
    els.append(text(70, 70, "Чисте обчислення (ALU)", size=12, color=POS, anchor="start", bold=True))
    els.append(text(790, 70, "Чиста пам'ять (LUT)", size=12, color=NEG, anchor="end", bold=True))

    # 4 стовпчики стратегій
    cols = [
        {
            "x": 60, "w": 170,
            "title": "Аналітичний розрахунок",
            "desc": ["Ряди Тейлора, CORDIC,", "ітераційні цикли"],
            "alu": "Високе навантаження АЛП",
            "mem": "0 байтів пам'яті",
            "time": "40–150 тактів CPU",
            "color": POS, "bg": "#fdf2f0"
        },
        {
            "x": 250, "w": 170,
            "title": "Гібрид: LUT + інтерполяція",
            "desc": ["Таблиця вузлових точок +", "лінійна інтерполяція"],
            "alu": "Помірне (1–2 множення)",
            "mem": "Компактна (128 Б – 4 КБ)",
            "time": "6–15 тактів CPU",
            "color": "#d35400", "bg": "#fef9e7"
        },
        {
            "x": 440, "w": 170,
            "title": "Пряма точна таблиця",
            "desc": ["Попередній розрахунок", "усіх дискретних значень"],
            "alu": "0 операцій АЛП",
            "mem": "Помірна (256 Б – 64 КБ)",
            "time": "1 читання (4–5 тактів L1)",
            "color": FIELD, "bg": "#eafaf1"
        },
        {
            "x": 630, "w": 170,
            "title": "Повна багатовимірна LUT",
            "desc": ["3D LUT, гігантські масиви,", "апаратні ROM / FPGA"],
            "alu": "0 операцій АЛП",
            "mem": "Велика (мегабайти / ГБ)",
            "time": "Ризик DRAM (150+ тактів)",
            "color": NEG, "bg": "#ebf5fb"
        }
    ]

    for c in cols:
        x, y, w = c["x"], 105, c["w"]
        els.append(rect(x, y, w, 185, fill=c["bg"], stroke=c["color"], sw=1.8, rx=6))
        els.append(text(x + w / 2.0, y + 22, c["title"], size=12, color=c["color"], bold=True))
        els.append(line(x + 10, y + 34, x + w - 10, y + 34, color=c["color"], sw=1, dash="3 3"))

        els.append(mtext(x + w / 2.0, y + 54, c["desc"], size=11, color=INK, lh=1.3))

        els.append(rect(x + 8, y + 94, w - 16, 22, fill="#ffffff", stroke="#d5dbdb", sw=1, rx=3))
        els.append(text(x + w / 2.0, y + 109, c["alu"], size=10, color=MUTED))

        els.append(rect(x + 8, y + 122, w - 16, 22, fill="#ffffff", stroke="#d5dbdb", sw=1, rx=3))
        els.append(text(x + w / 2.0, y + 137, c["mem"], size=10, color=MUTED))

        els.append(rect(x + 8, y + 150, w - 16, 22, fill="#ffffff", stroke="#d5dbdb", sw=1, rx=3))
        els.append(text(x + w / 2.0, y + 165, c["time"], size=10, color=c["color"], bold=True))

    els.append(mtext(W / 2.0, 320, [
        "Просторово-часовий компроміс: зменшення обчислень вимагає пам'яті.",
        "Ефективність залежить від того, чи залишається таблиця в швидкому кеші L1 процесора."
    ], size=12, color=INK, lh=1.4))

    return render(os.path.join(OUT, 'tradeoff-spectrum.svg'), W, H, *els,
                  title="Спектр компромісу між обчисленням і пам'яттю")


def fig_lut_addressing_mechanics():
    """Механіка перетворення вхідного значення на фізичну адресу пам'яті."""
    W, H = 880, 350
    els = []

    els.append(text(W / 2.0, 30, "Механіка прямої адресації в таблиці замін (LUT)", size=16, bold=True))

    # Крок 1: Вхідне значення
    els.append(rect(40, 75, 140, 85, fill="#fef9e7", stroke="#d35400", sw=1.8, rx=6))
    els.append(text(110, 100, "Вхідний аргумент", size=12, color="#d35400", bold=True))
    els.append(text(110, 125, "x = 0x3A (58)", size=14, color=INK, bold=True))
    els.append(text(110, 145, "значення з сенсора/коду", size=10, color=MUTED))

    # Стрілка 1 -> 2
    els.append(arrow(180, 117, 220, 117, color=LINE, sw=1.6))
    els.append(text(200, 108, "маска", size=10, color=MUTED))

    # Крок 2: Обчислення індексу
    els.append(rect(225, 75, 170, 85, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=6))
    els.append(text(310, 98, "Індексація масиву", size=12, color=FIELD, bold=True))
    els.append(text(310, 122, "idx = x & 0xFF", size=13, color=INK, bold=True))
    els.append(text(310, 144, "індекс = 58 (в межах [0..255])", size=10, color=MUTED))

    # Стрілка 2 -> 3
    els.append(arrow(395, 117, 435, 117, color=LINE, sw=1.6))
    els.append(text(415, 108, "зміщення", size=10, color=MUTED))

    # Крок 3: Формування адреси
    els.append(rect(440, 75, 200, 85, fill="#ebf5fb", stroke=NEG, sw=1.8, rx=6))
    els.append(text(540, 98, "Обчислення адреси", size=12, color=NEG, bold=True))
    els.append(text(540, 122, "Addr = Base + idx × 4", size=13, color=INK, bold=True))
    els.append(text(540, 144, "0x2000_1000 + 58 × 4", size=10, color=MUTED))

    # Стрілка 3 -> 4
    els.append(arrow(640, 117, 675, 117, color=LINE, sw=1.6))

    # Крок 4: Читання з кешу/пам'яті
    els.append(rect(680, 75, 160, 85, fill="#fdf2f0", stroke=POS, sw=1.8, rx=6))
    els.append(text(760, 98, "Результат LUT", size=12, color=POS, bold=True))
    els.append(text(760, 122, "LUT[58] = 0x00A4", size=13, color=POS, bold=True))
    els.append(text(760, 144, "готове значення f(x)", size=10, color=MUTED))

    # Нижня частина: Пам'ять таблиці
    els.append(rect(140, 190, 600, 95, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    els.append(text(440, 212, "Структура таблиці LUT у пам'яті (256 елементів по 4 байти = 1 КБ)", size=12, bold=True))

    # Комірки пам'яті
    slots = [
        {"idx": "0", "val": "f(0)", "hot": False},
        {"idx": "1", "val": "f(1)", "hot": False},
        {"idx": "...", "val": "...", "hot": False},
        {"idx": "58", "val": "f(58)", "hot": True},
        {"idx": "...", "val": "...", "hot": False},
        {"idx": "255", "val": "f(255)", "hot": False}
    ]

    for i, s in enumerate(slots):
        x = 170 + i * 90
        fill_c = "#fdecea" if s["hot"] else "#ffffff"
        strk_c = POS if s["hot"] else LINE
        txt_c = POS if s["hot"] else INK
        els.append(cell(x, 226, 80, 42, s["val"], size=12, fill=fill_c, stroke=strk_c, color=txt_c, bold=s["hot"]))
        els.append(text(x + 40, 280, f"idx: {s['idx']}", size=10, color=MUTED))

    # Стрілка вибірки
    els.append(arrow(540, 160, 480, 226, color=POS, sw=1.8))

    els.append(mtext(W / 2.0, 320, [
        "Трансляція індексу в адресу виконується апаратно за один такт командою непрямої адресації з масштабуванням.",
        "Складність будь-якої функції O(1) перетворюється на звичайне читання з оперативної пам'яті чи кеша."
    ], size=12, color=INK, lh=1.4))

    return render(os.path.join(OUT, 'lut-addressing-mechanics.svg'), W, H, *els,
                  title="Механіка прямої адресації в таблиці замін")


def fig_linear_interpolation_error():
    """Геометрія лінійної інтерполяції та похибка апроксимації."""
    W, H = 840, 360
    els = []

    els.append(text(W / 2.0, 30, "Похибка табличної апроксимації та лінійна інтерполяція", size=16, bold=True))

    # Осі координат
    els.append(arrow(80, 270, 760, 270, color=LINE, sw=1.5))
    els.append(text(750, 290, "x (аргумент)", size=12, color=INK, bold=True))

    els.append(arrow(100, 280, 100, 60, color=LINE, sw=1.5))
    els.append(text(80, 75, "f(x)", size=12, color=INK, bold=True))

    # Вузли сітки
    x1, y1 = 200, 230  # (x_i, y_i)
    x2, y2 = 560, 100  # (x_{i+1}, y_{i+1})
    xm = 380           # точка x між ними

    # Справжня крива f(x) (випукла дуга вгору)
    els.append('<path d="M 140,260 Q 380,80 620,95" fill="none" stroke="%s" stroke-width="2.5"/>' % FIELD)
    els.append(text(460, 110, "Справжня функція f(x)", size=12, color=FIELD, bold=True))

    # Січна (хорда) — лінійна інтерполяція
    els.append(line(x1, y1, x2, y2, color=NEG, sw=2, dash="5 3"))
    els.append(text(460, 185, "Лінійна інтерполяція L(x)", size=12, color=NEG, bold=True))

    # Сходинка (ступінчаста апроксимація)
    els.append(line(x1, y1, x2, y1, color=MUTED, sw=1.5, dash="3 3"))
    els.append(text(300, 245, "Ступінчаста апроксимація y = yᵢ", size=10, color=MUTED))

    # Вузлові точки
    els.append(circle(x1, y1, 5, fill=POS, stroke="#ffffff", sw=2))
    els.append(circle(x2, y2, 5, fill=POS, stroke="#ffffff", sw=2))

    # Позначення вузлів
    els.append(text(x1, 288, "xᵢ", size=13, bold=True))
    els.append(text(x2, 288, "xᵢ₊₁", size=13, bold=True))
    els.append(line(x1, y1, x1, 270, color=MUTED, sw=1, dash="2 2"))
    els.append(line(x2, y2, x2, 270, color=MUTED, sw=1, dash="2 2"))

    # Крок h
    els.append(line(x1, 305, x2, 305, color=LINE, sw=1.2))
    els.append(text((x1 + x2) / 2.0, 322, "Крок сітки h = xᵢ₊₁ − xᵢ", size=11, color=INK, bold=True))
    els.append(line(x1, 300, x1, 310, color=LINE, sw=1.2))
    els.append(line(x2, 300, x2, 310, color=LINE, sw=1.2))

    # Точка x всередині відрізка
    ym_curve = 135
    ym_chord = 165
    els.append(line(xm, 270, xm, ym_curve, color=POS, sw=1.2, dash="3 3"))
    els.append(text(xm, 288, "x", size=12, color=POS, bold=True))

    # Стрілка похибки інтерполяції
    els.append(line(xm, ym_curve, xm, ym_chord, color=POS, sw=2.5))
    els.append(circle(xm, ym_curve, 3.5, fill=FIELD, stroke=LINE, sw=1))
    els.append(circle(xm, ym_chord, 3.5, fill=NEG, stroke=LINE, sw=1))

    # Виноска похибки
    els.append(rect(590, 160, 210, 75, fill="#fdf2f0", stroke=POS, sw=1.5, rx=5))
    els.append(text(695, 182, "Похибка інтерполяції E(x)", size=12, color=POS, bold=True))
    els.append(text(695, 202, "E(x) = |f(x) − L(x)|", size=11, color=INK))
    els.append(text(695, 222, "E(x) ≤ (M₂ / 8) · h²", size=12, color=POS, bold=True))

    return render(os.path.join(OUT, 'linear-interpolation-error.svg'), W, H, *els,
                  title="Геометрія лінійної інтерполяції та похибка апроксимації")


def fig_cache_latency_cliff():
    """Ієрархія затримок пам'яті та прірва кеш-промаху."""
    W, H = 860, 360
    els = []

    els.append(text(W / 2.0, 30, "Прірва затримок пам'яті: коли таблиця замін стає повільною", size=16, bold=True))

    levels = [
        {"name": "Регістри АЛП / Векторний зсув", "time": "1 такт (0.25 нс)", "w": 30, "color": FIELD, "note": "Чисте обчислення або SIMD LUT"},
        {"name": "Кеш першого рівня (L1D Cache)", "time": "4–5 тактів (1.2 нс)", "w": 70, "color": "#27ae60", "note": "Мала LUT (≤ 32 КБ), гарячий цикл"},
        {"name": "Кеш другого рівня (L2 Cache)", "time": "12–14 тактів (3.5 нс)", "w": 140, "color": "#f39c12", "note": "Середня LUT (до 512 КБ)"},
        {"name": "Кеш третього рівня (L3 Cache)", "time": "40–60 тактів (15 нс)", "w": 260, "color": "#e67e22", "note": "Велика LUT (до кількох МБ)"},
        {"name": "Оперативна пам'ять (DRAM)", "time": "150–250+ тактів (60 нс)", "w": 480, "color": POS, "note": "Холодний промах / гігантська таблиця"}
    ]

    y0 = 70
    dy = 50

    for i, lv in enumerate(levels):
        y = y0 + i * dy
        # Назва
        els.append(text(250, y + 16, lv["name"], size=12, color=INK, anchor="end", bold=(i == 0 or i == 4)))

        # Смуга затримки
        els.append(rect(265, y, lv["w"], 24, fill=lv["color"], stroke="#ffffff", sw=1, rx=4))

        # Число тактів
        els.append(text(275 + lv["w"], y + 17, lv["time"], size=11, color=lv["color"], anchor="start", bold=True))

        # Примітка праворуч
        els.append(text(560, y + 17, f"({lv['note']})", size=10, color=MUTED, anchor="start"))

    # Пунктирна лінія порогу вигідності
    els.append(line(265 + 85, 55, 265 + 85, 305, color=POS, sw=1.5, dash="4 4"))
    els.append(text(265 + 92, 320, "Межа доцільності LUT над обчисленням АЛП", size=11, color=POS, bold=True))

    return render(os.path.join(OUT, 'cache-latency-cliff.svg'), W, H, *els,
                  title="Прірва затримок пам'яті")


def fig_simd_in_register_lut():
    """Векторна таблиця замін усередині 128-бітного SIMD-регістра."""
    W, H = 860, 360
    els = []

    els.append(text(W / 2.0, 30, "Векторна таблиця замін усередині регістра (SIMD In-Register LUT)", size=16, bold=True))

    # Регістр-таблиця (16 байтів)
    els.append(text(120, 75, "Таблиця LUT у регістрі (XMM0)", size=12, color=NEG, bold=True))
    els.append(rect(120, 90, 620, 40, fill="#ebf5fb", stroke=NEG, sw=1.6, rx=4))

    for i in range(16):
        x = 120 + i * 38.75
        els.append(line(x, 90, x, 130, color="#aed6f1", sw=1))
        els.append(text(x + 19, 114, f"v{i}", size=11, color=NEG, bold=True))
        els.append(text(x + 19, 82, str(i), size=9, color=MUTED))

    # Вхідний вектор індексів (16 байтів)
    els.append(text(120, 160, "Вхідний вектор 4-бітних індексів (XMM1)", size=12, color=FIELD, bold=True))
    els.append(rect(120, 175, 620, 40, fill="#eafaf1", stroke=FIELD, sw=1.6, rx=4))

    sample_indices = [3, 0, 15, 7, 2, 8, 1, 14, 4, 11, 6, 9, 13, 5, 12, 10]
    for i, idx in enumerate(sample_indices):
        x = 120 + i * 38.75
        els.append(line(x, 175, x, 215, color="#a9dfbf", sw=1))
        els.append(text(x + 19, 199, str(idx), size=11, color=FIELD, bold=True))

    # Стрілка операції тасування
    els.append(arrow(430, 220, 430, 255, color=POS, sw=2))
    els.append(text(445, 240, "_mm_shuffle_epi8 (pshufb) / vqtbl1q_u8 — 1 такт!", size=11, color=POS, bold=True, anchor="start"))

    # Вихідний вектор результатів
    els.append(text(120, 265, "Вихідний вектор замінених байтів (XMM2)", size=12, color=POS, bold=True))
    els.append(rect(120, 280, 620, 40, fill="#fdf2f0", stroke=POS, sw=1.6, rx=4))

    for i, idx in enumerate(sample_indices):
        x = 120 + i * 38.75
        els.append(line(x, 280, x, 320, color="#f5b7b1", sw=1))
        els.append(text(x + 19, 304, f"v{idx}", size=11, color=POS, bold=True))

    return render(os.path.join(OUT, 'simd-in-register-lut.svg'), W, H, *els,
                  title="Векторна таблиця замін усередині SIMD-регістра")


if __name__ == '__main__':
    fig_tradeoff_spectrum()
    fig_lut_addressing_mechanics()
    fig_linear_interpolation_error()
    fig_cache_latency_cliff()
    fig_simd_in_register_lut()
    print("Всі фігури згенеровано успішно.")
