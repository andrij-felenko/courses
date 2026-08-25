# -*- coding: utf-8 -*-
import os
import sys
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

def fig_wavelength_definition():
    w, h = 840, 380
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" style="background:#fff;">' % (w, h, w, h),
        '<defs>',
        '  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>',
        '  </marker>',
        '  <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#2457d6"/>',
        '  </marker>',
        '  <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#c0392b"/>',
        '  </marker>',
        '</defs>'
    ]

    # Grid / Axes
    cy = 200
    x0, x1 = 60, 700
    out.append(line(x0, cy, x1, cy, color=MUTED, sw=1.2, dash="4,4"))
    out.append(arrow(x0, cy, x1 + 15, cy, color=LINE, sw=1.5))
    out.append(text(x1 + 25, cy + 4, "x (простір)", size=13, color=INK, bold=True, anchor="start"))

    # Vertical axis (Amplitude)
    out.append(arrow(x0, cy + 120, x0, cy - 135, color=LINE, sw=1.5))
    out.append(text(x0, cy - 148, "u(x)", size=13, color=INK, bold=True, anchor="middle"))

    # Draw sine wave: u(x) = A * sin(2*pi*(x - x0)/lambda)
    lam = 240
    amp = 80
    pts = []
    for px in range(x0, x1 + 1):
        phase = 2 * math.pi * (px - x0) / lam
        py = cy - amp * math.sin(phase)
        pts.append("%.1f,%.1f" % (px, py))

    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts), NEG))

    # Crests and Troughs points
    c1_x, c2_x, c3_x = x0 + 60, x0 + 300, x0 + 540
    t1_x, t2_x = x0 + 180, x0 + 420

    # Dimension lines for Lambda (Crest to Crest)
    y_crest_dim = 65
    out.append(line(c1_x, cy - amp - 18, c1_x, y_crest_dim + 4, color=MUTED, sw=1, dash="2,2"))
    out.append(line(c2_x, cy - amp - 18, c2_x, y_crest_dim + 4, color=MUTED, sw=1, dash="2,2"))
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" marker-start="url(#arrow-red)" marker-end="url(#arrow-red)"/>' % (c1_x, y_crest_dim, c2_x, y_crest_dim, POS))
    tb_c, _, _ = textbox((c1_x + c2_x)/2, y_crest_dim - 20, "Довжина хвилі λ (між гребенями)", size=12, pad=4, fill="#fdf2f2", stroke=POS, color=POS, bold=True)
    out.append(tb_c)

    # Dimension lines for Lambda (Trough to Trough)
    y_trough_dim = 330
    out.append(line(t1_x, cy + amp + 18, t1_x, y_trough_dim - 4, color=MUTED, sw=1, dash="2,2"))
    out.append(line(t2_x, cy + amp + 18, t2_x, y_trough_dim - 4, color=MUTED, sw=1, dash="2,2"))
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" marker-start="url(#arrow-blue)" marker-end="url(#arrow-blue)"/>' % (t1_x, y_trough_dim, t2_x, y_trough_dim, NEG))
    tb_t, _, _ = textbox((t1_x + t2_x)/2, y_trough_dim + 20, "Довжина хвилі λ (між впадинами)", size=12, pad=4, fill="#f2f5fd", stroke=NEG, color=NEG, bold=True)
    out.append(tb_t)

    # Amplitude indicator
    out.append(line(c3_x, cy, c3_x, cy - amp, color=POS, sw=1.5, dash="2,2"))
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.5" marker-start="url(#arrow-red)" marker-end="url(#arrow-red)"/>' % (c3_x + 18, cy, c3_x + 18, cy - amp, POS))
    out.append(text(c3_x + 30, cy - amp/2, "Амплітуда A", size=12, color=POS, bold=True, anchor="start"))

    # Labels on wave features
    out.append(circle(c1_x, cy - amp, 4, fill=POS, stroke=POS))
    out.append(text(c1_x, cy - amp - 10, "Гребінь", size=11, color=POS, bold=True))
    
    out.append(circle(t1_x, cy + amp, 4, fill=NEG, stroke=NEG))
    out.append(text(t1_x, cy + amp + 14, "Впадина", size=11, color=NEG, bold=True))

    out.append("</svg>")
    return "\n".join(out)

def fig_medium_transition():
    w, h = 760, 340
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" style="background:#fff;">' % (w, h, w, h),
        '<defs>',
        '  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>',
        '  </marker>',
        '  <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#27ae60"/>',
        '  </marker>',
        '</defs>'
    ]

    boundary_x = 360
    cy = 170

    out.append(rect(20, 40, boundary_x - 20, h - 70, fill="#f9fbfd", stroke="#d0d7de", sw=1, rx=4))
    out.append(rect(boundary_x, 40, w - 20 - boundary_x, h - 70, fill="#f2f9f5", stroke="#c3e6cb", sw=1, rx=4))

    out.append(line(boundary_x, 30, boundary_x, h - 20, color=POS, sw=2, dash="5,4"))
    out.append(text(boundary_x, 22, "Межа середовищ", size=13, color=POS, bold=True))

    out.append(text(180, 65, "Середовище 1 (повільніше)", size=14, color=NEG, bold=True))
    out.append(text(180, 85, "v₁ = 343 м/с (повітря)", size=12, color=MUTED))

    out.append(text(560, 65, "Середовище 2 (швидше)", size=14, color=FIELD, bold=True))
    out.append(text(560, 85, "v₂ = 1500 м/с (вода)", size=12, color=MUTED))

    out.append(line(40, cy, w - 40, cy, color=MUTED, sw=1, dash="3,3"))

    lam1 = 70
    amp = 50
    pts1 = []
    for px in range(40, boundary_x + 1):
        phase = 2 * math.pi * (px - 40) / lam1
        py = cy - amp * math.sin(phase)
        pts1.append("%.1f,%.1f" % (px, py))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts1), NEG))

    phase_at_boundary = 2 * math.pi * (boundary_x - 40) / lam1
    lam2 = 160
    pts2 = []
    for px in range(boundary_x, w - 40 + 1):
        phase = phase_at_boundary + 2 * math.pi * (px - boundary_x) / lam2
        py = cy - amp * math.sin(phase)
        pts2.append("%.1f,%.1f" % (px, py))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts2), FIELD))

    dim_y = cy + amp + 30
    c1_m1 = 127.5
    c2_m1 = 197.5
    out.append(line(c1_m1, cy + amp, c1_m1, dim_y + 5, color=MUTED, sw=1, dash="2,2"))
    out.append(line(c2_m1, cy + amp, c2_m1, dim_y + 5, color=MUTED, sw=1, dash="2,2"))
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" marker-start="url(#arrow)" marker-end="url(#arrow)"/>' % (c1_m1, dim_y, c2_m1, dim_y, LINE))
    out.append(text((c1_m1 + c2_m1)/2, dim_y + 18, "λ₁ = v₁ / f", size=13, color=NEG, bold=True))

    crests2 = []
    for px in range(boundary_x, w - 40):
        ph = phase_at_boundary + 2 * math.pi * (px - boundary_x) / lam2
        if math.sin(ph) > 0.999:
            crests2.append(px)
    if len(crests2) >= 2:
        c1_m2 = crests2[0]
        c2_m2 = crests2[1]
        out.append(line(c1_m2, cy - amp, c1_m2, dim_y + 5, color=MUTED, sw=1, dash="2,2"))
        out.append(line(c2_m2, cy - amp, c2_m2, dim_y + 5, color=MUTED, sw=1, dash="2,2"))
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" marker-start="url(#arrow-green)" marker-end="url(#arrow-green)"/>' % (c1_m2, dim_y, c2_m2, dim_y, FIELD))
        out.append(text((c1_m2 + c2_m2)/2, dim_y + 18, "λ₂ = v₂ / f  (λ₂ > λ₁)", size=13, color=FIELD, bold=True))

    tb_key, _, _ = textbox(w/2, h - 25, "Головний принцип: частота f не змінюється на межі, тому λ ∝ v", size=13, pad=6, fill="#fff8e6", stroke="#f39c12", color="#b7950b", bold=True)
    out.append(tb_key)

    out.append("</svg>")
    return "\n".join(out)

def fig_standing_wave_nodes():
    w, h = 760, 330
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" style="background:#fff;">' % (w, h, w, h),
        '<defs>',
        '  <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#c0392b"/>',
        '  </marker>',
        '  <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#2457d6"/>',
        '  </marker>',
        '</defs>'
    ]

    cy = 150
    x0, x1 = 80, 680
    lam = 300
    amp = 75

    out.append(line(x0 - 20, cy, x1 + 20, cy, color=MUTED, sw=1.2, dash="4,4"))

    pts_pos = []
    pts_neg = []
    for px in range(x0, x1 + 1):
        phase = 2 * math.pi * (px - x0) / lam
        py_pos = cy - amp * math.sin(phase)
        py_neg = cy + amp * math.sin(phase)
        pts_pos.append("%.1f,%.1f" % (px, py_pos))
        pts_neg.append("%.1f,%.1f" % (px, py_neg))

    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_pos), NEG))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,3"/>' % (" ".join(pts_neg), NEG))

    nodes = [x0 + i * (lam / 2) for i in range(5)]
    antinodes = [x0 + (i + 0.5) * (lam / 2) for i in range(4)]

    for idx, nx in enumerate(nodes):
        out.append(circle(nx, cy, 5, fill=POS, stroke=POS))
        out.append(text(nx, cy + 22, "Вузол N%d" % (idx + 1), size=11, color=POS, bold=True))

    for idx, ax in enumerate(antinodes):
        y_ant = cy - amp if idx % 2 == 0 else cy + amp
        out.append(circle(ax, y_ant, 4, fill=FIELD, stroke=FIELD))
        y_txt = cy - amp - 12 if idx % 2 == 0 else cy + amp + 18
        out.append(text(ax, y_txt, "Пучність A%d" % (idx + 1), size=11, color=FIELD, bold=True))

    n1_x, n2_x = nodes[1], nodes[2]
    y_dim_node = cy - amp - 35
    out.append(line(n1_x, cy, n1_x, y_dim_node - 5, color=MUTED, sw=1, dash="2,2"))
    out.append(line(n2_x, cy, n2_x, y_dim_node - 5, color=MUTED, sw=1, dash="2,2"))
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" marker-start="url(#arrow-red)" marker-end="url(#arrow-red)"/>' % (n1_x, y_dim_node, n2_x, y_dim_node, POS))
    tb_n, _, _ = textbox((n1_x + n2_x)/2, y_dim_node - 2, "Відстань між вузлами = λ / 2", size=12, pad=5, fill="#fdf2f2", stroke=POS, color=POS, bold=True)
    out.append(tb_n)

    n0_x, n2_x = nodes[0], nodes[2]
    y_dim_full = cy + amp + 45
    out.append(line(n0_x, cy, n0_x, y_dim_full + 5, color=MUTED, sw=1, dash="2,2"))
    out.append(line(n2_x, cy, n2_x, y_dim_full + 5, color=MUTED, sw=1, dash="2,2"))
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" marker-start="url(#arrow-blue)" marker-end="url(#arrow-blue)"/>' % (n0_x, y_dim_full, n2_x, y_dim_full, NEG))
    tb_f, _, _ = textbox((n0_x + n2_x)/2, y_dim_full + 2, "Повна довжина хвилі λ (два інтервали між вузлами)", size=12, pad=5, fill="#f2f5fd", stroke=NEG, color=NEG, bold=True)
    out.append(tb_f)

    out.append("</svg>")
    return "\n".join(out)

def fig_dispersion_phase_group():
    w, h = 760, 350
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" style="background:#fff;">' % (w, h, w, h),
        '<defs>',
        '  <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#c0392b"/>',
        '  </marker>',
        '  <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#2457d6"/>',
        '  </marker>',
        '</defs>'
    ]

    cy = 160
    x0, x1 = 50, 710

    out.append(line(x0, cy, x1, cy, color=MUTED, sw=1, dash="3,3"))

    xc = 380
    sigma = 110
    lam_carrier = 32
    pts_wave = []
    pts_env_top = []
    pts_env_bot = []

    for px in range(x0, x1 + 1):
        env = 100 * math.exp(-((px - xc) / sigma) ** 2)
        carrier = math.sin(2 * math.pi * (px - x0) / lam_carrier)
        py = cy - env * carrier
        pts_wave.append("%.1f,%.1f" % (px, py))
        pts_env_top.append("%.1f,%.1f" % (px, cy - env))
        pts_env_bot.append("%.1f,%.1f" % (px, cy + env))

    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,4"/>' % (" ".join(pts_env_top), POS))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,4"/>' % (" ".join(pts_env_bot), POS))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts_wave), NEG))

    c_x1 = xc - lam_carrier/2
    c_x2 = xc + lam_carrier/2
    y_c_dim = cy - 115
    out.append(line(c_x1, cy - 80, c_x1, y_c_dim - 5, color=MUTED, sw=1, dash="2,2"))
    out.append(line(c_x2, cy - 80, c_x2, y_c_dim - 5, color=MUTED, sw=1, dash="2,2"))
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" marker-start="url(#arrow-blue)" marker-end="url(#arrow-blue)"/>' % (c_x1, y_c_dim, c_x2, y_c_dim, NEG))
    out.append(text((c_x1 + c_x2)/2, y_c_dim - 8, "Довжина несучої хвилі λ", size=12, color=NEG, bold=True))

    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" marker-end="url(#arrow-blue)"/>' % (xc - 40, cy + 50, xc + 40, cy + 50, NEG))
    out.append(text(xc, cy + 70, "Фазова швидкість vp = ω / k  (рух окремих гребенів)", size=12, color=NEG, bold=True))

    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" marker-end="url(#arrow-red)"/>' % (xc - 70, cy + 110, xc + 70, cy + 110, POS))
    out.append(text(xc, cy + 130, "Групова швидкість vg = dω / dk  (рух огинаючої та енергії)", size=12, color=POS, bold=True))

    out.append("</svg>")
    return "\n".join(out)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    figs = {
        'wavelength-definition.svg': fig_wavelength_definition(),
        'medium-transition.svg': fig_medium_transition(),
        'standing-wave-nodes.svg': fig_standing_wave_nodes(),
        'dispersion-phase-group.svg': fig_dispersion_phase_group()
    }

    for name, content in figs.items():
        path = os.path.join(img_dir, name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Generated %s" % path)

if __name__ == '__main__':
    main()
