# -*- coding: utf-8 -*-
"""Фігури до теми «Шина MDC/MDIO» (IEEE 802.3 Clause 22 та Clause 45).
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

ORANGE = "#e67e22"
PURPLE = "#8e44ad"


# ── 1. Топологія шини MDC/MDIO ──────────────────────────────────────────────
def fig_bus_topology():
    W, H = 760, 360
    f = [text(W / 2, 24, "Топологія шини MDC/MDIO: ведучий MAC та трансивери PHY на спільних лініях",
              size=14, bold=True)]

    # Ведучий MAC / STA
    b_mac, w_mac, h_mac = textbox(110, 170, "Ведучий MAC / STA\n(Station Management)\nКонтролер Ethernet",
                                  size=12, pad=10, fill="#eaf2f8", stroke=NEG, bold=True)
    f.append(b_mac)

    # Лінії живлення та Pull-Up резистор
    f.append(line(370, 50, 410, 50, color=POS, sw=2))
    f.append(text(390, 42, "+3.3V / +2.5V (VDD)", size=11, color=POS, bold=True))
    # Резистор підтяжки
    f.append(rect(378, 65, 24, 45, fill="#fff", stroke=LINE, sw=1.5, rx=2))
    f.append(line(390, 50, 390, 65, color=LINE, sw=1.5))
    f.append(line(390, 110, 390, 140, color=LINE, sw=1.5))
    f.append(text(415, 92, "Rp (1.5–10 кОм)", size=11, color=INK, anchor="start"))
    f.append(circle(390, 140, 3.5, fill=INK, stroke=INK))

    # Лінія MDC (Clock)
    f.append(line(200, 205, 710, 205, color=NEG, sw=2.2))
    f.append(text(210, 185, "MDC (Management Data Clock, до 2.5 МГц)", size=11, color=NEG, anchor="start", bold=True))

    # Лінія MDIO (Data)
    f.append(line(200, 130, 710, 130, color=FIELD, sw=2.2))
    f.append(text(210, 115, "MDIO (Двонаправлена лінія даних з відкритим стоком)", size=11, color=FIELD, anchor="start", bold=True))

    # З'єднання від MAC до шин
    f.append(line(190, 130, 200, 130, color=FIELD, sw=2.2))
    f.append(line(190, 205, 200, 205, color=NEG, sw=2.2))

    # PHY 0
    b_phy0, _, _ = textbox(300, 280, "PHY 0 (PHYAD=0)\n10/100/1000M\nТрансивер",
                           size=11, pad=8, fill="#fdfefe", stroke=LINE)
    f.append(b_phy0)
    f.append(line(300, 130, 300, 252, color=FIELD, sw=1.6))
    f.append(circle(300, 130, 3, fill=FIELD, stroke=FIELD))
    f.append(line(315, 205, 315, 252, color=NEG, sw=1.6))
    f.append(circle(315, 205, 3, fill=NEG, stroke=NEG))

    # PHY 1
    b_phy1, _, _ = textbox(470, 280, "PHY 1 (PHYAD=1)\n10/100/1000M\nТрансивер",
                           size=11, pad=8, fill="#fdfefe", stroke=LINE)
    f.append(b_phy1)
    f.append(line(470, 130, 470, 252, color=FIELD, sw=1.6))
    f.append(circle(470, 130, 3, fill=FIELD, stroke=FIELD))
    f.append(line(485, 205, 485, 252, color=NEG, sw=1.6))
    f.append(circle(485, 205, 3, fill=NEG, stroke=NEG))

    # Крапки багатоточкової шини
    f.append(text(575, 280, "• • •", size=20, color=MUTED, anchor="middle"))

    # PHY 31
    b_phy31, _, _ = textbox(660, 280, "PHY 31 (PHYAD=31)\n10/100/1000M\nТрансивер",
                            size=11, pad=8, fill="#fdfefe", stroke=LINE)
    f.append(b_phy31)
    f.append(line(650, 130, 650, 252, color=FIELD, sw=1.6))
    f.append(circle(650, 130, 3, fill=FIELD, stroke=FIELD))
    f.append(line(665, 205, 665, 252, color=NEG, sw=1.6))
    f.append(circle(665, 205, 3, fill=NEG, stroke=NEG))

    # Пояснювальний блок знизу
    f.append(text(W / 2, 345, "Спільна пара ліній обслуговує до 32 пристроїв PHY; адресація задається апаратно пінами bootstrap",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "bus-topology.svg"), W, H, *f)


# ── 2. Часова діаграма та формат кадру Clause 22 ────────────────────────────
def fig_clause22_timing():
    W, H = 760, 410
    f = [text(W / 2, 22, "Структура та часові діаграми кадрів IEEE 802.3 Clause 22 (Read / Write)",
              size=14, bold=True)]

    # --- Кадр ЗАПИСУ (Write) ---
    f.append(text(30, 52, "Кадр запису (Write Frame, Opcode = 01):", size=12, bold=True, anchor="start", color=NEG))

    fields_wr = [
        ("PRE (32 біти)", 140, "#eaeded", "Синхронізація (усі «1»)"),
        ("ST", 38, "#d5dbdb", "01"),
        ("OP", 38, "#aed6f1", "01"),
        ("PHYAD", 65, "#d4efdf", "A4..A0"),
        ("REGAD", 65, "#fdebd0", "R4..R0"),
        ("TA", 40, "#fadbd8", "10"),
        ("DATA (16 бітів)", 175, "#ebdef0", "D15 .. D0 (від MAC до PHY)"),
        ("IDLE", 45, "#f4f6f8", "Hi-Z"),
    ]

    x = 30
    y = 65
    h_box = 32
    for name, w_f, col, desc in fields_wr:
        f.append(rect(x, y, w_f, h_box, fill=col, stroke=LINE, sw=1.2, rx=3))
        f.append(text(x + w_f / 2, y + 15, name, size=10.5, bold=True))
        f.append(text(x + w_f / 2, y + 27, desc, size=9.5, color=MUTED))
        x += w_f

    f.append(text(30, 115, "MAC формує всі поля від PRE до DATA включно. TA = «10» утримується ведучим.",
                  size=10.5, color=INK, anchor="start"))

    # --- Розділювач ---
    f.append(line(30, 135, 730, 135, color="#e5e7e9", sw=1.2, dash="4,4"))

    # --- Кадр ЧИТАННЯ (Read) ---
    f.append(text(30, 155, "Кадр читання (Read Frame, Opcode = 10):", size=12, bold=True, anchor="start", color=FIELD))

    fields_rd = [
        ("PRE (32 біти)", 140, "#eaeded", "Синхронізація (усі «1»)"),
        ("ST", 38, "#d5dbdb", "01"),
        ("OP", 38, "#aed6f1", "10"),
        ("PHYAD", 65, "#d4efdf", "A4..A0"),
        ("REGAD", 65, "#fdebd0", "R4..R0"),
        ("TA", 40, "#f9e79f", "Z0"),
        ("DATA (16 бітів)", 175, "#d5f5e3", "D15 .. D0 (від PHY до MAC)"),
        ("IDLE", 45, "#f4f6f8", "Hi-Z"),
    ]

    x = 30
    y = 168
    for name, w_f, col, desc in fields_rd:
        f.append(rect(x, y, w_f, h_box, fill=col, stroke=LINE, sw=1.2, rx=3))
        f.append(text(x + w_f / 2, y + 15, name, size=10.5, bold=True))
        f.append(text(x + w_f / 2, y + 27, desc, size=9.5, color=MUTED))
        x += w_f

    # --- Деталізація Turnaround (TA) ---
    b_ta, _, _ = textbox(380, 275,
                         "Механізм перемикання лінії Turnaround (TA) під час читання:\n"
                         "• 1-й такт (Z): MAC відпускає лінію в Hi-Z; підтяжка тримає високий рівень\n"
                         "• 2-й такт (0): PHY перехоплює шину і притискає MDIO до нуля (підтвердження)\n"
                         "• Далі PHY передає 16 біт даних D15..D0, синхронізуючись за тактами MDC",
                         size=11, pad=10, fill="#fef9e7", stroke="#f39c12")
    f.append(b_ta)

    # Стрілки передачі володіння
    f.append(text(200, 360, "Керує MAC (Ведучий)", size=11, color=NEG, bold=True))
    f.append(arrow(200, 370, 350, 370, color=NEG))
    f.append(text(540, 360, "Керує PHY (Ведений)", size=11, color=FIELD, bold=True))
    f.append(arrow(430, 370, 580, 370, color=FIELD))

    render(os.path.join(IMG, "clause22-timing.svg"), W, H, *f)


# ── 3. Clause 45: пряма транзакція проти непрямого доступу ──────────────────
def fig_clause45_indirect_vs_direct():
    W, H = 760, 420
    f = [text(W / 2, 22, "Розширення Clause 45: прямий доступ MMD проти непрямого мосту Clause 22",
              size=14, bold=True)]

    # --- Верхня частина: Прямий Clause 45 ---
    f.append(text(30, 50, "Прямий протокол Clause 45 (ST = 00, 10G/40G/100G Ethernet):", size=12, bold=True, anchor="start", color=NEG))

    # Крок 1: Address Frame
    f.append(text(40, 72, "1. Кадр адреси (OP = 00, Address):", size=11, bold=True, anchor="start"))
    fields_c45_addr = [
        ("PRE", 45, "#eaeded"),
        ("ST (00)", 55, "#fadbd8"),
        ("OP (00)", 55, "#aed6f1"),
        ("PRTAD (5б)", 75, "#d4efdf"),
        ("DEVAD (5б)", 75, "#fdebd0"),
        ("TA (10)", 50, "#fadbd8"),
        ("16-бітна адреса регістра (0x0000..0xFFFF)", 260, "#ebdef0"),
        ("IDLE", 45, "#f4f6f8"),
    ]
    x = 40
    y = 80
    for name, w_f, col in fields_c45_addr:
        f.append(rect(x, y, w_f, 24, fill=col, stroke=LINE, sw=1.1, rx=2))
        f.append(text(x + w_f / 2, y + 16, name, size=9.5, bold=True))
        x += w_f

    # Крок 2: Data Frame
    f.append(text(40, 120, "2. Кадр даних (OP = 01 Запис / 11 Читання / 10 Читання з автоінкрементом):", size=11, bold=True, anchor="start"))
    fields_c45_data = [
        ("PRE", 45, "#eaeded"),
        ("ST (00)", 55, "#fadbd8"),
        ("OP (01/11/10)", 75, "#aed6f1"),
        ("PRTAD (5б)", 70, "#d4efdf"),
        ("DEVAD (5б)", 70, "#fdebd0"),
        ("TA (10/Z0)", 60, "#fadbd8"),
        ("16-бітні дані (DATA D15..D0)", 240, "#d5f5e3"),
        ("IDLE", 45, "#f4f6f8"),
    ]
    x = 40
    y = 128
    for name, w_f, col in fields_c45_data:
        f.append(rect(x, y, w_f, 24, fill=col, stroke=LINE, sw=1.1, rx=2))
        f.append(text(x + w_f / 2, y + 16, name, size=9.5, bold=True))
        x += w_f

    f.append(line(30, 168, 730, 168, color="#d5dbdb", sw=1.2, dash="4,4"))

    # --- Нижня частина: Непрямий міст Clause 22 ---
    f.append(text(30, 188, "Непрямий доступ через регістри 13 і 14 Clause 22 (для старих MAC):", size=12, bold=True, anchor="start", color=PURPLE))

    b_step1, _, _ = textbox(190, 240,
                            "Крок 1: Вибір MMD пристрою\n"
                            "Запис у Регістр 13 (MMD Control):\n"
                            "• Function = 00 (Address Mode)\n"
                            "• DEVAD = номер домену (напр. 3 = PCS)",
                            size=10.5, pad=8, fill="#fdfefe", stroke=PURPLE)
    f.append(b_step1)

    f.append(arrow(310, 240, 360, 240, color=PURPLE))

    b_step2, _, _ = textbox(480, 240,
                            "Крок 2: Передача адреси\n"
                            "Запис у Регістр 14 (MMD Address/Data):\n"
                            "• Запис 16-бітної адреси цільового\n"
                            "  регістра Clause 45 у вибраному MMD",
                            size=10.5, pad=8, fill="#fdfefe", stroke=PURPLE)
    f.append(b_step2)

    b_step3, _, _ = textbox(190, 335,
                            "Крок 3: Перемикання в режим даних\n"
                            "Запис у Регістр 13 (MMD Control):\n"
                            "• Function = 01 (Data Mode)\n"
                            "• DEVAD = той самий номер домену",
                            size=10.5, pad=8, fill="#fdfefe", stroke=PURPLE)
    f.append(b_step3)

    f.append(arrow(310, 335, 360, 335, color=PURPLE))

    b_step4, _, _ = textbox(480, 335,
                            "Крок 4: Операція з даними\n"
                            "Читання або Запис через Регістр 14:\n"
                            "• Зчитування/запис 16-бітних даних\n"
                            "  за раніше встановленою адресою",
                            size=10.5, pad=8, fill="#e8f8f5", stroke=FIELD)
    f.append(b_step4)

    f.append(text(W / 2, 400, "MMD домени: 1 (PMD/PMA), 2 (WIS), 3 (PCS), 4 (PHY XS), 5 (DTE XS), 7 (Auto-Negotiation)",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "clause45-indirect-vs-direct.svg"), W, H, *f)


# ── 4. Карта регістрів PHY та механіка Latching Low ─────────────────────────
def fig_phy_register_model():
    W, H = 760, 410
    f = [text(W / 2, 22, "Карта регістрів Ethernet PHY та механіка засувки Link Status (Latching Low)",
              size=14, bold=True)]

    # Ліва колонка: карта стандартних регістрів
    f.append(text(170, 50, "Стандартні регістри Clause 22 (0..15):", size=12, bold=True, color=NEG))

    reg_map = [
        ("0", "BMCR", "Basic Mode Control (Reset, Speed, Duplex, AutoNeg)"),
        ("1", "BMSR", "Basic Mode Status (Capabilities, AutoNeg, Link Status)"),
        ("2", "PHYID1", "PHY Identifier 1 (OUI біти 3..18)"),
        ("3", "PHYID2", "PHY Identifier 2 (OUI біти 19..24 + Model + Rev)"),
        ("4", "ANAR", "Auto-Negotiation Advertisement (Власні можливості)"),
        ("5", "ANLPAR", "Link Partner Ability (Можливості партнера по лінку)"),
        ("9", "1000CR", "1000BASE-T Control (Master/Slave, 1G режими)"),
        ("10", "1000SR", "1000BASE-T Status (Master/Slave результат, статус)"),
        ("13", "MMD_CTRL", "MMD Access Control (Міст до Clause 45)"),
        ("14", "MMD_DATA", "MMD Access Address/Data (Міст до Clause 45)"),
    ]

    y = 68
    for addr, name, desc in reg_map:
        f.append(rect(20, y, 32, 22, fill="#eaeded", stroke=LINE, sw=1, rx=2))
        f.append(text(36, y + 15, addr, size=10, bold=True))
        f.append(rect(56, y, 75, 22, fill="#e8f8f5", stroke=LINE, sw=1, rx=2))
        f.append(text(93, y + 15, name, size=10, bold=True, color=FIELD))
        f.append(rect(135, y, 195, 22, fill="#fdfefe", stroke=LINE, sw=1, rx=2))
        f.append(text(142, y + 15, desc, size=9.5, anchor="start", color=INK))
        y += 26

    # Права колонка: розбір BMSR Bit 2 (Link Status, Latching Low)
    f.append(text(540, 50, "Особливість BMSR Bit 2 (Link Status, LL):", size=12, bold=True, color=FIELD))

    b_ll, _, _ = textbox(540, 140,
                         "Чому звичайне опитування не губить обрив лінка:\n\n"
                         "1. Нормальний стан: Кабель підключено, Link = 1.\n"
                         "2. Подія збою: Кабель висмикнули й вставили назад.\n"
                         "   Аналоговий лінк відновився (1), але внутрішній\n"
                         "   тригер засувки зафіксував обрив (Latch = 0).\n"
                         "3. 1-ше читання BMSR: Повертає «0» (повідомляє стек\n"
                         "   про те, що лінк падав!) і скидає засувку.\n"
                         "4. 2-ге читання BMSR: Повертає реальний стан «1».",
                         size=10.5, pad=10, fill="#fef9e7", stroke="#f39c12")
    f.append(b_ll)

    # Часова ілюстрація читання LL
    f.append(rect(360, 255, 370, 110, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=4))
    f.append(text(545, 275, "Хронологія сигналів та регістрів", size=11, bold=True))

    f.append(text(375, 298, "Лінія зв'язку:", size=10, color=MUTED, anchor="start"))
    f.append(line(460, 295, 520, 295, color=FIELD, sw=2))
    f.append(line(520, 295, 520, 305, color=POS, sw=2))
    f.append(line(520, 305, 550, 305, color=POS, sw=2)) # обрив
    f.append(line(550, 305, 550, 295, color=FIELD, sw=2))
    f.append(line(550, 295, 710, 295, color=FIELD, sw=2))

    f.append(text(375, 328, "Регістр BMSR:", size=10, color=MUTED, anchor="start"))
    f.append(line(460, 325, 520, 325, color=FIELD, sw=2))
    f.append(line(520, 325, 520, 335, color=POS, sw=2))
    f.append(line(520, 335, 620, 335, color=POS, sw=2)) # тримає 0 до читання
    f.append(line(620, 335, 620, 325, color=FIELD, sw=2))
    f.append(line(620, 325, 710, 325, color=FIELD, sw=2))

    f.append(line(620, 260, 620, 355, color=NEG, sw=1.5, dash="3,3"))
    f.append(text(620, 350, "1-ше читання (скидання засувки)", size=9.5, color=NEG))

    f.append(text(W / 2, 395, "Latching Low гарантує, що жоден мікрообрив кабелю не пройде непоміченим для операційної системи",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "phy-register-model.svg"), W, H, *f)


# ── 5. Таймінги та вибірка бітів при Bit-Banging ────────────────────────────
def fig_bitbang_sampling():
    W, H = 760, 360
    f = [text(W / 2, 22, "Часові параметри вибірки та біт-бенгінгу на шині MDC/MDIO",
              size=14, bold=True)]

    # Сигнал MDC
    f.append(text(60, 80, "MDC (Clock)", size=12, bold=True, color=NEG, anchor="start"))
    # Меандр такту
    f.append(line(160, 95, 230, 95, color=NEG, sw=2.2))
    f.append(line(230, 95, 230, 55, color=NEG, sw=2.2))
    f.append(line(230, 55, 350, 55, color=NEG, sw=2.2))
    f.append(line(350, 55, 350, 95, color=NEG, sw=2.2))
    f.append(line(350, 95, 470, 95, color=NEG, sw=2.2))
    f.append(line(470, 95, 470, 55, color=NEG, sw=2.2))
    f.append(line(470, 55, 590, 55, color=NEG, sw=2.2))
    f.append(line(590, 55, 590, 95, color=NEG, sw=2.2))
    f.append(line(590, 95, 690, 95, color=NEG, sw=2.2))

    # Вимірювання періоду T_mdc
    f.append(line(230, 42, 470, 42, color=MUTED, sw=1.2))
    f.append(arrow(290, 42, 230, 42, color=MUTED))
    f.append(arrow(410, 42, 470, 42, color=MUTED))
    f.append(text(350, 38, "T_MDC ≥ 400 нс (f ≤ 2.5 МГц)", size=10.5, color=MUTED))

    # Сигнал MDIO
    f.append(text(60, 170, "MDIO (Data)", size=12, bold=True, color=FIELD, anchor="start"))
    # Шина даних з перепадами на спадному фронті
    f.append(line(160, 185, 200, 185, color=FIELD, sw=2.2))
    f.append(line(200, 185, 215, 150, color=FIELD, sw=1.5))
    f.append(line(200, 150, 215, 185, color=FIELD, sw=1.5))
    f.append(line(215, 150, 335, 150, color=FIELD, sw=2.2))
    f.append(line(215, 185, 335, 185, color=FIELD, sw=2.2))
    f.append(line(335, 150, 350, 185, color=FIELD, sw=1.5))
    f.append(line(335, 185, 350, 150, color=FIELD, sw=1.5))
    f.append(line(350, 150, 455, 150, color=FIELD, sw=2.2))
    f.append(line(350, 185, 455, 185, color=FIELD, sw=2.2))
    f.append(line(455, 150, 470, 185, color=FIELD, sw=1.5))
    f.append(line(455, 185, 470, 150, color=FIELD, sw=1.5))
    f.append(line(470, 150, 690, 150, color=FIELD, sw=2.2))
    f.append(line(470, 185, 690, 185, color=FIELD, sw=2.2))

    # Моменти встановлення (Setup) та утримання (Hold)
    f.append(line(230, 55, 230, 215, color=POS, sw=1.5, dash="3,3"))
    f.append(text(230, 230, "Фронт наростання MDC:\nВибірка даних (Sampling)", size=10.5, color=POS))

    # Зміна даних на спаді
    f.append(line(350, 95, 350, 215, color=NEG, sw=1.5, dash="3,3"))
    f.append(text(350, 230, "Спадний фронт MDC:\nЗміна біта на лінії MDIO", size=10.5, color=NEG))

    # Позначення t_setup та t_hold
    f.append(rect(190, 142, 40, 52, fill="none", stroke=POS, sw=1.2, rx=2))
    f.append(text(210, 132, "t_su ≥ 10 нс", size=9.5, color=POS))
    f.append(rect(230, 142, 40, 52, fill="none", stroke=POS, sw=1.2, rx=2))
    f.append(text(250, 132, "t_h ≥ 10 нс", size=9.5, color=POS))

    # Пояснювальний блок знизу
    b_rules, _, _ = textbox(W / 2, 305,
                            "Золоте правило Bit-Banging: дані виставляються при MDC = 0 (на спаді),\n"
                            "а зчитуються приймачем суворо при MDC = 1 (на наростанні).",
                            size=11, pad=8, fill="#fdfefe", stroke=LINE)
    f.append(b_rules)

    render(os.path.join(IMG, "bitbang-sampling.svg"), W, H, *f)


if __name__ == "__main__":
    fig_bus_topology()
    fig_clause22_timing()
    fig_clause45_indirect_vs_direct()
    fig_phy_register_model()
    fig_bitbang_sampling()
    print("Усі 5 фігур успішно згенеровано!")
