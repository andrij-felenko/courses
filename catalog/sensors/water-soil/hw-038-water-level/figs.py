# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «HW-038 — давач рівня води».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Устрій: дві гребінки доріжок + транзистор S8050 ─────────────────────────
def fig_inside():
    W, H = 940, 500
    f = []

    # --- гребінка доріжок (нижня частина плати, у воді) ---
    gx, gy, gw, gh = 70, 270, 300, 150          # рамка чутливої зони
    f.append(rect(gx, gy, gw, gh, fill="#eef3fb", stroke=NEG, sw=1.6, rx=8))
    f.append(text(gx + gw / 2, gy + gh + 30, "чутлива зона ≈ 40 × 16 мм", size=11, color=MUTED))

    # десять пальців: парні (0,2,4,6,8) — «живлення», непарні — «чуття»
    n = 10
    step = (gw - 40) / (n - 1)
    top_bus_y = gy + 24          # шина «живлення» вгорі
    bot_bus_y = gy + gh - 24     # шина «чуття» знизу
    for i in range(n):
        x = gx + 20 + i * step
        if i % 2 == 0:                       # палець від верхньої шини (VCC)
            f.append(line(x, top_bus_y, x, bot_bus_y - 18, color=POS, sw=3))
        else:                                # палець від нижньої шини (база)
            f.append(line(x, bot_bus_y, x, top_bus_y + 18, color=NEG, sw=3))
    # дві шини
    f.append(line(gx + 16, top_bus_y, gx + gw - 16, top_bus_y, color=POS, sw=3))
    f.append(line(gx + 16, bot_bus_y, gx + gw - 16, bot_bus_y, color=NEG, sw=3))
    # підписи гребінок — праворуч від рамки, поза пальцями
    f.append(text(gx + gw + 14, top_bus_y + 4, "5 доріжок → +живлення", size=10.5, color=POS, bold=True, anchor="start"))
    f.append(text(gx + gw + 14, bot_bus_y + 4, "5 доріжок → база", size=10.5, color=NEG, bold=True, anchor="start"))

    # рівень води (пунктир) — трохи нижче верху зони; підпис ВИНЕСЕНО над рамку, поза пальцями
    wl = gy + 40
    f.append(line(gx - 8, wl, gx + gw + 8, wl, color="#3aa6d0", sw=2, dash="7 5"))
    f.append(text(gx + gw / 2, gy - 12, "рівень води — саме вона замикає сусідні доріжки", size=10.5, color="#2a86a8", bold=True))

    # --- верхня частина плати: 100 Ом, транзистор, вихід ---
    # VCC зверху (ліворуч від лінії, щоб напис не лежав на дроті)
    vcc_x = 560
    f.append(text(vcc_x, 60, "+VCC (3–5 В)", size=12, bold=True, color=POS))
    f.append(line(vcc_x, 68, vcc_x, 108, color=POS, sw=2))
    # резистор 100 Ом на шині живлення
    r_b = textbox(vcc_x, 128, "R  100 Ом", size=12, color=POS, stroke=POS, min_w=110)
    f.append(r_b[0])
    f.append(text(vcc_x + 78, 128, "обмежувач струму", size=9.5, color=MUTED, anchor="start"))
    # від R до верхньої гребінки-шини (POS) — обходимо праворуч і згори
    f.append(line(vcc_x, 148, vcc_x, 224, color=POS, sw=2))
    f.append(line(vcc_x, 224, gx + gw - 40, 224, color=POS, sw=2))
    f.append(line(gx + gw - 40, 224, gx + gw - 40, top_bus_y, color=POS, sw=2))

    # транзистор S8050 (коробка з B/C/E)
    tx, ty, tw, th = 660, 280, 150, 110
    f.append(rect(tx, ty, tw, th, fill="#eef6ef", stroke=FIELD, sw=1.9, rx=10))
    f.append(text(tx + tw / 2, ty + 26, "S8050", size=13, bold=True, color=FIELD))
    f.append(text(tx + tw / 2, ty + 44, "NPN, підсилювач", size=9.5, color=MUTED))
    f.append(text(tx + 22, ty + 76, "B", size=11, bold=True, color=NEG))
    f.append(text(tx + tw - 20, ty + 64, "C", size=11, bold=True, color=INK))
    f.append(text(tx + tw - 20, ty + 98, "E", size=11, bold=True, color=INK))

    # база ← нижня шина «чуття» (веде до лівого краю коробки, нижче написів гребінки)
    f.append(line(gx + gw - 16, bot_bus_y + 6, tx, ty + 74, color=NEG, sw=2))
    f.append(text((gx + gw + tx) / 2 + 20, bot_bus_y + 44, "малий струм бази", size=9.5, color=NEG, anchor="start"))

    # колектор → OUT
    f.append(line(tx + tw, ty + 60, 872, ty + 60, color=INK, sw=2))
    f.append(text(880, ty + 56, "OUT", size=12, bold=True, color=INK, anchor="start"))
    f.append(text(880, ty + 74, "(аналог)", size=9.5, color=MUTED, anchor="start"))
    # емітер → GND
    f.append(line(tx + tw, ty + 94, 872, ty + 94, color=INK, sw=2))
    f.append(text(880, ty + 98, "GND", size=11, bold=True, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "hw038-inside.svg"), W, H, *f,
                  title="Устрій HW-038: дві гребінки доріжок → транзистор S8050 підсилює струм крізь воду")


