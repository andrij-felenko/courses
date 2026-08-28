# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Не знаю»: відмова від рішення як штатна відповідь."""

import sys
import os

# Підключаємо спільний svgkit із scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_feature_space():
    """Фігура 1: Простір ознак з кластерами ID, алеаторною зоною та зоною OOD-відмови."""
    w, h = 920, 540
    frags = []

    # Фон координатної сітки
    frags.append(rect(40, 50, 840, 460, fill="#fcfdfe", stroke="#d0d7de", sw=1.2, rx=8))



    # Осі координат простору латентних ембеддінгів
    frags.append(arrow(60, 480, 860, 480, color=LINE, sw=1.6))
    frags.append(text(850, 470, "z₁", size=13, color=LINE, bold=True))
    frags.append(arrow(60, 480, 60, 70, color=LINE, sw=1.6))
    frags.append(text(75, 75, "z₂", size=13, color=LINE, bold=True))

    # Заголовок графіка простору ембеддінгів
    frags.append(text(270, 75, "Латентний простір ознак (ембеддінгів передостаннього шару)", size=12, color=MUTED, bold=True))

    # Кластер Клас 1 (наприклад, «Знак СТОП»)
    frags.append('<ellipse cx="190" cy="240" rx="80" ry="60" fill="#eafaf1" stroke="#27ae60" stroke-width="1.6" stroke-dasharray="4,3"/>')
    frags.append('<ellipse cx="190" cy="240" rx="50" ry="38" fill="#d4efdf" stroke="#27ae60" stroke-width="1.2"/>')
    frags.append(circle(190, 240, 5, fill="#1e8449", stroke="#145a32", sw=1.5))
    frags.append(text(190, 226, "μ₁ (Клас A)", size=11, color="#145a32", bold=True))
    for pt in [(175, 230), (205, 248), (165, 252), (195, 220), (215, 235), (180, 255)]:
        frags.append(circle(pt[0], pt[1], 3, fill="#27ae60", stroke="none"))

    # Кластер Клас 2 (наприклад, «Знак Поступіться»)
    frags.append('<ellipse cx="370" cy="240" rx="80" ry="60" fill="#ebf5fb" stroke="#2980b9" stroke-width="1.6" stroke-dasharray="4,3"/>')
    frags.append('<ellipse cx="370" cy="240" rx="50" ry="38" fill="#d6eaf8" stroke="#2980b9" stroke-width="1.2"/>')
    frags.append(circle(370, 240, 5, fill="#2471a3", stroke="#1b4f72", sw=1.5))
    frags.append(text(370, 226, "μ₂ (Клас B)", size=11, color="#1b4f72", bold=True))
    for pt in [(355, 230), (385, 248), (360, 255), (375, 220), (395, 235)]:
        frags.append(circle(pt[0], pt[1], 3, fill="#2980b9", stroke="none"))

    # Кластер Клас 3 (наприклад, «Обмеження швидкості»)
    frags.append('<ellipse cx="280" cy="400" rx="75" ry="50" fill="#fef9e7" stroke="#f39c12" stroke-width="1.6" stroke-dasharray="4,3"/>')
    frags.append('<ellipse cx="280" cy="400" rx="45" ry="30" fill="#fdebd0" stroke="#f39c12" stroke-width="1.2"/>')
    frags.append(circle(280, 400, 5, fill="#d68910", stroke="#9a7d0a", sw=1.5))
    frags.append(text(280, 390, "μ₃ (Клас C)", size=11, color="#9a7d0a", bold=True))
    for pt in [(265, 395), (295, 410), (275, 415), (285, 385)]:
        frags.append(circle(pt[0], pt[1], 3, fill="#f39c12", stroke="none"))

    # Межа рішень між класами A і B
    frags.append(line(280, 185, 280, 335, color="#e74c3c", sw=1.8, dash="4,3"))
    
    # Зона високої алеаторної невизначеності (розміщена вгорі без перетину з еліпсами)
    b_al = fitbox(180, 95, 200, 75, "Алеаторна невизначеність\n(шум / завади / межа)\nH(p) > τ_H; p₁≈0.5, p₂≈0.5\nЗондування або відмова", size=9.5, fill="#fdedec", stroke="#e74c3c", sw=1.2)
    frags.append(b_al)
    frags.append(arrow(280, 170, 280, 184, color="#e74c3c", sw=1.5))

    # Велика зона OOD / Епістемічної невизначеності (праворуч)
    frags.append(rect(530, 80, 330, 400, fill="#f5eef8", stroke="#8e44ad", sw=1.5, rx=8))
    frags.append(text(695, 110, "Зона OOD / Епістемічної відмови", size=13, color="#6c3483", bold=True))
    frags.append(text(695, 130, "(Об'єкти поза навчальним розподілом даних)", size=10, color="#7d3c98", italic=True))

    # Контури вільної енергії та відстані Махаланобіса
    frags.append('<ellipse cx="695" cy="260" rx="100" ry="75" fill="none" stroke="#a569bd" stroke-width="1.2" stroke-dasharray="4,3"/>')
    frags.append('<ellipse cx="695" cy="260" rx="60" ry="45" fill="none" stroke="#8e44ad" stroke-width="1.5"/>')
    frags.append(circle(695, 260, 6, fill="#7d3c98", stroke="#4a235a", sw=1.8))
    frags.append(text(695, 245, "x_незнайомий (OOD)", size=11, color="#4a235a", bold=True))

    # Текстовий блок із формулами критеріїв OOD
    b_crit = fitbox(550, 350, 290, 110, "Критерії детекції OOD:\n1. Вільна енергія: E(x; T) = −T·ln ∑ e^{f_i/T} > τ_E\n2. Махаланобіс: D_M(z) = √((z−μ)^T Σ⁻¹ (z−μ)) > τ_M\n3. Чому не Softmax: далекі точки можуть мати\nвисокі логіти й хибно максимальну впевненість!", size=9.5, fill="#ffffff", stroke="#8e44ad", sw=1)
    frags.append(b_crit)

    # Стрілка-порівняння
    frags.append(arrow(455, 260, 525, 260, color="#8e44ad", sw=1.8))
    frags.append(text(490, 250, "D_M ≫ τ", size=10, color="#8e44ad", bold=True))

    return render(os.path.join(OUT_DIR, "feature-space-ood-rejection.svg"), w, h, *frags)


