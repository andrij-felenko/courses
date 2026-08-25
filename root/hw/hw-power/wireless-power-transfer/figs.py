# -*- coding: utf-8 -*-
"""Фігури для теми wireless-power-transfer (Бездротова передача енергії: Qi і резонансна індукція).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5). Вивід у ./img/.

    python figs.py
"""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *  # noqa: E402,F403

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

GOLD = "#b8860b"   # магнітне поле / котушки
COILC = "#8a6d1f"  # дріт котушки
MAG = "#8e44ad"    # фіолетовий для модульованих сигналів
BLUE = "#2457d6"
RED = "#c0392b"
GREEN = "#27ae60"


def _coil_v(x, y_top, y_bot, n=5, r=10, left=True, color=COILC):
    """Обмотка як ланцюжок півдуг уздовж вертикалі."""
    step = (y_bot - y_top) / n
    d = "M %.1f %.1f " % (x, y_top)
    sweep = 0 if left else 1
    yy = y_top
    for _ in range(n):
        d += "A %.1f %.1f 0 0 %d %.1f %.1f " % (r, step / 2, sweep, x, yy + step)
        yy += step
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, color)


def _coil_h(y, x_left, x_right, n=5, r=10, up=True, color=COILC):
    """Обмотка горизонтальна (ланцюжок півдуг)."""
    step = (x_right - x_left) / n
    d = "M %.1f %.1f " % (x_left, y)
    sweep = 1 if up else 0
    xx = x_left
    for _ in range(n):
        d += "A %.1f %.1f 0 0 %d %.1f %.1f " % (step / 2, r, sweep, xx + step, y)
        xx += step
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, color)


def _mag_flux_lines(x_tx, x_rx, y_top, y_bot, count=4, color="#e67e22"):
    """Силові лінії магнітного поля між двома котушками."""
    out = []
    cy = (y_top + y_bot) / 2
    h = y_bot - y_top
    for i in range(count):
        offset = (i - (count - 1) / 2) * (h / (count + 1))
        y = cy + offset
        curv = 18 + abs(offset) * 0.4
        d = "M %.1f %.1f Q %.1f %.1f %.1f %.1f" % (
            x_tx, y, (x_tx + x_rx) / 2, y + (curv if offset >= 0 else -curv), x_rx, y
        )
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,3"/>' % (d, color))
    return "".join(out)


