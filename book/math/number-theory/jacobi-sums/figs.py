import sys
import os
import math

# Add scripts directory to path (4 levels up from book/math/number-theory/jacobi-sums)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, fitbox, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')


def generate_jacobi_sum_circle():
    """Малює геометрію суми Якобі в комплексній площині: векторна сума фаз на колі радіуса √q."""
    width, height = 760, 440
    frags = []

    # Фон
    frags.append(rect(0, 0, width, height, fill=BG, stroke="none"))

    # Заголовок
    frags.append(text(width / 2, 26, "Геометрія суми Якобі J(χ₁, χ₂) в комплексній площині ℂ", size=15, bold=True, color=INK))

    # Ліва панель: Векторне додавання фаз
    frags.append(rect(30, 60, 340, 355, fill="#f8fafc", stroke="#cbd5e1", rx=8, sw=1.5))
    frags.append(fitbox(45, 72, 310, 32, "Векторний доданок: χ₁(t) · χ₂(1 - t)", fill="#e2e8f0", border="#94a3b8", color=INK, size=11, bold=True))

    # Центр комплексної площини ліворуч (cx=200, cy=250)
    cx1, cy1 = 200, 250
    # Вісі
    frags.append(line(cx1 - 130, cy1, cx1 + 130, cy1, color="#94a3b8", sw=1.0, dash="3,3"))
    frags.append(line(cx1, cy1 - 130, cx1, cy1 + 130, color="#94a3b8", sw=1.0, dash="3,3"))
    frags.append(text(cx1 + 135, cy1 + 4, "Re", size=10, color=MUTED, bold=True))
    frags.append(text(cx1 - 12, cy1 - 132, "Im", size=10, color=MUTED, bold=True))

    # Одиничне коло доданків
    frags.append(circle(cx1, cy1, 75, fill="none", stroke="#cbd5e1", sw=1.2))
    frags.append(text(cx1 + 55, cy1 - 55, "|χ(t)| = 1", size=9, color=MUTED))

    # Траєкторія векторної суми (траєкторія зсувів)
    angles = [0.4, 1.8, 3.2, 4.5, 5.7, 0.9, 2.3]
    lengths = [32, 28, 35, 30, 34, 31, 29]
    curr_x, curr_y = cx1, cy1
    for a, l in zip(angles, lengths):
        nx = curr_x + l * math.cos(a)
        ny = curr_y - l * math.sin(a)
        frags.append(line(curr_x, curr_y, nx, ny, color="#3b82f6", sw=1.5))
        frags.append(circle(nx, ny, 3, fill="#2563eb", stroke="none"))
        curr_x, curr_y = nx, ny

    # Підсумковий вектор J(χ₁, χ₂) (червоний)
    frags.append(line(cx1, cy1, curr_x, curr_y, color="#dc2626", sw=2.5))
    frags.append(circle(curr_x, curr_y, 4, fill="#dc2626", stroke="none"))
    frags.append(fitbox(curr_x + 8, curr_y - 22, 110, 24, "Вектор J(χ₁, χ₂)", fill="#fee2e2", border="#ef4444", color="#991b1b", size=9, bold=True))

    # Права панель: Коло радіуса √q
    frags.append(rect(390, 60, 340, 355, fill="#f8fafc", stroke="#cbd5e1", rx=8, sw=1.5))
    frags.append(fitbox(405, 72, 310, 32, "Фіксований модуль: |J(χ₁, χ₂)| = √q", fill="#dcfce7", border="#22c55e", color="#15803d", size=11, bold=True))

    cx2, cy2 = 560, 250
    # Вісі
    frags.append(line(cx2 - 130, cy2, cx2 + 130, cy2, color="#94a3b8", sw=1.0, dash="3,3"))
    frags.append(line(cx2, cy2 - 130, cx2, cy2 + 130, color="#94a3b8", sw=1.0, dash="3,3"))
    frags.append(text(cx2 + 135, cy2 + 4, "Re", size=10, color=MUTED, bold=True))
    frags.append(text(cx2 - 12, cy2 - 132, "Im", size=10, color=MUTED, bold=True))

    # Коло радіуса √q
    r_q = 95
    frags.append(circle(cx2, cy2, r_q, fill="#f0fdf4", stroke="#16a34a", sw=2.0))
    frags.append(line(cx2, cy2, cx2 + r_q * math.cos(0.7), cy2 - r_q * math.sin(0.7), color="#16a34a", sw=2.0))
    frags.append(circle(cx2 + r_q * math.cos(0.7), cy2 - r_q * math.sin(0.7), 5, fill="#15803d", stroke="none"))
    frags.append(fitbox(cx2 + 15, cy2 - 60, 80, 22, "Радіус = √q", fill="#dcfce7", border="#16a34a", color="#15803d", size=9, bold=True))

    # Кілька точок різних сум Якобі на колі
    for p_ang, lbl in zip([0.7, 2.1, 3.8, 5.2], ["J(χ¹,χ¹)", "J(χ¹,χ²)", "J(χ²,χ²)", "J(χ³,χ¹)"]):
        px = cx2 + r_q * math.cos(p_ang)
        py = cy2 - r_q * math.sin(p_ang)
        frags.append(circle(px, py, 4, fill="#7c3aed", stroke="none"))
        frags.append(text(px + (12 if px >= cx2 else -55), py + (4 if py >= cy2 else -8), lbl, size=9, color="#6b21a8", bold=True))

    # Пояснення внизу правої панелі
    frags.append(fitbox(405, 365, 310, 38, "Усі нетривіальні суми Якобі лежать строго на колі радіуса √q в ℂ", fill="#f3e8ff", border="#a855f7", color="#6b21a8", size=9, bold=False))

    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, 'jacobi-sum-circle.svg')
    render(out_path, width, height, *frags)
    print("Generated jacobi-sum-circle.svg")


