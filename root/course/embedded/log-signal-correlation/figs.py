# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. clock-drift-inversion: Інверсія причини й наслідку через дрейф RTC ─────────
def fig_clock_drift_inversion():
    W, H = 840, 480
    p = []

    p.append(text(W / 2, 26, "Хронологічна ілюзія: як розсинхронізовані годинники міняють місцями причину і наслідок",
                  size=14, bold=True, color=INK))

    y_phys = 85
    p.append(text(65, y_phys, "Фізичний час (UTC / Еталон)", size=11, bold=True, color=MUTED, anchor="start"))
    p.append(arrow(260, y_phys, 800, y_phys, color=LINE, sw=1.8))
    for t_val, tx in [(0, 300), (50, 430), (100, 560), (150, 690)]:
        p.append(line(tx, y_phys - 4, tx, y_phys + 4, color=LINE, sw=1.2))
        p.append(text(tx, y_phys - 10, f"{t_val} мс", size=10, color=MUTED))

    # Вузол А
    y_a = 165
    b_a, _, _ = textbox(120, y_a, "Вузол А: Контролер мотора\nRTC поспішає на +40 мс",
                        size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.5, min_w=190)
    p.append(b_a)
    p.append(arrow(260, y_a, 800, y_a, color=POS, sw=1.8))

    # Вузол Б
    y_b = 275
    b_b, _, _ = textbox(120, y_b, "Вузол Б: Супервізор системи\nRTC відстає на −25 мс",
                        size=11, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.5, min_w=190)
    p.append(b_b)
    p.append(arrow(260, y_b, 800, y_b, color=NEG, sw=1.8))

    # Подія 1 на Вузлі А (t_phys = 40 ms)
    x_ev1 = 405
    p.append(circle(x_ev1, y_a, 6, fill=POS, stroke="#ffffff", sw=2))
    b_ev1, _, _ = textbox(x_ev1, y_a - 40, "1. Аварійний надструм у моторі!\nЛокальний запис: t_A = 80 мс",
                          size=10, bold=True, color=POS, fill="#fff5f5", stroke=POS, sw=1.2)
    p.append(b_ev1)
    p.append(line(x_ev1, y_a - 18, x_ev1, y_a - 6, color=POS, sw=1.2))

    # Пакет CAN від Вузла А до Вузла Б
    x_ev2 = 535
    p.append(arrow(x_ev1 + 4, y_a + 6, x_ev2 - 4, y_b - 6, color=LINE, sw=1.6))
    p.append(text((x_ev1 + x_ev2) / 2 + 35, (y_a + y_b) / 2 - 6, "CAN: кадр тривоги (затримка 10 мс)",
                  size=9, bold=True, color=LINE))

    # Подія 2 на Вузлі Б (t_phys = 50 ms)
    p.append(circle(x_ev2, y_b, 6, fill=NEG, stroke="#ffffff", sw=2))
    b_ev2, _, _ = textbox(x_ev2, y_b + 42, "2. Прийом тривоги CAN\nЛокальний запис: t_Б = 25 мс",
                          size=10, bold=True, color=NEG, fill="#f0f5ff", stroke=NEG, sw=1.2)
    p.append(b_ev2)
    p.append(line(x_ev2, y_b + 6, x_ev2, y_b + 20, color=NEG, sw=1.2))

    # Підсумковий зведений журнал
    y_log = 390
    p.append(rect(40, y_log - 25, 760, 95, fill="#fffde7", stroke="#f57f17", sw=1.5, rx=6))
    p.append(text(60, y_log - 8, "Зведений журнал, відсортований за «настінним» RTC часом:", size=11, bold=True, color="#b78103", anchor="start"))
    
    p.append(text(75, y_log + 16, "[00:00:00.025] ВУЗОЛ Б: Отримано сигнал аварії від Вузла А (ПОМИЛКА СУПЕРВІЗОРА?)",
                  size=11, bold=True, color=NEG, anchor="start"))
    p.append(text(75, y_log + 38, "[00:00:00.080] ВУЗОЛ А: Спрацював апаратний захист за струмом (ПРИЧИНА)",
                  size=11, bold=True, color=POS, anchor="start"))
    p.append(text(75, y_log + 58, "Висновок непідготовленого інженера: «Супервізор почав панікувати на 55 мс раніше, ніж виник надструм!»",
                  size=10, italic=True, color=INK, anchor="start"))

    render(os.path.join(OUT, "clock-drift-inversion.svg"), W, H, *p,
           title="Інверсія послідовності подій у журналі через несинхронізовані RTC")


