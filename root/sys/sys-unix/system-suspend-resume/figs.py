# -*- coding: utf-8 -*-
"""Фігури до теми «Призупинення й пробудження системи: suspend to RAM у ядрі»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_BG = "#e6f5ec"
RED_BG   = "#fdecea"
GREY_BG  = "#eef0f3"
WARM_BG  = "#fff4e0"
BLUE_BG  = "#eaf0fd"
GOLD     = "#b8860b"


# ── 1. Повний конвеєр призупинення й пробудження (Suspend / Resume Pipeline) ──
def fig_suspend_resume_phases():
    W, H = 1380, 840
    P = []

    # Заголовки колонок (Фази сну та пробудження)
    LX = 360
    RX = 1020
    P.append(text(LX, 40, "Фаза 1–4: Перехід у сон (Suspend)", size=17, bold=True, color=POS))
    P.append(text(RX, 40, "Фаза 5–8: Пробудження (Resume)", size=17, bold=True, color=FIELD))

    # Лінія розділу
    P.append(line(690, 25, 690, 780, color=MUTED, sw=1.2, dash="6,6"))

    # Блоки призупинення (ліва колонка)
    suspend_steps = [
        (85, "1. Запит користувача", "echo mem > /sys/power/state (перевірка wakeup_count)", WARM_BG, GOLD),
        (175, "2. Заморожування процесів (Freezer)", "freeze_processes() [юзерспейс] → freeze_kernel_threads()", GREY_BG, LINE),
        (280, "3. Каскад DPM (Драйвери пристроїв)", "prepare() → suspend() → suspend_late() → suspend_noirq()", BLUE_BG, NEG),
        (395, "4. Зупинка CPU та переривань", "disable_nonboot_cpus() → syscore_suspend() → local_irq_disable()", WARM_BG, GOLD),
        (510, "5. Архітектурний сон (Arch sleep)", "Збереження CR3/GDT/MSR → wbinvd (кеш) → DRAM Self-Refresh", RED_BG, POS),
        (625, "6. Фізичний стан S3 (ACPI S3)", "Запис PM1a/b_CNT.SLP_EN → знеструмлення платформи (лише 5VSB/RAM)", RED_BG, POS),
    ]

    for y, title, desc, bg, st in suspend_steps:
        b, bw, bh = textbox(LX, y, [title, desc], size=13.5, fill=bg, stroke=st, sw=1.8, min_w=580)
        P.append(b)

    for i in range(len(suspend_steps) - 1):
        y1 = suspend_steps[i][0] + 28
        y2 = suspend_steps[i+1][0] - 28
        P.append(arrow(LX, y1, LX, y2, color=POS, sw=2))

    # Центральний вузол: Сигнал пробудження
    WY = 730
    wb, wbw, wbh = textbox(690, WY, ["ПОДІЯ ПРОБУДЖЕННЯ (Wakeup Event)", "RTC alarm / Кнопка живлення / PCIe PME# / GPIO / Клавіатура"],
                           size=14, bold=True, fill=WARM_BG, stroke=POS, sw=2.2, min_w=620)
    P.append(wb)

    # Стрілка від стану S3 до сигналу пробудження
    P.append(arrow(LX, 660, 690 - wbw/2 + 30, WY, color=POS, sw=2))
    # Стрілка від сигналу пробудження до першого кроку відновлення
    P.append(arrow(690 + wbw/2 - 30, WY, RX, 660, color=FIELD, sw=2))

    # Блоки пробудження (права колонка)
    resume_steps = [
        (85, "12. Робота відновлена", "Всі процеси розморожено, планувальник активний, I/O розблоковано", GREEN_BG, FIELD),
        (175, "11. Розморожування задач (Thaw)", "thaw_processes() [ядерні потоки → юзерспейс]", GREY_BG, LINE),
        (280, "10. Каскад DPM (Драйвери пристроїв)", "resume_noirq() → resume_early() → resume() → complete()", BLUE_BG, NEG),
        (395, "9. Запуск вторинних CPU та IRQ", "local_irq_enable() → syscore_resume() → enable_nonboot_cpus()", WARM_BG, GOLD),
        (510, "8. Відновлення архітектурного стану", "CR3/GDT/IDT/MSR відновлено → повернення в ядро (Waking Vector)", GREEN_BG, FIELD),
        (625, "7. Спрацьовування BIOS / Firmware", "Вмикання шин живлення → зняття DRAM Self-Refresh → FACS vector", GREEN_BG, FIELD),
    ]

    for y, title, desc, bg, st in resume_steps:
        b, bw, bh = textbox(RX, y, [title, desc], size=13.5, fill=bg, stroke=st, sw=1.8, min_w=580)
        P.append(b)

    # Стрілки в правій колонці йдуть від кроку 7 (знизу) до кроку 12 (вгору)
    for i in range(len(resume_steps) - 1, 0, -1):
        y1 = resume_steps[i][0] - 28
        y2 = resume_steps[i-1][0] + 28
        P.append(arrow(RX, y1, RX, y2, color=FIELD, sw=2))

    P.append(text(W/2, 810, "Повний цикл: від запису в sysfs крізь апаратний сон S3 до відновлення робочого стану планувальника",
                  size=13, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "suspend-resume-phases.svg"), W, H, *P,
           title="Повний конвеєр призупинення й пробудження системи в ядрі Linux")


# ── 2. Порівняння станів сну ACPI (S0, S0ix, S3, S4) ─────────────────────────
def fig_acpi_sleep_states_comparison():
    W, H = 1360, 680
    P = []

    # Заголовок таблиці
    P.append(text(W/2, 40, "Стани енергозбереження системи: від активного стану до глибокого сну", size=16, bold=True))

    cols = [
        ("S0 (Working)", 170, GREEN_BG, FIELD),
        ("S0ix (Modern Standby)", 470, BLUE_BG, NEG),
        ("S3 (Suspend to RAM)", 800, WARM_BG, GOLD),
        ("S4 (Hibernation)", 1130, RED_BG, POS),
    ]

    # Заголовки стовпців
    for name, cx, bg, st in cols:
        b, bw, bh = textbox(cx, 90, name, size=15, bold=True, fill=bg, stroke=st, sw=2, min_w=280)
        P.append(b)

    rows = [
        ("Режим у Linux (/sys/power/state)", 170, [
            "active (робочий)",
            "freeze (s2idle)",
            "mem (suspend-to-RAM)",
            "disk (hibernation)"
        ]),
        ("Стан процесора (CPU)", 265, [
            "C0–C10 (активний / cpuidle)",
            "SoC Power Gating (C10 / Package C-state)",
            "Вимкнено (живлення знято, контекст у RAM)",
            "Вимкнено (живлення знято, контекст на диску)"
        ]),
        ("Стан пам'яті (RAM)", 360, [
            "Активна (постійний рефреш)",
            "Self-Refresh коротко / низьке живлення",
            "Self-Refresh (автономне утримання)",
            "Знеструмлена (образ скинуто в Swap)"
        ]),
        ("Шини живлення платформи", 455, [
            "Всі увімкнені (+12V, +5V, +3.3V, Vcore)",
            "Vcore/GPU знеструмлені, PMIC активний",
            "Лише +5VSB та VDDQ (RAM retention)",
            "Повне знеструмлення (0 Вт споживання)"
        ]),
        ("Час пробудження (Latency)", 550, [
            "0 мс (миттєво)",
            "10–100 мс (без участі BIOS)",
            "500–2000 мс (крізь BIOS POST / FACS)",
            "5000–20000 мс (завантаження образу з SSD)"
        ]),
    ]

    for label, y, vals in rows:
        P.append(text(30, y - 25, label, size=13, bold=True, color=INK, anchor="start"))
        P.append(line(30, y - 12, W - 30, y - 12, color=MUTED, sw=1, dash="4,4"))

        for i, (_, cx, bg, st) in enumerate(cols):
            b, bw, bh = textbox(cx, y + 16, vals[i], size=12.5, fill=FILL, stroke=LINE, sw=1.2, min_w=280)
            P.append(b)

    P.append(text(W/2, 650, "S0ix забезпечує швидке пробудження під контролем ОС; S3 забезпечує мінімальне споживання ціною скидання контексту CPU",
                  size=13, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "acpi-sleep-states-comparison.svg"), W, H, *P,
           title="Порівняння станів енергозбереження ACPI: S0, S0ix, S3 та S4")


# ── 3. Чотириетапний каскад викликів dev_pm_ops (DPM Callbacks Flow) ──────────
def fig_dpm_callbacks_flow():
    W, H = 1320, 720
    P = []

    P.append(text(W/2, 40, "Чотири фази зворотних викликів dev_pm_ops та контекст їх виконання", size=16, bold=True))

    phases = [
        (130, "1. Фаза prepare() / complete()",
         "Блокування реєстрації нових дочірніх пристроїв у системі",
         "Юзерспейс заморожено, ядерні потоки сплять, локальні IRQ увімкнені, контекст дозволяє сон (can sleep)",
         WARM_BG, GOLD),
        (260, "2. Фаза suspend() / resume()",
         "Головна фаза: зупинка DMA-кілець, скидання черг передачі, переведення чіпів у низьке живлення",
         "Локальні IRQ увімкнені, виклики можуть блокуватися (mutex, msleep), доступні всі шини та периферія",
         GREEN_BG, FIELD),
        (390, "3. Фаза suspend_late() / resume_early()",
         "Обробка низькорівневих шин, таймерів та системних доменів живлення (PM domains / genpd)",
         "Більшість пристроїв уже приспано, залежності між шинами суворо контролюються, IRQ ще активні",
         BLUE_BG, NEG),
        (520, "4. Фаза suspend_noirq() / resume_noirq()",
         "Остаточне збереження конфігураційних регістрів, переведення контролерів у D3cold/D3hot",
         "Переривання пристроїв вимкнені (disable_device_irq), локальні IRQ ядра вимкнені — код НЕ МАЄ права спати!",
         RED_BG, POS),
    ]

    for y, title, task, ctx, bg, st in phases:
        P.append(text(60, y - 22, title, size=15, bold=True, color=st, anchor="start"))
        b1, bw1, bh1 = textbox(440, y + 16, ["Призначення:", task], size=13, fill=bg, stroke=st, sw=1.6, min_w=580)
        P.append(b1)
        b2, bw2, bh2 = textbox(1020, y + 16, ["Контекст і обмеження:", ctx], size=12.5, fill=FILL, stroke=LINE, sw=1.4, min_w=520)
        P.append(b2)

    # Стрілка порядку викликів під час Suspend (зверху вниз)
    P.append(arrow(28, 120, 28, 550, color=POS, sw=2.2))
    P.append(text(18, 335, "SUSPEND (знизу вгору по дереву пристроїв)", size=12, color=POS, anchor="middle", bold=True))

    # Стрілка порядку викликів під час Resume (знизу вгору)
    P.append(arrow(W - 28, 550, W - 28, 120, color=FIELD, sw=2.2))
    P.append(text(W - 18, 335, "RESUME (згори вниз по дереву пристроїв)", size=12, color=FIELD, anchor="middle", bold=True))

    P.append(text(W/2, 680, "Помилка на будь-якому етапі suspend негайно запускає симетричний зворотний відкіт виконаних фаз",
                  size=13, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "dpm-callbacks-flow.svg"), W, H, *P,
           title="Послідовність викликів dev_pm_ops: prepare, suspend, suspend_late, suspend_noirq")


# ── 4. Перегони пробудження та атомарний лічильник wakeup_count ──────────────
def fig_wakeup_count_race():
    W, H = 1300, 620
    P = []

    P.append(text(W/2, 40, "Запобігання перегонам: як /sys/power/wakeup_count блокує втрачений сон", size=16, bold=True))

    # Ліва колонка: Перегони без лічильника (Втрата події)
    P.append(text(340, 80, "БЕЗ лічильника: Подія зникає в момент засинання", size=14.5, bold=True, color=POS))
    P.append(rect(60, 105, 560, 450, fill=RED_BG, stroke=POS, sw=1.5))

    bad_events = [
        (140, "1. Демон сну вирішує: система простоює", "Запуск переходу в сон..."),
        (220, "2. Користувач натискає клавішу!", "Подія надходить у чергу переривань"),
        (300, "3. Демон пише: echo mem > /sys/power/state", "Ядро починає процес призупинення"),
        (380, "4. Freezer заморожує процеси", "Подію клавіатури НЕ прочитано застосунком!"),
        (460, "5. Система засинає в стан S3", "Результат: ноутбук заснув, проігнорувавши дію!"),
    ]

    for y, title, desc in bad_events:
        b, bw, bh = textbox(340, y, [title, desc], size=13, fill=FILL, stroke=LINE, sw=1.2, min_w=500)
        P.append(b)

    # Права колонка: Атомарна перевірка з wakeup_count
    P.append(text(960, 80, "З wakeup_count: Атомарне скасування призупинення", size=14.5, bold=True, color=FIELD))
    P.append(rect(680, 105, 560, 450, fill=GREEN_BG, stroke=FIELD, sw=1.5))

    good_events = [
        (140, "1. Демон читає /sys/power/wakeup_count", "Отримано поточне значення: count = 1420"),
        (220, "2. Користувач натискає клавішу!", "Драйвер викликає pm_wakeup_event() → count = 1421"),
        (300, "3. Демон пише: echo 1420 > wakeup_count", "Ядро порівнює: 1420 ≠ 1421 (перевірка не пройшла!)"),
        (380, "4. Запис завершується помилкою -EINVAL", "Спроба призупинення негайно скасовується!"),
        (460, "5. Юзерспейс обробляє подію клавіатури", "Результат: подія не втрачена, система лишається активною"),
    ]

    for y, title, desc in good_events:
        b, bw, bh = textbox(960, y, [title, desc], size=13, fill=FILL, stroke=LINE, sw=1.2, min_w=500)
        P.append(b)

    P.append(text(W/2, 585, "Атомарний інтерфейс wakeup_count гарантує відсутність вікна перегонів між простором користувача та ядром",
                  size=13, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "wakeup-count-race.svg"), W, H, *P,
           title="Атомарна синхронізація через /sys/power/wakeup_count та блокування перегонів")


if __name__ == "__main__":
    fig_suspend_resume_phases()
    fig_acpi_sleep_states_comparison()
    fig_dpm_callbacks_flow()
    fig_wakeup_count_race()
    print("All figures successfully generated.")
