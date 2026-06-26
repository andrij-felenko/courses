# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── systematic-vs-random: два почерки похибки на мішені ───────────────────────
# Ідея: систематична зміщує ВСІ постріли в один бік (можна відняти);
# випадкова РОЗКИДАЄ їх навколо (можна усереднити). Це два різні вороги.

def _shots(cx, cy, pts, color):
    out = ""
    for dx, dy in pts:
        out += circle(cx + dx, cy + dy, 3.4, fill=color, stroke="none", sw=1)
    return out

def _target(cx, cy, r=46):
    out = circle(cx, cy, r, fill=BG, stroke=MUTED, sw=1.3)
    out += circle(cx, cy, r * 0.62, fill=BG, stroke=MUTED, sw=1.1)
    out += circle(cx, cy, r * 0.24, fill="#f1f2f4", stroke=INK, sw=1.3)
    out += line(cx - r - 8, cy, cx + r + 8, cy, color="#d0d4da", sw=0.9)
    out += line(cx, cy - r - 8, cx, cy + r + 8, color="#d0d4da", sw=0.9)
    return out

def fig_systematic_vs_random():
    W, H = 760, 360
    p = []
    p.append(text(W / 2, 50, "Те, що зміщує всі покази однаково, — і те, що їх розкидає",
                  size=13, color=MUTED))
    cys = 200
    xs = [180, 410, 640]

    # 1) випадкова: розкид навколо центру
    cx = xs[0]
    p.append(text(cx, 108, "Випадкова", size=13.5, color=NEG, bold=True))
    p.append(_target(cx, cys))
    rnd = [(-14, 9), (11, -12), (-6, -16), (17, 6), (-19, -4),
           (4, 15), (9, 12), (-11, -8), (2, -7), (13, -2)]
    p.append(_shots(cx, cys, rnd, NEG))
    p.append(text(cx, cys + 78, "довкола істини — усереднити", size=11, color=NEG, bold=True))

    # 2) систематична: щільна купка, але збоку
    cx = xs[1]
    p.append(text(cx, 108, "Систематична", size=13.5, color=POS, bold=True))
    p.append(_target(cx, cys))
    sysoff = (24, -20)
    sysc = [(-5, 4), (3, -3), (-2, -5), (5, 2), (0, 0), (-4, -1), (2, 4)]
    p.append(_shots(cx, cys, [(dx + sysoff[0], dy + sysoff[1]) for dx, dy in sysc], POS))
    p.append(arrow(cx, cys, cx + sysoff[0] - 4, cys + sysoff[1] + 4, color=POS, sw=1.6))
    p.append(text(cx, cys + 78, "зсунута вбік — відняти", size=11, color=POS, bold=True))

    # 3) обидві разом
    cx = xs[2]
    p.append(text(cx, 108, "Обидві разом", size=13.5, color=INK, bold=True))
    p.append(_target(cx, cys))
    both = [(dx + sysoff[0], dy + sysoff[1]) for dx, dy in rnd]
    p.append(_shots(cx, cys, both, INK))
    p.append(text(cx, cys + 78, "і зсунуто, і розкидано", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "systematic-vs-random.svg"), W, H, *p,
           title="Дві природи похибки: зсув і розкид")


# ── budget-rows: бюджет як таблиця внесків ───────────────────────────────────
# Ідея: похибку розкладають на рядки-джерела; кожен має тип (S/R) і величину;
# систематичні складають у стовпчик, випадкові — у квадратурі.

