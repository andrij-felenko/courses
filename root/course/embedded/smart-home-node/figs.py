# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def three_layers():
    W, H = 720, 430
    p = []
    cx = W / 2

    # три шари як горизонтальні смуги
    lw = 360
    lx = cx - lw / 2
    band_h = 74
    gap = 26
    y0 = 70

    # верхній: звіт (мережа) — крихкий
    yb = y0
    p.append(rect(lx, yb, lw, band_h, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(text(cx, yb + 26, "Звіт і команди  (MQTT)", size=16, color=NEG, bold=True))
    p.append(text(cx, yb + 50, "раз на секунди · терпить обриви", size=12, color=MUTED))

    # серединний: рішення
    ym = y0 + band_h + gap
    p.append(rect(lx, ym, lw, band_h, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(cx, ym + 26, "Рішення  (автономне правило)", size=16, color=FIELD, bold=True))
    p.append(text(cx, ym + 50, "локально · мілісекунди · серце вузла", size=12, color=MUTED))

    # нижній: знімання
    ys = y0 + 2 * (band_h + gap)
    p.append(rect(lx, ys, lw, band_h, fill=FILL, stroke=INK, sw=2))
    p.append(text(cx, ys + 26, "Знімання  (давач · виконавець)", size=16, color=INK, bold=True))
    p.append(text(cx, ys + 50, "торкається світу · найнадійніше", size=12, color=MUTED))

    # підпис «усередині плати» біля двох нижніх
    p.append(line(lx - 18, ym - 6, lx - 18, ys + band_h + 6, color=FIELD, sw=2))
    p.append(text(lx - 26, (ym + ys + band_h) / 2, "усередині плати", size=12,
                  color=FIELD, anchor="end"))

    # брокер угорі + лінія до верхнього шару з розривом (пунктир = обрив)
    bx, by = cx, 50
    p.append(text(cx, by, "☁ брокер / мережа", size=13, color=NEG, anchor="middle"))
    p.append(line(cx, by + 6, cx, yb, color=NEG, sw=2, dash="6 5"))
    # значок розриву
    ymid = (by + 6 + yb) / 2
    p.append(text(cx + 56, ymid + 4, "обрив", size=11, color=POS, anchor="start"))
    p.append(line(cx - 8, ymid, cx + 8, ymid, color=POS, sw=2.5))

    # напрям залежності: верхній спирається на нижні (стрілка вниз збоку)
    ax = lx + lw + 22
    p.append(arrow(ax, yb + band_h - 6, ax, ys + 6, color=MUTED, sw=1.8))
    p.append(text(ax + 10, (yb + ys) / 2, "спирається", size=11, color=MUTED, anchor="start"))
    p.append(text(ax + 10, (yb + ys) / 2 + 16, "на нижні", size=11, color=MUTED, anchor="start"))

    # нижні працюють, коли верх відрізаний
    p.append(text(cx, ys + band_h + 34,
                  "обрив угорі не спиняє нижні два шари", size=13, color=FIELD, bold=True))

    render(os.path.join(IMG, 'three-layers.svg'), W, H, *p,
           title="Вузол як три шари з різним темпом і критичністю")


def node_topics():
    W, H = 720, 440
    p = []
    cx = W / 2
    spine = 235                     # рівень вузол — брокер — дім

    # вузол зліва, дім (панель) справа
    nx = 92
    dx = W - 92
    p.append(circle(nx, spine, 46, fill="#eafaf0", stroke=FIELD, sw=2.5))
    p.append(mtext(nx, spine - 4, ["ВУЗОЛ", "термостат"], size=13, color=FIELD, bold=True))
    p.append(circle(dx, spine, 46, fill="#eaf0fd", stroke=NEG, sw=2.5))
    p.append(mtext(dx, spine - 4, ["ДІМ", "панель"], size=13, color=NEG, bold=True))

    # брокер у центрі спини
    bb, bw, bh = textbox(cx, spine, "брокер", size=14, bold=True, fill="#fff7e6",
                         stroke="#b8860b", min_w=104)
    half = bw / 2

    # --- STATE (угорі): вузол -> брокер -> дім, retain ---
    y_state = 96
    p.append(text(cx, y_state - 18, "СТАН → (retain)", size=13, color=FIELD, bold=True))
    p.append(fitbox(cx - 120, y_state - 4, 240, 30, ".../state", size=13,
                    fill="#eafaf0", stroke=FIELD))
    p.append(arrow(nx + 20, spine - 42, cx - 120, y_state + 24, color=FIELD, sw=2))
    p.append(arrow(cx + 120, y_state + 24, dx - 20, spine - 42, color=FIELD, sw=2))

    # --- SET (унизу-центр): дім -> брокер -> вузол ---
    y_set = 356
    p.append(fitbox(cx - 120, y_set - 15, 240, 30, ".../set", size=13,
                    fill="#eaf0fd", stroke=NEG))
    p.append(text(cx, y_set + 34, "← КОМАНДА (дім наказує)", size=13, color=NEG, bold=True))
    p.append(arrow(dx - 20, spine + 42, cx + 120, y_set - 4, color=NEG, sw=2))
    p.append(arrow(cx - 120, y_set - 4, nx + 20, spine + 42, color=NEG, sw=2))

    # --- STATUS (заповіт): короткі теги обабіч брокера на спині ---
    p.append(fitbox(nx + 58, spine - 15, 118, 30, "online", size=12,
                    fill="#fdecea", stroke=POS))
    p.append(fitbox(dx - 176, spine - 15, 118, 30, ".../status", size=12,
                    fill="#fdecea", stroke=POS))
    p.append(line(nx + 46, spine, nx + 58, spine, color=POS, sw=2))
    p.append(line(cx - half, spine, nx + 176, spine, color=POS, sw=2, dash="2 3"))
    p.append(line(cx + half, spine, dx - 176, spine, color=POS, sw=2, dash="2 3"))
    p.append(line(dx - 58, spine, dx - 46, spine, color=POS, sw=2))
    p.append(text(cx, spine + 70, "ПРИСУТНІСТЬ: заповіт напише offline, якщо вузол зникне",
                  size=12, color=POS, bold=True))

    # брокер — поверх, щоб пунктир статусу не перекривав напис
    p.append(bb)

    render(os.path.join(IMG, 'node-topics.svg'), W, H, *p,
           title="Три топіки одного вузла: стан · команда · присутність")


def hysteresis_band():
    # Температура пиляє біля порога; реле перемикається лише на двох краях
    # мертвої зони, а не на кожному дотику до setpoint. Внизу — стан реле.
    W, H = 720, 430
    ox, oy = 96, 250            # початок осей верхнього графіка (t,°C)
    aw = 520                    # ширина осі часу
    p = []

    y_set = 130                 # рівень setpoint на екрані
    dpix = 42                   # піврозмах зони на екрані (Δ)
    y_on = y_set + dpix         # нижній поріг: set − Δ (нижче — увімкнути)
    y_off = y_set - dpix        # верхній поріг: set + Δ (вище — вимкнути)

    # три горизонтальні рівні
    p.append(line(ox, y_set, ox + aw, y_set, color=MUTED, sw=1.3, dash="5 5"))
    p.append(text(ox + aw + 6, y_set + 4, "поріг", size=12, color=MUTED, anchor="start"))
    p.append(line(ox, y_off, ox + aw, y_off, color=NEG, sw=1.6, dash="3 4"))
    p.append(text(ox + aw + 6, y_off + 4, "set + Δ", size=12, color=NEG, anchor="start"))
    p.append(line(ox, y_on, ox + aw, y_on, color=POS, sw=1.6, dash="3 4"))
    p.append(text(ox + aw + 6, y_on + 4, "set − Δ", size=12, color=POS, anchor="start"))

    # затінена мертва зона
    p.append(rect(ox, y_off, aw, y_on - y_off, fill="#f4f6f8", stroke="none", sw=0, rx=0))
    p.append(text(ox + 8, y_set - dpix / 2, "мертва зона 2Δ", size=11, color=MUTED, anchor="start"))

    # пиляста температура: гріємо (вгору) до верхнього порога, стигне (вниз) до нижнього.
    # Малюємо трикутну хвилю між y_on та y_off.
    import math as _m
    xs = []
    seg = aw / 6.0
    # послідовність вершин: стартуємо трохи вище нижнього порога, гріючись
    pts = [(ox, y_on - 6)]
    x = ox
    up = True
    for i in range(6):
        x += seg
        pts.append((x, y_off + 4 if up else y_on - 4))
        up = not up
    poly = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (poly, INK))
    p.append(text(ox + 40, y_on + 26, "температура", size=12, color=INK, anchor="start", italic=True))

    # точки перемикання — де крива торкається порогів
    for (px, py), on in [(pts[1], False), (pts[2], True), (pts[3], False),
                         (pts[4], True), (pts[5], False)]:
        col = NEG if not on else POS
        p.append(circle(px, py, 4.5, fill=col, stroke="#fff", sw=1.5))

    # стрілка «пам'ять»: у зоні напрям визначає стан
    axm = ox + seg * 1.5
    p.append(text(axm, y_set - dpix - 14, "у зоні реле НЕ чіпаємо —", size=11,
                  color=FIELD, anchor="middle", bold=True))
    p.append(text(axm, y_set - dpix - 0, "тримаємо те, що було", size=11,
                  color=FIELD, anchor="middle", bold=True))

    # --- нижня доріжка: стан реле (ON/OFF), синхронно з перемиканнями ---
    ry_hi = 320                 # рівень «ON»
    ry_lo = 360                 # рівень «OFF»
    p.append(text(ox - 12, ry_hi + 4, "ON", size=12, color=FIELD, anchor="end", bold=True))
    p.append(text(ox - 12, ry_lo + 4, "OFF", size=12, color=MUTED, anchor="end"))
    p.append(line(ox, ry_lo + 14, ox + aw, ry_lo + 14, color=INK, sw=1))
    p.append(text(ox + aw / 2, ry_lo + 32, "час →", size=12, color=INK))

    # реле: ON поки гріємось (до верхнього порога), OFF поки стигне. Прямокутна хвиля,
    # чиї фронти стоять під точками дотику до порогів.
    switch_x = [pts[i][0] for i in range(1, 6)]
    lvl = ry_hi                 # старт: гріємо (ON)
    prev_x = ox
    step = []
    xseq = switch_x + [ox + aw]
    for i, sx in enumerate(xseq):
        step.append((prev_x, lvl))
        step.append((sx, lvl))
        prev_x = sx
        lvl = ry_lo if lvl == ry_hi else ry_hi
    rel = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in step)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (rel, FIELD))
    # вертикальні пунктирні зноски від точок перемикання до доріжки реле
    for sx in switch_x:
        p.append(line(sx, y_set - dpix - 4, sx, ry_lo + 14, color=MUTED, sw=0.8, dash="2 4"))

    p.append(text(ox + aw / 2, 300,
                  "перемикань мало — лише на краях зони, не на кожному тремтінні",
                  size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, 'hysteresis-band.svg'), W, H, *p,
           title="Гістерезис: два пороги замість одного гасять брязкіт реле")


