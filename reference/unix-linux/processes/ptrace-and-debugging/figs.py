# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COOL = "#eaf0fd"
GREENF = "#eafaf0"
PALE = "#f4f6f8"


# ── 1. Життєвий цикл прикріплення та синхронізації ptrace ──────────────────────
def fig_ptrace_attach_flow():
    W, H = 1040, 560
    p = []

    # Трасувальник (Tracer) - Ліва колонка
    tx = 60
    p.append(fitbox(tx, 50, 420, 36, "Трасувальник (GDB / strace)", size=14,
                    fill=COOL, stroke=NEG, sw=1.8, color=INK, bold=True))
    
    # Трасований (Tracee) - Права колонка
    rx = 560
    p.append(fitbox(rx, 50, 420, 36, "Трасований процес (Target)", size=14,
                    fill=PALE, stroke=INK, sw=1.8, color=INK, bold=True))

    # Вертикальні лінії часової осі
    p.append(line(tx + 210, 86, tx + 210, 440, color=MUTED, sw=1.5, dash="4 4"))
    p.append(line(rx + 210, 86, rx + 210, 440, color=MUTED, sw=1.5, dash="4 4"))

    # Крок 1: PTRACE_ATTACH / TRACEME
    p.append(fitbox(tx + 40, 110, 340, 44, "1. ptrace(PTRACE_ATTACH, pid)\nабо ptrace(PTRACE_TRACEME)",
                    size=11, fill=COOL, stroke=NEG, sw=1.5, color=INK))
    p.append(arrow(tx + 380, 132, rx + 40, 132, color=NEG, sw=1.8))
    p.append(text(490, 122, "сигнал SIGSTOP / SIGTRAP", size=10, color=NEG, bold=True))

    # Крок 2: Перехід трасованого в TASK_TRACED
    p.append(fitbox(rx + 40, 160, 340, 46, "2. Ядро призупиняє процес\nСтан переходить у TASK_TRACED",
                    size=11, fill=WARM, stroke=POS, sw=1.5, color=INK))

    # Крок 3: waitpid() у трасувальника
    p.append(fitbox(tx + 40, 210, 340, 46, "3. waitpid(pid, &status, 0)\nТрасувальник розблоковується",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.5, color=INK))
    p.append(arrow(rx + 40, 183, tx + 380, 233, color=FIELD, sw=1.5))
    p.append(text(490, 200, "сповіщення waitpid", size=10, color=FIELD))

    # Крок 4: Читання/Запис пам'яті та регістрів
    p.append(fitbox(tx + 40, 280, 340, 48, "4. Інспекція та модифікація:\nPEEKDATA / POKEDATA / SETREGS",
                    size=11, fill="#fff", stroke=INK, sw=1.5, color=INK))
    p.append(line(tx + 380, 304, rx + 40, 304, color=INK, sw=1.5))
    p.append(text(490, 296, "прямий доступ через ядро", size=10, color=MUTED))

    # Крок 5: Відновлення виконання
    p.append(fitbox(tx + 40, 350, 340, 44, "5. ptrace(PTRACE_CONT, pid)\nПродовження роботи",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.5, color=INK))
    p.append(arrow(tx + 380, 372, rx + 40, 372, color=FIELD, sw=1.8))

    # Крок 6: Виконання трасованого
    p.append(fitbox(rx + 40, 390, 340, 44, "6. Процес виконує інструкції далі\nстан TASK_RUNNING",
                    size=11, fill=PALE, stroke=INK, sw=1.5, color=INK))

    p.append(fitbox(60, 470, 920, 54,
                    "Ключова ідея: трасований процес не робить жодної інструкції, поки трасувальник\n"
                    "перебуває у виклику waitpid() після зупинки у TASK_TRACED",
                    size=11, fill="#fff", stroke=MUTED, sw=1.2, color=INK))

    render(os.path.join(OUT, "ptrace-attach-flow.svg"), W, H, *p,
           title="Схема ініціалізації та управління процесів через ptrace")


