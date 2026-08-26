# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. link-budget-balance: Енергетичний ланцюг радіолінії (баланс дБм та дБ) ──────
def fig_link_budget_balance():
    W, H = 940, 400
    p = []

    p.append(text(W / 2, 28, "Енергетичний ланцюг радіолінії: від передавача до чутливості", size=16, color=INK, bold=True))

    def py(dbm):
        return 75 + (20.0 - dbm) * 1.6875

    for lvl, label in [(20, "+20 дБм"), (0, "0 дБм (1 мВт)"), (-40, "-40 дБм"), (-80, "-80 дБм"), (-120, "-120 дБм")]:
        yy = py(lvl)
        p.append(line(70, yy, 870, yy, color="#e5e7eb", sw=1, dash="4,4"))
        p.append(text(62, yy + 4, label, size=10, color=MUTED, anchor="end"))

    stages = [
        (130, 14.0, "P_tx", "+14 дБм\n(передавач)", POS),
        (240, 12.5, "L_tx", "−1.5 дБ\n(кабель Tx)", NEG),
        (350, 15.0, "G_tx", "+2.5 дБі\n(антена Tx)", POS),
        (510, -90.0, "FSPL", "−105 дБ\n(траса в полі)", NEG),
        (640, -87.5, "G_rx", "+2.5 дБі\n(антена Rx)", POS),
        (750, -89.0, "L_rx", "−1.5 дБ\n(кабель Rx)", NEG),
    ]

    coords = []
    for i, (x, val, tag, desc, col) in enumerate(stages):
        y = py(val)
        coords.append((x, y))

    for i in range(len(coords) - 1):
        x1, y1 = coords[i]
        x2, y2 = coords[i+1]
        p.append(line(x1, y1, x2, y1, color="#9ca3af", sw=1.8, dash="3,3"))
        p.append(arrow(x2, y1, x2, y2, color=LINE, sw=2.2))

    for i, (x, val, tag, desc, col) in enumerate(stages):
        y = py(val)
        p.append(circle(x, y, 6, fill=col, stroke="#ffffff", sw=2))
        
        if val > -50:
            box_html, bw, bh = textbox(x, y - 32, "%s\n%s" % (tag, desc), size=11, pad=6, fill="#f8fafc", stroke=col, sw=1.2)
            p.append(box_html)
        else:
            box_html, bw, bh = textbox(x, y + 32, "%s\n%s" % (tag, desc), size=11, pad=6, fill="#f8fafc", stroke=col, sw=1.2)
            p.append(box_html)

    sens_y = py(-120)
    p.append(line(680, sens_y, 880, sens_y, color=POS, sw=2, dash="6,3"))
    p.append(text(875, sens_y - 8, "S_rx = −120 дБм (поріг чутливості)", size=11, color=POS, anchor="end", bold=True))

    rx_final_y = py(-89)
    p.append(line(840, rx_final_y, 840, sens_y, color=FIELD, sw=2.5))
    p.append(line(833, rx_final_y, 847, rx_final_y, color=FIELD, sw=2))
    p.append(line(833, sens_y, 847, sens_y, color=FIELD, sw=2))
    
    margin_html, mw, mh = textbox(840, (rx_final_y + sens_y) / 2, "Запас на\nзавмирання\n+31 дБ", size=10, pad=5, fill="#ecfdf5", stroke=FIELD, sw=1.5, color="#065f46", bold=True)
    p.append(margin_html)

    render(os.path.join(OUT, "link-budget-balance.svg"), W, H, *p)


