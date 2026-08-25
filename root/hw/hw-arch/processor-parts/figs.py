# -*- coding: utf-8 -*-
# Фігури теми «Складові процесора». svgkit імпортуємо (не копіюємо) — §5 AUTHORING.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Спільні відтінки рамок (узгоджені з палітрою svgkit)
RED_F, RED = "#fdf4f4", POS          # процесор / регістри
GRN_F, GRN = "#f4f7f4", FIELD        # пам'ять
GLD_F, GLD = "#fbf3df", "#a9842f"    # керування / прапорці


# ── registers: регістри всередині, пам'ять далеко ────────────────────────────
# Ідея: жменька комірок усередині процесора (миттєво) проти величезної, але
# далекої пам'яті (через шину) — звідси вся логіка «тягни в регістри й рахуй».
def fig_registers():
    W, H = 720, 360
    p = []
    # процесор із регістрами
    px, py, pw, ph = 50, 70, 300, 250
    p.append(rect(px, py, pw, ph, fill=RED_F, stroke=RED, sw=2, rx=12))
    p.append(text(px + pw / 2, py + 26, "ПРОЦЕСОР", size=14, color=RED, bold=True))
    regs = [("R0", "0000 0111"), ("R1", "0011 1100"), ("R2", "0111 0001"),
            ("R3", "1010 0110"), ("R4", "1101 1011")]
    rx, rw, rh = px + 24, pw - 48, 30
    ry = py + 44
    for name, val in regs:
        p.append(rect(rx, ry, rw, rh, fill=BG, stroke=RED, sw=1.4, rx=5))
        p.append(text(rx + 12, ry + rh / 2 + 4.5, name, size=12, color=RED, anchor="start", bold=True))
        p.append(text(rx + rw - 12, ry + rh / 2 + 4.5, val, size=12, color=INK, anchor="end", bold=True))
        ry += rh + 4
    p.append(text(px + pw / 2, py + ph - 12, "6–32 комірки · доступ за частку такту",
                  size=10, color=MUTED, italic=True))

    # пам'ять
    mx, my, mw, mh = 510, 70, 170, 250
    p.append(rect(mx, my, mw, mh, fill=GRN_F, stroke=GRN, sw=2, rx=12))
    p.append(text(mx + mw / 2, my + 26, "ПАМ'ЯТЬ", size=14, color=GRN, bold=True))
    cy = my + 42
    for i in range(7):
        p.append(rect(mx + 18, cy, mw - 36, 22, fill=BG, stroke=GRN, sw=1.1, rx=3))
        p.append(text(mx + 28, cy + 15, "0x%02X" % i, size=10, color=MUTED, anchor="start", bold=True))
        cy += 25
    p.append(text(mx + mw / 2, my + mh - 12, "мільйони комірок · далеко",
                  size=10, color=MUTED, italic=True))

    # шина між ними
    p.append(arrow(px + pw + 4, 180, mx - 4, 180, color=INK, sw=2.2))
    p.append(arrow(mx - 4, 215, px + pw + 4, 215, color=INK, sw=2.2))
    p.append(text((px + pw + mx) / 2, 172, "шина", size=11, color=INK, bold=True))
    p.append(text((px + pw + mx) / 2, 233, "повільно", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "registers.svg"), W, H, *p,
           title="Регістри — усередині й миттєві; пам'ять — велика, але далеко")


