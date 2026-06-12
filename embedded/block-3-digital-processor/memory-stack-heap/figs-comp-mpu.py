# -*- coding: utf-8 -*-
"""
Генератор SVG для 🔌-вставки §3.6.7c — «MPU: апаратні стіни між задачами».
Окремий від головного figs.py (його не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/. Стиль (AUTHORING §9) — спільні допоміжні функції скопійовано
з figs.py розділу, щоб вигляд був єдиний: білий фон, «1»/«+» червоний, «0»/«−»
синій, поле зелене, стрілки через marker, sans-serif.

Фігури тут — три, кожна несе вагу (§9):
  fig-19-7c-1  MPU як застава між ядром і пам'яттю: кожен доступ звіряється з правами
  fig-19-7c-2  таблиця регіонів: база/межа + права (RWX, priv/unpriv) для кожної зони
  fig-19-7c-3  чому стек не затопить сусіда: глуха смуга-вартовий ловить переповнення
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


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ════════════ Рис. 3.6.7c.1 — MPU як застава між ядром і пам'яттю ═════════════
def fig_checkpoint():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 34, "MPU — застава на шляху кожного доступу до пам'яті", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ядро не дотягується до пам'яті напряму: між ними сидить вартовий, що звіряє кожне звернення з таблицею прав",
              11.5, GREY, "middle", style="italic")

    # ── ядро ліворуч ──
    cx, cy, cw, ch = 60, 150, 170, 130
    s += rect(cx, cy, cw, ch, "#f7f9fc", BLUE, 2.2, 12)
    s += text(cx + cw / 2, cy + 30, "ядро CPU", 15, BLUE, "middle", "bold")
    s += text(cx + cw / 2, cy + 54, "виконує код,", 10.5, GREY, "middle")
    s += text(cx + cw / 2, cy + 70, "читає й пише", 10.5, GREY, "middle")
    s += text(cx + cw / 2, cy + 86, "змінні (§3.6.1)", 10.5, GREY, "middle")
    s += text(cx + cw / 2, cy + 110, "у привілейованому", 9.5, GREY, "middle", style="italic")
    s += text(cx + cw / 2, cy + 124, "чи звичайному режимі", 9.5, GREY, "middle", style="italic")

    # ── MPU посередині ──
    mx, my, mw, mh = 360, 120, 200, 200
    s += rect(mx, my, mw, mh, "#fff8e8", AMBER, 2.6, 14)
    s += text(mx + mw / 2, my + 30, "MPU", 18, INK, "middle", "bold")
    s += text(mx + mw / 2, my + 50, "Memory Protection Unit", 9.5, GREY, "middle", style="italic")
    s += text(mx + mw / 2, my + 70, "блок захисту пам'яті", 10.5, GREY, "middle")
    # внутрішня «таблиця прав»
    s += rect(mx + 24, my + 86, mw - 48, 88, "#ffffff", INK, 1.6, 8)
    s += text(mx + mw / 2, my + 104, "таблиця регіонів", 11, INK, "middle", "bold")
    for i, lab in enumerate(["регіон 0: база–межа, права", "регіон 1: база–межа, права",
                             "регіон 2: база–межа, права", "…"]):
        s += text(mx + 34, my + 122 + i * 15, lab, 8.6, GREY, "start")

    # ── пам'ять праворуч ──
    px, py, pw = 690, 96, 170
    s += text(px + pw / 2, py - 8, "адресний простір (§3.6.2)", 11, INK, "middle", "bold")
    zones = [
        (".text  код", GREEN, "RX"),
        (".rodata стал.", GREEN, "R"),
        (".data/.bss", BLUE, "RW"),
        ("купа", BLUE, "RW"),
        ("стек", BLUE, "RW"),
        ("MMIO периф.", RED, "RW"),
    ]
    zh = 42
    for i, (lab, col, perm) in enumerate(zones):
        y = py + i * zh
        s += rect(px, y, pw, zh - 6, "#ffffff", col, 1.8, 6)
        s += text(px + 10, y + 23, lab, 11, INK, "start", "bold")
        s += text(px + pw - 10, y + 23, perm, 11, col, "end", "bold")

    # ── шлях доступу: ядро → MPU → пам'ять ──
    s += arrow(cx + cw, cy + 40, mx, my + 110, INK, 2.4)
    s += text((cx + cw + mx) / 2, cy + 24, "доступ:", 10.5, INK, "middle", "bold")
    s += text((cx + cw + mx) / 2, cy + 38, "адреса + R/W/fetch", 9.5, GREY, "middle")

    # дозволено
    s += arrow(mx + mw, my + 80, px - 6, py + 70, GREEN, 2.4)
    s += text((mx + mw + px) / 2 + 8, my + 64, "права збігаються →", 9.5, GREEN, "middle", "bold")
    s += text((mx + mw + px) / 2 + 8, my + 78, "доступ дозволено", 9.5, GREEN, "middle")

    # заборонено → виняток
    s += arrow(mx + mw / 2, my + mh, mx + mw / 2, 392, RED, 2.4, dash="6,4")
    s += text(mx + mw / 2 + 8, 372, "права порушено →", 10, RED, "start", "bold")

    # плашка-виняток унизу
    s += rect(60, 392, W - 120, 62, "#fdf4f4", RED, 1.8, 10)
    s += text(W / 2, 414, "Звернення поза дозволеним (запис у код, вихід за межі, доступ не з того режиму) MPU не пускає —",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 436, "натомість збуджує апаратний виняток (fault). Замість тихого псування (§3.6.7) — негайна, точна зупинка.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-7c-1-checkpoint.svg", s)


# ════════════ Рис. 3.6.7c.2 — таблиця регіонів: база/межа + права ═════════════
def fig_regions():
    W, H = 920, 500
    s = header(W, H)
    s += text(W / 2, 34, "Регіон = шматок адрес + права доступу до нього", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "MPU не сторожить кожну комірку окремо — лише кілька грубих діапазонів, кожному приписано, що з ним вільно робити",
              11.5, GREY, "middle", style="italic")

    # колонки таблиці
    x0 = 60
    col_x = [x0 + 8, x0 + 250, x0 + 470, x0 + 600, x0 + 700]
    head_y = 96
    s += rect(x0, head_y - 22, W - 120, 30, "#eef1f6", INK, 1.4, 6)
    for cx, lab in zip(col_x, ["регіон (де лежить)", "діапазон: база … межа",
                               "читати / писати", "викон.", "режим"]):
        s += text(cx, head_y - 2, lab, 11.5, INK, "start", "bold")

    rows = [
        (".text — код",        "0x0000_0000 … +код",  "R — лише читати",   "так (X)", "усі",    GREEN),
        (".rodata — сталі",    "далі за кодом",        "R — лише читати",   "ні",      "усі",    GREEN),
        (".data/.bss — глоб.", "у RAM",                "RW",                 "ні",      "усі",    BLUE),
        ("купа (§3.6.6)",      "у RAM, росте вгору",   "RW",                 "ні",      "усі",    BLUE),
        ("стек (§3.6.5)",      "у RAM, росте вниз",    "RW",                 "ні",      "своя задача", BLUE),
        ("MMIO — периферія",   "діапазон регістрів",   "RW",                 "ні",      "лише привіл.", RED),
    ]
    ry = head_y + 16
    rh = 44
    for i, (reg, rng, rw, x, mode, col) in enumerate(rows):
        y = ry + i * rh
        bg = "#fbfcfd" if i % 2 == 0 else "#ffffff"
        s += rect(x0, y, W - 120, rh - 6, bg, FAINT, 1.2, 5)
        s += rect(x0, y, 6, rh - 6, col, col, 0, 0)  # кольорова смужка зони
        s += text(col_x[0], y + 26, reg, 12, INK, "start", "bold")
        s += text(col_x[1], y + 26, rng, 10.5, GREY, "start")
        rw_col = RED if rw.startswith("R —") else BLUE
        s += text(col_x[2], y + 26, rw, 11, rw_col, "start", "bold")
        s += text(col_x[3], y + 26, x, 10.5, (GREEN if x.startswith("так") else GREY), "start", "bold")
        s += text(col_x[4], y + 26, mode, 10.5, (RED if "привіл" in mode else GREY), "start")

    # плашка-висновок: дві ідеї — NX і priv/unpriv
    by = ry + len(rows) * rh + 6
    s += rect(60, by, W - 120, 64, "#f4f7f4", GREEN, 1.8, 10)
    s += text(W / 2, by + 24, "Два правила гасять цілі класи бід §3.6.7: код позначено «лише читати», дані — «не виконувати» (NX, no-execute),",
              11.3, INK, "middle", "bold")
    s += text(W / 2, by + 46, "а регістри периферії (§3.6.2) доступні «лише з привілейованого режиму» — звичайна задача їх навіть не торкнеться.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-7c-2-regions.svg", s)


# ════════════ Рис. 3.6.7c.3 — чому стек не затопить сусіда ════════════════════
def fig_guard():
    W, H = 920, 500
    s = header(W, H)
    s += text(W / 2, 34, "Чому стек не затопить сусіда: глуха смуга-вартовий під ним", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "переповнення стека (§3.6.7) врізається не в чужі дані, а в регіон «жодного доступу» — і MPU миттєво зупиняє чип",
              11.5, GREY, "middle", style="italic")

    # ── ЛІВОРУЧ: без MPU — тихе псування ──
    lx = 70
    s += text(lx + 110, 92, "без MPU (§3.6.7)", 13.5, GREY, "middle", "bold")
    s += rect(lx, 110, 220, 70, "#eaf0fb", BLUE, 1.6, 4)
    s += text(lx + 110, 140, "стек", 11.5, BLUE, "middle", "bold")
    s += text(lx + 110, 158, "RW, росте вниз ↓", 9.5, GREY, "middle")
    s += rect(lx, 188, 220, 56, "#fafafa", GREY, 1.6, 4)
    s += text(lx + 110, 213, "спільний", 11, GREY, "middle", "bold")
    s += text(lx + 110, 231, "вільний простір", 10, GREY, "middle")
    s += rect(lx, 252, 220, 64, "#eafaef", GREEN, 1.6, 4)
    s += text(lx + 110, 280, ".data сусіда", 11.5, GREEN, "middle", "bold")
    s += text(lx + 110, 298, "звичайна доступна пам'ять", 8.8, GREY, "middle")
    # стрілка переповнення вниз, наскрізь у чужі дані
    s += arrow(lx + 110, 150, lx + 110, 300, RED, 3, dash="2,3")
    s += text(lx + 110, 330, "стек переріс і мовчки", 10.5, RED, "middle", "bold")
    s += text(lx + 110, 346, "затер .data сусіда —", 10.5, RED, "middle")
    s += text(lx + 110, 362, "баг тихий, далекий,", 10, GREY, "middle", style="italic")
    s += text(lx + 110, 376, "несталий (§3.6.7)", 10, GREY, "middle", style="italic")

    # ── ПРАВОРУЧ: з MPU — вартовий ловить ──
    rx = 560
    s += text(rx + 110, 92, "з MPU", 13.5, INK, "middle", "bold")
    # стек
    s += rect(rx, 110, 220, 70, "#eaf0fb", BLUE, 1.8, 4)
    s += text(rx + 110, 140, "стек задачі", 11.5, BLUE, "middle", "bold")
    s += text(rx + 110, 158, "RW, росте вниз ↓", 9.5, GREY, "middle")
    # вартовий — глуха смуга
    gx, gy, gw, gh = rx, 188, 220, 56
    s += rect(gx, gy, gw, gh, "#fdecec", RED, 2.4, 4)
    # штрихування
    for k in range(1, 11):
        xx = gx + k * (gw / 11)
        s += line(xx, gy, xx, gy + gh, RED, 1, dash="3,3")
    s += text(rx + 110, gy + 24, "регіон-вартовий", 11.5, RED, "middle", "bold")
    s += text(rx + 110, gy + 42, "ЖОДНОГО доступу", 10, RED, "middle", "bold")
    # сусід
    s += rect(rx, 252, 220, 64, "#eafaef", GREEN, 1.8, 4)
    s += text(rx + 110, 280, ".data сусіда", 11.5, GREEN, "middle", "bold")
    s += text(rx + 110, 298, "цілий і недоторканий", 9.5, GREY, "middle")
    # стрілка переповнення врізається у вартового
    s += arrow(rx + 110, 150, rx + 110, gy - 4, RED, 3, dash="2,3")
    s += text(rx + 250, gy + 30, "перший же запис", 10.5, RED, "start", "bold")
    s += text(rx + 250, gy + 46, "у вартового →", 10.5, RED, "start")
    s += text(rx + 250, gy + 64, "fault, чип спинено", 10.5, INK, "start", "bold")
    s += text(rx + 250, gy + 80, "до псування сусіда", 9.5, GREY, "start", style="italic")

    # роздільник
    s += line(W / 2, 86, W / 2, 332, FAINT, 1.4, dash="4,4")

    # плашка-висновок
    s += rect(60, 356, W - 120, 124, "#f7f9fc", BLUE, 1.8, 10)
    s += text(W / 2, 380, "Стек однаково «хоче» затопити сусіда в обох випадках — різниця в тому, що під ним лежить.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 404, "Без MPU нижче стека — звичайна доступна пам'ять, тож перевитрата мовчки псує її, і симптом спливе геть в іншому місці.",
              10.8, GREY, "middle")
    s += text(W / 2, 424, "З MPU під кожен стек кладуть тонкий регіон «жодного доступу» (guard). Перший же запис у нього — порушення прав,",
              10.8, GREY, "middle")
    s += text(W / 2, 444, "MPU збуджує виняток, і ядро зупиняється РАНІШЕ, ніж зачепить чужу пам'ять. Стіна стоїть на самій межі стека.",
              10.8, GREY, "middle")
    s += text(W / 2, 466, "Ось точна відповідь на «чому стек не затопить сусіда»: між ними — апаратна глуха стіна, а не просто порожнеча.",
              11, GREEN, "middle", "bold")
    save("fig-19-7c-3-guard.svg", s)


if __name__ == "__main__":
    fig_checkpoint()
    fig_regions()
    fig_guard()
    print("done.")
