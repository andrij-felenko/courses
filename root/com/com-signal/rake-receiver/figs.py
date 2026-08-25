# -*- coding: utf-8 -*-
import sys, os

# Add scripts directory to path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Fig 1: Багатопроменеве поширення та імпульсна характеристика ──────────────
def fig_multipath_channel():
    W, H = 740, 340
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    
    # Title
    p.append(text(W/2, 24, "Багатопроменевий канал та імпульсна характеристика h(t)", size=15, bold=True))
    
    # Left side: Geometry (Tx, Rx, Obstacles)
    p.append(rect(20, 45, 330, 275, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    p.append(text(185, 68, "Фізика поширення радіохвиль", size=13, bold=True, color=LINE))
    
    # Base station (Tx)
    p.append(rect(40, 160, 30, 80, fill="#3b82f6", stroke="#1d4ed8", rx=4))
    p.append(text(55, 205, "Tx", size=12, color="#ffffff", bold=True))
    # Antenna
    p.append(line(55, 160, 55, 140, color="#1d4ed8", sw=2))
    p.append(circle(55, 136, 5, fill="#1d4ed8", stroke="#1d4ed8"))
    
    # Receiver (Rx)
    p.append(rect(290, 170, 30, 70, fill="#10b981", stroke="#047857", rx=4))
    p.append(text(305, 210, "Rx", size=12, color="#ffffff", bold=True))
    # Antenna
    p.append(line(305, 170, 305, 150, color="#047857", sw=2))
    p.append(circle(305, 146, 5, fill="#047857", stroke="#047857"))
    
    # Obstacles
    # Building 1 (top)
    p.append(rect(160, 85, 45, 60, fill="#94a3b8", stroke="#475569", rx=3))
    p.append(text(182.5, 118, "Будинок 1", size=10, color="#ffffff", bold=True))
    
    # Hill / Building 2 (bottom)
    p.append(rect(170, 245, 55, 55, fill="#94a3b8", stroke="#475569", rx=3))
    p.append(text(197.5, 275, "Будинок 2", size=10, color="#ffffff", bold=True))
    
    # Rays
    # Ray 0: Direct LOS (Ray 0)
    p.append(arrow(60, 140, 300, 148, color="#2563eb", sw=2.2))
    b0, w0, h0 = textbox(170, 152, "Промінь 0: прямий (τ₀ = 0)", size=10, pad=4, fill="#eff6ff", stroke="#3b82f6")
    p.append(b0)
    
    # Ray 1: Top reflection
    p.append(line(60, 136, 160, 95, color="#dc2626", sw=1.8, dash="4,3"))
    p.append(arrow(160, 95, 300, 144, color="#dc2626", sw=1.8))
    b1, w1, h1 = textbox(140, 75, "Промінь 1 (τ₁)", size=10, pad=4, fill="#fef2f2", stroke="#ef4444")
    p.append(b1)
    
    # Ray 2: Bottom reflection
    p.append(line(60, 142, 170, 260, color="#d97706", sw=1.8, dash="4,3"))
    p.append(arrow(170, 260, 300, 154, color="#d97706", sw=1.8))
    b2, w2, h2 = textbox(105, 220, "Промінь 2 (τ₂)", size=10, pad=4, fill="#fffbeb", stroke="#f59e0b")
    p.append(b2)
    
    # Right side: Channel Impulse Response h(t)
    p.append(rect(370, 45, 350, 275, fill="#fafafa", stroke="#cbd5e1", rx=8))
    p.append(text(545, 68, "Імпульсна характеристика h(t)", size=13, bold=True, color=LINE))
    
    # Axes
    p.append(arrow(400, 260, 700, 260, color=LINE, sw=1.5)) # t axis
    p.append(arrow(410, 270, 410, 90, color=LINE, sw=1.5))  # |h| axis
    p.append(text(708, 264, "t", size=12, bold=True, color=LINE))
    p.append(text(410, 82, "|h(t)|", size=12, bold=True, color=LINE))
    
    # Pulses on timeline
    # Pulse 0 at t0=440
    p.append(arrow(440, 260, 440, 120, color="#2563eb", sw=2.5))
    p.append(circle(440, 120, 4, fill="#2563eb", stroke="#2563eb"))
    p.append(text(440, 276, "τ₀", size=11, bold=True, color="#2563eb"))
    p.append(text(440, 108, "a₀", size=11, bold=True, color="#2563eb"))
    
    # Pulse 1 at t1=540 (delay tau1 > Tc)
    p.append(arrow(540, 260, 540, 155, color="#dc2626", sw=2.5))
    p.append(circle(540, 155, 4, fill="#dc2626", stroke="#dc2626"))
    p.append(text(540, 276, "τ₁", size=11, bold=True, color="#dc2626"))
    p.append(text(540, 143, "a₁", size=11, bold=True, color="#dc2626"))
    
    # Pulse 2 at t2=640 (delay tau2 > Tc)
    p.append(arrow(640, 260, 640, 190, color="#d97706", sw=2.5))
    p.append(circle(640, 190, 4, fill="#d97706", stroke="#d97706"))
    p.append(text(640, 276, "τ₂", size=11, bold=True, color="#d97706"))
    p.append(text(640, 178, "a₂", size=11, bold=True, color="#d97706"))
    
    # Chip duration indication Tc
    p.append(line(440, 290, 540, 290, color=MUTED, sw=1.2))
    p.append(line(440, 285, 440, 295, color=MUTED, sw=1.2))
    p.append(line(540, 285, 540, 295, color=MUTED, sw=1.2))
    p.append(text(490, 306, "Δτ > T_c (роздільні промені)", size=10, italic=True, color=MUTED))
    
    # Write SVG file
    body = "".join(p)
    svg_str = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
               '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
               '<path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>\n%s\n</svg>' % (W, H, W, H, LINE, body))
    with open(os.path.join(OUT, "multipath-channel.svg"), "w", encoding="utf-8") as f:
        f.write(svg_str)


# ── Fig 2: Загальна архітектура RAKE-приймача ────────────────────────────────
def fig_rake_architecture():
    W, H = 760, 420
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    
    p.append(text(W/2, 24, "Структурна схема RAKE-приймача (3 пальці + пошуковець)", size=15, bold=True))
    
    # Input r(t)
    b_in, w_in, h_in = textbox(60, 200, "Вхідний\nсигнал r(t)", size=12, pad=8, fill="#eff6ff", stroke="#2563eb", bold=True)
    p.append(b_in)
    
    # Splitter node
    p.append(circle(125, 200, 4, fill="#2563eb", stroke="#2563eb"))
    p.append(arrow(100, 200, 125, 200, color="#2563eb", sw=2))
    
    # Searcher block (top)
    b_srch, w_srch, h_srch = textbox(260, 75, "Пошуковець затримок\n(Searcher / DLL)", size=11, pad=8, fill="#fef3c7", stroke="#d97706", bold=True)
    p.append(b_srch)
    p.append(line(125, 200, 125, 75, color="#d97706", sw=1.8, dash="3,3"))
    p.append(line(125, 75, 195, 75, color="#d97706", sw=1.8, dash="3,3"))
    
    # Fingers 1, 2, 3
    finger_y = [145, 215, 285]
    colors = ["#2563eb", "#dc2626", "#d97706"]
    bg_colors = ["#eff6ff", "#fef2f2", "#fffbeb"]
    
    for i, (fy, col, bg) in enumerate(zip(finger_y, colors, bg_colors)):
        # Line from input to delay tau_i
        p.append(line(125, 200, 145, fy, color=col, sw=1.8))
        
        # Delay block tau_i
        b_d, w_d, h_d = textbox(175, fy, "Затримка\nτ_%d" % i, size=10, pad=5, fill=bg, stroke=col)
        p.append(b_d)
        
        # Connection from delay to correlator
        p.append(arrow(205, fy, 235, fy, color=col, sw=1.8))
        
        # Correlator block
        b_c, w_c, h_c = textbox(290, fy, "Корелятор %d\n(ПСП × ∫)" % (i+1), size=10, pad=6, fill=bg, stroke=col, bold=True)
        p.append(b_c)
        
        # Control line from searcher to correlator delay
        p.append(line(260, 105, 260, fy-18, color="#d97706", sw=1.2, dash="2,2"))
        
        # Connection from correlator to weight/phase rotator
        p.append(arrow(345, fy, 375, fy, color=col, sw=1.8))
        
        # Weight block (a_i* * e^{-j theta_i})
        b_w, w_w, h_w = textbox(435, fy, "Множник MRC\nw_%d = h_%d*" % (i, i), size=10, pad=6, fill=bg, stroke=col, bold=True)
        p.append(b_w)
        
        # Output arrow to summer
        p.append(arrow(495, fy, 570, 215, color=col, sw=1.8))
    
    # Summer block (Sum Σ)
    p.append(circle(590, 215, 22, fill="#f1f5f9", stroke="#334155", sw=2))
    p.append(text(590, 221, "Σ", size=20, bold=True, color="#334155"))
    p.append(text(590, 183, "MRC Суматор", size=11, bold=True, color="#334155"))
    
    # Output to Decision block
    p.append(arrow(612, 215, 650, 215, color="#334155", sw=2))
    
    # Decision block
    b_dec, w_dec, h_dec = textbox(700, 215, "Решач\n(Decision)", size=11, pad=8, fill="#ecfdf5", stroke="#10b981", bold=True)
    p.append(b_dec)
    
    # Bottom note
    p.append(rect(120, 345, 520, 50, fill="#f8fafc", stroke="#cbd5e1", rx=6))
    p.append(text(380, 365, "Кожен палець RAKE відстежує свій промінь з затримкою τ_k > T_c.", size=11, bold=True, color=LINE))
    p.append(text(380, 383, "MRC вагові коефіцієнти w_k = h_k* повертають фазу й зважують за SNR.", size=10, color=MUTED))
    
    body = "".join(p)
    svg_str = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
               '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
               '<path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>\n%s\n</svg>' % (W, H, W, H, LINE, body))
    with open(os.path.join(OUT, "rake-architecture.svg"), "w", encoding="utf-8") as f:
        f.write(svg_str)


