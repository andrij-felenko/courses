# -*- coding: utf-8 -*-
"""
Фігури для 📜-історії до §3.4.8 — «UTF-8 на паперовій підкладці в дайнері»
(Кен Томпсон і Роб Пайк, 1992). Чистий Python, без залежностей. Вивід → ./img/.

Стиль (AUTHORING §9) копіюється з figs.py розділу: білий фон; «1» червоний,
«0» синій; «дійсне/зроблено» зелене; стрілки через marker; шрифт sans-serif.
Нумерація підписів історії до теми — Рис. 3.4.8i.k; імена файлів — fig-17-8i-*.
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


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 3.4.8i.1 — від ISO 10646 / UTF-1 через FSS-UTF до вечора в дайнері ──
# Не дублює бітову схему з теми: показує РОДОВІД ідеї та хто що вніс.
def fig_lineage():
    W, H = 920, 540
    s = header(W, H)
    s += text(W / 2, 36, "Родовід UTF-8: ідея визрівала роками, форму дістала за вечір",
              21, INK, "middle", "bold")
    s += text(W / 2, 58, "винахід — колективний: проблему окреслив комітет, ключову вимогу додав Томпсон у дайнері",
              12.5, GREY, "middle", style="italic")

    # три «попередники» зліва, велика стрілка в центр, дайнер справа
    boxw, boxh = 250, 92
    bx = 40
    stages = [
        ("1991–92 · ISO 10646 / UTF-1", BLUE,
         ["перша спроба вкласти Unicode в байти;", "ASCII і не-ASCII НЕ розділені чисто —", "байти-продовження плутаються з ASCII"]),
        ("лип. 1992 · X/Open (XoJIG)", AMBER,
         ["Дейв Проссер (Unix System Labs)", "пропонує FSS-UTF: «ASCII = лише сам себе,", "у багатобайтових — старший біт завжди 1»"]),
        ("серп. 1992 · розсилка IBM", AMBER,
         ["представник IBM в X/Open розсилає", "чернетку FSS-UTF зацікавленим —", "так вона дійшла до Bell Labs"]),
    ]
    for i, (title, col, lines) in enumerate(stages):
        y = 96 + i * (boxh + 28)
        s += rect(bx, y, boxw, boxh, "#fbfbfb", col, 2, 9)
        s += rect(bx, y, 6, boxh, col, col, 0, 0)
        s += text(bx + 16, y + 22, title, 12.5, col, "start", "bold")
        for j, ln in enumerate(lines):
            s += text(bx + 16, y + 42 + j * 17, ln, 11.5, INK, "start")
        s += arrow(bx + boxw + 4, y + boxh / 2, 360, 270, GREY, 2)

    # центральний вузол — вечір у дайнері
    cx, cy = 470, 270
    s += circle(cx, cy, 58, "#fdf4f4", RED, 3)
    s += text(cx, cy - 14, "2 вересня", 13, RED, "middle", "bold")
    s += text(cx, cy + 4, "1992", 13, RED, "middle", "bold")
    s += text(cx, cy + 24, "дайнер,", 11.5, INK, "middle")
    s += text(cx, cy + 39, "Нью-Джерсі", 11.5, INK, "middle")

    # підкладка-серветка з ескізом (стилізовано, без точної бітової схеми теми)
    px, py = 560, 150
    s += rect(px, py, 330, 250, "#fffdf5", AMBER, 2, 10)
    s += text(px + 165, py + 26, "паперова підкладка (placemat)", 12.5, GREY, "middle", style="italic")
    # «ескіз» Томпсона — пакування бітів, схематично
    s += text(px + 20, py + 58, "Кен Томпсон рахує пакування бітів:", 12, INK, "start", "bold")
    sk = [
        ("0xxxxxxx", "1 байт — і це РІВНО ASCII", BLUE),
        ("110xxxxx 10xxxxxx", "2 байти", INK),
        ("1110xxxx 10xxxxxx 10xxxxxx", "3 байти", INK),
        ("11110xxx 10xx… 10xx… 10xx…", "4 байти", INK),
    ]
    for j, (code, note, col) in enumerate(sk):
        yy = py + 84 + j * 30
        s += text(px + 20, yy, code, 12.5, col, "start", "bold")
        s += text(px + 20, yy + 14, note, 10.5, GREY, "start")
    s += text(px + 20, py + 232, "Роб Пайк — поряд, «cheering him on»",
              11, GREEN, "start", style="italic")

    # підпис-ремарка знизу
    s += text(W / 2, H - 16,
              "Томпсон не вигадав усе з нуля: він узяв ідею FSS-UTF і додав те, чого їй бракувало (див. Рис. 3.4.8i.2).",
              12, GREY, "middle", style="italic")
    save("fig-17-8i-1-lineage.svg", s)


# ── Рис. 3.4.8i.2 — що вже було у FSS-UTF, а що додав Томпсон (самосинхр.) ────
def fig_what_changed():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 36, "Внесок Томпсона: одна вимога, що зробила кодування живучим",
              21, INK, "middle", "bold")
    s += text(W / 2, 58, "у телефонній розмові Пайк «проспівав» список бажаного — і саме пункт про синхронізацію все вирішив",
              12.5, GREY, "middle", style="italic")

    colw = 410
    # ЛІВОРУЧ: уже було у FSS-UTF (Проссер)
    lx = 40
    s += rect(lx, 92, colw, 322, "#fbfbfb", AMBER, 2, 10)
    s += text(lx + colw / 2, 120, "Уже було у FSS-UTF (Дейв Проссер)", 14.5, AMBER, "middle", "bold")
    have = [
        "ASCII (0…127) кодується одним байтом —",
        "    і це той самий байт, що в ASCII",
        "у багатобайтовому символі КОЖЕН байт",
        "    має старший біт 1 (не сплутати з ASCII)",
        "немає нуль-байтів і скісної риски '/'",
        "    усередині символу → безпечно для",
        "    імен файлів Unix (звідси й «FS-Safe»)",
    ]
    for j, ln in enumerate(have):
        s += text(lx + 22, 150 + j * 24, ln, 12, INK, "start")

    # ПРАВОРУЧ: що додав Томпсон
    rx = 470
    s += rect(rx, 92, colw, 322, "#fdf4f4", RED, 2.4, 10)
    s += text(rx + colw / 2, 120, "Що додав Кен Томпсон", 14.5, RED, "middle", "bold")
    s += text(rx + 22, 150, "САМОСИНХРОНІЗАЦІЯ:", 12.5, RED, "start", "bold")
    add = [
        "за будь-яким байтом видно його роль —",
        "початок символу чи його продовження",
        "(продовження завжди починається з 10…);",
        "тож, «упавши» в середину потоку,",
        "знаходиш межу символу, втративши",
        "щонайбільше кілька байтів — і йдеш далі",
    ]
    for j, ln in enumerate(add):
        s += text(rx + 22, 176 + j * 24, ln, 12, INK, "start")

    # маленька ілюстрація самосинхронізації під текстом правого блоку
    bx, by, bw = rx + 22, 326, 46
    seq = [("0", BLUE), ("110", RED), ("10", GREY), ("1110", RED), ("10", GREY), ("10", GREY)]
    labels = ["ASCII", "поч.", "прод.", "поч.", "прод.", "прод."]
    for j, (tag, col) in enumerate(seq):
        x = bx + j * (bw + 6)
        s += rect(x, by, bw, 34, "#fff", col, 2, 5)
        s += text(x + bw / 2, by + 16, tag, 11.5, col, "middle", "bold")
        s += text(x + bw / 2, by + 29, labels[j], 8.5, GREY, "middle")
    # стрілка «впав сюди» вказує на байт-продовження
    fx = bx + 2 * (bw + 6) + bw / 2
    s += arrow(fx, by + 64, fx, by + 38, GREEN, 2.4)
    s += text(fx, by + 80, "почав читати звідси → видно «прод.» → відступив до межі",
              10.5, GREEN, "middle", style="italic")

    save("fig-17-8i-2-what-changed.svg", s)


# ── Рис. 3.4.8i.3 — тиждень: від ескізу до цілої ОС на UTF-8, тоді — світ ────
def fig_one_week():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 36, "Один тиждень: ескіз → жива система → стандарт",
              21, INK, "middle", "bold")
    s += text(W / 2, 58, "ідея «спрацювала», бо її одразу довели до кінця: за дні Plan 9 перейшла на UTF-8 цілком",
              12.5, GREY, "middle", style="italic")

    spine_y = 250
    x0, x1 = 80, 840
    s += line(x0, spine_y, x1, spine_y, GREY, 3)
    s += arrow(x1 - 2, spine_y, x1 + 18, spine_y, GREY, 3)

    nodes = [
        ("ср · 2 вер.", "вечеря в дайнері", RED,
         ["Томпсон на підкладці", "рахує пакування бітів;", "Пайк поряд"], "up"),
        ("ніч", "перший код", INK,
         ["Томпсон пише пакування/", "розпакування; Пайк береться", "за C- і графічні бібліотеки"], "down"),
        ("чт", "код готовий", INK,
         ["усе написано — і вони", "починають переганяти", "текстові файли системи"], "up"),
        ("пт · 11 вер.", "Plan 9 — лише UTF-8", GREEN,
         ["ціла ОС працює — і працює", "ВИКЛЮЧНО в новому кодуванні", "(не теорія, а жива система)"], "down"),
        ("8 вер., 03:22", "лист в X/Open", AMBER,
         ["Томпсон надсилає готову", "пропозицію FSS-UTF комітету;", "далі — голосування «за»"], "up"),
        ("січ. 1993", "USENIX, Сан-Дієго", INK,
         ["перша публічна доповідь —", "і кодування рушає у світ", "файлів, мереж і вебу"], "down"),
    ]
    n = len(nodes)
    for i, (when, what, col, lines, side) in enumerate(nodes):
        x = x0 + 40 + (x1 - x0 - 80) * i / (n - 1)
        s += circle(x, spine_y, 8, "#fff", col, 3)
        if col == GREEN:
            s += circle(x, spine_y, 3.5, GREEN, GREEN, 1)
        s += text(x, spine_y + (24 if side == "up" else -14), when, 11.5, GREY, "middle", "bold")
        if side == "up":
            boxy = spine_y - 150
            s += line(x, spine_y - 8, x, boxy + 70, col, 1.4, "3 3")
        else:
            boxy = spine_y + 40
            s += line(x, spine_y + 8, x, boxy, col, 1.4, "3 3")
        bw, bh = 150, 70
        s += rect(x - bw / 2, boxy, bw, bh, "#fbfbfb", col, 2, 8)
        s += text(x, boxy + 18, what, 12, col, "middle", "bold")
        for j, ln in enumerate(lines):
            s += text(x, boxy + 35 + j * 13, ln, 9.5, INK, "middle")

    save("fig-17-8i-3-one-week.svg", s)


if __name__ == "__main__":
    fig_lineage()
    fig_what_changed()
    fig_one_week()
    print("ok: 3 figures for §3.4.8i (UTF-8 diner history)")
