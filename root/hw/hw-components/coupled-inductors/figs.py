# -*- coding: utf-8 -*-
"""Фігури до статті «Зв'язані котушки в силовій електроніці» (book/electronics/components/coupled-inductors).
Генерує векторні SVG-ілюстрації у ./img/ за допомогою svgkit.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
from svgkit import (text, mtext, rect, line, arrow, circle, render, INK, MUTED, POS, NEG,
                    FIELD, FILL, BG, LINE)  # noqa: E402

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

CORECOL = "#374151"   # темно-сірий магнітопровід
COPPER1 = "#b45309"   # обмотка фази 1
COPPER2 = "#1d4ed8"   # обмотка фази 2
FLUXCOL = "#059669"   # взаємний потік
LEAKCOL = "#dc2626"   # потік розсіювання
PANELBG = "#f8fafc"


def fig_core_coupling():
    """Фігура 1: Розподіл магнітних потоків у зв'язаних обмотках (взаємний потік та розсіювання)."""
    W, H = 840, 440
    frags = []

    # Загальне тло
    frags.append(rect(15, 15, 810, 410, fill=PANELBG, stroke=MUTED, sw=1.5, rx=8))

    # Заголовок блоку
    frags.append(text(420, 45, "Магнітні потоки двох зв'язаних обмоток на спільному осерді", size=16, color=INK, bold=True))
    frags.append(text(420, 68, "Повний потік кожної обмотки: Φ = Φ_m (взаємний зв'язок) + Φ_lk (розсіювання в повітря)", size=12, color=MUTED))

    # Прямокутне осердя (рамка з вікном)
    # Зовнішній контур: x=140..700, y=100..340, внутрішнє вікно: x=240..600, y=170..270
    frags.append('<path d="M 140,100 L 700,100 L 700,340 L 140,340 Z M 240,170 L 240,270 L 600,270 L 600,170 Z" '
                 'fill="%s" fill-rule="evenodd" stroke="#1f2937" stroke-width="2"/>' % CORECOL)

    # Лінія основного магнітного потоку Φ_m всередині осердя (зелений пунктир зі стрілками)
    frags.append('<path d="M 190,135 L 650,135 L 650,305 L 190,305 Z" fill="none" stroke="%s" stroke-width="3" stroke-dasharray="8,5"/>' % FLUXCOL)
    frags.append(text(420, 125, "Спільний потік в осерді: Φ_m (індуктивність намагнічування L_m)", size=12, color=FIELD, bold=True))
    frags.append(text(420, 323, "Коефіцієнт зв'язку k = M / √(L₁·L₂) = Φ_m / Φ_повний", size=12, color=FIELD, bold=True))

    # Обмотка 1 на лівому керні (мідна котушка)
    for y in range(160, 280, 22):
        frags.append(rect(115, y, 50, 14, fill="#fef3c7", stroke=COPPER1, sw=2, rx=3))
    frags.append(text(80, 165, "Вхід 1 (●)", size=12, color=COPPER1, bold=True))
    frags.append(text(80, 285, "Вихід 1", size=12, color=COPPER1, bold=True))
    frags.append(arrow(60, 180, 110, 180, color=COPPER1, sw=2))
    frags.append(arrow(110, 270, 60, 270, color=COPPER1, sw=2))
    frags.append(text(80, 220, "Обмотка 1\n(L₁, i₁)", size=12, color=COPPER1, bold=True))

    # Потік розсіювання 1 (замикається через повітря навколо лівої обмотки)
    frags.append('<path d="M 190,180 C 230,180 230,260 190,260" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="5,4"/>' % LEAKCOL)
    frags.append('<path d="M 140,180 C 100,180 100,260 140,260" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="5,4"/>' % LEAKCOL)
    frags.append(text(285, 220, "Розсіювання Φ_lk1\n(L_lk1 = (1−k)·L₁)", size=11, color=LEAKCOL, bold=True))

    # Обмотка 2 на правому керні
    for y in range(160, 280, 22):
        frags.append(rect(675, y, 50, 14, fill="#dbeafe", stroke=COPPER2, sw=2, rx=3))
    frags.append(text(760, 165, "Вхід 2 (●)", size=12, color=COPPER2, bold=True))
    frags.append(text(760, 285, "Вихід 2", size=12, color=COPPER2, bold=True))
    frags.append(arrow(780, 180, 730, 180, color=COPPER2, sw=2))
    frags.append(arrow(730, 270, 780, 270, color=COPPER2, sw=2))
    frags.append(text(760, 220, "Обмотка 2\n(L₂, i₂)", size=12, color=COPPER2, bold=True))

    # Потік розсіювання 2
    frags.append('<path d="M 650,180 C 610,180 610,260 650,260" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="5,4"/>' % LEAKCOL)
    frags.append('<path d="M 700,180 C 740,180 740,260 700,260" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="5,4"/>' % LEAKCOL)
    frags.append(text(555, 220, "Розсіювання Φ_lk2\n(L_lk2 = (1−k)·L₂)", size=11, color=LEAKCOL, bold=True))

    # Пояснювальний підсумок знизу
    frags.append(rect(30, 360, 780, 50, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(420, 388, "Еквівалентна схема: кожна обмотка діє як послідовні L_leak та L_m. При k → 1 розсіювання зникає.", size=12, color=INK))

    return render(os.path.join(IMG, "core-coupling.svg"), W, H, *frags)


def fig_interleaved_buck_coupling():
    """Фігура 2: Порівняння згідного (Direct) та зустрічного (Inverse) зв'язку в 2-фазному Buck."""
    W, H = 860, 450
    frags = []

    # Ліва панель: Згідне включення (Direct Coupling, k > 0)
    frags.append(rect(15, 15, 405, 420, fill=PANELBG, stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(217, 45, "Згідний зв'язок (Direct Coupling, k > 0)", size=14, color=POS, bold=True))
    frags.append(text(217, 68, "Потоки постійного струму DC ДОДАЮТЬСЯ в осерді", size=11.5, color=MUTED))

    # Магнітопровід лівий (2 керни)
    frags.append('<path d="M 80,100 L 355,100 L 355,250 L 80,250 Z M 150,150 L 150,200 L 285,200 L 285,150 Z" '
                 'fill="%s" fill-rule="evenodd" stroke="#1f2937" stroke-width="1.5"/>' % CORECOL)
    # Обмотки
    frags.append(rect(65, 140, 30, 70, fill="#fef3c7", stroke=COPPER1, sw=2, rx=3))
    frags.append(rect(340, 140, 30, 70, fill="#dbeafe", stroke=COPPER2, sw=2, rx=3))
    frags.append(text(80, 130, "● L₁", size=12, color=COPPER1, bold=True))
    frags.append(text(355, 130, "● L₂", size=12, color=COPPER2, bold=True))

    # Стрілки сумування потоків
    frags.append(arrow(80, 175, 115, 175, color=POS, sw=2.5))
    frags.append(arrow(355, 175, 320, 175, color=POS, sw=2.5))
    frags.append(text(217, 125, "Φ_dc = Φ₁ + Φ₂ (удвічі більший!)", size=11, color=POS, bold=True))
    frags.append(text(217, 175, "Осердя швидко\nнасичується", size=12, color=POS, bold=True))

    # Результати для лівої панелі
    frags.append(rect(30, 270, 375, 150, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(mtext(217, 295, [
        "✖ Сумарний постійний потік Φ_dc подвоюється",
        "✖ Вимагає великого немагнітного зазору й габаритів",
        "✖ Пульсації фазного струму ЗБІЛЬШУЮТЬСЯ",
        "✖ Еквівалентна індуктивність для змінного струму:",
        "    L_eq,ss = L · (1 − k²) / (1 + k · D/(1−D)) < L",
        "Висновок: у понижувальних DCDC НЕ застосовується."
    ], size=11, color=INK, lh=1.35))

    # Права панель: Зустрічне включення (Inverse Coupling, k < 0)
    frags.append(rect(440, 15, 405, 420, fill=PANELBG, stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(642, 45, "Зустрічний зв'язок (Inverse Coupling, k < 0)", size=14, color=FIELD, bold=True))
    frags.append(text(642, 68, "Потоки постійного струму DC ВЗАЄМОЗНИЩУЮТЬСЯ", size=11.5, color=MUTED))

    # Магнітопровід правий
    frags.append('<path d="M 505,100 L 780,100 L 780,250 L 505,250 Z M 575,150 L 575,200 L 710,200 L 710,150 Z" '
                 'fill="%s" fill-rule="evenodd" stroke="#1f2937" stroke-width="1.5"/>' % CORECOL)
    # Обмотки (протифазне підключення - крапка знизу у другої обмотки)
    frags.append(rect(490, 140, 30, 70, fill="#fef3c7", stroke=COPPER1, sw=2, rx=3))
    frags.append(rect(765, 140, 30, 70, fill="#dbeafe", stroke=COPPER2, sw=2, rx=3))
    frags.append(text(505, 130, "● L₁", size=12, color=COPPER1, bold=True))
    frags.append(text(780, 225, "● L₂", size=12, color=COPPER2, bold=True))

    # Стрілки циркуляції потоку
    frags.append(arrow(505, 175, 540, 175, color=FIELD, sw=2.5))
    frags.append(arrow(745, 175, 780, 175, color=FIELD, sw=2.5))
    frags.append(text(642, 125, "Φ_dc(осердя) = Φ₁ − Φ₂ ≈ 0 !", size=11.5, color=FIELD, bold=True))
    frags.append(text(642, 175, "Осердя розвантажене,\nгабарити менші на 40%", size=12, color=FIELD, bold=True))

    # Результати для правої панелі
    frags.append(rect(455, 270, 375, 150, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(mtext(642, 295, [
        "✓ Постійні потоки від струмів навантаження гасяться",
        "✓ Пульсації струму у фазах ЗМЕНШУЮТЬСЯ у 2..5 разів",
        "✓ Ефективна індуктивність для пульсацій L_eq,ss >> L",
        "✓ Динамічна індуктивність для стрибка струму мала:",
        "    L_eq,tr = L · (1 − |k|)  →  блискавичний відгук",
        "Стандарт де-факто для живлення CPU/GPU (VRM)!"
    ], size=11, color=INK, lh=1.35))

    return render(os.path.join(IMG, "interleaved-buck-coupling.svg"), W, H, *frags)


def fig_transient_vs_ripple():
    """Фігура 3: Порівняння пульсацій струму та перехідного відгуку: роздільні vs зв'язані дроселі."""
    W, H = 860, 420
    frags = []

    frags.append(rect(15, 15, 830, 390, fill=PANELBG, stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(430, 42, "Динамічний компроміс: роздільні котушки проти зв'язаних дроселів", size=15, color=INK, bold=True))
    frags.append(text(430, 64, "Як зустрічний зв'язок (Inverse Coupling) одночасно дає малі пульсації та миттєвий відгук на стрибок навантаження", size=11.5, color=MUTED))

    # Схема графіків: 3 графіки струму в часі
    # Графік 1: Роздільні великі котушки (L = 1 мкГн)
    frags.append(rect(35, 90, 245, 230, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(157, 110, "1. Роздільні великі (L=1.0 мкГн)", size=11.5, color=INK, bold=True))
    # Сітка
    frags.append(line(55, 260, 260, 260, color="#9ca3af", sw=1))
    frags.append(line(55, 130, 55, 260, color="#9ca3af", sw=1))
    # Хвиля: мала пульсація в стаціонарі, повільне зростання при стрибку
    frags.append('<path d="M 55,230 L 75,220 L 95,230 L 115,220 L 135,230 L 140,230 L 220,150 L 240,160 L 260,150" '
                 'fill="none" stroke="%s" stroke-width="2.5"/>' % COPPER1)
    frags.append(text(157, 280, "Пульсації: МАЛІ (добре)\nСтрибок: ПОВІЛЬНИЙ (прогин Vout)", size=10.5, color=NEG))

    # Графік 2: Роздільні малі котушки (L = 0.2 мкГн)
    frags.append(rect(305, 90, 245, 230, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(427, 110, "2. Роздільні малі (L=0.2 мкГн)", size=11.5, color=INK, bold=True))
    frags.append(line(325, 260, 530, 260, color="#9ca3af", sw=1))
    frags.append(line(325, 130, 325, 260, color="#9ca3af", sw=1))
    # Хвиля: величезна пульсація, але швидкий стрибок
    frags.append('<path d="M 325,245 L 345,205 L 365,245 L 385,205 L 405,245 L 410,245 L 440,150 L 460,190 L 480,150 L 500,190 L 520,150" '
                 'fill="none" stroke="%s" stroke-width="2.5"/>' % POS)
    frags.append(text(427, 280, "Пульсації: ВЕЛИЧЕЗНІ (втрати ESR)\nСтрибок: ШВИДКИЙ (без прогину)", size=10.5, color=POS))

    # Графік 3: Зв'язані дроселі (L=0.2 мкГн, k = -0.7)
    frags.append(rect(575, 90, 250, 230, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(700, 110, "3. Зв'язані дроселі (|k|=0.7)", size=11.5, color=FIELD, bold=True))
    frags.append(line(595, 260, 805, 260, color="#9ca3af", sw=1))
    frags.append(line(595, 130, 595, 260, color="#9ca3af", sw=1))
    # Хвиля: малі пульсації (L_eq,ss велика) І швидкий стрибок (L_eq,tr мала)
    frags.append('<path d="M 595,230 L 615,222 L 635,230 L 655,222 L 675,230 L 680,230 L 710,150 L 730,142 L 750,150 L 770,142 L 790,150" '
                 'fill="none" stroke="%s" stroke-width="3"/>' % FIELD)
    frags.append(text(700, 280, "Пульсації: МАЛІ (L_eq,ss ≈ 0.8 мкГн)\nСтрибок: ШВИДКИЙ (L_eq,tr = 0.06 мкГн)", size=10.5, color=FIELD, bold=True))

    # Порівняльний блок знизу
    frags.append(rect(35, 335, 790, 55, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(430, 362, "Зв'язаний дросель розриває суперечність: у стаціонарі діє як велика фільтрувальна індуктивність,\nа під час різкого навантаження — як надмала котушка для миттєвого наростання струму.", size=11.5, color=INK))

    return render(os.path.join(IMG, "transient-vs-ripple.svg"), W, H, *frags)


def fig_coupled_topologies():
    """Фігура 4: Схеми топологій із використанням зв'язаних індуктивностей (SEPIC, Ćuk, Interleaved Buck)."""
    W, H = 860, 430
    frags = []

    frags.append(rect(15, 15, 830, 400, fill=PANELBG, stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(430, 42, "Топології імпульсних перетворювачів зі зв'язаними індуктивностями", size=15, color=INK, bold=True))
    frags.append(text(430, 64, "Спільне осердя зменшує кількість деталей, габарити та спрямовує пульсації струму до нуля", size=11.5, color=MUTED))

    # 1. SEPIC (лівий блок)
    frags.append(rect(30, 85, 255, 310, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(157, 108, "SEPIC зі зв'язком L₁-L₂", size=13, color=INK, bold=True))
    # Спрощена схема
    frags.append(text(50, 140, "Vin", size=11, bold=True))
    frags.append(line(70, 140, 100, 140, color=LINE, sw=1.5))
    # L1
    frags.append(rect(100, 130, 35, 20, fill="#fef3c7", stroke=COPPER1, sw=1.5, rx=2))
    frags.append(text(117, 145, "L₁", size=10, color=COPPER1, bold=True))
    frags.append(text(105, 125, "●", size=11, color=COPPER1))
    frags.append(line(135, 140, 160, 140, color=LINE, sw=1.5))
    # C_cp
    frags.append(line(160, 140, 175, 140, color=LINE, sw=1.5))
    frags.append(line(175, 130, 175, 150, color=LINE, sw=2))
    frags.append(line(180, 130, 180, 150, color=LINE, sw=2))
    frags.append(text(177, 122, "C_s", size=10, bold=True))
    frags.append(line(180, 140, 205, 140, color=LINE, sw=1.5))
    # D diode
    frags.append(line(205, 140, 220, 140, color=LINE, sw=1.5))
    frags.append(line(220, 140, 245, 140, color=LINE, sw=1.5))
    frags.append(text(255, 140, "Vout", size=11, bold=True))
    # Switch SW down
    frags.append(line(160, 140, 160, 175, color=LINE, sw=1.5))
    frags.append(rect(150, 175, 20, 20, fill="#fee2e2", stroke=POS, sw=1.5, rx=2))
    frags.append(text(160, 189, "Q", size=10, bold=True))
    frags.append(line(160, 195, 160, 220, color=LINE, sw=1.5))
    # L2 down
    frags.append(line(205, 140, 205, 165, color=LINE, sw=1.5))
    frags.append(rect(190, 165, 30, 25, fill="#dbeafe", stroke=COPPER2, sw=1.5, rx=2))
    frags.append(text(205, 182, "L₂", size=10, color=COPPER2, bold=True))
    frags.append(text(195, 160, "●", size=11, color=COPPER2))
    frags.append(line(205, 190, 205, 220, color=LINE, sw=1.5))
    # Core link
    frags.append(line(125, 155, 195, 155, color=FIELD, sw=2, dash="3,3"))
    frags.append(text(157, 172, "k ≈ 0.9", size=9.5, color=FIELD, bold=True))
    # Ground
    frags.append(line(70, 220, 245, 220, color=LINE, sw=1.5))
    # Опис переваг
    frags.append(mtext(157, 260, [
        "• Напруги на L₁ та L₂ ідентичні",
        "• Об'єднання на одному осерді",
        "  заощаджує 50% площі на платі",
        "• При k = √(L₂/L₁) пульсації",
        "  вхідного струму стікають до нуля!"
    ], size=10.5, color=INK, lh=1.35))

    # 2. Ćuk перетворювач (середній блок)
    frags.append(rect(300, 85, 255, 310, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(427, 108, "Інвертувальний перетворювач Чука", size=12.5, color=INK, bold=True))
    # Схема
    frags.append(text(318, 140, "Vin", size=11, bold=True))
    frags.append(rect(345, 130, 35, 20, fill="#fef3c7", stroke=COPPER1, sw=1.5, rx=2))
    frags.append(text(362, 145, "L₁", size=10, color=COPPER1, bold=True))
    frags.append(line(380, 140, 420, 140, color=LINE, sw=1.5))
    # C transfer
    frags.append(line(420, 130, 420, 150, color=LINE, sw=2))
    frags.append(line(425, 130, 425, 150, color=LINE, sw=2))
    frags.append(text(422, 122, "C₁", size=10, bold=True))
    frags.append(line(425, 140, 465, 140, color=LINE, sw=1.5))
    # L2
    frags.append(rect(465, 130, 35, 20, fill="#dbeafe", stroke=COPPER2, sw=1.5, rx=2))
    frags.append(text(482, 145, "L₂", size=10, color=COPPER2, bold=True))
    frags.append(line(500, 140, 525, 140, color=LINE, sw=1.5))
    frags.append(text(538, 140, "−Vout", size=11, bold=True))
    # Switch & Diode
    frags.append(rect(390, 175, 20, 20, fill="#fee2e2", stroke=POS, sw=1.5, rx=2))
    frags.append(text(400, 189, "Q", size=10, bold=True))
    frags.append(line(400, 140, 400, 175, color=LINE, sw=1.5))
    frags.append(line(400, 195, 400, 220, color=LINE, sw=1.5))
    # Diode D
    frags.append(line(445, 140, 445, 220, color=LINE, sw=1.5))
    frags.append(line(330, 220, 525, 220, color=LINE, sw=1.5))
    # Core link
    frags.append(line(375, 155, 475, 155, color=FIELD, sw=2, dash="3,3"))
    frags.append(text(422, 170, "k ≈ 0.9", size=9.5, color=FIELD, bold=True))
    # Опис
    frags.append(mtext(427, 260, [
        "• Неперервний вхідний І вихідний струм",
        "• Єдине магнітне осердя для обох кіл",
        "• Можливість досягти нульових",
        "  пульсацій на ВХОДІ або на ВИХОДІ",
        "  завдяки підбору L_leakage"
    ], size=10.5, color=INK, lh=1.35))

    # 3. Interleaved Buck (правий блок)
    frags.append(rect(570, 85, 260, 310, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(700, 108, "2-Phase Interleaved Buck", size=13, color=INK, bold=True))
    # Схема 2 фаз
    frags.append(text(585, 130, "Vin", size=10, bold=True))
    frags.append(rect(610, 125, 22, 18, fill="#fee2e2", stroke=POS, sw=1.5, rx=2))
    frags.append(text(621, 137, "Q₁", size=9.5, bold=True))
    frags.append(rect(610, 165, 22, 18, fill="#fee2e2", stroke=POS, sw=1.5, rx=2))
    frags.append(text(621, 177, "Q₂", size=9.5, bold=True))
    # Котушки
    frags.append(rect(660, 125, 35, 18, fill="#fef3c7", stroke=COPPER1, sw=1.5, rx=2))
    frags.append(text(677, 138, "L₁", size=10, color=COPPER1, bold=True))
    frags.append(rect(660, 165, 35, 18, fill="#dbeafe", stroke=COPPER2, sw=1.5, rx=2))
    frags.append(text(677, 178, "L₂", size=10, color=COPPER2, bold=True))
    # Зв'язок
    frags.append(line(677, 145, 677, 163, color=FIELD, sw=2, dash="3,3"))
    frags.append(text(715, 154, "k < 0", size=10, color=FIELD, bold=True))
    # Вихід
    frags.append(line(695, 134, 760, 134, color=LINE, sw=1.5))
    frags.append(line(695, 174, 760, 174, color=LINE, sw=1.5))
    frags.append(line(760, 134, 760, 174, color=LINE, sw=1.5))
    frags.append(line(760, 154, 790, 154, color=LINE, sw=1.5))
    frags.append(text(805, 154, "Vout", size=11, bold=True))
    # Опис
    frags.append(mtext(700, 260, [
        "• Зсув фаз 180° для ШІМ-ключів",
        "• Зустрічний магнітний зв'язок k < 0",
        "• Рекордна щільність струму (VRM)",
        "• Ефективність на 2-4% вища,",
        "  ніж у дискретних дроселів"
    ], size=10.5, color=INK, lh=1.35))

    return render(os.path.join(IMG, "coupled-topologies.svg"), W, H, *frags)


def fig_zvs_leakage():
    """Фігура 5: Використання L_leakage для забезпечення м'якої комутації (ZVS)."""
    W, H = 840, 420
    frags = []

    frags.append(rect(15, 15, 810, 390, fill=PANELBG, stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(420, 42, "М'яка комутація (ZVS) за рахунок індуктивності розсіювання L_leak", size=15, color=INK, bold=True))
    frags.append(text(420, 64, "Енергія, накопичена в розсіюванні (0.5·L_leak·I²), перезаряджає паразитивні ємності C_oss під час мертвого часу t_dead", size=11.5, color=MUTED))

    # Схема півмоста з Coss та L_leak
    frags.append(rect(35, 95, 340, 290, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(205, 120, "Схема перезаряду ємностей у Dead Time", size=12.5, color=INK, bold=True))

    # Рейка Vin та GND
    frags.append(line(70, 140, 250, 140, color=POS, sw=2))
    frags.append(text(55, 140, "Vin", size=11, color=POS, bold=True))
    frags.append(line(70, 340, 250, 340, color=NEG, sw=2))
    frags.append(text(55, 340, "GND", size=11, color=NEG, bold=True))

    # Верхній ключ Q1 та C_oss1
    frags.append(rect(90, 160, 45, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(112, 187, "Q₁ (OFF)", size=10, bold=True))
    frags.append(line(160, 160, 160, 205, color=LINE, sw=1.5))
    frags.append(rect(150, 175, 20, 15, fill="#dbeafe", stroke=NEG, sw=1.5, rx=2))
    frags.append(text(190, 185, "C_oss1", size=10, color=NEG, bold=True))

    # Середня точка SW
    frags.append(line(112, 140, 112, 160, color=LINE, sw=1.5))
    frags.append(line(112, 205, 112, 270, color=LINE, sw=1.5))
    frags.append(circle(112, 237, 4, fill=INK, stroke=INK))
    frags.append(text(85, 237, "V_sw", size=11, bold=True))

    # Нижній ключ Q2 та C_oss2
    frags.append(rect(90, 270, 45, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(112, 297, "Q₂ (OFF)", size=10, bold=True))
    frags.append(line(160, 270, 160, 315, color=LINE, sw=1.5))
    frags.append(rect(150, 285, 20, 15, fill="#dbeafe", stroke=NEG, sw=1.5, rx=2))
    frags.append(text(190, 295, "C_oss2", size=10, color=NEG, bold=True))
    frags.append(line(112, 315, 112, 340, color=LINE, sw=1.5))

    # Вихідний струм через L_leak
    frags.append(line(112, 237, 230, 237, color=LINE, sw=2))
    frags.append(rect(230, 227, 40, 20, fill="#fecaca", stroke=LEAKCOL, sw=1.5, rx=2))
    frags.append(text(250, 241, "L_leak", size=10, color=LEAKCOL, bold=True))
    frags.append(arrow(270, 237, 330, 237, color=FIELD, sw=2.5))
    frags.append(text(300, 222, "I_L (струм ZVS)", size=10.5, color=FIELD, bold=True))

    # Права панель: часові діаграми напруги V_sw та струму
    frags.append(rect(395, 95, 410, 290, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(600, 120, "Енергетичний баланс резонансного переходу", size=12.5, color=INK, bold=True))

    # Формули та кроки
    frags.append(rect(410, 140, 380, 230, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    frags.append(mtext(600, 165, [
        "1. Умова повного розряду C_oss для 100% ZVS:",
        "    0.5 · L_leak · I_pk²  ≥  0.5 · (C_oss1 + C_oss2) · Vin²",
        "",
        "2. Мінімальний струм для досягнення нульової напруги:",
        "    I_pk,min = Vin · √(2·C_oss / L_leak)",
        "",
        "3. Необхідна тривалість мертвого часу (Dead Time):",
        "    t_dead ≈ (π / 2) · √(L_leak · 2·C_oss)",
        "",
        "Результат: транзистор відкривається при V_ds = 0 В.",
        "Динамічні втрати вмикання P_sw = 0.5·f·C·V² ПОВНІСТЮ ЗНИКАЮТЬ!"
    ], size=11, color=INK, lh=1.35))

    return render(os.path.join(IMG, "zvs-leakage.svg"), W, H, *frags)


def fig_core_reluctance_model():
    """Фігура 6: Магнітна схема заміщення (Reluctance model) та електрична Т-подібна модель."""
    W, H = 840, 420
    frags = []

    frags.append(rect(15, 15, 810, 390, fill=PANELBG, stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(420, 42, "Магнітний опір та еквівалентна схема зв'язаних індуктивностей", size=15, color=INK, bold=True))
    frags.append(text(420, 64, "Від магнітних шляхів осердя (Reluctance network) до електричної Т-моделі (L_leak1, L_leak2, L_m)", size=11.5, color=MUTED))

    # Ліва панель: Магнітна схема опорів (Reluctance network)
    frags.append(rect(35, 90, 365, 300, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(217, 115, "Магнітне коло: опір шляхів (Reluctance ℛ)", size=12.5, color=INK, bold=True))

    # Контур магнітної схеми
    frags.append(rect(70, 160, 35, 25, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    frags.append(text(87, 177, "N₁·i₁", size=10.5, color=POS, bold=True))
    frags.append(line(87, 140, 87, 160, color=LINE, sw=1.5))
    frags.append(line(87, 185, 87, 240, color=LINE, sw=1.5))

    # Магнітний опір розсіювання R_lk1
    frags.append(rect(130, 160, 40, 22, fill="#fef3c7", stroke=LEAKCOL, sw=1.5, rx=2))
    frags.append(text(150, 175, "ℛ_lk1", size=10, color=LEAKCOL, bold=True))

    # Магнітний опір осердя R_m (центральний стовп)
    frags.append(rect(200, 160, 35, 45, fill="#d1fae5", stroke=FIELD, sw=1.5, rx=2))
    frags.append(text(217, 187, "ℛ_core\n(L_m)", size=10, color=FIELD, bold=True))
    frags.append(line(87, 140, 347, 140, color=LINE, sw=1.5))
    frags.append(line(87, 240, 347, 240, color=LINE, sw=1.5))
    frags.append(line(217, 140, 217, 160, color=LINE, sw=1.5))
    frags.append(line(217, 205, 217, 240, color=LINE, sw=1.5))

    # Магнітний опір розсіювання R_lk2
    frags.append(rect(270, 160, 40, 22, fill="#fef3c7", stroke=LEAKCOL, sw=1.5, rx=2))
    frags.append(text(290, 175, "ℛ_lk2", size=10, color=LEAKCOL, bold=True))

    # Джерело МРС 2
    frags.append(rect(330, 160, 35, 25, fill="#dbeafe", stroke=COPPER2, sw=1.5, rx=3))
    frags.append(text(347, 177, "N₂·i₂", size=10.5, color=COPPER2, bold=True))
    frags.append(line(347, 140, 347, 160, color=LINE, sw=1.5))
    frags.append(line(347, 185, 347, 240, color=LINE, sw=1.5))

    frags.append(mtext(217, 280, [
        "Магніторушійна сила: F = N · i",
        "Магнітний потік: Φ = F / ℛ",
        "• Повітряний зазор у центральному керні задає L_m",
        "• Шунти витоку задають незалежний L_leak"
    ], size=10.5, color=INK, lh=1.35))

    # Права панель: Електрична Т-схема
    frags.append(rect(420, 90, 385, 300, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(text(612, 115, "Електрична Т-подібна модель", size=12.5, color=INK, bold=True))

    # Вхід 1
    frags.append(text(440, 160, "Вхід 1", size=10.5, color=COPPER1, bold=True))
    frags.append(line(460, 160, 490, 160, color=LINE, sw=1.5))
    # L_lk1
    frags.append(rect(490, 150, 45, 20, fill="#fef3c7", stroke=LEAKCOL, sw=1.5, rx=2))
    frags.append(text(512, 164, "L_lk1", size=10, color=LEAKCOL, bold=True))
    frags.append(line(535, 160, 612, 160, color=LINE, sw=1.5))

    # L_m
    frags.append(circle(612, 160, 3, fill=INK, stroke=INK))
    frags.append(line(612, 160, 612, 190, color=LINE, sw=1.5))
    frags.append(rect(595, 190, 35, 35, fill="#d1fae5", stroke=FIELD, sw=1.5, rx=2))
    frags.append(text(612, 212, "L_m", size=11, color=FIELD, bold=True))
    frags.append(line(612, 225, 612, 250, color=LINE, sw=1.5))
    frags.append(line(460, 250, 765, 250, color=LINE, sw=1.5))

    # L_lk2
    frags.append(line(612, 160, 690, 160, color=LINE, sw=1.5))
    frags.append(rect(690, 150, 45, 20, fill="#dbeafe", stroke=LEAKCOL, sw=1.5, rx=2))
    frags.append(text(712, 164, "L_lk2", size=10, color=LEAKCOL, bold=True))
    frags.append(line(735, 160, 765, 160, color=LINE, sw=1.5))
    frags.append(text(785, 160, "Вхід 2", size=10.5, color=COPPER2, bold=True))

    frags.append(mtext(612, 280, [
        "Зв'язок параметрів Т-моделі:",
        "• Взаємна індуктивність: M = L_m",
        "• Повна індуктивність 1: L₁ = L_lk1 + L_m",
        "• Повна індуктивність 2: L₂ = L_lk2 + L_m",
        "• Коефіцієнт зв'язку: k = L_m / √(L₁ · L₂)"
    ], size=10.5, color=INK, lh=1.35))

    return render(os.path.join(IMG, "core-reluctance-model.svg"), W, H, *frags)


def main():
    fig_core_coupling()
    fig_interleaved_buck_coupling()
    fig_transient_vs_ripple()
    fig_coupled_topologies()
    fig_zvs_leakage()
    fig_core_reluctance_model()
    print("Усі 6 фігур згенеровано успішно.")


if __name__ == "__main__":
    main()
