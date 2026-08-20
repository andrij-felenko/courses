# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE   = "#1f47b5"
RED    = "#c0271e"
GREEN  = "#1f8a3b"
GOLD   = "#b8860b"
VIOLET = "#6b4fa0"
CYAN   = "#0e7490"
F_BLUE = "#f3f5fd"
F_RED  = "#fdf4f4"
F_GRN  = "#eef7ee"
F_GLD  = "#fff8e8"
F_VIOL = "#f7f4fb"
F_CYAN = "#ecfeff"
MONO   = "'Consolas', 'DejaVu Sans Mono', 'Courier New', monospace"

def mono(x, y, s, size=13, color=INK, anchor="start", bold=False, italic=False):
    w = ' font-weight="700"' if bold else ''
    it = ' font-style="italic"' if italic else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="%s"%s%s>%s</text>' % (x, y, MONO, size, color, anchor, w, it, esc(s)))


# ── 1. rapl-domains: Домени живлення RAPL та апаратний збір телеметрії ──────────
def fig_rapl_domains():
    W, H = 860, 520
    cx = W / 2
    p = []
    p.append(text(cx, 28, "Ієрархія апаратних доменів живлення Intel RAPL", size=16, bold=True))
    p.append(text(cx, 48, "Розподіл лічильників накопиченої енергії за фізичними зонами процесорного сокета",
                  size=11, color=MUTED, italic=True))

    # Зовнішній прямокутник: Platform / PSys Domain
    p.append(rect(30, 68, 800, 370, fill=F_GLD, stroke=GOLD, sw=2, rx=10))
    p.append(text(50, 92, "Платформний домен (Platform / PSys)", size=12.5, color=GOLD, bold=True, anchor="start"))
    p.append(mono(50, 110, "MSR 0x64D / VRM + SoC", size=10, color=MUTED, anchor="start"))

    # Внутрішній прямокутник: Package Domain (PKG)
    p.append(rect(50, 126, 540, 292, fill=F_BLUE, stroke=BLUE, sw=1.8, rx=8))
    p.append(text(70, 148, "Процесорний сокет (Package / PKG)", size=13, color=BLUE, bold=True, anchor="start"))
    p.append(mono(70, 166, "MSR_PKG_ENERGY_STATUS (0x611)", size=10.5, color=INK, anchor="start"))

    # Домен обчислювальних ядер PP0 (Power Plane 0)
    p.append(rect(70, 182, 245, 220, fill=F_GRN, stroke=GREEN, sw=1.5, rx=6))
    p.append(text(192, 204, "Домен ядер (PP0 / Cores)", size=12, color=GREEN, bold=True))
    p.append(mono(192, 220, "MSR 0x639", size=10, color=MUTED, anchor="middle"))

    for i in range(4):
        yx = 232 + i * 38
        p.append(rect(82, yx, 221, 30, fill="#ffffff", stroke=GREEN, sw=1, rx=4))
        p.append(mono(90, yx + 20, "Core %d + L1/L2" % i, size=10.5, color=INK))
        p.append(text(265, yx + 20, "ALU/FPU", size=9.5, color=MUTED))

    # Домен графіки PP1 (Power Plane 1)
    p.append(rect(330, 182, 245, 100, fill=F_VIOL, stroke=VIOLET, sw=1.5, rx=6))
    p.append(text(452, 204, "Графічне ядро (PP1 / GPU)", size=11.5, color=VIOLET, bold=True))
    p.append(mono(452, 222, "MSR 0x641", size=10, color=MUTED, anchor="middle"))
    p.append(rect(342, 234, 221, 36, fill="#ffffff", stroke=VIOLET, sw=1, rx=4))
    p.append(text(452, 257, "Intel HD / Iris Xe Graphics", size=10.5, color=INK))

    # Блок Uncore / LLC / System Agent всередині PKG
    p.append(rect(330, 292, 245, 110, fill="#ffffff", stroke=BLUE, sw=1.2, rx=6))
    p.append(text(452, 314, "Системний агент та Uncore", size=11, color=BLUE, bold=True))
    p.append(text(452, 332, "Спільний кеш L3 (LLC), Ring Bus,", size=9.5, color=MUTED))
    p.append(text(452, 348, "контролер пам'яті IMC, PCIe", size=9.5, color=MUTED))
    p.append(mono(452, 375, "E(Uncore) = PKG - PP0 - PP1", size=9.5, color=INK, anchor="middle", bold=True))

    # Окремий домен оперативної пам'яті DRAM Domain
    p.append(rect(610, 126, 205, 140, fill=F_CYAN, stroke=CYAN, sw=1.6, rx=8))
    p.append(text(712, 150, "Пам'ять (DRAM Domain)", size=12, color=CYAN, bold=True))
    p.append(mono(712, 168, "MSR 0x619", size=10.5, color=INK, anchor="middle"))
    p.append(rect(622, 180, 181, 72, fill="#ffffff", stroke=CYAN, sw=1, rx=4))
    p.append(text(712, 202, "Шина пам'яті DDR4/DDR5", size=10, color=INK))
    p.append(text(712, 220, "Живлення модулів DIMM", size=9.5, color=MUTED))
    p.append(text(712, 238, "(Сервери Xeon / деякі SoC)", size=9.5, color=MUTED, italic=True))

    # Блок контролера PCU (Power Control Unit)
    p.append(rect(610, 276, 205, 142, fill="#ffffff", stroke=RED, sw=1.8, rx=8))
    p.append(text(712, 298, "Апаратний мікроконтролер PCU", size=11, color=RED, bold=True))
    p.append(text(712, 315, "Опитування сенсорів ~1 мс", size=9.5, color=MUTED))
    p.append(rect(622, 326, 181, 80, fill=F_RED, stroke=RED, sw=1, rx=4))
    p.append(mono(630, 344, "Лічильники подій (PMC)", size=9.5, color=INK))
    p.append(mono(630, 360, "Струм/напруга (FIVR/SVID)", size=9.5, color=INK))
    p.append(mono(630, 378, "Модель енергії в мікрокоді", size=9.5, color=RED, bold=True))
    p.append(mono(630, 396, "-> Накопичення в MSR", size=9.5, color=GREEN, bold=True))

    # Стрілки передачі даних від PCU до доменів
    p.append(arrow(610, 350, 580, 350, color=RED, sw=1.6))
    p.append(arrow(712, 276, 712, 270, color=RED, sw=1.6))

    # Нижня плашка підсумку
    p.append(rect(30, 450, 800, 54, fill="#fafafa", stroke=INK, sw=1.2, rx=6))
    p.append(text(cx, 472, "Кожен домен накопичує спожиті мікроджоулі в окремому 32-бітному MSR-лічильнику.",
                  size=11, bold=True))
    p.append(text(cx, 490, "Квант енергії задається базовим регістром MSR_RAPL_POWER_UNIT (0x606): E = 1 / 2^ESU Джоулів.",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "rapl-domains.svg"), W, H, *p)


