# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Стояча хвиля: розмір задає частоту ────────────────────────────────────
def fig_standing_wave():
    W, H = 720, 360
    p = []
    p.append(text(W/2, 26, "Розмір деталі задає частоту: стояча пружна хвиля", size=17, bold=True))

    # спільна геометрія двох пластин
    x0 = 90
    top = 70
    plate_h = 70
    gap = 60

    def plate(cy, thick_px, label, wave_n, fdesc):
        out = []
        # тіло пластини
        out.append(rect(x0, cy - thick_px/2, 420, thick_px, fill="#eef2f7", stroke=LINE, sw=1.6, rx=4))
        # електроди зверху/знизу (тонкі смуги)
        out.append(rect(x0, cy - thick_px/2 - 5, 420, 5, fill=MUTED, stroke="none", sw=0))
        out.append(rect(x0, cy + thick_px/2, 420, 5, fill=MUTED, stroke="none", sw=0))
        # стояча хвиля зсуву поперек товщини: горизонтальний профіль u(y)
        # малюємо синусоїду вздовж товщини (по вертикалі), амплітуда — по горизонталі
        cx = x0 + 210
        amp = 150
        pts = []
        N = 40
        for i in range(N+1):
            fr = i / N
            yy = (cy - thick_px/2) + fr * thick_px
            # напіврізало: вузли на краях для n півхвиль
            u = amp * math.sin(wave_n * math.pi * fr)
            pts.append("%.1f,%.1f" % (cx + u, yy))
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), POS))
        # дзеркальний контур (обгортка руху) пунктиром
        pts2 = []
        for i in range(N+1):
            fr = i / N
            yy = (cy - thick_px/2) + fr * thick_px
            u = -amp * math.sin(wave_n * math.pi * fr)
            pts2.append("%.1f,%.1f" % (cx + u, yy))
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4 3"/>' % (" ".join(pts2), NEG))
        # осьова лінія
        out.append(line(cx, cy - thick_px/2, cx, cy + thick_px/2, color=MUTED, sw=1, dash="2 3"))
        # підпис товщини
        out.append(line(x0 - 22, cy - thick_px/2, x0 - 22, cy + thick_px/2, color=INK, sw=1.2))
        out.append(line(x0 - 26, cy - thick_px/2, x0 - 18, cy - thick_px/2, color=INK, sw=1.2))
        out.append(line(x0 - 26, cy + thick_px/2, x0 - 18, cy + thick_px/2, color=INK, sw=1.2))
        out.append(text(x0 - 34, cy + 4, label, size=13, color=INK, anchor="end"))
        # праворуч — частота
        out.append(text(x0 + 445, cy - 6, fdesc[0], size=13, color=INK, anchor="start", bold=True))
        out.append(text(x0 + 445, cy + 14, fdesc[1], size=12, color=MUTED, anchor="start"))
        return out

    cy1 = top + plate_h/2
    p += plate(cy1, plate_h, "d", 1, ("f = v / (2·d)", "товща d → нижча f"))
    cy2 = top + plate_h + gap + (plate_h*0.6)/2
    p += plate(cy2, plate_h*0.6, "d/1.7", 1, ("f ≈ 1.7× вища", "тонша d → вища f"))

    # нижній підпис-формула
    tb, tw, th = textbox(W/2, H-36, "півхвиля вкладається в товщину:  d = λ/2  →  f = v / (2·d)\nv — швидкість звуку в матеріалі (стала); товщина d — єдине, що варіюють",
                         size=12.5, fill="#f4faf5", stroke=FIELD, sw=1.4)
    p.append(tb)
    return render(os.path.join(OUT, 'standing-wave.svg'), W, H, *p)


