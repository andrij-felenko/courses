# -*- coding: utf-8 -*-
"""Фігури до теми «Коефіцієнт укорочення: хвиля в діелектрику».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""

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


# ── Фігура 1: Мікроскопічний механізм уповільнення хвилі ──────────────────────
def fig_polarization_wave():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 24, "Мікроскопічний механізм уповільнення електромагнітної хвилі", size=16, bold=True))

    # Зона 1: Вакуум (падаюча хвиля)
    f.append(rect(20, 50, 200, 240, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(120, 72, "Вакуум (ε_r = 1)", size=13, bold=True, color=INK))
    f.append(text(120, 90, "Швидкість c = 3·10⁸ м/с", size=11, color=MUTED))

    # Синусоїда первинної хвилі в зоні 1
    pts1 = []
    for x in range(30, 210, 4):
        y = 175 - 45 * math.sin((x - 30) * 2 * math.pi / 140)
        pts1.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts1), LINK))
    f.append(text(120, 240, "Первинна хвиля E₀(t)", size=12, bold=True, color=LINK))
    f.append(text(120, 260, "Довжина λ₀", size=11, color=MUTED))

    # Межа розділу
    f.append(line(220, 50, 220, 290, color=DARK, sw=2, dash="5,4"))

    # Зона 2: Діелектрик (поляризація та репромінювання)
    f.append(rect(220, 50, 520, 240, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    f.append(text(480, 72, "Діелектричне середовище (ε_r > 1)", size=13, bold=True, color=ACCENT))
    f.append(text(480, 90, "Швидкість v = c / √(ε_r) < c", size=11, color=DARK, bold=True))

    # Сітка атомів / диполів у діелектрику
    dipoles = [
        (260, 130), (320, 130), (380, 130), (440, 130), (500, 130),
        (290, 180), (350, 180), (410, 180), (470, 180), (530, 180),
        (260, 230), (320, 230), (380, 230), (440, 230), (500, 230)
    ]
    for cx, cy in dipoles:
        # Наводомий диполь (орієнтований полюс)
        f.append(line(cx - 10, cy, cx + 10, cy, color=MUTED, sw=1.2))
        f.append(circle(cx - 8, cy, 4, fill=POS, stroke=POS, sw=1))
        f.append(circle(cx + 8, cy, 4, fill=NEG, stroke=NEG, sw=1))

    # Звивиста вторинна хвиля зі зсувом фази
    pts2 = []
    for x in range(220, 730, 4):
        # Хвиля з коротшою довжиною хвилі (λ = λ₀ / 1.5)
        y = 180 - 40 * math.sin((x - 220) * 2 * math.pi / 93 + math.pi / 4)
        pts2.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts2), ACCENT))

    # Стрелочки вторинного випромінювання диполів
    f.append(arrow(350, 180, 385, 150, color=AMBER, sw=1.5))
    f.append(text(400, 145, "Вторинні хвилі (зсув фази Δφ)", size=10, bold=True, color=AMBER))

    f.append(text(620, 240, "Сумарна хвиля E_tot(t)", size=12, bold=True, color=ACCENT))
    f.append(text(620, 260, "Довжина λ = λ₀ · VF", size=11, color=DARK, bold=True))

    # Нижня пояснювальна картка
    b, w, h = textbox(W / 2, 335,
                      "Механізм: зміщення зв'язаних зарядів атомів під дією поля E₀ створює осцилювальні диполі.\n"
                      "Вторинне випромінювання диполів додається до первинної хвилі із запізненням фази,\n"
                      "формуючи результуючий хвильовий фронт, що рухається повільніше: v = c / √(ε_r · μ_r).",
                      size=11, pad=8, fill="#ffffff", stroke="#cbd5e1", sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "polarization-wave.svg"), W, H, *f)


# ── Фігура 2: Скорочення довжини хвилі та резонансних елементів ───────────────
def fig_wavelength_shortening():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 24, "Порівняння довжини хвилі у вакуумі та в діелектрику (f = 100 МГц)", size=16, bold=True))

    # Панель 1: Вакуум / Повітря
    f.append(rect(20, 50, 720, 125, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(40, 72, "Вакуум / Повітря: ε_r = 1.0,  VF = 1.0", size=12, bold=True, color=INK, anchor="start"))

    # Хвиля 1 (3 метри)
    pts1 = []
    x_start = 50
    for x in range(x_start, x_start + 600, 4):
        y = 115 - 35 * math.sin((x - x_start) * 2 * math.pi / 240)
        pts1.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts1), LINK))

    # Розмір хвилі λ₀ = 3.0 м
    f.append(line(x_start, 155, x_start + 240, 155, color=LINK, sw=1.5))
    f.append(circle(x_start, 155, 3, fill=LINK, stroke=LINK, sw=1))
    f.append(circle(x_start + 240, 155, 3, fill=LINK, stroke=LINK, sw=1))
    f.append(text(x_start + 120, 150, "Повна довжина хвилі λ₀ = 3.00 м", size=11, bold=True, color=LINK))

    # Чвертьхвильовий диполь у повітрі
    f.append(rect(520, 95, 180, 12, fill="#e2e8f0", stroke=DARK, sw=1.5, rx=2))
    f.append(line(610, 95, 610, 107, color=POS, sw=2))
    f.append(text(610, 85, "Чвертьхвильовий вибратор L₀ = λ₀/4 = 75.0 см", size=11, bold=True, color=DARK))

    # Панель 2: Діелектрик (PTFE / Фторопласт)
    f.append(rect(20, 190, 720, 125, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    f.append(text(40, 212, "Діелектрик (PTFE): ε_r = 2.25,  VF = 1 / √2.25 = 0.667", size=12, bold=True, color=ACCENT, anchor="start"))

    # Хвиля 2 (2 метри)
    pts2 = []
    for x in range(x_start, x_start + 600, 4):
        y = 255 - 35 * math.sin((x - x_start) * 2 * math.pi / 160)
        pts2.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts2), ACCENT))

    # Розмір хвилі λ = 2.0 м
    f.append(line(x_start, 295, x_start + 160, 295, color=ACCENT, sw=1.5))
    f.append(circle(x_start, 295, 3, fill=ACCENT, stroke=ACCENT, sw=1))
    f.append(circle(x_start + 160, 295, 3, fill=ACCENT, stroke=ACCENT, sw=1))
    f.append(text(x_start + 80, 290, "λ = λ₀ · VF = 2.00 м", size=11, bold=True, color=ACCENT))

    # Чвертьхвильовий диполь у діелектрику (скорочений)
    f.append(rect(520, 235, 120, 12, fill="#bbf7d0", stroke=DARK, sw=1.5, rx=2))
    f.append(line(580, 235, 580, 247, color=POS, sw=2))
    f.append(text(580, 225, "Резонансна довжина L = L₀ · VF = 50.0 см", size=11, bold=True, color=ACCENT))

    # Вертикальна пунктирна лінія співвідношення довжин
    f.append(line(x_start + 240, 120, x_start + 240, 305, color=MUTED, sw=1, dash="3,3"))
    f.append(line(x_start + 160, 220, x_start + 160, 305, color=ACCENT, sw=1, dash="3,3"))

    f.append(text(W / 2, 342, "Формула зв'язку:  λ = λ₀ · VF = (c / f) / √(ε_r)   ⇒   Фізичний розмір антен та шлейфів зменшується на 33.3%", size=11, italic=True, color=DARK))

    return render(os.path.join(IMG, "wavelength-shortening.svg"), W, H, *f)


# ── Фігура 3: Геометрія ліній передачі та ефективна проникність ──────────────
def fig_transmission_lines_fields():
    W, H = 780, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 24, "Розподіл полів і ефективна діелектрична проникність у лініях", size=16, bold=True))

    col_w = 236
    gap = 14
    x0 = 18 + col_w / 2

    # 1. Коаксіальний кабель
    cx1 = x0
    f.append(rect(cx1 - col_w/2, 48, col_w, 230, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(cx1, 68, "Коаксіальний кабель", size=13, bold=True, color=INK))

    # Переріз коаксіалу
    cy1 = 145
    f.append(circle(cx1, cy1, 48, fill="#e2e8f0", stroke=DARK, sw=2))  # Зовнішній екран
    f.append(circle(cx1, cy1, 42, fill="#dcfce7", stroke="#86efac", sw=1))  # Діелектрик
    f.append(circle(cx1, cy1, 14, fill="#bbf7d0", stroke=DARK, sw=1.5))  # Центральна жила

    # Електричні силові лінії (радіальні)
    for a in range(0, 360, 45):
        rad = math.radians(a)
        f.append(line(cx1 + 14 * math.cos(rad), cy1 + 14 * math.sin(rad),
                      cx1 + 42 * math.cos(rad), cy1 + 42 * math.sin(rad),
                      color=ACCENT, sw=1.2))

    b1, w1, h1 = textbox(cx1, 235,
                          "• Поле 100% у діелектрику\n"
                          "• Режим: чиста TEM-хвиля\n"
                          "• ε_eff = ε_r  (повна)\n"
                          "• VF = 1 / √(ε_r)",
                          size=11, pad=6, fill="#ffffff", stroke="#cbd5e1", sw=1)
    f.append(b1)

    # 2. Мікросмужкова лінія (Microstrip)
    cx2 = x0 + col_w + gap
    f.append(rect(cx2 - col_w/2, 48, col_w, 230, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(cx2, 68, "Мікросмужкова лінія", size=13, bold=True, color=INK))

    cy2 = 145
    # Заземлена площина
    f.append(rect(cx2 - 70, cy2 + 25, 140, 8, fill="#64748b", stroke=DARK, sw=1.2))
    # Підкладка FR-4
    f.append(rect(cx2 - 70, cy2 - 10, 140, 35, fill="#fef3c7", stroke="#fde047", sw=1.2))
    # Провідник траси
    f.append(rect(cx2 - 25, cy2 - 18, 50, 8, fill="#f97316", stroke=DARK, sw=1.2))

    # Силові лінії поля (крайові в повітрі + силові в підкладці)
    for dx in (-35, -20, 0, 20, 35):
        f.append(line(cx2 + dx, cy2 - 10, cx2 + dx, cy2 + 25, color=AMBER, sw=1.2))
    # Крайове поле в повітрі
    f.append('<path d="M %f %f Q %f %f %f %f" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,2"/>' %
             (cx2 - 25, cy2 - 14, cx2 - 50, cy2 - 15, cx2 - 55, cy2 + 25, LINK))
    f.append('<path d="M %f %f Q %f %f %f %f" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,2"/>' %
             (cx2 + 25, cy2 - 14, cx2 + 50, cy2 - 15, cx2 + 55, cy2 + 25, LINK))

    b2, w2, h2 = textbox(cx2, 235,
                          "• Поле розділене: повітря + FR-4\n"
                          "• Режим: квазі-TEM хвиля\n"
                          "• 1 < ε_eff < ε_r  (часткова)\n"
                          "• VF = 1 / √(ε_eff)",
                          size=11, pad=6, fill="#ffffff", stroke="#cbd5e1", sw=1)
    f.append(b2)

    # 3. Смужкова лінія (Stripline)
    cx3 = x0 + 2 * (col_w + gap)
    f.append(rect(cx3 - col_w/2, 48, col_w, 230, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(cx3, 68, "Смужкова лінія (Stripline)", size=13, bold=True, color=INK))

    cy3 = 145
    # Верхня й нижня землі
    f.append(rect(cx3 - 70, cy3 - 40, 140, 8, fill="#64748b", stroke=DARK, sw=1.2))
    f.append(rect(cx3 - 70, cy3 + 32, 140, 8, fill="#64748b", stroke=DARK, sw=1.2))
    # Діелектрик між ними
    f.append(rect(cx3 - 70, cy3 - 32, 140, 64, fill="#ede9fe", stroke="#c4b5fd", sw=1.2))
    # Внутрішня траса
    f.append(rect(cx3 - 25, cy3 - 4, 50, 8, fill="#8b5cf6", stroke=DARK, sw=1.2))

    # Силові лінії вгору й вниз
    for dx in (-20, 0, 20):
        f.append(line(cx3 + dx, cy3 - 4, cx3 + dx, cy3 - 32, color=PURPLE, sw=1.2))
        f.append(line(cx3 + dx, cy3 + 4, cx3 + dx, cy3 + 32, color=PURPLE, sw=1.2))

    b3, w3, h3 = textbox(cx3, 235,
                          "• Поле 100% закрите в підкладці\n"
                          "• Режим: чиста TEM-хвиля\n"
                          "• ε_eff = ε_r  (повна)\n"
                          "• VF = 1 / √(ε_r)",
                          size=11, pad=6, fill="#ffffff", stroke="#cbd5e1", sw=1)
    f.append(b3)

    f.append(text(W / 2, 338, "Ключовий висновок: у мікросмужці швидкість поширення вища (VF ≈ 0.55..0.60), ніж у смужковій лінії (VF ≈ 0.48 для FR-4)", size=11, italic=True, color=DARK))

    return render(os.path.join(IMG, "transmission-lines-fields.svg"), W, H, *f)


# ── Фігура 4: Принцип імпульсної рефлектометрії (TDR) ─────────────────────────
def fig_tdr_principle_pulse():
    W, H = 760, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 24, "Принцип локалізації пошкоджень кабелю методом TDR", size=16, bold=True))

    # Схема кабелю
    f.append(rect(30, 55, 340, 110, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(200, 75, "Тестований кабель (довжина d)", size=12, bold=True, color=INK))

    # Зонд TDR
    f.append(rect(45, 95, 50, 45, fill="#eff6ff", stroke=LINK, sw=1.5, rx=4))
    f.append(text(70, 122, "TDR", size=12, bold=True, color=LINK))

    # Лінії кабелю
    f.append(line(95, 105, 330, 105, color=DARK, sw=2))
    f.append(line(95, 130, 330, 130, color=DARK, sw=2))
    f.append(rect(95, 107, 235, 21, fill="#dcfce7", stroke="none"))  # Діелектрик кабелю

    # Падаючий імпульс (праворуч)
    f.append(arrow(120, 95, 180, 95, color=LINK, sw=2))
    f.append(text(150, 87, "Падаючий імпульс U_inc", size=10, bold=True, color=LINK))

    # Точка пошкодження (обрив / обриз)
    f.append(line(330, 95, 330, 140, color=POS, sw=2.5))
    f.append(circle(330, 117, 6, fill=POS, stroke=DARK, sw=1))
    f.append(text(330, 85, "Обрив кабелю (x = d)", size=11, bold=True, color=POS))

    # Відбитий імпульс (ліворуч)
    f.append(arrow(260, 140, 200, 140, color=ACCENT, sw=2))
    f.append(text(230, 153, "Відбитий імпульс U_refl", size=10, bold=True, color=ACCENT))

    # Осцилограма праворуч
    f.append(rect(400, 55, 330, 200, fill="#0f172a", stroke="#334155", sw=1.5, rx=6))
    f.append(text(565, 78, "Рефлектограма на екрані", size=12, bold=True, color="#ffffff"))

    # Осі осцилографа
    f.append(line(420, 190, 710, 190, color="#64748b", sw=1.2))
    f.append(line(430, 90, 430, 230, color="#64748b", sw=1.2))
    f.append(text(715, 194, "t", size=11, color="#cbd5e1"))
    f.append(text(420, 95, "U", size=11, color="#cbd5e1"))

    # Сигнал TDR (два піки)
    # Зондувальний пік при t = 0
    f.append('<polyline points="430,190 440,190 445,110 455,110 460,190" fill="none" stroke="#38bdf8" stroke-width="2.2"/>')
    f.append(text(450, 100, "t = 0", size=10, color="#38bdf8", bold=True))

    # Пунктирна лінія інтервалу T
    f.append(line(450, 200, 640, 200, color="#f59e0b", sw=1.5))
    f.append(circle(450, 200, 3, fill="#f59e0b", stroke="#f59e0b", sw=1))
    f.append(circle(640, 200, 3, fill="#f59e0b", stroke="#f59e0b", sw=1))
    f.append(text(545, 215, "Час затримки ΔT", size=11, bold=True, color="#f59e0b"))

    # Відбитий пік при t = T
    f.append('<polyline points="460,190 630,190 635,110 645,110 650,190 710,190" fill="none" stroke="#4ade80" stroke-width="2.2"/>')
    f.append(text(640, 100, "t = ΔT", size=10, color="#4ade80", bold=True))

    # Формульний блок внизу
    b, w, h = textbox(W / 2, 295,
                      "Розрахунок відстані:  d = (v · ΔT) / 2 = (c · VF · ΔT) / 2\n"
                      "Помилка в значенні VF призводить до пропорційної помилки локалізації пошкодження!",
                      size=11, pad=8, fill="#ffffff", stroke="#cbd5e1", sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "tdr-principle-pulse.svg"), W, H, *f)


if __name__ == "__main__":
    p1 = fig_polarization_wave()
    p2 = fig_wavelength_shortening()
    p3 = fig_transmission_lines_fields()
    p4 = fig_tdr_principle_pulse()
    print("written:")
    for p in (p1, p2, p3, p4):
        print("  ", p)
