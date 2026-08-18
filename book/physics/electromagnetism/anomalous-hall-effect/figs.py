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

def fig_ahe_vs_ohe():
    w, h = 760, 440
    frags = []
    
    # Background panel
    frags.append(rect(20, 20, 720, 400, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))
    
    # Axes
    ox, oy = 90, 370
    ax_w, ax_h = 620, 310
    frags.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    frags.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    
    frags.append(text(ox + ax_w - 30, oy + 28, "Зовнішнє магнітне поле B", size=13, color=INK, bold=True))
    frags.append(text(ox - 50, oy - ax_h + 15, "Опір Холла ρ_xy", size=13, color=INK, bold=True))
    
    # Ordinary Hall Effect (OHE - linear dashed line)
    pts_ohe = [(ox, oy), (ox + ax_w - 40, oy - 90)]
    path_ohe = f"M {pts_ohe[0][0]} {pts_ohe[0][1]} L {pts_ohe[1][0]} {pts_ohe[1][1]}"
    frags.append(f'<path d="{path_ohe}" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="6,4"/>')
    frags.append(text(ox + 460, oy - 55, "Ззвичайний ефект Холла: ρ_xy = R_0 · B", size=12, color=MUTED, bold=True))
    
    # Anomalous Hall Effect (AHE - steep curve saturating to a parallel line)
    path_ahe = f"M {ox} {oy} C {ox + 60} {oy - 180}, {ox + 120} {oy - 230}, {ox + 200} {oy - 240} L {ox + ax_w - 40} {oy - 275}"
    frags.append(f'<path d="{path_ahe}" fill="none" stroke="{NEG}" stroke-width="3.5"/>')
    
    # Extrapolation line back to B=0 to show spontaneous anomalous Hall resistivity rho_AH
    path_extrap = f"M {ox} {oy - 210} L {ox + 200} {oy - 240}"
    frags.append(f'<path d="{path_extrap}" fill="none" stroke="{POS}" stroke-width="1.8" stroke-dasharray="4,3"/>')
    frags.append(circle(ox, oy - 210, 5, fill=POS, stroke=POS, sw=1))
    
    # Annotations
    frags.append(arrow(ox - 30, oy, ox - 30, oy - 210, color=POS, sw=1.8))
    frags.append(arrow(ox - 30, oy - 210, ox - 30, oy, color=POS, sw=1.8))
    frags.append(fitbox(ox + 10, oy - 110, 150, 36, "Аномальний опір ρ_AH\n(при B = 0)", size=11, fill="#fadbd8", stroke="#c0392b"))
    
    # Saturation point indicator
    sat_x = ox + 200
    frags.append(line(sat_x, oy, sat_x, oy - 240, color="#bdc3c7", sw=1, dash="3,3"))
    frags.append(text(sat_x, oy + 18, "Поле насичення B_sat", size=11, color=INK, italic=True))
    
    # Legend panel
    frags.append(rect(380, 45, 330, 80, fill="#f8f9f9", stroke="#bdc3c7", sw=1.5, rx=4))
    frags.append(line(395, 65, 435, 65, color=NEG, sw=3.5))
    frags.append(text(445, 70, "Повний опір: ρ_xy = R_0 · B + R_s · M_z", size=12, color=NEG, bold=True))
    
    frags.append(line(395, 95, 435, 95, color=MUTED, sw=2, dash="6,4"))
    frags.append(text(445, 100, "Ззвичайний опір (лише від сили Лоренца)", size=11, color=MUTED, italic=True))
    
    render(os.path.join(IMG_DIR, "ahe-vs-ohe.svg"), w, h, *frags, title="Залежність опору Холла від магнітного поля у феромагнетиках")

