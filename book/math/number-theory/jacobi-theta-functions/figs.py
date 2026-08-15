import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import render, rect, line, text, circle, arrow, fitbox

def svg_path(d, fill="none", stroke="#333333", sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}/>'

def draw_theta_constants(path):
    w, h = 800, 480
    frags = []

    # Title
    frags.append(text(w / 2, 28, "Аналітичний біг тета-констант Якобі θ₂(q), θ₃(q), θ₄(q) при q ∈ [0, 1)", size=15, bold=True, color="#0f172a", anchor="middle"))

    # Left Box: Plot of Theta Constants
    frags.append(rect(25, 55, 430, 400, fill="#f8fafc", stroke="#94a3b8", sw=1))
    frags.append(text(240, 80, "Поведінка функцій на інтервалі q ∈ [0, 0.85]", size=13, color="#1e293b", bold=True, anchor="middle"))

    # Plot axes inside box
    ox, oy = 75, 410
    pw, ph = 350, 300  # width 350px for q in [0, 0.85], height 300px for y in [0, 3.5]

    # Grid lines
    for q_val in [0.2, 0.4, 0.6, 0.8]:
        gx = ox + (q_val / 0.85) * pw
        frags.append(line(gx, oy, gx, oy - ph, color="#e2e8f0", sw=1, dash="2,2"))
        frags.append(text(gx, oy + 18, f"{q_val:.1f}", size=10, color="#64748b", anchor="middle"))

    for y_val in [1.0, 2.0, 3.0]:
        gy = oy - (y_val / 3.5) * ph
        frags.append(line(ox, gy, ox + pw, gy, color="#e2e8f0", sw=1, dash="2,2"))
        frags.append(text(ox - 10, gy + 4, f"{y_val:.1f}", size=10, color="#64748b", anchor="end"))

    # Main axes
    frags.append(line(ox, oy, ox + pw + 15, oy, color="#475569", sw=1.5))
    frags.append(line(ox, oy, ox, oy - ph - 15, color="#475569", sw=1.5))
    frags.append(text(ox + pw + 20, oy + 4, "q", size=12, color="#1e293b", bold=True))
    frags.append(text(ox - 4, oy - ph - 20, "y", size=12, color="#1e293b", bold=True))

    # Calculate theta constants values for plotting
    pts3, pts4, pts2 = [], [], []
    steps = 60
    for i in range(steps + 1):
        q = (i / steps) * 0.82
        x = ox + (q / 0.85) * pw

        t3 = 1.0 + 2.0*q + 2.0*(q**4) + 2.0*(q**9)
        t4 = max(0.01, 1.0 - 2.0*q + 2.0*(q**4) - 2.0*(q**9))
        t2 = 2.0 * (q**0.25) * (1.0 + (q**2) + (q**6)) if q > 0 else 0.0

        y3 = oy - (t3 / 3.5) * ph
        y4 = oy - (t4 / 3.5) * ph
        y2 = oy - (t2 / 3.5) * ph

        pts3.append(f"{x:.1f},{y3:.1f}")
        pts4.append(f"{x:.1f},{y4:.1f}")
        pts2.append(f"{x:.1f},{y2:.1f}")

    d3 = "M " + " L ".join(pts3)
    d4 = "M " + " L ".join(pts4)
    d2 = "M " + " L ".join(pts2)

    frags.append(svg_path(d3, fill="none", stroke="#2563eb", sw=2.5))
    frags.append(svg_path(d4, fill="none", stroke="#dc2626", sw=2.5))
    frags.append(svg_path(d2, fill="none", stroke="#16a34a", sw=2.5))

    # Curve labels
    frags.append(text(ox + 290, oy - (2.9 / 3.5) * ph, "θ₃(q)", size=12, color="#1d4ed8", bold=True))
    frags.append(text(ox + 290, oy - (2.4 / 3.5) * ph, "θ₂(q)", size=12, color="#15803d", bold=True))
    frags.append(text(ox + 290, oy - (0.25 / 3.5) * ph, "θ₄(q)", size=12, color="#b91c1c", bold=True))

    # Key points markers
    frags.append(circle(ox, oy - (1.0 / 3.5) * ph, 4, fill="#2563eb", stroke="#1d4ed8", sw=1))
    frags.append(text(ox + 8, oy - (1.0 / 3.5) * ph - 8, "θ₃(0)=1, θ₄(0)=1", size=10, color="#1e293b"))
    frags.append(circle(ox, oy, 4, fill="#16a34a", stroke="#15803d", sw=1))
    frags.append(text(ox + 8, oy + 14, "θ₂(0)=0", size=10, color="#15803d", bold=True))

    # Right Box: Fundamental Identities & Asymptotics
    frags.append(rect(470, 55, 305, 400, fill="#f8fafc", stroke="#94a3b8", sw=1))
    frags.append(text(622, 80, "Фундаментальні тотожності", size=13, color="#1e293b", bold=True, anchor="middle"))

    s1 = "Тотожність Якобі 4-х степенів:\nθ₃(q)⁴ = θ₂(q)⁴ + θ₄(q)⁴\n\nДля будь-якого |q| < 1 квадрат суми\nθ₃⁴ дає суму квадратів θ₂⁴ та θ₄⁴."
    frags.append(fitbox(480, 95, 285, 95, s1, size=11, fill="#ffffff", stroke="#cbd5e1"))

    s2 = "Гранична поведінка при q → 0:\n● θ₃(q) = 1 + 2q + O(q⁴)\n● θ₄(q) = 1 - 2q + O(q⁴)\n● θ₂(q) = 2·q¹/⁴ · (1 + q² + O(q⁶))\nПри малик q ряд збігається експоненціально швидко!"
    frags.append(fitbox(480, 200, 285, 110, s2, size=11, fill="#eff6ff", stroke="#93c5fd"))

    s3 = "Модулярна двоїстість q → 1⁻:\nПри q = e^(-π t) та t → 0⁺:\n● θ₃(e^(-π t)) ~ 1 / √t\n● θ₂(e^(-π t)) ~ 1 / √t\n● θ₄(e^(-π t)) ~ 2 · e^(-π/(4t)) / √t"
    frags.append(fitbox(480, 320, 285, 120, s3, size=11, fill="#fef2f2", stroke="#fca5a5"))

    return render(path, w, h, *frags)

