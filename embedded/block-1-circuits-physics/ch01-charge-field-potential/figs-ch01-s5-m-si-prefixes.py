# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки §1.1.5m «Префікси СІ
та інженерна нотація». Чистий Python, без залежностей. Вивід → ./img/.
Імена файлів УНІКАЛЬНІ (префікс fig-1-5m-pref-*), головний figs.py розділу
не чіпається. Стиль за AUTHORING §9: білий фон, sans-serif, спільні кольори.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#eef1f4"
AMBER = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"
MONO  = "Consolas, 'DejaVu Sans Mono', monospace"


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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", GREY: "aGrey", GREEN: "aGreen"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", font=FONT):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 1.1.5m.1 — драбина префіксів СІ навколо одиниці ─────────────────────
# Вертикальна шкала показників 10^n; інженерні префікси (крок 3) — суцільні
# й широкі, «нестандартні» (санти/деци) — бліді. Праворуч — приклади.
def fig_ladder():
    W, H = 860, 760
    s = header(W, H)
    s += text(W / 2, 36, "Драбина префіксів СІ: множник = зсув коми", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "інженерні префікси йдуть кроком у три нулі (×10³); посередині — гола одиниця",
              13, GREY, "middle", style="italic")

    # рядки: (показник, символ, назва, множник-словами, інженерний?)
    rows = [
        (9,  "G", "гіга",  "1 000 000 000", True),
        (6,  "M", "мега",  "1 000 000",     True),
        (3,  "k", "кіло",  "1 000",         True),
        (0,  "",  "(одиниця)", "1",         True),
        (-3, "m", "мілі",  "0.001",         True),
        (-6, "µ", "мікро", "0.000 001",     True),
        (-9, "n", "нано",  "0.000 000 001", True),
        (-12,"p", "піко",  "0.000…001",     True),
    ]
    # «неінженерні» сусіди коло одиниці — для контрасту (бліді)
    minors = [(2, "h", "гекто"), (1, "da", "дека"), (-1, "d", "деци"), (-2, "c", "санти")]

    top, bot = 96, H - 150
    axx = 120
    s += line(axx, top, axx, bot, GREY, 3)
    s += text(axx, top - 12, "×10⁹", 12, GREY, "middle")
    s += text(axx, bot + 22, "×10⁻¹²", 12, GREY, "middle")

    def yof(n):
        # n від +9 (top) до -12 (bot)
        return top + (9 - n) * (bot - top) / (9 + 12)

    # бліді другорядні (зліва від осі тонкими рисочками)
    for n, sym, nm in minors:
        y = yof(n)
        s += line(axx - 14, y, axx, y, FAINT, 6)
        s += text(axx - 22, y + 4, f"{sym}", 12, "#c4c9cf", "end")

    # головні інженерні щаблі
    for n, sym, nm, words, _ in rows:
        y = yof(n)
        big = (n == 0)
        col = INK if not big else GREEN
        s += line(axx, y, axx + 18, y, col, 3 if not big else 4)
        # картка щабля
        bx, bw, bh = axx + 28, 250, 34
        s += rect(bx, y - bh / 2, bw, bh, FAINT if not big else "#e7f5ec",
                  GREEN if big else GREY, 2 if not big else 2.5, rx=7)
        lab = (f"{sym}  {nm}" if sym else nm)
        s += text(bx + 12, y - 3, lab, 16, col, "start", "bold")
        exp = (f"= ×10{_sup(n)}" if n else "= ×1")
        s += text(bx + 12, y + 14, exp, 12.5, GREY, "start", font=MONO)
        # множник словами праворуч від картки
        s += text(bx + bw + 16, y + 4, words, 13, "#6a6a6a", "start", font=MONO)

    # підпис кроку у три нулі (фігурна дужка між k та m через одиницю)
    yk, ym = yof(3), yof(-3)
    bxr = axx + 28 + 250 + 150
    s += line(bxr, yk, bxr, ym, AMBER, 2.4)
    s += line(bxr, yk, bxr - 8, yk, AMBER, 2.4)
    s += line(bxr, ym, bxr - 8, ym, AMBER, 2.4)
    s += text(bxr + 10, (yk + ym) / 2 - 8, "сусідні", 12.5, AMBER, "start", "bold")
    s += text(bxr + 10, (yk + ym) / 2 + 8, "інженерні", 12.5, AMBER, "start", "bold")
    s += text(bxr + 10, (yk + ym) / 2 + 24, "= ×1000", 12.5, AMBER, "start", font=MONO)

    # нижня плашка-висновок
    by = bot + 56
    s += rect(70, by, W - 140, 70, "#fbf7ec", AMBER, 2, rx=10)
    s += text(W / 2, by + 28, "Перемножуєш величини з префіксами — показники просто ДОДАЮТЬСЯ:",
              14.5, INK, "middle", "bold")
    s += text(W / 2, by + 52, "k · m = 10³ · 10⁻³ = 10⁰ = 1     (кіло й мілі гасять одне одного)",
              15, GREEN, "middle", font=MONO)
    save("fig-1-5m-pref-ladder.svg", s)