# ── named: спеціальні регістри та їхні ролі ──────────────────────────────────
# Ідея: чотири іменовані ролі (PC, IR, загальні, FLAGS) — кожна зі своїм
# призначенням і прикладом значення.
def fig_named():
    W, H = 720, 330
    p = []
    rows = [
        ("PC",       RED, "лічильник команд",  "адреса наступної команди",        "0x0C"),
        ("IR",       GLD, "регістр команд",    "команда, яку виконуємо зараз",     "ДОДАЙ R1,R2"),
        ("R0…Rn",    NEG, "загального призначення", "робочі числа: операнди й результат", "0110 1101"),
        ("FLAGS",    GRN, "регістр прапорців", "Z (нуль) · N (знак) · C (перенос) · V (переповнення)", "Z=0 C=1"),
    ]
    x, w = 50, 620
    y, rh = 60, 58
    for name, col, role, desc, ex in rows:
        p.append(rect(x, y, w, rh, fill=BG, stroke=col, sw=1.8, rx=8))
        p.append(rect(x, y, 96, rh, fill=col, stroke=col, sw=1.8, rx=8))
        p.append(text(x + 48, y + rh / 2 + 5, name, size=13, color=BG, bold=True))
        p.append(text(x + 112, y + 22, role, size=13, color=INK, anchor="start", bold=True))
        p.append(text(x + 112, y + 42, desc, size=11, color=MUTED, anchor="start"))
        p.append(text(x + w - 14, y + rh / 2 + 5, ex, size=12, color=col, anchor="end", bold=True))
        y += rh + 8

    render(os.path.join(OUT, "named.svg"), W, H, *p,
           title="Іменовані регістри: у кожного своя роль")


# ── alu: входи, операція, результат + прапорці ───────────────────────────────
# Ідея: два операнди + код операції зверху → трапеція АЛП → результат і прапорці.
# Конкретний приклад: 6 + 5 = 11, C=0, Z=0.
def fig_alu():
    W, H = 720, 340
    p = []
    # два входи зліва
    for i, (lab, val) in enumerate([("A (R1)", "0000 0110"), ("B (R2)", "0000 0101")]):
        iy = 120 + i * 46
        p.append(rect(70, iy, 190, 36, fill=BG, stroke=NEG, sw=1.6, rx=6))
        p.append(text(82, iy + 23, lab, size=12, color=NEG, anchor="start", bold=True))
        p.append(text(248, iy + 23, val, size=12, color=INK, anchor="end", bold=True))
        p.append(arrow(262, iy + 18, 352, 178 + (i - 0.5) * 26, color=INK, sw=1.8))

    # код операції зверху
    p.append(fitbox(300, 70, 260, 30, "операція: + − AND OR cmp зсув",
                    size=11, fill=GRN_F, stroke=GRN, sw=1.5, bold=True, color=GRN))
    p.append(arrow(430, 100, 460, 150, color=GRN, sw=1.8))

    # трапеція АЛП
    p.append('<path d="M360,150 L432,150 L450,176 L468,150 L540,150 L500,270 L400,270 Z" '
             'fill="%s" stroke="%s" stroke-width="2.2"/>' % (RED_F, RED))
    p.append(text(450, 215, "АЛП", size=18, color=RED, bold=True))
    p.append(text(450, 236, "(ALU)", size=11, color=MUTED))

    # результат униз
    p.append(arrow(450, 272, 450, 296, color=INK, sw=1.8))
    p.append(rect(330, 298, 240, 34, fill=BG, stroke=GRN, sw=1.6, rx=6))
    p.append(text(344, 320, "результат → R3", size=12, color=GRN, anchor="start", bold=True))
    p.append(text(558, 320, "0000 1011", size=12, color=INK, anchor="end", bold=True))

    # прапорці вправо
    p.append(arrow(540, 200, 600, 200, color=GLD, sw=1.8))
    b, bw, bh = textbox(660, 200, "ПРАПОРЦІ\nZ · N · C · V", size=12, bold=True,
                        color=GLD, fill=GLD_F, stroke=GLD, sw=1.6)
    p.append(b)
    p.append(text(660, 248, "6 + 5 = 11 · C=0 Z=0", size=10, color=MUTED))

    render(os.path.join(OUT, "alu.svg"), W, H, *p,
           title="АЛП: два числа + операція → результат і прапорці")