# ── 2. ptp-hw-timestamping: Апаратне штампування часових міток у PTP (IEEE 1588) ──
def fig_ptp_hw_timestamping():
    W, H = 820, 520
    p = []

    p.append(text(W / 2, 26, "Протокол точного часу IEEE 1588 PTP: апаратні мітки t1, t2, t3, t4",
                  size=14, bold=True, color=INK))

    x_m = 170
    x_s = 650

    b_m, _, _ = textbox(x_m, 70, "PTP Master\n(Еталон часу / Grandmaster)",
                        size=12, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.6, min_w=170)
    b_s, _, _ = textbox(x_s, 70, "PTP Slave\n(Кінцевий вузол / MCU)",
                        size=12, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.6, min_w=170)
    p.append(b_m); p.append(b_s)

    y_start = 115
    y_end = 405
    p.append(arrow(x_m, y_start, x_m, y_end, color=FIELD, sw=2.0))
    p.append(arrow(x_s, y_start, x_s, y_end, color=NEG, sw=2.0))

    # 1. Sync
    y_t1 = 150
    y_t2 = 210
    p.append(arrow(x_m, y_t1, x_s, y_t2, color=INK, sw=1.6))
    p.append(text((x_m + x_s) / 2, (y_t1 + y_t2) / 2 - 10, "1. Повідомлення Sync", size=11, bold=True, color=INK))

    b_t1, _, _ = textbox(x_m - 65, y_t1, "t1 (PHY TX)", size=10, bold=True, color=FIELD, fill="#ffffff", stroke=FIELD, sw=1.2)
    b_t2, _, _ = textbox(x_s + 65, y_t2, "t2 (PHY RX)", size=10, bold=True, color=NEG, fill="#ffffff", stroke=NEG, sw=1.2)
    p.append(b_t1); p.append(b_t2)

    # 2. Follow_Up
    y_fu1 = 230
    y_fu2 = 260
    p.append(arrow(x_m, y_fu1, x_s, y_fu2, color=MUTED, sw=1.4))
    p.append(text((x_m + x_s) / 2, (y_fu1 + y_fu2) / 2 - 10, "2. Follow_Up (передає точне значення t1)", size=10, italic=True, color=MUTED))

    # 3. Delay_Req
    y_t3 = 290
    y_t4 = 350
    p.append(arrow(x_s, y_t3, x_m, y_t4, color=INK, sw=1.6))
    p.append(text((x_m + x_s) / 2, (y_t3 + y_t4) / 2 - 10, "3. Повідомлення Delay_Req", size=11, bold=True, color=INK))

    b_t3, _, _ = textbox(x_s + 65, y_t3, "t3 (PHY TX)", size=10, bold=True, color=NEG, fill="#ffffff", stroke=NEG, sw=1.2)
    b_t4, _, _ = textbox(x_m - 65, y_t4, "t4 (PHY RX)", size=10, bold=True, color=FIELD, fill="#ffffff", stroke=FIELD, sw=1.2)
    p.append(b_t3); p.append(b_t4)

    # 4. Delay_Resp
    y_dr1 = 370
    y_dr2 = 400
    p.append(arrow(x_m, y_dr1, x_s, y_dr2, color=MUTED, sw=1.4))
    p.append(text((x_m + x_s) / 2, (y_dr1 + y_dr2) / 2 - 10, "4. Delay_Resp (передає точне значення t4)", size=10, italic=True, color=MUTED))

    # Блок формул
    y_box = 458
    p.append(rect(60, y_box - 38, 700, 80, fill="#f4f6f8", stroke="#b0bec5", sw=1.5, rx=6))
    p.append(text(W / 2, y_box - 18, "Розрахунок затримки каналу та зсуву годинника на боці Slave:",
                  size=11, bold=True, color=INK))
    p.append(text(W / 2 - 170, y_box + 12, "Затримка: Delay = ((t4 − t1) − (t3 − t2)) ÷ 2",
                  size=11, bold=True, color=FIELD))
    p.append(text(W / 2 + 170, y_box + 12, "Зсув часу: Offset = ((t2 − t1) − (t4 − t3)) ÷ 2",
                  size=11, bold=True, color=POS))
    p.append(text(W / 2, y_box + 30, "Апаратні мітки на рівні PHY виключають джитер стека ОС і черг RTOS (< 100 нс похибки)",
                  size=10, italic=True, color=MUTED))

    render(os.path.join(OUT, "ptp-hw-timestamping.svg"), W, H, *p,
           title="Обмін повідомленнями PTP та апаратна фіксація часових міток")


