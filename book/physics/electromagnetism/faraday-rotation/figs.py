# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Фарадеєвське обертання» (faraday-rotation)."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")

def generate_faraday_concept():
    """Фігура 1: Схема Фарадеєвського обертання світла в магнітному полі."""
    w, h = 800, 320
    out = []
    out.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    
    # Заголовок / рамка контексту
    out.append(rect(15, 15, 770, 290, fill="#fdfdfd", stroke="#d0d7de", sw=1, rx=8))
    
    # Оптична вісь (промінь світла)
    out.append(line(50, 160, 750, 160, color=MUTED, sw=1.5, dash="6,4"))
    out.append(arrow(50, 160, 740, 160, color=MUTED, sw=1.5))
    
    # 1. Вхідна лінійна поляризація (0 градусів - вертикальна)
    b1, _, _ = textbox(110, 75, "Вхідний промінь\n(вертикальна поляризація)", size=12, pad=6, fill="#eef6ff", stroke=NEG)
    out.append(b1)
    # Візуалізація вектора E0 (вертикальні стрілки)
    out.append(line(110, 120, 110, 200, color=NEG, sw=2.5))
    out.append(arrow(110, 160, 110, 115, color=NEG, sw=2))
    out.append(arrow(110, 160, 110, 205, color=NEG, sw=2))
    out.append(text(110, 220, "E₀ (0°)", size=13, color=NEG, bold=True))
    
    # 2. Магнітооптичний кристал та соленоїд
    # Кришталевий блок
    out.append(rect(240, 100, 280, 120, fill="#e8f4f8", stroke="#2c3e50", sw=2, rx=4))
    b_mat, _, _ = textbox(380, 130, "Магнітооптичне середовище (L)", size=13, pad=4, fill="#ffffff", stroke="#2c3e50", bold=True)
    out.append(b_mat)
    
    # Витки соленоїда довкола середовища
    for x_coil in range(255, 510, 35):
        out.append(line(x_coil, 90, x_coil + 15, 100, color=POS, sw=3))
        out.append(line(x_coil, 220, x_coil + 15, 230, color=POS, sw=3))
    
    # Вектор магнітного поля B (зелений)
    out.append(line(220, 160, 540, 160, color=FIELD, sw=3))
    out.append(arrow(220, 160, 535, 160, color=FIELD, sw=3))
    out.append(text(380, 185, "Поздовжнє магнітне поле B ➔", size=14, color=FIELD, bold=True))
    
    # 3. Вихідна лінійна поляризація (повернута на кут theta)
    b2, _, _ = textbox(670, 75, "Вихідний промінь\n(повернута поляризація)", size=12, pad=6, fill="#fff5ee", stroke=POS)
    out.append(b2)
    
    # Пунктир орієнтиру 0 град
    out.append(line(670, 120, 670, 200, color=MUTED, sw=1.2, dash="3,3"))
    # Повернутий вектор (на ~45 градусів)
    out.append(line(640, 190, 700, 130, color=POS, sw=2.5))
    out.append(arrow(670, 160, 703, 127, color=POS, sw=2))
    out.append(arrow(670, 160, 637, 193, color=POS, sw=2))
    
    # Дуга кута обертання theta
    out.append(text(670, 220, "E' (повернуто на θ)", size=13, color=POS, bold=True))
    out.append(text(670, 245, "θ = V · B · L", size=14, color=INK, bold=True))
    
    # Підпис довжини середовища
    out.append(line(240, 245, 520, 245, color=LINE, sw=1))
    out.append(line(240, 240, 240, 250, color=LINE, sw=1))
    out.append(line(520, 240, 520, 250, color=LINE, sw=1))
    out.append(text(380, 265, "Довжина шляху L", size=12, color=INK))

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, "faraday-concept.svg"), w, h, "\n".join(out))
    print("Згенеровано img/faraday-concept.svg")

