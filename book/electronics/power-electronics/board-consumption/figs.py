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


if __name__ == "__main__":
    fig_who_sleeps()
    fig_budget()
    fig_iq_stack()
    fig_crossover()
    print("OK: figures written to", OUT)
