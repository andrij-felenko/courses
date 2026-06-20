# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: величина тремтить навколо рівноваги ────────────────────────────
# Хаотичний тепловий рух → величина (заряд, напруга, положення) безперервно
# гойдається навколо рівноважного значення. Середнє = рівновага (нуль добавки),
# розкид = σ. Ідея, яку важко словами: «спокою немає, є лише середній спокій» —
# миттєве значення майже ніколи не дорівнює середньому, але тримається в поясі ±σ.
def fig_jitter():
    W, H = 660, 360
    ox, oy = 70, 40            # лівий-верхній кут поля графіка
    gw, gh = 520, 240          # розміри поля
    base = oy + gh / 2         # рівень середнього (рівноваги) — посередині
    sigma_px = 58              # σ у пікселях (пів-ширина пояса)

    # псевдовипадкова доріжка (детермінована, щоб фігура була відтворна)
    import random
    random.seed(7)
    N = 150
    xs = [ox + i / (N - 1) * gw for i in range(N)]
    # сума незалежних поштовхів, утримувана біля нуля легким поверненням (як у пастці)
    v, ys = 0.0, []
    for i in range(N):
        v += random.uniform(-1, 1) * 18 - 0.18 * v      # поштовх + повернення до 0
        v = max(-1.9 * sigma_px, min(1.9 * sigma_px, v))
        ys.append(base - v)

    p = []

    # пояс ±σ (зелене поле — «типовий» розкид)
    p.append(rect(ox, base - sigma_px, gw, 2 * sigma_px,
                  fill=FIELD, stroke="none", sw=0, rx=0).replace('fill="%s"' % FIELD,
                  'fill="%s" fill-opacity="0.12"' % FIELD))

    # вісь часу та рамка поля
    p.append(line(ox, oy, ox, oy + gh, color=MUTED, sw=1.2))           # вісь величини
    p.append(line(ox, oy + gh, ox + gw + 14, oy + gh, color=MUTED, sw=1.2))
    p.append(arrow(ox + gw + 2, oy + gh, ox + gw + 16, oy + gh, color=MUTED, sw=1.2))
    p.append(text(ox + gw + 20, oy + gh + 4, "час", 12, MUTED, "start", italic=True))
    p.append(text(ox - 12, oy + 10, "величина", 12, MUTED, "end", italic=True))

    # лінія середнього (рівноваги)
    p.append(line(ox, base, ox + gw, base, color=FIELD, sw=2, dash="7 5"))
    p.append(text(ox + gw - 2, base - 8, "середнє = рівновага", 12, FIELD, "end", bold=True))

    # межі ±σ
    p.append(line(ox, base - sigma_px, ox + gw, base - sigma_px, color=POS, sw=1.2, dash="3 4"))
    p.append(line(ox, base + sigma_px, ox + gw, base + sigma_px, color=NEG, sw=1.2, dash="3 4"))
    p.append(text(ox + 6, base - sigma_px - 6, "+σ", 12, POS, "start", bold=True))
    p.append(text(ox + 6, base + sigma_px + 14, "−σ", 12, NEG, "start", bold=True))

    # сама доріжка флуктуацій
    pts = " ".join("%.1f,%.1f" % (xs[i], ys[i]) for i in range(N))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (pts, INK))

    # стрілка ширини пояса 2σ
    ax = ox + gw * 0.16
    p.append(line(ax, base - sigma_px, ax, base + sigma_px, color=MUTED, sw=1.2))
    p.append(arrow(ax, base - sigma_px + 1, ax, base - sigma_px - 8, color=MUTED, sw=1.2))
    p.append(arrow(ax, base + sigma_px - 1, ax, base + sigma_px + 8, color=MUTED, sw=1.2))
    p.append(text(ax + 8, base + 4, "2σ", 11, MUTED, "start"))

    p.append(text(W / 2, H - 8,
                  "Миттєве значення майже ніколи не дорівнює середньому — але тримається в поясі ±σ.",
                  10.5, MUTED, "middle"))

    render(os.path.join(OUT, "jitter.svg"), W, H, *p,
           title="Теплова величина гойдається навколо рівноваги")


