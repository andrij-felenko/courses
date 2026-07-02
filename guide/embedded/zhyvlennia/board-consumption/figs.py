# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── who-sleeps: хто на платі їсть струм, поки чип спить ────────────────────────
# Ідея: у спокої струм тече не в чип, а в обвʼязку. Стовпчики споживачів у
# логарифмічній шкалі (бо діапазон — від 10 мкА до 4 мА, чотири порядки), щоб
# сплячий чип узагалі було видно поряд із power-LED.

def fig_who_sleeps():
    import math
    W, H = 720, 360
    bx, by = 70, 290          # лівий-нижній кут поля
    bw, bh = 600, 230         # поле графіка
    p = []

    # логарифмічна шкала струму: від 1 мкА (низ) до 10 мА (верх)
    lo, hi = 1e-3, 10.0       # у мА
    def ytop(ma):             # верх стовпчика для струму ma (мА)
        t = (math.log10(max(ma, lo)) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))
        return by - t * bh

    # сітка декад із підписами
    for dec, lab in [(1e-3, "1 мкА"), (1e-2, "10 мкА"), (1e-1, "100 мкА"),
                     (1.0, "1 мА"), (10.0, "10 мА")]:
        gy = ytop(dec)
        p.append(line(bx, gy, bx + bw, gy, color="#e3e7ee", sw=1.0))
        p.append(text(bx - 8, gy + 4, lab, size=10, color=MUTED, anchor="end"))

    bars = [
        ("power-LED\n330 Ом", 4.0, POS),
        ("LDO Iq\n(AMS1117)", 5.0, POS),
        ("USB-UART\n(міст)", 0.5, "#8a5fb0"),
        ("3 підтяжки\n10 кОм", 0.33, "#e67e22"),
        ("давач\nstandby", 0.0003, FIELD),
        ("ESP32\ndeep-sleep", 0.010, FIELD),
    ]
    n = len(bars)
    slot = bw / n
    cw = slot * 0.56
    for i, (lab, ma, col) in enumerate(bars):
        cx = bx + slot * (i + 0.5)
        top = ytop(ma)
        fill = {POS: "#fdecea", FIELD: "#eafaf1", "#8a5fb0": "#f2ecf8",
                "#e67e22": "#fdf2e9"}[col]
        p.append(rect(cx - cw / 2, top, cw, by - top, fill=fill, stroke=col, sw=1.8, rx=3))
        # значення над стовпчиком
        val = ("%.2f мА" % ma) if ma >= 0.01 else ("%d мкА" % round(ma * 1000))
        p.append(text(cx, top - 7, val, size=10, color=col, bold=True))
        # підпис під віссю
        p.append(mtext(cx, by + 18, lab, size=10, color=INK))

    # вісь
    p.append(line(bx, by, bx + bw, by, color=INK, sw=1.6))

    p.append(text(W / 2, H - 12,
                  "у спокої струм тече в обвʼязку, не в чип: сплячий ESP32 — наймовший стовпчик",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "who-sleeps.svg"), W, H, *p,
           title="Хто на платі не спить (логарифмічна шкала струму)")


# ── budget-before-after: бюджет спокою до і після оптимізації ──────────────────
# Ідея: два сумарні стовпчики — «з коробки» проти «оптимізовано», поряд із
# рядком життя від CR2032. Видно, що виграш — кратний, і дають його кілька
# дешевих рішень на платі, без жодного рядка прошивки.

def fig_budget():
    W, H = 700, 340
    p = []
    # два стовпчики сумарного струму (лінійна шкала, бо порівнюємо суми)
    base_x, opt_x = 200, 470
    bw = 120
    axis_y = 280
    top_y = 70
    full_h = axis_y - top_y

    base_total = 5.84         # мА (сума «з коробки», без USB-UART у цифрі суми)
    opt_total = 0.048         # мА (48 мкА після оптимізації)
    base_h = full_h
    # оптимізований майже невидимий у лінійній шкалі — підкреслюємо це навмисно
    opt_h = max(3.0, full_h * opt_total / base_total)

    p.append(line(120, axis_y, 580, axis_y, color=INK, sw=1.6))

    # стовпчик «з коробки»
    p.append(rect(base_x - bw / 2, top_y, bw, base_h, fill="#fdecea", stroke=POS, sw=2, rx=4))
    p.append(text(base_x, top_y - 30, "DevKit «з коробки»", size=12, color=POS, bold=True))
    p.append(text(base_x, top_y - 12, "≈ 5.8 мА", size=12, color=POS, bold=True))
    p.append(mtext(base_x, axis_y + 22, "CR2032 220 мА·год\n≈ 1.5 доби", size=11, color=INK))

    # стовпчик «оптимізовано»
    p.append(rect(opt_x - bw / 2, axis_y - opt_h, bw, opt_h, fill="#eafaf1", stroke=FIELD, sw=2, rx=4))
    p.append(text(opt_x, axis_y - opt_h - 12, "≈ 48 мкА", size=12, color=FIELD, bold=True))
    p.append(text(opt_x, top_y - 12, "Оптимізовано", size=12, color=FIELD, bold=True))
    p.append(mtext(opt_x, axis_y + 22, "CR2032 220 мА·год\n≈ 6 місяців", size=11, color=INK))

    # стрілка виграшу
    p.append(line(base_x + bw / 2 + 6, top_y + 20, opt_x - bw / 2 - 6, top_y + 20,
                  color=MUTED, sw=1.4, dash="5 4"))
    b, _, _ = textbox((base_x + opt_x) / 2, top_y + 20, "× 120", size=13, bold=True,
                      color=FIELD, fill="#eafaf1", stroke=FIELD, sw=1.6, pad=8)
    p.append(b)

    p.append(text(W / 2, H - 14,
                  "виграш дають кілька дешевих рішень на платі — без жодного рядка прошивки",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "budget-before-after.svg"), W, H, *p,
           title="Бюджет спокою: до і після оптимізації плати")


