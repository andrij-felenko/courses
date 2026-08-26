# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, color, sw, d)


# ── 1. pam4-levels ───────────────────────────────────────────────────────────

def fig_pam4_levels():
    W, H = 840, 480
    p = []

    b, _, _ = textbox(420, 28, "Двійковий NRZ (1 біт/символ) проти PAM4 (2 біти/символ) за однакової швидкості бітів", size=14, bold=True)
    p.append(b)

    # NRZ
    p.append(rect(40, 58, 760, 185, fill="#fafbfc", stroke="#d1d5db", rx=8))
    p.append(text(60, 82, "NRZ (Non-Return-to-Zero): 2 рівні напруги, 8 тактів T_bit", size=12, bold=True, anchor="start", color=INK))

    p.append(line(130, 160, 770, 160, color=MUTED, sw=1.0, dash="3,3"))
    p.append(text(120, 164, "0 В", size=11, color=MUTED, anchor="end"))
    p.append(line(130, 115, 770, 115, color="#e5e7eb", sw=1.0))
    p.append(text(120, 119, "+V₀ (1)", size=11, color=POS, anchor="end", bold=True))
    p.append(line(130, 205, 770, 205, color="#e5e7eb", sw=1.0))
    p.append(text(120, 209, "−V₀ (0)", size=11, color=NEG, anchor="end", bold=True))

    nrz_bits = [1, 0, 1, 1, 0, 1, 0, 0]
    t_start = 150
    t_step = 72

    pts_nrz = []
    curr_y = 115 if nrz_bits[0] == 1 else 205
    pts_nrz.append((t_start, curr_y))

    for i, b_val in enumerate(nrz_bits):
        x0 = t_start + i * t_step
        x1 = x0 + t_step
        y_val = 115 if b_val == 1 else 205
        pts_nrz.append((x0, y_val))
        pts_nrz.append((x1, y_val))
        p.append(text(x0 + t_step/2, 100, str(b_val), size=12, bold=True, color=POS if b_val == 1 else NEG))
        p.append(line(x1, 106, x1, 214, color="#e5e7eb", sw=1.0, dash="2,2"))

    p.append(polyline(pts_nrz, color=LINE, sw=2.2))

    p.append(line(t_start, 222, t_start + t_step, 222, color=MUTED, sw=1.2))
    p.append(line(t_start, 218, t_start, 226, color=MUTED, sw=1.2))
    p.append(line(t_start + t_step, 218, t_start + t_step, 226, color=MUTED, sw=1.2))
    p.append(text(t_start + t_step/2, 235, "T_NRZ = T_bit", size=10, color=MUTED))


    # PAM4
    p.append(rect(40, 255, 760, 205, fill="#fafbfc", stroke="#d1d5db", rx=8))
    p.append(text(60, 278, "PAM4: 4 рівні напруги, 4 такти T_symbol = 2·T_bit (удвічі нижча частота Найквіста)", size=12, bold=True, anchor="start", color=INK))

    p.append(line(130, 305, 770, 305, color="#fed7aa", sw=1.0))
    p.append(text(120, 309, "+V₀ (10, L3)", size=11, color="#ea580c", anchor="end", bold=True))

    p.append(line(130, 340, 770, 340, color="#bbf7d0", sw=1.0))
    p.append(text(120, 344, "+V₀/3 (11, L2)", size=11, color=FIELD, anchor="end", bold=True))

    p.append(line(130, 375, 770, 375, color="#bae6fd", sw=1.0))
    p.append(text(120, 379, "−V₀/3 (01, L1)", size=11, color=NEG, anchor="end", bold=True))

    p.append(line(130, 410, 770, 410, color="#fecaca", sw=1.0))
    p.append(text(120, 414, "−V₀ (00, L0)", size=11, color=POS, anchor="end", bold=True))

    pam_syms = [
        ("10", 305, "#ea580c"),
        ("11", 340, FIELD),
        ("01", 375, NEG),
        ("00", 410, POS)
    ]
    t_step_pam = t_step * 2

    pts_pam = []
    pts_pam.append((t_start, pam_syms[0][1]))

    for i, (bits, y_val, col) in enumerate(pam_syms):
        x0 = t_start + i * t_step_pam
        x1 = x0 + t_step_pam
        pts_pam.append((x0, y_val))
        pts_pam.append((x1, y_val))
        p.append(text(x0 + t_step_pam/2, 296 if y_val > 310 else 326, "«%s»" % bits, size=12, bold=True, color=col))
        p.append(line(x1, 300, x1, 418, color="#e5e7eb", sw=1.0, dash="2,2"))

    p.append(polyline(pts_pam, color=LINE, sw=2.2))

    p.append(line(t_start, 428, t_start + t_step_pam, 428, color=MUTED, sw=1.2))
    p.append(line(t_start, 424, t_start, 432, color=MUTED, sw=1.2))
    p.append(line(t_start + t_step_pam, 424, t_start + t_step_pam, 432, color=MUTED, sw=1.2))
    p.append(text(t_start + t_step_pam/2, 442, "T_PAM4 = 2·T_bit  (подвоєна тривалість символу)", size=10, color=MUTED))

    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    svg.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, BG))
    svg.extend(p)
    svg.append('</svg>')
    with open(os.path.join(OUT, "pam4-levels.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


# ── 2. eye-diagram ───────────────────────────────────────────────────────────

def fig_eye_diagram():
    W, H = 840, 460
    p = []

    b, _, _ = textbox(420, 26, "Очневий графік: одне широке вікно NRZ проти трьох звужених очей PAM4", size=14, bold=True)
    p.append(b)

    # Ліва панель: NRZ Eye
    p.append(rect(40, 52, 365, 390, fill="#fafbfc", stroke="#d1d5db", rx=8))
    p.append(text(222, 75, "NRZ: одне велике очко (Single Eye)", size=12, bold=True, color=INK))

    p.append(line(100, 125, 375, 125, color=POS, sw=2.0))
    p.append(line(100, 315, 375, 315, color=NEG, sw=2.0))
    p.append(text(95, 129, "+V₀ (1)", size=11, color=POS, anchor="end", bold=True))
    p.append(text(95, 319, "−V₀ (0)", size=11, color=NEG, anchor="end", bold=True))

    p.append('<path d="M 100 125 C 230 125, 230 315, 375 315" fill="none" stroke="#6b7280" stroke-width="1.8" stroke-opacity="0.6"/>')
    p.append('<path d="M 100 315 C 230 315, 230 125, 375 125" fill="none" stroke="#6b7280" stroke-width="1.8" stroke-opacity="0.6"/>')

    p.append(line(100, 220, 375, 220, color="#9ca3af", sw=1.0, dash="3,3"))
    p.append(text(378, 224, "Поріг 0 В", size=10, color=MUTED, anchor="start"))

    p.append(line(125, 130, 125, 310, color=FIELD, sw=1.8))
    p.append(line(120, 130, 130, 130, color=FIELD, sw=1.8))
    p.append(line(120, 310, 130, 310, color=FIELD, sw=1.8))

    p.append(text(235, 102, "H_NRZ = 2·V₀ (Запас = V₀)", size=11, bold=True, color=FIELD))

    p.append(text(222, 355, "Запас завадостійкості: 100%", size=11, color=FIELD, bold=True))
    p.append(text(222, 380, "Один строб вибірки в центрі такту", size=10, color=MUTED))
    p.append(text(222, 405, "Типовий Raw BER < 10⁻¹² (без FEC)", size=10, color=MUTED))


    # Права панель: PAM4 Eyes
    p.append(rect(435, 52, 365, 390, fill="#fafbfc", stroke="#d1d5db", rx=8))
    p.append(text(617, 75, "PAM4: три очка (Triple Stacked Eyes)", size=12, bold=True, color=INK))

    y_l3, y_l2, y_l1, y_l0 = 115, 175, 235, 295
    p.append(line(485, y_l3, 760, y_l3, color="#ea580c", sw=1.8))
    p.append(line(485, y_l2, 760, y_l2, color=FIELD, sw=1.8))
    p.append(line(485, y_l1, 760, y_l1, color=NEG, sw=1.8))
    p.append(line(485, y_l0, 760, y_l0, color=POS, sw=1.8))

    p.append(text(480, y_l3 + 4, "+V₀ (L3)", size=10, color="#ea580c", anchor="end", bold=True))
    p.append(text(480, y_l2 + 4, "+V₀/3 (L2)", size=10, color=FIELD, anchor="end", bold=True))
    p.append(text(480, y_l1 + 4, "−V₀/3 (L1)", size=10, color=NEG, anchor="end", bold=True))
    p.append(text(480, y_l0 + 4, "−V₀ (L0)", size=10, color=POS, anchor="end", bold=True))

    th_upper = 145
    th_mid   = 205
    th_lower = 265

    p.append(line(485, th_upper, 760, th_upper, color="#9ca3af", sw=1.0, dash="2,2"))
    p.append(line(485, th_mid,   760, th_mid,   color="#9ca3af", sw=1.0, dash="2,2"))
    p.append(line(485, th_lower, 760, th_lower, color="#9ca3af", sw=1.0, dash="2,2"))

    p.append(text(764, th_upper + 3, "+2V₀/3", size=9, color=MUTED, anchor="start"))
    p.append(text(764, th_mid + 3,   "0 В",     size=9, color=MUTED, anchor="start"))
    p.append(text(764, th_lower + 3, "−2V₀/3", size=9, color=MUTED, anchor="start"))

    p.append('<path d="M 485 115 C 600 115, 600 175, 760 175" fill="none" stroke="#6b7280" stroke-width="1.2" stroke-opacity="0.5"/>')
    p.append('<path d="M 485 175 C 600 175, 600 115, 760 115" fill="none" stroke="#6b7280" stroke-width="1.2" stroke-opacity="0.5"/>')
    p.append('<path d="M 485 175 C 600 175, 600 235, 760 235" fill="none" stroke="#6b7280" stroke-width="1.2" stroke-opacity="0.5"/>')
    p.append('<path d="M 485 235 C 600 235, 600 175, 760 175" fill="none" stroke="#6b7280" stroke-width="1.2" stroke-opacity="0.5"/>')
    p.append('<path d="M 485 235 C 600 235, 600 295, 760 295" fill="none" stroke="#6b7280" stroke-width="1.2" stroke-opacity="0.5"/>')
    p.append('<path d="M 485 295 C 600 295, 600 235, 760 235" fill="none" stroke="#6b7280" stroke-width="1.2" stroke-opacity="0.5"/>')

    p.append(text(625, 102, "H_PAM4 = 2·V₀ / 3 (Запас = V₀ / 3)", size=11, bold=True, color=POS))

    p.append(text(617, 335, "Штраф SNR: 20·log₁₀(1/3) ≈ −9.54 дБ", size=11, color=POS, bold=True))
    p.append(text(617, 360, "Вимагає 3 компаратори (слайсери)", size=10, color=MUTED))
    p.append(text(617, 385, "Raw BER ≈ 10⁻⁴ … 10⁻⁵ (потрібен FEC)", size=10, color="#b91c1c", bold=True))
    p.append(text(617, 410, "Post-FEC BER < 10⁻¹⁵ (цільовий рівень)", size=10, color=FIELD, bold=True))

    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    svg.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, BG))
    svg.extend(p)
    svg.append('</svg>')
    with open(os.path.join(OUT, "eye-diagram.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


# ── 3. gray-vs-binary ────────────────────────────────────────────────────────

def fig_gray_vs_binary():
    W, H = 840, 420
    p = []

    b, _, _ = textbox(420, 26, "Перевага коду Грея в PAM4: захист від подвійних бітових помилок на сусідніх рівнях", size=14, bold=True)
    p.append(b)

    # Ліва колонка
    p.append(rect(40, 52, 365, 345, fill="#fafbfc", stroke="#d1d5db", rx=8))
    p.append(text(222, 76, "Прямий двійковий код (Natural Binary)", size=12, bold=True, color=POS))

    levels_bin = [
        ("L3 (+V₀)",  "11", 115, "#ea580c"),
        ("L2 (+V₀/3)", "10", 170, FIELD),
        ("L1 (−V₀/3)", "01", 225, NEG),
        ("L0 (−V₀)",  "00", 280, POS),
    ]

    for lbl, code, y_pos, col in levels_bin:
        p.append(line(70, y_pos, 370, y_pos, color="#e5e7eb", sw=1.2))
        p.append(text(75, y_pos - 6, lbl, size=11, color=MUTED, anchor="start"))
        p.append(text(355, y_pos - 6, "«%s»" % code, size=13, bold=True, color=col, anchor="end"))

    p.append(arrow(210, 221, 210, 177, color=POS, sw=2.5))
    p.append(text(215, 200, "+Шум", size=10, bold=True, color=POS, anchor="start"))

    b_err1, _, _ = textbox(222, 335, "Збій L1 (01) → L2 (10)\nОбидва біти перевернулися!\nВідстань Геммінга d_H = 2\nBER ≈ SER (100% помилок)", size=11, fill="#fee2e2", stroke=POS, bold=True)
    p.append(b_err1)


    # Права колонка
    p.append(rect(435, 52, 365, 345, fill="#fafbfc", stroke="#d1d5db", rx=8))
    p.append(text(617, 76, "Кодування Грея (Gray Code Mapping)", size=12, bold=True, color=FIELD))

    levels_gray = [
        ("L3 (+V₀)",  "10", 115, "#ea580c"),
        ("L2 (+V₀/3)", "11", 170, FIELD),
        ("L1 (−V₀/3)", "01", 225, NEG),
        ("L0 (−V₀)",  "00", 280, POS),
    ]

    for lbl, code, y_pos, col in levels_gray:
        p.append(line(465, y_pos, 765, y_pos, color="#e5e7eb", sw=1.2))
        p.append(text(470, y_pos - 6, lbl, size=11, color=MUTED, anchor="start"))
        p.append(text(750, y_pos - 6, "«%s»" % code, size=13, bold=True, color=col, anchor="end"))

    p.append(arrow(605, 221, 605, 177, color=FIELD, sw=2.5))
    p.append(text(610, 200, "+Шум", size=10, bold=True, color=FIELD, anchor="start"))

    b_err2, _, _ = textbox(617, 335, "Збій L1 (01) → L2 (11)\nЛише один старший біт перекинувся!\nВідстань Геммінга d_H = 1\nBER ≈ SER / 2 (вдвічі менше бітових бід)", size=11, fill="#dcfce7", stroke=FIELD, bold=True)
    p.append(b_err2)

    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    svg.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, BG))
    svg.extend(p)
    svg.append('</svg>')
    with open(os.path.join(OUT, "gray-vs-binary.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


# ── 4. transceiver-chain ──────────────────────────────────────────────────────

def fig_transceiver_chain():
    W, H = 840, 460
    p = []

    b, _, _ = textbox(420, 26, "Архітектура тракту PAM4 SerDes: кодування, лінія зв'язку, еквалізація та виправлення помилок", size=14, bold=True)
    p.append(b)

    # TX
    p.append(rect(30, 55, 780, 110, fill="#eff6ff", stroke="#3b82f6", rx=8))
    p.append(text(45, 75, "Передавач (Transmitter, TX)", size=12, bold=True, color="#1d4ed8", anchor="start"))

    b1, _, _ = textbox(115, 115, "Вхідні дані\n(Паралельні біти)", size=10, fill="#ffffff", stroke="#93c5fd")
    p.append(b1)
    p.append(arrow(170, 115, 200, 115, color="#2563eb"))

    b2, _, _ = textbox(265, 115, "FEC кодер RS(544,514)\nДодає перевірочні байти", size=10, fill="#ffffff", stroke="#2563eb", bold=True)
    p.append(b2)
    p.append(arrow(335, 115, 365, 115, color="#2563eb"))

    b3, _, _ = textbox(425, 115, "Gray Мапер\n2 біти → Символ (L0..L3)", size=10, fill="#ffffff", stroke="#2563eb", bold=True)
    p.append(b3)
    p.append(arrow(490, 115, 520, 115, color="#2563eb"))

    b4, _, _ = textbox(580, 115, "TX FFE (Pre-emphasis)\nПопереднє підсилення ВЧ", size=10, fill="#ffffff", stroke="#93c5fd")
    p.append(b4)
    p.append(arrow(650, 115, 680, 115, color="#2563eb"))

    b5, _, _ = textbox(740, 115, "PAM4 Драйвер\n4 рівні напруги", size=10, fill="#dbeafe", stroke="#1d4ed8", bold=True)
    p.append(b5)


    # Канал
    p.append(rect(180, 180, 480, 65, fill="#fef2f2", stroke=POS, rx=6))
    p.append(text(420, 202, "Фізичний канал: мідні доріжки PCB, конектори, кабель (Згасання > 30 дБ на 28 ГГц)", size=11, bold=True, color=POS))
    p.append(text(420, 224, "Вносить міжсимвольну інтерференцію (ISI) та гаусів шум", size=10, color=MUTED))

    p.append(arrow(740, 142, 620, 180, color=POS, sw=2.0))
    p.append(arrow(220, 245, 110, 280, color=POS, sw=2.0))


    # RX
    p.append(rect(30, 280, 780, 160, fill="#f0fdf4", stroke=FIELD, rx=8))
    p.append(text(45, 300, "Приймач (Receiver, RX)", size=12, bold=True, color="#15803d", anchor="start"))

    b_rx1, _, _ = textbox(110, 345, "Аналоговий еквалайзер\n(CTLE / VGA)", size=10, fill="#ffffff", stroke="#86efac")
    p.append(b_rx1)
    p.append(arrow(175, 345, 205, 345, color=FIELD))

    b_rx2, _, _ = textbox(275, 345, "АЦП / 3 Слайсери + DFE\nВідновлення рівнів L0..L3", size=10, fill="#dcfce7", stroke=FIELD, bold=True)
    p.append(b_rx2)
    p.append(arrow(350, 345, 380, 345, color=FIELD))

    b_rx3, _, _ = textbox(445, 345, "Gray Демапер\nСимвол → 2 біти даних", size=10, fill="#ffffff", stroke=FIELD, bold=True)
    p.append(b_rx3)
    p.append(arrow(510, 345, 540, 345, color=FIELD))

    b_rx4, _, _ = textbox(620, 345, "FEC декодер RS(544,514)\nВиправляє до 15 символів", size=10, fill="#dcfce7", stroke="#15803d", bold=True)
    p.append(b_rx4)
    p.append(arrow(695, 345, 725, 345, color=FIELD))

    b_rx5, _, _ = textbox(760, 345, "Дані\nBER<10⁻¹⁵", size=10, fill="#ffffff", stroke="#86efac", bold=True)
    p.append(b_rx5)

    p.append(text(360, 415, "Raw BER після слайсера: 10⁻⁴ … 10⁻⁵ (зашумлений потік бітів)", size=10, color=POS, bold=True))
    p.append(text(680, 415, "Post-FEC BER: < 10⁻¹⁵ (чистий потік)", size=10, color="#15803d", bold=True))

    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    svg.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, BG))
    svg.extend(p)
    svg.append('</svg>')
    with open(os.path.join(OUT, "transceiver-chain.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


# ── 5. ber-vs-snr ────────────────────────────────────────────────────────────

def fig_ber_vs_snr():
    W, H = 840, 480
    p = []

    b, _, _ = textbox(420, 24, "Криві ймовірності бітової помилки (BER): штраф SNR у 9.54 дБ та поріг виправлення FEC", size=14, bold=True)
    p.append(b)

    gx0, gx1 = 110, 760
    gy0, gy1 = 65, 410

    p.append(rect(gx0, gy0, gx1 - gx0, gy1 - gy0, fill="#fafbfc", stroke="#d1d5db", rx=6))

    snr_min, snr_max = 6.0, 24.0
    log_ber_max, log_ber_min = 0.0, -16.0

    def get_x(snr):
        return gx0 + (snr - snr_min) / (snr_max - snr_min) * (gx1 - gx0)

    def get_y(log_ber):
        return gy0 + (log_ber_max - log_ber) / (log_ber_max - log_ber_min) * (gy1 - gy0)

    # Засічки на осі X замість суцільних вертикальних ліній
    for snr_val in range(6, 25, 2):
        x = get_x(snr_val)
        p.append(line(x, gy1, x, gy1 + 5, color=INK, sw=1.2))
        p.append(text(x, gy1 + 18, "%d" % snr_val, size=10, color=MUTED))

    p.append(text((gx0 + gx1) / 2, gy1 + 38, "Відношення сигнал/шум E_s / N₀ (дБ)", size=11, bold=True, color=INK))

    # Горизонтальні лінії декад
    for lber in range(0, -17, -2):
        y = get_y(lber)
        p.append(line(gx0, y, gx1, y, color="#f3f4f6", sw=1.0))
        exp_str = "10⁰" if lber == 0 else "10⁻%d" % abs(lber)
        p.append(text(gx0 - 10, y + 4, exp_str, size=10, color=MUTED, anchor="end"))

    p.append(text(gx0, gy0 - 10, "Ймовірність бітової помилки (BER)", size=11, bold=True, color=INK, anchor="start"))

    # Криві
    pts_nrz = []
    pts_pam4 = []

    steps = 100
    for i in range(steps + 1):
        s = snr_min + i * (snr_max - snr_min) / steps
        lin_snr = 10.0 ** (s / 10.0)

        arg_nrz = math.sqrt(lin_snr)
        ber_n = 0.5 * math.erfc(arg_nrz / math.sqrt(2.0))
        if ber_n > 1e-18:
            l_n = math.log10(max(ber_n, 1e-16))
            if l_n >= log_ber_min:
                pts_nrz.append((get_x(s), get_y(l_n)))

        arg_pam = math.sqrt(lin_snr / 9.0)
        ber_p = 0.375 * math.erfc(arg_pam / math.sqrt(2.0))
        if ber_p > 1e-18:
            l_p = math.log10(max(ber_p, 1e-16))
            if l_p >= log_ber_min:
                pts_pam4.append((get_x(s), get_y(l_p)))

    p.append(polyline(pts_nrz, color="#2563eb", sw=2.5))
    p.append(polyline(pts_pam4, color=POS, sw=2.5))

    p.append(text(get_x(12.5), get_y(-6.8), "NRZ", size=12, bold=True, color="#2563eb"))
    p.append(text(get_x(21.5), get_y(-6.8), "PAM4 (без FEC)", size=12, bold=True, color=POS))

    # Стрілка різниці SNR вгорі
    y_ref = get_y(-1.5)
    x_nrz_ref = get_x(7.2)
    x_pam_ref = get_x(16.74)

    p.append(line(x_nrz_ref, y_ref, x_pam_ref, y_ref, color=LINE, sw=1.5))
    p.append(line(x_nrz_ref, y_ref - 6, x_nrz_ref, y_ref + 6, color=LINE, sw=1.5))
    p.append(line(x_pam_ref, y_ref - 6, x_pam_ref, y_ref + 6, color=LINE, sw=1.5))

    p.append(text((x_nrz_ref + x_pam_ref) / 2, y_ref - 8, "Штраф SNR ≈ 9.54 дБ", size=10, color=POS, bold=True))

    # Поріг FEC
    y_fec_thresh = get_y(-4.0)
    p.append(line(gx0, y_fec_thresh, gx1, y_fec_thresh, color=FIELD, sw=1.8, dash="4,3"))
    p.append(text(gx1 - 10, y_fec_thresh - 8, "Поріг роботи RS(544,514) FEC (Raw BER ≈ 10⁻⁴)", size=10, color=FIELD, bold=True, anchor="end"))

    # Стрілка дії FEC
    x_fec_op = get_x(15.5)
    p.append(arrow(x_fec_op, y_fec_thresh + 4, x_fec_op, get_y(-15.0), color=FIELD, sw=2.5))
    p.append(text(x_fec_op, gy1 + 55, "Дія RS-FEC: зниження BER з 10⁻⁴ до цільового < 10⁻¹⁵", size=10.5, color=FIELD, bold=True, anchor="middle"))

    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, 510, W, 510)]
    svg.append('<rect width="%d" height="%d" fill="%s"/>' % (W, 510, BG))
    svg.extend(p)
    svg.append('</svg>')
    with open(os.path.join(OUT, "ber-vs-snr.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


if __name__ == "__main__":
    fig_pam4_levels()
    fig_eye_diagram()
    fig_gray_vs_binary()
    fig_transceiver_chain()
    fig_ber_vs_snr()
    print("Згенеровано 5 фігур у %s" % OUT)
