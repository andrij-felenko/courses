# -*- coding: utf-8 -*-
"""
SVG-фігури для 🔌-вставки §3.3.7c — «Лічильники-мікросхеми 74HC4017/4040:
біжучий вогник і дільник без МК».
Окремий генератор (головний figs.py не чіпаємо), чистий Python без залежностей.
Вивід → ./img/. Стиль за AUTHORING §9: білий фон; «1» червоний, «0» синій;
висновок/поле — зелене; стрілки через marker; шрифт sans-serif.

Фігури:
  fig-16-7c-1-two-flavors.svg — два класи лічильника-чипа: декадний (Johnson, 1-з-10)
                                і двійковий-дільник; що в кожного на виходах
  fig-16-7c-2-wiring.svg      — розпіновка обох DIP-16 і підключення без МК
                                (RC-генератор → CLK; біжучий вогник; поділ частоти)
  fig-16-7c-3-waves.svg       — часові діаграми: 10 виходів '4017 «біжать» по черзі;
                                біти '4040 діляться навпіл, навпіл, навпіл…
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
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


def led(cx, cy, on, r=10):
    """Світлодіод: коло + промінчики, якщо горить."""
    col = RED if on else GREY
    fill = "#ffe6e0" if on else "#f1f1f1"
    out = circle(cx, cy, r, fill, col, 2)
    if on:
        for a in (-0.9, 0.0, 0.9):
            import math
            dx, dy = math.cos(a - 1.57), math.sin(a - 1.57)
            out += line(cx + dx * (r + 2), cy + dy * (r + 2),
                        cx + dx * (r + 8), cy + dy * (r + 8), RED, 1.6)
    return out


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Фігура 1: два класи лічильника-чипа ──────────────────────────────────────
def fig1_two_flavors():
    W, H = 820, 540
    b = header(W, H)
    b += text(W / 2, 30, "Один такт на вході — а на виходах дві різні «мови» рахунку",
              17, INK, "middle", "bold")
    b += text(W / 2, 52, "лічильник §3.3.7, відлитий у корпус: декадний (1-з-10) проти двійкового-дільника",
              12, GREY, "middle", "italic")

    # спільний вхід-такт зліва
    b += rect(40, 250, 86, 70, "#eef7ee", GREEN, 2, 8)
    b += text(83, 280, "такт", 14, GREEN, "middle", "bold")
    b += text(83, 300, "CLK ↑↑↑", 11, GREY, "middle")
    b += arrow(126, 285, 250, 200, GREEN, 2.2)
    b += arrow(126, 285, 250, 400, GREEN, 2.2)

    # ── ВЕРХ: декадний 74HC4017 — біжучий вогник ──
    b += rect(250, 110, 520, 175, "#f4f7ff", BLUE, 2, 10)
    b += text(262, 134, "74HC4017 — декадний лічильник (Johnson, 5 ступенів)",
              14, BLUE, "start", "bold")
    b += text(262, 152, "10 ДЕКОДОВАНИХ виходів: у кожну мить «1» рівно на одному, решта — «0»",
              11, INK, "start")
    # десять виходів-світлодіодів, активний — третій
    active = 2
    ox, dox = 285, 46
    oy = 205
    for i in range(10):
        cx = ox + i * dox
        on = (i == active)
        b += led(cx, oy, on, 11)
        b += text(cx, oy + 28, f"Q{i}", 10, (RED if on else GREY), "middle",
                  "bold" if on else "normal")
    b += text(ox + active * dox, oy - 22, "тільки цей горить", 10, RED, "middle")
    b += arrow(ox + active * dox, oy - 18, ox + active * dox, oy - 6, RED, 1.6)
    b += text(262, 268, "наступний фронт → вогник перестрибує на Q3, потім Q4… — «біжить» по колу",
              11, GREEN, "start", "italic")

    # ── НИЗ: двійковий 74HC4040 — дільник ──
    b += rect(250, 320, 520, 175, "#fff7ec", AMBER, 2, 10)
    b += text(262, 344, "74HC4040 — двійковий лічильник-дільник (12 ступенів)",
              14, "#9a7b20", "start", "bold")
    b += text(262, 362, "12 виходів = РОЗРЯДИ одного числа; кожен наступний удвічі повільніший",
              11, INK, "start")
    # вісім розрядів (показуємо Q1..Q8 для місця) як двійкове число 00101101
    bitsx, dbx = 300, 52
    biy = 408
    sample = [0, 0, 1, 0, 1, 1, 0, 1]  # довільний «знімок» числа
    labels = ["Q12", "Q11", "Q10", "Q9", "Q4", "Q3", "Q2", "Q1"]
    for i, (v, nm) in enumerate(zip(sample, labels)):
        cx = bitsx + i * dbx
        col = RED if v else BLUE
        b += rect(cx - 18, biy - 18, 36, 36, "#fff", col, 2, 5)
        b += text(cx, biy + 6, str(v), 18, col, "middle", "bold")
        b += text(cx, biy + 34, nm, 10, GREY, "middle")
    b += text(bitsx + 3.5 * dbx, biy - 30, "ті самі виходи — це біти числа, що росте щотакту",
              10, "#9a7b20", "middle")
    b += text(262, 470, "Q1 = такт/2, Q2 = такт/4, … Q12 = такт/4096 — готовий дільник частоти на 2ⁿ",
              11, GREEN, "start", "italic")

    # підсумок
    b += text(W / 2, 522, "Та сама ідея §3.3.7 — лише «прочитана» двома способами: «де зараз вогник» проти «яке зараз число»",
              12, GREEN, "middle", "bold")
    save("fig-16-7c-1-two-flavors.svg", b)


# ── Фігура 2: розпіновка обох DIP-16 і підключення без МК ─────────────────────
def fig2_wiring():
    W, H = 840, 560
    b = header(W, H)
    b += text(W / 2, 28, "Розпіновка (DIP-16) і схема без мікроконтролера",
              17, INK, "middle", "bold")

    # ── RC-генератор такту (спільний для обох прикладів) ──
    gx, gy, gw, gh = 40, 70, 150, 110
    b += rect(gx, gy, gw, gh, "#eef7ee", GREEN, 2, 8)
    b += text(gx + gw / 2, gy + 22, "генератор такту", 12, GREEN, "middle", "bold")
    b += text(gx + gw / 2, gy + 42, "74HC14 + R + C", 11, INK, "middle")
    b += text(gx + gw / 2, gy + 60, "(інвертор Шмітта", 10, GREY, "middle")
    b += text(gx + gw / 2, gy + 74, "§3.1.6 — повільні", 10, GREY, "middle")
    b += text(gx + gw / 2, gy + 88, "імпульси CLK)", 10, GREY, "middle")
    b += text(gx + gw / 2, gy + 104, "f ≈ 1/(RC)", 11, GREEN, "middle", "italic")

    def chip(cx, cy, cw, ch, name, sub, left, right, pin1):
        out = rect(cx, cy, cw, ch, "#fbfbfb", INK, 2, 8)
        out += circle(cx + cw / 2, cy + 13, 6, "#fff", INK, 1.6)
        out += text(cx + cw / 2, cy + 38, name, 14, INK, "middle", "bold")
        out += text(cx + cw / 2, cy + 55, sub, 10, GREY, "middle")
        n = len(left)
        pitch = (ch - 50) / (n - 1)
        py0 = cy + 36
        for i, (nm, col) in enumerate(left):
            y = py0 + i * pitch
            out_pin = pin1 + i
            out += line(cx - 24, y, cx, y, INK, 2)
            out += circle(cx - 24, y, 2.6, INK, INK, 1)
            out += text(cx - 28, y - 3, f"{out_pin}", 9, GREY, "end")
            out += text(cx + 5, y + 4, nm, 11, col, "start", "bold")
        for i, (nm, col) in enumerate(right):
            y = py0 + i * pitch
            out_pin = pin1 + 2 * n - 1 - i
            out += line(cx + cw, y, cx + cw + 24, y, INK, 2)
            out += circle(cx + cw + 24, y, 2.6, INK, INK, 1)
            out += text(cx + cw + 28, y - 3, f"{out_pin}", 9, GREY, "start")
            out += text(cx + cw - 5, y + 4, nm, 11, col, "end", "bold")
        return out

    # ── 74HC4017: біжучий вогник ──
    c1x, c1y, c1w, c1h = 300, 70, 120, 210
    left4017 = [("Q5", BLUE), ("Q1", BLUE), ("Q0", RED), ("Q2", BLUE),
                ("Q6", BLUE), ("Q7", BLUE), ("Q3", BLUE), ("GND", BLUE)]
    right4017 = [("VDD", RED), ("RST", GREEN), ("CLK", GREEN), ("CE", INK),
                 ("Q9", BLUE), ("CO", AMBER), ("Q4", BLUE), ("Q8", BLUE)]
    b += chip(c1x, c1y, c1w, c1h, "74HC4017", "декадний", left4017, right4017, 1)
    b += text(c1x + c1w / 2, c1y - 8, "Біжучий вогник (10 LED)", 12, BLUE, "middle", "bold")
    # генератор → CLK (пін 14, справа)
    b += polyline([(gx + gw, gy + gh / 2), (c1x + c1w + 70, gy + gh / 2),
                   (c1x + c1w + 70, c1y + 36 + 2 * (c1h - 50) / 7),
                   (c1x + c1w + 24, c1y + 36 + 2 * (c1h - 50) / 7)], GREEN, 2)
    b += text(c1x + c1w + 30, gy + gh / 2 - 6, "CLK", 10, GREEN, "start", "bold")
    # десять LED від лівих/правих Q-ніжок (схематично — гірлянда праворуч-знизу)
    lx, ly, ldx = 470, 360, 32
    b += text(lx + 4.5 * ldx, ly - 22, "десять світлодіодів — по одному на кожен вихід Q0…Q9",
              11, INK, "middle")
    for i in range(10):
        cx = lx + i * ldx
        b += led(cx, ly, i == 2, 9)
        b += text(cx, ly + 24, f"{i}", 9, GREY, "middle")
    b += arrow(c1x + c1w + 24, c1y + 36, lx - 10, ly - 6, GREY, 1.6, "4,3")
    b += text(lx + 4.5 * ldx, ly + 40, "вогник перебігає 0→1→2→…→9→0; CO (пін 12) дає один імпульс за 10 тактів",
              10, AMBER, "middle")
    # RST/CE підказка
    b += text(c1x + c1w + 28, c1y + 36 + 1 * (c1h - 50) / 7 + 14,
              "RST=0, CE=0", 9, GREY, "start")
    b += text(c1x + c1w + 28, c1y + 36 + 3 * (c1h - 50) / 7 + 14,
              "(інакше стоп)", 9, GREY, "start")

    # ── 74HC4040: дільник частоти ──
    c2x, c2y, c2w, c2h = 300, 350, 120, 165
    left4040 = [("Q12", BLUE), ("Q6", BLUE), ("Q5", BLUE), ("Q7", BLUE),
                ("Q4", BLUE), ("Q3", BLUE), ("Q2", BLUE), ("GND", BLUE)]
    right4040 = [("VDD", RED), ("Q11", BLUE), ("Q10", BLUE), ("Q8", BLUE),
                 ("Q9", BLUE), ("RST", GREEN), ("CLK", GREEN), ("Q1", RED)]
    b += chip(c2x, c2y, c2w, c2h, "74HC4040", "12-розр. дільник", left4040, right4040, 1)
    b += text(c2x + c2w / 2, c2y - 8, "Поділ частоти на 2ⁿ", 12, "#9a7b20", "middle", "bold")
    b += polyline([(gx + gw / 2, gy + gh), (gx + gw / 2, c2y + 36 + 6 * (c2h - 50) / 7),
                   (c2x - 24, c2y + 36 + 6 * (c2h - 50) / 7)], GREEN, 2)
    b += text(gx + gw / 2 + 6, c2y + 24, "той самий CLK", 10, GREEN, "start")
    # виходи-дільники праворуч
    b += text(620, 388, "будь-який вихід — поділена частота:", 11, INK, "start")
    rows = [("Q1  (пін 9)", "такт / 2", RED),
            ("Q4  (пін 7)", "такт / 16", INK),
            ("Q10 (пін 14)", "такт / 1024", INK),
            ("Q12 (пін 1)", "такт / 4096", GREEN)]
    for i, (nm, val, col) in enumerate(rows):
        yy = 410 + i * 22
        b += text(620, yy, nm, 11, col, "start", "bold")
        b += text(740, yy, "→ " + val, 11, col, "start")
    b += text(620, 506, "16 МГц / 4096 ≈ 3.9 кГц — без жодного рядка коду",
              11, "#9a7b20", "start", "italic")

    b += text(W / 2, 544, "Живлення VDD/GND + блокувальний конденсатор 100 нФ — і чип рахує сам, без МК",
              12, GREEN, "middle", "bold")
    save("fig-16-7c-2-wiring.svg", b)


# ── Фігура 3: часові діаграми обох чипів ─────────────────────────────────────
def fig3_waves():
    W, H = 840, 560
    b = header(W, H)
    b += text(W / 2, 28, "Що видно осцилографом: вогник «біжить», біти «діляться»",
              17, INK, "middle", "bold")

    x0, x1 = 150, 800
    n = 11                                   # показуємо 11 тактів
    edges = [x0 + 30 + i * ((x1 - x0 - 40) / n) for i in range(n)]
    seg = (x1 - x0 - 40) / n

    def clk_track(y):
        out = text(x0 - 14, y + 5, "CLK", 12, INK, "end", "bold")
        pts = [(x0, y + 14)]
        pw = seg * 0.45
        for ex in edges:
            pts += [(ex, y + 14), (ex, y - 14), (ex + pw, y - 14), (ex + pw, y + 14)]
            out += circle(ex, y - 14, 2.6, GREEN, GREEN, 1)
        pts += [(x1, y + 14)]
        out += polyline(pts, INK, 2.0)
        for i, ex in enumerate(edges):
            out += text(ex + pw / 2, y + 30, f"{i}", 9, GREY, "middle")
        return out

    # ── 74HC4017: чотири з десяти виходів, кожен високий у «свій» такт ──
    b += text(x0 - 14, 70, "74HC4017", 13, BLUE, "end", "bold")
    b += text(x0 + (x1 - x0) / 2, 70, "кожен вихід — «1» рівно в один такт, по черзі (1-з-10)",
              11, BLUE, "middle", "italic")
    b += clk_track(95)
    show = [0, 1, 2, 3]
    for k, q in enumerate(show):
        y = 150 + k * 40
        b += text(x0 - 14, y + 5, f"Q{q}", 12, INK, "end", "bold")
        pts = [(x0, y + 12)]
        for i, ex in enumerate(edges):
            hi = (i % 10 == q)
            lvl = y - 12 if hi else y + 12
            xe = ex
            xnext = edges[i + 1] if i + 1 < len(edges) else x1
            pts += [(xe, pts[-1][1]), (xe, lvl), (xnext, lvl)]
        # підсвітити «свій» такт (під лінією), потім намалюємо саму лінію поверх
        for i, ex in enumerate(edges):
            if i % 10 == q:
                xnext = edges[i + 1] if i + 1 < len(edges) else x1
                b += rect(ex, y - 13, xnext - ex, 26, "#ffe6e0", "none", 0, 3)
                b += text((ex + xnext) / 2, y - 18, "HIGH", 9, RED, "middle", "bold")
        # перемалювати лінію поверх підсвітки
        b += polyline(pts, INK, 2.2)
    b += text(x1, 150 - 22, "…і так до Q9, далі знову Q0", 10, GREEN, "end", "italic")

    # роздільник
    b += line(x0 - 30, 330, x1, 330, FAINT, 1.5)

    # ── 74HC4040: молодші біти діляться навпіл ──
    b += text(x0 - 14, 360, "74HC4040", 13, "#9a7b20", "end", "bold")
    b += text(x0 + (x1 - x0) / 2, 360, "кожен наступний біт удвічі повільніший — поділ частоти",
              11, "#9a7b20", "middle", "italic")
    b += clk_track(385)
    # Q1=÷2, Q2=÷4, Q3=÷8 — біт q високий, коли ціла частина (такт / div) непарна.
    # (Будуємо ідеальний меандр з періодом div тактів; фаза-затримка переносу
    #  для масштабу рисунка несуттєва — показуємо саме поділ частоти.)
    for k, (q, div) in enumerate([(1, 2), (2, 4), (3, 8)]):
        y = 440 + k * 38
        b += text(x0 - 14, y + 5, f"Q{q}", 12, INK, "end", "bold")
        b += text(x0 - 14, y + 19, f"÷{div}", 9, GREY, "end")
        pts = [(x0, y + 12)]
        for i in range(n):
            hi = ((i // div) % 2) == 1
            lvl = y - 12 if hi else y + 12
            xe = edges[i]
            xnext = edges[i + 1] if i + 1 < len(edges) else x1
            pts += [(xe, pts[-1][1]), (xe, lvl), (xnext, lvl)]
        b += polyline(pts, INK, 2.4)
    b += text(x1, 440 - 20, "Q1 міняється щотакту, Q2 — раз на 2, Q3 — раз на 4…",
              10, "#9a7b20", "end", "italic")

    b += text(W / 2, 548, "Жоден з виходів не потребує програми — це чиста апаратна лічба тактів (§3.3.7)",
              12, GREEN, "middle", "bold")
    save("fig-16-7c-3-waves.svg", b)


if __name__ == "__main__":
    fig1_two_flavors()
    fig2_wiring()
    fig3_waves()
    print("ch16-s7-c-counter-ics figures done.")
