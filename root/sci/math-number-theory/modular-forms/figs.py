import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import render, rect, line, text, circle, arrow, textbox

def svg_path(d, fill="none", stroke="#333333", sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}/>'

def draw_fundamental_domain():
    w, h = 800, 520
    frags = []

    # Background
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="#cbd5e1", sw=1))

    # Title
    frags.append(text(w / 2, 30, "Фундаментальна область F = PSL(2,ℤ)\\ℍ та модулярні перетворення S, T", size=16, bold=True, color="#0f172a", anchor="middle"))

    # Mapping complex plane: Re(tau) in [-1.5, 1.5], Im(tau) in [0, 2.2]
    # Center x = 400 is Re=0. Scale x: 1.0 unit = 200px.
    # Center y = 430 is Im=0. Scale y: 1.0 unit = 180px (pointing up).

    def to_px(re, im):
        px = 400 + re * 200
        py = 430 - im * 180
        return px, py

    # Background for Upper Half Plane H
    frags.append(rect(50, 60, 700, 370, fill="#f8fafc", stroke="#e2e8f0", sw=1))
    frags.append(text(730, 80, "Верхня півплощина ℍ (Im(τ) > 0)", size=11, color="#64748b", anchor="end", bold=True))

    # Real Axis Im(tau) = 0
    ax0, ay0 = to_px(-1.6, 0)
    ax1, ay1 = to_px(1.6, 0)
    frags.append(arrow(ax0, ay0, ax1, ay1, color="#475569", sw=2))
    frags.append(text(ax1 + 10, ay1 + 4, "Re(τ)", size=12, color="#334155", bold=True))

    # Imaginary Axis Re(tau) = 0
    ix0, iy0 = to_px(0, 0)
    ix1, iy1 = to_px(0, 2.1)
    frags.append(arrow(ix0, iy0, ix1, iy1, color="#475569", sw=1.5))
    frags.append(text(ix1 + 10, iy1 + 5, "Im(τ)", size=12, color="#334155", bold=True))

    p_rho1_x, p_rho1_y = to_px(-0.5, 0.866025)
    p_rho2_x, p_rho2_y = to_px(0.5, 0.866025)
    p_top1_x, p_top1_y = to_px(-0.5, 2.05)
    p_top2_x, p_top2_y = to_px(0.5, 2.05)

    fd_d = f"M {p_top1_x},{p_top1_y} L {p_rho1_x},{p_rho1_y} A 180,180 0 0 1 {p_rho2_x},{p_rho2_y} L {p_top2_x},{p_top2_y} Z"
    frags.append(svg_path(fd_d, fill="#dbeafe", stroke="#2563eb", sw=2.5))

    # Tessellation domains (neighboring domains)
    # T(F): Re in [0.5, 1.5]
    t_rho1_x, t_rho1_y = to_px(0.5, 0.866025)
    t_rho2_x, t_rho2_y = to_px(1.5, 0.866025)
    t_top1_x, t_top1_y = to_px(0.5, 2.05)
    t_top2_x, t_top2_y = to_px(1.5, 2.05)
    fd_t = f"M {t_top1_x},{t_top1_y} L {t_rho1_x},{t_rho1_y} L {t_top2_x},{t_top2_y} Z"
    frags.append(svg_path(fd_t, fill="#f1f5f9", stroke="#94a3b8", sw=1, dash="3,3"))
    frags.append(text(to_px(1.0, 1.4)[0], to_px(1.0, 1.4)[1], "T·F (τ + 1)", size=11, color="#64748b", anchor="middle"))

    # T^-1(F): Re in [-1.5, -0.5]
    tm_top1_x, tm_top1_y = to_px(-1.5, 2.05)
    tm_top2_x, tm_top2_y = to_px(-0.5, 2.05)
    tm_rho1_x, tm_rho1_y = to_px(-1.5, 0.866025)
    tm_rho2_x, tm_rho2_y = to_px(-0.5, 0.866025)
    fd_tm = f"M {tm_top1_x},{tm_top1_y} L {tm_rho1_x},{tm_rho1_y} L {tm_top2_x},{tm_top2_y} Z"
    frags.append(svg_path(fd_tm, fill="#f1f5f9", stroke="#94a3b8", sw=1, dash="3,3"))
    frags.append(text(to_px(-1.0, 1.4)[0], to_px(-1.0, 1.4)[1], "T⁻¹·F (τ - 1)", size=11, color="#64748b", anchor="middle"))

    # S(F): inside unit circle under S: tau -> -1/tau
    s_arc_d = f"M {p_rho1_x},{p_rho1_y} A 180,180 0 0 0 {p_rho2_x},{p_rho2_y} A 90,90 0 0 1 {to_px(0, 0.5)[0]},{to_px(0, 0.5)[1]} A 90,90 0 0 1 {p_rho1_x},{p_rho1_y} Z"
    frags.append(svg_path(s_arc_d, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(to_px(0, 0.65)[0], to_px(0, 0.65)[1], "S·F (-1/τ)", size=11, color="#b45309", anchor="middle", bold=True))

    # Boundary lines Re = -1/2 and Re = 1/2
    l1_x0, l1_y0 = to_px(-0.5, 0)
    l1_x1, l1_y1 = to_px(-0.5, 2.1)
    frags.append(line(l1_x0, l1_y0, l1_x1, l1_y1, color="#2563eb", sw=1.5, dash="4,4"))
    frags.append(text(l1_x0, l1_y0 + 18, "Re = -1/2", size=10, color="#1e40af", anchor="middle"))

    l2_x0, l2_y0 = to_px(0.5, 0)
    l2_x1, l2_y1 = to_px(0.5, 2.1)
    frags.append(line(l2_x0, l2_y0, l2_x1, l2_y1, color="#2563eb", sw=1.5, dash="4,4"))
    frags.append(text(l2_x0, l2_y0 + 18, "Re = 1/2", size=10, color="#1e40af", anchor="middle"))

    # Unit circle arc boundary
    arc_d = f"M {to_px(-1.0, 0)[0]},{to_px(-1.0, 0)[1]} A 180,180 0 0 1 {to_px(1.0, 0)[0]},{to_px(1.0, 0)[1]}"
    frags.append(svg_path(arc_d, fill="none", stroke="#dc2626", sw=1.5, dash="3,3"))

    # Key vertices:
    # tau = i = (0, 1)
    ix, iy = to_px(0, 1.0)
    frags.append(circle(ix, iy, 5.5, fill="#ef4444", stroke="#991b1b", sw=1.5))
    frags.append(text(ix + 12, iy - 6, "τ = i (порядок 2)", size=11, bold=True, color="#991b1b"))

    # tau = rho = e^(2pi i / 3) = (-1/2, sqrt(3)/2)
    r1x, r1y = to_px(-0.5, 0.866025)
    frags.append(circle(r1x, r1y, 5.5, fill="#10b981", stroke="#047857", sw=1.5))
    frags.append(text(r1x - 12, r1y - 8, "ρ = e²ᵖⁱⁱ/³ (порядок 3)", size=11, bold=True, color="#047857", anchor="end"))

    # tau = rho + 1 = e^(pi i / 3) = (1/2, sqrt(3)/2)
    r2x, r2y = to_px(0.5, 0.866025)
    frags.append(circle(r2x, r2y, 5.5, fill="#10b981", stroke="#047857", sw=1.5))
    frags.append(text(r2x + 12, r2y - 8, "ρ + 1", size=11, bold=True, color="#047857", anchor="start"))

    # Cusp at infinity i*infinity
    frags.append(circle(to_px(0, 2.0)[0], to_px(0, 2.0)[1], 6, fill="#a855f7", stroke="#6b21a8", sw=1.5))
    frags.append(text(to_px(0, 2.0)[0] + 12, to_px(0, 2.0)[1] + 4, "i∞ (вершина / касп)", size=11, bold=True, color="#6b21a8"))

    # Label inside fundamental domain
    frags.append(text(to_px(0, 1.45)[0], to_px(0, 1.45)[1], "Фундаментальна\nобласть F", size=13, color="#1e40af", bold=True, anchor="middle"))

    # Transformation arrows
    # T: tau -> tau + 1 (horizontal arrow)
    frags.append(arrow(to_px(-0.2, 1.7)[0], to_px(-0.2, 1.7)[1], to_px(0.8, 1.7)[0], to_px(0.8, 1.7)[1], color="#2563eb", sw=2))
    frags.append(text(to_px(0.3, 1.7)[0], to_px(0.3, 1.7)[1] - 8, "T: τ ↦ τ + 1", size=11, bold=True, color="#1d4ed8", anchor="middle"))

    # S: tau -> -1/tau (inversion arrow)
    frags.append(arrow(to_px(0.1, 1.15)[0], to_px(0.1, 1.15)[1], to_px(0.05, 0.7)[0], to_px(0.05, 0.7)[1], color="#d97706", sw=2))
    frags.append(text(to_px(0.2, 0.9)[0], to_px(0.2, 0.9)[1], "S: τ ↦ -1/τ", size=11, bold=True, color="#b45309", anchor="start"))

    # Bottom summary box
    b_bot, _, _ = textbox(w / 2, 480, "Ключовий висновок: Будь-яка точка ℍ переводиться єдиним чином у F дією групи PSL(2,ℤ) = ⟨S, T | S² = (ST)³ = I⟩", size=11, fill="#eff6ff", stroke="#3b82f6", color="#1e40af", bold=True)
    frags.append(b_bot)

    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'fig-fundamental-domain.svg')
    render(out_path, w, h, *frags, title="Фундаментальна область PSL(2, Z)")
    print("Generated fig-fundamental-domain.svg successfully.")

