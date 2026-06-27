# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), color, sw, d))


# ── Аналітика першого порядку ────────────────────────────────────────────────
# Lead:  C(s)=(1+a*T*s)/(1+T*s), a>1  → зсув фази додатний (випередження), горб.
# Lag :  C(s)=(1+T*s)/(1+a*T*s), a>1  → зсув фази від'ємний (відставання), яма.
# Фаза одного корнера 1/τ: atan(ω·τ). Сумарна фаза = фаза нуля − фаза полюса.

def lead_phase_deg(w, z, p):
    # нуль на z, полюс на p (z<p) → випередження
    return math.degrees(math.atan(w / z) - math.atan(w / p))


def lag_phase_deg(w, z, p):
    # нуль на z, полюс на p (z>p) → відставання (від'ємна фаза)
    return math.degrees(math.atan(w / z) - math.atan(w / p))


# ── Фігура 1: lead і lag — розміщення нуля/полюса й що з фазою ────────────────

def fig_lead_lag_map():
    W, H = 760, 360
    p = []

    # Два частотних рядки-осі (лог), на кожному відмічаємо нуль і полюс,
    # і малюємо криву фази над ним: горб (lead) і яму (lag).
    def axis(y0, title, color, z_lab, p_lab, phase_fn, z, pl, bump_up):
        q = []
        ox, ax = 110, 540
        # вісь частоти
        q.append(arrow(ox, y0, ox + ax, y0, color=INK, sw=1.6))
        q.append(text(ox + ax, y0 + 18, "частота ω (лог)", size=10.5, color=INK, anchor="end"))
        # позиції нуля й полюса на осі (лог-розкладка від 0.1 до 100)
        def X(w):
            return ox + ax * (math.log10(w) - (-1.0)) / (2.0 - (-1.0))
        zx, px = X(z), X(pl)
        # крива фази над віссю
        H_ph = 64
        pts = []
        wmin, wmax = 0.1, 100.0
        steps = 120
        vals = []
        for i in range(steps + 1):
            lw = math.log10(wmin) + (math.log10(wmax) - math.log10(wmin)) * i / steps
            w = 10 ** lw
            vals.append(abs(phase_fn(w, z, pl)))
        vmax = max(vals) or 1.0
        for i in range(steps + 1):
            lw = math.log10(wmin) + (math.log10(wmax) - math.log10(wmin)) * i / steps
            w = 10 ** lw
            ph = abs(phase_fn(w, z, pl))
            x = ox + ax * i / steps
            yy = (y0 - 30) - H_ph * (ph / vmax) if bump_up else (y0 + 30) + H_ph * (ph / vmax)
            pts.append((x, yy))
        q.append(polyline(pts, color=color, sw=2.6))
        # маркери нуля (○) і полюса (×)
        q.append(circle(zx, y0, 5, fill=BG, stroke=FIELD, sw=2.4))
        q.append(text(zx, y0 + (22 if bump_up else 0) - (0 if bump_up else 16), z_lab, size=10, color=FIELD, bold=True))
        q.append(text(px - 6, y0 + 4, "×", size=15, color=POS, bold=True))
        q.append(text(px, y0 + (22 if bump_up else 0) - (0 if bump_up else 16), p_lab, size=10, color=POS, bold=True))
        # підпис кривої
        peak_x = (zx + px) / 2
        peak_y = (y0 - 30 - H_ph - 6) if bump_up else (y0 + 30 + H_ph + 16)
        q.append(text(peak_x, peak_y, title, size=11, color=color, bold=True))
        return q

    p += axis(120, "горб ВИПЕРЕДЖЕННЯ фази (+)", FIELD, "нуль (ближче)", "полюс", lead_phase_deg, 2.0, 12.0, True)
    p += axis(250, "яма ВІДСТАВАННЯ фази (−)", NEG, "нуль", "полюс (ближче)", lag_phase_deg, 12.0, 2.0, False)

    # роздільна підказка зліва
    p.append(text(56, 120, "LEAD", size=12, color=FIELD, bold=True))
    p.append(text(56, 250, "LAG", size=12, color=NEG, bold=True))

    render(os.path.join(OUT, "lead-lag-map.svg"), W, H, *p,
           title="Lead і lag: де нуль, де полюс — і що з фазою")


