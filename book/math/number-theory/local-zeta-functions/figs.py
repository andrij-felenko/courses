import sys
import os

# Add scripts directory to path (4 levels up from book/math/number-theory/local-zeta-functions)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, fitbox, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')


def generate_zeta_structure_overview():
    """Схема архітектури локальної дзета-функції: від кількості точок до раціональної форми."""
    width, height = 760, 420
    frags = []

    # Фон
    frags.append(rect(0, 0, width, height, fill=BG, stroke="none"))

    # Заголовок
    frags.append(text(width / 2, 26, "Архітектура та структура локальної Дзета-функції кривої C/𝔽_q", size=15, bold=True, color=INK))

    # Блок 1: Послідовність точок N_n (ліворуч)
    frags.append(rect(30, 65, 220, 320, fill="#f8fafc", stroke="#cbd5e1", rx=8, sw=1.5))
    frags.append(fitbox(45, 80, 190, 35, "Кількість точок N_n", fill="#e2e8f0", border="#94a3b8", color=INK, size=11, bold=True))
    frags.append(fitbox(40, 130, 200, 50, "Множина точок над 𝔽_qⁿ:\nN_n = #C(𝔽_qⁿ)", fill="#dbeafe", border="#3b82f6", color="#1e40af", size=10, bold=False))
    frags.append(fitbox(40, 195, 200, 65, "Підйом степеня:\nN₁ → N₂ → N₃ → ...\nЕкспоненційне зростання\nполя розширення", fill="#fef3c7", border="#f59e0b", color="#92400e", size=9, bold=False))
    frags.append(fitbox(40, 275, 200, 95, "Оцінка Хассе–Вейля:\n|N_n - (qⁿ + 1)| ≤ 2g·q^{n/2}\n\nРекурентне значення\nчерез власні числа", fill="#dcfce7", border="#22c55e", color="#15803d", size=9, bold=True))

    # Блок 2: Твірна функція та Ейлерів добуток (центр)
    frags.append(rect(270, 65, 220, 320, fill="#f8fafc", stroke="#cbd5e1", rx=8, sw=1.5))
    frags.append(fitbox(285, 80, 190, 35, "Твірна Дзета-функція Z(t)", fill="#e2e8f0", border="#94a3b8", color=INK, size=11, bold=True))
    frags.append(fitbox(280, 130, 200, 60, "Логарифмічний ряд:\nZ(C, t) = exp( ∑ N_n · tⁿ/n )\nЛогарифмічна похідна:\nt·d/dt[ln Z] = ∑ N_n·tⁿ", fill="#e0e7ff", border="#6366f1", color="#3730a3", size=9, bold=False))
    frags.append(fitbox(280, 205, 200, 70, "Ейлерів добуток:\nZ(C, t) = ∏_{x ∈ |C|} 1 / (1 - t^{deg(x)})\n\nДобуток по замкнених\nорбітах Галуа x", fill="#fae8ff", border="#c084fc", color="#6b21a8", size=9, bold=False))
    frags.append(fitbox(280, 290, 200, 80, "Гомоморфізм Фробеніуса:\nFrob_q: (x,y) ↦ (x^q, y^q)\n\nДія на когомології\nH¹(C, ℚ_ℓ)", fill="#ffe4e6", border="#fda4af", color="#9f1239", size=9, bold=False))

    # Блок 3: Раціональна форма P(t) (праворуч)
    frags.append(rect(510, 65, 220, 320, fill="#f8fafc", stroke="#cbd5e1", rx=8, sw=1.5))
    frags.append(fitbox(525, 80, 190, 35, "Раціональна форма", fill="#e2e8f0", border="#94a3b8", color=INK, size=11, bold=True))
    frags.append(fitbox(520, 130, 200, 65, "Дріб Теореми Рімана–Роха:\nZ(C, t) = P(t) / ((1-t)(1-qt))\n\nP(t) ∈ ℤ[t], deg P = 2g", fill="#dcfce7", border="#16a34a", color="#15803d", size=9, bold=True))
    frags.append(fitbox(520, 210, 200, 65, "Факторизація чисельника:\nP(t) = ∏_{i=1}^{2g} (1 - α_i·t)\n\nВласні значення α_i", fill="#dbeafe", border="#2563eb", color="#1e40af", size=9, bold=False))
    frags.append(fitbox(520, 290, 200, 80, "Аналог Гіпотези Рімана:\n|α_i| = √q для всіх i\n\nФункціональне рівняння:\nZ(1/(qt)) = (qt²)¹⁻ᵍ Z(t)", fill="#fef3c7", border="#d97706", color="#92400e", size=9, bold=True))

    # Зв'язуючі лінії та стрілки
    frags.append(line(250, 155, 270, 155, color="#2563eb", sw=2.0))
    frags.append(line(264, 150, 270, 155, color="#2563eb", sw=2.0))
    frags.append(line(264, 160, 270, 155, color="#2563eb", sw=2.0))

    frags.append(line(490, 160, 510, 160, color="#16a34a", sw=2.0))
    frags.append(line(504, 155, 510, 160, color="#16a34a", sw=2.0))
    frags.append(line(504, 165, 510, 160, color="#16a34a", sw=2.0))

    # Нижня зворотна лінія зв'язку власних чисел з N_n
    frags.append(line(520, 340, 490, 340, color="#9f1239", sw=1.5, dash="4,3"))
    frags.append(line(270, 340, 250, 340, color="#9f1239", sw=1.5, dash="4,3"))
    frags.append(line(256, 335, 250, 340, color="#9f1239", sw=1.5))
    frags.append(line(256, 345, 250, 340, color="#9f1239", sw=1.5))

    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, 'zeta-structure-overview.svg')
    render(out_path, width, height, *frags)
    print("Generated zeta-structure-overview.svg")


