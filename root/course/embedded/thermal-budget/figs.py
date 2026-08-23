# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── budget-chain: тепловий бюджет як драбина температур ────────────────────────
# Ідея: бюджет — це додавання Rθ уздовж шляху й накопичення температури знизу
# вгору. Зліва вісь температури, що росте від повітря (низ) до кристала (верх);
# кожна ланка Rθ підіймає рівень на P·Rθ. Видно, де найбільший стрибок (часто
# «корпус→повітря») і що Tj — це сума всіх піднять плюс довкілля.
def fig_budget_chain():
    W, H = 760, 460
    p = []
    # вісь температури (ліворуч)
    ax = 120
    base_y = 410          # рівень повітря (T_amb)
    top_y = 70
    p.append(line(ax, top_y - 10, ax, base_y, color=LINE, sw=1.6))
    p.append(text(ax, top_y - 22, "T, °C", size=12, color=MUTED))

    # рівні температури (накопичення знизу вгору)
    P = 5.0               # Вт
    amb = 40.0
    # ланки: (підпис ланки, Rθ, підпис рівня-вузла зверху)
    links = [
        ("Rθ радіатор→повітря\n= 4.0 °C/Вт", 4.0, "радіатор"),
        ("Rθ паста\n= 0.5 °C/Вт", 0.5, "корпус"),
        ("Rθ корпус→кристал (θJC)\n= 1.5 °C/Вт", 1.5, "кристал (Tj)"),
    ]
    # перерахунок у температури від низу
    temps = [amb]
    for _, r, _ in links:
        temps.append(temps[-1] + P * r)
    Tj = temps[-1]
    # масштаб: amb..Tj лягає на base_y..top_y
    span = Tj - amb
    def yfor(t):
        return base_y - (t - amb) / span * (base_y - top_y)

    # рівень повітря
    p.append(line(ax, base_y, W - 40, base_y, color=NEG, sw=1.6, dash="6 4"))
    b, _, _ = textbox(W - 120, base_y, "повітря  %.0f °C" % amb, size=11, color=NEG,
                      fill="#eaf0fd", stroke=NEG, sw=1.4, pad=7)
    p.append(b)

    xL = ax + 30          # ліва межа стовпця ланок
    xR = W - 230          # права межа
    colw = xR - xL
    # малюємо ланки знизу вгору як кольорові смуги між рівнями
    fills = ["#fdf2e9", "#fef9e7", "#fdecea"]
    strokes = ["#e67e22", "#caa700", POS]
    for i, (lab, r, node) in enumerate(links):
        y0 = yfor(temps[i])
        y1 = yfor(temps[i + 1])
        p.append(rect(xL, y1, colw, y0 - y1, fill=fills[i], stroke=strokes[i], sw=1.6, rx=4))
        # підпис ланки всередині смуги
        p.append(mtext(xL + colw / 2, (y0 + y1) / 2 + 4, lab, size=10, color=INK))
        # стрілка-вимір ΔT збоку
        dx = xR + 14
        p.append(line(dx, y0, dx, y1, color=strokes[i], sw=1.4))
        p.append(line(dx - 4, y0, dx + 4, y0, color=strokes[i], sw=1.4))
        p.append(line(dx - 4, y1, dx + 4, y1, color=strokes[i], sw=1.4))
        b, _, _ = textbox(dx + 52, (y0 + y1) / 2, "+%.0f°" % (P * r), size=10, bold=True,
                          color=strokes[i], fill="#ffffff", stroke=strokes[i], sw=1.2, pad=5)
        p.append(b)
        # підпис вузла-рівня
        p.append(text(ax - 8, y1 + 4, "%.0f°" % temps[i + 1], size=10, color=MUTED, anchor="end"))

    # кристал угорі — підсумок Tj
    p.append(line(ax, yfor(Tj), W - 40, yfor(Tj), color=POS, sw=1.8))
    b, _, _ = textbox(W - 120, yfor(Tj), "кристал  %.0f °C" % Tj, size=11, bold=True, color=POS,
                      fill="#fdecea", stroke=POS, sw=1.5, pad=7)
    p.append(b)

    # формула збоку
    b, _, _ = textbox(xL + colw / 2, base_y + 32,
                      "Tj = T_повітря + P·(Rθ₁+Rθ₂+Rθ₃) = 40 + 5·6 = 70 °C",
                      size=11, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.5, pad=8)
    p.append(b)

    render(os.path.join(OUT, "budget-chain.svg"), W, H, *p,
           title="Тепловий бюджет: температура накопичується вздовж шляху")


