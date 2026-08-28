# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми power-monitor (Давач живлення: струм і напруга на борту)."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, textbox, fitbox, text, mtext, line, arrow, rect, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_power_monitor_topology():
    """Схеми High-Side та Low-Side вимірювання струму та напруги."""
    w, h = 900, 440
    frags = []

    # ── Лівий блок: High-Side ──
    frags.append(fitbox(20, 20, 420, 400, "", fill="#fdfefe", stroke="#b0bec5", sw=1.2, rx=8))
    frags.append(text(230, 45, "High-Side включення (в плюсовій шині)", size=14, bold=True, color=POS))

    # Джерело живлення
    frags.append(textbox(75, 95, "Джерело\n+V_BUS", size=11, bold=True, fill="#fff3e0", stroke="#ff9800")[0])
    # Шунт
    frags.append(textbox(230, 95, "Шунт R_shunt\n(Кельвін)", size=11, bold=True, fill="#e8f5e9", stroke=FIELD)[0])
    # Навантаження
    frags.append(textbox(375, 190, "Навантаження\n(Load)", size=11, bold=True, fill="#ede7f6", stroke="#673ab7")[0])
    # Земля
    frags.append(textbox(375, 290, "Системна земля\nGND (0 В)", size=11, bold=True, fill="#eceff1", stroke="#607d8b")[0])

    # Провідники High-side
    frags.append(arrow(115, 95, 175, 95, color=LINE, sw=2))
    frags.append(arrow(285, 95, 375, 95, color=LINE, sw=2))
    frags.append(line(375, 95, 375, 165, color=LINE, sw=2))
    frags.append(arrow(375, 215, 375, 265, color=LINE, sw=2))
    frags.append(line(75, 120, 75, 290, color=LINE, sw=2))
    frags.append(line(75, 290, 315, 290, color=LINE, sw=2))

    # Вимірювач
    frags.append(textbox(230, 210, "Монітор живлення\n(INA226 / CSA)\nV_CM ≈ V_BUS", size=10, bold=True, fill="#e3f2fd", stroke=NEG)[0])
    frags.append(line(190, 115, 190, 185, color=NEG, sw=1.5, dash="3,3"))
    frags.append(line(270, 115, 270, 185, color=NEG, sw=1.5, dash="3,3"))
    frags.append(text(180, 150, "IN+", size=10, color=NEG, bold=True, anchor="end"))
    frags.append(text(280, 150, "IN−", size=10, color=NEG, bold=True, anchor="start"))
    frags.append(line(230, 235, 230, 290, color="#607d8b", sw=1.5, dash="3,3"))
    frags.append(text(238, 265, "GND", size=9, color="#607d8b", anchor="start"))

    # Пояснення High-side
    hs_notes = [
        "✓ Земля навантаження чиста (немає зміщення GND)",
        "✓ Фіксує коротке замикання в навантаженні на землю",
        "! Потребує високого придушення синфазної завади (CMRR)",
        "! Вхідні виводи підняті до повної напруги шини V_BUS"
    ]
    frags.append(textbox(230, 360, "\n".join(hs_notes), size=9.5, fill="#fafafa", stroke="#cfd8dc", pad=6)[0])

    # ── Правий блок: Low-Side ──
    frags.append(fitbox(460, 20, 420, 400, "", fill="#fdfefe", stroke="#b0bec5", sw=1.2, rx=8))
    frags.append(text(670, 45, "Low-Side включення (у зворотній шині)", size=14, bold=True, color=NEG))

    # Джерело живлення
    frags.append(textbox(515, 95, "Джерело\n+V_BUS", size=11, bold=True, fill="#fff3e0", stroke="#ff9800")[0])
    # Навантаження
    frags.append(textbox(670, 95, "Навантаження\n(Load)", size=11, bold=True, fill="#ede7f6", stroke="#673ab7")[0])
    # Шунт
    frags.append(textbox(815, 190, "Шунт R_shunt\n(Low-Side)", size=11, bold=True, fill="#e8f5e9", stroke=FIELD)[0])
    # Земля
    frags.append(textbox(815, 290, "Системна земля\nGND (0 В)", size=11, bold=True, fill="#eceff1", stroke="#607d8b")[0])

    # Провідники Low-side
    frags.append(arrow(555, 95, 615, 95, color=LINE, sw=2))
    frags.append(line(725, 95, 815, 95, color=LINE, sw=2))
    frags.append(arrow(815, 95, 815, 165, color=LINE, sw=2))
    frags.append(arrow(815, 215, 815, 265, color=LINE, sw=2))
    frags.append(line(515, 120, 515, 290, color=LINE, sw=2))
    frags.append(line(515, 290, 755, 290, color=LINE, sw=2))

    # Позначка підйому землі
    frags.append(textbox(720, 140, "Зсув землі:\nV = I · R_shunt", size=9, fill="#fffde7", stroke="#fbc02d", pad=4)[0])

    # Вимірювач Low-side
    frags.append(textbox(670, 210, "Підсилювач / АЦП\n(V_CM ≈ 0 В)\nПростий ОП", size=10, bold=True, fill="#e3f2fd", stroke=NEG)[0])
    frags.append(line(765, 180, 725, 200, color=NEG, sw=1.5, dash="3,3"))
    frags.append(line(765, 200, 725, 215, color=NEG, sw=1.5, dash="3,3"))

    # Пояснення Low-side
    ls_notes = [
        "✓ Синфазна напруга мінімальна (V_CM ≈ 0 В)",
        "✓ Можливе використання дешевого операційного підсилювача",
        "✗ Піднімає локальну землю навантаження (Ground Bounce)",
        "✗ НЕ бачить витоків струму та КЗ з шини +V на корпус/землю"
    ]
    frags.append(textbox(670, 360, "\n".join(ls_notes), size=9.5, fill="#fafafa", stroke="#cfd8dc", pad=6)[0])

    render(os.path.join(OUT_DIR, "fig-power-monitor-topology.svg"), w, h, *frags)


