# -*- coding: utf-8 -*-
# Фігури для вставки proj-copper-calc.md (тема pcb-intro).
# Виводимо в ./img/ поряд із фігурами основної теми, ІМЕНА не перетинаються.
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER = "#b87333"   # мідь
COPDK  = "#8a561f"   # темніший обрис міді
CORE   = "#d8c98a"   # склоепоксидне осердя (FR-4)
MASK   = "#1f7a4d"   # паяльна маска


# ── via-barrel-unroll: розкатати мідний циліндр отвору в пласку стрічку ──────
# Головна ідея вставки: переріз металізації via — це кільце міді (annulus),
# але для розрахунку його «розрізають і розкатують» у пласку доріжку
# завширшки π·d і завтовшки з плату (товщина = товщина металізації). Тоді
# формула IPC-2221 для доріжки застосовна до via як є.
def fig_via_barrel_unroll():
    W, H = 780, 430
    p = []

    # ── ЛІВОРУЧ: via в розрізі, з кільцем міді на стінці ──────────────────
    lx = 175              # центр отвору
    yt, yb = 110, 320     # верх/низ плати
    core_w = 150          # ширина шматка плати в розрізі
    d_out = 96            # зовнішній діаметр отвору (свердло)
    wall  = 15            # товщина металізації (перебільшено)

    p.append(text(lx, 74, "Металізований отвір у розрізі", size=13, bold=True))

    # осердя FR-4 навколо отвору (два стовпчики ліворуч/праворуч від каналу)
    p.append(rect(lx - core_w/2, yt, core_w/2 - d_out/2, yb - yt,
                  fill=CORE, stroke="#b8a55f", sw=1.4, rx=2))
    p.append(rect(lx + d_out/2, yt, core_w/2 - d_out/2, yb - yt,
                  fill=CORE, stroke="#b8a55f", sw=1.4, rx=2))
    # мідна стінка (дві вертикальні смуги — стінки каналу)
    p.append(rect(lx - d_out/2, yt, wall, yb - yt, fill=COPPER, stroke=COPDK, sw=1.2, rx=1))
    p.append(rect(lx + d_out/2 - wall, yt, wall, yb - yt, fill=COPPER, stroke=COPDK, sw=1.2, rx=1))
    # верхній/нижній майданчики
    p.append(rect(lx - d_out/2 - 10, yt - 8, d_out + 20, 8, fill=COPPER, stroke=COPDK, sw=1.0, rx=1))
    p.append(rect(lx - d_out/2 - 10, yb, d_out + 20, 8, fill=COPPER, stroke=COPDK, sw=1.0, rx=1))
    # порожнеча всередині каналу — підпис
    p.append(text(lx, (yt + yb)/2, "порожньо", size=10, color=MUTED, italic=True))

    # розмір d (зовнішній діаметр) угорі
    p.append(line(lx - d_out/2, yt - 24, lx + d_out/2, yt - 24, color=NEG, sw=1.4))
    p.append(line(lx - d_out/2, yt - 28, lx - d_out/2, yt - 20, color=NEG, sw=1.4))
    p.append(line(lx + d_out/2, yt - 28, lx + d_out/2, yt - 20, color=NEG, sw=1.4))
    p.append(text(lx, yt - 30, "d (свердло)", size=10, color=NEG))
    # товщина стінки — виноска праворуч від правої смуги
    p.append(line(lx + d_out/2 + 14, yt + 40, lx + d_out/2 - wall/2, yt + 40, color=POS, sw=1.2))
    b, _, _ = textbox(lx + d_out/2 + 58, yt + 40, "стінка t\n(металізація)", size=9.5,
                      color=POS, fill="#ffffff", stroke=POS, sw=1.0, pad=4)
    p.append(b)

    # стрілка «розкатати»
    p.append(arrow(300, 210, 372, 210, color=INK, sw=2.2))
    p.append(text(336, 196, "розкатати", size=11, bold=True))
    p.append(text(336, 230, "кільце", size=10, color=MUTED))

    # ── ПРАВОРУЧ: та сама мідь як пласка стрічка ─────────────────────────
    rx0 = 410
    strip_w = 300         # довжина стрічки (це периметр = π·d)
    strip_h = 26          # висота стрічки на екрані (це «товщина плати», не важлива для площі)
    ry = 200
    p.append(text(rx0 + strip_w/2, 74, "Та сама мідь — пласка стрічка", size=13, bold=True))

    p.append(rect(rx0, ry - strip_h/2, strip_w, strip_h, fill=COPPER, stroke=COPDK, sw=1.4, rx=2))
    # позначка ширини стрічки = периметр отвору
    p.append(line(rx0, ry - strip_h/2 - 16, rx0 + strip_w, ry - strip_h/2 - 16, color=NEG, sw=1.4))
    p.append(line(rx0, ry - strip_h/2 - 20, rx0, ry - strip_h/2 - 12, color=NEG, sw=1.4))
    p.append(line(rx0 + strip_w, ry - strip_h/2 - 20, rx0 + strip_w, ry - strip_h/2 - 12, color=NEG, sw=1.4))
    p.append(text(rx0 + strip_w/2, ry - strip_h/2 - 22, "ширина = π · d  (периметр отвору)", size=10.5, color=NEG))
    # позначка товщини стрічки = t
    p.append(line(rx0 + strip_w + 14, ry - strip_h/2, rx0 + strip_w + 14, ry + strip_h/2, color=POS, sw=1.4))
    p.append(text(rx0 + strip_w + 20, ry + 4, "t", size=12, color=POS, bold=True, anchor="start"))

    # площа перерізу — формула під стрічкою (у своїй рамці)
    b, _, _ = textbox(rx0 + strip_w/2, ry + 70,
                      "переріз міді  A ≈ π · d · t", size=13, bold=True,
                      fill="#fbf7f0", stroke=COPPER, sw=1.4, pad=10)
    p.append(b)

    render(os.path.join(OUT, "via-barrel-unroll.svg"), W, H, *p)


