# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори ролей
ARM   = "#1e8449"   # стандарт ARM — однаково скрізь (зелений)
ARMF  = "#d5f5e3"
VEND  = "#b9770e"   # заповнює виробник (амбра)
VENDF = "#fdf3d6"
CORE  = "#7d3c98"   # ядро (фіолетовий, як у cortex-m)
COREF = "#f0e6fa"
BLUE  = "#1a5276"
BLUEF = "#d6eaf8"


# ── cmsis-layers: вертикальний стек шарів ПЗ ─────────────────────────────────
# Ідея: CMSIS — це кілька шарів заголовків між застосунком і залізом. Зелені шари
# (абстракція компілятора + CMSIS-Core) дає ARM — вони однакові скрізь; амбровий
# шар пристрою заповнює виробник за шаблоном CMSIS.

def fig_cmsis_layers():
    W, H = 760, 596
    p = []
    bx, bw = 110, 540

    # легенда
    ly = 52
    p.append(rect(bx, ly - 12, 18, 18, fill=ARMF, stroke=ARM, sw=1.6, rx=3))
    p.append(text(bx + 26, ly + 2, "= стандарт ARM (однаково на кожному чипі)", size=11.5, color=INK, anchor="start"))
    p.append(rect(bx + 350, ly - 12, 18, 18, fill=VENDF, stroke=VEND, sw=1.6, rx=3))
    p.append(text(bx + 378, ly + 2, "= заповнює виробник", size=11.5, color=INK, anchor="start"))

    top, bh, gap = 82, 80, 12
    # (заголовок, деталь, заливка, обведення)
    layers = [
        ("Ваш застосунок", "#include \"stm32f4xx.h\"  — і весь шар нижче доступний", "#eef0f2", MUTED),
        ("Шар пристрою — stm32f4xx.h  (виробник)",
         "структури периферії · enum IRQn_Type · SystemInit() · SystemCoreClock", VENDF, VEND),
        ("CMSIS-Core — core_cm4.h  (ARM)",
         "структури SCB · NVIC · SysTick   ·   NVIC_EnableIRQ() · SysTick_Config()", ARMF, ARM),
        ("Абстракція компілятора — cmsis_compiler.h  (ARM)",
         "→ cmsis_gcc / cmsis_armclang / cmsis_iccarm   ·   __disable_irq() · __DSB()", ARMF, ARM),
    ]
    for i, (h1, h2, fill, col) in enumerate(layers):
        y = top + i * (bh + gap)
        p.append(rect(bx, y, bw, bh, fill=fill, stroke=col, sw=2.0))
        p.append(text(bx + bw / 2, y + 30, h1, size=13, color=col, bold=True))
        p.append(text(bx + bw / 2, y + 56, h2, size=11, color=INK))

    # шар заліза — двоколірний
    y = top + 4 * (bh + gap)
    half = bw / 2
    p.append(rect(bx, y, half, bh, fill=COREF, stroke=CORE, sw=2.0, rx=0))
    p.append(mtext(bx + half / 2, y + 34, "ядро Cortex-M\n(однакове)", size=12, color=CORE, bold=True))
    p.append(rect(bx + half, y, half, bh, fill=VENDF, stroke=VEND, sw=2.0, rx=0))
    p.append(mtext(bx + half + half / 2, y + 34, "периферія виробника\n(різна)", size=12, color=VEND, bold=True))
    p.append(text(bx + bw / 2, y - gap / 2 - 1, "ЗАЛІЗО", size=10, color=MUTED))

    p.append(text(W / 2, H - 16,
                  "Ти пишеш зверху; кожен шар нижче ховає одну відмінність — компілятор, тоді ядро, тоді периферію",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "cmsis-layers.svg"), W, H, *p,
           title="Шари CMSIS: від застосунку до заліза")


# ── register-struct: структура C, накладена на регістри в пам'яті ────────────
# Ідея: device-заголовок CMSIS описує периферію як struct із volatile-полів; поле
# за зміщенням лягає на регістр за адресою (база + зміщення). Тому GPIOA->BSRR — це
# просто запис за фіксованою адресою.