def generate_jacobi_gauss_bridge():
    """Малює міст між сумами Гаусса, сумами Якобі та підрахунком точок на кривих Ферма."""
    width, height = 760, 420
    frags = []

    # Фон
    frags.append(rect(0, 0, width, height, fill=BG, stroke="none"))

    # Заголовок
    frags.append(text(width / 2, 24, "Структурний міст: Гаусс → Якобі → Точки на кривих uⁿ + vⁿ = 1", size=15, bold=True, color=INK))

    # Блок 1: Мультиплікативні характери та суми Гаусса
    frags.append(fitbox(30, 55, 210, 125, "1. Суми Гаусса g(χ, ψ)\n\nХарактери: χ₁, χ₂ ∈ X(𝔽_q*)\nСума: g(χ, ψ) = ∑ χ(x)ψ(x)\nМодуль: |g(χ, ψ)| = √q", fill="#dbeafe", border="#2563eb", color="#1e40af", size=10, bold=False))

    # Стрілка 1 -> 2
    frags.append(line(240, 117, 270, 117, color=LINE, sw=2.0))
    frags.append(line(264, 112, 270, 117, color=LINE, sw=2.0))
    frags.append(line(264, 122, 270, 117, color=LINE, sw=2.0))
    frags.append(fitbox(238, 92, 34, 18, "g₁g₂/g₁₂", fill="#eff6ff", border="#93c5fd", color="#1e40af", size=8, bold=True))

    # Блок 2: Суми Якобі
    frags.append(fitbox(270, 55, 220, 125, "2. Суми Якобі J(χ₁, χ₂)\n\nФормула: J = ∑_{u+v=1} χ₁(u)χ₂(v)\nФакторизація:\nJ(χ₁, χ₂) = g(χ₁)g(χ₂) / g(χ₁χ₂)\nМодуль: |J| = √q", fill="#f3e8ff", border="#7c3aed", color="#6b21a8", size=10, bold=True))

    # Стрілка 2 -> 3
    frags.append(line(490, 117, 520, 117, color=LINE, sw=2.0))
    frags.append(line(514, 112, 520, 117, color=LINE, sw=2.0))
    frags.append(line(514, 122, 520, 117, color=LINE, sw=2.0))
    frags.append(fitbox(488, 92, 34, 18, "∑ J(χⁱ,χʲ)", fill="#faf5ff", border="#d8b4fe", color="#6b21a8", size=8, bold=True))

    # Блок 3: Кількість розв'язків N
    frags.append(fitbox(520, 55, 210, 125, "3. Кількість точок N\n\nРівняння: xⁿ + yⁿ = 1 в 𝔽_q\nФормула розв'язків:\nN = q + ∑_{i,j=1}^{n-1} J(χⁱ, χʲ)\nТочна оцінка Вейля", fill="#dcfce7", border="#16a34a", color="#15803d", size=10, bold=True))

    # Пояснювальна нижня частина
    frags.append(rect(30, 200, 700, 200, fill="#f8fafc", stroke="#94a3b8", rx=8, sw=1.2))
    frags.append(fitbox(50, 212, 660, 28, "Математичний зв'язок та оцінки відхилення від головного члена q", fill="#e2e8f0", border="#94a3b8", color=INK, size=11, bold=True))

    frags.append(fitbox(45, 250, 325, 135, "Головний член та залишок:\nГоловний внесок у N дають тривіальні\nкомпоненти: q точок.\nЗалишковий член складається з (n-1)²\nсум Якобі J(χⁱ, χʲ).", fill="#fef2f2", border="#ef4444", color="#991b1b", size=10, bold=False))

    frags.append(fitbox(390, 250, 325, 135, "Точна оцінка Гіпотези Вейля:\nОскільки кожна ненульова сума має |J| = √q,\nмаємо точну межу відхилення:\n|N - q| ≤ (n - 1)(n - 2) √q\nдля гладких кривих рода g = (n-1)(n-2)/2!", fill="#f0fdf4", border="#22c55e", color="#166534", size=10, bold=True))

    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, 'jacobi-gauss-bridge.svg')
    render(out_path, width, height, *frags)
    print("Generated jacobi-gauss-bridge.svg")


