# -*- coding: utf-8 -*-
import sys, os

# 4 рівні вгору від root/eng/sf-devices/hrafichnyi-interfeis до scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори ролей
ARM        = "#1e8449"
ARMF       = "#d5f5e3"
BLUE       = "#1a5276"
BLUEF      = "#d6eaf8"
AMBER      = "#b9770e"
AMBERF     = "#fdf3d6"
VIOLET     = "#7d3c98"
VIOLETF    = "#f0e6fa"
RED        = "#c0392b"
REDF       = "#fadbd8"

CPU_COL    = BLUE
CPU_BG     = BLUEF
DMA_COL    = ARM
DMA_BG     = ARMF
WARN_COL   = AMBER
WARN_BG    = AMBERF
DISP_COL   = VIOLET
DISP_BG    = VIOLETF
FRAME_COL  = RED
FRAME_BG   = REDF


# ── 1. display-buffer-modes: порівняння трьох режимів буферизації ──────────────
def fig_display_buffer_modes():
    W, H = 840, 430
    p = []

    p.append(text(W / 2, 25, "Режими буферизації дисплея в графічному рушії мікроконтролера", size=14, color=INK, bold=True))

    # Режим 1: Одинарний частковий буфер
    y1 = 55
    p.append(rect(30, y1, 780, 105, fill="#fcfcfc", stroke=MUTED, sw=1.2, rx=6))
    p.append(rect(45, y1 + 12, 230, 26, fill=WARN_BG, stroke=WARN_COL, sw=1.4, rx=4))
    p.append(text(160, y1 + 29, "1. Single Partial Buffer (1/10 екрана)", size=11, color=WARN_COL, bold=True))
    p.append(mtext(160, y1 + 58, "SRAM: ~15-30 КБ\nЧергування: CPU малює -> чекає DMA\nНизька швидкість (FPS) через простої CPU", size=9.5, color=INK, lh=1.25))

    # Схема часових інтервалів для Single Buffer
    p.append(rect(300, y1 + 15, 120, 36, fill=CPU_BG, stroke=CPU_COL, sw=1.3, rx=4))
    p.append(text(360, y1 + 37, "CPU: Рендер 1", size=10, color=CPU_COL, bold=True))
    p.append(rect(430, y1 + 15, 120, 36, fill=DMA_BG, stroke=DMA_COL, sw=1.3, rx=4))
    p.append(text(490, y1 + 37, "DMA: Вивід 1", size=10, color=DMA_COL, bold=True))
    p.append(rect(560, y1 + 15, 120, 36, fill=CPU_BG, stroke=CPU_COL, sw=1.3, rx=4))
    p.append(text(620, y1 + 37, "CPU: Рендер 2", size=10, color=CPU_COL, bold=True))
    p.append(rect(690, y1 + 15, 100, 36, fill=DMA_BG, stroke=DMA_COL, sw=1.3, rx=4))
    p.append(text(740, y1 + 37, "DMA: Вивід 2", size=10, color=DMA_COL, bold=True))

    p.append(rect(300, y1 + 62, 490, 28, fill=WARN_BG, stroke=WARN_COL, sw=1.0, rx=3))
    p.append(text(545, y1 + 80, "Послідовне виконання: CPU заблокований під час роботи DMA (FPS падає в 1.8-2 рази)", size=9.5, color=WARN_COL, bold=True))

    # Режим 2: Подвійний частковий буфер (Ping-Pong)
    y2 = 175
    p.append(rect(30, y2, 780, 115, fill="#fcfcfc", stroke=FIELD, sw=1.6, rx=6))
    p.append(rect(45, y2 + 12, 230, 26, fill=DMA_BG, stroke=DMA_COL, sw=1.4, rx=4))
    p.append(text(160, y2 + 29, "2. Double Partial Buffer (Ping-Pong)", size=11, color=DMA_COL, bold=True))
    p.append(mtext(160, y2 + 58, "SRAM: ~30-60 КБ (два буфери в ОЗП)\nПовне перекриття рендерингу й DMA\nОптимальний баланс для MCU без SDRAM", size=9.5, color=INK, lh=1.25))

    # Часова діаграма Ping-Pong
    p.append(rect(300, y2 + 15, 150, 34, fill=CPU_BG, stroke=CPU_COL, sw=1.3, rx=4))
    p.append(text(375, y2 + 36, "CPU: Рендер у Буфер A", size=9.5, color=CPU_COL, bold=True))
    p.append(rect(460, y2 + 15, 150, 34, fill=CPU_BG, stroke=CPU_COL, sw=1.3, rx=4))
    p.append(text(535, y2 + 36, "CPU: Рендер у Буфер B", size=9.5, color=CPU_COL, bold=True))
    p.append(rect(620, y2 + 15, 170, 34, fill=CPU_BG, stroke=CPU_COL, sw=1.3, rx=4))
    p.append(text(705, y2 + 36, "CPU: Рендер у Буфер A", size=9.5, color=CPU_COL, bold=True))

    p.append(rect(460, y2 + 58, 150, 34, fill=DMA_BG, stroke=DMA_COL, sw=1.3, rx=4))
    p.append(text(535, y2 + 79, "DMA: Передача Буфера A", size=9.5, color=DMA_COL, bold=True))
    p.append(rect(620, y2 + 58, 170, 34, fill=DMA_BG, stroke=DMA_COL, sw=1.3, rx=4))
    p.append(text(705, y2 + 79, "DMA: Передача Буфера B", size=9.5, color=DMA_COL, bold=True))

    p.append(text(545, y2 + 106, "Паралельна робота: CPU обчислює наступну смугу, поки DMA спустошує попередню", size=9.5, color=FIELD, bold=True))

    # Режим 3: Повний подвійний фреймбуфер (Full / Direct Mode)
    y3 = 305
    p.append(rect(30, y3, 780, 105, fill="#fcfcfc", stroke=MUTED, sw=1.2, rx=6))
    p.append(rect(45, y3 + 12, 230, 26, fill=FRAME_BG, stroke=FRAME_COL, sw=1.4, rx=4))
    p.append(text(160, y3 + 29, "3. Full Double Buffer / Direct Mode", size=11, color=FRAME_COL, bold=True))
    p.append(mtext(160, y3 + 58, "RAM: 600-1600 КБ (потрібна SDRAM/PSRAM)\nНульовий тиринг при VSYNC-синхронізації\nDirect: малювання лише брудних пікселів", size=9.5, color=INK, lh=1.25))

    p.append(rect(300, y3 + 15, 235, 75, fill=FRAME_BG, stroke=FRAME_COL, sw=1.3, rx=4))
    p.append(text(417, y3 + 36, "Фреймбуфер 1 (Front / Active)", size=10, color=FRAME_COL, bold=True))
    p.append(mtext(417, y3 + 58, "Відображається на дисплеї\nчерез LTDC / паралельну шину", size=9, color=INK, lh=1.2))

    p.append(rect(550, y3 + 15, 240, 75, fill=CPU_BG, stroke=CPU_COL, sw=1.3, rx=4))
    p.append(text(670, y3 + 36, "Фреймбуфер 2 (Back / Draw)", size=10, color=CPU_COL, bold=True))
    p.append(mtext(670, y3 + 58, "CPU / DMA2D малює новий кадр\nСвоп покажчиків по сигналу VSYNC", size=9, color=INK, lh=1.2))

    render(os.path.join(OUT, "display-buffer-modes.svg"), W, H, *p)


