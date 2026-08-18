# -*- coding: utf-8 -*-
import sys, os
import math

# Path to scripts/ folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def fig_dipole_models():
    """Схема 1: Модель Ґільберта (заряди) проти моделі Ампера (контур)"""
    w, h = 760, 380
    frags = []
    
    # Заголовок
    frags.append(text(w / 2, 25, "Дві фізичні моделі магнітного диполя", size=18, bold=True))
    
    # ── Ліва панель: Модель Ґільберта ──
    x_g = 190
    frags.append(rect(20, 55, 350, 250, fill="#f9fafb", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(x_g, 80, "Модель Ґільберта (магнітні заряди)", size=14, bold=True, color=INK))
    
    # Фіктивні заряди
    y_s, y_n = 230, 130
    frags.append(minus(x_g, y_s, r=16))
    frags.append(text(x_g + 30, y_s + 5, "-q_m (S)", size=13, bold=True, color=NEG, anchor="start"))
    
    frags.append(plus(x_g, y_n, r=16))
    frags.append(text(x_g + 30, y_n + 5, "+q_m (N)", size=13, bold=True, color=POS, anchor="start"))
    
    # Вектор відстані d та момент m
    frags.append(arrow(x_g - 40, y_s, x_g - 40, y_n, color=POS, sw=2.5))
    frags.append(text(x_g - 55, (y_s + y_n) / 2 + 4, "m = q_m · d", size=13, bold=True, color=POS, anchor="end"))
    
    # Зовнішнє поле (від + до - вгору і навколо)
    frags.append(arrow(x_g, y_n - 20, x_g, y_n - 55, color=FIELD, sw=2))
    frags.append(text(x_g + 12, y_n - 35, "B_зовн", size=12, color=FIELD, anchor="start"))
    
    # Внутрішнє поле (всередині від + до - проти m!)
    frags.append(line(x_g, y_n + 20, x_g, y_s - 20, color=NEG, sw=2, dash="4,3"))
    frags.append(text(x_g + 12, (y_s + y_n) / 2 + 4, "B_вн ∝ -m", size=11, color=NEG, anchor="start"))
    
    # Підпис лівої моделі
    fitbox(30, 260, 330, 35, "Фіктивні джерела: ∇ · B ≠ 0 локально\nПоле всередині спрямоване проти m", size=11, fill="#fef2f2", stroke="#fca5a5")

    # ── Права панель: Модель Ампера ──
    x_a = 570
    frags.append(rect(390, 55, 350, 250, fill="#f9fafb", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(x_a, 80, "Модель Ампера (струмовий контур)", size=14, bold=True, color=INK))
    
    # Еліпс контуру зі струмом
    y_c = 180
    frags.append('<ellipse cx="%d" cy="%d" rx="70" ry="25" fill="#e0f2fe" stroke="%s" stroke-width="2.5"/>' % (x_a, y_c, NEG))
    
    # Струм в контурі
    frags.append(arrow(x_a + 50, y_c + 15, x_a + 65, y_c + 5, color=NEG, sw=2))
    frags.append(text(x_a + 80, y_c + 18, "Струм I", size=13, bold=True, color=NEG, anchor="start"))
    
    # Вектор магнітного моменту m = I S n
    frags.append(arrow(x_a, y_c, x_a, y_c - 70, color=POS, sw=3))
    frags.append(text(x_a + 12, y_c - 45, "m = I · S · n", size=13, bold=True, color=POS, anchor="start"))
    
    # Поле крізь контур (неперервні замкнені лінії!)
    frags.append(arrow(x_a - 35, y_c + 40, x_a - 35, y_c - 40, color=FIELD, sw=2))
    frags.append(arrow(x_a + 35, y_c + 40, x_a + 35, y_c - 40, color=FIELD, sw=2))
    frags.append(text(x_a - 45, y_c, "B", size=12, bold=True, color=FIELD, anchor="end"))
    
    # Підпис правої моделі
    fitbox(400, 260, 330, 35, "Реальна фізика: ∇ · B = 0 всюди\nПоле неперервне, всередині B ∝ +m", size=11, fill="#f0fdf4", stroke="#86efac")

    # Нижній висновок
    textbox(w / 2, 345, "На відстані r >> d обидві моделі створюють одинакове поле B ∝ 1/r³", size=12, fill="#f3f4f6", stroke="#9ca3af")
    
    render(os.path.join(IMG_DIR, 'dipole-models.svg'), w, h, *frags)

def fig_dipole_field_lines():
    """Схема 2: Геометрія поля диполя на осі та на екваторі"""
    w, h = 760, 420
    frags = []
    
    frags.append(text(w / 2, 25, "Геометрія силових ліній та вектори поля диполя", size=18, bold=True))
    
    cx, cy = 380, 230
    
    # Диполь у центрі
    frags.append(arrow(cx, cy + 30, cx, cy - 40, color=POS, sw=3.5))
    frags.append(circle(cx, cy, 6, fill=POS, stroke=INK, sw=1))
    frags.append(text(cx + 15, cy - 10, "m (диполь)", size=14, bold=True, color=POS, anchor="start"))
    
    # Осі координат (пунктир)
    frags.append(line(cx - 320, cy, cx + 320, cy, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(cx + 330, cy + 4, "Екватор (θ = 90°)", size=12, color=MUTED, anchor="start"))
    
    frags.append(line(cx, cy - 160, cx, cy + 150, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(cx + 8, cy - 165, "Вісь (θ = 0°)", size=12, color=MUTED, anchor="start"))
    
    # Еліптичні силові лінії (за допомогою полів під кутом)
    # Ліва і права петлі
    frags.append('<path d="M %d %d C %d %d, %d %d, %d %d" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="6,3"/>' % 
                 (cx, cy - 35, cx - 180, cy - 140, cx - 180, cy + 140, cx, cy + 25, FIELD))
    frags.append('<path d="M %d %d C %d %d, %d %d, %d %d" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="6,3"/>' % 
                 (cx, cy - 35, cx + 180, cy - 140, cx + 180, cy + 140, cx, cy + 25, FIELD))
    
    # Вектор поля на осі (вгорі)
    y_axis = cy - 110
    frags.append(circle(cx, y_axis, 4, fill=FIELD, stroke=INK, sw=1))
    frags.append(arrow(cx, y_axis, cx, y_axis - 45, color=FIELD, sw=3))
    fitbox(cx + 15, y_axis - 45, 230, 36, "Поле на осі (θ = 0°):\nB_осі = (μ₀/2π) · m/r³ (паралельне m)", size=11, fill="#f0fdf4", stroke="#86efac", anchor="start")
    
    # Вектор поля на екваторі (праворуч)
    x_eq = cx + 180
    frags.append(circle(x_eq, cy, 4, fill=FIELD, stroke=INK, sw=1))
    frags.append(arrow(x_eq, cy, x_eq, cy + 45, color=FIELD, sw=3))
    fitbox(x_eq - 10, cy + 55, 250, 36, "Поле на екваторі (θ = 90°):\nB_екв = (μ₀/4π) · m/r³ (антипаралельне m)", size=11, fill="#eff6ff", stroke="#93c5fd")
    
    # Співвідношення величин
    textbox(180, 110, "Співвідношення полів:\nB_осі = 2 · B_екв\n(на однаковій відстані r)", size=12, fill="#fffbebe6", stroke="#fcd34d")
    
    # Формула модуля
    textbox(w / 2, 385, "|B(r, θ)| = (μ₀ m / 4π r³) · √(1 + 3 cos² θ)", size=13, bold=True, fill="#f3f4f6", stroke="#9ca3af")
    
    render(os.path.join(IMG_DIR, 'dipole-field-lines.svg'), w, h, *frags)

def fig_dipole_interaction():
    """Схема 3: Взаємодія двох диполів залежно від орієнтації"""
    w, h = 760, 400
    frags = []
    
    frags.append(text(w / 2, 25, "Сила та потенціальна енергія взаємодії двох магнітних диполів", size=18, bold=True))
    
    # ── Конфігурація 1: Співосна паралельна (Притягання) ──
    x1 = 140
    frags.append(rect(20, 60, 230, 270, fill="#f9fafb", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(x1, 85, "1. Співосна паралельна", size=13, bold=True, color=INK))
    
    # Вектори m1 і m2
    frags.append(arrow(x1 - 40, 180, x1 - 40, 120, color=POS, sw=2.8))
    frags.append(text(x1 - 40, 195, "m₁", size=13, bold=True, color=POS))
    
    frags.append(arrow(x1 + 40, 180, x1 + 40, 120, color=POS, sw=2.8))
    frags.append(text(x1 + 40, 195, "m₂", size=13, bold=True, color=POS))
    
    # Сили притягання (назустріч одна одній)
    frags.append(arrow(x1 - 40, 150, x1 - 10, 150, color=NEG, sw=2.5))
    frags.append(arrow(x1 + 40, 150, x1 + 10, 150, color=NEG, sw=2.5))
    
    fitbox(30, 230, 210, 85, "Енергія: U = -μ₀ m₁m₂ / (2π r³)\nДія: ПРИТЯГАННЯ\nF ∝ -1/r⁴\nМінімум енергії (стійкий)", size=11, fill="#f0fdf4", stroke="#86efac")

    # ── Конфігурація 2: Паралельна збоку (Відштовхування) ──
    x2 = 380
    frags.append(rect(265, 60, 230, 270, fill="#f9fafb", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(x2, 85, "2. Паралельна поруч", size=13, bold=True, color=INK))
    
    # Вектори m1 і m2 поруч
    frags.append(arrow(x2 - 50, 180, x2 - 50, 120, color=POS, sw=2.8))
    frags.append(text(x2 - 50, 195, "m₁", size=13, bold=True, color=POS))
    
    frags.append(arrow(x2 + 50, 180, x2 + 50, 120, color=POS, sw=2.8))
    frags.append(text(x2 + 50, 195, "m₂", size=13, bold=True, color=POS))
    
    # Сили відштовхування (у боки)
    frags.append(arrow(x2 - 50, 150, x2 - 85, 150, color=POS, sw=2.5))
    frags.append(arrow(x2 + 50, 150, x2 + 85, 150, color=POS, sw=2.5))
    
    fitbox(275, 230, 210, 85, "Енергія: U = +μ₀ m₁m₂ / (4π r³)\nДія: ВІДШТОВХУВАННЯ\nF ∝ +1/r⁴\nМаксимум (нестійкий)", size=11, fill="#fef2f2", stroke="#fca5a5")

    # ── Конфігурація 3: Антипаралельна поруч (Притягання) ──
    x3 = 620
    frags.append(rect(510, 60, 230, 270, fill="#f9fafb", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(x3, 85, "3. Антипаралельна поруч", size=13, bold=True, color=INK))
    
    # m1 вгору, m2 вниз
    frags.append(arrow(x3 - 50, 180, x3 - 50, 120, color=POS, sw=2.8))
    frags.append(text(x3 - 50, 195, "m₁", size=13, bold=True, color=POS))
    
    frags.append(arrow(x3 + 50, 120, x3 + 50, 180, color=NEG, sw=2.8))
    frags.append(text(x3 + 50, 195, "m₂", size=13, bold=True, color=NEG))
    
    # Сили притягання
    frags.append(arrow(x3 - 50, 150, x3 - 20, 150, color=FIELD, sw=2.5))
    frags.append(arrow(x3 + 50, 150, x3 + 20, 150, color=FIELD, sw=2.5))
    
    fitbox(520, 230, 210, 85, "Енергія: U = -μ₀ m₁m₂ / (4π r³)\nДія: ПРИТЯГАННЯ\nДиполі антипаралельні\nСтійкий стан для сусідів", size=11, fill="#f0fdf4", stroke="#86efac")

    # Загальний підсумок
    textbox(w / 2, 360, "Загальна формула енергії: U₁₂ = (μ₀ / 4π r³) · [m₁ · m₂ - 3(m₁ · r̂)(m₂ · r̂)]", size=13, bold=True, fill="#f3f4f6", stroke="#9ca3af")
    
    render(os.path.join(IMG_DIR, 'dipole-interaction.svg'), w, h, *frags)

def fig_atomic_planetary_dipoles():
    """Схема 4: Магнітний диполь на різних масштабах природи"""
    w, h = 760, 360
    frags = []
    
    frags.append(text(w / 2, 25, "Магнітний диполь у масштабах Всесвіту", size=18, bold=True))
    
    # 1. Мікромасштаб (Спін електрона)
    frags.append(rect(20, 60, 230, 220, fill="#f9fafb", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(135, 85, "Атомний масштаб", size=14, bold=True, color=INK))
    frags.append(circle(135, 140, 22, fill="#e0f2fe", stroke=NEG, sw=2))
    frags.append(text(135, 145, "e⁻", size=14, bold=True, color=NEG))
    frags.append(arrow(135, 140, 135, 95, color=POS, sw=2.5))
    frags.append(text(150, 110, "μ_B", size=13, bold=True, color=POS, anchor="start"))
    fitbox(30, 185, 210, 80, "Спін та орбітальний рух\nМагнетон Бора:\nμ_B ≈ 9.27 × 10⁻²⁴ А·м²\nДжерело квантового магнетизму", size=11, fill="#eff6ff", stroke="#93c5fd")

    # 2. Макромасштаб (Постійний магніт / котушка)
    frags.append(rect(265, 60, 230, 220, fill="#f9fafb", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(380, 85, "Лабораторний масштаб", size=14, bold=True, color=INK))
    frags.append(rect(340, 120, 80, 35, fill="#fee2e2", stroke=POS, sw=2, rx=4))
    frags.append(text(360, 142, "S", size=14, bold=True, color=NEG))
    frags.append(text(400, 142, "N", size=14, bold=True, color=POS))
    frags.append(arrow(380, 137, 435, 137, color=POS, sw=2.5))
    frags.append(text(440, 142, "m", size=13, bold=True, color=POS, anchor="start"))
    fitbox(275, 185, 210, 80, "Штабовий магніт / соленоїд\nНеодимовий магніт NdFeB:\nm ~ 1 - 10 А·м²\nСума доменних диполів", size=11, fill="#fef2f2", stroke="#fca5a5")

    # 3. Мегамасштаб (Земля / Пульсар)
    frags.append(rect(510, 60, 230, 220, fill="#f9fafb", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(625, 85, "Космічний масштаб", size=14, bold=True, color=INK))
    frags.append(circle(625, 140, 28, fill="#dcfce7", stroke=FIELD, sw=2))
    frags.append(text(625, 145, "Земля", size=12, bold=True, color=FIELD))
    frags.append(arrow(625, 155, 615, 100, color=POS, sw=2.5)) # Нахилений геомагнітний диполь
    frags.append(text(630, 110, "m_Землі", size=12, bold=True, color=POS, anchor="start"))
    fitbox(520, 185, 210, 80, "Магнітне поле Землі та зірок\nГеомагнітний диполь:\nm_E ≈ 8 × 10²² А·м²\nЗахищає від сонячного вітру", size=11, fill="#f0fdf4", stroke="#86efac")

    textbox(w / 2, 315, "Дипольна форма поля є універсальною фундаментальною симетрією на всіх рівнях природи", size=12, fill="#f3f4f6", stroke="#9ca3af")

    render(os.path.join(IMG_DIR, 'atomic-planetary-dipoles.svg'), w, h, *frags)

if __name__ == "__main__":
    fig_dipole_models()
    fig_dipole_field_lines()
    fig_dipole_interaction()
    fig_atomic_planetary_dipoles()
    print("Всі 4 фігури для magnetic-dipole успішно згенеровано!")