# ── 2. friis-sphere-aperture: Геометрія формули Фрііса (сфера та апертура) ──────
def fig_friis_sphere_aperture():
    W, H = 940, 380
    p = []

    p.append(text(W / 2, 28, "Формула Фрііса: сферичне розходження потужності та ефективна апертура", size=16, color=INK, bold=True))

    tx_x, tx_y = 120, 200
    p.append(circle(tx_x, tx_y, 14, fill="#fee2e2", stroke=POS, sw=2))
    p.append(text(tx_x, tx_y + 5, "Tx", size=12, color=POS, bold=True))
    
    tbox, tw, th = textbox(tx_x, tx_y + 42, "Випромінювач\nP_tx · G_tx", size=11, pad=5, fill=FILL, stroke=LINE, sw=1)
    p.append(tbox)

    radii = [80, 160, 260, 420]
    for r in radii:
        p.append('<path d="M %d %d A %d %d 0 0 1 %d %d" fill="none" stroke="#93c5fd" stroke-width="1.8" stroke-dasharray="4,3"/>' % 
                 (tx_x + r * math.cos(math.radians(-35)), tx_y + r * math.sin(math.radians(-35)),
                  r, r,
                  tx_x + r * math.cos(math.radians(35)), tx_y + r * math.sin(math.radians(35))))

    rx_x, rx_y = tx_x + 420, tx_y
    p.append(arrow(tx_x + 16, tx_y, rx_x - 16, rx_y, color=LINE, sw=1.8))
    p.append(text(tx_x + 210, tx_y - 12, "Відстань прямої видимості R", size=12, color=INK, bold=True))

    mid_r = 260
    mid_x = tx_x + mid_r * math.cos(math.radians(25))
    mid_y = tx_y - mid_r * math.sin(math.radians(25))
    box_sph, sw1, sh1 = textbox(mid_x + 80, mid_y - 30, "Густина потоку потужності:\nS = (P_tx · G_tx) / (4·π·R²)\n[Вт/м²]", size=11, pad=6, fill="#eff6ff", stroke=NEG, sw=1.3)
    p.append(box_sph)

    p.append(circle(rx_x, rx_y, 14, fill="#dcfce7", stroke=FIELD, sw=2))
    p.append(text(rx_x, rx_y + 5, "Rx", size=12, color=FIELD, bold=True))

    ap_h = 70
    p.append(rect(rx_x - 6, rx_y - ap_h/2, 12, ap_h, fill="#bbf7d0", stroke=FIELD, sw=2, rx=3))
    p.append(line(rx_x - 14, rx_y - ap_h/2, rx_x - 14, rx_y + ap_h/2, color=FIELD, sw=1.5))
    p.append(line(rx_x - 18, rx_y - ap_h/2, rx_x - 10, rx_y - ap_h/2, color=FIELD, sw=1.5))
    p.append(line(rx_x - 18, rx_y + ap_h/2, rx_x - 10, rx_y + ap_h/2, color=FIELD, sw=1.5))
    p.append(text(rx_x - 26, rx_y + 4, "A_eff", size=11, color=FIELD, anchor="end", bold=True))

    box_rx, rw, rh = textbox(rx_x + 115, rx_y - 20, "Ефективна площа антени:\nA_eff = G_rx · λ² / (4·π)\n\nПрийнята потужність:\nP_rx = S · A_eff", size=11, pad=7, fill="#f0fdf4", stroke=FIELD, sw=1.4)
    p.append(box_rx)

    sum_box, suw, suh = textbox(W / 2, 335, "Формула Фрііса: P_rx = P_tx · G_tx · G_rx · [ λ / (4·π·R) ]²   —   згасання як 1/R² (−6 дБ на кожне подвоєння відстані)", size=12, pad=8, fill="#f8fafc", stroke=LINE, sw=1.5, bold=True)
    p.append(sum_box)

    render(os.path.join(OUT, "friis-sphere-aperture.svg"), W, H, *p)


