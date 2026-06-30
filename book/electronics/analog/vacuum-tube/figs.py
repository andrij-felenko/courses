# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Будова тріода: нитка → катод, сітка, анод; потік електронів ───────────
def fig_triode():
    W, H = 720, 380
    f = []
    # скляна колба
    f.append('<rect x="120" y="40" width="480" height="300" rx="120" '
             'fill="#f7fbff" stroke="%s" stroke-width="2"/>' % MUTED)
    f.append(text(360, 30, "вакуум усередині колби", size=12, color=MUTED))

    ax = 360  # вісь симетрії
    # анод (пластина) — зверху
    f.append(rect(ax - 150, 70, 300, 26, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(ax, 87, "анод (пластина)  +", size=13, color=POS, bold=True))
    # сітка — посередині, як ряд штрихів
    gy = 175
    for i in range(-6, 7):
        gx = ax + i * 22
        f.append(line(gx, gy - 12, gx, gy + 12, color=FIELD, sw=2.4))
    f.append(line(ax - 150, gy, ax + 150, gy, color=FIELD, sw=1.2, dash="4 4"))
    f.append(text(ax + 200, gy + 4, "сітка", size=13, color=FIELD, bold=True))
    # катод (підігрівна нитка) — знизу
    f.append(rect(ax - 60, 280, 120, 22, fill="#fff6e6", stroke="#d98a00", sw=2))
    f.append(text(ax, 295, "катод (гарячий)  −", size=12, color="#9a5b00", bold=True))
    # нитка-розжарення (зигзаг під катодом)
    zz = ["M%.0f 312" % (ax - 50)]
    for i in range(11):
        zz.append("L%.0f %d" % (ax - 50 + i * 10, 312 + (8 if i % 2 else 0)))
    f.append('<path d="%s" fill="none" stroke="#e25b00" stroke-width="2.2"/>' % " ".join(zz))
    f.append(text(ax, 348, "нитка гріє катод", size=11, color=MUTED))

    # потік електронів вгору, крізь сітку
    for i in (-2, -1, 0, 1, 2):
        x = ax + i * 40
        f.append(arrow(x, 272, x, 100, color=NEG, sw=2.0))
    f.append(text(ax - 215, 185, "потік\nелектронів".split("\n")[0], size=12, color=NEG))
    f.append(text(ax - 215, 200, "електронів", size=12, color=NEG))

    return render(os.path.join(IMG, "triode.svg"), W, H, *f,
                  title="Тріод: катод гріється, кидає електрони на анод, сітка керує потоком")


# ── 2. Сітка як кран: мала напруга на сітці керує великим струмом анода ──────
def fig_grid_control():
    W, H = 720, 320
    f = []
    cx, cy = W / 2, H / 2 + 6
    nodes = [
        (cx - 250, cy, "Мала зміна\nнапруги на сітці", FIELD),
        (cx,       cy, "Сітка тонко\nпропускає/гальмує\nпотік електронів", INK),
        (cx + 250, cy, "Велика зміна\nструму анода", POS),
    ]
    boxes = []
    for (x, y, s, col) in nodes:
        fill = "#eafaf1" if col is FIELD else ("#fdecea" if col is POS else FILL)
        b, w, h = textbox(x, y, s, size=13, pad=12, fill=fill, stroke=col, sw=2.0)
        boxes.append((x, w))
        f.append(b)
    for i in (0, 1):
        x1 = boxes[i][0] + boxes[i][1] / 2 + 6
        x2 = boxes[i + 1][0] - boxes[i + 1][1] / 2 - 6
        f.append(arrow(x1, cy, x2, cy, color=INK, sw=2.2))
    f.append(text(cx, cy - 86, "крихітна потужність керує великою — це і є підсилення",
                  size=13, bold=True, color=INK))
    f.append(text(cx, cy + 92, "сітка ближча до катода за анод, тож важить набагато сильніше",
                  size=12, color=MUTED))
    return render(os.path.join(IMG, "grid-control.svg"), W, H, *f)


# ── 3. Анодні характеристики + навантажувальна пряма (графічний розрахунок) ──
def fig_loadline():
    W, H = 720, 420
    f = []
    ox, oy = 90, 360          # початок осей
    pw, ph = 560, 300         # поле графіка
    # осі
    f.append(arrow(ox, oy, ox + pw + 12, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ph - 12, color=INK, sw=1.8))
    f.append(text(ox + pw + 6, oy + 22, "напруга анод-катод Va, В", size=12, color=INK, anchor="end"))
    f.append('<text x="%.0f" y="%.0f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.0f %.0f)">струм анода Ia, мА</text>'
             % (ox - 58, oy - ph / 2, FONT, INK, ox - 58, oy - ph / 2))
    Vmax, Imax = 300.0, 12.0
    sx = pw / Vmax
    sy = ph / Imax
    def PX(v): return ox + v * sx
    def PY(i): return oy - i * sy

    # сітка значень по осях
    for v in (0, 100, 200, 300):
        f.append(line(PX(v), oy, PX(v), oy + 5, color=INK))
        f.append(text(PX(v), oy + 20, str(v), size=11, color=MUTED))
    for i in (0, 4, 8, 12):
        f.append(line(ox - 5, PY(i), ox, PY(i), color=INK))
        f.append(text(ox - 12, PY(i) + 4, str(i), size=11, color=MUTED, anchor="end"))

    # сімейство анодних кривих для кількох Vg (умовна, але реалістична форма)
    def curve(vg):
        pts = []
        for k in range(0, 121):
            v = k * Vmax / 120.0
            # струм росте з (Va + mu*Vg), приблизно степенево, з насиченням угорі
            mu = 20.0
            drive = v + mu * vg
            ia = 0.0 if drive <= 0 else 0.00028 * drive ** 1.5
            ia = min(ia, Imax * 1.4)
            pts.append((PX(v), PY(ia)))
        d = "M%.1f %.1f " % pts[0] + " ".join("L%.1f %.1f" % p for p in pts[1:])
        return d
    for vg, lab in [(0, "Vg=0"), (-2, "−2 В"), (-4, "−4 В"), (-6, "−6 В")]:
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>'
                 % (curve(vg), NEG))
    # підписи кривих праворуч
    f.append(text(PX(300) + 4, PY(11.2), "Vg=0", size=11, color=NEG, anchor="start"))
    f.append(text(PX(300) + 4, PY(7.8), "−2 В", size=11, color=NEG, anchor="start"))
    f.append(text(PX(300) + 4, PY(4.6), "−4 В", size=11, color=NEG, anchor="start"))
    f.append(text(PX(300) + 4, PY(2.0), "−6 В", size=11, color=NEG, anchor="start"))

    # навантажувальна пряма: Va = Vbb − Ia·R, Vbb=300, R=25k → Ia(0)=12мА при Va=0
    f.append(line(PX(300), PY(0), PX(0), PY(12), color=POS, sw=2.4))
    f.append(text(PX(150) + 70, PY(7.6), "навантажувальна\nпряма (R анода)".split("\n")[0],
                  size=11, color=POS))
    f.append(text(PX(150) + 70, PY(6.8), "пряма (R анода)", size=11, color=POS))

    # робоча точка на перетині з Vg=−2
    f.append(circle(PX(150), PY(6.0), 5, fill=POS, stroke=POS))
    f.append(text(PX(150), PY(6.0) - 12, "робоча точка", size=11, color=POS, bold=True))

    return render(os.path.join(IMG, "loadline.svg"), W, H, *f,
                  title="Анодні криві й навантажувальна пряма: перетин дає робочу точку")


