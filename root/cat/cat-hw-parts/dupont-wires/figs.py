# -*- coding: utf-8 -*-
"""Фігури до статті «Dupont дроти (M-M/M-F/F-F)». Вивід — ./img/*.svg.
Запуск: python figs.py  (швидко, без залежностей)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

METAL = "#9aa3ad"      # блискучий контакт
METAL_D = "#6b7480"    # темніший метал (тінь/край)
PLAS_M = "#c0392b"     # корпус male (умовно теплий)
PLAS_F = "#2457d6"     # корпус female (умовно холодний)
WIREA = "#c0392b"
WIREB = "#27ae60"
WIREC = "#2457d6"


# ── Фігура 1: три різновиди — M-M, M-F, F-F ────────────────────────────────
def fig_types():
    W, H = 760, 430
    p = []

    def male_end(x, y, facing=+1):
        """Штир (male): плаский чорний корпус + металевий шпеник, що ВИСТУПАЄ.
        facing=+1 — шпеник дивиться праворуч, -1 — ліворуч."""
        bw, bh = 34, 26                       # корпус
        bx = x if facing > 0 else x - bw
        s = [rect(bx, y - bh/2, bw, bh, fill="#3a3f45", stroke="#23262a", sw=1.4, rx=4)]
        # металевий штир
        pinlen = 26
        px = (bx + bw) if facing > 0 else bx
        s.append(rect(px, y - 3, pinlen*facing if facing>0 else -0, 6,
                      fill=METAL, stroke=METAL_D, sw=1) if facing>0 else
                 rect(px - pinlen, y - 3, pinlen, 6, fill=METAL, stroke=METAL_D, sw=1))
        # кінчик штиря
        tipx = px + pinlen*facing
        s.append(rect(tipx - (3 if facing>0 else 0), y - 4, 3, 8, fill=METAL_D, stroke=METAL_D, sw=1))
        return "".join(s), (tipx)

    def female_end(x, y, facing=+1):
        """Гніздо (female): корпус із заглибленою металевою втулкою — отвір під штир.
        facing — з якого боку отвір."""
        bw, bh = 34, 30
        bx = x if facing > 0 else x - bw
        s = [rect(bx, y - bh/2, bw, bh, fill="#3a3f45", stroke="#23262a", sw=1.4, rx=4)]
        # металева втулка всередині, видно торець-отвір
        holex = (bx + bw - 12) if facing > 0 else bx
        s.append(rect(holex, y - 7, 12, 14, fill="#20242a", stroke=METAL_D, sw=1.4, rx=2))
        s.append(circle(holex + 6, y, 4.5, fill="#0d0f12", stroke=METAL, sw=1.6))
        mouthx = (bx + bw) if facing > 0 else bx
        return "".join(s), mouthx

    def wire(x1, x2, y, color):
        return rect(min(x1,x2), y - 3.5, abs(x2-x1), 7, fill=color, stroke=None, sw=0, rx=3)

    rows = [
        ("M–M", "штир",  "штир",  WIREA, "male",  "male"),
        ("M–F", "штир",  "гніздо", WIREB, "male",  "female"),
        ("F–F", "гніздо", "гніздо", WIREC, "female","female"),
    ]
    top = 92
    gap = 108
    lx, rx = 250, 510            # де стоять ліві/праві кінці
    for i, (lbl, ln_l, ln_r, col, kl, kr) in enumerate(rows):
        y = top + i*gap
        # мітка різновиду ліворуч
        b, _, _ = textbox(70, y, lbl, size=22, bold=True, pad=12,
                          fill="#f4f6f8", stroke=col, sw=2.4)
        p.append(b)
        # лівий кінець (дивиться праворуч, до дроту)
        if kl == "male":
            seg, ledge = male_end(lx, y, facing=-1)   # штир дивиться ліворуч (від дроту)
        else:
            seg, ledge = female_end(lx, y, facing=-1)
        p.append(seg)
        # правий кінець (дивиться праворуч, від дроту)
        if kr == "male":
            seg, redge = male_end(rx, y, facing=+1)
        else:
            seg, redge = female_end(rx, y, facing=+1)
        p.append(seg)
        # дріт між внутрішніми краями корпусів
        p.append(wire(lx, rx, y, col))
        # підписи кінців (над кінцями, з запасом, поза дротом)
        p.append(text(lx - 6, y - 26, ln_l, size=13, color=MUTED, anchor="middle"))
        p.append(text(rx + 6, y - 26, ln_r, size=13, color=MUTED, anchor="middle"))

    # легенда знизу — компактні пояснення символів, рознесені
    ly = H - 34
    seg, _ = male_end(150, ly, facing=+1)
    p.append(seg)
    p.append(text(232, ly + 5, "штир (male) — метал виступає", size=12.5, color=INK, anchor="start"))
    seg, _ = female_end(470, ly, facing=+1)
    p.append(seg)
    p.append(text(552, ly + 5, "гніздо (female) — отвір під штир", size=12.5, color=INK, anchor="start"))

    render(os.path.join(OUT, 'types.svg'), W, H, *p)


# ── Фігура 2: як влаштований кінець — дріт → контакт → корпус ──────────────
def fig_anatomy():
    W, H = 720, 400
    p = []

    # 1) стрічка-дріт зі жилками
    y0 = 90
    p.append(text(120, y0 - 34, "1. Багатожильний дріт", size=13.5, bold=True, anchor="middle"))
    # ізоляція
    p.append(rect(40, y0 - 12, 120, 24, fill=WIREB, stroke="#1e7a44", sw=1.2, rx=6))
    # оголені жилки
    for k in range(5):
        yy = y0 - 8 + k*4
        p.append(line(160, yy, 205, yy, color=METAL_D, sw=1.4))

    # 2) обтиснутий контакт (crimp)
    xc = 300
    p.append(text(xc + 40, y0 - 34, "2. Обтиснутий контакт", size=13.5, bold=True, anchor="middle"))
    # тіло контакту
    p.append(rect(xc, y0 - 14, 130, 28, fill=METAL, stroke=METAL_D, sw=1.6, rx=4))
    # лапки-обтиск (дві пари) — умовно
    for lapx in (xc + 18, xc + 34):
        p.append(line(lapx, y0 - 14, lapx - 6, y0 - 22, color=METAL_D, sw=2))
        p.append(line(lapx, y0 - 14, lapx - 6, y0 + 22, color=METAL_D, sw=2))
    for lapx in (xc + 96, xc + 112):
        p.append(line(lapx, y0 - 14, lapx + 6, y0 - 22, color=METAL_D, sw=2))
        p.append(line(lapx, y0 - 14, lapx + 6, y0 + 22, color=METAL_D, sw=2))
    p.append(text(xc + 65, y0 + 42, "дві пари лапок: на жилки й на ізоляцію",
                  size=11, color=MUTED, anchor="middle"))

    # 3) корпус, у який контакт засувається й клацає
    xh = 520
    p.append(text(xh + 70, y0 - 34, "3. Пластиковий корпус", size=13.5, bold=True, anchor="middle"))
    p.append(rect(xh, y0 - 22, 150, 44, fill="#3a3f45", stroke="#23262a", sw=1.6, rx=6))
    # гнізда-канали
    for k in range(3):
        yy = y0 - 12 + k*12
        p.append(rect(xh + 8, yy - 4, 134, 8, fill="#23262a", stroke="#4a4f55", sw=1, rx=2))
    p.append(text(xh + 75, y0 + 42, "контакт клацає фіксатором", size=11, color=MUTED, anchor="middle"))

    # стрілки потоку
    p.append(arrow(210, y0, 292, y0, color=INK, sw=2))
    p.append(arrow(438, y0, 512, y0, color=INK, sw=2))

    # ── нижній ряд: male-контакт vs female-контакт (торець) ──────────────
    yb = 260
    p.append(line(30, yb - 34, W - 30, yb - 34, color="#e0e0e0", sw=1))
    p.append(text(W/2, yb - 12, "Той самий корпус — але метал усередині різний", size=13.5, bold=True, anchor="middle"))

    # male: суцільний штир, що стирчить
    mx = 190
    p.append(rect(mx - 40, yb + 30, 60, 34, fill="#3a3f45", stroke="#23262a", sw=1.4, rx=5))
    p.append(rect(mx + 20, yb + 43, 60, 8, fill=METAL, stroke=METAL_D, sw=1.2, rx=2))
    b, _, _ = textbox(mx, yb + 96, "male: суцільний штир стирчить\nвстромляється в гніздо",
                     size=11.5, pad=8, fill="#fdecea", stroke=PLAS_M, sw=1.6)
    p.append(b)

    # female: пружинна вилка всередині гнізда обхоплює штир
    fx = 520
    p.append(rect(fx - 40, yb + 30, 60, 34, fill="#3a3f45", stroke="#23262a", sw=1.4, rx=5))
    # дві пружинні щоки
    p.append(line(fx + 20, yb + 40, fx + 64, yb + 45, color=METAL, sw=3))
    p.append(line(fx + 20, yb + 54, fx + 64, yb + 49, color=METAL, sw=3))
    # штир, що заходить між ними (умовно, тонкий)
    p.append(rect(fx + 40, yb + 45.5, 40, 3, fill=METAL_D, stroke=None, sw=0, rx=1))
    b, _, _ = textbox(fx, yb + 96, "female: пружинні щоки всередині\nобхоплюють штир — тому й зношуються",
                     size=11.5, pad=8, fill="#eaf0fd", stroke=PLAS_F, sw=1.6)
    p.append(b)

    render(os.path.join(OUT, 'anatomy.svg'), W, H, *p)


# ── Фігура 3: хто володів контактом і як розійшлися дві назви ──────────────
def fig_owners():
    """Стрічка часу власників (Berg → du Pont → Berg знову → FCI → Amphenol)
    і паралельна нитка НАЗВ: справжня марка Mini-PV проти прижилого «DuPont».
    Мета — показати, що нікнейм застряг рівно на добі du Pont-оснастки."""
    W, H = 900, 470
    p = []

    # горизонтальна вісь часу
    axis_y = 150
    x0, x1 = 70, W - 40
    p.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.2))
    # роки, рівномірно рознесені під ключові події (позиція — не масштаб, а порядок)
    events = [
        (1950, "Berg\nElectronics", "Квентін Берг\nзасновує фірму", FIELD),
        (1972, "du Pont", "купує Berg —\nназва на оснастці", POS),
        (1993, "Berg знову", "Hicks, Muse\nвикуповують", "#7a5cd6"),
        (1998, "FCI", "Framatome\nConnectors Intl.", "#0f8a8a"),
        (2016, "Amphenol", "нинішній\nвласник Mini-PV", NEG),
    ]
    n = len(events)
    span = x1 - x0 - 60
    xs = [x0 + 40 + span * i / (n - 1) for i in range(n)]

    for (yr, who, note, col), x in zip(events, xs):
        p.append(circle(x, axis_y, 8, fill=col, stroke=INK, sw=1.6))
        # рік — над віссю
        p.append(text(x, axis_y - 20, str(yr), size=15, bold=True, color=INK))
        # хто (власник) — рамка над роком
        b, bw, bh = textbox(x, axis_y - 66, who, size=12.5, bold=True, pad=8,
                            fill="#f4f6f8", stroke=col, sw=2)
        p.append(b)
        # пояснення — під віссю
        p.append(mtext(x, axis_y + 34, note, size=11, color=MUTED))

    # ── нижня нитка: дві назви розходяться ───────────────────────────────────
    ny = 340
    p.append(line(x0, ny - 24, x1, ny - 24, color="#e0e0e0", sw=1))
    p.append(text(W/2, ny - 4, "Дві назви одного контакту", size=14, bold=True))

    # справжня марка
    b, bw, bh = textbox(255, ny + 60, "Mini-PV™\nсправжня марка Berg", size=13, bold=True,
                       pad=12, fill="#eaf7ef", stroke=FIELD, sw=2.2)
    p.append(b)
    p.append(mtext(255, ny + 108, "берилієва бронза, пружні щоки,\nсотні втиків без утоми",
                   size=10.5, color=MUTED))

    # прижилий нікнейм
    b, bw, bh = textbox(645, ny + 60, "«DuPont»\nприжилий нікнейм", size=13, bold=True,
                       pad=12, fill="#fdecea", stroke=POS, sw=2.2)
    p.append(b)
    p.append(mtext(645, ny + 108, "з напису du Pont на оснастці 70–80-х;\nдешеві копії-перемички носять це ім'я",
                   size=10.5, color=MUTED))

    # стрілка «звідки взявся нікнейм» — від вузла du Pont вниз до правої рамки
    p.append(arrow(xs[1], axis_y + 60, 645, ny + 30, color=POS, sw=1.8))

    render(os.path.join(OUT, 'owners.svg'), W, H, *p)


if __name__ == '__main__':
    fig_types()
    fig_anatomy()
    fig_owners()
    print("OK: types.svg, anatomy.svg, owners.svg")
