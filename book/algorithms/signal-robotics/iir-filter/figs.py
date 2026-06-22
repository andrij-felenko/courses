# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── structure: пряма гілка входів + зворотна гілка виходів ────────────────────
# Ідея: суматор у центрі; зліва зважена сума входів (як КІХ), справа петля, що
# повертає попередні виходи назад у суматор — саме вона відрізняє БІХ.

def fig_structure():
    W, H = 720, 340
    p = []
    cx, cy = 470, 120                     # суматор
    sr = 22
    # суматор
    p.append(circle(cx, cy, sr, fill="#f6f4ec", stroke=INK, sw=2))
    p.append(text(cx, cy + 6, "Σ", size=20, color=INK, bold=True))
    p.append(text(cx + sr + 4, cy - sr - 4, "y[n]", size=12, color=INK, anchor="start", bold=True, italic=True))

    # вхід x[n] зліва
    p.append(text(60, cy + 5, "x[n]", size=12, color=INK, anchor="start", bold=True, italic=True))
    p.append(arrow(96, cy, cx - sr - 2, cy, color=INK, sw=1.7))
    p.append(text((96 + cx) / 2, cy - 10, "b₀, b₁ … (входи)", size=11, color=NEG))

    # пряма гілка — два затримані входи, що підсумовуються
    p.append(text((96 + cx) / 2, cy + 22, "пряма гілка = зважена сума входів (як КІХ)",
                  size=10, color=MUTED))

    # вихід вправо
    p.append(line(cx + sr, cy, 660, cy, color=INK, sw=1.7))
    p.append(arrow(660, cy, 690, cy, color=INK, sw=1.7))

    # зворотна гілка: відгалуження від виходу вниз, через затримки, назад у Σ
    bx = 620
    by = 250
    p.append(circle(bx, cy, 3.2, fill=INK, stroke=INK, sw=1))      # точка відгалуження
    p.append(line(bx, cy, bx, by, color=POS, sw=1.7))
    # блоки затримки z⁻¹
    d1 = textbox(cx + 60, by, "z⁻¹\ny[n−1]", size=11, fill="#fdecea", stroke=POS, sw=1.6, color=POS)
    d2 = textbox(cx - 70, by, "z⁻¹\ny[n−2]", size=11, fill="#fdecea", stroke=POS, sw=1.6, color=POS)
    p.append(line(bx, by, cx + 60 + 30, by, color=POS, sw=1.7))
    p.append(d1[0])
    p.append(arrow(cx + 60 - d1[1] / 2, by, cx - 70 + d2[1] / 2, by, color=POS, sw=1.7))
    p.append(d2[0])
    # назад у суматор знизу
    upx = cx - 70 - d2[1] / 2
    p.append(line(upx, by, upx, cy + sr + 24, color=POS, sw=1.7))
    p.append(arrow(upx, cy + sr + 24, cx - 4, cy + sr + 2, color=POS, sw=1.7))
    p.append(text((bx + upx) / 2, by + 22, "−a₁, −a₂ … (попередні ВИХОДИ)", size=11, color=POS))
    p.append(text((bx + upx) / 2, by + 38, "зворотна гілка — петля від виходу назад у вхід",
                  size=10, color=MUTED))

    render(os.path.join(OUT, "structure.svg"), W, H, *p,
           title="БІХ: пряма гілка входів + зворотна гілка власних виходів")


# ── impulse: реакція БІХ згасає вічно (КІХ обривається) ───────────────────────
# Ідея: на одиничний імпульс БІХ (EMA) дає спадну геометрію, що НІКОЛИ не нуль;
# КІХ для порівняння — рівно нуль після M+1 відліків.

def fig_impulse():
    W, H = 720, 320
    ox, oy = 70, 250
    aw, ah = 600, 196
    p = []
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "n (відліки)", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 12, oy - ah - 2, "вихід", size=11, color=INK, anchor="end", italic=True))

    n = 16
    dx = aw / (n + 1)
    a = 0.3                                # EMA α
    # КІХ для порівняння: ненульовий лише перші M+1 = 5 відліків (плаский)
    M = 4
    for i in range(n):
        x = ox + (i + 1) * dx
        if i <= M:
            hf = ah * 0.20
            p.append(rect(x - 6, oy - hf, 5, hf, fill="#e7eee9", stroke=FIELD, sw=1.0, rx=0))
    # БІХ — геометрія α(1−α)^n, ніколи не нуль
    for i in range(n):
        x = ox + (i + 1) * dx
        h = ah * (a * (1 - a) ** i) / a * 0.92   # нормуємо: перший стовпчик майже на всю висоту
        p.append(rect(x, oy - h, 5, h, fill="#fdecea", stroke=POS, sw=1.2, rx=0))
        p.append(circle(x + 2.5, oy - h, 2.4, fill=POS, stroke=POS, sw=1))

    # пунктир «хвіст ніколи не нуль»
    p.append(text(ox + aw * 0.62, oy - ah * 0.30, "хвіст згасає, та не доходить до нуля",
                  size=11, color=POS))
    p.append(text(ox + aw * 0.62, oy - ah * 0.30 + 16, "— реакція нескінченна",
                  size=11, color=POS))

    # легенда
    p.append(rect(ox + 16, oy - ah + 6, 12, 12, fill="#fdecea", stroke=POS, sw=1.2, rx=0))
    p.append(text(ox + 34, oy - ah + 16, "БІХ (EMA, α=0.3): згасає вічно",
                  size=11, color=POS, anchor="start", bold=True))
    p.append(rect(ox + 16, oy - ah + 26, 12, 12, fill="#e7eee9", stroke=FIELD, sw=1.2, rx=0))
    p.append(text(ox + 34, oy - ah + 36, "КІХ (M=4): рівно нуль після M+1 кроків",
                  size=11, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "impulse.svg"), W, H, *p,
           title="Звідки назва: реакція на імпульс згасає, але не обривається")


