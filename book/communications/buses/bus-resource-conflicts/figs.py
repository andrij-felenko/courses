# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN_COL = "#d9534f"
OK_COL   = "#27ae60"
BUS_COL  = "#2457d6"
WARN_BG  = "#fdecea"
OK_BG    = "#eef6ef"
ACCENT   = "#d97706"


def polyline(pts, color=LINE, sw=1.5, fill="none"):
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{points}" fill="{fill}" stroke="{color}" stroke-width="{sw:.1f}"/>'


def fig_conflict_taxonomy():
    W, H = 840, 370
    p = []
    
    cols = [
        ("Електричний рівень", [
            "Зіткнення виходів (Push-Pull)",
            "Коротке замикання VCC ↔ GND",
            "Наскрізні струми через ключі",
            "Паразитне заживлення через ESD",
            "Плаваючий рівень ліній CS/SS"
        ], WARN_COL, WARN_BG, 30),
        ("Протокольний рівень", [
            "Збіг адрес на шині I2C (7/10-bit)",
            "Колізія ведучих (Multi-Master)",
            "Зависання шини SDA (Bus Lockup)",
            "Розсинхронізація автоматів",
            "Хибний ACK від пасивних ліній"
        ], ACCENT, "#fef8ee", 295),
        ("Системний (RTOS) рівень", [
            "Одночасний доступ кількох задач",
            "Дедлок у контексті переривання",
            "Інверсія пріоритетів на м'ютексі",
            "Конфлікт каналів і черг DMA",
            "Порушення атомарності транзакції"
        ], BUS_COL, "#eef3fc", 560)
    ]
    
    cw = 250
    ch = 270
    cy = 55
    
    for title, items, border_col, fill_col, cx in cols:
        p.append(rect(cx, cy, cw, ch, fill=fill_col, stroke=border_col, sw=1.8, rx=8))
        p.append(textbox(cx + cw / 2, cy + 26, title, size=12, color=border_col, bold=True, fill=BG, stroke=border_col, pad=6)[0])
        
        iy = cy + 64
        for item in items:
            p.append(circle(cx + 18, iy - 4, 3, fill=border_col, stroke=border_col))
            p.append(text(cx + 28, iy, item, size=9.5, color=INK, anchor="start"))
            iy += 39
            
    p.append(text(W / 2, H - 14, "Спільне середовище вимагає захисту на всіх трьох рівнях: схемотехнічному, протокольному та програмному", size=10.5, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "conflict-taxonomy.svg"), W, H, *p, title="Три рівні конфліктів ресурсів у цифрових шинах")


