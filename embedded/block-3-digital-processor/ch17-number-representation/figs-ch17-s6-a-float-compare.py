# -*- coding: utf-8 -*-
"""
Генератор SVG для ⚙️-вставки до §3.4.6 — «Порівняння float: чому a == b не працює».
Окремий скрипт вставки (головний figs.py розділу не чіпаємо). Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; «небезпечно/похибка» червоний, точне/опорне синій,
«безпечно/рівні» зелене; стрілки через marker; шрифт sans-serif.
Підписи у тексті — Рис. 3.4.6a.k. Допоміжні функції скопійовані з figs.py розділу,
щоб скрипти не ділили файлів і loop'и не конфліктували.
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


def circle(cx, cy, r, fill=INK, stroke="none", sw=0):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _mono(x, y, s, size=13, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, \'Courier New\', monospace" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


# ── Рис. 3.4.6a.1 — крок float росте з величиною → фіксований ε не годиться ──
def fig_spacing():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 34, "Чому один фіксований ε не годиться: крок між float-числами РОСТЕ", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "сусідні представні числа стоять то густо (біля 0), то рідко (біля великих) — допуск має масштабуватися",
              12, GREY, "middle", style="italic")

    # три «вікна» числової осі в різних масштабах
    axisX0, axisX1 = 70, 810
    bands = [
        (110, "біля 1.0", "крок ≈ 1.2×10⁻⁷", BLUE,
         [1.0000000, 1.0000001, 1.0000002, 1.0000004, 1.0000005, 1.0000006]),
        (235, "біля 1 000 000", "крок ≈ 0.06", AMBER,
         [1000000.00, 1000000.06, 1000000.12, 1000000.19, 1000000.25, 1000000.31]),
        (360, "біля 1 000 000 000", "крок ≈ 64 (!)", RED,
         [1000000000, 1000000064, 1000000128, 1000000192, 1000000256, 1000000320]),
    ]
    for y, label, step, col, ticks in bands:
        s += line(axisX0, y, axisX1, y, INK, 2)
        s += arrow(axisX1, y, axisX1 + 18, y, INK, 2)
        n = len(ticks)
        for i in range(n):
            x = axisX0 + 30 + i * (axisX1 - axisX0 - 60) / (n - 1)
            s += line(x, y - 9, x, y + 9, col, 2.4)
            s += circle(x, y, 3.4, col)
        s += text(axisX0, y - 22, label, 13.5, col, "start", "bold")
        s += text(axisX1 + 24, y + 5, step, 12.5, col, "start", "bold")
        # підпис «representable float» під крайніми точками першої смуги
    # пояснення розриву кроку
    s += text(axisX0 + 30, bands[0][0] + 30, "0.0000001", 10.5, GREY, "middle")
    s += text(axisX1 - 30, bands[0][0] + 30, "0.0000006", 10.5, GREY, "middle")

    # нижній підсумок з двома «поганими» сценаріями
    s += rect(60, 396, 380, 58, "#fdf4f4", RED, 1.7, 10)
    s += text(250, 419, "ε завеликий (напр. 0.001)", 12.5, RED, "middle", "bold")
    s += text(250, 439, "біля 1e9 числа за 64 одиниці зіллються в «рівні»", 11, INK, "middle")
    s += rect(460, 396, 360, 58, "#fdf4f4", RED, 1.7, 10)
    s += text(640, 419, "ε замалий (напр. 1e-9)", 12.5, RED, "middle", "bold")
    s += text(640, 439, "біля 1.0 жодні два сусіди не «рівні» — крок більший", 11, INK, "middle")
    save("fig-17-6a-1-spacing.svg", s)


# ── Рис. 3.4.6a.2 — три види порівняння: абсолютне / відносне / комбіноване ──
def fig_three_kinds():
    W, H = 880, 500
    s = header(W, H)
    s += text(W / 2, 34, "Три види допуску — і чому потрібні всі три", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "абсолютний рятує біля нуля, відносний — на великих числах, поріг між ними перемикає їх",
              12, GREY, "middle", style="italic")

    CW = 252  # ширина колонки
    cols = [
        (48, "Абсолютний", BLUE,
         "|a − b| ≤ εабс",
         ["Один сталий допуск.", "Працює БІЛЯ НУЛЯ", "(де відносний ділить", "на ~0 і вибухає).",
          "Хибний на великих:", "при a=1e6 поріг 1e-6", "недосяжний."]),
        (314, "Відносний", AMBER,
         "|a−b| ≤ εвідн·max(|a|,|b|)",
         ["Допуск росте з числом —", "як і крок float вище.", "Універсальний для", "«звичайних» величин.",
          "Ламається БІЛЯ НУЛЯ:", "max(|a|,|b|)→0, поріг→0,", "0.0 vs 1e-30 «нерівні»."]),
        (580, "Комбінований", GREEN,
         "абс. якщо малі, інакше відн.",
         ["Спершу абсолютна гілка", "для околу нуля,", "далі — відносна.", "Саме так і роблять",
          "на практиці — одна", "функція nearEqual.", "Покриває весь діапазон."]),
    ]
    for x, title, col, formula, lines in cols:
        cx = x + CW / 2
        s += rect(x, 84, CW, 386, "#fafafa", col, 1.8, 12)
        s += text(cx, 112, title, 15.5, col, "middle", "bold")
        s += rect(x + 12, 126, CW - 24, 34, "#ffffff", col, 1.3, 8)
        s += _mono(cx, 148, formula, 12, INK, "middle")
        yy = 188
        for ln in lines:
            bad = ln.startswith("Хибний") or ln.startswith("Ламається")
            c = RED if bad else INK
            w = "bold" if bad else "normal"
            s += text(x + 18, yy, ln, 12, c, "start", w)
            yy += 22
        # значок придатності
        ok = title == "Комбінований"
        s += circle(cx, 444, 13, GREEN if ok else AMBER)
        s += text(cx, 449, "✓" if ok else "±", 16, "#ffffff", "middle", "bold")

    save("fig-17-6a-2-three-kinds.svg", s)


# ── Рис. 3.4.6a.3 — ULP: рахуємо «скільки float-чисел між a і b» через біти ──
def fig_ulp():
    W, H = 880, 480
    s = header(W, H)
    s += text(W / 2, 34, "ULP-порівняння: «за скільки представних чисел a відстоїть від b»", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "перетлумачуємо біти float як ціле — і сусідні числа стають сусідніми цілими (різниця = 1)",
              12, GREY, "middle", style="italic")

    # ряд клітинок: послідовні float, під ними — їхній бітовий патерн як ціле
    x0, y = 70, 150
    cell = 118
    vals = [
        ("1.0000000", "0x3F800000", "= N"),
        ("1.0000001", "0x3F800001", "N+1"),
        ("1.0000002", "0x3F800002", "N+2"),
        ("1.0000004", "0x3F800003", "N+3"),
        ("1.0000005", "0x3F800004", "N+4"),
        ("1.0000006", "0x3F800005", "N+5"),
    ]
    for i, (fv, hexv, idx) in enumerate(vals):
        x = x0 + i * cell
        col = GREEN if i == 0 else INK
        s += rect(x, y, cell - 14, 54, "#f1f7f2" if i == 0 else "#fafafa", col, 1.6, 9)
        s += _mono(x + (cell - 14) / 2, y + 23, fv, 12.5, INK, "middle")
        s += _mono(x + (cell - 14) / 2, y + 44, hexv, 11, BLUE, "middle")
        s += text(x + (cell - 14) / 2, y + 78, idx, 13, RED if i else GREEN, "middle", "bold")
        if i:
            s += arrow(x - 14, y + 27, x, y + 27, GREY, 1.8)

    s += text(W / 2, y - 30, "послідовні float-значення (один крок ULP між сусідами)", 12.5, GREY, "middle", style="italic")
    s += text(W / 2, y + 108, "ті самі біти, прочитані як 32-бітне ціле → рівно +1 на кожен крок",
              12.5, BLUE, "middle", "bold")

    # формула ULP-відстані
    s += rect(150, y + 130, 580, 92, "#f5f8ff", BLUE, 1.7, 12)
    s += text(W / 2, y + 156, "ulpDiff = | bitsAsInt(a) − bitsAsInt(b) |", 15, INK, "middle", "bold")
    s += text(W / 2, y + 180, "«рівні» ⇔ ulpDiff ≤ maxUlps  (типово 1…4 ULP)", 13, INK, "middle")
    s += text(W / 2, y + 202, "поріг у ULP сам масштабується разом із числом — окремий ε не потрібен",
              11.5, GREEN, "middle", style="italic")

    # пастки ULP — праворуч-нижній блок
    s += rect(60, y + 248, 760, 70, "#fdf4f4", RED, 1.6, 10)
    s += text(80, y + 272, "Пастки ULP:", 12.5, RED, "start", "bold")
    s += text(80, y + 292, "• знак: від'ємні float як ціле йдуть «навспак» — звести до знак-величини перед відніманням;",
              11.5, INK, "start")
    s += text(80, y + 310, "• різні знаки a,b і ±0 — окремий випадок; • NaN не «рівний» нічому; • потрібен union/memcpy без UB.",
              11.5, INK, "start")
    save("fig-17-6a-3-ulp.svg", s)


if __name__ == "__main__":
    fig_spacing()
    fig_three_kinds()
    fig_ulp()
    print("done.")