# ── 3. two-ray-geometry: Двопроменева модель відбиття від землі ──────
def fig_two_ray_geometry():
    W, H = 940, 420
    p = []

    p.append(text(W / 2, 26, "Двопроменева модель: пряма хвиля та хвиля, відбита від землі", size=16, color=INK, bold=True))

    gy = 320
    p.append(line(60, gy, 880, gy, color="#78350f", sw=3))
    p.append(rect(60, gy, 820, 24, fill="#fef3c7", stroke="#d97706", sw=1, rx=0))
    p.append(text(120, gy + 16, "Поверхня ґрунту (плоска земля)", size=11, color="#92400e", italic=True))

    tx_x = 160
    h_tx = 130
    tx_y = gy - h_tx
    p.append(line(tx_x, gy, tx_x, tx_y, color=LINE, sw=3))
    p.append(circle(tx_x, tx_y, 8, fill="#fee2e2", stroke=POS, sw=2))
    p.append(text(tx_x, tx_y - 14, "Tx (h₁)", size=12, color=POS, bold=True))
    
    p.append(line(tx_x - 20, gy, tx_x - 20, tx_y, color=MUTED, sw=1.2))
    p.append(line(tx_x - 25, gy, tx_x - 15, gy, color=MUTED, sw=1.2))
    p.append(line(tx_x - 25, tx_y, tx_x - 15, tx_y, color=MUTED, sw=1.2))
    p.append(text(tx_x - 30, (gy + tx_y)/2 + 4, "h_tx", size=11, color=MUTED, anchor="end", bold=True))

    rx_x = 780
    h_rx = 90
    rx_y = gy - h_rx
    p.append(line(rx_x, gy, rx_x, rx_y, color=LINE, sw=3))
    p.append(circle(rx_x, rx_y, 8, fill="#dcfce7", stroke=FIELD, sw=2))
    p.append(text(rx_x, rx_y - 14, "Rx (h₂)", size=12, color=FIELD, bold=True))

    p.append(line(rx_x + 20, gy, rx_x + 20, rx_y, color=MUTED, sw=1.2))
    p.append(line(rx_x + 15, gy, rx_x + 25, gy, color=MUTED, sw=1.2))
    p.append(line(rx_x + 15, rx_y, rx_x + 25, rx_y, color=MUTED, sw=1.2))
    p.append(text(rx_x + 30, (gy + rx_y)/2 + 4, "h_rx", size=11, color=MUTED, anchor="start", bold=True))

    p.append(arrow(tx_x, tx_y, rx_x, rx_y, color=NEG, sw=2.5))
    p.append(text((tx_x + rx_x)/2, (tx_y + rx_y)/2 - 14, "Прямий промінь (r_dir)", size=12, color=NEG, bold=True))

    refl_x = tx_x + (rx_x - tx_x) * (float(h_tx) / (h_tx + h_rx))
    
    p.append(line(tx_x, tx_y, refl_x, gy, color=POS, sw=2, dash="6,3"))
    p.append(arrow(refl_x, gy, rx_x, rx_y, color=POS, sw=2))
    p.append(circle(refl_x, gy, 5, fill=POS, stroke="#ffffff", sw=1.5))
    
    b_refl, bw, bh = textbox(refl_x, gy + 42, "Точка відбиття від ґрунту\nКоефіцієнт Γ ≈ −1 (зсув фази на 180° / π)", size=10, pad=5, fill="#fff1f2", stroke=POS, sw=1.2, color=POS)
    p.append(b_refl)

    p.append(line(tx_x, gy + 75, rx_x, gy + 75, color=LINE, sw=1.5))
    p.append(line(tx_x, gy + 70, tx_x, gy + 80, color=LINE, sw=1.5))
    p.append(line(rx_x, gy + 70, rx_x, gy + 80, color=LINE, sw=1.5))
    p.append(text((tx_x + rx_x)/2, gy + 71, "Горизонтальна відстань R", size=11, color=INK, bold=True))

    box_math, mw, mh = textbox(470, 95, "Різниця ходу променів: Δd = r_refl − r_dir ≈ (2 · h_tx · h_rx) / R\nРізниця фаз: Δθ = (2·π·Δd / λ) + π (зсув ґрунту)", size=11, pad=7, fill="#f8fafc", stroke=LINE, sw=1.3)
    p.append(box_math)

    render(os.path.join(OUT, "two-ray-geometry.svg"), W, H, *p)


