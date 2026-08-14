# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_dash = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, stroke, sw, d_dash)



def fig_cwnd_sawtooth():
    W, H = 820, 420
    p = []
    
    # Background & axes
    ax_x0, ax_y0 = 80, 340
    ax_w, ax_h = 700, 280
    
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    p.append(arrow(ax_x0, ax_y0, ax_x0 + ax_w, ax_y0, color=LINE, sw=1.8))
    p.append(arrow(ax_x0, ax_y0, ax_x0, ax_y0 - ax_h, color=LINE, sw=1.8))
    
    p.append(text(ax_x0 + ax_w + 10, ax_y0 + 5, "Час (RTT)", size=12, color=MUTED, anchor="start", italic=True))
    p.append(text(ax_x0 - 10, ax_y0 - ax_h - 10, "Розмір вікна заторів (cwnd)", size=12, color=MUTED, anchor="middle", italic=True))

    # Threshold line ssthresh
    thresh_y = ax_y0 - 140
    p.append(line(ax_x0, thresh_y, ax_x0 + ax_w - 20, thresh_y, color=POS, sw=1.4, dash="4 4"))
    p.append(text(ax_x0 + 10, thresh_y - 8, "ssthresh (поріг повільного старту)", size=11, color=POS, bold=True, anchor="start"))

    # Curve points for Slow Start + Congestion Avoidance + Loss + Reno/CUBIC recovery
    # Draw Tahoe drop line (dashed)
    p.append(line(ax_x0 + 240, ax_y0 - 240, ax_x0 + 240, ax_y0 - 20, color=MUTED, sw=1.5, dash="3 3"))
    p.append(circle(ax_x0 + 240, ax_y0 - 20, 4, fill=POS, stroke=BG, sw=1))
    p.append(text(ax_x0 + 246, ax_y0 - 30, "Tahoe: скидання до 1 MSS", size=10, color=MUTED, anchor="start"))

    # Main Reno Path
    reno_pts = [
        (ax_x0, ax_y0 - 15),
        (ax_x0 + 30, ax_y0 - 35),
        (ax_x0 + 60, ax_y0 - 70),
        (ax_x0 + 100, ax_y0 - 140), # reaches ssthresh
        (ax_x0 + 160, ax_y0 - 180),
        (ax_x0 + 240, ax_y0 - 240), # Loss event!
    ]
    
    d_path1 = "M " + " L ".join(["%.1f,%.1f" % (pt[0], pt[1]) for pt in reno_pts])
    p.append(path_svg(d_path1, fill="none", stroke=NEG, sw=2.5))

    # Loss marker
    p.append(circle(ax_x0 + 240, ax_y0 - 240, 6, fill=POS, stroke=BG, sw=1.5))
    p.append(text(ax_x0 + 240, ax_y0 - 255, "Втрата пакета (3× dupACK)", size=11, color=POS, bold=True, anchor="middle"))

    # Reno Recovery curve:
    reno_rec = [
        (ax_x0 + 240, ax_y0 - 120), # ssthresh/2
        (ax_x0 + 340, ax_y0 - 170),
        (ax_x0 + 440, ax_y0 - 220), # Loss event 2
    ]
    d_path_reno = "M " + " L ".join(["%.1f,%.1f" % (pt[0], pt[1]) for pt in reno_rec])
    p.append(path_svg(d_path_reno, fill="none", stroke=NEG, sw=2.2))
    p.append(text(ax_x0 + 370, ax_y0 - 185, "Reno (AIMD: +1 MSS/RTT)", size=10.5, color=NEG, bold=True))

    # CUBIC curve from loss point:
    cubic_pts = [
        (ax_x0 + 240, ax_y0 - 120),
        (ax_x0 + 300, ax_y0 - 190),
        (ax_x0 + 360, ax_y0 - 230), # approaching W_max
        (ax_x0 + 420, ax_y0 - 240), # W_max inflection
        (ax_x0 + 480, ax_y0 - 260), # probing higher bandwidth
    ]
    d_path_cubic = "M " + " L ".join(["%.1f,%.1f" % (pt[0], pt[1]) for pt in cubic_pts])
    p.append(path_svg(d_path_cubic, fill="none", stroke=FIELD, sw=2.2, dash="5 3"))
    p.append(text(ax_x0 + 440, ax_y0 - 272, "CUBIC (кубічне розширення W(t))", size=10.5, color=FIELD, bold=True))

    # Annotations
    p.append(rect(ax_x0 + 15, ax_y0 - 55, 120, 40, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    p.append(text(ax_x0 + 75, ax_y0 - 40, "Повільний старт", size=10.5, color=NEG, bold=True))
    p.append(text(ax_x0 + 75, ax_y0 - 26, "Експоненціальний (×2)", size=9.5, color=MUTED))


    p.append(rect(ax_x0 + 135, ax_y0 - 225, 100, 45, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    p.append(text(ax_x0 + 185, ax_y0 - 205, "Уникання заторів", size=10.5, color=NEG, bold=True))
    p.append(text(ax_x0 + 185, ax_y0 - 190, "Лінійне зростання", size=9.5, color=MUTED))

    # Explanatory bottom note
    box, _, _ = textbox(W / 2, 395, "Динаміка вікна заторів: експоненціальний розгін до ssthresh, лінійне розширення AIMD та реакція на втрати.",
                        size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.2, min_w=760)
    p.append(box)

    render(os.path.join(OUT, "cwnd-sawtooth.svg"), W, H, *p,
           title="Пилоподібна динаміка вікна заторів TCP")


def fig_aimd_phase_plane():
    W, H = 760, 440
    p = []
    
    ax_x0, ax_y0 = 100, 360
    ax_size = 270
    
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    
    # Axes
    p.append(arrow(ax_x0, ax_y0, ax_x0 + ax_size + 40, ax_y0, color=LINE, sw=1.8))
    p.append(arrow(ax_x0, ax_y0, ax_x0, ax_y0 - ax_size - 40, color=LINE, sw=1.8))
    
    p.append(text(ax_x0 + ax_size + 45, ax_y0 + 5, "Швидкість Потоку 1 (x₁)", size=12, color=INK, anchor="start", bold=True))
    p.append(text(ax_x0 - 10, ax_y0 - ax_size - 45, "Швидкість Потоку 2 (x₂)", size=12, color=INK, anchor="middle", bold=True))

    # Fairness line x1 = x2 (45 degrees)
    p.append(line(ax_x0, ax_y0, ax_x0 + ax_size + 20, ax_y0 - ax_size - 20, color=FIELD, sw=2, dash="4 4"))
    p.append(text(ax_x0 + ax_size - 30, ax_y0 - ax_size - 25, "Лінія справедливості (x₁ = x₂)", size=11, color=FIELD, bold=True))

    # Efficiency line x1 + x2 = C
    c_intercept = ax_size + 10
    p.append(line(ax_x0, ax_y0 - c_intercept, ax_x0 + c_intercept, ax_y0, color=POS, sw=2))
    p.append(text(ax_x0 + c_intercept - 40, ax_y0 - 15, "Лінія ємності (x₁ + x₂ = C)", size=11, color=POS, bold=True, anchor="end"))

    # Intersection point (Optimal point)
    opt_x = ax_x0 + c_intercept / 2
    opt_y = ax_y0 - c_intercept / 2
    p.append(circle(opt_x, opt_y, 6, fill=FIELD, stroke=BG, sw=1.5))
    p.append(text(opt_x + 12, opt_y - 10, "Оптимум (C/2, C/2)", size=11, color=FIELD, bold=True))

    # Trajectory of AIMD starting from unfair point (e.g., x1=40, x2=180)
    p1 = (ax_x0 + 40, ax_y0 - 180)
    p2 = (ax_x0 + 100, ax_y0 - 240) # touches capacity line
    p3 = (ax_x0 + 50, ax_y0 - 120)
    p4 = (ax_x0 + 120, ax_y0 - 190) # touches capacity line
    p5 = (ax_x0 + 60, ax_y0 - 95)
    p6 = (ax_x0 + 130, ax_y0 - 165)

    traj = [p1, p2, p3, p4, p5, p6]
    for i in range(len(traj) - 1):
        color = NEG if i % 2 == 0 else POS
        p.append(arrow(traj[i][0], traj[i][1], traj[i+1][0], traj[i+1][1], color=color, sw=2))
        p.append(circle(traj[i][0], traj[i][1], 3.5, fill=color, stroke=BG))

    # Explanatory text box on the right
    rx, ry = ax_x0 + ax_size + 60, 80
    p.append(rect(rx, ry, 260, 260, fill=FILL, stroke=MUTED, sw=1.4, rx=6))
    p.append(text(rx + 130, ry + 25, "Чому AIMD стійкий:", size=12, color=INK, bold=True))
    
    p.append(text(rx + 15, ry + 60, "1. Аддитивне зростання (+1, +1):", size=10.5, color=NEG, bold=True, anchor="start"))
    p.append(text(rx + 25, ry + 78, "зміщує стан паралельно куту 45°,", size=10, color=INK, anchor="start"))
    p.append(text(rx + 25, ry + 94, "наближаючи відносні частки до 1:1.", size=10, color=INK, anchor="start"))

    p.append(text(rx + 15, ry + 130, "2. Мультиплікативне скорочення:", size=10.5, color=POS, bold=True, anchor="start"))
    p.append(text(rx + 25, ry + 148, "спрямовує вектор до початку координат", size=10, color=INK, anchor="start"))
    p.append(text(rx + 25, ry + 164, "(×0.5), зберігаючи пропорцію рівності.", size=10, color=INK, anchor="start"))

    p.append(text(rx + 15, ry + 200, "3. Збіжність:", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(rx + 25, ry + 218, "цикл пульсацій неминуче звужується", size=10, color=INK, anchor="start"))
    p.append(text(rx + 25, ry + 234, "навколо точки оптимуму (C/2, C/2).", size=10, color=INK, anchor="start"))

    box, _, _ = textbox(W / 2, 415, "Фазова діаграма Чіу-Джейна: доведення збіжності AIMD до лінії справедливості та лінії ємності.",
                        size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.2, min_w=700)
    p.append(box)

    render(os.path.join(OUT, "aimd-phase-plane.svg"), W, H, *p,
           title="Фазова діаграма збіжності AIMD до справедливості та ефективності")


def fig_bufferbloat_bbr():
    W, H = 800, 420
    p = []
    
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    
    pw = 360
    
    # Panel 1: Loss-based
    p.append(rect(30, 40, pw, 320, fill="#fdfefe", stroke=POS, sw=1.6, rx=6))
    p.append(text(30 + pw/2, 65, "Loss-based (Reno / CUBIC)", size=13, color=POS, bold=True))
    p.append(text(30 + pw/2, 85, "Переповнює буфер маршрутизатора", size=10.5, color=MUTED))
    
    # Router Queue drawing
    p.append(rect(60, 140, 200, 50, fill="#fdecea", stroke=POS, sw=1.6, rx=4))
    for i in range(7):
        p.append(rect(65 + i*27, 145, 23, 40, fill=POS, stroke=BG, sw=1))
        p.append(text(65 + i*27 + 11.5, 170, "P", size=10, color=BG, bold=True))
    p.append(text(160, 125, "Буфер маршрутизатора (ПОВНИЙ)", size=10, color=POS, bold=True))
    
    # Bottleneck link
    p.append(rect(260, 155, 110, 20, fill="#eaf0fd", stroke=NEG, sw=1.2))
    p.append(text(315, 169, "Вузький канал", size=9.5, color=NEG))
    
    # Packet drop
    p.append(arrow(245, 140, 245, 105, color=POS, sw=1.8))
    p.append(text(245, 95, "✗ Втрата (Tail Drop)", size=10.5, color=POS, bold=True))

    # Metric consequence
    p.append(rect(50, 220, 320, 120, fill=BG, stroke=MUTED, sw=1, rx=4))
    p.append(text(60, 245, "• Пропускна здатність: 100% (максимум)", size=10.5, color=INK, anchor="start"))
    p.append(text(60, 270, "• Затримка RTT: Висока (RTT = RTprop + Qdelay)", size=10.5, color=POS, anchor="start", bold=True))
    p.append(text(60, 295, "• Наслідок: Буферне роздування (Bufferbloat),", size=10, color=POS, anchor="start"))
    p.append(text(60, 315, "  величезний затримковий пік (лаг).", size=10, color=POS, anchor="start"))

    # Panel 2: BBR
    p.append(rect(410, 40, pw, 320, fill="#fdfefe", stroke=FIELD, sw=1.6, rx=6))
    p.append(text(410 + pw/2, 65, "Model-based (BBR)", size=13, color=FIELD, bold=True))
    p.append(text(410 + pw/2, 85, "Балансує на межі BDP = BtlBw × RTprop", size=10.5, color=MUTED))

    # Router Queue drawing BBR
    p.append(rect(440, 140, 200, 50, fill="#eafaf1", stroke=FIELD, sw=1.6, rx=4))
    for i in range(2):
        p.append(rect(445 + i*27, 145, 23, 40, fill=FIELD, stroke=BG, sw=1))
        p.append(text(445 + i*27 + 11.5, 170, "P", size=10, color=BG, bold=True))
    p.append(text(540, 125, "Буфер без черги (Оптимальний)", size=10, color=FIELD, bold=True))

    # Bottleneck link BBR
    p.append(rect(640, 155, 110, 20, fill="#eaf0fd", stroke=NEG, sw=1.2))
    p.append(text(695, 169, "Вузький канал", size=9.5, color=NEG))
    
    # Metric consequence BBR
    p.append(rect(430, 220, 320, 120, fill=BG, stroke=MUTED, sw=1, rx=4))
    p.append(text(440, 245, "• Пропускна здатність: 100% (BtlBw)", size=10.5, color=FIELD, anchor="start", bold=True))
    p.append(text(440, 270, "• Затримка RTT: Мінімальна (RTprop)", size=10.5, color=FIELD, anchor="start", bold=True))
    p.append(text(440, 295, "• Наслідок: Відсутність черги в буфері,", size=10, color=INK, anchor="start"))
    p.append(text(440, 315, "  мінімальний затримковий крок і плавна передача.", size=10, color=INK, anchor="start"))

    box, _, _ = textbox(W / 2, 395, "Порівняння заповнення буферів у Loss-based алгоритмах та BBR.",
                        size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.2, min_w=760)
    p.append(box)

    render(os.path.join(OUT, "bufferbloat-bbr.svg"), W, H, *p,
           title="Порівняння заповнення буферів у Loss-based алгоритмах та BBR")


if __name__ == "__main__":
    fig_cwnd_sawtooth()
    fig_aimd_phase_plane()
    fig_bufferbloat_bbr()
    print("All figures generated successfully.")