# ── 3. vector-clock-causality: Векторні годинники та причинність ──────────────────
def fig_vector_clock_causality():
    W, H = 840, 490
    p = []

    p.append(text(W / 2, 26, "Векторні годинники: розрізнення причинного зв'язку (a → b) та конкурентності (a || b)",
                  size=14, bold=True, color=INK))

    y_n1 = 90
    y_n2 = 210
    y_n3 = 330

    b1, _, _ = textbox(95, y_n1, "Вузол 1 (N1)", size=11, bold=True, color=INK, fill="#f4f6f8", stroke=LINE, sw=1.5, min_w=120)
    b2, _, _ = textbox(95, y_n2, "Вузол 2 (N2)", size=11, bold=True, color=INK, fill="#f4f6f8", stroke=LINE, sw=1.5, min_w=120)
    b3, _, _ = textbox(95, y_n3, "Вузол 3 (N3)", size=11, bold=True, color=INK, fill="#f4f6f8", stroke=LINE, sw=1.5, min_w=120)
    p.append(b1); p.append(b2); p.append(b3)

    p.append(arrow(170, y_n1, 790, y_n1, color=LINE, sw=1.8))
    p.append(arrow(170, y_n2, 790, y_n2, color=LINE, sw=1.8))
    p.append(arrow(170, y_n3, 790, y_n3, color=LINE, sw=1.8))

    # Подія a на N1 (x=240)
    x_a = 240
    p.append(circle(x_a, y_n1, 5, fill=POS, stroke=LINE, sw=1.5))
    b_va, _, _ = textbox(x_a, y_n1 - 25, "a [1, 0, 0]", size=10, bold=True, color=POS, fill="#fff5f5", stroke=POS, sw=1.2)
    p.append(b_va)

    # Подія c на N3 (x=280)
    x_c = 280
    p.append(circle(x_c, y_n3, 5, fill=NEG, stroke=LINE, sw=1.5))
    b_vc, _, _ = textbox(x_c, y_n3 + 25, "c [0, 0, 1]", size=10, bold=True, color=NEG, fill="#f0f5ff", stroke=NEG, sw=1.2)
    p.append(b_vc)

    # Повідомлення від N1 до N2
    x_b = 420
    p.append(arrow(x_a, y_n1 + 5, x_b, y_n2 - 5, color=POS, sw=1.5))
    p.append(text((x_a + x_b) / 2 + 15, (y_n1 + y_n2) / 2 - 8, "msg(a) [1, 0, 0]", size=9, bold=True, color=POS))

    # Подія b на N2
    p.append(circle(x_b, y_n2, 5, fill=POS, stroke=LINE, sw=1.5))
    b_vb, _, _ = textbox(x_b, y_n2 - 25, "b [1, 1, 0]", size=10, bold=True, color=POS, fill="#fff5f5", stroke=POS, sw=1.2)
    p.append(b_vb)

    # Подія d на N2
    x_d = 550
    p.append(circle(x_d, y_n2, 5, fill=FIELD, stroke=LINE, sw=1.5))
    b_vd, _, _ = textbox(x_d, y_n2 - 25, "d [1, 2, 0]", size=10, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.2)
    p.append(b_vd)

    # Повідомлення від N2 до N3
    x_e = 690
    p.append(arrow(x_d, y_n2 + 5, x_e, y_n3 - 5, color=FIELD, sw=1.5))
    p.append(text((x_d + x_e) / 2 + 15, (y_n2 + y_n3) / 2 - 8, "msg(d) [1, 2, 0]", size=9, bold=True, color=FIELD))

    # Подія e на N3
    p.append(circle(x_e, y_n3, 5, fill=FIELD, stroke=LINE, sw=1.5))
    b_ve, _, _ = textbox(x_e, y_n3 + 25, "e [1, 2, 2]", size=10, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.2)
    p.append(b_ve)

    # Аналітична панель
    y_comp = 415
    p.append(rect(40, y_comp - 20, 760, 78, fill="#ffffff", stroke="#cfd8dc", sw=1.5, rx=6))
    p.append(text(60, y_comp - 2, "Математичне визначення зв'язку між подіями за їхніми векторами V:", size=11, bold=True, color=INK, anchor="start"))
    p.append(text(75, y_comp + 20, "• Причинний зв'язок (a → e): V(a)=[1,0,0] ≤ V(e)=[1,2,2] (для всіх k: V_a[k] ≤ V_e[k] і є хоч одне <) ⇒ а передувало е",
                  size=10, bold=True, color=FIELD, anchor="start"))
    p.append(text(75, y_comp + 42, "• Конкурентні події (a || c): V(a)=[1,0,0] та V(c)=[0,0,1] — жоден вектор не менший за інший ⇒ події незалежні",
                  size=10, bold=True, color=POS, anchor="start"))

    render(os.path.join(OUT, "vector-clock-causality.svg"), W, H, *p,
           title="Просування векторних годинників та встановлення причинності")


