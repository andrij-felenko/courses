# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Розходження часових шкал TAI, UT1 та UTC ─────────────────────
def fig_time_scales_divergence():
    W, H = 840, 470
    parts = []
    parts.append(text(W/2, 24, "Розходження часових шкал TAI, UT1 та ступінчасте коригування UTC", size=15, bold=True))

    # Ліва інформаційна колонка (опис шкал)
    y0 = 55
    scales = [
        ("TAI (Міжнародний атомний час)", "Шкала на базі 400+ цезієвих еталонів. Суворо рівномірна та неперервна (секунда SI).", "#27ae60", "#eafaf1"),
        ("UT1 (Астрономічний час обертання Землі)", "Шкала за кутом повороту планети. Нерівномірна через припливне гальмування та рух магми.", "#d35400", "#fef5e7"),
        ("UTC (Координований всесвітній час)", "Секунда SI (як у TAI), але з дискретними кроками +1 с (23:59:60) для утримання |UTC−UT1| < 0.9 с.", "#2457d6", "#eaf0fd"),
    ]

    for i, (name, desc, col, bg_col) in enumerate(scales):
        box_y = y0 + i * 54
        b = fitbox(30, box_y, 780, 46, f"{name}: {desc}", size=11.5, fill=bg_col, stroke=col, color=col, bold=True)
        parts.append(b)

    # Нижня частина: графічна шкала розходження шкал
    gy = 240
    # Вісь часу
    parts.append(line(50, gy + 120, 790, gy + 120, color=LINE, sw=1.5))
    parts.append(arrow(750, gy + 120, 800, gy + 120, color=LINE, sw=1.8))
    parts.append(text(790, gy + 140, "Час (роки)", size=11, bold=True, anchor="end"))

    # Лінія TAI (зелена, опорна пряма)
    parts.append(line(60, gy + 30, 770, gy + 30, color="#27ae60", sw=2.5))
    parts.append(text(80, gy + 22, "TAI (ідеальна пряма SI)", size=11.5, color="#27ae60", bold=True, anchor="start"))

    # Лінія UT1 (помаранчева, плавно просідає вниз через сповільнення Землі)
    ut1_points = [
        (60, gy + 30), (180, gy + 45), (300, gy + 68), (420, gy + 90),
        (540, gy + 105), (660, gy + 125), (770, gy + 148)
    ]
    for j in range(len(ut1_points) - 1):
        x1, y1 = ut1_points[j]
        x2, y2 = ut1_points[j+1]
        parts.append(line(x1, y1, x2, y2, color="#d35400", sw=2, dash="5,3"))
    parts.append(text(550, gy + 135, "UT1 (астрономічне відхилення ΔT)", size=11, color="#d35400", bold=True))

    # Східчаста лінія UTC (синя, стрибками повертається ближче до UT1)
    utc_segments = [
        ((60, gy + 30), (180, gy + 30)),
        ((180, gy + 30), (180, gy + 50)), # стрибок 1
        ((180, gy + 50), (320, gy + 50)),
        ((320, gy + 50), (320, gy + 75)), # стрибок 2
        ((320, gy + 75), (460, gy + 75)),
        ((460, gy + 75), (460, gy + 95)), # стрибок 3
        ((460, gy + 95), (600, gy + 95)),
        ((600, gy + 95), (600, gy + 115)), # стрибок 4
        ((600, gy + 115), (770, gy + 115)),
    ]
    for seg in utc_segments:
        (x1, y1), (x2, y2) = seg
        is_step = (x1 == x2)
        parts.append(line(x1, y1, x2, y2, color="#2457d6", sw=2.5 if not is_step else 2, dash="3,2" if is_step else None))

    parts.append(text(210, gy + 45, "UTC (коригується на +1 с)", size=11, color="#2457d6", bold=True, anchor="start"))

    # Позначення зсуву TAI - UTC = 37 секунд
    parts.append(line(770, gy + 30, 770, gy + 115, color="#c0392b", sw=1.5))
    parts.append(textbox(710, gy + 72, "TAI − UTC = 37 с\n(станом на 2026 р.)", size=10.5, pad=5, fill="#fdecea", stroke="#c0392b", color="#c0392b", bold=True)[0])

    # Допустимий коридор |UTC - UT1| < 0.9 c
    parts.append(textbox(430, gy + 155, "Коридор IERS: |UTC − UT1| < 0.9 секунди", size=11, pad=6, fill="#f4f6f8", stroke=LINE, color=INK, bold=True)[0])

    render(os.path.join(IMG, "time-scales-divergence.svg"), W, H, *parts)


