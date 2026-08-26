# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. nyquist-vs-control-bandwidth: смуга сигналу проти смуги регулювання ──────
def fig_nyquist_vs_control():
    path = os.path.join(OUT, "nyquist-vs-control-bandwidth.svg")
    W, H = 880, 430
    p = []

    # Заголовок зверху
    p.append(text(W / 2, 28, "Смуга системи та вибір частоти тактування контуру", size=15, color=INK, bold=True))

    # Вісь частот
    x0, y0, w_axis = 60, 350, 760
    p.append(arrow(x0, y0, x0 + w_axis, y0, color=INK, sw=2.0))
    p.append(text(x0 + w_axis - 10, y0 + 26, "Частота f (лог. шкала) →", size=12, color=MUTED, anchor="end"))

    # 1. Смуга пропускання об'єкта f_BW (0 .. 100 Гц)
    x_bw = x0 + 100
    p.append(rect(x0, y0 - 180, x_bw - x0, 180, fill="#e8f4fd", stroke="#3498db", sw=1.5, rx=0))
    p.append(text((x0 + x_bw) / 2, y0 - 100, "Смуга об'єкта", size=11, color=NEG, bold=True))
    p.append(text((x0 + x_bw) / 2, y0 - 80, "f_BW", size=11, color=NEG, bold=True))
    p.append(text((x0 + x_bw) / 2, y0 - 60, "0..100 Гц", size=10, color=NEG))
    p.append(line(x_bw, y0 - 190, x_bw, y0 + 10, color=NEG, sw=1.5, dash="4,3"))
    p.append(text(x_bw, y0 + 22, "f_BW", size=11, color=NEG, bold=True))

    # 2. Межа Найквіста 2 x f_BW (200 Гц)
    x_nyq = x0 + 200
    p.append(line(x_nyq, y0 - 240, x_nyq, y0 + 10, color=POS, sw=2.0, dash="5,4"))
    p.append(text(x_nyq, y0 + 22, "2·f_BW", size=11, color=POS, bold=True))
    p.append(text(x_nyq, y0 + 38, "(200 Гц)", size=10, color=POS))

    # Зона катастрофи (між 2 x f_BW та 10 x f_BW)
    x_rec_min = x0 + 360
    p.append(rect(x_nyq, y0 - 140, x_rec_min - x_nyq, 140, fill="#fdecea", stroke=POS, sw=1.0, rx=0))
    p.append(text((x_nyq + x_rec_min) / 2, y0 - 85, "Непридатна зона для петлі", size=10, color=POS, bold=True))
    p.append(text((x_nyq + x_rec_min) / 2, y0 - 65, "Велика затримка ZOH", size=10, color=POS))
    p.append(text((x_nyq + x_rec_min) / 2, y0 - 45, "Втрата запасу стійкості", size=10, color=POS))

    # 3. Рекомендована зона тактування петлі (10 .. 50 x f_BW)
    x_rec_max = x0 + 600
    p.append(rect(x_rec_min, y0 - 210, x_rec_max - x_rec_min, 210, fill="#eafaf1", stroke=FIELD, sw=2.0, rx=0))
    p.append(text((x_rec_min + x_rec_max) / 2, y0 - 140, "Робоча зона тактування петлі", size=12, color=FIELD, bold=True))
    p.append(text((x_rec_min + x_rec_max) / 2, y0 - 118, "f_loop = 10 .. 50 × f_BW (1 .. 5 кГц)", size=11, color=FIELD, bold=True))
    p.append(text((x_rec_min + x_rec_max) / 2, y0 - 92, "Затримка квантування мала (Δφ < 5°..10°)", size=10, color=INK))
    p.append(text((x_rec_min + x_rec_max) / 2, y0 - 72, "Цифровий регулятор еквівалентний", size=10, color=INK))
    p.append(text((x_rec_min + x_rec_max) / 2, y0 - 54, "неперервній аналоговій моделі", size=10, color=INK))

    p.append(line(x_rec_min, y0 - 220, x_rec_min, y0 + 10, color=FIELD, sw=1.5, dash="4,3"))
    p.append(text(x_rec_min, y0 + 22, "10·f_BW", size=11, color=FIELD, bold=True))

    p.append(line(x_rec_max, y0 - 220, x_rec_max, y0 + 10, color=FIELD, sw=1.5, dash="4,3"))
    p.append(text(x_rec_max, y0 + 22, "50·f_BW", size=11, color=FIELD, bold=True))

    # 4. Зона надлишкового оверсемплінгу (> 50 x f_BW)
    x_excess = x0 + w_axis - 20
    p.append(rect(x_rec_max, y0 - 120, x_excess - x_rec_max, 120, fill="#f4f6f8", stroke=MUTED, sw=1.0, rx=0))
    p.append(text((x_rec_max + x_excess) / 2, y0 - 75, "Оверсемплінг (>50·f_BW)", size=10, color=MUTED, bold=True))
    p.append(text((x_rec_max + x_excess) / 2, y0 - 55, "Ріст шуму D-складової,", size=9, color=MUTED))
    p.append(text((x_rec_max + x_excess) / 2, y0 - 38, "перевантаження CPU", size=9, color=MUTED))

    # Порівняльна винесення
    tb, _, _ = textbox(x0 + 190, 75, "Теорема Найквіста-Шеннона:\nВідновлення пасивного спектра без накладання (f_s > 2·f_max)\nАле НЕ гарантує стійкість замкненого контуру!", size=10, pad=8, fill="#ffffff", stroke="#3498db")
    p.append(tb)

    return render(path, W, H, *p)


