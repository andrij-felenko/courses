# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: де живе позиція — поверхня vs глибина ─────────────────────────
def fig_where_position():
    W, H = 760, 430
    parts = []

    # межа води
    water_y = 150
    parts.append(rect(0, water_y, W, H - water_y, fill="#eaf2f8", stroke="none", rx=0))
    parts.append(line(0, water_y, W, water_y, color=NEG, sw=2))
    parts.append(text(12, water_y - 8, "повітря", size=13, color=MUTED, anchor="start"))
    parts.append(text(12, water_y + 20, "вода", size=13, color=NEG, anchor="start", italic=True))

    # супутник
    sat_x, sat_y = 150, 60
    parts.append(circle(sat_x, sat_y, 16, fill="#fff6d8", stroke=POS, sw=2))
    parts.append(text(sat_x, sat_y + 5, "GPS", size=12, bold=True, color=POS))

    # човен на поверхні — сигнал доходить
    boat_x = 200
    parts.append(rect(boat_x - 34, water_y - 24, 68, 24, fill=FILL, stroke=INK, sw=1.6))
    parts.append(text(boat_x, water_y - 8, "човен", size=12, bold=True))
    parts.append(arrow(sat_x + 8, sat_y + 14, boat_x - 6, water_y - 26, color=FIELD, sw=2))
    parts.append(text(boat_x + 96, water_y - 46, "радіо доходить", size=12, color=FIELD, italic=True, anchor="middle"))

    # підводний апарат — сигнал гасне
    sub_x, sub_y = 470, 320
    parts.append(rect(sub_x - 40, sub_y - 16, 80, 32, fill=FILL, stroke=INK, sw=1.6, rx=14))
    parts.append(text(sub_x, sub_y + 5, "підводний", size=12, bold=True))

    # промінь, що згасає у воді (пунктир слабне)
    parts.append(line(sat_x + 6, sat_y + 14, 300, water_y - 4, color=POS, sw=2, dash="1 0"))
    parts.append(line(300, water_y + 4, 360, water_y + 55, color=POS, sw=2, dash="6 6"))
    parts.append(line(360, water_y + 55, 405, water_y + 110, color=MUTED, sw=1.4, dash="2 8"))
    parts.append(text(330, water_y + 40, "×", size=26, bold=True, color=POS, anchor="middle"))
    parts.append(text(300, water_y + 92, "радіо гасне за\nсантиметри", size=12, color=POS, anchor="middle"))

    # маяки на дні (LBL) — акустика
    for bx in (150, 300):
        parts.append(circle(bx, H - 22, 9, fill="#fdecea", stroke=POS, sw=2))
    parts.append(text(225, H - 6, "акустичні маяки на дні", size=11, color=MUTED, anchor="middle"))
    parts.append(line(sub_x - 30, sub_y + 12, 160, H - 30, color=NEG, sw=1.5, dash="4 4"))
    parts.append(line(sub_x - 30, sub_y + 14, 305, H - 30, color=NEG, sw=1.5, dash="4 4"))
    parts.append(text(sub_x + 70, sub_y + 40, "звук доходить\n(~1500 м/с)", size=12, color=NEG, anchor="middle", italic=True))

    render(os.path.join(IMG, 'where-position.svg'), W, H, *parts,
           title="Позицію знадвору дає GPS на поверхні — але не під водою")


# ── Фігура 2: спільний контур, різні шари ───────────────────────────────────
def fig_shared_loop():
    W, H = 780, 340
    parts = []

    boxes = [
        ("Давачі", "IMU · компас\nGPS / акустика\nтиск / DVL", 70, NEG),
        ("Оцінювач", "фільтр\nпередбач–виправ\nпоза й швидкість", 265, FIELD),
        ("Регулятори", "каскад\nкурс → швидкість\n→ тяга", 460, INK),
        ("Приводи", "мотори-рушії\nкермо / диф. тяга", 650, POS),
    ]
    y0 = 90
    bw, bh = 150, 130
    for (t, body, cx, col) in boxes:
        parts.append(rect(cx - bw / 2, y0, bw, bh, fill=FILL, stroke=col, sw=2))
        parts.append(text(cx, y0 + 26, t, size=15, bold=True, color=col))
        parts.append(mtext(cx, y0 + 52, body.split("\n"), size=12, color=INK))

    # стрілки вперед
    for i in range(len(boxes) - 1):
        x1 = boxes[i][2] + bw / 2
        x2 = boxes[i + 1][2] - bw / 2
        parts.append(arrow(x1 + 2, y0 + bh / 2, x2 - 2, y0 + bh / 2, color=INK, sw=2))

    # зворотний зв'язок (світ)
    parts.append(line(boxes[3][2], y0 + bh, boxes[3][2], y0 + bh + 40, color=MUTED, sw=1.6))
    parts.append(line(boxes[3][2], y0 + bh + 40, boxes[0][2], y0 + bh + 40, color=MUTED, sw=1.6))
    parts.append(arrow(boxes[0][2], y0 + bh + 40, boxes[0][2], y0 + bh + 2, color=MUTED, sw=1.6))
    parts.append(text((boxes[0][2] + boxes[3][2]) / 2, y0 + bh + 58,
                       "світ рухає тіло → давачі бачать наслідок", size=12, color=MUTED, italic=True))

    parts.append(text(W / 2, y0 + bh + 92,
                      "той самий контур, що й у дрона чи ровера — змінюється лише вміст крайніх шарів",
                      size=12, color=INK, bold=True))

    render(os.path.join(IMG, 'shared-loop.svg'), W, H, *parts,
           title="Один контур на всі тіла: давач → оцінка → регулятор → привід")


