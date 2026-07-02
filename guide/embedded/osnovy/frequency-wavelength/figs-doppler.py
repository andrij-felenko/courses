# -*- coding: utf-8 -*-
# Фігури для вставки math-doppler-shift.md (тема «Частота й довжина»).
# Окремий файл, щоб не чіпати основний figs.py теми.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Чому взагалі є зсув: нерухоме джерело vs рухоме ─────────────────────────
# Ідея (першопричина всієї теми): гребені виходять концентричними колами. Коли
# джерело їде, кожне наступне коло виходить із точки, зсунутої вперед → попереду
# кола тиснуться (коротша λ, вища f), позаду розходяться (довша λ, нижча f).
def fig_wavefronts():
    W, H = 860, 400
    parts = []
    parts.append(text(W/2, 28, "Гребені — концентричні кола. Рух джерела зсуває їхні центри", size=16, bold=True))

    # ліворуч: нерухоме джерело — кола з одного центру
    lx, ly = 215, 215
    parts.append(text(lx, 70, "джерело стоїть", size=13, bold=True, color=MUTED))
    for k in range(1, 5):
        r = 34 * k
        parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
                     % (lx, ly, r, INK))
    parts.append(circle(lx, ly, 5, fill=POS, stroke=POS))
    parts.append(mtext(lx, ly + 150, ["λ однакова з усіх боків", "→ f однакова скрізь"],
                       size=12, color=MUTED))

    # праворуч: рухоме джерело — центри зсунуті вправо
    rx0, ry = 560, 215
    parts.append(text(660, 70, "джерело їде →", size=13, bold=True, color=POS))
    # чотири гребені, кожен випущений з дедалі правішої точки; усі однакового «віку»-радіуса кроку
    centers = [rx0 + 0, rx0 + 26, rx0 + 52, rx0 + 78]   # найстаріший ліворуч
    radii   = [130, 98, 66, 34]                          # найстаріший найбільший
    for cx, r in zip(centers, radii):
        parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
                     % (cx, ry, r, INK))
    # поточне положення джерела — найправіший центр
    src_x = centers[-1]
    parts.append(circle(src_x, ry, 5, fill=POS, stroke=POS))
    parts.append(arrow(src_x + 10, ry, src_x + 44, ry, color=POS, sw=2.2))

    # підписи «попереду тиснуться» / «позаду розходяться»
    parts.append(text(src_x + 122, ry - 8, "попереду", size=12, bold=True, color=POS, anchor="middle"))
    parts.append(mtext(src_x + 122, ry + 10, ["коротша λ", "вища f"], size=11, color=POS))
    parts.append(text(centers[0] - 138, ry - 8, "позаду", size=12, bold=True, color=NEG, anchor="middle"))
    parts.append(mtext(centers[0] - 138, ry + 10, ["довша λ", "нижча f"], size=11, color=NEG))

    parts.append(fitbox(40, 348, 780, 42,
                        "Джерело не міняє швидкість хвилі — воно наздоганяє власні гребені:\nпопереду вони скупчуються, позаду відстають. Так рух стає зсувом частоти.",
                        size=12, fill="#eafaf0", stroke=FIELD))
    render(os.path.join(OUT, "doppler-wavefronts.svg"), W, H, *parts)


# ── 2. Дві різні причини для звуку: рухається джерело vs приймач ───────────────
# Ідея: у середовищі це ДВА різні механізми. Джерело рухається → фізично коротшає
# λ у повітрі. Приймач рухається → λ у повітрі та сама, але він налітає на гребені
# частіше. Тому формули різні (асиметрія), хоч на малих швидкостях майже збігаються.
def fig_two_mechanisms():
    W, H = 860, 420
    parts = []
    parts.append(text(W/2, 26, "У звуку — дві РІЗНІ причини зсуву (тому й формули різні)", size=16, bold=True))

    def crests(y, x0, x1, spacing, color):
        out = []
        x = x0
        while x <= x1:
            out.append(line(x, y - 20, x, y + 20, color=color, sw=2.2))
            x += spacing
        return out

    # A: джерело рухається (гребені в повітрі стиснуті попереду)
    ay = 130
    parts.append(text(60, ay - 55, "A. їде ДЖЕРЕЛО", size=13.5, bold=True, color=POS, anchor="start"))
    parts.append(text(60, ay - 37, "гребені в повітрі реально стиснуті", size=11.5, color=MUTED, anchor="start"))
    # нерівномірні: зліва (позаду) рідше, справа (попереду) густіше
    xs = [120, 175, 224, 267, 304, 336, 363, 386]
    for x in xs:
        parts.append(line(x, ay - 20, x, ay + 20, color=POS, sw=2.2))
    parts.append(circle(120, ay, 6, fill=POS, stroke=POS))
    parts.append(arrow(398, ay, 440, ay, color=POS, sw=2.2))
    parts.append(circle(690, ay, 9, fill=FILL, stroke=INK))     # нерухомий приймач-вухо
    parts.append(text(690, ay + 30, "приймач стоїть", size=11, color=MUTED))
    parts.append(text(300, ay - 20, "λ коротшає у повітрі", size=11, color=POS))
    parts.append(mtext(690, ay + 46, ["чує вищу f, бо в повітря", "прийшли коротші хвилі"],
                       size=11, color=POS))

    # B: приймач рухається (гребені рівномірні, приймач налітає)
    by = 300
    parts.append(text(60, by - 55, "B. їде ПРИЙМАЧ", size=13.5, bold=True, color=NEG, anchor="start"))
    parts.append(text(60, by - 37, "гребені рівномірні, приймач налітає на них частіше", size=11.5, color=MUTED, anchor="start"))
    parts.extend(crests(by, 150, 600, 55, NEG))
    parts.append(circle(120, by, 6, fill=NEG, stroke=NEG))
    parts.append(mtext(120, by + 34, ["джерело", "стоїть"], size=10.5, color=MUTED))
    parts.append(circle(690, by, 9, fill=FILL, stroke=INK))
    parts.append(arrow(680, by, 636, by, color=NEG, sw=2.4))    # рух приймача НАЗУСТРІЧ
    parts.append(mtext(700, by + 44, ["сам біжить назустріч —", "минає гребені частіше"],
                       size=11, color=NEG, anchor="middle"))
    parts.append(text(375, by - 26, "λ у повітрі НЕ змінилась", size=11, color=NEG))

    render(os.path.join(OUT, "doppler-two-mechanisms.svg"), W, H, *parts)