def min_on_off():
    # Дві доріжки часу: без захисту часом (реле деренчить пачкою при шумі)
    # і з min-on/min-off (кожне вмикання/вимикання «залипає» на мінімум).
    W, H = 720, 340
    p = []
    ox = 130
    aw = 540

    def track(y, label, seq, guard):
        # seq: список (тривалість_умовна, рівень 1/0) — «сире» бажання регулятора;
        # guard: чи застосовуємо min-on/min-off (розтягуємо короткі імпульси).
        hi = y - 20
        lo = y + 20
        p.append(text(ox - 14, y - 18, "ON", size=11, color=INK, anchor="end", bold=True))
        p.append(text(ox - 14, y + 24, "OFF", size=11, color=MUTED, anchor="end"))
        p.append(text(ox - 14, y + 2, label, size=12, color=INK, anchor="end", bold=True))
        p.append(line(ox, lo + 4, ox + aw, lo + 4, color=INK, sw=0.8))

        unit = aw / sum(d for d, _ in seq)
        x = ox
        pts = []
        for d, lvl in seq:
            w = d * unit
            yy = hi if lvl else lo
            pts.append((x, yy)); pts.append((x + w, yy))
            x += w
        path = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
        col = POS if not guard else FIELD
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path, col))
        return

    # верх: сире бажання — короткі імпульси через шум на межі (деренчить)
    raw = [(3, 0), (1, 1), (1, 0), (1, 1), (1, 0), (1, 1), (5, 0), (2, 1), (1, 0), (4, 1)]
    track(90, "сире", raw, guard=False)
    p.append(text(ox + aw / 2, 40, "БЕЗ захисту часом: шум на межі → пачка коротких клацань",
                  size=12, color=POS, bold=True))

    # низ: те саме бажання, але кожен стан «залипає» на min-on/min-off →
    # короткі імпульси зникають, лишаються рідкі довгі
    guarded = [(3, 0), (5, 1), (7, 0), (3, 1)]   # злиті/розтягнуті до мінімумів
    track(230, "min-on/off", guarded, guard=True)
    p.append(text(ox + aw / 2, 180,
                  "З min-on/min-off: кожне вмикання тримається щонайменше T_on,",
                  size=12, color=FIELD, bold=True))
    p.append(text(ox + aw / 2, 198,
                  "вимикання — T_off; дрібні смикання просто не встигають статися",
                  size=12, color=FIELD, bold=True))

    # позначки мінімальних інтервалів під нижньою доріжкою
    p.append(text(ox + aw / 2, 300, "час →", size=12, color=INK))

    render(os.path.join(IMG, 'min-on-off.svg'), W, H, *p,
           title="Мінімальний час увімкнення/вимкнення проти частого клацання")


