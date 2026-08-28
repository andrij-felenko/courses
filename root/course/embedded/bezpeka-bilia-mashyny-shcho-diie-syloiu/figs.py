# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Чотири колаборативні режими безпеки (ISO 10218 / ISO/TS 15066) ──
def fig_four_modes():
    W, H = 840, 480
    frags = []
    frags.append(text(W / 2, 28, "Чотири колаборативні режими безпеки за ISO 10218-1/2 та ISO/TS 15066",
                      size=15, bold=True))

    modes = [
        (
            "1. Моніторинг зупинки (SMS)",
            "Safety-Rated Monitored Stop",
            "• Привід під напругою (SOS)\n• Робот нерухомий у робочій зоні\n• Людина завантажує / знімає деталь\n• Вихід людини відновлює рух без рестарту",
            "#f0f4f8", NEG
        ),
        (
            "2. Ручне ведення (HG)",
            "Hand Guiding",
            "• Силомоментний датчик на фланці\n• 3-позиційний перемикач згоди\n• Швидкість обмежена безпечною (SLS)\n• Оператор безпосередньо спрямовує інструмент",
            "#fdf9e8", "#d98324"
        ),
        (
            "3. Швидкість і дистанція (SSM)",
            "Speed & Separation Monitoring",
            "• Лазерні сканери / 3D-камери безпеки\n• Безперервний розрахунок дистанції S(t)\n• Наближення людини -> плавне сповільнення\n• Перетин межі зупинки -> плавний Stop",
            "#eafaf1", FIELD
        ),
        (
            "4. Обмеження сили й енергії (PFL)",
            "Power & Force Limiting",
            "• Фізичний контакт дозволений під час руху\n• Обмеження кінетичної енергії й тиску\n• Пороги болю за ISO/TS 15066\n• Детекція колізій і миттєвий реверс / відскок",
            "#fdecea", POS
        ),
    ]

    bw, bh = 380, 185
    coords = [
        (30, 60),
        (430, 60),
        (30, 265),
        (430, 265),
    ]

    for i, (title_ua, title_en, desc, bg_col, stroke_col) in enumerate(modes):
        x, y = coords[i]
        frags.append(rect(x, y, bw, bh, fill=bg_col, stroke=stroke_col, sw=1.8))
        frags.append(text(x + bw / 2, y + 24, title_ua, size=13, bold=True, color=stroke_col))
        frags.append(text(x + bw / 2, y + 44, title_en, size=11, bold=False, italic=True, color=MUTED))
        frags.append(line(x + 15, y + 54, x + bw - 15, y + 54, color=stroke_col, sw=1.0, dash="3,3"))
        frags.append(fitbox(x + 12, y + 60, bw - 24, bh - 68, desc, size=11, fill="none", stroke="none"))

    render(os.path.join(OUT, 'four-cobot-safety-modes.svg'), W, H, *frags)


