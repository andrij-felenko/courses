# -*- coding: utf-8 -*-
"""Фігури до теми «Груповий час затримки» (аналогова електроніка, кутом теорії кіл).
Чотири фігури:
  envelope-delay.svg — модульований сигнал на вході й виході: огинальна зсунута на τг
  phase-slope.svg    — фаза φ(ω): нахил дотичної = −τг; крута фаза → велика затримка
  flat-vs-not.svg    — плаский τг (огинальна ціла) проти горбатого (огинальна розпливлась)
  bessel-bump.svg    — три фільтри: Бесселя (рівний τг), Баттерворта, Чебишова (горб біля краю)
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def envelope_delay():
    """Радіоімпульс (несуча під огинальною) на вході й виході: огинальна цілою зсунулась на τг."""
    W, H = 720, 380
    p = []
    x0, x1 = 70, 650
    y_in = 110
    y_out = 250
    span = x1 - x0
    amp = 42
    shift = 0.16          # частка осі — зсув огинальної (груповий час)

    def packet(yc, x_off, col, lbl):
        out = []
        out.append(line(x0 - 8, yc, x1 + 8, yc, color=MUTED, sw=1))   # вісь
        pts_env_top = []
        pts_env_bot = []
        pts_car = []
        N = 240
        for k in range(N + 1):
            t = k / N
            xx = x0 + span * t
            # огинальна — гаусів горб, зсунутий на x_off
            g = math.exp(-((t - 0.5 - x_off) ** 2) / (2 * 0.10 ** 2))
            env = amp * g
            car = math.sin(2 * math.pi * 11 * t) * env
            pts_env_top.append((xx, yc - env))
            pts_env_bot.append((xx, yc + env))
            pts_car.append((xx, yc - car))
        # огинальна (пунктир, обидві половини)
        d_top = "M" + " L".join("%.1f %.1f" % q for q in pts_env_top)
        d_bot = "M" + " L".join("%.1f %.1f" % q for q in pts_env_bot)
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4 3"/>' % (d_top, col))
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4 3"/>' % (d_bot, col))
        # несуча
        d_car = "M" + " L".join("%.1f %.1f" % q for q in pts_car)
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (d_car, INK))
        out.append(text(x0 - 14, yc + 4, lbl, size=13, bold=True, anchor="end"))
        # вершина огинальної — позначка
        peak_x = x0 + span * (0.5 + x_off)
        out.append(line(peak_x, yc - amp - 10, peak_x, yc + amp + 10, color=col, sw=1.2, dash="2 3"))
        return out, peak_x

    inp, px_in = packet(y_in, 0.0, NEG, "вхід")
    outp, px_out = packet(y_out, shift, FIELD, "вихід")
    p += inp + outp

    # стрілка зсуву між вершинами
    ay = (y_in + y_out) / 2 + 36
    p.append(arrow(px_in, ay, px_out, ay, color=POS, sw=2))
    p.append(text((px_in + px_out) / 2, ay - 8, "τг", size=15, bold=True, color=POS))
    p.append(text((px_in + px_out) / 2, ay + 18, "груповий час затримки", size=11, color=POS))

    b, _, _ = textbox(W / 2, 354,
                      "Затримується НЕ окремий гребінець несучої, а вся огинальна (пакет).\n"
                      "Наскільки пізно прийшов горб пакета — це і є груповий час затримки τг.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'envelope-delay.svg'), W, H, *p,
           title="Груповий час затримки: на скільки спізнюється огинальна сигналу")


def phase_slope():
    """φ(ω) спадає з частотою; груповий час = −нахил. Крута ділянка → велика затримка."""
    W, H = 720, 400
    p = []
    ox, oy = 90, 320
    ax_w, ax_h = 560, 250
    # осі
    p.append(arrow(ox, oy, ox + ax_w + 10, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - ax_h - 10, color=INK, sw=1.8))
    p.append(text(ox + ax_w + 6, oy + 20, "частота ω", size=13, bold=True, anchor="end"))
    p.append(text(ox - 60, oy - ax_h - 2, "фаза φ(ω)", size=13, bold=True, anchor="start"))
    p.append(text(ox - 14, oy + 6, "0", size=12, anchor="end"))

    # крива φ(ω): спадає, з крутою ділянкою посередині (резонанс)
    pts = []
    N = 200
    for k in range(N + 1):
        t = k / N
        xx = ox + ax_w * t
        # фаза: монотонний спад, із крутим перегином коло t=0.5
        ph = -(0.45 * t + 0.55 / (1 + math.exp(-14 * (t - 0.5))))
        yy = oy - ax_h * (-ph) * 0.0 - (ax_h * 0.92) * (-ph) / 1.0
        # привести у пікселі: φ у [−1..0], малюємо вниз від верху осі
        yy = (oy - ax_h + 10) + (ax_h - 20) * (-ph)
        pts.append((xx, yy, t, ph))
    d = "M" + " L".join("%.1f %.1f" % (q[0], q[1]) for q in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, NEG))

    # дотична на крутій ділянці (t≈0.5)
    i_mid = N // 2
    xm, ym = pts[i_mid][0], pts[i_mid][1]
    # нахил по сусідах
    dxp = pts[i_mid + 6][0] - pts[i_mid - 6][0]
    dyp = pts[i_mid + 6][1] - pts[i_mid - 6][1]
    sl = dyp / dxp
    L = 70
    p.append(line(xm - L, ym - sl * L, xm + L, ym + sl * L, color=POS, sw=2.2))
    p.append(circle(xm, ym, 4, fill=POS, stroke=POS))
    p.append(text(xm + 96, ym - 6, "крутий нахил", size=12, bold=True, color=POS, anchor="middle"))
    p.append(text(xm + 96, ym + 12, "→ велике τг", size=12, bold=True, color=POS, anchor="middle"))

    # пологий нахил на краю (t≈0.12)
    i_lo = int(N * 0.12)
    xl, yl = pts[i_lo][0], pts[i_lo][1]
    dxl = pts[i_lo + 6][0] - pts[i_lo - 6][0]
    dyl = pts[i_lo + 6][1] - pts[i_lo - 6][1]
    sll = dyl / dxl
    L2 = 56
    p.append(line(xl - L2, yl - sll * L2, xl + L2, yl + sll * L2, color=FIELD, sw=2.2))
    p.append(circle(xl, yl, 4, fill=FIELD, stroke=FIELD))
    p.append(text(xl + 4, yl - 16, "пологий → мале τг", size=11, bold=True, color=FIELD, anchor="middle"))

    b, _, _ = textbox(W / 2, 366,
                      "Груповий час τг = −похідна фази по частоті (мінус нахил дотичної до φ(ω)).\n"
                      "Де фаза падає круто — там сигнал затримується найдужче.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'phase-slope.svg'), W, H, *p,
           title="τг — це мінус нахил фазової характеристики φ(ω)")


def flat_vs_not():
    """Дві панелі: плаский τг — пакет цілий; горбатий τг — пакет розплився (різні частоти різно спізнились)."""
    W, H = 720, 420
    p = []
    pw = (W - 50) / 2.0

    def panel(x0, tau_flat, lbl, col, note):
        out = []
        cx = x0 + pw / 2
        out.append(text(cx, 52, lbl, size=14, bold=True, color=col))
        # верх: τг(ω) — лінія
        tx0, tx1 = x0 + 30, x0 + pw - 30
        ty = 110
        th = 46
        out.append(line(tx0, ty + th, tx1, ty + th, color=MUTED, sw=1))   # вісь ω
        out.append(text(tx0 - 6, ty + th + 4, "τг", size=11, anchor="end", color=col))
        pts = []
        N = 80
        for k in range(N + 1):
            t = k / N
            xx = tx0 + (tx1 - tx0) * t
            if tau_flat:
                val = 0.5
            else:
                val = 0.5 + 0.42 * math.exp(-((t - 0.78) ** 2) / (2 * 0.07 ** 2))
            yy = (ty + th) - th * val
            pts.append((xx, yy))
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, col))
        # низ: вихідний пакет
        yc = 260
        amp = 40
        out.append(line(tx0 - 6, yc, tx1 + 6, yc, color=MUTED, sw=1))
        env_top = []
        car = []
        N2 = 220
        for k in range(N2 + 1):
            t = k / N2
            xx = tx0 + (tx1 - tx0) * t
            g = math.exp(-((t - 0.5) ** 2) / (2 * 0.11 ** 2))
            if tau_flat:
                env = amp * g
                ph = 2 * math.pi * 10 * t
            else:
                # розплив: ширша огинальна + «дзвін» позаду (дисперсія)
                g2 = math.exp(-((t - 0.56) ** 2) / (2 * 0.17 ** 2))
                env = amp * 0.78 * g2
                ph = 2 * math.pi * 10 * t
            c = math.sin(ph) * env
            env_top.append((xx, yc - env))
            car.append((xx, yc - c))
        d_e = "M" + " L".join("%.1f %.1f" % q for q in env_top)
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4 3"/>' % (d_e, col))
        d_c = "M" + " L".join("%.1f %.1f" % q for q in car)
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (d_c, INK))
        out.append(text(cx, 320, note, size=11, color=MUTED))
        return out

    p += panel(20, True, "плаский τг(ω)", FIELD, "усі частоти спізнились однаково — пакет цілий")
    p += panel(20 + pw + 10, False, "горбатий τг(ω)", POS, "частоти спізнились по-різному — пакет розплився")
    p.append(line(W / 2, 70, W / 2, 340, color=MUTED, sw=1, dash="3 4"))

    b, _, _ = textbox(W / 2, 386,
                      "Якщо τг однаковий на всіх частотах — огинальна доходить цілою (форма збережена).\n"
                      "Якщо τг горбатий — складові спізнюються нарізно, і пакет розпливається.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'flat-vs-not.svg'), W, H, *p,
           title="Чому важлива РІВНІСТЬ τг: цілий пакет проти розплилого")


def bessel_bump():
    """τг(ω) трьох фільтрів того самого порядку: Бесселя (рівний), Баттерворта, Чебишова (горб біля краю смуги)."""
    W, H = 720, 400
    p = []
    ox, oy = 90, 320
    ax_w, ax_h = 560, 250
    p.append(arrow(ox, oy, ox + ax_w + 10, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - ax_h - 10, color=INK, sw=1.8))
    p.append(text(ox + ax_w + 6, oy + 20, "частота → край смуги", size=12, bold=True, anchor="end"))
    p.append(text(ox - 60, oy - ax_h - 2, "τг(ω)", size=13, bold=True, anchor="start"))

    def curve(fn, col, sw=2.4, dash=None):
        pts = []
        N = 200
        for k in range(N + 1):
            t = k / N
            xx = ox + ax_w * t
            v = fn(t)
            yy = oy - (ax_h - 20) * v
            pts.append((xx, yy))
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)
        ds = ' stroke-dasharray="%s"' % dash if dash else ''
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, col, sw, ds))
        return pts

    # Бесселя — майже рівний, легкий спад
    bessel = lambda t: 0.50 - 0.06 * t
    # Баттерворт — рівний, тоді підйом і спад біля краю
    butter = lambda t: 0.50 + 0.18 * math.exp(-((t - 0.82) ** 2) / (2 * 0.10 ** 2)) - 0.10 * max(0, t - 0.9)
    # Чебишов — виразний горб коло краю смуги
    cheby = lambda t: 0.50 + 0.42 * math.exp(-((t - 0.86) ** 2) / (2 * 0.06 ** 2))

    curve(cheby, POS)
    curve(butter, NEG)
    curve(bessel, FIELD)

    # межа смуги пропускання
    bx = ox + ax_w * 0.86
    p.append(line(bx, oy, bx, oy - ax_h, color=MUTED, sw=1, dash="4 4"))
    p.append(text(bx, oy + 18, "край смуги", size=11, color=MUTED))

    # підписи кривих
    p.append(text(ox + 60, oy - (ax_h - 20) * 0.50 - 10, "Бесселя — рівний τг", size=12, bold=True, color=FIELD, anchor="start"))
    p.append(text(ox + 250, oy - (ax_h - 20) * 0.62, "Баттерворт", size=12, bold=True, color=NEG, anchor="start"))
    p.append(text(ox + 300, oy - (ax_h - 20) * 0.90 - 4, "Чебишов — горб біля краю", size=12, bold=True, color=POS, anchor="start"))

    b, _, _ = textbox(W / 2, 366,
                      "Що крутіший спад фільтра — то горбатіший τг біля краю смуги (Чебишов гірший за всіх).\n"
                      "Фільтр Бесселя свідомо жертвує крутістю заради майже рівного τг — заради форми сигналу.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'bessel-bump.svg'), W, H, *p,
           title="τг різних фільтрів: ціна крутого спаду — горб затримки біля краю")


def allpass_mirror():
    """Полюс зліва від уявної осі, нуль — його дзеркало справа. Звідси одинична амплітуда."""
    W, H = 720, 420
    p = []
    cx, cy = W / 2, 230
    R = 150                       # масштаб осей
    # осі (комплексна площина s = σ + jω)
    p.append(arrow(cx - R - 30, cy, cx + R + 30, cy, color=INK, sw=1.8))   # σ (дійсна)
    p.append(arrow(cx, cy + R + 30, cx, cy - R - 30, color=INK, sw=1.8))   # jω (уявна)
    p.append(text(cx + R + 26, cy + 20, "σ (дійсна вісь)", size=12, bold=True, anchor="end"))
    p.append(text(cx + 8, cy - R - 18, "jω (уявна вісь)", size=12, bold=True, anchor="start"))
    p.append(text(cx - 10, cy + 16, "0", size=11, anchor="end", color=MUTED))

    # полюс −a + jb (лівий) і нуль +a + jb (правий) — дзеркало відносно уявної осі
    a = 70.0
    b = 78.0
    pole = (cx - a, cy - b)
    zero = (cx + a, cy - b)
    # точка на уявній осі jω, до якої міряємо відстані
    jw = (cx, cy - 118)

    # відрізки від полюса й нуля до точки jω
    p.append(line(pole[0], pole[1], jw[0], jw[1], color=NEG, sw=1.6, dash="5 3"))
    p.append(line(zero[0], zero[1], jw[0], jw[1], color=POS, sw=1.6, dash="5 3"))
    p.append(line(pole[0], pole[1], zero[0], zero[1], color=MUTED, sw=1, dash="2 4"))  # дзеркало

    # позначки полюса (×) і нуля (○)
    p.append(text(pole[0], pole[1] + 5, "×", size=26, bold=True, color=NEG, anchor="middle"))
    p.append(circle(zero[0], zero[1], 8, fill=BG, stroke=POS, sw=2.4))
    p.append(text(pole[0] - 12, pole[1] - 12, "полюс  −a+jb", size=12, bold=True, color=NEG, anchor="end"))
    p.append(text(zero[0] + 12, zero[1] - 12, "нуль  +a+jb", size=12, bold=True, color=POS, anchor="start"))
    p.append(circle(jw[0], jw[1], 4, fill=INK, stroke=INK))
    p.append(text(jw[0] + 10, jw[1] - 2, "точка jω", size=11, anchor="start", color=INK))

    # підписи рівних відстаней
    p.append(text((pole[0] + jw[0]) / 2 - 16, (pole[1] + jw[1]) / 2 - 4, "|s−нуль|", size=11, color=NEG, anchor="end"))
    p.append(text((zero[0] + jw[0]) / 2 + 16, (zero[1] + jw[1]) / 2 - 4, "= |s−полюс|", size=11, color=POS, anchor="start"))

    b1, _, _ = textbox(W / 2, 372,
                       "Нуль — дзеркало полюса відносно уявної осі. Для будь-якої точки jω на осі\n"
                       "відстань до нуля = відстань до полюса, тож |H| = |jω−нуль| / |jω−полюс| = 1 — на ВСІХ частотах.",
                       size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b1)
    render(os.path.join(OUT, 'allpass-mirror.svg'), W, H, *p,
           title="Чому амплітуда всепропускної ланки рівно одиниця: нуль — дзеркало полюса")


def equalize_stack():
    """Горбатий τг основного фільтра + опуклий τг ланок = рівна сума. АЧХ не торкаємось."""
    W, H = 720, 430
    p = []
    ox, oy = 90, 300
    ax_w, ax_h = 560, 210
    p.append(arrow(ox, oy, ox + ax_w + 10, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - ax_h - 14, color=INK, sw=1.8))
    p.append(text(ox + ax_w + 6, oy + 20, "частота → край смуги", size=12, bold=True, anchor="end"))
    p.append(text(ox - 60, oy - ax_h - 4, "τг(ω)", size=13, bold=True, anchor="start"))

    def curve(fn, col, sw=2.4, dash=None):
        pts = []
        N = 200
        for k in range(N + 1):
            t = k / N
            xx = ox + ax_w * t
            yy = oy - (ax_h - 24) * fn(t)
            pts.append((xx, yy))
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)
        ds = ' stroke-dasharray="%s"' % dash if dash else ''
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, col, sw, ds))

    # горб основного фільтра коло краю смуги (росте вгору)
    filt = lambda t: 0.30 + 0.42 * math.exp(-((t - 0.82) ** 2) / (2 * 0.085 ** 2))
    # додаток усепропускних ланок — «дзеркальний» горб у западину (підсипає там, де фільтр дав мало)
    eq = lambda t: 0.72 - filt(t)

    curve(filt, POS, sw=2.4)
    curve(eq, NEG, sw=2.2, dash="6 4")
    # рівна сума
    p.append(line(ox, oy - (ax_h - 24) * 0.72, ox + ax_w, oy - (ax_h - 24) * 0.72, color=FIELD, sw=2.8))

    # підписи
    p.append(text(ox + ax_w * 0.82, oy - (ax_h - 24) * 0.74 - 8, "горб фільтра", size=12, bold=True, color=POS, anchor="middle"))
    p.append(text(ox + ax_w * 0.40, oy - (ax_h - 24) * 0.62, "+ ланки всепропускні", size=12, bold=True, color=NEG, anchor="middle"))
    p.append(text(ox + ax_w * 0.20, oy - (ax_h - 24) * 0.72 - 10, "= сума рівна", size=12, bold=True, color=FIELD, anchor="middle"))

    bx = ox + ax_w * 0.82
    p.append(line(bx, oy, bx, oy - ax_h + 6, color=MUTED, sw=1, dash="4 4"))

    b1, _, _ = textbox(W / 2, 372,
                       "Усепропускні ланки додають затримку саме там, де фільтр дав замало — у дзеркальну форму горба.\n"
                       "Сума виходить рівною, а амплітудно-частотна характеристика тракту не зрушується ні на децибел.",
                       size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b1)
    render(os.path.join(OUT, 'equalize-stack.svg'), W, H, *p,
           title="Вирівнювання затримки: горб фільтра + ланки = рівний τг, АЧХ недоторкана")


def bessel_compare():
    """Дві панелі для вставки про фільтр Бесселя:
       угорі АЧХ трьох фільтрів одного порядку, унизу їхній груповий час.
       Бесселя — пологий зріз + рівний τг; Чебишов — крутий зріз + горб τг."""
    W, H = 720, 470
    p = []
    ox = 95
    ax_w = 545
    bx = ox + ax_w * 0.62      # умовна частота зрізу на осі (нормована)

    # легенда (спільна для двох панелей)
    lx = ox + 8
    ly = 44
    for i, (lbl, col) in enumerate([("Бесселя", FIELD), ("Баттерворта", NEG), ("Чебишова", POS)]):
        xx = lx + i * 168
        p.append(line(xx, ly, xx + 26, ly, color=col, sw=2.6))
        p.append(text(xx + 32, ly + 4, lbl, size=12, bold=True, color=col, anchor="start"))

    # ── панель А: амплітуда (АЧХ) ───────────────────────────────────────────
    ay_top = 70
    ay_h = 150
    ay = ay_top + ay_h          # вісь X панелі А
    p.append(arrow(ox, ay, ox + ax_w + 10, ay, color=INK, sw=1.6))
    p.append(arrow(ox, ay, ox, ay_top - 6, color=INK, sw=1.6))
    p.append(text(ox - 8, ay_top + 2, "|H|", size=12, bold=True, anchor="end"))
    p.append(text(ox - 8, ay - 2, "1", size=11, anchor="end"))
    p.append(text(ox + ax_w + 6, ay + 18, "частота", size=12, bold=True, anchor="end"))

    def amp_curve(fn, col, sw=2.4):
        pts = []
        N = 240
        for k in range(N + 1):
            t = k / N
            xx = ox + ax_w * t
            v = max(0.0, min(1.06, fn(t)))
            yy = ay - ay_h * (v / 1.06)
            pts.append((xx, yy))
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, col, sw))

    # нормована частота u = t / 0.62 (зріз там, де u=1)
    def u_of(t):
        return t / 0.62
    # Бесселя: найпологіший спад, «обвисає» ще в смузі
    def amp_bessel(t):
        u = u_of(t)
        return 1.0 / math.sqrt(1.0 + 0.55 * u ** 2 + 0.10 * u ** 4 + 0.04 * u ** 6)
    # Баттерворт 4-го порядку: рівний у смузі, помірний спад
    def amp_butter(t):
        u = u_of(t)
        return 1.0 / math.sqrt(1.0 + u ** 8)
    # Чебишов: крутий спад + брижі в смузі
    def amp_cheby(t):
        u = u_of(t)
        eps = 0.35
        if u <= 1.0:
            c = math.cos(4 * math.acos(min(1.0, u)))
        else:
            c = math.cosh(4 * math.acosh(u))
        return 1.0 / math.sqrt(1.0 + (eps * c) ** 2)

    amp_curve(amp_cheby, POS)
    amp_curve(amp_butter, NEG)
    amp_curve(amp_bessel, FIELD)
    p.append(line(bx, ay, bx, ay_top, color=MUTED, sw=1, dash="4 4"))
    p.append(text(bx, ay_top - 10, "зріз", size=10, color=MUTED))
    p.append(text(ox + 8, ay_top - 10, "АЧХ: Чебишов ріже найкрутіше, Бесселя — найпологіше",
                  size=11, color=MUTED, anchor="start"))

    # ── панель Б: груповий час ──────────────────────────────────────────────
    by_top = 268
    by_h = 130
    by = by_top + by_h          # вісь X панелі Б
    p.append(arrow(ox, by, ox + ax_w + 10, by, color=INK, sw=1.6))
    p.append(arrow(ox, by, ox, by_top - 6, color=INK, sw=1.6))
    p.append(text(ox - 8, by_top + 2, "τг", size=12, bold=True, anchor="end"))
    p.append(text(ox + ax_w + 6, by + 18, "частота", size=12, bold=True, anchor="end"))

    def tau_curve(fn, col, sw=2.4):
        pts = []
        N = 200
        for k in range(N + 1):
            t = k / N
            xx = ox + ax_w * t
            v = fn(t)
            yy = by - (by_h - 16) * v
            pts.append((xx, yy))
        d = "M" + " L".join("%.1f %.1f" % q for q in pts)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, col, sw))

    # τг (нормовані рівні): Бесселя майже рівний; Чебишов із горбом під краєм
    tau_bessel = lambda t: 0.50 - 0.05 * u_of(t)
    tau_butter = lambda t: 0.50 + 0.20 * math.exp(-((t - 0.56) ** 2) / (2 * 0.11 ** 2)) - 0.06 * max(0, t - 0.62)
    tau_cheby = lambda t: 0.50 + 0.46 * math.exp(-((t - 0.60) ** 2) / (2 * 0.055 ** 2))

    tau_curve(tau_cheby, POS)
    tau_curve(tau_butter, NEG)
    tau_curve(tau_bessel, FIELD)
    p.append(line(bx, by, bx, by_top, color=MUTED, sw=1, dash="4 4"))
    p.append(text(bx, by_top - 10, "зріз", size=10, color=MUTED))
    p.append(text(ox + 8, by_top - 10, "τг: Бесселя рівний, у Чебишова горб під краєм смуги",
                  size=11, color=MUTED, anchor="start"))

    b, _, _ = textbox(W / 2, 442,
                      "Чим крутіший зріз амплітуди (верх), тим горбатіший груповий час (низ).\n"
                      "Бесселя свідомо віддає крутість заради рівного τг — заради збереження форми.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'bessel-compare.svg'), W, H, *p,
           title="Бесселя · Баттерворт · Чебишов: розмін «крутість зрізу ↔ рівність затримки»")


if __name__ == '__main__':
    envelope_delay()
    phase_slope()
    flat_vs_not()
    bessel_bump()
    allpass_mirror()
    equalize_stack()
    bessel_compare()
    print("OK: 7 figures ->", OUT)
