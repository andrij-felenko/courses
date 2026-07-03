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


# ── Фігура 1: баланс чотирьох сил у сталому польоті ──────────────────────────
def fig_forces():
    W, H = 640, 400
    cx, cy = 320, 210
    body = []
    # крило (профіль)
    d = airfoil_path(cx, cy, 200, 26, 6)
    body.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (d, FILL, LINE))
    body.append(text(cx, cy + 4, "крило", size=13, color=MUTED))
    # напрям польоту
    body.append(text(cx, 60, "напрям польоту →", size=13, color=MUTED))
    # чотири сили
    L = 120
    body.append(arrow(cx, cy - 18, cx, cy - 18 - L, color=FIELD, sw=3))
    body.append(text(cx + 14, cy - 18 - L + 22, "Підіймальна L", size=15, color=FIELD, bold=True, anchor="start"))
    body.append(arrow(cx, cy + 18, cx, cy + 18 + L, color=NEG, sw=3))
    body.append(text(cx + 14, cy + 18 + L - 8, "Вага mg", size=15, color=NEG, bold=True, anchor="start"))
    body.append(arrow(cx - 120, cy, cx - 120 + 90, cy, color=POS, sw=3))
    body.append(text(cx - 128, cy - 12, "Тяга T", size=15, color=POS, bold=True, anchor="end"))
    body.append(arrow(cx + 120, cy, cx + 120 - 90, cy, color=INK, sw=3))
    body.append(text(cx + 128, cy - 12, "Опір D", size=15, color=INK, bold=True, anchor="start"))
    # підпис рівноваги
    box = fitbox(180, 330, 280, 44, "сталий рівний політ:\nL = mg   і   T = D", size=14, bold=True, fill="#eef7f0", stroke=FIELD)
    body.append(box)
    render(os.path.join(OUT, "forces.svg"), W, H, *body,
           title="Чотири сили на літаку в польоті")


# ── Фігура 2: два погляди на підіймальну силу ────────────────────────────────
def fig_two_views():
    import math
    W, H = 720, 420
    body = []
    # ── ліворуч: різниця тисків ──
    lx, ly = 190, 200
    d = airfoil_path(lx, ly, 190, 24, 7)
    body.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (d, FILL, LINE))
    # мінуси зверху (низький тиск), плюси знизу (високий тиск)
    for i, dx in enumerate((-55, -18, 18, 55)):
        body.append(minus(lx + dx, ly - 34, 11))
    for i, dx in enumerate((-45, 0, 45)):
        body.append(plus(lx + dx, ly + 38, 11))
    body.append(text(lx, ly - 62, "зверху швидше → тиск нижчий", size=12, color=NEG))
    body.append(text(lx, ly + 74, "знизу повільніше → тиск вищий", size=12, color=POS))
    body.append(arrow(lx, ly - 4, lx, ly - 90, color=FIELD, sw=3))
    body.append(text(lx, 118, "погляд тиску", size=14, bold=True))

    # ── праворуч: відхилення повітря вниз (потік третього закону) ──
    rx, ry = 530, 200
    d = airfoil_path(rx, ry, 190, 24, 7)
    # лінії потоку: входять горизонтально, виходять з нахилом униз
    for k, off in enumerate((-46, -20, 20, 46)):
        y0 = ry + off
        x0 = rx - 150
        # злам біля хвоста
        xm = rx + 60
        drop = 26 - k * 2
        pth = "M%.1f %.1f Q%.1f %.1f %.1f %.1f" % (x0, y0, rx, y0 - 6, xm, y0 + drop * 0.4)
        body.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (pth, NEG))
        body.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>'
                     % (xm, y0 + drop * 0.4, xm + 60, y0 + drop, NEG, ))
    body.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (d, FILL, LINE))
    body.append(text(rx + 40, ry + 96, "повітря йде вниз (спутний потік)", size=12, color=NEG))
    body.append(arrow(rx, ry - 4, rx, ry - 84, color=FIELD, sw=3))
    body.append(text(rx, 118, "погляд імпульсу", size=14, bold=True))

    body.append(text(W / 2, 392, "той самий факт: крило штовхає повітря вниз — повітря штовхає крило вгору", size=12.5, color=MUTED))
    render(os.path.join(OUT, "two-views.svg"), W, H, *body,
           title="Дві мови однієї підіймальної сили")


