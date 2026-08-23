# -*- coding: utf-8 -*-
# Фігури саме для вставки proj-discrete-comp.md (окремий генератор, щоб не чіпати figs.py теми).
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math, cmath

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), color, sw, d))


# ── Аналітика ────────────────────────────────────────────────────────────────
def coeffs(wz, wp, dt, K=1.0):
    c = 2.0 / dt
    n0 = K * (1.0 + c / wz); n1 = K * (1.0 - c / wz)
    d0 = 1.0 + c / wp;       d1 = 1.0 - c / wp
    return n0 / d0, n1 / d0, d1 / d0


def fwd_euler(wz, wp, dt, K=1.0):
    a = 1.0 / (wz * dt); b = 1.0 / (wp * dt)
    return K * (1 + a) / (1 + b), K * (-a) / (1 + b), (-b) / (1 + b)


def Hz(b0, b1, a1, w, dt):
    zi = cmath.exp(-1j * w * dt)
    return (b0 + b1 * zi) / (1 + a1 * zi)


def analog_phase(wz, wp, w):
    return math.degrees(math.atan(w / wz) - math.atan(w / wp))


# ── Фігура A: s → z, чому фаза «пливе» лише на верхах (warping) ───────────────
# Зліва: вісь jω у s-площині (рівномірна шкала частоти, 0..π/dt).
# Справа: верхнє півколо одиничного кола в z-площині; білінійне відображає
# усю нескінченну вісь jω у скінченну дугу 0..π — тому верхні частоти стискаються.

def fig_s_to_z():
    W, H = 760, 380
    p = []

    # ── ліва панель: s-площина, уявна вісь ──
    lx = 70
    p.append(text(lx + 60, 52, "s-площина (неперервна)", size=12, color=INK, bold=True))
    axx = lx + 55
    p.append(arrow(axx, 330, axx, 80, color=INK, sw=1.6))          # jω вгору
    p.append(arrow(lx + 10, 300, lx + 150, 300, color=MUTED, sw=1.3))  # σ
    p.append(text(axx + 8, 90, "jω", size=12, color=INK, anchor="start", italic=True))
    p.append(text(lx + 150, 316, "σ", size=11, color=MUTED, anchor="end", italic=True))

    # відмітки частот на осі jω (рівномірно) і маркери
    ys = [300, 250, 200, 150, 110]
    labs = ["0", "ω₁", "ω₂", "ω₃", "→∞"]
    cols = [MUTED, FIELD, FIELD, POS, POS]
    for y, lab, c in zip(ys, labs, cols):
        p.append(circle(axx, y, 4, fill=BG, stroke=c, sw=2.0))
        p.append(text(axx - 10, y + 4, lab, size=10.5, color=c, anchor="end", bold=True))

    # ── стрілка-перехід ──
    p.append(arrow(lx + 165, 205, lx + 235, 205, color=INK, sw=2.2))
    p.append(text(lx + 200, 192, "Tustin", size=11, color=INK, bold=True))
    p.append(text(lx + 200, 226, "z = e^{jωdt}", size=9.5, color=MUTED))

    # ── права панель: z-площина, одиничне коло ──
    cx, cy, R = 560, 205, 110
    p.append(text(cx, 52, "z-площина (дискретна)", size=12, color=INK, bold=True))
    # осі
    p.append(arrow(cx - R - 30, cy, cx + R + 30, cy, color=MUTED, sw=1.3))
    p.append(arrow(cx, cy + R + 30, cx, cy - R - 30, color=MUTED, sw=1.3))
    p.append(text(cx + R + 30, cy + 16, "Re", size=10, color=MUTED, anchor="end"))
    p.append(text(cx + 10, cy - R - 22, "Im", size=10, color=MUTED, anchor="start"))
    # одиничне коло
    p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="2.0"/>'
             % (cx, cy, R, INK))

    # ті самі частоти лягають на дугу 0..π (верхнє півколо); рівні Δω в s
    # стискаються до різних кутів — рівномірна шкала частоти в s стає НЕрівномірною дугою.
    # Кут θ = 2·atan(ω·dt/2) (точне білінійне відображення).
    dt = 0.001
    ws = [0.0, 700.0, 1500.0, 2400.0, 1e9]
    cols2 = [MUTED, FIELD, FIELD, POS, POS]
    labs2 = ["0", "ω₁", "ω₂", "ω₃", "→π"]
    for w, c, lab in zip(ws, cols2, labs2):
        th = 2 * math.atan(w * dt / 2) if w < 1e8 else math.pi
        x = cx + R * math.cos(th)
        y = cy - R * math.sin(th)
        p.append(circle(x, y, 4, fill=BG, stroke=c, sw=2.2))
        ox = 12 if math.cos(th) >= 0 else -12
        an = "start" if math.cos(th) >= 0 else "end"
        p.append(text(x + ox, y + 2, lab, size=10.5, color=c, anchor=an, bold=True))

    # підпис: верхні частоти збиваються до π
    p.append(text(cx, cy + R + 52, "уся нескінченна вісь jω → скінченна дуга 0…π",
                  size=10.5, color=INK, bold=True))
    p.append(text(cx, cy + R + 70, "низи (зелене) майже не стиснуті · верхи (червоне) збиті до π",
                  size=10, color=MUTED))

    render(os.path.join(OUT, "s-to-z-warp.svg"), W, H, *p,
           title="Білінійне: рівномірна вісь частоти стискається в дугу — тому фаза «пливе» лише на верхах")


