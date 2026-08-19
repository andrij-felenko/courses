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


# ── 1. msr-space: Архітектурні регістри проти простору MSR ─────────────────────
def fig_msr_space():
    W, H = 840, 460
    cx = W / 2
    p = []
    p.append(text(cx, 28, "Простір MSR: паралельний світ апаратної конфігурації x86", size=15.5, bold=True))
    p.append(text(cx, 48, "відокремлений від загальних регістрів та адресного простору пам'яті",
                  size=11, color=MUTED, italic=True))

    # Ліва колонка: Архітектурні регістри
    p.append(rect(40, 72, 330, 290, fill=F_BLUE, stroke=BLUE, sw=1.8, rx=8))
    p.append(text(205, 96, "Архітектурні регістри процесора", size=13, color=BLUE, bold=True))
    p.append(text(205, 114, "прямо закодовані в опкодах інструкцій", size=10.5, color=MUTED))

    # Блоки регістрів
    p.append(rect(55, 130, 300, 68, fill="#ffffff", stroke=BLUE, sw=1.2, rx=6))
    p.append(text(205, 150, "Загального призначення (GPR)", size=11.5, bold=True))
    p.append(mono(205, 168, "RAX, RBX, RCX, RDX, RSI, RDI, R8..R15", size=10.5, color=INK, anchor="middle"))
    p.append(text(205, 186, "16 регістрів по 64 біти (обчислення та адреси)", size=10, color=MUTED))

    p.append(rect(55, 208, 300, 68, fill="#ffffff", stroke=BLUE, sw=1.2, rx=6))
    p.append(text(205, 228, "Керуючі регістри (Control Registers)", size=11.5, bold=True))
    p.append(mono(205, 246, "CR0, CR2, CR3, CR4, CR8", size=11, color=BLUE, anchor="middle", bold=True))
    p.append(text(205, 264, "Режими MMU, пейджинг, захист (MOV CRn, Reg)", size=10, color=MUTED))

    p.append(rect(55, 286, 300, 64, fill="#ffffff", stroke=BLUE, sw=1.2, rx=6))
    p.append(text(205, 306, "Вузьке місце кодування", size=11, color=RED, bold=True))
    p.append(text(205, 324, "Кожен новий CR вимагає фіксованого місця в ISA", size=10, color=INK))
    p.append(text(205, 340, "Неможливо вмістити тисячі мікроархітектурних ручок", size=9.5, color=MUTED))

    # Права колонка: Простір MSR
    p.append(rect(470, 72, 330, 290, fill=F_GRN, stroke=GREEN, sw=1.8, rx=8))
    p.append(text(635, 96, "Простір регістрів MSR (Ring 0)", size=13, color=GREEN, bold=True))
    p.append(text(635, 114, "адресується 32-бітним числовим індексом", size=10.5, color=MUTED))

    p.append(rect(485, 130, 300, 220, fill="#ffffff", stroke=GREEN, sw=1.2, rx=6))
    p.append(mono(500, 154, "0x00000010: IA32_TIME_STAMP_COUNTER", size=10, color=INK))
    p.append(mono(500, 174, "0x000001A0: IA32_MISC_ENABLE", size=10, color=INK))
    p.append(mono(500, 194, "0x00000606: MSR_RAPL_POWER_UNIT", size=10, color=INK))
    p.append(mono(500, 214, "0xC0000080: IA32_EFER (Long Mode, NXE)", size=10, color=GREEN, bold=True))
    p.append(mono(500, 234, "0xC0000082: IA32_LSTAR (SYSCALL RIP)", size=10, color=GREEN, bold=True))
    p.append(mono(500, 254, "0xC0000101: IA32_GS_BASE (TLS / Per-CPU)", size=10, color=GREEN, bold=True))
    p.append(mono(500, 274, "0xC0000102: IA32_KERNEL_GS_BASE", size=10, color=GREEN, bold=True))
    p.append(mono(500, 294, "  ... 2³² можливих 64-бітних комірок ...", size=10, color=MUTED, italic=True))
    p.append(mono(500, 314, "0xFFFFFFFF: Максимальний індекс", size=10, color=MUTED))
    p.append(text(635, 338, "Кожен MSR має фіксовану ширину 64 біти", size=10, color=GREEN, bold=True))

    # Центральний місток
    p.append(rect(385, 160, 70, 114, fill=F_GLD, stroke=GOLD, sw=1.5, rx=6))
    p.append(text(420, 184, "Шлюз", size=11, color=GOLD, bold=True))
    p.append(mono(420, 204, "RDMSR", size=11, color=INK, anchor="middle", bold=True))
    p.append(mono(420, 224, "WRMSR", size=11, color=INK, anchor="middle", bold=True))
    p.append(text(420, 244, "ECX", size=10, color=MUTED, bold=True))
    p.append(text(420, 260, "EDX:EAX", size=9.5, color=MUTED))

    p.append(line(370, 200, 385, 200, color=GOLD, sw=2))
    p.append(arrow(455, 200, 470, 200, color=GOLD, sw=2))
    p.append(line(470, 230, 455, 230, color=GOLD, sw=2))
    p.append(arrow(385, 230, 370, 230, color=GOLD, sw=2))

    # Нижнє підсумкове поле
    p.append(rect(40, 376, 760, 68, fill="#fafafa", stroke=INK, sw=1.4, rx=8))
    p.append(text(cx, 398, "MSR створюють масштабований простір конфігурації без спотворення системи команд (ISA).",
                  size=11.5, color=INK, bold=True))
    p.append(text(cx, 418, "Звертання не чіпає фізичну пам'ять і не використовує кеш: дані передаються внутрішньою шиною ядра.",
                  size=10.5, color=MUTED))
    p.append(text(cx, 434, "Доступ дозволено виключно в режимі ядра (Ring 0 / CPL = 0); спроба в Ring 3 генерує виняток #GP(0).",
                  size=10, color=RED, italic=True))

    render(os.path.join(OUT, "msr-space.svg"), W, H, *p)