def fig_ahe_mechanisms():
    w, h = 760, 480
    frags = []
    
    frags.append(rect(20, 20, 720, 440, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))
    
    # Three columns for 3 mechanisms
    col_w = 220
    gap = 20
    x0 = 40
    
    # 1. Intrinsic (Berry Curvature)
    x1 = x0
    frags.append(rect(x1, 40, col_w, 400, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=6))
    frags.append(fitbox(x1 + 10, 50, col_w - 20, 40, "1. Внутрішній механізм\n(Карплус-Латтінджер)", size=13, fill="#d4efdf", stroke="#27ae60"))
    
    frags.append(arrow(x1 + 40, 360, x1 + 40, 160, color=INK, sw=2))
    frags.append(text(x1 + 45, 150, "Електричне поле E", size=11, color=INK, bold=True))
    
    path_int = f"M {x1 + 60} 340 Q {x1 + 100} 250, {x1 + 180} 180"
    frags.append(f'<path d="{path_int}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')
    frags.append(arrow(x1 + 140, 215, x1 + 175, 185, color=NEG, sw=2.5))
    
    frags.append(circle(x1 + 110, 260, 8, fill=FIELD, stroke=FIELD, sw=1))
    frags.append(text(x1 + 110, 260, "e⁻", size=10, color="#ffffff", bold=True))
    
    frags.append(arrow(x1 + 110, 260, x1 + 160, 260, color=POS, sw=2))
    frags.append(text(x1 + 110, 290, "Аномальна швидкість", size=11, color=POS, bold=True))
    frags.append(text(x1 + 110, 308, "v_anom ∝ E × Ω(k)", size=11, color=POS, italic=True))
    frags.append(mtext(x1 + 110, 370, ["Без розсіювання!", "Властивість зонової", "структури кристала"], size=11, color=MUTED))
    
    # 2. Skew Scattering
    x2 = x1 + col_w + gap
    frags.append(rect(x2, 40, col_w, 400, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=6))
    frags.append(fitbox(x2 + 10, 50, col_w - 20, 40, "2. Зсувне розсіювання\n(Skew scattering, Smit)", size=13, fill="#fcf3cf", stroke="#f39c12"))
    
    frags.append(circle(x2 + 110, 240, 16, fill="#fadbd8", stroke="#c0392b", sw=2))
    frags.append(text(x2 + 110, 244, "Домішка", size=10, color="#c0392b", bold=True))
    
    frags.append(arrow(x2 + 110, 350, x2 + 110, 260, color=INK, sw=2))
    frags.append(arrow(x2 + 110, 240, x2 + 190, 170, color=NEG, sw=2.5))
    frags.append(text(x2 + 165, 160, "Асиметричний", size=11, color=NEG, bold=True))
    frags.append(text(x2 + 165, 176, "кут відхилення", size=11, color=NEG, bold=True))
    
    frags.append(arrow(x2 + 110, 310, x2 + 110, 290, color=POS, sw=2))
    frags.append(text(x2 + 85, 305, "Спін S", size=10, color=POS, bold=True))
    
    frags.append(mtext(x2 + 110, 370, ["Квантова асиметрія", "ймовірності розсіювання", "W(k → k') ≠ W(k' → k)"], size=11, color=MUTED))
    
    # 3. Side Jump
    x3 = x2 + col_w + gap
    frags.append(rect(x3, 40, col_w, 400, fill="#f4ecf7", stroke="#8e44ad", sw=1.5, rx=6))
    frags.append(fitbox(x3 + 10, 50, col_w - 20, 40, "3. Бічний стрибок\n(Side-jump, Berger)", size=13, fill="#e8daef", stroke="#8e44ad"))
    
    frags.append(circle(x3 + 90, 240, 14, fill="#ebedef", stroke="#7f8c8d", sw=2))
    frags.append(text(x3 + 90, 244, "Домішка", size=10, color="#7f8c8d", bold=True))
    
    frags.append(line(x3 + 90, 350, x3 + 90, 240, color=INK, sw=2))
    frags.append(arrow(x3 + 90, 240, x3 + 150, 240, color=POS, sw=2.5))
    frags.append(arrow(x3 + 150, 240, x3 + 150, 150, color=NEG, sw=2.5))
    
    frags.append(fitbox(x3 + 105, 270, 100, 30, "Бічний зсув\nΔr ~ 10⁻¹⁰ м", size=11, fill="#fadbd8", stroke="#c0392b"))
    frags.append(mtext(x3 + 110, 370, ["Миттєвий просторовий", "стрибок хвильового пакета", "під час зіткнення"], size=11, color=MUTED))

    render(os.path.join(IMG_DIR, "ahe-mechanisms.svg"), w, h, *frags, title="Три мікроскопічні механізми аномального ефекту Холла")

