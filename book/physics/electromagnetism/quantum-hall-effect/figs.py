# -*- coding: utf-8 -*-
import sys, os

# Four levels up to root scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, textbox, fitbox, text, mtext, rect, line, arrow, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def fig_hall_bar():
    w, h = 760, 440
    frags = []
    
    # Background panel
    frags.append(rect(20, 20, 720, 400, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))
    
    # 2DEG Sample body
    frags.append(rect(140, 150, 480, 140, fill="#eaf2f8", stroke="#2980b9", sw=2.5, rx=4))
    frags.append(text(380, 215, "2DEG (Двовимірний електронний газ)", size=15, color="#1b4f72", bold=True))
    frags.append(text(380, 235, "Гетероструктура GaAs / AlGaAs", size=12, color=MUTED, italic=True))
    
    # Current contacts (1 & 4) left and right
    frags.append(rect(90, 180, 50, 80, fill="#f9e79f", stroke="#d4ac0d", sw=2, rx=4))
    frags.append(mtext(115, 212, ["Контакт 1", "(+I)"], size=11, color="#7d6608", bold=True))
    
    frags.append(rect(620, 180, 50, 80, fill="#f9e79f", stroke="#d4ac0d", sw=2, rx=4))
    frags.append(mtext(645, 212, ["Контакт 4", "(-I)"], size=11, color="#7d6608", bold=True))
    
    # Current arrows - text well above arrow line
    frags.append(arrow(45, 220, 85, 220, color=POS, sw=2.5))
    frags.append(text(65, 175, "Струм I_x", size=12, color=POS, bold=True))
    
    frags.append(arrow(670, 220, 710, 220, color=POS, sw=2.5))
    
    # Voltage contacts on top (2 & 3)
    frags.append(rect(240, 110, 40, 40, fill="#d5f5e3", stroke="#27ae60", sw=2, rx=3))
    frags.append(text(260, 134, "2", size=14, color="#1e8449", bold=True))
    
    frags.append(rect(480, 110, 40, 40, fill="#d5f5e3", stroke="#27ae60", sw=2, rx=3))
    frags.append(text(500, 134, "3", size=14, color="#1e8449", bold=True))
    
    # Voltage contacts on bottom (6 & 5)
    frags.append(rect(240, 290, 40, 40, fill="#d5f5e3", stroke="#27ae60", sw=2, rx=3))
    frags.append(text(260, 314, "6", size=14, color="#1e8449", bold=True))
    
    frags.append(rect(480, 290, 40, 40, fill="#d5f5e3", stroke="#27ae60", sw=2, rx=3))
    frags.append(text(500, 314, "5", size=14, color="#1e8449", bold=True))
    
    # Measurement V_xx between contacts 2 and 3
    frags.append(line(260, 110, 260, 75, color=LINE, sw=1.5))
    frags.append(line(500, 110, 500, 75, color=LINE, sw=1.5))
    frags.append(line(260, 75, 340, 75, color=LINE, sw=1.5))
    frags.append(line(420, 75, 500, 75, color=LINE, sw=1.5))
    frags.append(fitbox(340, 57, 80, 36, "V_xx\n(поздовжня)", size=12, fill="#e8f8f5", stroke="#16a085"))
    
    # Measurement V_xy between contacts 3 and 5
    frags.append(line(500, 330, 500, 375, color=LINE, sw=1.5))
    frags.append(line(520, 130, 575, 130, color=LINE, sw=1.5))
    frags.append(line(575, 130, 575, 230, color=LINE, sw=1.5))
    frags.append(line(500, 375, 575, 375, color=LINE, sw=1.5))
    frags.append(line(575, 375, 575, 270, color=LINE, sw=1.5))
    frags.append(fitbox(535, 230, 80, 36, "V_xy\n(Холла)", size=12, fill="#fef9e7", stroke="#d4ac0d"))
    
    # Magnetic field B indicator (perpendicular into page)
    frags.append(circle(380, 100, 18, fill="#fadbd8", stroke=POS, sw=2))
    frags.append(text(380, 106, "⊗ B", size=14, color=POS, bold=True))
    frags.append(text(380, 68, "Магнітне поле B ⊥ 2DEG", size=12, color=POS, italic=True))
    
    render(os.path.join(IMG_DIR, "qhe-hall-bar.svg"), w, h, *frags, title="Геометрія вимірювального містка Холла у 2DEG")

