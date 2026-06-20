# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: середнє як центр ваги ───────────────────────────────────────────
# Відліки — однакові тягарці на лінійці в точках своїх значень. Точка опори
# стоїть рівно під середнім: моменти зліва = моменти справа. Один далекий відлік
# помітно тягне опору до себе. Ідея, яку важко передати словами: середнє — це
# точка балансу, і вона чутлива до викидів.
def fig_balance_mean():
    W, H = 640, 320
    ox = 70            # x для значення 0
    sx = 52            # px на одиницю значення
    base = 150         # y лінійки

    def gx(v): return ox + v * sx

    vals = [1.0, 2.0, 2.5, 3.0, 8.0]      # один далекий відлік (8) тягне центр
    mean = sum(vals) / len(vals)          # = 3.3

    p = []
    p.append(text(W / 2, 30, "Середнє — точка балансу лінійки з тягарцями",
                  16, INK, "middle", bold=True))

    # шкала значень під лінійкою
    for v in range(0, 10):
        p.append(line(gx(v), base, gx(v), base + 5, color=MUTED, sw=1))
        p.append(text(gx(v), base + 19, str(v), 10, MUTED, "middle"))

    # лінійка
    p.append(line(gx(-0.3), base, gx(9.3), base, color=INK, sw=3))

    # тягарці (однакові) у точках значень
    for v in vals:
        far = (v > 5)
        col = POS if far else NEG
        fill = "#fdecea" if far else "#eaf0fd"
        p.append('<rect x="%.1f" y="%.1f" width="20" height="26" rx="3" '
                 'fill="%s" stroke="%s" stroke-width="1.6"/>'
                 % (gx(v) - 10, base - 28, fill, col))
        p.append(line(gx(v), base, gx(v), base - 2, color=col, sw=1))

    # опора-трикутник рівно під середнім
    mx = gx(mean)
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" stroke="%s" '
             'stroke-width="1.4"/>' % (mx, base + 4, mx - 16, base + 40,
                                       mx + 16, base + 40, FIELD, "#1e7d46"))
    p.append(text(mx, base + 62, "опора = середнє", 12, "#1e7d46", "middle", bold=True))
    p.append(text(mx, base + 78, "x̄ = 3.3", 12, INK, "middle"))

    # позначити далекий відлік як викид
    p.append(fitbox(gx(8) - 70, base - 92, 150, 36,
                    "далекий відлік тягне\nопору до себе",
                    size=11, fill="#fdecea", stroke=POS, color=INK))
    p.append(line(gx(8), base - 56, gx(8), base - 30, color=POS, sw=1, dash="2 2"))

    render(os.path.join(OUT, "balance-mean.svg"), W, H, *p)


# ── Фігура 2: ковзне вікно над потоком ────────────────────────────────────────
# Зашумлений вхідний ряд; вікно з N відліків охоплює останні N і дає ОДНУ точку
# згладженого виходу. Нижче — гладша вихідна крива. Ідея: операція над усім
# сигналом (ряд→ряд), тремтіння осідає у взаємному погашенні всередині вікна.
def fig_moving_window():
    import random
    random.seed(7)
    W, H = 660, 420
    ox = 60
    sx = 11.2          # px на відлік
    n = 50
    win = 9

    # вхід: плавний підйом + шум
    base_in = 120
    amp = 46
    def signal(i): return 0.5 + 0.5 * math.sin((i / n) * math.pi * 1.1)   # 0..1 плавно
    noise = [random.uniform(-0.22, 0.22) for _ in range(n)]
    xin = [signal(i) + noise[i] for i in range(n)]

    def gx(i): return ox + i * sx
    def gy_in(v):  return base_in - (v - 0.5) * amp
    def gy_out(v): return base_in + 150 - (v - 0.5) * amp

    p = []
    p.append(text(W / 2, 28, "Ковзне вікно: ряд на вході — згладжений ряд на виході",
                  15, INK, "middle", bold=True))

    # ── верх: вхідний зашумлений ряд
    p.append(text(ox - 6, base_in - amp / 2 - 14, "вхід (зашумлений)", 12, MUTED, "start"))
    pts_in = " ".join("%.1f,%.1f" % (gx(i), gy_in(xin[i])) for i in range(n))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4"/>'
             % (pts_in, MUTED))
    for i in range(n):
        p.append(circle(gx(i), gy_in(xin[i]), 1.8, fill=MUTED, stroke="none", sw=0))

    # вікно з N відліків (підсвічене) у середині ряду
    wc = 30                                 # права межа вікна (індекс)
    wl = wc - win + 1
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" '
             'fill="#eafff3" fill-opacity="0.7" stroke="%s" stroke-width="1.6"/>'
             % (gx(wl) - 4, base_in - amp / 2 - 6, (win - 1) * sx + 8, amp + 12, FIELD))
    p.append(text(gx(wc) - (win - 1) * sx / 2, base_in - amp / 2 - 14 + amp + 26,
                  "вікно з N відліків", 11, "#1e7d46", "middle", bold=True))

    # ── вихід: ковзне середнє
    out = []
    for i in range(n):
        lo = max(0, i - win + 1)
        out.append(sum(xin[lo:i + 1]) / (i - lo + 1))
    p.append(text(ox - 6, gy_out(0.5) - amp / 2 - 14, "вихід (згладжений)", 12, FIELD, "start"))
    pts_out = " ".join("%.1f,%.1f" % (gx(i), gy_out(out[i])) for i in range(n))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (pts_out, FIELD))

    # одна точка виходу, що відповідає підсвіченому вікну
    p.append(circle(gx(wc), gy_out(out[wc]), 4.5, fill=FIELD, stroke="#1e7d46", sw=1.4))
    # стрілка від вікна вниз до цієї точки
    p.append(arrow(gx(wc) - (win - 1) * sx / 2, base_in - amp / 2 - 6 + amp + 34,
                   gx(wc), gy_out(out[wc]) - 8, color=MUTED, sw=1.4))
    p.append(text(gx(wc) + 8, gy_out(out[wc]) + 4, "одна точка виходу", 11, "#1e7d46", "start"))

    p.append(text(W / 2, H - 12,
                  "Тремтіння осідає у взаємному погашенні всередині кожного вікна.",
                  10.5, MUTED, "middle"))

    render(os.path.join(OUT, "moving-window.svg"), W, H, *p)


