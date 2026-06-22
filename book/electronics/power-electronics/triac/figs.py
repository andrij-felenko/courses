# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Дрібний помічник: малюнок тиристора (трикутник + катодна риска + затвор) ──
def scr_symbol(x_top, y_top, x_bot, y_bot, gx, gy, flip=False):
    """Символ тиристора між (x_top,y_top) і (x_bot,y_bot), затвор у (gx,gy).
    flip=False: трикутник дивиться вниз (анод згори). flip=True — навпаки."""
    midx = (x_top + x_bot) / 2
    ty = y_top + (y_bot - y_top) * 0.32
    by = y_top + (y_bot - y_top) * 0.55
    p = []
    p.append(line(x_top, y_top, midx, ty, color=INK, sw=2.2))
    if not flip:
        p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" '
                 'stroke="%s" stroke-width="1.8"/>' % (midx-13, ty, midx+13, ty, midx, by, INK))
        p.append(line(midx-15, by, midx+15, by, color=INK, sw=2.6))      # катодна риска
        p.append(line(midx, by, midx, y_bot, color=INK, sw=2.2))
        p.append(line(midx-15, by-2, gx, gy, color=INK, sw=2))           # затвор
    else:
        p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" '
                 'stroke="%s" stroke-width="1.8"/>' % (midx-13, by, midx+13, by, midx, ty, INK))
        p.append(line(midx-15, ty, midx+15, ty, color=INK, sw=2.6))
        p.append(line(midx, by, midx, y_bot, color=INK, sw=2.2))
        p.append(line(midx-15, ty+2, gx, gy, color=INK, sw=2))
    return "".join(p)