# ── heatsink-decision: один чип, два шляхи — з радіатором і без ─────────────────
# Ідея: бюджет — це не «гаряче чи ні», а «Tj нижче чи вище за Tj(max)». Дві
# колонки з тією самою P: голий корпус заганяє кристал за межу (червона лінія
# Tj_max), радіатор повертає під межу. Видно запас (margin) як стрілку.
def fig_heatsink_decision():
    W, H = 720, 440
    p = []
    base_y = 380
    top_y = 70
    amb = 40.0
    P = 5.0
    Tjmax = 150.0
    # масштаб T: amb..230 на base..top
    Tlo, Thi = amb, 230.0
    def yfor(t):
        return base_y - (t - Tlo) / (Thi - Tlo) * (base_y - top_y)

    # вісь
    p.append(line(70, top_y - 10, 70, base_y, color=LINE, sw=1.6))
    for t in (40, 80, 120, 150, 190, 230):
        gy = yfor(t)
        p.append(line(66, gy, 70, gy, color=LINE, sw=1.0))
        p.append(text(60, gy + 4, "%d" % t, size=10, color=MUTED, anchor="end"))
    p.append(text(70, top_y - 22, "Tj, °C", size=12, color=MUTED))

    # лінія межі Tj(max)
    p.append(line(70, yfor(Tjmax), W - 30, yfor(Tjmax), color=POS, sw=1.8, dash="7 4"))
    b, _, _ = textbox(W - 95, yfor(Tjmax), "Tj(max) 150 °C", size=11, bold=True, color=POS,
                      fill="#fdecea", stroke=POS, sw=1.5, pad=6)
    p.append(b)

    # дві колонки
    cols = [230, 460]
    cw = 130
    cases = [
        ("Без радіатора", 30.0, POS, "#fdecea"),      # Rθja ≈ 30 → Tj=40+150=190
        ("З радіатором",   6.0, FIELD, "#eafaf1"),     # Rθ сумарн ≈ 6 → Tj=40+30=70
    ]
    for cx, (lab, rja, col, fill) in zip(cols, cases):
        Tj = amb + P * rja
        ytop = yfor(Tj)
        # стовпчик від повітря до Tj
        p.append(rect(cx - cw / 2, ytop, cw, yfor(amb) - ytop, fill=fill, stroke=col, sw=2, rx=5))
        p.append(text(cx, ytop - 10, "Tj ≈ %.0f °C" % Tj, size=12, bold=True, color=col))
        p.append(mtext(cx, base_y + 22, "%s\nRθ(ja) = %.0f °C/Вт" % (lab, rja), size=11, color=INK))
        # позначка перевищення/запасу
        if Tj > Tjmax:
            b, _, _ = textbox(cx, (ytop + yfor(Tjmax)) / 2, "+%.0f° ЗА МЕЖЕЮ" % (Tj - Tjmax),
                              size=10, bold=True, color=POS, fill="#ffffff", stroke=POS, sw=1.4, pad=6)
            p.append(b)
        else:
            # стрілка запасу до межі
            dx = cx + cw / 2 + 16
            p.append(line(dx, ytop, dx, yfor(Tjmax), color=FIELD, sw=1.4))
            p.append(line(dx - 4, ytop, dx + 4, ytop, color=FIELD, sw=1.4))
            p.append(line(dx - 4, yfor(Tjmax), dx + 4, yfor(Tjmax), color=FIELD, sw=1.4))
            b, _, _ = textbox(dx + 40, (ytop + yfor(Tjmax)) / 2, "запас\n%.0f°" % (Tjmax - Tj),
                              size=10, bold=True, color=FIELD, fill="#f0fff4", stroke=FIELD, sw=1.3, pad=6)
            p.append(b)

    # рівень повітря
    p.append(line(70, yfor(amb), W - 30, yfor(amb), color=NEG, sw=1.4, dash="5 4"))
    p.append(text(W - 60, yfor(amb) - 6, "повітря 40 °C", size=10, color=NEG, anchor="end"))

    p.append(text(W / 2, H - 12,
                  "та сама P = 5 Вт: бюджет вирішує не «гаряче?», а «Tj під межею чи за нею?»",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "heatsink-decision.svg"), W, H, *p,
           title="Один чип, та сама потужність — два шляхи")


