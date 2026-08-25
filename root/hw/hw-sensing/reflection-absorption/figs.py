# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SUN = "#caa24a"   # сонце / стороннє світло


# ── fates: чотири долі зондувального променя ──────────────────────────────────
# Ідея: один промінь, чотири різні фінали. Лише «відбився назад» годує давач;
# поглинання, наскрізь і вбік лишають приймач ні з чим.

def fig_fates():
    W, H = 720, 250
    p = []
    panels = [
        ("відбився назад", FIELD, "давач бачить", "back"),
        ("поглинувся", POS, "темне / м'яке", "absorb"),
        ("пройшов наскрізь", NEG, "прозоре", "through"),
        ("відбився вбік", SUN, "гладке під кутом", "side"),
    ]
    pw, gap = 162, 12
    x0 = (W - (pw * 4 + gap * 3)) / 2
    for i, (head, col, foot, kind) in enumerate(panels):
        px = x0 + i * (pw + gap)
        p.append(rect(px, 50, pw, 178, fill="#fbfbfb", stroke=col, sw=1.4, rx=8))
        p.append(text(px + pw / 2, 74, head, size=12, color=col, bold=True))
        cy = 150
        emit = px + 22                       # джерело променя
        wall = px + pw - 44                  # ціль
        # давач-око
        p.append(circle(emit, cy, 9, fill="#fbf2f1", stroke=INK, sw=1.5))
        p.append(arrow(emit + 9, cy, wall, cy, color=INK, sw=1.6))
        if kind == "back":
            p.append(rect(wall, cy - 24, 12, 48, fill=FILL, stroke=INK, sw=1.4, rx=0))
            p.append(arrow(wall, cy + 8, emit + 10, cy + 8, color=FIELD, sw=1.8))
        elif kind == "absorb":
            p.append(rect(wall, cy - 24, 14, 48, fill="#2a2a2a", stroke=INK, sw=1.2, rx=0))
            p.append(text(wall + 7, cy + 40, "→ тепло", size=10, color=POS, italic=True))
        elif kind == "through":
            p.append(rect(wall, cy - 24, 12, 48, fill="#dceaf5", stroke=NEG, sw=1.2, rx=0))
            p.append(arrow(wall + 12, cy, wall + 44, cy, color=NEG, sw=1.5))
        else:  # side
            p.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" '
                     'fill="#cfd6de" stroke="%s" stroke-width="1"/>'
                     % (wall, cy - 22, wall + 16, cy - 10, wall + 6, cy + 30, wall - 10, cy + 18, INK))
            p.append(arrow(wall + 4, cy, px + pw - 6, cy - 28, color=SUN, sw=1.8))
        p.append(text(px + pw / 2, 214, foot, size=10, color=col, bold=True))

    render(os.path.join(OUT, "fates.svg"), W, H, *p,
           title="Чотири долі зондувального променя")


# ── reflection-types: дзеркальне, розсіяне, зворотне ──────────────────────────
# Ідея: гладке шле в один бік (промах або зайчик), матове — навсібіч (частина
# завжди вертається), ретрорефлектор — точно назад за будь-якого кута.

def fig_reflection_types():
    W, H = 700, 260
    p = []
    cols = ["specular", "diffuse", "retro"]
    titles = ["дзеркальне", "розсіяне", "зворотне"]
    foots = ["в один бік: зайчик або промах", "навсібіч: частина завжди назад", "точно назад: будь-який кут"]
    colors = [NEG, FIELD, POS]
    pw = 224
    x0 = 14
    for i, kind in enumerate(cols):
        px = x0 + i * (pw + 6)
        p.append(rect(px, 50, pw, 196, fill="#fbfbfb", stroke=colors[i], sw=1.4, rx=8))
        p.append(text(px + pw / 2, 74, titles[i], size=12.5, color=colors[i], bold=True))
        sx, sy = px + pw / 2, 200            # точка падіння на поверхню
        surf_y = 200
        p.append(line(px + 24, surf_y, px + pw - 24, surf_y, color=INK, sw=2.2))
        # промінь, що падає (зверху-зліва)
        ix, iy = px + 40, 96
        p.append(arrow(ix, iy, sx, sy, color=INK, sw=1.7))
        if kind == "specular":
            p.append(arrow(sx, sy, px + pw - 40, 96, color=colors[i], sw=1.9))
        elif kind == "diffuse":
            for ang in (200, 230, 255, 285, 310, 340):
                rad = math.radians(ang)
                p.append(arrow(sx, sy, sx + 78 * math.cos(rad), sy + 78 * math.sin(rad),
                               color=colors[i], sw=1.4))
        else:  # retro — назад уздовж падіння
            p.append(arrow(sx, sy, ix, iy, color=colors[i], sw=1.9))
        p.append(text(px + pw / 2, 232, foots[i], size=10.5, color=colors[i], bold=True))

    render(os.path.join(OUT, "reflection-types.svg"), W, H, *p,
           title="Три типи відбиття")