# ── 3. Класика проти релятивістики: лінійне наближення vs повний √ ─────────────
# Ідея: до β≈0.1 обидві криві й лінія Δf/f = v/c майже збігаються (тому в радіо
# беремо просту формулу). З ростом β релятивістська √-крива відривається вгору;
# з'являється поперечний зсув (β_радіальна=0, а зсув є) — суто релятивістський.
def fig_classic_vs_rel():
    W, H = 820, 440
    parts = []
    parts.append(text(W/2, 26, "Зсув частоти: проста лінія v/c vs повна релятивістська √", size=16, bold=True))

    # осі
    ox, oy = 110, 360         # початок координат
    ax, ay = 720, 60          # краї
    parts.append(line(ox, oy, ax, oy, color=INK, sw=1.6))   # X
    parts.append(line(ox, oy, ox, ay, color=INK, sw=1.6))   # Y
    parts.append(text((ox+ax)/2, oy + 40, "β = v / c  (частка швидкості світла)", size=12.5))
    parts.append(text(ox - 60, (oy+ay)/2, "f'/f", size=12.5, anchor="middle"))

    bmax = 0.6
    def X(b):  return ox + (b / bmax) * (ax - ox)
    fmin, fmax = 0.9, 2.2
    def Y(fr): return oy - (fr - fmin) / (fmax - fmin) * (oy - ay)

    # горизонталь f'/f = 1
    parts.append(line(ox, Y(1.0), ax, Y(1.0), color="#d7dbe0", sw=1, dash="4 3"))
    parts.append(text(ox - 10, Y(1.0) + 4, "1", size=11, anchor="end", color=MUTED))
    parts.append(text(ox - 10, Y(2.0) + 4, "2", size=11, anchor="end", color=MUTED))

    # точки для кривих (наближення на джерело: класика 1+β, релятивістика √((1+β)/(1-β)))
    def poly(fn, color, dash=None):
        pts = []
        b = 0.0
        while b <= bmax + 1e-9:
            pts.append("%.1f,%.1f" % (X(b), Y(fn(b))))
            b += 0.01
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"%s/>' % (" ".join(pts), color, d)

    parts.append(poly(lambda b: 1 + b, NEG))                              # проста лінія v/c
    parts.append(poly(lambda b: math.sqrt((1 + b) / (1 - b)), POS))      # повна релятивістська

    # підписи кривих
    parts.append(text(X(0.52), Y(1 + 0.52) + 18, "1 + β  (проста)", size=12, color=NEG, bold=True, anchor="middle"))
    parts.append(text(X(0.42), Y(math.sqrt(1.42/0.58)) - 12, "√((1+β)/(1−β))", size=12, color=POS, bold=True, anchor="middle"))
    parts.append(text(X(0.42), Y(math.sqrt(1.42/0.58)) + 6, "повна релятивістська", size=10.5, color=POS, anchor="middle"))

    # зона «радіо / повсякдення» — β до ~0.1
    parts.append(rect(X(0), ay + 6, X(0.05) - X(0), oy - ay - 6, fill="#eafaf0", stroke="none", rx=0, sw=0))
    parts.append(text(X(0.025), ay + 2, "тут майже", size=10, color=FIELD, anchor="middle"))
    parts.append(text(X(0.16), ay + 26, "радар, BLE, супутник: β ≪ 1 → криві злиті, беремо просту v/c",
                      size=11, color=FIELD, anchor="middle"))

    # позначка поперечного зсуву
    parts.append(fitbox(90, 396, 640, 40,
                        "Плюс суто релятивістський «поперечний» зсув: ціль летить упоперек (радіальна β = 0),\nа частота все одно падає — від сповільнення часу. У звуку такого немає.",
                        size=11, fill=FILL, stroke=LINE))
    render(os.path.join(OUT, "doppler-classic-vs-rel.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_wavefronts()
    fig_two_mechanisms()
    fig_classic_vs_rel()
    print("done:", sorted(f for f in os.listdir(OUT) if f.startswith("doppler-")))