# ── Фігура 2: чому lead кращий за сирий диференціал (обмежений горб) ──────────

def fig_lead_vs_derivative():
    W, H = 760, 330
    p = []
    ox, oy = 90, 250
    top = 58
    ax = 600
    H_ph = 150

    p.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + ax, oy, color=INK, sw=1.6))
    p.append(text(ox + ax, oy + 18, "частота ω (лог)", size=11, color=INK, anchor="end"))
    p.append(text(ox + 6, top + 4, "підсилення |C|", size=11, color=INK, anchor="start"))

    wmin, wmax = 0.1, 100.0
    steps = 140

    def X(i):
        return ox + ax * i / steps

    # Диференціал: |C| росте без меж (∝ ω) — підкачує шум на верхах
    pts_d = []
    for i in range(steps + 1):
        lw = math.log10(wmin) + (math.log10(wmax) - math.log10(wmin)) * i / steps
        w = 10 ** lw
        g = 0.15 * w  # ∝ ω
        yy = oy - H_ph * min(1.0, g / 8.0)
        pts_d.append((X(i), yy))
    p.append(polyline(pts_d, color=POS, sw=2.6))

    # Lead: |C| росте, але ВИПОЛОЖУЄТЬСЯ на плато (полюс ловить ріст)
    z, pl = 2.0, 18.0
    pts_l = []
    for i in range(steps + 1):
        lw = math.log10(wmin) + (math.log10(wmax) - math.log10(wmin)) * i / steps
        w = 10 ** lw
        g = math.sqrt((1 + (w / z) ** 2) / (1 + (w / pl) ** 2))  # |lead|
        yy = oy - H_ph * min(1.0, (g - 1.0) / 8.0)
        pts_l.append((X(i), yy))
    p.append(polyline(pts_l, color=FIELD, sw=2.8))

    # рівень плато lead (підпис)
    plat_y = pts_l[-1][1]
    p.append(line(ox, plat_y, ox + ax, plat_y, color=FIELD, sw=1.2, dash="4 4"))
    p.append(text(ox + ax - 4, plat_y - 8, "плато: ріст СПИНЯЄ полюс", size=10, color=FIELD, anchor="end", bold=True))

    # легенда
    lx = ox + 30
    p.append(line(lx, top + 8, lx + 26, top + 8, color=POS, sw=2.6))
    p.append(text(lx + 32, top + 12, "сирий диференціал: підсилення росте без меж → шум", size=10, color=POS, anchor="start", bold=True))
    p.append(line(lx, top + 28, lx + 26, top + 28, color=FIELD, sw=2.8))
    p.append(text(lx + 32, top + 32, "lead: те саме випередження, але підсилення обмежене", size=10, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "lead-vs-derivative.svg"), W, H, *p,
           title="Lead проти сирого диференціала: однакове випередження, без розгону шуму")


# ── Фігура 3: lead додає запас по фазі рівно на кросовері ─────────────────────