def fig_budget_rows():
    W, H = 760, 392
    p = []
    p.append(text(W / 2, 50, "Кожне джерело — окремий рядок; тип вирішує, як його складати",
                  size=13, color=MUTED))
    x0, y0 = 70, 86
    rw, rh = 620, 34
    gap = 6
    # шапка
    p.append(rect(x0, y0, rw, rh, fill="#eef2ff", stroke=INK, sw=1.3))
    p.append(text(x0 + 16, y0 + 22, "джерело похибки", size=12, color=INK, anchor="start", bold=True))
    p.append(text(x0 + 392, y0 + 22, "тип", size=12, color=INK, anchor="middle", bold=True))
    p.append(text(x0 + rw - 16, y0 + 22, "внесок", size=12, color=INK, anchor="end", bold=True))

    rows = [
        ("швидкість звуку (температура)", "S", "±9 мм", POS),
        ("зсув нуля (затримка схеми)", "S", "+4 мм", POS),
        ("крок таймера (квантування)", "R", "±1 мм", NEG),
        ("джитер засічки (шум)", "R", "±3 мм", NEG),
        ("ціль / кут відбиття", "R", "±6 мм", NEG),
    ]
    y = y0 + rh + gap
    for name, t, val, col in rows:
        p.append(rect(x0, y, rw, rh, fill=BG, stroke=MUTED, sw=1.1))
        p.append(text(x0 + 16, y + 22, name, size=11.5, color=INK, anchor="start"))
        tag_fill = "#fdecea" if t == "S" else "#eaf0fd"
        p.append(rect(x0 + 372, y + 7, 40, 20, fill=tag_fill, stroke=col, sw=1.3, rx=4))
        p.append(text(x0 + 392, y + 21, t, size=12, color=col, anchor="middle", bold=True))
        p.append(text(x0 + rw - 16, y + 22, val, size=11.5, color=col, anchor="end", bold=True))
        y += rh + gap

    # легенда
    p.append(text(x0, y + 18, "S — систематична (складають у стовпчик або калібрують)",
                  size=10.5, color=POS, anchor="start"))
    p.append(text(x0, y + 34, "R — випадкова (складають у квадратурі: √(Σ внесок²))",
                  size=10.5, color=NEG, anchor="start"))

    render(os.path.join(OUT, "budget-rows.svg"), W, H, *p,
           title="Бюджет похибок — таблиця внесків")


# ── rss-vs-sum: чому квадратура, а не проста сума ─────────────────────────────
# Ідея: незалежні випадкові внески частково гасять один одного, тож сумуються
# в квадратурі; результат менший за лінійну суму й керується найбільшим.

def fig_rss_vs_sum():
    W, H = 760, 360
    p = []
    p.append(text(W / 2, 50, "Незалежні розкиди частково гасяться — тож складають катети, не довжини",
                  size=12.5, color=MUTED))
    # лівий бік: лінійна сума (стовпчик)
    bx = 120
    base = 280
    scale = 9.0
    a, b = 6.0, 3.0          # два внески, мм
    p.append(text(bx, 100, "Проста сума (надто песимістично)", size=12, color=MUTED, bold=False))
    # стовпчик a
    p.append(rect(bx - 22, base - a * scale, 44, a * scale, fill="#eaf0fd", stroke=NEG, sw=1.3))
    p.append(text(bx, base - a * scale - 8, "6", size=11, color=NEG, bold=True))
    # стовпчик b зверху
    p.append(rect(bx - 22, base - (a + b) * scale, 44, b * scale, fill="#dfe7fb", stroke=NEG, sw=1.3))
    p.append(text(bx, base - (a + b) * scale - 8, "+3", size=11, color=NEG, bold=True))
    p.append(line(bx - 40, base, bx + 40, base, color=INK, sw=1.4))
    p.append(text(bx, base + 20, "6 + 3 = 9 мм", size=12, color=MUTED, anchor="middle", bold=True))

    # правий бік: квадратура як гіпотенуза прямокутного трикутника
    ox, oy = 470, 280
    la, lb = a * scale, b * scale
    # катети
    p.append(line(ox, oy, ox + la, oy, color=NEG, sw=2.4))                    # 6 уздовж
    p.append(line(ox + la, oy, ox + la, oy - lb, color=NEG, sw=2.4))          # 3 угору
    # гіпотенуза
    p.append(line(ox, oy, ox + la, oy - lb, color=POS, sw=2.8))
    # прямий кут
    p.append(rect(ox + la - 8, oy - 8, 8, 8, fill="none", stroke=MUTED, sw=1.0, rx=0))
    p.append(text(ox + la / 2, oy + 18, "6", size=11, color=NEG, bold=True))
    p.append(text(ox + la + 14, oy - lb / 2, "3", size=11, color=NEG, anchor="start", bold=True))
    rss = math.sqrt(a * a + b * b)
    p.append(text(ox + la / 2 - 20, oy - lb / 2 - 8, "√(6²+3²)", size=11.5, color=POS, anchor="end", bold=True))
    p.append(text(470 + 30, 100, "Квадратура (чесно)", size=12, color=POS, bold=True))
    p.append(text(ox + 10, oy + 44, "= %.1f мм — менше за 9, ближче до більшого внеску" % rss,
                  size=11.5, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "rss-vs-sum.svg"), W, H, *p,
           title="Випадкові внески складають у квадратурі")


