# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Класи ізоляції та шляхи витоку: Creepage і Clearance»."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_creepage_vs_clearance():
    """Фігура 1: Порівняння шляху витоку (Creepage) вздовж поверхні та повітряного зазору (Clearance)."""
    w, h = 820, 420
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Геометрія ізоляції: повітряний зазор (Clearance) проти шляху витоку (Creepage)", size=16, bold=True))

    # Ліва панель: плоска плата
    frags.append(rect(40, 60, 350, 330, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(215, 88, "Плоска поверхня діелектрика", size=15, bold=True))

    # Текстоліт (діелектрик)
    frags.append(rect(60, 240, 310, 80, fill="#dcfce7", stroke="#16a34a", sw=2, rx=4))
    frags.append(text(215, 285, "Текстоліт FR-4 (діелектрик)", size=13, color="#15803d", bold=True))

    # Провідник 1 (Primary / High Voltage)
    frags.append(rect(80, 200, 70, 40, fill="#fee2e2", stroke=POS, sw=2, rx=3))
    frags.append(text(115, 225, "L / +325 В", size=12, color=POS, bold=True))
    frags.append(text(115, 185, "Провідник 1", size=11, color=MUTED))

    # Провідник 2 (Secondary / Low Voltage)
    frags.append(rect(280, 200, 70, 40, fill="#dbeafe", stroke=NEG, sw=2, rx=3))
    frags.append(text(315, 225, "SELV / 0 В", size=12, color=NEG, bold=True))
    frags.append(text(315, 185, "Провідник 2", size=11, color=MUTED))

    # Clearance (пряма лінія у повітрі)
    frags.append(line(150, 210, 280, 210, color="#dc2626", sw=2, dash="5,4"))
    frags.append(arrow(150, 210, 275, 210, color="#dc2626", sw=2))
    frags.append(arrow(280, 210, 155, 210, color="#dc2626", sw=2))
    b1, _, _ = textbox(215, 140, "Clearance (повітря)\nНайкоротша пряма крізь повітря", size=11, fill="#fff1f2", stroke="#f43f5e", color="#9f1239")
    frags.append(b1)

    # Creepage (вздовж поверхні)
    frags.append(line(150, 243, 280, 243, color="#0284c7", sw=2.5))
    b2, _, _ = textbox(215, 355, "Creepage = Clearance\n(на плоскій платі шляхи рівні)", size=11, fill="#f0f9ff", stroke="#0284c7", color="#0369a1")
    frags.append(b2)

    # Права панель: плата з ізоляційним ребром / пропилом
    frags.append(rect(430, 60, 350, 330, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(605, 88, "Поверхня з ребром або пазом", size=15, bold=True))

    # Текстоліт з ребром
    # Базова основа
    frags.append(rect(450, 240, 310, 80, fill="#dcfce7", stroke="#16a34a", sw=2, rx=4))
    # Вертикальне ребро посередині
    frags.append(rect(590, 160, 30, 80, fill="#bbf7d0", stroke="#16a34a", sw=2, rx=2))
    frags.append(text(605, 285, "Діелектричний бар'єр (ребро)", size=12, color="#15803d", bold=True))

    # Провідник 1
    frags.append(rect(470, 200, 70, 40, fill="#fee2e2", stroke=POS, sw=2, rx=3))
    frags.append(text(505, 225, "L / +325 В", size=12, color=POS, bold=True))

    # Провідник 2
    frags.append(rect(670, 200, 70, 40, fill="#dbeafe", stroke=NEG, sw=2, rx=3))
    frags.append(text(705, 225, "SELV / 0 В", size=12, color=NEG, bold=True))

    # Clearance (перелітає через ребро по прямій над ребром)
    frags.append(line(540, 150, 670, 150, color="#dc2626", sw=2, dash="5,4"))
    frags.append(arrow(540, 150, 665, 150, color="#dc2626", sw=2))
    frags.append(arrow(670, 150, 545, 150, color="#dc2626", sw=2))
    b3, _, _ = textbox(605, 125, "Clearance (пряма лінія над ребром)", size=11, fill="#fff1f2", stroke="#f43f5e", color="#9f1239")
    frags.append(b3)

    # Creepage (обходить ребро вгору і вниз по контуру)
    frags.append('<path d="M 540 242 L 590 242 L 590 160 L 620 160 L 620 242 L 670 242" fill="none" stroke="#0284c7" stroke-width="2.8" stroke-linejoin="round"/>')
    b4, _, _ = textbox(605, 355, "Creepage ЗРОСТАЄ:\nШлях огинає всі вигини поверхні!", size=11, fill="#f0f9ff", stroke="#0284c7", color="#0369a1", bold=True)
    frags.append(b4)

    render(os.path.join(IMG_DIR, "creepage-vs-clearance.svg"), w, h, *frags)


def fig_insulation_levels():
    """Фігура 2: Ієрархія рівнів ізоляції та класи приладів (Class I, II, III)."""
    w, h = 840, 460
    frags = []

    frags.append(text(w / 2, 28, "Класи захисту приладів та рівні ізоляції за стандартами безпеки", size=16, bold=True))

    # Колонки для трьох класів
    col_w = 240
    gap = 20

    # 1. Class I
    x1 = 35
    frags.append(rect(x1, 60, col_w, 375, fill="#fffbeb", stroke="#d97706", sw=1.8, rx=8))
    frags.append(text(x1 + col_w / 2, 90, "Клас I (Class I)", size=15, color="#92400e", bold=True))
    frags.append(text(x1 + col_w / 2, 112, "Захисне заземлення PE", size=12, color=MUTED))

    box1, _, _ = textbox(x1 + col_w / 2, 160, "Базова ізоляція\n(Basic Insulation)", size=12, fill="#fef3c7", stroke="#d97706", color="#78350f", bold=True)
    frags.append(box1)

    box1_pe, _, _ = textbox(x1 + col_w / 2, 230, "Захисне заземлення (PE)\nЗ'єднує металевий корпус із землею", size=11, fill="#ecfdf5", stroke="#059669", color="#065f46")
    frags.append(box1_pe)

    box1_mech, _, _ = textbox(x1 + col_w / 2, 335, "Механізм захисту:\nПробій ізоляції → КЗ на корпус →\nструм у PE → спрацьовує\nавтомат або ПЗВ (RCD).\n3-контактна вилка із землею.", size=11, fill="#ffffff", stroke="#cbd5e1", color=INK)
    frags.append(box1_mech)

    # 2. Class II
    x2 = x1 + col_w + gap
    frags.append(rect(x2, 60, col_w, 375, fill="#eff6ff", stroke="#2563eb", sw=1.8, rx=8))
    frags.append(text(x2 + col_w / 2, 90, "Клас II (Class II)", size=15, color="#1e40af", bold=True))
    frags.append(text(x2 + col_w / 2, 112, "Символ: подвійний квадрат ⧈", size=12, color=MUTED))

    box2_1, _, _ = textbox(x2 + col_w / 2, 152, "Базова ізоляція (Basic)", size=11, fill="#dbeafe", stroke="#3b82f6", color="#1e3a8a")
    frags.append(box2_1)
    frags.append(text(x2 + col_w / 2, 178, "+", size=14, color="#2563eb", bold=True))
    box2_2, _, _ = textbox(x2 + col_w / 2, 204, "Додаткова ізоляція (Suppl.)", size=11, fill="#dbeafe", stroke="#3b82f6", color="#1e3a8a")
    frags.append(box2_2)

    box2_reinf, _, _ = textbox(x2 + col_w / 2, 252, "АБО Посилена (Reinforced)", size=12, fill="#bfdbfe", stroke="#1d4ed8", color="#1e3a8a", bold=True)
    frags.append(box2_reinf)

    box2_mech, _, _ = textbox(x2 + col_w / 2, 345, "Механізм захисту:\nДва незалежні бар'єри захисту.\nОдин відмовляє — другий захищає.\nЗаземлення НЕ потрібне.\n2-контактна вилка (Europlug).", size=11, fill="#ffffff", stroke="#cbd5e1", color=INK)
    frags.append(box2_mech)

    # 3. Class III
    x3 = x2 + col_w + gap
    frags.append(rect(x3, 60, col_w, 375, fill="#f0fdf4", stroke="#16a34a", sw=1.8, rx=8))
    frags.append(text(x3 + col_w / 2, 90, "Клас III (Class III)", size=15, color="#166534", bold=True))
    frags.append(text(x3 + col_w / 2, 112, "Безпечна низька напруга", size=12, color=MUTED))

    box3_selv, _, _ = textbox(x3 + col_w / 2, 160, "Живлення SELV / PELV\nU ≤ 60 В DC / 25 В AC RMS", size=12, fill="#dcfce7", stroke="#16a34a", color="#14532d", bold=True)
    frags.append(box3_selv)

    box3_int, _, _ = textbox(x3 + col_w / 2, 230, "Жодних високих напруг\nусередині приладу", size=11, fill="#f0fdf4", stroke="#86efac", color="#166534")
    frags.append(box3_int)

    box3_mech, _, _ = textbox(x3 + col_w / 2, 335, "Механізм захисту:\nНапруга фізично нездатна\nпробити суху шкіру людини\nта викликати небезпечний струм.\nЖивиться від зовнішнього БЖ.", size=11, fill="#ffffff", stroke="#cbd5e1", color=INK)
    frags.append(box3_mech)

    render(os.path.join(IMG_DIR, "insulation-levels.svg"), w, h, *frags)


def fig_pcb_slot_milling():
    """Фігура 3: Ізоляційний пропил на друкованій платі під оптопарою."""
    w, h = 820, 440
    frags = []

    frags.append(text(w / 2, 28, "Ізоляційний пропил (Isolation Slot) на платі під бар'єрним компонентом", size=16, bold=True))

    # Фон плати FR-4
    frags.append(rect(40, 60, 740, 350, fill="#1e3a1e", stroke="#14532d", sw=2, rx=8))
    frags.append(text(120, 88, "Друкована плата (FR-4)", size=13, color="#86efac", bold=True))

    # Первинна зона (High Voltage) - мідний полігон
    frags.append(rect(60, 110, 220, 270, fill="#7f1d1d", stroke="#ef4444", sw=1.5, rx=4))
    frags.append(text(170, 140, "Гаряча зона (Primary)", size=14, color="#fca5a5", bold=True))
    frags.append(text(170, 160, "Мережа ~230 В / +325 В DC", size=12, color="#fecaca"))

    # Вторинна зона (SELV / Low Voltage) - мідний полігон
    frags.append(rect(540, 110, 220, 270, fill="#1e3a8a", stroke="#3b82f6", sw=1.5, rx=4))
    frags.append(text(650, 140, "Холодна зона (Secondary)", size=14, color="#93c5fd", bold=True))
    frags.append(text(650, 160, "SELV +5 В / +3.3 В / GND", size=12, color="#bfdbfe"))

    # Зона розділення (ізоляційний бар'єр без міді)
    frags.append(text(410, 115, "Бар'єр ізоляції (без міді)", size=12, color="#cbd5e1", bold=True))

    # Ізоляційний пропил (верхня і нижня частини пазу, що виходять з-під корпусу)
    frags.append(rect(395, 130, 30, 50, fill="#0f172a", stroke="#e2e8f0", sw=2, rx=6))
    frags.append(rect(395, 300, 30, 70, fill="#0f172a", stroke="#e2e8f0", sw=2, rx=6))
    frags.append(text(410, 385, "Пропил (Slot)", size=12, color="#f8fafc", bold=True))
    frags.append(text(410, 403, "Ширина ≥ 1.0 мм", size=11, color="#38bdf8"))

    # Оптопара, перекинута через пропил
    frags.append(rect(340, 185, 140, 110, fill="#18181b", stroke="#71717a", sw=2, rx=4))
    frags.append(text(410, 235, "Оптопара", size=13, color="#f4f4f5", bold=True))
    frags.append(text(410, 255, "(напр. PC817 / DIP-4)", size=10, color="#a1a1aa"))

    # Виводи оптопари (лінії)
    frags.append(line(300, 210, 340, 210, color="#d4d4d8", sw=4))
    frags.append(line(300, 270, 340, 270, color="#d4d4d8", sw=4))
    frags.append(line(480, 210, 520, 210, color="#d4d4d8", sw=4))
    frags.append(line(480, 270, 520, 270, color="#d4d4d8", sw=4))

    # Контактні площадки (Pads)
    frags.append(circle(290, 210, 7, fill="#f59e0b", stroke="#d97706", sw=1.5))
    frags.append(circle(290, 270, 7, fill="#f59e0b", stroke="#d97706", sw=1.5))
    frags.append(circle(530, 210, 7, fill="#f59e0b", stroke="#d97706", sw=1.5))
    frags.append(circle(530, 270, 7, fill="#f59e0b", stroke="#d97706", sw=1.5))

    # Стрілка шляху витоку (Creepage), що змушений обходити пропил навколо
    frags.append('<path d="M 290 280 C 290 375, 370 375, 410 375 C 450 375, 530 375, 530 280" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="6,4"/>')
    b_creep, _, _ = textbox(170, 335, "Шлях витоку (Creepage)\nзмушений обходити паз,\nзростаючи з 4 мм до > 8 мм!", size=10, fill="#f0f9ff", stroke="#0284c7", color="#0369a1")
    frags.append(b_creep)

    # Стрілка повітряного зазору (Clearance) прямо між виводами
    frags.append(line(300, 210, 520, 210, color="#f87171", sw=2, dash="4,3"))
    frags.append(arrow(300, 210, 515, 210, color="#f87171", sw=2))
    frags.append(arrow(520, 210, 305, 210, color="#f87171", sw=2))
    b_clear, _, _ = textbox(650, 335, "Повітряний зазор (Clearance)\nпряма відстань між ніжками\nчерез корпус і повітря", size=10, fill="#fef2f2", stroke="#ef4444", color="#991b1b")
    frags.append(b_clear)

    render(os.path.join(IMG_DIR, "pcb-slot-milling.svg"), w, h, *frags)


def fig_transformer_insulation():
    """Фігура 4: Конструкція захисної ізоляції мережевого трансформатора: Margin Tape проти TIW та екран Фарадея."""
    w, h = 840, 440
    frags = []

    frags.append(text(w / 2, 28, "Конструкція безпечної ізоляції мережевого трансформатора", size=16, bold=True))

    # Ліва частина: Класичний трансформатор із захисною стрічкою (Margin Tape)
    frags.append(rect(35, 60, 365, 355, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(217, 88, "Класична обмотка з Margin Tape", size=14, bold=True))

    # Каркас котушки (Bobbin верх і низ)
    frags.append(rect(55, 115, 325, 20, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))
    frags.append(rect(55, 265, 325, 20, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))

    # Феритове осердя по центру
    frags.append(rect(202, 100, 30, 200, fill="#334155", stroke="#0f172a", sw=2, rx=2))
    frags.append(text(217, 205, "Ферит", size=10, color="#f8fafc", bold=True))

    # Margin Tape ліворуч і праворуч (жовті стовпчики)
    frags.append(rect(58, 138, 40, 124, fill="#fef08a", stroke="#ca8a04", sw=1.5))
    frags.append(rect(337, 138, 40, 124, fill="#fef08a", stroke="#ca8a04", sw=1.5))
    frags.append(text(78, 200, "3 мм", size=10, color="#854d0e", bold=True))
    frags.append(text(357, 200, "3 мм", size=10, color="#854d0e", bold=True))

    # Первинна обмотка (Primary, червона)
    frags.append(rect(102, 140, 96, 50, fill="#fee2e2", stroke=POS, sw=1.5))
    frags.append(rect(236, 140, 97, 50, fill="#fee2e2", stroke=POS, sw=1.5))
    frags.append(text(150, 170, "Первинна", size=11, color=POS, bold=True))
    frags.append(text(285, 170, "Первинна", size=11, color=POS, bold=True))

    # Міжобмоткова ізоляція (3 шари стрічки)
    frags.append(line(102, 195, 333, 195, color="#eab308", sw=3))

    # Вторинна обмотка (Secondary, синя)
    frags.append(rect(102, 202, 96, 50, fill="#dbeafe", stroke=NEG, sw=1.5))
    frags.append(rect(236, 202, 97, 50, fill="#dbeafe", stroke=NEG, sw=1.5))
    frags.append(text(150, 232, "Вторинна", size=11, color=NEG, bold=True))
    frags.append(text(285, 232, "Вторинна", size=11, color=NEG, bold=True))

    b_left, _, _ = textbox(217, 355, "Margin Tape: крайові бар'єри по 3 мм з боків\nзабезпечують 6 мм Creepage між обмотками.\nМінус: втрата 30-40% вікна намотки.", size=11, fill="#fefce8", stroke="#eab308", color="#713f12")
    frags.append(b_left)

    # Права частина: Потрійно ізольований дріт (TIW) + екран Фарадея
    frags.append(rect(440, 60, 365, 355, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(622, 88, "Потрійна ізоляція (TIW) + Екран", size=14, bold=True))

    # Каркас котушки верх і низ
    frags.append(rect(460, 115, 325, 20, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))
    frags.append(rect(460, 265, 325, 20, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=3))

    # Феритове осердя
    frags.append(rect(607, 100, 30, 200, fill="#334155", stroke="#0f172a", sw=2, rx=2))
    frags.append(text(622, 205, "Ферит", size=10, color="#f8fafc", bold=True))

    # Первинна обмотка на всю ширину каркаса
    frags.append(rect(463, 140, 140, 42, fill="#fee2e2", stroke=POS, sw=1.5))
    frags.append(rect(641, 140, 140, 42, fill="#fee2e2", stroke=POS, sw=1.5))
    frags.append(text(533, 165, "Первинна (100% ширини)", size=10, color=POS, bold=True))
    frags.append(text(711, 165, "Первинна (100% ширини)", size=10, color=POS, bold=True))

    # Електростатичний екран (мідна фольга / екран Фарадея)
    frags.append(line(463, 192, 781, 192, color="#64748b", sw=2.5, dash="6,3"))
    frags.append(text(533, 202, "Екран Фарадея (EMI)", size=9, color=MUTED))

    # Вторинна обмотка TIW (Triple Insulated Wire)
    frags.append(rect(463, 210, 140, 45, fill="#dcfce7", stroke="#16a34a", sw=2))
    frags.append(rect(641, 210, 140, 45, fill="#dcfce7", stroke="#16a34a", sw=2))
    frags.append(text(533, 236, "TIW Вторинна (3 шари)", size=10, color="#15803d", bold=True))
    frags.append(text(711, 236, "TIW Вторинна (3 шари)", size=10, color="#15803d", bold=True))

    b_right, _, _ = textbox(622, 355, "TIW: 3 незалежні екструдовані шари ізоляції.\nКрайові стрічки НЕ потрібні (0 мм Margin)!\n100% вікна каркаса, мінімальна L_витоку.", size=11, fill="#f0fdf4", stroke="#16a34a", color="#14532d", bold=True)
    frags.append(b_right)

    render(os.path.join(IMG_DIR, "transformer-insulation.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_creepage_vs_clearance()
    fig_insulation_levels()
    fig_pcb_slot_milling()
    fig_transformer_insulation()
    print("All figures generated successfully.")
