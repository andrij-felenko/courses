# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Додаткові кольори давачів (поверх палітри svgkit), узгоджені між фігурами.
AMBER = "#d98a00"   # барометр
VIOL  = "#8a5fb0"   # магнітометр


def polyline(pts, color, sw=2.0, opacity=1.0):
    op = ' stroke-opacity="%.2f"' % opacity if opacity < 1 else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (s, color, sw, op))


def cross(cx, cy, r=9, color=POS, sw=2.4):
    return (line(cx - r, cy - r, cx + r, cy + r, color=color, sw=sw) +
            line(cx - r, cy + r, cx + r, cy - r, color=color, sw=sw))


# ─────────────────────────────────────────────────────────────────────────────
# ВСТАВКА hist-draper
# ─────────────────────────────────────────────────────────────────────────────

# sealed-box: герметичний апарат без зовнішніх орієнтирів ─ лишаються лише прилади
def fig_sealed_box():
    W, H = 720, 380
    cx, cy = W / 2, 200
    p = []

    box, bw, bh = textbox(cx, cy, "ГЕРМЕТИЧНИЙ АПАРАТ\nсубмарина · ракета · літак\nлише прилади всередині",
                          size=12, bold=True, pad=18, fill=FILL, stroke=INK, sw=2.2, min_w=240)
    # розташування чотирьох перекреслених орієнтирів по кутах
    spots = [(120, 96, "зорі"), (W - 120, 96, "орієнтир"),
             (120, H - 90, "радіо / GPS"), (W - 120, H - 90, "карта")]
    for sx, sy, lab in spots:
        p.append(line(sx, sy, cx + (-bw / 2 if sx < cx else bw / 2),
                      cy + (-bh / 2 if sy < cy else bh / 2), color="#cfd4dc", sw=1.2, dash="3 4"))
    for sx, sy, lab in spots:
        p.append(circle(sx, sy, 30, fill=BG, stroke=MUTED, sw=1.5))
        p.append(text(sx, sy + 4, lab, size=11, color=MUTED))
        p.append(cross(sx, sy, r=24, color=POS, sw=2.4))
    p.append(box)
    p.append(text(cx, cy + bh / 2 - 16, "лише прилади всередині", size=10, color=FIELD, bold=True))
    p.append(text(cx, H - 24, "ні зір, ні землі, ні радіо — положення треба знати зсередини",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "sealed-box.svg"), W, H, *p,
           title="Знати, де ти, із зачиненими очима")


# gyro-accel: два чуття інерції + ланцюжок інтегрування до положення
def fig_gyro_accel():
    W, H = 760, 400
    p = []

    # гіроскоп — концентричні кільця з віссю
    gx, gy = 150, 150
    p.append(circle(gx, gy, 56, fill=BG, stroke=INK, sw=1.8))
    p.append(circle(gx, gy, 38, fill="#eef4ff", stroke=NEG, sw=1.6))
    p.append(circle(gx, gy, 7, fill=NEG, stroke=NEG, sw=1.6))
    p.append(line(gx - 56, gy, gx + 56, gy, color=INK, sw=1.2))
    p.append(line(gx, gy - 56, gx, gy + 56, color=INK, sw=1.2))
    p.append(text(gx, gy - 70, "ГІРОСКОП", size=13, color=INK, bold=True))
    p.append(text(gx, gy + 80, "ротор тримає напрям", size=10.5, color=MUTED))
    p.append(text(gx, gy + 96, "→ міряє ОБЕРТ", size=10.5, color=MUTED))

    # акселерометр — маса на пружинах у рамці
    ax, ay = 380, 150
    p.append(rect(ax - 58, ay - 45, 116, 90, fill=BG, stroke=INK, sw=1.8, rx=8))
    p.append(rect(ax - 17, ay - 16, 34, 32, fill=AMBER, stroke=INK, sw=1.4, rx=4))
    p.append(text(ax, ay + 6, "m", size=12, color=INK, bold=True))
    p.append(line(ax - 58, ay, ax - 17, ay, color=MUTED, sw=2.0))
    p.append(line(ax + 17, ay, ax + 58, ay, color=MUTED, sw=2.0))
    p.append(text(ax, ay - 70, "АКСЕЛЕРОМЕТР", size=13, color=INK, bold=True))
    p.append(text(ax, ay + 80, "маса на пружинах зміщується", size=10.5, color=MUTED))
    p.append(text(ax, ay + 96, "→ міряє ПРИСКОРЕННЯ", size=10.5, color=MUTED))

    # IMU-блок
    b, bw, bh = textbox(635, 150, "ІНЕРЦІАЛЬНИЙ БЛОК\n(IMU)\nгіро + акселерометр",
                        size=11.5, bold=True, color=NEG, fill="#eef4ff", stroke=NEG, sw=1.7, min_w=170)
    p.append(b)

    # ланцюжок інтегрування
    y = 320
    stepx = 220
    chain = [("прискорення", AMBER), ("швидкість", NEG), ("положення", FIELD)]
    cxs = [180, 180 + stepx, 180 + 2 * stepx]
    for i, (lab, col) in enumerate(chain):
        bb, w2, h2 = textbox(cxs[i], y, lab, size=13, bold=True, color=col, fill=BG, stroke=col, sw=1.8, min_w=150)
        p.append(bb)
        if i > 0:
            p.append(arrow(cxs[i - 1] + w2 / 2, y, cxs[i] - w2 / 2 - 2, y, color=INK, sw=2.0))
            p.append(text((cxs[i - 1] + cxs[i]) / 2, y - 14, "∫ dt", size=12, color=INK, bold=True))
    p.append(text(W / 2, H - 18,
                  "інтегруємо раз — швидкість, ще раз — положення: «розрахунок шляху» (dead reckoning)",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "gyro-accel.svg"), W, H, *p,
           title="Два чуття інерції: гіроскоп і акселерометр")


