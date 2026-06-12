# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до §3.4.4 — «Ariane 5 (1996)».
Окремий скрипт (головний figs.py розділу не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/ тієї ж папки розділу.

Стиль (AUTHORING §9): білий фон; «1»/«+» червоний, «0»/«−» синій; «дійсне» зелене;
стрілки через marker; шрифт sans-serif. Підписи фігур — за темою-історією: Рис. 3.4.4i.k.
Імена SVG унікальні (префікс fig-17-4i-ar5-*), щоб не зіткнутися з figs.py розділу.
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
PALE  = "#f4f4f4"
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


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, color=INK, w=2.4, fill="none", dash=None):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{ds} stroke-linecap="round"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _bits(x, n):
    return format(x & ((1 << n) - 1), "0{}b".format(n))


# ── Рис. 3.4.4i.1 — фатальне перетворення 64-біт float → 16-біт int ──────────
def fig_conversion():
    W, H = 920, 560
    s = header(W, H)
    s += text(W / 2, 36, "Один рядок коду, що знищив ракету: float64 → int16",
              21, INK, "middle", "bold")
    s += text(W / 2, 58, "змінна BH (горизонтальний зсув) була надто велика для 16-бітного цілого — і сталося переповнення",
              12.5, GREY, "middle", style="italic")

    # ── верх: 64-бітне дійсне (велике значення) ──
    bx, by, bw, bh = 110, 96, 700, 56
    s += rect(bx, by, bw, bh, "#eef6ef", GREEN, 2, 8)
    s += text(bx + 14, by + 23, "64-бітне дійсне (float64) — горизонтальна швидкість платформи",
              13.5, GREEN, "start", "bold")
    s += text(bx + 14, by + 44, "значення на Ariane 5 виросло в рази проти Ariane 4 — далеко за межу 16-бітного цілого",
              12, INK, "start")
    s += text(bx + bw - 14, by + 35, "≈ велике", 15, GREEN, "end", "bold")

    # стрілка-перетворення
    cx = bx + bw / 2
    s += arrow(cx, by + bh + 4, cx, by + bh + 40, INK, 2.6)
    s += text(cx + 12, by + bh + 28, "перетворення типу (приведення до int16)", 12.5, INK, "start", "bold")

    # ── 16-бітна сітка: показуємо, що влазить лише 16 молодших бітів ──
    gy = 220
    cell = 30
    total = 24  # показуємо 24 «логічні» біти, з них старші 8 — «зайві»
    gx = (W - total * cell) / 2
    s += text(W / 2, gy - 14, "а приймач — лише 16 бітів зі знаком: діапазон −32768 … +32767",
              13.5, INK, "middle", "bold")
    # старші «зайві» біти (поза 16-бітним вікном)
    for i in range(8):
        x = gx + i * cell
        s += rect(x, gy, cell, cell, "#fbecea", RED, 1.6)
        s += text(x + cell / 2, gy + 20, "×", 16, RED, "middle", "bold")
    # 16-бітне вікно
    win_x = gx + 8 * cell
    s += rect(win_x, gy - 4, 16 * cell, cell + 8, "none", BLUE, 2.6, 5)
    sample = "1011010101101001"
    for i in range(16):
        x = win_x + i * cell
        b = sample[i]
        s += rect(x, gy, cell, cell, "#eef2fb", BLUE, 1.4)
        s += text(x + cell / 2, gy + 20, b, 15, RED if b == "1" else BLUE, "middle", "bold")
    s += text(gx + 4 * cell, gy + cell + 22, "старші біти,", 12.5, RED, "middle", "bold")
    s += text(gx + 4 * cell, gy + cell + 38, "що НЕ влізли", 12.5, RED, "middle")
    s += text(win_x + 8 * cell, gy + cell + 24, "16-бітне вікно: «вижило» лише це — і воно вже безглузде",
              12.5, BLUE, "middle", "bold")

    # ── низ: наслідок — виняток Operand Error ──
    ey = 360
    s += rect(150, ey, W - 300, 150, PALE, INK, 1.4, 10)
    s += text(W / 2, ey + 28, "Залізо НЕ «тихо перевалило» — мова (Ada) кинула виняток",
              14.5, INK, "middle", "bold")
    s += text(W / 2, ey + 52, "Operand Error (помилка операнда): перетворення не вкладається в тип",
              12.5, RED, "middle", "bold")
    # дві гілки: тиша vs виняток
    s += line(W / 2, ey + 64, W / 2, ey + 78, GREY, 1.4)
    s += text(180, ey + 96, "У «голому» C/C++ (§3.4.4):", 12.5, INK, "start", "bold")
    s += text(180, ey + 116, "знакове переповнення — UB,", 12, BLUE, "start")
    s += text(180, ey + 134, "найчастіше тиха «перевалка»", 12, BLUE, "start")
    s += text(W - 180, ey + 96, "У цьому коді (Ada):", 12.5, INK, "end", "bold")
    s += text(W - 180, ey + 116, "виняток не оброблено →", 12, RED, "end")
    s += text(W - 180, ey + 134, "обчислювач SRI зупинився", 12, RED, "end", "bold")
    s += line(W / 2, ey + 84, W / 2, ey + 140, FAINT, 1.4, "4 4")

    save("fig-17-4i-ar5-1-conversion.svg", s)


