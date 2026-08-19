# -*- coding: utf-8 -*-
"""Фігури до статті «Комплементарна ШІМ і мертвий час» (book/electronics/power-electronics/complementary-pwm):
  - fig-shoot-through-mechanism.svg  — наскрізний струм при одночасному відкритті ключів стійки
  - fig-deadtime-generation.svg      — часові діаграми комплементарної ШІМ із затримкою наростання фронтів
  - fig-body-diode-conduction.svg    — замикання струму крізь body-діод у паузі та стрибок втрат
  - fig-mcu-timer-dtg.svg            — блок-схема апаратного генератора мертвого часу й входу Break
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Наскрізний струм (Shoot-Through) ───────────────────────────────────────
def fig_shoot_through():
    W, H = 840, 480
    f = [
        text(W / 2, 28, "Наскрізний струм (Shoot-Through): руйнівне замкнення шини живлення", size=15, bold=True),
    ]

    # Ліва панель: нормальна комутація (почергова)
    x_left = 40
    f.append(rect(x_left, 55, 360, 395, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(x_left + 180, 80, "Штатний режим: один ключ увімкнений", size=13, bold=True, color=FIELD))

    # Стійка ліворуч
    lx_bus = x_left + 70
    f.append(line(lx_bus, 105, lx_bus, 415, color="#d0d7de", sw=1.5))
    
    # Шини +Vbus та GND зліва
    f.append(line(lx_bus - 30, 105, lx_bus + 30, 105, color=POS, sw=2.5))
    f.append(text(lx_bus + 45, 109, "+V_bus", size=12, bold=True, color=POS, anchor="start"))
    
    f.append(line(lx_bus - 30, 415, lx_bus + 30, 415, color=NEG, sw=2.5))
    f.append(text(lx_bus + 45, 419, "GND (0 В)", size=12, bold=True, color=NEG, anchor="start"))

    # Верхній ключ Q_H (ON)
    f.append(rect(lx_bus - 25, 140, 50, 60, fill="#e8f8f0", stroke=FIELD, sw=2, rx=4))
    f.append(text(lx_bus, 166, "Q_H", size=12, bold=True, color=FIELD))
    f.append(text(lx_bus, 185, "ON (провідний)", size=10, color=FIELD))

    # Середній вузол SW
    f.append(circle(lx_bus, 260, 4, fill=INK))
    f.append(line(lx_bus, 260, lx_bus + 90, 260, color=INK, sw=2))
    f.append(text(lx_bus + 20, 252, "SW", size=11, bold=True))

    # Навантаження (дросель/мотор)
    f.append(rect(lx_bus + 90, 240, 80, 40, fill="#ffffff", stroke=INK, sw=1.5, rx=3))
    f.append(text(lx_bus + 130, 264, "Навантаження", size=11, bold=True))

    # Нижній ключ Q_L (OFF)
    f.append(rect(lx_bus - 25, 320, 50, 60, fill="#ffffff", stroke=MUTED, sw=1.5, rx=4))
    f.append(text(lx_bus, 346, "Q_L", size=12, bold=True, color=MUTED))
    f.append(text(lx_bus, 365, "OFF (закритий)", size=10, color=MUTED))

    # Стрілка корисного струму
    f.append('<path d="M %d,%d L %d,%d L %d,%d" stroke="%s" stroke-width="2.5" fill="none" stroke-dasharray="5,3"/>'
             % (lx_bus, 105, lx_bus, 260, lx_bus + 90, 260, FIELD))
    f.append(text(x_left + 230, 320, "Струм іде в навантаження", size=11, color=FIELD, bold=True))
    f.append(text(x_left + 230, 338, "I_вих = I_нав", size=10, color=INK))
    f.append(text(x_left + 230, 395, "Втрати: лише I² · R_ds(on)", size=11, color=FIELD))

    # Права панель: Аварія Shoot-Through
    x_right = 440
    f.append(rect(x_right, 55, 360, 395, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    f.append(text(x_right + 180, 80, "Аварія: перекриття сигналів керування", size=13, bold=True, color=POS))

    # Стійка праворуч
    rx_bus = x_right + 70
    f.append(line(rx_bus, 105, rx_bus, 415, color="#d0d7de", sw=1.5))

    # Шини +Vbus та GND праворуч
    f.append(line(rx_bus - 30, 105, rx_bus + 30, 105, color=POS, sw=2.5))
    f.append(text(rx_bus + 45, 109, "+V_bus", size=12, bold=True, color=POS, anchor="start"))
    
    f.append(line(rx_bus - 30, 415, rx_bus + 30, 415, color=NEG, sw=2.5))
    f.append(text(rx_bus + 45, 419, "GND (0 В)", size=12, bold=True, color=NEG, anchor="start"))

    # Верхній ключ Q_H (ON)
    f.append(rect(rx_bus - 25, 140, 50, 60, fill="#fdecea", stroke=POS, sw=2, rx=4))
    f.append(text(rx_bus, 166, "Q_H", size=12, bold=True, color=POS))
    f.append(text(rx_bus, 185, "ON (відкритий)", size=10, color=POS))

    # Середній вузол SW
    f.append(circle(rx_bus, 260, 4, fill=INK))
    f.append(line(rx_bus, 260, rx_bus + 90, 260, color=MUTED, sw=1.2))

    # Навантаження
    f.append(rect(rx_bus + 90, 240, 80, 40, fill="#ffffff", stroke=MUTED, sw=1.2, rx=3))
    f.append(text(rx_bus + 130, 264, "Навантаження", size=11, color=MUTED))

    # Нижній ключ Q_L (ЩЕ НЕ ЗАКРИВСЯ!)
    f.append(rect(rx_bus - 25, 320, 50, 60, fill="#fdecea", stroke=POS, sw=2, rx=4))
    f.append(text(rx_bus, 346, "Q_L", size=12, bold=True, color=POS))
    f.append(text(rx_bus, 365, "Ще провідний!", size=10, color=POS, bold=True))

    # Пряма стрілка короткого замикання (наскрізний струм)
    f.append('<path d="M %d,%d L %d,%d" stroke="%s" stroke-width="4" fill="none"/>'
             % (rx_bus, 105, rx_bus, 415, POS))
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s"/>'
             % (rx_bus, 418, rx_bus - 6, 404, rx_bus + 6, 404, POS))

    f.append(text(x_right + 235, 145, "Прямий наскрізний шлях", size=11, bold=True, color=POS))
    f.append(text(x_right + 235, 165, "I_пік = V_bus / (2·R_ds)", size=11, bold=True, color=POS))
    f.append(text(x_right + 235, 185, "Струм: сотні ампер!", size=11, color=POS))

    # Попереджувальна рамка про перегрів і вибух
    f.append(rect(x_right + 130, 315, 215, 85, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    f.append(text(x_right + 237, 336, "Наслідки наскрізного струму:", size=10, bold=True, color=POS))
    f.append(text(x_right + 237, 354, "• Миттєвий перегрів кристала", size=10, color=INK))
    f.append(text(x_right + 237, 370, "• Стрибок dV/dt та защіпка", size=10, color=INK))
    f.append(text(x_right + 237, 386, "• Тепловий пробій і вибух", size=10, color=POS, bold=True))

    render(os.path.join(IMG, 'fig-shoot-through-mechanism.svg'), W, H, *f)


# ── 2. Формування комплементарної ШІМ і мертвий час ──────────────────────────
def fig_deadtime_generation():
    W, H = 840, 480
    f = [
        text(W / 2, 28, "Формування комплементарної ШІМ та впровадження мертвого часу", size=15, bold=True),
    ]

    x0, x1 = 190, 800
    rows = [90, 175, 260, 345]
    hi = 36

    # Підписи осей ліворуч
    labels = [
        "Базовий ШІМ (Ref)",
        "Ідеальний PWM_L (NOT)",
        "Реальний PWM_H (з DT)",
        "Реальний PWM_L (з DT)"
    ]
    sublabels = [
        "Опорний сигнал таймера",
        "Проста логічна інверсія",
        "Затримка відкриття t_dead",
        "Затримка відкриття t_dead"
    ]

    for y, lab, sub in zip(rows, labels, sublabels):
        f.append(line(x0, y, x1, y, color="#e1e4e8", sw=1.0))
        f.append(text(x0 - 15, y - 14, lab, size=12, anchor="end", bold=True, color=INK))
        f.append(text(x0 - 15, y + 2, sub, size=10, anchor="end", color=MUTED))

    # Часові точки
    t1 = 260  # наростання Ref
    t2 = 500  # спадання Ref
    t3 = 740  # наступне наростання Ref

    dt = 45   # тривалість мертвого часу

    # Вертикальні допоміжні лінії перемикання
    for tx in [t1, t1 + dt, t2, t2 + dt, t3, t3 + dt]:
        f.append(line(tx, 60, tx, 400, color="#eceff1", sw=1.0, dash="3,3"))

    # Зони мертвого часу (підсвітка рожевим фоном)
    f.append(rect(t1, 60, dt, 340, fill="#fff0f0", stroke="none", sw=0))
    f.append(rect(t2, 60, dt, 340, fill="#fff0f0", stroke="none", sw=0))
    f.append(rect(t3, 60, dt, 340, fill="#fff0f0", stroke="none", sw=0))

    # Текстові підписи зон t_dead
    f.append(text(t1 + dt / 2, 54, "t_dead", size=11, bold=True, color=POS))
    f.append(text(t2 + dt / 2, 54, "t_dead", size=11, bold=True, color=POS))
    f.append(text(t3 + dt / 2, 54, "t_dead", size=11, bold=True, color=POS))

    # Доріжка 1: Базовий ШІМ (Ref)
    p1 = f"M {x0},{rows[0]} L {t1},{rows[0]} L {t1},{rows[0]-hi} L {t2},{rows[0]-hi} L {t2},{rows[0]} L {t3},{rows[0]} L {t3},{rows[0]-hi} L {x1},{rows[0]-hi}"
    f.append(f'<path d="{p1}" stroke="{INK}" stroke-width="2.2" fill="none"/>')

    # Доріжка 2: Ідеальний PWM_L (NOT PWM_H) - небезпечний через перекриття
    p2 = f"M {x0},{rows[1]-hi} L {t1},{rows[1]-hi} L {t1},{rows[1]} L {t2},{rows[1]} L {t2},{rows[1]-hi} L {t3},{rows[1]-hi} L {t3},{rows[1]} L {x1},{rows[1]}"
    f.append(f'<path d="{p2}" stroke="{MUTED}" stroke-width="2.0" stroke-dasharray="4,3" fill="none"/>')

    # Доріжка 3: Реальний PWM_H (Верхній ключ: спадання миттєве в t2, наростання затримане до t1+dt)
    p3 = f"M {x0},{rows[2]} L {t1+dt},{rows[2]} L {t1+dt},{rows[2]-hi} L {t2},{rows[2]-hi} L {t2},{rows[2]} L {t3+dt},{rows[2]} L {t3+dt},{rows[2]-hi} L {x1},{rows[2]-hi}"
    f.append(f'<path d="{p3}" stroke="{POS}" stroke-width="2.5" fill="none"/>')

    # Доріжка 4: Реальний PWM_L (Нижній ключ: спадання миттєве в t1, наростання затримане до t2+dt)
    p4 = f"M {x0},{rows[3]-hi} L {t1},{rows[3]-hi} L {t1},{rows[3]} L {t2+dt},{rows[3]} L {t2+dt},{rows[3]-hi} L {t3},{rows[3]-hi} L {t3},{rows[3]} L {x1},{rows[3]}"
    f.append(f'<path d="{p4}" stroke="{NEG}" stroke-width="2.5" fill="none"/>')

    # Нижня панель пояснення станів
    f.append(rect(40, 415, 760, 52, fill=FILL, stroke=LINE, sw=1.0, rx=5))
    f.append(text(140, 435, "Зона Q_L ON", size=11, bold=True, color=NEG))
    f.append(text(140, 452, "Нижній ключ замкнений", size=10, color=INK))

    f.append(text(380, 435, "Зона Q_H ON", size=11, bold=True, color=POS))
    f.append(text(380, 452, "Верхній ключ замкнений", size=10, color=INK))

    f.append(text(620, 435, "Зона Dead-Time: обидва OFF", size=11, bold=True, color=FIELD))
    f.append(text(620, 452, "Break-before-make: наскрізний шлях розімкнено", size=10, color=FIELD))

    render(os.path.join(IMG, 'fig-deadtime-generation.svg'), W, H, *f)


# ── 3. Комутація body-діода під час мертвого часу ──────────────────────────────
def fig_body_diode_conduction():
    W, H = 840, 460
    f = [
        text(W / 2, 28, "Комутація індуктивного струму в мертвий час та ціна задовгої паузи", size=15, bold=True),
    ]

    # Ліва схема: струм крізь body-діод
    x_sch = 40
    f.append(rect(x_sch, 55, 360, 385, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(x_sch + 180, 80, "Струм у мертвий час (обидва канали OFF)", size=12, bold=True, color=INK))

    cx = x_sch + 80
    # Шини живлення
    f.append(line(cx - 30, 105, cx + 30, 105, color=POS, sw=2.5))
    f.append(text(cx + 45, 109, "+V_bus", size=11, bold=True, color=POS, anchor="start"))

    f.append(line(cx - 30, 400, cx + 30, 400, color=NEG, sw=2.5))
    f.append(text(cx + 45, 404, "GND (0 В)", size=11, bold=True, color=NEG, anchor="start"))

    # Стійка
    f.append(line(cx, 105, cx, 400, color="#d0d7de", sw=1.5))

    # Верхній ключ (OFF)
    f.append(rect(cx - 20, 135, 40, 50, fill="#ffffff", stroke=MUTED, sw=1.5, rx=3))
    f.append(text(cx, 163, "Q_H OFF", size=10, color=MUTED))

    # Нижній ключ (Канал OFF, але Body-діод веде!)
    f.append(rect(cx - 20, 305, 40, 50, fill="#ffffff", stroke=MUTED, sw=1.5, rx=3))
    f.append(text(cx, 333, "Канал OFF", size=9, color=MUTED))

    # Паралельний вбудований body-діод нижнього ключа
    dx = cx + 55
    f.append(line(cx, 280, dx, 280, color=POS, sw=2))
    f.append(line(dx, 280, dx, 380, color=POS, sw=2))
    f.append(line(dx, 380, cx, 380, color=POS, sw=2))

    # Символ діода (анод знизу до GND, катод зверху до SW)
    f.append(rect(dx - 18, 310, 36, 40, fill="#fdecea", stroke=POS, sw=1.5, rx=3))
    f.append(text(dx, 327, "Body", size=10, bold=True, color=POS))
    f.append(text(dx, 342, "діод", size=10, bold=True, color=POS))

    # Вузол SW
    f.append(circle(cx, 250, 4, fill=INK))
    f.append(line(cx, 250, cx + 160, 250, color=INK, sw=2.5))
    f.append(text(cx + 15, 242, "Вузол SW", size=11, bold=True))

    # Індуктивність навантаження
    f.append(rect(cx + 160, 230, 85, 40, fill="#ffffff", stroke=INK, sw=1.5, rx=3))
    f.append(text(cx + 202, 254, "Дросель L", size=11, bold=True))

    # Стрілка струму самоіндукції, що тягне з землі крізь діод
    f.append(text(x_sch + 245, 125, "I_L не може перерватися!", size=11, bold=True, color=POS))
    f.append(text(x_sch + 245, 145, "Струм відкриває", size=10, color=INK))
    f.append(text(x_sch + 245, 160, "body-діод нижнього ключа", size=10, color=INK))

    f.append(rect(x_sch + 155, 335, 195, 90, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    f.append(text(x_sch + 252, 355, "Падіння напруги на SW:", size=10, bold=True, color=POS))
    f.append(text(x_sch + 252, 373, "• Канал ON: V = I·R_ds ≈ 0.05 В", size=10, color=FIELD))
    f.append(text(x_sch + 252, 391, "• Діод ON: V = -V_F ≈ -0.8..-1.2 В", size=10, color=POS, bold=True))
    f.append(text(x_sch + 252, 409, "Втрати зростають у 15-20 разів!", size=9, color=POS))

    # Права панель: графіки напруги на вузлі SW та миттєвих втрат
    x_gr = 430
    f.append(rect(x_gr, 55, 370, 385, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    f.append(text(x_gr + 185, 80, "Осцилограма вузла SW та втрати провідності", size=12, bold=True, color=INK))

    gx0, gx1 = x_gr + 50, x_gr + 340
    gy_sw = 170
    gy_p = 330

    # Вісь SW
    f.append(line(gx0, gy_sw, gx1, gy_sw, color="#d0d7de", sw=1.0))
    f.append(text(gx0 - 10, gy_sw - 35, "+V_bus", size=10, color=POS, anchor="end"))
    f.append(text(gx0 - 10, gy_sw + 4, "0 В", size=10, color=INK, anchor="end"))
    f.append(text(gx0 - 10, gy_sw + 25, "-V_F", size=10, color=POS, anchor="end", bold=True))

    # Часові інтервали на графіку
    gt1, gt2, gt3 = gx0 + 70, gx0 + 130, gx0 + 240
    f.append(rect(gt1, 105, gt2 - gt1, 290, fill="#fff0f0", stroke="none", sw=0))
    f.append(text(gt1 + (gt2 - gt1) / 2, 100, "t_dead", size=10, bold=True, color=POS))

    # Графік V_SW
    p_sw = f"M {gx0},{gy_sw-40} L {gt1},{gy_sw-40} L {gt1},{gy_sw+20} L {gt2},{gy_sw+20} L {gt2},{gy_sw-3} L {gt3},{gy_sw-3} L {gt3},{gy_sw-40} L {gx1},{gy_sw-40}"
    f.append(f'<path d="{p_sw}" stroke="{INK}" stroke-width="2.5" fill="none"/>')
    f.append(text(gx1, gy_sw - 48, "V_SW(t)", size=11, bold=True, anchor="end"))

    # Вісь миттєвої потужності P_loss
    f.append(line(gx0, gy_p, gx1, gy_p, color="#d0d7de", sw=1.0))
    f.append(text(gx0 - 10, gy_p - 40, "P_діод", size=10, color=POS, anchor="end", bold=True))
    f.append(text(gx0 - 10, gy_p - 5, "P_канал", size=10, color=FIELD, anchor="end"))
    f.append(text(gx0 - 10, gy_p + 15, "0 Вт", size=10, color=INK, anchor="end"))

    # Графік втрат: під час t_dead сплеск P_діод = V_F * I_L
    p_loss = f"M {gx0},{gy_p-5} L {gt1},{gy_p-5} L {gt1},{gy_p-45} L {gt2},{gy_p-45} L {gt2},{gy_p-5} L {gt3},{gy_p-5} L {gt3},{gy_p-5} L {gx1},{gy_p-5}"
    f.append(f'<path d="{p_loss}" stroke="{POS}" stroke-width="2.2" fill="none"/>')
    f.append(text(gx1, gy_p - 52, "P_втрат(t)", size=11, bold=True, color=POS, anchor="end"))

    # Пояснення
    f.append(text(x_gr + 185, 410, "Задовгий t_dead = перевитрата енергії та перегрів ключів", size=11, bold=True, color=POS))
    f.append(text(x_gr + 185, 428, "P_втрат_діод = f_sw · (t_dead1 + t_dead2) · V_F · I_L", size=10, color=INK))

    render(os.path.join(IMG, 'fig-body-diode-conduction.svg'), W, H, *f)


# ── 4. Апаратний генератор мертвого часу (MCU Timer DTG & Break) ──────────────
def fig_mcu_timer_dtg():
    W, H = 840, 500
    f = [
        text(W / 2, 26, "Апаратний генератор комплементарної ШІМ і захист Break (STM32 TIM1/TIM8)", size=15, bold=True),
    ]

    # Великий блок таймера
    bx, by, bw, bh = 40, 48, 760, 430
    f.append(rect(bx, by, bw, bh, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(bx + 20, by + 24, "Розширений таймер керування (Advanced Control Timer)", size=13, bold=True, color=INK, anchor="start"))

    # 1. Лічильник і компаратор
    f.append(rect(bx + 25, by + 45, 135, 170, fill="#ffffff", stroke=INK, sw=1.2, rx=4))
    f.append(text(bx + 92, by + 75, "Лічильник CNT", size=11, bold=True))
    f.append(text(bx + 92, by + 95, "та компаратор", size=10, color=MUTED))
    f.append(text(bx + 92, by + 120, "CCR1", size=12, bold=True, color=POS))
    f.append(text(bx + 92, by + 140, "(Duty Cycle)", size=10, color=MUTED))
    f.append(text(bx + 92, by + 175, "Базовий ШІМ", size=10, bold=True, color=FIELD))

    # Стрілка від CNT/CCR до комплементарного розгалужувача
    f.append(line(bx + 160, by + 130, bx + 200, by + 130, color=INK, sw=2.0))

    # 2. Розгалужувач на комплементарні канали
    f.append(rect(bx + 200, by + 45, 125, 170, fill="#ffffff", stroke=INK, sw=1.2, rx=4))
    f.append(text(bx + 262, by + 72, "Формування", size=11, bold=True))
    f.append(text(bx + 262, by + 90, "пари каналів", size=11, bold=True))
    f.append(text(bx + 262, by + 120, "OC1 (прямий)", size=10, color=FIELD, bold=True))
    f.append(text(bx + 262, by + 175, "OC1N (інверсний)", size=10, color=NEG, bold=True))

    # З'єднання між розгалужувачем і DTG
    f.append(line(bx + 325, by + 115, bx + 365, by + 115, color=FIELD, sw=2))
    f.append(line(bx + 325, by + 175, bx + 365, by + 175, color=NEG, sw=2))

    # 3. Блок мертвого часу (DTG)
    f.append(rect(bx + 365, by + 45, 175, 170, fill="#fff5f5", stroke=POS, sw=1.8, rx=5))
    f.append(text(bx + 452, by + 72, "Dead-Time Generator", size=11, bold=True, color=POS))
    f.append(text(bx + 452, by + 90, "(DTG лічильник)", size=10, bold=True, color=POS))
    f.append(text(bx + 452, by + 118, "Затримка наростання CH1", size=9, color=INK))
    f.append(text(bx + 452, by + 132, "Спадання миттєве", size=9, color=MUTED))
    f.append(text(bx + 452, by + 168, "Затримка наростання CH1N", size=9, color=INK))
    f.append(text(bx + 452, by + 182, "Спадання миттєве", size=9, color=MUTED))
    f.append(text(bx + 452, by + 202, "Регістр BDTR.DTG[7:0]", size=10, bold=True, color=POS))

    # З'єднання від DTG до Break Logic
    f.append(line(bx + 540, by + 115, bx + 580, by + 115, color=POS, sw=2))
    f.append(line(bx + 540, by + 175, bx + 580, by + 175, color=NEG, sw=2))

    # 4. Блок захисту Break & MOE
    f.append(rect(bx + 580, by + 45, 145, 170, fill="#ffffff", stroke=INK, sw=1.2, rx=4))
    f.append(text(bx + 652, by + 72, "Логіка Break & MOE", size=11, bold=True, color=POS))
    f.append(text(bx + 652, by + 90, "Головний дозвіл", size=10, color=MUTED))
    f.append(text(bx + 652, by + 120, "Аварійне зняття", size=10, color=POS))
    f.append(text(bx + 652, by + 136, "дозволу виходів", size=10, color=POS))
    f.append(text(bx + 652, by + 175, "Idle State (OIS1/OIS1N)", size=9, color=INK))
    f.append(text(bx + 652, by + 195, "Безпечний стан пінів", size=9, color=MUTED))

    # Вихідні піни праворуч
    f.append(line(bx + 725, by + 115, bx + 750, by + 115, color=POS, sw=2.5))
    f.append(circle(bx + 750, by + 115, 3, fill=POS))
    f.append(text(bx + 745, by + 102, "CH1", size=10, bold=True, color=POS, anchor="end"))

    f.append(line(bx + 725, by + 175, bx + 750, by + 175, color=NEG, sw=2.5))
    f.append(circle(bx + 750, by + 175, 3, fill=NEG))
    f.append(text(bx + 745, by + 195, "CH1N", size=10, bold=True, color=NEG, anchor="end"))

    # Вхідний пін BKIN (Break In) знизу
    f.append(rect(bx + 25, by + 260, 245, 145, fill="#fff0f0", stroke=POS, sw=1.5, rx=5))
    f.append(text(bx + 147, by + 288, "Аварійний вхід BKIN", size=12, bold=True, color=POS))
    f.append(text(bx + 147, by + 312, "Датчик струму / Компаратор / Драйвер", size=9, color=INK))
    f.append(text(bx + 147, by + 334, "Апаратний захист від КЗ та аварій", size=10, bold=True, color=POS))
    f.append(text(bx + 147, by + 355, "Миттєве спрацювання ( < 25 нс )", size=10, color=POS))
    f.append(text(bx + 147, by + 380, "Асинхронний апаратний перерив", size=9, color=MUTED))

    # Лінія від BKIN до Break Logic в обхід CPU
    f.append('<path d="M %d,%d L %d,%d L %d,%d" stroke="%s" stroke-width="2.5" fill="none" stroke-dasharray="5,3"/>'
             % (bx + 270, by + 332, bx + 652, by + 332, bx + 652, by + 215, POS))
    f.append(text(bx + 460, by + 322, "Апаратне скидання MOE в обхід ядра CPU!", size=10, bold=True, color=POS))

    # Реєстр конфігурації мертвого часу
    f.append(rect(bx + 300, by + 348, 425, 68, fill="#ffffff", stroke=MUTED, sw=1.0, rx=4))
    f.append(text(bx + 512, by + 368, "Формула обчислення DTG у регістрі TIMx_BDTR:", size=10, bold=True, color=INK))
    f.append(text(bx + 512, by + 386, "DTG[7]=0 => t_dead = DTG[6:0] · T_dts  (діапазон 0 .. 127 тактів)", size=9, color=FIELD))
    f.append(text(bx + 512, by + 402, "DTG[7:6]=10 => t_dead = (64 + DTG[5:0]) · 2 · T_dts  (128 .. 254 тактів)", size=9, color=INK))

    render(os.path.join(IMG, 'fig-mcu-timer-dtg.svg'), W, H, *f)


def main():
    fig_shoot_through()
    fig_deadtime_generation()
    fig_body_diode_conduction()
    fig_mcu_timer_dtg()
    print("Всі фігури згенеровано успішно.")


if __name__ == '__main__':
    main()