# ── Фігура 3: крива підіймальної сили та зрив ────────────────────────────────
def fig_lift_curve():
    import math
    W, H = 620, 420
    ox, oy = 90, 340        # початок осей
    ax, ay = 500, 250       # довжини осей
    body = []
    body.append(line(ox, oy, ox + ax, oy, color=INK, sw=1.6))   # X
    body.append(line(ox, oy, ox, oy - ay, color=INK, sw=1.6))   # Y
    body.append(text(ox + ax - 6, oy + 30, "кут атаки α, °", size=13, anchor="end"))
    body.append(text(ox - 30, oy - ay + 10, "CL", size=13, bold=True))
    # крива: лінійна до ~15°, максимум, тоді спад
    def CL(a):
        if a <= 15:
            return 0.10 * (a + 2)          # нахил, нульова підйомна при -2° (камбер)
        else:
            return 1.7 - 0.06 * (a - 15) ** 1.6
    pts = []
    for a in range(-4, 26):
        cl = CL(a)
        X = ox + (a + 4) / 30 * ax
        Y = oy - max(0, cl) / 1.9 * ay
        pts.append("%.1f,%.1f" % (X, Y))
    body.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), FIELD))
    # позначка зриву
    aS = 15
    XS = ox + (aS + 4) / 30 * ax
    YS = oy - CL(aS) / 1.9 * ay
    body.append(circle(XS, YS, 5, fill=POS, stroke=POS))
    body.append(line(XS, YS, XS, oy, color=MUTED, sw=1, dash="4 3"))
    body.append(text(XS + 6, oy - 6, "≈15°", size=12, color=MUTED, anchor="start"))
    b = fitbox(XS - 4, YS - 52, 150, 34, "зрив (stall):\nCL падає різко", size=12, bold=True, fill="#fdecea", stroke=POS)
    body.append(b)
    # лінійна ділянка — підпис
    body.append(text(ox + 150, oy - 120, "CL росте з кутом", size=12.5, color=FIELD))
    render(os.path.join(OUT, "lift-curve.svg"), W, H, *body,
           title="Підіймальна сила проти кута атаки")


# ── Фігура 4: циркуляція як контурний інтеграл швидкості ──────────────────────
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


# ── Фігура 5: умова Кутти — вибір єдиного режиму на гострій кромці ────────────
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


# ── Фігура 6: пусковий вихор і збереження циркуляції (Кельвін) ────────────────
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


# ── Фігура: три незалежні відкриття зв'язку циркуляції з підйомом ─────────────
def fig_lift_theory_timeline():
    W, H = 760, 360
    body = []
    # вісь часу
    ax0, ax1, ay = 70, 690, 250
    body.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    body.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
                % (ax1 - 2, ay, ax1 + 18, ay, INK))
    # роки-риски: 1894 ... 1907
    def X(year):
        return ax0 + (year - 1892) / (1908 - 1892) * (ax1 - ax0)
    for yr in (1894, 1902, 1906, 1907):
        body.append(line(X(yr), ay - 6, X(yr), ay + 6, color=INK, sw=1.6))
        body.append(text(X(yr), ay + 24, str(yr), size=13, bold=True))

    # три дійові особи — картки над відповідними роками
    def card(cx, top, name, tag, note, col):
        b = fitbox(cx - 96, top, 192, 66, name + "\n" + tag + "\n" + note,
                   size=11.5, bold=False, fill=FILL, stroke=col)
        return b
    body.append(card(X(1894), 40, "Ланчестер (англ.)", "1894 — ідея, 1907 — книга",
                     "циркуляція + вихровий слід", FIELD))
    body.append(line(X(1894), 106, X(1894), ay - 8, color=FIELD, sw=1.4, dash="4 3"))

    body.append(card(X(1902), 132, "Кутта (нім.)", "1902 — теорія",
                     "зв'язок є, без точної формули", NEG))
    body.append(line(X(1902), 198, X(1902), ay - 8, color=NEG, sw=1.4, dash="4 3"))

    body.append(card(X(1906) + 8, 40, "Жуковський (рос.)", "1906 — публікація",
                     "перший дав L' = ρvΓ", POS))
    body.append(line(X(1906), 106, X(1906), ay - 8, color=POS, sw=1.4, dash="4 3"))

    body.append(text(W / 2, 320,
                     "три незалежні шляхи до одного зв'язку — фон Карман приписує всім трьом",
                     size=12.5, color=MUTED))
    render(os.path.join(OUT, "lift-theory-timeline.svg"), W, H, *body,
           title="Циркуляція й підйом: три відкривачі")


