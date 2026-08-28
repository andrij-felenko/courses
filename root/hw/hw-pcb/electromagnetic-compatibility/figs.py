# -*- coding: utf-8 -*-
"""Фігури до теми «Електромагнітна сумісність: джерело, шлях, жертва».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Тріада ЕМС: Джерело — Шлях зв'язку — Жертва ───────────────────────────
def fig_source_path_victim():
    W, H = 760, 260
    p = []
    p.append(text(W / 2, 25, "Тріада електромагнітної сумісності (EMC Triad)", size=16, bold=True))

    # Джерело
    x1, y1, bw, bh = 40, 60, 190, 140
    p.append(rect(x1, y1, bw, bh, fill="#fdf2f2", stroke=POS, sw=2, rx=8))
    p.append(text(x1 + bw / 2, y1 + 25, "ДЖЕРЕЛО ЗАВАДИ", size=13, bold=True, color=POS))
    p.append(text(x1 + bw / 2, y1 + 45, "(Noise Source / Aggressor)", size=10, color=MUTED, italic=True))
    p.append(line(x1 + 15, y1 + 55, x1 + bw - 15, y1 + 55, color="#f0d0d0", sw=1))
    p.append(text(x1 + bw / 2, y1 + 75, "• Ключі DC-DC (dV/dt, dI/dt)", size=10, color=INK))
    p.append(text(x1 + bw / 2, y1 + 95, "• Тактові генератори, MCU", size=10, color=INK))
    p.append(text(x1 + bw / 2, y1 + 115, "• Реле, іскри, ESD-розряди", size=10, color=INK))

    # Жертва
    x3, y3 = 530, 60
    p.append(rect(x3, y3, bw, bh, fill="#f0f5ff", stroke=NEG, sw=2, rx=8))
    p.append(text(x3 + bw / 2, y3 + 25, "ЖЕРТВА ЗАВАДИ", size=13, bold=True, color=NEG))
    p.append(text(x3 + bw / 2, y3 + 45, "(Susceptible Device / Victim)", size=10, color=MUTED, italic=True))
    p.append(line(x3 + 15, y3 + 55, x3 + bw - 15, y3 + 55, color="#d0e0ff", sw=1))
    p.append(text(x3 + bw / 2, y3 + 75, "• Аналогові АЦП, сенсори", size=10, color=INK))
    p.append(text(x3 + bw / 2, y3 + 95, "• Лінії скидання (Reset), NMI", size=10, color=INK))
    p.append(text(x3 + bw / 2, y3 + 115, "• Радіотракти (LNA, антени)", size=10, color=INK))

    # Шлях зв'язку (центральний блок)
    x2, y2, w2, h2 = 255, 50, 250, 160
    p.append(rect(x2, y2, w2, h2, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(x2 + w2 / 2, y2 + 22, "ШЛЯХ ПЕРЕДАЧІ (Coupling Path)", size=12, bold=True, color=INK))
    p.append(line(x2 + 15, y2 + 32, x2 + w2 - 15, y2 + 32, color="#e0e0e0", sw=1))

    # 4 механізми
    paths = [
        ("1. Кондуктивний", "спільний імпеданс Z_GND, живлення"),
        ("2. Ємнісний", "електричне поле, струм C_M · dV/dt"),
        ("3. Індуктивний", "магнітне поле, напруга M · dI/dt"),
        ("4. Випромінювальний", "антени-петлі, хвилі в просторі")
    ]
    for i, (title_p, desc_p) in enumerate(paths):
        yy = y2 + 50 + i * 26
        p.append(text(x2 + 15, yy, title_p, size=11, bold=True, color=FIELD, anchor="start"))
        p.append(text(x2 + 115, yy, desc_p, size=9, color=MUTED, anchor="start"))

    # Стрілки з'єднання
    p.append(arrow(x1 + bw + 2, y1 + 70, x2 - 2, y1 + 70, color=POS, sw=2))
    p.append(arrow(x2 + w2 + 2, y1 + 70, x3 - 2, y1 + 70, color=NEG, sw=2))

    # Нижній висновок
    p.append(text(W / 2, 235, "Розрив або пригнічення будь-якої з 3 ланок повністю ліквідує проблему ЕМС", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG, "source-path-victim.svg"), W, H, *p)


# ── 2. Чотири фізичні шляхи передачі завади ─────────────────────────────────
def fig_four_coupling_paths():
    W, H = 780, 380
    p = []
    p.append(text(W / 2, 24, "Чотири фізичні шляхи електромагнітного зв'язку", size=16, bold=True))

    pw, ph = 360, 150
    # Панель 1: Кондуктивний зв'язок (ліворуч зверху)
    x1, y1 = 20, 45
    p.append(rect(x1, y1, pw, ph, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(text(x1 + pw / 2, y1 + 20, "1. Кондуктивний (спільний імпеданс)", size=12, bold=True, color=POS))
    p.append(line(x1 + 40, y1 + 50, x1 + 150, y1 + 50, color=POS, sw=2.5))
    p.append(text(x1 + 35, y1 + 53, "Агресор", size=9, color=POS, anchor="end"))
    p.append(line(x1 + 40, y1 + 80, x1 + 150, y1 + 80, color=NEG, sw=2.5))
    p.append(text(x1 + 35, y1 + 83, "Жертва", size=9, color=NEG, anchor="end"))
    # спільний провідник землі
    p.append(rect(x1 + 150, y1 + 55, 120, 20, fill="#e8ecf1", stroke="#778899", sw=1.5))
    p.append(text(x1 + 210, y1 + 69, "Z_спільне (R + jwL)", size=9, bold=True, color=INK))
    p.append(arrow(x1 + 70, y1 + 42, x1 + 130, y1 + 42, color=POS, sw=1.5))
    p.append(text(x1 + 100, y1 + 38, "I_агресора", size=9, color=POS))
    p.append(text(x1 + pw / 2, y1 + 110, "ΔV_землі = I_агресора · Z_спільне", size=11, bold=True, color=POS))
    p.append(text(x1 + pw / 2, y1 + 130, "Зворотний струм спотворює опорний нуль жертви", size=9, color=MUTED))

    # Панель 2: Ємнісний зв'язок (праворуч зверху)
    x2, y2 = 400, 45
    p.append(rect(x2, y2, pw, ph, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(text(x2 + pw / 2, y2 + 20, "2. Ємнісний (електричне поле E)", size=12, bold=True, color=POS))
    p.append(line(x2 + 40, y2 + 50, x2 + 320, y2 + 50, color=POS, sw=3))
    p.append(text(x2 + 35, y2 + 53, "V1(t)", size=10, bold=True, color=POS, anchor="end"))
    p.append(line(x2 + 40, y2 + 95, x2 + 320, y2 + 95, color=NEG, sw=3))
    p.append(text(x2 + 35, y2 + 98, "V2(t)", size=10, bold=True, color=NEG, anchor="end"))
    # конденсатор C_M
    cx = x2 + 180
    p.append(line(cx, y2 + 50, cx, y2 + 67, color=MUTED, sw=1.5))
    p.append(line(cx - 12, y2 + 67, cx + 12, y2 + 67, color=MUTED, sw=2))
    p.append(line(cx - 12, y2 + 77, cx + 12, y2 + 77, color=MUTED, sw=2))
    p.append(line(cx, y2 + 77, cx, y2 + 95, color=MUTED, sw=1.5))
    p.append(text(cx + 25, y2 + 75, "C_M", size=10, bold=True, color=MUTED))
    p.append(text(x2 + pw / 2, y2 + 118, "i_наведення = C_M · (dV1 / dt)", size=11, bold=True, color=POS))
    p.append(text(x2 + pw / 2, y2 + 135, "Швидкий перепад напруги впорскує струм у сусідню лінію", size=9, color=MUTED))

    # Панель 3: Індуктивний зв'язок (ліворуч знизу)
    x3, y3 = 20, 210
    p.append(rect(x3, y3, pw, ph, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(text(x3 + pw / 2, y3 + 20, "3. Індуктивний (магнітне поле B)", size=12, bold=True, color=NEG))
    # контур 1 зі струмом
    p.append(rect(x3 + 40, y3 + 45, 100, 45, fill="none", stroke=POS, sw=2, rx=4))
    p.append(arrow(x3 + 70, y3 + 45, x3 + 110, y3 + 45, color=POS, sw=1.5))
    p.append(text(x3 + 90, y3 + 68, "Контур 1 (I1)", size=9, bold=True, color=POS))
    # магнітні лінії B
    p.append('<circle cx="%d" cy="%d" r="14" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3 3"/>' % (x3 + 180, y3 + 68, FIELD))
    p.append(text(x3 + 180, y3 + 72, "Φ", size=11, bold=True, color=FIELD))
    # контур 2 жертва
    p.append(rect(x3 + 220, y3 + 45, 100, 45, fill="none", stroke=NEG, sw=2, rx=4))
    p.append(text(x3 + 270, y3 + 68, "Контур 2", size=9, bold=True, color=NEG))
    p.append(text(x3 + pw / 2, y3 + 114, "V_наведення = - M · (dI1 / dt)", size=11, bold=True, color=NEG))
    p.append(text(x3 + pw / 2, y3 + 133, "Змінний магнітний потік прошиває контур жертви", size=9, color=MUTED))

    # Панель 4: Випромінювальний зв'язок (праворуч знизу)
    x4, y4 = 400, 210
    p.append(rect(x4, y4, pw, ph, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(text(x4 + pw / 2, y4 + 20, "4. Випромінювальний (дальнє поле EM)", size=12, bold=True, color=FIELD))
    # антена-джерело
    p.append(line(x4 + 60, y4 + 45, x4 + 60, y4 + 95, color=POS, sw=3))
    p.append(text(x4 + 60, y4 + 107, "Кабель / петля", size=9, color=POS))
    # хвилі
    for r_arc in (30, 55, 80):
        p.append('<path d="M %d %d A %d %d 0 0 1 %d %d" fill="none" stroke="%s" stroke-width="1.5"/>'
                 % (x4 + 90, y4 + 70 - r_arc, r_arc, r_arc, x4 + 90, y4 + 70 + r_arc, FIELD))
    p.append(text(x4 + 160, y4 + 65, "E, H (Z0 = 377 Ω)", size=9, color=FIELD, italic=True))
    # антена-жертва
    p.append(line(x4 + 300, y4 + 45, x4 + 300, y4 + 95, color=NEG, sw=3))
    p.append(text(x4 + 300, y4 + 107, "Провідник-жертва", size=9, color=NEG))
    p.append(text(x4 + pw / 2, y4 + 120, "E_field ∝ (f · I_CM · L) / r", size=11, bold=True, color=FIELD))
    p.append(text(x4 + pw / 2, y4 + 136, "Хвиля у вільному просторі діє на великих відстанях", size=9, color=MUTED))

    render(os.path.join(IMG, "four-coupling-paths.svg"), W, H, *p)


# ── 3. Трасування зворотного струму та розрізи землі ─────────────────────────
def fig_return_path_split():
    W, H = 780, 320
    p = []
    p.append(text(W / 2, 24, "Трасування зворотного струму високої частоти", size=16, bold=True))

    pw, ph = 360, 260
    # Ліва панель: Суцільний полігон землі (ідеально)
    x1, y1 = 20, 45
    p.append(rect(x1, y1, pw, ph, fill="#f9fcf9", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(x1 + pw / 2, y1 + 22, "Суцільна площина землі (Continuous GND)", size=12, bold=True, color=FIELD))

    # Площина GND (фоновий прямокутник)
    gx1, gy1, gw, gh = x1 + 30, y1 + 50, 300, 130
    p.append(rect(gx1, gy1, gw, gh, fill="#e8f5e9", stroke="#81c784", sw=1.5, rx=4))
    p.append(text(gx1 + 10, gy1 + 18, "GND полігон", size=9, color=FIELD, anchor="start"))

    # Сигнальна лінія (верхній шар)
    sy = gy1 + 65
    p.append(line(gx1 + 20, sy, gx1 + gw - 20, sy, color=POS, sw=3))
    p.append(arrow(gx1 + 50, sy - 8, gx1 + 120, sy - 8, color=POS, sw=1.5))
    p.append(text(gx1 + 85, sy - 14, "I_signal (прямий)", size=9, color=POS))

    # Зворотний струм (під доріжкою)
    p.append(line(gx1 + 20, sy + 15, gx1 + gw - 20, sy + 15, color=NEG, sw=3, dash="4 3"))
    p.append(arrow(gx1 + 120, sy + 25, gx1 + 50, sy + 25, color=NEG, sw=1.5))
    p.append(text(gx1 + 85, sy + 38, "I_return (під сигналом)", size=9, color=NEG))

    p.append(text(x1 + pw / 2, y1 + 195, "✓ Мінімальна площа контуру (Loop Area → min)", size=10, bold=True, color=FIELD))
    p.append(text(x1 + pw / 2, y1 + 215, "✓ Паразитна індуктивність L_loop мінімальна", size=10, color=INK))
    p.append(text(x1 + pw / 2, y1 + 235, "✓ Електромагнітне випромінювання відсутнє", size=10, color=INK))

    # Права панель: Розріз у землі (катастрофа ЕМС)
    x2, y2 = 400, 45
    p.append(rect(x2, y2, pw, ph, fill="#fff9f9", stroke=POS, sw=1.5, rx=6))
    p.append(text(x2 + pw / 2, y2 + 22, "Розріз землі під швидкою трасою (Split GND)", size=12, bold=True, color=POS))

    # Площина GND з розрізом
    gx2, gy2 = x2 + 30, y1 + 50
    # ліва половина землі
    p.append(rect(gx2, gy2, 130, gh, fill="#ffebee", stroke="#e57373", sw=1.5, rx=4))
    # права половина землі
    p.append(rect(gx2 + 170, gy2, 130, gh, fill="#ffebee", stroke="#e57373", sw=1.5, rx=4))
    # щілина
    p.append(text(gx2 + 150, gy2 + 25, "РОЗРІЗ", size=9, bold=True, color=POS))
    p.append(text(gx2 + 150, gy2 + 40, "(Щілина)", size=9, color=MUTED))

    # Сигнальна лінія над розрізом
    p.append(line(gx2 + 20, sy, gx2 + gw - 20, sy, color=POS, sw=3))
    p.append(arrow(gx2 + 40, sy - 8, gx2 + 100, sy - 8, color=POS, sw=1.5))
    p.append(text(gx2 + 70, sy - 14, "I_signal", size=9, color=POS))

    # Шлях зворотного струму (в обхід щілини!)
    p.append('<path d="M %d %d L %d %d L %d %d L %d %d L %d %d" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="4 3"/>'
             % (gx2 + gw - 40, sy + 15, gx2 + 175, sy + 15, gx2 + 175, gy2 + gh - 10, gx2 + 125, gy2 + gh - 10, gx2 + 125, sy + 15, NEG))
    p.append(arrow(gx2 + 165, gy2 + gh - 10, gx2 + 135, gy2 + gh - 10, color=NEG, sw=1.5))
    p.append(text(gx2 + 150, gy2 + gh - 20, "Обхідний шлях", size=9, color=NEG))

    # Хвилі випромінювання від щілини
    for r_arc in (15, 28):
        p.append('<path d="M %d %d A %d %d 0 0 1 %d %d" fill="none" stroke="%s" stroke-width="1.5"/>'
                 % (gx2 + 150 - r_arc, sy, r_arc, r_arc, gx2 + 150 + r_arc, sy, POS))
    p.append(text(gx2 + 150, sy - 20, "Щілинна антена!", size=9, bold=True, color=POS))

    p.append(text(x2 + pw / 2, y1 + 195, "✗ Величезна площа контуру (петля роздута)", size=10, bold=True, color=POS))
    p.append(text(x2 + pw / 2, y1 + 215, "✗ Стрибок індуктивності L_loop → викид dI/dt", size=10, color=INK))
    p.append(text(x2 + pw / 2, y1 + 235, "✗ Провал випробувань на випромінювання", size=10, color=INK))

    render(os.path.join(IMG, "return-path-split.svg"), W, H, *p)


# ── 4. Мінімізація гарячої петлі у DC-DC перетворювачах ──────────────────────
def fig_hot_loop_minimization():
    W, H = 780, 310
    p = []
    p.append(text(W / 2, 24, "Мінімізація гарячої петлі (Hot Loop) у понижувальному перетворювачі", size=16, bold=True))

    pw, ph = 360, 250
    # Ліворуч: Погане розташування (велика петля)
    x1, y1 = 20, 45
    p.append(rect(x1, y1, pw, ph, fill="#fffafa", stroke=POS, sw=1.5, rx=6))
    p.append(text(x1 + pw / 2, y1 + 22, "ПОГАНО: Конденсатор віддалений від ключів", size=12, bold=True, color=POS))

    # Cin далеко ліворуч
    p.append(rect(x1 + 30, y1 + 60, 35, 70, fill="#f0f0f0", stroke=INK, sw=1.5))
    p.append(text(x1 + 47, y1 + 100, "C_in", size=10, bold=True, color=INK))

    # Ключі Q1/Q2 праворуч
    p.append(rect(x1 + 250, y1 + 55, 70, 40, fill="#e8f0fe", stroke=NEG, sw=1.5))
    p.append(text(x1 + 285, y1 + 80, "Q1 (Top)", size=9, bold=True, color=NEG))
    p.append(rect(x1 + 250, y1 + 105, 70, 40, fill="#e8f0fe", stroke=NEG, sw=1.5))
    p.append(text(x1 + 285, y1 + 130, "Q2 (Bot)", size=9, bold=True, color=NEG))

    # Довгі траси (контур)
    p.append(line(x1 + 65, y1 + 75, x1 + 250, y1 + 75, color=POS, sw=2.5))
    p.append(line(x1 + 65, y1 + 125, x1 + 250, y1 + 125, color=NEG, sw=2.5))
    p.append(arrow(x1 + 120, y1 + 75, x1 + 180, y1 + 75, color=POS, sw=1.5))
    p.append(arrow(x1 + 180, y1 + 125, x1 + 120, y1 + 125, color=NEG, sw=1.5))

    # Площа контуру зафарбована
    p.append(rect(x1 + 70, y1 + 80, 175, 40, fill="#ffebee", stroke="none"))
    p.append(text(x1 + 157, y1 + 104, "Велика площа S_loop", size=10, bold=True, color=POS))
    p.append(text(x1 + 157, y1 + 145, "Високе dI/dt → дзвін і випромінювання M", size=9, color=POS))

    p.append(text(x1 + pw / 2, y1 + 185, "✗ Паразитна індуктивність L_trace до 10–20 нГн", size=9, color=INK))
    p.append(text(x1 + pw / 2, y1 + 205, "✗ Сплески напруги V = L · (di/dt) пробивають ключі", size=9, color=INK))
    p.append(text(x1 + pw / 2, y1 + 225, "✗ Магнітне поле наводить завади на всю плату", size=9, color=INK))

    # Праворуч: Правильне розташування (компактна петля)
    x2, y2 = 400, 45
    p.append(rect(x2, y2, pw, ph, fill="#f9fcf9", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(x2 + pw / 2, y2 + 22, "ПРАВИЛЬНО: Cin впритул до виводів VIN/GND", size=12, bold=True, color=FIELD))

    # Cin прямо біля ключів
    p.append(rect(x2 + 70, y2 + 65, 35, 75, fill="#e8f5e9", stroke=FIELD, sw=1.5))
    p.append(text(x2 + 87, y2 + 107, "C_in", size=10, bold=True, color=FIELD))

    # Ключі в мікросхемі
    p.append(rect(x2 + 130, y2 + 65, 120, 75, fill="#e8f0fe", stroke=NEG, sw=1.5))
    p.append(text(x2 + 190, y2 + 90, "IC Конвертер", size=10, bold=True, color=INK))
    p.append(text(x2 + 190, y2 + 110, "VIN / PGND піни", size=9, color=MUTED))

    # Тісна петля
    p.append(line(x2 + 105, y2 + 80, x2 + 130, y2 + 80, color=POS, sw=3))
    p.append(line(x2 + 105, y2 + 125, x2 + 130, y2 + 125, color=NEG, sw=3))
    p.append(rect(x2 + 105, y2 + 85, 25, 35, fill="#c8e6c9", stroke="none"))
    p.append(text(x2 + 117, y2 + 106, "S_min", size=9, bold=True, color=FIELD))

    p.append(text(x2 + pw / 2, y2 + 160, "Короткий контур перемикання < 3–5 мм", size=10, bold=True, color=FIELD))
    p.append(text(x2 + pw / 2, y2 + 185, "✓ Індуктивність петлі зменшена до < 1–2 нГн", size=9, color=INK))
    p.append(text(x2 + pw / 2, y2 + 205, "✓ Сплески напруги (ringing) згасають миттєво", size=9, color=INK))
    p.append(text(x2 + pw / 2, y2 + 225, "✓ Поле замикається локально і не випромінює", size=9, color=INK))

    render(os.path.join(IMG, "hot-loop-minimization.svg"), W, H, *p)


# ── 5. Частотний імпеданс конденсатора та феритової намистини ────────────────
def fig_decoupling_ferrite_impedance():
    W, H = 760, 310
    p = []
    p.append(text(W / 2, 24, "Частотна поведінка реальних компонентів фільтрації", size=16, bold=True))

    pw, ph = 345, 250
    # Ліва панель: Реальний конденсатор (C + ESR + ESL)
    x1, y1 = 20, 45
    p.append(rect(x1, y1, pw, ph, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(text(x1 + pw / 2, y1 + 22, "Реальний конденсатор (C + ESR + ESL)", size=12, bold=True, color=NEG))

    # Графік |Z| конденсатора
    gx, gy, gw, gh = x1 + 50, y1 + 45, 260, 130
    p.append(line(gx, gy + gh, gx + gw, gy + gh, color=LINE, sw=1.5))  # вісь X
    p.append(line(gx, gy + gh, gx, gy, color=LINE, sw=1.5))            # вісь Y
    p.append(text(gx + gw - 10, gy + gh + 16, "Частота f", size=9, color=MUTED))
    p.append(text(gx - 8, gy + 15, "|Z|", size=10, bold=True, color=INK, anchor="end"))

    # V-подібна крива імпедансу конденсатора
    p.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (gx + 15, gy + 15, gx + 100, gy + gh - 15, gx + 130, gy + gh - 15, gx + 160, gy + gh - 15, gx + gw - 15, gy + 20, NEG))

    # Резонансна точка
    p.append('<circle cx="%d" cy="%d" r="4" fill="%s"/>' % (gx + 130, gy + gh - 15, POS))
    p.append(text(gx + 130, gy + gh - 25, "SRF", size=10, bold=True, color=POS))
    p.append(text(gx + 130, gy + gh + 14, "f_res = 1 / (2π√LC)", size=9, color=POS))

    p.append(text(gx + 45, gy + 50, "1 / (ωC)", size=9, color=NEG))
    p.append(text(gx + 45, gy + 65, "(ємнісний)", size=9, color=MUTED))
    p.append(text(gx + 200, gy + 50, "ω · ESL", size=9, color=POS))
    p.append(text(gx + 200, gy + 65, "(індуктивний)", size=9, color=MUTED))

    p.append(text(x1 + pw / 2, y1 + 205, "На дні V-кривої імпеданс рівний ESR (одиниці мОм)", size=9, bold=True, color=INK))
    p.append(text(x1 + pw / 2, y1 + 225, "Вище SRF конденсатор перетворюється на котушку!", size=9, color=POS))

    # Права панель: Феритова намистина Z = R + jX
    x2, y2 = 395, 45
    p.append(rect(x2, y2, pw, ph, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(text(x2 + pw / 2, y2 + 22, "Феритова намистина (Ferrite Bead)", size=12, bold=True, color=FIELD))

    # Графік фериту
    gx2 = x2 + 50
    p.append(line(gx2, gy + gh, gx2 + gw, gy + gh, color=LINE, sw=1.5))  # вісь X
    p.append(line(gx2, gy + gh, gx2, gy, color=LINE, sw=1.5))            # вісь Y
    p.append(text(gx2 + gw - 10, gy + gh + 16, "Частота f", size=9, color=MUTED))
    p.append(text(gx2 - 8, gy + 15, "Z, R, X", size=10, bold=True, color=INK, anchor="end"))

    # Крива X (реактивна індуктивність на низьких)
    p.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4 3"/>'
             % (gx2 + 15, gy + gh - 10, gx2 + 90, gy + 35, gx2 + 130, gy + 45, gx2 + 170, gy + gh - 15, gx2 + gw - 15, gy + gh - 5, NEG))
    p.append(text(gx2 + 70, gy + 60, "X(f)", size=9, color=NEG))

    # Крива R (активний опір втрат на високих)
    p.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (gx2 + 15, gy + gh - 2, gx2 + 100, gy + gh - 15, gx2 + 150, gy + 25, gx2 + 190, gy + 35, gx2 + gw - 15, gy + gh - 20, POS))
    p.append(text(gx2 + 210, gy + 55, "R(f)", size=9, color=POS))

    # Загальний імпеданс |Z|
    p.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2"/>'
             % (gx2 + 15, gy + gh - 12, gx2 + 110, gy + 20, gx2 + 155, gy + 18, gx2 + 195, gy + 30, gx2 + gw - 15, gy + gh - 25, FIELD))
    p.append(text(gx2 + 155, gy + 12, "|Z|", size=10, bold=True, color=FIELD))

    p.append(text(x2 + pw / 2, y2 + 205, "Низькі f: реактивна котушка (пропускає постійний струм)", size=9, color=INK))
    p.append(text(x2 + pw / 2, y2 + 225, "Високі f: резистор R(f) розсіює шум у ТЕПЛО", size=9, bold=True, color=FIELD))

    render(os.path.join(IMG, "decoupling-ferrite-impedance.svg"), W, H, *p)


if __name__ == "__main__":
    fig_source_path_victim()
    fig_four_coupling_paths()
    fig_return_path_split()
    fig_hot_loop_minimization()
    fig_decoupling_ferrite_impedance()
    print("All 5 figures generated successfully into img/")
