# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def svg_path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, stroke, sw, d_attr)


# ── Фігура 1: порівняння способів дебагу та прошивки в корпусі ───────────────
def fig_debug_access_comparison():
    W, H = 840, 440
    f = []

    f.append(text(W / 2, 28, "Способи налагодження та прошивки закритого виробу", size=16, bold=True))

    col_w = 250
    gap = 20
    x_starts = [35, 35 + col_w + gap, 35 + (col_w + gap) * 2]

    # Варіант 1: Відкритий роз'єм
    x1 = x_starts[0]
    f.append(rect(x1, 50, col_w, 375, fill="#fff6f5", stroke=POS, sw=1.5, rx=8))
    f.append(text(x1 + col_w / 2, 75, "1. Зовнішній роз'єм (гребінець)", size=13, bold=True, color=POS))
    b, _, _ = textbox(x1 + col_w / 2, 115, "Наскрізний отвір у стінці\nШтирі 2.54 мм або 1.27 мм", size=12, fill="#fdecea", stroke=POS, min_w=220); f.append(b)

    # Спрощена схема
    f.append(rect(x1 + 25, 155, col_w - 50, 75, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(rect(x1 + 35, 205, col_w - 70, 15, fill="#eafaf0", stroke=FIELD, sw=1))
    f.append(text(x1 + col_w / 2, 216, "Плата всередині", size=10, color=FIELD))
    f.append(line(x1 + 60, 155, x1 + 60, 205, color=POS, sw=2))
    f.append(line(x1 + 80, 155, x1 + 80, 205, color=POS, sw=2))
    f.append(line(x1 + 100, 155, x1 + 100, 205, color=POS, sw=2))
    f.append(text(x1 + col_w / 2, 145, "Вихід назовні крізь щілину", size=10, color=POS))

    b, _, _ = textbox(x1 + col_w / 2, 285, "Ризики:\n• Втрата герметичності IP\n• Корозія від вологи та солі\n• Прямий шлях для ESD-розряду\n• Ризик замикання брудом", size=11, fill="#ffffff", stroke=POS, min_w=220); f.append(b)
    b, _, _ = textbox(x1 + col_w / 2, 385, "Лише для макетів на столі", size=11, bold=True, fill="#fdecea", stroke=POS, color=POS); f.append(b)

    # Варіант 2: Pogo Pins / Tag-Connect під лючком
    x2 = x_starts[1]
    f.append(rect(x2, 50, col_w, 375, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(x2 + col_w / 2, 75, "2. Майданчики під лючком", size=13, bold=True, color=FIELD))
    b, _, _ = textbox(x2 + col_w / 2, 115, "Контактні п'ятаки ENIG\nTag-Connect / пого-піни стенда", size=12, fill="#eafaf0", stroke=FIELD, min_w=220); f.append(b)

    # Схема Tag-Connect
    f.append(rect(x2 + 25, 155, col_w - 50, 75, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(rect(x2 + 35, 205, col_w - 70, 15, fill="#eafaf0", stroke=FIELD, sw=1))
    f.append(rect(x2 + 75, 155, 100, 14, fill="#d8edd9", stroke=FIELD, sw=1.2))
    f.append(text(x2 + col_w / 2, 166, "Герметичний лючок", size=10, color=FIELD, bold=True))
    for px in [x2 + 85, x2 + 105, x2 + 125, x2 + 145, x2 + 165]:
        f.append(circle(px, 205, 3, fill="#c9a227", stroke=INK, sw=1))
    f.append(text(x2 + col_w / 2, 190, "Площадки 0.8–1.0 мм (нуль висоти)", size=10, color=INK))

    b, _, _ = textbox(x2 + col_w / 2, 285, "Переваги:\n• 0 грн вартості конектора на платі\n• Корпус герметичний у серії\n• Миттєве позиціювання щупів\n• Без механічного зносу швів", size=11, fill="#ffffff", stroke=FIELD, min_w=220); f.append(b)
    b, _, _ = textbox(x2 + col_w / 2, 385, "Ідеал: завод + сервісний центр", size=11, bold=True, fill="#eafaf0", stroke=FIELD, color=FIELD); f.append(b)

    # Варіант 3: Захищений магнітний конектор
    x3 = x_starts[2]
    f.append(rect(x3, 50, col_w, 375, fill="#f5f8ff", stroke=NEG, sw=1.5, rx=8))
    f.append(text(x3 + col_w / 2, 75, "3. Магнітний pogo-порт", size=13, bold=True, color=NEG))
    b, _, _ = textbox(x3 + col_w / 2, 115, "Герметичні піни в стінці\nМагнітна фіксація кабелю", size=12, fill="#eaf0fd", stroke=NEG, min_w=220); f.append(b)

    # Схема магнітного порту
    f.append(rect(x3 + 25, 155, col_w - 50, 75, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(rect(x3 + 35, 205, col_w - 70, 15, fill="#eafaf0", stroke=FIELD, sw=1))
    f.append(rect(x3 + 55, 140, 22, 15, fill="#e74c3c", stroke=INK, sw=1))
    f.append(rect(x3 + col_w - 77, 140, 22, 15, fill="#2457d6", stroke=INK, sw=1))
    f.append(text(x3 + 66, 152, "N", size=10, color="#ffffff", bold=True))
    f.append(text(x3 + col_w - 66, 152, "S", size=10, color="#ffffff", bold=True))
    for px in [x3 + 100, x3 + 125, x3 + 150]:
        f.append(rect(px - 3, 155, 6, 10, fill="#c9a227", stroke=INK, sw=1))
        f.append(line(px, 165, px, 205, color=LINE, sw=1.2))
    f.append(text(x3 + col_w / 2, 190, "TVS-діоди біля входів", size=10, color=POS))

    b, _, _ = textbox(x3 + col_w / 2, 285, "Особливості:\n• Доступ без розбирання виробу\n• Самовідрив при натягу кабелю\n• Потребує суворого TVS-захисту\n• Захист від бруду в поглибленні", size=11, fill="#ffffff", stroke=NEG, min_w=220); f.append(b)
    b, _, _ = textbox(x3 + col_w / 2, 385, "Польовий лог та швидка зарядка", size=11, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG); f.append(b)

    render(os.path.join(OUT, 'debug-access-comparison.svg'), W, H, *f,
           title="Порівняння способів доступу до налагодження")


# ── Фігура 2: взаємодія крізь глуху стінку корпусу ───────────────────────────
def fig_reed_capacitive_through_wall():
    W, H = 840, 420
    f = []

    f.append(text(W / 2, 26, "Керування без отворів: магнітний та ємнісний бар'єр", size=16, bold=True))

    half_w = 380
    gap = 20
    x_l = 30
    x_r = x_l + half_w + gap

    # Ліва панель: Геркон / Сенсор Холла
    f.append(rect(x_l, 46, half_w, 355, fill="#fcfdfa", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x_l + half_w / 2, 70, "Магнітне ввімкнення (геркон / Холл)", size=14, bold=True, color=INK))

    # Стінка
    f.append(rect(x_l + 170, 95, 20, 180, fill="#e6ddc9", stroke=INK, sw=1.5, rx=2))
    f.append(text(x_l + 180, 290, "Стінка корпусу (ABS, d = 2 мм)", size=10, color=MUTED))

    # Магніт зовні
    f.append(rect(x_l + 45, 150, 40, 30, fill="#e74c3c", stroke=INK, sw=1.5))
    f.append(rect(x_l + 85, 150, 40, 30, fill="#2457d6", stroke=INK, sw=1.5))
    f.append(text(x_l + 65, 170, "N", size=14, color="#ffffff", bold=True))
    f.append(text(x_l + 105, 170, "S", size=14, color="#ffffff", bold=True))
    f.append(text(x_l + 85, 140, "Зовнішній ключ-магніт", size=11, bold=True, color=POS))
    f.append(arrow(x_l + 130, 165, x_l + 165, 165, color=POS, sw=2))

    # Силові лінії
    f.append(svg_path("M %d 155 C %d 120, %d 120, %d 155" % (x_l + 65, x_l + 120, x_l + 250, x_l + 250), stroke="#c0392b", sw=1.2, dash="3,3"))
    f.append(svg_path("M %d 175 C %d 210, %d 210, %d 175" % (x_l + 65, x_l + 120, x_l + 250, x_l + 250), stroke="#2457d6", sw=1.2, dash="3,3"))

    # Плата і геркон всередині
    f.append(rect(x_l + 290, 110, 16, 150, fill="#eafaf0", stroke=FIELD, sw=1.5))
    f.append(text(x_l + 298, 100, "Плата", size=10, color=FIELD, bold=True))

    # Геркон
    f.append(rect(x_l + 235, 150, 40, 30, fill="#ffffff", stroke="#c9a227", sw=1.5, rx=6))
    f.append(line(x_l + 225, 162, x_l + 250, 162, color="#c9a227", sw=2))
    f.append(line(x_l + 258, 168, x_l + 285, 168, color="#c9a227", sw=2))
    f.append(line(x_l + 248, 162, x_l + 258, 168, color=POS, sw=2))
    f.append(text(x_l + 255, 195, "Геркон", size=10, bold=True, color="#c9a227"))

    b, _, _ = textbox(x_l + half_w / 2, 345, "Фізика: магнітне поле B вільно проходить крізь\nнемагнітний пластик (μr ≈ 1). Нуль отворів, IP68.\nЗахист від випадкових полів — утримання 5 с.", size=11, fill="#f4f6f8", stroke=LINE, min_w=340); f.append(b)

    # Права панель: Ємнісний сенсор
    f.append(rect(x_r, 46, half_w, 355, fill="#fcfdfa", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x_r + half_w / 2, 70, "Ємнісне відчуття дотику (Capacitive Touch)", size=14, bold=True, color=INK))

    # Стінка
    f.append(rect(x_r + 150, 95, 20, 180, fill="#e6ddc9", stroke=INK, sw=1.5, rx=2))
    f.append(text(x_r + 160, 290, "Стінка (d = 1.5–2.5 мм, εr ≈ 3)", size=10, color=MUTED))

    # Палець зовні
    f.append(rect(x_r + 35, 145, 95, 40, fill="#ffdcb4", stroke=INK, sw=1.5, rx=12))
    f.append(text(x_r + 80, 170, "Палець людини", size=11, bold=True, color=INK))
    f.append(text(x_r + 80, 140, "C_body ≈ 100 пФ", size=10, color=MUTED))

    # Електричні силові лінії
    for ly in [152, 160, 168, 176]:
        f.append(line(x_r + 130, ly, x_r + 150, ly, color=NEG, sw=1.5, dash="2,2"))

    # Плата праворуч
    f.append(rect(x_r + 280, 110, 16, 150, fill="#eafaf0", stroke=FIELD, sw=1.5))
    f.append(text(x_r + 288, 100, "Плата", size=10, color=FIELD, bold=True))

    # Пружина / провідна губка впритул до стінки
    f.append(rect(x_r + 170, 148, 14, 34, fill="#b0bec5", stroke=LINE, sw=1.2))
    f.append(line(x_r + 184, 152, x_r + 280, 152, color=LINE, sw=1.5))
    f.append(line(x_r + 184, 178, x_r + 280, 178, color=LINE, sw=1.5))
    f.append(rect(x_r + 276, 146, 5, 38, fill="#c9a227", stroke=INK, sw=1))
    f.append(text(x_r + 232, 142, "Пружина/Foam", size=10, bold=True, color=INK))
    f.append(text(x_r + 232, 195, "Без повітряного зазору!", size=10, color=POS, bold=True))

    b, _, _ = textbox(x_r + half_w / 2, 345, "Фізика: C = ε0·εr·S / d. При наближенні пальця\nємність зростає на ΔC ≈ 1–5 пФ. Повітряний зазор\nвбиває чутливість (ε_air = 1 проти ε_пластику = 3).", size=11, fill="#f4f6f8", stroke=LINE, min_w=340); f.append(b)

    render(os.path.join(OUT, 'reed-capacitive-through-wall.svg'), W, H, *f,
           title="Керування через пластикову стінку")


# ── Фігура 3: оптичний тракт світловода та захист від паразитних засвіток ────
def fig_light_pipe_optics():
    W, H = 840, 440
    f = []

    f.append(text(W / 2, 26, "Оптика світловода: повне внутрішнє відбиття та оптична ізоляція", size=16, bold=True))

    # Ліва частина: Хід променів і критичний кут
    x_l = 40
    w_l = 360
    f.append(rect(x_l, 48, w_l, 375, fill="#fcfdfa", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x_l + w_l / 2, 72, "Повне внутрішнє відбиття (TIR)", size=14, bold=True))

    # Світловод
    pipe_x = x_l + 120
    pipe_w = 120
    f.append(rect(pipe_x, 140, pipe_w, 170, fill="#edf5ff", stroke=NEG, sw=2, rx=4))
    f.append(text(pipe_x + pipe_w / 2, 210, "Світловод (PMMA)\nn ≈ 1.49", size=12, bold=True, color=NEG))

    # Вхідна лінза знизу світловода
    f.append(svg_path("M %d 310 Q %d 325, %d 310" % (pipe_x, pipe_x + pipe_w / 2, pipe_x + pipe_w), fill="#d6e8ff", stroke=NEG, sw=1.5))

    # SMD Світлодіод на платі
    f.append(rect(pipe_x + 35, 350, 50, 16, fill="#2c3e50", stroke=INK, sw=1.2))
    f.append(circle(pipe_x + 60, 354, 4, fill="#f1c40f", stroke=INK, sw=1))
    f.append(rect(x_l + 30, 366, w_l - 60, 12, fill="#eafaf0", stroke=FIELD, sw=1.5))
    f.append(text(x_l + 70, 376, "Плата (PCB)", size=10, color=FIELD, bold=True))
    f.append(text(pipe_x + 60, 344, "SMD LED", size=10, bold=True, color="#d35400"))

    # Промені від світлодіода
    f.append(line(pipe_x + 60, 350, pipe_x + 20, 260, color="#f39c12", sw=2))
    f.append(line(pipe_x + 20, 260, pipe_x + 100, 190, color="#f39c12", sw=2))
    f.append(line(pipe_x + 100, 190, pipe_x + 40, 140, color="#f39c12", sw=2))
    f.append(arrow(pipe_x + 40, 140, pipe_x + 40, 100, color="#f39c12", sw=2))

    # Вихідна панель
    f.append(rect(pipe_x - 10, 120, pipe_w + 20, 20, fill="#e6ddc9", stroke=INK, sw=1.5))
    f.append(text(pipe_x + pipe_w / 2, 134, "Лицьова панель приладу", size=10, color=INK))

    b, _, _ = textbox(x_l + w_l / 2, 402, "Критичний кут θc = arcsin(1 / n) ≈ 42.2°", size=11, color=NEG, bold=True, fill="#eaf0fd", stroke=NEG); f.append(b)

    # Права частина: Паразитна засвітка (Crosstalk) та ізоляція
    x_r = 440
    w_r = 360
    f.append(rect(x_r, 48, w_r, 375, fill="#fcfdfa", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x_r + w_r / 2, 72, "Оптична ізоляція сусідніх каналів", size=14, bold=True))

    # Два канали поруч
    p1_x = x_r + 50
    p2_x = x_r + 200
    p_w = 60

    # Світловоди
    f.append(rect(p1_x, 140, p_w, 170, fill="#edf5ff", stroke=NEG, sw=1.5, rx=3))
    f.append(rect(p2_x, 140, p_w, 170, fill="#edf5ff", stroke=NEG, sw=1.5, rx=3))

    # Чорна гумова гільза
    f.append(rect(p1_x - 6, 145, p_w + 12, 140, fill="none", stroke="#1a1a1a", sw=3.5))
    f.append(rect(p2_x - 6, 145, p_w + 12, 140, fill="none", stroke="#1a1a1a", sw=3.5))

    # Світлодіоди
    f.append(circle(p1_x + p_w / 2, 350, 5, fill="#27ae60", stroke=INK, sw=1))
    f.append(circle(p2_x + p_w / 2, 350, 5, fill="#e74c3c", stroke=INK, sw=1))
    f.append(text(p1_x + p_w / 2, 370, "LED 1 (Зелений)", size=10, color=FIELD, bold=True))
    f.append(text(p2_x + p_w / 2, 370, "LED 2 (Червоний)", size=10, color=POS, bold=True))

    # Паразитне світло блокується
    f.append(line(p1_x + p_w / 2, 345, p1_x + p_w + 4, 290, color="#27ae60", sw=2, dash="3,3"))
    f.append(text(p1_x + p_w + 45, 230, "Чорна еластомірна\nгільза блокує\nпаразитне світло", size=10, color=POS, bold=True))

    # Вихід
    f.append(rect(x_r + 20, 120, w_r - 40, 20, fill="#e6ddc9", stroke=INK, sw=1.5))
    f.append(circle(p1_x + p_w / 2, 130, 6, fill="#2ecc71", stroke=INK, sw=1))
    f.append(circle(p2_x + p_w / 2, 130, 6, fill="#7f8c8d", stroke=INK, sw=1))
    f.append(text(p1_x + p_w / 2, 105, "Чітка точка", size=10, color=FIELD, bold=True))
    f.append(text(p2_x + p_w / 2, 105, "Темно (без бліку)", size=10, color=MUTED, bold=True))

    b, _, _ = textbox(x_r + w_r / 2, 402, "Без гільзи світло розсіюється по всьому корпусу", size=11, color=INK, bold=True, fill="#fff8e1", stroke="#c9a227"); f.append(b)

    render(os.path.join(OUT, 'light-pipe-optics.svg'), W, H, *f,
           title="Хід променів у світловоді та усунення оптичного перекриття")


# ── Фігура 4: безпека батарейного відсіку та захист від переполюсовки ────────
def fig_battery_compartment_protection():
    W, H = 840, 440
    f = []

    f.append(text(W / 2, 26, "Батарейний відсік: механічний ключ, P-MOSFET та скидання газів", size=16, bold=True))

    # Ліва частина: Механічний відсік та газовідвід
    x_l = 35
    w_l = 370
    f.append(rect(x_l, 48, w_l, 375, fill="#fcfdfa", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x_l + w_l / 2, 72, "Механіка відсіку та захист від вибуху", size=13, bold=True))

    # Корпус відсіку
    f.append(rect(x_l + 25, 110, w_l - 50, 130, fill="#f4f6f8", stroke=INK, sw=1.5, rx=6))

    # Акумулятор 18650
    f.append(rect(x_l + 70, 130, 200, 90, fill="#34495e", stroke=INK, sw=1.5, rx=4))
    f.append(rect(x_l + 270, 155, 16, 40, fill="#bdc3c7", stroke=INK, sw=1.2)) # плюсовий сосок
    f.append(text(x_l + 160, 180, "Li-ion Акумулятор", size=13, bold=True, color="#ffffff"))
    f.append(text(x_l + 90, 180, "−", size=24, bold=True, color="#3498db"))
    f.append(text(x_l + 250, 180, "+", size=24, bold=True, color="#e74c3c"))

    # Механічний бурт (поляризація)
    f.append(rect(x_l + 286, 120, 12, 32, fill="#e67e22", stroke=INK, sw=1.2))
    f.append(rect(x_l + 286, 198, 12, 32, fill="#e67e22", stroke=INK, sw=1.2))
    f.append(text(x_l + 292, 112, "Пластиковий бурт-ключ", size=10, bold=True, color="#e67e22"))

    # Контактні пружини
    f.append(svg_path("M %d 175 L %d 160 L %d 190 L %d 165 L %d 185 L %d 175" %
                      (x_l + 45, x_l + 50, x_l + 55, x_l + 60, x_l + 65, x_l + 70), stroke="#c9a227", sw=2.5))
    f.append(text(x_l + 55, 210, "Пружина\nFN ≥ 1.5 Н", size=10, color=INK))

    # Газовідвідний клапан (мембрана) вгорі над відсіком
    f.append(rect(x_l + 140, 92, 70, 16, fill="#d5f5e3", stroke=FIELD, sw=1.5, rx=3))
    f.append(text(x_l + 175, 104, "GORE мембрана", size=10, bold=True, color=FIELD))
    f.append(text(x_l + w_l / 2, 265, "Скидання газів (degassing) при аварії банки\nВирівнює тиск, не пускає вологу всередину.", size=11, color=FIELD))

    b, _, _ = textbox(x_l + w_l / 2, 355, "Бурт фізично не дає плоскому мінусу\nдістати до контакту при перевертанні.", size=11, fill="#fef9e7", stroke="#c9a227", min_w=330); f.append(b)

    # Права частина: Електрична схема на P-MOSFET
    x_r = 430
    w_r = 375
    f.append(rect(x_r, 48, w_r, 375, fill="#fcfdfa", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x_r + w_r / 2, 72, "Електричний захист: P-MOSFET і TVS", size=13, bold=True))

    # Схема
    f.append(text(x_r + 40, 130, "+ BAT", size=12, bold=True, color=POS))
    f.append(text(x_r + 40, 240, "− BAT", size=12, bold=True, color=NEG))

    # Лінії живлення
    f.append(line(x_r + 70, 125, x_r + 150, 125, color=POS, sw=2))
    f.append(line(x_r + 70, 235, x_r + 320, 235, color=NEG, sw=2))

    # P-MOSFET
    f.append(rect(x_r + 150, 105, 70, 40, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    f.append(text(x_r + 185, 123, "P-MOSFET", size=10, bold=True, color=POS))
    f.append(text(x_r + 185, 137, "RDS < 20 мОм", size=10, color=MUTED))

    # Вихід до навантаження
    f.append(arrow(x_r + 220, 125, x_r + 320, 125, color=POS, sw=2))
    f.append(text(x_r + 335, 125, "+ VCC", size=11, bold=True, color=POS))
    f.append(text(x_r + 335, 235, "GND", size=11, bold=True, color=NEG))

    # Резистор затвора на GND
    f.append(line(x_r + 185, 145, x_r + 185, 175, color=LINE, sw=1.5))
    f.append(rect(x_r + 177, 175, 16, 30, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(text(x_r + 215, 192, "R_pull\n100 кОм", size=10, color=INK))
    f.append(line(x_r + 185, 205, x_r + 185, 235, color=LINE, sw=1.5))

    # Стабілітрон захисту затвора (Zener)
    f.append(line(x_r + 130, 125, x_r + 130, 175, color=LINE, sw=1.2))
    f.append(line(x_r + 130, 175, x_r + 185, 175, color=LINE, sw=1.2))
    f.append(rect(x_r + 122, 145, 16, 20, fill="#ffffff", stroke="#c9a227", sw=1.2))
    f.append(text(x_r + 105, 157, "VDZ\n12V", size=10, color="#c9a227"))

    # Пояснення роботи
    b, _, _ = textbox(x_r + w_r / 2, 300, "Пряме підключення: V_GS = −V_bat < V_th → транзистор\nповністю відімкнений, спад напруги < 10 мВ.\nЗворотне підключення: V_GS = 0 → закритий, струм 0.", size=10.5, fill="#eafaf0", stroke=FIELD, min_w=340); f.append(b)

    b, _, _ = textbox(x_r + w_r / 2, 375, "Падіння напруги в 50 разів менше за діод Шотткі", size=11, bold=True, fill="#fff8e1", stroke="#c9a227"); f.append(b)

    render(os.path.join(OUT, 'battery-compartment-protection.svg'), W, H, *f,
           title="Батарейний відсік та електричний захист від переполюсовки")


if __name__ == "__main__":
    fig_debug_access_comparison()
    fig_reed_capacitive_through_wall()
    fig_light_pipe_optics()
    fig_battery_compartment_protection()
    print("Всі 4 фігури успішно згенеровано.")