# ── 2. rendering-pipeline: конвеєр рендерингу LVGL ────────────────────────────
def fig_rendering_pipeline():
    W, H = 840, 400
    p = []

    p.append(text(W / 2, 25, "Конвеєр формування кадру в LVGL: від інвалідації до передачі через DMA", size=14, color=INK, bold=True))

    steps = [
        ("1. Подія у віджеті", "lv_slider_set_value()\nЗміна стану об'єкта", VIOLETF, VIOLET, 30, 60, 165, 80),
        ("2. Інвалідація", "lv_obj_invalidate()\nДодавання прямокутника", REDF, RED, 230, 60, 175, 80),
        ("3. Оптимізація площ", "Об'єднання брудних зон\n(Dirty Area Joining)", AMBERF, AMBER, 440, 60, 175, 80),
        ("4. Таймер рендерингу", "lv_timer_handler()\nЗапуск перемальовування", BLUEF, BLUE, 650, 60, 160, 80)
    ]

    for title, desc, fill, stroke_col, x, y, w, h in steps:
        p.append(rect(x, y, w, h, fill=fill, stroke=stroke_col, sw=1.5, rx=6))
        p.append(text(x + w / 2, y + 24, title, size=11, color=stroke_col, bold=True))
        p.append(mtext(x + w / 2, y + 46, desc, size=9.5, color=INK, lh=1.25))

    p.append(arrow(195, 100, 230, 100, color=MUTED, sw=1.8))
    p.append(arrow(405, 100, 440, 100, color=MUTED, sw=1.8))
    p.append(arrow(615, 100, 650, 100, color=MUTED, sw=1.8))

    # Стрілка вниз на другий ряд
    p.append(arrow(730, 140, 730, 185, color=MUTED, sw=1.8))

    steps_row2 = [
        ("7. DMA завершено", "lv_disp_flush_ready()\nЗвільнення буфера A", ARMF, ARM, 30, 185, 165, 85),
        ("6. Скидання буфера", "disp_drv.flush_cb()\nСтарт асинхронного DMA", DMA_BG, DMA_COL, 230, 185, 175, 85),
        ("5б. Пошаровий растр", "Фон -> Тінь -> Текст\nОбрізка за lv_area_t", CPU_BG, CPU_COL, 440, 185, 175, 85),
        ("5а. Виділення смуги", "Розбиття брудної зони\nпід розмір буфера SRAM", BLUEF, BLUE, 650, 185, 160, 85)
    ]

    for title, desc, fill, stroke_col, x, y, w, h in steps_row2:
        p.append(rect(x, y, w, h, fill=fill, stroke=stroke_col, sw=1.5, rx=6))
        p.append(text(x + w / 2, y + 24, title, size=11, color=stroke_col, bold=True))
        p.append(mtext(x + w / 2, y + 48, desc, size=9.5, color=INK, lh=1.25))

    p.append(arrow(650, 227, 615, 227, color=MUTED, sw=1.8))
    p.append(arrow(440, 227, 405, 227, color=MUTED, sw=1.8))
    p.append(arrow(230, 227, 195, 227, color=MUTED, sw=1.8))

    # Нижній пояснювальний блок: Ping-Pong зворотний зв'язок
    p.append(rect(30, 295, 780, 85, fill="#fcfcfc", stroke=MUTED, sw=1.3, rx=6))
    p.append(text(W / 2, 318, "Ключовий інваріант конвеєра: сигнал готовності flush_ready", size=11, color=INK, bold=True))
    p.append(mtext(W / 2, 340, "Якщо в черзі є наступні брудні смуги, LVGL негайно починає їх рендеринг у Буфер B, не чекаючи завершення DMA для Буфера A.\nВиклик lv_disp_flush_ready() в обробнику переривання DMA Transfer Complete сигналізує графічному ядру, що Буфер A знову вільний.", size=9.5, color=MUTED, lh=1.3))

    render(os.path.join(OUT, "rendering-pipeline.svg"), W, H, *p)