def fig_register_struct():
    W, H = 760, 500
    p = []
    top, rh = 96, 40
    # (адреса, регістр, зміщення, поле-коментар)
    rows = [
        ("0x4002_0000", "MODER",   "0x00"),
        ("0x4002_0004", "OTYPER",  "0x04"),
        ("0x4002_0008", "OSPEEDR", "0x08"),
        ("0x4002_000C", "PUPDR",   "0x0C"),
        ("0x4002_0010", "IDR",     "0x10"),
        ("0x4002_0014", "ODR",     "0x14"),
        ("0x4002_0018", "BSRR",    "0x18"),
    ]
    # ліва колонка — пам'ять
    mx, mw = 70, 250
    p.append(text(mx + mw / 2, top - 18, "Пам'ять периферії (адреси)", size=12, color=BLUE, bold=True))
    # права колонка — struct
    sx, sw_ = 440, 250
    p.append(text(sx + sw_ / 2, top - 18, "struct GPIO_TypeDef", size=12, color=CORE, bold=True))

    for i, (addr, reg, off) in enumerate(rows):
        y = top + i * rh
        hot = reg in ("MODER", "BSRR")
        # пам'ять
        p.append(rect(mx, y, mw, rh - 6, fill=BLUEF if hot else "#eef4ff", stroke=BLUE, sw=1.3, rx=0))
        p.append(text(mx + 10, y + (rh - 6) / 2 + 4, addr, size=11, color=MUTED, anchor="start"))
        p.append(text(mx + mw - 10, y + (rh - 6) / 2 + 4, reg, size=11.5, color=INK, anchor="end", bold=hot))
        # struct
        p.append(rect(sx, y, sw_, rh - 6, fill=COREF if hot else "#f7f2fb", stroke=CORE, sw=1.3, rx=0))
        p.append(text(sx + 10, y + (rh - 6) / 2 + 4,
                      "volatile uint32_t %s;" % reg, size=10.5, color=INK, anchor="start"))
        p.append(text(sx + sw_ - 8, y + (rh - 6) / 2 + 4, "// +" + off, size=9.5, color=MUTED, anchor="end"))
        # конектор (горизонтальний, не перетинається)
        p.append(line(mx + mw, y + (rh - 6) / 2, sx, y + (rh - 6) / 2, color="#c9ced4", sw=1.0))

    yb = top + len(rows) * rh + 6
    p.append(text(W / 2, yb + 6, "#define GPIOA  ((GPIO_TypeDef*) 0x4002_0000)",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, yb + 30, "GPIOA->BSRR = 1u << 5;      →   запис у 0x4002_0018",
                  size=12, color=BLUE))
    p.append(text(W / 2, yb + 54,
                  "Поле за зміщенням у struct лягає на регістр за адресою — доступ стає типованим і названим",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "register-struct.svg"), W, H, *p,
           title="Регістр як поле структури")


# ── portability-boundary: що CMSIS робить переносним, а що ні ─────────────────
# Ідея: CMSIS-Core уніфікує ЯДРО (NVIC/SysTick/SCB/інтринсики) — воно однакове
# скрізь; периферію виробника він лише типує, спільного API не дає — це окремий шар.

