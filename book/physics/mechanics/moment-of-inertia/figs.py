# -*- coding: utf-8 -*-
"""Фігури до теми «Момент інерції».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def arc_arrow(cx, cy, r, a0_deg, a1_deg, color=LINE, sw=2.4, head=10):
    """Дуга-стрілка (коло) від кута a0 до a1 (градуси, 0°=праворуч, проти год.)."""
    a0 = math.radians(a0_deg); a1 = math.radians(a1_deg)
    x0 = cx + r * math.cos(a0); y0 = cy - r * math.sin(a0)
    x1 = cx + r * math.cos(a1); y1 = cy - r * math.sin(a1)
    sweep_ccw = 1 if a1_deg > a0_deg else 0
    sweep = 0 if sweep_ccw else 1
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    path = ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw))
    dir_sign = 1 if sweep_ccw else -1
    tx = -math.sin(a1) * dir_sign
    ty = -math.cos(a1) * dir_sign
    L = math.hypot(tx, ty); tx, ty = tx / L, ty / L
    back = 2.2
    px, py = x1 - tx * head, y1 - ty * head
    nx, ny = -ty, tx
    h = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
         % (x1, y1, px + nx * head / back, py + ny * head / back,
            px - nx * head / back, py - ny * head / back, color))
    return path + h


def axis_dot(f, x, y, label="вісь", dy=26):
    """Позначка осі обертання (перпендикулярної до площини)."""
    f.append(circle(x, y, 8, fill=BG, stroke=INK, sw=2))
    f.append(circle(x, y, 2.6, fill=INK, stroke=INK, sw=1))
    if label:
        f.append(text(x, y + dy, label, size=12, color=MUTED))


# ── Фігура 1: момент інерції складається з частинок mᵢrᵢ² ─────────────────────
def fig_build():
    W, H = 840, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Далі від осі — швидше біжить і важче піддається",
                  size=17, bold=True))

    O = (205, 268)
    axis_dot(f, O[0], O[1], "вісь", dy=28)
    # напрям обертання
    f.append(arc_arrow(O[0], O[1], 44, 150, 40, color=MUTED, sw=1.8, head=8))
    f.append(text(O[0] - 2, O[1] - 52, "ω", size=15, italic=True, color=MUTED))

    # три частинки: (точка, підпис, зсув підпису r, бік підпису швидкості)
    parts = [
        ((345, 214), "m₁", 1),
        ((478, 322), "m₂", -1),
        ((690, 190), "m₃", 1),
    ]
    for P, mlabel, side in parts:
        dx, dy = P[0] - O[0], P[1] - O[1]
        r = math.hypot(dx, dy)
        # радіус-пунктир з підписом rᵢ
        f.append(line(O[0], O[1], P[0], P[1], color=MUTED, sw=1.3, dash="6 5"))
        mx, my = (O[0] + P[0]) / 2, (O[1] + P[1]) / 2
        nx, ny = -dy / r, dx / r
        f.append(text(mx + nx * 16, my + ny * 16 + 4,
                      "r" + mlabel[1], size=14, italic=True, color=MUTED))
        # частинка
        f.append(circle(P[0], P[1], 12, fill="#eef2fb", stroke=NEG, sw=2))
        f.append(text(P[0], P[1] + 5, mlabel, size=13, bold=True, color=NEG))
        # швидкість v = ωr, дотична (проти годинникової), довжина ∝ r
        tx, ty = dy / r, -dx / r
        Lv = 0.21 * r
        vx, vy = P[0] + tx * Lv, P[1] + ty * Lv
        f.append(arrow(P[0], P[1], vx, vy, color=POS, sw=2.8))
        f.append(text(vx + side * 8, vy - 8, "v = ωr" + mlabel[1],
                      size=12, bold=True, color=POS,
                      anchor="start" if side > 0 else "end"))

    b, w, h = textbox(W / 2, H - 30,
                      "внесок частинки = mᵢ·rᵢ²      →      J = Σ mᵢ·rᵢ²   (відстань — у квадраті!)",
                      size=14, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "build-from-parts.svg"), W, H, *f)


# ── Фігура 2: обруч проти диска — однакова маса, різний J ─────────────────────
def fig_hoop_disc():
    W, H = 800, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Однакова маса M і радіус R — а розкрутити по-різному важко",
                  size=17, bold=True))

    R = 108
    CL = (215, 210)
    CR = (585, 210)

    def spoke_R(C, ang_deg):
        a = math.radians(ang_deg)
        ex, ey = C[0] + R * math.cos(a), C[1] - R * math.sin(a)
        f.append(line(C[0], C[1], ex, ey, color=MUTED, sw=1.4, dash="5 4"))
        mx, my = (C[0] + ex) / 2, (C[1] + ey) / 2
        f.append(text(mx, my - 8, "R", size=14, italic=True, color=MUTED))

    # ── обруч: уся маса на ободі
    f.append(circle(CL[0], CL[1], R, fill="none", stroke=INK, sw=8))
    for k in range(16):
        a = math.radians(k * 360 / 16)
        f.append(circle(CL[0] + R * math.cos(a), CL[1] - R * math.sin(a),
                        4.5, fill=POS, stroke=POS, sw=1))
    axis_dot(f, CL[0], CL[1], "", dy=0)
    spoke_R(CL, 55)
    f.append(text(CL[0], CL[1] - R - 18, "ОБРУЧ — маса на краю",
                  size=13, bold=True, color=INK))

    # ── диск: маса по всій площі
    f.append(circle(CR[0], CR[1], R, fill="#eef2fb", stroke=INK, sw=2.2))
    dots = [(0.30, 20), (0.55, 80), (0.45, 150), (0.68, 200), (0.35, 250),
            (0.60, 300), (0.20, 340), (0.78, 120), (0.50, 240), (0.72, 350),
            (0.40, 110), (0.62, 40), (0.25, 170), (0.80, 270), (0.52, 15)]
    for frac, ang in dots:
        a = math.radians(ang)
        f.append(circle(CR[0] + frac * R * math.cos(a), CR[1] - frac * R * math.sin(a),
                        4.2, fill=POS, stroke=POS, sw=1))
    axis_dot(f, CR[0], CR[1], "", dy=0)
    spoke_R(CR, 55)
    f.append(text(CR[0], CR[1] - R - 18, "ДИСК — маса скрізь",
                  size=13, bold=True, color=INK))

    # формули під кожним
    b1, w1, h1 = textbox(CL[0], CL[1] + R + 52, "J = M·R²",
                         size=16, pad=10, fill="#fdecea", stroke=POS, sw=1.4, bold=True)
    f.append(b1)
    b2, w2, h2 = textbox(CR[0], CR[1] + R + 52, "J = ½·M·R²",
                         size=16, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b2)

    b3, w3, h3 = textbox(W / 2, H - 26,
                         "обруч розкрутити вдвічі важче: уся його маса винесена на повний радіус R",
                         size=13, pad=9, fill=FILL, stroke=LINE, sw=1.2, bold=False)
    f.append(b3)
    return render(os.path.join(IMG, "hoop-vs-disc.svg"), W, H, *f)


# ── Фігура 3: довідник моментів інерції простих тіл ───────────────────────────
def fig_gallery():
    W, H = 900, 580
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Момент інерції простих тіл: множник каже, як близько маса до осі",
                  size=17, bold=True))

    cols, rows = 3, 2
    cw, ch = W / cols, (H - 70) / rows
    y_top = 58

    def cell(ci, ri):
        return (ci * cw + cw / 2, y_top + ri * ch + ch / 2)

    def vaxis(cx, cy, half=70):
        f.append(line(cx, cy - half, cx, cy + half, color=NEG, sw=2.0, dash="6 5"))

    def caption(cx, cy_bottom, title, formula):
        f.append(text(cx, cy_bottom, title, size=13, bold=True, color=INK))
        b, w, h = textbox(cx, cy_bottom + 26, formula, size=15, pad=8,
                          fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
        f.append(b)

    # 1 точкова маса
    cx, cy = cell(0, 0); cy -= 24
    axis_dot(f, cx - 62, cy, "", dy=0)
    f.append(line(cx - 62, cy, cx + 46, cy, color=MUTED, sw=1.4, dash="5 4"))
    f.append(text((cx - 62 + cx + 46) / 2, cy - 8, "r", size=13, italic=True, color=MUTED))
    f.append(circle(cx + 46, cy, 12, fill=POS, stroke=POS, sw=1))
    f.append(text(cx + 46, cy + 5, "m", size=12, bold=True, color=BG))
    caption(cx, cy + 46, "точкова маса", "J = m·r²")

    # 2 обруч
    cx, cy = cell(1, 0); cy -= 24
    f.append(circle(cx, cy, 46, fill="none", stroke=INK, sw=7))
    axis_dot(f, cx, cy, "", dy=0)
    caption(cx, cy + 66, "обруч / труба", "J = M·R²")

    # 3 суцільний диск
    cx, cy = cell(2, 0); cy -= 24
    f.append(circle(cx, cy, 46, fill="#eef2fb", stroke=INK, sw=2.2))
    axis_dot(f, cx, cy, "", dy=0)
    caption(cx, cy + 66, "диск / циліндр", "J = ½·M·R²")

    # 4 куля
    cx, cy = cell(0, 1); cy -= 20
    f.append(circle(cx, cy, 46, fill="#eef2fb", stroke=INK, sw=2.2))
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="46" ry="15" fill="none" '
             'stroke="%s" stroke-width="1.4"/>' % (cx, cy, MUTED))
    axis_dot(f, cx, cy, "", dy=0)
    caption(cx, cy + 66, "суцільна куля", "J = (2/5)·M·R²")

    # 5 стрижень — вісь по центру
    cx, cy = cell(1, 1); cy -= 20
    f.append(rect(cx - 78, cy - 9, 156, 18, fill="#eef2fb", stroke=INK, sw=1.8, rx=4))
    vaxis(cx, cy, half=40)
    axis_dot(f, cx, cy, "", dy=0)
    caption(cx, cy + 62, "стрижень: вісь у центрі", "J = (1/12)·M·L²")

    # 6 стрижень — вісь на кінці
    cx, cy = cell(2, 1); cy -= 20
    f.append(rect(cx - 62, cy - 9, 156, 18, fill="#eef2fb", stroke=INK, sw=1.8, rx=4))
    vaxis(cx - 62, cy, half=40)
    axis_dot(f, cx - 62, cy, "", dy=0)
    caption(cx, cy + 62, "стрижень: вісь на кінці", "J = (1/3)·M·L²")

    return render(os.path.join(IMG, "shapes-gallery.svg"), W, H, *f)


# ── Фігура 4: фігуристка — L = Jω зберігається ────────────────────────────────
def fig_skater():
    W, H = 820, 450
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Притиснула руки — J впало, ω зросло: L = J·ω зберігається",
                  size=17, bold=True))

    def skater(cx, base_y, reach, hand_up, title, spin_r, spin_from, spin_to, spin_col, note):
        axis_x = cx
        top = base_y - 150
        # вісь обертання (вертикаль крізь тіло)
        f.append(line(axis_x, top - 34, axis_x, base_y + 20, color=MUTED, sw=1.4, dash="6 5"))
        # тулуб
        f.append('<ellipse cx="%.1f" cy="%.1f" rx="15" ry="52" fill="#eef2fb" '
                 'stroke="%s" stroke-width="2"/>' % (axis_x, top + 74, INK))
        # голова
        f.append(circle(axis_x, top + 8, 16, fill="#eef2fb", stroke=INK, sw=2))
        # ноги
        f.append(line(axis_x, top + 122, axis_x - 10, base_y + 8, color=INK, sw=4))
        f.append(line(axis_x, top + 122, axis_x + 10, base_y + 8, color=INK, sw=4))
        # руки з масами-долонями
        sh_y = top + 46
        hx = axis_x + reach
        hxL = axis_x - reach
        hy = sh_y - hand_up
        f.append(line(axis_x, sh_y, hx, hy, color=INK, sw=4))
        f.append(line(axis_x, sh_y, hxL, hy, color=INK, sw=4))
        for h_x in (hx, hxL):
            f.append(circle(h_x, hy, 10, fill=POS, stroke=POS, sw=1))
        # позначки відстані руки до осі
        f.append(line(axis_x, base_y + 40, hx, base_y + 40, color=MUTED, sw=1.2))
        f.append(line(axis_x, base_y + 34, axis_x, base_y + 46, color=MUTED, sw=1.2))
        f.append(line(hx, base_y + 34, hx, base_y + 46, color=MUTED, sw=1.2))
        f.append(text((axis_x + hx) / 2, base_y + 34, "r", size=13, italic=True, color=MUTED))
        # обертання
        f.append(arc_arrow(axis_x, top - 18, spin_r, spin_from, spin_to,
                           color=spin_col, sw=3.0, head=11))
        f.append(text(axis_x, top - 44, "ω", size=15, italic=True, bold=True, color=spin_col))
        # підпис під фігурою
        f.append(text(axis_x, base_y + 70, title, size=14, bold=True, color=INK))
        b, w, h = textbox(axis_x, base_y + 100, note, size=13, pad=9,
                          fill=FILL, stroke=spin_col, sw=1.3, bold=True)
        f.append(b)

    # ліворуч: руки розкинуті — велике J, мале ω (повільна дуга)
    skater(220, 250, reach=92, hand_up=0, title="руки розкинуті",
           spin_r=30, spin_from=140, spin_to=60, spin_col=NEG,
           note="велике J · мале ω")
    # праворуч: руки притиснуті — мале J, велике ω (широка швидка дуга)
    skater(600, 250, reach=26, hand_up=44, title="руки притиснуті",
           spin_r=46, spin_from=210, spin_to=-70, spin_col=POS,
           note="мале J · велике ω")

    # стрілка переходу між станами
    f.append(arrow(330, 200, 470, 200, color=FIELD, sw=3.0))
    f.append(text(400, 188, "J₁ω₁ = J₂ω₂", size=14, bold=True, color=FIELD))

    return render(os.path.join(IMG, "skater.svg"), W, H, *f)


# ── Фігура 5: центр коливань і взаємозамінність (Гюйгенс) ─────────────────────
def fig_center_oscillation():
    W, H = 940, 410
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Центр коливань: витягнуте тіло гойдається як точка на нитці",
                  size=17, bold=True))

    def bracket(x, y0, y1, label):
        f.append(line(x, y0, x, y1, color=MUTED, sw=1.4))
        f.append(line(x - 6, y0, x + 6, y0, color=MUTED, sw=1.4))
        f.append(line(x - 6, y1, x + 6, y1, color=MUTED, sw=1.4))
        f.append(text(x - 12, (y0 + y1) / 2 + 5, label, size=14, italic=True,
                      color=MUTED, anchor="end"))

    PIV_Y, C_Y = 100, 292

    # ── Ліва панель: справжній складений маятник
    LX = 250
    f.append(text(LX, 58, "Справжній маятник — витягнуте тіло", size=13, bold=True))
    f.append(text(LX, 88, "вісь підвісу O", size=12, color=MUTED))
    axis_dot(f, LX, PIV_Y, "", dy=0)
    f.append(rect(LX - 4, PIV_Y, 8, 96, fill="#eef2fb", stroke=INK, sw=1.8, rx=3))
    f.append(circle(LX, PIV_Y + 108, 26, fill="#eef2fb", stroke=INK, sw=2))
    bracket(LX - 44, PIV_Y, C_Y, "L")
    f.append(circle(LX, C_Y, 7, fill=POS, stroke=POS, sw=1))
    f.append(text(LX + 18, C_Y + 5, "центр коливань C", size=12, color=POS,
                  bold=True, anchor="start"))
    b, _, _ = textbox(LX, 366, "період — як у точки\nна нитці завдовжки L",
                      size=12, pad=9, fill=FILL, stroke=FIELD, sw=1.3, bold=True)
    f.append(b)

    # ── Права панель: переверни підвіс — той самий період
    RX = 690
    f.append(text(RX, 58, "Переверни підвіс у C — той самий період", size=13, bold=True))
    f.append(text(RX, 88, "вісь тепер у C", size=12, color=MUTED))
    axis_dot(f, RX, PIV_Y, "", dy=0)
    f.append(circle(RX, PIV_Y + 22, 26, fill="#eef2fb", stroke=INK, sw=2))
    f.append(rect(RX - 4, PIV_Y + 44, 8, 100, fill="#eef2fb", stroke=INK, sw=1.8, rx=3))
    bracket(RX - 44, PIV_Y, C_Y, "L (те саме)")
    f.append(circle(RX, C_Y, 7, fill=POS, stroke=POS, sw=1))
    f.append(text(RX + 18, C_Y - 2, "колишня вісь O —", size=12, color=POS,
                  bold=True, anchor="start"))
    f.append(text(RX + 18, C_Y + 15, "новий центр коливань", size=12, color=POS,
                  bold=True, anchor="start"))
    b, _, _ = textbox(RX, 366, "той самий період T",
                      size=12, pad=9, fill=FILL, stroke=FIELD, sw=1.3, bold=True)
    f.append(b)

    # ── Місток посередині: взаємозамінність
    f.append(arrow(408, 150, 512, 150, color=FIELD, sw=2.4))
    f.append(arrow(512, 166, 408, 166, color=FIELD, sw=2.4))
    b, _, _ = textbox(460, 202, "підвіс ⇄ центр\nколивань\nвзаємозамінні",
                      size=12, pad=9, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)

    return render(os.path.join(IMG, "center-of-oscillation.svg"), W, H, *f)


# ── Фігура 6: історична стрічка народження поняття ────────────────────────────
def fig_timeline():
    W, H = 1120, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Як народжувалося поняття моменту інерції",
                  size=17, bold=True))

    Y = 196
    f.append(arrow(70, Y, 1052, Y, color=LINE, sw=2.5))
    f.append(text(1052, Y - 12, "час", size=12, italic=True, color=MUTED, anchor="end"))

    # (x, above?, color, рядки)
    nodes = [
        (140, False, MUTED, ["1646", "Мерсенн ставить", "задачу центру", "коливань"]),
        (355, True,  NEG,   ["1657", "Маятниковий", "годинник", "Гюйгенса"]),
        (570, False, NEG,   ["1673", "«Horologium", "Oscillatorium»:", "центр коливань"]),
        (785, True,  POS,   ["1765", "Ейлер називає", "momentum inertiae,", "теорія обертання"]),
        (1000, False, FIELD, ["1817", "Кейтер: обернений", "маятник міряє g"]),
    ]
    for x, above, col, lines in nodes:
        cy = 100 if above else 292
        # конектор від вузла до рамки
        edge = cy + (len(lines) * 13 * 1.3 + 18 - 4) / 2 * (1 if above else -1)
        f.append(line(x, Y, x, edge, color=MUTED, sw=1.3, dash="4 4"))
        # вузол
        f.append(circle(x, Y, 8, fill=col, stroke=BG, sw=2.5))
        # рамка з роком (перший рядок) і підписом
        b, _, _ = textbox(x, cy, "\n".join(lines), size=13, pad=9,
                          fill=FILL, stroke=col, sw=1.5, bold=False)
        f.append(b)

    return render(os.path.join(IMG, "oscillation-timeline.svg"), W, H, *f)


# ── Фігура 7: складене тіло — сума m·d², дальня маса важить найбільше ──────────
def fig_compose_arm():
    W, H = 900, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Складене тіло: кожну частину зводимо до осі через J_цм + m·d²",
                  size=17, bold=True))

    # ── схема важеля ──
    S = 850.0                      # px на метр
    O = (300, 180)                 # вісь-шарнір
    xg = O[0] + int(0.40 * S)      # хват на кінці, d = 0.40
    xa = O[0] + int(0.20 * S)      # ЦМ плеча, d = 0.20
    xm = O[0] + int(0.02 * S)      # мотор коло осі, d ≈ 0
    xc = O[0] - int(0.10 * S)      # противага з іншого боку, d = 0.10

    # боом противаги і саме плече
    f.append(line(xc, O[1], O[0], O[1], color=INK, sw=3))
    f.append(rect(O[0], O[1] - 7, xg - O[0], 14, fill="#eef2fb", stroke=INK, sw=2, rx=3))
    # ЦМ плеча
    f.append(circle(xa, O[1], 5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(xa, O[1] - 16, "ЦМ плеча", size=12, color=NEG))
    # мотор
    f.append(rect(xm - 18, O[1] - 17, 36, 34, fill=FILL, stroke=MUTED, sw=1.8, rx=4))
    f.append(text(xm + 2, O[1] - 26, "мотор 0.50 кг", size=12, color=MUTED))
    # противага
    f.append(rect(xc - 17, O[1] - 15, 34, 30, fill="#eef6ef", stroke=FIELD, sw=2, rx=4))
    f.append(text(xc, O[1] - 24, "противага 0.40 кг", size=12, color=FIELD))
    # хват
    f.append(circle(xg, O[1], 13, fill=POS, stroke=POS, sw=1))
    f.append(text(xg, O[1] - 24, "хват 0.25 кг", size=12, bold=True, color=POS))
    # вісь
    axis_dot(f, O[0], O[1], "вісь-шарнір", dy=118)

    # ── розмірні дужки d (рознесені по y, щоб не накладались) ──
    def dbracket(x0, x1, y, label, col=MUTED):
        f.append(line(x0, y, x1, y, color=col, sw=1.3))
        f.append(line(x0, y - 5, x0, y + 5, color=col, sw=1.3))
        f.append(line(x1, y - 5, x1, y + 5, color=col, sw=1.3))
        f.append(text((x0 + x1) / 2, y - 8, label, size=12, italic=True, color=col))

    dbracket(O[0], xa, O[1] + 44, "d = 0.20 м", NEG)
    dbracket(xc, O[0], O[1] + 44, "d = 0.10 м", FIELD)
    dbracket(O[0], xg, O[1] + 84, "d = 0.40 м", POS)
    f.append(text(xm + 30, O[1] + 26, "d ≈ 0", size=12, italic=True, color=MUTED, anchor="start"))

    bF, wF, hF = textbox(W - 150, 96, "J_частини = J_цм + m·d²",
                         size=15, pad=10, fill=FILL, stroke=LINE, sw=1.3, bold=True)
    f.append(bF)

    # ── смуга внесків ──
    f.append(text(W / 2, 344, "Внесок кожної частини у повний момент інерції J = 0.0602 кг·м²",
                  size=15, bold=True))
    x0, ybar, Wbar, hbar = 130, 384, 640, 42
    Jtot = 0.0602
    segs = [("хват",      0.0400, POS,   "0.040", "66%"),
            ("плече",     0.0160, NEG,   "0.016", "27%"),
            ("противага", 0.0040, FIELD, "0.004", "7%"),
            ("мотор",     0.0002, MUTED, "",       "")]
    x = x0
    for name, val, col, above, below in segs:
        w = max(3, val / Jtot * Wbar)
        f.append(rect(x, ybar, w, hbar, fill=col, stroke=BG, sw=1.5, rx=0))
        cx = x + w / 2
        if above:
            f.append(text(cx, ybar - 10, above, size=13, bold=True, color=col))
            f.append(text(cx, ybar + hbar + 20, name + "  " + below, size=12, color=INK))
        x += w
    # мотор-сливер: підпис вирівняно по правому краю смуги, щоб не вийти за полотно
    xend = x0 + Wbar
    f.append(line(xend - 2, ybar + hbar, xend - 2, ybar + hbar + 18, color=MUTED, sw=1.1))
    f.append(text(xend, ybar + hbar + 34, "мотор коло осі ≈ 0.0002 (0.3%)",
                  size=12, color=MUTED, anchor="end"))

    b, w, h = textbox(W / 2, H - 30,
                      "Хват легший за мотор удвічі, а важить у двісті разів більше: відстань d входить у квадраті.",
                      size=13, pad=10, fill="#fdecea", stroke=POS, sw=1.3, bold=False)
    f.append(b)
    return render(os.path.join(IMG, "compose-arm.svg"), W, H, *f)


# ── Фігура 8: чисельне інтегрування — сітка й збіжність до ½MR² ────────────────
def fig_numeric_check():
    W, H = 900, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Довільна форма чисельно: Σ r²·Δm сходиться до відомої формули",
                  size=17, bold=True))

    # ── ЛІВА панель: диск, накритий сіткою ──
    C = (215, 250)
    Rpx = 130
    step = Rpx / 6.0               # 12 клітинок на діаметр
    f.append(text(C[0], 78, "кришимо на елементи маси", size=14, bold=True, color=INK))
    n = 12
    for i in range(n):
        for j in range(n):
            cx = C[0] - Rpx + (i + 0.5) * step
            cy = C[1] - Rpx + (j + 0.5) * step
            if (cx - C[0]) ** 2 + (cy - C[1]) ** 2 <= Rpx * Rpx:
                f.append(rect(cx - step / 2, cy - step / 2, step, step,
                              fill="#eef2fb", stroke="#c9d6ef", sw=0.8, rx=0))
    f.append(circle(C[0], C[1], Rpx, fill="none", stroke=INK, sw=2.4))
    axis_dot(f, C[0], C[1], "", dy=0)
    hi, hj = 8, 3
    hx = C[0] - Rpx + (hi + 0.5) * step
    hy = C[1] - Rpx + (hj + 0.5) * step
    f.append(rect(hx - step / 2, hy - step / 2, step, step,
                  fill="#fdecea", stroke=POS, sw=1.8, rx=0))
    f.append(line(C[0], C[1], hx, hy, color=POS, sw=2.0))
    f.append(text((C[0] + hx) / 2 + 6, (C[1] + hy) / 2 - 8, "r", size=14, italic=True, bold=True, color=POS))
    b, w, h = textbox(C[0], C[1] + Rpx + 52, "Δm = M / влучань      внесок = r²·Δm",
                      size=13, pad=9, fill=FILL, stroke=LINE, sw=1.2, bold=True)
    f.append(b)

    # ── ПРАВА панель: крива збіжності ──
    PX0, PX1 = 500, 850
    PY0, PY1 = 360, 110
    lo, hi_ = 2.4, 5.4            # log10(N)
    ylo, yhi = 0.0435, 0.0465
    f.append(text((PX0 + PX1) / 2, 78, "сходиться до ½MR²", size=14, bold=True, color=INK))

    def px(N):
        return PX0 + (math.log10(N) - lo) / (hi_ - lo) * (PX1 - PX0)

    def py(J):
        return PY0 - (J - ylo) / (yhi - ylo) * (PY0 - PY1)

    f.append(line(PX0, PY0, PX1, PY0, color=INK, sw=1.6))
    f.append(line(PX0, PY0, PX0, PY1, color=INK, sw=1.6))
    f.append(text((PX0 + PX1) / 2, PY0 + 40, "число елементів N (лог)", size=12, color=MUTED))
    for e in (3, 4, 5):
        xx = px(10 ** e)
        f.append(line(xx, PY0, xx, PY0 + 5, color=MUTED, sw=1.2))
        f.append(text(xx, PY0 + 20, "10" + "³⁴⁵"[e - 3], size=12, color=MUTED))
    ya = py(0.045)
    f.append(line(PX0, ya, PX1, ya, color=FIELD, sw=1.8, dash="7 5"))
    f.append(text(PX1, ya - 8, "½MR² = 0.045", size=12, bold=True, color=FIELD, anchor="end"))
    for jv in (0.044, 0.045, 0.046):
        yy = py(jv)
        f.append(line(PX0 - 5, yy, PX0, yy, color=MUTED, sw=1.2))
        f.append(text(PX0 - 10, yy + 4, "%.3f" % jv, size=11, color=MUTED, anchor="end"))

    grid = [(400, 0.04525), (2500, 0.04528), (1e4, 0.04503), (4e4, 0.04502), (1.6e5, 0.04500)]
    mc = [(1e3, 0.04355), (1e4, 0.04481), (1e5, 0.04508)]
    gpts = [(px(N), py(J)) for N, J in grid]
    for a, b2 in zip(gpts, gpts[1:]):
        f.append(line(a[0], a[1], b2[0], b2[1], color=NEG, sw=1.4))
    for X, Y in gpts:
        f.append(circle(X, Y, 4.5, fill=NEG, stroke=NEG, sw=1))
    for N, J in mc:
        f.append(circle(px(N), py(J), 4.5, fill=POS, stroke=POS, sw=1))

    f.append(circle(PX0 + 14, PY1 + 4, 4.5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(PX0 + 24, PY1 + 8, "сітка", size=12, color=NEG, anchor="start"))
    f.append(circle(PX0 + 92, PY1 + 4, 4.5, fill=POS, stroke=POS, sw=1))
    f.append(text(PX0 + 102, PY1 + 8, "Монте-Карло", size=12, color=POS, anchor="start"))

    return render(os.path.join(IMG, "numeric-check.svg"), W, H, *f)


# ── Фігура: теорема Штайнера — перехресний член гасне (Σmρ = 0) ────────────────
def fig_steiner():
    W, H = 820, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Теорема Штайнера: перехресний член гасне, бо Σm·ρ = 0",
                  size=17, bold=True))

    C = (390, 300)   # вісь через центр мас
    O = (205, 300)   # нова паралельна вісь (зсув d)
    P = (600, 150)   # частинка

    f.append(arrow(C[0], C[1], O[0], O[1], color=INK, sw=2.4))
    f.append(text((C[0] + O[0]) / 2, C[1] - 12, "d", size=15, italic=True, bold=True, color=INK))
    f.append(arrow(C[0], C[1], P[0], P[1], color=NEG, sw=2.4))
    f.append(arrow(O[0], O[1], P[0], P[1], color=POS, sw=2.4))
    f.append(text(480, 204, "ρ", size=15, italic=True, bold=True, color=NEG))
    f.append(text(411, 251, "ρ − d", size=14, italic=True, bold=True, color=POS))
    f.append(circle(P[0], P[1], 11, fill="#eef2fb", stroke=INK, sw=2))
    f.append(text(P[0] + 22, P[1] - 2, "m", size=13, bold=True, color=INK))
    axis_dot(f, C[0], C[1], "", dy=0)
    axis_dot(f, O[0], O[1], "", dy=0)
    f.append(text(C[0], C[1] + 32, "вісь через ЦМ", size=12, color=MUTED))
    f.append(text(C[0], C[1] + 50, "(Σm·ρ = 0)", size=12, color=FIELD, bold=True))
    f.append(text(O[0], O[1] + 32, "нова вісь", size=12, color=MUTED))

    b, w, h = textbox(W / 2, H - 40,
                      "J = Σm|ρ−d|²  =  Σmρ²  −  2d·Σmρ  +  d²·M  =  J_цм + M·d²",
                      size=14, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "steiner-proof.svg"), W, H, *f)


# ── Фігура: L не паралельний ω, окрім головної осі ────────────────────────────
def fig_l_omega():
    W, H = 880, 490
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Загальна вісь: L відхиляється від ω.   Головна вісь: L ∥ ω",
                  size=17, bold=True))
    f.append(line(445, 70, 445, 405, color=MUTED, sw=1.1, dash="4 6"))

    CL = (240, 275)
    f.append(line(CL[0], 120, CL[0], 400, color=MUTED, sw=1.3, dash="6 5"))
    f.append(arrow(CL[0], 235, CL[0], 125, color=NEG, sw=2.6))
    f.append(text(CL[0] - 16, 120, "ω", size=16, italic=True, bold=True, color=NEG))
    m1 = (296, 195); m2 = (184, 355)
    f.append(line(m1[0], m1[1], m2[0], m2[1], color=INK, sw=3.2))
    f.append(circle(m1[0], m1[1], 12, fill=POS, stroke=POS, sw=1))
    f.append(circle(m2[0], m2[1], 12, fill=POS, stroke=POS, sw=1))
    f.append(arrow(CL[0], CL[1], 162, 221, color=POS, sw=2.6))
    f.append(text(150, 208, "L", size=16, italic=True, bold=True, color=POS))
    b, w, h = textbox(CL[0], 448, "стрижень нахилений:\nL не вздовж ω → биття",
                      size=13, pad=9, fill=FILL, stroke=POS, sw=1.3, bold=True)
    f.append(b)

    CR = (655, 275)
    f.append(line(CR[0], 120, CR[0], 400, color=MUTED, sw=1.3, dash="6 5"))
    f.append(arrow(CR[0], 235, CR[0], 125, color=NEG, sw=2.6))
    f.append(text(CR[0] - 18, 120, "ω", size=16, italic=True, bold=True, color=NEG))
    r1 = (CR[0] + 98, 275); r2 = (CR[0] - 98, 275)
    f.append(line(r1[0], r1[1], r2[0], r2[1], color=INK, sw=3.2))
    f.append(circle(r1[0], r1[1], 12, fill=POS, stroke=POS, sw=1))
    f.append(circle(r2[0], r2[1], 12, fill=POS, stroke=POS, sw=1))
    f.append(arrow(CR[0] + 16, 250, CR[0] + 16, 140, color=POS, sw=2.6))
    f.append(text(CR[0] + 30, 150, "L", size=16, italic=True, bold=True, color=POS))
    b, w, h = textbox(CR[0], 448, "стрижень ⊥ осі (головна):\nL ∥ ω → чисте обертання",
                      size=13, pad=9, fill=FILL, stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "l-vs-omega.svg"), W, H, *f)


# ── Фігура: діагоналізація тензора двох мас (головні осі) ──────────────────────
def fig_principal():
    W, H = 880, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Головні осі: у повернутих осях тензор діагональний",
                  size=17, bold=True))

    O = (235, 235)
    f.append(arrow(O[0], O[1], 420, O[1], color=INK, sw=1.9))
    f.append(text(432, O[1] + 5, "x", size=14, italic=True, color=INK))
    f.append(arrow(O[0], O[1], O[0], 90, color=INK, sw=1.9))
    f.append(text(O[0], 80, "y", size=14, italic=True, color=INK))
    f.append(line(110, 360, 360, 110, color=FIELD, sw=2.0, dash="7 5"))
    f.append(line(135, 135, 335, 335, color=NEG, sw=2.0, dash="7 5"))
    f.append(text(372, 104, "e₁", size=14, bold=True, italic=True, color=FIELD))
    f.append(text(345, 352, "e₂", size=14, bold=True, italic=True, color=NEG))
    m1 = (335, 135); m2 = (135, 335)
    f.append(circle(m1[0], m1[1], 11, fill=POS, stroke=POS, sw=1))
    f.append(circle(m2[0], m2[1], 11, fill=POS, stroke=POS, sw=1))
    f.append(text(352, 152, "(a, a)", size=12, color=INK, anchor="start"))
    f.append(text(105, 360, "(−a, −a)", size=12, color=INK, anchor="end"))

    b1, w1, h1 = textbox(650, 148,
                         "осі x, y:\nвідцентровий J_xy = −2ma² ≠ 0\n(осі не головні)",
                         size=13, pad=10, fill="#fdecea", stroke=POS, sw=1.3, bold=True)
    f.append(b1)
    f.append(arrow(650, 195, 650, 262, color=INK, sw=2.2))
    f.append(text(748, 232, "поворот осей на 45°", size=12, color=MUTED))
    b2, w2, h2 = textbox(650, 318,
                         "головні осі e₁, e₂, e₃:\nJ₁ = 0,   J₂ = J₃ = 4ma²\nвідцентрові = 0",
                         size=13, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b2)
    return render(os.path.join(IMG, "principal-axes.svg"), W, H, *f)


# ── Фігура: стійкість — проміжна вісь зраджує (тенісна ракетка) ────────────────
def fig_intermediate():
    W, H = 900, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Стійкість вільного обертання навколо трьох головних осей",
                  size=17, bold=True))

    def book(cx, cy, w, h):
        dx, dy = 18, -12
        x0, y0 = cx - w / 2, cy - h / 2
        x1, y1 = cx + w / 2, cy - h / 2
        x3, y3 = cx + w / 2, cy + h / 2
        out = rect(x0, y0, w, h, fill="#eef2fb", stroke=INK, sw=2, rx=3)
        out += line(x0, y0, x0 + dx, y0 + dy, color=INK, sw=1.6)
        out += line(x1, y1, x1 + dx, y1 + dy, color=INK, sw=1.6)
        out += line(x3, y3, x3 + dx, y3 + dy, color=INK, sw=1.6)
        out += line(x0 + dx, y0 + dy, x1 + dx, y1 + dy, color=INK, sw=1.6)
        out += line(x1 + dx, y1 + dy, x1 + dx, y3 + dy, color=INK, sw=1.6)
        out += line(cx - w / 2 + 9, y0 + 8, cx - w / 2 + 9, y3 - 8, color=MUTED, sw=1.1)
        return out

    def tag(cx, txt, col):
        b, w, h = textbox(cx, 312, txt, size=13, pad=9, fill=FILL, stroke=col, sw=1.4, bold=True)
        f.append(b)

    f.append(book(150, 195, 104, 60))
    f.append(arrow(64, 195, 236, 195, color=FIELD, sw=3.0))
    f.append(text(246, 190, "ê₁", size=14, bold=True, italic=True, color=FIELD, anchor="start"))
    tag(150, "довга вісь (J мін)\nСТІЙКА", FIELD)

    f.append(book(450, 195, 104, 60))
    f.append(arrow(450, 268, 450, 122, color=POS, sw=3.0))
    f.append(text(466, 128, "ê₂", size=14, bold=True, italic=True, color=POS, anchor="start"))
    f.append(arc_arrow(536, 195, 30, 115, -115, color=POS, sw=2.6, head=9))
    f.append(text(590, 199, "180°", size=12, bold=True, color=POS))
    tag(450, "проміжна вісь\nНЕСТІЙКА — переворот", POS)

    f.append(book(748, 195, 104, 60))
    f.append(arrow(704, 240, 806, 148, color=FIELD, sw=3.0))
    f.append(text(816, 146, "ê₃", size=14, bold=True, italic=True, color=FIELD, anchor="start"))
    tag(748, "⊥ обкладинки (J макс)\nСТІЙКА", FIELD)

    b, w, h = textbox(W / 2, H - 42,
                      "стійко ⟺ вісь найбільшого або найменшого J    ·    проміжна вісь завжди зривається",
                      size=13, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "intermediate-axis.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_build(), fig_hoop_disc(), fig_gallery(), fig_skater(),
          fig_center_oscillation(), fig_timeline(),
          fig_compose_arm(), fig_numeric_check(),
          fig_steiner(), fig_l_omega(), fig_principal(), fig_intermediate()]
    print("written:")
    for p in ps:
        print("  ", p)