# ── Рис. 3.4.4i.2 — ланцюг відмови: від одного біта до вибуху ────────────────
def fig_cascade():
    W, H = 720, 760
    s = header(W, H)
    s += text(W / 2, 34, "Ланцюг відмови Ariane 5: як один виняток зруйнував ракету",
              19, INK, "middle", "bold")
    s += text(W / 2, 56, "жодної механічної поломки — лише послідовність програмних рішень, що склалися в катастрофу",
              12, GREY, "middle", style="italic")

    steps = [
        ("H0 — старт", "Ariane 5 злітає; траєкторія крутіша й швидша за Ariane 4", INK, "#f4f4f4"),
        ("Зайва робота", "Функція вирівнювання платформи (SRI) ще працює — хоча після старту вже НЕ потрібна (вимога Ariane 4)", AMBER, "#fbf4e6"),
        ("Переповнення BH", "Горизонтальний зсув BH виріс за межу int16; перетворення float64 → int16 не вклалося", RED, "#fbecea"),
        ("Виняток (Ada)", "Operand Error — і його НЕ було оброблено: обчислювач SRI зупинився як «несправний»", RED, "#fbecea"),
        ("Обидва SRI впали", "Резервний і робочий блоки — однакова програма, тож обидва впали з тієї ж причини (різниця ~72 мс)", RED, "#fbecea"),
        ("Діагностику — за дані", "Бортовий комп'ютер прийняв аварійний бітовий код SRI за справжні польотні дані", RED, "#fbecea"),
        ("Повне відхилення сопел", "За хибними «даними» система різко вивернула сопла прискорювачів і маршового двигуна", RED, "#fbecea"),
        ("Злам і самознищення", "≈ +37 с після старту ракета втратила орієнтацію, почала руйнуватися й самознищилася", BLUE, "#eef2fb"),
    ]
    bx, bw = 70, W - 140
    top = 86
    gap = 80
    bh = 58
    for i, (title, body, col, fill) in enumerate(steps):
        y = top + i * gap
        s += rect(bx, y, bw, bh, fill, col, 2, 9)
        s += text(bx + 16, y + 24, "{}. {}".format(i + 1, title), 14.5, col, "start", "bold")
        s += text(bx + 16, y + 44, body, 11.3, INK, "start")
        if i < len(steps) - 1:
            s += arrow(W / 2, y + bh + 2, W / 2, y + gap - 2, GREY, 2.4)

    # бічна виноска: три «вузли», де ланцюг можна було розірвати
    save("fig-17-4i-ar5-2-cascade.svg", s)


