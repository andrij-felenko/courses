# -*- coding: utf-8 -*-
"""Фігури до теми «Ефект Rowhammer у DRAM: фізика збою комірок».
Запуск: python figs.py  → генерує SVG у ./img/
Стиль і примітиви — зі спільного svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Фізика ємнісного перехресного зв'язку словесних ліній ────────────────
def fig_wordline_coupling():
    W, H = 880, 520
    f = []

    # Заголовок
    f.append(text(W / 2, 28, "Фізика збурення сусідньої комірки: паразитна ємність та інжекція носіїв", size=16, bold=True))

    # Ліва частина: Структура зрізу кристала (агресор і жертва)
    f.append(rect(40, 55, 480, 435, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(280, 80, "Поперечний переріз комірок масиву DRAM (вузол < 25 нм)", size=13, bold=True, color=INK))

    # Підкладка (p-well)
    f.append(rect(60, 310, 440, 160, fill="#f5f0eb", stroke="#b89d85", sw=1.5, rx=4))
    f.append(text(280, 450, "Спільна p-кишеня кремнію (p-well substrate)", size=12, color="#7d5d3b", bold=True))

    # N+ дифузійні області (drain / source)
    # Агресор n+
    f.append(rect(80, 275, 60, 45, fill="#d5e8d4", stroke="#82b366", sw=1.5, rx=2))
    f.append(rect(180, 275, 60, 45, fill="#d5e8d4", stroke="#82b366", sw=1.5, rx=2))
    f.append(text(110, 302, "n+ (BL)", size=11, color="#274e13", bold=True))
    f.append(text(210, 302, "n+ (C_S)", size=11, color="#274e13", bold=True))

    # Жертва n+
    f.append(rect(290, 275, 60, 45, fill="#f8cecc", stroke="#b85450", sw=1.5, rx=2))
    f.append(rect(390, 275, 60, 45, fill="#f8cecc", stroke="#b85450", sw=1.5, rx=2))
    f.append(text(320, 302, "n+ (BL)", size=11, color="#660000", bold=True))
    f.append(text(420, 302, "n+ (C_V)", size=11, color="#660000", bold=True))

    # Затвори / Wordlines (поховані словесні лінії BCAT)
    # Агресор WL_A
    f.append(rect(130, 220, 60, 65, fill="#ffe6cc", stroke=POS, sw=2, rx=3))
    f.append(text(160, 245, "WL_A", size=13, bold=True, color=POS))
    f.append(text(160, 265, "Агресор", size=10, color=POS))

    # Жертва WL_V
    f.append(rect(340, 220, 60, 65, fill="#e1d5e7", stroke=NEG, sw=2, rx=3))
    f.append(text(370, 245, "WL_V", size=13, bold=True, color=NEG))
    f.append(text(370, 265, "Жертва", size=10, color=NEG))

    # Конденсатори зберігання (стековані циліндри C_S)
    f.append(rect(195, 110, 30, 160, fill="#dae8fc", stroke="#6c8ebf", sw=1.5, rx=3))
    f.append(text(210, 175, "C_A", size=12, bold=True, color=NEG))

    f.append(rect(405, 110, 30, 160, fill="#f8cecc", stroke=POS, sw=1.8, rx=3))
    f.append(text(420, 175, "C_V", size=12, bold=True, color=POS))
    f.append(text(420, 140, "Заряд", size=9, color=POS))

    # Паразитна ємність між словесними лініями C_WL-WL
    f.append(line(190, 252, 340, 252, color=POS, sw=2, dash="4,3"))
    f.append(text(265, 240, "C_WL-WL", size=12, bold=True, color=POS))
    f.append(text(265, 268, "(перехресний зв'язок)", size=9, color=POS))

    # Витоки через підкладку та інжекція
    f.append(arrow(160, 285, 230, 340, color=POS, sw=1.8))
    f.append(text(210, 365, "Гарячі носії (HCI)", size=10, color=POS, bold=True))

    f.append(arrow(260, 375, 380, 310, color=POS, sw=1.8))
    f.append(text(340, 390, "Струм витоку I_sub", size=10, color=POS, bold=True))

    # Права частина: Пояснення трьох фізичних чинників
    px = 540
    f.append(rect(px, 55, 300, 435, fill="#f8f9fa", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(px + 150, 80, "Три вектори деградації заряду", size=13, bold=True, color=INK))

    # Блок 1
    f.append(rect(px + 12, 98, 276, 100, fill="#fff2cc", stroke="#d6b656", sw=1.2, rx=6))
    f.append(text(px + 24, 118, "1. Ємнісне перекачування (C_WL-WL)", size=11, bold=True, color="#825a00", anchor="start"))
    f.append(text(px + 24, 138, "Перемикання WL_A (V_PP ↔ V_NWL)", size=10, color=INK, anchor="start"))
    f.append(text(px + 24, 154, "наводить імпульси напруги ΔV на WL_V,", size=10, color=INK, anchor="start"))
    f.append(text(px + 24, 170, "миттєво відкриваючи закритий транзистор.", size=10, color=INK, anchor="start"))
    f.append(text(px + 24, 186, "Втрата: ΔQ = C_couple · ΔV_WL", size=10, color="#825a00", bold=True, anchor="start"))

    # Блок 2
    f.append(rect(px + 12, 210, 276, 110, fill="#f8cecc", stroke="#b85450", sw=1.2, rx=6))
    f.append(text(px + 24, 230, "2. Інжекція гарячих носіїв (HCI)", size=11, bold=True, color="#990000", anchor="start"))
    f.append(text(px + 24, 250, "Різкі фронти з амплітудою ~3.3 В", size=10, color=INK, anchor="start"))
    f.append(text(px + 24, 266, "створюють високоенергетичні електрони.", size=10, color=INK, anchor="start"))
    f.append(text(px + 24, 282, "Вони дифундують крізь p-кишеню", size=10, color=INK, anchor="start"))
    f.append(text(px + 24, 298, "і захоплюються вузлом зберігання C_V.", size=10, color=INK, anchor="start"))

    # Блок 3
    f.append(rect(px + 12, 332, 276, 140, fill="#e1d5e7", stroke="#9673a6", sw=1.2, rx=6))
    f.append(text(px + 24, 352, "3. Флуктуація потенціалу підкладки", size=11, bold=True, color="#4a2574", anchor="start"))
    f.append(text(px + 24, 372, "Струми перемикання зміщують", size=10, color=INK, anchor="start"))
    f.append(text(px + 24, 388, "локальний потенціал p-well (body bounce).", size=10, color=INK, anchor="start"))
    f.append(text(px + 24, 404, "Це знижує порогову напругу V_th жертви", size=10, color=INK, anchor="start"))
    f.append(text(px + 24, 420, "та експоненційно розганяє підпороговий", size=10, color=INK, anchor="start"))
    f.append(text(px + 24, 436, "струм розряду конденсатора (GIDL/I_sub).", size=10, color=INK, anchor="start"))

    render(os.path.join(IMG, "wordline-capacitive-coupling.svg"), W, H, *f)


# ── 2. Топологічні шаблони атак Rowhammer ────────────────────────────────────
def fig_aggressor_patterns():
    W, H = 880, 480
    f = []

    f.append(text(W / 2, 28, "Топологічні шаблони активації: від Single-Sided до Blacksmith", size=16, bold=True))

    # Стовпчик 1: Single-Sided
    x1 = 40
    w_col = 185
    f.append(rect(x1, 55, w_col, 405, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(x1 + w_col / 2, 80, "Single-Sided", size=13, bold=True, color=INK))
    f.append(text(x1 + w_col / 2, 98, "(односторонній молот)", size=10, color=MUTED))

    # Рядки
    ry = 120
    rh = 36
    f.append(rect(x1 + 15, ry, w_col - 30, rh, fill="#f5f5f5", stroke="#cccccc", sw=1, rx=4))
    f.append(text(x1 + w_col / 2, ry + 22, "Рядок N-1 (Жертва)", size=10, color=NEG))

    f.append(rect(x1 + 15, ry + 44, w_col - 30, rh, fill="#ffe6cc", stroke=POS, sw=2, rx=4))
    f.append(text(x1 + w_col / 2, ry + 66, "Рядок N (Агресор)", size=11, bold=True, color=POS))

    f.append(rect(x1 + 15, ry + 88, w_col - 30, rh, fill="#f5f5f5", stroke="#cccccc", sw=1, rx=4))
    f.append(text(x1 + w_col / 2, ry + 110, "Рядок N+1 (Жертва)", size=10, color=NEG))

    f.append(arrow(x1 + w_col / 2, ry + 44, x1 + w_col / 2, ry + 36, color=POS, sw=1.8))
    f.append(arrow(x1 + w_col / 2, ry + 80, x1 + w_col / 2, ry + 88, color=POS, sw=1.8))

    f.append(textbox(x1 + w_col / 2, 330, "Активація одного рядка N.\nЗбурення розсіюється\nна обидва сусідні рядки.\nПоріг N_ACT: ~100 000\n(DDR3, перші досліди)", size=10, min_w=165)[0])

    # Стовпчик 2: Double-Sided
    x2 = 250
    f.append(rect(x2, 55, w_col, 405, fill="#fbfcfd", stroke=POS, sw=1.8, rx=8))
    f.append(text(x2 + w_col / 2, 80, "Double-Sided", size=13, bold=True, color=POS))
    f.append(text(x2 + w_col / 2, 98, "(сендвіч-атака)", size=10, color=POS))

    f.append(rect(x2 + 15, ry, w_col - 30, rh, fill="#ffe6cc", stroke=POS, sw=2, rx=4))
    f.append(text(x2 + w_col / 2, ry + 22, "Рядок N-1 (Агресор 1)", size=10, bold=True, color=POS))

    f.append(rect(x2 + 15, ry + 44, w_col - 30, rh, fill="#f8cecc", stroke="#b85450", sw=2, rx=4))
    f.append(text(x2 + w_col / 2, ry + 66, "Рядок N (ЖЕРТВА)", size=11, bold=True, color="#990000"))

    f.append(rect(x2 + 15, ry + 88, w_col - 30, rh, fill="#ffe6cc", stroke=POS, sw=2, rx=4))
    f.append(text(x2 + w_col / 2, ry + 110, "Рядок N+1 (Агресор 2)", size=10, bold=True, color=POS))

    f.append(arrow(x2 + w_col / 2, ry + 36, x2 + w_col / 2, ry + 44, color=POS, sw=2))
    f.append(arrow(x2 + w_col / 2, ry + 88, x2 + w_col / 2, ry + 80, color=POS, sw=2))

    f.append(textbox(x2 + w_col / 2, 330, "Чергування (N-1) ↔ (N+1).\nПодвійний тиск на рядок N\nз обох боків одночасно.\nПоріг N_ACT падає в 2-4 рази!\nОсновний вектор експлойтів.", size=10, min_w=165)[0])

    # Стовпчик 3: Half-Double
    x3 = 460
    f.append(rect(x3, 55, w_col, 405, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(x3 + w_col / 2, 80, "Half-Double", size=13, bold=True, color=INK))
    f.append(text(x3 + w_col / 2, 98, "(дистанція 2 рядки)", size=10, color=MUTED))

    f.append(rect(x3 + 15, ry - 10, w_col - 30, 30, fill="#ffe6cc", stroke=POS, sw=1.8, rx=4))
    f.append(text(x3 + w_col / 2, ry + 8, "Рядок N-2 (Агресор)", size=9, bold=True, color=POS))

    f.append(rect(x3 + 15, ry + 26, w_col - 30, 30, fill="#fff2cc", stroke="#d6b656", sw=1.2, rx=4))
    f.append(text(x3 + w_col / 2, ry + 44, "Рядок N-1 (Проміжний)", size=9, color="#825a00"))

    f.append(rect(x3 + 15, ry + 62, w_col - 30, 30, fill="#f8cecc", stroke="#b85450", sw=2, rx=4))
    f.append(text(x3 + w_col / 2, ry + 80, "Рядок N (ЖЕРТВА)", size=10, bold=True, color="#990000"))

    f.append(arrow(x3 + w_col / 2, ry + 20, x3 + w_col / 2, ry + 26, color=POS, sw=1.5))
    f.append(arrow(x3 + w_col / 2, ry + 56, x3 + w_col / 2, ry + 62, color="#d6b656", sw=1.5))

    f.append(textbox(x3 + w_col / 2, 330, "Агресор б'є по N-2.\nЗахист TRR рятує N-1,\nале легке збурення N-1\nплюс фоновий витік\nдобивають рядок N на діст. 2!", size=10, min_w=165)[0])

    # Стовпчик 4: Blacksmith
    x4 = 670
    f.append(rect(x4, 55, w_col, 405, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(x4 + w_col / 2, 80, "Blacksmith", size=13, bold=True, color=INK))
    f.append(text(x4 + w_col / 2, 98, "(неоднорідний шаблон)", size=10, color=MUTED))

    # Складна пачка агресорів
    f.append(rect(x4 + 15, ry - 15, w_col - 30, 24, fill="#ffe6cc", stroke=POS, sw=1.2, rx=3))
    f.append(text(x4 + w_col / 2, ry - 1, "Агр. A1 (f = 40%)", size=9, color=POS))

    f.append(rect(x4 + 15, ry + 13, w_col - 30, 24, fill="#ffe6cc", stroke=POS, sw=1.2, rx=3))
    f.append(text(x4 + w_col / 2, ry + 27, "Агр. A2 (f = 25%)", size=9, color=POS))

    f.append(rect(x4 + 15, ry + 41, w_col - 30, 24, fill="#f8cecc", stroke="#b85450", sw=2, rx=3))
    f.append(text(x4 + w_col / 2, ry + 55, "ЖЕРТВА V", size=10, bold=True, color="#990000"))

    f.append(rect(x4 + 15, ry + 69, w_col - 30, 24, fill="#ffe6cc", stroke=POS, sw=1.2, rx=3))
    f.append(text(x4 + w_col / 2, ry + 83, "Агр. A3 (f = 35%)", size=9, color=POS))

    f.append(textbox(x4 + w_col / 2, 330, "Атака на N рядків одночасно\nз різними частотами.\nПереповнює внутрішні\nтаблиці семплювання TRR\nу чіпах DDR4 і DDR5.", size=10, min_w=165)[0])

    render(os.path.join(IMG, "aggressor-victim-patterns.svg"), W, H, *f)


# ── 3. Часова діаграма регенерації та витоку заряду ─────────────────────────
def fig_timeline_refresh():
    W, H = 880, 500
    f = []

    f.append(text(W / 2, 28, "Часова шкала регенерації tREFW проти імпульсного шторму Rowhammer", size=16, bold=True))

    # Вісь часу
    t_start_x, t_end_x = 80, 800
    y_axis = 430
    f.append(line(t_start_x, y_axis, t_end_x + 30, y_axis, color=INK, sw=2))
    f.append(arrow(t_end_x + 20, y_axis, t_end_x + 35, y_axis, color=INK, sw=2))
    f.append(text(t_end_x + 40, y_axis + 5, "t", size=14, bold=True, anchor="start"))

    # Позначки часу
    f.append(line(t_start_x, y_axis - 5, t_start_x, y_axis + 5, color=INK, sw=1.5))
    f.append(text(t_start_x, y_axis + 22, "t = 0", size=11, color=MUTED))

    t_flip_x = 480
    f.append(line(t_flip_x, 80, t_flip_x, y_axis + 5, color=POS, sw=1.5, dash="4,3"))
    f.append(text(t_flip_x, y_axis + 22, "t_flip ≈ 28 мс", size=11, bold=True, color=POS))

    t_ref_x = 760
    f.append(line(t_ref_x, 80, t_ref_x, y_axis + 5, color=FIELD, sw=1.5, dash="4,3"))
    f.append(text(t_ref_x, y_axis + 22, "tREFW = 64 мс (Планова регенерація)", size=11, bold=True, color=FIELD))

    # Верхній трек: Команди шини (ACT / PRE)
    y_cmd = 110
    f.append(text(t_start_x, y_cmd - 25, "Команди контролера (Row Hammer Loop):", size=12, bold=True, anchor="start"))

    # Серія вузьких прямокутників ACT/PRE
    for i in range(16):
        cx = t_start_x + i * 42
        f.append(rect(cx, y_cmd - 12, 18, 24, fill="#ffe6cc", stroke=POS, sw=1.2, rx=2))
        f.append(text(cx + 9, y_cmd + 4, "A", size=10, bold=True, color=POS))
        f.append(rect(cx + 20, y_cmd - 12, 18, 24, fill="#f5f5f5", stroke=MUTED, sw=1.2, rx=2))
        f.append(text(cx + 29, y_cmd + 4, "P", size=10, color=MUTED))

    f.append(text(t_start_x + 16 * 42 + 20, y_cmd + 4, "… сотні тисяч пар ACT/PRE підряд (t_RC ≈ 45 нс) …", size=11, color=POS, italic=True, anchor="start"))

    # Графік заряду конденсатора жертви Q(t)
    y_q_top = 180
    y_q_bot = 400
    f.append(line(t_start_x, y_q_top - 10, t_start_x, y_q_bot + 10, color=INK, sw=1.5))
    f.append(arrow(t_start_x, y_q_top, t_start_x, y_q_top - 15, color=INK, sw=1.5))
    f.append(text(t_start_x - 10, y_q_top - 10, "Заряд Q", size=12, bold=True, anchor="end"))

    # Рівень Q_full, Q_sense, Q_zero
    f.append(line(t_start_x - 5, y_q_top + 20, t_end_x, y_q_top + 20, color="#27ae60", sw=1, dash="3,3"))
    f.append(text(t_start_x - 10, y_q_top + 24, "Q_full (Логічна «1»)", size=10, color="#27ae60", anchor="end"))

    y_sense = 300
    f.append(line(t_start_x - 5, y_sense, t_end_x, y_sense, color=POS, sw=1.5, dash="5,4"))
    f.append(text(t_start_x - 10, y_sense + 4, "Q_sense (Поріг читання)", size=10, bold=True, color=POS, anchor="end"))

    # Нормальний розряд (зелена лінія — повільний спад)
    f.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="#27ae60" stroke-width="2.5"/>' %
             (t_start_x, y_q_top + 20, (t_start_x + t_ref_x)/2, y_q_top + 45, t_ref_x, y_sense - 35))
    f.append(text(620, y_sense - 55, "Природний витік (безпечно, Q > Q_sense)", size=10, bold=True, color="#27ae60"))

    # Прискорений розряд під атакою Rowhammer (червона крута пилка)
    path_d = ["M %d %d" % (t_start_x, y_q_top + 20)]
    steps = 14
    for s in range(1, steps + 1):
        sx = t_start_x + s * (t_flip_x - t_start_x + 90) / steps
        sy = y_q_top + 20 + s * (y_q_bot - y_q_top - 30) / steps
        path_d.append("L %d %d" % (sx - 8, sy - 4))
        path_d.append("L %d %d" % (sx, sy))

    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(path_d), POS))

    # Точка збою Bit Flip
    f.append(circle(t_flip_x, y_sense, 6, fill=POS, stroke="#ffffff", sw=2))
    f.append(textbox(t_flip_x + 95, y_sense + 38, "ЗБІЙ BIT FLIP!\nЗаряд впав нижче порога\nдо приходу команди REFRESH", size=10, color=POS, bold=True, fill="#ffe6cc", stroke=POS)[0])

    render(os.path.join(IMG, "rowhammer-timeline-refresh.svg"), W, H, *f)


# ── 4. Архітектура методів захисту (Mitigations) ─────────────────────────────
def fig_mitigation_mechanisms():
    W, H = 880, 500
    f = []

    f.append(text(W / 2, 28, "Архітектурні ешелони захисту від Rowhammer у пам'яті та контролері", size=16, bold=True))

    # Три рівні / блоки
    # Рівень 1: Пам'ять (In-DRAM)
    x1, y1, w_box, h_box = 40, 60, 255, 410
    f.append(rect(x1, y1, w_box, h_box, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(x1 + w_box / 2, y1 + 25, "1. Усередині чіпа (In-DRAM)", size=13, bold=True, color=INK))

    f.append(rect(x1 + 12, y1 + 45, w_box - 24, 85, fill="#e8f0fe", stroke=NEG, sw=1.2, rx=6))
    f.append(text(x1 + w_box / 2, y1 + 65, "Target Row Refresh (TRR)", size=11, bold=True, color=NEG))
    f.append(text(x1 + 20, y1 + 83, "• Апаратне семплювання адрес", size=10, color=INK, anchor="start"))
    f.append(text(x1 + 20, y1 + 99, "• Приховані цикли поновлення сусідів", size=10, color=INK, anchor="start"))
    f.append(text(x1 + 20, y1 + 115, "• Вразливий до Blacksmith / TRRespass", size=10, color=POS, anchor="start"))

    f.append(rect(x1 + 12, y1 + 140, w_box - 24, 95, fill="#f5f0eb", stroke="#b89d85", sw=1.2, rx=6))
    f.append(text(x1 + w_box / 2, y1 + 160, "Фізичне проектування комірок", size=11, bold=True, color="#7d5d3b"))
    f.append(text(x1 + 20, y1 + 178, "• Збільшення ізоляції Wordline", size=10, color=INK, anchor="start"))
    f.append(text(x1 + 20, y1 + 194, "• Глибші кишені (Deep Well)", size=10, color=INK, anchor="start"))
    f.append(text(x1 + 20, y1 + 210, "• Збільшення ємності C_S (> 15 fF)", size=10, color=INK, anchor="start"))
    f.append(text(x1 + 20, y1 + 226, "• Обмежує масштабування вузла", size=10, color=MUTED, anchor="start"))

    f.append(rect(x1 + 12, y1 + 245, w_box - 24, 150, fill="#fdf0ed", stroke=POS, sw=1.2, rx=6))
    f.append(text(x1 + w_box / 2, y1 + 265, "DDR5: Directed RFM / DRR", size=11, bold=True, color=POS))
    f.append(text(x1 + 20, y1 + 283, "• Сигнал RFM (Refresh Management)", size=10, color=INK, anchor="start"))
    f.append(text(x1 + 20, y1 + 299, "• Чіп сигналізує про високе навантаження", size=10, color=INK, anchor="start"))
    f.append(text(x1 + 20, y1 + 315, "• Контролер виділяє квант часу", size=10, color=INK, anchor="start"))
    f.append(text(x1 + 20, y1 + 331, "• DRR: точна адреса агресора", size=10, color=INK, anchor="start"))
    f.append(text(x1 + 20, y1 + 347, "• Стандарт JEDEC DDR5", size=10, color="#27ae60", bold=True, anchor="start"))

    # Рівень 2: Контролер пам'яті (Memory Controller)
    x2 = 312
    f.append(rect(x2, y1, w_box, h_box, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(x2 + w_box / 2, y1 + 25, "2. Контролер пам'яті (MC)", size=13, bold=True, color=INK))

    f.append(rect(x2 + 12, y1 + 45, w_box - 24, 100, fill="#fbf8e6", stroke="#d6b656", sw=1.2, rx=6))
    f.append(text(x2 + w_box / 2, y1 + 65, "2x / 4x Refresh Rate", size=11, bold=True, color="#825a00"))
    f.append(text(x2 + 20, y1 + 83, "• Скорочення tREFI: 7.8 мкс → 3.9 мкс", size=10, color=INK, anchor="start"))
    f.append(text(x2 + 20, y1 + 99, "• Вдвічі менше часу на атаку", size=10, color=INK, anchor="start"))
    f.append(text(x2 + 20, y1 + 115, "• Падіння пропускної здатності ~3-5%", size=10, color=POS, anchor="start"))
    f.append(text(x2 + 20, y1 + 131, "• Ріст енергоспоживання", size=10, color=POS, anchor="start"))

    f.append(rect(x2 + 12, y1 + 155, w_box - 24, 115, fill="#e8f5e9", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(x2 + w_box / 2, y1 + 175, "Алгоритм PARA", size=11, bold=True, color=FIELD))
    f.append(text(x2 + 20, y1 + 193, "• Ймовірнісна регенерація сусідів", size=10, color=INK, anchor="start"))
    f.append(text(x2 + 20, y1 + 209, "• На кожне закриття PRE з ймов. p ≈ 0.001", size=10, color=INK, anchor="start"))
    f.append(text(x2 + 20, y1 + 225, "  поновлюється рядок (Row ± 1)", size=10, color=INK, anchor="start"))
    f.append(text(x2 + 20, y1 + 241, "• Без збереження стану й пам'яті!", size=10, color=FIELD, bold=True, anchor="start"))
    f.append(text(x2 + 20, y1 + 257, "• Нульові накладні витрати пам'яті", size=10, color=INK, anchor="start"))

    f.append(rect(x2 + 12, y1 + 280, w_box - 24, 115, fill="#f3e5f5", stroke="#9c27b0", sw=1.2, rx=6))
    f.append(text(x2 + w_box / 2, y1 + 300, "Детерміновані лічильники", size=11, bold=True, color="#7b1fa2"))
    f.append(text(x2 + 20, y1 + 318, "• TWiCE / Graphene / BlockHammer", size=10, color=INK, anchor="start"))
    f.append(text(x2 + 20, y1 + 334, "• Точний підрахунок ACT по рядках", size=10, color=INK, anchor="start"))
    f.append(text(x2 + 20, y1 + 350, "• Примусове гальмування агресора", size=10, color=INK, anchor="start"))
    f.append(text(x2 + 20, y1 + 366, "• Потребує буферів у MC", size=10, color=MUTED, anchor="start"))

    # Рівень 3: Системний та апаратний рівень (System / OS)
    x3 = 584
    f.append(rect(x3, y1, w_box, h_box, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(x3 + w_box / 2, y1 + 25, "3. Системний та ОС рівень", size=13, bold=True, color=INK))

    f.append(rect(x3 + 12, y1 + 45, w_box - 24, 110, fill="#ede7f6", stroke="#673ab7", sw=1.2, rx=6))
    f.append(text(x3 + w_box / 2, y1 + 65, "ECC (SECDED & Chipkill)", size=11, bold=True, color="#512da8"))
    f.append(text(x3 + 20, y1 + 83, "• Виправляє 1 біт на 64-бітне слово", size=10, color=INK, anchor="start"))
    f.append(text(x3 + 20, y1 + 99, "• Детектує 2 біти (падіння в Kernel Panic)", size=10, color=INK, anchor="start"))
    f.append(text(x3 + 20, y1 + 115, "• Вразливий до спрямованого", size=10, color=POS, anchor="start"))
    f.append(text(x3 + 20, y1 + 131, "  мультибітного збою (ECCploit)", size=10, color=POS, anchor="start"))

    f.append(rect(x3 + 12, y1 + 165, w_box - 24, 105, fill="#efebe9", stroke="#8d6e63", sw=1.2, rx=6))
    f.append(text(x3 + w_box / 2, y1 + 185, "Ізоляція сторінок у ядрі ОС", size=11, bold=True, color="#4e342e"))
    f.append(text(x3 + 20, y1 + 203, "• B-Alloc / ZebRAM ізоляція", size=10, color=INK, anchor="start"))
    f.append(text(x3 + 20, y1 + 219, "• Розділення фізичних рядків ядра", size=10, color=INK, anchor="start"))
    f.append(text(x3 + 20, y1 + 235, "  та непривілейованих процесів", size=10, color=INK, anchor="start"))
    f.append(text(x3 + 20, y1 + 251, "• Захисні смуги порожніх сторінок", size=10, color=INK, anchor="start"))

    f.append(rect(x3 + 12, y1 + 280, w_box - 24, 115, fill="#e0f2f1", stroke="#00897b", sw=1.2, rx=6))
    f.append(text(x3 + w_box / 2, y1 + 300, "Програмні обмеження", size=11, bold=True, color="#004d40"))
    f.append(text(x3 + 20, y1 + 318, "• Заборона некешованого доступу", size=10, color=INK, anchor="start"))
    f.append(text(x3 + 20, y1 + 334, "• Зниження точності таймерів у JS", size=10, color=INK, anchor="start"))
    f.append(text(x3 + 20, y1 + 350, "  (performance.now)", size=10, color=INK, anchor="start"))
    f.append(text(x3 + 20, y1 + 366, "• Блокування інструкцій clflush", size=10, color=INK, anchor="start"))

    render(os.path.join(IMG, "mitigation-mechanisms.svg"), W, H, *f)


if __name__ == "__main__":
    fig_wordline_coupling()
    fig_aggressor_patterns()
    fig_timeline_refresh()
    fig_mitigation_mechanisms()
    print("Готово: 4 SVG у", IMG)
