# -*- coding: utf-8 -*-
"""
Генератор SVG для ⚙️-вставки до §3.4.4 — «Ловимо переповнення в C».
Окремий скрипт вставки (головний figs.py розділу не чіпаємо). Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; «1» червоний, «0» синій; «безпечно» зелене;
стрілки через marker; шрифт sans-serif. Підписи — Рис. 3.4.4a.k.
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


# ── Рис. 3.4.4a.1 — чому перевірка ПІСЛЯ не працює в знаковому C ────────────
def fig_post_check_trap():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 34, "Чому перевірку ПІСЛЯ знакового переповнення компілятор викидає", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "знакове переповнення — UB, тож оптимізатор має право вважати, що його НЕ буває",
              12, GREY, "middle", style="italic")

    # ліва колонка — наївний код
    s += rect(60, 86, 360, 150, "#fdf4f4", RED, 1.7, 10)
    s += text(240, 110, "Наївно: «перевіримо потім»", 13.5, RED, "middle", "bold")
    s += _mono(80, 140, "int x = ...;", 13, INK)
    s += _mono(80, 162, "int y = x + 1;", 13, INK)
    s += _mono(80, 184, "if (y < x)        // ловимо wrap?", 13, INK)
    s += _mono(96, 206, "handle_overflow();", 13, RED)

    # стрілка вниз — що робить компілятор
    s += arrow(240, 240, 240, 286, RED, 2.4)
    s += text(258, 268, "оптимізатор «міркує»", 11.5, RED, "start", style="italic")

    s += rect(60, 290, 760, 70, "#fff7e8", AMBER, 1.7, 10)
    s += text(80, 316, "«x + 1 — знакове, отже переповнення НЕМОЖЛИВЕ (це було б UB),",
              12.5, "#8a6d1f", "start", "bold")
    s += text(80, 338, " отже y завжди > x, отже умова (y < x) завжди ХИБНА» → гілку видалено.",
              12.5, "#8a6d1f", "start", "bold")

    # права колонка — правильний підхід
    s += rect(440, 86, 380, 150, "#f1f7f2", GREEN, 1.7, 10)
    s += text(630, 110, "Правильно: перевірка ДО дії", 13.5, GREEN, "middle", "bold")
    s += _mono(458, 140, "if (x > INT_MAX - 1)", 13, INK)
    s += _mono(474, 162, "handle_overflow();   // безпечно", 13, GREEN)
    s += _mono(458, 184, "else", 13, INK)
    s += _mono(474, 206, "y = x + 1;           // тут не вилізе", 13, INK)

    s += rect(60, 392, 760, 56, "#f1f7f2", GREEN, 1.7, 10)
    s += text(W / 2, 416, "Головне: суму, що переповнить знаковий тип, НЕ МОЖНА навіть обчислювати.",
              13, INK, "middle", "bold")
    s += text(W / 2, 436, "Перевіряй межу ДО операції — або обчислюй у ширшому/беззнаковому типі.",
              12, GREY, "middle", style="italic")
    save("fig-17-4a-1-post-check-trap.svg", s)


# ── Рис. 3.4.4a.2 — перевірка ДО додавання: знаковий і беззнаковий ─────────
def fig_pre_check_rules():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 34, "Перевірка переповнення ДО додавання a + b", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "переставляємо нерівність так, щоб ризикованої суми взагалі не виникало",
              12, GREY, "middle", style="italic")

    # беззнаковий блок
    s += rect(50, 84, 390, 300, "none", BLUE, 1.8, 12)
    s += text(245, 110, "Беззнаковий (uint)", 14.5, BLUE, "middle", "bold")
    s += text(245, 130, "wrap визначений (mod 2ᴺ), та все одно хибний", 11, GREY, "middle", style="italic")
    s += _mono(70, 162, "// межа — UINT_MAX", 12.5, GREY)
    s += _mono(70, 188, "if (a > UINT_MAX - b)", 13.5, INK)
    s += _mono(86, 210, "/* переповниться */;", 13.5, BLUE)
    s += text(70, 248, "Чому так:", 12, BLUE, "start", "bold")
    s += text(70, 270, "a + b вилізе ⇔ a + b > UINT_MAX.", 11.5, INK, "start")
    s += text(70, 290, "Переносимо b праворуч (різниця безпечна,", 11.5, INK, "start")
    s += text(70, 308, "бо b ≤ UINT_MAX): a > UINT_MAX − b.", 11.5, INK, "start")
    s += text(70, 336, "Дешева перевірка, що НЕ переповнюється", 11.5, GREEN, "start", "bold")
    s += text(70, 354, "сама — лише одне віднімання й порівняння.", 11.5, GREEN, "start")

    # знаковий блок
    s += rect(460, 84, 390, 300, "none", RED, 1.8, 12)
    s += text(655, 110, "Знаковий (int)", 14.5, RED, "middle", "bold")
    s += text(655, 130, "переповнення — UB; треба ловити ОБИДВІ межі", 11, GREY, "middle", style="italic")
    s += _mono(480, 162, "if (b > 0 && a > INT_MAX - b)", 12.8, INK)
    s += _mono(496, 184, "/* верхня межа */;", 12.8, RED)
    s += _mono(480, 206, "if (b < 0 && a < INT_MIN - b)", 12.8, INK)
    s += _mono(496, 228, "/* нижня межа */;", 12.8, RED)
    s += text(480, 266, "Дві перевірки, бо знакове вилазить", 11.5, RED, "start", "bold")
    s += text(480, 286, "у ДВА боки: + переб'є INT_MAX,", 11.5, INK, "start")
    s += text(480, 304, "− провалиться під INT_MIN.", 11.5, INK, "start")
    s += text(480, 332, "Знак b каже, яку межу перевіряти —", 11.5, INK, "start")
    s += text(480, 350, "інша різниця сама була б UB.", 11.5, INK, "start")

    s += text(W / 2, 410, "Той самий прийом для × (ділення межі) і для −b: спершу перевір, тоді дій.",
              12.5, INK, "middle", "bold")
    save("fig-17-4a-2-pre-check-rules.svg", s)


# ── Рис. 3.4.4a.3 — арсенал засобів: від найнадійнішого до найручнішого ────
def fig_toolbox():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 34, "Чим ловити переповнення: від найнадійнішого до найручнішого", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "обирай за наявним компілятором і потрібним контролем",
              12, GREY, "middle", style="italic")

    rows = [
        ("1. Ширший тип",
         "int64 для проміжку, тоді звузь із перевіркою. Найпростіше, коли запас по бітах є.",
         GREEN, "найдешевше думкою"),
        ("2. __builtin_*_overflow",
         "GCC/Clang: bool o = __builtin_add_overflow(a, b, &r). Робить дію Й каже, чи вилізло.",
         GREEN, "найнадійніше"),
        ("3. Беззнаковий домен",
         "Свідомий wrap mod 2ᴺ: лічильники, гешування, різниця часу (t2 − t1). Визначено стандартом.",
         BLUE, "коли wrap — фіча"),
        ("4. Ручна перевірка ДО",
         "Переставлена нерівність (Рис. 3.4.4a.2). Переносна на будь-який компілятор, без розширень.",
         AMBER, "максимум контролю"),
    ]
    y = 92
    for title, body, col, tag in rows:
        s += rect(60, y, 760, 70, "#fafafa", col, 1.7, 10)
        s += text(82, y + 28, title, 14, col, "start", "bold")
        s += text(82, y + 52, body, 12, INK, "start")
        s += rect(648, y + 14, 158, 26, "#ffffff", col, 1.3, 8)
        s += text(727, y + 31, tag, 11, col, "middle", "bold")
        y += 80

    s += text(W / 2, y + 14, "Найгірший варіант — НЕ перевіряти зовсім і сподіватися, що «не вилізе».",
              12.5, RED, "middle", "bold")
    save("fig-17-4a-3-toolbox.svg", s)


if __name__ == "__main__":
    fig_post_check_trap()
    fig_pre_check_rules()
    fig_toolbox()
    print("done.")
