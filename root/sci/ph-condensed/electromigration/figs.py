# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Механізм передачі імпульсу електронного вітру
# ════════════════════════════════════════════════════════════════════════════
def fig_electron_wind():
    W, H = 820, 420
    f = []

    # Заголовок та тло
    f.append(rect(15, 15, W - 30, H - 30, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    f.append(text(W / 2, 42, "Баланс сил на активованому іоні кристалічної ґратки", size=15, bold=True, color=INK))

    # Напрямок електричного поля та потенціалів
    f.append(rect(60, 68, 90, 30, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    f.append(text(105, 88, "Катод (+)", size=12, bold=True, color=POS))

    f.append(rect(670, 68, 90, 30, fill="#dbeafe", stroke=NEG, sw=1.5, rx=4))
    f.append(text(715, 88, "Анод (-)", size=12, bold=True, color=NEG))

    # Стрілка напруженості електричного поля E
    f.append(arrow(160, 83, 660, 83, color=MUTED, sw=1.5))
    f.append(text(410, 77, "Електричне поле E (напруженість)", size=11, color=MUTED, italic=True))

    # Кристалічна ґратка з іонами
    grid_y = [150, 220, 290, 360]
    grid_x = [120, 200, 280, 360, 440, 520, 600, 680]

    for gx in grid_x:
        for gy in grid_y:
            if gx == 440 and gy == 220:
                continue # місце активованого іона / вакансії
            f.append(circle(gx, gy, 14, fill="#e2e8f0", stroke="#64748b", sw=1.5))
            f.append(text(gx, gy + 4, "M⁺", size=10, color="#475569", bold=True))

    # Вакансія поблизу активованого іона
    f.append(circle(520, 220, 14, fill="#ffffff", stroke=POS, sw=2))
    f.append(text(520, 224, "V", size=11, color=POS, bold=True))

    # Активований іон (повишений енергетичний стан)
    f.append(circle(440, 220, 16, fill="#fef08a", stroke="#d97706", sw=2.5))
    f.append(text(440, 225, "M⁺*", size=12, color="#92400e", bold=True))

    # Електрони провідності (дрейф від катода до анода)
    electrons = [(220, 210), (250, 235), (310, 200), (340, 225), (370, 210)]
    for ex, ey in electrons:
        f.append(circle(ex, ey, 7, fill=NEG, stroke="#1e40af", sw=1))
        f.append(text(ex, ey + 3, "e⁻", size=9, color="#ffffff", bold=True))
        f.append(arrow(ex + 8, ey, ex + 24, ey, color=NEG, sw=1.5))

    # Розсіювання електронів на іоні (пунктирні стрілки відскоку)
    f.append(svg_path("M 400 220 L 430 220", stroke=NEG, sw=2))
    f.append(svg_path("M 440 220 L 465 195", stroke=NEG, sw=1.5, dash="2 2"))
    f.append(svg_path("M 440 220 L 465 245", stroke=NEG, sw=1.5, dash="2 2"))

    # Вектори сил на іон M+*
    # 1. Пряма електростатична сила F_direct (до катода, ліворуч)
    f.append(arrow(440, 175, 350, 175, color=POS, sw=2.5))
    f.append(text(395, 165, "F_direct (+Z_d · e · E)", size=11, bold=True, color=POS))

    # 2. Сила електронного вітру F_wind (до анода, праворуч)
    f.append(arrow(440, 265, 590, 265, color=NEG, sw=2.5))
    f.append(text(515, 282, "F_wind (-|Z_w*| · e · E)", size=11, bold=True, color=NEG))

    # 3. Сумарна сила F_net
    f.append(arrow(440, 315, 560, 315, color=FIELD, sw=3))
    f.append(text(500, 335, "F_net = Z* · e · E (Z* < 0)", size=12, bold=True, color=FIELD))

    # Пояснювальний підпис під іоном
    f.append(text(440, 385, "Активований іон стрибає у вакансію під дією F_net у напрямку електронного вітру", size=11.5, color=INK))

    render(os.path.join(OUT, "electron-wind.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Дивергенція потоку маси: зародження порожнин та пагорбів
# ════════════════════════════════════════════════════════════════════════════
def fig_void_hillock():
    W, H = 820, 440
    f = []

    # Заголовок
    f.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(W / 2, 42, "Локальна дивергенція потоку маси ∇·J у мікроструктурі провідника", size=15, bold=True, color=INK))

    # Провідник (металева лінія)
    f.append(rect(60, 100, 700, 180, fill="#f1f5f9", stroke="#475569", sw=2, rx=4))

    # Потік електронів (ліворуч праворуч)
    f.append(arrow(80, 75, 740, 75, color=NEG, sw=2))
    f.append(text(410, 68, "Потік електронів та атомний транспорт J_wind →", size=11.5, bold=True, color=NEG))

    # Межі зерен у провіднику
    # Потрійний стик 1 (дивергенція > 0, вихід маси > приплив -> Void)
    f.append(line(240, 100, 240, 190, color="#64748b", sw=2))
    f.append(line(240, 190, 140, 280, color="#64748b", sw=2))
    f.append(line(240, 190, 320, 280, color="#64748b", sw=2))

    # Потрійний стик 2 (дивергенція < 0, приплив маси > вихід -> Hillock)
    f.append(line(560, 100, 560, 190, color="#64748b", sw=2))
    f.append(line(560, 190, 480, 280, color="#64748b", sw=2))
    f.append(line(560, 190, 640, 280, color="#64748b", sw=2))

    # Зона 1: Порожнина (Void, ∇·J > 0)
    f.append(polygon([(220, 100), (260, 100), (250, 150), (230, 140)], fill="#ffffff", stroke=POS, sw=2))
    f.append(text(240, 128, "Void", size=11, bold=True, color=POS))

    # Зона 2: Пагорб (Hillock, ∇·J < 0)
    f.append(polygon([(540, 100), (580, 100), (590, 60), (570, 50), (530, 65)], fill="#d97706", stroke="#b45309", sw=2))
    f.append(text(560, 80, "Hillock", size=11, bold=True, color="#ffffff"))

    # Потоки на стику 1 (J_in < J_out)
    f.append(arrow(140, 180, 220, 180, color="#2563eb", sw=1.8))
    f.append(text(175, 172, "J_in (малий)", size=10, color="#2563eb"))

    f.append(arrow(260, 180, 370, 180, color=POS, sw=3))
    f.append(text(315, 172, "J_out (великий)", size=10.5, bold=True, color=POS))

    # Потоки на стику 2 (J_in > J_out)
    f.append(arrow(450, 180, 540, 180, color=POS, sw=3))
    f.append(text(495, 172, "J_in (великий)", size=10.5, bold=True, color=POS))

    f.append(arrow(580, 180, 660, 180, color="#2563eb", sw=1.8))
    f.append(text(620, 172, "J_out (малий)", size=10, color="#2563eb"))

    # Виносні блоки пояснення
    # Блок Порожнини
    f.append(rect(80, 310, 310, 95, fill="#fff1f2", stroke=POS, sw=1.5, rx=6))
    f.append(text(235, 332, "Позитивна дивергенція: ∇·J > 0", size=12, bold=True, color=POS))
    f.append(text(235, 353, "• Накопичення вакансій, розтяг (σ > 0)", size=11, color=INK))
    f.append(text(235, 372, "• Утворення та ріст порожнини (Void)", size=11, color=INK))
    f.append(text(235, 391, "• Ризик розриву кола (Open Circuit)", size=11, bold=True, color=POS))

    # Блок Пагорба
    f.append(rect(430, 310, 310, 95, fill="#fef3c7", stroke="#b45309", sw=1.5, rx=6))
    f.append(text(585, 332, "Негативна дивергенція: ∇·J < 0", size=12, bold=True, color="#b45309"))
    f.append(text(585, 353, "• Накопичення атомів, стиск (σ < 0)", size=11, color=INK))
    f.append(text(585, 372, "• Видавлювання пагорбів (Hillocks/Whiskers)", size=11, color=INK))
    f.append(text(585, 391, "• Ризик короткого замикання (Short Circuit)", size=11, bold=True, color="#b45309"))

    render(os.path.join(OUT, "void-hillock-formation.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Ефект Блеха: зворотний потік та критична довжина
# ════════════════════════════════════════════════════════════════════════════
def fig_blech_effect():
    W, H = 820, 420
    f = []

    # Заголовок
    f.append(rect(15, 15, W - 30, H - 30, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    f.append(text(W / 2, 42, "Ефект Блеха: механічний зворотний потік і стаціонарний стан", size=15, bold=True, color=INK))

    # Провідник обмеженої довжини L з діелектричними бар'єрами
    f.append(rect(140, 100, 540, 60, fill="#e2e8f0", stroke="#334155", sw=2, rx=2))
    f.append(rect(100, 80, 40, 100, fill="#94a3b8", stroke="#475569", sw=2, rx=4)) # Катодний бар'єр
    f.append(rect(680, 80, 40, 100, fill="#94a3b8", stroke="#475569", sw=2, rx=4)) # Анодний бар'єр

    f.append(text(120, 135, "Катод", size=11, bold=True, color="#ffffff"))
    f.append(text(700, 135, "Анод", size=11, bold=True, color="#ffffff"))

    # Позначення довжини L
    f.append(line(140, 175, 680, 175, color=DARK, sw=1.5))
    f.append(line(140, 170, 140, 180, color=DARK, sw=1.5))
    f.append(line(680, 170, 680, 180, color=DARK, sw=1.5))
    f.append(text(410, 192, "Довжина провідника L", size=12, bold=True, color=DARK))

    # Потоки у провіднику
    # 1. Потік електронного вітру (ліворуч праворуч)
    f.append(arrow(200, 118, 620, 118, color=NEG, sw=2.5))
    f.append(text(410, 112, "J_wind = C · (D / k_B T) · Z* e E →", size=11, bold=True, color=NEG))

    # 2. Зворотний механічний потік (праворуч ліворуч)
    f.append(arrow(620, 142, 200, 142, color=POS, sw=2.5))
    f.append(text(410, 156, "← J_back = - C · (D / k_B T) · Ω (∂σ / ∂x)", size=11, bold=True, color=POS))

    # Графік розподілу напруження σ(x)
    gx, gy, gw, gh = 140, 230, 540, 130
    f.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=4))

    # Нульова лінія напружень
    f.append(line(gx, gy + gh / 2, gx + gw, gy + gh / 2, color=MUTED, sw=1, dash="4 4"))
    f.append(text(gx - 35, gy + gh / 2 + 4, "σ = 0", size=11, color=MUTED))

    # Лінійний розподіл напруження (Розтяг на катоді σ > 0, Стиск на аноді σ < 0)
    f.append(line(gx + 20, gy + 25, gx + gw - 20, gy + gh - 25, color=FIELD, sw=3))

    f.append(circle(gx + 20, gy + 25, 5, fill=POS, stroke="#991b1b", sw=1.5))
    f.append(text(gx + 90, gy + 25, "Розтяг +σ_tensile (Катод)", size=11, bold=True, color=POS))

    f.append(circle(gx + gw - 20, gy + gh - 25, 5, fill=NEG, stroke="#1e3a8a", sw=1.5))
    f.append(text(gx + gw - 110, gy + gh - 20, "Стиск -σ_compressive (Анод)", size=11, bold=True, color=NEG))

    # Градієнт напруження ∂σ/∂x
    f.append(text(gx + gw / 2, gy + gh / 2 - 10, "Градієнт ∇σ = (σ_comp - σ_tens) / L", size=11, bold=True, color=FIELD))

    # Умова Блеха в кутку
    f.append(rect(540, 25, 250, 45, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(665, 43, "Умова імунітету (J_net = 0):", size=11, bold=True, color="#166534"))
    f.append(text(665, 60, "(j · L) < (j · L)_c  ⇒ Безсмертна лінія", size=11, bold=True, color="#166534"))

    render(os.path.join(OUT, "blech-length-effect.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Структура мідного міжз'єднання dual-damascene
# ════════════════════════════════════════════════════════════════════════════
def fig_interconnect_structure():
    W, H = 820, 440
    f = []

    # Заголовок
    f.append(rect(15, 15, W - 30, H - 30, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(W / 2, 42, "Поперечний переріз мідного міжз'єднання Dual-Damascene та шляхи дифузії", size=15, bold=True, color=INK))

    # Міжшаровий діелектрик Low-k
    f.append(rect(80, 80, 660, 260, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=6))
    f.append(text(140, 105, "Low-k діелектрик (SiO₂ / SiCOH)", size=11, color="#64748b", bold=True))

    # Захисне покриття (Co / Ru / SiN Cap layer) зверху
    f.append(rect(230, 115, 360, 20, fill="#cbd5e1", stroke="#475569", sw=1.5, rx=2))
    f.append(text(410, 129, "Верхнє покриття (Co/Ru cap або SiN / SiCN dielectric cap)", size=11, bold=True, color="#1e293b"))

    # Мідний провідник (Cu line) під покриттям
    f.append(rect(240, 140, 340, 160, fill="#fed7aa", stroke="#c2410c", sw=2, rx=4))

    # Бар'єрний шар (Ta/TaN liner) навколо Cu з трьох боків
    f.append(svg_path("M 235 140 L 235 305 L 585 305 L 585 140", stroke="#475569", sw=5, fill="none"))
    f.append(text(410, 322, "Бар'єрний шар Ta / TaN (1.5–3 нм)", size=11, bold=True, color="#334155"))

    # Зерна міді всередині провідника (межі зерен)
    f.append(line(310, 145, 310, 300, color="#d97706", sw=1.5, dash="3 3"))
    f.append(line(430, 145, 430, 300, color="#d97706", sw=1.5, dash="3 3"))
    f.append(line(510, 145, 510, 300, color="#d97706", sw=1.5, dash="3 3"))
    f.append(text(370, 220, "Кристалічні зерна міді (Cu)", size=13, bold=True, color="#9a3412"))

    # Стрілки та позначення шляхів дифузії
    # Шлях 1: Межа Cu / Cap (ГОЛОВНИЙ ШЛЯХ!)
    f.append(arrow(260, 148, 550, 148, color=POS, sw=3))
    f.append(text(410, 165, "① Дифузія по межі Cu / Cap (Найшвидший шлях! E_a ≈ 0.7–0.8 еВ)", size=11, bold=True, color=POS))

    # Шлях 2: Межі зерен
    f.append(arrow(310, 240, 310, 290, color="#2563eb", sw=2))
    f.append(text(320, 270, "② Межі зерен", size=10.5, bold=True, color="#2563eb"))

    # Шлях 3: Межа Cu / TaN
    f.append(arrow(575, 170, 575, 290, color=FIELD, sw=2))
    f.append(text(650, 230, "③ Межа Cu / TaN liner\n(E_a ≈ 0.9–1.1 еВ)", size=10.5, color=FIELD, bold=True))

    # Легенда / Таблиця енергій активації внизу
    f.append(rect(80, 355, 660, 65, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(410, 373, "Головні шляхи дифузії атомів у мідній металізації:", size=11.5, bold=True, color=INK))
    f.append(text(410, 393, "Поверхня розділу Cu/Cap > Межі зерен > Межа Cu/Liner >> Об'ємна дифузія ґратки (E_a ≈ 1.4 еВ)", size=11, color=MUTED))

    render(os.path.join(OUT, "interconnect-structure.svg"), W, H, *f)


if __name__ == '__main__':
    fig_electron_wind()
    fig_void_hillock()
    fig_blech_effect()
    fig_interconnect_structure()
    print("All figures successfully generated.")
