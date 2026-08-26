# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Colors
C_APP   = "#1a5276"
C_APP_F = "#d6eaf8"
C_LIB   = "#b9770e"
C_LIB_F = "#fdf3d6"
C_SYS   = "#7d3c98"
C_SYS_F = "#f0e6fa"
C_HW    = "#1e8449"
C_HW_F  = "#d5f5e3"
C_WARN  = "#c0392b"
C_WARN_F= "#fdecea"


def fig_printf_retarget_chain():
    W, H = 820, 480
    p = []

    # Title / header banner
    p.append(fitbox(40, 20, 740, 44, "Рівень застосунку: printf(\"T=%d\\r\\n\", val) або std::print",
                    size=13, color=C_APP, fill=C_APP_F, stroke=C_APP, bold=True))

    p.append(arrow(410, 64, 410, 96, color=LINE, sw=1.8))

    # C Standard Library layer
    p.append(rect(40, 96, 740, 74, fill=C_LIB_F, stroke=C_LIB, sw=1.8, rx=6))
    p.append(text(410, 120, "Стандартна бібліотека C (newlib / picolibc / arm-none-eabi-gcc libc)", size=13, color=C_LIB, bold=True))
    p.append(text(410, 148, "Розбір формату: vfprintf() → перетворення чисел, буферизація FILE / _reent", size=11.5, color=INK))

    p.append(arrow(410, 170, 410, 202, color=LINE, sw=1.8))

    # Low-level syscall glue layer
    p.append(rect(40, 202, 740, 74, fill=C_SYS_F, stroke=C_SYS, sw=1.8, rx=6))
    p.append(text(410, 226, "Шар системних заглушок: int _write(int fd, const char *buf, int len)", size=13, color=C_SYS, bold=True))
    p.append(text(410, 254, "Точка перенаправлення (Retargeting): маршрутизація байтів у вибраний апаратний транспорт", size=11.5, color=INK))

    # Arrows branching to 3 transports
    p.append(arrow(170, 276, 170, 318, color=LINE, sw=1.8))
    p.append(arrow(410, 276, 410, 318, color=LINE, sw=1.8))
    p.append(arrow(650, 276, 650, 318, color=LINE, sw=1.8))

    # 3 Transport destinations
    # 1: UART
    p.append(rect(40, 318, 220, 130, fill=C_HW_F, stroke=C_HW, sw=1.8, rx=6))
    p.append(text(150, 344, "Апаратний UART / USART", size=12.5, color=C_HW, bold=True))
    p.append(text(150, 372, "Побайтовий запис у TDR", size=11, color=INK))
    p.append(text(150, 396, "Або DMA кільцевий буфер", size=11, color=INK))
    p.append(text(150, 424, "Вивід на TX піни чіпа", size=10.5, color=MUTED))

    # 2: SWO / ITM
    p.append(rect(300, 318, 220, 130, fill=C_HW_F, stroke=C_HW, sw=1.8, rx=6))
    p.append(text(410, 344, "ARM ITM Trace (SWO)", size=12.5, color=C_HW, bold=True))
    p.append(text(410, 372, "Запис у ITM->PORT[0].u8", size=11, color=INK))
    p.append(text(410, 396, "Апаратний FIFO трасування", size=11, color=INK))
    p.append(text(410, 424, "1 вивід SWO через JTAG/SWD", size=10.5, color=MUTED))

    # 3: SEGGER RTT
    p.append(rect(560, 318, 220, 130, fill=C_HW_F, stroke=C_HW, sw=1.8, rx=6))
    p.append(text(670, 344, "SEGGER RTT (RAM)", size=12.5, color=C_HW, bold=True))
    p.append(text(670, 372, "Запис у кільцевий буфер RAM", size=11, color=INK))
    p.append(text(670, 396, "Асинхронне читання хостом", size=11, color=INK))
    p.append(text(670, 424, "Без додаткових ліній зв'язку", size=10.5, color=MUTED))

    render(os.path.join(OUT, "printf-retarget-chain.svg"), W, H, *p)


