# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── arm-licensing: одне ядро — багато виробників ──────────────────────────────
# Ідея: ARM не виробляє чипів, а ліцензує IP ядра; кожен виробник обростає його
# власною периферією. Центр — ядро, навколо — чипи різних компаній.

def fig_arm_licensing():
    W, H = 720, 420
    cx, cy = W / 2, 210
    p = []

    # центр — ядро ARM
    core, cw, ch = textbox(cx, cy, "ядро\nCortex-M\n(IP від ARM)", size=14, bold=True,
                           fill="#f0e6fa", stroke="#7d3c98", sw=2.4, pad=14)

    # виробники навколо: (cx, cy, підпис, колір рамки, заливка)
    makers = [
        (150, 90,  "ST → STM32",        "#1a5276", "#d6eaf8"),
        (cx,  72,  "Nordic → nRF",      "#b03a2e", "#fce0dc"),
        (W - 150, 90,  "Raspberry\n→ RP2040", "#1e8449", "#d5f5e3"),
        (140, 330, "NXP → i.MX RT",     "#6c3483", "#f5f0ff"),
        (cx,  348, "Microchip\n→ SAM",  "#d68910", "#fef9e7"),
        (W - 140, 330, "Renesas → RA",  "#2471a3", "#d2e4f5"),
    ]
    # спершу стрілки від ядра до кожного виробника, тоді рамки зверху
    for mx, my, lab, col, fill in makers:
        p.append(line(cx, cy, mx, my, color="#7d3c98", sw=1.4))
    p.append(core)
    for mx, my, lab, col, fill in makers:
        b, bw, bh = textbox(mx, my, lab, size=11.5, bold=True, color=col, fill=fill, stroke=col, sw=1.8)
        p.append(b)

    p.append(text(cx, H - 14,
                  "ARM продає специфікацію та IP-блок; виробник додає свою периферію й платить роялті",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "arm-licensing.svg"), W, H, *p,
           title="Одне ядро — багато виробників")


# ── cortexm-ladder: сходи продуктивності зі спільним низом ────────────────────
# Ідея: знизу вгору додається продуктивність (FPU, DSP, кеш), але NVIC/SysTick/
# модель винятків лишаються однакові; ESP32 стоїть осторонь — не Cortex-M.

def fig_cortexm_ladder():
    W, H = 740, 470
    p = []

    # сходинки родини (знизу вгору): (підпис, що додає, низ, висота, ширина)
    steps = [
        ("M0 / M0+", "ощадне 32-біт ядро; конкурент 8-бітника", 380, 60, 300),
        ("M3",       "апаратне ділення, насичення, повний Thumb-2", 304, 72, 330),
        ("M4",       "+ DSP-інструкції, опційний FPU (float)", 224, 76, 360),
        ("M7",       "подвійний конвеєр, кеш L1, TCM", 152, 68, 390),
    ]
    for lab, add, by, bh, bw in steps:
        p.append(rect(60, by, bw, bh, fill="#f0e6fa", stroke="#7d3c98", sw=2.0))
        p.append(text(130, by + 24, lab, size=14, color="#7d3c98", bold=True))
        p.append(mtext(bw / 2 + 80, by + bh / 2 + 4, add, size=11, color=INK))

    # колонка «спільне у всіх»
    bx, byc, bcw, bch = 500, 150, 210, 290
    p.append(rect(bx, byc, bcw, bch, fill="#f8f4ff", stroke="#7d3c98", sw=2.0))
    p.append(text(bx + bcw / 2, byc + 26, "Спільне у ВСІХ", size=13, color="#7d3c98", bold=True))
    common = ["NVIC — контролер переривань", "SysTick — таймер ядра",
              "модель винятків (вхід/вихід)", "Thumb-2 (підмножина)",
              "регістри ядра + CMSIS"]
    yy = byc + 58
    for c in common:
        p.append(text(bx + 14, yy, "• " + c, size=11, color="#5b2c80", anchor="start"))
        yy += 40

    # ESP32 осторонь
    ex, ey, ew, eh = 560, 50, 150, 64
    p.append(rect(ex, ey, ew, eh, fill="#d2e4f5", stroke="#2471a3", sw=2.0))
    p.append(mtext(ex + ew / 2, ey + 22, "ESP32\n(Xtensa / RISC-V)\nНЕ Cortex-M", size=11, color=INK))
    p.append(line(ex + ew / 2, ey + eh, ex + ew / 2, byc, color=MUTED, sw=1.4, dash="5 3"))

    p.append(text(W / 2, H - 14,
                  "Вгору додається продуктивність; ядро переривань і таймер незмінні",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "cortexm-ladder.svg"), W, H, *p,
           title="Сходи Cortex-M: спільний низ, продуктивність угору")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури детальної версії (cortex-m-d.md)