def fig_phase_margin_boost():
    W, H = 760, 420
    p = []
    ox = 90
    ax = 600
    wmin, wmax = 0.1, 100.0
    steps = 160

    def X(i):
        return ox + ax * i / steps

    # верхня панель: фаза петлі
    oy1 = 175
    top1 = 70
    p.append(arrow(ox, oy1, ox, top1, color=INK, sw=1.5))
    p.append(arrow(ox, oy1, ox + ax, oy1, color=INK, sw=1.5))
    p.append(text(ox + 6, top1 + 2, "фаза петлі", size=10.5, color=INK, anchor="start"))
    # рівень −180°
    y180 = oy1 - 8
    p.append(line(ox, y180 - 95, ox + ax, y180 - 95, color=MUTED, sw=1.2, dash="6 4"))
    p.append(text(ox + ax + 2, y180 - 95 + 4, "−180°", size=9.5, color=MUTED, anchor="start"))

    # базова фаза петлі (сповзає до −180) і фаза з lead (горб угору біля кросовера)
    z, pl = 4.0, 30.0
    wc = 11.0  # частота кросовера

    def base_phase(w):
        # від 0 до ~−200°: два інерційні корнери + трохи затримки
        return -(math.degrees(math.atan(w / 1.2)) + math.degrees(math.atan(w / 6.0)) + 0.9 * w)

    def lead_extra(w):
        return lead_phase_deg(w, z, pl)

    def Yph(ph):
        # масштаб: 0° на top1+10, −180° на y180-95
        return (top1 + 10) + (ph - 0.0) / (-180.0) * ((y180 - 95) - (top1 + 10))

    pts_b = []
    pts_c = []
    for i in range(steps + 1):
        lw = math.log10(wmin) + (math.log10(wmax) - math.log10(wmin)) * i / steps
        w = 10 ** lw
        pts_b.append((X(i), Yph(base_phase(w))))
        pts_c.append((X(i), Yph(base_phase(w) + lead_extra(w))))
    p.append(polyline(pts_b, color=POS, sw=2.4))
    p.append(polyline(pts_c, color=FIELD, sw=2.8))

    # вертикаль кросовера
    def Xw(w):
        lw = math.log10(w)
        return ox + ax * (lw - math.log10(wmin)) / (math.log10(wmax) - math.log10(wmin))
    xc = Xw(wc)
    p.append(line(xc, top1, xc, 360, color=MUTED, sw=1.2, dash="3 3"))
    p.append(text(xc, 372, "кросовер (|L|=1)", size=10, color=MUTED, bold=True))

    # дужки запасу по фазі на кросовері
    yb = Yph(base_phase(wc))
    yc = Yph(base_phase(wc) + lead_extra(wc))
    p.append(line(xc - 4, yb, xc - 4, Yph(-180.0), color=POS, sw=2.2))
    p.append(text(xc - 10, (yb + Yph(-180.0)) / 2, "запас (без lead)", size=9, color=POS, anchor="end", bold=True))
    p.append(line(xc + 4, yc, xc + 4, Yph(-180.0), color=FIELD, sw=2.6))
    p.append(text(xc + 10, (yc + Yph(-180.0)) / 2 - 8, "запас (з lead) — БІЛЬШИЙ", size=9, color=FIELD, anchor="start", bold=True))

    # нижня панель: відгук у часі
    oy2 = 400
    top2 = 300
    p.append(arrow(ox, oy2, ox, top2, color=INK, sw=1.5))
    p.append(arrow(ox, oy2, ox + ax, oy2, color=INK, sw=1.5))
    p.append(text(ox + ax, oy2 + 16, "час", size=10.5, color=INK, anchor="end"))
    yset = top2 + 18
    p.append(line(ox, yset, ox + ax, yset, color=MUTED, sw=1.4, dash="6 4"))
    p.append(text(ox + ax + 2, yset + 4, "завдання", size=9.5, color=MUTED, anchor="start"))

    # дві криві перехідного процесу: розгойдана (мало запасу) і чиста (з lead)
    def step_resp(damp, wn, n=200, dt=0.06):
        # коливальна ланка 2-го порядку, дискретно
        y = 0.0; v = 0.0; out = []
        for _ in range(n):
            a = wn * wn * (1.0 - y) - 2 * damp * wn * v
            v += a * dt; y += v * dt
            out.append(y)
        return out

    def draw_resp(data, color, sw):
        N = len(data)
        pts = []
        for i, yv in enumerate(data):
            x = ox + ax * i / (N - 1)
            yy = oy2 - (oy2 - yset) * yv
            pts.append((x, yy))
        return polyline(pts, color=color, sw=sw)

    p.append(draw_resp(step_resp(0.18, 2.2), POS, 2.4))   # мало запасу — дзвенить
    p.append(draw_resp(step_resp(0.6, 2.2), FIELD, 2.8))  # з lead — чисто

    p.append(text(ox + ax * 0.62, top2 + 8, "без lead: переліт і дзвін", size=10, color=POS, anchor="start", bold=True))
    p.append(text(ox + ax * 0.62, top2 + 24, "з lead: чистий, швидкий доїзд", size=10, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "phase-margin-boost.svg"), W, H, *p,
           title="Lead підіймає фазу рівно на кросовері → більший запас, менший дзвін")


