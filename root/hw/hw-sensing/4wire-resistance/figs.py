# -*- coding: utf-8 -*-
"""Фігури до теми «Чотирипровідний метод вимірювання опору».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"


# ── Фігура 1: Порівняння 2-провідної та 4-провідної схем ────────────────────
def fig_two_vs_four_wire():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Порівняння 2-провідної та 4-провідної схем вимірювання", size=16, bold=True))

    midx = W / 2
    f.append(line(midx, 50, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- ЛІВА ЧАСТИНА: 2-провідна схема ---
    f.append(text(midx / 2, 54, "2-провідний метод (похибка від дротів)", size=13, bold=True, color=COLOR_RED))

    # Джерело струму I
    f.append(circle(60, 150, 22, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(60, 150, "I", size=15, bold=True, color=COLOR_BLUE))
    f.append(arrow(60, 164, 60, 136, color=COLOR_BLUE, sw=1.5))

    # Паразитні опори дротів Rw1, Rw2
    f.append(line(60, 110, 110, 110, color=LINE, sw=1.8))
    f.append(rect(110, 100, 36, 20, fill='#fff4e6', stroke='#e67e22', sw=1.6, rx=3))
    f.append(text(128, 90, "Rw1", size=11, bold=True, color=COLOR_ORANGE))

    f.append(line(60, 190, 110, 190, color=LINE, sw=1.8))
    f.append(rect(110, 180, 36, 20, fill='#fff4e6', stroke='#e67e22', sw=1.6, rx=3))
    f.append(text(128, 212, "Rw2", size=11, bold=True, color=COLOR_ORANGE))

    # Лінії до вольтметра і до Rx
    f.append(line(146, 110, 260, 110, color=LINE, sw=1.8))
    f.append(line(146, 190, 260, 190, color=LINE, sw=1.8))

    # Точки підключення вольтметра
    f.append(line(190, 110, 190, 140, color=LINE, sw=1.5))
    f.append(line(190, 190, 190, 160, color=LINE, sw=1.5))
    f.append(circle(190, 150, 18, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(190, 150, "V", size=14, bold=True, color=INK))

    # Вимірюваний опір Rx
    f.append(line(260, 110, 260, 130, color=LINE, sw=1.8))
    f.append(line(260, 190, 260, 170, color=LINE, sw=1.8))
    f.append(rect(248, 130, 24, 40, fill='#eef6ff', stroke=COLOR_BLUE, sw=2, rx=4))
    f.append(text(260, 150, "Rx", size=13, bold=True, color=COLOR_BLUE))

    # Текстова формула похибки
    b1, w1, h1 = textbox(midx / 2, 280, "Vm = I · (Rx + Rw1 + Rw2)\nВольтметр міряє спад на дротах!",
                         size=12, pad=8, fill="#fff0f0", stroke="#ffb3b3", sw=1.2)
    f.append(b1)


    # --- ПРАВА ЧАСТИНА: 4-провідна схема (Kelvin sensing) ---
    f.append(text(midx + midx / 2, 54, "4-провідний метод (Kelvin sensing)", size=13, bold=True, color=COLOR_GREEN))

    # Джерело струму I (Force)
    f.append(circle(430, 150, 22, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(430, 150, "I", size=15, bold=True, color=COLOR_BLUE))
    f.append(arrow(430, 164, 430, 136, color=COLOR_BLUE, sw=1.5))

    # Силові дроти Force+ та Force-
    f.append(line(430, 110, 470, 110, color=COLOR_BLUE, sw=2))
    f.append(rect(470, 101, 34, 18, fill='#fff4e6', stroke='#e67e22', sw=1.4, rx=3))
    f.append(text(487, 92, "Rw1", size=10, color=COLOR_ORANGE))
    f.append(line(504, 110, 680, 110, color=COLOR_BLUE, sw=2))
    f.append(text(540, 96, "Force+ (I+)", size=11, bold=True, color=COLOR_BLUE))

    f.append(line(430, 190, 470, 190, color=COLOR_BLUE, sw=2))
    f.append(rect(470, 181, 34, 18, fill='#fff4e6', stroke='#e67e22', sw=1.4, rx=3))
    f.append(text(487, 210, "Rw4", size=10, color=COLOR_ORANGE))
    f.append(line(504, 190, 680, 190, color=COLOR_BLUE, sw=2))
    f.append(text(540, 204, "Force- (I-)", size=11, bold=True, color=COLOR_BLUE))

    # Вимірювальні дроти Sense+ та Sense-
    f.append(circle(640, 150, 18, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(640, 150, "V", size=14, bold=True, color=COLOR_GREEN))

    f.append(line(680, 125, 658, 125, color=COLOR_GREEN, sw=1.6))
    f.append(rect(610, 117, 34, 16, fill='#eafaf1', stroke=COLOR_GREEN, sw=1.2, rx=3))
    f.append(text(627, 108, "Rw2", size=10, color=COLOR_GREEN))
    f.append(line(610, 125, 590, 125, color=COLOR_GREEN, sw=1.6))

    f.append(line(680, 175, 658, 175, color=COLOR_GREEN, sw=1.6))
    f.append(rect(610, 167, 34, 16, fill='#eafaf1', stroke=COLOR_GREEN, sw=1.2, rx=3))
    f.append(text(627, 192, "Rw3", size=10, color=COLOR_GREEN))
    f.append(line(610, 175, 590, 175, color=COLOR_GREEN, sw=1.6))

    # Вертикальні з'єднання до Sense від точок прямо на Rx
    f.append(line(590, 125, 590, 135, color=COLOR_GREEN, sw=1.6))
    f.append(line(590, 175, 590, 165, color=COLOR_GREEN, sw=1.6))

    # Точки контакту Кельвіна (Kelvin contacts)
    f.append(circle(680, 110, 4, fill=COLOR_RED, stroke=LINE, sw=1))
    f.append(circle(680, 190, 4, fill=COLOR_RED, stroke=LINE, sw=1))
    f.append(circle(590, 135, 3, fill=COLOR_GREEN, stroke=LINE, sw=1))
    f.append(circle(590, 165, 3, fill=COLOR_GREEN, stroke=LINE, sw=1))

    # Об'єкт вимірювання Rx
    f.append(line(680, 110, 680, 130, color=COLOR_BLUE, sw=2))
    f.append(line(680, 190, 680, 170, color=COLOR_BLUE, sw=2))
    f.append(rect(668, 130, 24, 40, fill='#eef6ff', stroke=COLOR_BLUE, sw=2, rx=4))
    f.append(text(680, 150, "Rx", size=13, bold=True, color=COLOR_BLUE))

    # Текстова формула успіху
    b2, w2, h2 = textbox(midx + midx / 2, 280, "Isense ≈ 0  →  Spad na Rw2, Rw3 = 0\nVm = Vx = I · Rx (точно!)",
                         size=12, pad=8, fill="#eafaf1", stroke="#a3e4d7", sw=1.2)
    f.append(b2)

    return render(os.path.join(IMG, "two-vs-four-wire.svg"), W, H, *f)


# ── Фігура 2: Подвійний місток Кельвіна ─────────────────────────────────────
def fig_kelvin_bridge():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Схема подвійного моста Томсона — Кельвіна", size=16, bold=True))

    # Живлення моста (великий струм I)
    f.append(circle(70, 180, 20, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(70, 180, "E", size=14, bold=True, color=COLOR_BLUE))
    f.append(line(70, 70, 70, 160, color=LINE, sw=1.8))
    f.append(line(70, 200, 70, 290, color=LINE, sw=1.8))

    # Верхній контур: Стандартний опір R_std і вимірюваний R_x
    f.append(line(70, 70, 200, 70, color=LINE, sw=1.8))
    f.append(rect(200, 60, 50, 20, fill='#eef6ff', stroke=COLOR_BLUE, sw=1.8, rx=3))
    f.append(text(225, 70, "Rstd", size=12, bold=True, color=COLOR_BLUE))

    # Паразитний опір з'єднувального провідника R_y
    f.append(line(250, 70, 310, 70, color=LINE, sw=1.8))
    f.append(rect(310, 61, 40, 18, fill='#fff4e6', stroke='#e67e22', sw=1.5, rx=3))
    f.append(text(330, 70, "Ry", size=11, bold=True, color=COLOR_ORANGE))
    f.append(line(350, 70, 410, 70, color=LINE, sw=1.8))

    # Невідомий опір R_x
    f.append(rect(410, 60, 50, 20, fill='#eef6ff', stroke=COLOR_BLUE, sw=1.8, rx=3))
    f.append(text(435, 70, "Rx", size=12, bold=True, color=COLOR_BLUE))
    f.append(line(460, 70, 650, 70, color=LINE, sw=1.8))
    f.append(line(650, 70, 650, 290, color=LINE, sw=1.8))
    f.append(line(70, 290, 650, 290, color=LINE, sw=1.8))

    # Внутрішній плечовий міст: R1, R2, r1, r2
    # Точка A (між Rstd і Ry) і Точка B (між Ry і Rx)
    f.append(circle(250, 70, 4, fill=COLOR_RED, stroke=LINE, sw=1))
    f.append(text(250, 52, "A", size=12, bold=True, color=COLOR_RED))

    f.append(circle(410, 70, 4, fill=COLOR_RED, stroke=LINE, sw=1))
    f.append(text(410, 52, "B", size=12, bold=True, color=COLOR_RED))

    # Плечі R1 і R2 (зовнішні)
    f.append(line(250, 70, 250, 130, color=LINE, sw=1.5))
    f.append(rect(240, 130, 20, 40, fill='#f9f9f9', stroke=INK, sw=1.5, rx=3))
    f.append(text(222, 150, "R1", size=12, bold=True, color=INK))

    f.append(line(410, 70, 410, 130, color=LINE, sw=1.5))
    f.append(rect(400, 130, 20, 40, fill='#f9f9f9', stroke=INK, sw=1.5, rx=3))
    f.append(text(428, 150, "R2", size=12, bold=True, color=INK))

    # З'єднання R1 і R2 у вузол C
    f.append(line(250, 170, 330, 200, color=LINE, sw=1.5))
    f.append(line(410, 170, 330, 200, color=LINE, sw=1.5))

    # Плечі r1 і r2 (внутрішні)
    f.append(line(280, 70, 280, 110, color=LINE, sw=1.4))
    f.append(rect(272, 110, 16, 32, fill='#f9f9f9', stroke=INK, sw=1.4, rx=3))
    f.append(text(262, 126, "r1", size=11, color=INK))

    f.append(line(380, 70, 380, 110, color=LINE, sw=1.4))
    f.append(rect(372, 110, 16, 32, fill='#f9f9f9', stroke=INK, sw=1.4, rx=3))
    f.append(text(396, 126, "r2", size=11, color=INK))

    # З'єднання r1 і r2 у вузол D
    f.append(line(280, 142, 330, 165, color=LINE, sw=1.4))
    f.append(line(380, 142, 330, 165, color=LINE, sw=1.4))

    # Гальванометр G між C і D
    f.append(line(330, 165, 330, 180, color=LINE, sw=1.5))
    f.append(circle(330, 200, 16, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(330, 200, "G", size=14, bold=True, color=COLOR_GREEN))
    f.append(line(330, 216, 330, 230, color=LINE, sw=1.5))

    # Пояснення рівноваги
    b, w, h = textbox(W / 2, 310, "Умова балансу моста при R1/R2 = r1/r2:\nRx = Rstd · (R2 / R1) — опір провідника Ry повністю випадає з рівняння!",
                      size=12, pad=8, fill="#eef6ff", stroke="#99ccff", sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "kelvin-bridge-circuit.svg"), W, H, *f)


# ── Фігура 3: Компенсація термо-ЕРС (Offset Compensated Ohms) ───────────────
def fig_thermal_emf():
    W, H = 720, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Метод реверсування струму для компенсації термо-ЕРС (Vemf)", size=15, bold=True))

    # Графік струму збудження I(t) та виміряної напруги Vm(t)
    # Осі координат
    f.append(line(60, 230, 680, 230, color=LINE, sw=1.5)) # Ось t
    f.append(text(685, 234, "t", size=13, bold=True, color=INK))

    f.append(line(60, 45, 60, 250, color=LINE, sw=1.5)) # Ось V, I
    f.append(text(45, 45, "V, I", size=13, bold=True, color=INK))

    # Нульовий рівень напруги
    f.append(line(55, 150, 670, 150, color=MUTED, sw=1, dash="4,4"))
    f.append(text(40, 154, "0", size=11, color=MUTED))

    # Струм збудження +I та -I (пунктир або напівпрозорий блок)
    f.append(rect(100, 70, 240, 80, fill='#eef6ff', stroke='#b3d7ff', sw=1, rx=2))
    f.append(text(220, 90, "Струм +I", size=12, bold=True, color=COLOR_BLUE))

    f.append(rect(380, 150, 240, 80, fill='#fff4e6', stroke='#ffd8a8', sw=1, rx=2))
    f.append(text(500, 210, "Струм −I", size=12, bold=True, color=COLOR_ORANGE))

    # Рівень термо-ЕРС Vemf (постійне зміщення)
    f.append(line(70, 130, 660, 130, color=COLOR_RED, sw=1.4, dash="6,4"))
    f.append(text(620, 120, "Vemf (термо-ЕРС)", size=11, bold=True, color=COLOR_RED))

    # Виміряна напруга V+ = I*Rx + Vemf та V- = -I*Rx + Vemf
    # Фаза +I: V+
    f.append(line(100, 80, 340, 80, color=COLOR_GREEN, sw=2.5))
    f.append(circle(220, 80, 4, fill=COLOR_GREEN, stroke=LINE, sw=1))
    f.append(text(220, 68, "V+ = +I·Rx + Vemf", size=12, bold=True, color=COLOR_GREEN))

    # Фаза -I: V-
    f.append(line(380, 180, 620, 180, color=COLOR_GREEN, sw=2.5))
    f.append(circle(500, 180, 4, fill=COLOR_GREEN, stroke=LINE, sw=1))
    f.append(text(500, 196, "V− = −I·Rx + Vemf", size=12, bold=True, color=COLOR_GREEN))

    # Вертикальні пунктири перемикання
    f.append(line(100, 60, 100, 240, color=MUTED, sw=1, dash="2,2"))
    f.append(line(340, 60, 340, 240, color=MUTED, sw=1, dash="2,2"))
    f.append(line(380, 60, 380, 240, color=MUTED, sw=1, dash="2,2"))
    f.append(line(620, 60, 620, 240, color=MUTED, sw=1, dash="2,2"))

    # Формула віднімання
    b, w, h = textbox(W / 2, 282, "Vx = (V+ − V−) / 2 = I · Rx   →   Vemf повністю взаємознищується!",
                      size=12, pad=7, fill="#eafaf1", stroke="#a3e4d7", sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "thermal-emf-compensation.svg"), W, H, *f)


# ── Фігура 4: Розведення Кельвіна на друкованій платі (PCB layout) ─────────
def fig_pcb_kelvin():
    W, H = 720, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Топологія трасування Kelvin Sensing для SMD-шунта на PCB", size=15, bold=True))

    # Корпус SMD резистора-шунта (наприклад, 2512)
    f.append(rect(240, 90, 240, 100, fill='#2c3e50', stroke='#1a252f', sw=2, rx=6))
    f.append(text(360, 140, "SMD Шинний шунт (Rx)", size=14, bold=True, color='#ffffff'))

    # Контактні площадки (Pads) ліва і права
    f.append(rect(160, 80, 90, 120, fill='#d4ac0d', stroke='#b7950b', sw=2, rx=4))
    f.append(rect(470, 80, 90, 120, fill='#d4ac0d', stroke='#b7950b', sw=2, rx=4))

    # Силові провідники (широкі мідні полигони / Force traces)
    f.append(rect(40, 100, 120, 80, fill='#e59866', stroke='#d35400', sw=1.8, rx=2))
    f.append(text(90, 144, "Force I- (широкий)", size=12, bold=True, color='#7e5109'))

    f.append(rect(560, 100, 120, 80, fill='#e59866', stroke='#d35400', sw=1.8, rx=2))
    f.append(text(620, 144, "Force I+ (широкий)", size=12, bold=True, color='#7e5109'))

    # Сигнальні тонкі доріжки (Sense traces) — підключаються зсередини площадок
    f.append(line(230, 190, 230, 240, color=COLOR_GREEN, sw=3))
    f.append(line(230, 240, 320, 240, color=COLOR_GREEN, sw=3))
    f.append(circle(230, 190, 4, fill=COLOR_GREEN, stroke=LINE, sw=1))
    f.append(text(280, 260, "Sense- (тонкий)", size=11, bold=True, color=COLOR_GREEN))

    f.append(line(490, 190, 490, 240, color=COLOR_GREEN, sw=3))
    f.append(line(490, 240, 400, 240, color=COLOR_GREEN, sw=3))
    f.append(circle(490, 190, 4, fill=COLOR_GREEN, stroke=LINE, sw=1))
    f.append(text(440, 260, "Sense+ (тонкий)", size=11, bold=True, color=COLOR_GREEN))

    # Пояснення правильного знімання напруги
    f.append(arrow(210, 220, 230, 195, color=COLOR_RED, sw=1.5))
    f.append(text(150, 225, "Знімання потенціалу\nбезпосередньо з пада!", size=10, bold=True, color=COLOR_RED))

    f.append(arrow(510, 220, 490, 195, color=COLOR_RED, sw=1.5))
    f.append(text(570, 225, "Не включає опір\nсилової доріжки!", size=10, bold=True, color=COLOR_RED))

    return render(os.path.join(IMG, "pcb-kelvin-trace.svg"), W, H, *f)


if __name__ == '__main__':
    fig_two_vs_four_wire()
    fig_kelvin_bridge()
    fig_thermal_emf()
    fig_pcb_kelvin()
    print("Всі 4 фігури згенеровано успішно у ./img/")
