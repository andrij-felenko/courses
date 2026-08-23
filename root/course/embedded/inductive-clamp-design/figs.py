# -*- coding: utf-8 -*-
"""Фігури до кроку «Розрахунок клампу для індуктивного навантаження».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: компроміс «напруга клампу ↔ час вимкнення» ────────────────────
# Три рівні клампу дають три швидкості спаду струму (V_clamp−V_supply на L).
def fig_tradeoff():
    W, H = 720, 360
    x0, y0 = 90, 290          # початок осей
    xr, yt = 660, 70          # край осей
    # три ламані спаду струму I(t): крутіша = вищий кламп = швидше до нуля
    I0y = y0 - 170            # рівень повного струму
    base = line(x0, I0y, x0 + 70, I0y, color=INK, sw=2.2)   # спільна «полиця» струму до розмикання
    # точки нуля по осі часу для трьох клампів
    t_diode = xr - 30
    t_zener = x0 + 70 + (t_diode - (x0 + 70)) * 0.42
    t_tvs   = x0 + 70 + (t_diode - (x0 + 70)) * 0.20
    seg = lambda tx, col: line(x0 + 70, I0y, tx, y0, color=col, sw=2.6)
    g = (rect(x0, yt, xr - x0, y0 - yt, fill="#fbfcfd", stroke="#dfe3e8", sw=1.2, rx=8)
         + line(x0, y0, xr, y0, color=INK, sw=2)          # вісь часу
         + line(x0, y0, x0, yt, color=INK, sw=2)          # вісь струму
         + base
         + seg(t_tvs, POS) + seg(t_zener, FIELD) + seg(t_diode, NEG)
         + text(x0 - 12, I0y + 5, "I₀", size=14, color=INK, anchor="end", bold=True)
         + text(x0 - 12, y0 + 5, "0", size=13, color=MUTED, anchor="end")
         + text(xr, y0 + 26, "час →", size=13, color=MUTED, anchor="end")
         + text(x0 - 64, (yt + y0) / 2, "струм", size=13, color=MUTED, anchor="middle")
         )
    # підписи кривих
    b1, w1, h1 = textbox(t_diode - 6, I0y - 34, "діод 0.7 В\nповільно", size=11,
                         color=NEG, stroke=NEG, fill="#eef3fe", pad=6)
    b2, w2, h2 = textbox(t_zener, y0 - 116, "+Зенер ~36 В\nшвидше", size=11,
                         color=FIELD, stroke=FIELD, fill="#eafaf0", pad=6)
    b3, w3, h3 = textbox(t_tvs - 4, y0 - 60, "TVS / лавина\nнайшвидше", size=11,
                         color=POS, stroke=POS, fill="#fdecea", pad=6)
    # формула швидкості спаду
    f, wf, hf = textbox((x0 + xr) / 2, yt - 28, "di/dt = (V_кламп − V_жив) / L", size=13,
                        bold=True, fill="#fff8e1", stroke="#e0c068", pad=8)
    return render(os.path.join(OUT, 'clamp-tradeoff.svg'), W, H,
                  g, b1, b2, b3, f,
                  title="Вищий кламп → швидший спад струму")


# ── Фігура 2: три схеми клампу поруч, із напругою на ключі ───────────────────
def fig_three_clamps():
    W, H = 800, 330
    cw = 230
    gap = 25
    x = 30
    panels = [
        ("Діод", NEG, "V_ключ ≈\nV_жив + 0.7", "повільно"),
        ("Діод + Зенер", FIELD, "V_ключ ≈\nV_жив + V_Z", "швидше"),
        ("TVS / лавинний\nключ", POS, "V_ключ ≈\nV_кламп", "найшвидше"),
    ]
    parts = []
    for i, (name, col, vform, speed) in enumerate(panels):
        px = x + i * (cw + gap)
        parts.append(rect(px, 56, cw, 250, fill="#fbfcfd", stroke="#dfe3e8", sw=1.3, rx=10))
        # заголовок панелі
        parts.append(mtext(px + cw / 2, 78, name.split("\n"), size=13, bold=True, color=col))
        # схема: V+ зверху, котушка, ключ знизу, кламп паралельно котушці
        topy, boty = 120, 230
        lx = px + 70           # ліва шина (котушка)
        rx = px + cw - 55      # права гілка (кламп)
        parts.append(text(lx, topy - 12, "V+", size=11, color=POS, anchor="middle"))
        parts.append(line(lx, topy, lx, boty, color=INK, sw=1.6))     # ліва вітка-котушка
        # котушка — три дужки
        coil = ""
        cy = topy + 16
        for k in range(3):
            yy = cy + k * 22
            coil += ('<path d="M %.1f %.1f a 8 11 0 1 1 0 22" fill="none" stroke="%s" stroke-width="2"/>'
                     % (lx, yy, INK))
        parts.append(coil)
        parts.append(text(lx - 14, (topy + boty) / 2 + 4, "L", size=13, color=INK, anchor="end", bold=True))
        # ключ унизу
        parts.append(line(lx, boty, rx, boty, color=INK, sw=1.6))
        sw_x = (lx + rx) / 2
        parts.append(circle(sw_x, boty, 3, fill=INK, stroke=INK))
        parts.append(text(sw_x, boty + 18, "ключ", size=10, color=MUTED, anchor="middle"))
        # кламп паралельно котушці (права гілка top→bot)
        parts.append(line(lx, topy, rx, topy, color=INK, sw=1.6))
        parts.append(line(rx, topy, rx, boty, color=col, sw=2))
        # символ клампу посередині правої гілки
        my = (topy + boty) / 2
        if i == 0:   # діод
            parts.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.5"/>'
                         % (rx - 8, my - 9, rx + 8, my, rx - 8, my + 9, "#eef3fe", col))
            parts.append(line(rx - 8, my + 9, rx + 8, my + 9, color=col, sw=2))
        elif i == 1:  # діод + зенер (два символи)
            parts.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.5"/>'
                         % (rx - 7, my - 22, rx + 7, my - 13, rx - 7, my - 4, "#eafaf0", col))
            parts.append(line(rx - 7, my - 4, rx + 7, my - 4, color=col, sw=2))
            parts.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.5"/>'
                         % (rx - 7, my + 22, rx + 7, my + 13, rx - 7, my + 4, "#eafaf0", col))
            parts.append('<path d="M %.1f %.1f l 5 0 l 0 4 M %.1f %.1f l -5 0 l 0 -4" stroke="%s" stroke-width="2" fill="none"/>'
                         % (rx - 5, my + 4, rx + 5, my + 4, col))
        else:         # TVS / лавина — стабілітронний символ
            parts.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.5"/>'
                         % (rx - 8, my - 9, rx + 8, my, rx - 8, my + 9, "#fdecea", col))
            parts.append('<path d="M %.1f %.1f l 6 0 l 0 5 M %.1f %.1f l -6 0 l 0 -5" stroke="%s" stroke-width="2" fill="none"/>'
                         % (rx - 6, my + 9, rx + 6, my + 9, col))
        # напруга на ключі
        vb = fitbox(px + 16, 248, cw - 32, 30, vform.replace("\n", "  "), size=11,
                    color=col, stroke=col, fill=BG, pad=6)
        parts.append(vb)
        parts.append(text(px + cw / 2, 296, "спад струму: " + speed, size=10, color=MUTED, anchor="middle"))
    return render(os.path.join(OUT, 'three-clamps.svg'), W, H,
                  "".join(parts),
                  title="Що ставлять паралельно котушці — і яку напругу терпить ключ")


# ── Фігура 3: куди дівається ½·L·I² і чому рейтинг різний ────────────────────
def fig_energy_split():
    W, H = 720, 320
    # ліворуч — резервуар енергії ½LI²; стрілки в дві долі: діод+котушка / кламп
    src, ws, hs = textbox(150, 90, "Запас у полі\n½·L·I²", size=14, bold=True,
                          fill="#fff8e1", stroke="#e0c068", pad=12, min_w=170)
    # дві гілки
    a1 = arrow(150, 90 + hs / 2, 150, 200, color=INK)
    box1 = fitbox(40, 205, 220, 90,
                  "ОДИН імпульс:\nкламп має лише пережити сплеск енергії "
                  "(рейтинг по джоулях E_AS)", size=12, fill="#eef3fe", stroke=NEG, pad=10)
    a2 = arrow(360, 60, 470, 60, color=INK)
    box2 = fitbox(470, 30, 230, 110,
                  "ПОВТОРНО (ШІМ):\nсереднє розсіяння = ½·L·I²·f_перем "
                  "→ діод/кламп має тримати СЕРЕДНЮ потужність, не лише пік", size=12,
                  fill="#fdecea", stroke=POS, pad=10)
    # підказка-зв'язок
    note = fitbox(330, 205, 370, 90,
                  "Енергія завжди йде в тепло: на падінні клампу + на опорі "
                  "обмотки. Питання лише — за який час і скільки разів за секунду.",
                  size=12, fill="#eafaf0", stroke=FIELD, pad=10)
    return render(os.path.join(OUT, 'energy-split.svg'), W, H,
                  src, a1, a2, box1, box2, note,
                  title="Одна й та сама енергія — два різні рейтинги")


# ── Фігура 4: вибір клампу за вимогою до часу вимкнення ──────────────────────
def fig_selection():
    W, H = 700, 340
    q, wq, hq = textbox(350, 64, "Як швидко навантаження має вимкнутися?", size=14,
                        bold=True, fill="#fff8e1", stroke="#e0c068", pad=12)
    rows = [
        ("байдуже (реле раз на хвилину)", "діод-кламп (0.7 В)\nнайдешевше, найповільніше", NEG),
        ("важливе (точне реле, клапан)", "діод + Зенер / TVS\nкламп на 1.5…2× V_жив", FIELD),
        ("критичне (ШІМ-соленоїд, швидкий рух)", "лавинний MOSFET або TVS,\nрахуй E_AS і середню P", POS),
    ]
    parts = [q]
    y = 110
    for cond, ans, col in rows:
        cb = fitbox(40, y, 300, 64, cond, size=12, fill="#fbfcfd", stroke="#dfe3e8", pad=10)
        ab = fitbox(400, y, 270, 64, ans, size=12, fill=BG, stroke=col, pad=8, color=col)
        ar = arrow(345, y + 32, 398, y + 32, color=col)
        parts += [cb, ab, ar]
        y += 78
    return render(os.path.join(OUT, 'clamp-selection.svg'), W, H,
                  *parts,
                  title="Вимога до швидкості диктує кламп")


# ── Фігура 5 (вставка math): експонента діода проти прямої Зенера ────────────
# Низький кламп → струм згасає за i=I₀·e^(−t/τ) (вигин); високий кламп → прямий
# короткий спад, що уривається перш ніж експонента встигне зігнутися.
def fig_decay_curves():
    import math
    W, H = 720, 360
    x0, y0 = 90, 295          # початок осей
    xr, yt = 660, 70          # край осей
    I0y = yt + 30             # рівень повного струму I₀
    span_x = xr - x0
    span_y = y0 - I0y
    # експонента діода: розтягнута на майже всю вісь (спад сумірний з τ)
    tau_px = span_x * 0.30                       # τ у пікселях
    pts_exp = []
    n = 60
    for k in range(n + 1):
        tx = x0 + span_x * k / n
        val = math.exp(-(tx - x0) / tau_px)
        pts_exp.append((tx, y0 - span_y * val))
    poly_exp = ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                % (" ".join("%.1f,%.1f" % p for p in pts_exp), NEG))
    # пряма Зенера: крутий короткий спад до нуля (уривається рано)
    t_z = x0 + span_x * 0.22
    line_z = line(x0, I0y, t_z, y0, color=POS, sw=2.6)
    # позначка τ на осі часу
    tau_x = x0 + tau_px
    g = (rect(x0, yt, xr - x0, y0 - yt, fill="#fbfcfd", stroke="#dfe3e8", sw=1.2, rx=8)
         + line(x0, y0, xr, y0, color=INK, sw=2)
         + line(x0, y0, x0, yt, color=INK, sw=2)
         + line(x0, I0y, x0 + 8, I0y, color=INK, sw=2)
         + text(x0 - 12, I0y + 5, "I₀", size=14, color=INK, anchor="end", bold=True)
         + text(x0 - 12, y0 + 5, "0", size=13, color=MUTED, anchor="end")
         + text(xr, y0 + 26, "час →", size=13, color=MUTED, anchor="end")
         + text(x0 - 64, (yt + y0) / 2, "струм", size=13, color=MUTED, anchor="middle")
         + line(tau_x, y0, tau_x, y0 + 6, color=MUTED, sw=1.5)
         + text(tau_x, y0 + 20, "τ=L/R", size=11, color=MUTED, anchor="middle")
         + poly_exp + line_z)
    b1, _, _ = textbox(x0 + span_x * 0.62, y0 - span_y * 0.33,
                       "діод: i = I₀·e^(−t/τ)\nвигин, довгий спад", size=11,
                       color=NEG, stroke=NEG, fill="#eef3fe", pad=6)
    b2, _, _ = textbox(t_z + 80, I0y + 36,
                       "Зенер/TVS: прямий\nкороткий спад (≪ τ)", size=11,
                       color=POS, stroke=POS, fill="#fdecea", pad=6)
    cap, _, _ = textbox((x0 + xr) / 2, yt - 26,
                        "лінійна формула чесна, поки спад ≪ τ", size=12,
                        bold=True, fill="#fff8e1", stroke="#e0c068", pad=8)
    return render(os.path.join(OUT, 'decay-curves.svg'), W, H,
                  g, b1, b2, cap,
                  title="Спад струму: експонента діода проти прямої Зенера")


# ── Фігура 6 (вставка math): зайвий клин енергії від живлення в лавині ───────
# p(t)=BV·i(t). Без живлення струм гасить повна BV (крутий спад, площа ½LI²);
# із живленням гасить лише (BV−V_жив) — спад пологіший, площа більша на «клин».
def fig_uis_extra():
    W, H = 720, 360
    x0, y0 = 95, 290
    xr, yt = 655, 80
    Ptop = yt + 24                # рівень пікової потужності BV·I₀
    span_x = xr - x0
    span_y = y0 - Ptop
    # без живлення: крутий спад до нуля за короткий час (площа ½LI²)
    t_noV = x0 + span_x * 0.42
    tri_noV = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#eef3fe" '
               'stroke="%s" stroke-width="2.2"/>'
               % (x0, Ptop, t_noV, y0, x0, y0, NEG))
    # із живленням: пологіший спад, довший час (більша площа)
    t_V = x0 + span_x * 0.82
    # «клин» надлишку — між двома гіпотенузами
    wedge = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fdecea" '
             'stroke="none" opacity="0.85"/>'
             % (x0, Ptop, t_V, y0, t_noV, y0))
    hyp_V = line(x0, Ptop, t_V, y0, color=POS, sw=2.6)
    g = (rect(x0, yt, xr - x0, y0 - yt, fill="#fbfcfd", stroke="#dfe3e8", sw=1.2, rx=8)
         + line(x0, y0, xr, y0, color=INK, sw=2)
         + line(x0, y0, x0, yt, color=INK, sw=2)
         + line(x0, Ptop, x0 + 8, Ptop, color=INK, sw=2)
         + text(x0 - 12, Ptop + 5, "BV·I₀", size=12, color=INK, anchor="end", bold=True)
         + text(x0 - 12, y0 + 5, "0", size=13, color=MUTED, anchor="end")
         + text(xr, y0 + 26, "час →", size=13, color=MUTED, anchor="end")
         + text(x0 - 70, (yt + y0) / 2, "потужність\nв кристалі".split("\n")[0],
                size=12, color=MUTED, anchor="middle")
         + wedge + tri_noV + hyp_V
         + line(t_noV, y0, t_noV, y0 + 6, color=NEG, sw=1.5)
         + line(t_V, y0, t_V, y0 + 6, color=POS, sw=1.5))
    b1, _, _ = textbox(x0 + span_x * 0.20, Ptop + span_y * 0.42,
                       "без живлення:\nгасить повна BV\nплоща = ½·L·I²", size=11,
                       color=NEG, stroke=NEG, fill="#eef3fe", pad=6)
    b2, _, _ = textbox(x0 + span_x * 0.60, y0 - span_y * 0.30,
                       "клин від живлення:\nгасить лише\n(BV − V_жив)", size=11,
                       color=POS, stroke=POS, fill="#fdecea", pad=6)
    cap, _, _ = textbox((x0 + xr) / 2, yt - 30,
                        "E_AS = ½·L·I² · BV/(BV − V_жив)", size=13,
                        bold=True, fill="#fff8e1", stroke="#e0c068", pad=8)
    return render(os.path.join(OUT, 'uis-extra-energy.svg'), W, H,
                  g, b1, b2, cap,
                  title="Чому в кристалі більше за ½·L·I²")


if __name__ == '__main__':
    fig_tradeoff()
    fig_three_clamps()
    fig_energy_split()
    fig_selection()
    fig_decay_curves()
    fig_uis_extra()
    print("OK: 6 figures ->", OUT)