def generate_stickelberger_decomposition():
    """Малює розклад Штікельберга для ідеалу (J(χ_a, χ_b)) у круговому полі Z[ζ_p]."""
    width, height = 740, 390
    frags = []

    # Фон
    frags.append(rect(0, 0, width, height, fill=BG, stroke="none"))

    # Заголовок
    frags.append(text(width / 2, 24, "Розклад Штікельберга ідеалу (J(χᵃ, χᵇ)) у круговому полі ℤ[ζ_p]", size=15, bold=True, color=INK))

    # Верхній блок: Ідеал суми Якобі
    frags.append(fitbox(40, 55, 660, 60, "Головний ідеал суми Якобі в кільці цілих кругового поля ℤ[ζ_p]:\n(J(χᵃ, χᵇ)) = ∏_{t ∈ (ℤ/pℤ)*} (𝔭_t)^{γ(t)}", fill="#dbeafe", border="#2563eb", color="#1e40af", size=11, bold=True))

    # Операційний блок зі стрілкою (дві лінії по обидва боки fitbox, щоб не перетинати текст)
    frags.append(line(370, 115, 370, 125, color=LINE, sw=2.0))
    frags.append(line(370, 149, 370, 165, color=LINE, sw=2.0))
    frags.append(line(365, 158, 370, 165, color=LINE, sw=2.0))
    frags.append(line(375, 158, 370, 165, color=LINE, sw=2.0))
    frags.append(fitbox(240, 125, 260, 24, "Показник γ(t) за теоремою Штікельбергера", fill="#f3e8ff", border="#7c3aed", color="#6b21a8", size=10, bold=True))

    # Нижні 3 розщеплені блоки
    frags.append(fitbox(40, 175, 205, 115, "1. Суми p-адичних цифр:\ns_p(k)\n\nСума цифр числа k у p-адичній системі числення", fill="#fef3c7", border="#d97706", color="#92400e", size=10, bold=False))

    frags.append(fitbox(265, 175, 210, 115, "2. Перенесення розрядів:\nγ(t) = ⌊(⟨t·a⟩ + ⟨t·b⟩)/p⌋\n\nЧисло перенесень одиниці при додаванні t·a + t·b mod p", fill="#dcfce7", border="#16a34a", color="#15803d", size=10, bold=True))

    frags.append(fitbox(495, 175, 205, 115, "3. Норма ідеалу:\nNorm((J)) = p^{s_p(a)+s_p(b)-s_p(a+b)}\n\nТочний p-адичний нормалізований модуль", fill="#e0e7ff", border="#4f46e5", color="#3730a3", size=10, bold=False))

    # Нижній узагальнювальний блок
    frags.append(rect(40, 305, 660, 65, fill="#faf5ff", stroke="#c084fc", rx=6, sw=1.2))
    frags.append(text(width / 2, 325, "Значення для законів взаємності та тесту простоти APR-CL:", size=11, bold=True, color="#6b21a8"))
    frags.append(text(width / 2, 350, "Факторизація Штікельбергера визначає точні лишкові степіні у кругових полях ℚ(ζ_m),\nщо дозволяє будувати квазіполіноміальний детермінований тест простоти!", size=10, color=INK))

    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, 'stickelberger-decomposition.svg')
    render(out_path, width, height, *frags)
    print("Generated stickelberger-decomposition.svg")


if __name__ == '__main__':
    generate_jacobi_sum_circle()
    generate_jacobi_gauss_bridge()
    generate_stickelberger_decomposition()
