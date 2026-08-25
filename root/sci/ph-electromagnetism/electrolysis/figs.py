# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Електроліз»."""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def fig_electrolytic_cell(path):
    w, h = 720, 460
    frags = []

    # Джерело постійного струму вгорі
    frags.append(rect(280, 20, 160, 50, fill="#f8fafc", stroke=LINE, sw=2, rx=8))
    frags.append(mtext(360, 40, ["Джерело ДС", "U > E⁰cell"], size=13, bold=True))

    # Провідники від джерела до електродів
    frags.append(line(280, 45, 120, 45, color=NEG, sw=2.5))
    frags.append(line(120, 45, 120, 120, color=NEG, sw=2.5))
    frags.append(line(440, 45, 600, 45, color=POS, sw=2.5))
    frags.append(line(600, 45, 600, 120, color=POS, sw=2.5))

    # Стрілки руху електронів у зовнішньому колі
    frags.append(arrow(260, 35, 180, 35, color=NEG, sw=2))
    frags.append(text(220, 25, "e⁻ (до катода)", size=12, color=NEG, bold=True))

    frags.append(arrow(600, 80, 600, 55, color=POS, sw=2))
    frags.append(text(620, 75, "e⁻ (від анода)", size=12, color=POS, bold=True, anchor="start"))

    # Ванна з електролітом (використовуємо контур із заливкою без окремих суцільних перекривань)
    frags.append('<rect x="80" y="150" width="560" height="260" rx="12" fill="#eef6fc" stroke="#78a9c6" stroke-width="2"/>')
    frags.append(text(360, 175, "Розчин / розплав електроліту", size=14, color="#2c5282", bold=True))

    # Електрод Катод (ліворуч, від'ємний) - малюємо лініями/штриховкою щоб уникнути конфлікту блоків
    frags.append(line(120, 120, 120, 380, color="#475569", sw=18))
    frags.append(minus(120, 140, r=11))
    frags.append(text(120, 400, "КАТОД (−)", size=14, color=NEG, bold=True))
    frags.append(text(120, 420, "Відновлення", size=12, color=MUTED, italic=True))

    # Електрод Анод (праворуч, додатний)
    frags.append(line(600, 120, 600, 380, color="#c2410c", sw=18))
    frags.append(plus(600, 140, r=11))
    frags.append(text(600, 400, "АНОД (+)", size=14, color=POS, bold=True))
    frags.append(text(600, 420, "Окиснення", size=12, color=MUTED, italic=True))

    # Рух катіона до катода
    frags.append(plus(260, 240, r=12))
    frags.append(text(260, 243, "Mᶻ⁺", size=11, color=POS, bold=True))
    frags.append(arrow(260, 240, 160, 240, color=NEG, sw=2))
    frags.append(text(210, 225, "Катіони пливуть до катода", size=12, color=NEG))

    # Реакція на катоді
    b1, _, _ = textbox(240, 310, "Реакція на катоді:\nMᶻ⁺ + z·e⁻ → M⁰\n(осадження / виділення H₂)", size=12, pad=8, fill="#ffffff", stroke=NEG, sw=1.5)
    frags.append(b1)

    # Рух аніона до анода
    frags.append(minus(460, 240, r=12))
    frags.append(text(460, 243, "Xᶻ⁻", size=11, color=NEG, bold=True))
    frags.append(arrow(460, 240, 560, 240, color=POS, sw=2))
    frags.append(text(510, 225, "Аніони пливуть до анода", size=12, color=POS))

    # Реакція на аноді
    b2, _, _ = textbox(480, 310, "Реакція на аноді:\nXᶻ⁻ → X⁰ + z·e⁻\n(розчинення / виділення Cl₂, O₂)", size=12, pad=8, fill="#ffffff", stroke=POS, sw=1.5)
    frags.append(b2)

    return render(path, w, h, *frags)