# ── 2. Гострота резонансу: Q задає ширину піка ───────────────────────────────
def fig_q_shape():
    W, H = 720, 380
    p = []
    p.append(text(W/2, 26, "Добротність Q задає ширину резонансу", size=17, bold=True))

    # осі
    ox, oy = 90, 300
    axw, axh = 560, 230
    p.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.6))          # X
    p.append(line(ox, oy, ox, oy - axh, color=INK, sw=1.6))          # Y
    p.append(text(ox + axw, oy + 22, "частота", size=12, color=MUTED, anchor="end"))
    p.append(text(ox - 10, oy - axh + 4, "|відгук|", size=12, color=MUTED, anchor="end"))

    f0x = ox + axw*0.5   # центр резонансу
    def lorentz(Q, scale):
        # відносна форма: A(f) = 1/sqrt(1+(2Q·x)^2), x=(f-f0)/f0
        pts = []
        Nn = 200
        for i in range(Nn+1):
            fr = i/Nn                      # 0..1 по всій осі
            xrel = (fr - 0.5) * 0.02       # смуга ±1 %
            A = 1.0 / math.sqrt(1 + (2*Q*xrel)**2)
            xx = ox + fr*axw
            yy = oy - A*scale
            pts.append("%.1f,%.1f" % (xx, yy))
        return pts

    # кварц Q=100000 (дуже вузький), кераміка Q=400, RC-подібне Q=15
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(lorentz(100000, axh*0.94)), INK))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(lorentz(400, axh*0.94)), POS))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(lorentz(15, axh*0.94)), MUTED))

    # позначка f0
    p.append(line(f0x, oy, f0x, oy - axh*0.98, color=MUTED, sw=1, dash="3 3"))
    p.append(text(f0x, oy + 20, "f₀", size=13, color=INK))

    # легенда
    lx, ly = ox + axw - 210, oy - axh + 6
    p.append(line(lx, ly, lx+26, ly, color=INK, sw=2.6));   p.append(text(lx+32, ly+4, "кварц   Q ≈ 100 000", size=12, color=INK, anchor="start"))
    p.append(line(lx, ly+22, lx+26, ly+22, color=POS, sw=2.6)); p.append(text(lx+32, ly+26, "кераміка  Q ≈ 400", size=12, color=POS, anchor="start"))
    p.append(line(lx, ly+44, lx+26, ly+44, color=MUTED, sw=2.6)); p.append(text(lx+32, ly+48, "RC-контур  Q ≈ 15", size=12, color=MUTED, anchor="start"))

    tb, tw, th = textbox(W/2, H-24, "вузький пік → крута фаза → генератор тримає f₀ точно;  широкий пік → частота «пливе»",
                         size=12, fill="#f4faf5", stroke=FIELD, sw=1.4)
    p.append(tb)
    return render(os.path.join(OUT, 'q-shape.svg'), W, H, *p)


# ── 3. Температурна компенсація кремнію ──────────────────────────────────────
def fig_tcf():
    W, H = 720, 400
    p = []
    p.append(text(W/2, 26, "Кремній дрейфує — його компенсують у три способи", size=17, bold=True))

    ox, oy = 95, 250
    axw, axh = 540, 190
    # осі (0 в центрі по вертикалі = нульовий зсув)
    midy = oy - axh/2
    p.append(line(ox, oy, ox+axw, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ox, oy-axh, color=INK, sw=1.6))
    p.append(line(ox, midy, ox+axw, midy, color=MUTED, sw=1, dash="3 3"))
    p.append(text(ox+axw, oy+22, "температура, °C", size=12, color=MUTED, anchor="end"))
    p.append(text(ox-8, oy-axh+2, "Δf, ppm", size=12, color=MUTED, anchor="end"))
    p.append(text(ox-8, midy+4, "0", size=11, color=MUTED, anchor="end"))
    p.append(text(ox-8, oy+4, "−", size=12, color=MUTED, anchor="end"))
    # мітки T
    for frac, lab in [(0.0,"−40"),(0.5,"+25"),(1.0,"+85")]:
        xx = ox + frac*axw
        p.append(line(xx, oy, xx, oy+5, color=INK, sw=1.2))
        p.append(text(xx, oy+20, lab, size=11, color=MUTED))

    def curve(fn, color, sw=2.6, dash=None):
        pts = []
        Nn = 120
        for i in range(Nn+1):
            fr = i/Nn
            T = -40 + fr*125         # °C
            dppm = fn(T)
            xx = ox + fr*axw
            yy = midy - dppm * (axh*0.5/4200)   # масштаб: ±4200 ppm у півосі
            yy = max(oy-axh, min(oy, yy))
            pts.append("%.1f,%.1f" % (xx, yy))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (" ".join(pts), color, sw, d)

    # сирий кремній: ~ -30 ppm/°C лінійно від 25°C
    p.append(curve(lambda T: -30*(T-25), POS))
    # оксид SiO2: +50 ppm/°C (протилежний нахил)
    p.append(curve(lambda T: +50*(T-25), NEG, sw=1.8, dash="5 4"))
    # скомпенсований композит/легування: майже плаский, легка кубічна
    p.append(curve(lambda T: 0.0009*(T-25)**3 - 2*(T-25)*0.0, FIELD, sw=3.0))

    lx, ly = ox+14, oy-axh+2
    p.append(line(lx, ly, lx+24, ly, color=POS, sw=2.6));   p.append(text(lx+30, ly+4, "сирий кремній  ≈ −30 ppm/°C", size=12, color=POS, anchor="start"))
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" stroke-dasharray="5 4"/>' % (lx, ly+21, lx+24, ly+21, NEG))
    p.append(text(lx+30, ly+25, "шар SiO₂  ≈ +50 ppm/°C (протинахил)", size=12, color=NEG, anchor="start"))
    p.append(line(lx, ly+42, lx+24, ly+42, color=FIELD, sw=3.0)); p.append(text(lx+30, ly+46, "скомпенсовано  < ±1 ppm/°C", size=12, color=FIELD, anchor="start"))

    tb, tw, th = textbox(W/2, H-30, "три шляхи: композит Si+SiO₂ · важке легування n⁺ · активна поправка PLL за давачем T",
                         size=12, fill="#f4faf5", stroke=FIELD, sw=1.4)
    p.append(tb)
    return render(os.path.join(OUT, 'tcf-compensation.svg'), W, H, *p)