def fig_uart_blocking_timeline():
    W, H = 840, 500
    p = []

    # Title area
    p.append(text(420, 30, "Порівняння навантаження CPU: передача 50 байтів логу", size=15, color=INK, bold=True))

    # Timeline 1: Blocking UART 115200
    y1 = 70
    p.append(text(50, y1 + 18, "Блокуючий UART (115200 бод, ~86.8 мкс/байт)", size=12, color=C_WARN, anchor="start", bold=True))
    p.append(rect(50, y1 + 30, 740, 56, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=4))
    
    # 50 bytes * 86.8 us = 4.34 ms
    p.append(rect(50, y1 + 30, 640, 56, fill=C_WARN_F, stroke=C_WARN, sw=1.8, rx=4))
    p.append(text(370, y1 + 54, "Ядро заблоковане в циклі очікування TXE прапорця (~4340 мкс = 4.34 мс)", size=11.5, color=C_WARN, bold=True))
    p.append(text(370, y1 + 74, "Витрачено ~347 200 тактів CPU при 80 МГц — пропущено тайм-слоти та ітерації контуру керування!", size=10.5, color=INK))
    p.append(rect(690, y1 + 30, 100, 56, fill=C_HW_F, stroke=C_HW, sw=1.5, rx=4))
    p.append(text(740, y1 + 62, "Код далі", size=11, color=C_HW, bold=True))

    # Timeline 2: DMA + Ring Buffer
    y2 = 210
    p.append(text(50, y2 + 18, "Асинхронний логер (Кільцевий буфер у RAM + UART DMA)", size=12, color=C_LIB, anchor="start", bold=True))
    p.append(rect(50, y2 + 30, 740, 56, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=4))
    
    # CPU part: 12 us
    p.append(rect(50, y2 + 30, 75, 56, fill=C_APP_F, stroke=C_APP, sw=1.8, rx=4))
    p.append(text(87, y2 + 54, "Запис у FIFO", size=10, color=C_APP, bold=True))
    p.append(text(87, y2 + 72, "~10 мкс", size=9.5, color=INK))

    p.append(rect(125, y2 + 30, 665, 56, fill=C_HW_F, stroke=C_HW, sw=1.5, rx=4))
    p.append(text(457, y2 + 54, "Ядро виконує основну логіку та обробляє переривання без затримок", size=11.5, color=C_HW, bold=True))
    p.append(text(457, y2 + 74, "Контролер DMA паралельно передає байти в регістр UART по шині пам'яті", size=10.5, color=INK))

    # Timeline 3: SEGGER RTT
    y3 = 350
    p.append(text(50, y3 + 18, "SEGGER RTT (Запис у кільцевий буфер SRAM для читання через SWD/JTAG)", size=12, color=C_HW, anchor="start", bold=True))
    p.append(rect(50, y3 + 30, 740, 56, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=4))

    # CPU part: 1 us
    p.append(rect(50, y3 + 30, 45, 56, fill=C_SYS_F, stroke=C_SYS, sw=1.8, rx=4))
    p.append(text(72, y3 + 54, "RAM", size=10, color=C_SYS, bold=True))
    p.append(text(72, y3 + 72, "<1 мкс", size=9.5, color=INK))

    p.append(rect(95, y3 + 30, 695, 56, fill=C_HW_F, stroke=C_HW, sw=1.5, rx=4))
    p.append(text(442, y3 + 54, "Повне звільнення CPU: нульова затримка шини зв'язку", size=11.5, color=C_HW, bold=True))
    p.append(text(442, y3 + 74, "Зонд налагоджувача зчитує дані з RAM у фоновому режимі через шинний міст AHB-AP", size=10.5, color=INK))

    render(os.path.join(OUT, "uart-blocking-timeline.svg"), W, H, *p)


