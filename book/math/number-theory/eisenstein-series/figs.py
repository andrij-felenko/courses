import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import render, rect, line, text, circle, arrow, fitbox

def svg_path(d, fill="none", stroke="#333333", sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}/>'

def draw_lattice_sum(path):
    w, h = 800, 520
    frags = []

    # Title
    frags.append(text(w / 2, 28, "Сумування по вузлах решітки Λ = ℤτ + ℤ для ряду Ейзенштейна G₂ₖ(τ)", size=15, bold=True, color="#0f172a", anchor="middle"))

    # Left Box: Geometric Lattice on C (Complex plane)
    frags.append(rect(25, 55, 415, 440, fill="#f8fafc", stroke="#94a3b8", sw=1))
    frags.append(text(232, 80, "Комплексна решітка Λ у ℂ (τ = x + i·y)", size=13, color="#1e293b", bold=True, anchor="middle"))

    # Origin (0,0) at x=232, y=280
    ox, oy = 232, 280

    # Axes
    frags.append(line(45, oy, 420, oy, color="#cbd5e1", sw=1))
    frags.append(line(ox, 465, ox, 100, color="#cbd5e1", sw=1))
    frags.append(text(410, oy - 8, "Re", size=11, color="#64748b"))
    frags.append(text(ox + 8, 112, "Im", size=11, color="#64748b"))

    # Basis vectors: e1 = 1 (horizontal, 65px), e2 = tau = 0.4 + 1.25*i -> (28px, -75px)
    u_x, u_y = 65, 0
    v_x, v_y = 28, -75

    # Draw grid lines for m, n in [-3, 3]
    for m in range(-3, 4):
        x1 = ox + m * u_x - 3 * v_x
        y1 = oy + m * u_y - 3 * v_y
        x2 = ox + m * u_x + 3 * v_x
        y2 = oy + m * u_y + 3 * v_y
        frags.append(line(x1, y1, x2, y2, color="#e2e8f0", sw=1))

    for n in range(-3, 4):
        x1 = ox - 3 * u_x + n * v_x
        y1 = oy - 3 * u_y + n * v_y
        x2 = ox + 3 * u_x + n * v_x
        y2 = oy + 3 * u_y + n * v_y
        frags.append(line(x1, y1, x2, y2, color="#e2e8f0", sw=1))

    # Shell concentric zones
    frags.append(svg_path(f"M {ox+68},{oy} A 68,68 0 1,1 {ox-68},{oy} A 68,68 0 1,1 {ox+68},{oy}", fill="none", stroke="#cbd5e1", sw=1, dash="3,3"))
    frags.append(svg_path(f"M {ox+135},{oy} A 135,135 0 1,1 {ox-135},{oy} A 135,135 0 1,1 {ox+135},{oy}", fill="none", stroke="#e2e8f0", sw=1, dash="3,3"))

    # Lattice points
    for m in range(-3, 4):
        for n in range(-3, 4):
            px = ox + m * u_x + n * v_x
            py = oy + m * u_y + n * v_y
            if m == 0 and n == 0:
                frags.append(circle(px, py, 6, fill="#ef4444", stroke="#b91c1c", sw=1.5))
                frags.append(text(px + 10, py + 16, "(0,0) виключено", size=10, color="#b91c1c", bold=True))
            else:
                r_sq = m*m + n*n
                if r_sq <= 2:
                    col = "#2563eb"
                elif r_sq <= 5:
                    col = "#0284c7"
                else:
                    col = "#64748b"
                frags.append(circle(px, py, 4, fill=col, stroke="#1e293b", sw=1))

    # Basis vectors arrows
    frags.append(arrow(ox, oy, ox + u_x, oy + u_y, color="#16a34a", sw=2.5))
    frags.append(text(ox + u_x / 2, oy + 18, "1", size=12, color="#15803d", bold=True))

    frags.append(arrow(ox, oy, ox + v_x, oy + v_y, color="#d97706", sw=2.5))
    frags.append(text(ox + v_x - 18, oy + v_y / 2, "τ", size=12, color="#b45309", bold=True))

    # Generic point label
    m_test, n_test = 2, 1
    pt_x = ox + m_test * u_x + n_test * v_x
    pt_y = oy + m_test * u_y + n_test * v_y
    frags.append(line(ox, oy, pt_x, pt_y, color="#2563eb", sw=1.5, dash="2,2"))
    frags.append(text(pt_x + 8, pt_y - 4, "ω = 2 + τ", size=11, color="#1d4ed8", bold=True))

    # Right Box: Analytical Properties & Convergence
    frags.append(rect(455, 55, 320, 440, fill="#f8fafc", stroke="#94a3b8", sw=1))
    frags.append(text(615, 80, "Аналітичний збіг і вагові класи", size=13, color="#1e293b", bold=True, anchor="middle"))

    s1 = "Формула ряду G₂ₖ(τ)\nG₂ₖ(τ) = ∑' 1 / (m·τ + n)²ₖ\nде ∑' — сумування по всім (m, n) ∈ ℤ² \\ {(0,0)}.\nПарна вага 2k забезпечує G₂ₖ ≠ 0."
    frags.append(fitbox(465, 95, 300, 100, s1, size=11, fill="#ffffff", stroke="#cbd5e1"))

    s2 = "Абсолютна збіжність (2k ≥ 4)\n● Оцінка ряду: ∑ 1 / |m·τ + n|²ₖ\n● На сфері радіуса R: ~ R елементів, кожен ~ 1 / R²ₖ.\n● Інтеграл: ∫ R / R²ₖ dR < ∞ ⇔ 2k > 2.\n● Для k ≥ 2 ряд збігається абсолютно\n  і рівномірно на компактних підмножинах ℍ."
    frags.append(fitbox(465, 205, 300, 130, s2, size=11, fill="#eff6ff", stroke="#93c5fd"))

    s3 = "Умовна збіжність k = 1 (G₂)\n● Для k = 1 (вага 2): ряд збігається лише УМОВНО!\n● Порядок сумування має значення:\n  lim_N ∑_{-N}^N (∑_{n} 1/(m·τ+n)²)\n● Порушується інваріантність SL(2,ℤ):\n  G₂(-1/τ) = τ²·G₂(τ) - 2π·i·τ.\n● Утворює КВАЗІМОДУЛЯРНУ форму."
    frags.append(fitbox(465, 345, 300, 140, s3, size=11, fill="#fef2f2", stroke="#fca5a5"))

    return render(path, w, h, *frags)

