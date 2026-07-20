# -*- coding: utf-8 -*-
"""Фігури до теми «Закон збереження енергії».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# локальні кольори енергій (світлі заливки + міцний контур)
PE_F, PE_E = "#a9dcbd", FIELD          # потенціальна — зелена (запас)
KE_F, KE_E = "#f2c982", "#cf8a1a"      # кінетична — бурштинова (рух)
HT_F, HT_E = "#eeb0a6", POS            # теплова — червона (нагрів)


def poly(pts, color=INK, sw=2.4, dash=None, fill="none"):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, fill, color, sw, da))


def swatch(x, y, fill, edge, label, size=12):
    return (rect(x, y - 9, 20, 14, fill=fill, stroke=edge, sw=1.5, rx=3)
            + text(x + 28, y + 2, label, size=size, color=INK, anchor="start"))


# ── Фігура 1: переливання T ↔ U, сума стала ─────────────────────────────────
def fig_energy_trade():
    W, H = 900, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Кінетична й потенціальна енергія переливаються — сума стала",
                  size=17, bold=True))

    # три станції: x-центр, частка потенціальної (0..1) від повної, підпис
    stations = [(160, 0.90, "A"), (450, 0.10, "B"), (740, 0.50, "C")]

    # ── схематичний схил із кулькою у трьох точках ──
    gy = 150                                    # опорний рівень «землі» схилу
    track = [(70, gy - 70), (160, gy - 66), (280, gy - 34),
             (450, gy + 42), (620, gy - 2), (740, gy - 20), (830, gy - 16)]
    f.append(poly(track, color=MUTED, sw=3.2))
    # висота кульки на схилі приблизно за часткою U
    ball_y = {160: gy - 66, 450: gy + 42, 740: gy - 20}
    for cx, uf, name in stations:
        by = ball_y[cx]
        f.append(circle(cx, by - 12, 11, fill=KE_F, stroke=INK, sw=1.8))
        f.append(text(cx, by - 30, name, size=14, bold=True, color=INK))

    # ── стовпчики енергій під станціями ──
    base = 430                                  # низ стовпчиків
    top = 250                                   # спільний верх (повна енергія)
    full = base - top                           # 180
    bw = 84
    # пунктир повної енергії через усі три
    f.append(line(90, top, 810, top, color=MUTED, sw=1.5, dash="7,5"))
    f.append(text(812, top + 4, "T + U = стала", size=13, bold=True,
                  color=INK, anchor="start"))

    descr = {160: "майже все —\nу висоті", 450: "майже все —\nу русі",
             740: "порівну"}
    for cx, uf, name in stations:
        x = cx - bw / 2
        u_h = full * uf                         # висота потенціальної частини
        k_h = full - u_h                        # кінетична — решта до повної
        # потенціальна (знизу)
        f.append(rect(x, base - u_h, bw, u_h, fill=PE_F, stroke=PE_E, sw=1.6, rx=3))
        # кінетична (згори)
        f.append(rect(x, top, bw, k_h, fill=KE_F, stroke=KE_E, sw=1.6, rx=3))
        # тонкий конектор від кульки до стовпчика
        f.append(line(cx, ball_y[cx] - 1, cx, base - u_h, color="#cfd6de",
                      sw=1.2, dash="3,4"))
        # підпис станції під стовпчиком
        f.append(text(cx, base + 20, name, size=14, bold=True, color=INK))
        f.append(mtext(cx, base + 38, descr[cx], size=11.5, color=MUTED))

    # легенда
    f.append(swatch(150, 462, PE_F, PE_E, "U — потенціальна (висота)"))
    f.append(swatch(470, 462, KE_F, KE_E, "T — кінетична (рух)"))
    return render(os.path.join(IMG, "energy-trade.svg"), W, H, *f)


# ── Фігура 2: аудит енергії стрибучого м'яча (механічна → теплова) ───────────
def fig_friction_ledger():
    W, H = 900, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Стрибучий м'яч: механічна енергія перетікає в тепло, сума стала",
                  size=17, bold=True))

    xs = [140, 300, 460, 620, 780]              # центри стрибків/стовпчиків
    frac = [1.0, 0.70, 0.49, 0.34, 0.24]        # частка механічної (r = 0.7 за стрибок)

    # ── верх: параболічні стрибки спадної висоти ──
    ground = 250
    Hmax = 150
    f.append(line(70, ground, 850, ground, color=INK, sw=2))   # підлога
    for i, cx in enumerate(xs):
        peak = Hmax * frac[i]
        half = 74
        pts = []
        for k in range(21):
            t = k / 20.0                        # 0..1 зліва направо
            px = cx - half + t * 2 * half
            py = ground - peak * (1 - (2 * t - 1) ** 2)   # парабола, вершина в cx
            pts.append((px, py))
        f.append(poly(pts, color=KE_E, sw=2.2))
        f.append(circle(cx, ground - peak, 9, fill=KE_F, stroke=INK, sw=1.6))
        f.append(text(cx, ground + 20, "удар %d" % i if i else "старт",
                      size=11.5, color=MUTED))

    # ── низ: стовпчики механічна(зелена) + теплова(червона) = стала ──
    base = 470
    top = 300
    full = base - top
    bw = 82
    f.append(line(95, top, 825, top, color=MUTED, sw=1.5, dash="7,5"))
    f.append(text(827, top + 4, "повна = стала", size=12.5, bold=True,
                  color=INK, anchor="start"))
    for i, cx in enumerate(xs):
        x = cx - bw / 2
        m_h = full * frac[i]                    # механічна (знизу)
        h_h = full - m_h                        # накопичене тепло (згори)
        f.append(rect(x, base - m_h, bw, m_h, fill=PE_F, stroke=PE_E, sw=1.6, rx=3))
        if h_h > 1:
            f.append(rect(x, top, bw, h_h, fill=HT_F, stroke=HT_E, sw=1.6, rx=3))
        f.append(text(cx, base + 18, "%d%%" % round(frac[i] * 100),
                      size=12, bold=True, color=PE_E))

    f.append(swatch(150, 495, PE_F, PE_E, "механічна (рух + висота)", size=12))
    f.append(swatch(470, 495, HT_F, HT_E, "теплова (нагрів від ударів)", size=12))
    return render(os.path.join(IMG, "friction-ledger.svg"), W, H, *f)


# ── Фігура 3: чому зберігається — однорідність часу vs вічний двигун ─────────
def no_sign(cx, cy, r, color=POS, sw=3):
    a = r * 0.71
    return (circle(cx, cy, r, fill="none", stroke=color, sw=sw)
            + line(cx - a, cy + a, cx + a, cy - a, color=color, sw=sw))


def weight(cx, cy, r=10, fill=KE_F):
    return circle(cx, cy, r, fill=fill, stroke=INK, sw=1.8)


def fig_time_symmetry():
    W, H = 980, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Чому енергія зберігається: однорідність часу",
                  size=17, bold=True))

    # роздільник панелей
    f.append(line(490, 58, 490, 470, color="#d6dde6", sw=1.4, dash="5,6"))
    f.append(text(250, 58, "Закони ті самі в кожну мить", size=14, bold=True, color=FIELD))
    f.append(text(735, 58, "Якби закони дрейфували з часом", size=14, bold=True, color=POS))

    # ── ЛІВА панель: той самий дослід сьогодні й завтра ──
    ax_y = 300
    f.append(arrow(70, ax_y, 450, ax_y, color=MUTED, sw=1.6))     # вісь часу
    f.append(text(452, ax_y + 4, "час", size=12, color=MUTED, anchor="start"))
    for lx, tick in ((160, "сьогодні"), (360, "завтра")):
        f.append(line(lx, ax_y, lx, ax_y + 6, color=MUTED, sw=1.4))
        f.append(text(lx, ax_y + 22, tick, size=12, color=MUTED))
        # мінідослід: тіло падає з висоти h, віддає енергію E (однаково)
        f.append(line(lx, 120, lx, 205, color="#cfd6de", sw=1.3, dash="3,4"))
        f.append(weight(lx, 128))
        f.append(weight(lx, 198, fill="#e7edf3"))
        f.append(arrow(lx, 140, lx, 190, color=INK, sw=2))
        f.append(text(lx + 16, 168, "E", size=14, bold=True, italic=True,
                      color=INK, anchor="start"))
    f.append(text(255, 108, "той самий дослід → той самий результат",
                  size=12, color=INK))
    f.append(fitbox(95, 360, 320, 46,
                    "закон не залежить від того, КОЛИ дивишся\n⇒ повна енергія зберігається",
                    size=13, pad=9, fill="#eef6ef", stroke=FIELD, sw=1.8, color=INK))

    # ── ПРАВА панель: дрейф → дармова енергія → заборонено ──
    # ранок: тяжіння слабше — підняти дешево
    f.append(fitbox(540, 92, 180, 30, "ранок: тяжіння слабше", size=12, pad=6,
                    fill=FILL, stroke=MUTED, sw=1.4))
    f.append(weight(560, 190))
    f.append(arrow(560, 182, 560, 138, color=NEG, sw=2.2))       # підйом угору
    f.append(mtext(560, 214, "підняти —\nдешево", size=11, color=NEG))

    # вечір: тяжіння дужче — впаде й дасть більше
    f.append(fitbox(760, 92, 180, 30, "вечір: тяжіння дужче", size=12, pad=6,
                    fill=FILL, stroke=MUTED, sw=1.4))
    f.append(weight(800, 138))
    f.append(arrow(800, 146, 800, 200, color=POS, sw=3))         # падіння вниз (жирніше)
    f.append(mtext(800, 224, "впаде —\nдасть більше", size=11, color=POS))

    # підсумок: виграш > витрати → дармова енергія → заборонено
    f.append(arrow(600, 250, 740, 250, color=INK, sw=2))
    f.append(fitbox(535, 300, 300, 44,
                    "виграш − витрата > 0\nдармова енергія з нічого",
                    size=13, pad=8, fill="#fdecea", stroke=POS, sw=1.6, color=INK))
    f.append(no_sign(880, 322, 26, color=POS, sw=4))
    f.append(text(880, 366, "вічний двигун", size=11.5, color=POS))
    f.append(fitbox(535, 402, 405, 40,
                    "цього не буває → сила НЕ залежить від часу",
                    size=13, pad=8, fill=FILL, stroke=MUTED, sw=1.4, color=INK))

    return render(os.path.join(IMG, "time-symmetry.svg"), W, H, *f)


# ── Фігура 4: консервативна сила — незалежність від дороги, петля = 0 ─────────
def fig_conservative_paths():
    W, H = 980, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Консервативна сила: робота не залежить від дороги",
                  size=17, bold=True))
    f.append(line(495, 58, 495, 440, color="#d6dde6", sw=1.4, dash="5,6"))
    f.append(text(250, 60, "Дві дороги — однакова робота", size=14, bold=True, color=FIELD))
    f.append(text(742, 60, "Замкнений круг — робота нуль", size=14, bold=True, color=NEG))

    # ── ЛІВА панель: A→B двома дорогами ──
    Ax, Ay, Bx, By = 155, 365, 420, 155
    # висотна дужка h ліворуч
    f.append(line(105, By, 105, Ay, color=MUTED, sw=1.6))
    f.append(line(105, By, 112, By, color=MUTED, sw=1.6))
    f.append(line(105, Ay, 112, Ay, color=MUTED, sw=1.6))
    f.append(text(90, (Ay + By) / 2 + 4, "h", size=14, bold=True, color=MUTED, anchor="end"))
    f.append(line(105, By, Bx, By, color="#cfd6de", sw=1.2, dash="4,5"))
    f.append(line(105, Ay, Ax, Ay, color="#cfd6de", sw=1.2, dash="4,5"))
    # дорога 1 — пряма (зелена суцільна)
    f.append(line(Ax, Ay, Bx, By, color=FIELD, sw=3.4))
    # дорога 2 — гак (синя пунктирна)
    f.append(poly([(Ax, Ay), (300, 366), (360, 300), (400, 225), (Bx, By)],
                  color=NEG, sw=3.0, dash="8,6"))
    f.append(circle(Ax, Ay, 6, fill=KE_F, stroke=INK, sw=1.8))
    f.append(circle(Bx, By, 6, fill=KE_F, stroke=INK, sw=1.8))
    f.append(text(Ax - 4, Ay + 22, "A", size=14, bold=True, color=INK))
    f.append(text(Bx + 16, By + 4, "B", size=14, bold=True, color=INK, anchor="start"))
    f.append(text(300, 205, "дорога 1", size=12.5, bold=True, color=FIELD))
    f.append(text(245, 345, "дорога 2", size=12.5, bold=True, color=NEG))
    f.append(fitbox(120, 452, 300, 40,
                    "W однакова для обох доріг\nзалежить лише від висоти h",
                    size=13, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.6, color=INK))

    # ── ПРАВА панель: обхід по колу дає нуль ──
    ax, ay, bx, by = 655, 365, 885, 155
    f.append(text(768, 112, "∮ F·ds = 0", size=19, bold=True, color=INK))
    f.append(arrow(ax, ay, bx, by, color=FIELD, sw=3.0))       # туди A→B
    f.append(poly([(bx, by), (830, 300), (720, 362), (663, ay)],
                  color=NEG, sw=3.0, dash="8,6"))               # назад B→A
    f.append(arrow(720, 362, 665, 365, color=NEG, sw=2.6))     # голівка стрілки назад
    f.append(circle(ax, ay, 6, fill=KE_F, stroke=INK, sw=1.8))
    f.append(circle(bx, by, 6, fill=KE_F, stroke=INK, sw=1.8))
    f.append(text(ax - 4, ay + 22, "A", size=14, bold=True, color=INK))
    f.append(text(bx + 16, by + 4, "B", size=14, bold=True, color=INK, anchor="start"))
    f.append(fitbox(600, 452, 300, 40,
                    "обхід повертає, скільки взяв\n⇒ можна ввести потенціал U",
                    size=13, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.6, color=INK))
    return render(os.path.join(IMG, "conservative-paths.svg"), W, H, *f)


# ── Фігура 5: робота = площа під силою → m·g·h (прямокутник), ½·k·x² (трикутник)
def fig_work_as_area():
    W, H = 1000, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Робота = площа під силою: звідки m·g·h і ½·k·x²",
                  size=17, bold=True))
    f.append(line(495, 58, 495, 410, color="#d6dde6", sw=1.4, dash="5,6"))
    f.append(text(255, 58, "Стала сила → прямокутник → m·g·h", size=13.5, bold=True, color=INK))
    f.append(text(740, 58, "Лінійна сила → трикутник → ½·k·x²", size=13.5, bold=True, color=INK))

    # ── ЛІВА: стала сила m·g на шляху h ──
    Ox, Oy = 130, 370
    Fx, Fy = 380, 210                                  # правий край шляху / рівень сили
    f.append(rect(Ox, Fy, Fx - Ox, Oy - Fy, fill=KE_F, stroke=KE_E, sw=1.6, rx=0))
    f.append(arrow(Ox, Oy, 460, Oy, color=INK, sw=1.8))     # вісь шляху
    f.append(arrow(Ox, Oy, Ox, 100, color=INK, sw=1.8))     # вісь сили
    f.append(text(462, Oy + 4, "переміщення", size=11.5, color=MUTED, anchor="start"))
    f.append(text(Ox + 6, 96, "сила F", size=11.5, color=MUTED, anchor="start"))
    f.append(line(Ox, Fy, Fx, Fy, color=POS, sw=2.6))       # рівень F = m·g
    f.append(text(Fx + 10, Fy - 2, "F = m·g", size=12.5, bold=True, color=POS, anchor="start"))
    f.append(text((Ox + Fx) / 2, 296, "площа = m·g·h", size=13.5, bold=True, color=INK))
    f.append(line(Fx, Oy, Fx, Oy + 6, color=INK, sw=1.6))
    f.append(text(Fx, Oy + 22, "h", size=13, bold=True, color=INK))
    f.append(text(Ox - 8, Fy + 4, "m·g", size=12, color=POS, anchor="end"))

    # ── ПРАВА: лінійна сила k·x на розтягу x ──
    Px, Py = 600, 370
    Xx, Yt = 860, 160                                  # край розтягу / вершина сили
    f.append(poly([(Px, Py), (Xx, Py), (Xx, Yt)], color=KE_E, sw=1.6, fill=KE_F))
    f.append(arrow(Px, Py, 932, Py, color=INK, sw=1.8))     # вісь розтягу
    f.append(arrow(Px, Py, Px, 100, color=INK, sw=1.8))     # вісь сили
    f.append(text(936, Py + 4, "розтяг x", size=11.5, color=MUTED, anchor="start"))
    f.append(text(Px + 6, 96, "сила F", size=11.5, color=MUTED, anchor="start"))
    f.append(line(Px, Py, Xx, Yt, color=POS, sw=2.6))       # F = k·x
    f.append(text(Xx + 8, Yt, "F = k·x", size=12.5, bold=True, color=POS, anchor="start"))
    f.append(line(Px, Yt, Xx, Yt, color=MUTED, sw=1.2, dash="4,5"))
    f.append(text(Px - 8, Yt + 4, "k·x", size=12, color=POS, anchor="end"))
    f.append(text(775, 316, "площа = ½·k·x²", size=13.5, bold=True, color=INK))
    f.append(line(Xx, Py, Xx, Py + 6, color=INK, sw=1.6))
    f.append(text(Xx, Py + 22, "x", size=13, bold=True, color=INK))
    return render(os.path.join(IMG, "work-as-area.svg"), W, H, *f)


# ── Фігура 6: народження закону — столітня стрічка часу (для hist-вставки) ────
def fig_birth_timeline():
    W, H = 1080, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Народження закону збереження енергії: столітня дорога",
                  size=17, bold=True))

    axis_y = 235
    f.append(line(60, axis_y, 1018, axis_y, color=MUTED, sw=2))
    f.append(arrow(1010, axis_y, 1040, axis_y, color=MUTED, sw=1.8))
    f.append(text(1046, axis_y + 4, "час", size=12, color=MUTED, anchor="start"))

    # (x, рік, колір-епохи, назва[3 рядки], над_віссю)
    nodes = [
        (115, "1686", NEG,   "Ляйбніц\nсила руху — mv²,\nа не mv",         True),
        (257, "1722", NEG,   "с'Гравесанде\nкульки в глину:\nямка ∝ v²",   False),
        (398, "1740", FIELD, "дю Шатле\nmv² зберігається\nокремо від mv",  True),
        (540, "1807", FIELD, "Юнг\nназвав це\n«енергія»",                  False),
        (682, "1842", POS,   "Маєр і Джоуль\nтепло = робота\n(екв. тепла)", True),
        (823, "1847", POS,   "Гельмгольц\nусе — один\nзагальний закон",    False),
        (965, "1853", MUTED, "Ренкін, Кельвін\n«потенціальна»\nй «кінетична»", True),
    ]

    bw, bh = 202, 76
    for x, yr, col, name, above in nodes:
        emphasize = (yr == "1740")
        if above:
            f.append(fitbox(x - bw / 2, 150 - bh, bw, bh, name, size=13, pad=8,
                            fill=FILL, stroke=col, sw=2.4 if emphasize else 1.6,
                            color=INK, bold=True))
            f.append(line(x, 150, x, axis_y - 9, color=col, sw=1.4, dash="3,4"))
            f.append(text(x, axis_y + 24, yr, size=13, bold=True, color=col))
        else:
            f.append(fitbox(x - bw / 2, 322, bw, bh, name, size=13, pad=8,
                            fill=FILL, stroke=col, sw=1.6, color=INK, bold=True))
            f.append(line(x, axis_y + 9, x, 322, color=col, sw=1.4, dash="3,4"))
            f.append(text(x, axis_y - 14, yr, size=13, bold=True, color=col))
        f.append(circle(x, axis_y, 7, fill=col, stroke=BG, sw=2))
        if emphasize:
            f.append(circle(x, axis_y, 12, fill="none", stroke=FIELD, sw=2.2))
            f.append(text(x, 62, "повернене з забуття", size=11, italic=True,
                          color=FIELD))

    # легенда епох
    ly = 452
    for lx, col, lab in [(70, NEG, "суперечка: mv чи mv²"),
                         (360, FIELD, "слово «енергія»"),
                         (585, POS, "тепло = робота"),
                         (800, MUTED, "сучасні назви")]:
        f.append(rect(lx, ly - 11, 17, 13, fill=col, stroke=col, sw=1, rx=3))
        f.append(text(lx + 24, ly, lab, size=12, color=INK, anchor="start"))

    return render(os.path.join(IMG, "birth-timeline.svg"), W, H, *f)


# ── Симуляція для proj-вставки: аудит енергії стрибучого м'яча ────────────────
G = 9.81


def _step_exact(y, v, dt, m, e):
    """Просунути стан (y,v) на час dt ТОЧНОЮ кінематикою сталого прискорення,
    обробивши всі удари всередині кроку. Повертає (y, v, dQ)."""
    if y == 0.0 and v == 0.0:
        return 0.0, 0.0, 0.0          # м'яч уже лежить — нічого не діється
    dQ = 0.0
    tau = dt
    while tau > 1e-15:
        disc = v * v + 2 * G * y      # квадрат швидкості біля підлоги
        s = math.sqrt(disc) if disc > 0 else 0.0
        tc = (v + s) / G              # час до наступного дотику підлоги
        if s == 0.0 or tc <= 0.0 or tc >= tau:
            y = y + v * tau - 0.5 * G * tau * tau     # вільний політ на tau
            v = v - G * tau
            break
        # чи встигне м'яч ЗКОЛАПСУВАТИ (нескінченно ударів) за лишок часу?
        t_rest = tc + (2 * s / G) * e / (1 - e)
        if t_rest <= tau:
            dQ += 0.5 * m * (v * v + 2 * G * y)       # уся механічна — в тепло
            y, v = 0.0, 0.0
            break
        v_hit = v - G * tc            # швидкість у мить удару (= −s)
        dQ += 0.5 * m * v_hit * v_hit * (1 - e * e)   # народжене тепло удару
        v = -e * v_hit               # відскок угору
        y = 0.0
        tau -= tc
    return y, v, dQ


def _run_ball(h0, m, e, dt, t_end, euler=False):
    """Аудит енергії. Повертає (E0, ts, Em, Qs, Et)."""
    E0 = m * G * h0
    y, v, Q, t = h0, 0.0, 0.0, 0.0
    ts, Em, Qs, Et = [0.0], [E0], [0.0], [E0]
    for _ in range(int(round(t_end / dt))):
        if euler:                              # наївний явний Ейлер
            y2, v2 = y + v * dt, v - G * dt
            if y2 < 0.0:                        # удар ловимо на межі кроку
                Q += 0.5 * m * v2 * v2 * (1 - e * e)
                v2, y2 = -e * v2, 0.0
            y, v = y2, v2
        else:
            y, v, dQ = _step_exact(y, v, dt, m, e)
            Q += dQ
        t += dt
        em = 0.5 * m * v * v + m * G * y
        ts.append(t); Em.append(em); Qs.append(Q); Et.append(em + Q)
    return E0, ts, Em, Qs, Et


def _mapper(x0, x1, y0, y1, px, py, pw, ph):
    """Лінійне відображення (data)→(pixels) у рамку (px,py,pw,ph); y — угору."""
    def M(x, y):
        return (px + (x - x0) / (x1 - x0) * pw,
                py + ph - (y - y0) / (y1 - y0) * ph)
    return M


# ── Фігура 7: слід аудиту — механічна ↓, теплова ↑, повна = стала ─────────────
def fig_audit_trace():
    W, H = 940, 520
    h0, m, e, dt, t_end = 2.0, 0.15, 0.75, 0.004, 4.6
    E0, ts, Em, Qs, Et = _run_ball(h0, m, e, dt, t_end)
    res = max(abs(v - E0) for v in Et) / E0
    print("  [audit] E0=%.4f J, max|Etot-E0|/E0 = %.2e" % (E0, res))

    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Слід аудиту: механічна тане, теплова росте, повна — стала",
                  size=17, bold=True))
    f.append(fitbox(W / 2 - 205, 40, 410, 26,
                    "залишок |повна − E₀| ≈ %.0e · E₀  —  машинний нуль" % res,
                    size=12.5, pad=6, fill="#eef6ef", stroke=FIELD, sw=1.5, color=INK))

    px, py, pw, ph = 90, 86, 760, 350
    ymax = E0 * 1.12
    M = _mapper(0, t_end, 0, ymax, px, py, pw, ph)
    # осі
    f.append(line(px, py, px, py + ph, color=INK, sw=1.8))
    f.append(line(px, py + ph, px + pw, py + ph, color=INK, sw=1.8))
    f.append(text(px - 12, py + ph + 4, "0", size=12, color=MUTED, anchor="end"))
    for frac in (0.5, 1.0):
        yy = M(0, E0 * frac)[1]
        f.append(line(px - 5, yy, px, yy, color=MUTED, sw=1.4))
        f.append(text(px - 12, yy + 4, ("E₀" if frac == 1.0 else "E₀/2"),
                      size=12, color=MUTED, anchor="end"))
        f.append(line(px, yy, px + pw, yy, color="#e7ecf2", sw=1.0))
    for tk in range(0, int(t_end) + 1):
        xx = M(tk, 0)[0]
        f.append(line(xx, py + ph, xx, py + ph + 5, color=MUTED, sw=1.4))
        f.append(text(xx, py + ph + 22, "%d" % tk, size=12, color=MUTED))
    f.append(text(px + pw / 2, py + ph + 44, "час, с", size=12.5, color=MUTED))

    # пунктир повної енергії E₀
    f.append(line(px, M(0, E0)[1], px + pw, M(0, E0)[1], color=INK, sw=1.4, dash="2,4"))

    def curve(vals, color, sw):
        return poly([M(ts[i], vals[i]) for i in range(len(ts))], color=color, sw=sw)

    f.append(curve(Qs, HT_E, 2.4))     # теплова — росте сходинками
    f.append(curve(Em, PE_E, 2.4))     # механічна — спадає сходинками
    f.append(curve(Et, INK, 2.6))      # повна — пряма на E₀

    # підписи кривих просто на полотні
    f.append(text(px + pw - 6, M(t_end, E0)[1] - 10, "повна = E₀", size=13,
                  bold=True, color=INK, anchor="end"))
    f.append(text(px + pw - 6, M(t_end, E0 * 0.93)[1] + 6, "теплова Q", size=13,
                  bold=True, color=HT_E, anchor="end"))
    f.append(text(px + 150, M(0.9, E0 * 0.62)[1], "механічна T+U", size=13,
                  bold=True, color=PE_E, anchor="start"))

    f.append(swatch(150, 500, PE_F, PE_E, "механічна T+U (спадає)"))
    f.append(swatch(430, 500, HT_F, HT_E, "теплова Q (накопичується)"))
    f.append(swatch(690, 500, "#ffffff", INK, "повна = стала"))
    return render(os.path.join(IMG, "audit-trace.svg"), W, H, *f)


# ── Фігура 8: чому важить інтегратор — нев'язка балансу в часі ────────────────
def fig_integrator_residual():
    W, H = 940, 500
    h0, m, e, t_end = 2.0, 0.15, 0.75, 4.6
    dt = 0.01
    E0x, tx, _, _, Etx = _run_ball(h0, m, e, dt, t_end, euler=False)
    E0e, te, _, _, Ete = _run_ball(h0, m, e, dt, t_end, euler=True)
    rx = [(v - E0x) / E0x for v in Etx]
    re = [(v - E0e) / E0e for v in Ete]
    drift = re[-1]
    exact_max = max(abs(v) for v in rx)
    print("  [resid] dt=%.3f  euler final drift=%.3f  exact max=%.2e"
          % (dt, drift, exact_max))

    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Чому важить інтегратор: нев'язка балансу (повна − E₀)/E₀",
                  size=17, bold=True))

    px, py, pw, ph = 90, 74, 760, 330
    ytop = max(0.05, drift * 1.25)
    M = _mapper(0, t_end, -0.02, ytop, px, py, pw, ph)
    # осі та нульова лінія
    f.append(line(px, py, px, py + ph, color=INK, sw=1.8))
    y0 = M(0, 0)[1]
    f.append(line(px, y0, px + pw, y0, color=INK, sw=1.6))
    f.append(text(px - 12, y0 + 4, "0", size=12, color=MUTED, anchor="end"))
    for frac in (0.25, 0.5, 0.75, 1.0):
        val = ytop * frac
        yy = M(0, val)[1]
        f.append(line(px - 5, yy, px, yy, color=MUTED, sw=1.2))
        f.append(text(px - 12, yy + 4, "%.0f%%" % (val * 100), size=11,
                      color=MUTED, anchor="end"))
        f.append(line(px, yy, px + pw, yy, color="#eef1f5", sw=1.0))
    for tk in range(0, int(t_end) + 1):
        xx = M(tk, 0)[0]
        f.append(line(xx, py + ph, xx, py + ph + 5, color=MUTED, sw=1.3))
        f.append(text(xx, py + ph + 22, "%d" % tk, size=12, color=MUTED))
    f.append(text(px + pw / 2, py + ph + 44, "час, с", size=12.5, color=MUTED))

    f.append(poly([M(te[i], re[i]) for i in range(len(te))], color=POS, sw=2.6))
    f.append(poly([M(tx[i], rx[i]) for i in range(len(tx))], color=FIELD, sw=2.8))

    f.append(fitbox(px + 330, py + 8, 300, 46,
                    "наївний Ейлер: політ вкидає\n½·m·g²·dt² енергії на КОЖНОМУ кроці\n→ баланс повзе вгору на %.0f%%" % (drift * 100),
                    size=12, pad=7, fill="#fdecea", stroke=POS, sw=1.6, color=INK))
    f.append(fitbox(px + 120, y0 + 14, 360, 30,
                    "точна кінематика: нев'язка ≈ %.0e — машинний нуль" % exact_max,
                    size=12, pad=7, fill="#eef6ef", stroke=FIELD, sw=1.6, color=INK))

    f.append(swatch(200, 480, "#ffffff", FIELD, "точна кінематика (баланс тримається)"))
    f.append(swatch(560, 480, "#ffffff", POS, "наївний Ейлер (баланс повзе)"))
    return render(os.path.join(IMG, "integrator-residual.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_energy_trade(), fig_friction_ledger(), fig_time_symmetry(),
          fig_conservative_paths(), fig_work_as_area(), fig_birth_timeline(),
          fig_audit_trace(), fig_integrator_residual()]
    print("written:")
    for p in ps:
        print("  ", p)
