# -*- coding: utf-8 -*-
"""Генератор схем для теми 'Скільки коштує відео: мегапікселі, стиснення, пам'ять, живлення'."""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fig_bandwidth_hierarchy():
    """Фігура 1: Ієрархія пропускної здатності та трафік шини пам'яті (1080p30)."""
    w, h = 880, 480
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        f'<rect width="{w}" height="{h}" fill="{BG}"/>',
    ]

    # Заголовок
    svg.append(text(w / 2, 28, "Трафік відеотракту 1080p @ 30 fps: пікселі, шина DDR та радіоканал", size=16, bold=True))

    # Сенсор (зліва)
    svg.append(rect(30, 60, 200, 100, rx=6, fill=FILL, stroke=LINE, sw=1.5))
    svg.append(text(130, 85, "Сенсор CMOS (Bayer)", size=13, bold=True))
    svg.append(text(130, 108, "1920×1080 @ 30 fps", size=11, color=MUTED))
    svg.append(text(130, 128, "10-bit RAW = 78 МБ/с", size=12, color=POS, bold=True))
    svg.append(text(130, 145, "(622 Мбіт/с по MIPI CSI-2)", size=10, color=MUTED))

    # Стрілка Sensor -> ISP
    svg.append(arrow(230, 110, 310, 110, color=LINE, sw=2))
    svg.append(text(270, 98, "MIPI CSI", size=10, color=MUTED))

    # ISP блок
    svg.append(rect(310, 60, 220, 100, rx=6, fill=FILL, stroke=LINE, sw=1.5))
    svg.append(text(420, 85, "Апаратний ISP", size=13, bold=True))
    svg.append(text(420, 108, "Демозаїка + Гама + 3DNR", size=11, color=MUTED))
    svg.append(text(420, 128, "Вихід YUV420: 93 МБ/с", size=12, color=POS, bold=True))
    svg.append(text(420, 145, "(подвійна буферизація DMA)", size=10, color=MUTED))

    # Шина DDR (По центру знизу)
    svg.append(rect(150, 210, 580, 110, rx=8, fill="#edf2f7", stroke=LINE, sw=2))
    svg.append(text(440, 235, "Системна шина DRAM (AXI Bus / LPDDR3/4)", size=14, bold=True))
    svg.append(text(440, 258, "Сумарний трафік пам'яті: ~465–620 МБ/с (3.7–5.0 Гбіт/с)", size=13, color=POS, bold=True))
    svg.append(text(440, 280, "• ISP DMA Write: 93 МБ/с   • VPU Input Read: 93 МБ/с", size=11, color=INK))
    svg.append(text(440, 298, "• Референсні кадри DPB (Read/Write): 186–340 МБ/с   • Bitstream Write: 1 МБ/с", size=11, color=INK))

    # Стрілки між ISP/VPU та DRAM
    svg.append(arrow(420, 160, 420, 210, color=LINE, sw=2))
    svg.append(text(445, 185, "Запис YUV", size=10, color=MUTED, anchor="start"))

    svg.append(arrow(630, 210, 630, 160, color=LINE, sw=2))
    svg.append(text(655, 185, "Зчитування YUV", size=10, color=MUTED, anchor="start"))

    # VPU кодер (справа вгорі)
    svg.append(rect(570, 60, 220, 100, rx=6, fill=FILL, stroke=LINE, sw=1.5))
    svg.append(text(680, 85, "Апаратний кодек VPU", size=13, bold=True))
    svg.append(text(680, 108, "H.264 / H.265 (AVC/HEVC)", size=11, color=MUTED))
    svg.append(text(680, 128, "Стиснення: 50×–150×", size=12, color=FIELD, bold=True))
    svg.append(text(680, 145, "Вихідний потік: 2–6 Мбіт/с", size=10, color=MUTED))

    # Стрілка VPU -> Мережа / Картка
    svg.append(arrow(680, 320, 680, 370, color=LINE, sw=2))
    svg.append(text(705, 345, "Бітстрім", size=10, color=MUTED, anchor="start"))

    # Блок виходу (Знизу)
    svg.append(rect(200, 370, 480, 85, rx=6, fill="#eafaf1", stroke=FIELD, sw=1.5))
    svg.append(text(440, 395, "Фінальний вихід: Мережа (Wi-Fi / LTE) або Flash SD", size=13, bold=True, color=FIELD))
    svg.append(text(440, 418, "Бітрейт потоку: ~4 Мбіт/с (0.5 МБ/с) проти 78 МБ/с сирого Bayer", size=12, color=INK))
    svg.append(text(440, 438, "Множник внутрішнього трафіку шини: майже 1000× відносно радіоефіру!", size=11, color=POS, bold=True))

    svg.append("</svg>")
    with open(os.path.join(OUTPUT_DIR, "bandwidth-hierarchy.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def fig_mcu_vs_soc_pipeline():
    """Фігура 2: Порівняння Cortex-M7 та Linux SoC з апаратним VPU."""
    w, h = 880, 460
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        f'<rect width="{w}" height="{h}" fill="{BG}"/>',
    ]

    svg.append(text(w / 2, 28, "Обчислювальний бар'єр відеотракту: Cortex-M проти Linux SoC з VPU", size=16, bold=True))

    # Ліва колонка: Cortex-M7
    svg.append(rect(30, 60, 390, 370, rx=8, fill="#fdf2e9", stroke=POS, sw=1.5))
    svg.append(text(225, 90, "Мікроконтролер (Cortex-M7 @ 480 МГц)", size=14, bold=True, color=POS))

    svg.append(rect(50, 110, 350, 65, rx=4, fill=BG, stroke=LINE, sw=1))
    svg.append(text(225, 132, "Пам'ять: 512 КБ – 1 МБ внутрішнього SRAM", size=11, bold=True))
    svg.append(text(225, 152, "1 кадр 1080p YUV420 = 3.11 МБ → Не влазить навіть 1 кадр!", size=10, color=POS))

    svg.append(rect(50, 185, 350, 75, rx=4, fill=BG, stroke=LINE, sw=1))
    svg.append(text(225, 207, "Обчислення: Програмний H.264 на ядрі CPU", size=11, bold=True))
    svg.append(text(225, 227, "Пошук руху вимагає 6–30 млрд оп/с (GOPS)", size=10, color=INK))
    svg.append(text(225, 245, "Процесор має лише ~1 GOPS → Навантаження 100%, швидкість < 1 fps", size=10, color=POS, bold=True))

    svg.append(rect(50, 270, 350, 65, rx=4, fill=BG, stroke=LINE, sw=1))
    svg.append(text(225, 292, "Шина: Зовнішня PSRAM / OctoSPI (100–200 МБ/с)", size=11, bold=True))
    svg.append(text(225, 312, "Вузька шина душиться DMA-трафіком камери", size=10, color=POS))

    svg.append(rect(50, 345, 350, 65, rx=4, fill="#fbeee6", stroke=POS, sw=1))
    svg.append(text(225, 370, "Реальна межа Cortex-M:", size=11, bold=True, color=POS))
    svg.append(text(225, 392, "Лише MJPEG (QVGA/VGA @ 15 fps) або сирий знімок раз на секунду", size=10, color=INK))

    # Права колонка: Linux SoC з VPU
    svg.append(rect(460, 60, 390, 370, rx=8, fill="#eafaf1", stroke=FIELD, sw=1.5))
    svg.append(text(655, 90, "SoC для камер (Allwinner V853 / RV1106)", size=14, bold=True, color=FIELD))

    svg.append(rect(480, 110, 350, 65, rx=4, fill=BG, stroke=LINE, sw=1))
    svg.append(text(655, 132, "Пам'ять: 64–512 МБ вбудованої DDR2/DDR3 (SiP)", size=11, bold=True))
    svg.append(text(655, 152, "Пропускна здатність 1.6–3.2 ГБ/с → Вільний буфер DPB", size=10, color=FIELD))

    svg.append(rect(480, 185, 350, 75, rx=4, fill=BG, stroke=LINE, sw=1))
    svg.append(text(655, 207, "Апаратний VPU/ISP (Спеціалізований ASIC)", size=11, bold=True))
    svg.append(text(655, 227, "Кодування H.264/H.265 у кремнієвому конвеєрі", size=10, color=INK))
    svg.append(text(655, 245, "Швидкість 1080p @ 30 fps при завантаженні CPU < 5 %", size=10, color=FIELD, bold=True))

    svg.append(rect(480, 270, 350, 65, rx=4, fill=BG, stroke=LINE, sw=1))
    svg.append(text(655, 292, "Штучний інтелект: Вбудований NPU (0.5–1 TOPS)", size=11, bold=True))
    svg.append(text(655, 312, "Локальна детекція об'єктів (YOLO) за 15–25 мс", size=10, color=FIELD))

    svg.append(rect(480, 345, 350, 65, rx=4, fill="#d5f5e3", stroke=FIELD, sw=1))
    svg.append(text(655, 370, "Результат SoC:", size=11, bold=True, color=FIELD))
    svg.append(text(655, 392, "Повноцінне потокове Full HD/4K відео + аналітика при 1–2 Вт", size=10, color=INK))

    svg.append("</svg>")
    with open(os.path.join(OUTPUT_DIR, "mcu-vs-soc-pipeline.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def fig_power_breakdown():
    """Фігура 3: Енергетичний баланс відеопідсистеми (День проти Ночі з ІЧ-підсвічуванням)."""
    w, h = 880, 440
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        f'<rect width="{w}" height="{h}" fill="{BG}"/>',
    ]

    svg.append(text(w / 2, 28, "Енергетичний бюджет IP-камери: Денний режим проти Нічного з ІЧ-підсвіткою", size=16, bold=True))

    # Стовпчик 1: День
    svg.append(rect(80, 70, 320, 330, rx=8, fill=FILL, stroke=LINE, sw=1.5))
    svg.append(text(240, 98, "Денний режим (Разом: ~2.1 Вт)", size=14, bold=True, color=INK))

    # Блоки споживання День
    # Wi-Fi TX: 1100 мВт
    svg.append(rect(100, 120, 280, 90, rx=4, fill="#f9e79f", stroke="#d4ac0d", sw=1.2))
    svg.append(text(240, 150, "Радіоканал Wi-Fi (TX 4 Мбіт/с)", size=12, bold=True))
    svg.append(text(240, 172, "1100 мВт (52 % бюджету)", size=13, color=POS, bold=True))
    svg.append(text(240, 192, "Робота підсилювача потужності PA", size=10, color=MUTED))

    # SoC/VPU: 800 мВт
    svg.append(rect(100, 220, 280, 80, rx=4, fill="#d6eaf8", stroke="#2e86c1", sw=1.2))
    svg.append(text(240, 248, "SoC + ISP + VPU кодування", size=12, bold=True))
    svg.append(text(240, 270, "800 мВт (38 % бюджету)", size=13, color=NEG, bold=True))

    # Sensor: 200 мВт
    svg.append(rect(100, 310, 280, 70, rx=4, fill="#d5f5e3", stroke=FIELD, sw=1.2))
    svg.append(text(240, 336, "Матриця камери (CMOS Sensor)", size=12, bold=True))
    svg.append(text(240, 356, "200 мВт (10 % бюджету)", size=13, color=FIELD, bold=True))

    # Стовпчик 2: Ніч
    svg.append(rect(480, 70, 320, 330, rx=8, fill="#fbeee6", stroke=POS, sw=1.5))
    svg.append(text(640, 98, "Нічний режим з ІЧ (Разом: ~5.6 Вт)", size=14, bold=True, color=POS))

    # ІЧ-підсвічування: 3500 мВт
    svg.append(rect(500, 120, 280, 120, rx=4, fill="#f5b7b1", stroke=POS, sw=1.5))
    svg.append(text(640, 150, "ІЧ-підсвічування сцени (IR LED)", size=13, bold=True, color=POS))
    svg.append(text(640, 175, "3500 мВт (63 % всього бюджету!)", size=14, color=POS, bold=True))
    svg.append(text(640, 198, "ККД світлодіода 30 % → 1.0 Вт оптичної сили", size=10, color=INK))
    svg.append(text(640, 218, "вимагає 3.5 Вт електричної потужності", size=10, color=INK))

    # Wi-Fi TX: 1100 мВт
    svg.append(rect(500, 250, 280, 50, rx=4, fill="#f9e79f", stroke="#d4ac0d", sw=1))
    svg.append(text(640, 272, "Радіоканал Wi-Fi: 1100 мВт (20 %)", size=11, bold=True))

    # SoC + Sensor: 1000 мВт
    svg.append(rect(500, 310, 280, 70, rx=4, fill="#d6eaf8", stroke="#2e86c1", sw=1))
    svg.append(text(640, 335, "SoC (VPU) + Сенсор камери", size=11, bold=True))
    svg.append(text(640, 355, "1000 мВт (17 % бюджету)", size=12, color=NEG, bold=True))

    svg.append("</svg>")
    with open(os.path.join(OUTPUT_DIR, "power-breakdown.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def fig_edge_ai_vs_cloud():
    """Фігура 4: Порівняння архітектур: Edge AI проти безперервного хмарного стрімінгу."""
    w, h = 880, 450
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        f'<rect width="{w}" height="{h}" fill="{BG}"/>',
    ]

    svg.append(text(w / 2, 28, "Архітектурний компроміс: Безперервний стрім проти локального Edge AI", size=16, bold=True))

    # Верхній блок: Хмарний стрімінг
    svg.append(rect(30, 55, 820, 175, rx=8, fill="#fdf2e9", stroke=POS, sw=1.5))
    svg.append(text(60, 82, "1. Постійний стрім у хмару (Cloud Streaming Camera)", size=13, bold=True, color=POS, anchor="start"))

    svg.append(rect(50, 100, 220, 70, rx=4, fill=BG, stroke=LINE, sw=1))
    svg.append(text(160, 122, "Камера + Кодер H.264", size=11, bold=True))
    svg.append(text(160, 142, "Працює 24/7 безперервно", size=10, color=MUTED))
    svg.append(text(160, 158, "Потужність SoC: 800 мВт", size=10, color=INK))

    svg.append(arrow(270, 135, 340, 135, color=POS, sw=2))
    svg.append(text(305, 123, "2–6 Мбіт/с", size=10, color=POS))

    svg.append(rect(340, 100, 220, 70, rx=4, fill=BG, stroke=LINE, sw=1))
    svg.append(text(450, 122, "Радіопередавач (Wi-Fi / 4G)", size=11, bold=True))
    svg.append(text(450, 142, "TX передавач увімкнений 100 % часу", size=10, color=POS, bold=True))
    svg.append(text(450, 158, "Потужність радіо: 1200–2500 мВт", size=10, color=INK))

    svg.append(arrow(560, 135, 630, 135, color=POS, sw=2))
    svg.append(text(595, 123, "Трафік", size=10, color=POS))

    svg.append(rect(630, 100, 200, 70, rx=4, fill="#fbeee6", stroke=POS, sw=1))
    svg.append(text(730, 122, "Хмара / Сервер", size=11, bold=True))
    svg.append(text(730, 142, "Трафік: 650–1900 ГБ/міс", size=10, color=POS, bold=True))
    svg.append(text(730, 158, "Батарея 10 А·год: ~15 годин", size=10, color=POS, bold=True))

    svg.append(text(440, 205, "Середня потужність системи: ~2.5–3.5 Вт • Висока вартість серверів і трафіку", size=11, color=POS, bold=True))

    # Нижній блок: Edge AI
    svg.append(rect(30, 245, 820, 185, rx=8, fill="#eafaf1", stroke=FIELD, sw=1.5))
    svg.append(text(60, 272, "2. Локальне розпізнавання на борту (Edge AI Event Camera)", size=13, bold=True, color=FIELD, anchor="start"))

    svg.append(rect(50, 290, 220, 75, rx=4, fill=BG, stroke=LINE, sw=1))
    svg.append(text(160, 312, "Черговий режим (PIR / 1 fps)", size=11, bold=True))
    svg.append(text(160, 332, "Сон 99 % часу: 15–30 мВт", size=10, color=FIELD, bold=True))
    svg.append(text(160, 350, "Пробудження лише на подію", size=10, color=MUTED))

    svg.append(arrow(270, 327, 340, 327, color=FIELD, sw=2))
    svg.append(text(305, 315, "Тригер", size=10, color=FIELD))

    svg.append(rect(340, 290, 220, 75, rx=4, fill=BG, stroke=LINE, sw=1))
    svg.append(text(450, 312, "Нейромережа NPU на борту", size=11, bold=True))
    svg.append(text(450, 332, "Інференс YOLO: 20 мс @ 1.2 Вт", size=10, color=FIELD))
    svg.append(text(450, 350, "Фільтрація хибних тривог", size=10, color=MUTED))

    svg.append(arrow(560, 327, 630, 327, color=FIELD, sw=2))
    svg.append(text(595, 315, "Подія!", size=10, color=FIELD))

    svg.append(rect(630, 290, 200, 75, rx=4, fill="#d5f5e3", stroke=FIELD, sw=1))
    svg.append(text(730, 312, "Короткий радіоімпульс", size=11, bold=True))
    svg.append(text(730, 332, "Пакет JSON 250 Б + кадр", size=10, color=FIELD, bold=True))
    svg.append(text(730, 350, "Батарея 10 А·год: 30–90 ДНІВ", size=10, color=FIELD, bold=True))

    svg.append(text(440, 405, "Середня потужність системи: ~45–80 мВт • Радіоефір увімкнений < 0.5 % часу", size=11, color=FIELD, bold=True))

    svg.append("</svg>")
    with open(os.path.join(OUTPUT_DIR, "edge-ai-vs-cloud.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


if __name__ == "__main__":
    fig_bandwidth_hierarchy()
    fig_mcu_vs_soc_pipeline()
    fig_power_breakdown()
    fig_edge_ai_vs_cloud()
    print("Усі фігури згенеровано успішно в", OUTPUT_DIR)