def generate_frobenius_eigenvalues():
    """Комплексна площина з колом радіуса √q та нулями P(t)."""
    width, height = 740, 380
    frags = []

    # Фон
    frags.append(rect(0, 0, width, height, fill=BG, stroke="none"))

    # Заголовок
    frags.append(text(width / 2, 24, "Розподіл власних значень Фробеніуса α_i на колі |α| = √q", size=15, bold=True, color=INK))

    # Ліва частина: Графік комплексної площини (cx=220, cy=200, R=110)
    cx, cy, R = 220, 200, 110

    # Сітка та осі
    frags.append(line(cx - 150, cy, cx + 150, cy, color="#cbd5e1", sw=1.2))
    frags.append(line(cx, cy - 140, cx, cy + 140, color="#cbd5e1", sw=1.2))
    frags.append(text(cx + 155, cy + 4, "Re", size=11, bold=True, color=MUTED))
    frags.append(text(cx - 10, cy - 142, "Im", size=11, bold=True, color=MUTED))

    # Коло |α| = √q
    frags.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="#f0fdf4" stroke="#22c55e" stroke-width="2.0" stroke-dasharray="5,3"/>')
    frags.append(text(cx + R - 15, cy - R + 25, "|α| = √q", size=11, bold=True, color="#15803d"))

    # Точки α1, α2 (спряжена пара для g=1)
    # α1 при куті 45 градусів (cos 45 = sin 45 ≈ 0.707)
    x1 = cx + R * 0.707
    y1 = cy - R * 0.707
    x2 = cx + R * 0.707
    y2 = cy + R * 0.707

    # Лінії від центру до точок
    frags.append(line(cx, cy, x1, y1, color="#2563eb", sw=1.5))
    frags.append(line(cx, cy, x2, y2, color="#2563eb", sw=1.5))

    # Точки на колі
    frags.append(circle(x1, y1, 6, fill="#3b82f6", stroke="#1d4ed8", sw=1.5))
    frags.append(circle(x2, y2, 6, fill="#3b82f6", stroke="#1d4ed8", sw=1.5))

    frags.append(text(x1 + 18, y1 - 6, "α₁ = √q · e^{iθ}", size=11, bold=True, color="#1e40af"))
    frags.append(text(x2 + 18, y2 + 12, "α₂ = ᾱ₁ = √q · e^{-iθ}", size=11, bold=True, color="#1e40af"))

    # Позначки на осях: √q та -√q
    frags.append(circle(cx + R, cy, 3, fill=INK, stroke=INK))
    frags.append(circle(cx - R, cy, 3, fill=INK, stroke=INK))
    frags.append(text(cx + R, cy + 18, "+√q", size=10, bold=False, color=INK))
    frags.append(text(cx - R, cy + 18, "-√q", size=10, bold=False, color=INK))

    # Позначка суми α1 + α2 = a (слід)
    frags.append(line(x1, y1, x1, cy, color="#dc2626", sw=1.2, dash="3,3"))
    frags.append(circle(x1, cy, 4, fill="#dc2626", stroke="#991b1b"))
    frags.append(text(x1 + 35, cy + 18, "a/2 = Re(α₁)", size=10, bold=True, color="#dc2626"))

    # Праворуч: Пояснювальна картка властивостей
    frags.append(rect(430, 50, 280, 300, fill="#f8fafc", stroke="#cbd5e1", rx=8, sw=1.5))
    frags.append(fitbox(445, 65, 250, 32, "Властивості нулів P(t)", fill="#e2e8f0", border="#94a3b8", color=INK, size=11, bold=True))

    frags.append(fitbox(445, 110, 250, 48, "1. Гіпотеза Рімана:\n|α_i| = √q для i = 1, ..., 2g\nНулі Z(s) мають Re(s) = 1/2", fill="#dcfce7", border="#22c55e", color="#15803d", size=9, bold=True))

    frags.append(fitbox(445, 170, 250, 48, "2. Спряження та дуальність:\nᾱ_i = q / α_i\nПари (α_i, q/α_i) формують P(t)", fill="#dbeafe", border="#3b82f6", color="#1e40af", size=9, bold=False))

    frags.append(fitbox(445, 230, 250, 52, "3. Слід та Дискримінант (g=1):\nα₁ + α₂ = a = q + 1 - N₁\nα₁·α₂ = q\nΔ = a² - 4q ≤ 0 (уявні корені)", fill="#fef3c7", border="#f59e0b", color="#92400e", size=9, bold=False))

    frags.append(fitbox(445, 292, 250, 45, "4. Формула для N_n:\nN_n = qⁿ + 1 - (α₁ⁿ + α₂ⁿ)", fill="#ffe4e6", border="#fda4af", color="#9f1239", size=9, bold=True))

    out_path = os.path.join(IMG_DIR, 'frobenius-eigenvalues.svg')
    render(out_path, width, height, *frags)
    print("Generated frobenius-eigenvalues.svg")


