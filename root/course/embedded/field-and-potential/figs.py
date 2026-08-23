# -*- coding: utf-8 -*-
"""Фігури до детальної статті «Поле й потенціал».
Кожна несе вагу: незалежність від шляху, друга похідна (Пуассон/Лаплас),
умови на межі, сідло Ерншоу. Запуск: python figs.py  → ./img/*.svg
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Незалежність від шляху + нульовий контур ─────────────────────────────
def fig_path_independence():
    W, H = 720, 340
    els = []
    # --- ліва панель: три шляхи з B в A ---
    els.append(text(180, 52, "Три шляхи — та сама різниця", size=15, bold=True))
    ax, ay = 300, 250   # A (верх-права точка)
    bx, by = 70, 250    # B (низ-ліва)
    # легкий фон-рельєф: кілька ізоліній (діагональні)
    for i, off in enumerate((-40, 0, 40, 80, 120)):
        els.append(line(60 + off, 300, 200 + off, 90, color="#d9dee6", sw=1.2, dash="4 4"))
    # три шляхи різної форми
    els.append('<path d="M%d %d L%d %d" stroke="%s" stroke-width="2.4" fill="none"/>' % (bx, by, ax, ay, FIELD))
    els.append('<path d="M%d %d C %d %d, %d %d, %d %d" stroke="%s" stroke-width="2.4" fill="none"/>'
               % (bx, by, 90, 120, 260, 300, ax, ay, POS))
    els.append('<path d="M%d %d C %d %d, %d %d, %d %d" stroke="%s" stroke-width="2.4" fill="none"/>'
               % (bx, by, 250, 250, 120, 120, ax, ay, NEG))
    els.append(circle(bx, by, 6, fill=INK, stroke=INK))
    els.append(text(bx - 4, by + 22, "B", size=15, bold=True))
    els.append(circle(ax, ay, 6, fill=INK, stroke=INK))
    els.append(text(ax + 12, ay + 6, "A", size=15, bold=True))
    box, _, _ = textbox(185, 300, "−∫E·dl однаковий → V(A) єдине число",
                        size=12, pad=7)
    els.append(box)
    # роздільник
    els.append(line(370, 60, 370, 300, color="#cfd6df", sw=1.4, dash="3 5"))

    # --- права панель: замкнений контур, ∮ = 0 ---
    els.append(text(545, 52, "Замкнений контур", size=15, bold=True))
    cx, cy = 545, 185
    # петля
    els.append('<path d="M%d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d Z" '
               'stroke="%s" stroke-width="2.4" fill="none"/>'
               % (cx - 90, cy, cx - 90, cy - 80, cx + 90, cy - 80, cx + 90, cy,
                  cx + 90, cy + 80, cx - 90, cy + 80, cx - 90, cy, FIELD))
    # стрілки напрямку обходу
    els.append(arrow(cx + 90, cy - 6, cx + 90, cy + 30, color=FIELD, sw=2.2))
    els.append(arrow(cx - 90, cy + 6, cx - 90, cy - 30, color=FIELD, sw=2.2))
    els.append(text(cx, cy - 2, "∮ E·dl = 0", size=17, bold=True, color=INK))
    box2, _, _ = textbox(cx, cy + 118, "вийшов і повернувся на ту саму висоту",
                         size=12, pad=7)
    els.append(box2)
    render(os.path.join(OUT, 'path-independence.svg'), W, H, *els)


# ── 2. Друга похідна: горб над +, яма над −, пряма в порожнечі ───────────────
def fig_second_derivative():
    W, H = 720, 360
    els = []
    els.append(text(W / 2, 26, "Заряд задає кривину потенціалу V", size=16, bold=True))
    # осі
    x0, x1 = 60, 660
    base = 250   # рівень V=0 умовний
    els.append(line(x0, base, x1, base, color=MUTED, sw=1.2, dash="4 4"))
    els.append(text(x0 - 6, base + 4, "V", size=13, color=MUTED, anchor="end"))

    # профіль V(x): горб зліва (над +), рівний посередині, яма справа (над −)
    pts = []
    for px in range(x0, x1 + 1, 4):
        t = (px - x0) / (x1 - x0)
        # горб центр ~0.2, яма центр ~0.8
        hump = 95 * math.exp(-((t - 0.2) ** 2) / (2 * 0.010))
        dip = -95 * math.exp(-((t - 0.8) ** 2) / (2 * 0.010))
        y = base - (hump + dip)
        pts.append((px, y))
    path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    els.append('<path d="%s" stroke="%s" stroke-width="2.6" fill="none"/>' % (path, INK))

    # заряди під профілем
    xplus = x0 + 0.2 * (x1 - x0)
    xminus = x0 + 0.8 * (x1 - x0)
    xflat = x0 + 0.5 * (x1 - x0)
    els.append(plus(xplus, 305, r=12))
    els.append(minus(xminus, 305, r=12))
    # підписи ділянок
    els.append(textbox(xplus, 120, ["горб угору", "∇²V < 0"], size=12, pad=6)[0])
    els.append(textbox(xminus, 330, ["яма вниз", "∇²V > 0"], size=12, pad=6)[0])
    els.append(textbox(xflat, base - 34, ["порожньо:", "∇²V = 0"], size=12, pad=6)[0])
    render(os.path.join(OUT, 'second-derivative.svg'), W, H, *els)


# ── 3. Умови на межі ────────────────────────────────────────────────────────
def fig_boundary():
    W, H = 720, 360
    els = []
    els.append(text(W / 2, 26, "Поле й потенціал на межі двох середовищ", size=16, bold=True))
    my = 190  # лінія межі
    els.append(rect(60, 60, 600, my - 60, fill="#eef4ff", stroke="none"))
    els.append(rect(60, my, 600, 300 - my + 60 - 60, fill="#fff5ee", stroke="none"))
    els.append(line(60, my, 660, my, color=INK, sw=2.4))
    els.append(text(650, 80, "середовище 1", size=12, color=NEG, anchor="end"))
    els.append(text(650, my + 26, "середовище 2", size=12, color=POS, anchor="end"))
    els.append(text(70, my - 8, "межа", size=12, color=INK))

    # E∥ неперервне: горизонтальні стрілки однакові по обидва боки
    els.append(arrow(120, my - 45, 200, my - 45, color=FIELD, sw=2.2))
    els.append(arrow(120, my + 45, 200, my + 45, color=FIELD, sw=2.2))
    els.append(text(230, my - 45 + 4, "E∥ рівне", size=12, color=FIELD, anchor="start"))
    els.append(text(230, my + 45 + 4, "E∥ рівне", size=12, color=FIELD, anchor="start"))

    # E⊥ стрибає: вертикальні стрілки різної довжини
    els.append(arrow(430, my - 20, 430, my - 75, color=FIELD, sw=2.4))   # коротша зверху
    els.append(arrow(430, my + 20, 430, my + 95, color=FIELD, sw=2.4))   # довша знизу
    els.append(text(448, my - 50, "E⊥", size=12, color=FIELD, anchor="start"))
    els.append(text(448, my + 60, "E⊥ (більше)", size=12, color=FIELD, anchor="start"))
    # заряд на межі
    els.append(text(520, my - 8, "σ", size=15, color=POS, bold=True))
    for sx in range(500, 561, 20):
        els.append(plus(sx, my, r=7))

    # підпис-формула
    box, _, _ = textbox(W / 2, 320, "V неперервний · E∥ неперервне · E⊥ стрибає на σ/ε₀",
                        size=13, pad=8)
    els.append(box)
    render(os.path.join(OUT, 'boundary-conditions.svg'), W, H, *els)


# ── 4. Сідло Ерншоу ─────────────────────────────────────────────────────────
def fig_earnshaw():
    W, H = 720, 360
    els = []
    els.append(text(W / 2, 26, "Порожній простір допускає лише сідло", size=16, bold=True))
    cx, cy = 300, 195
    # сідлові контурні лінії (гіперболи-натяк): дві родини
    for k in (0.6, 1.0, 1.6):
        # x²−y²=c форма, малюємо як пара дуг
        pts_r, pts_l = [], []
        for tt in range(-90, 91, 6):
            u = tt / 60.0
            X = 55 * math.cosh(u) * k
            Y = 55 * math.sinh(u) * k
            pts_r.append((cx + X, cy - Y))
            pts_l.append((cx - X, cy - Y))
        els.append('<path d="M %s" stroke="%s" stroke-width="1.4" fill="none"/>'
                   % (" L ".join("%.1f %.1f" % p for p in pts_r), "#b9c2cf"))
        els.append('<path d="M %s" stroke="%s" stroke-width="1.4" fill="none"/>'
                   % (" L ".join("%.1f %.1f" % p for p in pts_l), "#b9c2cf"))
        pts_u, pts_d = [], []
        for tt in range(-90, 91, 6):
            u = tt / 60.0
            X = 55 * math.sinh(u) * k
            Y = 55 * math.cosh(u) * k
            pts_u.append((cx + X, cy - Y))
            pts_d.append((cx + X, cy + Y))
        els.append('<path d="M %s" stroke="%s" stroke-width="1.4" fill="none"/>'
                   % (" L ".join("%.1f %.1f" % p for p in pts_u), "#d7b9c2"))
        els.append('<path d="M %s" stroke="%s" stroke-width="1.4" fill="none"/>'
                   % (" L ".join("%.1f %.1f" % p for p in pts_d), "#d7b9c2"))
    # осі сідла: вниз (яма) синьою, геть (гірка) червоною
    els.append(arrow(cx, cy, cx, cy - 95, color=NEG, sw=2.6))
    els.append(arrow(cx, cy, cx, cy + 95, color=NEG, sw=2.6))
    els.append(arrow(cx, cy, cx - 130, cy, color=POS, sw=2.6))
    els.append(arrow(cx, cy, cx + 130, cy, color=POS, sw=2.6))
    els.append(circle(cx, cy, 5, fill=INK, stroke=INK))
    els.append(text(cx, cy - 105, "повертає (яма)", size=12, color=NEG))
    els.append(text(cx + 140, cy + 4, "тікає (гірка)", size=12, color=POS, anchor="start"))

    # права колонка: логіка знаків
    lines = [
        "мінімум: усі кривини > 0 → сума > 0  ✗",
        "максимум: усі кривини < 0 → сума < 0  ✗",
        "сідло: знаки різні → сума = 0  ✓",
        "",
        "Лаплас вимагає ∇²V = 0",
        "→ ями-пастки не буває",
    ]
    els.append(fitbox(500, 90, 200, 200, "\n".join(lines), size=12, pad=12))
    render(os.path.join(OUT, 'earnshaw-saddle.svg'), W, H, *els)


# ── 5. Радіальне поле: чому робота залежить лише від r (вставка math) ─────────
def fig_radial_work():
    """Крок dl розкладається на радіальну (вздовж E) і колову (⊥ E) складові.
    Тільки радіальна дає внесок E·dl → робота залежить лише від зміни r."""
    import math as _m
    W, H = 720, 400
    els = []
    els.append(text(W / 2, 26, "Кулонівське поле радіальне: працює лише рух по r", size=16, bold=True))
    qx, qy = 120, 330   # заряд у лівому нижньому куті
    els.append(plus(qx, qy, r=13))
    els.append(text(qx, qy + 32, "заряд", size=12, color=MUTED))

    # кілька радіальних променів поля E (тонкі зелені стрілки геть від заряду, вгору-праворуч)
    for ang in (-20, -40, -60, -80):
        a = _m.radians(ang)
        els.append(arrow(qx + 26 * _m.cos(a), qy + 26 * _m.sin(a),
                         qx + 250 * _m.cos(a), qy + 250 * _m.sin(a),
                         color="#a9d9bd", sw=1.6))
    els.append(text(qx + 210, qy - 205, "лінії E", size=12, color=FIELD, anchor="start"))

    # точка на шляху й крихітний крок dl, розкладений на dr (вздовж променя) + коловий
    a0 = _m.radians(-50)
    r0 = 190
    px, py = qx + r0 * _m.cos(a0), qy + r0 * _m.sin(a0)
    ur = (_m.cos(a0), _m.sin(a0))            # уздовж радіуса (напрям E)
    ut = (-_m.sin(a0), _m.cos(a0))           # поперек (коловий)
    L = 110
    drx, dry = px + ur[0] * L, py + ur[1] * L                        # радіальна складова dr
    dlx, dly = drx + ut[0] * L, dry + ut[1] * L                      # dl = dr + коловий
    els.append(line(drx, dry, dlx, dly, color=NEG, sw=2.2, dash="5 3"))  # колова частина
    els.append(arrow(px, py, drx, dry, color=POS, sw=2.6))          # dr (вздовж E)
    els.append(arrow(px, py, dlx, dly, color=INK, sw=2.8))          # dl (повний крок)
    els.append(circle(px, py, 4.5, fill=INK, stroke=INK))
    els.append(text(dlx + 6, dly + 16, "dl", size=14, bold=True, anchor="start"))
    els.append(text((px + drx) / 2 - 4, (py + dry) / 2 - 8, "dr", size=14, bold=True, color=POS, anchor="end"))
    els.append(text(drx + 30, dry + 30, "⊥ E → внесок 0", size=11, color=NEG, anchor="start"))

    # права колонка: висновок формулою
    lines = [
        "E · dl = E · (dr + коловий)",
        "коловий крок ⊥ E → внесок 0",
        "лишається  E·dr = E(r)·dr",
        "",
        "робота = ∫ E(r) dr",
        "залежить ЛИШЕ від r-кінців —",
        "хоч як петляй шлях між ними",
    ]
    els.append(fitbox(440, 120, 262, 150, "\n".join(lines), size=12, pad=12))
    render(os.path.join(OUT, 'radial-work.svg'), W, H, *els)


# ── 6. Місток локальне↔глобальне: ∮ малого контуру = rot E · площа ────────────
def fig_curl_bridge():
    """Стокс: циркуляція по крихітному контуру = завихреність × площа.
    Велику петлю ділимо сіткою — внутрішні ребра гасяться, лишається край."""
    W, H = 720, 360
    els = []
    els.append(text(W / 2, 26, "Мозаїка контурів: сума завихрень = обхід краю", size=16, bold=True))

    # ліва панель: велика петля, порізана на клітинки
    ox, oy, cell, n = 70, 70, 46, 4
    for i in range(n):
        for j in range(n):
            x, y = ox + i * cell, oy + j * cell
            els.append(rect(x, y, cell, cell, fill="#f0f7f2", stroke="#c9e3d5", sw=1.0, rx=2))
            # маленька колова стрілочка-натяк у центрі
            els.append(text(x + cell / 2, y + cell / 2 + 4, "↺", size=15, color="#7fc4a2"))
    # жирний край усієї області
    els.append(rect(ox, oy, cell * n, cell * n, fill="none", stroke=FIELD, sw=3.0, rx=2))
    els.append(text(ox + cell * n / 2, oy + cell * n + 24,
                    "внутрішні ребра гасяться попарно", size=12, color=MUTED))
    els.append(text(ox + cell * n + 6, oy - 6, "край", size=12, color=FIELD, anchor="start"))

    # роздільник
    els.append(line(340, 60, 340, 300, color="#cfd6df", sw=1.4, dash="3 5"))

    # права панель: один крихітний квадратик + формула Стокса
    sx, sy, s = 430, 120, 90
    els.append(rect(sx, sy, s, s, fill="#eef4ff", stroke=NEG, sw=2.2, rx=3))
    # стрілки обходу проти годинника
    els.append(arrow(sx, sy + s, sx, sy, color=NEG, sw=2.0))
    els.append(arrow(sx, sy, sx + s, sy, color=NEG, sw=2.0))
    els.append(arrow(sx + s, sy, sx + s, sy + s, color=NEG, sw=2.0))
    els.append(arrow(sx + s, sy + s, sx, sy + s, color=NEG, sw=2.0))
    els.append(text(sx + s / 2, sy + s / 2 + 5, "ΔA", size=14, bold=True))
    lines = [
        "∮ E·dl  =  (rot E)·ΔA",
        "        (крихітний контур)",
        "",
        "усюди ∮=0  ⇔  rot E = 0",
        "у кожній точці",
    ]
    els.append(fitbox(sx - 20, sy + s + 24, 230, 110, "\n".join(lines), size=12, pad=12))
    render(os.path.join(OUT, 'curl-bridge.svg'), W, H, *els)


# ── 7. Змінне поле ламає потенціал: ∮E·dl = −dΦ/dt (індукція) ─────────────────
def fig_induction():
    """Через контур росте магнітний потік Φ → з'являється циркулююче поле E,
    ∮E·dl = −dΦ/dt ≠ 0. Одного числа V точці вже не приписати."""
    W, H = 720, 360
    els = []
    els.append(text(W / 2, 26, "Змінне поле: контур уже не нульовий", size=16, bold=True))

    cx, cy, R = 250, 200, 105
    # магнітний потік Φ, що росте (пучок хрестиків «у площину» + підпис)
    for dx in (-40, 0, 40):
        for dy in (-40, 0, 40):
            els.append(text(cx + dx, cy + dy + 4, "×", size=16, color=NEG))
    els.append(textbox(cx, cy - R - 22, "потік B росте: dΦ/dt", size=12, pad=6, stroke=NEG)[0])

    # циркулююче поле E — колові стрілки навколо
    import math as _m
    for k in range(4):
        a = _m.radians(90 * k + 20)
        a2 = _m.radians(90 * k + 70)
        x1, y1 = cx + R * _m.cos(a), cy + R * _m.sin(a)
        x2, y2 = cx + R * _m.cos(a2), cy + R * _m.sin(a2)
        els.append('<path d="M%.1f %.1f A %d %d 0 0 1 %.1f %.1f" stroke="%s" '
                   'stroke-width="2.6" fill="none" marker-end="url(#arrow)"/>'
                   % (x1, y1, R, R, x2, y2, FIELD))
    els.append(text(cx + R + 4, cy - 4, "E", size=14, color=FIELD, bold=True, anchor="start"))

    # права колонка: чому потенціалу нема
    lines = [
        "∮ E·dl  =  −dΦ/dt  ≠  0",
        "",
        "контур НЕ нульовий",
        "→ V(A) залежало б від шляху",
        "→ єдиного числа V нема",
        "",
        "статика: dΦ/dt = 0 → все як було",
    ]
    els.append(fitbox(450, 120, 250, 170, "\n".join(lines), size=12, pad=12))
    render(os.path.join(OUT, 'induction-loop.svg'), W, H, *els)


if __name__ == '__main__':
    fig_path_independence()
    fig_second_derivative()
    fig_boundary()
    fig_earnshaw()
    fig_radial_work()
    fig_curl_bridge()
    fig_induction()
    print("figs done ->", OUT)
