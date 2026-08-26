# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Завантажувач, який не можна закирпичити».
svgkit імпортуємо зі scripts/, вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

AMBER   = "#b08900"
AMBERBG = "#fdf6e3"
BLUEBG  = "#eaf0fd"
GRNBG   = "#e9f7ef"
REDBG   = "#fdecea"
GREYBG  = "#eef2f7"
PURPLE  = "#5b21b6"
PURPLEBG= "#ede9fe"


# ── 1. Однобанківське оновлення проти Dual-Bank A/B ──────────────────────────
def fig_single_vs_dual_bank():
    W, H = 960, 490
    P = [
        text(W / 2, 30, "Однобанківське оновлення проти Dual-Bank A/B", size=17, bold=True),
        text(W / 2, 50, "Чому перезапис на місці неминуче створює вікно фатальної вразливості до збою",
             size=11, color=MUTED, italic=True)
    ]

    # Верхня смуга: Однобанківське оновлення (In-Place)
    yT = 115
    P.append(fitbox(40, yT - 26, 260, 24, "ОДНОБАНКІВСЬКА СХЕМА (In-Place)", size=12, bold=True,
                    color=POS, fill=REDBG, stroke=POS))
    P.append(line(50, yT + 22, 910, yT + 22, color="#d0d5dd", sw=1.2))

    # Блоки верхньої смуги
    P.append(fitbox(50, yT, 170, 44, "1. Робоча v1.0\n(виконується в Flash)", size=10, bold=True,
                    color=FIELD, fill=GRNBG, stroke=FIELD))
    P.append(arrow(225, yT + 22, 265, yT + 22, color=LINE, sw=1.5))

    P.append(fitbox(270, yT, 180, 44, "2. Стирання Flash\n(0xFF у векторах/коді)", size=10, bold=True,
                    color=POS, fill=REDBG, stroke=POS))
    P.append(arrow(455, yT + 22, 495, yT + 22, color=LINE, sw=1.5))

    P.append(fitbox(500, yT, 180, 44, "3. Запис нової v2.0\n(обрив на 42%...) ⚡", size=10, bold=True,
                    color=AMBER, fill=AMBERBG, stroke=AMBER))
    P.append(arrow(685, yT + 22, 725, yT + 22, color=POS, sw=2.0))

    P.append(fitbox(730, yT, 180, 44, "💀 «ЦЕГЛИНА»\nВектори знищені, чіп мертвий", size=10, bold=True,
                    color=POS, fill=REDBG, stroke=POS))

    P.append(text(480, yT + 66, "Збій живлення або лінка посеред запису знищує стару прошивку до того, як записано нову",
                  size=10.5, color=POS, bold=True))

    # Нижня смуга: Dual-Bank A/B
    yB = 270
    P.append(fitbox(40, yB - 26, 260, 24, "АРХІТЕКТУРА DUAL-BANK (A / B)", size=12, bold=True,
                    color=FIELD, fill=GRNBG, stroke=FIELD))
    P.append(line(50, yB + 22, 910, yB + 22, color="#d0d5dd", sw=1.2))

    P.append(fitbox(50, yB, 210, 44, "Слот A (v1.0, Активний)\nПрацює, керує залізом", size=10, bold=True,
                    color=FIELD, fill=GRNBG, stroke=FIELD))

    P.append(arrow(265, yB + 22, 305, yB + 22, color=LINE, sw=1.5))

    P.append(fitbox(310, yB, 220, 44, "Слот B (v2.0, Пасивний)\nФоновий прийом байтів OTA", size=10, bold=True,
                    color=NEG, fill=BLUEBG, stroke=NEG))

    P.append(arrow(535, yB + 22, 575, yB + 22, color=LINE, sw=1.5))

    P.append(fitbox(580, yB, 150, 44, "Валідація образу\n(SHA-256 + ECDSA)", size=10, bold=True,
                    color=PURPLE, fill=PURPLEBG, stroke=PURPLE))

    P.append(arrow(735, yB + 22, 775, yB + 22, color=FIELD, sw=1.8))

    P.append(fitbox(780, yB, 130, 44, "Атомарний своп\nСлот B стає Active", size=10, bold=True,
                    color=FIELD, fill=GRNBG, stroke=FIELD))

    P.append(text(480, yB + 66, "Обрив на будь-якому етапі залишає Слот A неушкодженим; пристрій продовжує штатно працювати",
                  size=10.5, color=FIELD, bold=True))

    fr, w, h = textbox(W / 2, 445,
                       "В однобанківській схемі є фатальний момент напівстертої пам'яті. У Dual-Bank робочий код ніколи не перезаписується наживо.",
                       size=11.5, bold=True, fill=AMBERBG, stroke=AMBER)
    P.append(fr)
    render("img/single-vs-dual-bank.svg", W, H, *P)


