# -*- coding: utf-8 -*-
"""Фігури до теми «Коротке замикання пакета: струм, дуга, що згорить першим»."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def path_elem(d, stroke=LINE, sw=1.5, fill="none", dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{sw:.1f}" fill="{fill}"{d_attr}/>'


def polyline_elem(pts, stroke=LINE, sw=1.5, fill="none", dash=None):
    p_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<polyline points="{p_str}" stroke="{stroke}" stroke-width="{sw:.1f}" fill="{fill}"{d_attr}/>'


# ── 1. Динаміка струму та напруги при короткому замиканні ───────────────────
def fig_sc_dynamics():
    W, H = 840, 420
    frags = []

    frags.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    x0, y0 = 90, 340
    xw, yh = 420, 260

    frags.append(line(x0, y0, x0 + xw, y0, color=LINE, sw=1.5))
    frags.append(line(x0, y0, x0, y0 - yh, color=LINE, sw=1.5))
    frags.append(text(x0 + xw + 10, y0 + 4, "Час t (мкс)", size=11, color=INK, anchor="start", bold=True))
    frags.append(text(x0 - 10, y0 - yh - 10, "Струм I / Напруга V", size=11, color=INK, anchor="start", bold=True))

    for t_val, lab in [(0, "0"), (20, "20"), (40, "40"), (60, "60"), (80, "80"), (100, "100")]:
        px = x0 + t_val * (xw / 100)
        frags.append(line(px, y0, px, y0 + 5, color=MUTED, sw=1))
        frags.append(text(px, y0 + 18, lab, size=10, color=MUTED, anchor="middle"))

    frags.append(line(x0 - 5, y0 - 180, x0, y0 - 180, color=MUTED, sw=1))
    frags.append(text(x0 - 10, y0 - 176, "I_sc (пік)", size=10, color=POS, anchor="end", bold=True))
    frags.append(line(x0 - 5, y0 - 120, x0, y0 - 120, color=MUTED, sw=1))
    frags.append(text(x0 - 10, y0 - 116, "V_bat (ном)", size=10, color=NEG, anchor="end"))

    i_pts = [
        (x0, y0),
        (x0 + 30, y0 - 100),
        (x0 + 63, y0 - 180),
        (x0 + 105, y0 - 180),
        (x0 + 130, y0 - 80),
        (x0 + 150, y0),
        (x0 + xw, y0)
    ]
    path_i = "M " + " L ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in i_pts)
    frags.append(path_elem(path_i, stroke=POS, sw=2.8, fill="none"))

    v_pts = [
        (x0, y0 - 120),
        (x0 + 10, y0 - 10),
        (x0 + 105, y0 - 10),
        (x0 + 115, y0 - 240),
        (x0 + 135, y0 - 130),
        (x0 + 170, y0 - 120),
        (x0 + xw, y0 - 120)
    ]
    path_v = "M " + " L ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in v_pts)
    frags.append(path_elem(path_v, stroke=NEG, sw=2.2, fill="none", dash="5,3"))

    frags.append(circle(x0 + 115, y0 - 240, 4, fill=NEG, stroke=NEG, sw=0))
    frags.append(text(x0 + 125, y0 - 242, "Індуктивний викид V_ds = L · |di/dt|", size=10, color=NEG, anchor="start", bold=True))

    frags.append(line(x0 + 105, y0, x0 + 105, y0 - 250, color=FIELD, sw=1.2, dash="3,3"))
    frags.append(text(x0 + 105, y0 - 255, "BMS SCP (~25 мкс)", size=9, color=FIELD, anchor="middle", bold=True))

    rx, rw = 540, 275
    frags.append(fitbox(rx, 40, rw, 75,
                        "1. ФАЗА НАРОСТАННЯ (0–15 мкс)\n"
                        "di/dt = U_bat / L_петлі\n"
                        "Струм зростає зі швидкістю 100–300 А/мкс,\n"
                        "обмежуючись паразитною індуктивністю.",
                        size=9, pad=6, fill="#fdf2e9", stroke="#e67e22", sw=1.2))

    frags.append(fitbox(rx, 125, rw, 75,
                        "2. ПІК СТРУМУ КЗ (15–25 мкс)\n"
                        "I_max = U_ocv / R_петлі\n"
                        "Сягає 1000–8000 А залежно від опору\n"
                        "комірок, шин, ключів BMS та шунта.",
                        size=9, pad=6, fill="#fdecea", stroke=POS, sw=1.2))

    frags.append(fitbox(rx, 210, rw, 85,
                        "3. АПАРАТНА ВІДСІЧКА BMS\n"
                        "Швидкісний компаратор (<20–50 мкс)\n"
                        "розряджає затвори MOSFET.\n"
                        "Різке переривання струму породжує\n"
                        "високовольтний викид на стоку.",
                        size=9, pad=6, fill="#eafaf0", stroke=FIELD, sw=1.2))

    frags.append(fitbox(rx, 305, rw, 65,
                        "4. ЗАХИСТ ВІД ПРОБОЮ\n"
                        "TVS-супресори та RC-демпфери\n"
                        "поглинають енергію L·I²/2, рятуючи\n"
                        "ключі від лавинного пробою.",
                        size=9, pad=6, fill="#eaf0fd", stroke=NEG, sw=1.2))

    render(os.path.join(IMG, 'sc-current-dynamics.svg'), W, H, *frags,
           title="Динаміка наростання струму КЗ та індуктивного сплеску напруги")


# ── 2. Ієрархія руйнування компонентів («Естафета руйнування») ──────────────
def fig_destruction_ladder():
    W, H = 820, 390
    frags = []
    frags.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    frags.append(text(W / 2, 25, "Ієрархія швидкості та стійкості до руйнування при аварійному КЗ", size=13, color=INK, anchor="middle", bold=True))

    steps = [
        ("1. Кристал MOSFET (BMS)", "10 – 50 мкс", "I²t ≈ 50 – 300 А²·с",
         "Маса кремнію — частки міліграма. При затримці вимкнення заходить у лінійний режим, "
         "миттєва потужність >50 кВт випаровує перехід, спікаючи стік-витік у монолітне КЗ.",
         "#fdecea", POS),
        ("2. Доріжки плати (PCB Traces)", "0.5 – 5 мс", "I²t ≈ 500 – 2500 А²·с",
         "Тонка мідь (35–70 мкм) за формулою Ондердонка миттєво плавиться, відшаровується "
         "від діелектрика FR-4 і вибухає спалахом металевої пари.",
         "#fdf2e9", "#e67e22"),
        ("3. Плавкий DC-запобіжник", "0.5 – 3 мс", "I²t_fuse < I²t_провідника",
         "Срібна калібрована вставка плавиться в кварцовому піску, гасячи дугу та розриваючи "
         "коло ДО термічного руйнування кабелів і шин.",
         "#eafaf0", FIELD),
        ("4. Міжкоміркові нікелеві шини", "100 – 500 мс", "I²t > 10 000 А²·с",
         "Високий питомий опір нікелю призводить до розжарення до 1000 °C. Плавить ізоляцію "
         "комірок і пластикові тримачі, провокуючи каскадне коротке замикання.",
         "#f3e5f5", "#8e44ad"),
        ("5. Акумуляторні комірки (Li-ion)", "1 – 10 с", "Тепловий розгін",
         "Масивний хімічний нагрів від внутрішнього опору R_cell. Спрацьовує струмовий розмикач CID, "
         "скидається мембрана тиску (venting), виникає незворотний тепловий розгін.",
         "#f5f5f5", INK),
    ]

    y = 50
    for title, time_str, i2t_str, desc, bg_col, border_col in steps:
        frags.append(rect(40, y, 740, 58, fill=bg_col, stroke=border_col, sw=1.3, rx=4))
        frags.append(text(55, y + 22, title, size=11, color=border_col, anchor="start", bold=True))
        frags.append(text(300, y + 22, f"Час: {time_str}", size=10, color=INK, anchor="start", bold=True))
        frags.append(text(460, y + 22, f"Межа: {i2t_str}", size=10, color=MUTED, anchor="start"))
        frags.append(text(55, y + 44, desc, size=9, color=INK, anchor="start"))
        y += 66

    render(os.path.join(IMG, 'component-destruction-ladder.svg'), W, H, *frags,
           title="Ієрархія теплової стійкості елементів кола короткого замикання")


# ── 3. Фізика дуги постійного струму та гасіння в піску ─────────────────────
def fig_dc_arc():
    W, H = 840, 390
    frags = []
    frags.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Ліва панель
    frags.append(fitbox(40, 35, 360, 40, "Змінний струм (AC) vs Постійний струм (DC)", size=11, pad=6, fill="#f4f6f8", stroke=LINE, sw=1.2, bold=True))

    frags.append(rect(40, 85, 360, 270, fill="#fafafa", stroke=LINE, sw=1, rx=4))
    frags.append(text(60, 110, "Змінний струм (AC):", size=10, color=FIELD, anchor="start", bold=True))
    frags.append(text(60, 128, "• Переходить через нуль кожні 10 мс (при 50 Гц).", size=9, color=INK, anchor="start"))
    frags.append(text(60, 144, "• У момент нульового струму дуга згасає,", size=9, color=INK, anchor="start"))
    frags.append(text(60, 160, "  даючи плазмі час на деіонізацію.", size=9, color=INK, anchor="start"))

    frags.append(text(60, 195, "Постійний струм (DC):", size=10, color=POS, anchor="start", bold=True))
    frags.append(text(60, 213, "• Нульових переходів НЕМАЄ — струм безперервний.", size=9, color=INK, anchor="start"))
    frags.append(text(60, 229, "• Термоелектронна емісія розжарених електродів", size=9, color=INK, anchor="start"))
    frags.append(text(60, 245, "  постійно підтримує плазмовий канал 3000–6000 °C.", size=9, color=INK, anchor="start"))
    frags.append(text(60, 261, "• Падіння на дузі U_arc ≈ 15–30 В.", size=9, color=INK, anchor="start"))
    frags.append(text(60, 277, "  Якщо U_пакета > U_arc — дуга горить стабільно,", size=9, color=POS, anchor="start", bold=True))
    frags.append(text(60, 293, "  розплавляючи метал і підпалюючи корпус.", size=9, color=POS, anchor="start"))
    frags.append(text(60, 325, "Звичайні AC-автомати на DC ПЕРЕТВОРЮЮТЬСЯ НА ПЛАЗМОРІЗ!", size=9, color=POS, anchor="start", bold=True))

    # Права панель
    frags.append(fitbox(430, 35, 370, 40, "Механізм гасіння в піску DC-запобіжника", size=11, pad=6, fill="#f4f6f8", stroke=LINE, sw=1.2, bold=True))

    frags.append(rect(430, 85, 370, 270, fill="#fafafa", stroke=LINE, sw=1, rx=4))

    # Спрощена схема внутрішньої частини запобіжника
    frags.append(rect(460, 105, 310, 85, fill="#fdfefe", stroke=LINE, sw=1.5, rx=3))
    frags.append(text(615, 122, "Керамічний корпус високої міцності (корунд / стеатит)", size=9, color=MUTED, anchor="middle"))

    # Пісок
    frags.append(rect(470, 130, 290, 50, fill="#fff9c4", stroke="none"))
    frags.append(text(615, 145, "Дрібнодисперсний кварцовий пісок (SiO₂)", size=9, color="#b7950b", anchor="middle", bold=True))

    # Плавкий елемент зі звуженнями
    frags.append(line(470, 160, 540, 160, color=LINE, sw=4))
    frags.append(line(540, 160, 560, 160, color=POS, sw=1.5))
    frags.append(line(560, 160, 670, 160, color=LINE, sw=4))
    frags.append(line(670, 160, 690, 160, color=POS, sw=1.5))
    frags.append(line(690, 160, 760, 160, color=LINE, sw=4))
    frags.append(text(615, 172, "Срібна смуга з перешийками (калібровані точки розриву)", size=9, color=INK, anchor="middle"))

    frags.append(text(450, 215, "Фази спрацьовування DC-запобіжника:", size=10, color=FIELD, anchor="start", bold=True))
    frags.append(text(450, 235, "1. Струм КЗ розплавляє перешийки за <0.5 мс.", size=9, color=INK, anchor="start"))
    frags.append(text(450, 255, "2. Спалахує дуга, миттєво плавлячи кварцовий пісок (SiO₂ >1700 °C).", size=9, color=INK, anchor="start"))
    frags.append(text(450, 275, "3. Пісок поглинає колосальне тепло і спікається у скляну", size=9, color=INK, anchor="start"))
    frags.append(text(450, 293, "   непровідну трубку — фульгурит, стискаючи й охолоджуючи плазму.", size=9, color=INK, anchor="start"))
    frags.append(text(450, 318, "4. Напруга дуги різко зростає вище напруги пакета → дуга гасне.", size=9, color=FIELD, anchor="start", bold=True))

    render(os.path.join(IMG, 'dc-arc-mechanism.svg'), W, H, *frags,
           title="Фізика дуги постійного струму та механізм дугогасіння кварцовим піском")


# ── 4. Селективність та три рівні захисту від КЗ ─────────────────────────────
def fig_coordination():
    W, H = 840, 380
    frags = []
    frags.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    frags.append(text(W / 2, 25, "Три рівні оборони батарейного пакета: координація часу та енергії", size=13, color=INK, anchor="middle", bold=True))

    tiers = [
        ("РІВЕНЬ 1: Напівпровідниковий захист BMS",
         "Апаратний компаратор SCP (<20–50 мкс)",
         "• Розриває коло закриттям MOSFET.\n"
         "• Відновлюваний: після зняття КЗ пакет повертається до роботи.\n"
         "• Обмеження: ключі можуть пробитися при L·di/dt викиді або тепловому ударі.",
         "#eafaf0", FIELD, 40, 55),
        ("РІВЕНЬ 2: Плавкий піщаний DC-запобіжник",
         "Спеціалізований DC Fuse (0.5–2 мс)",
         "• Одноразовий фізичний розрив кола при відмові/пробої ключів BMS.\n"
         "• Піщаний наповнювач гарантовано гасить кілоамперну DC дугу.\n"
         "• Номінальна відключаюча здатність (AIC) >20–50 кА.",
         "#fdf2e9", "#e67e22", 40, 160),
        ("РІВЕНЬ 3: Піропатрон (Pyro-fuse / Squib)",
         "Піротехнічний розмикач (1–3 мс)",
         "• Застосовується в EV та високовольтних системах (>100–800 В).\n"
         "• Мікровибух перерубує мідну шину поршнем за сигналом краш-датчика або BMS.\n"
         "• Створює фізичний ізоляційний проміжок у кілька сантиметрів.",
         "#fdecea", POS, 40, 265)
    ]

    for title, sub, desc, bg, stroke_c, x, y in tiers:
        frags.append(rect(x, y, 760, 95, fill=bg, stroke=stroke_c, sw=1.3, rx=4))
        frags.append(text(x + 15, y + 22, title, size=11, color=stroke_c, anchor="start", bold=True))
        frags.append(text(x + 500, y + 22, sub, size=10, color=INK, anchor="start", bold=True))

        lines = desc.split("\n")
        ly = y + 42
        for l in lines:
            frags.append(text(x + 15, ly, l, size=9, color=INK, anchor="start"))
            ly += 17

    render(os.path.join(IMG, 'protection-coordination.svg'), W, H, *frags,
           title="Трирівнева координація захисту від короткого замикання")


if __name__ == '__main__':
    fig_sc_dynamics()
    fig_destruction_ladder()
    fig_dc_arc()
    fig_coordination()
    print("All figures generated successfully.")