def fig_refusal_fsm():
    """Фігура 2: Кінцевий автомат обробки невизначеності та каскад захисних дій."""
    w, h = 920, 560
    frags = []

    # Заголовок діаграми
    frags.append(text(460, 28, "Архітектура каскадного фільтра невизначеності та обробки відмови", size=15, color=INK, bold=True))

    # Стан 1: Вхідний сенсорний кадр
    b1 = fitbox(40, 70, 160, 65, "1. Сенсорний вхід\nКадр камери / лідара\nx ∈ ℝ^D", size=10.5, fill="#eaf2f8", stroke="#2980b9", bold=True)
    frags.append(b1)

    # Стан 2: Нейромережевий вивід
    b2 = fitbox(250, 70, 180, 65, "2. Нейромережа\nЛогіти f(x) та\nембеддінги z", size=10.5, fill="#ebf5fb", stroke="#2471a3", bold=True)
    frags.append(b2)
    frags.append(arrow(200, 102, 248, 102, color=LINE, sw=1.6))

    # Стан 3: Енергетичний OOD-фільтр (Каскад 1)
    b3 = fitbox(480, 60, 190, 85, "3. Енергетичний тест\nE(x; T) = −T·ln ∑ e^{f_i/T}\nE(x) ≤ τ_E  (ID-дані?)", size=10.5, fill="#fefde8", stroke="#d4ac0d", bold=True)
    frags.append(b3)
    frags.append(arrow(430, 102, 478, 102, color=LINE, sw=1.6))

    # Стан 4: Ентропійний тест невизначеності (Каскад 2)
    b4 = fitbox(710, 60, 180, 85, "4. Ентропійний тест\nH(p) = −∑ p_i ln p_i\nH(p) ≤ τ_H (Впевнено?)", size=10.5, fill="#fef9e7", stroke="#f39c12", bold=True)
    frags.append(b4)
    frags.append(arrow(670, 102, 708, 102, color=FIELD, sw=1.8))
    frags.append(text(689, 92, "Так", size=10, color=FIELD, bold=True))

    # Стан 5: Довірена дія (Успіх)
    b5 = fitbox(710, 200, 180, 70, "5. Довірена відповідь\nŷ = argmax p_i\nШтатне керування", size=10.5, fill="#eafaf1", stroke="#27ae60", bold=True)
    frags.append(b5)
    frags.append(arrow(800, 145, 800, 198, color=FIELD, sw=1.8))
    frags.append(text(815, 172, "Так", size=10, color=FIELD, bold=True))

    # Розгалуження відмов (Ні від OOD або Ні від Ентропії)
    # Шина відмови
    frags.append(arrow(575, 145, 575, 230, color=POS, sw=1.8))
    frags.append(text(595, 175, "Ні (OOD)", size=10, color=POS, bold=True))

    frags.append(arrow(710, 120, 640, 230, color=POS, sw=1.8))
    frags.append(text(690, 160, "Ні (Шум)", size=10, color=POS, bold=True))

    # Вузол ухвалення захисної стратегії
    b_refuse = fitbox(440, 230, 230, 75, "Штатна відмова («Не знаю»)\nКласифікатор блокує прямий вивід\nВибір захисного протоколу", size=10.5, fill="#fdedec", stroke=POS, bold=True)
    frags.append(b_refuse)

    # Три гілки обробки відмови
    # Гілка 1: Активне сенсорне доопитування (Active Sensing)
    b_act = fitbox(50, 360, 240, 95, "Стратегія 1: Активне зондування\n• Запит додаткового кадру\n• Зміна експозиції / підсвітка\n• Поворот PTZ-камери / фокусу\n• Зменшення алеаторного шуму", size=9.5, fill="#f4f6f7", stroke="#566573")
    frags.append(b_act)
    frags.append(arrow(470, 305, 170, 358, color=LINE, sw=1.6))
    # Зворотний зв'язок на сенсор
    frags.append(arrow(120, 360, 120, 137, color="#2980b9", sw=1.5))
    frags.append(text(145, 240, "Новий вимір", size=10, color="#2980b9", italic=True))

    # Гілка 2: Детерміновані консервативні правила безпеки
    b_det = fitbox(340, 360, 250, 95, "Стратегія 2: Консервативні правила\n• Перехід у безпечний режим (Limp mode)\n• Зниження швидкості / зупинка\n• Детермінований safety envelope\n• Гарантія безаварійності", size=9.5, fill="#fbfcfc", stroke="#34495e")
    frags.append(b_det)
    frags.append(arrow(555, 305, 465, 358, color=LINE, sw=1.6))

    # Гілка 3: Передача керування людині (Takeover Request)
    b_tor = fitbox(640, 360, 240, 95, "Стратегія 3: Запит на перехоплення\n• Takeover Request (TOR) оператору\n• Звукова / тактильна сигналізація\n• Очікування підтвердження (1.5-3 с)\n• Буфер безпечної траєкторії", size=9.5, fill="#fdfefe", stroke="#7f8c8d")
    frags.append(b_tor)
    frags.append(arrow(630, 305, 760, 358, color=LINE, sw=1.6))

    # Кінцевий аварійний стан (якщо оператор не відповів)
    b_stop = fitbox(490, 485, 260, 55, "Мінімальний стан ризику (MRM)\nАвтономне безпечне гальмування до повної зупинки", size=10, fill="#eaecee", stroke="#2c3e50", bold=True)
    frags.append(b_stop)
    frags.append(arrow(760, 455, 680, 483, color=POS, sw=1.5))
    frags.append(text(750, 472, "Таймаут TOR", size=9, color=POS))
    frags.append(arrow(465, 455, 560, 483, color="#34495e", sw=1.5))

    return render(os.path.join(OUT_DIR, "refusal-state-machine.svg"), w, h, *frags)


if __name__ == "__main__":
    f1 = fig_feature_space()
    print("Згенеровано:", f1)
    f2 = fig_refusal_fsm()
    print("Згенеровано:", f2)