def draw_ring_structure(path):
    w, h = 800, 520
    frags = []

    # Title
    frags.append(text(w / 2, 28, "Структура кільця модулярних форм 𝕄*(SL(2,ℤ)) = ℂ[E₄, E₆]", size=15, bold=True, color="#0f172a", anchor="middle"))

    # Generators Box
    frags.append(rect(30, 60, 355, 200, fill="#eff6ff", stroke="#3b82f6", sw=1.5))
    frags.append(text(207, 85, "Фундаментальні твірні (Generators)", size=13, color="#1e3a8a", bold=True, anchor="middle"))

    # E4 box
    s_e4 = "E₄(τ)  (Вага 4)\nE₄ = 1 + 240·∑ σ₃(n)·qⁿ\nG₄(τ) = (π⁴ / 45)·E₄\nНуль у точці τ = e^{2πi/3}\nпростий нуль"
    frags.append(fitbox(45, 100, 155, 145, s_e4, size=11, fill="#ffffff", stroke="#93c5fd"))

    # E6 box
    s_e6 = "E₆(τ)  (Вага 6)\nE₆ = 1 - 504·∑ σ₅(n)·qⁿ\nG₆(τ) = (2π⁶ / 945)·E₆\nНуль у точці τ = i\nпростий нуль"
    frags.append(fitbox(215, 100, 155, 145, s_e6, size=11, fill="#ffffff", stroke="#93c5fd"))

    # Higher weights combination box
    frags.append(rect(415, 60, 355, 200, fill="#f0fdf4", stroke="#22c55e", sw=1.5))
    frags.append(text(592, 85, "Градуйоване кільце 𝕄₂ₖ = ℂ · E₄ᵃ E₆ᵇ", size=13, color="#14532d", bold=True, anchor="middle"))

    s_ring = "Базиси модулярних форм за вагою 2k\n● Вага 0:  ℂ (константи)\n● Вага 4:  ℂ·E₄       ● Вага 6:  ℂ·E₆\n● Вага 8:  ℂ·E₄²      ● Вага 10: ℂ·E₄·E₆\n● Вага 12: ℂ·E₄³ ⊕ ℂ·E₆² = ℂ·E₁₂ ⊕ ℂ·Δ\n● dim 𝕄₂ₖ = ⌊2k/12⌋ + (1 якщо 2k ≢ 2 mod 12)"
    frags.append(fitbox(430, 100, 325, 145, s_ring, size=11, fill="#ffffff", stroke="#bbf7d0"))

    # Arrows down to Discriminant and J-invariant
    frags.append(arrow(207, 260, 207, 285, color="#3b82f6", sw=2))
    frags.append(arrow(592, 260, 592, 285, color="#22c55e", sw=2))

    # Cusp Form / Discriminant Box
    frags.append(rect(30, 290, 355, 205, fill="#faf5ff", stroke="#a855f7", sw=1.5))
    frags.append(text(207, 312, "Параболічна форма Δ(τ) (Cusp Form)", size=13, color="#581c87", bold=True, anchor="middle"))

    s_disc = "Модулярний дискримінант Δ(τ) (Вага 12)\nΔ(τ) = (E₄³ - E₆²) / 1728\n● Перший член q-розкладу: Δ(τ) = q + O(q²)\n● Не має нулів у півплощині ℍ (лише в i∞).\n● Твірний елемент простору параболічних форм 𝕊₁₂.\n● Добуток Ейлера: Δ(τ) = q·∏_{n=1}^∞ (1 - qⁿ)²⁴\n● Коефіцієнти: τ(n) — функція Рамануджана."
    frags.append(fitbox(45, 325, 325, 155, s_disc, size=11, fill="#ffffff", stroke="#e9d5ff"))

    # Invariant J Box & Elliptic Curves
    frags.append(rect(415, 290, 355, 205, fill="#fff7ed", stroke="#f97316", sw=1.5))
    frags.append(text(592, 312, "Арифметика та інваріанти еліптичних кривих", size=13, color="#7c2d12", bold=True, anchor="middle"))

    s_j = "j-інваріант Клейна та рівняння Вейєрштрасса\nj(τ) = 1728 · E₄³ / (E₄³ - E₆²) = E₄³ / Δ\n● Безрозмірна інваріантна функція ваги 0.\n● Рівняння еліптичної кривої E_τ: y² = 4x³ - g₂x - g₃\n  де g₂ = 60·G₄(τ), g₃ = 140·G₆(τ).\n● Дві криві E_τ₁ ≅ E_τ₂ ізоморфні ⇔ j(τ₁) = j(τ₂).\n● Розклад: j(q) = 1/q + 744 + 196884·q + 21493760·q² + ..."
    frags.append(fitbox(430, 325, 325, 155, s_j, size=11, fill="#ffffff", stroke="#fed7aa"))

    return render(path, w, h, *frags)

