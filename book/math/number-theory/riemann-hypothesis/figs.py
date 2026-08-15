import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: Комплексна площина, критична смуга та критична лінія ────────────

def fig_critical_strip():
    W, H = 640, 540
    ox, oy = 240, 270        # початок координат (0, 0)
    sx = 160                 # масштаб по дійсій осі (1 одиниця = 160px)
    sy = 6.5                 # масштаб по уявній осі (1 одиниця = 6.5px)

    parts = []

    # Критична смуга 0 < σ < 1 (зафарбована область)
    x0 = ox
    x1 = ox + 1.0 * sx
    parts.append('<rect x="%.1f" y="40" width="%.1f" height="%.1f" fill="%s" opacity="0.35"/>'
                 % (x0, x1 - x0, H - 80, FIELD))

    # Осі координат
    parts.append(arrow(60, oy, W - 40, oy, color=INK, sw=1.5))
    parts.append(arrow(ox, H - 35, ox, 25, color=INK, sw=1.5))
    parts.append(text(W - 30, oy + 5, 'Re(s) = σ', size=13, color=INK, anchor='start'))
    parts.append(text(ox + 12, 22, 'Im(s) = t', size=13, color=INK, anchor='start'))

    # Критична лінія σ = 1/2
    x_half = ox + 0.5 * sx
    parts.append(line(x_half, 40, x_half, H - 40, color=POS, sw=2.5))
    
    # Межі критичної смуги σ = 0 та σ = 1
    parts.append(line(ox, 40, ox, H - 40, color=MUTED, sw=1.2, dash='4 3'))
    parts.append(line(x1, 40, x1, H - 40, color=MUTED, sw=1.2, dash='4 3'))

    # Позначки на дійсій осі (σ = 0, 1/2, 1, полюс s=1, тривіальні нулі -2, -4, -6)
    parts.append(text(ox - 10, oy + 18, '0', size=12, color=INK, anchor='end'))
    parts.append(text(x_half, oy + 22, '1/2', size=12, color=POS, anchor='middle', bold=True))
    parts.append(text(x1 + 4, oy + 22, '1', size=12, color=INK, anchor='start'))

    # Полюс при s = 1
    parts.append(text(x1 + 25, oy - 14, 'Полюс s=1', size=11, color=NEG, anchor='start'))
    parts.append(circle(x1, oy, 5, fill='#ffffff', stroke=NEG, sw=2))

    # Тривіальні нулі s = -2, -4, -6
    triv_zeros = [-2, -4, -6]
    for tz in triv_zeros:
        tx = ox + tz * (sx * 0.25)
        parts.append(circle(tx, oy, 4.5, fill=MUTED, stroke=INK, sw=1))
        parts.append(text(tx, oy + 18, str(tz), size=11, color=MUTED, anchor='middle'))

    # Підпис тривіальних нулів
    tb_tr, tw_tr, th_tr = textbox(ox - 110, oy - 35, 'Тривіальні нулі: s = −2, −4, −6...',
                                  size=11, color=MUTED, fill=FILL, stroke=MUTED, sw=1)
    parts.append(tb_tr)

    # Перші кілька нетривіальних нулів на критичній лінії (t ≈ 14.13, 21.02, 25.01, 30.42)
    zeros_t = [14.13, 21.02, 25.01, 30.42]
    for t_val in zeros_t:
        # Верхня напівплощина (+t)
        py_up = oy - t_val * sy
        if py_up > 45:
            parts.append(circle(x_half, py_up, 5.5, fill=POS, stroke=INK, sw=1.2))
            parts.append(text(x_half + 12, py_up + 4, '1/2 + i·%.2f' % t_val,
                              size=11, color=POS, anchor='start'))

        # Нижня напівплощина (-t)
        py_dn = oy + t_val * sy
        if py_dn < H - 45:
            parts.append(circle(x_half, py_dn, 5.5, fill=POS, stroke=INK, sw=1.2))
            parts.append(text(x_half + 12, py_dn + 4, '1/2 − i·%.2f' % t_val,
                              size=11, color=POS, anchor='start'))

    # Текстові підписи зон
    tb_cs, tw_cs, th_cs = textbox(W - 110, 45, 'Критична смуга (0 < Re(s) < 1)',
                                  size=11, color=INK, fill=FILL, stroke=MUTED, sw=1)
    parts.append(tb_cs)

    tb_cl, tw_cl, th_cl = textbox(x_half, H - 25, 'Гіпотеза Рімана: УСІ нетривіальні нулі лежать на Re(s) = 1/2',
                                  size=12, color=POS, fill='#e6f4ea', stroke=POS, sw=1.5, bold=True)
    parts.append(tb_cl)

    render(os.path.join(OUT, 'fig-critical-strip.svg'), W, H, *parts,
           title='Комплексна площина Дзета-функції Рімана: критична смуга та лінія')