def fig_ina226_architecture():
    """Внутрішня архітектура мікросхеми монітора живлення (INA226 / PAC1934)."""
    w, h = 940, 460
    frags = []

    # Головний корпус мікросхеми
    frags.append(rect(130, 25, 670, 415, fill="#ffffff", stroke="#37474f", sw=2, rx=10))
    frags.append(text(465, 50, "Внутрішня архітектура цифрового монітора живлення (INA226)", size=14, bold=True, color="#263238"))

    # Зовнішні входи ліворуч
    frags.append(textbox(55, 105, "IN+\n(Шунт +)", size=10, bold=True, fill="#ffebee", stroke=POS)[0])
    frags.append(textbox(55, 165, "IN−\n(Шунт −)", size=10, bold=True, fill="#ffebee", stroke=POS)[0])
    frags.append(textbox(55, 260, "VBUS\n(0..36 В)", size=10, bold=True, fill="#fff3e0", stroke="#ff9800")[0])

    # Вхідний чоппер / PGA для шунта
    frags.append(fitbox(150, 85, 130, 115, "Чоппер-підсилювач\n(Chop-Stabilized\nPGA, CMRR>120dB\nV_OS < 10 μV)", size=9.5, bold=True, fill="#e8f5e9", stroke=FIELD))
    frags.append(arrow(90, 105, 150, 120, color=POS, sw=1.8))
    frags.append(arrow(90, 165, 150, 160, color=POS, sw=1.8))

    # Дільник напруги шини VBUS
    frags.append(fitbox(150, 230, 130, 65, "Прецизійний\nдільник VBUS\n(R1 / R2)", size=9.5, bold=True, fill="#fff8e1", stroke="#fbc02d"))
    frags.append(arrow(90, 260, 150, 260, color="#ff9800", sw=1.8))

    # Дельта-сигма АЦП
    frags.append(fitbox(305, 125, 120, 145, "16-розрядний\nΔΣ АЦП\n+\nЦифровий фільтр\n(T_int, усереднення)", size=9.5, bold=True, fill="#e1f5fe", stroke=NEG))
    frags.append(arrow(280, 145, 305, 170, color=FIELD, sw=1.8))
    frags.append(arrow(280, 260, 305, 230, color="#fbc02d", sw=1.8))

    # Опорна напруга VREF
    frags.append(fitbox(305, 300, 120, 55, "Внутрішній VREF\n(Precision Bandgap\n±0.1% дрейф)", size=9, bold=True, fill="#f3e5f5", stroke="#8e24aa"))
    frags.append(arrow(365, 300, 365, 270, color="#8e24aa", sw=1.5))

    # Регістри сирих значень
    frags.append(textbox(490, 115, "Регістр напруги шунта\n(Shunt Voltage Reg)", size=9, bold=True, fill="#f1f8e9", stroke=FIELD)[0])
    frags.append(textbox(490, 260, "Регістр напруги шини\n(Bus Voltage Reg)", size=9, bold=True, fill="#fffde7", stroke="#fbc02d")[0])
    frags.append(arrow(425, 170, 480, 130, color=NEG, sw=1.5))
    frags.append(arrow(425, 230, 480, 245, color=NEG, sw=1.5))

    # Калібрувальний регістр
    frags.append(textbox(490, 185, "Калібрувальний регістр\n(Calibration Reg)", size=9, bold=True, fill="#e0f2f1", stroke="#00897b")[0])

    # Апаратний помножувач
    frags.append(fitbox(645, 125, 140, 110, "Апаратний\nпомножувач\nI = (V_sh · CAL)/2048\nP = (I · V_bus)/20000", size=9, bold=True, fill="#fce4ec", stroke="#d81b60"))
    frags.append(arrow(575, 115, 645, 145, color=FIELD, sw=1.5))
    frags.append(arrow(575, 185, 645, 175, color="#00897b", sw=1.5))
    frags.append(arrow(575, 260, 645, 205, color="#fbc02d", sw=1.5))

    # Регістри струму й потужності
    frags.append(textbox(715, 290, "Регістри струму\nй потужності", size=9, bold=True, fill="#f8bbd0", stroke="#c2185b")[0])
    frags.append(arrow(715, 235, 715, 265, color="#d81b60", sw=1.5))

    # Компаратор тривог ALERT
    frags.append(fitbox(450, 365, 200, 60, "Компаратор ALERT\n(Overcurrent, Overvoltage,\nPower Limit, Ready)", size=9, bold=True, fill="#ffebee", stroke=POS))
    frags.append(arrow(550, 395, 830, 395, color=POS, sw=1.8))
    frags.append(textbox(870, 395, "ALERT\n(Open Drain)", size=9.5, bold=True, fill="#ffebee", stroke=POS)[0])

    # Цифровий інтерфейс I2C праворуч
    frags.append(fitbox(825, 140, 95, 130, "I2C / SMBus\nІнтерфейс\n(SCL, SDA,\nАдреси A0/A1)", size=9.5, bold=True, fill="#e8eaf6", stroke="#3f51b5"))
    frags.append(arrow(785, 175, 825, 175, color="#3f51b5", sw=1.5))
    frags.append(arrow(785, 290, 825, 230, color="#3f51b5", sw=1.5))

    render(os.path.join(OUT_DIR, "fig-ina226-architecture.svg"), w, h, *frags)


