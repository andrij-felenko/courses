# -*- coding: utf-8 -*-
"""Фігури до статті «OCXO: термостатований кварцовий генератор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

HEAT = "#d35400"
COLD = "#2980b9"
PURPLE = "#8e44ad"

def polyline(pts, color, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s stroke-linejoin="round"/>' % (p, color, sw, d)


# ── 1. Анатомія та внутрішня будова OCXO ───────────────────────────────────────
def fig_ocxo_structure():
    W, H = 960, 560
    f = [
        text(W / 2, 28, "Анатомія термостатованого кварцового генератора (OCXO)", size=17, bold=True),
        text(W / 2, 50, "багатошаровий бар'єр захищає резонатор і схему від температурних коливань довкілля",
             size=12, color=MUTED, italic=True)
    ]

    # Зовнішній корпус (металевий екран)
    cx0, cy0, cw, ch = 60, 80, 540, 420
    f.append(rect(cx0, cy0, cw, ch, fill="#f8fafc", stroke=LINE, sw=2.5, rx=12))
    f.append(text(cx0 + 20, cy0 + 24, "Зовнішній герметичний екран (GND, ковар / нікельована латунь)",
                  size=12, bold=True, color=MUTED, anchor="start"))

    # Шар теплоізолятора (пінополіуретан / аерогель)
    ix0, iy0, iw, ih = cx0 + 24, cy0 + 38, cw - 48, ch - 68
    f.append(rect(ix0, iy0, iw, ih, fill="#fdfbf7", stroke="#d1d5db", sw=1.5, rx=8))
    f.append(text(ix0 + 15, iy0 + 22, "Теплоізоляційна сорочка (мікропористий аерогель / пінополіуретан, R_th ≈ 35–50 К/Вт)",
                  size=11, bold=True, color="#b45309", anchor="start"))

    # Внутрішня камера-термостат (Oven Block - мідь / алюміній)
    ox0, oy0, ow, oh = ix0 + 25, iy0 + 34, iw - 50, ih - 56
    f.append(rect(ox0, oy0, ow, oh, fill="#fef3c7", stroke=HEAT, sw=2.2, rx=6))
    f.append(text((ox0 + ox0 + ow) / 2, oy0 + 20, "Ізотермічна камера-термостат (мідний блок, T = 80.0 °C ± 0.001 °C)",
                  size=12.5, bold=True, color=HEAT))

    # Вузол 1: Кварцовий резонатор SC-зрізу всередині камери
    rx, ry, rw, rh = ox0 + 30, oy0 + 42, 180, 110
    f.append(rect(rx, ry, rw, rh, fill="#eff6ff", stroke=COLD, sw=2, rx=6))
    f.append(text(rx + rw / 2, ry + 24, "Кварцовий резонатор", size=12, bold=True, color=COLD))
    f.append(text(rx + rw / 2, ry + 44, "SC-зріз (C-мода)", size=11, bold=True, color=INK))
    f.append(text(rx + rw / 2, ry + 64, "Q ≈ 2.5·10⁶ (3-й обертон)", size=10.5, color=MUTED))
    f.append(text(rx + rw / 2, ry + 84, "Turnover T_turn = 80 °C", size=10.5, color="#1e40af", bold=True))

    # Вузол 2: Схема генератора коливань (Pierce/Colpitts) всередині термостата
    gx, gy, gw, gh = ox0 + 230, oy0 + 42, 180, 110
    f.append(rect(gx, gy, gw, gh, fill="#ecfdf5", stroke=FIELD, sw=2, rx=6))
    f.append(text(gx + gw / 2, gy + 24, "Схема генератора", size=12, bold=True, color=FIELD))
    f.append(text(gx + gw / 2, gy + 44, "Малошумний BJT / JFET", size=11, bold=True, color=INK))
    f.append(text(gx + gw / 2, gy + 64, "C0G/NP0 конденсатори", size=10.5, color=MUTED))
    f.append(text(gx + gw / 2, gy + 84, "Варікап EFC (підстроювання)", size=10.5, color="#065f46", bold=True))

    # Вузол 3: Датчик температури (NTC-термістор)
    sx, sy, sw, sh = ox0 + 30, oy0 + 175, 180, 60
    f.append(rect(sx, sy, sw, sh, fill="#fdf2f8", stroke=PURPLE, sw=1.8, rx=6))
    f.append(text(sx + sw / 2, sy + 22, "Прецизійний NTC", size=11.5, bold=True, color=PURPLE))
    f.append(text(sx + sw / 2, sy + 42, "Чутливість ≈ −4 %/°C", size=10.5, color=MUTED))

    # Вузол 4: Силовий нагрівач (транзистор або резистивний шар)
    hx, hy, hw, hh = ox0 + 230, oy0 + 175, 180, 60
    f.append(rect(hx, hy, hw, hh, fill="#fff7ed", stroke=POS, sw=1.8, rx=6))
    f.append(text(hx + hw / 2, hy + 22, "Силовий нагрівач", size=11.5, bold=True, color=POS))
    f.append(text(hx + hw / 2, hy + 42, "Power BJT (1–8 Вт тепла)", size=10.5, color=MUTED))

    # Зв'язки всередині термостата
    f.append(line(rx + rw, ry + 55, gx, gy + 55, color=INK, sw=1.6))
    f.append(line(sx + sw / 2, sy + sh, sx + sw / 2, sy + sh + 15, color=PURPLE, sw=1.6))
    f.append(line(hx + hw / 2, hy + hh, hx + hw / 2, hy + hh + 15, color=POS, sw=1.6))

    # Прохідні контакти знизу
    pin_y0 = cy0 + ch
    pin_y1 = pin_y0 + 35
    pins = [
        (cx0 + 80, "Vcc (+12V)"),
        (cx0 + 170, "GND"),
        (cx0 + 260, "RF Out (10MHz)"),
        (cx0 + 350, "Vref (5V)"),
        (cx0 + 440, "EFC (Vcontrol)")
    ]
    for px, plab in pins:
        f.append(circle(px, pin_y0, 5, fill="#94a3b8", stroke=LINE, sw=1.5))
        f.append(line(px, pin_y0, px, pin_y1, color=LINE, sw=2.5))
        f.append(circle(px, pin_y1, 4, fill=LINE, stroke=LINE, sw=1))
        f.append(text(px, pin_y1 + 18, plab, size=10.5, bold=True, color=INK))

    # Права панель з поясненнями ключових переваг
    px0, py0, pw, ph = 630, 80, 300, 420
    f.append(fitbox(px0, py0, pw, 130,
                    "Чому схема всередині термостата?\n"
                    "• Паразитні ємності транзисторів і фазовий зсув залежать від температури\n"
                    "• Конденсатори обв'язки C0G дрейфують на 30 ppm/°C\n"
                    "• Розміщення генератора в камері усуває дрейф усього активного тракту",
                    size=11, fill="#f8fafc", stroke="#94a3b8", color=INK))

    f.append(fitbox(px0, py0 + 145, pw, 130,
                    "Ізотермічний градієнт камери:\n"
                    "• Металевий корпус з високою теплопровідністю вирівнює температуру\n"
                    "• NTC розташований впритул до кристала для мінімізації фазового запізнення\n"
                    "• Механічні кріплення пружні, щоб уникнути термомеханічних напружень",
                    size=11, fill="#fef3c7", stroke=HEAT, color=INK))

    f.append(fitbox(px0, py0 + 290, pw, 130,
                    "Теплова ізоляція та енергетика:\n"
                    "• R_th сорочки: 35–50 К/Вт (P_hold ≈ 1.0–1.5 Вт при 25 °C)\n"
                    "• При −40 °C довкілля градієнт ΔT = 120 °C, споживання зростає до 2.5–3 Вт\n"
                    "• Відсутність конвекції всередині виключає флуктуаційні протяги",
                    size=11, fill="#eff6ff", stroke=COLD, color=INK))

    render(os.path.join(IMG, "ocxo-internal-structure.svg"), W, H, *f)


# ── 2. Температурно-частотні криві: AT-зріз проти SC-зрізу ──────────────────────
def fig_turnover_curves():
    W, H = 960, 540
    f = [
        text(W / 2, 28, "Точка нульового температурного коефіцієнта (Turnover Point)", size=17, bold=True),
        text(W / 2, 50, "термостатування в точці T_turn знищує лінійний нахил df/dT: відхилення лишається лише у 2-му порядку",
             size=12, color=MUTED, italic=True)
    ]

    L, R, T, B = 90, 620, 95, 450
    t_min, t_max = -20.0, 100.0     # Температура °C
    df_min, df_max = -25.0, 15.0    # Відхилення частоти ppm

    def X(t):
        return L + (t - t_min) / (t_max - t_min) * (R - L)

    def Y(df):
        return B - (df - df_min) / (df_max - df_min) * (B - T)

    # Сітка та осі
    f.append(line(L, T - 10, L, B, color=INK, sw=2))
    f.append(line(L, B, R + 10, B, color=INK, sw=2))
    f.append(text(R + 10, B + 24, "Температура T (°C)", size=12.5, bold=True, anchor="end"))
    f.append(text(L - 10, T - 16, "Δf/f (ppm)", size=12.5, bold=True, anchor="start"))

    # Нульова горизонтальна лінія
    f.append(line(L, Y(0), R, Y(0), color="#cbd5e1", sw=1.2, dash="4 4"))

    # Позначки по осі X
    for t_val in (-20, 0, 25, 50, 75, 80, 100):
        x = X(t_val)
        f.append(line(x, B, x, B + 6, color=INK, sw=1.2))
        f.append(text(x, B + 20, str(t_val), size=10.5, color=MUTED))

    # Позначки по осі Y
    for df_val in (-20, -10, 0, 10):
        y = Y(df_val)
        f.append(line(L - 6, y, L, y, color=INK, sw=1.2))
        f.append(text(L - 10, y + 4, "%+d" % df_val, size=10.5, color=MUTED, anchor="end"))

    # 1. Крива AT-зрізу (кубічна крива з нулем біля 25 °C)
    # df_AT(T) = a1*(T-25) + c1*(T-25)^3, де біля 80 °C нахил різкий
    at_pts = []
    for step in range(121):
        t = t_min + (t_max - t_min) * step / 120.0
        dt = t - 25.0
        df = 0.05 * dt - 0.00035 * (dt ** 3)
        at_pts.append((X(t), Y(df)))
    f.append(polyline(at_pts, COLD, sw=2.5, dash="6 4"))

    # 2. Крива SC-зрізу (парабола з вершиною рівно при T_turn = 80 °C)
    # df_SC(T) = -b * (T - 80)^2, де b ≈ 0.000035 ppm/K^2
    sc_pts = []
    for step in range(121):
        t = t_min + (t_max - t_min) * step / 120.0
        dt = t - 80.0
        df = 5.0 - 0.0032 * (dt ** 2)
        sc_pts.append((X(t), Y(df)))
    f.append(polyline(sc_pts, HEAT, sw=3.2))

    # Точка turnover point
    t_turn_x, t_turn_y = X(80.0), Y(5.0)
    f.append(line(t_turn_x, T - 6, t_turn_x, B, color=POS, sw=1.5, dash="3 3"))
    f.append(circle(t_turn_x, t_turn_y, 6.0, fill=POS, stroke=BG, sw=2))

    # Зона термостатування навколо 80 °C
    z_x1, z_x2 = X(78.5), X(81.5)
    f.append(rect(z_x1, T, z_x2 - z_x1, B - T, fill="#fef3c7", stroke="none"))
    f.append(text(t_turn_x, T + 18, "T_turn = 80 °C", size=12, bold=True, color=POS))
    f.append(text(t_turn_x, T + 36, "df/dT = 0", size=11, bold=True, color=POS))

    # Виноски на кривих
    f.append(text(X(25), Y(2.0), "AT-зріз (кубічна S-крива)", size=11, bold=True, color=COLD))
    f.append(text(X(35), Y(-12.0), "SC-зріз (оптимізований під 80 °C)", size=11.5, bold=True, color=HEAT))

    # Права панель з математичним порівнянням
    px, py, pw = 650, 95, 290
    f.append(fitbox(px, py, pw, 125,
                    "Параболічна модель біля T_turn:\n"
                    "Δf/f(T) = a·(T − T₀) + b·(T − T₀)²\n"
                    "У вершині T₀ = T_turn лінійний член a = 0:\n"
                    "df/dT = 2·b·(T − T_turn) = 0\n"
                    "Чутливість до тепла спадає в 1000+ разів!",
                    size=11, fill="#fef3c7", stroke=HEAT, color=INK))

    f.append(fitbox(px, py + 140, pw, 140,
                    "Розрахунок похибки при коливанні ΔT:\n"
                    "Якщо терморегулятор тримає T з точністю:\n"
                    "ΔT = ±0.01 °C = ±10 mK\n"
                    "Тоді відхилення частоти:\n"
                    "Δf/f = b · (0.01 °C)²\n"
                    "Δf/f ≈ −3.2·10⁻³ · 10⁻⁴ ppm = −3.2·10⁻¹³!\n"
                    "Це рівень кращих квантових стандартів.",
                    size=11, fill="#eff6ff", stroke=COLD, color=INK))

    f.append(fitbox(px, py + 295, pw, 120,
                    "Чому саме 75–85 °C?\n"
                    "• Вище максимальної температури приладу (+70 °C)\n"
                    "• Потрібен лише нагрівач, без охолоджувача Пельтьє\n"
                    "• Нижче межі деградації старіння кварцу (+95 °C)",
                    size=11, fill="#f8fafc", stroke="#94a3b8", color=INK))

    render(os.path.join(IMG, "turnover-temperature-sc-at.svg"), W, H, *f)


# ── 3. Функціональна схема PI-терморегулятора ────────────────────────────────────
def fig_pi_thermal_loop():
    W, H = 980, 520
    f = [
        text(W / 2, 28, "Прецизійний аналоговий PI-терморегулятор камери", size=17, bold=True),
        text(W / 2, 50, "неперервне пропорційно-інтегральне керування струмом нагрівача без імпульсних завад (ШІМ заборонено)",
             size=12, color=MUTED, italic=True)
    ]

    # Блок 1: Вимірювальний міст (Wheatstone Bridge)
    b1_x, b1_y, b1_w, b1_h = 40, 110, 200, 240
    f.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#f8fafc", stroke="#64748b", sw=1.8, rx=8))
    f.append(text(b1_x + b1_w / 2, b1_y + 24, "Вимірювальний міст", size=13, bold=True, color=INK))
    f.append(text(b1_x + b1_w / 2, b1_y + 44, "Прецизійний міст Уїтстона", size=10.5, color=MUTED))

    # Резистори мосту
    f.append(rect(b1_x + 25, b1_y + 70, 65, 40, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(b1_x + 57, b1_y + 94, "R_ref1", size=11, bold=True))
    f.append(rect(b1_x + 110, b1_y + 70, 65, 40, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(b1_x + 142, b1_y + 94, "R_set", size=11, bold=True))

    f.append(rect(b1_x + 25, b1_y + 140, 65, 40, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(b1_x + 57, b1_y + 164, "R_ref2", size=11, bold=True))
    f.append(rect(b1_x + 110, b1_y + 140, 65, 40, fill="#fdf2f8", stroke=PURPLE, sw=2, rx=4))
    f.append(text(b1_x + 142, b1_y + 164, "R_ntc (T)", size=11, bold=True, color=PURPLE))

    f.append(text(b1_x + b1_w / 2, b1_y + 215, "Баланс: V_err = 0 при 80.0 °C", size=10.5, bold=True, color=PURPLE))

    # Стрілка живлення мосту від Vref
    f.append(line(b1_x + b1_w / 2, b1_y - 20, b1_x + b1_w / 2, b1_y, color=POS, sw=2))
    f.append(text(b1_x + b1_w / 2, b1_y - 26, "V_ref (+5.000 V)", size=11, bold=True, color=POS))

    # Блок 2: Підсилювач помилки та PI-ланка
    b2_x, b2_y, b2_w, b2_h = 290, 110, 220, 240
    f.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#eff6ff", stroke=COLD, sw=2, rx=8))
    f.append(text(b2_x + b2_w / 2, b2_y + 24, "PI-регулятор (ОУ)", size=13, bold=True, color=COLD))
    f.append(text(b2_x + b2_w / 2, b2_y + 44, "Low-Drift Chopper Op-Amp", size=10.5, color=MUTED))

    f.append(rect(b2_x + 30, b2_y + 75, 160, 50, fill="#ffffff", stroke=COLD, sw=1.5, rx=4))
    f.append(text(b2_x + 110, b2_y + 96, "Пропорційна ланка (P)", size=11, bold=True))
    f.append(text(b2_x + 110, b2_y + 114, "K_p · ΔV_err (швидкість)", size=10, color=MUTED))

    f.append(rect(b2_x + 30, b2_y + 140, 160, 50, fill="#ffffff", stroke=COLD, sw=1.5, rx=4))
    f.append(text(b2_x + 110, b2_y + 161, "Інтегральна ланка (I)", size=11, bold=True))
    f.append(text(b2_x + 110, b2_y + 179, "K_i · ∫ ΔV_err dt (нуль стат. похибки)", size=9.5, color=MUTED))

    f.append(text(b2_x + b2_w / 2, b2_y + 215, "u(t) = K_p·e(t) + K_i·∫e dt", size=11, bold=True, color="#1e40af"))

    # Лінії зв'язку між мостом і ОУ
    f.append(arrow(b1_x + b1_w, b1_y + 90, b2_x, b2_y + 90, color=INK, sw=1.8))
    f.append(arrow(b1_x + b1_w, b1_y + 160, b2_x, b2_y + 160, color=INK, sw=1.8))
    f.append(text((b1_x + b1_w + b2_x) / 2, b1_y + 80, "V+", size=10.5, bold=True))
    f.append(text((b1_x + b1_w + b2_x) / 2, b1_y + 150, "V−", size=10.5, bold=True))

    # Блок 3: Лінійний силовий каскад нагрівача
    b3_x, b3_y, b3_w, b3_h = 560, 110, 180, 240
    f.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#fff7ed", stroke=POS, sw=2, rx=8))
    f.append(text(b3_x + b3_w / 2, b3_y + 24, "Лінійний драйвер", size=13, bold=True, color=POS))
    f.append(text(b3_x + b3_w / 2, b3_y + 44, "Power BJT / MOSFET", size=10.5, color=MUTED))

    f.append(rect(b3_x + 20, b3_y + 75, 140, 45, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    f.append(text(b3_x + 90, b3_y + 102, "I_heater = f(u)", size=11, bold=True))

    f.append(rect(b3_x + 20, b3_y + 135, 140, 70, fill="#ffffff", stroke=HEAT, sw=1.8, rx=4))
    f.append(text(b3_x + 90, b3_y + 158, "Нагрівач R_h", size=11.5, bold=True, color=HEAT))
    f.append(text(b3_x + 90, b3_y + 178, "P_h = I² · R_h", size=11, bold=True))
    f.append(text(b3_x + 90, b3_y + 195, "P = 1.0...8.0 Вт", size=10, color=MUTED))

    # Лінія зв'язку від PI до драйвера
    f.append(arrow(b2_x + b2_w, b2_y + 120, b3_x, b3_y + 120, color=INK, sw=1.8))
    f.append(text((b2_x + b2_w + b3_x) / 2, b2_y + 110, "u_ctrl", size=10.5, bold=True))

    # Блок 4: Тепловий об'єкт (Камера з кварцом)
    b4_x, b4_y, b4_w, b4_h = 790, 110, 150, 240
    f.append(rect(b4_x, b4_y, b4_w, b4_h, fill="#fef3c7", stroke=HEAT, sw=2.2, rx=8))
    f.append(text(b4_x + b4_w / 2, b4_y + 24, "Камера OCXO", size=13, bold=True, color=HEAT))
    f.append(text(b4_x + b4_w / 2, b4_y + 50, "C_th · dT/dt = P_in − P_loss", size=9.5, color=MUTED))

    f.append(rect(b4_x + 15, b4_y + 75, 120, 50, fill="#eff6ff", stroke=COLD, sw=1.5, rx=4))
    f.append(text(b4_x + 75, b4_y + 98, "Кварц SC", size=11, bold=True, color=COLD))
    f.append(text(b4_x + 75, b4_y + 115, "T = 80.0 °C", size=10.5, bold=True))

    f.append(rect(b4_x + 15, b4_y + 140, 120, 50, fill="#fdf2f8", stroke=PURPLE, sw=1.5, rx=4))
    f.append(text(b4_x + 75, b4_y + 163, "NTC сенсор", size=11, bold=True, color=PURPLE))
    f.append(text(b4_x + 75, b4_y + 180, "R(T) зворотний зв'язок", size=9, color=MUTED))

    # Лінія тепла від нагрівача до камери
    f.append(arrow(b3_x + b3_w, b3_y + 170, b4_x, b4_y + 170, color=POS, sw=2.2))
    f.append(text((b3_x + b3_w + b4_x) / 2, b3_y + 160, "Тепло Q̇", size=11, bold=True, color=POS))

    # Зворотний тепловий зв'язок: від NTC в камері до Мосту Уїтстона (знизу)
    fb_y = 390
    f.append(line(b4_x + 75, b4_y + b4_h, b4_x + 75, fb_y, color=PURPLE, sw=2))
    f.append(line(b4_x + 75, fb_y, b1_x + 142, fb_y, color=PURPLE, sw=2, dash="6 4"))
    f.append(arrow(b1_x + 142, fb_y, b1_x + 142, b1_y + b1_h, color=PURPLE, sw=2))
    f.append(text(W / 2, fb_y - 12, "Тепловий зворотний зв'язок: зміна температури змінює опір R_ntc, замикаючи петлю",
                  size=11.5, bold=True, color=PURPLE))

    # Нижня панель зауважень
    f.append(fitbox(40, 430, 900, 70,
                    "Чому заборонено ШІМ (PWM) у прецизійних OCXO:\n"
                    "1. Електромагнітна наводка (EMI) від фронтів перемикання потрапляє на чутливий контур генератора\n"
                    "2. Пульсації температури камери викликають періодичну паразитну фазову модуляцію (spurs у спектрі)\n"
                    "3. Лише суто лінійний режим вихідного каскаду гарантує граничну чистоту спектра та низький фазовий шум",
                    size=11, fill="#fef2f2", stroke=POS, color=INK))

    render(os.path.join(IMG, "pi-thermal-control-loop.svg"), W, H, *f)


# ── 4. Динаміка розігріву (Warm-up profile) ──────────────────────────────────────
def fig_warmup_profile():
    W, H = 960, 530
    f = [
        text(W / 2, 28, "Динаміка холодного старту: потужність, температура та вихід частоти", size=17, bold=True),
        text(W / 2, 50, "перехід від форсованого розігріву (5–8 Вт) до стаціонарного утримання (1–1.5 Вт) за 3–5 хвилин",
             size=12, color=MUTED, italic=True)
    ]

    L, R, T, B = 80, 620, 95, 430
    t_min, t_max = 0.0, 10.0       # Час у хвилинах

    def X(t):
        return L + (t - t_min) / (t_max - t_min) * (R - L)

    # Ліва вісь Y: Потужність нагрівача P (0..8 Вт)
    # Права вісь Y: Похибка частоти df/f (ppm, лог або шкала від +10 до -0.1)
    p_min, p_max = 0.0, 8.0

    def Y_p(p):
        return B - (p - p_min) / (p_max - p_min) * (B - T)

    # Осі
    f.append(line(L, T - 10, L, B, color=INK, sw=2))
    f.append(line(L, B, R + 10, B, color=INK, sw=2))
    f.append(line(R, T - 10, R, B, color=INK, sw=2))
    f.append(text(R + 10, B + 24, "Час від увімкнення (хвилини)", size=12.5, bold=True, anchor="end"))
    f.append(text(L - 10, T - 16, "Потужність P (Вт)", size=12, bold=True, color=POS, anchor="start"))
    f.append(text(R + 10, T - 16, "Температура камери T (°C)", size=12, bold=True, color=HEAT, anchor="end"))

    # Позначки по осі X
    for m in range(0, 11):
        x = X(m)
        f.append(line(x, B, x, B + 6, color=INK, sw=1.2))
        f.append(text(x, B + 20, str(m), size=10.5, color=MUTED))

    # Позначки лівої осі Y (Потужність)
    for p_val in (0, 2, 4, 6, 8):
        y = Y_p(p_val)
        f.append(line(L - 6, y, L, y, color=POS, sw=1.2))
        f.append(text(L - 10, y + 4, str(p_val), size=10.5, color=POS, anchor="end"))

    # Позначки правої осі Y (Температура 20..80 °C)
    for temp in (20, 40, 60, 80):
        # Temp scale 20..80 mapped to Y_p(0..8)
        norm_t = (temp - 20.0) / 60.0 * 8.0
        y = Y_p(norm_t)
        f.append(line(R, y, R + 6, y, color=HEAT, sw=1.2))
        f.append(text(R + 10, y + 4, "%d °C" % temp, size=10.5, color=HEAT, anchor="start"))

    # 1. Крива споживання потужності P(t)
    # Спочатку насичення P = 7.5 Вт протягом 1.5 хв, потім спад до P_hold = 1.3 Вт
    pts_p = []
    for step in range(121):
        t = t_min + (t_max - t_min) * step / 120.0
        if t < 1.8:
            p = 7.5
        else:
            p = 1.3 + (7.5 - 1.3) * math.exp(-(t - 1.8) / 0.8)
        pts_p.append((X(t), Y_p(p)))
    f.append(polyline(pts_p, POS, sw=3.2))

    # 2. Крива температури камери T_oven(t)
    # Зростає від 25 °C до 80 °C
    pts_t = []
    for step in range(121):
        t = t_min + (t_max - t_min) * step / 120.0
        if t < 2.5:
            temp = 25.0 + (80.0 - 25.0) * (1.0 - math.exp(-t / 1.1))
        else:
            temp = 80.0
        norm_t = (temp - 20.0) / 60.0 * 8.0
        pts_t.append((X(t), Y_p(norm_t)))
    f.append(polyline(pts_t, HEAT, sw=3.0, dash="6 4"))

    # Зона виходу на стабільний режим (3 хвилини)
    x_lock = X(3.0)
    f.append(line(x_lock, T, x_lock, B, color=FIELD, sw=1.8, dash="4 4"))
    f.append(text(x_lock + 8, T + 20, "Lock: вихід у ±0.01 ppm (3 хв)", size=11, bold=True, color=FIELD, anchor="start"))

    # Підписи фаз
    f.append(rect(X(0.2), Y_p(7.8), 170, 32, fill="#fff7ed", stroke=POS, sw=1.5, rx=4))
    f.append(text(X(0.2) + 85, Y_p(7.8) + 20, "Форсований нагрів (7.5 Вт)", size=10.5, bold=True, color=POS))

    f.append(rect(X(5.5), Y_p(2.5), 180, 32, fill="#fef3c7", stroke=HEAT, sw=1.5, rx=4))
    f.append(text(X(5.5) + 90, Y_p(2.5) + 20, "Утримання P_hold = 1.3 Вт", size=10.5, bold=True, color=HEAT))

    # Права панель з детальним описом часових фаз
    px, py, pw = 650, 95, 290
    f.append(fitbox(px, py, pw, 100,
                    "Фаза 1: Холодний старт (0–2 хв)\n"
                    "• Максимальний струм нагрівача (насичення драйвера)\n"
                    "• Струм живлення: до 600–800 мА при 12 В\n"
                    "• Швидке зростання температури: dT/dt ≈ 0.5 °C/с",
                    size=11, fill="#fff7ed", stroke=POS, color=INK))

    f.append(fitbox(px, py + 115, pw, 100,
                    "Фаза 2: Захоплення температури (2–4 хв)\n"
                    "• Наближення до T_turn = 80 °C, драйвер виходить з насичення\n"
                    "• Інтегратор усуває перерегулювання (без викиду тепла)\n"
                    "• Частота потрапляє у вікно ±0.01 ppm (±10 ppb)",
                    size=11, fill="#fef3c7", stroke=HEAT, color=INK))

    f.append(fitbox(px, py + 230, pw, 100,
                    "Фаза 3: Стаціонарний режим (>5 хв)\n"
                    "• Тепловий баланс: P_hold = (T_oven − T_amb) / R_th\n"
                    "• Струм спадає до 100–120 мА (1.2–1.4 Вт)\n"
                    "• Вихід на граничну стабільність 10⁻¹¹ – 10⁻¹²",
                    size=11, fill="#eff6ff", stroke=COLD, color=INK))

    render(os.path.join(IMG, "warmup-and-power-profile.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ocxo_structure()
    fig_turnover_curves()
    fig_pi_thermal_loop()
    fig_warmup_profile()
    print("OK: 4 SVG generated in img/")