def fig_portability_boundary():
    W, H = 760, 452
    p = []
    # чип угорі по центру
    cw, chh = 170, 50
    cx0 = W / 2 - cw / 2
    p.append(rect(cx0, 52, cw, chh, fill="#fbfbfc", stroke=INK, sw=1.8, rx=8))
    p.append(mtext(W / 2, 72, "Cortex-M чип\nядро + периферія", size=11, color=INK))

    py, ph = 150, 232
    # ліва панель — ядро (переносне)
    lx, lw = 60, 300
    p.append(rect(lx, py, lw, ph, fill=ARMF, stroke=ARM, sw=2.0, rx=8))
    p.append(text(lx + lw / 2, py + 28, "Ядро ARM — переносне", size=13, color=ARM, bold=True))
    p.append(text(lx + lw / 2, py + 46, "CMSIS-Core дає той самий код скрізь", size=10.5, color=MUTED))
    left = ["NVIC — контролер переривань", "SysTick — таймер ядра",
            "SCB · MPU · FPU", "інтринсики __DSB / __WFI / __NOP"]
    yy = py + 78
    for c in left:
        p.append(text(lx + 20, yy, "✓  " + c, size=11.5, color="#186a3b", anchor="start"))
        yy += 34
    p.append(mtext(lx + lw / 2, py + ph - 24, "той самий вихідний код\nна ST, NXP, Nordic, RP2040",
                   size=10.5, color="#186a3b", bold=True))

    # права панель — периферія (не переносна)
    rx, rw = 400, 300
    p.append(rect(rx, py, rw, ph, fill=VENDF, stroke=VEND, sw=2.0, rx=8))
    p.append(text(rx + rw / 2, py + 28, "Периферія виробника", size=13, color=VEND, bold=True))
    p.append(text(rx + rw / 2, py + 46, "CMSIS дає лише ТИПОВАНИЙ доступ", size=10.5, color=MUTED))
    right = ["GPIO · UART · SPI · таймери", "розкладка бітів у ST ≠ NXP",
             "структура регістрів — своя в кожного"]
    yy = py + 78
    for c in right:
        p.append(text(rx + 20, yy, "•  " + c, size=11.5, color="#7a5200", anchor="start"))
        yy += 34
    p.append(mtext(rx + rw / 2, py + ph - 30, "спільний API периферії —\nце CMSIS-Driver / HAL\n(окремий шар, не CMSIS-Core)",
                   size=10.5, color="#7a5200", bold=True))

    # стрілки від чипа
    p.append(arrow(W / 2 - 30, 52 + chh, lx + lw / 2, py, color=MUTED, sw=1.4))
    p.append(arrow(W / 2 + 30, 52 + chh, rx + rw / 2, py, color=MUTED, sw=1.4))

    p.append(text(W / 2, H - 14,
                  "Стандарт уніфікує спільне (ядро) і дає спільну ФОРМУ для різного (типовані регістри)",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "portability-boundary.svg"), W, H, *p,
           title="Межа переносності: ядро проти периферії")


# ── cmsis-family: родина CMSIS, згрупована за родом ──────────────────────────
# Ідея: «CMSIS» — не одне, а кілька різних за природою речей: код у прошивку,
# спільні API, файлові формати, прошивка пробника. Групування знімає плутанину.

def fig_cmsis_family():
    W, H = 824, 470
    p = []
    gy, gh = 74, 322
    cols = [
        (30,  "Код у прошивку", ARM, ARMF,
         [("CMSIS-Core", "доступ до ядра"),
          ("CMSIS-DSP", "FIR · FFT · матриці"),
          ("CMSIS-NN", "нейромережеві ядра")]),
        (230, "Спільні API", BLUE, BLUEF,
         [("CMSIS-RTOS2", "osThreadNew, osDelay"),
          ("CMSIS-Driver", "UART/SPI/I2C однаково")]),
        (430, "Формати · специфікації", VEND, VENDF,
         [("CMSIS-SVD", "XML усіх регістрів"),
          ("CMSIS-Pack", "пакет підтримки чипа")]),
        (630, "Прошивка пробника", CORE, COREF,
         [("CMSIS-DAP", "пробник ↔ порт DAP")]),
    ]
    cw = 164
    for gx, gtitle, col, fill, members in cols:
        p.append(rect(gx, gy, cw, gh, fill="#ffffff", stroke=col, sw=2.0, rx=8))
        p.append(fitbox(gx + 8, gy + 10, cw - 16, 40, gtitle, size=12, bold=True,
                        color=col, fill=fill, stroke=col, sw=1.4, rx=6))
        yy = gy + 66
        for name, role in members:
            p.append(rect(gx + 14, yy, cw - 28, 58, fill=fill, stroke=col, sw=1.4, rx=6))
            p.append(text(gx + cw / 2, yy + 24, name, size=12, color=col, bold=True))
            p.append(text(gx + cw / 2, yy + 44, role, size=9.5, color=INK))
            yy += 74

    p.append(text(W / 2, H - 16,
                  "CMSIS 6 — кожен модуль окремим репозиторієм на GitHub (відкрите врядування)",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "cmsis-family.svg"), W, H, *p,
           title="Родина CMSIS: чотири різні за природою частини")