def draw_modular_forms_architecture():
    w, h = 800, 490
    frags = []

    # Background
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="#cbd5e1", sw=1))

    # Title
    frags.append(text(w / 2, 30, "Архітектура теорії модулярних форм та арифметичний міст", size=16, bold=True, color="#0f172a", anchor="middle"))

    # Left Column: Complex Analysis & Geometry
    b_left_top, _, _ = textbox(190, 85, "1. Верхня півплощина ℍ та Решітки Λ\nτ ∈ ℍ ⇔ решітка Λ = ℤ + ℤτ ⊂ ℂ\nДискретні симетрії групи SL(2,ℤ)", size=11.5, fill="#eff6ff", stroke="#3b82f6", color="#1e40af", bold=True)
    frags.append(b_left_top)

    b_left_mid, _, _ = textbox(190, 210, "2. Простір модулярних форм M_k\nf( (aτ+b)/(cτ+d) ) = (cτ+d)ᵏ f(τ)\nКільце M_* = ℂ[E₄, E₆], дискеримінант Δ", size=11.5, fill="#f0fdf4", stroke="#22c55e", color="#15803d", bold=True)
    frags.append(b_left_mid)

    b_left_bot, _, _ = textbox(190, 340, "3. Оператори Гекке T_p та Ейлерові добутки\nT_p f = λ_p f ⇒ L(s, f) = ∏ (1 - a_p p⁻ˢ + pᵏ⁻¹⁻²ˢ)⁻¹\nЗв'язок з рядами Діріхле", size=11.5, fill="#faf5ff", stroke="#a855f7", color="#7e22ce", bold=True)
    frags.append(b_left_bot)

    # Connecting arrows on left column
    frags.append(arrow(190, 125, 190, 170, color="#3b82f6", sw=2))
    frags.append(arrow(190, 250, 190, 295, color="#22c55e", sw=2))

    # Right Column: Arithmetic & Diophantine Geometry
    b_right_top, _, _ = textbox(610, 85, "4. Діофантові рівняння та суми квадратів\nθ(τ) = ∑ q^{n²} ⇒ θ(τ)ᵏ = ∑ r_k(n) qⁿ\nТочні формули для кількості розв'язків", size=11.5, fill="#fff7ed", stroke="#f97316", color="#c2410c", bold=True)
    frags.append(b_right_top)

    b_right_mid, _, _ = textbox(610, 210, "5. Еліптичні криві E/ℚ\ny² = x³ + ax + b (дискримінант D ≠ 0)\nЧисло точок #E(𝔽_p) = p + 1 - a_p", size=11.5, fill="#fefce8", stroke="#eab308", color="#a16207", bold=True)
    frags.append(b_right_mid)

    b_right_bot, _, _ = textbox(610, 340, "6. Велика теорема Ферма (FLT)\naⁿ + bⁿ = cⁿ ⇒ Крива Фрей y² = x(x-aⁿ)(x+bⁿ)\nЗниження рівня Рібета: S₂(Γ₀(2)) = {0}", size=11.5, fill="#fef2f2", stroke="#ef4444", color="#b91c1c", bold=True)
    frags.append(b_right_bot)

    # Connecting arrows on right column
    frags.append(arrow(610, 250, 610, 295, color="#eab308", sw=2))

    # Central Modularity Bridge (Shimura-Taniyama-Weil)
    frags.append(arrow(345, 210, 455, 210, color="#059669", sw=3))
    frags.append(arrow(455, 210, 345, 210, color="#059669", sw=3))
    frags.append(rect(345, 185, 110, 50, fill="#ecfdf5", stroke="#10b981", sw=2, rx=6))
    frags.append(text(400, 205, "ТЕОРЕМА ПРО", size=10, bold=True, color="#047857", anchor="middle"))
    frags.append(text(400, 222, "МОДУЛЯРНІСТЬ", size=11, bold=True, color="#065f46", anchor="middle"))

    # Arrow from modular forms to sums of squares
    frags.append(arrow(345, 100, 455, 100, color="#f97316", sw=1.8))

    # Arrow from modularity to FLT
    frags.append(arrow(345, 340, 455, 340, color="#dc2626", sw=2))

    # Bottom summary box
    b_bot, _, _ = textbox(w / 2, 445, "Фундаментальний результат: Кожна еліптична крива над ℚ є модулярною (Wiles et al.) — це поєднало аналіз і діофантову алгебру", size=11.5, fill="#ecfdf5", stroke="#059669", color="#065f46", bold=True)
    frags.append(b_bot)

    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'fig-modular-forms-architecture.svg')
    render(out_path, w, h, *frags, title="Архітектура модулярних форм")
    print("Generated fig-modular-forms-architecture.svg successfully.")

if __name__ == "__main__":
    draw_fundamental_domain()
    draw_modular_forms_architecture()