# ── dominant-term: найбільший внесок з'їдає решту ────────────────────────────
# Ідея: у квадратурі дрібні внески майже не чути; полірувати треба найбільший.

def fig_dominant_term():
    W, H = 720, 330
    p = []
    p.append(text(W / 2, 48, "У квадратурі дрібні внески майже не чути — лагодь найбільший",
                  size=13, color=MUTED))
    x0, base = 120, 250
    bw, gap = 70, 26
    comps = [("шум\nзасічки", 3.0, NEG), ("крок\nтаймера", 1.0, NEG),
             ("ціль", 6.0, NEG)]
    scale = 24.0
    x = x0
    sq = 0.0
    for name, v, col in comps:
        h = v * scale
        p.append(rect(x, base - h, bw, h, fill="#eaf0fd", stroke=col, sw=1.4))
        p.append(text(x + bw / 2, base - h - 8, "%.0f" % v, size=11.5, color=col, bold=True))
        p.append(mtext(x + bw / 2, base + 18, name, size=10, color=INK, lh=1.15))
        sq += v * v
        x += bw + gap

    # підсумковий стовпчик
    total = math.sqrt(sq)
    x += 18
    h = total * scale
    p.append(rect(x, base - h, bw, h, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(x + bw / 2, base - h - 8, "%.1f" % total, size=12, color=POS, bold=True))
    p.append(mtext(x + bw / 2, base + 18, "разом\n√Σ", size=10, color=POS, lh=1.15, bold=True))
    p.append(line(x0 - 14, base, x + bw + 14, base, color=INK, sw=1.4))

    # стрілка-висновок
    p.append(text(W / 2, 300, "разом ≈ 6.8 мм — майже та сама «ціль»; шум і таймер тонуть",
                  size=11.5, color=POS, bold=True))

    render(os.path.join(OUT, "dominant-term.svg"), W, H, *p,
           title="Квадратурою керує найбільший доданок")


# ── linearization: похибка входу йде на вихід через нахил дотичної ────────────
# Ідея закону поширення: гладку f(x) на ділянці розкиду входу заміняють прямою-
# дотичною; тоді розкид входу σ_x перетворюється на розкид виходу нахилом
# (∂f/∂x)·σ_x. Це і є «коефіцієнт чутливості».

def fig_linearization():
    W, H = 760, 430
    p = []
    p.append(text(W / 2, 52, "На вузькій смузі розкиду криву заміняє її дотична — нахил і переносить похибку",
                  size=12.5, color=MUTED))

    # осі
    ox, oy = 110, 330          # початок координат (лівий-низ)
    axw, axh = 560, 250
    p.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.6))         # вісь x
    p.append(line(ox, oy, ox, oy - axh, color=INK, sw=1.6))         # вісь f
    p.append(text(ox + axw, oy + 22, "вхід x", size=12, color=INK, anchor="end"))
    p.append(text(ox - 14, oy - axh + 4, "f(x)", size=12, color=INK, anchor="end"))

    # крива f(x) — щось гладко-зростаюче й опукле
    import math as _m
    def fx(t):  # t у [0,1] -> екранний y
        return oy - axh * (0.12 + 0.80 * (t ** 1.55))
    pts = []
    for i in range(0, 101):
        t = i / 100.0
        pts.append((ox + axw * t, fx(t)))
    path = "M " + " L ".join("%.1f %.1f" % pq for pq in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path, INK))

    # робоча точка
    t0 = 0.52
    x0 = ox + axw * t0
    y0 = fx(t0)
    p.append(circle(x0, y0, 4.5, fill=FIELD, stroke=INK, sw=1.4))
    p.append(text(x0 + 8, y0 - 10, "робоча точка", size=10.5, color=FIELD, anchor="start", bold=True))

    # дотична в робочій точці (числовий нахил)
    h = 0.001
    slope = (fx(t0 + h) - fx(t0 - h)) / (2 * h * axw)  # екранний нахил dy/dx
    def tang(xpix):
        return y0 + slope * (xpix - x0)
    tx1, tx2 = ox + axw * 0.18, ox + axw * 0.86
    p.append(line(tx1, tang(tx1), tx2, tang(tx2), color=POS, sw=2.0, dash="6 4"))
    p.append(text(tx2 - 6, tang(tx2) - 8, "дотична: нахил = ∂f/∂x", size=11, color=POS, anchor="end", bold=True))

    # смуга розкиду входу σ_x навколо x0
    sx = axw * 0.10
    p.append(line(x0 - sx, oy, x0 - sx, oy + 8, color=NEG, sw=1.4))
    p.append(line(x0 + sx, oy, x0 + sx, oy + 8, color=NEG, sw=1.4))
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.16"/>'
             % (x0 - sx, oy - axh, 2 * sx, axh, NEG))
    p.append(text(x0, oy + 24, "σ(x)", size=11, color=NEG, anchor="middle", bold=True))

    # відбита смуга виходу σ_d на осі f (через дотичну)
    dy = abs(slope) * sx
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.16"/>'
             % (ox, y0 - dy, axw, 2 * dy, POS))
    p.append(line(ox - 8, y0 - dy, ox, y0 - dy, color=POS, sw=1.4))
    p.append(line(ox - 8, y0 + dy, ox, y0 + dy, color=POS, sw=1.4))
    p.append(text(ox - 14, y0 + 4, "σ(d)", size=11, color=POS, anchor="end", bold=True))

    # проєкційні пунктири від точки до осей
    p.append(line(x0, y0, x0, oy, color=MUTED, sw=0.9, dash="3 3"))
    p.append(line(x0, y0, ox, y0, color=MUTED, sw=0.9, dash="3 3"))

    p.append(text(W / 2, 410, "σ(d) ≈ |∂f/∂x| · σ(x) — крутіший нахил переносить ту саму похибку як більшу",
                  size=11.5, color=INK, bold=True))

    render(os.path.join(OUT, "linearization.svg"), W, H, *p,
           title="Звідки беруться коефіцієнти чутливості")