# ── Фігура B: похибка фази Ейлера проти Tustin зі зростанням кросовера ────────

def fig_euler_vs_tustin():
    W, H = 760, 360
    p = []
    ox, oy = 95, 290
    top = 60
    ax = 600
    Hh = 210
    dt = 0.001
    wnyq = math.pi / dt

    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + ax, oy, color=INK, sw=1.6))
    p.append(text(ox + ax, oy + 18, "частота кросовера / частота Найквіста", size=10.5, color=INK, anchor="end"))
    p.append(text(ox + 6, top + 2, "фаза дискретної ланки на кросовері", size=10.5, color=INK, anchor="start"))

    # ціль (аналог) — 40°, горизонталь
    a = 4.6; sa = math.sqrt(a)
    target = 40.0

    def Yph(ph):  # 0..45° map
        return oy - Hh * (ph / 45.0)

    p.append(line(ox, Yph(target), ox + ax, Yph(target), color=MUTED, sw=1.4, dash="6 4"))
    p.append(text(ox + ax - 4, Yph(target) - 8, "ціль: 40° (аналог)", size=10, color=MUTED, anchor="end", bold=True))

    # шкала X: фракція 0..0.65
    fmax = 0.65

    def X(frac):
        return ox + ax * frac / fmax

    pts_t = []; pts_e = []
    fr = 0.005
    while fr <= fmax:
        wc = fr * wnyq
        z = wc / sa; pl = wc * sa
        bt = coeffs(z, pl, dt)
        be = fwd_euler(z, pl, dt)
        pt = math.degrees(cmath.phase(Hz(*bt, wc, dt)))
        pe = math.degrees(cmath.phase(Hz(*be, wc, dt)))
        pts_t.append((X(fr), Yph(pt)))
        pts_e.append((X(fr), Yph(pe)))
        fr += 0.01
    p.append(polyline(pts_t, color=FIELD, sw=3.0))
    p.append(polyline(pts_e, color=POS, sw=2.8))

    # вертикалі-орієнтири 0.1 і 0.3
    for frac, txt in [(0.1, "1/10"), (0.3, "1/3")]:
        p.append(line(X(frac), top, X(frac), oy, color=MUTED, sw=1.0, dash="3 3"))
        p.append(text(X(frac), oy + 34, txt + " Найквіста", size=9, color=MUTED, bold=True))

    # легенда
    lx = ox + 40
    p.append(line(lx, top + 6, lx + 26, top + 6, color=FIELD, sw=3.0))
    p.append(text(lx + 32, top + 10, "Tustin: тримає ціль майже до Найквіста", size=10, color=FIELD, anchor="start", bold=True))
    p.append(line(lx, top + 26, lx + 26, top + 26, color=POS, sw=2.8))
    p.append(text(lx + 32, top + 30, "Ейлер: фаза тане тим швидше, чим вищий кросовер", size=10, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "euler-vs-tustin-phase.svg"), W, H, *p,
           title="Чому не Ейлер: його запас по фазі на кросовері «пливе» вже від десятої Найквіста")


# ── Фігура C: що код реально зберігає — потік різницевого рівняння + каскад ───