# ── Фігура 2: Інтерференція хвиль нулів та східчаста функція ─────────────────

def fig_explicit_formula_waves():
    W, H = 640, 440
    gx0, gy0 = 70, 370
    gw, gh = 520, 310

    parts = []

    # Осі
    parts.append(arrow(gx0 - 10, gy0, gx0 + gw + 20, gy0, color=INK, sw=1.5))
    parts.append(arrow(gx0, gy0 + 10, gx0, gy0 - gh - 20, color=INK, sw=1.5))
    parts.append(text(gx0 + gw + 25, gy0 + 5, 'x', size=13, color=INK, anchor='start'))
    parts.append(text(gx0 - 10, gy0 - gh - 25, 'ψ(x)', size=13, color=INK, anchor='end'))

    # Масштаб: x від 2 до 30
    xmin, xmax = 2.0, 30.0
    def to_px(x):
        return gx0 + (x - xmin) / (xmax - xmin) * gw
    def to_py(y):
        return gy0 - (y / 30.0) * gh

    # Головний тренд y = x (гладка лінія Li(x) або x)
    N = 100
    tpts = []
    for i in range(N + 1):
        x_val = xmin + (xmax - xmin) * i / N
        tpts.append('%.1f,%.1f' % (to_px(x_val), to_py(x_val)))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5 4"/>'
                 % (' '.join(tpts), MUTED))
    parts.append(text(to_px(28), to_py(28) - 10, 'Гладкий тренд y = x', size=11, color=MUTED, anchor='end'))

    # Точні сходинки для ψ(x) = ∑_{p^k ≤ x} ln(p)
    pk_list = [
        (2, math.log(2)), (3, math.log(3)), (4, math.log(2)), (5, math.log(5)),
        (7, math.log(7)), (8, math.log(2)), (9, math.log(3)), (11, math.log(11)),
        (13, math.log(13)), (16, math.log(2)), (17, math.log(17)), (19, math.log(19)),
        (23, math.log(23)), (25, math.log(5)), (27, math.log(3)), (29, math.log(29))
    ]

    # Побудова східчастої функції
    st_pts = []
    curr_x = xmin
    curr_y = 0.0
    st_pts.append('%.1f,%.1f' % (to_px(curr_x), to_py(curr_y)))
    
    for px_val, jump in pk_list:
        if px_val > xmax:
            break
        st_pts.append('%.1f,%.1f' % (to_px(px_val), to_py(curr_y)))
        curr_y += jump
        st_pts.append('%.1f,%.1f' % (to_px(px_val), to_py(curr_y)))
    st_pts.append('%.1f,%.1f' % (to_px(xmax), to_py(curr_y)))

    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
                 % (' '.join(st_pts), INK))
    parts.append(text(to_px(29), to_py(curr_y) - 15, 'Точна східчаста ψ(x)', size=11, color=INK, anchor='end', bold=True))

    # Наближення сумою перших 3 хвиль нулів: x - ∑ 2·x^(1/2)/ln(x) · cos(t_k · ln x)
    zeros_t = [14.13, 21.02, 25.01]
    wave_pts = []
    N_w = 200
    for i in range(N_w + 1):
        x_val = xmin + (xmax - xmin) * i / N_w
        w_sum = 0.0
        for t_k in zeros_t:
            w_sum += math.cos(t_k * math.log(x_val)) / t_k
        y_val = x_val - 2.0 * math.sqrt(x_val) * w_sum
        wave_pts.append('%.1f,%.1f' % (to_px(x_val), to_py(y_val)))

    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" opacity="0.85"/>'
                 % (' '.join(wave_pts), POS))
    parts.append(text(to_px(18), to_py(23), 'Наближення хвиль нулів (перші 3 нулі)', size=11, color=POS, anchor='start', bold=True))

    # Пояснювальний текст у рамці
    tb, tw, th = textbox(W / 2, 50,
                         'Кожен нуль ρ = 1/2 + i·t_k дає гармоніку ~ x^(1/2)·cos(t_k·ln x). Їхня сума висекає сходинки!',
                         size=11, color=INK, fill='#f4f5f7', stroke=MUTED, sw=1)
    parts.append(tb)

    render(os.path.join(OUT, 'fig-explicit-formula-waves.svg'), W, H, *parts,
           title='Синтез хвилями нулів східчастої функції розподілу простих чисел')


