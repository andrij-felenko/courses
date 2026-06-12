# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для вставки ⚙️ «Одновібратор у ділі» (тема 2.12.4, Модуль 2).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; стрілки
через marker; шрифт sans-serif. Допоміжні функції скопійовано з figs.py розділів
цього модуля (єдиний вигляд). Імена SVG — унікальні (префікс fig-12-4a-…),
щоб НЕ зачіпати головний figs.py розділу.
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
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def path(d, color=INK, w=2, fill="none", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{da} '
            f'stroke-linejoin="round" stroke-linecap="round"/>\n')


def axes_t(ox, oy, ow, label):
    """Базова лінія сигналу з підписом ліворуч; повертає (рядок SVG)."""
    s = ""
    s += text(ox - 10, oy + 5, label, size=13, anchor="end", weight="bold")
    return s


# ---------------------------------------------------------------------------
# Фігура 1: три застосування одновібратора — затримка, розтяг, антидребезг
# ---------------------------------------------------------------------------
def fig_uses():
    W, H = 780, 470
    s = header(W, H)
    s += text(W / 2, 26, "Одновібратор у ділі: затримка · розтяг імпульсу · антидребезг",
              size=17, anchor="middle", weight="bold")

    x0 = 150          # старт осей по X
    xend = 740
    hi = 26           # висота "1" над базовою лінією
    pulse_h = 28      # висота вихідного імпульсу

    # ----- ряд A: ЗАТРИМКА (delay) -----
    ya = 88
    s += axes_t(x0, ya, xend - x0, "")
    s += text(x0 - 10, ya - 18, "А. Затримка", size=13, anchor="end", weight="bold", color=INK)
    # вхідний тригер (короткий спад) — позначка події
    s += line(x0, ya, xend, ya, color=FAINT, w=1)
    te = x0 + 70      # момент події
    s += line(te, ya, te, ya - hi, color=GREY, w=2)
    s += text(te, ya - hi - 6, "подія (trigger)", size=11, anchor="middle", color=GREY)
    s += line(te, ya - hi, te, ya, color=GREY, w=2)
    # вихід стає активним відразу, тримається T, дія — на ЗАДНЬОМУ фронті
    ystart = te
    yfin = te + 250
    out = [(x0, ya), (ystart, ya), (ystart, ya - pulse_h),
           (yfin, ya - pulse_h), (yfin, ya), (xend, ya)]
    s += polyline(out, color=GREEN, w=2.4)
    s += text((ystart + yfin) / 2, ya - pulse_h - 6, "T = 1.1·R·C", size=12, anchor="middle", color=GREEN)
    # стрілка задньої дії
    s += arrow(yfin, ya - pulse_h - 2, yfin + 38, ya - pulse_h - 2, color=RED, w=2)
    s += text(yfin + 42, ya - pulse_h + 2, "дія тут", size=11, color=RED, anchor="start", weight="bold")
    s += text(x0, ya + 22, "вхід ↓ запускає → вихід падає рівно через T (реле/звук «через хвилину»)",
              size=11, color=GREY, anchor="start")

    # ----- ряд B: РОЗТЯГ короткого імпульсу (pulse stretch) -----
    yb = 230
    s += text(x0 - 10, yb - 18, "Б. Розтяг", size=13, anchor="end", weight="bold", color=INK)
    s += line(x0, yb, xend, yb, color=FAINT, w=1)
    # дуже короткий вхідний імпульс
    ts = x0 + 70
    inp = [(x0, yb), (ts, yb), (ts, yb - hi), (ts + 10, yb - hi), (ts + 10, yb), (xend, yb)]
    s += polyline(inp, color=BLUE, w=2.4)
    s += text(ts + 5, yb - hi - 6, "коротка подія (мкс)", size=11, anchor="middle", color=BLUE)
    # довгий вихід
    os_ = ts
    of_ = ts + 300
    outb = [(x0, yb), (os_, yb), (os_, yb - pulse_h), (of_, yb - pulse_h), (of_, yb), (xend, yb)]
    s += polyline(outb, color=GREEN, w=2.4)
    s += text((os_ + of_) / 2, yb - pulse_h - 6, "розтягнуто до T (видно оком / встигає МК)",
              size=12, anchor="middle", color=GREEN)
    s += text(x0, yb + 22, "імпульс коротший за реакцію приймача → робимо його гарантовано довгим",
              size=11, color=GREY, anchor="start")

    # ----- ряд C: АНТИДРЕБЕЗГ (debounce) -----
    yc = 372
    s += text(x0 - 10, yc - 18, "В. Антидребезг", size=13, anchor="end", weight="bold", color=INK)
    s += line(x0, yc, xend, yc, color=FAINT, w=1)
    # дрижання контакту: серія коротких піків
    tb = x0 + 50
    bounce = [(x0, yc)]
    bx = tb
    for i in range(5):
        bounce += [(bx, yc), (bx, yc - hi), (bx + 8, yc - hi), (bx + 8, yc)]
        bx += 8 + (10 - i)            # дедалі рідші
    bounce += [(xend, yc)]
    s += polyline(bounce, color=BLUE, w=2.0)
    s += text(tb + 30, yc - hi - 6, "дребезг контакту", size=11, anchor="middle", color=BLUE)
    # один чистий вихід; T довший за дребезг → повторні фронти ігноруються (нерезапускний)
    cs = tb
    cf = tb + 300
    outc = [(x0, yc), (cs, yc), (cs, yc - pulse_h), (cf, yc - pulse_h), (cf, yc), (xend, yc)]
    s += polyline(outc, color=GREEN, w=2.4)
    s += text((cs + cf) / 2, yc - pulse_h - 6, "один чистий імпульс T (T > часу дребезгу)",
              size=12, anchor="middle", color=GREEN)
    s += text(x0, yc + 22, "перший фронт запускає; решта стрибків потрапляє в «глуху» зону T",
              size=11, color=GREY, anchor="start")

    # легенда
    s += line(150, 442, 178, 442, color=BLUE, w=2.4)
    s += text(184, 446, "вхід", size=12, color=BLUE, anchor="start")
    s += line(280, 442, 308, 442, color=GREEN, w=2.4)
    s += text(314, 446, "вихід одновібратора (OUT)", size=12, color=GREEN, anchor="start")

    return W, H, s