def fig_overpotential_voltage(path):
    w, h = 680, 400
    frags = []

    frags.append(text(340, 25, "Структура прикладеної напруги в електролізері", size=16, bold=True))

    # Ліва вісь напруги
    frags.append(line(80, 340, 80, 60, color=LINE, sw=2))
    frags.append(arrow(80, 70, 80, 50, color=LINE, sw=2))
    frags.append(text(65, 55, "Напруга (В)", size=12, bold=True, anchor="end"))

    # Стовпчик компонентів напруги (x=160..360)
    frags.append(rect(160, 220, 200, 120, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=0))
    frags.append(mtext(260, 275, ["Рівноважна напруга E⁰cell", "ΔG / (z·F)"], size=13, color="#1e40af", bold=True))

    frags.append(rect(160, 170, 200, 50, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=0))
    frags.append(mtext(260, 192, ["Катодна перенапруга ηc", "(кінетика відновлення)"], size=11, color="#92400e", bold=True))

    frags.append(rect(160, 110, 200, 60, fill="#ffedd5", stroke="#ea580c", sw=1.5, rx=0))
    frags.append(mtext(260, 137, ["Анодна перенапруга ηa", "(активація окиснення + масоперенос)"], size=11, color="#9a3412", bold=True))

    frags.append(rect(160, 70, 200, 40, fill="#fecdd3", stroke="#e11d48", sw=1.5, rx=0))
    frags.append(mtext(260, 87, ["Омічне падіння I·Rcell", "(опір електроліту й мембрани)"], size=11, color="#9f1239", bold=True))

    # Права підсумкова дужка / стрілка для V_applied
    frags.append(line(380, 70, 410, 70, color=INK, sw=1.5))
    frags.append(line(380, 340, 410, 340, color=INK, sw=1.5))
    frags.append(line(410, 70, 410, 340, color=INK, sw=2))

    b_sum, _, _ = textbox(530, 205, "Повна напруга:\nVприклад = E⁰cell + ηa + ηc + I·Rcell\n\nЗавжди Vприклад > E⁰cell\nНадлишок іде в тепло!", size=13, pad=10, fill="#f8fafc", stroke=LINE, sw=1.5)
    frags.append(b_sum)

    # Пунктирні лінії від осі Y
    frags.append(line(80, 340, 160, 340, color=MUTED, sw=1, dash="4,4"))
    frags.append(line(80, 220, 160, 220, color=MUTED, sw=1, dash="4,4"))
    frags.append(line(80, 70, 160, 70, color=MUTED, sw=1, dash="4,4"))

    frags.append(text(70, 345, "0 В", size=11, color=MUTED, anchor="end"))
    frags.append(text(70, 225, "E⁰cell", size=11, color=MUTED, anchor="end"))
    frags.append(text(70, 75, "Vприклад", size=11, color=MUTED, anchor="end"))

    return render(path, w, h, *frags)

