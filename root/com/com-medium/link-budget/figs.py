# -*- coding: utf-8 -*-
import sys
import os

# Add scripts dir to path (4 levels up from book/communications/propagation/link-budget)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def make_link_budget_chain():
    w, h = 820, 360
    frags = []
    
    # Background panel
    frags.append(rect(10, 40, 800, 300, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=8))
    
    # 1. Transmitter Block (TX)
    frags.append(rect(25, 65, 170, 255, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    frags.append(text(110, 88, "Передавач (TX)", size=15, color="#1e40af", bold=True))
    frags.append(fitbox(35, 105, 150, 45, "Потужність P_TX\n+30 dBm (1 Вт)", size=12, fill="#ffffff", stroke="#93c5fd"))
    frags.append(fitbox(35, 160, 150, 45, "Втрати кабелю L_tx\n-2 dB", size=12, fill="#ffffff", stroke="#93c5fd"))
    frags.append(fitbox(35, 215, 150, 45, "Антена TX G_TX\n+14 dBi", size=12, fill="#ffffff", stroke="#93c5fd"))
    frags.append(fitbox(35, 270, 150, 40, "EIRP = +42 dBm", size=13, fill="#dbeafe", stroke="#2563eb", bold=True, color="#1e40af"))
    
    # Arrow TX -> Channel
    frags.append(arrow(195, 190, 225, 190, color="#2563eb", sw=2))
    
    # 2. Propagation Channel Block
    frags.append(rect(230, 65, 340, 255, fill="#fefce8", stroke="#eab308", sw=1.5, rx=6))
    frags.append(text(400, 88, "Середовище поширення (Channel)", size=15, color="#854d0e", bold=True))
    frags.append(fitbox(245, 105, 150, 45, "Втрати простору FSPL\n-130 dB", size=12, fill="#ffffff", stroke="#fef08a"))
    frags.append(fitbox(405, 105, 150, 45, "Атмосфера L_atm\n-2 dB", size=12, fill="#ffffff", stroke="#fef08a"))
    frags.append(fitbox(245, 160, 150, 45, "Завади/Поляризація L_misc\n-3 dB", size=12, fill="#ffffff", stroke="#fef08a"))
    frags.append(fitbox(405, 160, 150, 45, "Запас на завмирання L_fade\n-15 dB", size=12, fill="#ffffff", stroke="#fef08a"))
    frags.append(fitbox(245, 220, 310, 80, "Загальні втрати траси (Path Loss):\nL_total = FSPL + L_atm + L_misc + L_fade\nL_total = 150 dB", size=13, fill="#fef9c3", stroke="#ca8a04", bold=True, color="#713f12"))
    
    # Arrow Channel -> RX
    frags.append(arrow(570, 190, 600, 190, color="#ca8a04", sw=2))
    
    # 3. Receiver Block (RX)
    frags.append(rect(605, 65, 190, 255, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    frags.append(text(700, 88, "Приймач (RX)", size=15, color="#166534", bold=True))
    frags.append(fitbox(615, 105, 170, 45, "Антена RX G_RX\n+12 dBi", size=12, fill="#ffffff", stroke="#86efac"))
    frags.append(fitbox(615, 160, 170, 45, "Втрати кабелю L_rx\n-1 dB", size=12, fill="#ffffff", stroke="#86efac"))
    frags.append(fitbox(615, 215, 170, 45, "Потужність P_RX\n-97 dBm", size=13, fill="#dcfce7", stroke="#16a34a", bold=True, color="#14532d"))
    frags.append(fitbox(615, 270, 170, 40, "Чутливість P_sens = -110 dBm\nMargin = +13 dB", size=11.5, fill="#bbf7d0", stroke="#15803d", bold=True, color="#14532d"))
    
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    render(os.path.join(img_dir, 'link-budget-chain.svg'), w, h, *frags, title="Схема ланцюга передачі та складові балансу потужності")

def make_power_waterfall():
    w, h = 820, 380
    frags = []
    
    # Grid lines & scale
    # Power from +45 dBm down to -120 dBm
    frags.append(rect(10, 40, 800, 325, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=8))
    
    # Levels: +40, +20, 0, -20, -40, -60, -80, -100, -120
    levels = [
        (+40, 70), (+20, 110), (0, 150), (-20, 190), 
        (-40, 230), (-60, 270), (-80, 310), (-100, 350)
    ]
    for pwr, y_pos in levels:
        frags.append(line(70, y_pos, 790, y_pos, color="#f1f5f9", sw=1, dash="4,4"))
        frags.append(text(45, y_pos + 4, f"{pwr:+d}", size=11, color="#64748b", anchor="end"))
    frags.append(text(45, 55, "dBm", size=11, color="#475569", anchor="end", bold=True))
    
    # Sensitivity line
    frags.append(line(70, 350, 790, 350, color="#ef4444", sw=2, dash="6,3"))
    frags.append(textbox(710, 335, "Поріг чутливості P_sens = -100 dBm", size=11, fill="#fee2e2", stroke="#ef4444", color="#991b1b", bold=True)[0])
    
    # Waterfall bars
    bars = [
        ("P_TX\n+30 dBm", 0, 30, 90, 150, "#3b82f6"),
        ("L_tx\n-2 dB", 30, 28, 175, 235, "#ef4444"),
        ("G_TX\n+14 dBi", 28, 42, 260, 320, "#22c55e"),
        ("FSPL\n-130 dB", 42, -88, 345, 405, "#dc2626"),
        ("L_env\n-5 dB", -88, -93, 430, 490, "#b91c1c"),
        ("G_RX\n+12 dBi", -93, -81, 515, 575, "#16a34a"),
        ("L_rx\n-1 dB", -81, -82, 600, 660, "#ef4444"),
    ]
    
    def pwr_to_y(p):
        return 70 + (40 - p) * 2.0
    
    for name, p_start, p_end, x1, x2, col in bars:
        y1 = pwr_to_y(p_start)
        y2 = pwr_to_y(p_end)
        top = min(y1, y2)
        h_bar = abs(y2 - y1)
        if h_bar < 4: h_bar = 4
        frags.append(rect(x1, top, x2 - x1, h_bar, fill=col, stroke=col, sw=1, rx=3))
        lbl_y = top - 12 if p_end >= p_start else top + h_bar + 16
        if lbl_y > 330: lbl_y = top - 12
        frags.append(mtext((x1 + x2)/2, lbl_y, name.split("\n"), size=11, color="#1e293b", bold=True))
    
    # Margin highlight between P_RX (-82 dBm) and P_sens (-100 dBm)
    frags.append(arrow(630, pwr_to_y(-82), 630, pwr_to_y(-100), color="#15803d", sw=2))
    frags.append(arrow(630, pwr_to_y(-100), 630, pwr_to_y(-82), color="#15803d", sw=2))
    frags.append(textbox(710, 290, "Запас лінії (Margin)\nM = +18 dB", size=12, fill="#dcfce7", stroke="#16a34a", color="#14532d", bold=True)[0])
    
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    render(os.path.join(img_dir, 'power-waterfall.svg'), w, h, *frags, title="Профіль потужності радіолінії (Waterfall Chart)")

def make_receiver_sensitivity_stack():
    w, h = 780, 360
    frags = []
    
    frags.append(rect(10, 40, 760, 305, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=8))
    
    frags.append(rect(40, 260, 360, 60, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=6))
    frags.append(mtext(220, 283, ["Тепловий шум середовища (k_B · T)", "-174 dBm/Hz (при T = 290 K)"], size=13, color="#991b1b", bold=True))
    
    frags.append(rect(40, 195, 360, 55, fill="#ffedd5", stroke="#f97316", sw=1.5, rx=6))
    frags.append(mtext(220, 218, ["+ Смуга пропускання (10 · log10 B)", "+60 dB (для смуги B = 1 МГц)"], size=13, color="#c2410c", bold=True))
    
    frags.append(rect(40, 130, 360, 55, fill="#fef9c3", stroke="#eab308", sw=1.5, rx=6))
    frags.append(mtext(220, 153, ["+ Коефіцієнт шуму приймача (N_F)", "+5 dB (власні шуми підсилювача/LNA)"], size=13, color="#854d0e", bold=True))
    
    frags.append(rect(40, 65, 360, 55, fill="#dcfce7", stroke="#22c55e", sw=1.5, rx=6))
    frags.append(mtext(220, 88, ["+ Поріг сигнал/шум (SNR_min)", "+10 dB (для демодуляції QPSK)"], size=13, color="#166534", bold=True))
    
    frags.append(arrow(415, 290, 415, 92, color="#1e293b", sw=3))
    
    frags.append(rect(440, 65, 310, 255, fill="#f0fdf4", stroke="#16a34a", sw=2, rx=8))
    frags.append(text(595, 95, "Підсумковий поріг чутливості", size=15, color="#14532d", bold=True))
    
    eq_lines = [
        "P_sens = k_B·T + 10·log10(B) + N_F + SNR_min",
        "",
        "P_sens = -174 + 60 + 5 + 10",
        "",
        "P_sens = -99 dBm"
    ]
    frags.append(mtext(595, 135, eq_lines, size=13, color="#166534", anchor="middle", bold=True))
    frags.append(fitbox(460, 240, 270, 65, "Якщо прийнятий сигнал P_RX < -99 dBm,\nприймач не зможе декодувати дані\n(імовірність помилки BER розтеться).", size=11.5, fill="#ffffff", stroke="#86efac", color="#15803d"))
    
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    render(os.path.join(img_dir, 'receiver-sensitivity-stack.svg'), w, h, *frags, title="Формування порогу чутливості приймача")

def make_link_margin_vs_distance():
    w, h = 800, 360
    frags = []
    
    frags.append(rect(10, 40, 780, 305, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=8))
    
    frags.append(line(80, 310, 740, 310, color="#475569", sw=1.5))
    frags.append(line(80, 60, 80, 310, color="#475569", sw=1.5))
    
    frags.append(text(410, 338, "Відстань між антенами d (км)", size=13, color="#1e293b", bold=True))
    frags.append(text(40, 50, "Margin (dB)", size=12, color="#1e293b", bold=True))
    
    frags.append(line(80, 230, 740, 230, color="#ef4444", sw=2, dash="5,4"))
    frags.append(text(730, 222, "Поріг зв'язку (Margin = 0 dB)", size=11, color="#dc2626", anchor="end", bold=True))
    
    for margin_val, y_p in [(+30, 110), (+20, 150), (+10, 190), (0, 230), (-10, 270)]:
        if margin_val != 0:
            frags.append(line(80, y_p, 740, y_p, color="#f1f5f9", sw=1, dash="3,3"))
        frags.append(text(72, y_p + 4, f"{margin_val:+d}", size=11, color="#64748b", anchor="end"))
        
    for dist, x_p in [(1, 90), (5, 200), (10, 320), (20, 480), (50, 700)]:
        frags.append(line(x_p, 60, x_p, 310, color="#f1f5f9", sw=1, dash="3,3"))
        frags.append(text(x_p, 325, f"{dist}", size=11, color="#64748b"))
        
    pts_433 = [(90, 80), (200, 120), (320, 160), (480, 205), (700, 255)]
    pts_2400 = [(90, 130), (200, 170), (320, 210), (480, 255), (700, 305)]
    pts_5800 = [(90, 165), (200, 205), (320, 245), (480, 290), (700, 335)]
    
    def path_from_pts(pts):
        d = [f"M {pts[0][0]} {pts[0][1]}"]
        for px, py in pts[1:]:
            d.append(f"L {px} {py}")
        return " ".join(d)
        
    frags.append(f'<path d="{path_from_pts(pts_433)}" fill="none" stroke="#2563eb" stroke-width="2.5"/>')
    frags.append(f'<path d="{path_from_pts(pts_2400)}" fill="none" stroke="#16a34a" stroke-width="2.5"/>')
    frags.append(f'<path d="{path_from_pts(pts_5800)}" fill="none" stroke="#9333ea" stroke-width="2.5"/>')
    
    frags.append(rect(480, 70, 240, 90, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(line(495, 90, 525, 90, color="#2563eb", sw=2.5))
    frags.append(text(535, 94, "433 МГц (Sub-GHz LoRa)", size=11, color="#1e293b", anchor="start"))
    
    frags.append(line(495, 115, 525, 115, color="#16a34a", sw=2.5))
    frags.append(text(535, 119, "2.4 ГГц (Wi-Fi / BLE)", size=11, color="#1e293b", anchor="start"))
    
    frags.append(line(495, 140, 525, 140, color="#9333ea", sw=2.5))
    frags.append(text(535, 144, "5.8 ГГц (Radio Link)", size=11, color="#1e293b", anchor="start"))
    
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    render(os.path.join(img_dir, 'link-margin-vs-distance.svg'), w, h, *frags, title="Залежність запасу радіолінії від відстані для різних частот")

if __name__ == '__main__':
    make_link_budget_chain()
    make_power_waterfall()
    make_receiver_sensitivity_stack()
    make_link_margin_vs_distance()
    print("All figures generated successfully.")