def fig_hall_vs_shunt():
    """Порівняння вимірювання струму: Резистивний шунт проти давача Холла."""
    w, h = 900, 410
    frags = []

    # ── Ліва колонка: Шунт ──
    frags.append(fitbox(20, 20, 420, 370, "", fill="#ffffff", stroke="#b0bec5", sw=1.2, rx=8))
    frags.append(text(230, 45, "Резистивний шунт (Kelvin Shunt)", size=14, bold=True, color=FIELD))

    # Схема шунта
    frags.append(rect(100, 75, 260, 50, fill="#e8f5e9", stroke=FIELD, sw=2, rx=4))
    frags.append(text(230, 95, "Резистивний сплав (Манганін / Zeranin)", size=9.5, bold=True, color=FIELD))
    frags.append(text(230, 112, "R_shunt = 1..10 мΩ, низький TCR", size=9.5, color=INK))

    # Силові та сенсорні виводи
    frags.append(arrow(40, 100, 100, 100, color=POS, sw=3))
    frags.append(text(65, 88, "I_in", size=10, bold=True, color=POS))
    frags.append(arrow(360, 100, 420, 100, color=POS, sw=3))
    frags.append(text(395, 88, "I_out", size=10, bold=True, color=POS))

    frags.append(line(145, 125, 145, 160, color=NEG, sw=1.8))
    frags.append(line(315, 125, 315, 160, color=NEG, sw=1.8))
    frags.append(text(145, 175, "Sense +", size=9.5, bold=True, color=NEG))
    frags.append(text(315, 175, "Sense −", size=9.5, bold=True, color=NEG))
    frags.append(text(230, 160, "V_shunt = I · R_shunt (мВ)", size=10, bold=True, color=INK))

    shunt_chars = [
        "✓ Максимальна точність (до 0.1% з калібруванням)",
        "✓ Нечутливий до зовнішніх магнітних полів",
        "✓ Немає магнітного гістерезису та залишкової індукції",
        "✗ Гальванічний зв'язок із високовольтною шиною",
        "✗ Омічні втрати тепла P = I²·R на великих струмах (>50 А)",
        "✗ Саморозігрів викликає дрейф опору (TCR)"
    ]
    frags.append(textbox(230, 285, "\n".join(shunt_chars), size=9.5, fill="#f1f8e9", stroke="#c5e1a5", pad=8)[0])

    # ── Права колонка: Давач Холла ──
    frags.append(fitbox(460, 20, 420, 370, "", fill="#ffffff", stroke="#b0bec5", sw=1.2, rx=8))
    frags.append(text(670, 45, "Давач на ефекті Холла (ACS712 / TMCS1100)", size=14, bold=True, color="#d81b60"))

    # Схема Холла
    frags.append(rect(490, 75, 95, 50, fill="#ffebee", stroke=POS, sw=2, rx=4))
    frags.append(text(537, 100, "Силова петля\n(1.2 мΩ)", size=9.5, bold=True, color=POS))
    frags.append(arrow(465, 100, 490, 100, color=POS, sw=3))
    frags.append(arrow(585, 100, 615, 100, color=POS, sw=3))

    # Гальванічний бар'єр
    frags.append(line(630, 65, 630, 145, color="#78909c", sw=2, dash="4,4"))
    frags.append(text(630, 160, "Бар'єр 3-5 кВ", size=9, bold=True, color="#546e7a", anchor="middle"))

    # Чіп Холла
    frags.append(rect(650, 75, 160, 50, fill="#fce4ec", stroke="#d81b60", sw=1.8, rx=4))
    frags.append(text(730, 95, "Магнітне поле B ∝ I", size=9.5, bold=True, color="#d81b60"))
    frags.append(text(730, 112, "Елемент Холла + TIA", size=9.5, color=INK))
    frags.append(arrow(810, 100, 855, 100, color=NEG, sw=1.8))
    frags.append(text(860, 95, "V_OUT", size=9, bold=True, color=NEG, anchor="start"))

    hall_chars = [
        "✓ Повна гальванічна розв'язка (безпека до 400..1000 В)",
        "✓ Мінімальне виділення тепла на надвеликих струмах",
        "✓ Не обмежує синфазну напругу силового кола",
        "✗ Чутливий до зовнішніх магнітних полів (мотори, дроселі)",
        "✗ Початкове зміщення нуля (Zero Offset) та шум",
        "✗ Температурний дрейф чутливості й гістерезис"
    ]
    frags.append(textbox(670, 285, "\n".join(hall_chars), size=9.5, fill="#fce4ec", stroke="#f48fb1", pad=8)[0])

    render(os.path.join(OUT_DIR, "fig-hall-vs-shunt.svg"), w, h, *frags)


