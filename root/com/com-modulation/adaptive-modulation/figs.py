# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def fig_shannon_stairs():
    w, h = 720, 420
    out = []
    out.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff"))
    out.append(text(w/2, 26, "Спектральна ефективність: границя Шеннона та сходова адаптація MCS", size=16, bold=True))
    
    ox, oy = 70, 360
    gw, gh = 600, 290
    
    out.append(arrow(ox, oy, ox + gw + 20, oy, color="#333333", sw=2))
    out.append(arrow(ox, oy, ox, oy - gh - 20, color="#333333", sw=2))
    out.append(text(ox + gw + 25, oy + 5, "SNR (дБ)", size=12, color=MUTED, anchor="start"))
    out.append(text(ox - 10, oy - gh - 20, "Спектральна ефективність η (біт/с/Гц)", size=12, color=MUTED, anchor="start"))
    
    for snr_db in range(0, 31, 5):
        x = ox + (snr_db / 30.0) * gw
        out.append(line(x, oy, x, oy - gh, color="#e5e7eb", sw=1, dash="3,3"))
        out.append(text(x, oy + 18, str(snr_db), size=11, color=MUTED))
        
    for eta in range(1, 9):
        y = oy - (eta / 8.0) * gh
        out.append(line(ox, y, ox + gw, y, color="#e5e7eb", sw=1, dash="3,3"))
        out.append(text(ox - 12, y + 4, str(eta), size=11, color=MUTED, anchor="end"))
        
    import math
    pts_shannon = []
    for step in range(0, 301):
        snr_db = step / 10.0
        snr_lin = 10.0 ** (snr_db / 10.0)
        c_b = math.log2(1.0 + snr_lin)
        if c_b > 8.5:
            c_b = 8.5
        x = ox + (snr_db / 30.0) * gw
        y = oy - (c_b / 8.0) * gh
        pts_shannon.append((x, y))
        
    path_shannon = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_shannon)
    out.append(f'<path d="{path_shannon}" fill="none" stroke="{POS}" stroke-width="2.5" stroke-dasharray="6,3"/>')
    out.append(text(ox + 440, oy - 255, "Теоретична межа Шеннона", size=12, color=POS, bold=True, anchor="start"))
    
    stairs = [
        (0.0, 2.0, 0.0),
        (2.0, 5.0, 1.0),
        (5.0, 8.0, 1.5),
        (8.0, 12.0, 2.0),
        (12.0, 16.0, 3.0),
        (16.0, 20.0, 4.0),
        (20.0, 24.0, 5.0),
        (24.0, 27.0, 6.0),
        (27.0, 30.0, 6.67)
    ]
    
    pts_stairs = []
    for s_start, s_end, eta in stairs:
        x1 = ox + (s_start / 30.0) * gw
        x2 = ox + (s_end / 30.0) * gw
        y = oy - (eta / 8.0) * gh
        if not pts_stairs:
            pts_stairs.append((x1, oy))
        pts_stairs.append((x1, y))
        pts_stairs.append((x2, y))
        
    path_stairs = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_stairs)
    out.append(f'<path d="{path_stairs}" fill="none" stroke="{NEG}" stroke-width="3"/>')
    
    labels = [
        (3.5, 1.0, "QPSK 1/2"),
        (6.5, 1.5, "QPSK 3/4"),
        (10.0, 2.0, "16-QAM 1/2"),
        (14.0, 3.0, "16-QAM 3/4"),
        (18.0, 4.0, "64-QAM 2/3"),
        (22.0, 5.0, "64-QAM 5/6"),
        (25.5, 6.0, "256-QAM 3/4"),
        (28.5, 6.67, "256-QAM 5/6")
    ]
    for snr_val, eta_val, txt in labels:
        lx = ox + (snr_val / 30.0) * gw
        ly = oy - (eta_val / 8.0) * gh - 8
        out.append(text(lx, ly, txt, size=10, color=INK, bold=True))
        
    out.append(rect(450, 60, 230, 65, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    out.append(line(460, 80, 485, 80, color=POS, sw=2.5, dash="6,3"))
    out.append(text(495, 84, "Межа Шеннона (неперервна)", size=11, color=INK, anchor="start"))
    out.append(line(460, 105, 485, 105, color=NEG, sw=3))
    out.append(text(495, 109, "Дискретні рівні MCS", size=11, color=INK, anchor="start"))

    render(os.path.join(os.path.dirname(__file__), "img", "mcs-shannon-stairs.svg"), w, h, *out)

def fig_amc_architecture():
    w, h = 740, 320
    out = []
    out.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff"))
    out.append(text(w/2, 26, "Архітектура замкненої петлі адаптації лінку (Link Adaptation)", size=16, bold=True))

    tx_box = fitbox(30, 70, 170, 100, "ПЕРЕДАВАЧ (Tx)\n• Кодер FEC (R)\n• Модулятор (M)\n• Селектор MCS", fill="#eef2ff", stroke=NEG, sw=2)
    out.append(tx_box)
    
    ch_box = fitbox(270, 70, 180, 100, "РАДІОКАНАЛ\n• Загасання & Fading\n• Аддитивний шум\n• Z-простір (SNR)", fill="#fefce8", stroke="#eab308", sw=2)
    out.append(ch_box)
    
    rx_box = fitbox(520, 70, 190, 100, "ПРИЙМАЧ (Rx)\n• Демодулятор / FEC\n• Замір SINR / EVM\n• Квантувач CQI", fill="#ecfdf5", stroke=FIELD, sw=2)
    out.append(rx_box)
    
    out.append(arrow(200, 120, 270, 120, color=LINE, sw=2))
    out.append(text(235, 110, "Сигнал (MCS)", size=10, color=MUTED))
    
    out.append(arrow(450, 120, 520, 120, color=LINE, sw=2))
    out.append(text(485, 110, "Сигнал + Шум", size=10, color=MUTED))

    ctrl_box = fitbox(240, 210, 240, 80, "КОНТРОЛЕР АДАПТАЦІЇ (AMC)\n• Зовнішня петля (OLRC)\n• Гістерезис порогів\n• Оновлення MCS", fill="#fdf2f8", stroke=POS, sw=2)
    out.append(ctrl_box)
    
    out.append(line(615, 170, 615, 250, color=LINE, sw=2))
    out.append(arrow(615, 250, 480, 250, color=LINE, sw=2))
    out.append(text(555, 240, "Зворотний зв'язок: CQI + ACK/NACK", size=11, color=POS, bold=True))
    
    out.append(line(240, 250, 115, 250, color=LINE, sw=2))
    out.append(arrow(115, 250, 115, 170, color=LINE, sw=2))
    out.append(text(175, 240, "Новий MCS індекс", size=11, color=NEG, bold=True))

    render(os.path.join(os.path.dirname(__file__), "img", "amc-architecture.svg"), w, h, *out)

def fig_fading_mcs_adaptation():
    w, h = 740, 380
    out = []
    out.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff"))
    out.append(text(w/2, 26, "Динаміка замирань SNR та реакція алгоритму адаптації MCS", size=16, bold=True))

    ox, oy = 70, 330
    gw, gh = 620, 250
    
    out.append(arrow(ox, oy, ox + gw + 20, oy, color="#333333", sw=2))
    out.append(arrow(ox, oy, ox, oy - gh - 15, color="#333333", sw=2))
    out.append(text(ox + gw + 25, oy + 5, "Час t", size=12, color=MUTED, anchor="start"))
    out.append(text(ox - 10, oy - gh - 15, "Рівень (SNR / MCS)", size=12, color=MUTED, anchor="start"))

    import math
    snr_pts = []
    mcs_pts = []
    
    for t in range(0, 101):
        x = ox + (t / 100.0) * gw
        snr = 16.0 + 9.0 * math.sin(0.08 * t) + 4.0 * math.cos(0.22 * t) + 2.0 * math.sin(0.45 * t)
        if snr < 2.0: snr = 2.0
        if snr > 28.0: snr = 28.0
        
        y_snr = oy - (snr / 30.0) * gh
        snr_pts.append((x, y_snr))
        
        if snr < 9.0:
            mcs_val = 5.0
        elif snr < 17.0:
            mcs_val = 12.0
        elif snr < 24.0:
            mcs_val = 20.0
        else:
            mcs_val = 26.5
            
        y_mcs = oy - (mcs_val / 30.0) * gh
        mcs_pts.append((x, y_mcs))
        
    path_snr = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in snr_pts)
    out.append(f'<path d="{path_snr}" fill="none" stroke="#e11d48" stroke-width="2"/>')

    path_mcs = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in mcs_pts)
    out.append(f'<path d="{path_mcs}" fill="none" stroke="{NEG}" stroke-width="3"/>')
    
    for th_val, th_name in [(9.0, "Поріг MCS1/4 (9 дБ)"), (17.0, "Поріг MCS4/7 (17 дБ)"), (24.0, "Поріг MCS7/9 (24 дБ)")]:
        y_th = oy - (th_val / 30.0) * gh
        out.append(line(ox, y_th, ox + gw, y_th, color="#cbd5e1", sw=1, dash="4,4"))
        out.append(text(ox + gw - 5, y_th - 4, th_name, size=10, color=MUTED, anchor="end"))

    out.append(rect(80, 50, 260, 55, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    out.append(line(90, 68, 115, 68, color="#e11d48", sw=2))
    out.append(text(125, 72, "Миттєвий SINR каналу", size=11, color=INK, anchor="start"))
    out.append(line(90, 90, 115, 90, color=NEG, sw=3))
    out.append(text(125, 94, "Вибраний рівень MCS", size=11, color=INK, anchor="start"))

    render(os.path.join(os.path.dirname(__file__), "img", "fading-mcs-adaptation.svg"), w, h, *out)

if __name__ == "__main__":
    os.makedirs(os.path.join(os.path.dirname(__file__), "img"), exist_ok=True)
    fig_shannon_stairs()
    fig_amc_architecture()
    fig_fading_mcs_adaptation()
    print("Figures generated successfully!")