# ── iq-stack: куди тече струм сплячого пристрою (для вставки LDO vs buck) ───────
# Ідея: корисне споживання (МК у сні) — тонка смужка; струм спокою дешевого LDO
# накриває її в сотні разів; low-Iq LDO повертає бюджет пристрою. Вісь із
# розривом, бо 5000 мкА і 15 мкА на одній лінійній шкалі несумісні.

def fig_iq_stack():
    W, H = 720, 500
    p = []
    base_y = 420          # рівень «0»
    # три колонки: корисне / AMS1117 / low-Iq
    cols = [150, 380, 610]
    cw = 110

    # вісь Y із розривом
    p.append(line(60, 60, 60, base_y + 5, color=LINE, sw=1.5))
    for ty, lab in [(base_y, "0"), (base_y - 38, "10"), (315, "30"),
                    (200, "60 мкА"), (125, "5000 мкА"), (65, "5200")]:
        p.append(line(55, ty, 60, ty, color=LINE, sw=1.0))
        p.append(text(52, ty + 4, lab, size=11, color=MUTED, anchor="end"))
    # позначка розриву осі
    p.append(line(52, 197, 65, 207, color=MUTED, sw=2.0))
    p.append(line(52, 178, 65, 188, color=MUTED, sw=2.0))
    p.append(rect(58, 185, 660, 15, fill="#f0f0f0", stroke="none", sw=0, rx=0))
    p.append(text(388, 197, "розрив осі", size=11, color=MUTED))

    # корисне споживання (однакове в усіх колонках) — синій блок ~15 мкА
    for cx in (cols[0], cols[2]):
        b, _, _ = textbox(cx, base_y - 29, "МК ~10 мкА\n+ периферія ~5 мкА",
                          size=9, fill="#eaf0fd", stroke=NEG, sw=1.5, pad=8)
        p.append(b)

    # AMS1117 — велика червона маса I_Q вище розриву
    p.append(rect(cols[1] - cw / 2, 125, cw, 60, fill="#fdecea", stroke=POS, sw=1.5, rx=3))
    b, _, _ = textbox(cols[1], 152, "I_Q AMS1117\n≈ 5000 мкА", size=12, bold=True,
                      fill="#fdecea", stroke=POS, sw=1.5, pad=8)
    p.append(b)
    p.append(rect(cols[1] - cw / 2, base_y - 29 - 28, cw, 28,
                  fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))

    # стрілка масштабу ×500
    p.append(line(cols[1] + cw / 2 + 4, 150, cols[1] + cw / 2 + 4, base_y - 5,
                  color=POS, sw=1.5, dash="4 3"))
    b, _, _ = textbox(cols[1] + cw / 2 + 48, 280, "× 500\nбільше", size=11, bold=True,
                      color=POS, fill="#fff0f0", stroke=POS, sw=1.5, pad=7)
    p.append(b)

    # low-Iq — тонка зелена смужка над корисним
    p.append(rect(cols[2] - cw / 2, base_y - 29 - 28 - 6, cw, 6,
                  fill="#27ae60", stroke=FIELD, sw=1.2, rx=2))
    b, _, _ = textbox(cols[2], 340, "I_Q low-Iq\n≈ 3 мкА", size=11, bold=True,
                      color=FIELD, fill="#f0fff4", stroke=FIELD, sw=1.5, pad=7)
    p.append(b)

    # підписи колонок під віссю
    labels = ["Корисне\nспоживання", "AMS1117-клас\n(I_Q ≈ 5 мА)", "low-Iq LDO\n(I_Q ≈ 3 мкА)"]
    for cx, lab in zip(cols, labels):
        b, _, _ = textbox(cx, base_y + 28, lab, size=11, pad=8)
        p.append(b)

    render(os.path.join(OUT, "iq-stack.svg"), W, H, *p,
           title="Куди тече струм сплячого пристрою")


