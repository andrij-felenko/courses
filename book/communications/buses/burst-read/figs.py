# -*- coding: utf-8 -*-
"""Фігури теми «Пакетне зчитування регістрів» (book/communications/buses/burst-read).
Чистий Python без зовнішніх залежностей; svgkit імпортується зі scripts/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Порівняння побайтового й пакетного зчитування ───────────────────────────
def fig_comparison():
    W, H = 920, 480
    p = []
    p.append(text(W/2, 28, "Порівняння витрат шини: одиночні транзакції проти Burst-пакета", size=18, bold=True))
    p.append(text(W/2, 48, "зчитування 6 байтів вимірів 3-осьового давача (X_L, X_H, Y_L, Y_H, Z_L, Z_H)", size=12, color=MUTED, italic=True))

    # Блок 1: Побайтове зчитування (Single Read x 6)
    y1 = 75
    p.append(rect(40, y1, 840, 175, fill="#fff7f7", stroke=POS, sw=1.5, rx=8))
    p.append(text(55, y1+22, "Одиночні транзакції (Single-Byte Read × 6)", size=13, color=POS, anchor="start", bold=True))
    p.append(text(55, y1+38, "Кожен байт вимагає окремого циклу адресації, повторного старту й підтверджень", size=11, color=MUTED, anchor="start"))

    cw = 130
    x_start = 55
    ty = y1 + 52
    for i in range(6):
        bx = x_start + i * cw
        p.append(rect(bx, ty, 122, 54, fill="#ffffff", stroke="#d98880", sw=1.2, rx=4))
        p.append(rect(bx+2, ty+2, 22, 22, fill="#e6b0aa", stroke="none", rx=2))
        p.append(text(bx+13, ty+17, "S", size=10, bold=True, color="#78281f"))
        p.append(rect(bx+26, ty+2, 38, 22, fill="#f2d7d5", stroke="none", rx=2))
        p.append(text(bx+45, ty+16, "Addr", size=9.5, color=INK))
        p.append(rect(bx+66, ty+2, 34, 22, fill="#f9e79f", stroke="none", rx=2))
        p.append(text(bx+83, ty+16, "Reg", size=9.5, color="#7d6608"))
        p.append(rect(bx+102, ty+2, 18, 22, fill="#e6b0aa", stroke="none", rx=2))
        p.append(text(bx+111, ty+17, "P", size=10, bold=True, color="#78281f"))

        p.append(rect(bx+2, ty+28, 62, 22, fill="#d5f5e3", stroke="none", rx=2))
        p.append(text(bx+33, ty+43, f"Data[{i}]", size=9.5, bold=True, color="#196f3d"))
        p.append(rect(bx+66, ty+28, 54, 22, fill="#fadbd8", stroke="none", rx=2))
        p.append(text(bx+93, ty+43, "Sr+Stop", size=9.5, color=MUTED))

    p.append(rect(55, y1+118, 810, 42, fill="#fdedec", stroke=POS, sw=1, rx=4))
    p.append(text(W/2, y1+144, "174 такти шини I2C + 6 програмних затримок переривань CPU · Корисна ефективність: 27.6%", size=11.5, color=POS, bold=True))

    # Блок 2: Пакетне зчитування (Burst Read)
    y2 = 265
    p.append(rect(40, y2, 840, 195, fill="#f4faf5", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(55, y2+22, "Пакетна транзакція (Burst Read: 1 Start + 1 Reg + 6 Data)", size=13, color=FIELD, anchor="start", bold=True))
    p.append(text(55, y2+38, "Один префікс адресації; апаратний автоінкремент покажчика читає весь масив поспіль", size=11, color=MUTED, anchor="start"))

    ty2 = y2 + 52
    # Start
    p.append(rect(55, ty2, 34, 52, fill="#d5e8d4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(72, ty2+31, "START", size=9.5, bold=True, color="#196f3d"))
    # Dev Addr (W)
    p.append(rect(93, ty2, 82, 52, fill="#d5e8d4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(134, ty2+24, "Адреса (W)", size=10, bold=True, color=INK))
    p.append(text(134, ty2+40, "+ ACK", size=9.5, color=MUTED))
    # Reg Start Addr
    p.append(rect(179, ty2, 92, 52, fill="#fff2cc", stroke="#d6b656", sw=1.2, rx=4))
    p.append(text(225, ty2+24, "Регістр 0x28", size=10, bold=True, color="#7d6608"))
    p.append(text(225, ty2+40, "OUTX_L_A + ACK", size=9.5, color=MUTED))
    # ReStart
    p.append(rect(275, ty2, 38, 52, fill="#d5e8d4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(294, ty2+31, "Sr", size=10, bold=True, color="#196f3d"))
    # Dev Addr (R)
    p.append(rect(317, ty2, 82, 52, fill="#d5e8d4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(358, ty2+24, "Адреса (R)", size=10, bold=True, color=INK))
    p.append(text(358, ty2+40, "+ ACK", size=9.5, color=MUTED))

    # 6 Data Bytes
    labels = ["X_L", "X_H", "Y_L", "Y_H", "Z_L", "Z_H"]
    reg_nums = ["0x28", "0x29", "0x2A", "0x2B", "0x2C", "0x2D"]
    for i, (lb, rn) in enumerate(zip(labels, reg_nums)):
        dx = 403 + i * 72
        p.append(rect(dx, ty2, 68, 52, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=4))
        p.append(text(dx+34, ty2+20, lb, size=11, bold=True, color="#117864"))
        p.append(text(dx+34, ty2+34, rn, size=9.5, color=MUTED))
        p.append(text(dx+34, ty2+46, "ACK" if i < 5 else "NACK", size=9.5, bold=True, color=FIELD if i < 5 else POS))

    # Stop
    p.append(rect(839, ty2, 36, 52, fill="#fadbd8", stroke=POS, sw=1.2, rx=4))
    p.append(text(857, ty2+31, "STOP", size=9.5, bold=True, color=POS))

    p.append(rect(55, y2+118, 810, 60, fill="#eafaf1", stroke=FIELD, sw=1, rx=4))
    p.append(text(W/2, y2+140, "74 такти шини I2C (у 2.35 раза швидше) · Безперервний потік без простоїв процесора", size=11.5, color=FIELD, bold=True))
    p.append(text(W/2, y2+162, "Гарантована часова узгодженість: усі осі X, Y, Z належать одному моменту вибірки ADC", size=10.5, color="#196f3d"))

    render(os.path.join(OUT, "single-vs-burst-comparison.svg"), W, H, *p)


# ── 2. Апаратний механізм автоінкременту адреси ───────────────────────────────
def fig_autoincrement():
    W, H = 920, 440
    p = []
    p.append(text(W/2, 28, "Апаратна логіка автоінкременту внутрішнього вказівника адреси", size=18, bold=True))
    p.append(text(W/2, 48, "покрокове зміщення покажчика на рівні апаратного декодера шинного інтерфейсу", size=12, color=MUTED, italic=True))

    p.append(rect(40, 75, 230, 330, fill="#f8f9fa", stroke=LINE, sw=1.5, rx=8))
    p.append(text(155, 102, "Шинний інтерфейс (PHY)", size=13, bold=True))
    p.append(text(155, 120, "I2C SDA/SCL або SPI SDI/SCK", size=10.5, color=MUTED))

    p.append(rect(55, 140, 200, 55, fill="#e8f4f8", stroke=NEG, sw=1.2, rx=5))
    p.append(text(155, 162, "Зсувний регістр вводу", size=11, bold=True, color=NEG))
    p.append(text(155, 180, "Прийом стартової адреси", size=9.5, color=MUTED))

    p.append(rect(55, 215, 200, 60, fill="#fef9e7", stroke="#d4ac0d", sw=1.2, rx=5))
    p.append(text(155, 238, "Детектор стробу байта", size=11, bold=True, color="#7d6608"))
    p.append(text(155, 256, "ACK (I2C) / 8-й такт (SPI)", size=9.5, color=MUTED))

    p.append(rect(55, 295, 200, 90, fill="#f5eef8", stroke="#8e44ad", sw=1.2, rx=5))
    p.append(text(155, 318, "Логіка конфігурації", size=11, bold=True, color="#8e44ad"))
    p.append(text(155, 336, "Прапорець IF_INC / MB", size=9.5, color=MUTED))
    p.append(text(155, 354, "1 = Дозволити +1", size=9.5, color=FIELD))
    p.append(text(155, 370, "0 = Залишити адресу", size=9.5, color=POS))

    p.append(rect(320, 110, 240, 260, fill="#edf7ee", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(440, 138, "Вказівник адреси (Address Pointer)", size=13, bold=True, color=FIELD))

    p.append(rect(340, 160, 200, 55, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(440, 182, "Регістр адреси (Pointer Reg)", size=11.5, bold=True))
    p.append(text(440, 201, "Поточне значення: 0x28 → 0x29...", size=10, color=MUTED))

    p.append(rect(360, 245, 160, 50, fill="#e8f8f5", stroke="#16a085", sw=1.3, rx=6))
    p.append(text(440, 268, "Суматор +1 (Adder)", size=11.5, bold=True, color="#117864"))
    p.append(text(440, 284, "ADDR = ADDR + 1", size=10, color=MUTED))

    p.append(rect(340, 315, 200, 42, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    p.append(text(440, 332, "Маска меж блоку / FIFO", size=10, bold=True))
    p.append(text(440, 347, "Запобігання виходу за регістри", size=9.5, color=MUTED))

    p.append(arrow(255, 168, 335, 180, color=NEG, sw=1.8))
    p.append(text(295, 164, "Запис", size=9.5, color=NEG, bold=True))

    p.append(arrow(255, 245, 355, 265, color="#d4ac0d", sw=1.8))
    p.append(text(295, 246, "Строб", size=9.5, color="#7d6608", bold=True))

    p.append(arrow(440, 218, 440, 240, color=FIELD, sw=1.5))
    p.append(arrow(355, 275, 330, 275, color=FIELD, sw=1.5))
    p.append(line(330, 275, 330, 185, color=FIELD, sw=1.5))
    p.append(arrow(330, 185, 335, 185, color=FIELD, sw=1.5))

    p.append(rect(610, 75, 270, 330, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    p.append(text(745, 102, "Карта регістрів давача", size=13, bold=True))

    regs = [
        ("0x28", "OUTX_L_A", "Молодший байт осі X", "#d5f5e3", FIELD),
        ("0x29", "OUTX_H_A", "Старший байт осі X", "#d5f5e3", FIELD),
        ("0x2A", "OUTY_L_A", "Молодший байт осі Y", "#d5f5e3", FIELD),
        ("0x2B", "OUTY_H_A", "Старший байт осі Y", "#d5f5e3", FIELD),
        ("0x2C", "OUTZ_L_A", "Молодший байт осі Z", "#d5f5e3", FIELD),
        ("0x2D", "OUTZ_H_A", "Старший байт осі Z", "#d5f5e3", FIELD),
        ("0x2E", "FIFO_CTRL", "Наступний регістр (вихід)", "#f2f3f4", MUTED),
    ]

    for i, (addr, name, desc, bgc, col) in enumerate(regs):
        ry = 125 + i * 38
        p.append(rect(625, ry, 240, 32, fill=bgc, stroke=col, sw=1, rx=4))
        p.append(text(645, ry+20, addr, size=10, bold=True, color="#b07a00"))
        p.append(text(710, ry+20, name, size=10.5, bold=True, color=col))
        p.append(text(800, ry+20, desc, size=9.5, color=MUTED))

    p.append(arrow(545, 188, 620, 140, color=FIELD, sw=2))
    p.append(text(585, 150, "Декодер", size=9.5, bold=True, color=FIELD))

    render(os.path.join(OUT, "address-pointer-autoincrement.svg"), W, H, *p)


# ── 3. Узгодженість вимірювань і тіньові регістри (BDU) ───────────────────────
def fig_atomic_shadow():
    W, H = 920, 480
    p = []
    p.append(text(W/2, 28, "Узгодженість вимірювань: запобігання розриву слова (Word Tearing)", size=18, bold=True))
    p.append(text(W/2, 48, "як механізм Block Data Update (BDU) та тіньові регістри захищають від спотворення 16-бітних слів", size=12, color=MUTED, italic=True))

    w_box = 405
    p.append(rect(40, 75, w_box, 380, fill="#fdfefe", stroke=POS, sw=1.5, rx=8))
    p.append(text(242, 102, "БЕЗ блокування (BDU = 0)", size=14, bold=True, color=POS))
    p.append(text(242, 120, "ADC оновлює регістри посеред читання", size=10.5, color=MUTED))

    p.append(rect(55, 140, 375, 48, fill="#fadbd8", stroke=POS, sw=1, rx=4))
    p.append(text(75, 160, "Вибірка N:", size=10, bold=True))
    p.append(text(190, 160, "0x00FF (255)", size=11, bold=True, color=INK))
    p.append(text(75, 178, "Вибірка N+1:", size=10, bold=True))
    p.append(text(190, 178, "0x0100 (256)", size=11, bold=True, color=POS))

    p.append(rect(55, 200, 375, 42, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    p.append(text(70, 225, "1. Читання OUTX_L:", size=10.5, anchor="start", bold=True))
    p.append(text(280, 225, "взято 0xFF (з N)", size=10.5, color=NEG, bold=True))

    p.append(rect(55, 252, 375, 38, fill="#fdedec", stroke=POS, sw=1.2, rx=4))
    p.append(text(242, 275, "⚡ ADC завершив перетворення N+1! Регістри перезаписано", size=9.5, color=POS, bold=True))

    p.append(rect(55, 300, 375, 42, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    p.append(text(70, 325, "2. Читання OUTX_H:", size=10.5, anchor="start", bold=True))
    p.append(text(280, 325, "взято 0x01 (з N+1)", size=10.5, color=POS, bold=True))

    p.append(rect(55, 355, 375, 85, fill="#f9ebea", stroke=POS, sw=1.5, rx=6))
    p.append(text(242, 378, "РЕЗУЛЬТАТ ОБ'ЄДНАННЯ:", size=11, bold=True, color=POS))
    p.append(text(242, 400, "(0x01 << 8) | 0xFF = 0x01FF (511 відліків!)", size=12, bold=True, color=POS))
    p.append(text(242, 425, "Фальшивий сплеск на 100% шкали замість плавного 255 → 256", size=9.5, color=MUTED))

    x2 = 475
    p.append(rect(x2, 75, w_box, 380, fill="#fdfefe", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(x2+202, 102, "З ТІНЬОВИМИ РЕГІСТРАМИ (BDU = 1)", size=14, bold=True, color=FIELD))
    p.append(text(x2+202, 120, "Атомарна фіксація вихідного банку", size=10.5, color=MUTED))

    p.append(rect(x2+15, 140, 375, 48, fill="#d5f5e3", stroke=FIELD, sw=1, rx=4))
    p.append(text(x2+35, 160, "Вибірка N:", size=10, bold=True))
    p.append(text(x2+150, 160, "0x00FF (255)", size=11, bold=True, color=FIELD))
    p.append(text(x2+35, 178, "Вибірка N+1:", size=10, bold=True))
    p.append(text(x2+150, 178, "0x0100 (чекає в буфері ADC)", size=10.5, color=MUTED))

    p.append(rect(x2+15, 200, 375, 42, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    p.append(text(x2+30, 225, "1. Читання OUTX_L:", size=10.5, anchor="start", bold=True))
    p.append(text(x2+240, 225, "взято 0xFF (замок активний)", size=10, color=FIELD, bold=True))

    p.append(rect(x2+15, 252, 375, 38, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(x2+202, 275, "🔒 ADC завершив N+1, але вихідні регістри ЗАМОРОЖЕНО", size=9.5, color="#117864", bold=True))

    p.append(rect(x2+15, 300, 375, 42, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    p.append(text(x2+30, 325, "2. Читання OUTX_H:", size=10.5, anchor="start", bold=True))
    p.append(text(x2+240, 325, "взято 0x00 (з тої ж вибірки N)", size=10, color=FIELD, bold=True))

    p.append(rect(x2+15, 355, 375, 85, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(x2+202, 378, "РЕЗУЛЬТАТ ОБ'ЄДНАННЯ:", size=11, bold=True, color=FIELD))
    p.append(text(x2+202, 400, "(0x00 << 8) | 0xFF = 0x00FF (255 відліків)", size=12, bold=True, color=FIELD))
    p.append(text(x2+202, 425, "Ідеальна фізична узгодженість. Замок знімається після читання MSB", size=9.5, color=MUTED))

    render(os.path.join(OUT, "atomic-shadow-latch.svg"), W, H, *p)


# ── 4. Бітові структури команд SPI та I2C ─────────────────────────────────────
def fig_flags():
    W, H = 920, 430
    p = []
    p.append(text(W/2, 28, "Формати байтів адреси та прапорці автоінкременту (SPI / I2C)", size=18, bold=True))
    p.append(text(W/2, 48, "кодування операцій читання/запису та пакетного доступу в різних родинах давачів", size=12, color=MUTED, italic=True))

    y1 = 75
    p.append(rect(40, y1, 840, 95, fill="#fbfcfc", stroke=LINE, sw=1.3, rx=6))
    p.append(text(55, y1+20, "STMicroelectronics (LSM6DSO, LSM6DS3, LIS3DH SPI)", size=12.5, bold=True, anchor="start"))
    
    bw = 48
    bx0 = 240
    st_bits = [
        ("b7", "R/W", "1=Read\n0=Write", POS),
        ("b6", "MS/INC", "1=Auto-Inc\n0=Static", FIELD),
        ("b5", "AD5", "Адреса", INK),
        ("b4", "AD4", "Адреса", INK),
        ("b3", "AD3", "Адреса", INK),
        ("b2", "AD2", "Адреса", INK),
        ("b1", "AD1", "Адреса", INK),
        ("b0", "AD0", "Адреса", INK),
    ]
    for i, (bname, bval, bdesc, bcol) in enumerate(st_bits):
        x = bx0 + i * bw
        p.append(rect(x, y1+32, bw, 36, fill="#ffffff", stroke=bcol, sw=1.2, rx=3))
        p.append(text(x+bw/2, y1+46, bname, size=9.5, color=MUTED))
        p.append(text(x+bw/2, y1+60, bval, size=10, bold=True, color=bcol))

    p.append(text(710, y1+44, "Команда Burst Read:", size=10.5, bold=True, anchor="start"))
    p.append(text(710, y1+62, "0xC0 | RegAddr (LIS3DH)", size=10, color=FIELD, anchor="start"))
    p.append(text(710, y1+78, "0x80 | RegAddr (LSM6DSO)", size=10, color=FIELD, anchor="start"))

    y2 = 185
    p.append(rect(40, y2, 840, 95, fill="#fbfcfc", stroke=LINE, sw=1.3, rx=6))
    p.append(text(55, y2+20, "Bosch Sensortec (BMI270, BME280 SPI)", size=12.5, bold=True, anchor="start"))

    bosch_bits = [
        ("b7", "R/W", "1=Read\n0=Write", POS),
        ("b6", "AD6", "Адреса", INK),
        ("b5", "AD5", "Адреса", INK),
        ("b4", "AD4", "Адреса", INK),
        ("b3", "AD3", "Адреса", INK),
        ("b2", "AD2", "Адреса", INK),
        ("b1", "AD1", "Адреса", INK),
        ("b0", "AD0", "Адреса", INK),
    ]
    for i, (bname, bval, bdesc, bcol) in enumerate(bosch_bits):
        x = bx0 + i * bw
        p.append(rect(x, y2+32, bw, 36, fill="#ffffff", stroke=bcol, sw=1.2, rx=3))
        p.append(text(x+bw/2, y2+46, bname, size=9.5, color=MUTED))
        p.append(text(x+bw/2, y2+60, bval, size=10, bold=True, color=bcol))

    p.append(text(710, y2+44, "Особливість BMI270 SPI:", size=10.5, bold=True, anchor="start"))
    p.append(text(710, y2+62, "Потрібен 1 Dummy-байт", size=10, color=POS, anchor="start"))
    p.append(text(710, y2+78, "перед першим байтом даних", size=9.5, color=MUTED, anchor="start"))

    y3 = 295
    p.append(rect(40, y3, 840, 95, fill="#fbfcfc", stroke=LINE, sw=1.3, rx=6))
    p.append(text(55, y3+20, "Analog Devices (ADXL345 SPI & I2C Sub-Address)", size=12.5, bold=True, anchor="start"))

    adi_bits = [
        ("b7", "R/W", "1=Read\n0=Write", POS),
        ("b6", "MB", "1=Multi-Byte\n0=Single", FIELD),
        ("b5", "AD5", "Адреса", INK),
        ("b4", "AD4", "Адреса", INK),
        ("b3", "AD3", "Адреса", INK),
        ("b2", "AD2", "Адреса", INK),
        ("b1", "AD1", "Адреса", INK),
        ("b0", "AD0", "Адреса", INK),
    ]
    for i, (bname, bval, bdesc, bcol) in enumerate(adi_bits):
        x = bx0 + i * bw
        p.append(rect(x, y3+32, bw, 36, fill="#ffffff", stroke=bcol, sw=1.2, rx=3))
        p.append(text(x+bw/2, y3+46, bname, size=9.5, color=MUTED))
        p.append(text(x+bw/2, y3+60, bval, size=10, bold=True, color=bcol))

    p.append(text(710, y3+44, "Прапорець MB (Multi-Byte):", size=10.5, bold=True, anchor="start"))
    p.append(text(710, y3+62, "MB = 1 активує пакет", size=10, color=FIELD, anchor="start"))
    p.append(text(710, y3+78, "у SPI та I2C субадресах", size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "spi-i2c-burst-flags.svg"), W, H, *p)


# ── 5. Архітектура апаратного зчитування через DMA ─────────────────────────────
def fig_dma():
    W, H = 920, 440
    p = []
    p.append(text(W/2, 28, "Апаратне Burst-зчитування з прямим доступом до пам'яті (DMA)", size=18, bold=True))
    p.append(text(W/2, 48, "автономна перекачка масивів вимірів без завантаження ядра мікроконтролера", size=12, color=MUTED, italic=True))

    p.append(rect(40, 80, 200, 310, fill="#fbfcfc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(140, 110, "Давач (IMU Sensor)", size=13, bold=True))
    p.append(text(140, 128, "LSM6DSO / BMI270", size=10.5, color=MUTED))

    p.append(rect(55, 150, 170, 50, fill="#fdebd0", stroke="#b9770e", sw=1.2, rx=5))
    p.append(text(140, 172, "Лінія INT / DRDY", size=11, bold=True, color="#b9770e"))
    p.append(text(140, 188, "Імпульс готовності даних", size=9.5, color=MUTED))

    p.append(rect(55, 220, 170, 145, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(140, 242, "Регістри виходу (14 B)", size=11, bold=True, color=FIELD))
    p.append(text(140, 260, "0x20: Status", size=9.5, color=MUTED))
    p.append(text(140, 278, "0x28..0x2D: Accel XYZ", size=9.5, color=INK))
    p.append(text(140, 296, "0x22..0x27: Gyro XYZ", size=9.5, color=INK))
    p.append(text(140, 314, "0x30..0x31: Temp", size=9.5, color=MUTED))
    p.append(text(140, 345, "SPI / I2C інтерфейс", size=10, bold=True, color="#117864"))

    p.append(rect(280, 80, 330, 310, fill="#edf7ee", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(445, 108, "Мікроконтролер (STM32 / ESP32)", size=13.5, bold=True, color=FIELD))

    p.append(rect(295, 130, 300, 55, fill="#ffffff", stroke=LINE, sw=1.2, rx=5))
    p.append(text(445, 152, "Периферія SPI / I2C (Shift Reg + FIFO)", size=11, bold=True))
    p.append(text(445, 170, "Апаратна генерація такту SCK / SCL", size=9.5, color=MUTED))

    p.append(rect(295, 205, 300, 160, fill="#ffffff", stroke=FIELD, sw=1.3, rx=6))
    p.append(text(445, 228, "Контролер прямого доступу (DMA Engine)", size=11.5, bold=True, color=FIELD))
    p.append(text(445, 246, "Stream / Channel з апаратним тригером", size=9.5, color=MUTED))

    p.append(rect(310, 260, 270, 42, fill="#e8f8f5", stroke=FIELD, sw=1, rx=4))
    p.append(text(445, 278, "Лічильник передачі (NDTR = 14)", size=10, bold=True, color="#117864"))
    p.append(text(445, 292, "Автоматичне декрементування лічильника", size=9.5, color=MUTED))

    p.append(rect(310, 310, 270, 42, fill="#e8f8f5", stroke=FIELD, sw=1, rx=4))
    p.append(text(445, 328, "Інкремент адреси пам'яті (MINC = 1)", size=10, bold=True, color="#117864"))
    p.append(text(445, 342, "Адреса периферії фіксована (PINC = 0)", size=9.5, color=MUTED))

    p.append(rect(650, 80, 230, 310, fill="#f8f9fa", stroke=LINE, sw=1.5, rx=8))
    p.append(text(765, 108, "Оперативна пам'ять (SRAM)", size=13, bold=True))

    p.append(rect(665, 130, 200, 115, fill="#eaf2f8", stroke=NEG, sw=1.2, rx=5))
    p.append(text(765, 150, "Кільцевий / Подвійний буфер", size=10.5, bold=True, color=NEG))
    p.append(text(765, 170, "Buffer A [14 B] — заповнює DMA", size=9.5, color=FIELD, bold=True))
    p.append(text(765, 190, "Buffer B [14 B] — читає CPU", size=9.5, color=POS, bold=True))
    p.append(text(765, 215, "Transfer Complete (TC) ISR", size=9.5, color=NEG, bold=True))

    p.append(rect(665, 260, 200, 105, fill="#f4f6f7", stroke=LINE, sw=1.2, rx=5))
    p.append(text(765, 282, "Ядро процесора (CPU Core)", size=11, bold=True))
    p.append(text(765, 302, "Завантаження CPU = 0%", size=11, bold=True, color=FIELD))
    p.append(text(765, 322, "Вільний для обчислень", size=9.5, color=MUTED))
    p.append(text(765, 338, "AHRS / Фільтр Калмана", size=9.5, color=MUTED))

    p.append(arrow(225, 175, 290, 175, color="#b9770e", sw=2))
    p.append(text(257, 165, "DRDY", size=9.5, bold=True, color="#b9770e"))

    p.append(arrow(225, 290, 290, 170, color=FIELD, sw=2))
    p.append(text(255, 245, "Burst", size=9.5, bold=True, color=FIELD))

    p.append(arrow(445, 185, 445, 205, color=FIELD, sw=1.8))
    p.append(arrow(595, 285, 665, 185, color=NEG, sw=2))
    p.append(text(630, 225, "DMA Bus", size=9.5, bold=True, color=NEG))

    render(os.path.join(OUT, "dma-burst-pipeline.svg"), W, H, *p)


if __name__ == '__main__':
    fig_comparison()
    fig_autoincrement()
    fig_atomic_shadow()
    fig_flags()
    fig_dma()
    print('Всі 5 фігур згенеровано успішно.')
