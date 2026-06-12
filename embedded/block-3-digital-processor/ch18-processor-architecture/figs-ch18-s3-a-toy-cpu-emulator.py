# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для ВСТАВКИ ⚙️ «Іграшковий процесор-емулятор» (до теми 3.5.3).
Окремий скрипт — головний figs.py розділу не чіпаємо. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif.
Підписи фігур у тексті — «Рис. 3.5.3a.k» (вставка до теми 3.5.3).
Допоміжні функції — копія зі стилю розділу 18, щоб вигляд був єдиний.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"
MONO  = "Consolas, 'DejaVu Sans Mono', monospace"


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
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", AMBER: "aAmber"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = MONO if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═══════════ Рис. 3.5.3a.1 — цикл fetch–decode–execute ↔ код на C ════════════
def fig_loop():
    W, H = 920, 560
    s = header(W, H)
    s += text(W / 2, 34, "Серцебиття процесора (§3.5.3) — рядок-у-рядок у коді емулятора",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "ліворуч — три фази циклу з теми; праворуч — той самий цикл у while-петлі на C; стрілки єднають фазу з її рядком",
              11.5, GREY, "middle", style="italic")

    # ── ліворуч: три фази по колу ──
    cx, cy, r = 230, 320, 150
    s += circle(cx, cy, r, "none", FAINT, 2)
    phases = [
        ("ВИБІРКА", "fetch", "ip → байт із code[]\nдекодувати opcode", GREEN, -90),
        ("ВИКОНАННЯ", "execute", "switch(op): зробити\n(+ , LD, ST, JMP…)", RED, 30),
        ("(наступний оберт)", "", "ip уже вказує далі —\nколо замикається", BLUE, 150),
    ]
    import math
    pts = []
    for i, (title, en, body, col, ang) in enumerate(phases):
        a = math.radians(ang)
        px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        pts.append((px, py, col))
    # дуги-стрілки між фазами (за годинниковою)
    for i in range(3):
        x1, y1, c1 = pts[i]
        x2, y2, _ = pts[(i + 1) % 3]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        # вигнути назовні від центру
        ox, oy = mx - cx, my - cy
        nl = math.hypot(ox, oy) or 1
        bx, by = mx + ox / nl * 26, my + oy / nl * 26
        s += path(f"M{x1:.0f},{y1:.0f} Q{bx:.0f},{by:.0f} {x2:.0f},{y2:.0f}", "none", c1, 2.4)
    # маркер напряму
    s += text(cx, cy - 4, "цикл", 13, GREY, "middle", "bold")
    s += text(cx, cy + 16, "крутиться", 13, GREY, "middle", "bold")
    nodes = [
        (pts[0][0], pts[0][1], "ВИБІРКА", "(fetch)", "code[ip]", GREEN, "below"),
        (pts[1][0], pts[1][1], "ВИКОНАННЯ", "(execute)", "switch(op)", RED, "right"),
        (pts[2][0], pts[2][1], "наступна", "команда", "ip готовий", BLUE, "left"),
    ]
    for (px, py, t1, t2, t3, col, side) in nodes:
        s += circle(px, py, 11, "#fff", col, 3)
        s += circle(px, py, 4.5, col, col, 1)
        if side == "below":
            s += text(px, py - 22, t1, 14, col, "middle", "bold")
            s += text(px, py - 6, t2, 11, col, "middle", style="italic")
        elif side == "right":
            s += text(px + 20, py - 4, t1, 14, col, "start", "bold")
            s += text(px + 20, py + 13, t2, 11, col, "start", style="italic")
        else:
            s += text(px - 20, py - 4, t1, 14, col, "end", "bold")
            s += text(px - 20, py + 13, t2, 11, col, "end", style="italic")
    s += text(cx, H - 22, "«декодування» зливається з вибіркою:", 11, INK, "middle", "bold")
    s += text(cx, H - 6, "розрізати байт на op та операнди (§3.5.3)", 11, INK, "middle")

    # ── праворуч: код на C ──
    bx, by, bw, bh = 470, 96, 430, 432
    s += rect(bx, by, bw, bh, "#0e1116", "#0e1116", 0, 12)
    s += text(bx + 18, by + 26, "// ядро емулятора", 13.5, "#7fd58f", "start", mono=True)
    code = [
        ("while (running) {", "#e8e8e8"),
        ("    byte op = code[ip++];   // ВИБІРКА", GREEN),
        ("    byte a  = code[ip++];   //  +декод", GREEN),
        ("    switch (op) {           // ВИКОНАННЯ", RED),
        ("      case HLT: running = 0; break;", "#caa24a"),
        ("      case LD:  r[a]=code[ip++]; break;", RED),
        ("      case ADD: r[a]+=r[code[ip++]];", RED),
        ("                break;", RED),
        ("      case ST:  mem[code[ip++]]=r[a];", RED),
        ("                break;", RED),
        ("      case JMP: ip = a;      break;", BLUE),
        ("      // ... решта з 8-ми опкодів ...", "#9aa0a6"),
        ("    }", "#e8e8e8"),
        ("}", "#e8e8e8"),
    ]
    yy = by + 56
    for item in code:
        txt = item[0]
        col = item[1]
        s += text(bx + 18, yy, txt, 14, col, "start", mono=True)
        yy += 26
    # зв'язки фаза → рядок
    s += arrow(pts[0][0] + 14, pts[0][1] - 18, bx + 8, by + 56 + 26 - 4, GREEN, 2)
    s += arrow(pts[1][0] + 70, pts[1][1] + 6, bx + 8, by + 56 + 26 * 3 - 4, RED, 2)
    save("fig-3-5-3a-1-loop.svg", s)