# ── pc: PC указує на наступну команду; +1 і стрибок ──────────────────────────
# Ідея: список команд за адресами; PC — палець, що веде; +1 дає порядок,
# запис іншої адреси — стрибок (цикл).
def fig_pc():
    W, H = 720, 360
    p = []
    prog = [("0x0A", "завантаж R1"), ("0x0B", "завантаж R2"), ("0x0C", "ДОДАЙ R1,R2"),
            ("0x0D", "запиши R3"), ("0x0E", "порівняй"), ("0x0F", "перейди 0x0C")]
    lx, lw, rh = 250, 240, 38
    ly = 70
    cur = 2   # PC указує на 0x0C
    rows_y = []
    for i, (addr, cmd) in enumerate(prog):
        fill = "#fdeee9" if i == cur else BG
        p.append(rect(lx, ly, lw, rh, fill=fill, stroke=RED if i == cur else LINE,
                      sw=1.8 if i == cur else 1.2, rx=6))
        p.append(text(lx + 12, ly + rh / 2 + 4.5, addr, size=11, color=MUTED, anchor="start", bold=True))
        p.append(text(lx + 56, ly + rh / 2 + 4.5, cmd, size=12, color=INK, anchor="start", bold=True))
        rows_y.append(ly + rh / 2)
        ly += rh + 6

    # регістр PC зліва
    p.append(rect(70, rows_y[cur] - 26, 120, 52, fill=RED_F, stroke=RED, sw=2, rx=8))
    p.append(text(130, rows_y[cur] - 6, "PC", size=14, color=RED, bold=True))
    p.append(text(130, rows_y[cur] + 16, "0x0C", size=14, color=INK, bold=True))
    p.append(arrow(192, rows_y[cur], lx - 4, rows_y[cur], color=RED, sw=2))

    # +1 вниз
    p.append(arrow(lx + lw + 8, rows_y[cur], lx + lw + 8, rows_y[cur + 1], color=GRN, sw=1.8))
    p.append(text(lx + lw + 16, (rows_y[cur] + rows_y[cur + 1]) / 2 + 4,
                  "PC + 1 → наступна", size=10, color=GRN, anchor="start", bold=True))

    # стрибок: остання команда повертає PC назад
    p.append('<path d="M%.0f,%.0f C %.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="none" stroke="%s" '
             'stroke-width="1.8" stroke-dasharray="5 4" marker-end="url(#arrow)"/>'
             % (lx + lw, rows_y[5], lx + lw + 80, rows_y[5], lx + lw + 80, rows_y[cur],
                lx + lw + 4, rows_y[cur] + 14, NEG))
    p.append(text(lx + lw + 86, rows_y[4] + 4, "стрибок:", size=10, color=NEG, anchor="start", bold=True))
    p.append(text(lx + lw + 86, rows_y[4] + 20, "PC ← інша адреса", size=10, color=NEG, anchor="start"))

    render(os.path.join(OUT, "pc.svg"), W, H, *p,
           title="Лічильник команд: палець по списку команд")


# ── bus: три набори ліній між процесором, пам'яттю та В/В ─────────────────────
# Ідея: адреса (куди), дані (що, в обидва боки), керування (читати/писати/такт);
# усі три набори спільні для пам'яті й В/В.
def fig_bus():
    W, H = 720, 340
    p = []
    # процесор / пам'ять / В-В
    p.append(rect(40, 130, 130, 80, fill=RED_F, stroke=RED, sw=2, rx=10))
    p.append(text(105, 175, "ПРОЦЕСОР", size=12, color=RED, bold=True))
    p.append(rect(550, 130, 130, 80, fill=GRN_F, stroke=GRN, sw=2, rx=10))
    p.append(text(615, 175, "ПАМ'ЯТЬ", size=12, color=GRN, bold=True))
    p.append(rect(290, 270, 140, 50, fill=GLD_F, stroke=GLD, sw=2, rx=10))
    p.append(text(360, 300, "Ввід / Вивід", size=12, color=GLD, bold=True))

    # три горизонтальні шини
    lines = [
        (118, "Адресна шина", "куди — номер комірки", NEG, True),
        (160, "Шина даних", "що — саме число (туди й назад)", GRN, False),
        (202, "Шина керування", "читати / писати / такт", GLD, True),
    ]
    for ly, name, sub, col, oneway in lines:
        if oneway:
            p.append(arrow(170, ly, 550, ly, color=col, sw=2.4))
        else:
            p.append(arrow(170, ly, 550, ly, color=col, sw=2.4))
            p.append(arrow(550, ly + 0.001, 170, ly + 0.001, color=col, sw=2.4))
        p.append(text(360, ly - 8, name, size=11, color=col, bold=True))
        p.append(text(360, ly + 13, sub, size=9, color=MUTED))

    # відвід до В/В
    p.append(line(360, 202, 360, 270, color=GLD, sw=1.6, dash="4 3"))

    render(os.path.join(OUT, "bus.svg"), W, H, *p,
           title="Шина: адреса (куди) · дані (що) · керування")


