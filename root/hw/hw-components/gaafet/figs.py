# -*- coding: utf-8 -*-
"""Фігури до теми «GAAFET і наношари: транзистори з круговим затвором» (book/electronics/microelectronics/gaafet)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), "img"), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), "img")


def fig_planar_vs_finfet_vs_gaafet():
    w, h = 960, 440
    frags = []

    # Заголовки трьох поколінь
    t1, _, _ = textbox(160, 30, "1. Planar MOSFET (2D)\nЗатвор лише зверху (1 грань)", size=12, bold=True, pad=6)
    frags.append(t1)

    t2, _, _ = textbox(480, 30, "2. FinFET / Tri-Gate (3D)\nЗатвор з трьох боків ребра", size=12, bold=True, pad=6)
    frags.append(t2)

    t3, _, _ = textbox(800, 30, "3. GAAFET / Nanosheet (4D)\nКруговий затвор (усі 4 боки)", size=12, bold=True, pad=6)
    frags.append(t3)

    # ── 1. Planar MOSFET ──
    # Підкладка
    frags.append(rect(30, 160, 260, 140, fill="#e8ecf1", stroke="#7f8c8d", sw=1.5, rx=0))
    frags.append(text(160, 280, "p-підкладка Si", size=11, color=MUTED))

    # Витік / Стік
    frags.append(rect(30, 160, 65, 55, fill="#d4edda", stroke="#27ae60", sw=1.5, rx=0))
    frags.append(text(62, 192, "n⁺ Витік", size=10, bold=True, color="#1e7e34"))

    frags.append(rect(225, 160, 65, 55, fill="#d4edda", stroke="#27ae60", sw=1.5, rx=0))
    frags.append(text(257, 192, "n⁺ Стік", size=10, bold=True, color="#1e7e34"))

    # Оксид і Затвор
    frags.append(rect(95, 150, 130, 10, fill="#ffeeba", stroke="#d39e00", sw=1.2, rx=0))
    frags.append(rect(95, 95, 130, 55, fill="#cce5ff", stroke="#004085", sw=1.5, rx=2))
    frags.append(text(160, 125, "Затвор (Gate)", size=11, bold=True, color="#004085"))

    # Витік у глибині підкладки
    frags.append(line(225, 195, 95, 195, color=POS, sw=1.5, dash="3,3"))
    frags.append(line(225, 210, 95, 210, color=POS, sw=1.5, dash="3,3"))
    tb_l1, _, _ = textbox(160, 210, "Глибокий витік DIBL\nв обхід затвора", size=10, color=POS, fill="#fff3cd", stroke=POS, pad=4)
    frags.append(tb_l1)

    tb_n1, _, _ = textbox(160, 375, "Слабкий контроль:\nвитік при L_g < 30 нм", size=10, color=INK, fill="#ffffff", stroke=MUTED, pad=5)
    frags.append(tb_n1)

    # Розділювач 1
    frags.append(line(320, 20, 320, 420, color="#d0d7de", sw=1.5, dash="4,4"))

    # ── 2. FinFET ──
    # Основа STI
    frags.append(rect(350, 270, 260, 45, fill="#e8ecf1", stroke="#7f8c8d", sw=1.5, rx=0))
    frags.append(text(480, 295, "Ізоляція STI (SiO₂)", size=11, color=MUTED))

    # Вертикальне ребро
    frags.append(rect(455, 110, 50, 100, fill="#d4edda", stroke="#27ae60", sw=1.8, rx=0))
    frags.append(text(480, 160, "Канал Si", size=10, bold=True, color="#1e7e34"))

    # Затвор FinFET з 3 боків
    frags.append(rect(410, 95, 45, 115, fill="#cce5ff", stroke="#004085", sw=1.4, rx=1))
    frags.append(rect(505, 95, 45, 115, fill="#cce5ff", stroke="#004085", sw=1.4, rx=1))
    frags.append(rect(410, 60, 140, 35, fill="#cce5ff", stroke="#004085", sw=1.4, rx=1))
    frags.append(text(480, 80, "Затвор (3 боки)", size=11, bold=True, color="#004085"))

    # Підреберний витік
    frags.append(line(430, 235, 530, 235, color=POS, sw=1.5, dash="3,3"))
    tb_l2, _, _ = textbox(480, 240, "Sub-fin витік під основою\nпри L_g < 14 нм", size=9.5, color=POS, fill="#fff3cd", stroke=POS, pad=3)
    frags.append(tb_l2)

    tb_n2, _, _ = textbox(480, 375, "Дно ребра без затвора;\nдискретне квантування W_eff", size=10, color=INK, fill="#ffffff", stroke=MUTED, pad=5)
    frags.append(tb_n2)

    # Розділювач 2
    frags.append(line(640, 20, 640, 420, color="#d0d7de", sw=1.5, dash="4,4"))

    # ── 3. GAAFET / Nanosheet ──
    # Основа STI
    frags.append(rect(670, 255, 260, 55, fill="#e8ecf1", stroke="#7f8c8d", sw=1.5, rx=0))
    frags.append(text(800, 290, "Діелектрична основа", size=11, color=MUTED))

    # Спільний блок затвора
    frags.append(rect(710, 65, 180, 185, fill="#cce5ff", stroke="#004085", sw=1.5, rx=3))
    frags.append(text(800, 82, "Металевий затвор HKMG", size=10, bold=True, color="#004085"))

    # 3 наношари
    frags.append(rect(735, 100, 130, 22, fill="#d4edda", stroke="#27ae60", sw=1.6, rx=2))
    frags.append(text(800, 114, "Наношар 3 (Si)", size=9.5, bold=True, color="#1e7e34"))

    frags.append(rect(735, 145, 130, 22, fill="#d4edda", stroke="#27ae60", sw=1.6, rx=2))
    frags.append(text(800, 159, "Наношар 2 (Si)", size=9.5, bold=True, color="#1e7e34"))

    frags.append(rect(735, 190, 130, 22, fill="#d4edda", stroke="#27ae60", sw=1.6, rx=2))
    frags.append(text(800, 204, "Наношар 1 (Si)", size=9.5, bold=True, color="#1e7e34"))

    # Стрілки
    frags.append(arrow(725, 156, 735, 156, color=FIELD, sw=1.4))
    frags.append(arrow(875, 156, 865, 156, color=FIELD, sw=1.4))
    frags.append(arrow(800, 132, 800, 142, color=FIELD, sw=1.4))
    frags.append(arrow(800, 180, 800, 170, color=FIELD, sw=1.4))

    tb_n3, _, _ = textbox(800, 375, "100% круговий контроль;\nдовільна ширина W_ns; нуль витоку", size=10, color="#1e7e34", fill="#d4edda", stroke="#27ae60", pad=5)
    frags.append(tb_n3)

    render(os.path.join(IMG, "planar-vs-finfet-vs-gaafet.svg"), w, h, *frags)


def fig_gaafet_fabrication_flow():
    w, h = 960, 490
    frags = []

    # Заголовок
    tb_hdr, _, _ = textbox(480, 25, "Технологічний маршрут виготовлення наношарів GAAFET (Gate-All-Around)", size=13, bold=True, pad=6)
    frags.append(tb_hdr)

    # 6 етапів у вигляді сітки 3 × 2
    # Етап 1: Епітаксія суперґратки Si/SiGe
    frags.append(rect(30, 60, 280, 185, fill="#ffffff", stroke="#7f8c8d", sw=1.2, rx=4))
    tb_s1, _, _ = textbox(170, 75, "1. Епітаксія суперґратки Si / SiGe", size=11, bold=True, pad=4, fill="#e8ecf1")
    frags.append(tb_s1)

    frags.append(rect(50, 195, 240, 35, fill="#d0d7de", stroke="#6b7280", sw=1.2, rx=0))
    frags.append(text(170, 217, "Підкладка монокристалічного Si", size=9.5, color=INK))

    colors_stack = [("#d4edda", "Si (канал, 5 нм)"), ("#ffeeba", "SiGe (жертовний, 10 нм)")]
    for i in range(5):
        c, _ = colors_stack[i % 2]
        y_pos = 180 - i * 16
        frags.append(rect(70, y_pos, 200, 13, fill=c, stroke="#6b7280", sw=1.0, rx=0))
    frags.append(text(170, 110, "Чергування Si та Si₀.₇₅Ge₀.₂₅", size=10, bold=True, color="#004085"))

    # Етап 2: Формування ребра й фіктивного затвора
    frags.append(rect(340, 60, 280, 185, fill="#ffffff", stroke="#7f8c8d", sw=1.2, rx=4))
    tb_s2, _, _ = textbox(480, 75, "2. Фіктивний затвор (Dummy Gate)", size=11, bold=True, pad=4, fill="#e8ecf1")
    frags.append(tb_s2)

    frags.append(rect(360, 195, 240, 35, fill="#d0d7de", stroke="#6b7280", sw=1.2, rx=0))
    frags.append(rect(380, 125, 60, 70, fill="#d4edda", stroke="#27ae60", sw=1.2, rx=0))
    frags.append(text(410, 160, "Ребро\nSi/SiGe", size=9.5, color="#1e7e34"))

    frags.append(rect(450, 95, 60, 100, fill="#e2e3e5", stroke="#383d41", sw=1.4, rx=1))
    frags.append(text(480, 145, "Dummy\nGate", size=10, bold=True, color="#383d41"))

    frags.append(rect(520, 125, 60, 70, fill="#d4edda", stroke="#27ae60", sw=1.2, rx=0))
    frags.append(text(550, 160, "Ребро\nSi/SiGe", size=9.5, color="#1e7e34"))
    frags.append(text(480, 217, "Травлення ребра й маскування", size=9.5, color=INK))

    # Етап 3: Селективне травлення SiGe і внутрішні спейсери
    frags.append(rect(650, 60, 280, 185, fill="#ffffff", stroke="#7f8c8d", sw=1.2, rx=4))
    tb_s3, _, _ = textbox(790, 75, "3. Внутрішні спейсери (Inner Spacers)", size=11, bold=True, pad=4, fill="#e8ecf1")
    frags.append(tb_s3)

    frags.append(rect(670, 195, 240, 35, fill="#d0d7de", stroke="#6b7280", sw=1.2, rx=0))
    for i in range(3):
        y_pos = 175 - i * 25
        frags.append(rect(710, y_pos, 160, 10, fill="#d4edda", stroke="#27ae60", sw=1.2, rx=1))
        frags.append(rect(730, y_pos - 12, 20, 12, fill="#f8d7da", stroke="#721c24", sw=1.0, rx=1))
        frags.append(rect(830, y_pos - 12, 20, 12, fill="#f8d7da", stroke="#721c24", sw=1.0, rx=1))
    tb_sp_lbl, _, _ = textbox(790, 110, "Low-k спейсери SiBCN\nзахищають паразити C_gd/C_gs", size=9.5, color="#721c24", fill="#f8d7da", stroke="#721c24", pad=3)
    frags.append(tb_sp_lbl)
    frags.append(text(790, 217, "Бокове травлення SiGe + ALD low-k", size=9.5, color=INK))

    # Ряд 2: Етапи 4, 5, 6
    # Етап 4: Епітаксія витоку/стоку (Source/Drain)
    frags.append(rect(30, 265, 280, 195, fill="#ffffff", stroke="#7f8c8d", sw=1.2, rx=4))
    tb_s4, _, _ = textbox(170, 280, "4. Епітаксія витоку й стоку (S/D)", size=11, bold=True, pad=4, fill="#e8ecf1")
    frags.append(tb_s4)

    frags.append(rect(50, 410, 240, 35, fill="#d0d7de", stroke="#6b7280", sw=1.2, rx=0))
    frags.append(rect(60, 320, 60, 90, fill="#d4edda", stroke="#27ae60", sw=1.5, rx=4))
    frags.append(text(90, 365, "Витік\n(S)", size=10, bold=True, color="#1e7e34"))

    frags.append(rect(220, 320, 60, 90, fill="#d4edda", stroke="#27ae60", sw=1.5, rx=4))
    frags.append(text(250, 365, "Стік\n(D)", size=10, bold=True, color="#1e7e34"))

    frags.append(rect(130, 320, 80, 90, fill="#e2e3e5", stroke="#383d41", sw=1.2, rx=0))
    frags.append(text(170, 365, "Dummy\nGate", size=10, color="#383d41"))
    frags.append(text(170, 432, "In-situ легування Si:P (nMOS) / SiGe:B (pMOS)", size=9.5, color=INK))

    # Етап 5: Звільнення наношарів (Sheet Release)
    frags.append(rect(340, 265, 280, 195, fill="#ffffff", stroke="#7f8c8d", sw=1.2, rx=4))
    tb_s5, _, _ = textbox(480, 280, "5. Звільнення наношарів (Release)", size=11, bold=True, pad=4, fill="#e8ecf1")
    frags.append(tb_s5)

    frags.append(rect(360, 410, 240, 35, fill="#d0d7de", stroke="#6b7280", sw=1.2, rx=0))
    for i in range(3):
        y_pos = 390 - i * 25
        frags.append(rect(420, y_pos, 120, 10, fill="#d4edda", stroke="#27ae60", sw=1.4, rx=1))
    frags.append(rect(370, 320, 45, 90, fill="#d4edda", stroke="#27ae60", sw=1.2, rx=2))
    frags.append(rect(545, 320, 45, 90, fill="#d4edda", stroke="#27ae60", sw=1.2, rx=2))
    tb_rel, _, _ = textbox(480, 315, "Вибіркове травлення SiGe:\nвільно підвішені містки Si", size=9.5, color="#004085", fill="#cce5ff", stroke="#004085", pad=3)
    frags.append(tb_rel)
    frags.append(text(480, 432, "Селективність травлення SiGe:Si > 150:1", size=9.5, color=INK))

    # Етап 6: Нанесення кругового металевого затвора (RMG ALD)
    frags.append(rect(650, 265, 280, 195, fill="#ffffff", stroke="#7f8c8d", sw=1.2, rx=4))
    tb_s6, _, _ = textbox(790, 280, "6. Фінальний затвор HKMG (GAA)", size=11, bold=True, pad=4, fill="#e8ecf1")
    frags.append(tb_s6)

    frags.append(rect(670, 410, 240, 35, fill="#d0d7de", stroke="#6b7280", sw=1.2, rx=0))
    frags.append(rect(680, 320, 45, 90, fill="#d4edda", stroke="#27ae60", sw=1.2, rx=2))
    frags.append(rect(855, 320, 45, 90, fill="#d4edda", stroke="#27ae60", sw=1.2, rx=2))

    # Металевий затвор, що заповнює всі щілини
    frags.append(rect(730, 320, 120, 90, fill="#cce5ff", stroke="#004085", sw=1.5, rx=2))
    for i in range(3):
        y_pos = 390 - i * 25
        frags.append(rect(730, y_pos, 120, 10, fill="#d4edda", stroke="#27ae60", sw=1.2, rx=1))
    frags.append(text(790, 310, "ALD HfO₂ + метал затвора", size=9.5, bold=True, color="#004085"))
    frags.append(text(790, 432, "Повний 4-сторонній круговий затвор", size=9.5, bold=True, color="#1e7e34"))

    render(os.path.join(IMG, "gaafet-fabrication-flow.svg"), w, h, *frags)


def fig_frontside_vs_backside_power():
    w, h = 920, 430
    frags = []

    # Заголовки
    t_f, _, _ = textbox(230, 30, "Традиційне живлення (Frontside PDN)\nСигнали й шини живлення в одному стеку", size=12, bold=True, pad=6)
    frags.append(t_f)

    t_b, _, _ = textbox(690, 30, "Зворотна мережа (Backside PDN / PowerVia)\nРозділення: сигнали зверху, живлення знизу", size=12, bold=True, pad=6)
    frags.append(t_b)

    # ── Ліва частина: Frontside PDN ──
    # Металевий стек зверху (M0 .. M12)
    frags.append(rect(50, 70, 360, 160, fill="#fff3cd", stroke="#d39e00", sw=1.5, rx=2))
    frags.append(text(230, 92, "Верхній стек металізації (M0–M15)", size=11, bold=True, color="#856404"))

    # Провідники сигналів і живлення поруч у тисняві
    frags.append(rect(70, 110, 75, 25, fill="#d4edda", stroke="#27ae60", sw=1.2, rx=2))
    frags.append(text(107, 126, "Сигнал A", size=9.5, bold=True, color="#1e7e34"))

    frags.append(rect(155, 110, 70, 25, fill="#f8d7da", stroke=POS, sw=1.2, rx=2))
    frags.append(text(190, 126, "VDD (живл.)", size=9.5, bold=True, color=POS))

    frags.append(rect(235, 110, 75, 25, fill="#d4edda", stroke="#27ae60", sw=1.2, rx=2))
    frags.append(text(272, 126, "Сигнал B", size=9.5, bold=True, color="#1e7e34"))

    frags.append(rect(320, 110, 70, 25, fill="#cce5ff", stroke=NEG, sw=1.2, rx=2))
    frags.append(text(355, 126, "VSS (земля)", size=9.5, bold=True, color=NEG))

    tb_ir, _, _ = textbox(230, 175, "Тиснява доріжок + високий опір тонких M0/M1\nПадіння напруги IR-drop сягає 10–15% VDD", size=9.5, color=POS, fill="#ffffff", stroke=POS, pad=4)
    frags.append(tb_ir)

    # Шар транзисторів
    frags.append(rect(50, 240, 360, 60, fill="#d4edda", stroke="#27ae60", sw=1.5, rx=0))
    frags.append(text(230, 275, "Шар транзисторів GAAFET (кремній)", size=11, bold=True, color="#1e7e34"))

    # Масивна кремнієва підкладка знизу
    frags.append(rect(50, 310, 360, 50, fill="#e8ecf1", stroke="#7f8c8d", sw=1.5, rx=0))
    frags.append(text(230, 340, "Пасивна кремнієва підкладка (~700 мкм)", size=10, color=MUTED))

    tb_f_sum, _, _ = textbox(230, 395, "Втрати тактової частоти через шум живлення\nі конкуренцію за простір трасування", size=10, color=INK, fill="#f4f6f8", stroke=MUTED, pad=5)
    frags.append(tb_f_sum)

    # Розділювач
    frags.append(line(460, 20, 460, 420, color="#d0d7de", sw=1.5, dash="4,4"))

    # ── Права частина: Backside PDN ──
    # Верхній стек — 100% сигнали
    frags.append(rect(510, 70, 360, 110, fill="#d4edda", stroke="#27ae60", sw=1.5, rx=2))
    frags.append(text(690, 95, "Верхній стек: 100% чисте трасування сигналів", size=11, bold=True, color="#1e7e34"))
    frags.append(text(690, 120, "Немає шин VDD/VSS — вільні канали зв'язку", size=9.5, color="#1e7e34"))
    frags.append(text(690, 145, "Зменшення площі стандартної комірки на 15–20%", size=9.5, bold=True, color="#004085"))

    # Шар транзисторів посередині
    frags.append(rect(510, 190, 360, 60, fill="#cce5ff", stroke="#004085", sw=1.5, rx=0))
    frags.append(text(690, 225, "Шар транзисторів GAAFET (надтонкий Si)", size=11, bold=True, color="#004085"))

    # Nano-TSV переходи крізь зворотний бік
    frags.append(rect(580, 250, 36, 50, fill="#f8d7da", stroke=POS, sw=1.5, rx=0))
    frags.append(text(598, 278, "TSV", size=9.5, bold=True, color=POS))

    frags.append(rect(770, 250, 36, 50, fill="#cce5ff", stroke=NEG, sw=1.5, rx=0))
    frags.append(text(788, 278, "TSV", size=9.5, bold=True, color=NEG))

    # Зворотний товстий стек живлення
    frags.append(rect(510, 300, 360, 60, fill="#f4f6f8", stroke="#383d41", sw=1.5, rx=2))
    frags.append(rect(530, 315, 140, 30, fill="#f8d7da", stroke=POS, sw=1.5, rx=2))
    frags.append(text(600, 334, "Товста шина VDD (Backside)", size=9.5, bold=True, color=POS))

    frags.append(rect(700, 315, 150, 30, fill="#cce5ff", stroke=NEG, sw=1.5, rx=2))
    frags.append(text(775, 334, "Товста шина VSS (Backside)", size=9.5, bold=True, color=NEG))

    tb_b_sum, _, _ = textbox(690, 395, "Зниження IR-drop на 30–50%; ліквідація шумів;\nпрямий контакт із джерелом живлення через Nano-TSV", size=10, color="#1e7e34", fill="#d4edda", stroke="#27ae60", pad=5)
    frags.append(tb_b_sum)

    render(os.path.join(IMG, "frontside-vs-backside-power.svg"), w, h, *frags)


def fig_cfet_stacked_architecture():
    w, h = 880, 440
    frags = []

    # Заголовок
    tb_h, _, _ = textbox(440, 25, "Комплементарний FET (CFET): монолітне 3D-стекування nMOS над pMOS", size=13, bold=True, pad=6)
    frags.append(tb_h)

    # Ліва частина: Стандартний CMOS (nMOS і pMOS поруч)
    tb_c1, _, _ = textbox(220, 65, "Стандартний CMOS (GAAFET поруч)\nПлоща комірки обмежена ізоляцією STI", size=11, bold=True, pad=5)
    frags.append(tb_c1)

    # Підкладка STI
    frags.append(rect(40, 300, 360, 50, fill="#e8ecf1", stroke="#7f8c8d", sw=1.5, rx=0))
    frags.append(text(220, 330, "Спільна основа кристала", size=11, color=MUTED))

    # Стовпчик nMOS
    frags.append(rect(70, 150, 130, 150, fill="#d4edda", stroke="#27ae60", sw=1.5, rx=2))
    frags.append(text(135, 175, "nMOS GAAFET", size=11, bold=True, color="#1e7e34"))
    for i in range(3):
        frags.append(rect(85, 200 + i * 30, 100, 15, fill="#ffffff", stroke="#27ae60", sw=1.2, rx=1))
        frags.append(text(135, 212 + i * 30, "Si n-канал", size=9.5, color="#1e7e34"))

    # Ізоляція STI між ними
    frags.append(rect(205, 180, 30, 120, fill="#e2e3e5", stroke="#6c757d", sw=1.0, rx=0))
    frags.append(text(220, 245, "STI", size=9.5, color="#6c757d"))

    # Стовпчик pMOS
    frags.append(rect(240, 150, 130, 150, fill="#ffeeba", stroke="#d39e00", sw=1.5, rx=2))
    frags.append(text(305, 175, "pMOS GAAFET", size=11, bold=True, color="#856404"))
    for i in range(3):
        frags.append(rect(255, 200 + i * 30, 100, 15, fill="#ffffff", stroke="#d39e00", sw=1.2, rx=1))
        frags.append(text(305, 212 + i * 30, "SiGe p-канал", size=9.5, color="#856404"))

    tb_w_cmos, _, _ = textbox(220, 385, "Ширина комірки = W(nMOS) + W(pMOS) + W(STI)\nВисота стандартної комірки: 5.0–5.5T", size=9.5, color=INK, fill="#ffffff", stroke=MUTED, pad=4)
    frags.append(tb_w_cmos)

    # Розділювач
    frags.append(line(440, 50, 440, 420, color="#d0d7de", sw=1.5, dash="4,4"))

    # Права частина: CFET (стекування 3D)
    tb_c2, _, _ = textbox(660, 65, "CFET: nMOS над pMOS у єдиному стовпчику\nСкорочення площі комірки вдвічі (3.0–3.5T)", size=11, bold=True, pad=5)
    frags.append(tb_c2)

    frags.append(rect(510, 320, 300, 30, fill="#e8ecf1", stroke="#7f8c8d", sw=1.5, rx=0))
    frags.append(text(660, 340, "Основа кристала (Backside PDN)", size=10, color=MUTED))

    # Спільна рамка CFET стовпчика
    frags.append(rect(570, 105, 180, 215, fill="#f4f6f8", stroke="#004085", sw=1.8, rx=4))

    # Верхній поверх: nMOS (2 наношари)
    frags.append(rect(585, 115, 150, 85, fill="#d4edda", stroke="#27ae60", sw=1.4, rx=2))
    frags.append(text(660, 130, "Верхній ярус: nMOS", size=10, bold=True, color="#1e7e34"))
    for i in range(2):
        frags.append(rect(600, 142 + i * 22, 120, 14, fill="#ffffff", stroke="#27ae60", sw=1.2, rx=1))
        frags.append(text(660, 153 + i * 22, "Si наношар n-типу", size=9.5, color="#1e7e34"))

    # Середній діелектричний спейсер (ізоляція між ярусами)
    frags.append(rect(585, 205, 150, 18, fill="#f8d7da", stroke=POS, sw=1.2, rx=1))
    frags.append(text(660, 218, "Діелектричний розділювач (Middle Dielectric)", size=9.0, bold=True, color=POS))

    # Нижній поверх: pMOS (2 наношари)
    frags.append(rect(585, 228, 150, 85, fill="#ffeeba", stroke="#d39e00", sw=1.4, rx=2))
    frags.append(text(660, 243, "Нижній ярус: pMOS", size=10, bold=True, color="#856404"))
    for i in range(2):
        frags.append(rect(600, 255 + i * 22, 120, 14, fill="#ffffff", stroke="#d39e00", sw=1.2, rx=1))
        frags.append(text(660, 266 + i * 22, "SiGe наношар p-типу", size=9.5, color="#856404"))

    # Підсумок CFET
    frags.append(text(660, 395, "Спільний або розділений вертикальний затвор для обох ярусів\nЕкономія площі логіки до 50% без втрати струму Id", size=9.5, bold=True, color="#004085"))

    render(os.path.join(IMG, "cfet-stacked-architecture.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_planar_vs_finfet_vs_gaafet()
    fig_gaafet_fabrication_flow()
    fig_frontside_vs_backside_power()
    fig_cfet_stacked_architecture()
    print("Всі фігури згенеровано успішно.")