def fig_inductive_vs_resonant():
    """Порівняння звичайної індуктивної передачі та резонансної магнітної індукції."""
    W, H = 940, 480
    f = []

    midx = W / 2

    # Ліва колонка: Звичайна індукція (Нерезонансна)
    x0_l = 30
    w_col = midx - 45
    f.append(rect(x0_l, 40, w_col, 410, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(x0_l + w_col / 2, 70, "Звичайна індукція (трансформатор без осердя)", size=15, color=INK, bold=True))
    f.append(text(x0_l + w_col / 2, 92, "Слабкий зв'язок k ≈ 0.15 без резонансної компенсації", size=12, color=MUTED))

    # Схема зліва
    ytx = 180
    f.append(circle(x0_l + 50, ytx, 18, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(text(x0_l + 50, ytx + 5, "~", size=20, bold=True))
    f.append(text(x0_l + 50, ytx - 26, "U_вх", size=12, color=MUTED))

    f.append(line(x0_l + 68, ytx - 10, x0_l + 130, ytx - 10, sw=1.8))
    f.append(line(x0_l + 68, ytx + 10, x0_l + 130, ytx + 10, sw=1.8))

    f.append(_coil_v(x0_l + 130, ytx - 50, ytx + 50, n=5, r=10, left=True))
    f.append(text(x0_l + 100, ytx + 5, "L₁", size=14, bold=True))

    f.append(rect(x0_l + 145, ytx - 60, 50, 120, fill="#fff3e0", stroke="#f39c12", sw=1.2, rx=4))
    f.append(text(x0_l + 170, ytx - 40, "Зазор", size=11, color="#d35400", bold=True))
    f.append(text(x0_l + 170, ytx - 24, "3–8 мм", size=10, color="#d35400"))
    f.append(text(x0_l + 170, ytx + 42, "k ≈ 0.15", size=11, color=RED, bold=True))

    f.append(_mag_flux_lines(x0_l + 130, x0_l + 210, ytx - 40, ytx + 40, count=3, color=RED))

    f.append(_coil_v(x0_l + 210, ytx - 50, ytx + 50, n=5, r=10, left=False))
    f.append(text(x0_l + 240, ytx + 5, "L₂", size=14, bold=True))

    f.append(line(x0_l + 210, ytx - 50, x0_l + 320, ytx - 50, sw=1.8))
    f.append(line(x0_l + 210, ytx + 50, x0_l + 320, ytx + 50, sw=1.8))

    f.append(rect(x0_l + 310, ytx - 25, 25, 50, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(text(x0_l + 360, ytx + 5, "R_нав", size=13, bold=True))
    f.append(line(x0_l + 320, ytx - 50, x0_l + 320, ytx - 25, sw=1.8))
    f.append(line(x0_l + 320, ytx + 25, x0_l + 320, ytx + 50, sw=1.8))

    b1, _, _ = textbox(x0_l + w_col / 2, 330,
                       "• 85% магнітного потоку розсіюється в повітрі\n"
                       "• Величезна індуктивність розсіяння L_σ\n"
                       "• Реактивний опір ωL_σ душить струм передачі\n"
                       "• ККД падає нижче 15–20%",
                       size=12, pad=10, fill="#fdf2e9", stroke="#e67e22")
    f.append(b1)

    # Права колонка: Резонансна індукція (Qi / WPT)
    x0_r = midx + 15
    f.append(rect(x0_r, 40, w_col, 410, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(x0_r + w_col / 2, 70, "Резонансна індукція (WPT / Qi)", size=15, color=INK, bold=True))
    f.append(text(x0_r + w_col / 2, 92, "Конденсатори C₁ і C₂ компенсують реактивність ωL", size=12, color=GREEN))

    f.append(circle(x0_r + 45, ytx, 18, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(text(x0_r + 45, ytx + 5, "~", size=20, bold=True))

    f.append(line(x0_r + 63, ytx - 10, x0_r + 85, ytx - 10, sw=1.8))
    f.append(line(x0_r + 85, ytx - 20, x0_r + 85, ytx, sw=2.2, color=BLUE))
    f.append(line(x0_r + 91, ytx - 20, x0_r + 91, ytx, sw=2.2, color=BLUE))
    f.append(text(x0_r + 88, ytx - 26, "C₁", size=13, color=BLUE, bold=True))
    f.append(line(x0_r + 91, ytx - 10, x0_r + 130, ytx - 10, sw=1.8))
    f.append(line(x0_r + 63, ytx + 10, x0_r + 130, ytx + 10, sw=1.8))

    f.append(_coil_v(x0_r + 130, ytx - 50, ytx + 50, n=5, r=10, left=True))
    f.append(text(x0_r + 100, ytx + 5, "L₁", size=14, bold=True))

    f.append(rect(x0_r + 145, ytx - 60, 50, 120, fill="#e8f8f5", stroke="#1abc9c", sw=1.2, rx=4))
    f.append(text(x0_r + 170, ytx - 40, "Зазор", size=11, color="#16a085", bold=True))
    f.append(text(x0_r + 170, ytx - 24, "3–8 мм", size=10, color="#16a085"))
    f.append(text(x0_r + 170, ytx + 42, "k·Q > 10", size=11, color=GREEN, bold=True))

    f.append(_mag_flux_lines(x0_r + 130, x0_r + 210, ytx - 40, ytx + 40, count=4, color=GREEN))

    f.append(_coil_v(x0_r + 210, ytx - 50, ytx + 50, n=5, r=10, left=False))
    f.append(text(x0_r + 240, ytx + 5, "L₂", size=14, bold=True))

    f.append(line(x0_r + 210, ytx - 50, x0_r + 245, ytx - 50, sw=1.8))
    f.append(line(x0_r + 245, ytx - 60, x0_r + 245, ytx - 40, sw=2.2, color=BLUE))
    f.append(line(x0_r + 251, ytx - 60, x0_r + 251, ytx - 40, sw=2.2, color=BLUE))
    f.append(text(x0_r + 248, ytx - 68, "C₂", size=13, color=BLUE, bold=True))
    f.append(line(x0_r + 251, ytx - 50, x0_r + 320, ytx - 50, sw=1.8))
    f.append(line(x0_r + 210, ytx + 50, x0_r + 320, ytx + 50, sw=1.8))

    f.append(rect(x0_r + 310, ytx - 25, 25, 50, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(text(x0_r + 360, ytx + 5, "R_нав", size=13, bold=True))
    f.append(line(x0_r + 320, ytx - 50, x0_r + 320, ytx - 25, sw=1.8))
    f.append(line(x0_r + 320, ytx + 25, x0_r + 320, ytx + 50, sw=1.8))

    b2, _, _ = textbox(x0_r + w_col / 2, 330,
                       "• 1/(ωC) повністю гасить реактивний опір ωL\n"
                       "• Циркулююча енергія контуру підтримує потік\n"
                       "• Добротність контурів Q₁·Q₂ компенсує малий k\n"
                       "• ККД передачі сягає 75–88%",
                       size=12, pad=10, fill="#eafaf1", stroke="#27ae60")
    f.append(b2)

    return render(os.path.join(IMG, "inductive-vs-resonant.svg"), W, H, *f)


def fig_wpt_system_architecture():
    """Повна структурна схема системи Qi WPT: Передавач TX та Приймач RX."""
    W, H = 960, 520
    f = []

    f.append(text(W / 2, 28, "Архітектура системи бездротової передачі енергії Qi", size=16, bold=True))

    w_tx = 430
    h_box = 440
    f.append(rect(20, 50, w_tx, h_box, fill="#f8f9fa", stroke="#2c3e50", sw=1.8, rx=8))
    f.append(text(140, 75, "ПЕРЕДАВАЧ (TX)", size=14, color="#2c3e50", bold=True))
    f.append(text(140, 93, "WPC Qi Base Station", size=11, color=MUTED))

    f.append(rect(40, 120, 90, 44, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(85, 140, "DC Вхід", size=12, bold=True))
    f.append(text(85, 155, "5V / 9V / 12V", size=10, color=MUTED))

    f.append(rect(160, 115, 120, 54, fill="#ebf5fb", stroke=BLUE, sw=1.8))
    f.append(text(220, 137, "H-міст (Full-Bridge)", size=11, color=BLUE, bold=True))
    f.append(text(220, 153, "4× MOSFET (110–205 кГц)", size=9, color=MUTED))
    f.append(arrow(130, 142, 160, 142, sw=1.5))

    f.append(rect(310, 122, 50, 40, fill="#ffffff", stroke=BLUE, sw=1.5))
    f.append(text(335, 146, "C_tx", size=13, color=BLUE, bold=True))
    f.append(arrow(280, 142, 310, 142, sw=1.5))

    f.append(line(360, 142, 390, 142, sw=1.8))
    f.append(_coil_v(390, 115, 235, n=5, r=10, left=True, color=GOLD))
    f.append(text(360, 190, "L_tx", size=14, color=COILC, bold=True))
    f.append(line(390, 235, 220, 235, sw=1.8))
    f.append(line(220, 235, 220, 170, sw=1.8))

    f.append(rect(160, 265, 140, 50, fill="#fef9e7", stroke="#f39c12", sw=1.5))
    f.append(text(230, 285, "Демодулятор сигналу", size=11, color="#b7950b", bold=True))
    f.append(text(230, 302, "Детектор обвідної струму", size=9, color=MUTED))
    f.append(line(220, 235, 220, 265, sw=1.5, dash="3,3"))

    f.append(rect(60, 340, 240, 120, fill="#ffffff", stroke="#2c3e50", sw=1.8))
    f.append(text(180, 365, "Контролер TX (MCU / DSP)", size=13, bold=True))
    f.append(text(180, 385, "• Генератор частоти ШІМ", size=10, color=MUTED))
    f.append(text(180, 402, "• Декодер пакетів (BMC 2 kbps)", size=10, color=MUTED))
    f.append(text(180, 419, "• Петля потужності (PID / CEP)", size=10, color=MUTED))
    f.append(text(180, 436, "• Захист FOD (контроль Q та P_loss)", size=10, color=RED, bold=True))

    f.append(arrow(230, 315, 230, 340, sw=1.5))
    f.append(arrow(85, 340, 85, 164, sw=1.5))
    f.append(arrow(180, 340, 180, 170, sw=1.5))

    f.append(rect(455, 100, 50, 160, fill="#fcf3cf", stroke="#f1c40f", sw=1.5, rx=4))
    f.append(text(480, 130, "k", size=18, color="#b7950b", bold=True))
    f.append(text(480, 155, "Зазор", size=11, color="#7d6608", bold=True))
    f.append(text(480, 172, "3–8 мм", size=10, color="#7d6608"))
    f.append(text(480, 220, "Магнітний\nпотік", size=10, color="#7d6608"))

    # Блок RX (праворуч)
    x_rx_box = 510
    f.append(rect(x_rx_box, 50, w_tx, h_box, fill="#f8f9fa", stroke="#27ae60", sw=1.8, rx=8))
    f.append(text(x_rx_box + 120, 75, "ПРИЙМАЧ (RX)", size=14, color="#27ae60", bold=True))
    f.append(text(x_rx_box + 120, 93, "Qi Receiver (Phone / Device)", size=11, color=MUTED))

    f.append(_coil_v(x_rx_box + 30, 115, 235, n=5, r=10, left=False, color=GOLD))
    f.append(text(x_rx_box + 60, 190, "L_rx", size=14, color=COILC, bold=True))

    f.append(line(x_rx_box + 30, 115, x_rx_box + 70, 115, sw=1.8))
    f.append(rect(x_rx_box + 70, 100, 40, 30, fill="#ffffff", stroke=BLUE, sw=1.5))
    f.append(text(x_rx_box + 90, 120, "C_s", size=12, color=BLUE, bold=True))
    f.append(line(x_rx_box + 110, 115, x_rx_box + 145, 115, sw=1.8))
    f.append(line(x_rx_box + 30, 235, x_rx_box + 145, 235, sw=1.8))

    f.append(rect(x_rx_box + 60, 270, 110, 60, fill="#f4ecf7", stroke=MAG, sw=1.5))
    f.append(text(x_rx_box + 115, 290, "Модулятор RX", size=11, color=MAG, bold=True))
    f.append(text(x_rx_box + 115, 305, "Ключі C_mod / R_mod", size=9, color=MUTED))
    f.append(text(x_rx_box + 115, 319, "In-Band зв'язок", size=9, color=MAG))
    f.append(line(x_rx_box + 115, 235, x_rx_box + 115, 270, sw=1.5, dash="3,3"))

    f.append(rect(x_rx_box + 145, 115, 110, 120, fill="#eafaf1", stroke=GREEN, sw=1.8))
    f.append(text(x_rx_box + 200, 140, "Синхронний", size=12, color=GREEN, bold=True))
    f.append(text(x_rx_box + 200, 156, "випрямляч", size=12, color=GREEN, bold=True))
    f.append(text(x_rx_box + 200, 175, "4× MOSFET", size=10, color=MUTED))
    f.append(text(x_rx_box + 200, 195, "V_rect (DC)", size=11, color=GREEN, bold=True))

    f.append(rect(x_rx_box + 285, 130, 80, 90, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(x_rx_box + 325, 155, "DC-DC", size=12, bold=True))
    f.append(text(x_rx_box + 325, 172, "Buck / LDO", size=10, color=MUTED))
    f.append(text(x_rx_box + 325, 195, "5V / 9V / 12V", size=10, color=GREEN, bold=True))
    f.append(arrow(x_rx_box + 255, 175, x_rx_box + 285, 175, sw=1.8))

    f.append(rect(x_rx_box + 385, 140, 35, 70, fill="#ebf5fb", stroke=BLUE, sw=1.8))
    f.append(text(x_rx_box + 402, 170, "АКБ", size=11, color=BLUE, bold=True))
    f.append(text(x_rx_box + 402, 185, "Load", size=10, color=MUTED))
    f.append(arrow(x_rx_box + 365, 175, x_rx_box + 385, 175, sw=1.8))

    f.append(rect(x_rx_box + 190, 340, 220, 120, fill="#ffffff", stroke="#27ae60", sw=1.8))
    f.append(text(x_rx_box + 300, 365, "Контролер RX (MCU)", size=13, color="#27ae60", bold=True))
    f.append(text(x_rx_box + 300, 385, "• Вимірювання V_rect та I_rect", size=10, color=MUTED))
    f.append(text(x_rx_box + 300, 402, "• Формування пакетів помилки CEP", size=10, color=MUTED))
    f.append(text(x_rx_box + 300, 419, "• Пакет переданої потужності (FOD)", size=10, color=MUTED))
    f.append(text(x_rx_box + 300, 436, "• Керування ключем модуляції", size=10, color=MAG, bold=True))

    f.append(arrow(x_rx_box + 200, 235, x_rx_box + 200, 340, sw=1.5))
    f.append(arrow(x_rx_box + 190, 380, x_rx_box + 170, 300, sw=1.5, color=MAG))

    return render(os.path.join(IMG, "wpt-system-architecture.svg"), W, H, *f)


def fig_reflected_impedance():
    """Еквівалентна схема та відбитий імпеданс: Z_refl = (ωM)² / Z₂."""
    W, H = 920, 420
    f = []

    f.append(text(W / 2, 28, "Трансформація імпедансу: відбитий опір вторинного кола", size=16, bold=True))

    y1 = 120
    f.append(rect(30, 50, 410, 330, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(235, 75, "Два зв'язані контури (Первинний + Вторинний)", size=13, bold=True))

    f.append(circle(65, y1 + 30, 15, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(65, y1 + 34, "~", size=16, bold=True))
    f.append(text(65, y1 + 8, "U₁", size=11, color=MUTED))

    f.append(line(80, y1 + 15, 110, y1 + 15, sw=1.5))
    f.append(rect(110, y1 + 5, 25, 20, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(122, y1 + 18, "R₁", size=10, bold=True))
    f.append(line(135, y1 + 15, 155, y1 + 15, sw=1.5))
    f.append(line(155, y1 + 5, 155, y1 + 25, sw=2, color=BLUE))
    f.append(line(160, y1 + 5, 160, y1 + 25, sw=2, color=BLUE))
    f.append(text(158, y1 - 2, "C₁", size=10, color=BLUE, bold=True))
    f.append(line(160, y1 + 15, 185, y1 + 15, sw=1.5))

    f.append(_coil_v(185, y1 - 10, y1 + 70, n=4, r=8, left=True))
    f.append(text(165, y1 + 35, "L₁", size=11, bold=True))
    f.append(line(185, y1 + 70, 65, y1 + 70, sw=1.5))
    f.append(line(65, y1 + 70, 65, y1 + 45, sw=1.5))

    f.append(text(217, y1 + 20, "M", size=14, color=GOLD, bold=True))
    f.append(text(217, y1 + 40, "k", size=12, color=MUTED))
    f.append(_mag_flux_lines(185, 245, y1, y1 + 60, count=3, color=GOLD))

    f.append(_coil_v(245, y1 - 10, y1 + 70, n=4, r=8, left=False))
    f.append(text(265, y1 + 35, "L₂", size=11, bold=True))

    f.append(line(245, y1 - 10, 275, y1 - 10, sw=1.5))
    f.append(line(275, y1 - 20, 275, y1, sw=2, color=BLUE))
    f.append(line(280, y1 - 20, 280, y1, sw=2, color=BLUE))
    f.append(text(278, y1 - 26, "C₂", size=10, color=BLUE, bold=True))

    f.append(line(280, y1 - 10, 305, y1 - 10, sw=1.5))
    f.append(rect(305, y1 - 20, 25, 20, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(317, y1 - 7, "R₂", size=10, bold=True))

    f.append(line(330, y1 - 10, 365, y1 - 10, sw=1.5))
    f.append(line(245, y1 + 70, 365, y1 + 70, sw=1.5))

    f.append(rect(355, y1 + 10, 20, 40, fill="#ebf5fb", stroke=BLUE, sw=1.5))
    f.append(text(400, y1 + 33, "R_нав", size=11, color=BLUE, bold=True))
    f.append(line(365, y1 - 10, 365, y1 + 10, sw=1.5))
    f.append(line(365, y1 + 50, 365, y1 + 70, sw=1.5))

    b_z2, _, _ = textbox(235, 290,
                         "Вторинний контур має власний повний імпеданс:\n"
                         "Z₂ = R₂ + R_нав + j·(ωL₂ − 1/(ωC₂))\n"
                         "На резонансі ω₀: Im(Z₂) = 0  ⇒  Z₂ = R₂ + R_нав",
                         size=11, pad=8, fill="#f4f6f8", stroke=MUTED)
    f.append(b_z2)

    f.append(arrow(450, 200, 480, 200, sw=2.5, color=BLUE))
    f.append(text(465, 180, "≡", size=24, color=BLUE, bold=True))

    f.append(rect(490, 50, 400, 330, fill="#fdfefe", stroke=BLUE, sw=1.8, rx=8))
    f.append(text(690, 75, "Еквівалентне первинне коло з Z_відб", size=13, color=BLUE, bold=True))

    f.append(circle(525, y1 + 30, 15, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(525, y1 + 34, "~", size=16, bold=True))
    f.append(text(525, y1 + 8, "U₁", size=11, color=MUTED))

    f.append(line(540, y1 + 15, 570, y1 + 15, sw=1.5))
    f.append(rect(570, y1 + 5, 25, 20, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(582, y1 + 18, "R₁", size=10, bold=True))
    f.append(line(595, y1 + 15, 620, y1 + 15, sw=1.5))
    f.append(line(620, y1 + 5, 620, y1 + 25, sw=2, color=BLUE))
    f.append(line(625, y1 + 5, 625, y1 + 25, sw=2, color=BLUE))
    f.append(text(623, y1 - 2, "C₁", size=10, color=BLUE, bold=True))
    f.append(line(625, y1 + 15, 650, y1 + 15, sw=1.5))

    f.append(_coil_h(y1 + 15, 650, 720, n=4, r=7, up=True))
    f.append(text(685, y1 - 2, "L₁", size=11, bold=True))

    f.append(line(720, y1 + 15, 755, y1 + 15, sw=1.5))
    f.append(rect(755, y1 + 2, 50, 26, fill="#fef9e7", stroke="#f39c12", sw=1.8))
    f.append(text(780, y1 + 19, "Z_відб", size=11, color="#b7950b", bold=True))

    f.append(line(805, y1 + 15, 830, y1 + 15, sw=1.5))
    f.append(line(830, y1 + 15, 830, y1 + 70, sw=1.5))
    f.append(line(830, y1 + 70, 525, y1 + 70, sw=1.5))
    f.append(line(525, y1 + 70, 525, y1 + 45, sw=1.5))

    b_zrefl, _, _ = textbox(690, 280,
                            "Z_відб = (ω·M)² / Z₂\n\n"
                            "Якщо вторинний контур у чистому резонансі:\n"
                            "Z_відб = (ω·M)² / (R₂ + R_нав)   [суто активний опір!]\n\n"
                            "Зміна R_нав або M миттєво змінює струм первинної L₁!",
                            size=11, pad=10, fill="#fefde8", stroke="#f1c40f")
    f.append(b_zrefl)

    return render(os.path.join(IMG, "reflected-impedance.svg"), W, H, *f)


def fig_compensation_topologies():
    """Порівняння топологій резонансної компенсації: SS, SP та LCC."""
    W, H = 940, 460
    f = []

    f.append(text(W / 2, 26, "Топології компенсації: Series-Series (SS), Series-Parallel (SP) та LCC", size=15, bold=True))

    col_w = 285
    gap = 20

    # 1. SS Топологія
    x1 = 20
    f.append(rect(x1, 50, col_w, 390, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=6))
    f.append(text(x1 + col_w / 2, 75, "SS (Series-Series)", size=14, color=BLUE, bold=True))
    f.append(text(x1 + col_w / 2, 93, "Стандарт Qi (BPP / EPP)", size=11, color=MUTED))

    ys = 150
    f.append(line(x1 + 30, ys, x1 + 55, ys, sw=1.5))
    f.append(line(x1 + 55, ys - 12, x1 + 55, ys + 12, sw=2, color=BLUE))
    f.append(line(x1 + 60, ys - 12, x1 + 60, ys + 12, sw=2, color=BLUE))
    f.append(text(x1 + 57, ys - 18, "C₁", size=10, color=BLUE, bold=True))
    f.append(line(x1 + 60, ys, x1 + 90, ys, sw=1.5))
    f.append(_coil_v(x1 + 90, ys - 35, ys + 35, n=4, r=7, left=True))
    f.append(text(x1 + 75, ys, "L₁", size=11, bold=True))

    f.append(_mag_flux_lines(x1 + 90, x1 + 135, ys - 25, ys + 25, count=3, color=GOLD))

    f.append(_coil_v(x1 + 135, ys - 35, ys + 35, n=4, r=7, left=False))
    f.append(text(x1 + 150, ys, "L₂", size=11, bold=True))
    f.append(line(x1 + 135, ys - 35, x1 + 175, ys - 35, sw=1.5))
    f.append(line(x1 + 175, ys - 45, x1 + 175, ys - 25, sw=2, color=BLUE))
    f.append(line(x1 + 180, ys - 45, x1 + 180, ys - 25, sw=2, color=BLUE))
    f.append(text(x1 + 177, ys - 50, "C₂", size=10, color=BLUE, bold=True))
    f.append(line(x1 + 180, ys - 35, x1 + 225, ys - 35, sw=1.5))

    f.append(rect(x1 + 215, ys - 15, 20, 30, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(x1 + 255, ys + 3, "R_н", size=11, bold=True))
    f.append(line(x1 + 225, ys - 35, x1 + 225, ys - 15, sw=1.5))
    f.append(line(x1 + 225, ys + 15, x1 + 225, ys + 35, sw=1.5))
    f.append(line(x1 + 135, ys + 35, x1 + 225, ys + 35, sw=1.5))
    f.append(line(x1 + 30, ys + 35, x1 + 90, ys + 35, sw=1.5))

    b_ss, _, _ = textbox(x1 + col_w / 2, 310,
                         "• C₁ та C₂ не залежать від k\n"
                         "• ω₀ = 1/√(L₁C₁) = 1/√(L₂C₂)\n"
                         "• Постійна резонансна частота\n"
                         "• Працює як джерело струму\n"
                         "• Небезпечний ХХ без зв'язку",
                         size=11, pad=8, fill="#ebf5fb", stroke=BLUE)
    f.append(b_ss)

    # 2. SP Топологія
    x2 = x1 + col_w + gap
    f.append(rect(x2, 50, col_w, 390, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=6))
    f.append(text(x2 + col_w / 2, 75, "SP (Series-Parallel)", size=14, color=GREEN, bold=True))
    f.append(text(x2 + col_w / 2, 93, "Джерело стабільної напруги", size=11, color=MUTED))

    f.append(line(x2 + 30, ys, x2 + 55, ys, sw=1.5))
    f.append(line(x2 + 55, ys - 12, x2 + 55, ys + 12, sw=2, color=BLUE))
    f.append(line(x2 + 60, ys - 12, x2 + 60, ys + 12, sw=2, color=BLUE))
    f.append(text(x2 + 57, ys - 18, "C₁", size=10, color=BLUE, bold=True))
    f.append(line(x2 + 60, ys, x2 + 90, ys, sw=1.5))
    f.append(_coil_v(x2 + 90, ys - 35, ys + 35, n=4, r=7, left=True))
    f.append(text(x2 + 75, ys, "L₁", size=11, bold=True))

    f.append(_mag_flux_lines(x2 + 90, x2 + 135, ys - 25, ys + 25, count=3, color=GOLD))

    f.append(_coil_v(x2 + 135, ys - 35, ys + 35, n=4, r=7, left=False))
    f.append(text(x2 + 150, ys, "L₂", size=11, bold=True))
    f.append(line(x2 + 135, ys - 35, x2 + 235, ys - 35, sw=1.5))
    f.append(line(x2 + 135, ys + 35, x2 + 235, ys + 35, sw=1.5))

    f.append(line(x2 + 180, ys - 35, x2 + 180, ys - 10, sw=1.5))
    f.append(line(x2 + 172, ys - 10, x2 + 188, ys - 10, sw=2, color=BLUE))
    f.append(line(x2 + 172, ys - 4, x2 + 188, ys - 4, sw=2, color=BLUE))
    f.append(text(x2 + 198, ys - 7, "C₂", size=10, color=BLUE, bold=True))
    f.append(line(x2 + 180, ys - 4, x2 + 180, ys + 35, sw=1.5))

    f.append(rect(x2 + 225, ys - 15, 20, 30, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(x2 + 265, ys + 3, "R_н", size=11, bold=True))
    f.append(line(x2 + 235, ys - 35, x2 + 235, ys - 15, sw=1.5))
    f.append(line(x2 + 235, ys + 15, x2 + 235, ys + 35, sw=1.5))
    f.append(line(x2 + 30, ys + 35, x2 + 90, ys + 35, sw=1.5))

    b_sp, _, _ = textbox(x2 + col_w / 2, 310,
                         "• C₁ ЗАЛЕЖИТЬ від зв'язку k:\n"
                         "  C₁ = C_p / (1 − k²)\n"
                         "• Зміна відстані зсуває резонанс\n"
                         "• Працює як джерело напруги\n"
                         "• Добре тримає холостий хід",
                         size=11, pad=8, fill="#eafaf1", stroke=GREEN)
    f.append(b_sp)

    # 3. LCC Топологія
    x3 = x2 + col_w + gap
    f.append(rect(x3, 50, col_w, 390, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=6))
    f.append(text(x3 + col_w / 2, 75, "LCC / WPT високої потужності", size=14, color=GOLD, bold=True))
    f.append(text(x3 + col_w / 2, 93, "Електромобілі / 1–22 кВт", size=11, color=MUTED))

    f.append(_coil_h(ys - 35, x3 + 30, x3 + 80, n=3, r=6, up=True))
    f.append(text(x3 + 55, ys - 48, "L_f1", size=10, bold=True))

    f.append(line(x3 + 80, ys - 35, x3 + 80, ys - 10, sw=1.5))
    f.append(line(x3 + 72, ys - 10, x3 + 88, ys - 10, sw=2, color=BLUE))
    f.append(line(x3 + 72, ys - 4, x3 + 88, ys - 4, sw=2, color=BLUE))
    f.append(text(x3 + 98, ys - 7, "C_p1", size=9, color=BLUE, bold=True))
    f.append(line(x3 + 80, ys - 4, x3 + 80, ys + 35, sw=1.5))

    f.append(line(x3 + 80, ys - 35, x3 + 105, ys - 35, sw=1.5))
    f.append(line(x3 + 105, ys - 45, x3 + 105, ys - 25, sw=2, color=BLUE))
    f.append(line(x3 + 110, ys - 45, x3 + 110, ys - 25, sw=2, color=BLUE))
    f.append(text(x3 + 107, ys - 50, "C_s1", size=9, color=BLUE, bold=True))
    f.append(line(x3 + 110, ys - 35, x3 + 130, ys - 35, sw=1.5))

    f.append(_coil_v(x3 + 130, ys - 35, ys + 35, n=4, r=7, left=True))
    f.append(text(x3 + 145, ys, "L₁", size=11, bold=True))
    f.append(line(x3 + 30, ys + 35, x3 + 130, ys + 35, sw=1.5))

    b_lcc, _, _ = textbox(x3 + col_w / 2, 310,
                          "• 3 реактивні елементи L-C-C\n"
                          "• Повний ZVS у всьому діапазоні\n"
                          "• Струм котушки не залежить від R_н\n"
                          "• Низькі напруги на конденсаторах\n"
                          "• Більше пасивних компонентів",
                          size=11, pad=8, fill="#fefde8", stroke="#f1c40f")
    f.append(b_lcc)

    return render(os.path.join(IMG, "compensation-topologies.svg"), W, H, *f)


def fig_load_modulation_waveform():
    """Осцилограми In-Band модуляції навантаженням (Backscatter Load Modulation)."""
    W, H = 920, 480
    f = []

    f.append(text(W / 2, 26, "Осцилограми In-Band модуляції навантаженням (Backscatter AM у Qi)", size=15, bold=True))

    x0 = 95
    w_graph = 760

    # 1. Сигнал керування ключем модуляції на стороні RX (MOD FET Gate)
    y1 = 80
    f.append(text(x0 - 10, y1 + 20, "RX Модуляція\n(MOD FET)", size=11, color=MAG, anchor="end", bold=True))
    f.append(rect(x0, y1, w_graph, 60, fill="#fbfcfc", stroke=MUTED, sw=1))
    f.append(line(x0, y1 + 50, x0 + w_graph, y1 + 50, sw=1, color="#d5dbdb", dash="2,2"))

    d_mod = "M %d %d " % (x0, y1 + 50)
    segments = [(60, 0), (60, 1), (60, 0), (60, 1), (120, 0), (60, 1), (60, 0), (120, 1), (120, 0), (60, 1)]
    cx = x0
    for w_s, val in segments:
        h_val = y1 + 10 if val else y1 + 50
        d_mod += "L %d %d L %d %d " % (cx, h_val, cx + w_s, h_val)
        cx += w_s
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_mod, MAG))
    f.append(text(x0 + 80, y1 + 25, "C_mod увімкнено (R_відб зростає)", size=10, color=MAG))

    # 2. Несуча високочастотна напруга на котушці TX (125 кГц AC Carrier з AM)
    y2 = 180
    f.append(text(x0 - 10, y2 + 40, "Напруга TX\n(Котушка L_tx)", size=11, color=BLUE, anchor="end", bold=True))
    f.append(rect(x0, y2, w_graph, 90, fill="#fbfcfc", stroke=MUTED, sw=1))
    f.append(line(x0, y2 + 45, x0 + w_graph, y2 + 45, sw=1, color="#d5dbdb", dash="2,2"))

    d_carrier = []
    cx = x0
    step_px = 3
    t = 0
    while cx < x0 + w_graph:
        rel_x = cx - x0
        is_mod = (60 <= rel_x < 120) or (180 <= rel_x < 240) or (360 <= rel_x < 420) or (540 <= rel_x < 660) or (720 <= rel_x)
        amp = 38 if is_mod else 24
        yy = (y2 + 45) + amp * math.sin(t * 0.7)
        d_carrier.append("%.1f,%.1f" % (cx, yy))
        cx += step_px
        t += 1

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.2"/>' % (" ".join(d_carrier), BLUE))

    d_env_top = "M %d %d " % (x0, y2 + 21)
    d_env_bot = "M %d %d " % (x0, y2 + 69)
    cx = x0
    for w_s, val in segments:
        a = 38 if val else 24
        d_env_top += "L %d %d L %d %d " % (cx, (y2 + 45) - a, cx + w_s, (y2 + 45) - a)
        d_env_bot += "L %d %d L %d %d " % (cx, (y2 + 45) + a, cx + w_s, (y2 + 45) + a)
        cx += w_s
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="3,3"/>' % (d_env_top, RED))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="3,3"/>' % (d_env_bot, RED))
    f.append(text(x0 + 260, y2 + 15, "Амплітудна модуляція ΔU ≈ 5–10%", size=10, color=RED, bold=True))

    # 3. Вихід аналогового детектора обвідної (Envelope Detector)
    y3 = 310
    f.append(text(x0 - 10, y3 + 20, "Виділена\nобвідна (TX)", size=11, color="#d35400", anchor="end", bold=True))
    f.append(rect(x0, y3, w_graph, 50, fill="#fbfcfc", stroke=MUTED, sw=1))
    cx = x0
    d_env_filt = "M %d %d " % (x0, y3 + 38)
    for w_s, val in segments:
        h_val = y3 + 12 if val else y3 + 38
        d_env_filt += "Q %d %d %d %d " % (cx + 8, h_val, cx + w_s, h_val)
        cx += w_s
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_env_filt, "#d35400"))

    f.append(line(x0, y3 + 25, x0 + w_graph, y3 + 25, sw=1.5, color="#27ae60", dash="4,3"))
    f.append(text(x0 + w_graph - 80, y3 + 20, "Поріг компаратора V_th", size=9, color="#27ae60", bold=True))

    # 4. Відновлений цифровий потік даних (BMC Data Stream до MCU)
    y4 = 395
    f.append(text(x0 - 10, y4 + 20, "Цифрові дані\n(BMC потік)", size=11, color=GREEN, anchor="end", bold=True))
    f.append(rect(x0, y4, w_graph, 50, fill="#fbfcfc", stroke=MUTED, sw=1))

    d_dig = "M %d %d " % (x0, y4 + 40)
    cx = x0
    for w_s, val in segments:
        h_val = y4 + 10 if val else y4 + 40
        d_dig += "L %d %d L %d %d " % (cx, h_val, cx + w_s, h_val)
        cx += w_s
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_dig, GREEN))

    f.append(text(x0 + 30, y4 + 28, "1", size=12, color=GREEN, bold=True))
    f.append(text(x0 + 90, y4 + 28, "1", size=12, color=GREEN, bold=True))
    f.append(text(x0 + 150, y4 + 28, "0", size=12, color=GREEN, bold=True))
    f.append(text(x0 + 210, y4 + 28, "1", size=12, color=GREEN, bold=True))
    f.append(text(x0 + 300, y4 + 28, "0", size=12, color=GREEN, bold=True))
    f.append(text(x0 + 390, y4 + 28, "1", size=12, color=GREEN, bold=True))

    return render(os.path.join(IMG, "load-modulation-waveform.svg"), W, H, *f)


def fig_qi_state_machine():
    """Діаграма станів протоколу Qi (Ping, ID & Config, Power Transfer, FOD)."""
    W, H = 940, 480
    f = []

    f.append(text(W / 2, 26, "Послідовність фаз протоколу WPC Qi", size=16, bold=True))

    y_box = 80
    h_b = 130
    w_b = 195
    step = 230

    # 1. Ping
    x1 = 25
    f.append(rect(x1, y_box, w_b, h_b, fill="#ebf5fb", stroke=BLUE, sw=1.8, rx=6))
    f.append(text(x1 + w_b / 2, y_box + 24, "1. Фаза Ping", size=13, color=BLUE, bold=True))
    f.append(text(x1 + w_b / 2, y_box + 44, "Аналоговий + Цифровий", size=10, color=MUTED))
    f.append(line(x1 + 10, y_box + 54, x1 + w_b - 10, y_box + 54, sw=1, color="#aed6f1"))
    f.append(text(x1 + w_b / 2, y_box + 72, "• TX подає імпульс 65–100 мс", size=9))
    f.append(text(x1 + w_b / 2, y_box + 88, "• Зарядка C_rect в приймачі", size=9))
    f.append(text(x1 + w_b / 2, y_box + 104, "• RX шле Signal Strength (0x01)", size=9, color=BLUE, bold=True))
    f.append(text(x1 + w_b / 2, y_box + 120, "• Перевірка добротності Q (FOD)", size=9, color=RED))

    f.append(arrow(x1 + w_b, y_box + h_b / 2, x1 + step, y_box + h_b / 2, sw=2, color=BLUE))

    # 2. Identification & Configuration
    x2 = x1 + step
    f.append(rect(x2, y_box, w_b, h_b, fill="#fef9e7", stroke="#f39c12", sw=1.8, rx=6))
    f.append(text(x2 + w_b / 2, y_box + 24, "2. ID & Конфігурація", size=13, color="#b7950b", bold=True))
    f.append(text(x2 + w_b / 2, y_box + 44, "Переговори параметрів", size=10, color=MUTED))
    f.append(line(x2 + 10, y_box + 54, x2 + w_b - 10, y_box + 54, sw=1, color="#f9e79f"))
    f.append(text(x2 + w_b / 2, y_box + 72, "• RX: Identification (0x71)", size=9))
    f.append(text(x2 + w_b / 2, y_box + 88, "• RX: Configuration (0x51)", size=9))
    f.append(text(x2 + w_b / 2, y_box + 104, "• Узгодження потужності 5W/15W", size=9, color="#b7950b", bold=True))
    f.append(text(x2 + w_b / 2, y_box + 120, "• Калібрування порогів FOD", size=9))

    f.append(arrow(x2 + w_b, y_box + h_b / 2, x2 + step, y_box + h_b / 2, sw=2, color="#f39c12"))

    # 3. Power Transfer
    x3 = x2 + step
    f.append(rect(x3, y_box, w_b, h_b, fill="#eafaf1", stroke=GREEN, sw=1.8, rx=6))
    f.append(text(x3 + w_b / 2, y_box + 24, "3. Передача енергії", size=13, color=GREEN, bold=True))
    f.append(text(x3 + w_b / 2, y_box + 44, "Замкнена петля (CEP)", size=10, color=MUTED))
    f.append(line(x3 + 10, y_box + 54, x3 + w_b - 10, y_box + 54, sw=1, color="#a9dfbf"))
    f.append(text(x3 + w_b / 2, y_box + 72, "• RX шле CEP (0x03) кожні 250 мс", size=9, color=GREEN, bold=True))
    f.append(text(x3 + w_b / 2, y_box + 88, "• TX підлаштовує частоту / ШІМ", size=9))
    f.append(text(x3 + w_b / 2, y_box + 104, "• RX шле Received Power (0x04)", size=9))
    f.append(text(x3 + w_b / 2, y_box + 120, "• Контроль втрат P_loss (FOD)", size=9, color=RED, bold=True))

    f.append(arrow(x3 + w_b, y_box + h_b / 2, x3 + step, y_box + h_b / 2, sw=2, color=GREEN))

    # 4. End of Power Transfer
    x4 = x3 + step
    f.append(rect(x4, y_box, w_b, h_b, fill="#fdf2e9", stroke="#e67e22", sw=1.8, rx=6))
    f.append(text(x4 + w_b / 2, y_box + 24, "4. Завершення (EPT)", size=13, color="#d35400", bold=True))
    f.append(text(x4 + w_b / 2, y_box + 44, "Вимкнення / Захист", size=10, color=MUTED))
    f.append(line(x4 + 10, y_box + 54, x4 + w_b - 10, y_box + 54, sw=1, color="#f5cba7"))
    f.append(text(x4 + w_b / 2, y_box + 72, "• Пакет EPT (0x02)", size=9, color="#d35400", bold=True))
    f.append(text(x4 + w_b / 2, y_box + 88, "• Батарея заряджена (100%)", size=9))
    f.append(text(x4 + w_b / 2, y_box + 104, "• Перегрів (Over-Temp)", size=9))
    f.append(text(x4 + w_b / 2, y_box + 120, "• FOD аварія (сторонній метал)", size=9, color=RED, bold=True))

    f.append('<path d="M %d %d A 30 30 0 1 1 %d %d" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
             % (x3 + w_b - 20, y_box + h_b, x3 + 20, y_box + h_b, GREEN))
    f.append(text(x3 + w_b / 2, y_box + h_b + 38, "Безперервний цикл стабілізації CEP (PID)", size=10, color=GREEN, bold=True))

    f.append('<path d="M %d %d L %d %d L %d %d L %d %d" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,4" marker-end="url(#arrow)"/>'
             % (x4 + w_b / 2, y_box + h_b, x4 + w_b / 2, 420, x1 + w_b / 2, 420, x1 + w_b / 2, y_box + h_b, RED))
    f.append(text(W / 2, 412, "Скидання у фазу пошуку (Analog Ping) після зняття пристрою або аварії FOD", size=11, color=RED, bold=True))

    return render(os.path.join(IMG, "qi-state-machine.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inductive_vs_resonant()
    fig_wpt_system_architecture()
    fig_reflected_impedance()
    fig_compensation_topologies()
    fig_load_modulation_waveform()
    fig_qi_state_machine()
    print("All figures generated successfully in ./img/")
