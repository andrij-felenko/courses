# -*- coding: utf-8 -*-
"""Фігури для статті vrazlyvist-u-chuzhomu-chypi-iakyi-ty-ne-mozhesh.
Згенеровані через svgkit зі scripts/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_silicon_blast_radius():
    """Анатомія нелагоджуваної апаратної вразливості та ешелони компенсаційного захисту."""
    W, H = 840, 480
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 28, "Ешелони компенсаційного захисту від кремнієвих вразливостей", size=16, color=INK, bold=True))

    # Ліва колонка — Незмінний кремній
    p.append(rect(30, 55, 250, 395, fill="#fdf2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(155, 84, "Незмінний кремній (Чіп)", size=14, color=POS, bold=True))

    silicon_items = [
        ("Масковий BootROM", "Зашитий на фабриці фотошаблоном", 115),
        ("Вразливий USB DFU / UART", "Помилка парсингу або переповнення", 185),
        ("Апаратні криптоакселератори", "Витік побічним каналом / збої", 255),
        ("Регістри захисту від читання", "Вразливість до глітчингу напруги", 325),
    ]

    for title, desc, y in silicon_items:
        p.append(rect(45, y, 220, 56, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
        p.append(text(155, y + 22, title, size=11, color=POS, bold=True))
        p.append(text(155, y + 42, desc, size=9, color=MUTED))

    p.append(text(155, 415, "Неможливо оновити в полі", size=10, color=POS, bold=True))

    # Стрілка атаки / пробою
    p.append(arrow(280, 250, 325, 250, color=POS, sw=2.5))
    p.append(text(302, 235, "Загроза", size=10, color=POS, bold=True))

    # Права колонка — Компенсаційні ешелони
    p.append(rect(330, 55, 480, 395, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(570, 84, "Системні ешелони компенсаційного захисту", size=14, color=FIELD, bold=True))

    echelons = [
        ("Ешелон 1: Схемотехніка та друкована плата (PCB)",
         "Спалювання eFuse, апаратне глушіння BOOT-пінів, заливка компаундом, зовнішній Secure Element (ATECC608)",
         "#ffffff", FIELD, 115),
        ("Ешелон 2: Вторинний завантажувач (SBL) та бар'єри MPU",
         "Ізоляція пам'яті через MPU, заборона DMA до секретних зон, вимкнення вразливих периферійних модулів",
         "#ffffff", "#1d6fa5", 200),
        ("Ешелон 3: Програмне загартування коду (Fault Hardening)",
         "Багатозначні маски станів, надлишкові перевірки умов, рандомізація затримок проти глітчингу",
         "#ffffff", "#7e22ce", 285),
        ("Ешелон 4: Нульова довіра між чіпами (Zero-Trust Bus)",
         "Шифрування та HMAC міжпроцесорних шин SPI/UART, жорсткий ліміт глибини парсерів повідомлень",
         "#ffffff", "#b45309", 370),
    ]

    for title, desc, fcol, scol, y in echelons:
        p.append(rect(345, y, 450, 68, fill=fcol, stroke=scol, sw=1.4, rx=6))
        p.append(text(570, y + 24, title, size=11, color=scol, bold=True))
        p.append(fitbox(355, y + 34, 430, 26, desc, size=10, pad=2, fill="none", stroke="none", color=INK))

    render(os.path.join(OUT, "silicon-vulnerability-blast-radius.svg"), W, H, *p)


def fig_mpu_bus_isolation():
    """Ізоляція системної шини та пам'яті за допомогою MPU."""
    W, H = 840, 480
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 28, "Ізоляція адресного простору та шини через апаратний MPU", size=16, color=INK, bold=True))

    # Ліва частина — Процесорні режими
    p.append(rect(30, 60, 210, 390, fill="#f8fafc", stroke="#475569", sw=1.5, rx=8))
    p.append(text(135, 90, "Ядро Cortex-M", size=13, color="#1e293b", bold=True))

    p.append(rect(45, 120, 180, 80, fill="#e0f2fe", stroke="#0284c7", sw=1.4, rx=6))
    p.append(text(135, 150, "Привілейований режим", size=11, color="#0369a1", bold=True))
    p.append(text(135, 175, "(SBL / Ядро ОС)", size=10, color=MUTED))

    p.append(rect(45, 230, 180, 80, fill="#fef3c7", stroke="#d97706", sw=1.4, rx=6))
    p.append(text(135, 260, "Непривілейований режим", size=11, color="#b45309", bold=True))
    p.append(text(135, 285, "(Користувацький код)", size=10, color=MUTED))

    p.append(rect(45, 340, 180, 80, fill="#fee2e2", stroke=POS, sw=1.4, rx=6))
    p.append(text(135, 370, "Контролер DMA", size=11, color=POS, bold=True))
    p.append(text(135, 395, "(Потенційний обхід MPU)", size=10, color=POS))

    # Центральний блок — MPU / Bus Matrix
    p.append(rect(270, 60, 160, 390, fill="#ecfdf5", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(350, 95, "MPU & Bus Matrix", size=13, color=FIELD, bold=True))
    p.append(text(350, 120, "Фільтрація доступу", size=10, color=MUTED))

    # Стрілки від ядра до MPU
    p.append(arrow(225, 160, 270, 160, color="#0284c7", sw=1.8))
    p.append(arrow(225, 270, 270, 270, color="#d97706", sw=1.8))
    p.append(arrow(225, 380, 270, 380, color=POS, sw=1.8))

    # Права частина — Регіони пам'яті та рівні доступу
    regions = [
        ("Регіон 0: Вектори та код SBL (Flash)", "Привілейований: RO (Лише читання) | Користувач: Немає доступу", "#f0fdf4", FIELD, 70),
        ("Регіон 1: Секретні ключі та стек безпеки (SRAM)", "Привілейований: RW | Користувач: Немає доступу | DMA: Заблоковано", "#fef2f2", POS, 165),
        ("Регіон 2: Пам'ять застосунку та буфери", "Привілейований: RW | Користувач: RW | Виконання заборонено (XN)", "#f0f9ff", "#0284c7", 260),
        ("Регіон 3: Периферія та вразливий BootROM", "Доступ лише з SBL | Виконання з ROM заборонено після старту", "#fffbeb", "#d97706", 355),
    ]

    for title, desc, fcol, scol, y in regions:
        p.append(rect(460, y, 350, 75, fill=fcol, stroke=scol, sw=1.4, rx=6))
        p.append(text(635, y + 25, title, size=11, color=scol, bold=True))
        p.append(fitbox(470, y + 36, 330, 32, desc, size=9, pad=2, fill="none", stroke="none", color=INK))
        p.append(arrow(430, y + 37, 460, y + 37, color=scol, sw=1.5))

    render(os.path.join(OUT, "mpu-bus-isolation-barrier.svg"), W, H, *p)


def fig_glitch_mitigation():
    """Порівняння звичайного та загартованого від збоїв алгоритму перевірки."""
    W, H = 840, 480
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 28, "Програмне загартування логіки проти збійних атак (Fault Injection)", size=16, color=INK, bold=True))

    # Ліва колонка — Вразливий код
    p.append(rect(30, 60, 360, 390, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(210, 90, "Вразлива лінійна перевірка", size=13, color=POS, bold=True))

    left_steps = [
        ("bool ok = verify_signature();", 120),
        ("if (ok == true) {", 195),
        ("    boot_application();", 270),
        ("} else { panic(); }", 345),
    ]

    for code_str, y in left_steps:
        p.append(rect(50, y, 220, 42, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
        p.append(text(160, y + 26, code_str, size=10, color=INK))

    p.append(arrow(160, 162, 160, 195, color=POS, sw=1.5))
    p.append(arrow(160, 237, 160, 270, color=POS, sw=1.5))
    p.append(arrow(160, 312, 160, 345, color=POS, sw=1.5))

    # Пояснення атаки праворуч у лівому блоці
    p.append(rect(280, 200, 100, 105, fill="#fee2e2", stroke=POS, sw=1.2, rx=6))
    p.append(text(330, 228, "Апаратний глітч", size=10, color=POS, bold=True))
    p.append(text(330, 252, "Пропуск CBZ / BNE", size=9, color=POS))
    p.append(text(330, 275, "або заміна опкоду", size=9, color=POS))
    p.append(arrow(280, 215, 270, 215, color=POS, sw=1.5))

    p.append(text(210, 425, "Один імпульс напруги пропускає перевірку", size=10, color=POS, bold=True))

    # Права колонка — Загартована перевірка
    p.append(rect(450, 60, 360, 390, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(630, 90, "Загартована дуальна перевірка", size=13, color=FIELD, bold=True))

    right_steps = [
        ("uint32_t s1 = verify_stage_1();", 115),
        ("random_delay(); // Джитер тактування", 175),
        ("uint32_t s2 = verify_stage_2();", 235),
        ("if ((s1 == 0x5AA5) && (s2 == 0xA55A)) {", 295),
        ("    boot_application();", 355),
    ]

    for code_str, y in right_steps:
        p.append(rect(470, y, 320, 38, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
        p.append(text(630, y + 24, code_str, size=10, color=INK))

    p.append(arrow(630, 153, 630, 175, color=FIELD, sw=1.4))
    p.append(arrow(630, 213, 630, 235, color=FIELD, sw=1.4))
    p.append(arrow(630, 273, 630, 295, color=FIELD, sw=1.4))
    p.append(arrow(630, 333, 630, 355, color=FIELD, sw=1.4))

    p.append(text(630, 425, "Багатобітові константи + перевірка інваріанта", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "glitch-mitigation-flow.svg"), W, H, *p)


if __name__ == "__main__":
    fig_silicon_blast_radius()
    fig_mpu_bus_isolation()
    fig_glitch_mitigation()
    print("Figures generated successfully.")
