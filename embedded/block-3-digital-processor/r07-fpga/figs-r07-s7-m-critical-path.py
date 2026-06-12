# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки §3.7.7m —
«Критичний шлях і slack: звідки береться максимальна частота дизайну».
Чистий Python, без залежностей. Вивід → ./img/ (унікальні імена fig-r07-7m-*).
Стиль (AUTHORING §9): білий фон; «+»/швидке/чисте червоний, «−»/повільне синій;
поле/висновок/запас (slack) зелене; стрілки через marker; шрифт sans-serif.
Хелпери скопійовано з math-вставок розділу (за §9 — кожен скрипт самодостатній).
Нумерація підписів: Рис. 3.7.7m.k.
НЕ чіпає головний figs.py розділу.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"   # критичний шлях / акцент-«найдовший»
BLUE  = "#1f47b5"   # повільне / маршрутизація
GREEN = "#1f8a3b"   # запас (slack) / висновок / «встигло»
AMBER = "#caa24a"   # проміжний акцент
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
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
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", GREEN: "aGreen", BLUE: "aBlue", GREY: "aGrey", AMBER: "aAmber"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def polyline(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def roundrect(x, y, w, h, color=GREEN, sw=3, rx=14, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{color}" stroke-width="{sw}"{d}/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


def ff(x, y, w, h, label, color=INK):
    """Тригер-прямокутник із трикутничком такту в куті (умовно)."""
    s = rect(x, y, w, h, "#eef2fb", color, 2, rx=4)
    s += text(x + w / 2, y + h / 2 + 5, label, 14, color, "middle", "bold")
    # значок фронту такту
    s += polyline([(x + 5, y + h - 5), (x + 11, y + h - 5), (x + 11, y + h - 13)],
                  color, 1.6)
    return s


