# -*- coding: utf-8 -*-
import os
import sys

# Path to scripts directory (4 levels up from topic dir)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def make_fig1(path):
    """Fig 1: Barotropic vs Baroclinic state comparison."""
    dw, dh = 760, 380
    out = []

    # Background
    out.append(rect(0, 0, dw, dh, fill="#ffffff", stroke="#ffffff", sw=0, rx=0))

    # Panel 1: Barotropic (Left)
    out.append(rect(20, 20, 350, 340, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    out.append(text(195, 45, "Баротропний стан (∇ρ || ∇p)", size=15, bold=True, color="#0f172a"))

    # Isobars and Isopycnals (parallel horizontal lines)
    y_levels = [110, 170, 230, 290]
    p_labels = ["p₁ = 1010 hPa", "p₂ = 1000 hPa", "p₃ = 990 hPa", "p₄ = 980 hPa"]
    rho_labels = ["ρ₁ = 1.25", "ρ₂ = 1.20", "ρ₃ = 1.15", "ρ₄ = 1.10"]

    for i, y in enumerate(y_levels):
        out.append(line(50, y, 340, y, color="#64748b", sw=2, dash="4,4"))
        out.append(text(45, y - 6, p_labels[i], size=11, color="#334155", anchor="start"))
        out.append(text(345, y - 6, rho_labels[i], size=11, color="#2563eb", anchor="end"))

    # Vectors for barotropic: grad p (upwards), grad rho (upwards)
    out.append(arrow(195, 230, 195, 120, color="#d97706", sw=2.5))
    out.append(text(210, 150, "∇p", size=13, bold=True, color="#d97706", anchor="start"))

    out.append(arrow(170, 230, 170, 140, color="#2563eb", sw=2.5))
    out.append(text(155, 170, "∇ρ", size=13, bold=True, color="#2563eb", anchor="end"))

    # Result box
    tb1, _, _ = textbox(195, 330, "∇ρ × ∇p = 0  ⇒  τ_baro = 0\nНемає генерації завихреності", size=12, pad=6, fill="#f1f5f9", stroke="#94a3b8", color="#334155")
    out.append(tb1)

    # Panel 2: Baroclinic (Right)
    out.append(rect(390, 20, 350, 340, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    out.append(text(565, 45, "Бароклінний стан (∇ρ × ∇p ≠ 0)", size=15, bold=True, color="#0f172a"))

    # Isobars (horizontal)
    for i, y in enumerate(y_levels):
        out.append(line(420, y, 710, y, color="#64748b", sw=2, dash="4,4"))
        out.append(text(415, y - 6, p_labels[i], size=11, color="#334155", anchor="start"))

    # Isopycnals (tilted)
    # Slanted lines from top-left to bottom-right
    out.append(line(430, 80, 680, 320, color="#2563eb", sw=2))
    out.append(text(685, 315, "ρ₁ = 1.25", size=11, color="#2563eb", anchor="start"))
    out.append(line(480, 80, 710, 300, color="#2563eb", sw=2))
    out.append(text(715, 295, "ρ₂ = 1.20", size=11, color="#2563eb", anchor="start"))
    out.append(line(530, 80, 710, 250, color="#2563eb", sw=2))
    out.append(text(715, 245, "ρ₃ = 1.15", size=11, color="#2563eb", anchor="start"))

    # Vectors for baroclinic: grad p (upwards), grad rho (perpendicular to tilted isopycnals, i.e., up-left)
    out.append(arrow(565, 230, 565, 120, color="#d97706", sw=2.5))
    out.append(text(578, 140, "∇p", size=13, bold=True, color="#d97706", anchor="start"))

    out.append(arrow(565, 230, 480, 160, color="#2563eb", sw=2.5))
    out.append(text(475, 185, "∇ρ", size=13, bold=True, color="#2563eb", anchor="end"))

    # Torque arc / rotation symbol
    out.append(path_arc(565, 200, 30, -30, 120, color="#dc2626", sw=2.5))
    out.append(text(525, 145, "τ_baro", size=13, bold=True, color="#dc2626", anchor="end"))

    # Result box
    tb2, _, _ = textbox(565, 330, "∇ρ × ∇p ≠ 0  ⇒  ∂ω/∂t > 0\nСоленоїди створюють циркуляцію", size=12, pad=6, fill="#fef2f2", stroke="#fca5a5", color="#991b1b")
    out.append(tb2)

    return render(path, dw, dh, *out)

def path_arc(cx, cy, r, start_deg, end_deg, color="#dc2626", sw=2):
    import math
    rad1 = math.radians(start_deg)
    rad2 = math.radians(end_deg)
    x1 = cx + r * math.cos(rad1)
    y1 = cy + r * math.sin(rad1)
    x2 = cx + r * math.cos(rad2)
    y2 = cy + r * math.sin(rad2)
    large_arc = 1 if (end_deg - start_deg) % 360 > 180 else 0
    d = f"M {x1:.1f} {y1:.1f} A {r:.1f} {r:.1f} 0 {large_arc} 1 {x2:.1f} {y2:.1f}"
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw:.1f}" marker-end="url(#arrow)"/>'

def make_fig2(path):
    """Fig 2: Sea breeze baroclinic solenoidal cell."""
    dw, dh = 740, 400
    out = []

    out.append(rect(0, 0, dw, dh, fill="#ffffff", stroke="#ffffff", sw=0, rx=0))

    # Title
    out.append(text(370, 30, "Бароклінна циркуляція морського бризу", size=16, bold=True, color="#0f172a"))

    # Background split: Land (left, warm) vs Sea (right, cool)
    out.append(rect(40, 240, 320, 100, fill="#fef3c7", stroke="#fde047", sw=1.5, rx=0))
    out.append(text(200, 310, "СУХОДІЛ (теплий)\nВисока T, мала густина ρ", size=12, color="#78350f", bold=True))

    out.append(rect(360, 240, 340, 100, fill="#e0f2fe", stroke="#bae6fd", sw=1.5, rx=0))
    out.append(text(530, 310, "МОРЕ (холодне)\nНизька T, висока густина ρ", size=12, color="#075985", bold=True))

    # Shoreline divider
    out.append(line(360, 240, 360, 340, color="#0284c7", sw=2, dash="5,5"))

    # Isobars (slightly sloped or horizontal)
    out.append(line(60, 90, 680, 90, color="#64748b", sw=1.5, dash="4,4"))
    out.append(text(75, 83, "p = 950 hPa (верхній рівень)", size=11, color="#475569", anchor="start"))

    out.append(line(60, 230, 680, 230, color="#64748b", sw=1.5, dash="4,4"))
    out.append(text(75, 223, "p = 1013 hPa (поверхня)", size=11, color="#475569", anchor="start"))

    # Tilted density surfaces (isopycnals) crossing isobars
    out.append(line(120, 70, 580, 250, color="#2563eb", sw=2))
    out.append(text(585, 255, "ρ = const (ізопікна)", size=11, color="#2563eb", anchor="start"))

    # Vector grad p (pointing straight down towards higher pressure)
    out.append(arrow(360, 120, 360, 200, color="#d97706", sw=2.5))
    out.append(text(375, 160, "∇p (вертикальний)", size=12, bold=True, color="#d97706", anchor="start"))

    # Vector grad rho (pointing horizontally towards cold sea)
    out.append(arrow(260, 160, 440, 160, color="#2563eb", sw=2.5))
    out.append(text(445, 150, "∇ρ (горизонтальний)", size=12, bold=True, color="#2563eb", anchor="start"))

    # Solenoid circulation arrows (Counter-clockwise flow: Surface wind sea->land, ascent over land, aloft wind land->sea, descent over sea)
    # Surface wind (sea to land)
    out.append(arrow(520, 215, 220, 215, color="#dc2626", sw=3))
    out.append(text(370, 205, "Поверхневий бриз (з моря на суходіл)", size=12, bold=True, color="#dc2626"))

    # Ascent over warm land
    out.append(arrow(180, 200, 180, 110, color="#dc2626", sw=2.5))
    out.append(text(125, 155, "Конвективний\nпідйом", size=11, bold=True, color="#dc2626"))

    # Aloft return flow (land to sea)
    out.append(arrow(220, 105, 520, 105, color="#dc2626", sw=2.5))
    out.append(text(370, 122, "Верхній зворотний потік", size=11, bold=True, color="#dc2626"))

    # Descent over cool sea
    out.append(arrow(560, 110, 560, 200, color="#dc2626", sw=2.5))
    out.append(text(620, 155, "Опускання\nповітря", size=11, bold=True, color="#dc2626"))

    # Explanation box at bottom
    tb, _, _ = textbox(370, 365, "Соленоїдальний момент τ = (∇ρ × ∇p) / ρ² прискорює замкнену циркуляцію Г(t)", size=12, pad=6, fill="#f8fafc", stroke="#94a3b8", color="#0f172a")
    out.append(tb)

    return render(path, dw, dh, *out)

def make_fig3(path):
    """Fig 3: Thermal wind relation (vertical shear of geostrophic wind)."""
    dw, dh = 740, 380
    out = []

    out.append(rect(0, 0, dw, dh, fill="#ffffff", stroke="#ffffff", sw=0, rx=0))

    out.append(text(370, 30, "Термічний зсув геострофічного вітру (Thermal Wind Shear)", size=16, bold=True, color="#0f172a"))

    # Left side: Atmosphere cross section (Equator to Pole)
    out.append(rect(40, 60, 360, 280, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    out.append(text(220, 85, "Переріз атмосфери (Екватор → Полюс)", size=13, bold=True, color="#1e293b"))

    # Latitude axis
    out.append(arrow(70, 310, 370, 310, color="#475569", sw=1.5))
    out.append(text(75, 328, "Теплі тропіки (висока T)", size=11, color="#b45309", anchor="start"))
    out.append(text(365, 328, "Холодний полюс (низька T)", size=11, color="#0369a1", anchor="end"))

    # Height axis z
    out.append(arrow(70, 310, 70, 90, color="#475569", sw=1.5))
    text_z = text(60, 100, "z (висота)", size=11, color="#475569", anchor="end")
    out.append(text_z)

    # Slanted pressure surfaces (higher height at tropics, lower at pole)
    out.append(line(80, 270, 360, 280, color="#94a3b8", sw=1.5, dash="3,3")) # p3 near surface
    out.append(text(365, 275, "p₃ (1000 hPa)", size=10, color="#64748b", anchor="start"))

    out.append(line(80, 190, 360, 220, color="#94a3b8", sw=1.5, dash="3,3")) # p2 mid troposphere
    out.append(text(365, 215, "p₂ (500 hPa)", size=10, color="#64748b", anchor="start"))

    out.append(line(80, 110, 360, 160, color="#94a3b8", sw=1.5, dash="3,3")) # p1 tropopause
    out.append(text(365, 155, "p₁ (250 hPa)", size=10, color="#64748b", anchor="start"))

    # Temperature gradient arrow
    out.append(arrow(320, 290, 120, 290, color="#dc2626", sw=2))
    out.append(text(220, 282, "∇T (до тропіків)", size=11, bold=True, color="#dc2626"))

    # Right side: Geostrophic wind profiles at low vs high altitude
    out.append(rect(420, 60, 280, 280, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    out.append(text(560, 85, "Профіль західного вітру vg(z)", size=13, bold=True, color="#1e293b"))

    # Altitude z axis on right
    out.append(arrow(450, 300, 450, 100, color="#475569", sw=1.5))
    out.append(text(440, 110, "z", size=12, bold=True, color="#475569", anchor="end"))

    # Wind velocity vectors growing with height
    levels_z = [270, 210, 150]
    speeds = [40, 100, 180]
    labels_v = ["vg (поверхня) ~ 5 м/с", "vg (середня тропосфера) ~ 20 м/с", "vg (струминна течія) ~ 50 м/с"]

    for i, y in enumerate(levels_z):
        out.append(arrow(450, y, 450 + speeds[i], y, color="#2563eb", sw=2.5))
        out.append(text(460 + speeds[i], y + 4, labels_v[i], size=10, color="#1e40af", anchor="start"))

    # Formula box at bottom center
    tb, _, _ = textbox(370, 355, "∂vg / ∂z = (g / f·T) · (k × ∇T)   ⇒   Термічний вітер генерує струминні течії", size=12, pad=6, fill="#eff6ff", stroke="#bfdbfe", color="#1e3a8a")
    out.append(tb)

    return render(path, dw, dh, *out)

def make_fig4(path):
    """Fig 4: Baroclinic wave and cyclogenesis."""
    dw, dh = 760, 400
    out = []

    out.append(rect(0, 0, dw, dh, fill="#ffffff", stroke="#ffffff", sw=0, rx=0))

    out.append(text(380, 30, "Бароклінна хвиля та початкова фаза циклоногенезу", size=16, bold=True, color="#0f172a"))

    # Map area box
    out.append(rect(30, 50, 700, 290, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Warm air mass (south/bottom) and cold air mass (north/top)
    out.append(text(120, 80, "ХОЛОДНЕ ПОЛЯРНЕ ПОВІТРЯ (Північ)", size=12, bold=True, color="#0369a1"))
    out.append(text(120, 310, "ТЕПЛЕ ТРОПІЧНЕ ПОВІТРЯ (Південь)", size=12, bold=True, color="#b45309"))

    # Wavy frontal line (Baroclinic wave perturbation)
    # Sinusoidal path across map
    path_wave = "M 50 180 Q 200 100 350 180 T 650 180"
    out.append(f'<path d="{path_wave}" fill="none" stroke="#dc2626" stroke-width="3"/>')

    # Frontal labels (Cold front & Warm front)
    out.append(text(220, 130, "Холодний фронт (зсув на південь)", size=11, bold=True, color="#1d4ed8"))
    out.append(text(480, 230, "Теплий фронт (зсув на північ)", size=11, bold=True, color="#b91c1c"))

    # Low pressure center at wave trough / crest
    out.append(circle(350, 180, 24, fill="#fef2f2", stroke="#dc2626", sw=2))
    out.append(text(350, 184, "L", size=18, bold=True, color="#dc2626"))
    out.append(text(350, 215, "Центр циклону (Низький тиск)", size=11, bold=True, color="#991b1b"))

    # Cyclonic rotation arrows around Low center
    out.append(path_arc(350, 180, 36, 45, 220, color="#dc2626", sw=2))
    out.append(path_arc(350, 180, 36, 225, 400, color="#dc2626", sw=2))

    # Available Potential Energy (APE) conversion arrow
    out.append(arrow(150, 270, 250, 210, color="#d97706", sw=2.5))
    out.append(text(140, 250, "Опускання холодного\nта підйом теплого", size=10, bold=True, color="#b45309", anchor="end"))

    # Isobars (dashed concentric oval waves around L)
    out.append(f'<ellipse cx="350" cy="180" rx="90" ry="50" fill="none" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4,4"/>')
    out.append(f'<ellipse cx="350" cy="180" rx="160" ry="85" fill="none" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4,4"/>')

    # Summary box
    tb, _, _ = textbox(380, 365, "Бароклінна нестійкість вивільняє доступну потенціальну енергію (APE) і генерує синоптичні циклони", size=12, pad=6, fill="#fef2f2", stroke="#fca5a5", color="#991b1b")
    out.append(tb)

    return render(path, dw, dh, *out)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    figs = [
        ('fig1-barotropic-vs-baroclinic.svg', make_fig1),
        ('fig2-sea-breeze-solenoid.svg', make_fig2),
        ('fig3-thermal-wind-shear.svg', make_fig3),
        ('fig4-baroclinic-wave-cyclogenesis.svg', make_fig4),
    ]

    for fname, func in figs:
        path = os.path.join(img_dir, fname)
        func(path)
        print(f"Wrote {path}")

if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()
