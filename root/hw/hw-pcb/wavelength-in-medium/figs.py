# -*- coding: utf-8 -*-
"""Фігури до теми «Ефективна довжина хвилі у діелектрику».
Запуск: python figs.py -> генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

ACCENT = "#16a34a"  # зелений
DARK   = "#0f172a"  # темний
LINK   = "#2563eb"  # синій
AMBER  = "#d97706"  # бурштиновий
PURPLE = "#7c3aed"  # фіолетовий

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Розподіл полів у мікросмужці та ефективна проникність ───────────
def fig_microstrip_fields():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Розподіл електромагнітного поля у мікросмужковій лінії", size=16, bold=True))

    # Ліва частина: поперечний переріз мікросмужки (геометрія та силові лінії)
    # Повітря зверху
    f.append(rect(40, 55, 380, 120, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=4))
    f.append(text(80, 78, "Повітря (ε_r = 1.0)", size=12, bold=True, color=MUTED))

    # Діелектрична підкладка
    f.append(rect(40, 175, 380, 130, fill="#ecfdf5", stroke="#10b981", sw=1.5, rx=0))
    f.append(text(120, 295, "Підкладка: FR-4 / Rogers (ε_r > 1)", size=12, bold=True, color=ACCENT))

    # Суцільний шар заземлення знизу (Ground Plane)
    f.append(rect(40, 305, 380, 16, fill="#cbd5e1", stroke="#475569", sw=1.5, rx=2))
    f.append(text(230, 318, "Суцільна площина заземлення (GND)", size=11, bold=True, color=DARK))

    # Сигнальний смужковий провідник (Microstrip conductor)
    f.append(rect(170, 162, 120, 13, fill="#f59e0b", stroke="#b45309", sw=1.5, rx=2))
    f.append(text(230, 154, "Смужка (ширина w)", size=12, bold=True, color="#b45309"))

    # Розмірні стрілки для товщини підкладки h
    f.append(line(25, 175, 35, 175, color=DARK, sw=1.2))
    f.append(line(25, 305, 35, 305, color=DARK, sw=1.2))
    f.append(line(30, 175, 30, 305, color=DARK, sw=1.2))
    f.append(text(20, 245, "h", size=13, bold=True, color=DARK))

    # Розмірні стрілки для ширини смужки w
    f.append(line(170, 140, 170, 148, color=DARK, sw=1.0))
    f.append(line(290, 140, 290, 148, color=DARK, sw=1.0))
    f.append(line(170, 144, 290, 144, color=DARK, sw=1.0))
    f.append(text(230, 138, "w", size=12, bold=True, color=DARK))

    # Силові лінії електричного поля (E-field) - зелені/сині
    # Прямі вертикальні лінії під смужкою (основне поле в діелектрику)
    for x in (190, 210, 230, 250, 270):
        f.append(line(x, 175, x, 305, color=LINK, sw=1.8))
        f.append('<polygon points="%d,245 %d,237 %d,237" fill="%s"/>' % (x, x - 3, x + 3, LINK))

    # Крайові лінії поля (Fringing fields), що заходять у повітря
    # Лівий край
    f.append('<path d="M 170 168 C 110 130, 90 220, 110 305" fill="none" stroke="%s" stroke-width="1.8"/>' % LINK)
    f.append('<path d="M 175 168 C 135 150, 120 230, 140 305" fill="none" stroke="%s" stroke-width="1.8"/>' % LINK)
    # Правий край
    f.append('<path d="M 290 168 C 350 130, 370 220, 350 305" fill="none" stroke="%s" stroke-width="1.8"/>' % LINK)
    f.append('<path d="M 285 168 C 325 150, 340 230, 320 305" fill="none" stroke="%s" stroke-width="1.8"/>' % LINK)

    # Права частина: Інженерний баланс проникності
    box1, _, _ = textbox(580, 110, "Крайове поле у повітрі\n• Проникність ε_0 (ε_r = 1.0)\n• Збільшує фазову швидкість v_p", size=12, pad=10, fill="#f8fafc", stroke="#94a3b8", color=DARK)
    f.append(box1)

    box2, _, _ = textbox(580, 220, "Основне поле в підкладці\n• Проникність ε_0 · ε_r (ε_r = 3.5...10)\n• Сповільнює хвилю, скорочує λ", size=12, pad=10, fill="#ecfdf5", stroke="#10b981", color=DARK)
    f.append(box2)

    box3, _, _ = textbox(580, 335, "Результуюча ефективна проникність:\n1.0 < ε_eff < ε_r\nКоефіцієнт заповнення: q = (ε_eff − 1) / (ε_r − 1)", size=12, pad=10, fill="#eff6ff", stroke=LINK, color=LINK, bold=True)
    f.append(box3)

    return render(os.path.join(IMG, "fig-microstrip-fields.svg"), W, H, *f)


# ── Фігура 2: Порівняння скорочення довжини хвилі у різних середовищах ─────────
def fig_wavelength_compression():
    W, H = 760, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Просторове скорочення довжини електромагнітної хвилі", size=16, bold=True))

    # Рівень 1: Вакуум / Повітря (довжина хвилі λ₀)
    f.append(rect(30, 50, 700, 85, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(160, 72, "1. Вільний простір / вакуум (ε_r = 1.0)", size=13, bold=True, color=DARK))
    f.append(text(590, 72, "v_p = c ≈ 300 000 км/с", size=12, bold=True, color=MUTED))

    # Синусоїда для вільного простору (довжина хвилі 240px)
    pts1 = []
    for x in range(50, 690, 3):
        y = 105 - 24 * math.sin((x - 50) * 2 * math.pi / 240.0)
        pts1.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts1), LINK))

    # Розмірна стрілка λ₀
    f.append(line(50, 125, 290, 125, color=LINK, sw=1.5))
    f.append(line(50, 120, 50, 130, color=LINK, sw=1.5))
    f.append(line(290, 120, 290, 130, color=LINK, sw=1.5))
    f.append(text(170, 122, "λ₀ = c / f (100%)", size=11, bold=True, color=LINK))

    # Рівень 2: Мікросмужка на FR-4 (ε_eff ≈ 3.3, квазі-ТЕМ хвиля)
    f.append(rect(30, 150, 700, 95, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=6))
    f.append(text(180, 172, "2. Мікросмужка на PCB (ε_eff ≈ 3.3)", size=13, bold=True, color=LINK))
    f.append(text(590, 172, "v_p = c / √(ε_eff) ≈ 0.55 · c", size=12, bold=True, color=LINK))

    # Синусоїда для мікросмужки (довжина хвилі 240 / sqrt(3.3) ≈ 132px)
    pts2 = []
    for x in range(50, 690, 3):
        y = 210 - 24 * math.sin((x - 50) * 2 * math.pi / 132.0)
        pts2.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts2), ACCENT))

    # Розмірна стрілка λ_g
    f.append(line(50, 235, 182, 235, color=ACCENT, sw=1.5))
    f.append(line(50, 230, 50, 240, color=ACCENT, sw=1.5))
    f.append(line(182, 230, 182, 240, color=ACCENT, sw=1.5))
    f.append(text(116, 232, "λ_g = λ₀ / √(ε_eff)  (~55%)", size=11, bold=True, color=ACCENT))

    # Рівень 3: Суцільний об'ємний діелектрик (ε_r = 4.4)
    f.append(rect(30, 260, 700, 95, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    f.append(text(190, 282, "3. Суцільний діелектрик FR-4 (ε_r = 4.4)", size=13, bold=True, color=DARK))
    f.append(text(590, 282, "v_p = c / √(ε_r) ≈ 0.477 · c", size=12, bold=True, color=DARK))

    # Синусоїда для суцільного діелектрика (довжина хвилі 240 / sqrt(4.4) ≈ 114px)
    pts3 = []
    for x in range(50, 690, 3):
        y = 320 - 24 * math.sin((x - 50) * 2 * math.pi / 114.0)
        pts3.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (" ".join(pts3), PURPLE))

    # Розмірна стрілка λ_m
    f.append(line(50, 345, 164, 345, color=PURPLE, sw=1.5))
    f.append(line(50, 340, 50, 350, color=PURPLE, sw=1.5))
    f.append(line(164, 340, 164, 350, color=PURPLE, sw=1.5))
    f.append(text(107, 342, "λ_m = λ₀ / √(ε_r)  (~48%)", size=11, bold=True, color=PURPLE))

    f.append(text(W / 2, 376, "Висновок: хвиля в мікросмужці стискається сильніше, ніж у повітрі, але слабше, ніж у суцільному моноліті", size=12, bold=True, color=DARK))

    return render(os.path.join(IMG, "fig-wavelength-compression.svg"), W, H, *f)


# ── Фігура 3: Частотна дисперсія ефективної діелектричної проникності ──────────
def fig_dispersion_curve():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Частотна дисперсія ефективної діелектричної проникності ε_eff(f)", size=16, bold=True))

    # Осі координат
    ox, oy = 90, 330
    ax_w, ax_h = 420, 250

    f.append(line(ox, oy, ox + ax_w, oy, color=DARK, sw=1.8))  # Вісь частоти
    f.append(line(ox, oy, ox, oy - ax_h, color=DARK, sw=1.8))  # Вісь ε_eff

    f.append(arrow(ox + ax_w - 20, oy, ox + ax_w, oy, color=DARK, sw=1.8))
    f.append(arrow(ox, oy - ax_h + 20, ox, oy - ax_h, color=DARK, sw=1.8))

    f.append(text(ox + ax_w - 30, oy + 25, "Частота f (ГГц)", size=12, bold=True, color=DARK))
    f.append(text(ox - 35, oy - ax_h + 15, "ε_eff(f)", size=13, bold=True, color=DARK))

    # Горизонтальні асимптоти: квазістатика ε_eff(0) та межа ε_r
    # Низ: ε_eff(0)
    y_low = oy - 40
    f.append(line(ox, y_low, ox + ax_w - 30, y_low, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(ox - 30, y_low + 4, "ε_eff(0)", size=12, bold=True, color=LINK))

    # Верх: ε_r
    y_high = oy - 210
    f.append(line(ox, y_high, ox + ax_w - 30, y_high, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(ox - 25, y_high + 4, "ε_r", size=12, bold=True, color=ACCENT))

    # S-подібна дисперсійна крива ε_eff(f)
    pts = []
    for i in range(0, 380, 5):
        px = ox + i
        # Логістична сигмоїда дисперсії Kirschning-Jansen
        arg = (i - 160) / 45.0
        val = 1.0 / (1.0 + math.exp(-arg))
        py = y_low - val * (y_low - y_high)
        pts.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), LINK))

    # Зони на графіку
    # 1. Квазі-статична зона (DC - сотні МГц)
    f.append(rect(100, 230, 110, 50, fill="#f8fafc", stroke="#94a3b8", sw=1.0, rx=4))
    f.append(text(155, 248, "Квазістатика", size=11, bold=True, color=DARK))
    f.append(text(155, 266, "f < 1 ГГц", size=10, color=MUTED))

    # 2. Зона дисперсії
    f.append(rect(235, 145, 120, 50, fill="#eff6ff", stroke=LINK, sw=1.2, rx=4))
    f.append(text(295, 163, "Зона дисперсії", size=11, bold=True, color=LINK))
    f.append(text(295, 181, "1 ГГц < f < 30 ГГц", size=10, color=DARK))

    # 3. Високочастотна межа
    f.append(rect(380, 75, 115, 50, fill="#ecfdf5", stroke=ACCENT, sw=1.0, rx=4))
    f.append(text(437, 93, "Поле в підкладці", size=11, bold=True, color=ACCENT))
    f.append(text(437, 111, "ε_eff → ε_r", size=10, color=DARK))

    # Пояснювальний блок праворуч
    f.append(rect(535, 60, 205, 270, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(637, 85, "Фізичний механізм:", size=13, bold=True, color=DARK))

    f.append(text(548, 115, "1. Низькі частоти (DC):", size=11, bold=True, color=DARK, anchor="start"))
    f.append(text(548, 132, "Поле вільно виходить", size=11, color=MUTED, anchor="start"))
    f.append(text(548, 148, "в повітряний простір.", size=11, color=MUTED, anchor="start"))

    f.append(text(548, 180, "2. Високі частоти (НВЧ):", size=11, bold=True, color=LINK, anchor="start"))
    f.append(text(548, 197, "Електромагнітна енергія", size=11, color=DARK, anchor="start"))
    f.append(text(548, 213, "стягується під смужку", size=11, color=DARK, anchor="start"))
    f.append(text(548, 229, "всередину діелектрика.", size=11, color=DARK, anchor="start"))

    f.append(text(548, 260, "3. Наслідки дисперсії:", size=11, bold=True, color=ACCENT, anchor="start"))
    f.append(text(548, 277, "• ε_eff зростає", size=11, color=DARK, anchor="start"))
    f.append(text(548, 293, "• Швидкість v_p падає", size=11, color=DARK, anchor="start"))
    f.append(text(548, 309, "• Хвиля λ_g стискається", size=11, color=DARK, anchor="start"))

    return render(os.path.join(IMG, "fig-dispersion-curve.svg"), W, H, *f)


# ── Фігура 4: Чвертьхвильовий трансформатор та узгоджувальний шлейф ─────────────
def fig_quarterwave_stub():
    W, H = 760, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Топологія чвертьхвильового трансформатора та шлейфа на друкованій платі", size=16, bold=True))

    # Верхній блок: λ/4 трансформатор
    f.append(rect(30, 50, 700, 150, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(180, 72, "Чвертьхвильовий узгоджувальний трансформатор (λ_g / 4)", size=13, bold=True, color=DARK))

    # Секція 1: Вхідна лінія 50 Ом (ширина w₀)
    f.append(rect(50, 110, 110, 30, fill="#93c5fd", stroke=LINK, sw=1.5, rx=0))
    f.append(text(105, 128, "Z₀ = 50 Ω (w₀)", size=11, bold=True, color=DARK))

    # Секція 2: Трансформаторна секція Z_T (ширина w_T, довжина L = λ_g / 4)
    f.append(rect(160, 100, 180, 50, fill="#86efac", stroke=ACCENT, sw=1.8, rx=0))
    f.append(text(250, 123, "Z_T = √(Z₀ · R_L)", size=12, bold=True, color=DARK))
    f.append(text(250, 140, "Ширина w_T", size=11, color=MUTED))

    # Розмірна стрілка для довжини трансформатора L = λ_g / 4
    f.append(line(160, 165, 340, 165, color=ACCENT, sw=1.5))
    f.append(line(160, 160, 160, 170, color=ACCENT, sw=1.5))
    f.append(line(340, 160, 340, 170, color=ACCENT, sw=1.5))
    f.append(text(250, 180, "L_геом = λ_g / 4 = λ₀ / (4 · √(ε_eff))", size=11, bold=True, color=ACCENT))

    # Секція 3: Навантаження R_L (ширина w_L)
    f.append(rect(340, 118, 110, 14, fill="#fde68a", stroke="#d97706", sw=1.5, rx=0))
    f.append(text(395, 127, "R_L = 100 Ω", size=11, bold=True, color=DARK))

    # Інженерна формула трансформації праворуч
    f.append(rect(480, 80, 230, 105, fill="#eff6ff", stroke=LINK, sw=1.2, rx=4))
    f.append(text(595, 102, "Трансформація імпедансу:", size=12, bold=True, color=LINK))
    f.append(text(595, 126, "Z_вх = Z_T² / R_L = 50 Ω", size=12, bold=True, color=DARK))
    f.append(text(595, 148, "Помилка без ε_eff:", size=11, bold=True, color=POS))
    f.append(text(595, 168, "Зсув частоти на 25...40%", size=11, color=POS))

    # Нижній блок: Розімкнений шлейф і крайовий ефект (End-effect Δl)
    f.append(rect(30, 215, 700, 160, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(210, 237, "Розімкнений шлейф (Open Stub) та крайова ємність розриву Δl", size=13, bold=True, color=DARK))

    # Основна магістральна лінія
    f.append(rect(50, 275, 200, 24, fill="#93c5fd", stroke=LINK, sw=1.5, rx=0))
    f.append(text(150, 290, "Магістраль 50 Ω", size=11, bold=True, color=DARK))

    # Відгалужений шлейф (Stub)
    f.append(rect(170, 299, 45, 55, fill="#86efac", stroke=ACCENT, sw=1.5, rx=0))
    f.append(text(192, 330, "Шлейф", size=10, bold=True, color=DARK))

    # Крайове електричне поле розімкненого кінця (End-effect extension Δl)
    f.append('<rect x="170.0" y="354.0" width="45.0" height="12.0" fill="#fee2e2" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>' % POS)
    f.append(text(192, 363, "+Δl", size=9, bold=True, color=POS))

    # Розмірні лінії шлейфа
    f.append(line(225, 299, 235, 299, color=DARK, sw=1.0))
    f.append(line(225, 354, 235, 354, color=DARK, sw=1.0))
    f.append(line(230, 299, 230, 354, color=DARK, sw=1.0))
    f.append(text(275, 325, "L_фіз", size=11, bold=True, color=DARK))

    # Пояснення праворуч
    f.append(rect(330, 252, 380, 110, fill="#fffbeb", stroke="#f59e0b", sw=1.2, rx=4))
    f.append(text(520, 272, "Компенсація крайової ємності (End-Effect):", size=12, bold=True, color="#b45309"))
    f.append(text(345, 296, "Крайові лінії поля на відкритому кінці створюють", size=11, color=DARK, anchor="start"))
    f.append(text(345, 314, "додаткову паразитну ємність C_end, еквівалентну", size=11, color=DARK, anchor="start"))
    f.append(text(345, 332, "подовженню лінії на відрізок Δl ≈ 0.412 · h.", size=11, bold=True, color=DARK, anchor="start"))
    f.append(text(345, 350, "Фізична довжина: L_фіз = (λ_g / 4) − Δl", size=11, bold=True, color=POS, anchor="start"))

    return render(os.path.join(IMG, "fig-quarterwave-stub.svg"), W, H, *f)


if __name__ == "__main__":
    fig_microstrip_fields()
    fig_wavelength_compression()
    fig_dispersion_curve()
    fig_quarterwave_stub()
    print("Всі 4 фігури успішно згенеровано у ./img/")