# spire: переліт через континент, ведений лише інерціальною навігацією
def fig_spire():
    W, H = 760, 380
    p = []

    p.append(rect(90, 130, W - 180, 130, fill="#eef4ff", stroke="#c9d6f0", sw=1.6, rx=20))
    p.append(text(W / 2, 120, "США — від океану до океану (~4200 км)", size=10.5, color=MUTED))

    # маршрут (хвиляста ламана) справа наліво
    route = [(640, 200), (520, 176), (420, 214), (320, 182), (150, 200)]
    p.append(polyline(route, NEG, sw=2.6))
    p.append(text(420, 168, "✈", size=18, color=NEG))

    # старт / фініш
    p.append(circle(640, 200, 8, fill=FIELD, stroke=INK, sw=1.4))
    p.append(text(640, 182, "СТАРТ", size=11, color=FIELD, bold=True))
    p.append(text(640, 228, "Бедфорд, Массачусетс", size=10, color=INK))
    p.append(circle(150, 200, 8, fill=POS, stroke=INK, sw=1.4))
    p.append(text(150, 182, "ФІНІШ", size=11, color=POS, bold=True))
    p.append(text(150, 228, "Лос-Анджелес", size=10, color=INK))

    b, bw, bh = textbox(W / 2, 312,
                        "Пілот вивів на курс — і передав керування системі.\n"
                        "SPIRE (~1.4 т) сама вела апарат майже 13 год.\n"
                        "Док Дрейпер летів на борту, щоб довести: працює.",
                        size=10.5, fill="#eafaf0", stroke=FIELD, sw=1.5, pad=12)
    p.append(b)

    render(os.path.join(OUT, "spire.svg"), W, H, *p,
           title="SPIRE, 1953: переліт наосліп через континент")


# drift-fusion: інерціальна оцінка дрейфує, зовнішній вимір осаджує її назад
def fig_drift_fusion():
    W, H = 760, 360
    ox, oy = 90, 290
    aw, ah = 600, 210
    p = []

    p.append(line(ox, oy - ah, ox, oy, color=INK, sw=1.4))
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.4))
    p.append(text(ox - 8, oy - ah + 6, "похибка", size=10.5, color=MUTED, anchor="end"))
    p.append(text(ox - 8, oy - ah + 20, "оцінки", size=10.5, color=MUTED, anchor="end"))
    p.append(text(ox + aw, oy + 20, "час", size=11, color=MUTED, italic=True, anchor="end"))

    # істина — нульова похибка
    p.append(line(ox, oy, ox + aw, oy, color=FIELD, sw=2.2))
    p.append(text(ox + aw, oy - 6, "істина (нульова похибка)", size=10, color=FIELD, bold=True, anchor="end"))

    # пилка дрейфу: повзе вгору, виправлення кидають назад до осі
    saw = [(ox, oy)]
    n = 5
    seg = aw / n
    high = ah * 0.62
    for i in range(n):
        x0 = ox + i * seg
        saw.append((x0 + seg, oy - high))      # дрейф угору
        if i < n - 1:
            saw.append((x0 + seg, oy - high * 0.12))  # осадження вниз (виправлення)
    p.append(polyline(saw, POS, sw=2.4))
    p.append(text(ox + 60, oy - high - 8, "інерціальна оцінка дрейфує", size=10.5, color=POS, bold=True, anchor="start"))

    # мітки виправлень
    for i in range(1, n):
        xx = ox + i * seg
        p.append(circle(xx, oy - high * 0.12, 5, fill=NEG, stroke=INK, sw=1.2))
    lx = ox + aw - 150
    p.append(circle(lx, oy - ah + 10, 5, fill=NEG, stroke=INK, sw=1.2))
    p.append(text(lx + 12, oy - ah + 14, "виправлення (зорі / GPS / баро)", size=10, color=NEG, anchor="start"))

    p.append(text(W / 2, H - 16,
                  "інерція точна миттєво, та її похибка накопичується; зовнішній вимір рідкий, зате не дрейфує",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "drift-fusion.svg"), W, H, *p,
           title="Дрейф і виправлення: чому одного давача замало")