# ── cmsis-timeline: дуга народження й дозрівання стандарту (для hist-вставки) ──
# Ідея: CMSIS народжується проти роздроблення тулчейнів і виробників (2008) і за
# 16 років дозріває у федерацію модулів (CMSIS 6, 2024). Вертикальна лінія часу:
# ліворуч — коли, праворуч — що; зелена крапка-2008 більша (момент народження).

def fig_cmsis_timeline():
    W, H = 860, 760
    p = []
    spine_x = 250
    y0, dy = 120, 108
    p.append(line(spine_x, y0 - 30, spine_x, y0 + 5 * dy + 30, color="#c9ced4", sw=3))

    # (рік, підпис-коли, колір, заливка, заголовок, [рядки опису])
    miles = [
        ("2004", "19 жовтня", CORE, COREF, "Cortex-M3: ядро стає однаковим",
         ["NVIC, SysTick і їхні адреси входять в архітектуру;",
          "кремній — Luminary (2006), STM32 (2007), далі решта"]),
        ("2005", "28 жовтня", BLUE, BLUEF, "ARM купує Keil",
         ["ARM здобуває людей, що 20 років жили в зоопарку",
          "заголовків 8051 — і мотив задати програмний стандарт"]),
        ("2008", "12 листоп.", ARM, ARMF, "CMSIS 1.0 · ядро CMSIS-Core",
         ["ARM + Atmel · IAR · Keil · Luminary · Micrium · NXP · SEGGER · ST",
          "один C-інтерфейс до ядра — на кожному чипі й компіляторі"]),
        ("2009–14", "CMSIS 2–4", VEND, VENDF, "Родина розростається",
         ["DSP · SVD · Pack · DAP · RTOS · Driver — кожен модуль",
          "закриває свій фронт роздроблення; під Pack уже 16 партнерів"]),
        ("2016+", "CMSIS 5", CORE, COREF, "«Cortex» → «Common»",
         ["GitHub і ліцензія Apache 2.0; стандарт виходить за межі",
          "Cortex-M на молодші Cortex-A — назва «Cortex» більше не точна"]),
        ("2023-24", "CMSIS 6", ARM, ARMF, "Модульна федерація",
         ["монорепо розбито на окремі репозиторії GitHub",
          "з відкритим врядуванням — кожен модуль сам по собі"]),
    ]
    bx, bw, bh = 292, 546, 74
    for i, (d1, d2, col, fill, title, desc) in enumerate(miles):
        y = y0 + i * dy
        # колонка «коли» — праворуч вирівняна, ліворуч від хребта
        p.append(text(spine_x - 28, y - 3, d1, size=13, color=col, bold=True, anchor="end"))
        if d2:
            p.append(text(spine_x - 28, y + 14, d2, size=10.5, color=MUTED, anchor="end"))
        # конектор і крапка (крапка народження — більша, зелена)
        p.append(line(spine_x, y, bx, y, color="#c9ced4", sw=1.4))
        big = (i == 2)
        p.append(circle(spine_x, y, 11 if big else 7, fill=fill, stroke=col, sw=2.4 if big else 2))
        # картка «що»
        p.append(rect(bx, y - bh / 2, bw, bh, fill="#ffffff", stroke=col, sw=1.8, rx=8))
        p.append(text(bx + 16, y - bh / 2 + 23, title, size=13.5, color=col, bold=True, anchor="start"))
        yy = y - bh / 2 + 44
        for ln in desc:
            p.append(text(bx + 16, yy, ln, size=10.5, color=INK, anchor="start"))
            yy += 16

    p.append(text(W / 2, H - 16,
                  "Стандарт приходить через чотири роки після ядра — вирівнювати те, що вже встигло розійтися",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "cmsis-timeline.svg"), W, H, *p,
           title="Лінія часу CMSIS: від купівлі Keil до модульної федерації")