# ── 2. rdmsr-wrmsr: Механізм команд RDMSR та WRMSR ───────────────────────────
def fig_rdmsr_wrmsr():
    W, H = 840, 470
    cx = W / 2
    p = []
    p.append(text(cx, 28, "Анатомія команд RDMSR та WRMSR", size=15.5, bold=True))
    p.append(text(cx, 48, "протокол передачі 64-бітного значення через регістрову пару EDX:EAX",
                  size=11, color=MUTED, italic=True))

    # Верхній блок: вхідний індекс ECX
    p.append(rect(290, 72, 260, 60, fill=F_VIOL, stroke=VIOLET, sw=1.8, rx=8))
    p.append(text(420, 94, "Регістр ECX (32 біти)", size=12, color=VIOLET, bold=True))
    p.append(mono(420, 114, "Номер MSR (напр. 0xC0000080)", size=11, color=INK, anchor="middle"))

    p.append(arrow(420, 132, 420, 168, color=VIOLET, sw=2))

    # Блок перевірки привілеїв
    p.append(rect(270, 168, 300, 64, fill=F_RED, stroke=RED, sw=1.6, rx=8))
    p.append(text(420, 188, "Апаратна перевірка привілеїв", size=11.5, color=RED, bold=True))
    p.append(text(420, 206, "CPL == 0 (Ring 0)?", size=11, color=INK, bold=True))
    p.append(text(420, 222, "Якщо CPL > 0 → Генерація винятку #GP(0)", size=10, color=RED, italic=True))

    p.append(arrow(420, 232, 420, 268, color=GREEN, sw=2))
    p.append(text(435, 252, "Так", size=11, color=GREEN, bold=True))

    # Нижній блок: обмін даними EDX:EAX <-> MSR
    p.append(rect(60, 268, 720, 110, fill=F_GRN, stroke=GREEN, sw=1.8, rx=8))
    p.append(text(cx, 290, "64-бітний цільовий MSR-регістр усередині процесорного ядра", size=12, color=GREEN, bold=True))

    # MSR розбивка
    p.append(rect(140, 304, 260, 44, fill="#ffffff", stroke=BLUE, sw=1.4, rx=6))
    p.append(text(270, 322, "Старші 32 біти [63:32]", size=11, color=BLUE, bold=True))
    p.append(mono(270, 338, "Передаються через EDX", size=10.5, color=INK, anchor="middle"))

    p.append(rect(440, 304, 260, 44, fill="#ffffff", stroke=BLUE, sw=1.4, rx=6))
    p.append(text(570, 322, "Молодші 32 біти [31:0]", size=11, color=BLUE, bold=True))
    p.append(mono(570, 338, "Передаються через EAX", size=10.5, color=INK, anchor="middle"))

    p.append(text(cx, 368, "RDMSR: MSR → EDX:EAX  |  WRMSR: EDX:EAX → MSR (скидає конвеєр / серіалізує)",
                  size=11, color=INK, bold=True))

    # Нижні пояснювальні картки
    p.append(rect(60, 392, 345, 66, fill=F_GLD, stroke=GOLD, sw=1.4, rx=6))
    p.append(text(232, 412, "Чому EDX:EAX навіть у 64-бітному режимі?", size=10.5, color=GOLD, bold=True))
    p.append(text(232, 430, "Зворотна сумісність з Pentium (1993 рік).", size=10, color=INK))
    p.append(text(232, 446, "Старші 32 біти RAX/RDX при RDMSR обнуляються.", size=9.5, color=MUTED))

    p.append(rect(435, 392, 345, 66, fill=F_BLUE, stroke=BLUE, sw=1.4, rx=6))
    p.append(text(607, 412, "Ціна інструкції WRMSR", size=10.5, color=BLUE, bold=True))
    p.append(text(607, 430, "WRMSR — важка мікрокодова інструкція (100–300 тактів).", size=10, color=INK))
    p.append(text(607, 446, "Вона очищує конвеєр та буфери запису (store buffers).", size=9.5, color=MUTED))

    render(os.path.join(OUT, "rdmsr-wrmsr.svg"), W, H, *p)