# ── 2. power-capping-pl1-pl2: Дворівневе обмеження потужності PL1 та PL2 ─────────
def fig_power_capping():
    W, H = 840, 460
    cx = W / 2
    p = []
    p.append(text(cx, 28, "Дворівневе апаратне керування потужністю: ліміти PL1 та PL2", size=15.5, bold=True))
    p.append(text(cx, 48, "Динамічне обмеження сплесків навантаження через ковзне часове вікно інтегрування",
                  size=11, color=MUTED, italic=True))

    # Графік: осі
    ox, oy = 90, 340
    gw, gh = 680, 260
    p.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2))
    p.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2))

    p.append(text(ox + gw - 15, oy + 25, "Час (секунди)", size=11, bold=True, anchor="end"))
    p.append(text(ox - 10, oy - gh + 10, "Потужність (Вт)", size=11, bold=True, anchor="end"))

    # Горизонтальні лінії лімітів
    y_pl2 = 140
    y_pl1 = 205
    y_idle = 320

    p.append(line(ox, y_pl2, ox + gw, y_pl2, color=RED, sw=1.6, dash="6,4"))
    p.append(mono(ox - 12, y_pl2 + 4, "PL2 (180 Вт)", size=10.5, color=RED, anchor="end", bold=True))
    p.append(text(ox + gw - 10, y_pl2 - 8, "Короткочасний ліміт (Short-term Limit / Tau)", size=9.5, color=RED, anchor="end"))

    p.append(line(ox, y_pl1, ox + gw, y_pl1, color=BLUE, sw=1.6, dash="6,4"))
    p.append(mono(ox - 12, y_pl1 + 4, "PL1 (125 Вт)", size=10.5, color=BLUE, anchor="end", bold=True))
    p.append(text(ox + gw - 10, y_pl1 - 8, "Тривалий тепловий ліміт TDP (Sustained Limit)", size=9.5, color=BLUE, anchor="end"))

    p.append(mono(ox - 12, y_idle + 4, "Холостий (15 Вт)", size=10, color=MUTED, anchor="end"))

    pts = [
        (ox, y_idle),
        (ox + 90, y_idle),
        (ox + 95, 145),
        (ox + 230, 145),
        (ox + 270, y_pl1),
        (ox + 460, y_pl1),
        (ox + 475, y_idle),
        (ox + gw, y_idle)
    ]
    polyline_str = " ".join(["%.1f,%.1f" % pt for pt in pts])
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (polyline_str, INK))

    # Виділення зони турбо-бусту Tau
    p.append(rect(ox + 95, y_pl1, 135, y_pl1 - 145, fill=F_RED, stroke=RED, sw=1, rx=2))
    p.append(text(ox + 162, 175, "Енергетичний кредит", size=10, color=RED, bold=True))
    p.append(text(ox + 162, 190, "Turbo Boost (Tau ≈ 28-56 c)", size=9.5, color=RED))

    # Стрілка часового вікна Tau
    p.append(line(ox + 95, 120, ox + 230, 120, color=RED, sw=1.5))
    p.append(line(ox + 95, 114, ox + 95, 126, color=RED, sw=1.5))
    p.append(line(ox + 230, 114, ox + 230, 126, color=RED, sw=1.5))
    p.append(text(ox + 162, 112, "Часове вікно Tau (Time Window)", size=10, color=RED, bold=True))

    # Анотація зниження частоти
    p.append(arrow(ox + 300, 240, ox + 265, y_pl1 + 5, color=BLUE, sw=1.4))
    p.append(text(ox + 330, 255, "PCU зменшує частоту (DVFS):", size=10, color=BLUE, bold=True, anchor="start"))
    p.append(text(ox + 330, 270, "середня енергія у вікні досягла PL1", size=9.5, color=MUTED, anchor="start"))

    # Пояснення знизу
    p.append(rect(40, 375, 760, 68, fill="#fafafa", stroke=INK, sw=1.2, rx=6))
    p.append(text(cx, 396, "Алгоритм RAPL Power Capping не обмежує миттєву потужність жорстко щомиті.",
                  size=11, bold=True))
    p.append(text(cx, 414, "Він інтегрує енергію E = ∫ P dt: процесор може споживати PL2, доки середня потужність у вікні Tau не перевищить PL1.",
                  size=10.5, color=MUTED))
    p.append(text(cx, 430, "При вичерпанні теплового бюджету апаратний контролер плавно скидає P-стан до рівня охолодження.",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "power-capping-pl1-pl2.svg"), W, H, *p)