# ── Фігура 3: Відштовхування нулів та статистична кореляція (GUE) ─────────────

def fig_gue_random_matrices():
    W, H = 640, 360
    parts = []

    # 1. Випадкові точки Пуассона (без взаємодії) — згруповані
    y1 = 110
    parts.append(text(50, y1 - 25, 'Випадковий процес Пуассона (незалежні точки):', size=12, color=INK, anchor='start', bold=True))
    parts.append(line(50, y1, 590, y1, color=MUTED, sw=1.5))
    
    # Набір точок Пуассона з кластерами та великими прогалинами
    poisson_pts = [65, 75, 82, 140, 210, 215, 222, 230, 350, 480, 488, 570]
    for px in poisson_pts:
        parts.append(circle(px, y1, 5, fill=NEG, stroke=INK, sw=1))
    
    parts.append(text(80, y1 + 22, 'кластер (скупчення)', size=10, color=NEG, anchor='middle'))
    parts.append(text(280, y1 + 22, 'велика порожнеча (гап)', size=10, color=MUTED, anchor='middle'))

    # 2. Нулі Дзета-функції / Власні значення випадкових матриць (GUE) — відштовхування
    y2 = 250
    parts.append(text(50, y2 - 25, 'Нулі Дзета-функції / Власні значення GUE-матриць (відштовхування):', size=12, color=POS, anchor='start', bold=True))
    parts.append(line(50, y2, 590, y2, color=POS, sw=1.8))
    
    # Рівномірніше розподілені точки з квантовим відштовхуванням
    gue_pts = [70, 115, 162, 208, 255, 305, 352, 400, 448, 495, 545, 585]
    for px in gue_pts:
        parts.append(circle(px, y2, 5, fill=POS, stroke=INK, sw=1))

    parts.append(text(W / 2, y2 + 25, 'Плавне рівномірне впорядкування: точки відштовхують одна одну на малих відстанях',
                      size=11, color=POS, anchor='middle'))

    # Підпис унизу
    tb, tw, th = textbox(W / 2, H - 25,
                         'Закон Монтгомері–Одлижка: кореляція пар нулів Рімана точно збігається з квантовим хаосом GUE',
                         size=11, color=INK, fill='#fff8e1', stroke='#f0b429', sw=1.2)
    parts.append(tb)

    render(os.path.join(OUT, 'fig-gue-random-matrices.svg'), W, H, *parts,
           title='Статистичне відштовхування нулів Рімана порівняно з точками Пуассона')


fig_critical_strip()
fig_explicit_formula_waves()
fig_gue_random_matrices()
print('SVG figures generated successfully in', OUT)
