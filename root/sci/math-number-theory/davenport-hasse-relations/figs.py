import sys
import os

# Add scripts directory to path (4 levels up from book/math/number-theory/davenport-hasse-relations)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, fitbox, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')


def generate_davenport_hasse_lifting():
    """Малює схему підйому характерів та сум Гаусса при розширенні полів F_q^s / F_q."""
    width, height = 760, 420
    frags = []

    # Фон
    frags.append(rect(0, 0, width, height, fill=BG, stroke="none"))

    # Заголовок
    frags.append(text(width / 2, 26, "Структура підйому Девенпорта–Хассе для розширення 𝔽_qˢ / 𝔽_q", size=15, bold=True, color=INK))

    # Базове поле F_q (ліворуч)
    frags.append(rect(40, 65, 310, 315, fill="#f8fafc", stroke="#cbd5e1", rx=8, sw=1.5))
    frags.append(fitbox(55, 80, 280, 35, "Базове поле 𝔽_q (характеристика p)", fill="#e2e8f0", border="#94a3b8", color=INK, size=11, bold=True))

    frags.append(fitbox(60, 130, 270, 45, "Мультиплікативний характер:\nχ : 𝔽_q* → ℂ*", fill="#dbeafe", border="#3b82f6", color="#1e40af", size=10, bold=False))
    frags.append(fitbox(60, 190, 270, 45, "Адитивний характер:\nψ : 𝔽_q → ℂ*", fill="#e0e7ff", border="#6366f1", color="#3730a3", size=10, bold=False))

    frags.append(fitbox(60, 255, 270, 55, "Сума Гаусса в 𝔽_q:\ng(χ, ψ) = ∑_{x ∈ 𝔽_q} χ(x) ψ(x)\nМодуль: |g(χ, ψ)| = √q", fill="#dcfce7", border="#22c55e", color="#15803d", size=10, bold=True))

    frags.append(fitbox(60, 325, 270, 40, "Базовий степінь:\n(g(χ, ψ))ˢ (піднесено до s)", fill="#fef3c7", border="#f59e0b", color="#92400e", size=10, bold=False))

    # Розширене поле F_q^s (праворуч)
    frags.append(rect(410, 65, 310, 315, fill="#f8fafc", stroke="#cbd5e1", rx=8, sw=1.5))
    frags.append(fitbox(425, 80, 280, 35, "Розширене поле 𝔽_qˢ (степінь s)", fill="#e2e8f0", border="#94a3b8", color=INK, size=11, bold=True))

    frags.append(fitbox(430, 130, 270, 45, "Піднятий мультиплікативний характер:\nχ' = χ ∘ Norm_{𝔽_qˢ/𝔽_q}", fill="#dbeafe", border="#3b82f6", color="#1e40af", size=10, bold=False))
    frags.append(fitbox(430, 190, 270, 45, "Піднятий адитивний характер:\nψ' = ψ ∘ Tr_{𝔽_qˢ/𝔽_q}", fill="#e0e7ff", border="#6366f1", color="#3730a3", size=10, bold=False))

    frags.append(fitbox(430, 255, 270, 55, "Піднята сума Гаусса в 𝔽_qˢ:\ng(χ', ψ') = ∑_{y ∈ 𝔽_qˢ} χ'(y) ψ'(y)\nМодуль: |g(χ', ψ')| = (√q)ˢ = qˢ/²", fill="#dcfce7", border="#22c55e", color="#15803d", size=10, bold=True))

    frags.append(fitbox(430, 325, 270, 40, "Піднята сума через базову:\ng(χ', ψ') = (-1)ˢ⁻¹ (g(χ, ψ))ˢ", fill="#fecdd3", border="#e11d48", color="#9f1239", size=10, bold=True))

    # Зв'язуючі стрілки
    # Стрілка Norm
    frags.append(line(430, 152, 330, 152, color="#2563eb", sw=1.5, dash="4,3"))
    frags.append(fitbox(335, 135, 90, 18, "Norm_{𝔽_qˢ/𝔽_q}", fill="#eff6ff", border="#93c5fd", color="#1e40af", size=9))

    # Стрілка Trace
    frags.append(line(430, 212, 330, 212, color="#4f46e5", sw=1.5, dash="4,3"))
    frags.append(fitbox(335, 195, 90, 18, "Tr_{𝔽_qˢ/𝔽_q}", fill="#eef2ff", border="#a5b4fc", color="#3730a3", size=9))

    # Нижня стрілка співвідношення
    frags.append(line(330, 345, 430, 345, color="#dc2626", sw=2.0))
    frags.append(line(424, 340, 430, 345, color="#dc2626", sw=2.0))
    frags.append(line(424, 350, 430, 345, color="#dc2626", sw=2.0))

    # Знак (-1)^(s-1)
    frags.append(fitbox(335, 330, 90, 30, "Множник знаку:\n(-1)ˢ⁻¹", fill="#ffe4e6", border="#fda4af", color="#9f1239", size=9, bold=True))

    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, 'davenport-hasse-lifting.svg')
    render(out_path, width, height, *frags)
    print("Generated davenport-hasse-lifting.svg")


