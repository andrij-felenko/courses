# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. event-vs-interrupt: Переривання проти подієвої матриці ────────────────
def fig_event_vs_interrupt():
    W, H = 840, 430
    p = []

    # Розділювач між двома шляхами
    p.append(line(40, 215, W - 40, 215, color="#d5d9dd", sw=1.2, dash="3 4"))

    # ── ВЕРХНЯ ЧАСТИНА: Класичний шлях через переривання (NVIC / CPU) ──
    y_top = 40
    p.append(text(60, y_top + 16, "Традиційний шлях: через переривання ядра", size=13, color=POS, anchor="start", bold=True))

    # Блоки: Периферія 1 -> NVIC -> CPU (стек, ISR, регістри) -> Периферія 2
    b1, _, _ = textbox(120, y_top + 70, "Периферія A\n(подія / статус)", size=10.5, pad=8, fill="#fef0ef", stroke=POS, sw=1.6)
    p.append(b1)

    p.append(arrow(180, y_top + 70, 240, y_top + 70, color=POS, sw=2.0))
    p.append(text(210, y_top + 58, "IRQ", size=10, color=POS, bold=True))

    b2, _, _ = textbox(305, y_top + 70, "Контролер NVIC\n(арбітраж пріоритетів)", size=10.5, pad=8, fill="#f4f6f8", stroke="#c8ccd0", sw=1.5)
    p.append(b2)

    p.append(arrow(375, y_top + 70, 435, y_top + 70, color=POS, sw=2.0))
    p.append(text(405, y_top + 58, "вектор", size=10, color=POS, bold=True))

    b3, _, _ = textbox(525, y_top + 70, "Ядро CPU (активне)\n1. Збереження стек-фрейму\n2. Вибірка ISR з Flash\n3. Читання/запис шини APB", size=10, pad=8, fill="#fff5e6", stroke="#e67e22", sw=1.6)
    p.append(b3)

    p.append(arrow(620, y_top + 70, 685, y_top + 70, color=POS, sw=2.0))
    p.append(text(652, y_top + 58, "запис", size=10, color=POS, bold=True))

    b4, _, _ = textbox(745, y_top + 70, "Периферія B\n(запуск дії)", size=10.5, pad=8, fill="#f4f6f8", stroke="#c8ccd0", sw=1.5)
    p.append(b4)

    # Підсумок верхньої частини
    p.append(text(W / 2, y_top + 145, "Затримка: 30–150 тактів · Джиттер: ±10..50 тактів · Струм: 5–15 мА (CPU працює)", size=11, color=POS, italic=True, bold=True))

    # ── НИЖНЯ ЧАСТИНА: Подієва матриця (Event System / PPI / Interconnect) ──
    y_bot = 235
    p.append(text(60, y_bot + 16, "Апаратна матриця подій: прямий зв'язок без CPU", size=13, color=FIELD, anchor="start", bold=True))

    b_e1, _, _ = textbox(120, y_bot + 75, "Джерело події\n(Event Generator)", size=10.5, pad=8, fill="#edf7ed", stroke=FIELD, sw=1.6)
    p.append(b_e1)

    p.append(arrow(185, y_bot + 75, 275, y_bot + 75, color=FIELD, sw=2.4))
    p.append(text(230, y_bot + 62, "EVENT (строб)", size=10, color=FIELD, bold=True))

    b_mat, _, _ = textbox(375, y_bot + 75, "Апаратна матриця подій\n(Подієвий канал / Crossbar)\n0 тактів CPU · Апаратна комутація", size=10.5, pad=9, fill="#e8f5e9", stroke=FIELD, sw=2.0)
    p.append(b_mat)

    p.append(arrow(475, y_bot + 75, 565, y_bot + 75, color=FIELD, sw=2.4))
    p.append(text(520, y_bot + 62, "TASK (тригер)", size=10, color=FIELD, bold=True))

    b_e2, _, _ = textbox(635, y_bot + 75, "Споживач події\n(Event User / Task)", size=10.5, pad=8, fill="#edf7ed", stroke=FIELD, sw=1.6)
    p.append(b_e2)

    # CPU спить поруч
    b_cpu_sleep, _, _ = textbox(760, y_bot + 75, "Ядро CPU\nСПИТЬ (WFI)\nструм ~2 мкА", size=10, pad=8, fill="#f0f4f8", stroke="#90a4ae", sw=1.4)
    p.append(b_cpu_sleep)

    p.append(text(W / 2, y_bot + 150, "Затримка: 1 такт (синхронно) або 0 тактів (асинхронно) · Джиттер: 0.0 нс · Струм: мкА", size=11, color=FIELD, italic=True, bold=True))

    render(os.path.join(OUT, "event-vs-interrupt.svg"), W, H, *p,
           title="Порівняння: реакція через переривання CPU проти апаратної матриці подій")


