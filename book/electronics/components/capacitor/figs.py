# -*- coding: utf-8 -*-
"""Фігури до вставки «Маркування й типорозміри конденсаторів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Як читається 3-цифровий код: 104 → 100 нФ ───────────────────────────
def fig_code_104():
    W, H = 720, 400
    f = [text(W / 2, 30, "Три цифри — це не число пікофарад, а «два знаки + нулі»", size=16, bold=True)]

    # великий код на «корпусі»
    bx, by, bw, bh = 250, 64, 220, 96
    f.append(rect(bx, by, bw, bh, fill="#fff7e6", stroke="#d98c00", sw=2.2, rx=10))
    # три цифри окремими клітинками
    digits = ["1", "0", "4"]
    cw = 56
    cx0 = bx + (bw - 3 * cw) / 2
    roles = ["1-й знак", "2-й знак", "× нулі"]
    rcol = [INK, INK, POS]
    for i, d in enumerate(digits):
        x = cx0 + i * cw
        f.append(rect(x + 4, by + 14, cw - 8, bh - 28, fill=BG, stroke=MUTED, sw=1.4, rx=5))
        f.append(text(x + cw / 2, by + bh / 2 + 13, d, size=38, bold=True, color=rcol[i]))
        f.append(text(x + cw / 2, by + bh + 20, roles[i], size=12, color=MUTED))

    # стрілка вниз
    f.append(arrow(W / 2, by + bh + 38, W / 2, by + bh + 70, color=LINE, sw=2))

    # розкладання
    box = fitbox(150, by + bh + 80, 420, 56,
                 "10  ×  10⁴  =  100 000 пФ", size=20, bold=True,
                 fill="#eaf6ee", stroke=FIELD, sw=2)
    f.append(box)

    # ланцюжок одиниць
    yy = by + bh + 168
    chain = "100 000 пФ   =   100 нФ   =   0.1 мкФ"
    cb = fitbox(150, yy, 420, 44, chain, size=18, bold=True,
                fill=FILL, stroke=LINE, sw=1.5)
    f.append(cb)

    # підпис-нагадування про базу
    f.append(text(W / 2, yy + 70, "База коду — завжди пікофарад (пФ). Літера після коду (104K) — це допуск.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, "read-code-104.svg"), W, H, *f)


# ── 2. Драбинка типорозмірів SMD: імперський код = соті дюйма ───────────────
def fig_smd_sizes():
    W, H = 740, 430
    f = [text(W / 2, 28, "Імперський код — це розмір у сотих дюйма; метричний — у десятих міліметра",
              size=15, bold=True)]

    # рядки: (імперський, метричний, L_mm, Wd_mm, px-довжина)
    rows = [
        ("0402", "1005", "1.0 × 0.5", 1.0, 0.5),
        ("0603", "1608", "1.6 × 0.8", 1.6, 0.8),
        ("0805", "2012", "2.0 × 1.25", 2.0, 1.25),
        ("1206", "3216", "3.2 × 1.6", 3.2, 1.6),
    ]
    # масштаб: 1 мм → px
    scale = 58
    x_chip = 470          # ліва межа області, де малюємо корпус у масштабі
    y = 78
    rh = 84

    # шапка таблиці
    f.append(text(70, y - 14, "імперський", size=12, bold=True, color=MUTED, anchor="start"))
    f.append(text(190, y - 14, "метричний", size=12, bold=True, color=MUTED, anchor="start"))
    f.append(text(310, y - 14, "Д × Ш, мм", size=12, bold=True, color=MUTED, anchor="start"))
    f.append(text(x_chip, y - 14, "у масштабі (вид зверху)", size=12, bold=True, color=MUTED, anchor="start"))

    for imp, met, dims, L, Wd in rows:
        cy = y + rh / 2
        f.append(line(60, y + rh - 6, W - 30, y + rh - 6, color="#e3e6ea", sw=1))
        f.append(text(70, cy + 6, imp, size=20, bold=True, anchor="start"))
        f.append(text(190, cy + 6, met, size=18, color=MUTED, anchor="start"))
        f.append(text(310, cy + 6, dims, size=15, anchor="start"))
        # корпус у масштабі: прямокутник L×Wd мм
        rw, rwd = L * scale, Wd * scale
        rx, ry = x_chip, cy - rwd / 2
        # металізовані торці
        f.append(rect(rx, ry, rw, rwd, fill="#e9edf2", stroke=LINE, sw=1.6, rx=2))
        cap = max(4, rw * 0.16)
        f.append(rect(rx, ry, cap, rwd, fill="#b9c2cc", stroke=LINE, sw=1.2, rx=2))
        f.append(rect(rx + rw - cap, ry, cap, rwd, fill="#b9c2cc", stroke=LINE, sw=1.2, rx=2))
        y += rh

    # застереження
    f.append(text(W / 2, y + 18,
                  "Той самий «0603» у двох системах — це РІЗНІ корпуси: імперський 0603 = метричний 1608.",
                  size=13, color=POS, bold=True))
    render(os.path.join(IMG, "smd-size-ladder.svg"), W, H, *f)


# ── 3. Чому «багатошаровий»: пачка електродів = велика площа в малому об'ємі ──
def fig_mlcc_stack():
    W, H = 760, 470
    f = [text(W / 2, 30,
              "MLCC зсередини: десятки тонких електродів, увімкнених паралельно",
              size=15, bold=True)]

    # Ліворуч — розріз пачки. Електроди заходять гребінкою з двох торців.
    bx, by, bw, bh = 70, 78, 300, 286
    f.append(rect(bx, by, bw, bh, fill="#eef3f0", stroke=LINE, sw=2))

    n = 9                      # видимих внутрішніх електродів
    gap = bh / (n + 1)
    elx0, elw = bx + 18, bw - 36
    for i in range(n):
        y = by + gap * (i + 1)
        left = (i % 2 == 0)    # парні чіпляються до лівого торця, непарні — до правого
        if left:
            x1, x2 = elx0, elx0 + elw - 26
            col = POS
        else:
            x1, x2 = elx0 + 26, elx0 + elw
            col = NEG
        f.append(line(x1, y, x2, y, color=col, sw=4))

    # Металізовані торцеві контакти (термінації)
    f.append(rect(bx - 14, by, 14, bh, fill="#9aa7ad", stroke=LINE, sw=1.5, rx=2))
    f.append(rect(bx + bw, by, 14, bh, fill="#9aa7ad", stroke=LINE, sw=1.5, rx=2))
    f.append(text(bx + bw / 2, by - 12,
                  "← сотні таких шарів по висоті →", size=12, color=MUTED))
    f.append(text(bx + bw / 2, by + bh + 24,
                  "керамічний діелектрик між кожною парою електродів",
                  size=12, color=INK))
    f.append(text(bx - 7, by + bh + 44, "термінація", size=11, color=MUTED))
    f.append(text(bx + bw + 7, by + bh + 44, "термінація", size=11, color=MUTED))

    # Праворуч — рушії ємності: площа × шари ÷ товщина шару.
    rx = 470
    box, _w, _h = textbox(rx + 130, 120, "C = ε · (N−1) · A / d",
                          size=16, bold=True, fill="#fff8e1", stroke="#d4a017")
    f.append(box)
    f.append(text(rx + 130, 168, "більше шарів N  →  більше C", size=13, color=FIELD))
    f.append(text(rx + 130, 193, "тонший шар d   →  більше C", size=13, color=FIELD))
    f.append(text(rx + 130, 218, "тонший шар d   →  нижча Uроб", size=13, color=POS))

    f.append(line(rx + 16, 250, rx + 244, 250, color=MUTED, dash="4 4"))
    note = ("Усі шари — паралельно: кожен додає ємності.\n"
            "Так у крихітному корпусі вміщається стільки ж,\n"
            "скільки колись у великому конденсаторі.")
    f.append(mtext(rx + 130, 286, note, size=12, color=INK))

    render(os.path.join(IMG, 'mlcc-stack.svg'), W, H, *f)


# ── 4. Серце теми: ємність «пливе» від напруги (DC bias) за класами ──────────
def fig_dc_bias():
    W, H = 800, 500
    f = [text(W / 2, 28,
              "DC bias: під робочою напругою ємність класу II просідає",
              size=15, bold=True)]

    ox, oy = 100, 410          # початок координат
    pw, ph = 560, 320          # поле графіка
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=2))          # вісь X
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=2))          # вісь Y

    def ypct(p):
        return oy - ph * p / 120.0

    def xpct(p):
        return ox + pw * p / 100.0

    # Сітка Y: 0..120 % ємності
    for pct in (0, 20, 40, 60, 80, 100, 120):
        y = ypct(pct)
        f.append(line(ox, y, ox + pw, y, color="#e5e7eb", sw=1))
        f.append(text(ox - 12, y + 4, "%d" % pct, size=11, color=MUTED, anchor="end"))
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">%s</text>'
             % (ox - 64, oy - ph / 2, FONT, INK, ox - 64, oy - ph / 2,
                "ємність, % від номіналу"))

    # Сітка X: 0..100 % робочої напруги
    for pct in (0, 25, 50, 75, 100):
        x = xpct(pct)
        f.append(line(x, oy, x, oy - ph, color="#f0f1f3", sw=1))
        f.append(text(x, oy + 22, "%d" % pct, size=11, color=MUTED))
    f.append(text(ox + pw / 2, oy + 44,
                  "прикладена постійна напруга, % від номінальної",
                  size=12, color=INK))

    # C0G/NP0 — клас I: пряма ~100 %.
    pts = " ".join("%.1f,%.1f" % (xpct(v), ypct(100)) for v in range(0, 101, 10))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (pts, FIELD))
    # X7R/X5R — клас II: помірне просідання, ~−55 % на номіналі.
    x7r = [(0, 100), (25, 92), (50, 78), (75, 60), (100, 45)]
    pts = " ".join("%.1f,%.1f" % (xpct(k), ypct(v)) for k, v in x7r)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (pts, "#e08a1e"))
    # Y5V — клас II «крайній»: обвал до ~18 %.
    y5v = [(0, 100), (25, 80), (50, 55), (75, 32), (100, 18)]
    pts = " ".join("%.1f,%.1f" % (xpct(k), ypct(v)) for k, v in y5v)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (pts, POS))

    f.append(text(xpct(100) + 8, ypct(100) + 4, "C0G / NP0  (клас I)",
                  size=12, color=FIELD, anchor="start", bold=True))
    f.append(text(xpct(100) + 8, ypct(45) + 4, "X7R / X5R  (клас II)",
                  size=12, color="#e08a1e", anchor="start", bold=True))
    f.append(text(xpct(100) + 8, ypct(18) + 4, "Y5V  (клас II)",
                  size=12, color=POS, anchor="start", bold=True))
    f.append(circle(xpct(100), ypct(45), 4, fill=POS, stroke="#fff", sw=1.5))

    render(os.path.join(IMG, 'dc-bias.svg'), W, H, *f)


if __name__ == "__main__":
    fig_code_104()
    fig_smd_sizes()
    fig_mlcc_stack()
    fig_dc_bias()
    print("OK: figs written to", IMG)
