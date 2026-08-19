# -*- coding: utf-8 -*-
"""Фігури для теми «Clock stretching у I2C» (book/communications/buses/clock-stretching)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Палітра теми
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def svg_path(d_str, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_dash = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d_str}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_dash}/>'

def svg_polygon(pts, fill=FILL, stroke=LINE, sw=1.5):
    pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{pts_str}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def fig_wired_and():
    """wired-and-scl.svg: Електрична схема монтажного «І» на лінії SCL."""
    W, H = 840, 420
    body = []

    # Загальне тло
    body.append(rect(15, 15, 810, 390, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    
    # Живлення VDD і підтягувальний резистор Rp
    body.append(line(420, 35, 420, 60, color=POS, sw=2))
    b_vdd, _, _ = textbox(420, 35, "VDD (+3.3V / +5V)", size=12, bold=True, fill="#fff1f0", stroke=POS)
    body.append(b_vdd)

    # Резистор Rp
    body.append(rect(408, 60, 24, 50, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=3))
    body.append(text(448, 88, "Rp (4.7 kΩ)", size=11, bold=True, color=AMBER_S, anchor="start"))
    body.append(line(420, 110, 420, 150, color=LINE, sw=2))

    # Головна лінія шини SCL
    body.append(line(80, 150, 760, 150, color=LINE, sw=3))
    b_scl, _, _ = textbox(420, 175, "Спільна фізична лінія SCL (Wired-AND)", size=13, bold=True, fill="#f1f5f9", stroke=LINE)
    body.append(b_scl)

    # Вузол з'єднання з Rp
    body.append(circle(420, 150, 4.5, fill=LINE, stroke=LINE))

    # Блок Ведучого (Master / Controller)
    body.append(rect(60, 220, 310, 165, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    body.append(text(215, 242, "Ведучий (Master / Controller)", size=13, bold=True, color=BLUE_S))

    # Внутрішня схема ведучого: ключ Open-Drain + вхідний буфер SCL Sense
    body.append(line(160, 150, 160, 260, color=LINE, sw=1.5))
    body.append(circle(160, 150, 4, fill=LINE, stroke=LINE))
    
    # N-MOSFET ведучого
    body.append(rect(142, 260, 36, 40, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    body.append(text(160, 284, "N-FET", size=10, bold=True, color=LINE))
    body.append(line(160, 300, 160, 335, color=LINE, sw=1.5))
    body.append(line(145, 335, 175, 335, color=LINE, sw=2)) # Земля
    body.append(line(150, 340, 170, 340, color=LINE, sw=1.5))
    body.append(line(155, 345, 165, 345, color=LINE, sw=1.2))
    body.append(text(160, 362, "GND (0V)", size=9, color=MUTED))

    # Керування затвором ведучого
    body.append(line(95, 280, 142, 280, color=BLUE_S, sw=1.5))
    body.append(text(115, 272, "SCL_OUT", size=9, bold=True, color=BLUE_S))

    # Вхідний буфер SCL Sense (для перевірки рівня SCL)
    body.append(line(275, 150, 275, 265, color=LINE, sw=1.5))
    body.append(circle(275, 150, 4, fill=LINE, stroke=LINE))
    # Буфер (трикутник)
    body.append(svg_polygon([(263, 265), (287, 265), (275, 290)], fill="#ffffff", stroke=GREEN_S, sw=1.5))
    body.append(line(275, 290, 275, 320, color=GREEN_S, sw=1.5))
    body.append(text(275, 338, "SCL_IN (Sense)", size=10, bold=True, color=GREEN_S))
    body.append(text(275, 355, "Контроль розтягування", size=9, color=MUTED))

    # Блок Веденого (Slave / Target)
    body.append(rect(470, 220, 310, 165, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    body.append(text(625, 242, "Ведений (Slave / Target)", size=13, bold=True, color=PURPLE_S))

    # Внутрішня схема веденого: ключ утримання SCL
    body.append(line(570, 150, 570, 260, color=LINE, sw=1.5))
    body.append(circle(570, 150, 4, fill=LINE, stroke=LINE))

    body.append(rect(552, 260, 36, 40, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    body.append(text(570, 284, "N-FET", size=10, bold=True, color=LINE))
    body.append(line(570, 300, 570, 335, color=LINE, sw=1.5))
    body.append(line(555, 335, 585, 335, color=LINE, sw=2)) # Земля
    body.append(line(560, 340, 580, 340, color=LINE, sw=1.5))
    body.append(line(565, 345, 575, 345, color=LINE, sw=1.2))
    body.append(text(570, 362, "GND (0V)", size=9, color=MUTED))

    # Сигнал розтягування від веденого
    body.append(line(505, 280, 552, 280, color=PURPLE_S, sw=1.5))
    body.append(text(525, 272, "STRETCH", size=9, bold=True, color=PURPLE_S))

    # Детектор такту у веденого
    body.append(line(685, 150, 685, 265, color=LINE, sw=1.5))
    body.append(circle(685, 150, 4, fill=LINE, stroke=LINE))
    body.append(svg_polygon([(673, 265), (697, 265), (685, 290)], fill="#ffffff", stroke=PURPLE_S, sw=1.5))
    body.append(line(685, 290, 685, 320, color=PURPLE_S, sw=1.5))
    body.append(text(685, 338, "SCL_CLK_IN", size=10, bold=True, color=PURPLE_S))
    body.append(text(685, 355, "Прийом синхротакту", size=9, color=MUTED))

    render(os.path.join(IMG, "wired-and-scl.svg"), W, H, *body)


def fig_stretch_timing():
    """stretch-timing-diagram.svg: Часова діаграма розтягування такту на фазі ACK/NACK."""
    W, H = 860, 400
    body = []

    body.append(rect(15, 15, 830, 370, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    body.append(text(430, 38, "Часова діаграма: розтягування такту (Clock Stretching) після 8-го біта даних", size=14, bold=True, color=LINE))

    # Мітки сигналів
    body.append(text(40, 95, "SCL (Master\nDrive)", size=11, bold=True, color=BLUE_S, anchor="start"))
    body.append(text(40, 175, "SCL (Slave\nStretch)", size=11, bold=True, color=PURPLE_S, anchor="start"))
    body.append(text(40, 255, "SCL (Bus\nActual)", size=11, bold=True, color=LINE, anchor="start"))
    body.append(text(40, 335, "SDA (Data\n& ACK)", size=11, bold=True, color=TEAL_S, anchor="start"))

    # Вертикальні роздільники фаз
    body.append(line(250, 60, 250, 365, color="#e2e8f0", sw=1, dash="4,4"))
    body.append(line(340, 60, 340, 365, color="#e2e8f0", sw=1, dash="4,4"))
    body.append(line(620, 60, 620, 365, color="#e2e8f0", sw=1, dash="4,4"))
    body.append(line(710, 60, 710, 365, color="#e2e8f0", sw=1, dash="4,4"))

    body.append(text(205, 55, "Біт 7 (Data)", size=11, bold=True, color=MUTED))
    body.append(text(295, 55, "Біт 8 (Data)", size=11, bold=True, color=MUTED))
    body.append(text(480, 55, "Фаза ACK / Очікування веденого (Clock Stretch)", size=11, bold=True, color=PURPLE_S))
    body.append(text(665, 55, "Наступний біт", size=11, bold=True, color=MUTED))

    # Сигнал 1: SCL (Master Drive)
    scl_m_d = "M 160 115 H 205 V 80 H 250 V 115 H 295 V 80 H 340 V 115 H 385 V 80 H 620 V 115 H 665 V 80 H 710 V 115 H 750"
    body.append(svg_path(scl_m_d, fill="none", stroke=BLUE_S, sw=2))

    # Сигнал 2: SCL (Slave Stretch)
    scl_s_d = "M 160 160 H 340 V 195 H 560 V 160 H 750"
    body.append(svg_path(scl_s_d, fill="none", stroke=PURPLE_S, sw=2))
    body.append(text(450, 185, "Ведений примусово тримає 0V (Processing / ADC)", size=10, bold=True, color=PURPLE_S))

    # Сигнал 3: Фактичний SCL на шині (Wired-AND)
    scl_act_d = "M 160 275 H 205 V 240 H 250 V 275 H 295 V 240 H 340 V 275 H 560 Q 572 245 585 240 H 620 V 275 H 665 V 240 H 710 V 275 H 750"
    body.append(svg_path(scl_act_d, fill="none", stroke=LINE, sw=2.5))

    # Підсвічування зони розтягування
    body.append(rect(385, 230, 175, 55, fill="#fef2f2", stroke=RED_S, sw=1, rx=4))
    body.append(text(472, 255, "t_STRETCH (Пауза)", size=11, bold=True, color=RED_S))

    # Сигнал 4: SDA
    sda_d = "M 160 320 H 250 V 355 H 340 H 620 V 320 H 750"
    body.append(svg_path(sda_d, fill="none", stroke=TEAL_S, sw=2))
    body.append(text(480, 345, "ACK від веденого (SDA = 0)", size=10, bold=True, color=TEAL_S))

    # Стрілка виявлення фронту майстром
    body.append(arrow(585, 215, 585, 235, color=GREEN_S, sw=1.8))
    body.append(text(585, 205, "SCL досяг VIH: Майстер фіксує ACK", size=10, bold=True, color=GREEN_S))

    render(os.path.join(IMG, "stretch-timing-diagram.svg"), W, H, *body)


def fig_master_fsm():
    """master-state-machine.svg: Автомат станів ведучого при формуванні такту з контролем SCL."""
    W, H = 840, 430
    body = []

    body.append(rect(15, 15, 810, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    body.append(text(420, 38, "Алгоритм ведучого: генерація такту з опитуванням SCL та таймаутом", size=14, bold=True, color=LINE))

    # Блок 1: Спад SCL
    b1, _, _ = textbox(160, 95, "1. Притягнути SCL до 0V\n(SCL_OUT = LOW)\nЗапустити таймер t_LOW", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    body.append(b1)

    # Блок 2: Очікування t_LOW
    b2, _, _ = textbox(160, 190, "2. Відрахувати t_LOW\n(затримка половини періоду)", size=11, bold=True, fill=GRAY_F, stroke=GRAY_S)
    body.append(b2)
    body.append(arrow(160, 130, 160, 160, color=LINE, sw=1.5))

    # Блок 3: Відпускання SCL у High-Z
    b3, _, _ = textbox(160, 285, "3. Відпустити лінію SCL\n(SCL_OUT = HIGH-Z)\nЗапустити таймер таймауту", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    body.append(b3)
    body.append(arrow(160, 225, 160, 255, color=LINE, sw=1.5))

    # Блок 4: Ромб перевірки SCL Sense
    b4, _, _ = textbox(440, 285, "4. Чи піднявся SCL до VIH?\n(Зчитування SCL_IN == 1)", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    body.append(b4)
    body.append(arrow(275, 285, 330, 285, color=LINE, sw=1.5))

    # Блок 5: Гілка ТАК -> t_HIGH
    b5, _, _ = textbox(700, 285, "5. SCL високий!\nЗапустити таймер t_HIGH\n(Семплування біта SDA)", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    body.append(b5)
    body.append(arrow(550, 285, 595, 285, color=GREEN_S, sw=2))
    body.append(text(572, 275, "ТАК", size=10, bold=True, color=GREEN_S))

    # Блок 6: Завершення такту
    b6, _, _ = textbox(700, 95, "6. Відрахувати t_HIGH\nПерейти до наступного біта", size=11, bold=True, fill=GRAY_F, stroke=GRAY_S)
    body.append(b6)
    body.append(arrow(700, 245, 700, 135, color=LINE, sw=1.5))
    body.append(arrow(600, 95, 275, 95, color=LINE, sw=1.5))

    # Гілка НІ від Блоку 4 -> Перевірка таймауту
    b_tout, _, _ = textbox(440, 375, "Чи не перевищено таймаут?\n(t_WAIT > t_TIMEOUT_MAX, напр. 35 мс)", size=10, bold=True, fill=RED_F, stroke=RED_S)
    body.append(b_tout)
    body.append(arrow(440, 320, 440, 350, color=RED_S, sw=1.5))
    body.append(text(460, 335, "НІ (0V)", size=10, bold=True, color=RED_S))

    # Цикл очікування (Stretching)
    cycle_d = "M 330 375 H 260 V 310 H 330"
    body.append(svg_path(cycle_d, fill="none", stroke=AMBER_S, sw=1.5, dash="3,3"))
    b_st_lbl, _, _ = textbox(260, 345, "Очікування\n(Stretching)", size=9, fill="#ffffff", stroke=AMBER_S)
    body.append(b_st_lbl)

    # Таймаут аварійний вихід
    b_err, _, _ = textbox(700, 375, "Аварія шини (Bus Lockup)!\nВиклик процедури 9 тактів\nСкидання інтерфейсу I2C", size=10, bold=True, fill=RED_F, stroke=RED_S)
    body.append(b_err)
    body.append(arrow(550, 375, 600, 375, color=RED_S, sw=2))
    body.append(text(575, 365, "ТАК (Fail)", size=10, bold=True, color=RED_S))

    render(os.path.join(IMG, "master-state-machine.svg"), W, H, *body)


def fig_bcm2835_bug():
    """bcm2835-glitch-mechanism.svg: Апаратний баг контролера Broadcom BCM2835 (Raspberry Pi)."""
    W, H = 840, 390
    body = []

    body.append(rect(15, 15, 810, 360, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    body.append(text(420, 38, "Апаратний баг SoC Broadcom BCM2835: порушення зсуву фази при розтягуванні", size=14, bold=True, color=LINE))

    # Ліва колонка: Нормальний контролер
    body.append(rect(35, 65, 370, 290, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=6))
    body.append(text(220, 88, "Коректний I2C контролер", size=12, bold=True, color=GREEN_S))

    # Графік коректного
    body.append(text(50, 125, "SCL:", size=10, bold=True, color=LINE, anchor="start"))
    scl_ok_d = "M 90 135 H 130 V 115 H 170 V 135 H 260 V 115 H 320 V 135 H 370"
    body.append(svg_path(scl_ok_d, fill="none", stroke=GREEN_S, sw=2))
    body.append(text(215, 150, "Розтягнуто веденим", size=9, bold=True, color=GREEN_S))

    body.append(text(50, 185, "SDA:", size=10, bold=True, color=LINE, anchor="start"))
    sda_ok_d = "M 90 180 H 190 V 195 H 370"
    body.append(svg_path(sda_ok_d, fill="none", stroke=BLUE_S, sw=1.8))

    # Семплування
    body.append(arrow(290, 220, 290, 195, color=GREEN_S, sw=1.5))
    body.append(text(290, 235, "Семпл після підйому SCL", size=9, bold=True, color=GREEN_S))
    body.append(text(220, 280, "Внутрішній лічильник чекає\nреального наростаючого фронту SCL.\nДані зчитуються коректно.", size=10, color=LINE))

    # Права колонка: Broadcom BCM2835 BSC
    body.append(rect(435, 65, 370, 290, fill=RED_F, stroke=RED_S, sw=1.5, rx=6))
    body.append(text(620, 88, "SoC Broadcom BCM2835 (Raspberry Pi)", size=12, bold=True, color=RED_S))

    # Графік багованого
    body.append(text(450, 125, "SCL:", size=10, bold=True, color=LINE, anchor="start"))
    scl_bug_d = "M 490 135 H 530 V 115 H 570 V 135 H 670 V 115 H 720 V 135 H 770"
    body.append(svg_path(scl_bug_d, fill="none", stroke=RED_S, sw=2))

    body.append(text(450, 185, "SDA:", size=10, bold=True, color=LINE, anchor="start"))
    sda_bug_d = "M 490 180 H 590 V 195 H 770"
    body.append(svg_path(sda_bug_d, fill="none", stroke=BLUE_S, sw=1.8))

    # Фальшиве семплування
    body.append(arrow(610, 220, 610, 195, color=RED_S, sw=1.5))
    body.append(text(610, 235, "ПОМИЛКОВИЙ семпл під час 0V!", size=9, bold=True, color=RED_S))
    body.append(text(620, 280, "Апаратний автомат пропускає такт,\nзсуває внутрішній стан без очікування SCL,\nщо призводить до втрати бітів і спотворень.", size=10, color=LINE))

    render(os.path.join(IMG, "bcm2835-glitch-mechanism.svg"), W, H, *body)


def fig_bus_recovery():
    """bus-recovery-9clocks.svg: Процедура аварійного відновлення шини (9 тактів SCL)."""
    W, H = 840, 390
    body = []

    body.append(rect(15, 15, 810, 360, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    body.append(text(420, 38, "Процедура розблокування шини (Bus Clear): генерація 9 імпульсів SCL", size=14, bold=True, color=LINE))

    # Мітки сигналів
    body.append(text(40, 100, "SCL (Master\nRecovery)", size=11, bold=True, color=BLUE_S, anchor="start"))
    body.append(text(40, 190, "SDA (Stuck\nSlave)", size=11, bold=True, color=RED_S, anchor="start"))
    body.append(text(40, 280, "Стан шини", size=11, bold=True, color=MUTED, anchor="start"))

    # 9 тактів SCL
    x0 = 160
    dx = 42
    scl_pts = [f"M {x0} 115"]
    for i in range(9):
        cx = x0 + i * dx
        scl_pts.append(f"H {cx + 15} V 85 H {cx + 30} V 115")
        body.append(text(cx + 22, 75, str(i + 1), size=10, bold=True, color=BLUE_S))
    scl_pts.append(f"H {x0 + 9 * dx + 20}")
    # Потім STOP condition: SCL High, SDA Low->High
    stop_x = x0 + 9 * dx + 30
    scl_pts.append(f"V 85 H {stop_x + 80}")
    body.append(svg_path(" ".join(scl_pts), fill="none", stroke=BLUE_S, sw=2))

    # SDA (завислий ведений тримає 0V, але після 5-го такту виштовхує свій байт і відпускає на 1)
    sda_pts = [f"M {x0} 205 H {x0 + 5 * dx + 20} V 175 H {stop_x + 40} V 205 H {stop_x + 60} V 175 H {stop_x + 80}"]
    body.append(svg_path(" ".join(sda_pts), fill="none", stroke=RED_S, sw=2))

    body.append(text(x0 + int(2.5 * dx), 220, "Ведений тримав SDA=0", size=9, bold=True, color=RED_S))
    body.append(text(x0 + 7 * dx, 165, "Ведений завершив байт і відпустив SDA (High-Z)", size=9, bold=True, color=GREEN_S))

    # STOP condition маркер
    body.append(rect(stop_x + 20, 65, 75, 160, fill="#f0fdf4", stroke=GREEN_S, sw=1, rx=4))
    body.append(text(stop_x + 57, 240, "STOP", size=11, bold=True, color=GREEN_S))
    body.append(text(stop_x + 57, 255, "SDA: 0→1 при SCL=1", size=9, color=MUTED))

    # Пояснювальний текст унизу
    b_desc, _, _ = textbox(420, 325, "1. Переведення пінів у режим GPIO (Bit-Banging)  →  2. Генерація до 9 тактів SCL (виштовхування бітів веденого)\n3. Моніторинг SDA: якщо SDA став '1', ведений відпустив шину  →  4. Формування сигналу STOP для скидання стану", size=10, fill=GRAY_F, stroke=GRAY_S)
    body.append(b_desc)

    render(os.path.join(IMG, "bus-recovery-9clocks.svg"), W, H, *body)


if __name__ == "__main__":
    print("Генерація фігур для clock-stretching...")
    fig_wired_and()
    fig_stretch_timing()
    fig_master_fsm()
    fig_bcm2835_bug()
    fig_bus_recovery()
    print("Готово!")
