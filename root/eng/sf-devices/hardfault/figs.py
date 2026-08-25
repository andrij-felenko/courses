# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── stacked-frame: що ядро кладе на стек у мить збою ──────────────────────────
# Ідея: вісім слів кадру лежать у пам'яті в строгому порядку R0..xPSR; з усього
# кадру вирішальне — PC (слово 6), бо це адреса інструкції-винуватця. Стрілка
# веде від PC через .elf до конкретного рядка коду.

def fig_stacked_frame():
    W, H = 760, 430
    p = []
    # вісім комірок кадру (зверху вниз — як на стеку, старша адреса вище)
    bx, bw, bh = 60, 230, 36
    top = 60
    rows = [
        ("xPSR", "стан процесора", MUTED, FILL),
        ("PC", "адреса інструкції-винуватця", POS, "#fdecea"),
        ("LR", "адреса повернення", NEG, "#eaf0fd"),
        ("R12", "", MUTED, FILL),
        ("R3", "", MUTED, FILL),
        ("R2", "", MUTED, FILL),
        ("R1", "", MUTED, FILL),
        ("R0", "", MUTED, FILL),
    ]
    pc_y = None
    for i, (reg, note, col, fill) in enumerate(rows):
        y = top + i * bh
        bold = reg in ("PC", "LR")
        p.append(rect(bx, y, bw, bh, fill=fill, stroke=col, sw=1.8 if bold else 1.4))
        p.append(text(bx + 12, y + bh * 0.64, reg, size=12, color=col, anchor="start", bold=bold))
        if note:
            p.append(text(bx + bw - 10, y + bh * 0.64, note, size=9.5, color=col, anchor="end"))
        if reg == "PC":
            pc_y = y + bh / 2

    # слово 6 — позначка офсету біля PC
    p.append(text(bx - 10, pc_y + 4, "слово 6", size=9, color=POS, anchor="end"))
    p.append(text(bx + bw / 2, top + 8 * bh + 18, "↑ покажчик стека на вході в обробник",
                  size=10, color=MUTED))

    # стрілка PC → .elf → рядок
    ex, ey, ewd, eh = 360, pc_y - 38, 160, 76
    p.append(arrow(bx + bw, pc_y, ex - 4, pc_y, color=POS, sw=2.2))
    p.append(rect(ex, ey, ewd, eh, fill="#fff8e1", stroke="#e67e22", sw=1.8))
    p.append(text(ex + ewd / 2, ey + 26, "firmware.elf", size=13, color="#e67e22", bold=True))
    p.append(text(ex + ewd / 2, ey + 48, "addr2line / GDB", size=10, color=MUTED))
    p.append(text(ex + ewd / 2, ey + 65, "info line *PC", size=10, color="#e67e22"))

    rx, ry, rwd, rh = 580, pc_y - 28, 160, 56
    p.append(arrow(ex + ewd, pc_y, rx - 4, pc_y, color=FIELD, sw=2.2))
    p.append(rect(rx, ry, rwd, rh, fill="#d5e8d4", stroke=FIELD, sw=2.0))
    p.append(mtext(rx + rwd / 2, ry + 24, ["config.c:42", "cfg->rate = val;"],
                   size=11, color=FIELD, bold=True))

    p.append(text(W / 2, H - 22,
                  "Ядро зберігає кадр САМО, ще до обробника — лишається прочитати слова й декодувати PC.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "stacked-frame.svg"), W, H, *p,
           title="Кадр виключення на стеку: вісім слів, вирішальне — PC")


# ── fault-regs: де записано ПРИЧИНУ збою ──────────────────────────────────────
# Ідея: PC каже ДЕ, а ЧОМУ — у статусних регістрах SCB. CFSR поділено на три
# поля (UsageFault/BusFault/MemManage); адресу дають BFAR/MMFAR, але лише коли
# відповідний *VALID піднято. HFSR.FORCED означає ескалацію знизу.

def fig_fault_regs():
    W, H = 860, 470
    p = []
    # шапка CFSR
    p.append(rect(30, 50, 800, 56, fill="#eaf0fd", stroke=NEG, sw=2.0, rx=8))
    p.append(text(430, 72, "CFSR — Configurable Fault Status Register (0xE000ED28)",
                  size=13, color=NEG, bold=True))
    p.append(text(430, 93, "32 біти: [31:16] UsageFault · [15:8] BusFault · [7:0] MemManage",
                  size=11, color=INK))

    cols = [
        (30, "UsageFault [31:16]", "#e67e22", "#fff8e1",
         ["DIVBYZERO — ділення на 0", "UNALIGNED — невирівняний доступ",
          "UNDEFINSTR — невідома інструкція", "NOCP — немає співпроцесора"]),
        (310, "BusFault [15:8]", POS, "#fdecea",
         ["PRECISERR — точна, адреса в BFAR", "IMPRECISERR — неточна (буфер запису)",
          "IBUSERR — помилка вибірки коду", "BFARVALID — BFAR дійсний"]),
        (590, "MemManage [7:0]", FIELD, "#d5e8d4",
         ["IACCVIOL — заборона на код", "DACCVIOL — заборона на дані",
          "MSTKERR — збій при стекуванні", "MMARVALID — MMFAR дійсний"]),
    ]
    cw, cy, ch = 240, 120, 170
    for cx, head, col, fill, items in cols:
        p.append(rect(cx, cy, cw, ch, fill=fill, stroke=col, sw=1.8))
        p.append(text(cx + cw / 2, cy + 22, head, size=11, color=col, bold=True))
        for j, it in enumerate(items):
            p.append(text(cx + 12, cy + 48 + j * 30, it, size=9.5, color=INK, anchor="start"))

    # нижній ряд: HFSR, BFAR, MMFAR
    by, bh2 = 310, 60
    p.append(rect(30, by, 240, bh2, fill="#f2ecf8", stroke="#8a5fb0", sw=1.8))
    p.append(text(150, by + 22, "HFSR (0xE000ED2C)", size=11, color="#8a5fb0", bold=True))
    p.append(text(150, by + 44, "FORCED — ескалація знизу · VECTTBL", size=9.5, color=INK))

    p.append(rect(310, by, 240, bh2, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(430, by + 22, "BFAR (0xE000ED38)", size=11, color=POS, bold=True))
    p.append(text(430, by + 44, "адреса шинної помилки", size=9.5, color=INK))

    p.append(rect(590, by, 240, bh2, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(710, by + 22, "MMFAR (0xE000ED34)", size=11, color=POS, bold=True))
    p.append(text(710, by + 44, "адреса помилки пам'яті (MPU)", size=9.5, color=INK))

    # застереження про IMPRECISERR
    p.append(rect(140, 392, 580, 50, fill="#fff3cd", stroke="#e67e22", sw=1.6, rx=6))
    p.append(mtext(430, 411,
                   ["IMPRECISERR: через буфер запису справжня адреса вже втрачена —",
                    "BFARVALID = 0, а PC показує на кілька інструкцій далі."],
                   size=10, color="#a05a0a"))

    render(os.path.join(OUT, "fault-regs.svg"), W, H, *p,
           title="Причина збою закодована в бітах SCB: читаємо як діагноз")


# ── addr-to-line: адреси без .elf — німі числа ───────────────────────────────
# Ідея: обробник чи паніка дають голі адреси; той самий .elf-файл перекладає їх
# на функції й рядки. Інший .elf дасть хибні рядки — це головна пастка.

def fig_addr_to_line():
    W, H = 840, 380
    p = []
    # ліворуч — голі адреси
    p.append(rect(20, 60, 200, 210, fill="#1e2030", stroke=POS, sw=2.0, rx=8))
    p.append(text(120, 86, "Обробник / паніка", size=12, color=POS, bold=True))
    p.append(text(32, 112, "PC = 0x08001F88", size=10, color="#ffffff", anchor="start"))
    p.append(text(32, 138, "LR = 0x08002ABD", size=10, color="#aaaaaa", anchor="start"))
    p.append(text(32, 170, "Backtrace:", size=10, color="#ffffff", anchor="start"))
    for j, a in enumerate(["0x08001F88", "0x08000C12", "0x08000A40"]):
        p.append(text(32, 196 + j * 22, a, size=10, color="#aaaaaa", anchor="start"))

    # центр — інструмент + .elf
    p.append(arrow(220, 165, 308, 165, color="#e67e22", sw=2.2))
    p.append(rect(315, 112, 200, 106, fill="#fff8e1", stroke="#e67e22", sw=2.0, rx=8))
    p.append(text(415, 136, "addr2line / GDB", size=12, color="#e67e22", bold=True))
    p.append(text(415, 160, "arm-none-eabi-", size=10, color=MUTED))
    p.append(text(415, 182, "+ firmware.elf", size=11, color=POS, bold=True))
    p.append(text(415, 202, "(той самий, що прошитий!)", size=9, color=MUTED))

    # праворуч — функції й рядки
    p.append(arrow(515, 165, 600, 165, color=FIELD, sw=2.2))
    p.append(rect(605, 60, 215, 210, fill="#d5e8d4", stroke=FIELD, sw=2.0, rx=8))
    p.append(text(712, 86, "Читана траса", size=12, color=FIELD, bold=True))
    pairs = [("cfg_write", "config.c:42"), ("init_system", "init.c:67"),
             ("app_main", "main.c:120")]
    yy = 116
    for fn, ln in pairs:
        p.append(text(617, yy, fn, size=10, color=FIELD, anchor="start"))
        p.append(text(633, yy + 20, ln, size=10, color=MUTED, anchor="start"))
        yy += 50

    p.append(rect(170, 312, 500, 44, fill="#fdecea", stroke=POS, sw=1.6, rx=6))
    p.append(mtext(420, 331,
                   ["Потрібен РІВНО той .elf, що прошитий у пам'ять,", "інакше рядки будуть хибні."],
                   size=10.5, color="#8a1f1f"))

    render(os.path.join(OUT, "addr-to-line.svg"), W, H, *p,
           title="Адреси без .elf — німі числа; з .elf — читана траса падіння")


if __name__ == "__main__":
    fig_stacked_frame()
    fig_fault_regs()
    fig_addr_to_line()
    print("OK: figures written to", OUT)
