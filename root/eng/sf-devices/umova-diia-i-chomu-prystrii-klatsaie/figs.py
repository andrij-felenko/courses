# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_chattering_problem():
    """Фігура 1: Проблема контактного брязкоту (Relay Chattering) при наївному пороговому порівнянні."""
    W, H = 760, 360
    p = []

    # Верхній графік: зашумлений аналоговий сигнал і один поріг
    ax_x, ax_w = 80, 620
    top_y0, top_h = 40, 140

    # Осі верхнього графіка
    p.append(arrow(ax_x, top_y0 + top_h, ax_x + ax_w, top_y0 + top_h, color=LINE, sw=1.5))
    p.append(arrow(ax_x, top_y0 + top_h, ax_x, top_y0 - 15, color=LINE, sw=1.5))
    p.append(text(ax_x - 15, top_y0 - 5, "Сигнал сенсора", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ax_x + ax_w, top_y0 + top_h + 18, "Час t", size=11, color=MUTED, anchor="end"))

    # Лінія єдиного наївного порога
    th_y = top_y0 + 65
    p.append(line(ax_x, th_y, ax_x + ax_w - 20, th_y, color=POS, sw=1.8, dash="5 4"))
    p.append(text(ax_x + ax_w - 10, th_y + 4, "Поріг (Threshold)", size=11, color=POS, anchor="start", bold=True))

    # Траєкторія зашумленого сигналу (хвиля з шумом, що перетинає поріг туди-сюди біля центру)
    raw_points = [
        (80, 150), (120, 145), (150, 142), (180, 135), (210, 125),
        (240, 115), (270, 112), (300, 106),
        # Критична зона перетину (x: 320 .. 490) - коливання навколо th_y (105)
        (330, 108), (345, 102), (360, 107), (375, 101), (390, 109),
        (405, 99),  (420, 106), (435, 98),  (450, 104), (465, 96),
        (480, 102), (495, 94),
        # Вихід у стабільну верхню зону
        (530, 85), (570, 75), (610, 65), (650, 60), (680, 58)
    ]
    
    pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in raw_points)
    p.append(f'<polyline points="{pts_str}" fill="none" stroke="{NEG}" stroke-width="2.2" />')

    # Підсвітка зони невизначеності / шуму
    p.append(rect(320, top_y0 + 20, 185, top_h - 20, fill="#fdedec", stroke=POS, sw=1.2, rx=4))
    p.append(text(412, top_y0 + 35, "Зона шуму біля порога", size=11, color=POS, bold=True))

    # Нижній графік: стан виконавчого механізму (Реле / Нагрівач)
    bot_y0, bot_h = 225, 95
    p.append(arrow(ax_x, bot_y0 + bot_h, ax_x + ax_w, bot_y0 + bot_h, color=LINE, sw=1.5))
    p.append(arrow(ax_x, bot_y0 + bot_h, ax_x, bot_y0 - 15, color=LINE, sw=1.5))
    p.append(text(ax_x - 15, bot_y0 - 5, "Вихід реле (0 / 1)", size=11, color=INK, anchor="end", bold=True))

    # Рівні 0 та 1
    y_off = bot_y0 + bot_h
    y_on = bot_y0 + 20
    p.append(text(ax_x - 8, y_off - 4, "ВИМК (0)", size=10, color=MUTED, anchor="end"))
    p.append(text(ax_x - 8, y_on + 4, "УВІМК (1)", size=10, color=MUTED, anchor="end"))
    p.append(line(ax_x, y_on, ax_x + ax_w - 20, y_on, color="#e0e0e0", sw=1, dash="2 2"))

    # Форма цифрового сигналу з пачкою брязкоту
    digital_pts = [
        (80, y_off), (330, y_off),
        # Брязкіт перемикань
        (330, y_on), (345, y_on), (345, y_off),
        (360, y_off), (360, y_on), (375, y_on), (375, y_off),
        (390, y_off), (390, y_on), (405, y_on), (405, y_off),
        (420, y_off), (420, y_on), (435, y_on), (435, y_off),
        (450, y_off), (450, y_on), (465, y_on), (465, y_off),
        (480, y_off), (480, y_on),
        # Стабільне увімкнення
        (680, y_on)
    ]
    dig_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in digital_pts)
    p.append(f'<polyline points="{dig_str}" fill="none" stroke="{POS}" stroke-width="2.5" />')

    # Пояснювальний напис про брязкіт
    b, _, _ = textbox(412, bot_y0 + bot_h + 22, "Relay Chattering: сотні перемикань за секунду руйнують контакти",
                      size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.4)
    p.append(b)

    render(os.path.join(OUT, "chattering-problem.svg"), W, H, *p,
           title="Проблема брязкоту стану при єдиному порозі компаратора")


