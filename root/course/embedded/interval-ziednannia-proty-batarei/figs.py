# -*- coding: utf-8 -*-
import sys, os

# 4 levels up to root/scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. ble-connection-timing.svg ─────────────────────────────────────────────
def fig_connection_timing():
    W, H = 940, 430
    p = []

    # Фон діаграми
    p.append(rect(20, 20, 900, 390, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))

    # Заголовок та легенда
    p.append(text(470, 48, "Часова анатомія з'єднання BLE: Connection Interval, Slave Latency та Supervision Timeout", size=15, color=INK, bold=True))

    # Вісь часу
    p.append(line(50, 220, 890, 220, color=LINE, sw=1.5))
    p.append(arrow(870, 220, 905, 220, color=LINE, sw=1.8))
    p.append(text(905, 238, "Час (t)", size=12, color=INK, bold=True, anchor="end"))

    # Позначення анкерних точок A0, A1, A2, A3, A4
    anchors = [
        (80, "A0 (Подія #0)", True, "Активний обмін"),
        (240, "A1 (Подія #1)", False, "Пропуск (Slave Latency)"),
        (400, "A2 (Подія #2)", False, "Пропуск (Slave Latency)"),
        (560, "A3 (Подія #3)", False, "Пропуск (Slave Latency)"),
        (720, "A4 (Подія #4)", True, "Спрацювання Latency / Подія")
    ]

    for x, label, is_active, desc in anchors:
        # Вертикальна лінія анкерної точки
        p.append(line(x, 90, x, 310, color="#94a3b8", sw=1, dash="4 4"))
        p.append(circle(x, 220, 4, fill=POS if is_active else MUTED, stroke=LINE, sw=1.2))
        p.append(text(x, 80, label, size=11, color=INK, bold=True))

        if is_active:
            # Пакет Master (Центральний)
            p.append(rect(x + 5, 140, 50, 35, fill="#dbeafe", stroke=NEG, sw=1.5, rx=4))
            p.append(text(x + 30, 162, "Central", size=11, color=NEG, bold=True))

            # IFS (150 мкс)
            p.append(rect(x + 57, 150, 16, 15, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=2))
            p.append(text(x + 65, 142, "IFS", size=9, color=MUTED))

            # Пакет Slave (Периферія)
            p.append(rect(x + 75, 175, 50, 35, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
            p.append(text(x + 100, 197, "Peripheral", size=11, color=POS, bold=True))

            # Радіо увімкнене
            p.append(rect(x + 2, 235, 126, 26, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
            p.append(text(x + 65, 252, "Радіо активне (~1.5 мс)", size=10, color=FIELD, bold=True))
        else:
            # Сон периферії
            p.append(rect(x + 5, 235, 145, 26, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
            p.append(text(x + 77, 252, "Глибокий сон (1.5–2.5 мкА)", size=10, color=MUTED, italic=True))

    # Вимірні стрілки для Connection Interval
    p.append(line(80, 290, 240, 290, color=NEG, sw=1.5))
    p.append(line(80, 283, 80, 297, color=NEG, sw=1.5))
    p.append(line(240, 283, 240, 297, color=NEG, sw=1.5))
    p.append(text(160, 308, "Connection Interval (T_CI = 7.5 мс .. 4.0 с)", size=11, color=NEG, bold=True))

    # Вимірна стрілка для Slave Latency (3 події)
    p.append(line(240, 335, 720, 335, color=POS, sw=1.5))
    p.append(line(240, 328, 240, 342, color=POS, sw=1.5))
    p.append(line(720, 328, 720, 342, color=POS, sw=1.5))
    p.append(text(480, 353, "Slave Latency = 3 пропущені події", size=11, color=POS, bold=True))

    # Ефективний інтервал
    p.append(line(80, 380, 720, 380, color=FIELD, sw=1.5))
    p.append(line(80, 373, 80, 387, color=FIELD, sw=1.5))
    p.append(line(720, 373, 720, 387, color=FIELD, sw=1.5))
    p.append(text(400, 398, "Ефективний інтервал T_eff = T_CI · (1 + Slave Latency)", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, "ble-connection-timing.svg"), W, H, *p,
           title="Часова анатомія з'єднання BLE")


# ── 2. ble-event-current-profile.svg ─────────────────────────────────────────
def fig_current_profile():
    W, H = 940, 460
    p = []

    p.append(rect(20, 20, 900, 420, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(470, 48, "Осцилограма струму події з'єднання (Connection Event) за фазами мікроконтролера", size=15, color=INK, bold=True))

    # Сітка та осі графіка
    p.append(rect(80, 75, 800, 270, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))

    for y_val, i_txt in [(325, "0 мА"), (275, "3 мА"), (215, "7 мА"), (155, "11 мА"), (95, "15 мА")]:
        p.append(line(80, y_val, 880, y_val, color="#f1f5f9", sw=1, dash="3 3"))
        p.append(text(72, y_val + 4, i_txt, size=11, color=MUTED, anchor="end"))

    # Осі
    p.append(arrow(80, 325, 885, 325, color=LINE, sw=1.5))
    p.append(arrow(80, 325, 80, 70, color=LINE, sw=1.5))
    p.append(text(880, 342, "Час (мкс)", size=11, color=INK, bold=True, anchor="end"))
    p.append(text(65, 62, "Струм I (мА)", size=11, color=INK, bold=True, anchor="end"))

    # Форма хвилі (багатокутник/ламані)
    # Сон: 80..130 (y=324, 2 мкА)
    # Wakeup & HFXO: 130->150 (y=290, 2.5 мА), 150..270 (y=280..270, 3 мА)
    # Radio Ramp-up: 270->300 (y=225, 6.5 мА)
    # RX Window: 300..450 (y=210, 7.5 мА)
    # IFS: 450..550 (y=265, 4.0 мА)
    # TX Burst: 550..700 (y=130, 12.5 мА)
    # Ramp-down & Post-proc: 700..770 (y=280, 2.8 мА)
    # Sleep floor: 770..870 (y=324, 2 мкА)

    pts = [
        (80, 324), (130, 324),
        (145, 285), (270, 280),
        (295, 225), (450, 215),
        (470, 265), (545, 265),
        (560, 130), (695, 130),
        (710, 280), (765, 285),
        (775, 324), (870, 324)
    ]

    # Заливка інтеграла заряду (площа під кривою)
    poly_pts = " ".join(["%.1f,%.1f" % pt for pt in pts]) + " 870,325 80,325"
    p.append(f'<polygon points="{poly_pts}" fill="#eff6ff" stroke="none"/>')

    # Контур сигналу
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        p.append(line(x1, y1, x2, y2, color=POS, sw=2.5))

    # Вертикальні роздільники фаз
    phases = [
        (130, 270, "1. Пробудження та HFXO\n~300 мкс (2.5–3 мА)", "#3b82f6"),
        (270, 300, "2. Ramp-up\n~100 мкс", "#6366f1"),
        (300, 450, "3. Прийом RX (Central)\n~150–300 мкс (~7.5 мА)", "#0284c7"),
        (450, 550, "4. IFS\n150 мкс", "#64748b"),
        (550, 700, "5. Передача TX (Відповідь)\n~150–1500 мкс (~12.5 мА)", "#dc2626"),
        (700, 770, "6. Пост-обробка\n~70 мкс", "#059669")
    ]

    for x_start, x_end, label, col in phases:
        p.append(line(x_start, 75, x_start, 325, color="#cbd5e1", sw=1, dash="2 2"))

    p.append(line(770, 75, 770, 325, color="#cbd5e1", sw=1, dash="2 2"))

    # Пояснювальні плашки фаз внизу
    bx1, _, _ = textbox(200, 375, "1. Пробудження RTC + HFXO\n(32 МГц кварц, ~3 мА)", size=10, fill="#eff6ff", stroke="#3b82f6")
    bx2, _, _ = textbox(375, 375, "3. Вікно прийому RX\n(LNA + демодулятор)", size=10, fill="#f0f9ff", stroke="#0284c7")
    bx3, _, _ = textbox(625, 375, "5. Випромінювання TX\n(Підсилювач PA, 0..+4 dBm)", size=10, fill="#fef2f2", stroke="#dc2626")
    bx4, _, _ = textbox(810, 375, "7. Глибокий сон\n(RTC, 1.5–2.5 мкА)", size=10, fill="#f8fafc", stroke=MUTED)

    p.extend([bx1, bx2, bx3, bx4])

    # Інтеграл заряду напис
    p.append(rect(430, 95, 230, 40, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(545, 112, "Заряд події Q_event = ∫ i(t) dt", size=11, color=POS, bold=True))
    p.append(text(545, 127, "Q_event ≈ 10 .. 25 мкКл (мкА·с)", size=10, color=MUTED))

    render(os.path.join(OUT, "ble-event-current-profile.svg"), W, H, *p,
           title="Профіль струму події з'єднання BLE")


# ── 3. ios-android-parameter-rules.svg ───────────────────────────────────────
def fig_os_rules():
    W, H = 940, 440
    p = []

    p.append(rect(20, 20, 900, 400, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(470, 48, "Вимоги мобільних ОС до параметрів з'єднання BLE (iOS проти Android)", size=15, color=INK, bold=True))

    # Ліва колонка: Apple iOS Accessory Design Guidelines
    p.append(rect(40, 75, 415, 325, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    p.append(rect(40, 75, 415, 38, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(247, 99, "Apple iOS (Accessory Design Guidelines)", size=13, color=NEG, bold=True))

    ios_rules = [
        "1. connIntervalMin ≥ 15 мс (для HID ≥ 11.25 мс)",
        "2. connIntervalMax ≥ connIntervalMin + 15 мс",
        "3. connIntervalMax є кратним 15 мс (15, 30, 45, 60...)",
        "4. Slave Latency ≤ 30 пропущених подій",
        "5. Supervision Timeout ≤ 6000 мс (6.0 секунд)",
        "6. connIntervalMax · (1 + Slave Latency) ≤ 2000 мс",
        "7. Timeout ≥ connIntervalMax · (1 + Slave Latency) · 3",
        "Порушення хоч одного правила → відхилення L2CAP"
    ]

    for i, r_txt in enumerate(ios_rules):
        col = POS if i == 7 else INK
        bold_flag = True if i == 7 else False
        p.append(text(55, 135 + i * 23, r_txt, size=11, color=col, anchor="start", bold=bold_flag))

    # Права колонка: Google Android Bluetooth Stack
    p.append(rect(485, 75, 415, 325, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(rect(485, 75, 415, 38, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(692, 99, "Google Android (BluetoothGatt Priority)", size=13, color=FIELD, bold=True))

    p.append(text(500, 132, "Рівні requestConnectionPriority():", size=11, color=INK, anchor="start", bold=True))

    # Таблиця 3 рівнів Android
    android_tiers = [
        ("HIGH (Висока швидкість)", "Interval: 11.25–15 мс | Latency: 0", "Для передачі файлів та OTA DFU", "#dbeafe", NEG),
        ("BALANCED (Збалансований)", "Interval: 30–50 мс | Latency: 0", "Типовий режим після підключення", "#f1f5f9", INK),
        ("LOW_POWER (Енергоощадний)", "Interval: 100–125 мс | Latency: 2", "Для рідкісного опитування датчиків", "#dcfce7", FIELD)
    ]

    for i, (name, params, desc, bg_c, t_c) in enumerate(android_tiers):
        y_b = 150 + i * 56
        p.append(rect(500, y_b, 385, 50, fill=bg_c, stroke="#cbd5e1", sw=1, rx=4))
        p.append(text(510, y_b + 17, name, size=11, color=t_c, anchor="start", bold=True))
        p.append(text(510, y_b + 32, params, size=10, color=INK, anchor="start"))
        p.append(text(510, y_b + 44, desc, size=9, color=MUTED, anchor="start", italic=True))

    p.append(text(500, 335, "⚠️ Фрагментація вендорів:", size=11, color=POS, anchor="start", bold=True))
    p.append(text(500, 353, "Samsung, Xiaomi та Huawei можуть накладати власні", size=10, color=MUTED, anchor="start"))
    p.append(text(500, 368, "обмеження енергозбереження та затримувати L2CAP оновлення.", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "ios-android-parameter-rules.svg"), W, H, *p,
           title="Вимоги iOS та Android до параметрів BLE")


# ── 4. cr2032-lifetime-vs-interval.svg ───────────────────────────────────────
def fig_battery_lifetime():
    W, H = 940, 440
    p = []

    p.append(rect(20, 20, 900, 400, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(470, 48, "Термін автономної роботи від CR2032 (225 мА·год) та просідання напруги", size=15, color=INK, bold=True))

    # Лівий графік: Тривалість життя від інтервалу
    p.append(rect(50, 75, 410, 260, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(255, 96, "Розрахунковий час життя батареї", size=12, color=INK, bold=True))

    # Осі
    p.append(arrow(90, 305, 435, 305, color=LINE, sw=1.5))
    p.append(arrow(90, 305, 90, 105, color=LINE, sw=1.5))
    p.append(text(435, 322, "Interval (мс)", size=10, color=INK, bold=True, anchor="end"))
    p.append(text(80, 100, "Роки", size=10, color=INK, bold=True, anchor="end"))

    # Сітка
    for y_v, yr_txt in [(305, "0"), (255, "1 р."), (205, "2 р."), (155, "3 р."), (115, "4 р.")]:
        p.append(line(90, y_v, 430, y_v, color="#f1f5f9", sw=1, dash="2 2"))
        p.append(text(82, y_v + 4, yr_txt, size=9, color=MUTED, anchor="end"))

    # Крива Latency = 0 (червона)
    p.append(line(100, 303, 140, 295, color=POS, sw=2))
    p.append(line(140, 295, 200, 280, color=POS, sw=2))
    p.append(line(200, 280, 300, 250, color=POS, sw=2))
    p.append(line(300, 250, 420, 210, color=POS, sw=2))
    p.append(text(380, 200, "Slave Latency = 0", size=10, color=POS, bold=True))

    # Крива Latency = 4 (синя)
    p.append(line(100, 295, 140, 270, color=NEG, sw=2))
    p.append(line(140, 270, 200, 235, color=NEG, sw=2))
    p.append(line(200, 235, 300, 180, color=NEG, sw=2))
    p.append(line(300, 180, 420, 145, color=NEG, sw=2))
    p.append(text(380, 138, "Slave Latency = 4", size=10, color=NEG, bold=True))

    # Крива Latency = 19 (зелена)
    p.append(line(100, 275, 140, 220, color=FIELD, sw=2))
    p.append(line(140, 220, 200, 170, color=FIELD, sw=2))
    p.append(line(200, 170, 300, 135, color=FIELD, sw=2))
    p.append(line(300, 135, 420, 120, color=FIELD, sw=2))
    p.append(text(330, 115, "Latency = 19 (Стеля ~4.5 роки)", size=10, color=FIELD, bold=True))

    # Правий блок: Фізика ESR та буферний конденсатор
    p.append(rect(480, 75, 420, 260, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(690, 96, "Імпульсне просідання напруги (ESR батареї)", size=12, color=INK, bold=True))

    p.append(rect(495, 115, 390, 50, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    p.append(text(505, 133, "Без буферного конденсатора (C_bulk = 0):", size=10, color=POS, anchor="start", bold=True))
    p.append(text(505, 150, "ΔV = I_peak · R_int = 15 мА · 100 Ом = 1.5 В → Brownout Reset!", size=10, color=INK, anchor="start"))

    p.append(rect(495, 175, 390, 50, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(505, 193, "З буферним конденсатором C_bulk = 47..100 мкФ:", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(505, 210, "ΔV_cap = Q_event / C_bulk = 20 мкКл / 47 мкФ ≈ 0.42 В (Безпечно)", size=10, color=INK, anchor="start"))

    p.append(rect(495, 235, 390, 85, fill="#f8fafc", stroke="#94a3b8", sw=1, rx=4))
    p.append(text(505, 252, "Фактори скорочення ємності CR2032:", size=10, color=INK, anchor="start", bold=True))
    p.append(text(505, 269, "• Саморозряд: ~1.0–1.5% на рік (еквівалентно ~0.4 мкА постійно)", size=9, color=MUTED, anchor="start"))
    p.append(text(505, 284, "• Зростання ESR при розряді: від 15 Ом (нова) до 200–300+ Ом (стара)", size=9, color=MUTED, anchor="start"))
    p.append(text(505, 299, "• Падіння ємності за низьких температур (0 °C втрачає до 40% заряду)", size=9, color=MUTED, anchor="start"))

    # Підсумкова плашка
    bx_sum, _, _ = textbox(470, 380, "Головне правило: високий Slave Latency (10–25) дає 3–5 років роботи,\nзберігаючи миттєвий відгук (<50 мс) при надсиланні даних з боку периферії.", size=11, fill="#eff6ff", stroke=NEG, bold=True)
    p.append(bx_sum)

    render(os.path.join(OUT, "cr2032-lifetime-vs-interval.svg"), W, H, *p,
           title="Термін служби батареї CR2032")


def main():
    fig_connection_timing()
    fig_current_profile()
    fig_os_rules()
    fig_battery_lifetime()
    print("All 4 figures generated successfully in img/")


if __name__ == "__main__":
    main()
