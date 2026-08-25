#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-ілюстрацій для теми debouncing-throttling.
Використовує бібліотеку svgkit з кореня репозиторію.
"""

import os
import sys

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. timing-debounce-modes.svg: Часові діаграми дебаунсу
# ─────────────────────────────────────────────────────────────────────────────
def make_debounce_timing():
    W, H = 1000, 470
    f = []

    # Заголовок / фонова сітка
    f.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))
    f.append(text(W / 2, 35, "Режими дебаунсу (Debouncing): trailing, leading та maxWait", size=15, bold=True))

    # Вісь часу
    t_start_x = 220
    t_end_x = 940
    f.append(line(t_start_x, 430, t_end_x, 430, color="#555555", sw=1.5))
    f.append(arrow(t_end_x - 10, 430, t_end_x + 20, 430, color="#555555", sw=1.5))
    f.append(text(t_end_x + 25, 434, "Час (t)", size=12, anchor="start", color="#555555"))

    # Поділки часу
    time_ticks = [
        (250, "0 мс"), (370, "200 мс"), (490, "400 мс"),
        (610, "600 мс"), (730, "800 мс"), (850, "1000 мс")
    ]
    for tx, lbl in time_ticks:
        f.append(line(tx, 60, tx, 425, color="#f0f2f5", sw=1, dash="4,4"))
        f.append(line(tx, 427, tx, 433, color="#888888", sw=1))
        f.append(text(tx, 448, lbl, size=11, color="#777777"))

    # Рядки
    rows = [
        {"y": 90,  "title": "Вхідні події (Events)", "desc": "Потік імпульсів вводу"},
        {"y": 175, "title": "Trailing Debounce", "desc": "Виклик після затишшя delay"},
        {"y": 260, "title": "Leading Debounce", "desc": "Виклик негайно на старті"},
        {"y": 345, "title": "Debounce + maxWait", "desc": "Гарантований виклик при спалаху"}
    ]

    for r in rows:
        ry = r["y"]
        f.append(rect(20, ry - 18, 185, 54, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
        f.append(text(112, ry + 2, r["title"], size=12, bold=True, color=INK))
        f.append(text(112, ry + 22, r["desc"], size=10, color=MUTED))
        f.append(line(t_start_x, ry + 10, t_end_x, ry + 10, color="#cbd5e1", sw=1.2))

    # 1. Події: Серія 1 (швидкі натискання: t=260, 290, 320, 350) -> пауза -> Подія 2 (t=580) -> Події 3 (безперервні: 680, 720, 760, 800, 840, 880)
    burst1 = [260, 290, 320, 350]
    single = [540]
    burst2 = [680, 715, 750, 785, 820, 855]

    all_events = burst1 + single + burst2
    for ev_x in all_events:
        f.append(line(ev_x, 100, ev_x, 70, color=NEG, sw=2))
        f.append(circle(ev_x, 70, 4, fill=NEG, stroke="#ffffff", sw=1))

    # Візуалізація таймерів delay = 100px (≈160мс)
    delay_px = 90

    # 2. Trailing Debounce
    # Після burst1: остання подія на 350 -> виклик на 350 + 90 = 440
    f.append(rect(350, 185 - 12, delay_px, 14, fill="#e0f2fe", stroke="#7dd3fc", sw=1, rx=2))
    f.append(text(350 + delay_px / 2, 185 - 1, "вікно delay", size=9, color="#0369a1"))
    f.append(arrow(350, 185, 440, 185, color="#0284c7", sw=1.5))
    f.append(circle(440, 185, 6, fill=FIELD, stroke="#ffffff", sw=1.5))
    f.append(text(440, 207, "Виклик 1", size=11, bold=True, color=FIELD))

    # Після single (540) -> виклик на 540 + 90 = 630
    f.append(rect(540, 185 - 12, delay_px, 14, fill="#e0f2fe", stroke="#7dd3fc", sw=1, rx=2))
    f.append(text(540 + delay_px / 2, 185 - 1, "вікно delay", size=9, color="#0369a1"))
    f.append(circle(630, 185, 6, fill=FIELD, stroke="#ffffff", sw=1.5))
    f.append(text(630, 207, "Виклик 2", size=11, bold=True, color=FIELD))

    # Після burst2: остання на 855 -> виклик на 855 + 90 = 945 (відкладався весь час!)
    f.append(rect(855, 185 - 12, 70, 14, fill="#fee2e2", stroke="#fca5a5", sw=1, rx=2))
    f.append(text(890, 185 - 1, "відкладання...", size=9, color=POS))
    f.append(text(780, 207, "голодування (не викликається)", size=10, italic=True, color=POS))

    # 3. Leading Debounce (Immediate)
    # На burst1: виклик на 260 негайно! Потім вікно тиші до 350+90 = 440
    f.append(circle(260, 270, 6, fill=POS, stroke="#ffffff", sw=1.5))
    f.append(text(260, 292, "Виклик 1", size=11, bold=True, color=POS))
    f.append(rect(260, 270 - 12, 180, 14, fill="#fef3c7", stroke="#fcd34d", sw=1, rx=2))
    f.append(text(350, 270 - 1, "блокування повторів до затишшя", size=9, color="#b45309"))

    # На single (540): виклик на 540 негайно!
    f.append(circle(540, 270, 6, fill=POS, stroke="#ffffff", sw=1.5))
    f.append(text(540, 292, "Виклик 2", size=11, bold=True, color=POS))
    f.append(rect(540, 270 - 12, delay_px, 14, fill="#fef3c7", stroke="#fcd34d", sw=1, rx=2))
    f.append(text(540 + delay_px / 2, 270 - 1, "блокування", size=9, color="#b45309"))

    # На burst2: виклик на 680 негайно! Потім тиша
    f.append(circle(680, 270, 6, fill=POS, stroke="#ffffff", sw=1.5))
    f.append(text(680, 292, "Виклик 3", size=11, bold=True, color=POS))
    f.append(rect(680, 270 - 12, 240, 14, fill="#fef3c7", stroke="#fcd34d", sw=1, rx=2))
    f.append(text(800, 270 - 1, "блокування до паузи", size=9, color="#b45309"))

    # 4. Debounce + maxWait (maxWait = 130px)
    max_wait_px = 125
    # burst1: виклик trailing на 440 (закінчився раніше maxWait)
    f.append(circle(440, 355, 6, fill=FIELD, stroke="#ffffff", sw=1.5))
    f.append(text(440, 377, "Виклик 1 (trailing)", size=10, bold=True, color=FIELD))

    # single: виклик на 630
    f.append(circle(630, 355, 6, fill=FIELD, stroke="#ffffff", sw=1.5))
    f.append(text(630, 377, "Виклик 2", size=10, bold=True, color=FIELD))

    # burst2: старт на 680 -> maxWait спрацьовує на 680 + 125 = 805 примусово!
    f.append(rect(680, 355 - 12, max_wait_px, 14, fill="#dcfce7", stroke="#86efac", sw=1, rx=2))
    f.append(text(680 + max_wait_px / 2, 355 - 1, "ліміт maxWait", size=9, color="#15803d"))
    f.append(circle(805, 355, 6, fill="#7c3aed", stroke="#ffffff", sw=1.5))
    f.append(text(805, 377, "Виклик 3 (maxWait)", size=10, bold=True, color="#7c3aed"))
    f.append(text(805, 392, "прорив голодування", size=9, color="#7c3aed"))

    render(os.path.join(IMG, "timing-debounce-modes.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. timing-throttle-modes.svg: Часові діаграми тротлінгу
# ─────────────────────────────────────────────────────────────────────────────
def make_throttle_timing():
    W, H = 1000, 460
    f = []

    f.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))
    f.append(text(W / 2, 35, "Режими тротлінгу (Throttling): гарантована періодичність викликів", size=15, bold=True))

    t_start_x = 220
    t_end_x = 940
    f.append(line(t_start_x, 415, t_end_x, 415, color="#555555", sw=1.5))
    f.append(arrow(t_end_x - 10, 415, t_end_x + 20, 415, color="#555555", sw=1.5))
    f.append(text(t_end_x + 25, 419, "Час (t)", size=12, anchor="start", color="#555555"))

    # Інтервали квантування T = 140 px
    interval_w = 140
    start_t0 = 240
    windows = [start_t0 + i * interval_w for i in range(5)]

    for i, wx in enumerate(windows):
        f.append(line(wx, 55, wx, 410, color="#94a3b8", sw=1, dash="3,3"))
        f.append(line(wx, 412, wx, 418, color="#475569", sw=1))
        f.append(text(wx, 432, f"T{i} ({i * 100}мс)", size=11, color="#475569"))
        if i < 4:
            f.append(rect(wx + 2, 57, interval_w - 4, 18, fill="#f1f5f9", stroke="none"))
            f.append(text(wx + interval_w / 2, 70, f"Квант часу T ({i+1})", size=10, color=MUTED))

    # Рядки
    rows = [
        {"y": 105, "title": "Вхідні події", "desc": "Щільний потік (scroll / move)"},
        {"y": 185, "title": "Leading Throttle", "desc": "Виклик на старті кожного кванта"},
        {"y": 265, "title": "Trailing Throttle", "desc": "Виклик у кінці кванта з останнім"},
        {"y": 345, "title": "Leading + Trailing", "desc": "Швидкий старт + фінальний стан"}
    ]

    for r in rows:
        ry = r["y"]
        f.append(rect(20, ry - 18, 185, 54, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
        f.append(text(112, ry + 2, r["title"], size=12, bold=True, color=INK))
        f.append(text(112, ry + 22, r["desc"], size=10, color=MUTED))
        f.append(line(t_start_x, ry + 10, t_end_x, ry + 10, color="#cbd5e1", sw=1.2))

    # Події у квантах
    # Квант 0 [240..380]: 250, 275, 305, 340, 370
    # Квант 1 [380..520]: 390, 420, 460, 500
    # Квант 2 [520..660]: 530, 560 (зупинився на 560!)
    # Квант 3 [660..800]: порожній
    q0_events = [250, 275, 305, 340, 370]
    q1_events = [390, 420, 460, 500]
    q2_events = [530, 560]
    all_ev = q0_events + q1_events + q2_events

    for ex in all_ev:
        f.append(line(ex, 115, ex, 85, color=NEG, sw=1.8))
        f.append(circle(ex, 85, 3.5, fill=NEG, stroke="#ffffff", sw=1))

    # 1. Leading Throttle: постріли на першу подію в кванті
    # Квант 0 -> постріл на 250
    f.append(circle(250, 195, 6, fill=POS, stroke="#ffffff", sw=1.5))
    f.append(text(250, 217, "Виклик (250)", size=10, bold=True, color=POS))
    # Квант 1 -> постріл на 390
    f.append(circle(390, 195, 6, fill=POS, stroke="#ffffff", sw=1.5))
    f.append(text(390, 217, "Виклик (390)", size=10, bold=True, color=POS))
    # Квант 2 -> постріл на 530
    f.append(circle(530, 195, 6, fill=POS, stroke="#ffffff", sw=1.5))
    f.append(text(530, 217, "Виклик (530)", size=10, bold=True, color=POS))
    f.append(text(730, 205, "Фінальна подія 560 втрачена!", size=10, italic=True, color=POS))

    # 2. Trailing Throttle: виклики наприкінці кванта
    # Квант 0 -> кінець на 380 з даними 370
    f.append(circle(380, 275, 6, fill=FIELD, stroke="#ffffff", sw=1.5))
    f.append(text(380, 297, "Виклик (370)", size=10, bold=True, color=FIELD))
    # Квант 1 -> кінець на 520 з даними 500
    f.append(circle(520, 275, 6, fill=FIELD, stroke="#ffffff", sw=1.5))
    f.append(text(520, 297, "Виклик (500)", size=10, bold=True, color=FIELD))
    # Квант 2 -> кінець на 660 з даними 560
    f.append(circle(660, 275, 6, fill=FIELD, stroke="#ffffff", sw=1.5))
    f.append(text(660, 297, "Виклик (560)", size=10, bold=True, color=FIELD))

    # 3. Leading + Trailing: постріл на старті + хвіст у кінці
    # Квант 0: старт на 250, хвіст на 380 (дані 370)
    f.append(circle(250, 355, 5.5, fill=POS, stroke="#ffffff", sw=1.5))
    f.append(circle(380, 355, 5.5, fill=FIELD, stroke="#ffffff", sw=1.5))
    f.append(text(250, 377, "Старт 250", size=9, bold=True, color=POS))
    f.append(text(380, 377, "Хвіст 370", size=9, bold=True, color=FIELD))

    # Квант 1: хвіст на 520 (дані 500)
    f.append(circle(520, 355, 5.5, fill=FIELD, stroke="#ffffff", sw=1.5))
    f.append(text(520, 377, "Хвіст 500", size=9, bold=True, color=FIELD))

    # Квант 2: хвіст на 660 (дані 560 — збережено фінальний стан!)
    f.append(circle(660, 355, 5.5, fill=FIELD, stroke="#ffffff", sw=1.5))
    f.append(text(660, 377, "Хвіст 560 (фінал)", size=9, bold=True, color=FIELD))

    render(os.path.join(IMG, "timing-throttle-modes.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. raf-vsync-coalescing.svg: Коалесценція подій у requestAnimationFrame
# ─────────────────────────────────────────────────────────────────────────────
def make_raf_coalescing():
    W, H = 1040, 420
    f = []

    f.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))
    f.append(text(W / 2, 35, "Коалесценція високочастотного вводу через requestAnimationFrame", size=15, bold=True))

    # Два кадри по 16.67 мс (60 Гц)
    f_w = 290
    f1_x = 230
    f2_x = f1_x + f_w + 15

    # Кадр 1
    f.append(rect(f1_x, 60, f_w, 330, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(f1_x + f_w / 2, 80, "Кадр N (16.67 мс)", size=13, bold=True, color=INK))

    # Кадр 2
    f.append(rect(f2_x, 60, f_w, 330, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(f2_x + f_w / 2, 80, "Кадр N+1 (16.67 мс)", size=13, bold=True, color=INK))

    # Ліва колонка — мітки шарів
    f.append(rect(20, 105, 190, 75, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    f.append(text(115, 130, "Вхідні макрозадачі", size=12, bold=True, color=INK))
    f.append(text(115, 150, "1000 Гц миша / тач", size=10, color=MUTED))
    f.append(text(115, 168, "запис (x, y) у пам'ять", size=10, color=FIELD))

    f.append(rect(20, 195, 190, 80, fill="#eff6ff", stroke="#bfdbfe", sw=1, rx=4))
    f.append(text(115, 220, "Фаза rAF зворотних викликів", size=12, bold=True, color=NEG))
    f.append(text(115, 240, "виконується строго перед", size=10, color=MUTED))
    f.append(text(115, 258, "перерахунком стилів і малюванням", size=10, color=MUTED))

    f.append(rect(20, 290, 190, 85, fill="#f0fdf4", stroke="#bbf7d0", sw=1, rx=4))
    f.append(text(115, 315, "Конвеєр рендерингу", size=12, bold=True, color=FIELD))
    f.append(text(115, 335, "Style → Layout → Paint", size=10, bold=True, color=INK))
    f.append(text(115, 355, "1 раз на VSync (без тротлінгу)", size=10, color=MUTED))

    # Події всередині Кадру 1: 7 подій миші
    ev_x1 = [f1_x + 20 + i * 36 for i in range(7)]
    for i, ex in enumerate(ev_x1):
        f.append(circle(ex, 135, 9, fill="#e2e8f0", stroke="#64748b", sw=1.2))
        f.append(text(ex, 139, f"e{i+1}", size=9, bold=True, color="#334155"))
        # Стрілка вниз до акумулятора
        f.append(line(ex, 146, ex, 165, color="#94a3b8", sw=1))

    # Буфер стану
    f.append(rect(f1_x + 10, 165, f_w - 20, 20, fill="#dcfce7", stroke="#86efac", sw=1, rx=3))
    f.append(text(f1_x + f_w / 2, 179, "state = {x: 412, y: 195}", size=10, color="#15803d", bold=True))

    # Блок rAF перед VSync у Кадрі 1
    raf_x1 = f1_x + f_w - 75
    f.append(rect(raf_x1, 205, 65, 60, fill="#dbeafe", stroke="#3b82f6", sw=1.5, rx=4))
    f.append(text(raf_x1 + 32, 227, "rAF cb", size=11, bold=True, color="#1d4ed8"))
    f.append(text(raf_x1 + 32, 245, "1 запуск", size=10, color="#1e40af"))
    f.append(arrow(f1_x + f_w / 2, 186, raf_x1 + 32, 203, color="#3b82f6", sw=1.5))

    # Рендеринг у Кадрі 1
    f.append(rect(raf_x1, 300, 65, 70, fill="#bbf7d0", stroke="#22c55e", sw=1.5, rx=4))
    f.append(text(raf_x1 + 32, 322, "Style", size=10, bold=True, color="#15803d"))
    f.append(text(raf_x1 + 32, 340, "Layout", size=10, bold=True, color="#15803d"))
    f.append(text(raf_x1 + 32, 358, "Paint", size=10, bold=True, color="#15803d"))
    f.append(arrow(raf_x1 + 32, 266, raf_x1 + 32, 298, color="#22c55e", sw=1.5))

    # Події всередині Кадру 2
    ev_x2 = [f2_x + 20 + i * 36 for i in range(7)]
    for i, ex in enumerate(ev_x2):
        f.append(circle(ex, 135, 9, fill="#e2e8f0", stroke="#64748b", sw=1.2))
        f.append(text(ex, 139, f"e{i+8}", size=9, bold=True, color="#334155"))
        f.append(line(ex, 146, ex, 165, color="#94a3b8", sw=1))

    f.append(rect(f2_x + 10, 165, f_w - 20, 20, fill="#dcfce7", stroke="#86efac", sw=1, rx=3))
    f.append(text(f2_x + f_w / 2, 179, "state = {x: 480, y: 230}", size=10, color="#15803d", bold=True))

    raf_x2 = f2_x + f_w - 75
    f.append(rect(raf_x2, 205, 65, 60, fill="#dbeafe", stroke="#3b82f6", sw=1.5, rx=4))
    f.append(text(raf_x2 + 32, 227, "rAF cb", size=11, bold=True, color="#1d4ed8"))
    f.append(text(raf_x2 + 32, 245, "1 запуск", size=10, color="#1e40af"))
    f.append(arrow(f2_x + f_w / 2, 186, raf_x2 + 32, 203, color="#3b82f6", sw=1.5))

    f.append(rect(raf_x2, 300, 65, 70, fill="#bbf7d0", stroke="#22c55e", sw=1.5, rx=4))
    f.append(text(raf_x2 + 32, 322, "Style", size=10, bold=True, color="#15803d"))
    f.append(text(raf_x2 + 32, 340, "Layout", size=10, bold=True, color="#15803d"))
    f.append(text(raf_x2 + 32, 358, "Paint", size=10, bold=True, color="#15803d"))
    f.append(arrow(raf_x2 + 32, 266, raf_x2 + 32, 298, color="#22c55e", sw=1.5))

    # Висновок праворуч
    res_x = f2_x + f_w + 15
    f.append(rect(res_x, 105, 170, 270, fill="#fefce8", stroke="#fef08a", sw=1.5, rx=6))
    f.append(text(res_x + 85, 130, "Результат", size=13, bold=True, color="#854d0e"))
    f.append(mtext(res_x + 85, 160,
                   "• 14 подій вводу\n"
                   "  зведені до 2 викликів\n\n"
                   "• Нуль зайвих Layout\n"
                   "  і відмальовок\n\n"
                   "• Ідеальна синхронізація\n"
                   "  з розгорткою екрана\n\n"
                   "• 60 / 120 FPS без ривків",
                   size=11, color="#713f12", lh=1.35))

    render(os.path.join(IMG, "raf-vsync-coalescing.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4. debounce-state-machine.svg: Автомат станів обмежувача частоти подій
# ─────────────────────────────────────────────────────────────────────────────
def make_state_machine():
    W, H = 1000, 480
    f = []

    f.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))
    f.append(text(W / 2, 35, "Внутрішній скінченний автомат універсального дебаунсу / тротлінгу", size=15, bold=True))

    # Стани
    # 1. IDLE (Очікування)
    b1, w1, h1 = textbox(160, 130, "IDLE\n(Стан спокою)", size=13, pad=14, fill="#f1f5f9", stroke="#64748b", bold=True)
    f.append(b1)

    # 2. SCHEDULED (Таймер запущено)
    b2, w2, h2 = textbox(520, 130, "SCHEDULED\n(Очікування delay / кванта)", size=13, pad=14, fill="#dbeafe", stroke="#2563eb", bold=True)
    f.append(b2)

    # 3. MAX_WAIT (Очікування граничного часу)
    b3, w3, h3 = textbox(520, 340, "MAX_WAIT_ACTIVE\n(Контроль голодування)", size=13, pad=14, fill="#fef3c7", stroke="#d97706", bold=True)
    f.append(b3)

    # 4. EXECUTING (Виклик цільової функції)
    b4, w4, h4 = textbox(850, 230, "INVOKING\n(Виконання fn(...))", size=13, pad=14, fill="#dcfce7", stroke="#16a34a", bold=True)
    f.append(b4)

    # 5. CANCELLED / FLUSHED
    b5, w5, h5 = textbox(160, 340, "CANCELLED / FLUSHED\n(Скидання стану)", size=12, pad=12, fill="#fee2e2", stroke="#dc2626", bold=True)
    f.append(b5)

    # Переходи
    # IDLE -> SCHEDULED (виклик wrapper(args))
    f.append(arrow(240, 130, 400, 130, color="#2563eb", sw=1.8))
    f.append(text(320, 115, "call(args)", size=11, bold=True, color="#2563eb"))
    f.append(text(320, 150, "leading=true → fn()", size=9, color=MUTED))

    # SCHEDULED -> SCHEDULED (повторний call: скидання таймера delay)
    f.append(rect(460, 40, 120, 36, fill="#f8fafc", stroke="#93c5fd", sw=1, rx=4))
    f.append(text(520, 56, "call(args) [ще раз]", size=10, bold=True, color="#1e40af"))
    f.append(text(520, 70, "delay таймер перезапуск", size=9, color=MUTED))
    f.append(line(480, 95, 480, 77, color="#2563eb", sw=1.2))
    f.append(arrow(560, 77, 560, 95, color="#2563eb", sw=1.2))

    # SCHEDULED -> MAX_WAIT_ACTIVE (якщо задано maxWait)
    f.append(arrow(520, 175, 520, 295, color="#d97706", sw=1.5))
    f.append(text(565, 235, "maxWait таймер", size=10, bold=True, color="#d97706"))

    # SCHEDULED -> INVOKING (спрацював таймер delay)
    f.append(arrow(645, 130, 770, 200, color="#16a34a", sw=1.8))
    f.append(text(725, 150, "delay вийшов", size=11, bold=True, color="#16a34a"))
    f.append(text(725, 167, "trailing=true", size=9, color=MUTED))

    # MAX_WAIT_ACTIVE -> INVOKING (спрацював maxWait)
    f.append(arrow(645, 340, 770, 260, color="#16a34a", sw=1.8))
    f.append(text(730, 310, "maxWait вийшов!", size=11, bold=True, color="#b45309"))

    # INVOKING -> IDLE (після виконання)
    f.append(line(850, 190, 850, 75, color="#16a34a", sw=1.5))
    f.append(line(850, 75, 160, 75, color="#16a34a", sw=1.5))
    f.append(arrow(160, 75, 160, 95, color="#16a34a", sw=1.5))
    f.append(text(520, 90, "очищення таймерів → повернення до спокою", size=10, color="#15803d"))

    # SCHEDULED -> CANCELLED (виклик .cancel() або .flush())
    f.append(arrow(430, 165, 235, 305, color="#dc2626", sw=1.5))
    f.append(text(310, 230, ".cancel() / .flush()", size=10, bold=True, color="#dc2626"))

    # CANCELLED -> IDLE
    f.append(arrow(160, 300, 160, 175, color="#64748b", sw=1.5))
    f.append(text(110, 240, "скинуто", size=10, color=MUTED))

    render(os.path.join(IMG, "debounce-state-machine.svg"), W, H, *f)


def main():
    make_debounce_timing()
    make_throttle_timing()
    make_raf_coalescing()
    make_state_machine()
    print("Всі 4 діаграми успішно згенеровано у теці img/")


if __name__ == "__main__":
    main()