# ── 4. Космічний заряд: хмара електронів біля катода ────────────────────────
def fig_space_charge():
    W, H = 720, 300
    f = []
    # катод ліворуч, анод праворуч
    f.append(rect(70, 70, 24, 160, fill="#fff6e6", stroke="#d98a00", sw=2))
    f.append(text(82, 250, "катод −", size=12, color="#9a5b00", bold=True))
    f.append(rect(626, 70, 24, 160, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(638, 250, "анод +", size=12, color=POS, bold=True))

    # хмара космічного заряду — густо біля катода, рідше далі
    import random
    random.seed(7)
    for _ in range(140):
        # більше точок зліва
        t = random.random() ** 2.2
        x = 100 + t * 480
        y = 80 + random.random() * 140
        r = 2.6 - 1.4 * t
        f.append(circle(x, y, max(1.2, r), fill=NEG, stroke="none"))
    f.append(text(200, 56, "густа хмара електронів (космічний заряд)", size=12, color=NEG))
    f.append(text(200, 285, "вона відштовхує наступні електрони — тому струм не безмежний",
                  size=12, color=MUTED, anchor="start"))

    # стрілка дрейфу
    f.append(arrow(360, 165, 600, 165, color=INK, sw=1.6))
    f.append(text(480, 158, "дрейф до анода", size=11, color=INK))
    return render(os.path.join(IMG, "space-charge.svg"), W, H, *f,
                  title="Космічний заряд: хмара електронів біля катода обмежує струм")


# ── 5. Геометрія µ = gm·ra: крок сталого струму на сімействі кривих ──────────
def fig_mu_geometry():
    """Дві сусідні анодні криві (Vg та Vg+ΔVg). Щоб лишитися на ТОМУ ж струмі
    при відкритішій сітці, треба відступити анодом униз на ΔVa = µ·ΔVg.
    Прямокутник кроку: горизонталь ΔVa, що компенсує вертикаль gm·ΔVg."""
    W, H = 720, 430
    f = []
    ox, oy = 95, 360
    pw, ph = 555, 300
    f.append(arrow(ox, oy, ox + pw + 12, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ph - 12, color=INK, sw=1.8))
    f.append(text(ox + pw + 8, oy + 22, "напруга анода Va", size=12, color=INK, anchor="end"))
    f.append('<text x="%.0f" y="%.0f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.0f %.0f)">струм анода Ia</text>'
             % (ox - 60, oy - ph / 2, FONT, INK, ox - 60, oy - ph / 2))

    Vmax, Imax = 300.0, 12.0
    sx, sy = pw / Vmax, ph / Imax
    def PX(v): return ox + v * sx
    def PY(i): return oy - i * sy

    # струм як степенева функція «рушія» (Va + µ·Vg); тут параметризуємо зсувом по Va
    KC = 0.0022    # коефіцієнт, підібраний щоб криві заповнили поле [0..12 мА]
    def ia_of(v, shift):
        d = v - shift
        return 0.0 if d <= 0 else min(KC * d ** 1.5, Imax * 1.2)
    def curve(shift):
        pts = []
        for k in range(0, 121):
            v = k * Vmax / 120.0
            pts.append((PX(v), PY(ia_of(v, shift))))
        return "M%.1f %.1f " % pts[0] + " ".join("L%.1f %.1f" % p for p in pts[1:])
    # дві сусідні криві, рознесені по Va на µ·ΔVg: ліва — відкритіша сітка, права — більш від'ємна
    shiftL, shiftR = 30.0, 110.0    # відстань між кривими по Va = 80 В = µ·ΔVg
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (curve(shiftL), NEG))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (curve(shiftR), NEG))
    f.append(text(PX(300) + 4, PY(8.0), "Vg", size=12, color=NEG, anchor="start", bold=True))
    f.append(text(PX(300) + 4, PY(4.6), "Vg−ΔVg", size=11, color=NEG, anchor="start"))

    # робоча точка A на лівій кривій при Va=vA; B — та сама висота струму на правій кривій
    vA = 150.0
    Ia0 = ia_of(vA, shiftL)              # струм у A
    vB = vA + (shiftR - shiftL)          # рівний струм на правій кривій (однаковий «рушій»)
    djump = ia_of(vA, shiftL) - ia_of(vA, shiftR)   # стрибок струму при Va=vA, якби анод не рухався
    Iup = Ia0 + djump
    f.append(line(PX(vA), PY(Ia0), PX(vA), PY(Iup), color=FIELD, sw=2.2, dash="5 4"))   # вгору: +gm·ΔVg
    f.append(line(PX(vA), PY(Iup), PX(vB), PY(Ia0), color=POS, sw=2.2, dash="5 4"))     # назад униз анодом
    f.append(line(PX(vA), PY(Ia0), PX(vB), PY(Ia0), color=MUTED, sw=1.4, dash="3 4"))   # горизонталь ΔVa

    # точки
    f.append(circle(PX(vA), PY(Ia0), 5, fill=INK, stroke=INK))
    f.append(text(PX(vA) - 10, PY(Ia0) + 18, "A", size=13, color=INK, bold=True, anchor="end"))
    f.append(circle(PX(vB), PY(Ia0), 5, fill=POS, stroke=POS))
    f.append(text(PX(vB) + 10, PY(Ia0) + 18, "B", size=13, color=POS, bold=True, anchor="start"))

    # підписи плечей
    f.append(text(PX(vA) - 8, PY((Ia0 + Iup) / 2) + 4, "+gm·ΔVg", size=11, color=FIELD, anchor="end", bold=True))
    f.append(text((PX(vA) + PX(vB)) / 2, PY(Ia0) + 22, "ΔVa = µ·ΔVg", size=11, color=POS, bold=True))
    f.append(text((PX(vA) + PX(vB)) / 2, PY((Ia0 + Iup) / 2) - 4, "−(1/ra)·ΔVa", size=11, color=POS, anchor="start"))

    f.append(text(W / 2, oy + 50, "сітку відкрили на ΔVg, анод відвели на ΔVa — струм назад той самий: gm·ΔVg = (1/ra)·ΔVa",
                  size=12, color=MUTED))
    return render(os.path.join(IMG, "mu-geometry.svg"), W, H, *f,
                  title="Чому µ = gm·ra: крок зі сталим струмом між двома кривими")


