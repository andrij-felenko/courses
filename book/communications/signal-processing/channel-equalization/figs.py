# -*- coding: utf-8 -*-
import sys, os
import math

# Add scripts directory to path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Fig 1: Багатопроменеве викривлення каналу та міжсимвольна інтерференція (ISI) ──
def fig_channel_isi():
    W, H = 740, 320
    p = []
    
    # Header
    p.append(text(W/2, 24, "Викривлення каналу та виникнення міжсимвольної інтерференції (ISI)", size=15, bold=True, color=LINE))
    
    # Left Box: Ideal Transmitted Signals s[n]
    p.append(rect(20, 45, 210, 255, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    p.append(text(125, 68, "Передані символи s[n]", size=12, bold=True, color=LINE))
    
    # Discrete pulse sequence
    p.append(arrow(35, 250, 215, 250, color=MUTED, sw=1.2)) # time axis
    p.append(arrow(45, 260, 45, 90, color=MUTED, sw=1.2))  # ampl axis
    p.append(text(215, 264, "t", size=11, color=MUTED))
    
    # Pulses (rectangular / clear separation)
    symbols = [(70, 160, "+1"), (110, 220, "-1"), (150, 140, "+1"), (190, 140, "+1")]
    for x, y, val in symbols:
        p.append(line(x, 250, x, y, color="#2563eb", sw=2.5))
        p.append(circle(x, y, 4, fill="#2563eb", stroke="#2563eb"))
        p.append(text(x, y - 10, val, size=11, bold=True, color="#2563eb"))
    
    p.append(text(125, 285, "Чіткі інтервали T_s", size=10, italic=True, color=MUTED))
    
    # Middle: Channel Filter h(t)
    p.append(rect(250, 125, 120, 95, fill="#eff6ff", stroke="#3b82f6", rx=8))
    p.append(text(310, 153, "Канал зв'язку", size=12, bold=True, color="#1d4ed8"))
    p.append(text(310, 173, "h(t) + Шум w(t)", size=11, color="#1e40af"))
    p.append(text(310, 195, "Дисперсія / Згасання", size=9, italic=True, color="#3b82f6"))
    
    p.append(arrow(230, 172, 250, 172, color="#2563eb", sw=2))
    p.append(arrow(370, 172, 390, 172, color="#dc2626", sw=2))
    
    # Right Box: Received Overlapping Signals y(t) with ISI
    p.append(rect(390, 45, 330, 255, fill="#fef2f2", stroke="#fca5a5", rx=8))
    p.append(text(555, 68, "Прийнятий сигнал y(t) з міжсимвольною інтерференцією", size=12, bold=True, color="#991b1b"))
    
    p.append(arrow(405, 250, 705, 250, color=MUTED, sw=1.2))
    p.append(arrow(415, 260, 415, 90, color=MUTED, sw=1.2))
    p.append(text(708, 264, "t", size=11, color=MUTED))
    
    # Overlapping sinc/gaussian tails
    def draw_pulse(cx, amp, col):
        pts = []
        for px in range(cx - 50, cx + 51, 2):
            dx = (px - cx) / 18.0
            val = amp * math.exp(-dx*dx)
            py = 250 - val
            pts.append((px, py))
        path_str = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        p.append('<path d="%s" stroke="%s" fill="none" stroke-width="1.8" stroke-dasharray="3,3"/>' % (path_str, col))

    draw_pulse(460, 90, "#2563eb")
    draw_pulse(520, -50, "#059669")
    draw_pulse(580, 80, "#d97706")
    draw_pulse(640, 80, "#7c3aed")
    
    # Total sum curve
    pts_sum = []
    for px in range(415, 700, 2):
        v1 = 90 * math.exp(-((px - 460)/18.0)**2)
        v2 = -50 * math.exp(-((px - 520)/18.0)**2)
        v3 = 80 * math.exp(-((px - 580)/18.0)**2)
        v4 = 80 * math.exp(-((px - 640)/18.0)**2)
        v_tot = v1 + v2 + v3 + v4
        pts_sum.append((px, 250 - v_tot))
    path_sum = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_sum)
    p.append('<path d="%s" stroke="#dc2626" fill="none" stroke-width="2.5"/>' % path_sum)
    
    b_isi, w_isi, h_isi = textbox(555, 285, "Хвости імпульсів накладаються на сусідні відліки (ISI)", size=10, pad=4, fill="#fee2e2", stroke="#ef4444")
    p.append(b_isi)
    
    render(os.path.join(OUT, "channel-isi-distortion.svg"), W, H, *p)

# ── Fig 2: Частотна характеристика Zero-Forcing vs MMSE ──────────────────────
def fig_zf_vs_mmse_response():
    W, H = 740, 340
    p = []
    
    # Header
    p.append(text(W/2, 24, "Частотна характеристика вирівнювача: Zero-Forcing проти MMSE", size=15, bold=True, color=LINE))
    
    # Main graph area
    gx0, gy0, gw, gh = 60, 270, 640, 210
    p.append(rect(gx0 - 10, 50, gw + 20, gh + 45, fill="#fafafa", stroke="#e2e8f0", rx=6))
    
    # Axes
    p.append(arrow(gx0, gy0, gx0 + gw, gy0, color=LINE, sw=1.5)) # freq axis
    p.append(arrow(gx0, gy0 + 10, gx0, gy0 - gh, color=LINE, sw=1.5)) # magnitude axis
    p.append(text(gx0 + gw - 20, gy0 + 20, "Частота f", size=11, bold=True, color=LINE))
    p.append(text(gx0 - 25, gy0 - gh + 10, "|W(f)|, |H(f)|", size=11, bold=True, color=LINE))
    
    # Channel magnitude |H(f)| with a spectral null at center (x = gx0 + gw/2)
    cx = gx0 + gw / 2.0
    pts_h = []
    pts_zf = []
    pts_mmse = []
    
    snr_inv = 0.08 # 1/SNR parameter for MMSE
    
    for px in range(gx0, gx0 + gw + 1, 3):
        norm_x = (px - cx) / 70.0
        h_val = 0.12 + 0.75 * (1.0 - math.exp(-norm_x*norm_x))
        y_h = gy0 - h_val * (gh * 0.7)
        pts_h.append((px, y_h))
        
        # Zero Forcing: 1 / H(f)
        zf_val = 1.0 / h_val
        y_zf = gy0 - zf_val * 22.0
        if y_zf < gy0 - gh + 5:
            y_zf = gy0 - gh + 5
        pts_zf.append((px, y_zf))
        
        # MMSE: H* / (|H|^2 + 1/SNR)
        mmse_val = h_val / (h_val*h_val + snr_inv)
        y_mmse = gy0 - mmse_val * 22.0
        pts_mmse.append((px, y_mmse))

    path_h = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_h)
    path_zf = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_zf)
    path_mmse = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_mmse)
    
    # Draw Channel H(f)
    p.append('<path d="%s" stroke="#64748b" fill="none" stroke-width="2.5" stroke-dasharray="5,4"/>' % path_h)
    
    # Draw Zero-Forcing (ZF)
    p.append('<path d="%s" stroke="#ef4444" fill="none" stroke-width="2.5"/>' % path_zf)
    
    # Draw MMSE
    p.append('<path d="%s" stroke="#10b981" fill="none" stroke-width="2.8"/>' % path_mmse)
    
    # Annotate spectral null
    p.append(line(cx, gy0, cx, gy0 - gh, color="#cbd5e1", sw=1, dash="2,2"))
    b_null, w_null, h_null = textbox(cx, gy0 + 22, "Глибока завада каналу |H(f)| -> 0", size=10, pad=3, fill="#fff1f2", stroke="#fda4af")
    p.append(b_null)
    
    # Annotate ZF spike (Noise enhancement)
    b_zf_spike, w_zf, h_zf = textbox(cx, gy0 - gh + 20, "ZF: W(f) -> ∞ (посилення шуму)", size=10, pad=4, fill="#fef2f2", stroke="#ef4444")
    p.append(b_zf_spike)
    
    # Annotate MMSE regularization
    b_mmse_reg, w_mmse, h_mmse = textbox(cx + 140, gy0 - 100, "MMSE: обмежується рівнем ~ √SNR", size=10, pad=4, fill="#ecfdf5", stroke="#10b981")
    p.append(b_mmse_reg)
    
    # Legend
    p.append(rect(gx0 + 20, 60, 230, 75, fill="#ffffff", stroke="#cbd5e1", rx=4))
    p.append(line(gx0 + 30, 75, gx0 + 60, 75, color="#64748b", sw=2.5, dash="5,4"))
    p.append(text(gx0 + 70, 78, "Канал |H(f)|", size=10, bold=True, color="#475569"))
    
    p.append(line(gx0 + 30, 95, gx0 + 60, 95, color="#ef4444", sw=2.5))
    p.append(text(gx0 + 70, 98, "Zero-Forcing: 1 / |H(f)|", size=10, bold=True, color="#dc2626"))
    
    p.append(line(gx0 + 30, 115, gx0 + 60, 115, color="#10b981", sw=2.8))
    p.append(text(gx0 + 70, 118, "MMSE: |H*| / (|H|² + 1/SNR)", size=10, bold=True, color="#059669"))

    render(os.path.join(OUT, "equalizer-frequency-response.svg"), W, H, *p)

