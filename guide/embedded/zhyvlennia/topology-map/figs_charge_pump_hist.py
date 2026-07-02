# -*- coding: utf-8 -*-
"""Фігури вставки hist-charge-pump-lineage.md (родовід зарядної помпи).
Окремий файл, щоб не заважати паралельному редагуванню figs.py у цій теці.
svgkit зі scripts/ ІМПОРТУЄМО, не переписуємо (AUTHORING §5).

Запуск:  python figs_charge_pump_hist.py   →  кладе .svg у ./img/
Перевірка: python ../../../../scripts/svgcheck.py img --min-font 8
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

T_BUCK = NEG
T_BOOST = POS
T_BB = FIELD
T_PUMP = "#b8860b"
GOOD_FILL = "#eef7f0"


# ─────────────────────────────────────────────────────────────────────────────
def fig_cw_vs_dickson():
    """Той самий родовід, інша механіка: драбина CW осідає — помпа Діксона ні.
    Ліворуч — CW-драбина (щаблі один НА одному, верх блідне = осідає).
    Праворуч — помпа Діксона (щаблі в РЯД, годинник качає всі одразу)."""
    W, H = 940, 470
    f = []

    # ── Ліва панель: Cockcroft–Walton / Greinacher ──
    f.append(rect(24, 46, 430, 400, fill="#fbf7ec", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(239, 74, "Драбина Кокрофта–Волтона", size=13, color=INK, bold=True))
    f.append(text(239, 92, "щаблі стоять один НА одному", size=10.5, color=MUTED))
    base_y = 402
    xL, xR = 150, 300
    fades = ["#333333", "#5a5a5a", "#8a8a8a", "#b4b4b4"]
    labels = ["×2 Vp", "×3.8", "×5.4", "×6.7"]  # реальні щаблі осідають нижче ×2N
    for i in range(4):
        y = base_y - i * 76
        col = fades[i]
        for cx in (xL, xR):
            f.append(line(cx - 14, y - 5, cx + 14, y - 5, color=col, sw=2.6))
            f.append(line(cx - 14, y + 5, cx + 14, y + 5, color=col, sw=2.6))
        f.append(arrow(xL + 18, y + 2, xR - 18, y - 20, color=col, sw=1.6))
        f.append(text(xR + 66, y - 3, labels[i], size=11, color=col, bold=(i == 0)))
    f.append(line(xL, base_y + 5, xL, base_y + 24, color=INK, sw=2))
    f.append(text(xL, base_y + 38, "~ вхід (AC)", size=10, color=INK))
    f.append(arrow(xR + 40, 128, xR + 40, 104, color=POS, sw=2))
    f.append(text(xR + 40, 146, "верх осідає", size=10, color=POS, bold=True))
    f.append(text(239, 430, "приріст на щабель ПАДАЄ з висотою · брижі ростуть",
                  size=10, color=POS))

    # ── Права панель: Dickson ──
    f.append(rect(486, 46, 430, 400, fill="#eef7f0", stroke=T_BB, sw=1.6, rx=10))
    f.append(text(701, 74, "Помпа Діксона", size=13, color=INK, bold=True))
    f.append(text(701, 92, "щаблі в РЯД, годинник качає всі одразу", size=10.5, color=T_BB))
    ch_y = 200
    xs = [545, 625, 705, 785, 865]
    for i, cx in enumerate(xs):
        last = (i == len(xs) - 1)
        col = T_BOOST if last else T_BB
        f.append(circle(cx, ch_y, 19, fill="#ffffff", stroke=col, sw=2.2))
        f.append(text(cx, ch_y + 5, "×%d" % (i + 1), size=12, color=col, bold=True))
        if i > 0:
            f.append(arrow(xs[i - 1] + 19, ch_y, cx - 19, ch_y, color=INK, sw=1.7))
        if not last:
            pcol = NEG if i % 2 == 0 else POS
            phase = "φ1" if i % 2 == 0 else "φ2"
            f.append(line(cx, ch_y + 19, cx, ch_y + 42, color=pcol, sw=1.6))
            f.append(text(cx, ch_y + 56, phase, size=10, color=pcol, bold=True))
    f.append(text(545, ch_y - 32, "+5В", size=10, color=INK))
    f.append(text(865, ch_y - 32, "+40В", size=11, color=T_BOOST, bold=True))

    def clk(y0, x0, col):
        seq = [0, 1, 1, 0, 0, 1, 1, 0, 0]
        pts = []
        x = x0
        for lvl in seq:
            pts.append((x, y0 - lvl * 15))
            x += 17
            pts.append((x, y0 - lvl * 15))
        d = "M" + " L".join("%.0f %.0f" % p for p in pts)
        return '<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d, col)
    f.append(clk(326, 560, NEG))
    f.append(text(536, 320, "φ1", size=10, color=NEG, bold=True))
    f.append(clk(360, 560, POS))
    f.append(text(536, 354, "φ2", size=10, color=POS, bold=True))
    f.append(rect(500, 384, 402, 52, fill="#ffffff", stroke=T_BB, sw=1.3, rx=8))
    f.append(text(701, 404, "приріст на щабель ОДНАКОВИЙ (≈ Vp − діод)",
                  size=10.5, color=INK, bold=True))
    f.append(text(701, 423, "кратність і струм НЕ залежать від числа щаблів",
                  size=10.5, color=T_BB))

    render(os.path.join(OUT, "cw-vs-dickson.svg"), W, H, *f,
           title="Той самий родовід, інша механіка: драбина осідає — помпа ні")


# ─────────────────────────────────────────────────────────────────────────────
def fig_charge_pump_timeline():
    """Хронологія: від Ґрайнахера крізь прискорювач до напруги пам'яті."""
    W, H = 940, 300
    f = []
    y = 150
    f.append(line(58, y, 882, y, color=INK, sw=2.5))
    f.append(arrow(858, y, 884, y, color=INK, sw=2.5))

    events = [
        (128, "1919", "Ґрайнахер", "каскад-помножувач;\n«помножувач Ґрайнахера»", NEG, True),
        (350, "1932", "Кокрофт·Волтон", "драбина живить прискорювач;\nперший штучний розпад ядра", INK, False),
        (575, "1976", "Діксон (JSSC)", "приріст на щабель незалежний\nвід їх числа; +40В на кристалі", T_BB, True),
        (800, "к. 1970-х", "патент", "помпа Діксона в кремнії;\nживлення flash / EEPROM", T_BOOST, False),
    ]
    for x, yr, who, what, col, up in events:
        f.append(circle(x, y, 8, fill=col, stroke=col, sw=2))
        if up:
            f.append(line(x, y - 8, x, y - 42, color=col, sw=1.5, dash="3,3"))
            f.append(text(x, y - 52, yr, size=13, color=col, bold=True))
            f.append(text(x, y - 36, who, size=11, color=INK, bold=True))
            f.append(mtext(x, y + 26, what, size=9.5, color=MUTED, lh=1.28))
        else:
            f.append(line(x, y + 8, x, y + 42, color=col, sw=1.5, dash="3,3"))
            f.append(text(x, y + 64, yr, size=13, color=col, bold=True))
            f.append(text(x, y + 48, who, size=11, color=INK, bold=True))
            f.append(mtext(x, y - 42, what, size=9.5, color=MUTED, lh=1.28))

    render(os.path.join(OUT, "charge-pump-timeline.svg"), W, H, *f,
           title="Родовід зарядної помпи: від прискорювача до пам'яті")


if __name__ == "__main__":
    fig_cw_vs_dickson()
    fig_charge_pump_timeline()
    print("ok figs charge-pump-hist: 2 файли у img/")
