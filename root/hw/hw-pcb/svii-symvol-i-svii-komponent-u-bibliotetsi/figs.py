# -*- coding: utf-8 -*-
"""Фігури до теми «Свій символ і свій компонент у бібліотеці» (root/hw/hw-pcb).
Дві фігури:
  atomic-component-structure.svg — чотири стовпи атомарного компонента (символ, футпринт, 3D STEP, BOM-атрибути)
  sot23-pin-mapping.svg          — схема Pin-to-Pad маппінгу для SOT-23 / діодів і пастка нумерації

Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# 1. atomic-component-structure.svg — Будова атомарного бібліотечного компонента
# ════════════════════════════════════════════════════════════════════════════
def fig_atomic_structure():
    W, H = 840, 440
    f = []

    f.append(text(W / 2, 30, "Атомарний компонент бібліотеки (Atomic Library Component)", size=16, bold=True))
    f.append(text(W / 2, 50, "Єдина неподільна сутність: неможливо вставити символ без прив'язаного корпусу й точного MPN", size=12, color=MUTED))

    # Центральне ядро — MPN / Унікальний ідентифікатор
    core_cx, core_cy = W / 2, 170
    core_w, core_h = 240, 70
    f.append(rect(core_cx - core_w / 2, core_cy - core_h / 2, core_w, core_h, fill="#eef7f0", stroke=FIELD, sw=2.4, rx=10))
    f.append(text(core_cx, core_cy - 12, "АРТИКУЛ ВИРОБНИКА (MPN)", size=12, bold=True, color=FIELD))
    f.append(text(core_cx, core_cy + 8, "STM32F401RET6 / 2N7002", size=13, bold=True, color=INK))
    f.append(text(core_cx, core_cy + 24, "Єдиний ключ бази даних", size=10, color=MUTED))

    # 4 сутності довкола
    # 1. Схемний символ (зліва вгорі)
    b1_x, b1_y, b1_w, b1_h = 40, 90, 230, 150
    f.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#ffffff", stroke=NEG, sw=1.8, rx=8))
    f.append(text(b1_x + b1_w / 2, b1_y + 24, "1. СХЕМНИЙ СИМВОЛ", size=12, bold=True, color=NEG))
    f.append(mtext(b1_x + b1_w / 2, b1_y + 48, [
        "• Логічні лінії та порти",
        "• Функційне групування пінів",
        "• Електричні типи (In, Out, Pwr)",
        "• Полярність (Active Low, ~RESET)"
    ], size=11, color=INK, lh=1.35))

    # 2. Посадкове місце (Footprint) (справа вгорі)
    b2_x, b2_y, b2_w, b2_h = 570, 90, 230, 150
    f.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#ffffff", stroke=POS, sw=1.8, rx=8))
    f.append(text(b2_x + b2_w / 2, b2_y + 24, "2. ПОСАДКОВЕ МІСЦЕ", size=12, bold=True, color=POS))
    f.append(mtext(b2_x + b2_w / 2, b2_y + 48, [
        "• Контактні площадки (Pads)",
        "• Маска та паста (Mask/Paste)",
        "• Шовкографія та полярність (Pin 1)",
        "• Межа дворика (Courtyard IPC)"
    ], size=11, color=INK, lh=1.35))

    # 3. 3D-модель (STEP) (зліва внизу)
    b3_x, b3_y, b3_w, b3_h = 40, 270, 230, 140
    f.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#ffffff", stroke=LINE, sw=1.8, rx=8))
    f.append(text(b3_x + b3_w / 2, b3_y + 24, "3. 3D-МОДЕЛЬ (STEP)", size=12, bold=True, color=LINE))
    f.append(mtext(b3_x + b3_w / 2, b3_y + 48, [
        "• Точні просторові габарити",
        "• Перевірка кліренсу з корпусом",
        "• Центрування відносно посадки",
        "• Тепловий та механічний аналіз"
    ], size=11, color=INK, lh=1.35))

    # 4. Атрибути BOM / ERP (справа внизу)
    b4_x, b4_y, b4_w, b4_h = 570, 270, 230, 140
    f.append(rect(b4_x, b4_y, b4_w, b4_h, fill="#ffffff", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(b4_x + b4_w / 2, b4_y + 24, "4. АТРИБУТИ BOM ТА ERP", size=12, bold=True, color=FIELD))
    f.append(mtext(b4_x + b4_w / 2, b4_y + 48, [
        "• Виробник та повний артикул",
        "• Номінал, точність, напруга",
        "• Пряме посилання на Datasheet",
        "• Статус життєвого циклу / RoHS"
    ], size=11, color=INK, lh=1.35))

    # Стрілки зв'язку ядра з блоками
    f.append(arrow(core_cx - core_w / 2, core_cy - 15, b1_x + b1_w, b1_y + b1_h / 2, color=NEG, sw=2))
    f.append(arrow(core_cx + core_w / 2, core_cy - 15, b2_x, b2_y + b2_h / 2, color=POS, sw=2))
    f.append(arrow(core_cx - core_w / 2, core_cy + 15, b1_x + b1_w, b3_y + b3_h / 2, color=LINE, sw=2))
    f.append(arrow(core_cx + core_w / 2, core_cy + 15, b2_x, b4_y + b4_h / 2, color=FIELD, sw=2))

    # Нижній висновок
    f.append(rect(290, 290, 260, 100, fill="#fdf0ea", stroke=POS, sw=1.6, rx=8))
    f.append(text(420, 314, "ЗАБОРОНА «generic» СИМВОЛІВ", size=11, bold=True, color=POS))
    f.append(mtext(420, 334, [
        "Символ без точного посадкового",
        "місця або без MPN блокується",
        "автоматичним валідатором"
    ], size=11, color=INK, lh=1.3))

    render(os.path.join(IMG, "atomic-component-structure.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. sot23-pin-mapping.svg — Pin-to-Pad маппінг та пастка розпіновки SOT-23
# ════════════════════════════════════════════════════════════════════════════
def fig_sot23_pin_mapping():
    W, H = 840, 430
    f = []

    f.append(text(W / 2, 28, "Зіставлення виводів символу і контактних площадок (Pin-to-Pad Mapping)", size=16, bold=True))
    f.append(text(W / 2, 48, "Як логічні виводи схеми пов'язуються з фізичними площадками корпусу SOT-23", size=12, color=MUTED))

    # Секція 1: Схемний символ (N-канальний MOSFET)
    sx, sy, sw, sh = 40, 80, 210, 310
    f.append(rect(sx, sy, sw, sh, fill="#ffffff", stroke=NEG, sw=1.8, rx=8))
    f.append(text(sx + sw / 2, sy + 24, "СХЕМНИЙ СИМВОЛ", size=12, bold=True, color=NEG))
    f.append(text(sx + sw / 2, sy + 42, "Логічні виводи транзистора", size=10, color=MUTED))

    # Візуалізація пінів символу
    # Gate
    f.append(rect(sx + 20, sy + 70, 170, 45, fill="#f4f6f8", stroke=NEG, sw=1.2, rx=4))
    f.append(text(sx + 40, sy + 97, "Pin 1", size=12, bold=True, color=NEG))
    f.append(text(sx + 120, sy + 97, "Gate (Затвор)", size=11, bold=True, color=INK))

    # Source
    f.append(rect(sx + 20, sy + 135, 170, 45, fill="#f4f6f8", stroke=NEG, sw=1.2, rx=4))
    f.append(text(sx + 40, sy + 162, "Pin 2", size=12, bold=True, color=NEG))
    f.append(text(sx + 120, sy + 162, "Source (Витік)", size=11, bold=True, color=INK))

    # Drain
    f.append(rect(sx + 20, sy + 200, 170, 45, fill="#f4f6f8", stroke=NEG, sw=1.2, rx=4))
    f.append(text(sx + 40, sy + 227, "Pin 3", size=12, bold=True, color=NEG))
    f.append(text(sx + 120, sy + 227, "Drain (Стік)", size=11, bold=True, color=INK))

    f.append(mtext(sx + sw / 2, sy + 270, [
        "Номери в бібліотеці:",
        "1 -> G, 2 -> S, 3 -> D"
    ], size=11, color=MUTED, lh=1.3))

    # Секція 2: Таблиця маппінгу в CAD (Netlist Bridge)
    mx, my, mw, mh = 290, 80, 240, 310
    f.append(rect(mx, my, mw, mh, fill="#ffffff", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(mx + mw / 2, my + 24, "ТАБЛИЦЯ СПІВВІДНОШЕННЯ", size=12, bold=True, color=FIELD))
    f.append(text(mx + mw / 2, my + 42, "Pin-to-Pad Mapping", size=10, color=MUTED))

    # Рядки таблиці
    f.append(rect(mx + 15, my + 65, 210, 40, fill="#eef7f0", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(mx + mw / 2, my + 90, "Symbol Pin 1 (G)  ==  Pad 1", size=11, bold=True, color=FIELD))

    f.append(rect(mx + 15, my + 115, 210, 40, fill="#eef7f0", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(mx + mw / 2, my + 140, "Symbol Pin 2 (S)  ==  Pad 2", size=11, bold=True, color=FIELD))

    f.append(rect(mx + 15, my + 165, 210, 40, fill="#eef7f0", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(mx + mw / 2, my + 190, "Symbol Pin 3 (D)  ==  Pad 3", size=11, bold=True, color=FIELD))

    # Попередження про пастку виробників
    f.append(rect(mx + 15, my + 220, 210, 75, fill="#fdf0ea", stroke=POS, sw=1.4, rx=6))
    f.append(text(mx + mw / 2, my + 240, "ПАСТКА ВИРОБНИКІВ:", size=11, bold=True, color=POS))
    f.append(mtext(mx + mw / 2, my + 258, [
        "У транзистора 2N7002: 1-G, 2-S, 3-D",
        "А в BJT BC847: 1-Base, 2-Emitter, 3-Coll",
        "У діода BAT54: 1-Anode, 3-Cathode (2-NC)"
    ], size=9, color=INK, lh=1.25))

    # Секція 3: Фізичний корпус SOT-23 (Footprint Top View)
    fx, fy, fw, fh = 570, 80, 230, 310
    f.append(rect(fx, fy, fw, fh, fill="#ffffff", stroke=POS, sw=1.8, rx=8))
    f.append(text(fx + fw / 2, fy + 24, "ФІЗИЧНИЙ SOT-23", size=12, bold=True, color=POS))
    f.append(text(fx + fw / 2, fy + 42, "Вигляд згори (Top View)", size=10, color=MUTED))

    # Малюнок корпусу SOT-23
    cx, cy = fx + fw / 2, fy + 160
    # Тіло корпусу
    f.append(rect(cx - 45, cy - 35, 90, 70, fill="#2b2b2b", stroke="#111111", sw=1.5, rx=3))
    f.append(text(cx, cy + 4, "SOT-23", size=11, bold=True, color="#ffffff"))

    # Площадка 1 (Gate / ліворуч знизу)
    p1_x, p1_y = cx - 35, cy + 45
    f.append(rect(p1_x - 14, p1_y - 8, 28, 22, fill="#e67e22", stroke="#b95e09", sw=1.5, rx=2))
    f.append(text(p1_x, p1_y + 7, "1", size=11, bold=True, color="#ffffff"))
    f.append(text(p1_x - 28, p1_y + 7, "Pad 1", size=10, bold=True, color=POS))

    # Площадка 2 (Source / праворуч знизу)
    p2_x, p2_y = cx + 35, cy + 45
    f.append(rect(p2_x - 14, p2_y - 8, 28, 22, fill="#e67e22", stroke="#b95e09", sw=1.5, rx=2))
    f.append(text(p2_x, p2_y + 7, "2", size=11, bold=True, color="#ffffff"))
    f.append(text(p2_x + 28, p2_y + 7, "Pad 2", size=10, bold=True, color=POS))

    # Площадка 3 (Drain / по центру зверху)
    p3_x, p3_y = cx, cy - 58
    f.append(rect(p3_x - 14, p3_y - 8, 28, 22, fill="#e67e22", stroke="#b95e09", sw=1.5, rx=2))
    f.append(text(p3_x, p3_y + 7, "3", size=11, bold=True, color="#ffffff"))
    f.append(text(p3_x, p3_y - 14, "Pad 3", size=10, bold=True, color=POS))

    f.append(mtext(fx + fw / 2, fy + 265, [
        "Несумісність нумерації",
        "призводить до інверсії сигналів",
        "або короткого замикання"
    ], size=11, color=MUTED, lh=1.3))

    # З'єднувальні стрілки між блоками
    f.append(arrow(sx + sw + 5, sy + 92, mx - 5, my + 85, color=NEG, sw=1.8))
    f.append(arrow(sx + sw + 5, sy + 157, mx - 5, my + 135, color=NEG, sw=1.8))
    f.append(arrow(sx + sw + 5, sy + 222, mx - 5, my + 185, color=NEG, sw=1.8))

    f.append(arrow(mx + mw + 5, my + 85, fx - 5, fy + 160, color=POS, sw=1.8))

    render(os.path.join(IMG, "sot23-pin-mapping.svg"), W, H, *f)


if __name__ == "__main__":
    fig_atomic_structure()
    fig_sot23_pin_mapping()
    print("Figures generated successfully in", IMG)