def fig_error_budget_tcr():
    """Джерела похибок: зміщення нуля на малому струмі, саморозігрів на великому струмі."""
    w, h = 860, 380
    frags = []

    # Заголовок
    frags.append(text(430, 30, "Розподіл похибок вимірювання струму та потужності за діапазоном", size=14, bold=True, color=INK))

    # Вісь X та Y
    frags.append(arrow(80, 280, 800, 280, color=LINE, sw=2))
    frags.append(arrow(80, 280, 80, 55, color=LINE, sw=2))
    frags.append(text(800, 305, "Вимірюваний струм I_load (А)", size=11, bold=True, color=INK, anchor="end"))
    frags.append(text(75, 45, "Відносна похибка вимірювання (%)", size=11, bold=True, color=INK, anchor="start"))

    # Блоки опису зон
    frags.append(fitbox(95, 75, 225, 85, "Зона малого струму:\nДомінує зміщення нуля (V_OS)\nε_offset = V_OS / (I · R_shunt)\n(10 μV при 100 μV дає 10%!)", size=9.5, fill="#ffebee", stroke=POS))
    frags.append(arrow(200, 165, 150, 215, color=POS, sw=1.5))

    frags.append(fitbox(340, 75, 210, 80, "Оптимальний діапазон:\nПохибка < 0.2%..0.5%\nДомінує початковий допуск R\nта нелінійність АЦП (INL)", size=9.5, fill="#e8f5e9", stroke=FIELD))
    frags.append(arrow(445, 160, 445, 240, color=FIELD, sw=1.5))

    frags.append(fitbox(570, 75, 245, 90, "Зона великого струму:\nДомінує саморозігрів шунта (P=I²R)\nДрейф опору через TCR:\nΔR = R_0 · TCR · ΔT\n(50 ppm/°C при ΔT=60°C → +0.3%)", size=9.5, fill="#fff3e0", stroke="#ff9800"))
    frags.append(arrow(685, 170, 725, 220, color="#ff9800", sw=1.5))

    # Спрощена стилізована крива похибки
    curve_points = [
        (100, 85), (120, 120), (150, 170), (200, 215), (280, 245),
        (445, 255), (590, 245), (670, 220), (740, 175), (770, 130)
    ]
    path_d = ["M %d %d" % curve_points[0]]
    for pt in curve_points[1:]:
        path_d.append("L %d %d" % pt)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(path_d), NEG))

    frags.append(circle(445, 255, 5, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(text(445, 272, "Мінімум похибки", size=9.5, bold=True, color=FIELD))

    # Підписи осей
    frags.append(text(120, 300, "I_min", size=10, bold=True, color=MUTED))
    frags.append(text(445, 300, "I_nominal", size=10, bold=True, color=MUTED))
    frags.append(text(740, 300, "I_max", size=10, bold=True, color=MUTED))

    render(os.path.join(OUT_DIR, "fig-error-budget-tcr.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_power_monitor_topology()
    fig_ina226_architecture()
    fig_hall_vs_shunt()
    fig_error_budget_tcr()
    print("All figures generated successfully.")