# ── ldo-buck-crossover: хто виграє залежно від струму (для вставки) ────────────
# Ідея: дві криві неефективності в лог-шкалі струму. Зліва (сон) панує струм
# спокою — бере гору low-Iq LDO; справа (активність) панує ефективність — бере
# гору buck. Точка перетину каже, який клас обрати під профіль пристрою.

def fig_crossover():
    import math
    W, H = 720, 410
    p = []
    ox, oy = 70, 330          # початок осей
    aw, ah = 640, 272
    # лог-шкала струму від 10 мкА до 300 мА
    lo, hi = 1e-2, 300.0      # мА
    def xpos(ma):
        t = (math.log10(ma) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))
        return ox + t * aw

    # зони сну/передачі
    xcross = xpos(0.07)       # ~70 мкА
    p.append(rect(ox, oy - ah, xcross - ox, ah, fill="#eaf4fb", stroke="none", sw=0, rx=0))
    p.append(rect(xcross, oy - ah, ox + aw - xcross, ah, fill="#fef9e7", stroke="none", sw=0, rx=0))
    p.append(text((ox + xcross) / 2, oy - ah + 18, "тут живе «сон»", size=12, color=NEG))
    p.append(text((xcross + ox + aw) / 2, oy - ah + 18, "тут живе «передача»", size=12, color="#e67e22"))

    # криві неефективності (умовні): LDO низька в сні, росте на великому струмі;
    # buck висока в сні (I_Q контролера), падає на великому струмі
    def curve(fn, color):
        pts = []
        for i in range(0, 161):
            ma = lo * (hi / lo) ** (i / 160.0)
            pts.append("%.1f,%.1f" % (xpos(ma), oy - fn(ma) * ah))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" '
                'stroke-linejoin="round"/>' % (" ".join(pts), color))

    def ldo(ma):              # low-Iq LDO: майже нуль у сні, лінійно росте втрата на струмі
        return min(0.95, 0.05 + 0.78 * (math.log10(ma) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)))
    def buck(ma):             # buck: висока відносна втрата в сні, падає й виходить на плато
        t = (math.log10(ma) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))
        return 0.62 * math.exp(-3.0 * t) + 0.07
    p.append(curve(ldo, NEG))
    p.append(curve(buck, POS))

    # точка перетину
    p.append(circle(xcross, oy - ldo(0.07) * ah, 7, fill="#fff", stroke=FIELD, sw=2.5))
    b, _, _ = textbox(xcross + 10, oy - ldo(0.07) * ah - 48, "межа\nдоцільності\n(~70 мкА)",
                      size=11, color=FIELD, fill="#f0fff4", stroke=FIELD, sw=1.5, pad=7)
    p.append(b)

    # підписи кривих праворуч
    b, _, _ = textbox(ox + aw - 50, oy - ldo(300) * ah - 6, "LDO\n(low-Iq)", size=12, bold=True,
                      color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.5, pad=7)
    p.append(b)
    b, _, _ = textbox(ox + aw - 50, oy - buck(300) * ah + 20, "buck-PFM", size=12, bold=True,
                      color=POS, fill="#fdecea", stroke=POS, sw=1.5, pad=7)
    p.append(b)

    # осі
    p.append(line(ox, oy, ox + aw, oy, color=LINE, sw=1.5))
    p.append(line(ox, oy - ah, ox, oy, color=LINE, sw=1.5))
    for ma, lab in [(0.01, "10 мкА"), (0.05, "50"), (0.1, "100 мкА"),
                    (1.0, "1 мА"), (10.0, "10"), (100.0, "100"), (300.0, "300 мА")]:
        gx = xpos(ma)
        p.append(line(gx, oy, gx, oy + 5, color=LINE, sw=1.0))
        p.append(text(gx, oy + 18, lab, size=10, color=MUTED))
    p.append(text(ox + aw / 2, oy + 40, "струм навантаження (логарифмічна шкала)",
                  size=12, color=MUTED))
    p.append('<text x="22" y="%.0f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90, 22, %.0f)">відносна втрата (неефективність)</text>'
             % (oy - ah / 2, FONT, MUTED, oy - ah / 2))

    render(os.path.join(OUT, "ldo-buck-crossover.svg"), W, H, *p,
           title="Хто виграє — залежить від струму навантаження")


# ── inside-ldo: куди фізично тече струм спокою всередині LDO ───────────────────
# Ідея (для детальної): I_Q — це не одне число, а сума кількох завжди-живих
# гілок усередині стабілізатора: джерело опорної напруги (bandgap), підсилювач
# похибки, і — окремо — струм крізь дільник зворотного звʼязку. Показуємо блок-
# схему з підписаними струмами кожної гілки, щоб «I_Q» перестало бути магією.

