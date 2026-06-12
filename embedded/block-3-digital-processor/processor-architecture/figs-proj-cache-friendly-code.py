# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для ВСТАВКИ ⚙️ «Код, дружній до кешу» (до теми 3.5.9).
Окремий скрипт — головний figs.py розділу не чіпаємо. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif.
Підписи фігур у тексті — «Рис. 3.5.9a.k» (вставка до теми 3.5.9).
Допоміжні функції — копія зі стилю розділу 18, щоб вигляд був єдиний.
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
MONO  = "Consolas, 'DejaVu Sans Mono', monospace"


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
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", AMBER: "aAmber"}


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
    fam = MONO if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═══ Рис. 3.5.9a.1 — обхід 2D-масиву рядками проти стовпців ═══════════════════
def fig_order():
    W, H = 940, 600
    s = header(W, H)
    s += text(W / 2, 34, "Той самий масив, той самий обсяг роботи — інший порядок обходу",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "масив у пам'яті лежить рядок за рядком (row-major); колір клітинки — кешлінія, у яку вона потрапляє",
              11.5, GREY, "middle", style="italic")

    n = 4
    cell = 56
    # палітра ліній: один рядок = одна кешлінія
    linec = ["#dfeafc", "#e2f3e6", "#fdeede", "#f3e2f0"]
    lined = [BLUE, GREEN, AMBER, "#9a3b8a"]

    def grid(ox, oy, order, title, good):
        sub = ""
        # підпис над сіткою
        sub += text(ox + n * cell / 2, oy - 14, title, 15, INK, "middle", "bold")
        # клітинки
        for r in range(n):
            for c in range(n):
                x = ox + c * cell
                y = oy + r * cell
                sub_fill = linec[r]
                sub_loc = rect(x, y, cell, cell, sub_fill, lined[r], 1.4)
                sub += sub_loc
                sub += text(x + cell / 2, y + cell / 2 + 4,
                            f"[{r}][{c}]", 11.5, INK, "middle", mono=True)
        # порядок обходу — ламана через центри клітинок
        pts = []
        if order == "row":
            seq = [(r, c) for r in range(n) for c in range(n)]
        else:
            seq = [(r, c) for c in range(n) for r in range(n)]
        for (r, c) in seq:
            pts.append((ox + c * cell + cell / 2, oy + r * cell + cell / 2))
        col = GREEN if good else RED
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            sub += arrow(x1, y1, x2, y2, col, 2.2)
        # старт-маркер
        sub += rect(pts[0][0] - 7, pts[0][1] - 7, 14, 14, "none", col, 2.4)
        return sub

    s += grid(70, 110, "row", "Обхід РЯДКАМИ — for r: for c:  A[r][c]", True)
    s += grid(560, 110, "col", "Обхід СТОВПЦЯМИ — for c: for r:  A[r][c]", False)

    # нижні висновки
    yb = 110 + n * cell + 44
    s += rect(70, yb, n * cell, 86, "#f3f8f3", GREEN, 1.8, 10)
    s += text(70 + 12, yb + 26, "Сусіди в пам'яті — поспіль.", 13.5, GREEN, "start", "bold")
    s += text(70 + 12, yb + 48, "Витягли лінію (рядок) — і беремо", 12.5, INK, "start")
    s += text(70 + 12, yb + 66, "з неї всі 4: 1 промах, 3 влучання.", 12.5, INK, "start")

    s += rect(560, yb, n * cell, 86, "#fbf2f2", RED, 1.8, 10)
    s += text(560 + 12, yb + 26, "Кожен крок — у новій лінії.", 13.5, RED, "start", "bold")
    s += text(560 + 12, yb + 48, "Щоразу новий промах: тягнемо лінію", 12.5, INK, "start")
    s += text(560 + 12, yb + 66, "заради 1 клітинки, решту кидаємо.", 12.5, INK, "start")

    s += text(W / 2, H - 14,
              "Однакові 16 звернень — але обхід рядками влучає в кеш, обхід стовпцями б'є мимо. Звідси й різниця в рази.",
              12.5, INK, "middle", "bold")
    save("fig-3-5-9a-1-order.svg", s)