def lut(x, y, w, h, label="LUT"):
    s = rect(x, y, w, h, "#fff7ef", AMBER, 2, rx=4)
    s += text(x + w / 2, y + h / 2 + 5, label, 12.5, "#9a7a2a", "middle", "bold")
    return s


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.7.7m.1 — Дизайн = БАГАТО шляхів «тригер → логіка+маршрут → тригер».
#  Критичний шлях — найдовший із них; саме він задає мінімальний період.
#  Показуємо граф із чотирма шляхами різної затримки; max підсвічено червоним.
# ════════════════════════════════════════════════════════════════════════════
def fig_paths_graph():
    W, H = 1000, 600
    s = header(W, H)
    s += text(W / 2, 34, "Дизайн — це не один шлях, а тисячі: критичний — найдовший",
              20, INK, "middle", "bold")
    s += text(W / 2, 56,
              "Між кожною парою тригерів є свій шлях «такт → логіка + маршрут → setup»; стелю частоти задає НАЙДОВШИЙ із них",
              12.5, GREY, "middle", style="italic")

    # ліва колонка тригерів-джерел, права — приймачів
    srcx, dstx = 120, 760
    ffw, ffh = 86, 46
    ys = [120, 230, 340, 450]
    # джерела
    src_lbl = ["FF a", "FF b", "FF c", "FF d"]
    dst_lbl = ["FF p", "FF q", "FF r", "FF s"]
    for i, yy in enumerate(ys):
        s += ff(srcx, yy, ffw, ffh, src_lbl[i], INK)
        s += ff(dstx, yy, ffw, ffh, dst_lbl[i], INK)
    s += text(srcx + ffw / 2, ys[0] - 16, "тригери-джерела", 12, GREY, "middle", style="italic")
    s += text(dstx + ffw / 2, ys[0] - 16, "тригери-приймачі", 12, GREY, "middle", style="italic")

    # хмара логіки+маршруту посередині
    mx0, mx1 = srcx + ffw + 40, dstx - 40
    s += roundrect(mx0, 96, mx1 - mx0, 420, GREY, 1.4, 18, dash="4,5")
    s += text((mx0 + mx1) / 2, 116, "поле LUT + маршрутизація (§3.7.4)", 12.5, GREY, "middle", style="italic")
    # кілька LUT всередині як «вузли»
    nodes = [(360, 175), (470, 300), (560, 200), (430, 420), (620, 380), (520, 470)]
    for (nx, ny) in nodes:
        s += lut(nx - 26, ny - 16, 52, 32)

    # шляхи: список (індекс джерела, [проміжні вузли], індекс приймача, затримка, критичний?)
    paths = [
        (0, [0, 2], 0, "5.1 нс", False),
        (1, [1, 4], 1, "8.7 нс", False),
        (2, [1, 3, 5], 2, "12.4 нс", True),   # критичний
        (3, [5], 3, "6.3 нс", False),
    ]

    def src_pt(i):
        return (srcx + ffw, ys[i] + ffh / 2)

    def dst_pt(i):
        return (dstx, ys[i] + ffh / 2)

    for (si, mids, di, delay, crit) in paths:
        col = RED if crit else BLUE
        wdt = 3.4 if crit else 2
        dash = None if crit else "1,0"
        pts = [src_pt(si)]
        for m in mids:
            pts.append(nodes[m])
        pts.append(dst_pt(di))
        # лінії між точками (остання — стрілкою)
        for k in range(len(pts) - 1):
            x1, y1 = pts[k]
            x2, y2 = pts[k + 1]
            if k == len(pts) - 2:
                s += arrow(x1, y1, x2, y2, col, wdt, dash)
            else:
                s += line(x1, y1, x2, y2, col, wdt, dash)
        # підпис затримки коло приймача
        dpx, dpy = dst_pt(di)
        s += text(dpx - 10, dpy - 10 if not crit else dpy - 12, delay, 13,
                  col, "end", "bold")
        if crit:
            s += text(dpx - 10, dpy + 16, "критичний шлях", 11.5, RED, "end", "bold")

    # підсумкова рамка
    s += roundrect(335, 528, 330, 58, RED, 2.2, 12, fill="#fdeef0")
    s += text(500, 552, "T_мін = найдовший шлях", 14.5, RED, "middle", "bold")
    s += text(500, 573, "усі інші мають запас (slack) — про нього далі", 11.5, INK, "middle", style="italic")

    # бічна підказка про max
    s += text(W - 30, 150, "f_max дизайну", 13, INK, "end", "bold")
    s += text(W - 30, 168, "тримає ОДИН", 11.5, GREY, "end")
    s += text(W - 30, 184, "найповільніший шлях,", 11.5, GREY, "end")
    s += text(W - 30, 200, "хоч би скільки їх", 11.5, GREY, "end")
    s += text(W - 30, 216, "було швидких.", 11.5, GREY, "end")
    save("fig-r07-7m-1-paths-graph.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.7.7m.2 — slack = required − arrival на часовій осі одного приймача.
#  Два ендпоінти: один із додатним запасом (встигає), другий — від'ємним (зрив).
#  Найгірший (мінімальний) slack по всьому дизайну і є WNS.
# ════════════════════════════════════════════════════════════════════════════
def fig_slack_timeline():
    W, H = 1000, 560
    s = header(W, H)
    s += text(W / 2, 34, "Запас (slack) = коли треба − коли прийшло",
              20, INK, "middle", "bold")
    s += text(W / 2, 56,
              "Для кожного приймача аналізатор рахує час приходу даних і час, до якого вони МУСЯТЬ застигнути; різниця — запас",
              12.5, GREY, "middle", style="italic")

    # спільна часова шкала
    t0 = 120          # x фронту-старту (такт N)
    scale = 36        # пікселів на нс
    def TX(ns):
        return t0 + ns * scale

    T_period = 16.0   # період такту, нс
    setup = 2.0
    req = T_period - setup   # «коли треба» = фронт N+1 мінус setup

    rows = [
        # (заголовок, y, arrival_ns, колір-статус, опис)
        ("Приймач p — встигає", 150, 11.5, GREEN),
        ("Приймач r — зрив (критичний)", 350, 16.2, RED),
    ]

    for (title, y, arr, col) in rows:
        # вісь часу
        ax_y = y + 60
        s += arrow(t0 - 10, ax_y, TX(T_period) + 60, ax_y, INK, 1.8)
        s += text(TX(T_period) + 66, ax_y + 5, "час", 12, INK, "start")
        s += text(t0, y + 4, title, 14.5, col, "start", "bold")

        # фронт N (старт) і фронт N+1
        s += line(t0, ax_y - 70, t0, ax_y + 8, GREY, 1.6)
        s += text(t0, ax_y + 26, "фронт N", 11.5, GREY, "middle")
        s += line(TX(T_period), ax_y - 70, TX(T_period), ax_y + 8, GREY, 1.6)
        s += text(TX(T_period), ax_y + 26, "фронт N+1", 11.5, GREY, "middle")
        # позначка періоду
        s += arrow(t0, ax_y - 64, TX(T_period), ax_y - 64, GREY, 1.3)
        s += arrow(TX(T_period), ax_y - 64, t0, ax_y - 64, GREY, 1.3)
        s += text((t0 + TX(T_period)) / 2, ax_y - 70, f"період T = {T_period:.0f} нс",
                  11.5, GREY, "middle", style="italic")

        # «коли треба» (required) — фронт N+1 мінус setup
        rx = TX(req)
        s += line(rx, ax_y - 44, rx, ax_y + 8, AMBER, 2, "5,4")
        s += text(rx, ax_y - 50, "коли ТРЕБА", 11.5, "#9a7a2a", "middle", "bold")
        s += text(rx, ax_y + 26, f"(req = {req:.0f})", 10.5, "#9a7a2a", "middle")
        # маленький setup-клинець перед фронтом N+1
        s += rect(rx, ax_y - 8, TX(T_period) - rx, 16, "#fdeecb", AMBER, 1.2)
        s += text((rx + TX(T_period)) / 2, ax_y + 4, "su", 9.5, "#9a7a2a", "middle")

        # «коли прийшло» (arrival) — смуга t_clk→q + логіка + маршрут
        s += rect(t0, ax_y - 8, TX(arr) - t0, 16, "#eef2fb", BLUE, 1.6)
        s += text((t0 + TX(arr)) / 2, ax_y - 14, "прийшло: clk→q + логіка + маршрут",
                  10.5, BLUE, "middle")
        s += line(TX(arr), ax_y - 24, TX(arr), ax_y + 8, BLUE, 2)
        s += circle(TX(arr), ax_y, 4, BLUE, BLUE, 1)
        s += text(TX(arr), ax_y + 26, f"(arr = {arr:.1f})", 10.5, BLUE, "middle")

        # slack = req − arr
        slack = req - arr
        sx0, sx1 = (TX(arr), rx) if slack >= 0 else (rx, TX(arr))
        scol = GREEN if slack >= 0 else RED
        s += f'<rect x="{min(sx0, sx1):.1f}" y="{ax_y + 14:.1f}" width="{abs(sx1 - sx0):.1f}" height="14" fill="{scol}" opacity="0.18"/>\n'
        s += arrow(sx0, ax_y + 21, sx1, ax_y + 21, scol, 2)
        mid = (sx0 + sx1) / 2
        if slack >= 0:
            s += text(mid, ax_y + 50, f"slack = +{slack:.1f} нс  ✓", 12.5, GREEN, "middle", "bold")
        else:
            s += text(mid, ax_y + 50, f"slack = {slack:.1f} нс  ✗", 12.5, RED, "middle", "bold")

    # підсумкова рамка: формула + WNS
    s += roundrect(660, 470, 320, 76, INK, 1.8, 12)
    s += text(820, 494, "slack = required − arrival", 14.5, INK, "middle", "bold")
    s += text(820, 516, "найменший slack по ВСІХ приймачах = WNS", 11.5, RED, "middle", "bold")
    s += text(820, 534, "WNS ≥ 0 → дизайн тримає частоту", 11.5, GREEN, "middle")
    save("fig-r07-7m-2-slack-timeline.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.7.7m.3 — у FPGA шлях = затримка LUT + затримка МАРШРУТУ; маршрут
#  часто більший і змінюється від прогону до прогону розміщення/трасування.
#  Той самий RTL → різні прогони P&R → різний критичний шлях → різна f_max.
# ════════════════════════════════════════════════════════════════════════════
def fig_routing_dominates():
    W, H = 1000, 560
    s = header(W, H)
    s += text(W / 2, 34, "Чому в FPGA f_max «плаває»: маршрут важить більше за логіку",
              20, INK, "middle", "bold")
    s += text(W / 2, 56,
              "Затримка шляху = час у LUT + час у перемикачах маршруту; той самий опис після іншого розміщення дає інший критичний шлях",
              12.5, GREY, "middle", style="italic")

    # три «прогони» P&R: різний розклад LUT/маршрут → різний T → різна f_max
    runs = [
        ("Прогін A", 4.0, 8.5, "#ffffff"),   # (назва, lut_ns, route_ns)
        ("Прогін B", 4.0, 6.0, "#fafafa"),
        ("Прогін C", 4.0, 12.0, "#ffffff"),
    ]
    setup_q = 3.0   # умовно clk→q + setup, спільна «незмінна» частина

    bx = 90              # ліва межа смуг
    bw_scale = 26        # пікселів на нс
    by0 = 130
    rowh = 96
    s += text(bx, by0 - 16, "Розклад критичного шляху (нс):", 13, INK, "start", "bold")

    for i, (name, lut_ns, route_ns, bg) in enumerate(runs):
        y = by0 + i * rowh
        total = setup_q + lut_ns + route_ns
        fmax = 1000.0 / total   # МГц, бо нс
        s += text(bx - 4, y + 18, name, 13.5, INK, "start", "bold")
        # сегменти: clk→q+setup (сірий) | LUT (бурштин) | маршрут (синій)
        x = bx
        seg = [
            (setup_q, GREY, "#efefef", "clk→q+su"),
            (lut_ns, AMBER, "#fff7ef", "LUT"),
            (route_ns, BLUE, "#eef2fb", "маршрут"),
        ]
        for (val, sc, fc, lab) in seg:
            wpx = val * bw_scale
            s += rect(x, y + 26, wpx, 30, fc, sc, 2)
            if wpx > 44:
                s += text(x + wpx / 2, y + 45, lab, 11, sc, "middle", "bold")
                s += text(x + wpx / 2, y + 59 + 8, f"{val:.0f}", 10, GREY, "middle")
            x += wpx
        # підсумок праворуч
        s += line(x, y + 22, x, y + 60, INK, 1.4, "3,3")
        s += text(x + 12, y + 38, f"T = {total:.0f} нс", 13, INK, "start", "bold")
        s += text(x + 12, y + 56, f"f_max ≈ {fmax:.0f} МГц", 12.5,
                  GREEN if route_ns <= 8.5 else RED, "start", "bold")

    # вісь-лінійка часу під смугами
    ay = by0 + len(runs) * rowh + 6
    s += line(bx, ay, bx + 22 * bw_scale, ay, GREY, 1.4)
    for t in range(0, 21, 5):
        xx = bx + t * bw_scale
        s += line(xx, ay - 4, xx, ay + 4, GREY, 1.2)
        s += text(xx, ay + 18, str(t), 10.5, GREY, "middle")
    s += text(bx + 22 * bw_scale + 8, ay + 5, "нс", 11, GREY, "start")

    # рамка-висновок
    s += roundrect(70, ay + 36, W - 140, 70, GREEN, 2.2, 12, fill="#eef6ef")
    s += text(W / 2, ay + 60,
              "Той самий RTL (§3.7.5) → інше розміщення й трасування (§3.7.6) → інший критичний шлях → інша f_max.",
              13, INK, "middle", "bold")
    s += text(W / 2, ay + 84,
              "Тому реальну стелю частоти знає лише часовий аналіз ПІСЛЯ трасування, а не сам опис схеми.",
              12.5, GREEN, "middle", style="italic")
    save("fig-r07-7m-3-routing-dominates.svg", s)


if __name__ == "__main__":
    fig_paths_graph()
    fig_slack_timeline()
    fig_routing_dominates()
    print("done.")