# ── Фігура 2: Динамічна захисна дистанція SSM (ISO 13855 / ISO/TS 15066) ──────
def fig_ssm_distance():
    W, H = 840, 430
    frags = []
    frags.append(text(W / 2, 28, "Динамічна захисна дистанція розділення (Speed & Separation Monitoring)",
                      size=15, bold=True))

    # Схема зон
    # Робот (зліва) -> Зона зупинки -> Зона гальмування -> Людина (справа)
    y_lane = 80
    h_lane = 120

    # Робочий простір робота
    frags.append(rect(30, y_lane, 140, h_lane, fill="#feebe8", stroke=POS, sw=1.8))
    frags.append(text(100, y_lane + 45, "Робот", size=14, bold=True, color=POS))
    frags.append(text(100, y_lane + 70, "v_r = швидкість", size=11, color=INK))
    frags.append(text(100, y_lane + 90, "Маса ланок M", size=11, color=MUTED))

    # Зона гальмування робота (S_r + S_s)
    frags.append(rect(170, y_lane, 180, h_lane, fill="#fef5e7", stroke="#d98324", sw=1.5))
    frags.append(text(260, y_lane + 45, "Зупинний шлях", size=12, bold=True, color="#d98324"))
    frags.append(text(260, y_lane + 70, "S_r + S_s", size=12, bold=True, color=INK))
    frags.append(text(260, y_lane + 95, "v_r·T_r + 0.5·a·T_s²", size=10, color=MUTED))

    # Зона допусків і проникнення (C + Z_d)
    frags.append(rect(350, y_lane, 160, h_lane, fill="#f0f4f8", stroke=NEG, sw=1.5))
    frags.append(text(430, y_lane + 45, "Запас безпеки", size=12, bold=True, color=NEG))
    frags.append(text(430, y_lane + 70, "C + Z_s + Z_r", size=12, bold=True, color=INK))
    frags.append(text(430, y_lane + 95, "Оптичні допуски", size=10, color=MUTED))

    # Зона руху людини під час реакції (S_h)
    frags.append(rect(510, y_lane, 180, h_lane, fill="#eafaf1", stroke=FIELD, sw=1.5))
    frags.append(text(600, y_lane + 45, "Хід людини", size=12, bold=True, color=FIELD))
    frags.append(text(600, y_lane + 70, "S_h = v_h·(T_r + T_s)", size=12, bold=True, color=INK))
    frags.append(text(600, y_lane + 95, "v_h ≈ 1.6...2.0 м/с", size=10, color=MUTED))

    # Людина (справа)
    frags.append(rect(690, y_lane, 120, h_lane, fill="#eafaf1", stroke=FIELD, sw=1.8))
    frags.append(text(750, y_lane + 45, "Оператор", size=14, bold=True, color=FIELD))
    frags.append(text(750, y_lane + 70, "Наближення", size=11, color=INK))
    frags.append(text(750, y_lane + 90, "до робота", size=11, color=MUTED))

    # Стрілка загальної захисної дистанції S
    y_dim = 230
    frags.append(line(170, y_dim, 690, y_dim, color=INK, sw=2.0))
    frags.append(arrow(430, y_dim, 170, y_dim, color=INK, sw=2.0))
    frags.append(arrow(430, y_dim, 690, y_dim, color=INK, sw=2.0))
    frags.append(line(170, y_lane + h_lane + 5, 170, y_dim + 15, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(line(690, y_lane + h_lane + 5, 690, y_dim + 15, color=MUTED, sw=1.0, dash="3,3"))

    frags.append(textbox(430, y_dim + 25, "Загальна мінімальна захисна відстань S(t)", size=12, bold=True, fill="#ffffff", stroke=INK)[0])

    # Нижній аналітичний блок
    frags.append(fitbox(30, 290, 780, 120,
                        "Рівняння ISO 13855 / ISO/TS 15066:\n"
                        "S = (v_h · T_r) + (v_h · T_s) + (v_r · T_r) + S_s(v_r, a_max) + C + Z_s + Z_r\n"
                        "• T_r — час циклу безпекового сканера та шини (типово 30–80 мс)\n"
                        "• T_s — час механічного гальмування приводами (залежить від інерції та поточної швидкості v_r)\n"
                        "• C — глибина проникнення руки оператора до перетину оптичного променя сканера",
                        size=11, fill="#f4f6f8", stroke=LINE, sw=1.4))

    render(os.path.join(OUT, 'ssm-protective-distance.svg'), W, H, *frags)


# ── Фігура 3: Функції безпечного руху сервоприводу (IEC 61800-5-2) ────────────
def fig_drive_safety():
    W, H = 840, 450
    frags = []
    frags.append(text(W / 2, 28, "Порівняння функцій безпечного руху: STO, SS1 та SS2 (IEC 61800-5-2)",
                      size=15, bold=True))

    # Три колонки: STO, SS1, SS2
    cols = [
        (
            "Safe Torque Off (STO)",
            "Миттєве зняття моменту",
            "• Апаратний розрив PWM затворів\n• Привід знеструмлений миттєво\n• Ротор рухається за інерцією (coasting)\n• На вертикальних осях ланка ПАДАЄ!\n• Категорія зупинки 0 (IEC 60204-1)",
            "#fdecea", POS
        ),
        (
            "Safe Stop 1 (SS1)",
            "Контрольоване гальмування + STO",
            "• Активне гальмування двигуном (рампа)\n• Контроль швидкості під час зупинки\n• Після v=0 або таймауту -> перехід у STO\n• Вмикання механічного гальма (SBC)\n• Категорія зупинки 1 (IEC 60204-1)",
            "#fef9e7", "#d98324"
        ),
        (
            "Safe Stop 2 / SOS",
            "Зупинка з утриманням позиції",
            "• Активне гальмування за рампою\n• Двигун залишається під струмом (SOS)\n• Замкнений контур тримає позицію x=const\n• Дозволяє миттєвий рестарт руху\n• Категорія зупинки 2 (IEC 60204-1)",
            "#eafaf1", FIELD
        ),
    ]

    bw = 245
    gap = 20
    x0 = 32
    y0 = 60
    bh = 220

    for i, (title_ua, subtitle, desc, bg_col, stroke_col) in enumerate(cols):
        x = x0 + i * (bw + gap)
        frags.append(rect(x, y0, bw, bh, fill=bg_col, stroke=stroke_col, sw=1.8))
        frags.append(text(x + bw / 2, y0 + 26, title_ua, size=13, bold=True, color=stroke_col))
        frags.append(text(x + bw / 2, y0 + 46, subtitle, size=10, bold=False, italic=True, color=MUTED))
        frags.append(line(x + 12, y0 + 56, x + bw - 12, y0 + 56, color=stroke_col, sw=1.0, dash="3,3"))
        frags.append(fitbox(x + 10, y0 + 64, bw - 20, bh - 74, desc, size=10.5, fill="none", stroke="none"))

    # Графіки поведінки швидкості знизу
    y_gr = 300
    h_gr = 120

    # STO графіка
    x_sto = x0
    frags.append(rect(x_sto, y_gr, bw, h_gr, fill="#ffffff", stroke=POS, sw=1.2))
    frags.append(text(x_sto + bw / 2, y_gr + 20, "Швидкість v(t) при STO", size=11, bold=True, color=POS))
    # некерований спад / коливання
    frags.append(line(x_sto + 20, y_gr + 45, x_sto + 70, y_gr + 45, color=POS, sw=2.0))
    frags.append(line(x_sto + 70, y_gr + 45, x_sto + 220, y_gr + 105, color=POS, sw=2.0, dash="4,4"))
    frags.append(text(x_sto + 80, y_gr + 65, "Тригер STO", size=9, color=POS, bold=True))
    frags.append(text(x_sto + 160, y_gr + 95, "Неконтрольований вибіг", size=9, color=MUTED))

    # SS1 графіка
    x_ss1 = x0 + bw + gap
    frags.append(rect(x_ss1, y_gr, bw, h_gr, fill="#ffffff", stroke="#d98324", sw=1.2))
    frags.append(text(x_ss1 + bw / 2, y_gr + 20, "Швидкість v(t) при SS1", size=11, bold=True, color="#d98324"))
    # керована рампа
    frags.append(line(x_ss1 + 20, y_gr + 45, x_ss1 + 70, y_gr + 45, color="#d98324", sw=2.0))
    frags.append(line(x_ss1 + 70, y_gr + 45, x_ss1 + 170, y_gr + 105, color="#d98324", sw=2.5))
    frags.append(line(x_ss1 + 170, y_gr + 105, x_ss1 + 225, y_gr + 105, color=POS, sw=2.0))
    frags.append(text(x_ss1 + 120, y_gr + 65, "Керована рампа", size=9, color="#d98324", bold=True))
    frags.append(text(x_ss1 + 195, y_gr + 95, "STO + SBC", size=9, color=POS, bold=True))

    # SS2 графіка
    x_ss2 = x0 + 2 * (bw + gap)
    frags.append(rect(x_ss2, y_gr, bw, h_gr, fill="#ffffff", stroke=FIELD, sw=1.2))
    frags.append(text(x_ss2 + bw / 2, y_gr + 20, "Швидкість v(t) при SS2 / SOS", size=11, bold=True, color=FIELD))
    # керована рампа + утримання нульової швидкості
    frags.append(line(x_ss2 + 20, y_gr + 45, x_ss2 + 70, y_gr + 45, color=FIELD, sw=2.0))
    frags.append(line(x_ss2 + 70, y_gr + 45, x_ss2 + 160, y_gr + 105, color=FIELD, sw=2.5))
    frags.append(line(x_ss2 + 160, y_gr + 105, x_ss2 + 225, y_gr + 105, color=FIELD, sw=2.5))
    frags.append(text(x_ss2 + 115, y_gr + 65, "Гальмування", size=9, color=FIELD, bold=True))
    frags.append(text(x_ss2 + 190, y_gr + 95, "SOS (v=0 під струмом)", size=9, color=FIELD, bold=True))

    render(os.path.join(OUT, 'drive-safety-functions-timing.svg'), W, H, *frags)


# ── Фігура 4: Двоканальна архітектура моніторингу безпеки та виявлення колізій ─
def fig_safety_architecture():
    W, H = 840, 480
    frags = []
    frags.append(text(W / 2, 28, "Двоканальна архітектура безпеки (Safety Watchdog & Collision Observer)",
                      size=15, bold=True))

    # Лівий блок: Сенсори та зворотний зв'язок (Двоканальні енкодери, датчики струму, сканер)
    frags.append(fitbox(25, 60, 180, 390,
                        "Сенсорний рівень\n(Двоканальний вхід)\n\n[ Канал A ]\n• Абсолютний енкодер осей\n• Датчики фазного струму I_u, I_v\n• 6-осьовий F/T датчик фланця\n\n[ Канал B ]\n• Інкрементний енкодер / sin-cos\n• Незалежні шунти струму\n\n[ Зовнішні сенсори ]\n• Safety LiDAR (OSSD1 / OSSD2)\n• Кнопка E-Stop (2xNC)",
                        size=11, fill="#f0f4f8", stroke=NEG, sw=1.6))

    # Центральний блок: Два незалежних обчислювальних ядра безпеки
    # Ядро 1 (Головний контролер траєкторії та спостерігач)
    frags.append(fitbox(235, 60, 260, 185,
                        "Основне ядро керування (MCU 1)\n(Trajectory & Momentum Observer)\n\n• Планувальник траєкторії q_cmd(t)\n• Модель динаміки: M(q), C(q,q̇), g(q)\n• Спостерігач імпульсу r(t) -> τ_ext\n• Детекція перевищення сили F_ext > F_max",
                        size=11, fill="#ffffff", stroke=LINE, sw=1.6))

    # Ядро 2 (Незалежний безпековий монітор / Safety Watchdog Core)
    frags.append(fitbox(235, 265, 260, 185,
                        "Безпековий співпроцесор (MCU 2)\n(Safety Watchdog & Geofencing)\n\n• Незалежний розрахунок прямої кінематики\n• Декартовий геофенсинг (3D Safety Zones)\n• Контроль швидкості ланок SLS (v < v_max)\n• Крос-контроль узгодженості (Cross-Check)",
                        size=11, fill="#fdf9e8", stroke="#d98324", sw=1.6))

    # Зв'язок між MCU 1 та MCU 2 (Крос-валідація)
    frags.append(arrow(340, 245, 340, 265, color="#d98324", sw=1.5))
    frags.append(arrow(390, 265, 390, 245, color="#d98324", sw=1.5))
    frags.append(rect(300, 240, 130, 30, fill="#ffffff", stroke="#d98324", sw=1.0))
    frags.append(text(365, 258, "Крос-обмін (SPI)", size=9, bold=True, color="#d98324"))

    # Правий блок: Силовий каскад та комутація STO
    frags.append(fitbox(525, 60, 290, 390,
                        "Виконавчий силовий вузол\n(Dual STO & Gate Drives)\n\n[ Канал керування STO 1 ]\n• Оптоізолятор драйвера верхнього плеча\n• Заборона тактування IGBT / GaN\n\n[ Канал керування STO 2 ]\n• Оптоізолятор драйвера нижнього плеча\n• Апаратне блокування ENABLE\n\n[ Безпекове реле гальма (SBC) ]\n• Розрив живлення котушок гальм осей\n• Примусове затискання при аварії\n\n─────► Знеструмлення серводвигунів\n─────► Активація фрикційних гальм",
                        size=11, fill="#feebe8", stroke=POS, sw=1.8))

    # Стрілки
    frags.append(arrow(205, 130, 235, 130, color=NEG, sw=1.5))
    frags.append(arrow(205, 340, 235, 340, color=NEG, sw=1.5))

    frags.append(arrow(495, 130, 525, 130, color=INK, sw=1.5))
    frags.append(arrow(495, 340, 525, 340, color=POS, sw=1.8))

    render(os.path.join(OUT, 'safety-watchdog-architecture.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_four_modes()
    fig_ssm_distance()
    fig_drive_safety()
    fig_safety_architecture()
    print("All figures generated successfully.")
