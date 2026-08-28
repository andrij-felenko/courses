# -*- coding: utf-8 -*-
"""Фігури для теми «Де закінчується девборда» (root/course/embedded/de-zakinchuietsia-devborda).
Генерує SVG у ./img/ за допомогою svgkit.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
from svgkit import (render, text, mtext, rect, line, arrow, circle, textbox,
                    fitbox, INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── 1. dupont-inductance-loop.svg ─────────────────────────────────────────────
def fig_dupont_loop():
    W, H = 820, 390
    parts = []

    # Фон лівої панелі (Дроти DuPont / макетка)
    parts.append(rect(15, 15, 385, 360, fill="#fffaf9", stroke=POS, sw=1.5, rx=8))
    parts.append(text(207, 42, "Макетка: роздільні дроти DuPont", size=15, color=POS, bold=True))
    parts.append(text(207, 60, "Велика петля струму, висока індуктивність L ≈ 180 нГн", size=11, color=MUTED))

    # Мікроконтролер ліворуч
    parts.append(rect(35, 95, 75, 170, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=4))
    parts.append(text(72, 175, "МК\n(вихід)", size=12, color=INK, bold=True))
    parts.append(circle(110, 125, 4, fill=POS, stroke=LINE, sw=1))
    parts.append(circle(110, 235, 4, fill=NEG, stroke=LINE, sw=1))
    parts.append(text(125, 120, "TX / SCK", size=10, color=POS, anchor="start"))
    parts.append(text(125, 245, "GND", size=10, color=NEG, anchor="start"))

    # Давач праворуч
    parts.append(rect(305, 95, 75, 170, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=4))
    parts.append(text(342, 175, "Давач\n(вхід)", size=12, color=INK, bold=True))
    parts.append(circle(305, 125, 4, fill=POS, stroke=LINE, sw=1))
    parts.append(circle(305, 235, 4, fill=NEG, stroke=LINE, sw=1))

    # Довгі вигнуті дроти з великою петлею
    parts.append('<path d="M 110 125 C 160 80, 250 80, 305 125" fill="none" stroke="%s" stroke-width="2.5"/>' % POS)
    parts.append('<path d="M 305 235 C 250 280, 160 280, 110 235" fill="none" stroke="%s" stroke-width="2.5"/>' % NEG)

    # Площа петлі (заливка)
    parts.append('<path d="M 110 125 C 160 80, 250 80, 305 125 L 305 235 C 250 280, 160 280, 110 235 Z" fill="#c0392b" fill-opacity="0.08" stroke="none"/>')

    # Позначення петлі
    parts.append(text(207, 165, "Площа петлі A", size=13, color=POS, bold=True))
    parts.append(text(207, 185, "Антена для наводок + дзвін", size=11, color=INK))
    parts.append(text(207, 203, "ΔV = L · (di / dt)", size=12, color=POS, bold=True))

    # Підсумкова плашка ліворуч
    parts.append(rect(28, 290, 358, 70, fill="#ffffff", stroke="#e0b4b0", sw=1, rx=4))
    parts.append(text(207, 312, "Наслідки для швидких шин (SPI > 4 МГц):", size=11, color=POS, bold=True))
    parts.append(text(207, 330, "• Викиди напруги (дзвін) понад 4.5 В при 3.3 В живленні", size=10, color=INK))
    parts.append(text(207, 348, "• Помилкові строби тактування й збої зв'язку", size=10, color=INK))

    # Фон правої панелі (Власна плата PCB microstrip)
    parts.append(rect(420, 15, 385, 360, fill="#f7fbf8", stroke=FIELD, sw=1.5, rx=8))
    parts.append(text(612, 42, "Власна PCB: мікрополоскова лінія", size=15, color=FIELD, bold=True))
    parts.append(text(612, 60, "Мінімальна петля, суцільна земля, L < 0.5 нГн", size=11, color=MUTED))

    # Мікроконтролер ліворуч
    parts.append(rect(440, 95, 75, 170, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=4))
    parts.append(text(477, 175, "МК\n(SMD)", size=12, color=INK, bold=True))
    parts.append(circle(515, 135, 4, fill=FIELD, stroke=LINE, sw=1))
    parts.append(circle(515, 215, 4, fill=NEG, stroke=LINE, sw=1))

    # Давач праворуч
    parts.append(rect(710, 95, 75, 170, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=4))
    parts.append(text(747, 175, "Давач\n(SMD)", size=12, color=INK, bold=True))
    parts.append(circle(710, 135, 4, fill=FIELD, stroke=LINE, sw=1))
    parts.append(circle(710, 215, 4, fill=NEG, stroke=LINE, sw=1))

    # Шари PCB між чипами
    parts.append(rect(515, 131, 195, 8, fill=FIELD, stroke="none"))
    parts.append(text(612, 122, "Сигнальна доріжка (Top Layer, Z₀ = 50 Ом)", size=10, color=FIELD, bold=True))

    parts.append(rect(515, 139, 195, 68, fill="#eef3e8", stroke="#ccd9c4", sw=1))
    parts.append(text(612, 175, "Діелектрик препрегу h ≈ 0.1–0.2 мм", size=10, color=MUTED, italic=True))

    parts.append(rect(515, 207, 195, 12, fill=NEG, stroke="none"))
    parts.append(text(612, 235, "Зворотний струм тече суворо під доріжкою", size=10, color=NEG, bold=True))

    # Підсумкова плашка праворуч
    parts.append(rect(433, 290, 358, 70, fill="#ffffff", stroke="#b9dbbf", sw=1, rx=4))
    parts.append(text(612, 312, "Переваги власної друкованої плати:", size=11, color=FIELD, bold=True))
    parts.append(text(612, 330, "• Контрольований хвильовий опір без відбиттів", size=10, color=INK))
    parts.append(text(612, 348, "• Стабільна робота SPI на 20–50 МГц та захист від EMI", size=10, color=INK))

    render(out("dupont-inductance-loop.svg"), W, H, *parts)


# ── 2. devboard-leakage-paths.svg ─────────────────────────────────────────────
def fig_leakage_paths():
    W, H = 840, 420
    parts = []

    # Заголовок блоку
    parts.append(rect(15, 15, 810, 390, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    parts.append(text(420, 42, "Анатомія прихованого споживання девборди в режимі «глибокого сну»", size=15, color=INK, bold=True))
    parts.append(text(420, 60, "Голий чип МК спить на 10 мкА, але плата споживає 15–25 мА через службову обв'язку", size=11, color=MUTED))

    # Вхідне живлення (USB 5V або Батарея)
    parts.append(rect(30, 110, 100, 70, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(80, 140, "Живлення\nUSB 5 В", size=12, color=INK, bold=True))

    # Лінія 5V
    parts.append(arrow(130, 145, 185, 145, color=POS, sw=2))

    # Блок LDO стабілізатора (AMS1117 / ME6211)
    parts.append(rect(185, 105, 130, 80, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    parts.append(text(250, 135, "LDO 3.3 В\n(AMS1117)", size=12, color=POS, bold=True))
    parts.append(text(250, 168, "I_q ≈ 5–10 мА!", size=11, color=POS, bold=True))

    # Вихідна шина 3.3V
    parts.append(line(315, 145, 365, 145, color=POS, sw=2.5))
    parts.append(line(365, 145, 365, 305, color=POS, sw=2))

    # 1. Мікроконтролер (MCU)
    parts.append(rect(400, 105, 145, 80, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(472, 135, "Чип МК (ESP32/STM32)", size=11, color=FIELD, bold=True))
    parts.append(text(472, 155, "Deep Sleep: 5–15 мкА", size=11, color=FIELD, bold=True))
    parts.append(text(472, 172, "(реальне споживання ядра)", size=9, color=MUTED))
    parts.append(arrow(365, 145, 400, 145, color=POS, sw=1.5))

    # 2. Світлодіод живлення (Power LED)
    parts.append(rect(400, 195, 145, 60, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    parts.append(text(472, 220, "Світлодіод живлення", size=11, color=POS, bold=True))
    parts.append(text(472, 240, "I_led ≈ 1.5–3.0 мА", size=11, color=POS, bold=True))
    parts.append(arrow(365, 225, 400, 225, color=POS, sw=1.5))

    # 3. USB-UART міст (CH340 / CP2102 / FT232)
    parts.append(rect(400, 265, 145, 75, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    parts.append(text(472, 290, "USB-UART міст", size=11, color=POS, bold=True))
    parts.append(text(472, 308, "CP2102 / CH340", size=10, color=MUTED))
    parts.append(text(472, 326, "Витік: 8–15 мА", size=11, color=POS, bold=True))
    parts.append(arrow(365, 302, 400, 302, color=POS, sw=1.5))

    # Фантомне живлення через лінії TX/RX: обхідний шлях праворуч від блоків
    parts.append(line(545, 302, 575, 302, color=POS, sw=1.5))
    parts.append(line(575, 302, 575, 145, color=POS, sw=1.5))
    parts.append(arrow(575, 145, 545, 145, color=POS, sw=1.5))
    parts.append(text(585, 218, "Паразитний витік\nкрізь RX/TX діоди", size=9, color=POS, bold=True, anchor="start"))

    # Підсумкова порівняльна таблиця праворуч
    parts.append(rect(670, 105, 140, 235, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(740, 130, "Підсумок уві сні", size=12, color=INK, bold=True))
    parts.append(line(680, 142, 800, 142, color=LINE, sw=0.8))

    parts.append(text(740, 163, "Девборда:", size=11, color=POS, bold=True))
    parts.append(text(740, 178, "15–25 мА", size=11, color=POS, bold=True))
    parts.append(text(740, 193, "2000 мАг: ~4 дні", size=9, color=MUTED))

    parts.append(line(685, 208, 795, 208, color="#e0e0e0", sw=0.8))

    parts.append(text(740, 230, "Власна плата:", size=11, color=FIELD, bold=True))
    parts.append(text(740, 246, "10–25 мкА", size=11, color=FIELD, bold=True))
    parts.append(text(740, 261, "2000 мАг: >5 років", size=9, color=FIELD, bold=True))

    parts.append(rect(678, 280, 124, 45, fill="#eafaf1", stroke=FIELD, sw=1, rx=4))
    parts.append(text(740, 298, "Різниця автономії:", size=9, color=INK))
    parts.append(text(740, 313, "у 1000 разів!", size=12, color=FIELD, bold=True))

    # Виноски внизу
    parts.append(rect(30, 365, 780, 30, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=4))
    parts.append(text(420, 385, "Висновок: тестувати енергоспоживання автономного пристрою на девборді «як є» неможливо.", size=11, color=INK, bold=True))

    render(out("devboard-leakage-paths.svg"), W, H, *parts)


# ── 3. transient-scope-comparison.svg ─────────────────────────────────────────
def fig_transient_scope():
    W, H = 820, 380
    parts = []

    # Загальна рамка
    parts.append(rect(15, 15, 790, 350, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))

    # Ліва половина: Осцилограма макетки
    parts.append(rect(30, 30, 365, 320, fill="#1c2421", stroke=POS, sw=1.5, rx=6))
    parts.append(text(212, 55, "Девборда + макетка (SPI SCK 12 МГц)", size=13, color="#fdecea", bold=True))
    parts.append(text(212, 72, "Дзвін через L_дроту, викиди V_pp > 4.6 В", size=10, color="#f5b7b1"))

    # Сітка осцилографа ліворуч
    for gx in range(50, 380, 40):
        parts.append(line(gx, 85, gx, 275, color="#2e3b36", sw=0.8, dash="2,2"))
    for gy in range(85, 280, 38):
        parts.append(line(50, gy, 370, gy, color="#2e3b36", sw=0.8, dash="2,2"))

    # Опорні рівні
    parts.append(text(42, 125, "3.3V", size=9, color="#95a5a6", anchor="end"))
    parts.append(text(42, 239, "0.0V", size=9, color="#95a5a6", anchor="end"))
    parts.append(line(50, 123, 370, 123, color="#566573", sw=1, dash="4,4"))
    parts.append(line(50, 237, 370, 237, color="#566573", sw=1, dash="4,4"))

    # Крива сигналу з сильним дзвоном та викидами
    s_wave = (
        "M 55 237 L 85 237 "
        "L 95 90 "
        "Q 105 155, 115 105 "
        "Q 125 135, 135 120 "
        "L 165 123 "
        "L 175 270 "
        "Q 185 210, 195 250 "
        "Q 205 230, 215 237 "
        "L 245 237 "
        "L 255 90 "
        "Q 265 155, 275 105 "
        "Q 285 135, 295 120 "
        "L 325 123 "
        "L 335 270 "
        "Q 345 210, 355 250 "
        "L 365 237"
    )
    parts.append('<path d="%s" fill="none" stroke="#e74c3c" stroke-width="2.5"/>' % s_wave)

    # Виноска на викид
    parts.append(arrow(150, 95, 102, 92, color=POS, sw=1.2))
    parts.append(text(155, 98, "Викид +1.5 В (дзвін)", size=10, color=POS, bold=True, anchor="start"))
    parts.append(arrow(240, 270, 185, 270, color=POS, sw=1.2))
    parts.append(text(245, 273, "Просідання під GND (-0.7 В)", size=10, color=POS, bold=True, anchor="start"))

    parts.append(rect(40, 285, 345, 55, fill="#2a1b1a", stroke=POS, sw=1, rx=4))
    parts.append(text(212, 305, "Небезпека: пробій затворів польовиків,", size=10, color="#f5b7b1"))
    parts.append(text(212, 323, "паразитний latch-up та фальшиві тактові імпульси", size=10, color="#f5b7b1", bold=True))

    # Права половина: Осцилограма друкованої плати
    parts.append(rect(425, 30, 365, 320, fill="#1c2421", stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(607, 55, "Власна плата (узгоджений імпеданс 50 Ом)", size=13, color="#eafaf1", bold=True))
    parts.append(text(607, 72, "Чистий прямокутний фронт без дзвону", size=10, color="#a9dfbf"))

    # Сітка осцилографа праворуч
    for gx in range(445, 775, 40):
        parts.append(line(gx, 85, gx, 275, color="#2e3b36", sw=0.8, dash="2,2"))
    for gy in range(85, 280, 38):
        parts.append(line(445, gy, 765, gy, color="#2e3b36", sw=0.8, dash="2,2"))

    parts.append(text(437, 125, "3.3V", size=9, color="#95a5a6", anchor="end"))
    parts.append(text(437, 239, "0.0V", size=9, color="#95a5a6", anchor="end"))
    parts.append(line(445, 123, 765, 123, color="#566573", sw=1, dash="4,4"))
    parts.append(line(445, 237, 765, 237, color="#566573", sw=1, dash="4,4"))

    # Чиста крива
    clean_wave = (
        "M 450 237 L 480 237 "
        "L 490 123 "
        "L 560 123 "
        "L 570 237 "
        "L 640 237 "
        "L 650 123 "
        "L 720 123 "
        "L 730 237 "
        "L 760 237"
    )
    parts.append('<path d="%s" fill="none" stroke="#2ecc71" stroke-width="2.5"/>' % clean_wave)

    parts.append(arrow(580, 110, 520, 120, color=FIELD, sw=1.2))
    parts.append(text(585, 113, "Ідеальна плоска поличка", size=10, color=FIELD, bold=True, anchor="start"))

    parts.append(rect(435, 285, 345, 55, fill="#1a2a1f", stroke=FIELD, sw=1, rx=4))
    parts.append(text(607, 305, "Результат: 100% валідність пакетів на 40 МГц,", size=10, color="#a9dfbf"))
    parts.append(text(607, 323, "нульовий джиттер та відсутність EMI завад", size=10, color="#a9dfbf", bold=True))

    render(out("transient-scope-comparison.svg"), W, H, *parts)


# ── 4. prototype-to-pcb-flow.svg ──────────────────────────────────────────────
def fig_flowchart():
    W, H = 820, 260
    parts = []

    # Загальний фон
    parts.append(rect(15, 15, 790, 230, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    parts.append(text(410, 42, "Гейти готовності прототипу до переходу на власну друковану плату (PCB)", size=15, color=INK, bold=True))

    boxes_data = [
        ("1. Функціональний PoC", "Перевірка алгоритму\nта сумісності чипів\nна девборді"),
        ("2. Фіксація пінів", "Розподіл апаратних\nфункцій (DMA, Timers,\nUART/SPI без конфліктів)"),
        ("3. Аудит живлення", "Вимір пікових струмів,\nвибір джерела,\nбюджет сну"),
        ("4. Схемотехніка PCB", "Додавання TVS-захисту,\nфільтрів живлення,\nправильних LDO"),
    ]

    bx_w = 160
    bx_h = 100
    y_top = 75
    spacing = 195
    x_start = 35

    for i, (b_title, b_desc) in enumerate(boxes_data):
        x = x_start + i * spacing
        is_last = (i == len(boxes_data) - 1)
        bg_col = "#eafaf1" if is_last else "#f4f6f8"
        strk_col = FIELD if is_last else LINE

        parts.append(rect(x, y_top, bx_w, bx_h, fill=bg_col, stroke=strk_col, sw=1.5, rx=6))
        parts.append(text(x + bx_w / 2, y_top + 25, b_title, size=11, color=INK, bold=True))
        parts.append(line(x + 10, y_top + 35, x + bx_w - 10, y_top + 35, color=strk_col, sw=0.8))
        parts.append(mtext(x + bx_w / 2, y_top + 53, b_desc, size=10, color=MUTED, lh=1.35))

        if i < len(boxes_data) - 1:
            arr_x1 = x + bx_w + 3
            arr_x2 = x + bx_w + 32
            arr_y = y_top + bx_h / 2
            parts.append(arrow(arr_x1, arr_y, arr_x2, arr_y, color=LINE, sw=2))

    # Висновок знизу
    parts.append(rect(35, 190, 750, 40, fill="#fdfefe", stroke="#d5d8dc", sw=1, rx=4))
    parts.append(text(410, 215, "Правило: переходити до трасування PCB лише тоді, коли всі 4 гейти закриті без невизначеностей.", size=11, color=FIELD, bold=True))

    render(out("prototype-to-pcb-flow.svg"), W, H, *parts)


def main():
    fig_dupont_loop()
    fig_leakage_paths()
    fig_transient_scope()
    fig_flowchart()
    print("Всі 4 фігури успішно згенеровано у img/")


if __name__ == "__main__":
    main()