# ── Фігура 3: згладження проти затримки ───────────────────────────────────────
# Один різкий стрибок входу під двома вікнами. Коротке: наздоганяє швидко, та
# лишає тремтіння. Довге: гладке, але наздоганяє пізно (видима затримка).
# Ідея: краще й швидше водночас не буває — це центральний компроміс.
def fig_smoothing_lag():
    import random
    random.seed(3)
    W, H = 660, 420
    ox = 64
    sx = 11.0
    n = 52
    step_at = 20

    # вхід: сходинка з 0.25 до 0.8 + шум
    def base_sig(i): return 0.25 if i < step_at else 0.8
    noise = [random.uniform(-0.07, 0.07) for _ in range(n)]
    xin = [base_sig(i) + noise[i] for i in range(n)]

    def gx(i): return ox + i * sx

    def panel(cy, win, label, lagnote):
        f = []
        amp = 80
        def gy(v): return cy - (v - 0.5) * amp
        # ідеальна сходинка (пунктир) — орієнтир
        f.append(line(gx(0), gy(0.25), gx(step_at), gy(0.25), color=MUTED, sw=1.2, dash="4 3"))
        f.append(line(gx(step_at), gy(0.25), gx(step_at), gy(0.8), color=MUTED, sw=1.2, dash="4 3"))
        f.append(line(gx(step_at), gy(0.8), gx(n - 1), gy(0.8), color=MUTED, sw=1.2, dash="4 3"))
        # вхід (тонкий сірий)
        pin = " ".join("%.1f,%.1f" % (gx(i), gy(xin[i])) for i in range(n))
        f.append('<polyline points="%s" fill="none" stroke="#c7ccd3" stroke-width="1.2"/>' % pin)
        # ковзне середнє цим вікном
        out = []
        for i in range(n):
            lo = max(0, i - win + 1)
            out.append(sum(xin[lo:i + 1]) / (i - lo + 1))
        pout = " ".join("%.1f,%.1f" % (gx(i), gy(out[i])) for i in range(n))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pout, NEG))
        # позначка моменту сходинки
        f.append(line(gx(step_at), gy(0.95), gx(step_at), gy(0.05), color=POS, sw=1.2, dash="2 3"))
        # де вихід досяг половини підйому — груба міра затримки
        target = 0.25 + 0.5 * (0.8 - 0.25)
        reach = step_at
        for i in range(step_at, n):
            if out[i] >= target:
                reach = i
                break
        f.append(arrow(gx(step_at), gy(target), gx(reach), gy(target), color="#1e7d46", sw=1.6))
        f.append(text(gx(reach) + 6, gy(target) - 6, lagnote, 11, "#1e7d46", "start", bold=True))
        # підпис панелі
        f.append(text(ox, cy - amp / 2 - 16, label, 13, INK, "start", bold=True))
        return f

    p = []
    p.append(text(W / 2, 26, "Згладження проти затримки: один стрибок, два вікна",
                  15, INK, "middle", bold=True))
    p += panel(120, 4,  "коротке вікно — швидке, але тремтить", "наздоганяє швидко")
    p += panel(300, 16, "довге вікно — гладке, але запізнюється", "наздоганяє пізно")

    # легенда
    p.append(text(W - 16, 120 - 56, "пунктир — ідеальна сходинка", 10, MUTED, "end"))
    p.append(text(W - 16, 120 - 42, "червона риска — момент стрибка", 10, POS, "end"))

    p.append(text(W / 2, H - 12,
                  "Довше вікно гладшає сильніше, та наздоганяє зміну пізніше — за одне платиш іншим.",
                  10.5, MUTED, "middle"))

    render(os.path.join(OUT, "smoothing-lag.svg"), W, H, *p)


if __name__ == "__main__":
    fig_balance_mean()
    fig_moving_window()
    fig_smoothing_lag()
    print("Done: 3 figures ->", OUT)