# ── 3. syscall-msr-flow: Швидкі системні виклики та SWAPGS ───────────────────
def fig_syscall_msr_flow():
    W, H = 860, 480
    cx = W / 2
    p = []
    p.append(text(cx, 28, "Швидкий перехід у ядро: MSR-регістри SYSCALL та SWAPGS", size=15.5, bold=True))
    p.append(text(cx, 48, "апаратна диспетчеризація системного виклику без звернення до таблиці IDT",
                  size=11, color=MUTED, italic=True))

    # Крок 1: Ring 3 SYSCALL
    p.append(rect(40, 72, 230, 270, fill=F_RED, stroke=RED, sw=1.6, rx=8))
    p.append(text(155, 96, "1. Простір користувача", size=12, color=RED, bold=True))
    p.append(text(155, 114, "CPL = 3 (Ring 3)", size=10.5, color=MUTED))

    p.append(rect(55, 130, 200, 60, fill="#ffffff", stroke=RED, sw=1.2, rx=6))
    p.append(mono(155, 152, "mov rax, 1  ; sys_write", size=9.5, color=INK, anchor="middle"))
    p.append(mono(155, 172, "syscall", size=11, color=RED, anchor="middle", bold=True))

    p.append(rect(55, 202, 200, 126, fill="#ffffff", stroke=INK, sw=1, rx=6))
    p.append(text(155, 222, "Апаратне збереження:", size=10, bold=True))
    p.append(mono(65, 240, "RCX ← наступний RIP", size=9.5, color=INK))
    p.append(mono(65, 258, "R11 ← поточний RFLAGS", size=9.5, color=INK))
    p.append(mono(65, 278, "CPL ← 0 (Ring 0)", size=9.5, color=RED, bold=True))
    p.append(text(155, 308, "Стек не чіпається залізом!", size=9, color=MUTED, italic=True))

    p.append(arrow(270, 170, 310, 170, color=RED, sw=2))

    # Крок 2: Апаратна конфігурація з MSR
    p.append(rect(310, 72, 260, 270, fill=F_GRN, stroke=GREEN, sw=1.8, rx=8))
    p.append(text(440, 96, "2. Апаратне читання MSR", size=12, color=GREEN, bold=True))
    p.append(text(440, 114, "миттєва ініціалізація стану CPU", size=10.5, color=MUTED))

    p.append(rect(325, 130, 230, 56, fill="#ffffff", stroke=GREEN, sw=1.2, rx=6))
    p.append(mono(440, 150, "IA32_LSTAR (0xC0000082)", size=10, color=GREEN, anchor="middle", bold=True))
    p.append(text(440, 170, "RIP ← entry_SYSCALL_64", size=10, color=INK))

    p.append(rect(325, 196, 230, 56, fill="#ffffff", stroke=GREEN, sw=1.2, rx=6))
    p.append(mono(440, 216, "IA32_STAR (0xC0000081)", size=10, color=GREEN, anchor="middle", bold=True))
    p.append(text(440, 236, "CS/SS ← Селектори ядра", size=10, color=INK))

    p.append(rect(325, 262, 230, 66, fill="#ffffff", stroke=GREEN, sw=1.2, rx=6))
    p.append(mono(440, 282, "IA32_FMASK (0xC0000084)", size=10, color=GREEN, anchor="middle", bold=True))
    p.append(text(440, 300, "RFLAGS &= ~FMASK", size=10, color=INK))
    p.append(text(440, 316, "Маскує IF=0 (вимикає переривання)", size=9, color=MUTED))

    p.append(arrow(570, 170, 610, 170, color=GREEN, sw=2))

    # Крок 3: Простір ядра та SWAPGS
    p.append(rect(610, 72, 210, 270, fill=F_BLUE, stroke=BLUE, sw=1.6, rx=8))
    p.append(text(715, 96, "3. Обробник ядра", size=12, color=BLUE, bold=True))
    p.append(text(715, 114, "Точка входу entry_SYSCALL_64", size=10, color=MUTED))

    p.append(rect(622, 130, 186, 56, fill="#ffffff", stroke=BLUE, sw=1.2, rx=6))
    p.append(mono(715, 150, "swapgs", size=12, color=BLUE, anchor="middle", bold=True))
    p.append(text(715, 170, "GS_BASE ↔ KERNEL_GS_BASE", size=9.5, color=INK))

    p.append(rect(622, 196, 186, 132, fill="#ffffff", stroke=INK, sw=1, rx=6))
    p.append(text(715, 216, "Доступ через %gs:", size=10, bold=True))
    p.append(mono(630, 234, "mov rsp, gs:[pda_stack]", size=9, color=INK))
    p.append(text(715, 252, "Стек ядра для процесу", size=9, color=MUTED))
    p.append(mono(630, 274, "mov rbx, gs:[current]", size=9, color=INK))
    p.append(text(715, 292, "Вказівник task_struct", size=9, color=MUTED))
    p.append(text(715, 314, "Безпечний контекст ядра", size=9.5, color=BLUE, bold=True))

    # Нижня панель: SWAPGS механіка
    p.append(rect(40, 360, 780, 100, fill="#fafafa", stroke=INK, sw=1.4, rx=8))
    p.append(text(cx, 382, "Чому інструкція SWAPGS незамінна на вході в ядро:", size=11.5, color=INK, bold=True))
    p.append(text(cx, 402, "При вході через SYSCALL стек залишається стеком користувача (RSP не змінюється апаратно).",
                  size=10.5, color=MUTED))
    p.append(text(cx, 420, "Ядро не може довіряти стеку користувача і не має вільних GPR-регістрів без затирання значень.",
                  size=10.5, color=MUTED))
    p.append(text(cx, 440, "SWAPGS атомарно підставляє структуру per-CPU ядра в GS_BASE, відкриваючи доступ до валідного стека ядра.",
                  size=10.5, color=GREEN, bold=True))

    render(os.path.join(OUT, "syscall-msr-flow.svg"), W, H, *p)