def fig_code_dataflow():
    W, H = 760, 420
    p = []

    # ── верх: один блок як граф сигналу (Direct Form I) ──
    p.append(text(W / 2, 52, "Один блок: що множиться й що зберігається кожен такт", size=12.5, color=INK, bold=True))
    yin = 105
    # вхід e[n]
    p.append(text(70, yin + 4, "e[n]", size=12, color=INK, anchor="middle", italic=True))
    p.append(arrow(95, yin, 165, yin, color=INK, sw=1.8))
    # вузол множення b0
    p.append(circle(180, yin, 14, fill="#eafaf0", stroke=FIELD, sw=2.0))
    p.append(text(180, yin + 4, "b0", size=10, color=FIELD, bold=True))
    # затримка e -> e_prev
    p.append(rect(150, yin + 55, 60, 34, fill="#f6f4ec", stroke=INK, sw=1.6, rx=5))
    p.append(text(180, yin + 77, "z⁻¹", size=12, color=INK, bold=True))
    p.append(text(180, yin + 108, "e_prev", size=9.5, color=MUTED, italic=True))
    p.append(line(120, yin, 120, yin + 72, color=INK, sw=1.4))
    p.append(arrow(120, yin + 72, 150, yin + 72, color=INK, sw=1.4))
    p.append(circle(245, yin + 72, 14, fill="#eafaf0", stroke=FIELD, sw=2.0))
    p.append(text(245, yin + 76, "b1", size=10, color=FIELD, bold=True))
    p.append(arrow(210, yin + 72, 231, yin + 72, color=INK, sw=1.4))

    # суматор
    sx = 360
    p.append(plus(sx, yin, 14))
    p.append(arrow(194, yin, sx - 16, yin, color=INK, sw=1.8))
    p.append(line(245, yin + 58, 245, yin + 14, color=INK, sw=1.4))
    p.append(arrow(245, yin + 14, sx - 12, yin + 8, color=INK, sw=1.4))

    # вихід u[n]
    p.append(arrow(sx + 16, yin, sx + 120, yin, color=INK, sw=1.8))
    p.append(text(sx + 145, yin + 4, "u[n]", size=12, color=INK, anchor="middle", italic=True))

    # зворотний шлях u -> u_prev -> (−a1)
    p.append(line(sx + 90, yin, sx + 90, yin + 72, color=INK, sw=1.4))
    p.append(rect(sx + 60, yin + 55, 60, 34, fill="#f6f4ec", stroke=INK, sw=1.6, rx=5))
    p.append(text(sx + 90, yin + 77, "z⁻¹", size=12, color=INK, bold=True))
    p.append(text(sx + 90, yin + 108, "u_prev", size=9.5, color=MUTED, italic=True))
    p.append(circle(sx - 50, yin + 72, 14, fill="#fdecea", stroke=POS, sw=2.0))
    p.append(text(sx - 50, yin + 76, "−a1", size=9, color=POS, bold=True))
    p.append(line(sx + 60, yin + 72, sx - 36, yin + 72, color=INK, sw=1.4))
    p.append(arrow(sx - 50, yin + 58, sx - 50, yin + 14, color=INK, sw=1.4))
    p.append(line(sx - 50, yin + 58, sx - 50, yin + 72, color=INK, sw=1.4))
    p.append(arrow(sx - 36, yin, sx - 16, yin + 6, color=INK, sw=1.4))

    p.append(text(W / 2, yin + 140, "стан = два числа (e_prev, u_prev); решта — три множення й додавання",
                  size=10, color=MUTED))

    # ── низ: каскад lag → lead ──
    yc = 330
    p.append(text(W / 2, yc - 40, "Каскад: lag живить lead, кожен — свій блок зі своїм станом",
                  size=12.5, color=INK, bold=True))
    p.append(text(70, yc + 4, "e", size=12, color=INK, anchor="middle", italic=True))
    p.append(arrow(85, yc, 150, yc, color=INK, sw=1.8))
    # LAG
    p.append(fitbox(150, yc - 30, 150, 60, "", fill="#eef2fb", stroke=NEG, sw=2.0))
    p.append(text(225, yc - 8, "LAG", size=12, color=NEG, bold=True))
    p.append(text(225, yc + 12, "точність на низах", size=9, color=INK))
    p.append(arrow(300, yc, 360, yc, color=INK, sw=1.8))
    p.append(text(330, yc - 8, "проміжне", size=8.5, color=MUTED, italic=True))
    # LEAD
    p.append(fitbox(360, yc - 30, 150, 60, "", fill="#eafaf0", stroke=FIELD, sw=2.0))
    p.append(text(435, yc - 8, "LEAD", size=12, color=FIELD, bold=True))
    p.append(text(435, yc + 12, "фаза на кросовері", size=9, color=INK))
    p.append(arrow(510, yc, 575, yc, color=INK, sw=1.8))
    p.append(text(605, yc + 4, "u", size=12, color=INK, anchor="middle", italic=True))
    p.append(arrow(620, yc, 690, yc, color=INK, sw=1.8))
    p.append(text(690, yc - 10, "насич.", size=9, color=POS, anchor="middle", bold=True))
    p.append(text(690, yc + 18, "[u_min,u_max]", size=8.5, color=POS, anchor="middle"))

    render(os.path.join(OUT, "code-dataflow.svg"), W, H, *p,
           title="Дискретний компенсатор у пам'яті: один блок і каскад двох блоків")


if __name__ == "__main__":
    fig_s_to_z()
    fig_euler_vs_tustin()
    fig_code_dataflow()
    print("OK: proj figures written to", OUT)
