# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра
VEC = "#8e24aa"      # векторний блок / фіолетовий
VECBG = "#f3e5f5"
VECST = "#ba68c8"

SRAM = "#1565c0"     # SRAM / синій
SRAMBG = "#e3f2fd"
SRAMST = "#64b5f6"

PSRAM = "#d84315"    # PSRAM / оранжево-червоний
PSRAMBG = "#fbe9e7"
PSRAMST = "#ff8a65"

DMA_COL = "#2e7d32"  # DMA / зелений
DMABG = "#e8f5e9"
DMAST = "#81c784"


def fig_vector_pipeline():
    W, H = 880, 520
    p = []

    # Тло головного процесорного ядра Xtensa LX7
    p.append(rect(30, 40, 820, 430, fill="#fafafa", stroke=INK, sw=2, rx=12))
    p.append(text(210, 68, "Ядро Xtensa LX7 (до 240 МГц) — Векторне розширення PIE", size=14, color=INK, bold=True))

    # Блок 1: Інструкційний конвеєр та декодер
    p.append(fitbox(50, 95, 230, 80, "Конвеєр вибірки та декодування\n• Dual-Issue розпаралелювання\n• Автоінкремент вказівників (IP)\n• Декодування 128-біт SIMD", size=11, fill=FILL, stroke=LINE, sw=1.5, bold=True))

    # Блок 2: Векторний регістровий файл 8 × 128 біт (q0–q7)
    p.append(rect(320, 95, 250, 160, fill=VECBG, stroke=VECST, sw=1.8, rx=8))
    p.append(text(445, 118, "Векторні регістри q0–q7", size=12.5, color=VEC, bold=True))
    p.append(fitbox(335, 130, 220, 32, "q0: [b15|b14|...|b1|b0]  (128 біт)", size=10.5, fill=BG, stroke=VECST, sw=1.2))
    p.append(fitbox(335, 168, 220, 32, "q1: [w7 |w6 |...|w1|w0]  (128 біт)", size=10.5, fill=BG, stroke=VECST, sw=1.2))
    p.append(fitbox(335, 206, 220, 38, "... q7: 8/16-бітні упаковані вектори\nабо 16 × 64-бітних підрегістрів", size=10, fill=BG, stroke=VECST, sw=1.2))

    # Блок 3: Векторні АЛП та паралельні помножувачі SIMD MAC
    p.append(rect(600, 95, 230, 160, fill="#fff3e0", stroke="#ffb74d", sw=1.8, rx=8))
    p.append(text(715, 118, "SIMD MAC та АЛП (1 такт)", size=12, color="#e65100", bold=True))
    p.append(fitbox(615, 130, 200, 34, "8 × (int8 × int8) → int32\nабо 4 × (int16 × int16) → int32", size=10, fill=BG, stroke="#ffb74d", sw=1.2, bold=True))
    p.append(fitbox(615, 170, 200, 34, "Векторні логічні зсуви,\nквантування, ReLU, Max/Min", size=10, fill=BG, stroke="#ffb74d", sw=1.2))
    p.append(fitbox(615, 210, 200, 34, "Акумулятори SAR / ACCX\n(32-бітні та 40-бітні суматори)", size=10, fill=BG, stroke="#ffb74d", sw=1.2))

    # Блок 4: Пам'ять та шини зв'язку 128 біт
    p.append(rect(50, 290, 780, 160, fill=SRAMBG, stroke=SRAMST, sw=1.8, rx=8))
    p.append(text(180, 314, "Шинний інтерфейс і внутрішня SRAM (512 КБ)", size=13, color=SRAM, bold=True))

    p.append(fitbox(70, 330, 210, 105, "128-бітне завантаження:\nEE.LD.128.USAR.IP\n• 16 байтів за 1 такт\n• вирівнювання 16 байт\n• нульовий овергед кроку", size=10.5, fill=BG, stroke=SRAMST, sw=1.4))

    p.append(fitbox(310, 330, 240, 105, "Внутрішній пул тензорів (SRAM):\n• Тензор активацій входу/виходу\n• Scratchpad для проміжних шарів\n• Без затримок кеш-промахів (1 такт)", size=10.5, fill=BG, stroke=SRAMST, sw=1.4))

    p.append(fitbox(580, 330, 230, 105, "Поєднані інструкції MAC+LD:\nEE.VMULA.S8.ACCX.LD.IP\n• Одночасне множення вектора\nта завантаження наступного блоку\n• Максимальне насичення конвеєра", size=10.5, fill=BG, stroke=SRAMST, sw=1.4))

    # Стрілки та зв'язки
    p.append(arrow(280, 135, 320, 135, color=LINE, sw=2))
    p.append(arrow(570, 150, 600, 150, color=LINE, sw=2))
    p.append(arrow(165, 175, 165, 290, color=LINE, sw=1.8))
    p.append(arrow(445, 290, 445, 255, color=VEC, sw=2.2))
    p.append(arrow(715, 255, 715, 290, color=FIELD, sw=2))

    p.append(text(W / 2, 495, "Векторне розширення Xtensa LX7: паралельне виконання 8 операцій MAC за 1 такт через 128-бітні регістри q0–q7", size=11.5, color=INK, italic=True, bold=True))

    render(os.path.join(OUT, "esp32s3-vector-pipeline.svg"), W, H, *p,
           title="Архітектура векторного конвеєра ESP32-S3")