# ── reg-layout-check: одне забуте слово зсуває всю решту структури ───────────
# Ідея (для proj-вставки): карта RCC має справжні діри. Якщо не оголосити поля-
# заглушки, кожне наступне поле з'їжджає на 4 байти — і запис у AHB1ENR фізично
# потрапляє в APB2RSTR. _Static_assert ловить це на етапі компіляції.

def fig_reg_layout_check():
    W, H = 900, 592
    p = []
    BAD, BADF = "#c0392b", "#fdecea"
    OKC, OKF = "#1e8449", "#eafaf0"

    # (зміщення, карта, наївна структура, правильна, чи розійшлося)
    rows = [
        ("0x00–0x10", "CR · PLLCFGR · CFGR · CIR", "ті самі поля", "ті самі поля", False),
        ("0x14", "AHB2RSTR", "AHB2RSTR", "AHB2RSTR", False),
        ("0x18", "AHB3RSTR", "AHB3RSTR", "AHB3RSTR", False),
        ("0x1C", "— зарезервовано —", "APB1RSTR", "uint32_t RESERVED0", True),
        ("0x20", "APB1RSTR", "APB2RSTR", "APB1RSTR", True),
        ("0x24", "APB2RSTR", "AHB1ENR", "APB2RSTR", True),
        ("0x28", "— зарезервовано —", "порожньо", "uint32_t RESERVED1[0]", True),
        ("0x2C", "— зарезервовано —", "порожньо", "uint32_t RESERVED1[1]", True),
        ("0x30", "AHB1ENR", "порожньо", "AHB1ENR", True),
    ]

    ox, ow = 34, 84            # колонка зміщень
    mx, mw = 126, 216          # карта з даташита
    nx, nw = 356, 244          # наївна структура
    cx, cw = 616, 252          # правильна структура
    top, rh = 108, 36

    p.append(text(ox + ow / 2, top - 20, "зміщення", size=11.5, color=MUTED))
    p.append(text(mx + mw / 2, top - 20, "Карта RCC у даташиті", size=12.5, color=BLUE, bold=True))
    p.append(text(nx + nw / 2, top - 20, "Структура без заглушок", size=12.5, color=BAD, bold=True))
    p.append(text(cx + cw / 2, top - 20, "Структура із заглушками", size=12.5, color=OKC, bold=True))

    for i, (off, mapname, naive, good, bad) in enumerate(rows):
        y = top + i * rh
        h = rh - 7
        yc = y + h / 2 + 4
        p.append(text(ox + ow, yc, off, size=10.5, color=MUTED, anchor="end"))
        p.append(rect(mx, y, mw, h, fill="#eef4ff", stroke=BLUE, sw=1.2, rx=0))
        p.append(text(mx + 9, yc, mapname, size=10.5, color=INK, anchor="start"))
        p.append(rect(nx, y, nw, h, fill=BADF if bad else "#f6f7f8",
                      stroke=BAD if bad else MUTED, sw=1.2, rx=0))
        p.append(text(nx + 9, yc, naive, size=10.5,
                      color=BAD if bad else MUTED, anchor="start", bold=bad))
        if bad:
            p.append(text(nx + nw - 9, yc, "✗", size=12, color=BAD, anchor="end", bold=True))
        p.append(rect(cx, y, cw, h, fill=OKF if bad else "#f6f7f8",
                      stroke=OKC if bad else MUTED, sw=1.2, rx=0))
        p.append(text(cx + 9, yc, good, size=10.5,
                      color=INK if bad else MUTED, anchor="start"))

    ybot = top + len(rows) * rh + 16
    p.append(rect(mx, ybot, cx + cw - mx, 46, fill=BADF, stroke=BAD, sw=1.6, rx=6))
    p.append(mtext((mx + cx + cw) / 2, ybot + 19,
                   ["RCC->AHB1ENR |= 1  насправді пише за 0x24 — це APB2RSTR, молодший біт TIM1RST:",
                    "тактування GPIOA не вмикається, зате TIM1 стає в reset — два несхожі симптоми з однієї помилки"],
                   size=10.5, color=BAD))
    p.append(rect(mx, ybot + 58, cx + cw - mx, 34, fill=OKF, stroke=OKC, sw=1.6, rx=6))
    p.append(text((mx + cx + cw) / 2, ybot + 79,
                  "_Static_assert(offsetof(RCC_TypeDef, AHB1ENR) == 0x30, \"зсув\");   — падає на етапі компіляції",
                  size=10.5, color="#186a3b"))
    p.append(text(W / 2, H - 16,
                  "Заглушка — не косметика: пропущене слово зсуває кожне наступне поле, і запис іде в чужий регістр",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "reg-layout-check.svg"), W, H, *p,
           title="Пропущена діра в карті: куди насправді потрапляє запис")


