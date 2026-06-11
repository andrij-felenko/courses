# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для алгоритмічної вставки 2.10.5a — «Чому генератор не
стартує: діагностика крок за кроком».
НЕ чіпає головний figs.py розділу. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(fig-r10-s5a-*). Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій;
поле зелене; стрілки через marker; шрифт sans-serif. Допоміжні функції
скопійовано з figs.py розділу (єдиний вигляд між розділами).
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
COPP  = "#b5732e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LYEL  = "#fbf6e3"
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
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 2.10.5a.1 — дерево діагностики «генератор не стартує» ────────────────
def fig_debug_tree():
    """Покрокове дерево рішень: симптом → перевірка → найімовірніша причина
    → дія. Три гілки збігаються з трьома типовими причинами з підзаголовка
    теми: завелика CL, довгі доріжки, слабкий інвертор."""
    W, H = 980, 720
    s = header(W, H)
    s += text(W / 2, 34, "Генератор мовчить: дерево діагностики крок за кроком",
              20, INK, "middle", "bold")
    s += text(W / 2, 56,
              "не міняй усе одразу — спускайся по гілці, на кожному кроці одна перевірка й одна дія",
              12.5, GREY, "middle", style="italic")

    def node(x, y, w, h, title, sub, fill, stroke):
        out = rect(x, y, w, h, fill, stroke, 2.2, 9)
        out += text(x + w / 2, y + (22 if sub else h / 2 + 5), title,
                    14, INK, "middle", "bold")
        if sub:
            out += text(x + w / 2, y + 40, sub, 11.5, GREY, "middle")
        return out

    # стартовий вузол
    cx = W / 2
    s += node(cx - 150, 78, 300, 52, "Подати живлення, дати ~10 мс на старт",
              "пробник осцилографа — на вивід XTAL_OUT (через 10×)", LYEL, COPP)
    s += arrow(cx, 130, cx, 156, INK, 2.2)

    # перша розвилка: чи є взагалі коливання
    s += node(cx - 165, 156, 330, 52, "Чи є синусоїда на XTAL_OUT?",
              "амплітуда хоча б ~0.5 В розмаху", "#fff", INK)

    # ─ гілка «НІ» (ліворуч): не стартує зовсім ─
    nx = 175
    s += arrow(cx - 165, 182, nx + 150, 182, RED, 2.2)
    s += text(cx - 175, 176, "НІ — тиша", 12, RED, "end", "bold")
    s += node(nx, 232, 300, 88,
              "Перевір амплітуду й підсилення",
              None, LRED, RED)
    s += text(nx + 150, 262, "Чи правильний інвертор / режим піна?", 12, INK, "middle")
    s += text(nx + 150, 282, "Чи не завелика сумарна CL?", 12, INK, "middle")
    s += text(nx + 150, 302, "Чи правильний номінал Rext (якщо є)?", 12, INK, "middle")

    # дії гілки НІ — три причини з підзаголовка теми
    ay = 360
    s += arrow(nx + 150, 320, nx + 150, ay, RED, 2)
    s += node(40, ay, 250, 96, "Слабкий інвертор",
              None, "#fff", RED)
    s += text(40 + 125, ay + 30, "gm замалий для цього кварцу", 11, GREY, "middle")
    s += text(40 + 125, ay + 50, "→ увімкнути «high-gain»/", 11.5, INK, "middle")
    s += text(40 + 125, ay + 66, "high-drive режим осцилятора", 11.5, INK, "middle")
    s += text(40 + 125, ay + 84, "→ або менший Rext", 11.5, INK, "middle")

    s += node(310, ay, 250, 96, "Завелика CL",
              None, "#fff", RED)
    s += text(310 + 125, ay + 30, "C1, C2 більші за норму даташита", 11, GREY, "middle")
    s += text(310 + 125, ay + 50, "→ зменшити C1=C2 до", 11.5, INK, "middle")
    s += text(310 + 125, ay + 66, "CL_потр (− Cstray)", 11.5, INK, "middle")
    s += text(310 + 125, ay + 84, "→ перевірити вхідну ємність піна", 11.0, INK, "middle")

    # «довгі доріжки» належать радше до гілки «ТАК але нестабільно», тож з'єднаємо нижче

    # ─ гілка «ТАК» (праворуч): стартує, але погано ─
    s += arrow(cx + 165, 182, cx + 360, 182, GREEN, 2.2)
    s += text(cx + 175, 176, "ТАК", 12, GREEN, "start", "bold")
    s += node(cx + 360 - 0, 156, 0, 0, "", None, "#fff", "#fff")  # spacer no-op
    s += node(700, 232, 250, 88, "Стартує, та частота «гуляє» / зриви",
              None, LGRN, GREEN)
    s += text(700 + 125, 262, "Чи довгі/звивисті доріжки?", 12, INK, "middle")
    s += text(700 + 125, 282, "Чи близько кварц до чипа?", 12, INK, "middle")
    s += text(700 + 125, 302, "Чи є охоронне заземлення?", 12, INK, "middle")

    s += arrow(700 + 125, 320, 700 + 125, ay, GREEN, 2)
    s += node(640, ay, 300, 96, "Довгі доріжки / погана земля",
              None, "#fff", GREEN)
    s += text(640 + 150, ay + 30, "паразитна C і наводки на петлі", 11, GREY, "middle")
    s += text(640 + 150, ay + 50, "→ кварц упритул до піна XTAL", 11.5, INK, "middle")
    s += text(640 + 150, ay + 66, "→ короткі доріжки, охоронна земля", 11.0, INK, "middle")
    s += text(640 + 150, ay + 84, "→ перерахувати CL з урахуванням Cstray", 10.5, INK, "middle")

    # збіжний висновок
    by = 500
    s += arrow(165, ay + 96, cx - 10, by, RED, 1.8, "4 3")
    s += arrow(435, ay + 96, cx - 6, by, RED, 1.8, "4 3")
    s += arrow(790, ay + 96, cx + 10, by, GREEN, 1.8, "4 3")
    s += node(cx - 250, by, 500, 70,
              "Зміна спрацювала? Перевір ЗАПАС, не сам факт старту",
              None, LYEL, COPP)
    s += text(cx, by + 44,
              "робочий генератор має стартувати з 3–5× запасом за підсиленням (gain margin)",
              12, INK, "middle")

    s += arrow(cx, by + 70, cx, by + 96, INK, 2.2)
    s += node(cx - 200, by + 96, 400, 52,
              "Заміряй частоту й час старту в холоді й теплі",
              "−40 °C і +85 °C — найгірші кути для старту", "#fff", INK)

    # підпис-резюме внизу
    s += text(W / 2, H - 16,
              "Золоте правило: міняй ОДИН чинник за раз і дивись на запас, а не на «хоч якось завелося»",
              12, GREY, "middle", style="italic")
    return s


