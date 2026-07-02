# -*- coding: utf-8 -*-
"""Фігури до детальної теми «Діоди» (guide/embedded).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b9770e"   # акцент-вузол
COOL = NEG
WARM = POS
GRN  = FIELD


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


# ── 1. Динамічний опір: нахил дотичної на експоненті ────────────────────────
def fig_dynamic_resistance():
    W, H = 720, 430
    ox, oy = 90, 350          # початок осей
    aw, ah = 560, 300         # довжина осей
    frags = []
    # осі
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))          # U →
    frags.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.8))          # I ↑
    frags.append(text(ox + aw - 4, oy + 24, "U на діоді", size=13, anchor="end", color=MUTED))
    frags.append(text(ox - 8, oy - ah + 6, "I", size=14, anchor="end", color=MUTED))

    # експонента I = Is*(e^(U/Ut)-1), намальована в умовних одиницях
    Ut = 0.026
    Is = 1e-9
    Umax = 0.75
    # масштаб: підберемо так, щоб при Umax струм = ah*0.92
    Imax = Is * (math.exp(Umax / Ut) - 1)
    ky = (ah * 0.92) / Imax
    kx = aw / Umax
    pts = []
    u = 0.0
    while u <= Umax + 1e-9:
        I = Is * (math.exp(u / Ut) - 1)
        pts.append((ox + u * kx, oy - I * ky))
        u += Umax / 260
    frags.append(polyline(pts, color=INK, sw=2.4))

    # дві робочі точки: малий струм і в 100× більший
    def pt(u):
        I = Is * (math.exp(u / Ut) - 1)
        return ox + u * kx, oy - I * ky, I

    u1 = 0.62
    u2 = u1 + Ut * math.log(100)   # у 100 разів більший струм
    x1, y1, I1 = pt(u1)
    x2, y2, I2 = pt(u2)

    # дотичні (нахил di/du = I/Ut → r_d = Ut/I у реальних одиницях; у px нахил = ky/kx*I/Ut)
    def tangent(u):
        x, y, I = pt(u)
        slope_px = (ky / kx) * (I / Ut)     # px по y на px по x
        dx = 46
        return [(x - dx, y + slope_px * dx), (x + dx, y - slope_px * dx)]

    frags.append(polyline(tangent(u1), color=COOL, sw=2.2))
    frags.append(polyline(tangent(u2), color=WARM, sw=2.2))
    frags.append(circle(x1, y1, 4.5, fill=COOL, stroke=COOL))
    frags.append(circle(x2, y2, 4.5, fill=WARM, stroke=WARM))

    b, w, h = textbox(x1 - 120, y1 - 10, ["мала I:", "полога дотична", "великий r_d"],
                      size=12, color=COOL, stroke=COOL, pad=7)
    frags.append(b)
    b, w, h = textbox(x2 - 96, y2 + 70, ["велика I:", "крута дотична", "малий r_d"],
                      size=12, color=WARM, stroke=WARM, pad=7)
    frags.append(b)

    b, w, h = textbox(ox + aw * 0.30, oy - ah + 30, "r_d = n·U_T / I", size=15, bold=True,
                      color=GOLD, stroke=GOLD, pad=9)
    frags.append(b)

    render(os.path.join(IMG, 'dynamic-resistance.svg'), W, H, *frags,
           title="Динамічний опір — це нахил ВАХ у робочій точці")


# ── 2. Паралельні діоди: розбіг ВАХ і «загарбання» струму ───────────────────
def fig_parallel_sharing():
    W, H = 720, 430
    ox, oy = 90, 350
    aw, ah = 560, 300
    frags = []
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    frags.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    frags.append(text(ox + aw - 4, oy + 24, "U (спільна на обох)", size=13, anchor="end", color=MUTED))
    frags.append(text(ox - 8, oy - ah + 6, "I", size=14, anchor="end", color=MUTED))

    Ut = 0.026
    Umax = 0.75
    kx = aw / Umax

    # два діоди: у «гарячого» Is трохи більший (нижче падіння на той самий струм)
    def curve(Is, ky):
        pts = []
        u = 0.0
        while u <= Umax + 1e-9:
            I = Is * (math.exp(u / Ut) - 1)
            pts.append((ox + u * kx, oy - I * ky))
            u += Umax / 260
        return pts

    Is_a = 1e-9
    Is_b = 3e-9          # діод B «легше» відкривається (більший Is) → загрібає струм
    Imax = Is_b * (math.exp(Umax / Ut) - 1)
    ky = (ah * 0.9) / Imax

    frags.append(polyline(curve(Is_a, ky), color=COOL, sw=2.4))
    frags.append(polyline(curve(Is_b, ky), color=WARM, sw=2.4))

    # спільна робоча напруга U*
    Ustar = 0.66
    xline = ox + Ustar * kx
    frags.append(line(xline, oy, xline, oy - ah, color=MUTED, sw=1.2, dash="5 5"))
    Ia = Is_a * (math.exp(Ustar / Ut) - 1)
    Ib = Is_b * (math.exp(Ustar / Ut) - 1)
    ya = oy - Ia * ky
    yb = oy - Ib * ky
    frags.append(circle(xline, ya, 4.5, fill=COOL, stroke=COOL))
    frags.append(circle(xline, yb, 4.5, fill=WARM, stroke=WARM))
    # горизонтальні виноски струмів
    frags.append(line(ox, ya, xline, ya, color=COOL, sw=1.0, dash="3 4"))
    frags.append(line(ox, yb, xline, yb, color=WARM, sw=1.0, dash="3 4"))
    frags.append(text(xline + 6, oy - 6, "спільна U", size=12, anchor="start", color=MUTED))

    b, w, h = textbox(ox + aw * 0.66, oy - ah * 0.30, ["діод B (гарячіший):", "загрібає більший струм"],
                      size=12, color=WARM, stroke=WARM, pad=7)
    frags.append(b)
    b, w, h = textbox(ox + aw * 0.66, oy - ah * 0.66, ["діод A (холодніший):", "лишається майже без струму"],
                      size=12, color=COOL, stroke=COOL, pad=7)
    frags.append(b)

    render(os.path.join(IMG, 'parallel-sharing.svg'), W, H, *frags,
           title="Паралельні діоди: за однакової напруги струм ділиться нерівно")


# ── 3. Зворотне відновлення: заряд, di/dt, пік, м'який/різкий хвіст ──────────
def fig_reverse_recovery():
    W, H = 760, 430
    ox, oy = 80, 210          # нульова лінія струму — посередині
    aw = 620
    frags = []
    # осі
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))          # t →
    frags.append(line(ox, 40, ox, 380, color=INK, sw=1.6))             # I ↑↓
    frags.append(text(ox + aw - 2, oy - 8, "час", size=13, anchor="end", color=MUTED))
    frags.append(text(ox - 10, 52, "I", size=14, anchor="end", color=MUTED))
    frags.append(text(ox - 12, oy + 4, "0", size=12, anchor="end", color=MUTED))

    IF_y = oy - 120           # рівень прямого струму
    IRM_y = oy + 95           # рівень піка зворотного струму

    # 1) прямий струм (плато)
    t0 = ox + 30
    t1 = ox + 190             # початок спаду
    frags.append(polyline([(t0, IF_y), (t1, IF_y)], color=GRN, sw=2.6))
    frags.append(text(t0 + 4, IF_y - 10, "I_F", size=13, anchor="start", color=GRN, bold=True))

    # 2) лінійний спад зі швидкістю di/dt, проходить нуль
    t_zero = t1 + 90          # де перетинає нуль
    t_min = t_zero + 55       # де пік зворотного
    frags.append(polyline([(t1, IF_y), (t_min, IRM_y)], color=INK, sw=2.6))
    # позначка нахилу di/dt
    frags.append(text((t1 + t_zero) / 2 + 6, (IF_y + oy) / 2 - 8, "нахил = di/dt",
                      size=12, anchor="start", color=MUTED, ))

    # 3) хвіст: різкий (snappy) і м'який (soft)
    t_end_soft = t_min + 160
    t_end_snap = t_min + 55
    # snappy — різко назад до нуля
    frags.append(polyline([(t_min, IRM_y), (t_min + 18, oy + 10), (t_end_snap, oy)],
                          color=WARM, sw=2.4))
    # soft — плавно
    soft = [(t_min, IRM_y)]
    n = 30
    for i in range(1, n + 1):
        tt = t_min + (t_end_soft - t_min) * i / n
        # експоненційне згасання від IRM_y до oy
        frac = math.exp(-3.0 * i / n)
        soft.append((tt, oy + (IRM_y - oy) * frac))
    frags.append(polyline(soft, color=COOL, sw=2.4))

    # рівень -I_RM
    frags.append(line(ox, IRM_y, t_min, IRM_y, color=MUTED, sw=1.0, dash="4 4"))
    frags.append(text(ox + 4, IRM_y + 16, "−I_RM", size=12, anchor="start", color=MUTED))

    # штрихування площі Q_rr (спрощений трикутник під віссю до soft-хвоста)
    tri = [(t_zero, oy), (t_min, IRM_y), (t_min + 60, oy)]
    poly = '<polygon points="%s" fill="%s" fill-opacity="0.14" stroke="none"/>' % (
        " ".join("%.1f,%.1f" % (x, y) for x, y in tri), WARM)
    frags.append(poly)
    b, w, h = textbox(t_min + 6, oy + 50, "площа = Q_rr", size=12, color=WARM, stroke=WARM, pad=6)
    frags.append(b)

    # мітки t_rr
    frags.append(line(t_zero, oy + 118, t_end_soft, oy + 118, color=INK, sw=1.0))
    frags.append(line(t_zero, oy + 112, t_zero, oy + 124, color=INK, sw=1.0))
    frags.append(line(t_end_soft, oy + 112, t_end_soft, oy + 124, color=INK, sw=1.0))
    frags.append(text((t_zero + t_end_soft) / 2, oy + 138, "t_rr", size=13, bold=True))

    # легенда хвостів
    b, w, h = textbox(t_end_soft + 8, IRM_y - 40, ["м'який", "(soft)"], size=12,
                      color=COOL, stroke=COOL, pad=6)
    frags.append(b)
    b, w, h = textbox(t_end_soft + 8, oy - 40, ["різкий", "(snappy)"], size=12,
                      color=WARM, stroke=WARM, pad=6)
    frags.append(b)

    render(os.path.join(IMG, 'reverse-recovery.svg'), W, H, *frags,
           title="Зворотне відновлення: спад di/dt, пік −I_RM і хвіст (Q_rr)")


# ── 4. Ємність діода vs зміщення: бар'єрна падає, дифузійна росте ────────────
def fig_capacitance():
    W, H = 720, 430
    cx = 360
    oy = 350
    ah = 290
    half = 250
    frags = []
    # вісь напруги: ліворуч зворотна, праворуч пряма; нуль по центру
    frags.append(line(cx - half, oy, cx + half, oy, color=INK, sw=1.8))
    frags.append(line(cx, 60, cx, oy + 8, color=INK, sw=1.4, dash="4 4"))
    frags.append(text(cx, oy + 24, "0", size=12, color=MUTED))
    frags.append(text(cx - half + 4, oy + 24, "← зворотна U", size=13, anchor="start", color=MUTED))
    frags.append(text(cx + half - 4, oy + 24, "пряма U →", size=13, anchor="end", color=MUTED))
    frags.append(text(cx - half - 6, 74, "C", size=14, anchor="end", color=MUTED))

    # бар'єрна (junction) ємність: C ∝ 1/(Vbi - U)^(1/2); росте до нуля й далі в пряму
    Vbi = 0.7
    kx = half / 5.0   # 5 умовних вольтів зворотної на пів-осі
    pts = []
    U = -5.0
    while U <= 0.55:
        val = 1.0 / math.sqrt(Vbi - U)     # умовні одиниці
        y = oy - val * 55
        x = cx + U * kx
        pts.append((x, y))
        U += 0.05
    frags.append(polyline(pts, color=COOL, sw=2.6))

    # дифузійна ємність: ~0 у зворотній, різко злітає в прямій (∝ e^(U/Ut))
    Ut = 0.026
    pts2 = []
    U = 0.30
    while U <= 0.66:
        val = 0.02 * math.exp((U - 0.30) / Ut) * 1e-3   # умовно
        y = oy - min(val, 4.6) * 55
        x = cx + U * kx
        pts2.append((x, y))
        U += 0.004
    frags.append(polyline(pts2, color=WARM, sw=2.6))

    b, w, h = textbox(cx - half * 0.55, oy - ah * 0.72,
                      ["бар'єрна C_j", "(зворотна): ∝ 1/√(V_bi−U)"],
                      size=12, color=COOL, stroke=COOL, pad=7)
    frags.append(b)
    b, w, h = textbox(cx + half * 0.30, oy - ah * 0.78,
                      ["дифузійна C_d", "(пряма): ∝ I·τ"],
                      size=12, color=WARM, stroke=WARM, pad=7)
    frags.append(b)
    b, w, h = textbox(cx, 92, "у зворотному зміщенні панує C_j — це вона задає f_відсічки",
                      size=12, color=INK, stroke=MUTED, pad=7)
    frags.append(b)

    render(os.path.join(IMG, 'capacitance.svg'), W, H, *frags,
           title="Ємність діода залежить від зміщення")


# ── 5. Тепловий зворотний зв'язок прямого падіння ───────────────────────────
def fig_thermal_runaway():
    W, H = 720, 360
    frags = []
    cx, cy = 360, 180
    r = 128
    # чотири вузли по колу
    nodes = [
        (cx, cy - r, ["T переходу ↑"], WARM),
        (cx + r + 30, cy, ["V_F ↓", "(−2 мВ/°C)"], COOL),
        (cx, cy + r, ["за сталої U —", "струм I ↑"], GOLD),
        (cx - r - 30, cy, ["втрати", "P = V_F·I ↑"], WARM),
    ]
    # стрілки по колу (за годинниковою)
    import math as _m
    pos = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    for i in range(4):
        x1, y1 = pos[i]
        x2, y2 = pos[(i + 1) % 4]
        # злегка підтягнути кінці до країв рамок
        ang = _m.atan2(y2 - y1, x2 - x1)
        frags.append(arrow(x1 + 26 * _m.cos(ang), y1 + 26 * _m.sin(ang),
                           x2 - 30 * _m.cos(ang), y2 - 30 * _m.sin(ang),
                           color=INK, sw=2.0))
    for (nx, ny, lbl, col) in nodes:
        b, w, h = textbox(nx, ny, lbl, size=12.5, color=col, stroke=col, bold=True, pad=8, min_w=110)
        frags.append(b)

    b, w, h = textbox(cx, cy, ["петля"], size=13, color=INK, stroke=MUTED, pad=8)
    frags.append(b)

    render(os.path.join(IMG, 'thermal-runaway.svg'), W, H, *frags,
           title="Петля теплового розгону прямого падіння")


# ── 6. Глибокий рівень золота проти мілких рівнів легування (для hist-вставки) ─
def fig_gold_deep_level():
    W, H = 760, 460
    frags = []
    # смуга забороненої зони: дно (валентна) внизу, дах (провідності) вгорі
    bx, bw = 130, 380
    ec_y = 74          # край зони провідності (Ec)
    ev_y = 360         # край валентної зони (Ev)
    # заливка «зони провідності» і «валентної зони»
    frags.append(rect(bx, ec_y - 34, bw, 34, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=3))
    frags.append(rect(bx, ev_y, bw, 34, fill="#fdecea", stroke=POS, sw=1.4, rx=3))
    frags.append(text(bx + bw + 12, ec_y - 12, "зона провідності E_c", size=12.5,
                      anchor="start", color=NEG, bold=True))
    frags.append(text(bx + bw + 12, ev_y + 22, "валентна зона E_v", size=12.5,
                      anchor="start", color=POS, bold=True))
    # заборонена зона між ними
    frags.append(line(bx, ec_y, bx + bw, ec_y, color=NEG, sw=1.2, dash="4 4"))
    frags.append(line(bx, ev_y, bx + bw, ev_y, color=POS, sw=1.2, dash="4 4"))
    frags.append(text(bx - 12, (ec_y + ev_y) / 2, "1.12 еВ", size=13, anchor="end",
                      color=MUTED))
    # двобічна стрілка ширини щілини
    frags.append(arrow(bx - 40, ec_y, bx - 40, ev_y, color=MUTED, sw=1.4))
    frags.append(arrow(bx - 40, ev_y, bx - 40, ec_y, color=MUTED, sw=1.4))

    gap = ev_y - ec_y
    # мілкий донор (фосфор) — трохи нижче Ec
    don_y = ec_y + gap * 0.06
    frags.append(line(bx + 40, don_y, bx + 150, don_y, color=NEG, sw=3))
    frags.append(text(bx + 95, don_y - 8, "мілкий донор (P)", size=11.5, color=NEG))
    # мілкий акцептор (бор) — трохи вище Ev
    acc_y = ev_y - gap * 0.06
    frags.append(line(bx + 40, acc_y, bx + 150, acc_y, color=POS, sw=3))
    frags.append(text(bx + 95, acc_y + 16, "мілкий акцептор (B)", size=11.5, color=POS))

    # ГЛИБОКИЙ рівень золота — майже посередині
    au_y = ec_y + gap * 0.48         # ~0.54 еВ від Ec
    frags.append(line(bx + 205, au_y, bx + 355, au_y, color=GOLD, sw=4))
    b, w, h = textbox(bx + 280, au_y - 30, ["глибокий рівень Au", "≈0.54 еВ від E_c"],
                      size=12, color=GOLD, stroke=GOLD, bold=True, pad=7)
    frags.append(b)

    # стрілки-«сходинки» рекомбінації через глибокий рівень
    xr = bx + 280
    frags.append(arrow(xr, ec_y + 2, xr, au_y - 4, color=INK, sw=1.8))     # e зверху ↓
    frags.append(arrow(xr, ev_y - 2, xr, au_y + 4, color=INK, sw=1.8))     # h знизу ↑ (діра)
    frags.append(text(xr + 10, (ec_y + au_y) / 2, "e⁻", size=12, anchor="start", color=NEG, bold=True))
    frags.append(text(xr + 10, (ev_y + au_y) / 2, "h⁺", size=12, anchor="start", color=POS, bold=True))

    # підпис-висновок
    b, w, h = textbox(W / 2, ev_y + 74,
                      "мілкі рівні — легування; глибокий рівень Au — «пастка» посередині, що гасить носіїв",
                      size=12, color=INK, stroke=MUTED, pad=8)
    frags.append(b)

    render(os.path.join(IMG, 'gold-deep-level.svg'), W, H, *frags,
           title="Чому золото прискорює діод: глибокий рівень у середині щілини")


# ══════════════════════════════════════════════════════════════════════════
#  Фігури до математичної вставки «Заряд-контроль» (math-charge-control.md)
# ══════════════════════════════════════════════════════════════════════════

# ── M1. Заряд-контроль як бак: приплив струму − стік рекомбінації ────────────
def fig_charge_bucket():
    """Баланс неосновного заряду в базі: рівняння неперервності dQ/dt = i − Q/τ
    показане як бак із припливом (струм) і стоком (рекомбінація ∝ Q/τ)."""
    W, H = 720, 390
    frags = []
    bx, by, bw, bh = 275, 96, 170, 196
    frags.append(rect(bx, by, bw, bh, fill="#eef3fb", stroke=NEG, sw=2.2, rx=10))
    lvl = by + 66
    frags.append(rect(bx + 6, lvl, bw - 12, by + bh - lvl - 6,
                      fill="#cfe0f7", stroke="none", rx=6))
    frags.append(text(bx + bw / 2, lvl + 52, "Q = I_F·τ", size=18, bold=True, color=NEG))
    frags.append(text(bx + bw / 2, lvl + 76, "запас заряду", size=12, color=MUTED))
    frags.append(text(bx + bw / 2, lvl + 92, "у базі", size=12, color=MUTED))

    # приплив зверху — струм i(t)
    frags.append(arrow(bx + bw / 2, 46, bx + bw / 2, by - 2, color=FIELD, sw=3.0))
    b, w, h = textbox(bx + bw / 2, 34, "приплив: струм i(t)", size=13,
                      color=FIELD, stroke=FIELD, bold=True, pad=7)
    frags.append(b)

    # стік знизу — рекомбінація Q/τ
    frags.append(arrow(bx + bw / 2, by + bh + 2, bx + bw / 2, by + bh + 42,
                       color=POS, sw=3.0))
    b, w, h = textbox(bx + bw / 2, by + bh + 60, "стік: рекомбінація Q/τ",
                      size=13, color=POS, stroke=POS, bold=True, pad=7)
    frags.append(b)

    # рівняння балансу ліворуч
    b, w, h = textbox(120, by + 30, ["рівняння", "неперервності:"], size=13,
                      color=INK, stroke=MUTED, pad=8)
    frags.append(b)
    b, w, h = textbox(120, by + 104, "dQ/dt = i − Q/τ", size=15, bold=True,
                      color=GOLD, stroke=GOLD, pad=9, min_w=175)
    frags.append(b)

    # рівновага праворуч
    b, w, h = textbox(602, by + 44, ["рівновага:", "приплив = стік"], size=13,
                      color=INK, stroke=MUTED, pad=8)
    frags.append(b)
    b, w, h = textbox(602, by + 122, ["I_F = Q/τ", "⇒ Q = I_F·τ"], size=14, bold=True,
                      color=NEG, stroke=NEG, pad=9, min_w=155)
    frags.append(b)

    render(os.path.join(IMG, 'charge-bucket.svg'), W, H, *frags,
           title="Накопичений заряд — баланс припливу струму й стоку рекомбінації")


# ── M2. Геометрія Q_rr: трикутник, катети t_a/t_b, softness ──────────────────
def fig_qrr_triangle():
    """Форма зворотного струму як трикутник: катет виносу t_a (нахил di/dt до
    −I_RM) і хвіст t_b (спад до нуля). Площа = Q_rr; softness S = t_b/t_a."""
    W, H = 760, 410
    ox, oy = 92, 150          # нульова лінія струму
    aw = 608
    frags = []
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    frags.append(line(ox, 60, ox, 300, color=INK, sw=1.6))
    frags.append(text(ox + aw - 2, oy - 8, "час", size=13, anchor="end", color=MUTED))
    frags.append(text(ox - 10, 72, "I", size=14, anchor="end", color=MUTED))
    frags.append(text(ox - 12, oy + 4, "0", size=12, anchor="end", color=MUTED))

    IF_y = oy - 58
    IRM_y = oy + 120          # рівень піка −I_RM

    # плато I_F
    t0 = ox + 20
    t1 = ox + 150
    frags.append(polyline([(t0, IF_y), (t1, IF_y)], color=FIELD, sw=2.6))
    frags.append(text(t0 + 2, IF_y - 10, "I_F", size=13, anchor="start", color=FIELD, bold=True))

    # спад di/dt через нуль до піка (катет t_a)
    t_zero = t1 + 95
    t_min = t_zero + 58
    frags.append(polyline([(t1, IF_y), (t_min, IRM_y)], color=INK, sw=2.8))

    # хвіст t_b (soft) назад до нуля
    t_end = t_min + 150
    soft = [(t_min, IRM_y)]
    n = 26
    for i in range(1, n + 1):
        tt = t_min + (t_end - t_min) * i / n
        frac = math.exp(-2.6 * i / n)
        soft.append((tt, oy + (IRM_y - oy) * frac))
    frags.append(polyline(soft, color=INK, sw=2.8))

    # заливка трикутника заряду
    tri = [(t_zero, oy), (t_min, IRM_y), (t_end, oy)]
    poly = '<polygon points="%s" fill="%s" fill-opacity="0.13" stroke="none"/>' % (
        " ".join("%.1f,%.1f" % (x, y) for x, y in tri), NEG)
    frags.append(poly)
    b, w, h = textbox((t_zero + t_end) / 2, oy + 52, "площа = Q_rr", size=13,
                      color=NEG, stroke=NEG, bold=True, pad=7)
    frags.append(b)

    # рівень −I_RM + пунктир
    frags.append(line(ox, IRM_y, t_min, IRM_y, color=MUTED, sw=1.0, dash="4 4"))
    frags.append(text(ox + 4, IRM_y - 8, "−I_RM", size=12, anchor="start", color=MUTED))
    frags.append(circle(t_min, IRM_y, 4.0, fill=POS, stroke=POS))

    # позначка нахилу di/dt на катеті виносу
    b, w, h = textbox((t1 + t_zero) / 2 - 6, (IF_y + oy) / 2 - 24, "нахил di/dt",
                      size=12, color=MUTED, stroke=MUTED, pad=6)
    frags.append(b)

    # мітки t_a і t_b знизу
    yb = oy + 140
    frags.append(line(t_zero, yb, t_min, yb, color=NEG, sw=1.4))
    frags.append(line(t_zero, yb - 5, t_zero, yb + 5, color=NEG, sw=1.2))
    frags.append(line(t_min, yb - 5, t_min, yb + 5, color=NEG, sw=1.2))
    frags.append(text((t_zero + t_min) / 2, yb + 18, "t_a", size=13, bold=True, color=NEG))

    frags.append(line(t_min, yb, t_end, yb, color=POS, sw=1.4))
    frags.append(line(t_end, yb - 5, t_end, yb + 5, color=POS, sw=1.2))
    frags.append(text((t_min + t_end) / 2, yb + 18, "t_b", size=13, bold=True, color=POS))

    # повний t_rr
    yr = yb + 40
    frags.append(line(t_zero, yr, t_end, yr, color=INK, sw=1.2))
    frags.append(line(t_zero, yr - 5, t_zero, yr + 5, color=INK, sw=1.0))
    frags.append(line(t_end, yr - 5, t_end, yr + 5, color=INK, sw=1.0))
    frags.append(text((t_zero + t_end) / 2, yr + 18, "t_rr = t_a + t_b", size=13, bold=True))

    # softness праворуч
    b, w, h = textbox(t_end + 4, IRM_y, ["softness", "S = t_b / t_a"], size=12,
                      color=GOLD, stroke=GOLD, bold=True, pad=7)
    frags.append(b)

    render(os.path.join(IMG, 'qrr-triangle.svg'), W, H, *frags,
           title="Геометрія Q_rr: катет виносу t_a, хвіст t_b, softness")


if __name__ == '__main__':
    fig_dynamic_resistance()
    fig_parallel_sharing()
    fig_reverse_recovery()
    fig_capacitance()
    fig_thermal_runaway()
    fig_gold_deep_level()
    fig_charge_bucket()
    fig_qrr_triangle()
    print("OK: figures written to", IMG)