# ── Фігура 4: де компенсатор стоїть у петлі й що рахує код ────────────────────

def fig_loop_placement():
    W, H = 760, 300
    p = []
    y = 112
    # вузол порівняння
    p.append(text(70, y + 4, "завдання r", size=10.5, color=INK, anchor="middle"))
    p.append(minus(150, y, 13))
    p.append(arrow(95, y, 137, y, color=INK, sw=1.8))
    # компенсатор
    cx = 250
    p.append(fitbox(cx - 60, y - 34, 120, 68, "", fill="#eafaf0", stroke=FIELD, sw=2.0))
    p.append(text(cx, y - 12, "LEAD/LAG", size=12, color=FIELD, bold=True))
    p.append(text(cx, y + 8, "компенсатор", size=10, color=INK))
    p.append(text(cx, y + 24, "C(z)", size=11, color=FIELD, bold=True))
    p.append(arrow(163, y, cx - 62, y, color=INK, sw=1.8))
    p.append(text(195, y - 8, "e", size=11, color=INK, anchor="middle", italic=True))
    # об'єкт
    px = 470
    p.append(rect(px - 62, y - 34, 124, 68, fill="#dce4f2", stroke=INK, sw=1.8, rx=5))
    p.append(text(px, y - 6, "об'єкт", size=12, color=INK, bold=True))
    p.append(text(px, y + 14, "(мотор, плече…)", size=9.5, color=MUTED))
    p.append(arrow(cx + 62, y, px - 64, y, color=INK, sw=1.8))
    p.append(text(cx + 105, y - 8, "u", size=11, color=INK, anchor="middle", italic=True))
    # вихід
    p.append(arrow(px + 62, y, px + 150, y, color=INK, sw=1.8))
    p.append(text(px + 150, y - 8, "вихід y", size=10.5, color=INK, anchor="middle"))
    # зворотний зв'язок
    fbx = px + 110
    p.append(line(fbx, y, fbx, y + 80, color=INK, sw=1.6))
    p.append(line(fbx, y + 80, 150, y + 80, color=INK, sw=1.6))
    p.append(arrow(150, y + 80, 150, y + 14, color=INK, sw=1.6))
    p.append(text((fbx + 150) / 2, y + 96, "вимір y (давач)", size=10, color=MUTED, bold=True))

    # рамка-формула різницевого рівняння
    p.append(fitbox(160, y + 128, 440, 46,
                    "код щотакту:  u = b0·e + b1·e_prev − a1·u_prev",
                    size=12, fill="#f6f4ec", stroke=INK, sw=1.6, bold=True))
    p.append(text(380, y + 186, "три коефіцієнти, два збережені значення — увесь компенсатор",
                  size=10, color=MUTED))

    render(os.path.join(OUT, "loop-placement.svg"), W, H, *p,
           title="Де стоїть компенсатор і що рахує код")


# ── Історія, фіг. A: як методи Bell перейшли з телефону в наведення ───────────

