# -*- coding: utf-8 -*-
"""Фігури до статті «Межа Шоклі–Квайссера».
Запуск із теки теми:  python figs.py   →  ./img/*.svg

Модель — детальний баланс (Шоклі–Квайссер): Сонце як чорне тіло Ts,
елемент за Tc=300 K неминуче світиться сам (випромінна рекомбінація).
Усі криві й числа порахувано тут, а не намальовано на око."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ── фізичні сталі (SI) ───────────────────────────────────────────────────────
h  = 6.62607015e-34    # Дж·с
c  = 2.99792458e8      # м/с
kB = 1.380649e-23      # Дж/К
q  = 1.602176634e-19   # Кл
sigma = 5.670374419e-8 # Вт/(м²·К⁴)

Ts = 5800.0            # температура фотосфери Сонця, К (S–Q брали 6000)
Tc = 300.0             # температура елемента, К
theta = math.radians(0.2665)               # кутовий радіус Сонця із Землі
OMEGA = 2*math.pi*(1-math.cos(theta))      # тілесний кут диска Сонця, ср (~6.8e-5)

# спектральна густина потоку фотонів чорного тіла, фотони/(м²·с·ср·еВ)
def nph(E_eV, T):
    E = E_eV*q
    x = E/(kB*T)
    if x > 700 or x <= 0:
        return 0.0
    return (2.0/(h**3*c**2))*E*E/(math.exp(x)-1.0)*q   # ×q: dE_Дж = q·dE_еВ

# сітка енергій для інтегрування
EGRID = [0.05 + 0.002*i for i in range(int((4.5-0.05)/0.002)+1)]
DE = 0.002

def integ(f, lo, hi):
    s = 0.0
    for E in EGRID:
        if E < lo or E > hi:
            continue
        s += f(E)*DE
    return s

# інтеграли Сонця (кешуємо профіль Ts)
NS = [nph(E, Ts) for E in EGRID]          # фотонна густина Сонця
PS = [E*q*NS[i] for i, E in enumerate(EGRID)]  # енергетична густина, Вт/(м²·ср·еВ)/q… (E у Дж)

Pin = OMEGA*sum(PS[i]*DE for i in range(len(EGRID)))  # падна потужність, Вт/м² (~1.36 кВт/м²)

def photons_above(Eg, T):   # фотони/(м²·с·ср) з E ≥ Eg
    return sum(nph(E, T)*DE for E in EGRID if E >= Eg)

def model(Eg):
    """Повертає словник детально-балансових величин для порога Eg (еВ)."""
    Ng = OMEGA*photons_above(Eg, Ts)       # генерація: фотони Сонця над порогом
    N0 = math.pi*photons_above(Eg, Tc)     # емісія елемента у півсферу (Ламберт)
    Jsc = q*Ng
    J0  = q*N0
    Voc = (kB*Tc/q)*math.log(Jsc/J0 + 1.0)
    # максимум потужності: пробіг по напрузі
    Pmax, Vmp, Jmp = 0.0, 0.0, 0.0
    N = 600
    for i in range(1, N):
        V = Voc*i/N
        J = Jsc - J0*(math.exp(q*V/(kB*Tc)) - 1.0)
        if J < 0:
            break
        P = J*V
        if P > Pmax:
            Pmax, Vmp, Jmp = P, V, J
    eta = Pmax/Pin
    # енергетичний розклад втрат (частки падної потужності)
    E_below = OMEGA*sum(E*q*NS[i]*DE for i, E in enumerate(EGRID) if E < Eg)
    E_therm = OMEGA*sum((E-Eg)*q*NS[i]*DE for i, E in enumerate(EGRID) if E >= Eg)
    u = (Eg*q*Ng)/Pin                       # «гранична»: рівно Eg з фотона
    v = Voc/Eg                              # частка порога, що дійшла в напругу
    FF = Pmax/(Jsc*Voc) if Jsc*Voc > 0 else 0.0
    return dict(Eg=Eg, Jsc=Jsc, J0=J0, Voc=Voc, Pmax=Pmax, eta=eta,
                below=E_below/Pin, therm=E_therm/Pin, u=u, v=v, m=FF)

# крива η(Eg) і пік
EGS = [0.4 + 0.02*i for i in range(int((3.0-0.4)/0.02)+1)]
CURVE = [(Eg, model(Eg)['eta']) for Eg in EGS]
PK = max(CURVE, key=lambda t: t[1])
PKEg, PKeta = PK
M_opt = model(PKEg)
M_si  = model(1.12)
M_ga  = model(1.42)

# ── локальні помічники малювання ─────────────────────────────────────────────
BLUE = "#2457d6"; RED = "#c0392b"; GRN = "#27ae60"; ORG = "#d98c00"; PUR = "#7b3fa0"

def polyline(pts, color, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (p, color, sw, d)

def polygon(pts, fill, opacity=0.5):
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return '<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="none"/>' % (p, fill, opacity)


# ── Фігура 1: сонячний спектр і два спектральні марнотратства ─────────────────
def fig_spectrum():
    W, H = 780, 500
    x0, x1, y0, y1 = 92, 700, 92, 388
    Emin, Emax = 0.4, 4.0
    Eg = 1.34
    ys = [nph(E, Ts) for E in EGRID if Emin <= E <= Emax]
    ymax = max(ys)*1.08

    def X(E): return x0 + (E-Emin)/(Emax-Emin)*(x1-x0)
    def Y(n): return y1 - n/ymax*(y1-y0)

    prof = [(E, nph(E, Ts)) for E in EGRID if Emin <= E <= Emax]
    s = []
    # осьові позначки (без вертикальної сітки, щоб не перетинати підписи зон)
    for E in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]:
        s.append(line(X(E), y1, X(E), y1+5, color=INK, sw=1.2))
        s.append(text(X(E), y1+22, "%.1f" % E, size=12, color=MUTED))
    s.append(text((x0+x1)/2, y1+46, "енергія фотона, еВ", size=13, color=INK))
    s.append(text(x0-58, (y0+y1)/2, "потік фотонів", size=13, color=INK, anchor="middle"))
    s.append(line(x0, y1, x1, y1, color=INK, sw=1.6))
    s.append(line(x0, y0, x0, y1, color=INK, sw=1.6))

    # заливки: нижче порога (прозоре) і надлишок над порогом (тепло)
    below = [(X(Emin), y1)] + [(X(E), Y(n)) for E, n in prof if E <= Eg] + [(X(Eg), y1)]
    s.append(polygon(below, BLUE, 0.22))
    # «корисна» частка над порогом (Eg з кожного фотона) — до рівня, що відповідає Eg? спрощено — весь пік над порогом:
    above = [(X(Eg), y1)] + [(X(E), Y(n)) for E, n in prof if E >= Eg] + [(X(Emax), y1)]
    s.append(polygon(above, RED, 0.14))
    # крива спектра
    s.append(polyline([(X(E), Y(n)) for E, n in prof], INK, sw=2.8))
    # поріг
    s.append(line(X(Eg), y0-4, X(Eg), y1, color=GRN, sw=2.2, dash="6 4"))
    s.append(text(X(Eg), y0-12, "поріг Eg = 1.34 еВ", size=13, color=GRN, bold=True))

    # підписи зон: синій — низько-ліворуч (лівіше порога, під кривою);
    # червоний — праворуч, де крива вже низько
    fb = fitbox(100, 300, 140, 52,
                "E < Eg:\nелемент прозорий,\nфотон утрачено",
                size=12, fill="#eaf0fd", stroke=BLUE, color="#1a2b6b")
    s.append(fb)
    fb2 = fitbox(X(2.32), y0+22, 182, 52,
                 "E > Eg: пара є, але\nнадлишок E−Eg\nвідразу йде теплом",
                 size=12, fill="#fdece9", stroke=RED, color="#7a231a")
    s.append(fb2)

    render(os.path.join(OUT, 'spectrum-gap.svg'), W, H, *s,
           title="Один поріг проти цілого спектра: дві неминучі спектральні втрати")


# ── Фігура 2: чому є оптимум — струм падає, напруга росте ─────────────────────
def fig_tradeoff():
    W, H = 850, 500
    x0, x1, y0, y1 = 96, 620, 92, 384
    Emin, Emax = 0.5, 2.6

    egs = [Emin + 0.02*i for i in range(int((Emax-Emin)/0.02)+1)]
    ms = [model(E) for E in egs]
    jmax = max(m['Jsc'] for m in ms)
    etamax = max(m['eta'] for m in ms)

    def X(E): return x0 + (E-Emin)/(Emax-Emin)*(x1-x0)
    def Yj(j): return y1 - j/jmax*(y1-y0)           # нормований струм / напруга
    def Ye(e): return y1 - e/(etamax*1.12)*(y1-y0)  # ККД

    s = []
    for E in [0.5, 1.0, 1.5, 2.0, 2.5]:
        s.append(line(X(E), y0, X(E), y1, color="#eef0f3", sw=1))
        s.append(text(X(E), y1+22, "%.1f" % E, size=12, color=MUTED))
    s.append(text((x0+x1)/2, y1+46, "заборонена зона Eg, еВ", size=13, color=INK))
    s.append(line(x0, y1, x1, y1, color=INK, sw=1.6))
    s.append(line(x0, y0, x0, y1, color=INK, sw=1.6))

    # струм (фотони над порогом) — падає
    s.append(polyline([(X(m['Eg']), Yj(m['Jsc'])) for m in ms], RED, sw=2.8))
    # напруга Voc — росте
    vmax = max(m['Voc'] for m in ms)
    s.append(polyline([(X(m['Eg']), y1-(m['Voc']/vmax)*(y1-y0)) for m in ms], BLUE, sw=2.8))
    # ККД (добуток) — має горб
    s.append(polyline([(X(m['Eg']), Ye(m['eta'])) for m in ms], GRN, sw=3.2))

    # вершина ККД
    s.append(line(X(PKEg), y0, X(PKEg), y1, color=GRN, sw=1.3, dash="5 4"))
    s.append(circle(X(PKEg), Ye(PKeta), 5, fill=GRN, stroke=GRN, sw=1))

    # легенда праворуч у вільному полі
    lx, ly = 638, 130
    items = [(RED, "струм Jsc (лічить фотони) ↓"),
             (BLUE, "напруга Voc ↑"),
             (GRN, "ККД = струм × напруга")]
    for i, (col, lab) in enumerate(items):
        yy = ly + i*30
        s.append(line(lx, yy, lx+26, yy, color=col, sw=3.2))
        wrapped = lab
        s.append(text(lx+34, yy+4, wrapped, size=12, color=INK, anchor="start"))
    s.append(text(lx, ly+108, "струм любить", size=12, color=RED, anchor="start"))
    s.append(text(lx, ly+126, "низький поріг;", size=12, color=RED, anchor="start"))
    s.append(text(lx, ly+150, "напруга —", size=12, color=BLUE, anchor="start"))
    s.append(text(lx, ly+168, "високий.", size=12, color=BLUE, anchor="start"))
    s.append(text(lx, ly+192, "пік — між ними", size=12, color=GRN, bold=True, anchor="start"))

    render(os.path.join(OUT, 'tradeoff.svg'), W, H, *s,
           title="Чому пік посередині: струм тягне вниз, напруга — вгору")


# ── Фігура 3: крива межі η(Eg) з матеріалами ─────────────────────────────────
def fig_eta_curve():
    W, H = 780, 500
    x0, x1, y0, y1 = 96, 700, 88, 384
    Emin, Emax = 0.4, 3.0
    emax = 0.40

    def X(E): return x0 + (E-Emin)/(Emax-Emin)*(x1-x0)
    def Y(e): return y1 - e/emax*(y1-y0)

    s = []
    # горизонтальна сітка обривається перед куточком із приміткою (x=452)
    for e in [0.0, 0.10, 0.20, 0.30, 0.40]:
        s.append(line(x0, Y(e), 452, Y(e), color="#eef0f3", sw=1))
        s.append(text(x0-10, Y(e)+4, "%d%%" % int(e*100), size=12, color=MUTED, anchor="end"))
    for E in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        s.append(line(X(E), y1, X(E), y1+5, color=INK, sw=1.2))
        s.append(text(X(E), y1+22, "%.1f" % E, size=12, color=MUTED))
    s.append(text((x0+x1)/2, y1+46, "заборонена зона матеріалу Eg, еВ", size=13, color=INK))
    s.append(text(x0-56, (y0+y1)/2, "межа ККД", size=13, color=INK, anchor="middle"))
    s.append(line(x0, y1, x1, y1, color=INK, sw=1.6))
    s.append(line(x0, y0, x0, y1, color=INK, sw=1.6))

    # крива межі
    s.append(polyline([(X(Eg), Y(eta)) for Eg, eta in CURVE], INK, sw=3.2))

    # вершина (наша чорнотільна модель)
    s.append(circle(X(PKEg), Y(PKeta), 5.5, fill=GRN, stroke=GRN, sw=1))
    s.append(line(X(PKEg), Y(PKeta), X(PKEg), y1, color=GRN, sw=1.2, dash="5 4"))

    # матеріали
    for m, col, lab, dx in [(M_si, BLUE, "Si  1.12 еВ", -6), (M_ga, PUR, "GaAs 1.42 еВ", 8)]:
        s.append(circle(X(m['Eg']), Y(m['eta']), 5, fill=col, stroke=col, sw=1))
        an = "end" if dx < 0 else "start"
        s.append(text(X(m['Eg'])+dx, Y(m['eta'])-12, lab, size=12, color=col, bold=True, anchor=an))

    # напис про вершину — у вільному верхньому куті праворуч
    fb = fitbox(x1-236, y0+6, 228, 74,
                "вершина ~%.0f%% (Сонце — чорне\nтіло %d K). З реальним спектром\nAM1.5 межа сягає 33.7%% при\n1.34 еВ" % (PKeta*100, int(Ts)),
                size=12, fill=FILL, stroke=MUTED, color=INK)
    s.append(fb)

    render(os.path.join(OUT, 'eta-vs-eg.svg'), W, H, *s,
           title="Межа одного переходу як функція забороненої зони")


# ── Фігура 4: водоспад втрат — куди дівається сонце ──────────────────────────
def fig_waterfall():
    W, H = 780, 470
    m = model(1.34)   # розклад коло оптимуму
    below = m['below']; therm = m['therm']; u = m['u']
    volt = u*(1-m['v']); fill_l = u*m['v']*(1-m['m']); out = u*m['v']*m['m']

    segs = [("нижче порога\n(прозоре)", below, BLUE),
            ("надлишок → тепло\n(термалізація)", therm, RED),
            ("напруга < Eg\n(вимушене світіння)", volt, ORG),
            ("форма ВАХ\n(fill factor)", fill_l, "#9aa0a6"),
            ("у струм", out, GRN)]

    x0, x1, ytop, ybot = 70, 560, 96, 392
    def Y(frac): return ybot - frac*(ybot-ytop)   # 1.0 → ytop
    s = []
    # вісь
    for f in [0.0, 0.25, 0.5, 0.75, 1.0]:
        s.append(line(x0-6, Y(f), x1, Y(f), color="#eef0f3", sw=1))
        s.append(text(x0-12, Y(f)+4, "%d%%" % int(f*100), size=12, color=MUTED, anchor="end"))

    # ступінчастий водоспад
    barw = 78
    xs = x0 + 8
    running = 1.0
    for lab, frac, col in segs:
        top = running
        bot = running - frac if col != GRN else 0.0
        if col == GRN:
            bot = 0.0
        yt, yb = Y(top), Y(bot)
        s.append(rect(xs, yt, barw, yb-yt, fill=col, stroke=INK, sw=1.4, rx=3))
        # відсоток усередині або над стовпчиком
        pct = "%.0f%%" % (frac*100)
        s.append(text(xs+barw/2, (yt+yb)/2+5, pct, size=14, color="#ffffff", bold=True))
        # підпис під віссю
        for j, ln in enumerate(lab.split("\n")):
            s.append(text(xs+barw/2, ybot+20+j*15, ln, size=11, color=INK))
        # з'єднувальна пунктирна лінія до наступного рівня
        if col != GRN:
            s.append(line(xs+barw, yb, xs+barw+ (78-barw) +8, yb, color=MUTED, sw=1.2, dash="4 3"))
            running = bot
        xs += barw + 8

    s.append(text((x0+x1)/2, 74, "100%% сонця = %d%% нижче порога + %d%% тепла + %d%% напруги + %d%% форми + %d%% струму"
                  % (round(below*100), round(therm*100), round(volt*100), round(fill_l*100), round(out*100)),
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'loss-waterfall.svg'), W, H, *s,
           title="Куди дівається сонце: п'ять сходинок до ~третини")


# ── Фігура 5 (hist): віхи народження статті 1961 року ────────────────────────
def fig_timeline():
    """Часова стрічка-намисто до історичної вставки: як у згасаючій
    лабораторії Шоклі народилася стаття про межу. Події рівновіддалені
    (не за роками), рік — підпис на намистині; рамки чергуються вгору/вниз."""
    W, H = 900, 400
    axis_y = 200
    x0, x1 = 108, 792
    # (рік-мітка, текст, бік, колір намистини)
    beads = [
        ("1947",    "точковий\nтранзистор\n(Bell Labs)",        "up",   INK),
        ("1956",    "Нобель +\nлабораторія\nШоклі",              "down", INK),
        ("1957",    "«зрадлива\nвісімка» →\nFairchild",          "up",   RED),
        ("1959",    "Квайссер\nприходить\n(PhD 1958)",           "down", BLUE),
        ("1961",    "СТАТТЯ:\nмежа S–Q\nJ.Appl.Phys.\n32, 510",  "up",   GRN),
        ("1970-ті", "канон:\nсонячний\nбум",                     "down", ORG),
    ]
    n = len(beads)
    xs = [x0 + i * (x1 - x0) / (n - 1) for i in range(n)]
    box_w, box_h, gap = 134, 80, 42
    s = []
    # базова лінія часу
    s.append(line(x0 - 14, axis_y, x1 + 14, axis_y, color=INK, sw=3))
    s.append(text(x1 + 14, axis_y - 12, "час →", size=12, color=MUTED, anchor="end"))
    for (ylab, txt, side, col), bx in zip(beads, xs):
        s.append(circle(bx, axis_y, 7.5, fill=col, stroke=INK, sw=1.6))
        if side == "up":
            box_y = axis_y - gap - box_h                 # рамка над віссю
            s.append(line(bx, axis_y - 7, bx, box_y + box_h, color=MUTED, sw=1.4))
            s.append(text(bx, axis_y + 28, ylab, size=15, color=col, bold=True))
            fill = "#eafaf1" if col == GRN else FILL     # виділяємо статтю
        else:
            box_y = axis_y + gap                          # рамка під віссю
            s.append(line(bx, axis_y + 7, bx, box_y, color=MUTED, sw=1.4))
            s.append(text(bx, axis_y - 18, ylab, size=15, color=col, bold=True))
            fill = FILL
        s.append(fitbox(bx - box_w / 2, box_y, box_w, box_h, txt,
                        size=13, pad=8, fill=fill, stroke=col, color=INK))
    render(os.path.join(OUT, 'timeline.svg'), W, H, *s,
           title="Народження статті 1961 року: віхи згасаючої лабораторії")


# ── Фігура 7 (math): напруга як лог-розрив між двома чорними тілами ───────────
def fig_voltage_gap():
    """Voc = (kT/q)·ln(Jsc/J0). Малюємо ДВА потоки фотонів у лог-масштабі:
    що приносить Сонце (OMEGA·b, Ts) і що випромінює елемент (π·b, 300 K).
    Вертикальний розрив над порогом = ln(Jsc/J0) = q·Voc/kT."""
    W, H = 820, 520
    x0, x1, y0, y1 = 104, 632, 104, 404
    Emin, Emax = 0.4, 3.0
    Eg = 1.26
    xs = [E for E in EGRID if Emin <= E <= Emax]
    gen = [OMEGA*nph(E, Ts) for E in xs]         # потік від Сонця (розведений)
    emi = [math.pi*nph(E, Tc) for E in xs]       # власна емісія елемента, 300 K
    lg = [math.log10(v) if v > 0 else None for v in gen]
    le = [math.log10(v) if v > 0 else None for v in emi]
    ymax = math.ceil(max(v for v in lg if v is not None)) + 1
    ymin = ymax - 24                              # 24 декади заввишки

    def X(E): return x0 + (E-Emin)/(Emax-Emin)*(x1-x0)
    def Y(L):
        L = max(ymin, min(ymax, L))
        return y1 - (L-ymin)/(ymax-ymin)*(y1-y0)

    s = []
    # декадна сітка (кожні 4 порядки)
    L = ymin
    while L <= ymax:
        s.append(line(x0, Y(L), x1, Y(L), color="#eef0f3", sw=1))
        s.append(text(x0-10, Y(L)+4, "10", size=11, color=MUTED, anchor="end"))
        s.append(text(x0-10+2, Y(L)-4, "%d" % int(L), size=8, color=MUTED, anchor="start"))
        L += 4
    for E in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        s.append(line(X(E), y1, X(E), y1+5, color=INK, sw=1.2))
        s.append(text(X(E), y1+22, "%.1f" % E, size=12, color=MUTED))
    s.append(text((x0+x1)/2, y1+46, "енергія фотона E, еВ", size=13, color=INK))
    s.append(text(x0-72, (y0+y1)/2, "потік фотонів на еВ", size=13, color=INK, anchor="middle"))
    s.append(line(x0, y1, x1, y1, color=INK, sw=1.6))
    s.append(line(x0, y0, x0, y1, color=INK, sw=1.6))

    # криві (обриваємо там, де значення падає під дно осі)
    def seg(vals):
        pts, run = [], []
        for E, L in zip(xs, vals):
            if L is None or L < ymin:
                if run: pts.append(run); run = []
                continue
            run.append((X(E), Y(L)))
        if run: pts.append(run)
        return pts
    for p in seg(lg): s.append(polyline(p, ORG, sw=3.0))
    for p in seg(le): s.append(polyline(p, BLUE, sw=3.0))

    # поріг і розрив над ним
    s.append(line(X(Eg), y0-2, X(Eg), y1, color=GRN, sw=2.0, dash="6 4"))
    Lg = math.log10(OMEGA*nph(Eg, Ts)); Le = math.log10(math.pi*nph(Eg, Tc))
    yA, yB = Y(Lg), Y(Le)
    s.append(line(X(Eg), yA, X(Eg), yB, color=INK, sw=2.2))
    s.append(line(X(Eg)-5, yA, X(Eg)+5, yA, color=INK, sw=2.2))
    s.append(line(X(Eg)-5, yB, X(Eg)+5, yB, color=INK, sw=2.2))
    # число розриву
    m = model(Eg)
    dec = math.log10(m['Jsc']/m['J0'])
    fb = fitbox(X(Eg)+16, (yA+yB)/2-30, 210, 62,
                "розрив ≈ ln(Jsc/J0)\n= q·Voc/kT ≈ %.0f\n(%.1f порядку × ln10)" % (m['Voc']*q/(kB*Tc), dec),
                size=12, fill="#eafaf0", stroke=GRN, color="#14532d")
    s.append(fb)
    s.append(text(X(Eg), y0-8, "поріг Eg = %.2f еВ" % Eg, size=12, color=GRN, bold=True))

    # підписи кривих
    s.append(text(X(0.62), Y(lg[[i for i,E in enumerate(xs) if E>=0.62][0]])+20,
                  "Сонце: Ω·b(E, 5800 K)", size=12, color=ORG, bold=True, anchor="start"))
    s.append(text(X(0.44), Y(le[2])+2, "елемент: π·b(E, 300 K)", size=12, color=BLUE, bold=True, anchor="start"))

    # легенда-висновок у вільному правому полі (праворуч від осі x1)
    s.append(fitbox(x1+10, y0+6, 172, 88,
                    "струм наперед заданий\n(площа під Сонцем);\nнапруга — це РОЗРИВ\nміж двома тілами",
                    size=12, fill=FILL, stroke=MUTED, color=INK))
    render(os.path.join(OUT, 'voltage-loggap.svg'), W, H, *s,
           title="Напруга розімкнутого кола — це логарифмічний розрив двох чорних тіл")


# ── Фігура 8 (math): ВАХ і прямокутник максимальної потужності (fill factor) ──
def fig_jv_mpp():
    """P = J·V максимальна не на краю, а в коліні. m = площа(MPP)/площа(Jsc·Voc)."""
    W, H = 780, 500
    Eg = 1.26
    m = model(Eg)
    Jsc, J0, Voc = m['Jsc'], m['J0'], m['Voc']
    # MPP тонким пробігом
    Pmax, Vmp, Jmp = 0.0, 0.0, 0.0
    N = 4000
    for i in range(1, N):
        V = Voc*i/N
        J = Jsc - J0*(math.exp(q*V/(kB*Tc)) - 1.0)
        if J < 0: break
        P = J*V
        if P > Pmax: Pmax, Vmp, Jmp = P, V, J

    x0, x1, y0, y1 = 96, 560, 92, 400
    Vmax, Jmax = Voc*1.06, Jsc*1.10
    def X(V): return x0 + V/Vmax*(x1-x0)
    def Y(J): return y1 - J/Jmax*(y1-y0)
    # струм у мА/см² (÷10): 469 А/м² = 46.9 мА/см²
    def mAcm2(J): return J/10.0

    s = []
    for J in [0, 100, 200, 300, 400]:
        s.append(line(x0, Y(J), x1, Y(J), color="#eef0f3", sw=1))
        s.append(text(x0-10, Y(J)+4, "%.0f" % mAcm2(J), size=11, color=MUTED, anchor="end"))
    for V in [0, 0.25, 0.5, 0.75, 1.0]:
        s.append(line(X(V), y1, X(V), y1+5, color=INK, sw=1.2))
        s.append(text(X(V), y1+22, "%.2f" % V, size=11, color=MUTED))
    s.append(text((x0+x1)/2, y1+46, "напруга V, В", size=13, color=INK))
    s.append(text(x0-64, (y0+y1)/2, "струм J, мА/см²", size=13, color=INK, anchor="middle"))

    # зовнішній прямокутник Jsc×Voc (стеля потужності)
    s.append(rect(x0, Y(Jsc), X(Voc)-x0, y1-Y(Jsc), fill="none", stroke=MUTED, sw=1.6, rx=0))
    s[-1] = s[-1].replace('/>', ' stroke-dasharray="6 4"/>')
    # прямокутник MPP
    s.append(rect(x0, Y(Jmp), X(Vmp)-x0, y1-Y(Jmp), fill=GRN, stroke=GRN, sw=1.4, rx=0))
    s[-1] = s[-1].replace('fill="%s"' % GRN, 'fill="%s" fill-opacity="0.18"' % GRN)

    s.append(line(x0, y1, x1, y1, color=INK, sw=1.6))
    s.append(line(x0, y0, x0, y1, color=INK, sw=1.6))

    # крива ВАХ
    pts = []
    for i in range(0, 561):
        V = Vmax*i/560
        J = Jsc - J0*(math.exp(q*V/(kB*Tc)) - 1.0)
        if J < 0: break
        pts.append((X(V), Y(J)))
    s.append(polyline(pts, RED, sw=3.2))

    # ключові точки
    s.append(circle(x0, Y(Jsc), 4.5, fill=RED, stroke=RED, sw=1))
    s.append(text(x0+8, Y(Jsc)-8, "Jsc = %.1f мА/см²" % mAcm2(Jsc), size=12, color=RED, bold=True, anchor="start"))
    s.append(circle(X(Voc), y1, 4.5, fill=BLUE, stroke=BLUE, sw=1))
    s.append(text(X(Voc)+2, y1-10, "Voc = %.2f В" % Voc, size=12, color=BLUE, bold=True, anchor="end"))
    s.append(circle(X(Vmp), Y(Jmp), 5.5, fill=GRN, stroke="#0d3b21", sw=1.4))
    s.append(text(X(Vmp)+10, Y(Jmp)+4, "MPP (Vmp=%.2f, Jmp=%.1f)" % (Vmp, mAcm2(Jmp)),
                  size=12, color="#0d3b21", bold=True, anchor="start"))

    # напис про fill factor
    fb = fitbox(x0+14, y0+6, 214, 62,
                "m = площа MPP / (Jsc·Voc)\n= %.3f\n(коефіцієнт заповнення)" % (Pmax/(Jsc*Voc)),
                size=12, fill="#eafaf0", stroke=GRN, color="#14532d")
    s.append(fb)

    render(os.path.join(OUT, 'jv-mpp.svg'), W, H, *s,
           title="P = J·V: максимум сидить у коліні, а не на краю")


if __name__ == "__main__":
    fig_spectrum()
    fig_tradeoff()
    fig_eta_curve()
    fig_waterfall()
    fig_voltage_gap()
    fig_jv_mpp()
    fig_timeline()
    print("Pin = %.1f W/m^2" % Pin)
    print("PEAK: Eg=%.3f eV  eta=%.3f" % (PKEg, PKeta))
    mo = model(PKEg)
    print("  at peak: Voc=%.3f V  u=%.3f v=%.3f m=%.3f  below=%.3f therm=%.3f"
          % (mo['Voc'], mo['u'], mo['v'], mo['m'], mo['below'], mo['therm']))
    print("Si 1.12: eta=%.3f Voc=%.3f" % (M_si['eta'], M_si['Voc']))
    print("GaAs 1.42: eta=%.3f Voc=%.3f" % (M_ga['eta'], M_ga['Voc']))
    m134 = model(1.34)
    print("At 1.34: eta=%.3f below=%.3f therm=%.3f u=%.3f v=%.3f m=%.3f"
          % (m134['eta'], m134['below'], m134['therm'], m134['u'], m134['v'], m134['m']))
    print("OK ->", OUT)