# ════════════════════════════════════════════════════════════════════════════

# ── memory-map: єдиний 4-ГБ адресний простір, поділений на смуги ──────────────
# Ідея: усе — код, RAM, периферія, ядро — лежить в одному 32-бітному просторі за
# фіксованими адресами; тому ту саму команду читання можна звернути куди завгодно.

def fig_memory_map():
    W, H = 720, 540
    p = []
    bx, bw = 250, 250
    top, bot = 60, 500
    # смуги зверху (висока адреса) вниз (нуль); кожна — півгігабайта, крім PPB
    regions = [
        ("0xE000_0000", "System / PPB\nNVIC · SysTick · MPU · SCB · debug", "#f0e6fa", "#7d3c98"),
        ("0xA000_0000", "External device\n(зовнішні пристрої)", "#eef0f2", "#6b7280"),
        ("0x6000_0000", "External RAM\n(зовнішня память)", "#eef0f2", "#6b7280"),
        ("0x4000_0000", "Peripheral\nGPIO · UART · SPI · таймери · АЦП", "#d6eaf8", "#1a5276"),
        ("0x2000_0000", "SRAM\nстек · купа · змінні", "#d5f5e3", "#1e8449"),
        ("0x0000_0000", "Code\nFlash · вектори · константи", "#fdf3d6", "#b9770e"),
    ]
    n = len(regions)
    seg = (bot - top) / n
    for i, (addr, lab, fill, col) in enumerate(regions):
        y = top + i * seg
        p.append(rect(bx, y, bw, seg, fill=fill, stroke=col, sw=1.8, rx=0))
        p.append(mtext(bx + bw / 2, y + seg / 2 - 4, lab, size=11, color=INK))
        p.append(text(bx - 12, y + 5, addr, size=11, color=MUTED, anchor="end"))
    p.append(text(bx - 12, bot + 16, "0xFFFF_FFFF — вершина", size=10, color=MUTED, anchor="end"))
    # підпис праворуч
    p.append(mtext(bx + bw + 24, top + seg * 2.0,
                   "Один простір\nна 4 ГБ.\nТа сама команда\nчитає й RAM,\nі регістр\nпериферії —\nрізниться лише\nадреса.",
                   size=11, color=INK, anchor="start"))
    render(os.path.join(OUT, "memory-map.svg"), W, H, *p,
           title="Карта памяті: усе в одному адресному просторі")


# ── vector-table: таблиця векторів від адреси 0 ──────────────────────────────
# Ідея: за нульовою адресою лежить не код, а таблиця адрес-обробників; слот 0 —
# початковий стек, слот 1 — Reset, далі системні винятки, потім лінії IRQ.

def fig_vector_table():
    W, H = 720, 560
    p = []
    bx, bw = 210, 330
    top = 60
    rh = 34
    rows = [
        ("0x00", "Initial MSP — початкова вершина стеку", "#fdf3d6", "#b9770e"),
        ("0x04", "Reset — перша адреса виконання", "#fce0dc", "#b03a2e"),
        ("0x08", "NMI", "#f0e6fa", "#7d3c98"),
        ("0x0C", "HardFault", "#f0e6fa", "#7d3c98"),
        ("0x10", "MemManage / BusFault / UsageFault", "#f0e6fa", "#7d3c98"),
        ("0x2C", "SVCall", "#f0e6fa", "#7d3c98"),
        ("0x38", "PendSV", "#f0e6fa", "#7d3c98"),
        ("0x3C", "SysTick", "#f0e6fa", "#7d3c98"),
        ("0x40", "IRQ0  (перша лінія периферії)", "#d6eaf8", "#1a5276"),
        ("0x44", "IRQ1  …  IRQn", "#d6eaf8", "#1a5276"),
    ]
    for i, (off, lab, fill, col) in enumerate(rows):
        y = top + i * rh
        p.append(rect(bx, y, bw, rh, fill=fill, stroke=col, sw=1.4, rx=0))
        p.append(text(bx + 12, y + rh / 2 + 4, lab, size=11, color=INK, anchor="start"))
        p.append(text(bx - 12, y + rh / 2 + 4, off, size=10, color=MUTED, anchor="end"))
    yb = top + len(rows) * rh
    p.append(text(bx + bw / 2, yb + 26,
                  "кожен слот — 4-байтова АДРЕСА обробника, не код", size=11, color=MUTED, italic=True))
    # стрілки скидання: слот0→SP, слот1→PC
    p.append(text(bx + bw + 20, top + rh / 2 + 4, "→ MSP при скиданні", size=10, color="#b9770e", anchor="start"))
    p.append(text(bx + bw + 20, top + rh + rh / 2 + 4, "→ PC при скиданні", size=10, color="#b03a2e", anchor="start"))
    render(os.path.join(OUT, "vector-table.svg"), W, H, *p,
           title="Таблиця векторів: список адрес від нуля")