# ── 2. Що на виході: глибина занурення → напруга ──────────────────────────────
def fig_curve():
    W, H = 820, 430
    f = []
    ox, oy = 130, 340        # початок осей
    aw, ah = 560, 250        # довжина осей

    # осі
    f.append(arrow(ox, oy, ox + aw + 20, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ah - 20, color=INK, sw=1.8))
    f.append(text(ox + aw / 2, oy + 46, "глибина занурення доріжок →", size=12, bold=True))
    f.append(text(ox - 96, oy - ah / 2, "показ АЦП", size=12, bold=True, anchor="middle"))
    f.append(text(ox - 96, oy - ah / 2 + 18, "(напруга OUT)", size=10, color=MUTED, anchor="middle"))

    # позначки на осі X
    f.append(text(ox, oy + 22, "0 (сухо)", size=10, color=MUTED))
    f.append(text(ox + aw, oy + 22, "повне", size=10, color=MUTED))
    # на осі Y
    f.append(text(ox - 18, oy + 4, "0", size=10, color=MUTED, anchor="end"))
    f.append(text(ox - 18, oy - ah + 6, "~max", size=10, color=MUTED, anchor="end"))

    # крива для «звичайної» води — насичена, монотонна (корінь-подібна)
    import math
    def curve(frac_max, tag, col, dash=None, xs=1.0):
        pts = []
        N = 40
        for k in range(N + 1):
            t = k / N
            v = frac_max * (t ** 0.62)       # спадна крутість — насичення
            px = ox + t * aw * xs
            py = oy - v * ah
            pts.append((px, py))
        d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"%s/>'
                 % (d, col, ' stroke-dasharray="7 5"' if dash else ''))
        lx, ly = pts[int(N * 0.82)]
        return lx, ly, tag, col

    l1 = curve(0.92, "провідна вода / вища VCC", NEG, None)
    l2 = curve(0.60, "чиста вода / нижча VCC", FIELD, True)

    for lx, ly, tag, col in (l1, l2):
        f.append(text(lx + 8, ly - 8, tag, size=10.5, color=col, bold=True, anchor="start"))

    # пояснення нелінійності
    box = fitbox(ox + 20, oy - ah - 6, 330, 54,
                 "Крива МОНОТОННА, але НЕ пряма й НЕ абсолютна:\n"
                 "її висота залежить від провідності води й VCC.",
                 size=10.5, stroke=MUTED, fill="#fbfbfc")
    f.append(box)

    return render(os.path.join(IMG, "hw038-curve.svg"), W, H, *f,
                  title="Вихід HW-038: більше занурено — вища напруга, але шкала «пливе» з водою й живленням")


