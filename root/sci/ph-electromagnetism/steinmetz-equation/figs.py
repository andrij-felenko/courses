# -*- coding: utf-8 -*-
"""Фігури до теми «Рівняння Штейнмеця».
Запуск: python figs.py -> генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

BORDER = "#cbd5e1"

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

def ellipse(cx, cy, rx, ry, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'


# ── Фігура 1: Поділ втрат у магнітному сердечнику ──────────────────────────────
def fig_steinmetz_hysteresis_loss_separation():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 25, "Поділ втрат у магнітному сердечнику (Loss Separation)", size=16, bold=True, color=INK))

    panel_w = 235
    panel_h = 340
    y_top = 50

    # 1. Гістерезисні втрати
    x1 = 15
    f.append(rect(x1, y_top, panel_w, panel_h, fill="#eff6ff", stroke=BORDER, rx=6))
    f.append(text(x1 + panel_w / 2, y_top + 22, "1. Гістерезисні втрати (P_h)", size=13, bold=True, color="#1d4ed8"))
    
    # Hysteresis loop drawing
    cx1, cy1 = x1 + panel_w / 2, y_top + 170
    f.append(line(cx1 - 90, cy1, cx1 + 90, cy1, color=MUTED, sw=1.0)) # H axis
    f.append(line(cx1, cy1 + 90, cx1, cy1 - 90, color=MUTED, sw=1.0)) # B axis
    f.append(text(cx1 + 95, cy1 + 4, "H", size=12, bold=True, color=MUTED))
    f.append(text(cx1 + 5, cy1 - 95, "B", size=12, bold=True, color=MUTED))

    # B-H Loop path
    loop_d = (f"M {cx1 - 70} {cy1 + 70} "
              f"Q {cx1 - 20} {cy1 - 20} {cx1 + 70} {cy1 - 70} "
              f"Q {cx1 + 20} {cy1 + 20} {cx1 - 70} {cy1 + 70}")
    f.append(path_svg(loop_d, fill="rgba(29, 78, 216, 0.15)", stroke="#1d4ed8", sw=2.0))
    
    f.append(text(cx1, cy1 + 10, "Площа = E_h", size=11, bold=True, color="#1d4ed8"))
    
    # Formula box inside panel 1
    f.append(rect(x1 + 10, y_top + 265, panel_w - 20, 60, fill="#ffffff", stroke="#93c5fd", rx=4))
    f.append(text(x1 + panel_w / 2, y_top + 285, "P_h = k_h · f · B_m^β", size=12, bold=True, color=INK))
    f.append(text(x1 + panel_w / 2, y_top + 310, "Зачіпляння доменних стінок", size=10, italic=True, color=MUTED))

    # 2. Вихрові струми
    x2 = 272
    f.append(rect(x2, y_top, panel_w, panel_h, fill="#f0fdf4", stroke=BORDER, rx=6))
    f.append(text(x2 + panel_w / 2, y_top + 22, "2. Вихрові струми (P_e)", size=13, bold=True, color="#15803d"))
    
    cx2, cy2 = x2 + panel_w / 2, y_top + 170
    # Core cross section laminations
    f.append(rect(cx2 - 75, cy2 - 75, 150, 150, fill="#ffffff", stroke="#15803d", sw=1.5))
    for i in range(1, 5):
        lx = cx2 - 75 + i * 30
        f.append(line(lx, cy2 - 75, lx, cy2 + 75, color="#86efac", sw=1.2))
    
    # Flux arrow
    f.append(circle(cx2, cy2, 12, fill="#dcfce7", stroke="#15803d", sw=1.5))
    f.append(circle(cx2, cy2, 3, fill="#15803d", stroke="#15803d"))
    f.append(text(cx2 + 20, cy2 - 15, "dB/dt", size=11, bold=True, color="#15803d"))
    
    # Eddy current loops
    for lx_c in [cx2 - 60, cx2 - 30, cx2, cx2 + 30, cx2 + 60]:
        f.append(ellipse(lx_c, cy2, 10, 35, fill="none", stroke="#22c55e", sw=1.2, dash="3,2"))

    f.append(text(cx2, cy2 + 92, "Шихтовка / Ферит (d)", size=11, color=MUTED))

    # Formula box inside panel 2
    f.append(rect(x2 + 10, y_top + 265, panel_w - 20, 60, fill="#ffffff", stroke="#86efac", rx=4))
    f.append(text(x2 + panel_w / 2, y_top + 285, "P_e = k_e · f² · B_m²", size=12, bold=True, color=INK))
    f.append(text(x2 + panel_w / 2, y_top + 310, "Нагрів Джоуля від індукції", size=10, italic=True, color=MUTED))

    # 3. Розподіл по частоті (Графік)
    x3 = 530
    f.append(rect(x3, y_top, panel_w, panel_h, fill="#fff7ed", stroke=BORDER, rx=6))
    f.append(text(x3 + panel_w / 2, y_top + 22, "3. Розподіл P_v / f від f", size=13, bold=True, color="#c2410c"))

    cx3, cy3 = x3 + 35, y_top + 230
    # Axes
    f.append(line(cx3, cy3, cx3 + 175, cy3, color=INK, sw=1.5)) # f axis
    f.append(line(cx3, cy3, cx3, cy3 - 150, color=INK, sw=1.5)) # P/f axis
    f.append(text(cx3 + 180, cy3 + 4, "f", size=12, bold=True, color=INK))
    f.append(text(cx3 - 5, cy3 - 155, "P_v/f", size=12, bold=True, color=INK))

    # Lines on graph
    # 1. Hysteresis baseline (horizontal)
    f.append(line(cx3, cy3 - 40, cx3 + 160, cy3 - 40, color="#1d4ed8", sw=1.8, dash="4,3"))
    f.append(text(cx3 + 80, cy3 - 46, "P_h / f = const", size=10, bold=True, color="#1d4ed8"))

    # 2. Total loss curve (curved up due to f^2 eddy and f^1.5 excess)
    total_d = f"M {cx3} {cy3 - 40} Q {cx3 + 80} {cy3 - 70} {cx3 + 160} {cy3 - 140}"
    f.append(path_svg(total_d, fill="none", stroke="#c2410c", sw=2.2))
    
    # Fill between lines
    f.append(text(cx3 + 115, cy3 - 95, "+ P_e + P_exc", size=10, bold=True, color="#c2410c"))

    # Formula box inside panel 3
    f.append(rect(x3 + 10, y_top + 265, panel_w - 20, 60, fill="#ffffff", stroke="#ffedd5", rx=4))
    f.append(text(x3 + panel_w / 2, y_top + 285, "P_tot = P_h + P_e + P_exc", size=12, bold=True, color=INK))
    f.append(text(x3 + panel_w / 2, y_top + 310, "Модель Бертотті (Bertotti)", size=10, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, "steinmetz-hysteresis-loss-separation.svg"), W, H, *f)

# ── Фігура 2: Порівняння OSE та iSE для несплавних сигналів ─────────────────────
def fig_steinmetz_waveform_ise_comparison():
    W, H = 780, 440
    f = []

    f.append(text(W / 2, 25, "Порівняння класичного Штейнмеця (OSE) та розширення (iSE)", size=16, bold=True, color=INK))

    panel_w = 750
    panel_h = 180

    # Top Panel: Sinusoidal (OSE works)
    y1 = 50
    f.append(rect(15, y1, panel_w, panel_h, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(30, y1 + 22, "А. Синусоїдальний сигнал — Класичне рівняння Штейнмеця (OSE)", size=13, bold=True, color="#0f172a"))

    # Sinusoidal B(t) waveform
    ox1, oy1 = 50, y1 + 100
    f.append(line(ox1, oy1, ox1 + 320, oy1, color=MUTED, sw=1.0))
    f.append(line(ox1, oy1 - 50, ox1, oy1 + 50, color=MUTED, sw=1.0))
    
    sin_pts = []
    for x in range(300):
        t = x / 300.0 * 2 * math.pi
        y_val = oy1 - 40 * math.sin(t)
        sin_pts.append(f"{ox1 + x:.1f},{y_val:.1f}")
    f.append(f'<polyline points="{" ".join(sin_pts)}" fill="none" stroke="#2563eb" stroke-width="2.0"/>')
    f.append(text(ox1 + 330, oy1 + 4, "t", size=11, color=MUTED))
    f.append(text(ox1 + 5, oy1 - 45, "B(t)", size=11, bold=True, color="#2563eb"))

    # Loss power p(t)
    ox1_p, oy1_p = 420, y1 + 100
    f.append(line(ox1_p, oy1_p, ox1_p + 300, oy1_p, color=MUTED, sw=1.0))
    f.append(line(ox1_p, oy1_p - 50, ox1_p, oy1_p + 50, color=MUTED, sw=1.0))

    p_pts = []
    for x in range(280):
        t = x / 280.0 * 2 * math.pi
        # loss proportional to |cos(t)|^alpha
        loss_val = math.pow(abs(math.cos(t)), 1.5) * 35
        y_val = oy1_p - loss_val
        p_pts.append(f"{ox1_p + x:.1f},{y_val:.1f}")
    f.append(f'<polyline points="{" ".join(p_pts)}" fill="none" stroke="#dc2626" stroke-width="1.8"/>')
    f.append(text(ox1_p + 310, oy1_p + 4, "t", size=11, color=MUTED))
    f.append(text(ox1_p + 5, oy1_p - 45, "p(t) втрати", size=11, bold=True, color="#dc2626"))

    # Formula box for OSE
    f.append(rect(450, y1 + 125, 290, 45, fill="#eff6ff", stroke="#bfdbfe", rx=4))
    f.append(text(595, y1 + 152, "P_v = k · f^α · B_m^β", size=13, bold=True, color="#1e40af"))

    # Bottom Panel: PWM / Triangular (iSE needed)
    y2 = 245
    f.append(rect(15, y2, panel_w, panel_h, fill="#fff7ed", stroke=BORDER, rx=6))
    f.append(text(30, y2 + 22, "Б. Прямокутний / PWM сигнал — Покращене рівняння Штейнмеця (iSE)", size=13, bold=True, color="#7c2d12"))

    # Triangular B(t) waveform with zero-voltage interval
    ox2, oy2 = 50, y2 + 100
    f.append(line(ox2, oy2, ox2 + 320, oy2, color=MUTED, sw=1.0))
    f.append(line(ox2, oy2 - 50, ox2, oy2 + 50, color=MUTED, sw=1.0))

    tri_d = (f"M {ox2} {oy2 + 40} "
             f"L {ox2 + 60} {oy2 - 40} "   # Fast rise
             f"L {ox2 + 120} {oy2 - 40} "  # Dead time (flat)
             f"L {ox2 + 180} {oy2 + 40} "  # Fall
             f"L {ox2 + 240} {oy2 + 40} "  # Dead time (flat)
             f"L {ox2 + 300} {oy2 - 40}")  # Next rise
    f.append(path_svg(tri_d, fill="none", stroke="#d97706", sw=2.0))
    f.append(text(ox2 + 330, oy2 + 4, "t", size=11, color=MUTED))
    f.append(text(ox2 + 5, oy2 - 45, "B(t) PWM", size=11, bold=True, color="#d97706"))

    # Instantaneous loss spikes p(t) during slopes
    ox2_p, oy2_p = 420, y2 + 100
    f.append(line(ox2_p, oy2_p, ox2_p + 300, oy2_p, color=MUTED, sw=1.0))
    f.append(line(ox2_p, oy2_p - 50, ox2_p, oy2_p + 50, color=MUTED, sw=1.0))

    spike_d = (f"M {ox2_p} {oy2_p} "
               f"L {ox2_p + 10} {oy2_p - 42} L {ox2_p + 55} {oy2_p - 42} L {ox2_p + 60} {oy2_p} " # Spike 1
               f"L {ox2_p + 120} {oy2_p} "                                                        # Zero loss during flat
               f"L {ox2_p + 125} {oy2_p - 42} L {ox2_p + 175} {oy2_p - 42} L {ox2_p + 180} {oy2_p} " # Spike 2
               f"L {ox2_p + 240} {oy2_p} "                                                        # Zero loss
               f"L {ox2_p + 245} {oy2_p - 42} L {ox2_p + 290} {oy2_p - 42}")                       # Spike 3
    f.append(path_svg(spike_d, fill="none", stroke="#b91c1c", sw=1.8))
    f.append(text(ox2_p + 310, oy2_p + 4, "t", size=11, color=MUTED))
    f.append(text(ox2_p + 5, oy2_p - 45, "p(t) сплески", size=11, bold=True, color="#b91c1c"))

    # Formula box for iSE
    f.append(rect(430, y2 + 125, 310, 45, fill="#fff1f2", stroke="#fecdd3", rx=4))
    f.append(text(585, y2 + 152, "P_v = (1/T) ∫ k_i |dB/dt|^α |ΔB|^(β-α) dt", size=12, bold=True, color="#9f1239"))

    render(os.path.join(IMG_DIR, "steinmetz-waveform-ise-comparison.svg"), W, H, *f)

if __name__ == "__main__":
    fig_steinmetz_hysteresis_loss_separation()
    fig_steinmetz_waveform_ise_comparison()
    print("Figures generated successfully in ./img/")