# ── 2. Карта пам'яті та механізм VTOR ─────────────────────────────────────────
def fig_memory_layout_and_vtor():
    W, H = 960, 520
    P = [
        text(W / 2, 30, "Розподіл Flash-пам'яті та перемикання векторів VTOR", size=17, bold=True),
        text(W / 2, 50, "Ізоляція завантажувача, захист метаданих та передача керування між слотами",
             size=11, color=MUTED, italic=True)
    ]

    # Стовпчик Flash-пам'яті
    fx, fy, fw = 70, 75, 360
    sectors = [
        ("0x08000000", "Завантажувач (Bootloader)", "64 KB, апаратний захист від запису (WRP)", PURPLE, PURPLEBG, 54),
        ("0x08010000", "Сектор метаданих (Boot Metadata)", "16 KB, подвійний запис із CRC32 та версією", AMBER, AMBERBG, 48),
        ("0x08014000", "Слот A (Firmware Image A)", "480 KB: Header + Vector Table + Code", FIELD, GRNBG, 76),
        ("0x0808C000", "Слот B (Firmware Image B)", "480 KB: Header + Vector Table + Code", NEG, BLUEBG, 76),
        ("0x08104000", "NVS / Дані застосунку", "Пресет калібрувань, лог помилок", INK, GREYBG, 44),
    ]

    cur_y = fy
    for addr, name, desc, col, bg, sh in sectors:
        P.append(fitbox(fx, cur_y, fw, sh, f"{name}\n({desc})", size=10, bold=True, color=col, fill=bg, stroke=col))
        P.append(text(fx - 10, cur_y + 16, addr, size=9, color=MUTED, anchor="end", bold=True))
        cur_y += sh + 6

    # Права частина: Схема стрибка та переналаштування VTOR
    rx, ry, rw = 490, 75, 420
    P.append(fitbox(rx, ry, rw, 38, "Регістр SCB->VTOR (Vector Table Offset)", size=11.5, bold=True,
                    color=PURPLE, fill=PURPLEBG, stroke=PURPLE))

    # Стрілки від слотів до VTOR
    P.append(line(fx + fw, 225, rx - 20, 225, color=FIELD, sw=1.8, dash="4 3"))
    P.append(line(rx - 20, 225, rx - 20, 94, color=FIELD, sw=1.8, dash="4 3"))
    P.append(arrow(rx - 20, 94, rx, 94, color=FIELD, sw=1.8))
    P.append(text(fx + fw + 15, 215, "Активний Слот A (0x08014000)", size=9, color=FIELD, anchor="start", bold=True))

    steps_y = 126
    jump_steps = [
        ("1. Перевірка цілісності", "Хеш SHA-256 + підпис Ed25519 валідні"),
        ("2. Очищення периферії", "Вимкнення всіх переривань (NVIC), скидання SysTick"),
        ("3. Перенесення векторів", "SCB->VTOR = Target_Slot_Base + 0x200 (Offset)"),
        ("4. Встановлення стека", "__set_MSP(*(uint32_t*)Target_Slot_Base)"),
        ("5. Стрибок у прошивку", "Reset_Handler() за адресою *(uint32_t*)(Base + 4)"),
    ]

    for i, (st_t, st_d) in enumerate(jump_steps):
        P.append(fitbox(rx, steps_y + i * 48, rw, 40, f"{st_t}: {st_d}", size=9.5, bold=False,
                        color=INK, fill=FILL, stroke=LINE))

    fr, w, h = textbox(W / 2, 475,
                       "Завантажувач ізольований у захищеному секторі. Передача керування вимагає повного скидання переривань і перевстановлення VTOR.",
                       size=11.5, bold=True, fill=GRNBG, stroke=FIELD)
    P.append(fr)
    render("img/memory-layout-and-vtor.svg", W, H, *P)


