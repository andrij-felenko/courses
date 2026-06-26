# -*- coding: utf-8 -*-
"""Фігури до теми «Щільність енергії та потужності: конденсатор, суперконденсатор, акумулятор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Сталі кольори трьох класів сховищ (узгоджено між фігурами теми)
C_CAP  = NEG        # конденсатор — синій (швидкий, холодний)
C_SC   = "#caa24a"  # суперконденсатор — золотавий (посередині)
C_BAT  = POS        # акумулятор — червоний (енергія, хімія, тепло)


# ── 1. Площина Рагоне: енергія проти потужності ──────────────────────────────
def fig_ragone():
    """Центральна фігура. Логарифмічні осі: енергія (Вт·год/кг) проти потужності
    (Вт/кг). Три хмари — конденсатор, суперконденсатор, акумулятор — лягають на
    різні діагоналі сталого часу. Діагональ показує, ЗА ЯКИЙ ЧАС віддається запас."""
    W, H = 780, 540
    f = [text(W / 2, 28, "Площина Рагоне: за який час сховище віддає свій запас", size=16, bold=True)]
    ox, oy = 92, 430                 # початок координат (лівий-нижній кут поля)
    pw, ph = W - ox - 40, oy - 70

    # межі осей у декадах (10^k)
    ex0, ex1 = -3, 3                 # енергія: 10^-3 .. 10^3 Вт·год/кг
    py0, py1 = 1, 5                  # потужність: 10^1 .. 10^5 Вт/кг

    def X(loge):  # логарифм енергії -> піксель
        return ox + (loge - ex0) / (ex1 - ex0) * pw
    def Y(logp):  # логарифм потужності -> піксель
        return oy - (logp - py0) / (py1 - py0) * ph

    # сітка декад
    for k in range(ex0, ex1 + 1):
        f.append(line(X(k), oy, X(k), oy - ph, color="#e3e6ea", sw=1))
        lab = ("10%s" % _sup(k))
        f.append(text(X(k), oy + 18, lab, size=10, color=MUTED))
    for k in range(py0, py1 + 1):
        f.append(line(ox, Y(k), ox + pw, Y(k), color="#e3e6ea", sw=1))
        f.append(text(ox - 8, Y(k) + 4, "10%s" % _sup(k), size=10, color=MUTED, anchor="end"))
    # осі
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.6))
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.6))
    f.append(text(ox + pw / 2, oy + 40, "питома енергія, Вт·год/кг  (скільки запасено) →", size=11, color=INK))
    f.append('<text x="26" y="%.1f" font-family="%s" font-size="11" fill="%s" text-anchor="middle" transform="rotate(-90 26 %.1f)">питома потужність, Вт/кг  (як швидко віддає) ↑</text>'
             % (oy - ph / 2, FONT, INK, oy - ph / 2))

    # діагоналі сталого часу: P = E / t  =>  logP = logE - log10(t[год])
    # підписуємо час віддавання повного запасу
    times = [(1/3600., "1 с"), (1/60., "1 хв"), (1.0, "1 год"), (10.0, "10 год")]
    for t, lab in times:
        lt = math.log10(t)
        # лінія logP = logE - lt у межах поля
        e_a, e_b = ex0, ex1
        p_a, p_b = e_a - lt, e_b - lt
        # обрізати по вертикальних межах потужності
        pts = _clip(e_a, p_a, e_b, p_b, ex0, ex1, py0, py1)
        if pts:
            (xa, ya), (xb, yb) = pts
            f.append(line(X(xa), Y(ya), X(xb), Y(yb), color=MUTED, sw=1, dash="5 4"))
            # підпис біля верхнього кінця лінії
            f.append(text(X(xb) - 4, Y(yb) - 6, lab, size=9, color=MUTED, anchor="end", italic=True))

    # хмари трьох класів: (центр logE, logP, напівширина, напіввисота, колір, назва)
    clouds = [
        (-1.3, 4.3, 0.7, 0.5, C_CAP, "конденсатор"),     # ~0.05 Вт·год/кг, ~20 кВт/кг
        (0.85, 3.4, 0.55, 0.55, C_SC,  "суперконден-\nсатор"),# ~7 Вт·год/кг, ~2.5 кВт/кг
        (2.2,  2.6, 0.45, 0.6, C_BAT, "акумулятор"),     # ~160 Вт·год/кг, ~400 Вт/кг
    ]
    for cle, clp, dw, dh, col, nm in clouds:
        cx, cy = X(cle), Y(clp)
        rxp = (X(cle + dw) - X(cle - dw)) / 2
        ryp = (Y(clp - dh) - Y(clp + dh)) / 2
        f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" fill-opacity="0.18" stroke="%s" stroke-width="2"/>'
                 % (cx, cy, rxp, ryp, col, col))
        nlines = nm.count("\n") + 1
        ty0 = cy - (nlines - 1) * 11 * 1.3 / 2 + 4
        f.append(mtext(cx, ty0, nm, size=11, color=col, bold=True))

    # стрілка-висновок унизу ліворуч (вільне місце під хмарою конденсатора)
    f.append(fitbox(ox + 8, oy - 64, 252, 40,
                    "Праворуч-униз — більше енергії, але повільніше.\nЛіворуч-угору — менше енергії, зате миттєво.",
                    size=9.5, fill="#f6f7f9", stroke=MUTED, sw=1.2))
    render(os.path.join(IMG, "ragone.svg"), W, H, *f)


# ── 2. Чому конденсатор тримає так мало: поверхня проти об'єму ─────────────────
def fig_where():
    """ЧОМУ енергія різниться на порядки. Конденсатор тримає заряд на ДВОХ
    поверхнях (розділені діелектриком); суперконденсатор — на величезній
    розвиненій поверхні пористого вугілля; акумулятор — у ВСЬОМУ об'ємі
    матеріалу через хімічну реакцію. Звідси й розрив у щільності енергії."""
    W, H = 820, 360
    f = [text(W / 2, 28, "Де саме сидить заряд: дві поверхні → пориста поверхня → весь об'єм", size=15.5, bold=True)]
    cw = 250
    gx = 24
    x0 = (W - 3 * cw - 2 * gx) / 2
    cy = 56
    ch = 200
    px = x0 + cw / 2

    # --- картка 1: конденсатор (дві пластини) ---
    cx1 = x0
    f.append(rect(cx1, cy, cw, ch, fill="#fff", stroke=C_CAP, sw=2))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="30" rx="6" fill="%s" fill-opacity="0.15"/>' % (cx1, cy, cw, C_CAP))
    f.append(text(cx1 + cw / 2, cy + 20, "Конденсатор", size=13, color=C_CAP, bold=True))
    # дві пластини з зарядами
    pcx = cx1 + cw / 2
    f.append(rect(pcx - 70, cy + 60, 14, 90, fill="#eaf0fd", stroke=C_CAP, sw=2))
    f.append(rect(pcx + 56, cy + 60, 14, 90, fill="#fdecea", stroke=C_BAT, sw=2))
    for j in range(4):
        yy = cy + 72 + j * 22
        f.append(text(pcx - 63, yy + 4, "−", size=14, color=C_CAP, bold=True))
        f.append(text(pcx + 63, yy + 4, "+", size=14, color=C_BAT, bold=True))
    f.append(line(pcx - 56, cy + 105, pcx + 56, cy + 105, color=MUTED, sw=0.8, dash="3 3"))
    f.append(text(pcx, cy + ch - 14, "заряд лише на 2 поверхнях", size=9.5, color=MUTED, italic=True))

    # --- картка 2: суперконденсатор (пориста поверхня) ---
    cx2 = x0 + cw + gx
    f.append(rect(cx2, cy, cw, ch, fill="#fff", stroke=C_SC, sw=2))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="30" rx="6" fill="%s" fill-opacity="0.18"/>' % (cx2, cy, cw, C_SC))
    f.append(text(cx2 + cw / 2, cy + 20, "Суперконденсатор", size=13, color=C_SC, bold=True))
    # пориста губка — багато дрібних виступів, на кожному заряд
    scx = cx2 + cw / 2
    f.append(rect(scx - 80, cy + 70, 30, 80, fill="#faf4e4", stroke=C_SC, sw=1.6))
    # «пори» — зубчики
    for j in range(6):
        yy = cy + 76 + j * 12
        f.append(line(scx - 50, yy, scx - 30, yy, color=C_SC, sw=1.2))
        f.append(text(scx - 22, yy + 4, "−", size=9, color=C_CAP, bold=True))
    f.append(text(scx + 30, cy + 110, "та сама поверхня,", size=9.5, color=INK, anchor="middle"))
    f.append(text(scx + 30, cy + 124, "але в 1000× більша", size=9.5, color=INK, anchor="middle"))
    f.append(text(scx, cy + ch - 14, "пориста поверхня, тонкий шар", size=9.5, color=MUTED, italic=True))

    # --- картка 3: акумулятор (весь об'єм) ---
    cx3 = x0 + 2 * (cw + gx)
    f.append(rect(cx3, cy, cw, ch, fill="#fff", stroke=C_BAT, sw=2))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="30" rx="6" fill="%s" fill-opacity="0.15"/>' % (cx3, cy, cw, C_BAT))
    f.append(text(cx3 + cw / 2, cy + 20, "Акумулятор", size=13, color=C_BAT, bold=True))
    # суцільний блок матеріалу, весь у «+» — заряд у кожній молекулі
    bcx = cx3 + cw / 2
    f.append(rect(bcx - 64, cy + 60, 128, 90, fill="#fdecea", stroke=C_BAT, sw=2))
    for r in range(3):
        for c in range(5):
            f.append(text(bcx - 50 + c * 25, cy + 80 + r * 26, "•", size=15, color=C_BAT, bold=True))
    f.append(text(bcx, cy + ch - 14, "реакція у всьому об'ємі", size=9.5, color=MUTED, italic=True))

    f.append(fitbox(x0, cy + ch + 18, 3 * cw + 2 * gx, 26,
                    "Більше місця під заряд → більше енергії, але повільніший доступ. Це й є компроміс енергія ↔ потужність.",
                    size=10, fill="#eafaf0", stroke=FIELD, sw=1.3))
    render(os.path.join(IMG, "where.svg"), W, H, *f)


# ── 3. Карта вибору: три осі рішення ─────────────────────────────────────────
def fig_decision():
    """Під яку роль яке сховище. Три осі — енергія / потужність / ресурс — і
    типова роль кожного класу в реальному пристрої."""
    W, H = 780, 330
    f = [text(W / 2, 28, "Яке сховище під яку роль", size=16, bold=True)]
    cards = [
        (C_CAP, "Конденсатор", "мікросекунди-мілісекунди",
         "розв'язка живлення,\nзгладжування, фільтр", "енергії майже нема"),
        (C_SC,  "Суперконденсатор", "секунди-хвилини",
         "пікова потужність,\nрезерв на час перемикання,\nрекуперація", "саморозряд за тижні"),
        (C_BAT, "Акумулятор", "години-дні",
         "основний запас енергії,\nживлення в автономі", "обмежений ресурс, заряд повільний"),
    ]
    cw = 244
    gx = 18
    x0 = (W - 3 * cw - 2 * gx) / 2
    cy = 52
    ch = 230
    for i, (col, title, tscale, role, cost) in enumerate(cards):
        cx = x0 + i * (cw + gx)
        f.append(rect(cx, cy, cw, ch, fill="#fff", stroke=col, sw=2))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="48" rx="6" fill="%s" fill-opacity="0.15"/>'
                 % (cx, cy, cw, col))
        f.append(text(cx + cw / 2, cy + 22, title, size=13.5, color=col, bold=True))
        f.append(text(cx + cw / 2, cy + 40, "віддає за: " + tscale, size=9.5, color=MUTED, italic=True))
        f.append(mtext(cx + cw / 2, cy + 86, role, size=11, color=INK))
        f.append(line(cx + 16, cy + ch - 38, cx + cw - 16, cy + ch - 38, color=col, sw=0.8, dash="3 3"))
        f.append(fitbox(cx + 10, cy + ch - 32, cw - 20, 24, "платить: " + cost,
                        size=9.5, fill="none", stroke="none", color=MUTED))
    render(os.path.join(IMG, "decision.svg"), W, H, *f)


# ── допоміжне: верхній індекс для степеня 10 ─────────────────────────────────
_SUP = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵",
        "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
def _sup(k):
    return "".join(_SUP[ch] for ch in str(k))


# ── допоміжне: обрізати відрізок прямої по прямокутнику в координатах (logE,logP) ─
def _clip(xa, ya, xb, yb, xmin, xmax, ymin, ymax):
    """Повертає кінці відрізка [(x,y),(x,y)] усередині рамки або None.
    Лінія параметрична; перетинаємо з y=ymin, y=ymax, x=xmin, x=xmax."""
    pts = []
    dx, dy = xb - xa, yb - ya
    # перетини з горизонталями y=const
    for yc in (ymin, ymax):
        if dy != 0:
            t = (yc - ya) / dy
            x = xa + t * dx
            if 0 <= t <= 1 and xmin - 1e-9 <= x <= xmax + 1e-9:
                pts.append((x, yc))
    # перетини з вертикалями x=const
    for xc in (xmin, xmax):
        if dx != 0:
            t = (xc - xa) / dx
            y = ya + t * dy
            if 0 <= t <= 1 and ymin - 1e-9 <= y <= ymax + 1e-9:
                pts.append((xc, y))
    # унікалізувати й узяти дві крайні
    uniq = []
    for p in pts:
        if all(abs(p[0] - q[0]) > 1e-6 or abs(p[1] - q[1]) > 1e-6 for q in uniq):
            uniq.append(p)
    if len(uniq) >= 2:
        uniq.sort()
        return [uniq[0], uniq[-1]]
    return None


if __name__ == "__main__":
    fig_ragone()
    fig_where()
    fig_decision()
    print("OK: 3 figures ->", IMG)
