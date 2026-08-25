# -*- coding: utf-8 -*-
"""Фігури теми «Коефіцієнт потужності». Запуск: python figs.py → ./img/*.svg"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_triangle():
    """Коефіцієнт потужності як відношення сторін: P/S. Дві колонки — відстаючий і випереджальний."""
    W, H = 760, 410
    parts = []
    parts.append(text(W/2, 26, "Коефіцієнт потужності = P / S", size=17, bold=True))

    def triangle(ox, oy, q_sign, caption, kw):
        # катет P уздовж осі, катет Q вгору (lag) або вниз (lead), гіпотенуза S
        P = 200.0
        Q = 130.0
        out = []
        # активна (горизонталь)
        out.append(arrow(ox, oy, ox + P, oy, color=FIELD, sw=3))
        out.append(text(ox + P/2, oy + (20 if q_sign > 0 else -10), "P  (Вт)", size=13, color=FIELD, bold=True))
        # реактивна (вертикаль)
        qy = oy - q_sign * Q
        out.append(arrow(ox + P, oy, ox + P, qy, color=POS, sw=3))
        lab = "Q" if q_sign > 0 else "Q"
        out.append(text(ox + P + 14, (oy + qy)/2 + 4, "Q (вар)", size=13, color=POS, anchor="start", bold=True))
        # повна (гіпотенуза)
        out.append(arrow(ox, oy, ox + P, qy, color=INK, sw=2.6))
        out.append(text(ox + P/2 - 30, qy + q_sign*4 - (4 if q_sign>0 else -16), "S (В·А)", size=13, color=INK, bold=True))
        # кут φ
        out.append(text(ox + 34, oy - q_sign*14, "φ", size=15, color=MUTED, italic=True))
        body = fitbox(ox - 8, oy + (60 if q_sign > 0 else -112), 232, 42, caption,
                      size=12, fill="#f4f6f8", stroke=MUTED, **kw)
        out.append(body)
        return "".join(out)

    parts.append(triangle(70, 140, +1,
                          "Відстаючий (lag): котушка, мотор —\nструм відстає, Q «вгору»", {}))
    parts.append(triangle(440, 240, -1,
                          "Випереджальний (lead): конденсатор —\nструм випереджає, Q «вниз»", {}))
    render(os.path.join(OUT, 'pf-triangle.svg'), W, H, *parts)


def fig_distortion():
    """Чиста синусоїда vs пік-струм випрямляча: однакова фаза, але PF падає через гармоніки."""
    W, H = 760, 400
    parts = []
    parts.append(text(W/2, 24, "Однакова фаза — різний коефіцієнт потужності", size=16, bold=True))
    x0, x1 = 70, 690
    midL = 130   # вісь верхнього (напруга-струм лінійні)
    midR = 290   # вісь нижнього (струм випрямляча)
    span = x1 - x0
    amp = 50

    def axis(my, label):
        out = [line(x0, my, x1, my, color=MUTED, sw=1.2)]
        out.append(text(x0 - 8, my + 4, "0", size=11, color=MUTED, anchor="end"))
        out.append(text(x0, my - amp - 14, label, size=12, color=MUTED, anchor="start"))
        return "".join(out)

    parts.append(axis(midL, "лінійне навантаження: струм — чиста синусоїда"))
    parts.append(axis(midR, "вхід випрямляча: струм — вузькі піки на вершинах напруги"))

    N = 240
    # напруга (обидва графіки) — синя синусоїда
    for my in (midL, midR):
        d = []
        for i in range(N+1):
            t = i/N
            x = x0 + t*span
            y = my - amp*math.sin(2*math.pi*t)
            d.append(("M" if i == 0 else "L") + "%.1f %.1f" % (x, y))
        parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" opacity="0.85"/>' % (" ".join(d), NEG))

    # верх: струм у фазі — помаранчева синусоїда
    d = []
    for i in range(N+1):
        t = i/N
        x = x0 + t*span
        y = midL - amp*0.9*math.sin(2*math.pi*t)
        d.append(("M" if i == 0 else "L") + "%.1f %.1f" % (x, y))
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(d), POS))

    # низ: пік-струм випрямляча — вузькі імпульси біля вершин |sin|
    d = []
    for i in range(N+1):
        t = i/N
        x = x0 + t*span
        s = math.sin(2*math.pi*t)
        # імпульс лише поблизу |s|≈1
        env = max(0.0, abs(s) - 0.86) / 0.14
        y = midR - amp*1.05*env*math.copysign(1, s)
        d.append(("M" if i == 0 else "L") + "%.1f %.1f" % (x, y))
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(d), POS))

    # підписи-висновки
    b1 = fitbox(x0, midL + amp + 12, 300, 34,
                "cos φ ≈ 1  →  PF ≈ 1.0", size=13, fill="#eafaf1", stroke=FIELD, bold=True)
    b2 = fitbox(x1 - 300, midR + amp + 12, 300, 34,
                "cos φ ≈ 1, але THD ≈ 100%  →  PF ≈ 0.6", size=13, fill="#fdecea", stroke=POS, bold=True)
    parts.append(b1)
    parts.append(b2)
    render(os.path.join(OUT, 'pf-distortion.svg'), W, H, *parts)


def fig_overcurrent():
    """Скільки «зайвого» струму тягне навантаження залежно від PF: множник 1/PF."""
    W, H = 720, 300
    parts = []
    parts.append(text(W/2, 26, "Низький PF = більше струму на той самий ват", size=16, bold=True))
    pfs = [1.0, 0.9, 0.8, 0.7, 0.5]
    x0 = 90
    base = 250            # нульова лінія стовпців
    bw = 70
    gap = 56
    maxmul = 2.0
    scale = 150          # px на одиницю множника понад 1
    for k, pf in enumerate(pfs):
        mul = 1.0/pf
        x = x0 + k*(bw+gap)
        h = (mul-1.0)*scale + 40
        y = base - h
        col = FIELD if pf >= 0.95 else (MUTED if pf >= 0.85 else POS)
        fillc = "#eafaf1" if pf >= 0.95 else ("#eef1f4" if pf >= 0.85 else "#fdecea")
        parts.append(rect(x, y, bw, h, fill=fillc, stroke=col, sw=2))
        parts.append(text(x + bw/2, y - 10, "×%.2f" % mul, size=14, color=col, bold=True))
        parts.append(text(x + bw/2, base + 20, "PF %.2f" % pf, size=12, color=INK))
    parts.append(line(x0-20, base, x0 + len(pfs)*(bw+gap)-gap+20, base, color=MUTED, sw=1.2))
    parts.append(text(W/2, base + 50,
                      "Множник струму = 1 / PF: при PF 0.5 крізь дроти тече вдвічі більший струм",
                      size=12, color=MUTED))
    render(os.path.join(OUT, 'pf-overcurrent.svg'), W, H, *parts)


def fig_orthogonality():
    """Чому середнє від добутку двох різних гармонік = 0, а від однакових ≠ 0.
    Дві колонки: ліворуч 1×2 (різні частоти) → площі вгору і вниз рівні, середнє 0;
    праворуч 1×1 (та сама частота) → добуток лежить переважно вгорі, середнє > 0."""
    W, H = 760, 470
    parts = []
    parts.append(text(W/2, 24, "Середнє від добутку: однакові частоти працюють, різні — гасяться", size=15, bold=True))

    x0, x1 = 60, 360       # ліва колонка
    x2, x3 = 410, 710      # права колонка
    amp = 30
    N = 360

    def sinpath(xa, xb, my, k, ph, a, color, sw, op=1.0):
        d = []
        for i in range(N+1):
            t = i/N
            x = xa + t*(xb-xa)
            y = my - a*math.sin(2*math.pi*k*t + ph)
            d.append(("M" if i == 0 else "L") + "%.1f %.1f" % (x, y))
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" opacity="%.2f"/>' % (" ".join(d), color, sw, op)

    def prodfill(xa, xb, my, k1, ph1, k2, ph2, a):
        """Заштрихувати площу під добутком двох синусів (нормованим), + над віссю, − під."""
        up, dn = [], []
        prev_x = xa
        seg_u, seg_d = [], []
        for i in range(N+1):
            t = i/N
            x = xa + t*(xb-xa)
            p = math.sin(2*math.pi*k1*t + ph1) * math.sin(2*math.pi*k2*t + ph2)
            y = my - a*p
            (up if p >= 0 else dn).append((x, y))
        # малюємо як тонку лінію добутку + півпрозора заливка стовпчиками
        out = []
        d = []
        for i in range(N+1):
            t = i/N
            x = xa + t*(xb-xa)
            p = math.sin(2*math.pi*k1*t + ph1) * math.sin(2*math.pi*k2*t + ph2)
            y = my - a*p
            d.append(("M" if i == 0 else "L") + "%.1f %.1f" % (x, y))
        # заливка: набір вертикальних рисочок угору(+)/вниз(−)
        step = 4
        for i in range(0, N+1, step):
            t = i/N
            x = xa + t*(xb-xa)
            p = math.sin(2*math.pi*k1*t + ph1) * math.sin(2*math.pi*k2*t + ph2)
            y = my - a*p
            c = FIELD if p >= 0 else NEG
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" opacity="0.30"/>' % (x, my, x, y, c))
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(d), INK))
        return "".join(out)

    def column(xa, xb, k2, ph2, title_top, verdict, vcol, vfill):
        out = []
        topY = 110     # вісь двох співмножників
        botY = 300     # вісь добутку
        # підпис колонки
        out.append(text((xa+xb)/2, 56, title_top, size=12, color=MUTED))
        # осі
        out.append(line(xa, topY, xb, topY, color=MUTED, sw=1.1))
        out.append(line(xa, botY, xb, botY, color=MUTED, sw=1.1))
        out.append(text(xa-6, topY-amp-10, "два співмножники", size=10.5, color=MUTED, anchor="start"))
        out.append(text(xa-6, botY-amp-44, "їхній добуток за період", size=10.5, color=MUTED, anchor="start"))
        # два співмножники: f1 (синій-ish INK тонкий) і f2
        out.append(sinpath(xa, xb, topY, 1, 0.0, amp, NEG, 2.2))
        out.append(sinpath(xa, xb, topY, k2, ph2, amp, POS, 2.2))
        # добуток із заливкою
        out.append(prodfill(xa, xb, botY, 1, 0.0, k2, ph2, amp*1.0))
        # вердикт
        out.append(fitbox(xa, botY+amp+24, xb-xa, 34, verdict, size=12, fill=vfill, stroke=vcol, bold=True))
        return "".join(out)

    parts.append(column(x0, x1, 2, 0.0,
                         "різні частоти (1-ша × 2-га)",
                         "однаково вгору і вниз → середнє = 0", NEG, "#eaf0fd"))
    parts.append(column(x2, x3, 1, 0.0,
                         "та сама частота (1-ша × 1-ша)",
                         "переважно вгору → середнє > 0", FIELD, "#eafaf1"))
    render(os.path.join(OUT, 'pf-orthogonality.svg'), W, H, *parts)


def fig_current_pythagoras():
    """Розклад діючого струму: I_rms² = I₁² + (сума гармонік)². Прямий кут між
    основною й «спотворювальною» складовою; проєкція I₁ на напругу дає cos φ."""
    W, H = 760, 420
    parts = []
    parts.append(text(W/2, 24, "Діючий струм за теоремою Піфагора", size=16, bold=True))

    # лівий блок: вертикальний прямокутний трикутник I₁ (гор.) ⊥ I_h (верт.) = I_rms (гіп.)
    ox, oy = 95, 300
    I1 = 230.0     # горизонталь — основна гармоніка
    Ih = 150.0     # вертикаль — гармоніки разом
    # I₁
    parts.append(arrow(ox, oy, ox+I1, oy, color=FIELD, sw=3))
    parts.append(text(ox+I1/2, oy+22, "I₁  (основна гармоніка)", size=12.5, color=FIELD, bold=True))
    # маркер прямого кута
    parts.append(line(ox+I1-16, oy, ox+I1-16, oy-16, color=MUTED, sw=1.4))
    parts.append(line(ox+I1-16, oy-16, ox+I1, oy-16, color=MUTED, sw=1.4))
    # I_h
    parts.append(arrow(ox+I1, oy, ox+I1, oy-Ih, color=POS, sw=3))
    parts.append(text(ox+I1+12, oy-Ih/2+4, "√(I₂²+I₃²+…)", size=12.5, color=POS, anchor="start", bold=True))
    parts.append(text(ox+I1+12, oy-Ih/2+22, "усі гармоніки разом", size=11, color=POS, anchor="start"))
    # I_rms (гіпотенуза)
    parts.append(arrow(ox, oy, ox+I1, oy-Ih, color=INK, sw=2.6))
    parts.append(text(ox+I1/2-40, oy-Ih/2-6, "I_rms", size=13.5, color=INK, bold=True))
    # формула під трикутником
    parts.append(fitbox(ox-10, oy+44, I1+90, 30,
                        "I_rms² = I₁² + I₂² + I₃² + …", size=13, fill="#f4f6f8", stroke=MUTED, bold=True))

    # правий блок: дві проєкції основної гармоніки → cos φ та коеф. спотворення
    bx = 470
    parts.append(fitbox(bx, 70, 250, 30, "Два множники PF", size=13, fill="#ffffff", stroke=INK, bold=True))
    parts.append(fitbox(bx, 120, 250, 60,
                        "коеф. спотворення =\nI₁ / I_rms = 1/√(1+THD²)", size=12.5,
                        fill="#fdecea", stroke=POS, bold=True))
    parts.append(fitbox(bx, 200, 250, 60,
                        "коеф. зсуву =\ncos φ₁ (тільки основна)", size=12.5,
                        fill="#eafaf1", stroke=FIELD, bold=True))
    parts.append(fitbox(bx, 290, 250, 44,
                        "PF = cos φ₁ × 1/√(1+THD²)", size=12.5,
                        fill="#eef1f4", stroke=INK, bold=True))
    render(os.path.join(OUT, 'pf-current-pythagoras.svg'), W, H, *parts)


if __name__ == '__main__':
    fig_triangle()
    fig_distortion()
    fig_overcurrent()
    fig_orthogonality()
    fig_current_pythagoras()
    print("done:", os.listdir(OUT))