# ---------------------------------------------------------------------------
# Фігура 2: пастка повторного запуску — нерезапускний 555 проти resapuskного
# ---------------------------------------------------------------------------
def fig_retrigger():
    W, H = 780, 430
    s = header(W, H)
    s += text(W / 2, 26, "Пастка повторного запуску: 555 НЕ резапускний",
              size=17, anchor="middle", weight="bold")

    x0 = 60
    xend = 740
    hi = 24
    pulse_h = 26

    # ----- ряд 1: вхідні тригери (TRIG, активний рівень — НИЗЬКИЙ) -----
    y1 = 92
    s += text(x0, y1 - 30, "TRIG (вивід 2, активний — НИЗЬКИЙ рівень):", size=12, weight="bold", anchor="start")
    s += line(x0, y1 - hi, xend, y1 - hi, color=FAINT, w=1)   # рівень "1" (спокій)
    # три запуски: t1 (валідний), t2 (поки активно — ігнор), t3 (після — валідний)
    t1 = x0 + 60
    t2 = x0 + 250    # під час активного імпульсу
    t3 = x0 + 470    # після завершення
    def trig(xc, color, lbl, lblc):
        ss = ""
        ss += line(xc, y1 - hi, xc, y1, color=color, w=2)
        ss += line(xc, y1, xc + 14, y1, color=color, w=2)
        ss += line(xc + 14, y1, xc + 14, y1 - hi, color=color, w=2)
        ss += text(xc + 7, y1 + 16, lbl, size=11, anchor="middle", color=lblc)
        return ss
    # базова лінія "1"
    s += line(x0, y1 - hi, xend, y1 - hi, color=GREY, w=1, dash="3 3")
    s += text(xend, y1 - hi - 5, "1 (спокій)", size=10, color=GREY, anchor="end")
    s += trig(t1, BLUE, "t₁", BLUE)
    s += trig(t2, RED, "t₂ (рано)", RED)
    s += trig(t3, BLUE, "t₃", BLUE)

    # ----- ряд 2: вихід НЕрезапускного 555 -----
    y2 = 200
    s += text(x0, y2 - 36, "Вихід 555 (нерезапускний): t₂ ПОТРАПЛЯЄ В НІКУДИ", size=12, weight="bold", anchor="start", color=INK)
    s += line(x0, y2, xend, y2, color=FAINT, w=1)
    Ta = 150          # тривалість T (у пікселях)
    # імпульс від t1 на T; t2 всередині — ігнор; t3 → новий імпульс на T
    p1s, p1f = t1, t1 + Ta
    p3s, p3f = t3, t3 + Ta
    out555 = [(x0, y2), (p1s, y2), (p1s, y2 - pulse_h), (p1f, y2 - pulse_h), (p1f, y2),
              (p3s, y2), (p3s, y2 - pulse_h), (p3f, y2 - pulse_h), (p3f, y2), (xend, y2)]
    s += polyline(out555, color=GREEN, w=2.4)
    s += text((p1s + p1f) / 2, y2 - pulse_h - 6, "T", size=12, anchor="middle", color=GREEN)
    s += text((p3s + p3f) / 2, y2 - pulse_h - 6, "T", size=12, anchor="middle", color=GREEN)
    # позначка ігнорованого t2
    s += line(t2 + 7, y2 - pulse_h, t2 + 7, y2 + 6, color=RED, w=1.4, dash="3 3")
    s += text(t2 + 7, y2 + 20, "t₂ проігноровано", size=11, anchor="middle", color=RED, weight="bold")
    # відлік T не подовжився
    s += arrow(p1f, y2 - pulse_h - 2, p1f - 30, y2 - pulse_h - 2, color=GREY, w=1.6)
    s += text(p1f + 4, y2 - pulse_h - 4, "T від t₁ не подовжився", size=10, anchor="start", color=GREY)

    # ----- ряд 3: вихід РЕЗАПУСКНОГО одновібратора (для контрасту) -----
    y3 = 322
    s += text(x0, y3 - 36, "Для контрасту — РЕЗАПУСКНИЙ (74123-родина): t₂ ПЕРЕЗАПУСКАЄ T", size=12, weight="bold", anchor="start", color=COPP)
    s += line(x0, y3, xend, y3, color=FAINT, w=1)
    # t1 стартує; t2 (до кінця) перезапускає відлік → вихід тягнеться t2+T; t3 знову
    p1s = t1
    restart_end = t2 + Ta          # перезапуск від t2
    p3s2, p3f2 = t3, t3 + Ta
    outR = [(x0, y3), (p1s, y3), (p1s, y3 - pulse_h), (restart_end, y3 - pulse_h), (restart_end, y3),
            (p3s2, y3), (p3s2, y3 - pulse_h), (p3f2, y3 - pulse_h), (p3f2, y3), (xend, y3)]
    s += polyline(outR, color=COPP, w=2.4)
    # позначка перезапуску
    s += line(t2 + 7, y3 - pulse_h - 14, t2 + 7, y3 - pulse_h, color=COPP, w=1.4, dash="3 3")
    s += text(t2 + 7, y3 - pulse_h - 18, "t₂ перезапуск", size=11, anchor="middle", color=COPP, weight="bold")
    s += arrow(t2 + 7, y3 - pulse_h - 2, restart_end, y3 - pulse_h - 2, color=COPP, w=1.6)
    s += text(restart_end + 4, y3 - pulse_h + 2, "новий повний T", size=10, anchor="start", color=COPP)

    # підпис-висновок
    s += text(W / 2, 410,
              "Друга пастка: якщо TRIG лишити НИЗЬКИМ довше за T — вихід «застрягне» активним (RC-розрядка через вивід 7 тримає)",
              size=11.5, anchor="middle", color=RED)

    return W, H, s


def save(name, tup):
    W, H, body = tup
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name, f"({W}x{H})")


if __name__ == "__main__":
    save("fig-12-4a-1-uses.svg", fig_uses())
    save("fig-12-4a-2-retrigger.svg", fig_retrigger())
    print("done")
