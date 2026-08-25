# -*- coding: utf-8 -*-
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def ensure_img_dir():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir

def build_fresnel_ellipsoid():
    W, H = 820, 380
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H))
    out.append('<rect width="100%%" height="100%%" fill="%s"/>' % BG)

    defs = '''<defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />
      </marker>
      <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="%s" />
      </marker>
    </defs>''' % (LINE, NEG)
    out.append(defs)

    b_title, _, _ = textbox(410, 30, "Геометрія зон Френеля та прямої траси (LOS)", size=16, bold=True, pad=8, fill="#eef2f7", stroke="#4a5568")
    out.append(b_title)

    tx_x, tx_y = 110, 200
    rx_x, rx_y = 710, 200
    cx, cy = 410, 200

    out.append('<ellipse cx="%d" cy="%d" rx="300" ry="110" fill="#f0f4fe" stroke="%s" stroke-width="1.5" stroke-dasharray="4,4"/>' % (cx, cy, MUTED))
    out.append('<ellipse cx="%d" cy="%d" rx="300" ry="85" fill="#e1ebfb" stroke="%s" stroke-width="1.5" stroke-dasharray="6,3"/>' % (cx, cy, NEG))
    out.append('<ellipse cx="%d" cy="%d" rx="300" ry="55" fill="#d0e1fd" stroke="%s" stroke-width="2.2"/>' % (cx, cy, FIELD))

    out.append(line(tx_x, tx_y, rx_x, rx_y, color=POS, sw=2.2))

    p_x, p_y = cx, cy - 55

    out.append(line(tx_x, tx_y, p_x, p_y, color=NEG, sw=1.8, dash="5,3"))
    out.append(line(p_x, p_y, rx_x, rx_y, color=NEG, sw=1.8, dash="5,3"))

    out.append(line(cx, cy, cx, p_y, color=FIELD, sw=2))

    out.append(rect(tx_x - 12, tx_y - 30, 24, 60, fill="#3182ce", stroke="#1a365d", sw=1.5, rx=3))
    out.append(text(tx_x, tx_y + 4, "Tx", size=13, color="#ffffff", bold=True))

    out.append(rect(rx_x - 12, rx_y - 30, 24, 60, fill="#3182ce", stroke="#1a365d", sw=1.5, rx=3))
    out.append(text(rx_x, rx_y + 4, "Rx", size=13, color="#ffffff", bold=True))

    dim_y = 330
    out.append(arrow(tx_x, dim_y, cx, dim_y, color=LINE, sw=1.5))
    out.append(arrow(cx, dim_y, tx_x, dim_y, color=LINE, sw=1.5))
    tb_d1, _, _ = textbox((tx_x + cx)/2, dim_y, "d₁", size=13, pad=4, fill="#ffffff", stroke=MUTED, sw=1)
    out.append(tb_d1)

    out.append(arrow(cx, dim_y, rx_x, dim_y, color=LINE, sw=1.5))
    out.append(arrow(rx_x, dim_y, cx, dim_y, color=LINE, sw=1.5))
    tb_d2, _, _ = textbox((cx + rx_x)/2, dim_y, "d₂", size=13, pad=4, fill="#ffffff", stroke=MUTED, sw=1)
    out.append(tb_d2)

    out.append(line(tx_x, tx_y + 35, tx_x, dim_y + 12, color=MUTED, sw=1, dash="2,2"))
    out.append(line(cx, cy + 115, cx, dim_y + 12, color=MUTED, sw=1, dash="2,2"))
    out.append(line(rx_x, rx_y + 35, rx_x, dim_y + 12, color=MUTED, sw=1, dash="2,2"))

    tb_r1, _, _ = textbox(cx + 45, cy - 28, "R₁ (1-ша зона)", size=12, pad=4, fill="#ffffff", stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    out.append(tb_r1)

    tb_r2, _, _ = textbox(cx + 65, cy - 70, "R₂ (2-га зона)", size=11, pad=3, fill="#ffffff", stroke=NEG, sw=1, color=NEG)
    out.append(tb_r2)

    tb_los, _, _ = textbox(250, cy + 18, "Прямий промінь (LOS)", size=12, pad=4, fill="#ffffff", stroke=POS, sw=1.2, color=POS, bold=True)
    out.append(tb_los)

    tb_path, _, _ = textbox(260, cy - 50, "Непрямий шлях (Δ = λ/2)", size=11, pad=3, fill="#ffffff", stroke=NEG, sw=1, color=NEG)
    out.append(tb_path)

    out.append('</svg>')
    return "".join(out)


def build_clearance_loss_curve():
    W, H = 820, 420
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H))
    out.append('<rect width="100%%" height="100%%" fill="%s"/>' % BG)

    b_title, _, _ = textbox(410, 28, "Залежність дифракційних втрат від просвіту траси (c/R₁)", size=16, bold=True, pad=8, fill="#eef2f7", stroke="#4a5568")
    out.append(b_title)

    ox, oy = 100, 340
    gx_w, gy_h = 570, 270

    def map_x(c_val):
        return ox + (c_val - (-1.2)) / (1.5 - (-1.2)) * gx_w

    def map_y(loss_db):
        return oy - (loss_db - (-22)) / (6 - (-22)) * gy_h

    grid_dbs = [-20, -15, -10, -6, 0, 5]
    for db in grid_dbs:
        y_pos = map_y(db)
        out.append(line(ox, y_pos, ox + gx_w, y_pos, color="#e2e8f0", sw=1, dash="3,3" if db != 0 else None))
        lbl = "%+d дБ" % db if db != 0 else "0 дБ (LOS)"
        out.append(text(ox - 12, y_pos + 4, lbl, size=11, color=MUTED, anchor="end"))

    grid_c = [-1.0, -0.6, 0.0, 0.6, 1.0, 1.4]
    for c_val in grid_c:
        x_pos = map_x(c_val)
        out.append(line(x_pos, oy, x_pos, oy - gy_h, color="#e2e8f0", sw=1, dash="3,3" if c_val != 0.6 else None))
        out.append(text(x_pos, oy + 20, "%.1f" % c_val, size=12, color=INK, anchor="middle"))

    out.append(line(ox, oy, ox + gx_w + 10, oy, color=LINE, sw=2))
    out.append(line(ox, oy, ox, oy - gy_h - 10, color=LINE, sw=2))
    out.append(text(ox + gx_w / 2, oy + 42, "Відносний просвіт траси (c / R₁)", size=13, color=INK, bold=True))
    out.append(text(ox - 65, oy - gy_h / 2, "Втрати (дБ)", size=13, color=INK, bold=True, anchor="middle"))

    curve_pts = []
    steps = 100
    for i in range(steps + 1):
        c_val = -1.2 + i * (2.7 / steps)
        v = c_val * 1.4142
        if v < -1.0:
            loss = -6.9 - 20 * math.log10(math.sqrt((v - 0.1)**2 + 1) - v)
        elif v < 1.0:
            loss = -6.0 + 6.0 * v - 1.5 * (v**2)
        else:
            loss = 0.8 * math.sin(3.14159 * (v - 0.6)) * math.exp(-0.8 * (v - 0.6))
        
        px = map_x(c_val)
        py = map_y(loss)
        curve_pts.append((px, py))

    path_d = ["M %.1f %.1f" % curve_pts[0]]
    for px, py in curve_pts[1:]:
        path_d.append("L %.1f %.1f" % (px, py))
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(path_d), NEG))

    x_06, y_06 = map_x(0.6), map_y(0.0)
    out.append(circle(x_06, y_06, 6, fill=FIELD, stroke="#ffffff", sw=2))
    tb_c06, _, _ = textbox(710, 90, "c = 0.6 R₁ (Втрати ≈ 0 дБ)\nКритерій просвіту", size=11, pad=5, fill="#e6fffa", stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    out.append(tb_c06)

    x_00, y_00 = map_x(0.0), map_y(-6.0)
    out.append(circle(x_00, y_00, 6, fill=POS, stroke="#ffffff", sw=2))
    tb_c00, _, _ = textbox(290, 195, "c = 0.0 R₁ (Втрати = 6 дБ)\nДотикання перешкоди", size=11, pad=5, fill="#fff5f5", stroke=POS, sw=1.5, color=POS, bold=True)
    out.append(tb_c00)

    out.append('</svg>')
    return "".join(out)


def build_earth_curvature_profile():
    W, H = 820, 420
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H))
    out.append('<rect width="100%%" height="100%%" fill="%s"/>' % BG)

    b_title, _, _ = textbox(410, 28, "Профіль траси з урахуванням опуклості Землі та атмосферної рефракції", size=15, bold=True, pad=8, fill="#eef2f7", stroke="#4a5568")
    out.append(b_title)

    tx_x, tx_y = 100, 240
    rx_x, rx_y = 720, 240
    cx = (tx_x + rx_x) / 2

    base_y = 340
    earth_bulge = 45
    
    out.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="#4a5568" stroke-width="2.2"/>' % 
               (tx_x - 30, base_y, cx, base_y - earth_bulge, rx_x + 30, base_y))
    out.append('<path d="M %d %d Q %d %d %d %d L %d %d L %d %d Z" fill="#edf2f7" stroke="none"/>' % 
               (tx_x - 30, base_y, cx, base_y - earth_bulge, rx_x + 30, base_y, rx_x + 30, H - 20, tx_x - 30, H - 20))

    obs_x = 220
    nx = (obs_x - tx_x) / (rx_x - tx_x) * 2 - 1
    obs_base_y = base_y - earth_bulge * (1 - nx**2)
    obs_h = 55
    obs_top_y = obs_base_y - obs_h

    tb_obs, _, _ = textbox(obs_x, obs_top_y + obs_h / 2, "Гора", size=12, pad=4, fill="#cbd5e0", stroke="#4a5568", sw=1.5, color=INK, bold=True)
    out.append(tb_obs)

    h_tx = 75
    h_rx = 75
    tx_top_y = base_y - h_tx
    rx_top_y = base_y - h_rx

    out.append(line(tx_x, base_y, tx_x, tx_top_y, color="#2b6cb0", sw=3))
    out.append(circle(tx_x, tx_top_y, 6, fill="#3182ce", stroke="#1a365d", sw=1.5))
    out.append(text(tx_x, base_y + 18, "Щогла Tx (h₁)", size=12, color=INK, bold=True))

    out.append(line(rx_x, base_y, rx_x, rx_top_y, color="#2b6cb0", sw=3))
    out.append(circle(rx_x, rx_top_y, 6, fill="#3182ce", stroke="#1a365d", sw=1.5))
    out.append(text(rx_x, base_y + 18, "Щогла Rx (h₂)", size=12, color=INK, bold=True))

    out.append(line(tx_x, tx_top_y, rx_x, rx_top_y, color=POS, sw=2, dash="6,3"))

    los_obs_y = tx_top_y + (rx_top_y - tx_top_y) * ((cx - tx_x) / (rx_x - tx_x))

    out.append('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,4"/>' %
               (cx, los_obs_y, (rx_x - tx_x)/2, 42, FIELD))

    out.append(line(cx, base_y, cx, base_y - earth_bulge, color="#e53e3e", sw=1.8))
    tb_eb, _, _ = textbox(cx + 90, base_y - earth_bulge - 25, "h_землі (опуклість)", size=11, pad=3, fill="#ffffff", stroke="#e53e3e", sw=1, color="#e53e3e")
    out.append(tb_eb)

    out.append(line(obs_x + 35, obs_top_y, obs_x + 35, los_obs_y, color=FIELD, sw=2))
    tb_clr, _, _ = textbox(obs_x + 110, obs_top_y + (los_obs_y - obs_top_y)/2, "Просвіт c ≥ 0.6 R₁", size=11, pad=4, fill="#ffffff", stroke=FIELD, sw=1.2, color=FIELD, bold=True)
    out.append(tb_clr)

    tb_k, _, _ = textbox(660, 90, "Еквівалентний радіус Землі:\nR_екв = k · R_землі (k = 4/3)", size=11, pad=5, fill="#f7fafc", stroke="#a0aec0", sw=1, color=INK)
    out.append(tb_k)

    out.append('</svg>')
    return "".join(out)


def main():
    img_dir = ensure_img_dir()
    
    files = {
        'fresnel-ellipsoid.svg': build_fresnel_ellipsoid(),
        'clearance-loss-curve.svg': build_clearance_loss_curve(),
        'earth-curvature-profile.svg': build_earth_curvature_profile()
    }
    
    for filename, content in files.items():
        filepath = os.path.join(img_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated: {filepath}")

if __name__ == '__main__':
    main()
