# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE   = "#1f47b5"
RED    = "#c0271e"
GREEN  = "#1f8a3b"
GOLD   = "#b8860b"
VIOLET = "#6b4fa0"
F_BLUE = "#f3f5fd"
F_RED  = "#fdf4f4"
F_GRN  = "#eef7ee"
F_GLD  = "#fff8e8"
MONO   = "'Consolas', 'DejaVu Sans Mono', 'Courier New', monospace"


def mono(x, y, s, size=13, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


# ── two-doors: у процесора ДВІ адресні шухляди ────────────────────────────────
# Ідея: ті самі дроти адреси й даних, але один сигнал M/IO# обирає, ДО ЯКОГО
# простору звертання — до пам'яті (LD/ST) чи до окремого простору портів (IN/OUT).

def fig_two_doors():
    W, H = 780, 430
    cx = W / 2
    p = []
    p.append(text(cx, 30, "Дві шухляди адрес: пам'ять і окремий простір портів", size=16, bold=True))
    p.append(text(cx, 52, "ті самі дроти адреси й даних; один сигнал M/IO# обирає, до ЯКОГО простору звертання",
                  size=11, color=MUTED, italic=True))

    # процесор
    p.append(rect(300, 78, 180, 66, fill=F_BLUE, stroke=BLUE, sw=2.2, rx=10))
    p.append(text(cx, 104, "ПРОЦЕСОР", size=14, color=BLUE, bold=True))
    p.append(text(cx, 125, "виставляє адресу + сигнал", size=10, color=MUTED))

    # ліва гілка — пам'ять
    p.append('<line x1="330" y1="144" x2="200" y2="212" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>' % GREEN)
    p.append(text(214, 176, "M/IO# = 0", size=11, color=GREEN, bold=True, anchor="start"))
    p.append(text(214, 192, "(команди LD / ST)", size=10, color=MUTED, anchor="start"))
    p.append(rect(60, 218, 300, 96, fill=F_GRN, stroke=GREEN, sw=2, rx=10))
    p.append(text(210, 242, "ПРОСТІР ПАМ'ЯТІ", size=13.5, color=GREEN, bold=True))
    p.append(text(210, 264, "код, змінні, стек, купа", size=11, color=INK))
    p.append(text(210, 284, "величезний: 2³² адрес і більше", size=10.5, color=MUTED))
    p.append(text(210, 303, "тут живе вся звична пам'ять", size=10, color=MUTED, italic=True))

    # права гілка — порти
    p.append('<line x1="450" y1="144" x2="580" y2="212" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>' % RED)
    p.append(text(566, 176, "M/IO# = 1", size=11, color=RED, bold=True, anchor="end"))
    p.append(text(566, 192, "(команди IN / OUT)", size=10, color=MUTED, anchor="end"))
    p.append(rect(420, 218, 300, 96, fill=F_RED, stroke=RED, sw=2, rx=10))
    p.append(text(570, 242, "ПРОСТІР ПОРТІВ (I/O)", size=13.5, color=RED, bold=True))
    p.append(text(570, 264, "тільки регістри пристроїв", size=11, color=INK))
    p.append(text(570, 284, "крихітний: на x86 лише 65536 портів", size=10.5, color=MUTED))
    p.append(text(570, 303, "жодного байта пам'яті сюди не кладуть", size=10, color=MUTED, italic=True))

    p.append(rect(60, 336, 660, 74, fill="#fafafa", stroke=INK, sw=1.6, rx=10))
    p.append(text(cx, 359, "Адреса 0x60 живе ДВІЧІ: як 0x60 у пам'яті й окремо як порт 0x60 — це РІЗНІ комірки.",
                  size=11.5, color=INK, bold=True))
    p.append(text(cx, 380, "Куди саме потрапить звертання, вирішує не адреса, а команда: LD/ST → пам'ять, IN/OUT → порт.",
                  size=10.5, color=MUTED))
    p.append(text(cx, 398, "Той самий провід адреси; різниця — лише в одному сигналі-прапорці M/IO#.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "two-doors.svg"), W, H, *p)


# ── in-out: анатомія команди IN / OUT ─────────────────────────────────────────
# Ідея: IN читає з порту в регістр, OUT пише з регістра в порт; номер порту —
# або 8-бітний прямо в команді (0..255), або повний 16-бітний у регістрі DX.

def fig_in_out():
    W, H = 780, 440
    cx = W / 2
    p = []
    p.append(text(cx, 30, "Команди IN та OUT: єдиний спосіб дістатися простору портів", size=15.5, bold=True))
    p.append(text(cx, 52, "звичайні LD/ST сюди не дістають — потрібні окремі команди з власним кодом операції",
                  size=11, color=MUTED, italic=True))

    # IN
    p.append(rect(50, 78, 320, 120, fill=F_GRN, stroke=GREEN, sw=2, rx=10))
    p.append(text(210, 102, "IN  — прочитати з порту", size=14, color=GREEN, bold=True))
    p.append(mono(74, 132, "IN  AL, 0x60", size=15, color=INK, bold=True))
    p.append(text(210, 158, "порт 0x60  →  регістр AL", size=11, color=INK))
    p.append('<line x1="300" y1="150" x2="210" y2="150" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>' % GREEN)
    p.append(text(210, 182, "дані течуть із пристрою в процесор", size=10, color=MUTED, italic=True))

    # OUT
    p.append(rect(410, 78, 320, 120, fill=F_RED, stroke=RED, sw=2, rx=10))
    p.append(text(570, 102, "OUT — записати в порт", size=14, color=RED, bold=True))
    p.append(mono(434, 132, "OUT 0x20, AL", size=15, color=INK, bold=True))
    p.append(text(570, 158, "регістр AL  →  порт 0x20", size=11, color=INK))
    p.append('<line x1="470" y1="150" x2="560" y2="150" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>' % RED)
    p.append(text(570, 182, "дані течуть із процесора в пристрій", size=10, color=MUTED, italic=True))

    # адресація порту
    p.append(text(cx, 236, "Звідки береться номер порту — два способи", size=13, bold=True))
    p.append(rect(90, 252, 300, 92, fill=BG, stroke=BLUE, sw=1.8, rx=10))
    p.append(text(240, 276, "прямо в команді (immediate)", size=12, color=BLUE, bold=True))
    p.append(mono(112, 302, "IN AL, 0x60", size=13, color=INK, bold=True))
    p.append(text(240, 324, "8 бітів → порти лише 0..255", size=11, color=INK))
    p.append(text(240, 340, "коротко, але вузько", size=10, color=MUTED, italic=True))

    p.append(rect(410, 252, 300, 92, fill=BG, stroke=GOLD, sw=1.8, rx=10))
    p.append(text(560, 276, "через регістр DX", size=12, color=GOLD, bold=True))
    p.append(mono(432, 302, "MOV DX, 0x3F8", size=13, color=INK, bold=True))
    p.append(mono(432, 322, "IN  AL, DX", size=13, color=INK, bold=True))
    p.append(text(560, 340, "16 бітів → усі 65536 портів", size=10.5, color=MUTED, italic=True))

    p.append(rect(50, 360, 680, 62, fill=F_GLD, stroke=GOLD, sw=1.6, rx=10))
    p.append(text(cx, 383, "Дані завжди йдуть через один регістр-акумулятор (AL/AX/EAX) — а не будь-який, як у пам'яті.",
                  size=11, color=INK, bold=True))
    p.append(text(cx, 403, "Тому робота з портами тісна: одна команда — один байт (чи слово) через одну-єдину «трубу».",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "in-out.svg"), W, H, *p)


# ── two-worlds: PMIO проти MMIO — дві філософії доступу до пристроїв ───────────
# Ідея: ліворуч — окремий простір портів з IN/OUT (x86); праворуч — пристрої
# просто в звичайній пам'яті, доступні LD/ST (ARM, RISC-V, майже всі МК).

def fig_two_worlds():
    W, H = 820, 470
    p = []
    p.append(text(W / 2, 32, "Дві філософії: окремий простір портів проти пристроїв у пам'яті", size=16, bold=True))

    # ── ліва картка: port-mapped ──
    p.append(rect(30, 66, 375, 372, fill=F_RED, stroke=RED, sw=2.4, rx=10))
    p.append(text(217, 94, "PORT-MAPPED I/O", size=15.5, color=RED, bold=True))
    p.append(text(217, 113, "пристрої мають ОКРЕМИЙ простір", size=11, color=MUTED, italic=True))
    left = [
        "• два простори: пам'ять і порти",
        "• до портів — лише IN / OUT",
        "• номер порту НЕ їсть адрес пам'яті",
        "• дані — через акумулятор (AL/AX)",
        "• потрібен зайвий сигнал (M/IO#)",
        "• простір портів тісний (65536)",
        "• живе в x86 (від 8080, 1974)",
    ]
    ly = 148
    for ln in left:
        p.append(text(54, ly, ln, size=12.5, color=INK, anchor="start"))
        ly += 28
    p.append(rect(54, 356, 327, 62, fill=BG, stroke=RED, sw=1.5, rx=8))
    p.append(mono(74, 380, "OUT 0x20, AL", size=13, color=INK, bold=True))
    p.append(text(217, 404, "окрема команда для окремого світу", size=10.5, color=MUTED, italic=True))

    # ── права картка: memory-mapped ──
    p.append(rect(445, 66, 375, 372, fill=F_GRN, stroke=GREEN, sw=2.4, rx=10))
    p.append(text(632, 94, "MEMORY-MAPPED I/O", size=15.5, color=GREEN, bold=True))
    p.append(text(632, 113, "пристрої живуть у звичайній пам'яті", size=11, color=MUTED, italic=True))
    right = [
        "• один простір на все",
        "• до пристроїв — ті самі LD / ST",
        "• регістр пристрою = адреса пам'яті",
        "• дані — через будь-який регістр",
        "• жодного зайвого сигналу не треба",
        "• простору скільки завгодно",
        "• ARM, RISC-V, майже всі МК",
    ]
    ry = 148
    for ln in right:
        p.append(text(469, ry, ln, size=12.5, color=INK, anchor="start"))
        ry += 28
    p.append(rect(469, 356, 327, 62, fill=BG, stroke=GREEN, sw=1.5, rx=8))
    p.append(mono(489, 380, "*(uint32_t*)0x40021000 = 1;", size=12, color=INK, bold=True))
    p.append(text(632, 404, "звичайний запис у пам'ять — і все", size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "two-worlds.svg"), W, H, *p)


# ── io-genealogy: родовід окремого вводу-виводу (для hist-вставки) ─────────────
# Ідея: окремий ввід-вивід визрів ДВІЧІ незалежно — у мінікомп'ютерах (PDP-8)
# і в мікропроцесорній лінії від термінала Datapoint. Мікролінія тягнеться в x86,
# де живе донині; сучасні ARM/RISC-V пішли іншим шляхом (пристрої в пам'яті).

def fig_io_genealogy():
    W, H = 900, 470
    p = []
    p.append(text(W / 2, 30, "Родовід окремого простору вводу-виводу", size=17, bold=True))
    p.append(text(W / 2, 51, "ідея визріла двічі незалежно; мікролінія дотягла порти аж у сьогоднішній x86",
                  size=11, color=MUTED, italic=True))

    def node(cx, cy, w, h, title, sub, year, col, fcol):
        out = rect(cx - w / 2, cy - h / 2, w, h, fill=fcol, stroke=col, sw=2, rx=9)
        out += text(cx, cy - h / 2 + 18, year, size=10.5, color=col, bold=True)
        out += text(cx, cy - h / 2 + 36, title, size=12.5, color=INK, bold=True)
        out += text(cx, cy - h / 2 + 53, sub, size=9.5, color=MUTED)
        return out

    ymini = 118
    ymic = 300
    NW, NH = 176, 66

    # ── лінія мінікомп'ютерів ──
    p.append(text(30, ymini - 52, "лінія мінікомп'ютерів (DEC)", size=11.5, color=BLUE, bold=True, anchor="start"))
    p.append(node(150, ymini, NW, NH, "PDP-8", "один опкод IOT", "1965", BLUE, F_BLUE))
    p.append(text(150, ymini + NH / 2 + 20, "пристрій = номер на шині,", size=9.5, color=MUTED))
    p.append(text(150, ymini + NH / 2 + 34, "3 імпульси-команди", size=9.5, color=MUTED))

    # ── мікропроцесорна лінія ──
    p.append(text(30, ymic - 52, "мікропроцесорна лінія (від термінала до Intel)", size=11.5, color=RED, bold=True, anchor="start"))
    xs = [160, 400, 620, 800]
    p.append(node(xs[0], ymic, NW, NH, "Datapoint 2200", "STATUS · BEEP · REWIND", "1970", VIOLET, "#f6f3fb"))
    p.append(node(xs[1], ymic, NW, NH, "Intel 8008", "32 родові команди в/в", "1972", RED, F_RED))
    p.append(node(xs[2], ymic, NW, NH, "Intel 8080", "IN / OUT · 256 портів", "1974", RED, F_RED))
    p.append(node(xs[3], ymic, NW, NH, "x86 (8086→…)", "тягне порти донині", "1978→", RED, F_RED))
    for i in range(3):
        p.append(arrow(xs[i] + NW / 2, ymic, xs[i + 1] - NW / 2, ymic, color=RED, sw=2))

    # відгалуження Z80/8085 від 8080
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" stroke-dasharray="4,3"/>'
             % (xs[2], ymic + NH / 2, xs[2], ymic + NH / 2 + 26, RED))
    p.append(text(xs[2], ymic + NH / 2 + 40, "Z80 · 8085 — теж успадкували", size=9.5, color=MUTED))
    p.append(text(xs[2], ymic + NH / 2 + 54, "окремі порти (сумісність)", size=9.5, color=MUTED))

    # «застигла причина» — примітка над лінією 8080
    p.append(rect(560, 96, 300, 44, fill=F_GLD, stroke=GOLD, sw=1.5, rx=8))
    p.append(text(710, 114, "8-бітний номер порту заморожено тут:", size=9.5, color=INK, bold=True))
    p.append(text(710, 130, "256 портів = стеля 1974 року, жива й досі", size=9.5, color=MUTED, italic=True))

    # ── ті, хто пішов іншим шляхом ──
    p.append(rect(30, 402, 840, 54, fill=F_GRN, stroke=GREEN, sw=1.8, rx=9))
    p.append(text(W / 2, 423, "Без вантажу сумісності обирають ІНШЕ: пристрої просто в пам'яті (memory-mapped I/O)",
                  size=11.5, color=GREEN, bold=True))
    p.append(text(W / 2, 443, "6502 і 68000 тоді · ARM, RISC-V, майже всі мікроконтролери тепер — окремого простору портів немає зовсім",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "io-genealogy.svg"), W, H, *p)


if __name__ == "__main__":
    fig_two_doors()
    fig_in_out()
    fig_two_worlds()
    fig_io_genealogy()
    print("OK: figures written to", OUT)