# ── nvic-priority: пріоритет, витіснення й підпріоритет ──────────────────────
# Ідея: байт пріоритету ділиться полем PRIGROUP на старші біти (група = право
# витіснити) і молодші (підпріоритет = лише порядок у спільній черзі).

def fig_nvic_priority():
    W, H = 720, 360
    p = []
    # байт із 8 комірок-бітів; реалізовано, скажімо, 4 старші
    cellw, ch = 56, 56
    x0, y0 = 90, 110
    impl = 4               # реалізовано старших бітів
    group = 2              # з них — поле групи (витіснення)
    for i in range(8):
        used = i < impl
        is_group = i < group
        fill = "#fce0dc" if is_group else ("#d6eaf8" if used else "#eef0f2")
        col = "#b03a2e" if is_group else ("#1a5276" if used else "#9aa0a6")
        x = x0 + i * cellw
        p.append(rect(x, y0, cellw, ch, fill=fill, stroke=col, sw=1.8, rx=0))
        p.append(text(x + cellw / 2, y0 + ch / 2 + 5, "b%d" % (7 - i), size=12, color=col, bold=used))
    # дужки-підписи
    p.append(line(x0, y0 - 10, x0 + group * cellw, y0 - 10, color="#b03a2e", sw=2))
    p.append(text(x0 + group * cellw / 2, y0 - 18, "група = витіснення", size=11, color="#b03a2e", bold=True))
    p.append(line(x0 + group * cellw, y0 - 10, x0 + impl * cellw, y0 - 10, color="#1a5276", sw=2))
    p.append(text(x0 + (group + impl) * cellw / 2, y0 - 18, "підпріоритет", size=11, color="#1a5276", bold=True))
    p.append(line(x0 + impl * cellw, y0 + ch + 10, x0 + 8 * cellw, y0 + ch + 10, color="#9aa0a6", sw=2))
    p.append(text(x0 + (impl + 8) * cellw / 2, y0 + ch + 26, "не реалізовано (читається 0)", size=10, color="#9aa0a6"))
    # правило
    p.append(text(W / 2, y0 + ch + 70,
                  "Менше число = вищий пріоритет.", size=12, color=INK, bold=True))
    p.append(text(W / 2, y0 + ch + 94,
                  "Вища ГРУПА витісняє поточний обробник; рівна група чекає черги за підпріоритетом.",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "nvic-priority.svg"), W, H, *p,
           title="Байт пріоритету: група витіснення + підпріоритет")


# ── modes-stacks: Thread/Handler і MSP/PSP ───────────────────────────────────
# Ідея: два режими (Thread/Handler) × вибір стека; винятки завжди в Handler на
# MSP; RTOS дає задачам PSP, а ядру лишає MSP — стеки не змішуються.