# ── 4. Розгойдування: Q задає час старту ─────────────────────────────────────
def fig_startup():
    W, H = 720, 360
    p = []
    p.append(text(W/2, 26, "Що вища Q, то повільніший старт: наростання за τ = 2Q/ω₀", size=16.5, bold=True))

    ox, oy = 80, 250
    axw, axh = 570, 200
    midy = oy - axh/2
    p.append(line(ox, oy, ox+axw, oy, color=INK, sw=1.6))
    p.append(line(ox, oy-axh, ox, oy, color=INK, sw=1.6))
    p.append(line(ox, midy, ox+axw, midy, color=MUTED, sw=0.8, dash="2 3"))
    p.append(text(ox+axw, oy+22, "час", size=12, color=MUTED, anchor="end"))
    p.append(text(ox-8, oy-axh+4, "амплітуда", size=12, color=MUTED, anchor="end"))

    def osc(tau_frac, color, fill_env=False):
        # обвідна 1-exp(-t/τ); всередині — швидкі коливання
        pts = []
        env_up = []
        env_dn = []
        Nn = 400
        tau = tau_frac * axw
        for i in range(Nn+1):
            t = i/Nn * axw
            env = (1 - math.exp(-t/tau))
            osc_v = math.sin(t/axw * 2*math.pi * 26)  # багато періодів
            yy = midy - env*osc_v*(axh*0.46)
            pts.append("%.1f,%.1f" % (ox+t, yy))
            env_up.append("%.1f,%.1f" % (ox+t, midy - env*(axh*0.46)))
            env_dn.append("%.1f,%.1f" % (ox+t, midy + env*(axh*0.46)))
        out = []
        if fill_env:
            out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.1" stroke-dasharray="4 3"/>' % (" ".join(env_up), color))
            out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.1" stroke-dasharray="4 3"/>' % (" ".join(env_dn), color))
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.7"/>' % (" ".join(pts), color))
        return out

    # кераміка/MEMS: швидко (мала τ)
    p += osc(0.06, MUTED)
    # кварц: повільно (велика τ), з обвідною
    p += osc(0.42, POS, fill_env=True)

    # позначки часу виходу на режим (кап у межах осі)
    mx1 = ox + axw*0.18
    mx2 = ox + axw*0.90
    p.append(line(mx1, oy, mx1, oy-axh*0.9, color=MUTED, sw=1, dash="3 3"))
    p.append(text(mx1, oy-axh*0.9-6, "кераміка/MEMS", size=11.5, color=MUTED))
    p.append(line(mx2, oy, mx2, oy-axh*0.9, color=POS, sw=1, dash="3 3"))
    p.append(text(mx2, oy-axh*0.9-6, "кварц ~7×", size=11.5, color=POS, anchor="middle"))

    tb, tw, th = textbox(W/2, H-26, "при високій Q енергія в петлі наростає повільно — тому камертон 32768 Гц стартує сотні мс",
                         size=12, fill="#fdf3f2", stroke=POS, sw=1.4)
    p.append(tb)
    return render(os.path.join(OUT, 'startup-envelope.svg'), W, H, *p)