# ── ir-vs-visible: колір ока ≠ відбивність давача ────────────────────────────
# Ідея: та сама поверхня дає протилежний результат у видимому й в ІЧ. «Чорне на
# око» буває яскравим в інфрачервоному — судити можна лише на робочій хвилі.

def fig_ir_vs_visible():
    W, H = 700, 250
    p = []
    bw, bh = 150, 90
    gap = 90
    y = 80
    x1 = (W - (bw * 2 + gap)) / 2
    x2 = x1 + bw + gap
    # ліва пара: видиме світло
    p.append(text(x1 + bw / 2, y - 18, "видиме світло", size=12, color=INK, bold=True))
    p.append(rect(x1, y, bw, bh, fill="#2a2a2a", stroke=INK, sw=1.5, rx=8))
    p.append(text(x1 + bw / 2, y + bh / 2 + 5, "темна на око", size=11, color="#f4f6f8", bold=True))
    # права пара: ІЧ
    p.append(text(x2 + bw / 2, y - 18, "в інфрачервоному", size=12, color=INK, bold=True))
    p.append(rect(x2, y, bw, bh, fill="#f3e6c4", stroke=SUN, sw=1.6, rx=8))
    p.append(text(x2 + bw / 2, y + bh / 2 + 5, "яскрава для ІЧ", size=11, color="#7a5f12", bold=True))
    # стрілка «та сама поверхня»
    p.append(arrow(x1 + bw, y + bh / 2, x2, y + bh / 2, color=MUTED, sw=1.8))
    p.append(text((x1 + bw + x2) / 2, y + bh / 2 - 10, "та сама поверхня", size=10, color=MUTED, italic=True))
    p.append(text(W / 2, y + bh + 48,
                  "висновок робити тільки на робочій довжині хвилі давача, а не на око",
                  size=11.5, color=POS, bold=True))

    render(os.path.join(OUT, "ir-vs-visible.svg"), W, H, *p,
           title="Колір ока ≠ відбивність давача")


# ── ir-obstacle: ІЧ-відбивач наявності ───────────────────────────────────────
# Ідея: світлодіод і фотоприймач поряд, дивляться в один бік; близька відбивна
# ціль вертає частину світла на приймач — спрацювання. Це «є/нема», не відстань.