# ── 3. dma2d-chrom-art: апаратне прискорення DMA2D ────────────────────────────
def fig_dma2d_chrom_art():
    W, H = 840, 420
    p = []

    p.append(text(W / 2, 25, "Апаратний прискорювач 2D-графіки (STM32 Chrom-ART / DMA2D)", size=14, color=INK, bold=True))

    # Три режими DMA2D
    modes = [
        ("Режим 1: Регістр-у-пам'ять (R2M)", "Миттєве заповнення кольором", [
            "DMA2D->CR = DMA2D_R2M",
            "Колір записується в OOR/OMAR",
            "Швидкість: 1 піксель за такт шини",
            "Застосування: очищення фону, прямокутники"
        ], 30, 55, 245, 210, CPU_BG, CPU_COL),
        ("Режим 2: Пам'ять-у-пам'ять (M2M + PFC)", "Конвертація форматів пікселів", [
            "DMA2D->CR = DMA2D_M2M_PFC",
            "Вхід: ARGB8888 з Flash пам'яті",
            "Вихід: RGB565 у буфер дисплея",
            "Застосування: малювання кольорових іконок"
        ], 295, 55, 250, 210, AMBERF, AMBER),
        ("Режим 3: M2M зі змішуванням (Blending)", "Апаратне накладання з альфа-каналом", [
            "DMA2D->CR = DMA2D_M2M_BLEND",
            "FG (іконка) + BG (фон) -> Вихід",
            "Формула: dst = (src*a + dst*(255-a))/255",
            "Застосування: напівпрозорі меню, тіні, anti-aliasing"
        ], 565, 55, 245, 210, ARMF, ARM)
    ]

    for title, subtitle, bullets, x, y, w, h, fill, col in modes:
        p.append(rect(x, y, w, h, fill=fill, stroke=col, sw=1.5, rx=6))
        p.append(text(x + w / 2, y + 24, title, size=10.5, color=col, bold=True))
        p.append(text(x + w / 2, y + 42, subtitle, size=9.5, color=INK, italic=True))
        p.append(line(x + 15, y + 52, x + w - 15, y + 52, color=col, sw=1.0))
        for idx, b in enumerate(bullets):
            by = y + 74 + idx * 30
            p.append(circle(x + 20, by - 4, 3, fill=col, stroke=col, sw=1.0))
            p.append(text(x + 30, by, b, size=9, color=INK, anchor="start"))

    # Нижній блок: Взаємодія CPU, DMA2D та кешу D-Cache
    y_b = 280
    p.append(rect(30, y_b, 780, 120, fill="#fcfcfc", stroke=MUTED, sw=1.3, rx=6))
    p.append(text(W / 2, y_b + 22, "Архітектурна пастка Cortex-M7: узгодженість кешу даних (D-Cache)", size=11, color=RED, bold=True))

    cache_steps = [
        ("1. Рендеринг CPU", "Запис даних у L1 D-Cache\n(брудні рядки в кеші)", CPU_BG, CPU_COL, 50, y_b + 38, 220, 65),
        ("2. Очищення кешу", "SCB_CleanDCache_by_Addr()\nСкидання з кешу в SRAM", WARN_BG, WARN_COL, 310, y_b + 38, 220, 65),
        ("3. Старт DMA2D / DMA", "DMA2D читає узгоджені дані\nбезпосередньо з шини SRAM", DMA_BG, DMA_COL, 570, y_b + 38, 220, 65)
    ]

    for title, desc, fill, col, x, y, w, h in cache_steps:
        p.append(rect(x, y, w, h, fill=fill, stroke=col, sw=1.3, rx=4))
        p.append(text(x + w / 2, y + 22, title, size=10, color=col, bold=True))
        p.append(mtext(x + w / 2, y + 42, desc, size=9, color=INK, lh=1.2))

    p.append(arrow(270, y_b + 70, 310, y_b + 70, color=MUTED, sw=1.8))
    p.append(arrow(530, y_b + 70, 570, y_b + 70, color=MUTED, sw=1.8))

    render(os.path.join(OUT, "dma2d-chrom-art.svg"), W, H, *p)


