# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_dvp_timings():
    """Часова діаграма сигналів DVP: синхронізація кадру, рядка та піксельні строби."""
    W, H = 960, 480
    parts = [text(W / 2, 28, "Часова діаграма фізичного інтерфейсу DVP (Digital Video Port)", size=17, bold=True)]

    # Фонова панель
    parts.append(rect(20, 50, W - 40, H - 70, fill="#fcfdfe", stroke="#d0d7de", sw=1.2, rx=8))

    # Сигнали: VSYNC, HREF, PCLK, D[7:0]
    sig_names = ["VSYNC (Кадр)", "HREF (Рядок)", "PCLK (Такт)", "D[7:0] (Дані)"]
    sig_ys = [105, 185, 265, 345]

    for name, y in zip(sig_names, sig_ys):
        parts.append(rect(35, y - 22, 135, 40, fill="#eef2f7", stroke="#c2cdd9", sw=1.2, rx=4))
        parts.append(fitbox(40, y - 18, 125, 32, name, size=12, bold=True, color="#1e293b"))

    # Часові рівні
    t_start = 185
    t_end = 920

    # 1. VSYNC: Active High (кадр активний між t_start + 40 та t_end - 40)
    vy = sig_ys[0]
    parts.append(line(t_start, vy + 12, t_start + 30, vy + 12, color=NEG, sw=2))
    parts.append(line(t_start + 30, vy + 12, t_start + 45, vy - 12, color=NEG, sw=2))
    parts.append(line(t_start + 45, vy - 12, t_end - 45, vy - 12, color=NEG, sw=2))
    parts.append(line(t_end - 45, vy - 12, t_end - 30, vy + 12, color=NEG, sw=2))
    parts.append(line(t_end - 30, vy + 12, t_end, vy + 12, color=NEG, sw=2))
    parts.append(fitbox(t_start + 80, vy - 34, 180, 20, "Активний інтервал кадру", size=11, bold=True, fill="none", stroke="none", color=NEG))
    parts.append(fitbox(t_start - 5, vy + 14, 50, 18, "VBLANK", size=10, fill="none", stroke="none", color=MUTED))

    # 2. HREF: Рядок 1, HBLANK, Рядок 2
    hy = sig_ys[1]
    # Line 1: 250..520
    parts.append(line(t_start, hy + 12, t_start + 65, hy + 12, color=FIELD, sw=2))
    parts.append(line(t_start + 65, hy + 12, t_start + 75, hy - 12, color=FIELD, sw=2))
    parts.append(line(t_start + 75, hy - 12, t_start + 370, hy - 12, color=FIELD, sw=2))
    parts.append(line(t_start + 370, hy - 12, t_start + 380, hy + 12, color=FIELD, sw=2))
    # HBLANK: 380..460
    parts.append(line(t_start + 380, hy + 12, t_start + 450, hy + 12, color=FIELD, sw=2))
    # Line 2: 460..750
    parts.append(line(t_start + 450, hy + 12, t_start + 460, hy - 12, color=FIELD, sw=2))
    parts.append(line(t_start + 460, hy - 12, t_start + 710, hy - 12, color=FIELD, sw=2))
    parts.append(line(t_start + 710, hy - 12, t_start + 720, hy + 12, color=FIELD, sw=2))
    parts.append(line(t_start + 720, hy + 12, t_end, hy + 12, color=FIELD, sw=2))

    parts.append(fitbox(t_start + 110, hy - 34, 180, 20, "Рядок 1 (Active Video)", size=11, bold=True, fill="none", stroke="none", color=FIELD))
    parts.append(fitbox(t_start + 382, hy + 14, 66, 18, "HBLANK", size=10, fill="none", stroke="none", color=MUTED))
    parts.append(fitbox(t_start + 490, hy - 34, 180, 20, "Рядок 2 (Active Video)", size=11, bold=True, fill="none", stroke="none", color=FIELD))

    # 3. PCLK: Тактові імпульси (10..50 МГц)
    py = sig_ys[2]
    clk_step = 22
    p_x = t_start + 10
    while p_x + clk_step <= t_end - 10:
        parts.append(line(p_x, py + 12, p_x, py - 12, color="#475569", sw=1.5))
        parts.append(line(p_x, py - 12, p_x + clk_step / 2, py - 12, color="#475569", sw=1.5))
        parts.append(line(p_x + clk_step / 2, py - 12, p_x + clk_step / 2, py + 12, color="#475569", sw=1.5))
        parts.append(line(p_x + clk_step / 2, py + 12, p_x + clk_step, py + 12, color="#475569", sw=1.5))
        p_x += clk_step

    parts.append(fitbox(t_start + 120, py - 34, 220, 20, "PCLK: частота 10–50 МГц (T ≈ 20–100 нс)", size=10.5, bold=True, fill="none", stroke="none", color="#334155"))

    # 4. D[7:0]: Шина даних (шестикутники байтів)
    dy = sig_ys[3]
    # Неактивна зона
    parts.append(line(t_start, dy, t_start + 75, dy, color=MUTED, sw=1.5, dash="3,3"))
    
    # Байти в межах Рядка 1
    byte_x = t_start + 75
    b_idx = 0
    while byte_x + 36 <= t_start + 370:
        bx1 = byte_x
        bx2 = byte_x + 36
        pts = f"{bx1},{dy} {bx1+6},{dy-13} {bx2-6},{dy-13} {bx2},{dy} {bx2-6},{dy+13} {bx1+6},{dy+13}"
        parts.append(f'<polygon points="{pts}" fill="#fef3c7" stroke="#d97706" stroke-width="1.2"/>')
        parts.append(text((bx1 + bx2) / 2, dy + 4, f"B{b_idx}", size=10, bold=True, color="#92400e"))
        byte_x += 36
        b_idx += 1

    # HBLANK пауза
    parts.append(line(byte_x, dy, t_start + 460, dy, color=MUTED, sw=1.5, dash="3,3"))
    parts.append(fitbox(byte_x + 8, dy - 10, 70, 20, "Неактивно", size=9.5, fill="none", stroke="none", color=MUTED))

    # Байти в межах Рядка 2
    byte_x = t_start + 460
    b_idx = 0
    while byte_x + 36 <= t_start + 710:
        bx1 = byte_x
        bx2 = byte_x + 36
        pts = f"{bx1},{dy} {bx1+6},{dy-13} {bx2-6},{dy-13} {bx2},{dy} {bx2-6},{dy+13} {bx1+6},{dy+13}"
        parts.append(f'<polygon points="{pts}" fill="#fef3c7" stroke="#d97706" stroke-width="1.2"/>')
        parts.append(text((bx1 + bx2) / 2, dy + 4, f"B{b_idx}", size=10, bold=True, color="#92400e"))
        byte_x += 36
        b_idx += 1

    # Позначення стробування за фронтом PCLK (t_setup, t_hold)
    sample_x = t_start + 75 + 18
    parts.append(line(sample_x, dy - 20, sample_x, dy + 20, color=POS, sw=1.5, dash="2,2"))
    parts.append(fitbox(sample_x - 70, dy + 22, 140, 28, "Стробування за наростанням PCLK (t_setup, t_hold)", size=9.5, bold=True, fill="#fff1f2", stroke="#f43f5e"))

    # Пояснення знизу
    parts.append(fitbox(35, H - 55, W - 70, 26, "Байт фіксується апаратним DMA-контролером лише тоді, коли HREF = HIGH та VSYNC = HIGH на кожному такті PCLK", size=11, bold=True, fill="#eff6ff", stroke="#93c5fd", color="#1e40af"))

    render(os.path.join(OUT, "fig-dvp-timings.svg"), W, H, *parts)


