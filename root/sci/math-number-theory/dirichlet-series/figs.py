import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import render, rect, line, text, circle, arrow, textbox, fitbox, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG

def draw_convergence_plane():
    frags = []
    w, h = 800, 450
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="#cbd5e1", sw=1))
    
    # Title
    frags.append(text(w / 2, 35, "Області збіжності ряду Діріхле в комплексній площині s = σ + i·t", size=17, bold=True, color="#0f172a", anchor="middle"))
    
    # Axes: horizontal (Re s = sigma), vertical (Im s = t)
    ox, oy = 160, 230
    # Shading regions (backgrounds before axes and lines)
    xc = 350
    xa = 550
    
    # Region 1: Re(s) > sigma_a (Absolute convergence)
    frags.append(rect(xa, 85, 190, 215, fill="#ecfdf5", stroke="none"))
    # Region 2: sigma_c < Re(s) <= sigma_a (Conditional convergence)
    frags.append(rect(xc, 85, xa - xc, 215, fill="#fefce8", stroke="none"))
    # Region 3: Re(s) <= sigma_c (Divergence / Analytic continuation)
    frags.append(rect(60, 85, xc - 60, 215, fill="#fef2f2", stroke="none"))
    
    # Axis lines
    frags.append(arrow(50, oy, 750, oy, color="#475569", sw=1.8))
    frags.append(arrow(ox, 370, ox, 65, color="#475569", sw=1.8))
    frags.append(text(755, oy + 18, "σ = Re(s)", size=13, bold=True, color="#334155", anchor="start"))
    frags.append(text(ox + 12, 75, "t = Im(s)", size=13, bold=True, color="#334155", anchor="start"))
    frags.append(text(ox - 12, oy + 20, "0", size=13, color="#64748b", anchor="end"))
    
    # Vertical dashed lines for abscissas (stop at y=300 to avoid ineq_box)
    frags.append(line(xc, 80, xc, 300, color="#d97706", sw=2, dash="5,5"))
    frags.append(line(xa, 80, xa, 300, color="#059669", sw=2, dash="5,5"))
    
    # Box labels inside regions
    textbox1, _, _ = textbox(645, 145, "Абсолютна та рівномірна\nзбіжність ряду\nRe(s) > σ_a", size=12, fill="#d1fae5", stroke="#059669", color="#065f46", bold=True)
    frags.append(textbox1)
    
    textbox2, _, _ = textbox(450, 145, "Умовна збіжність\nσ_c < Re(s) ≤ σ_a\n(коли σ_a ≠ σ_c)", size=12, fill="#fef9c3", stroke="#d97706", color="#92400e", bold=True)
    frags.append(textbox2)
    
    textbox3, _, _ = textbox(255, 145, "Область розбіжності\nRe(s) ≤ σ_c\n(потрібне аналітичне\nпродовження)", size=12, fill="#fee2e2", stroke="#dc2626", color="#991b1b", bold=True)
    frags.append(textbox3)
    
    # Key inequality box
    ineq_box, _, _ = textbox(w / 2, 340, "Властивість смуги збіжності: 0 ≤ σ_a - σ_c ≤ 1", size=13.5, fill="#f8fafc", stroke="#64748b", color="#1e293b", bold=True)
    frags.append(ineq_box)

    # Labels for abscissas below ineq_box
    frags.append(text(xc, 405, "σ_c", size=15, bold=True, color="#b45309", anchor="middle"))
    frags.append(text(xc, 423, "абсциса збіжності", size=11, color="#d97706", anchor="middle"))
    
    frags.append(text(xa, 405, "σ_a", size=15, bold=True, color="#047857", anchor="middle"))
    frags.append(text(xa, 423, "абсциса абсол. збіжності", size=11, color="#059669", anchor="middle"))

    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'fig-dirichlet-convergence.svg')
    render(out_path, w, h, *frags, title="Області збіжності ряду Діріхле")
    print("Generated fig-dirichlet-convergence.svg successfully.")

