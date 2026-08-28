# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. errata-classification-matrix: Матриця та дерево класифікації помилок ──
def fig_errata_classification_matrix():
    W, H = 960, 480
    p = []

    # Вхідний вузол
    b_root, _, _ = textbox(160, 240, "Виявлено дефект\nна платі Rev 1.0\n(Аномалія в роботі)",
                           size=13, fill="#f8fafc", stroke=INK, sw=2, bold=True)
    p.append(b_root)

    # Аналіз першопричини (Root Cause Analysis)
    p.append(arrow(245, 240, 315, 240, color=LINE, sw=2))
    b_diag, _, _ = textbox(410, 240, "Діагностика першопричини (RCA):\n• Помилка схеми (Schematic bug)\n• Помилка футпрінта (Footprint bug)\n• Завади та цілісність сигналу\n• Порушення послідовності живлення",
                           size=11.5, fill="#ffffff", stroke=MUTED, sw=1.5)
    p.append(b_diag)

    # Розгалуження вгору: Блокуючі дефекти
    p.append(arrow(515, 210, 580, 120, color=POS, sw=2))
    p.append(text(520, 150, "Блокуючий дефект", size=11.5, color=POS, bold=True, anchor="end"))

    b_block, _, _ = textbox(760, 120, "Категорія 1: Блокуючі дефекти (Hardware Rework)\n• Фізичне коротке замикання або переполюсовка\n• Дзеркальний чип / непідключені життєві шини\nРішення: Різання доріжок (Cut) + дротяні перемички (Bodge)\nОбов'язково: Технологічна інструкція монтажнику (SOP)",
                            size=11.5, fill="#fdf2f2", stroke=POS, sw=2)
    p.append(b_block)

    # Розгалуження вниз: Некритичні дефекти
    p.append(arrow(515, 270, 580, 360, color=FIELD, sw=2))
    p.append(text(520, 330, "Некритичний дефект", size=11.5, color=FIELD, bold=True, anchor="end"))

    b_nonblock, _, _ = textbox(760, 360, "Категорія 2: Некритичні дефекти (Software Workaround)\n• Зависання датчика через збій FSM шини\n• Брязкіт контактів / відсутність RC-фільтра\n• Завалені фронти шини через велику ємність\nРішення: Програмне скидання GPIO, таймерний фільтр, downclock",
                               size=11.5, fill="#eefaf1", stroke=FIELD, sw=2)
    p.append(b_nonblock)

    render(os.path.join(OUT, "errata-classification-matrix.svg"), W, H, *p,
           title="Матриця класифікації апаратних дефектів та вибору стратегії виправлення")


# ── 2. errata-record-structure: Анатомія інженерного запису Errata ────────────
def fig_errata_record_structure():
    W, H = 960, 460
    p = []

    # 5 ключових полів картки дефекту
    cols = [
        ("1. Ідентифікатор (ID)", "ERR-HW-003\nПлати: Rev 1.0\nКритичність: High", "#eaf0fd", NEG),
        ("2. Симптом (Symptom)", "Шина I2C блокується;\nлінія SDA притиснута\nдо 0 В намертво", "#fdf2f2", POS),
        ("3. Першопричина (RCA)", "Збій FSM датчика при\nпросіданні напруги;\nback-power через діод", "#fffbeb", "#d97706"),
        ("4. Обхід (Workaround)", "Ізоляція шини (High-Z)\nта вимикання GPIO VDD\nна 25 мс у прошивці", "#eefaf1", FIELD),
        ("5. Фіксація в Rev B", "Додати виділений LDO\nз лінією EN та апаратні\nпідтяжки 4.7 кОм", "#f8fafc", INK),
    ]

    box_w = 168
    box_h = 240
    start_x = 40
    y_pos = 90

    for i, (head, body_text, fill_c, stroke_c) in enumerate(cols):
        cur_x = start_x + i * 184
        p.append(rect(cur_x, y_pos, box_w, box_h, fill=fill_c, stroke=stroke_c, sw=1.8, rx=6))
        p.append(text(cur_x + box_w / 2, y_pos + 26, head, size=11.5, color=stroke_c, bold=True))
        p.append(line(cur_x + 10, y_pos + 38, cur_x + box_w - 10, y_pos + 38, color=stroke_c, sw=1, dash="3 3"))
        
        lines = body_text.split("\n")
        for j, ln in enumerate(lines):
            p.append(text(cur_x + box_w / 2, y_pos + 70 + j * 24, ln, size=11, color=INK))

        if i < len(cols) - 1:
            p.append(arrow(cur_x + box_w + 3, y_pos + box_h / 2, cur_x + box_w + 14, y_pos + box_h / 2, color=MUTED, sw=2))

    # Нижній висновок
    b_bot, _, _ = textbox(W / 2, 395,
                          "Кожен запис зв'язує фізичний симптом із першопричиною, дає негайний обхід для живої плати\nта формує однозначне технічне завдання для трасування наступної ревізії.",
                          size=12, stroke=NEG, fill="#f0f7ff")
    p.append(b_bot)

    render(os.path.join(OUT, "errata-record-structure.svg"), W, H, *p,
           title="Структура інженерного запису Hardware Errata Sheet")


