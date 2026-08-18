# -*- coding: utf-8 -*-
# Фігури до статті «Джиттер вибірки» (book/communications/synchronization/sampling-jitter).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

def polygon(pts, fill=FILL, stroke=LINE, sw=1.5):
    pts_str = " ".join("%.1f,%.1f" % (p[0], p[1]) for p in pts)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts_str, fill, stroke, sw)


# ── Фігура 1: Перетворення часового джиттеру на похибку напруги ────────────────
def fig_jitter_sampling_error():
    W, H = 760, 430
    parts = []

    parts.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Заголовок зверху
    parts.append(text(W / 2, 40, "Механізм виникнення похибки напруги: ΔV = (dV/dt) · Δt", size=14, color=INK, anchor="middle", bold=True))

    # Ліва панель: Низька частота сигналу (пологий нахил)
    parts.append(rect(30, 65, 335, 335, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(197, 90, "Низька частота f_in (малий нахил dV/dt)", size=12, color=INK, anchor="middle", bold=True))
    parts.append(text(197, 108, "Той самий джиттер Δt → незначна похибка ΔV ≪ LSB", size=10, color=MUTED, anchor="middle"))

    # Осі лівої панелі
    parts.append(line(55, 340, 345, 340, color="#94a3b8", sw=1.2))
    parts.append(line(75, 360, 75, 130, color="#94a3b8", sw=1.2))
    parts.append(text(340, 355, "t", size=11, color=MUTED, anchor="end", italic=True))
    parts.append(text(65, 140, "V", size=11, color=MUTED, anchor="middle", italic=True))

    # Синусоїда низької частоти
    pts_low = []
    for i in range(120):
        t_val = i / 119.0
        x = 75 + t_val * 250
        y = 245 - 90 * math.sin(t_val * math.pi * 0.7 + 0.1)
        pts_low.append((x, y))
    for i in range(len(pts_low) - 1):
        parts.append(line(pts_low[i][0], pts_low[i][1], pts_low[i+1][0], pts_low[i+1][1], color=NEG, sw=2))

    # Точка вибірки ліворуч
    t0_x = 180
    t_early_x = 165
    t_late_x = 195
    y_early = 245 - 90 * math.sin(((t_early_x - 75) / 250.0) * math.pi * 0.7 + 0.1)
    y_late = 245 - 90 * math.sin(((t_late_x - 75) / 250.0) * math.pi * 0.7 + 0.1)

    # Смуга джиттеру в часі
    parts.append(rect(t_early_x, 140, t_late_x - t_early_x, 200, fill="#fee2e2", stroke="none"))
    parts.append(line(t0_x, 135, t0_x, 340, color=POS, sw=1.2, dash="3 3"))
    parts.append(line(t_early_x, 140, t_early_x, 340, color="#ef4444", sw=1, dash="2 2"))
    parts.append(line(t_late_x, 140, t_late_x, 340, color="#ef4444", sw=1, dash="2 2"))

    # Похибка напруги ліворуч
    parts.append(line(65, y_early, 320, y_early, color="#b91c1c", sw=1, dash="2 2"))
    parts.append(line(65, y_late, 320, y_late, color="#b91c1c", sw=1, dash="2 2"))
    parts.append(arrow(310, y_late, 310, y_early, color=POS, sw=1.3))
    parts.append(text(318, (y_early + y_late) / 2 + 4, "ΔV_low", size=10, color=POS, anchor="start", bold=True))

    parts.append(arrow(t_early_x, 325, t_late_x, 325, color=POS, sw=1.3))
    parts.append(text(t0_x, 315, "±Δt (джиттер)", size=10, color=POS, anchor="middle", bold=True))

    b_low, _, _ = textbox(197, 375, "Шум джиттеру потопає у шумі квантування", size=10, fill="#eff6ff", stroke=NEG, pad=5)
    parts.append(b_low)

    # Права панель: Висока частота сигналу (крутий нахил)
    parts.append(rect(395, 65, 335, 335, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(562, 90, "Висока частота f_in (крутий нахил dV/dt)", size=12, color=INK, anchor="middle", bold=True))
    parts.append(text(562, 108, "Той самий джиттер Δt → катастрофічна похибка ΔV ≫ LSB", size=10, color=POS, anchor="middle"))

    # Осі правої панелі
    parts.append(line(420, 340, 710, 340, color="#94a3b8", sw=1.2))
    parts.append(line(440, 360, 440, 130, color="#94a3b8", sw=1.2))
    parts.append(text(705, 355, "t", size=11, color=MUTED, anchor="end", italic=True))
    parts.append(text(430, 140, "V", size=11, color=MUTED, anchor="middle", italic=True))

    # Синусоїда високої частоти
    pts_high = []
    for i in range(120):
        t_val = i / 119.0
        x = 440 + t_val * 250
        y = 245 - 95 * math.sin(t_val * math.pi * 2.8 - 0.2)
        pts_high.append((x, y))
    for i in range(len(pts_high) - 1):
        parts.append(line(pts_high[i][0], pts_high[i][1], pts_high[i+1][0], pts_high[i+1][1], color=NEG, sw=2))

    # Точка вибірки праворуч
    t0_rx = 545
    t_early_rx = 530
    t_late_rx = 560
    y_early_r = 245 - 95 * math.sin(((t_early_rx - 440) / 250.0) * math.pi * 2.8 - 0.2)
    y_late_r = 245 - 95 * math.sin(((t_late_rx - 440) / 250.0) * math.pi * 2.8 - 0.2)

    # Смуга джиттеру в часі
    parts.append(rect(t_early_rx, 140, t_late_rx - t_early_rx, 200, fill="#fee2e2", stroke="none"))
    parts.append(line(t0_rx, 135, t0_rx, 340, color=POS, sw=1.2, dash="3 3"))
    parts.append(line(t_early_rx, 140, t_early_rx, 340, color="#ef4444", sw=1, dash="2 2"))
    parts.append(line(t_late_rx, 140, t_late_rx, 340, color="#ef4444", sw=1, dash="2 2"))

    # Похибка напруги праворуч
    parts.append(line(430, y_early_r, 685, y_early_r, color="#b91c1c", sw=1, dash="2 2"))
    parts.append(line(430, y_late_r, 685, y_late_r, color="#b91c1c", sw=1, dash="2 2"))
    parts.append(arrow(675, y_late_r, 675, y_early_r, color=POS, sw=1.5))
    parts.append(text(683, (y_early_r + y_late_r) / 2 + 4, "ΔV_high", size=10, color=POS, anchor="start", bold=True))

    parts.append(arrow(t_early_rx, 325, t_late_rx, 325, color=POS, sw=1.3))
    parts.append(text(t0_rx, 315, "±Δt (той самий джиттер)", size=10, color=POS, anchor="middle", bold=True))

    b_high, _, _ = textbox(562, 375, "Похибка напруги перевищує десятки LSB (деградація ENOB)", size=10, fill="#fef2f2", stroke=POS, pad=5)
    parts.append(b_high)

    return render(os.path.join(OUT, 'jitter-sampling-error.svg'), W, H,
                  *parts, title='Перетворення часового джиттеру на похибку напруги')


# ── Фігура 2: Фазовий шум генератора L(f) та часовий джиттер σ_t ───────────────
def fig_phase_noise_to_jitter():
    W, H = 760, 420
    parts = []

    parts.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    parts.append(text(W / 2, 40, "Зв'язок між частотним фазовим шумом L(f) та часовим джиттером σ_t", size=14, color=INK, anchor="middle", bold=True))

    # Лівий блок: Спектральна густина фазового шуму L(f)
    parts.append(rect(30, 65, 340, 325, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(200, 90, "Частотна область: Фазовий шум L(f)", size=12, color=INK, anchor="middle", bold=True))
    parts.append(text(200, 108, "Спектральна густина потужності [дБн/Гц] vs зсув частоти Δf", size=10, color=MUTED, anchor="middle"))

    # Графік L(f)
    parts.append(line(55, 320, 350, 320, color="#94a3b8", sw=1.2))
    parts.append(line(75, 340, 75, 130, color="#94a3b8", sw=1.2))
    parts.append(text(345, 335, "Δf (зсув)", size=10, color=MUTED, anchor="end"))
    parts.append(text(65, 140, "L(f)", size=11, color=MUTED, anchor="middle", italic=True))

    # Крива фазового шуму
    curve_pts = [
        (85, 150), (110, 175), (140, 205), (180, 235), (230, 260), (280, 275), (335, 280)
    ]
    for i in range(len(curve_pts) - 1):
        parts.append(line(curve_pts[i][0], curve_pts[i][1], curve_pts[i+1][0], curve_pts[i+1][1], color=NEG, sw=2.2))

    # Заштрихована область інтегрування від f1 до f2
    int_poly = [(140, 320), (140, 205), (180, 235), (230, 260), (280, 275), (280, 320)]
    parts.append(polygon(int_poly, fill="#dbeafe", stroke=NEG, sw=1))

    parts.append(line(140, 200, 140, 325, color=NEG, sw=1, dash="2 2"))
    parts.append(line(280, 270, 280, 325, color=NEG, sw=1, dash="2 2"))
    parts.append(text(140, 335, "f₁ (10 Гц)", size=9, color=INK, anchor="middle"))
    parts.append(text(280, 335, "f₂ (30 МГц)", size=9, color=INK, anchor="middle"))

    parts.append(text(210, 280, "Інтеграл: 2 ∫ L(f) df", size=10, color=NEG, anchor="middle", bold=True))

    b_pnoise, _, _ = textbox(200, 368, "σ_φ = √( 2 · ∫_{f₁}^{f₂} 10^{L(f)/10} df ) [рад]", size=10, fill="#eff6ff", stroke=NEG, pad=5)
    parts.append(b_pnoise)

    # Центральна стрілка переходу
    parts.append(arrow(375, 215, 395, 215, color=POS, sw=2))
    parts.append(text(385, 200, "σ_t = σ_φ / (2π f₀)", size=10, color=POS, anchor="middle", bold=True))

    # Правий блок: Часовий джиттер σ_t
    parts.append(rect(400, 65, 330, 325, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(565, 90, "Часова область: Апертурний джиттер σ_t", size=12, color=INK, anchor="middle", bold=True))
    parts.append(text(565, 108, "Випадкове блукання моментів тактових фронтів у часі", size=10, color=MUTED, anchor="middle"))

    parts.append(line(420, 320, 710, 320, color="#94a3b8", sw=1.2))
    parts.append(text(705, 335, "t", size=11, color=MUTED, anchor="end", italic=True))

    edges_x = [460, 560, 660]
    for idx, ex in enumerate(edges_x):
        parts.append(line(ex - 35, 300, ex, 300, color="#94a3b8", sw=1.2))
        parts.append(line(ex, 300, ex, 200, color="#94a3b8", sw=1.2, dash="3 3"))
        parts.append(line(ex, 200, ex + 35, 200, color="#94a3b8", sw=1.2))
        parts.append(line(ex + 35, 200, ex + 35, 300, color="#94a3b8", sw=1.2))

        parts.append(rect(ex - 12, 195, 24, 110, fill="#fee2e2", stroke="none"))
        parts.append(line(ex - 8, 300, ex - 6, 200, color=POS, sw=1.2))
        parts.append(line(ex + 6, 300, ex + 8, 200, color=POS, sw=1.2))
        parts.append(line(ex - 2, 300, ex, 200, color="#b91c1c", sw=1.5))

    parts.append(arrow(548, 175, 572, 175, color=POS, sw=1.3))
    parts.append(text(560, 165, "±3σ_t (розподіл Гауса)", size=10, color=POS, anchor="middle", bold=True))

    gauss_pts = []
    for i in range(40):
        t_val = (i - 20) / 6.0
        gx = 560 + t_val * 4
        gy = 250 - 35 * math.exp(-t_val*t_val * 0.5)
        gauss_pts.append((gx, gy))
    for i in range(len(gauss_pts) - 1):
        parts.append(line(gauss_pts[i][0], gauss_pts[i][1], gauss_pts[i+1][0], gauss_pts[i+1][1], color=POS, sw=1.4))

    b_tjit, _, _ = textbox(565, 368, "RMS джиттер: σ_t = 100 фс ... 50 пс (типово)", size=10, fill="#fef2f2", stroke=POS, pad=5)
    parts.append(b_tjit)

    return render(os.path.join(OUT, 'phase-noise-to-jitter.svg'), W, H,
                  *parts, title='Зв\'язок фазового шуму та джиттеру')


# ── Фігура 3: Деградація SNR та ENOB від частоти сигналу ───────────────────────
def fig_snr_degradation_curves():
    W, H = 760, 440
    parts = []

    parts.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    parts.append(text(W / 2, 40, "Деградація SNR та ENOB від вхідної частоти f_in при різному джиттері", size=14, color=INK, anchor="middle", bold=True))

    x0, y0, gw, gh = 85, 80, 480, 290
    parts.append(rect(x0, y0, gw, gh, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=4))

    freq_labels = ["10 кГц", "100 кГц", "1 МГц", "10 МГц", "100 МГц", "1 ГГц"]
    for i in range(6):
        gx = x0 + (i / 5.0) * gw
        parts.append(line(gx, y0, gx, y0 + gh, color="#e2e8f0", sw=1))
        parts.append(text(gx, y0 + gh + 18, freq_labels[i], size=10, color=MUTED, anchor="middle"))
    parts.append(text(x0 + gw / 2, y0 + gh + 35, "Вхідна частота сигналу f_in (логарифмічна шкала)", size=11, color=INK, anchor="middle", bold=True))

    snr_vals = [20, 40, 60, 80, 100]
    enob_vals = ["3.0", "6.3", "9.7", "13.0", "16.3"]
    for i, s in enumerate(snr_vals):
        gy = y0 + gh - (i / 4.0) * gh
        parts.append(line(x0, gy, x0 + gw, gy, color="#e2e8f0", sw=1))
        parts.append(text(x0 - 10, gy + 4, "%d дБ" % s, size=10, color=MUTED, anchor="end"))
        parts.append(text(x0 + gw + 10, gy + 4, "%s біт" % enob_vals[i], size=10, color=NEG, anchor="start"))
    parts.append(text(x0 - 50, y0 + gh / 2, "SNR [дБ]", size=11, color=INK, anchor="middle", bold=True))
    parts.append(text(x0 + gw + 55, y0 + gh / 2, "ENOB [біт]", size=11, color=NEG, anchor="middle", bold=True))

    def to_coords(log_f, snr):
        cx = x0 + ((log_f - 4.0) / 5.0) * gw
        cy = y0 + gh - ((snr - 20.0) / 80.0) * gh
        return max(x0, min(x0 + gw, cx)), max(y0, min(y0 + gh, cy))

    q16_y = y0 + gh - ((98.08 - 20.0) / 80.0) * gh
    parts.append(line(x0, q16_y, x0 + gw, q16_y, color="#94a3b8", sw=1.5, dash="4 4"))
    parts.append(text(x0 + 10, q16_y - 6, "Межа 16-біт квантування (98 дБ)", size=9, color="#64748b", anchor="start"))

    q12_y = y0 + gh - ((74.0 - 20.0) / 80.0) * gh
    parts.append(line(x0, q12_y, x0 + gw, q12_y, color="#94a3b8", sw=1.2, dash="4 4"))
    parts.append(text(x0 + 10, q12_y - 6, "Межа 12-біт квантування (74 дБ)", size=9, color="#64748b", anchor="start"))

    jitters = [
        (100e-15, "σ = 100 фс", FIELD),
        (1e-12, "σ = 1 пс", "#0284c7"),
        (10e-12, "σ = 10 пс", "#d97706"),
        (100e-12, "σ = 100 пс", POS),
        (1e-9, "σ = 1 нс (MCU ISR)", "#9333ea")
    ]

    for sig, label, col in jitters:
        pts = []
        for step in range(101):
            log_f = 4.0 + (step / 100.0) * 5.0
            f_in = 10.0 ** log_f
            snr_j = -20.0 * math.log10(2.0 * math.pi * f_in * sig)
            cx, cy = to_coords(log_f, snr_j)
            if cy < y0 + gh:
                pts.append((cx, cy))
        for i in range(len(pts) - 1):
            parts.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=col, sw=2))

    lx, ly = 585, 95
    parts.append(rect(lx, ly, 150, 205, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    parts.append(text(lx + 75, ly + 20, "Джиттер вибірки σ_t", size=11, color=INK, anchor="middle", bold=True))

    for idx, (sig, label, col) in enumerate(jitters):
        item_y = ly + 45 + idx * 28
        parts.append(line(lx + 15, item_y, lx + 45, item_y, color=col, sw=2.5))
        parts.append(text(lx + 55, item_y + 4, label, size=10, color=INK, anchor="start", bold=True))

    b_decay, _, _ = textbox(lx + 75, ly + 185, "-20 дБ/декаду\n(-1 біт / 2× частота)", size=9, fill="#eff6ff", stroke=NEG, pad=4)
    parts.append(b_decay)

    return render(os.path.join(OUT, 'snr-degradation-curves.svg'), W, H,
                  *parts, title='Криві деградації SNR та ENOB')


# ── Фігура 4: Джерела джиттеру в мікроконтролерах ─────────────────────────────
def fig_mcu_sampling_jitter_sources():
    W, H = 760, 420
    parts = []

    parts.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    parts.append(text(W / 2, 40, "Механізми виникнення джиттеру в MCU: Програмне vs Апаратне тактування", size=14, color=INK, anchor="middle", bold=True))

    # Верхня панель: Програмне опитування / Переривання ISR
    parts.append(rect(30, 65, W - 60, 150, fill="#fef2f2", stroke="#fca5a5", sw=1.2, rx=6))
    parts.append(text(45, 88, "1. Програмний запуск або ISR таймера (Джиттер: 50 нс – 10 мкс)", size=12, color=POS, anchor="start", bold=True))
    parts.append(text(45, 106, "Затримка входу в переривання змінюється через очікування Flash, критичні секції CLI/SEI та інші ISR.", size=10, color=MUTED, anchor="start"))

    t_base_y = 150
    parts.append(line(50, t_base_y, 710, t_base_y, color="#94a3b8", sw=1.2))
    parts.append(text(705, t_base_y + 15, "t", size=11, color=MUTED, anchor="end", italic=True))

    ideal_x = [120, 260, 400, 540, 680]
    for idx, ix in enumerate(ideal_x):
        parts.append(line(ix, t_base_y - 25, ix, t_base_y + 15, color="#64748b", sw=1.2, dash="3 3"))
        parts.append(text(ix, t_base_y - 28, "T%d" % idx, size=9, color="#64748b", anchor="middle"))

    real_offsets = [15, 42, 8, 55, 22]
    for idx, ix in enumerate(ideal_x):
        rx = ix + real_offsets[idx]
        parts.append(rect(ix, t_base_y - 12, real_offsets[idx], 24, fill="#fecaca", stroke="none"))
        parts.append(line(rx, t_base_y - 18, rx, t_base_y + 18, color=POS, sw=2))
        parts.append(circle(rx, t_base_y, 3.5, fill=POS, stroke="#ffffff", sw=1))

    parts.append(arrow( ideal_x[1], t_base_y + 25, ideal_x[1] + real_offsets[1], t_base_y + 25, color=POS, sw=1.3))
    parts.append(text(ideal_x[1] + 21, t_base_y + 38, "ISR Latency Jitter (Δt_var)", size=9, color=POS, anchor="middle", bold=True))

    b_sw, _, _ = textbox(620, 185, "Деградація ENOB до 4–8 біт!", size=10, fill="#fee2e2", stroke=POS, pad=5)
    parts.append(b_sw)

    # Нижня панель: Апаратний тригер таймера TRGO + DMA
    parts.append(rect(30, 230, W - 60, 160, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    parts.append(text(45, 253, "2. Апаратний тригер Timer TRGO -> ADC -> DMA (Джиттер: < 50 пс)", size=12, color=FIELD, anchor="start", bold=True))
    parts.append(text(45, 271, "Внутрішній апаратний сигнал запускає Sample&Hold напряму без участі CPU. DMA переносить дані автономно.", size=10, color=MUTED, anchor="start"))

    t_hw_y = 320
    parts.append(line(50, t_hw_y, 710, t_hw_y, color="#94a3b8", sw=1.2))
    parts.append(text(705, t_hw_y + 15, "t", size=11, color=MUTED, anchor="end", italic=True))

    for idx, ix in enumerate(ideal_x):
        parts.append(line(ix, t_hw_y - 25, ix, t_hw_y + 15, color="#64748b", sw=1.2, dash="3 3"))
        parts.append(text(ix, t_hw_y - 28, "T%d" % idx, size=9, color="#64748b", anchor="middle"))
        parts.append(line(ix, t_hw_y - 18, ix, t_hw_y + 18, color=FIELD, sw=2))
        parts.append(circle(ix, t_hw_y, 3.5, fill=FIELD, stroke="#ffffff", sw=1))

    parts.append(arrow(120, t_hw_y + 25, 260, t_hw_y + 25, color=FIELD, sw=1.3))
    parts.append(text(190, t_hw_y + 38, "T_s = строго константа (кварцова точність)", size=9, color=FIELD, anchor="middle", bold=True))

    b_hw, _, _ = textbox(620, 355, "Зберігається повна розрядність АЦП", size=10, fill="#ecfdf5", stroke=FIELD, pad=5)
    parts.append(b_hw)

    return render(os.path.join(OUT, 'mcu-sampling-jitter-sources.svg'), W, H,
                  *parts, title='Джерела джиттеру в мікроконтролерах')


# ── Фігура 5: Придушення джиттеру петлею ФАПЧ (PLL / CDR) ─────────────────────
def fig_pll_jitter_cleaning():
    W, H = 760, 420
    parts = []

    parts.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    parts.append(text(W / 2, 40, "Архітектура очищувача тактового сигналу (PLL Jitter Cleaner)", size=14, color=INK, anchor="middle", bold=True))

    parts.append(text(65, 120, "Засмічений тактовий\nсигнал f_ref (з джиттером)", size=10, color=POS, anchor="middle", bold=True))
    parts.append(arrow(65, 150, 115, 150, color=POS, sw=1.8))

    b_pfd, _, _ = textbox(165, 150, "Фазовий\nдетектор PFD\n+ Насос заряду CP", size=10, fill="#eff6ff", stroke=NEG, pad=6)
    parts.append(b_pfd)

    parts.append(arrow(215, 150, 265, 150, color=INK, sw=1.5))
    parts.append(text(240, 140, "i_cp(t)", size=9, color=MUTED, anchor="middle", italic=True))

    b_lf, _, _ = textbox(325, 150, "Петльовий\nфільтр ФНЧ\n(Смуга f_BW)", size=10, fill="#fffbeb", stroke="#d97706", pad=6)
    parts.append(b_lf)

    parts.append(arrow(385, 150, 435, 150, color=INK, sw=1.5))
    parts.append(text(410, 140, "V_ctrl", size=9, color=MUTED, anchor="middle", italic=True))

    b_vco, _, _ = textbox(505, 150, "Малошумний\nгенератор\nVCXO / VCO", size=10, fill="#eff6ff", stroke=NEG, pad=6)
    parts.append(b_vco)

    parts.append(arrow(575, 150, 680, 150, color=FIELD, sw=2))
    parts.append(circle(610, 150, 3, fill=INK, stroke="none"))
    parts.append(line(610, 150, 610, 240, color=INK, sw=1.3))
    parts.append(arrow(610, 240, 385, 240, color=INK, sw=1.3))

    b_div, _, _ = textbox(335, 240, "Дільник частоти\n/ N", size=10, fill="#f8fafc", stroke="#64748b", pad=6)
    parts.append(b_div)

    parts.append(line(285, 240, 165, 240, color=INK, sw=1.3))
    parts.append(arrow(165, 240, 165, 185, color=INK, sw=1.3))
    parts.append(text(175, 215, "f_fb", size=9, color=MUTED, anchor="start", italic=True))

    parts.append(text(685, 135, "Очищений клок f_out\n(Ультранизький джиттер σ < 100 фс)", size=10, color=FIELD, anchor="start", bold=True))

    parts.append(rect(30, 290, W - 60, 100, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(45, 312, "Компроміс смуги петлі ФАПЧ (Loop Bandwidth f_BW):", size=11, color=INK, anchor="start", bold=True))
    parts.append(text(45, 335, "• f < f_BW (Низькі частоти): Петля відстежує опорний сигнал f_ref (виправляє повільний дрейф частоти).", size=10, color=MUTED, anchor="start"))
    parts.append(text(45, 355, "• f > f_BW (Високі частоти): Петльовий фільтр блокує швидкий фазовий шум f_ref; вихід визначається надчистим VCXO.", size=10, color=MUTED, anchor="start"))
    parts.append(text(45, 375, "• Оптимум f_BW: Обирається на точці перетину спектральних густин фазового шуму вхідного клоку та внутрішнього VCXO.", size=10, color=NEG, anchor="start", bold=True))

    return render(os.path.join(OUT, 'pll-jitter-cleaning.svg'), W, H,
                  *parts, title='Архітектура очищувача тактового сигналу')


if __name__ == '__main__':
    fig_jitter_sampling_error()
    fig_phase_noise_to_jitter()
    fig_snr_degradation_curves()
    fig_mcu_sampling_jitter_sources()
    fig_pll_jitter_cleaning()
    print("All sampling-jitter figures generated successfully.")
