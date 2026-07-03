# -*- coding: utf-8 -*-
"""figs-d.py — фігури до ДЕТАЛЬНОЇ статті «Телекерування…-d».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Окремий від figs.py (базові фігури), щоб не чіпати їх."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура D1: затримка з'їдає запас по фазі (φ = ω·τ) ───────────────────────
# Ідея: чиста затримка додає фазове відставання, ЛІНІЙНЕ по частоті. Стійкість
# тримається, поки на робочій частоті ω_c відставання < запасу PM. Межа —
# τ_max = PM/ω_c. Малюємо дві прямі φ=ω·τ (мала й гранична затримка) на площині
# «частота → фаза», горизонт PM і вертикаль ω_c; перетин = межа.
def fig_phase_margin():
    W, H = 940, 520
    P = []
    P.append(text(W / 2, 34, "Затримка з'їдає запас по фазі: φ = ω·τ",
                  size=18, bold=True))

    # осі
    ox, oy = 110, 400          # початок координат
    ax_w, ax_h = W - 210, 300  # довжина осей
    P.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=2))           # вісь частоти →
    P.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=2))           # вісь фази ↑
    P.append(text(ox + ax_w - 4, oy + 34, "частота коливання  ω →", size=13,
                  color=MUTED, anchor="end"))
    P.append(text(ox - 18, oy - ax_h + 4, "фазове", size=12.5, color=MUTED, anchor="end"))
    P.append(text(ox - 18, oy - ax_h + 20, "відставання φ ↑", size=12.5, color=MUTED, anchor="end"))

    # горизонт запасу по фазі PM
    pm_y = oy - ax_h * 0.62
    P.append(line(ox, pm_y, ox + ax_w, pm_y, color=FIELD, sw=2, dash="8 5"))
    P.append(text(ox + ax_w - 4, pm_y - 12, "запас по фазі PM (60°)", size=13,
                  color=FIELD, bold=True, anchor="end"))

    # вертикаль робочої частоти ω_c
    wc_x = ox + ax_w * 0.52
    P.append(line(wc_x, oy, wc_x, oy - ax_h, color=MUTED, sw=1.6, dash="4 4"))
    P.append(text(wc_x, oy + 20, "ω_c", size=13.5, color=INK, bold=True))
    P.append(text(wc_x, oy + 36, "робоча частота", size=11, color=MUTED))

    # пряма φ=ω·τ для ГРАНИЧНОЇ затримки — проходить точно через (ω_c, PM)
    slope_max = (oy - pm_y) / (wc_x - ox)        # px фази на px частоти
    x_end = ox + ax_w
    y_end = oy - slope_max * (x_end - ox)
    if y_end < oy - ax_h:                          # обрізати до верху осі
        x_end = ox + ax_h / slope_max
        y_end = oy - ax_h
    P.append(line(ox, oy, x_end, y_end, color=POS, sw=2.6))

    # пряма для МАЛОЇ затримки (полога) — під межею на ω_c
    slope_ok = slope_max * 0.5
    P.append(line(ox, oy, ox + ax_w, oy - slope_ok * ax_w, color=NEG, sw=2.4))

    # точка перетину граничної прямої з (ω_c, PM)
    P.append(circle(wc_x, pm_y, 6, fill=POS, stroke=POS))

    # підписи прямих — розводимо з запасом, повз лінії
    fr, w, h = textbox(ox + ax_w * 0.30, oy - ax_h * 0.86,
                       "гранична затримка τ_max:\nна ω_c дістає межу PM",
                       size=11.5, color=POS, bold=True, fill="#fdecea", stroke=POS)
    P.append(fr)
    fr, w, h = textbox(ox + ax_w * 0.74, oy - ax_h * 0.30,
                       "мала затримка:\nзапас лишається",
                       size=11.5, color=NEG, bold=True, fill="#eaf0fd", stroke=NEG)
    P.append(fr)

    # висновок-формула під віссю
    fr, w, h = textbox(W / 2, H - 40,
                       "Межа розгойдування:  τ_max = PM / ω_c.  "
                       "Важелі проти лагу: ↓τ,  ↓ω_c (веди повільніше),  або предиктивний дисплей.",
                       size=13, bold=True, fill="#eef2f7", stroke=INK)
    P.append(fr)

    render("img/phase-margin.svg", W, H, *P)


# ── Фігура D2: компроміс глибини буфера (лаг ⇄ сіпання) ──────────────────────
# Ідея: дві біди тягнуть у різні боки з глибиною буфера. Лаг росте лінійно,
# частка кадрів «не встиг» падає (хвіст джитера). Ідеалу нема — лише точка.
def fig_buffer_tradeoff():
    W, H = 940, 520
    P = []
    P.append(text(W / 2, 34, "Буфер джитера: торг без ідеального розв'язку",
                  size=18, bold=True))

    ox, oy = 120, 400
    ax_w, ax_h = W - 240, 300
    P.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    P.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    P.append(text(ox + ax_w - 4, oy + 34, "глибина буфера →", size=13,
                  color=MUTED, anchor="end"))

    # крива 1: ЛАГ росте лінійно (червона) — «більший буфер = більший лаг»
    n = 60
    lag_pts = []
    for i in range(n + 1):
        t = i / n
        x = ox + t * ax_w
        y = oy - t * ax_h * 0.92
        lag_pts.append((x, y))
    for a, b in zip(lag_pts, lag_pts[1:]):
        P.append(line(a[0], a[1], b[0], b[1], color=POS, sw=2.6))

    # крива 2: частка «не встиг» падає (хвіст джитера) — синя, спадна експонента
    miss_pts = []
    for i in range(n + 1):
        t = i / n
        x = ox + t * ax_w
        y = oy - (ax_h * 0.9) * math.exp(-4.2 * t)
        miss_pts.append((x, y))
    for a, b in zip(miss_pts, miss_pts[1:]):
        P.append(line(a[0], a[1], b[0], b[1], color=NEG, sw=2.6))

    # робоча точка — де криві близькі (компроміс), приблизно t≈0.42
    tw = 0.42
    wx = ox + tw * ax_w
    P.append(line(wx, oy, wx, oy - ax_h * 0.86, color=FIELD, sw=1.8, dash="5 4"))
    P.append(circle(wx, oy - tw * ax_h * 0.92, 5.5, fill=POS, stroke=POS))
    P.append(circle(wx, oy - (ax_h * 0.9) * math.exp(-4.2 * tw), 5.5, fill=NEG, stroke=NEG))
    fr, w, h = textbox(wx, oy + 30, "робоча точка\n(компроміс)", size=11.5,
                       color=FIELD, bold=True, fill="#e9f7ef", stroke=FIELD)
    P.append(fr)

    # підписи кривих — далеко одна від одної й від ліній
    fr, w, h = textbox(ox + ax_w * 0.80, oy - ax_h * 0.86,
                       "ЛАГ ↑\nросте з глибиною", size=12, color=POS, bold=True,
                       fill="#fdecea", stroke=POS)
    P.append(fr)
    fr, w, h = textbox(ox + ax_w * 0.80, oy - ax_h * 0.30,
                       "«не встиг» ↓\nхвіст джитера гасне", size=12, color=NEG,
                       bold=True, fill="#eaf0fd", stroke=NEG)
    P.append(fr)

    # краї осі — крайні режими
    fr, w, h = textbox(ox + ax_w * 0.13, oy - ax_h * 0.52,
                       "дрібний:\nмалий лаг,\nале сіпається", size=11, bold=True,
                       fill="#f4f6f8", stroke=MUTED)
    P.append(fr)

    fr, w, h = textbox(W / 2, H - 40,
                       "І лаг, і повну плавність одночасно — не можна. Обираєш точку на кривій; "
                       "адаптивний буфер рухає її під ефір.",
                       size=13, bold=True, fill="#eef2f7", stroke=INK)
    P.append(fr)

    render("img/buffer-tradeoff.svg", W, H, *P)


# ── Фігура D3: двобічний сторожовий таймер (uplink / downlink) ───────────────
# Ідея: лінк гине з двох боків ОКРЕМО. Ровер стереже uplink, пульт — downlink.
# Найгірше — uplink живий, downlink мертвий: команди йдуть, оператор осліп.
def fig_two_sided_watchdog():
    W, H = 980, 470
    P = []
    P.append(text(W / 2, 34, "Лінк гине з двох боків окремо — стережи обидва кінці",
                  size=17, bold=True))

    # пульт ліворуч, ровер праворуч
    px, rx, cy = 175, W - 185, 175
    fr, w, h = textbox(px, cy, "ПУЛЬТ / GCS\nсторож на DOWNLINK\n(чи чую телеметрію?)",
                       size=12.5, bold=True, fill="#eef2f7", stroke=NEG, min_w=200)
    P.append(fr)
    fr, w, h = textbox(rx, cy, "РОВЕР\nсторож на UPLINK\n(чи чую команди?)",
                       size=12.5, bold=True, fill="#e9f7ef", stroke=FIELD, min_w=200)
    P.append(fr)

    # uplink угорі (пульт → ровер), команди
    up_y = 92
    P.append(arrow(px + 105, up_y, rx - 105, up_y, color=FIELD, sw=2.4))
    fr, w, h = textbox((px + rx) / 2, up_y - 26,
                       "UPLINK ↑  команди + серцебиття пульта",
                       size=12, color=FIELD, bold=True, fill="#e9f7ef", stroke=FIELD)
    P.append(fr)

    # downlink унизу (ровер → пульт), телеметрія/відео
    dn_y = 258
    P.append(arrow(rx - 105, dn_y, px + 105, dn_y, color=NEG, sw=2.4))
    fr, w, h = textbox((px + rx) / 2, dn_y + 26,
                       "DOWNLINK ↓  телеметрія + відео ровера",
                       size=12, color=NEG, bold=True, fill="#eaf0fd", stroke=NEG)
    P.append(fr)

    # найгірший випадок — окрема виноска внизу, широка
    fr, w, h = textbox(W / 2, H - 44,
                       "Найпідступніше: UPLINK живий, DOWNLINK мертвий — команди долітають, "
                       "та оператор веде машину НАОСЛІП.\n"
                       "Тому ровер входить у failsafe і коли пульт перестав його ЧУТИ, не лише коли сам оглух.",
                       size=12.5, bold=True, fill="#fdecea", stroke=POS)
    P.append(fr)

    render("img/two-sided-watchdog.svg", W, H, *P)


# ── Фігура D4: скінченний автомат failsafe (несиметричний) ───────────────────
# Ідея: 4 стани в лінію за тишею; підйом обережний і поетапний, повернення в
# NORMAL — миттєве з будь-якого стану (єдина зворотна дуга внизу).
def fig_failsafe_fsm():
    W, H = 1080, 470
    P = []
    P.append(text(W / 2, 34, "Failsafe як скінченний автомат: підйом обережний, повернення миттєве",
                  size=16.5, bold=True))

    cy = 165
    states = [
        ("NORMAL",   "виконуй\nкоманди",           FIELD, "#e9f7ef"),
        ("HOLD",     "тримай курс,\nне гальмуй",    "#b8860b", "#fdf6e3"),
        ("SAFE-STOP","плавно стій,\nмаяк",          POS,      "#fdecea"),
        ("RTL / чекай","за політикою\nмісії",       NEG,      "#eaf0fd"),
    ]
    n = len(states)
    x0, x1 = 130, W - 130
    xs = [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]
    box_w = [0] * n
    for i, (nm, sub, col, fill) in enumerate(states):
        fr, w, h = textbox(xs[i], cy, "%s\n%s" % (nm, sub), size=13, bold=True,
                           color=col, fill=fill, stroke=col, min_w=170)
        box_w[i] = w
        P.append(fr)

    # прямі переходи вправо (підйом по тривозі) з підписом-порогом НАД стрілкою
    thr = ["тиша > 0.3 с", "тиша > 1 с", "тиша > 5 с"]
    for i in range(n - 1):
        ax = xs[i] + box_w[i] / 2 + 6
        bx = xs[i + 1] - box_w[i + 1] / 2 - 6
        P.append(arrow(ax, cy - 14, bx, cy - 14, color=INK, sw=2.2))
        P.append(text((ax + bx) / 2, cy - 30, thr[i], size=11.5, color=INK, bold=True))

    # єдина зворотна дуга внизу: будь-який стан → NORMAL миттєво
    back_y = cy + 78
    P.append(line(xs[-1], cy + 40, xs[-1], back_y, color=FIELD, sw=2.2))
    P.append(arrow(xs[-1], back_y, xs[0], back_y, color=FIELD, sw=2.4))
    P.append(line(xs[0], back_y, xs[0], cy + 40, color=FIELD, sw=2.2))
    for i in (1, 2):  # проміжні стани теж падають у NORMAL
        P.append(line(xs[i], cy + 40, xs[i], back_y, color=FIELD, sw=1.6, dash="4 4"))
        P.append(circle(xs[i], back_y, 3.5, fill=FIELD, stroke=FIELD))
    P.append(text((xs[0] + xs[-1]) / 2, back_y + 24,
                  "прийшло серцебиття → МИТТЄВО в NORMAL (з будь-якого стану)",
                  size=12.5, color=FIELD, bold=True))

    fr, w, h = textbox(W / 2, H - 36,
                       "Несиметрія навмисна: у тривогу заходь обережно (кілька ударів поспіль), "
                       "із тривоги виходь миттєво — повернення зв'язку завжди безпечне.",
                       size=12.5, bold=True, fill="#eef2f7", stroke=INK)
    P.append(fr)

    render("img/failsafe-fsm.svg", W, H, *P)


if __name__ == "__main__":
    fig_phase_margin()
    fig_buffer_tradeoff()
    fig_two_sided_watchdog()
    fig_failsafe_fsm()
    print("OK: 4 detailed figures -> img/")