# ── trace-width-wall: нелінійна стіна ширини під струм (степінь 0.725) ───────
# Ідея: ширина доріжки під струм росте НЕ лінійно. Показуємо криву ширина(струм)
# за IPC-2221 (external, 1 oz, dT=10) та підписуємо, що подвоєння струму вимагає
# ~2.6× ширини — ось чому з якогось моменту дешевше товща мідь або багато via.
def fig_trace_width_wall():
    W, H = 760, 440
    p = []
    p.append(text(W/2, 30, "Стіна ширини: подвоїти струм ≠ подвоїти ширину", size=15, bold=True))

    # осі
    ox, oy = 90, 360      # початок координат (лівий низ)
    ax_w, ax_h = 600, 280
    p.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.6))          # X
    p.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.6))          # Y
    p.append(text(ox + ax_w/2, oy + 40, "струм I, А", size=12))
    # підпис осі Y — вертикально
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">ширина доріжки, мм</text>'
             % (ox - 52, oy - ax_h/2, FONT, INK, ox - 52, oy - ax_h/2))

    # діапазони
    I_max = 12.0          # А
    w_max = 6.0           # мм (для масштабу осі)

    def W_of_I(I):
        # IPC-2221 external, 1 oz, dT=10: A[mil^2] = (I/(0.048*10^0.44))^(1/0.725)
        A = (I / (0.048 * (10.0 ** 0.44))) ** (1.0 / 0.725)
        thick_mil = 1.378
        w_mil = A / thick_mil
        return w_mil * 0.0254   # мм

    def sx(I):  return ox + (I / I_max) * ax_w
    def sy(w):  return oy - (min(w, w_max) / w_max) * ax_h

    # позначки осей — короткі риски біля осей (не суцільна сітка, щоб лінії
    # не перетинали підписів точок усередині поля)
    for I in range(2, 13, 2):
        gx = sx(I)
        p.append(line(gx, oy, gx, oy + 6, color=INK, sw=1.2))
        p.append(text(gx, oy + 20, str(I), size=10, color=MUTED))
    for w in [1, 2, 3, 4, 5, 6]:
        gy = sy(w)
        p.append(line(ox - 6, gy, ox, gy, color=INK, sw=1.2))
        p.append(text(ox - 12, gy + 4, str(w), size=10, color=MUTED, anchor="end"))

    # крива ширина(струм)
    pts = []
    I = 0.3
    while I <= I_max + 0.01:
        pts.append((sx(I), sy(W_of_I(I))))
        I += 0.15
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % pt for pt in pts[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, COPPER))

    # позначити пару точок: 3 А та 6 А (подвоєння струму)
    for I in (3.0, 6.0):
        w = W_of_I(I)
        cx, cy = sx(I), sy(w)
        p.append(circle(cx, cy, 5, fill=POS, stroke="#7a1d13", sw=1.4))
        b, _, _ = textbox(cx + (70 if I == 3.0 else 92), cy - (2 if I == 3.0 else 20),
                          "I=%.0f А\nw≈%.2f мм" % (I, w), size=10, color=INK,
                          fill="#ffffff", stroke=POS, sw=1.0, pad=5)
        p.append(b)

    # виноска про множник ширини
    r36 = W_of_I(6.0) / W_of_I(3.0)
    b, _, _ = textbox(ox + ax_w - 150, oy - ax_h + 34,
                      "×2 струму →\n×%.1f ширини" % r36, size=11, bold=True,
                      color=INK, fill="#fef6f5", stroke=POS, sw=1.3, pad=8)
    p.append(b)

    render(os.path.join(OUT, "trace-width-wall.svg"), W, H, *p)


if __name__ == "__main__":
    fig_via_barrel_unroll()
    fig_trace_width_wall()
    print("figs-proj done:", [f for f in os.listdir(OUT) if 'via-barrel' in f or 'width-wall' in f])
