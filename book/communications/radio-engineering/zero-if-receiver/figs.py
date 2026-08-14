# -*- coding: utf-8 -*-
import sys
import os

# '..' 4 levels up to scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Domain colors
RF    = "#8e44ad"   # Radio frequency (purple)
LO    = FIELD       # Local oscillator (green)
BB    = POS         # Baseband / IF signal (red/coral)
MUTED = "#6b7280"   # Secondary elements (gray)
FILTER_COL = NEG    # Filter elements (blue)


def tri(cx, base_y, half_w, h, color, sw=2.4, fill=None):
    """Triangular spectrum shape centered at cx, base at base_y."""
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (cx - half_w, base_y, cx, base_y - h, cx + half_w, base_y)
    f = fill if fill else "none"
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (pts, f, color, sw))


def fig_zero_if_architecture():
    W, H = 760, 400
    p = []

    # Title / Antenna
    p.append(line(40, 200, 70, 200, color=INK, sw=2.0))
    p.append('<polygon points="40,200 30,170 50,170" fill="%s" stroke="%s" stroke-width="2.0"/>' % (FILL, INK))
    p.append(line(40, 170, 40, 200, color=INK, sw=2.0))
    p.append(text(40, 160, "Antenna", size=12, color=INK, bold=True))

    # BPF (Band-pass filter)
    b, bw, bh = textbox(70, 180, "RF BPF", size=12, color=INK, bold=True, min_w=60, fill="#f8fafc")
    p.append(b)

    p.append(line(130, 200, 160, 200, color=INK, sw=2.0))

    # LNA
    p.append('<polygon points="160,175 160,225 210,200" fill="#f3e8fb" stroke="%s" stroke-width="2.0"/>' % RF)
    p.append(text(175, 204, "LNA", size=12, color=RF, bold=True))

    p.append(line(210, 200, 250, 200, color=INK, sw=2.0))
    # Node splitter
    p.append('<circle cx="250" cy="200" r="4" fill="%s"/>' % INK)
    p.append(line(250, 200, 250, 110, color=INK, sw=2.0))
    p.append(line(250, 200, 250, 290, color=INK, sw=2.0))
    p.append(line(250, 110, 290, 110, color=INK, sw=2.0))
    p.append(line(250, 290, 290, 290, color=INK, sw=2.0))

    # I-Mixer (top)
    p.append('<circle cx="310" cy="110" r="20" fill="#fdf2f2" stroke="%s" stroke-width="2.0"/>' % POS)
    p.append(line(296, 96, 324, 124, color=POS, sw=2.0))
    p.append(line(296, 124, 324, 96, color=POS, sw=2.0))
    p.append(text(310, 82, "Mixer I", size=13, color=POS, bold=True))

    # Q-Mixer (bottom)
    p.append('<circle cx="310" cy="290" r="20" fill="#fdf2f2" stroke="%s" stroke-width="2.0"/>' % POS)
    p.append(line(296, 276, 324, 304, color=POS, sw=2.0))
    p.append(line(296, 304, 324, 276, color=POS, sw=2.0))
    p.append(text(310, 325, "Mixer Q", size=13, color=POS, bold=True))

    # LO & Phase Shifter
    b_lo, _, _ = textbox(280, 190, "Synthesizer\nf_LO = f_RF", size=11, color=FIELD, bold=True, min_w=90, fill="#eefaf1")
    p.append(b_lo)

    # LO paths
    p.append(line(370, 200, 400, 200, color=FIELD, sw=2.0))
    b_90, _, _ = textbox(400, 185, "Phase\n0° / 90°", size=11, color=FIELD, bold=True, min_w=60, fill="#eefaf1")
    p.append(b_90)

    p.append(line(430, 175, 430, 140, color=FIELD, sw=2.0))
    p.append(line(430, 140, 310, 140, color=FIELD, sw=2.0))
    p.append(arrow(310, 140, 310, 130, color=FIELD, sw=2.0))
    p.append(text(370, 135, "cos(ω_LO t)", size=11, color=FIELD, bold=True))

    p.append(line(430, 225, 430, 260, color=FIELD, sw=2.0))
    p.append(line(430, 260, 310, 260, color=FIELD, sw=2.0))
    p.append(arrow(310, 260, 310, 270, color=FIELD, sw=2.0))
    p.append(text(370, 272, "−sin(ω_LO t)", size=11, color=FIELD, bold=True))

    # I-channel path (top)
    p.append(line(330, 110, 370, 110, color=INK, sw=2.0))
    b_lpf_i, _, _ = textbox(370, 95, "LPF & DCOC", size=11, color=FILTER_COL, bold=True, min_w=75, fill="#eff6ff")
    p.append(b_lpf_i)

    p.append(line(445, 110, 475, 110, color=INK, sw=2.0))
    b_pga_i, _, _ = textbox(475, 95, "PGA I", size=11, color=INK, bold=True, min_w=50, fill=FILL)
    p.append(b_pga_i)

    p.append(line(525, 110, 555, 110, color=INK, sw=2.0))
    b_adc_i, _, _ = textbox(555, 95, "ADC I", size=11, color=POS, bold=True, min_w=50, fill="#fdf2f2")
    p.append(b_adc_i)

    p.append(arrow(605, 110, 650, 110, color=INK, sw=2.0))
    p.append(text(628, 100, "I[n]", size=12, color=POS, bold=True))

    # Q-channel path (bottom)
    p.append(line(330, 290, 370, 290, color=INK, sw=2.0))
    b_lpf_q, _, _ = textbox(370, 275, "LPF & DCOC", size=11, color=FILTER_COL, bold=True, min_w=75, fill="#eff6ff")
    p.append(b_lpf_q)

    p.append(line(445, 290, 475, 290, color=INK, sw=2.0))
    b_pga_q, _, _ = textbox(475, 275, "PGA Q", size=11, color=INK, bold=True, min_w=50, fill=FILL)
    p.append(b_pga_q)

    p.append(line(525, 290, 555, 290, color=INK, sw=2.0))
    b_adc_q, _, _ = textbox(555, 275, "ADC Q", size=11, color=POS, bold=True, min_w=50, fill="#fdf2f2")
    p.append(b_adc_q)

    p.append(arrow(605, 290, 650, 290, color=INK, sw=2.0))
    p.append(text(628, 280, "Q[n]", size=12, color=POS, bold=True))

    # DSP block on right
    p.append(rect(650, 80, 95, 240, fill="#f8fafc", stroke=INK, sw=1.5, rx=6))
    p.append(mtext(697, 195, "Digital Signal Processor\n(DSP / Baseband IQ)", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "zero-if-architecture.svg"), W, H, *p,
           title="Архітектура приймача прямого перетворення (Zero-IF)")


