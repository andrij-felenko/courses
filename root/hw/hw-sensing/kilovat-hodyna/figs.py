# -*- coding: utf-8 -*-
"""Фігури до теми «Кіловат-година: облік енергії в пристрої».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys
import os
import math

# Додаємо scripts до шляху пошуку модулів (4 рівні вгору від root/hw/hw-sensing/kilovat-hodyna)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

COLOR_IMP = "#2457d6"      # Імпорт / Синій
COLOR_EXP = "#c0392b"      # Експорт / Червоний
COLOR_IND = "#d35400"      # Індуктивна / Помаранчевий
COLOR_CAP = "#27ae60"      # Ємнісна / Зелений
COLOR_GRID = "#d6dde6"
COLOR_ACCENT = "#8e44ad"   # Фіолетовий акцент


# ── Фігура 1: 4-квадрантна площина потужності та енергії ─────────────────────
def fig_four_quadrant_plane():
    W, H = 820, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    cx, cy = 410, 290
    qw, qh = 350, 210

    # 4 квадрантні підкладки
    # Q2: Лівий верх (P < 0, Q > 0)
    f.append(rect(cx - qw, cy - qh, qw, qh, fill="#fff5f5", stroke=COLOR_GRID, sw=1, rx=4))
    # Q1: Правий верх (P > 0, Q > 0)
    f.append(rect(cx, cy - qh, qw, qh, fill="#f4f7fc", stroke=COLOR_GRID, sw=1, rx=4))
    # Q3: Лівий низ (P < 0, Q < 0)
    f.append(rect(cx - qw, cy, qw, qh, fill="#fdfbf7", stroke=COLOR_GRID, sw=1, rx=4))
    # Q4: Правий низ (P > 0, Q < 0)
    f.append(rect(cx, cy, qw, qh, fill="#f4faf6", stroke=COLOR_GRID, sw=1, rx=4))

    # Головні осі координат
    f.append(line(40, cy, 780, cy, color=LINE, sw=2))
    f.append(arrow(770, cy, 795, cy, color=LINE, sw=2))
    f.append(line(cx, 510, cx, 60, color=LINE, sw=2))
    f.append(arrow(cx, 70, cx, 45, color=LINE, sw=2))

    # Підписи осей
    f.append(text(760, cy + 24, "+P (Імпорт активної)", size=12, bold=True, color=COLOR_IMP, anchor="end"))
    f.append(text(60, cy + 24, "-P (Експорт активної)", size=12, bold=True, color=COLOR_EXP, anchor="start"))
    f.append(text(cx + 12, 55, "+Q (Індуктивна реактивна, Lagging)", size=12, bold=True, color=COLOR_IND, anchor="start"))
    f.append(text(cx + 12, 525, "-Q (Ємнісна реактивна, Leading)", size=12, bold=True, color=COLOR_CAP, anchor="start"))

    # Вміст Квадранта I (Q1)
    b_q1, _, _ = textbox(cx + 175, cy - 150, "КВАДРАНТ I (Q1)\nІмпорт P (+P)  |  Індуктивна Q (+Q)\nСтрум відстає від напруги (0° < φ < 90°)\nНавантаження: асинхронні двигуни, ТП", 
                         size=11, pad=8, fill="#ffffff", stroke=COLOR_IMP, sw=1.4)
    f.append(b_q1)

    # Вміст Квадранта II (Q2)
    b_q2, _, _ = textbox(cx - 175, cy - 150, "КВАДРАНТ II (Q2)\nЕкспорт P (-P)  |  Індуктивна Q (+Q)\nГенерація активної, споживання індуктивної\nСинхронний генератор (недозбудження)", 
                         size=11, pad=8, fill="#ffffff", stroke=COLOR_EXP, sw=1.4)
    f.append(b_q2)

    # Вміст Квадранта III (Q3)
    b_q3, _, _ = textbox(cx - 175, cy + 110, "КВАДРАНТ III (Q3)\nЕкспорт P (-P)  |  Ємнісна Q (-Q)\nСтрум випереджає напругу (-180° < φ < -90°)\nСонячний інвертор (генерація в мережу)", 
                         size=11, pad=8, fill="#ffffff", stroke=COLOR_EXP, sw=1.4)
    f.append(b_q3)

    # Вміст Квадранта IV (Q4)
    b_q4, _, _ = textbox(cx + 175, cy + 110, "КВАДРАНТ IV (Q4)\nІмпорт P (+P)  |  Ємнісна Q (-Q)\nСтрум випереджає напругу (-90° < φ < 0°)\nІмпульсні БЖ з X-конденсаторами, КБ", 
                         size=11, pad=8, fill="#ffffff", stroke=COLOR_CAP, sw=1.4)
    f.append(b_q4)

    # Кутові стрілки обертання та фазори в центрі
    f.append(circle(cx, cy, 5, fill=LINE, stroke=LINE, sw=1))
    
    render(os.path.join(IMG, "four-quadrant-plane.svg"), W, H, *f, 
           title="4-квадрантна площина обліку активної та реактивної енергії")


# ── Фігура 2: Миттєва потужність та її розклад ───────────────────────────────
def fig_instantaneous_power():
    W, H = 820, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Вісь часу
    ox = 80
    oy = 230
    gw = 680
    gh = 160

    # Сітка та нульова лінія
    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.6))
    f.append(arrow(ox + gw - 10, oy, ox + gw + 15, oy, color=LINE, sw=1.6))
    f.append(text(ox + gw + 20, oy + 4, "t", size=13, bold=True, color=LINE, anchor="start"))
    f.append(line(ox, oy - gh, ox, oy + gh, color=LINE, sw=1.6))
    f.append(arrow(ox, oy - gh + 10, ox, oy - gh - 15, color=LINE, sw=1.6))
    f.append(text(ox - 10, oy - gh - 8, "p(t), v(t), i(t)", size=12, bold=True, color=LINE, anchor="end"))

    # Генеруємо точки синусоїд для φ = 45°
    phi = math.pi / 4  # 45 deg
    points_v = []
    points_i = []
    points_p = []
    
    N = 120
    t_max = 2 * math.pi * 2 # 2 періоди
    for k in range(N + 1):
        wt = k * t_max / N
        px = ox + (k / N) * (gw - 40)
        
        v_val = math.sin(wt) * 90
        i_val = math.sin(wt - phi) * 65
        p_val = (v_val / 90.0) * (i_val / 65.0) * 110  # масштаб p(t)
        
        points_v.append((px, oy - v_val))
        points_i.append((px, oy - i_val))
        points_p.append((px, oy - p_val))

    # Малюємо заливку негативної енергії (коли p(t) < 0 — енергія повертається в джерело)
    for k in range(N):
        x1, y1 = points_p[k]
        x2, y2 = points_p[k+1]
        if y1 > oy or y2 > oy:
            py1 = max(y1, oy)
            py2 = max(y2, oy)
            f.append(f'<polygon points="{x1:.1f},{oy:.1f} {x1:.1f},{py1:.1f} {x2:.1f},{py2:.1f} {x2:.1f},{oy:.1f}" fill="#ffebee" stroke="none"/>')

    # Лінії кривих
    def path_from_points(pts):
        return "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

    f.append(f'<path d="{path_from_points(points_v)}" fill="none" stroke="{COLOR_IMP}" stroke-width="1.8" stroke-dasharray="4,3"/>')
    f.append(f'<path d="{path_from_points(points_i)}" fill="none" stroke="{COLOR_IND}" stroke-width="1.8" stroke-dasharray="2,2"/>')
    f.append(f'<path d="{path_from_points(points_p)}" fill="none" stroke="{COLOR_EXP}" stroke-width="2.5"/>')

    # Лінія середньої активної потужності P
    p_avg_y = oy - (math.cos(phi) * 0.5 * 110)
    f.append(line(ox, p_avg_y, ox + gw - 40, p_avg_y, color=COLOR_ACCENT, sw=2, dash="6,4"))
    f.append(text(ox + gw - 30, p_avg_y - 6, "P = V_RMS · I_RMS · cos(φ)", size=11, bold=True, color=COLOR_ACCENT, anchor="start"))

    # Позначки та легенда
    b_leg, _, _ = textbox(410, 425, 
                          "Легенда:  -- v(t) Напруга (синій)    ·· i(t) Струм із відставанням φ = 45° (помаранчевий)\n"
                          "— p(t) = v(t) · i(t) Миттєва потужність (червоний)   - - P Середня активна потужність (фіолетовий)\n"
                          "Червоні зони нижче нуля — зворотний потік енергії в реактивних елементах кола (Q)",
                          size=11, pad=10, fill="#f8f9fa", stroke=LINE, sw=1.2)
    f.append(b_leg)

    render(os.path.join(IMG, "instantaneous-power-components.svg"), W, H, *f,
           title="Миттєва потужність p(t), активна складова P та реактивні пульсації")


# ── Фігура 3: DSP-конвеєр вимірювання та обчислення енергії ──────────────────
def fig_energy_meter_dsp_pipeline():
    W, H = 860, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Вхідні сигнали
    f.append(text(50, 95, "v(t) Напруга\n(Дільник/ТН)", size=11, bold=True, color=COLOR_IMP, anchor="middle"))
    f.append(arrow(95, 95, 125, 95, color=LINE, sw=1.8))

    f.append(text(50, 195, "i(t) Струм\n(Шунт/ТC)", size=11, bold=True, color=COLOR_IND, anchor="middle"))
    f.append(arrow(95, 195, 125, 195, color=LINE, sw=1.8))

    # Блок АЦП
    f.append(fitbox(130, 65, 100, 60, "Sigma-Delta\nADC (V)\n24-bit / 8 kSps", size=11, fill="#eaf2f8", stroke=COLOR_IMP, bold=True))
    f.append(fitbox(130, 165, 100, 60, "Sigma-Delta\nADC (I)\n24-bit / 8 kSps", size=11, fill="#fef5e7", stroke=COLOR_IND, bold=True))

    # Стрілки від АЦП до фільтрів
    f.append(arrow(230, 95, 260, 95, color=LINE, sw=1.8))
    f.append(arrow(230, 195, 260, 195, color=LINE, sw=1.8))

    # Блоки видалення зміщення HPF та калібрування фази
    f.append(fitbox(265, 65, 110, 60, "HPF Фільтр\n(DC Removal)\n+ Gain v[n]", size=11, fill=FILL, stroke=LINE))
    f.append(fitbox(265, 165, 110, 60, "Phase Delay\nCompensation\n+ Gain i[n]", size=11, fill=FILL, stroke=LINE))

    # Множення для миттєвої потужності p[n] = v[n] * i[n]
    f.append(arrow(375, 95, 430, 135, color=LINE, sw=1.8))
    f.append(arrow(375, 195, 430, 155, color=LINE, sw=1.8))

    f.append(circle(445, 145, 18, fill="#ffffff", stroke=COLOR_EXP, sw=2))
    f.append(text(445, 150, "×", size=20, bold=True, color=COLOR_EXP))
    f.append(text(445, 120, "p[n] = v[n] · i[n]", size=10, bold=True, color=COLOR_EXP))

    # Блок обчислення реактивної потужності q[n] (через зсув 90°)
    f.append(line(340, 95, 340, 285, color=LINE, sw=1.5))
    f.append(arrow(340, 285, 400, 285, color=LINE, sw=1.5))
    f.append(fitbox(405, 260, 90, 50, "Hilbert / 90°\nDelay v_90[n]", size=10, fill="#f4faf6", stroke=COLOR_CAP))
    f.append(arrow(495, 285, 525, 285, color=LINE, sw=1.5))

    f.append(line(375, 195, 500, 195, color=LINE, sw=1.5))
    f.append(arrow(500, 195, 535, 275, color=LINE, sw=1.5))

    f.append(circle(540, 285, 16, fill="#ffffff", stroke=COLOR_CAP, sw=2))
    f.append(text(540, 290, "×", size=18, bold=True, color=COLOR_CAP))
    f.append(text(540, 260, "q[n] = v_90 · i", size=10, bold=True, color=COLOR_CAP))

    # Фільтрація / Низькочастотний акумулятор потужності P та Q
    f.append(arrow(463, 145, 530, 145, color=LINE, sw=1.8))
    f.append(fitbox(535, 115, 110, 60, "LPF Фільтр /\nУсереднення\nP_avg, Q_avg", size=11, fill="#ffffff", stroke=COLOR_ACCENT, bold=True))

    f.append(arrow(556, 285, 590, 285, color=LINE, sw=1.5))
    f.append(line(590, 285, 590, 175, color=LINE, sw=1.5))

    # 4-квадрантний класифікатор
    f.append(arrow(645, 145, 680, 145, color=LINE, sw=1.8))
    f.append(fitbox(685, 105, 135, 80, "4-Квадрантний\nКласифікатор\n(Q1 / Q2 / Q3 / Q4)\n+ Anti-creep фільтр", size=11, fill="#fdfbf7", stroke=COLOR_IND, bold=True))

    # Стрілка вниз до 64-бітних акумуляторів
    f.append(arrow(752, 185, 752, 230, color=LINE, sw=1.8))

    # 64-бітні акумулятори енергії
    b_acc, _, _ = textbox(560, 395, 
                          "Енергетичні 64-бітні Реєстри Накопичення (SRAM Micro-Joule Accumulators)\n"
                          "• E_act_imp: Активна енергія імпорт (+P, кВт·год)\n"
                          "• E_act_exp: Активна енергія експорт (-P, кВт·год)\n"
                          "• E_react_ind: Реактивна індуктивна (+Q, квар·год)\n"
                          "• E_react_cap: Реактивна ємнісна (-Q, квар·год)",
                          size=11, pad=10, fill="#f4f7fc", stroke=COLOR_IMP, sw=1.5)
    f.append(b_acc)

    f.append(arrow(685, 270, 685, 330, color=LINE, sw=1.8))

    # NVM Wear-Leveling блок
    f.append(arrow(340, 395, 230, 395, color=LINE, sw=1.8))
    f.append(fitbox(50, 360, 175, 70, "Flash / EEPROM NVM\nWear-Leveling Ring Buffer\n+ CRC32 / Power-Fail Safe", size=11, fill="#fff5f5", stroke=COLOR_EXP, bold=True))

    render(os.path.join(IMG, "energy-meter-dsp-pipeline.svg"), W, H, *f,
           title="Цифровий конвеєр обробки сигналів та 4-квадрантного обліку енергії")


# ── Фігура 4: Кільцевий NVM Wear-Leveling буфер для енергонезалежної пам'яті ─
def fig_flash_wear_leveling_ring():
    W, H = 860, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Дворівнева схема накопичення: SRAM -> Flash Ring Buffer
    b_sram, _, _ = textbox(140, 150, "Рівень 1: Швидка SRAM\n• Дробовий мікро-джоульний\n  акумулятор (uint64_t)\n• Оновлення: 8 кГц (125 мкс)\n• Необмежений ресурс запису",
                           size=11, pad=10, fill="#eaf2f8", stroke=COLOR_IMP, sw=1.5)
    f.append(b_sram)

    # Стрілка та умова перенесення
    f.append(arrow(260, 150, 345, 150, color=LINE, sw=1.8))
    b_trig, _, _ = textbox(302, 100, "Подія запису:\nΔE ≥ 1 Вт·год\nабо Power-Fail",
                           size=10, pad=6, fill="#fff0f0", stroke=COLOR_EXP, sw=1.2, color=COLOR_EXP, bold=True)
    f.append(b_trig)

    # Рівень 2: Flash/EEPROM Кільцевий сектор (Ring Buffer Slots)
    f.append(rect(360, 55, 470, 245, fill="#fafbfc", stroke=LINE, sw=1.5, rx=6))
    f.append(text(595, 80, "Рівень 2: Енергонезалежна пам'ять (Flash / EEPROM Сектор)", size=12, bold=True, color=LINE, anchor="middle"))

    # Слоти кільцевого буфера
    slot_w = 95
    slot_h = 165
    sx0 = 380
    sy0 = 105

    slots_data = [
        ("Слот #0\n(Seq: 1041)\nValid OK\nE: 142.1 кВт·год\nCRC: 0x9A4F", "#eafaf1", COLOR_CAP),
        ("Слот #1\n(Seq: 1042)\nValid OK\nE: 142.2 кВт·год\nCRC: 0x3B12", "#eafaf1", COLOR_CAP),
        ("Слот #2\n(Seq: 1043)\nАКТИВНИЙ\nE: 142.3 кВт·год\nCRC: 0x7E89", "#fff4e6", COLOR_IND),
        ("Слот #3\n(0xFF...FF)\nВільний\n(Готовий до\nзапису)", "#ffffff", COLOR_GRID),
    ]

    for idx, (stext, sfill, sstroke) in enumerate(slots_data):
        bx = sx0 + idx * (slot_w + 15)
        f.append(fitbox(bx, sy0, slot_w, slot_h, stext, size=10, fill=sfill, stroke=sstroke, sw=1.4))

    # Стрілка покажчика запису на слот #2
    f.append(arrow(625, 320, 625, 280, color=COLOR_IND, sw=2))
    f.append(text(625, 338, "Поточний дійсний запис (Seq MAX)", size=11, bold=True, color=COLOR_IND, anchor="middle"))

    # Опис структури слота внизу
    b_struct, _, _ = textbox(430, 410, 
                             "Анатомія слота журналу: [ Magic (2B) | SeqID (4B) | E_act_imp (8B) | E_act_exp (8B) | E_react (16B) | CRC16 (2B) ]\n"
                             "При старті МК: сканування сектору → перевірка CRC → вибір слота з максимальним SeqID.\n"
                             "Збільшення ресурсу пам'яті у N разів (де N — кількість слотів у секторі).",
                             size=11, pad=10, fill="#f8f9fa", stroke=LINE, sw=1.2)
    f.append(b_struct)

    render(os.path.join(IMG, "flash-wear-leveling-ring.svg"), W, H, *f,
           title="Кільцевий буфер енергонезалежного зберігання (Wear-Leveling) та захист від збоїв")


if __name__ == "__main__":
    fig_four_quadrant_plane()
    fig_instantaneous_power()
    fig_energy_meter_dsp_pipeline()
    fig_flash_wear_leveling_ring()
    print("Всі фігури успішно згенеровано у ./img/")