# ── Фігура 3: інерція проти опору (крок газу) ───────────────────────────────
def fig_drag_vs_inertia():
    W, H = 720, 320
    parts = []
    import math

    # осі
    ox, oy = 90, 250
    ax_w, ax_h = 560, 190
    parts.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=1.6))
    parts.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=1.6))
    parts.append(text(ox + ax_w, oy + 22, "час", size=12, color=MUTED, anchor="end"))
    parts.append(text(ox - 12, oy - ax_h + 6, "швидкість", size=12, color=MUTED, anchor="end"))

    # ступінь газу
    step_y = oy - 150
    parts.append(line(ox, oy, ox + 60, oy, color=MUTED, sw=1.6, dash="4 4"))
    parts.append(line(ox + 60, oy, ox + 60, step_y, color=MUTED, sw=1.6, dash="4 4"))
    parts.append(line(ox + 60, step_y, ox + ax_w - 10, step_y, color=MUTED, sw=1.6, dash="4 4"))
    parts.append(text(ox + 300, step_y - 10, "команда тяги (сходинка)", size=11, color=MUTED, anchor="middle"))

    # крива з опором: 1 - e^{-t/τ} → усталюється (човен)
    pts_drag = []
    for k in range(0, 121):
        t = k / 120.0
        vx = ox + 60 + t * (ax_w - 70)
        v = 1 - math.exp(-t * 4.2)
        vy = oy - v * 150
        pts_drag.append("%.1f,%.1f" % (vx, vy))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (" ".join(pts_drag), NEG))
    parts.append(text(ox + ax_w - 10, step_y + 20, "опір: швидкість\nусталюється", size=12, color=NEG, anchor="end"))

    # крива без опору (інерція): майже пряма розгонка вгору й за межі
    pts_in = []
    for k in range(0, 90):
        t = k / 120.0
        vx = ox + 60 + t * (ax_w - 70)
        v = t * 3.4
        vy = oy - v * 150
        if vy < oy - ax_h:
            break
        pts_in.append("%.1f,%.1f" % (vx, vy))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="7 5"/>'
                 % (" ".join(pts_in), POS))
    parts.append(text(ox + 250, oy - ax_h + 20, "без опору (у повітрі):\nрозганяється й далі", size=12, color=POS, anchor="middle"))

    render(os.path.join(IMG, 'drag-vs-inertia.svg'), W, H, *parts,
           title="Вода гальмує сама: стала тяга → стала швидкість, не нескінченний розгін")


# ── Фігура 4: баланс сил по вертикалі — що тримає інтеграл ───────────────────
def fig_buoyancy_balance():
    W, H = 720, 380
    parts = []

    # три апарати: тоне / спливає / майже нейтральний-з-дрібним-залишком.
    # довжини стрілок ВІДБИВАЮТЬ дисбаланс: у важчого вага довша, у легшого —
    # виштовх; у майже нейтрального обидві майже рівні (різниця крихітна).
    body_y = 170
    cols = [
        # cx, підпис, вага(px), виштовх(px), підпис-наслідку, колір, y-наслідку
        (150, "важчий за воду",  74, 44, "вага > виштовх\n→ тоне",      POS,   body_y + 128),
        (360, "легший за воду",  44, 74, "виштовх > вага\n→ спливає",    NEG,   body_y - 104),
        (575, "майже нейтральний", 60, 52, "різниця дрібна,\nале НЕ нуль", FIELD, body_y + 116),
    ]
    for (cx, capt, wlen, blen, force_txt, col, ry) in cols:
        parts.append(rect(cx - 44, body_y - 20, 88, 40, fill=FILL, stroke=INK, sw=1.8, rx=12))
        parts.append(text(cx, body_y - 30, capt, size=12, color=INK, bold=True))
        # вага вниз (від низу корпусу)
        parts.append(arrow(cx - 17, body_y + 20, cx - 17, body_y + 20 + wlen, color=POS, sw=2.4))
        parts.append(text(cx - 17, body_y + 20 + wlen + 14, "вага", size=11, color=POS))
        # виштовх угору (від верху корпусу)
        parts.append(arrow(cx + 17, body_y - 20, cx + 17, body_y - 20 - blen, color=NEG, sw=2.4))
        parts.append(text(cx + 17, body_y - 20 - blen - 6, "виштовх", size=11, color=NEG))
        # наслідок
        parts.append(mtext(cx, ry, force_txt.split("\n"), size=12, color=col, bold=True))

    parts.append(text(W / 2, H - 44,
                      "ідеально нуль не виставити: лишається СТАЛА сила — її й компенсує інтеграл",
                      size=13, color=INK, bold=True))
    parts.append(text(W / 2, H - 22,
                      "П дає нуль тяги при нульовій помилці; без І апарат просів би, поки помилка знову не зросте",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'buoyancy-balance.svg'), W, H, *parts,
           title="Чому утриманню глибини потрібна інтегральна складова")