def offline_buffer():
    # Два потоки даних вузла й різна доля кожного при обриві: телеметрія стану
    # тече повз буфер (QoS 0, при обриві губиться), критична подія лягає в
    # кільце фіксованого розміру з дублем у NVS і досилається з QoS 1 після
    # відновлення зв'язку, викреслюючись лише за PUBACK.
    import math
    W, H = 760, 470
    p = []

    src_x = 96
    tel_y = 96
    ev_y = 330
    p.append(circle(src_x, tel_y, 40, fill=FILL, stroke=INK, sw=2))
    p.append(mtext(src_x, tel_y - 4, ["стан", "(часто)"], size=12, color=INK, bold=True))
    p.append(circle(src_x, ev_y, 40, fill="#fdecea", stroke=POS, sw=2.5))
    p.append(mtext(src_x, ev_y - 4, ["ПОДІЯ", "(рідко)"], size=12, color=POS, bold=True))

    net_x = W - 96
    p.append(circle(net_x, 200, 42, fill="#eaf0fd", stroke=NEG, sw=2.5))
    p.append(mtext(net_x, 196, ["брокер", "/ мережа"], size=12, color=NEG, bold=True))

    p.append(arrow(src_x + 34, tel_y - 16, net_x - 34, 178, color=MUTED, sw=1.8))
    p.append(text((src_x + net_x) / 2, tel_y - 22, "QoS 0 — є зв'язок: публікуй",
                  size=12, color=MUTED))
    p.append(text((src_x + net_x) / 2, tel_y + 2, "нема зв'язку: тихо губимо",
                  size=12, color=MUTED, italic=True))

    ring_cx, ring_cy, ring_r = 322, ev_y, 58
    p.append(circle(ring_cx, ring_cy, ring_r, fill="#ffffff", stroke=POS, sw=2.5))
    p.append(circle(ring_cx, ring_cy, ring_r - 22, fill="#ffffff", stroke="#e5b3ad", sw=1.2))
    n_slot = 8
    for i in range(n_slot):
        a = -math.pi / 2 + i * 2 * math.pi / n_slot
        x1 = ring_cx + (ring_r - 22) * math.cos(a)
        y1 = ring_cy + (ring_r - 22) * math.sin(a)
        x2 = ring_cx + ring_r * math.cos(a)
        y2 = ring_cy + ring_r * math.sin(a)
        filled = i < 3
        p.append(line(x1, y1, x2, y2, color=(POS if filled else "#d9d9d9"),
                      sw=2.2 if filled else 1.2))
    p.append(mtext(ring_cx, ring_cy - 4, ["кільце", "N слотів"], size=12, color=POS, bold=True))
    p.append(text(ring_cx, ring_cy + ring_r + 18, "переповнення → витісни найстарішу",
                  size=11, color=MUTED))

    p.append(arrow(src_x + 34, ev_y - 6, ring_cx - ring_r - 4, ring_cy - 6, color=POS, sw=2))

    nvs_y = ev_y + 118
    p.append(fitbox(ring_cx - 96, nvs_y - 18, 192, 34,
                    "журнал у NVS (переживе ресет)", size=12,
                    fill="#eafaf0", stroke=FIELD))
    p.append(arrow(ring_cx, ring_cy + ring_r + 26, ring_cx, nvs_y - 20, color=FIELD, sw=1.8))
    p.append(text(ring_cx + 10, (ring_cy + ring_r + 26 + nvs_y - 20) / 2 + 4,
                  "commit", size=10, color=FIELD, anchor="start"))

    p.append(arrow(ring_cx + ring_r + 4, ring_cy - 20, net_x - 30, 224, color=POS, sw=2.4))
    # підписи «досилання» — НИЖЧЕ пунктиру PUBACK, щоб зустрічна стрілка їх не різала
    p.append(text((ring_cx + net_x) / 2 + 24, 312, "QoS 1", size=14, color=POS, bold=True))
    p.append(text((ring_cx + net_x) / 2 + 24, 330, "дослати після", size=11, color=MUTED))
    p.append(text((ring_cx + net_x) / 2 + 24, 344, "перепідключення", size=11, color=MUTED))

    p.append(arrow(net_x - 30, 250, ring_cx + ring_r + 6, ring_cy + 12, color=NEG, sw=1.6))
    p.append(text((ring_cx + net_x) / 2 + 20, 382, "PUBACK → викресли", size=11,
                  color=NEG, italic=True))

    render(os.path.join(IMG, 'offline-buffer.svg'), W, H, *p,
           title="Стан губимо · подію беремо в кільце й досилаємо з QoS 1")


