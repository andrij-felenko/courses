# -*- coding: utf-8 -*-
"""Фігури до вставки comp-linear-mosfet (guide/embedded/zhyvlennia/thermal-runaway-protection).
Окремий генератор, щоб не чіпати спільний figs.py.
Запуск:  python figs_linear_mosfet.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

HOT  = POS        # гаряче, небезпека — червоне
COOL = NEG        # холодне, безпечне — синє
OK   = FIELD      # зелене виділення
WARN = "#caa24a"  # бурштин — проміжний поріг


# ── 1. Лінійна SOA: лінії тривалості пірнають під сталу потужність ────────────
def fig_fbsoa_spirito():
    """Лінійна (FB)SOA у координатах log Id — log Vds. Лінія сталої потужності —
    пряма з нахилом −1; реальні межі тривалості ПІДНИРЮЮТЬ під неї в області
    Спіріто, і що довший імпульс (аж до DC), то нижче. Вага: показати, що в
    лінійному режимі за великих Vds обмежує НЕ потужність, а теплова нестійкість —
    і саме цю просадку треба читати в даташиті, а не звичний RDS(on)-графік."""
    W, H = 860, 480
    f = [text(W / 2, 30, "Лінійна SOA: лінії тривалості пірнають під сталу потужність (область Спіріто)", size=14.5, bold=True)]

    ox, oy = 92, 360
    axw, axh = 600, 290
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw - 4, oy + 26, "напруга стік–витік Vds (log)", size=11, color=INK, anchor="end"))
    f.append('<text x="40" y="%d" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 40 %d)">струм стоку Id (log)</text>'
             % (oy - axh // 2, FONT, INK, oy - axh // 2))

    # сітка декад (умовні): Vds 1..100 В (2 декади), Id 0.1..100 А (3 декади)
    DX = axw / 2.0
    DY = axh / 3.0
    def X(d): return ox + d * DX
    def Y(d): return oy - d * DY
    for d, lab in [(0, "1"), (1, "10"), (2, "100")]:
        f.append(line(X(d), oy, X(d), oy - axh, color="#e6e9ec", sw=1))
        f.append(text(X(d), oy + 15, lab, size=9.5, color=MUTED))
    for d, lab in [(0, "0.1"), (1, "1"), (2, "10"), (3, "100")]:
        f.append(line(ox, Y(d), ox + axw, Y(d), color="#e6e9ec", sw=1))
        f.append(text(ox - 8, Y(d) + 4, lab, size=9.5, color=MUTED, anchor="end"))

    # Лінія сталої потужності P = Vds*Id → у log-log пряма з нахилом −1 (орієнтир)
    f.append(line(X(0.0), Y(2.7), X(2.0), Y(0.7), color=MUTED, sw=1.6, dash="6 5"))
    f.append(text(X(0.05), Y(2.82), "стала потужність (тепловий ліміт)", size=9.5, color=MUTED, anchor="start"))

    # Реальні межі тривалості: до зламу йдуть по лінії потужності, тоді крутіше
    # вниз; що довший імпульс — то лівіше точка зламу.
    def soa(d_break, drop, color, lab, lab_above):
        pts, dx = [], 0.0
        while dx <= 2.0:
            dy = (2.7 - dx) if dx <= d_break else (2.7 - d_break) - drop * (dx - d_break)
            if dy < 0.05:
                dy = 0.05
            pts.append((X(dx), Y(dy)))
            dx += 0.04
        path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path, color))
        bx, by = X(d_break), Y(2.7 - d_break)
        f.append(circle(bx, by, 4, fill="#fff", stroke=color, sw=1.8))
        # підпис біля точки зламу, з відступом угору-ліворуч (криві добре розведені там)
        f.append(text(bx - 8, by - lab_above, lab, size=10, color=color, anchor="end", bold=True))

    soa(1.45, 2.0, COOL, "100 мкс", 6)
    soa(1.05, 2.3, WARN, "10 мс", 6)
    soa(0.55, 2.6, HOT, "DC", 6)

    f.append(text(X(1.20), Y(0.62), "область Спіріто:", size=10, color=HOT, anchor="start", bold=True))
    f.append(text(X(1.20), Y(0.34), "теплова нестійкість, не потужність", size=9.5, color=HOT, anchor="start"))

    f.append(fitbox(ox, oy + 40, axw, 60,
                    "Як ключ MOSFET живе по лінії сталої потужності.\n"
                    "Як лінійний елемент за великих Vds його тримає теплова нестійкість: реальні криві тривалості\n"
                    "пірнають під сталу потужність, і що довший імпульс (до DC), то нижче.\n"
                    "У даташиті це окремий графік «linear-mode SOA», а не звичний RDS(on)-режим.",
                    size=9.5, fill="#fdecea", stroke=HOT, sw=1.3))
    render(os.path.join(IMG, "fbsoa-spirito.svg"), W, H, *f)


# ── 2. Спіріто зблизька: фокусування струму в одну гарячу комірку ─────────────
def fig_hot_spot_focusing():
    """Чому гине ОДИН прилад, хоч «у середньому» крива виглядає безпечно: кристал
    не ізотермічний. Трохи гарячіша комірка (нижче ZTC) бере більший струм → ще
    гарячіша → стягує струм у вузький гарячий канал. Вага: пояснити Спіріто як
    фокусування струму ВСЕРЕДИНІ кристала, а не глобальну петлю на весь чип."""
    W, H = 860, 360
    f = [text(W / 2, 30, "Спіріто зблизька: струм фокусується в одну гарячу комірку кристала", size=15, bold=True)]

    n = 11
    cx0, cy0 = 122, 108
    cw, ch, gap = 52, 86, 6
    hot_i = 5
    for i in range(n):
        x = cx0 + i * (cw + gap)
        dist = abs(i - hot_i)
        if dist == 0:
            col, fop = HOT, 0.85
        elif dist == 1:
            col, fop = HOT, 0.42
        elif dist == 2:
            col, fop = WARN, 0.34
        else:
            col, fop = COOL, 0.16
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s" '
                 'fill-opacity="%.2f" stroke="%s" stroke-width="1.3"/>'
                 % (x, cy0, cw, ch, col, fop, LINE))
        sw = 1.0 + (5.0 if dist == 0 else 2.4 if dist == 1 else 1.3 if dist == 2 else 0.5)
        f.append(arrow(x + cw / 2, cy0 - 6, x + cw / 2, cy0 - 34, color=col, sw=sw))
    f.append(text(cx0 + n * (cw + gap) / 2 - gap / 2, cy0 + ch + 24,
                  "комірки одного кристала (спільні затвор і витік)", size=10.5, color=INK))
    f.append(text(cx0 + hot_i * (cw + gap) + cw / 2, cy0 - 44,
                  "сюди стікається струм", size=9.5, color=HOT, bold=True))

    loop_y = 292
    steps = ["комірка трохи гарячіша", "нижче ZTC → більший струм",
             "більше тепла саме тут", "ще гарячіша"]
    bx0 = 64
    span = 198
    for k, s in enumerate(steps):
        cx = bx0 + 86 + k * span
        box, w, h = textbox(cx, loop_y, s, size=9.5, fill="#fff", stroke=HOT, sw=1.4, min_w=150)
        f.append(box)
        if k < len(steps) - 1:
            f.append(arrow(cx + w / 2 + 3, loop_y, cx + span - w / 2 - 3, loop_y, color=HOT, sw=1.6))
    f.append(text(W / 2, loop_y + 34, "петля замикається на ОДНІЙ комірці — глобальна «середня» крива тут не рятує", size=9.5, color=HOT, bold=True))
    render(os.path.join(IMG, "hot-spot-focusing.svg"), W, H, *f)


# ── 3. Лінійний режим паралельно: без баластів і з баластами ──────────────────
def fig_parallel_ballast_linear():
    """Кілька MOSFET у лінійному режимі паралельно: спільний затвор → «жадібний»
    стягує струм. Лік — витоковий баласт КОЖНОМУ: узяв більше струму, дістав
    більше падіння на своєму баласті, прикрив свій Vgs, віддав надлишок. Вага:
    у лінійному режимі (нижче ZTC) самобалансу немає, баласт обов'язковий —
    на відміну від ключового режиму, де додатний tempco RDS(on) вирівнює сам."""
    W, H = 860, 390
    f = [text(W / 2, 28, "Лінійний режим паралельно: без баластів один стягує струм, з баластами — ділять", size=14, bold=True)]

    def fet(x, gate_y, col):
        # стік угору
        f.append(line(x, gate_y + 6, x, gate_y + 20, color=col, sw=1.6))
        # тіло
        f.append(rect(x - 22, gate_y + 20, 44, 38, fill=FILL, stroke=col, sw=2.0))
        f.append(text(x, gate_y + 44, "Q", size=13, color=col, bold=True))
        # під'єднання до шини затвора
        f.append(circle(x, gate_y, 3.5, fill=INK, stroke=INK, sw=1))
        f.append(line(x, gate_y, x, gate_y + 20, color=INK, sw=1.3))
        return gate_y + 58   # y витоку

    offs = [-92, 0, 92]
    gate_y = 86

    # ── ліва панель: БЕЗ баластів ──
    lx = 200
    f.append(text(lx, 60, "без баластів", size=12, bold=True, color=HOT))
    f.append(line(lx - 120, gate_y, lx + 120, gate_y, color=INK, sw=1.6))
    f.append(text(lx - 126, gate_y + 4, "Vgs", size=10, color=INK, anchor="end"))
    yv = gate_y + 58
    for off in offs:
        fet(lx + off, gate_y, HOT)
    f.append(line(lx + offs[0], yv, lx + offs[-1], yv, color=INK, sw=1.6))
    f.append(line(lx, yv, lx, yv + 16, color=INK, sw=1.6))
    f.append(text(lx, yv + 30, "спільний витік", size=9.5, color=MUTED))
    for off, sw in [(-92, 0.6), (0, 5.2), (92, 0.8)]:
        f.append(arrow(lx + off, gate_y + 18, lx + off, gate_y + 6, color=HOT, sw=sw))
    f.append(text(lx, yv + 50, "один «жадібний» бере майже все →", size=9, color=HOT, anchor="middle"))
    f.append(text(lx, yv + 64, "гріється → бере ще більше → гине", size=9, color=HOT, anchor="middle"))

    # ── права панель: З баластами ──
    rx = 650
    f.append(text(rx, 60, "з витоковими баластами", size=12, bold=True, color=OK))
    f.append(line(rx - 120, gate_y, rx + 120, gate_y, color=INK, sw=1.6))
    f.append(text(rx - 126, gate_y + 4, "Vgs", size=10, color=INK, anchor="end"))
    yv = gate_y + 58
    for off in offs:
        fet(rx + off, gate_y, OK)
        f.append(rect(rx + off - 9, yv, 18, 26, fill="#eafaf0", stroke=OK, sw=1.6))
        f.append(text(rx + off, yv + 17, "Rs", size=9, color=OK, bold=True))
    by = yv + 26
    f.append(line(rx + offs[0], by + 8, rx + offs[-1], by + 8, color=INK, sw=1.6))
    for off in offs:
        f.append(line(rx + off, by, rx + off, by + 8, color=INK, sw=1.4))
    f.append(line(rx, by + 8, rx, by + 22, color=INK, sw=1.6))
    f.append(text(rx, by + 36, "спільний витік", size=9.5, color=MUTED))
    for off in offs:
        f.append(arrow(rx + off, gate_y + 18, rx + off, gate_y + 6, color=OK, sw=2.6))
    f.append(text(rx, by + 56, "взяв більше → більше падіння на своєму Rs →", size=9, color=OK, anchor="middle"))
    f.append(text(rx, by + 70, "прикрив Vgs → віддав надлишок сусідам", size=9, color=OK, anchor="middle"))

    f.append(fitbox(70, 326, W - 140, 50,
                    "У ключовому режимі додатний tempco RDS(on) сам вирівнює паралельні прилади.\n"
                    "У ЛІНІЙНОМУ (нижче ZTC) самобалансу немає — витоковий баласт кожному обов'язковий,\n"
                    "інакше один прилад стягне струм і згорить, потягнувши за собою решту.",
                    size=9.5, fill="#eafaf0", stroke=OK, sw=1.3))
    render(os.path.join(IMG, "parallel-ballast-linear.svg"), W, H, *f)


if __name__ == "__main__":
    fig_fbsoa_spirito()
    fig_hot_spot_focusing()
    fig_parallel_ballast_linear()
    print("OK: 3 figures ->", IMG)