def fig_inside_ldo():
    W, H = 720, 430
    p = []
    # рамка кристала LDO
    p.append(rect(60, 70, 470, 300, fill="#fbfcfe", stroke=LINE, sw=1.6, rx=10))
    p.append(text(295, 92, "усередині стабілізатора", size=12, color=MUTED, italic=True))

    # вхід / вихід / земля
    p.append(text(30, 130, "Vin", size=12, color=INK, bold=True, anchor="middle"))
    p.append(line(20, 140, 60, 140, color=POS, sw=2.2))
    p.append(text(690, 200, "Vout", size=12, color=INK, bold=True, anchor="middle"))
    p.append(line(530, 200, 660, 200, color=FIELD, sw=2.2))
    p.append(line(660, 200, 660, 250, color=FIELD, sw=2.2))

    # прохідний транзистор (pass FET) — несе КОРИСНИЙ струм, не I_Q
    b, _, _ = textbox(200, 140, "прохідний\nтранзистор", size=11, bold=True,
                      fill="#eafaf1", stroke=FIELD, sw=1.8, pad=9)
    p.append(b)
    p.append(line(240, 140, 530, 140, color=FIELD, sw=2.2))
    p.append(line(530, 140, 530, 200, color=FIELD, sw=2.2))
    p.append(text(370, 132, "корисний струм навантаження", size=9, color=FIELD, italic=True))

    # bandgap — опора
    b, _, _ = textbox(150, 250, "опорна\nнапруга\n(bandgap)", size=10, bold=True,
                      fill="#fff7e6", stroke="#e67e22", sw=1.6, pad=8)
    p.append(b)
    # підсилювач похибки
    b, _, _ = textbox(320, 250, "підсилювач\nпохибки", size=10, bold=True,
                      fill="#f2ecf8", stroke="#8a5fb0", sw=1.6, pad=8)
    p.append(b)
    p.append(arrow(190, 250, 285, 250, color="#8a5fb0", sw=1.6))
    p.append(arrow(320, 225, 210, 165, color="#8a5fb0", sw=1.6))  # керує затвором

    # дільник зворотного звʼязку — окрема завжди-жива гілка на землю
    p.append(line(560, 200, 560, 250, color=NEG, sw=1.8))
    b, _, _ = textbox(560, 285, "дільник\nR1/R2", size=10, bold=True,
                      fill="#eaf0fd", stroke=NEG, sw=1.6, pad=8)
    p.append(b)
    p.append(arrow(520, 260, 500, 260, color=NEG, sw=1.4))
    p.append(line(560, 250, 500, 250, color=NEG, sw=1.4))  # зворотний звʼязок в підсилювач
    p.append(line(500, 250, 355, 250, color=NEG, sw=1.4, dash="4 3"))

    # спільна земля
    p.append(line(150, 300, 560, 300, color=INK, sw=1.6))
    p.append(line(150, 275, 150, 300, color="#e67e22", sw=1.6))
    p.append(line(320, 275, 320, 300, color="#8a5fb0", sw=1.6))
    p.append(line(560, 310, 560, 300, color=NEG, sw=1.6))
    p.append(text(355, 316, "струм у землю (ground current) = сума всіх гілок", size=10, color=INK))

    # права колонка — розклад I_Q
    p.append(text(625, 100, "I_Q — це сума:", size=12, bold=True, color=INK))
    rows = [("bandgap", "~1 мкА", "#e67e22"),
            ("підсилювач", "~1 мкА", "#8a5fb0"),
            ("дільник R1/R2", "0.3–300 мкА", NEG),
            ("(прохідний FET —", "не I_Q)", FIELD)]
    for i, (nm, val, col) in enumerate(rows):
        yy = 135 + i * 46
        b, _, _ = textbox(625, yy, "%s\n%s" % (nm, val), size=10, bold=True,
                          color=col, fill="#ffffff", stroke=col, sw=1.4, pad=7)
        p.append(b)

    render(os.path.join(OUT, "inside-ldo.svg"), W, H, *p,
           title="Куди тече струм спокою всередині LDO")


# ── avg-vs-peak: середнє за цикл вирішує, не пік; і підлога саморозряду ─────────
# Ідея (для детальної): профіль струму в часі — короткі високі піки активності на
# тлі довгого низького сну. Час життя визначає СЕРЕДНЄ (пунктир), а не пік. Нижче
# лежить підлога — саморозряд батареї, нижче за яку оптимізація вже не опускає.