# ════════════════════════════════════════════════════════════════════════════
# 1) Симістор = два антипаралельні тиристори + символ
# ════════════════════════════════════════════════════════════════════════════
def fig_two_scr():
    W, H = 760, 300
    p = []
    # ── ліва панель: два тиристори назустріч ──
    p.append(rect(40, 56, 350, 214, fill=BG, stroke="#c9d3dc", sw=1.4))
    p.append(text(215, 80, "два тиристори назустріч", size=13, bold=True))
    # лівий тиристор: анод згори
    p.append(scr_symbol(150, 110, 150, 200, 112, 168, flip=False))
    p.append(text(150, 104, "A", size=11, bold=True))
    p.append(text(150, 214, "K", size=11, bold=True))
    p.append(text(108, 172, "G", size=11, color=FIELD, bold=True, anchor="end"))
    # правий тиристор: анод знизу (антипаралельно)
    p.append(scr_symbol(250, 200, 250, 110, 288, 152, flip=True))
    p.append(text(250, 104, "K", size=11, bold=True))
    p.append(text(250, 214, "A", size=11, bold=True))
    # перемички між ними (антипаралель)
    p.append(line(150, 110, 250, 110, color=MUTED, sw=1.6, dash="4 3"))
    p.append(line(150, 200, 250, 200, color=MUTED, sw=1.6, dash="4 3"))
    p.append(text(200, 250, "обидві полярності разом", size=11, color=FIELD, bold=True))

    # ── права панель: символ симістора ──
    p.append(rect(410, 56, 310, 214, fill=BG, stroke="#c9d3dc", sw=1.4))
    p.append(text(565, 80, "символ симістора", size=13, bold=True))
    cx = 560
    # два зустрічні трикутники між MT1(низ) і MT2(верх)
    p.append(line(cx, 120, cx, 140, color=INK, sw=2.2))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.8"/>'
             % (cx-14, 140, cx+14, 140, cx, 162, INK))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.8"/>'
             % (cx-14, 188, cx+14, 188, cx, 166, INK))
    p.append(line(cx, 188, cx, 208, color=INK, sw=2.2))
    p.append(line(cx+14, 140, cx+14, 162, color=INK, sw=2.6))
    p.append(line(cx-14, 188, cx-14, 166, color=INK, sw=2.6))
    p.append(line(cx-14, 182, cx-40, 196, color=FIELD, sw=2))   # затвор
    p.append(text(cx, 116, "MT2", size=11, bold=True))
    p.append(text(cx, 222, "MT1", size=11, bold=True))
    p.append(text(cx-44, 200, "G", size=11, color=FIELD, bold=True, anchor="end"))
    p.append(text(cx+22, 166, "один затвор", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(cx, 250, "MT1 і MT2 рівноправні", size=10, color=MUTED, italic=True))
    return render(os.path.join(OUT, "triac-two-scr.svg"), W, H, *p,
                  title="Симістор: два зустрічні тиристори в одному кристалі")


# ════════════════════════════════════════════════════════════════════════════
# 2) Обидві півхвилі на навантаженні (повна синусоїда з відсіканням)
# ════════════════════════════════════════════════════════════════════════════
def fig_both_halves():
    W, H = 760, 300
    ox, oy = 70, 160          # початок осей (oy — вісь нуля)
    aw = 620
    amp = 95
    p = []
    p.append(arrow(ox, 270, ox, 50, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw + 8, oy + 4, "t", size=13, bold=True, italic=True))
    p.append(text(ox - 6, 48, "U на навантаженні", size=12, bold=True, anchor="start"))

    cycles = 2.0
    delay = 0.18              # частка півхвилі до запуску (кут відсікання)
    n = 700
    # сіра «повна» синусоїда-орієнтир
    pts_full = []
    for i in range(n + 1):
        frac = i / n
        x = ox + frac * aw
        y = oy - amp * math.sin(frac * cycles * 2 * math.pi)
        pts_full.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="#e2e2e2" stroke-width="2.0"/>' % " ".join(pts_full))

    # «жива» крива на навантаженні: кожна півхвиля стартує із затримкою (стрибок)
    half = 1.0 / (cycles * 2)
    seg = []
    for i in range(n + 1):
        frac = i / n
        ph = frac / half               # номер півхвилі (0..2*cycles)
        loc = ph - math.floor(ph)      # позиція всередині півхвилі 0..1
        x = ox + frac * aw
        if loc < delay:
            # до запуску: нуль (на осі)
            if seg:
                p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(seg), INK))
                seg = []
            continue
        y = oy - amp * math.sin(frac * cycles * 2 * math.pi)
        # вертикальний фронт у момент запуску
        if not seg:
            seg.append("%.1f,%.1f" % (x, oy))
        seg.append("%.1f,%.1f" % (x, y))
    if seg:
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(seg), INK))

    # позначки переходів через нуль (де симістор гасне)
    for k in range(1, int(cycles * 2) + 1):
        x = ox + k * half * aw
        p.append(line(x, oy - 6, x, oy + 6, color=MUTED, sw=1.4))
    p.append(text(ox + half * aw * 0.6, oy - amp - 10, "+ півхвиля", size=10, color=POS, bold=True))
    p.append(text(ox + half * aw * 1.6, oy + amp + 18, "− півхвиля", size=10, color=NEG, bold=True))
    return render(os.path.join(OUT, "triac-both-halves.svg"), W, H, *p,
                  title="Симістор віддає обидві півхвилі — весь період")