# ── 2. Точка зупину INT 3 (Breakpoint) ─────────────────────────────────────────
def fig_breakpoint_int3():
    W, H = 1040, 580
    p = []

    steps = [
        ("1. Початковий код", SOFT, INK,
         "Адреса 0x401120: [ 0x55 ] (push rbp)\n"
         "Оригінальний байт інструкції в пам'яті"),

        ("2. Впровадження 0xCC", WARM, POS,
         "gdb робить PTRACE_POKEDATA\n"
         "Запис 0xCC (int 3) замість 0x55"),

        ("3. Спрацьовування #BP", WARM, POS,
         "Процесор виконує 0xCC → виняток #BP\n"
         "Ядро шле SIGTRAP, RIP = 0x401121"),

        ("4. Відновлення та крок", GREENF, FIELD,
         "gdb повертає 0x55, ставить RIP = 0x401120\n"
         "PTRACE_SINGLESTEP → повернення 0xCC"),
    ]

    bw, bh = 220, 160
    for i, (title_str, fill, accent, desc) in enumerate(steps):
        bx = 40 + i * 245
        p.append(fitbox(bx, 70, bw, 36, title_str, size=12, fill=fill, stroke=accent, sw=1.6, color=INK, bold=True))
        p.append(fitbox(bx, 114, bw, 220, desc, size=11, fill="#fff", stroke=accent, sw=1.4, color=INK))
        if i < 3:
            p.append(arrow(bx + bw + 4, 220, bx + bw + 21, 220, color=accent, sw=1.8))

    # Схема адресного простору знизу
    p.append(fitbox(40, 370, 960, 120,
                    "Деталі виконання Singlestep:\n"
                    "1. PTRACE_POKEDATA: запис оригінального байта 0x55 назад у пам'ять.\n"
                    "2. PTRACE_SETREGS: зменшення регістра RIP на 1 байт (з 0x401121 назад на 0x401120).\n"
                    "3. PTRACE_SINGLESTEP: встановлення прапорця TF (Trap Flag) у RFLAGS для виконання 1 інструкції.\n"
                    "4. Після виконання 0x55 процесор знову генерує SIGTRAP, gdb повертає 0xCC і робить PTRACE_CONT.",
                    size=11, fill=PALE, stroke=MUTED, sw=1.3, color=INK))

    p.append(text(W / 2, 540,
                  "Програмна точка зупину тимчасово модифікує машинний код процесу в пам'яті",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "breakpoint-int3.svg"), W, H, *p,
           title="Механізм роботи программної точки зупину (INT 3)")


# ── 3. Перехоплення системних викликів у strace ───────────────────────────────
def fig_syscall_interception():
    W, H = 1040, 540
    p = []

    p.append(fitbox(40, 50, 960, 36, "Трасування системного виклику за допомогою PTRACE_SYSCALL",
                    size=14, fill=COOL, stroke=NEG, sw=1.8, color=INK, bold=True))

    # Фази виконання
    phases = [
        (60, 110, 260, "1. Вхід у виклик (Syscall Entry)", WARM, POS,
         "Зупинка перед виконанням виклику.\n"
         "strace читає RAX (номер виклику)\n"
         "та RDI, RSI, RDX (аргументи)"),

        (390, 110, 260, "2. Виконання у ядрі", PALE, MUTED,
         "Ядро виконує системну операцію\n"
         "(наприклад, sys_read або sys_write).\n"
         "Трасований процес спить у ядрі"),

        (720, 110, 260, "3. Вихід з виклику (Syscall Exit)", GREENF, FIELD,
         "Зупинка після виконання виклику.\n"
         "strace читає RAX (код повернення).\n"
         "Друкування результату у консоль"),
    ]

    for x, y, w, title_str, fill, accent, desc in phases:
        p.append(fitbox(x, y, w, 36, title_str, size=12, fill=fill, stroke=accent, sw=1.6, color=INK, bold=True))
        p.append(fitbox(x, y + 42, w, 150, desc, size=11, fill="#fff", stroke=accent, sw=1.4, color=INK))

    p.append(arrow(324, 185, 386, 185, color=POS, sw=1.8))
    p.append(arrow(654, 185, 716, 185, color=FIELD, sw=1.8))

    # Пояснення щодо PTRACE_O_TRACESYSGOOD
    p.append(fitbox(60, 360, 920, 110,
                    "Прапорець PTRACE_O_TRACESYSGOOD:\n"
                    "За замовчуванням ядро надсилає звичайний SIGTRAP при системному виклику.\n"
                    "З прапорцем PTRACE_O_TRACESYSGOOD ядро встановлює 7-й біт у номері сигналу (SIGTRAP | 0x80 = 0x85).\n"
                    "Це дозволяє strace миттєво відрізнити зупинку на системному виклику від звичайного сигналу.",
                    size=11, fill=SOFT, stroke=INK, sw=1.4, color=INK))

    render(os.path.join(OUT, "syscall-interception.svg"), W, H, *p,
           title="Двоетапне перехоплення системних викликів у strace")