def fig_hist_transfer():
    W, H = 780, 430
    p = []

    # Ліва колонка — телефонна задача Bell Labs; права — наведення MIT.
    # Стрілки-«перенесення» показують, який інструмент перейшов.
    def box(cx, cy, w, h, title, sub, fill, stroke):
        out = rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, sw=2.0, rx=7)
        if "\n" in title:
            out += mtext(cx, cy - 8, title, size=12.0, color=INK, bold=True, lh=1.2)
        else:
            out += text(cx, cy - 6, title, size=12.5, color=INK, bold=True)
        if sub:
            out += text(cx, cy + 14, sub, size=9.5, color=MUTED)
        return out

    # заголовки колонок
    p.append(text(195, 60, "Bell Labs: телефон на тисячі км", size=12.5, color=NEG, bold=True))
    p.append(text(590, 60, "MIT: наведення на ціль", size=12.5, color=FIELD, bold=True))
    p.append(line(390, 74, 390, 396, color=MUTED, sw=1.0, dash="3 5"))

    # ліва колонка (Bell)
    p.append(box(195, 110, 290, 50, "Підсилювач спотворює голос",
                 "десятки ламп на трасі → каша", "#eaf0fd", NEG))
    p.append(box(195, 185, 290, 50, "Блек, 1927: від'ємний зв'язок",
                 "віддати підсилення за чистоту", "#eaf0fd", NEG))
    p.append(box(195, 260, 290, 50, "Найквіст, 1932: чи зірветься?",
                 "крива в комплексній площині", "#eaf0fd", NEG))
    p.append(box(195, 335, 290, 50, "Боде, 1945: запас фази й підсил.",
                 "діаграми підсилення й фази", "#eaf0fd", NEG))

    # стрілки вниз у лівій колонці
    for y1, y2 in [(135, 160), (210, 235), (285, 310)]:
        p.append(arrow(195, y1, 195, y2, color=NEG, sw=1.6))

    # права колонка (MIT)
    p.append(box(590, 110, 290, 50, "Гармата мляво або розгойдується",
                 "ціль швидка, ціна — збитий літак", "#eafaf0", FIELD))
    p.append(box(590, 235, 290, 60, "Голл, 1943 (таємно): частотний\nпогляд + ланка випередження",
                 "", "#eafaf0", FIELD))
    p.append(box(590, 340, 290, 50, "Браун і Кемпбелл, 1948",
                 "lead/lag — у підручнику", "#eafaf0", FIELD))
    p.append(arrow(590, 265, 590, 315, color=FIELD, sw=1.6))

    # «перенесення» інструменту: Найквіст/Боде → Голл
    p.append(arrow(340, 260, 446, 235, color=POS, sw=2.4))
    p.append(arrow(340, 335, 446, 250, color=POS, sw=2.0))
    p.append(text(390, 198, "ті самі частотні", size=10, color=POS, bold=True))
    p.append(text(390, 213, "інструменти →", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "hist-transfer.svg"), W, H, *p,
           title="Частотні методи перейшли з телефонних підсилювачів у наведення гармат")


# ── Історія, фіг. B: ідея Голла — читати замкнений контур з кривої розімкненого ─