def fig_avg_vs_peak():
    import math
    W, H = 720, 380
    p = []
    ox, oy = 70, 300
    aw, ah = 600, 240

    # осі
    p.append(line(ox, oy, ox + aw, oy, color=LINE, sw=1.5))
    p.append(line(ox, oy - ah, ox, oy, color=LINE, sw=1.5))
    p.append(text(ox + aw / 2, oy + 34, "час →", size=12, color=MUTED))
    p.append('<text x="24" y="%.0f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90, 24, %.0f)">струм (лог-масштаб)</text>'
             % (oy - ah / 2, FONT, MUTED, oy - ah / 2))

    # рівні (лог): сон 10 мкА, активність 120 мА, саморозряд ~2 мкА, середнє ~50 мкА
    lo, hi = 1e-3, 200.0  # мА
    def yv(ma):
        t = (math.log10(max(ma, lo)) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))
        return oy - t * ah
    for ma, lab in [(1e-3, "1 мкА"), (1e-2, "10 мкА"), (1e-1, "0.1 мА"),
                    (1.0, "1 мА"), (10.0, "10 мА"), (100.0, "100 мА")]:
        gy = yv(ma)
        p.append(line(ox, gy, ox + aw, gy, color="#eef1f6", sw=1.0))
        p.append(text(ox - 8, gy + 4, lab, size=9, color=MUTED, anchor="end"))

    # профіль струму: сон — короткі піки активності — сон
    sleep_y = yv(0.010)
    act_y = yv(120.0)
    seg = []
    x = ox
    pat = [(150, sleep_y), (18, act_y), (150, sleep_y), (18, act_y), (170, sleep_y),
           (18, act_y), (60, sleep_y)]
    px, py = ox, sleep_y
    pts = ["%.1f,%.1f" % (px, py)]
    for dw, ty in pat:
        # вертикаль на новий рівень, потім горизонталь
        pts.append("%.1f,%.1f" % (px, ty))
        px += dw
        pts.append("%.1f,%.1f" % (px, ty))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="round"/>' % (" ".join(pts), POS))

    # лінія середнього
    avg_y = yv(0.050)
    p.append(line(ox, avg_y, ox + aw, avg_y, color=NEG, sw=2.0, dash="7 4"))
    b, _, _ = textbox(ox + aw - 70, avg_y - 22, "середнє за цикл\n≈ 50 мкА",
                      size=10, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.5, pad=7)
    p.append(b)

    # підлога саморозряду
    floor_y = yv(0.002)
    p.append(rect(ox, floor_y, aw, oy - floor_y, fill="#f4f4f4", stroke="none", sw=0, rx=0))
    p.append(line(ox, floor_y, ox + aw, floor_y, color=MUTED, sw=1.4, dash="3 3"))
    p.append(text(ox + 8, floor_y + 16, "підлога саморозряду батареї — нижче не опустишся",
                  size=10, color=MUTED, anchor="start"))

    # підписи режимів
    p.append(text(ox + 75, act_y - 10, "пік активності", size=10, color=POS, bold=True))
    p.append(text(ox + 260, sleep_y - 8, "сон (тут пристрій майже весь час)", size=10, color=POS))

    render(os.path.join(OUT, "avg-vs-peak.svg"), W, H, *p,
           title="Життя від батареї визначає середнє, не пік")


# ── leak-map: тихі шляхи витоку на сплячій платі ──────────────────────────────
# Ідея (для детальної): окрім I_Q стабілізатора є «тихіші» витоки, які видно лише
# коли решту прибрано: витік конденсаторів, зворотний струм діода, підтікання
# вимкненого перемикача живлення, дільник для ADC. Кожен підписаний величиною.

def fig_leak_map():
    W, H = 720, 400
    p = []
    # шина 3.3 В зверху, земля знизу
    p.append(line(70, 80, 650, 80, color=POS, sw=2.4))
    p.append(text(60, 84, "3.3 В", size=11, color=POS, bold=True, anchor="end"))
    p.append(line(70, 340, 650, 340, color=INK, sw=2.4))
    p.append(text(60, 344, "GND", size=11, color=INK, bold=True, anchor="end"))

    # чотири «тихі» витоки як вертикальні гілки між шиною і землею
    items = [
        (140, "конденсатори\n(DCL / витік\nдіелектрика)", "0.1–5 мкА", "#8a5fb0"),
        (300, "зворотний\nструм діода\n(reverse-polarity)", "1–50 мкА\n(росте з t°)", "#e67e22"),
        (460, "вимкнений\nперемикач\nживлення", "0.01–1 мкА", FIELD),
        (600, "дільник ADC\nвиміру батареї", "V/(R1+R2)\n~10–100 мкА", NEG),
    ]
    for cx, lab, val, col in items:
        p.append(line(cx, 80, cx, 150, color=col, sw=1.8))
        p.append(line(cx, 270, cx, 340, color=col, sw=1.8))
        b, _, _ = textbox(cx, 190, lab, size=10, bold=True, color=col,
                          fill="#ffffff", stroke=col, sw=1.5, pad=8)
        p.append(b)
        p.append(text(cx, 258, val.split("\n")[0], size=9, color=col, bold=True))
        if "\n" in val:
            p.append(text(cx, 270, val.split("\n")[1], size=9, color=col))

    p.append(text(W / 2, H - 14,
                  "їх видно лише коли power-LED і щедрий I_Q вже прибрано — це «другий шар» бюджету",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "leak-map.svg"), W, H, *p,
           title="Тихі шляхи витоку на сплячій платі")