# ── 5. Історія: чотири різні внески (ідея/матеріал/властивість/продукт) ───────
def fig_hist_contributions():
    W, H = 760, 430
    p = []
    p.append(text(W/2, 26, "Один винахід — чотири різні внески, чотири різні руки", size=17, bold=True))

    # чотири колонки-стовпці
    cols = [
        ("МАТЕРІАЛ",   "тверда суміш\nPbZrO₃ + PbTiO₃",  "Ваку й Хорі\nЯпонія, 1949",           FIELD, "#f1faf3"),
        ("ВЛАСТИВІСТЬ","сильна п'єзо-\nелектрика на MPB", "Б. Джаффе й ко.\nUS NBS, 1954",       NEG,   "#eef2fd"),
        ("ПРОДУКТ-1",  "перший керамічний\nфільтр (ліценз. PZT)", "Murata\nЯпонія, 1963",         POS,   "#fdeeec"),
        ("ПРОДУКТ-2",  "керамічний\nрезонатор — такт МК",  "галузь\n1970–80-ті",                 MUTED, "#f3f4f6"),
    ]
    n = len(cols)
    margin = 40
    gap = 18
    cw = (W - 2*margin - (n-1)*gap) / n
    top = 70
    box_h = 250
    for i, (tag, what, who, color, bg) in enumerate(cols):
        x = margin + i*(cw+gap)
        # рамка колонки
        p.append(rect(x, top, cw, box_h, fill=bg, stroke=color, sw=2, rx=8))
        # ярлик угорі
        p.append(text(x+cw/2, top+26, tag, size=13.5, color=color, bold=True))
        p.append(line(x+14, top+38, x+cw-14, top+38, color=color, sw=1.2))
        # що це
        p.append(mtext(x+cw/2, top+68, what, size=12.5, color=INK, lh=1.3))
        # хто/де/коли
        p.append(mtext(x+cw/2, top+box_h-52, who, size=12, color=color, lh=1.3, bold=True))
        # стрілка до наступної
        if i < n-1:
            ax = x + cw + 2
            p.append(arrow(ax, top+box_h/2, ax+gap-4, top+box_h/2, color=MUTED, sw=2))

    tb, tw, th = textbox(W/2, H-32,
        "мати матеріал ≠ побачити властивість ≠ зробити продукт ≠ знайти нове застосування",
        size=12.5, fill="#f7f7f9", stroke=MUTED, sw=1.4)
    p.append(tb)
    return render(os.path.join(OUT, 'hist-contributions.svg'), W, H, *p)


