# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Топологія кварцового генератора з охоронним кільцем ───────────────────
def fig_crystal_guard():
    W, H = 840, 480
    f = []

    # Заголовок
    f.append(text(W / 2, 28, "Топологія кварцового генератора: охоронне кільце, симетрія й повернення струму", size=16, bold=True))

    # Тло друкованої плати (Layer 1 Top)
    f.append(rect(30, 50, 780, 410, fill="#f9fbfa", stroke="#c8d1cd", sw=1.5, rx=8))
    f.append(text(50, 75, "Шар L1 (Top): Сигнали та охоронне кільце", size=12, color=MUTED, anchor="start", bold=True))

    # Корпус мікроконтролера (MCU) зліва
    mcu_x, mcu_y, mcu_w, mcu_h = 50, 110, 140, 310
    f.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#2c3e50", stroke="#1a252f", sw=2, rx=4))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 35, "Мікроконтролер", size=14, color="#ffffff", bold=True))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 55, "(MCU / SoC)", size=12, color="#bdc3c7"))

    # Піни MCU
    pin_y_in = 180
    pin_y_out = 240
    pin_y_gnd = 320

    # Виводи MCU (пади без накладання)
    for py, label, col in [(pin_y_in, "OSC_IN", "#e74c3c"), (pin_y_out, "OSC_OUT", "#e67e22"), (pin_y_gnd, "VSS_OSC", "#27ae60")]:
        f.append(rect(mcu_x + mcu_w, py - 10, 18, 20, fill="#f1c40f", stroke="#d4ac0d", sw=1.2, rx=2))
        f.append(text(mcu_x + mcu_w - 10, py + 5, label, size=11, color="#ffffff", anchor="end", bold=True))

    # ── Keep-Out Zone (Зона заборони трасування) під кварцом
    ko_x, ko_y, ko_w, ko_h = 265, 95, 480, 340
    f.append(rect(ko_x, ko_y, ko_w, ko_h, fill="#fff5f5", stroke="#e74c3c", sw=1.5, rx=6))
    f.append(text(ko_x + ko_w / 2, ko_y + 22, "Зона заборони (Keep-Out): жодних сторонніх сигналів на L1–L4", size=12, color=POS, bold=True))

    # ── Охоронне кільце (Guard Ring)
    gr_x, gr_y, gr_w, gr_h = 280, 125, 450, 290
    f.append(rect(gr_x, gr_y, gr_w, gr_h, fill="none", stroke="#27ae60", sw=4, rx=6))
    f.append(text(gr_x + gr_w - 15, gr_y + 24, "Guard Ring (AGND / VSS)", size=12, color=FIELD, anchor="end", bold=True))

    # Перехідні отвори (Vias) на охоронному кільці до суцільної землі L2
    via_coords = [
        (295, 140), (375, 140), (465, 140), (555, 140), (645, 140), (715, 140),
        (715, 210), (715, 280), (715, 350), (715, 400),
        (295, 400), (375, 400), (465, 400), (555, 400), (645, 400),
        (295, 210), (295, 280), (295, 350)
    ]
    for vx, vy in via_coords:
        f.append(circle(vx, vy, 6, fill="#27ae60", stroke="#1e8449", sw=1.5))
        f.append(circle(vx, vy, 2.5, fill="#ffffff", stroke="none"))

    # Пояснення до перехідних отворів
    f.append(text(540, 430, "GND Stitching Vias на шар L2 (крок λ/20)", size=11, color=FIELD))

    # ── Демпфуючий резистор Rd у лінії OSC_OUT
    rd_x, rd_y, rd_w, rd_h = 320, pin_y_out - 12, 36, 24
    f.append(line(mcu_x + mcu_w + 18, pin_y_out, rd_x, pin_y_out, color="#e67e22", sw=3))
    f.append(rect(rd_x, rd_y, rd_w, rd_h, fill="#34495e", stroke="#1a252f", sw=1.5, rx=2))
    f.append(text(rd_x + rd_w / 2, rd_y - 8, "Rd", size=12, color=INK, bold=True))
    f.append(text(rd_x + rd_w / 2, rd_y + 16, "демпфер", size=9, color="#ecf0f1"))

    # Доріжка від OSC_IN
    f.append(line(mcu_x + mcu_w + 18, pin_y_in, 440, pin_y_in, color="#e74c3c", sw=3))
    f.append(line(rd_x + rd_w, pin_y_out, 440, pin_y_out, color="#e67e22", sw=3))

    # ── Кварцовий резонатор (XTAL SMD 4-pin)
    xt_x, xt_y, xt_w, xt_h = 440, 160, 110, 100
    f.append(rect(xt_x, xt_y, xt_w, xt_h, fill="#ecf0f1", stroke="#7f8c8d", sw=2, rx=4))
    f.append(text(xt_x + xt_w / 2, xt_y + 45, "Кварцовий", size=13, bold=True, color="#2c3e50"))
    f.append(text(xt_x + xt_w / 2, xt_y + 65, "резонатор", size=13, bold=True, color="#2c3e50"))

    # Пади кварцу (винесені зовні корпусу резонатора)
    # Pad 1 (In)
    f.append(rect(xt_x - 16, pin_y_in - 10, 16, 20, fill="#f1c40f", stroke="#d4ac0d", sw=1.2, rx=2))
    # Pad 2 (Out)
    f.append(rect(xt_x - 16, pin_y_out - 10, 16, 20, fill="#f1c40f", stroke="#d4ac0d", sw=1.2, rx=2))
    # Pad 3, 4 (GND кришки)
    f.append(rect(xt_x + xt_w, pin_y_in - 10, 16, 20, fill="#27ae60", stroke="#1e8449", sw=1.2, rx=2))
    f.append(rect(xt_x + xt_w, pin_y_out - 10, 16, 20, fill="#27ae60", stroke="#1e8449", sw=1.2, rx=2))

    # ── Навантажувальні конденсатори C1 та C2
    c1_x, c1_y = 600, pin_y_in
    c2_x, c2_y = 600, pin_y_out

    # Доріжки до конденсаторів
    f.append(line(xt_x - 16, pin_y_in, c1_x, pin_y_in, color="#e74c3c", sw=2.5))
    f.append(line(xt_x - 16, pin_y_out, c2_x, pin_y_out, color="#e67e22", sw=2.5))

    # Конденсатор C1
    f.append(rect(c1_x, c1_y - 12, 34, 24, fill="#bdc3c7", stroke="#7f8c8d", sw=1.5, rx=2))
    f.append(text(c1_x + 17, c1_y - 18, "C1 (CL1)", size=12, color=INK, bold=True))
    f.append(text(c1_x + 17, c1_y + 5, "12 пФ", size=10, color="#2c3e50"))

    # Конденсатор C2
    f.append(rect(c2_x, c2_y - 12, 34, 24, fill="#bdc3c7", stroke="#7f8c8d", sw=1.5, rx=2))
    f.append(text(c2_x + 17, c2_y + 30, "C2 (CL2)", size=12, color=INK, bold=True))
    f.append(text(c2_x + 17, c2_y + 5, "12 пФ", size=10, color="#2c3e50"))

    # Спільне заземлення конденсаторів (Зірка заземлення C1/C2)
    star_gnd_x = 665
    f.append(line(c1_x + 34, c1_y, star_gnd_x, c1_y, color="#27ae60", sw=3))
    f.append(line(c2_x + 34, c2_y, star_gnd_x, c2_y, color="#27ae60", sw=3))
    f.append(line(star_gnd_x, c1_y, star_gnd_x, c2_y, color="#27ae60", sw=4))

    # Точка сходження та зворотний шлях до VSS_OSC
    f.append(circle(star_gnd_x, (c1_y + c2_y) / 2, 7, fill="#27ae60", stroke="#1e8449", sw=1.5))
    f.append(circle(star_gnd_x, (c1_y + c2_y) / 2, 2.5, fill="#ffffff", stroke="none"))
    f.append(text(star_gnd_x + 12, (c1_y + c2_y) / 2 + 4, "Локальна земля", size=11, color=FIELD, anchor="start", bold=True))

    # Прямий поворотний провідник до піна VSS_OSC мікроконтролера
    f.append('<path d="M %d %d L %d %d L %d %d L %d %d" stroke="#27ae60" stroke-width="3.5" fill="none"/>' % (
        star_gnd_x, (c1_y + c2_y) / 2 + 10,
        star_gnd_x, 320,
        mcu_x + mcu_w + 18, 320,
        mcu_x + mcu_w, 320
    ))
    f.append(text(460, 340, "Прямий зворотний шлях струму на VSS_OSC (без цифрових шумів)", size=11, color=FIELD, bold=True))

    # З'єднання кришки кварцу з землею
    f.append(line(xt_x + xt_w + 16, pin_y_in, xt_x + xt_w + 30, pin_y_in, color="#27ae60", sw=2))
    f.append(line(xt_x + xt_w + 16, pin_y_out, xt_x + xt_w + 30, pin_y_out, color="#27ae60", sw=2))
    f.append(line(xt_x + xt_w + 30, pin_y_in, xt_x + xt_w + 30, pin_y_out, color="#27ae60", sw=2))
    f.append(circle(xt_x + xt_w + 30, (pin_y_in + pin_y_out) / 2, 5, fill="#27ae60", stroke="#1e8449", sw=1.5))

    return "\n".join(f)


