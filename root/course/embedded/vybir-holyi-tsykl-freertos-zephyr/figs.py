# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. three-architectures: порівняння трьох архітектурних моделей ────────────
def fig_three_architectures():
    W, H = 840, 360
    p = []

    # Заголовок зверху
    p.append(text(W / 2, 28, "Три підходи до архітектури прошивки мікроконтролера", size=16, color=INK, bold=True))

    col_w = 250
    gap = 25
    y_top = 55
    card_h = 280

    # 1. Super-Loop
    x1 = 30
    p.append(rect(x1, y_top, col_w, card_h, fill="#f8fafc", stroke="#64748b", sw=1.6, rx=8))
    p.append(text(x1 + col_w / 2, y_top + 26, "Голий супер-цикл", size=14, color=INK, bold=True))
    p.append(text(x1 + col_w / 2, y_top + 46, "Super-Loop / Bare-metal", size=11, color=MUTED))

    # Вміст Super-Loop
    p.append(rect(x1 + 15, y_top + 65, col_w - 30, 42, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=5))
    p.append(text(x1 + col_w / 2, y_top + 84, "Обробники переривань", size=11, color=POS, bold=True))
    p.append(text(x1 + col_w / 2, y_top + 98, "ISR (Hardware Timers, UART)", size=9, color=MUTED))

    p.append(arrow(x1 + col_w / 2, y_top + 107, x1 + col_w / 2, y_top + 123, color="#64748b", sw=1.5))

    p.append(rect(x1 + 15, y_top + 125, col_w - 30, 68, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=5))
    p.append(text(x1 + col_w / 2, y_top + 148, "Головний цикл while(1)", size=12, color=FIELD, bold=True))
    p.append(text(x1 + col_w / 2, y_top + 166, "Task A → Task B → Task C", size=10, color=INK))
    p.append(text(x1 + col_w / 2, y_top + 182, "Послідовне опитування (FSM)", size=9, color=MUTED))

    p.append(rect(x1 + 15, y_top + 208, col_w - 30, 58, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(x1 + col_w / 2, y_top + 226, "• RAM: єдиний стек (MSP)", size=10, color=INK))
    p.append(text(x1 + col_w / 2, y_top + 242, "• Flash: 1..8 КБ (мінімум)", size=10, color=INK))
    p.append(text(x1 + col_w / 2, y_top + 258, "• Затримка: L_worst = Σ Cᵢ", size=10, color=POS, bold=True))

    # 2. Classic RTOS (FreeRTOS)
    x2 = x1 + col_w + gap
    p.append(rect(x2, y_top, col_w, card_h, fill="#f0fdf4", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(x2 + col_w / 2, y_top + 26, "Класична RTOS", size=14, color=INK, bold=True))
    p.append(text(x2 + col_w / 2, y_top + 46, "FreeRTOS / embOS", size=11, color=MUTED))

    # Вміст RTOS
    p.append(rect(x2 + 15, y_top + 65, col_w - 30, 36, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(x2 + col_w / 2, y_top + 87, "Планувальник (SysTick/PendSV)", size=10, color=FIELD, bold=True))

    p.append(arrow(x2 + col_w / 2, y_top + 101, x2 + col_w / 2, y_top + 113, color=FIELD, sw=1.5))

    p.append(rect(x2 + 15, y_top + 115, col_w - 30, 78, fill="#ffffff", stroke="#86efac", sw=1.2, rx=5))
    p.append(text(x2 + col_w / 2, y_top + 133, "Ізольовані задачі (PSP)", size=11, color=INK, bold=True))
    p.append(text(x2 + col_w / 2, y_top + 150, "Задача 1 (Пріоритет 3) | Стек 1", size=9, color=NEG))
    p.append(text(x2 + col_w / 2, y_top + 165, "Задача 2 (Пріоритет 2) | Стек 2", size=9, color=FIELD))
    p.append(text(x2 + col_w / 2, y_top + 180, "IPC: М'ютекси, Черги, Семафори", size=9, color=MUTED))

    p.append(rect(x2 + 15, y_top + 208, col_w - 30, 58, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(x2 + col_w / 2, y_top + 226, "• RAM: стек на кожен таск", size=10, color=INK))
    p.append(text(x2 + col_w / 2, y_top + 242, "• Flash: 8..25 КБ", size=10, color=INK))
    p.append(text(x2 + col_w / 2, y_top + 258, "• Затримка: детермінована", size=10, color=FIELD, bold=True))

    # 3. Meta-OS (Zephyr RTOS)
    x3 = x2 + col_w + gap
    p.append(rect(x3, y_top, col_w, card_h, fill="#eff6ff", stroke=NEG, sw=1.6, rx=8))
    p.append(text(x3 + col_w / 2, y_top + 26, "Сучасна Мета-ОС", size=14, color=INK, bold=True))
    p.append(text(x3 + col_w / 2, y_top + 46, "Zephyr RTOS / NuttX", size=11, color=MUTED))

    # Вміст Zephyr
    p.append(rect(x3 + 15, y_top + 65, col_w - 30, 36, fill="#dbeafe", stroke=NEG, sw=1.2, rx=5))
    p.append(text(x3 + col_w / 2, y_top + 82, "DeviceTree + Kconfig", size=10, color=NEG, bold=True))
    p.append(text(x3 + col_w / 2, y_top + 94, "Статична збірка конфігурації", size=9, color=MUTED))

    p.append(arrow(x3 + col_w / 2, y_top + 101, x3 + col_w / 2, y_top + 113, color=NEG, sw=1.5))

    p.append(rect(x3 + 15, y_top + 115, col_w - 30, 78, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=5))
    p.append(text(x3 + col_w / 2, y_top + 133, "Уніфіковані підсистеми", size=11, color=INK, bold=True))
    p.append(text(x3 + col_w / 2, y_top + 150, "BLE, Thread, Wi-Fi, IP, USB", size=9, color=NEG))
    p.append(text(x3 + col_w / 2, y_top + 165, "Драйвери: struct device API", size=9, color=INK))
    p.append(text(x3 + col_w / 2, y_top + 180, "Кросплатформний HAL", size=9, color=MUTED))

    p.append(rect(x3 + 15, y_top + 208, col_w - 30, 58, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(x3 + col_w / 2, y_top + 226, "• RAM: від 16..64+ КБ", size=10, color=INK))
    p.append(text(x3 + col_w / 2, y_top + 242, "• Flash: від 50..250+ КБ", size=10, color=INK))
    p.append(text(x3 + col_w / 2, y_top + 258, "• Time-to-Market: найшвидший", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "three-architectures.svg"), W, H, *p,
           title="Порівняння архітектурних підходів: Super-Loop, FreeRTOS, Zephyr")


# ── 2. task-stack-overhead: порівняння використання RAM ───────────────────────
def fig_task_stack_overhead():
    W, H = 800, 340
    p = []

    p.append(text(W / 2, 26, "Розподіл оперативної пам'яті (SRAM): Super-Loop проти RTOS", size=15, color=INK, bold=True))

    box_w = 340
    box_h = 260
    y_start = 50

    # Ліва колонка: Super-Loop (єдиний стек)
    x1 = 45
    p.append(rect(x1, y_start, box_w, box_h, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    p.append(text(x1 + box_w / 2, y_start + 24, "Super-Loop: Єдиний стек", size=13, color=INK, bold=True))

    # Секції пам'яті в Super-Loop
    sy = y_start + 45
    # Глобальні змінні
    p.append(rect(x1 + 20, sy, box_w - 40, 36, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(x1 + box_w / 2, sy + 22, ".data / .bss (Глобальні змінні)", size=11, color=INK))

    # Динамічна купа (опційно)
    sy += 44
    p.append(rect(x1 + 20, sy, box_w - 40, 30, fill="#f1f5f9", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(x1 + box_w / 2, sy + 19, "Купа (Heap) — часто 0 Б", size=10, color=MUTED))

    # Вільна пам'ять
    sy += 38
    p.append(rect(x1 + 20, sy, box_w - 40, 48, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(x1 + box_w / 2, sy + 22, "Вільна нерозподілена RAM", size=11, color=FIELD, bold=True))
    p.append(text(x1 + box_w / 2, sy + 38, "Спільний простір для пікових сплесків", size=9, color=MUTED))

    # Спільний стек (MSP)
    sy += 56
    p.append(rect(x1 + 20, sy, box_w - 40, 56, fill="#fee2e2", stroke=POS, sw=1.4, rx=4))
    p.append(text(x1 + box_w / 2, sy + 22, "Спільний стек (MSP): 512 Б .. 2 КБ", size=11, color=POS, bold=True))
    p.append(text(x1 + box_w / 2, sy + 40, "Виклики функцій main + обробники ISR", size=9, color=INK))

    # Права колонка: RTOS (ізольовані стеки)
    x2 = 415
    p.append(rect(x2, y_start, box_w, box_h, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(x2 + box_w / 2, y_start + 24, "RTOS: Ізольовані стеки задач", size=13, color=INK, bold=True))

    sy2 = y_start + 45
    # Глобальні змінні
    p.append(rect(x2 + 20, sy2, box_w - 40, 36, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(x2 + box_w / 2, sy2 + 22, ".data / .bss + TCB структури", size=11, color=INK))

    sy2 += 42
    # Стек переривань
    p.append(rect(x2 + 20, sy2, box_w - 40, 30, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(x2 + box_w / 2, sy2 + 19, "Стек переривань (MSP): 512 Б .. 1 КБ", size=10, color=POS))

    sy2 += 36
    # Стек Задачі 1
    p.append(rect(x2 + 20, sy2, box_w - 40, 34, fill="#dbeafe", stroke=NEG, sw=1.2, rx=4))
    p.append(text(x2 + box_w / 2, sy2 + 15, "Стек Задачі 1 (Sensor): 1024 Б (PSP1)", size=10, color=NEG, bold=True))
    p.append(text(x2 + box_w / 2, sy2 + 27, "Використано 300 Б | 724 Б резерв", size=9, color=MUTED))

    sy2 += 38
    # Стек Задачі 2
    p.append(rect(x2 + 20, sy2, box_w - 40, 34, fill="#dbeafe", stroke=NEG, sw=1.2, rx=4))
    p.append(text(x2 + box_w / 2, sy2 + 15, "Стек Задачі 2 (UI/Display): 2048 Б (PSP2)", size=10, color=NEG, bold=True))
    p.append(text(x2 + box_w / 2, sy2 + 27, "Використано 900 Б | 1148 Б резерв", size=9, color=MUTED))

    sy2 += 38
    # Стек Задачі 3
    p.append(rect(x2 + 20, sy2, box_w - 40, 34, fill="#dbeafe", stroke=NEG, sw=1.2, rx=4))
    p.append(text(x2 + box_w / 2, sy2 + 15, "Стек Задачі 3 (Comm/BLE): 2048 Б (PSP3)", size=10, color=NEG, bold=True))
    p.append(text(x2 + box_w / 2, sy2 + 27, "Використано 1200 Б | 848 Б резерв", size=9, color=MUTED))

    # Висновок під правою колонкою
    p.append(text(W / 2, H - 12, "Наклад RTOS: кожен таск заморожує свій worst-case запас RAM, блокуючи пам'ять для інших", size=11, color=POS, italic=True))

    render(os.path.join(OUT, "task-stack-overhead.svg"), W, H, *p,
           title="Порівняння накладу пам'яті: єдиний стек проти ізольованих стеків задач")


# ── 3. decision-tree: дерево вибору архітектурного каркасу ─────────────────────
def fig_decision_tree():
    W, H = 820, 370
    p = []

    p.append(text(W / 2, 24, "Дерево інженерного вибору архітектури прошивки", size=15, color=INK, bold=True))

    # Вузли дерева
    # Корінь
    rx, ry = W / 2, 60
    b1, bw1, bh1 = textbox(rx, ry, "Чи є мережеві стеки (BLE, Thread, Wi-Fi, IP, USB)\nабо вимога легкої зміни чипа між вендорами?",
                           size=11, bold=True, color=INK, fill="#f8fafc", stroke="#64748b", sw=1.5, pad=10)
    p.append(b1)

    # Гілка ТАК (Праворуч) -> Перевірка ресурсів для Zephyr
    zx, zy = 650, 160
    p.append(arrow(rx + bw1 / 4, ry + bh1 / 2, zx, zy - 22, color=NEG, sw=1.6))
    p.append(text(rx + bw1 / 4 + 40, ry + bh1 / 2 + 12, "ТАК", size=10, color=NEG, bold=True))

    b_zcheck, bzw, bzh = textbox(zx, zy, "Пам'ять чіпа:\nFlash ≥ 64-128 КБ,\nRAM ≥ 32-64 КБ?",
                                 size=10, bold=True, color=NEG, fill="#eff6ff", stroke=NEG, sw=1.4, pad=8)
    p.append(b_zcheck)

    # Zephyr результати
    p.append(arrow(zx + 40, zy + bzh / 2, 720, 270, color=FIELD, sw=1.6))
    p.append(text(735, 230, "ТАК", size=10, color=FIELD, bold=True))
    bz_res, _, _ = textbox(720, 295, "ZEPHYR RTOS\nЄдина екосистема,\nDeviceTree, готова мережа",
                           size=10, bold=True, color=FIELD, fill="#f0fdf4", stroke=FIELD, sw=1.6, pad=8)
    p.append(bz_res)

    p.append(arrow(zx - 40, zy + bzh / 2, 570, 270, color=POS, sw=1.6))
    p.append(text(545, 230, "НІ", size=10, color=POS, bold=True))
    bz_fail, _, _ = textbox(570, 295, "FREERTOS + ВЕНДОРСЬКИЙ СТЕК\nРучна інтеграція драйверів\nпід ліміти пам'яті",
                            size=9, bold=True, color=POS, fill="#fff7ed", stroke="#ea580c", sw=1.4, pad=8)
    p.append(bz_fail)

    # Гілка НІ (Ліворуч від кореня) -> Перевірка кількості асинхронних задач та дедлайнів
    lx, ly = 230, 160
    p.append(arrow(rx - bw1 / 4, ry + bh1 / 2, lx, ly - 22, color=INK, sw=1.6))
    p.append(text(rx - bw1 / 4 - 40, ry + bh1 / 2 + 12, "НІ", size=10, color=INK, bold=True))

    b_rtoscheck, blw, blh = textbox(lx, ly, "Чи є важкі асинхронні задачі,\nблокуючий I/O або жорсткі дедлайни\nреального часу (latency < 1-5 мс)?",
                                    size=10, bold=True, color=INK, fill="#f8fafc", stroke="#64748b", sw=1.4, pad=8)
    p.append(b_rtoscheck)

    # RTOS vs Super-Loop результати
    p.append(arrow(lx + 40, ly + blh / 2, 350, 270, color=FIELD, sw=1.6))
    p.append(text(375, 230, "ТАК", size=10, color=FIELD, bold=True))
    br_res, _, _ = textbox(350, 295, "FREERTOS / EMBOS\nВитісняюча багатозадачність,\nдетермінізм, мікросекундний відгук",
                           size=10, bold=True, color=FIELD, fill="#f0fdf4", stroke=FIELD, sw=1.6, pad=8)
    p.append(br_res)

    p.append(arrow(lx - 40, ly + blh / 2, 120, 270, color=POS, sw=1.6))
    p.append(text(95, 230, "НІ", size=10, color=POS, bold=True))
    bs_res, _, _ = textbox(120, 295, "SUPER-LOOP (BARE-METAL)\nМінімальний наклад,\nнуль пам'яті на ОС, простота",
                           size=10, bold=True, color=POS, fill="#fef2f2", stroke=POS, sw=1.6, pad=8)
    p.append(bs_res)

    render(os.path.join(OUT, "decision-tree.svg"), W, H, *p,
           title="Дерево рішень: вибір між Super-Loop, FreeRTOS та Zephyr RTOS")


if __name__ == "__main__":
    fig_three_architectures()
    fig_task_stack_overhead()
    fig_decision_tree()
    print("All figures generated successfully.")