# ── 4. Рівні безпеки Yama ptrace_scope ─────────────────────────────────────────
def fig_yama_security_scopes():
    W, H = 1040, 560
    p = []

    scopes = [
        ("Scope 0: Класичний", COOL, NEG,
         "ptrace_scope = 0\n\n"
         "Будь-який процес може трасувати\n"
         "інший процес того самого UID.\n"
         "Високий ризик ін'єкцій шкідливого коду."),

        ("Scope 1: Обмежений", GREENF, FIELD,
         "ptrace_scope = 1 (Стандарт)\n\n"
         "Процес може трасувати лише своїх\n"
         "потомків (через fork + TRACEME).\n"
         "Прямий attach до сторонніх заборонено."),

        ("Scope 2: Лише Root", WARM, POS,
         "ptrace_scope = 2\n\n"
         "Трасування дозволено лише для\n"
         "процесів з CAP_SYS_PTRACE\n"
         "(або суперкористувачу root)."),

        ("Scope 3: Заблоковано", PALE, MUTED,
         "ptrace_scope = 3\n\n"
         "ptrace повністю вимкнено для всіх.\n"
         "Зміна режиму вимагає перезавантаження\n"
         "системи (перезапуск ядра)."),
    ]

    bw, bh = 220, 240
    for i, (title_str, fill, accent, desc) in enumerate(scopes):
        bx = 40 + i * 245
        p.append(fitbox(bx, 70, bw, 38, title_str, size=12, fill=fill, stroke=accent, sw=1.6, color=INK, bold=True))
        p.append(fitbox(bx, 116, bw, bh, desc, size=11, fill="#fff", stroke=accent, sw=1.4, color=INK))

    p.append(fitbox(40, 390, 960, 110,
                    "Налаштування через sysctl / procfs:\n"
                    "Поточний рівень регулюється у файлі /proc/sys/kernel/yama/ptrace_scope.\n"
                    "Для обходу Scope 1 при налагодженні сервісів використовують команду:\n"
                    "sysctl -w kernel.yama.ptrace_scope=0  або надають права CAP_SYS_PTRACE.",
                    size=11, fill=PALE, stroke=MUTED, sw=1.3, color=INK))

    p.append(text(W / 2, 530,
                  "Модуль безпеки Yama обмежує радіус ураження ptrace у сучасних Linux дистрибутивах",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "yama-security-scopes.svg"), W, H, *p,
           title="Рівні обмежень безпеки Yama ptrace_scope")


if __name__ == "__main__":
    fig_ptrace_attach_flow()
    fig_breakpoint_int3()
    fig_syscall_interception()
    fig_yama_security_scopes()
    print("ok")
