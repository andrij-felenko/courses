# -*- coding: utf-8 -*-
"""figs.py — ілюстрації до теми «Причина скидання як діагноз».
Генерує векторні SVG-діаграми у теці ./img/ через svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

TOPIC_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(TOPIC_DIR)
os.makedirs(os.path.join(TOPIC_DIR, "img"), exist_ok=True)

AMBER   = "#b08900"
AMBERBG = "#fdf6e3"
BLUEBG  = "#eaf0fd"
GRNBG   = "#e9f7ef"
REDBG   = "#fdecea"
GREYBG  = "#eef2f7"
PURPLE  = "#6b21a8"
PURPLEBG= "#f3e8ff"


# ── 1. Апаратні джерела скидання та мультиплексор RCC_CSR ───────────────
def fig_reset_reason_flags():
    W, H = 960, 480
    P = [
        text(W / 2, 28, "Апаратні джерела скидання та мультиплексор RCC_CSR", size=16, bold=True),
        text(W / 2, 48, "фізичні тригери защіпаються в регістрах стану; без раннього очищення прапорці накопичуються",
             size=11, color=MUTED, italic=True)
    ]

    # Ліва колонка — апаратні джерела (тригери)
    sources = [
        ("POR / PDR", "Холодний старт / подача живлення 3.3 В", POS, REDBG),
        ("BOR / BOD", "Просідання напруги нижче порогу (Brownout)", POS, REDBG),
        ("IWDG", "Таймаут незалежного сторожового таймера", AMBER, AMBERBG),
        ("WWDG", "Порушення вікна віконного сторожового таймера", AMBER, AMBERBG),
        ("SFT / NVIC", "Програмне скидання (NVIC_SystemReset / Assert)", PURPLE, PURPLEBG),
        ("PIN / NRST", "Зовнішня кнопка, супервізор або SWD-дебагер", NEG, BLUEBG),
    ]

    x_src = 50
    w_src = 240
    h_src = 42
    gap_y = 14
    y_start = 80

    for i, (title_, desc, col, fill) in enumerate(sources):
        y = y_start + i * (h_src + gap_y)
        P.append(rect(x_src, y, w_src, h_src, fill=fill, stroke=col, sw=1.5))
        P.append(text(x_src + 12, y + 17, title_, size=11.5, color=col, bold=True, anchor="start"))
        P.append(text(x_src + 12, y + 33, desc, size=9.5, color=INK, anchor="start"))
        # Стрілка до мультиплексора
        P.append(arrow(x_src + w_src, y + h_src / 2, 360, 225, color=col, sw=1.3))

    # Центральний блок — Reset Controller (RCC_CSR)
    rc_x, rc_y, rc_w, rc_h = 360, 110, 230, 230
    P.append(rect(rc_x, rc_y, rc_w, rc_h, fill=GREYBG, stroke=LINE, sw=2, rx=8))
    P.append(text(rc_x + rc_w / 2, rc_y + 24, "Контролер скидання", size=13, bold=True))
    P.append(text(rc_x + rc_w / 2, rc_y + 42, "Регістр RCC_CSR / RMU", size=11, color=MUTED))

    # Прапорці всередині регістра
    flags = [
        ("LPWRRSTF", "26"), ("WWDGRSTF", "27"),
        ("IWDGRSTF", "28"), ("SFTRSTF",  "29"),
        ("PORRSTF",  "30"), ("PINRSTF",  "31")
    ]
    fx = rc_x + 15
    fy = rc_y + 60
    fw = 200
    fh = 24
    for name, bit in flags:
        P.append(rect(fx, fy, fw, fh, fill=BG, stroke="#cbd5e1", sw=1.2, rx=3))
        P.append(text(fx + 10, fy + 16, f"bit [{bit}]  {name}", size=9.5, color=INK, bold=True, anchor="start"))
        fy += fh + 4

    # Стрілка на Reset Core
    P.append(arrow(rc_x + rc_w, 225, 660, 225, color=LINE, sw=2))
    P.append(text(625, 215, "RESET", size=10, color=POS, bold=True))

    # Права колонка — пастка липких прапорців та правильна послідовність
    rt_x, rt_y, rt_w, rt_h = 660, 80, 250, 290
    P.append(rect(rt_x, rt_y, rt_w, rt_h, fill=BG, stroke=LINE, sw=1.5, rx=6))
    P.append(text(rt_x + rt_w / 2, rt_y + 22, "Пастка «липких» бітів", size=12.5, color=POS, bold=True))

    notes = [
        ("1. Холодний старт (POR):", POS, "Встановлено: POR + PIN"),
        ("2. Робота пристрою...", MUTED, "Прапорці залишаються 1!"),
        ("3. Збій за Watchdog (IWDG):", AMBER, "Встановлено: IWDG + POR + PIN"),
        ("4. Без очищення (RMVF):", POS, "Діагноз хибний: 'Cold Boot?!'"),
        ("5. Правило bootloader/main:", FIELD, "Зчитати RCC_CSR → у RAM,\nнегайно RCC_CSR |= RMVF!")
    ]
    ny = rt_y + 45
    for title_, col, body_ in notes:
        P.append(text(rt_x + 12, ny, title_, size=10, color=col, bold=True, anchor="start"))
        ny += 15
        for line_ in body_.split("\n"):
            P.append(text(rt_x + 16, ny, line_, size=9.5, color=INK, anchor="start"))
            ny += 14
        ny += 4

    # Нижній висновок
    fr, fw, fh = textbox(W / 2, 435,
                         "Прапорці скидання є апаратно накопичувальними. Читайте стан на першому рядку main() та одразу скидайте бітом RMVF.",
                         size=11.5, bold=True, fill=GRNBG, stroke=FIELD)
    P.append(fr)

    render("img/reset-reason-flags.svg", W, H, *P)


# ── 2. Анатомія кадру винятку ARM Cortex-M та регістри аварій ─────────────────
def fig_cortex_m_stack_frame():
    W, H = 960, 500
    P = [
        text(W / 2, 28, "Апаратне зняття стекового кадру та регістри винятків ARM Cortex-M", size=16, bold=True),
        text(W / 2, 48, "при виникненні HardFault ядро автоматично зберігає 8 регістрів на активний стек (MSP або PSP)",
             size=11, color=MUTED, italic=True)
    ]

    # Лівий блок — Автоматичний апаратний стек
    st_x, st_y, st_w = 70, 80, 270
    P.append(rect(st_x, st_y, st_w, 340, fill=GREYBG, stroke=LINE, sw=1.8, rx=6))
    P.append(text(st_x + st_w / 2, st_y + 24, "Апаратний стековий кадр", size=12.5, bold=True))
    P.append(text(st_x + st_w / 2, st_y + 42, "Автоматично зберігається ядром", size=10, color=MUTED))

    slots = [
        ("xPSR", "Стан процесора та прапорці", "SP + 28", GRNBG, FIELD),
        ("PC (r15)", "Адреса інструкції краху!", "SP + 24", REDBG, POS),
        ("LR (r14)", "Адреса повернення (caller)", "SP + 20", BLUEBG, NEG),
        ("R12", "Загальний регістр", "SP + 16", BG, LINE),
        ("R3", "Аргумент функції / значення", "SP + 12", BG, LINE),
        ("R2", "Аргумент функції / значення", "SP + 8", BG, LINE),
        ("R1", "Аргумент функції / значення", "SP + 4", BG, LINE),
        ("R0", "Перший аргумент / повернення", "SP + 0", BG, LINE),
    ]

    sy = st_y + 55
    sh = 28
    for reg_name, reg_desc, sp_off, fill, col in slots:
        P.append(rect(st_x + 12, sy, st_w - 24, sh, fill=fill, stroke=col, sw=1.3, rx=4))
        P.append(text(st_x + 20, sy + 18, reg_name, size=10.5, color=col, bold=True, anchor="start"))
        P.append(text(st_x + 95, sy + 18, reg_desc, size=9, color=INK, anchor="start"))
        P.append(text(st_x + st_w - 20, sy + 18, sp_off, size=9.5, color=MUTED, anchor="end"))
        sy += sh + 5

    # Центральний блок — EXC_RETURN та вибір стека
    ex_x, ex_y, ex_w = 380, 80, 240
    P.append(rect(ex_x, ex_y, ex_w, 170, fill=PURPLEBG, stroke=PURPLE, sw=1.5, rx=6))
    P.append(text(ex_x + ex_w / 2, ex_y + 22, "Регістр LR (EXC_RETURN)", size=12, color=PURPLE, bold=True))
    P.append(text(ex_x + ex_w / 2, ex_y + 40, "0xFFFFFFFx усередині Fault ISR", size=10, color=MUTED))

    exc_bits = [
        ("Bit [2] = 0", "Виняток перервав Handler (стек MSP)"),
        ("Bit [2] = 1", "Виняток перервав Thread (стек PSP)"),
        ("Bit [4] = 0", "Розширений кадр (FPU S0-S15)"),
        ("Bit [4] = 1", "Базовий кадр (8 слів, без FPU)")
    ]
    ey = ex_y + 55
    for bit_title, bit_desc in exc_bits:
        P.append(text(ex_x + 14, ey + 12, bit_title, size=10, color=PURPLE, bold=True, anchor="start"))
        P.append(text(ex_x + 14, ey + 25, bit_desc, size=9, color=INK, anchor="start"))
        ey += 27

    # Нижній центральний блок — Naked Trampoline
    tr_y = 265
    P.append(rect(ex_x, tr_y, ex_w, 155, fill=BG, stroke=LINE, sw=1.5, rx=6))
    P.append(text(ex_x + ex_w / 2, tr_y + 20, "Асемблерний трамплін", size=11.5, bold=True))
    P.append(text(ex_x + 12, tr_y + 42, "TST   LR, #4", size=10, color=PURPLE, bold=True, anchor="start"))
    P.append(text(ex_x + 12, tr_y + 60, "ITE   EQ", size=10, color=PURPLE, bold=True, anchor="start"))
    P.append(text(ex_x + 12, tr_y + 78, "MRSEQ R0, MSP  ; r0 = Main Stack", size=9.5, color=FIELD, bold=True, anchor="start"))
    P.append(text(ex_x + 12, tr_y + 96, "MRSNE R0, PSP  ; r0 = Task Stack", size=9.5, color=FIELD, bold=True, anchor="start"))
    P.append(text(ex_x + 12, tr_y + 114, "MOV   R1, LR   ; r1 = EXC_RETURN", size=9.5, color=INK, anchor="start"))
    P.append(text(ex_x + 12, tr_y + 132, "B     c_hardfault_handler", size=10, color=POS, bold=True, anchor="start"))

    # Правий блок — Регістри SCB (Діагностика)
    scb_x, scb_y, scb_w = 660, 80, 250
    P.append(rect(scb_x, scb_y, scb_w, 340, fill=BG, stroke=LINE, sw=1.8, rx=6))
    P.append(text(scb_x + scb_w / 2, scb_y + 24, "Регістри аналізу SCB", size=12.5, bold=True))

    scb_regs = [
        ("CFSR (0xE000ED28)", "Configurable Fault Status", [
            "• UFSR: DIVBYZERO, UNALIGNED, UNDEFINSTR",
            "• BFSR: PRECISERR, IMPRECISERR, STKERR",
            "• MMFSR: IACCVIOL, DACCVIOL, MUNSTKERR"
        ], REDBG, POS),
        ("HFSR (0xE000ED2C)", "HardFault Status", [
            "• FORCED: Ескалація з Bus/Usage/MemFault",
            "• VECTTBL: Помилка читання таблиці векторів"
        ], AMBERBG, AMBER),
        ("BFAR / MMFAR", "Адреса збою пам'яті", [
            "• BFAR: Точна адреса збійної шини",
            "• MMFAR: Адреса порушення MPU"
        ], BLUEBG, NEG)
    ]

    rgy = scb_y + 40
    for r_name, r_sub, r_items, r_fill, r_col in scb_regs:
        rh_box = 86
        P.append(rect(scb_x + 10, rgy, scb_w - 20, rh_box, fill=r_fill, stroke=r_col, sw=1.2, rx=4))
        P.append(text(scb_x + 16, rgy + 16, r_name, size=10.5, color=r_col, bold=True, anchor="start"))
        P.append(text(scb_x + 16, rgy + 30, r_sub, size=9.5, color=MUTED, anchor="start"))
        iy = rgy + 46
        for item in r_items:
            P.append(text(scb_x + 16, iy, item, size=9.5, color=INK, anchor="start"))
            iy += 15
        rgy += rh_box + 8

    # Нижній висновок
    fr, fw, fh = textbox(W / 2, 455,
                         "Трамплін витягує збережені значення PC, LR та R0-R3 з MSP/PSP і зіставляє їх з регістрами CFSR/BFAR для вичерпного звіту.",
                         size=11.5, bold=True, fill=BLUEBG, stroke=NEG)
    P.append(fr)

    render("img/cortex-m-stack-frame.svg", W, H, *P)


# ── 3. Повний життєвий цикл чорної скриньки (Flight Recorder) ─────────────────
def fig_crash_dump_lifecycle():
    W, H = 960, 480
    P = [
        text(W / 2, 28, "Життєвий цикл аварійного дампу (Flight Recorder)", size=16, bold=True),
        text(W / 2, 48, "від перехоплення краху в ядрі до збереження в Retention RAM та відправки телеметрії після перезапуску",
             size=11, color=MUTED, italic=True)
    ]

    steps = [
        ("1. Аварія / HardFault", "Ділення на 0, NULL-ptr,\nпомилка шини або Assert", REDBG, POS),
        ("2. Зняття знімка", "PC, LR, SP, CFSR, HFSR,\nверхівка стека, активна задача", AMBERBG, AMBER),
        ("3. Запис у .noinit", "Збереження в Retention RAM,\nрозрахунок контрольної CRC32", BLUEBG, NEG),
        ("4. Системний Reset", "NVIC_SystemReset() / IWDG;\nпам'ять SRAM не скидається!", GREYBG, LINE),
        ("5. Валідація при старті", "Перевірка MAGIC (0x43525348)\nта CRC32; захист від шуму POR", PURPLEBG, PURPLE),
        ("6. Телеметрія & Звіт", "Передача в хмару/UART/Flash;\nочищення скриньки після ACK", GRNBG, FIELD)
    ]

    box_w = 138
    box_h = 102
    gap_x = 15
    start_x = 30
    y_pos = 120

    for i, (st_title, st_desc, st_fill, st_col) in enumerate(steps):
        x = start_x + i * (box_w + gap_x)
        P.append(rect(x, y_pos, box_w, box_h, fill=st_fill, stroke=st_col, sw=1.6, rx=6))
        P.append(text(x + box_w / 2, y_pos + 20, st_title, size=10.5, color=st_col, bold=True))
        desc_lines = st_desc.split("\n")
        dy = y_pos + 44
        for dline in desc_lines:
            P.append(text(x + box_w / 2, dy, dline, size=9.5, color=INK))
            dy += 16

        if i < len(steps) - 1:
            P.append(arrow(x + box_w, y_pos + box_h / 2, x + box_w + gap_x, y_pos + box_h / 2, color=st_col, sw=1.6))

    # Нижня частина — організація пам'яті та лінкер
    ly_x, ly_y, ly_w, ly_h = 60, 250, 840, 150
    P.append(rect(ly_x, ly_y, ly_w, ly_h, fill="none", stroke=LINE, sw=1.5, rx=6))
    P.append(text(ly_x + 20, ly_y + 24, "Структура збереженої пам'яті Retention RAM (.noinit)", size=13, bold=True, anchor="start"))

    # Блоки пам'яті
    mem_blocks = [
        ("MAGIC (4B)", "0x43525348 ('CRSH')", 125, PURPLEBG, PURPLE),
        ("REASON (4B)", "RCC_CSR raw flags", 125, AMBERBG, AMBER),
        ("FAULT REG (16B)", "CFSR, HFSR, BFAR...", 145, REDBG, POS),
        ("CORE REG (32B)", "PC, LR, SP, R0-R12...", 145, BLUEBG, NEG),
        ("STACK DUMP (64B)", "16 слів стека аварії", 135, GREYBG, LINE),
        ("CRC32 (4B)", "Контрольна сума", 115, GRNBG, FIELD)
    ]
    bx = ly_x + 18
    by = ly_y + 45
    bh = 55
    for m_name, m_val, mw, mfill, mcol in mem_blocks:
        P.append(rect(bx, by, mw, bh, fill=mfill, stroke=mcol, sw=1.2, rx=4))
        P.append(text(bx + mw / 2, by + 20, m_name, size=9.5, color=mcol, bold=True))
        P.append(text(bx + mw / 2, by + 40, m_val, size=9.5, color=INK))
        bx += mw + 8

    P.append(text(ly_x + 20, ly_y + 125,
                  "Розміщення в Linker Script: .noinit (NOLOAD) : { *(.noinit*) } > RAM  — стартап-код не затирає нулями при ресеті!",
                  size=10, color=MUTED, bold=True, anchor="start"))

    # Підсумкова рамка
    fr, fw, fh = textbox(W / 2, 435,
                         "Чорна скринька перетворює раптовий крах на структурований звіт: адреса інструкції, стан шини, стековий контекст і причина ресету.",
                         size=11.5, bold=True, fill=GRNBG, stroke=FIELD)
    P.append(fr)

    render("img/crash-dump-lifecycle.svg", W, H, *P)


if __name__ == "__main__":
    fig_reset_reason_flags()
    fig_cortex_m_stack_frame()
    fig_crash_dump_lifecycle()
    print("OK: 3 figures created in img/")