# ── 2. Чистий аналоговий домен VREF та ADC ──────────────────────────────────
def fig_analog_domain():
    W, H = 840, 500
    f = []

    f.append(text(W / 2, 28, "Чистий аналоговий домен: єдина площина землі, VREF та фільтрація VDDA", size=16, bold=True))

    # Суцільна плата з Layer 2 Solid Ground Plane
    f.append(rect(30, 50, 780, 430, fill="#f4f8fa", stroke="#bdc3c7", sw=1.5, rx=8))
    f.append(text(50, 75, "Шар L2: Суцільна площина заземлення GND (без щілин та розрізів)", size=12, color="#2980b9", anchor="start", bold=True))

    # Просторовий поділ: Цифрова зона (зліва) та Аналогова зона (справа)
    f.append(rect(45, 95, 280, 370, fill="#eef2f7", stroke="#34495e", sw=1.5, rx=6))
    f.append(text(185, 120, "ЦИФРОВИЙ ДОМЕН (Шумний)", size=13, bold=True, color="#2c3e50"))
    f.append(text(185, 138, "MCU Core, DC-DC, SPI/I2C, PWM", size=11, color=MUTED))

    f.append(rect(500, 95, 310, 370, fill="#f0faf4", stroke="#27ae60", sw=1.5, rx=6))
    f.append(text(655, 120, "АНАЛОГОВИЙ ДОМЕН (Тихий)", size=13, bold=True, color=FIELD))
    f.append(text(655, 138, "VREF+, VDDA, Датчики, RC-фільтри", size=11, color="#2ecc71"))

    # Посередині: Змішана ІС (АЦП / MCU Mixed-Signal Boundary)
    adc_x, adc_y, adc_w, adc_h = 345, 140, 135, 310
    f.append(rect(adc_x, adc_y, adc_w, adc_h, fill="#2c3e50", stroke="#1a252f", sw=2, rx=4))
    f.append(text(adc_x + adc_w / 2, adc_y + 30, "АЦП / MCU", size=14, bold=True, color="#ffffff"))
    f.append(text(adc_x + adc_w / 2, adc_y + 48, "Mixed-Signal IC", size=11, color="#bdc3c7"))

    # Цифрові піни зліва АЦП (примикають зліва)
    f.append(rect(adc_x - 16, adc_y + 70, 16, 16, fill="#e74c3c", stroke="#c0392b", sw=1, rx=2))
    f.append(text(adc_x + 18, adc_y + 82, "DVDD", size=10, color="#ffffff"))
    f.append(rect(adc_x - 16, adc_y + 110, 16, 16, fill="#3498db", stroke="#2980b9", sw=1, rx=2))
    f.append(text(adc_x + 18, adc_y + 122, "DGND", size=10, color="#ffffff"))
    f.append(rect(adc_x - 16, adc_y + 160, 16, 16, fill="#f39c12", stroke="#d68910", sw=1, rx=2))
    f.append(text(adc_x + 24, adc_y + 172, "SPI_BUS", size=10, color="#ffffff"))

    # Аналогові піни справа АЦП (примикають справа)
    f.append(rect(adc_x + adc_w, adc_y + 70, 16, 16, fill="#e74c3c", stroke="#c0392b", sw=1, rx=2))
    f.append(text(adc_x + adc_w - 16, adc_y + 82, "VDDA", size=10, color="#ffffff", anchor="end"))
    f.append(rect(adc_x + adc_w, adc_y + 110, 16, 16, fill="#27ae60", stroke="#1e8449", sw=1, rx=2))
    f.append(text(adc_x + adc_w - 16, adc_y + 122, "AGND", size=10, color="#ffffff", anchor="end"))
    f.append(rect(adc_x + adc_w, adc_y + 160, 16, 16, fill="#9b59b6", stroke="#8e44ad", sw=1, rx=2))
    f.append(text(adc_x + adc_w - 16, adc_y + 172, "VREF+", size=10, color="#ffffff", anchor="end"))
    f.append(rect(adc_x + adc_w, adc_y + 210, 16, 16, fill="#1abc9c", stroke="#16a085", sw=1, rx=2))
    f.append(text(adc_x + adc_w - 16, adc_y + 222, "AIN+", size=10, color="#ffffff", anchor="end"))
    f.append(rect(adc_x + adc_w, adc_y + 240, 16, 16, fill="#1abc9c", stroke="#16a085", sw=1, rx=2))
    f.append(text(adc_x + adc_w - 16, adc_y + 252, "AIN-", size=10, color="#ffffff", anchor="end"))

    # ── Фільтрація VDDA (Ferrite Bead + Pi-фільтр)
    # Джерело цифрового живлення 3.3V
    f.append(text(75, 230, "Шина 3.3V", size=12, color=POS, bold=True))
    f.append(line(115, 226, 195, 226, color=POS, sw=3))

    # Ferrite Bead
    fb_x, fb_y, fb_w, fb_h = 195, 216, 50, 20
    f.append(rect(fb_x, fb_y, fb_w, fb_h, fill="#34495e", stroke="#1a252f", sw=1.5, rx=3))
    f.append(text(fb_x + fb_w / 2, fb_y - 6, "Ferrite Bead", size=11, bold=True, color="#2c3e50"))
    f.append(text(fb_x + fb_w / 2, fb_y + 14, "600Ω@100MHz", size=9, color="#ecf0f1"))

    # Лінія після фериту переходить в аналогову зону в обхід ADC
    f.append(line(fb_x + fb_w, 226, 310, 226, color=POS, sw=3))
    f.append(line(310, 226, 310, 80, color=POS, sw=2.5))
    f.append(line(310, 80, 520, 80, color=POS, sw=2.5))
    f.append(line(520, 80, 520, adc_y + 78, color=POS, sw=2.5))
    f.append(line(520, adc_y + 78, adc_x + adc_w + 16, adc_y + 78, color=POS, sw=2.5))

    # Конденсатори розв'язки VDDA: 10uF + 100nF
    f.append(rect(540, 216, 24, 20, fill="#bdc3c7", stroke="#7f8c8d", sw=1.2, rx=2))
    f.append(text(552, 208, "10 мкФ", size=9, color=INK))
    f.append(line(552, adc_y + 78, 552, 216, color=POS, sw=2))
    f.append(line(552, 236, 552, 260, color="#27ae60", sw=2))
    f.append(circle(552, 260, 4, fill="#27ae60", stroke="#1e8449"))

    f.append(rect(580, 216, 24, 20, fill="#bdc3c7", stroke="#7f8c8d", sw=1.2, rx=2))
    f.append(text(592, 208, "100 нФ", size=9, color=INK))
    f.append(line(592, adc_y + 78, 592, 216, color=POS, sw=2))
    f.append(line(592, 236, 592, 260, color="#27ae60", sw=2))
    f.append(circle(592, 260, 4, fill="#27ae60", stroke="#1e8449"))

    # ── Джерело опорної напруги VREF (Прецизійний чіп)
    vref_x, vref_y, vref_w, vref_h = 670, 200, 125, 90
    f.append(rect(vref_x, vref_y, vref_w, vref_h, fill="#ffffff", stroke="#9b59b6", sw=2, rx=4))
    f.append(text(vref_x + vref_w / 2, vref_y + 28, "ІОН VREF", size=13, bold=True, color="#8e44ad"))
    f.append(text(vref_x + vref_w / 2, vref_y + 48, "REF5030 / ADR4525", size=10, color=MUTED))
    f.append(text(vref_x + vref_w / 2, vref_y + 68, "Низький шум + Ізотермія", size=9, color="#8e44ad"))

    # Лінія VREF до піна
    f.append(line(vref_x, vref_y + 45, adc_x + adc_w + 16, adc_y + 168, color="#9b59b6", sw=2.5))
    f.append(circle(vref_x - 25, adc_y + 168, 4, fill="#9b59b6", stroke="none"))
    # Кераміка 10 мкФ на VREF
    f.append(rect(vref_x - 45, adc_y + 158, 22, 20, fill="#bdc3c7", stroke="#7f8c8d", sw=1.2, rx=2))
    f.append(text(vref_x - 34, adc_y + 150, "10 мкФ", size=9, color=INK))

    # ── Вхідний антиаліасинговий RC-фільтр
    f.append(text(730, 320, "Диференційний датчик", size=12, color=INK, bold=True))
    f.append(line(730, 358, 670, 358, color="#1abc9c", sw=2.5))
    f.append(line(730, 388, 670, 388, color="#1abc9c", sw=2.5))

    # Резистори Rext
    f.append(rect(640, 350, 28, 16, fill="#34495e", stroke="#1a252f", sw=1.2, rx=2))
    f.append(text(654, 344, "Rext 47Ω", size=9, color=INK))
    f.append(rect(640, 380, 28, 16, fill="#34495e", stroke="#1a252f", sw=1.2, rx=2))
    f.append(text(654, 404, "Rext 47Ω", size=9, color=INK))

    f.append(line(640, 358, adc_x + adc_w + 16, adc_y + 218, color="#1abc9c", sw=2.5))
    f.append(line(640, 388, adc_x + adc_w + 16, adc_y + 248, color="#1abc9c", sw=2.5))

    # Конденсатор Cext диференційний
    f.append(rect(560, 358, 16, 30, fill="#bdc3c7", stroke="#7f8c8d", sw=1.2, rx=2))
    f.append(text(582, 376, "Cext 1 нФ (C0G)", size=9, color=INK, anchor="start"))

    # Екрануючі земляні доріжки вздовж аналогових сигналів
    f.append(line(adc_x + adc_w + 20, 330, 750, 330, color="#27ae60", sw=1.5, dash="4,3"))
    f.append(line(adc_x + adc_w + 20, 415, 750, 415, color="#27ae60", sw=1.5, dash="4,3"))
    f.append(text(650, 434, "Копланарні захисні земляні траси (Shield Traces)", size=10, color=FIELD))

    # Підсумок внизу
    f.append(rect(45, 455, 750, 30, fill="#ffffff", stroke="#27ae60", sw=1.2, rx=4))
    f.append(text(420, 474, "Правило: Не розділяти полігон L2! Поділ створюється просторовим розміщенням компонентів.", size=11, color=FIELD, bold=True))

    return "\n".join(f)


def main():
    figs = {
        "crystal-guard-topology.svg": (840, 480, fig_crystal_guard),
        "quiet-analog-vref-domain.svg": (840, 500, fig_analog_domain),
    }
    for name, (w, h, fn) in figs.items():
        content = fn()
        svg_code = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n{content}\n</svg>'
        path = os.path.join(IMG, name)
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(svg_code)
        print(f"Generated: {path}")


if __name__ == "__main__":
    main()
