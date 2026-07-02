# -*- coding: utf-8 -*-
"""Фігури для теми companion-power-thermal (Енергія й тепло бортового комп'ютера).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_two_problems():
    """Дві задачі живлення бортового комп'ютера: завести ватти всередину (ліворуч,
    батарея→перетворювач→стійка шина 5 В) і вивести марні ватти назовні (праворуч,
    кристал→радіатор→повітря). Одна течія енергії, два вузьких горла."""
    W, H = 780, 400
    frags = []

    # ── ліва половина: подача енергії ──
    bat, bw, bh = textbox(105, 150, ["батарея", "3S–6S"], size=13,
                          fill="#eef0f4", stroke=LINE)
    frags.append(bat)
    conv, cw, ch = textbox(255, 150, ["імпульсний", "перетворювач"], size=13,
                          fill="#eef7f0", stroke=FIELD)
    frags.append(conv)
    frags.append(arrow(148, 150, 210, 150))
    # стійка шина 5 В
    rail, rw, rh = textbox(255, 250, ["стійка шина", "5.0 В"], size=13,
                          fill="#fdecea", stroke=POS, bold=True)
    frags.append(rail)
    frags.append(arrow(255, 178, 255, 224))
    frags.append(text(200, 62, "ЗАВЕСТИ ВАТТИ", size=15, color=INK, bold=True))
    frags.append(text(200, 84, "з батареї — в чисту, тверду шину", size=12, color=MUTED))

    # плата-споживач у центрі
    board, pbw, pbh = textbox(390, 250, ["бортовий", "комп'ютер"], size=13,
                             fill="#eaf0fd", stroke=NEG, bold=True)
    frags.append(board)
    frags.append(arrow(300, 250, 348, 250))

    # ── права половина: відведення тепла ──
    frags.append(text(590, 62, "ВИВЕСТИ ВАТТИ", size=15, color=INK, bold=True))
    frags.append(text(590, 84, "марне тепло з кристала — в повітря", size=12, color=MUTED))
    die, dbw, dbh = textbox(500, 150, ["кристал", "SoC"], size=13,
                           fill="#fdecea", stroke=POS)
    frags.append(die)
    sink, sbw, sbh = textbox(650, 150, ["радіатор", "+ вентилятор"], size=13,
                            fill="#eef0f4", stroke=LINE)
    frags.append(sink)
    frags.append(arrow(543, 150, 604, 150))
    air, abw, abh = textbox(650, 250, ["повітря", "довкола"], size=13,
                           fill="#eef7f0", stroke=FIELD)
    frags.append(air)
    frags.append(arrow(650, 178, 650, 224))
    frags.append(arrow(432, 232, 476, 172))  # плата гріється → кристал

    # підпис-нитка внизу
    frags.append(text(W/2, 340, "Та сама енергія: скільки ватт увійшло — стільки тепла треба вивести.",
                     size=13, color=INK))
    frags.append(text(W/2, 360, "Обидва горла вузькі, і кожне окремо здатне звалити плату.",
                     size=12, color=MUTED))

    render(os.path.join(OUT, "two-problems.svg"), W, H, *frags,
           title="Живлення бортового комп'ютера — це дві задачі, не одна")


def fig_linear_vs_switch():
    """Чому лінійний стабілізатор не годиться для амперів: із 4S (≈14.8 В) у 5 В
    він мусить спалити різницю. Стовпчики втрати: лінійний ≈29 Вт проти
    імпульсного ≈2 Вт при однаковій корисній потужності 15 Вт."""
    W, H = 760, 440
    L, R = 110, 640
    T, B = 80, 350
    Pmax = 34.0  # Вт по осі

    def by(p): return B - (p / Pmax) * (B - T)

    frags = []
    # осі
    frags.append(line(L, T, L, B, color=INK, sw=2))
    frags.append(line(L, B, R, B, color=INK, sw=2))
    for p in range(0, int(Pmax) + 1, 5):
        y = by(p)
        frags.append(line(L - 5, y, L, y, color=INK, sw=1.2))
        frags.append(text(L - 12, y + 4, "%d" % p, size=12, color=MUTED, anchor="end"))
    frags.append(text(L - 60, (T + B) / 2, "потужність, Вт", size=13, color=INK))

    # спільна корисна потужність, яку бере плата
    Puse = 15.0
    # лінійний: Vin 14.8 → Vout 5, I = 3 A → корисних 15 Вт, спалено (14.8−5)·3 = 29.4 Вт
    Ilin = 3.0
    Plin_loss = (14.8 - 5.0) * Ilin
    # імпульсний: КПД ~88% → втрата ≈ Puse·(1/0.88 − 1) ≈ 2.0 Вт
    Psw_loss = Puse * (1.0 / 0.88 - 1.0)

    bw = 120
    # стовпчик 1 — лінійний
    x1 = 220
    frags.append(rect(x1 - bw/2, by(Puse), bw, B - by(Puse), fill="#eaf0fd", stroke=NEG))
    frags.append(rect(x1 - bw/2, by(Puse + Plin_loss), bw, by(Puse) - by(Puse + Plin_loss),
                     fill="#fdecea", stroke=POS))
    frags.append(text(x1, by(Puse) + (B - by(Puse))/2 + 4, "корисних 15 Вт", size=11, color=NEG))
    frags.append(text(x1, by(Puse + Plin_loss/2) + 4, "спалено 29 Вт", size=12, color=POS, bold=True))
    frags.append(text(x1, B + 22, "лінійний (LDO)", size=13, color=INK, bold=True))
    frags.append(text(x1, B + 40, "з 14.8 В у 5 В  ·  ККД 34%", size=11, color=MUTED))

    # стовпчик 2 — імпульсний
    x2 = 500
    frags.append(rect(x2 - bw/2, by(Puse), bw, B - by(Puse), fill="#eaf0fd", stroke=NEG))
    frags.append(rect(x2 - bw/2, by(Puse + Psw_loss), bw, by(Puse) - by(Puse + Psw_loss),
                     fill="#fdecea", stroke=POS))
    frags.append(text(x2, by(Puse) + (B - by(Puse))/2 + 4, "корисних 15 Вт", size=11, color=NEG))
    frags.append(text(x2, by(Puse + Psw_loss) - 10, "спалено ~2 Вт", size=12, color=POS, bold=True))
    frags.append(text(x2, B + 22, "імпульсний (buck)", size=13, color=INK, bold=True))
    frags.append(text(x2, B + 40, "з 14.8 В у 5 В  ·  ККД ~88%", size=11, color=MUTED))

    # виноска
    box, _, _ = textbox((x1 + x2)/2, by(30),
                       ["однакова плата,", "однакові 15 Вт корисних —", "різниця лише в марному теплі"],
                       size=12, fill="#eef7f0", stroke=FIELD)
    frags.append(box)

    render(os.path.join(OUT, "linear-vs-switch.svg"), W, H, *frags,
           title="Ті самі 15 Вт у плату: лінійний спалює 29 Вт, buck — 2 Вт")


def fig_thermal_ohm():
    """Тепловий закон Ома: потужність тече крізь ланцюжок теплових опорів
    (кристал→корпус→радіатор→повітря), як струм крізь резистори, і на кожному
    «спадає» перепад температури. Аналогія й де вона ламається."""
    W, H = 800, 380
    frags = []

    frags.append(text(W/2, 60, "P (Вт) тече, як струм; θ (°C/Вт) — як опір; ΔT (°C) — як спад напруги",
                     size=13, color=MUTED))

    # ланцюжок вузлів (температури) і опорів (θ) між ними
    ys = 170
    xs = [110, 320, 530, 710]
    Tnodes = ["кристал\nTj", "корпус\nTc", "радіатор\nTs", "повітря\nTa"]
    for x, lbl in zip(xs, Tnodes):
        b, _, _ = textbox(x, ys, lbl.split("\n"), size=13, fill="#fdecea"
                          if x == xs[0] else ("#eef7f0" if x == xs[-1] else "#eef0f4"),
                          stroke=POS if x == xs[0] else (FIELD if x == xs[-1] else LINE))
        frags.append(b)

    # θ між вузлами як «резистори» (стрілки з підписом)
    thetas = ["θJC", "θCS", "θSA"]
    for i in range(3):
        xa, xb = xs[i] + 46, xs[i+1] - 46
        frags.append(arrow(xa, ys, xb, ys))
        frags.append(text((xa+xb)/2, ys - 14, thetas[i], size=13, color=INK, bold=True))

    # джерело тепла зліва
    frags.append(text(110, ys - 60, "P = I²·Rds(on)", size=12, color=POS))
    frags.append(arrow(110, ys - 46, 110, ys - 24))

    # формула-підсумок
    box, _, _ = textbox(W/2, 300,
                       ["Tj = Ta + P · (θJC + θCS + θSA)",
                        "перегрів кристала = потужність × сумарний тепловий опір"],
                       size=14, fill="#eef7f0", stroke=FIELD, bold=True)
    frags.append(box)

    # де ламається
    frags.append(text(W/2, 350, "Аналогія точна в усталеному стані; на кидках потужності вмикається теплова ЄМНІСТЬ маси — вона згладжує пік.",
                     size=11, color=MUTED))

    render(os.path.join(OUT, "thermal-ohm.svg"), W, H, *frags,
           title="Тепловий закон Ома: тепло тече крізь ланцюжок опорів")


def fig_rail_sag():
    """Стійкість шини 5 В у часі: кидок струму (плата рвонула на інференс) просаджує
    напругу; кволе живлення падає нижче 4.63 В → плата бачить недовольтаж і скидає
    частоту; тверда шина + буферна ємність тримають рівень."""
    W, H = 780, 430
    L, R = 90, 700
    T, B = 70, 300
    tmax = 10.0     # умовні одиниці часу
    Vlo, Vhi = 4.2, 5.4

    def px(t): return L + (t / tmax) * (R - L)
    def py(v): return B - ((v - Vlo) / (Vhi - Vlo)) * (B - T)

    frags = []
    frags.append(line(L, T, L, B, color=INK, sw=2))
    frags.append(line(L, B, R, B, color=INK, sw=2))
    for v in [4.4, 4.63, 4.8, 5.0, 5.2]:
        y = py(v)
        frags.append(line(L - 5, y, L, y, color=INK, sw=1.1))
        frags.append(text(L - 10, y + 4, "%.2f" % v, size=11, color=MUTED, anchor="end"))
    frags.append(text(L - 58, (T + B) / 2, "напруга шини, В", size=13, color=INK))
    frags.append(text((L + R) / 2, B + 58, "час →", size=12, color=INK))

    # поріг недовольтажу 4.63 В
    yth = py(4.63)
    frags.append(line(L, yth, R, yth, color=POS, sw=1.6, dash="6,4"))
    frags.append(text(R - 4, yth - 8, "поріг 4.63 В — плата кричить «мало живлення»", size=11,
                     color=POS, anchor="end"))

    # момент кидка струму
    tstep = 4.0
    frags.append(line(px(tstep), T, px(tstep), B, color=MUTED, sw=1.2, dash="3,4"))
    frags.append(text(px(tstep), T - 6, "кидок струму (рвонув інференс)", size=11, color=MUTED))

    # крива «кволе живлення» — глибоко просідає й лишається під порогом
    # (кволе джерело не має запасу струму, тож напруга не відновлюється).
    weak = []
    for k in range(121):
        t = tmax * k / 120
        if t < tstep:
            v = 5.05
        else:
            dt = t - tstep
            # швидкий провал до ~4.45 В і мляве часткове відновлення лише до ~4.55 В
            v = 4.55 - 0.55 * (2.718 ** (-dt * 1.6))
        weak.append("%.1f,%.1f" % (px(t), py(v)))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
                 'stroke-dasharray="5,3"/>' % (" ".join(weak), NEG))
    frags.append(text(px(8.4), py(4.44), "кволе живлення", size=12, color=NEG, bold=True, anchor="middle"))

    # крива «тверда шина + буфер» — просідає ледь-ледь, лишається над порогом
    stiff = []
    for k in range(121):
        t = tmax * k / 120
        if t < tstep:
            v = 5.05
        else:
            dt = t - tstep
            v = 5.05 - 0.18 * (2.718 ** (-dt * 1.2))
        stiff.append("%.1f,%.1f" % (px(t), py(v)))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                 % (" ".join(stiff), FIELD))
    frags.append(text(px(7.4), py(5.12), "тверда шина + буфер", size=12, color=FIELD, bold=True))

    # виноска
    box, _, _ = textbox(px(2.0), py(5.28),
                       ["стійкість = мала",
                        "просадка під кидком"],
                       size=11, fill="#eef7f0", stroke=FIELD)
    frags.append(box)

    render(os.path.join(OUT, "rail-sag.svg"), W, H, *frags,
           title="Кидок струму просаджує шину: кволе живлення падає під поріг")


def fig_bec_block():
    """Блок-схема BEC-модуля зсередини: вхід із польотної батареї → вхідна ємність →
    ядро-buck (ключ + котушка + діод/нижній FET) → вихідна ємність → тверді 5 В.
    Праворуч — чотири числа паспорта, кожне «висить» на своєму порту."""
    W, H = 820, 430
    frags = []

    ys = 150  # рядок силового тракту
    # вхід
    vin, _, _ = textbox(95, ys, ["ВХІД", "з батареї"], size=12,
                        fill="#eef0f4", stroke=LINE)
    frags.append(vin)
    # вхідна ємність
    cin, _, _ = textbox(215, ys, ["вхідна", "ємність"], size=12,
                        fill="#eef7f0", stroke=FIELD)
    frags.append(cin)
    frags.append(arrow(138, ys, 172, ys))
    # ядро buck
    core, cw, ch = textbox(390, ys, ["ЯДРО — buck", "ключ · котушка · діод/FET"], size=12,
                          fill="#fdf6e3", stroke=POS, bold=True)
    frags.append(core)
    frags.append(arrow(258, ys, 306, ys))
    # вихідна ємність
    cout, _, _ = textbox(575, ys, ["вихідна", "ємність"], size=12,
                        fill="#eef7f0", stroke=FIELD)
    frags.append(cout)
    frags.append(arrow(474, ys, 528, ys))
    # вихід 5 В
    vout, _, _ = textbox(695, ys, ["ВИХІД", "5.0 В"], size=12,
                        fill="#fdecea", stroke=POS, bold=True)
    frags.append(vout)
    frags.append(arrow(622, ys, 656, ys))

    # спільна земля знизу — суцільна лінія від входу до виходу
    gy = ys + 70
    frags.append(line(95, gy, 695, gy, color=NEG, sw=2))
    frags.append(text(395, gy + 18, "спільна земля (−) наскрізна — вхід і вихід ділять GND",
                     size=11, color=NEG))
    for x in (95, 695):
        frags.append(line(x, ys + 24, x, gy, color=NEG, sw=1.4))

    # заголовок-нитка
    frags.append(text(W/2, 62, "BEC/UBEC — це понижувальний імпульсний перетворювач у готовому корпусі",
                     size=13, color=MUTED))

    # чотири числа паспорта — картки праворуч, кожна «дивиться» на свій вузол
    px0 = W/2
    specs = [
        ("вхід: діапазон напруги / S-число пакета", "напр. 2S–6S ≈ 6–26 В", 250),
        ("вихід: НОМІНАЛЬНИЙ і ПІКОВИЙ струм", "напр. 3 А тривало / 5 А коротко", 290),
        ("ККД (скільки взяв — стільки й віддав)", "напр. 85–92 %", 330),
        ("пульсації виходу (розмах на 5 В)", "напр. < 50 мВ p-p", 370),
    ]
    for lbl, val, yy in specs:
        frags.append(text(70, yy, "• " + lbl, size=12, color=INK, anchor="start", bold=True))
        frags.append(text(560, yy, val, size=12, color=FIELD, anchor="start"))

    render(os.path.join(OUT, "bec-block.svg"), W, H, *frags,
           title="Що в паспорті BEC-модуля — і де це в схемі")


def fig_bec_wiring():
    """Типове підключення BEC: та сама польотна батарея → BEC → КОРОТКИЙ ТОВСТИЙ провід →
    плата-споживач, з буферною ємністю прямо біля плати й спільною землею.
    Показано дві граблі: тонкий/довгий провід (просадка) і де саме шум лізе в шину."""
    W, H = 820, 400
    frags = []

    ys = 150
    # батарея
    bat, _, _ = textbox(105, ys, ["польотна", "батарея"], size=12,
                       fill="#eef0f4", stroke=LINE)
    frags.append(bat)
    # BEC
    bec, _, _ = textbox(280, ys, ["BEC / UBEC", "→ тверді 5 В"], size=12,
                       fill="#fdf6e3", stroke=POS, bold=True)
    frags.append(bec)
    frags.append(arrow(150, ys, 230, ys))
    frags.append(text(190, ys - 14, "11–25 В", size=11, color=MUTED))

    # короткий товстий провід до плати
    frags.append(arrow(332, ys, 470, ys, sw=4))  # товста стрілка = товстий провід
    frags.append(text(400, ys - 16, "КОРОТКИЙ ТОВСТИЙ", size=11, color=FIELD, bold=True))
    frags.append(text(400, ys - 2, "провід 5 В", size=11, color=MUTED))

    # плата-споживач
    board, bw, bh = textbox(560, ys, ["бортовий", "комп'ютер"], size=12,
                           fill="#eaf0fd", stroke=NEG, bold=True)
    frags.append(board)

    # буферна ємність прямо біля плати
    buf, _, _ = textbox(560, ys + 95, ["буферна ємність", "тут, впритул до плати"], size=11,
                       fill="#eef7f0", stroke=FIELD)
    frags.append(buf)
    frags.append(arrow(560, ys + 62, 560, ys + 30))
    frags.append(text(560, ys + 132, "підхоплює кидок першою, поки BEC наздоганяє",
                     size=10, color=MUTED))

    # спільна земля
    gy = ys + 40
    frags.append(line(105, gy, 560, gy, color=NEG, sw=1.8))
    frags.append(text(300, gy + 15, "спільна земля — усі мінуси в одну точку",
                     size=11, color=NEG))

    # ── граблі: тонкий довгий провід ──
    frags.append(text(400, 300, "⚠ те саме, але провід тонкий і довгий:",
                     size=12, color=POS, anchor="start", bold=True))
    frags.append(text(400, 320, "на 3 А він губить десяті вольта — шина просідає ще до плати",
                     size=11, color=INK, anchor="start"))
    frags.append(text(400, 340, "(тонка стрілка = тонкий провід = зайвий опір послідовно)",
                     size=10, color=MUTED, anchor="start"))
    frags.append(arrow(140, 320, 360, 320, sw=1))  # тонка стрілка-контраст

    render(os.path.join(OUT, "bec-wiring.svg"), W, H, *frags,
           title="Підключення BEC: коротким товстим проводом, буфер біля плати")


if __name__ == "__main__":
    fig_two_problems()
    fig_linear_vs_switch()
    fig_thermal_ohm()
    fig_rail_sag()
    fig_bec_block()
    fig_bec_wiring()
    print("ok figs")