# ── 4. rapl-pmc-monitoring: Телеметрія та ліміти енергії ───────────────────────
def fig_rapl_pmc_monitoring():
    W, H = 840, 460
    cx = W / 2
    p = []
    p.append(text(cx, 28, "Апаратна телеметрія та керування енергією через MSR", size=15.5, bold=True))
    p.append(text(cx, 48, "лічильники продуктивності (PMC) та інтерфейс лімітів потужності (RAPL)",
                  size=11, color=MUTED, italic=True))

    # Ліва колонка: PMC
    p.append(rect(40, 72, 360, 260, fill=F_CYAN, stroke=CYAN, sw=1.8, rx=8))
    p.append(text(220, 96, "Performance Monitoring Counters (PMC)", size=12.5, color=CYAN, bold=True))
    p.append(text(220, 114, "профілювання архітектурних подій ядра", size=10.5, color=MUTED))

    p.append(rect(55, 128, 330, 60, fill="#ffffff", stroke=CYAN, sw=1.2, rx=6))
    p.append(text(220, 148, "Фіксовані лічильники (Fixed Counters)", size=11, bold=True))
    p.append(mono(220, 166, "IA32_FIXED_CTR0..2 (Інструкції, Такти, Реф-такти)", size=9.5, color=INK, anchor="middle"))

    p.append(rect(55, 196, 330, 72, fill="#ffffff", stroke=CYAN, sw=1.2, rx=6))
    p.append(text(220, 216, "Програмовані події (General PMC)", size=11, bold=True))
    p.append(mono(220, 234, "IA32_PERFEVTSELx → IA32_PMCx", size=10, color=CYAN, anchor="middle", bold=True))
    p.append(text(220, 252, "Кеш-промахи (L1/L2/LLC), Branch Misses, TLB stalls", size=9.5, color=MUTED))

    p.append(rect(55, 276, 330, 44, fill="#ffffff", stroke=CYAN, sw=1.2, rx=6))
    p.append(text(220, 296, "Використання: Linux perf, VTune, flamegraphs", size=10, color=INK, bold=True))

    # Права колонка: RAPL
    p.append(rect(440, 72, 360, 260, fill=F_GLD, stroke=GOLD, sw=1.8, rx=8))
    p.append(text(620, 96, "Running Average Power Limit (RAPL)", size=12.5, color=GOLD, bold=True))
    p.append(text(620, 114, "апаратний моніторинг і лімітування енергії", size=10.5, color=MUTED))

    p.append(rect(455, 128, 330, 60, fill="#ffffff", stroke=GOLD, sw=1.2, rx=6))
    p.append(text(620, 148, "Одиниці вимірювання (Power Units)", size=11, bold=True))
    p.append(mono(620, 166, "MSR_RAPL_POWER_UNIT (0x606) → Джоулі / Вати", size=9.5, color=INK, anchor="middle"))

    p.append(rect(455, 196, 330, 72, fill="#ffffff", stroke=GOLD, sw=1.2, rx=6))
    p.append(text(620, 216, "Накопичена енергія (Energy Status)", size=11, bold=True))
    p.append(mono(620, 234, "MSR_PKG_ENERGY_STATUS (0x611) / PP0 / DRAM", size=9.5, color=GOLD, anchor="middle", bold=True))
    p.append(text(620, 252, "32-бітні лічильники джоулів, що безперервно тікають", size=9.5, color=MUTED))

    p.append(rect(455, 276, 330, 44, fill="#ffffff", stroke=GOLD, sw=1.2, rx=6))
    p.append(text(620, 296, "Керування: MSR_PKG_POWER_LIMIT (PL1/PL2 TDP ліміти)", size=10, color=INK, bold=True))

    # Нижня панель зв'язку з простором користувача
    p.append(rect(40, 348, 760, 94, fill="#fafafa", stroke=INK, sw=1.4, rx=8))
    p.append(text(cx, 370, "Доступ з простору користувача в Linux через драйвер msr:", size=11.5, color=INK, bold=True))
    p.append(mono(cx, 392, "pread(fd, &val, 8, msr_offset)  ←  /dev/cpu/<cpu_id>/msr  (потребує root / CAP_SYS_RAWIO)",
                  size=10.5, color=BLUE, anchor="middle", bold=True))
    p.append(text(cx, 412, "Дозволяє системним демонам читати телеметрію температури, енергії та лічильників без модуля ядра.",
                  size=10, color=MUTED))
    p.append(text(cx, 428, "У режимі Kernel Lockdown запис у критичні MSR блокується для захисту пам'яті ядра.",
                  size=9.5, color=RED, italic=True))

    render(os.path.join(OUT, "rapl-pmc-monitoring.svg"), W, H, *p)


if __name__ == "__main__":
    fig_msr_space()
    fig_rdmsr_wrmsr()
    fig_syscall_msr_flow()
    fig_rapl_pmc_monitoring()
    print("MSR figures generated successfully.")
