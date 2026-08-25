# -*- coding: utf-8 -*-
"""Фігури для ДЕТАЛЬНОЇ версії «Дільник напруги» (voltage-divider-d.md).
Базові SVG (divider-formula, choose-ratio, potentiometer, loading, sensor,
tolerance-*, divider-*) створено раніше й тут НЕ переген­еровуються — цей
файл додає лише три нові фігури детального викладу."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def gnd(cx, cy, w=24):
    s = line(cx, cy, cx, cy + 9, color=INK, sw=1.8)
    for i, ww in enumerate((w, w * 0.6, w * 0.28)):
        s += line(cx - ww / 2, cy + 9 + i * 5, cx + ww / 2, cy + 9 + i * 5, color=INK, sw=1.8)
    return s


def cap_v(cx, cy, gap=8, plate=16):
    """Конденсатор із ГОРИЗОНТАЛЬНИМИ пластинами (струм тече вертикально)."""
    return (line(cx - plate, cy - gap / 2, cx + plate, cy - gap / 2, color=INK, sw=2.4) +
            line(cx - plate, cy + gap / 2, cx + plate, cy + gap / 2, color=INK, sw=2.4))


def polyline(pts, color=INK, sw=2.2):
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (" ".join("%.1f,%.1f" % p for p in pts), color, sw))


# ── 1. Дільник ⟺ еквівалент Тевеніна ─────────────────────────────────────────
def fig_thevenin():
    W, H = 760, 384
    e = []

    # ── лівий бік: реальний дільник ──
    sx = 150
    e.append(text(sx, 54, "V", size=15, bold=True, color=POS))
    e.append(line(sx, 62, sx, 92, color=INK, sw=2))
    e.append(rect(sx - 12, 92, 24, 46, fill="#fdecea", stroke=POS, sw=2))
    e.append(text(sx - 20, 120, "R₁", size=14, bold=True, color=POS, anchor="end"))
    e.append(line(sx, 138, sx, 168, color=INK, sw=2))
    e.append(circle(sx, 168, 3.6, fill=INK, stroke=INK))
    e.append(line(sx + 4, 168, 236, 168, color=INK, sw=2))            # відвід
    e.append(text(242, 172, "V_вих", size=13, color=INK, anchor="start"))
    e.append(line(sx, 168, sx, 198, color=INK, sw=2))
    e.append(rect(sx - 12, 198, 24, 46, fill=FILL, stroke=INK, sw=2))
    e.append(text(sx - 20, 226, "R₂", size=14, bold=True, anchor="end"))
    e.append(line(sx, 244, sx, 272, color=INK, sw=2))
    e.append(gnd(sx, 272))

    # ── стрілка тотожності + підпис ──
    e.append(arrow(268, 120, 372, 120, color=FIELD, sw=2.4))
    b, _, _ = textbox(320, 182, "еквівалент\nТевеніна", size=13, fill="#eafaf0",
                      stroke=FIELD, color=INK)
    e.append(b)

    # ── правий бік: джерело V_т за опором R_т ──
    tx = 578
    e.append(circle(tx, 108, 4, fill=BG, stroke=INK, sw=1.8))          # відкритий вихід
    e.append(text(tx + 22, 112, "V_вих", size=13, color=INK, anchor="start"))
    e.append(line(tx, 112, tx, 150, color=INK, sw=2))
    e.append(rect(tx - 12, 150, 24, 46, fill="#eafaf0", stroke=FIELD, sw=2))
    e.append(text(tx + 20, 178, "R_т", size=14, bold=True, color=FIELD, anchor="start"))
    e.append(line(tx, 196, tx, 226, color=INK, sw=2))
    e.append(circle(tx, 252, 26, fill=BG, stroke=NEG, sw=2))           # джерело
    e.append(text(tx, 239, "+", size=15, bold=True, color=POS))
    e.append(text(tx, 261, "V_т", size=14, bold=True, color=NEG))
    e.append(text(tx, 276, "−", size=15, bold=True, color=NEG))
    e.append(line(tx, 278, tx, 300, color=INK, sw=2))
    e.append(gnd(tx, 300))

    # ── формули внизу ──
    e.append(fitbox(150, 330, 460, 40,
                    "V_т = V·R₂/(R₁+R₂)      R_т = R₁∥R₂ = R₁·R₂/(R₁+R₂)",
                    size=15, fill=FILL, stroke=MUTED, color=INK))
    return render(os.path.join(OUT, 'divider-thevenin.svg'), W, H, *e,
                  title="Будь-який дільник — це джерело V_т за внутрішнім опором R_т = R₁∥R₂")


# ── 2. Просідання виходу залежно від R_н/R_т ─────────────────────────────────
def fig_loading_sag():
    W, H = 720, 360
    e = []
    base = 300
    axx = 74
    e.append(line(axx, 70, axx, base, color=INK, sw=1.6))            # вісь Y
    e.append(line(axx, base, 672, base, color=INK, sw=1.6))          # вісь X
    e.append(text(axx - 4, 62, "просідання, %", size=12.5, color=MUTED, anchor="start"))

    data = [("×1", 50.0), ("×2", 33.3), ("×5", 16.7),
            ("×10", 9.1), ("×20", 4.8), ("×100", 1.0)]
    scale = 4.2
    x0, step, bw = 108, 94, 54
    for i, (lab, sag) in enumerate(data):
        cx = x0 + i * step
        h = sag * scale
        col = POS if sag >= 20 else (FIELD if sag <= 5 else "#b8860b")
        fill = "#fdecea" if sag >= 20 else ("#eafaf0" if sag <= 5 else "#fef6e7")
        e.append(rect(cx - bw / 2, base - h, bw, h, fill=fill, stroke=col, sw=2, rx=3))
        e.append(text(cx, base - h - 9, "%.0f %%" % sag if sag >= 10 or sag == 1.0
                      else "%.1f %%" % sag, size=13, bold=True, color=col))
        e.append(text(cx, base + 19, lab, size=13, color=INK))
    e.append(text(x0 + 2.5 * step, base + 40, "R_н / R_т  (у скільки разів навантаження опірніше)",
                  size=12.5, color=MUTED))
    e.append(fitbox(430, 60, 250, 40, "просідання = R_т / (R_н + R_т)",
                    size=14, fill=FILL, stroke=MUTED, color=INK))
    return render(os.path.join(OUT, 'loading-sag.svg'), W, H, *e,
                  title="Чим слабше навантажений дільник, тим менше просідає вихід")


# ── 3. Компенсований дільник і реакція на прямокутник ────────────────────────
def _square_levels(x0, x1, y_lo, y_hi, cycles=2, n=260):
    """Ідеальний прямокутник як список семплів рівня (0/1) і точок."""
    lv = []
    for i in range(n + 1):
        t = i / n
        s = 1 if (int(t * cycles * 2) % 2 == 0) else 0     # 0 = високий, 1 = низький? задамо: парний → високий
        lv.append(s)
    return lv


def _mode_points(x0, x1, y_lo, y_hi, mode, cycles=2, n=300):
    span = y_lo - y_hi
    lv = []
    for i in range(n + 1):
        t = i / n
        lv.append(1.0 if (int(t * cycles * 2) % 2 == 0) else 0.0)   # 1=високий рівень
    # низькочастотне згладжування (недокомпенсація — округлені кути)
    yl = [0.0] * (n + 1)
    tau = 0.9
    for i in range(1, n + 1):
        yl[i] = yl[i - 1] + (lv[i] - yl[i - 1]) / tau
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + t * (x1 - x0)
        if mode == "ok":
            u = lv[i]
        elif mode == "under":
            u = yl[i]
        else:  # over — ідеал + підкреслені фронти (викиди)
            u = lv[i] + 1.15 * (lv[i] - yl[i])
            u = max(-0.28, min(1.28, u))
        y = y_hi + (1.0 - u) * span
        pts.append((x, y))
    return pts


def fig_compensated():
    W, H = 786, 384
    e = []

    # ── схема компенсованого дільника ──
    sx = 148
    top, mid, bot = 92, 168, 244
    e.append(text(sx, 54, "вхід", size=13, color=MUTED))
    e.append(line(sx, 62, sx, top, color=INK, sw=2))
    # верхнє плече: R1 ∥ C1
    e.append(line(126, top, 178, top, color=INK, sw=2))
    e.append(rect(114, top + 8, 24, 44, fill="#fdecea", stroke=POS, sw=2))       # R1 (x=126)
    e.append(line(126, top, 126, top + 8, color=INK, sw=2))
    e.append(line(126, top + 52, 126, mid, color=INK, sw=2))
    e.append(text(100, top + 32, "R₁", size=13, bold=True, color=POS, anchor="end"))
    e.append(line(178, top, 178, top + 22, color=INK, sw=2))                     # C1 (x=178)
    e.append(cap_v(178, top + 30))
    e.append(line(178, top + 38, 178, mid, color=INK, sw=2))
    e.append(text(196, top + 34, "C₁", size=13, bold=True, color=NEG, anchor="start"))
    e.append(line(126, mid, 178, mid, color=INK, sw=2))
    # відвід
    e.append(circle(152, mid, 3.4, fill=INK, stroke=INK))
    e.append(line(152, mid, 244, mid, color=INK, sw=2))
    e.append(text(250, mid + 4, "V_вих", size=13, color=INK, anchor="start"))
    # нижнє плече: R2 ∥ C2
    e.append(line(126, mid, 126, mid + 8, color=INK, sw=2))
    e.append(rect(114, mid + 8, 24, 44, fill=FILL, stroke=INK, sw=2))            # R2
    e.append(line(126, mid + 52, 126, bot, color=INK, sw=2))
    e.append(text(100, mid + 32, "R₂", size=13, bold=True, anchor="end"))
    e.append(line(178, mid, 178, mid + 22, color=INK, sw=2))                     # C2
    e.append(cap_v(178, mid + 30))
    e.append(line(178, mid + 38, 178, bot, color=INK, sw=2))
    e.append(text(196, mid + 34, "C₂", size=13, bold=True, color=NEG, anchor="start"))
    e.append(line(126, bot, 178, bot, color=INK, sw=2))
    e.append(line(152, bot, 152, bot + 22, color=INK, sw=2))
    e.append(gnd(152, bot + 22))
    e.append(fitbox(60, 322, 240, 42, "умова: R₁·C₁ = R₂·C₂\n→ поділ не залежить від частоти",
                    size=13, fill="#eafaf0", stroke=FIELD, color=INK))

    # ── три реакції на прямокутник ──
    panels = [("недокомпенсація: кути завалені", "under", POS, 60),
              ("точно (R₁C₁ = R₂C₂): рівна полиця", "ok", FIELD, 168),
              ("перекомпенсація: викиди на фронтах", "over", "#b8860b", 276)]
    px0, px1 = 452, 700
    for title, mode, col, y0 in panels:
        e.append(text((px0 + px1) / 2, y0 - 8, title, size=12, color=col, bold=True))
        e.append(rect(px0, y0, px1 - px0, 74, fill=BG, stroke=MUTED, sw=1.2))
        pts = _mode_points(px0 + 10, px1 - 10, y0 + 60, y0 + 16, mode)
        e.append(polyline(pts, color=col, sw=2.4))
    return render(os.path.join(OUT, 'compensated-divider.svg'), W, H, *e,
                  title="Компенсований дільник: конденсатор у кожне плече робить поділ рівним на всіх частотах")


if __name__ == '__main__':
    fig_thevenin()
    fig_loading_sag()
    fig_compensated()
    print("ok: 3 figures")