# ── Рис. 2.10.5a.2 — баланс негативного опору: де кожна вада з'їдає запас ─────
def fig_neg_resistance():
    """Умова старту: |−R_осц| має перекривати втрати кварцу ESR з запасом.
    Стовпчики показують, як завелика CL, довгі доріжки і слабкий інвертор
    кожне окремо зменшують −R_осц або збільшують ESR_еф — і з'їдають запас."""
    W, H = 940, 540
    s = header(W, H)
    s += text(W / 2, 34, "Умова старту: «негативний опір» має перекрити втрати кварцу",
              20, INK, "middle", "bold")
    s += text(W / 2, 56,
              "генератор заводиться лише коли |−R_осц| > ESR з запасом; кожна типова вада з'їдає цей запас",
              12.5, GREY, "middle", style="italic")

    ox, oy = 90, H - 110          # початок осі
    axh = H - 230                 # висота шкали
    s += arrow(ox, oy, ox, oy - axh - 14, INK, 2.2)
    s += text(ox - 8, oy - axh - 22, "опір", 13, INK, "middle", "bold")
    s += arrow(ox, oy, W - 60, oy, INK, 2.2)

    # рівень ESR кварцу — поріг, який треба перекрити
    esr_y = oy - axh * 0.34
    s += line(ox, esr_y, W - 80, esr_y, BLUE, 2, "6 4")
    s += text(W - 84, esr_y - 8, "ESR кварцу (втрати, які треба покрити)", 12, BLUE, "end", "bold")

    bw = 96
    gap = 58
    base = ox + 70

    def bar(i, label, top_frac, col, fillc, note):
        x = base + i * (bw + gap)
        top = oy - axh * top_frac
        out = rect(x, top, bw, oy - top, fillc, col, 2.4, 5)
        # підпис висоти = доступний |−R|
        out += text(x + bw / 2, top - 10, "|−R_осц|", 12, col, "middle", "bold")
        out += text(x + bw / 2, oy + 22, label, 12.5, INK, "middle", "bold")
        out += text(x + bw / 2, oy + 40, note, 10.8, GREY, "middle")
        # маркер запасу відносно ESR
        if top <= esr_y:
            out += line(x + bw / 2, top, x + bw / 2, esr_y, GREEN, 2.4)
            out += text(x + bw + 6, (top + esr_y) / 2, "запас", 11, GREEN, "start", "bold")
        else:
            out += line(x + bw / 2, esr_y, x + bw / 2, top, RED, 2.6)
            out += text(x + bw + 6, (top + esr_y) / 2, "НЕ стартує", 11, RED, "start", "bold")
        return out

    s += bar(0, "Норма", 0.92, GREEN, LGRN, "C1=C2 за даташитом,\nкороткі доріжки")
    s += bar(1, "Завелика CL", 0.46, COPP, "#f6ede2", "C1,C2 завеликі →\nменший |−R|")
    s += bar(2, "Довгі доріжки", 0.30, RED, LRED, "+Cstray і наводки →\nефективний ESR росте")
    s += bar(3, "Слабкий інвертор", 0.20, RED, LRED, "малий gm →\nмалий |−R|")

    # дворядкові підписи: розіб'ємо \n вручну
    # (текст вище має \n — браузер їх не рендерить; зробимо другий рядок окремо)
    # перезапишемо: прибрати \n-варіант, додати другий рядок
    return s