# ── 6. Історія: від фільтра до резонатора — та сама кераміка, дві ролі ─────────
def fig_hist_filter_to_resonator():
    W, H = 720, 380
    p = []
    p.append(text(W/2, 26, "Та сама п'єзокераміка: спершу фільтр, потім джерело такту", size=16.5, bold=True))

    def disc(cx, cy, r):
        # п'єзо-диск збоку: тонка «монета» з електродами
        out = []
        out.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#eef2f7" stroke="%s" stroke-width="1.8"/>'
                   % (cx, cy, r, r*0.34, LINE))
        out.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="1.2"/>'
                   % (cx, cy, r*0.62, r*0.2, MUTED))
        return "".join(out)

    # ЛІВА панель: фільтр — вузьке вікно в спектрі
    lx, ly = 60, 90
    lw, lh = 280, 210
    p.append(rect(lx, ly, lw, lh, fill="#fdeeec", stroke=POS, sw=1.8, rx=10))
    p.append(text(lx+lw/2, ly+26, "РОЛЬ 1 — ФІЛЬТР (радіо, 1963)", size=13, color=POS, bold=True))
    p.append(disc(lx+lw/2, ly+66, 40))
    # ось частоти зі смугою пропускання
    axo_x, axo_y = lx+30, ly+lh-40
    axo_w = lw-60
    p.append(line(axo_x, axo_y, axo_x+axo_w, axo_y, color=INK, sw=1.4))
    p.append(text(axo_x+axo_w, axo_y+18, "частота", size=11, color=MUTED, anchor="end"))
    # дзвін пропускання довкола 455 кГц
    pts = []
    Nn = 80
    for i in range(Nn+1):
        fr = i/Nn
        val = math.exp(-((fr-0.5)*7)**2)
        pts.append("%.1f,%.1f" % (axo_x+fr*axo_w, axo_y - val*60))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), POS))
    p.append(line(axo_x+0.5*axo_w, axo_y, axo_x+0.5*axo_w, axo_y-64, color=MUTED, sw=1, dash="3 3"))
    p.append(text(axo_x+0.5*axo_w, axo_y-70, "455 кГц", size=11, color=POS))
    p.append(text(lx+lw/2, ly+lh-8, "пропускає свій канал, глушить сусідні", size=11, color=MUTED))

    # ПРАВА панель: резонатор — джерело такту
    rx0, ry0 = 380, 90
    rw, rh = 280, 210
    p.append(rect(rx0, ry0, rw, rh, fill="#f1faf3", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(rx0+rw/2, ry0+26, "РОЛЬ 2 — РЕЗОНАТОР (такт МК)", size=13, color=FIELD, bold=True))
    p.append(disc(rx0+rw/2, ry0+66, 40))
    # інвертор + вихідний меандр
    gx, gy = rx0+40, ry0+130
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="#eef2f7" stroke="%s" stroke-width="1.6"/>'
             % (gx, gy-16, gx, gy+16, gx+28, gy, LINE))
    p.append(circle(gx+33, gy, 4, fill=BG, stroke=LINE, sw=1.4))
    p.append(text(gx+14, gy+34, "інвертор у чипі", size=10.5, color=MUTED))
    # меандр на виході
    mx, my = rx0+150, ry0+130
    mw = 100
    step = mw/8
    mpts = []
    hi, lo = my-16, my+16
    cur = lo
    mpts.append("%.1f,%.1f" % (mx, cur))
    for k in range(8):
        cur = hi if k % 2 == 0 else lo
        mpts.append("%.1f,%.1f" % (mx+k*step, cur))
        mpts.append("%.1f,%.1f" % (mx+(k+1)*step, cur))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(mpts), FIELD))
    p.append(text(rx0+rw/2, ry0+rh-8, "тримає одну частоту — задає ритм роботи", size=11, color=MUTED))

    # зв'язок між панелями
    p.append(arrow(lx+lw+4, ly+lh/2, rx0-4, ry0+rh/2, color=MUTED, sw=2.2))
    p.append(text((lx+lw+rx0)/2, ly+lh/2-10, "той самий", size=11, color=MUTED))
    p.append(text((lx+lw+rx0)/2, ly+lh/2+16, "п'єзорезонанс", size=11, color=MUTED))

    tb, tw, th = textbox(W/2, H-26,
        "фільтр і резонатор — одна фізика (гострий механічний резонанс), різне застосування",
        size=12, fill="#f7f7f9", stroke=MUTED, sw=1.4)
    p.append(tb)
    return render(os.path.join(OUT, 'hist-filter-to-resonator.svg'), W, H, *p)


# ── 7. Коефіцієнт трансдукції: зміщення як важіль на параболі F(U) ────────────
def fig_transduction_lever():
    W, H = 720, 400
    p = []
    p.append(text(W/2, 26, "Зміщення U_dc ставить робочу точку на схил параболи сили", size=16, bold=True))

    ox, oy = 90, 320
    axw, axh = 560, 250
    p.append(line(ox, oy, ox+axw, oy, color=INK, sw=1.6))            # X (U)
    p.append(line(ox, oy, ox, oy-axh, color=INK, sw=1.6))            # Y (F)
    p.append(text(ox+axw, oy+22, "напруга U", size=12, color=MUTED, anchor="end"))
    p.append(text(ox-8, oy-axh+2, "сила F ∝ U²", size=12, color=MUTED, anchor="end"))

    # парабола F = a·U², вершина у cx0 (U=0)
    cx0 = ox + 60
    a = axh                                # масштаб під нормовану вісь 0..1
    def par(u):                            # u у нормованих одиницях 0..1
        return max(oy-axh, oy - a*(u*u))
    def PX(u):
        return cx0 + u*(axw-90)
    pts = []
    Nn = 120
    for i in range(Nn+1):
        u = i/Nn
        pts.append("%.1f,%.1f" % (PX(u), par(u)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), INK))

    # робоча точка 1: біля вершини (без зміщення) — дотична майже плоска
    u1 = 0.08
    x1, y1 = PX(u1), par(u1)
    p.append(circle(x1, y1, 5, fill=NEG, stroke=NEG, sw=1))
    p.append(line(x1-30, y1, x1+30, y1, color=NEG, sw=1.4, dash="4 3"))
    p.append(text(x1+2, y1+34, "без зміщення:", size=11.5, color=NEG))
    p.append(text(x1+2, y1+50, "вихід ∝ u², мало", size=11, color=NEG))

    # робоча точка 2: на схилі (U_dc) — крута дотична = η
    u2 = 0.62
    x2, y2 = PX(u2), par(u2)
    # нахил параболи у px(y) на px(x): dF/dx = a·2u / (axw-90)
    sx = (a*2*u2)/(axw-90)
    dx = 88
    p.append(circle(x2, y2, 5, fill=POS, stroke=POS, sw=1))
    p.append(line(x2-dx, y2 + sx*dx, x2+dx, y2 - sx*dx, color=POS, sw=1.8))
    p.append(line(x2, oy, x2, y2, color=MUTED, sw=1, dash="3 3"))
    p.append(text(x2, oy+18, "U_dc", size=12, color=POS))
    p.append(text(x2+66, y2-16, "нахил = η", size=12, color=POS, anchor="start", bold=True))
    p.append(text(x2+66, y2+2, "= U_dc·εA/g₀²", size=11, color=POS, anchor="start"))

    tb, tw, th = textbox(W/2, H-22, "на схилі малий сигнал u дає лінійну силу F = η·u;  η ∝ U_dc — що вище зміщення, то дужчий важіль",
                         size=11.5, fill="#f4faf5", stroke=FIELD, sw=1.4)
    p.append(tb)
    return render(os.path.join(OUT, 'transduction-lever.svg'), W, H, *p)


