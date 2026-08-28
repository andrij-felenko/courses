# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BORDER    = "#bdc3c7"
POLL_CLR  = "#c0392b"  # Червоний / опитування
POLL_BG   = "#fceae8"
ISR_CLR   = "#d35400"  # Помаранчевий / переривання
ISR_BG    = "#fdf2e9"
DMA_CLR   = "#27ae60"  # Зелений / DMA
DMA_BG    = "#eafaf1"
WARN_CLR  = "#b7950b"
WARN_BG   = "#fcf9e8"
BLUE_CLR  = "#2980b9"
BLUE_BG   = "#ebf5fb"
PURP_CLR  = "#8e44ad"
PURP_BG   = "#f4ecf7"
GRID_LINE = "#d5dbdb"


def fig_tradeoff_matrix():
    W, H = 840, 680
    p = []

    # Підзаголовок матриці
    p.append(text(W / 2, 50, "Критерії вибору механізму вводу-виводу для драйвера мікроконтролера", size=11.5, color=MUTED))

    # Стовпці таблиці
    col_w = [180, 200, 200, 200]
    col_x = [30, 210, 410, 610]
    
    # Шапка таблиці
    y_head = 70
    h_head = 40
    p.append(rect(col_x[0], y_head, col_w[0], h_head, fill="#eaeded", stroke=BORDER, sw=1.2, rx=4))
    p.append(text(col_x[0] + col_w[0] / 2, y_head + 25, "Критерій / Властивість", size=11.5, color=INK, bold=True))

    p.append(rect(col_x[1], y_head, col_w[1], h_head, fill=POLL_BG, stroke=POLL_CLR, sw=1.5, rx=4))
    p.append(text(col_x[1] + col_w[1] / 2, y_head + 25, "Polling (Опитування)", size=12, color=POLL_CLR, bold=True))

    p.append(rect(col_x[2], y_head, col_w[2], h_head, fill=ISR_BG, stroke=ISR_CLR, sw=1.5, rx=4))
    p.append(text(col_x[2] + col_w[2] / 2, y_head + 25, "Interrupts (Переривання)", size=12, color=ISR_CLR, bold=True))

    p.append(rect(col_x[3], y_head, col_w[3], h_head, fill=DMA_BG, stroke=DMA_CLR, sw=1.5, rx=4))
    p.append(text(col_x[3] + col_w[3] / 2, y_head + 25, "DMA (Прямий доступ)", size=12, color=DMA_CLR, bold=True))

    rows = [
        (
            "Навантаження CPU\n(CPU Utilization)",
            "100% ядра під час операції.\nЯдро замкнене в циклі\nочікування прапорця.",
            "Пропорційне до потоку:\n20–50 тактів стека на байт.\nШторм при високих швидкостях.",
            "~0% під час передачі.\nОдин вектор переривання\nна блок або півбуфера."
        ),
        (
            "Латентність до\nпершого байта",
            "Мінімальна (<1 мкс),\nякщо опитування активне.\nНульові витрати на контекст.",
            "12–30 тактів NVIC\nплюс латентність конвеєра\nта хвоста переривань.",
            "80–150 тактів налаштування\nканалу, дескрипторів та\nскидання D-Cache."
        ),
        (
            "Оптимальний розмір\nтранзакції (поріг)",
            "1–4 байти\n(короткі статусні регістри,\nініціалізація чипа).",
            "4–64 байти\n(асинхронні події, CLI,\nпоодинокі пакети датчиків).",
            ">64 байти або постійний\nпотік (аудіо, ADC/DAC, SPI flash,\nмережеві кадри)."
        ),
        (
            "Складність коду та\nпідводні камені",
            "Тривіальний лінійний код.\nНемає конкурентності\nта гонок за ресурси.",
            "Кільцеві буфери, атоміки,\nкритичні секції, ризик\nпереповнення буфера (RXNE).",
            "Когерентність D-Cache\n(Clean / Invalidate),\nвирівнювання 32B, MPU."
        ),
        (
            "Енергоефективність\n(Sleep / Standby)",
            "Найгірша: ядро не спить,\nспоживає максимальний\nструм у Run-режимі.",
            "Середня: ядро спить у WFI,\nпрокидається на кожен байт,\nчастий дренаж на стекінг.",
            "Найвища: CPU спить довгими\nінтервалами, DMA автономно\nкачає дані шиною AHB."
        ),
    ]

    y_cur = 120
    row_h = 96
    for idx, (crit, c_poll, c_isr, c_dma) in enumerate(rows):
        # Критерій
        p.append(rect(col_x[0], y_cur, col_w[0], row_h, fill="#f8f9f9", stroke=BORDER, sw=1.0, rx=3))
        p.append(mtext(col_x[0] + col_w[0] / 2, y_cur + row_h / 2 - 10, crit, size=11, color=INK, bold=True))

        # Polling
        p.append(rect(col_x[1], y_cur, col_w[1], row_h, fill="#fffaf9", stroke=BORDER, sw=0.8, rx=3))
        p.append(mtext(col_x[1] + col_w[1] / 2, y_cur + 20, c_poll, size=10, color=INK))

        # ISR
        p.append(rect(col_x[2], y_cur, col_w[2], row_h, fill="#fefdfb", stroke=BORDER, sw=0.8, rx=3))
        p.append(mtext(col_x[2] + col_w[2] / 2, y_cur + 20, c_isr, size=10, color=INK))

        # DMA
        p.append(rect(col_x[3], y_cur, col_w[3], row_h, fill="#f9fdfa", stroke=BORDER, sw=0.8, rx=3))
        p.append(mtext(col_x[3] + col_w[3] / 2, y_cur + 20, c_dma, size=10, color=INK))

        y_cur += row_h + 8

    p.append(text(W / 2, H - 20,
                  "Золоте правило: до 4 байтів — Polling; 4–64 байти — ISR; понад 64 байти або потоковий потік — Circular DMA",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "io-mechanism-tradeoff-matrix.svg"), W, H, *p,
           title="Порівняльна матриця компромісів вводу-виводу")


