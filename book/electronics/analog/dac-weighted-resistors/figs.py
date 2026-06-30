# -*- coding: utf-8 -*-
"""Фігури до статті «ЦАП на зважених резисторах»
(book/electronics/analog/dac-weighted-resistors).
Три фігури:
  idea.svg    — суть: чотири біти крізь зважені резистори R,R/2,R/4,R/8 у віртуальну землю
  steps.svg   — дискретність: код на вході → сходинки напруги на виході, квант = LSB
  spread.svg  — вада: розкид опорів вибухає з розрядністю, допуск стискається → немонотонність
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ─────────────────────────────────────────────────────────
def gnd(cx, y, label=None):
    out = [line(cx, y, cx, y + 7, color=INK, sw=1.8),
           line(cx - 12, y + 7, cx + 12, y + 7, color=INK, sw=2.4),
           line(cx - 7, y + 12, cx + 7, y + 12, color=INK, sw=2.0),
           line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.8)]
    if label:
        out.append(text(cx, y + 31, label, size=11, color=MUTED))
    return "".join(out)


def res_h(x0, x1, y, label=None, lab_above=True, col=INK):
    """Горизонтальний резистор-зигзаг між (x0,y) і (x1,y)."""
    out = []
    n = 6
    seg = (x1 - x0) / (n + 2)
    out.append(line(x0, y, x0 + seg, y, color=col, sw=1.6))
    amp = 6
    xx = x0 + seg
    for i in range(n):
        ny = y + (amp if i % 2 == 0 else -amp)
        out.append(line(xx, y if i == 0 else (y - amp if i % 2 == 1 else y + amp),
                        xx + seg, ny, color=col, sw=1.6))
        xx += seg
    out.append(line(xx, y + (amp if (n - 1) % 2 == 0 else -amp), xx + seg, y, color=col, sw=1.6))
    out.append(line(xx + seg, y, x1, y, color=col, sw=1.6))
    if label:
        ly = y - 13 if lab_above else y + 18
        out.append(text((x0 + x1) / 2, ly, label, size=12, color=col, bold=True))
    return "".join(out)


def opamp(cx, cy, w=70, h=64):
    """Трикутник ОП вістрям праворуч. Повертає (svg, in_minus, in_plus, out)."""
    x0 = cx - w / 2
    top, bot = cy - h / 2, cy + h / 2
    tip = (cx + w / 2, cy)
    out = ['<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#ffffff" '
           'stroke="%s" stroke-width="1.8"/>' % (x0, top, x0, bot, tip[0], tip[1], INK)]
    inm = (x0, cy - h * 0.22)
    inp = (x0, cy + h * 0.22)
    out.append(text(x0 + 12, inm[1] + 5, "−", size=15, color=NEG, bold=True))
    out.append(text(x0 + 12, inp[1] + 5, "+", size=14, color=POS, bold=True))
    return "".join(out), inm, inp, tip


# ════════════════════════════════════════════════════════════════════════════
# 1. idea.svg — суть: зважені резистори у віртуальну землю
# ════════════════════════════════════════════════════════════════════════════
def fig_idea():
    W, H = 700, 430
    f = []

    # ОП праворуч
    opx, opy = 510, 210
    op, inm, inp, tip = opamp(opx, opy)
    f.append(op)

    # віртуальна земля — вузол на вході «−»
    vg_x = inm[0] - 70
    vg_y = inm[1]
    f.append(line(vg_x, vg_y, inm[0], inm[1], color=INK, sw=1.8))
    f.append(circle(vg_x, vg_y, 3, fill=NEG, stroke=NEG))
    f.append(text(vg_x - 4, vg_y - 14, "віртуальна", size=11, color=NEG, anchor="middle"))
    f.append(text(vg_x - 4, vg_y - 1, "земля (0 В)", size=11, color=NEG, anchor="middle", ))

    # «+» на землю
    f.append(line(inp[0], inp[1], inp[0] - 30, inp[1], color=INK, sw=1.6))
    f.append(gnd(inp[0] - 30, inp[1] + 6))

    # чотири біти зліва, кожен через свій резистор у вузол vg
    bits = [
        (70,  "b0", "R",   "вага 1"),
        (130, "b1", "R/2", "вага 2"),
        (190, "b2", "R/4", "вага 4"),
        (250, "b3", "R/8", "вага 8"),
    ]
    res_right = vg_x          # усі резистори сходяться у вертикаль вузла
    for by, blab, rlab, wlab in bits:
        # квадратик-«ключ» біта (0/5 В)
        f.append(rect(56, by - 13, 40, 26, fill="#f4f6f8", stroke=INK, sw=1.4, rx=4))
        f.append(text(76, by + 5, blab, size=13, color=INK, bold=True))
        # резистор від ключа праворуч до спільної вертикалі вузла
        f.append(res_h(96, res_right - 0, by, label=rlab, col=POS))
        # вертикальна злучка резистора до рівня віртуальної землі
    # спільна вертикаль вузла (збираємо всі праві кінці резисторів у vg)
    top_b = bits[0][0]
    bot_b = bits[-1][0]
    f.append(line(res_right, top_b, res_right, vg_y, color=INK, sw=1.8))
    # позначки ваг / напруги розрядів
    f.append(text(40, top_b - 30, "біти: 0 або Vref", size=12, color=MUTED, anchor="start"))

    # стрілка струму вздовж вертикалі у вузол
    f.append(text(res_right + 8, (top_b + vg_y) / 2, "Σ I", size=12, color=FIELD, bold=True, anchor="start"))

    # резистор зворотного зв'язку Rf над ОП: від виходу до вузла «−»
    fbx0, fbx1 = vg_x, tip[0] + 24
    fby = opy - 86
    f.append(line(vg_x, vg_y, vg_x, fby, color=INK, sw=1.6))
    f.append(res_h(vg_x + 6, fbx1 - 6, fby, label="Rf", lab_above=True, col=INK))
    f.append(line(fbx1, fby, fbx1, opy, color=INK, sw=1.6))
    f.append(line(tip[0], tip[1], fbx1, opy, color=INK, sw=1.6))

    # вихід
    f.append(line(tip[0], tip[1], tip[0] + 90, tip[1], color=INK, sw=1.8))
    f.append(arrow(tip[0] + 60, tip[1], tip[0] + 90, tip[1], color=FIELD, sw=2.4))
    f.append(text(tip[0] + 96, tip[1] - 8, "Vout", size=13, color=FIELD, bold=True, anchor="start"))
    f.append(text(tip[0] + 96, tip[1] + 10, "∝ число", size=11, color=MUTED, anchor="start"))

    # підпис-суть унизу
    body, w0, h0 = textbox(W / 2, 392,
                           "Опір половиниться R → R/2 → R/4 → R/8, тож струми відносяться як 1 : 2 : 4 : 8 —\n"
                           "рівно як ваги двійкових розрядів. Сума струмів дає напругу, пропорційну числу.",
                           size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)

    render(os.path.join(IMG, "idea.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. steps.svg — код → сходинки; квант = LSB
# ════════════════════════════════════════════════════════════════════════════
def fig_steps():
    W, H = 680, 420
    f = []
    ox, oy = 90, 320              # початок осей
    axw, axh = 500, 250

    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw - 4, oy + 26, "цифровий код на вході", size=12, color=INK, anchor="end"))
    f.append(text(ox - 14, oy - axh + 8, "Vout", size=13, color=INK, bold=True, anchor="end"))

    # ідеальна пряма (з'єднати верхи сходинок) — пунктир
    nmax = 8                      # 3-бітний приклад: 8 рівнів 000..111
    step_w = axw / (nmax)
    step_h = axh / (nmax)
    # пунктирна ідеальна лінія
    f.append(line(ox, oy, ox + step_w * (nmax - 1), oy - step_h * (nmax - 1),
                  color=MUTED, sw=1.4, dash="6 5"))
    f.append(text(ox + step_w * (nmax - 1) + 6, oy - step_h * (nmax - 1) - 4,
                  "ідеальна\nпряма" if False else "ідеальна пряма", size=10, color=MUTED, anchor="start"))

    # сходинки
    px, py = ox, oy
    for k in range(nmax):
        nx = ox + step_w * (k + 1)
        ny = oy - step_h * k
        f.append(line(px, ny, nx, ny, color=POS, sw=2.6))          # горизонталь сходинки
        if k < nmax - 1:
            f.append(line(nx, ny, nx, ny - step_h, color=POS, sw=2.6))  # підйом
        px = nx
    # коди під віссю
    codes = ["000", "001", "010", "011", "100", "101", "110", "111"]
    for k, c in enumerate(codes):
        cx = ox + step_w * (k + 0.5)
        f.append(text(cx, oy + 16, c, size=10, color=INK))

    # квант (LSB) — показати висоту однієї сходинки
    qx = ox + step_w * 1
    f.append(line(qx - 6, oy, qx - 6, oy - step_h, color=NEG, sw=1.6))
    f.append(line(qx - 10, oy, qx - 2, oy, color=NEG, sw=1.6))
    f.append(line(qx - 10, oy - step_h, qx - 2, oy - step_h, color=NEG, sw=1.6))
    bb, _, _ = textbox(qx + 70, oy - step_h / 2, "квант\n(1 LSB)", size=10, color=NEG,
                       fill="#eaf0fd", stroke=NEG)
    f.append(bb)

    # підпис унизу
    f.append(text(W / 2, H - 16,
                  "Код стрибає цілими комбінаціями → напруга йде сходинками. Більше бітів — дрібніший квант, ближче до прямої.",
                  size=11, color=MUTED))

    render(os.path.join(IMG, "steps.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. spread.svg — розкид опорів вибухає; немонотонність на переході старшого
# ════════════════════════════════════════════════════════════════════════════
def fig_spread():
    W, H = 700, 430
    f = []

    f.append(text(W / 2, 34, "Чому зважена схема не масштабується", size=16, bold=True))

    # ── ліва панель: таблиця розкиду ──
    lx = 60
    rows = [
        ("4 біти",  "8 : 1",     "≈ 11 %"),
        ("8 бітів", "128 : 1",   "≈ 0.4 %"),
        ("12 бітів", "2048 : 1", "≈ 0.02 %"),
    ]
    f.append(text(lx, 80, "розряд-", size=11, color=MUTED, anchor="start"))
    f.append(text(lx, 94, "ність", size=11, color=MUTED, anchor="start"))
    f.append(text(lx + 110, 87, "розкид опорів", size=11, color=MUTED, anchor="middle"))
    f.append(text(lx + 235, 80, "допуск на", size=11, color=MUTED, anchor="middle"))
    f.append(text(lx + 235, 94, "старший біт", size=11, color=MUTED, anchor="middle"))
    yy = 116
    for name, spread, tol in rows:
        f.append(text(lx, yy + 4, name, size=12, color=INK, bold=True, anchor="start"))
        f.append(text(lx + 110, yy + 4, spread, size=12, color=POS, bold=True, anchor="middle"))
        f.append(text(lx + 235, yy + 4, tol, size=12, color=NEG, bold=True, anchor="middle"))
        yy += 34
    bb, _, _ = textbox(lx + 150, yy + 26,
                       "більше бітів →\nширший розкид, жорсткіший допуск",
                       size=10, color=INK, fill="#fdecea", stroke=POS)
    f.append(bb)

    # ── права панель: немонотонність на переході 0111 → 1000 ──
    ox, oy = 420, 330
    axw, axh = 230, 200
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.6))
    f.append(text(ox + axw - 2, oy + 22, "код →", size=11, color=INK, anchor="end"))
    f.append(text(ox - 8, oy - axh + 6, "Vout", size=11, color=INK, bold=True, anchor="end"))

    # ідеальні монотонні сходинки (сірий пунктир) — рівномірні
    n = 8
    sw_ = axw / n
    sh_ = axh / (n + 1)
    px = ox
    ideal_y = []
    for k in range(n):
        ny = oy - sh_ * k
        ideal_y.append(ny)
        f.append(line(px, ny, ox + sw_ * (k + 1), ny, color=MUTED, sw=1.3, dash="4 4"))
        px = ox + sw_ * (k + 1)

    # реальна крива з провалом на переході 3→4 (0111 → 1000)
    real_y = list(ideal_y)
    real_y[4] = ideal_y[4] + sh_ * 1.6   # код 100 просів НИЖЧЕ за код 011
    px = ox
    for k in range(n):
        ny = real_y[k]
        f.append(line(px, ny, ox + sw_ * (k + 1), ny, color=POS, sw=2.4))
        px = ox + sw_ * (k + 1)
    # стрілка-провал
    fall_x = ox + sw_ * 4 + 2
    f.append(arrow(fall_x, real_y[3] - 2, fall_x, real_y[4] - 2, color=NEG, sw=2.0))
    bb, _, _ = textbox(ox + axw - 50, oy - axh + 26,
                       "код виріс —\nнапруга впала", size=10, color=NEG,
                       fill="#eaf0fd", stroke=NEG)
    f.append(bb)
    # позначка переходу під віссю
    f.append(text(ox + sw_ * 4, oy + 16, "0111→1000", size=9.5, color=INK))

    # підпис унизу
    body, w0, h0 = textbox(W / 2, 404,
                           "На переході старшого розряду гаснуть усі молодші й запалюється один старший: якщо його резистор\n"
                           "трохи неточний, стрибок виходить замалим — напруга просідає там, де код зріс. Це немонотонність.",
                           size=11, color=INK, fill="#f4f6f8", stroke=MUTED)
    f.append(body)

    render(os.path.join(IMG, "spread.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. sar-loop.svg — історія: ЦАП живе ВСЕРЕДИНІ оцифровувача (петля наближення)
# ════════════════════════════════════════════════════════════════════════════
def fig_sar_loop():
    W, H = 820, 360
    f = []

    # вхідна аналогова напруга зліва
    inx, iny = 60, 150
    f.append(text(inx, iny - 18, "аналоговий", size=11, color=MUTED))
    f.append(text(inx, iny - 4, "сигнал", size=11, color=MUTED))

    # компаратор (трикутник вістрям праворуч) — «терези»
    cmpx, cmpy = 250, 150
    cw, ch = 78, 78
    x0 = cmpx - cw / 2
    top, bot = cmpy - ch / 2, cmpy + ch / 2
    tip = (cmpx + cw / 2, cmpy)
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#ffffff" '
             'stroke="%s" stroke-width="1.8"/>' % (x0, top, x0, bot, tip[0], tip[1], INK))
    f.append(text(cmpx - 8, cmpy + 5, "?", size=22, color=INK, bold=True))
    f.append(text(cmpx, bot + 16, "компаратор", size=11, color=MUTED))
    inhi = (x0, cmpy - ch * 0.24)
    inlo = (x0, cmpy + ch * 0.24)
    f.append(text(x0 + 13, inhi[1] + 5, "+", size=14, color=POS, bold=True))
    f.append(text(x0 + 13, inlo[1] + 5, "−", size=15, color=NEG, bold=True))

    # вхід → «+» компаратора
    f.append(arrow(inx + 4, iny, inhi[0] - 2, inhi[1], color=INK, sw=1.8))

    # реєстр наближення (число-здогад) праворуч угорі
    regb, rw, rh = textbox(540, 70, "регістр наближення\n(поточний здогад — число)",
                           size=11.5, color=INK, fill="#f4f6f8", stroke=INK, bold=False)
    f.append(regb)

    # ЦАП — центральна рамка, виділена зеленим (ОСЬ ВІН)
    dacb, dw, dh = textbox(540, 230, "ЦАП\nкод → пробна напруга",
                           size=13, color=FIELD, fill="#eafaf0", stroke=FIELD, bold=True)
    f.append(dacb)
    f.append(text(540, 230 + dh / 2 + 16, "це і є перетворювач усередині", size=10.5, color=FIELD))

    # регістр → ЦАП (число вниз)
    f.append(arrow(540, 70 + rh / 2, 540, 230 - dh / 2, color=INK, sw=1.8))
    f.append(text(540 + 8, (70 + rh / 2 + 230 - dh / 2) / 2 + 4, "код", size=11, color=INK, anchor="start"))

    # ЦАП → «−» компаратора (пробна напруга вліво)
    yb = 230 + dh / 2 + 40
    f.append(line(540, 230 + dh / 2, 540, yb, color=FIELD, sw=2.0))
    f.append(line(540, yb, inlo[0] - 24, yb, color=FIELD, sw=2.0))
    f.append(line(inlo[0] - 24, yb, inlo[0] - 24, inlo[1], color=FIELD, sw=2.0))
    f.append(arrow(inlo[0] - 24, inlo[1], inlo[0] - 2, inlo[1], color=FIELD, sw=2.0))
    f.append(text((540 + inlo[0]) / 2, yb + 16, "пробна напруга", size=11, color=FIELD))

    # компаратор → регістр (рішення про біт угору)
    f.append(line(tip[0], tip[1], tip[0] + 40, tip[1], color=INK, sw=1.8))
    f.append(line(tip[0] + 40, tip[1], tip[0] + 40, 70, color=INK, sw=1.8))
    f.append(arrow(tip[0] + 40, 70, 540 - rw / 2 - 2, 70, color=INK, sw=1.8))
    f.append(text(tip[0] + 46, 110, "лишити чи", size=10.5, color=INK, anchor="start"))
    f.append(text(tip[0] + 46, 124, "скинути біт", size=10.5, color=INK, anchor="start"))

    # підпис
    body, _, _ = textbox(W / 2, 332,
                         "Оцифровувач вгадує число розряд за розрядом: компаратор зважує вхід проти пробної напруги, а ту "
                         "пробну\nнапругу виробляє ЦАП із поточного здогаду. Тому перші резисторні ЦАП народилися саме "
                         "тут — як вузол усередині оцифровувача.",
                         size=11, color=INK, fill="#f4f6f8", stroke=MUTED)
    f.append(body)

    render(os.path.join(IMG, "sar-loop.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. kelvin-varley.svg — історія: одна декада = 11 резисторів замість 1000
# ════════════════════════════════════════════════════════════════════════════
def fig_kelvin_varley():
    W, H = 780, 320
    f = []

    f.append(text(W / 2, 30, "Подільник Кельвіна-Варлі: каскад декад", size=16, color=INK, bold=True))

    # Декада 1: вертикальний ланцюг з 11 резисторів зліва
    dx = 120
    y_top, y_bot = 70, 250
    n = 11
    step = (y_bot - y_top) / n
    f.append(text(dx, y_top - 14, "декада 1", size=12, color=INK, bold=True))
    f.append(text(dx, y_top - 1, "(десяті)", size=10.5, color=MUTED))
    for i in range(n):
        yy = y_top + i * step
        # резистор-прямокутник
        col = FIELD if i in (4, 5) else INK    # дві охоплені ланки — зелені
        f.append(rect(dx - 12, yy + 3, 24, step - 6, fill=("#eafaf0" if col == FIELD else "#f4f6f8"),
                      stroke=col, sw=1.6, rx=3))
    f.append(line(dx, y_top, dx, y_top, color=INK))
    # опорні виводи
    f.append(text(dx, y_top - 28, "Vref", size=11, color=POS, bold=True))
    f.append(text(dx, y_bot + 18, "0 В", size=11, color=NEG))

    # повзунок охоплює 2 сусідні (зелені) ланки
    tap_y = y_top + 5 * step
    f.append(line(dx + 12, tap_y, dx + 70, tap_y, color=FIELD, sw=2.4))
    f.append(circle(dx + 12, tap_y, 3.5, fill=FIELD, stroke=FIELD))
    bb, bw, bh = textbox(dx + 150, tap_y, "повзунок охоплює\n2 сусідні ланки", size=10.5,
                         color=FIELD, fill="#eafaf0", stroke=FIELD)
    f.append(bb)

    # Стрілка до декади 2
    f.append(arrow(dx + 150 + bw / 2, tap_y, 430, tap_y, color=INK, sw=1.8))

    # Декада 2: знову 11 ланок, праворуч
    dx2 = 500
    f.append(text(dx2, y_top - 14, "декада 2", size=12, color=INK, bold=True))
    f.append(text(dx2, y_top - 1, "(соті)", size=10.5, color=MUTED))
    for i in range(n):
        yy = y_top + i * step
        f.append(rect(dx2 - 12, yy + 3, 24, step - 6, fill="#f4f6f8", stroke=INK, sw=1.4, rx=3))
    # ключова рівність
    eqb, ew, eh = textbox(dx2 + 150, 130,
                          "вхідний опір декади 2\n= опору ТИХ 2 ланок\n→ не навантажує\n   декаду 1",
                          size=10.5, color=INK, fill="#f4f6f8", stroke=MUTED)
    f.append(eqb)

    # підсумковий рядок
    body, _, _ = textbox(W / 2, 296,
                         "Одна декада — лише 11 однакових резисторів, а не сотні. Каскад трьох декад дає крок 0.001 "
                         "(33 резистори замість 1000):\nточність береться з рівності й відношень елементів, а не з "
                         "абсолютних номіналів — та сама засада, що й у драбинці R-2R.",
                         size=11, color=INK, fill="#f4f6f8", stroke=MUTED)
    f.append(body)

    render(os.path.join(IMG, "kelvin-varley.svg"), W, H, *f)


if __name__ == "__main__":
    fig_idea()
    fig_steps()
    fig_spread()
    fig_sar_loop()
    fig_kelvin_varley()
    print("OK: 5 фігур у", IMG)
