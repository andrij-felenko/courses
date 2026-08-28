#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми rizba-pid-vibratsiieiu.
Вивід у ./img/
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_junker_transverse_slip():
    """Фігура 1: Механіка Юнкера — поперечний зсув ліквідує тангенційне тертя."""
    w, h = 820, 360
    frags = []
    
    # Фон
    frags.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Ліва колонка: Статичний стан (самогальмування)
    frags.append(rect(20, 20, 375, 315, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(207, 48, "Статичний стан: самогальмування", size=13, color=INK, bold=True))
    
    # Похила площина різьби (кут бета)
    p_pts = "60,240 340,160 340,255 60,255"
    frags.append('<polygon points="%s" fill="#e2e8f0" stroke="%s" stroke-width="1.5"/>' % (p_pts, LINE))
    frags.append(text(120, 235, "Кут підйому різьби β ≈ 2.5°–3.5°", size=10, color=MUTED))
    
    # Тіло (виток гайки) на похилій площині
    frags.append(rect(145, 155, 110, 50, fill="#ffffff", stroke=LINE, sw=1.8, rx=4))
    frags.append(text(200, 184, "Виток гайки", size=11, color=INK, bold=True))
    
    # Сили: Затяжка (F_p) вниз
    frags.append(arrow(200, 155, 200, 95, color=NEG, sw=2))
    frags.append(text(200, 85, "Осьовий натяг F_p", size=11, color=NEG, bold=True))
    
    # Складова скочування (F_p * sin β) вниз по похилій
    frags.append(arrow(155, 185, 105, 200, color=POS, sw=2))
    frags.append(text(120, 175, "F_unwind", size=10, color=POS, bold=True))
    
    # Сила тертя спокою (F_f = μ * N) вгору по похилій
    frags.append(arrow(245, 160, 305, 142, color=FIELD, sw=2.2))
    frags.append(text(285, 130, "Тертя F_friction = μ · N", size=10, color=FIELD, bold=True))
    
    # Пояснення під лівою схемою
    frags.append(text(207, 280, "F_friction > F_unwind (tg ρ' > tg β)", size=11, color=FIELD, bold=True))
    frags.append(text(207, 302, "Сила тертя надійно блокує відкручування", size=10, color=MUTED))
    
    # Права колонка: Знакозмінний поперечний зсув (Теорія Юнкера)
    frags.append(rect(425, 20, 375, 315, fill="#fff7ed", stroke="#ea580c", sw=1.5, rx=8))
    frags.append(text(612, 48, "Поперечна вібрація: ефект Юнкера", size=13, color="#9a3412", bold=True))
    
    # Схема поперечного руху
    frags.append(rect(465, 80, 295, 140, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    
    # Поперечні стрілки сили зсуву (F_transverse)
    frags.append(arrow(490, 150, 440, 150, color=POS, sw=2.2))
    frags.append(arrow(735, 150, 785, 150, color=POS, sw=2.2))
    frags.append(text(612, 100, "Циклічний зсув стику ±F_transverse", size=11, color=POS, bold=True))
    
    # Векторне коло тертя
    frags.append(circle(612, 160, 32, fill="#fed7aa", stroke="#ea580c", sw=1.5))
    frags.append(arrow(612, 160, 612, 130, color="#c2410c", sw=2))
    frags.append(text(612, 122, "v_transverse (кінетичне тертя)", size=10, color="#9a3412", bold=True))
    
    # Залишкова сила опору в тангенційному напрямку прямує до нуля
    frags.append(arrow(612, 160, 560, 160, color=POS, sw=2))
    frags.append(text(545, 152, "F_unwind", size=10, color=POS, bold=True))
    frags.append(text(670, 165, "Тертя по колу → 0", size=10, color=POS, bold=True))
    
    # Пояснення під правою схемою
    frags.append(text(612, 248, "Ковзання впоперек вичерпує силу тертя Кулона", size=11, color=INK, bold=True))
    frags.append(text(612, 272, "Постійна сила пружного розкручування F_unwind", size=10, color=MUTED))
    frags.append(text(612, 292, "повертає різьбу на мікрокути в кожному циклі", size=10, color=MUTED))
    frags.append(text(612, 314, "Результат: лавиноподібна втрата натягу (Preload Loss)", size=10, color=POS, bold=True))
    
    render(os.path.join(IMG_DIR, 'junker-transverse-slip.svg'), w, h, *frags)
    print("Generated junker-transverse-slip.svg")


def fig_preload_decay_curve():
    """Фігура 2: Криві Юнкера — динаміка падіння сили затяжки під вібрацією."""
    w, h = 820, 360
    frags = []
    
    frags.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Рамка графіка
    gx, gy, gw, gh = 85, 45, 480, 255
    frags.append(rect(gx, gy, gw, gh, fill="#fafafa", stroke=LINE, sw=1.2, rx=0))
    
    # Горизонтальні лінії сітки (25%, 50%, 75%, 100%)
    for pct in [25, 50, 75, 100]:
        y_pos = gy + gh - (pct / 100.0) * gh
        frags.append(line(gx, y_pos, gx + gw, y_pos, color="#e5e7eb", sw=1, dash="4,4"))
        frags.append(text(gx - 10, y_pos + 4, f"{pct}%", size=10, color=MUTED, anchor="end"))
    frags.append(text(gx - 10, gy + gh + 4, "0%", size=10, color=MUTED, anchor="end"))
    
    # Вертикальні лінії сітки (цикли 0, 300, 600, 900, 1200, 1500)
    for c in [300, 600, 900, 1200, 1500]:
        x_pos = gx + (c / 1500.0) * gw
        frags.append(line(x_pos, gy, x_pos, gy + gh, color="#e5e7eb", sw=1, dash="4,4"))
        frags.append(text(x_pos, gy + gh + 18, f"{c}", size=10, color=MUTED, anchor="middle"))
    frags.append(text(gx, gy + gh + 18, "0", size=10, color=MUTED, anchor="middle"))
    
    # Підписи осей
    frags.append(text(gx + gw / 2, gy + gh + 38, "Кількість циклів поперечної вібрації (Junker Test DIN 65151)", size=11, color=INK, bold=True))
    frags.append(text(gx - 45, gy + gh / 2, "Залишковий натяг F_p / F_0", size=11, color=INK, bold=True, anchor="middle"))
    
    # Крива 1: Звичайний болт/гайка без фіксації (падає за 100-200 циклів)
    pts_std = [
        (0, 100), (50, 75), (100, 35), (150, 10), (220, 0), (1500, 0)
    ]
    p_std_svg = " ".join(f"{gx + (c/1500.0)*gw:.1f},{gy + gh - (p/100.0)*gh:.1f}" for c, p in pts_std)
    frags.append(f'<polyline points="{p_std_svg}" fill="none" stroke="{POS}" stroke-width="2.6"/>')
    
    # Крива 2: Шайба Гровера DIN 127 (падає майже так само швидко, 200-300 циклів)
    pts_grover = [
        (0, 100), (60, 80), (120, 48), (200, 15), (300, 0), (1500, 0)
    ]
    p_grover_svg = " ".join(f"{gx + (c/1500.0)*gw:.1f},{gy + gh - (p/100.0)*gh:.1f}" for c, p in pts_grover)
    frags.append(f'<polyline points="{p_grover_svg}" fill="none" stroke="#d97706" stroke-width="2.2" stroke-dasharray="6,3"/>')
    
    # Крива 3: Гайка з нейлоном Nyloc DIN 985 (натяг падає до 0 за 500-700 циклів, гайка не спадає)
    pts_nyloc = [
        (0, 100), (100, 85), (250, 50), (450, 18), (650, 0), (1500, 0)
    ]
    p_nyloc_svg = " ".join(f"{gx + (c/1500.0)*gw:.1f},{gy + gh - (p/100.0)*gh:.1f}" for c, p in pts_nyloc)
    frags.append(f'<polyline points="{p_nyloc_svg}" fill="none" stroke="#2563eb" stroke-width="2.4"/>')
    
    # Крива 4: Синій фіксатор різьби Loctite 243 (зберігає 85% натягу після початкової релаксації)
    pts_loctite = [
        (0, 100), (50, 92), (150, 88), (400, 86), (800, 85), (1500, 84)
    ]
    p_loctite_svg = " ".join(f"{gx + (c/1500.0)*gw:.1f},{gy + gh - (p/100.0)*gh:.1f}" for c, p in pts_loctite)
    frags.append(f'<polyline points="{p_loctite_svg}" fill="none" stroke="#0891b2" stroke-width="2.6"/>')
    
    # Крива 5: Клинові шайби Nord-Lock (зберігає 92-95% натягу стабільно)
    pts_nord = [
        (0, 100), (40, 95), (120, 93), (400, 93), (1000, 92), (1500, 92)
    ]
    p_nord_svg = " ".join(f"{gx + (c/1500.0)*gw:.1f},{gy + gh - (p/100.0)*gh:.1f}" for c, p in pts_nord)
    frags.append(f'<polyline points="{p_nord_svg}" fill="none" stroke="{FIELD}" stroke-width="3"/>')
    
    # Права панель: Легенда та висновки
    lx, ly = 590, 45
    frags.append(rect(lx, ly, 210, 275, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(lx + 105, ly + 25, "Методи фіксації", size=12, color=INK, bold=True))
    
    # Елементи легенди
    items = [
        ("Клинові шайби Nord-Lock", FIELD, "3", "none", "Стабільний натяг ~92%"),
        ("Loctite 243 (синій анаероб)", "#0891b2", "2.6", "none", "Хім. полімер ~85%"),
        ("Гайка Nyloc (DIN 985)", "#2563eb", "2.4", "none", "Втрата натягу (без спадання)"),
        ("Шайба Гровера (DIN 127)", "#d97706", "2.2", "6,3", "Неефективна проти зсуву"),
        ("Стандартний болт без замка", POS, "2.6", "none", "Повне розкручування (<200 ц)")
    ]
    
    cur_y = ly + 50
    for title, col, sw_val, d_val, note in items:
        dash_attr = f' stroke-dasharray="{d_val}"' if d_val != "none" else ""
        frags.append(f'<line x1="{lx+12}" y1="{cur_y}" x2="{lx+42}" y2="{cur_y}" stroke="{col}" stroke-width="{sw_val}"{dash_attr}/>')
        frags.append(text(lx + 48, cur_y + 4, title, size=10, color=INK, anchor="start", bold=True))
        frags.append(text(lx + 48, cur_y + 17, note, size=9, color=MUTED, anchor="start"))
        cur_y += 42
        
    render(os.path.join(IMG_DIR, 'preload-decay-curve.svg'), w, h, *frags)
    print("Generated preload-decay-curve.svg")


def fig_nord_lock_wedge_cam():
    """Фігура 3: Геометрія клинової шайби Nord-Lock (α > β)."""
    w, h = 820, 320
    frags = []
    
    frags.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Лівий блок: Схема клинового розпирання пари шайб
    frags.append(rect(20, 20, 420, 275, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(230, 48, "Клиновий ефект Nord-Lock: кут α > кут β", size=13, color=INK, bold=True))
    
    # Головка болта / гайка вгорі
    frags.append(rect(60, 75, 340, 30, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=2))
    frags.append(text(230, 95, "Головка болта (радіальні насічки зчіплюються з шайбою)", size=10, color=INK))
    
    # Верхня шайба пари (з клинами вниз)
    frags.append('<polygon points="60,110 400,110 400,140 315,155 230,140 145,155 60,140" fill="#bfdbfe" stroke="#1d4ed8" stroke-width="1.8"/>')
    frags.append(text(230, 130, "Верхня шайба: клинові скоси під кутом α", size=10, color="#1e40af", bold=True))
    
    # Нижня шайба пари (з клинами вгору)
    frags.append('<polygon points="60,158 145,173 230,158 315,173 400,158 400,188 60,188" fill="#bfdbfe" stroke="#1d4ed8" stroke-width="1.8"/>')
    frags.append(text(230, 180, "Нижня шайба: клинові скоси під кутом α", size=10, color="#1e40af", bold=True))
    
    # Опорна деталь внизу (корпус/рама)
    frags.append(rect(60, 193, 340, 30, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=2))
    frags.append(text(230, 213, "Скріплювана деталь (насічки врізаються в метал)", size=10, color=INK))
    
    # Стрілки клинового розтискання
    frags.append(arrow(100, 150, 70, 150, color=POS, sw=2))
    frags.append(text(105, 145, "Спроба відкручування", size=9, color=POS, bold=True, anchor="start"))
    frags.append(arrow(230, 145, 230, 115, color=FIELD, sw=2.5))
    frags.append(arrow(230, 168, 230, 198, color=FIELD, sw=2.5))
    frags.append(text(230, 245, "Осьове видовження болта: ΔL_cam = r · tg α · Δθ", size=10, color=FIELD, bold=True))
    frags.append(text(230, 265, "Підйом різьби: ΔL_thread = r · tg β · Δθ", size=10, color=MUTED))
    frags.append(text(230, 282, "Оскільки α > β, натяг F_p зростає — обертання стопориться!", size=10, color=FIELD, bold=True))
    
    # Правий блок: Порівняння кутів та насічок
    frags.append(rect(460, 20, 340, 275, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(630, 48, "Чому клиновий замок непереможний", size=13, color=INK, bold=True))
    
    # Пункти розбору
    box1 = fitbox(475, 70, 310, 58, "1. Зовнішні радіальні насічки:\nТвердість шайби (HRC 46–48) вища за болт.\nНасічки чіпляються за метал — ковзання лише по клинах.", size=10, color=INK)
    frags.append(box1)
    
    box2 = fitbox(475, 138, 310, 58, "2. Кутова умова блокування:\nКут клина α = 13°...15°\nКут підйому різьби β = 2.5°...3.5°\nСпіввідношення: tg(α) > tg(β) у 4–5 разів!", size=10, color="#1e40af")
    frags.append(box2)
    
    box3 = fitbox(475, 206, 310, 75, "3. Динамічний відгук на вібрацію:\nБудь-який імпульс на відкручування миттєво\nпіднімає силу затягування (клиновий бар'єр).\nРозбирання можливе лише гайковим ключем.", size=10, color=FIELD)
    frags.append(box3)
    
    render(os.path.join(IMG_DIR, 'nord-lock-wedge-cam.svg'), w, h, *frags)
    print("Generated nord-lock-wedge-cam.svg")


def fig_carbon_aluminum_joint_stress():
    """Фігура 4: Розподіл тиску під фланцем у карбоні та довжина різьби в алюмінії."""
    w, h = 820, 340
    frags = []
    
    frags.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Ліва половина: Карбон (тиск під вузькою головкою проти широкої шайби)
    frags.append(rect(20, 20, 375, 300, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(207, 45, "Затискання карбону (CFRP): зминання матриці", size=12, color=INK, bold=True))
    
    # Схема 1: Вузька головка DIN 912 (руйнування смоли)
    frags.append(rect(40, 65, 155, 150, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(117, 85, "Вузька головка M3 (d=5.5mm)", size=9, color=POS, bold=True))
    # Карбонова пластина
    frags.append(rect(50, 125, 135, 30, fill="#374151", stroke="#111827", sw=1.2, rx=1))
    frags.append(text(117, 142, "Карбон 2.5 мм", size=9, color="#f9fafb"))
    # Головка болта
    frags.append(rect(92, 100, 50, 25, fill="#9ca3af", stroke=LINE, sw=1.2, rx=1))
    # Піковий тиск
    frags.append(arrow(117, 95, 117, 123, color=POS, sw=2))
    frags.append(text(117, 175, "Тиск σ > 220 МПа", size=9, color=POS, bold=True))
    frags.append(text(117, 192, "Роздавлювання смоли!", size=9, color=POS))
    frags.append(text(117, 205, "Мікророзшарування", size=9, color=MUTED))
    
    # Схема 2: Широка шайба DIN 9021 / фланець (захист матриці)
    frags.append(rect(215, 65, 165, 150, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(297, 85, "Фланець/шайба (d=9.0mm)", size=9, color=FIELD, bold=True))
    # Карбонова пластина
    frags.append(rect(225, 130, 145, 30, fill="#374151", stroke="#111827", sw=1.2, rx=1))
    frags.append(text(297, 147, "Карбон 2.5 мм", size=9, color="#f9fafb"))
    # Шайба
    frags.append(rect(252, 122, 90, 8, fill="#d1d5db", stroke=LINE, sw=1.2, rx=1))
    # Головка
    frags.append(rect(272, 100, 50, 22, fill="#9ca3af", stroke=LINE, sw=1.2, rx=1))
    # Рівномірний тиск
    frags.append(arrow(297, 95, 297, 120, color=FIELD, sw=2))
    frags.append(text(297, 175, "Тиск σ ≈ 65 МПа", size=9, color=FIELD, bold=True))
    frags.append(text(297, 192, "Безпечно для епоксиду", size=9, color=FIELD))
    frags.append(text(297, 205, "Стабільний натяг без повзучості", size=9, color=MUTED))
    
    frags.append(text(207, 240, "Правило для карбону:", size=10, color=INK, bold=True))
    frags.append(text(207, 260, "Допустимий тиск стиску поперек шарів σ_adm ≤ 120–150 МПа", size=9, color=MUTED))
    frags.append(text(207, 280, "Площа контакту збільшується у 2.5–3 рази → ризик повзучості усунуто", size=9, color=MUTED))
    frags.append(text(207, 300, "Обов'язкові шайби з фаскою або гвинти ISO 7380-2 з фланцем", size=9, color=FIELD, bold=True))
    
    # Права половина: Алюміній (довжина зачеплення і вставки Helicoil)
    frags.append(rect(415, 20, 385, 300, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(607, 45, "Різьба в алюмінії: зріз витків проти вставки", size=12, color=INK, bold=True))
    
    # Схема 3: Коротка різьба в 6061-T6 (зріз)
    frags.append(rect(430, 65, 165, 150, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(512, 85, "Пряма різьба L = 1.0·d (3 мм)", size=9, color=POS, bold=True))
    frags.append(rect(445, 115, 135, 45, fill="#cbd5e1", stroke=LINE, sw=1.2, rx=2))
    frags.append(text(512, 138, "Алюміній 6061-T6", size=9, color=INK))
    frags.append(text(512, 175, "Зріз алюмінієвих витків!", size=9, color=POS, bold=True))
    frags.append(text(512, 192, "τ_shear > 150 МПа при затяжці", size=9, color=POS))
    frags.append(text(512, 205, "Сталевий болт вириває різьбу", size=9, color=MUTED))
    
    # Схема 4: Вставка Helicoil / Глибоке зачеплення L = 2.0·d
    frags.append(rect(615, 65, 170, 150, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(700, 85, "Вставка Helicoil або L ≥ 2·d", size=9, color=FIELD, bold=True))
    frags.append(rect(630, 110, 140, 55, fill="#cbd5e1", stroke=LINE, sw=1.2, rx=2))
    frags.append(text(700, 125, "Алюміній 6061-T6", size=9, color=INK))
    frags.append(rect(670, 110, 60, 55, fill="#93c5fd", stroke="#1d4ed8", sw=1.2, rx=1))
    frags.append(text(700, 145, "Нерж. вставка", size=9, color="#1e40af", bold=True))
    frags.append(text(700, 175, "Діаметр зрізу більший на 30%", size=9, color=FIELD, bold=True))
    frags.append(text(700, 192, "Повний натяг болта класу 8.8/10.9", size=9, color=FIELD))
    frags.append(text(700, 205, "Багаторазове загвинчування", size=9, color=MUTED))
    
    frags.append(text(607, 240, "Правило для м'яких сплавів (6061/6082):", size=10, color=INK, bold=True))
    frags.append(text(607, 260, "Мінімальна довжина прямої різьби: L_eff ≥ 1.8...2.2 · d (для M3 ≥ 6 мм)", size=9, color=MUTED))
    frags.append(text(607, 280, "Для високонавантажених точок (мотори, стійки) — різьбові гільзи Helicoil", size=9, color=FIELD, bold=True))
    frags.append(text(607, 300, "Зниження моменту затягування на 30–40% при прямій різьбі в 6061", size=9, color=MUTED))
    
    render(os.path.join(IMG_DIR, 'carbon-aluminum-joint-stress.svg'), w, h, *frags)
    print("Generated carbon-aluminum-joint-stress.svg")


def main():
    fig_junker_transverse_slip()
    fig_preload_decay_curve()
    fig_nord_lock_wedge_cam()
    fig_carbon_aluminum_joint_stress()
    print("All figures generated successfully.")


if __name__ == '__main__':
    main()