# ── Фігура 5: насичення рушіїв → перекид без антивіндапу (глибина в часі) ────
def fig_saturation_antiwindup():
    W, H = 810, 380
    parts = []
    import math

    ox, oy = 90, 300
    ax_w, ax_h = 590, 240
    parts.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=1.6))
    parts.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=1.6))
    parts.append(text(ox + ax_w, oy + 22, "час", size=12, color=MUTED, anchor="end"))
    parts.append(text(ox - 8, oy - ax_h + 2, "глибина", size=12, color=MUTED, anchor="start"))

    # цільова глибина (горизонталь посередині)
    tgt_y = oy - 120
    parts.append(line(ox, tgt_y, ox + ax_w - 6, tgt_y, color=INK, sw=1.4, dash="5 5"))
    parts.append(text(ox + ax_w - 8, tgt_y - 8, "задана глибина", size=11, color=INK, anchor="end"))
    parts.append(text(ox + 12, oy - 12, "мілко", size=10, color=MUTED, anchor="start"))
    parts.append(text(ox + 12, oy - ax_h + 16, "глибоко", size=10, color=MUTED, anchor="start"))

    # фаза збурення: апарат затягло вгору (до поверхні) — рушії уперлися в межу
    dist_x = ox + 190
    parts.append(rect(ox + 40, oy - ax_h + 26, dist_x - (ox + 40), 40, fill="#fdecea", stroke="none", rx=6))
    parts.append(mtext(ox + 118, oy - ax_h + 44, ["течія/хвиля тягне вгору,", "рушії — на межі (насичення)"],
                       size=11, color=POS))

    # з антивіндапом: чисте повернення до заданої, без перельоту вниз
    pts_good = []
    for k in range(0, 201):
        t = k / 200.0
        vx = dist_x + t * (ox + ax_w - dist_x - 6)
        # старт мілко (мала глибина, тобто високо), плавно осідає на ціль
        depth = 0.30 + 0.70 * (1 - math.exp(-t * 3.4))
        vy = oy - depth * 120
        pts_good.append("%.1f,%.1f" % (vx, vy))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts_good), FIELD))

    # без антивіндапу: накопичений інтеграл проштовхує ГЛИБШЕ за ціль → перекид, тоді назад
    pts_bad = []
    for k in range(0, 201):
        t = k / 200.0
        vx = dist_x + t * (ox + ax_w - dist_x - 6)
        depth = 0.30 + 0.70 * (1 - math.exp(-t * 3.4)) + 0.55 * math.sin(t * 3.1) * math.exp(-t * 1.4)
        vy = oy - depth * 120
        pts_bad.append("%.1f,%.1f" % (vx, vy))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="7 5"/>'
                 % (" ".join(pts_bad), POS))

    # межа збурення
    parts.append(line(dist_x, oy - ax_h + 20, dist_x, oy, color=MUTED, sw=1.2, dash="2 4"))

    # підписи кривих
    parts.append(text(ox + 520, tgt_y - 40, "з антивіндапом:\nосідає на ціль без перельоту",
                      size=11, color=FIELD, anchor="middle"))
    parts.append(text(ox + 470, oy - 30, "без антивіндапу: інтеграл накрутився за\nнасичення → перекид глибше цілі, тоді хитання",
                      size=11, color=POS, anchor="middle"))

    render(os.path.join(IMG, 'saturation-antiwindup.svg'), W, H, *parts,
           title="Насичення вертикальних рушіїв: без антивіндапу — перекид глибини")