# ── Fig 3: Детальна схема одного пальця RAKE ─────────────────────────────────
def fig_finger_correlator():
    W, H = 740, 320
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    
    p.append(text(W/2, 24, "Внутрішня будова окремого пальця (Finger K)", size=15, bold=True))
    
    # Input r(t)
    b_in, w_in, h_in = textbox(55, 120, "Вхід r(t)", size=11, pad=6, fill="#eff6ff", stroke="#2563eb", bold=True)
    p.append(b_in)
    
    p.append(arrow(95, 120, 140, 120, color="#2563eb", sw=2))
    
    # Multiplier 1: Despreader (r(t) x c*(t - tau_k))
    p.append(circle(160, 120, 18, fill="#fef2f2", stroke="#ef4444", sw=2))
    p.append(text(160, 126, "×", size=20, bold=True, color="#ef4444"))
    p.append(text(160, 92, "Дерозширення", size=10, color="#ef4444", bold=True))
    
    # Code Generator block below multiplier 1
    b_pn, w_pn, h_pn = textbox(160, 230, "Генератор ПСП\nc(t - τ_k)", size=10, pad=6, fill="#fef3c7", stroke="#d97706", bold=True)
    p.append(b_pn)
    p.append(arrow(160, 202, 160, 138, color="#d97706", sw=1.8))
    
    p.append(arrow(178, 120, 220, 120, color="#334155", sw=2))
    
    # Integrator block
    b_int, w_int, h_int = textbox(280, 120, "Інтегратор за T_s\n∫_{0}^{T_s} dt", size=11, pad=8, fill="#f8fafc", stroke="#475569", bold=True)
    p.append(b_int)
    
    p.append(arrow(340, 120, 390, 120, color="#334155", sw=2))
    
    # Node to Channel estimator
    p.append(circle(365, 120, 3.5, fill="#334155", stroke="#334155"))
    p.append(line(365, 120, 365, 230, color="#059669", sw=1.5, dash="3,3"))
    
    # Channel Estimator block
    b_est, w_est, h_est = textbox(365, 255, "Оцінювач каналу\nh_k = a_k · e^{j θ_k}", size=10, pad=6, fill="#ecfdf5", stroke="#10b981", bold=True)
    p.append(b_est)
    
    # Multiplier 2: MRC weighting (x h_k*)
    p.append(circle(410, 120, 18, fill="#eff6ff", stroke="#2563eb", sw=2))
    p.append(text(410, 126, "×", size=20, bold=True, color="#2563eb"))
    p.append(text(410, 92, "Фазування й зважування", size=10, color="#2563eb", bold=True))
    
    # Conjugate weight from estimator
    p.append(line(365, 280, 410, 280, color="#10b981", sw=1.5))
    p.append(arrow(410, 280, 410, 138, color="#10b981", sw=1.5))
    b_wlabel, w_wl, h_wl = textbox(445, 200, "Вага w_k = h_k*", size=9, pad=3, fill="#ecfdf5", stroke="#10b981")
    p.append(b_wlabel)
    
    p.append(arrow(428, 120, 490, 120, color="#2563eb", sw=2))
    
    # Finger Output
    b_out, w_out, h_out = textbox(570, 120, "Вихід пальця K\ny_k = a_k² · s + n_k'", size=11, pad=8, fill="#f0fdf4", stroke="#16a34a", bold=True)
    p.append(b_out)
    
    # Summary card at bottom right
    p.append(rect(480, 205, 230, 95, fill="#fafafa", stroke="#e2e8f0", rx=6))
    p.append(text(595, 225, "Результат роботи пальця:", size=10, bold=True, color=LINE))
    p.append(text(595, 245, "1. Очищення від ПСП супроводжувачів", size=9, color=MUTED))
    p.append(text(595, 263, "2. Компенсація фази e^{-j θ_k}", size=9, color=MUTED))
    p.append(text(595, 281, "3. Зважування пропорційно a_k", size=9, color=MUTED))
    
    body = "".join(p)
    svg_str = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
               '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
               '<path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>\n%s\n</svg>' % (W, H, W, H, LINE, body))
    with open(os.path.join(OUT, "finger-correlator.svg"), "w", encoding="utf-8") as f:
        f.write(svg_str)