# ── Рис. 3.4.4i.3 — пастка повторного коду: Ariane 4 vs Ariane 5 ────────────
def fig_reuse():
    W, H = 900, 560
    s = header(W, H)
    s += text(W / 2, 34, "Корінь біди: справний код Ariane 4 у новому польоті Ariane 5",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "припущення «BH ніколи не переросте int16» було правдою на старій ракеті — і хибою на новій",
              12.5, GREY, "middle", style="italic")

    # ── ліворуч: дві траєкторії (BH у часі) ──
    ax, ay, aw, ah = 70, 110, 360, 300
    s += rect(ax, ay, aw, ah, "#fcfcfc", FAINT, 1.4, 6)
    # осі
    s += arrow(ax + 36, ay + ah - 36, ax + aw - 16, ay + ah - 36, INK, 2)   # час
    s += arrow(ax + 36, ay + ah - 36, ax + 36, ay + 20, INK, 2)             # BH
    s += text(ax + aw - 16, ay + ah - 16, "час", 12.5, INK, "end")
    s += text(ax + 30, ay + 16, "BH", 12.5, INK, "end", "bold")
    # межа int16
    lim_y = ay + 70
    s += line(ax + 36, lim_y, ax + aw - 16, lim_y, RED, 2, "6 5")
    s += text(ax + aw - 20, lim_y - 8, "межа int16 (+32767)", 12, RED, "end", "bold")
    # крива Ariane 4 — пологá, нижче межі
    x0 = ax + 36
    y0 = ay + ah - 36
    a4 = [(x0 + t * (aw - 56), y0 - (90 * (t ** 1.7))) for t in [i / 12 for i in range(13)]]
    s += polyline(a4, BLUE, 2.8)
    s += text(a4[-1][0] - 6, a4[-1][1] + 18, "Ariane 4", 12.5, BLUE, "end", "bold")
    s += text(a4[-1][0] - 6, a4[-1][1] + 34, "лишається під межею", 11, BLUE, "end")
    # крива Ariane 5 — крутá, перетинає межу
    a5 = [(x0 + t * (aw - 56), y0 - (250 * (t ** 1.7))) for t in [i / 12 for i in range(13)]]
    a5 = [(x, max(y, ay + 22)) for (x, y) in a5]
    s += polyline(a5, RED, 2.8)
    # точка перетину межі
    cross = None
    for (x, y) in a5:
        if y <= lim_y:
            cross = (x, lim_y)
            break
    if cross:
        s += circle(cross[0], cross[1], 6, RED, RED, 0)
        s += circle(cross[0], cross[1], 6, "none", "#fff", 1.6)
        # виноску ставимо НИЖЧЕ межі й ліворуч від точки, щоб не зіткнутись із підписом межі
        s += line(cross[0], cross[1] + 6, cross[0] - 18, cross[1] + 30, RED, 1.4)
        s += text(cross[0] - 22, cross[1] + 34, "тут BH вилазить за межу", 11.5, RED, "end", "bold")
    s += text(a5[3][0] + 8, a5[3][1] + 4, "Ariane 5", 12.5, RED, "start", "bold")
    s += text(ax + aw / 2, ay + ah + 22, "та сама фізична величина, інша траєкторія", 12, INK, "middle", style="italic")

    # ── праворуч: 7 перетворень, 4 захищені, 3 — ні ──
    rx = 500
    s += text(rx, 110, "7 критичних перетворень в SRI:", 14, INK, "start", "bold")
    s += text(rx, 130, "захистили лише 4 — щоб утриматись", 12.5, INK, "start")
    s += text(rx, 147, "у межах завантаження процесора ≈ 80%", 12.5, INK, "start")
    cy = 176
    box = 30
    items = [
        ("1", True), ("2", True), ("3", True), ("4", True),
        ("5", False), ("6", False), ("7", False),
    ]
    for i, (lab, prot) in enumerate(items):
        y = cy + i * (box + 8)
        col = GREEN if prot else RED
        fill = "#eef6ef" if prot else "#fbecea"
        s += rect(rx, y, box, box, fill, col, 1.8, 5)
        s += text(rx + box / 2, y + 20, ("✓" if prot else "✗"), 16, col, "middle", "bold")
        msg = "захищене від переповнення" if prot else "НЕ захищене (ризик визнали «фізично неможливим»)"
        s += text(rx + box + 12, y + 20, "перетворення №{} — {}".format(lab, msg),
                  12, INK if prot else RED, "start", "bold" if not prot else "normal")
    # підпис-висновок
    by = cy + 7 * (box + 8) + 8
    s += rect(rx, by, W - rx - 40, 64, PALE, INK, 1.4, 8)
    s += text(rx + 12, by + 24, "Рішення колективне, не «помилка одного»:", 12.5, INK, "start", "bold")
    s += text(rx + 12, by + 44, "вимога, тест-сценарій і повторне використання коду зійшлися в одну діру.",
              11.8, INK, "start")

    save("fig-17-4i-ar5-3-reuse.svg", s)


if __name__ == "__main__":
    fig_conversion()
    fig_cascade()
    fig_reuse()
    print("done.")