def draw_fourier_convergence(path):
    w, h = 800, 520
    frags = []

    # Title
    frags.append(text(w / 2, 28, "Аналітична структура q-розкладу та арифметичні застосування рядів Ейзенштейна", size=15, bold=True, color="#0f172a", anchor="middle"))

    # Top Left: Normalization & Bernoulli Numbers
    frags.append(rect(30, 60, 355, 215, fill="#f8fafc", stroke="#94a3b8", sw=1))
    frags.append(text(207, 85, "Нормалізація та числа Бернуллі B₂ₖ", size=13, color="#1e293b", bold=True, anchor="middle"))

    s_norm = "Від G₂ₖ(τ) до нормалізованого ряда E₂ₖ(τ)\n● Нормалізація: E₂ₖ(τ) = G₂ₖ(τ) / (2·ζ(2k))\n● Значення ζ-функції: ζ(2k) = (2π)²ₖ·(-1)ᵏ⁺¹·B₂ₖ / (2·(2k)!)\n● Загальна формула q-розкладу (q = e^{2πiτ}):\n  E₂ₖ(τ) = 1 - (4k / B₂ₖ) · ∑_{n=1}^∞ σ₂ₖ₋₁(n)·qⁿ\n● Звідси коефіцієнти завжди є РАЦІОНАЛЬНИМИ\n  і цілими для E₄, E₆, E₈, E₁₀, E₁₂, E₁₄!"
    frags.append(fitbox(45, 98, 325, 162, s_norm, size=11, fill="#ffffff", stroke="#cbd5e1"))

    # Top Right: Divisor Functions Table
    frags.append(rect(415, 60, 355, 215, fill="#f0f9ff", stroke="#0284c7", sw=1))
    frags.append(text(592, 85, "Мультиплікативна сума дільників σₖ(n)", size=13, color="#0369a1", bold=True, anchor="middle"))

    s_table = "Значення σ₂ₖ₋₁(n) = ∑_{d|n} d²ₖ⁻¹\nn  │ σ₁(n)   │ σ₃(n)   │ σ₅(n)    │ σ₇(n)\n───┼─────────┼─────────┼──────────┼──────────\n1  │ 1       │ 1       │ 1        │ 1\n2  │ 3       │ 9       │ 33       │ 129\n3  │ 4       │ 28      │ 244      │ 2188\n4  │ 7       │ 73      │ 1057     │ 16513\n5  │ 6       │ 126     │ 3126     │ 78126\n● Мультиплікативність: σₖ(m·n) = σₖ(m)·σₖ(n) при gcd(m,n)=1"
    frags.append(fitbox(430, 98, 325, 162, s_table, size=11, fill="#ffffff", stroke="#bae6fd"))

    # Bottom Box: Arithmetic Applications
    frags.append(rect(30, 290, 740, 205, fill="#fafaf9", stroke="#78716c", sw=1))
    frags.append(text(400, 312, "Представлення чисел сумами квадратів r₄(n) та r₈(n)", size=13, color="#292524", bold=True, anchor="middle"))

    s_app1 = "Суми 4 квадратів r₄(n) (Теорема Якобі)\n● Тета-серія ϑ(τ)⁴ ∈ 𝕄₂(Γ₀(4)) виражається\n  через ряд Ейзенштейна E₂(τ) зі зсувом:\n● r₄(n) = 8·∑_{d|n, 4∤d} d = 8·σ₁(n) для непарних n.\n● Точна комбінаторна формула без залишкових\n  членів випливає з тотожностей Ейзенштейна!"
    frags.append(fitbox(45, 330, 340, 150, s_app1, size=11, fill="#ffffff", stroke="#e7e5e4"))

    s_app2 = "Суми 8 квадратів r₈(n)\n● ϑ(τ)⁸ ∈ 𝕄₄(Γ₀(2)) виражається через E₄(τ):\n● r₈(n) = 16·∑_{d|n} (-1)^{n - d} · d³\n● Тотожність для E₈ = E₄² дає арифметичний співвідношення:\n  σ₇(n) = σ₃(n) + 120·∑_{m=1}^{n-1} σ₃(m)·σ₃(n-m).\n● Глибокий зв'язь між мультиплікативністю та формами."
    frags.append(fitbox(415, 330, 340, 150, s_app2, size=11, fill="#ffffff", stroke="#e7e5e4"))

    return render(path, w, h, *frags)

def main():
    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)

    draw_lattice_sum(os.path.join(out_dir, 'eisenstein-lattice-sum.svg'))
    draw_ring_structure(os.path.join(out_dir, 'eisenstein-ring-structure.svg'))
    draw_fourier_convergence(os.path.join(out_dir, 'eisenstein-fourier-convergence.svg'))

    print("SVG figures generated successfully.")

if __name__ == '__main__':
    main()
