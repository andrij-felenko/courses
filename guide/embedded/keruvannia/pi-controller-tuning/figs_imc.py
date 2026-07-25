# -*- coding: utf-8 -*-
# Фігури для вставки math-imc-pi.md (виведення lambda/IMC-формул ПІ).
# Окремий генератор, щоб не чіпати основний figs.py теми.
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), color, sw, d))


# ── 1. Скорочення полюса: нуль регулятора сідає на повільний полюс об'єкта ──────
# Ліворуч експонента об'єкта (повільний полюс, стала τ); у центрі дзеркальний
# нуль регулятора на тій самій сталій; праворуч — їхній добуток, рівний 1.
def fig_pole_cancel():
    W, H = 720, 350
    p = []
    oy = 250
    H0 = 150

    # три панелі
    def panel(ox, Ax, label):
        p.append(arrow(ox, oy, ox + Ax + 8, oy, color=MUTED, sw=1.3))
        p.append(arrow(ox, oy, ox, oy - H0 - 14, color=MUTED, sw=1.3))
        p.append(text(ox + Ax / 2, oy + 30, label, size=11, color=INK, anchor="middle", bold=True))

    Ax = 150
    gap = 70
    ox1 = 70
    ox2 = ox1 + Ax + gap
    ox3 = ox2 + Ax + gap

    panel(ox1, Ax, "об'єкт: повільний\nспад зі сталою τ")
    panel(ox2, Ax, "нуль регулятора:\nдзеркальний підйом")
    panel(ox3, Ax, "добуток = 1:\nполюс зник")

    tau_px = Ax * 0.34
    N = 120

    # 1: спадна експонента exp(-t/τ) — «повільність» об'єкта
    pts1 = []
    for i in range(N + 1):
        x = ox1 + (i / N) * Ax
        tt = (x - ox1) / tau_px
        y = oy - H0 * math.exp(-tt)
        pts1.append((x, y))
    p.append(polyline(pts1, color=NEG, sw=2.6))
    p.append(text(ox1 + Ax * 0.5, oy - H0 - 22, "1 / (1 + τs)", size=11, color=NEG, anchor="middle", bold=True))

    # 2: дзеркальна — наростання (1 + τs), той самий темп, інший знак нахилу
    pts2 = []
    for i in range(N + 1):
        x = ox2 + (i / N) * Ax
        tt = (x - ox2) / tau_px
        y = oy - H0 * (1 - math.exp(-tt))   # дзеркало: від 0 угору до плато
        pts2.append((x, y))
    p.append(polyline(pts2, color=POS, sw=2.6))
    p.append(text(ox2 + Ax * 0.5, oy - H0 - 22, "(1 + τs)", size=11, color=POS, anchor="middle", bold=True))

    # 3: рівна лінія = 1 (полюс і нуль знищилися)
    yflat = oy - H0 * 0.62
    p.append(line(ox3, yflat, ox3 + Ax, yflat, color=FIELD, sw=2.8))
    p.append(text(ox3 + Ax * 0.5, oy - H0 - 22, "= 1", size=12, color=FIELD, anchor="middle", bold=True))

    # знаки множення між панелями
    p.append(text(ox1 + Ax + gap / 2, oy - H0 * 0.5, "×", size=20, color=MUTED, anchor="middle", bold=True))
    p.append(text(ox2 + Ax + gap / 2, oy - H0 * 0.5, "=", size=20, color=MUTED, anchor="middle", bold=True))

    render(os.path.join(OUT, "pole-cancel.svg"), W, H, *p,
           title="Вибір Ti = τ ставить нуль регулятора рівно на полюс об'єкта")