# ── efficiency: та сама гострота — багато коефіцієнтів КІХ vs кілька БІХ ───────
# Ідея: дві майже однакові АЧХ ФНЧ; КІХ набирає крутість 64 коеф., БІХ — 5.

def fig_efficiency():
    W, H = 700, 320
    ox, oy = 70, 250
    aw, ah = 580, 196
    p = []
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "частота", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 12, oy - ah - 2, "|H|", size=11, color=INK, anchor="end", italic=True))

    fc = 0.42
    def resp(steep):
        pts = []
        for i in range(0, 401):
            f = i / 400.0
            v = 1.0 / (1.0 + (f / fc) ** (2 * steep))
            v = math.sqrt(v)
            pts.append("%.1f,%.1f" % (ox + f * aw, oy - v * ah * 0.9))
        return pts
    # майже однакові криві — обидві гострі
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join(resp(7)), FIELD))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-dasharray="6 4" stroke-linejoin="round"/>' % (" ".join(resp(7.4)), NEG))

    p.append(line(ox + 30, oy - ah + 8, ox + 56, oy - ah + 8, color=FIELD, sw=2.6))
    p.append(text(ox + 62, oy - ah + 12, "КІХ — 64 коефіцієнти",
                  size=11, color=FIELD, anchor="start", bold=True))
    p.append(line(ox + 30, oy - ah + 28, ox + 56, oy - ah + 28, color=NEG, sw=2.4, dash="6 4"))
    p.append(text(ox + 62, oy - ah + 32, "БІХ — 5 коефіцієнтів",
                  size=11, color=NEG, anchor="start", bold=True))
    p.append(text(ox + aw * 0.6, oy - ah * 0.18, "однаково гострий зріз —",
                  size=11, color=MUTED, anchor="middle"))
    p.append(text(ox + aw * 0.6, oy - ah * 0.18 + 15, "удесятеро менше арифметики",
                  size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "efficiency.svg"), W, H, *p,
           title="Та сама крутість: КІХ — десятки коефіцієнтів, БІХ — одиниці")


# ── stability: той самий БІХ — згасає чи вибухає ──────────────────────────────
# Ідея: дві реакції на імпульс; стабільна спадає, нестабільна наростає й злітає.

def fig_stability():
    W, H = 700, 320
    ox, oy = 70, 250
    aw, ah = 580, 196
    p = []
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "n (відліки)", size=11, color=INK, italic=True, anchor="end"))

    n = 18
    dx = aw / (n + 1)
    # стабільний: згасальне коливання
    for i in range(n):
        x = ox + (i + 1) * dx
        v = math.exp(-0.28 * i) * math.cos(0.9 * i)
        h = v * ah * 0.42
        p.append(circle(x, oy - ah * 0.42 * 0 - h - 0, 0, fill=FIELD, stroke=FIELD, sw=0))
    # лінія стабільного
    pts = []
    for i in range(n):
        x = ox + (i + 1) * dx
        v = math.exp(-0.28 * i) * math.cos(0.9 * i)
        pts.append("%.1f,%.1f" % (x, oy - 0 - v * ah * 0.40 - ah * 0.0))
    # зсунемо стабільну криву вгору від осі, щоб не плуталась
    base_s = oy - ah * 0.16
    pts = []
    for i in range(n):
        x = ox + (i + 1) * dx
        v = math.exp(-0.30 * i) * math.cos(0.9 * i)
        pts.append("%.1f,%.1f" % (x, base_s - v * ah * 0.20))
    p.append(line(ox, base_s, ox + aw, base_s, color=MUTED, sw=1.0, dash="3 3"))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (" ".join(pts), FIELD))
    for s in pts:
        xx, yy = s.split(",")
        p.append(circle(float(xx), float(yy), 2.4, fill=FIELD, stroke=FIELD, sw=1))
    p.append(text(ox + aw * 0.5, base_s + 2, "стабільний: реакція згасає",
                  size=11, color=FIELD, anchor="middle", bold=True))

    # нестабільний: наростальне коливання, що вилітає вгору
    base_u = oy - ah * 0.62
    ptu = []
    for i in range(n):
        x = ox + (i + 1) * dx
        v = (1.32 ** i) * math.cos(0.9 * i) * 0.12
        yy = base_u - v * ah * 0.20
        yy = max(oy - ah + 4, yy)          # не вище полотна
        ptu.append("%.1f,%.1f" % (x, yy))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join(ptu), POS))
    p.append(text(ox + aw * 0.30, oy - ah + 18, "нестабільний: наростає й «вибухає»",
                  size=11, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "stability.svg"), W, H, *p,
           title="Та сама петля: правильні коефіцієнти згасають, завеликі — розганяються")