# ── Фігура 6: LBL vs USBL — дві дзеркальні геометрії (для hist-вставки) ──────
def fig_lbl_vs_usbl_history():
    W, H = 780, 400
    parts = []

    mid = W / 2
    parts.append(line(mid, 44, mid, H - 12, color=MUTED, sw=1.2, dash="3 6"))

    # заголовки панелей
    parts.append(text(W / 4, 62, "LBL — наддовга база", size=15, bold=True, color=NEG))
    parts.append(text(3 * W / 4, 62, "USBL — надкоротка база", size=15, bold=True, color=POS))

    surf_y = 96
    floor_y = H - 40

    # ── ЛІВА панель: LBL ────────────────────────────────────────────────
    Lx = W / 4
    parts.append(rect(20, surf_y, mid - 40, floor_y - surf_y, fill="#eaf2f8", stroke="none", rx=0))
    parts.append(line(20, surf_y, mid - 20, surf_y, color=MUTED, sw=1.6))
    parts.append(line(20, floor_y, mid - 20, floor_y, color=INK, sw=2))
    # апарат унизу
    sub_lx, sub_ly = Lx, floor_y - 96
    # три маяки на дні
    beacons = [(Lx - 128, floor_y), (Lx - 4, floor_y), (Lx + 118, floor_y)]
    for (bx, by) in beacons:
        parts.append(line(sub_lx, sub_ly + 8, bx, by - 12, color=NEG, sw=1.4, dash="5 4"))
    for (bx, by) in beacons:
        parts.append(circle(bx, by - 6, 8, fill="#eaf0fd", stroke=NEG, sw=2))
    parts.append(rect(sub_lx - 30, sub_ly - 13, 60, 26, fill=FILL, stroke=INK, sw=1.6, rx=11))
    parts.append(text(sub_lx, sub_ly + 4, "апарат", size=11, bold=True))
    parts.append(text(Lx, floor_y + 22, "маяки на дні (відомі місця)", size=11, color=NEG, anchor="middle"))
    parts.append(text(Lx, sub_ly - 24, "міряю ВІДСТАНЬ до кожного\n→ трилатерація", size=11, color=INK, anchor="middle"))

    # ── ПРАВА панель: USBL ──────────────────────────────────────────────
    Rx = 3 * W / 4
    parts.append(rect(mid + 20, surf_y, mid - 40, floor_y - surf_y, fill="#eaf2f8", stroke="none", rx=0))
    parts.append(line(mid + 20, surf_y, W - 20, surf_y, color=MUTED, sw=1.6))
    parts.append(line(mid + 20, floor_y, W - 20, floor_y, color=INK, sw=2))
    # маяк на апараті внизу
    beacon_rx, beacon_ry = Rx + 66, floor_y - 66
    # судно на поверхні з решіткою
    ship_x = Rx - 30
    # промінь від решітки до маяка (відстань + кут)
    parts.append(arrow(ship_x, surf_y + 12, beacon_rx - 20, beacon_ry - 6, color=POS, sw=1.8))
    parts.append(rect(ship_x - 40, surf_y - 22, 80, 22, fill=FILL, stroke=INK, sw=1.6))
    parts.append(text(ship_x, surf_y - 7, "судно", size=11, bold=True))
    # тісна решітка гідрофонів (кілька точок близько)
    for dx in (-9, -3, 3, 9):
        parts.append(circle(ship_x + dx, surf_y + 8, 3.2, fill="#fdecea", stroke=POS, sw=1.6))
    parts.append(text(ship_x - 66, surf_y + 2, "тісна\nрешітка", size=10, color=POS, anchor="middle"))
    # маяк-апарат
    parts.append(rect(beacon_rx - 30, beacon_ry - 12, 60, 24, fill=FILL, stroke=INK, sw=1.6, rx=10))
    parts.append(text(beacon_rx, beacon_ry + 4, "апарат", size=11, bold=True))
    parts.append(circle(beacon_rx - 21, beacon_ry, 4, fill="#fdecea", stroke=POS, sw=1.6))
    parts.append(text(Rx + 4, (surf_y + beacon_ry) / 2 + 4, "відстань\n+ НАПРЯМОК\n(фаза на решітці)", size=11, color=POS, anchor="middle"))

    parts.append(text(W / 2, H - 8,
                      "усе перевернуто: LBL — база на дні (сотні м); USBL — база на судні (сантиметри)",
                      size=12, color=INK, bold=True))

    render(os.path.join(IMG, 'lbl-vs-usbl-history.svg'), W, H, *parts,
           title="Дві дзеркальні відповіді: маяки на дні проти решітки на судні")


if __name__ == "__main__":
    fig_where_position()
    fig_shared_loop()
    fig_drag_vs_inertia()
    fig_buoyancy_balance()
    fig_saturation_antiwindup()
    fig_lbl_vs_usbl_history()
    print("figures written to", IMG)