# ── Fig 3: Сузір'я IQ: Zero-Forcing проти MMSE ──────────────────────────────
def fig_constellation_zf_vs_mmse():
    W, H = 740, 310
    p = []
    
    # Header
    p.append(text(W/2, 24, "Сузір'я сигналів (4-QAM): вплив вирівнювання Zero-Forcing та MMSE", size=15, bold=True, color=LINE))
    
    # Panel 1: Transmitted 4-QAM
    p.append(rect(15, 45, 220, 250, fill="#fafafa", stroke="#cbd5e1", rx=6))
    p.append(text(125, 68, "1. Передане сузір'я", size=12, bold=True, color=LINE))
    
    # Axes
    p.append(line(25, 170, 225, 170, color=MUTED, sw=1))
    p.append(line(125, 75, 125, 265, color=MUTED, sw=1))
    p.append(text(218, 163, "I", size=10, bold=True, color=MUTED))
    p.append(text(132, 85, "Q", size=10, bold=True, color=MUTED))
    
    # Ideal 4 points
    pts_ideal = [(75, 120), (175, 120), (75, 220), (175, 220)]
    for x, y in pts_ideal:
        p.append(circle(x, y, 6, fill="#2563eb", stroke="#1d4ed8"))
    p.append(text(125, 280, "Ідеально чіткі точки", size=10, italic=True, color=MUTED))

    # Panel 2: Zero-Forcing output (Large noise cloud)
    p.append(rect(260, 45, 220, 250, fill="#fef2f2", stroke="#fca5a5", rx=6))
    p.append(text(370, 68, "2. Вихід Zero-Forcing", size=12, bold=True, color="#dc2626"))
    
    p.append(line(270, 170, 470, 170, color=MUTED, sw=1))
    p.append(line(370, 75, 370, 265, color=MUTED, sw=1))
    p.append(text(463, 163, "I", size=10, bold=True, color=MUTED))
    p.append(text(377, 85, "Q", size=10, bold=True, color=MUTED))
    
    centers_zf = [(320, 120), (420, 120), (320, 220), (420, 220)]
    import random
    rng = random.Random(42)
    for cx, cy in centers_zf:
        p.append(circle(cx, cy, 3, fill="#dc2626", stroke="none"))
        for _ in range(18):
            dx = rng.gauss(0, 14.0)
            dy = rng.gauss(0, 14.0)
            p.append(circle(cx + dx, cy + dy, 2, fill="#ef4444", stroke="none"))
            
    b_zf_note, w_zfn, h_zfn = textbox(370, 280, "Центри незсунуті, але шум роздуто", size=9, pad=3, fill="#fee2e2", stroke="#ef4444")
    p.append(b_zf_note)

    # Panel 3: MMSE output (Compact cloud, slight bias towards origin)
    p.append(rect(505, 45, 220, 250, fill="#ecfdf5", stroke="#6ee7b7", rx=6))
    p.append(text(615, 68, "3. Вихід MMSE", size=12, bold=True, color="#059669"))
    
    p.append(line(515, 170, 715, 170, color=MUTED, sw=1))
    p.append(line(615, 75, 615, 265, color=MUTED, sw=1))
    p.append(text(708, 163, "I", size=10, bold=True, color=MUTED))
    p.append(text(622, 85, "Q", size=10, bold=True, color=MUTED))
    
    centers_mmse = [(615 - 42.5, 170 - 42.5), (615 + 42.5, 170 - 42.5), (615 - 42.5, 170 + 42.5), (615 + 42.5, 170 + 42.5)]
    rng_mmse = random.Random(42)
    for cx, cy in centers_mmse:
        p.append(circle(cx, cy, 3, fill="#059669", stroke="none"))
        for _ in range(18):
            dx = rng_mmse.gauss(0, 6.0)
            dy = rng_mmse.gauss(0, 6.0)
            p.append(circle(cx + dx, cy + dy, 2, fill="#10b981", stroke="none"))
            
    b_mmse_note, w_mmn, h_mmn = textbox(615, 280, "Компактна хмара, легке стиснення (зсув)", size=9, pad=3, fill="#d1fae5", stroke="#10b981")
    p.append(b_mmse_note)

    render(os.path.join(OUT, "constellation-zf-vs-mmse.svg"), W, H, *p)

if __name__ == "__main__":
    fig_channel_isi()
    fig_zf_vs_mmse_response()
    fig_constellation_zf_vs_mmse()
    print("Figures generated successfully!")