# ── 6. Підсилення по навантажувальній прямій: вхідний хитун → вихідний розмах ─
def fig_gain_swing():
    W, H = 720, 430
    f = []
    ox, oy = 90, 355
    pw, ph = 560, 300
    f.append(arrow(ox, oy, ox + pw + 12, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ph - 12, color=INK, sw=1.8))
    f.append(text(ox + pw + 8, oy + 22, "Va, В", size=12, color=INK, anchor="end"))
    f.append('<text x="%.0f" y="%.0f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.0f %.0f)">Ia, мА</text>'
             % (ox - 58, oy - ph / 2, FONT, INK, ox - 58, oy - ph / 2))
    Vmax, Imax = 320.0, 12.0
    sx, sy = pw / Vmax, ph / Imax
    def PX(v): return ox + v * sx
    def PY(i): return oy - i * sy
    for v in (0, 100, 200, 300):
        f.append(line(PX(v), oy, PX(v), oy + 5, color=INK))
        f.append(text(PX(v), oy + 20, str(v), size=11, color=MUTED))

    # триодні криві крутіші за пентодні; модель ia = KC·(Va − зсув)^1.4, зсув ~ µ·|Vg|
    KC, EXP = 0.014, 1.4
    Vbb, Iaxis = 300.0, 11.0           # навантажувальна пряма від (Vbb,0) до (0, Iaxis)
    def ia_curve(v, off):
        d = v - off
        return 0.0 if d <= 0 else min(KC * d ** EXP, Imax * 1.4)
    def ia_line(v):
        return (Vbb - v) / Vbb * Iaxis
    def curve(off):
        pts = []
        for k in range(0, 129):
            v = k * Vmax / 128.0
            pts.append((PX(v), PY(ia_curve(v, off))))
        return "M%.1f %.1f " % pts[0] + " ".join("L%.1f %.1f" % p for p in pts[1:])
    offs = [115.0, 75.0, 155.0]        # центр (робоча Vg), сітка відкритіша (+ΔVg), прикритіша (−ΔVg)
    cols = [NEG, "#7fa0e8", "#7fa0e8"]
    for off, c in zip(offs, cols):
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                 % (curve(off), c, 2.0 if c is NEG else 1.5))

    # навантажувальна пряма
    f.append(line(PX(Vbb), PY(0), PX(0), PY(Iaxis), color=POS, sw=2.4))
    f.append(text(PX(8), PY(9.6), "Va = Vbb − Ia·R", size=11, color=POS, bold=True, anchor="start"))

    # перетини прямої з трьома кривими (скан по Va)
    def hit(off):
        best = None
        for k in range(1, 321):
            v = k * Vmax / 320.0
            d = ia_curve(v, off) - ia_line(v)
            if best is None or abs(d) < best[0]:
                best = (abs(d), v, (ia_curve(v, off) + ia_line(v)) / 2)
        return best[1], best[2]
    pts = [hit(o) for o in offs]
    # підписи кривих — праворуч від їхніх робочих точок
    f.append(text(PX(pts[0][0]) + 30, PY(pts[0][1]) + 26, "робоча Vg", size=11, color=NEG, anchor="start", bold=True))
    f.append(text(PX(pts[1][0]) - 4, PY(pts[1][1]) - 14, "+ΔVg", size=10, color="#3f6fd0", anchor="end"))
    f.append(text(PX(pts[2][0]) + 6, PY(pts[2][1]) + 16, "−ΔVg", size=10, color="#3f6fd0", anchor="start"))
    # вертикальні/горизонтальні проєкції для центральної (Q) й крайніх
    (vQ, iQ) = pts[0]
    f.append(circle(PX(vQ), PY(iQ), 5, fill=INK, stroke=INK))
    f.append(text(PX(vQ), PY(iQ) - 12, "Q", size=12, color=INK, bold=True))
    for (v, i), lab, col in [(pts[1], "+ΔVg", POS), (pts[2], "−ΔVg", POS)]:
        f.append(circle(PX(v), PY(i), 4, fill=col, stroke=col))

    # розмах на осі Va: від крайньої лівої до крайньої правої робочої точки
    vL = min(p[0] for p in pts)
    vR = max(p[0] for p in pts)
    yb = oy + 38
    f.append(line(PX(vL), PY(pts[1][1]), PX(vL), yb + 6, color=POS, sw=1.0, dash="3 3"))
    f.append(line(PX(vR), PY(pts[2][1]), PX(vR), yb + 6, color=POS, sw=1.0, dash="3 3"))
    f.append(arrow(PX(vL), yb, PX(vR), yb, color=POS, sw=1.8))
    f.append(arrow(PX(vR), yb, PX(vL), yb, color=POS, sw=1.8))
    f.append(text((PX(vL) + PX(vR)) / 2, yb - 6, "розмах виходу ΔVout = A·ΔVin", size=11, color=POS, bold=True))
    return render(os.path.join(IMG, "gain-swing.svg"), W, H, *f,
                  title="Сигнал гойдає сітку — робоча точка ковзає прямою — вихід гойдається сильніше")


