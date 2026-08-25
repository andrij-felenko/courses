# -*- coding: utf-8 -*-
"""Фігури до теми «Спин-орбітальний обертальний момент (SOT)».
Запуск: python figs.py -> генерує SVG у ./img/
Стиль та допоміжні функції — зі спільного svgkit.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

BORDER = "#cbd5e1"

# ── Фігура 1: Спиновий ефект Холла та ефект Рашби-Едельштейна ───────────────
def fig_spin_hall_and_rashba():
    W, H = 820, 460
    f = []

    f.append(text(W / 2, 26, "Мікроскопічні механізми генерації SOT у гетероструктурах", size=16, bold=True, color=INK, anchor="middle"))

    # Ліва панель: Спиновий ефект Холла (SHE)
    x1, y1, w1, h1 = 20, 50, 380, 370
    f.append(rect(x1, y1, w1, h1, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(x1 + w1 / 2, y1 + 24, "Об'ємний спиновий ефект Холла (SHE)", size=13, bold=True, color="#1e293b", anchor="middle"))

    # Важкий метал шар
    hm_y = y1 + 120
    hm_h = 150
    f.append(rect(x1 + 25, hm_y, 330, hm_h, fill="#e2e8f0", stroke="#94a3b8", rx=4))
    f.append(text(x1 + 35, hm_y + 20, "Важкий метал (Pt, W, Ta)", size=11, bold=True, color="#475569", anchor="start"))

    # Струм заряду J_c
    f.append(arrow(x1 + 40, hm_y + hm_h / 2, x1 + 290, hm_y + hm_h / 2, color="#2563eb", sw=3))
    f.append(text(x1 + 165, hm_y + hm_h / 2 - 10, "Зарядовий струм J_c (уздовж x)", size=11, bold=True, color="#1d4ed8", anchor="middle"))

    # Відхилення спінів
    for cx in [x1 + 90, x1 + 165, x1 + 240]:
        f.append(circle(cx, hm_y + 35, 10, fill="#fef08a", stroke="#ca8a04"))
        f.append(arrow(cx, hm_y + 42, cx, hm_y + 26, color="#ca8a04", sw=2))

    for cx in [x1 + 90, x1 + 165, x1 + 240]:
        f.append(circle(cx, hm_y + 115, 10, fill="#bfdbfe", stroke="#2563eb"))
        f.append(arrow(cx, hm_y + 108, cx, hm_y + 124, color="#2563eb", sw=2))

    # Спиновий струм J_s (уздовж z)
    f.append(arrow(x1 + 310, hm_y + 125, x1 + 310, hm_y + 20, color="#dc2626", sw=3))
    f.append(text(x1 + 345, hm_y + 70, "J_s (z)", size=11, bold=True, color="#dc2626", anchor="middle"))

    f.append(text(x1 + w1 / 2, y1 + h1 - 40, "Спиновий струм генерується в об'ємі HM", size=11, bold=True, color="#334155", anchor="middle"))
    f.append(text(x1 + w1 / 2, y1 + h1 - 22, "завдяки спин-орбітальному розсіюванню електронів", size=10, color=MUTED, anchor="middle"))

    # Права панель: Ефект Рашби-Едельштейна (REE)
    x2, y2, w2, h2 = 420, 50, 380, 370
    f.append(rect(x2, y2, w2, h2, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(x2 + w2 / 2, y2 + 24, "Інтерфейсний ефект Рашби-Едельштейна (REE)", size=13, bold=True, color="#1e293b", anchor="middle"))

    # Межа розділу HM/FM
    int_y = y2 + 160
    f.append(rect(x2 + 25, int_y - 65, 330, 65, fill="#f1f5f9", stroke="#cbd5e1"))
    f.append(text(x2 + 35, int_y - 45, "Феромагнетик (CoFeB)", size=11, bold=True, color="#0f172a", anchor="start"))

    f.append(rect(x2 + 25, int_y, 330, 65, fill="#e2e8f0", stroke="#cbd5e1"))
    f.append(text(x2 + 35, int_y + 20, "Важкий метал (Pt, Ta)", size=11, bold=True, color="#475569", anchor="start"))

    # Межа розділу (червона лінія)
    f.append(line(x2 + 25, int_y, x2 + 355, int_y, color="#dc2626", sw=2.5))
    f.append(text(x2 + 190, int_y - 10, "Інтерфейс з порушеною симетрією z", size=10, bold=True, color="#dc2626", anchor="middle"))

    # Внутрішнє електричне поле E_z
    f.append(arrow(x2 + 55, int_y + 45, x2 + 55, int_y - 45, color="#9333ea", sw=2.5))
    f.append(text(x2 + 75, int_y, "E_z", size=11, bold=True, color="#9333ea", anchor="start"))

    # Ефективне поле Рашби B_R та накопичення спінів
    f.append(circle(x2 + 220, int_y, 14, fill="#fef08a", stroke="#ca8a04", sw=2))
    f.append(arrow(x2 + 206, int_y, x2 + 234, int_y, color="#ca8a04", sw=2.5))
    f.append(text(x2 + 220, int_y + 30, "Спінова поляризація σ_y", size=11, bold=True, color="#b45309", anchor="middle"))

    f.append(text(x2 + w2 / 2, y2 + h2 - 40, "Градієнт потенціалу генерує ефективне поле B_R ~ (k × E)", size=11, bold=True, color="#334155", anchor="middle"))
    f.append(text(x2 + w2 / 2, y2 + h2 - 22, "утворюючи нерівноважну спінову поляризацію на межі", size=10, color=MUTED, anchor="middle"))

    f.append(text(W / 2, H - 12, "Обидва ефекти створюють поперечну спінову поляризацію σ_y на гетеромежі", size=11, italic=True, color=MUTED, anchor="middle"))

    render(os.path.join(IMG_DIR, 'spin-hall-and-rashba.svg'), W, H, "\n".join(f))

# ── Фігура 2: Векторна геометрія обертальних моментів SOT ───────────────────
def fig_sot_torques_geometry():
    W, H = 820, 460
    f = []

    f.append(text(W / 2, 26, "Векторна геометрія обертальних моментів (DL-torque та FL-torque)", size=16, bold=True, color=INK, anchor="middle"))

    # Схема системи координат та векторів
    cx, cy = 250, 250

    # Осі координат
    f.append(arrow(cx, cy, cx + 160, cy, color="#64748b", sw=1.5))
    f.append(text(cx + 175, cy + 5, "x (струм J_c)", size=11, bold=True, color="#475569", anchor="start"))

    f.append(arrow(cx, cy, cx - 90, cy + 75, color="#64748b", sw=1.5))
    f.append(text(cx - 105, cy + 90, "y (спін σ)", size=11, bold=True, color="#475569", anchor="middle"))

    f.append(arrow(cx, cy, cx, cy - 160, color="#64748b", sw=1.5))
    f.append(text(cx, cy - 172, "z (нормаль)", size=11, bold=True, color="#475569", anchor="middle"))

    # Вектор поляризації σ (уздовж y)
    f.append(arrow(cx, cy, cx - 70, cy + 58, color="#eab308", sw=3.5))
    f.append(text(cx - 85, cy + 45, "σ (спіновий потік)", size=12, bold=True, color="#ca8a04", anchor="end"))

    # Вектор намагніченості m (похилий)
    mx, my = cx + 70, cy - 120
    f.append(arrow(cx, cy, mx, my, color="#1d4ed8", sw=4))
    f.append(text(mx + 15, my - 5, "m (намагніченість)", size=13, bold=True, color="#1d4ed8", anchor="start"))

    # Field-like torque: τ_FL ~ m × σ (перпендикулярно m і σ)
    f.append(arrow(mx, my, mx + 55, my + 65, color="#059669", sw=3))
    f.append(text(mx + 65, my + 75, "τ_FL ~ m × σ (Field-like)", size=11, bold=True, color="#059669", anchor="start"))

    # Damping-like torque: τ_DL ~ m × (m × σ) (у площині m і σ, спрямований до σ)
    f.append(arrow(mx, my, mx - 80, my + 25, color="#dc2626", sw=3.5))
    f.append(text(mx - 90, my - 10, "τ_DL ~ m × (m × σ) (Damping-like)", size=11, bold=True, color="#dc2626", anchor="end"))

    # Права інформаційна панель
    px, py, pw, ph = 490, 55, 310, 360
    f.append(rect(px, py, pw, ph, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(px + pw / 2, py + 24, "Компоненти SOT", size=13, bold=True, color="#0f172a", anchor="middle"))

    # DL-torque деталі
    f.append(rect(px + 12, py + 40, pw - 24, 140, fill="#fef2f2", stroke="#fca5a5", rx=6))
    f.append(text(px + 20, py + 62, "Damping-like torque (τ_DL):", size=11, bold=True, color="#991b1b", anchor="start"))
    f.append(text(px + 20, py + 84, "• Дія: Протидіє дисипації (Гільберту)", size=10, color="#7f1d1d", anchor="start"))
    f.append(text(px + 20, py + 102, "• Формула: τ_DL = τ_DL0 · m × (m × σ)", size=10, bold=True, color="#991b1b", anchor="start"))
    f.append(text(px + 20, py + 120, "• Джерело: Передебільшого SHE", size=10, color="#7f1d1d", anchor="start"))
    f.append(text(px + 20, py + 138, "• Роль: Відповідає за перемикання", size=10, bold=True, color="#991b1b", anchor="start"))

    # FL-torque деталі
    f.append(rect(px + 12, py + 195, pw - 24, 140, fill="#ecfdf5", stroke="#6ee7b7", rx=6))
    f.append(text(px + 20, py + 217, "Field-like torque (τ_FL):", size=11, bold=True, color="#065f46", anchor="start"))
    f.append(text(px + 20, py + 239, "• Дія: Викликає прецесію навколо σ", size=10, color="#064e3b", anchor="start"))
    f.append(text(px + 20, py + 257, "• Формула: τ_FL = τ_FL0 · (m × σ)", size=10, bold=True, color="#065f46", anchor="start"))
    f.append(text(px + 20, py + 275, "• Джерело: Передебільшого REE", size=10, color="#064e3b", anchor="start"))
    f.append(text(px + 20, py + 293, "• Роль: Знижує енергетичний бар'єр", size=10, color="#064e3b", anchor="start"))

    f.append(text(W / 2, H - 12, "Damping-like момент виштовхує намагніченість з площини та забезпечує інверсію спіна", size=11, italic=True, color=MUTED, anchor="middle"))

    render(os.path.join(IMG_DIR, 'sot-torques-geometry.svg'), W, H, "\n".join(f))

# ── Фігура 3: Детеміноване перемикання PMA з поздовжнім полем ────────────────
def fig_sot_pma_switching():
    W, H = 820, 450
    f = []

    f.append(text(W / 2, 26, "Механізм детермінованого перемикання PMA шару за допомогою похилого поля B_x", size=16, bold=True, color=INK, anchor="middle"))

    # Ліва панель: Без поля B_x (Недетермінований стан)
    x1, y1, w1, h1 = 20, 55, 380, 355
    f.append(rect(x1, y1, w1, h1, fill="#fff5f5", stroke="#fecaca", rx=8))
    f.append(text(x1 + w1 / 2, y1 + 24, "Без зовнішнього поля (B_x = 0)", size=13, bold=True, color="#991b1b", anchor="middle"))

    # Початковий стан m = +z
    f.append(arrow(x1 + 100, y1 + 180, x1 + 100, y1 + 80, color="#1d4ed8", sw=3.5))
    f.append(text(x1 + 100, y1 + 65, "Стан '0' (+z)", size=11, bold=True, color="#1d4ed8", anchor="middle"))

    # Дія SOT -> обертання в площину (m_z = 0)
    f.append(arrow(x1 + 100, y1 + 180, x1 + 190, y1 + 180, color="#dc2626", sw=3))
    f.append(text(x1 + 190, y1 + 165, "SOT (τ_DL)", size=11, bold=True, color="#dc2626", anchor="middle"))
    f.append(text(x1 + 190, y1 + 200, "m розвертається в площину (xy)", size=10, bold=True, color="#475569", anchor="middle"))

    # Симетричне розгалуження при вимкненні струму
    f.append(arrow(x1 + 260, y1 + 180, x1 + 320, y1 + 115, color="#94a3b8", sw=2))
    f.append(text(x1 + 330, y1 + 110, "+z (50%)", size=11, bold=True, color="#64748b", anchor="start"))

    f.append(arrow(x1 + 260, y1 + 180, x1 + 320, y1 + 245, color="#94a3b8", sw=2))
    f.append(text(x1 + 330, y1 + 250, "-z (50%)", size=11, bold=True, color="#64748b", anchor="start"))

    f.append(rect(x1 + 20, y1 + h1 - 65, w1 - 40, 50, fill="#fee2e2", stroke="#fca5a5", rx=4))
    f.append(text(x1 + w1 / 2, y1 + h1 - 45, "Симетрія енергетичного профілю!", size=11, bold=True, color="#991b1b", anchor="middle"))
    f.append(text(x1 + w1 / 2, y1 + h1 - 28, "Перемикання випадкове (хаотичний старт/фініш)", size=10, color="#7f1d1d", anchor="middle"))

    # Права панель: З похилим полем B_x (Детерміноване перемикання)
    x2, y2, w2, h2 = 420, 55, 380, 355
    f.append(rect(x2, y2, w2, h2, fill="#f0fdf4", stroke="#bbf7d0", rx=8))
    f.append(text(x2 + w2 / 2, y2 + 24, "З допоміжним полем B_x > 0", size=13, bold=True, color="#166534", anchor="middle"))

    # Початковий стан m = +z з невеликим нахилом від B_x
    f.append(arrow(x2 + 80, y2 + 180, x2 + 100, y2 + 80, color="#1d4ed8", sw=3.5))
    f.append(text(x2 + 90, y2 + 65, "Початковий +z", size=11, bold=True, color="#1d4ed8", anchor="middle"))

    # Зовнішнє поле B_x
    f.append(arrow(x2 + 40, y2 + 260, x2 + 140, y2 + 260, color="#9333ea", sw=3))
    f.append(text(x2 + 90, y2 + 280, "Допоміжне поле B_x", size=11, bold=True, color="#9333ea", anchor="middle"))

    # Траєкторія прецесії під дією τ_DL + B_x
    f.append(arrow(x2 + 100, y2 + 180, x2 + 210, y2 + 210, color="#dc2626", sw=3))
    f.append(text(x2 + 155, y2 + 175, "Зняття симетрії", size=10, bold=True, color="#dc2626", anchor="middle"))

    # Гарантований фінальний стан m = -z
    f.append(arrow(x2 + 240, y2 + 180, x2 + 280, y2 + 270, color="#166534", sw=4))
    f.append(text(x2 + 295, y2 + 280, "Стан '1' (-z) 100%", size=11, bold=True, color="#166534", anchor="start"))

    f.append(rect(x2 + 20, y2 + h2 - 65, w2 - 40, 50, fill="#dcfce7", stroke="#86efac", rx=4))
    f.append(text(x2 + w2 / 2, y2 + h2 - 45, "Порушення симетрії за допомогою B_x", size=11, bold=True, color="#166534", anchor="middle"))
    f.append(text(x2 + w2 / 2, y2 + h2 - 28, "Детермінована інверсія спіна за < 1 нс", size=10, color="#14532d", anchor="middle"))

    f.append(text(W / 2, H - 12, "Поле B_x надає векторний напрямок проекції торка, забезпечуючи однозначний вибір фінального стану", size=11, italic=True, color=MUTED, anchor="middle"))

    render(os.path.join(IMG_DIR, 'sot-pma-switching.svg'), W, H, "\n".join(f))

# ── Фігура 4: Тритермінальна SOT-MRAM комірка vs Двотермінальна STT-MRAM ─────
def fig_sot_3terminal_cell():
    W, H = 820, 460
    f = []

    f.append(text(W / 2, 26, "Порівняння схемотехніки STT-MRAM (2T) та SOT-MRAM (3T)", size=16, bold=True, color=INK, anchor="middle"))

    # Ліва панель: 2-термінальна STT-MRAM комірка
    x1, y1, w1, h1 = 20, 55, 380, 360
    f.append(rect(x1, y1, w1, h1, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(x1 + w1 / 2, y1 + 24, "Двотермінальна STT-MRAM комірка", size=13, bold=True, color="#0f172a", anchor="middle"))

    # Стек MTJ
    mtj_x = x1 + 130
    f.append(rect(mtj_x, y1 + 80, 120, 30, fill="#cbd5e1", stroke="#475569"))
    f.append(text(mtj_x + 60, y1 + 100, "Pinned Layer", size=10, bold=True, color="#0f172a", anchor="middle"))

    f.append(rect(mtj_x, y1 + 110, 120, 20, fill="#fef08a", stroke="#ca8a04"))
    f.append(text(mtj_x + 60, y1 + 124, "Tunnel Barrier MgO", size=9, bold=True, color="#854d0e", anchor="middle"))

    f.append(rect(mtj_x, y1 + 130, 120, 30, fill="#93c5fd", stroke="#1d4ed8"))
    f.append(text(mtj_x + 60, y1 + 150, "Free Layer", size=10, bold=True, color="#1e3a8a", anchor="middle"))

    # Струм запису та зчитування проходить через один бар'єр MgO
    f.append(arrow(mtj_x + 60, y1 + 50, mtj_x + 60, y1 + 175, color="#dc2626", sw=3))
    f.append(text(mtj_x + 130, y1 + 75, "Запис I_write", size=10, bold=True, color="#dc2626", anchor="start"))
    f.append(text(mtj_x + 130, y1 + 90, "(Високий струм!)", size=9, color="#dc2626", anchor="start"))

    f.append(arrow(mtj_x + 60, y1 + 175, mtj_x + 60, y1 + 240, color="#2563eb", sw=2))
    f.append(text(mtj_x + 130, y1 + 200, "Зчитування I_read", size=10, bold=True, color="#2563eb", anchor="start"))

    f.append(rect(x1 + 15, y1 + h1 - 85, w1 - 30, 70, fill="#fff1f2", stroke="#fecdd3", rx=6))
    f.append(text(x1 + 25, y1 + h1 - 65, "Проблеми STT:", size=11, bold=True, color="#9f1239", anchor="start"))
    f.append(text(x1 + 25, y1 + h1 - 48, "• Струм запису зношує бар'єр MgO (деградація)", size=10, color="#881337", anchor="start"))
    f.append(text(x1 + 25, y1 + h1 - 32, "• Конфлікт між швидкістю та надійністю read/write", size=10, color="#881337", anchor="start"))

    # Права панель: 3-термінальна SOT-MRAM комірка
    x2, y2, w2, h2 = 420, 55, 380, 360
    f.append(rect(x2, y2, w2, h2, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(x2 + w2 / 2, y2 + 24, "Тритермінальна SOT-MRAM комірка", size=13, bold=True, color="#0f172a", anchor="middle"))

    # Стек MTJ зверху
    mtj2_x = x2 + 130
    f.append(rect(mtj2_x, y2 + 70, 120, 25, fill="#cbd5e1", stroke="#475569"))
    f.append(text(mtj2_x + 60, y2 + 87, "Pinned Layer", size=10, bold=True, color="#0f172a", anchor="middle"))

    f.append(rect(mtj2_x, y2 + 95, 120, 15, fill="#fef08a", stroke="#ca8a04"))
    f.append(text(mtj2_x + 60, y2 + 106, "Barrier MgO", size=9, bold=True, color="#854d0e", anchor="middle"))

    f.append(rect(mtj2_x, y2 + 110, 120, 25, fill="#93c5fd", stroke="#1d4ed8"))
    f.append(text(mtj2_x + 60, y2 + 127, "Free Layer", size=10, bold=True, color="#1e3a8a", anchor="middle"))

    # Важкий метал трек знизу (HM channel)
    hm_track_y = y2 + 135
    f.append(rect(x2 + 40, hm_track_y, 300, 25, fill="#fed7aa", stroke="#ea580c"))
    f.append(text(x2 + 190, hm_track_y + 16, "HM Шлях (Pt / W / Ta)", size=10, bold=True, color="#9a3412", anchor="middle"))

    # Термінали
    # Terminal 1 (Write L)
    f.append(circle(x2 + 50, hm_track_y + 12, 6, fill="#ea580c", stroke="none"))
    f.append(text(x2 + 50, hm_track_y + 40, "T1 (Write 1)", size=9, bold=True, color="#ea580c", anchor="middle"))

    # Terminal 2 (Write R)
    f.append(circle(x2 + 330, hm_track_y + 12, 6, fill="#ea580c", stroke="none"))
    f.append(text(x2 + 330, hm_track_y + 40, "T2 (Write 2)", size=9, bold=True, color="#ea580c", anchor="middle"))

    # Terminal 3 (Read Top)
    f.append(circle(mtj2_x + 140, y2 + 70, 6, fill="#2563eb", stroke="none"))
    f.append(text(mtj2_x + 140, y2 + 55, "T3 (Read)", size=9, bold=True, color="#2563eb", anchor="middle"))

    # Шляхи струмів
    # Запис (горизонтальний у HM)
    f.append(arrow(x2 + 65, hm_track_y + 12, x2 + 315, hm_track_y + 12, color="#dc2626", sw=3))
    f.append(text(x2 + 190, hm_track_y - 8, "I_write (не проходить через MgO!)", size=10, bold=True, color="#dc2626", anchor="middle"))

    # Зчитування (вертикальне через MTJ, по правому краю)
    f.append(arrow(mtj2_x + 140, y2 + 70, mtj2_x + 140, hm_track_y + 12, color="#2563eb", sw=2))

    f.append(rect(x2 + 15, y2 + h2 - 85, w2 - 30, 70, fill="#f0fdf4", stroke="#bbf7d0", rx=6))
    f.append(text(x2 + 25, y2 + h1 - 65, "Переваги SOT:", size=11, bold=True, color="#166534", anchor="start"))
    f.append(text(x2 + 25, y2 + h1 - 48, "• Розділені канали: MgO захищений від руйнування", size=10, color="#14532d", anchor="start"))
    f.append(text(x2 + 25, y2 + h1 - 32, "• Запис < 1 нс, ресурсоємність > 10¹⁵ циклів", size=10, color="#14532d", anchor="start"))

    f.append(text(W / 2, H - 12, "Розділення шляхів читання і запису вирішує фундаментальну проблему надійності MRAM", size=11, italic=True, color=MUTED, anchor="middle"))

    render(os.path.join(IMG_DIR, 'sot-3terminal-cell.svg'), W, H, "\n".join(f))


if __name__ == '__main__':
    fig_spin_hall_and_rashba()
    fig_sot_torques_geometry()
    fig_sot_pma_switching()
    fig_sot_3terminal_cell()
    print("Всі фігури успішно згенеровані у ./img/")