# ── sleep-order: правильний порядок засинання й пастка back-powering ────────────
# Ідея (для proj): у сон треба заходити в жорсткому порядку — спершу приспати
# периферію по шині, тоді опустити її сигнальні лінії, ТОДІ зняти живлення гілки,
# і аж наостанок заснути. Якщо зняти живлення РАНІШЕ, ніж опустити сигнали, чип
# продовжує «годувати» знеструмлену мікросхему крізь її ж лінії даних —
# back-powering. Показуємо конвеєр кроків і червону стрілку хибного шляху.

def fig_sleep_order():
    W, H = 720, 430
    p = []
    # чотири правильні кроки як стовпці конвеєра
    steps = [
        ("1. приспати\nпериферію", "команда по шині:\nsleep / power-down", FIELD, "#eafaf1"),
        ("2. опустити\nсигнали", "CS, лінії даних →\nHi-Z або 0", NEG, "#eaf0fd"),
        ("3. зняти\nживлення гілки", "load switch OFF:\nгілка знеструмлена", "#e67e22", "#fdf2e9"),
        ("4. заснути", "hold + вибір\nпробудження →\ndeep-sleep", "#8a5fb0", "#f2ecf8"),
    ]
    n = len(steps)
    bw, gap = 128, 24
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    top = 90
    bh = 96
    cxs = []
    for i, (title, sub, col, fill) in enumerate(steps):
        x = x0 + i * (bw + gap)
        cx = x + bw / 2
        cxs.append(cx)
        p.append(rect(x, top, bw, bh, fill=fill, stroke=col, sw=2, rx=8))
        p.append(mtext(cx, top + 26, title, size=12, color=col, bold=True))
        p.append(mtext(cx, top + 58, sub, size=9, color=INK))
        if i < n - 1:
            p.append(arrow(x + bw + 3, top + bh / 2, x + bw + gap - 3, top + bh / 2,
                           color=INK, sw=2.0))

    p.append(text(W / 2, top - 24, "правильний порядок: приспати → опустити → знеструмити → заснути",
                  size=12, color=INK, bold=True))

    # ── пастка: якщо зняти живлення (крок 3) РАНІШЕ, ніж опустити сигнали (крок 2)
    trap_y = top + bh + 96
    p.append(rect(x0, trap_y, total, 116, fill="#fff5f5", stroke=POS, sw=1.6, rx=10))
    p.append(text(W / 2, trap_y + 22, "пастка: зняли живлення, не опустивши сигнали",
                  size=12, color=POS, bold=True))

    # чип ліворуч, знеструмлена мікросхема праворуч, лінія даних під напругою
    chip_x = x0 + 70
    per_x = x0 + total - 90
    my = trap_y + 74
    b, _, _ = textbox(chip_x, my, "ESP32\n(живий)", size=10, bold=True,
                      fill="#eafaf1", stroke=FIELD, sw=1.6, pad=8)
    p.append(b)
    b, _, _ = textbox(per_x, my, "давач\n(живлення знято)", size=10, bold=True,
                      fill="#f0f0f0", stroke=MUTED, sw=1.6, pad=8)
    p.append(b)
    # сигнальна лінія лишилась у «1» — тече струм у знеструмлений давач
    p.append(arrow(chip_x + 52, my - 8, per_x - 66, my - 8, color=POS, sw=2.2))
    p.append(text(W / 2, my - 16, "лінія даних усе ще у «1» → струм тече крізь захисний діод давача",
                  size=9, color=POS, italic=True))
    p.append(text(W / 2, my + 22, "«мертва» мікросхема живиться крізь власні входи — back-powering",
                  size=9, color=POS))

    render(os.path.join(OUT, "sleep-order.svg"), W, H, *p,
           title="Порядок засинання й пастка back-powering")


# ── gpio-domains: два домени пінів у сні — завжди-живий RTC і цифровий, що гасне ─
# Ідея (для proj): у сні кристал ділиться на домени. RTC-домен лишається живим —
# лише його піни можуть будити чип і лише вони тримають рівень самі. Цифрові піни
# знеструмлюються: їхній рівень «відпускається» в сні, ЯКЩО не ввімкнути
# gpio_deep_sleep_hold_en. Звідси дві дії: джерело пробудження — з RTC-домену;
# критичні цифрові рівні — прибити hold, інакше стрибок струму від сну до сну.