def fig_memory_hierarchy():
    W, H = 880, 520
    p = []

    # Верхній рівень: Ядра процесора та L1 кеш
    p.append(rect(40, 30, 800, 100, fill="#fdfefe", stroke=INK, sw=2, rx=10))
    p.append(text(440, 52, "Двоядерний Xtensa LX7 (Ядро 0 / Ядро 1) — Обчислювальний рівень", size=13, color=INK, bold=True))
    p.append(fitbox(60, 64, 350, 54, "Ядро 0: 32 КБ L1 I-Cache + 32/64 КБ D-Cache\nПрямий доступ до SRAM за 1 такт (~4.16 нс)", size=10.5, fill=FILL, stroke=LINE, sw=1.2))
    p.append(fitbox(470, 64, 350, 54, "Ядро 1: 32 КБ L1 I-Cache + 32/64 КБ D-Cache\nПаралельний інференс або мережевий стек", size=10.5, fill=FILL, stroke=LINE, sw=1.2))

    # Середній рівень: Внутрішня SRAM 512 КБ
    p.append(rect(40, 160, 800, 165, fill=SRAMBG, stroke=SRAMST, sw=2, rx=10))
    p.append(text(190, 184, "Внутрішня SRAM (512 КБ) — Швидка оперативна пам'ять", size=13, color=SRAM, bold=True))

    p.append(fitbox(60, 196, 235, 115, "Тензори активацій (Tensor Arena):\n• Вхідні/вихідні матриці шарів\n• Робочі scratchpad-буфери\n• Повністю в SRAM (без stall-затримок)", size=10, fill=BG, stroke=SRAMST, sw=1.4))

    p.append(fitbox(315, 196, 250, 115, "Подвійна буферизація ваг (Ping-Pong):\n• Буфер A: розрахунок шару N (SIMD)\n• Буфер B: DMA-підкачування шару N+1\n• Перемикання без простою процесора", size=10, fill=BG, stroke=DMA_COL, sw=1.6, bold=True))

    p.append(fitbox(585, 196, 235, 115, "Критичні ваги моделі:\n• Ваги 1×1 згорток і перших шарів\n• Таблиці квантування (LUT)\n• Векторні дескриптори", size=10, fill=BG, stroke=SRAMST, sw=1.4))

    # Нижній рівень: Зовнішня Octal PSRAM та Flash
    p.append(rect(40, 360, 800, 115, fill=PSRAMBG, stroke=PSRAMST, sw=2, rx=10))
    p.append(text(210, 384, "Зовнішня Octal PSRAM (до 8 МБ / 16 МБ) та Octal SPI Flash", size=13, color=PSRAM, bold=True))

    p.append(fitbox(60, 396, 360, 68, "Зберігання великих моделей (TFLite FlatBuffers, ESP-DL):\n• Ваги згорткових і повнозв'язних шарів (мегабайти)\n• Швидкість шини OPI: DDR 80/120 МГц (~400–800 МБ/с)", size=10, fill=BG, stroke=PSRAMST, sw=1.3))

    p.append(fitbox(460, 396, 360, 68, "Контролер GDMA (General DMA):\n• Фонове перенесення блоків ваг PSRAM → SRAM\n• Повне приховування латентності повільної шини", size=10, fill=DMABG, stroke=DMAST, sw=1.5, bold=True, color=DMA_COL))

    # Сполучні шини та стрілки (тільки у проміжках між блоками)
    p.append(arrow(175, 130, 175, 160, color=SRAM, sw=2.2))
    p.append(arrow(645, 130, 645, 160, color=SRAM, sw=2.2))
    p.append(arrow(440, 160, 440, 130, color=VEC, sw=2.2))
    p.append(arrow(640, 360, 640, 325, color=DMA_COL, sw=2.4))
    p.append(arrow(440, 360, 440, 325, color=DMA_COL, sw=2.4))

    p.append(text(W / 2, 498, "Ієрархія пам'яті: внутрішня SRAM для швидких активацій та фонове DMA-завантаження ваг із зовнішньої Octal PSRAM", size=11.5, color=INK, italic=True, bold=True))

    render(os.path.join(OUT, "esp32s3-ai-memory-hierarchy.svg"), W, H, *p,
           title="Ієрархія пам'яті та розміщення тензорів в ESP32-S3")


if __name__ == "__main__":
    fig_vector_pipeline()
    fig_memory_hierarchy()
    print("SVG figures generated successfully.")
