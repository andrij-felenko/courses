# -*- coding: utf-8 -*-
# Фігури ДЛЯ ДЕТАЛЬНОЇ статті risc-cisc-d.md. Базові фігури лишає figs.py.
# Вивід — у ту саму теку ./img/, окремі імена (…-d.svg), базових не чіпає.
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE   = "#1f47b5"   # CISC-бік
GREEN  = "#1f8a3b"   # RISC-бік
F_BLUE = "#f3f5fd"
F_GRN  = "#eef7ee"
F_GREY = "#f4f5f7"


# ── encoding-fields: фіксоване поле проти байтового потоку ─────────────────────
# Головна механіка декодування: у RISC поля на сталих місцях (регістри читаються
# ПАРАЛЕЛЬНО з розбором); у CISC — байтовий потік, довжину знаєш лише розібравши.

def fig_encoding():
    W, H = 780, 430
    p = [text(W / 2, 44, "Чому декодування таке різне — усе в кодуванні команди",
              size=14, bold=True)]

    # ── RISC: 32-бітове R-type із фіксованими полями ──
    y = 92
    p.append(text(60, y, "RISC (RV32I), R-type — рівно 32 біти, поля на сталих місцях:",
                  size=11.5, bold=True, color=GREEN, anchor="start"))
    fields = [("funct7", 7, "31:25"), ("rs2", 5, "24:20"), ("rs1", 5, "19:15"),
              ("funct3", 3, "14:12"), ("rd", 5, "11:7"), ("opcode", 7, "6:0")]
    total = sum(f[1] for f in fields)
    x0, ww, hh = 60, 660, 46
    bx = x0
    for name, bits, rng in fields:
        w = ww * bits / total
        fill = F_GRN if name in ("rs2", "rs1", "rd") else BG
        p.append(rect(bx, y + 16, w, hh, fill=fill, stroke=GREEN, sw=1.6, rx=4))
        p.append(text(bx + w / 2, y + 16 + 20, name, size=10.5, bold=True, color=INK))
        p.append(text(bx + w / 2, y + 16 + 36, "%d б" % bits, size=9, color=MUTED))
        p.append(text(bx + w / 2, y + 16 + hh + 13, rng, size=8.5, color=MUTED))
        bx += w
    p.append(text(x0 + ww / 2, y + 16 + hh + 34,
                  "номери регістрів (rd, rs1, rs2) — ЗАВЖДИ на тих самих бітах → читаються паралельно з розбором опкоду",
                  size=10, color=GREEN, italic=True))

    # ── CISC: байтовий потік різної довжини ──
    y2 = 250
    p.append(text(60, y2, "CISC (x86) — байтовий потік; довжину команди знаєш лише почавши розбирати:",
                  size=11.5, bold=True, color=BLUE, anchor="start"))
    # три команди різної довжини поспіль
    cmds = [("89 D8", 2, "mov eax,ebx"),
            ("01 04 8B", 3, "add [rbx+rcx*4],eax"),
            ("48 8B 05 3A 27 01 00", 7, "mov rax,[rip+0x1273a]")]
    bx = 60
    byte_w = 30
    for hexs, nbytes, asm in cmds:
        w = nbytes * byte_w
        p.append(rect(bx, y2 + 16, w, 34, fill=F_BLUE, stroke=BLUE, sw=1.6, rx=4))
        p.append(text(bx + w / 2, y2 + 16 + 15, hexs, size=8.5, color=INK))
        p.append(text(bx + w / 2, y2 + 16 + 28, "%d байт" % nbytes, size=8.5, color=BLUE, bold=True))
        p.append(text(bx + w / 2, y2 + 16 + 48, asm, size=8.5, color=MUTED))
        bx += w + 14
    p.append(text(60, y2 + 16 + 78,
                  "межі команд плавають; поля залежать від префіксів і ModR/M — декодер мусить спершу частково розібрати команду.",
                  size=10, color=BLUE, italic=True, anchor="start"))

    p.append(text(W / 2, H - 16,
                  "Сталі поля → миттєве паралельне декодування. Плавні межі → послідовний розбір і вузьке місце.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "encoding-fields.svg"), W, H, *p)


# ── pipeline-hazard: чому рівні команди течуть, а залежність дає бульбашку ──────
# Механіка: 5-ступеневий конвеєр; load-use hazard вставляє бульбашку (stall),
# forwarding її прибирає. Показуємо, ЧОМУ простота команд робить це керованим.

def fig_pipeline():
    W, H = 800, 420
    p = [text(W / 2, 42, "Конвеєр RISC: рівні команди течуть, залежність дає бульбашку",
              size=13.5, bold=True)]

    stages = ["IF", "ID", "EX", "MEM", "WB"]
    scol = {"IF": "#e8eefb", "ID": "#e9f6ec", "EX": "#fff3e0", "MEM": "#fdeaea", "WB": "#efe9fb"}
    cw, ch, x0, y0 = 62, 34, 150, 78
    # шкала тактів
    for c in range(8):
        p.append(text(x0 + cw / 2 + c * cw, y0 - 12, "t%d" % (c + 1), size=10, color=MUTED))

    # рядки-команди: (мітка, зсув-старт, список ступенів; None = бульбашка)
    rows = [
        ("LD  r2,[r1]", 0, ["IF", "ID", "EX", "MEM", "WB"]),
        ("ADD r3,r2,r4", 1, ["IF", "ID", "**", "EX", "MEM", "WB"]),  # ** = stall
        ("SUB r5,r3,r6", 3, ["IF", "ID", "EX", "MEM", "WB"]),
    ]
    for i, (lab, start, seq) in enumerate(rows):
        ry = y0 + i * (ch + 12)
        p.append(text(x0 - 12, ry + ch / 2 + 4, lab, size=10.5, anchor="end", bold=True))
        for k, st in enumerate(seq):
            cx = x0 + (start + k) * cw
            if st == "**":
                p.append(rect(cx + 4, ry + 4, cw - 8, ch - 8, fill="#f4f5f7", stroke=POS, sw=1.6, rx=4))
                p.append(text(cx + cw / 2, ry + ch / 2 + 4, "бульб.", size=8.5, color=POS, bold=True))
            else:
                p.append(rect(cx + 2, ry + 2, cw - 4, ch - 4, fill=scol[st], stroke=INK, sw=1.2, rx=4))
                p.append(text(cx + cw / 2, ry + ch / 2 + 4, st, size=11, bold=True))

    # стрілка forwarding: EX(LD… MEM) -> EX(ADD)
    yA = y0 + 0 * (ch + 12)
    yB = y0 + 1 * (ch + 12)
    fx1 = x0 + 3 * cw + cw / 2         # MEM ступінь LD (t4)
    fx2 = x0 + 4 * cw + cw / 2         # EX ступінь ADD (після бульбашки, t5)
    p.append(arrow(fx1, yA + ch, fx2, yB + 2, color=GREEN, sw=1.8))
    p.append(text((fx1 + fx2) / 2 + 44, yA + ch + 26,
                  "forwarding: результат LD одразу в EX", size=9.5, color=GREEN))

    # легенда ступенів
    ly = y0 + 3 * (ch + 12) + 20
    names = ["IF — вибірка", "ID — декод+регістри", "EX — АЛП", "MEM — пам'ять", "WB — запис"]
    for i, n in enumerate(names):
        p.append(text(x0 - 12 + i * 130, ly, n, size=9, anchor="start", color=MUTED))

    p.append(text(W / 2, H - 40,
                  "Однакова довжина → кожна команда рівно один такт на ступінь; ID читає регістри з фіксованих полів.",
                  size=11, bold=True))
    p.append(text(W / 2, H - 18,
                  "Єдиний реальний затик — load-use: значення з пам'яті ще не готове; одна бульбашка або forwarding.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "pipeline-hazard.svg"), W, H, *p)


# ── code-density: скільки коштує простота і як її відіграли ────────────────────
# Кількісно: довжина коду ARM32 (усе 32-біт) vs Thumb-2 (16/32) vs RVC (16/32).
# Показуємо ціну RISC (довший код) і як компресія її майже прибрала.

def fig_density():
    W, H = 720, 360
    p = [text(W / 2, 44, "Ціна простоти — довший код — і як її майже відіграли",
              size=14, bold=True)]

    ox, oy = 120, 250
    aw, ah = 470, 170
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox - 16, oy - ah + 6, "розмір\nкоду", size=9.5, color=INK, anchor="end"))

    # умовні відносні розміри (ілюстрація тенденції, не мікробенчмарк)
    bars = [("CISC x86\n(щільний)", 0.62, BLUE, F_BLUE),
            ("RISC ARM32\n(усе 32-біт)", 1.00, GREEN, F_GRN),
            ("Thumb-2\n(16/32)", 0.70, GREEN, F_GRN),
            ("RISC-V +C\n(16/32)", 0.72, GREEN, F_GRN)]
    bw = aw / (len(bars) + 0.8)
    for i, (lab, frac, col, fill) in enumerate(bars):
        bx = ox + 20 + i * bw
        bh = ah * frac
        p.append(rect(bx, oy - bh, bw * 0.62, bh, fill=fill, stroke=col, sw=1.6, rx=4))
        p.append(mtext(bx + bw * 0.31, oy + 16, lab, size=9.5, color=INK))

    # позначка «−25…30 %» від ARM32 до RVC
    ax = ox + 20 + 1 * bw + bw * 0.31
    bx2 = ox + 20 + 3 * bw + bw * 0.31
    p.append(line(ax, oy - ah - 4, bx2, oy - ah - 4, color=POS, sw=1.4, dash="4 3"))
    p.append(text((ax + bx2) / 2, oy - ah - 12, "компресія: −25…30 % коду", size=10, color=POS, bold=True))

    p.append(text(W / 2, H - 40,
                  "Класичний RISC платить довшим кодом. Стиснуті набори (Thumb-2, розширення C) вертають щільність,",
                  size=10.5, bold=True))
    p.append(text(W / 2, H - 18,
                  "лишаючи декодування простим: 16-бітову команду декодер розкриває в звичайну 32-бітову.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "code-density.svg"), W, H, *p)


# ── decode-both-ways: збіжність із двох боків ─────────────────────────────────
# CISC ріже складну команду на µops (crack); RISC зшиває дві прості в одну
# макрооперацію (fusion). Обидва рухаються до «розумної кількості простих кроків».

def fig_convergence_both():
    W, H = 800, 360
    p = [text(W / 2, 44, "Збіжність із двох боків: CISC ріже, RISC зшиває",
              size=14, bold=True)]

    # ── верх: CISC crack ──
    y = 118
    b, w1, h1 = textbox(150, y, "1 складна\nx86-команда", size=11, bold=True,
                        color=BLUE, fill=F_BLUE, stroke=BLUE, sw=2, pad=12)
    p.append(b)
    p.append(arrow(150 + w1 / 2, y, 330, y, color=INK, sw=1.8))
    p.append(text((150 + w1 / 2 + 330) / 2, y - 12, "crack", size=10, color=BLUE, bold=True))
    for i in range(3):
        p.append(rect(340, y - 34 + i * 24, 140, 20, fill=F_GRN, stroke=GREEN, sw=1.4, rx=5))
        p.append(text(410, y - 34 + i * 24 + 14, "µop %d" % (i + 1), size=9.5, bold=True, color=GREEN))
    p.append(text(560, y, "= кілька простих кроків", size=11, color=GREEN, anchor="start"))

    # роздільник
    p.append(line(60, 190, W - 60, 190, color=MUTED, sw=1, dash="4 4"))

    # ── низ: RISC macro-op fusion ──
    y2 = 262
    p.append(rect(80, y2 - 30, 150, 24, fill=F_GRN, stroke=GREEN, sw=1.5, rx=5))
    p.append(text(155, y2 - 30 + 16, "CMP  r1, r2", size=10, bold=True))
    p.append(rect(80, y2 + 2, 150, 24, fill=F_GRN, stroke=GREEN, sw=1.5, rx=5))
    p.append(text(155, y2 + 2 + 16, "BR.eq  target", size=10, bold=True))
    p.append(arrow(236, y2, 400, y2, color=INK, sw=1.8))
    p.append(text(318, y2 - 10, "fusion", size=10, color=GREEN, bold=True))
    b2, w2, h2 = textbox(470, y2, "1 злита\nмакрооперація", size=11, bold=True,
                         color=GREEN, fill=F_GRN, stroke=GREEN, sw=2, pad=12)
    p.append(b2)
    p.append(text(560, y2, "= порівняй-і-стрибни за раз", size=11, color=GREEN, anchor="start"))

    p.append(text(W / 2, H - 34,
                  "Ті самі прості кроки всередині: CISC дробить складне на них, RISC склеює дрібне в один.",
                  size=11, bold=True))
    p.append(text(W / 2, H - 14,
                  "Обидва сходяться до однієї внутрішньої одиниці роботи — перемогла не мова, а фізика простих кроків.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "decode-both-ways.svg"), W, H, *p)


if __name__ == "__main__":
    fig_encoding()
    fig_pipeline()
    fig_density()
    fig_convergence_both()
    print("OK: detailed figures written to", OUT)