# ── 2. Згортання IMC: дві ланки → один чистий контур першого порядку ───────────
# Зверху блок-схема IMC (модель + фільтр), знизу — еквівалентний відгук:
# замкнений контур поводиться як один лаг зі сталою λ (плюс затримка θ).
def fig_imc_collapse():
    W, H = 720, 360
    p = []

    # ── верх: ідея «контролер = обернена модель × фільтр» ──
    yb = 96
    bw, bh = 150, 52

    def blk(cx, s, fill=FILL, stroke=LINE, color=INK):
        x = cx - bw / 2
        p.append(rect(x, yb - bh / 2, bw, bh, fill=fill, stroke=stroke, sw=1.8))
        p.append(text(cx, yb + 5, s, size=12.5, color=color, anchor="middle", bold=True))

    cx1 = 170
    cx2 = 410
    cx3 = 640 - 70
    blk(cx1, "1 / G(s)", stroke=NEG, color=NEG)            # обернена модель
    blk(cx2, "1 / (λs + 1)", stroke=FIELD, color=FIELD)    # фільтр з ручкою λ
    p.append(text((cx1 + cx2) / 2, yb - bh / 2 - 8, "×", size=18, color=MUTED, anchor="middle", bold=True))

    # стрілки потоку
    p.append(arrow(cx1 + bw / 2, yb, cx2 - bw / 2, yb, color=LINE, sw=1.6))
    p.append(text(cx1, yb - bh / 2 - 12, "обертаємо те, що можна", size=10, color=NEG, anchor="middle"))
    p.append(text(cx2, yb - bh / 2 - 12, "ручка швидкодії λ", size=10, color=FIELD, anchor="middle"))

    p.append(arrow(cx2 + bw / 2, yb, cx2 + bw / 2 + 56, yb, color=LINE, sw=1.6))
    p.append(text(cx2 + bw / 2 + 30, yb - 8, "контур", size=10, color=MUTED, anchor="middle"))

    # ── низ: відгук замкненого контуру — чистий лаг зі сталою λ після затримки θ ──
    ox, oy = 90, 320
    Ax = 540
    top = 200
    target = top + 18
    p.append(arrow(ox, oy, ox + Ax + 8, oy, color=MUTED, sw=1.3))
    p.append(arrow(ox, oy, ox, top - 8, color=MUTED, sw=1.3))
    p.append(text(ox + Ax + 10, oy + 14, "час", size=10, color=MUTED, anchor="end"))
    p.append(line(ox, target, ox + Ax, target, color=MUTED, sw=1.2, dash="6 4"))
    p.append(text(ox + Ax + 10, target - 4, "завдання", size=10, color=MUTED, anchor="start"))

    dead = 0.10 * Ax          # затримку θ обернути не можна — вона лишається
    lam_px = 0.30 * Ax        # стала замкненого контуру λ
    x0 = ox + dead
    N = 300
    pts = []
    full = oy - target
    for i in range(N + 1):
        x = ox + (i / N) * Ax
        if x <= x0:
            y = oy
        else:
            tt = (x - x0) / lam_px
            y = oy - full * (1 - math.exp(-tt))
        pts.append((x, y))
    p.append(polyline(pts, color=FIELD, sw=2.8))

    # позначки θ і λ
    p.append(line(ox, oy + 6, x0, oy + 6, color=POS, sw=1.6))
    p.append(text((ox + x0) / 2, oy + 22, "θ (затримку не прибрати)", size=10, color=POS, anchor="middle", bold=True))
    y63 = oy - 0.632 * full
    x63 = x0 + lam_px
    p.append(line(ox, y63, x63, y63, color=INK, sw=1.0, dash="2 3"))
    p.append(line(x63, oy, x63, y63, color=INK, sw=1.0, dash="2 3"))
    p.append(text(x63 + 6, y63 + 14, "63 %", size=9, color=INK, anchor="start"))
    p.append(line(x0, target - 12, x63, target - 12, color=INK, sw=1.4))
    p.append(text((x0 + x63) / 2, target - 16, "λ — ви її обираєте", size=10, color=INK, anchor="middle", bold=True))

    render(os.path.join(OUT, "imc-collapse.svg"), W, H, *p,
           title="IMC згортає контур у простий лаг сталої λ із незмінною затримкою θ")


# ── 3. Місток C = Q/(1−G·Q): звідки (λ + θ) та інтегратор ПІ ────────────────────
# Чесне переведення IMC-контролера Q у класичний ПІ: у добутку G·Q раціональне
# скорочується (лишається затримка), а в різниці 1−G·Q одиниці гасяться (→ 1/s,
# інтегратор) і θs додається до λs (→ множник (λ+θ)).
def fig_deadtime_split():
    W, H = 720, 300
    p = []
    cx = W / 2

    # заголовок: місток IMC → класичний ПІ
    p.append(text(cx, 34, "місток:  класичний ПІ   C(s) = Q / ( 1 − G·Q )",
                  size=13.5, color=INK, anchor="middle", bold=True))

    # рядок 1: добуток G·Q — раціональне скорочується, лишається затримка
    p.append(fitbox(130, 58, W - 260, 44, "G·Q  =  e^(−θs) / (λs + 1)",
                    size=14, fill=FILL, stroke=NEG, sw=1.8, bold=True, color=NEG))
    p.append(text(cx, 122,
                  "раціональна частина об'єкта скоротилась проти оберненої моделі — лишились фільтр λ і затримка",
                  size=10, color=MUTED, anchor="middle"))

    # рядок 2: різниця 1 − G·Q — одиниці гасяться, θs додається до λs
    p.append(fitbox(130, 142, W - 260, 44, "1 − G·Q  =  (λs+1) − (1−θs)  =  (λ + θ)s",
                    size=14, fill=FILL, stroke=FIELD, sw=1.8, bold=True, color=INK))
    p.append(text(cx, 206, "e^(−θs) ≈ 1 − θs   (перший порядок)",
                  size=10, color=MUTED, anchor="middle"))

    # два висновки
    p.append(text(cx, 240, "одиниці гасяться  →  у C(s) з'являється 1/s : інтегратор ПІ",
                  size=11.5, color=FIELD, anchor="middle", bold=True))
    p.append(text(cx, 268, "θs стає поряд із λs  →  спільний множник (λ + θ) у знаменнику Kp",
                  size=11.5, color=POS, anchor="middle", bold=True))

    render(os.path.join(OUT, "deadtime-split.svg"), W, H, *p,
           title="Місток C = Q/(1−G·Q): звідки (λ + θ) та інтегратор ПІ")


if __name__ == "__main__":
    fig_pole_cancel()
    fig_imc_collapse()
    fig_deadtime_split()
    print("OK: IMC-figures written to", OUT)