# ═══ Рис. 3.5.9a.2 — кешлінія: один промах тягне цілий блок ═══════════════════
def fig_line():
    W, H = 940, 540
    s = header(W, H)
    s += text(W / 2, 34, "Чому порядок важить: пам'ять їздить не байтами, а кешлініями",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "промах підтягує не одну комірку, а цілий блок-сусід (кешлінію) — типово десятки байтів за раз",
              11.5, GREY, "middle", style="italic")

    # стрічка пам'яті: 16 комірок, по 4 в лінії
    ox, oy = 70, 110
    cw = 50
    per = 4
    linec = ["#dfeafc", "#e2f3e6", "#fdeede", "#f3e2f0"]
    lined = [BLUE, GREEN, AMBER, "#9a3b8a"]
    s += text(ox, oy - 14, "ОЗП / пам'ять: адреси ростуть праворуч →", 13, INK, "start", "bold")
    for i in range(16):
        ln = i // per
        x = ox + i * cw
        s += rect(x, oy, cw, 44, linec[ln], lined[ln], 1.3)
        s += text(x + cw / 2, oy + 28, str(i), 12, INK, "middle", mono=True)
    # дужки ліній
    for ln in range(per):
        x0 = ox + ln * per * cw
        x1 = x0 + per * cw
        s += path(f"M{x0+4},{oy+54} L{x0+4},{oy+62} L{x1-4},{oy+62} L{x1-4},{oy+54}", "none", lined[ln], 1.8)
        s += text((x0 + x1) / 2, oy + 80, f"кешлінія {ln}", 11.5, lined[ln], "middle", "bold")

    # послідовний обхід
    sy = oy + 130
    s += text(ox, sy - 8, "Послідовно (рядками): просимо 0,1,2,3,4…", 14, GREEN, "start", "bold")
    s += text(ox, sy + 14, "1-й доступ у лінії — ПРОМАХ (тягнемо всю лінію з пам'яті);", 12.5, INK, "start")
    s += text(ox, sy + 34, "наступні 3 в тій самій лінії — ВЛУЧАННЯ (вже поруч у кеші). Лінію використали повністю.", 12.5, INK, "start")
    # маркер: промах/влучання під першими 8
    for i in range(8):
        x = ox + i * cw + cw / 2
        miss = (i % per == 0)
        col = RED if miss else GREEN
        lbl = "✗" if miss else "✓"
        s += text(x, sy + 58, lbl, 17, col, "middle", "bold")
    s += text(ox + 8 * cw + 14, sy + 58, "1 промах + 3 влучання на лінію", 12, GREEN, "start", "bold")

    # стрибковий обхід
    jy = sy + 110
    s += text(ox, jy - 8, "Стрибками (стовпцями, крок = ширина рядка): просимо 0,4,8,12,…", 14, RED, "start", "bold")
    s += text(ox, jy + 14, "Кожен наступний — уже в ІНШІЙ лінії: щоразу ПРОМАХ. Лінію тягнемо заради 1 комірки —", 12.5, INK, "start")
    s += text(ox, jy + 34, "і викидаємо решту 3. Та сама робота, але кеш не допомагає майже ніяк.", 12.5, INK, "start")
    for k, i in enumerate([0, 4, 8, 12]):
        x = ox + i * cw + cw / 2
        s += text(x, jy + 58, "✗", 17, RED, "middle", "bold")
    s += text(ox + 13 * cw, jy + 58, "усе — промахи", 12, RED, "start", "bold")

    save("fig-3-5-9a-2-line.svg", s)


