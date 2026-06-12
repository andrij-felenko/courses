# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для ⚙️-вставки до теми 3.5.4 — «Читаємо дизасемблер».
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами (fig-18-4a-*).
НЕ чіпає головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif.
Нумерація підписів у тексті — Рис. 3.5.4a.k.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
ORANGE = "#e08030"
PURPLE = "#7a3fb0"
MONO = "Consolas, 'DejaVu Sans Mono', 'Courier New', monospace"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", PURPLE: "aPurple"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", family=FONT):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def mono(x, y, s, size=14, color=INK, anchor="start", weight="normal"):
    return text(x, y, s, size, color, anchor, weight, "normal", MONO)


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.5.4a.1 — той самий цикл на C → асемблер двома ISA (Xtensa, RISC-V)
# ════════════════════════════════════════════════════════════════════════════
def fig_loop_to_asm():
    W, H = 960, 540
    s = header(W, H)
    s += text(W / 2, 30, "Один цикл на C — і що з нього зробив компілятор двома мовами процесора",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 51,
              "та сама сума масиву; кожен рядок C розгортається в кілька машинних команд — і вони РІЗНІ для різних ISA",
              11, GREY, "middle", style="italic")

    # ── ліворуч: вихідний C ──────────────────────────────────────────────
    cx, cw = 24, 250
    s += rect(cx, 78, cw, 200, "#fbfbff", BLUE, 1.8, 12)
    s += text(cx + cw / 2, 100, "вихідний код (C)", 12.5, BLUE, "middle", "bold")
    cline = [
        "int sum = 0;",
        "for (int i = 0; i < n; i++)",
        "    sum += a[i];",
        "return sum;",
    ]
    cy = 130
    for i, ln in enumerate(cline):
        s += mono(cx + 16, cy + i * 26, ln, 13.5, INK)
    # позначки-«ярлики» рядків
    s += rect(cx + 14, cy + 1 * 26 - 14, cw - 28, 20, "none", GREEN, 1.3, 5)
    s += rect(cx + 14, cy + 2 * 26 - 14, cw - 28, 20, "none", RED, 1.3, 5)
    s += text(cx + cw / 2, 262, "4 короткі рядки людською мовою", 10, GREY, "middle", style="italic")

    # стрілки «компілятор»
    s += arrow(cx + cw + 6, 150, cx + cw + 40, 150, INK, 2.4)
    s += text(cx + cw + 23, 142, "gcc", 10, INK, "middle", "bold", family=MONO)
    s += arrow(cx + cw + 6, 360, cx + cw + 40, 360, INK, 2.4)
    s += text(cx + cw + 23, 352, "gcc", 10, INK, "middle", "bold", family=MONO)

    # ── праворуч-згори: Xtensa (ESP32) ───────────────────────────────────
    ax, aw = cx + cw + 48, 632
    s += rect(ax, 78, aw, 198, "#f6fbf6", GREEN, 1.8, 12)
    s += text(ax + 16, 100, "Xtensa  (ядро ESP32)", 12.5, GREEN, "start", "bold")
    s += text(ax + aw - 14, 100, "objdump -d", 11, GREY, "end", "normal", family=MONO)
    xt = [
        ("  movi   a8, 0", "sum = 0  (поклади 0 у регістр)", GREEN),
        ("  blti   a3, 1, .Lend", "якщо n<1 — одразу в кінець", PURPLE),
        (".Lloop:", "— початок тіла циклу —", GREY),
        ("  l32i   a9, a2, 0", "завантаж a[i] з пам'яті", INK),
        ("  add.n  a8, a8, a9", "sum += a[i]", RED),
        ("  addi   a2, a2, 4", "крок покажчика на наступне слово", INK),
        ("  addi   a3, a3, -1", "лічильник n-- ", INK),
        ("  bnez   a3, .Lloop", "ще лишилось? — назад у .Lloop", PURPLE),
    ]
    yy = 124
    for i, (op, cmt, col) in enumerate(xt):
        s += mono(ax + 14, yy + i * 19, op, 13, col, weight="bold" if op.endswith(":") is False else "normal")
        s += text(ax + 290, yy + i * 19, "; " + cmt, 10.5, GREY)

    # ── праворуч-знизу: RISC-V ───────────────────────────────────────────
    s += rect(ax, 288, aw, 198, "#fff8f0", ORANGE, 1.8, 12)
    s += text(ax + 16, 310, "RISC-V  (новіші ESP32-C, Pico 2…)", 12.5, ORANGE, "start", "bold")
    s += text(ax + aw - 14, 310, "objdump -d", 11, GREY, "end", "normal", family=MONO)
    rv = [
        ("  li     a5, 0", "sum = 0", GREEN),
        ("  blez   a1, .Lend", "якщо n<=0 — у кінець", PURPLE),
        (".Lloop:", "— початок тіла циклу —", GREY),
        ("  lw     a4, 0(a0)", "завантаж a[i]", INK),
        ("  add    a5, a5, a4", "sum += a[i]", RED),
        ("  addi   a0, a0, 4", "покажчик += 4 байти", INK),
        ("  addi   a1, a1, -1", "n--", INK),
        ("  bnez   a1, .Lloop", "ще є — назад", PURPLE),
    ]
    yy = 334
    for i, (op, cmt, col) in enumerate(rv):
        s += mono(ax + 14, yy + i * 19, op, 13, col)
        s += text(ax + 290, yy + i * 19, "; " + cmt, 10.5, GREY)

    # підсумкова смужка
    s += rect(cx, 296, cw, 150, "#fafafa", GREY, 1.4, 10)
    s += text(cx + cw / 2, 318, "що видно одразу", 11.5, INK, "middle", "bold")
    notes = [
        "• кожен рядок C → кілька команд",
        "• ідеї ті самі: load, add,",
        "   крок покажчика, лічильник,",
        "   умовний стрибок назад = ЦИКЛ",
        "• мнемоніки й імена регістрів",
        "   різні (a8 проти a5, l32i/lw)",
        "• «sum += a[i]» — це 3 команди,",
        "   а не одна",
    ]
    for i, nt in enumerate(notes):
        s += text(cx + 12, 338 + i * 14, nt, 9.6, INK)

    save("fig-18-4a-1-loop-to-asm.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.5.4a.2 — анатомія одного рядка дизасемблера (адреса|байти|мнемоніка)
# ════════════════════════════════════════════════════════════════════════════
def fig_anatomy():
    W, H = 960, 470
    s = header(W, H)
    s += text(W / 2, 30, "Анатомія одного рядка дизасемблера: чотири колонки",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 51, "objdump показує і число-команду, і її людський «правопис» — рядок у рядок, як у §3.5.4",
              11, GREY, "middle", style="italic")

    # реальний рядок objdump (RISC-V, стиль): адреса: байти   мнемоніка операнди
    rowy = 120
    s += rect(60, rowy - 30, W - 120, 56, "#fbfbff", INK, 1.6, 10)
    # колонки за x
    cols = [
        ("400d12a8:", 92, BLUE, "адреса в пам'яті"),
        ("00b50533", 250, PURPLE, "машинний код (байти команди)"),
        ("add", 430, RED, "мнемоніка (opcode)"),
        ("a0, a0, a1", 540, GREEN, "операнди (регістри)"),
    ]
    for txt, x, col, _lbl in cols:
        s += mono(x, rowy, txt, 17, col, weight="bold")

    # підписи-виноски під кожною колонкою (рознесені, щоб рамки не злипались)
    legy = 200
    boxes = [
        (92, 70, BLUE, "АДРЕСА", ["де команда лежить", "(сюди вказував PC,", "§3.5.2)"]),
        (252, 240, PURPLE, "БАЙТИ КОМАНДИ", ["те саме число, що", "в пам'яті; декодер", "ріже його на поля", "(§3.5.4, Рис. 3.5.4.2)"]),
        (430, 422, RED, "МНЕМОНІКА", ["що робити:", "тут — додати", "(opcode → дія)"]),
        (540, 712, GREEN, "ОПЕРАНДИ", ["над чим:", "a0 = a0 + a1", "(куди ← що, що)"]),
    ]
    bw = 156
    for x, bx, col, title, lines in boxes:
        s += arrow(x + 12, rowy + 16, bx + bw / 2, legy - 8, col, 1.6)
        s += rect(bx, legy, bw, 22 + len(lines) * 17, "#ffffff", col, 1.5, 8)
        s += text(bx + bw / 2, legy + 18, title, 11.5, col, "middle", "bold")
        for i, ln in enumerate(lines):
            s += text(bx + 10, legy + 38 + i * 16, ln, 10, INK)

    # нижній блок: те саме трьома мовами (зв'язок із Рис. 3.5.4.3 теми)
    by = 360
    s += rect(60, by, W - 120, 86, "#fafafa", GREY, 1.4, 10)
    s += text(W / 2, by + 22, "одна команда — три погляди (як у §3.5.4)", 12.5, INK, "middle", "bold")
    s += mono(120, by + 52, "0x00b50533", 14.5, PURPLE, weight="bold")
    s += text(120, by + 70, "число в пам'яті", 10, GREY)
    s += text(330, by + 52, "→", 18, INK)
    s += mono(380, by + 52, "add  a0, a0, a1", 14.5, RED, weight="bold")
    s += text(380, by + 70, "асемблер (мнемоніка)", 10, GREY)
    s += text(640, by + 52, "→", 18, INK)
    s += mono(690, by + 52, "a0 = a0 + a1", 14.5, GREEN, weight="bold")
    s += text(690, by + 70, "що це означає", 10, GREY)

    save("fig-18-4a-2-anatomy.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.5.4a.3 — той самий код, два рівні оптимізації: -O0 проти -O2
# ════════════════════════════════════════════════════════════════════════════
def fig_optimization():
    W, H = 960, 500
    s = header(W, H)
    s += text(W / 2, 30, "Сюрприз дизасемблера: компілятор НЕ перекладає рядок-у-рядок",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 51, "той самий цикл суми з -O0 і з -O2 — оптимізатор перебудовує код до невпізнанності",
              11, GREY, "middle", style="italic")

    # спільний C згори
    s += rect(W / 2 - 200, 70, 400, 64, "#fbfbff", BLUE, 1.6, 10)
    s += text(W / 2, 90, "вихідний C (однаковий для обох):", 11, BLUE, "middle", "bold")
    s += mono(W / 2, 116, "for (i=0;i<n;i++) sum += a[i];", 14, INK, "middle")

    s += arrow(W / 2 - 150, 140, 260, 178, INK, 2.2)
    s += text(W / 2 - 150, 162, "-O0", 11, GREY, "middle", "bold", family=MONO)
    s += arrow(W / 2 + 150, 140, 700, 178, INK, 2.2)
    s += text(W / 2 + 150, 162, "-O2", 11, GREY, "middle", "bold", family=MONO)

    # ── ліворуч: -O0 (наївно, рядок-у-рядок, через стек) ──
    lx, lw = 30, 440
    s += rect(lx, 184, lw, 286, "#fff6f6", RED, 1.8, 12)
    s += text(lx + 16, 206, "-O0  (без оптимізації)", 13, RED, "start", "bold")
    s += text(lx + 16, 224, "буквально, через пам'ять — довго, але «як написано»", 10, GREY, "start", style="italic")
    o0 = [
        "  sw    zero, sum(sp)      ; sum=0 у стек",
        ".L2:",
        "  lw    t0, i(sp)          ; узяти i зі стека",
        "  bge   t0, n, .Lend       ; i<n ?",
        "  lw    t0, i(sp)          ; i знову",
        "  slli  t1, t0, 2          ; i*4 (зсув)",
        "  add   t1, base, t1       ; &a[i]",
        "  lw    t1, 0(t1)          ; a[i]",
        "  lw    t2, sum(sp)        ; sum зі стека",
        "  add   t2, t2, t1         ; sum + a[i]",
        "  sw    t2, sum(sp)        ; назад у стек",
        "  lw    t0, i(sp)          ; i++ ...",
        "  addi  t0, t0, 1",
        "  sw    t0, i(sp)",
        "  j     .L2                ; знову",
    ]
    for i, ln in enumerate(o0):
        col = INK
        if ln.strip().startswith("."):
            col = GREY
        s += mono(lx + 14, 244 + i * 14.7, ln, 11, col)
    s += text(lx + lw / 2, 466, "≈ 15 команд у тілі · усе ганяє через стек", 10, RED, "middle", "bold")

    # ── праворуч: -O2 (регістри, тісний цикл) ──
    rx, rw = 490, 440
    s += rect(rx, 184, rw, 286, "#f6fbf6", GREEN, 1.8, 12)
    s += text(rx + 16, 206, "-O2  (оптимізовано)", 13, GREEN, "start", "bold")
    s += text(rx + 16, 224, "усе в регістрах, тіло стиснуте — те саме за змістом", 10, GREY, "start", style="italic")
    o2 = [
        "  li    a5, 0             ; sum=0 (регістр)",
        "  blez  a1, .Lend         ; n<=0 ? вийти",
        ".L3:",
        "  lw    a4, 0(a0)         ; a[i]",
        "  addi  a0, a0, 4         ; покажчик далі",
        "  add   a5, a5, a4        ; sum += a[i]",
        "  bne   a0, a3, .L3       ; не кінець? — назад",
        "  ...",
        "  mv    a0, a5            ; повернути sum",
        "  ret",
    ]
    for i, ln in enumerate(o2):
        col = INK
        if ln.strip().startswith("."):
            col = GREY
        s += mono(rx + 14, 250 + i * 18, ln, 12, col)
    s += text(rx + rw / 2, 466, "≈ 4 команди у тілі · жодного звертання в стек", 10, GREEN, "middle", "bold")

    save("fig-18-4a-3-optimization.svg", s)


if __name__ == "__main__":
    fig_loop_to_asm()
    fig_anatomy()
    fig_optimization()
    print("OK")