# ── 7. Хто що зробив: ланцюг кроків від ефекту Едісона до робочої лампи ──────
def fig_birth_chain():
    """Горизонтальна стрічка для вставки hist-: винахід лампи — колективний,
    кожен крок зробила інша людина, в іншій країні, за тридцять із гаком років.
    Кольори карток = роль кроку."""
    W, H = 760, 470
    f = []
    f.append(text(W / 2, 30, "Лампа — не винахід однієї людини: ланцюг кроків",
                  size=16, bold=True, color=INK))

    # (рік, хто, що зробив, колір ролі)
    steps = [
        ("1880", "Едісон\n(США)", "помітив струм\nу вакуумі —\nале не зрозумів", MUTED),
        ("1904", "Флемінг\n(Англія)", "діод-випрямляч\nдля радіо —\n«народження\nелектроніки»", NEG),
        ("1906", "де Форест\n(США)", "додав сітку:\nтріод / Audion,\nале фізику\nзрозумів хибно", POS),
        ("1912", "AT&T,\nдослідники", "усвідомили\nпідсилення;\nтреба високий\nвакуум", FIELD),
        ("1913", "Армстронг,\nЛенгмюр,\nАрнольд", "правильна теорія;\nтвердий вакуум;\nнадійна лінійна\nлампа", INK),
    ]
    n = len(steps)
    margin = 24
    gap = 14
    bw = (W - 2 * margin - (n - 1) * gap) / n
    top = 70
    bh = 318
    for i, (yr, who, what, col) in enumerate(steps):
        x = margin + i * (bw + gap)
        cx = x + bw / 2
        fill = ("#f2f4f7" if col is MUTED else
                "#eaf0fd" if col is NEG else
                "#fdecea" if col is POS else
                "#eafaf1" if col is FIELD else "#fbfbfb")
        f.append(rect(x, top, bw, bh, fill=fill, stroke=col, sw=2.2, rx=10))
        f.append(text(cx, top + 36, yr, size=22, bold=True, color=col))
        who_lines = who.count("\n") + 1
        f.append(mtext(cx, top + 64, who, size=12, bold=True, color=INK, lh=1.2))
        wy = top + 64 + who_lines * 12 * 1.2 + 16
        f.append(mtext(cx, wy, what, size=11, color=INK, lh=1.3))
        if i < n - 1:
            ax0 = x + bw + 1
            ax1 = ax0 + gap - 2
            f.append(arrow(ax0, top + bh / 2, ax1, top + bh / 2, color=MUTED, sw=2.0))

    ly = top + bh + 36
    f.append(text(W / 2, ly,
                  "ідея · випрямляч · підсилювач-заявка · усвідомлення · теорія+реалізація",
                  size=12, color=MUTED, italic=True))
    f.append(text(W / 2, ly + 22,
                  "— різні люди, різні країни, понад тридцять років",
                  size=12, color=MUTED, italic=True))
    return render(os.path.join(IMG, "birth-chain.svg"), W, H, *f)


if __name__ == "__main__":
    fig_triode()
    fig_grid_control()
    fig_loadline()
    fig_space_charge()
    fig_mu_geometry()
    fig_gain_swing()
    fig_birth_chain()
    print("ok")