# ─────────────────────────────────────────────────────────────────────────────
# СТАТТЯ sensor-insufficiency
# ─────────────────────────────────────────────────────────────────────────────

# witnesses: чотири картки давачів, кожен ✓ сила / ✗ вада
def fig_witnesses():
    W, H = 760, 410
    p = []
    cards = [
        (60, 80, NEG, "IMU (гіро + акселерометр)",
         "швидкий, миттєвий, самодостатній", "дрейфує — похибка росте щосекунди"),
        (390, 80, FIELD, "GNSS (GPS)",
         "абсолютна позиція, без дрейфу", "повільний, шумний, пропадає"),
        (60, 245, AMBER, "Барометр",
         "висота будь-де, дешево", "шумить і «пливе» з погодою"),
        (390, 245, VIOL, "Магнітометр",
         "курс — де північ", "кривлять мотори, струми, залізо"),
    ]
    cw, ch = 310, 140
    for x, y, col, name, good, bad in cards:
        p.append(rect(x, y, cw, ch, fill=BG, stroke=col, sw=2.0, rx=12))
        p.append(text(x + 16, y + 28, name, size=13.5, color=col, bold=True, anchor="start"))
        p.append(line(x + 16, y + 40, x + cw - 16, y + 40, color="#e5e7eb", sw=1.0))
        p.append(text(x + 20, y + 74, "✓", size=15, color=FIELD, bold=True, anchor="start"))
        p.append(text(x + 44, y + 74, good, size=11.5, color=INK, anchor="start"))
        p.append(text(x + 20, y + 110, "✗", size=15, color=POS, bold=True, anchor="start"))
        p.append(text(x + 44, y + 110, bad, size=11.5, color=INK, anchor="start"))
    p.append(text(W / 2, H - 18,
                  "бездоганного свідка немає: покладешся на одного — успадкуєш усі його вади",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "witnesses.svg"), W, H, *p,
           title="Кожен давач — свідок зі своєю вадою")


# complementary: дзеркальні смужки IMU / GPS — миттєво vs надовго
def fig_complementary():
    W, H = 760, 360
    p = []
    colL, colR = 300, 430          # лівий старт смуг, повна ширина пари смуг
    bw = colR / 2 - 16             # ширина однієї смуги
    gap = 28
    p.append(text(colL + bw / 2, 90, "МИТТЄВО (зараз)", size=12, color=MUTED, bold=True))
    p.append(text(colL + bw + gap + bw / 2, 90, "НАДОВГО (без дрейфу)", size=12, color=MUTED, bold=True))

    def bars(y, name, col, left_frac, right_frac):
        out = [text(110, y + 6, name, size=14, color=col, bold=True, anchor="start")]
        # ліва смуга (миттєво)
        out.append(rect(colL, y - 20, bw, 40, fill="#f1f1f3", stroke="#e5e7eb", sw=1.0))
        out.append(rect(colL, y - 20, bw * left_frac, 40, fill=col, stroke="none", sw=1.0))
        out.append(text(colL + bw * left_frac + (8 if left_frac < 0.6 else -8),
                        y + 5, "сильно" if left_frac > 0.6 else "слабко",
                        size=11.5, color=(BG if left_frac > 0.6 else MUTED),
                        bold=True, anchor="start" if left_frac < 0.6 else "end"))
        # права смуга (надовго)
        rx = colL + bw + gap
        out.append(rect(rx, y - 20, bw, 40, fill="#f1f1f3", stroke="#e5e7eb", sw=1.0))
        out.append(rect(rx, y - 20, bw * right_frac, 40, fill=col, stroke="none", sw=1.0))
        out.append(text(rx + bw * right_frac + (8 if right_frac < 0.6 else -8),
                        y + 5, "сильно" if right_frac > 0.6 else "слабко",
                        size=11.5, color=(BG if right_frac > 0.6 else MUTED),
                        bold=True, anchor="start" if right_frac < 0.6 else "end"))
        return out

    p += bars(150, "IMU", NEG, 0.92, 0.18)
    p += bars(230, "GNSS / GPS", FIELD, 0.25, 0.95)
    p.append(text(W / 2, 300, "дзеркало: де IMU сильний — GPS слабкий, і навпаки",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, H - 16,
                  "поєднання бере від кожного сильний бік: швидку реакцію IMU й стабільну прив'язку GPS",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "complementary.svg"), W, H, *p,
           title="Слабкість одного — сила іншого")