# ════════════════════════════════════════════════════════════════════════════
# 3) Чотири квадранти запуску (за конвенцією: Q-IV = MT2−, G+ — найвередливіший)
# ════════════════════════════════════════════════════════════════════════════
def fig_quadrants():
    W, H = 720, 360
    cx, cy = 360, 195
    p = []
    p.append(line(cx - 150, cy, cx + 150, cy, color=INK, sw=1.6))
    p.append(text(cx + 156, cy + 4, "MT2", size=11, bold=True, anchor="start"))
    p.append(line(cx, cy + 150, cx, cy - 150, color=INK, sw=1.6))
    p.append(text(cx + 6, cy - 152, "затвор G", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(cx + 150, cy + 18, "+", size=13, color=POS, bold=True))
    p.append(text(cx - 150, cy + 18, "−", size=13, color=NEG, bold=True))
    p.append(text(cx + 14, cy - 142, "+", size=13, color=POS, bold=True, anchor="start"))
    p.append(text(cx - 14, cy + 152, "−", size=13, color=NEG, bold=True, anchor="end"))

    def cell(qx, qy, name, sign, note, col):
        return (text(qx, qy, name, size=13, color=col, bold=True) +
                text(qx, qy + 20, sign, size=11) +
                text(qx, qy + 38, note, size=9.5, color=col, italic=True))
    # Q-I: MT2+, G+ (праворуч-угорі) — найчутливіший
    p.append(cell(cx + 80, cy - 78, "Квадрант I", "MT2 +, G +", "найчутливіший", FIELD))
    # Q-II: MT2+, G− (праворуч-унизу)
    p.append(cell(cx + 80, cy + 56, "Квадрант II", "MT2 +, G −", "трохи гірше", "#e0a32e"))
    # Q-III: MT2−, G− (ліворуч-унизу)
    p.append(cell(cx - 80, cy + 56, "Квадрант III", "MT2 −, G −", "трохи гірше", "#e0a32e"))
    # Q-IV: MT2−, G+ (ліворуч-угорі) — найвередливіший
    p.append(cell(cx - 80, cy - 78, "Квадрант IV", "MT2 −, G +", "найвередливіший", POS))
    return render(os.path.join(OUT, "triac-quadrants.svg"), W, H, *p,
                  title="Квадранти запуску: знак MT2 × знак затвора")


# ════════════════════════════════════════════════════════════════════════════
# 4) RC-DIAC коло керування симістором (класичний димер)
# ════════════════════════════════════════════════════════════════════════════
def fig_diac_circuit():
    W, H = 760, 300
    p = []
    # шина фази (верх) і MT1 (низ)
    top, bot = 90, 240
    p.append(line(90, top, 660, top, color=INK, sw=2))
    p.append(text(86, top - 8, "фаза (MT2-бік)", size=10, bold=True, anchor="start"))
    p.append(line(90, bot, 660, bot, color=INK, sw=2))
    p.append(text(420, bot + 18, "MT1 (нейтраль)", size=10, bold=True))

    # вузол керування: R від фази → точка K, далі DIAC у затвор; C від K на MT1
    p.append(line(150, top, 150, 130, color=INK, sw=2))
    # резистор R (потенціометр) — прямокутник зі стрілкою
    p.append(rect(125, 130, 50, 16, fill=BG, stroke=INK, sw=1.8, rx=0))
    p.append(line(168, 122, 132, 154, color=INK, sw=1.4))     # стрілка потенціометра
    p.append(text(150, 124, "R", size=11, bold=True))
    p.append(line(150, 146, 150, 175, color=INK, sw=2))        # до вузла K
    Ky = 175
    p.append(circle(150, Ky, 2.5, fill=INK, stroke=INK))
    # конденсатор C від K донизу на MT1
    p.append(line(150, Ky, 150, 200, color=INK, sw=2))
    p.append(line(134, 200, 166, 200, color=INK, sw=2.4))
    p.append(line(134, 210, 166, 210, color=INK, sw=2.4))
    p.append(text(174, 208, "C", size=11, bold=True, anchor="start"))
    p.append(line(150, 210, 150, bot, color=INK, sw=2))
    # DIAC від K праворуч у затвор
    p.append(line(150, Ky, 300, Ky, color=INK, sw=2))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.6"/>'
             % (316, Ky-7, 316, Ky+7, 334, Ky, INK))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.6"/>'
             % (344, Ky-7, 344, Ky+7, 326, Ky, INK))
    p.append(text(330, Ky - 14, "DIAC", size=10, bold=True))
    p.append(line(344, Ky, 430, Ky, color=FIELD, sw=2))
    p.append(text(388, Ky - 8, "імпульс у затвор", size=9, color=FIELD, bold=True))

    # силовий симістор праворуч між фазою(top) і MT1(bot)
    sx = 560
    p.append(line(sx, top, sx, 140, color=INK, sw=2.2))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.8"/>'
             % (sx-14, 140, sx+14, 140, sx, 162, INK))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.8"/>'
             % (sx-14, 188, sx+14, 188, sx, 166, INK))
    p.append(line(sx, 188, sx, bot, color=INK, sw=2.2))
    p.append(line(sx+14, 140, sx+14, 162, color=INK, sw=2.6))
    p.append(line(sx-14, 188, sx-14, 166, color=INK, sw=2.6))
    p.append(line(sx-14, 182, 430, Ky, color=FIELD, sw=2))     # затвор від DIAC
    p.append(text(sx, 134, "MT2", size=10, bold=True))
    p.append(text(sx, bot + 18, "MT1", size=10, bold=True))
    p.append(text(sx - 40, 178, "G", size=11, color=FIELD, bold=True, anchor="end"))
    p.append(text(sx + 60, 165, "симістор", size=10, bold=True, anchor="middle"))
    return render(os.path.join(OUT, "triac-diac-circuit.svg"), W, H, *p,
                  title="RC-DIAC: R задає момент, DIAC робить фронт різким")