def fig_gpio_domains():
    W, H = 720, 400
    p = []
    # кристал
    p.append(rect(50, 60, 620, 300, fill="#fbfcfe", stroke=LINE, sw=1.6, rx=12))

    # RTC-домен — лишається під живленням
    p.append(rect(80, 100, 250, 220, fill="#eafaf1", stroke=FIELD, sw=2, rx=10))
    p.append(text(205, 124, "RTC-домен — ЖИВИЙ у сні", size=12, color=FIELD, bold=True))
    p.append(mtext(205, 150,
                   "живиться завжди-живою гілкою:\nгодинник, лічильник, RTC-піни",
                   size=10, color=INK))
    b, _, _ = textbox(205, 210, "RTC-піни (0,2,4,12,13,14,15,\n25,26,27,32–39)",
                      size=9, bold=True, fill="#ffffff", stroke=FIELD, sw=1.4, pad=8)
    p.append(b)
    b, _, _ = textbox(205, 272, "тільки звідси —\nджерело пробудження\n(ext0/ext1)",
                      size=10, bold=True, color=FIELD, fill="#ffffff", stroke=FIELD, sw=1.5, pad=8)
    p.append(b)

    # цифровий домен — гасне
    p.append(rect(390, 100, 250, 220, fill="#fdecea", stroke=POS, sw=2, rx=10))
    p.append(text(515, 124, "цифровий домен — ГАСНЕ", size=12, color=POS, bold=True))
    p.append(mtext(515, 150,
                   "живлення знято на час сну:\nрівень пінів «відпускається»",
                   size=10, color=INK))
    b, _, _ = textbox(515, 202, "без hold: пін попливе →\nстрибок струму від сну до сну",
                      size=9, bold=True, color=POS, fill="#ffffff", stroke=POS, sw=1.4, pad=8)
    p.append(b)
    b, _, _ = textbox(515, 272, "gpio_deep_sleep_hold_en()\nпримусово тримає рівень",
                      size=10, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.5, pad=8)
    p.append(b)

    # межа доменів
    p.append(line(360, 100, 360, 320, color=MUTED, sw=1.4, dash="5 4"))

    p.append(text(W / 2, H - 14,
                  "будити — з RTC-домену; критичні цифрові рівні — прибити hold, інакше «попливуть» у сні",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "gpio-domains.svg"), W, H, *p,
           title="Два домени пінів у сні: живий RTC і цифровий, що гасне")


# ── charge-integral: заряд за цикл = площа під профілем струму (для math) ───────
# Ідея (для math-вставки): середній струм — це заряд за цикл, поділений на цикл, а
# заряд — це ПЛОЩА під кусково-сталим профілем струму, тобто сума прямокутників
# «струм × час». Показуємо кілька сходинок пробудження різної висоти й ширини на
# тлі довгого низького сну; підпис кожної — її площа (внесок у середнє). Мораль:
# у середнє входить заряд фази (I·t), а не пік чи тривалість поодинці.

def fig_charge_integral():
    import math
    W, H = 720, 420
    p = []
    ox, oy = 70, 320
    aw, ah = 600, 250

    # лог-шкала струму, бо сходинки від 0.014 мА до 110 мА (чотири порядки)
    lo, hi = 1e-2, 200.0      # мА
    def yv(ma):
        t = (math.log10(max(ma, lo)) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))
        return oy - t * ah

    # сітка декад
    for ma, lab in [(1e-2, "10 мкА"), (1e-1, "0.1 мА"), (1.0, "1 мА"),
                    (10.0, "10 мА"), (100.0, "100 мА")]:
        gy = yv(ma)
        p.append(line(ox, gy, ox + aw, gy, color="#eef1f6", sw=1.0))
        p.append(text(ox - 8, gy + 4, lab, size=9, color=MUTED, anchor="end"))

    # осі
    p.append(line(ox, oy, ox + aw, oy, color=LINE, sw=1.5))
    p.append(line(ox, oy - ah, ox, oy, color=LINE, sw=1.5))
    p.append(text(ox + aw / 2, oy + 40, "час за один цикл →", size=12, color=MUTED))
    p.append('<text x="22" y="%.0f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90, 22, %.0f)">струм (лог-масштаб)</text>'
             % (oy - ah / 2, FONT, MUTED, oy - ah / 2))

    sleep_y = yv(0.014)

    # сон — широка низька смуга під усім циклом (заливка до осі)
    p.append(rect(ox, sleep_y, aw, oy - sleep_y, fill="#eafaf1", stroke="none", sw=0, rx=0))
    p.append(line(ox, sleep_y, ox + aw, sleep_y, color=FIELD, sw=1.6))

    # сходинки пробудження зліва (широкі в px для наочності, підпис — реальна площа)
    # (назва, струм мА, px-ширина, колір, підпис-внесок)
    steps = [
        ("розгін\n+ гілка", 18.0, 46, "#e67e22", "3.0 мкА"),
        ("старт\nдавача", 6.0, 70, "#8a5fb0", "4.0 мкА"),
        ("читання", 3.0, 40, NEG, "1.0 мкА"),
        ("радіо", 110.0, 30, POS, "29.3 мкА"),
    ]
    x = ox + 12
    for lab, ma, wpx, col, contrib in steps:
        ty = yv(ma)
        fill = {"#e67e22": "#fdf2e9", "#8a5fb0": "#f2ecf8", NEG: "#eaf0fd",
                POS: "#fdecea"}[col]
        p.append(rect(x, ty, wpx, oy - ty, fill=fill, stroke=col, sw=1.8, rx=2))
        # внесок площі — над стовпчиком
        p.append(text(x + wpx / 2, ty - 7, contrib, size=9, color=col, bold=True))
        p.append(mtext(x + wpx / 2, ty + 16, lab, size=8, color=col, bold=True))
        x += wpx

    # дужка «активні піки» над сходинками
    p.append(line(ox + 12, oy - ah + 24, x, oy - ah + 24, color=MUTED, sw=1.2))
    p.append(text((ox + 12 + x) / 2, oy - ah + 16, "активні сходинки (вузькі, але високі)",
                  size=10, color=MUTED))

    # підпис сну праворуч від сходинок
    p.append(text(x + 130, sleep_y - 8, "сон — низький, але тягнеться на весь цикл (14 мкА)",
                  size=10, color=FIELD, bold=True, anchor="middle"))

    # підсумок середнього
    b, _, _ = textbox(ox + aw - 110, oy - ah + 70,
                      "I_сер = Σ(площа)/T\n= 51.3 мкА", size=11, bold=True,
                      color=INK, fill="#ffffff", stroke=INK, sw=1.5, pad=9)
    p.append(b)

    p.append(text(W / 2, H - 12,
                  "у середнє входить ПЛОЩА фази (струм × час), а не пік чи тривалість поодинці",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "charge-integral.svg"), W, H, *p,
           title="Заряд за цикл — це площа під профілем струму")