# ── 3. energy-accumulator-wrap: 32-бітний акумулятор і переповнення ─────────────
def fig_energy_accumulator_wrap():
    W, H = 860, 430
    cx = W / 2
    p = []
    p.append(text(cx, 28, "32-бітний лічильник енергії: квантування та переповнення", size=15.5, bold=True))
    p.append(text(cx, 48, "Розрахунок спожитих Джоулів та обробка переходу через 2³² беззнаковою арифметикою",
                  size=11, color=MUTED, italic=True))

    # Схема кругового лічильника
    ox, oy, r = 160, 210, 85
    p.append(circle(ox, oy, r, fill=F_BLUE, stroke=BLUE, sw=2))
    p.append(circle(ox, oy, r - 30, fill="#ffffff", stroke=BLUE, sw=1.2))

    p.append(text(ox, oy - 8, "32 біти", size=12, color=BLUE, bold=True))
    p.append(mono(ox, oy + 10, "0 .. 2³²-1", size=10, color=INK, anchor="middle"))
    p.append(mono(ox, oy + 26, "≈ 65 536 Дж", size=9.5, color=MUTED, anchor="middle"))

    p.append(line(ox, oy - r - 8, ox, oy - r + 8, color=RED, sw=2.5))
    p.append(mono(ox, oy - r - 12, "0 / 2³²", size=11, color=RED, anchor="middle", bold=True))

    # Точки вимірів: E1 та E2
    # E1: верхній правий квадрант
    # E2: нижній правий квадрант
    p.append(circle(ox + 55, oy - 55, 5, fill=GOLD, stroke=LINE, sw=1))
    p.append(mono(ox + 65, oy - 65, "E1 = 0xE0000000", size=9.5, color=GOLD, bold=True))
    p.append(text(ox + 65, oy - 50, "t1 = 10.0 c", size=9.5, color=MUTED, anchor="start"))

    p.append(circle(ox + 55, oy + 55, 5, fill=GREEN, stroke=LINE, sw=1))
    p.append(mono(ox + 65, oy + 55, "E2 = 0x10000000", size=9.5, color=GREEN, bold=True))
    p.append(text(ox + 65, oy + 70, "t2 = 12.0 c", size=9.5, color=MUTED, anchor="start"))

    p.append(text(ox + 10, oy + r + 24, "Приріст ΔE через нуль", size=10, color=RED, bold=True, anchor="middle"))

    # Права частина: математичний розрахунок
    p.append(rect(390, 75, 430, 265, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    p.append(text(605, 98, "Математика беззнакової дельти uint32_t", size=13, color=BLUE, bold=True))

    p.append(rect(405, 114, 400, 48, fill=F_GRN, stroke=GREEN, sw=1, rx=4))
    p.append(mono(415, 134, "uint32_t delta = (uint32_t)(E2 - E1);", size=11, color=GREEN, bold=True))
    p.append(text(415, 150, "За модулем 2³² віднімання дає точний приріст без if-розгалужень", size=9.5, color=MUTED, anchor="start"))

    p.append(mono(405, 180, "1. Квант ESU = 16  ->  Unit = 1 / 2¹⁶ = 15.258789 мкДж", size=10, color=INK))
    p.append(mono(405, 200, "2. ΔE_raw = 0x10000000 - 0xE0000000 = 0x30000000", size=10, color=INK))
    p.append(mono(405, 218, "          = 805 306 368 квантів лічильника", size=10, color=MUTED))
    p.append(mono(405, 240, "3. Енергія = 805 306 368 * 15.26 мкДж = 12 288.0 Дж", size=10, color=BLUE, bold=True))
    p.append(mono(405, 262, "4. Час Δt  = 12.0 c - 10.0 c = 2.0 секунди", size=10, color=INK))
    p.append(mono(405, 286, "5. Потужність P = 12288.0 Дж / 2.0 с = 6 144.0 Вт", size=10.5, color=RED, bold=True))
    p.append(text(415, 310, "(Приклад для серверного вузла або прискореного тесту)", size=9.5, color=MUTED, italic=True, anchor="start"))

    # Підсумкова плашка
    p.append(rect(30, 355, 790, 58, fill="#fafafa", stroke=INK, sw=1.2, rx=6))
    p.append(text(cx, 376, "Період повного переповнення 32-бітного лічильника при TDP 150 Вт становить ≈ 436 секунд (7.2 хвилини).",
                  size=11, bold=True))
    p.append(text(cx, 394, "Опитування частіше одного разу на 5 хвилин гарантує відсутність втрати кратних обертів лічильника.",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "energy-accumulator-wrap.svg"), W, H, *p)


# ── 4. linux-rapl-access-stack: Програмні інтерфейси доступу в Linux ─────────────
def fig_linux_access_stack():
    W, H = 860, 500
    cx = W / 2
    p = []
    p.append(text(cx, 28, "Стек програмного доступу до лічильників RAPL у Linux", size=16, bold=True))
    p.append(text(cx, 48, "Від апаратних MSR до високорівневих систем моніторингу в просторі користувача",
                  size=11, color=MUTED, italic=True))

    # Рівень 1: Користувацький простір
    p.append(rect(30, 68, 800, 130, fill=F_BLUE, stroke=BLUE, sw=1.8, rx=8))
    p.append(text(50, 92, "Простір користувача (User Space / Ring 3)", size=12.5, color=BLUE, bold=True, anchor="start"))

    # 4 колонки
    p.append(rect(50, 108, 175, 76, fill="#ffffff", stroke=BLUE, sw=1.2, rx=6))
    p.append(text(137, 128, "Низькорівневі утиліти", size=10.5, bold=True))
    p.append(mono(137, 146, "turbostat, msr-tools", size=10, color=INK, anchor="middle"))
    p.append(text(137, 164, "Прямий pread(/dev/cpu/0/msr)", size=9.5, color=MUTED))

    p.append(rect(240, 108, 185, 76, fill="#ffffff", stroke=GREEN, sw=1.2, rx=6))
    p.append(text(332, 128, "Sysfs Powercap клієнти", size=10.5, color=GREEN, bold=True))
    p.append(mono(332, 146, "/sys/class/powercap", size=10, color=INK, anchor="middle"))
    p.append(text(332, 164, "Читання energy_uj (ASCII)", size=9.5, color=MUTED))

    p.append(rect(440, 108, 180, 76, fill="#ffffff", stroke=VIOLET, sw=1.2, rx=6))
    p.append(text(530, 128, "Профілювальники Linux", size=10.5, color=VIOLET, bold=True))
    p.append(mono(530, 146, "perf stat -e power/...", size=10, color=INK, anchor="middle"))
    p.append(text(530, 164, "perf_event_open() API", size=9.5, color=MUTED))

    p.append(rect(635, 108, 175, 76, fill="#ffffff", stroke=CYAN, sw=1.2, rx=6))
    p.append(text(722, 128, "Хмарний моніторинг", size=10.5, color=CYAN, bold=True))
    p.append(mono(722, 146, "Kepler / Scaphandre", size=10, color=INK, anchor="middle"))
    p.append(text(722, 164, "eBPF + cgroups облік", size=9.5, color=MUTED))

    # Рівень 2: Ядро Linux
    p.append(rect(30, 218, 800, 130, fill=F_GRN, stroke=GREEN, sw=1.8, rx=8))
    p.append(text(50, 242, "Ядро Linux (Kernel Space / Ring 0)", size=12.5, color=GREEN, bold=True, anchor="start"))

    p.append(rect(50, 258, 230, 76, fill="#ffffff", stroke=GREEN, sw=1.2, rx=6))
    p.append(text(165, 278, "Драйвер msr.ko", size=11, bold=True))
    p.append(mono(165, 296, "drivers/char/msr.c", size=9.5, color=INK, anchor="middle"))
    p.append(text(165, 314, "Перевірка CAP_SYS_RAWIO", size=9.5, color=RED))

    p.append(rect(295, 258, 260, 76, fill="#ffffff", stroke=GREEN, sw=1.2, rx=6))
    p.append(text(425, 278, "Power Capping Framework", size=11, color=GREEN, bold=True))
    p.append(mono(425, 296, "intel_rapl_common.c", size=9.5, color=INK, anchor="middle"))
    p.append(text(425, 314, "sysfs атрибути енергії та лімітів", size=9.5, color=MUTED))

    p.append(rect(570, 258, 240, 76, fill="#ffffff", stroke=GREEN, sw=1.2, rx=6))
    p.append(text(690, 278, "Підсистема Perf Events", size=11, color=VIOLET, bold=True))
    p.append(mono(690, 296, "arch/x86/events/rapl.c", size=9.5, color=INK, anchor="middle"))
    p.append(text(690, 314, "Драйвер PMU 'power'", size=9.5, color=MUTED))

    # Стрілки між Ring 3 та Ring 0
    p.append(arrow(137, 184, 165, 258, color=BLUE, sw=1.5))
    p.append(arrow(332, 184, 380, 258, color=GREEN, sw=1.5))
    p.append(arrow(530, 184, 650, 258, color=VIOLET, sw=1.5))
    p.append(arrow(722, 184, 480, 258, color=CYAN, sw=1.5))

    # Рівень 3: Апаратний рівень
    p.append(rect(30, 368, 800, 68, fill=F_GLD, stroke=GOLD, sw=1.8, rx=8))
    p.append(text(50, 392, "Апаратний рівень процесора (Silicon / PCU)", size=12.5, color=GOLD, bold=True, anchor="start"))
    p.append(mono(cx, 415, "RDMSR / WRMSR : 0x606 (Units), 0x611 (PKG), 0x639 (PP0), 0x619 (DRAM), 0x610 (Limits)",
                  size=9.5, color=INK, anchor="middle", bold=True))

    # Стрілки від ядра до заліза
    p.append(arrow(165, 334, 250, 368, color=GOLD, sw=1.5))
    p.append(arrow(425, 334, 425, 368, color=GOLD, sw=1.5))
    p.append(arrow(690, 334, 600, 368, color=GOLD, sw=1.5))

    # Нижня підсумкова плашка
    p.append(rect(30, 448, 800, 42, fill="#fafafa", stroke=INK, sw=1.2, rx=6))
    p.append(text(cx, 468, "Після уразливості PLATYPUS (CVE-2020-8694) прямий доступ до лічильників обмежено root (0400).",
                  size=10.5, color=RED, bold=True))

    render(os.path.join(OUT, "linux-rapl-access-stack.svg"), W, H, *p)


if __name__ == "__main__":
    fig_rapl_domains()
    fig_power_capping()
    fig_energy_accumulator_wrap()
    fig_linux_access_stack()
    print("Всі фігури згенеровано успішно.")
