# -*- coding: utf-8 -*-
"""Фігури до теми «Струм зміщення».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
import math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

ACCENT = "#16a34a"  # зелений (поперечні / полів)
DARK   = "#0f172a"  # темний синій/вугільний
LINK   = "#2563eb"  # синій
WHITE  = "#ffffff"

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Парадокс закону Ампера в колі з конденсатором ─────────────────
def fig_capacitor_paradox():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 28, "Парадокс закону Ампера у колі зі змінним струмом", size=16, bold=True))

    # Дріт зліва
    f.append(line(50, 190, 260, 190, color=DARK, sw=3.5))
    f.append(arrow(110, 180, 170, 180, color=LINK, sw=2.2))
    f.append(text(140, 162, "I(t) [струм провідності]", size=12, color=LINK, bold=True))

    # Ліва пластина конденсатора
    f.append(rect(260, 100, 16, 180, fill="#dbeafe", stroke=LINK, sw=2, rx=3))
    f.append(text(268, 82, "+Q(t)", size=13, color=POS, bold=True))

    # Права пластина конденсатора
    f.append(rect(460, 100, 16, 180, fill="#fef2f2", stroke=POS, sw=2, rx=3))
    f.append(text(468, 82, "−Q(t)", size=13, color=NEG, bold=True))

    # Дріт справа
    f.append(line(476, 190, 690, 190, color=DARK, sw=3.5))
    f.append(arrow(530, 180, 590, 180, color=LINK, sw=2.2))
    f.append(text(560, 162, "I(t)", size=12, color=LINK, bold=True))

    # Замкнений контур C навколо дроту
    cx, cy = 190, 190
    rx, ry = 22, 60
    # Намалюємо еліпс контуру
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="#7c3aed" stroke-width="2.5" stroke-dasharray="6,3"/>' % (cx, cy, rx, ry))
    f.append(text(cx - 32, cy - 40, "Контур C", size=12, color="#7c3aed", bold=True))

    # Поверхня S1 (плоский диск, що перетинає дріт)
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#7c3aed" fill-opacity="0.15" stroke="#7c3aed" stroke-width="1.5"/>' % (cx, cy, rx, ry))
    b1, w1, h1 = textbox(190, 305, "Поверхня S₁:\nПеретинає дріт\nI_encl = I(t) ≠ 0\n∮ H·dl = I", size=11, pad=6, fill="#f3e8ff", stroke="#7c3aed", sw=1.2)
    f.append(b1)

    # Поверхня S2 (мішок, що проходить між пластинами)
    path_s2 = "M 190,130 C 230,130 360,110 360,190 C 360,270 230,250 190,250"
    f.append('<path d="%s" fill="#fef3c7" fill-opacity="0.35" stroke="#d97706" stroke-width="2" stroke-dasharray="4,4"/>' % path_s2)
    b2, w2, h2 = textbox(360, 305, "Поверхня S₂ (без струму зміщення):\nПроходить між пластинами\nI_encl = 0  →  ∮ H·dl = 0\nСУПЕРЕЧНІСТЬ!", size=11, pad=6, fill="#fffbeb", stroke="#d97706", sw=1.2)
    f.append(b2)

    # Електричне поле між пластинами E(t)
    for ey in range(120, 270, 30):
        f.append(arrow(280, ey, 450, ey, color=ACCENT, sw=1.8))
    f.append(text(365, 95, "Електричне поле E(t)", size=12, color=ACCENT, bold=True))

    # Пояснення розв'язку Максвелла справа
    b3, w3, h3 = textbox(595, 305, "Розв'язок Максвелла:\nJ_d = ∂D/∂t  (струм зміщення)\nПовний струм крізь S₂ = I_d = I\nЦиркуляція H однакова для S₁ і S₂!", size=11, pad=6, fill="#ecfdf5", stroke=ACCENT, sw=1.2)
    f.append(b3)

    return render(os.path.join(IMG, "capacitor-paradox.svg"), W, H, *f)


# ── Фігура 2: Вихрове магнітне поле струму зміщення у плоскому конденсаторі ─
def fig_field_between_plates():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 28, "Генерація вихрового магнітного поля зміною електричного поля", size=16, bold=True))

    # Ліва панель: Вид сбоку на конденсатор
    f.append(rect(40, 60, 310, 310, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    f.append(text(195, 82, "Вид сбоку (поперечний переріз)", size=13, bold=True))

    # Пластини
    f.append(rect(90, 100, 12, 220, fill="#dbeafe", stroke=LINK, sw=1.8, rx=2))
    f.append(rect(290, 100, 12, 220, fill="#fef2f2", stroke=POS, sw=1.8, rx=2))
    f.append(text(96, 340, "+Q", size=12, color=POS, bold=True))
    f.append(text(296, 340, "−Q", size=12, color=NEG, bold=True))

    # Вектори E та J_d
    for ey in range(125, 300, 35):
        f.append(arrow(105, ey, 285, ey, color=ACCENT, sw=2))
    f.append(text(195, 115, "∂E/∂t > 0", size=13, color=ACCENT, bold=True))
    f.append(text(195, 305, "J_d = ε₀ (∂E/∂t)", size=12, color=ACCENT, bold=True))

    # Права панель: Вид вздовж осі (концентричні кола B)
    cx, cy = 550, 210
    f.append(rect(380, 60, 340, 310, fill="#f8fafc", stroke=MUTED, sw=1, rx=8))
    f.append(text(550, 82, "Вид уздовж осі (поле B(r))", size=13, bold=True))

    # Зовнішнє коло пластини R
    R = 110
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#f1f5f9" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4,4"/>' % (cx, cy, R))
    f.append(text(cx + R - 15, cy - R + 25, "Радіус R", size=11, color=MUTED, bold=True))

    # Вектори E входом у сторінку (хрестики)
    f.append(text(cx, cy, "⊗ E, J_d", size=14, color=ACCENT, bold=True))

    # Концентричні кола магнітного поля B(r)
    r1, r2, r3 = 45, 80, 135
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#7c3aed" stroke-width="1.8"/>' % (cx, cy, r1))
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#7c3aed" stroke-width="2.2"/>' % (cx, cy, r2))
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#7c3aed" stroke-width="1.8" stroke-dasharray="5,3"/>' % (cx, cy, r3))

    # Стрілки напрямку B (за годинниковою стрілкою)
    f.append(arrow(cx, cy - r1, cx + 1, cy - r1, color="#7c3aed", sw=2))
    f.append(arrow(cx + r1, cy, cx + r1, cy + 1, color="#7c3aed", sw=2))
    f.append(arrow(cx, cy - r2, cx + 1, cy - r2, color="#7c3aed", sw=2))
    f.append(arrow(cx + r2, cy, cx + r2, cy + 1, color="#7c3aed", sw=2))
    f.append(arrow(cx, cy + r2, cx - 1, cy + r2, color="#7c3aed", sw=2))

    # Позначки формул B(r)
    f.append(text(cx, cy - r1 - 10, "B ∝ r  (r < R)", size=11, color="#7c3aed", bold=True))
    f.append(text(cx, cy - r3 - 10, "B ∝ 1/r  (r > R)", size=11, color="#7c3aed", bold=True))

    return render(os.path.join(IMG, "field-between-plates.svg"), W, H, *f)


# ── Фігура 3: Потік енергії у конденсатор через вектор Пойнтінга ───────────
def fig_poynting_capacitor():
    W, H = 760, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 28, "Вектор Пойнтінга S = E × H під час заряджання конденсатора", size=16, bold=True))

    # Циліндр конденсатора (схематично)
    cx, cy = 340, 210
    w_cap, h_cap = 220, 160

    # Задня пластина
    f.append(rect(cx - w_cap/2, cy - h_cap/2, 14, h_cap, fill="#dbeafe", stroke=LINK, sw=2, rx=3))
    f.append(text(cx - w_cap/2, cy - h_cap/2 - 14, "Пластина 1 (+V)", size=11, color=POS, bold=True))

    # Передня пластина
    f.append(rect(cx + w_cap/2 - 14, cy - h_cap/2, 14, h_cap, fill="#fef2f2", stroke=POS, sw=2, rx=3))
    f.append(text(cx + w_cap/2 - 14, cy - h_cap/2 - 14, "Пластина 2 (0V)", size=11, color=NEG, bold=True))

    # Діелектричний проміжок
    f.append(rect(cx - w_cap/2 + 14, cy - h_cap/2, w_cap - 28, h_cap, fill="#f1f5f9", stroke="#cbd5e1", sw=1))

    # Вектори E(t) горизонтально вправо
    for ey in [-40, 0, 40]:
        f.append(arrow(cx - 70, cy + ey, cx + 70, cy + ey, color=ACCENT, sw=2))
    f.append(text(cx, cy - 55, "Електричне поле E_z", size=12, color=ACCENT, bold=True))

    # Вектори H_φ по періметру
    f.append(text(cx, cy + 55, "Магнітне поле H_φ (кругове)", size=12, color="#7c3aed", bold=True))

    # Радіальні вектори Пойнтінга S спрямовані ВСЕРЕДИНУ об'єму конденсатора!
    f.append(arrow(cx - 40, cy - h_cap/2 - 35, cx - 40, cy - h_cap/2 + 15, color="#dc2626", sw=2.5))
    f.append(arrow(cx + 40, cy - h_cap/2 - 35, cx + 40, cy - h_cap/2 + 15, color="#dc2626", sw=2.5))
    f.append(text(cx, cy - h_cap/2 - 42, "S = E × H  (потік енергії всередину)", size=12, color="#dc2626", bold=True))

    f.append(arrow(cx - 40, cy + h_cap/2 + 35, cx - 40, cy + h_cap/2 - 15, color="#dc2626", sw=2.5))
    f.append(arrow(cx + 40, cy + h_cap/2 + 35, cx + 40, cy + h_cap/2 - 15, color="#dc2626", sw=2.5))
    f.append(text(cx, cy + h_cap/2 + 48, "S (радіально всередину)", size=11, color="#dc2626", bold=True))

    # Картка пояснення праворуч
    b1, w1, h1 = textbox(600, 210, "Парадокс Пойнтінга:\n\n• Енергія не тече по дротах!\n  Дроти лише створюють E й H.\n\n• Енергія надходить із простору\n  довкола конденсатора через S.\n\n• Повний потік P = ∬ S·dA = V · I\n  дорівнює dW_e/dt !", size=11, pad=10, fill="#fef2f2", stroke="#dc2626", sw=1.5)
    f.append(b1)

    return render(os.path.join(IMG, "poynting-capacitor.svg"), W, H, *f)


# ── Фігура 4: Співвідношення струмів провідності та зміщення ─────────────────
def fig_current_density_ratio():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 28, "Перехід від струму провідності J_c до струму зміщення J_d за частотою", size=16, bold=True))

    # Графік: Осі lg(f) vs lg(J_d / J_c)
    ox, oy = 90, 320
    gx_w, gy_h = 420, 250

    # Вісі
    f.append(line(ox, oy, ox + gx_w, oy, color=DARK, sw=2))
    f.append(line(ox, oy, ox, oy - gy_h, color=DARK, sw=2))
    f.append(text(ox + gx_w / 2, oy + 38, "Частота f (Гц) →", size=12, bold=True))
    f.append(text(ox - 50, oy - gy_h / 2, "Відношення J_d / J_c", size=12, bold=True))

    # Позначки частот на осі X
    freqs = [("50 Гц", 50), ("1 кГц", 120), ("1 МГц", 210), ("1 ГГц", 300), ("1 ТГц", 390)]
    for lbl, fx in freqs:
        f.append(line(ox + fx, oy, ox + fx, oy - 6, color=DARK, sw=1.5))
        f.append(text(ox + fx, oy + 18, lbl, size=10, color=MUTED))

    # Лінія рівності J_d = J_c
    y_eq = oy - gy_h * 0.5
    f.append(line(ox, y_eq, ox + gx_w, y_eq, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(ox + gx_w - 40, y_eq - 8, "J_d = J_c (tan δ = 1)", size=10, color=MUTED, bold=True))

    # Крива для міді
    f.append(line(ox, oy - 20, ox + gx_w, oy - 35, color=LINK, sw=2.5))
    f.append(text(ox + 220, oy - 48, "Мідь (провідник): J_c ≫ J_d", size=11, color=LINK, bold=True))

    # Крива для вологого ґрунту / води
    f.append(line(ox, oy - 70, ox + gx_w, oy - 200, color="#d97706", sw=2.5))
    f.append(text(ox + 240, oy - 140, "Вода / ґрунт", size=11, color="#d97706", bold=True))

    # Крива для тефлону
    f.append(line(ox, oy - 150, ox + gx_w, oy - 240, color=ACCENT, sw=2.5))
    f.append(text(ox + 120, oy - 220, "Тефлон (діелектрик): J_d ≫ J_c", size=11, color=ACCENT, bold=True))

    # Картка з формулою та висновком праворуч
    b1, w1, h1 = textbox(630, 180, "Формула співвідношення:\n\nJ_d / J_c = (ω · ε) / σ\n\n• Низькі частоти (DC..50Гц):\n  Домінує струм провідності J_c\n\n• Високі частоти (ВЧ/ВЧ-НВЧ):\n  Домінує струм зміщення J_d\n\n• У вакуумі (σ = 0):\n  Існує ВИКЛЮЧНО J_d !", size=11, pad=10, fill="#f8fafc", stroke=DARK, sw=1.5)
    f.append(b1)

    return render(os.path.join(IMG, "current-density-ratio.svg"), W, H, *f)


if __name__ == "__main__":
    fig_capacitor_paradox()
    fig_field_between_plates()
    fig_poynting_capacitor()
    fig_current_density_ratio()
    print("Figures generated successfully in ./img/")