# ═══ Фігури ДЕТАЛЬНОЇ версії (smart-home-node-d.md) ═══════════════════════════

def loop_budget():
    # Дві часові доріжки одного витка loop(): угорі — блокувальний мережевий
    # виклик з'їдає весь бюджет і морозить керування; унизу — розділені петлі,
    # де керування завжди встигає, а мережа лише зазирає й іде далі.
    # Вісь часу проведена ПІД блоками (не крізь них), щоб лінія не різала написи.
    W, H = 740, 430
    p = []
    ox = 160
    aw = 536

    def blk(ytop, x, w, col, fill, s):
        h = 30
        p.append(rect(x, ytop, w, h, fill=fill, stroke=col, sw=1.8, rx=4))
        fs = fit_font(s, w - 8, 12, True)
        p.append(text(x + w / 2, ytop + h / 2 + 4, s, size=fs, color=col, bold=True))

    # --- ВЕРХ: наївний блокувальний loop ---
    p.append(text(ox + aw / 2, 54,
                  "БЛОКУВАЛЬНО: один загальний цикл, кроки чекають один одного",
                  size=13, color=POS, bold=True))
    yt = 78                       # верх ряду блоків
    ax_t = yt + 30 + 8            # вісь — під блоками
    blk(yt, ox + 4, 70, FIELD, "#eafaf0", "давач")
    blk(yt, ox + 78, 66, FIELD, "#eafaf0", "правило")
    blk(yt, ox + 148, 300, POS, "#fdecea", "mqtt_connect / publish — ЧЕКАЄ")
    p.append(text(ox + 148 + 150, yt - 10, "мережа зависла на секунди", size=11,
                  color=POS, italic=True))
    p.append(line(ox - 4, ax_t, ox + aw, ax_t, color=INK, sw=1.1))
    p.append(text(ox - 12, ax_t - 4, "loop()", size=12, color=INK, anchor="end", bold=True))
    # брекет під віссю: увесь цей час керування мертве
    by = ax_t + 14
    p.append(line(ox + 148, by, ox + 448, by, color=POS, sw=1.4))
    p.append(line(ox + 148, by - 5, ox + 148, by, color=POS, sw=1.4))
    p.append(line(ox + 448, by - 5, ox + 448, by, color=POS, sw=1.4))
    p.append(text(ox + 298, by + 15, "тут давач не читається, реле не смикається — вузол глухне",
                  size=11, color=POS, anchor="middle"))

    # --- НИЗ: розділені петлі ---
    p.append(text(ox + aw / 2, 244,
                  "НЕБЛОКУВАЛЬНО: швидка петля обмежена в часі, мережа лише зазирає",
                  size=13, color=FIELD, bold=True))
    yb = 272
    ax_b = yb + 24 + 8
    xx = ox + 4
    for i in range(6):
        blk(yb, xx, 44, FIELD, "#eafaf0", "керув.")
        xx += 50
        p.append(rect(xx, yb + 3, 18, 18, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=3))
        xx += 24
    p.append(line(ox - 4, ax_b, ox + aw, ax_b, color=INK, sw=1.1))
    p.append(text(ox - 12, ax_b - 4, "loop()", size=12, color=INK, anchor="end", bold=True))
    p.append(text(ox + 4 + 22, yb - 10, "≤ T_max", size=11, color=FIELD, bold=True, anchor="middle"))
    p.append(text(xx + 8, yb + 2, "мережа —", size=10, color=NEG, anchor="start"))
    p.append(text(xx + 8, yb + 15, "по краплі,", size=10, color=NEG, anchor="start"))
    p.append(text(xx + 8, yb + 28, "без чекання", size=10, color=NEG, anchor="start"))
    p.append(text(ox + aw / 2, ax_b + 30,
                  "найгірший виток обмежений зверху → watchdog можна ставити тісно",
                  size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, 'loop-budget.svg'), W, H, *p,
           title="Бюджет часу витка: блокувальний виклик краде його весь")


