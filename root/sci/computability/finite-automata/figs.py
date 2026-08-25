# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Скінченні автомати».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

RED   = "#c0392b"   # вхід «1» / гаряче
BLUE  = "#2457d6"   # вхід «0» / холодне
GREEN = "#27ae60"   # приймальний стан
STATE = "#eef2fb"   # заливка звичайного стану
ACC   = "#eafaf0"   # заливка приймального стану


def arrow_c(x1, y1, x2, y2, color, sw=2.2):
    """Пряма стрілка заданого кольору (свій marker під колір)."""
    mid = "ar_%s" % color.lstrip("#")
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#%s)"/>' % (x1, y1, x2, y2, color, sw, mid))


def curve(d, color, sw=2.2):
    mid = "ar_%s" % color.lstrip("#")
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'marker-end="url(#%s)"/>' % (d, color, sw, mid))


def defs_arrows(*colors):
    out = ["<defs>"]
    for c in colors:
        mid = "ar_%s" % c.lstrip("#")
        out.append('<marker id="%s" viewBox="0 0 10 10" refX="8.4" refY="5" '
                   'markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse">'
                   '<path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>' % (mid, c))
    out.append("</defs>")
    return "".join(out)


def state(cx, cy, label, sub=None, accept=False, r=33):
    """Кружок-стан; приймальний — подвійним колом і зеленим."""
    col = GREEN if accept else INK
    fill = ACC if accept else STATE
    out = circle(cx, cy, r, fill=fill, stroke=col, sw=2.3)
    if accept:
        out += circle(cx, cy, r - 5, fill="none", stroke=col, sw=2.0)
    out += text(cx, cy + (1 if sub else 5), label, size=17, color=INK, bold=True)
    if sub:
        out += text(cx, cy + 18, sub, size=10.5, color=MUTED)
    return out


def loop_top(cx, cy, label, color, r=33):
    """Петля над станом (вхід веде в той самий стан)."""
    x1, x2 = cx - 12, cx + 12
    y = cy - r
    d = "M %.1f,%.1f C %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        x1, y, x1 - 14, y - 42, x2 + 14, y - 42, x2, y)
    out = curve(d, color)
    out += text(cx, y - 48, label, size=14, color=color, bold=True)
    return out


def start_mark(cx, cy, r=33):
    out = arrow_c(cx - r - 36, cy, cx - r - 4, cy, INK, sw=2.2)
    out += text(cx - r - 40, cy - 8, "старт", size=11, color=MUTED, anchor="end")
    return out


# ── Фігура 1: DFA-детектор підрядка «101» ────────────────────────────────────
# Серце статті: стан = «скільки початку візерунка вже зібрано». Чотири стани
# S0..S3 у ряд; підписані дуги δ (червона — «1», синя — «0»); важливі ВІДКАТИ
# (S2 --0--> S0, S3 --1--> S1). Знизу — прогін «1 1 0 1», що закінчується в S3.
def fig_dfa_states():
    W, H = 820, 430
    P = [defs_arrows(RED, BLUE, INK)]
    xs = [120, 320, 520, 720]
    y = 175
    # прямі дуги вперед: S0--1-->S1, S1--0-->S2, S2--1-->S3
    P.append(curve("M %d,%d Q %d,%d %d,%d" % (xs[0] + 34, y, (xs[0] + xs[1]) / 2, y, xs[1] - 34, y), RED))
    P.append(text((xs[0] + xs[1]) / 2, y - 12, "1", size=14, color=RED, bold=True))
    P.append(curve("M %d,%d Q %d,%d %d,%d" % (xs[1] + 34, y, (xs[1] + xs[2]) / 2, y, xs[2] - 34, y), BLUE))
    P.append(text((xs[1] + xs[2]) / 2, y - 12, "0", size=14, color=BLUE, bold=True))
    P.append(curve("M %d,%d Q %d,%d %d,%d" % (xs[2] + 34, y, (xs[2] + xs[3]) / 2, y, xs[3] - 34, y), RED))
    P.append(text((xs[2] + xs[3]) / 2, y - 12, "1", size=14, color=RED, bold=True))
    # петлі: S0 по «0» (лишаємось), S1 по «1» (лишаємось)
    P.append(loop_top(xs[0], y, "0", BLUE))
    P.append(loop_top(xs[1], y, "1", RED))
    # відкати (дуги вниз): S2 --0--> S0 ; S3 --1--> S1
    P.append(curve("M %d,%d Q %d,%d %d,%d" % (xs[2] - 24, y + 24, (xs[0] + xs[2]) / 2, y + 110, xs[0] + 24, y + 24), BLUE))
    P.append(text((xs[0] + xs[2]) / 2, y + 96, "0", size=14, color=BLUE, bold=True))
    P.append(curve("M %d,%d Q %d,%d %d,%d" % (xs[3] - 22, y + 26, (xs[1] + xs[3]) / 2, y + 150, xs[1] + 22, y + 26), RED))
    P.append(text((xs[1] + xs[3]) / 2, y + 132, "1", size=14, color=RED, bold=True))
    # стани
    P.append(state(xs[0], y, "S0", "нічого"))
    P.append(state(xs[1], y, "S1", "є «1»"))
    P.append(state(xs[2], y, "S2", "є «10»"))
    P.append(state(xs[3], y, "S3", "є «101»", accept=True))
    P.append(start_mark(xs[0], y))
    # прогін «1 1 0 1»
    bx, by, bw, bh = 250, 348, 380, 64
    P.append(rect(bx, by, bw, bh, fill="#fbfbfb", stroke="#e2e6ea", sw=1.4, rx=8))
    P.append(text(bx + 16, by + 24, "Прогін входу  1 1 0 1 :", size=12.5, color=INK, anchor="start", bold=True))
    P.append(text(bx + 16, by + 46, "S0 →1 S1 →1 S1 →0 S2 →1 S3", size=13.5, color=INK, anchor="start"))
    P.append(text(bx + bw - 16, by + 46, "✓", size=16, color=GREEN, anchor="end", bold=True))
    render("img/dfa-states.svg", W, H, *P)