# ═══════════ Рис. 3.5.3a.2 — набір з 8 інструкцій (ISA іграшки) ══════════════
def fig_isa():
    W, H = 920, 520
    s = header(W, H)
    s += text(W / 2, 34, "Уся «мова» іграшкового процесора: рівно 8 інструкцій",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "крихітний словник (§3.5.4) — та цих восьми досить, щоб писати справжні програми з лічбою, циклами й гілками",
              11.5, GREY, "middle", style="italic")
    # таблиця
    cols = [
        ("opcode", 70),
        ("мнемоніка", 150),
        ("байти", 150),
        ("що робить", 360),
        ("родина", 130),
    ]
    x0 = 30
    colx = [x0]
    for _, w in cols:
        colx.append(colx[-1] + w)
    top = 84
    rowh = 44
    # шапка
    s += rect(x0, top, colx[-1] - x0, rowh, "#eef2f7", INK, 1.6, 6)
    for i, (name, w) in enumerate(cols):
        s += text(colx[i] + 12, top + 28, name, 13.5, INK, "start", "bold")
    rows = [
        ("0", "HLT", "0  –  –", "зупинити машину (running ← 0)", "плин", AMBER),
        ("1", "LD  r,n", "1  r  n", "r ← n  (поклади число n у регістр)", "дані", BLUE),
        ("2", "LDM r,a", "2  r  a", "r ← mem[a]  (читати з пам'яті)", "дані", BLUE),
        ("3", "ST  r,a", "3  r  a", "mem[a] ← r  (писати в пам'ять)", "дані", BLUE),
        ("4", "ADD r,s", "4  r  s", "r ← r + s  (АЛП: §3.5.2)", "арифм.", RED),
        ("5", "SUB r,s", "5  r  s", "r ← r − s  (заразом для порівнянь)", "арифм.", RED),
        ("6", "JMP a", "6  a  –", "ip ← a  (безумовний стрибок)", "плин", GREEN),
        ("7", "JNZ r,a", "7  r  a", "якщо r≠0 → ip ← a  (цикл/гілка)", "плин", GREEN),
    ]
    for i, (op, mn, by, what, fam, col) in enumerate(rows):
        ry = top + rowh + i * rowh
        bg = "#ffffff" if i % 2 == 0 else "#f7f9fb"
        s += rect(x0, ry, colx[-1] - x0, rowh, bg, FAINT, 1.2, 0)
        # opcode badge
        s += rect(colx[0] + 16, ry + 9, 26, 26, "#f0f0f0", col, 1.8, 5)
        s += text(colx[0] + 29, ry + 27, op, 14, col, "middle", "bold", mono=True)
        s += text(colx[1] + 12, ry + 28, mn, 14, INK, "start", "bold", mono=True)
        s += text(colx[2] + 12, ry + 28, by, 13.5, GREY, "start", mono=True)
        s += text(colx[3] + 12, ry + 28, what, 13, INK, "start")
        s += text(colx[4] + 12, ry + 28, fam, 12.5, col, "start", "bold")
    # рамка таблиці
    s += rect(x0, top, colx[-1] - x0, rowh * (len(rows) + 1), "none", INK, 1.8, 6)
    # вертикальні лінії
    for i in range(1, len(cols)):
        s += line(colx[i], top, colx[i], top + rowh * (len(rows) + 1), FAINT, 1)
    s += text(W / 2, H - 14,
              "Кожна команда — 1–3 байти в пам'яті: один байт opcode + до двох операндів. Декодер просто читає їх по черзі.",
              12, INK, "middle", "bold")
    save("fig-3-5-3a-2-isa.svg", s)