def fig_ir_obstacle():
    W, H = 700, 250
    p = []
    led_y, pd_y = 110, 156
    sx = 90
    wall = 470
    # світлодіод
    p.append(rect(sx, led_y - 13, 30, 26, fill="#fbf2f1", stroke=POS, sw=1.6, rx=4))
    p.append(text(sx + 15, led_y + 4, "LED", size=9, color=POS, bold=True))
    # фотоприймач
    p.append(rect(sx, pd_y - 13, 30, 26, fill="#eef4fb", stroke=NEG, sw=1.6, rx=4))
    p.append(text(sx + 15, pd_y + 4, "PD", size=9, color=NEG, bold=True))
    p.append(text(sx + 15, pd_y + 34, "поряд, в один бік", size=10, color=MUTED))
    # ціль
    p.append(rect(wall, 96, 14, 80, fill=FILL, stroke=INK, sw=1.5, rx=0))
    p.append(text(wall + 7, 190, "близька ціль", size=10, color=INK))
    # промінь туди (від LED) і назад (на PD)
    p.append(arrow(sx + 30, led_y, wall, 128, color=POS, sw=1.8))
    p.append(arrow(wall, 144, sx + 30, pd_y, color=FIELD, sw=1.8))
    p.append(text((sx + wall) / 2, 104, "світить", size=10, color=POS, italic=True))
    p.append(text((sx + wall) / 2 + 10, 186, "вертає частину", size=10, color=FIELD, italic=True))
    # результат
    b, bw, bh = textbox(620, 133, "«щось є»", size=13, bold=True, color=FIELD,
                        fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(b)

    render(os.path.join(OUT, "ir-obstacle.svg"), W, H, *p,
           title="ІЧ-відбивач наявності: яскравість, а не відстань")


# ── ambient: стороннє світло й рятунок модуляцією ────────────────────────────
# Ідея: рівне сонячне ІЧ топить корисний сигнал; мерехтливий світлодіод і
# синхронний приймач лишають тільки власне «блимання».

def fig_ambient():
    W, H = 700, 290
    p = []
    # сонце
    cx, cy = 110, 78
    p.append(circle(cx, cy, 17, fill="#fdf3d6", stroke=SUN, sw=2))
    for k in range(8):
        a = math.radians(k * 45)
        p.append(line(cx + 20 * math.cos(a), cy + 20 * math.sin(a),
                      cx + 28 * math.cos(a), cy + 28 * math.sin(a), color=SUN, sw=1.6))
    p.append(text(cx, cy + 46, "сонце (рівне ІЧ)", size=10, color="#9a7a1e", bold=True))
    # приймач
    px, py = 320, 168
    p.append(rect(px, py, 30, 40, fill="#eef4fb", stroke=NEG, sw=1.6, rx=3))
    p.append(text(px + 15, py + 24, "PD", size=9, color=NEG, bold=True))
    p.append(text(px + 15, py + 58, "приймач", size=10, color=NEG, bold=True))
    # три рівні промені сонця в приймач
    for off in (-8, 0, 8):
        p.append(line(cx + 14, cy + 14, px, py + 6 + 0 * off, color=SUN, sw=1.0))
    p.append(line(cx + 14, cy + 14, px, py + 4, color=SUN, sw=1.2))
    # світлодіод, що мерехтить
    lx, ly = 120, 196
    p.append(rect(lx, ly, 24, 26, fill="#fbf2f1", stroke=POS, sw=1.6, rx=3))
    p.append(text(lx + 12, ly + 44, "ІЧ-LED (мерехтить)", size=9.5, color=POS, bold=True))
    # мерехтлива хвиля від LED до приймача
    pts = []
    x = lx + 24
    while x < px:
        t = (x - (lx + 24)) / (px - (lx + 24))
        yy = ly + 8 - 7 * math.sin((x - (lx + 24)) * 0.55)
        pts.append("%.1f,%.1f" % (x, yy))
        x += 3
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" '
             'stroke-linejoin="round"/>' % (" ".join(pts), POS))
    # панель «приймач бачить»
    bx, by, bw2, bh2 = 430, 96, 256, 160
    p.append(rect(bx, by, bw2, bh2, fill="#fbfbfb", stroke="#e4e4e4", sw=1, rx=6))
    p.append(text(bx + bw2 / 2, by + 22, "приймач бачить:", size=11, color=INK, bold=True))
    # рівне тло
    p.append(line(bx + 20, by + 56, bx + bw2 - 20, by + 56, color=SUN, sw=3))
    p.append(text(bx + bw2 / 2, by + 46, "рівне тло — відкинути", size=9.5, color="#9a7a1e"))
    # мерехтіння
    wpts = []
    x = bx + 20
    while x < bx + bw2 - 20:
        yy = by + 110 - 11 * math.sin((x - (bx + 20)) * 0.32)
        wpts.append("%.1f,%.1f" % (x, yy))
        x += 3
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" '
             'stroke-linejoin="round"/>' % (" ".join(wpts), POS))
    p.append(text(bx + bw2 / 2, by + 142, "тільки мерехтіння → корисний сигнал",
                  size=9.5, color=POS, bold=True))

    render(os.path.join(OUT, "ambient.svg"), W, H, *p,
           title="Стороннє світло заливає приймач; модуляція й віднімання тла рятують")


# ── acoustic: акустичний двійник відбивності ─────────────────────────────────
# Ідея: тверде різко відрізняється акустичним опором від повітря — добре
# відбиває звук; м'яке близьке до повітря — поглинає. «М'яке» = «чорне» для звуку.

