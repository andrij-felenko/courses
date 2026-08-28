# -*- coding: utf-8 -*-
"""Фігури до теми «Фізика фотоприймача».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (scripts/svgkit.py)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Механізм фотодетекції: поглинання, генерація пар і поділ полем ────────
def fig_photodetection_mechanism():
    W, H = 820, 480
    f = [text(W / 2, 28, "Внутрішній фотоефект і поділ носіїв у p-n переході", size=16, bold=True)]

    # Верхня частина: фізична структура напівпровідника
    top_y = 55
    sx = 70
    pw, dw, nw = 140, 200, 340
    h_layer = 150

    # p-шар (тонкий анод)
    f.append(rect(sx, top_y, pw, h_layer, fill="#fdecea", stroke=POS, sw=1.8, rx=0))
    f.append(text(sx + pw / 2, top_y + 24, "p⁺-шар (анод)", size=13, bold=True, color=POS))
    f.append(text(sx + pw / 2, top_y + 44, "висока концентрація дірок", size=10, color=MUTED))

    # Збіднена область W (depletion region)
    dx = sx + pw
    f.append(rect(dx, top_y, dw, h_layer, fill="#eef8f2", stroke=FIELD, sw=2.0, rx=0))
    f.append(text(dx + dw / 2, top_y + 24, "Збіднена область (W)", size=13, bold=True, color=FIELD))
    f.append(text(dx + dw / 2, top_y + 44, "сильне вбудоване поле E", size=10, color=FIELD))

    # n-шар (підкладка / катод)
    nx = dx + dw
    f.append(rect(nx, top_y, nw, h_layer, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=0))
    f.append(text(nx + nw / 2, top_y + 24, "n-база / підкладка (катод)", size=13, bold=True, color=NEG))
    f.append(text(nx + nw / 2, top_y + 44, "основні носії — електрони", size=10, color=MUTED))

    # Стрілка напруженості електричного поля E у збідненій зоні (напрямлена від n до p)
    f.append(line(nx - 20, top_y + 70, dx + 20, top_y + 70, color=FIELD, sw=2.2))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (dx + 20, top_y + 70, dx + 32, top_y + 64, dx + 32, top_y + 76, FIELD))
    f.append(text(dx + dw / 2, top_y + 64, "Електричне поле  E (від n⁺ до p⁺)", size=11, bold=True, color=FIELD))

    # Падаюче світло (фотони) згори
    for k in range(4):
        lx = sx + 40 + k * 80
        f.append(line(lx, top_y - 22, lx + 15, top_y + 10, color="#d48806", sw=2.2, dash="4,3"))
        f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                 % (lx + 15, top_y + 10, lx + 7, top_y + 2, lx + 16, top_y - 1, "#d48806"))
    f.append(text(sx + 150, top_y - 14, "Падаючі фотони (h·ν ≥ Eg)", size=12, bold=True, color="#b8801f"))

    # Процес 1 у збідненій зоні: генерація і швидкий дрейф
    gx1, gy1 = dx + 70, top_y + 105
    f.append(circle(gx1, gy1, 6, fill="#ffe58f", stroke="#d48806", sw=1.5))
    f.append(text(gx1, gy1 - 10, "h·ν", size=9, bold=True, color="#b8801f"))
    # електрон дрейфує вправо до n
    f.append(circle(gx1 + 55, gy1, 8, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(gx1 + 55, gy1 + 4, "e⁻", size=10, bold=True, color=NEG))
    f.append(line(gx1 + 10, gy1, gx1 + 42, gy1, color=NEG, sw=1.6))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (gx1 + 44, gy1, gx1 + 36, gy1 - 3.5, gx1 + 36, gy1 + 3.5, NEG))
    # дірка дрейфує вліво до p
    f.append(circle(gx1 - 45, gy1, 8, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(gx1 - 45, gy1 + 4, "h⁺", size=10, bold=True, color=POS))
    f.append(line(gx1 - 10, gy1, gx1 - 32, gy1, color=POS, sw=1.6))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (gx1 - 34, gy1, gx1 - 26, gy1 - 3.5, gx1 - 26, gy1 + 3.5, POS))
    f.append(text(dx + dw / 2, gy1 + 28, "Швидкий дрейф (пікосекунди, t_drift = W / v_sat)", size=10.5, color=FIELD, bold=True))

    # Процес 2 в глибині n-бази: повільна дифузія
    gx2, gy2 = nx + 130, top_y + 105
    f.append(circle(gx2, gy2, 6, fill="#ffe58f", stroke="#d48806", sw=1.5))
    f.append(text(gx2, gy2 - 10, "h·ν", size=9, bold=True, color="#b8801f"))
    # дірка дифундує хвилясто вліво
    f.append(circle(gx2 - 55, gy2, 8, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(gx2 - 55, gy2 + 4, "h⁺", size=10, bold=True, color=POS))
    f.append(line(gx2 - 10, gy2, gx2 - 42, gy2, color=POS, sw=1.5, dash="3,2"))
    f.append(text(nx + 130, gy2 + 28, "Повільна дифузія (наносекунди, t_diff ≈ d² / 2D)", size=10, color=MUTED))

    # Нижня частина: Зонна діаграма (Band diagram)
    by = 280
    bh = 135
    f.append(rect(sx, by, pw + dw + nw, bh, fill="#fafbfc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(sx + 15, by + 20, "Зонна енергетична діаграма", size=12, bold=True, color=INK, anchor="start"))

    # Лінії зон Ec та Ev
    ec_p, ec_n = by + 40, by + 95
    ev_p, ev_n = by + 75, by + 130

    # Зона провідності Ec
    pts_ec = [
        f"{sx},{ec_p}",
        f"{dx},{ec_p}",
        f"{dx + dw},{ec_n}",
        f"{nx + nw},{ec_n}"
    ]
    f.append(f'<polyline points="{" ".join(pts_ec)}" fill="none" stroke="{NEG}" stroke-width="2.4"/>')
    f.append(text(nx + nw - 10, ec_n - 6, "Зона провідності  Ec", size=11, bold=True, color=NEG, anchor="end"))

    # Валентна зона Ev
    pts_ev = [
        f"{sx},{ev_p}",
        f"{dx},{ev_p}",
        f"{dx + dw},{ev_n}",
        f"{nx + nw},{ev_n}"
    ]
    f.append(f'<polyline points="{" ".join(pts_ev)}" fill="none" stroke="{POS}" stroke-width="2.4"/>')
    f.append(text(nx + nw - 10, ev_n + 16, "Валентна зона  Ev", size=11, bold=True, color=POS, anchor="end"))

    # Позначення забороненої зони Eg у p-шарі
    f.append(line(sx + 35, ec_p, sx + 35, ev_p, color="#722ed1", sw=1.6))
    f.append(text(sx + 45, (ec_p + ev_p) / 2 + 4, "Eg (1.12 еВ)", size=10, bold=True, color="#722ed1", anchor="start"))

    # Падіння потенціалу q*(V_bi + V_R)
    f.append(line(dx + dw + 30, ec_p, dx + dw + 30, ec_n, color=FIELD, sw=1.6, dash="3,3"))
    f.append(text(dx + dw + 38, (ec_p + ec_n) / 2 + 4, "q·(V_bi + V_R)", size=10.5, bold=True, color=FIELD, anchor="start"))

    # Фотонне збудження на діаграмі у збідненій зоні
    ph_x = dx + 90
    f.append(line(ph_x, (ev_p + ev_n)/2, ph_x, (ec_p + ec_n)/2, color="#d48806", sw=2.2))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (ph_x, (ec_p + ec_n)/2, ph_x - 4, (ec_p + ec_n)/2 + 8, ph_x + 4, (ec_p + ec_n)/2 + 8, "#d48806"))
    f.append(text(ph_x - 8, (ec_p + ev_p + ec_n + ev_n)/4 + 4, "h·ν", size=10, bold=True, color="#b8801f", anchor="end"))

    # Електрон котиться вниз по схилу до n-зони
    f.append(circle(ph_x + 35, (ec_p + ec_n)/2 + 10, 6, fill="#eaf0fd", stroke=NEG, sw=1.6))
    f.append(text(ph_x + 35, (ec_p + ec_n)/2 + 13, "e⁻", size=9, bold=True, color=NEG))
    f.append(line(ph_x + 5, (ec_p + ec_n)/2 + 2, ph_x + 25, (ec_p + ec_n)/2 + 8, color=NEG, sw=1.5))

    # Дірка спливає вгору по схилу до p-зони
    f.append(circle(ph_x - 35, (ev_p + ev_n)/2 - 10, 6, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(ph_x - 35, (ev_p + ev_n)/2 - 7, "h⁺", size=9, bold=True, color=POS))
    f.append(line(ph_x - 5, (ev_p + ev_n)/2 - 2, ph_x - 25, (ev_p + ev_n)/2 - 8, color=POS, sw=1.5))

    f.append(text(W / 2, H - 14,
                  "Поглинання кванта світла народжує пару e⁻/h⁺; вбудоване поле розносить носії у протилежні боки",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(IMG, "photodetection-mechanism.svg"), W, H, *f)


# ── 2. Спектральна чутливість різних матеріалів ──────────────────────────────
def fig_spectral_responsivity():
    W, H = 800, 440
    f = [text(W / 2, 28, "Спектральна чутливість R(λ) та червона межа фотоефекту", size=16, bold=True)]

    ox, oy = 85, 340
    axw, axh = 650, 260
    f.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw / 2, oy + 42, "Довжина хвилі  λ  (нм)", size=12, bold=True, color=INK))
    f.append(mtext(ox - 52, oy - axh / 2, ["Спектральна", "чутливість", "R(λ)  (А/Вт)"], size=11, bold=True, color=INK, lh=1.2))

    # X: 200 .. 1800 нм
    lam_min, lam_max = 200, 1800
    def X(lam):
        return ox + (lam - lam_min) / (lam_max - lam_min) * axw

    for lam in (200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800):
        f.append(line(X(lam), oy, X(lam), oy + 5, color=INK, sw=1.4))
        f.append(text(X(lam), oy + 20, str(lam), size=10, color=MUTED))

    # Y: 0.0 .. 1.2 А/Вт
    def Y(r_val):
        return oy - (r_val / 1.2) * axh

    for r_val in (0.2, 0.4, 0.6, 0.8, 1.0, 1.2):
        f.append(line(ox - 5, Y(r_val), ox, Y(r_val), color=INK, sw=1.4))
        f.append(text(ox - 10, Y(r_val) + 4, "%.1f" % r_val, size=10, color=MUTED, anchor="end"))

    # Смужки спектра (видимий)
    vis_x0, vis_x1 = X(400), X(700)
    f.append(rect(vis_x0, oy + 4, vis_x1 - vis_x0, 6, fill="#52c41a", stroke="none", sw=0, rx=0))
    f.append(text((vis_x0 + vis_x1)/2, oy + 32, "видимий", size=9, color="#389e0d"))

    # Теоретична ідеальна крива квантової ефективності η = 100%: R_ideal = q*λ/(h*c) = λ(мкм)/1.2398
    pts_ideal = []
    for l_val in range(200, 1500, 50):
        r_id = (l_val / 1000.0) / 1.2398
        pts_ideal.append(f"{X(l_val):.1f},{Y(r_id):.1f}")
    f.append(f'<polyline points="{" ".join(pts_ideal)}" fill="none" stroke="#8c8c8c" stroke-width="1.8" stroke-dasharray="5,4"/>')
    f.append(text(X(1150), Y((1.15/1.2398)) - 10, "Ідеальна межа (η = 100%)", size=10, color="#595959", bold=True))

    # 1. Кремній (Si)
    pts_si = [
        (300, 0.08), (400, 0.18), (500, 0.28), (600, 0.38), (700, 0.48),
        (800, 0.58), (900, 0.65), (960, 0.62), (1020, 0.45), (1060, 0.22), (1100, 0.04), (1120, 0.0)
    ]
    f_si = " ".join([f"{X(p[0]):.1f},{Y(p[1]):.1f}" for p in pts_si])
    f.append(f'<polyline points="{f_si}" fill="none" stroke="{NEG}" stroke-width="2.6"/>')
    f.append(text(X(850), Y(0.65) - 10, "Кремній (Si)", size=11, bold=True, color=NEG))
    f.append(text(X(1107), Y(0.04) - 22, "λ_max = 1107 нм", size=9.5, color=NEG))
    f.append(line(X(1107), Y(0.04) - 18, X(1107), Y(0.0), color=NEG, sw=1.2, dash="2,2"))

    # 2. InGaAs
    pts_ingaas = [
        (850, 0.20), (1000, 0.55), (1200, 0.75), (1310, 0.85), (1550, 0.98),
        (1600, 0.95), (1650, 0.70), (1680, 0.30), (1710, 0.0)
    ]
    f_ingaas = " ".join([f"{X(p[0]):.1f},{Y(p[1]):.1f}" for p in pts_ingaas])
    f.append(f'<polyline points="{f_ingaas}" fill="none" stroke="{POS}" stroke-width="2.6"/>')
    f.append(text(X(1500), Y(0.98) - 10, "InGaAs (телекомунікації)", size=11, bold=True, color=POS))
    f.append(text(X(1700), Y(0.30) - 14, "λ_max ≈ 1700 нм", size=9.5, color=POS))

    # 3. Германій (Ge)
    pts_ge = [
        (600, 0.20), (800, 0.35), (1000, 0.50), (1200, 0.62), (1400, 0.72),
        (1550, 0.75), (1700, 0.55), (1800, 0.15)
    ]
    f_ge = " ".join([f"{X(p[0]):.1f},{Y(p[1]):.1f}" for p in pts_ge])
    f.append(f'<polyline points="{f_ge}" fill="none" stroke="{FIELD}" stroke-width="2.2" stroke-dasharray="6,3"/>')
    f.append(text(X(1350), Y(0.72) + 18, "Германій (Ge)", size=10.5, bold=True, color=FIELD))

    # Пояснювальна плашка в лівому верхньому куті, де немає кривих
    b, _, _ = textbox(ox + 160, oy - axh + 50,
                      "R(λ) росте лінійно з λ, бо менша енергія фотона\nозначає більше фотонів на 1 Ват потужності.\nПри h·ν < Eg поглинання зникає (обвал до нуля).",
                      size=10.5, pad=8, fill="#fafbfc", stroke="#d9d9d9", sw=1.2)
    f.append(b)

    f.append(text(W / 2, H - 12,
                  "Спектральна чутливість визначається шириною забороненої зони Eg матеріалу та квантовим виходом",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(IMG, "spectral-responsivity.svg"), W, H, *f)


# ── 3. ВАХ фотодіода: Фотовольтаїчний (0 В) проти Фотопровідного (−VR) ────────
def fig_photodiode_iv_quadrants():
    W, H = 820, 480
    f = [text(W / 2, 28, "Вольт-амперна характеристика: фотовольтаїчний та фотопровідний режими", size=16, bold=True)]

    ox, oy = 460, 230
    L, R = 320, 180
    UP, DN = 140, 160

    f.append(line(ox - L, oy, ox + R, oy, color=INK, sw=1.8))
    f.append(line(ox, oy - UP, ox, oy + DN, color=INK, sw=1.8))
    f.append(text(ox + R + 10, oy + 4, "V (напруга)", size=12, bold=True, color=INK, anchor="start"))
    f.append(text(ox + 10, oy - UP - 6, "I (струм)", size=12, bold=True, color=INK, anchor="start"))

    f.append(text(ox - L + 20, oy - UP + 20, "II квадрант", size=10, color=MUTED, anchor="start"))
    f.append(text(ox + R - 20, oy - UP + 20, "I квадрант (пряме зміщення)", size=10, color=MUTED, anchor="end"))
    f.append(text(ox - L + 20, oy + DN - 20, "III квадрант (фотопровідний)", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(ox + R - 20, oy + DN - 20, "IV квадрант (генераторний)", size=11, bold=True, color=FIELD, anchor="end"))

    def draw_iv(iph_shift, col, sw=2.4, is_dark=False):
        pts = []
        for i in range(0, 140):
            v_px = -L + i * (L + R) / 139.0
            if v_px <= 0:
                cur_px = iph_shift + (abs(v_px)/L)*4.0
            else:
                cur_px = iph_shift + 3.0 * (2.718 ** (v_px / 32.0) - 1.0)
            y_px = oy + cur_px
            if y_px < oy - UP:
                pts.append(f"{(ox + v_px):.1f},{(oy - UP):.1f}")
                break
            if y_px > oy + DN:
                continue
            pts.append(f"{(ox + v_px):.1f},{y_px:.1f}")
        dash = ' stroke-dasharray="4,4"' if is_dark else ''
        f.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="{sw}"{dash}/>')

    draw_iv(0, "#8c8c8c", sw=2.0, is_dark=True)
    draw_iv(60, "#69c0ff", sw=2.2)
    draw_iv(120, NEG, sw=2.8)

    f.append(text(ox - 240, oy - 8, "Темнова крива (I_ph = 0)", size=10.5, color="#595959"))
    f.append(text(ox - 240, oy + 52, "Помірна освітленість P₁", size=10, color="#1890ff"))
    f.append(text(ox - 240, oy + 112, "Висока освітленість P₂ (P₂ > P₁)", size=10.5, bold=True, color=NEG))

    f.append(line(ox - 260, oy + 15, ox - 260, oy + 110, color="#d48806", sw=1.8))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (ox - 260, oy + 110, ox - 264, oy + 100, ox - 256, oy + 100, "#d48806"))
    f.append(text(ox - 275, oy + 65, "I_ph ∝ P_opt", size=10, bold=True, color="#b8801f", anchor="end"))

    pt1_x, pt1_y = ox, oy + 120
    f.append(circle(pt1_x, pt1_y, 6, fill="#ffffff", stroke=FIELD, sw=2.4))
    f.append(text(pt1_x + 12, pt1_y + 4, "V = 0 (Фотогальванічний)", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(pt1_x + 12, pt1_y + 18, "Нульовий темновий струм, малий шум", size=9.5, color=MUTED, anchor="start"))

    voc_x, voc_y = ox + 68, oy
    f.append(circle(voc_x, voc_y, 4, fill=FIELD, stroke=FIELD, sw=1.5))
    f.append(text(voc_x + 6, voc_y - 10, "V_oc", size=10.5, bold=True, color=FIELD))

    pt2_x, pt2_y = ox - 180, oy + 120 + 2.5
    f.append(circle(pt2_x, pt2_y, 6, fill="#ffffff", stroke=NEG, sw=2.4))
    f.append(text(pt2_x, pt2_y + 20, "V = −V_R (Фотопровідний)", size=11, bold=True, color=NEG, anchor="middle"))
    f.append(text(pt2_x, pt2_y + 34, "Мала ємність Cj, висока швидкодія (ГГц)", size=9.5, color=MUTED, anchor="middle"))

    idark_y = oy + 3.0
    f.append(circle(pt2_x, idark_y, 4, fill=POS, stroke=POS, sw=1.5))
    f.append(line(pt2_x, oy, pt2_x, idark_y, color=POS, sw=1.6))
    f.append(text(pt2_x - 10, idark_y + 14, "I_dark", size=10, bold=True, color=POS, anchor="end"))

    card_x = ox + 35
    f.append(rect(card_x, oy - UP + 30, 150, 68, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(card_x + 75, oy - UP + 48, "Режим V = 0", size=11, bold=True, color=FIELD))
    f.append(mtext(card_x + 75, oy - UP + 66, ["• I_dark = 0", "• C_j — максимальна", "• ідеальний для DC/люксметрів"], size=9, color=INK, lh=1.2))

    f.append(rect(card_x, oy - UP + 106, 150, 68, fill="#eef2f8", stroke=NEG, sw=1.4, rx=6))
    f.append(text(card_x + 75, oy - UP + 124, "Режим −V_R (зміщення)", size=11, bold=True, color=NEG))
    f.append(mtext(card_x + 75, oy - UP + 142, ["• C_j падає в рази", "• смуга до ГГц", "• є темновий струм I_dark"], size=9, color=INK, lh=1.2))

    f.append(text(W / 2, H - 12,
                  "Світло зміщує ВАХ вниз на величину I_ph; вибір робочої точки визначає баланс «шум проти швидкості»",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(IMG, "photodiode-iv-quadrants.svg"), W, H, *f)


# ── 4. Еквівалентна схема та частотний баланс швидкодії ──────────────────────
def fig_equivalent_circuit_bandwidth():
    W, H = 840, 470
    f = [text(W / 2, 28, "Еквівалентна схема фотодіода та компроміс смуги пропускання f_3dB", size=16, bold=True)]

    sx, sy = 50, 70
    sw_box, sh_box = 360, 340
    f.append(rect(sx, sy, sw_box, sh_box, fill="#fafbfc", stroke=LINE, sw=1.4, rx=8))
    f.append(text(sx + sw_box / 2, sy + 24, "Інженерна еквівалентна схема", size=13, bold=True, color=INK))

    top_wire = sy + 70
    bot_wire = sy + 260
    f.append(line(sx + 30, top_wire, sx + 270, top_wire, color=LINE, sw=1.8))
    f.append(line(sx + 30, bot_wire, sx + 270, bot_wire, color=LINE, sw=1.8))

    # 1. Джерело фотоструму I_ph
    c1_x = sx + 60
    f.append(line(c1_x, top_wire, c1_x, bot_wire, color=LINE, sw=1.8))
    f.append(circle(c1_x, (top_wire + bot_wire)/2, 16, fill="#ffffff", stroke="#d48806", sw=2.0))
    f.append(line(c1_x, (top_wire + bot_wire)/2 - 10, c1_x, (top_wire + bot_wire)/2 + 10, color="#d48806", sw=2.0))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (c1_x, (top_wire + bot_wire)/2 + 10, c1_x - 4, (top_wire + bot_wire)/2 + 2, c1_x + 4, (top_wire + bot_wire)/2 + 2, "#d48806"))
    f.append(text(c1_x, (top_wire + bot_wire)/2 + 30, "I_ph", size=11, bold=True, color="#b8801f"))

    # 2. Діод D (Шоклі)
    c2_x = sx + 125
    f.append(line(c2_x, top_wire, c2_x, bot_wire, color=LINE, sw=1.8))
    mid_y = (top_wire + bot_wire)/2
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#eaf0fd" stroke="%s" stroke-width="1.8"/>'
             % (c2_x - 12, mid_y + 10, c2_x + 12, mid_y + 10, c2_x, mid_y - 10, NEG))
    f.append(line(c2_x - 12, mid_y - 10, c2_x + 12, mid_y - 10, color=NEG, sw=2.0))
    f.append(text(c2_x, mid_y + 26, "D (Шоклі)", size=10, bold=True, color=NEG))

    # 3. Бар'єрна ємність C_j
    c3_x = sx + 190
    f.append(line(c3_x, top_wire, c3_x, bot_wire, color=LINE, sw=1.8))
    f.append(line(c3_x - 14, mid_y - 4, c3_x + 14, mid_y - 4, color=FIELD, sw=2.2))
    f.append(line(c3_x - 14, mid_y + 4, c3_x + 14, mid_y + 4, color=FIELD, sw=2.2))
    f.append(text(c3_x, mid_y + 24, "C_j(V_R)", size=10.5, bold=True, color=FIELD))

    # 4. Опір шунтування R_sh
    c4_x = sx + 255
    f.append(line(c4_x, top_wire, c4_x, bot_wire, color=LINE, sw=1.8))
    f.append(rect(c4_x - 10, mid_y - 16, 20, 32, fill="#ffffff", stroke="#595959", sw=1.6, rx=2))
    f.append(text(c4_x, mid_y + 28, "R_sh (ГОм)", size=10, color="#595959"))

    # Послідовний опір R_s
    f.append(line(sx + 270, top_wire, sx + 290, top_wire, color=LINE, sw=1.8))
    f.append(rect(sx + 290, top_wire - 8, 30, 16, fill="#ffffff", stroke=POS, sw=1.6, rx=2))
    f.append(text(sx + 305, top_wire - 14, "R_s (Ом)", size=9.5, bold=True, color=POS))
    f.append(line(sx + 320, top_wire, sx + 345, top_wire, color=LINE, sw=1.8))

    # Зовнішнє навантаження R_load
    f.append(line(sx + 345, top_wire, sx + 345, bot_wire, color=LINE, sw=1.8))
    f.append(rect(sx + 335, mid_y - 16, 20, 32, fill="#fff7e6", stroke="#d48806", sw=1.6, rx=2))
    f.append(text(sx + 345, mid_y + 28, "R_load", size=10, bold=True, color="#b8801f"))
    f.append(line(sx + 270, bot_wire, sx + 345, bot_wire, color=LINE, sw=1.8))

    f.append(mtext(sx + sw_box / 2, sy + 300,
                   ["RC-постійна кола:  τ_RC = (R_s + R_load) · C_j",
                    "R_sh ≫ R_load  (R_sh формує тепловий шум струму)"],
                   size=10.5, color=INK, lh=1.3))

    # Права частина: Графік компромісу смуги f_3dB від товщини W
    gx, gy = 460, sy
    gw_box, gh_box = 340, sh_box
    f.append(rect(gx, gy, gw_box, gh_box, fill="#ffffff", stroke=LINE, sw=1.4, rx=8))
    f.append(text(gx + gw_box / 2, gy + 24, "Компроміс швидкодії від товщини W", size=13, bold=True, color=INK))

    g_ox, g_oy = gx + 50, gy + 250
    g_w, g_h = 260, 180
    f.append(line(g_ox, g_oy, g_ox + g_w, g_oy, color=INK, sw=1.6))
    f.append(line(g_ox, g_oy, g_ox, g_oy - g_h, color=INK, sw=1.6))
    f.append(text(g_ox + g_w / 2, g_oy + 30, "Товщина збідненої зони  W", size=11, bold=True, color=INK))
    f.append(mtext(g_ox - 30, g_oy - g_h / 2, ["Частота", "зрізу f"], size=10.5, bold=True, color=INK, lh=1.2))

    # f_RC ∝ W
    pts_frc = []
    for i in range(10, 101, 5):
        w_rel = i / 100.0
        x_pt = g_ox + w_rel * g_w
        y_pt = g_oy - (w_rel * 0.85) * g_h
        pts_frc.append(f"{x_pt:.1f},{y_pt:.1f}")
    f.append(f'<polyline points="{" ".join(pts_frc)}" fill="none" stroke="{FIELD}" stroke-width="2.0" stroke-dasharray="4,3"/>')
    f.append(text(g_ox + g_w - 10, g_oy - 0.82 * g_h - 6, "f_RC ∝ W (мала Cj)", size=10, bold=True, color=FIELD, anchor="end"))

    # f_transit ∝ 1/W
    pts_ftransit = []
    for i in range(12, 101, 5):
        w_rel = i / 100.0
        x_pt = g_ox + w_rel * g_w
        val = 0.12 / w_rel
        y_pt = g_oy - min(val, 0.95) * g_h
        pts_ftransit.append(f"{x_pt:.1f},{y_pt:.1f}")
    f.append(f'<polyline points="{" ".join(pts_ftransit)}" fill="none" stroke="{NEG}" stroke-width="2.0" stroke-dasharray="4,3"/>')
    f.append(text(g_ox + 35, g_oy - 0.88 * g_h, "f_transit ∝ 1/W", size=10, bold=True, color=NEG, anchor="start"))

    # f_3dB
    pts_ftot = []
    for i in range(12, 101, 4):
        w_rel = i / 100.0
        f_rc = w_rel * 0.85
        f_tr = 0.12 / w_rel
        f_comb = 1.0 / ((1.0 / (f_rc**2) + 1.0 / (f_tr**2)) ** 0.5)
        x_pt = g_ox + w_rel * g_w
        y_pt = g_oy - f_comb * g_h
        pts_ftot.append(f"{x_pt:.1f},{y_pt:.1f}")
    f.append(f'<polyline points="{" ".join(pts_ftot)}" fill="none" stroke="{POS}" stroke-width="2.8"/>')
    f.append(text(g_ox + 130, g_oy - 0.52 * g_h - 10, "Результуюча f_3dB", size=11, bold=True, color=POS))

    # W_opt
    w_opt_x = g_ox + 0.38 * g_w
    w_opt_y = g_oy - 0.44 * g_h
    f.append(circle(w_opt_x, w_opt_y, 5, fill="#ffffff", stroke=POS, sw=2.2))
    f.append(line(w_opt_x, w_opt_y, w_opt_x, g_oy, color=POS, sw=1.4, dash="3,3"))
    f.append(text(w_opt_x, g_oy + 16, "W_opt", size=10.5, bold=True, color=POS))

    f.append(mtext(gx + gw_box / 2, gy + 300,
                   ["Максимум смуги досягається при балансі:",
                    "час дрейфу дорівнює RC-постійній кола"],
                   size=10.5, color=INK, lh=1.3))

    f.append(text(W / 2, H - 12,
                  "Смуга частот обмежена бар'єрною ємністю при малій товщині W та часом прольоту при великій W",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(IMG, "equivalent-circuit-bandwidth.svg"), W, H, *f)


if __name__ == "__main__":
    fig_photodetection_mechanism()
    fig_spectral_responsivity()
    fig_photodiode_iv_quadrants()
    fig_equivalent_circuit_bandwidth()
    print("OK: 4 figures ->", IMG)