# ── 2. async-vs-sync-event-timing: Синхронні та асинхронні події ─────────────
def fig_async_vs_sync_event_timing():
    W, H = 820, 390
    p = []

    # Заголовок блоків
    p.append(text(W / 2, 48, "Поширення сигналу події в часі: Асинхронний проти Синхронного шляху", size=12.5, color=INK, bold=True))

    # ── Асинхронний канал (Async Event Channel) ──
    ay = 70
    p.append(rect(40, ay, 740, 125, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    p.append(text(55, ay + 20, "Асинхронний канал (Microchip EVSYS / STM32 EXTI): чиста логіка, тактування вимкнене", size=11, color=FIELD, anchor="start", bold=True))

    # Діаграма сигналів
    # Вхідний перепад
    p.append(text(120, ay + 55, "Вхід (генератор):", size=10, color=INK, anchor="end"))
    p.append(line(130, ay + 62, 220, ay + 62, color=INK, sw=1.8))
    p.append(line(220, ay + 62, 220, ay + 42, color=FIELD, sw=2.2))
    p.append(line(220, ay + 42, 400, ay + 42, color=FIELD, sw=1.8))

    # Вихід на споживача
    p.append(text(120, ay + 95, "Вихід (споживач):", size=10, color=INK, anchor="end"))
    p.append(line(130, ay + 102, 224, ay + 102, color=INK, sw=1.8))
    p.append(line(224, ay + 102, 224, ay + 82, color=FIELD, sw=2.2))
    p.append(line(224, ay + 82, 400, ay + 82, color=FIELD, sw=1.8))

    # Затримка t_prop
    p.append(line(220, ay + 36, 220, ay + 108, color="#e0a800", sw=1.2, dash="2 2"))
    p.append(line(224, ay + 36, 224, ay + 108, color="#e0a800", sw=1.2, dash="2 2"))

    box_async, _, _ = textbox(580, ay + 72, "Затримка вентилів t_prop ≈ 2–5 нс\nНе потребує тактової частоти\nПрацює в режимі глибокого сну", size=10, pad=8, fill="#e8f5e9", stroke=FIELD, sw=1.5)
    p.append(box_async)

    # ── Синхронний канал із CDC (Sync Channel with CDC) ──
    sy = 215
    p.append(rect(40, sy, 740, 140, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    p.append(text(55, sy + 20, "Синхронний канал із вирівнюванням домену тактування (CDC Resynchronization)", size=11, color=NEG, anchor="start", bold=True))

    # Тактовий сигнал домену B
    p.append(text(120, sy + 50, "Тактовий сигнал CLK_B:", size=10, color=MUTED, anchor="end"))
    cx = 130
    for i in range(7):
        p.append(line(cx, sy + 54, cx + 18, sy + 54, color=MUTED, sw=1.2))
        p.append(line(cx + 18, sy + 54, cx + 18, sy + 40, color=MUTED, sw=1.2))
        p.append(line(cx + 18, sy + 40, cx + 36, sy + 40, color=MUTED, sw=1.2))
        p.append(line(cx + 36, sy + 40, cx + 36, sy + 54, color=MUTED, sw=1.2))
        cx += 36

    # Вхідний строб з домену A
    p.append(text(120, sy + 80, "Подія з домену A:", size=10, color=INK, anchor="end"))
    p.append(line(130, sy + 84, 175, sy + 84, color=INK, sw=1.6))
    p.append(line(175, sy + 84, 175, sy + 70, color=NEG, sw=2.0))
    p.append(line(175, sy + 70, 230, sy + 70, color=NEG, sw=2.0))
    p.append(line(230, sy + 70, 230, sy + 84, color=NEG, sw=2.0))
    p.append(line(230, sy + 84, 380, sy + 84, color=INK, sw=1.6))

    # Синхронізований строб у домені B (через 2 такти)
    p.append(text(120, sy + 112, "Строб у домені B:", size=10, color=INK, anchor="end"))
    p.append(line(130, sy + 116, 274, sy + 116, color=INK, sw=1.6))
    p.append(line(274, sy + 116, 274, sy + 100, color=FIELD, sw=2.2))
    p.append(line(274, sy + 100, 310, sy + 100, color=FIELD, sw=2.2))
    p.append(line(310, sy + 100, 310, sy + 116, color=FIELD, sw=2.2))
    p.append(line(310, sy + 116, 380, sy + 116, color=INK, sw=1.6))

    box_sync, _, _ = textbox(580, sy + 80, "Подвійний D-тригер (CDC 2-FF)\nЗатримка: строго 2 такти CLK_B\nПовний захист від метастабільності", size=10, pad=8, fill="#eaf0fd", stroke=NEG, sw=1.5)
    p.append(box_sync)

    render(os.path.join(OUT, "async-vs-sync-event-timing.svg"), W, H, *p,
           title="Фізика подієвих сигналів: комбінаційний асинхронний та синхронізований шляхи")


# ── 3. ppi-vs-dppi-vs-dmamux: Порівняння трьох топологій ─────────────────────
def fig_ppi_vs_dppi_vs_dmamux():
    W, H = 840, 460
    p = []

    # Три колонки: Nordic PPI, Nordic DPPI, STM32 DMAMUX
    cw = 240
    gap = 25
    x_base = 35

    # ── КОЛОНКА 1: Nordic PPI (Централізована) ──
    x1 = x_base
    p.append(rect(x1, 50, cw, 380, fill="#fbfcfd", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(x1 + cw / 2, 75, "Nordic PPI (nRF52)", size=12, color=INK, bold=True))
    p.append(text(x1 + cw / 2, 92, "Централізований Point-to-Point", size=10, color=MUTED, italic=True))

    b_src1, _, _ = textbox(x1 + cw / 2, 130, "Джерело: EVENT\n(адреса регістра)", size=10, pad=6, fill="#edf7ed", stroke=FIELD, sw=1.4)
    p.append(b_src1)

    p.append(arrow(x1 + cw / 2, 155, x1 + cw / 2, 185, color=FIELD, sw=1.8))

    b_chan1, _, _ = textbox(x1 + cw / 2, 230, "Центральний блок PPI\nРегістри каналу N:\n· EEP = &EVENT_SRC\n· TEP = &TASK_DST\n· FORK.TEP = &TASK2", size=9.5, pad=7, fill="#e8f5e9", stroke=FIELD, sw=1.8)
    p.append(b_chan1)

    p.append(arrow(x1 + cw / 2 - 35, 275, x1 + 50, 330, color=FIELD, sw=1.8))
    p.append(arrow(x1 + cw / 2 + 35, 275, x1 + cw - 50, 330, color=FIELD, sw=1.8))

    b_dst1, _, _ = textbox(x1 + 50, 355, "TASK 1\n(основна)", size=9.5, pad=6, fill="#f4f6f8", stroke="#c8ccd0", sw=1.4)
    b_dst2, _, _ = textbox(x1 + cw - 50, 355, "TASK 2\n(FORK)", size=9.5, pad=6, fill="#f4f6f8", stroke="#c8ccd0", sw=1.4)
    p.append(b_dst1)
    p.append(b_dst2)

    p.append(text(x1 + cw / 2, 410, "Гнучко, але довгі дроти", size=10, color=MUTED, italic=True))

    # ── КОЛОНКА 2: Nordic DPPI (Розподілена шина) ──
    x2 = x_base + cw + gap
    p.append(rect(x2, 50, cw, 380, fill="#fbfcfd", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(x2 + cw / 2, 75, "Nordic DPPI (nRF53/91)", size=12, color=INK, bold=True))
    p.append(text(x2 + cw / 2, 92, "Розподілена шина Publish/Subscribe", size=10, color=MUTED, italic=True))

    b_dpub, _, _ = textbox(x2 + cw / 2, 130, "Периферія 1 (Джерело)\nPUBLISH_EVENT = 7\n(транслює на шину 7)", size=9.5, pad=6, fill="#edf7ed", stroke=FIELD, sw=1.4)
    p.append(b_dpub)

    p.append(arrow(x2 + cw / 2, 160, x2 + cw / 2, 195, color=FIELD, sw=2.0))

    # Шина DPPI (набір ліній)
    p.append(rect(x2 + 20, 200, cw - 40, 50, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    p.append(text(x2 + cw / 2, 220, "Магістраль DPPI (Канали 0..31)", size=10, color=NEG, bold=True))
    p.append(text(x2 + cw / 2, 236, "Немає центрального комутатора", size=9.5, color=MUTED, italic=True))

    p.append(arrow(x2 + 65, 250, x2 + 65, 290, color=NEG, sw=1.8))
    p.append(arrow(x2 + cw - 65, 250, x2 + cw - 65, 290, color=NEG, sw=1.8))

    b_dsub1, _, _ = textbox(x2 + 65, 330, "Периферія A\nSUBSCRIBE_START=7", size=9.5, pad=5, fill="#f4f6f8", stroke="#c8ccd0", sw=1.4)
    b_dsub2, _, _ = textbox(x2 + cw - 65, 330, "Периферія B\nSUBSCRIBE_CAP=7", size=9.5, pad=5, fill="#f4f6f8", stroke="#c8ccd0", sw=1.4)
    p.append(b_dsub1)
    p.append(b_dsub2)

    p.append(text(x2 + cw / 2, 410, "Локальні домени TrustZone", size=10, color=MUTED, italic=True))

    # ── КОЛОНКА 3: STM32 DMAMUX / Triggers ──
    x3 = x_base + (cw + gap) * 2
    p.append(rect(x3, 50, cw, 380, fill="#fbfcfd", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(x3 + cw / 2, 75, "STM32 DMAMUX & Triggers", size=12, color=INK, bold=True))
    p.append(text(x3 + cw / 2, 92, "Мультиплексор + Синхронізатор", size=10, color=MUTED, italic=True))

    b_sgen, _, _ = textbox(x3 + cw / 2, 130, "Події: EXTI, TIM TRGO, COMP\n(генератори тригерів)", size=9.5, pad=6, fill="#edf7ed", stroke=FIELD, sw=1.4)
    p.append(b_sgen)

    p.append(arrow(x3 + cw / 2, 160, x3 + cw / 2, 195, color=FIELD, sw=1.8))

    b_dmamux, _, _ = textbox(x3 + cw / 2, 235, "Блок DMAMUX\n· Request Generator\n· Trigger Counter (N подій)\n· Синхронізатор фронту", size=9.5, pad=7, fill="#fff5e6", stroke="#e67e22", sw=1.8)
    p.append(b_dmamux)

    p.append(arrow(x3 + cw / 2, 275, x3 + cw / 2, 310, color="#e67e22", sw=2.0))

    b_dma_ch, _, _ = textbox(x3 + cw / 2, 345, "DMA Канал -> SRAM Буфер\n(автономна пересилка блоку)", size=9.5, pad=6, fill="#f4f6f8", stroke="#c8ccd0", sw=1.4)
    p.append(b_dma_ch)

    p.append(text(x3 + cw / 2, 410, "Події керують запитами DMA", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "ppi-vs-dppi-vs-dmamux.svg"), W, H, *p,
           title="Архітектурні моделі: централізований PPI, розподілений DPPI та STM32 DMAMUX")


# ── 4. autonomous-pipeline: Наскрізний автономний вимірювальний конвеєр ──────
def fig_autonomous_pipeline():
    W, H = 840, 440
    p = []

    # Заголовок
    p.append(text(W / 2, 45, "Автономний 5-ланковий вимірювальний конвеєр без участі CPU", size=13, color=INK, bold=True))

    # Горизонтальні блоки конвеєра: COMP -> TIM -> ADC -> DMA -> SRAM -> CPU Wakeup
    steps = [
        ("1. Компаратор", "COMP_OUT\n(поріг напруги)", 100, 110),
        ("2. Таймер затримки", "TIM_START\n(пауза 10 мкс)", 260, 110),
        ("3. АЦП перетворювач", "ADC_START\n(пачка 4 канали)", 420, 110),
        ("4. DMAMUX / DMA", "DMA_REQ\n(пересилка слів)", 580, 110),
        ("5. Буфер пам'яті", "SRAM Buffer\n(накопичення кадру)", 740, 110),
    ]

    for title, desc, cx, cy in steps:
        b, _, _ = textbox(cx, cy + 12, desc, size=9.5, pad=6, fill="#f8fafc", stroke="#64748b", sw=1.5)
        p.append(text(cx, cy - 20, title, size=10.5, color=INK, bold=True))
        p.append(b)

    # Стрілки між етапами (подієві строби)
    arrows_data = [
        (160, 122, 200, 122, "Канал 0\n(строб)"),
        (320, 122, 360, 122, "TRGO\nКанал 1"),
        (480, 122, 520, 122, "EOC\nКанал 2"),
        (640, 122, 680, 122, "AHB шина\n(дані)"),
    ]
    for x1, y1, x2, y2, lbl in arrows_data:
        p.append(arrow(x1, y1, x2, y2, color=FIELD, sw=2.2))
        p.append(mtext((x1 + x2) / 2, y1 - 20, lbl.split("\n"), size=9.5, color=FIELD, bold=True))

    # ── Часова діаграма знизу (Стан CPU та Периферії) ──
    dy = 220
    p.append(rect(40, dy, 760, 175, fill="#fbfcfd", stroke="#cbd5e1", sw=1.4, rx=6))
    p.append(text(60, dy + 22, "Часова шкала подій та енергетичний профіль процесора:", size=11, color=INK, anchor="start", bold=True))

    # Вісь часу
    p.append(line(80, dy + 110, 760, dy + 110, color=MUTED, sw=1.5))
    p.append(arrow(740, dy + 110, 765, dy + 110, color=MUTED, sw=1.5))
    p.append(text(765, dy + 125, "час (t)", size=10, color=MUTED, anchor="end", italic=True))

    # Стан ядра: СПИТЬ (синій прямокутник), ПРОКИДАЄТЬСЯ (червоний прямокутник наприкінці)
    p.append(rect(100, dy + 55, 520, 36, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=4))
    p.append(text(360, dy + 77, "ЯДРО CPU СПИТЬ (режим WFI / DeepSleep · Струм ~2.5 мкА)", size=10.5, color=NEG, bold=True))

    p.append(rect(630, dy + 55, 120, 36, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    p.append(text(690, dy + 77, "CPU Прокидається\n(обробка кадру)", size=9.5, color=POS, bold=True))

    # Подія пробудження (DMA Transfer Complete)
    p.append(line(625, dy + 45, 625, dy + 110, color=POS, sw=2.0, dash="3 3"))
    p.append(text(625, dy + 40, "DMA TC IRQ", size=9.5, color=POS, bold=True))

    # Позначки точок часу на осі
    t_marks = [
        (110, "t0: Поріг COMP"),
        (220, "t1: Старт TIM"),
        (380, "t2: АЦП вибірка"),
        (540, "t3: DMA запис"),
        (625, "t4: Кадр готовий"),
    ]
    for tx, tlbl in t_marks:
        p.append(line(tx, dy + 105, tx, dy + 115, color=MUTED, sw=1.4))
        p.append(text(tx, dy + 130, tlbl, size=9.5, color=INK))

    p.append(text(W / 2, dy + 160, "Ядро не витрачає жодного такту на проміжні етапи 1–4 і прокидається лише на готовий результат", size=10.5, color=FIELD, italic=True, bold=True))

    render(os.path.join(OUT, "autonomous-pipeline.svg"), W, H, *p,
           title="Автономний вимірювальний конвеєр: 5 апаратних ланок без пробудження процесора")


if __name__ == "__main__":
    fig_event_vs_interrupt()
    fig_async_vs_sync_event_timing()
    fig_ppi_vs_dppi_vs_dmamux()
    fig_autonomous_pipeline()
    print("OK: all 4 figures generated in", OUT)
