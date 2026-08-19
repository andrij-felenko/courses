# -*- coding: utf-8 -*-
"""Фігури до теми «Baud проти біт/с».
Запуск: python figs.py -> генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Порівняння тривалості символу Ts і тривалості біта Tb ──────────────
def fig_symbol_vs_bit():
    W, H = 880, 480
    f = [
        text(W / 2, 28, "Символ проти біта: як групування бітів знижує швидкість перемикання лінії",
             size=15, bold=True)
    ]

    # Бітовий потік: 1 0 1 1 0 0 0 1 (8 бітів)
    bits = [1, 0, 1, 1, 0, 0, 0, 1]
    n_bits = len(bits)

    x0 = 180
    bw = 75   # ширина одного бітового інтервалу Tb
    total_w = n_bits * bw

    # Верхній часовий пояс — бітовий потік
    y_bits = 75
    f.append(text(x0 - 20, y_bits + 12, "Бітовий потік (8 біт):", size=12, bold=True, anchor="end"))
    for i, b in enumerate(bits):
        bx = x0 + i * bw
        f.append(rect(bx, y_bits, bw, 32, fill="#f8fafc", stroke=LINE, sw=1.2))
        f.append(text(bx + bw / 2, y_bits + 21, str(b), size=14, bold=True, color=POS if b else NEG))
        # верхова риска Tb
        if i == 0:
            f.append(line(bx, y_bits - 6, bx + bw, y_bits - 6, color=MUTED, sw=1.2))
            f.append(line(bx, y_bits - 10, bx, y_bits - 2, color=MUTED, sw=1.2))
            f.append(line(bx + bw, y_bits - 10, bx + bw, y_bits - 2, color=MUTED, sw=1.2))
            f.append(text(bx + bw / 2, y_bits - 12, "T_b (час 1 біта)", size=10.5, color=MUTED))

    # 1) Двійковий NRZ (1 біт/символ, Ts = Tb, 1 бод = 1 біт/с)
    y_nrz = 175
    f.append(text(x0 - 20, y_nrz - 10, "1. 2-PAM / NRZ (k = 1 біт/символ):", size=12, bold=True, anchor="end"))
    f.append(text(x0 - 20, y_nrz + 10, "T_s = T_b  |  1 бод = 1 біт/с", size=10.5, color=MUTED, anchor="end"))

    # Хвиля NRZ
    hi_v = y_nrz - 22
    lo_v = y_nrz + 22
    prev_v = hi_v if bits[0] == 1 else lo_v

    for i, b in enumerate(bits):
        cur_v = hi_v if b == 1 else lo_v
        bx = x0 + i * bw
        if cur_v != prev_v:
            f.append(line(bx, prev_v, bx, cur_v, color=INK, sw=2.2))
        f.append(line(bx, cur_v, bx + bw, cur_v, color=INK, sw=2.2))
        # пунктир такту
        f.append(line(bx, y_nrz - 30, bx, y_nrz + 30, color="#d1d5db", sw=1.0, dash="3,3"))
        # підпис символу
        f.append(text(bx + bw / 2, y_nrz + 38, f"S{i} = «{b}»", size=10, color=MUTED))
        prev_v = cur_v
    f.append(line(x0 + total_w, y_nrz - 30, x0 + total_w, y_nrz + 30, color="#d1d5db", sw=1.0, dash="3,3"))

    # 2) 4-PAM / QPSK (2 біти/символ, Ts = 2 Tb, 1 бод = 2 біт/с)
    y_pam4 = 295
    f.append(text(x0 - 20, y_pam4 - 10, "2. 4-PAM (k = 2 біти/символ):", size=12, bold=True, anchor="end"))
    f.append(text(x0 - 20, y_pam4 + 10, "T_s = 2·T_b  |  1 бод = 2 біт/с", size=10.5, color=MUTED, anchor="end"))

    pam4_levels = {
        (1, 1): (y_pam4 - 28, "+3 В («11»)"),
        (1, 0): (y_pam4 - 10, "+1 В («10»)"),
        (0, 1): (y_pam4 + 10, "−1 В («01»)"),
        (0, 0): (y_pam4 + 28, "−3 В («00»)")
    }
    sym_pairs = [(bits[2*i], bits[2*i+1]) for i in range(4)]
    prev_pv = pam4_levels[sym_pairs[0]][0]

    for i, pair in enumerate(sym_pairs):
        cur_pv, lab = pam4_levels[pair]
        sx = x0 + i * (2 * bw)
        sw_w = 2 * bw
        if cur_pv != prev_pv:
            f.append(line(sx, prev_pv, sx, cur_pv, color=FIELD, sw=2.5))
        f.append(line(sx, cur_pv, sx + sw_w, cur_pv, color=FIELD, sw=2.5))
        # пунктир такту символу
        f.append(line(sx, y_pam4 - 36, sx, y_pam4 + 36, color="#9ca3af", sw=1.2, dash="4,3"))
        # рамка символу
        f.append(text(sx + sw_w / 2, y_pam4 + 48, f"Символ {i}: «{pair[0]}{pair[1]}» ({lab})", size=10.5, color=INK, bold=True))
        prev_pv = cur_pv
    f.append(line(x0 + total_w, y_pam4 - 36, x0 + total_w, y_pam4 + 36, color="#9ca3af", sw=1.2, dash="4,3"))

    # 3) 16-QAM (4 біти/символ, Ts = 4 Tb, 1 бод = 4 біт/с)
    y_qam16 = 405
    f.append(text(x0 - 20, y_qam16 - 10, "3. 16-QAM (k = 4 біти/символ):", size=12, bold=True, anchor="end"))
    f.append(text(x0 - 20, y_qam16 + 10, "T_s = 4·T_b  |  1 бод = 4 біт/с", size=10.5, color=MUTED, anchor="end"))

    qam_syms = [
        ("«1011» (Фаза φ₁ = 135°, Амплітуда A₁)", y_qam16 - 18),
        ("«0001» (Фаза φ₂ = 315°, Амплітуда A₂)", y_qam16 + 18)
    ]
    for i, (lab, y_pos) in enumerate(qam_syms):
        qx = x0 + i * (4 * bw)
        qw_w = 4 * bw
        f.append(rect(qx + 4, y_qam16 - 22, qw_w - 8, 44, fill="#eff6ff", stroke="#3b82f6", sw=1.8, rx=6))
        f.append(line(qx, y_qam16 - 28, qx, y_qam16 + 28, color="#2563eb", sw=1.5, dash="4,3"))
        f.append(text(qx + qw_w / 2, y_qam16 + 4, f"Символ {i}: {lab}", size=11, color="#1e40af", bold=True))
    f.append(line(x0 + total_w, y_qam16 - 28, x0 + total_w, y_qam16 + 28, color="#2563eb", sw=1.5, dash="4,3"))

    # Підсумковий висновок унизу
    f.append(text(W / 2, 468, "Фізична лінія змінює стан у 2 або 4 рази рідше, але інформаційний бітрейт лишається тим самим або зростає",
                  size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, "symbol-vs-bit.svg"), W, H, *f)


# ── 2. «Драбина» модуляцій: M, k = log2(M), стійкість і застосування ──────
def fig_modulation_ladder():
    W, H = 880, 430
    f = [
        text(W / 2, 26, "Драбина модуляцій: біти на символ k = log₂(M), щільність сузір'я та запас до шуму",
             size=15, bold=True)
    ]

    rows = [
        ("2-PAM / BPSK / FSK", "M = 2", "k = 1 біт/бод", "UART, RS-232, модем Bell 103", "+", "#10b981", "#ecfdf5"),
        ("4-PAM / QPSK", "M = 4", "k = 2 біти/бод", "1000BASE-T Ethernet, QPSK у DVB-S, GPS", "++", "#059669", "#d1fae5"),
        ("8-PSK", "M = 8", "k = 3 біти/бод", "EDGE (2.75G GSM), супутниковий DVB-S2", "+++", "#0284c7", "#e0f2fe"),
        ("16-QAM", "M = 16", "k = 4 біти/бод", "V.34 модем (33.6 кбіт/с), LTE, Wi-Fi 4", "++++", "#2563eb", "#dbeafe"),
        ("64-QAM", "M = 64", "k = 6 бітів/бод", "DVB-C, DOCSIS 3.0, Wi-Fi 5 (802.11ac)", "+++++", "#7c3aed", "#ede9fe"),
        ("256-QAM", "M = 256", "k = 8 бітів/бод", "Wi-Fi 5 Wave 2, LTE-Advanced, 10G-EPON", "++++++", "#d97706", "#fef3c7"),
        ("1024-QAM", "M = 1024", "k = 10 бітів/бод", "Wi-Fi 6 (802.11ax), DOCSIS 3.1", "+++++++", "#ea580c", "#ffedd5"),
        ("4096-QAM", "M = 4096", "k = 12 бітів/бод", "Wi-Fi 7 (802.11be), DOCSIS 4.0", "++++++++", "#dc2626", "#fee2e2"),
    ]

    x0 = 40
    y0 = 60
    rh = 38
    col_w = [170, 75, 115, 300, 140]

    headers = ["Схема модуляції", "Станів M", "Біти k = log₂M", "Де застосовується у зв'язку", "Вимоги до SNR"]
    hx = x0
    for j, h_text in enumerate(headers):
        f.append(rect(hx, y0, col_w[j], 28, fill="#e5e7eb", stroke=LINE, sw=1.2, rx=3))
        f.append(text(hx + col_w[j] / 2, y0 + 19, h_text, size=11, bold=True))
        hx += col_w[j]

    for i, (name, m_val, k_val, apps, snr, bar_col, bg_col) in enumerate(rows):
        ry = y0 + 32 + i * rh
        rx = x0
        f.append(rect(rx, ry, col_w[0], rh - 4, fill=bg_col, stroke=LINE, sw=1.0, rx=3))
        f.append(text(rx + col_w[0] / 2, ry + 22, name, size=11.5, bold=True, color=bar_col))
        rx += col_w[0]

        f.append(rect(rx, ry, col_w[1], rh - 4, fill="#ffffff", stroke=LINE, sw=1.0, rx=3))
        f.append(text(rx + col_w[1] / 2, ry + 22, m_val, size=11, color=MUTED))
        rx += col_w[1]

        f.append(rect(rx, ry, col_w[2], rh - 4, fill="#ffffff", stroke=LINE, sw=1.0, rx=3))
        f.append(text(rx + col_w[2] / 2, ry + 22, k_val, size=11.5, bold=True))
        rx += col_w[2]

        f.append(rect(rx, ry, col_w[3], rh - 4, fill="#ffffff", stroke=LINE, sw=1.0, rx=3))
        f.append(text(rx + 10, ry + 22, apps, size=11, anchor="start"))
        rx += col_w[3]

        f.append(rect(rx, ry, col_w[4], rh - 4, fill="#ffffff", stroke=LINE, sw=1.0, rx=3))
        f.append(text(rx + col_w[4] / 2, ry + 22, snr, size=12, color=bar_col, bold=True))

    y_bot = y0 + 32 + len(rows) * rh + 12
    f.append(line(x0 + 40, y_bot, x0 + 760, y_bot, color=LINE, sw=1.5))
    f.append(line(x0 + 760, y_bot - 4, x0 + 760, y_bot + 4, color=LINE, sw=1.5))
    f.append(text(x0 + 40, y_bot + 16, "← Вища стійкість до завад і шуму (низький SNR)", size=10.5, color=FIELD, anchor="start", bold=True))
    f.append(text(x0 + 760, y_bot + 16, "Вища швидкість передачі біт/с (високий SNR) →", size=10.5, color=POS, anchor="end", bold=True))

    render(os.path.join(IMG, "modulation-ladder.svg"), W, H, *f)


# ── 3. Ієрархія бітрейтів від фізичного дроту до застосунку ────────────────
def fig_throughput_layers():
    W, H = 880, 450
    f = [
        text(W / 2, 28, "Ієрархія швидкостей: від бодів на лінії до корисного Goodput застосунку",
             size=15, bold=True)
    ]

    layers = [
        ("1. Бодова швидкість (Symbol Rate, R_s)", "125 Мбод", "Фізична частота перемикання станів на дроті (тактові імпульси/с)", "#f1f5f9", "#475569"),
        ("2. Фізичний бітрейт лінії (Raw Bitrate, R_raw = R_s · k)", "250 Мбіт/с", "Множення на k = 2 біти/символ (4-PAM модуляція, 4 рівні напруги)", "#e0f2fe", "#0284c7"),
        ("3. Брутто-бітрейт лінії (Gross Bitrate, R_gross)", "200 Мбіт/с", "Вирахування надлишковості лінійного кодування (наприклад, 8b/10b забирає 20%)", "#fef3c7", "#d97706"),
        ("4. Нетто-бітрейт каналу (Net Coded Bitrate, R_net)", "166.7 Мбіт/с", "Вирахування завадостійкого кодування FEC (кодова швидкість R = 5/6 або LDPC)", "#ede9fe", "#7c3aed"),
        ("5. Корисний бітрейт застосунку (Goodput)", "158.2 Мбіт/с", "Чисті корисні байти після відкидання заголовків Ethernet, IP, TCP і пауз IFG", "#dcfce7", "#16a34a"),
    ]

    x0 = 60
    y0 = 65
    lh = 60
    w_box = 760

    for i, (title, rate, desc, bg_c, str_c) in enumerate(layers):
        cy = y0 + i * lh
        f.append(rect(x0, cy, w_box, lh - 12, fill=bg_c, stroke=str_c, sw=1.8, rx=6))
        f.append(text(x0 + 16, cy + 24, title, size=12.5, bold=True, anchor="start", color=INK))
        f.append(text(x0 + 16, cy + 40, desc, size=10.5, color=MUTED, anchor="start"))
        f.append(rect(x0 + w_box - 140, cy + 8, 128, 32, fill="#ffffff", stroke=str_c, sw=1.4, rx=4))
        f.append(text(x0 + w_box - 76, cy + 29, rate, size=13, bold=True, color=str_c))

        if i < len(layers) - 1:
            arrow_x = x0 + w_box / 2
            f.append(line(arrow_x, cy + lh - 12, arrow_x, cy + lh, color=LINE, sw=1.5))
            f.append(line(arrow_x - 3, cy + lh - 3, arrow_x, cy + lh, color=LINE, sw=1.5))
            f.append(line(arrow_x + 3, cy + lh - 3, arrow_x, cy + lh, color=LINE, sw=1.5))

    f.append(text(W / 2, y0 + len(layers) * lh + 20,
                  "Бодова швидкість задає фізику передачі на дроті; корисний бітрейт (Goodput) визначається математикою кодування та протоколами",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "throughput-layers.svg"), W, H, *f)


if __name__ == '__main__':
    fig_symbol_vs_bit()
    fig_modulation_ladder()
    fig_throughput_layers()
    print("Всі фігури успішно згенеровано у img/")