# ── Фігура 2: чому масштаб ~kT — пастка-парабола й заповнення на висоту kT ────
# Енергія відхилення квадратична: E(x) = ½·κ·x² (парабола). Тепло наливає в цю
# чашу енергію масштабу kT; рівень kT відсікає смугу дозволених x — це і є розкид.
# Гарячіше (вищий kT) → ширша смуга → більша σ. Жорсткіша пастка (крутіша
# парабола) → вужча смуга за того самого kT. Звідси σ² ∝ kT/κ.
def fig_well():
    W, H = 660, 380
    ox, oy = 80, 56
    gw, gh = 500, 250
    cx = ox + gw / 2           # дно пастки (x = рівновага)
    floor = oy + gh            # рівень нульової енергії

    # парабола E = a·(x−cx)²; підберемо a так, щоб гілки дійшли до верху поля
    a = (gh) / ((gw / 2) ** 2)
    def ey(x): return floor - a * (x - cx) ** 2          # y-екран від x-екран

    # рівень kT (де парабола = kT) — горизонталь, що відсікає смугу
    kT_h = gh * 0.42                                       # висота рівня kT над дном
    half = math.sqrt(kT_h / a)                            # пів-ширина смуги при цьому рівні

    p = []

    # осі
    p.append(line(ox, oy - 6, ox, floor, color=MUTED, sw=1.2))         # вісь енергії
    p.append(arrow(ox, oy + 4, ox, oy - 10, color=MUTED, sw=1.2))
    p.append(text(ox - 8, oy - 2, "енергія", 12, MUTED, "end", italic=True))
    p.append(line(ox - 6, floor, ox + gw + 14, floor, color=MUTED, sw=1.2))   # вісь x
    p.append(arrow(ox + gw + 2, floor, ox + gw + 16, floor, color=MUTED, sw=1.2))
    p.append(text(ox + gw + 20, floor + 4, "відхилення x", 12, MUTED, "start", italic=True))
    p.append(text(cx, floor + 20, "0", 11, MUTED))

    # заливка «налитої» теплової енергії до рівня kT
    fillpts = []
    x = cx - half
    while x <= cx + half:
        fillpts.append("%.1f,%.1f" % (x, ey(x)))
        x += 2
    fillpts.append("%.1f,%.1f" % (cx + half, floor - kT_h))
    fillpts.append("%.1f,%.1f" % (cx - half, floor - kT_h))
    p.append('<polygon points="%s" fill="%s" fill-opacity="0.16" stroke="none"/>' % (" ".join(fillpts), POS))

    # сама парабола E(x)
    cur = []
    x = ox + 2
    while x <= ox + gw - 2:
        y = ey(x)
        if y >= oy - 2:
            cur.append("%.1f,%.1f" % (x, y))
        x += 2
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(cur), INK))
    p.append(text(ox + gw - 6, oy + 24, "E = ½·κ·x²", 12, INK, "end", italic=True))

    # рівень kT
    yk = floor - kT_h
    p.append(line(ox, yk, cx + half, yk, color=POS, sw=1.8, dash="6 4"))
    p.append(text(ox + 6, yk - 7, "рівень теплової енергії ~ kT", 12, POS, "start", bold=True))

    # відсічена смуга дозволених x (= розкид)
    p.append(line(cx - half, floor, cx - half, yk, color=NEG, sw=1.3, dash="3 4"))
    p.append(line(cx + half, floor, cx + half, yk, color=NEG, sw=1.3, dash="3 4"))
    p.append(line(cx - half, floor + 30, cx + half, floor + 30, color=NEG, sw=1.4))
    p.append(arrow(cx - half + 1, floor + 30, cx - half - 8, floor + 30, color=NEG, sw=1.4))
    p.append(arrow(cx + half - 1, floor + 30, cx + half + 8, floor + 30, color=NEG, sw=1.4))
    p.append(text(cx, floor + 46, "ширина розкиду ~ √(kT/κ)", 12, NEG, "middle", bold=True))

    p.append(text(W / 2, H - 8,
                  "Тепло наливає в чашу енергію масштабу kT; рівень kT задає смугу x — це й є розкид.",
                  10.5, MUTED, "middle"))

    render(os.path.join(OUT, "well.svg"), W, H, *p,
           title="Чому масштаб флуктуацій — kT: чаша енергії, налита до kT")


# ── Фігура 3: дисперсія росте лінійно з температурою ─────────────────────────
# σ² ∝ T — пряма через початок координат. Холоднішає → менший розкид; при T→0
# флуктуації завмирають. Прямий місток до Найквіста: потужність шуму ∝ T.
def fig_variance_vs_t():
    W, H = 620, 360
    ox, oy = 78, 50
    gw, gh = 470, 230
    x0, y0 = ox, oy + gh        # початок координат (T=0, σ²=0)

    # пряма σ² = c·T
    Tmax = 1.0
    def px(T): return x0 + T / Tmax * gw
    def py(var): return y0 - var * gh        # var у частках максимуму [0..1]

    p = []

    # осі
    p.append(line(x0, oy - 6, x0, y0, color=MUTED, sw=1.3))
    p.append(arrow(x0, oy + 2, x0, oy - 12, color=MUTED, sw=1.3))
    p.append(line(x0 - 6, y0, x0 + gw + 14, y0, color=MUTED, sw=1.3))
    p.append(arrow(x0 + gw + 2, y0, x0 + gw + 16, y0, color=MUTED, sw=1.3))
    p.append(text(x0 + gw + 20, y0 + 4, "T (К)", 12, MUTED, "start", italic=True))
    p.append(text(x0 - 10, oy - 2, "σ²  (дисперсія, ∝ потужність)", 12, MUTED, "end", italic=True))
    p.append(text(x0 - 8, y0 + 16, "0", 11, MUTED, "end"))

    # сама пряма через нуль
    p.append(line(px(0), py(0), px(1.0), py(0.92), color=INK, sw=2.6))
    p.append(text(px(1.0) - 4, py(0.92) - 8, "σ² = c·T", 13, INK, "end", italic=True, bold=True))

    # дві контрольні точки: холодно vs гаряче
    for T, lab, col in [(0.32, "холодно", NEG), (0.82, "гаряче", POS)]:
        vy = 0.92 * T
        p.append(line(px(T), y0, px(T), py(vy), color=col, sw=1.2, dash="4 4"))
        p.append(line(x0, py(vy), px(T), py(vy), color=col, sw=1.2, dash="4 4"))
        p.append(circle(px(T), py(vy), 5, fill=col, stroke=col, sw=1))
        p.append(text(px(T), y0 + 16, lab, 11, col, "middle", bold=True))

    # позначка абсолютного нуля
    p.append(circle(px(0), py(0), 4, fill=FIELD, stroke=FIELD, sw=1))
    p.append(text(px(0) + 8, py(0) + 18, "T = 0: розкид завмирає", 11, FIELD, "start"))

    p.append(text(W / 2, H - 8,
                  "Дисперсія флуктуацій пряма за температурою — тому потужність теплового шуму ∝ T.",
                  10.5, MUTED, "middle"))

    render(os.path.join(OUT, "variance-vs-t.svg"), W, H, *p,
           title="Дисперсія росте лінійно з температурою")


if __name__ == "__main__":
    fig_jitter()
    fig_well()
    fig_variance_vs_t()
    print("Done.")