# ── bsrr-vs-rmw: чому «прочитати-змінити-записати» губить зміни ──────────────
# Ідея (для proj-вставки): ODR |= ... — три команди, і переривання між читанням
# та записом зникає безслідно. BSRR — одна команда, губити нічого.

def fig_bsrr_vs_rmw():
    W, H = 900, 544
    p = []
    BAD, BADF = "#c0392b", "#fdecea"
    OKC, OKF = "#1e8449", "#eafaf0"

    # ── верхня панель: read-modify-write ──
    px, pw = 34, W - 68
    p.append(rect(px, 56, pw, 258, fill="#fffdfd", stroke=BAD, sw=2.0, rx=8))
    p.append(text(px + 20, 82, "GPIOA->ODR |= (1u << 5);   — три команди",
                  size=13, color=BAD, bold=True, anchor="start"))

    steps = [
        (66, "LDR r3, [ODR]", "r3 = 0x0000"),
        (330, "ORR r3, #0x20", "r3 = 0x0020"),
        (652, "STR r3, [ODR]", "ODR ← 0x0020"),
    ]
    bw, bh, by = 190, 52, 102
    for bx, ins, val in steps:
        p.append(rect(bx, by, bw, bh, fill="#f6f7f8", stroke=INK, sw=1.4, rx=6))
        p.append(text(bx + bw / 2, by + 22, ins, size=12, color=INK, bold=True))
        p.append(text(bx + bw / 2, by + 40, val, size=10.5, color=MUTED))
    p.append(arrow(steps[0][0] + bw + 6, by + bh / 2, steps[1][0] - 6, by + bh / 2, color=MUTED, sw=1.4))
    p.append(arrow(steps[1][0] + bw + 6, by + bh / 2, steps[2][0] - 6, by + bh / 2, color=MUTED, sw=1.4))

    # клин переривання між ORR і STR
    wedge_x = (steps[1][0] + bw + steps[2][0]) / 2
    p.append(line(wedge_x, by + bh + 4, wedge_x, 194, color=BAD, sw=1.6, dash="4 3"))
    p.append(rect(300, 194, 566, 56, fill=BADF, stroke=BAD, sw=1.6, rx=6))
    p.append(mtext(583, 216,
                   ["переривання вклинюється тут: ISR робить ODR |= (1u << 7)",
                    "залізо: ODR = 0x0080, вивід 7 піднято"],
                   size=11, color=BAD))
    p.append(text(px + 20, 288,
                  "STR кладе своє 0x0020 поверх — 0x0080 затерто, зміна ISR зникла без сліду",
                  size=11.5, color=BAD, anchor="start", bold=True))

    # ── нижня панель: BSRR ──
    p.append(rect(px, 334, pw, 158, fill="#fcfefd", stroke=OKC, sw=2.0, rx=8))
    p.append(text(px + 20, 360, "GPIOA->BSRR = (1u << 5);   — одна команда",
                  size=13, color=OKC, bold=True, anchor="start"))
    p.append(rect(66, 380, bw, bh, fill="#f6f7f8", stroke=INK, sw=1.4, rx=6))
    p.append(text(66 + bw / 2, 402, "STR r3, [BSRR]", size=12, color=INK, bold=True))
    p.append(text(66 + bw / 2, 420, "0x0000_0020", size=10.5, color=MUTED))
    p.append(arrow(66 + bw + 6, 380 + bh / 2, 292, 380 + bh / 2, color=MUTED, sw=1.4))
    p.append(rect(300, 374, 566, 64, fill=OKF, stroke=OKC, sw=1.6, rx=6))
    p.append(mtext(583, 396,
                   ["читання немає — переривання може влучити лише ДО або ПІСЛЯ;",
                    "залізо саме зводить біт 5 і не чіпає решти: ODR = 0x00A0"],
                   size=11, color="#186a3b"))
    p.append(text(px + 20, 470,
                  "Молодші 16 біт BSRR зводять, старші 16 — скидають; при збігу перемагає зведення",
                  size=11, color=MUTED, anchor="start"))

    p.append(text(W / 2, H - 16,
                  "Атомарність тут не від volatile і не від компілятора — від того, що залізо приймає ціле слово за раз",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "bsrr-vs-rmw.svg"), W, H, *p,
           title="Втрачена зміна: read-modify-write проти BSRR")