def fig_i2c_address_mux():
    W, H = 840, 370
    p = []
    
    # MCU Host
    p.append(rect(30, 85, 120, 160, fill=OK_BG, stroke=OK_COL, sw=1.8))
    p.append(text(90, 120, "Мікроконтролер", size=11, color=OK_COL, bold=True))
    p.append(text(90, 138, "(I2C Host)", size=9.5, color=MUTED, italic=True))
    p.append(text(90, 180, "SDA / SCL", size=10, color=INK, bold=True))
    p.append(text(90, 200, "Головна шина", size=9.5, color=MUTED))
    
    # TCA9548A Switch
    p.append(rect(240, 70, 170, 195, fill="#f4f6f8", stroke=BUS_COL, sw=2))
    p.append(text(325, 96, "TCA9548A", size=13, color=BUS_COL, bold=True))
    p.append(text(325, 114, "Адреса: 0x70", size=10, color=MUTED, italic=True))
    p.append(text(325, 136, "8-канальний ключ", size=10, color=INK))
    
    # Internal switch gates
    p.append(line(300, 165, 340, 165, color=BUS_COL, sw=1.5))
    p.append(line(340, 165, 360, 150, color=OK_COL, sw=2)) # Gate 0 closed
    p.append(text(370, 146, "CH0 (ON)", size=9.5, color=OK_COL, anchor="start", bold=True))
    
    p.append(line(300, 205, 340, 205, color=BUS_COL, sw=1.5))
    p.append(line(340, 205, 360, 225, color=WARN_COL, sw=1.5, dash="3 3")) # Gate 1 open
    p.append(text(370, 227, "CH1 (OFF)", size=9.5, color=WARN_COL, anchor="start", bold=True))
    
    # Bus connecting MCU to Switch
    p.append(line(150, 165, 240, 165, color=BUS_COL, sw=2))
    p.append(arrow(150, 165, 235, 165, color=BUS_COL, sw=2))
    p.append(text(195, 155, "SDA / SCL", size=9.5, color=BUS_COL, bold=True))
    
    # Channel 0: Sensor 1 (Address 0x68)
    p.append(line(410, 150, 510, 150, color=OK_COL, sw=2))
    p.append(arrow(410, 150, 505, 150, color=OK_COL, sw=2))
    p.append(text(460, 140, "Гілка 0", size=9.5, color=OK_COL, bold=True))
    
    p.append(rect(510, 105, 140, 85, fill=OK_BG, stroke=OK_COL, sw=1.8))
    p.append(text(580, 130, "Давач 1 (IMU)", size=10.5, color=INK, bold=True))
    p.append(text(580, 150, "Адреса: 0x68", size=10, color=OK_COL, bold=True))
    p.append(text(580, 170, "Активна гілка", size=9.5, color=OK_COL))
    
    # Channel 1: Sensor 2 (Address 0x68)
    p.append(line(410, 225, 510, 225, color=WARN_COL, sw=1.5, dash="4 4"))
    p.append(arrow(410, 225, 505, 225, color=WARN_COL, sw=1.5))
    p.append(text(460, 215, "Гілка 1", size=9.5, color=WARN_COL, bold=True))
    
    p.append(rect(510, 200, 140, 85, fill="#fafafa", stroke=MUTED, sw=1.5))
    p.append(text(580, 225, "Давач 2 (IMU)", size=10.5, color=MUTED, bold=True))
    p.append(text(580, 245, "Адреса: 0x68", size=10, color=MUTED, bold=True))
    p.append(text(580, 265, "Ізольовано ключем", size=9.5, color=WARN_COL))
    
    # Explanation panel right side
    p.append(rect(670, 95, 150, 180, fill="#f8fafc", stroke=MUTED, sw=1.2))
    p.append(text(745, 118, "Принцип роботи", size=10.5, color=INK, bold=True))
    p.append(mtext(745, 142, "1. Запис 0x01 у\nрегістр 0x70:\nвмикає CH0\n\n2. Опитування 0x68\n\n3. Запис 0x02:\nвмикає CH1", size=9.5, color=INK, lh=1.35))
    
    p.append(text(W / 2, H - 14, "Комутатор ізолює однакові адреси та ділить паразитну ємність довгих ліній на незалежні сегменти", size=10.5, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "i2c-address-mux.svg"), W, H, *p, title="Розв'язання конфлікту адрес комутатором I2C (TCA9548A)")


def fig_spi_miso_contention():
    W, H = 840, 360
    p = []
    
    # Host MCU
    p.append(rect(30, 75, 120, 195, fill="#f4f6f8", stroke=INK, sw=1.8))
    p.append(text(90, 105, "MCU (Host)", size=11.5, color=INK, bold=True))
    p.append(text(90, 145, "CS0 (LOW)", size=10, color=OK_COL, bold=True))
    p.append(text(90, 195, "CS1 (Floating)", size=10, color=WARN_COL, bold=True))
    p.append(text(90, 245, "MISO (Вхід)", size=10, color=BUS_COL, bold=True))
    
    # MISO Bus wire
    p.append(line(150, 245, 780, 245, color=BUS_COL, sw=2.5))
    p.append(text(185, 235, "Спільна MISO", size=9.5, color=BUS_COL, bold=True))
    
    # Slave 1 (CS asserted correctly)
    p.append(rect(300, 65, 170, 115, fill=OK_BG, stroke=OK_COL, sw=1.8))
    p.append(text(385, 90, "Ведений 1 (Flash)", size=10.5, color=INK, bold=True))
    p.append(text(385, 110, "CS0 = 0 (Активний)", size=10, color=OK_COL, bold=True))
    p.append(text(385, 132, "Вихідний буфер: УВІМК", size=9.5, color=OK_COL))
    p.append(text(385, 154, "Генерить '1' (+3.3V)", size=10, color=OK_COL, bold=True))
    
    # Slave 2 (CS floating low / both active)
    p.append(rect(580, 65, 170, 115, fill=WARN_BG, stroke=WARN_COL, sw=1.8))
    p.append(text(665, 90, "Ведений 2 (Sensor)", size=10.5, color=INK, bold=True))
    p.append(text(665, 110, "CS1 = ? (Шум / 0V)", size=10, color=WARN_COL, bold=True))
    p.append(text(665, 132, "Вихідний буфер: УВІМК!", size=9.5, color=WARN_COL))
    p.append(text(665, 154, "Генерить '0' (0V)", size=10, color=WARN_COL, bold=True))
    
    # Wires from slaves to MISO
    p.append(line(385, 180, 385, 245, color=OK_COL, sw=2))
    p.append(arrow(385, 180, 385, 240, color=OK_COL, sw=2))
    
    p.append(line(665, 180, 665, 245, color=WARN_COL, sw=2))
    p.append(arrow(665, 180, 665, 240, color=WARN_COL, sw=2))
    
    # Contention zone highlight
    p.append(rect(470, 220, 140, 85, fill=WARN_BG, stroke=WARN_COL, sw=1.5, rx=6))
    p.append(text(540, 242, "⚡ КОЛІЗІЯ СТРУМІВ", size=10, color=WARN_COL, bold=True))
    p.append(text(540, 262, "V_MISO ≈ 1.65 В", size=10, color=WARN_COL, bold=True))
    p.append(text(540, 282, "Наскрізний струм > 50 мА", size=9.5, color=INK))
    
    # Pullup resistor recommendation
    p.append(rect(200, 285, 200, 48, fill="#ffffff", stroke=OK_COL, sw=1.2, rx=4))
    p.append(text(300, 304, "Захист: резистори 10 кОм", size=9.5, color=OK_COL, bold=True))
    p.append(text(300, 320, "підтяжки кожної CS до VCC", size=9.5, color=MUTED))
    
    p.append(text(W / 2, H - 10, "Два двотактні виходи на одній лінії закорочують живлення на землю через внутрішні транзистори", size=10.5, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "spi-miso-contention.svg"), W, H, *p, title="Конфлікт на спільній лінії MISO у шині SPI")