# ═══════════ Рис. 3.5.3a.3 — трасування: програма біжить такт за тактом ══════
def fig_trace():
    W, H = 920, 600
    s = header(W, H)
    s += text(W / 2, 34, "Емулятор «біжить»: множення 6×3 додаванням — стан машини на кожному оберті",
              19, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама механіка, що в трасі §3.5.3 (Рис. 3.5.3.5), лише тепер її друкує наш цикл while — оберт за обертом",
              11.5, GREY, "middle", style="italic")

    # ── ліворуч: програма в пам'яті ──
    px, py = 36, 92
    s += text(px, py - 6, "програма в code[] (адреси зліва):", 13, INK, "start", "bold")
    prog = [
        ("0", "LD  r0, 0", "акумулятор = 0"),
        ("3", "LD  r1, 3", "лічильник = 3"),
        ("6", "ADD r0, r2", "r0 += 6   ← тіло циклу"),
        ("9", "SUB r1, r3", "r1 -= 1"),
        ("12", "JNZ r1, 6", "якщо r1≠0 → на адресу 6"),
        ("15", "HLT", "стоп; відповідь — у r0"),
    ]
    for i, (a, instr, cm) in enumerate(prog):
        ry = py + 14 + i * 34
        hot = (i in (2, 3, 4))
        bg = "#fff7e8" if hot else "#f6f8fb"
        ec = AMBER if hot else BLUE
        s += rect(px, ry, 250, 28, bg, ec, 1.6, 4)
        s += text(px + 10, ry + 19, a.rjust(2), 12.5, GREY, "start", mono=True)
        s += text(px + 44, ry + 19, instr, 13, INK, "start", "bold", mono=True)
    s += path(f"M{px+150},{py+14+4*34+14} C{px+300},{py+14+4*34+40} {px+300},{py+14+2*34-10} {px+150+8},{py+14+2*34+6}",
              "none", AMBER, 2.2)
    s += text(px + 256, py + 14 + 3 * 34 + 4, "цикл", 11, AMBER, "start", "bold")
    s += text(px, py + 14 + 6 * 34 + 18, "(r2=6, r3=1 — наперед задані сталі)", 11, GREY, "start", style="italic")

    # ── праворуч: таблиця станів ──
    tx = 330
    s += text(tx, py - 6, "стан після кожного OUT-оберту циклу (ip, r0, r1):", 13, INK, "start", "bold")
    heads = ["оберт", "що сталося", "r0 (сума)", "r1 (лічб.)"]
    hx = [tx, tx + 80, tx + 320, tx + 440]
    hw = [80, 240, 120, 110]
    top = py + 12
    rowh = 38
    s += rect(tx, top, 550, rowh, "#eef2f7", INK, 1.6, 6)
    for i, hd in enumerate(heads):
        s += text(hx[i] + 12, top + 25, hd, 12.5, INK, "start", "bold")
    trace = [
        ("старт", "LD r0,0 ; LD r1,3", "0", "3", INK),
        ("1", "r0+=6 ; r1-=1 ; r1≠0→стриб", "6", "2", RED),
        ("2", "r0+=6 ; r1-=1 ; r1≠0→стриб", "12", "1", RED),
        ("3", "r0+=6 ; r1-=1 ; r1=0 → далі", "18", "0", GREEN),
        ("стоп", "JNZ не стрибнув ; HLT", "18", "0", AMBER),
    ]
    for i, (st, ev, r0, r1, col) in enumerate(trace):
        ry = top + rowh + i * rowh
        bg = "#ffffff" if i % 2 == 0 else "#f7f9fb"
        s += rect(tx, ry, 550, rowh, bg, FAINT, 1.2, 0)
        s += text(hx[0] + 12, ry + 24, st, 12.5, col, "start", "bold")
        s += text(hx[1] + 12, ry + 24, ev, 12, INK, "start", mono=True)
        s += text(hx[2] + 26, ry + 24, r0, 14, col, "start", "bold", mono=True)
        s += text(hx[3] + 26, ry + 24, r1, 14, col, "start", "bold", mono=True)
    s += rect(tx, top, 550, rowh * (len(trace) + 1), "none", INK, 1.8, 6)
    for i in range(1, len(heads)):
        s += line(hx[i], top, hx[i], top + rowh * (len(trace) + 1), FAINT, 1)

    # підсумок-результат
    ry = top + rowh * (len(trace) + 1) + 26
    s += rect(tx, ry, 550, 96, "#f4f7f4", GREEN, 1.8, 10)
    s += text(tx + 18, ry + 28, "Відповідь у r0: 6 + 6 + 6 = 18 = 6×3.", 15, GREEN, "start", "bold")
    s += text(tx + 18, ry + 52, "Множення «зникло» — лишилося додавання в циклі, кероване JNZ.", 12.5, INK, "start")
    s += text(tx + 18, ry + 74, "Жодної магії: ip веде по code[], switch робить дію, петля крутиться.", 12.5, INK, "start")
    save("fig-3-5-3a-3-trace.svg", s)


if __name__ == "__main__":
    fig_loop()
    fig_isa()
    fig_trace()
    print("toy-cpu insert figures done.")
