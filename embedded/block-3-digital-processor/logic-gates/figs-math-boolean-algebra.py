# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для МАТЕМАТИЧНОЇ вставки до теми §3.2.1
— «Булева алгебра формально: аксіоми, закони де Моргана, доведення тотожностей».

Самодостатній: спільні допоміжні функції (header/text/rect/…) скопійовано з figs.py
розділу 15 (AUTHORING §9 — кожен скрипт несе свою копію хелперів, щоб не ділити стану).
Головний figs.py НЕ чіпаємо. Вивід → ./img/. Нумерація підписів — за темою-вставкою:
«Рис. 3.2.1m.k»; імена файлів на диску — fig-15-1m-*.svg (унікальні).
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (та сама, що в розділі) ──────────────────────────────────────────
RED   = "#c0271e"   # «1» / істина
BLUE  = "#1f47b5"   # «0» / хибність
GREEN = "#1f8a3b"   # дійсне / висновок
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", GREEN: "aGreen"}


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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 3.2.1m.1 — аксіоми Гантінґтона у дуальних парах ─────────────────────
def fig_axioms():
    """Постулати Гантінґтона (1904): дві колонки-двійники (· і +), що показують
    головну ідею — кожна аксіома має ДУАЛЬНУ; усе інше з них ВИВОДИТЬСЯ."""
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 36, "Аксіоми булевої алгебри (постулати Гантінґтона, 1904)",
              21, INK, "middle", "bold")
    s += text(W / 2, 58, "усього кілька правил, узятих за дане; решта законів §3.2.1 — це вже ТЕОРЕМИ, доведені з них",
              12.5, GREY, "middle", style="italic")

    # шапки колонок
    colx_or, colx_and = 250, 620
    s += text(colx_or, 96, "для « + » (АБО)", 14, INK, "middle", "bold")
    s += text(colx_and, 96, "для « · » (І)", 14, INK, "middle", "bold")
    s += text(118, 96, "аксіома", 12.5, GREY, "middle", "bold")
    # вертикальний роздільник між дуальними колонками
    s += line(W / 2 + 185, 110, W / 2 + 185, 392, FAINT, 1.4)

    rows = [
        ("Замкненість", "a + b ∈ B", "a · b ∈ B"),
        ("Нейтральний", "a + 0 = a", "a · 1 = a"),
        ("Комутативність", "a + b = b + a", "a · b = b · a"),
        ("Дистрибутивність", "a + (b·c) = (a+b)·(a+c)", "a · (b+c) = a·b + a·c"),
        ("Доповнення", "a + ā = 1", "a · ā = 0"),
        ("Два елементи", "у B є 0 ≠ 1", "(не той самий)"),
    ]
    y0 = 116
    rowh = 46
    s += rect(60, y0, W - 120, rowh * len(rows) + 6, "none", GREY, 1.2, 8)
    for i, (name, lo, la) in enumerate(rows):
        yy = y0 + 30 + i * rowh
        if i % 2 == 0:
            s += rect(60, yy - 24, W - 120, rowh, "#f6f8f6", "none", 0)
        s += text(74, yy, name, 12.5, INK, "start", "bold")
        last = (i == len(rows) - 1)
        s += text(colx_or, yy, lo, 14.5, (GREY if last else INK), "middle",
                  "normal" if last else "bold")
        s += text(colx_and, yy, la, 14.5, (GREY if last else INK), "middle",
                  "normal" if last else "bold")

    # підпис-висновок про дуальність
    s += rect(60, y0 + rowh * len(rows) + 16, W - 120, 44, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, y0 + rowh * len(rows) + 43,
              "Кожна аксіома ліворуч має ДВІЙНИКА праворуч: міняємо + ↔ · та 0 ↔ 1 — і одне правило стає іншим.",
              12.5, INK, "middle", "bold")
    save("fig-15-1m-axioms.svg", s)


# ── Рис. 3.2.1m.2 — доведення тотожності a+a=a крок-за-кроком з аксіом ────────
def fig_proof():
    """Демонструє САМ МЕТОД: вивести 'очевидний' закон a+a=a, не приймаючи його,
    а лише з аксіом — кожен рядок підписаний аксіомою, що його виправдовує."""
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 36, "Доведення тотожності: a + a = a — лише з аксіом",
              21, INK, "middle", "bold")
    s += text(W / 2, 58, "ідемпотентність не приймаємо як «очевидну» — її ВИВОДИМО; праворуч від кожного кроку — аксіома, що його дозволяє",
              12, GREY, "middle", style="italic")

    steps = [
        ("a + a", "= (a + a) · 1", "нейтральний (·1)"),
        ("", "= (a + a) · (a + ā)", "доповнення (a+ā=1)"),
        ("", "= a + (a · ā)", "дистрибутивність"),
        ("", "= a + 0", "доповнення (a·ā=0)"),
        ("", "= a", "нейтральний (+0)"),
    ]
    x_lhs = 150
    x_eq = 250
    x_law = 600
    y = 116
    dy = 46
    for i, (lhs, rhs, law) in enumerate(steps):
        yy = y + i * dy
        if lhs:
            s += text(x_lhs, yy, lhs, 18, INK, "end", "bold")
        col = GREEN if i == len(steps) - 1 else INK
        s += text(x_eq, yy, rhs, 17, col, "start", "bold" if i == len(steps) - 1 else "normal")
        # підпис-аксіома
        s += text(x_law, yy, "[ " + law + " ]", 12.5, GREY, "start", style="italic")
    # вертикальна дужка-висновок
    s += line(x_eq - 16, y - 14, x_eq - 16, y + dy * (len(steps) - 1) + 8, FAINT, 2)

    s += rect(60, 360, W - 120, 50, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 382,
              "За дуальністю одразу маємо й двійника: a · a = a (міняємо + ↔ · та 0 ↔ 1 у кожному рядку).",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 401,
              "Так само з аксіом доводять поглинання, Де Моргана й решту «шпаргалки» §3.2.1 — нічого не беручи на віру.",
              11.5, GREY, "middle", style="italic")
    save("fig-15-1m-proof.svg", s)


if __name__ == "__main__":
    fig_axioms()
    fig_proof()
    print("ch15-s1-m boolean-algebra figures done.")