# ── Фігура 2: regex ⇄ автомат (теорема Кліні) ───────────────────────────────
# Угорі — три цеглини алгебри (вибір, склейка, повтор) і весь приклад одним
# виразом. Стрілка вниз з підписом «теорема Кліні». Унизу — той самий об'єкт
# як компактна машина зі станами.
def fig_regex_fsm():
    W, H = 820, 470
    P = [defs_arrows(RED, BLUE, INK, GREEN)]
    P.append(text(60, 40, "Алгебра рядків (regex) над алфавітом Σ = {0, 1}", size=14, color=INK, anchor="start", bold=True))
    P.append(text(60, 62, "три операції — і будь-яка «регулярна» множина рядків:", size=11.5, color=MUTED, anchor="start"))
    cards = [(60, BLUE, "вибір", "a | b", "«або a, або b»"),
             (298, INK, "склейка", "a · b", "«a, за ним b»"),
             (536, RED, "повтор (зірочка)", "a*", "«a нуль чи більше разів»")]
    for x, col, name, expr, gloss in cards:
        P.append(rect(x, 78, 224, 66, fill="#fbfbfb", stroke=col, sw=1.8, rx=9))
        P.append(text(x + 14, 102, name, size=12, color=col, anchor="start", bold=True))
        P.append(text(x + 14, 128, expr, size=16, color=INK, anchor="start", bold=True))
        P.append(text(x + 92, 128, gloss, size=10.5, color=MUTED, anchor="start"))
    P.append(text(410, 184, "Наш приклад одним виразом — «десь у потоці стоїть 101»:", size=12.5, color=INK))
    P.append(rect(190, 196, 440, 42, fill="#eef4ff", stroke=BLUE, sw=2, rx=9))
    P.append(text(410, 224, "(0|1)*  ·  1 · 0 · 1  ·  (0|1)*", size=18, color=INK, bold=True))
    P.append(text(255, 256, "будь-що спереду", size=10.5, color=MUTED))
    P.append(text(410, 256, "ядро 101", size=10.5, color=RED))
    P.append(text(565, 256, "будь-що позаду", size=10.5, color=MUTED))
    # стрілка-теорема
    P.append(arrow_c(410, 274, 410, 312, GREEN, sw=2.6))
    box, w_, h_ = textbox(410, 296, "теорема Кліні:  вираз ⇄ автомат", size=12.5,
                          fill=ACC, stroke=GREEN, color=GREEN, bold=True)
    # textbox центрується сам — змістимо праворуч від стрілки, щоб не накрити її
    P.append(textbox(560, 296, "вираз ⇄ автомат", size=12, fill=ACC, stroke=GREEN, color=GREEN, bold=True)[0])
    # машина внизу (компактно)
    yb = 410
    xs = [150, 330, 510, 690]
    P.append(text(60, 356, "Той самий опис — як машина зі станами:", size=12.5, color=INK, anchor="start", bold=True))
    P.append(curve("M %d,%d Q %d,%d %d,%d" % (xs[0] + 26, yb, (xs[0] + xs[1]) / 2, yb, xs[1] - 26, yb), RED))
    P.append(text((xs[0] + xs[1]) / 2, yb - 10, "1", size=13, color=RED, bold=True))
    P.append(curve("M %d,%d Q %d,%d %d,%d" % (xs[1] + 26, yb, (xs[1] + xs[2]) / 2, yb, xs[2] - 26, yb), BLUE))
    P.append(text((xs[1] + xs[2]) / 2, yb - 10, "0", size=13, color=BLUE, bold=True))
    P.append(curve("M %d,%d Q %d,%d %d,%d" % (xs[2] + 26, yb, (xs[2] + xs[3]) / 2, yb, xs[3] - 26, yb), RED))
    P.append(text((xs[2] + xs[3]) / 2, yb - 10, "1", size=13, color=RED, bold=True))
    P.append(loop_top(xs[0], yb, "0", BLUE, r=26))
    P.append(loop_top(xs[1], yb, "1", RED, r=26))
    for i, (x, lab) in enumerate(zip(xs, ["S0", "S1", "S2", "S3"])):
        P.append(state(x, yb, lab, accept=(i == 3), r=26))
    P.append(start_mark(xs[0], yb, r=26))
    render("img/regex-fsm.svg", W, H, *P)