# ── regimes-correction: яка поправка домінує залежно від скважності (для math) ──
# Ідея (для math-вставки): та сама формула життя, але для різних D «світиться»
# різний доданок. Мала D (пристрій спить) → вирішує підлога саморозряду. Середня
# D із великими піками → використання ємності + тип стабілізатора. Велика D
# (активний) → ККД перетворення. Три зони вздовж осі D, у кожній підсвічено свою
# поправку. Мораль: оптимізувати «взагалі» не можна — лише під свій профіль.

def fig_regimes_correction():
    W, H = 720, 380
    p = []
    ox, oy = 60, 300
    aw = 600
    top = 70
    band_h = oy - top

    # три зони по осі D
    zones = [
        (0.00, 0.33, "#eaf4fb", "мала D\n(пристрій майже\nзавжди спить)", NEG,
         "вирішує:\nПІДЛОГА\nсаморозряду", "мітка, лічильник,\nгодинник на CR2032"),
        (0.33, 0.66, "#fef9e7", "середня D\n(сон + великі\nпіки радіо)", "#e67e22",
         "вирішують:\nвикористання\nємності + тип\nстабілізатора", "давач із радіо\nна батарейці"),
        (0.66, 1.00, "#fdecea", "велика D\n(пристрій\nпереважно активний)", POS,
         "вирішує:\nККД\nперетворення", "пристрій, що\nпрацює, не спить"),
    ]
    for a, b_, bg, title, col, corr, ex in zones:
        x0 = ox + a * aw
        x1 = ox + b_ * aw
        p.append(rect(x0, top, x1 - x0, band_h, fill=bg, stroke="none", sw=0, rx=0))
        cx = (x0 + x1) / 2
        # назва режиму зверху
        p.append(mtext(cx, top + 26, title, size=11, color=col, bold=True))
        # головна поправка — рамка в центрі
        bb, _, _ = textbox(cx, top + band_h * 0.5, corr, size=11, bold=True,
                           color=col, fill="#ffffff", stroke=col, sw=1.8, pad=9)
        p.append(bb)
        # приклад пристрою знизу
        p.append(mtext(cx, oy - 34, ex, size=9, color=MUTED))

    # роздільники зон
    for a in (0.33, 0.66):
        gx = ox + a * aw
        p.append(line(gx, top, gx, oy, color=MUTED, sw=1.2, dash="5 4"))

    # вісь D зі стрілкою
    p.append(arrow(ox, oy + 18, ox + aw, oy + 18, color=INK, sw=1.8))
    p.append(text(ox, oy + 40, "D → 0  (спить)", size=10, color=MUTED, anchor="start"))
    p.append(text(ox + aw, oy + 40, "D → 1  (активний)", size=10, color=MUTED, anchor="end"))
    p.append(text(ox + aw / 2, oy + 40, "скважність D = частка часу в активній фазі",
                  size=10, color=INK))

    p.append(text(W / 2, H - 12,
                  "одна формула життя — але для кожного пристрою в ній «світиться» свій доданок",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "regimes-correction.svg"), W, H, *p,
           title="Яка поправка вирішальна — залежить від скважності")


if __name__ == "__main__":
    fig_who_sleeps()
    fig_budget()
    fig_iq_stack()
    fig_crossover()
    fig_inside_ldo()
    fig_avg_vs_peak()
    fig_leak_map()
    fig_sleep_order()
    fig_gpio_domains()
    fig_charge_integral()
    fig_regimes_correction()
    print("OK: figures written to", OUT)