def generate_circular_decomposition():
    """Фігура 2: Розклад лінійної поляризації на дві кругові моди (RCP та LCP)."""
    w, h = 800, 340
    out = []
    out.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    out.append(rect(15, 15, 770, 310, fill="#fafafa", stroke="#d0d7de", sw=1, rx=8))
    
    # Ліва частина: Вхідний розклад E0 = E_R + E_L
    b_title1, _, _ = textbox(200, 45, "1. Вхід: Синфазні кругові моди (θ = 0)", size=14, pad=6, fill="#eef6ff", stroke=NEG, bold=True)
    out.append(b_title1)
    
    # Коло для лівої діаграми
    out.append(circle(200, 175, 70, fill="#ffffff", stroke="#b0b0b0", sw=1.5))
    # Осі
    out.append(line(200, 95, 200, 255, color=MUTED, sw=1, dash="4,4"))
    out.append(line(120, 175, 280, 175, color=MUTED, sw=1, dash="4,4"))
    
    # Вектори E_R (праве обертання, синій) та E_L (ліве обертання, червоний)
    out.append(line(200, 175, 245, 130, color=NEG, sw=2))
    out.append(arrow(200, 175, 245, 130, color=NEG, sw=2))
    out.append(text(255, 125, "E₊ (RCP)", size=12, color=NEG, bold=True))
    
    out.append(line(200, 175, 155, 130, color=POS, sw=2))
    out.append(arrow(200, 175, 155, 130, color=POS, sw=2))
    out.append(text(125, 125, "E₋ (LCP)", size=12, color=POS, bold=True))
    
    # Результуючий вектор E0 (вертикальний)
    out.append(line(200, 175, 200, 110, color=INK, sw=3))
    out.append(arrow(200, 175, 200, 105, color=INK, sw=3))
    out.append(text(200, 90, "E₀ = E₊ + E₋", size=13, color=INK, bold=True))
    
    # Центр: Середовище з n+ != n-
    b_mid, _, _ = textbox(400, 175, "Магнітне поле B\n\nn₊ ≠ n₋\n(Різні фазові\nшвидкості v₊ ≠ v₋)", size=13, pad=8, fill="#e8f8f5", stroke=FIELD, bold=True)
    out.append(b_mid)
    
    # Стрілка проходження
    out.append(arrow(285, 175, 335, 175, color=FIELD, sw=2.5))
    out.append(arrow(465, 175, 515, 175, color=FIELD, sw=2.5))
    
    # Права частина: Вихідний вектор зі зсувом фаз Delta Phi
    b_title2, _, _ = textbox(600, 45, "2. Вихід: Набіг фаз Δφ → Сумарний вектор повернуто", size=13, pad=6, fill="#fff5ee", stroke=POS, bold=True)
    out.append(b_title2)
    
    # Коло для правої діаграми
    out.append(circle(600, 175, 70, fill="#ffffff", stroke="#b0b0b0", sw=1.5))
    # Осі
    out.append(line(600, 95, 600, 255, color=MUTED, sw=1, dash="4,4"))
    out.append(line(520, 175, 680, 175, color=MUTED, sw=1, dash="4,4"))
    
    # Через n+ != n-, E+ повернувся на +phi, E- на -phi
    out.append(line(600, 175, 665, 150, color=NEG, sw=2)) # E+
    out.append(arrow(600, 175, 665, 150, color=NEG, sw=2))
    out.append(text(675, 145, "E₊", size=12, color=NEG, bold=True))
    
    out.append(line(600, 175, 575, 115, color=POS, sw=2)) # E-
    out.append(arrow(600, 175, 575, 115, color=POS, sw=2))
    out.append(text(560, 110, "E₋", size=12, color=POS, bold=True))
    
    # Сумарний E' бісектриса
    out.append(line(600, 175, 638, 112, color=POS, sw=3))
    out.append(arrow(600, 175, 638, 112, color=POS, sw=3))
    out.append(text(645, 95, "E' (повернуто на θ)", size=13, color=POS, bold=True))
    
    # Підпис кута обертання
    out.append(text(600, 270, "Кут обертання: θ = Δφ / 2", size=13, color=INK, bold=True))
    out.append(text(600, 292, "Δφ = (ω L / c) · (n₊ - n₋)", size=12, color=MUTED))

    render(os.path.join(IMG_DIR, "circular-decomposition.svg"), w, h, "\n".join(out))
    print("Згенеровано img/circular-decomposition.svg")