def fig_modes_stacks():
    W, H = 720, 380
    p = []
    # дві колонки режимів
    colx = [150, 430]
    boxw, boxh = 220, 90
    p.append(text(colx[0] + boxw / 2, 70, "Thread mode", size=14, color="#1e8449", bold=True))
    p.append(text(colx[0] + boxw / 2, 90, "(звичайний код, main, задачі)", size=10, color=MUTED))
    p.append(text(colx[1] + boxw / 2, 70, "Handler mode", size=14, color="#b03a2e", bold=True))
    p.append(text(colx[1] + boxw / 2, 90, "(обробники винятків і IRQ)", size=10, color=MUTED))

    p.append(rect(colx[0], 110, boxw, boxh, fill="#d5f5e3", stroke="#1e8449", sw=2, rx=8))
    p.append(mtext(colx[0] + boxw / 2, 145, "стек: MSP або PSP\n(вибір у CONTROL)", size=11, color=INK))
    p.append(rect(colx[1], 110, boxw, boxh, fill="#fce0dc", stroke="#b03a2e", sw=2, rx=8))
    p.append(mtext(colx[1] + boxw / 2, 145, "стек: ЗАВЖДИ MSP\n(привілейований)", size=11, color=INK))

    # перехід між режимами
    p.append(arrow(colx[0] + boxw, 140, colx[1], 140, color=INK, sw=1.8))
    p.append(text((colx[0] + boxw + colx[1]) / 2, 130, "виняток", size=10, color="#b03a2e"))
    p.append(arrow(colx[1], 168, colx[0] + boxw, 168, color=INK, sw=1.8))
    p.append(text((colx[0] + boxw + colx[1]) / 2, 184, "EXC_RETURN", size=10, color="#1e8449"))

    # типова розкладка RTOS унизу
    p.append(rect(150, 250, 500, 80, fill="#f8f4ff", stroke="#7d3c98", sw=1.8, rx=8))
    p.append(text(400, 274, "Типова розкладка в RTOS", size=12, color="#7d3c98", bold=True))
    p.append(mtext(400, 300, "задачі — на своїх PSP (кожна зі своїм стеком) · ядро й переривання — на MSP\nпереповнення стеку однієї задачі не псує ядро",
                   size=11, color=INK))
    render(os.path.join(OUT, "modes-stacks.svg"), W, H, *p,
           title="Режими Thread/Handler і два стеки MSP/PSP")


# ── exception-entry: автоматичне складання кадру й EXC_RETURN ─────────────────
# Ідея: на вході в виняток залізо саме кладе 8 регістрів у стек і вантажить в LR
# код EXC_RETURN; на BX LR воно ж відновлює кадр — обробник пишеться як C-функція.

def fig_exception_entry():
    W, H = 720, 470
    p = []
    # стек-кадр (8 слів), згори вниз — порядок зростання адреси у кадрі
    sx, sw_ = 90, 150
    top = 90
    rh = 34
    frame = ["xPSR", "PC (повернення)", "LR", "R12", "R3", "R2", "R1", "R0"]
    p.append(text(sx + sw_ / 2, top - 16, "Кадр у стеку (8 слів)", size=12, color=INK, bold=True))
    for i, r in enumerate(frame):
        y = top + i * rh
        fill = "#d6eaf8" if r in ("xPSR", "PC (повернення)", "LR") else "#eef4ff"
        p.append(rect(sx, y, sw_, rh, fill=fill, stroke="#1a5276", sw=1.3, rx=0))
        p.append(text(sx + sw_ / 2, y + rh / 2 + 4, r, size=11, color=INK))
    p.append(text(sx + sw_ / 2, top + 8 * rh + 18, "залізо кладе саме", size=10, color=MUTED, italic=True))

    # права колонка — EXC_RETURN коди
    ex = 360
    p.append(text(ex, top - 16, "LR ← EXC_RETURN (куди й як вертатись):", size=12, color=INK, anchor="start", bold=True))
    codes = [
        ("0xFFFFFFF1", "Handler mode, стек MSP"),
        ("0xFFFFFFF9", "Thread mode, стек MSP"),
        ("0xFFFFFFFD", "Thread mode, стек PSP"),
    ]
    yy = top + 14
    for code, mean in codes:
        p.append(rect(ex, yy, 110, 30, fill="#fdf3d6", stroke="#b9770e", sw=1.4, rx=4))
        p.append(text(ex + 55, yy + 20, code, size=11, color="#7a5200"))
        p.append(text(ex + 124, yy + 20, mean, size=11, color=INK, anchor="start"))
        yy += 44
    p.append(mtext(ex, yy + 6,
                   "Біт 2 — стек (MSP/PSP), біт 3 — режим.\nFP-варіанти (E1/E9/ED) додають\nкадр співпроцесора.\n\nBX LR із цим кодом → залізо\nрозкладає кадр назад. Тому\nобробник — звичайна C-функція.",
                   size=11, color=INK, anchor="start"))
    render(os.path.join(OUT, "exception-entry.svg"), W, H, *p,
           title="Вхід у виняток: апаратний кадр і EXC_RETURN")


# ── mpu-regions: память поділена на захищені регіони ─────────────────────────
# Ідея: MPU накладає на лінійну память кілька регіонів із правами; доступ поза
# дозволом → MemManage fault, а не тиха псувань сусідньої памяті.