# altitude: баро шумить, GPS східчаста й відстає, інтеграл дрейфує, поєднання гладке
def fig_altitude():
    import random
    random.seed(7)
    W, H = 760, 400
    ox, oy = 80, 330
    aw, ah = 600, 240
    p = []
    p.append(rect(ox, oy - ah, aw, ah, fill="#f8fafc", stroke="#e5e7eb", sw=1.0, rx=6))
    p.append(text(ox - 8, oy - ah + 4, "висота", size=10.5, color=MUTED, anchor="end"))
    p.append(text(ox + aw - 6, oy + 18, "час →", size=11, color=MUTED, anchor="end"))

    span = 100
    sx = aw / span

    def X(i):
        return ox + i * sx

    def Y(frac):                      # frac 0..1 від низу області
        return oy - frac * (ah - 20) - 8

    # справжній набір висоти — пологий підйом
    def truth(i):
        t = i / span
        return 0.18 + 0.62 * (1 - math.exp(-2.4 * t))

    # баро: істина + шум
    baro = [(X(i), Y(truth(i) + random.uniform(-0.05, 0.05))) for i in range(span + 1)]
    p.append(polyline(baro, AMBER, sw=1.3, opacity=0.75))
    # GPS-висота: грубі сходинки, відстає
    gps = []
    for i in range(span + 1):
        step = (i // 14) * 14
        gps.append((X(i), Y(truth(max(0, step - 4)) )))
    p.append(polyline(gps, NEG, sw=1.5, opacity=0.7))
    # інтеграл акселерометра: гладкий, але дрейфує геть угору
    accel = [(X(i), Y(truth(i) + 0.45 * (i / span) ** 1.7)) for i in range(span + 1)]
    p.append(polyline(accel, POS, sw=1.5, opacity=0.8))
    # поєднання: гладке, точне — тримається істини
    fused = [(X(i), Y(truth(i))) for i in range(span + 1)]
    p.append(polyline(fused, FIELD, sw=3.0))

    # легенда
    leg = [(AMBER, 2, "баро (шум)"), (NEG, 2, "GPS-висота (відстає, грубо)"),
           (POS, 2, "акселерометр (дрейф)"), (FIELD, 3, "ПОЄДНАННЯ (точно й гладко)")]
    ly = oy - ah + 16
    for col, sw, lab in leg:
        p.append(line(ox + 16, ly, ox + 40, ly, color=col, sw=sw))
        p.append(text(ox + 48, ly + 4, lab, size=10, color=INK,
                      bold=(col == FIELD), anchor="start"))
        ly += 20

    p.append(text(W / 2, H - 14,
                  "кожен слід окремо шумить, відстає або тікає; зведені разом — гладка, точна висота",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "altitude.svg"), W, H, *p,
           title="Висота: жоден сам не годиться, разом — точно")


# fusion-concept: чотири давачі → вузол поєднання → стан апарата
def fig_fusion_concept():
    W, H = 760, 360
    p = []
    sensors = [("IMU", NEG, 110), ("GPS", FIELD, 170), ("барометр", AMBER, 230), ("магнітометр", VIOL, 290)]
    hubx, huby = 400, 200
    for lab, col, y in sensors:
        b, bw, bh = textbox(150, y, lab, size=13, bold=True, color=col, fill=BG, stroke=col, sw=1.7, min_w=150)
        p.append(line(150 + bw / 2, y, hubx - 95, huby, color=col, sw=1.6, dash="1 0"))
        p.append(b)

    hub, hw, hh = textbox(hubx, huby, "ПОЄДНАННЯ\n(оцінювач стану,\nнапр. фільтр Калмана)",
                          size=12, bold=True, fill="#eef4ff", stroke=INK, sw=2.2, min_w=180)
    p.append(hub)

    st, sw2, sh = textbox(640, huby, "СТАН АПАРАТА\n• положення\n• швидкість\n• орієнтація",
                          size=12, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=2.0, min_w=180)
    p.append(arrow(hubx + hw / 2, huby, 640 - sw2 / 2 - 2, huby, color=INK, sw=2.4))
    p.append(st)

    p.append(text(W / 2, H - 18,
                  "одна оцінка, якій можна довіряти, — складена з багатьох, жодному з яких не вірять наодинці",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "fusion-concept.svg"), W, H, *p,
           title="Поєднання: багато недосконалих → одна довірена оцінка")


if __name__ == "__main__":
    fig_sealed_box()
    fig_gyro_accel()
    fig_spire()
    fig_drift_fusion()
    fig_witnesses()
    fig_complementary()
    fig_altitude()
    fig_fusion_concept()
    print("OK: figures written to", OUT)
