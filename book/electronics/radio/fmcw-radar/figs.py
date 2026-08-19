# -*- coding: utf-8 -*-
"""Генератор векторних SVG-ілюстрацій для теми fmcw-radar."""

import sys
import os
import math

# Підключення svgkit із scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def fig_chirp_timing():
    """Фігура 1: Частотно-часова діаграма випроміненого (TX) та відбитого (RX) LFM-чірпів."""
    W, H = 820, 430
    f = []

    # Осі координат
    ox, oy = 90, 350
    w_axis, h_axis = 660, 280

    # Сітка та допоміжні лінії
    f.append(line(ox, oy, ox + w_axis, oy, color=LINE, sw=1.8))  # Вісь t
    f.append(line(ox, oy, ox, oy - h_axis, color=LINE, sw=1.8))  # Вісь f
    f.append(text(ox + w_axis - 10, oy + 28, "Час t", size=14, bold=True, anchor="end"))
    f.append(text(ox - 15, oy - h_axis + 15, "Частота f", size=14, bold=True, anchor="end"))

    # Позначки частоти f0 та f0 + B
    y_f0 = oy - 40
    y_fmax = oy - 240
    f.append(line(ox - 6, y_f0, ox, y_f0, color=LINE, sw=1.5))
    f.append(text(ox - 12, y_f0 + 5, "f₀", size=14, bold=True, anchor="end"))
    f.append(line(ox, y_f0, ox + 620, y_f0, color="#e2e8f0", sw=1.2, dash="4,4"))

    f.append(line(ox - 6, y_fmax, ox, y_fmax, color=LINE, sw=1.5))
    f.append(text(ox - 12, y_fmax + 5, "f₀ + B", size=14, bold=True, anchor="end"))
    f.append(line(ox, y_fmax, ox + 620, y_fmax, color="#e2e8f0", sw=1.2, dash="4,4"))

    # Смуга B (двостороння стрілка)
    x_b_arrow = ox + 30
    f.append(line(x_b_arrow, y_f0, x_b_arrow, y_fmax, color=FIELD, sw=2))
    f.append(line(x_b_arrow - 6, y_f0, x_b_arrow + 6, y_f0, color=FIELD, sw=2))
    f.append(line(x_b_arrow - 6, y_fmax, x_b_arrow + 6, y_fmax, color=FIELD, sw=2))
    f.append(textbox(x_b_arrow + 55, (y_f0 + y_fmax) / 2, "Смуга B\n(девіація)", size=12, pad=6, fill="#f0fff4", stroke=FIELD, color=FIELD, bold=True)[0])

    # Чірп 1 TX (червона лінія)
    t0_tx = ox + 60
    tc = 240
    t1_tx = t0_tx + tc
    f.append(line(t0_tx, y_f0, t1_tx, y_fmax, color=POS, sw=3))
    f.append(line(t1_tx, y_fmax, t1_tx, y_f0, color=POS, sw=1.5, dash="3,3"))

    # Чірп 2 TX
    t_idle = 40
    t0_tx2 = t1_tx + t_idle
    t1_tx2 = t0_tx2 + tc
    f.append(line(t0_tx2, y_f0, t1_tx2, y_fmax, color=POS, sw=3))

    # Чірп 1 RX (синя лінія, зсунута на tau)
    tau = 45
    t0_rx = t0_tx + tau
    t1_rx = t1_tx + tau
    f.append(line(t0_rx, y_f0, t1_rx, y_fmax, color=NEG, sw=2.5, dash="6,3"))

    # Чірп 2 RX
    t0_rx2 = t0_tx2 + tau
    t1_rx2 = t1_tx2 + tau
    f.append(line(t0_rx2, y_f0, t1_rx2, y_fmax, color=NEG, sw=2.5, dash="6,3"))

    # Затримка tau
    y_tau = oy + 12
    f.append(line(t0_tx, oy, t0_tx, y_tau + 10, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(t0_rx, oy, t0_rx, y_tau + 10, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(t0_tx, y_tau, t0_rx, y_tau, color=LINE, sw=1.5))
    f.append(text((t0_tx + t0_rx) / 2, y_tau + 18, "τ = 2R/c", size=12, bold=True))

    # Тривалість чірпа Tc
    y_tc = oy + 42
    f.append(line(t0_tx, y_tau + 10, t0_tx, y_tc + 10, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(t1_tx, oy, t1_tx, y_tc + 10, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(t0_tx, y_tc, t1_tx, y_tc, color=LINE, sw=1.5))
    f.append(text((t0_tx + t1_tx) / 2, y_tc + 18, "Тривалість чірпа Tc", size=12, bold=True))

    # Частота биття fb (вертикальна різниця між TX і RX)
    t_meas = t0_tx + 160
    f_tx_meas = y_f0 - (y_f0 - y_fmax) * (160 / tc)
    f_rx_meas = y_f0 - (y_f0 - y_fmax) * ((160 - tau) / tc)

    f.append(line(t_meas, f_tx_meas, t_meas, f_rx_meas, color="#d97706", sw=2.5))
    f.append(line(t_meas - 6, f_tx_meas, t_meas + 6, f_tx_meas, color="#d97706", sw=2))
    f.append(line(t_meas - 6, f_rx_meas, t_meas + 6, f_rx_meas, color="#d97706", sw=2))

    fb_box, _, _ = textbox(t_meas + 95, (f_tx_meas + f_rx_meas) / 2, "Частота биття\nfb = S · τ", size=12, pad=6, fill="#fffbeb", stroke="#d97706", color="#b45309", bold=True)
    f.append(fb_box)

    # Легенда та позначення чірпів
    f.append(textbox(ox + 160, oy - 270, "TX: випромінений чірп (нахил S = B/Tc)", size=12, pad=6, fill="#fdf2f2", stroke=POS, color=POS, bold=True)[0])
    f.append(textbox(ox + 460, oy - 270, "RX: відбитий чірп (затриманий на τ)", size=12, pad=6, fill="#eff6ff", stroke=NEG, color=NEG, bold=True)[0])

    render(os.path.join(IMG, "chirp-timing.svg"), W, H, *f)


def fig_fmcw_transceiver_block():
    """Фігура 2: Структурна схема прямого змішування (дечірпінгу) в FMCW-трансивері."""
    W, H = 840, 420
    f = []

    # Верхній тракт передавача (TX)
    # Синтезатор / ГУН
    f.append(fitbox(50, 150, 130, 60, "Генератор чірпів\n(PLL + VCO)", size=13, bold=True, fill="#eef2ff", stroke="#4f46e5"))

    # Дільник потужності
    f.append(arrow(180, 180, 230, 180, color=LINE, sw=2))
    f.append(fitbox(230, 150, 100, 60, "Дільник\nпотужності", size=13, bold=True, fill="#f8fafc", stroke=LINE))

    # Тракт TX до антени
    f.append(arrow(330, 180, 390, 180, color=LINE, sw=2))
    f.append(fitbox(390, 150, 80, 60, "Підсилювач\nPA", size=13, bold=True, fill="#fef2f2", stroke=POS))
    f.append(arrow(470, 180, 520, 180, color=LINE, sw=2))

    # Антена TX
    f.append(line(520, 180, 545, 180, color=POS, sw=2))
    f.append(line(545, 160, 545, 200, color=POS, sw=2.5))
    f.append(line(545, 160, 565, 150, color=POS, sw=2))
    f.append(line(545, 200, 565, 210, color=POS, sw=2))
    f.append(line(565, 150, 565, 210, color=POS, sw=2))
    f.append(text(555, 138, "TX антена", size=12, bold=True, color=POS))

    # Відвід гетеродина LO на змішувач (вниз)
    f.append(arrow(280, 210, 280, 290, color=LINE, sw=2))
    f.append(text(295, 255, "Опорний LO", size=11, bold=True, color=MUTED, anchor="start"))

    # Нижній тракт приймача (RX)
    # Антена RX
    f.append(line(520, 320, 545, 320, color=NEG, sw=2))
    f.append(line(545, 300, 545, 340, color=NEG, sw=2.5))
    f.append(line(545, 300, 565, 290, color=NEG, sw=2))
    f.append(line(545, 340, 565, 350, color=NEG, sw=2))
    f.append(line(565, 290, 565, 350, color=NEG, sw=2))
    f.append(text(555, 368, "RX антена", size=12, bold=True, color=NEG))

    # LNA
    f.append(arrow(520, 320, 460, 320, color=LINE, sw=2))
    f.append(fitbox(380, 290, 80, 60, "МШП\n(LNA)", size=13, bold=True, fill="#eff6ff", stroke=NEG))

    # Змішувач (I/Q Mixer)
    f.append(arrow(380, 320, 320, 320, color=LINE, sw=2))
    f.append(circle(280, 320, 26, fill="#fffbeb", stroke="#d97706", sw=2))
    f.append(line(265, 305, 295, 335, color="#d97706", sw=2))
    f.append(line(265, 335, 295, 305, color="#d97706", sw=2))
    f.append(text(280, 362, "Змішувач", size=12, bold=True, color="#b45309"))

    # Тракт ПЧ: ФВЧ/ФНЧ еквалайзер
    f.append(arrow(254, 320, 200, 320, color=LINE, sw=2))
    f.append(fitbox(110, 290, 90, 60, "Фільтр ПЧ\n(HPF + LPF)", size=12, bold=True, fill="#f0fdf4", stroke=FIELD))

    # АЦП
    f.append(arrow(110, 320, 60, 320, color=LINE, sw=2))
    # Блок обробки DSP зліва внизу
    f.append(fitbox(45, 290, 65, 60, "АЦП\n(ADC)", size=12, bold=True, fill="#f8fafc", stroke=LINE))

    # Хвилі між антенами і ціллю
    f.append(text(620, 160, "Випромінювання s_tx(t)", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(620, 335, "Відбиття s_rx(t) = s_tx(t - τ)", size=12, color=NEG, bold=True, anchor="start"))

    # Ціль
    f.append(textbox(750, 245, "Ціль\n(R, v, θ)", size=13, pad=10, fill="#fef3c7", stroke="#d97706", bold=True)[0])
    f.append(arrow(580, 175, 700, 230, color=POS, sw=1.8))
    f.append(arrow(700, 260, 580, 315, color=NEG, sw=1.8))

    # Пояснювальний блок вгорі
    f.append(textbox(280, 60, "Пряме змішування (дечірпінг):\nОпорний сигнал ГУН змішується з відбитим, утворюючи сигнал биття на звукових/мегагерцових ПЧ", size=13, pad=8, fill="#f8fafc", stroke=MUTED, bold=False)[0])

    render(os.path.join(IMG, "fmcw-transceiver-block.svg"), W, H, *f)


def fig_range_doppler_2dfft():
    """Фігура 3: Двовимірне перетворення Фур'є (2D-FFT): Швидкий і Повільний час."""
    W, H = 880, 450
    f = []

    # Лівий блок: Матриця відліків АЦП (Кадр)
    f.append(text(250, 35, "Радарний кадр (Radar Data Matrix)", size=15, bold=True))

    mx, my, mw, mh = 110, 75, 270, 220
    f.append(rect(mx, my, mw, mh, fill="#f8fafc", stroke=LINE, sw=1.8))

    # Рядки матриці (чірпи)
    for i in range(1, 6):
        y_l = my + i * (mh / 6)
        f.append(line(mx, y_l, mx + mw, y_l, color="#cbd5e1", sw=1.2, dash="3,3"))

    # Стовпчики матриці (відліки)
    for j in range(1, 8):
        x_l = mx + j * (mw / 8)
        f.append(line(x_l, my, x_l, my + mh, color="#cbd5e1", sw=1.2, dash="3,3"))

    # Позначення осей Fast Time та Slow Time
    f.append(arrow(mx, my - 15, mx + mw, my - 15, color=POS, sw=2))
    f.append(text(mx + mw / 2, my - 24, "Швидкий час (Fast Time): N_adc відліків", size=12, bold=True, color=POS))

    f.append(arrow(mx - 15, my, mx - 15, my + mh, color=NEG, sw=2))
    f.append(textbox(55, my + mh / 2, "Повільний час\n(Slow Time)\nN_chirp чірпів", size=11, pad=6, fill="#eff6ff", stroke=NEG, color=NEG, bold=True)[0])

    # Пояснення 1D Range-FFT внизу лівого блоку
    f.append(textbox(245, my + mh + 42, "1D Range-FFT (по рядках):\nВизначає частоту биття fb → Дальність R", size=12, pad=6, fill="#fdf2f2", stroke=POS, color=POS, bold=True)[0])

    # Стрілка переходу між матрицями
    mid_x = (mx + mw + 500) / 2
    f.append(textbox(mid_x, my + mh / 2 - 35, "2D-FFT\nОбробка", size=12, pad=6, fill="#eef2ff", stroke="#4f46e5", color="#4f46e5", bold=True)[0])
    f.append(arrow(mx + mw + 10, my + mh / 2 + 10, 490, my + mh / 2 + 10, color="#4f46e5", sw=2.5))

    # Правий блок: Range-Doppler карта
    rx, ry, rw, rh = 500, 75, 270, 220
    f.append(text(rx + rw / 2, 35, "Range-Doppler карта (R-D Map)", size=15, bold=True))
    f.append(rect(rx, ry, rw, rh, fill="#0f172a", stroke=LINE, sw=1.8))

    # Координатні осі на карті
    f.append(line(rx, ry + rh / 2, rx + rw, ry + rh / 2, color="#475569", sw=1.5, dash="4,4"))  # Швидкість v = 0
    f.append(line(rx + 20, ry, rx + 20, ry + rh, color="#475569", sw=1.5))  # Дальність R = 0

    # Пік цілі на карті
    t_px, t_py = rx + 150, ry + 65
    f.append(circle(t_px, t_py, 20, fill="#fee2e2", stroke="#ef4444", sw=1.5))
    f.append(circle(t_px, t_py, 13, fill="#fef3c7", stroke="#f59e0b", sw=1.5))
    f.append(circle(t_px, t_py, 6, fill="#fbbf24", stroke="#b45309", sw=1.5))

    f.append(line(t_px, ry + rh, t_px, t_py + 22, color="#38bdf8", sw=1.2, dash="3,3"))
    f.append(line(rx, t_py, t_px - 22, t_py, color="#38bdf8", sw=1.2, dash="3,3"))

    f.append(text(t_px + 48, t_py - 10, "Ціль: (R₀, v₀)", size=13, bold=True, color="#fbbf24"))

    # Підписи осей правої карти
    f.append(arrow(rx + 20, ry + rh + 15, rx + rw, ry + rh + 15, color=LINE, sw=2))
    f.append(text(rx + rw / 2 + 10, ry + rh + 28, "Дальність R (Range Bin)", size=12, bold=True))

    f.append(arrow(rx - 15, ry + rh, rx - 15, ry, color=LINE, sw=2))
    f.append(textbox(rx - 55, ry + rh / 2, "Радіальна швидкість\n(Doppler Bin)", size=11, pad=6, fill="#f8fafc", stroke=LINE, bold=True)[0])

    f.append(textbox(rx + rw / 2, ry + rh + 58, "2D Doppler-FFT (по стовпчиках):\nВимірює фазове обертання між чірпами → Швидкість v", size=12, pad=6, fill="#f0fdf4", stroke=FIELD, color=FIELD, bold=True)[0])

    render(os.path.join(IMG, "range-doppler-2dfft.svg"), W, H, *f)


def fig_mimo_virtual_array():
    """Фігура 4: Віртуальна антенна решітка у MIMO FMCW радарі."""
    W, H = 840, 430
    f = []

    # Верхній блок: Фізичні антени (2 TX + 4 RX)
    f.append(text(420, 30, "Фізична конфігурація антен (на друкованій платі)", size=15, bold=True))

    # Передавальні антени TX1, TX2 (відстань 4d)
    y_phys = 85
    tx1_x = 100
    tx2_x = 100 + 4 * 60  # 340

    f.append(textbox(tx1_x, y_phys, "TX 1", size=13, pad=10, fill="#fef2f2", stroke=POS, color=POS, bold=True)[0])
    f.append(textbox(tx2_x, y_phys, "TX 2", size=13, pad=10, fill="#fef2f2", stroke=POS, color=POS, bold=True)[0])

    f.append(line(tx1_x, y_phys + 28, tx2_x, y_phys + 28, color=POS, sw=1.8))
    f.append(line(tx1_x, y_phys + 23, tx1_x, y_phys + 33, color=POS, sw=1.8))
    f.append(line(tx2_x, y_phys + 23, tx2_x, y_phys + 33, color=POS, sw=1.8))
    f.append(text((tx1_x + tx2_x) / 2, y_phys + 45, "Відстань d_TX = 4 · d = 2 · λ", size=12, bold=True, color=POS))

    # Приймальні антени RX1..RX4 (відстань d = lambda/2)
    rx_start_x = 520
    d_rx = 60
    for i in range(4):
        cur_rx_x = rx_start_x + i * d_rx
        f.append(textbox(cur_rx_x, y_phys, f"RX {i+1}", size=13, pad=8, fill="#eff6ff", stroke=NEG, color=NEG, bold=True)[0])

    f.append(line(rx_start_x, y_phys + 28, rx_start_x + 3 * d_rx, y_phys + 28, color=NEG, sw=1.8))
    f.append(text(rx_start_x + 1.5 * d_rx, y_phys + 45, "Крок d_RX = d = λ/2", size=12, bold=True, color=NEG))

    # Стрілка та блок синтезу віртуальної апертури
    f.append(arrow(420, y_phys + 65, 420, y_phys + 90, color="#4f46e5", sw=2.5))
    f.append(textbox(420, y_phys + 115, "Просторове згортання (MIMO Synthesis: 2 TX × 4 RX)", size=12, pad=6, fill="#eef2ff", stroke="#4f46e5", color="#4f46e5", bold=True)[0])
    f.append(arrow(420, y_phys + 140, 420, y_phys + 165, color="#4f46e5", sw=2.5))

    # Нижній блок: Синтезована віртуальна решітка з 8 елементів
    y_virt = 295
    f.append(text(420, y_virt - 35, "Еквівалентна віртуальна антенна решітка (8 віртуальних приймачів)", size=15, bold=True))

    v_start_x = 100
    for k in range(8):
        vx = v_start_x + k * 85
        # Перші 4 згенеровані парою TX1-RX, другі 4 - парою TX2-RX
        if k < 4:
            f_color = "#fef2f2"
            s_color = POS
            txt_label = f"V {k+1}\n(T1·R{k+1})"
        else:
            f_color = "#eff6ff"
            s_color = NEG
            txt_label = f"V {k+1}\n(T2·R{k-3})"

        f.append(fitbox(vx - 36, y_virt, 72, 54, txt_label, size=11, bold=True, fill=f_color, stroke=s_color))

    # Лінія віртуальної апертури
    f.append(line(v_start_x, y_virt + 65, v_start_x + 7 * 85, y_virt + 65, color=FIELD, sw=2))
    f.append(line(v_start_x, y_virt + 58, v_start_x, y_virt + 72, color=FIELD, sw=2))
    f.append(line(v_start_x + 7 * 85, y_virt + 58, v_start_x + 7 * 85, y_virt + 72, color=FIELD, sw=2))
    f.append(text(v_start_x + 3.5 * 85, y_virt + 85, "Розширена віртуальна апертура D_v = 7 · (λ/2) → Висока кутова роздільність Δθ ≈ λ / D_v", size=13, bold=True, color=FIELD))

    render(os.path.join(IMG, "mimo-virtual-array.svg"), W, H, *f)


if __name__ == "__main__":
    fig_chirp_timing()
    fig_fmcw_transceiver_block()
    fig_range_doppler_2dfft()
    fig_mimo_virtual_array()
    print("All figures generated successfully.")