# ── derating: безпечна потужність падає з температурою повітря ──────────────────
# Ідея: бюджет залежить від довкілля. Гранична P, яку можна розсіяти, лінійно
# спадає від (T_amb=25, P_max) до (T_amb=Tj_max, 0): P = (Tj_max − T_amb)/Rθ.
# Робоча точка має лежати ПІД лінією. Дві лінії — кращий і гірший Rθ.
def fig_derating():
    W, H = 720, 430
    p = []
    ox, oy = 80, 350
    aw, ah = 590, 290
    Tjmax = 150.0
    Tlo, Thi = 0.0, Tjmax      # вісь X: T_amb
    Pmax = 10.0                # верх осі P
    def xfor(t):
        return ox + (t - Tlo) / (Thi - Tlo) * aw
    def yfor(pw):
        return oy - pw / Pmax * ah

    # осі
    p.append(line(ox, oy, ox + aw, oy, color=LINE, sw=1.6))
    p.append(line(ox, oy - ah, ox, oy, color=LINE, sw=1.6))
    for t in (0, 25, 50, 75, 100, 125, 150):
        gx = xfor(t)
        p.append(line(gx, oy, gx, oy + 5, color=LINE, sw=1.0))
        p.append(text(gx, oy + 18, "%d" % t, size=10, color=MUTED))
    for pw in (0, 2, 4, 6, 8, 10):
        gy = yfor(pw)
        p.append(line(ox - 5, gy, ox, gy, color=LINE, sw=1.0))
        p.append(text(ox - 9, gy + 4, "%d" % pw, size=10, color=MUTED, anchor="end"))
    p.append(text(ox + aw / 2, oy + 40, "температура повітря T_довк, °C", size=12, color=MUTED))
    p.append('<text x="24" y="%.0f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90, 24, %.0f)">безпечна P, Вт</text>'
             % (oy - ah / 2, FONT, MUTED, oy - ah / 2))

    # дві лінії дерейтингу: P = (Tjmax − Tamb)/Rθ, обрізані зверху Pmax
    def deline(rja, color, fill, name, namex):
        # точка, де P досягає Pmax: Tamb = Tjmax − Pmax·Rθ
        t_full = Tjmax - Pmax * rja
        pts = []
        if t_full > Tlo:
            pts.append((xfor(Tlo), yfor(Pmax)))
            pts.append((xfor(t_full), yfor(Pmax)))
        else:
            pts.append((xfor(Tlo), yfor((Tjmax - Tlo) / rja)))
        pts.append((xfor(Tjmax), yfor(0)))
        poly = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
        out = ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
               'stroke-linejoin="round"/>' % (poly, color))
        return out, t_full

    g1, _ = deline(8.0, POS, "#fdecea", "Rθ = 8", 0)    # гірший радіатор
    g2, _ = deline(20.0, "#e67e22", "#fdf2e9", "Rθ = 20", 0)  # без радіатора
    p.append(g2)
    p.append(g1)

    # підписи ліній
    b, _, _ = textbox(xfor(95), yfor(7.4), "добрий радіатор\nRθ = 8 °C/Вт", size=10, bold=True,
                      color=POS, fill="#fdecea", stroke=POS, sw=1.4, pad=6)
    p.append(b)
    b, _, _ = textbox(xfor(55), yfor(2.6), "без радіатора\nRθ = 20 °C/Вт", size=10, bold=True,
                      color="#e67e22", fill="#fdf2e9", stroke="#e67e22", sw=1.4, pad=6)
    p.append(b)

    # робоча точка (P=5 Вт, T=40) — під обома? перевіримо: для Rθ8 межа при 40 → (150-40)/8=13.75 ОК;
    # для Rθ20 межа при 40 → (150-40)/20=5.5 → 5 Вт ледь під лінією
    wx, wy = xfor(40), yfor(5.0)
    p.append(circle(wx, wy, 6, fill="#fff", stroke=FIELD, sw=2.4))
    b, _, _ = textbox(wx + 86, wy + 30, "робоча точка\n5 Вт @ 40 °C", size=10, bold=True,
                      color=FIELD, fill="#f0fff4", stroke=FIELD, sw=1.4, pad=6)
    p.append(b)
    # зона під лінією Rθ8 = безпечно
    p.append(text(xfor(28), yfor(1.2), "нижче лінії — безпечно", size=10, color=FIELD))

    render(os.path.join(OUT, "derating.svg"), W, H, *p,
           title="Дерейтинг: гаряче повітря з'їдає бюджет потужності")


if __name__ == "__main__":
    fig_budget_chain()
    fig_heatsink_decision()
    fig_derating()
    print("OK: figures written to", OUT)