def _sup(n):
    # ціле → надрядковий рядок Unicode (зі знаком мінус для від'ємних)
    sup = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
           "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
    return "".join(sup[c] for c in str(n))


# ── Рис. 1.1.5m.2 — приклад «у голові»: 1 мкА × 10 кОм = 10 мВ ────────────────
# Показуємо роздільне множення: числа × числа, префікси × префікси.
def fig_headcalc():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 36, "Множення «в голові»: окремо числа, окремо префікси", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "беремо мікро (10⁻⁶) і кіло (10³) — показники додаються до 10⁻³, тобто «мілі»",
              13, GREY, "middle", style="italic")

    # верхній рядок — задача
    yq = 110
    s += text(W / 2, yq, "1 мкА  ×  10 кОм  =  ?", 26, INK, "middle", "bold", font=MONO)

    # дві колонки: ЧИСЛА та ПРЕФІКСИ
    colY = 168
    cw = 360
    cxL, cxR = 70, W - 70 - cw
    s += rect(cxL, colY, cw, 150, FAINT, GREY, 2, rx=10)
    s += rect(cxR, colY, cw, 150, "#e7f5ec", GREEN, 2.2, rx=10)

    s += text(cxL + cw / 2, colY + 30, "ЧИСЛА (мантиси)", 15, INK, "middle", "bold")
    s += text(cxL + cw / 2, colY + 70, "1  ×  10  =  10", 22, INK, "middle", font=MONO)
    s += text(cxL + cw / 2, colY + 112, "просте множення", 13, GREY, "middle", style="italic")

    s += text(cxR + cw / 2, colY + 30, "ПРЕФІКСИ (степені 10)", 15, GREEN, "middle", "bold")
    s += text(cxR + cw / 2, colY + 70, "10⁻⁶ · 10³ = 10⁻³", 22, GREEN, "middle", font=MONO)
    s += text(cxR + cw / 2, colY + 112, "−6 + 3 = −3  →  «мілі»", 13, "#2a7d46", "middle", style="italic")

    # стрілки вниз до результату
    ym = colY + 150
    s += arrow(cxL + cw / 2, ym + 4, W / 2 - 70, ym + 54, GREY, 2.2)
    s += arrow(cxR + cw / 2, ym + 4, W / 2 + 70, ym + 54, GREEN, 2.2)

    # результат
    yr = ym + 90
    s += rect(W / 2 - 180, yr - 30, 360, 58, "#fbf7ec", AMBER, 2.4, rx=12)
    s += text(W / 2, yr + 8, "= 10 × 10⁻³ В = 10 мВ", 24, RED, "middle", "bold", font=MONO)
    s += text(W / 2, yr + 64, "одиниця (А·Ом = В) і множник зійшлися самі — калькулятор не потрібен",
              13, GREY, "middle", style="italic")
    save("fig-1-5m-pref-headcalc.svg", s)


if __name__ == "__main__":
    fig_ladder()
    fig_headcalc()
    print("done.")
