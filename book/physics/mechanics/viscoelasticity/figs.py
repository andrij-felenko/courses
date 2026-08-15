# -*- coding: utf-8 -*-
"""Generator for SVG figures in book/physics/mechanics/viscoelasticity."""

import os
import sys
import math

# Add scripts/ directory to Python path (4 levels up from book/physics/mechanics/viscoelasticity)
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from svgkit import (
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT,
    text, mtext, rect, line, arrow, circle, textbox, esc, text_width
)

def ensure_img_dir(base_dir):
    img_dir = os.path.join(base_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    return img_dir

def save_svg(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def make_svg_doc(width, height, content):
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">\n'
        '<defs>\n'
        '  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        '    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#333333" />\n'
        '  </marker>\n'
        '  <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        f'    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{NEG}" />\n'
        '  </marker>\n'
        '  <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        f'    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="{POS}" />\n'
        '  </marker>\n'
        '</defs>\n'
        f'<rect width="100%" height="100%" fill="{BG}" />\n'
        f'{content}\n'
        '</svg>\n'
    )

# ── Fig 1: Viscoelastic Responses (Elastic vs Viscous vs Viscoelastic) ─────────
def fig1_viscoelastic_responses(out_dir):
    w, h = 820, 360
    out = []

    # Title card / Legend boxes
    tb1, _, _ = textbox(150, 40, "Пружне тіло (Гук)\nМиттєва деформація, 0 втрат", size=13, fill="#e8f4f8", stroke=NEG)
    tb2, _, _ = textbox(410, 40, "В'язка рідина (Ньютон)\nТечія з часом, 100% дисипація", size=13, fill="#fcf3cf", stroke=POS)
    tb3, _, _ = textbox(670, 40, "В'язкопружне тіло\nЧасткове відновлення + релаксація", size=13, fill="#eafaf1", stroke=FIELD)
    out.extend([tb1, tb2, tb3])

    # Panel 1: Elastic (Hooke)
    out.append(rect(40, 90, 220, 240, fill="#fdfdfd", stroke="#dddddd", rx=4))
    out.append(line(70, 290, 240, 290, color=LINE, sw=1.5)) # t-axis
    out.append(line(70, 290, 70, 110, color=LINE, sw=1.5))  # strain-axis
    out.append(text(245, 294, "t", size=13, color=INK, bold=True))
    out.append(text(65, 105, "ε(t)", size=13, color=INK, bold=True))
    out.append(text(150, 115, "Пружний відгук", size=13, color=NEG, bold=True))
    
    # Step stress input (dashed) and step strain response (solid)
    out.append(line(70, 260, 100, 260, color=MUTED, sw=1.2, dash="3,3"))
    out.append(line(100, 260, 100, 160, color=MUTED, sw=1.2, dash="3,3"))
    out.append(line(100, 160, 180, 160, color=MUTED, sw=1.2, dash="3,3"))
    out.append(line(180, 160, 180, 260, color=MUTED, sw=1.2, dash="3,3"))
    out.append(line(180, 260, 230, 260, color=MUTED, sw=1.2, dash="3,3"))

    out.append(line(70, 260, 100, 260, color=NEG, sw=2.5))
    out.append(line(100, 260, 100, 160, color=NEG, sw=2.5))
    out.append(line(100, 160, 180, 160, color=NEG, sw=2.5))
    out.append(line(180, 160, 180, 260, color=NEG, sw=2.5))
    out.append(line(180, 260, 230, 260, color=NEG, sw=2.5))
    out.append(text(140, 150, "ε = σ₀ / E", size=12, color=NEG, bold=True))
    out.append(text(140, 315, "Миттєве синфазне\nповернення", size=11, color=MUTED))

    # Panel 2: Viscous (Newton)
    out.append(rect(300, 90, 220, 240, fill="#fdfdfd", stroke="#dddddd", rx=4))
    out.append(line(330, 290, 500, 290, color=LINE, sw=1.5))
    out.append(line(330, 290, 330, 110, color=LINE, sw=1.5))
    out.append(text(505, 294, "t", size=13, color=INK, bold=True))
    out.append(text(325, 105, "ε(t)", size=13, color=INK, bold=True))
    out.append(text(410, 115, "В'язкий відгук", size=13, color=POS, bold=True))

    out.append(line(330, 260, 360, 260, color=POS, sw=2.5))
    out.append(line(360, 260, 440, 150, color=POS, sw=2.5)) # linear creep
    out.append(line(440, 150, 490, 150, color=POS, sw=2.5)) # residual strain
    out.append(text(380, 175, "dε/dt = σ₀ / η", size=12, color=POS, bold=True))
    out.append(text(410, 315, "Незворотна залишкова\nдеформація", size=11, color=MUTED))

    # Panel 3: Viscoelastic
    out.append(rect(560, 90, 220, 240, fill="#fdfdfd", stroke="#dddddd", rx=4))
    out.append(line(590, 290, 760, 290, color=LINE, sw=1.5))
    out.append(line(590, 290, 590, 110, color=LINE, sw=1.5))
    out.append(text(765, 294, "t", size=13, color=INK, bold=True))
    out.append(text(585, 105, "ε(t)", size=13, color=INK, bold=True))
    out.append(text(670, 115, "В'язкопружність", size=13, color=FIELD, bold=True))

    path_d = "M 590 260 L 620 260 L 620 220 C 630 180, 660 160, 700 155 L 700 195 C 710 230, 730 250, 750 255 L 755 255"
    out.append(f'<path d="{path_d}" fill="none" stroke="{FIELD}" stroke-width="2.5" />')
    out.append(line(620, 260, 620, 220, color=FIELD, sw=1.5, dash="2,2"))
    out.append(text(645, 175, "Повзучість", size=11, color=FIELD, bold=True))
    out.append(text(725, 275, "Відновлення", size=11, color=FIELD, bold=True))
    out.append(text(670, 315, "Часова затримка та\nгістерезис", size=11, color=MUTED))

    save_svg(os.path.join(out_dir, "viscoelastic-responses.svg"), make_svg_doc(w, h, "".join(out)))

# ── Fig 2: Mechanical Rheological Models (Maxwell, Kelvin-Voigt, Zener SLS) ──
def fig2_mechanical_models(out_dir):
    w, h = 820, 380
    out = []

    out.append(text(410, 25, "Механічні реологічні моделі (пружини та демпфери)", size=16, color=INK, bold=True))

    def spring(x1, y1, x2, y2, turns=5, width=16, color=NEG):
        dx = x2 - x1
        path = [f"M {x1} {y1}"]
        path.append(f"L {x1 + dx*0.1} {y1}")
        step = (dx * 0.8) / turns
        for i in range(turns):
            px = x1 + dx*0.1 + step*(i + 0.25)
            py = y1 - width/2
            path.append(f"L {px} {py}")
            px2 = x1 + dx*0.1 + step*(i + 0.75)
            py2 = y1 + width/2
            path.append(f"L {px2} {py2}")
        path.append(f"L {x1 + dx*0.9} {y1}")
        path.append(f"L {x2} {y2}")
        return f'<path d="{" ".join(path)}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round"/>'

    def dashpot(x1, y1, x2, y2, width=20, color=POS):
        dx = x2 - x1
        cx1 = x1 + dx * 0.2
        cx2 = x1 + dx * 0.7
        res = []
        res.append(line(x1, y1, cx1, y1, color=color, sw=2))
        res.append(line(cx1, y1 - width/2, cx2, y1 - width/2, color=color, sw=2))
        res.append(line(cx1, y1 + width/2, cx2, y1 + width/2, color=color, sw=2))
        res.append(line(cx1, y1 - width/2, cx1, y1 + width/2, color=color, sw=2))
        px = x1 + dx * 0.45
        res.append(line(px, y1 - width/2 + 2, px, y1 + width/2 - 2, color=color, sw=2.5))
        res.append(line(px, y1, x2, y1, color=color, sw=2))
        return "".join(res)

    # Model 1: Maxwell
    out.append(rect(30, 50, 235, 300, fill="#fafafa", stroke="#cccccc", rx=6))
    out.append(text(147, 75, "Модель Максвелла", size=14, color=INK, bold=True))
    out.append(text(147, 95, "(послідовне з'єднання)", size=12, color=MUTED))
    out.append(line(50, 160, 70, 160, color=LINE, sw=2))
    out.append(spring(70, 160, 140, 160, color=NEG))
    out.append(dashpot(140, 160, 210, 160, color=POS))
    out.append(line(210, 160, 230, 160, color=LINE, sw=2))
    out.append(text(105, 135, "E", size=14, color=NEG, bold=True))
    out.append(text(175, 135, "η", size=14, color=POS, bold=True))
    
    tb_m, _, _ = textbox(147, 240, "dε/dt = (1/E) dσ/dt + σ/η\n\n• Чудова релаксація σ(t)\n• Повзучість не обмежена", size=11, fill="#ffffff", stroke="#dddddd")
    out.append(tb_m)

    # Model 2: Kelvin-Voigt
    out.append(rect(292, 50, 235, 300, fill="#fafafa", stroke="#cccccc", rx=6))
    out.append(text(410, 75, "Модель Кельвіна-Фойгта", size=14, color=INK, bold=True))
    out.append(text(410, 95, "(паралельне з'єднання)", size=12, color=MUTED))
    
    out.append(line(312, 160, 332, 160, color=LINE, sw=2))
    out.append(line(332, 125, 332, 195, color=LINE, sw=2))
    out.append(spring(332, 125, 487, 125, color=NEG))
    out.append(dashpot(332, 195, 487, 195, color=POS))
    out.append(line(487, 125, 487, 195, color=LINE, sw=2))
    out.append(line(487, 160, 507, 160, color=LINE, sw=2))
    out.append(text(410, 105, "E", size=14, color=NEG, bold=True))
    out.append(text(410, 220, "η", size=14, color=POS, bold=True))

    tb_kv, _, _ = textbox(410, 255, "σ = E·ε + η·(dε/dt)\n\n• Чудова повзучість ε(t)\n• Немає миттєвого стрибка", size=11, fill="#ffffff", stroke="#dddddd")
    out.append(tb_kv)

    # Model 3: SLS / Zener
    out.append(rect(555, 50, 235, 300, fill="#fafafa", stroke="#cccccc", rx=6))
    out.append(text(672, 75, "Стандартне лінійне тіло", size=14, color=INK, bold=True))
    out.append(text(672, 95, "(Модель Зенера)", size=12, color=MUTED))

    out.append(line(575, 160, 590, 160, color=LINE, sw=2))
    out.append(line(590, 125, 590, 195, color=LINE, sw=2))
    out.append(spring(590, 125, 745, 125, color=FIELD))
    out.append(spring(590, 195, 665, 195, color=NEG))
    out.append(dashpot(665, 195, 745, 195, color=POS))
    out.append(line(745, 125, 745, 195, color=LINE, sw=2))
    out.append(line(745, 160, 760, 160, color=LINE, sw=2))
    out.append(text(667, 105, "E₀ (тривала)", size=12, color=FIELD, bold=True))
    out.append(text(627, 220, "E₁", size=12, color=NEG, bold=True))
    text_eta_x = 705
    out.append(text(text_eta_x, 220, "η₁", size=12, color=POS, bold=True))

    tb_sls, _, _ = textbox(672, 260, "σ + τ_σ(dσ/dt) = E_R(ε + τ_ε dε/dt)\n\n• Описує і релаксацію, і повзучість\n• Обмежена пружність E₀ + E₁", size=10.5, fill="#ffffff", stroke="#dddddd")
    out.append(tb_sls)

    save_svg(os.path.join(out_dir, "mechanical-models.svg"), make_svg_doc(w, h, "".join(out)))

# ── Fig 3: Stress Relaxation vs Creep/Recovery Curves ─────────────────────────
def fig3_creep_relaxation_curves(out_dir):
    w, h = 820, 360
    out = []

    out.append(rect(30, 40, 365, 290, fill="#ffffff", stroke="#cccccc", rx=6))
    out.append(text(212, 65, "Релаксація напружень σ(t) при ε = const", size=14, color=INK, bold=True))
    
    out.append(line(70, 270, 360, 270, color=LINE, sw=1.5))
    out.append(line(70, 270, 70, 90, color=LINE, sw=1.5))
    out.append(text(365, 274, "t", size=13, color=INK, bold=True))
    out.append(text(65, 85, "σ", size=13, color=INK, bold=True))

    out.append(line(70, 110, 110, 110, color=MUTED, sw=1, dash="2,2"))
    out.append(text(55, 115, "σ₀", size=12, color=INK, bold=True))

    path_m = []
    for i in range(100):
        t_val = i / 99.0
        x = 110 + t_val * 230
        y = 270 - 160 * math.exp(-t_val * 3.5)
        path_m.append(f"{'M' if i==0 else 'L'} {x:.1f} {y:.1f}")
    out.append(f'<path d="{" ".join(path_m)}" fill="none" stroke="{POS}" stroke-width="2.5" />')
    out.append(text(270, 255, "Максвелл (σ → 0)", size=11, color=POS, bold=True))

    path_sls = []
    for i in range(100):
        t_val = i / 99.0
        x = 110 + t_val * 230
        y = 270 - (60 + 100 * math.exp(-t_val * 3.0))
        path_sls.append(f"{'M' if i==0 else 'L'} {x:.1f} {y:.1f}")
    out.append(f'<path d="{" ".join(path_sls)}" fill="none" stroke="{FIELD}" stroke-width="2.5" />')
    out.append(text(280, 195, "Зенер (σ → σ_∞)", size=11, color=FIELD, bold=True))

    out.append(line(110, 270, 110, 95, color=NEG, sw=2, dash="4,2"))
    out.append(text(115, 100, "Кельвін-Фойгт (дельта-сплеск)", size=10, color=NEG))

    out.append(line(110, 270, 110, 110, color=LINE, sw=1.5, dash="2,2"))
    out.append(text(110, 285, "t₀", size=12, color=INK))

    out.append(rect(425, 40, 365, 290, fill="#ffffff", stroke="#cccccc", rx=6))
    out.append(text(607, 65, "Повзучість та відновлення ε(t)", size=14, color=INK, bold=True))

    out.append(line(465, 270, 755, 270, color=LINE, sw=1.5))
    out.append(line(465, 270, 465, 90, color=LINE, sw=1.5))
    out.append(text(760, 274, "t", size=13, color=INK, bold=True))
    out.append(text(460, 85, "ε", size=13, color=INK, bold=True))

    t0_x = 505
    t1_x = 645
    out.append(line(t0_x, 270, t0_x, 90, color=MUTED, sw=1, dash="2,2"))
    out.append(line(t1_x, 270, t1_x, 90, color=MUTED, sw=1, dash="2,2"))
    out.append(text(t0_x, 285, "t₀ (навантаження)", size=11, color=MUTED))
    out.append(text(t1_x, 285, "t₁ (розвантаження)", size=11, color=MUTED))

    out.append(f'<path d="M 465 270 L {t0_x} 270 L {t0_x} 220 L {t1_x} 140 L {t1_x} 190 L 750 190" fill="none" stroke="{POS}" stroke-width="2" dash="4,2"/>')
    out.append(text(710, 175, "Максвелл", size=11, color=POS, bold=True))

    path_kv = [f"M 465 270 L {t0_x} 270"]
    for i in range(50):
        t_val = i / 49.0
        x = t0_x + t_val * (t1_x - t0_x)
        y = 270 - 110 * (1.0 - math.exp(-t_val * 3.0))
        path_kv.append(f"L {x:.1f} {y:.1f}")
    y_at_t1 = 270 - 110 * (1.0 - math.exp(-3.0))
    for i in range(50):
        t_val = i / 49.0
        x = t1_x + t_val * (750 - t1_x)
        y = 270 - (y_at_t1 - 270) * math.exp(-t_val * 3.0) - 270
        path_kv.append(f"L {x:.1f} {y:.1f}")
    out.append(f'<path d="{" ".join(path_kv)}" fill="none" stroke="{NEG}" stroke-width="2" />')
    out.append(text(710, 255, "Кельвін-Фойгт", size=11, color=NEG, bold=True))

    path_sls_c = [f"M 465 270 L {t0_x} 270 L {t0_x} 240"]
    for i in range(50):
        t_val = i / 49.0
        x = t0_x + t_val * (t1_x - t0_x)
        y = 240 - 80 * (1.0 - math.exp(-t_val * 3.0))
        path_sls_c.append(f"L {x:.1f} {y:.1f}")
    y_end = 240 - 80 * (1.0 - math.exp(-3.0))
    path_sls_c.append(f"L {t1_x} {y_end + 30}")
    for i in range(50):
        t_val = i / 49.0
        x = t1_x + t_val * (750 - t1_x)
        y = 270 - (y_end + 30 - 270) * math.exp(-t_val * 3.0) - 270
        path_sls_c.append(f"L {x:.1f} {y:.1f}")
    out.append(f'<path d="{" ".join(path_sls_c)}" fill="none" stroke="{FIELD}" stroke-width="2.5" />')
    out.append(text(620, 85, "Зенер (реалістична)", size=11, color=FIELD, bold=True))

    save_svg(os.path.join(out_dir, "creep-relaxation-curves.svg"), make_svg_doc(w, h, "".join(out)))

# ── Fig 4: Dynamic Mechanical Analysis (DMA) & Complex Modulus ────────────────
def fig4_dma_complex_modulus(out_dir):
    w, h = 820, 380
    out = []

    out.append(rect(30, 40, 365, 310, fill="#ffffff", stroke="#cccccc", rx=6))
    out.append(text(212, 65, "Гармонічне збудження (зсув фази δ)", size=14, color=INK, bold=True))

    out.append(line(70, 200, 370, 200, color=LINE, sw=1.5))
    out.append(line(70, 200, 70, 80, color=LINE, sw=1.5))
    out.append(text(375, 204, "t", size=13, color=INK, bold=True))

    path_strain = []
    path_stress = []
    delta = 0.75
    for i in range(120):
        t_val = i / 119.0 * 2.5 * math.pi
        x = 80 + i * 2.3
        y_str = 200 - 70 * math.sin(t_val)
        y_sts = 200 - 90 * math.sin(t_val + delta)
        path_strain.append(f"{'M' if i==0 else 'L'} {x:.1f} {y_str:.1f}")
        path_stress.append(f"{'M' if i==0 else 'L'} {x:.1f} {y_sts:.1f}")

    out.append(f'<path d="{" ".join(path_strain)}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')
    out.append(f'<path d="{" ".join(path_stress)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    out.append(text(285, 120, "Напруження σ(t)", size=12, color=POS, bold=True))
    out.append(text(285, 260, "Деформація ε(t)", size=12, color=NEG, bold=True))

    x_sts_peak = 80 + ((math.pi/2 - delta) / (2.5*math.pi)) * 120 * 2.3
    x_str_peak = 80 + ((math.pi/2) / (2.5*math.pi)) * 120 * 2.3
    out.append(line(x_sts_peak, 110, x_sts_peak, 280, color=MUTED, sw=1, dash="2,2"))
    out.append(line(x_str_peak, 130, x_str_peak, 280, color=MUTED, sw=1, dash="2,2"))
    out.append(line(x_sts_peak, 275, x_str_peak, 275, color=FIELD, sw=2, dash="none"))
    out.append(text((x_sts_peak + x_str_peak)/2, 295, "зсув δ", size=12, color=FIELD, bold=True))

    tb_comp, _, _ = textbox(212, 325, "G* = G' + i·G''     tan δ = G'' / G'", size=12, fill="#eafaf1", stroke=FIELD)
    out.append(tb_comp)

    out.append(rect(425, 40, 365, 310, fill="#ffffff", stroke="#cccccc", rx=6))
    out.append(text(607, 65, "Температурний спектр DMA (склування T_g)", size=14, color=INK, bold=True))

    out.append(line(465, 270, 765, 270, color=LINE, sw=1.5))
    out.append(line(465, 270, 465, 90, color=LINE, sw=1.5))
    out.append(text(770, 274, "T", size=13, color=INK, bold=True))
    out.append(text(445, 85, "G', G''", size=12, color=INK, bold=True))

    tg_x = 615
    out.append(line(tg_x, 90, tg_x, 270, color=MUTED, sw=1.5, dash="3,3"))
    out.append(text(tg_x, 285, "T_g", size=13, color=POS, bold=True))

    path_g1 = []
    for i in range(100):
        t_val = i / 99.0
        x = 475 + t_val * 270
        y = 110 + 130 / (1.0 + math.exp(-(t_val - 0.52) * 15))
        path_g1.append(f"{'M' if i==0 else 'L'} {x:.1f} {y:.1f}")
    out.append(f'<path d="{" ".join(path_g1)}" fill="none" stroke="{NEG}" stroke-width="2.5" />')
    out.append(text(515, 100, "G' (пружний)", size=12, color=NEG, bold=True))
    out.append(text(725, 230, "високоеластичне плато", size=10, color=NEG))

    path_g2 = []
    for i in range(100):
        t_val = i / 99.0
        x = 475 + t_val * 270
        y = 250 - 110 * math.exp(-((t_val - 0.52) * 8)**2)
        path_g2.append(f"{'M' if i==0 else 'L'} {x:.1f} {y:.1f}")
    out.append(f'<path d="{" ".join(path_g2)}" fill="none" stroke="{POS}" stroke-width="2.5" />')
    out.append(text(655, 135, "G'' (в'язкий пік)", size=12, color=POS, bold=True))

    out.append(text(515, 255, "Склоподібний", size=11, color=MUTED))
    out.append(text(715, 255, "Високоеластичний", size=11, color=MUTED))

    save_svg(os.path.join(out_dir, "dma-complex-modulus.svg"), make_svg_doc(w, h, "".join(out)))

# ── Fig 5: Time-Temperature Superposition (TTS) & WLF Master Curve ───────────
def fig5_wlf_master_curve(out_dir):
    w, h = 820, 360
    out = []

    out.append(text(410, 25, "Температурно-часова суперпозиція (принцип еквівалентності та інваріантності WLF)", size=15, color=INK, bold=True))

    out.append(rect(30, 50, 365, 295, fill="#ffffff", stroke="#cccccc", rx=6))
    out.append(text(212, 75, "Окремі ізотерми G'(ω) при T₁, T₂, T₃...", size=13, color=INK, bold=True))

    out.append(line(65, 300, 375, 300, color=LINE, sw=1.5))
    out.append(line(65, 300, 65, 95, color=LINE, sw=1.5))
    out.append(text(375, 318, "lg ω (частота)", size=12, color=INK, bold=True))
    out.append(text(60, 90, "lg G'", size=12, color=INK, bold=True))

    temps = [
        ("T₁ < T₀ (холодно)", POS, 80, 170, 110, 240),
        ("T₀ (опорна)", FIELD, 150, 240, 130, 260),
        ("T₂ > T₀ (гаряче)", NEG, 220, 310, 160, 280),
    ]
    for label, col, x_start, x_end, y_start, y_end in temps:
        path = []
        for i in range(50):
            t_val = i / 49.0
            x = x_start + t_val * (x_end - x_start)
            y = y_start + (y_end - y_start) / (1.0 + math.exp(-(t_val - 0.5)*6))
            path.append(f"{'M' if i==0 else 'L'} {x:.1f} {y:.1f}")
        out.append(f'<path d="{" ".join(path)}" fill="none" stroke="{col}" stroke-width="2.5"/>')
        out.append(text((x_start+x_end)/2, y_start - 12, label, size=10.5, color=col, bold=True))

    out.append(arrow(110, 260, 170, 260, color=POS, sw=1.5))
    out.append(arrow(280, 200, 220, 200, color=NEG, sw=1.5))
    out.append(text(140, 275, "+lg a_T", size=11, color=POS, bold=True))
    out.append(text(250, 190, "-lg a_T", size=11, color=NEG, bold=True))

    out.append(rect(425, 50, 365, 295, fill="#ffffff", stroke="#cccccc", rx=6))
    out.append(text(607, 75, "Єдина узагальнена інваріантна крива (Master Curve)", size=13, color=INK, bold=True))

    out.append(line(460, 300, 770, 300, color=LINE, sw=1.5))
    out.append(line(460, 300, 460, 95, color=LINE, sw=1.5))
    out.append(text(765, 318, "lg (a_T · ω)", size=12, color=INK, bold=True))
    out.append(text(455, 90, "lg G'", size=12, color=INK, bold=True))

    path_master = []
    for i in range(100):
        t_val = i / 99.0
        x = 475 + t_val * 270
        y = 110 + 170 / (1.0 + math.exp(-(t_val - 0.5) * 8))
        path_master.append(f"{'M' if i==0 else 'L'} {x:.1f} {y:.1f}")
    out.append(f'<path d="{" ".join(path_master)}" fill="none" stroke="{FIELD}" stroke-width="3"/>')

    wlf_text = "Рівняння ВІЛЬЯМСА-ЛАНДЕЛА-ФЕРРІ (WLF):\nlog₁₀ a_T = -C₁·(T - T₀) / (C₂ + T - T₀)"
    tb_wlf, _, _ = textbox(607, 240, wlf_text, size=11, fill="#fcf3cf", stroke="#f39c12")
    out.append(tb_wlf)

    save_svg(os.path.join(out_dir, "wlf-master-curve.svg"), make_svg_doc(w, h, "".join(out)))

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = ensure_img_dir(base_dir)
    fig1_viscoelastic_responses(out_dir)
    fig2_mechanical_models(out_dir)
    fig3_creep_relaxation_curves(out_dir)
    fig4_dma_complex_modulus(out_dir)
    fig5_wlf_master_curve(out_dir)
    print(f"Generated 5 SVG figures in {out_dir}")

if __name__ == "__main__":
    main()
