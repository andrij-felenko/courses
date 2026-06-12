# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🔌-вставки r09-s7-c-component-tester (до теми 2.9.7).
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс fig-r09-7c-...), щоб не зачіпати головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки marker; sans-serif.
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
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LGREY = "#f3f3f3"
LSUN  = "#fbf3df"
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


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = '"Cascadia Mono", Consolas, "Courier New", monospace' if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
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


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.9.7c.1 — що ховається за КОЖНОЮ з трьох клем: МК + дві відомі опори + АЦП
# ─────────────────────────────────────────────────────────────────────────────
def fig1():
    W, H = 780, 540
    s = header(W, H)
    s += text(W / 2, 30, "Що насправді стоїть за кожною з трьох клем тестера",
              17, INK, "middle", "bold")

    # ── мікроконтролер ──
    mx, my, mw, mh = 40, 70, 210, 330
    s += rect(mx, my, mw, mh, LGREY, "#9aa6b0", 2, 10)
    s += text(mx + mw / 2, my + 26, "мікроконтролер", 15, INK, "middle", "bold")
    s += text(mx + mw / 2, my + 45, "(AVR ATmega328-клас)", 12, GREY, "middle")

    # АЦП всередині МК
    ax, ay, aw, ah = mx + 24, my + 64, mw - 48, 58
    s += rect(ax, ay, aw, ah, "#ffffff", BLUE, 1.8, 7)
    s += text(ax + aw / 2, ay + 22, "АЦП (ADC)", 13, BLUE, "middle", "bold")
    s += text(ax + aw / 2, ay + 41, "опора 5 В ↔ 1.1 В", 11.5, INK, "middle")

    # три виводи МК (драйвери) — кожен «штовхає» 0 або Vcc
    s += text(mx + mw / 2, my + 152, "цифрові виводи:", 12, INK, "middle", "bold")
    s += text(mx + mw / 2, my + 170, "кожен → 0 В, Vcc або Z", 11.5, GREY, "middle")
    pin_lab = ["вивід A", "вивід B", "вивід C"]
    py0 = my + 192
    for i, pl in enumerate(pin_lab):
        yy = py0 + i * 40
        s += rect(mx + 30, yy, mw - 60, 28, "#ffffff", INK, 1.4, 5)
        s += text(mx + mw / 2, yy + 19, pl, 12.5, INK, "middle")

    # ── для кожної клеми: пара резисторів 680 Ом / 470 кОм → клема ──
    cx_term = 660           # x клем
    cx_split = 330          # де гілка ділиться на два резистори
    term_lab = ["клема 1", "клема 2", "клема 3"]
    for i in range(3):
        yc = py0 + i * 40 + 14            # рівень виводу МК
        # лінія від виводу МК до вузла розгалуження
        s += line(mx + mw - 30, yc, cx_split, yc, INK, 2)
        s += circle(cx_split, yc, 3.5, INK, INK, 1)

        # верхня гілка — 680 Ом (силова, для струму/опору)
        yhi = yc - 16
        s += line(cx_split, yc, cx_split, yhi, INK, 2)
        s += line(cx_split, yhi, cx_split + 36, yhi, INK, 2)
        s += rect(cx_split + 36, yhi - 9, 56, 18, "#ffffff", RED, 1.6, 3)
        s += text(cx_split + 64, yhi + 4, "680 Ω", 11, RED, "middle", "bold")
        s += line(cx_split + 92, yhi, cx_term - 70, yhi, INK, 2)

        # нижня гілка — 470 кОм (слабка, для бази/високого опору)
        ylo = yc + 16
        s += line(cx_split, yc, cx_split, ylo, INK, 2)
        s += line(cx_split, ylo, cx_split + 36, ylo, INK, 2)
        s += rect(cx_split + 36, ylo - 9, 56, 18, "#ffffff", BLUE, 1.6, 3)
        s += text(cx_split + 64, ylo + 4, "470 kΩ", 10.5, BLUE, "middle", "bold")
        s += line(cx_split + 92, ylo, cx_term - 70, ylo, INK, 2)

        # збір обох гілок у клему
        s += line(cx_term - 70, yhi, cx_term - 70, ylo, INK, 2)
        s += line(cx_term - 70, yc, cx_term - 24, yc, INK, 2)

        # клема (золоте гніздо)
        s += circle(cx_term, yc, 12, "#f3e2a8", "#b5912e", 2)
        s += text(cx_term, yc + 5, str(i + 1), 13, INK, "middle", "bold")
        s += text(cx_term + 26, yc + 5, term_lab[i], 12.5, INK, "start", "bold")

        # вимірювання напруги клеми → АЦП (одна спільна стрілка-натяк)
        if i == 1:
            s += arrow(cx_term, yc - 12, ax + aw / 2 + 6, ay + ah + 4, GREEN, 1.6, "5 4")

    # легенда двох гілок (під резисторним блоком, без накладань)
    s += rect(cx_split + 8, my + mh - 8, 112, 16, "#ffffff", RED, 1.3, 4)
    s += text(cx_split + 64, my + mh + 4, "680 Ω — струм", 10.5, RED, "middle", "bold")
    s += rect(cx_split + 130, my + mh - 8, 122, 16, "#ffffff", BLUE, 1.3, 4)
    s += text(cx_split + 191, my + mh + 4, "470 kΩ — слабка", 10.5, BLUE, "middle", "bold")
    s += text((ax + cx_term) / 2 + 30, my + mh + 36,
              "зелений пунктир: той самий АЦП міряє напругу клем", 11.5, GREEN, "middle", style="italic")

    # підсумкова рамка-сенс
    s += rect(420, my + mh + 50, 340, 44, LSUN, "#e3d09a", 1.2, 6)
    s += text(590, my + mh + 68,
              "Три однакові клеми. Жодна не «база» чи «анод»", 11.5, INK, "middle", "bold")
    s += text(590, my + mh + 85,
              "наперед — роль кожної тестер ще має вгадати.", 11.5, INK, "middle")

    save("fig-r09-7c-1-test-port.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.9.7c.2 — перебір 6 перестановок + дерево рішень «що це за прилад»
# ─────────────────────────────────────────────────────────────────────────────
def fig2():
    W, H = 780, 500
    s = header(W, H)
    s += text(W / 2, 30, "Як тестер вгадує тип і розпіновку: спробуй усе — лиши те, що «спрацювало»",
              15.5, INK, "middle", "bold")

    # ── ліва колонка: 6 перестановок трьох клем ──
    lx = 40
    s += rect(lx, 52, 250, 250, "#ffffff", "#c9d3dc", 1.6, 8)
    s += text(lx + 125, 74, "1. Перебрати всі ролі", 13.5, INK, "middle", "bold")
    s += text(lx + 125, 92, "3 клеми → 6 перестановок", 11.5, GREY, "middle")
    perms = ["1-2-3", "1-3-2", "2-1-3", "2-3-1", "3-1-2", "3-2-1"]
    for i, p in enumerate(perms):
        col = i % 2
        row = i // 2
        bx = lx + 24 + col * 110
        by = 108 + row * 56
        s += rect(bx, by, 96, 42, LBLUE, "#9fb3e0", 1.4, 6)
        s += text(bx + 48, by + 19, p, 14, BLUE, "middle", "bold", mono=True)
        s += text(bx + 48, by + 35, "проба", 10.5, GREY, "middle")
    s += text(lx + 125, 296, "для кожної: подаємо напругу,", 11, INK, "middle")

    # стрілка ліворуч-праворуч
    s += arrow(lx + 252, 180, lx + 300, 180, GREY, 2.2)

    # ── права частина: дерево рішень ──
    rx = lx + 312
    s += rect(rx, 52, W - rx - 30, 250, "#ffffff", "#c9d3dc", 1.6, 8)
    s += text(rx + (W - rx - 30) / 2, 74, "2. Спитати фізику кожної проби", 13.5, INK, "middle", "bold")

    # питання → відповіді (дерево)
    qx = rx + 26
    rows = [
        ("Тече струм в ОБИДВА боки між парою клем?", "→ РЕЗИСТОР (міряємо опір дільником)", GREEN),
        ("Тече в ОДИН бік, ~0.7 В порогу?", "→ ДІОД (міряємо пряме падіння)", BLUE),
        ("Слабкий струм у слабкій гілці керує", "сильним у силовій?  → ТРАНЗИСТОР", RED),
        ("Заряд накопичується й тримається?", "→ КОНДЕНСАТОР (міряємо час заряду)", SUN),
    ]
    yy = 104
    for q, a, col in rows:
        s += circle(qx + 8, yy + 8, 7, col, col, 1)
        s += text(qx + 24, yy + 13, q, 12, INK, "start", "bold")
        s += text(qx + 24, yy + 31, a, 12, col, "start")
        yy += 50

    # ── нижня смуга: переможна проба фіксує і ТИП, і РОЗПІНОВКУ ──
    by = 326
    s += rect(40, by, W - 80, 150, LGRN, "#bfe0c6", 1.6, 10)
    s += text(W / 2, by + 26, "3. Перемагає проба з найкращим результатом — вона і дає відповідь",
              14, GREEN, "middle", "bold")

    # приклад: транзистор NPN, спрацювала перестановка 2-1-3
    ex = 70
    s += rect(ex, by + 44, 300, 90, "#ffffff", GREEN, 1.6, 8)
    s += text(ex + 150, by + 64, "напр., NPN-транзистор", 13, INK, "middle", "bold")
    s += text(ex + 150, by + 84, "найбільший коефіцієнт β — у пробі", 11.5, INK, "middle")
    s += text(ex + 150, by + 102, "де клема 2 = база", 12, RED, "middle", "bold")
    s += text(ex + 150, by + 120, "1=колектор · 2=база · 3=емітер", 11.5, INK, "middle")

    s += arrow(ex + 304, by + 89, ex + 360, by + 89, INK, 2.2)

    # результат на екрані
    sx = ex + 372
    s += rect(sx, by + 44, W - sx - 70, 90, "#10231a", "#0a160f", 2, 8)
    s += text(sx + (W - sx - 70) / 2, by + 66, "на екрані:", 11.5, "#8fd3a4", "middle")
    s += text(sx + (W - sx - 70) / 2, by + 90, "NPN  B=180", 16, "#eafff0", "middle", "bold", mono=True)
    s += text(sx + (W - sx - 70) / 2, by + 112, "C=1 B=2 E=3", 14, "#eafff0", "middle", "bold", mono=True)

    save("fig-r09-7c-2-permutation-tree.svg", s)


if __name__ == "__main__":
    fig1()
    fig2()
    print("done.")
