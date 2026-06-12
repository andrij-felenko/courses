# -*- coding: utf-8 -*-
"""
Генератор SVG для ⚙️-вставки до §3.6.4 — «Покажчики без паніки:
арифметика, приведення типів і класичні помилки».
Окремий скрипт вставки (головний figs.py розділу не чіпаємо). Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; «+» червоний, «−» синій; «безпечно» зелене;
стрілки через marker; шрифт sans-serif. Підписи — Рис. 3.6.4a.k.
Допоміжні функції скопійовані з figs.py розділу (щоб скрипти не ділили файлів).
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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _mono(x, y, s, size=13, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, \'Courier New\', monospace" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


# ── Рис. 3.6.4a.1 — арифметика покажчика масштабується типом ────────────────
def fig_scaling():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 32, "Арифметика покажчика рахується В ЕЛЕМЕНТАХ, а не в байтах", 19.5, INK, "middle", "bold")
    s += text(W / 2, 54, "p + 1 зсуває на sizeof(*p) байтів — компілятор сам множить крок на розмір елемента",
              12, GREY, "middle", style="italic")

    # спільна стрічка байтів пам'яті (адреси)
    base = 0x1000
    cell = 26
    x0 = 70
    yb = 110
    n = 24
    for i in range(n):
        x = x0 + i * cell
        s += rect(x, yb, cell, 30, "#fbfbfb", FAINT, 1)
        if i % 4 == 0:
            s += _mono(x + 1, yb - 6, f"{base + i:#06x}"[2:], 8.5, GREY)
    s += text(x0, yb + 52, "одна й та сама пам'ять (адреси байтів), p = 0x1000", 11.5, GREY, "start", style="italic")

    # рядок char*  (крок 1)
    yc = yb + 84
    s += text(x0 - 4, yc - 6, "char*  — крок 1 байт:", 13, BLUE, "start", "bold")
    for i in range(n):
        x = x0 + i * cell
        s += rect(x, yc, cell, 28, "#eef3fb", BLUE, 1.2)
    for k in range(0, 5):
        x = x0 + k * cell + cell / 2
        s += arrow(x, yc + 50, x, yc + 30, BLUE, 1.8)
        s += _mono(x, yc + 66, f"p+{k}" if k else "p", 11, BLUE, "middle", "bold")

    # рядок int*  (крок 4)
    yi = yc + 96
    s += text(x0 - 4, yi - 6, "int*  — крок 4 байти (на 32-біт цілому):", 13, RED, "start", "bold")
    for k in range(6):
        x = x0 + k * 4 * cell
        s += rect(x, yi, 4 * cell, 28, "#fbeeee", RED, 1.2)
        s += _mono(x + 2 * cell, yi + 19, f"int[{k}]", 11.5, RED, "middle")
    for k in range(6):
        x = x0 + k * 4 * cell + 2 * cell
        s += arrow(x, yi + 50, x, yi + 30, RED, 1.8)
        s += _mono(x, yi + 66, f"p+{k}" if k else "p", 11, RED, "middle", "bold")

    # підсумок
    s += rect(60, 426, 780, 34, "#f1f7f2", GREEN, 1.6, 9)
    s += text(W / 2, 448, "Те саме «p + 1» — інша адреса для int* і для char*. Байтовий зсув = індекс × sizeof(*p).",
              12.5, INK, "middle", "bold")
    save("fig-19-4a-1-scaling.svg", s)


# ── Рис. 3.6.4a.2 — приведення типів і дві правди про char* ─────────────────
def fig_casts():
    W, H = 900, 500
    s = header(W, H)
    s += text(W / 2, 32, "Приведення покажчика змінює лише «крок» і «лінзу», а не саму адресу", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "те саме число-адреса; тип каже, скільки байтів читати й яким кроком іти",
              12, GREY, "middle", style="italic")

    # одне 4-байтне ціле в пам'яті
    cell = 60
    x0 = 110
    yb = 96
    val = ["0x78", "0x56", "0x34", "0x12"]
    for i in range(4):
        x = x0 + i * cell
        s += rect(x, yb, cell, 34, "#fbfbfb", INK, 1.4)
        s += _mono(x + cell / 2, yb + 22, val[i], 13, INK, "middle")
    s += _mono(x0, yb - 8, "0x2000", 10, GREY)
    s += text(x0 + 2 * cell, yb + 60, "одне 32-бітне ціле = 0x12345678 за адресою 0x2000 (мол. байт першим, §3.4.5)",
              11, GREY, "middle", style="italic")

    # лінза int*  — бачить усі 4 байти як одне число
    yi = 200
    s += rect(70, yi, 360, 84, "#fbeeee", RED, 1.6, 10)
    s += text(250, yi + 24, "int* p  —  «лінза» на 4 байти", 13.5, RED, "middle", "bold")
    s += _mono(90, yi + 50, "*p   → 0x12345678  (усі 4 байти)", 12.5, INK)
    s += _mono(90, yi + 70, "p+1  → 0x2004  (крок 4)", 12.5, INK)

    # лінза char*  — бачить по одному байту
    s += rect(470, yi, 360, 84, "#eef3fb", BLUE, 1.6, 10)
    s += text(650, yi + 24, "char* q = (char*)p  —  «лінза» на 1 байт", 12.5, BLUE, "middle", "bold")
    s += _mono(490, yi + 50, "*q   → 0x78  (лише мол. байт)", 12.5, INK)
    s += _mono(490, yi + 70, "q+1  → 0x2001  (крок 1)", 12.5, INK)

    # законне vs незаконне
    yk = 318
    s += rect(70, yk, 360, 150, "#f1f7f2", GREEN, 1.7, 10)
    s += text(250, yk + 24, "Законно й переносно", 14, GREEN, "middle", "bold")
    s += text(88, yk + 50, "• char*/unsigned char* — «оглядати» байти", 11.5, INK, "start")
    s += text(88, yk + 70, "  будь-якого об'єкта (винятку з aliasing)", 11.5, INK, "start")
    s += text(88, yk + 90, "• void* ↔ конкретний тип (туди-й-назад)", 11.5, INK, "start")
    s += text(88, yk + 110, "• up-cast у межах однієї структури/масиву", 11.5, INK, "start")
    s += text(88, yk + 132, "memcpy у правильний тип — завжди безпечно", 11.5, GREEN, "start", "bold")

    s += rect(470, yk, 360, 150, "#fdf4f4", RED, 1.7, 10)
    s += text(650, yk + 24, "Небезпечно (UB!)", 14, RED, "middle", "bold")
    s += text(488, yk + 50, "• читати int через float*/чужий тип —", 11.5, INK, "start")
    s += text(488, yk + 70, "  порушення strict aliasing (§7)", 11.5, INK, "start")
    s += text(488, yk + 90, "• (int*) на непідрівняну адресу →", 11.5, INK, "start")
    s += text(488, yk + 110, "  HardFault на Cortex-M (вирівнювання!)", 11.5, INK, "start")
    s += text(488, yk + 132, "адреса та сама — а доступ уже зламаний", 11.5, RED, "start", "bold")
    save("fig-19-4a-2-casts.svg", s)


# ── Рис. 3.6.4a.3 — каталог класичних помилок ──────────────────────────────
def fig_mistakes():
    W, H = 900, 520
    s = header(W, H)
    s += text(W / 2, 32, "Сім класичних помилок покажчиків (і чим вони карають на МК)", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "майже всі — або «адреса не туди», або «крок не той»; на МК без захисту пам'яті — тихо й боляче",
              11.5, GREY, "middle", style="italic")

    rows = [
        ("Вихід за межу (off-by-one)",
         "цикл i ≤ N замість i < N → читаєш/пишеш a[N], якого нема", RED),
        ("Плутанина байт vs елемент",
         "p + n коли треба p + n*sizeof, або навпаки memcpy на елементи", AMBER),
        ("Висячий покажчик (dangling)",
         "адреса на звільнену пам'ять чи локальну поза функцією (§3.6.5)", RED),
        ("Подвійне/забуте free",
         "free двічі або витік: на МК без MMU — фрагментація й крах купи (§3.6.6)", AMBER),
        ("Непідрівняний доступ",
         "(int*) на адресу не кратну 4 → HardFault на Cortex-M", BLUE),
        ("Порушення strict aliasing",
         "читати об'єкт через чужий тип; оптимізатор переставить доступи (UB)", BLUE),
        ("Арифметика поза одним масивом",
         "віднімати/порівнювати покажчики з різних блоків — UB, не «просто число»", AMBER),
    ]
    y = 86
    for i, (title, body, col) in enumerate(rows):
        s += rect(60, y, 780, 54, "#fafafa", col, 1.6, 9)
        s += text(78, y + 22, f"{i + 1}. {title}", 13.5, col, "start", "bold")
        s += text(78, y + 43, body, 11.5, INK, "start")
        y += 60

    save("fig-19-4a-3-mistakes.svg", s)


if __name__ == "__main__":
    fig_scaling()
    fig_casts()
    fig_mistakes()
    print("done.")