# ── sensitivity: однакове Δ у v і в t дає різний Δd ──────────────────────────
# Ідея: у d = v·t/2 коефіцієнт біля v є t/2, біля t є v/2; той самий відносний
# зсув входу важить рівно стільки, скільки його коефіцієнт.

def fig_sensitivity():
    W, H = 720, 300
    p = []
    p.append(text(W / 2, 50, "d = v·t/2: кожен вхід тисне на вихід із власною «вагою» — своїм коефіцієнтом",
                  size=12.5, color=MUTED))

    boxes = [
        (150, "∂d/∂v = t/2", "зсунь швидкість на Δv\n→ відстань зсунеться на (t/2)·Δv", NEG),
        (570, "∂d/∂t = v/2", "зсунь час на Δt\n→ відстань зсунеться на (v/2)·Δt", POS),
    ]
    cy = 150
    for cx, head, body, col in boxes:
        frag, w, hgt = textbox(cx, cy, body, size=11.5, pad=14, fill=BG, stroke=col, sw=1.6, color=INK)
        p.append(frag)
        p.append(text(cx, cy - hgt / 2 - 12, head, size=13.5, color=col, bold=True))

    # середина: формула масштабу
    p.append(text(W / 2, 244, "σ(d)² = (t/2)²·σ(v)² + (v/2)²·σ(t)²   — внесок кожного = (його коефіцієнт)²·(його σ)²",
                  size=11.5, color=INK, bold=True, anchor="middle"))
    p.append(text(W / 2, 270, "ось чому 3 % розкиду у швидкості коштують 3 % відстані, а наносекунда таймера — майже нічого",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "sensitivity.svg"), W, H, *p,
           title="Коефіцієнт чутливості: хто скільки важить")