def millis_wrap():
    # Числова пряма лічильника millis() з переповненням у нулі. Показуємо, що
    # беззнакове віднімання now − then дає правильний інтервал навіть коли now
    # перескочив через межу, а «пряме» порівняння then < now — ламається.
    W, H = 740, 380
    p = []
    ox, aw = 90, 560
    y = 150
    fullw = aw

    # вісь лічильника 0 … MAX, з обгортанням
    p.append(line(ox, y, ox + fullw, y, color=INK, sw=1.6))
    p.append(text(ox, y + 26, "0", size=12, color=INK))
    p.append(text(ox + fullw, y + 26, "2³² − 1 (MAX)", size=12, color=INK, anchor="end"))
    # значок «перескок через край» — стрілка з кінця на початок
    p.append('<path d="M %.1f %.1f q 40 -46 -%.1f -46 q -%.1f 0 -%.1f 46" '
             'fill="none" stroke="%s" stroke-width="1.6" '
             'marker-end="url(#arrow)"/>' % (ox + fullw, y - 8, fullw, fullw / 2, fullw, MUTED))
    p.append(text(ox + fullw / 2, y - 62, "лічильник обертається кожні ≈ 49 діб",
                  size=12, color=MUTED, italic=True))

    # then — трохи не доходячи до кінця; now — уже за краєм, тобто на малому значенні
    x_then = ox + fullw - 70
    x_now = ox + 60
    p.append(line(x_then, y - 9, x_then, y + 9, color=NEG, sw=2.4))
    p.append(text(x_then, y - 18, "then", size=13, color=NEG, bold=True, anchor="middle"))
    p.append(text(x_then, y - 34, "= MAX − 30", size=11, color=NEG, anchor="middle"))
    p.append(line(x_now, y - 9, x_now, y + 9, color=POS, sw=2.4))
    p.append(text(x_now, y - 18, "now", size=13, color=POS, bold=True, anchor="middle"))
    p.append(text(x_now, y - 34, "= 70", size=11, color=POS, anchor="middle"))

    # справжній інтервал = коротка дуга через край (30 + 70 = 100)
    p.append(text(ox + fullw / 2, y + 58,
                  "справжній інтервал = 30 + 70 = 100 мс (короткий стрибок через край)",
                  size=12, color=INK))

    # два підписи внизу: правильно / неправильно
    b1 = fitbox(ox, y + 92, 300, 62,
                "now − then  (беззнаково)\n= 70 − (MAX−30)\n= 100  ✓ правильно",
                size=12, fill="#eafaf0", stroke=FIELD, bold=True)
    p.append(b1)
    b2 = fitbox(ox + fullw - 300, y + 92, 300, 62,
                "then < now ?\nMAX−30 < 70 → хибно\n→ «час не настав» ✗ зависання",
                size=12, fill="#fdecea", stroke=POS, bold=True)
    p.append(b2)

    render(os.path.join(IMG, 'millis-wrap.svg'), W, H, *p,
           title="Чому now − then переживає переповнення, а then < now — ні")