def fig_ahe_scaling():
    w, h = 760, 440
    frags = []
    
    frags.append(rect(20, 20, 720, 400, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))
    
    ox, oy = 90, 370
    ax_w, ax_h = 620, 310
    frags.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    frags.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    
    frags.append(text(ox + ax_w - 40, oy + 28, "Поздовжня провідність σ_xx (Ом⁻¹см⁻¹)", size=12, color=INK, bold=True))
    frags.append(text(ox - 50, oy - ax_h + 15, "Аномальна провідність σ_xy^AH", size=12, color=INK, bold=True))
    
    x_b1 = ox + 220
    x_b2 = ox + 440
    
    frags.append(line(x_b1, oy, x_b1, oy - ax_h + 30, color="#d5dbdb", sw=1.5, dash="4,4"))
    frags.append(line(x_b2, oy, x_b2, oy - ax_h + 30, color="#d5dbdb", sw=1.5, dash="4,4"))
    
    frags.append(text(x_b1, oy + 16, "10⁴", size=11, color=INK, bold=True))
    frags.append(text(x_b2, oy + 16, "10⁶", size=11, color=INK, bold=True))
    
    pts_r1 = [(ox + 40, oy - 40), (x_b1, oy - 150)]
    path_r1 = f"M {pts_r1[0][0]} {pts_r1[0][1]} L {pts_r1[1][0]} {pts_r1[1][1]}"
    frags.append(f'<path d="{path_r1}" fill="none" stroke="{MUTED}" stroke-width="3"/>')
    frags.append(fitbox(ox + 40, oy - 120, 140, 44, "Грязний режим\nσ_xy ∝ σ_xx^1.6\n(локалізація)", size=11, fill="#eaeded", stroke="#95a5a6"))
    
    pts_r2 = [(x_b1, oy - 150), (x_b2, oy - 150)]
    path_r2 = f"M {pts_r2[0][0]} {pts_r2[0][1]} L {pts_r2[1][0]} {pts_r2[1][1]}"
    frags.append(f'<path d="{path_r2}" fill="none" stroke="{NEG}" stroke-width="3.5"/>')
    frags.append(fitbox(x_b1 + 30, oy - 230, 160, 46, "Помірний режим\nσ_xy ≈ const\n(Внутрішній + Side-jump)", size=11, fill="#ebf5fb", stroke="#2980b9"))
    
    pts_r3 = [(x_b2, oy - 150), (ox + ax_w - 40, oy - 280)]
    path_r3 = f"M {pts_r3[0][0]} {pts_r3[0][1]} L {pts_r3[1][0]} {pts_r3[1][1]}"
    frags.append(f'<path d="{path_r3}" fill="none" stroke="{POS}" stroke-width="3"/>')
    frags.append(fitbox(x_b2 + 20, oy - 230, 140, 44, "Чистий режим\nσ_xy ∝ σ_xx\n(Skew scattering)", size=11, fill="#d4efdf", stroke="#27ae60"))
    
    frags.append(fitbox(240, 35, 380, 30, "Універсальна діаграма масштабування Наґаоси", size=13, fill="#fcf3cf", stroke="#f39c12"))

    render(os.path.join(IMG_DIR, "ahe-scaling.svg"), w, h, *frags, title="Універсальна залежність аномальної провідності від чистоти кристала")

if __name__ == "__main__":
    fig_ahe_vs_ohe()
    fig_ahe_mechanisms()
    fig_ahe_scaling()
    print("All AHE figures generated successfully.")