def draw_convolution_duality():
    frags = []
    w, h = 800, 400
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="#cbd5e1", sw=1))
    
    frags.append(text(w / 2, 35, "Дуальність: Множення рядів Діріхле та Згортка арифметичних функцій", size=16, bold=True, color="#0f172a", anchor="middle"))
    
    # Left Box: Dirichlet Series
    b1, _, _ = textbox(210, 120, "Ряди Діріхле\nF(s) = ∑ a[n] / nˢ\nG(s) = ∑ b[n] / nˢ", size=13, fill="#eff6ff", stroke="#2563eb", color="#1e40af", bold=True, min_w=240)
    frags.append(b1)
    
    # Center Arrow: Multiplication
    frags.append(arrow(340, 120, 460, 120, color="#0284c7", sw=2.5))
    frags.append(text(400, 105, "F(s) · G(s)", size=14, bold=True, color="#0369a1", anchor="middle"))
    frags.append(text(400, 140, "Множення рядів", size=12, color="#0284c7", anchor="middle"))
    
    # Right Box: Resulting Series & Convolution
    b2, _, _ = textbox(590, 120, "Добуток H(s) = ∑ c[n] / nˢ\nc[n] = (a * b)(n)\n= ∑_{d|n} a[d] b[n/d]", size=13, fill="#f0fdf4", stroke="#16a34a", color="#166534", bold=True, min_w=240)
    frags.append(b2)
    
    # Connection line down to applications
    frags.append(line(w / 2, 190, w / 2, 220, color="#64748b", sw=1.5, dash="4,4"))
    
    # Bottom Panel: Classic Dirichlet Identities
    frags.append(rect(40, 225, 720, 145, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(w / 2, 248, "Фундаментальні тотожності згортки та рядів Діріхле:", size=13.5, bold=True, color="#334155", anchor="middle"))
    
    frags.append(text(200, 280, "ζ(s) · ζ(s) = ∑ d(n) / nˢ", size=13, bold=True, color="#0f172a", anchor="middle"))
    frags.append(text(200, 302, "(число дільників d(n) = (1 * 1)(n))", size=11, color="#64748b", anchor="middle"))
    
    frags.append(text(600, 280, "ζ(s) · (1 / ζ(s)) = 1", size=13, bold=True, color="#0f172a", anchor="middle"))
    frags.append(text(600, 302, "(функція Мебіуса: (1 * μ)(n) = ε(n))", size=11, color="#64748b", anchor="middle"))
    
    frags.append(text(400, 335, "ζ(s - 1) / ζ(s) = ∑ φ(n) / nˢ   |   (φ * 1)(n) = n", size=13, bold=True, color="#1e293b", anchor="middle"))
    
    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'fig-dirichlet-convolution.svg')
    render(out_path, w, h, *frags, title="Дуальність згортки Діріхле")
    print("Generated fig-dirichlet-convolution.svg successfully.")

def draw_l_functions():
    frags = []
    w, h = 800, 420
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="#cbd5e1", sw=1))
    
    frags.append(text(w / 2, 35, "Структура L-функцій Діріхле та теорема про прості числа в прогресіях", size=16, bold=True, color="#0f172a", anchor="middle"))
    
    # Top Box: Character and L-series
    b_top, _, _ = textbox(w / 2, 95, "Характер Діріхле χ (mod m)  →  L-ряд L(s, χ) = ∑ χ(n) / nˢ\nДобуток Ейлера: L(s, χ) = ∏_{p} (1 - χ(p) p⁻ˢ)⁻¹", size=13, fill="#faf5ff", stroke="#9333ea", color="#581c87", bold=True)
    frags.append(b_top)
    
    # Two Branch arrows
    frags.append(arrow(300, 140, 200, 190, color="#6b21a8", sw=2))
    frags.append(arrow(500, 140, 600, 190, color="#6b21a8", sw=2))
    
    # Left Branch: Principal character
    b_left, _, _ = textbox(200, 240, "Головний характер χ₀\nL(s, χ₀) має полюс у s = 1\nПоведінка аналогічна ζ(s)\nДає середню щільність", size=12, fill="#eff6ff", stroke="#1d4ed8", color="#1e40af", bold=True)
    frags.append(b_left)
    
    # Right Branch: Non-principal character
    b_right, _, _ = textbox(600, 240, "Неголовні характери χ ≠ χ₀\nL(s, χ) аналітична у s = 1\nКлючовий факт: L(1, χ) ≠ 0!\nВиключає деструктивну інтерференцію", size=12, fill="#fef2f2", stroke="#dc2626", color="#991b1b", bold=True)
    frags.append(b_right)
    
    # Converge arrows down to conclusion
    frags.append(arrow(200, 295, 340, 340, color="#475569", sw=2))
    frags.append(arrow(600, 295, 460, 340, color="#475569", sw=2))
    
    # Bottom Box: Dirichlet's 1837 Theorem
    b_bot, _, _ = textbox(w / 2, 365, "Теорема Діріхле (1837): ∑_{p ≡ a (mod m)} 1/p = ∞\nУ будь-якій арифметичній прогресії a + k·m (з НСД(a,m)=1) існує нескінченно багатьох простих чисел", size=12.5, fill="#ecfdf5", stroke="#059669", color="#065f46", bold=True)
    frags.append(b_bot)

    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'fig-dirichlet-l-functions.svg')
    render(out_path, w, h, *frags, title="L-функції Діріхле")
    print("Generated fig-dirichlet-l-functions.svg successfully.")

if __name__ == "__main__":
    draw_convergence_plane()
    draw_convolution_duality()
    draw_l_functions()