def fig_i2c_multimaster_arbitration():
    W, H = 880, 400
    p = []
    
    # Labels left
    p.append(text(40, 70, "SCL (Master 1)", size=10, color=BUS_COL, bold=True, anchor="start"))
    p.append(text(40, 115, "SCL (Master 2)", size=10, color=BUS_COL, bold=True, anchor="start"))
    p.append(text(40, 160, "SCL (Шина AND)", size=10, color=INK, bold=True, anchor="start"))
    
    p.append(text(40, 220, "SDA (Master 1)", size=10, color=OK_COL, bold=True, anchor="start"))
    p.append(text(40, 265, "SDA (Master 2)", size=10, color=WARN_COL, bold=True, anchor="start"))
    p.append(text(40, 310, "SDA (Шина AND)", size=10, color=INK, bold=True, anchor="start"))
    
    # Time markers (Bit slots)
    slots = [170, 260, 350, 440, 530, 620, 710]
    bit_names = ["START", "Bit 7 (1)", "Bit 6 (1)", "Bit 5 (0)", "Bit 4 (Суперечка)", "Bit 3", "ACK"]
    
    for i, sx in enumerate(slots):
        p.append(line(sx, 45, sx, 335, color="#e2e8f0", sw=1, dash="3 3"))
        if i < len(bit_names):
            p.append(text(sx + 40, 40, bit_names[i], size=9.5, color=MUTED, bold=True))
            
    # Master 1 SDA: 1 -> 1 -> 0 -> 1 (loses at bit 4)
    p.append(polyline([(170, 215), (260, 215), (350, 215), (400, 230), (440, 230), (480, 215), (530, 215)], color=OK_COL, sw=2))
    p.append(text(495, 205, "M1 шле '1'", size=9.5, color=OK_COL, bold=True))
    
    # Master 2 SDA: 1 -> 1 -> 0 -> 0 (wins at bit 4)
    p.append(polyline([(170, 260), (260, 260), (350, 260), (400, 275), (440, 275), (480, 275), (530, 275)], color=WARN_COL, sw=2))
    p.append(text(495, 290, "M2 шле '0'", size=9.5, color=WARN_COL, bold=True))
    
    # Actual SDA on bus (Wired-AND: 0 wins)
    p.append(polyline([(170, 305), (260, 305), (350, 305), (400, 320), (440, 320), (480, 320), (530, 320)], color=INK, sw=2.5))
    
    # Collision box placed on the right side
    p.append(f'<rect x="630" y="200" width="220" height="120" rx="6" fill="#fef2f2" stroke="{WARN_COL}" stroke-width="1.8" stroke-dasharray="4 4"/>')
    p.append(text(740, 222, "ВТРАТА АРБІТРАЖУ", size=10, color=WARN_COL, bold=True))
    p.append(mtext(740, 245, "M1 виставив '1', але\nна шині бачить '0' (від M2).\n→ M1 вимикає передавач\n→ M1 стає слухачем,\nкадр M2 не пошкоджено!", size=9.5, color=INK, lh=1.3))
    
    # Clock sync illustration
    p.append(polyline([(170, 65), (200, 65), (220, 80), (250, 80), (260, 65)], color=BUS_COL, sw=1.8))
    p.append(polyline([(170, 110), (190, 110), (210, 125), (255, 125), (260, 110)], color=BUS_COL, sw=1.8))
    p.append(polyline([(170, 155), (190, 155), (210, 170), (255, 170), (260, 155)], color=INK, sw=2))
    
    p.append(text(W / 2, H - 14, "Завдяки відкритому колектору передача переможця не спотворюється жодним бітом", size=10.5, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "i2c-multimaster-arbitration.svg"), W, H, *p, title="Арбітраж доступу та синхронізація годинника у шині I2C")