# ── 8. Опір руху R₁ ∝ g⁴/(U_dc²·Q): чому прямий генератор важкий ──────────────
def fig_motional_resistance():
    W, H = 720, 380
    p = []
    p.append(text(W/2, 26, "Опір руху ємнісного MEMS росте як четвертий степінь зазору", size=15.5, bold=True))

    ox, oy = 95, 300
    axw, axh = 545, 225
    p.append(line(ox, oy, ox+axw, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ox, oy-axh, color=INK, sw=1.6))
    p.append(text(ox+axw, oy+22, "зазор g₀ (відносно)", size=12, color=MUTED, anchor="end"))
    p.append(text(ox-8, oy-axh+2, "R₁ (лог. масштаб)", size=12, color=MUTED, anchor="end"))

    def R(g): return g**4                     # R₁ ∝ g⁴ (відносно)
    gmin, gmax = 0.5, 2.0
    ylo = math.log10(R(gmin)); yhi = math.log10(R(gmax))
    def X(g): return ox + (g-gmin)/(gmax-gmin)*axw
    def Y(g): return oy - (math.log10(R(g))-ylo)/(yhi-ylo)*axh*0.90
    pts = []
    Nn = 120
    for i in range(Nn+1):
        g = gmin + (gmax-gmin)*i/Nn
        pts.append("%.1f,%.1f" % (X(g), Y(g)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), POS))

    for g, lab in [(0.5,"g₀/2"),(1.0,"g₀"),(2.0,"2·g₀")]:
        p.append(line(X(g), oy, X(g), oy+5, color=INK, sw=1.2))
        p.append(text(X(g), oy+20, lab, size=11.5, color=MUTED))
        p.append(line(X(g), oy, X(g), Y(g), color=MUTED, sw=0.8, dash="2 3"))
        p.append(circle(X(g), Y(g), 4, fill=POS, stroke=POS, sw=1))

    p.append(text(X(2.0)-6, Y(2.0)-14, "×2 зазору → ×16 опору", size=12, color=POS, anchor="end", bold=True))
    p.append(text(X(0.5)+8, Y(0.5)+20, "менший зазор → різко нижчий R₁", size=11.5, color=FIELD, anchor="start"))

    # рівень кварцу для порівняння — умовна лінія внизу
    yq = oy - 0.05*axh
    p.append(line(ox, yq, ox+axw, yq, color=NEG, sw=1.6, dash="6 4"))
    p.append(text(ox+axw-4, yq-6, "рівень кварцу ~десятки Ом", size=11, color=NEG, anchor="end"))

    tb, tw, th = textbox(W/2, H-22, "R₁ ∝ g₀⁴/(U_dc²·Q):  навіть за нанозазору R₁ у кілоомах — прямою схемою П'єрса не перекрити, звідси PLL",
                         size=11, fill="#fdf3f2", stroke=POS, sw=1.4)
    p.append(tb)
    return render(os.path.join(OUT, 'motional-resistance.svg'), W, H, *p)


if __name__ == '__main__':
    print(fig_standing_wave())
    print(fig_q_shape())
    print(fig_tcf())
    print(fig_startup())
    print(fig_hist_contributions())
    print(fig_hist_filter_to_resonator())
    print(fig_transduction_lever())
    print(fig_motional_resistance())