# ── correlation: квадратура тримається лише на незалежності ───────────────────
# Ідея: незалежні внески — перпендикулярні вектори (Піфагор, гіпотенуза);
# повністю корельовані — колінеарні (просто додаються); від'ємна кореляція гасить.

def fig_correlation():
    W, H = 760, 340
    p = []
    p.append(text(W / 2, 50, "Квадратура — це Піфагор; вона діє, лише поки внески перпендикулярні (незалежні)",
                  size=12.5, color=MUTED))

    import math as _m
    a, b = 70.0, 50.0           # довжини векторів (px)
    base = 250

    panels = [
        (150, "незалежні (r=0)", _m.sqrt(a * a + b * b), "квадратура: √(a²+b²)", FIELD),
        (390, "однаковий бік (r=+1)", a + b, "просто сума: a+b", POS),
        (630, "протилежні (r=−1)", abs(a - b), "гасяться: |a−b|", NEG),
    ]
    for cx, label, res, note, col in panels:
        p.append(text(cx, 96, label, size=12.5, color=col, bold=True))
        ax = cx - 55
        if "r=0" in label:
            # перпендикулярні катети + гіпотенуза
            p.append(line(ax, base, ax + a, base, color=NEG, sw=2.4))
            p.append(line(ax + a, base, ax + a, base - b, color=NEG, sw=2.4))
            p.append(line(ax, base, ax + a, base - b, color=col, sw=3.0))
            p.append(rect(ax + a - 8, base - 8, 8, 8, fill="none", stroke=MUTED, sw=1.0, rx=0))
        elif "r=+1" in label:
            # колінеарні, в один бік
            p.append(line(ax, base, ax + a, base, color=NEG, sw=2.4))
            p.append(line(ax + a, base, ax + a + b, base, color="#7a93e8", sw=2.4))
            p.append(line(ax, base + 16, ax + a + b, base + 16, color=col, sw=3.0))
        else:
            # протилежні
            p.append(line(ax, base, ax + a, base, color=NEG, sw=2.4))
            p.append(line(ax + a, base, ax + a - b, base, color="#7a93e8", sw=2.4))
            p.append(line(ax, base + 16, ax + (a - b), base + 16, color=col, sw=3.0))
        p.append(text(cx, base + 50, note, size=11, color=col, anchor="middle", bold=True))

    p.append(text(W / 2, 318, "у бюджеті далекоміра внески незалежні → лівий випадок; спільна причина зсунула б до середнього чи правого",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "correlation.svg"), W, H, *p,
           title="Чому квадратура потребує незалежності")


# ── gum-timeline: дві дороги до «плюс-мінуса» (для вставки hist-gum-uncertainty) ─
# Ідея: поняття невизначеності визрівало в метрології (верхня смуга), а готову
# процедуру «бюджет похибок» дала аерокосмічна інженерія (нижня смуга); у
# сучасному далекомірі обидві дороги сходяться.