# ════════════════════════════════════════════════════════════════════════════
# 5) [comp] Ізольоване керування: МК → MOC30xx → силовий симістор → мережа
# ════════════════════════════════════════════════════════════════════════════
def fig_isolated_drive():
    W, H = 780, 320
    p = []
    # бар'єр (оптична розв'язка) посередині
    bx = 360
    p.append(line(bx, 50, bx, 280, color=MUTED, sw=1.6, dash="6 5"))
    p.append(text(bx, 300, "оптична розв'язка (струм не тече)", size=10, color=MUTED, italic=True))

    # ── лівий бік: логіка ──
    p.append(text(160, 48, "бік логіки  (GND₁)", size=12, bold=True))
    b1, w1, h1 = textbox(120, 150, "МК\nGPIO", size=12, bold=True, min_w=90)
    p.append(b1)
    p.append(line(165, 150, 230, 150, color=INK, sw=2))
    p.append(rect(232, 142, 40, 16, fill=BG, stroke=INK, sw=1.6, rx=0))
    p.append(text(252, 136, "R1", size=10, bold=True))
    # вхідний світлодіод оптрона
    p.append(line(272, 150, 320, 150, color=INK, sw=2))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.6"/>'
             % (320, 142, 320, 158, 336, 150, INK))
    p.append(line(336, 142, 336, 158, color=INK, sw=2.2))
    p.append(line(322, 138, 330, 130, color=POS, sw=1.4))     # промінчики
    p.append(line(328, 140, 336, 132, color=POS, sw=1.4))
    p.append(text(305, 178, "вхідний LED", size=9, bold=True))
    p.append(line(120, 172, 120, 230, color=INK, sw=2))
    p.append(line(336, 158, 336, 230, color=INK, sw=2))
    p.append(line(120, 230, 336, 230, color=INK, sw=2))
    p.append(text(228, 246, "GND₁", size=10, bold=True))

    # ── правий бік: мережа ──
    p.append(text(580, 48, "бік мережі  (L / N)", size=12, bold=True))
    # опто-симістор усередині MOC30xx
    ox = 410
    p.append(rect(384, 110, 68, 80, fill="#f0f4ff", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(418, 102, "опто-\nсимістор", size=9, bold=True))
    p.append(line(418-9, 130, 418+9, 130, color=INK, sw=1.6))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.3"/>'
             % (418-9, 145, 418+9, 145, 418, 158, INK))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.3"/>'
             % (418-9, 172, 418+9, 172, 418, 160, INK))
    # вивід 6 → R2 → вузол L
    p.append(line(448, 130, 510, 130, color=INK, sw=2))
    p.append(rect(512, 122, 38, 16, fill=BG, stroke=INK, sw=1.6, rx=0))
    p.append(text(531, 116, "R2", size=10, bold=True))
    p.append(line(550, 130, 600, 130, color=INK, sw=2))
    # силовий симістор
    sx = 640
    p.append(line(sx, 80, sx, 120, color=INK, sw=2.2))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.8"/>'
             % (sx-13, 120, sx+13, 120, sx, 140, INK))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.8"/>'
             % (sx-13, 165, sx+13, 165, sx, 145, INK))
    p.append(line(sx, 165, sx, 210, color=INK, sw=2.2))
    p.append(line(sx+13, 120, sx+13, 140, color=INK, sw=2.6))
    p.append(line(sx-13, 165, sx-13, 145, color=INK, sw=2.6))
    p.append(line(sx-13, 160, 448, 170, color=FIELD, sw=2))    # вивід 4 → затвор
    p.append(text(sx, 74, "MT2", size=10, bold=True))
    p.append(text(sx, 226, "MT1", size=10, bold=True))
    p.append(text(sx - 70, 150, "силовий\nсимістор", size=9, bold=True, anchor="middle"))
    # вузол L (фаза) і навантаження
    p.append(line(600, 130, 600, 90, color=INK, sw=2))
    p.append(line(600, 90, sx, 90, color=INK, sw=2))
    p.append(line(sx, 90, sx, 80, color=INK, sw=2))
    p.append(line(sx, 80, 720, 80, color=INK, sw=2))
    p.append(text(724, 84, "L", size=11, color=POS, bold=True, anchor="start"))
    b2, _, _ = textbox(700, 150, "наван-\nтаження", size=9.5, bold=True, min_w=70)
    p.append(b2)
    p.append(line(sx, 210, 700, 210, color=INK, sw=2))
    p.append(line(700, 170, 700, 210, color=INK, sw=2))
    p.append(line(700, 130, 700, 80, color=INK, sw=2))
    p.append(text(724, 214, "N", size=11, color=NEG, bold=True, anchor="start"))
    p.append(line(700, 210, 724, 210, color=INK, sw=2))
    return render(os.path.join(OUT, "triac-isolated-drive.svg"), W, H, *p,
                  title="Ізольоване керування: МК → оптодрайвер → силовий симістор")