def conn_fsm():
    # Мережевий шар вузла як явний автомат: OFFLINE → CONNECTING → ONLINE,
    # з поверненням у BACKOFF і паузою, що подвоюється. Керування живе окремо
    # й не входить у цей автомат зовсім.
    W, H = 760, 430
    p = []

    def node(cx, cy, r, s, col, fill):
        out = circle(cx, cy, r, fill=fill, stroke=col, sw=2.4)
        out += mtext(cx, cy - 2, s, size=13, color=col, bold=True)
        return out

    # чотири стани по колу
    p.append(node(150, 220, 52, ["OFFLINE", "накопичуй"], NEG, "#eaf0fd"))
    p.append(node(380, 110, 52, ["CONNECTING", "спроба"], "#b8860b", "#fff7e6"))
    p.append(node(610, 220, 52, ["ONLINE", "звітуй"], FIELD, "#eafaf0"))
    p.append(node(380, 340, 56, ["BACKOFF", "пауза×2"], POS, "#fdecea"))

    # переходи (стрілки з підписами поза лініями)
    p.append(arrow(196, 196, 336, 132, color=INK, sw=1.8))
    p.append(text(250, 150, "є Wi-Fi →", size=11, color=INK, anchor="middle"))
    p.append(arrow(424, 132, 566, 196, color=INK, sw=1.8))
    p.append(text(512, 150, "CONNACK →", size=11, color=FIELD, anchor="middle", bold=True))

    # ONLINE → BACKOFF (обрив)
    p.append(arrow(576, 258, 430, 322, color=POS, sw=1.8))
    p.append(text(543, 316, "обрив / keepalive", size=11, color=POS, anchor="middle"))
    # CONNECTING → BACKOFF (невдача)
    p.append(arrow(380, 162, 380, 284, color=POS, sw=1.8))
    p.append(text(392, 226, "невдача", size=11, color=POS, anchor="start"))
    # BACKOFF → OFFLINE (пауза сплила, пробуємо знову з новою затримкою)
    p.append(arrow(326, 330, 190, 262, color=NEG, sw=1.8))
    p.append(text(250, 316, "пауза сплила →", size=11, color=NEG, anchor="middle"))

    # зростання затримки збоку
    bx = 632
    p.append(text(bx, 330, "затримка:", size=11, color=POS, anchor="start", bold=True))
    p.append(text(bx, 348, "1·2·4·8·…", size=11, color=POS, anchor="start"))
    p.append(text(bx, 366, "→ стеля", size=11, color=POS, anchor="start"))
    p.append(text(bx, 384, "+ джитер", size=11, color=MUTED, anchor="start"))

    # окремо: керування поза автоматом
    cb = fitbox(70, 372, 300, 40,
                "керування крутиться ПОЗА цим автоматом — байдуже до стану мережі",
                size=11, fill=FILL, stroke=FIELD, bold=True)
    p.append(cb)

    render(os.path.join(IMG, 'conn-fsm.svg'), W, H, *p,
           title="Мережевий шар як автомат: спроба · онлайн · відкат із паузою")