def fig_gum_timeline():
    W, H = 960, 460
    p = []
    p.append(text(W / 2, 52, "Поняття — з метрології; процедуру — з аерокосмічної інженерії",
                  size=13, color=MUTED))

    # дві горизонтальні смуги-осі
    xL, xR = 70, 660
    yTop, yBot = 160, 330
    p.append(line(xL, yTop, xR, yTop, color=NEG, sw=2.0))
    p.append(line(xL, yBot, xR, yBot, color=FIELD, sw=2.0))
    p.append(text(xL, yTop - 52, "Метрологія: поняття невизначеності", size=12.5, color=NEG, anchor="start", bold=True))
    p.append(text(xL, yBot + 58, "Інженерія: бюджет похибок (RSS)", size=12.5, color=FIELD, anchor="start", bold=True))

    bw, bh = 96, 40
    # верхня смуга — метрологічні віхи (рівномірно вздовж осі)
    top = [
        (xL + 30,  "NBS\n1963"),
        (xL + 175, "CIPM\n1977"),
        (xL + 320, "INC-1\n1980"),
        (xL + 460, "GUM\n1993"),
        (xL + 590, "JCGM\n1997"),
    ]
    for cx, label in top:
        p.append(circle(cx, yTop, 4.5, fill=NEG, stroke=BG, sw=1.4))
        p.append(fitbox(cx - bw / 2, yTop - bh - 18, bw, bh, label, size=11,
                        fill="#eaf0fd", stroke=NEG, sw=1.3, color=INK, bold=True))

    # JCGM 100:2008 — «чинна редакція», окремий ярлик ПІД смугою біля кінця
    p.append(circle(xR, yTop, 4.5, fill=NEG, stroke=BG, sw=1.4))
    p.append(fitbox(xR - 150, yTop + 18, 160, bh, "чинна редакція:\nJCGM 100:2008",
                    size=10.5, fill="#eaf0fd", stroke=NEG, sw=1.3, color=INK))

    # нижня смуга — інженерна віха (одна, бо «error budget» — поступово усталений вислів)
    xEng = xL + 150
    p.append(circle(xEng, yBot, 4.5, fill=FIELD, stroke=BG, sw=1.4))
    p.append(fitbox(xEng - 140, yBot + 18, 280, bh,
                    "інерціальна навігація (MIT/Draper), 1950–60-ті",
                    size=10.5, fill="#eafaf0", stroke=FIELD, sw=1.3, color=INK))
    p.append(text(xEng + 170, yBot - 14, "кошторис джерел, складання в квадратурі",
                  size=10.5, color=FIELD, anchor="start"))

    # вузол-сходження справа
    nx, ny = 850, (yTop + yBot) / 2
    frag, w, hh = textbox(nx, ny, "сучасний\nдалекомір\n{d, σ, bias}", size=11.5,
                          pad=14, fill="#f1f2f4", stroke=INK, sw=1.8, color=INK, bold=True)
    # стрілки обох смуг у вузол
    p.append(arrow(xR + 8, yTop, nx - w / 2 - 6, ny - 16, color=NEG, sw=1.8))
    p.append(arrow(xR + 8, yBot, nx - w / 2 - 6, ny + 16, color=FIELD, sw=1.8))
    p.append(frag)

    p.append(text(W / 2, 438,
                  "Дві традиції сходяться: невизначеність-коридор (поняття) + error budget (процедура)",
                  size=11.5, color=INK, bold=True))

    render(os.path.join(OUT, "gum-timeline.svg"), W, H, *p,
           title="Дві дороги до одного «плюс-мінуса»")


if __name__ == "__main__":
    fig_systematic_vs_random()
    fig_budget_rows()
    fig_rss_vs_sum()
    fig_dominant_term()
    fig_linearization()
    fig_sensitivity()
    fig_correlation()
    fig_gum_timeline()
    print("ok: figs generated")