# ── 4. signal-log-correlation: Крос-доменне зіставлення аналогових сигналів та логів ─
def fig_signal_log_correlation():
    W, H = 840, 540
    p = []

    p.append(text(W / 2, 22, "Крос-доменна кореляція: апаратний строб-пін як міст між осцилографом і логами",
                  size=14, bold=True, color=INK))

    x_left = 220
    x_right = 790

    # 1. Аналоговий сигнал напруги VDD
    y_vdd = 80
    p.append(text(205, y_vdd + 10, "Напруга VDD (3.3V)\n(Аналоговий осцилограф)", size=10, bold=True, color=NEG, anchor="end"))
    p.append(line(x_left, y_vdd, x_left + 230, y_vdd, color=NEG, sw=2.0))
    p.append(line(x_left + 230, y_vdd, x_left + 260, y_vdd + 42, color=NEG, sw=2.2))
    p.append(line(x_left + 260, y_vdd + 42, x_left + 420, y_vdd + 42, color=NEG, sw=2.2))
    p.append(line(x_left + 420, y_vdd + 42, x_left + 460, y_vdd, color=NEG, sw=2.0))
    p.append(line(x_left + 460, y_vdd, x_right, y_vdd, color=NEG, sw=2.0))
    p.append(line(x_left, y_vdd + 35, x_right, y_vdd + 35, color=POS, sw=1.2, dash="4 4"))
    p.append(text(x_right - 10, y_vdd + 28, "Поріг BOD (2.7V)", size=9, bold=True, color=POS, anchor="end"))

    # 2. Струм живлення I_supply
    y_curr = 180
    p.append(text(205, y_curr + 10, "Струм I_supply\n(Шунт / Power Profiler)", size=10, bold=True, color="#b9770e", anchor="end"))
    p.append(line(x_left, y_curr + 30, x_left + 225, y_curr + 30, color="#e67e22", sw=2.0))
    p.append(line(x_left + 225, y_curr + 30, x_left + 240, y_curr - 15, color="#e67e22", sw=2.2))
    p.append(line(x_left + 240, y_curr - 15, x_left + 420, y_curr - 15, color="#e67e22", sw=2.2))
    p.append(line(x_left + 420, y_curr - 15, x_left + 435, y_curr + 30, color="#e67e22", sw=2.0))
    p.append(line(x_left + 435, y_curr + 30, x_right, y_curr + 30, color="#e67e22", sw=2.0))
    p.append(text(x_left + 330, y_curr - 22, "Сплеск 85 мА (Flash Charge Pump)", size=9, bold=True, color="#b9770e"))

    # 3. Апаратний налагоджувальний GPIO Строб (Debug Pin)
    y_gpio = 280
    p.append(text(205, y_gpio + 10, "Debug GPIO Строб\n(1 такт ядра, 0 нс затримка)", size=10, bold=True, color=FIELD, anchor="end"))
    p.append(line(x_left, y_gpio + 25, x_left + 210, y_gpio + 25, color=FIELD, sw=2.0))
    p.append(line(x_left + 210, y_gpio + 25, x_left + 210, y_gpio - 10, color=FIELD, sw=2.2))
    p.append(line(x_left + 210, y_gpio - 10, x_left + 440, y_gpio - 10, color=FIELD, sw=2.2))
    p.append(line(x_left + 440, y_gpio - 10, x_left + 440, y_gpio + 25, color=FIELD, sw=2.2))
    p.append(line(x_left + 440, y_gpio + 25, x_right, y_gpio + 25, color=FIELD, sw=2.0))
    p.append(text(x_left + 325, y_gpio + 3, "GPIO=HIGH (Тривалість операції Flash Erase)", size=9, bold=True, color=FIELD))

    # Вертикальний маркер синхронізації від GPIO
    x_marker = x_left + 210
    p.append(line(x_marker, 52, x_marker, 365, color=FIELD, sw=1.5, dash="3 3"))
    b_mark, _, _ = textbox(x_marker, 48, "Точка прив'язки t_0 (BSRR=HIGH)", size=9, bold=True, color=FIELD, fill="#ffffff", stroke=FIELD, sw=1.0)
    p.append(b_mark)

    # 4. Програмний потік логування (Log Buffer / UART)
    y_log = 370
    p.append(text(205, y_log + 10, "Програмні логи\n(Буфер RTOS / UART)", size=10, bold=True, color=INK, anchor="end"))
    b_l1, _, _ = textbox(x_left + 160, y_log + 12, "LOG_EVENT(ERASE_START)\n[t = 120.000 мс]", size=9, bold=True, color=INK, fill="#f4f6f8", stroke=LINE, sw=1.2)
    p.append(b_l1)
    
    x_uart = x_left + 520
    b_l2, _, _ = textbox(x_uart, y_log + 12, "UART TX: «[FLASH] Sector Erase...»\n(Затримка виводу +1.8 мс)", size=9, bold=True, color=MUTED, fill="#ffffff", stroke=MUTED, sw=1.2)
    p.append(b_l2)
    p.append(arrow(x_left + 260, y_log + 12, x_uart - 110, y_log + 12, color=MUTED, sw=1.2))

    # Блок висновку
    y_bot = 475
    p.append(rect(40, y_bot - 25, 760, 68, fill="#e8f5e9", stroke="#2e7d32", sw=1.4, rx=6))
    p.append(text(60, y_bot - 8, "Ключ до точної кореляції причин і наслідків:", size=11, bold=True, color="#1b5e20", anchor="start"))
    p.append(text(75, y_bot + 12, "1. Програмний лог безпомилково ідентифікує тип операції («хто викликав дію»)", size=10, color=INK, anchor="start"))
    p.append(text(75, y_bot + 28, "2. Апаратний GPIO строб усуває затримку форматування UART/RTT і точно зв'язує лог із фізичною просадкою на осцилографі", size=10, bold=True, color=FIELD, anchor="start"))

    render(os.path.join(OUT, "signal-log-correlation.svg"), W, H, *p,
           title="Крос-доменне зіставлення аналогових сигналів живлення та логів прошивки")


if __name__ == "__main__":
    fig_clock_drift_inversion()
    fig_ptp_hw_timestamping()
    fig_vector_clock_causality()
    fig_signal_log_correlation()
    print("All 4 figures generated successfully.")
