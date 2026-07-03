# -*- coding: utf-8 -*-
# Фігури для вставки math-area-ratio.md (площинне відношення трафарету).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: переріз апертури — дно L·W проти стінок 2(L+W)T ────────────────
def fig_aperture_balance():
    W, H = 780, 430
    frags = []
    frags.append(text(W / 2, 34, "Дві поверхні, за які тримається паста в апертурі",
                      size=16, bold=True))

    # ── Ліва панель: прямостінна апертура, переріз ──
    cx = 210
    top = 90
    depth = 150          # висота стінки на малюнку = товщина T
    half = 95            # піввікна (ширина = 2·half)
    # трафарет (сірі блоки з боків)
    frags.append(rect(cx - half - 70, top, 70, depth, fill="#d9dee5", stroke=MUTED, sw=1.4, rx=2))
    frags.append(rect(cx + half, top, 70, depth, fill="#d9dee5", stroke=MUTED, sw=1.4, rx=2))
    # плата під трафаретом
    frags.append(rect(cx - half - 70, top + depth, 2 * half + 140, 26, fill="#efe7d0", stroke=MUTED, sw=1.4, rx=2))
    # мідна площадка (дно) — жирна лінія знизу вікна
    frags.append(line(cx - half, top + depth, cx + half, top + depth, color=POS, sw=6))
    # паста-цеглинка (напівпрозорий блок у вікні)
    frags.append(rect(cx - half, top, 2 * half, depth, fill="#eef2f7", stroke="#b8c1cc", sw=1.2, rx=2))
    # стінки — сині жирні вертикалі
    frags.append(line(cx - half, top, cx - half, top + depth, color=NEG, sw=5))
    frags.append(line(cx + half, top, cx + half, top + depth, color=NEG, sw=5))
    # позначки
    frags.append(text(cx, top + depth / 2, "паста", size=13, color=MUTED))
    frags.append(text(cx, top - 12, "прямі стінки", size=12, color=MUTED))
    # підпис дна
    frags.append(text(cx, top + depth + 55, "дно = L · W", size=14, color=POS, bold=True))
    frags.append(text(cx, top + depth + 74, "(мідна площадка)", size=11, color=MUTED))
    # підпис стінки + стрілка глибини T
    frags.append(text(cx - half - 96, top + depth / 2 - 8, "стінка", size=12, color=NEG, bold=True, anchor="end"))
    frags.append(text(cx - half - 96, top + depth / 2 + 9, "= (L+W)·T", size=12, color=NEG, anchor="end"))
    # стрілка глибини праворуч
    tx = cx + half + 96
    frags.append(line(tx, top, tx, top + depth, color=INK, sw=1.2))
    frags.append(line(tx - 5, top, tx + 5, top, color=INK, sw=1.2))
    frags.append(line(tx - 5, top + depth, tx + 5, top + depth, color=INK, sw=1.2))
    frags.append(text(tx + 8, top + depth / 2 + 4, "T", size=14, color=INK, bold=True, anchor="start"))

    # ── Права панель: трапецієподібна апертура (ширша знизу) ──
    cx2 = 585
    ht = 95              # піввікна ЗВЕРХУ
    hb = 122             # піввікна ЗНИЗУ (ширше)
    frags.append(rect(cx2 - hb - 62, top, 62 + (hb - ht), depth, fill="#d9dee5", stroke=MUTED, sw=1.4, rx=2))  # ліворуч заглушка (наближено прямокутником)
    # намалюємо трапецію-порожнечу через polygon стінок:
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#eef2f7" stroke="#b8c1cc" stroke-width="1.2"/>' % (
        cx2 - ht, top, cx2 + ht, top, cx2 + hb, top + depth, cx2 - hb, top + depth))
    # трафарет двома трапеціями обабіч
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#d9dee5" stroke="%s" stroke-width="1.4"/>' % (
        cx2 - ht - 70, top, cx2 - ht, top, cx2 - hb, top + depth, cx2 - hb - 70, top + depth, MUTED))
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#d9dee5" stroke="%s" stroke-width="1.4"/>' % (
        cx2 + ht, top, cx2 + ht + 70, top, cx2 + hb + 70, top + depth, cx2 + hb, top + depth, MUTED))
    # плата
    frags.append(rect(cx2 - hb - 70, top + depth, 2 * hb + 140, 26, fill="#efe7d0", stroke=MUTED, sw=1.4, rx=2))
    # дно ширше — жирна червона лінія
    frags.append(line(cx2 - hb, top + depth, cx2 + hb, top + depth, color=POS, sw=6))
    # похилі стінки сині
    frags.append(line(cx2 - ht, top, cx2 - hb, top + depth, color=NEG, sw=5))
    frags.append(line(cx2 + ht, top, cx2 + hb, top + depth, color=NEG, sw=5))
    frags.append(text(cx2, top + depth / 2, "паста", size=13, color=MUTED))
    frags.append(text(cx2, top - 12, "трапеція: ширша знизу", size=12, color=FIELD, bold=True))
    frags.append(text(cx2, top + depth + 55, "паста відходить від стінки одразу", size=12, color=FIELD))
    frags.append(text(cx2, top + depth + 73, "+10…15 % до перенесення", size=12, color=FIELD, bold=True))

    # ── Нижня рамка з умовою ──
    body, bw, bh = textbox(W / 2, 400,
        "AR = дно / стінки = L·W / (2·(L+W)·T)     AR > 1 → лишиться на платі",
        size=14, bold=True, fill="#f4f6f8", stroke=INK, sw=1.6, pad=12)
    frags.append(body)

    render(os.path.join(OUT, 'aperture-area-ratio.svg'), W, H, *frags)


