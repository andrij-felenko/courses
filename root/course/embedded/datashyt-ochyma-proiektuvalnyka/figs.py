# -*- coding: utf-8 -*-
"""Генерація SVG-фігур для теми «Даташит очима проєктувальника»."""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_abs_vs_operating():
    """Фігура 1: Порівняння Absolute Maximum Ratings та Recommended Operating Conditions."""
    W, H = 820, 360
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=0))

    # Заголовок шкали напруги / параметрів
    p.append(text(W / 2, 28, "Шкала параметрів компонента: від штатної роботи до теплового пробою", size=15, bold=True, color=INK))

    # Вісь параметрів горизонтальна
    y_axis = 140
    p.append(line(50, y_axis, 770, y_axis, color="#374151", sw=2))

    # Зони на осі
    # Зона 1: Рекомендована робоча зона (Recommended Operating Conditions)
    p.append(rect(60, 70, 240, 140, fill="#e8f5e9", stroke=FIELD, sw=2, rx=6))
    p.append(text(180, 95, "Рекомендовані умови", size=14, bold=True, color="#1b5e20"))
    p.append(text(180, 115, "(Recommended Operating)", size=12, italic=True, color="#2e7d32"))
    p.append(mtext(180, 145, "Гарантовані всі параметри:\n• Швидкість і таймінги\n• Рівні напруг V_OH/V_OL\n• Струм споживання", size=11, color="#1b5e20", lh=1.2))

    # Зона 2: Зона деградації / невизначеності
    p.append(rect(310, 70, 200, 140, fill="#fff8e1", stroke="#f59e0b", sw=2, rx=6))
    p.append(text(410, 95, "Зона невизначеності", size=14, bold=True, color="#b45309"))
    p.append(text(410, 115, "(Functional Degradation)", size=12, italic=True, color="#d97706"))
    p.append(mtext(410, 145, "Чіп не згорає, але:\n• Параметри «пливуть»\n• Збої логіки й таймінгів\n• Гарантії НЕ діють", size=11, color="#78350f", lh=1.2))

    # Червона межа: Absolute Maximum Ratings
    p.append(line(520, 50, 520, 230, color=POS, sw=3, dash="6,4"))
    p.append(rect(470, 235, 100, 24, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    p.append(text(520, 251, "Abs Max межа", size=11, bold=True, color=POS))

    # Зона 3: Зона руйнування (Permanent Damage)
    p.append(rect(530, 70, 230, 140, fill="#ffebee", stroke=POS, sw=2, rx=6))
    p.append(text(645, 95, "Зона руйнування", size=14, bold=True, color=POS))
    p.append(text(645, 115, "(Permanent Damage)", size=12, italic=True, color="#b91c1c"))
    p.append(mtext(645, 145, "Незворотне пошкодження:\n• Пробій оксиду затвора\n• Latch-up (тиристорний ефект)\n• Деградація кристала", size=11, color="#7f1d1d", lh=1.2))

    # Стрілка запасу (Design Margin)
    p.append(arrow(180, 290, 510, 290, color="#1e40af", sw=2))
    p.append(text(345, 280, "Інженерний запас (Safety Margin / Derating)", size=12, bold=True, color="#1e40af"))
    p.append(text(345, 315, "Проєктувальник завжди утримує схему ліворуч від Recommended Max", size=11, italic=True, color=MUTED))

    render(os.path.join(OUT, "abs-vs-operating.svg"), W, H, *p)


def fig_logic_noise_margins():
    """Фігура 2: Пороги логічних рівнів передавача та приймача із запасами завадостійкості."""
    W, H = 820, 380
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=0))

    p.append(text(W / 2, 26, "Узгодження логічних рівнів: вихід передавача (TX) проти входу приймача (RX)", size=15, bold=True, color=INK))

    # Лівий стовпчик: Передавач (Driver / Output)
    x_tx = 180
    p.append(text(x_tx, 60, "Вихід передавача (TX)", size=14, bold=True, color="#1e40af"))
    p.append(rect(x_tx - 80, 80, 160, 250, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=4))

    # Рівень V_DD
    p.append(line(x_tx - 90, 80, x_tx + 90, 80, color="#374151", sw=2))
    p.append(text(x_tx - 115, 85, "V_DD (3.3V)", size=11, bold=True, color=INK, anchor="end"))

    # V_OH min (зона High передавача)
    p.append(rect(x_tx - 75, 85, 150, 55, fill="#dbeafe", stroke="#3b82f6", sw=1.5, rx=3))
    p.append(text(x_tx, 115, "V_OH min (2.9V)", size=12, bold=True, color="#1e40af"))
    p.append(text(x_tx, 130, "Гарантована лог. 1", size=10, color="#1e40af"))

    # Невизначена зона передавача
    p.append(rect(x_tx - 75, 145, 150, 115, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=3))
    p.append(text(x_tx, 205, "Перехідний стан", size=11, italic=True, color=MUTED))

    # V_OL max (зона Low передавача)
    p.append(rect(x_tx - 75, 265, 150, 60, fill="#dbeafe", stroke="#3b82f6", sw=1.5, rx=3))
    p.append(text(x_tx, 295, "V_OL max (0.4V)", size=12, bold=True, color="#1e40af"))
    p.append(text(x_tx, 310, "Гарантований лог. 0", size=10, color="#1e40af"))

    # Рівень GND
    p.append(line(x_tx - 90, 330, x_tx + 90, 330, color="#374151", sw=2))
    p.append(text(x_tx - 115, 335, "GND (0V)", size=11, bold=True, color=INK, anchor="end"))

    # Правий стовпчик: Приймач (Receiver / Input)
    x_rx = 640
    p.append(text(x_rx, 60, "Вхід приймача (RX)", size=14, bold=True, color="#047857"))
    p.append(rect(x_rx - 80, 80, 160, 250, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=4))

    # Рівень V_DD
    p.append(line(x_rx - 90, 80, x_rx + 90, 80, color="#374151", sw=2))
    p.append(text(x_rx + 115, 85, "V_DD (3.3V)", size=11, bold=True, color=INK, anchor="start"))

    # V_IH min (зона High приймача)
    p.append(rect(x_rx - 75, 85, 150, 90, fill="#d1fae5", stroke="#10b981", sw=1.5, rx=3))
    p.append(text(x_rx, 125, "V_IH min (2.3V)", size=12, bold=True, color="#065f46"))
    p.append(text(x_rx, 142, "Поріг розпізнавання 1", size=10, color="#065f46"))

    # Заборонена зона приймача (Undefined)
    p.append(rect(x_rx - 75, 180, 150, 70, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=3))
    p.append(text(x_rx, 210, "Заборонена зона", size=11, bold=True, color="#991b1b"))
    p.append(text(x_rx, 226, "(Метастабільність)", size=10, italic=True, color="#991b1b"))

    # V_IL max (зона Low приймача)
    p.append(rect(x_rx - 75, 255, 150, 70, fill="#d1fae5", stroke="#10b981", sw=1.5, rx=3))
    p.append(text(x_rx, 285, "V_IL max (0.8V)", size=12, bold=True, color="#065f46"))
    p.append(text(x_rx, 302, "Поріг розпізнавання 0", size=10, color="#065f46"))

    # Рівень GND
    p.append(line(x_rx - 90, 330, x_rx + 90, 330, color="#374151", sw=2))
    p.append(text(x_rx + 115, 335, "GND (0V)", size=11, bold=True, color=INK, anchor="start"))

    # Центральна область: Запас завадостійкості
    # Верхній запас: N_MH = V_OH min - V_IH min = 2.9 - 2.3 = 0.6V
    p.append(line(x_tx + 80, 140, 390, 140, color="#2563eb", sw=1.5, dash="4,4"))
    p.append(line(x_rx - 80, 175, 430, 175, color="#059669", sw=1.5, dash="4,4"))

    p.append(rect(320, 120, 180, 50, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=5))
    p.append(text(410, 140, "Запас лог. 1 (N_MH)", size=11, bold=True, color="#1e40af"))
    p.append(text(410, 158, "V_OH min − V_IH min = 0.6 В", size=10, color="#1e40af"))

    # Нижній запас: N_ML = V_IL max - V_OL max = 0.8 - 0.4 = 0.4V
    p.append(line(x_tx + 80, 265, 390, 265, color="#2563eb", sw=1.5, dash="4,4"))
    p.append(line(x_rx - 80, 255, 430, 255, color="#059669", sw=1.5, dash="4,4"))

    p.append(rect(320, 240, 180, 50, fill="#ecfdf5", stroke="#10b981", sw=1.5, rx=5))
    p.append(text(410, 260, "Запас лог. 0 (N_ML)", size=11, bold=True, color="#065f46"))
    p.append(text(410, 278, "V_IL max − V_OL max = 0.4 В", size=10, color="#065f46"))

    render(os.path.join(OUT, "logic-noise-margins.svg"), W, H, *p)