def draw_poisson_transform(path):
    w, h = 800, 460
    frags = []

    # Title
    frags.append(text(w / 2, 28, "Модулярне перетворення τ ↦ -1/τ та формула підсумовування Пуассона", size=15, bold=True, color="#0f172a", anchor="middle"))

    # Box 1: Physical domain (time t)
    frags.append(rect(25, 55, 360, 380, fill="#f8fafc", stroke="#94a3b8", sw=1))
    frags.append(text(205, 80, "Часова область (параметр t > 0)", size=13, color="#1e293b", bold=True, anchor="middle"))

    s_phys = "Тета-ряд у прямому просторі:\nθ₃(0, e^(-π t)) = ∑_{n=-∞}^∞ e^(-π n² t)\n\n● При великих t (t ≫ 1):\n  Доданки з n ≠ 0 експоненціально малі.\n  Достатньо 1-2 членів: 1 + 2·e^(-π t).\n\n● При малих t (t ≪ 1):\n  Збіжність вкрай повільна (тисячі членів)."
    frags.append(fitbox(40, 100, 330, 160, s_phys, size=11, fill="#ffffff", stroke="#cbd5e1"))

    # Gaussian visual representation for t=0.2 (wide) vs t=2.0 (narrow)
    frags.append(text(205, 275, "Сума гаусіан у дискретних вузлах ℤ:", size=11, color="#475569", bold=True, anchor="middle"))
    # Draw lattice ticks
    oy1 = 380
    frags.append(line(45, oy1, 365, oy1, color="#cbd5e1", sw=1.5))
    for n in range(-4, 5):
        nx = 205 + n * 35
        frags.append(line(nx, oy1 - 5, nx, oy1 + 5, color="#64748b", sw=1.5))
        frags.append(text(nx, oy1 + 18, str(n), size=10, color="#64748b", anchor="middle"))
        # draw gaussian pulse
        gh = 50 * math.exp(-0.25 * (n**2))
        frags.append(line(nx, oy1, nx, oy1 - gh, color="#2563eb", sw=2))
        frags.append(circle(nx, oy1 - gh, 3, fill="#2563eb", stroke="#1d4ed8", sw=1))

    # Middle Arrow: Poisson Summation Transformation
    frags.append(arrow(395, 245, 435, 245, color="#d97706", sw=3))
    frags.append(text(415, 230, "Пуассон", size=11, color="#b45309", bold=True, anchor="middle"))
    frags.append(text(415, 265, "t ↦ 1/t", size=11, color="#b45309", bold=True, anchor="middle"))

    # Box 2: Frequency domain (reciprocal 1/t)
    frags.append(rect(445, 55, 330, 380, fill="#f8fafc", stroke="#94a3b8", sw=1))
    frags.append(text(610, 80, "Частотна область (параметр 1/t)", size=13, color="#1e293b", bold=True, anchor="middle"))

    s_freq = "Тета-ряд у двоїстому просторі:\nθ₃(0, e^(-π/t)) = ∑_{k=-∞}^∞ e^(-π k² / t)\n\nФундаментальне тотожність Якобі:\nθ₃(0, e^(-π t)) = (1/√t) · θ₃(0, e^(-π/t))\n\n● При малих t (t ≪ 1):\n  Параметр 1/t великий! Двоїстий ряд\n  збігається МИТТЄВО (2-3 члени)."
    frags.append(fitbox(460, 100, 300, 180, s_freq, size=11, fill="#eff6ff", stroke="#93c5fd"))

    # Dual Gaussian visual
    frags.append(text(610, 295, "Перемасштабовані двоїсті вузли:", size=11, color="#475569", bold=True, anchor="middle"))
    oy2 = 380
    frags.append(line(460, oy2, 760, oy2, color="#cbd5e1", sw=1.5))
    for k in range(-3, 4):
        kx = 610 + k * 45
        frags.append(line(kx, oy2 - 5, kx, oy2 + 5, color="#64748b", sw=1.5))
        frags.append(text(kx, oy2 + 18, f"{k}", size=10, color="#64748b", anchor="middle"))
        gh2 = 60 * math.exp(-0.8 * (k**2))
        frags.append(line(kx, oy2, kx, oy2 - gh2, color="#16a34a", sw=2))
        frags.append(circle(kx, oy2 - gh2, 3, fill="#16a34a", stroke="#15803d", sw=1))

    return render(path, w, h, *frags)