# ── biquad: ланка 2-го порядку + каскад ───────────────────────────────────────
# Ідея: один біквад = 5 коефіцієнтів; складний фільтр = ланцюжок біквадів.

def fig_biquad():
    W, H = 720, 300
    p = []
    # один біквад — рамка з формулою
    bx, by = 360, 95
    box, bw, bh = textbox(bx, by, "y = b₀x + b₁x₋₁ + b₂x₋₂ − a₁y₋₁ − a₂y₋₂",
                          size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=14)
    p.append(box)
    p.append(text(bx, by - bh / 2 - 10, "біквад — БІХ 2-го порядку: 5 коефіцієнтів, ~5 множень",
                  size=11, color=MUTED))

    # каскад чотирьох біквадів = 8-й порядок
    y = 215
    n = 4
    cw, ch = 96, 50
    gap = 36
    total = n * cw + (n - 1) * gap
    x = (W - total) / 2
    p.append(text(W / 2, y - ch / 2 - 16, "складніший фільтр = каскад біквадів (вихід одного → вхід наступного)",
                  size=11, color=INK, bold=True))
    cxs = []
    for i in range(n):
        b = fitbox(x, y - ch / 2, cw, ch, "біквад %d" % (i + 1), size=12,
                   fill="#eef4ff", stroke=NEG, sw=1.6, bold=True, color=NEG)
        p.append(b)
        cxs.append((x, x + cw))
        if i > 0:
            p.append(arrow(cxs[i - 1][1], y, x - 2, y, color=INK, sw=1.7))
        x += cw + gap
    p.append(arrow(cxs[-1][1], y, cxs[-1][1] + 26, y, color=INK, sw=1.7))
    p.append(text(W / 2, y + ch / 2 + 22, "чотири біквади поспіль = фільтр 8-го порядку — стійкіший за одну довгу формулу",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "biquad.svg"), W, H, *p,
           title="Біквад — цеглинка БІХ; складне будують каскадом")


# ── phase: лінійна фаза КІХ зберігає форму, БІХ — спотворює ────────────────────
# Ідея: той самий складений сигнал; КІХ зсуває цілком (форма та сама), БІХ зсуває
# частоти по-різному → форма «перекособочена».

def fig_phase():
    W, H = 720, 340
    p = []
    span = 4 * math.pi
    aw = 600
    ox = 70

    def draw(yc, fn, color, label, lab_col):
        pts = []
        for i in range(0, 481):
            t = span * i / 480.0
            pts.append("%.1f,%.1f" % (ox + (t / span) * aw, yc - fn(t) * 36))
        p.append(line(ox, yc, ox + aw, yc, color=MUTED, sw=1.0, dash="3 3"))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
                 'stroke-linejoin="round"/>' % (" ".join(pts), color))
        p.append(text(ox, yc - 52, label, size=11, color=lab_col, anchor="start", bold=True))

    # вихідний складений сигнал: основна + третя гармоніка
    def base(t):
        return math.sin(t) + 0.5 * math.sin(3 * t)
    # КІХ: зсув обох гармонік на однаковий час (форма зберігається)
    sh = 0.6
    def fir(t):
        return math.sin(t - sh) + 0.5 * math.sin(3 * (t - sh))
    # БІХ: гармоніки зсунуті на РІЗНИЙ час → форма змінюється
    def iir(t):
        return math.sin(t - sh) + 0.5 * math.sin(3 * t - 2.6)

    draw(80, base, INK, "вхідний сигнал (основна + 3-я гармоніка)", INK)
    draw(190, fir, FIELD, "після лінійно-фазового КІХ — та сама форма, лише зсунута", FIELD)
    draw(300, iir, POS, "після БІХ — форма спотворена (частоти зсунуті по-різному)", POS)

    render(os.path.join(OUT, "phase.svg"), W, H, *p,
           title="Плата за петлю: КІХ береже форму, БІХ її спотворює")


if __name__ == "__main__":
    fig_structure()
    fig_impulse()
    fig_efficiency()
    fig_stability()
    fig_biquad()
    fig_phase()
    print("OK: figures written to", OUT)
