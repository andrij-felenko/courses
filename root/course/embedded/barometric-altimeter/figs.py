# -*- coding: utf-8 -*-
"""Фігури теми «Барометр-альтиметр». Запуск: python figs.py  → ./img/*.svg"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фіг.1 — крива «тиск vs висота»: експонента + локальний лінійний нахил ─────
def fig_pressure_altitude():
    W, H = 720, 460
    # поле графіка
    x0, y0 = 110, 70          # лівий-верх осей
    gw, gh = 420, 320         # ширина/висота поля
    xb, yb = x0, y0 + gh      # початок координат (ліво-низ)

    p0 = 1013.0               # гПа на рівні моря
    hmax = 12000.0            # м (до ~тропопаузи)
    # барометрична залежність ISA: p = p0*(1 - L*h/T0)^5.255
    L, T0, expo = 0.0065, 288.15, 5.255
    def p_of_h(h): return p0 * (1 - L * h / T0) ** expo

    def X(p):  return xb + (p0 - p) / p0 * gw          # тиск ліворуч-високий
    def Y(h):  return yb - h / hmax * gh

    frs = []
    # осі
    frs.append(line(xb, yb, xb + gw, yb, color=INK, sw=2))   # вісь тиску (низ)
    frs.append(line(xb, yb, xb, y0, color=INK, sw=2))        # вісь висоти (ліво)
    frs.append(text(xb + gw / 2, yb + 46, "тиск, гПа  (падає праворуч)", size=13, color=MUTED))
    frs.append(text(x0 - 70, y0 + gh / 2, "висота, км", size=13, color=MUTED,
                    anchor="middle"))
    # позначки висоти
    for hk in (0, 3, 6, 9, 12):
        yy = Y(hk * 1000)
        frs.append(line(xb - 5, yy, xb, yy, color=INK, sw=1.5))
        frs.append(text(xb - 12, yy + 4, "%d" % hk, size=12, color=INK, anchor="end"))
    # позначки тиску
    for pp in (1013, 850, 700, 500, 300, 200):
        xx = X(pp)
        frs.append(line(xx, yb, xx, yb + 5, color=INK, sw=1.5))
        frs.append(text(xx, yb + 20, "%d" % pp, size=11, color=INK))

    # справжня крива (експонента)
    pts = []
    h = 0.0
    while h <= hmax + 1:
        pts.append("%.1f,%.1f" % (X(p_of_h(h)), Y(h)))
        h += 150
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
               % (" ".join(pts), POS))

    # дотична біля землі: лінійний крок ~12 Па/м => 1 гПа ~ 8.3 м
    # від (p0, 0) проведемо пряму так, ніби нахил сталий
    h_lin = 4000.0
    p_lin = p0 - h_lin * 0.12      # 0.12 гПа/м => прибл. лінійний приріст
    frs.append(line(X(p0), Y(0), X(p_lin), Y(h_lin), color=NEG, sw=2, dash="7 5"))

    # підписи двох кривих
    box1 = fitbox(X(620), Y(2400), 200, 40,
                  "справжня крива\n(барометрична)", size=12, fill="#fdecea",
                  stroke=POS, color=POS)
    frs.append(box1)
    box2 = fitbox(xb + 6, Y(4600), 250, 40,
                  "лінійне наближення\nбіля землі: 1 гПа ≈ 8.3 м", size=12,
                  fill="#eaf0fd", stroke=NEG, color=NEG)
    frs.append(box2)

    # точка-маркер «біля землі круто»
    frs.append(circle(X(p0), Y(0), 5, fill=INK, stroke=INK))
    frs.append(text(X(p0) + 8, Y(0) + 18, "рівень моря, 1013 гПа", size=11,
                    color=INK, anchor="start"))

    # правий стовпчик-висновок
    rb = fitbox(x0 + gw + 30, y0 + 30, 150, 200,
                "Біля землі\nкрива найкрутіша:\n\n~12 Па на метр\n~1 гПа на 8.3 м\n\n"
                "вище — тиск\nпадає повільніше", size=12, fill=FILL, stroke=LINE)
    frs.append(rb)

    render(os.path.join(IMG, "pressure-altitude.svg"), W, H, *frs,
           title="Тиск падає з висотою — звідси й висотомір")


# ── Фіг.2 — MEMS-давач тиску: прогин мембрани читають як сигнал ───────────────
def fig_mems_pressure():
    W, H = 720, 380
    frs = []
    cx = 220
    # вакуумна камера-еталон з мембраною зверху
    cap_y = 150
    cap_w, cap_h = 240, 90
    cap_x = cx - cap_w / 2
    # корпус камери
    frs.append(rect(cap_x, cap_y, cap_w, cap_h, fill="#eef2f6", stroke=INK, sw=2))
    frs.append(text(cx, cap_y + cap_h / 2 + 5, "герметична камера (еталон ~0)",
                    size=12, color=MUTED))
    # мембрана (прогнута вниз) — крива Безьє
    mx0, mx1 = cap_x + 6, cap_x + cap_w - 6
    sag = 18
    frs.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
               'stroke="%s" stroke-width="4"/>'
               % (mx0, cap_y, cx, cap_y + sag, mx1, cap_y, POS))
    frs.append(text(cx, cap_y - 14, "тонка кремнієва мембрана", size=12,
                    color=POS, bold=True))
    # тензорезистори на мембрані
    for fx in (mx0 + 28, mx1 - 28):
        frs.append(rect(fx - 9, cap_y + 2, 18, 7, fill=FIELD, stroke=INK, sw=1, rx=2))
    frs.append(text(cx, cap_y + sag + 28, "вбудовані тензорезистори", size=11,
                    color=FIELD))

    # стрілки тиску згори
    for ax in (cap_x + 40, cx, cap_x + cap_w - 40):
        frs.append(arrow(ax, cap_y - 56, ax, cap_y - 6, color=NEG, sw=2))
    frs.append(text(cx, cap_y - 66, "атмосферний тиск тисне зверху", size=13,
                    color=NEG, bold=True))

    # ланцюжок перетворення праворуч
    bx = 470
    steps = ["прогин\nмембрани", "зміна опору\n(чи ємності)", "напруга",
             "ADC →\nчисло тиску"]
    by = 70
    prev = None
    for i, s in enumerate(steps):
        yy = by + i * 72
        frs.append(fitbox(bx, yy, 170, 52, s, size=12, fill=FILL, stroke=LINE))
        if prev is not None:
            frs.append(arrow(bx + 85, prev + 52, bx + 85, yy, color=INK, sw=1.8))
        prev = yy
    # лінк думки: ADC
    frs.append(text(bx + 85, by + 4 * 72 + 4, "далі — у висоту", size=11,
                    color=MUTED))

    render(os.path.join(IMG, "mems-pressure.svg"), W, H, *frs,
           title="MEMS-давач тиску: прогин мембрани стає числом")


# ── Фіг.3 — бюджет похибки: роздільність vs дрейф погоди vs опора ─────────────
def fig_error_budget():
    W, H = 720, 430
    frs = []
    # три «термометри» помилки в метрах, лог-ішня шкала підписами
    bars = [
        ("роздільність\nдавача", 0.1, FIELD, "що ДРІБНІШЕ давач\nбачить (≈ см)"),
        ("шум / дрейф\nнуля чипа", 0.5, NEG, "повільне сповзання\n(десятки см за хв)"),
        ("дрейф ПОГОДИ\n(фронт)", 30.0, POS, "1 гПа фронту\n= ~8 м фальшу"),
    ]
    base_y = 320
    x = 150
    maxlog = math.log10(40)
    for name, val, col, note in bars:
        # висота стовпчика за лог-масштабом
        hh = (math.log10(val) - math.log10(0.05)) / (maxlog - math.log10(0.05)) * 230
        hh = max(20, hh)
        frs.append(rect(x, base_y - hh, 90, hh, fill=col, stroke=INK, sw=1.5))
        frs.append(text(x + 45, base_y - hh - 10, "%g м" % val, size=13, bold=True,
                        color=INK))
        frs.append(mtext(x + 45, base_y + 22, name, size=12, color=INK))
        frs.append(mtext(x + 45, base_y + 58, note, size=10, color=MUTED))
        x += 170
    frs.append(line(140, base_y, 620, base_y, color=INK, sw=2))
    frs.append(text(W / 2, base_y + 92, "висота в метрах (лог-масштаб)", size=11,
                    color=MUTED))
    # висновок-рамка
    frs.append(fitbox(150, 70, 460, 40,
                      "Точність на коротку мить — чудова; точність «у метрах над морем» "
                      "вбиває погода.", size=12, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, "error-budget.svg"), W, H, *frs,
           title="Що обмежує барометричну висоту")


# ── Фіг.4 — утримання висоти: барометр (відносно старту) vs далекомір (до землі)
def fig_altitude_hold():
    W, H = 720, 400
    frs = []
    ground_y = 320
    # рельєф: рівнина, потім пагорб
    relief = ("M60 %d L300 %d Q420 %d 470 %d Q540 %d 620 %d L660 %d"
              % (ground_y, ground_y, ground_y, ground_y - 90,
                 ground_y - 90, ground_y, ground_y))
    frs.append('<path d="%s L660 360 L60 360 Z" fill="#eef2f6" stroke="%s" '
               'stroke-width="2"/>' % (relief, INK))
    frs.append(text(170, ground_y + 30, "земля (рельєф)", size=12, color=MUTED))

    # точка старту й лінія обнуленого барометричного нуля
    start_x = 90
    frs.append(circle(start_x, ground_y, 6, fill=INK, stroke=INK))
    frs.append(text(start_x, ground_y + 26, "старт\n(нуль баро)", size=11, color=INK))

    # горизонтальна траєкторія дрона на сталій баро-висоті
    fly_y = ground_y - 150
    frs.append(line(120, fly_y, 640, fly_y, color=POS, sw=3, dash="9 5"))
    frs.append(text(380, fly_y - 12, "барометр тримає СТАЛУ висоту над точкою старту",
                    size=12, color=POS, bold=True))
    # дрон-маркер
    drone_x = 500
    frs.append(rect(drone_x - 16, fly_y - 8, 32, 16, fill="#fdecea", stroke=POS, sw=2))

    # барометрична висота (стала) — зелена стрілка від рівня старту
    frs.append(line(140, fly_y, 140, ground_y, color=FIELD, sw=2))
    frs.append(arrow(140, ground_y, 140, fly_y, color=FIELD, sw=2))
    frs.append(text(108, (fly_y + ground_y) / 2, "баро\nвисота", size=11,
                    color=FIELD, anchor="middle"))

    # далекомір: відстань ВНИЗ до фактичної землі (над пагорбом — менша!)
    hill_top_y = ground_y - 90
    frs.append(arrow(drone_x, fly_y + 8, drone_x, hill_top_y, color=NEG, sw=2))
    frs.append(text(drone_x + 70, (fly_y + hill_top_y) / 2,
                    "далекомір:\nреальний\nпросвіт до\nземлі тут", size=11,
                    color=NEG, anchor="middle"))
    # підкреслити, що над пагорбом просвіт менший
    frs.append(text(470, hill_top_y - 8, "над пагорбом земля ближче!", size=11,
                    color=NEG))

    render(os.path.join(IMG, "altitude-hold.svg"), W, H, *frs,
           title="Утримання висоти: над морем (баро) vs над землею (далекомір)")


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури ДЕТАЛЬНОЇ статті (-d.md): глибша механіка й виведення
# ══════════════════════════════════════════════════════════════════════════════

# ── Фіг.D1 — гідростатична рівновага тонкого шару повітря ─────────────────────
def fig_hydrostatic_slab():
    """Сили на тонкий шар товщиною dh: тиск знизу штовхає вгору, тиск зверху
    плюс вага штовхають униз → dp = −ρ g dh."""
    W, H = 720, 430
    frs = []
    cx = 250
    sw_ = 150               # ширина стовпа
    top, bot = 120, 250     # верх/низ виділеного шару
    xl, xr = cx - sw_ / 2, cx + sw_ / 2

    # стовп повітря (світлий), із виділеним тонким шаром
    frs.append(rect(xl, 70, sw_, 300, fill="#eef4fb", stroke=MUTED, sw=1.2))
    frs.append(text(cx, 60, "стовп повітря", size=12, color=MUTED))
    # тонкий шар dh
    frs.append(rect(xl, top, sw_, bot - top, fill="#eaf0fd", stroke=NEG, sw=2))
    frs.append(text(xr + 14, (top + bot) / 2 + 4, "шар  dh", size=13, color=NEG,
                    bold=True, anchor="start"))

    # тиск знизу p (штовхає ВГОРУ) — стрілка вгору по нижній грані
    frs.append(arrow(cx, bot + 46, cx, bot + 4, color=FIELD, sw=2.4))
    frs.append(text(cx, bot + 64, "тиск знизу  p · A  ↑", size=12, color=FIELD,
                    bold=True))
    # тиск зверху p+dp (штовхає ВНИЗ) — стрілка вниз по верхній грані
    frs.append(arrow(cx, top - 46, cx, top - 4, color=POS, sw=2.4))
    frs.append(text(cx, top - 54, "тиск зверху  (p+dp) · A  ↓", size=12, color=POS,
                    bold=True))
    # вага шару — стрілка вниз усередині
    frs.append(arrow(cx - 44, (top + bot) / 2 - 18, cx - 44, (top + bot) / 2 + 22,
                     color=INK, sw=2))
    frs.append(mtext(cx - 50, (top + bot) / 2 - 4, "вага\nρ·A·dh·g", size=11,
                     color=INK, anchor="end"))

    # висновок-виведення праворуч
    frs.append(fitbox(430, 100, 250, 210,
        "Рівновага сил на шар:\n\n"
        "p·A  =  (p+dp)·A  +  ρ·A·dh·g\n\n"
        "звідси, скоротивши A:\n\n"
        "     dp  =  − ρ·g·dh\n\n"
        "Тиск падає (dp<0) рівно на\n"
        "вагу шару, що додався зверху.\n"
        "Це — гідростатика, з якої\n"
        "виростає вся формула висоти.",
        size=12, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "hydrostatic-slab.svg"), W, H, *frs,
           title="Звідки береться dp = −ρ·g·dh: сили на тонкий шар повітря")


# ── Фіг.D2 — дві моделі атмосфери: ізотермічна (експонента) vs лінійний спад ──
def fig_two_models():
    """Ізотермічна модель (чиста експонента, стала T) vs модель зі сталим спадом
    температури (степенева, ISA). Низько збігаються, високо розходяться."""
    W, H = 720, 470
    x0, y0 = 110, 70
    gw, gh = 430, 320
    xb, yb = x0, y0 + gh

    p0 = 1013.0
    hmax = 16000.0
    # степенева ISA
    L, T0, expo = 0.0065, 288.15, 5.255
    def p_isa(h): return p0 * (1 - L * h / T0) ** expo
    # ізотермічна: p = p0 * exp(-h/Hs), Hs = R*T0/(g*M) ≈ 8434 м при T0
    Hs = 8434.0
    def p_iso(h): return p0 * math.exp(-h / Hs)

    def X(p): return xb + (p0 - p) / p0 * gw
    def Y(h): return yb - h / hmax * gh

    frs = []
    frs.append(line(xb, yb, xb + gw, yb, color=INK, sw=2))
    frs.append(line(xb, yb, xb, y0, color=INK, sw=2))
    frs.append(text(xb + gw / 2, yb + 44, "тиск, гПа  (падає праворуч)", size=13,
                    color=MUTED))
    frs.append(text(x0 - 74, y0 + gh / 2, "висота, км", size=13, color=MUTED))
    for hk in (0, 4, 8, 12, 16):
        yy = Y(hk * 1000)
        frs.append(line(xb - 5, yy, xb, yy, color=INK, sw=1.5))
        frs.append(text(xb - 12, yy + 4, "%d" % hk, size=12, color=INK, anchor="end"))
    for pp in (1013, 700, 500, 300, 200, 100):
        xx = X(pp)
        frs.append(line(xx, yb, xx, yb + 5, color=INK, sw=1.5))
        frs.append(text(xx, yb + 20, "%d" % pp, size=11, color=INK))

    # ізотермічна крива (пунктир, синя)
    pts = []
    h = 0.0
    while h <= hmax + 1:
        pts.append("%.1f,%.1f" % (X(p_iso(h)), Y(h)))
        h += 200
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
               'stroke-dasharray="8 5"/>' % (" ".join(pts), NEG))

    # ISA степенева (суцільна, червона) — до 11 км, далі позначка тропопаузи
    pts = []
    h = 0.0
    while h <= 11000 + 1:
        pts.append("%.1f,%.1f" % (X(p_isa(h)), Y(h)))
        h += 150
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
               % (" ".join(pts), POS))
    # тропопауза
    yt = Y(11000)
    frs.append(line(xb, yt, X(p_isa(11000)), yt, color=MUTED, sw=1, dash="3 4"))
    frs.append(text(X(p_isa(11000)) + 6, yt + 4, "тропопауза ~11 км", size=10,
                    color=MUTED, anchor="start"))

    # підписи кривих
    frs.append(fitbox(X(430) - 8, Y(3200), 208, 44,
        "лінійний спад T (ISA):\nстепенева, exp 5.255", size=11,
        fill="#fdecea", stroke=POS, color=POS))
    frs.append(fitbox(xb + 8, Y(13600), 232, 44,
        "стала T (ізотермічна):\nчиста експонента, H≈8.4 км", size=11,
        fill="#eaf0fd", stroke=NEG, color=NEG))

    # правий стовпчик-висновок
    frs.append(fitbox(x0 + gw + 22, y0 + 20, 158, 250,
        "Низько обидві\nмоделі майже\nзбігаються —\n"
        "тому лінійне\nнаближення й\nпрацює біля\nземлі.\n\n"
        "Високо стала T\nбреше: реальна\nT падає, повітря\n"
        "холодніше й\nщільніше за\nізотермічне.", size=11, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "two-models.svg"), W, H, *frs,
           title="Дві моделі атмосфери: ізотермічна проти лінійного спаду T")


# ── Фіг.D3 — температурна похибка висоти: холодний/стандартний/теплий день ────
def fig_temperature_error():
    """Той самий виміряний тиск → різна ІСТИННА висота залежно від температури
    шару. Множник T_реальна / T_ISA. «High to low, look out below»."""
    W, H = 720, 430
    frs = []
    ground_y = 330
    frs.append(line(90, ground_y, 640, ground_y, color=INK, sw=2))
    frs.append(text(365, ground_y + 24, "рівень, де тиск = p (однаковий у трьох випадках)",
                    size=11, color=MUTED))

    # три стовпці: холодний, стандартний, теплий
    cols = [
        ("ХОЛОДНИЙ день", -18, NEG, 0.82, "нижче, ніж показує!"),
        ("стандарт (ISA)", 15, INK, 1.00, "показ = правда"),
        ("ТЕПЛИЙ день", 40, POS, 1.09, "вище, ніж показує"),
    ]
    xs = [180, 365, 550]
    baro_top = 110      # висота, яку ПОКАЗУЄ барометр (однакова)
    for (name, t, col, k, note), x in zip(cols, xs):
        true_top = ground_y - (ground_y - baro_top) * k
        # показана висота (пунктир, сірий) — однакова в усіх
        frs.append(line(x, ground_y, x, baro_top, color=MUTED, sw=1.2, dash="4 4"))
        frs.append(circle(x, baro_top, 4, fill="#ffffff", stroke=MUTED, sw=1.5))
        # істинна висота (кольорова суцільна стрілка)
        frs.append(arrow(x, ground_y, x, true_top, color=col, sw=2.6))
        frs.append(circle(x, true_top, 5, fill=col, stroke=col))
        frs.append(text(x, true_top - 12, "істинна", size=10, color=col, bold=True))
        frs.append(mtext(x, ground_y + 52, "%s\n%+d °C" % (name, t), size=11, color=col))
        frs.append(text(x, ground_y + 92, note, size=10, color=MUTED))

    # показана висота — спільна лінія
    frs.append(line(xs[0] - 26, baro_top, xs[-1] + 26, baro_top, color=MUTED,
                    sw=1, dash="2 4"))
    frs.append(mtext(xs[-1] + 30, baro_top - 8, "показ\nбарометра\n(однаковий)", size=10,
                     color=MUTED, anchor="start"))

    frs.append(fitbox(150, 48, 420, 46,
        "Множник висоти = T_реальна / T_ISA.\n"
        "Холодне повітря щільніше —\nістинна висота НИЖЧА за показ.",
        size=11, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, "temperature-error.svg"), W, H, *frs,
           title="Температура зсуває висоту: холодний день — небезпечний")


# ── Фіг.D4 — комплементарний фільтр вертикалі: баро + акселерометр ────────────
def fig_vertical_fusion():
    """Барометр (повільний, шумний, абсолютний) + подвійний інтеграл акселерометра
    (швидкий, дрейфує) → комплементарний фільтр дає гладку й незсунену висоту."""
    W, H = 720, 420
    frs = []
    # ліворуч — два джерела
    bx = 60
    frs.append(fitbox(bx, 90, 210, 66,
        "БАРОМЕТР\nабсолютна висота,\nповільна + шумна", size=12,
        fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))
    frs.append(fitbox(bx, 250, 210, 66,
        "АКСЕЛЕРОМЕТР (вісь Z)\nдвічі проінтегрувати →\nшвидка, але ДРЕЙФУЄ", size=12,
        fill="#fdecea", stroke=POS, color=POS, bold=True))

    # фільтри частот
    fx = 320
    frs.append(fitbox(fx, 96, 150, 54, "НИЗЬКІ частоти\n(повільна правда)", size=11,
                      fill=FILL, stroke=NEG))
    frs.append(fitbox(fx, 254, 150, 54, "ВИСОКІ частоти\n(швидка зміна)", size=11,
                      fill=FILL, stroke=POS))
    frs.append(arrow(bx + 210, 123, fx, 123, color=NEG, sw=2))
    frs.append(arrow(bx + 210, 283, fx, 281, color=POS, sw=2))

    # суматор
    sx, sy = 545, 205
    frs.append(circle(sx, sy, 26, fill="#ffffff", stroke=INK, sw=2))
    frs.append(text(sx, sy + 7, "+", size=26, color=INK, bold=True))
    frs.append(arrow(fx + 150, 123, sx - 20, sy - 14, color=NEG, sw=2))
    frs.append(arrow(fx + 150, 281, sx - 20, sy + 14, color=POS, sw=2))

    # вихід
    frs.append(arrow(sx + 26, sy, 640, sy, color=FIELD, sw=2.6))
    frs.append(fitbox(600, sy - 34, 110, 68,
        "ВИСОТА:\nгладка +\nбез дрейфу", size=11, fill="#eafaf0", stroke=FIELD,
        color=FIELD, bold=True))

    # частота зрізу
    frs.append(fitbox(300, 350, 380, 50,
        "Частота зрізу ставить межу довіри: повільніше за неї віримо барометру "
        "(не дрейфує), швидше — акселерометру (не шумить). Точнісінько як крен = "
        "гіро+акселерометр, лише для вертикалі.", size=11, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "vertical-fusion.svg"), W, H, *frs,
           title="Комплементарний фільтр вертикалі: баро (повільне) + акселерометр (швидке)")


# ══════════════════════════════════════════════════════════════════════════════
#  Фігура вставки math-barometric-derivation.md: границя L→0
# ══════════════════════════════════════════════════════════════════════════════

# ── Фіг.M1 — сім'я степеневих кривих сходиться до експоненти при L→0 ───────────
def fig_lapse_limit():
    """Та сама відносна зміна тиску p/p0 від висоти для кількох значень спаду L.
    Що менший L, то ближча степенева крива до чистої експоненти (стала T).
    При L=0 степенева форма ПЕРЕХОДИТЬ в експоненційну — ту саму, з масштабом
    висоти H=RT0/(Mg)."""
    W, H = 720, 470
    x0, y0 = 96, 64
    gw, gh = 430, 330
    xb, yb = x0, y0 + gh

    g, M, R, T0 = 9.80665, 0.0289644, 8.31447, 288.15
    hmax = 16000.0
    Hs = R * T0 / (M * g)           # масштаб висоти ≈ 8435 м

    def p_pow(h, L):               # степенева: (1 − L·h/T0)^(gM/RL)
        ex = g * M / (R * L)
        base = 1 - L * h / T0
        return base ** ex if base > 0 else 0.0

    def p_exp(h):                  # границя L→0: exp(−h/Hs)
        return math.exp(-h / Hs)

    def X(pr): return xb + pr * gw            # pr = p/p0 у [0..1], зліва 1 → справа 0
    def Y(h):  return yb - h / hmax * gh

    frs = []
    # осі
    frs.append(line(xb, yb, xb + gw, yb, color=INK, sw=2))
    frs.append(line(xb, yb, xb, y0, color=INK, sw=2))
    frs.append(text(xb + gw / 2, yb + 44, "відносний тиск  p / p₀", size=13, color=MUTED))
    frs.append(text(x0 - 66, y0 + gh / 2, "висота, км", size=13, color=MUTED))
    for hk in (0, 4, 8, 12, 16):
        yy = Y(hk * 1000)
        frs.append(line(xb - 5, yy, xb, yy, color=INK, sw=1.5))
        frs.append(text(xb - 12, yy + 4, "%d" % hk, size=12, color=INK, anchor="end"))
    for pr in (1.0, 0.75, 0.5, 0.25, 0.0):
        xx = X(pr)
        frs.append(line(xx, yb, xx, yb + 5, color=INK, sw=1.5))
        frs.append(text(xx, yb + 20, "%.2f" % pr, size=11, color=INK))

    # степеневі криві для кількох L (що менший L — то ближче до експоненти)
    fam = [(0.0065, NEG, "L = 6.5 K/км (реальний)"),
           (0.0020, "#7aa0e8", "L = 2 K/км"),
           (0.0005, "#b9cbf3", "L = 0.5 K/км")]
    for L, col, _lbl in fam:
        pts = []
        h = 0.0
        while h <= hmax + 1:
            pr = p_pow(h, L)
            if pr <= 0:
                break
            pts.append("%.1f,%.1f" % (X(pr), Y(h)))
            h += 160
        frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                   % (" ".join(pts), col))

    # границя L→0: чиста експонента (товста зелена)
    pts = []
    h = 0.0
    while h <= hmax + 1:
        pts.append("%.1f,%.1f" % (X(p_exp(h)), Y(h)))
        h += 160
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.4"/>'
               % (" ".join(pts), FIELD))

    # легенда
    lx, ly = X(0.30), Y(15200)
    frs.append(fitbox(lx, ly, 200, 118,
        "L = 6.5 K/км  (степенева)\n"
        "L = 2 K/км\n"
        "L = 0.5 K/км\n"
        "L → 0:  exp(−h/H),  H≈8.4 км",
        size=11, fill=FILL, stroke=LINE))
    # кольорові мітки біля рядків легенди
    for i, (col, _) in enumerate([(NEG, 0), ("#7aa0e8", 1), ("#b9cbf3", 2), (FIELD, 3)]):
        yy = ly + 20 + i * 22
        frs.append(line(lx + 8, yy, lx + 26, yy, color=col, sw=3.2))

    # висновок-стовпчик праворуч
    frs.append(fitbox(x0 + gw + 22, y0 + 14, 156, 300,
        "Що МЕНШИЙ спад\nтемператури L,\nто ближча\n"
        "степенева крива\nдо чистої\nекспоненти.\n\n"
        "При L=0 показник\ngM/(RL) прямує\nдо ∞, а вся\n"
        "степенева форма\nПЕРЕХОДИТЬ у\nexp(−h/H) —\n"
        "ізотермічну\nатмосферу зі\nсталою T.",
        size=11, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(IMG, "lapse-limit.svg"), W, H, *frs,
           title="Границя L→0: степенева форма стає експонентою")


# ── Вставка comp: блок-схема класу MEMS-давача тиску ─────────────────────────
def fig_comp_blockdiagram():
    W, H = 760, 380
    frs = []
    # межа кристала (усе, що всередині корпусу) — пунктирна рамка вручну
    frs.append('<rect x="40" y="56" width="560" height="292" rx="8" fill="#fbfcfd" '
               'stroke="%s" stroke-width="1.5" stroke-dasharray="6 5"/>' % MUTED)
    frs.append(text(50, 74, "усередині корпусу (один кристал)", size=11,
                    color=MUTED, anchor="start"))

    # чутливий елемент (мембрана над камерою)
    frs.append(fitbox(70, 110, 150, 74,
                      "чутливий елемент:\nмембрана над\nеталонною камерою",
                      size=11, fill="#fdecea", stroke=POS, color=POS))
    # окремий тепловий давач
    frs.append(fitbox(70, 214, 150, 60,
                      "давач власної\nтемператури кристала",
                      size=11, fill="#eaf0fd", stroke=NEG, color=NEG))
    # мультиплексор
    frs.append(fitbox(258, 150, 92, 84, "мульти-\nплексор\n(p / T)",
                      size=11, fill=FILL, stroke=LINE))
    # 24-біт сигма-дельта АЦП
    frs.append(fitbox(388, 150, 128, 84, "24-біт\nΣΔ АЦП\n+ усереднення",
                      size=12, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))
    # ПЗП коефіцієнтів
    frs.append(fitbox(258, 262, 258, 60,
                      "ПЗП: заводські калібрувальні коефіцієнти чипа",
                      size=11, fill="#fff7e6", stroke="#b7791f", color="#8a5a00"))

    # інтерфейсний блок (частково на межі корпусу — виходить назовні)
    frs.append(fitbox(548, 150, 92, 84, "інтер-\nфейс\nI2C / SPI",
                      size=11, fill=FILL, stroke=LINE))

    # стрілки шляху сигналу
    frs.append(arrow(220, 147, 258, 175, color=POS, sw=1.8))     # мембрана -> mux
    frs.append(arrow(220, 244, 258, 210, color=NEG, sw=1.8))     # темп -> mux
    frs.append(arrow(350, 192, 388, 192, color=INK, sw=1.8))     # mux -> ADC
    frs.append(arrow(516, 192, 548, 192, color=INK, sw=1.8))     # ADC -> iface
    # коефіцієнти НЕ йдуть у АЦП, а віддаються назовні по тій самій шині
    frs.append(arrow(516, 288, 594, 236, color="#b7791f", sw=1.6))  # ПЗП -> інтерфейс
    frs.append(text(387, 340, "коефіцієнти хост читає по шині при старті",
                    size=10, color="#8a5a00"))

    # хост зовні
    frs.append(arrow(640, 192, 686, 192, color=INK, sw=2))
    frs.append(fitbox(648, 150, 96, 120,
                      "ХОСТ (МК):\n\n1) коефіцієнти\n2) сирий T\n3) сирий p\n"
                      "4) компенсація",
                      size=11, fill="#eef2f6", stroke=INK))

    render(os.path.join(IMG, "comp-blockdiagram.svg"), W, H, *frs,
           title="Клас MEMS-давача тиску: що всередині корпусу")


# ── Вставка comp: розпіновка й два рішення обв'язки (шина + адреса) ───────────
def fig_comp_pinout():
    W, H = 760, 430
    frs = []
    # корпус чипа у центрі
    cw, ch = 150, 210
    cx0, cy0 = 305, 110
    frs.append(rect(cx0, cy0, cw, ch, fill="#eef2f6", stroke=INK, sw=2))
    frs.append(text(cx0 + cw / 2, cy0 + ch / 2 - 6, "MEMS-", size=13, color=MUTED))
    frs.append(text(cx0 + cw / 2, cy0 + ch / 2 + 12, "барометр", size=13, color=MUTED))

    # піни ліворуч (живлення / земля) і праворуч (шина)
    left = [("VDD", "живлення аналогу"), ("VDDIO", "живлення шини"),
            ("GND", "спільна земля")]
    right = [("SCK", "такт (SCL для I2C)"), ("SDI", "дані в (SDA для I2C)"),
             ("SDO", "дані назовні / адреса"), ("CSB", "вибір шини й чипа")]

    py0 = cy0 + 34
    for i, (nm, desc) in enumerate(left):
        yy = py0 + i * 52
        frs.append(line(cx0 - 34, yy, cx0, yy, color=INK, sw=2))
        frs.append(text(cx0 - 40, yy - 4, nm, size=12, bold=True, color=INK, anchor="end"))
        frs.append(text(cx0 - 40, yy + 12, desc, size=10, color=MUTED, anchor="end"))
    for i, (nm, desc) in enumerate(right):
        yy = py0 + i * 46
        frs.append(line(cx0 + cw, yy, cx0 + cw + 34, yy, color=INK, sw=2))
        col = POS if nm in ("CSB", "SDO") else INK
        frs.append(text(cx0 + cw + 40, yy - 4, nm, size=12, bold=True, color=col, anchor="start"))
        frs.append(text(cx0 + cw + 40, yy + 12, desc, size=10, color=MUTED, anchor="start"))

    # два рішення — рамки внизу
    frs.append(fitbox(60, 336, 320, 78,
                      "РІШЕННЯ 1 — яка шина? Це визначає CSB:\n"
                      "CSB на живлення (тримати HIGH)  →  I2C\n"
                      "CSB смикає хост (chip-select)   →  SPI",
                      size=11, fill="#fdecea", stroke=POS, color=INK))
    frs.append(fitbox(400, 336, 300, 78,
                      "РІШЕННЯ 2 — адреса на I2C? Її задає SDO:\n"
                      "SDO на землю     →  молодший біт 0\n"
                      "SDO на живлення  →  молодший біт 1",
                      size=11, fill="#eaf0fd", stroke=NEG, color=INK))

    render(os.path.join(IMG, "comp-pinout.svg"), W, H, *frs,
           title="Типова розпіновка: два піни-перемикачі — CSB і SDO")


# ── Вставка comp: компроміс передискретизації — тиша vs затримка vs самонагрів ─
def fig_comp_tradeoff():
    W, H = 720, 400
    frs = []
    x0, y0 = 110, 70
    gw, gh = 470, 250
    xb, yb = x0, y0 + gh
    # осі
    frs.append(line(xb, yb, xb + gw, yb, color=INK, sw=2))
    frs.append(line(xb, yb, xb, y0, color=INK, sw=2))
    frs.append(text(xb + gw / 2, yb + 42, "передискретизація (×2, ×4, ×8 …)  →",
                    size=12, color=MUTED))
    frs.append(text(x0 - 66, y0 + gh / 2, "більше →", size=11, color=MUTED, anchor="middle"))

    N = 6           # кроки ×1..×32
    def X(i): return xb + (i + 0.5) / N * gw

    # крива «роздільність росте» (виграш) — насичується
    pts_res = []
    for i in range(N):
        val = 1 - 0.8 ** (i + 1)                 # монотонно вгору, насичення
        pts_res.append((X(i), yb - val * gh * 0.9))
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
               % (" ".join("%.1f,%.1f" % p for p in pts_res), FIELD))

    # крива «затримка росте» — лінійна вгору (плата часом)
    pts_lat = []
    for i in range(N):
        pts_lat.append((X(i), yb - (i / (N - 1)) * gh * 0.9))
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
               'stroke-dasharray="8 5"/>'
               % (" ".join("%.1f,%.1f" % p for p in pts_lat), NEG))

    # крива «самонагрів росте» при частому опитуванні — прискорюється
    pts_heat = []
    for i in range(N):
        pts_heat.append((X(i), yb - (i / (N - 1)) ** 1.7 * gh * 0.9))
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
               'stroke-dasharray="2 4"/>'
               % (" ".join("%.1f,%.1f" % p for p in pts_heat), POS))

    # мітки осі X
    for i, lab in enumerate(["×1", "×2", "×4", "×8", "×16", "×32"]):
        frs.append(text(X(i), yb + 18, lab, size=11, color=INK))

    # легенда
    lx, ly = xb + gw - 6, y0 + 6
    frs.append(fitbox(lx - 236, ly, 236, 92,
                      "———  роздільність (виграш) — насичується\n"
                      "– – –  затримка віддачі (плата часом)\n"
                      "· · ·  самонагрів при частому опитуванні",
                      size=11, fill=BG, stroke=LINE, color=INK))
    # підфарбувати перші символи легенди кольором — окремі короткі лінії
    frs.append(line(lx - 232, ly + 22, lx - 210, ly + 22, color=FIELD, sw=3))
    frs.append(line(lx - 232, ly + 44, lx - 210, ly + 44, color=NEG, sw=3, dash="8 5"))
    frs.append(line(lx - 232, ly + 66, lx - 210, ly + 66, color=POS, sw=3, dash="2 4"))

    render(os.path.join(IMG, "comp-tradeoff.svg"), W, H, *frs,
           title="Одна ручка тягне три речі одразу")


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури ІСТОРИЧНОЇ вставки (hist-standard-atmosphere.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── Фіг.H1 — шлях до однієї домовленої атмосфери: 1919 → 1964 ─────────────────
def fig_atmosphere_timeline():
    """Хронологія: від пропозиції Тусена (1919) через національні стандарти
    1920-х до єдиного стандарту ICAO (1952/54) і його розширення (1964)."""
    W, H = 760, 430
    frs = []
    ax_y = 150
    x0, x1 = 70, 690
    frs.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2.5))
    frs.append(arrow(x1 - 2, ax_y, x1 + 8, ax_y, color=INK, sw=2.5))

    nodes = [
        (1919, "Тусен пропонує\n6.5 K/км, 15 °C", "up", NEG),
        (1920, "Франція й Італія\nформалізують", "down", FIELD),
        (1925, "США (NACA):\nсвій стандарт", "up", INK),
        (1952, "ICAO зводить у\nМІЖНАРОДНИЙ", "down", POS),
        (1964, "розширення\nвгору (32 км)", "up", MUTED),
    ]
    span = {1919: 0.02, 1920: 0.20, 1925: 0.42, 1952: 0.74, 1964: 0.96}
    for yr, label, side, col in nodes:
        x = x0 + span[yr] * (x1 - x0)
        frs.append(circle(x, ax_y, 7, fill=col, stroke=col))
        frs.append(text(x, ax_y + (28 if side == "down" else -16),
                        str(yr), size=15, color=col, bold=True))
        if side == "up":
            frs.append(fitbox(x - 78, ax_y - 108, 156, 60, label, size=12,
                              fill=FILL, stroke=col, color=col))
            frs.append(line(x, ax_y - 48, x, ax_y - 8, color=col, sw=1.2, dash="3 3"))
        else:
            frs.append(fitbox(x - 78, ax_y + 44, 156, 60, label, size=12,
                              fill=FILL, stroke=col, color=col))
            frs.append(line(x, ax_y + 8, x, ax_y + 44, color=col, sw=1.2, dash="3 3"))

    frs.append(fitbox(90, 350, 580, 54,
        "За піввіку розрізнені національні таблиці зійшлися в ОДНУ домовлену "
        "атмосферу — щоб два будь-які висотоміри світу з того самого тиску діставали "
        "ту саму висоту.", size=13, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, "atmosphere-timeline.svg"), W, H, *frs,
           title="Шлях до однієї атмосфери: 1919 -> 1964")


# ── Фіг.H2 — домовлений «середній день» проти справжніх днів ─────────────────
def fig_agreed_vs_real():
    """15 °C і 6.5 K/км — не закон природи, а домовлена пряма посередині хмари
    справжніх, різних профілів температури над реальними днями."""
    W, H = 720, 450
    x0, y0 = 120, 60
    gw, gh = 380, 320
    xb, yb = x0, y0 + gh

    Tmin, Tmax = -70.0, 45.0
    hmax = 11000.0
    def X(t): return xb + (t - Tmin) / (Tmax - Tmin) * gw
    def Y(h): return yb - h / hmax * gh

    frs = []
    frs.append(line(xb, yb, xb + gw, yb, color=INK, sw=2))
    frs.append(line(xb, yb, xb, y0, color=INK, sw=2))
    frs.append(text(xb + gw / 2, yb + 44, "температура, °C", size=13, color=MUTED))
    frs.append(text(x0 - 84, y0 + gh / 2, "висота, км", size=13, color=MUTED))
    for tk in (-60, -40, -20, 0, 20, 40):
        xx = X(tk)
        frs.append(line(xx, yb, xx, yb + 5, color=INK, sw=1.2))
        frs.append(text(xx, yb + 20, "%d" % tk, size=11, color=INK))
    for hk in (0, 3, 6, 9, 11):
        yy = Y(hk * 1000)
        frs.append(line(xb - 5, yy, xb, yy, color=INK, sw=1.2))
        frs.append(text(xb - 12, yy + 4, "%d" % hk, size=11, color=INK, anchor="end"))

    real = [
        (30.0, 0.0072, MUTED),
        (5.0, 0.0058, MUTED),
        (-10.0, 0.0064, MUTED),
        (22.0, 0.0069, MUTED),
    ]
    for t0, L, col in real:
        pts = []
        h = 0.0
        while h <= hmax + 1:
            pts.append("%.1f,%.1f" % (X(t0 - L * h), Y(h)))
            h += 400
        frs.append('<polyline points="%s" fill="none" stroke="%s" '
                   'stroke-width="1.6" stroke-dasharray="5 4" opacity="0.75"/>'
                   % (" ".join(pts), col))

    pts = []
    h = 0.0
    while h <= hmax + 1:
        pts.append("%.1f,%.1f" % (X(15.0 - 0.0065 * h), Y(h)))
        h += 200
    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.4"/>'
               % (" ".join(pts), POS))
    frs.append(circle(X(15.0), Y(0), 6, fill=POS, stroke=POS))
    frs.append(text(X(15.0) + 8, Y(0) - 8, "15 °C", size=12, color=POS, bold=True,
                    anchor="start"))

    frs.append(fitbox(X(15.0) - 10, Y(7600), 210, 44,
        "ДОМОВЛЕНА пряма ISA:\n15 °C, спад 6.5 K/км", size=12,
        fill="#fdecea", stroke=POS, color=POS))
    frs.append(fitbox(xb + 6, Y(2400), 150, 40,
        "справжні дні —\nусі різні", size=11, fill=FILL, stroke=MUTED, color=MUTED))

    frs.append(fitbox(x0 + gw + 22, y0 + 10, 150, 300,
        "Жоден реальний\nдень не лягає\nточно на червону\nпряму.\n\n"
        "Її обрали НЕ бо\nтака природа, а\nбо треба ОДНА\n"
        "спільна опора,\nна якій зійдуться\nвсі висотоміри.\n\n"
        "Кожне відхилення\nсправжнього дня\nвід неї — це\n"
        "похибка висоти.", size=11, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "agreed-vs-real.svg"), W, H, *frs,
           title="15 °C і 6.5 K/км — домовленість, а не закон природи")


if __name__ == "__main__":
    fig_pressure_altitude()
    fig_mems_pressure()
    fig_error_budget()
    fig_altitude_hold()
    # фігури детальної статті
    fig_hydrostatic_slab()
    fig_two_models()
    fig_temperature_error()
    fig_vertical_fusion()
    # фігура вставки-математики
    fig_lapse_limit()
    # фігури вставки comp (клас MEMS-давача тиску)
    fig_comp_blockdiagram()
    fig_comp_pinout()
    fig_comp_tradeoff()
    # фігури історичної вставки (стандартна атмосфера)
    fig_atmosphere_timeline()
    fig_agreed_vs_real()
    print("OK: figures written to", IMG)
