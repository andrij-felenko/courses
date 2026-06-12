# -*- coding: utf-8 -*-
"""
SVG-фігури для 🧮-вставки §3.3.8m — «Бюджет таймінгу: t_setup, t_hold,
t_clk-to-q — звідки береться межа частоти».
Окремий генератор (головний figs.py не чіпаємо), чистий Python без залежностей.
Вивід → ./img/. Стиль за AUTHORING §9: білий фон; «1» червоний, «0» синій;
висновок/поле — зелене; стрілки через marker; шрифт sans-serif.

Фігури:
  fig-16-8m-1-budget.svg   — період такту як «бюджет»: t_cq + t_logic + t_su + запас = T;
                             найдовший шлях між двома тригерами на тлі двох фронтів.
  fig-16-8m-2-fmax.svg     — як скорочення критичного шляху піднімає f_max:
                             два бюджети (повільна / швидша логіка) у тому самому масштабі.
  fig-16-8m-3-hold.svg     — гонка hold проти ТОГО САМОГО фронту: чому надто
                             короткий шлях (малий t_cq + t_logic) псує hold, і період тут ні до чого.
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
VIOL  = "#7a3fb0"
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
        f'  <marker id="dotInk" markerWidth="7" markerHeight="7" refX="3.2" refY="3.2"><circle cx="3.2" cy="3.2" r="2.4" fill="{INK}"/></marker>\n'
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


def darrow(x1, y1, x2, y2, color=INK, w=1.6):
    """Двобічна мірна стрілка (розмір)."""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}" marker-start="url(#{m})" marker-end="url(#{m})"/>\n')


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


def clk_wave(x0, y_hi, y_lo, edges, w=2.4, color=INK):
    """Прямокутний такт: edges — список x наростальних фронтів; між ними половина періоду.
    Малюємо просту хвилю 0/1 із чіткими фронтами в точках edges."""
    # будуємо як полілінію: старт низько, на кожному фронті — стрибок угору, через піврядок — униз
    s = ""
    pts = [(x0, y_lo)]
    for i in range(len(edges) - 1):
        e = edges[i]
        nxt = edges[i + 1]
        mid = (e + nxt) / 2.0
        pts.append((e, y_lo))
        pts.append((e, y_hi))
        pts.append((mid, y_hi))
        pts.append((mid, y_lo))
    # останній фронт
    e = edges[-1]
    pts.append((e, y_lo))
    pts.append((e, y_hi))
    pts.append((e + (edges[-1] - edges[-2]) / 2.0 if len(edges) > 1 else e + 30, y_hi))
    s += polyline(pts, color=color, w=w)
    return s


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1 — період такту як бюджет: t_cq + t_logic + t_su + запас = T
# ─────────────────────────────────────────────────────────────────────────────
def fig_budget():
    W, H = 860, 480
    s = header(W, H)
    s += text(W / 2, 30, "Період такту — це бюджет часу, який треба поділити",
              size=18, anchor="middle", weight="bold")

    # ── верх: маленька схема FF1 → логіка → FF2, спільний CLK ──
    yb = 70
    # FF1
    rect(0, 0, 0, 0)  # no-op guard
    ff1 = (70, yb)
    ff2 = (620, yb)
    bw, bh = 78, 70
    s += rect(ff1[0], ff1[1], bw, bh, fill="#f4f6ff", stroke=INK, sw=2, rx=6)
    s += text(ff1[0] + bw / 2, ff1[1] + 27, "FF1", size=15, anchor="middle", weight="bold")
    s += text(ff1[0] + bw / 2, ff1[1] + 46, "тригер", size=11, anchor="middle", color=GREY)
    # хмара логіки
    lx = ff1[0] + bw + 70
    lw = ff2[0] - lx - 70
    s += rect(lx, yb + 6, lw, bh - 12, fill="#fff8ec", stroke=AMBER, sw=2, rx=24)
    s += text(lx + lw / 2, yb + 33, "комбінаційна логіка", size=14, anchor="middle", weight="bold")
    s += text(lx + lw / 2, yb + 52, "(найдовший = критичний шлях)", size=11, anchor="middle", color=GREY)
    # FF2
    s += rect(ff2[0], ff2[1], bw, bh, fill="#f4f6ff", stroke=INK, sw=2, rx=6)
    s += text(ff2[0] + bw / 2, ff2[1] + 27, "FF2", size=15, anchor="middle", weight="bold")
    s += text(ff2[0] + bw / 2, ff2[1] + 46, "тригер", size=11, anchor="middle", color=GREY)

    # сполучні дроти з підписами Q1 / D2
    midy = yb + bh / 2
    s += arrow(ff1[0] + bw, midy, lx, yb + bh / 2, color=INK, w=2)
    s += text(ff1[0] + bw + 8, midy - 8, "Q1", size=12, color=BLUE)
    s += arrow(lx + lw, yb + bh / 2, ff2[0], midy, color=INK, w=2)
    s += text(ff2[0] - 30, midy - 8, "D2", size=12, color=RED)

    # спільний CLK до обох
    clky = yb + bh + 40
    s += line(ff1[0] + bw / 2, ff1[1] + bh, ff1[0] + bw / 2, clky, color=GREEN, w=2)
    s += line(ff2[0] + bw / 2, ff2[1] + bh, ff2[0] + bw / 2, clky, color=GREEN, w=2)
    s += line(ff1[0] + bw / 2, clky, ff2[0] + bw / 2, clky, color=GREEN, w=2)
    s += text(ff2[0] + bw / 2 + 14, clky + 4, "спільний CLK", size=12, color=GREEN, weight="bold")

    # ── низ: вісь часу з фронтами й сегментами бюджету ──
    axy = 320
    x_e1 = 120          # фронт N (запускає FF1)
    x_e2 = 700          # фронт N+1 (FF2 захоплює)
    # дві короткі хвильки такту над фронтами
    s += clk_wave(x_e1 - 50, axy - 150, axy - 118, [x_e1, x_e2], w=2.4, color=GREEN)
    s += text(x_e1 - 56, axy - 158, "CLK", size=12, color=GREEN, weight="bold", anchor="end")
    # вертикальні лінії фронтів
    for xe, lab in [(x_e1, "фронт N"), (x_e2, "фронт N+1")]:
        s += line(xe, axy - 150, xe, axy + 70, color=GREEN, w=1.6, dash="4 4")
        s += text(xe, axy + 90, lab, size=13, anchor="middle", color=GREEN, weight="bold")

    # сегменти: t_cq (FF1 видає Q1) | t_logic | t_su (D2 застиг до фронту) | запас(slack)
    seg_y = axy
    seg_h = 30
    # ширини (умовні, у пікселях, лише для ілюстрації пропорцій)
    p_cq, p_log, p_su, p_slk = 90, 250, 70, (x_e2 - x_e1) - (90 + 250 + 70)
    x = x_e1
    blocks = [
        (p_cq, "t_clk→q", "#dfe8ff", BLUE, "FF1 виставив Q1"),
        (p_log, "t_logic", "#ffeccb", AMBER, "логіка порахувала"),
        (p_su, "t_setup", "#ffd9d6", RED, "D2 застиг"),
        (p_slk, "запас (slack)", "#d8f3df", GREEN, "вільний резерв"),
    ]
    for wseg, lab, fill, edge, sub in blocks:
        s += rect(x, seg_y, wseg, seg_h, fill=fill, stroke=edge, sw=1.8, rx=3)
        if wseg > 60:
            s += text(x + wseg / 2, seg_y + 20, lab, size=13, anchor="middle", weight="bold", color=edge)
        else:
            s += text(x + wseg / 2, seg_y - 8, lab, size=12, anchor="middle", weight="bold", color=edge)
        s += text(x + wseg / 2, seg_y + seg_h + 16, sub, size=10.5, anchor="middle", color=GREY)
        x += wseg

    # повна дужка T згори сегментів
    bray = seg_y - 36
    s += darrow(x_e1, bray, x_e2, bray, color=INK, w=1.8)
    s += text((x_e1 + x_e2) / 2, bray - 8, "період такту T = 1 / f", size=14, anchor="middle", weight="bold")

    # формула-висновок унизу
    fy = axy + 120
    s += rect(120, fy, 580, 34, fill="#eef7f0", stroke=GREEN, sw=1.6, rx=6)
    s += text(130, fy + 22, "T  ≥  t_clk→q  +  t_logic(макс)  +  t_setup", size=16, weight="bold", color=INK)
    s += text(470, fy + 22, "→   запас ≥ 0", size=15, weight="bold", color=GREEN)

    save("fig-16-8m-1-budget.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2 — як скорочення критичного шляху піднімає f_max
# ─────────────────────────────────────────────────────────────────────────────
def fig_fmax():
    W, H = 860, 470
    s = header(W, H)
    s += text(W / 2, 30, "Скоротив критичний шлях — підняв стелю частоти f_max",
              size=18, anchor="middle", weight="bold")

    # спільна вісь часу (нс), однаковий масштаб для обох смуг
    x0 = 150
    scale = 9.0   # пікселів на нс
    # фіксовані частини (нс)
    t_cq, t_su = 4.0, 3.0
    # два варіанти логіки
    cases = [
        ("Повільна логіка", 30.0, 130, "#ffeccb"),
        ("Швидша логіка (спрощена / конвеєр)", 13.0, 250, "#ffe2bb"),
    ]
    # шкала зверху
    sy = 78
    s += line(x0, sy, x0 + 60 * scale, sy, color=GREY, w=1.4)
    for t in range(0, 61, 10):
        xx = x0 + t * scale
        s += line(xx, sy - 4, xx, sy + 4, color=GREY, w=1.2)
        s += text(xx, sy - 8, str(t), size=10.5, anchor="middle", color=GREY)
    s += text(x0 + 60 * scale + 8, sy + 4, "нс", size=11, color=GREY)

    for name, t_log, y, logfill in cases:
        T = t_cq + t_log + t_su
        f = 1000.0 / T  # МГц, бо T у нс
        # фон-смуга бюджету
        s += text(x0 - 12, y + 20, name, size=13, anchor="end", weight="bold")
        x = x0
        for wt, lab, fill, edge in [
            (t_cq, "t_clk→q", "#dfe8ff", BLUE),
            (t_log, "t_logic", logfill, AMBER),
            (t_su, "t_su", "#ffd9d6", RED),
        ]:
            ww = wt * scale
            s += rect(x, y, ww, 32, fill=fill, stroke=edge, sw=1.6, rx=3)
            if ww > 42:
                s += text(x + ww / 2, y + 21, lab, size=12, anchor="middle", weight="bold", color=edge)
                s += text(x + ww / 2, y - 6, f"{wt:.0f}", size=10.5, anchor="middle", color=GREY)
            x += ww
        # дужка повного T і підпис частоти
        s += darrow(x0, y + 46, x0 + T * scale, y + 46, color=INK, w=1.5)
        s += text(x0 + T * scale + 12, y + 26,
                  f"T = {T:.0f} нс   →   f_max = {f:.0f} МГц",
                  size=14, weight="bold", color=GREEN)

    # стрілка «менше → правіше стеля»
    y1 = cases[0][2] + 32
    y2 = cases[1][2]
    x_end1 = x0 + (t_cq + cases[0][1] + t_su) * scale
    x_end2 = x0 + (t_cq + cases[1][1] + t_su) * scale
    s += arrow(x_end1, y1 + 8, x_end2, y2 - 8, color=VIOL, w=2)
    s += text((x_end1 + x_end2) / 2 + 8, (y1 + y2) / 2 + 6,
              "коротший T", size=12, color=VIOL, weight="bold")

    # формула-висновок
    fy = 370
    s += rect(150, fy, 560, 60, fill="#eef7f0", stroke=GREEN, sw=1.6, rx=6)
    s += text(162, fy + 24, "f_max  =  1 / T_мін  =  1 / (t_clk→q + t_logic + t_setup)",
              size=15, weight="bold", color=INK)
    s += text(162, fy + 47,
              "t_clk→q і t_setup задані чипом; вище f можна лише, зменшивши t_logic.",
              size=12.5, color=GREY)

    save("fig-16-8m-2-fmax.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3 — гонка hold проти ТОГО САМОГО фронту
# ─────────────────────────────────────────────────────────────────────────────
def fig_hold():
    W, H = 860, 470
    s = header(W, H)
    s += text(W / 2, 30, "Hold — гонка проти ТОГО САМОГО фронту (період тут ні до чого)",
              size=17.5, anchor="middle", weight="bold")

    # один фронт у центрі, кілька рядків сигналів
    xe = 360
    top = 70
    # вертикаль фронту
    s += line(xe, top - 8, xe, 360, color=GREEN, w=1.8, dash="4 4")
    s += text(xe, 380, "той самий фронт (FF1 і FF2 спрацьовують разом)",
              size=12.5, anchor="middle", color=GREEN, weight="bold")

    rowh = 70
    lab_x = 30

    # рядок 1: CLK
    yc = top + 8
    s += text(lab_x, yc + 18, "CLK", size=13, weight="bold", color=GREEN)
    s += clk_wave(120, yc, yc + 30, [xe], w=2.4, color=GREEN)

    # вікно hold праворуч від фронту (заборонена зона)
    yh = top + rowh
    th_w = 60
    s += rect(xe, yh - 6, th_w, 150, fill="#ffecea", stroke=RED, sw=1.2, rx=3)
    s += text(xe + th_w / 2, yh - 12, "вікно t_hold", size=11.5, anchor="middle", color=RED, weight="bold")

    # рядок 2: D2 при ЗАКОРОТКОМУ шляху — Q1 уже добіг і смикнув D2 у вікні hold → збій
    y2 = top + rowh
    s += text(lab_x, y2 + 22, "D2  ← коротка", size=12.5, weight="bold", color=RED)
    s += text(lab_x, y2 + 38, "логіка (мало)", size=11, color=RED)
    # D2 був стабільний, потім невдовзі ПІСЛЯ фронту смикнувся (бо Q1→логіка швидко добігли)
    xchg = xe + 24
    s += polyline([(120, y2 + 30), (xchg, y2 + 30), (xchg, y2), (560, y2)], color=RED, w=2.4)
    s += arrow(xe + th_w / 2, y2 + 56, xchg, y2 + 30, color=RED, w=1.6)
    s += text(xe + th_w + 8, y2 + 60, "D2 змінився ВСЕРЕДИНІ вікна hold", size=12, color=RED, weight="bold")
    s += text(xe + th_w + 8, y2 + 76, "→ дані «прослизнули» на зайвий тригер: ЗБІЙ", size=11.5, color=RED)
    # «хибна» зона на зміні
    s += circle(xchg, y2 + 15, 5, fill=RED, stroke=RED, w=1)

    # рядок 3: D2 при НОРМАЛЬНОМУ шляху — зміна приходить ПІЗНІШЕ, поза вікном hold → чисто
    y3 = top + 2 * rowh + 36
    s += text(lab_x, y3 + 22, "D2  ← довша", size=12.5, weight="bold", color=GREEN)
    s += text(lab_x, y3 + 38, "логіка (досить)", size=11, color=GREEN)
    xchg3 = xe + th_w + 70
    s += polyline([(120, y3 + 30), (xchg3, y3 + 30), (xchg3, y3), (560, y3)], color=GREEN, w=2.4)
    s += text(xchg3 + 10, y3 + 18, "D2 змінився ПІСЛЯ вікна — чисто", size=12, color=GREEN, weight="bold")
    s += circle(xchg3, y3 + 15, 5, fill=GREEN, stroke=GREEN, w=1)
    # стрілка, що зміна посунулась праворуч за рахунок затримки логіки
    s += darrow(xchg, y3 + 52, xchg3, y3 + 52, color=GREY, w=1.4)
    s += text((xchg + xchg3) / 2, y3 + 68, "затримка шляху відсуває зміну праворуч",
              size=11, anchor="middle", color=GREY)

    # формула-висновок
    fy = 400
    s += rect(120, fy, 620, 50, fill="#eef7f0", stroke=GREEN, sw=1.6, rx=6)
    s += text(132, fy + 22, "t_clk→q + t_logic(мін)  ≥  t_hold      (умова короткого шляху)",
              size=14.5, weight="bold", color=INK)
    s += text(132, fy + 42,
              "Не залежить від T: повільніший такт hold не лікує — рятують буфери на закоротких шляхах.",
              size=11.5, color=GREY)

    save("fig-16-8m-3-hold.svg", s)


if __name__ == "__main__":
    fig_budget()
    fig_fmax()
    fig_hold()
    print("done.")