def fig_mlcc_dc_bias():
    """Фігура 3: Падіння реальної ємності керамічних конденсаторів (DC Bias Derating)."""
    W, H = 820, 360
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=0))

    p.append(text(W / 2, 26, "Ефект зміщення постійною напругою (DC-Bias) у MLCC ємністю 10 мкФ", size=15, bold=True, color=INK))

    # Вісь графіка: X — напруга (0..16 В), Y — ефективна ємність (0..100% / 0..10 мкФ)
    gx, gy, gw, gh = 100, 60, 480, 240
    p.append(rect(gx, gy, gw, gh, fill="#fafafa", stroke="#9ca3af", sw=1.5, rx=0))

    # Горизонтальні сітки (Ємність)
    for i, pct in enumerate([100, 80, 60, 40, 20, 0]):
        y = gy + i * (gh / 5)
        p.append(line(gx, y, gx + gw, y, color="#e5e7eb", sw=1))
        p.append(text(gx - 10, y + 4, "%d%%" % pct, size=11, color=MUTED, anchor="end"))

    # Вертикальні сітки (Напруга)
    for i, v in enumerate([0, 3.3, 5.0, 10.0, 16.0]):
        x = gx + (v / 16.0) * gw
        p.append(line(x, gy, x, gy + gh, color="#e5e7eb", sw=1))
        p.append(text(x, gy + gh + 18, "%.1f В" % v, size=11, color=MUTED, anchor="middle"))

    p.append(text(gx + gw / 2, gy + gh + 38, "Прикладена постійна напруга (DC Bias Voltage)", size=12, bold=True, color=INK))
    p.append(text(gx - 45, gy + gh / 2, "Залишкова ємність", size=12, bold=True, color=INK, anchor="middle"))

    # Криві:
    # 1. C0G / NP0 (стабільний, 100%)
    p.append(line(gx, gy, gx + gw, gy, color="#10b981", sw=3))

    # 2. X7R 1206 (помірне падіння: 0V->100%, 3.3V->88%, 5V->80%, 10V->60%, 16V->42%)
    pts_1206 = [
        (0, 1.0), (1.5, 0.95), (3.3, 0.88), (5.0, 0.80), (8.0, 0.68), (10.0, 0.60), (13.0, 0.49), (16.0, 0.42)
    ]
    svg_pts_1206 = " ".join(["%.1f,%.1f" % (gx + (v / 16.0) * gw, gy + (1.0 - c) * gh) for v, c in pts_1206])
    p.append('<polyline points="%s" fill="none" stroke="#2563eb" stroke-width="2.5"/>' % svg_pts_1206)

    # 3. X7R 0603 (значне падіння: 0V->100%, 3.3V->62%, 5V->48%, 10V->28%, 16V->16%)
    pts_0603 = [
        (0, 1.0), (1.5, 0.80), (3.3, 0.62), (5.0, 0.48), (8.0, 0.35), (10.0, 0.28), (13.0, 0.21), (16.0, 0.16)
    ]
    svg_pts_0603 = " ".join(["%.1f,%.1f" % (gx + (v / 16.0) * gw, gy + (1.0 - c) * gh) for v, c in pts_0603])
    p.append('<polyline points="%s" fill="none" stroke="#f59e0b" stroke-width="2.5"/>' % svg_pts_0603)

    # 4. X5R 0402 (катастрофічне падіння: 0V->100%, 3.3V->32%, 5V->18%, 10V->9%, 16V->5%)
    pts_0402 = [
        (0, 1.0), (1.0, 0.65), (2.0, 0.48), (3.3, 0.32), (5.0, 0.18), (8.0, 0.12), (10.0, 0.09), (16.0, 0.05)
    ]
    svg_pts_0402 = " ".join(["%.1f,%.1f" % (gx + (v / 16.0) * gw, gy + (1.0 - c) * gh) for v, c in pts_0402])
    p.append('<polyline points="%s" fill="none" stroke="#ef4444" stroke-width="2.5"/>' % svg_pts_0402)

    # Легенда праворуч
    lx, ly = 610, 75
    p.append(rect(lx, ly, 190, 215, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=5))
    p.append(text(lx + 95, ly + 22, "Типи діелектриків і корпусів", size=11, bold=True, color=INK))

    p.append(line(lx + 15, ly + 50, lx + 45, ly + 50, color="#10b981", sw=3))
    p.append(text(lx + 55, ly + 54, "C0G / NP0 (0% втрат)", size=11, color="#065f46", anchor="start"))

    p.append(line(lx + 15, ly + 85, lx + 45, ly + 85, color="#2563eb", sw=2.5))
    p.append(text(lx + 55, ly + 89, "X7R 1206 (10 мкФ)", size=11, color="#1e40af", anchor="start"))

    p.append(line(lx + 15, ly + 120, lx + 45, ly + 120, color="#f59e0b", sw=2.5))
    p.append(text(lx + 55, ly + 124, "X7R 0603 (10 мкФ)", size=11, color="#b45309", anchor="start"))

    p.append(line(lx + 15, ly + 155, lx + 45, ly + 155, color="#ef4444", sw=2.5))
    p.append(text(lx + 55, ly + 159, "X5R 0402 (10 мкФ)", size=11, color="#991b1b", anchor="start"))

    p.append(mtext(lx + 95, ly + 185, "У корпусі 0402 на 3.3 В\nлишається лише ~3.2 мкФ!", size=10, bold=True, color="#991b1b", lh=1.2))

    render(os.path.join(OUT, "mlcc-dc-bias.svg"), W, H, *p)


