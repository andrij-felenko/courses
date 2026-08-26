# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. outdoor-attenuation-vegetation: Затухання 2.4 ГГц у рослинності та вологості ──────
def fig_outdoor_attenuation_vegetation():
    W, H = 940, 450
    p = []

    p.append(text(W / 2, 26, "Затухання 2.4 ГГц у рослинності та вплив вологості", size=16, color=INK, bold=True))

    x0, y0 = 90, 360
    xw, yh = 780, 270

    def sx(dist_m):
        return x0 + (dist_m / 250.0) * xw

    def sy(loss_db):
        return y0 - ((loss_db - 40.0) / 100.0) * yh

    # Сітка децибелів
    for l_db in [40, 60, 80, 100, 120, 140]:
        yy = sy(l_db)
        p.append(line(x0, yy, x0 + xw, yy, color="#e5e7eb", sw=1))
        p.append(text(x0 - 10, yy + 4, "%d дБ" % l_db, size=10, color=MUTED, anchor="end"))

    # Сітка дистанції
    for d_m in [0, 50, 100, 150, 200, 250]:
        xx = sx(d_m)
        p.append(line(xx, y0, xx, y0 - yh, color="#e5e7eb", sw=1))
        p.append(text(xx, y0 + 18, "%d м" % d_m, size=10, color=MUTED, anchor="middle"))

    p.append(line(x0, y0, x0 + xw, y0, color=LINE, sw=1.8))
    p.append(line(x0, y0, x0, y0 - yh, color=LINE, sw=1.8))
    p.append(text(x0 + xw, y0 + 32, "Відстань крізь поле / лісосмугу (м) →", size=11, color=INK, anchor="end", bold=True))
    p.append(text(x0 - 10, y0 - yh - 10, "Сумарні втрати сигналу (дБ) ↑", size=11, color=INK, anchor="start", bold=True))

    # Поріг чутливості Wi-Fi 802.11n MCS0 (-82 дБм при Tx = +18 дБм -> MAPL = 100 дБ)
    sens_loss = 100.0
    sens_y = sy(sens_loss)
    p.append(line(x0, sens_y, x0 + xw, sens_y, color=POS, sw=2, dash="6,4"))
    p.append(text(x0 + xw - 10, sens_y - 8, "Поріг обриву зв'язку Wi-Fi (MAPL ≈ 100 дБ)", size=11, color=POS, anchor="end", bold=True))

    # Крива 1: Чисте відкрите поле (Two-Ray Ground, пряма видимість)
    pts_free = []
    for d in range(10, 255, 10):
        if d < 72:
            loss = 20 * math.log10(d) + 40.0
        else:
            loss = 40 * math.log10(d) + 3.0
        if loss > 140:
            break
        pts_free.append((sx(d), sy(loss)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts_free), FIELD))
    p.append(text(sx(210), sy(40 * math.log10(210) + 3.0) - 10, "Пряма видимість (LOS)", size=11, color=FIELD, bold=True))

    # Крива 2: Сухий чагарник / поле кукурудзи (Weissberger: +0.55 дБ/м)
    pts_dry = []
    for d in range(10, 255, 10):
        fspl = 20 * math.log10(d) + 40.0
        veg = 0.55 * d
        loss = fspl + veg
        if loss > 140:
            pts_dry.append((sx(d), sy(140)))
            break
        pts_dry.append((sx(d), sy(loss)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="5,3"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts_dry), NEG))
    p.append(text(sx(95), sy(20 * math.log10(75) + 40.0 + 0.55 * 75) - 14, "Сухе листя (+0.55 дБ/м)", size=11, color=NEG, bold=True))

    # Крива 3: Мокре листя після дощу (ε_r=80, поглинання водою +1.75 дБ/м)
    pts_wet = []
    for d in range(10, 255, 10):
        fspl = 20 * math.log10(d) + 40.0
        veg = 1.75 * d
        loss = fspl + veg
        if loss > 140:
            pts_wet.append((sx(d), sy(140)))
            break
        pts_wet.append((sx(d), sy(loss)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts_wet), POS))
    p.append(text(sx(38), sy(20 * math.log10(28) + 40.0 + 1.75 * 28) - 14, "Мокре листя (+1.75 дБ/м)", size=11, color=POS, bold=True))

    # Пояснювальний блок (розміщений у чистому просторі вгорі праворуч)
    box_info, biw, bih = textbox(660, 110, "Фізика 2.4 ГГц у вологому середовищі:\n• Довжина хвилі λ = 12.5 см порівнянна з листям\n• Вода на листі (ε_r ≈ 80) утворює плівку-екран\n• 30 м мокрих заростей з'їдають понад 50 дБ!", size=10, pad=7, fill="#fff7ed", stroke="#f97316", sw=1.2)
    p.append(box_info)

    render(os.path.join(OUT, "outdoor-attenuation-vegetation.svg"), W, H, *p)