# ── 4. touch-indev-flow: конвеєр сенсорного вводу ──────────────────────────────
def fig_touch_indev_flow():
    W, H = 840, 390
    p = []

    p.append(text(W / 2, 25, "Конвеєр обробки сенсорного введення (Touch Driver InDev) в LVGL", size=14, color=INK, bold=True))

    steps = [
        ("1. Апаратний давач", "Сенсорний контролер\n(FT6206 / CST816 / GT911)\nПереривання IRQ або I2C", DISP_BG, DISP_COL, 30, 65, 175, 95),
        ("2. Драйвер InDev", "read_cb(indev_drv, data)\nЗчитування сирих (X, Y)\nСтан PR (Pressed) / REL", BLUEF, BLUE, 235, 65, 175, 95),
        ("3. Нормалізація", "Калібрування матриці\nФільтрація шумів (медіана)\nПоворот під орієнтацію", AMBERF, AMBER, 435, 65, 175, 95),
        ("4. Черга подій LVGL", "Генерація LV_EVENT_:\nCLICKED, PRESSING, SCROLL\nДиспетчеризація до віджета", ARMF, ARM, 635, 65, 175, 95)
    ]

    for title, desc, fill, col, x, y, w, h in steps:
        p.append(rect(x, y, w, h, fill=fill, stroke=col, sw=1.5, rx=6))
        p.append(text(x + w / 2, y + 24, title, size=11, color=col, bold=True))
        p.append(mtext(x + w / 2, y + 48, desc, size=9.5, color=INK, lh=1.25))

    p.append(arrow(205, 112, 235, 112, color=MUTED, sw=1.8))
    p.append(arrow(410, 112, 435, 112, color=MUTED, sw=1.8))
    p.append(arrow(610, 112, 635, 112, color=MUTED, sw=1.8))

    # Нижній блок: Машина станів подій сенсора
    y_s = 185
    p.append(rect(30, y_s, 780, 180, fill="#fcfcfc", stroke=MUTED, sw=1.3, rx=6))
    p.append(text(W / 2, y_s + 24, "Машина станів обробника жесту та віджета у фокусі", size=11.5, color=INK, bold=True))

    ev_boxes = [
        ("Дотик (Touch Down)", "LV_INDEV_STATE_PR\nПошук віджета за координатами\nНадсилання LV_EVENT_PRESSED", CPU_BG, CPU_COL, 50, y_s + 45, 220, 80),
        ("Утримання / Рух (Drag)", "Зміна координат (dX, dY)\nПоріг скролу (scroll_limit)\nLV_EVENT_PRESSING / SCROLL", WARN_BG, WARN_COL, 310, y_s + 45, 220, 80),
        ("Відпускання (Touch Up)", "LV_INDEV_STATE_REL\nЯкщо курсор у межах віджета:\nLV_EVENT_CLICKED / SHORT_CLICK", DMA_BG, DMA_COL, 570, y_s + 45, 220, 80)
    ]

    for title, desc, fill, col, x, y, w, h in ev_boxes:
        p.append(rect(x, y, w, h, fill=fill, stroke=col, sw=1.3, rx=4))
        p.append(text(x + w / 2, y + 22, title, size=10, color=col, bold=True))
        p.append(mtext(x + w / 2, y + 44, desc, size=9, color=INK, lh=1.25))

    p.append(arrow(270, y_s + 85, 310, y_s + 85, color=MUTED, sw=1.8))
    p.append(arrow(530, y_s + 85, 570, y_s + 85, color=MUTED, sw=1.8))

    p.append(text(W / 2, y_s + 155, "Період опитування lv_indev_drv_t.read_timer за замовчуванням: 30 мс (~33 Гц) для плавної анімації", size=9.5, color=MUTED, bold=False))

    render(os.path.join(OUT, "touch-indev-flow.svg"), W, H, *p)


if __name__ == "__main__":
    fig_display_buffer_modes()
    fig_rendering_pipeline()
    fig_dma2d_chrom_art()
    fig_touch_indev_flow()
    print("All figures generated successfully.")
