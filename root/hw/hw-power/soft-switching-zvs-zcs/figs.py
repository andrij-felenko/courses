# -*- coding: utf-8 -*-
"""Фігури до статті «М'яке перемикання: ZVS і ZCS». Чистий Python, svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

U_COL = POS      # напруга — гаряча
I_COL = NEG      # струм — холодний
P_COL = "#e67e22"  # добуток / спалах


# ── Фігура 1: жорстке / ZVS / ZCS — перекриття U·I ──────────────────────────
def fig_overlap():
    W, H = 780, 340
    panels = [
        ("Жорстке", "hard"),
        ("ZVS", "zvs"),
        ("ZCS", "zcs"),
    ]
    pw = 240          # ширина панелі
    gap = 20
    x0 = 20
    top = 60          # верх осей
    bot = 250         # низ осей (нульова лінія струму/напруги)
    frags = []
    for idx, (name, kind) in enumerate(panels):
        px = x0 + idx * (pw + gap)
        axx = px + 34             # вісь Y
        axr = px + pw - 12        # правий край осей
        # рамка панелі
        frags.append(rect(px, 46, pw, H - 66, fill="#ffffff", stroke=MUTED, sw=1.2))
        # осі
        frags.append(line(axx, top - 6, axx, bot, color=INK, sw=1.4))
        frags.append(line(axx, bot, axr, bot, color=INK, sw=1.4))
        frags.append(text(px + pw / 2, 66, name, size=15, bold=True))
        # часова сітка: перехід посередині
        tmid = (axx + axr) / 2
        hi = top + 8            # рівень «високо»
        lo = bot               # рівень «нуль»
        span = 26              # ширина фронту
        # --- напруга U (червона) і струм I (синя) як функції часу ---
        if kind == "hard":
            # U падає, I росте, обидва проходять середину одночасно → перекриття
            uxs = [(axx, hi), (tmid - span, hi), (tmid + span, lo), (axr, lo)]
            ixs = [(axx, lo), (tmid - span, lo), (tmid + span, hi), (axr, hi)]
            note = "U·I перекриваються"
        elif kind == "zvs":
            # напруга ВЖЕ впала до нуля лівіше переходу; струм наростає на нулі напруги
            uxs = [(axx, hi), (tmid - span - 30, hi), (tmid - span, lo), (axr, lo)]
            ixs = [(axx, lo), (tmid - 4, lo), (tmid + span + 20, hi), (axr, hi)]
            note = "U = 0 до вмикання"
        else:  # zcs
            # струм ВЖЕ впав до нуля лівіше переходу; напруга росте на нулі струму
            ixs = [(axx, hi), (tmid - span - 30, hi), (tmid - span, lo), (axr, lo)]
            uxs = [(axx, lo), (tmid - 4, lo), (tmid + span + 20, hi), (axr, hi)]
            note = "I = 0 до вимикання"

        def poly(pts, color):
            d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
            return '<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, color)
        frags.append(poly(uxs, U_COL))
        frags.append(poly(ixs, I_COL))

        # зона перекриття (спалах) — лише для жорсткого
        if kind == "hard":
            # трикутник спалаху навколо середини
            sp = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                  'fill="%s" opacity="0.30"/>' % (tmid - span, lo, tmid, hi - 14,
                                                  tmid + span, lo, P_COL))
            frags.append(sp)
            frags.append(text(tmid, hi - 20, "P", size=13, bold=True, color=P_COL))
        # підпис-нота під панеллю
        frags.append(text(px + pw / 2, bot + 26, note, size=12, color=MUTED))
        # осьові підписи U / I
        frags.append(text(axx - 6, top + 2, "U", size=12, color=U_COL, anchor="end", bold=True))
        frags.append(text(axx - 6, top + 20, "I", size=12, color=I_COL, anchor="end", bold=True))
        frags.append(text(axr, bot + 16, "t", size=12, color=MUTED))

    render(os.path.join(IMG, "zvs-zcs-overlap.svg"), W, H, *frags)


# ── Фігура 2: послідовність ZVS у мертвому часі напівмоста ──────────────────
def fig_zvs_dead_time():
    W, H = 760, 400
    frags = []
    # 4 кроки-картки
    steps = [
        ("1", "Верхній вимкнувся", "обидва ключі закриті\n(мертвий час)"),
        ("2", "Струм котушки тече", "перезаряджає Coss:\nодну заряджає, другу\nрозряджає"),
        ("3", "Напруга впала до 0", "нуль підхопив\nbody-діод"),
        ("4", "Канал відмикається", "вмикання на 0 В\n= ZVS"),
    ]
    cw, chh = 168, 150
    gx = 20
    x0 = 22
    cy = 110
    for i, (n, ttl, body) in enumerate(steps):
        cx = x0 + i * (cw + gx)
        # картка
        col = FIELD if n == "4" else INK
        frags.append(rect(cx, cy, cw, chh, fill=FILL, stroke=col,
                          sw=2 if n == "4" else 1.4))
        # номер-кружок
        frags.append(circle(cx + 22, cy + 22, 15, fill="#ffffff", stroke=col, sw=2))
        frags.append(text(cx + 22, cy + 27, n, size=15, bold=True, color=col))
        frags.append(text(cx + cw / 2 + 8, cy + 27, ttl, size=12.5, bold=True))
        frags.append(mtext(cx + cw / 2, cy + 58, body, size=11.5, color=MUTED, lh=1.25))
        # стрілка до наступної
        if i < 3:
            ax = cx + cw
            frags.append(arrow(ax + 2, cy + chh / 2, ax + gx - 2, cy + chh / 2, color=INK))

    # верхній заголовок сцени
    frags.append(text(W / 2, 40, "Напівміст: ZVS народжується в мертвому часі", size=15, bold=True))

    # нижня смуга: осцилограма напруги на майбутньому ключі
    oy_top = 300     # рівень «висока напруга»
    oy_bot = 366     # нуль
    ox0 = 60
    ox1 = W - 40
    frags.append(line(ox0, oy_bot, ox1, oy_bot, color=INK, sw=1.3))   # вісь t
    frags.append(line(ox0, oy_top - 8, ox0, oy_bot, color=INK, sw=1.3))  # вісь U
    frags.append(text(ox0 - 8, oy_top + 2, "U", size=12, color=U_COL, anchor="end", bold=True))
    frags.append(text(ox1, oy_bot + 16, "t", size=12, color=MUTED))
    # крива: висока → спад (мертвий час) → нуль-полиця → фронт вмикання
    xa = ox0 + 40
    xb = ox0 + 250      # початок спаду
    xc = ox0 + 380      # досяг нуля
    xd = ox1 - 60       # мить вмикання
    d = ("M %.1f %.1f L %.1f %.1f Q %.1f %.1f %.1f %.1f L %.1f %.1f"
         % (xa, oy_top, xb, oy_top, (xb + xc) / 2, oy_bot, xc, oy_bot, xd, oy_bot))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, U_COL))
    # позначка мертвого часу
    frags.append(line(xb, oy_top - 6, xb, oy_bot + 6, color=MUTED, sw=1, dash="4 3"))
    frags.append(line(xc, oy_top - 6, xc, oy_bot + 6, color=MUTED, sw=1, dash="4 3"))
    frags.append(text((xb + xc) / 2, oy_top - 12, "мертвий час", size=11, color=MUTED))
    # мить ZVS-вмикання
    frags.append(line(xd, oy_top - 6, xd, oy_bot + 6, color=FIELD, sw=1.4, dash="4 3"))
    frags.append(text(xd, oy_bot + 30, "вмикання на 0 В", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "zvs-dead-time.svg"), W, H, *frags)


# ── Фігура 3: ZCS — синусоїдний струм ключа, вимикання в нулі ────────────────
def fig_zcs_current():
    W, H = 700, 320
    frags = []
    frags.append(text(W / 2, 34, "ZCS: струм ключа — синусоїдний півперіод", size=15, bold=True))
    ox0 = 70
    ox1 = W - 40
    base = 250       # нульова лінія струму
    amp = 150        # висота піка
    frags.append(line(ox0, base, ox1, base, color=INK, sw=1.4))    # вісь t
    frags.append(line(ox0, base - amp - 20, ox0, base + 10, color=INK, sw=1.4))  # вісь I
    frags.append(text(ox0 - 8, base - amp - 6, "I", size=13, color=I_COL, anchor="end", bold=True))
    frags.append(text(ox1, base + 20, "t", size=12, color=MUTED))

    # для порівняння — блідий прямокутник (жорсткий струм)
    xr0 = ox0 + 60
    xr1 = ox1 - 60
    hlev = base - amp * 0.72
    frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5 4" opacity="0.55"/>'
                 % (xr0, base, xr0, hlev, xr1, hlev, xr1, base, xr1, base, xr1, base, MUTED))
    frags.append(text((xr0 + xr1) / 2, hlev - 8, "жорсткий (прямокутник)", size=11, color=MUTED))

    # синусоїдний півперіод струму від xr0 до xr1
    N = 80
    pts = []
    for k in range(N + 1):
        t = k / N
        x = xr0 + (xr1 - xr0) * t
        y = base - amp * math.sin(math.pi * t)
        pts.append((x, y))
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, I_COL))

    # точки вмикання (нуль зліва) і вимикання (нуль справа)
    frags.append(circle(xr0, base, 5, fill="#ffffff", stroke=FIELD, sw=2.4))
    frags.append(circle(xr1, base, 5, fill="#ffffff", stroke=FIELD, sw=2.4))
    frags.append(text(xr0, base + 22, "вмик.\n(I=0)", size=11, color=FIELD, bold=True))
    frags.append(mtext(xr1, base + 22, "вимик.\n(I=0)", size=11, color=FIELD, bold=True))
    # пік
    frags.append(text((xr0 + xr1) / 2, base - amp - 6, "пік", size=11, color=I_COL))

    render(os.path.join(IMG, "zcs-current.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_overlap()
    fig_zvs_dead_time()
    fig_zcs_current()
    print("figs done")