def generate_hasse_weil_strip():
    """Візуалізація коридору Хассе–Вейля для N_n при зростанні степеня n."""
    width, height = 760, 360
    frags = []

    # Фон
    frags.append(rect(0, 0, width, height, fill=BG, stroke="none"))

    # Заголовок
    frags.append(text(width / 2, 24, "Коридор обмежень Хассе–Вейля для кількості точок N_n над 𝔽_qⁿ", size=15, bold=True, color=INK))

    # Графічна область (x_start=80, y_start=50, w=640, h=250)
    gx, gy, gw, gh = 80, 50, 640, 250

    # Рамка графіка
    frags.append(rect(gx, gy, gw, gh, fill="#fafafa", stroke="#e2e8f0", rx=4, sw=1.0))

    # Вісь X (степінь n = 1, 2, 3, 4, 5)
    frags.append(line(gx, gy + gh - 30, gx + gw, gy + gh - 30, color="#94a3b8", sw=1.2))
    frags.append(text(gx + gw - 20, gy + gh - 10, "Степінь розширення n", size=10, bold=True, color=MUTED))

    # Вісь Y (Кількість точок N_n)
    frags.append(line(gx + 40, gy, gx + 40, gy + gh, color="#94a3b8", sw=1.2))
    frags.append(text(gx + 10, gy + 15, "N_n", size=11, bold=True, color=MUTED))

    # Точки за n = 1..5 для підняття кривої q=5, g=1
    n_x = [gx + 70 + i * 125 for i in range(5)]

    y_mid = [gy + 200, gy + 165, gy + 130, gy + 90, gy + 45]
    y_upper = [gy + 175, gy + 135, gy + 95, gy + 55, gy + 20]
    y_lower = [gy + 225, gy + 195, gy + 165, gy + 125, gy + 70]
    y_points = [gy + 215, gy + 150, gy + 140, gy + 75, gy + 35]

    # Верхня та нижня огинаючі криві
    poly_path = f"M {n_x[0]},{y_upper[0]} L " + " L ".join([f"{n_x[i]},{y_upper[i]}" for i in range(1, 5)]) + \
                " L " + " L ".join([f"{n_x[i]},{y_lower[i]}" for i in reversed(range(5))]) + " Z"

    frags.append(f'<path d="{poly_path}" fill="#dcfce7" stroke="none" opacity="0.75"/>')

    # Крива асимптоти qⁿ + 1 (пунктир)
    mid_path = "M " + " L ".join([f"{n_x[i]},{y_mid[i]}" for i in range(5)])
    frags.append(f'<path d="{mid_path}" fill="none" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4,4"/>')

    # Верхня межа
    up_path = "M " + " L ".join([f"{n_x[i]},{y_upper[i]}" for i in range(5)])
    frags.append(f'<path d="{up_path}" fill="none" stroke="#16a34a" stroke-width="1.8"/>')

    # Нижня межа
    low_path = "M " + " L ".join([f"{n_x[i]},{y_lower[i]}" for i in range(5)])
    frags.append(f'<path d="{low_path}" fill="none" stroke="#16a34a" stroke-width="1.8"/>')

    # Нанесення точок N_n та засічок на осях
    for i in range(5):
        frags.append(line(n_x[i], gy + gh - 35, n_x[i], gy + gh - 25, color="#64748b", sw=1.2))
        frags.append(text(n_x[i], gy + gh - 10, f"n = {i+1}", size=10, bold=False, color=INK))

        frags.append(line(n_x[i], y_lower[i], n_x[i], y_upper[i], color="#cbd5e1", sw=1.0, dash="2,2"))
        frags.append(circle(n_x[i], y_points[i], 5, fill="#dc2626", stroke="#991b1b", sw=1.5))

    # Легенда нижче
    frags.append(rect(100, 312, 560, 38, fill="#ffffff", stroke="#cbd5e1", rx=4, sw=1.0))

    frags.append(circle(120, 331, 4, fill="#dc2626", stroke="#991b1b"))
    frags.append(text(160, 335, "Точки N_n = #C(𝔽_qⁿ)", size=10, bold=True, color=INK))

    frags.append(line(240, 331, 270, 331, color="#16a34a", sw=2.0))
    frags.append(text(370, 335, "Межа Хассе–Вейля: qⁿ + 1 ± 2g·q^{n/2}", size=10, bold=True, color="#15803d"))

    frags.append(line(460, 331, 490, 331, color="#64748b", sw=1.5, dash="4,4"))
    frags.append(text(540, 335, "Асимптота qⁿ + 1", size=10, bold=False, color=MUTED))

    out_path = os.path.join(IMG_DIR, 'hasse-weil-strip.svg')
    render(out_path, width, height, *frags)
    print("Generated hasse-weil-strip.svg")


if __name__ == '__main__':
    generate_zeta_structure_overview()
    generate_frobenius_eigenvalues()
    generate_hasse_weil_strip()