def fig_hysteresis_loop():
    """Фігура 2: Петля гістерезису з двома порогами та мертвою зоною."""
    W, H = 760, 360
    p = []

    ox, oy = 110, 290
    gw, gh = 560, 230

    # Осі координат
    p.append(arrow(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.8))
    p.append(text(ox + gw, oy + 25, "Вхідний сигнал сенсора x", size=12, color=INK, anchor="end", bold=True))
    p.append(text(ox - 15, oy - gh - 10, "Стан виходу y", size=12, color=INK, anchor="end", bold=True))

    y_low = oy
    y_high = oy - gh

    p.append(text(ox - 10, y_low - 5, "0 (LOW)", size=11, color=MUTED, anchor="end", bold=True))
    p.append(text(ox - 10, y_high + 5, "1 (HIGH)", size=11, color=MUTED, anchor="end", bold=True))

    # Пороги
    x_tlow = ox + 180
    x_thigh = ox + 380
    x_sp = (x_tlow + x_thigh) / 2

    # Мертва зона (Deadband)
    p.append(rect(x_tlow, y_high, x_thigh - x_tlow, gh, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(x_sp, y_high + 30, "Мертва зона (Deadband Δ)", size=12, color=FIELD, bold=True))
    p.append(text(x_sp, y_high + 50, "стан не змінюється (пам'ять)", size=10, color=MUTED, italic=True))

    # Вертикальні лінії порогів
    p.append(line(x_tlow, oy, x_tlow, y_high - 10, color=NEG, sw=1.5, dash="4 4"))
    p.append(line(x_thigh, oy, x_thigh, y_high - 10, color=POS, sw=1.5, dash="4 4"))
    p.append(line(x_sp, oy, x_sp, y_high - 10, color="#888888", sw=1.2, dash="2 3"))

    p.append(text(x_tlow, oy + 20, "T_low (вимкнення)", size=11, color=NEG, bold=True))
    p.append(text(x_thigh, oy + 20, "T_high (увімкнення)", size=11, color=POS, bold=True))
    p.append(text(x_sp, oy + 38, "Уставка SP", size=11, color=INK, bold=True))

    # Траєкторія перемикання вперед (знизу вгору при зростанні x > T_high)
    # Нижня гілка
    p.append(line(ox, y_low, x_thigh, y_low, color=POS, sw=3.0))
    p.append(arrow(ox + 90, y_low, ox + 150, y_low, color=POS, sw=2.5))
    # Стрибок вгору при x = T_high
    p.append(line(x_thigh, y_low, x_thigh, y_high, color=POS, sw=3.0))
    p.append(arrow(x_thigh, y_low - 40, x_thigh, y_high + 40, color=POS, sw=2.5))
    # Продовження праворуч
    p.append(line(x_thigh, y_high, ox + gw - 30, y_high, color=POS, sw=3.0))

    # Траєкторія перемикання назад (зверху вниз при спаданні x < T_low)
    # Верхня гілка вліво
    p.append(line(ox + gw - 30, y_high, x_tlow, y_high, color=NEG, sw=2.5))
    p.append(arrow(ox + 480, y_high, ox + 420, y_high, color=NEG, sw=2.2))
    # Стрибок вниз при x = T_low
    p.append(line(x_tlow, y_high, x_tlow, y_low, color=NEG, sw=2.5))
    p.append(arrow(x_tlow, y_high + 40, x_tlow, y_low - 40, color=NEG, sw=2.2))

    # Підписи гілок
    p.append(text(x_thigh + 12, y_low - gh / 2, "Перехід 0 → 1 лише при x > T_high", size=10, color=POS, anchor="start", bold=True))
    p.append(text(x_tlow - 12, y_low - gh / 2, "Перехід 1 → 0 лише при x < T_low", size=10, color=NEG, anchor="end", bold=True))

    render(os.path.join(OUT, "hysteresis-loop.svg"), W, H, *p,
           title="Статична характеристика гістерезисного компаратора з двома порогами")


def fig_fsm_hysteresis():
    """Фігура 3: Граф станів автомату з гістерезисом та збереженням стану в мертвій зоні."""
    W, H = 760, 340
    p = []

    # Два основних стани автомата: IDLE (OFF) та ACTIVE (ON)
    s1_cx, s1_cy = 200, 160
    s2_cx, s2_cy = 560, 160
    r = 65

    # Стан 1: HEATER_OFF / IDLE
    p.append(circle(s1_cx, s1_cy, r, fill="#eaf0fd", stroke=NEG, sw=2.4))
    p.append(mtext(s1_cx, s1_cy - 12, "HEATER_OFF\n[Вимкнено]", size=13, color=NEG, bold=True))
    p.append(text(s1_cx, s1_cy + 22, "actuator = 0", size=11, color=MUTED))

    # Стан 2: HEATER_ON / ACTIVE
    p.append(circle(s2_cx, s2_cy, r, fill="#fdecea", stroke=POS, sw=2.4))
    p.append(mtext(s2_cx, s2_cy - 12, "HEATER_ON\n[Увімкнено]", size=13, color=POS, bold=True))
    p.append(text(s2_cx, s2_cy + 22, "actuator = 1", size=11, color=MUTED))

    # Перехід 1 -> 2: верхня дуга (сигнал впав нижче порога увімкнення T_on / T_low)
    # Стрілка з s1 в s2 зверху
    p.append(f'<path d="M {s1_cx + 45} {s1_cy - 45} Q 380 40 {s2_cx - 45} {s2_cy - 45}" '
             f'fill="none" stroke="{POS}" stroke-width="2.2" marker-end="url(#arrow)" />')
    tb1, _, _ = textbox(380, 52, "Умова: T_sensor < T_on  (холодно)", size=11, bold=True,
                        color=POS, fill="#fff5f5", stroke=POS, sw=1.4)
    p.append(tb1)

    # Перехід 2 -> 1: нижня дуга (сигнал піднявся вище порога вимкнення T_off / T_high)
    # Стрілка з s2 в s1 знизу
    p.append(f'<path d="M {s2_cx - 45} {s2_cy + 45} Q 380 280 {s1_cx + 45} {s1_cy + 45}" '
             f'fill="none" stroke="{NEG}" stroke-width="2.2" marker-end="url(#arrow)" />')
    tb2, _, _ = textbox(380, 268, "Умова: T_sensor > T_off  (нагріто)", size=11, bold=True,
                        color=NEG, fill="#f0f5ff", stroke=NEG, sw=1.4)
    p.append(tb2)

    # Петлі утримання стану (Self-loops) в мертвій зоні
    # Для стану OFF (зліва)
    p.append(f'<path d="M {s1_cx - 50} {s1_cy - 40} C {s1_cx - 130} {s1_cy - 60} '
             f'{s1_cx - 130} {s1_cy + 60} {s1_cx - 50} {s1_cy + 40}" '
             f'fill="none" stroke="{MUTED}" stroke-width="1.8" marker-end="url(#arrow)" />')
    p.append(mtext(s1_cx - 135, s1_cy - 6, "T_on ≤ T ≤ T_off\n(лишатися OFF)", size=10, color=MUTED, anchor="end"))

    # Для стану ON (справа)
    p.append(f'<path d="M {s2_cx + 50} {s2_cy - 40} C {s2_cx + 130} {s2_cy - 60} '
             f'{s2_cx + 130} {s2_cy + 60} {s2_cx + 50} {s2_cy + 40}" '
             f'fill="none" stroke="{MUTED}" stroke-width="1.8" marker-end="url(#arrow)" />')
    p.append(mtext(s2_cx + 135, s2_cy - 6, "T_on ≤ T ≤ T_off\n(лишатися ON)", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "fsm-hysteresis-table.svg"), W, H, *p,
           title="Автоматний граф переходів із гістерезисною мертвою зоною")


if __name__ == "__main__":
    fig_chattering_problem()
    fig_hysteresis_loop()
    fig_fsm_hysteresis()
    print("All figures rendered successfully.")