def fig_dc_offset_flicker():
    W, H = 720, 340
    p = []

    ax, ay = 80, 250
    axw = 580

    p.append(line(ax, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(arrow(ax + axw - 22, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(text(ax + axw + 10, ay + 5, "f", size=15, color=INK, italic=True, anchor="start"))

    cx = ax + axw / 2
    p.append(line(cx, ay - 200, cx, ay + 20, color=MUTED, sw=1.0, dash="4 4"))
    p.append(text(cx, ay + 36, "0 Hz (DC / f_LO)", size=13, color=INK, bold=True))

    p.append(tri(cx, ay, 140, 110, POS, fill="#fdf2f2", sw=2.2))
    p.append(text(cx + 80, ay - 70, "Корисний Baseband\nсигнал", size=12, color=POS, bold=True, anchor="start"))

    path_left = "M %.1f,%.1f Q %.1f,%.1f %.1f,%.1f" % (ax + 50, ay - 15, cx - 30, ay - 25, cx - 4, ay - 170)
    path_right = "M %.1f,%.1f Q %.1f,%.1f %.1f,%.1f" % (cx + 4, ay - 170, cx + 30, ay - 25, ax + axw - 50, ay - 15)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path_left, NEG))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path_right, NEG))
    p.append(text(cx - 140, ay - 150, "Флікер-шум 1/f\n(транзистори)", size=12, color=NEG, bold=True, anchor="end"))

    p.append(arrow(cx, ay, cx, ay - 195, color=FIELD, sw=3.0))
    p.append(text(cx + 12, ay - 180, "Паразитний пік DC\n(LO self-mixing)", size=12, color=FIELD, bold=True, anchor="start"))

    p.append(rect(cx - 15, ay - 115, 30, 115, fill="#ffffff", stroke=MUTED, sw=1.2, rx=2))
    p.append(text(cx, ay - 125, "Зріз AC / DCOC", size=10, color=MUTED))

    render(os.path.join(OUT, "dc-offset-flicker.svg"), W, H, *p,
           title="Спектральні вади Zero-IF: постійна складова та 1/f шум")