# ── 2. espnow-vs-standard-wifi-timing: Профіль часу та струму Wi-Fi проти ESP-NOW ──────
def fig_espnow_vs_standard_wifi_timing():
    W, H = 940, 420
    p = []

    p.append(text(W / 2, 26, "Часовий та енергетичний профіль: стандартний Wi-Fi проти ESP-NOW", size=16, color=INK, bold=True))

    # Секція 1: Стандартна Wi-Fi асоціація
    top_y = 60
    p.append(rect(40, top_y, 860, 140, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(60, top_y + 24, "Класичне Wi-Fi підключення (Холодний старт: Scan + Handshake + DHCP)", size=12, color=POS, bold=True, anchor="start"))

    # Фази Wi-Fi
    phases = [
        (60, 220, "1. Скан каналів 1..13\n(800 мс @ 110 мА)", "#fee2e2", "#ef4444"),
        (290, 140, "2. Probe / Auth\n(200 мс @ 140 мА)", "#fecaca", "#dc2626"),
        (440, 180, "3. 4-Way Handshake\n(350 мс @ 220 мА)", "#fca5a5", "#b91c1c"),
        (630, 160, "4. DHCP оренда IP\n(600 мс @ 130 мА)", "#fecaca", "#dc2626"),
        (800, 80, "Payload\n(50 мс)", "#bbf7d0", "#16a34a"),
    ]
    for px, pw, ptext, pfill, pstroke in phases:
        p.append(rect(px, top_y + 38, pw, 50, fill=pfill, stroke=pstroke, sw=1.2, rx=4))
        p.append(mtext(px + pw/2, top_y + 60, ptext, size=10, color=INK, bold=True))

    p.append(text(60, top_y + 115, "Сумарний час увімкненого радіо: ≈ 2000–3000 мс   |   Витрачений заряд: Q ≈ 350–450 мА·с (мКл)", size=11, color=POS, bold=True, anchor="start"))

    # Секція 2: ESP-NOW безз'єднувальний кадр
    bot_y = 230
    p.append(rect(40, bot_y, 860, 145, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(60, bot_y + 24, "ESP-NOW: безз'єднувальна передача сирого Action Frame (P2P без асоціації)", size=12, color=FIELD, bold=True, anchor="start"))

    enow_phases = [
        (60, 180, "1. Пробудження радіо\n(1.5 мс @ 80 мА)", "#dcfce7", "#22c55e"),
        (250, 240, "2. Action Frame TX + MAC ACK\n(2.5 мс @ 160 мА)", "#bbf7d0", "#16a34a"),
        (500, 180, "3. Перехід у Deep-Sleep\n(0.2 мс)", "#dcfce7", "#22c55e"),
    ]
    for px, pw, ptext, pfill, pstroke in enow_phases:
        p.append(rect(px, bot_y + 38, pw, 50, fill=pfill, stroke=pstroke, sw=1.2, rx=4))
        p.append(mtext(px + pw/2, bot_y + 60, ptext, size=10, color=INK, bold=True))

    p.append(text(60, bot_y + 115, "Сумарний час увімкненого радіо: ≈ 4.0–4.5 мс   |   Витрачений заряд: Q ≈ 0.6 мА·с (мКл)", size=11, color=FIELD, bold=True, anchor="start"))

    # Порівняльний висновок
    cmp_box, cw, ch = textbox(770, bot_y + 70, "Економія заряду\nв 600–700 разів!\nБатарея служить\nроками замість днів", size=10, pad=6, fill="#ecfdf5", stroke=FIELD, sw=1.5, color="#065f46", bold=True)
    p.append(cmp_box)

    render(os.path.join(OUT, "espnow-vs-standard-wifi-timing.svg"), W, H, *p)


# ── 3. fast-connect-rtc-flow: Архітектура Fast Connect через RTC SRAM ──────
def fig_fast_connect_rtc_flow():
    W, H = 940, 420
    p = []

    p.append(text(W / 2, 26, "Архітектура Fast Connect через збереження параметрів у RTC Slow Memory", size=16, color=INK, bold=True))

    # Блок 1: Перший старт (Cold Boot)
    b1_x, b1_y, b1_w, b1_h = 60, 70, 240, 160
    p.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(b1_x + b1_w/2, b1_y + 22, "1. Холодний старт", size=12, color=NEG, bold=True))
    p.append(mtext(b1_x + b1_w/2, b1_y + 55, "• Повний скан ефіру\n• Повне WPA2 PBKDF2\n• DHCP отримання IP\n• Тривалість: 2.5–4.0 с", size=10, color=INK))

    # Стрілка збереження в RTC
    p.append(arrow(b1_x + b1_w, b1_y + 80, b1_x + b1_w + 50, b1_y + 80, color=LINE, sw=1.8))
    p.append(text(b1_x + b1_w + 25, b1_y + 68, "Збереження", size=10, color=MUTED))

    # Блок 2: RTC Slow Memory (Енергонезалежна в Deep-Sleep)
    b2_x, b2_y, b2_w, b2_h = 360, 55, 220, 210
    p.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#fef9c3", stroke="#ca8a04", sw=2, rx=6))
    p.append(text(b2_x + b2_w/2, b2_y + 24, "RTC Slow Memory / SRAM", size=12, color="#854d0e", bold=True))
    p.append(mtext(b2_x + b2_w/2, b2_y + 60, "Кешовані параметри:\n[1] BSSID точки (6 байт)\n[2] Номер каналу (1..13)\n[3] PMKID / PMKSA кеш\n[4] Статична IP-конфігурація\n(IP, шлюз, маска, DNS)", size=10, color=INK, bold=True))
    p.append(rect(b2_x + 15, b2_y + 160, b2_w - 30, 35, fill="#fef08a", stroke="#ca8a04", sw=1, rx=4))
    p.append(text(b2_x + b2_w/2, b2_y + 182, "Живиться в Deep-Sleep (<10 мкА)", size=9, color="#854d0e", italic=True))

    # Стрілка відновлення
    p.append(arrow(b2_x + b2_w, b1_y + 80, b2_x + b2_w + 50, b1_y + 80, color=FIELD, sw=2))
    p.append(text(b2_x + b2_w + 25, b1_y + 68, "Fast Init", size=10, color=FIELD, bold=True))

    # Блок 3: Швидке пробудження (Fast Connect)
    b3_x, b3_y, b3_w, b3_h = 640, 70, 240, 160
    p.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(b3_x + b3_w/2, b3_y + 22, "2. Пробудження з Deep-Sleep", size=12, color=FIELD, bold=True))
    p.append(mtext(b3_x + b3_w/2, b3_y + 55, "• Прямий вибір каналу\n• Миттєва асоціація BSSID\n• PMKSA без PBKDF2\n• Статичний IP (без DHCP)\n• Час до UDP: 80–120 мс!", size=10, color=INK, bold=True))

    # Нижній таймлайн циклу сенсора
    p.append(rect(60, 300, 820, 85, fill="#f8fafc", stroke=LINE, sw=1.3, rx=6))
    p.append(text(470, 322, "Цикл автономного польового вузла:", size=11, color=INK, bold=True))

    # Кроки циклу
    c_steps = [
        (80, 160, "Deep-Sleep 10 хв\n(I = 12 мкА)", "#f1f5f9", LINE),
        (260, 170, "Пробудження + Замір\n(15 мс @ 25 мА)", "#e0e7ff", NEG),
        (450, 210, "Fast Connect + UDP TX\n(90 мс @ 150 мА)", "#dcfce7", FIELD),
        (680, 180, "Засинання в RTC\n(5 мс @ 15 мА)", "#f1f5f9", LINE),
    ]
    for cx, cw, ctext, cfill, cstroke in c_steps:
        p.append(rect(cx, 335, cw, 38, fill=cfill, stroke=cstroke, sw=1.2, rx=4))
        p.append(mtext(cx + cw/2, 350, ctext, size=9, color=INK, bold=True))

    render(os.path.join(OUT, "fast-connect-rtc-flow.svg"), W, H, *p)


