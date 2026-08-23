# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── timeline: еволюція швидкості й рік за роком, з головним нововведенням ──────
# Ідея: не сухий список, а зростання пікової швидкості — і поряд видно, ЯКА ідея
# дала стрибок (OFDM, MIMO, ширші канали, OFDMA, MLO). Шкала швидкості — лог.

def fig_timeline():
    W, H = 940, 470
    p = []

    x0, y0 = 90, 380          # початок осей
    xw, yh = 800, 300         # довжина осей

    # вузли: (підпис, покоління, рік, пікова Мбіт/с, головна ідея)
    nodes = [
        ("b",  "",        "1999", 11,    "DSSS/CCK"),
        ("g",  "",        "2003", 54,    "OFDM на 2.4"),
        ("n",  "Wi-Fi 4", "2009", 600,   "MIMO + 40 МГц"),
        ("ac", "Wi-Fi 5", "2013", 6933,  "256-QAM + 160 МГц"),
        ("ax", "Wi-Fi 6", "2019", 9608,  "OFDMA + 1024-QAM"),
        ("be", "Wi-Fi 7", "2024", 23059, "320 МГц + 4096-QAM + MLO"),
    ]

    import math
    lo, hi = math.log10(10), math.log10(30000)
    def sy(v):
        return y0 - (math.log10(v) - lo) / (hi - lo) * yh
    # рік -> x рівномірно за позицією (не за календарем — щоб не тіснилося)
    xs = [x0 + 40 + i * (xw - 60) / (len(nodes) - 1) for i in range(len(nodes))]

    # горизонтальні рівні-орієнтири швидкості
    for v, lab in [(10, "10 Мбіт/с"), (100, "100"), (1000, "1 Гбіт/с"),
                   (10000, "10"), (30000, "30")]:
        yy = sy(v)
        p.append(line(x0, yy, x0 + xw, yy, color="#e3e6ec", sw=1))
        p.append(text(x0 - 8, yy + 4, lab, size=9, color=MUTED, anchor="end"))

    # осі
    p.append(line(x0, y0, x0 + xw, y0, color=INK, sw=1.8))
    p.append(text(x0 + xw, y0 + 22, "рік стандарту →", size=10, color=MUTED, anchor="end"))
    p.append(text(x0 - 8, sy(30000) - 14, "пікова швидкість (лог)", size=10,
                  color=MUTED, anchor="start"))

    # крива зростання
    pts = " ".join("%.1f,%.1f" % (xs[i], sy(nodes[i][3])) for i in range(len(nodes)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (pts, FIELD))

    # вузли
    for i, (lab, gen, yr, v, idea) in enumerate(nodes):
        xx, yy = xs[i], sy(nodes[i][3])
        p.append(circle(xx, yy, 6, fill="#ffffff", stroke=FIELD, sw=2.4))
        # підпис стандарту над точкою
        p.append(text(xx, yy - 26, "802.11" + lab, size=12, color=INK, bold=True))
        if gen:
            p.append(text(xx, yy - 12, gen, size=10, color=FIELD, bold=True))
        # рік під віссю
        p.append(text(xx, y0 + 22, yr, size=10, color=MUTED))
        # головна ідея — похилою колонкою під роком
        p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="9" fill="%s" '
                 'text-anchor="end" transform="rotate(-32 %.1f %.1f)">%s</text>'
                 % (xx + 4, y0 + 40, FONT, INK, xx + 4, y0 + 40, esc(idea)))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Шлях 802.11: кожен стрибок швидкості — нова ідея в PHY")


# ── three-knobs: три ручки, що ПЕРЕМНОЖУЮТЬСЯ у пікову швидкість ───────────────
# Ідея: швидкість росте не магією, а добутком трьох незалежних множників —
# ширша смуга × більше потоків MIMO × щільніша QAM. Показати як добуток.