def fig_plateaus():
    w, h = 760, 460
    frags = []
    
    # Background panel
    frags.append(rect(20, 20, 720, 420, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))
    
    # Axes
    ox, oy = 90, 380
    ax_w, ax_h = 620, 310
    frags.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    frags.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    
    frags.append(text(ox + ax_w - 20, oy + 28, "Магнітне поле B (Тесла)", size=13, color=INK, bold=True))
    frags.append(text(ox - 50, oy - ax_h + 15, "Опір R", size=13, color=INK, bold=True))
    
    # Grid lines and plateau values on Y axis
    y_p1 = oy - 250  # i=1
    y_p2 = oy - 170  # i=2
    y_p3 = oy - 120  # i=3
    y_p4 = oy - 80   # i=4
    
    frags.append(line(ox, y_p1, ox + ax_w - 40, y_p1, color="#ebedef", sw=1, dash="4,4"))
    frags.append(line(ox, y_p2, ox + ax_w - 40, y_p2, color="#ebedef", sw=1, dash="4,4"))
    frags.append(line(ox, y_p3, ox + ax_w - 40, y_p3, color="#ebedef", sw=1, dash="4,4"))
    
    frags.append(text(ox - 35, y_p1 + 4, "h/e² (i=1)", size=11, color=NEG, bold=True))
    frags.append(text(ox - 35, y_p2 + 4, "h/2e² (i=2)", size=11, color=NEG, bold=True))
    frags.append(text(ox - 35, y_p3 + 4, "h/3e² (i=3)", size=11, color=NEG, bold=True))
    
    # R_xy curve (Hall resistance - blue steps)
    pts_rxy = [
        (ox, oy),
        (ox + 50, oy - 60),
        (ox + 90, y_p4),
        (ox + 140, y_p4),  # Plateau i=4
        (ox + 180, y_p3),
        (ox + 250, y_p3),  # Plateau i=3
        (ox + 300, y_p2),
        (ox + 420, y_p2),  # Plateau i=2
        (ox + 480, y_p1),
        (ox + 630, y_p1)   # Plateau i=1
    ]
    
    path_rxy = "M " + " L ".join("%d %d" % (x, y) for x, y in pts_rxy)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_rxy, NEG))
    
    # R_xx curve (Longitudinal resistance - red peaks)
    pts_rxx = [
        (ox, oy),
        (ox + 50, oy - 40),
        (ox + 90, oy),
        (ox + 140, oy),     # Zero at i=4
        (ox + 160, oy - 70),# Peak
        (ox + 180, oy),
        (ox + 250, oy),     # Zero at i=3
        (ox + 275, oy - 110),# Peak
        (ox + 300, oy),
        (ox + 420, oy),     # Zero at i=2
        (ox + 450, oy - 160),# Peak
        (ox + 480, oy),
        (ox + 630, oy)      # Zero at i=1
    ]
    
    path_rxx = "M " + " L ".join("%d %d" % (x, y) for x, y in pts_rxx)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_rxx, POS))
    
    # Legend
    frags.append(rect(450, 45, 250, 65, fill="#f8f9f9", stroke="#bdc3c7", sw=1.5, rx=4))
    frags.append(line(465, 65, 505, 65, color=NEG, sw=3))
    frags.append(text(575, 70, "R_xy (Поперечний опір)", size=12, color=NEG, bold=True))
    
    frags.append(line(465, 90, 505, 90, color=POS, sw=2.5))
    frags.append(text(575, 95, "R_xx (Поздовжній опір = 0)", size=12, color=POS, bold=True))
    
    # Annotations on plateaus
    frags.append(fitbox(360, y_p2 - 22, 100, 26, "Плато i = 2", size=11, fill="#eaf2f8", stroke="#2980b9"))
    frags.append(fitbox(550, y_p1 - 22, 100, 26, "Плато i = 1", size=11, fill="#eaf2f8", stroke="#2980b9"))
    frags.append(fitbox(550, oy - 25, 110, 26, "R_xx = 0 (Без дисипації)", size=10, fill="#fadbd8", stroke="#c0392b"))

    render(os.path.join(IMG_DIR, "qhe-plateaus.svg"), w, h, *frags, title="Плато квантового опору Холла R_xy та зникаючий поздовжній опір R_xx")