# ── Фігура 2: крива ефективності перенесення з порогами 0.66 і 0.58 ─────────
def fig_te_curve():
    W, H = 720, 440
    frags = []
    frags.append(text(W / 2, 34, "Ефективність перенесення падає нижче порога площинного відношення",
                      size=15, bold=True))

    # осі
    ox, oy = 100, 350          # початок координат (лівий низ)
    axw, axh = 540, 260        # довжина осей
    frags.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))      # X
    frags.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))      # Y
    frags.append(text(ox + axw / 2, oy + 52, "площинне відношення AR", size=13, bold=True))
    # Y-підпис вертикально
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" font-weight="700" fill="%s" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">%s</text>' % (
        34, oy - axh / 2, FONT, INK, 34, oy - axh / 2, esc("ефективність перенесення TE, %")))

    # межі даних: AR 0.30…1.00 по X; TE 0…100 по Y
    ar0, ar1 = 0.30, 1.00
    def X(ar): return ox + (ar - ar0) / (ar1 - ar0) * axw
    def Y(te): return oy - te / 100.0 * axh

    # сітка + підписи X
    for ar in [0.40, 0.50, 0.58, 0.66, 0.75, 0.90, 1.00]:
        frags.append(line(X(ar), oy, X(ar), oy + 5, color=INK, sw=1.2))
        frags.append(text(X(ar), oy + 20, ("%.2f" % ar).rstrip('0').rstrip('.') if ar not in (0.58, 0.66) else "%.2f" % ar, size=11, color=INK))
    # підписи Y (без горизонтальної сітки — щоб лінії не різали виноски порогів)
    for te in [0, 25, 50, 75, 90, 100]:
        frags.append(line(ox - 5, Y(te), ox, Y(te), color=INK, sw=1.2))
        frags.append(text(ox - 12, Y(te) + 4, str(te), size=11, color=INK, anchor="end"))

    # крива TE(AR): плато вгорі, коліно, крутий спад униз (сигмоїда-подібна)
    import math
    pts = []
    a = ar0
    while a <= ar1 + 1e-6:
        # логістична: центр ~0.62, крутизна велика; верх ~97%
        te = 5 + 92 / (1 + math.exp(-22 * (a - 0.62)))
        pts.append((X(a), Y(te)))
        a += 0.01
    path = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path, INK))

    # пороги 0.58 (Type 4/5) і 0.66 (Type 3) — вертикальні пунктири
    frags.append(line(X(0.58), oy, X(0.58), Y(70), color=FIELD, sw=1.8, dash="5,4"))
    frags.append(line(X(0.66), oy, X(0.66), Y(80), color=POS, sw=1.8, dash="5,4"))
    # виноски порогів (рознесені, щоб не накладались)
    b1, w1, h1 = textbox(X(0.58) - 4, Y(70) - 42, "0.58\nType 4/5", size=12, bold=True,
                         fill="#eafaf0", stroke=FIELD, sw=1.5, pad=8)
    frags.append(b1)
    b2, w2, h2 = textbox(X(0.66) + 66, Y(80) - 30, "0.66\nType 3 (IPC)", size=12, bold=True,
                         fill="#fdecea", stroke=POS, sw=1.5, pad=8)
    frags.append(b2)

    # зони: «стабільно» праворуч, «мало й розкидано» ліворуч від коліна
    frags.append(text(X(0.85), Y(60), "плато: 90…100 %", size=12, color=MUTED))
    frags.append(text(X(0.85), Y(48), "стабільно", size=12, color=MUTED))
    frags.append(text(X(0.44), Y(30), "мало пасти", size=12, color=MUTED, anchor="start"))
    frags.append(text(X(0.44), Y(18), "і великий розкид", size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'transfer-efficiency-curve.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_aperture_balance()
    fig_te_curve()
    print("ok: aperture-area-ratio.svg, transfer-efficiency-curve.svg")
