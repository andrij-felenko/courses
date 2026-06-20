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


if __name__ == "__main__":
    fig_pressure_altitude()
    fig_mems_pressure()
    fig_error_budget()
    fig_altitude_hold()
    print("OK: figures written to", IMG)