def fig_landau_levels():
    w, h = 760, 440
    frags = []
    
    frags.append(rect(20, 20, 720, 400, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))
    
    # Energy axis
    ox, oy = 80, 380
    frags.append(arrow(ox, oy, ox, oy - 320, color=INK, sw=2))
    frags.append(text(ox - 35, oy - 310, "Енергія E", size=13, color=INK, bold=True))
    
    # Density of states D(E) axis horizontally
    frags.append(arrow(ox, oy, ox + 620, oy, color=INK, sw=2))
    frags.append(text(ox + 550, oy + 28, "Густина станів D(E)", size=13, color=INK, bold=True))
    
    # Landau levels E_0, E_1, E_2
    y_l0 = oy - 70
    y_l1 = oy - 170
    y_l2 = oy - 270
    
    # Draw broadened DOS peaks (Gaussians)
    frags.append(line(ox, y_l0, ox + 580, y_l0, color="#d5dbdb", sw=1, dash="3,3"))
    frags.append(text(ox - 30, y_l0 + 4, "E_0", size=12, color=INK, bold=True))
    
    frags.append(line(ox, y_l1, ox + 580, y_l1, color="#d5dbdb", sw=1, dash="3,3"))
    frags.append(text(ox - 30, y_l1 + 4, "E_1", size=12, color=INK, bold=True))
    
    frags.append(line(ox, y_l2, ox + 580, y_l2, color="#d5dbdb", sw=1, dash="3,3"))
    frags.append(text(ox - 30, y_l2 + 4, "E_2", size=12, color=INK, bold=True))
    
    # Cyclotron gap energy label
    frags.append(arrow(ox + 420, y_l0, ox + 420, y_l1, color=FIELD, sw=1.8))
    frags.append(arrow(ox + 420, y_l1, ox + 420, y_l0, color=FIELD, sw=1.8))
    frags.append(text(ox + 475, (y_l0 + y_l1) / 2 + 4, "ΔE = ℏω_c", size=13, color=FIELD, bold=True))
    
    # Broadened peaks rendering using smooth paths
    p0 = "M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d" % (
        ox, y_l0 + 35, ox + 150, y_l0 + 30, ox + 300, y_l0 - 30, ox + 350, y_l0 - 35,
        ox + 300, y_l0 - 40, ox + 150, y_l0 - 30, ox, y_l0 - 35
    )
    frags.append('<path d="%s" fill="#ebf5fb" stroke="#2980b9" stroke-width="2"/>' % p0)
    
    p1 = "M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d" % (
        ox, y_l1 + 35, ox + 150, y_l1 + 30, ox + 300, y_l1 - 30, ox + 350, y_l1 - 35,
        ox + 300, y_l1 - 40, ox + 150, y_l1 - 30, ox, y_l1 - 35
    )
    frags.append('<path d="%s" fill="#ebf5fb" stroke="#2980b9" stroke-width="2"/>' % p1)
    
    # Fermi level E_F in gap between E_0 and E_1
    y_ef = oy - 120
    frags.append(line(ox, y_ef, ox + 580, y_ef, color=POS, sw=2, dash="6,4"))
    frags.append(text(ox + 280, y_ef - 8, "Рівень Фермі E_F (у щілині рухливості)", size=12, color=POS, bold=True))
    
    # Highlight delocalized vs localized states
    frags.append(fitbox(ox + 340, y_l0, 140, 26, "Делокалізовані стани", size=11, fill="#d4efdf", stroke="#27ae60"))
    frags.append(fitbox(ox + 160, y_ef + 15, 140, 26, "Локалізовані стани", size=11, fill="#fcf3cf", stroke="#f39c12"))

    render(os.path.join(IMG_DIR, "qhe-landau-levels.svg"), w, h, *frags, title="Розширені рівні Ландау та рівень Фермі у щілині рухливості")

def fig_edge_channels():
    w, h = 760, 440
    frags = []
    
    frags.append(rect(20, 20, 720, 400, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))
    
    # Sample body (2DEG bulk)
    frags.append(rect(100, 100, 560, 240, fill="#f2f4f4", stroke="#7f8c8d", sw=2, rx=6))
    frags.append(text(380, 205, "Диелектричний bulk (ізольований об'єм)", size=14, color=MUTED, bold=True))
    frags.append(text(380, 230, "Рівень Фермі між рівнями Ландау", size=12, color=MUTED, italic=True))
    
    # Top edge channel
    frags.append(rect(100, 100, 560, 30, fill="#d4efdf", stroke="#27ae60", sw=1.5, rx=3))
    frags.append(arrow(140, 115, 340, 115, color=FIELD, sw=2.5))
    frags.append(arrow(340, 115, 620, 115, color=FIELD, sw=2.5))
    frags.append(text(380, 85, "Верхній крайковий канал (рух праворуч →)", size=13, color="#1e8449", bold=True))
    
    # Bottom edge channel
    frags.append(rect(100, 310, 560, 30, fill="#d4efdf", stroke="#27ae60", sw=1.5, rx=3))
    frags.append(arrow(620, 325, 420, 325, color=FIELD, sw=2.5))
    frags.append(arrow(420, 325, 140, 325, color=FIELD, sw=2.5))
    frags.append(text(380, 360, "Нижній крайковий канал (рух ліворуч ←)", size=13, color="#1e8449", bold=True))
    
    # B-field indicator
    frags.append(circle(380, 160, 16, fill="#fadbd8", stroke=POS, sw=1.5))
    frags.append(text(380, 165, "⊗ B", size=13, color=POS, bold=True))
    
    # Skipping orbits illustration on top edge
    for cx in (180, 260, 500, 580):
        p = "M %d 130 A 20 20 0 0 1 %d 130" % (cx - 30, cx + 10)
        frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="3,2"/>' % (p, POS))
    
    # Text annotation inside bulk
    frags.append(text(380, 275, "Відсутність зворотного розсіювання: канали просторово рознесені", size=12, color="#16a085", bold=True))

    render(os.path.join(IMG_DIR, "qhe-edge-channels.svg"), w, h, *frags, title="Хіральні крайкові канали та відсутність дисипації у 2DEG")

if __name__ == "__main__":
    fig_hall_bar()
    fig_plateaus()
    fig_landau_levels()
    fig_edge_channels()
    print("All figures generated successfully.")
