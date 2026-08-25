# -*- coding: utf-8 -*-
"""Фігури до теми «Принцип відносності Ґалілея».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

MOVE = "#2457d6"   # швидкість, рух — холодне
CURR = "#27ae60"   # течія / швидкість системи — зелене
BREAK = "#c0392b"  # де принцип ламається — гаряче


# ── Фігура 1: каюта Ґалілея — рівний хід не відрізнити від стоянки ────────────
def fig_galileo_ship():
    W, H = 920, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32,
                  "Каюта Ґалілея: жоден дослід усередині не відрізнить причал від рівного ходу",
                  size=15.5, bold=True))
    f.append(line(460, 62, 460, 392, color="#dfe4ea", sw=1.3, dash="4,6"))

    def scene(cx, title, moving):
        out = text(cx, 84, title, size=13.5, bold=True)
        # вода
        wy = 356
        if moving:
            # хвилясті лінії
            d = "M %.1f %.1f " % (cx - 150, wy)
            for i in range(0, 12):
                x0 = cx - 150 + i * 25
                d += "q 12 -7 25 0 "
            out += '<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, MOVE)
            out += arrow(cx + 30, wy + 26, cx + 120, wy + 26, color=MOVE, sw=3)
            out += text(cx + 75, wy + 20, "V", size=15, bold=True, italic=True, color=MOVE)
        else:
            out += line(cx - 150, wy, cx + 150, wy, color="#9fb6d6", sw=2)
            # причальний кнехт
            out += rect(cx + 120, wy - 26, 12, 26, fill="#cbd3dd", stroke=LINE, sw=1.4, rx=2)
            out += text(cx + 126, wy + 20, "причал", size=11, color=MUTED)
        # корпус (трапеція)
        out += ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                'fill="#e7edf5" stroke="%s" stroke-width="2"/>'
                % (cx - 128, 322, cx + 128, 322, cx + 96, wy, cx - 96, wy, LINE))
        # каюта (закрита скринька)
        cabX, cabY, cabW, cabH = cx - 88, 196, 176, 126
        out += rect(cabX, cabY, cabW, cabH, fill="#f6f8fb", stroke=LINE, sw=2, rx=8)
        out += text(cx, cabY - 8, "закрита каюта", size=11.5, color=MUTED)
        # ── дослід 1: крапля з пляшки падає прямовисно у чашку ──
        bx = cx - 46
        out += rect(bx - 7, cabY + 14, 14, 26, fill="#dbe6f5", stroke=LINE, sw=1.4, rx=3)  # пляшка
        # прямовисний пунктир-орієнтир
        out += line(bx, cabY + 42, bx, cabY + 104, color="#c7d0da", sw=1.2, dash="3,5")
        for dy in (54, 72, 90):
            out += circle(bx, cabY + dy, 3.4, fill=MOVE, stroke=MOVE, sw=1)
        # чашка
        out += ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                'fill="#eef2f7" stroke="%s" stroke-width="1.6"/>'
                % (bx - 10, cabY + 104, bx + 10, cabY + 104, bx + 7, cabY + 118, bx - 7, cabY + 118, LINE))
        # ── дослід 2: рибка у мисці ──
        fx, fy = cx + 46, cabY + 74
        out += circle(fx, fy, 26, fill="#eaf3ff", stroke="#8fb4dd", sw=1.8)
        out += ('<ellipse cx="%.1f" cy="%.1f" rx="12" ry="7" fill="%s"/>'
                % (fx - 2, fy, MOVE))
        out += ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>'
                % (fx + 8, fy, fx + 18, fy - 6, fx + 18, fy + 6, MOVE))
        out += circle(fx - 8, fy - 2, 1.8, fill=BG, stroke=BG, sw=0)
        return out

    f.append(scene(230, "Корабель стоїть біля причалу", False))
    f.append(scene(690, "Корабель пливе рівно (V стала)", True))

    b, _, _ = textbox(
        W / 2, 432,
        "Крапля падає прямовисно в чашку, риба плаває на всі боки однаково — у стоячому й у рухомому однаково.\n"
        "Поки хід рівний, усередині немає жодної прикмети руху: рівномірний рух не можна відчути зсередини.",
        size=12, pad=12, fill="#eef3fb", stroke=FIELD, sw=1.5)
    f.append(b)
    return render(os.path.join(IMG, "galileo-ship.svg"), W, H, *f)


# ── Фігура 2: швидкості систем додаються векторно (човен і течія) ─────────────
def fig_velocity_composition():
    W, H = 900, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32,
                  "Швидкості систем додаються векторно: та сама швидкість — різна в різних системах",
                  size=15, bold=True))

    # ── річка ──
    rx0, rx1 = 70, 470
    ry0, ry1 = 150, 356
    f.append(rect(rx0, ry0, rx1 - rx0, ry1 - ry0, fill="#eaf3ff", stroke='none', sw=0, rx=0))
    f.append(line(rx0, ry0, rx1, ry0, color="#8fb4dd", sw=2))
    f.append(line(rx0, ry1, rx1, ry1, color="#8fb4dd", sw=2))
    f.append(text(rx0 + 6, ry0 - 10, "берег", size=11, color=MUTED, anchor="start"))
    f.append(text(rx0 + 6, ry1 + 20, "берег", size=11, color=MUTED, anchor="start"))
    # течія
    for yy in (188, 240, 292, 330):
        f.append(arrow(rx0 + 30, yy, rx0 + 96, yy, color="#bcd3ee", sw=2))
    f.append(text(rx1 - 8, ry0 + 22, "течія →", size=11.5, color=CURR, anchor="end"))

    # ── векторний трикутник у стартовій точці ──
    S = 30.0                       # 1 м/с = 30 px
    ox, oy = 210, 320              # старт човна (на нижньому березі)
    up = (ox, oy - 3 * S)          # човен відносно води: 3 м/с упоперек
    rt = (ox + 4 * S, oy)          # течія: 4 м/с уздовж
    res = (ox + 4 * S, oy - 3 * S)  # відносно берега: 5 м/с по діагоналі

    # човник у старті
    f.append(('<ellipse cx="%.1f" cy="%.1f" rx="15" ry="7" fill="#fdf1d8" '
              'stroke="%s" stroke-width="1.8"/>') % (ox, oy, LINE))
    # u' — упоперек (синє)
    f.append(arrow(ox, oy, up[0], up[1], color=MOVE, sw=3.2))
    f.append(text(ox - 12, (oy + up[1]) / 2, "u′ = 3 м/с", size=12.5, bold=True, color=MOVE, anchor="end"))
    f.append(text(ox - 12, (oy + up[1]) / 2 + 18, "(відносно води)", size=10.5, color=MOVE, anchor="end"))
    # V — течія (зелене)
    f.append(arrow(ox, oy, rt[0], rt[1], color=CURR, sw=3.2))
    f.append(text((ox + rt[0]) / 2, oy + 22, "V = 4 м/с (течія)", size=12.5, bold=True, color=CURR))
    # u — відносно берега (діагональ, чорне); підпис винесено за вершину, поза векторами
    f.append(line(up[0], up[1], res[0], res[1], color="#c7d0da", sw=1.4, dash="4,5"))
    f.append(line(rt[0], rt[1], res[0], res[1], color="#c7d0da", sw=1.4, dash="4,5"))
    f.append(arrow(ox, oy, res[0], res[1], color=INK, sw=3.4))
    f.append(circle(res[0], res[1], 4.5, fill="#fef6e7", stroke=INK, sw=2))
    f.append(text(res[0] + 14, res[1] - 12, "u = 5 м/с", size=13, bold=True, anchor="start"))
    f.append(text(res[0] + 14, res[1] + 6, "(відносно берега)", size=10.5, color=INK, anchor="start"))

    # ── права колонка: суть ──
    bx, _, _ = textbox(
        700, 150,
        "u = u′ + V",
        size=20, pad=14, fill="#eef3fb", stroke=FIELD, sw=1.6)
    f.append(bx)
    b2, _, _ = textbox(
        700, 262,
        "Швидкість човна залежить від системи:\n"
        "• 3 м/с — відносно води;\n"
        "• 5 м/с — відносно берега.\n"
        "Обидва числа правильні. Швидкість\n"
        "самої системи (течія V) просто\n"
        "додається векторно.",
        size=12.5, pad=13, fill=FILL, stroke=LINE, sw=1.4)
    f.append(b2)
    b3, _, _ = textbox(
        700, 392,
        "Стала V зсуває швидкість, але не її\n"
        "зміну → прискорення однакове →\n"
        "F = m·a виглядає в обох системах однаково.",
        size=12, pad=12, fill="#eafaf1", stroke=FIELD, sw=1.4)
    f.append(b3)
    return render(os.path.join(IMG, "velocity-composition.svg"), W, H, *f)


# ── Фігура 3: де принцип ламається — м'яч додається, світло ні ────────────────
def fig_ball_vs_light():
    W, H = 920, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32,
                  "Межа принципу: механічні швидкості додаються, а швидкість світла — ні",
                  size=15.5, bold=True))

    def train(cx, cy, w=150, h=54):
        out = rect(cx - w / 2, cy - h / 2, w, h, fill="#eef2f7", stroke=LINE, sw=1.9, rx=11)
        out += rect(cx - w / 2 + 14, cy - h / 2 + 10, 26, 22, fill="#dbe6f5", stroke=LINE, sw=1.1, rx=3)
        out += rect(cx - w / 2 + 50, cy - h / 2 + 10, 26, 22, fill="#dbe6f5", stroke=LINE, sw=1.1, rx=3)
        out += circle(cx - w / 2 + 34, cy + h / 2 + 9, 11, fill="#d8dee6", stroke=LINE, sw=1.5)
        out += circle(cx + w / 2 - 34, cy + h / 2 + 9, 11, fill="#d8dee6", stroke=LINE, sw=1.5)
        return out

    # ── рядок 1: м'яч ──
    y1 = 150
    f.append(text(150, y1 - 78, "М'яч, кинутий уперед із потяга", size=13.5, bold=True, anchor="start"))
    f.append(train(230, y1))
    f.append(arrow(150, y1 + 52, 250, y1 + 52, color=CURR, sw=3))
    f.append(text(200, y1 + 46, "V = 30 м/с (потяг)", size=12, bold=True, color=CURR))
    # м'яч + його швидкість відносно потяга
    f.append(circle(330, y1 - 6, 8, fill="#fdecea", stroke=BREAK, sw=2))
    f.append(arrow(342, y1 - 6, 430, y1 - 6, color=BREAK, sw=3))
    f.append(text(386, y1 - 16, "u′ = 10 м/с", size=12, bold=True, color=BREAK))
    b1, _, _ = textbox(700, y1, "відносно землі:  30 + 10 = 40 м/с\nшвидкості додаються — принцип Ґалілея",
                       size=12.5, pad=12, fill="#eafaf1", stroke=FIELD, sw=1.4)
    f.append(b1)

    # роздільник
    f.append(line(70, 268, W - 70, 268, color="#e3e8ee", sw=1.4, dash="5,6"))

    # ── рядок 2: світло ──
    y2 = 372
    f.append(text(150, y2 - 78, "Спалах світла з того самого потяга", size=13.5, bold=True, anchor="start"))
    f.append(train(230, y2))
    f.append(arrow(150, y2 + 52, 250, y2 + 52, color=CURR, sw=3))
    f.append(text(200, y2 + 46, "V = 30 м/с (потяг)", size=12, bold=True, color=CURR))
    # промінь — жовта хвиляста стрілка
    lx0 = 322
    d = "M %.1f %.1f " % (lx0, y2 - 6)
    for i in range(7):
        d += "q 8 -8 16 0 q 8 8 16 0 "
    f.append('<path d="%s" fill="none" stroke="#e8a400" stroke-width="3"/>' % d)
    f.append(arrow(lx0 + 210, y2 - 6, lx0 + 222, y2 - 6, color="#e8a400", sw=3))
    f.append(text(lx0 + 96, y2 - 20, "c", size=15, bold=True, italic=True, color="#c98a00"))
    b2, _, _ = textbox(700, y2, "відносно землі:  усе одно c, а не c + 30\nсвітло не підкоряється додаванню",
                       size=12.5, pad=12, fill="#fdecea", stroke=BREAK, sw=1.4)
    f.append(b2)

    b, _, _ = textbox(
        W / 2, 452,
        "Уся механіка кориться Ґалілеєві; світло — ні. Тому перетворення Ґалілея — лише границя малих швидкостей "
        "(v ≪ c),\nа при швидкостях, близьких до c, його заступає перетворення Лоренца (Ейнштейн).",
        size=12, pad=11, fill=FILL, stroke=LINE, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "ball-vs-light.svg"), W, H, *f)


# ── Фігура 4 (вставка hist): часова лінія народження принципу ─────────────────
def fig_relativity_birth_timeline():
    W, H = 1000, 684
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Народження принципу відносності: шар за шаром, а не спалахом", size=16, bold=True))
    f.append(text(W / 2, 56, "ідея старша за назву на дві з половиною тисячі років", size=12.5, color=MUTED))

    PURP = "#5b3fb0"   # формулювання
    ORNG = "#e08a00"   # назва
    rows = [
        ("~499",        "Аріабгата · «Аріабгатія»",
         "човен пояснює видиме обертання неба — відносність спостереження",
         "ІДЕЯ", NEG, "#eaf0fd"),
        ("1584",        "Джордано Бруно · «Вечеря на попіл»",
         "камінь зі щогли рухомого корабля не відстає — довід за Коперника",
         "ІДЕЯ", NEG, "#eaf0fd"),
        ("1632",        "Ґалілео Ґалілей · «Діалог» (вустами Сальвіаті)",
         "ціла закрита каюта: жоден дослід усередині не викаже рівного ходу",
         "ФОРМУЛЮВАННЯ", PURP, "#efeafb"),
        ("1640",        "П'єр Ґассенді · галера в Марселі",
         "справжній камінь падає до підніжжя щогли — уявний дослід став фактом",
         "ДОСЛІД", FIELD, "#eafaf1"),
        ("1687",        "Ісаак Ньютон · «Начала», Короларій V",
         "відносність як наслідок законів руху: F = m·a однакове в усіх системах",
         "ЗАКОН", INK, "#eceff3"),
        ("1904 · 1905", "Анрі Пуанкаре · Альберт Айнштайн",
         "з'являється ім'я «принцип відносності»; піднесено в постулат",
         "НАЗВА", ORNG, "#fdf3e0"),
        ("~1911",       "релятивістська література (Франк, Роте)",
         "«перетворення Ґалілея» — ретроспективний ярлик, пара до Лоренца",
         "РЕТРОНІМ", POS, "#fdecea"),
    ]

    cy0, step = 106, 82
    for i, (year, actor, note, tag, col, tint) in enumerate(rows):
        cy = cy0 + i * step
        # картка рядка
        f.append(rect(48, cy - 34, W - 96, 68, fill="#fbfcfd", stroke="#e6eaef", sw=1.3, rx=10))
        # кольорова смуга-акцент зліва
        f.append(rect(52, cy - 30, 6, 60, fill=col, stroke='none', sw=0, rx=3))
        # з'єднувальна лінія часу між картками
        if i < len(rows) - 1:
            f.append(line(90, cy + 34, 90, cy + step - 34, color="#dfe4ea", sw=1.6))
        # пігулка-шар (фіксована ширина, текст гарантовано влазить)
        f.append(fitbox(74, cy - 15, 156, 30, tag, size=11.5, pad=7,
                        fill=tint, stroke=col, sw=1.5, color=col, bold=True, rx=15))
        # рік + дійова особа (жирний рядок)
        f.append(text(250, cy - 6, year + " — " + actor, size=14, bold=True, anchor="start"))
        # внесок (другорядний рядок)
        f.append(text(250, cy + 15, note, size=12.5, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "relativity-birth-timeline.svg"), W, H, *f)


# ── Фігура 5 (вставка math): геометрія бусту x′ = x − Vt, спільний час t′ = t ──
def fig_boost_geometry():
    W, H = 920, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32,
                  "Геометрія переходу: чому x′ = x − Vt і чому час спільний t′ = t",
                  size=15.5, bold=True))

    ax_y = 236
    Ox, Opx, Px = 150, 360, 690       # O, O′ (дрейф Vt = 210 px), точка P
    # спільна просторова вісь
    f.append(arrow(90, ax_y, 800, ax_y, color=INK, sw=2))
    f.append(text(796, ax_y - 12, "простір", size=12, color=MUTED, anchor="end"))
    # позначки O, O′, P з підписами над віссю
    f.append(circle(Ox, ax_y, 5, fill=INK, stroke=INK, sw=1))
    f.append(text(Ox, ax_y - 16, "O", size=13, bold=True))
    f.append(text(Ox, ax_y - 33, "початок S", size=10.5, color=MUTED))
    f.append(circle(Opx, ax_y, 5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(Opx, ax_y - 16, "O′", size=13, bold=True, color=NEG))
    f.append(text(Opx, ax_y - 33, "початок S′ (пливе на V)", size=10.5, color=NEG))
    f.append(circle(Px, ax_y, 6, fill="#fef6e7", stroke=INK, sw=2))
    f.append(text(Px, ax_y - 16, "P", size=14, bold=True))
    # тонкі вертикалі-орієнтири від точок униз до брусів
    for xx in (Ox, Opx, Px):
        f.append(line(xx, ax_y + 8, xx, 314, color="#cdd6df", sw=1, dash="3,4"))
    # бруси Vt (O→O′) і x′ (O′→P) — суміжні, на одному рівні
    yb = 292
    f.append(line(Ox, yb, Opx, yb, color=CURR, sw=2.6))
    f.append(text((Ox + Opx) / 2, yb - 10, "Vt", size=13, bold=True, color=CURR))
    f.append(line(Opx, yb, Px, yb, color=NEG, sw=2.6))
    f.append(text((Opx + Px) / 2, yb - 10, "x′  (координата P у S′)", size=12, bold=True, color=NEG))
    # брус x (O→P) — нижче, весь проліт
    yb2 = 324
    f.append(line(Ox, yb2, Px, yb2, color=INK, sw=2.6))
    f.append(text((Ox + Px) / 2, yb2 + 19, "x  (координата P у S)  =  x′ + Vt", size=12.5, bold=True))
    # засічки на кінцях брусів
    for (x1, x2, yy, col) in ((Ox, Opx, yb, CURR), (Opx, Px, yb, NEG), (Ox, Px, yb2, INK)):
        f.append(line(x1, yy - 5, x1, yy + 5, color=col, sw=2))
        f.append(line(x2, yy - 5, x2, yy + 5, color=col, sw=2))

    # годинник + абсолютний час (угорі праворуч)
    cx, cy = 812, 112
    f.append(circle(cx, cy, 24, fill="#f6f8fb", stroke=LINE, sw=1.8))
    f.append(line(cx, cy, cx, cy - 15, color=INK, sw=2.2))       # хвилинна
    f.append(line(cx, cy, cx + 11, cy + 6, color=INK, sw=2.2))   # годинна
    f.append(circle(cx, cy, 2.6, fill=INK, stroke=INK, sw=1))
    f.append(text(cx, cy + 43, "t′ = t", size=14, bold=True))
    f.append(text(cx, cy + 61, "спільний час", size=10.5, color=MUTED))

    b, _, _ = textbox(
        W / 2, 388,
        "Початок S′ за час t відплив на Vt, тож координата тієї самої точки в S′ менша рівно на цей дрейф: x′ = x − Vt.\n"
        "Різниця двох координат від системи не залежить: (x₂ − x₁) = (x₂′ − x₁′) — спільний дрейф Vt скорочується.",
        size=12, pad=12, fill="#eef3fb", stroke=FIELD, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "galilei-boost-geometry.svg"), W, H, *f)


# ── Фігура 6 (вставка math): Ґалілей-зсув vs Лоренц-поворот у просторі-часі ────
def fig_galilei_vs_lorentz():
    W, H = 940, 492
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30,
                  "Що перехід робить із простором-часом: Ґалілей зсуває, Лоренц повертає",
                  size=15.5, bold=True))
    f.append(line(470, 58, 470, 344, color="#dfe4ea", sw=1.3, dash="4,6"))

    top, By = 104, 312

    # ── ліва панель: Ґалілей ──
    Lx = 150
    f.append(text(275, 62, "Ґалілей: t′ = t (час абсолютний)", size=13.5, bold=True))
    f.append(arrow(Lx, By, Lx + 250, By, color=INK, sw=2))        # вісь x
    f.append(text(Lx + 250, By + 22, "x", size=13, bold=True, italic=True))
    f.append(arrow(Lx, By, Lx, top, color=INK, sw=2))             # вісь t
    f.append(text(Lx - 15, top + 2, "t", size=13, bold=True, italic=True))
    # t′-вісь — світова лінія рухомого початку x = Vt (нахил праворуч)
    f.append(arrow(Lx, By, Lx + 96, top, color=NEG, sw=2.6))
    f.append(text(Lx + 108, top + 4, "t′", size=13, bold=True, italic=True, color=NEG))
    # лінія однакового часу — горизонтальна (спільна для обох систем)
    sy = 208
    f.append(line(Lx, sy, Lx + 250, sy, color=FIELD, sw=2, dash="7,5"))
    f.append(text(Lx + 250, sy - 9, "однаковий час — горизонталь", size=10.5, color=FIELD, anchor="end"))
    f.append(text(Lx + 150, By - 10, "x′ ∥ x", size=11.5, color=NEG, anchor="start"))

    # ── права панель: Лоренц ──
    Rx = 560
    f.append(text(686, 62, "Лоренц: помітне V/c", size=13.5, bold=True))
    f.append(arrow(Rx, By, Rx + 250, By, color=INK, sw=2))        # вісь x
    f.append(text(Rx + 250, By + 22, "x", size=13, bold=True, italic=True))
    f.append(arrow(Rx, By, Rx, top, color=INK, sw=2))             # вісь ct
    f.append(text(Rx - 20, top + 2, "ct", size=13, bold=True, italic=True))
    # світлова лінія 45°
    f.append(line(Rx, By, Rx + 208, By - 208, color="#e8a400", sw=2, dash="7,5"))
    f.append(text(Rx + 150, By - 176, "світло (45°)", size=10.5, color="#c98a00", anchor="start"))
    # ct′-вісь — нахил праворуч до світлової
    f.append(arrow(Rx, By, Rx + 96, top, color=NEG, sw=2.6))
    f.append(text(Rx + 108, top + 4, "ct′", size=13, bold=True, italic=True, color=NEG))
    # x′-вісь — нахил угору до світлової (симетрично) = похила лінія однакового часу
    f.append(arrow(Rx, By, Rx + 240, By - 120, color=NEG, sw=2.6))
    f.append(text(Rx + 252, By - 120, "x′", size=13, bold=True, italic=True, color=NEG))
    f.append(text(Rx + 150, By - 44, "однаковий час — похило", size=10.5, color=NEG, anchor="start"))

    b, _, _ = textbox(
        W / 2, 434,
        "Ґалілей зсуває лише вісь часу — лінії однакового часу лишаються\n"
        "горизонтальними: час у всіх системах спільний, t′ = t.\n"
        "Лоренц повертає обидві осі до світлової лінії (45°) — і одночасність\n"
        "стає похилою, залежною від системи.\n"
        "Нахил x′-осі має порядок V/c: при V ≪ c він зникає (γ → 1) — Лоренц зливається з Ґалілеєм.",
        size=12, pad=12, fill=FILL, stroke=LINE, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "galilei-vs-lorentz-spacetime.svg"), W, H, *f)


if __name__ == "__main__":
    p1 = fig_galileo_ship()
    p2 = fig_velocity_composition()
    p3 = fig_ball_vs_light()
    p4 = fig_relativity_birth_timeline()
    p5 = fig_boost_geometry()
    p6 = fig_galilei_vs_lorentz()
    print("written:")
    for p in (p1, p2, p3, p4, p5, p6):
        print("  ", p)