# ═══ Рис. 3.5.9a.3 — пастки на МК: AoS↔SoA та де кеш узагалі є ════════════════
def fig_mcu():
    W, H = 940, 580
    s = header(W, H)
    s += text(W / 2, 34, "На мікроконтролері: розкладка даних і де кеш узагалі вмикається",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "ліворуч — як покласти масив структур, якщо обходять одне поле; праворуч — де порядок важить, а де ні",
              11.5, GREY, "middle", style="italic")

    # ── ліворуч: AoS vs SoA ──
    ox = 60
    s += text(ox, 92, "Обхід одного поля з масиву об'єктів", 14.5, INK, "start", "bold")

    # AoS
    ay = 112
    s += text(ox, ay + 14, "AoS — масив структур  {x,y,z}[]:", 12.5, RED, "start", "bold")
    fields = [("x", GREEN), ("y", FAINT), ("z", FAINT)]
    cw = 30
    xx = ox
    for obj in range(4):
        for (f, c) in fields:
            fill = "#e2f3e6" if c == GREEN else "#f1f1f1"
            s += rect(xx, ay + 26, cw, 30, fill, GREY, 1.1)
            s += text(xx + cw / 2, ay + 46, f, 11, INK, "middle", mono=True)
            xx += cw
    # потрібні лише x — підсвітити
    for obj in range(4):
        x = ox + obj * 3 * cw
        s += rect(x, ay + 26, cw, 30, "none", GREEN, 2.4)
    s += text(ox, ay + 76, "Потрібні лише x — а в лінію щоразу", 11.5, INK, "start")
    s += text(ox, ay + 94, "лізуть і непотрібні y,z. Корисних —", 11.5, INK, "start")
    s += text(ox, ay + 112, "лише третина лінії.", 11.5, RED, "start", "bold")

    # SoA
    sy2 = ay + 138
    s += text(ox, sy2 + 14, "SoA — структура масивів  x[],y[],z[]:", 12.5, GREEN, "start", "bold")
    xx = ox
    for i in range(8):
        s += rect(xx, sy2 + 26, cw, 30, "#e2f3e6", GREEN, 1.2)
        s += text(xx + cw / 2, sy2 + 46, "x", 11, INK, "middle", mono=True)
        xx += cw
    s += text(ox, sy2 + 76, "Усі x лежать поспіль — лінія несе", 11.5, INK, "start")
    s += text(ox, sy2 + 94, "самі лиш потрібні x. Уся лінія —", 11.5, INK, "start")
    s += text(ox, sy2 + 112, "у діло.", 11.5, GREEN, "start", "bold")

    # ── праворуч: де кеш є ──
    rx = 540
    s += text(rx, 92, "А чи є в цього МК кеш узагалі?", 14.5, INK, "start", "bold")
    cards = [
        ("Класичний 8-біт МК", "ОЗП = SRAM на кристалі, доступ за ~такт,",
         "кешу НЕМА. Порядок обходу майже не змінює часу.",
         "приклад: AVR ATmega", BLUE),
        ("МК з кешем флешу", "Код/дані відображено з повільного флешу,",
         "а ядро живить КЕШ. Тут порядок важить сильно.",
         "приклад: ESP32 (кеш ~32 КБ/ядро)", RED),
        ("Внутрішній рядок-буфер", "Навіть без кешу флеш часто віддає дані",
         "блоками. Послідовний доступ і тут вигідніший.",
         "багато ARM Cortex-M", AMBER),
    ]
    cy = 112
    for (t, l1, l2, ex, col) in cards:
        s += rect(rx, cy, 350, 116, "#fbfbfb", col, 1.8, 10)
        s += rect(rx, cy, 7, 116, col, col, 0, 0)
        s += text(rx + 20, cy + 26, t, 13.5, col, "start", "bold")
        s += text(rx + 20, cy + 48, l1, 11.3, INK, "start")
        s += text(rx + 20, cy + 66, l2, 11.3, INK, "start")
        s += text(rx + 20, cy + 96, ex, 11.3, GREY, "start", style="italic")
        cy += 130

    s += text(W / 2, H - 14,
              "Правило одне: дані, які читаєш разом, клади поряд і йди по них поспіль. Виграш — там, де між ядром і пам'яттю є кеш.",
              12, INK, "middle", "bold")
    save("fig-3-5-9a-3-mcu.svg", s)


if __name__ == "__main__":
    fig_order()
    fig_line()
    fig_mcu()
    print("cache-friendly insert figures done.")
