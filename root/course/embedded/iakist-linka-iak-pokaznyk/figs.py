# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. rssi-vs-snr-noise-floor: чистий ефір проти завади ───────────────────────
def fig_rssi_vs_snr():
    W, H = 880, 450
    p = []

    # Заголовок зверху
    p.append(text(W / 2, 28, "RSSI проти SNR: чому рівень сигналу без шумового порогу не гарантує зв'язок", size=15, bold=True))

    pw, ph = 390, 360
    p1_x, p2_x = 35, 455
    py = 55

    # Базова лінія стовпчиків (низ шкали -130 дБм)
    y_base = py + ph - 85

    def y_dbm(v):
        # -130 дБм -> y_base, -40 дБм -> py + 60
        # діапазон 90 дБм на висоту y_base - (py + 60)
        h_range = y_base - (py + 60)
        return y_base - (v + 130) * (h_range / 90.0)

    # Панель 1: Чистий ефір
    p.append(rect(p1_x, py, pw, ph, fill="#f6fbf7", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(p1_x + pw / 2, py + 26, "Сценарій А: Чистий ефір (далека дистанція)", size=13, color=FIELD, bold=True))

    for dbm in [-120, -100, -80, -60]:
        yy = y_dbm(dbm)
        p.append(line(p1_x + 70, yy, p1_x + pw - 20, yy, color="#d8e6dc", sw=1, dash="3,3"))
        p.append(text(p1_x + 62, yy + 4, "%d дБм" % dbm, size=10, color=MUTED, anchor="end"))

    # Рівні А (-90 дБм і -115 дБм)
    y_sig_a = y_dbm(-90)
    y_noise_a = y_dbm(-115)

    p.append(rect(p1_x + 95, y_sig_a, 60, y_base - y_sig_a, fill="#d5e8d4", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(p1_x + 125, y_sig_a - 8, "-90 дБм", size=10.5, color=FIELD, bold=True))
    p.append(text(p1_x + 125, y_base + 18, "RSSI", size=11, color=INK, bold=True))

    p.append(rect(p1_x + 185, y_noise_a, 60, y_base - y_noise_a, fill="#eaeaea", stroke="#888888", sw=1.5, rx=4))
    p.append(text(p1_x + 215, y_noise_a - 8, "-115 дБм", size=10.5, color=MUTED, bold=True))
    p.append(text(p1_x + 215, y_base + 18, "Шум", size=11, color=MUTED, bold=True))

    # Стрілка запасу SNR
    p.append(arrow(p1_x + 275, y_noise_a, p1_x + 275, y_sig_a, color=FIELD, sw=2))
    p.append(text(p1_x + 330, (y_sig_a + y_noise_a) / 2 + 4, "SNR = +25 дБ", size=11, color=FIELD, bold=True))

    # Результат А
    p.append(rect(p1_x + 20, py + ph - 55, pw - 40, 40, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(p1_x + pw / 2, py + ph - 30, "Результат: 100% декодування (LQ 100%)", size=11, color=FIELD, bold=True))


    # Панель 2: Сильна завада
    p.append(rect(p2_x, py, pw, ph, fill="#fdf6f5", stroke=POS, sw=1.5, rx=8))
    p.append(text(p2_x + pw / 2, py + 26, "Сценарій Б: Сильна завада (близька дистанція)", size=13, color=POS, bold=True))

    for dbm in [-120, -100, -80, -60]:
        yy = y_dbm(dbm)
        p.append(line(p2_x + 70, yy, p2_x + pw - 20, yy, color="#edd8d5", sw=1, dash="3,3"))
        p.append(text(p2_x + 62, yy + 4, "%d дБм" % dbm, size=10, color=MUTED, anchor="end"))

    # Рівні Б (-65 дБм і -58 дБм)
    y_sig_b = y_dbm(-65)
    y_noise_b = y_dbm(-58)

    p.append(rect(p2_x + 95, y_sig_b, 60, y_base - y_sig_b, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    p.append(text(p2_x + 125, y_sig_b - 8, "-65 дБм", size=10.5, color=POS, bold=True))
    p.append(text(p2_x + 125, y_base + 18, "RSSI", size=11, color=INK, bold=True))

    p.append(rect(p2_x + 185, y_noise_b, 60, y_base - y_noise_b, fill="#fadbd8", stroke=POS, sw=1.8, rx=4))
    p.append(text(p2_x + 215, y_noise_b - 8, "-58 дБм", size=10.5, color=POS, bold=True))
    p.append(text(p2_x + 215, y_base + 18, "Шум", size=11, color=POS, bold=True))

    # Стрілка від'ємного SNR
    p.append(arrow(p2_x + 275, y_sig_b, p2_x + 275, y_noise_b, color=POS, sw=2))
    p.append(text(p2_x + 330, (y_sig_b + y_noise_b) / 2 + 4, "SNR = -7 дБ", size=11, color=POS, bold=True))

    # Результат Б
    p.append(rect(p2_x + 20, py + ph - 55, pw - 40, 40, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    p.append(text(p2_x + pw / 2, py + ph - 30, "Результат: 0% декодування (сигнал під шумом)", size=10.5, color=POS, bold=True))

    render(os.path.join(OUT, "rssi-vs-snr-noise-floor.svg"), W, H, *p,
           title="RSSI та SNR: порівняння чистого каналу із зашумленим")


# ── 2. lq-rolling-window: рухоме вікно LQ ──────────────────────────────────────
def fig_lq_rolling_window():
    W, H = 860, 370
    p = []

    p.append(text(W / 2, 26, "Обчислення Link Quality (LQ) у рухомому кільцевому буфері", size=15, bold=True))

    p.append(text(45, 62, "Потік очікуваних пакетів (кожні 10 мс для 100 Гц):", size=12, color=INK, anchor="start", bold=True))

    slots_x = 45
    slots_y = 76
    slot_w = 35
    slot_h = 48

    stream = [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1]
    
    for i, ok in enumerate(stream):
        sx = slots_x + i * (slot_w + 4)
        fill = "#eef6ef" if ok else "#fdecea"
        stroke = FIELD if ok else POS
        sym = "✓" if ok else "✗"
        col = FIELD if ok else POS
        p.append(rect(sx, slots_y, slot_w, slot_h, fill=fill, stroke=stroke, sw=1.5, rx=4))
        p.append(text(sx + slot_w / 2, slots_y + 22, sym, size=15, color=col, bold=True))
        p.append(text(sx + slot_w / 2, slots_y + 40, "#%d" % (i + 1), size=9.5, color=MUTED))

    # Рухоме вікно в пам'яті MCU
    wy = 160
    p.append(rect(45, wy, 770, 180, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(65, wy + 26, "Структура в оперативній пам'яті MCU (Бітова маска вікна на N = 100 пакетів)", size=12.5, color=NEG, anchor="start", bold=True))

    p.append(rect(65, wy + 42, 430, 42, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=5))
    p.append(text(280, wy + 68, "uint32_t window[4]  →  100 біт (1 = OK, 0 = Lost)", size=11.5, color=INK))

    p.append(rect(515, wy + 42, 280, 82, fill="#eff6ff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(655, wy + 66, "LQ = (Прийнято / 100) × 100%", size=12, color=NEG, bold=True))
    p.append(text(655, wy + 90, "LQ = (93 / 100) × 100% = 93%", size=12, color=FIELD, bold=True))
    p.append(text(655, wy + 112, "Швидкий popcount() за 1 такт", size=10, color=MUTED))

    p.append(text(65, wy + 115, "• Кожен новий пакет витісняє найстаріший біт: вікно постійно ковзає в часі", size=10.5, color=MUTED, anchor="start"))
    p.append(text(65, wy + 138, "• 1 втрачений пакет дає LQ 99%; пачка з 10 втрат знижує LQ до 90% без розриву лінка", size=10.5, color=MUTED, anchor="start"))
    p.append(text(65, wy + 160, "• Приймач знає про пропущений пакет за таймером чергового слота, навіть якщо пакет не прийшов взагалі", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "lq-rolling-window.svg"), W, H, *p,
           title="Обчислення Link Quality у рухомому вікні")


# ── 3. packet-age-timeline-failsafe: вік даних і пороги failsafe ───────────────
def fig_packet_age():
    W, H = 880, 380
    p = []

    p.append(text(W / 2, 26, "Вік даних (Packet Age) та східчасті пороги аварійного захисту (Failsafe)", size=15, bold=True))

    x0, y0 = 60, 110
    xw = 760
    
    x_50   = x0 + 80
    x_200  = x0 + 200
    x_1000 = x0 + 440
    x_end  = x0 + xw

    h_bar = 50

    # Зона 1
    p.append(rect(x0, y0, x_50 - x0, h_bar, fill="#d5e8d4", stroke=FIELD, sw=1.5, rx=0))
    p.append(text((x0 + x_50) / 2, y0 + 30, "Норма", size=11, color=FIELD, bold=True))

    # Зона 2
    p.append(rect(x_50, y0, x_200 - x_50, h_bar, fill="#fff2cc", stroke="#d6b656", sw=1.5, rx=0))
    p.append(text((x_50 + x_200) / 2, y0 + 30, "Hold Last", size=11, color="#b45f06", bold=True))

    # Зона 3
    p.append(rect(x_200, y0, x_1000 - x_200, h_bar, fill="#ffe6cc", stroke="#d79b00", sw=1.5, rx=0))
    p.append(text((x_200 + x_1000) / 2, y0 + 30, "Stage 1: Горизонт / Warning", size=11, color="#b45f06", bold=True))

    # Зона 4
    p.append(rect(x_1000, y0, x_end - x_1000, h_bar, fill="#f8cecc", stroke=POS, sw=1.5, rx=0))
    p.append(text((x_1000 + x_end) / 2, y0 + 30, "Stage 2: Аварійний RTL / Посадка", size=11, color=POS, bold=True))

    for (xx, lbl) in [(x0, "0 мс"), (x_50, "50 мс"), (x_200, "200 мс"), (x_1000, "1000 мс (1 с)"), (x_end, "2.5 с+")]:
        p.append(line(xx, y0 + h_bar, xx, y0 + h_bar + 10, color=INK, sw=1.5))
        p.append(text(xx, y0 + h_bar + 25, lbl, size=10.5, color=INK, bold=True))

    cy = 210
    card_w = 175
    card_h = 135

    # Картка 1: Норма
    p.append(rect(x0, cy, card_w, card_h, fill="#f6fbf7", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(x0 + card_w / 2, cy + 22, "0 – 50 мс", size=11, color=FIELD, bold=True))
    p.append(mtext(x0 + card_w / 2, cy + 48, ["• Пакети надходять", "• Вік скидається в 0", "• Пряме керування", "без затримок"], size=9.5, color=INK, lh=1.35))

    # Картка 2: Hold
    p.append(rect(x0 + 195, cy, card_w, card_h, fill="#fffdf5", stroke="#d6b656", sw=1.2, rx=6))
    p.append(text(x0 + 195 + card_w / 2, cy + 22, "50 – 200 мс", size=11, color="#b45f06", bold=True))
    p.append(mtext(x0 + 195 + card_w / 2, cy + 48, ["• Втрата 2–10 пакетів", "• Утримання останніх", "положень стіків", "• Пілот відчуває легку", "ватність керма"], size=9.5, color=INK, lh=1.35))

    # Картка 3: Stage 1
    p.append(rect(x0 + 390, cy, card_w, card_h, fill="#fffaf5", stroke="#d79b00", sw=1.2, rx=6))
    p.append(text(x0 + 390 + card_w / 2, cy + 22, "200 – 1000 мс", size=11, color="#b45f06", bold=True))
    p.append(mtext(x0 + 390 + card_w / 2, cy + 48, ["• Зумер / OSD тривога", "• Автостабілізація:", "скидання крену/тангажу", "• Газ у позицію зависання", "• Чекання лінка"], size=9.5, color=INK, lh=1.35))

    # Картка 4: Stage 2
    p.append(rect(x0 + 585, cy, card_w, card_h, fill="#fdf6f5", stroke=POS, sw=1.2, rx=6))
    p.append(text(x0 + 585 + card_w / 2, cy + 22, "понад 1.0 – 1.5 с", size=11, color=POS, bold=True))
    p.append(mtext(x0 + 585 + card_w / 2, cy + 48, ["• Лінк визнано втраченим", "• Автономний RTL:", "набір висоти та політ", "до точки зльоту", "• Або аварійна посадка"], size=9.5, color=INK, lh=1.35))

    render(os.path.join(OUT, "packet-age-timeline-failsafe.svg"), W, H, *p,
           title="Вік даних і східчастий failsafe")


# ── 4. dynamic-power-rate-fsm: адаптація потужності й швидкості ────────────────
def fig_dynamic_adaptation():
    W, H = 880, 400
    p = []

    p.append(text(W / 2, 26, "Двовимірна динамічна адаптація радіолінка (Power + Packet Rate)", size=15, bold=True))

    bx1 = 50
    by = 65
    bw = 360
    bh = 305
    p.append(rect(bx1, by, bw, bh, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(bx1 + bw / 2, by + 26, "Важіль 1: Динамічна потужність (Dynamic Power)", size=12.5, color=NEG, bold=True))

    powers = [
        ("25 мВт (14 дБм)", "Близька дистанція, холодна електроніка, економія батареї"),
        ("100 мВт (20 дБм)", "Початкова деградація SNR (< +10 дБ)"),
        ("250 мВт (24 дБм)", "Посилення завади / вихід за зону прямої видимості"),
        ("1000 мВт (30 дБм / 1 Вт)", "Критичне падіння SNR (< +2 дБ), максимальна потужність"),
    ]
    for i, (p_title, p_desc) in enumerate(powers):
        py_i = by + 46 + i * 58
        p.append(rect(bx1 + 15, py_i, bw - 30, 50, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
        p.append(text(bx1 + 25, py_i + 20, p_title, size=11, color=NEG, anchor="start", bold=True))
        p.append(text(bx1 + 25, py_i + 38, p_desc, size=9.5, color=MUTED, anchor="start"))
        if i < 3:
            p.append(text(bx1 + bw - 25, py_i + 54, "▼", size=10, color=NEG))

    bx2 = 470
    p.append(rect(bx2, by, bw, bh, fill="#fdfbf7", stroke="#b45f06", sw=1.5, rx=8))
    p.append(text(bx2 + bw / 2, by + 26, "Важіль 2: Динамічна швидкість (Dynamic Rate)", size=12.5, color="#b45f06", bold=True))

    rates = [
        ("500 Гц (LoRa SF5 / BW500)", "Затримка 2 мс, чутливість -105 дБм (для динамічного FPV)"),
        ("250 Гц (LoRa SF6 / BW500)", "Затримка 4 мс, чутливість -108 дБм"),
        ("100 Гц (LoRa SF7 / BW500)", "Затримка 10 мс, чутливість -112 дБм"),
        ("50 Гц (LoRa SF8 / BW250)", "Затримка 20 мс, чутливість -117 дБм (далекий зв'язок)"),
    ]
    for i, (r_title, r_desc) in enumerate(rates):
        ry_i = by + 46 + i * 58
        p.append(rect(bx2 + 15, ry_i, bw - 30, 50, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
        p.append(text(bx2 + 25, ry_i + 20, r_title, size=11, color="#b45f06", anchor="start", bold=True))
        p.append(text(bx2 + 25, ry_i + 38, r_desc, size=9.5, color=MUTED, anchor="start"))
        if i < 3:
            p.append(text(bx2 + bw - 25, ry_i + 54, "▼", size=10, color="#b45f06"))

    p.append(arrow(bx1 + bw, by + bh / 2, bx2, by + bh / 2, color=INK, sw=2))
    p.append(text(W / 2, by + bh / 2 - 12, "Потужність в стелі 1 Вт,", size=9.5, color=INK, bold=True))
    p.append(text(W / 2, by + bh / 2 + 20, "а SNR падає → знижуємо Rate", size=9.5, color=INK, bold=True))

    render(os.path.join(OUT, "dynamic-power-rate-fsm.svg"), W, H, *p,
           title="Динамічна адаптація потужності та швидкості")


if __name__ == "__main__":
    fig_rssi_vs_snr()
    fig_lq_rolling_window()
    fig_packet_age()
    fig_dynamic_adaptation()
    print("All figures generated successfully.")
