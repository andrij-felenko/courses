# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки 2.8.5m
«ОП і ємнісне навантаження: чому буфер дзвонить на довгому кабелі».
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
fig-13-5m-*. Головний figs.py розділу НЕ чіпаємо.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; зелене — поле/корисне;
стрілки через marker; шрифт sans-serif.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
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
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def plus(cx, cy, r=11, color=RED, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


def minus(cx, cy, r=11, color=BLUE, w=2.5):
    return circle(cx, cy, r, "none", color, w) + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def _cap_v(cx, cy, gap=6, plate=13, col=INK):
    """Вертикальний конденсатор (дві горизонтальні пластини, виводи вгору-вниз)."""
    return (line(cx - plate, cy - gap, cx + plate, cy - gap, col, 2.4)
            + line(cx - plate, cy + gap, cx + plate, cy + gap, col, 2.4))


def _res_h(x0, cy, length, col=INK, w=2):
    """Горизонтальний резистор зиґзаґом."""
    n = 6
    seg = length / (n + 1)
    pts = [(x0, cy)]
    x = x0 + seg
    up = True
    for i in range(n):
        pts.append((x, cy - 9 if up else cy + 9))
        up = not up
        x += seg
    pts.append((x0 + length, cy))
    return _poly(pts, col, w)


def _opamp(cx, cy, scale=1.0, plus_top=False):
    """Трикутник ОП. Повертає (svg, l_top, l_bot, l_out) — координати виводів."""
    w = 56 * scale
    h = 64 * scale
    p1 = (cx - w / 2, cy - h / 2)
    p2 = (cx - w / 2, cy + h / 2)
    p3 = (cx + w / 2, cy)
    s = f'<path d="M {p1[0]:.1f},{p1[1]:.1f} L {p2[0]:.1f},{p2[1]:.1f} L {p3[0]:.1f},{p3[1]:.1f} Z" fill="#fbfbf7" stroke="{INK}" stroke-width="2"/>\n'
    top = (cx - w / 2, cy - h / 4)
    bot = (cx - w / 2, cy + h / 4)
    out = (cx + w / 2, cy)
    # знаки входів
    if plus_top:
        s += text(top[0] + 12, top[1] + 5, "+", 17, RED, "middle", "bold")
        s += text(bot[0] + 12, bot[1] + 5, "−", 17, BLUE, "middle", "bold")
    else:
        s += text(top[0] + 12, top[1] + 5, "−", 17, BLUE, "middle", "bold")
        s += text(bot[0] + 12, bot[1] + 5, "+", 17, RED, "middle", "bold")
    return s, top, bot, out


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.8.5m.1 — звідки береться зайвий полюс: Rout буфера × C кабелю
# ─────────────────────────────────────────────────────────────────────────────
def fig1():
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 26, "Прихований RC: вихідний опір буфера × ємність кабелю", 16, INK, "middle", "bold")

    # буфер (повторювач): вихід прямо на «−»
    op, top, bot, out = _opamp(150, 150, 1.0, plus_top=True)
    s += op
    # сигнал на «+» (верхній вхід)
    s += line(80, top[1], top[0], top[1], INK, 2)
    s += text(76, top[1] - 8, "Vin", 14, INK, "end", "bold")
    # зворотний зв'язок: вихід прямо на «−»
    s += line(out[0], out[1], out[0] + 18, out[1], INK, 2)
    s += line(out[0] + 18, out[1], out[0] + 18, bot[1] - 34, INK, 2)
    s += line(out[0] + 18, bot[1] - 34, bot[0] - 22, bot[1] - 34, INK, 2)
    s += line(bot[0] - 22, bot[1] - 34, bot[0] - 22, bot[1], INK, 2)
    s += line(bot[0] - 22, bot[1], bot[0], bot[1], INK, 2)
    s += text(150, 250, "буфер ×1", 13, INK, "middle", "bold")

    # вузол виходу ОП (внутрішній)
    nx = out[0] + 18
    s += circle(nx, out[1], 3.2, INK, INK, 1)

    # Rout як ЯВНИЙ послідовний резистор (модель вихідного опору)
    rx0 = nx + 14
    rlen = 86
    s += _res_h(rx0, out[1], rlen, RED, 2.4)
    s += text(rx0 + rlen / 2, out[1] - 16, "Rout", 14, RED, "middle", "bold")
    s += text(rx0 + rlen / 2, out[1] - 32, "(десятки Ω)", 11, RED, "middle")

    # довгий кабель — як штрихова «лінія передачі»
    kx0 = rx0 + rlen
    kx1 = 560
    s += line(kx0, out[1], kx1, out[1], INK, 2)
    s += text((kx0 + kx1) / 2, out[1] - 14, "довгий кабель", 12, INK, "middle")
    # хвиляста підкладка кабелю
    pts = []
    for j in range(0, int(kx1 - kx0) + 1, 4):
        pts.append((kx0 + j, out[1] + 14 + 3 * math.sin(j / 9.0)))
    s += _poly(pts, GREY, 1.4)

    # ємність кабелю на землю — Cload
    s += line(kx1, out[1], kx1, out[1] + 30, INK, 2)
    s += _cap_v(kx1, out[1] + 36, 6, 14, GREEN)
    s += line(kx1, out[1] + 42, kx1, out[1] + 58, INK, 2)
    # земля
    s += line(kx1 - 16, out[1] + 58, kx1 + 16, out[1] + 58, INK, 2.4)
    s += line(kx1 - 10, out[1] + 63, kx1 + 10, out[1] + 63, INK, 2)
    s += line(kx1 - 5, out[1] + 68, kx1 + 5, out[1] + 68, INK, 2)
    s += text(kx1 + 22, out[1] + 40, "Cload", 14, GREEN, "start", "bold")
    s += text(kx1 + 22, out[1] + 56, "(сотні пФ –", 11, GREEN, "start")
    s += text(kx1 + 22, out[1] + 70, " нФ)", 11, GREEN, "start")

    # рамка-висновок: Rout + Cload = зайвий полюс
    bx, by, bw, bh = 70, 286, 580, 56
    s += rect(bx, by, bw, bh, LBLUE, "#c9d3dc", 1.4, 8)
    s += text(bx + 14, by + 23, "Rout × Cload  =  зайвий полюс (затримка фази) усередині петлі", 14, INK, "start", "bold")
    s += text(bx + 14, by + 43, "f_p = 1 / (2π · Rout · Cload)   →   на цій частоті фаза провисає, запас тане", 13, INK, "start")

    save("fig-13-5m-1-hidden-pole.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.8.5m.2 — наслідок: запас фази тане → дзвін / самозбудження
# ─────────────────────────────────────────────────────────────────────────────
def _step_resp(ox, oy, w, h, zeta, col, n=240, cycles=3.4):
    """Перехідна крива на одиничну сходинку для 2-го порядку (нормований час)."""
    pts = []
    wn = 2 * math.pi * cycles / w  # умовна кутова на ширину
    for j in range(n + 1):
        x = w * j / n
        t = x
        if zeta < 1.0:
            wd = wn * math.sqrt(1 - zeta * zeta)
            env = math.exp(-zeta * wn * t)
            y = 1 - env * (math.cos(wd * t) + (zeta * wn / wd) * math.sin(wd * t))
        else:
            y = 1 - math.exp(-wn * t) * (1 + wn * t)
        pts.append((ox + x, oy - h * y))
    return _poly(pts, col, 2.6)


def fig2():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 26, "Той самий буфер: чим важча ємність, тим сильніший дзвін", 16, INK, "middle", "bold")

    ox, oy = 70, 252
    w, h = 560, 92
    # осі (з запасом угору на перестрибування)
    s += arrow(ox, oy, ox, oy - h - 96, INK, 2)
    s += arrow(ox, oy, ox + w + 14, oy, INK, 2)
    s += text(ox + w + 16, oy + 5, "час", 12, INK, "start", "bold")
    s += text(ox - 8, oy - h - 102, "Vout", 12, INK, "middle", "bold")

    # рівень заданої напруги (ціль)
    s += line(ox, oy - h * 1.0, ox + w, oy - h * 1.0, GREY, 1.6, "5 5")
    s += text(ox + w + 4, oy - h * 1.0 + 4, "ціль", 11, GREY, "start")
    # рівень 0
    s += line(ox, oy, ox + w, oy, FAINT, 1.4)

    # вхідна сходинка
    s += _poly([(ox, oy), (ox + 30, oy), (ox + 30, oy - h * 1.0), (ox + w, oy - h * 1.0)], INK, 1.8, "4 4")
    s += text(ox + 34, oy - h * 1.0 - 6, "вхід (сходинка)", 11, INK, "start")

    # три відгуки: чиста (мала C), дзвін (середня), на межі зриву (велика)
    s += _step_resp(ox + 30, oy, w - 30, h, 0.9, GREEN, cycles=2.6)
    s += _step_resp(ox + 30, oy, w - 30, h, 0.30, "#d98a1f", cycles=3.4)
    s += _step_resp(ox + 30, oy, w - 30, h, 0.10, RED, cycles=4.2)

    # легенда
    lx, ly = ox + w - 200, oy - h - 92
    s += rect(lx, ly, 200, 60, "#ffffff", "#c9d3dc", 1.2, 6)
    s += line(lx + 10, ly + 16, lx + 34, ly + 16, GREEN, 2.6)
    s += text(lx + 40, ly + 20, "мала C: чисто, з запасом", 11, INK, "start")
    s += line(lx + 10, ly + 34, lx + 34, ly + 34, "#d98a1f", 2.6)
    s += text(lx + 40, ly + 38, "більша C: дзвін (overshoot)", 11, INK, "start")
    s += line(lx + 10, ly + 52, lx + 34, ly + 52, RED, 2.6)
    s += text(lx + 40, ly + 56, "велика C: на межі зриву", 11, INK, "start")

    # підпис «overshoot»
    s += text(ox + 120, oy - h * 1.62, "перестрибування", 11, "#d98a1f", "middle", "bold")
    s += text(W / 2, H - 8, "Зайвий полюс з'їдає запас фази → вихід уже не приходить плавно, а коливається; за малого запасу — самозбудження.",
              11.5, INK, "middle")

    save("fig-13-5m-2-ringing.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.8.5m.3 — лік: послідовний резистор Riso поза петлею
# ─────────────────────────────────────────────────────────────────────────────
def fig3():
    W, H = 720, 340
    s = header(W, H)
    s += text(W / 2, 26, "Лік: маленький Riso між виходом і кабелем — поза петлею", 16, INK, "middle", "bold")

    op, top, bot, out = _opamp(140, 150, 1.0, plus_top=True)
    s += op
    s += line(74, top[1], top[0], top[1], INK, 2)
    s += text(70, top[1] - 8, "Vin", 14, INK, "end", "bold")
    s += text(140, 250, "буфер ×1", 13, INK, "middle", "bold")

    # вузол виходу ОП
    nx = out[0] + 16
    s += line(out[0], out[1], nx, out[1], INK, 2)
    s += circle(nx, out[1], 3.2, INK, INK, 1)

    # зворотний зв'язок беремо ДО Riso (із самого виходу ОП) — петля бачить лише вихід
    s += line(nx, out[1], nx, bot[1] - 40, GREEN, 2.2)
    s += line(nx, bot[1] - 40, bot[0] - 26, bot[1] - 40, GREEN, 2.2)
    s += line(bot[0] - 26, bot[1] - 40, bot[0] - 26, bot[1], GREEN, 2.2)
    s += line(bot[0] - 26, bot[1], bot[0], bot[1], GREEN, 2.2)
    s += text(nx + 6, bot[1] - 46, "ЗЗ — до Riso", 11, GREEN, "start", "bold")

    # Riso послідовно
    rx0 = nx + 8
    rlen = 70
    s += _res_h(rx0, out[1], rlen, RED, 2.4)
    s += text(rx0 + rlen / 2, out[1] - 16, "Riso", 14, RED, "middle", "bold")
    s += text(rx0 + rlen / 2, out[1] - 32, "~10–50 Ω", 11, RED, "middle")

    # кабель + Cload
    kx0 = rx0 + rlen
    kx1 = 540
    s += line(kx0, out[1], kx1, out[1], INK, 2)
    s += circle(kx1, out[1], 3.2, INK, INK, 1)
    s += text((kx0 + kx1) / 2, out[1] - 12, "кабель", 12, INK, "middle")
    s += line(kx1, out[1], kx1, out[1] + 28, INK, 2)
    s += _cap_v(kx1, out[1] + 34, 6, 14, GREEN)
    s += line(kx1, out[1] + 40, kx1, out[1] + 56, INK, 2)
    s += line(kx1 - 16, out[1] + 56, kx1 + 16, out[1] + 56, INK, 2.4)
    s += line(kx1 - 10, out[1] + 61, kx1 + 10, out[1] + 61, INK, 2)
    s += line(kx1 - 5, out[1] + 66, kx1 + 5, out[1] + 66, INK, 2)
    s += text(kx1 + 22, out[1] + 40, "Cload", 14, GREEN, "start", "bold")

    # вихід «до навантаження» далі
    s += arrow(kx1, out[1], kx1 + 70, out[1], INK, 2)
    s += text(kx1 + 74, out[1] + 4, "до навантаження", 11, INK, "start")

    # дві рамки-висновки
    s += rect(60, 268, 300, 60, LGRN, "#cfe0d0", 1.4, 8)
    s += text(72, 290, "Riso ізолює C від виходу ОП:", 12.5, INK, "start", "bold")
    s += text(72, 308, "полюс іде назовні петлі — запас фази", 11.5, INK, "start")
    s += text(72, 322, "повертається, дзвін гасне.", 11.5, INK, "start")

    s += rect(380, 268, 280, 60, LRED, "#e7cccc", 1.4, 8)
    s += text(392, 290, "Ціна: на Riso падає трохи напруги", 12, INK, "start", "bold")
    s += text(392, 308, "під струмом → точність на самому", 11.5, INK, "start")
    s += text(392, 322, "навантаженні трохи гірша.", 11.5, INK, "start")

    save("fig-13-5m-3-iso-resistor.svg", s)


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
    print("done: 2.8.5m figures")