def fig_i2c_bus_lockup():
    W, H = 840, 370
    p = []
    
    # Left Box: Problem
    p.append(rect(30, 55, 360, 270, fill=WARN_BG, stroke=WARN_COL, sw=1.8, rx=6))
    p.append(text(210, 80, "Аварія: зависання шини (Bus Lockup)", size=11.5, color=WARN_COL, bold=True))
    
    p.append(mtext(210, 112, "1. Ведучий читав байт із веденого.\n2. Ведений виставив біт '0' (притягнув SDA до GND).\n3. Ведучий скинувся (Watchdog / Brownout / Reset).\n4. Після перезавантаження ведучий бачить SDA=LOW.\n5. Ведучий не може згенерувати START (потрібен SDA=HIGH).\n6. Ведений вічно чекає такту SCL від ведучого.", size=9.5, color=INK, lh=1.38))
    
    p.append(line(40, 275, 380, 275, color=WARN_COL, sw=1, dash="3 3"))
    p.append(text(210, 298, "РЕЗУЛЬТАТ: Шина мертва для всіх пристроїв", size=10, color=WARN_COL, bold=True))
    
    # Right Box: Solution / 9 Clock pulses
    p.append(rect(420, 55, 390, 270, fill=OK_BG, stroke=OK_COL, sw=1.8, rx=6))
    p.append(text(615, 80, "Процедура скидання (9-Clock Recovery)", size=11.5, color=OK_COL, bold=True))
    
    # Steps
    p.append(mtext(615, 108, "1. Перевести піни SCL і SDA в режим GPIO Open-Drain.\n2. Якщо SDA == 0, подати до 9 імпульсів на лінію SCL.\n3. Ведений дочитує внутрішній байт і відпускає SDA.\n4. Щойно SDA == 1, сформувати сигнал STOP.\n5. Повторно ініціалізувати апаратний блок I2C.", size=9.5, color=INK, lh=1.35))
    
    # Pulse diagram inside right box
    py = 230
    p.append(text(440, py, "SCL:", size=10, color=INK, bold=True, anchor="start"))
    p.append(polyline([(475, py), (485, py - 16), (495, py), (505, py - 16), (515, py), (525, py - 16), (535, py), (545, py - 16), (555, py), (590, py)], color=OK_COL, sw=1.8))
    p.append(text(515, py + 16, "9 тактів SCL", size=9.5, color=OK_COL, bold=True))
    
    py2 = 275
    p.append(text(440, py2, "SDA:", size=10, color=INK, bold=True, anchor="start"))
    p.append(polyline([(475, py2), (545, py2), (555, py2 - 16), (590, py2 - 16), (595, py2), (615, py2), (620, py2 - 16)], color=BUS_COL, sw=1.8))
    p.append(text(560, py2 + 16, "Ведений відпустив SDA", size=9.5, color=BUS_COL, bold=True, anchor="start"))
    p.append(text(640, py2 - 8, "STOP", size=9.5, color=OK_COL, bold=True))
    
    p.append(text(W / 2, H - 14, "9 тактів гарантують вихід веденого з поточного байтового вікна без апаратного скидання живлення", size=10.5, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "i2c-bus-lockup.svg"), W, H, *p, title="Механізм зависання шини I2C та процедура відновлення 9 тактами")