def fig_sram_vs_psram():
    """Внутрішній SRAM проти зовнішньої PSRAM: архітектура, затримки та шинні конфлікти."""
    W, H = 960, 520
    parts = [text(W / 2, 28, "Внутрішній SRAM проти зовнішньої PSRAM: пропускна здатність і затримки", size=17, bold=True)]

    col_w = 440
    # Колонка 1: Внутрішня SRAM
    x1 = 30
    parts.append(rect(x1, 55, col_w, 310, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(fitbox(x1 + 15, 68, col_w - 30, 32, "Внутрішня SRAM (128–512 КБ)", size=13, bold=True, fill="#e2e8f0", stroke="#94a3b8", color="#0f172a"))

    parts.append(fitbox(x1 + 20, 115, col_w - 40, 48, "• Прямий доступ через 32/64-бітну шину AXI/AHB\n• Затримка доступу: 1 такт процесора (0 wait-states)", size=11, fill="#ffffff", stroke="#e2e8f0"))
    parts.append(fitbox(x1 + 20, 172, col_w - 40, 48, "• DMA пише напряму в RAM без участі CPU\n• Немає конфліктів кешу та затримок витіснення", size=11, fill="#ffffff", stroke="#e2e8f0"))

    # Обмеження SRAM
    parts.append(rect(x1 + 20, 230, col_w - 40, 115, fill="#fef2f2", stroke="#fca5a5", sw=1.2, rx=6))
    parts.append(text(x1 + col_w / 2, 252, "Головний глухий кут внутрішнього SRAM:", size=11.5, bold=True, color=POS))
    parts.append(mtext(x1 + col_w / 2, 276, [
        "VGA 640×480 RGB888 = 921 КБ (НЕ ВМІЩАЄТЬСЯ)",
        "VGA 640×480 RGB565 / YUV = 614 КБ (НЕ ВМІЩАЄТЬСЯ)",
        "Доступний суцільний Heap: лише 180–320 КБ"
    ], size=10.5, color="#991b1b", bold=True))

    # Колонка 2: Зовнішня PSRAM
    x2 = 490
    parts.append(rect(x2, 55, col_w, 310, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(fitbox(x2 + 15, 68, col_w - 30, 32, "Зовнішня PSRAM (Quad / Octal SPI 2–8 МБ)", size=13, bold=True, fill="#e0e7ff", stroke="#a5b4fc", color="#3730a3"))

    parts.append(fitbox(x2 + 20, 115, col_w - 40, 48, "• Величезна ємність: кадр 640×480 або 1600×1200\n• Доступ відображається в адресний простір через MMU", size=11, fill="#ffffff", stroke="#e2e8f0"))
    parts.append(fitbox(x2 + 20, 172, col_w - 40, 48, "• Доступ проходить крізь контролер Flash/PSRAM Cache\n• Потребує періодичного самооновлення (Self-Refresh)", size=11, fill="#ffffff", stroke="#e2e8f0"))

    # Ціна PSRAM
    parts.append(rect(x2 + 20, 230, col_w - 40, 115, fill="#fffbeb", stroke="#fcd34d", sw=1.2, rx=6))
    parts.append(text(x2 + col_w / 2, 252, "Прихована ціна та пастки PSRAM:", size=11.5, bold=True, color="#b45309"))
    parts.append(mtext(x2 + col_w / 2, 276, [
        "Затримка промаху кешу (Cache Miss): 15–40 тактів CPU",
        "Шинні колізії (Bus Contention) між DMA та ядром",
        "Стеля швидкості: QSPI 80 МГц ≈ 40 МБ/с (падає FPS)"
    ], size=10.5, color="#92400e", bold=True))

    # Нижня частина: Порівняння розмірів та вихідне рішення
    by = 385
    parts.append(rect(30, by, W - 60, 115, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    parts.append(text(W / 2, by + 24, "Інженерне вирішення дилеми пам'яті:", size=13, bold=True, color="#166534"))

    # Три порівняльні блоки
    b_w = 270
    # Блок 1: Сирий кадр
    parts.append(rect(50, by + 40, b_w, 60, fill="#ffffff", stroke="#f87171", sw=1.2, rx=4))
    parts.append(text(50 + b_w / 2, by + 60, "Сирий кадр VGA (YUV422)", size=11, bold=True, color="#991b1b"))
    parts.append(text(50 + b_w / 2, by + 82, "614.4 КБ (потребує PSRAM)", size=10.5, color=MUTED))

    # Блок 2: Стиснений JPEG
    parts.append(rect(345, by + 40, b_w, 60, fill="#ffffff", stroke="#4ade80", sw=1.2, rx=4))
    parts.append(text(345 + b_w / 2, by + 60, "Апаратний JPEG на сенсорі", size=11, bold=True, color="#15803d"))
    parts.append(text(345 + b_w / 2, by + 82, "15–40 КБ (вміщається в SRAM)", size=10.5, color="#166534"))

    # Блок 3: Рядковий DMA буфер
    parts.append(rect(640, by + 40, b_w, 60, fill="#ffffff", stroke="#60a5fa", sw=1.2, rx=4))
    parts.append(text(640 + b_w / 2, by + 60, "Потоковий Line/Chunk DMA", size=11, bold=True, color="#1d4ed8"))
    parts.append(text(640 + b_w / 2, by + 82, "2 × 2 КБ = 4 КБ у швидкому SRAM", size=10.5, color="#1e40af"))

    render(os.path.join(OUT, "fig-sram-vs-psram.svg"), W, H, *parts)


def fig_dma_pingpong_chunks():
    """Конвеєрний прийом без суцільного буфера: DMA Ping-Pong і передача чанками."""
    W, H = 960, 520
    parts = [text(W / 2, 28, "Конвеєрний прийом через DMA Ping-Pong та передача чанками", size=17, bold=True)]

    # Фонова панель
    parts.append(rect(20, 50, W - 40, H - 70, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=8))

    # 1. Сенсор зображення ліворуч
    sx = 35
    sy = 110
    parts.append(rect(sx, sy, 160, 260, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(sx + 80, sy + 30, "Сенсор камери", size=13, bold=True, color="#0f172a"))
    parts.append(fitbox(sx + 10, sy + 48, 140, 30, "(OV2640 / OV5640)", size=11, fill="none", stroke="none", color=MUTED))
    parts.append(rect(sx + 12, sy + 90, 136, 60, fill="#fef3c7", stroke="#f59e0b", sw=1.2, rx=4))
    parts.append(fitbox(sx + 15, sy + 96, 130, 48, "Внутрішній ISP +\nJPEG-енкодер", size=10.5, bold=True, fill="none", stroke="none", color="#92400e"))
    parts.append(fitbox(sx + 12, sy + 175, 136, 60, "DVP потік байтів\n(PCLK, HREF, D[7:0])", size=10, fill="#e2e8f0", stroke="#cbd5e1", color="#334155"))

    # Стрілка від сенсора до DMA
    parts.append(arrow(sx + 160, sy + 205, sx + 205, sy + 205, color=LINE, sw=2))
    parts.append(text(sx + 182, sy + 195, "DVP", size=10.5, bold=True, color="#475569"))

    # 2. Контролер DMA та Ping-Pong буфери посередині
    mx = 210
    my = 75
    parts.append(rect(mx, my, 390, 355, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=8))
    parts.append(text(mx + 195, my + 26, "Внутрішня SRAM: DMA Ping-Pong", size=13, bold=True, color="#1e293b"))

    # DMA контролер
    parts.append(rect(mx + 20, my + 42, 350, 42, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=4))
    parts.append(fitbox(mx + 25, my + 46, 340, 34, "Апаратний DMA контролер (DCMI / I2S-CAM)", size=11.5, bold=True, fill="none", stroke="none", color="#0f172a"))

    # Буфер A (Ping)
    parts.append(rect(mx + 20, my + 100, 350, 92, fill="#dbeafe", stroke="#3b82f6", sw=1.5, rx=6))
    parts.append(text(mx + 195, my + 122, "Буфер A (2048 байтів) [DMA ЗАПИС]", size=11.5, bold=True, color="#1d4ed8"))
    parts.append(fitbox(mx + 30, my + 134, 330, 48, "DMA наповнює буфер поточними байтами з DVP.\nПереривання по закінченню дескриптора (EOF).", size=10, fill="#ffffff", stroke="#93c5fd", color="#1e40af"))

    # Буфер B (Pong)
    parts.append(rect(mx + 20, my + 230, 350, 92, fill="#fef9c3", stroke="#eab308", sw=1.5, rx=6))
    parts.append(text(mx + 195, my + 252, "Буфер B (2048 байтів) [CPU ОБРОБКА]", size=11.5, bold=True, color="#a16207"))
    parts.append(fitbox(mx + 30, my + 264, 330, 48, "CPU валідує SOI/EOI маркери, формує заголовок\nпакета й відправляє чанк у мережевий стек.", size=10, fill="#ffffff", stroke="#fde047", color="#854d0e"))

    # Перемикання позначка
    parts.append(rect(mx + 110, my + 198, 170, 24, fill="#fee2e2", stroke="#f87171", sw=1, rx=4))
    parts.append(text(mx + 195, my + 214, "⮂ Перемикання буферів ⮃", size=10, bold=True, color=POS))

    # 3. Мережева передача праворуч
    rx = 645
    ry = 75
    parts.append(rect(rx, ry, 280, 355, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(rx + 140, ry + 26, "Мережевий передавач (UDP / WiFi)", size=12.5, bold=True, color="#0f172a"))

    # Стрілка від буфера B до мережі
    parts.append(arrow(mx + 370, my + 276, rx + 15, ry + 110, color=FIELD, sw=2))

    # Пакети-чанки
    pkt_ys = [ry + 55, ry + 150, ry + 245]
    pkt_labels = ["Пакет 0 (Чанк 0: SOI + дані)", "Пакет 1 (Чанк 1: корисні дані)", "Пакет K (Чанк K: дані + EOI)"]
    pkt_fills = ["#e0f2fe", "#f0fdf4", "#fef2f2"]
    pkt_strokes = ["#38bdf8", "#4ade80", "#f87171"]

    for py, plab, pfill, pstrk in zip(pkt_ys, pkt_labels, pkt_fills, pkt_strokes):
        parts.append(rect(rx + 15, py, 250, 75, fill=pfill, stroke=pstrk, sw=1.2, rx=4))
        parts.append(text(rx + 140, py + 22, plab, size=10.5, bold=True, color="#1e293b"))
        parts.append(fitbox(rx + 25, py + 32, 230, 34, "Заголовок: [Magic|ID|Idx|Len|CRC]\nКорисне навантаження: 1400 Б (MTU)", size=9.5, fill="none", stroke="none", color="#475569"))

    # Підсумок знизу
    parts.append(fitbox(30, H - 60, W - 60, 26, "Повний кадр (25–50 КБ) транслюється частинами: мікроконтролер витрачає лише 4 КБ RAM замість монолітного буфера", size=11, bold=True, fill="#f0fdf4", stroke="#86efac", color="#166534"))

    render(os.path.join(OUT, "fig-dma-pingpong-chunks.svg"), W, H, *parts)


def fig_jpeg_fsm_markers():
    """Скінченний автомат потокового детектора меж JPEG-кадру."""
    W, H = 960, 520
    parts = [text(W / 2, 28, "Скінченний автомат (FSM) розбору потоку JPEG та виявлення маркерів", size=17, bold=True)]

    parts.append(rect(20, 50, W - 40, H - 70, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))

    # Стан 1: IDLE / WAIT_VSYNC
    s1_x, s1_y = 45, 140
    s_w, s_h = 185, 120
    parts.append(rect(s1_x, s1_y, s_w, s_h, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    parts.append(text(s1_x + s_w / 2, s1_y + 24, "IDLE / WAIT_FRAME", size=11.5, bold=True, color="#0f172a"))
    parts.append(fitbox(s1_x + 8, s1_y + 36, s_w - 16, 74, "Очікування старту VSYNC.\nСкидання лічильника байтів.\nІгнорування сміття шини.", size=10, fill="none", stroke="none", color="#475569"))

    # Стан 2: SEARCH_SOI
    s2_x, s2_y = 275, 140
    parts.append(rect(s2_x, s2_y, s_w, s_h, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    parts.append(text(s2_x + s_w / 2, s2_y + 24, "SEARCH_SOI", size=11.5, bold=True, color="#1d4ed8"))
    parts.append(fitbox(s2_x + 8, s2_y + 36, s_w - 16, 74, "Сканування потоку байтів.\nПошук маркера:\n0xFF, 0xD8 (Start of Image).\nВідкидання паддінгу.", size=10, fill="none", stroke="none", color="#1e40af"))

    # Стан 3: STREAM_PAYLOAD
    s3_x, s3_y = 505, 140
    parts.append(rect(s3_x, s3_y, s_w, s_h, fill="#fefce8", stroke="#eab308", sw=1.5, rx=6))
    parts.append(text(s3_x + s_w / 2, s3_y + 24, "STREAM_PAYLOAD", size=11.5, bold=True, color="#a16207"))
    parts.append(fitbox(s3_x + 8, s3_y + 36, s_w - 16, 74, "Запис байтів у чанк-буфер.\nПідрахунок контрольної суми.\nВідправка пакета при 1400 Б.\nПаралельний пошук 0xFF 0xD9.", size=10, fill="none", stroke="none", color="#854d0e"))

    # Стан 4: FRAME_COMPLETE
    s4_x, s4_y = 735, 140
    parts.append(rect(s4_x, s4_y, s_w, s_h, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    parts.append(text(s4_x + s_w / 2, s4_y + 24, "FRAME_COMPLETE", size=11.5, bold=True, color="#15803d"))
    parts.append(fitbox(s4_x + 8, s4_y + 36, s_w - 16, 74, "Знайдено маркер:\n0xFF, 0xD9 (End of Image).\nВідправка фінального чанка\nз прапором LAST_CHUNK.", size=10, fill="none", stroke="none", color="#166534"))

    # Переходи між станами (прямі стрілки згори або посередині)
    # 1 -> 2
    parts.append(arrow(s1_x + s_w, s1_y + 60, s2_x, s1_y + 60, color=LINE, sw=1.8))
    parts.append(text((s1_x + s_w + s2_x) / 2, s1_y + 50, "VSYNC High", size=9.5, bold=True, color="#334155"))

    # 2 -> 3
    parts.append(arrow(s2_x + s_w, s2_y + 60, s3_x, s2_y + 60, color=LINE, sw=1.8))
    parts.append(text((s2_x + s_w + s3_x) / 2, s2_y + 50, "SOI (FF D8)", size=9.5, bold=True, color="#1d4ed8"))

    # 3 -> 4
    parts.append(arrow(s3_x + s_w, s3_y + 60, s4_x, s3_y + 60, color=LINE, sw=1.8))
    parts.append(text((s3_x + s_w + s4_x) / 2, s3_y + 50, "EOI (FF D9)", size=9.5, bold=True, color="#15803d"))

    # Зворотний перехід: 4 -> 1 (початок наступного кадру) знизу
    parts.append(line(s4_x + s_w / 2, s4_y + s_h, s4_x + s_w / 2, s4_y + s_h + 30, color=MUTED, sw=1.5))
    parts.append(line(s4_x + s_w / 2, s4_y + s_h + 30, s1_x + s_w / 2, s1_y + s_h + 30, color=MUTED, sw=1.5))
    parts.append(arrow(s1_x + s_w / 2, s1_y + s_h + 30, s1_x + s_w / 2, s1_y + s_h, color=MUTED, sw=1.5))
    parts.append(fitbox(W / 2 - 130, s1_y + s_h + 18, 260, 24, "Скидання стану перед новим кадром (VSYNC Low)", size=10, bold=True, fill="#ffffff", stroke="#cbd5e1", color=MUTED))

    # Перехід по таймауту / помилці (3 -> 1) згори
    parts.append(line(s3_x + s_w / 2, s3_y, s3_x + s_w / 2, s3_y - 25, color=POS, sw=1.5))
    parts.append(line(s3_x + s_w / 2, s3_y - 25, s1_x + s_w / 2, s1_y - 25, color=POS, sw=1.5))
    parts.append(arrow(s1_x + s_w / 2, s1_y - 25, s1_x + s_w / 2, s1_y, color=POS, sw=1.5))
    parts.append(fitbox(210, s1_y - 37, 280, 24, "Помилка: VSYNC впав до EOI (Drop Frame)", size=9.5, bold=True, fill="#fff1f2", stroke="#fecdd3", color=POS))

    # Нижня панель з маркерами
    by = 365
    parts.append(rect(40, by, W - 80, 105, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6))
    parts.append(text(W / 2, by + 22, "Маркери формату JPEG та їх призначення у потоковому DVP-драйвері:", size=11.5, bold=True, color="#1e293b"))

    parts.append(fitbox(60, by + 36, 260, 56, "0xFF 0xD8 (SOI — Start of Image)\nПочаток корисного тіла кадру.\nВсе до цього маркера є сміттям.", size=10, fill="#eff6ff", stroke="#bfdbfe", color="#1e40af"))
    parts.append(fitbox(350, by + 36, 260, 56, "0xFF 0x00 (Byte Stuffing у JPEG)\nЕкранування байта 0xFF всередині\nентропійного потоку Хаффмана.", size=10, fill="#fefce8", stroke="#fef08a", color="#854d0e"))
    parts.append(fitbox(640, by + 36, 260, 56, "0xFF 0xD9 (EOI — End of Image)\nКінець кадру. Сенсор може далі\nгнати нулі або 0xFF до VSYNC Low.", size=10, fill="#f0fdf4", stroke="#bbf7d0", color="#166534"))

    render(os.path.join(OUT, "fig-jpeg-fsm-markers.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_dvp_timings()
    fig_sram_vs_psram()
    fig_dma_pingpong_chunks()
    fig_jpeg_fsm_markers()
    print("All figures generated successfully.")