# ── 3. Автомат пробного запуску (Trial Boot FSM) ──────────────────────────────
def fig_trial_boot_fsm():
    W, H = 960, 490
    P = [
        text(W / 2, 30, "Скінченний автомат пробного запуску та відкату (Trial Boot FSM)", size=17, bold=True),
        text(W / 2, 50, "Як система автоматично відновлюється, якщо нова прошивка містить логічний збій або зависає",
             size=11, color=MUTED, italic=True)
    ]

    # Стан 1: CONFIRMED (Поточний робочий)
    P.append(fitbox(60, 135, 220, 70, "СТАН: CONFIRMED\n(Слот A стабільний)\nШтатна робота пристрою",
                    size=11, bold=True, color=FIELD, fill=GRNBG, stroke=FIELD))

    # Стрілка OTA запису
    P.append(arrow(280, 170, 410, 170, color=NEG, sw=2.0))
    P.append(text(345, 155, "OTA Запис у Слот B", size=10, color=NEG, bold=True))
    P.append(text(345, 190, "Хеш і підпис OK", size=9.5, color=MUTED, italic=True))

    # Стан 2: TRIAL (Пробний запуск)
    P.append(fitbox(410, 135, 240, 70, "СТАН: TRIAL\n(Слот B у пробному режимі)\nЛічильник спроб = 1 з 3",
                    size=11, bold=True, color=AMBER, fill=AMBERBG, stroke=AMBER))

    # Гілка Успіху: підтвердження працездатності
    P.append(arrow(650, 170, 770, 170, color=FIELD, sw=2.2))
    P.append(text(710, 155, "Самотест OK", size=10, color=FIELD, bold=True))
    P.append(text(710, 190, "firmware_mark_valid()", size=9, color=FIELD, bold=True))

    # Стан 3: NEW CONFIRMED
    P.append(fitbox(770, 135, 150, 70, "НОВИЙ СТАН:\nCONFIRMED\n(Слот B активний)",
                    size=11, bold=True, color=FIELD, fill=GRNBG, stroke=FIELD))

    # Гілка Збою: Watchdog / Panic / HardFault
    P.append(line(530, 205, 530, 285, color=POS, sw=2.0))
    P.append(arrow(530, 285, 530, 305, color=POS, sw=2.0))
    P.append(text(540, 250, "Креш / Зависання / Watchdog ⚡", size=10, color=POS, anchor="start", bold=True))
    P.append(text(540, 270, "Інкремент лічильника спроб (спроба 2, 3...)", size=9.5, color=MUTED, anchor="start", italic=True))

    # Стан 4: RETRY / FAILED ROLLBACK
    P.append(fitbox(390, 305, 280, 65, "СТАН: FAILED (ВІДКАТ)\nВичерпано ліміт спроб (> 3)\nСлот B блокується",
                    size=11, bold=True, color=POS, fill=REDBG, stroke=POS))

    # Стрілка відкату назад у Слот A
    P.append(line(390, 337, 170, 337, color=POS, sw=2.0))
    P.append(arrow(170, 337, 170, 205, color=POS, sw=2.0))
    P.append(text(280, 325, "Автоматичний відкат у Слот A", size=10.5, color=POS, bold=True))
    P.append(text(280, 355, "Завантаження стабільної версії", size=9.5, color=MUTED, italic=True))

    fr, w, h = textbox(W / 2, 440,
                       "Якщо нова версія зависає в HardFault, Watchdog перезавантажує мікроконтролер, а завантажувач повертає попередній перевірений слот.",
                       size=11.5, bold=True, fill=PURPLEBG, stroke=PURPLE)
    P.append(fr)
    render("img/trial-boot-fsm.svg", W, H, *P)


if __name__ == "__main__":
    fig_single_vs_dual_bank()
    fig_memory_layout_and_vtor()
    fig_trial_boot_fsm()
    print("Всі 3 фігури згенеровано успішно.")