def keepalive_lwt():
    # Часова лінія keepalive: клієнт шле PINGREQ, брокер відповідає PINGRESP;
    # коли вузол раптово зник, брокер чекає 1.5×keepalive мовчання й публікує
    # заповіт offline. Показуємо вікно виявлення обриву.
    W, H = 760, 380
    p = []
    ox, aw = 70, 620
    yc = 120                      # лінія клієнта
    yb = 300                      # лінія брокера
    p.append(text(ox - 4, yc - 40, "ВУЗОЛ", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(ox - 4, yb + 44, "БРОКЕР", size=12, color=NEG, anchor="start", bold=True))
    p.append(line(ox, yc, ox + aw, yc, color=FIELD, sw=1.6))
    p.append(line(ox, yb, ox + aw, yb, color=NEG, sw=1.6))

    # три успішні пінги через рівні проміжки
    ka = 150
    for i, x in enumerate([ox + 60, ox + 60 + ka, ox + 60 + 2 * ka]):
        alive = i < 2                          # третій пінг уже не піде (вузол зник)
        if alive:
            p.append(arrow(x, yc + 6, x, yb - 6, color=FIELD, sw=1.6))
            p.append(text(x, yc - 12, "PINGREQ", size=10, color=FIELD, anchor="middle"))
            p.append(arrow(x + 14, yb - 6, x + 14, yc + 6, color=NEG, sw=1.4))
            p.append(text(x + 40, yb + 18, "PINGRESP", size=10, color=NEG, anchor="middle"))

    # мить раптової смерті вузла — після другого пінга
    x_die = ox + 60 + ka + 40
    p.append(line(x_die, yc - 22, x_die, yc + 22, color=POS, sw=2.2))
    p.append(text(x_die, yc - 30, "вузол раптово зник", size=11, color=POS, anchor="middle", bold=True))
    # хрестик на лінії клієнта далі — тиша
    p.append(line(x_die, yc, ox + aw, yc, color=POS, sw=1.4, dash="4 5"))

    # брокер чекає 1.5×keepalive тиші, тоді публікує LWT
    x_lwt = x_die + int(1.5 * ka) - 30
    p.append(line(x_die, yb + 60, x_lwt, yb + 60, color=POS, sw=1.4))
    p.append(line(x_die, yb + 55, x_die, yb + 65, color=POS, sw=1.4))
    p.append(line(x_lwt, yb + 55, x_lwt, yb + 65, color=POS, sw=1.4))
    p.append(text((x_die + x_lwt) / 2, yb + 78, "тиша ≥ 1.5 × keepalive", size=11,
                  color=POS, anchor="middle", bold=True))
    p.append(arrow(x_lwt, yb - 6, x_lwt, yc + 40, color=POS, sw=1.8))
    p.append(fitbox(x_lwt - 78, yc + 40, 156, 30, "публікує заповіт: offline",
                    size=11, fill="#fdecea", stroke=POS, bold=True))

    p.append(text(ox + aw / 2, H - 18,
                  "поки вузол пінгує — він online; замовк надовго — брокер сам оголосить offline",
                  size=12, color=INK, anchor="middle"))

    render(os.path.join(IMG, 'keepalive-lwt.svg'), W, H, *p,
           title="Keepalive і заповіт: як брокер помічає, що вузол мовчить")


def backoff_schedule():
    # Розклад перепідключення в часі: після кожної невдалої спроби пауза
    # ПОДВОЮЄТЬСЯ (1·2·4·8·16·32 с) і впирається у стелю (60 с), далі тримається.
    # Показуємо, ЧОМУ це щадить і процесор, і ефір: спроби рідшають самі.
    # Кожна спроба — окрема КОЛОНКА; підпис паузи стоїть ПІД проміжком між
    # колонками, тому нічого не налазить. Ширина колонок росте, але стиснуто.
    W, H = 760, 340
    p = []
    oy = 200                              # рівень осі часу
    x0 = 62

    gaps = [1, 2, 4, 8, 16, 32, 60, 60]   # умовні секунди пауз
    cap = 60
    # ширина проміжку перед спробою: стиснено (log2), щоб усі 8 влізли в 760
    def gw(sec):
        import math
        return 30 + 13 * math.log2(sec + 1)   # 1с→~43, 8с→~74, 60с→~106

    # спершу порахуємо повну ширину, аби центрувати
    xs = []                                # x кожної риски-спроби
    x = x0
    for g in gaps:
        x += gw(g)
        xs.append(x)
    total = xs[-1] - x0
    # вісь
    ax0, ax1 = x0, xs[-1] + 20
    p.append(line(ax0, oy, ax1, oy, color=INK, sw=1.4))
    p.append(arrow(ax1, oy, ax1 + 12, oy, color=INK, sw=1.4))
    p.append(text(ax1 + 4, oy + 22, "час →", size=12, color=INK, anchor="end"))
    # мітка обриву на старті
    p.append(line(x0, oy - 14, x0, oy + 8, color=POS, sw=2.4))
    p.append(text(x0, oy + 24, "обрив", size=11, color=POS, anchor="middle", bold=True))

    xprev = x0
    for i, (g, xa) in enumerate(zip(gaps, xs)):
        atcap = (g == cap)
        col = MUTED if atcap else POS
        yb = oy + 8
        # брекет паузи в проміжку [xprev .. xa]
        p.append(line(xprev, yb, xa, yb, color=col, sw=1.3))
        p.append(line(xprev, yb - 4, xprev, yb + 4, color=col, sw=1.3))
        p.append(line(xa, yb - 4, xa, yb + 4, color=col, sw=1.3))
        p.append(text((xprev + xa) / 2, yb + 18, "%d с" % g, size=11, color=col,
                      anchor="middle", bold=not atcap))
        # риска спроби на осі
        p.append(line(xa, oy - 12, xa, oy + 6, color=NEG, sw=2))
        p.append(text(xa, oy - 18, "×", size=12, color=NEG, anchor="middle", bold=True))
        xprev = xa

    # мітка «стеля» над двома останніми (плоскими) проміжками
    xcap0 = xs[-3]
    xcap1 = xs[-1]
    p.append(line(xcap0, oy - 52, xcap1, oy - 52, color=MUTED, sw=1.4, dash="5 4"))
    p.append(text((xcap0 + xcap1) / 2, oy - 58, "стеля 60 с — далі не росте",
                  size=12, color=MUTED, anchor="middle", bold=True))

    # підпис зростання зліва вгорі
    p.append(text(x0, oy - 78, "пауза ×2 після кожної невдалої спроби (×)",
                  size=13, color=POS, anchor="start", bold=True))

    # висновок унизу
    p.append(fitbox(x0, H - 44, total + 20, 30,
                    "брокера нема → спроби самі рідшають: не гріємо процесор і не забиваємо ефір даремно",
                    size=12, fill=FILL, stroke=FIELD, bold=True))

    render(os.path.join(IMG, 'backoff-schedule.svg'), W, H, *p,
           title="Експоненційний відкат: пауза подвоюється до стелі")


def storm_jitter():
    """Синхронний шторм: детермінований відкат збирає всі спроби в одну мить
    (пачка-спайк), повний джитер розмазує їх рівним килимом у часі."""
    W, H = 760, 470
    p = []
    left = 70
    right = W - 40
    axw = right - left

    # дві осі часу одна над одною: зверху детермінований, знизу з джитером
    def time_axis(oy, label, lcol):
        p.append(line(left, oy, right, oy, color=INK, sw=1.6))
        # поділки часу
        for k in range(0, 6):
            xt = left + axw * k / 5
            p.append(line(xt, oy, xt, oy + 5, color=MUTED, sw=1.2))
            p.append(text(xt, oy + 18, "%d" % k, size=11, color=MUTED))
        p.append(text(right + 2, oy + 18, "с", size=11, color=MUTED, anchor="start"))
        p.append(text(left, oy - 74, label, size=13, color=lcol, anchor="start", bold=True))

    # --- ВЕРХ: детермінований відкат — усі N спроб в один момент (t=1 c) ---
    oyA = 150
    time_axis(oyA, "Детермінований відкат: усі вузли — в ту саму секунду", POS)
    xspk = left + axw * 1 / 5                     # усі падають на t = 1 c
    spike_h = 58
    # товстий стовп-пачка
    p.append(line(xspk, oyA, xspk, oyA - spike_h, color=POS, sw=9))
    p.append(text(xspk + 78, oyA - spike_h + 6, "N спроб РАЗОМ", size=13, color=POS,
                  anchor="start", bold=True))
    # хмарка вузлів праворуч від спайка, що всі показують один час
    for i, dx in enumerate((150, 122, 94, 190, 162, 134)):
        p.append(circle(xspk + dx, oyA - 34 - (i % 3) * 16, 4.5, fill="#fdecea", stroke=POS, sw=1.5))
    p.append(text(xspk, oyA + 40, "брокер захлинається пачкою → усі відбиті → знову разом",
                  size=12, color=POS, anchor="middle"))

    # --- НИЗ: повний джитер — ті самі N спроб рівним килимом 0..cap ---
    oyB = 370
    time_axis(oyB, "Повний джитер: кожен чекає випадково від 0 до cap", FIELD)
    import random
    random.seed(7)
    N = 40
    for _ in range(N):
        t = random.uniform(0, 5)                  # рівномірно по всій осі
        xt = left + axw * t / 5
        h = 20 + random.uniform(0, 8)             # дрібні окремі рисочки
        p.append(line(xt, oyB, xt, oyB - h, color=FIELD, sw=2.2))
    # рівень середнього навантаження — низька рівна лінія (обриваємо перед підписом)
    lvl_y = oyB - 46
    p.append(line(left, lvl_y, left + axw * 0.52, lvl_y, color=FIELD, sw=1.2, dash="6 5"))
    p.append(text(right, lvl_y + 4, "рівне низьке навантаження  N/cap за секунду",
                  size=11, color=FIELD, anchor="end"))
    p.append(text(left + axw / 2, oyB + 40,
                  "жодної секунди-піку → брокер устигає всіх прийняти → рій розсмоктується",
                  size=12, color=FIELD, anchor="middle", bold=True))

    # стрілка перетворення між панелями (підпис ПІД стрілкою, поза її лінією)
    ax_x = left - 40
    p.append(arrow(ax_x, oyA + 34, ax_x, oyB - 120, color=NEG, sw=2))
    p.append(text(ax_x, oyB - 100, "джитер", size=12, color=NEG,
                  anchor="middle", bold=True))

    render(os.path.join(IMG, 'storm-jitter.svg'), W, H, *p,
           title="Синхронний шторм: пачка проти розмазаного килима")


def jitter_strategies():
    """Три стратегії джитера як діапазони паузи на кожній спробі:
    повний (0..cap), рівний (пів+пів), decorrelated (від base до 3× попередньої)."""
    W, H = 780, 430
    p = []
    left = 150
    right = W - 40
    axw = right - left
    cap_val = 8.0                                 # умовна стеля, с
    def X(v):                                     # значення паузи → x
        return left + axw * min(v, cap_val) / cap_val

    rows = [
        ("Повний джитер", "0 … min(cap, base·2ᵃ)", 0.0, cap_val, FIELD),
        ("Рівний джитер", "d/2 … d  (d = min(cap, base·2ᵃ))", cap_val / 2, cap_val, NEG),
        ("Decorrelated", "base … 3× попередньої (до cap)", 1.0, cap_val, POS),
    ]
    y0 = 90
    rh = 96
    # спільна вісь часу знизу
    axis_y = y0 + len(rows) * rh + 6
    p.append(line(left, axis_y, right, axis_y, color=INK, sw=1.5))
    for k in range(0, 5):
        xt = left + axw * k / 4
        p.append(line(xt, axis_y, xt, axis_y + 5, color=MUTED, sw=1.1))
        p.append(text(xt, axis_y + 18, "%.0f" % (k * cap_val / 4), size=11, color=MUTED))
    p.append(text(right, axis_y - 12, "пауза, с (умовні одиниці)", size=11, color=MUTED, anchor="end"))
    # стеля
    p.append(line(X(cap_val), y0 - 10, X(cap_val), axis_y, color=MUTED, sw=1.3, dash="5 4"))
    p.append(text(X(cap_val), y0 - 16, "cap", size=12, color=MUTED, anchor="middle", bold=True))

    for i, (name, rng, lo, hi, col) in enumerate(rows):
        cy = y0 + i * rh + rh / 2
        # підпис зліва
        p.append(text(20, cy - 6, name, size=14, color=col, anchor="start", bold=True))
        p.append(text(20, cy + 14, rng, size=11, color=MUTED, anchor="start"))
        # смуга-діапазон вибору паузи
        bx0, bx1 = X(lo), X(hi)
        p.append(rect(bx0, cy - 16, bx1 - bx0, 32, fill="#eef7f0" if col == FIELD else FILL,
                      stroke=col, sw=2, rx=5))
        # для рівного — показати «завжди-присутню» ліву половину суцільним, праву — джитер
        if name.startswith("Рівний"):
            p.append(rect(X(0), cy - 16, X(cap_val / 2) - X(0), 32, fill="#eef1fb", stroke=NEG, sw=1.6, rx=5))
            p.append(text((X(0) + X(cap_val / 2)) / 2, cy + 5, "гарантована", size=10, color=NEG))
            p.append(text((bx0 + bx1) / 2, cy + 5, "випадкова", size=10, color=NEG))
        elif name.startswith("Повний"):
            p.append(text((bx0 + bx1) / 2, cy + 5, "будь-де в діапазоні — з рівною ймовірністю", size=10, color=FIELD))
        else:
            p.append(text((bx0 + bx1) / 2, cy + 5, "стеля залежить від попередньої паузи", size=10, color=POS))
            # хвостик, що діапазон може рости за cap і зрізається
            p.append(arrow(bx1 - 4, cy, X(cap_val) + 0, cy, color=POS, sw=1.4))

    render(os.path.join(IMG, 'jitter-strategies.svg'), W, H, *p,
           title="Три стратегії джитера: звідки береться пауза")


if __name__ == '__main__':
    three_layers()
    node_topics()
    hysteresis_band()
    min_on_off()
    offline_buffer()
    loop_budget()
    millis_wrap()
    conn_fsm()
    keepalive_lwt()
    backoff_schedule()
    storm_jitter()
    jitter_strategies()
    print("ok")
