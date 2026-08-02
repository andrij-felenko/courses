# -*- coding: utf-8 -*-
"""Фігури теми «Системний виклик: як програма просить ядро»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Що змінює інструкція syscall ────────────────────────────────────────
def fig_transition():
    W, H = 980, 470
    f = []

    cols = [(20, 210), (240, 235), (485, 235), (730, 230)]   # (x, w)
    heads = ["що саме", "до інструкції", "після інструкції", "хто змінив"]

    hy, hh = 52, 36
    for (x, w), s in zip(cols, heads):
        f.append(fitbox(x, hy, w, hh, s, size=14, bold=True, fill="#e8edf3"))

    rows = [
        ("рівень привілею",
         ["рівень 3", "(непривілейований)"],
         ["рівень 0", "(привілейований)"],
         ["процесор"]),
        ("RIP",
         ["наступна", "інструкція програми"],
         ["адреса з IA32_LSTAR"],
         ["процесор"]),
        ("RCX і R11",
         ["значення програми"],
         ["стара RIP", "і старі RFLAGS"],
         ["процесор"]),
        ("RSP",
         ["стек програми"],
         ["стек програми —", "той самий!"],
         ["ядро,", "після swapgs"]),
        ("база GS",
         ["дані програми"],
         ["дані цього ядра CPU"],
         ["ядро,", "swapgs"]),
        ("CR3 (таблиця сторінок)",
         ["таблиця програми"],
         ["таблиця ядра"],
         ["ядро,", "лише з KPTI"]),
    ]

    y = hy + hh + 12
    rh, gap = 52, 8
    for label, before, after, who in rows:
        f.append(fitbox(cols[0][0], y, cols[0][1], rh, [label], size=13, bold=True,
                        fill="#ffffff"))
        f.append(fitbox(cols[1][0], y, cols[1][1], rh, before, size=12, fill=FILL))
        f.append(fitbox(cols[2][0], y, cols[2][1], rh, after, size=12, fill="#eaf3ec"))
        f.append(fitbox(cols[3][0], y, cols[3][1], rh, who, size=12, fill="#ffffff",
                        color=MUTED))
        y += rh + gap

    render(os.path.join(OUT, 'syscall-transition.svg'), W, H, *f,
           title="Стан процесора до і після інструкції syscall")


# ── 2. Шлях одного виклику ─────────────────────────────────────────────────
def fig_path():
    W, H = 960, 720
    f = []

    bx = 470                     # межа привілею
    f.append(line(bx, 66, bx, 596, color=POS, sw=2, dash="7 6"))

    f.append(text(240, 48, "простір користувача", size=15, bold=True))
    f.append(text(700, 48, "ядро", size=15, bold=True))

    LX, LW = 60, 380
    RX, RW = 500, 380

    steps = [
        ("L", 88, 52, ["n = write(1, buf, 13); — рядок у програмі"]),
        ("L", 158, 66, ["обгортка libc: 1 → rax,",
                        "fd → rdi, buf → rsi, 13 → rdx"]),
        ("L", 244, 52, ["інструкція syscall"]),
        ("R", 314, 66, ["swapgs, стек ядра,",
                        "реєстри → pt_regs"]),
        ("R", 400, 66, ["перевірка номера,",
                        "sys_call_table[1] → sys_write"]),
        ("R", 486, 66, ["дескриптор, copy_from_user,",
                        "запис; результат → rax"]),
        ("L", 572, 66, ["sysretq; libc: rax у [−4095…−1]?",
                        "тоді errno = −rax і повернути −1"]),
    ]

    for side, y, h, lines in steps:
        x, w = (LX, LW) if side == "L" else (RX, RW)
        fill = FILL if side == "L" else "#eaf3ec"
        f.append(fitbox(x, y, w, h, lines, size=13, fill=fill))

    # стрілки в межах однієї колонки
    f.append(arrow(250, 140, 250, 156))
    f.append(arrow(250, 224, 250, 242))
    f.append(arrow(690, 380, 690, 398))
    f.append(arrow(690, 466, 690, 484))
    # переходи через межу
    f.append(arrow(442, 272, 502, 336, color=POS))
    f.append(arrow(498, 540, 438, 600, color=POS))

    f.append(text(W / 2, 660, "штрихова лінія — межа привілею; за один виклик її перетинають двічі",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, 'syscall-path.svg'), W, H, *f,
           title="Шлях одного виклику write і назад")


# ── 3. Подвійне читання проти однієї копії ─────────────────────────────────
def fig_double_fetch():
    W, H = 960, 500
    f = []

    panels = [
        (30, 440, POS, "#fdecea",
         "ядро читає структуру в пам'яті програми двічі",
         ["читає len = 8,", "перевіряє: помістилося"],
         ["інший потік:", "len = 1000000"],
         ["читає len удруге —", "копіює 1000000 байтів"],
         ["перевірили одне,", "скористалися іншим"]),
        (490, 440, FIELD, "#eaf3ec",
         "ядро копіює структуру один раз",
         ["copy_from_user:", "одна копія в пам'ять ядра"],
         ["інший потік:", "len = 1000000"],
         ["перевіряє й уживає", "СВОЮ копію: len = 8"],
         ["зміна вже ні на що", "не впливає"]),
    ]

    for x0, w, accent, tint, head, e1, e2, e3, out in panels:
        f.append(fitbox(x0, 56, w, 42, [head], size=14, bold=True, fill="#e8edf3"))
        cx1, cx2 = x0 + 115, x0 + 320
        f.append(text(cx1, 126, "ядро", size=13, bold=True, color=MUTED))
        f.append(text(cx2, 126, "потік програми", size=13, bold=True, color=MUTED))

        f.append(fitbox(cx1 - 100, 140, 200, 56, e1, size=12, fill=FILL))
        f.append(fitbox(cx2 - 100, 222, 200, 56, e2, size=12, fill="#fff7e6"))
        f.append(fitbox(cx1 - 100, 304, 200, 56, e3, size=12, fill=FILL))
        f.append(fitbox(x0 + 15, 396, w - 30, 56, out, size=13, bold=True,
                        fill=tint, stroke=accent, sw=2))

        f.append(arrow(cx1 + 30, 198, cx2 - 30, 220))
        f.append(arrow(cx2 - 30, 280, cx1 + 30, 302))
        f.append(arrow(cx1, 362, cx1, 394))

    render(os.path.join(OUT, 'double-fetch.svg'), W, H, *f,
           title="Чому ядро копіює аргументи, а не читає їх на місці")


# ── 4. Імена, які народжує один макрос ─────────────────────────────────────
def fig_macro_names():
    W, H = 1080, 550
    f = []

    f.append(fitbox(140, 56, 800, 36, ["у fs/read_write.c написано рівно це:"],
                    size=14, bold=True, fill="#e8edf3"))
    f.append(fitbox(140, 100, 800, 44,
                    ["SYSCALL_DEFINE3(write, unsigned int, fd, "
                     "const char __user *, buf, size_t, count)"],
                    size=13, fill=FILL))

    f.append(arrow(540, 148, 540, 176))
    f.append(fitbox(300, 180, 480, 42,
                    ["препроцесор склеює: write → _write → sys_write"],
                    size=13, fill="#fff7e6"))

    f.append(line(141, 240, 939, 240))
    f.append(arrow(540, 224, 540, 239))

    cells = [
        (16, ["__x64_sys_write", "(const struct pt_regs *)",
              "розбирає реєстри", "64-бітної програми"]),
        (282, ["__ia32_sys_write", "(const struct pt_regs *)",
               "те саме для 32-бітної", "програми на цьому ж ядрі"]),
        (548, ["__se_sys_write", "(long, long, long)",
               "знакове розширення", "аргументів"]),
        (814, ["__do_sys_write", "(fd, buf, count)",
               "тіло: те, що написано", "в дужках макроса"]),
    ]
    for x, lines in cells:
        f.append(arrow(x + 125, 240, x + 125, 254))
        f.append(fitbox(x, 256, 250, 106, lines, size=12, fill="#eaf3ec"))

    f.append(fitbox(60, 394, 620, 62,
                    ["рядка «sys_write» як означення функції в дереві немає —",
                     "тому пошук за цим іменем не знаходить тіла"],
                    size=13, fill="#fdecea", stroke=POS, sw=2))
    f.append(fitbox(700, 394, 340, 62,
                    ["де «sys_write» таки написано:",
                     "syscall_64.tbl і оголошення в syscalls.h"],
                    size=12, fill="#eaf3ec", stroke=FIELD, sw=2))

    f.append(text(540, 496, "шукати треба аргумент макроса — «write», а не склеєне ім'я",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, 'macro-names.svg'), W, H, *f,
           title="Одне означення — чотири різні імені")


# ── 5. Карта: де що шукати ─────────────────────────────────────────────────
def fig_source_map():
    W, H = 1060, 670
    f = []

    f.append(fitbox(40, 52, 680, 32, ["де дивитися"], size=13, bold=True,
                    fill="#e8edf3"))
    f.append(fitbox(750, 52, 270, 32, ["що для цього потрібно"], size=13,
                    bold=True, fill="#e8edf3"))

    rows = [
        (["strace: write(1, …, 13) = 13", "номер виклику — 1"],
         ["жива система"], "#fff7e6"),
        (["arch/x86/entry/syscalls/syscall_64.tbl",
          "1  common  write  sys_write — номер ↔ точка входу"],
         ["сирці"], FILL),
        (["arch/x86/entry/entry_64.S",
          "entry_SYSCALL_64: swapgs, стек ядра, pt_regs"],
         ["сирці"], FILL),
        (["arch/x86/entry/syscall_64.c",
          "do_syscall_64 → x64_sys_call(regs, 1): switch за номером"],
         ["сирці"], FILL),
        (["arch/x86/include/generated/asm/syscalls_64.h",
          "__SYSCALL(1, sys_write) → case 1: __x64_sys_write(regs)"],
         ["з'являється лише", "після збірки"], "#fff7e6"),
        (["fs/read_write.c",
          "SYSCALL_DEFINE3(write, …) → ksys_write → vfs_write"],
         ["сирці"], "#eaf3ec"),
        (["write_iter конкретної файлової системи",
          "ext4, tmpfs, procfs — далі шляхи розходяться"],
         ["сирці"], FILL),
    ]

    y, rh, gap = 96, 62, 16
    for left, right, tint in rows:
        f.append(fitbox(40, y, 680, rh, left, size=13, fill=tint))
        f.append(fitbox(750, y, 270, rh, right, size=12, fill="#ffffff",
                        color=MUTED))
        if y + rh + gap < 96 + len(rows) * (rh + gap):
            f.append(arrow(380, y + rh + 1, 380, y + rh + gap - 2))
        y += rh + gap

    f.append(text(530, 634,
                  "для будь-якого іншого виклику міняються тільки номер і два останні рядки",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, 'source-map.svg'), W, H, *f,
           title="Карта шляху: від рядка strace до коду файлової системи")


# ── 6. Куди чіпляти зонд ───────────────────────────────────────────────────
def fig_probe_layers():
    W, H = 1060, 500
    f = []

    cols = [(30, 300), (350, 330), (700, 330)]
    heads = ["куди чіпляти", "що побачите", "чого не побачите"]
    for (x, w), s in zip(cols, heads):
        f.append(fitbox(x, 52, w, 34, [s], size=13, bold=True, fill="#e8edf3"))

    rows = [
        (["__x64_sys_write"],
         ["усі write", "з програм на x86-64"],
         ["виклики 32-бітних програм", "і писання зсередини ядра"]),
        (["__se_sys_write", "__do_sys_write"],
         ["нічого: обидві статичні,", "компілятор їх вбудовує"],
         ["у /proc/kallsyms", "цих імен зазвичай немає"]),
        (["vfs_write"],
         ["усі писання через VFS —", "і від програм, і від ядра"],
         ["писання повз VFS —", "напряму у write_iter"]),
        (["tracepoint:", "syscalls:sys_enter_write"],
         ["виклик за номером,", "без архітектурних імен"],
         ["що робилося далі —", "нижче межі не видно"]),
    ]

    y, rh, gap = 98, 80, 12
    for name, see, miss in rows:
        f.append(fitbox(cols[0][0], y, cols[0][1], rh, name, size=13, bold=True,
                        fill=FILL))
        f.append(fitbox(cols[1][0], y, cols[1][1], rh, see, size=12,
                        fill="#eaf3ec"))
        f.append(fitbox(cols[2][0], y, cols[2][1], rh, miss, size=12,
                        fill="#fdecea"))
        y += rh + gap

    f.append(text(530, 466,
                  "вибір шару — це вибір того, що саме ви ловите, а не деталь синтаксису",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, 'probe-layers.svg'), W, H, *f,
           title="Три шари одного write — три різні зонди")


if __name__ == '__main__':
    fig_transition()
    fig_path()
    fig_double_fetch()
    fig_macro_names()
    fig_source_map()
    fig_probe_layers()
    print("ok")