# ── Fig 4: MRC Векторне додавання в комплексній площині ─────────────────────
def fig_mrc_combining():
    W, H = 740, 340
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    
    p.append(text(W/2, 24, "Принцип MRC: поворот фаз і когерентне додавання у комплексній площині", size=15, bold=True))
    
    # Left Box: Before Phase Rotation (random phases theta_k)
    p.append(rect(20, 45, 335, 275, fill="#fff5f5", stroke="#fca5a5", rx=8))
    p.append(text(187.5, 68, "До обробки: довільні фази (некогерентні)", size=12, bold=True, color="#dc2626"))
    
    # Axes Left
    p.append(line(70, 190, 300, 190, color="#94a3b8", sw=1.2)) # Re
    p.append(line(185, 90, 185, 290, color="#94a3b8", sw=1.2))  # Im
    p.append(text(295, 182, "Re", size=10, color=MUTED))
    p.append(text(192, 102, "Im", size=10, color=MUTED))
    
    # Vectors before phase alignment
    # Vector 0 (blue)
    p.append(arrow(185, 190, 270, 140, color="#2563eb", sw=2.2))
    p.append(text(275, 135, "y₀ (θ₀ = 30°)", size=10, bold=True, color="#2563eb"))
    
    # Vector 1 (red)
    p.append(arrow(185, 190, 120, 110, color="#dc2626", sw=2.2))
    p.append(text(105, 105, "y₁ (θ₁ = 130°)", size=10, bold=True, color="#dc2626"))
    
    # Vector 2 (amber)
    p.append(arrow(185, 190, 135, 250, color="#d97706", sw=2.2))
    p.append(text(115, 260, "y₂ (θ₂ = 220°)", size=10, bold=True, color="#d97706"))
    
    p.append(text(187.5, 305, "Вектори гасять один одного! (руйнівна інтерференція)", size=10, italic=True, color="#dc2626"))
    
    # Right Box: After MRC Phase Rotation & Weighting
    p.append(rect(385, 45, 335, 275, fill="#f0fdf4", stroke="#86efac", rx=8))
    p.append(text(552.5, 68, "Після MRC: фази вирівняні вздовж Re", size=12, bold=True, color="#16a34a"))
    
    # Axes Right
    p.append(line(410, 190, 700, 190, color="#94a3b8", sw=1.2)) # Re
    p.append(line(440, 90, 440, 290, color="#94a3b8", sw=1.2))  # Im
    p.append(text(695, 182, "Re", size=10, color=MUTED))
    p.append(text(447, 102, "Im", size=10, color=MUTED))
    
    # Vectors aligned along Re axis
    # Vector 0 aligned (blue)
    p.append(arrow(440, 190, 520, 190, color="#2563eb", sw=2.2))
    p.append(text(475, 175, "w₀·y₀", size=10, bold=True, color="#2563eb"))
    
    # Vector 1 aligned (red, starting at 520)
    p.append(arrow(520, 190, 580, 190, color="#dc2626", sw=2.2))
    p.append(text(545, 175, "w₁·y₁", size=10, bold=True, color="#dc2626"))
    
    # Vector 2 aligned (amber, starting at 580)
    p.append(arrow(580, 190, 625, 190, color="#d97706", sw=2.2))
    p.append(text(600, 175, "w₂·y₂", size=10, bold=True, color="#d97706"))
    
    # Total combined vector sum Y
    p.append(arrow(440, 230, 625, 230, color="#16a34a", sw=3.5))
    p.append(text(530, 252, "Сумарний сигнал Y = Σ w_k · y_k", size=11, bold=True, color="#16a34a"))
    
    p.append(text(552.5, 305, "Повна конструктивна інтерференція: SNR максимально можливе!", size=10, italic=True, color="#16a34a"))
    
    body = "".join(p)
    svg_str = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
               '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
               '<path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>\n%s\n</svg>' % (W, H, W, H, LINE, body))
    with open(os.path.join(OUT, "mrc-combining.svg"), "w", encoding="utf-8") as f:
        f.write(svg_str)


if __name__ == "__main__":
    fig_multipath_channel()
    fig_rake_architecture()
    fig_finger_correlator()
    fig_mrc_combining()
    print("All figures generated successfully.")