# ── together: пристрій керування диригує рештою ──────────────────────────────
# Ідея: усе в зборі — керування читає IR і спрямовує регістри ↔ АЛП, командує
# шиною до пам'яті.
def fig_together():
    W, H = 760, 420
    p = []
    # корпус процесора
    p.append(rect(40, 60, 470, 330, fill="#fff7f7", stroke=RED, sw=2, rx=14))
    p.append(text(275, 84, "ПРОЦЕСОР", size=13, color=RED, bold=True))

    # пристрій керування — широка смуга
    p.append(rect(70, 98, 410, 52, fill=GLD_F, stroke=GLD, sw=1.8, rx=8))
    p.append(text(275, 122, "Пристрій керування (диригент)", size=12.5, color=INK, bold=True))
    p.append(text(275, 140, "читає команду й вирішує, хто що робить", size=10, color=MUTED, italic=True))

    # регістри
    p.append(rect(70, 180, 180, 180, fill=RED_F, stroke=RED, sw=1.8, rx=10))
    p.append(text(160, 202, "Регістри", size=12.5, color=RED, bold=True))
    for i, (n, v) in enumerate([("PC", "0x0C"), ("IR", "ДОДАЙ"), ("R1", "6"),
                                ("R2", "5"), ("FLAGS", "Z C N V")]):
        ry = 214 + i * 28
        p.append(rect(84, ry, 152, 24, fill=BG, stroke=RED, sw=1.3, rx=5))
        p.append(text(94, ry + 16, n, size=11, color=RED, anchor="start", bold=True))
        p.append(text(228, ry + 16, v, size=11, color=INK, anchor="end", bold=True))

    # АЛП
    p.append('<path d="M300,210 L360,210 L375,232 L390,210 L450,210 L415,320 L335,320 Z" '
             'fill=\"%s\" stroke="%s" stroke-width="2.2"/>' % (RED_F, RED))
    p.append(text(375, 272, "АЛП", size=15, color=RED, bold=True))
    p.append(arrow(252, 268, 332, 250, color=INK, sw=1.8))
    p.append(arrow(375, 322, 375, 348, color=INK, sw=1.8))
    p.append(text(375, 362, "результат → регістр", size=9.5, color=MUTED))
    p.append(line(275, 150, 275, 178, color=GLD, sw=1.4, dash="3 3"))

    # пам'ять праворуч + шина
    p.append(rect(580, 120, 150, 210, fill=GRN_F, stroke=GRN, sw=2, rx=12))
    p.append(text(655, 144, "ПАМ'ЯТЬ", size=12.5, color=GRN, bold=True))
    cy = 160
    for a in ("0x0A", "0x0B", "0x0C", "0x0D", "0x0E", "0x0F"):
        p.append(rect(596, cy, 118, 22, fill=BG, stroke=GRN, sw=1.1, rx=3))
        p.append(text(606, cy + 15, a, size=10, color=MUTED, anchor="start", bold=True))
        cy += 26
    p.append(arrow(510, 205, 578, 205, color=INK, sw=2.4))
    p.append(arrow(578, 235, 510, 235, color=INK, sw=2.4))
    p.append(text(544, 197, "шина", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "together.svg"), W, H, *p,
           title="Усе в зборі: керування диригує регістрами, АЛП і шиною")


if __name__ == "__main__":
    fig_registers()
    fig_named()
    fig_alu()
    fig_pc()
    fig_bus()
    fig_together()
    print("OK: figures written to", OUT)
