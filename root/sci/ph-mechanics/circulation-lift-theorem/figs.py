# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def airfoil_path(cx, cy, chord, thick, aoa_deg, camber=0.10):
    """Повертає d-атрибут для крила з опущеним хвостом (камбер) під кутом атаки."""
    import math
    a = math.radians(-aoa_deg)  # додатний кут атаки — ніс угору
    ca, sa = math.cos(a), math.sin(a)
    top, bot = [], []
    N = 24
    for i in range(N + 1):
        t = i / N
        x = (t - 0.5) * chord
        # товщина за простим профілем
        th = thick * (1 - (2 * t - 1) ** 2) ** 0.5
        cam = camber * chord * (t - t * t) * 4  # опукла серединна лінія
        yt = -th / 2 - cam
        yb = th / 2 - cam
        top.append((x, yt))
        bot.append((x, yb))
    pts = top + bot[::-1]
    d = []
    for k, (x, y) in enumerate(pts):
        xr = cx + x * ca - y * sa
        yr = cy + x * sa + y * ca
        d.append(("M" if k == 0 else "L") + "%.1f %.1f" % (xr, yr))
    return " ".join(d) + " Z"


# ── Фігура 1: циркуляція як контурний інтеграл швидкості ──────────────────────
def fig_circulation():
    import math
    W, H = 720, 430
    cx, cy = 360, 220
    body = []
    # крило
    d = airfoil_path(cx, cy, 210, 26, 6)
    body.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (d, FILL, LINE))
    # замкнений контур C навколо профілю (еліпс), пунктиром
    rx, ry = 185, 92
    body.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" '
                'stroke="%s" stroke-width="1.8" stroke-dasharray="7 5"/>'
                % (cx, cy, rx, ry, FIELD))
    body.append(text(cx + rx - 6, cy - ry - 8, "контур C", size=13, color=FIELD, bold=True, anchor="end"))
    # дотичні стрілки швидкості вздовж контуру: зверху довші (швидше), знизу коротші
    def on_ellipse(ang):
        return cx + rx * math.cos(ang), cy - ry * math.sin(ang)
    def tangent(ang):
        # напрям обходу проти годинникової — дотична (-sin, -cos) у екранних координатах
        tx, ty = -rx * math.sin(ang), -ry * math.cos(ang)
        n = math.hypot(tx, ty)
        return tx / n, ty / n
    # відбираємо точки; довжина стрілки ~ локальній швидкості (більша зверху)
    for deg in range(20, 360, 40):
        ang = math.radians(deg)
        px, py = on_ellipse(ang)
        tx, ty = tangent(ang)
        top = py < cy                      # верхня половина контуру
        speed = 30 if top else 16          # зверху потік швидший
        body.append(arrow(px, py, px + tx * speed, py + ty * speed, color=NEG if top else POS, sw=2.2))
    body.append(text(cx, cy - ry + 26, "зверху швидше (внесок +)", size=12, color=NEG))
    body.append(text(cx, cy + ry - 14, "знизу повільніше (внесок −)", size=12, color=POS))
    # формула
    body.append(fitbox(cx - 150, 356, 300, 46,
                       "Γ = ∮  v · dl   (обхід проти годинникової)",
                       size=15, bold=True, fill="#eef7f0", stroke=FIELD))
    body.append(text(cx, cy - ry - 40, "сума дотичної швидкості по колу ≠ 0 — є циркуляція",
                     size=12.5, color=MUTED))
    render(os.path.join(OUT, "circulation.svg"), W, H, *body,
           title="Циркуляція Γ — контурний інтеграл швидкості")


