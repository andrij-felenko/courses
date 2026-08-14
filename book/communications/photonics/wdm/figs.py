# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Палітра довжин хвиль (кольорове кодування каналів)
C1 = "#e74c3c"   # червоний   (1530 нм / Лямбда 1)
C2 = "#e67e22"   # помаранчевий (1540 нм / Лямбда 2)
C3 = "#27ae60"   # зелений    (1550 нм / Лямбда 3)
C4 = "#2980b9"   # синій      (1560 нм / Лямбда 4)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Принцип спектрального ущільнення (WDM)
# ═══════════════════════════════════════════════════════════════════════════
def fig_wdm_principle():
    W, H = 760, 360
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W / 2, 28, 'Принцип спектрального ущільнення (WDM)', 17, INK, 'middle', bold=True))

    # Передавачі (Tx1..Tx4)
    tx_x = 40
    tx_ys = [80, 140, 200, 260]
    colors = [C1, C2, C3, C4]
    labels = ['Tx₁ (λ₁ = 1530 нм)', 'Tx₂ (λ₂ = 1540 нм)', 'Tx₃ (λ₃ = 1550 нм)', 'Tx₄ (λ₄ = 1560 нм)']

    mux_x = 190
    mux_y = 60
    mux_w, mux_h = 70, 220

    # Блок MUX
    f.append(rect(mux_x, mux_y, mux_w, mux_h, fill="#f0f4f8", stroke=LINE, sw=1.8, rx=8))
    f.append(mtext(mux_x + mux_w / 2, mux_y + mux_h / 2 - 8, "МУКС\nMUX\n(ущільнювач)", 12, INK, "middle", bold=True))

    for i in range(4):
        y = tx_ys[i]
        col = colors[i]
        lbl = labels[i]
        f.append(rect(tx_x, y - 18, 110, 36, fill=FILL, stroke=col, sw=1.5, rx=5))
        f.append(text(tx_x + 55, y + 4, lbl, 11, col, 'middle', bold=True))
        # Лінія від Tx до MUX
        f.append(line(tx_x + 110, y, mux_x, y, color=col, sw=2.0))
        f.append(arrow(mux_x - 12, y, mux_x, y, color=col, sw=2.0))

    # Оптоволоконна лінія з EDFA
    fib_start_x = mux_x + mux_w
    fib_y = mux_y + mux_h / 2
    edfa_x = 370
    edfa_w, edfa_h = 64, 40
    demux_x = 500
    demux_w, demux_h = 70, 220

    # Волокно від MUX до EDFA (багатоколірний пучок — товста лінія з пунктирами або багатьма кольорами)
    f.append(line(fib_start_x, fib_y, edfa_x, fib_y, color=INK, sw=4.0))
    f.append(line(fib_start_x, fib_y - 1.5, edfa_x, fib_y - 1.5, color=C1, sw=1.2))
    f.append(line(fib_start_x, fib_y + 1.5, edfa_x, fib_y + 1.5, color=C3, sw=1.2))
    f.append(text(fib_start_x + 35, fib_y - 14, 'одне одномодове волокно (Σ λᵢ)', 11, INK, 'middle'))

    # EDFA підсилювач
    f.append(rect(edfa_x, fib_y - edfa_h / 2, edfa_w, edfa_h, fill="#fde9c8", stroke="#d35400", sw=1.5, rx=6))
    f.append(text(edfa_x + edfa_w / 2, fib_y + 4, 'EDFA', 13, "#d35400", 'middle', bold=True))
    f.append(text(edfa_x + edfa_w / 2, fib_y + edfa_h / 2 + 14, 'підсилювач', 10, MUTED, 'middle'))

    # Волокно від EDFA до DEMUX
    fib2_start_x = edfa_x + edfa_w
    demux_y = mux_y
    f.append(line(fib2_start_x, fib_y, demux_x, fib_y, color=INK, sw=4.0))
    f.append(line(fib2_start_x, fib_y - 1.5, demux_x, fib_y - 1.5, color=C2, sw=1.2))
    f.append(line(fib2_start_x, fib_y + 1.5, demux_x, fib_y + 1.5, color=C4, sw=1.2))

    # Блок DEMUX
    f.append(rect(demux_x, demux_y, demux_w, demux_h, fill="#f0f4f8", stroke=LINE, sw=1.8, rx=8))
    f.append(mtext(demux_x + demux_w / 2, demux_y + demux_h / 2 - 8, "ДЕМУКС\nDEMUX\n(розділювач)", 12, INK, "middle", bold=True))

    # Приймачі (Rx1..Rx4)
    rx_x = 620
    for i in range(4):
        y = tx_ys[i]
        col = colors[i]
        lbl = f'Rx₁ (λ₁)' if i == 0 else (f'Rx₂ (λ₂)' if i == 1 else (f'Rx₃ (λ₃)' if i == 2 else f'Rx₄ (λ₄)'))
        # Лінія від DEMUX до Rx
        f.append(line(demux_x + demux_w, y, rx_x, y, color=col, sw=2.0))
        f.append(arrow(rx_x - 12, y, rx_x, y, color=col, sw=2.0))
        f.append(rect(rx_x, y - 18, 90, 36, fill=FILL, stroke=col, sw=1.5, rx=5))
        f.append(text(rx_x + 45, y + 4, lbl, 11, col, 'middle', bold=True))

    f.append(text(W / 2, H - 14,
                  'Багато незалежних оптичних сигналів передаються одночасно через одну скляну нитку',
                  12, MUTED, 'middle'))

    render(os.path.join(IMG, 'wdm-principle.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Порівняння сіток CWDM та DWDM
# ═══════════════════════════════════════════════════════════════════════════
def fig_cwdm_vs_dwdm():
    W, H = 760, 360
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W / 2, 28, 'Порівняння спектральних сіток CWDM та DWDM', 17, INK, 'middle', bold=True))

    # Розділ CWDM (Верхня частина)
    f.append(text(50, 65, 'Грубе ущільнення (CWDM): крок 20 нм (широкі пропускні смуги)', 13, POS, 'start', bold=True))
    f.append(line(50, 125, 710, 125, color=MUTED, sw=1.2)) # ось оптичного спектра

    cwdm_x_centers = [120, 250, 380, 510, 640]
    cwdm_labels = ['1471 нм', '1491 нм', '1511 нм', '1531 нм', '1551 нм']
    for i, cx in enumerate(cwdm_x_centers):
        # Широкий дзвоноподібний контур каналу CWDM
        path_d = f"M {cx-45} 125 Q {cx-20} 75 {cx} 75 Q {cx+20} 75 {cx+45} 125 Z"
        f.append(f'<path d="{path_d}" fill="#fdecea" stroke="{POS}" stroke-width="1.5"/>')
        f.append(text(cx, 142, cwdm_labels[i], 11, POS, 'middle'))

    f.append(line(250, 95, 380, 95, color=POS, sw=1.0, dash="3,3"))
    f.append(text(315, 90, 'Δλ = 20 нм', 11, POS, 'middle', bold=True))

    # Розділ DWDM (Нижня частина)
    f.append(text(50, 195, 'Щільне ущільнення (DWDM): крок 100 ГГц / 50 ГГц (0.8 / 0.4 нм у C-діапазоні)', 13, NEG, 'start', bold=True))
    f.append(line(50, 290, 710, 290, color=MUTED, sw=1.2)) # ось оптичного спектра

    # Виділення вікна C-band (1530-1565 нм / EDFA gain envelope)
    f.append(rect(340, 208, 350, 92, fill="#eaf0fd", stroke="none", sw=0, rx=4))
    f.append(text(515, 222, 'C-band (1530–1565 нм) — смуга підсилення EDFA', 11, NEG, 'middle', italic=True))

    dwdm_x_start = 360
    for i in range(12):
        cx = dwdm_x_start + i * 26
        path_d = f"M {cx-8} 290 Q {cx-3} 230 {cx} 230 Q {cx+3} 230 {cx+8} 290 Z"
        f.append(f'<path d="{path_d}" fill="#d0e1fd" stroke="{NEG}" stroke-width="1.2"/>')

    f.append(line(360, 245, 386, 245, color=NEG, sw=1.0, dash="2,2"))
    f.append(text(373, 240, '100 ГГц (0.8 нм)', 9, NEG, 'middle', bold=True))
    f.append(text(503, 308, 'Спектральна сітка ITU-T G.694.1 (до 96+ каналів у C-band)', 11, MUTED, 'middle'))

    f.append(text(W / 2, H - 14,
                  'CWDM використовує неохолоджувані лазери для коротких відстаней, DWDM — прецизійні лазери й EDFA',
                  12, MUTED, 'middle'))

    render(os.path.join(IMG, 'cwdm-vs-dwdm.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Принцип роботи AWG (Arrayed Waveguide Grating)
# ═══════════════════════════════════════════════════════════════════════════
def fig_awg_demux():
    W, H = 760, 360
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W / 2, 28, 'Мультиплексор на масиві хвилеводів (AWG)', 17, INK, 'middle', bold=True))

    # Вхідний хвилевід
    in_x1, in_x2 = 40, 140
    cy = 180
    f.append(line(in_x1, cy, in_x2, cy, color=INK, sw=3.5))
    f.append(text(in_x1 + 45, cy - 14, 'Вхід (Σ λᵢ)', 12, INK, 'middle', bold=True))

    # Вхідна область вільного поширення (FPR1)
    fpr1_x = 140
    fpr1_w, fpr1_h = 70, 120
    f.append(rect(fpr1_x, cy - fpr1_h / 2, fpr1_w, fpr1_h, fill="#e8f4f8", stroke=LINE, sw=1.5, rx=15))
    f.append(mtext(fpr1_x + fpr1_w / 2, cy + 4, "FPR1\n(змішувач)", 11, INK, "middle"))

    # Масив хвилеводів (Arrayed Waveguides) з наростаючою довжиною (ΔL)
    awg_x1 = fpr1_x + fpr1_w
    awg_x2 = 480
    num_wg = 5
    y_starts = [cy - 40, cy - 20, cy, cy + 20, cy + 40]
    y_ends   = [cy - 40, cy - 20, cy, cy + 20, cy + 40]

    for i in range(num_wg):
        ys = y_starts[i]
        ye = y_ends[i]
        # Дуга зі збільшуваним вигоном угору для створення різниці ходу ΔL
        arch = (i - 2) * 18
        mid_x = (awg_x1 + awg_x2) / 2
        mid_y = (ys + ye) / 2 - 35 + arch
        path_d = f"M {awg_x1} {ys} Q {mid_x} {mid_y} {awg_x2} {ye}"
        f.append(f'<path d="{path_d}" fill="none" stroke="{FIELD}" stroke-width="2.0"/>')

    f.append(text((awg_x1 + awg_x2) / 2, cy - 65, 'Масив хвилеводів із різницею довжин ΔL', 12, FIELD, 'middle', bold=True))
    f.append(text((awg_x1 + awg_x2) / 2, cy - 48, 'фіксований фазовий зсув Δφ = β·ΔL', 10, MUTED, 'middle'))

    # Вихідна область вільного поширення (FPR2)
    fpr2_x = awg_x2
    fpr2_w, fpr2_h = 70, 120
    f.append(rect(fpr2_x, cy - fpr2_h / 2, fpr2_w, fpr2_h, fill="#e8f4f8", stroke=LINE, sw=1.5, rx=15))
    f.append(mtext(fpr2_x + fpr2_w / 2, cy + 4, "FPR2\n(фокусування)", 11, INK, "middle"))

    # Вихідні окремі хвилеводи (фокусування в залежності від λ)
    out_x1 = fpr2_x + fpr2_w
    out_x2 = 640
    out_ys = [cy - 45, cy - 15, cy + 15, cy + 45]
    out_cols = [C1, C2, C3, C4]
    out_lbls = ['λ₁ (1530 нм)', 'λ₂ (1540 нм)', 'λ₃ (1550 нм)', 'λ₄ (1560 нм)']

    for i in range(4):
        yo = out_ys[i]
        col = out_cols[i]
        lbl = out_lbls[i]
        f.append(line(out_x1, yo, out_x2, yo, color=col, sw=2.2))
        f.append(arrow(out_x2 - 10, yo, out_x2, yo, color=col, sw=2.2))
        f.append(text(out_x2 + 8, yo + 4, lbl, 11, col, 'start', bold=True))

    f.append(text(W / 2, H - 14,
                  'Інтерференція світла з фазовим зсувом розводить різні довжини хвиль у різні вихідні канали',
                  12, MUTED, 'middle'))

    render(os.path.join(IMG, 'awg-demux.svg'), W, H, *f)


if __name__ == '__main__':
    fig_wdm_principle()
    fig_cwdm_vs_dwdm()
    fig_awg_demux()
    print("All figures generated successfully.")
