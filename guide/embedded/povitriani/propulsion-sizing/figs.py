# -*- coding: utf-8 -*-
"""Фігури до теми «Підбір пропульсії: мотор + гвинт + батарея» (курс embedded/povitriani).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Дискове навантаження: малий швидкий струмінь проти великого повільного ──
def fig_disk_loading():
    """Ліворуч малий гвинт жене вузький швидкий струмінь; праворуч великий гвинт
    жене широкий повільний струмінь. Обидва дають ту саму тягу, але великий —
    меншою потужністю. Пояснює, чому великий повільний гвинт економніший."""
    W, H = 760, 400
    f = [text(W / 2, 30, "Та сама тяга: мало повітря швидко  чи  багато повітря повільно", size=16, bold=True)]

    def rig(cx, hub_r, blade, jet_w, arrows, cap, watt, wcol):
        out = []
        top = 90
        # маточина (мотор) і лопаті гвинта
        out.append(circle(cx, top, hub_r, fill="#eef2f7", stroke=LINE, sw=2))
        out.append(line(cx - blade, top, cx + blade, top, color=INK, sw=6))   # диск гвинта збоку
        out.append(text(cx, top - hub_r - 10, "гвинт", size=12, color=MUTED))
        # стовп повітря вниз (ширина jet_w), заливка
        jy0, jy1 = top + 18, 330
        out.append(rect(cx - jet_w / 2, jy0, jet_w, jy1 - jy0, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
        # стрілки струменя — довжина = швидкість повітря
        n = arrows
        for i in range(n):
            ax = cx - jet_w / 2 + jet_w * (i + 0.5) / n
            out.append(arrow(ax, jy0 + 8, ax, jy1 - 8, color=NEG, sw=2.4))
        return out, (cx, jy1)

    # ліворуч: малий гвинт, вузький швидкий струмінь (стрілки довгі)
    left, _ = rig(200, 20, 55, 70, 2, "малий гвинт", 100, POS)
    f += left
    f.append(text(200, 352, "малий гвинт — швидкий струмінь", size=13, bold=True, color=INK))
    b, w, h = textbox(200, 378, "більша потужність на ту саму тягу", size=12, color=POS, stroke=POS, fill="#fdecea")
    f.append(b)

    # праворуч: великий гвинт, широкий повільний струмінь (стрілки короткі — імітуємо кількома рядами)
    right, _ = rig(555, 26, 110, 150, 4, "великий гвинт", 60, FIELD)
    f += right
    f.append(text(555, 352, "великий гвинт — повільний струмінь", size=13, bold=True, color=INK))
    b, w, h = textbox(555, 378, "менша потужність на ту саму тягу", size=12, color=FIELD, stroke=FIELD, fill="#eafaf0")
    f.append(b)

    render(os.path.join(IMG, 'disk-loading.svg'), W, H, *f)


# ── 2. Правило узгодження KV з гвинтом ───────────────────────────────────────
def fig_kv_prop():
    """Ліворуч високий KV + малий гвинт (гоночний), праворуч низький KV + великий
    гвинт (знімальний). Посередині — правило-стрілка. Показує обов'язкове
    узгодження KV мотора з розміром гвинта."""
    W, H = 760, 380
    f = [text(W / 2, 30, "KV мотора мусить пасувати до розміру гвинта", size=16, bold=True)]

    def side(cx, kv, motor_r, blade, role, note, ncol):
        out = []
        my = 130
        out.append(circle(cx, my, motor_r, fill="#eef2f7", stroke=LINE, sw=2.5))       # мотор
        out.append(text(cx, my + 5, "мотор", size=12, color=MUTED))
        out.append(text(cx, my - motor_r - 12, kv, size=15, bold=True, color=ncol))
        # гвинт — горизонтальна лопать під мотором
        py = my + motor_r + 32
        out.append(line(cx - blade, py, cx + blade, py, color=INK, sw=7))
        out.append(circle(cx, py, 5, fill=INK, stroke=INK))
        out.append(text(cx, py + 26, "гвинт " + ("малий" if blade < 70 else "великий"), size=12, color=MUTED))
        # роль
        b, w, h = textbox(cx, py + 62, role, size=13, bold=True, color=ncol, stroke=ncol,
                          fill=("#fdecea" if ncol == POS else "#eafaf0"))
        out.append(b)
        out.append(text(cx, py + 100, note, size=12, color=MUTED))
        return out

    f += side(190, "високий KV", 26, 50,  "гоночний FPV",  "швидко, кволо", POS)
    f += side(570, "низький KV", 32, 118, "знімальний коптер", "повільно, сильно", FIELD)

    # правило посередині
    b, w, h = textbox(W / 2, 150, "ПРАВИЛО\nвисокий KV → малий гвинт\nнизький KV → великий гвинт",
                      size=13, bold=True, color=INK, stroke=LINE, min_w=190)
    f.append(b)
    # застереження внизу
    f.append(fitbox(W / 2 - 250, 338, 500, 34,
                    "великий гвинт на високому KV = надмірний струм, перегрів, дим із регулятора",
                    size=13, bold=True, color=POS, stroke=POS, fill="#fdecea"))

    render(os.path.join(IMG, 'kv-prop.svg'), W, H, *f)


# ── 3. Кільце пропульсії: маса → тяга → мотор/гвинт → струм → батарея → маса ──
def fig_budget_loop():
    """Замкнене кільце з п'яти вузлів: злітна маса задає тягу (×2), тяга — мотор+
    гвинт, ті — струм, струм — батарею (C-rate, ємність), маса батареї вертається
    у злітну масу. Показує, чому вузол підбирають ітераціями."""
    W, H = 720, 470
    f = [text(W / 2, 30, "Кільце пропульсії: рушиш одне — попливе все", size=16, bold=True)]

    cx, cy, R = W / 2, 250, 165
    nodes = [
        ("Злітна маса\nрама+електроніка+батарея", -90,  NEG),
        ("Потрібна тяга\n×2 над вагою",            -18,  POS),
        ("Мотор + гвинт\nKV під напругу",           54,  INK),
        ("Піковий струм\nбатарея: C-rate, ємність",126,  FIELD),
        ("Маса батареї\nдодається у злітну",       198,  NEG),
    ]
    pts = []
    for _, ang, _ in nodes:
        a = math.radians(ang)
        pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))

    # стрілки по колу (між сусідніми вузлами), трохи не доводячи до рамок
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        f.append(arrow(x1 + ux * 58, y1 + uy * 40, x2 - ux * 58, y2 - uy * 40, color=MUTED, sw=2.2))

    # вузли-рамки
    for (label, ang, col), (px, py) in zip(nodes, pts):
        b, w, h = textbox(px, py, label, size=12, bold=True, color=col, stroke=col,
                          fill=("#eaf0fd" if col == NEG else "#fdecea" if col == POS
                                else "#eafaf0" if col == FIELD else FILL))
        f.append(b)

    # підпис у центрі
    f.append(mtext(cx, cy - 6, ["підбір", "ітераціями"], size=13, color=MUTED, bold=True))

    render(os.path.join(IMG, 'budget-loop.svg'), W, H, *f)


# ── 4. Ефективність висіння падає як 1/√(дискове навантаження) ────────────────
def fig_fom_curve():
    """Крива грамів тяги на ват проти дискового навантаження (T/A).
    Ефективність висіння ∝ 1/√(T/A): дешевий великий гвинт сидить ліворуч
    (низьке навантаження, багато г/Вт), квадрокоптер і гелікоптер — правіше.
    Показує, ЧОМУ економність задає саме площа диска."""
    import math as _m
    W, H = 760, 430
    f = [text(W / 2, 30, "Ефективність висіння падає як 1 / √(дискове навантаження)", size=16, bold=True)]

    # осі
    ox, oy = 95, 350          # початок координат
    ax_w, ax_h = 590, 270     # довжина осей
    f.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=2))          # X
    f.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=2))          # Y
    f.append(text(ox + ax_w / 2, oy + 42, "дискове навантаження  T/A  (Н/м²)", size=13, color=INK))
    f.append(mtext(30, oy - ax_h / 2, ["г тяги", "на ват"], size=13, color=INK, anchor="middle"))

    # крива eff = k / sqrt(x) у діапазоні x∈[dl_min..dl_max]
    dl_min, dl_max = 8.0, 480.0
    k = 22.0 * _m.sqrt(dl_min)     # так, щоб ліва точка ≈ 22 г/Вт
    def X(dl):  # лог-масштаб по X, щоб охопити два порядки
        t = (_m.log(dl) - _m.log(dl_min)) / (_m.log(dl_max) - _m.log(dl_min))
        return ox + t * ax_w
    eff_max = 24.0
    def Y(eff):
        return oy - (eff / eff_max) * ax_h

    pts = []
    steps = 60
    for i in range(steps + 1):
        dl = dl_min * (dl_max / dl_min) ** (i / steps)
        eff = k / _m.sqrt(dl)
        pts.append((X(dl), Y(eff)))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, FIELD))

    # мітки-режими на кривій: кружок на кривій + рамка з підписом над/під ним
    def marker(dl, label, col, fillc, above=True):
        eff = k / _m.sqrt(dl)
        x, y = X(dl), Y(eff)
        out = [circle(x, y, 5, fill=col, stroke=col)]
        boxcy = y - 26 if above else y + 26
        b, w, h = textbox(x, boxcy, label, size=12, bold=True, color=col, stroke=col, fill=fillc)
        out.append(b)
        return out

    f += marker(14,  "великий гвинт\nнизьке T/A", FIELD, "#eafaf0", above=True)
    f += marker(110, "квадрокоптер", NEG, "#eaf0fd", above=True)
    f += marker(420, "гелікоптер,\nвисоке T/A", POS, "#fdecea", above=False)

    # пояснювальна рамка
    f.append(fitbox(ox + 250, oy - ax_h + 10, 300, 58,
                    "удвічі менший диск → удвічі більше T/A\n→ у √2 ≈ 1.41 раза гірша ефективність",
                    size=12, bold=True, color=INK, stroke=LINE, fill=FILL))

    render(os.path.join(IMG, 'fom-curve.svg'), W, H, *f)


# ── 5. Дві сталі — один констант мотора (обернена вагойка) ───────────────────
def fig_kv_kt_seesaw():
    """KV (оберти-на-вольт) і Kt (момент-на-ампер) — обернені сторони однієї
    сталої мотора. У центрі — рівність потужностей (баланс енергії), що їх зшиває:
    Ke = Kt, а Kt = 1/KV у SI. Показує, чому не можна мати водночас великий KV і
    великий Kt (вставка math-kv-kt)."""
    W, H = 760, 440
    f = [text(W / 2, 28, "KV і Kt — обернені сторони однієї сталої мотора", size=16, bold=True)]
    b, w, h = textbox(W / 2, 108,
                      "БАЛАНС ПОТУЖНОСТІ\nелектрична = механічна\nU·I = ω·M\n→  Ke = Kt  →  Kt = 1/KV",
                      size=13, bold=True, color=INK, stroke=LINE, fill=FILL, min_w=280)
    f.append(b)
    fx, fy = W / 2, 250
    f.append(line(fx, fy, fx, fy + 118, color=MUTED, sw=3))
    f.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f z" fill="#eef2f7" stroke="%s" stroke-width="1.5"/>'
             % (fx - 26, fy + 118, fx + 26, fy + 118, fx, fy + 78, LINE))
    ang = -10
    L = 250
    dx, dy = L * math.cos(math.radians(ang)), L * math.sin(math.radians(ang))
    lx1, ly1 = fx - dx, fy - dy
    lx2, ly2 = fx + dx, fy + dy
    f.append(line(lx1, ly1, lx2, ly2, color=INK, sw=6))
    f.append(circle(fx, fy, 7, fill=INK, stroke=INK))
    b, w, h = textbox(lx1, ly1 - 38, "KV\nоберти-на-вольт\nрад/с на вольт", size=12, bold=True,
                      color=NEG, stroke=NEG, fill="#eaf0fd", min_w=160)
    f.append(b)
    b, w, h = textbox(lx2, ly2 + 38, "Kt\nмомент-на-ампер\nН·м на ампер", size=12, bold=True,
                      color=POS, stroke=POS, fill="#fdecea", min_w=160)
    f.append(b)
    f.append(fitbox(W / 2 - 260, 404, 520, 30,
                    "піднявся один бік — опустився інший: більший KV ⇒ менший Kt, і навпаки",
                    size=13, bold=True, color=INK, stroke=LINE, fill="#f4f6f8"))
    render(os.path.join(IMG, 'kv-kt-seesaw.svg'), W, H, *f)


# ── 6. Фізична причина: витки обмотки задають обидві сталі разом ──────────────
def fig_winding_turns():
    """Ліворуч — багато тонких витків (низький KV, великий Kt); праворуч — мало
    товстих витків (високий KV, малий Kt). Та сама котушка задає KV і Kt одним
    вибором намотки — тому вони обернені, а не незалежні (вставка math-kv-kt)."""
    W, H = 760, 410
    f = [text(W / 2, 28, "Одна намотка задає обидві сталі — тому вони обернені", size=16, bold=True)]

    def coil(cx, turns, thick, kv, kt, ncol, fillc):
        out = []
        cy = 150
        core_w, core_h = 26, 150
        out.append(rect(cx - core_w / 2, cy - core_h / 2, core_w, core_h, fill="#e8ecf1", stroke=LINE, sw=2, rx=4))
        step = core_h / (turns + 1)
        for i in range(turns):
            yy = cy - core_h / 2 + step * (i + 1)
            rw = core_w / 2 + 16
            out.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="%.1f"/>'
                       % (cx, yy, rw, step * 0.42, ncol, thick))
        out.append(text(cx, cy + core_h / 2 + 24, "%d витків, %s дріт" %
                        (turns, "тонкий" if thick <= 2.2 else "товстий"), size=12, color=MUTED))
        b, w, h = textbox(cx, cy + core_h / 2 + 58, kv, size=13, bold=True, color=ncol, stroke=ncol, fill=fillc, min_w=160)
        out.append(b)
        b, w, h = textbox(cx, cy + core_h / 2 + 96, kt, size=13, bold=True, color=ncol, stroke=ncol, fill=fillc, min_w=160)
        out.append(b)
        return out

    f += coil(195, 9, 2.0, "низький KV", "великий Kt", NEG, "#eaf0fd")
    f += coil(565, 4, 4.2, "високий KV", "малий Kt", POS, "#fdecea")
    f.append(arrow(300, 150, 460, 150, color=MUTED, sw=2.4))
    f.append(mtext(380, 128, ["менше витків,", "товщий дріт"], size=12, color=MUTED, bold=True))
    render(os.path.join(IMG, 'winding-turns.svg'), W, H, *f)


# ── 7. (detailed) Тяга гвинта падає зі швидкістю; крок задає стелю ────────────
def fig_thrust_vs_speed():
    """Дві криві тяги проти швидкості польоту: малий крок дає більшу тягу на місці,
    але низьку стелю швидкості; великий крок — навпаки. Перетини з нулем —
    швидкості кроку. Пояснює, чому «швидкий» і «тягучий» гвинти різні (detailed)."""
    W, H = 760, 470
    f = [text(W / 2, 30, "Тяга гвинта падає зі швидкістю — крок задає, де вона впаде до нуля", size=15, bold=True)]
    # осі
    ox, oy = 100, 380          # початок координат
    ax_w, ax_h = 560, 300      # довжина осей
    f.append(arrow(ox, oy, ox + ax_w + 20, oy, color=INK, sw=2))      # X
    f.append(arrow(ox, oy, ox, oy - ax_h - 20, color=INK, sw=2))      # Y
    f.append(text(ox + ax_w + 20, oy - 12, "швидкість польоту →", size=13, color=INK, anchor="end"))
    f.append(text(ox - 12, oy - ax_h - 10, "тяга", size=13, color=INK, anchor="end"))

    # дві спадні криві: тяга(V) ~ T0*(1 - (V/Vp)^2). Малий крок: більший T0, менший Vp.
    def curve(T0_px, Vp_px, col, dash=None):
        pts = []
        N = 40
        for i in range(N + 1):
            v = Vp_px * i / N
            t = T0_px * (1.0 - (v / Vp_px) ** 2)
            if t < 0:
                t = 0
            pts.append((ox + v, oy - t))
        d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<path d="%s" fill="none" stroke="%s" stroke-width="3"%s/>' % (d, col, da)

    Vp_small = 300.0   # мала стеля швидкості (малий крок)
    Vp_big   = 520.0   # велика стеля (великий крок)
    T0_small = 270.0   # висока тяга на місці (малий крок)
    T0_big   = 200.0   # нижча тяга на місці (великий крок)
    f.append(curve(T0_small, Vp_small, NEG))
    f.append(curve(T0_big, Vp_big, POS))

    # точки перетину з нулем (швидкості кроку) — підписи ПІД віссю, осторонь
    f.append(circle(ox + Vp_small, oy, 4, fill=NEG, stroke=NEG))
    f.append(circle(ox + Vp_big, oy, 4, fill=POS, stroke=POS))
    f.append(text(ox + Vp_small, oy + 46, "швидк. кроку (малий)", size=11, color=NEG))
    f.append(text(ox + Vp_big - 10, oy + 26, "швидк. кроку (великий)", size=11, color=POS, anchor="end"))

    # підписи кривих — біля старту, осторонь одна від одної
    b, w, h = textbox(ox + 128, oy - T0_small + 8, ["малий крок 10×3.3", "тягучий, повільний"],
                      size=11, bold=True, color=NEG, stroke=NEG, fill="#eaf0fd")
    f.append(b)
    b, w, h = textbox(ox + 300, oy - T0_big - 30, ["великий крок 5×4.8", "швидкий, менш тягучий"],
                      size=11, bold=True, color=POS, stroke=POS, fill="#fdecea")
    f.append(b)
    render(os.path.join(IMG, 'thrust-vs-speed.svg'), W, H, *f)


# ── 8. (detailed) Струм росте як куб газу, не лінійно ─────────────────────────
def fig_current_vs_throttle():
    """Кубічна крива струму проти газу; пунктир — хибна лінійна інтуїція.
    Висіння на півгаза ~1/8 піку, повний газ ×8. Пояснює небезпеку піку (detailed)."""
    W, H = 720, 470
    f = [text(W / 2, 30, "Струм росте як куб газу — а не лінійно", size=16, bold=True)]
    ox, oy = 100, 390
    ax_w, ax_h = 520, 310
    f.append(arrow(ox, oy, ox + ax_w + 20, oy, color=INK, sw=2))
    f.append(arrow(ox, oy, ox, oy - ax_h - 20, color=INK, sw=2))
    f.append(text(ox + ax_w + 20, oy - 12, "газ →", size=13, color=INK, anchor="end"))
    f.append(text(ox - 14, oy - ax_h - 10, "струм", size=13, color=INK, anchor="end"))
    # позначки 50% і 100% газу
    xhalf = ox + ax_w * 0.5
    xfull = ox + ax_w
    f.append(line(xhalf, oy, xhalf, oy + 6, color=INK, sw=1.5))
    f.append(text(xhalf, oy + 24, "½ газу", size=12, color=INK))
    f.append(text(xfull, oy + 24, "повний", size=12, color=INK))

    # кубічна крива I = Imax*(g)^3
    Imax = ax_h
    pts = []
    N = 40
    for i in range(N + 1):
        g = i / N
        I = Imax * g ** 3
        pts.append((ox + ax_w * g, oy - I))
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (d, POS))
    # хибна лінійна інтуїція (пунктир)
    f.append(line(ox, oy, xfull, oy - Imax, color=MUTED, sw=2, dash="6 5"))
    f.append(text(ox + ax_w * 0.62, oy - Imax * 0.40, "хибна лінійна", size=11, color=MUTED, anchor="start"))
    f.append(text(ox + ax_w * 0.62, oy - Imax * 0.40 + 15, "інтуїція", size=11, color=MUTED, anchor="start"))

    # точка висіння (½ газу → 1/8 піку); напис — над лінійним пунктиром, осторонь
    yh = oy - Imax * 0.125
    f.append(line(ox, yh, xhalf, yh, color=NEG, sw=1.3, dash="4 4"))
    f.append(circle(xhalf, yh, 5, fill=NEG, stroke=NEG))
    b, w, h = textbox(ox + 108, yh - 92, ["висіння ½ газу", "≈ 1/8 піку"],
                      size=11, bold=True, color=NEG, stroke=NEG, fill="#eaf0fd")
    f.append(b)
    f.append(line(ox + 108, yh - 78, xhalf - 6, yh - 5, color=NEG, sw=1.0, dash="2 3"))  # тонкий вказівник до точки
    # точка піку
    f.append(circle(xfull, oy - Imax, 5, fill=POS, stroke=POS))
    b, w, h = textbox(xfull - 96, oy - Imax + 34, ["пік = повний газ", "×8 від висіння"],
                      size=11, bold=True, color=POS, stroke=POS, fill="#fdecea")
    f.append(b)
    render(os.path.join(IMG, 'current-vs-throttle.svg'), W, H, *f)


# ── 9. (detailed) Кільце як нерухома точка: збіжна проти розбіжної ─────────────
def fig_fixed_point():
    """Павутинна діаграма ітерації m = m0 + m_bat(m). Ліворуч нахил < 1 —
    сходинки збігаються до перетину з y=x; праворуч нахил > 1 — розбігаються.
    Пояснює, чому сайзинг сходиться за 2-3 кроки, і межу витривалості (detailed)."""
    W, H = 780, 500
    f = [text(W / 2, 28, "Кільце пропульсії — нерухома точка m = m₀ + m_бат(m)", size=16, bold=True)]

    def panel(px, title, slope, converge, note, notecol):
        out = []
        ox, oy = px, 380      # початок координат панелі
        sz = 240              # довжина осей
        col = NEG if converge else POS
        fillc = "#eaf0fd" if converge else "#fdecea"
        # заголовок панелі — під верхнім заголовком фігури, над осями
        out.append(text(ox + sz / 2, 66, title, size=13, bold=True, color=notecol))
        out.append(arrow(ox, oy, ox + sz + 16, oy, color=INK, sw=1.8))
        out.append(arrow(ox, oy, ox, oy - sz - 16, color=INK, sw=1.8))
        out.append(text(ox + sz + 16, oy + 22, "маса m →", size=11, color=INK, anchor="end"))
        # пряма y = x
        out.append(line(ox, oy, ox + sz, oy - sz, color=MUTED, sw=1.8, dash="5 4"))
        out.append(text(ox + sz - 4, oy - sz + 2, "y = x", size=11, color=MUTED, anchor="start"))
        # крива y = b + slope*x (px-координати), обрізана верхнім краєм рамки
        b0 = 0.28 * sz
        def Y(xpx):
            return b0 + slope * xpx
        # знайти x, де крива торкається стелі sz (щоб не вилазила)
        x_top = (sz - b0) / slope
        x2 = min(sz * 0.92, x_top)
        out.append(line(ox, oy - Y(0.0), ox + x2, oy - Y(x2), color=col, sw=3))
        # підпис кривої — коротким кольоровим відрізком-легендою під заголовком панелі,
        # осторонь самої кривої, сходинок і рамки-нотатки (щоб напис був поза лініями)
        ly = 88
        out.append(line(ox + 8, ly, ox + 30, ly, color=col, sw=3))
        out.append(text(ox + 36, ly + 4, "крива m₀ + m_бат(m)", size=11, color=col, anchor="start"))
        # павутинні сходинки ітерації
        if converge:
            xpx = 0.12 * sz
            for _ in range(6):
                y = Y(xpx)
                out.append(line(ox + xpx, oy - xpx, ox + xpx, oy - y, color=INK, sw=1.2))
                out.append(line(ox + xpx, oy - y, ox + y, oy - y, color=INK, sw=1.2))
                xpx = y
        else:
            xpx = 0.12 * sz
            for _ in range(4):
                y = min(Y(xpx), sz)
                out.append(line(ox + xpx, oy - xpx, ox + xpx, oy - y, color=INK, sw=1.2))
                out.append(line(ox + xpx, oy - y, ox + min(y, sz), oy - y, color=INK, sw=1.2))
                xpx = y
                if xpx >= sz:
                    break
        # нотатка — ПІД віссю X, де нема ні кривої, ні сходинок
        b, w, h = textbox(ox + sz / 2, oy + 58, note, size=11, bold=True,
                          color=notecol, stroke=notecol, fill=fillc)
        out.append(b)
        return out

    f += panel(70, "нахил < 1 — збіжно", 0.55, True,
               ["грам тягне < грама", "2–3 кроки — стоїть"], NEG)
    f += panel(450, "нахил > 1 — розбіжно", 1.25, False,
               ["батарея тягне батарею", "розв'язку немає"], POS)
    render(os.path.join(IMG, 'fixed-point.svg'), W, H, *f)


# ── 10. (detailed) Другий контур: просадка напруги з'їдає тягу ─────────────────
def fig_sag_loop():
    """Ланцюг стрілок контуру просадки (газ→струм→просадка→оберти→тяга→провал→газ)
    і два стовпчики тяги: здорова батарея (малий провал) проти слабкої (глибокий).
    Пояснює, чому 11% просадки коштують 20% тяги й чому C-rate беруть із запасом."""
    W, H = 840, 470
    f = [text(W / 2, 28, "Просадка напруги замикає другий контур — і з'їдає тягу на піку", size=15, bold=True)]

    # ── лівий бік: кільце стрілок ──
    cx, cy, R = 235, 255, 150
    steps = [
        ("повний газ", -90),
        ("↑ струм", -30),
        ("просадка I·R", 30),
        ("↓ напруга", 90),
        ("↓ оберти (×KV)", 150),
        ("↓ тяга (×²)", 210),
    ]
    import math as _m
    node_pos = []
    for label, ang in steps:
        a = _m.radians(ang)
        nx, ny = cx + R * _m.cos(a), cy + R * _m.sin(a)
        node_pos.append((nx, ny, label))
    # стрілки по колу
    for i in range(len(node_pos)):
        x0, y0, _ = node_pos[i]
        x1, y1, _ = node_pos[(i + 1) % len(node_pos)]
        # трохи вкоротити, щоб стрілка не лізла в текст
        dx, dy = x1 - x0, y1 - y0
        L = _m.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        f.append(arrow(x0 + ux * 30, y0 + uy * 22, x1 - ux * 30, y1 - uy * 22, color=MUTED, sw=2))
    # вузли-написи
    for nx, ny, label in node_pos:
        col = POS if ("↓ тяга" in label or "просадка" in label) else INK
        b, w, h = textbox(nx, ny, label, size=11, bold=True, color=col,
                          stroke=(POS if col == POS else LINE), fill=("#fdecea" if col == POS else FILL))
        f.append(b)
    f.append(text(cx, cy, "контур", size=12, color=MUTED, bold=True))
    f.append(text(cx, cy + 16, "просадки", size=12, color=MUTED, bold=True))

    # ── правий бік: два стовпчики тяги ──
    bx = 560
    base_y = 400
    bar_w = 70
    # розрахункова (100%)
    full_h = 250
    f.append(text(bx + 95, 90, "тяга на піку", size=13, bold=True))
    # здорова батарея: ~80% (просадка 11% → тяга ×0.80)
    hh = full_h * 0.80
    f.append(rect(bx, base_y - full_h, bar_w, full_h, fill="#eef2f7", stroke=MUTED, sw=1.5))
    f.append(rect(bx, base_y - hh, bar_w, hh, fill="#dcefe0", stroke=FIELD, sw=2))
    f.append(text(bx + bar_w / 2, base_y + 20, "здорова", size=11, color=FIELD, bold=True))
    f.append(text(bx + bar_w / 2, base_y + 36, "R малий", size=10, color=MUTED))
    f.append(text(bx + bar_w / 2, base_y - hh - 8, "≈80%", size=11, color=FIELD, bold=True))
    # слабка батарея: ~53%
    bx2 = bx + 150
    hh2 = full_h * 0.53
    f.append(rect(bx2, base_y - full_h, bar_w, full_h, fill="#eef2f7", stroke=MUTED, sw=1.5))
    f.append(rect(bx2, base_y - hh2, bar_w, hh2, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(bx2 + bar_w / 2, base_y + 20, "слабка", size=11, color=POS, bold=True))
    f.append(text(bx2 + bar_w / 2, base_y + 36, "R великий", size=10, color=MUTED))
    f.append(text(bx2 + bar_w / 2, base_y - hh2 - 8, "≈53%", size=11, color=POS, bold=True))
    f.append(text(bx2 + bar_w / 2, base_y - hh2 + 22, "провал", size=10, color=POS, bold=True))
    # лінія «розрахункова 100%»
    f.append(line(bx - 10, base_y - full_h, bx2 + bar_w + 10, base_y - full_h, color=INK, sw=1.2, dash="4 4"))
    f.append(text(bx2 + bar_w + 8, base_y - full_h - 8, "100% (папір)", size=10, color=INK, anchor="end"))
    render(os.path.join(IMG, 'sag-loop.svg'), W, H, *f)


# ── 11. (math-thermal-limit) Обмотка як теплове RC: пік проходить, тривале — палить ──
def fig_thermal_rc_motor():
    """Температура обмотки росте по експоненті до усталеної ΔT_∞ = P·Rθ.
    Тривалий струм (велике P) веде криву ПОНАД клас ізоляції; пік такого ж струму
    на кілька секунд не встигає й лишається низько. Ядро вставки — чому два рейтинги."""
    W, H = 780, 470
    f = [text(W / 2, 28, "Обмотка гріється по експоненті — пік не встигає, тривале переростає клас", size=15, bold=True)]

    ox, oy = 92, 380           # початок координат
    ax_w, ax_h = 600, 300      # довжина осей
    f.append(arrow(ox, oy, ox + ax_w + 18, oy, color=INK, sw=2))       # X — час
    f.append(arrow(ox, oy, ox, oy - ax_h - 16, color=INK, sw=2))       # Y — температура
    f.append(text(ox + ax_w + 14, oy + 22, "час →", size=13, color=INK, anchor="end"))
    f.append(mtext(30, oy - ax_h / 2 - 6, ["темпе-", "ратура"], size=12, color=INK, anchor="middle"))

    # рівень довкілля (низ) і клас ізоляції F (стеля)
    y_amb = oy
    y_class = oy - ax_h * 0.72
    f.append(line(ox, y_class, ox + ax_w, y_class, color=POS, sw=1.6, dash="7 5"))
    f.append(text(ox + ax_w - 4, y_class - 8, "клас F — 155 °C (межа ізоляції)", size=12, color=POS, anchor="end", bold=True))

    # усталена ΔT_∞ тривалого струму — ВИЩЕ за клас (тому крива його переростає)
    y_inf = oy - ax_h * 0.96
    f.append(line(ox, y_inf, ox + ax_w * 0.62, y_inf, color=MUTED, sw=1.3, dash="3 4"))
    f.append(text(ox + 6, y_inf - 8, "ΔT∞ = P·Rθ (тривалий струм) — понад клас", size=11, color=MUTED, anchor="start"))

    import math as _m
    # тривала крива: T = amb + (inf-amb)*(1 - e^{-t/τ}); τ у px, стеля y_inf
    def rise(y_stop, tau_px, col, x_end, sw=3.2, dash=None):
        pts = []
        N = 60
        span = (oy - y_stop)
        for i in range(N + 1):
            xp = x_end * i / N
            yv = span * (1.0 - _m.exp(-xp / tau_px))
            pts.append((ox + xp, oy - yv))
        d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, col, sw, da)

    tau = 150.0
    # тривалий струм — прямує до y_inf (понад клас), перетинає лінію класу
    f.append(rise(y_inf, tau, POS, ax_w * 0.98))
    # точка, де тривала крива перетинає клас F
    span_inf = oy - y_inf
    # розв'язок 1-e^{-t/τ} = (перепад до класу)/(перепад до inf)
    frac = (oy - y_class) / span_inf
    t_cross = -tau * _m.log(1.0 - frac)
    f.append(circle(ox + t_cross, y_class, 5, fill=POS, stroke=POS))
    # короткий вказівник униз від точки перетину (не через увесь графік) + підпис поряд
    f.append(line(ox + t_cross, y_class, ox + t_cross, y_class + 34, color=POS, sw=1.0, dash="2 3"))
    f.append(text(ox + t_cross + 8, y_class + 30, "тут згорить", size=11, color=POS, anchor="start", bold=True))

    # ПІКОВИЙ струм такий самий, але вимкнений через t_burst ≪ τ — крива обривається низько
    t_burst = ax_w * 0.14
    yb = span_inf * (1.0 - _m.exp(-t_burst / tau))
    # частина кривої до обриву (синя, той самий нахил на старті)
    ptsB = []
    N = 24
    for i in range(N + 1):
        xp = t_burst * i / N
        yv = span_inf * (1.0 - _m.exp(-xp / tau))
        ptsB.append((ox + xp, oy - yv))
    dB = "M " + " L ".join("%.1f %.1f" % p for p in ptsB)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.4"/>' % (dB, NEG))
    # після обриву — спад назад (охолодження), пунктиром вниз
    f.append(circle(ox + t_burst, oy - yb, 5, fill=NEG, stroke=NEG))
    coolN = 20
    ptsC = []
    for i in range(coolN + 1):
        xp = (ax_w * 0.20) * i / coolN
        yv = yb * _m.exp(-xp / (tau * 1.4))
        ptsC.append((ox + t_burst + xp, oy - yv))
    dC = "M " + " L ".join("%.1f %.1f" % p for p in ptsC)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="5 4"/>' % (dC, NEG))

    # підписи кривих — осторонь, у вільних зонах: червоний біля свого високого плато (правий верх),
    # синій — під своїм горбом, ліворуч від дропа
    b, w, h = textbox(ox + ax_w * 0.72, oy - ax_h * 0.62,
                      ["той самий струм — але ТРИВАЛО", "T → ΔT∞, переростає клас"],
                      size=11, bold=True, color=POS, stroke=POS, fill="#fdecea")
    f.append(b)
    b, w, h = textbox(ox + t_burst - 6, oy - yb + 66,
                      ["той самий струм ПІКОМ", "(секунди) — вимкнув,", "T ще низько"],
                      size=11, bold=True, color=NEG, stroke=NEG, fill="#eaf0fd")
    f.append(b)
    # тонкий вказівник від синього підпису вгору до горба піку
    f.append(line(ox + t_burst - 6, oy - yb + 44, ox + t_burst, oy - yb + 8, color=NEG, sw=1.0, dash="2 3"))
    # позначка τ на осі
    f.append(line(ox + tau, oy, ox + tau, oy + 6, color=INK, sw=1.4))
    f.append(text(ox + tau, oy + 20, "τ", size=13, color=INK, anchor="middle", italic=True))

    render(os.path.join(IMG, 'thermal-rc-motor.svg'), W, H, *f)


# ── 12. (math-thermal-limit) Нагрів швидкий, охолодження на висінні повільне ──
def fig_heat_cool_asymmetry():
    """Одна й та сама обмотка: нагрів під струмом (крутий, мала τ) і охолодження
    на висінні без обдуву (пологий, τ у рази більша, бо Rθ великий без потоку).
    Пояснює, чому на висінні мотор не встигає остигати між навантаженнями."""
    import math as _m
    W, H = 780, 450
    f = [text(W / 2, 28, "Нагрів швидкий — а охолодження на висінні в рази повільніше", size=15, bold=True)]

    ox, oy = 92, 360
    ax_w, ax_h = 600, 280
    f.append(arrow(ox, oy, ox + ax_w + 18, oy, color=INK, sw=2))
    f.append(arrow(ox, oy, ox, oy - ax_h - 16, color=INK, sw=2))
    f.append(text(ox + ax_w + 14, oy + 22, "час →", size=13, color=INK, anchor="end"))
    f.append(mtext(30, oy - ax_h / 2 - 6, ["темпе-", "ратура"], size=12, color=INK, anchor="middle"))

    peak = ax_h * 0.82
    x_on = ax_w * 0.40          # доки струм увімкнено — нагрів
    tau_h = 70.0                # мала стала нагріву (обдув від розгону чи стенд)
    tau_c = 240.0              # велика стала охолодження на висінні (без обдуву)

    # фаза нагріву 0..x_on
    ptsH = []
    N = 40
    for i in range(N + 1):
        xp = x_on * i / N
        yv = peak * (1.0 - _m.exp(-xp / tau_h))
        ptsH.append((ox + xp, oy - yv))
    y_at_on = peak * (1.0 - _m.exp(-x_on / tau_h))
    dH = "M " + " L ".join("%.1f %.1f" % p for p in ptsH)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.4"/>' % (dH, POS))

    # фаза охолодження x_on..кінець — пологий спад із великою τ_c
    ptsC = []
    for i in range(N + 1):
        xp = (ax_w - x_on) * i / N
        yv = y_at_on * _m.exp(-xp / tau_c)
        ptsC.append((ox + x_on + xp, oy - yv))
    dC = "M " + " L ".join("%.1f %.1f" % p for p in ptsC)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.4"/>' % (dC, NEG))

    # вертикаль-межа фаз
    f.append(line(ox + x_on, oy, ox + x_on, oy - peak - 6, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(ox + x_on, oy + 20, "струм знято", size=11, color=MUTED, anchor="middle"))

    # підписи фаз — осторонь від кривих
    b, w, h = textbox(ox + x_on * 0.52, oy - ax_h * 0.86,
                      ["НАГРІВ", "мала τ = Rθ·Cθ", "(є обдув — Rθ малий)"],
                      size=11, bold=True, color=POS, stroke=POS, fill="#fdecea")
    f.append(b)
    b, w, h = textbox(ox + x_on + (ax_w - x_on) * 0.55, oy - ax_h * 0.50,
                      ["ОХОЛОДЖЕННЯ на висінні", "велика τ (нема обдуву —", "Rθ у рази більший)"],
                      size=11, bold=True, color=NEG, stroke=NEG, fill="#eaf0fd")
    f.append(b)

    # нижня рамка-висновок — під віссю
    f.append(fitbox(ox + 40, oy + 40, ax_w - 80, 34,
                    "висіння прибирає обдув → Rθ росте → τ_охол ≫ τ_нагр: тепло накопичується швидше, ніж стікає",
                    size=12, bold=True, color=INK, stroke=LINE, fill=FILL))
    render(os.path.join(IMG, 'heat-cool-asymmetry.svg'), W, H, *f)


# ── 13. (math-endurance-limit) Час висіння проти маси батареї: горб зі стелею ──
def fig_endurance_hump():
    """Крива t(m_bat) = e·m_bat / (c·(m0+m_bat)^1.5): спершу росте, сягає МАКСИМУМУ
    при частці батареї 2/3 (m_bat = 2·m0), далі ПАДАЄ — більше батареї = коротший
    політ. Вершина горба і є стеля витривалості; праворуч від неї батарея возить себе."""
    import math as _m
    W, H = 780, 470
    f = [text(W / 2, 28, "Час висіння проти маси батареї — є вершина, за нею політ коротшає", size=15, bold=True)]

    ox, oy = 92, 380           # початок координат
    ax_w, ax_h = 610, 300      # довжина осей
    f.append(arrow(ox, oy, ox + ax_w + 18, oy, color=INK, sw=2))       # X — маса батареї / частка
    f.append(arrow(ox, oy, ox, oy - ax_h - 16, color=INK, sw=2))       # Y — час висіння
    f.append(text(ox + ax_w + 14, oy + 22, "частка батареї m_бат / m →", size=12, color=INK, anchor="end"))
    f.append(mtext(34, oy - ax_h / 2, ["час", "висіння"], size=12, color=INK, anchor="middle"))

    # крива t(frac): параметризуємо часткою p = m_bat/(m0+m_bat) ∈ (0..0.97)
    # при фіксованому m0: m_bat = p*m0/(1-p); t ∝ e*m_bat/(m0+m_bat)^1.5.
    # У пікселях беремо безрозмірну форму з максимумом при p=2/3.
    m0 = 1.0
    def t_of_p(p):
        mb = p * m0 / (1.0 - p)
        m = m0 + mb
        return mb / m ** 1.5     # ∝ час (константи e,c поглинуто масштабом)
    p_lo, p_hi = 0.03, 0.965
    t_peak = t_of_p(2.0 / 3.0)
    def X(p):
        return ox + ((p - p_lo) / (p_hi - p_lo)) * ax_w
    def Y(t):
        return oy - (t / t_peak) * (ax_h - 30)
    pts = []
    N = 200
    for i in range(N + 1):
        p = p_lo + (p_hi - p_lo) * i / N
        pts.append((X(p), Y(t_of_p(p))))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % q for q in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (d, FIELD))

    # вершина горба — стеля витривалості при частці 2/3
    px, py = X(2.0 / 3.0), Y(t_peak)
    f.append(line(px, py, px, oy, color=MUTED, sw=1.4, dash="4 4"))
    f.append(circle(px, py, 6, fill=INK, stroke=INK))
    f.append(text(px, oy + 22, "⅔", size=13, bold=True, color=INK))
    b, w, h = textbox(px, py - 40, ["СТЕЛЯ витривалості", "частка батареї = ⅔"],
                      size=12, bold=True, color=INK, stroke=LINE, fill=FILL, min_w=210)
    f.append(b)

    # ліва зона — грам батареї ще додає хвилини (висхідна вітка)
    b, w, h = textbox(X(0.30), Y(t_of_p(0.30)) - 66, ["тут грам батареї", "ще додає хвилини"],
                      size=11, bold=True, color=NEG, stroke=NEG, fill="#eaf0fd")
    f.append(b)
    f.append(line(X(0.30), Y(t_of_p(0.30)) - 50, X(0.30), Y(t_of_p(0.30)) - 8, color=NEG, sw=1.0, dash="2 3"))

    # права зона — батарея возить себе, політ коротшає
    b, w, h = textbox(X(0.88), Y(t_of_p(0.88)) + 60, ["батарея возить себе", "політ КОРОТШАЄ"],
                      size=11, bold=True, color=POS, stroke=POS, fill="#fdecea")
    f.append(b)
    f.append(line(X(0.88), Y(t_of_p(0.88)) + 8, X(0.88), Y(t_of_p(0.88)) + 44, color=POS, sw=1.0, dash="2 3"))

    # практична робоча зона — лівіше вершини, де крива ще крута
    f.append(text(X(0.24), oy - 12, "реальні апарати сидять тут ← ⅓…½", size=11, color=FIELD, bold=True, anchor="middle"))

    render(os.path.join(IMG, 'endurance-hump.svg'), W, H, *f)


# ── 14. (math-endurance-limit) Енергогустина піднімає стелю лінійно ───────────
def fig_energy_density_ladder():
    """Стеля витривалості t_crit ∝ енергогустина: стовпчики для LiPo, Li-ion і
    паливної комірки на ОДНІЙ рамі. Вершина горба стоїть на тій самій частці ⅔,
    та сама фізика — лише вища енергогустина розтягує час угору лінійно."""
    W, H = 780, 440
    f = [text(W / 2, 28, "Вища енергогустина піднімає стелю витривалості — лінійно", size=15, bold=True)]

    base_y = 350
    max_h = 250
    # (назва, Вт·год/кг, стеля хв для m0≈0.6 кг, колір, заливка)
    bars = [
        ("LiPo\n~180 Вт·год/кг", 180, 64, NEG, "#eaf0fd"),
        ("Li-ion 18650\n~240 Вт·год/кг", 240, 85, FIELD, "#eafaf0"),
        ("паливна комірка\n~490 Вт·год/кг", 490, 174, POS, "#fdecea"),
    ]
    e_max = 490.0
    bx0 = 150
    step = 200
    bw = 96
    for i, (name, e, tmin, col, fillc) in enumerate(bars):
        bx = bx0 + i * step
        h = max_h * (e / e_max)
        f.append(rect(bx, base_y - h, bw, h, fill=fillc, stroke=col, sw=2.5))
        f.append(text(bx + bw / 2, base_y - h - 26, "%d Вт·год/кг" % e, size=12, bold=True, color=col))
        f.append(text(bx + bw / 2, base_y - h - 10, "стеля ≈ %d хв" % tmin, size=12, bold=True, color=col))
        # підпис під віссю
        first, second = name.split("\n")
        f.append(text(bx + bw / 2, base_y + 22, first, size=12, bold=True, color=INK))
        f.append(text(bx + bw / 2, base_y + 40, second, size=11, color=MUTED))

    f.append(line(bx0 - 20, base_y, bx0 + 2 * step + bw + 20, base_y, color=INK, sw=2))

    # підпис-висновок унизу
    f.append(fitbox(W / 2 - 300, base_y + 58, 600, 34,
                    "та сама рама, та сама вершина при частці ⅔ — лише енергогустина розтягує стелю вгору",
                    size=12, bold=True, color=INK, stroke=LINE, fill=FILL))
    render(os.path.join(IMG, 'energy-density-ladder.svg'), W, H, *f)


if __name__ == "__main__":
    fig_disk_loading()
    fig_kv_prop()
    fig_budget_loop()
    fig_fom_curve()
    fig_kv_kt_seesaw()
    fig_winding_turns()
    fig_thrust_vs_speed()
    fig_current_vs_throttle()
    fig_fixed_point()
    fig_sag_loop()
    fig_thermal_rc_motor()
    fig_heat_cool_asymmetry()
    fig_endurance_hump()
    fig_energy_density_ladder()
    print("OK: +endurance-hump, energy-density-ladder ->", IMG)