# ── priority-byte: куди лягає число пріоритету у 8-бітному полі ──────────────
# Ідея (для api-довідки): NVIC_SetPriority зсуває логічний пріоритет у СТАРШІ
# реалізовані біти байта, а __set_BASEPRI приймає вже готове значення регістра —
# та сама трійка в двох функціях означає різне.

def fig_priority_byte():
    W, H = 900, 580
    p = []
    BAD, BADF = "#c0392b", "#fdecea"
    OKC, OKF = "#1e8449", "#eafaf0"
    GREY = "#e9ecef"

    cw, ncell = 76, 8
    x0 = (W - cw * ncell) / 2          # 146
    mid = x0 + cw * 4                  # межа реалізованих і нереалізованих

    def byte_row(y, h, bits, hi_ok):
        """Рядок із 8 комірок; hi_ok=True — старші 4 зелені, інакше сірі."""
        for i, b in enumerate(bits):
            x = x0 + i * cw
            top4 = i < 4
            fill = (OKF if hi_ok else GREY) if top4 else GREY
            col = (OKC if hi_ok else MUTED) if top4 else MUTED
            p.append(rect(x, y, cw, h, fill=fill, stroke=col, sw=1.6, rx=0))
            p.append(text(x + cw / 2, y + h / 2 + 7, b, size=19,
                          color=col if b == "0" else INK, bold=True))

    # ── панель А: NVIC_SetPriority ──
    p.append(rect(30, 50, W - 60, 250, fill="#fbfdfc", stroke=OKC, sw=2.0, rx=8))
    p.append(text(52, 80, "NVIC_SetPriority(TIM2_IRQn, 3)  —  ти передаєш логічний рівень",
                  size=13, color=OKC, bold=True, anchor="start"))
    p.append(text(52, 104, "3 = 0b0011,  функція сама зсуває на (8 − __NVIC_PRIO_BITS) = 4 біти вліво",
                  size=11, color=MUTED, anchor="start"))

    for i in range(ncell):
        p.append(text(x0 + i * cw + cw / 2, 126, "біт %d" % (7 - i), size=10, color=MUTED))
    byte_row(132, 56, ["0", "0", "1", "1", "0", "0", "0", "0"], hi_ok=True)

    p.append(line(x0, 200, mid, 200, color=OKC, sw=1.6))
    p.append(line(mid, 200, x0 + cw * 8, 200, color=MUTED, sw=1.6))
    p.append(mtext((x0 + mid) / 2, 220, ["4 реалізовані біти", "сюди лягає значення"],
                   size=11, color=OKC))
    p.append(mtext((mid + x0 + cw * 8) / 2, 220, ["4 нереалізовані", "залізо їх ігнорує"],
                   size=11, color=MUTED))

    p.append(text(W / 2, 278, "NVIC->IPR[28] = 0x30", size=15, color=INK, bold=True))

    # ── панель Б: __set_BASEPRI ──
    p.append(rect(30, 320, W - 60, 212, fill="#fffdfd", stroke=BAD, sw=2.0, rx=8))
    p.append(text(52, 350, "__set_BASEPRI(3)  —  та сама трійка, але зсуву НЕМАЄ",
                  size=13, color=BAD, bold=True, anchor="start"))
    p.append(text(52, 374, "BASEPRI приймає готове значення регістра, а не логічний рівень",
                  size=11, color=MUTED, anchor="start"))

    byte_row(388, 48, ["0", "0", "0", "0", "0", "0", "1", "1"], hi_ok=False)

    p.append(text(W / 2, 464, "реалізовані біти = 0   →   BASEPRI = 0   →   маскування вимкнено",
                  size=12.5, color=BAD, bold=True))
    p.append(text(W / 2, 500, "правильно:  __set_BASEPRI(3 << (8 − __NVIC_PRIO_BITS));   →   0x30",
                  size=12.5, color=OKC, bold=True))

    p.append(text(W / 2, H - 18,
                  "Дві сусідні функції приймають різне: одна зсуває сама, друга чекає вже зсунутого",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "priority-byte.svg"), W, H, *p,
           title="Байт пріоритету при __NVIC_PRIO_BITS = 4")