def fig_mpu_regions():
    W, H = 720, 380
    p = []
    bx, bw = 120, 200
    top, seg = 80, 56
    regs = [
        ("Flash код", "R-X", "#fdf3d6", "#b9770e"),
        ("RO-дані", "R--", "#d6eaf8", "#1a5276"),
        ("стек ядра", "RW-", "#d5f5e3", "#1e8449"),
        ("стек задачі", "RW- (лише задача)", "#f0e6fa", "#7d3c98"),
        ("периферія", "RW- (привіл.)", "#fce0dc", "#b03a2e"),
    ]
    for i, (lab, rights, fill, col) in enumerate(regs):
        y = top + i * seg
        p.append(rect(bx, y, bw, seg - 8, fill=fill, stroke=col, sw=1.8, rx=4))
        p.append(text(bx + 12, y + (seg - 8) / 2 + 4, lab, size=12, color=INK, anchor="start"))
        p.append(text(bx + bw - 12, y + (seg - 8) / 2 + 4, rights, size=11, color=col, anchor="end", bold=True))
    # порушник
    vx = bx + bw + 70
    p.append(rect(vx, top + 3 * seg, 180, seg - 8, fill="#fff", stroke="#b03a2e", sw=2, rx=4))
    p.append(mtext(vx + 90, top + 3 * seg + (seg - 8) / 2, "запис у чужий\nстек / код", size=11, color="#b03a2e", bold=True))
    p.append(arrow(vx, top + 3 * seg + (seg - 8) / 2, bx + bw + 4, top + 3 * seg + (seg - 8) / 2, color="#b03a2e", sw=1.8))
    p.append(text((bx + bw + vx) / 2, top + 3 * seg - 8, "MemManage fault", size=10, color="#b03a2e"))
    p.append(text(W / 2, H - 24,
                  "MPU ловить вихід за дозвіл як виняток — баг видно одразу, а не як тиху псувань",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "mpu-regions.svg"), W, H, *p,
           title="MPU: регіони памяті з правами доступу")


# ── bit-banding: один біт = окреме слово в alias-зоні ────────────────────────
# Ідея: кожному біту перших 1 МБ SRAM/периферії відповідає окреме 32-бітне слово
# в alias-зоні; запис у нього атомарно змінює один біт без read-modify-write.

def fig_bit_banding():
    W, H = 720, 360
    p = []
    # ліворуч — байт у bit-band регіоні (8 бітів)
    bx, cellw = 90, 40
    y0 = 130
    p.append(text(bx + 4 * cellw, y0 - 20, "1 байт у bit-band регіоні", size=11, color="#1e8449", bold=True))
    for i in range(8):
        x = bx + i * cellw
        on = (i == 3)
        p.append(rect(x, y0, cellw, 40, fill="#d5f5e3" if on else "#eef0f2",
                      stroke="#1e8449", sw=1.4, rx=0))
        p.append(text(x + cellw / 2, y0 + 26, str(1 if on else 0), size=14, color=INK, bold=on))
    p.append(text(bx + 3 * cellw + cellw / 2, y0 + 58, "біт 3", size=10, color="#1e8449"))

    # стрілка до alias-слова
    ax = bx + 8 * cellw + 80
    p.append(arrow(bx + 3 * cellw + cellw / 2, y0 + 44, ax + 70, y0 + 20, color=INK, sw=1.7))
    p.append(rect(ax, y0 - 4, 200, 48, fill="#fdf3d6", stroke="#b9770e", sw=1.8, rx=6))
    p.append(mtext(ax + 100, y0 + 14, "ціле 32-бітне СЛОВО\nв alias-зоні", size=11, color=INK))

    p.append(text(W / 2, y0 + 100,
                  "Записав 1 у це слово — апаратно зведено лише біт 3. Без read-modify-write,",
                  size=11, color=MUTED))
    p.append(text(W / 2, y0 + 120,
                  "тож переривання не вклиниться посередині. SRAM-alias 0x2200_0000, периферія 0x4200_0000.",
                  size=11, color=MUTED))
    p.append(text(W / 2, y0 + 146, "(є на M3/M4; на M0+/M7 здебільшого немає)", size=10, color="#9aa0a6", italic=True))
    render(os.path.join(OUT, "bit-banding.svg"), W, H, *p,
           title="Bit-banding: один біт — окреме слово")


if __name__ == "__main__":
    fig_arm_licensing()
    fig_cortexm_ladder()
    fig_memory_map()
    fig_vector_table()
    fig_nvic_priority()
    fig_modes_stacks()
    fig_exception_entry()
    fig_mpu_regions()
    fig_bit_banding()
    print("OK: figures written to", OUT)
