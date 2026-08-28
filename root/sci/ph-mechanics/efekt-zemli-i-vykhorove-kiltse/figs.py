# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

AIR_BLUE   = "#eaf2fb"
FLOW_BLUE  = "#2457d6"
VORTEX_RED = "#c0392b"
WARM_FILL  = "#fef5e7"
GREEN_ZONE = "#27ae60"

# ═══════════════════════════════════════════════════════════════════════════
# Фігура 1: Порівняння течії OGE (поза екраном) та IGE (в екрані землі)
# ═══════════════════════════════════════════════════════════════════════════
def fig_ground_effect_flow():
    W, H = 780, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, 'Структура струменя ротора: вільна течія (OGE) проти ефекту землі (IGE)',
                  15, INK, 'middle', bold=True))

    # Розділювач двох половин
    f.append(line(W / 2, 45, W / 2, H - 25, color=MUTED, sw=1.0, dash='4,4'))

    # Ліва панель: OGE
    f.append(text(W / 4, 52, 'Поза екраном (OGE: h > 2R)', 14, INK, 'middle', bold=True))
    f.append(text(W / 4, 70, 'Струмінь вільно стискається й розганяється вниз', 11, MUTED, 'middle'))

    # Ротор OGE
    r_x = W / 4
    r_y = 130
    rw = 90
    f.append(line(r_x - rw, r_y, r_x + rw, r_y, color=INK, sw=3.5))
    f.append(circle(r_x, r_y, 5, fill=INK, stroke=INK, sw=1))
    f.append(text(r_x, r_y - 12, 'Диск ротора (діаметр D = 2R)', 11, INK, 'middle', bold=True))

    # Струмінь OGE (пунктирні лінії звуження струменя)
    f.append(arrow(r_x, r_y + 8, r_x, r_y + 45, color=FLOW_BLUE, sw=2.0))
    f.append(text(r_x + 18, r_y + 30, 'v_i0', 12, FLOW_BLUE, 'start', italic=True))

    # Лінії току звуження
    d_oge_left = "M %d %d Q %d %d %d %d" % (r_x - rw, r_y, r_x - rw * 0.85, r_y + 70, r_x - rw * 0.70, r_y + 160)
    d_oge_right = "M %d %d Q %d %d %d %d" % (r_x + rw, r_y, r_x + rw * 0.85, r_y + 70, r_x + rw * 0.70, r_y + 160)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,3"/>' % (d_oge_left, FLOW_BLUE))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,3"/>' % (d_oge_right, FLOW_BLUE))

    # Стрілки швидкості у далекому сліді
    f.append(arrow(r_x, r_y + 100, r_x, r_y + 155, color=FLOW_BLUE, sw=2.2))
    f.append(text(r_x + 18, r_y + 135, 'w = 2 v_i0', 12, FLOW_BLUE, 'start', italic=True))

    # Кінцеві вихори OGE
    f.append(circle(r_x - rw * 0.78, r_y + 70, 7, fill='none', stroke=VORTEX_RED, sw=1.6))
    f.append(circle(r_x + rw * 0.78, r_y + 70, 7, fill='none', stroke=VORTEX_RED, sw=1.6))
    f.append(circle(r_x - rw * 0.71, r_y + 140, 6, fill='none', stroke=VORTEX_RED, sw=1.4))
    f.append(circle(r_x + rw * 0.71, r_y + 140, 6, fill='none', stroke=VORTEX_RED, sw=1.4))

    f.append(text(W / 4, r_y + 185, 'Стандартна індукована потужність: P_i = T · v_i0', 11, INK, 'middle'))

    # Права панель: IGE
    x_ige = 3 * W / 4
    f.append(text(x_ige, 52, 'В екрані землі (IGE: h < R)', 14, INK, 'middle', bold=True))
    f.append(text(x_ige, 70, 'Поверхня блокує розгін униз; утворюється розтікання вбік', 11, MUTED, 'middle'))

    # Поверхня землі (лінія зі штрихами)
    g_y = 260
    f.append(line(x_ige - 170, g_y, x_ige + 170, g_y, color=INK, sw=2.5))
    for sx in range(int(x_ige - 160), int(x_ige + 170), 15):
        f.append(line(sx, g_y, sx - 8, g_y + 10, color=MUTED, sw=1.2))
    f.append(text(x_ige, g_y + 24, 'Непроникна поверхня землі (v_z = 0)', 11, INK, 'middle', bold=True))

    # Ротор IGE
    r_ige_y = g_y - 100
    f.append(line(x_ige - rw, r_ige_y, x_ige + rw, r_ige_y, color=INK, sw=3.5))
    f.append(circle(x_ige, r_ige_y, 5, fill=INK, stroke=INK, sw=1))

    # Розмір висоти h
    f.append(line(x_ige - rw - 35, r_ige_y, x_ige - rw - 35, g_y, color=POS, sw=1.5))
    f.append(line(x_ige - rw - 42, r_ige_y, x_ige - rw - 28, r_ige_y, color=POS, sw=1.2))
    f.append(line(x_ige - rw - 42, g_y, x_ige - rw - 28, g_y, color=POS, sw=1.2))
    f.append(text(x_ige - rw - 48, (r_ige_y + g_y) / 2 + 4, 'h', 13, POS, 'end', bold=True, italic=True))

    # Менша індукована швидкість vi_IGE
    f.append(arrow(x_ige, r_ige_y + 8, x_ige, r_ige_y + 35, color=FIELD, sw=2.0))
    f.append(text(x_ige + 14, r_ige_y + 24, 'v_i,IGE < v_i0', 11, FIELD, 'start', bold=True, italic=True))

    # Струмінь IGE (розширюється до землі й переходить у пристінний струмінь)
    d_ige_l = "M %d %d Q %d %d %d %d" % (x_ige - rw, r_ige_y, x_ige - rw * 1.05, g_y - 25, x_ige - rw * 1.7, g_y - 8)
    d_ige_r = "M %d %d Q %d %d %d %d" % (x_ige + rw, r_ige_y, x_ige + rw * 1.05, g_y - 25, x_ige + rw * 1.7, g_y - 8)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (d_ige_l, FIELD))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (d_ige_r, FIELD))

    # Стрілки радіального розтікання
    f.append(arrow(x_ige - 80, g_y - 12, x_ige - 145, g_y - 12, color=FIELD, sw=2.0))
    f.append(arrow(x_ige + 80, g_y - 12, x_ige + 145, g_y - 12, color=FIELD, sw=2.0))
    f.append(text(x_ige - 120, g_y - 22, 'розтікання', 10, FIELD, 'middle'))
    f.append(text(x_ige + 120, g_y - 22, 'розтікання', 10, FIELD, 'middle'))

    # Підвищений тиск під ротором
    f.append(text(x_ige, (r_ige_y + g_y) / 2 + 10, '+Δp (динамічна подушка)', 11, POS, 'middle', bold=True))
    f.append(text(x_ige, H - 20, 'Зниження індукованої потужності: P_i,IGE / P_i,OGE ≈ 0.65 ... 0.85', 11, FIELD, 'middle'))

    render(os.path.join(IMG, 'ground-effect-flow.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 2: Графік відношення тяги та потужності IGE/OGE від висоти h/R
# ═══════════════════════════════════════════════════════════════════════════
def fig_thrust_ige_curve():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, 'Приріст тяги та падіння потрібної потужності в екрані землі (IGE)',
                  15, INK, 'middle', bold=True))

    ox = 95
    oy = 290
    gw = 570
    gh = 220

    # Сітка та осі
    f.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke=MUTED, sw=1.0))

    # Горизонтальні лінії сітки (T_IGE / T_OGE від 1.0 до 1.5)
    for i, val in enumerate([1.0, 1.1, 1.2, 1.3, 1.4, 1.5]):
        y_lvl = oy - (val - 1.0) / 0.5 * gh
        f.append(line(ox, y_lvl, ox + gw, y_lvl, color="#e2e8f0", sw=1.0))
        f.append(text(ox - 8, y_lvl + 4, '%.1f' % val, 11, MUTED, 'end'))

    # Вертикальні лінії сітки (h/R від 0.2 до 2.0)
    for hr in [0.4, 0.8, 1.2, 1.6, 2.0]:
        x_lvl = ox + (hr / 2.2) * gw
        f.append(line(x_lvl, oy - gh, x_lvl, oy, color="#e2e8f0", sw=1.0))
        f.append(text(x_lvl, oy + 18, '%.1f' % hr, 11, MUTED, 'middle'))

    # Підписи осей
    f.append(text(ox + gw / 2, oy + 36, 'Відносна висота над поверхнею: h / R  (де R — радіус гвинта)',
                  12, INK, 'middle', bold=True))
    f.append(text(ox - 52, oy - gh / 2, 'T_IGE / T_OGE', 12, INK, 'middle', bold=True))

    # Крива 1: Модель Чізмена й Беннетта: T_IGE/T_OGE = 1 / (1 - (R / (4h))^2)
    pts_cb = []
    n_pts = 60
    for i in range(n_pts + 1):
        hr = 0.38 + i / n_pts * (2.2 - 0.38)
        denom = 1.0 - 1.0 / (16.0 * hr * hr)
        if denom <= 0.01: continue
        ratio = 1.0 / denom
        if ratio > 1.55: continue
        x_px = ox + (hr / 2.2) * gw
        y_px = oy - (ratio - 1.0) / 0.5 * gh
        pts_cb.append((x_px, y_px))

    d_cb = 'M ' + ' L '.join('%.1f %.1f' % (px, py) for px, py in pts_cb)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d_cb, POS))

    # Крива 2: Емпірична модель Гейдена: T_IGE / T_OGE = 1 / [0.9926 + 0.0379 (h/R)^(-2)]
    pts_hay = []
    for i in range(n_pts + 1):
        hr = 0.25 + i / n_pts * (2.2 - 0.25)
        denom = 0.9926 + 0.0379 * math.pow(hr, -2.0)
        ratio = 1.0 / denom
        if ratio > 1.55: continue
        x_px = ox + (hr / 2.2) * gw
        y_px = oy - (ratio - 1.0) / 0.5 * gh
        pts_hay.append((x_px, y_px))

    d_hay = 'M ' + ' L '.join('%.1f %.1f' % (px, py) for px, py in pts_hay)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="6,4"/>' % (d_hay, FLOW_BLUE))

    # Зона практичної значущості ефекту землі
    x_crit = ox + (1.0 / 2.2) * gw
    f.append(line(x_crit, oy - gh, x_crit, oy, color=FIELD, sw=1.5, dash='3,3'))
    f.append(text(x_crit + 6, oy - gh + 18, 'h/R = 1.0 (h = 0.5 D)', 11, FIELD, 'start', bold=True))
    f.append(text(x_crit + 6, oy - gh + 34, 'основна зона IGE', 10, FIELD, 'start'))

    # Легенда
    f.append(line(ox + 310, oy - gh + 25, ox + 350, oy - gh + 25, color=POS, sw=2.6))
    f.append(text(ox + 356, oy - gh + 29, 'Чізмен-Беннетт: 1 / (1 - (R/4h)²)', 11, INK, 'start', bold=True))

    f.append(line(ox + 310, oy - gh + 48, ox + 350, oy - gh + 48, color=FLOW_BLUE, sw=2.4, dash='6,4'))
    f.append(text(ox + 356, oy - gh + 52, 'Емпірика Гейдена (Hayden)', 11, INK, 'start', bold=True))

    render(os.path.join(IMG, 'thrust-ige-curve.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 3: Аеродинамічні режими вертикального спуску та вихорове кільце (VRS)
# ═══════════════════════════════════════════════════════════════════════════
def fig_vrs_states():
    W, H = 840, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 22, 'Режими роботи ротора при осьовому русі вздовж осі тяги',
                  15, INK, 'middle', bold=True))

    col_w = W / 4
    headers = [
        ("Висіння / Набір", "V_z ≥ 0", "Чистий потік униз"),
        ("Вихорове кільце (VRS)", "-1.2 < V_z/v_i0 < -0.5", "Тороїдальна рециркуляція"),
        ("Турбулентний слід", "-2.0 < V_z/v_i0 < -1.2", "Хаотичний розпад сліду"),
        ("Вітряк / Авторотація", "V_z/v_i0 ≤ -2.0", "Повний потік угору (гальмо)")
    ]

    for i, (title, sub, note) in enumerate(headers):
        cx = col_w * (i + 0.5)
        # Рамка стовпчика
        fill_col = "#fff4f2" if i == 1 else "#fafbfc"
        border_col = VORTEX_RED if i == 1 else "#cbd5e1"
        f.append(rect(col_w * i + 8, 42, col_w - 16, 290, fill=fill_col, stroke=border_col, sw=1.6 if i==1 else 1.0, rx=6))

        f.append(text(cx, 62, title, 12, VORTEX_RED if i==1 else INK, 'middle', bold=True))
        f.append(text(cx, 78, sub, 11, FLOW_BLUE if i!=1 else VORTEX_RED, 'middle', italic=True))

        # Ротор
        ry = 150
        rw = 36
        f.append(line(cx - rw, ry, cx + rw, ry, color=INK, sw=3.0))
        f.append(circle(cx, ry, 4, fill=INK, stroke=INK, sw=1))

        if i == 0:
            f.append(arrow(cx, ry - 35, cx, ry - 10, color=FLOW_BLUE, sw=2.0))
            f.append(arrow(cx, ry + 10, cx, ry + 55, color=FLOW_BLUE, sw=2.2))
            f.append(text(cx, ry + 75, 'струмінь униз', 11, FLOW_BLUE, 'middle'))
            f.append(text(cx, 290, 'Стабільна тяга', 11, INK, 'middle'))

        elif i == 1:
            f.append(arrow(cx, ry + 75, cx, ry + 50, color=POS, sw=2.0))
            f.append(text(cx + 28, ry + 65, 'V_z (спуск)', 10, POS, 'start', italic=True))

            d_ring_l = "M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d" % (
                cx - 24, ry + 8,  cx - 48, ry + 25, cx - 48, ry - 25, cx - 24, ry - 8,
                cx - 12, ry - 2, cx - 12, ry + 4, cx - 24, ry + 8
            )
            d_ring_r = "M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d" % (
                cx + 24, ry + 8,  cx + 48, ry + 25, cx + 48, ry - 25, cx + 24, ry - 8,
                cx + 12, ry - 2, cx + 12, ry + 4, cx + 24, ry + 8
            )
            f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_ring_l, VORTEX_RED))
            f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_ring_r, VORTEX_RED))

            f.append(circle(cx - 30, ry, 3, fill=VORTEX_RED, stroke=VORTEX_RED, sw=1))
            f.append(circle(cx + 30, ry, 3, fill=VORTEX_RED, stroke=VORTEX_RED, sw=1))

            f.append(text(cx, ry + 100, 'Втрата тяги 30-50%', 11, VORTEX_RED, 'middle', bold=True))
            f.append(text(cx, 290, 'Тряска, падіння', 11, VORTEX_RED, 'middle', bold=True))

        elif i == 2:
            f.append(arrow(cx, ry + 65, cx, ry + 20, color=MUTED, sw=2.0))
            f.append(circle(cx - 18, ry - 30, 8, fill='none', stroke=MUTED, sw=1.5))
            f.append(circle(cx + 18, ry - 30, 8, fill='none', stroke=MUTED, sw=1.5))
            f.append(circle(cx, ry - 45, 6, fill='none', stroke=MUTED, sw=1.5))
            f.append(text(cx, ry + 80, 'слід над диском', 11, MUTED, 'middle'))
            f.append(text(cx, 290, 'Нестійка течія', 11, INK, 'middle'))

        elif i == 3:
            f.append(arrow(cx, ry + 65, cx, ry + 15, color=GREEN_ZONE, sw=2.2))
            f.append(arrow(cx, ry - 15, cx, ry - 60, color=GREEN_ZONE, sw=2.2))
            f.append(text(cx, ry + 85, 'наскрізний потік', 11, GREEN_ZONE, 'middle'))
            f.append(text(cx, 290, 'Відбір потужності', 11, GREEN_ZONE, 'middle', bold=True))

        f.append(text(cx, 316, note, 10, MUTED, 'middle'))

    render(os.path.join(IMG, 'vrs-states.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 4: Траєкторії виходу з VRS (Класичний маневр проти маневру Вюішара)
# ═══════════════════════════════════════════════════════════════════════════
def fig_vrs_recovery_vuichard():
    W, H = 780, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, 'Методи виходу з вихорового кільця: класичний розгін проти маневру Вюішара',
                  15, INK, 'middle', bold=True))

    sx0 = 120
    sy0 = 90

    # Вихорова колона (вертикальний стовп рециркуляції)
    f.append(rect(sx0 - 55, 60, 110, 240, fill="#fff0ee", stroke="#fca5a5", sw=1.2, rx=4))
    f.append(text(sx0, 78, 'Стовп VRS', 11, VORTEX_RED, 'middle', bold=True))
    f.append(circle(sx0 - 32, 115, 8, fill='none', stroke=VORTEX_RED, sw=1.5))
    f.append(circle(sx0 + 32, 115, 8, fill='none', stroke=VORTEX_RED, sw=1.5))

    # Початкова точка гелікоптера
    f.append(circle(sx0, sy0, 6, fill=VORTEX_RED, stroke=VORTEX_RED, sw=1))
    f.append(text(sx0, sy0 - 14, 'Попадання у VRS', 11, INK, 'middle', bold=True))

    # Траєкторія 1: Класичний метод (ніс униз, розгін уперед)
    d_trad = "M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d" % (
        sx0, sy0,
        sx0 + 20, sy0 + 110, sx0 + 90, sy0 + 175, sx0 + 220, sy0 + 185,
        sx0 + 330, sy0 + 190, sx0 + 440, sy0 + 185, sx0 + 580, sy0 + 180
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="6,4"/>' % (d_trad, MUTED))

    # Стрілка на кінці класичної траєкторії
    f.append(arrow(sx0 + 500, sy0 + 181, sx0 + 560, sy0 + 180, color=MUTED, sw=2.4))

    # Маркери втрати висоти класичного методу
    h_trad_y = sy0 + 185
    f.append(line(sx0 + 260, sy0, sx0 + 260, h_trad_y, color=MUTED, sw=1.4, dash='3,3'))
    f.append(text(sx0 + 270, (sy0 + h_trad_y) / 2, 'Втрата висоти: 60 - 150 м', 11, MUTED, 'start', bold=True))
    f.append(text(sx0 + 440, sy0 + 168, '1. Класичний метод: нахил уперед + розгін', 12, MUTED, 'start', bold=True))
    f.append(text(sx0 + 440, sy0 + 205, 'Тривалий вихід уздовж власного сліду', 10, MUTED, 'start'))

    # Траєкторія 2: Маневр Вюішара (Vuichard Recovery)
    d_vui = "M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d" % (
        sx0, sy0,
        sx0 + 40, sy0 + 15, sx0 + 80, sy0 + 25, sx0 + 150, sy0 + 22,
        sx0 + 240, sy0 + 18, sx0 + 360, sy0 + 10, sx0 + 500, sy0 + 5
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (d_vui, GREEN_ZONE))
    f.append(arrow(sx0 + 420, sy0 + 7, sx0 + 490, sy0 + 5, color=GREEN_ZONE, sw=2.6))

    # Маркери втрати висоти маневру Вюішара
    h_vui_y = sy0 + 25
    f.append(line(sx0 + 150, sy0, sx0 + 150, h_vui_y, color=GREEN_ZONE, sw=1.6))
    f.append(text(sx0 + 160, sy0 + 38, 'Втрата висоти: лише 10 - 20 м', 11, GREEN_ZONE, 'start', bold=True))
    f.append(text(sx0 + 260, sy0 - 12, '2. Маневр Вюішара: циклік убік + протимоментна педаль', 12, GREEN_ZONE, 'start', bold=True))
    f.append(text(sx0 + 260, sy0 + 6, 'Миттєвий вихід крізь бічну межу вихора у чисте повітря', 10, GREEN_ZONE, 'start'))

    # Візуалізація дії маневру Вюішара
    f.append(arrow(sx0 + 20, sy0 + 5, sx0 + 65, sy0 + 18, color=GREEN_ZONE, sw=2.2))
    f.append(text(sx0 + 38, sy0 - 2, 'Тяга кермового гвинта допомагає зсуву →', 10, GREEN_ZONE, 'start'))

    render(os.path.join(IMG, 'vrs-recovery-vuichard.svg'), W, H, *f)


if __name__ == '__main__':
    fig_ground_effect_flow()
    fig_thrust_ige_curve()
    fig_vrs_states()
    fig_vrs_recovery_vuichard()
    print("All figures generated successfully.")