def draw_applications_map(path):
    w, h = 800, 480
    frags = []

    # Title
    frags.append(text(w / 2, 28, "Мережа застосувань тета-функцій Якобі в теорії чисел та аналізі", size=15, bold=True, color="#0f172a", anchor="middle"))

    # Central Node: Jacobi Theta Functions
    frags.append(rect(270, 60, 260, 70, fill="#1e293b", stroke="#0f172a", sw=2, rx=8))
    frags.append(text(400, 88, "Тета-функції Якобі θᵢ(z, q)", size=14, color="#ffffff", bold=True, anchor="middle"))
    frags.append(text(400, 112, "q = e^(iπτ),  Im(τ) > 0", size=11, color="#94a3b8", anchor="middle"))

    # Branch 1: Sums of Squares (Top Left)
    frags.append(arrow(330, 130, 175, 175, color="#2563eb", sw=2))
    frags.append(rect(25, 175, 290, 125, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    frags.append(text(170, 198, "Теорія чисел: Суми квадратів", size=13, color="#1e3a8a", bold=True, anchor="middle"))
    s_sq = "● θ₃(q)ᵏ = ∑ rₖ(n) qⁿ\n● r₂(n) = 4 (d₁(n) - d₃(n))\n● r₄(n) = 8 ∑_{d|n, 4∤d} d (Лагранж)\n● r₈(n) = 16 ∑_{d|n} (-1)ⁿ⁻ᵈ d³"
    frags.append(fitbox(35, 210, 270, 80, s_sq, size=11, fill="#ffffff", stroke="#bfdbfe"))

    # Branch 2: Heat Equation (Top Right)
    frags.append(arrow(470, 130, 625, 175, color="#dc2626", sw=2))
    frags.append(rect(485, 175, 290, 125, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    frags.append(text(630, 198, "Фізика: Рівняння теплопровідності", size=13, color="#7f1d1d", bold=True, anchor="middle"))
    s_heat = "● Фундаментальний розв'язок на колі:\n  ∂u/∂t = D · ∂²u/∂x²\n● θ₃(z, τ) задовольняє диференціальне\n  рівняння в частинних похідних."
    frags.append(fitbox(495, 210, 270, 80, s_heat, size=11, fill="#ffffff", stroke="#fecaca"))

    # Branch 3: Riemann Zeta Function (Bottom Left)
    frags.append(arrow(310, 130, 175, 330, color="#16a34a", sw=2))
    frags.append(rect(25, 330, 290, 125, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    frags.append(text(170, 353, "Аналітична теорія чисел: ζ(s)", size=13, color="#14532d", bold=True, anchor="middle"))
    s_zeta = "● Перетворення Мелліна тета-константи:\n  π⁻ˢ/² Γ(s/2) ζ(s) = ∫₀^∞ xˢ/²⁻¹ ψ(x) dx\n● Функціональне рівняння ζ(s) випливає\n  безпосередньо з θ₃(1/t) = √t · θ₃(t)."
    frags.append(fitbox(35, 365, 270, 80, s_zeta, size=11, fill="#ffffff", stroke="#bbf7d0"))

    # Branch 4: Elliptic Integrals & AGM (Bottom Right)
    frags.append(arrow(490, 130, 625, 330, color="#d97706", sw=2))
    frags.append(rect(485, 330, 290, 125, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=6))
    frags.append(text(630, 353, "Обчислення: Еліптичні інтеграли & AGM", size=13, color="#78350f", bold=True, anchor="middle"))
    s_agm = "● Модуль k = (θ₂(q)/θ₃(q))²\n● Повний інтеграл K(k) = (π/2) · θ₃(q)²\n● Квадратично збіжне обчислення π та\n  спеціальних функцій через AGM Ґаусса."
    frags.append(fitbox(495, 365, 270, 80, s_agm, size=11, fill="#ffffff", stroke="#fde68a"))

    return render(path, w, h, *frags)

def main():
    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)

    draw_theta_constants(os.path.join(out_dir, 'fig-theta-constants.svg'))
    draw_poisson_transform(os.path.join(out_dir, 'fig-poisson-modular-transform.svg'))
    draw_applications_map(os.path.join(out_dir, 'fig-theta-applications-map.svg'))
    print("Successfully generated all figures for jacobi-theta-functions.")

if __name__ == '__main__':
    main()