def generate_multiplicative_relation():
    """Малює розклад мультиплікативного співвідношення Девенпорта–Хассе."""
    width, height = 740, 380
    frags = []

    # Фон
    frags.append(rect(0, 0, width, height, fill=BG, stroke="none"))

    # Заголовок
    frags.append(text(width / 2, 24, "Мультиплікативне співвідношення Девенпорта–Хассе (m | q - 1)", size=15, bold=True, color=INK))

    # Верхній блок: Добуток зсунутих сум Гаусса
    frags.append(fitbox(40, 55, 660, 60, "Ліва частина: Добуток m сум Гаусса зі зсувом характерів на θᵃ (орбіта порядків m)\n∏_{a=0}^{m-1} g(χ · θᵃ, ψ) = g(χ, ψ) · g(χ·θ, ψ) · ... · g(χ·θᵐ⁻¹, ψ)", fill="#dbeafe", border="#2563eb", color="#1e40af", size=11, bold=True))

    # Операційний блок зі стрілкою
    frags.append(line(370, 115, 370, 160, color=LINE, sw=2.0))
    frags.append(line(365, 153, 370, 160, color=LINE, sw=2.0))
    frags.append(line(375, 153, 370, 160, color=LINE, sw=2.0))
    frags.append(fitbox(240, 125, 260, 24, "Тотожність Девенпорта–Хассе", fill="#f3e8ff", border="#7c3aed", color="#6b21a8", size=10, bold=True))

    # Нижні 3 розщеплені блоки (Права частина)
    frags.append(fitbox(40, 175, 205, 110, "1. Зсув аргументу:\nχ(m⁻ᵐ)\n\nХарактер χ від скаляра m⁻ᵐ в 𝔽_q*", fill="#fef3c7", border="#d97706", color="#92400e", size=10, bold=False))

    frags.append(fitbox(265, 175, 210, 110, "2. Згорнута сума:\ng(χᵐ, ψ)\n\nСума Гаусса від m-го степеня характеру χ", fill="#dcfce7", border="#16a34a", color="#15803d", size=10, bold=True))

    frags.append(fitbox(495, 175, 205, 110, "3. Нормувальний константний добуток:\n∏_{a=1}^{m-1} g(θᵃ, ψ)\n\nДобуток нетривіальних m-сум", fill="#e0e7ff", border="#4f46e5", color="#3730a3", size=10, bold=False))

    # Нижній узагальнювальний блок: Аналогія з Гамма-функцією
    frags.append(rect(40, 300, 660, 60, fill="#faf5ff", stroke="#c084fc", rx=6, sw=1.2))
    frags.append(text(width / 2, 322, "Аналогія з формулою множення Гаусса для Γ-функції Ейлера:", size=11, bold=True, color="#6b21a8"))
    frags.append(text(width / 2, 345, "∏_{k=0}^{m-1} Γ((x + k)/m) = (2π)^{(m-1)/2} · m^{1/2 - x} · Γ(x)   ↔   Суми Гаусса як p-адичні Γ-значення", size=10, color=INK))

    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, 'multiplicative-relation.svg')
    render(out_path, width, height, *frags)
    print("Generated multiplicative-relation.svg")


