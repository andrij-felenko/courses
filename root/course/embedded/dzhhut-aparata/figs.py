# -*- coding: utf-8 -*-
"""Фігури до теми «Джгут апарата: від пакета до вузлів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED = POS     # #c0392b
BLU = NEG     # #2457d6
GRN = FIELD   # #27ae60

def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))

# ── 1. Падіння напруги та перекіс потенціалів землі (Ground Shift) ───────────
def fig_ground_shift():
    W, H = 840, 440
    f = []

    # Головна плата / Джерело (лівий блок)
    b_main, _, _ = textbox(130, 200, "ГОЛОВНА ПЛАТА / MCU\nДжерело живлення 3.3 В\nV_GND = 0.00 В\nВхід Rx (V_IL < 0.8 В)",
                           size=13, pad=12, fill="#f8fafc", stroke=LINE, sw=1.8, bold=True)
    f.append(b_main)

    # Периферійна плата / Давач (правий блок)
    b_node, _, _ = textbox(710, 200, "ВІДДАЛЕНИЙ ВУЗОЛ\nМотор / Давач / MCU\nV_GND_local = +0.55 В\nВихід Tx (V_OL = 0.2 В)",
                           size=13, pad=12, fill="#f8fafc", stroke=LINE, sw=1.8, bold=True)
    f.append(b_node)

    # Провід живлення +3.3V (верхня лінія)
    y_pwr = 100
    f.append(line(230, y_pwr, 600, y_pwr, color=RED, sw=2.5))
    f.append(arrow(380, y_pwr, 450, y_pwr, color=RED, sw=2.5))
    f.append(text(415, y_pwr - 14, "+3.3 В шина (струм навантаження I_load = 2.0 А)", size=12, color=RED, bold=True))
    f.append(text(415, y_pwr + 16, "Падіння на плюсовому проводі: ΔV_pos = I · R_pos = 0.55 В", size=11, color=MUTED))

    # Сигнальний провід UART / GPIO (середня лінія)
    y_sig = 200
    f.append(line(600, y_sig, 230, y_sig, color=GRN, sw=2.0, dash="5 3"))
    f.append(arrow(450, y_sig, 380, y_sig, color=GRN, sw=2.0))
    f.append(text(415, y_sig - 12, "Сигнальна лінія (UART Tx → Rx, слабкострумова)", size=12, color=GRN, bold=True))

    # Земляний провід GND (нижня лінія)
    y_gnd = 300
    f.append(line(600, y_gnd, 230, y_gnd, color=BLU, sw=2.5))
    f.append(arrow(450, y_gnd, 380, y_gnd, color=BLU, sw=2.5))
    f.append(text(415, y_gnd - 14, "Спільна земля GND (зворотний струм I_load = 2.0 А)", size=12, color=BLU, bold=True))
    f.append(text(415, y_gnd + 16, "Падіння на земляному проводі: ΔV_gnd = I · R_gnd = 0.55 В", size=11, color=MUTED))

    # Резистор R_gnd на земляному проводі (ілюстрація паразитного опору)
    f.append(rect(390, y_gnd - 8, 50, 16, fill="#e2e8f0", stroke=BLU, sw=1.5, rx=2))
    f.append(text(415, y_gnd + 34, "R_gnd = 0.275 Ом", size=11, color=BLU, bold=True))

    # Підсумковий блок конфлікту логічних рівнів
    bx_warn, _, _ = textbox(420, 390,
                            "КРИТИЧНИЙ ЗБІЙ: Сигнал нуля Tx віддаленого вузла приходить на головний MCU з рівнем:\n"
                            "V_in = V_OL + V_GND_local = 0.20 В + 0.55 В = 0.75 В (майже на межі порога V_IL = 0.8 В)!\n"
                            "Будь-яка додаткова завада сприймається мікроконтролером як хибна одиниця.",
                            size=12, pad=10, fill="#fef2f2", stroke=RED, sw=1.5, color="#991b1b")
    f.append(bx_warn)

    return render(os.path.join(IMG, "ground-shift-diagram.svg"), W, H, *f,
                  title="Падіння напруги на джгуті та перекіс потенціалів землі (Ground Shift)")

# ── 2. Вита пара, петлі магнітного поля та екранування ───────────────────────
def fig_twisted_pair_shielding():
    W, H = 840, 420
    f = []

    # Верхня частина: Паралельні дроти проти витої пари
    f.append(text(420, 24, "ВПЛИВ ГЕОМЕТРІЇ ПРОВІДНИКІВ НА МАГНІТНЕ НАВЕДЕННЯ", size=14, color=INK, bold=True))

    # (A) Прямі паралельні проводи — велика петля
    f.append(text(210, 60, "Паралельні проводи (велика площа петлі S)", size=12, color=RED, bold=True))
    f.append(line(50, 85, 370, 85, color=RED, sw=2.5))
    f.append(line(50, 135, 370, 135, color=BLU, sw=2.5))
    # Магнітне поле крізь петлю
    f.append(rect(50, 85, 320, 50, fill="#fee2e2", stroke="none", rx=0))
    f.append(text(210, 110, "Зовнішнє магнітне поле B(t) → Наведена ЕРС e = -dΦ/dt", size=11, color=RED))
    f.append(text(210, 155, "Кожна петля підсумовує наведену заваду в один фатальний сплеск", size=11, color=MUTED))

    # (B) Вита пара — взаємна компенсація сусідніх петель
    f.append(text(630, 60, "Вита пара (Twisted Pair — чергування фаз)", size=12, color=GRN, bold=True))
    # Малюємо синусоїдальні перехрестя
    pts_a = []
    pts_b = []
    x_start = 470
    for i in range(160):
        t = i / 159.0
        x = x_start + t * 320
        y_mid = 110
        amp = 20 * math.sin(t * 8 * math.pi)
        pts_a.append((x, y_mid + amp))
        pts_b.append((x, y_mid - amp))
    f.append(polyline(pts_a, color=RED, sw=2.2))
    f.append(polyline(pts_b, color=BLU, sw=2.2))

    f.append(text(510, 110, "+e₁", size=11, color=GRN, bold=True))
    f.append(text(550, 110, "−e₂", size=11, color=GRN, bold=True))
    f.append(text(590, 110, "+e₃", size=11, color=GRN, bold=True))
    f.append(text(630, 110, "−e₄", size=11, color=GRN, bold=True))
    f.append(text(630, 155, "Сусідні напіввитки мають протилежний знак: ∑ e_ind ≈ 0", size=11, color=GRN, bold=True))

    # Розділювальна лінія
    f.append(line(50, 185, 790, 185, color="#cbd5e1", sw=1.5, dash="4 4"))

    # Нижня частина: Правила заземлення екрана
    f.append(text(420, 215, "ПРАВИЛА ЗАЗЕМЛЕННЯ ЕКРАНА ДЖГУТА", size=14, color=INK, bold=True))

    # Одностороннє заземлення (НЧ)
    bx_lf, _, _ = textbox(220, 310,
                          "Низькі частоти та аналогові сигнали (DC…100 кГц)\n\n"
                          "• Заземлення екрана ТІЛЬКИ З ОДНОГО БОКУ\n"
                          "• Розриває земляну петлю струмів 50 Гц / вирівнювання\n"
                          "• Другий кінець ізолюється термозбіжкою\n"
                          "• Захищає від паразитної ємнісної наводки E-поля",
                          size=11.5, pad=10, fill="#f0fdf4", stroke=GRN, sw=1.5)
    f.append(bx_lf)

    # Двостороннє 360° заземлення (ВЧ)
    bx_hf, _, _ = textbox(620, 310,
                          "Високі частоти, CAN, Ethernet, RF (понад 1 МГц)\n\n"
                          "• Заземлення екрана З ОБОХ БОКІВ на металеве шасі\n"
                          "• Суцільний 360° контакт роз'єму (без свинячих хвостів)\n"
                          "• Забезпечує шлях повернення ВЧ струмів зміщення\n"
                          "• Пастка Pigtail (хвіст 5 см) = антена на 50 МГц!",
                          size=11.5, pad=10, fill="#eff6ff", stroke=BLU, sw=1.5)
    f.append(bx_hf)

    return render(os.path.join(IMG, "twisted-pair-and-shielding.svg"), W, H, *f,
                  title="Геометрія витої пари та стратегії заземлення екрана")

# ── 3. Анатомія надійного обтиску та розвантаження джгута ───────────────────
def fig_crimp_and_strain():
    W, H = 840, 420
    f = []

    f.append(text(420, 24, "АНАТОМІЯ ОБТИСКУ (CRIMP) ТА РОЗВАНТАЖЕННЯ ВІД НАТЯГУ", size=14, color=INK, bold=True))

    # Ліва частина: B-Crimp обтиск
    f.append(text(210, 60, "Правильний двозонний B-обтиск клеми", size=12, color=GRN, bold=True))

    # Контур дроту з ізоляцією
    f.append(rect(50, 100, 110, 50, fill="#cbd5e1", stroke=LINE, sw=1.8, rx=4))
    f.append(text(105, 128, "Ізоляція дроту", size=11, color=INK, bold=True))

    # Оголені мідні жилки
    f.append(rect(160, 110, 90, 30, fill="#fdba74", stroke="#ea580c", sw=1.5, rx=2))
    f.append(text(205, 128, "Мідні жили", size=11, color="#9a3412", bold=True))

    # Зона обтиску ізоляції
    f.append(rect(130, 85, 45, 80, fill="none", stroke=BLU, sw=2.5, rx=4))
    f.append(text(152, 190, "Обтиск ізоляції\n(механічна опора)", size=11, color=BLU, bold=True))

    # Зона обтиску міді (газощільний B-crimp)
    f.append(rect(215, 95, 50, 60, fill="none", stroke=GRN, sw=2.5, rx=4))
    f.append(text(240, 190, "Обтиск міді (B-Crimp)\n(газощільний контакт)", size=11, color=GRN, bold=True))

    # Наконечник контакту
    f.append(rect(290, 112, 80, 26, fill="#94a3b8", stroke=LINE, sw=1.8, rx=2))
    f.append(text(330, 128, "Контакт", size=11, color=INK, bold=True))

    # Чому пайка небезпечна
    bx_solder, _, _ = textbox(210, 310,
                              "ПАСТКА ПАЯННЯ ПРОВОДІВ У РОЗ'ЄМ:\n\n"
                              "Припій затікає під ізоляцію (капілярний ефект).\n"
                              "Гнучкий багатожильний дріт стає крихким монолітом.\n"
                              "При вібрації жилки ламаються на межі затікання припою!",
                              size=11.5, pad=10, fill="#fef2f2", stroke=RED, sw=1.5, color="#991b1b")
    f.append(bx_solder)

    # Права частина: Механічний захист та Strain Relief
    f.append(text(630, 60, "Шари захисту джгута та розвантаження", size=12, color=BLU, bold=True))

    bx_layers, _, _ = textbox(630, 190,
                              "БАГАТОШАРОВИЙ ЗАХИСТ ВІД ПЕРЕТИРАННЯ:\n\n"
                              "1. Внутрішній пучок: виті пари дротів (PTFE/силікон)\n"
                              "2. Екран: мідне луджене обплетення (покриття 85–95%)\n"
                              "3. Рукав: плетена поліефірна «зміїна шкіра» (PET)\n"
                              "4. Розгалуження: клейова термозбіжка (Dual-Wall)\n"
                              "5. Зовнішня броня в небезпечних зонах: гофрована трубка",
                              size=11.5, pad=10, fill="#f8fafc", stroke=LINE, sw=1.5)
    f.append(bx_layers)

    bx_relief, _, _ = textbox(630, 335,
                              "ПРАВИЛО РОЗВАНТАЖЕННЯ ВІД НАТЯГУ (STRAIN RELIEF):\n\n"
                              "• Перша точка кріплення (P-clip/стяжка): ≤ 50–100 мм від плати\n"
                              "• Обов'язкова сервісна петля (Service Loop) для компенсації рухів\n"
                              "• Мінімальний радіус вигину: R_bend ≥ 6 · D (статичний), ≥ 12 · D (динамічний)",
                              size=11, pad=10, fill="#f0fdf4", stroke=GRN, sw=1.5)
    f.append(bx_relief)

    return render(os.path.join(IMG, "connector-crimp-and-strain-relief.svg"), W, H, *f,
                  title="Правила обтиску контактів, захист від перетирання та розвантаження")

if __name__ == "__main__":
    fig_ground_shift()
    fig_twisted_pair_shielding()
    fig_crimp_and_strain()
    print("All figures successfully generated in ./img/")