# ── Фігура 2: Стрибок часу (Step Jump) проти Розмазування (Leap Smear) ─────
def fig_kernel_step_vs_smear():
    W, H = 840, 480
    parts = []
    parts.append(text(W/2, 24, "Обробка високосної секунди: POSIX Step Jump проти Leap Smear", size=15, bold=True))

    mid_x = W / 2

    # Розділювальна лінія
    parts.append(line(mid_x, 50, mid_x, 460, color="#d0d7de", sw=1.5, dash="6,4"))

    # ЛІВА ПАНЕЛЬ: POSIX Step Jump (Дискретний стрибок / повтор)
    parts.append(fitbox(25, 52, 375, 40, "1. POSIX Step Jump (Повтор секунди)\nСтандартна поведінка ядра Linux / Unix", size=12, fill="#fdecea", stroke="#c0392b", color="#c0392b", bold=True))

    # Схема повтору секунд
    timeline_y = 150
    parts.append(line(40, timeline_y, 385, timeline_y, color=LINE, sw=1.5))
    parts.append(arrow(360, timeline_y, 390, timeline_y, color=LINE, sw=1.8))

    # Стовпчики часу
    steps = [
        ("23:59:58", 70, False),
        ("23:59:59", 145, True),
        ("23:59:59", 225, True), # повтор!
        ("00:00:00", 305, False),
        ("00:00:01", 365, False),
    ]

    for label, x_pos, is_dup in steps:
        parts.append(line(x_pos, timeline_y - 8, x_pos, timeline_y + 8, color="#c0392b" if is_dup else LINE, sw=2))
        parts.append(text(x_pos, timeline_y + 24, label, size=10, color="#c0392b" if is_dup else INK, bold=is_dup, anchor="middle"))

    # Дуга повернення назад
    parts.append(line(225, timeline_y - 12, 225, timeline_y - 30, color="#c0392b", sw=1.5))
    parts.append(line(225, timeline_y - 30, 145, timeline_y - 30, color="#c0392b", sw=1.5))
    parts.append(arrow(145, timeline_y - 30, 145, timeline_y - 14, color="#c0392b", sw=1.5))
    parts.append(text(185, timeline_y - 36, "Стрибок назад (−1 с)", size=10.5, color="#c0392b", bold=True))

    # Наслідки ліворуч
    bad_box = fitbox(25, 205, 375, 230,
        "Критичні наслідки для систем:\n"
        "• Порушення монотонності: t2 < t1 (clock_gettime)\n"
        "• Від'ємні інтервали в логах і транзакціях (Δt < 0)\n"
        "• Збій hrtimer/futex: таймери очікують абсолютного\n"
        "  дедлайну; після стрибка назад потрапляють у\n"
        "  нескінченний цикл негайного пробудження\n"
        "• 100% CPU lockup у JVM, MySQL, Hadoop (2012 р.)\n"
        "• Ризик розсинхронізації баз даних та кластерів",
        size=11, fill="#ffffff", stroke="#c0392b", color="#1a1a1a", pad=8)
    parts.append(bad_box)

    # ПРАВА ПАНЕЛЬ: Leap Smearing (Плавне розмазування)
    parts.append(fitbox(mid_x + 15, 52, 385, 40, "2. Leap Smear / Slew (Розмазування)\nТехнологія Google NTP, AWS, Cloudflare, Meta", size=12, fill="#eafaf1", stroke="#27ae60", color="#27ae60", bold=True))

    # Схема розмазування частоти
    smear_y = 150
    parts.append(line(mid_x + 30, smear_y, W - 30, smear_y, color=LINE, sw=1.5))
    parts.append(arrow(W - 50, smear_y, W - 25, smear_y, color=LINE, sw=1.8))

    # Плавний графік частоти
    parts.append(textbox(mid_x + 205, smear_y - 36, "Вікно 24 години: частота уповільнена на −11.57 ppm\n(1 секунда рівномірно розподіляється на 86 400 с)", size=10.5, pad=5, fill="#f4f6f8", stroke="#27ae60", color="#27ae60", bold=True)[0])

    smear_steps = [
        ("−12:00:00", mid_x + 55),
        ("00:00:00 UTC", mid_x + 205),
        ("+12:00:00", mid_x + 355),
    ]
    for label, x_pos in smear_steps:
        parts.append(line(x_pos, smear_y - 8, x_pos, smear_y + 8, color="#27ae60", sw=2))
        parts.append(text(x_pos, smear_y + 24, label, size=10.5, color="#27ae60", bold=True, anchor="middle"))

    # Наслідки праворуч
    good_box = fitbox(mid_x + 15, 205, 385, 230,
        "Переваги розмазування:\n"
        "• Сувора монотонність: час завжди зростає (t2 > t1)\n"
        "• Жодного стрибка дедлайнів у hrtimer та futex\n"
        "• Клієнтська ОС не знає про високосну секунду\n"
        "  (прапорець LI = 00 у відповідях NTP)\n"
        "• Відхилення частоти (11.6 ppm) непомітне для\n"
        "  більшості додатків і компенсується PLL\n"
        "• Повна стабільність високонавантажених сервісів",
        size=11, fill="#ffffff", stroke="#27ae60", color="#1a1a1a", pad=8)
    parts.append(good_box)

    render(os.path.join(IMG, "kernel-step-vs-smear.svg"), W, H, *parts)