def fig_low_if_architecture():
    W, H = 760, 380
    p = []

    p.append(line(40, 130, 70, 130, color=INK, sw=2.0))
    p.append('<polygon points="40,130 30,100 50,100" fill="%s" stroke="%s" stroke-width="2.0"/>' % (FILL, INK))
    p.append(text(40, 90, "Antenna", size=11, color=INK, bold=True))

    p.append('<polygon points="70,105 70,155 120,130" fill="#f3e8fb" stroke="%s" stroke-width="2.0"/>' % RF)
    p.append(text(85, 134, "LNA", size=11, color=RF, bold=True))

    p.append(line(120, 130, 160, 130, color=INK, sw=2.0))
    p.append('<circle cx="160" cy="130" r="3" fill="%s"/>' % INK)

    p.append(line(160, 130, 160, 70, color=INK, sw=2.0))
    p.append(line(160, 130, 160, 190, color=INK, sw=2.0))
    p.append(line(160, 70, 190, 70, color=INK, sw=2.0))
    p.append(line(160, 190, 190, 190, color=INK, sw=2.0))

    p.append('<circle cx="210" cy="70" r="16" fill="#fdf2f2" stroke="%s" stroke-width="2.0"/>' % POS)
    p.append(line(199, 59, 221, 81, color=POS, sw=2.0))
    p.append(line(199, 81, 221, 59, color=POS, sw=2.0))

    p.append('<circle cx="210" cy="190" r="16" fill="#fdf2f2" stroke="%s" stroke-width="2.0"/>' % POS)
    p.append(line(199, 179, 221, 201, color=POS, sw=2.0))
    p.append(line(199, 201, 221, 179, color=POS, sw=2.0))

    b_lo, _, _ = textbox(165, 120, "Synthesizer\nf_LO = f_RF − f_IF", size=10, color=FIELD, bold=True, min_w=90, fill="#eefaf1")
    p.append(b_lo)

    p.append(line(226, 70, 270, 70, color=INK, sw=2.0))
    p.append(line(226, 190, 270, 190, color=INK, sw=2.0))

    p.append(rect(270, 50, 180, 160, fill="#eff6ff", stroke=FILTER_COL, sw=1.5, rx=6))
    p.append(mtext(360, 125, "Complex Polyphase Filter\n(Приглушення дзеркалки)", size=11, color=FILTER_COL, bold=True))

    p.append(line(450, 70, 480, 70, color=INK, sw=2.0))
    p.append(line(450, 190, 480, 190, color=INK, sw=2.0))

    p.append(rect(480, 50, 100, 160, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(mtext(530, 125, "Dual ADC &\nDSP Polyphase", size=11, color=POS, bold=True))

    p.append(arrow(580, 130, 710, 130, color=INK, sw=2.0))
    p.append(text(645, 120, "Чистий Baseband", size=11, color=POS, bold=True))

    ax, ay = 60, 330
    axw = 640
    p.append(line(ax, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(arrow(ax + axw - 22, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(text(ax + axw + 8, ay + 5, "f", size=14, color=INK, italic=True, anchor="start"))

    cx = ax + 200
    p.append(line(cx, ay - 90, cx, ay + 15, color=MUTED, sw=1.0, dash="3 3"))
    p.append(text(cx, ay + 26, "0 Hz (DC)", size=12, color=INK, bold=True))

    f_if_x = cx + 180
    p.append(tri(f_if_x, ay, 30, 60, POS, fill="#fdf2f2"))
    p.append(text(f_if_x, ay + 26, "+f_IF (Корисний)", size=12, color=POS, bold=True))

    f_img_x = cx - 140
    p.append(tri(f_img_x, ay, 30, 20, MUTED, fill="#f1f5f9", sw=1.5))
    p.append(text(f_img_x, ay + 26, "−f_IF (Пригнічена дзеркалка)", size=11, color=MUTED))

    path_flicker = "M %.1f,%.1f Q %.1f,%.1f %.1f,%.1f" % (cx - 60, ay - 10, cx, ay - 75, cx + 60, ay - 10)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4 3"/>' % (path_flicker, NEG))
    p.append(text(cx, ay - 80, "1/f шум лишився на DC", size=11, color=NEG))

    render(os.path.join(OUT, "low-if-architecture.svg"), W, H, *p,
           title="Архітектура низькочастотної проміжної частоти (Low-IF)")


def fig_iq_imbalance_constellation():
    W, H = 720, 320
    p = []

    p.append(rect(40, 30, 310, 250, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=6))
    p.append(mtext(195, 55, "Ідеальний I/Q баланс (Phase = 90°, Gain = 1.0)", size=12, color=FIELD, bold=True))

    cx1, cy1 = 195, 160
    p.append(line(cx1 - 80, cy1, cx1 + 80, cy1, color=MUTED, sw=1.2))
    p.append(line(cx1, cy1 - 80, cx1, cy1 + 80, color=MUTED, sw=1.2))
    p.append(text(cx1 + 85, cy1 + 4, "I", size=12, color=INK, bold=True))
    p.append(text(cx1 + 4, cy1 - 85, "Q", size=12, color=INK, bold=True))

    r = 50
    pts_ideal = [(cx1 - r, cy1 - r), (cx1 + r, cy1 - r), (cx1 - r, cy1 + r), (cx1 + r, cy1 + r)]
    for px, py in pts_ideal:
        p.append('<circle cx="%.1f" cy="%.1f" r="6" fill="%s" stroke="%s" stroke-width="1.8"/>' % (px, py, FIELD, INK))
    p.append(text(cx1, cy1 + 105, "Високе приглушення дзеркалки (IRR > 60 dB)", size=11, color=FIELD, bold=True))

    p.append(rect(370, 30, 310, 250, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(mtext(525, 55, "I/Q Дисбаланс (Phase Error θ, Gain Error ε)", size=12, color=POS, bold=True))

    cx2, cy2 = 525, 160
    p.append(line(cx2 - 80, cy2, cx2 + 80, cy2, color=MUTED, sw=1.2))
    p.append(line(cx2, cy2 - 80, cx2, cy2 + 80, color=MUTED, sw=1.2))
    p.append(text(cx2 + 85, cy2 + 4, "I", size=12, color=INK, bold=True))
    p.append(text(cx2 + 4, cy2 - 85, "Q", size=12, color=INK, bold=True))

    pts_dist = [(cx2 - r * 1.15 + 12, cy2 - r * 0.9),
                (cx2 + r * 1.15 + 12, cy2 - r * 0.9),
                (cx2 - r * 1.15 - 12, cy2 + r * 0.9),
                (cx2 + r * 1.15 - 12, cy2 + r * 0.9)]
    for px, py in pts_dist:
        p.append('<circle cx="%.1f" cy="%.1f" r="6" fill="%s" stroke="%s" stroke-width="1.8"/>' % (px, py, POS, INK))

    p.append(text(cx2, cy2 + 105, "Низьке приглушення дзеркалки (IRR ≈ 30 dB)", size=11, color=POS, bold=True))

    render(os.path.join(OUT, "iq-imbalance-constellation.svg"), W, H, *p,
           title="Вплив I/Q дисбалансу на сигнальне сузір'я та дзеркальне приглушення")


if __name__ == "__main__":
    fig_zero_if_architecture()
    fig_dc_offset_flicker()
    fig_low_if_architecture()
    fig_iq_imbalance_constellation()
    print("Zero-IF figures generated successfully.")