def generate_gauss_jacobi_duality():
    """Малює дуальність сум Гаусса, Якобі та рахунок точок на кривих Ферма."""
    width, height = 760, 420
    frags = []

    # Фон
    frags.append(rect(0, 0, width, height, fill=BG, stroke="none"))

    # Заголовок
    frags.append(text(width / 2, 24, "Трансляція: Суми Гаусса → Суми Якобі → Точки на алгебраїчних кривих", size=15, bold=True, color=INK))

    # Блок 1: Суми Гаусса
    frags.append(fitbox(30, 55, 210, 115, "1. Суми Гаусса g(χ, ψ)\n\nОб'єкти на 𝔽_qˢ.\nПідйом через Девенпорт–Хассе:\ng(χ', ψ') = (-1)ˢ⁻¹ g(χ, ψ)ˢ", fill="#dbeafe", border="#2563eb", color="#1e40af", size=10, bold=False))

    # Стрілка 1 -> 2
    frags.append(line(240, 112, 270, 112, color=LINE, sw=2.0))
    frags.append(line(264, 107, 270, 112, color=LINE, sw=2.0))
    frags.append(line(264, 117, 270, 112, color=LINE, sw=2.0))

    # Блок 2: Суми Якобі
    frags.append(fitbox(270, 55, 220, 115, "2. Суми Якобі J(χ₁, χ₂)\n\nФакторизація через Гаусса:\nJ = g(χ₁)g(χ₂) / g(χ₁χ₂)\nПідйом:\nJ' = (-1)ˢ⁻¹ Jˢ", fill="#f3e8ff", border="#7c3aed", color="#6b21a8", size=10, bold=False))

    # Стрілка 2 -> 3
    frags.append(line(490, 112, 520, 112, color=LINE, sw=2.0))
    frags.append(line(514, 107, 520, 112, color=LINE, sw=2.0))
    frags.append(line(514, 117, 520, 112, color=LINE, sw=2.0))

    # Блок 3: Кількість точок N_s
    frags.append(fitbox(520, 55, 210, 115, "3. Точки на кривих N_s\n\nРозв'язки xⁿ + yⁿ = 1 в 𝔽_qˢ:\nN_s = qˢ + 1 + ∑ α_iˢ\nα_i — власні значення", fill="#dcfce7", border="#16a34a", color="#15803d", size=10, bold=True))

    # Пояснювальна панель під ними
    frags.append(rect(30, 195, 700, 205, fill="#f8fafc", stroke="#94a3b8", rx=8, sw=1.2))
    frags.append(fitbox(50, 205, 660, 28, "Наслідки для Діофантової геометрії та Дзета-функції Вейля Z(T)", fill="#e2e8f0", border="#94a3b8", color=INK, size=11, bold=True))

    frags.append(fitbox(45, 245, 325, 140, "Раціональність Дзета-функції:\nФормула підйому гарантує,\nщо N_s є сумою s-х степенів\nскінченного числа чисел α_i.\nЗвідси Z(T) = P(T) / ((1-T)(1-qT))\nє раціональною функцією!", fill="#fef2f2", border="#ef4444", color="#991b1b", size=10, bold=False))

    frags.append(fitbox(390, 245, 325, 140, "Гіпотеза Рімана (Вейль):\nМодуль суми Гаусса |g(χ, ψ)| = √q\nзадає величину власних значень:\n|α_i| = q¹/²\nЦе доводить аналог Гіпотези\nРімана для кривих над 𝔽_q!", fill="#f0fdf4", border="#22c55e", color="#166534", size=10, bold=False))

    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, 'gauss-jacobi-duality.svg')
    render(out_path, width, height, *frags)
    print("Generated gauss-jacobi-duality.svg")


if __name__ == '__main__':
    generate_davenport_hasse_lifting()
    generate_multiplicative_relation()
    generate_gauss_jacobi_duality()
