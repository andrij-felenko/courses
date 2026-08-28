# -*- coding: utf-8 -*-
"""Генератор SVG-діаграм для теми «Вимірювання температури живої плати»."""

import os
import sys
import math

# Додаємо scripts до шляху імпорту (4 рівні вгору від root/hw/hw-pcb/slug/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)


def draw_thermal_resistance_network():
    """Фігура 1: Еквівалентна схема теплових опорів друкованої плати та напівпровідникового компонента (JESD51)."""
    w, h = 920, 600
    frags = []

    # Заголовок діаграми
    t_box, _, _ = textbox(w / 2, 28, "Еквівалентна мережа теплових опорів: кристал → корпус → плата → середовище",
                          size=15, bold=True, fill="#f8fafc", stroke="#94a3b8")
    frags.append(t_box)

    # Ліва частина: Фізичний розріз компонента на платі
    px, py, pw, ph = 40, 70, 360, 480
    frags.append(rect(px, py, pw, ph, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(px + pw / 2, py + 22, "Фізична структура (IC + PCB)", size=13, bold=True, color=INK))

    # Радіатор / Верхнє охолодження
    frags.append(rect(px + 40, py + 45, 280, 35, fill="#e2e8f0", stroke="#64748b", sw=1.2, rx=3))
    frags.append(text(px + pw / 2, py + 67, "Радіатор / Конвекція верхньої кришки", size=11, bold=True, color="#334155"))

    # Термоінтерфейс (TIM)
    frags.append(rect(px + 60, py + 85, 240, 10, fill="#fed7aa", stroke="#f97316", sw=1.0, rx=1))
    frags.append(text(px + pw / 2, py + 93, "TIM (термопаста / клей)", size=9, bold=True, color="#c2410c"))

    # Корпус мікросхеми (Mold compound / Top Case)
    frags.append(rect(px + 50, py + 100, 260, 95, fill="#334155", stroke="#1e293b", sw=1.5, rx=4))
    frags.append(text(px + 100, py + 120, "Корпус (епоксидний компаунд)", size=11, bold=True, color="#f8fafc"))
    frags.append(text(px + pw / 2, py + 115, "Контрольна точка T_C (верх кришки)", size=10, italic=True, color="#cbd5e1"))

    # Кремнієвий кристал (Silicon Die) - джерело тепла
    frags.append(rect(px + 90, py + 135, 180, 32, fill="#ef4444", stroke="#b91c1c", sw=2.0, rx=2))
    frags.append(text(px + pw / 2, py + 155, "Кремнієвий кристал (P_diss, T_J)", size=12, bold=True, color="#ffffff"))

    # Припій кристала / Die Attach
    frags.append(rect(px + 90, py + 168, 180, 12, fill="#cbd5e1", stroke="#64748b", sw=1.0))
    frags.append(text(px + pw / 2, py + 177, "Die Attach (припій / клей)", size=9, bold=True, color="#1e293b"))

    # Відкритий нижній тепловий майданчик (Exposed Pad)
    frags.append(rect(px + 80, py + 182, 200, 14, fill="#d97706", stroke="#b45309", sw=1.5, rx=1))
    frags.append(text(px + pw / 2, py + 193, "Exposed Thermal Pad (мідна основа)", size=10, bold=True, color="#ffffff"))

    # Паяне з'єднання з платою
    frags.append(rect(px + 80, py + 198, 200, 12, fill="#94a3b8", stroke="#475569", sw=1.0))
    frags.append(text(px + pw / 2, py + 207, "Шар припою SAC305 (T_pad)", size=9, bold=True, color="#0f172a"))

    # Верхній шар плати (Top Copper)
    frags.append(rect(px + 30, py + 208, 300, 12, fill="#b45309", stroke="#78350f", sw=1.2))
    frags.append(text(px + pw / 2, py + 218, "Top Copper (полігон тепловідведення)", size=10, bold=True, color="#ffffff"))

    # Діелектрик FR-4 та теплові перехідні отвори
    frags.append(rect(px + 30, py + 222, 300, 130, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=2))
    frags.append(text(px + 80, py + 285, "FR-4 плата", size=12, bold=True, color="#15803d"))
    frags.append(text(px + 80, py + 302, "k = 0.3 Вт/(м·K)", size=10, color="#166534"))

    # Теплові перехідні отвори (Thermal Vias)
    for vx in [px + 140, px + 170, px + 200, px + 230]:
        frags.append(rect(vx - 4, py + 222, 8, 130, fill="#f59e0b", stroke="#b45309", sw=1.0))
    frags.append(text(px + 230, py + 285, "Масив Thermal Vias", size=10, bold=True, color="#92400e"))

    # Внутрішній суцільний мідний шар (GND Plane)
    frags.append(rect(px + 30, py + 265, 300, 8, fill="#b45309", stroke="#78350f", sw=1.0))

    # Нижній шар плати (Bottom Copper)
    frags.append(rect(px + 30, py + 354, 300, 12, fill="#b45309", stroke="#78350f", sw=1.2))
    frags.append(text(px + pw / 2, py + 363, "Bottom Copper / Нижня паяльна маска", size=9, bold=True, color="#ffffff"))

    # Нижнє розсіювання тепла (Bottom Convection)
    frags.append(rect(px + 40, py + 375, 280, 30, fill="#f1f5f9", stroke="#94a3b8", sw=1.0, rx=2))
    frags.append(text(px + pw / 2, py + 394, "Природна конвекція та випромінювання (T_A)", size=10, italic=True, color="#475569"))

    # Права частина: Еквівалентна електрична схема заміщення
    ex, ey, ew, eh = 430, 70, 460, 480
    frags.append(rect(ex, ey, ew, eh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(ex + ew / 2, ey + 22, "Еквівалентна електротеплова схема (Thermal RC Network)", size=13, bold=True, color=INK))

    # Вузол кристала (P_diss та T_J)
    nj_x, nj_y = ex + 130, ey + 220
    frags.append(circle(nj_x, nj_y, 7, fill="#ef4444", stroke="#b91c1c", sw=2.0))
    frags.append(text(nj_x - 15, nj_y + 5, "T_J", size=14, bold=True, color="#b91c1c", anchor="end"))
    frags.append(arrow(nj_x - 70, nj_y, nj_x - 10, nj_y, color="#ef4444", sw=2.5))
    frags.append(text(nj_x - 45, nj_y - 10, "P_diss (Вт)", size=11, bold=True, color="#ef4444", anchor="middle"))

    # Гілка вгору (Top Case Branch)
    # Резистор theta_JC_top
    frags.append(line(nj_x, nj_y, nj_x, nj_y - 45, color="#1e293b", sw=2.0))
    frags.append(rect(nj_x - 16, nj_y - 75, 32, 30, fill="#fee2e2", stroke="#b91c1c", sw=1.5, rx=2))
    frags.append(text(nj_x + 24, nj_y - 60, "θ_JC(top)", size=11, bold=True, color="#b91c1c", anchor="start"))

    # Вузол корпусу T_C
    nc_y = nj_y - 95
    frags.append(line(nj_x, nj_y - 75, nj_x, nc_y, color="#1e293b", sw=2.0))
    frags.append(circle(nj_x, nc_y, 5, fill="#3b82f6", stroke="#1d4ed8", sw=1.5))
    frags.append(text(nj_x + 12, nc_y + 4, "T_C (вимірюваний)", size=11, bold=True, color="#1d4ed8", anchor="start"))

    # Резистор theta_CA (радіатор / повітря зверху)
    frags.append(line(nj_x, nc_y, nj_x, nc_y - 30, color="#1e293b", sw=2.0))
    frags.append(rect(nj_x - 16, nc_y - 60, 32, 30, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=2))
    frags.append(text(nj_x + 24, nc_y - 45, "θ_CA (конвекція)", size=11, bold=True, color="#475569", anchor="start"))
    frags.append(line(nj_x, nc_y - 60, nj_x, nc_y - 80, color="#1e293b", sw=2.0))

    # Вузол навколишнього середовища T_A зверху
    frags.append(circle(nj_x, nc_y - 80, 5, fill="#10b981", stroke="#047857", sw=1.5))
    frags.append(text(nj_x + 15, nc_y - 76, "T_A (Ambient)", size=12, bold=True, color="#047857", anchor="start"))

    # Гілка вниз (Bottom Board Branch - основний шлях тепла >85%)
    # Резистор theta_JC_bot
    frags.append(line(nj_x, nj_y, nj_x, nj_y + 40, color="#1e293b", sw=2.0))
    frags.append(rect(nj_x - 16, nj_y + 40, 32, 30, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=2))
    frags.append(text(nj_x + 24, nj_y + 57, "θ_JC(bot)", size=11, bold=True, color="#b45309", anchor="start"))

    # Вузол паяльного майданчика T_pad
    np_y = nj_y + 90
    frags.append(line(nj_x, nj_y + 70, nj_x, np_y, color="#1e293b", sw=2.0))
    frags.append(circle(nj_x, np_y, 5, fill="#d97706", stroke="#92400e", sw=1.5))
    frags.append(text(nj_x + 12, np_y + 4, "T_pad", size=11, bold=True, color="#92400e", anchor="start"))

    # Резистор theta_vias (теплові перехідні отвори)
    frags.append(line(nj_x, np_y, nj_x, np_y + 25, color="#1e293b", sw=2.0))
    frags.append(rect(nj_x - 16, np_y + 25, 32, 30, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=2))
    frags.append(text(nj_x + 24, np_y + 42, "θ_vias (масив)", size=11, bold=True, color="#b45309", anchor="start"))

    # Резистор theta_board (розтікання в полігонах плати)
    nb_y = np_y + 75
    frags.append(line(nj_x, np_y + 55, nj_x, nb_y, color="#1e293b", sw=2.0))
    frags.append(circle(nj_x, nb_y, 5, fill="#2563eb", stroke="#1d4ed8", sw=1.5))
    frags.append(text(nj_x + 12, nb_y + 4, "T_B (температура плати)", size=11, bold=True, color="#1d4ed8", anchor="start"))

    frags.append(line(nj_x, nb_y, nj_x, nb_y + 25, color="#1e293b", sw=2.0))
    frags.append(rect(nj_x - 16, nb_y + 25, 32, 30, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=2))
    frags.append(text(nj_x + 24, nb_y + 42, "θ_BA (плата → повітря)", size=11, bold=True, color="#15803d", anchor="start"))

    # Вузол навколишнього середовища T_A знизу
    frags.append(line(nj_x, nb_y + 55, nj_x, nb_y + 80, color="#1e293b", sw=2.0))
    frags.append(circle(nj_x, nb_y + 80, 5, fill="#10b981", stroke="#047857", sw=1.5))
    frags.append(text(nj_x + 15, nb_y + 84, "T_A (Ambient)", size=12, bold=True, color="#047857", anchor="start"))

    # З'єднувальна лінія між верхнім та нижнім T_A
    frags.append(line(nj_x - 60, nc_y - 80, nj_x, nc_y - 80, color="#10b981", sw=1.5, dash="3,3"))
    frags.append(line(nj_x - 60, nb_y + 80, nj_x, nb_y + 80, color="#10b981", sw=1.5, dash="3,3"))
    frags.append(line(nj_x - 60, nc_y - 80, nj_x - 60, nb_y + 80, color="#10b981", sw=1.5, dash="3,3"))

    # Блок пояснення параметрів Psi_JT та Psi_JB
    pbx, pby, pbw, pbh = ex + 220, ey + 180, 225, 230
    frags.append(rect(pbx, pby, pbw, pbh, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=4))
    frags.append(text(pbx + pbw / 2, pby + 20, "Метрики JEDEC JESD51", size=12, bold=True, color="#0f172a"))
    
    frags.append(text(pbx + 12, pby + 48, "Характеризація Ψ_JT:", size=11, bold=True, color="#1e293b", anchor="start"))
    frags.append(text(pbx + 12, pby + 68, "T_J = T_C + Ψ_JT · P_diss", size=11, bold=True, color="#b91c1c", anchor="start"))
    frags.append(text(pbx + 12, pby + 86, "Враховує, що через верх", size=9, color="#475569", anchor="start"))
    frags.append(text(pbx + 12, pby + 100, "іде лише 2–10% тепла.", size=9, color="#475569", anchor="start"))

    frags.append(line(pbx + 10, pby + 115, pbx + pbw - 10, pby + 115, color="#cbd5e1", sw=1.0))

    frags.append(text(pbx + 12, pby + 135, "Характеризація Ψ_JB:", size=11, bold=True, color="#1e293b", anchor="start"))
    frags.append(text(pbx + 12, pby + 155, "T_J = T_B + Ψ_JB · P_diss", size=11, bold=True, color="#1d4ed8", anchor="start"))
    frags.append(text(pbx + 12, pby + 173, "Вимірюється на платі поруч", size=9, color="#475569", anchor="start"))
    frags.append(text(pbx + 12, pby + 187, "з корпусом (на відстані 1 мм).", size=9, color="#475569", anchor="start"))

    # Нижня інформаційна плашка
    frags.append(rect(40, 555, 850, 32, fill="#f1f5f9", stroke="#cbd5e1", sw=1.0, rx=3))
    frags.append(text(w / 2, 575, "Для корпусів з нижнім майданчиком (QFN, DFN, D2PAK): θ_JC(bot) ≪ θ_JC(top), понад 90% теплового потоку прямує в мідь плати.",
                      size=10, bold=True, color="#334155"))

    render(os.path.join(IMG_DIR, "pcb-thermal-resistance-network.svg"), w, h, *frags)


def draw_emissivity_correction_points():
    """Фігура 2: Порівняння дійсної та уявних температур поверхонь плати при тепловізійному контролі."""
    w, h = 920, 560
    frags = []

    # Заголовок діаграми
    t_box, _, _ = textbox(w / 2, 28, "Вплив коефіцієнта випромінювання ε та відбиття фону на тепловізор (LWIR 8–14 мкм)",
                          size=15, bold=True, fill="#f8fafc", stroke="#94a3b8")
    frags.append(t_box)

    # Лівий блок: Фізична друкована плата в тепловій рівновазі (T_true = 85.0 °C)
    bx, by, bw, bh = 40, 70, 410, 435
    frags.append(rect(bx, by, bw, bh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(bx + bw / 2, by + 22, "Фізична плата в рівновазі (T_істинна = 85.0 °C)", size=13, bold=True, color=INK))

    # Зона фону плати (Зелена паяльна маска)
    frags.append(rect(bx + 20, by + 45, 370, 330, fill="#15803d", stroke="#166534", sw=1.5, rx=4))
    frags.append(text(bx + 190, by + 68, "Паяльна маска (FR-4 PCB, ε = 0.91)", size=11, bold=True, color="#ffffff"))

    # Компонент: Силовий транзистор / контролер у чорному епоксидному корпусі
    frags.append(rect(bx + 50, by + 95, 140, 110, fill="#1e293b", stroke="#0f172a", sw=2.0, rx=3))
    frags.append(text(bx + 120, by + 145, "IC Корпус QFN", size=12, bold=True, color="#f8fafc"))
    frags.append(text(bx + 120, by + 165, "Епоксид (ε = 0.94)", size=10, color="#cbd5e1"))

    # Блискучі паяні ніжки / меніск припою (SAC305)
    for iy, py_off in enumerate([105, 125, 145, 165, 185]):
        frags.append(rect(bx + 35, by + py_off, 15, 10, fill="#e2e8f0", stroke="#64748b", sw=1.2))
        frags.append(rect(bx + 190, by + py_off, 15, 10, fill="#e2e8f0", stroke="#64748b", sw=1.2))
    frags.append(text(bx + 255, by + 145, "Паяні з'єднання", size=10, bold=True, color="#ffffff"))
    frags.append(text(bx + 255, by + 160, "Припій SAC305 (ε = 0.08)", size=9, color="#fef08a"))

    # Відкритий мідний тестовий майданчик (ENIG / Bare Copper)
    frags.append(circle(bx + 100, by + 265, 28, fill="#f59e0b", stroke="#b45309", sw=1.5))
    frags.append(text(bx + 100, by + 260, "Тестова точка", size=10, bold=True, color="#ffffff"))
    frags.append(text(bx + 100, by + 275, "Мідь (ε = 0.05)", size=9, bold=True, color="#78350f"))

    # Стрічка калібрувальна (Каптон / Матова чорна стрічка)
    frags.append(rect(bx + 180, by + 230, 180, 70, fill="#0f172a", stroke="#ef4444", sw=2.0, rx=2))
    frags.append(text(bx + 270, by + 260, "Калібрувальна стрічка", size=11, bold=True, color="#fca5a5"))
    frags.append(text(bx + 270, by + 278, "Каптон / ПВХ (ε = 0.96)", size=10, color="#fee2e2"))

    # Індикатор опорного фону
    frags.append(rect(bx + 20, by + 385, 370, 32, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=2))
    frags.append(text(bx + bw / 2, by + 405, "Температура фону / ламп T_refl = 25.0 °C (відбивається від металу)", size=10, italic=True, color="#475569"))

    # Правий блок: Що «бачить» невідкалібрований тепловізор (ε_camera = 0.95 за замовчуванням)
    rx, ry, rw, rh = 470, 70, 410, 435
    frags.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(rx + rw / 2, ry + 22, "Уявна картина тепловізора (без калібрування ε)", size=13, bold=True, color=INK))

    # Таблиця точок вимірювання
    ty = ry + 50
    rows = [
        ("Точка на платі", "ε поверхні", "T_істинна", "T_уявна (камера)", "Помилка ΔT"),
        ("Калібрувальна стрічка", "0.96", "85.0 °C", "85.6 °C", "+0.6 °C (ОК)"),
        ("Корпус IC (епоксид)", "0.94", "85.0 °C", "84.4 °C", "-0.6 °C (ОК)"),
        ("Паяльна маска FR-4", "0.91", "85.0 °C", "82.6 °C", "-2.4 °C (прийнятно)"),
        ("Паяний меніск (припій)", "0.08", "85.0 °C", "32.1 °C", "-52.9 °C (ХИБНО!)"),
        ("Відкрита мідна точка", "0.05", "85.0 °C", "29.4 °C", "-55.6 °C (ХИБНО!)"),
    ]

    for i, r_data in enumerate(rows):
        cy_r = ty + i * 36
        bg_col = "#0f172a" if i == 0 else ("#fef2f2" if i >= 4 else ("#ecfdf5" if i == 1 else "#f8fafc"))
        txt_col = "#ffffff" if i == 0 else ("#b91c1c" if i >= 4 else "#1e293b")
        bld = True if i == 0 or i >= 4 else False
        
        frags.append(rect(rx + 15, cy_r, rw - 30, 32, fill=bg_col, stroke="#cbd5e1", sw=1.0, rx=2))
        
        # Колонки
        frags.append(text(rx + 25, cy_r + 20, r_data[0], size=10, bold=bld, color=txt_col, anchor="start"))
        frags.append(text(rx + 175, cy_r + 20, r_data[1], size=10, bold=bld, color=txt_col, anchor="middle"))
        frags.append(text(rx + 235, cy_r + 20, r_data[2], size=10, bold=bld, color=txt_col, anchor="middle"))
        frags.append(text(rx + 310, cy_r + 20, r_data[3], size=10, bold=bld, color=txt_col, anchor="middle"))
        frags.append(text(rx + 375, cy_r + 20, r_data[4], size=9, bold=bld, color=txt_col, anchor="middle"))

    # Формула радіометрії Стефана-Больцмана
    fy = ry + 280
    frags.append(rect(rx + 15, fy, rw - 30, 135, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=4))
    frags.append(text(rx + rw / 2, fy + 22, "Радіометричне рівняння тепловізора:", size=11, bold=True, color="#0f172a"))
    
    frags.append(text(rx + rw / 2, fy + 48, "W_tot = ε · σ · T_obj⁴ + (1 - ε) · σ · T_refl⁴", size=12, bold=True, color="#b91c1c"))
    
    frags.append(text(rx + 25, fy + 75, "• ε ≈ 1 (діелектрик, стрічка): W_tot визначається випромінюванням тіла.", size=9, color="#334155", anchor="start"))
    frags.append(text(rx + 25, fy + 92, "• ε ≪ 1 (блискучий метал): W_tot на 90–95% є відбиттям кімнатного фону!", size=9, bold=True, color="#b91c1c", anchor="start"))
    frags.append(text(rx + 25, fy + 112, "Висновок: ніколи не вимірювати температуру на відкритому припої та міді!", size=10, bold=True, color="#1e293b", anchor="start"))

    # Нижній висновок
    frags.append(rect(40, 515, 840, 32, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=3))
    frags.append(text(w / 2, 535, "Правило верифікації: для точного ІЧ-вимірювання нанесіть матову поліімідну стрічку (Kapton) або термопасту на досліджуваний вузол.",
                      size=10, bold=True, color="#92400e"))

    render(os.path.join(IMG_DIR, "thermal-emissivity-correction-points.svg"), w, h, *frags)


if __name__ == "__main__":
    draw_thermal_resistance_network()
    draw_emissivity_correction_points()
    print("Фігури успішно згенеровано у %s" % IMG_DIR)