# ── Фігура 3: NFA проти DFA (детермінізація підмножинами) ────────────────────
# Ліворуч — недетермінований опис «…101…»: зі старту петля по 0/1 І стрілка по
# «1» далі; машина «вгадує», де починається 101. Праворуч — детермінований
# еквівалент: стани DFA = ПІДМНОЖИНИ станів NFA (це і є побудова підмножинами).
def fig_nfa_dfa():
    W, H = 820, 440
    P = [defs_arrows(RED, BLUE, INK, GREEN)]
    P.append(line(410, 60, 410, 392, color="#e2e6ea", sw=1.6, dash="6,6"))
    # ── ліворуч: NFA ──
    P.append(text(205, 40, "NFA — недетермінований", size=14.5, color=INK, bold=True))
    P.append(text(205, 60, "зі старту по «1» — ДВА варіанти; машина «вгадує»", size=10.5, color=MUTED))
    nx = [70, 205, 340]
    ny = 175
    # старт-стан n0 з петлею по 0 і 1, і стрілкою по 1 у n1
    P.append(loop_top(nx[0], ny, "0, 1", INK, r=28))
    P.append(curve("M %d,%d Q %d,%d %d,%d" % (nx[0] + 28, ny, (nx[0] + nx[1]) / 2, ny, nx[1] - 28, ny), RED))
    P.append(text((nx[0] + nx[1]) / 2, ny - 10, "1", size=13, color=RED, bold=True))
    P.append(curve("M %d,%d Q %d,%d %d,%d" % (nx[1] + 28, ny, (nx[1] + nx[2]) / 2, ny, nx[2] - 28, ny), BLUE))
    P.append(text((nx[1] + nx[2]) / 2, ny - 10, "0", size=13, color=BLUE, bold=True))
    # n2 --1--> accept (петля 0,1 на прийомі)
    P.append(curve("M %d,%d Q %d,%d %d,%d" % (nx[2] - 24, ny + 24, 205, ny + 120, nx[0] + 24, ny + 24), RED))
    P.append(text(205, ny + 104, "1 → прийом", size=12, color=RED, bold=True))
    P.append(state(nx[0], ny, "n0", accept=False, r=28))
    P.append(state(nx[1], ny, "n1", accept=False, r=28))
    P.append(state(nx[2], ny, "n2", "після 10", accept=True, r=28))
    P.append(start_mark(nx[0], ny, r=28))
    P.append(text(205, 360, "стрілок з n0 по «1» — більше однієї →", size=11, color=INK))
    P.append(text(205, 378, "це й є недетермінізм", size=11, color=MUTED))
    # ── праворуч: DFA = підмножини ──
    P.append(text(615, 40, "DFA — той самий мовний клас", size=14.5, color=INK, bold=True))
    P.append(text(615, 60, "стан DFA = ПІДМНОЖИНА станів NFA", size=10.5, color=MUTED))
    dx = [500, 615, 730]
    dy = 175
    P.append(loop_top(dx[0], dy, "0", BLUE, r=26))
    P.append(curve("M %d,%d Q %d,%d %d,%d" % (dx[0] + 26, dy, (dx[0] + dx[1]) / 2, dy, dx[1] - 26, dy), RED))
    P.append(text((dx[0] + dx[1]) / 2, dy - 10, "1", size=13, color=RED, bold=True))
    P.append(loop_top(dx[1], dy, "1", RED, r=26))
    P.append(curve("M %d,%d Q %d,%d %d,%d" % (dx[1] + 26, dy, (dx[1] + dx[2]) / 2, dy, dx[2] - 26, dy), BLUE))
    P.append(text((dx[1] + dx[2]) / 2, dy - 10, "0", size=13, color=BLUE, bold=True))
    P.append(state(dx[0], dy, "{n0}", accept=False, r=26))
    P.append(state(dx[1], dy, "{n0,n1}", accept=False, r=26))
    P.append(state(dx[2], dy, "{n0,n2}", accept=True, r=26))
    P.append(start_mark(dx[0], dy, r=26))
    P.append(text(615, 300, "кожна досяжна підмножина — один стан;", size=11, color=INK))
    P.append(text(615, 318, "підмножина з прийомом NFA → прийом DFA.", size=11, color=MUTED))
    P.append(text(615, 360, "Рабін і Скотт: NFA не сильніший за DFA —", size=11, color=INK))
    P.append(text(615, 378, "та сама множина рядків, лиш більше станів.", size=11, color=MUTED))
    render("img/nfa-dfa.svg", W, H, *P)


if __name__ == "__main__":
    fig_dfa_states()
    fig_regex_fsm()
    fig_nfa_dfa()
    print("OK: dfa-states.svg, regex-fsm.svg, nfa-dfa.svg")