# ── 3. parasitic-power-leakage: Механізм паразитного живлення (Back-powering) ─
def fig_parasitic_power_leakage():
    W, H = 960, 480
    p = []

    # Ліва панель: Небезпечне скидання (Ghost powering)
    p.append(rect(30, 50, 430, 360, fill="#fdf2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(245, 80, "Помилка: Скидання лише піна живлення VDD", size=13, color=POS, bold=True))

    # МК ліворуч
    p.append(rect(50, 110, 110, 200, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(105, 135, "МК", size=13, color=INK, bold=True))
    p.append(text(105, 165, "VDD_PIN=0V", size=10.5, color=POS, bold=True))
    p.append(text(105, 215, "SDA = 3.3V", size=10.5, color=NEG, bold=True))
    p.append(text(105, 275, "SCL = 3.3V", size=10.5, color=NEG, bold=True))

    # Датчик праворуч
    p.append(rect(320, 110, 120, 200, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(380, 135, "Датчик", size=13, color=INK, bold=True))
    p.append(text(380, 165, "V_int ≈ 2.6V!", size=11, color=POS, bold=True))
    p.append(text(380, 215, "ESD Diode", size=10, color=MUTED))
    p.append(text(380, 275, "FSM завис", size=10.5, color=POS))

    # Лінія живлення VDD
    p.append(line(160, 165, 320, 165, color=POS, sw=2))
    p.append(text(240, 155, "Живлення знято (0 В)", size=10, color=POS))

    # Лінія сигнальна SDA зі струмом витоку
    p.append(line(160, 215, 320, 215, color=NEG, sw=2))
    p.append(arrow(210, 215, 270, 215, color=POS, sw=2.2))
    p.append(line(320, 215, 350, 180, color=POS, sw=2))
    p.append(arrow(350, 180, 365, 172, color=POS, sw=2))
    p.append(text(240, 235, "Струм паразитної підживки", size=10.5, color=POS, bold=True))

    b1, _, _ = textbox(245, 360, "Струм через захисний діод живить внутрішню схему.\nНапруга не падає до 0 В — чип не скидається!",
                       size=11, fill="#ffffff", stroke=POS)
    p.append(b1)

    # Права панель: Правильне скидання (High-Z Isolation)
    p.append(rect(500, 50, 430, 360, fill="#eefaf1", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(715, 80, "Правильно: Ізоляція шини в High-Z + скидання", size=13, color=FIELD, bold=True))

    # МК ліворуч
    p.append(rect(520, 110, 110, 200, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(575, 135, "МК", size=13, color=INK, bold=True))
    p.append(text(575, 165, "VDD_PIN=0V", size=10.5, color=FIELD, bold=True))
    p.append(text(575, 215, "SDA: High-Z", size=10.5, color=FIELD, bold=True))
    p.append(text(575, 275, "SCL: High-Z", size=10.5, color=FIELD, bold=True))

    # Датчик праворуч
    p.append(rect(790, 110, 120, 200, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(850, 135, "Датчик", size=13, color=INK, bold=True))
    p.append(text(850, 165, "V_int = 0.0V", size=11, color=FIELD, bold=True))
    p.append(text(850, 215, "Струм = 0 мкА", size=10, color=MUTED))
    p.append(text(850, 275, "Повний POR", size=10.5, color=FIELD, bold=True))

    # Лінії
    p.append(line(630, 165, 790, 165, color=FIELD, sw=2))
    p.append(text(710, 155, "VDD = 0 В", size=10, color=FIELD))

    p.append(line(630, 215, 790, 215, color=MUTED, sw=1.5, dash="4 3"))
    p.append(text(710, 205, "Шина знеструмлена (High-Z)", size=10, color=MUTED))
    p.append(line(630, 275, 790, 275, color=MUTED, sw=1.5, dash="4 3"))

    b2, _, _ = textbox(715, 360, "Шляхи витоку відсутні, конденсатори розряджаються.\nПісля подачі живлення відбувається апаратний POR.",
                       size=11, fill="#ffffff", stroke=FIELD)
    p.append(b2)

    # Нижній висновок
    b_bot, _, _ = textbox(W / 2, 445,
                          "Перед знеструмленням VDD усі сигнальні лінії обов'язково переводяться в режим High-Z (вхід без підтяжки).\nІнакше внутрішня логіка датчика живиться «з чорного ходу» через власні захисні ESD-діоди.",
                          size=11.5, stroke=FIELD, fill="#f8fafc")
    p.append(b_bot)

    render(os.path.join(OUT, "parasitic-power-leakage.svg"), W, H, *p,
           title="Механізм паразитного живлення через захисні ESD-діоди та процедура ізоляції шини")


# ── 4. hardware-patch-bodge: Анатомія апаратного патчу плати ──────────────────
def fig_hardware_patch_bodge():
    W, H = 960, 440
    p = []

    # 1. Розріз доріжки (Cut trace)
    p.append(rect(40, 60, 410, 310, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(245, 90, "Крок 1: Прецизійний розріз доріжки (Trace Cut)", size=13, color=INK, bold=True))

    # Доріжка ліворуч від розрізу
    p.append(rect(80, 160, 140, 30, fill="#38a169", stroke="#276749", sw=1.5, rx=3))
    p.append(text(150, 180, "Траса (Вхід)", size=11, color="#ffffff", bold=True))

    # Доріжка праворуч від розрізу
    p.append(rect(270, 160, 140, 30, fill="#38a169", stroke="#276749", sw=1.5, rx=3))
    p.append(text(340, 180, "Траса (Вихід)", size=11, color="#ffffff", bold=True))

    # Зона розрізу
    p.append(line(245, 145, 245, 205, color=POS, sw=3))
    p.append(text(245, 135, "Розріз > 0.5 мм", size=10.5, color=POS, bold=True))

    b_c1, _, _ = textbox(245, 270, "• Зняти захисну маску лезом скальпеля\n• Вирізати ділянку міді шириною ≥ 0.5 мм\n• Перевірити опір мультиметром (R > 10 МОм)",
                         size=11.5, fill="#ffffff", stroke=MUTED)
    p.append(b_c1)

    # 2. Дротяна перемичка (Bodge wire)
    p.append(rect(510, 60, 410, 310, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(715, 90, "Крок 2: Монтаж та фіксація перемички (Bodge Wire)", size=13, color=INK, bold=True))

    # Контактні точки
    p.append(circle(570, 175, 14, fill="#cbd5e1", stroke=INK, sw=1.5))
    p.append(text(570, 179, "TP1", size=10, color=INK, bold=True))

    p.append(circle(860, 175, 14, fill="#cbd5e1", stroke=INK, sw=1.5))
    p.append(text(860, 179, "IC2.4", size=10, color=INK, bold=True))

    # Дріт
    p.append(line(570, 175, 680, 150, color=FIELD, sw=3))
    p.append(line(680, 150, 760, 200, color=FIELD, sw=3))
    p.append(line(760, 200, 860, 175, color=FIELD, sw=3))
    p.append(text(715, 140, "Емальований дріт 30 AWG (Kynar)", size=10.5, color=FIELD, bold=True))

    # Краплі маски
    p.append(circle(680, 150, 9, fill="#10b981", stroke="#047857", sw=1.5))
    p.append(circle(760, 200, 9, fill="#10b981", stroke="#047857", sw=1.5))
    p.append(text(720, 230, "Фіксація краплями УФ-маски", size=10.5, color="#047857", bold=True))

    b_c2, _, _ = textbox(715, 300, "• Паяння до тестової точки або виводу чипа\n• Акуратне прокладання вздовж полігону\n• Фіксація УФ-клеєм для захисту від вібрації",
                         size=11.5, fill="#ffffff", stroke=MUTED)
    p.append(b_c2)

    # Нижній висновок
    b_bot, _, _ = textbox(W / 2, 405,
                          "Апаратний патч першої ревізії обов'язково фотографується та супроводжується Rework-інструкцією,\nщоб уся партія лабораторних прототипів була модифікована ідентично.",
                          size=11.5, stroke=INK, fill="#eefaf1")
    p.append(b_bot)

    render(os.path.join(OUT, "hardware-patch-bodge.svg"), W, H, *p,
           title="Анатомія апаратного патчу: розріз доріжки та монтаж дротяної перемички")


if __name__ == "__main__":
    fig_errata_classification_matrix()
    fig_errata_record_structure()
    fig_parasitic_power_leakage()
    fig_hardware_patch_bodge()
    print("OK: generated 4 figures in img/")