# ── 4. pathloss-breakpoint: Порівняння FSPL (1/R^2) та Two-Ray (1/R^4) ──────
def fig_pathloss_breakpoint():
    W, H = 940, 430
    p = []

    p.append(text(W / 2, 26, "Крива втрат: перехід від вільного простору (1/R²) до згасання над землею (1/R⁴)", size=16, color=INK, bold=True))

    x0, y0 = 100, 360
    xw, yh = 780, 280

    def sx(dist_m):
        return x0 + (math.log10(dist_m) - 1.0) / 3.0 * xw

    def sy(loss_db):
        return y0 - (loss_db - 40.0) / 120.0 * yh

    for l_db in [60, 80, 100, 120, 140, 160]:
        yy = sy(l_db)
        p.append(line(x0, yy, x0 + xw, yy, color="#e5e7eb", sw=1))
        p.append(text(x0 - 10, yy + 4, "%d дБ" % l_db, size=10, color=MUTED, anchor="end"))

    for d_m, lab in [(10, "10 м"), (50, "50 м"), (100, "100 м"), (300, "300 м"), (1000, "1 км"), (3000, "3 км"), (10000, "10 км")]:
        xx = sx(d_m)
        p.append(line(xx, y0, xx, y0 - yh, color="#e5e7eb", sw=1))
        p.append(text(xx, y0 + 18, lab, size=10, color=MUTED, anchor="middle"))

    p.append(line(x0, y0, x0 + xw, y0, color=LINE, sw=1.8))
    p.append(line(x0, y0, x0, y0 - yh, color=LINE, sw=1.8))
    p.append(text(x0 + xw, y0 + 32, "Відстань R (логарифмічна шкала) →", size=11, color=INK, anchor="end", bold=True))
    p.append(text(x0 - 10, y0 - yh - 10, "Згасання на трасі L (дБ) ↑", size=11, color=INK, anchor="start", bold=True))

    fspl_pts = []
    for d in [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]:
        l_val = 20 * math.log10(d) + 31.2
        fspl_pts.append((sx(d), sy(l_val)))
    
    fspl_str = " ".join("%.1f,%.1f" % pt for pt in fspl_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6,4"/>' % (fspl_str, NEG))
    p.append(text(sx(4000), sy(20 * math.log10(4000) + 31.2) - 10, "FSPL 1/R² (−20 дБ/дек)", size=11, color=NEG, bold=True))

    two_ray_pts = []
    d_vals = [10, 12, 14, 16, 18, 20, 22, 24, 26, 35, 50, 80, 120, 200, 350, 600, 1000, 2000, 4000, 7000, 10000]
    for d in d_vals:
        lam = 0.345
        d_phi = (4 * math.pi * 1.5 * 1.5) / (lam * d)
        sin_val = math.sin(d_phi / 2.0)
        if d > 40:
            l_val = 40 * math.log10(d) + 12.0
        else:
            ripple = -10 * math.log10(max(1e-4, 4.0 * (sin_val ** 2)))
            l_val = 20 * math.log10(d) + 31.2 + ripple
        two_ray_pts.append((sx(d), sy(min(160, max(40, l_val)))))

    two_ray_str = " ".join("%.1f,%.1f" % pt for pt in two_ray_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (two_ray_str, POS))
    p.append(text(sx(1800), sy(40 * math.log10(1800) + 12.0) + 18, "Two-Ray 1/R⁴ (−40 дБ/дек)", size=11, color=POS, bold=True))

    # Breakpoint vertical marker (ending below the textbox area)
    d_brk = 26.1
    bx = sx(d_brk)
    p.append(line(bx, y0, bx, y0 - yh + 70, color=FIELD, sw=2, dash="4,3"))
    p.append(circle(bx, sy(60), 6, fill=FIELD, stroke="#ffffff", sw=2))
    
    brk_box, bw, bh = textbox(bx + 130, y0 - yh + 35, "Точка зламу d_break = 4·h₁·h₂ / λ\n(≈ 26 м для h=1.5 м, 868 МГц)", size=10, pad=6, fill="#ecfdf5", stroke=FIELD, sw=1.3, color="#065f46", bold=True)
    p.append(brk_box)

    render(os.path.join(OUT, "pathloss-breakpoint.svg"), W, H, *p)


# ── 5. field-technique-rssi-snr: Методика оцінки сигналу та зони надійності ──────
def fig_field_technique_rssi_snr():
    W, H = 940, 390
    p = []

    p.append(text(W / 2, 26, "Польова оцінка каналу: RSSI, SNR та поріг стійкого прийому", size=16, color=INK, bold=True))

    bar_x, bar_w = 120, 90
    top_y, bot_y = 65, 335
    total_h = bot_y - top_y

    def y_of(dbm):
        return top_y + (0 - dbm) / 140.0 * total_h

    p.append(rect(bar_x, y_of(0), bar_w, y_of(-80) - y_of(0), fill="#dcfce7", stroke=FIELD, sw=1.5, rx=0))
    p.append(text(bar_x + bar_w/2, (y_of(0) + y_of(-80))/2 + 4, "Надійний зв'язок\nPER = 0%", size=11, color="#15803d", bold=True))

    p.append(rect(bar_x, y_of(-80), bar_w, y_of(-115) - y_of(-80), fill="#fef9c3", stroke="#ca8a04", sw=1.5, rx=0))
    p.append(text(bar_x + bar_w/2, (y_of(-80) + y_of(-115))/2 + 4, "Буфер завмирання\nPER < 1%", size=11, color="#854d0e", bold=True))

    p.append(rect(bar_x, y_of(-115), bar_w, y_of(-125) - y_of(-115), fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=0))
    p.append(text(bar_x + bar_w/2, (y_of(-115) + y_of(-125))/2 + 4, "Зона обриву\nPER 1–50%", size=10, color="#9a3412", bold=True))

    p.append(rect(bar_x, y_of(-125), bar_w, y_of(-140) - y_of(-125), fill="#fee2e2", stroke=POS, sw=1.5, rx=0))
    p.append(text(bar_x + bar_w/2, (y_of(-125) + y_of(-140))/2 + 4, "Втрата зв'язку\nPER = 100%", size=10, color=POS, bold=True))

    for lvl in [0, -40, -80, -100, -115, -125, -140]:
        yy = y_of(lvl)
        p.append(line(bar_x - 8, yy, bar_x, yy, color=LINE, sw=1.5))
        p.append(text(bar_x - 14, yy + 4, "%d дБм" % lvl, size=10, color=MUTED, anchor="end"))

    cx = 540

    c1, w1, h1 = textbox(cx, 110, "1. RSSI (Received Signal Strength Indicator)\nПоказує сумарну енергію в каналі (сигнал + завади + шум).\nВисокий RSSI не гарантує зв'язку, якщо поруч потужна завада!", size=11, pad=8, fill="#f8fafc", stroke=LINE, sw=1.2)
    p.append(c1)

    c2, w2, h2 = textbox(cx, 210, "2. SNR (Signal-to-Noise Ratio)\nПоказує перевищення сигналу над локальним шумом.\nДля LoRa допустимий SNR < 0 (до −20 дБ), для FSK/BLE треба SNR > +8...+14 дБ.", size=11, pad=8, fill="#eff6ff", stroke=NEG, sw=1.2)
    p.append(c2)

    c3, w3, h3 = textbox(cx, 310, "3. PER (Packet Error Rate) та Запас (Fade Margin)\nПольовий тест вимагає вимірювання відсотка втрачених пакетів.\nЗапас 15–20 дБ над порогом чутливості гарантує зв'язок під час завмирань.", size=11, pad=8, fill="#ecfdf5", stroke=FIELD, sw=1.2)
    p.append(c3)

    p.append(arrow(bar_x + bar_w, y_of(-80), cx - w1/2, 110, color=MUTED, sw=1.2))
    p.append(arrow(bar_x + bar_w, y_of(-115), cx - w2/2, 210, color=MUTED, sw=1.2))
    p.append(arrow(bar_x + bar_w, y_of(-125), cx - w3/2, 310, color=MUTED, sw=1.2))

    render(os.path.join(OUT, "field-technique-rssi-snr.svg"), W, H, *p)


if __name__ == "__main__":
    fig_link_budget_balance()
    fig_friis_sphere_aperture()
    fig_two_ray_geometry()
    fig_pathloss_breakpoint()
    fig_field_technique_rssi_snr()
    print("All figures generated successfully.")
