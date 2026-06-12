# -*- coding: utf-8 -*-
"""
SVG-фігури для ⚙️-вставки §3.3.9a — «Автомат у коді: switch проти таблиці переходів».
Окремий генератор (головний figs.py не чіпаємо), чистий Python без залежностей.
Вивід → ./img/. Стиль за AUTHORING §9: білий фон; активне/«1» червоний,
пасивне/«0» синій; висновок/поле — зелене; стрілки через marker; шрифт sans-serif.

Фігури:
  fig-16-9a-1-two-ways.svg   — той самий автомат двома способами: switch-код vs таблиця переходів
  fig-16-9a-2-dispatch.svg   — диспетчеризація події: каскад if/switch (O(N)) vs індекс у таблицю (O(1))
  fig-16-9a-3-pitfalls.svg   — граблі на МК: діри в таблиці, дія на вході vs на переході, default→безпечно
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
PALE  = "#f4f7ff"
PALEG = "#eef7f0"
PALER = "#fbeeee"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


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
    fam = "Consolas, 'Courier New', monospace" if mono else FONT
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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# Спільний приклад на всі фігури — мінімальний автомат «турнікета»:
#   стани:  LOCKED (зачинено), OPEN (відчинено)
#   події:  COIN (вкинули жетон), PUSH (штовхнули)
# Це канонічний навчальний FSM; на ньому видно і таблицю, і switch, і дію переходу.
STATES = ["LOCKED", "OPEN"]
EVENTS = ["COIN", "PUSH"]
# next[state][event] -> (новий_стан, дія)
TABLE = {
    ("LOCKED", "COIN"): ("OPEN",   "unlock"),
    ("LOCKED", "PUSH"): ("LOCKED", "—"),       # штовхати зачинене — нічого (можна: alarm)
    ("OPEN",   "COIN"): ("OPEN",   "—"),       # зайвий жетон — ігнор
    ("OPEN",   "PUSH"): ("LOCKED", "lock"),    # пройшли — знову зачиняємо
}


# ── Фігура 1: той самий автомат двома способами ──────────────────────────────
def fig1_two_ways():
    W, H = 920, 560
    b = header(W, H)
    b += text(W/2, 30, "Один автомат — два втілення: код-розгалуження проти таблиці-даних",
              17, INK, "middle", "bold")
    b += text(W/2, 52, "приклад: турнікет {LOCKED, OPEN}, події {COIN, PUSH}",
              13, GREY, "middle", style="italic")

    # ── ЛІВОРУЧ: switch(state){ switch(event) } як «дерево» коду ──
    lx = 40
    b += text(lx + 200, 84, "А. switch: логіка живе в КОДІ", 15, BLUE, "middle", "bold")
    code = [
        "switch (state) {",
        "  case LOCKED:",
        "    if (ev==COIN){ unlock();",
        "                   state=OPEN; }",
        "    else /*PUSH*/  ; // нічого",
        "    break;",
        "  case OPEN:",
        "    if (ev==PUSH){ lock();",
        "                   state=LOCKED; }",
        "    else /*COIN*/  ; // ігнор",
        "    break;",
        "}",
    ]
    cw, ch = 410, 26
    cy0 = 100
    b += rect(lx, cy0 - 4, cw, len(code) * ch + 14, PALE, BLUE, 2, 10)
    for i, ln in enumerate(code):
        col = INK
        if "case" in ln:
            col = BLUE
        if "unlock" in ln or "lock(" in ln:
            col = RED
        b += text(lx + 16, cy0 + 18 + i * ch, ln, 14, col, "start", mono=True)
    b += text(lx + 200, cy0 + len(code) * ch + 34,
              "кожен стан і подія — окрема гілка; додати стан = правити код",
              12, BLUE, "middle", style="italic")

    # ── ПРАВОРУЧ: таблиця переходів як ДАНІ ──
    tx = 540
    b += text(tx + 165, 84, "Б. таблиця: логіка живе в ДАНИХ", 15, GREEN, "middle", "bold")
    # сітка 2 події × 2 стани, з осями
    gx, gy = tx + 90, 120
    colw, rowh = 130, 78
    # заголовки колонок (події)
    b += text(gx - 12, gy - 14, "стан \\ подія", 12, GREY, "end")
    for j, ev in enumerate(EVENTS):
        b += text(gx + j * colw + colw / 2, gy - 12, ev, 14, INK, "middle", "bold", mono=True)
    # рядки (стани)
    for i, st in enumerate(STATES):
        ry = gy + i * rowh
        b += text(gx - 12, ry + rowh / 2 + 5, st, 14, INK, "end", "bold", mono=True)
        for j, ev in enumerate(EVENTS):
            cx = gx + j * colw
            ns, act = TABLE[(st, ev)]
            changed = ns != st
            fill = PALEG if changed else "#ffffff"
            edge = GREEN if changed else FAINT
            b += rect(cx, ry, colw, rowh, fill, edge, 2, 6)
            ncol = RED if changed else BLUE
            b += text(cx + colw / 2, ry + 30, "→ " + ns, 13, ncol, "middle", "bold", mono=True)
            acol = RED if act not in ("—",) else GREY
            b += text(cx + colw / 2, ry + 54, "/ " + act, 12, acol, "middle", mono=True)
    # підпис під таблицею
    ty2 = gy + len(STATES) * rowh
    b += text(tx + 165, ty2 + 26,
              "next[state][event] = (новий стан, дія)", 13, INK, "middle", mono=True)
    b += text(tx + 165, ty2 + 46,
              "додати стан = дописати РЯДОК, рушій той самий", 12, GREEN, "middle", style="italic")

    # ── міст між підходами: однаковий перехід підсвічено ──
    b += text(W/2, H - 64, "Обидва описують ТЕ САМЕ: у стані LOCKED подія COIN → unlock() і перехід в OPEN.",
              13, INK, "middle", "bold")
    b += text(W/2, H - 42,
              "Зліва це гілка коду, справа — клітина даних. Таблиця відділяє «що робить автомат» від «як його крутить рушій».",
              12, GREEN, "middle", style="italic")
    b += text(W/2, H - 20,
              "(Рядки таблиці — це банк тригерів зі стану §3.3.1, що тримає поточний стан; рушій лише оновлює його по події.)",
              11, GREY, "middle", style="italic")
    save("fig-16-9a-1-two-ways.svg", b)


# ── Фігура 2: диспетчеризація події — каскад порівнянь проти індексації ──────
def fig2_dispatch():
    W, H = 900, 470
    b = header(W, H)
    b += text(W/2, 30, "Як подія знаходить свій перехід: каскад порівнянь проти прямого індексу",
              16, INK, "middle", "bold")

    # ── ЛІВОРУЧ: switch / if-каскад = ланцюг порівнянь, O(станів × подій) у найгіршому ──
    lx = 70
    b += text(lx + 120, 70, "switch / if-каскад", 15, BLUE, "middle", "bold")
    # вхід «подія»
    b += rect(lx + 40, 86, 160, 32, PALE, BLUE, 2, 8)
    b += text(lx + 120, 108, "подія (state, ev)", 13, INK, "middle", mono=True)
    # ланцюг ромбів-порівнянь
    ys = [152, 212, 272, 332]
    qs = ["state==LOCKED ?", "ev==COIN ?", "ev==PUSH ?", "… ще гілки …"]
    px = lx + 120
    prev = (px, 118)
    for i, (yy, q) in enumerate(zip(ys, qs)):
        # ромб
        hw, hh = 92, 24
        pts = f"{px-hw},{yy} {px},{yy-hh} {px+hw},{yy} {px},{yy+hh}"
        last = i == len(ys) - 1
        col = GREY if last else BLUE
        b += f'<polygon points="{pts}" fill="#ffffff" stroke="{col}" stroke-width="2"/>\n'
        b += text(px, yy + 4, q, 12, col, "middle", mono=True)
        b += arrow(prev[0], prev[1], px, yy - hh, BLUE if i else INK, 1.8)
        # «ні» вбік
        b += text(px + hw + 8, yy + 4, "ні →", 11, GREY, "start")
        prev = (px, yy + hh)
    b += text(lx + 120, 372, "перевіряємо гілку за гілкою згори вниз", 11, BLUE, "middle", style="italic")
    b += rect(lx + 8, 392, 224, 30, PALER, RED, 2, 8)
    b += text(lx + 120, 412, "час росте з числом станів × подій", 12, RED, "middle", "bold")

    # роздільник
    b += line(W/2, 64, W/2, 430, FAINT, 2, "5 5")

    # ── ПРАВОРУЧ: один індекс у двовимірну таблицю = O(1) ──
    rx = 500
    b += text(rx + 150, 70, "таблиця: один індекс", 15, GREEN, "middle", "bold")
    b += rect(rx + 70, 86, 160, 32, PALE, BLUE, 2, 8)
    b += text(rx + 150, 108, "подія (state, ev)", 13, INK, "middle", mono=True)
    b += text(rx + 150, 150, "next[state][ev]", 12, GREEN, "middle", "bold", mono=True)
    # маленька таблиця 2×2
    gx, gy = rx + 96, 206
    colw, rowh = 96, 58
    for j, ev in enumerate(EVENTS):
        hdrx = gx + j * colw + colw / 2
        # заголовок COIN зсунутий праворуч, щоб не лягти під стрілку-індекс
        b += text(hdrx + (16 if j == 0 else 0), gy - 10, ev, 12, GREY, "middle", mono=True)
    for i, st in enumerate(STATES):
        ry = gy + i * rowh
        b += text(gx - 10, ry + rowh / 2 + 4, st, 12, GREY, "end", mono=True)
        for j in range(len(EVENTS)):
            cx = gx + j * colw
            hit = (i == 0 and j == 0)
            fill = PALEG if hit else "#ffffff"
            edge = GREEN if hit else FAINT
            b += rect(cx, ry, colw, rowh, fill, edge, 2.4 if hit else 1.6, 6)
            if hit:
                b += text(cx + colw / 2, ry + 26, "→OPEN", 12, RED, "middle", "bold", mono=True)
                b += text(cx + colw / 2, ry + 44, "/unlock", 11, RED, "middle", mono=True)
    # стрілка прямо в клітину [LOCKED][COIN]: цілимось у лівий верх клітини
    b += arrow(rx + 150, 160, gx + 22, gy + 4, GREEN, 2.2)
    b += rect(rx + 38, 392, 224, 30, PALEG, GREEN, 2, 8)
    b += text(rx + 150, 412, "час сталий — одне читання з пам'яті", 12, GREEN, "middle", "bold")

    save("fig-16-9a-2-dispatch.svg", b)


# ── Фігура 3: три класичні граблі автомата на МК ─────────────────────────────
def fig3_pitfalls():
    W, H = 940, 540
    b = header(W, H)
    b += text(W/2, 30, "Три пастки автомата на мікроконтролері — і як їх закрити",
              16, INK, "middle", "bold")

    colw = 296
    x0 = 18
    top = 60
    boxh = 430

    # ── панель 1: «діри» в таблиці (незадані переходи) ──
    p1 = x0
    b += rect(p1, top, colw, boxh, "#ffffff", FAINT, 2, 12)
    b += text(p1 + colw / 2, top + 26, "1. Діри: незаданий перехід", 14, INK, "middle", "bold")
    # таблиця з порожньою клітиною
    gx, gy = p1 + 48, top + 56
    cw, rh = 92, 50
    evs = ["COIN", "PUSH"]
    sts = ["LOCKED", "OPEN"]
    cells = {(0, 0): ("OPEN", GREEN), (0, 1): ("LOCKED", GREEN),
             (1, 0): ("OPEN", GREEN), (1, 1): ("???", RED)}
    for j, ev in enumerate(evs):
        b += text(gx + j * cw + cw / 2, gy - 8, ev, 11, GREY, "middle", mono=True)
    for i, st in enumerate(sts):
        ry = gy + i * rh
        b += text(gx - 8, ry + rh / 2 + 4, st, 11, GREY, "end", mono=True)
        for j in range(2):
            cx = gx + j * cw
            ns, col = cells[(i, j)]
            hole = ns == "???"
            b += rect(cx, ry, cw, rh, PALER if hole else "#ffffff", RED if hole else FAINT, 2 if hole else 1.4, 5)
            b += text(cx + cw / 2, ry + rh / 2 + 4, ns, 12, col, "middle", "bold" if hole else "normal", mono=True)
    b += text(p1 + colw / 2, gy + 2 * rh + 26,
              "забута клітина → стан «упав» у NULL", 11, RED, "middle")
    b += rect(p1 + 16, top + boxh - 96, colw - 32, 78, PALEG, GREEN, 2, 8)
    b += text(p1 + colw / 2, top + boxh - 74, "Лік:", 12, GREEN, "middle", "bold")
    b += text(p1 + colw / 2, top + boxh - 56, "заповнити ВСІ клітини явно;", 11, INK, "middle")
    b += text(p1 + colw / 2, top + boxh - 40, "невідому подію → лишитись на місці", 11, INK, "middle")
    b += text(p1 + colw / 2, top + boxh - 24, "або піти в безпечний стан + лог", 11, INK, "middle")

    # ── панель 2: дія на ВХОДІ (Мур) vs на ПЕРЕХОДІ (Мілі) ──
    p2 = x0 + colw + 14
    b += rect(p2, top, colw, boxh, "#ffffff", FAINT, 2, 12)
    b += text(p2 + colw / 2, top + 26, "2. Де викликати дію?", 14, INK, "middle", "bold")
    # Мур: дія в стані
    cy = top + 64
    b += circle(p2 + 70, cy, 30, PALE, BLUE, 2)
    b += text(p2 + 70, cy - 2, "OPEN", 12, BLUE, "middle", "bold", mono=True)
    b += text(p2 + 70, cy + 14, "/ unlock", 10, RED, "middle", mono=True)
    b += text(p2 + 70, cy + 46, "Мур: дія НА ВХОДІ", 11, BLUE, "middle", "bold")
    b += text(p2 + 70, cy + 62, "в стан (on_enter)", 10, GREY, "middle")
    # Мілі: дія на стрілці
    ax1, ax2 = p2 + 170, p2 + 268
    b += circle(ax1, cy, 24, "#ffffff", INK, 2)
    b += text(ax1, cy + 4, "LCK", 10, INK, "middle", mono=True)
    b += circle(ax2, cy, 24, "#ffffff", INK, 2)
    b += text(ax2, cy + 4, "OPN", 10, INK, "middle", mono=True)
    b += arrow(ax1 + 24, cy, ax2 - 24, cy, RED, 2)
    b += text((ax1 + ax2) / 2, cy - 16, "COIN", 10, INK, "middle", mono=True)
    b += text((ax1 + ax2) / 2, cy + 40, "Мілі: дія НА", 11, RED, "middle", "bold")
    b += text((ax1 + ax2) / 2, cy + 56, "ПЕРЕХОДІ (стрілці)", 10, GREY, "middle")
    # застереження
    b += rect(p2 + 16, top + boxh - 150, colw - 32, 56, PALER, RED, 2, 8)
    b += text(p2 + colw / 2, top + boxh - 130, "Пастка:", 12, RED, "middle", "bold")
    b += text(p2 + colw / 2, top + boxh - 112, "дія на вході спрацює ЩЕ РАЗ,", 11, INK, "middle")
    b += text(p2 + colw / 2, top + boxh - 96, "якщо стан перейшов сам у себе", 11, INK, "middle")
    b += rect(p2 + 16, top + boxh - 80, colw - 32, 62, PALEG, GREEN, 2, 8)
    b += text(p2 + colw / 2, top + boxh - 58, "Лік: обери ОДНУ модель", 11, GREEN, "middle", "bold")
    b += text(p2 + colw / 2, top + boxh - 42, "і клич on_enter лише на", 11, INK, "middle")
    b += text(p2 + colw / 2, top + boxh - 26, "СПРАВЖНІЙ зміні стану", 11, INK, "middle")

    # ── панель 3: default → безпечний стан ──
    p3 = x0 + 2 * (colw + 14)
    b += rect(p3, top, colw, boxh, "#ffffff", FAINT, 2, 12)
    b += text(p3 + colw / 2, top + 26, "3. default = безпека", 14, INK, "middle", "bold")
    code = [
        "ev = read_event();",
        "if (!valid(state,ev)) {",
        "    log(\"bad transition\");",
        "    state = SAFE;   // failsafe",
        "    return;",
        "}",
        "n = next[state][ev];",
        "if (n.act) n.act();",
        "state = n.to;",
    ]
    cy0 = top + 52
    b += rect(p3 + 14, cy0 - 4, colw - 28, len(code) * 22 + 12, PALE, BLUE, 1.6, 8)
    for i, ln in enumerate(code):
        col = INK
        if "SAFE" in ln or "failsafe" in ln or "bad" in ln:
            col = RED
        if "next[" in ln or "act()" in ln:
            col = GREEN
        b += text(p3 + 24, cy0 + 16 + i * 22, ln, 11.5, col, "start", mono=True)
    b += rect(p3 + 16, top + boxh - 96, colw - 32, 78, PALEG, GREEN, 2, 8)
    b += text(p3 + colw / 2, top + boxh - 74, "Думка:", 12, GREEN, "middle", "bold")
    b += text(p3 + colw / 2, top + boxh - 56, "у залізі вхід буває «брудний»", 11, INK, "middle")
    b += text(p3 + colw / 2, top + boxh - 40, "(шум, збій, чужа подія) —", 11, INK, "middle")
    b += text(p3 + colw / 2, top + boxh - 24, "автомат мусить мати куди впасти", 11, INK, "middle")

    # підсумковий рядок
    b += text(W/2, H - 14,
              "Спільне правило: автомат не має «зависати» на невідомому — кожен стан і кожна подія мусять мати визначений вихід.",
              12, GREEN, "middle", "bold")
    save("fig-16-9a-3-pitfalls.svg", b)


if __name__ == "__main__":
    fig1_two_ways()
    fig2_dispatch()
    fig3_pitfalls()
    print("ch16-s9-a-fsm-in-code figures done.")