def generate_optical_isolator():
    """Фігура 3: Принцип роботи нереципрокного оптичного ізолятора."""
    w, h = 820, 420
    out = []
    out.append(rect(0, 0, w, h, fill=BG, stroke="none"))
    out.append(rect(15, 15, 790, 390, fill="#fcfcfc", stroke="#d0d7de", sw=1, rx=8))
    
    # Секція 1: Прямий хід (Пропускання)
    out.append(rect(35, 35, 750, 165, fill="#f4faf6", stroke="#27ae60", sw=1.5, rx=6))
    out.append(text(380, 58, "Прямий хід (Forward): Світло проходить з нульовими втратами", size=14, color=FIELD, bold=True))
    
    # Компоненти прямого ходу:
    # 1. Поляризатор 0 град
    out.append(rect(80, 80, 90, 80, fill="#ffffff", stroke=NEG, sw=1.5))
    out.append(line(125, 90, 125, 150, color=NEG, sw=2))
    out.append(text(125, 175, "Поляризатор P1\n(0°)", size=11, color=INK))
    
    # Стрілка між елементами
    out.append(arrow(180, 120, 230, 120, color=FIELD, sw=2))
    out.append(text(205, 105, "E (0°)", size=11, color=NEG, bold=True))
    
    # 2. Ротатор Фарадея (+45 град)
    out.append(rect(240, 80, 150, 80, fill="#eef6ff", stroke="#2980b9", sw=1.5))
    out.append(text(315, 110, "Ротатор Фарадея", size=12, color="#2980b9", bold=True))
    out.append(text(315, 130, "(Обертання +45°)", size=11, color=INK))
    out.append(text(315, 175, "Ефект Фарадея (+45°)", size=11, color=INK))
    
    # Стрілка далі
    out.append(arrow(400, 120, 450, 120, color=FIELD, sw=2))
    out.append(text(425, 105, "E (+45°)", size=11, color=POS, bold=True))
    
    # 3. Аналізатор (+45 град)
    out.append(rect(460, 80, 90, 80, fill="#ffffff", stroke=POS, sw=1.5))
    out.append(line(480, 145, 530, 95, color=POS, sw=2))
    out.append(text(505, 175, "Аналізатор P2\n(+45°)", size=11, color=INK))
    
    # Стрілка виходу
    out.append(arrow(560, 120, 710, 120, color=FIELD, sw=3))
    out.append(text(635, 105, "ПРОПУЩЕНО 100%", size=12, color=FIELD, bold=True))
    
    # Секція 2: Зворотний хід (Блокування)
    out.append(rect(35, 215, 750, 175, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    out.append(text(380, 238, "Зворотний хід (Backward): Відбитий промінь повністю блокується", size=14, color=POS, bold=True))
    
    # Компоненти зворотного ходу:
    out.append(arrow(710, 300, 560, 300, color=POS, sw=2))
    out.append(text(635, 285, "Відбите світло", size=11, color=POS))
    
    out.append(rect(460, 260, 90, 80, fill="#ffffff", stroke=POS, sw=1.5))
    out.append(line(480, 325, 530, 275, color=POS, sw=2))
    out.append(text(505, 355, "Аналізатор P2\n(Пропускає +45°)", size=11, color=INK))
    
    out.append(arrow(450, 300, 400, 300, color=POS, sw=2))
    out.append(text(425, 285, "E (+45°)", size=11, color=POS, bold=True))
    
    # Ротатор додає +45 град
    out.append(rect(240, 260, 150, 80, fill="#ffeef0", stroke=POS, sw=1.5))
    out.append(text(315, 290, "Ротатор Фарадея", size=12, color=POS, bold=True))
    out.append(text(315, 310, "Знов +45° ➔ Разом 90°!", size=11, color=POS, bold=True))
    out.append(text(315, 355, "Нереципрокне обертання", size=11, color=INK))
    
    out.append(arrow(230, 300, 180, 300, color=POS, sw=2))
    out.append(text(205, 285, "E (90° - перпендикулярно!)", size=10, color=POS, bold=True))
    
    # Вхідний поляризатор блокує
    out.append(rect(80, 260, 90, 80, fill="#ffffff", stroke=NEG, sw=1.5))
    out.append(line(125, 270, 125, 330, color=NEG, sw=2))
    out.append(line(95, 275, 155, 325, color=POS, sw=3))
    out.append(line(95, 325, 155, 275, color=POS, sw=3))
    out.append(text(125, 355, "Поляризатор P1 (0°)\nБЛОКУЄ 90°", size=11, color=POS, bold=True))
    
    out.append(text(60, 300, "X 0%", size=14, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "optical-isolator.svg"), w, h, "\n".join(out))
    print("Згенеровано img/optical-isolator.svg")

if __name__ == "__main__":
    generate_faraday_concept()
    generate_circular_decomposition()
    generate_optical_isolator()