# ── 2. jitter-derivative-spike: спотворення ПІД через джитер ────────────────────
def fig_jitter_derivative_spike():
    path = os.path.join(OUT, "jitter-derivative-spike.svg")
    W, H = 880, 390
    p = []

    p.append(text(W / 2, 26, "Вплив часового джитера на обчислення похідної та інтеграла", size=15, color=INK, bold=True))

    # Лівий графік: Ідеальний фіксований крок dt
    gx1, gy1, gw, gh = 60, 190, 360, 110
    p.append(rect(gx1, gy1 - gh, gw, gh + 40, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(gx1 + gw / 2, gy1 - gh + 20, "Ідеальний стабільний такт (dt = const)", size=12, color=FIELD, bold=True))

    # Вісь часу
    p.append(arrow(gx1 + 20, gy1, gx1 + gw - 20, gy1, color=INK, sw=1.5))
    p.append(text(gx1 + gw - 15, gy1 + 18, "t", size=12, color=INK, italic=True))

    # Рівномірні засічки часу
    dt_ideal = 45
    t_starts = [gx1 + 45 + i * dt_ideal for i in range(7)]
    for i, tx in enumerate(t_starts):
        p.append(line(tx, gy1 - 5, tx, gy1 + 5, color=INK, sw=1.5))
        p.append(text(tx, gy1 + 18, "t_%d" % i, size=10, color=MUTED))

    # Плавний сигнал помилки e(t)
    p.append(line(t_starts[0], gy1 - 10, t_starts[1], gy1 - 25, color=NEG, sw=2.0))
    p.append(line(t_starts[1], gy1 - 25, t_starts[2], gy1 - 45, color=NEG, sw=2.0))
    p.append(line(t_starts[2], gy1 - 45, t_starts[3], gy1 - 65, color=NEG, sw=2.0))
    p.append(line(t_starts[3], gy1 - 65, t_starts[4], gy1 - 80, color=NEG, sw=2.0))
    p.append(line(t_starts[4], gy1 - 80, t_starts[5], gy1 - 90, color=NEG, sw=2.0))
    p.append(line(t_starts[5], gy1 - 90, t_starts[6], gy1 - 95, color=NEG, sw=2.0))

    for tx, ty in zip(t_starts, [10, 25, 45, 65, 80, 90, 95]):
        p.append(circle(tx, gy1 - ty, 3.5, fill=NEG, stroke="#ffffff", sw=1.0))

    # Стабільна похідна
    p.append(text(gx1 + 30, gy1 + 32, "Похідна d(e)/dt:", size=10, color=INK, bold=True, anchor="start"))
    p.append(text(gx1 + 140, gy1 + 32, "Плавний сигнал керування, без викидів", size=10, color=FIELD, anchor="start"))

    # Правий графік: Реальний крок із джитером
    gx2 = 470
    p.append(rect(gx2, gy1 - gh, gw, gh + 40, fill="#fef2f2", stroke="#fca5a5", sw=1.0, rx=4))
    p.append(text(gx2 + gw / 2, gy1 - gh + 20, "Плаваючий такт із джитером (dt ± δt)", size=12, color=POS, bold=True))

    p.append(arrow(gx2 + 20, gy1, gx2 + gw - 20, gy1, color=INK, sw=1.5))
    p.append(text(gx2 + gw - 15, gy1 + 18, "t", size=12, color=INK, italic=True))

    # Нерівномірні засічки (з джитером)
    offsets = [0, -14, +16, -10, +18, -12, +5]
    t_jitter = [gx2 + 45 + i * dt_ideal + offsets[i] for i in range(7)]
    for i, tx in enumerate(t_jitter):
        p.append(line(tx, gy1 - 5, tx, gy1 + 5, color=POS, sw=1.5))
        p.append(text(tx, gy1 + 18, "t_%d" % i, size=10, color=POS))

    # Сигнал помилки
    p.append(line(t_jitter[0], gy1 - 10, t_jitter[1], gy1 - 18, color=NEG, sw=1.5, dash="3,2"))
    p.append(line(t_jitter[1], gy1 - 18, t_jitter[2], gy1 - 58, color=NEG, sw=1.5, dash="3,2"))
    p.append(line(t_jitter[2], gy1 - 58, t_jitter[3], gy1 - 60, color=NEG, sw=1.5, dash="3,2"))
    p.append(line(t_jitter[3], gy1 - 60, t_jitter[4], gy1 - 88, color=NEG, sw=1.5, dash="3,2"))
    p.append(line(t_jitter[4], gy1 - 88, t_jitter[5], gy1 - 85, color=NEG, sw=1.5, dash="3,2"))
    p.append(line(t_jitter[5], gy1 - 85, t_jitter[6], gy1 - 95, color=NEG, sw=1.5, dash="3,2"))

    for tx, ty in zip(t_jitter, [10, 18, 58, 60, 88, 85, 95]):
        p.append(circle(tx, gy1 - ty, 3.5, fill=NEG, stroke="#ffffff", sw=1.0))

    # Похідна зі спайками
    p.append(text(gx2 + 30, gy1 + 32, "Похідна при dt=const:", size=10, color=INK, bold=True, anchor="start"))
    p.append(text(gx2 + 160, gy1 + 32, "Хибні сплески та шум струму ШІМ!", size=10, color=POS, bold=True, anchor="start"))

    # Пояснювальний блок знизу
    bx, by, bw, bh = 60, 280, 770, 85
    p.append(rect(bx, by, bw, bh, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=6))
    p.append(text(bx + 15, by + 22, "Механізм спотворення: чому софтверна затримка знищує ПІД-регулятор", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(bx + 15, by + 45, "1. Диференціатор: D[k] = Kd · (e[k] − e[k−1]) / dt_ном. При затримці виклику реальна зміна Δe зростає, даючи хибний сплеск сили.", size=10, color=INK, anchor="start"))
    p.append(text(bx + 15, by + 65, "2. Інтегратор: I[k] = I[k−1] + Ki · e[k] · dt_ном. Недооцінка або переоцінка реального часу призводить до низькочастотного дрейфу.", size=10, color=INK, anchor="start"))

    return render(path, W, H, *p)


# ── 3. timer-trgo-adc-pipeline: апаратний пайплайн тактування ───────────────────
def fig_timer_trgo_pipeline():
    path = os.path.join(OUT, "timer-trgo-adc-pipeline.svg")
    W, H = 880, 360
    p = []

    p.append(text(W / 2, 26, "Апаратний конвеєр тактування: АЦП по тригеру таймера vs RTOS", size=15, color=INK, bold=True))

    # 1. Апаратний таймер
    b1_x, b1_y, b1_w, b1_h = 40, 70, 160, 95
    p.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#e8f4fd", stroke="#2980b9", sw=1.8, rx=6))
    p.append(text(b1_x + b1_w / 2, b1_y + 24, "Апаратний таймер", size=12, color=NEG, bold=True))
    p.append(text(b1_x + b1_w / 2, b1_y + 44, "TIM1 / TIM2 (Auto-Reload)", size=10, color=INK))
    p.append(text(b1_x + b1_w / 2, b1_y + 64, "Період T_s = 50 мкс", size=10, color=NEG, bold=True))
    p.append(text(b1_x + b1_w / 2, b1_y + 80, "Абсолютний нуль джитера", size=9, color=FIELD, bold=True))

    # Стрілка TRGO
    p.append(arrow(b1_x + b1_w, b1_y + b1_h / 2, b1_x + b1_w + 45, b1_y + b1_h / 2, color=NEG, sw=2.0))
    p.append(text(b1_x + b1_w + 22, b1_y + b1_h / 2 - 10, "TRGO", size=10, color=NEG, bold=True))
    p.append(text(b1_x + b1_w + 22, b1_y + b1_h / 2 + 18, "(апаратний)", size=9, color=MUTED))

    # 2. АЦП по тригеру
    b2_x = b1_x + b1_w + 50
    b2_w = 170
    p.append(rect(b2_x, b1_y, b2_w, b1_h, fill="#fef9e7", stroke="#f39c12", sw=1.8, rx=6))
    p.append(text(b2_x + b2_w / 2, b1_y + 24, "АЦП (Dual SAR)", size=12, color="#d35400", bold=True))
    p.append(text(b2_x + b2_w / 2, b1_y + 44, "Синхронна вибірка струму", size=10, color=INK))
    p.append(text(b2_x + b2_w / 2, b1_y + 64, "T_sample + T_conv = 1.2 мкс", size=10, color="#d35400", bold=True))
    p.append(text(b2_x + b2_w / 2, b1_y + 80, "Автоматичний старт без CPU", size=9, color=FIELD, bold=True))

    # Стрілка EOC / DMA
    p.append(arrow(b2_x + b2_w, b1_y + b1_h / 2, b2_x + b2_w + 45, b1_y + b1_h / 2, color="#d35400", sw=2.0))
    p.append(text(b2_x + b2_w + 22, b1_y + b1_h / 2 - 10, "DMA / ISR", size=10, color="#d35400", bold=True))
    p.append(text(b2_x + b2_w + 22, b1_y + b1_h / 2 + 18, "(переривання)", size=9, color=MUTED))

    # 3. Обчислення ПІД в ISR
    b3_x = b2_x + b2_w + 50
    b3_w = 175
    p.append(rect(b3_x, b1_y, b3_w, b1_h, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(b3_x + b3_w / 2, b1_y + 24, "ISR найвищого пріоритету", size=12, color=FIELD, bold=True))
    p.append(text(b3_x + b3_w / 2, b1_y + 44, "ПІД-регулятор / FOC", size=10, color=INK))
    p.append(text(b3_x + b3_w / 2, b1_y + 64, "T_calc = 3.5 мкс", size=10, color=FIELD, bold=True))
    p.append(text(b3_x + b3_w / 2, b1_y + 80, "Неблокуючий, без malloc", size=9, color=INK))

    # Стрілка оновлення ШІМ
    p.append(arrow(b3_x + b3_w, b1_y + b1_h / 2, b3_x + b3_w + 45, b1_y + b1_h / 2, color=FIELD, sw=2.0))
    p.append(text(b3_x + b3_w + 22, b1_y + b1_h / 2 - 10, "Preload", size=10, color=FIELD, bold=True))
    p.append(text(b3_x + b3_w + 22, b1_y + b1_h / 2 + 18, "(тіньовий)", size=9, color=MUTED))

    # 4. Модулятор ШІМ
    b4_x = b3_x + b3_w + 50
    b4_w = 160
    p.append(rect(b4_x, b1_y, b4_w, b1_h, fill="#f4f6f8", stroke=INK, sw=1.8, rx=6))
    p.append(text(b4_x + b4_w / 2, b1_y + 24, "ШІМ-генератор", size=12, color=INK, bold=True))
    p.append(text(b4_x + b4_w / 2, b1_y + 44, "TIM1 Complementary PWM", size=10, color=INK))
    p.append(text(b4_x + b4_w / 2, b1_y + 64, "Оновлення на верхівці", size=10, color=INK, bold=True))
    p.append(text(b4_x + b4_w / 2, b1_y + 80, "Без глітчів коефіцієнта", size=9, color=FIELD, bold=True))

    # Порівняння: Червоний блок знизу (Чому RTOS task програє)
    rx, ry, rw, rh = 40, 200, 800, 130
    p.append(rect(rx, ry, rw, rh, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(rx + 20, ry + 26, "Чому FreeRTOS vTaskDelay / delay_ms() руйнує прецизійний контур:", size=13, color=POS, bold=True, anchor="start"))

    p.append(text(rx + 20, ry + 54, "• Квант системного таймера (SysTick): 1 мс (1000 Гц) — занадто повільно для контуру 10..20 кГц.", size=10, color=INK, anchor="start"))
    p.append(text(rx + 20, ry + 74, "• Диспетчеризація та блокування: виклик vTaskDelayUntil залежить від інших переривань і критичних секцій (taskENTER_CRITICAL).", size=10, color=INK, anchor="start"))
    p.append(text(rx + 20, ry + 94, "• Джитер перемикання контексту: затримка може випадково стрибати на 10..200 мкс, викликаючи резонанс диференціатора.", size=10, color=INK, anchor="start"))
    p.append(text(rx + 20, ry + 114, "• Висновок: Жорсткий контур керування живе ТІЛЬКИ в апаратному ISR; FreeRTOS отримує лише телеметрію через чергу.", size=10, color=POS, bold=True, anchor="start"))

    return render(path, W, H, *p)


# ── 4. transport-delay-phase-erosion: затримка транспорту й запас за фазою ──────
def fig_transport_delay_phase():
    path = os.path.join(OUT, "transport-delay-phase-erosion.svg")
    W, H = 880, 420
    p = []

    p.append(text(W / 2, 26, "Складові чистої затримки транспорту та ерозія запасу за фазою", size=15, color=INK, bold=True))

    # Верхній таймлайн: ланцюг затримок
    tx0, ty0, tw = 60, 60, 760
    p.append(rect(tx0, ty0, tw, 70, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(tx0 + 15, ty0 + 20, "Часова шкала одного такту керування (Повна затримка T_total = T_sample + T_calc + T_pwm + T_zoh):", size=11, color=INK, bold=True, anchor="start"))

    # Відрізки затримок
    sx = tx0 + 20
    # 1. T_sample (АЦП вибірка)
    w_s = 90
    p.append(rect(sx, ty0 + 32, w_s, 26, fill="#fde8e8", stroke=POS, sw=1.2, rx=3))
    p.append(text(sx + w_s / 2, ty0 + 49, "T_adc (1.5 мкс)", size=9, color=POS, bold=True))

    # 2. T_calc (Обчислення ПІД)
    sx += w_s + 10
    w_c = 130
    p.append(rect(sx, ty0 + 32, w_c, 26, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=3))
    p.append(text(sx + w_c / 2, ty0 + 49, "T_calc (4.0 мкс)", size=9, color="#b45309", bold=True))

    # 3. T_pwm_sync (Очікування оновлення ШІМ)
    sx += w_c + 10
    w_p = 190
    p.append(rect(sx, ty0 + 32, w_p, 26, fill="#e0e7ff", stroke="#4f46e5", sw=1.2, rx=3))
    p.append(text(sx + w_p / 2, ty0 + 49, "T_pwm_sync (очікування тіні 0..25 мкс)", size=9, color="#4338ca", bold=True))

    # 4. T_zoh (Екстраполятор нульового порядку)
    sx += w_p + 10
    w_z = 240
    p.append(rect(sx, ty0 + 32, w_z, 26, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=3))
    p.append(text(sx + w_z / 2, ty0 + 49, "T_zoh = T_s / 2 (еквівалент затримки ЦАП/ШІМ 25 мкс)", size=9, color="#0369a1", bold=True))

    # Графік Боде фази (знизу ліворуч та праворуч)
    bx0, by0, bw, bh = 60, 160, 760, 230
    p.append(rect(bx0, by0, bw, bh, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    p.append(text(bx0 + 20, by0 + 24, "Фазовий зсув на ЛАФЧХ: Втрата Phase Margin через затримку транспорту e^(−j·ω·T_d)", size=12, color=INK, bold=True, anchor="start"))

    # Осі графіка
    ax0, ay0, aw, ah = bx0 + 60, by0 + 175, 640, 120
    p.append(arrow(ax0, ay0, ax0 + aw, ay0, color=INK, sw=1.5))
    p.append(arrow(ax0, ay0 + 20, ax0, ay0 - ah, color=INK, sw=1.5))
    p.append(text(ax0 + aw - 10, ay0 + 22, "Частота ω (рад/с) →", size=10, color=MUTED, anchor="end"))
    p.append(text(ax0 - 10, ay0 - ah + 10, "Фаза φ(ω)", size=10, color=MUTED, anchor="end"))

    # Горизонтальні лінії фази: 0°, -90°, -180°
    p.append(line(ax0, ay0 - 100, ax0 + aw, ay0 - 100, color="#e2e8f0", sw=1.0))
    p.append(text(ax0 - 8, ay0 - 96, "0°", size=9, color=MUTED, anchor="end"))

    p.append(line(ax0, ay0 - 50, ax0 + aw, ay0 - 50, color="#e2e8f0", sw=1.0))
    p.append(text(ax0 - 8, ay0 - 46, "−90°", size=9, color=MUTED, anchor="end"))

    p.append(line(ax0, ay0, ax0 + aw, ay0, color="#fca5a5", sw=1.5, dash="4,3"))
    p.append(text(ax0 - 8, ay0 + 4, "−180° (Межа стійкості)", size=9, color=POS, bold=True, anchor="end"))

    # Частота зрізу (кросовера) wc
    x_wc = ax0 + 340
    p.append(line(x_wc, ay0 - ah, x_wc, ay0 + 20, color="#64748b", sw=1.5, dash="3,3"))
    p.append(text(x_wc, ay0 + 20, "ω_c (Частота зрізу)", size=10, color=INK, bold=True))

    # Крива 1: Неперервна система (без дискретної затримки)
    # Плавний спуск від -40° до -125° на wc
    p.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (ax0, ay0 - 85, ax0 + 200, ay0 - 75, ax0 + aw, ay0 - 20, FIELD))
    p.append(text(ax0 + 160, ay0 - 85, "Неперервна модель: PM = 55° (Стійко)", size=10, color=FIELD, bold=True))

    # Стрілка запасу по фазі для неперервної
    p.append(line(x_wc, ay0 - 35, x_wc, ay0, color=FIELD, sw=2.0))
    p.append(text(x_wc + 8, ay0 - 18, "PM_ideal = 55°", size=9, color=FIELD, bold=True, anchor="start"))

    # Крива 2: Дискретна система з затримкою T_d (стрімке падіння фази: Δφ = −ω·T_d)
    p.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (ax0, ay0 - 85, ax0 + 220, ay0 - 55, ax0 + aw, ay0 + 28, POS))
    p.append(text(ax0 + 380, ay0 + 10, "Дискретна петля з затримкою T_d (фаза провалюється за −180°)", size=10, color=POS, bold=True, anchor="start"))

    # Точка на wc з затримкою
    p.append(circle(x_wc, ay0 + 8, 4.5, fill=POS, stroke="#ffffff", sw=1.5))
    p.append(text(x_wc - 12, ay0 + 14, "Δφ_delay = −65°", size=9, color=POS, bold=True, anchor="end"))
    p.append(text(x_wc + 8, ay0 + 25, "PM_real = −10° → АВТОКОЛИВАННЯ", size=10, color=POS, bold=True, anchor="start"))

    return render(path, W, H, *p)


def main():
    fig_nyquist_vs_control()
    fig_jitter_derivative_spike()
    fig_timer_trgo_pipeline()
    fig_transport_delay_phase()
    print("All 4 SVGs generated successfully in", OUT)


if __name__ == "__main__":
    main()