# ── 3. Підключення пін-у-пін + живлення від цифрової ніжки проти корозії ───────
def fig_wiring():
    W, H = 900, 470
    f = []

    # МК ліворуч
    mx, my, mw, mh = 70, 120, 190, 250
    f.append(rect(mx, my, mw, mh, fill="#eef6ef", stroke=FIELD, sw=1.9, rx=12))
    f.append(text(mx + mw / 2, my + 28, "Мікроконтролер", size=13, bold=True, color=FIELD))
    pins = [("+5 В / 3.3 В", 70, POS),
            ("D7 (цифрова)", 120, POS),
            ("A0 (АЦП)", 178, NEG),
            ("GND", 224, MUTED)]
    for name, dy, col in pins:
        f.append(text(mx + mw - 14, my + dy, name, size=10.5, color=col, anchor="end", bold=True))
        f.append(circle(mx + mw, my + dy - 4, 4, fill=BG, stroke=col, sw=1.6))

    # HW-038 праворуч
    sx, sy, sw2, sh = 620, 150, 200, 190
    f.append(rect(sx, sy, sw2, sh, fill="#eef3fb", stroke=NEG, sw=1.9, rx=12))
    f.append(text(sx + sw2 / 2, sy + 28, "HW-038", size=14, bold=True, color=NEG))
    f.append(text(sx + sw2 / 2, sy + 46, "три ніжки: + / S / −", size=9.5, color=MUTED))
    spins = [("+  (VCC)", 84, POS),
             ("S  (OUT)", 128, NEG),
             ("−  (GND)", 172, MUTED)]
    for name, dy, col in spins:
        f.append(text(sx + 16, sy + dy, name, size=11, color=col, anchor="start", bold=True))
        f.append(circle(sx, sy + dy - 4, 4, fill=BG, stroke=col, sw=1.6))

    # дроти
    # S (OUT) → A0
    f.append(line(mx + mw, my + 174, sx, sy + 124, color=NEG, sw=2))
    # − → GND
    f.append(line(mx + mw, my + 220, sx, sy + 168, color=MUTED, sw=2))

    # + давача — ДВА варіанти живлення (обидва йдуть до ніжки «+» давача)
    # варіант А: прямо на +5 В (сірий пунктир, «простіше, але корозія») — верхня траса
    ax_v = 400
    f.append(line(mx + mw, my + 66, ax_v, my + 66, color=POS, sw=2, dash="6 5"))
    f.append(line(ax_v, my + 66, ax_v, sy + 80, color=POS, sw=2, dash="6 5"))
    f.append(line(ax_v, sy + 80, sx, sy + 80, color=POS, sw=2, dash="6 5"))
    # підпис — над трасою A, ліворуч, поза лініями
    f.append(text(mx + mw + 8, my + 52, "A) прямо на живлення:", size=10, color=POS, bold=True, anchor="start"))
    f.append(text(mx + mw + 8, my + 92, "просто, але доріжки роз'їдає", size=9.5, color=MUTED, anchor="start"))

    # варіант Б: від цифрової ніжки D7 (суцільний, «вмикай лише на час читання») — нижча траса
    bx_v = 470
    f.append(line(mx + mw, my + 116, bx_v, my + 116, color=FIELD, sw=2.4))
    f.append(line(bx_v, my + 116, bx_v, sy + 92, color=FIELD, sw=2.4))
    f.append(line(bx_v, sy + 92, sx, sy + 92, color=FIELD, sw=2.4))
    # підпис — під нижнім згином траси Б, у вільному місці праворуч від МК
    f.append(text(mx + mw + 8, my + 150, "Б) від D7 — вмикай лише", size=10, color=FIELD, bold=True, anchor="start"))
    f.append(text(mx + mw + 8, my + 166, "на мить виміру → менше корозії", size=9.5, color=FIELD, anchor="start"))

    # склянка з водою під давачем
    wx, wy, ww, wh = sx + 30, sy + sh + 6, 140, 70
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#eaf6fb" stroke="%s" stroke-width="1.6"/>'
             % (wx, wy, wx + ww, wy, wx + ww - 14, wy + wh, wx + 14, wy + wh, "#3aa6d0"))
    f.append(line(wx + 6, wy + 22, wx + ww - 6, wy + 22, color="#3aa6d0", sw=1.6, dash="6 4"))
    f.append(text(wx + ww / 2, wy + 46, "вода", size=11, color="#2a86a8", bold=True))
    # доріжки давача занурені
    f.append(line(sx + sw2 / 2 - 20, sy + sh, sx + sw2 / 2 - 20, wy + 40, color=NEG, sw=2))
    f.append(line(sx + sw2 / 2 + 20, sy + sh, sx + sw2 / 2 + 20, wy + 40, color=POS, sw=2))

    return render(os.path.join(IMG, "hw038-wiring.svg"), W, H, *f,
                  title="Підключення HW-038: S→АЦП, −→GND, а «+» краще від цифрової ніжки (вмикати лише на читання)")