# ── Фігура 3: Сигналізація високосної секунди (NTP та PTP) ─────────────────
def fig_ntp_ptp_leap_signaling():
    W, H = 840, 480
    parts = []
    parts.append(text(W/2, 24, "Сигналізація та поширення прапорців високосної секунди в мережі", size=15, bold=True))

    # Блок 1: Джерело (IERS Bulletin C & GNSS)
    b1 = fitbox(40, 55, 760, 46, "1. Міжнародна служба IERS (Bulletin C) та супутники GNSS (GPS/Galileo)\nПублікують повідомлення про подію за 6 місяців (IERS) або за тижні через навігаційні кадри (GNSS Δt_LS)", size=11.5, fill="#f4f6f8", stroke=LINE, color=INK, bold=True)
    parts.append(b1)
    parts.append(arrow(W/2, 101, W/2, 125, color=LINE, sw=1.5))

    # Блок 2: Сервери точного часу Stratum 1 / PTP Grandmaster
    b2 = fitbox(40, 125, 760, 52, "2. Первинні сервери синхронізації (NTP Stratum 1 / PTP Grandmaster Clock)\nВстановлюють прапорці сповіщення у заголовках мережевих пакетів за 24 години до настання події", size=11.5, fill="#eaf0fd", stroke="#2457d6", color="#2457d6", bold=True)
    parts.append(b2)
    parts.append(arrow(W/2, 177, W/2, 205, color=LINE, sw=1.5))

    # Блок 3: Два протоколи (NTP vs PTP)
    y3 = 205
    w_proto = 365
    b_ntp = fitbox(40, y3, w_proto, 115,
        "NTPv4 (RFC 5905) — поле Leap Indicator:\n"
        "• LI = 00 (0b00): нормальна робота (без стрибка)\n"
        "• LI = 01 (0b01): остання хвилина доби має 61 с (+1)\n"
        "• LI = 10 (0b10): остання хвилина доби має 59 с (−1)\n"
        "• LI = 11 (0b11): розсинхрон / стан тривоги",
        size=10.5, fill="#ffffff", stroke="#2457d6", color=INK, bold=False)

    b_ptp = fitbox(435, y3, w_proto, 115,
        "PTP (IEEE 1588) — прапорці повідомлень Announce:\n"
        "• leap61: прапорець додавання +1 с наприкінці доби\n"
        "• leap59: прапорець видалення 1 с наприкінці доби\n"
        "• currentUtcOffsetValid: чинність зсуву TAI−UTC\n"
        "• currentUtcOffset: поточний зсув (37 с)",
        size=10.5, fill="#ffffff", stroke="#27ae60", color=INK, bold=False)

    parts.extend([b_ntp, b_ptp])

    parts.append(arrow(40 + w_proto/2, y3 + 115, 40 + w_proto/2, 345, color=LINE, sw=1.5))
    parts.append(arrow(435 + w_proto/2, y3 + 115, 435 + w_proto/2, 345, color=LINE, sw=1.5))

    # Блок 4: Ядро операційної системи (Linux timex state machine)
    b4 = fitbox(40, 345, 760, 110,
        "4. Клієнтська операційна система (Ядро Linux та демон chrony / ntpd / ptp4l)\n"
        "• Системний виклик adjtimex(&tx) встановлює статус STA_INS у struct timex\n"
        "• Автомат станів ядра: TIME_OK → TIME_INS (очікування) → TIME_OOP (секунда 23:59:60) → TIME_WAIT → TIME_OK\n"
        "• У режимі Leap Smear прапорець LI скидається в 00, а ядро плавно підлаштовує частоту без переходу в TIME_OOP",
        size=10.5, fill="#fef5e7", stroke="#d35400", color="#d35400", bold=True)
    parts.append(b4)

    render(os.path.join(IMG, "ntp-ptp-leap-signaling.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_time_scales_divergence()
    fig_kernel_step_vs_smear()
    fig_ntp_ptp_leap_signaling()
    print("Figures generated successfully.")