def fig_dma_double_buffer():
    W, H = 840, 560
    p = []

    p.append(text(W / 2, 50, "Конвеєр паралельного приймання периферією та обробки ядром з обслуговуванням D-Cache", size=11.5, color=MUTED))

    # Блок периферії (UART/SPI RX)
    p.append(rect(40, 80, 160, 70, fill=BLUE_BG, stroke=BLUE_CLR, sw=1.8, rx=6))
    p.append(text(120, 110, "Периферія RX", size=12.5, color=BLUE_CLR, bold=True))
    p.append(text(120, 130, "USART_DR / SPI_DR", size=10.5, color=MUTED))

    # Стрілка від периферії до DMA
    p.append(arrow(200, 115, 270, 115, color=BLUE_CLR, sw=2.0))
    p.append(text(235, 105, "Апаратний запит", size=9.5, color=BLUE_CLR))

    # Блок DMA контролера
    p.append(rect(270, 80, 180, 70, fill=DMA_BG, stroke=DMA_CLR, sw=2.0, rx=6))
    p.append(text(360, 108, "DMA Controller", size=13, color=DMA_CLR, bold=True))
    p.append(text(360, 130, "Circular Mode (NDTR=2N)", size=10.5, color=INK))

    # Стрілка від DMA до пам'яті
    p.append(arrow(450, 115, 520, 115, color=DMA_CLR, sw=2.0))
    p.append(text(485, 105, "AHB Master", size=9.5, color=DMA_CLR))

    # Блок пам'яті SRAM (Кільцевий буфер розділений на дві половини)
    sram_x, sram_y = 520, 75
    p.append(rect(sram_x, sram_y, 280, 120, fill="#fdfefe", stroke=BORDER, sw=1.5, rx=6))
    p.append(text(sram_x + 140, sram_y + 22, "SRAM Buffer (Вирівняно по 32 байти)", size=11, color=INK, bold=True))

    # Буфер A (Half 0)
    buf_a_x, buf_a_y = sram_x + 15, sram_y + 35
    p.append(rect(buf_a_x, buf_a_y, 120, 65, fill="#e8f8f5", stroke=DMA_CLR, sw=1.5, rx=4))
    p.append(text(buf_a_x + 60, buf_a_y + 25, "Буфер A (Half 0)", size=11, color=DMA_CLR, bold=True))
    p.append(text(buf_a_x + 60, buf_a_y + 45, "0 .. N-1 байтів", size=9.5, color=MUTED))

    # Буфер B (Half 1)
    buf_b_x, buf_b_y = sram_x + 145, sram_y + 35
    p.append(rect(buf_b_x, buf_b_y, 120, 65, fill="#fef9e7", stroke=WARN_CLR, sw=1.5, rx=4))
    p.append(text(buf_b_x + 60, buf_b_y + 25, "Буфер B (Half 1)", size=11, color=WARN_CLR, bold=True))
    p.append(text(buf_b_x + 60, buf_b_y + 45, "N .. 2N-1 байтів", size=9.5, color=MUTED))

    # Діаграма часових фаз (Фаза 1 і Фаза 2)
    t_y = 230
    p.append(rect(40, t_y, 760, 140, fill="#fafbfc", stroke=BORDER, sw=1.2, rx=6))
    p.append(text(420, t_y + 22, "Часовий розподіл: DMA та CPU працюють паралельно без простоїв", size=12, color=INK, bold=True))

    # Лінія часу: Фаза 1
    p.append(rect(60, t_y + 40, 340, 40, fill="#e8f8f5", stroke=DMA_CLR, sw=1.5, rx=4))
    p.append(text(230, t_y + 65, "1. DMA наповнює Буфер A", size=11, color=DMA_CLR, bold=True))

    p.append(rect(60, t_y + 85, 340, 40, fill="#f4f6f7", stroke=BORDER, sw=1.0, rx=4))
    p.append(text(230, t_y + 110, "CPU виконує іншу роботу / спить (WFI)", size=10.5, color=MUTED))

    # Подія Half Transfer (HT)
    p.append(line(400, t_y + 35, 400, t_y + 135, color=PURP_CLR, sw=2.0, dash="4,3"))
    p.append(rect(350, t_y + 135, 100, 24, fill=PURP_BG, stroke=PURP_CLR, sw=1.2, rx=3))
    p.append(text(400, t_y + 151, "HTIF Interrupt", size=10, color=PURP_CLR, bold=True))

    # Лінія часу: Фаза 2
    p.append(rect(420, t_y + 40, 360, 40, fill="#fef9e7", stroke=WARN_CLR, sw=1.5, rx=4))
    p.append(text(600, t_y + 65, "2. DMA автономно наповнює Буфер B", size=11, color=WARN_CLR, bold=True))

    p.append(rect(420, t_y + 85, 360, 40, fill="#e8f8f5", stroke=DMA_CLR, sw=1.2, rx=4))
    p.append(text(600, t_y + 103, "CPU інвалідує D-Cache для Буфера A", size=10.5, color=DMA_CLR, bold=True))
    p.append(text(600, t_y + 119, "та обробляє готові дані Half 0", size=10, color=INK))

    # Блок D-Cache Coherency (нижня частина)
    c_y = 400
    p.append(rect(40, c_y, 760, 110, fill=PURP_BG, stroke=PURP_CLR, sw=1.5, rx=6))
    p.append(text(420, c_y + 22, "Обслуговування когерентності D-Cache (Cortex-M7 / SCB Maintenance)", size=12, color=PURP_CLR, bold=True))

    p.append(rect(60, c_y + 38, 340, 58, fill="#ffffff", stroke=PURP_CLR, sw=1.0, rx=4))
    p.append(text(230, c_y + 56, "Приймання (RX): Invalidate", size=11, color=PURP_CLR, bold=True))
    p.append(text(230, c_y + 74, "SCB_InvalidateDCache_by_Addr(BufA, N)", size=9.5, color=INK))
    p.append(text(230, c_y + 88, "Скидає старі копії кешу перед читанням CPU", size=9, color=MUTED))

    p.append(rect(420, c_y + 38, 360, 58, fill="#ffffff", stroke=PURP_CLR, sw=1.0, rx=4))
    p.append(text(600, c_y + 56, "Передача (TX): Clean", size=11, color=PURP_CLR, bold=True))
    p.append(text(600, c_y + 74, "SCB_CleanDCache_by_Addr(BufA, N)", size=9.5, color=INK))
    p.append(text(600, c_y + 88, "Виштовхує брудні рядки з кешу в SRAM перед DMA TX", size=9, color=MUTED))

    p.append(text(W / 2, H - 16,
                  "Подвійна буферизація дозволяє передавати дані безперервно без втрат байтів та блокувань процесора",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "dma-double-buffer-circular-flow.svg"), W, H, *p,
           title="Кільцевий подвійний буфер DMA та D-Cache")


if __name__ == "__main__":
    fig_tradeoff_matrix()
    fig_dma_double_buffer()
    print("Figures generated successfully.")