# ── scs-map: простір системного керування з архітектурними адресами ──────────
# Ідея (для api-довідки): усе, чим керує CMSIS-Core, лежить за адресами, які
# задає архітектура, а не виробник — тому цей шар однаковий на кожному чипі.

def fig_scs_map():
    W, H = 880, 566
    p = []
    bx, bw = 210, 620
    rh, gap, top = 60, 10, 116

    p.append(text(W / 2, 66, "SCS_BASE = 0xE000_E000 — архітектурна адреса, однакова в усіх виробників",
                  size=12.5, color=ARM, bold=True))
    p.append(text(bx - 40, 96, "адреса", size=10.5, color=MUTED, anchor="end"))
    p.append(text(bx + 14, 96, "блок ядра і структура CMSIS", size=10.5, color=MUTED, anchor="start"))

    rows = [
        ("0xE000_E010", "SysTick  —  системний таймер",
         "SysTick_Type:  CTRL · LOAD · VAL · CALIB", True),
        ("0xE000_E100", "NVIC  —  контролер переривань",
         "NVIC_Type:  ISER · ICER · ISPR · ICPR · IABR · IPR[240] · STIR", True),
        ("0xE000_ED00", "SCB  —  блок системного керування",
         "SCB_Type:  CPUID · ICSR · VTOR · AIRCR · SCR · CCR · SHPR · CFSR", True),
        ("0xE000_ED90", "MPU  —  блок захисту пам'яті",
         "MPU_Type — лише якщо __MPU_PRESENT == 1", False),
        ("0xE000_EF30", "FPU  —  блок дробових чисел",
         "FPU_Type — лише якщо __FPU_PRESENT == 1", False),
    ]
    for i, (addr, head, fields, always) in enumerate(rows):
        y = top + i * (rh + gap)
        col, fill = (ARM, ARMF) if always else (VEND, VENDF)
        p.append(text(bx - 40, y + rh / 2 + 4, addr, size=11.5, color=BLUE, anchor="end"))
        p.append(rect(bx, y, bw, rh, fill=fill, stroke=col, sw=1.8))
        p.append(text(bx + 16, y + 24, head, size=12.5, color=col, bold=True, anchor="start"))
        p.append(text(bx + 16, y + 45, fields, size=10.5, color=INK, anchor="start"))

    yb = top + len(rows) * (rh + gap) + 8
    p.append(line(60, yb, W - 60, yb, color="#d5d8dc", sw=1.2, dash="5 4"))
    p.append(text(W / 2, yb + 26,
                  "поза SCS:   ITM 0xE000_0000   ·   DWT 0xE000_1000   ·   DCB 0xE000_EDF0   ·   TPIU 0xE004_0000",
                  size=11, color=MUTED))

    p.append(text(W / 2, H - 16,
                  "Виробник не обирає ці адреси — тому шар доступу до ядра пишеться раз і збирається скрізь",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "scs-map.svg"), W, H, *p,
           title="Де лежать блоки ядра, якими керує CMSIS-Core")


if __name__ == "__main__":
    fig_cmsis_layers()
    fig_register_struct()
    fig_portability_boundary()
    fig_cmsis_family()
    fig_cmsis_timeline()
    fig_reg_layout_check()
    fig_bsrr_vs_rmw()
    fig_priority_byte()
    fig_scs_map()
    print("OK: figures written to", OUT)