# другий варіант bar-підпису з двома рядками (без \n у <text>)
def fig_neg_resistance_v2():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 34, "Умова старту: «негативний опір» має перекрити втрати кварцу",
              20, INK, "middle", "bold")
    s += text(W / 2, 56,
              "генератор заводиться лише коли |−R_осц| > ESR із запасом; кожна типова вада з'їдає цей запас",
              12.5, GREY, "middle", style="italic")

    ox, oy = 90, H - 130
    axh = H - 250
    s += arrow(ox, oy, ox, oy - axh - 14, INK, 2.2)
    s += text(ox - 8, oy - axh - 22, "опір", 13, INK, "middle", "bold")
    s += arrow(ox, oy, W - 60, oy, INK, 2.2)

    esr_y = oy - axh * 0.34
    s += line(ox, esr_y, W - 90, esr_y, BLUE, 2, "6 4")
    s += text(W - 92, esr_y - 8, "ESR кварцу — поріг, який треба перекрити", 12, BLUE, "end", "bold")

    bw = 100
    gap = 56
    base = ox + 60

    bars = [
        ("Норма", 0.92, GREEN, LGRN, "C1=C2 за даташитом,", "короткі доріжки"),
        ("Завелика CL", 0.46, COPP, "#f6ede2", "C1, C2 завеликі →", "падає |−R_осц|"),
        ("Довгі доріжки", 0.30, RED, LRED, "+Cstray і наводки →", "росте ефективний ESR"),
        ("Слабкий інвертор", 0.20, RED, LRED, "малий gm →", "падає |−R_осц|"),
    ]
    for i, (label, frac, col, fillc, n1, n2) in enumerate(bars):
        x = base + i * (bw + gap)
        top = oy - axh * frac
        s += rect(x, top, bw, oy - top, fillc, col, 2.4, 5)
        s += text(x + bw / 2, top - 10, "|−R_осц|", 12, col, "middle", "bold")
        s += text(x + bw / 2, oy + 22, label, 12.5, INK, "middle", "bold")
        s += text(x + bw / 2, oy + 39, n1, 10.6, GREY, "middle")
        s += text(x + bw / 2, oy + 53, n2, 10.6, GREY, "middle")
        if top <= esr_y:
            s += line(x + bw / 2, top, x + bw / 2, esr_y, GREEN, 2.6)
            s += text(x + bw + 4, (top + esr_y) / 2 + 4, "запас", 11, GREEN, "start", "bold")
        else:
            s += line(x + bw / 2, esr_y, x + bw / 2, top, RED, 2.8)
            s += text(x + bw + 4, (top + esr_y) / 2 + 4, "не стартує", 11, RED, "start", "bold")

    s += text(W / 2, H - 16,
              "Запас за підсиленням = |−R_осц| / ESR; для надійного старту цілься в 3–5×",
              12, GREY, "middle", style="italic")
    return s


if __name__ == "__main__":
    save("fig-r10-s5a-1-debug-tree.svg", fig_debug_tree())
    save("fig-r10-s5a-2-neg-resistance.svg", fig_neg_resistance_v2())
    print("done.")
