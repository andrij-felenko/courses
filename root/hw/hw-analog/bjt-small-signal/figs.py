# -*- coding: utf-8 -*-
"""Фігури до теми «Мала-сигнальна модель BJT».
Три фігури:
  tangent.svg  — крива Ic(Vbe) та дотична в робочій точці (лінеаризація)
  model.svg    — мала-сигнальна схема заміщення (rπ + джерело gm·vbe + Rc)
  reconcile.svg— чому Av = −Rc/(Re+re), і коли спрощується до −Rc/Re
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні примітиви ──────────────────────────────────────────────────────
def gnd(cx, y, label=None):
    out = [line(cx, y, cx, y + 6, color=INK, sw=1.8),
           line(cx - 12, y + 6, cx + 12, y + 6, color=INK, sw=2.4),
           line(cx - 7, y + 11, cx + 7, y + 11, color=INK, sw=2.0),
           line(cx - 2, y + 16, cx + 2, y + 16, color=INK, sw=1.8)]
    if label:
        out.append(text(cx, y + 31, label, size=11, color=MUTED))
    return "".join(out)


def res_box(x, y, w, h, label=None, vert=False, lab_dx=0, lab_dy=0):
    out = [rect(x, y, w, h, fill="#ffffff", stroke=INK, sw=1.6, rx=2)]
    if label:
        cx, cy = x + w / 2, y + h / 2
        out.append(text(cx + lab_dx, cy + lab_dy, label, size=12, color=INK))
    return "".join(out)


def cs_source(cx, cy, r=22, label=None):
    """Символ керованого джерела струму: ромб зі стрілкою вгору."""
    d = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
         'fill="#ffffff" stroke="%s" stroke-width="1.8"/>'
         % (cx, cy - r, cx + r, cy, cx, cy + r, cx - r, cy, FIELD))
    arr = arrow(cx, cy + r * 0.55, cx, cy - r * 0.55, color=FIELD, sw=2.2)
    out = d + arr
    if label:
        out += text(cx + r + 8, cy + 4, label, size=12, color=FIELD, anchor="start", bold=True)
    return out


# ── Фігура 1: лінеаризація — крива Ic(Vbe) та дотична в точці Q ──────────────
def fig_tangent():
    W, H = 640, 420
    P = []
    ox, oy = 90, 350          # початок осей
    aw, ah = 470, 280         # довжина осей
    # осі
    P.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    P.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    P.append(text(ox + aw - 6, oy + 26, "Vbe", size=13, color=INK, anchor="end", italic=True))
    P.append(text(ox - 60, oy - ah + 8, "Ic", size=13, color=INK, anchor="start", italic=True))
    # експонента Ic = I0 * exp(k*x); підберемо так, щоб гарно лягла
    import math as m
    xs = [i / 100.0 for i in range(0, 101)]   # 0..1 нормовано
    k = 5.2
    def Y(t):  # t у 0..1
        return (m.exp(k * t) - 1) / (m.exp(k) - 1)   # 0..1
    pts = []
    for t in xs:
        X = ox + t * aw
        Yv = oy - Y(t) * ah
        pts.append("%.1f,%.1f" % (X, Yv))
    P.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), POS))
    # робоча точка Q при t=0.72
    tq = 0.72
    Xq = ox + tq * aw
    Yq = oy - Y(tq) * ah
    # дотична: похідна Y'(t) = k*exp(k t)/(exp(k)-1); у px: dYpx/dXpx
    dydt = k * m.exp(k * tq) / (m.exp(k) - 1)
    # нахил у px-координатах (Y вниз інвертовано)
    slope_px = -(dydt * ah) / (1.0 * aw)
    # намалюємо відрізок дотичної навколо Q
    seg = 150
    x1, x2 = Xq - seg, Xq + seg
    y1 = Yq + slope_px * (x1 - Xq)
    y2 = Yq + slope_px * (x2 - Xq)
    P.append(line(x1, y1, x2, y2, color=NEG, sw=2.2, dash="7 5"))
    # точка Q
    P.append(circle(Xq, Yq, 5, fill=INK, stroke=INK))
    P.append(text(Xq + 12, Yq - 10, "Q", size=14, color=INK, bold=True, anchor="start"))
    # маленький трикутник нахилу ΔIc/ΔVbe
    tb = textbox(ox + 150, oy - ah + 44, "нахил у Q = gm = ΔIc / ΔVbe",
                 size=13, color=NEG, stroke=NEG, fill="#eef3ff")
    P.append(tb[0])
    # підпис кривої
    P.append(text(ox + aw - 8, oy - ah + 70, "Ic ~ exp(Vbe / VT)", size=12,
                  color=POS, anchor="end", italic=True))
    # маленький сигнал навколо Q (хвилька на осі x)
    P.append(line(Xq, oy, Xq, Yq, color=MUTED, sw=1.0, dash="3 4"))
    P.append(line(ox, Yq, Xq, Yq, color=MUTED, sw=1.0, dash="3 4"))
    render(os.path.join(IMG, "tangent.svg"), W, H, *P,
           title="Малий сигнал бачить пряму дотичну")


# ── Фігура 2: мала-сигнальна схема заміщення ────────────────────────────────
def fig_model():
    W, H = 660, 380
    P = []
    # ── ліва частина: вхід ── база (b) ── rπ ── емітер (e, земля) ──
    bx, by = 70, 150          # вузол бази
    ex, ey = 70, 300          # вузол емітера (земля)
    P.append(text(bx - 18, by + 4, "b", size=13, color=INK, anchor="end", bold=True))
    P.append(circle(bx, by, 4, fill=INK, stroke=INK))
    # вхідне джерело vbe (позначка) ліворуч
    P.append(line(bx, by, bx, by, color=INK))
    # rπ між b і e
    rw, rh = 18, 70
    P.append(line(bx, by, bx, by + 20, color=INK, sw=1.6))
    P.append(res_box(bx - rw / 2, by + 20, rw, rh, label=None))
    P.append(text(bx + rw / 2 + 8, by + 20 + rh / 2 + 4, "rπ", size=14, color=INK, anchor="start"))
    P.append(line(bx, by + 20 + rh, ex, ey, color=INK, sw=1.6))
    P.append(circle(ex, ey, 4, fill=INK, stroke=INK))
    P.append(text(ex - 18, ey + 4, "e", size=13, color=INK, anchor="end", bold=True))
    P.append(gnd(ex, ey + 6))
    # підпис vbe — напруга на rπ
    P.append(text(bx - 30, by + 55, "vbe", size=12, color=NEG, anchor="middle", italic=True))
    P.append(line(bx - 30, by + 24, bx - 30, by + 20 + rh, color=NEG, sw=1.0, dash="3 3"))
    P.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" text-anchor="middle">↕</text>'
             % (bx - 30, by + 18, FONT, NEG))

    # ── права частина: вихід ── колектор (c) ── джерело gm·vbe || Rc ──
    cx, cy = 360, 150          # вузол колектора
    P.append(circle(cx, cy, 4, fill=INK, stroke=INK))
    P.append(text(cx + 12, cy - 6, "c", size=13, color=INK, anchor="start", bold=True))
    # кероване джерело струму між c і землею
    src_y = (cy + ey) / 2 + 5
    P.append(line(cx, cy, cx, src_y - 24, color=INK, sw=1.6))
    P.append(cs_source(cx, src_y, r=22, label="gm·vbe"))
    P.append(line(cx, src_y + 22, cx, ey, color=INK, sw=1.6))
    P.append(line(cx, ey, ex, ey, color=INK, sw=1.6))      # спільна земля (емітер)
    # Rc праворуч від колектора до Vcc(змінно — земля для сигналу)
    rcx = 520
    P.append(line(cx, cy, rcx, cy, color=INK, sw=1.6))
    P.append(res_box(rcx - rw / 2, cy + 18, rw, rh, label=None))
    P.append(line(rcx, cy, rcx, cy + 18, color=INK, sw=1.6))
    P.append(text(rcx + rw / 2 + 8, cy + 18 + rh / 2 + 4, "Rc", size=14, color=INK, anchor="start"))
    P.append(line(rcx, cy + 18 + rh, rcx, ey, color=INK, sw=1.6))
    P.append(line(rcx, ey, cx, ey, color=INK, sw=1.6))
    # вихід vout на колекторі
    P.append(circle(cx, cy, 4, fill=INK, stroke=INK))
    P.append(text(cx, cy - 24, "vout", size=12, color=POS, italic=True))

    # стрілка-зв'язок: vbe керує джерелом
    P.append(line(bx - 30, by + 70, cx, src_y, color=FIELD, sw=1.2, dash="4 4"))
    tb = textbox(215, src_y, "те саме vbe\nкерує струмом", size=11, color=FIELD,
                 stroke=FIELD, fill="#eafaf0")
    P.append(tb[0])

    # підписи областей
    P.append(text(70, 60, "ВХІД", size=12, color=MUTED, bold=True))
    P.append(text(440, 60, "ВИХІД", size=12, color=MUTED, bold=True))
    render(os.path.join(IMG, "model.svg"), W, H, *P,
           title="Мала-сигнальна схема заміщення BJT")


# ── Фігура 3: звідки −Rc/Re і чому re всередині ─────────────────────────────
def fig_reconcile():
    W, H = 660, 360
    P = []
    # три рамки-кроки згори вниз
    cx = W / 2
    b1 = textbox(cx, 70, "повна формула:  Av = − Rc / (re + Re)", size=15,
                 color=INK, stroke=INK, fill=FILL, bold=True)
    P.append(b1[0])
    # стрілка вниз
    P.append(arrow(cx, 70 + b1[2] / 2, cx, 150, color=MUTED, sw=1.6))

    b2 = textbox(cx - 150, 180, "Re ≫ re\n(є емітерний резистор)", size=12,
                 color=NEG, stroke=NEG, fill="#eef3ff")
    P.append(b2[0])
    b3 = textbox(cx + 150, 180, "Re = 0\n(емітер на землі)", size=12,
                 color=POS, stroke=POS, fill="#fdecea")
    P.append(b3[0])
    P.append(arrow(cx - 30, 150, cx - 150, 180 - b2[2] / 2 - 4, color=NEG, sw=1.4))
    P.append(arrow(cx + 30, 150, cx + 150, 180 - b3[2] / 2 - 4, color=POS, sw=1.4))

    b4 = textbox(cx - 150, 285, "Av ≈ − Rc / Re\n(задають резистори)", size=13,
                 color=NEG, stroke=NEG, fill="#eef3ff", bold=True)
    P.append(b4[0])
    b5 = textbox(cx + 150, 285, "Av = − gm·Rc = − Rc / re\n(задає робочий струм)", size=12,
                 color=POS, stroke=POS, fill="#fdecea", bold=True)
    P.append(b5[0])
    P.append(arrow(cx - 150, 180 + b2[2] / 2, cx - 150, 285 - b4[2] / 2 - 4, color=NEG, sw=1.4))
    P.append(arrow(cx + 150, 180 + b3[2] / 2, cx + 150, 285 - b5[2] / 2 - 4, color=POS, sw=1.4))

    render(os.path.join(IMG, "reconcile.svg"), W, H, *P,
           title="Одна формула — два знайомі випадки")


if __name__ == "__main__":
    fig_tangent()
    fig_model()
    fig_reconcile()
    print("OK: 3 figures ->", IMG)