def fig_rtos_bus_deadlock():
    W, H = 840, 370
    p = []
    
    # Left: Bad Architecture (Direct HW access from ISR & Tasks)
    p.append(rect(30, 55, 370, 270, fill=WARN_BG, stroke=WARN_COL, sw=1.8, rx=6))
    p.append(text(215, 80, "Помилка: прямий доступ без захисту", size=11.5, color=WARN_COL, bold=True))
    
    p.append(rect(50, 100, 140, 42, fill="#ffffff", stroke=MUTED, sw=1.2))
    p.append(text(120, 126, "Задача A (Telemetry)", size=9.5, color=INK))
    
    p.append(rect(240, 100, 140, 42, fill="#ffffff", stroke=MUTED, sw=1.2))
    p.append(text(310, 126, "Задача B (Display)", size=9.5, color=INK))
    
    p.append(rect(145, 155, 140, 42, fill="#fdecea", stroke=WARN_COL, sw=1.5))
    p.append(text(215, 180, "Переривання (ISR)", size=10, color=WARN_COL, bold=True))
    
    p.append(arrow(120, 142, 180, 225, color=WARN_COL, sw=1.5))
    p.append(arrow(310, 142, 250, 225, color=WARN_COL, sw=1.5))
    p.append(arrow(215, 197, 215, 225, color=WARN_COL, sw=2))
    
    p.append(rect(125, 228, 180, 48, fill="#fee2e2", stroke=WARN_COL, sw=2))
    p.append(text(215, 248, "Апаратний драйвер SPI/I2C", size=10, color=WARN_COL, bold=True))
    p.append(text(215, 265, "КОНФЛІКТ РЕЄСТРІВ / ДЕДЛОК", size=9.5, color=WARN_COL, bold=True))
    
    p.append(text(215, 305, "М'ютекс у ISR викликає паніку ядра!", size=9.5, color=WARN_COL, bold=True))
    
    # Right: Good Architecture (Bus Arbiter Task / Queue + Mutex with Priority Inheritance)
    p.append(rect(430, 55, 380, 270, fill=OK_BG, stroke=OK_COL, sw=1.8, rx=6))
    p.append(text(620, 80, "Правильно: шлюз / менеджер шини", size=11.5, color=OK_COL, bold=True))
    
    p.append(rect(450, 100, 130, 42, fill="#ffffff", stroke=MUTED, sw=1.2))
    p.append(text(515, 126, "Задача A", size=10, color=INK))
    
    p.append(rect(660, 100, 130, 42, fill="#ffffff", stroke=MUTED, sw=1.2))
    p.append(text(725, 126, "Задача B", size=10, color=INK))
    
    # Queue / Mutex layer
    p.append(rect(500, 155, 240, 48, fill="#dcfce7", stroke=OK_COL, sw=1.6))
    p.append(text(620, 175, "Черга повідомлень (Queue)", size=10, color=OK_COL, bold=True))
    p.append(text(620, 192, "або Mutex + Priority Inheritance", size=9.5, color=INK))
    
    p.append(arrow(515, 142, 560, 155, color=OK_COL, sw=1.5))
    p.append(arrow(725, 142, 680, 155, color=OK_COL, sw=1.5))
    p.append(arrow(620, 203, 620, 228, color=OK_COL, sw=2))
    
    p.append(rect(520, 228, 200, 48, fill="#ffffff", stroke=OK_COL, sw=1.8))
    p.append(text(620, 248, "Єдиний потік-менеджер шини", size=10, color=OK_COL, bold=True))
    p.append(text(620, 265, "(Bus Server / Arbiter)", size=9.5, color=MUTED, italic=True))
    
    p.append(text(620, 305, "Транзакції атомарні, черги DMA захищені", size=9.5, color=OK_COL, bold=True))
    
    p.append(text(W / 2, H - 14, "Централізований шлюз шини запобігає пошкодженню транзакцій та зависанню переривань", size=10.5, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "rtos-bus-deadlock.svg"), W, H, *p, title="Конкуренція задач та архітектура захисту шин в RTOS")


if __name__ == "__main__":
    fig_conflict_taxonomy()
    fig_i2c_address_mux()
    fig_spi_miso_contention()
    fig_i2c_multimaster_arbitration()
    fig_i2c_bus_lockup()
    fig_rtos_bus_deadlock()
    print("OK: All figures generated successfully in", OUT)