def fig_acoustic():
    W, H = 700, 250
    p = []
    for i, (head, kind, foot, col) in enumerate([
        ("тверда щільна стіна", "hard", "великий стрибок опору → відбиває", FIELD),
        ("м'яка пориста (поролон)", "soft", "опір близький до повітря → в'язне", POS),
    ]):
        px = 20 + i * 350
        pw = 330
        p.append(rect(px, 50, pw, 196, fill="#fbfbfb", stroke=col, sw=1.4, rx=8))
        p.append(text(px + pw / 2, 74, head, size=12, color=col, bold=True))
        emit = px + 40
        wall = px + pw - 70
        cy = 150
        p.append(circle(emit, cy, 10, fill="#fbf2f1", stroke=INK, sw=1.5))
        p.append(arrow(emit + 10, cy, wall, cy, color=INK, sw=1.7))
        if kind == "hard":
            p.append(rect(wall, cy - 30, 16, 60, fill="#cfd6de", stroke=INK, sw=1.5, rx=0))
            p.append(arrow(wall, cy + 9, emit + 12, cy + 9, color=FIELD, sw=1.9))
        else:
            # пориста штрихована смуга, слабке відлуння
            p.append(rect(wall, cy - 30, 26, 60, fill="#efe3e1", stroke=POS, sw=1.4, rx=0))
            for yy in range(int(cy - 26), int(cy + 30), 8):
                p.append(line(wall + 2, yy, wall + 24, yy - 4, color=POS, sw=0.8))
            p.append(arrow(wall, cy + 9, wall - 50, cy + 9, color=POS, sw=1.3))
            p.append(text(wall - 30, cy + 30, "кволо", size=9, color=POS, italic=True))
        p.append(text(px + pw / 2, 230, foot, size=10.5, color=col, bold=True))

    render(os.path.join(OUT, "acoustic.svg"), W, H, *p,
           title="Акустичний двійник: «м'яке» для звуку — те саме, що «чорне» для світла")


# ── line-edge: відбивний контраст у ділі ─────────────────────────────────────
# Ідея: лінієвод (провал відбиття на світлій підлозі), давач краю (зникнення
# відбитку над прірвою), близькість (поява відбитку). Усі читають різницю.

def fig_line_edge():
    W, H = 700, 270
    p = []
    panels = [
        ("лінієвод", "line"),
        ("давач краю", "edge"),
        ("близькість", "prox"),
    ]
    pw = 224
    x0 = 14
    for i, (head, kind) in enumerate(panels):
        px = x0 + i * (pw + 6)
        p.append(rect(px, 50, pw, 200, fill="#fbfbfb", stroke=INK, sw=1.2, rx=8))
        p.append(text(px + pw / 2, 74, head, size=12.5, color=INK, bold=True))
        sx = px + pw / 2
        sensor_y = 120
        floor_y = 200
        # давач
        p.append(rect(sx - 16, sensor_y - 12, 32, 24, fill=FILL, stroke=INK, sw=1.4, rx=3))
        if kind == "line":
            p.append(line(px + 24, floor_y, px + pw - 24, floor_y, color="#cfd6de", sw=8))
            p.append(line(sx - 18, floor_y, sx + 18, floor_y, color="#1a1a1a", sw=8))
            p.append(arrow(sx, sensor_y + 12, sx, floor_y - 6, color=POS, sw=1.6))
            p.append(text(sx, floor_y + 22, "чорна лінія = провал", size=9.5, color=POS, bold=True))
        elif kind == "edge":
            p.append(line(px + 24, floor_y, sx, floor_y, color="#cfd6de", sw=8))
            p.append(arrow(sx, sensor_y + 12, sx + 40, floor_y + 30, color=MUTED, sw=1.4, ))
            p.append(text(sx + 20, floor_y + 24, "прірва = нема відбитку", size=9.5, color=MUTED, bold=True))
        else:
            p.append(rect(sx + 30, sensor_y - 26, 14, 52, fill=FILL, stroke=INK, sw=1.4, rx=0))
            p.append(arrow(sx + 16, sensor_y, sx + 30, sensor_y, color=POS, sw=1.6))
            p.append(arrow(sx + 30, sensor_y + 8, sx + 16, sensor_y + 8, color=FIELD, sw=1.6))
            p.append(text(sx, floor_y + 22, "перешкода = поява відбитку", size=9, color=FIELD, bold=True))
        p.append(text(px + pw / 2, 240, "читає різницю, не відстань", size=9.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "line-edge.svg"), W, H, *p,
           title="Відбивний контраст у ділі")


if __name__ == "__main__":
    fig_fates()
    fig_reflection_types()
    fig_ir_vs_visible()
    fig_ir_obstacle()
    fig_ambient()
    fig_acoustic()
    fig_line_edge()
    print("OK: figures written to", OUT)