def fig_water_electrolysis(path):
    w, h = 720, 440
    frags = []

    frags.append(text(360, 25, "Механізм електролізу води (розклад на H₂ та O₂)", size=16, bold=True))

    # Джерело струму
    frags.append(rect(300, 45, 120, 40, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(360, 68, "Джерело ДС", size=12, bold=True))

    frags.append(line(300, 65, 140, 65, color=NEG, sw=2))
    frags.append(line(140, 65, 140, 130, color=NEG, sw=2))

    frags.append(line(420, 65, 580, 65, color=POS, sw=2))
    frags.append(line(580, 65, 580, 130, color=POS, sw=2))

    # Корпус комірки
    frags.append('<rect x="60" y="130" width="600" height="270" rx="10" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2"/>')

    # Пориста мембрана посередині
    frags.append(line(360, 130, 360, 400, color="#94a3b8", sw=3, dash="6,4"))
    frags.append(text(360, 390, "Мембрана / Діафрагма", size=11, color="#475569", bold=True))

    # Катод (ліворуч)
    frags.append(line(140, 130, 140, 370, color="#475569", sw=18))
    frags.append(text(140, 115, "КАТОД (−)", size=13, color=NEG, bold=True))

    # Анод (праворуч)
    frags.append(line(580, 130, 580, 370, color="#c2410c", sw=18))
    frags.append(text(580, 115, "АНОД (+)", size=13, color=POS, bold=True))

    # Бульбашки H2 біля катода
    frags.append(circle(200, 200, 14, fill="#bae6fd", stroke=NEG, sw=1.5))
    frags.append(text(200, 204, "H₂", size=12, color=NEG, bold=True))
    frags.append(circle(230, 170, 10, fill="#bae6fd", stroke=NEG, sw=1.5))
    frags.append(text(230, 173, "H₂", size=9, color=NEG, bold=True))
    frags.append(circle(180, 250, 16, fill="#bae6fd", stroke=NEG, sw=1.5))
    frags.append(text(180, 254, "H₂", size=13, color=NEG, bold=True))

    # Реакція катода
    bk, _, _ = textbox(230, 320, "Відновлення:\n4H⁺ + 4e⁻ → 2H₂ ↑\n(об'єм 2V)", size=12, pad=8, fill="#ffffff", stroke=NEG, sw=1.5)
    frags.append(bk)

    # Бульбашки O2 біля анода
    frags.append(circle(500, 210, 14, fill="#ffedd5", stroke=POS, sw=1.5))
    frags.append(text(500, 214, "O₂", size=12, color=POS, bold=True))
    frags.append(circle(470, 260, 12, fill="#ffedd5", stroke=POS, sw=1.5))
    frags.append(text(470, 263, "O₂", size=10, color=POS, bold=True))

    # Реакція анода
    ba, _, _ = textbox(490, 320, "Окиснення:\n2H₂O → O₂ ↑ + 4H⁺ + 4e⁻\n(об'єм 1V)", size=12, pad=8, fill="#ffffff", stroke=POS, sw=1.5)
    frags.append(ba)

    # Об'ємне співвідношення - виносимо нижче або використовуємо textbox
    bspec, _, _ = textbox(360, 420, "Об'ємне співвідношення H₂ : O₂ = 2 : 1", size=13, pad=6, fill="#ffffff", stroke="#0284c7", sw=1.5)
    frags.append(bspec)

    return render(path, w, h, *frags)

def fig_industrial_applications(path):
    w, h = 760, 380
    frags = []

    frags.append(text(380, 25, "Три стовпи промислового електролізу", size=16, bold=True))

    # Панель 1: Процес Голла-Еру (Алюміній)
    p1 = rect(30, 60, 220, 290, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8)
    frags.append(p1)
    frags.append(text(140, 85, "Отримання Al", size=14, color="#1e293b", bold=True))
    frags.append(text(140, 105, "Процес Голла-Еру", size=11, color=MUTED, italic=True))
    frags.append(rect(50, 125, 180, 100, fill="#e2e8f0", stroke="#475569", sw=1, rx=4))
    frags.append(mtext(140, 155, ["Розплав Al₂O₃", "у кріоліті Na₃AlF₆", "T ≈ 950°C"], size=11, color="#334155"))
    frags.append(rect(60, 190, 160, 25, fill="#94a3b8", stroke="#334155", sw=1, rx=2))
    frags.append(text(140, 207, "Рідкий Al (катод)", size=11, color="#ffffff", bold=True))
    frags.append(mtext(140, 255, ["Анод: вугільні блоки", "C + 2O²⁻ → CO₂ + 4e⁻", "", "Катод: Al³⁺ + 3e⁻ → Al"], size=11, color="#0f172a"))

    # Панель 2: Хлорно-лужний процес
    p2 = rect(270, 60, 220, 290, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8)
    frags.append(p2)
    frags.append(text(380, 85, "Хлор та Луг", size=14, color="#15803d", bold=True))
    frags.append(text(380, 105, "Мембранний процес", size=11, color=MUTED, italic=True))
    frags.append(rect(290, 125, 180, 100, fill="#dcfce7", stroke="#22c55e", sw=1, rx=4))
    frags.append(mtext(380, 155, ["Розчин NaCl (ропа)", "Катіонообмінна", "мембрана Na⁺"], size=11, color="#166534"))
    frags.append(mtext(380, 255, ["Анод: 2Cl⁻ → Cl₂ ↑ + 2e⁻", "", "Катод: 2H₂O + 2e⁻ →", "→ H₂ ↑ + 2OH⁻", "", "Продукт: NaOH + Cl₂ + H₂"], size=11, color="#14532d"))

    # Панель 3: Електрорафінування / Гальваніка
    p3 = rect(510, 60, 220, 290, fill="#fff7ed", stroke="#ea580c", sw=1.5, rx=8)
    frags.append(p3)
    frags.append(text(620, 85, "Рафінування міді", size=14, color="#c2410c", bold=True))
    frags.append(text(620, 105, "Гальваніка / Очищення", size=11, color=MUTED, italic=True))
    frags.append(rect(530, 125, 180, 100, fill="#ffedd5", stroke="#f97316", sw=1, rx=4))
    frags.append(mtext(620, 155, ["Розчин CuSO₄", "Чорнова Cu (анод)", "Чиста Cu (катод)"], size=11, color="#9a3412"))
    frags.append(mtext(620, 255, ["Анод (чорнова мідь):", "Cu⁰ → Cu²⁺ + 2e⁻", "", "Катод (чиста мідь):", "Cu²⁺ + 2e⁻ → Cu⁰ (99.99%)"], size=11, color="#7c2d12"))

    return render(path, w, h, *frags)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    figures = {
        'electrolytic-cell.svg': fig_electrolytic_cell,
        'overpotential-voltage.svg': fig_overpotential_voltage,
        'water-electrolysis.svg': fig_water_electrolysis,
        'industrial-applications.svg': fig_industrial_applications,
    }

    for name, func in figures.items():
        path = os.path.join(img_dir, name)
        func(path)
        print(f"Generated {name}")

if __name__ == '__main__':
    main()