def fig_three_knobs():
    W, H = 920, 430
    p = []

    cols = [
        ("ширша смуга", "20 → 320 МГц", "більше герців —\nбільше символів за час",
         "#eef6ef", FIELD),
        ("більше потоків", "1 → 8 (MIMO)", "кілька незалежних\nпросторових каналів",
         "#e9eefb", NEG),
        ("щільніша QAM", "BPSK → 4096-QAM", "більше бітів\nу кожному символі",
         "#fdf0e6", "#c07a2e"),
    ]
    bw, bh = 230, 150
    xs = [50, 50 + 260, 50 + 520]
    cy = 130
    for i, (title, rng, sub, fill, stroke) in enumerate(cols):
        x = xs[i]
        p.append(rect(x, cy, bw, bh, fill=fill, stroke=stroke, sw=2, rx=10))
        p.append(text(x + bw / 2, cy + 30, title, size=14, color=stroke, bold=True))
        p.append(text(x + bw / 2, cy + 56, rng, size=13, color=INK, bold=True))
        p.append(mtext(x + bw / 2, cy + 86, sub, size=10.5, color=MUTED, lh=1.25))
        if i < 2:
            p.append(text(x + bw + 13, cy + bh / 2 + 8, "×", size=30, color=INK, bold=True))

    # знак рівності й результат
    p.append(text(W / 2, cy + bh + 52, "= пікова швидкість лінка", size=15,
                  color=INK, bold=True))
    p.append(mtext(W / 2, cy + bh + 80,
                   "кожне покоління крутить ці самі три ручки далі;\n"
                   "усі три множники незалежні — тому й перемножуються",
                   size=11, color=MUTED, lh=1.3))

    render(os.path.join(OUT, "three-knobs.svg"), W, H, *p,
           title="Звідки беруться гігабіти: три ручки, що перемножуються")


# ── ofdma: OFDM (один за раз) проти OFDMA (канал ділять кілька) ────────────────
# Ідея головного нововведення Wi-Fi 6: замість «весь канал одному пакету на черзі»
# — нарізати канал на ресурсні блоки й віддати кільком пристроям одночасно.

def fig_ofdma():
    W, H = 940, 430
    p = []

    # ── ліворуч: OFDM — по черзі, увесь канал одному ──
    lx, ly, lw, lh = 60, 90, 360, 260
    p.append(text(lx + lw / 2, ly - 16, "OFDM (до Wi-Fi 6): по черзі", size=13,
                  color=MUTED, bold=True))
    p.append(rect(lx, ly, lw, lh, fill="#fafbfc", stroke=MUTED, sw=1.4, rx=8))
    p.append(text(lx - 8, ly + lh / 2, "канал", size=10, color=MUTED, anchor="end"))
    p.append(text(lx + lw / 2, ly + lh + 22, "час →", size=10, color=MUTED))
    # три часові слоти, кожен — весь канал одному пристрою
    slot_w = lw / 3.0
    devc = ["#cfe6d4", "#cdd7f3", "#f6dcc4"]
    devn = ["A", "B", "C"]
    for i in range(3):
        sx = lx + i * slot_w + 4
        p.append(rect(sx, ly + 8, slot_w - 8, lh - 16, fill=devc[i],
                      stroke="#9aa3b2", sw=1, rx=4))
        p.append(text(sx + (slot_w - 8) / 2, ly + lh / 2 + 6, devn[i],
                      size=20, color=INK, bold=True))
    p.append(text(lx + lw / 2, ly + lh + 40,
                  "малий пакет однаково займає весь канал", size=10,
                  color=POS, italic=True))

    # ── праворуч: OFDMA — один слот, канал поділено між кількома ──
    rx_, ry, rw, rh = 520, 90, 360, 260
    p.append(text(rx_ + rw / 2, ry - 16, "OFDMA (Wi-Fi 6): одночасно", size=13,
                  color=FIELD, bold=True))
    p.append(rect(rx_, ry, rw, rh, fill="#fafbfc", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(rx_ - 8, ry + rh / 2, "канал", size=10, color=MUTED, anchor="end"))
    p.append(text(rx_ + rw / 2, ry + rh + 22, "час →", size=10, color=MUTED))
    # один часовий слот, поділений по частоті на ресурсні блоки (RU)
    rows = [("A", "#cfe6d4", 0.34), ("B", "#cdd7f3", 0.22),
            ("C", "#f6dcc4", 0.22), ("D", "#e7d6f0", 0.22)]
    yy = ry + 8
    inner_h = rh - 16
    for name, col, frac in rows:
        hh = inner_h * frac
        p.append(rect(rx_ + 6, yy, rw - 12, hh - 4, fill=col, stroke="#9aa3b2",
                      sw=1, rx=4))
        p.append(text(rx_ + 26, yy + hh / 2 + 4, name, size=15, color=INK, bold=True))
        p.append(text(rx_ + rw - 16, yy + hh / 2 + 4, "RU", size=10, color=MUTED,
                      anchor="end"))
        yy += hh
    p.append(text(rx_ + rw / 2, ry + rh + 40,
                  "кожному — свій шматок смуги, усі за один слот", size=10,
                  color=FIELD, italic=True))

    # стрілка між ними
    p.append(text(W / 2, ry + rh / 2 - 6, "→", size=34, color=INK, bold=True))

    render(os.path.join(OUT, "ofdma.svg"), W, H, *p,
           title="Головна ідея Wi-Fi 6: ділити канал, а не чекати черги")


if __name__ == "__main__":
    fig_timeline()
    fig_three_knobs()
    fig_ofdma()
    print("OK: figures ->", OUT)