def fig_hist_hall_circles():
    W, H = 720, 400
    p = []
    cx, cy = 300, 220
    R = 150

    # осі комплексної площини (площина розімкненої петлі L)
    p.append(arrow(cx - R - 30, cy, cx + R + 30, cy, color=INK, sw=1.5))
    p.append(arrow(cx, cy + R + 30, cx, cy - R - 30, color=INK, sw=1.5))
    p.append(text(cx + R + 28, cy + 18, "Re L", size=10.5, color=INK, anchor="end"))
    p.append(text(cx + 14, cy - R - 18, "Im L", size=10.5, color=INK, anchor="start"))
    # критична точка −1
    p.append(circle(cx - R * 0.62, cy, 4, fill=POS, stroke=POS, sw=1.5))
    p.append(text(cx - R * 0.62, cy + 18, "−1", size=11, color=POS, bold=True))

    # крива розімкненої петлі (Найквістів годограф) — спадна спіраль у III квадрант
    import math as _m
    pts = []
    for i in range(80):
        t = i / 79.0
        ang = _m.pi * (0.05 + 1.15 * t)          # від ~0 до ~−210° (за год. стрілкою донизу)
        rad = R * (0.95 - 0.7 * t)
        x = cx + rad * _m.cos(-ang)
        y = cy + rad * _m.sin(-ang)
        pts.append((x, y))
    p.append(polyline(pts, color=NEG, sw=2.8))
    p.append(text(cx + R * 0.5, cy - R * 0.62, "крива розімкненої L(jω)", size=10, color=NEG, bold=True))

    # M-кола Голла: кола сталого |замкненого| підсилення (намалюємо 2 для ідеї)
    # M-коло для M має центр і радіус за відомими формулами; тут — схематично.
    for (mc, ry, rr, lab) in [(0.78, cx - R * 0.42, R * 0.55, "M=1.3"),
                              (0.62, cx - R * 0.70, R * 0.30, "M=2")]:
        p.append(circle(ry, cy, rr, fill="none", stroke=FIELD, sw=2.0))
    p.append(text(cx - R * 0.42, cy - R * 0.55 - 6, "M-коло: |замкн.|=const", size=10, color=FIELD, anchor="middle", bold=True))

    # точка дотику — резонансний пік замкненого контуру
    p.append(circle(cx - R * 0.86, cy + R * 0.18, 5, fill=BG, stroke=POS, sw=2.4))
    p.append(mtext(cx - R * 0.86, cy + R * 0.40, ["дотик → пік", "замкненого"], size=9, color=POS, bold=True, lh=1.2))

    # підпис-висновок праворуч
    p.append(fitbox(500, 120, 200, 200,
                    "Ідея Голла:\n\nнакласти M-кола на\nкриву розімкненої\nпетлі — і ПРЯМО\nпрочитати, який\nпік дасть\nЗАМКНЕНИЙ контур\n\nстабільність —\nз однієї картинки",
                    size=11, fill="#fbfbf6", stroke=MUTED, sw=1.4, color=INK))

    render(os.path.join(OUT, "hist-hall-circles.svg"), W, H, *p,
           title="М-кола Голла (1943): замкнений контур читають із кривої розімкненого")


# ── Історія, фіг. C: стрічка часу 1927→1948 ──────────────────────────────────

def fig_hist_timeline():
    W, H = 800, 290
    p = []
    ox, ax = 70, 660
    y = 150
    p.append(line(ox, y, ox + ax, y, color=INK, sw=2.2))

    yr0, yr1 = 1925, 1949
    def X(yr):
        return ox + ax * (yr - yr0) / (yr1 - yr0)

    marks = [
        (1927, "Блек\nвід'ємний\nзв'язок", NEG, True),
        (1932, "Найквіст\nкритерій\nстійкості", NEG, False),
        (1934, "Гейзен\nтеорія\nсерво", MUTED, True),
        (1940, "Серво-\nлабораторія\nMIT (Браун)", FIELD, False),
        (1943, "Голл\nчастотний\nметод (таємно)", FIELD, True),
        (1945, "Боде\nзапас\nфази", NEG, False),
        (1948, "Браун-\nКемпбелл\nпідручник", FIELD, True),
    ]
    for yr, lab, col, up in marks:
        x = X(yr)
        p.append(circle(x, y, 6, fill=col, stroke=col, sw=1.5))
        p.append(text(x, y + (-14 if up else 26), str(yr), size=11, color=INK, bold=True))
        ty = (y - 30) if up else (y + 40)
        p.append(mtext(x, ty - (24 if up else 0), lab, size=9, color=col, bold=True, lh=1.15))

    # дві смуги-походження
    p.append(text(ox, 250, "Bell Labs (телефон): синє      MIT (наведення): зелене", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Двадцять років: від телефонного підсилювача до lead/lag у підручнику")


if __name__ == "__main__":
    fig_lead_lag_map()
    fig_lead_vs_derivative()
    fig_phase_margin_boost()
    fig_loop_placement()
    fig_hist_transfer()
    fig_hist_hall_circles()
    fig_hist_timeline()
    print("OK: figures written to", OUT)