# ── Фігура: міф «однакового часу» проти виміру ───────────────────────────────
def fig_equal_time_myth():
    import math
    W, H = 720, 420
    body = []

    def wing(bx, by):
        d = airfoil_path(bx, by, 200, 26, 9)
        return '<path d="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (d, FILL, LINE)

    # ── верх: МІФ (частинки нібито зустрічаються позаду) ──
    bx, by = 300, 120
    body.append(text(bx, 52, "міф «однакового часу»", size=14, bold=True, color=POS))
    body.append(wing(bx, by))
    # дві частинки стартують разом ліворуч
    body.append(circle(bx - 130, by - 18, 4.5, fill=NEG, stroke=NEG))
    body.append(circle(bx - 130, by + 18, 4.5, fill=POS, stroke=POS))
    # верхня і нижня «зустрічаються» на кромці (пунктир)
    body.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5 4"/>'
                % (bx - 130, by - 18, bx, by - 40, bx + 108, by - 2, NEG))
    body.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5 4"/>'
                % (bx - 130, by + 18, bx, by + 30, bx + 108, by + 2, POS))
    body.append(circle(bx + 112, by, 5, fill=INK, stroke=INK))
    body.append(text(bx + 168, by - 4, "«зустрілися разом»", size=11.5, color=MUTED, anchor="start"))
    body.append(text(bx + 168, by + 14, "(так не буває)", size=11.5, color=POS, anchor="start"))

    # ── низ: ВИМІР (верхня долітає раніше) ──
    bx2, by2 = 300, 300
    body.append(text(bx2, 232, "що показує вимір", size=14, bold=True, color=FIELD))
    body.append(wing(bx2, by2))
    body.append(circle(bx2 - 130, by2 - 18, 4.5, fill=NEG, stroke=NEG))
    body.append(circle(bx2 - 130, by2 + 18, 4.5, fill=POS, stroke=POS))
    # верхня частинка вже далеко за кромкою; нижня ще позаду
    body.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
                % (bx2 - 130, by2 - 18, bx2, by2 - 44, bx2 + 168, by2 - 20, NEG))
    body.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
                % (bx2 - 130, by2 + 18, bx2, by2 + 32, bx2 + 92, by2 + 8, POS))
    body.append(circle(bx2 + 150, by2 - 20, 5, fill=NEG, stroke=NEG))   # верхня — попереду
    body.append(circle(bx2 + 84, by2 + 8, 5, fill=POS, stroke=POS))     # нижня — відстала
    body.append(text(bx2 + 176, by2 - 24, "верхня — попереду", size=11.5, color=NEG, anchor="start"))
    body.append(text(bx2 + 100, by2 + 30, "нижня відстала", size=11.5, color=POS, anchor="start"))

    render(os.path.join(OUT, "equal-time-myth.svg"), W, H, *body,
           title="Верх долітає до кромки раніше, а не «одночасно»")


if __name__ == "__main__":
    fig_forces()
    fig_two_views()
    fig_lift_curve()
    fig_circulation()
    fig_kutta()
    fig_starting_vortex()
    fig_lift_theory_timeline()
    fig_equal_time_myth()
    print("figs done")
