# -*- coding: utf-8 -*-
"""Фігури до теми «П'єзоелектрика та зворотний п'єзоефект».
Запуск: python figs.py -> генерує SVG у ./img/
Стиль та допоміжні примітиви — зі спільного svgkit.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

BORDER = "#cbd5e1"

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'


# ── Фігура 1: Прямий та зворотний п'єзоелектричний ефекти ───────────────────
def fig_piezo_direct_inverse():
    W, H = 760, 360
    f = []

    f.append(text(W / 2, 25, "Прямий та зворотний п'єзоелектричний ефекти", size=16, bold=True, color=INK))

    # Ліва панель: Прямий п'єзоефект
    f.append(rect(20, 50, 350, 275, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(195, 75, "Прямий п'єзоефект (стиск → заряд)", size=14, bold=True, color="#1e3a8a"))

    # Сили стиску
    f.append(arrow(195, 95, 195, 125, color=POS, sw=2.5))
    f.append(text(205, 110, "F", size=12, bold=True, color=POS, anchor="start"))
    f.append(arrow(195, 255, 195, 225, color=POS, sw=2.5))
    f.append(text(205, 240, "F", size=12, bold=True, color=POS, anchor="start"))

    # П'єзокристал
    f.append(rect(125, 130, 140, 90, fill="#e2e8f0", stroke="#475569", sw=2, rx=4))
    f.append(text(195, 175, "П'єзоелектрик", size=12, bold=True, color="#334155"))

    # Поляризаційні електроди
    f.append(rect(125, 126, 140, 4, fill="#3b82f6", stroke="none"))
    f.append(rect(125, 220, 140, 4, fill="#ef4444", stroke="none"))

    # Знаки заряду
    for x in range(140, 220, 20):
        f.append(text(x, 121, "−", size=14, bold=True, color=NEG))
        f.append(text(x, 235, "+", size=14, bold=True, color=POS))

    # Виводи на вольтметр / вимірювач
    f.append(line(125, 128, 80, 128, color="#334155", sw=1.5))
    f.append(line(125, 222, 80, 222, color="#334155", sw=1.5))
    f.append(circle(80, 175, 18, fill="#ffffff", stroke="#334155", sw=2))
    f.append(text(80, 180, "V", size=12, bold=True, color="#1e293b"))
    f.append(line(80, 128, 80, 157, color="#334155", sw=1.5))
    f.append(line(80, 222, 80, 193, color="#334155", sw=1.5))

    # Пояснення прямого
    f.append(text(195, 280, "Механічне напруження σ₃₃", size=11, bold=True, color=INK))
    f.append(text(195, 298, "індукує поляризацію: D₃ = d₃₃ · σ₃₃", size=11, bold=True, color="#1e3a8a"))


    # Права панель: Зворотний п'єзоефект
    f.append(rect(390, 50, 350, 275, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(565, 75, "Зворотний п'єзоефект (напруга → деформація)", size=14, bold=True, color="#1e3a8a"))

    # П'єзокристал розширений
    f.append(rect(495, 120, 140, 110, fill="#e2e8f0", stroke="#475569", sw=2, rx=4))
    f.append(text(565, 175, "П'єзоелектрик", size=12, bold=True, color="#334155"))

    # Пунктирна рамка початкового розміру
    f.append(rect(495, 130, 140, 90, fill="none", stroke="#94a3b8", sw=1.5, rx=4))
    f.append(line(495, 130, 635, 130, color="#94a3b8", sw=1.5, dash="3,3"))
    f.append(line(495, 220, 635, 220, color="#94a3b8", sw=1.5, dash="3,3"))

    # Стрілки деформації
    f.append(arrow(565, 130, 565, 112, color=FIELD, sw=2.5))
    f.append(arrow(565, 220, 565, 238, color=FIELD, sw=2.5))
    f.append(text(580, 112, "+ΔS", size=11, bold=True, color=FIELD, anchor="start"))

    # Електроди
    f.append(rect(495, 116, 140, 4, fill="#ef4444", stroke="none"))
    f.append(rect(495, 230, 140, 4, fill="#3b82f6", stroke="none"))

    # Виводи до джерела живлення
    f.append(line(635, 118, 685, 118, color="#334155", sw=1.5))
    f.append(line(635, 232, 685, 232, color="#334155", sw=1.5))
    f.append(circle(685, 175, 18, fill="#ffffff", stroke="#334155", sw=2))
    f.append(text(685, 179, "U", size=12, bold=True, color="#1e293b"))
    f.append(line(685, 118, 685, 157, color="#334155", sw=1.5))
    f.append(line(685, 232, 685, 193, color="#334155", sw=1.5))
    f.append(text(710, 168, "+", size=13, bold=True, color=POS))
    f.append(text(710, 188, "−", size=13, bold=True, color=NEG))

    # Пояснення зворотного
    f.append(text(565, 280, "Зовнішнє електричне поле E₃", size=11, bold=True, color=INK))
    f.append(text(565, 298, "викликає деформацію: S₃₃ = d₃₃ · E₃", size=11, bold=True, color="#1e3a8a"))

    f.append(text(W / 2, H - 12, "Прямий та зворотний ефекти описуються тими самими п'єзомодулями d₃₃ за лінійною теорією", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'piezo-direct-inverse.svg'), W, H, "\n".join(f))


# ── Фігура 2: Симетрія кристалічної ґратки та виникнення дипольного моменту ──
def fig_crystal_symmetry_polarization():
    W, H = 760, 360
    f = []

    f.append(text(W / 2, 25, "Мікроскопічний механізм: центросиметричні та нецентросиметричні кристали", size=15, bold=True, color=INK))

    # Лівий блок: Центросиметрична ґратка (без п'єзоефекту)
    f.append(rect(20, 50, 350, 275, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(195, 75, "Центросиметрична ґратка (NaCl, Si)", size=13, bold=True, color="#334155"))

    # Схема іонів без деформації та з деформацією
    cx1, cy1 = 195, 165
    f.append(circle(cx1, cy1, 14, fill="#ef4444", stroke="none")) # Катіон (+)
    f.append(text(cx1, cy1 + 4, "+", size=14, bold=True, color="#ffffff"))

    anions1 = [(cx1 - 50, cy1), (cx1 + 50, cy1), (cx1, cy1 - 50), (cx1, cy1 + 50)]
    for ax, ay in anions1:
        f.append(line(cx1, cy1, ax, ay, color="#94a3b8", sw=1.5, dash="2,2"))
        f.append(circle(ax, ay, 10, fill="#3b82f6", stroke="none"))
        f.append(text(ax, ay + 3, "−", size=12, bold=True, color="#ffffff"))

    # Стиск
    f.append(arrow(195, 88, 195, 102, color=POS, sw=2))
    f.append(arrow(195, 242, 195, 228, color=POS, sw=2))

    f.append(text(195, 275, "Центр позитивних і негативних зарядів", size=11, bold=True, color=INK))
    f.append(text(195, 293, "збігається в одній точці: P = 0", size=11, bold=True, color="#dc2626"))


    # Правий блок: Нецентросиметрична ґратка (Кварц α-SiO2 / PZT)
    f.append(rect(390, 50, 350, 275, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(565, 75, "Нецентросиметрична ґратка (кварц, PZT)", size=13, bold=True, color="#1e3a8a"))

    # Асиметричний іонний трикутник/тетраедр
    cx2, cy2 = 565, 172
    f.append(circle(cx2, cy2 - 12, 14, fill="#ef4444", stroke="none")) # Катіон Si4+ / Ti4+
    f.append(text(cx2, cy2 - 8, "+", size=14, bold=True, color="#ffffff"))

    anions2 = [(cx2 - 45, cy2 + 25), (cx2 + 45, cy2 + 25), (cx2, cy2 - 52)]
    for ax, ay in anions2:
        f.append(line(cx2, cy2 - 12, ax, ay, color="#94a3b8", sw=1.5, dash="2,2"))
        f.append(circle(ax, ay, 10, fill="#3b82f6", stroke="none"))
        f.append(text(ax, ay + 3, "−", size=12, bold=True, color="#ffffff"))

    # Сили стиску
    f.append(arrow(565, 88, 565, 102, color=POS, sw=2))
    f.append(arrow(565, 242, 565, 228, color=POS, sw=2))

    # Стрілка дипольного моменту p
    f.append(arrow(565, cy2 + 20, 565, cy2 - 25, color=FIELD, sw=2.5))
    f.append(text(580, cy2 - 5, "p = q · Δx", size=12, bold=True, color=FIELD, anchor="start"))

    f.append(text(565, 275, "Деформація зсуває центри зарядів:", size=11, bold=True, color=INK))
    f.append(text(565, 293, "виникає ненульова поляризація P ≠ 0", size=11, bold=True, color=FIELD))

    f.append(text(W / 2, H - 12, "Відсутність центра інверсії — необхідна умова існування п'єзоелектричного ефекту", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'crystal-symmetry-polarization.svg'), W, H, "\n".join(f))


# ── Фігура 3: Процес поляризації (poling) п'єзокераміки PZT ────────────────
def fig_pzt_domain_poling():
    W, H = 760, 370
    f = []

    f.append(text(W / 2, 25, "Процес високовольтної поляризації (Poling) п'єзокераміки", size=15, bold=True, color=INK))

    stages = [
        ("1. Неполяризована кераміка", "Хаотичні домени\nNet P = 0\nT < T_c", "#f1f5f9", "unpoled"),
        ("2. Гаряча поляризація", "Прикладено сильне поле E\nT ≈ T_c (E > E_c)", "#fef3c7", "poling"),
        ("3. Залишкова поляризація", "Охолодження та зняття E\nЗалишкова P_r > 0", "#ecfdf5", "poled")
    ]

    sw_box = 225
    sh_box = 265
    y_top = 55

    for idx, (stitle, ssub, sbg, stype) in enumerate(stages):
        x0 = 20 + idx * 245
        f.append(rect(x0, y_top, sw_box, sh_box, fill=sbg, stroke=BORDER, rx=6))
        f.append(text(x0 + sw_box / 2, y_top + 22, stitle, size=12, bold=True, color="#1e293b"))

        # П'єзокерамичний блок
        cx = x0 + sw_box / 2
        cy = y_top + 120
        f.append(rect(cx - 85, cy - 50, 170, 100, fill="#ffffff", stroke="#475569", sw=1.5, rx=4))

        # Домени з векторами поляризації
        if stype == "unpoled":
            f.append(line(cx - 85, cy, cx + 85, cy, color="#cbd5e1", sw=1))
            f.append(line(cx, cy - 50, cx, cy + 50, color="#cbd5e1", sw=1))
            f.append(arrow(cx - 40, cy - 10, cx - 70, cy - 35, color="#64748b", sw=1.8))
            f.append(arrow(cx + 40, cy - 35, cx + 70, cy - 10, color="#64748b", sw=1.8))
            f.append(arrow(cx - 60, cy + 35, cx - 25, cy + 15, color="#64748b", sw=1.8))
            f.append(arrow(cx + 25, cy + 35, cx + 60, cy + 15, color="#64748b", sw=1.8))
        elif stype == "poling":
            f.append(rect(cx - 85, cy - 54, 170, 4, fill="#ef4444", stroke="none"))
            f.append(rect(cx - 85, cy + 50, 170, 4, fill="#3b82f6", stroke="none"))
            for ex in [cx - 60, cx, cx + 60]:
                f.append(arrow(ex, cy - 42, ex, cy + 42, color="#dc2626", sw=2))
            f.append(text(cx + 72, cy, "E_pol", size=11, bold=True, color="#dc2626"))
        elif stype == "poled":
            for dx_off, dy_off in [(-50, -20), (-20, -25), (20, -20), (50, -25),
                                   (-45, 20), (-15, 25), (25, 20), (55, 25)]:
                f.append(arrow(cx + dx_off, cy + dy_off - 15, cx + dx_off, cy + dy_off + 15, color=FIELD, sw=2))
            f.append(text(cx + 72, cy, "P_r", size=12, bold=True, color=FIELD))

        lines = ssub.split("\n")
        for l_i, l_txt in enumerate(lines):
            f.append(text(cx, y_top + sh_box - 55 + l_i * 18, l_txt, size=11, bold=True, color=INK))

    f.append(text(W / 2, H - 12, "Після поляризації ізотропна кераміка PZT набуває макроскопічних п'єзоелектричних властивостей", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'pzt-domain-poling.svg'), W, H, "\n".join(f))


# ── Фігура 4: Конструкція та принцип роботи SAW-фільтра ────────────────────
def fig_saw_filter_structure():
    W, H = 760, 360
    f = []

    f.append(text(W / 2, 25, "Принцип роботи SAW-фільтра (поверхневі акустичні хвилі)", size=15, bold=True, color=INK))

    # П'єзоелектрична підкладка (LiNbO3, ST-cut quartz)
    f.append(rect(40, 160, 680, 130, fill="#e2e8f0", stroke="#475569", sw=2, rx=6))
    f.append(text(380, 260, "П'єзоелектрична монокристалічна підкладка (LiNbO₃ / α-SiO₂)", size=12, bold=True, color="#334155"))

    # Вхідний зустрічно-штирьовий перетворювач (IDT 1)
    f.append(text(160, 60, "Вхідний IDT", size=13, bold=True, color="#1e3a8a"))
    f.append(line(70, 80, 250, 80, color="#1d4ed8", sw=3))
    f.append(line(70, 140, 250, 140, color="#2563eb", sw=3))

    for ix, x_pos in enumerate(range(90, 240, 25)):
        if ix % 2 == 0:
            f.append(line(x_pos, 80, x_pos, 175, color="#1d4ed8", sw=3))
        else:
            f.append(line(x_pos, 140, x_pos, 162, color="#2563eb", sw=3))

    # Вхідний сигнал RF in
    f.append(circle(50, 110, 16, fill="#ffffff", stroke="#1d4ed8", sw=2))
    f.append(text(50, 114, "RF", size=10, bold=True, color="#1d4ed8"))
    f.append(line(50, 80, 50, 94, color="#1d4ed8", sw=1.5))
    f.append(line(50, 140, 50, 126, color="#2563eb", sw=1.5))
    f.append(line(50, 80, 70, 80, color="#1d4ed8", sw=1.5))
    f.append(line(50, 140, 70, 140, color="#2563eb", sw=1.5))

    # Поверхнева акустична хвиля
    saw_path = []
    for x_p in range(240, 520, 5):
        y_p = 160 + 8 * math.sin((x_p - 240) * 0.1)
        saw_path.append(f"{x_p:.1f},{y_p:.1f}")
    f.append(path_svg("M " + " L ".join(saw_path), fill="none", stroke="#dc2626", sw=2.5))
    f.append(arrow(340, 135, 420, 135, color="#dc2626", sw=2))
    f.append(text(380, 122, "Хвиля Релея (v_SAW ≈ 3000 м/с)", size=11, bold=True, color="#dc2626"))

    # Вихідний зустрічно-штирьовий перетворювач (IDT 2)
    f.append(text(600, 60, "Вихідний IDT", size=13, bold=True, color="#1e3a8a"))
    f.append(line(510, 80, 690, 80, color="#15803d", sw=3))
    f.append(line(510, 140, 690, 140, color="#16a34a", sw=3))

    for ix, x_pos in enumerate(range(530, 680, 25)):
        if ix % 2 == 0:
            f.append(line(x_pos, 80, x_pos, 175, color="#15803d", sw=3))
        else:
            f.append(line(x_pos, 140, x_pos, 162, color="#16a34a", sw=3))

    # Вихідний сигнал RF out
    f.append(circle(710, 110, 16, fill="#ffffff", stroke="#15803d", sw=2))
    f.append(text(710, 114, "OUT", size=9, bold=True, color="#15803d"))
    f.append(line(690, 80, 710, 80, color="#15803d", sw=1.5))
    f.append(line(690, 140, 710, 140, color="#16a34a", sw=1.5))
    f.append(line(710, 80, 710, 94, color="#15803d", sw=1.5))
    f.append(line(710, 140, 710, 126, color="#16a34a", sw=1.5))

    # Крок електродів lambda
    f.append(line(115, 205, 165, 205, color="#1e293b", sw=1.5))
    f.append(line(115, 198, 115, 212, color="#1e293b", sw=1.5))
    f.append(line(165, 198, 165, 212, color="#1e293b", sw=1.5))
    f.append(text(140, 222, "p = λ_SAW", size=11, bold=True, color="#1e293b"))

    f.append(text(W / 2, H - 12, "Центральна частота фільтрації: f₀ = v_SAW / p, де p — крок штирів зустрічно-штирьової системи", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'saw-filter-structure.svg'), W, H, "\n".join(f))


if __name__ == '__main__':
    fig_piezo_direct_inverse()
    fig_crystal_symmetry_polarization()
    fig_pzt_domain_poling()
    fig_saw_filter_structure()
    print("Всі 4 фігури згенеровано успішно в ./img/")