def fig_rtt_memory_structure():
    W, H = 820, 490
    p = []

    p.append(text(410, 26, "Структура керування SEGGER RTT у пам'яті SRAM мікроконтролера", size=14, color=INK, bold=True))

    # Left: MCU SRAM memory block
    p.append(rect(40, 56, 430, 400, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(40, 56, 430, 36, fill=C_SYS_F, stroke=C_SYS, sw=1.5, rx=6))
    p.append(text(255, 80, "SRAM мікроконтролера: Дескриптор SEGGER_RTT_CB", size=12.5, color=C_SYS, bold=True))

    # Structure fields inside SEGGER_RTT_CB
    fields = [
        ("char acID[16]", "\"SEGGER RTT\"  (магічний сигнатурний рядок для пошуку зондом)", C_LIB_F, C_LIB),
        ("int MaxNumUpBuffers", "Кількість висхідних каналів MCU → Host (наприклад, 3)", FILL, LINE),
        ("int MaxNumDownBuffers", "Кількість низхідних каналів Host → MCU (наприклад, 3)", FILL, LINE),
        ("RING_BUFFER aUp[0]", "Конфігурація каналу виводу #0 (\"Terminal\"): ", C_APP_F, C_APP),
    ]

    top_y = 104
    for name, desc, fill_c, strk_c in fields:
        p.append(rect(55, top_y, 400, 42, fill=fill_c, stroke=strk_c, sw=1.2, rx=4))
        p.append(text(65, top_y + 18, name, size=11, color=strk_c, anchor="start", bold=True))
        p.append(text(65, top_y + 34, desc, size=9.5, color=INK, anchor="start"))
        top_y += 48

    # Subfields of aUp[0]
    subfields = [
        ("char* sName", "Вказівник на назву \"Terminal\""),
        ("char* pBuffer", "Вказівник на виділений масив байтів у SRAM"),
        ("unsigned SizeOfBuffer", "Розмір кільцевого буфера (наприклад, 1024 байти)"),
        ("unsigned WrOff", "Зсув запису (ОНОВЛЮЄТЬСЯ МІКРОКОНТРОЛЕРОМ)"),
        ("unsigned RdOff", "Зсув читання (ОНОВЛЮЄТЬСЯ НАЛАГОДЖУВАЧЕМ)"),
        ("unsigned Flags", "Режим: NO_BLOCK_SKIP / NO_BLOCK_TRIM / BLOCK_IF_FIFO_FULL"),
    ]

    p.append(rect(55, top_y, 400, 150, fill="#ffffff", stroke=C_APP, sw=1.2, rx=4))
    sub_y = top_y + 16
    for fn, fd in subfields:
        is_wr = "ОНОВЛЮЄТЬСЯ МІКРОКОНТРОЛЕРОМ" in fd
        is_rd = "ОНОВЛЮЄТЬСЯ НАЛАГОДЖУВАЧЕМ" in fd
        col = C_WARN if is_wr else (C_HW if is_rd else INK)
        p.append(text(65, sub_y, fn + ":", size=10, color=col, anchor="start", bold=(is_wr or is_rd)))
        p.append(text(210, sub_y, fd, size=9.5, color=col, anchor="start"))
        sub_y += 22

    # Right: Host Debugger side
    p.append(rect(510, 56, 270, 400, fill=C_HW_F, stroke=C_HW, sw=1.5, rx=6))
    p.append(rect(510, 56, 270, 36, fill=C_HW, stroke=C_HW, sw=1.5, rx=6))
    p.append(text(645, 80, "Хост-налагоджувач (J-Link / OpenOCD)", size=11.5, color="#ffffff", bold=True))

    p.append(text(645, 120, "Апаратний зонд SWD / JTAG", size=12, color=C_HW, bold=True))
    p.append(text(645, 150, "1. Сканує SRAM на наявність", size=11, color=INK))
    p.append(text(645, 170, "сигнатури \"SEGGER RTT\"", size=11, color=C_LIB, bold=True))
    p.append(text(645, 205, "2. Зчитує адресу буфера", size=11, color=INK))
    p.append(text(645, 225, "та поточні WrOff / RdOff", size=11, color=INK))
    p.append(text(645, 260, "3. Вичитує нові байти логу", size=11, color=INK))
    p.append(text(645, 280, "через фоновий порт AHB-AP", size=11, color=INK))
    p.append(text(645, 315, "4. Записує новий RdOff", size=11, color=C_WARN, bold=True))
    p.append(text(645, 335, "прямо в пам'ять SRAM чіпа", size=11, color=INK))
    p.append(text(645, 380, "Ядро MCU продовжує роботу", size=11.5, color=C_HW, bold=True))
    p.append(text(645, 402, "без жодних пауз і переривань!", size=10.5, color=INK))

    # Connection arrow between SRAM and Probe
    p.append(arrow(510, 240, 455, 240, color=LINE, sw=2))
    p.append(arrow(455, 350, 510, 350, color=C_WARN, sw=2))

    render(os.path.join(OUT, "rtt-memory-structure.svg"), W, H, *p)


if __name__ == "__main__":
    fig_printf_retarget_chain()
    fig_uart_blocking_timeline()
    fig_rtt_memory_structure()
    print("Figures generated successfully.")