# ── Фігура 2: умова Кутти — вибір єдиного режиму на гострій кромці ────────────
def fig_kutta():
    import math
    W, H = 720, 400
    body = []
    # два профілі поруч: ліворуч «неправильний» (Γ=0), праворуч «правильний» (Кутта)
    for side, (bx, ok) in enumerate(((190, False), (530, True))):
        by = 210
        d = airfoil_path(bx, by, 190, 24, 7)
        # хвіст профілю (гостра задня кромка) — правий край
        te_x = bx + 190 / 2 * math.cos(math.radians(-7)) - 0 * math.sin(math.radians(-7))
        te_y = by + 190 / 2 * math.sin(math.radians(-7))
        # лінії потоку
        for off in (-40, -14, 14, 40):
            y0 = by + off
            x0 = bx - 150
            if ok:
                # плавний схід: обидві поверхні сходяться на кромці й ідуть похило вниз
                xm = te_x + 4
                drop = 20
                pth = "M%.1f %.1f Q%.1f %.1f %.1f %.1f" % (x0, y0, bx, y0 - 5, xm, y0 + (drop if off < 0 else drop * 0.5))
                body.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (pth, NEG))
            else:
                # нижня лінія огинає кромку знизу вгору — розворот на вістрі
                if off > 0:
                    # струмінь знизу завертає вгору навколо кромки
                    pth = ("M%.1f %.1f Q%.1f %.1f %.1f %.1f T %.1f %.1f"
                           % (x0, y0, bx, y0 + 4, te_x + 6, by + 30,
                              te_x + 14, by - 20))
                    body.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (pth, POS))
                else:
                    pth = "M%.1f %.1f Q%.1f %.1f %.1f %.1f" % (x0, y0, bx, y0 - 4, te_x + 6, y0 - 4)
                    body.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (pth, MUTED))
        body.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (d, FILL, LINE))
        # позначка кромки
        body.append(circle(te_x + 4, te_y, 3.5, fill=INK, stroke=INK))
        if ok:
            body.append(text(bx, 120, "умова Кутти виконана", size=14, bold=True, color=FIELD))
            body.append(text(bx, 138, "потік гладко сходить із кромки", size=12, color=MUTED))
            body.append(text(bx, by + 96, "єдина Γ, що робить це — реальна", size=12, color=FIELD))
        else:
            body.append(text(bx, 120, "фізично неможливо (Γ = 0)", size=14, bold=True, color=POS))
            body.append(text(bx, 138, "розворот на вістрі → нескінченна швидкість", size=11.5, color=MUTED))
            body.append(text(bx, by + 96, "в'язкість такого не терпить", size=12, color=POS))
    render(os.path.join(OUT, "kutta.svg"), W, H, *body,
           title="Умова Кутти добирає єдине значення циркуляції")


# ── Фігура 3: пусковий вихор і збереження циркуляції (Кельвін) ────────────────
def fig_starting_vortex():
    import math
    W, H = 720, 360
    body = []
    cy = 190
    # крило зліва
    wx = 210
    d = airfoil_path(wx, cy, 150, 20, 8)
    body.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (d, FILL, LINE))
    # зв'язаний вихор +Γ навколо крила (кругова стрілка)
    def curl(cx0, cy0, r, cw, color):
        # дуга ~300° зі стрілкою на кінці; cw=+1 за годинниковою
        a0, a1 = math.radians(30), math.radians(300)
        x0 = cx0 + r * math.cos(a0); y0 = cy0 - r * math.sin(a0)
        x1 = cx0 + r * math.cos(a1); y1 = cy0 - r * math.sin(a1)
        sweep = 1 if cw > 0 else 0
        p = ('<path d="M%.1f %.1f A %.1f %.1f 0 1 %d %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>'
             % (x0, y0, r, r, sweep, x1, y1, color))
        return p
    body.append(curl(wx, cy, 40, +1, FIELD))
    body.append(text(wx, cy - 58, "зв'язаний вихор +Γ", size=13, bold=True, color=FIELD))
    body.append(text(wx, cy + 66, "на крилі", size=12, color=MUTED))
    # пусковий вихор −Γ позаду, збіг у місці старту
    sx = 540
    body.append(curl(sx, cy, 34, -1, POS))
    body.append(text(sx, cy - 52, "пусковий вихор −Γ", size=13, bold=True, color=POS))
    body.append(text(sx, cy + 60, "лишився там, де рушили", size=12, color=MUTED))
    # стрілка руху крила
    body.append(arrow(wx + 90, cy, sx - 60, cy, color=MUTED, sw=1.6))
    body.append(text((wx + sx) / 2, cy - 10, "крило полетіло →", size=12, color=MUTED))
    # баланс
    body.append(fitbox(W / 2 - 165, 300, 330, 44,
                       "+Γ (крило)  +  (−Γ) (слід)  =  0   — теорема Кельвіна",
                       size=13.5, bold=True, fill="#eef7f0", stroke=FIELD))
    render(os.path.join(OUT, "starting-vortex.svg"), W, H, *body,
           title="Циркуляція народжується парою: крило й пусковий вихор")


if __name__ == "__main__":
    fig_circulation()
    fig_kutta()
    fig_starting_vortex()
    print("figs done")
