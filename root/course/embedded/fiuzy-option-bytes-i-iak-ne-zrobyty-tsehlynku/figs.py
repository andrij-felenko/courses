# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. option-bytes-architecture: Завантаження та апаратна дія Option Bytes ──
def fig_option_bytes_architecture():
    W, H = 920, 500
    p = []

    # Загальна рамка чипа
    p.append(rect(20, 20, 880, 460, fill="#ffffff", stroke=MUTED, sw=1.5, rx=10))
    p.append(text(460, 45, "Апаратна архітектура завантаження Option Bytes / Fuses у мікроконтролері", size=15, color=INK, bold=True))

    # Блок 1: Енергонезалежна пам'ять (Flash Info Block / eFuses / EEPROM)
    p.append(rect(45, 80, 220, 310, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(155, 108, "Енергонезалежне сховище", size=13, color=INK, bold=True))
    p.append(text(155, 126, "(Flash Info / eFuses / EEPROM)", size=10.5, color=MUTED))

    p.append(fitbox(60, 145, 190, 40, "RDP / Lock Bits\n(Рівні захисту від читання)", size=11, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(60, 195, 190, 40, "BOR / BOD Level\n(Пороги скидання за напругою)", size=11, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(60, 245, 190, 40, "WDG_SW / WDTON\n(Апаратний чи програмний WDG)", size=11, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(60, 295, 190, 40, "CKSEL / HSE / SUT\n(Джерело тактування й затримка)", size=11, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(60, 345, 190, 35, "nBOOT0 / RSTDISBL\n(Конфігурація пінів)", size=11, fill="#ffffff", stroke=MUTED))

    # POR і апаратний завантажувач
    p.append(rect(300, 80, 175, 120, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=8))
    p.append(text(387, 108, "Power-On Reset (POR)", size=12.5, color=NEG, bold=True))
    p.append(text(387, 128, "Детектор наростання VDD", size=10.5, color=INK))
    p.append(text(387, 148, "↓ Запуск апаратного FSM", size=10.5, color=NEG, bold=True))
    p.append(text(387, 168, "до розблокування ядра", size=10, color=MUTED))

    # Стрілка POR -> Сховище
    p.append(arrow(300, 140, 270, 140, color=NEG, sw=2))
    p.append(text(285, 130, "Read", size=10, color=NEG, bold=True))

    # Блок 2: Тіньові регістри-засувки (Shadow Registers / Latches)
    p.append(rect(300, 230, 175, 160, fill="#fdf6e2", stroke="#d97706", sw=1.8, rx=8))
    p.append(text(387, 258, "Тіньові регістри", size=13, color="#92400e", bold=True))
    p.append(text(387, 278, "Shadow Registers / Latches", size=10.5, color="#b45309"))
    p.append(text(387, 305, "Фізичні апаратні тригери", size=10.5, color=INK))
    p.append(text(387, 325, "Зберігають копію бітів", size=10.5, color=INK))
    p.append(text(387, 345, "Керують логікою напряму", size=10.5, color=INK))
    p.append(text(387, 368, "FLASH->OPTR / OBR", size=10.5, color=MUTED, bold=True))

    # Стрілка зі сховища в тіньові регістри
    p.append(arrow(265, 310, 295, 310, color="#d97706", sw=2.5))
    p.append(text(280, 298, "Load", size=10, color="#d97706", bold=True))

    # Блок 3: Контрольовані периферійні вузли та ядро
    nodes = [
        ("CoreSight SWD/JTAG", "Вимкнення / блокування шини налагодження", POS, 100),
        ("BOR Компаратор", "Встановлення порогу захисту 1.8 / 2.4 / 2.7 В", NEG, 165),
        ("Сторожовий таймер", "Старт WDG одразу з моменту подачі VDD", FIELD, 230),
        ("Дерево тактування", "Вибір HSI / HSE / PLL та затримок запуску", "#8b5cf6", 295),
        ("Ядро CPU & Boot ROM", "Маршрутизація вектору скидання Flash/SRAM", INK, 360),
    ]

    for title, desc, col, ypos in nodes:
        p.append(rect(540, ypos, 335, 52, fill="#ffffff", stroke=col, sw=1.5, rx=6))
        p.append(text(707, ypos + 20, title, size=12, color=col, bold=True))
        p.append(text(707, ypos + 38, desc, size=10, color=MUTED))
        p.append(arrow(475, ypos + 26, 535, ypos + 26, color=col, sw=1.8))

    # Нижній висновок
    b, _, _ = textbox(460, 440, "Option Bytes завантажуються апаратною схемою за нуль тактів CPU ще до зняття сигналу скидання з процесорного ядра.\nПрограмна помилка у фьюзах блокує апаратні модулі до початку виконання першої інструкції прошивки.",
                      size=11, fill="#f8fafc", stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "option-bytes-architecture.svg"), W, H, *p)

# ── 2. rdp-levels-state-machine: Граф станів STM32 Readout Protection (RDP) ──
def fig_rdp_levels_state_machine():
    W, H = 920, 460
    p = []

    p.append(text(460, 35, "Автомат станів захисту пам'яті STM32 RDP (Readout Protection)", size=15, color=INK, bold=True))

    # Рівень 0 (Open)
    p.append(rect(40, 80, 240, 280, fill="#ecfdf5", stroke=FIELD, sw=2, rx=10))
    p.append(text(160, 115, "Рівень 0 (Level 0)", size=14, color=FIELD, bold=True))
    p.append(text(160, 138, "Байт RDP = 0xAA", size=12, color=INK, bold=True))
    p.append(line(60, 155, 260, 155, color=FIELD, sw=1.2))
    p.append(text(160, 180, "• Повний доступ SWD/JTAG", size=11, color=INK))
    p.append(text(160, 205, "• Читання та запис Flash", size=11, color=INK))
    p.append(text(160, 230, "• Читання та запис SRAM", size=11, color=INK))
    p.append(text(160, 255, "• Зневадження та точки зупину", size=11, color=INK))
    p.append(text(160, 285, "Заводський стан", size=11, color=FIELD, bold=True))
    p.append(text(160, 305, "Для розробки та зневадження", size=10, color=MUTED))

    # Рівень 1 (Memory Protection)
    p.append(rect(340, 80, 240, 280, fill="#fef3c7", stroke="#d97706", sw=2, rx=10))
    p.append(text(460, 115, "Рівень 1 (Level 1)", size=14, color="#b45309", bold=True))
    p.append(text(460, 138, "Будь-яке значення крім 0xAA / 0xCC", size=10.5, color=INK, bold=True))
    p.append(line(360, 155, 560, 155, color="#d97706", sw=1.2))
    p.append(text(460, 180, "• Flash недоступна через SWD", size=11, color=INK))
    p.append(text(460, 205, "• Спроба читання → Bus Error", size=11, color=INK))
    p.append(text(460, 230, "• Ядро з Flash читає штатно", size=11, color=INK))
    p.append(text(460, 255, "• Доступний доступ до SRAM", size=11, color=INK))
    p.append(text(460, 285, "Серійний захист", size=11, color="#b45309", bold=True))
    p.append(text(460, 305, "Захист від копіювання коду", size=10, color=MUTED))

    # Рівень 2 (No Debug / Permanent Brick)
    p.append(rect(640, 80, 240, 280, fill="#fee2e2", stroke=POS, sw=2, rx=10))
    p.append(text(760, 115, "Рівень 2 (Level 2)", size=14, color=POS, bold=True))
    p.append(text(760, 138, "Байт RDP = 0xCC", size=12, color=POS, bold=True))
    p.append(line(660, 155, 860, 155, color=POS, sw=1.2))
    p.append(text(760, 180, "• SWD/JTAG вимкнено назавжди", size=11, color=POS, bold=True))
    p.append(text(760, 205, "• Завантаження з SRAM блоковано", size=11, color=INK))
    p.append(text(760, 230, "• Bootloader ROM блоковано", size=11, color=INK))
    p.append(text(760, 255, "• Оновлення лише з коду (IAP)", size=11, color=INK))
    p.append(text(760, 285, "ФАТАЛЬНИЙ СТАН", size=11, color=POS, bold=True))
    p.append(text(760, 305, "Незворотне запечатування", size=10, color=POS))

    # Стрілка L0 -> L1
    p.append(arrow(280, 170, 335, 170, color="#d97706", sw=2))
    p.append(text(310, 160, "RDP = 0xBB", size=10, color="#b45309", bold=True))

    # Стрілка L1 -> L0 (Mass Erase)
    p.append(arrow(340, 230, 285, 230, color=FIELD, sw=2))
    p.append(text(310, 218, "RDP = 0xAA", size=10, color=FIELD, bold=True))
    p.append(text(310, 245, "ПОВНЕ СТИРАННЯ", size=9.5, color=POS, bold=True))
    p.append(text(310, 258, "Flash + SRAM", size=9.5, color=POS))

    # Стрілка L1 -> L2
    p.append(arrow(580, 170, 635, 170, color=POS, sw=2.5))
    p.append(text(610, 160, "RDP = 0xCC", size=10, color=POS, bold=True))

    # Стрілка L0 -> L2 (пряма дуга знизу)
    p.append(line(160, 360, 160, 395, color=POS, sw=2))
    p.append(line(160, 395, 760, 395, color=POS, sw=2))
    p.append(arrow(760, 395, 760, 365, color=POS, sw=2))
    p.append(text(460, 390, "Прямий запис RDP = 0xCC (Незворотний перехід)", size=10.5, color=POS, bold=True))

    # Перекреслена стрілка повернення з L2
    p.append(line(640, 230, 585, 230, color=MUTED, sw=1.5, dash="4 3"))
    p.append(text(612, 220, "ЗАБОРОНЕНО", size=9.5, color=POS, bold=True))
    p.append(text(612, 236, "✕", size=14, color=POS, bold=True))

    # Нижній висновок
    b, _, _ = textbox(460, 435, "Перехід з Level 1 у Level 0 стирає всю пам'ять для захисту від зчитування через налагоджувач.\nЗворотного шляху з Level 2 не існує: інтерфейс SWD апаратно спалюється / блокується на рівні кремнію.",
                      size=10.5, fill="#f8fafc", stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "rdp-levels-state-machine.svg"), W, H, *p)

# ── 3. connect-under-reset-timing: Таймінги підключення SWD ──
def fig_connect_under_reset_timing():
    W, H = 920, 470
    p = []

    p.append(text(460, 30, "Часова діаграма: Звичайне підключення SWD проти Connect Under Reset", size=15, color=INK, bold=True))

    # Блок 1 (Верхній): Звичайне підключення (Збій)
    p.append(rect(30, 55, 860, 175, fill="#fff5f5", stroke=POS, sw=1.2, rx=8))
    p.append(text(170, 78, "Сценарій А: Звичайне підключення (Normal Connect) — ЗБІЙ", size=12.5, color=POS, bold=True))

    # Сигнали верхнього блоку
    p.append(text(90, 110, "NRST (MCU)", size=10.5, color=INK, bold=True))
    p.append(line(160, 120, 220, 120, color=NEG, sw=2))
    p.append(line(220, 120, 230, 105, color=NEG, sw=2))
    p.append(line(230, 105, 840, 105, color=NEG, sw=2))
    p.append(text(200, 135, "t0: VDD OK", size=9.5, color=MUTED))

    p.append(text(90, 148, "Код прошивки", size=10.5, color=INK, bold=True))
    p.append(rect(230, 140, 120, 22, fill="#e2e8f0", stroke=MUTED, sw=1))
    p.append(text(290, 155, "SystemInit()", size=9.5, color=INK))
    p.append(rect(350, 140, 140, 22, fill="#fee2e2", stroke=POS, sw=1.5))
    p.append(text(420, 155, "SWD → GPIO / Sleep", size=9.5, color=POS, bold=True))
    p.append(rect(490, 140, 350, 22, fill="#f1f5f9", stroke=MUTED, sw=1))
    p.append(text(665, 155, "Порти зневадження вимкнені / Ядро спить", size=9.5, color=MUTED))

    p.append(text(90, 190, "SWD Налагоджувач", size=10.5, color=INK, bold=True))
    p.append(line(160, 195, 550, 195, color=MUTED, sw=1.5, dash="4 3"))
    p.append(rect(550, 182, 140, 24, fill="#fee2e2", stroke=POS, sw=1.5))
    p.append(text(620, 198, "Спроба зв'язку SWD", size=9.5, color=POS, bold=True))
    p.append(text(780, 198, "❌ Помилка: No target connected", size=10, color=POS, bold=True))

    # Блок 2 (Нижній): Connect Under Reset (Успіх)
    p.append(rect(30, 245, 860, 175, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=8))
    p.append(text(210, 268, "Сценарій Б: Підключення під час скидання (Connect Under Reset) — УСПІХ", size=12.5, color=FIELD, bold=True))

    # Сигнали нижнього блоку
    p.append(text(90, 300, "NRST (MCU)", size=10.5, color=INK, bold=True))
    p.append(line(160, 310, 520, 310, color=NEG, sw=2.5))
    p.append(text(340, 325, "Налагоджувач утримує NRST = 0 (Ядро зупинене)", size=9.5, color=NEG, bold=True))
    p.append(line(520, 310, 530, 295, color=FIELD, sw=2))
    p.append(line(530, 295, 840, 295, color=FIELD, sw=2))

    p.append(text(90, 345, "SWD CoreSight DAP", size=10.5, color=INK, bold=True))
    p.append(rect(230, 335, 270, 24, fill="#dbeafe", stroke=NEG, sw=1.5))
    p.append(text(365, 351, "DAP активний під час Reset: запис DEMCR.VC_CORERESET", size=9.5, color=NEG, bold=True))
    p.append(rect(530, 335, 140, 24, fill="#dcfce7", stroke=FIELD, sw=1.5))
    p.append(text(600, 351, "Зупинка на Reset Vector", size=9.5, color=FIELD, bold=True))
    p.append(rect(670, 335, 170, 24, fill="#f8fafc", stroke=FIELD, sw=1.2))
    p.append(text(755, 351, "Повний контроль / Flash Erase", size=9.5, color=FIELD))

    p.append(text(90, 390, "Код прошивки", size=10.5, color=INK, bold=True))
    p.append(text(340, 395, "Не виконується (Ядро заморожене до першої інструкції)", size=9.5, color=FIELD, bold=True))
    p.append(text(730, 395, "✓ Код знешкоджено", size=10.5, color=FIELD, bold=True))

    b, _, _ = textbox(460, 442, "Connect Under Reset утримує пін NRST притиснутим до землі, поки налагоджувач конфігурує апаратне перехоплення вектору скидання.\nЦе унеможливлює виконання користувацького коду, який вимикає лінії SWD або переводить чип у глибокий сон.",
                      size=10, fill="#ffffff", stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "connect-under-reset-timing.svg"), W, H, *p)

# ── 4. external-clock-injection-schematic: Ін'єкція зовнішнього тактування ──
def fig_external_clock_injection_schematic():
    W, H = 920, 460
    p = []

    p.append(text(460, 30, "Схема реанімації мікроконтролера через ін'єкцію зовнішнього тактування (Clock Injection)", size=15, color=INK, bold=True))

    # Джерело тактування (Зовнішній генератор / допоміжний МК)
    p.append(rect(40, 70, 250, 320, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(165, 100, "Джерело тактування", size=13.5, color=NEG, bold=True))
    p.append(text(165, 120, "Генератор / Допоміжний МК", size=10.5, color=MUTED))

    p.append(rect(65, 150, 200, 75, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=6))
    p.append(text(165, 175, "Генератор меандру", size=11.5, color=NEG, bold=True))
    p.append(text(165, 195, "Частота: 1–8 МГц (TTL/CMOS)", size=10.5, color=INK))
    p.append(text(165, 212, "Амплітуда: 3.3 В або 5 В", size=10, color=MUTED))

    p.append(circle(265, 185, 5, fill=NEG, stroke=INK))
    p.append(text(235, 180, "CLK_OUT", size=9.5, color=NEG, bold=True))

    p.append(circle(165, 340, 5, fill=INK, stroke=INK))
    p.append(text(165, 360, "GND (Спільна земля)", size=10.5, color=INK, bold=True))

    # Заблокований цільовий чип (AVR / STM32)
    p.append(rect(590, 70, 290, 320, fill="#fff5f5", stroke=POS, sw=1.8, rx=8))
    p.append(text(735, 100, "Заблокований цільовий МК", size=13.5, color=POS, bold=True))
    p.append(text(735, 120, "AVR (ATmega/tiny) або STM32", size=10.5, color=MUTED))

    # Піни МК
    p.append(circle(590, 185, 6, fill=NEG, stroke=INK))
    p.append(text(645, 190, "XTAL1 / OSC_IN", size=11, color=NEG, bold=True))

    p.append(circle(590, 245, 5, fill=FIELD, stroke=INK))
    p.append(text(630, 250, "RESET", size=10.5, color=FIELD, bold=True))

    p.append(circle(590, 285, 5, fill=FIELD, stroke=INK))
    p.append(text(645, 290, "SWDIO / MOSI", size=10.5, color=FIELD, bold=True))

    p.append(circle(590, 315, 5, fill=FIELD, stroke=INK))
    p.append(text(645, 320, "SWCLK / SCK", size=10.5, color=FIELD, bold=True))

    p.append(circle(735, 370, 5, fill=INK, stroke=INK))
    p.append(text(735, 360, "GND", size=10.5, color=INK, bold=True))

    # Резистор узгодження на лінії тактування
    p.append(line(265, 185, 380, 185, color=NEG, sw=2))
    p.append(rect(380, 175, 60, 20, fill="#ffffff", stroke=NEG, sw=1.5))
    p.append(text(410, 189, "100–330 Ом", size=9.5, color=NEG, bold=True))
    p.append(arrow(440, 185, 584, 185, color=NEG, sw=2))
    p.append(text(460, 170, "Меандр 1–8 МГц", size=10, color=NEG, bold=True))

    # Програматор (SWD / ISP)
    p.append(rect(330, 240, 180, 120, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(420, 265, "Програматор", size=12, color=FIELD, bold=True))
    p.append(text(420, 282, "ST-Link / USBasp / J-Link", size=9.5, color=MUTED))

    p.append(arrow(510, 290, 584, 250, color=FIELD, sw=1.5))
    p.append(arrow(510, 300, 584, 285, color=FIELD, sw=1.5))
    p.append(arrow(510, 310, 584, 315, color=FIELD, sw=1.5))

    # Лінія спільної землі
    p.append(line(165, 340, 165, 400, color=INK, sw=2))
    p.append(line(165, 400, 735, 400, color=INK, sw=2))
    p.append(line(735, 400, 735, 375, color=INK, sw=2))
    p.append(line(420, 360, 420, 400, color=INK, sw=2))
    p.append(text(450, 415, "СПІЛЬНА ЗЕМЛЯ (Common Ground)", size=10.5, color=INK, bold=True))

    # Нижній висновок
    b, _, _ = textbox(460, 442, "Якщо фьюзи налаштовані на зовнішній кварц, якого немає, автомат інтерфейсу програмування не отримує стробуючих тактів.\nПодача зовнішнього меандру на XTAL1 відновлює тактування шини SPI/SWD і дозволяє перепрограмувати фьюзи на внутрішній генератор.",
                      size=9.5, fill="#ffffff", stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "external-clock-injection-schematic.svg"), W, H, *p)

if __name__ == "__main__":
    fig_option_bytes_architecture()
    fig_rdp_levels_state_machine()
    fig_connect_under_reset_timing()
    fig_external_clock_injection_schematic()
    print("All figures generated successfully.")