def fig_interface_timings():
    """Фігура 4: Таймінги інтерфейсу (Setup, Hold, RC rise time) та спотворення шини."""
    W, H = 820, 360
    p = []
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=0))

    p.append(text(W / 2, 26, "Часові вимоги синхронної шини: тактовий фронт, Setup / Hold та RC-затягування", size=15, bold=True, color=INK))

    # 1. Тактовий сигнал (CLK)
    y_clk = 95
    p.append(text(75, y_clk + 15, "Тактовий CLK", size=12, bold=True, color="#1e40af", anchor="end"))
    # Низький рівень -> фронт -> високий -> спад -> низький
    # Фронт на x = 380
    clk_path = "M 90,%d L 360,%d L 380,%d L 580,%d L 600,%d L 760,%d" % (
        y_clk + 30, y_clk + 30, y_clk - 10, y_clk - 10, y_clk + 30, y_clk + 30
    )
    p.append('<path d="%s" fill="none" stroke="#2563eb" stroke-width="2.5"/>' % clk_path)

    # Вертикальна лінія стробування (Latch Edge)
    p.append(line(380, 50, 380, 310, color=POS, sw=1.8, dash="5,4"))
    p.append(text(380, 45, "Активний фронт стробування", size=11, bold=True, color=POS))

    # 2. Ідеальні дані (DATA)
    y_data = 185
    p.append(text(75, y_data + 15, "Шина DATA", size=12, bold=True, color="#059669", anchor="end"))

    # Валідне вікно даних: перехід перед фронтом за t_setup, перехід після фронту через t_hold
    # Перехід на x = 220 (за 160px до фронту), перехід на x = 500 (через 120px після фронту)
    # Верхня і нижня лінії шини
    p.append(line(90, y_data - 10, 200, y_data - 10, color="#9ca3af", sw=1.5))
    p.append(line(90, y_data + 30, 200, y_data + 30, color="#9ca3af", sw=1.5))
    # Хрест переходу
    p.append(line(200, y_data - 10, 230, y_data + 30, color="#10b981", sw=2))
    p.append(line(200, y_data + 30, 230, y_data - 10, color="#10b981", sw=2))
    # Валідне вікно
    p.append(rect(230, y_data - 10, 250, 40, fill="#d1fae5", stroke="#10b981", sw=1.5, rx=0))
    p.append(text(355, y_data + 14, "СТАБІЛЬНІ ДАНІ", size=11, bold=True, color="#065f46"))
    # Хрест виходу
    p.append(line(480, y_data - 10, 510, y_data + 30, color="#10b981", sw=2))
    p.append(line(480, y_data + 30, 510, y_data - 10, color="#10b981", sw=2))
    p.append(line(510, y_data - 10, 760, y_data - 10, color="#9ca3af", sw=1.5))
    p.append(line(510, y_data + 30, 760, y_data + 30, color="#9ca3af", sw=1.5))

    # Стрілки t_setup та t_hold
    # t_setup: від 230 до 380
    p.append(arrow(230, y_data - 25, 380, y_data - 25, color="#b45309", sw=1.5))
    p.append(arrow(380, y_data - 25, 230, y_data - 25, color="#b45309", sw=1.5))
    p.append(text(305, y_data - 33, "t_setup (час встановлення)", size=11, bold=True, color="#b45309"))

    # t_hold: від 380 до 480
    p.append(arrow(380, y_data - 25, 480, y_data - 25, color="#b45309", sw=1.5))
    p.append(arrow(480, y_data - 25, 380, y_data - 25, color="#b45309", sw=1.5))
    p.append(text(430, y_data - 33, "t_hold", size=11, bold=True, color="#b45309"))

    # 3. Реальний фронт зі спотворенням (RC Bus Capacitance)
    y_rc = 280
    p.append(text(75, y_rc + 10, "Реальний сигнал\n(RC затягування)", size=11, bold=True, color="#dc2626", anchor="end"))

    # Експоненційне наростання через R_pullup та C_bus
    rc_path = "M 90,%d L 200,%d Q 280,%d 440,%d L 760,%d" % (
        y_rc + 25, y_rc + 25, y_rc + 20, y_rc - 10, y_rc - 10
    )
    p.append('<path d="%s" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="5,3"/>' % rc_path)

    # Поріг V_IH
    p.append(line(90, y_rc + 3, 760, y_rc + 3, color="#6b7280", sw=1, dash="3,3"))
    p.append(text(765, y_rc + 7, "V_IH поріг", size=10, color=MUTED, anchor="start"))

    # Затягнутий перетин порогу
    p.append(circle(360, y_rc + 3, 4, fill=POS, stroke=POS, sw=1))
    p.append(text(430, y_rc + 35, "Перетин V_IH надто пізно: порушення t_setup!", size=10, bold=True, color=POS))

    render(os.path.join(OUT, "interface-timings.svg"), W, H, *p)


if __name__ == "__main__":
    fig_abs_vs_operating()
    fig_logic_noise_margins()
    fig_mlcc_dc_bias()
    fig_interface_timings()
    print("Всі фігури успішно згенеровано.")
