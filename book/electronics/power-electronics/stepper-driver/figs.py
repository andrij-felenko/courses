# -*- coding: utf-8 -*-
"""Фігури до статті «Драйвер крокового». Чистий Python, вивід — ./img/*.svg."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def sw_box(cx, cy, on=False):
    """Ключ-квадратик: зелений відкритий (on), сірий закритий."""
    r = 13
    col = FIELD if on else MUTED
    fill = "#e8f7ee" if on else "#f0f1f3"
    out = rect(cx - r, cy - r, 2 * r, 2 * r, fill=fill, stroke=col, sw=2, rx=4)
    if on:
        out += line(cx - 6, cy, cx + 6, cy, color=col, sw=2.5)  # замкнено
    else:
        out += line(cx - 6, cy - 6, cx + 6, cy + 6, color=col, sw=2.2)  # розімкнено
    return out


def h_bridge(x, y, w, h, label, diag="left"):
    """Один H-міст: 4 ключі навколо обмотки, підписаний label.
    diag='left' → відкрита діагональ Q1(TL)+Q4(BR); 'right' → Q2(TR)+Q3(BL)."""
    out = rect(x, y, w, h, fill=BG, stroke=MUTED, sw=1.4, rx=8)
    top = y + 30
    bot = y + h - 30
    lx = x + 34
    rx = x + w - 34
    # шини живлення
    out += line(x + 16, top, x + w - 16, top, color=POS, sw=2)
    out += line(x + 16, bot, x + w - 16, bot, color=NEG, sw=2)
    out += text(x + w - 14, top - 6, "V+", size=12, color=POS, anchor="end", bold=True)
    out += text(x + w - 14, bot + 16, "GND", size=12, color=NEG, anchor="end", bold=True)
    tl = diag == "left"
    tr = diag == "right"
    bl = diag == "right"
    br = diag == "left"
    # верхні ключі
    out += sw_box(lx, top + 26, on=tl)
    out += sw_box(rx, top + 26, on=tr)
    out += line(lx, top, lx, top + 13, color=LINE, sw=1.4)
    out += line(rx, top, rx, top + 13, color=LINE, sw=1.4)
    # нижні ключі
    out += sw_box(lx, bot - 26, on=bl)
    out += sw_box(rx, bot - 26, on=br)
    out += line(lx, bot - 13, lx, bot, color=LINE, sw=1.4)
    out += line(rx, bot - 13, rx, bot, color=LINE, sw=1.4)
    # обмотка (перекладина H) — котушка
    my = (top + bot) / 2
    out += line(lx, top + 39, lx, my, color=LINE, sw=1.4)
    out += line(rx, top + 39, rx, my, color=LINE, sw=1.4)
    out += line(lx, bot - 39, lx, my + 0, color=LINE, sw=1.4)
    out += line(rx, bot - 39, rx, my, color=LINE, sw=1.4)
    # символ котушки — три горбики
    cxs = (lx + rx) / 2
    out += line(lx, my, cxs - 24, my, color=LINE, sw=1.4)
    out += line(cxs + 24, my, rx, my, color=LINE, sw=1.4)
    hb = ""
    for i in range(3):
        bx = cxs - 18 + i * 18
        hb += ('<path d="M%.1f %.1f q 9 -13 18 0" fill="none" stroke="%s" stroke-width="1.6"/>'
               % (bx - 9, my, LINE))
    out += hb
    out += text(cxs, my + 22, label, size=13, color=INK, anchor="middle", bold=True)
    # стрілка напрямку струму крізь обмотку
    if tl:  # струм: V+ → TL → обмотка зліва-направо → BR → GND
        out += arrow(cxs - 26, my - 9, cxs + 26, my - 9, color=POS, sw=2)
    else:
        out += arrow(cxs + 26, my - 9, cxs - 26, my - 9, color=POS, sw=2)
    return out


# ── Фігура 1: два H-мости на дві обмотки ────────────────────────────────────
def fig_two_bridges():
    W, H = 720, 400
    frags = []
    bw, bh = 300, 250
    y0 = 78
    frags.append(h_bridge(40, y0, bw, bh, "Обмотка A (фаза A)", diag="left"))
    frags.append(h_bridge(380, y0, bw, bh, "Обмотка B (фаза B)", diag="right"))
    # підписи-пояснення під мостами
    frags.append(fitbox(40, y0 + bh + 16, bw, 48,
                        "H-міст фази A: діагональ задає\nзнак струму в обмотці A",
                        size=12, fill="#fdf0ee", stroke=POS))
    frags.append(fitbox(380, y0 + bh + 16, bw, 48,
                        "H-міст фази B: другий незалежний\nміст на другу обмотку",
                        size=12, fill="#eef1fd", stroke=NEG))
    render(os.path.join(IMG, 'two-bridges.svg'), W, H, *frags,
           title="Драйвер біполярного кроковика — два H-мости")


# ── Фігура 2: петля чоппера + пилчастий струм ───────────────────────────────
def fig_chopper():
    W, H = 720, 380
    frags = []
    # ліва частина: петля
    # обмотка + міст (спрощено як блок)
    frags.append(fitbox(50, 70, 150, 60, "H-міст\n+ обмотка", size=13,
                        fill="#f4f6f8", stroke=LINE, bold=True))
    # резистор-давач
    frags.append(fitbox(50, 200, 150, 56, "R_sense\n(давач струму)", size=12,
                        fill="#eef6ef", stroke=FIELD, bold=True))
    frags.append(line(125, 130, 125, 200, color=LINE, sw=1.8))  # струм униз крізь давач
    frags.append(text(140, 170, "I фази", size=12, color=INK, anchor="start"))
    # компаратор (трикутник)
    ctx, cty = 300, 150
    tri = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="#eef1fd" stroke="%s" stroke-width="1.8"/>'
           % (ctx, cty - 30, ctx + 58, cty, ctx, cty + 30, NEG))
    frags.append(tri)
    frags.append(text(ctx + 20, cty + 5, "≥", size=20, color=NEG, anchor="middle", bold=True))
    frags.append(text(ctx + 24, cty - 44, "компаратор", size=12, color=INK, anchor="middle"))
    # входи компаратора
    frags.append(line(200, 228, ctx, cty + 14, color=LINE, sw=1.6))  # U_sense
    frags.append(text(214, 244, "U = I·R", size=11, color=FIELD, anchor="start", bold=True))
    frags.append(line(214, cty - 14, ctx, cty - 14, color=LINE, sw=1.6))  # U_опорна
    frags.append(text(150, cty - 18, "U_опорна", size=11, color=POS, anchor="middle", bold=True))
    frags.append(line(150, cty - 8, 150, cty - 14, color=POS, sw=1.6))
    # вихід компаратора → вимикання моста
    frags.append(arrow(ctx + 58, cty, 400, cty, color=INK, sw=1.8))
    frags.append(arrow(400, cty, 400, 100, color=INK, sw=1.8))
    frags.append(arrow(400, 100, 200, 100, color=INK, sw=1.8))
    frags.append(fitbox(300, 78, 150, 44, "дорос струм —\nвимкнути ключі", size=11,
                        fill="#fdf0ee", stroke=POS))
    # права частина: пилчастий струм
    gx, gy, gw, gh = 470, 90, 210, 200
    frags.append(rect(gx, gy, gw, gh, fill=BG, stroke=MUTED, sw=1.4, rx=6))
    frags.append(line(gx, gy + gh, gx + gw, gy + gh, color=LINE, sw=1.4))  # вісь t
    frags.append(line(gx, gy, gx, gy + gh, color=LINE, sw=1.4))            # вісь I
    frags.append(text(gx + gw - 6, gy + gh + 16, "час", size=11, color=MUTED, anchor="end"))
    frags.append(text(gx + 6, gy + 12, "I", size=12, color=INK, anchor="start", bold=True))
    # заданий рівень
    lvl = gy + 60
    frags.append(line(gx, lvl, gx + gw, lvl, color=POS, sw=1.6, dash="6 4"))
    frags.append(text(gx + gw - 4, lvl - 6, "заданий струм", size=10.5, color=POS, anchor="end", bold=True))
    # пилка навколо рівня: наростання від 0, тоді дрібний зубець
    pts = []
    x = gx
    y = gy + gh
    pts.append((x, y))
    # наростання до рівня
    xr = gx + 70
    pts.append((xr, lvl))
    # пилка
    step = 18
    up = True
    xx = xr
    while xx < gx + gw - 6:
        xx2 = min(xx + step, gx + gw - 6)
        yy = lvl + (7 if up else -7)
        pts.append((xx2, yy))
        up = not up
        xx = xx2
    path = "M" + " L".join("%.1f %.1f" % p for p in pts)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (path, FIELD))
    frags.append(fitbox(gx, gy + gh + 26, gw, 40,
                        "струм «пиляє» коло заданого —\nне залежить від напруги живлення",
                        size=10.5, fill="#eef6ef", stroke=FIELD))
    render(os.path.join(IMG, 'chopper-loop.svg'), W, H, *frags,
           title="Чоппер: петля тримає струм обмотки рівним")


# ── Фігура 3: синус/косинус фаз + вектор мікрокроку ─────────────────────────
def fig_microstep():
    W, H = 720, 470
    frags = []
    # верх: два зсунуті сигнали
    gx, gy, gw, gh = 60, 70, 600, 120
    midy = gy + gh / 2
    frags.append(line(gx, midy, gx + gw, midy, color=MUTED, sw=1.2))  # нуль
    frags.append(line(gx, gy, gx, gy + gh, color=LINE, sw=1.2))
    frags.append(text(gx - 8, gy + 10, "I", size=12, color=INK, anchor="end", bold=True))
    frags.append(text(gx + gw, midy - 6, "крок", size=11, color=MUTED, anchor="end"))
    A = gh / 2 - 8
    # синус A, косинус B — і точки-мікрокроки
    def curve(fn, col):
        pts = []
        for i in range(0, 121):
            t = i / 120.0 * 2 * math.pi
            xx = gx + i / 120.0 * gw
            yy = midy - fn(t) * A
            pts.append((xx, yy))
        return '<path d="M%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (
            " L".join("%.1f %.1f" % p for p in pts), col)
    frags.append(curve(math.sin, POS))
    frags.append(curve(math.cos, NEG))
    frags.append(text(gx + gw + 4, midy - A - 2, "I_A = sin", size=12, color=POS, anchor="start", bold=True))
    frags.append(text(gx + gw + 4, midy + 14, "I_B = cos", size=12, color=NEG, anchor="start", bold=True))
    # позначки-мікрокроки (дискретні рівні) на синусі
    for k in range(0, 17):
        t = k / 16.0 * 2 * math.pi
        xx = gx + k / 16.0 * gw
        yy = midy - math.sin(t) * A
        frags.append(circle(xx, yy, 2.6, fill=POS, stroke=POS, sw=1))
    frags.append(fitbox(gx, gy + gh + 12, gw, 30,
                        "драйвер задає струмам дискретні рівні синуса/косинуса — кожен набір рівнів = один мікрокрок",
                        size=11, fill="#f4f6f8", stroke=MUTED))
    # низ: вектор поля
    ccx, ccy, R = 200, 330, 62
    frags.append(circle(ccx, ccy, R, fill=BG, stroke=MUTED, sw=1.4))
    frags.append(line(ccx - R - 10, ccy, ccx + R + 10, ccy, color=MUTED, sw=1))  # осі
    frags.append(line(ccx, ccy - R - 10, ccx, ccy + R + 10, color=MUTED, sw=1))
    frags.append(text(ccx + R + 14, ccy + 4, "A", size=12, color=POS, anchor="start", bold=True))
    frags.append(text(ccx - 4, ccy - R - 14, "B", size=12, color=NEG, anchor="end", bold=True))
    # кілька векторів різного кута
    for ang, col, sw in [(20, MUTED, 1.6), (45, MUTED, 1.6), (70, INK, 2.6)]:
        a = math.radians(ang)
        vx = ccx + R * math.cos(a)
        vy = ccy - R * math.sin(a)
        frags.append(arrow(ccx, ccy, vx, vy, color=col, sw=sw))
    frags.append(text(ccx, ccy + R + 30, "вектор (I_A, I_B) — сталої довжини,",
                     size=11.5, color=INK, anchor="middle"))
    frags.append(text(ccx, ccy + R + 46, "обертається дрібними сходинками; ротор іде за ним",
                     size=11.5, color=INK, anchor="middle"))
    # праворуч — пояснення мікрокроку
    frags.append(fitbox(400, 288, 270, 84,
                        "1 повний крок (1.8°)\nділиться на 16 сходинок\nструму → 16 мікрокроків\n(плавніше й тихіше)",
                        size=12.5, fill="#e8f7ee", stroke=FIELD, bold=True))
    render(os.path.join(IMG, 'microstep-sincos.svg'), W, H, *frags,
           title="Мікрокрок: рівні струму фаз задають кут ротора")


def _current_axes(gx, gy, gw, gh, caption, cap_col, cap_fill):
    """Порожні осі I(t) з підписами й рамкою-підписом унизу."""
    out = rect(gx, gy, gw, gh, fill=BG, stroke=MUTED, sw=1.3, rx=6)
    out += line(gx, gy + gh, gx + gw, gy + gh, color=LINE, sw=1.3)  # t
    out += line(gx, gy, gx, gy + gh, color=LINE, sw=1.3)            # I
    out += text(gx + 7, gy + 12, "I", size=11, color=INK, anchor="start", bold=True)
    out += text(gx + gw - 5, gy + gh + 15, "час", size=10, color=MUTED, anchor="end")
    return out


def _target_line(gx, gy, gw, lvl_y):
    out = line(gx, lvl_y, gx + gw, lvl_y, color=POS, sw=1.4, dash="5 4")
    out += text(gx + gw - 4, lvl_y - 5, "потрібний струм", size=9.5, color=POS,
                anchor="end", bold=True)
    return out


# ── Фігура (для вставки hist): три покоління живлення обмотки ────────────────
def fig_drive_evolution():
    """L/R (низька напруга) → L/nR (резистор гасить) → чоппер (петля)."""
    W, H = 720, 300
    frags = []
    gw, gh = 190, 150
    gy = 60
    xs = [30, 265, 500]
    lvl = gy + 44  # цільовий рівень струму (той самий у всіх трьох)

    # 1) L/R — низька напруга: струм повзе до рівня повільно (експонента), ледь дотягує
    gx = xs[0]
    frags.append(_current_axes(gx, gy, gw, gh, "", POS, "#fdf0ee"))
    frags.append(_target_line(gx, gy, gw, lvl))
    pts = []
    for i in range(0, 101):
        t = i / 100.0
        # повільна експонента, доходить майже до рівня лише в кінці вікна
        yy = (gy + gh) - (gy + gh - lvl) * (1 - math.exp(-2.3 * t))
        pts.append((gx + t * gw, yy))
    frags.append('<path d="M%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (
        " L".join("%.1f %.1f" % p for p in pts), NEG))
    frags.append(text(gx + gw / 2, gy - 12, "L/R — «правильна» напруга",
                      size=11.5, color=INK, anchor="middle", bold=True))
    frags.append(fitbox(gx, gy + gh + 12, gw, 46,
                        "струм повзе повільно (U/L мале) —\nна швидкості не встигає, момент падає",
                        size=10, fill="#eef1fd", stroke=NEG))

    # 2) L/nR — вища напруга + послідовний резистор: наростає швидко, тримає рівень, але гріється
    gx = xs[1]
    frags.append(_current_axes(gx, gy, gw, gh, "", POS, "#fdf0ee"))
    frags.append(_target_line(gx, gy, gw, lvl))
    pts = []
    for i in range(0, 101):
        t = i / 100.0
        yy = (gy + gh) - (gy + gh - lvl) * (1 - math.exp(-6.5 * t))
        pts.append((gx + t * gw, yy))
    frags.append('<path d="M%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (
        " L".join("%.1f %.1f" % p for p in pts), FIELD))
    frags.append(text(gx + gw / 2, gy - 12, "L/nR — резистор гасить",
                      size=11.5, color=INK, anchor="middle", bold=True))
    # символ «жар» на резисторі
    frags.append(text(gx + gw - 16, lvl + 26, "🔥", size=15, anchor="middle"))
    frags.append(fitbox(gx, gy + gh + 12, gw, 46,
                        "вища напруга — струм наростає\nшвидко, але резистор палить ват",
                        size=10, fill="#eef6ef", stroke=FIELD))

    # 3) чоппер — висока напруга, петля пиляє коло рівня
    gx = xs[2]
    frags.append(_current_axes(gx, gy, gw, gh, "", POS, "#fdf0ee"))
    frags.append(_target_line(gx, gy, gw, lvl))
    pts = [(gx, gy + gh)]
    xr = gx + 40
    pts.append((xr, lvl))  # крутий фронт наростання
    step = 15
    up = True
    xx = xr
    while xx < gx + gw - 5:
        xx2 = min(xx + step, gx + gw - 5)
        pts.append((xx2, lvl + (6 if up else -6)))
        up = not up
        xx = xx2
    frags.append('<path d="M%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (
        " L".join("%.1f %.1f" % p for p in pts), POS))
    frags.append(text(gx + gw / 2, gy - 12, "чоппер — петля стереже",
                      size=11.5, color=INK, anchor="middle", bold=True))
    frags.append(fitbox(gx, gy + gh + 12, gw, 46,
                        "висока напруга жене вгору, ключ\nріже — струм рівний, втрат нема",
                        size=10, fill="#fdf0ee", stroke=POS))

    render(os.path.join(IMG, 'drive-evolution.svg'), W, H, *frags,
           title="Три покоління живлення обмотки кроковика")


if __name__ == '__main__':
    fig_two_bridges()
    fig_chopper()
    fig_microstep()
    fig_drive_evolution()
    print("OK: figures written to", IMG)