# ── 4. halow-subghz-spectrum-range: Wi-Fi HaLow (802.11ah) проти Wi-Fi 2.4 ГГц ──────
def fig_halow_subghz_spectrum_range():
    W, H = 940, 410
    p = []

    p.append(text(W / 2, 26, "Wi-Fi HaLow (IEEE 802.11ah Sub-GHz) проти стандартного Wi-Fi (802.11n 2.4 ГГц)", size=16, color=INK, bold=True))

    # Ліва колонка: Wi-Fi 2.4 ГГц
    w_x, w_y, col_w, col_h = 60, 65, 380, 310
    p.append(rect(w_x, w_y, col_w, col_h, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(w_x + col_w/2, w_y + 26, "Стандартний Wi-Fi (802.11b/g/n 2.4 ГГц)", size=13, color=POS, bold=True))

    w_items = [
        ("Несуча частота:", "2.412–2.472 ГГц (λ ≈ 12.5 см)"),
        ("Ширина каналу:", "20 МГц або 40 МГц (OFDM)"),
        ("Шумова підлога:", "−101 дБм (широка смуга 20 МГц)"),
        ("Чутливість (MCS0):", "−82 дБм (пор. чутливість)"),
        ("Енергобюджет MAPL:", "≈ 100–103 дБ (+18 дБм Tx)"),
        ("Дальність у полі:", "70–150 м (пряма видимість)"),
        ("Проникнення листя:", "Критичне затухання (−1.8 дБ/м у росі)"),
    ]
    for i, (k, v) in enumerate(w_items):
        yy = w_y + 60 + i * 33
        p.append(text(w_x + 15, yy, k, size=10, color=MUTED, anchor="start", bold=True))
        p.append(text(w_x + col_w - 15, yy, v, size=10, color=INK, anchor="end"))

    # Права колонка: Wi-Fi HaLow (802.11ah)
    h_x = 500
    p.append(rect(h_x, w_y, col_w, col_h, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(h_x + col_w/2, w_y + 26, "Wi-Fi HaLow (IEEE 802.11ah Sub-1GHz)", size=13, color=FIELD, bold=True))

    h_items = [
        ("Несуча частота:", "868 МГц (ЄС) / 915 МГц (США) (λ ≈ 34.5 см)"),
        ("Ширина каналу:", "1 МГц / 2 МГц / 4 МГц / 8 МГц"),
        ("Шумова підлога:", "−114 дБм (вузька смуга 1 МГц)"),
        ("Чутливість (MCS10):", "−109 дБм (BPSK + 2x Repetition)"),
        ("Енергобюджет MAPL:", "≈ 130–135 дБ (+20 дБм Tx)"),
        ("Дальність у полі:", "1000–1500 м (> 1 км у полі!)"),
        ("Проникнення листя:", "Висока огинаюча здатність (Sub-GHz)"),
    ]
    for i, (k, v) in enumerate(h_items):
        yy = w_y + 60 + i * 33
        p.append(text(h_x + 15, yy, k, size=10, color=MUTED, anchor="start", bold=True))
        p.append(text(h_x + col_w - 15, yy, v, size=10, color=INK, anchor="end", bold=True))

    render(os.path.join(OUT, "halow-subghz-spectrum-range.svg"), W, H, *p)


# ── 5. outdoor-antenna-patterns-protection: Антени та грозозахист у полі ──────
def fig_outdoor_antenna_patterns_protection():
    W, H = 940, 430
    p = []

    p.append(text(W / 2, 26, "Польовий антенний тракт: вибір діаграми спрямованості та грозозахист", size=16, color=INK, bold=True))

    # Ліва частина: Типи антен
    ant_x = 50
    p.append(rect(ant_x, 60, 420, 335, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(text(ant_x + 210, 86, "Типи польових антен для Wi-Fi", size=13, color=INK, bold=True))

    ants = [
        (ant_x + 20, 110, "1. Штирьовий диполь / колінеар (Dipole)", "Всеспрямована 360° по горизонту (+2..+5 дБі).\nСтискає вертикальну пелюстку: при нахилі щогли лінк зникає!"),
        (ant_x + 20, 185, "2. Патч-антена (Microstrip Panel)", "Секторна 60°..90° (+8..+14 дБі).\nКомпактна, стійка до вітру, для базових станцій на межі поля."),
        (ant_x + 20, 260, "3. Хвильовий канал (Yagi-Uda)", "Гостроспрямована 25°..40° (+12..+18 дБі).\nМаксимальна дальність для фіксованих точкових радіомостів."),
    ]
    for ax, ay, atitle, adesc in ants:
        p.append(rect(ax, ay, 380, 60, fill="#ffffff", stroke=LINE, sw=1, rx=4))
        p.append(text(ax + 10, ay + 18, atitle, size=11, color=NEG, bold=True, anchor="start"))
        p.append(mtext(ax + 10, ay + 36, adesc, size=9.5, color=INK, anchor="start"))

    # Права частина: Схема монтажу та грозозахисту
    sch_x = 500
    p.append(rect(sch_x, 60, 390, 335, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(sch_x + 195, 86, "Схема захисту від атмосферної статики", size=13, color=FIELD, bold=True))

    # Щогла
    mast_x = sch_x + 60
    p.append(line(mast_x, 110, mast_x, 360, color="#4b5563", sw=5))
    p.append(text(mast_x - 12, 340, "Щогла", size=10, color=MUTED, anchor="end"))

    # Антена на верхівці
    p.append(line(mast_x, 110, mast_x, 90, color=POS, sw=3))
    p.append(circle(mast_x, 85, 4, fill=POS, stroke="#ffffff", sw=1.5))
    p.append(text(mast_x + 12, 90, "Антена (DC-Grounded)", size=10, color=POS, bold=True, anchor="start"))

    # Грозорозрядник GDT
    gdt_y = 150
    p.append(rect(mast_x + 10, gdt_y - 12, 45, 24, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    p.append(text(mast_x + 32, gdt_y + 4, "GDT", size=10, color=POS, bold=True))
    p.append(line(mast_x, 110, mast_x + 10, gdt_y, color=LINE, sw=2))

    # Шина заземлення
    p.append(line(mast_x + 32, gdt_y + 12, mast_x + 32, 360, color="#d97706", sw=3, dash="4,2"))
    p.append(line(mast_x + 20, 360, mast_x + 44, 360, color="#d97706", sw=3))
    p.append(line(mast_x + 24, 366, mast_x + 40, 366, color="#d97706", sw=2.5))
    p.append(line(mast_x + 28, 372, mast_x + 36, 372, color="#d97706", sw=2))
    p.append(text(mast_x + 50, 365, "Контур заземлення (PE)\nмідна шина ≥16 мм²", size=9.5, color="#b45309", bold=True, anchor="start"))

    # Гермобокс біля антени
    box_y = 210
    p.append(rect(mast_x + 70, box_y, 140, 95, fill="#f8fafc", stroke=LINE, sw=1.5, rx=5))
    p.append(text(mast_x + 140, box_y + 20, "Гермобокс IP67", size=11, color=INK, bold=True))
    p.append(mtext(mast_x + 140, box_y + 42, "ESP32 / Wi-Fi вузол\n(Фідер < 0.5 м LMR-195)\n\nВниз іде лише дріт\nживлення / PoE / RS-485", size=9.5, color=INK))

    p.append(line(mast_x + 55, gdt_y, mast_x + 70, box_y + 30, color=LINE, sw=2))

    render(os.path.join(OUT, "outdoor-antenna-patterns-protection.svg"), W, H, *p)


if __name__ == "__main__":
    fig_outdoor_attenuation_vegetation()
    fig_espnow_vs_standard_wifi_timing()
    fig_fast_connect_rtc_flow()
    fig_halow_subghz_spectrum_range()
    fig_outdoor_antenna_patterns_protection()
    print("Generated 5 figures successfully.")