# ════════════════════════════════════════════════════════════════════════════
# 6) [comp] random-phase проти zero-cross: коли йде струм після команди
# ════════════════════════════════════════════════════════════════════════════
def _mains_sine(ox, oy, aw, amp, n=400, cycles=2.0):
    pts = []
    for i in range(n + 1):
        frac = i / n
        x = ox + frac * aw
        y = oy - amp * math.sin(frac * cycles * 2 * math.pi)
        pts.append((frac, x, y))
    return pts


def fig_random_vs_zerocross():
    W, H = 780, 380
    aw, amp = 600, 60
    ox = 100
    cmd = 0.30            # частка осі, де МК дав команду
    p = []
    cycles = 2.0
    half = 1.0 / (cycles * 2)

    def panel(oy, label, color, zero_cross):
        out = []
        out.append(arrow(ox, oy + amp + 22, ox, oy - amp - 14, color=INK, sw=1.4))
        out.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.4))
        out.append(text(ox + aw + 6, oy + 4, "t", size=11, bold=True, italic=True))
        out.append(text(ox - 8, oy - amp - 16, label, size=11, color=color, bold=True, anchor="start"))
        # сіра напруга мережі
        sine = _mains_sine(ox, oy, aw, amp, cycles=cycles)
        out.append('<polyline points="%s" fill="none" stroke="#dcdcdc" stroke-width="1.8"/>'
                   % " ".join("%.1f,%.1f" % (x, y) for _, x, y in sine))
        # пунктири переходів через нуль
        for k in range(1, int(cycles * 2)):
            x = ox + k * half * aw
            out.append(line(x, oy - amp - 4, x, oy + amp + 4, color=MUTED, sw=1.0, dash="3 4"))
        # лінія команди МК
        xc = ox + cmd * aw
        out.append(line(xc, oy - amp - 10, xc, oy + amp + 10, color=POS, sw=1.4, dash="5 4"))
        out.append(text(xc, oy - amp - 14, "команда МК", size=9, color=POS, bold=True))
        # момент старту струму
        if zero_cross:
            # найближчий перехід через нуль ПІСЛЯ команди
            start = math.ceil(cmd / half) * half
        else:
            start = cmd
        xs = ox + start * aw
        # струм у навантаженні від старту до кінця осі (форма = синус мережі)
        seg = []
        for frac, x, y in sine:
            if frac >= start - 1e-6:
                if not seg:
                    seg.append("%.1f,%.1f" % (x, oy))
                seg.append("%.1f,%.1f" % (x, y))
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                   % (" ".join(seg), color))
        if zero_cross:
            out.append(line(xs, oy - 5, xs, oy + 5, color=color, sw=2))
            out.append(text(xs + 4, oy + amp + 18, "старт — на нулі", size=9, color=color, bold=True, anchor="start"))
        else:
            out.append(text(xs + 4, oy - amp + 2, "старт — одразу", size=9, color=color, bold=True, anchor="start"))
        return out

    p += panel(110, "random-phase: струм іде в момент команди", POS, zero_cross=False)
    p += panel(285, "zero-cross: струм чекає переходу через нуль", FIELD, zero_cross=True)
    p.append(text(W/2, 360, "Сірий — напруга мережі; пунктир — переходи через нуль. Затримка zero-cross — до півперіоду (≈10 мс при 50 Гц).",
                  size=9.5, color=MUTED, italic=True))
    return render(os.path.join(OUT, "triac-random-vs-zerocross.svg"), W, H, *p,
                  title="Коли вмикається струм після команди МК")


if __name__ == "__main__":
    fig_two_scr()
    fig_both_halves()
    fig_quadrants()
    fig_diac_circuit()
    fig_isolated_drive()
    fig_random_vs_zerocross()
    print("OK: figures regenerated ->", OUT)
