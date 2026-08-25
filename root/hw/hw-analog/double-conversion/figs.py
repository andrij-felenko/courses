# -*- coding: utf-8 -*-
import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Колірна палітра
RF_COLOR   = "#8e44ad"  # Фіолетовий (ВЧ-сигнал)
LO_COLOR   = FIELD      # Зелений (Гетеродин)
IF1_COLOR  = POS        # Червоний (Перша ПЧ)
IF2_COLOR  = NEG        # Синій (Друга ПЧ)
SPUR_COLOR = MUTED      # Сірий (Завади/Дзеркальний)

def render(w, h, elements):
    """Скласти підсумковий SVG-документ з оголошенням стрілок."""
    defs = '''<defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/>
    </marker>
  </defs>''' % INK
    body = "\n  ".join(elements)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '  %s\n  %s\n</svg>' % (w, h, w, h, defs, body))

def save_svg(filename, content):
    path = os.path.join(OUT, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Збережено: %s" % path)


# ── Фігура 1: Порівняння однократного та подвійного перетворення ─────────────
def fig_single_vs_double_tradeoff():
    W, H = 760, 340
    p = []
    p.append(rect(0, 0, W, H, fill="#fafbfc", stroke=MUTED, sw=1.0, rx=0))

    # Секція 1: Низька ПЧ (однократна)
    p.append(rect(30, 20, 210, 290, fill="#fff5f5", stroke=POS, sw=1.2, rx=8))
    p.append(text(135, 45, "Однократна низька ПЧ", size=13, color=POS, bold=True))
    p.append(textbox(135, 80, "f_IF = 455 кГц", size=12, fill="#ffffff", stroke=POS, min_w=140)[0])
    p.append(textbox(135, 140, "Сусідня селективність:\nВІДМІННА (2.4 кГц)", size=11, color=POS, fill="#ffffff", stroke=POS, min_w=180)[0])
    p.append(textbox(135, 220, "Дзеркальний канал:\nКРИТИЧНО ПЛОХИЙ\n(відхилення 910 кГц)", size=11, color=POS, fill="#ffffff", stroke=POS, min_w=180)[0])

    # Секція 2: Висока ПЧ (однократна)
    p.append(rect(275, 20, 210, 290, fill="#f5f8ff", stroke=NEG, sw=1.2, rx=8))
    p.append(text(380, 45, "Однократна висока ПЧ", size=13, color=NEG, bold=True))
    p.append(textbox(380, 80, "f_IF = 10.7 МГц", size=12, fill="#ffffff", stroke=NEG, min_w=140)[0])
    p.append(textbox(380, 140, "Дзеркальний канал:\nВІДМІННИЙ (> 70 дБ)\n(відхилення 21.4 МГц)", size=11, color=NEG, fill="#ffffff", stroke=NEG, min_w=180)[0])
    p.append(textbox(380, 220, "Сусідня селективність:\nВАЖКО / НЕМОЖЛИВО\n(потрібен Q > 4400)", size=11, color=NEG, fill="#ffffff", stroke=NEG, min_w=180)[0])

    # Секція 3: Подвійне перетворення
    p.append(rect(520, 20, 210, 290, fill="#f2fdf5", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(625, 45, "Подвійне перетворення", size=13, color=FIELD, bold=True))
    p.append(textbox(625, 80, "1-ша ПЧ: 45 МГц\n2-га ПЧ: 455 кГц", size=12, fill="#ffffff", stroke=FIELD, min_w=160)[0])
    p.append(textbox(625, 150, "1-ше перетворення:\nВідсікає дзеркальний\nканал на 90+ дБ", size=11, color=FIELD, fill="#ffffff", stroke=FIELD, min_w=180)[0])
    p.append(textbox(625, 230, "2-ге перетворення:\nДає точну смугу\n2.4 кГц та підсилення", size=11, color=FIELD, fill="#ffffff", stroke=FIELD, min_w=180)[0])

    save_svg("single-vs-double-tradeoff.svg", render(W, H, p))


# ── Фігура 2: Блок-схема супергетеродина з подвійним перетворенням ───────────
def fig_double_conversion_block_diagram():
    W, H = 760, 300
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    # Антена
    p.append(line(30, 110, 30, 70, color=INK, sw=2.0))
    p.append(line(20, 70, 40, 70, color=INK, sw=2.0))
    p.append(line(20, 70, 30, 90, color=INK, sw=2.0))
    p.append(line(40, 70, 30, 90, color=INK, sw=2.0))
    p.append(arrow(30, 110, 60, 110, color=INK, sw=1.5))

    # Вхідний преселектор (ФНЧ / Смуговий)
    p.append(textbox(100, 110, "Вхідний\nпреселектор\n(ФНЧ/Смуга)", size=11, fill="#f4f6f8", stroke=RF_COLOR, min_w=80)[0])
    p.append(arrow(140, 110, 175, 110, color=INK, sw=1.5))

    # Змішувач 1
    p.append(circle(195, 110, 20, fill="#ffffff", stroke=RF_COLOR, sw=2.0))
    p.append(text(195, 114, "×", size=18, color=RF_COLOR, bold=True))
    p.append(arrow(195, 190, 195, 130, color=LO_COLOR, sw=1.5))
    p.append(textbox(195, 215, "Гетеродин 1\nLO1 (Перебуд.)", size=10, color=LO_COLOR, fill="#eafaf1", stroke=LO_COLOR, min_w=95)[0])

    p.append(arrow(215, 110, 260, 110, color=INK, sw=1.5))

    # Руфінг-фільтр (1-ша ПЧ)
    p.append(textbox(310, 110, "Руфінг-фільтр\n1-ша ПЧ (45 МГц)\nB = 15 кГц", size=11, color=IF1_COLOR, fill="#fdf2e9", stroke=IF1_COLOR, min_w=100)[0])
    p.append(arrow(360, 110, 405, 110, color=INK, sw=1.5))

    # Змішувач 2
    p.append(circle(425, 110, 20, fill="#ffffff", stroke=IF1_COLOR, sw=2.0))
    p.append(text(425, 114, "×", size=18, color=IF1_COLOR, bold=True))
    p.append(arrow(425, 190, 425, 130, color=LO_COLOR, sw=1.5))
    p.append(textbox(425, 215, "Гетеродин 2\nLO2 (Кварц)", size=10, color=LO_COLOR, fill="#eafaf1", stroke=LO_COLOR, min_w=90)[0])

    p.append(arrow(445, 110, 490, 110, color=INK, sw=1.5))

    # Канальний фільтр (2-га ПЧ)
    p.append(textbox(540, 110, "Канальний фільтр\n2-га ПЧ (455 кГц)\nB = 2.4 кГц", size=11, color=IF2_COLOR, fill="#ebf5fb", stroke=IF2_COLOR, min_w=100)[0])
    p.append(arrow(590, 110, 625, 110, color=INK, sw=1.5))

    # Демодулятор / DSP
    p.append(textbox(675, 110, "Підсилювач ПЧ2\nта Демодулятор\n(DSP / Звук)", size=11, fill="#f4f6f8", stroke=INK, min_w=100)[0])

    # Підписи частотних областей зверху
    p.append(text(100, 40, "Радіочастота (RF)", size=11, color=RF_COLOR, bold=True))
    p.append(text(310, 40, "Висока 1-ша ПЧ", size=11, color=IF1_COLOR, bold=True))
    p.append(text(540, 40, "Низька 2-га ПЧ", size=11, color=IF2_COLOR, bold=True))

    save_svg("double-conversion-block-diagram.svg", render(W, H, p))


# ── Фігура 3: Спектри подвійного перетворення ────────────────────────────────
def fig_spectrum_double_conversion():
    W, H = 760, 360
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    # Верхній спектр: Перше перетворення (ВЧ -> 1-ша ПЧ)
    p.append(text(380, 25, "1-ше перетворення: Перенос RF -> Висока ПЧ1 (віддалення 1-го дзеркального каналу)", size=12, color=INK, bold=True))
    base_y1 = 140
    p.append(line(40, base_y1, 700, base_y1, color=LINE, sw=1.5))
    p.append(arrow(700, base_y1, 720, base_y1, color=LINE, sw=1.5))
    p.append(text(725, base_y1 + 4, "f", size=12, color=INK, italic=True))

    # Сигнал RF (14 МГц)
    p.append(line(120, base_y1, 120, base_y1 - 60, color=RF_COLOR, sw=2.5))
    p.append(text(120, base_y1 + 20, "f_RF (14 МГц)", size=11, color=RF_COLOR, bold=True))

    # Перша ПЧ (45 МГц)
    p.append(line(290, base_y1, 290, base_y1 - 60, color=IF1_COLOR, sw=2.5))
    p.append(text(290, base_y1 + 20, "f_IF1 (45 МГц)", size=11, color=IF1_COLOR, bold=True))

    # Гетеродин LO1 (59 МГц)
    p.append(line(430, base_y1, 430, base_y1 - 85, color=LO_COLOR, sw=2.0, dash="4 3"))
    p.append(text(430, base_y1 + 20, "f_LO1 (59 МГц)", size=11, color=LO_COLOR, bold=True))

    # Дзеркальний 1 (104 МГц - далеко!)
    p.append(line(610, base_y1, 610, base_y1 - 40, color=SPUR_COLOR, sw=2.0, dash="3 3"))
    p.append(text(610, base_y1 + 20, "f_img1 (104 МГц)", size=11, color=SPUR_COLOR, bold=True))
    p.append(text(610, base_y1 + 35, "[Зрізано ФНЧ]", size=10, color=FIELD, italic=True))

    # Нижній спектр: Друге перетворення (1-ша ПЧ -> 2-га ПЧ)
    p.append(text(380, 205, "2-ге перетворення: Перенос ПЧ1 -> Низька ПЧ2 (відсікання 2-го дзеркального руфінгом)", size=12, color=INK, bold=True))
    base_y2 = 300
    p.append(line(40, base_y2, 700, base_y2, color=LINE, sw=1.5))
    p.append(arrow(700, base_y2, 720, base_y2, color=LINE, sw=1.5))
    p.append(text(725, base_y2 + 4, "f", size=12, color=INK, italic=True))

    # Друга ПЧ (455 кГц)
    p.append(line(100, base_y2, 100, base_y2 - 60, color=IF2_COLOR, sw=2.5))
    p.append(text(100, base_y2 + 20, "f_IF2 (455 кГц)", size=11, color=IF2_COLOR, bold=True))

    # Другий дзеркальний (44.09 МГц) — ліворуч від LO2
    p.append(line(320, base_y2, 320, base_y2 - 40, color=SPUR_COLOR, sw=2.0, dash="3 3"))
    p.append(text(320, base_y2 + 20, "f_img2 (44.09 МГц)", size=10, color=SPUR_COLOR, bold=True))
    p.append(text(320, base_y2 + 35, "[Зрізано руфінгом]", size=9, color=POS, bold=True))

    # Гетеродин LO2 (44.545 МГц)
    p.append(line(440, base_y2, 440, base_y2 - 85, color=LO_COLOR, sw=2.0, dash="4 3"))
    p.append(text(440, base_y2 + 20, "f_LO2 (44.545 МГц)", size=11, color=LO_COLOR, bold=True))

    # Перша ПЧ на входу 2-го змішувача (45.000 МГц)
    p.append(line(570, base_y2, 570, base_y2 - 60, color=IF1_COLOR, sw=2.5))
    p.append(text(570, base_y2 + 20, "f_IF1 (45.0 МГц)", size=11, color=IF1_COLOR, bold=True))

    # Руфінг-фільтр навколо IF1
    p.append(rect(555, base_y2 - 75, 30, 75, fill="#fdebd0", stroke=IF1_COLOR, sw=1.2, rx=4))
    p.append(text(570, base_y2 - 82, "Руфінг (15 кГц)", size=10, color=IF1_COLOR, bold=True))

    save_svg("spectrum-double-conversion.svg", render(W, H, p))


# ── Фігура 4: Схема Up-Conversion для КВ-діапазону ───────────────────────────
def fig_up_conversion_hf():
    W, H = 740, 260
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    base_y = 170
    p.append(line(40, base_y, 700, base_y, color=LINE, sw=1.5))
    p.append(arrow(700, base_y, 720, base_y, color=LINE, sw=1.5))
    p.append(text(725, base_y + 4, "f (МГц)", size=12, color=INK, italic=True))

    # Вхідний КВ діапазон (0.1 - 30 МГц)
    p.append(rect(60, base_y - 45, 150, 45, fill="#e8daef", stroke=RF_COLOR, sw=1.5, rx=4))
    p.append(text(135, base_y - 22, "Вхідний КВ діапазон\n(0.1 ... 30 МГц)", size=11, color=RF_COLOR, bold=True))
    p.append(text(135, base_y + 18, "Антена (RF)", size=11, color=RF_COLOR))

    # Вхідний ФНЧ (0-30 МГц)
    p.append(line(210, base_y - 65, 210, base_y, color=POS, sw=1.5, dash="4 2"))
    p.append(text(210, base_y - 72, "Зріз ФНЧ (30 МГц)", size=10, color=POS, bold=True))

    # 1-ша ПЧ (70.455 МГц) — ВИЩЕ ЗА ВСЕ!
    p.append(line(450, base_y, 450, base_y - 80, color=IF1_COLOR, sw=3.0))
    p.append(rect(435, base_y - 95, 30, 95, fill="#fadbd8", stroke=IF1_COLOR, sw=1.2, rx=4))
    p.append(text(450, base_y + 18, "f_IF1 = 70.455 МГц", size=11, color=IF1_COLOR, bold=True))
    p.append(text(450, base_y - 105, "Перша ПЧ (Руфінг)", size=10, color=IF1_COLOR))

    # Перший гетеродин LO1 (70.555 ... 100.455 МГц)
    p.append(rect(465, base_y - 50, 130, 50, fill="#e8f8f5", stroke=LO_COLOR, sw=1.5, rx=4))
    p.append(text(530, base_y - 25, "Діапазон LO1\n70.55 ... 100.45 МГц", size=10, color=LO_COLOR, bold=True))

    # Перший дзеркальний (140.9 ... 170.9 МГц) — ГЛИБОКО У ДЗЕРКАЛЬНІЙ ЗОНІ
    p.append(rect(610, base_y - 35, 75, 35, fill="#eaeded", stroke=SPUR_COLOR, sw=1.2, rx=4))
    p.append(text(647, base_y - 17, "Дзеркальні\n141...170 МГц", size=9, color=SPUR_COLOR, bold=True))
    p.append(text(647, base_y + 18, "f_img1 (Вище 140 МГц)", size=10, color=SPUR_COLOR))

    p.append(text(370, 35, "Архітектура Up-Conversion: ПЧ1 (70.45 МГц) вища за найвищу вхідну частоту (30 МГц)", size=12, color=INK, bold=True))

    save_svg("up-conversion-hf.svg", render(W, H, p))


# ── Фігура 5: Історичний Collins R-390A ──────────────────────────────────────
def fig_hist_collins_r390():
    W, H = 740, 240
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    p.append(text(370, 25, "Структурна схема легендарного приймача Collins R-390A (1954)", size=12, color=INK, bold=True))

    # Блоки
    p.append(textbox(80, 100, "Вхід КВ\n0.5-32 МГц", size=11, fill="#f4f6f8", min_w=80)[0])
    p.append(arrow(120, 100, 155, 100, color=INK))

    p.append(textbox(205, 100, "1-й Змішувач\n(Дискретний\nКварц LO1)", size=11, color=RF_COLOR, fill="#f5eeed", stroke=RF_COLOR, min_w=100)[0])
    p.append(arrow(255, 100, 290, 100, color=INK))

    p.append(textbox(355, 100, "Змінна 1-ша ПЧ\n(2.0 ... 3.0 МГц)\n+ Перестроюваний PTO", size=10, color=IF1_COLOR, fill="#fdebd0", stroke=IF1_COLOR, min_w=130)[0])
    p.append(arrow(420, 100, 455, 100, color=INK))

    p.append(textbox(515, 100, "2-й Змішувач\n+ Механічні дискові\nфільтри (455 кГц)", size=10, color=IF2_COLOR, fill="#ebf5fb", stroke=IF2_COLOR, min_w=120)[0])
    p.append(arrow(575, 100, 610, 100, color=INK))

    p.append(textbox(665, 100, "Підсилювач ПЧ2\nта Детектор", size=11, fill="#f4f6f8", min_w=90)[0])

    p.append(textbox(370, 185, "Особливість: Перший гетеродин перемикається кварцами через 1 МГц,\nа точна настройка виконується перестроюванням першої ПЧ (2-3 МГц).", size=11, color=FIELD, fill="#eafaf1", stroke=FIELD, min_w=580)[0])

    save_svg("hist-collins-r390.svg", render(W, H, p))


# ── Фігура 6: Топологія двоперетворювального фронтенду ───────────────────────
def fig_comp_frontend_topology():
    W, H = 740, 250
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    p.append(text(370, 25, "Схемотехнічна топологія ВЧ-фронтенду подвійного перетворення", size=12, color=INK, bold=True))

    p.append(textbox(80, 110, "Вхід RF\n(Преселектор)", size=11, fill="#f4f6f8", stroke=RF_COLOR, min_w=90)[0])
    p.append(arrow(125, 110, 160, 110))

    p.append(textbox(220, 110, "Пасивний Змішувач 1\n(FST3125 FET-ключі /\nОсередка Гілберта)", size=10, color=RF_COLOR, fill="#f4ecf7", stroke=RF_COLOR, min_w=120)[0])
    p.append(arrow(280, 110, 315, 110))

    p.append(textbox(375, 110, "Кварцовий Руфінг\n(45 МГц, B=15 кГц)\n+ Узгодження LC", size=10, color=IF1_COLOR, fill="#fadbd8", stroke=IF1_COLOR, min_w=120)[0])
    p.append(arrow(435, 110, 470, 110))

    p.append(textbox(530, 110, "Інтегральна 2-га ПЧ\n(SA605 / MC3362)\nЗмішувач 2 + LO2", size=10, color=IF2_COLOR, fill="#d4efdf", stroke=IF2_COLOR, min_w=120)[0])
    p.append(arrow(590, 110, 625, 110))

    p.append(textbox(670, 110, "Керамічний\nФільтр\n455 кГц", size=10, fill="#f4f6f8", stroke=INK, min_w=70)[0])

    p.append(text(220, 180, "LO1 (+13 дБм)", size=11, color=LO_COLOR, bold=True))
    p.append(arrow(220, 170, 220, 145, color=LO_COLOR))

    p.append(text(530, 180, "Кварц LO2 (44.545 МГц)", size=11, color=LO_COLOR, bold=True))
    p.append(arrow(530, 170, 530, 145, color=LO_COLOR))

    save_svg("comp-frontend-topology.svg", render(W, H, p))


# ── Фігура 7: Розпіновка та схема IC подвійного перетворення ─────────────────
def fig_comp_ic_pinout():
    W, H = 820, 300
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))

    p.append(text(410, 25, "Функціональна схема та виводи двоперетворювальної мікросхеми (тип MC3362)", size=12, color=INK, bold=True))

    # Корпус мікросхеми у центрі
    p.append(rect(260, 50, 300, 220, fill="#2c3e50", stroke="#1a252f", sw=2.0, rx=6))
    p.append(text(410, 80, "MC3362 / SA605", size=14, color="#ffffff", bold=True))
    p.append(circle(285, 75, 5, fill="#ecf0f1", stroke="none"))

    # Виводи зліва
    pins_left = [
        (1, "RF_IN (Вхід ВЧ)"),
        (2, "LO1_OSC (Гетеродин 1)"),
        (3, "MIX1_OUT (Вихід Зміш 1)"),
        (4, "IF1_IN (Вхід 1-ї ПЧ)"),
        (5, "VCC (+5V Живлення)")
    ]
    for i, (num, label) in enumerate(pins_left):
        y = 110 + i * 32
        p.append(rect(180, y - 8, 80, 16, fill="#bdc3c7", stroke=INK, sw=1.0, rx=2))
        p.append(text(220, y + 4, str(num), size=10, color=INK, bold=True))
        p.append(line(130, y, 180, y, color=INK, sw=1.5))
        p.append(text(125, y + 4, label, size=10, color=INK, anchor="end"))

    # Виводи справа
    pins_right = [
        (10, "AUDIO_OUT (Звук)"),
        (9,  "RSSI_OUT (Рівень)"),
        (8,  "IF2_IN (Вхід 2-ї ПЧ)"),
        (7,  "MIX2_OUT (Вихід Зміш 2)"),
        (6,  "OSC2 (Кварц LO2)")
    ]
    for i, (num, label) in enumerate(pins_right):
        y = 110 + i * 32
        p.append(rect(560, y - 8, 80, 16, fill="#bdc3c7", stroke=INK, sw=1.0, rx=2))
        p.append(text(600, y + 4, str(num), size=10, color=INK, bold=True))
        p.append(line(640, y, 690, y, color=INK, sw=1.5))
        p.append(text(695, y + 4, label, size=10, color=INK, anchor="start"))

    save_svg("comp-ic-pinout.svg", render(W, H, p))


if __name__ == "__main__":
    print("Генерація SVG фігур для теми double-conversion...")
    fig_single_vs_double_tradeoff()
    fig_double_conversion_block_diagram()
    fig_spectrum_double_conversion()
    fig_up_conversion_hf()
    fig_hist_collins_r390()
    fig_comp_frontend_topology()
    fig_comp_ic_pinout()
    print("Генерацію завершено успішно.")
