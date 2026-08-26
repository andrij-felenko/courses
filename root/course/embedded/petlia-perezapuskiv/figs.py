# -*- coding: utf-8 -*-
"""Фігури до теми «Петля перезапусків: мотор, просадка, скидання».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED, GRN, BLU = POS, FIELD, NEG

def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


# ── 1. Механізм петлі перезапусків (Brownout Reboot Loop) ──────────────────────
def fig_brownout_loop():
    W, H = 840, 480
    f = []

    # Верхня половина: циклічний автомат петлі (6 блоків)
    b1_x, b1_y = 130, 80    # 1. Холодний старт
    b2_x, b2_y = 420, 80    # 2. Ініціалізація
    b3_x, b3_y = 710, 80    # 3. Пуск мотора (100%)
    b4_x, b4_y = 710, 220   # 4. Кидок струму I_inrush
    b5_x, b5_y = 420, 220   # 5. Просадка V_DD < V_BOR
    b6_x, b6_y = 130, 220   # 6. Скидання BOR -> вимкнення

    f.append(fitbox(b1_x - 100, b1_y - 30, 200, 60, "1. Старт ядра\n(скидання знято)", size=12, bold=True, fill="#eaf0fd", stroke=BLU))
    f.append(fitbox(b2_x - 100, b2_y - 30, 200, 60, "2. Ініціалізація\nналаштування GPIO, периферії", size=12, fill="#f4f6f8", stroke=LINE))
    f.append(fitbox(b3_x - 100, b3_y - 30, 200, 60, "3. Команда «Пуск»\nвідкриття силового ключа", size=12, bold=True, fill="#fdecea", stroke=RED))
    
    f.append(fitbox(b4_x - 100, b4_y - 30, 200, 60, "4. Кидок струму I_inrush\nнерухомий якір / розряджений C", size=12, fill="#fdecea", stroke=RED))
    f.append(fitbox(b5_x - 100, b5_y - 30, 200, 60, "5. Спад напруги на R_дрел\nV_DD падає нижче V_BOR", size=12, bold=True, fill="#fdecea", stroke=RED))
    f.append(fitbox(b6_x - 100, b6_y - 30, 200, 60, "6. Апаратне скидання\nключ гасне, напруга підстрибує", size=12, fill="#eaf0fd", stroke=BLU))

    # Стрілки циклу
    f.append(arrow(b1_x + 102, b1_y, b2_x - 102, b2_y, color=LINE, sw=2))
    f.append(arrow(b2_x + 102, b2_y, b3_x - 102, b3_y, color=LINE, sw=2))
    f.append(arrow(b3_x, b3_y + 32, b4_x, b4_y - 32, color=RED, sw=2))
    f.append(arrow(b4_x - 102, b4_y, b5_x + 102, b5_y, color=RED, sw=2))
    f.append(arrow(b5_x - 102, b5_y, b6_x + 102, b6_y, color=RED, sw=2))
    f.append(arrow(b6_x, b6_y - 32, b1_x, b1_y + 32, color=BLU, sw=2.5))
    f.append(text(75, 150, "петля\nперезапуску", size=11, color=POS, bold=True))

    # Нижня половина: осцилограми V_DD, I_load, /RESET у часі
    x0, y0 = 100, 440
    w_plot = 690
    f.append(line(x0, y0, x0 + w_plot, y0, color=MUTED, sw=1)) # вісь часу
    f.append(text(x0 + w_plot - 30, y0 + 20, "час (t) →", size=11, color=MUTED))

    # 3 цикли перезапуску
    dt = 220
    for cycle in range(3):
        cx = x0 + cycle * dt
        # Напруга V_DD (синя лінія)
        v_pts = [
            (cx, y0 - 120),
            (cx + 90, y0 - 120),
            (cx + 95, y0 - 35),
            (cx + 120, y0 - 35),
            (cx + 130, y0 - 120),
            (cx + dt, y0 - 120)
        ]
        f.append(polyline(v_pts, color=BLU, sw=2.2))

        # Струм мотора I_load (червона лінія)
        i_pts = [
            (cx, y0 - 10),
            (cx + 90, y0 - 10),
            (cx + 93, y0 - 75),
            (cx + 115, y0 - 75),
            (cx + 118, y0 - 10),
            (cx + dt, y0 - 10)
        ]
        f.append(polyline(i_pts, color=RED, sw=2.0))

        # Стан RESET (пунктирний імпульс)
        f.append(line(cx + 98, y0 - 145, cx + 98, y0 - 130, color=POS, sw=1.5))
        f.append(line(cx + 98, y0 - 130, cx + 125, y0 - 130, color=POS, sw=1.5))
        f.append(line(cx + 125, y0 - 130, cx + 125, y0 - 145, color=POS, sw=1.5))
        f.append(text(cx + 112, y0 - 152, "BOR", size=10, color=POS, bold=True))

        # Вертикальні мітки етапів
        f.append(line(cx + 90, y0 - 130, cx + 90, y0, color="#dddddd", sw=1, dash="3 3"))
        f.append(line(cx + 120, y0 - 130, cx + 120, y0, color="#dddddd", sw=1, dash="3 3"))

    # Позначення порогів
    f.append(line(x0 - 20, y0 - 55, x0 + w_plot, y0 - 55, color=POS, sw=1.2, dash="4 4"))
    f.append(text(x0 - 50, y0 - 52, "V_BOR (2.4V)", size=10, color=POS, bold=True))
    f.append(text(x0 - 50, y0 - 120, "V_NOM (3.3V)", size=10, color=BLU))

    # Легенда
    f.append(rect(620, 290, 190, 65, fill="#ffffff", stroke=MUTED, sw=1))
    f.append(line(630, 305, 655, 305, color=BLU, sw=2.2))
    f.append(text(715, 308, "Напруга живлення V_DD", size=10, color=INK))
    f.append(line(630, 325, 655, 325, color=RED, sw=2.0))
    f.append(text(705, 328, "Пусковий струм навантаження", size=10, color=INK))
    f.append(line(630, 345, 655, 345, color=POS, sw=1.5))
    f.append(text(710, 348, "Сигнал скидання /RESET", size=10, color=INK))

    render(os.path.join(IMG, "brownout-reboot-loop.svg"), W, H, *f)


# ── 2. Фізика супервізора BOR та гістерезис ──────────────────────────────────
def fig_bor_hysteresis():
    W, H = 820, 420
    f = []

    # Ліва частина: структурна схема детектора BOR всередині MCU
    f.append(rect(40, 40, 330, 340, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(205, 65, "Внутрішній супервізор BOR / POR", size=13, bold=True, color=INK))

    # Дільник напруги
    f.append(line(80, 90, 80, 120, color=BLU, sw=2))
    f.append(circle(80, 90, 3, fill=BLU, stroke=BLU))
    f.append(text(80, 80, "V_DD", size=11, bold=True, color=BLU))
    f.append(rect(68, 120, 24, 40, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(80, 144, "R1", size=10, color=MUTED))
    f.append(line(80, 160, 80, 200, color=LINE, sw=1.5))
    f.append(rect(68, 200, 24, 40, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(80, 224, "R2", size=10, color=MUTED))
    f.append(line(80, 240, 80, 260, color=LINE, sw=1.5))
    f.append(line(70, 260, 90, 260, color=LINE, sw=1.5)) # GND
    f.append(line(74, 264, 86, 264, color=LINE, sw=1.5))
    f.append(line(77, 268, 83, 268, color=LINE, sw=1.5))

    # Джерело опорної напруги Bandgap V_REF
    f.append(rect(60, 290, 95, 45, fill="#eaf0fd", stroke=BLU, sw=1.5))
    f.append(text(107, 312, "Bandgap", size=10, bold=True, color=BLU))
    f.append(text(107, 326, "V_REF (1.2V)", size=10, color=BLU))

    # Компаратор із гістерезисом (трикутник)
    comp_pts = [(180, 140), (180, 240), (250, 190)]
    f.append(polyline(comp_pts + [(180, 140)], color=LINE, sw=2))
    f.append(text(192, 165, "−", size=14, color=INK))
    f.append(text(192, 220, "+", size=14, color=INK))
    f.append(text(215, 194, "Hyst", size=10, color=MUTED))

    # З'єднання компаратора
    f.append(line(80, 180, 180, 180, color=LINE, sw=1.5))
    f.append(line(155, 312, 165, 312, color=LINE, sw=1.5))
    f.append(line(165, 312, 165, 220, color=LINE, sw=1.5))
    f.append(line(165, 220, 180, 220, color=LINE, sw=1.5))

    # Фільтр глічів + таймер скидання
    f.append(line(250, 190, 265, 190, color=LINE, sw=1.5))
    f.append(rect(265, 165, 95, 50, fill="#fdecea", stroke=RED, sw=1.5))
    f.append(text(312, 185, "Фільтр глічів", size=10, bold=True, color=RED))
    f.append(text(312, 201, "+ t_RST затримка", size=10, color=RED))

    f.append(arrow(360, 190, 390, 190, color=POS, sw=2))
    f.append(text(405, 185, "/RESET", size=11, bold=True, color=POS))
    f.append(text(405, 202, "до ядра", size=10, color=MUTED))

    # Права частина: діаграма рівнів напруги, порогів та гістерезису
    x_rt, y_rt = 450, 50
    w_rt, h_rt = 340, 330
    
    # 1. Безпечна зона (2.4V .. 3.6V)
    f.append(rect(x_rt, y_rt, w_rt, 120, fill="#e8f8f0", stroke=FIELD, sw=1.5))
    f.append(text(x_rt + w_rt/2, y_rt + 30, "ЗОНА НАДІЙНОЇ РОБОТИ ЛОГІКИ", size=11, bold=True, color=FIELD))
    f.append(text(x_rt + w_rt/2, y_rt + 50, "Усі тригери, SRAM, Flash та PLL стабільні", size=10, color=INK))
    f.append(text(x_rt + w_rt/2, y_rt + 75, "V_DD > V_BOR_rise (номінал 3.3 В)", size=10, color=FIELD))

    # 2. Зона гістерезису (2.3V .. 2.4V)
    f.append(rect(x_rt, y_rt + 120, w_rt, 50, fill="#fef9e7", stroke="#d4ac0d", sw=1.5))
    f.append(text(x_rt + w_rt/2, y_rt + 140, "СМУГА ГІСТЕРЕЗИСУ (ΔV_hyst ≈ 50–100 мВ)", size=10, bold=True, color="#7d6608"))
    f.append(text(x_rt + w_rt/2, y_rt + 158, "Захист від дзеленчання на пологих фронтах", size=10, color="#7d6608"))

    # 3. Зона небезпеки та скидання (< 2.3V)
    f.append(rect(x_rt, y_rt + 170, w_rt, 150, fill="#fdecea", stroke=RED, sw=1.5))
    f.append(text(x_rt + w_rt/2, y_rt + 200, "АКТИВНЕ АПАРАТНЕ СКИДАННЯ (RESET)", size=11, bold=True, color=RED))
    f.append(text(x_rt + w_rt/2, y_rt + 225, "V_DD < V_BOR_fall (ядро утримується в ресеті)", size=10, color=RED))
    f.append(text(x_rt + w_rt/2, y_rt + 258, "НЕБЕЗПЕЧНА МЕТАСТАБІЛЬНІСТЬ БЕЗ BOR:", size=10, bold=True, color="#7a1d12"))
    f.append(text(x_rt + w_rt/2, y_rt + 278, "• Затримка поширення t_pd > тактового періоду T_clk", size=10, color=INK))
    f.append(text(x_rt + w_rt/2, y_rt + 296, "• Пошкодження даних Flash/SRAM, виконання «сміття»", size=10, color=INK))

    render(os.path.join(IMG, "bor-hysteresis-timing.svg"), W, H, *f)


# ── 3. Апаратна ізоляція шин (Діод Шотткі + Hold-up конденсатор) ─────────────
def fig_isolated_rails():
    W, H = 840, 420
    f = []

    # Джерело живлення (Батарея / Power In)
    f.append(rect(40, 150, 110, 110, fill="#eaf0fd", stroke=BLU, sw=2))
    f.append(text(95, 185, "Джерело", size=12, bold=True, color=BLU))
    f.append(text(95, 205, "V_BATT (5..12V)", size=10, color=INK))
    f.append(text(95, 225, "R_src + R_дріт", size=10, color=MUTED))

    # Головна силова точка розгалуження
    split_x = 210
    f.append(line(150, 180, split_x, 180, color=RED, sw=3))
    f.append(circle(split_x, 180, 4, fill=RED, stroke=RED))

    # Верхня силова гілка (Мотор, Сервопривід)
    f.append(line(split_x, 180, split_x, 80, color=RED, sw=3))
    f.append(line(split_x, 80, 360, 80, color=RED, sw=3))
    f.append(rect(360, 45, 190, 80, fill="#fdecea", stroke=RED, sw=2))
    f.append(text(455, 75, "Силове навантаження", size=12, bold=True, color=RED))
    f.append(text(455, 95, "DC-мотор, драйвер, RF-підсилювач", size=10, color=INK))
    f.append(text(455, 112, "Створює кидок I_inrush = 5..20 А", size=10, color=RED))

    # Силовий ключ (MOSFET soft-start)
    f.append(line(550, 80, 600, 80, color=RED, sw=2))
    f.append(rect(600, 55, 100, 50, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(650, 78, "Load Switch", size=10, bold=True, color=INK))
    f.append(text(650, 93, "Soft-Start", size=10, color=FIELD))

    # Нижня захищена гілка для MCU
    f.append(line(split_x, 180, split_x, 280, color=RED, sw=2.5))
    f.append(line(split_x, 280, 270, 280, color=RED, sw=2.5))

    # Діод Шотткі D_iso (символ діода)
    d_x = 290
    f.append(rect(d_x - 20, 260, 50, 40, fill="#ffffff", stroke=LINE, sw=1.5))
    # Трикутник діода
    d_pts = [(d_x - 10, 268), (d_x - 10, 292), (d_x + 10, 280)]
    f.append(polyline(d_pts + [(d_x - 10, 268)], color=BLU, sw=2))
    f.append(line(d_x + 10, 268, d_x + 10, 292, color=BLU, sw=2)) # катодна риска
    f.append(text(d_x + 5, 250, "Діод Шотткі D_iso", size=10, bold=True, color=BLU))
    f.append(text(d_x + 5, 315, "V_F ≈ 0.25–0.35 В", size=10, color=MUTED))

    # Вузол після діода з Hold-up конденсатором
    c_x = 400
    f.append(line(d_x + 30, 280, c_x, 280, color=FIELD, sw=2.5))
    f.append(circle(c_x, 280, 4, fill=FIELD, stroke=FIELD))
    f.append(text(c_x, 265, "V_HOLD", size=11, bold=True, color=FIELD))

    # Конденсатор C_hold
    f.append(line(c_x, 280, c_x, 320, color=FIELD, sw=2))
    f.append(line(c_x - 20, 320, c_x + 20, 320, color=FIELD, sw=2.5))
    f.append(line(c_x - 20, 328, c_x + 20, 328, color=FIELD, sw=2.5))
    f.append(line(c_x, 328, c_x, 360, color=LINE, sw=1.5))
    f.append(line(c_x - 12, 360, c_x + 12, 360, color=LINE, sw=1.5)) # GND
    f.append(text(c_x + 55, 330, "C_hold", size=11, bold=True, color=FIELD))
    f.append(text(c_x + 55, 345, "100..1000 мкФ", size=10, color=MUTED))

    # LDO регулятор
    ldo_x = 520
    f.append(line(c_x, 280, ldo_x, 280, color=FIELD, sw=2.5))
    f.append(rect(ldo_x, 250, 90, 60, fill="#e8f8f0", stroke=FIELD, sw=1.5))
    f.append(text(ldo_x + 45, 275, "LDO / Buck", size=11, bold=True, color=FIELD))
    f.append(text(ldo_x + 45, 295, "3.3 В вихід", size=10, color=INK))

    # MCU блок
    mcu_x = 670
    f.append(line(ldo_x + 90, 280, mcu_x, 280, color=FIELD, sw=2))
    f.append(rect(mcu_x, 240, 130, 80, fill="#eaf0fd", stroke=BLU, sw=2))
    f.append(text(mcu_x + 65, 270, "Мікроконтролер", size=12, bold=True, color=BLU))
    f.append(text(mcu_x + 65, 290, "MCU (V_DD = 3.3V)", size=10, color=INK))
    f.append(text(mcu_x + 65, 305, "I_mcu ≈ 20–50 мА", size=10, color=MUTED))

    # Пояснювальний банер дії діода при просадці
    f.append(fitbox(200, 370, 520, 36, "Коли силова шина падає до 0 В: діод D_iso закривається, а C_hold живить MCU", size=11, bold=True, fill="#fef9e7", stroke="#d4ac0d", color="#7d6608"))

    render(os.path.join(IMG, "isolated-power-rails.svg"), W, H, *f)


# ── 4. Автомат станів безпечного старту та обробки скидань ────────────────────
def fig_reset_fsm():
    W, H = 840, 440
    f = []

    # 1. Початок виконання Reset_Handler
    f.append(fitbox(40, 180, 140, 60, "Reset Vector\nСтарт Reset_Handler", size=11, bold=True, fill="#eaf0fd", stroke=BLU))

    # 2. Аналіз регістрів скидання RCC_CSR
    f.append(arrow(180, 210, 220, 210, color=LINE, sw=2))
    f.append(fitbox(220, 175, 170, 70, "Читання регістра\nскидання RCC_CSR\n(BORF, PORF, WWDGF)", size=11, bold=True, fill="#ffffff", stroke=LINE))

    # Розгалуження: Холодний старт (POR) чи Brownout (BOR)
    f.append(arrow(390, 195, 450, 110, color=FIELD, sw=2))
    f.append(text(400, 140, "POR / PIN", size=10, bold=True, color=FIELD))

    f.append(arrow(390, 225, 450, 310, color=RED, sw=2))
    f.append(text(405, 280, "BORF = 1", size=10, bold=True, color=RED))

    # Гілка А: Нормальний старт
    f.append(fitbox(450, 70, 180, 70, "Штатний запуск\n• Скидання BOR-лічильника\n• Стандартний профіль тяги", size=11, fill="#e8f8f0", stroke=FIELD))
    f.append(arrow(630, 105, 680, 180, color=FIELD, sw=2))

    # Гілка Б: Обробка Brownout Recovery
    f.append(fitbox(450, 260, 200, 95, "Brownout Recovery Mode\n• Інкремент bor_counter у .noinit\n• Затримка Safe Startup Delay\n• Обмеження потужності (ШІМ ≤ 25%)\n• Активація плавного пуску", size=10.5, fill="#fdecea", stroke=RED))
    f.append(arrow(650, 305, 680, 240, color=RED, sw=2))

    # Фінальний крок: Очищення прапорців та перехід у Main Loop
    f.append(fitbox(680, 175, 130, 70, "Очищення прапорців\nRMVF = 1\nВхід у main()", size=11, bold=True, fill="#eaf0fd", stroke=BLU))

    # Пояснювальний блок знизу
    f.append(fitbox(60, 375, 720, 45, "Критичне правило: прапорці скидання в RCC_CSR зберігаються між перезапусками.\nЯкщо не виконати RMVF, наступний звичайний ресет успадкує застарілий біт BORF!", size=10.5, bold=True, fill="#fef9e7", stroke="#d4ac0d", color="#7d6608"))

    render(os.path.join(IMG, "reset-flags-fsm.svg"), W, H, *f)


if __name__ == "__main__":
    fig_brownout_loop()
    fig_bor_hysteresis()
    fig_isolated_rails()
    fig_reset_fsm()
    print("Усі фігури успішно згенеровано.")