# ── 4. Багатоточкове калібрування: одна пряма vs ламана ────────────────────────
def fig_calib():
    W, H = 820, 470
    f = []
    ox, oy = 130, 370       # початок осей
    aw, ah = 560, 270       # довжина осей

    # осі
    f.append(arrow(ox, oy, ox + aw + 20, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ah - 20, color=INK, sw=1.8))
    f.append(text(ox + aw / 2, oy + 44, "справжній рівень води →", size=12, bold=True))
    f.append(text(ox - 92, oy - ah / 2 - 6, "показ", size=12, bold=True, anchor="middle"))
    f.append(text(ox - 92, oy - ah / 2 + 12, "АЦП", size=12, bold=True, anchor="middle"))
    f.append(text(ox - 18, oy + 4, "0", size=10, color=MUTED, anchor="end"))
    f.append(text(ox, oy + 22, "сухо", size=10, color=MUTED))
    f.append(text(ox + aw, oy + 22, "повно", size=10, color=MUTED))

    # справжня вигнута крива відліку від рівня (насичується вгорі)
    def curve_y(t):
        return oy - (t ** 0.68) * ah        # спадна крутість — насичення

    pts = []
    N = 60
    for k in range(N + 1):
        t = k / N
        pts.append((ox + t * aw, curve_y(t)))
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d, NEG))
    # підпис кривої — біля її середини, над лінією, поза іншими написами
    mid = pts[int(N * 0.5)]
    f.append(text(mid[0] + 6, mid[1] - 14, "справжня крива давача", size=10.5, color=NEG, bold=True, anchor="start"))

    # одна пряма між крайніми точками (двоточкове) — сіра штрихова
    x0, y0 = pts[0]
    x1, y1 = pts[N]
    f.append(line(x0, y0, x1, y1, color=MUTED, sw=2, dash="8 5"))
    f.append(text(ox + aw * 0.30, curve_y(0.30) + 40, "двоточкова пряма —", size=10, color=MUTED, bold=True, anchor="start"))
    f.append(text(ox + aw * 0.30, curve_y(0.30) + 56, "посередині мажеться", size=10, color=MUTED, anchor="start"))

    # ламана по кількох калібрувальних точках — зелена, притискається до кривої
    fracs = [0.0, 0.25, 0.5, 0.75, 1.0]
    poly = [(ox + t * aw, curve_y(t)) for t in fracs]
    dp = "M " + " L ".join("%.1f %.1f" % p for p in poly)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (dp, FIELD))
    for px, py in poly:
        f.append(circle(px, py, 4.5, fill=BG, stroke=FIELD, sw=2))
    # підпис ламаної — унизу праворуч, у вільному полі під кривою
    f.append(text(ox + aw * 0.52, oy - 24, "ламана з кількох точок —", size=10.5, color=FIELD, bold=True, anchor="start"))
    f.append(text(ox + aw * 0.52, oy - 8, "притискається до кривої", size=10.5, color=FIELD, anchor="start"))

    return render(os.path.join(IMG, "hw038-calib.svg"), W, H, *f,
                  title="Багатоточкове калібрування: одна пряма мажеться, ламана повторює вигин")


# ── 5. Поріг помпи з гістерезисом: два пороги + мертва зона ────────────────────
def fig_hyst():
    W, H = 860, 460
    f = []
    ox, oy = 90, 330        # початок осей
    aw, ah = 690, 250

    # осі
    f.append(arrow(ox, oy, ox + aw + 16, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ah - 20, color=INK, sw=1.8))
    f.append(text(ox + aw / 2, oy + 40, "час →", size=12, bold=True))
    f.append(text(ox - 60, oy - ah / 2, "рівень", size=12, bold=True, anchor="middle"))

    # два пороги (горизонталі)
    y_on  = oy - ah * 0.72        # верхній: увімкнути помпу
    y_off = oy - ah * 0.44        # нижній: вимкнути помпу
    f.append(line(ox, y_on, ox + aw, y_on, color=POS, sw=1.8, dash="7 5"))
    f.append(line(ox, y_off, ox + aw, y_off, color=NEG, sw=1.8, dash="7 5"))

    # мертва зона між порогами — жовта заливка
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdf6d8" opacity="0.7"/>'
             % (ox, y_on, aw, y_off - y_on))
    f.append(text(ox + aw - 12, (y_on + y_off) / 2 + 4, "мертва зона: стан помпи не міняється",
                  size=10, color="#9a7d00", anchor="end", bold=True))

    # підписи порогів — ліворуч, поза кривою
    f.append(text(ox + 8, y_on - 8, "верхній поріг → УВІМКНУТИ", size=10.5, color=POS, bold=True, anchor="start"))
    f.append(text(ox + 8, y_off + 18, "нижній поріг → ВИМКНУТИ", size=10.5, color=NEG, bold=True, anchor="start"))

    # крива рівня, що повільно росте з дрібним тремтінням, топчучись у зоні
    import math
    pts = []
    N = 220
    for k in range(N + 1):
        t = k / N
        base = 0.20 + 0.62 * t                 # повільне наростання
        jitter = 0.02 * math.sin(t * 46) + 0.012 * math.sin(t * 113)
        v = base + jitter
        px = ox + t * aw
        py = oy - v * ah
        pts.append((px, py))
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, INK))
    f.append(text(pts[int(N * 0.12)][0], pts[int(N * 0.12)][1] - 12,
                  "рівень (тремтить)", size=10, color=INK, anchor="start"))

    return render(os.path.join(IMG, "hw038-hyst.svg"), W, H, *f,
                  title="Поріг помпи з гістерезисом: два пороги й мертва зона між ними")


if __name__ == "__main__":
    fig_inside()
    fig_curve()
    fig_wiring()
    fig_calib()
    fig_hyst()
    print("OK: 5 SVG у ./img/")
