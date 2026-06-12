# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для 🧮-вставки «Арифметика продуктивності» (до §3.5.5, Модуль 3).
Окремий скрипт вставки (головний figs.py розділу не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/. Імена файлів — з токеном "18-5m", щоб не конфліктувати з фігурами теми (18-5-*).

Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif; єдиний вигляд з рештою розділів.
Нумерація підписів у тексті — Рис. 3.5.5m.k (на диску імена не перенумеровуються).
Хелпери — копія зі спільного набору розділу (за §9 кожен скрипт самодостатній).
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


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.5.5m.1 — «Залізний закон»: час = команди × CPI × період такту
# Три множники як три «ручки», кожну крутить свій рівень рішень.
# ═══════════════════════════════════════════════════════════════════════════
def fig_ironlaw():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 36, "«Залізний закон» продуктивності: час програми = добуток трьох множників",
              20, INK, "middle", "bold")
    s += text(W / 2, 59, "розженеш один множник — час падає; та кожну «ручку» крутить свій рівень, і вони тягнуть одне одного",
              12.5, GREY, "middle", style="italic")

    # три колонки-блоки
    cols = [
        (150, GREEN, "N", "Скільки команд",
         ["кількість команд", "у програмі (instruction count)"],
         ["що задає:", "• ISA (§3.5.4): CISC — менше", "  команд, RISC — більше", "• компілятор та алгоритм"]),
        (450, BLUE, "CPI", "Тактів на команду",
         ["середньо тактів", "на одну команду (CPI)"],
         ["що задає:", "• мікроархітектура: конвеєр", "  (§3.5.6), кеш (§3.5.9)", "• склад самих команд"]),
        (750, RED, "T", "Довжина такту",
         ["період такту T = 1 / частота", "(секунд на такт)"],
         ["що задає:", "• критичний шлях (§3.1.5,", "  §3.3.8) → стеля частоти", "• техпроцес, напруга, тепло"]),
    ]

    # рядок-формула з кольоровими множниками
    fy2 = 138
    s += text(170, fy2, "час", 20, INK, "middle", "bold")
    s += text(210, fy2, "=", 20, INK, "middle")
    s += text(250, fy2, "N", 22, GREEN, "middle", "bold")
    s += text(285, fy2, "×", 20, INK, "middle")
    s += text(335, fy2, "CPI", 22, BLUE, "middle", "bold")
    s += text(385, fy2, "×", 20, INK, "middle")
    s += text(425, fy2, "T", 22, RED, "middle", "bold")
    s += text(640, fy2, "(а робота за секунду = 1 / час)", 13, GREY, "middle", style="italic")

    boxw, boxh = 240, 250
    by = 170
    for cx, col, sym, head, mid, who in cols:
        bx = cx - boxw / 2
        s += rect(bx, by, boxw, boxh, "#ffffff", col, 2.4, 12)
        s += rect(bx, by, boxw, 40, col, col, 0, 12)
        s += rect(bx, by + 28, boxw, 12, col, col, 0, 0)  # square off bottom of header band
        s += text(cx, by + 27, f"{sym} — {head}", 16, "#ffffff", "middle", "bold")
        yy = by + 64
        for ln in mid:
            s += text(cx, yy, ln, 13, INK, "middle")
            yy += 19
        yy += 8
        s += line(bx + 16, yy - 6, bx + boxw - 16, yy - 6, FAINT, 1.4)
        for ln in who:
            wgt = "bold" if ln.endswith(":") else "normal"
            s += text(bx + 16, yy + 10, ln, 12, GREY if not ln.endswith(":") else INK, "start", wgt)
            yy += 17

    # підсумкова стрічка
    s += rect(70, 442, W - 140, 20, "#f5f7fb", BLUE, 0, 6)
    s += text(W / 2, 456, "Жоден множник окремо не каже про швидкість: МГц — це лише 1/T, "
                          "одна ручка з трьох. Важить ДОБУТОК.",
              12.5, INK, "middle")
    save("fig-18-5m-1-ironlaw.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.5.5m.2 — чому MIPS бреше між різними ISA:
# та сама задача → різна кількість команд → MIPS міряє НЕ роботу.
# ═══════════════════════════════════════════════════════════════════════════
def fig_mips_lies():
    W, H = 900, 500
    s = header(W, H)
    s += text(W / 2, 36, "Чому MIPS теж оманливий: однакова РОБОТА — різне число команд",
              20, INK, "middle", "bold")
    s += text(W / 2, 59, "MIPS рахує мільйони команд за секунду; але «команда» в різних ISA робить різну порцію роботи",
              12.5, GREY, "middle", style="italic")

    # Спільна задача
    s += rect(W / 2 - 230, 78, 460, 34, "#f3f3f3", GREY, 1.6, 8)
    s += text(W / 2, 100, "Одна й та сама задача: порахувати a = b + c·d (однаковий результат)",
              13.5, INK, "middle", "bold")

    # Дві машини
    pan = [
        (235, BLUE, "Машина X — «густа» ISA (CISC-стиль)",
         ["1 команда: MAC  a, b, c, d", "(множення-додавання за раз)"],
         "N = 1 команда", "100 МГц · CPI = 5",
         "MIPS = 100/5 = 20", "робота: 1 задача за 5 тактів"),
        (665, GREEN, "Машина Y — «проста» ISA (RISC-стиль)",
         ["MUL t, c, d", "ADD a, b, t", "(те саме — двома командами)"],
         "N = 2 команди", "100 МГц · CPI = 1",
         "MIPS = 100/1 = 100", "робота: 1 задача за 2 такти"),
    ]
    bx0 = 60
    boxw = 360
    by = 128
    for cx, col, title, code, ncount, clk, mips, work in pan:
        bx = cx - boxw / 2
        s += rect(bx, by, boxw, 250, "#ffffff", col, 2.4, 12)
        s += rect(bx, by, boxw, 38, col, col, 0, 12)
        s += rect(bx, by + 26, boxw, 12, col, col, 0, 0)
        s += text(cx, by + 25, title, 14.5, "#ffffff", "middle", "bold")
        # код у моноширинному вигляді
        yy = by + 66
        s += rect(bx + 18, yy - 18, boxw - 36, 22 * len(code) + 12, "#f6f8fc", FAINT, 1.4, 6)
        for ln in code:
            s += (f'<text x="{bx + 30:.1f}" y="{yy:.1f}" font-family="Consolas, monospace" '
                  f'font-size="13.5" fill="{INK}">{_esc(ln)}</text>\n')
            yy += 22
        yy += 16
        s += text(cx, yy, ncount, 14, INK, "middle", "bold"); yy += 24
        s += text(cx, yy, clk, 13, GREY, "middle"); yy += 26
        s += text(cx, yy, mips, 17, col, "middle", "bold"); yy += 24
        s += text(cx, yy, work, 12.5, INK, "middle", style="italic")

    # стрілка-висновок
    s += text(W / 2, 410, "↓", 26, RED, "middle", "bold")
    s += rect(70, 422, W - 140, 60, "#fdf3f2", RED, 1.8, 8)
    s += text(W / 2, 444,
              "Y показує MIPS = 100 проти 20 у X — у п'ять разів «більше»!",
              14.5, RED, "middle", "bold")
    s += text(W / 2, 466,
              "Та обидві роблять ту саму роботу; Y лише дробить її на більше дрібних команд. "
              "MIPS міряє команди, а не роботу.",
              12.5, INK, "middle")
    save("fig-18-5m-2-mips-lies.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.5.5m.3 — наскрізний worked example: три процесори, той самий код,
# від частоти й CPI до часу й «у скільки разів швидше». Таблиця + смуги.
# ═══════════════════════════════════════════════════════════════════════════
def fig_worked():
    W, H = 900, 520
    s = header(W, H)
    s += text(W / 2, 34, "Порахуймо чесно: три процесори, та сама програма (10⁹ команд)",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "час = N × CPI × T = N × CPI / частота;  менший час = швидше (нижче — короча смуга)",
              12.5, GREY, "middle", style="italic")

    # ── таблиця ──
    tx, ty = 60, 80
    tw = W - 120
    rows = 4
    rh = 34
    cols_x = [tx, tx + 150, tx + 300, tx + 450, tx + 600, tx + tw]
    headers = ["процесор", "частота", "CPI", "час = N·CPI/f", "у скільки разів"]
    # шапка
    s += rect(tx, ty, tw, rh, "#eef1f6", GREY, 1.4, 0)
    for i, h in enumerate(headers):
        s += text(cols_x[i] + 12, ty + 22, h, 13.5, INK, "start", "bold")
    # рядки даних: (name, color, freq_text, cpi, time_text, rel_text)
    data = [
        ("A", RED,   "200 МГц", "4.0", "10⁹·4 / 2·10⁸ = 20.0 с", "база (×1.0)"),
        ("B", BLUE,  "100 МГц", "1.0", "10⁹·1 / 1·10⁸ = 10.0 с", "×2.0 швидше"),
        ("C", GREEN, "240 МГц", "1.2", "10⁹·1.2 / 2.4·10⁸ = 5.0 с", "×4.0 швидше"),
    ]
    for r, (name, col, freq, cpi, tt, rel) in enumerate(data):
        ry = ty + rh * (r + 1)
        fill = "#ffffff" if r % 2 == 0 else "#fafbfd"
        s += rect(tx, ry, tw, rh, fill, FAINT, 1.0, 0)
        s += circle(cols_x[0] + 22, ry + rh / 2, 11, col, col, 0)
        s += text(cols_x[0] + 22, ry + 21, name, 14, "#ffffff", "middle", "bold")
        s += text(cols_x[1] + 12, ry + 22, freq, 13, INK, "start")
        s += text(cols_x[2] + 12, ry + 22, cpi, 13, INK, "start")
        s += (f'<text x="{cols_x[3] + 12:.1f}" y="{ry + 22:.1f}" font-family="Consolas, monospace" '
              f'font-size="12.5" fill="{INK}">{_esc(tt)}</text>\n')
        s += text(cols_x[4] + 12, ry + 22, rel, 13, col, "start", "bold")
    # вертикальні лінії таблиці
    for cxv in cols_x[1:-1]:
        s += line(cxv, ty, cxv, ty + rh * rows, FAINT, 1.0)
    s += rect(tx, ty, tw, rh * rows, "none", GREY, 1.4, 0)

    # ── смуги часу (менше = швидше) ──
    bx0 = 150
    bmax = 600  # пікселів на 20 с
    base_t = 20.0
    byy = ty + rh * rows + 54
    s += text(tx, byy - 14, "Час виконання (коротша смуга = швидший процесор):", 13.5, INK, "start", "bold")
    bars = [("A", RED, 20.0), ("B", BLUE, 10.0), ("C", GREEN, 5.0)]
    for i, (name, col, t) in enumerate(bars):
        yb = byy + i * 46
        s += text(bx0 - 16, yb + 20, name, 14, col, "end", "bold")
        wbar = bmax * (t / base_t)
        s += rect(bx0, yb, wbar, 28, col, col, 0, 5)
        s += text(bx0 + wbar + 10, yb + 20, f"{t:.0f} с", 13.5, INK, "start", "bold")
    # вісь
    s += line(bx0, byy - 4, bx0, byy + 3 * 46 - 8, GREY, 1.2)

    # висновок
    s += rect(60, H - 44, W - 120, 30, "#f2f8f4", GREEN, 1.6, 8)
    s += text(W / 2, H - 24,
              "C на 240 МГц б'є A на 200 МГц у 4 рази; B на 100 МГц — удвічі швидший за A. "
              "Вирішує добуток CPI·T, а не самі МГц.",
              12.5, INK, "middle")
    save("fig-18-5m-3-worked.svg", s)


if __name__ == "__main__":
    fig_ironlaw()
    fig_mips_lies()
    fig_worked()
    print("ch18-s5-m performance-math figures done.")
