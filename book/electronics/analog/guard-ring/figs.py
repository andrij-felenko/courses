# -*- coding: utf-8 -*-
"""Фігури до статті «Guard ring і ведений екран» (book/electronics/analog/guard-ring).
Чотири фігури:
  idea.svg    — ідея: сторож тієї самої напруги навколо вузла → між ними 0 В → нема витоку
  buffer.svg  — механізм: буфер копіює напругу сигналу на сторож; витік тече з виходу буфера
  cable.svg   — ємність: заземлений екран ріже смугу ↔ ведений екран (обкладки рухаються разом)
  triax.svg   — триакс у розрізі: жила / внутрішній (guard) / зовнішній (земля) — три ролі
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ────────────────────────────────────────────────────────
def gnd(cx, y, label=None):
    out = [line(cx, y, cx, y + 7, color=INK, sw=1.8),
           line(cx - 13, y + 7, cx + 13, y + 7, color=INK, sw=2.4),
           line(cx - 8, y + 12, cx + 8, y + 12, color=INK, sw=2.0),
           line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.8)]
    if label:
        out.append(text(cx, y + 31, label, size=11, color=MUTED))
    return "".join(out)


def buffer_tri(cx, cy, scale=1.0, label="×1"):
    """Трикутник буфера-повторювача, вершиною вправо.
    Повертає (svg, in_node, out_node)."""
    w = 46 * scale
    h = 42 * scale
    p_in_top = (cx - w / 2, cy - h / 2)
    p_in_bot = (cx - w / 2, cy + h / 2)
    p_out = (cx + w / 2, cy)
    body = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#ffffff" '
            'stroke="%s" stroke-width="1.8"/>' % (p_in_top[0], p_in_top[1],
            p_in_bot[0], p_in_bot[1], p_out[0], p_out[1], INK))
    body += text(cx - w * 0.12, cy + 5, label, size=int(13 * scale), color=INK, bold=True)
    return body, (cx - w / 2, cy), (cx + w / 2, cy)


def cap(cx, cy, horiz=False, gap=10, plate=20, label=None, color=INK):
    """Конденсатор (дві пластини). Повертає svg + два вузли-виводи."""
    if horiz:
        x1 = cx - gap / 2; x2 = cx + gap / 2
        out = [line(x1, cy - plate / 2, x1, cy + plate / 2, color=color, sw=2.6),
               line(x2, cy - plate / 2, x2, cy + plate / 2, color=color, sw=2.6)]
        n1 = (cx - gap / 2 - 0, cy); n2 = (cx + gap / 2 + 0, cy)
        if label:
            out.append(text(cx, cy + plate / 2 + 16, label, size=11, color=color, anchor="middle"))
        return "".join(out), (x1, cy), (x2, cy)
    else:
        y1 = cy - gap / 2; y2 = cy + gap / 2
        out = [line(cx - plate / 2, y1, cx + plate / 2, y1, color=color, sw=2.6),
               line(cx - plate / 2, y2, cx + plate / 2, y2, color=color, sw=2.6)]
        if label:
            out.append(text(cx + plate / 2 + 6, cy + 4, label, size=11, color=color, anchor="start"))
        return "".join(out), (cx, y1), (cx, y2)


# ════════════════════════════════════════════════════════════════════════════
# 1. idea.svg — сторож тієї самої напруги → нуль вольтів між ним і сигналом
# ════════════════════════════════════════════════════════════════════════════
def fig_idea():
    W, H = 660, 360
    f = []

    # зовнішнє «брудне» кільце-світ (шина з витоком)
    cxn, cyn = W / 2, 180
    # сторож — середнє кільце
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="170" ry="110" fill="#eef7f0" '
             'stroke="%s" stroke-width="2.6"/>' % (cxn, cyn, FIELD))
    f.append(text(cxn, cyn - 78, "СТОРОЖ  (тієї самої напруги, що сигнал)", size=12, color=FIELD, bold=True))

    # чутливий вузол — у центрі
    f.append(circle(cxn, cyn + 6, 34, fill="#fdecea", stroke=POS, sw=2.4))
    f.append(text(cxn, cyn + 2, "сигнал", size=12, color=POS, bold=True))
    f.append(text(cxn, cyn + 18, "U", size=12, color=POS, bold=True))

    # витік ззовні (брудна плата / шина +5В) — стрілки в сторож, не у вузол
    f.append(text(70, 60, "брудна поверхня · сусідня шина +5 В", size=12, color=MUTED, anchor="start"))
    for sx in (120, W - 120):
        f.append(arrow(sx, 95, cxn + (-150 if sx < cxn else 150), cyn - 60, color=MUTED, sw=2.0))
    f.append(text(cxn, 110, "витік", size=11, color=MUTED))

    # підпис «між сторожем і сигналом 0 В»
    f.append(line(cxn, cyn + 6 + 34, cxn, cyn + 84, color=FIELD, sw=1.4, dash="4 4"))
    body, w0, h0 = textbox(cxn, cyn + 104, "між сигналом і сторожем  ΔU = 0  →  I = ΔU / R = 0",
                           size=12, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)

    # винесена суть
    f.append(text(W / 2, H - 16, "Витік тече туди, де є різниця напруг. Зрівняли потенціали — і він обходить сигнал.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "idea.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. buffer.svg — буфер копіює напругу сигналу на сторож
# ════════════════════════════════════════════════════════════════════════════
def fig_buffer():
    W, H = 740, 360
    f = []
    top, bot = 70, 300

    # вузол-сигнал ліворуч
    nx, ny = 120, 150
    f.append(circle(nx, ny, 8, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(text(nx, ny - 18, "високоомний", size=11, color=POS, anchor="middle"))
    f.append(text(nx, ny - 4, "вузол", size=11, color=POS, anchor="middle"))

    # лінія сигналу на вхід буфера
    btri, bin_, bout = buffer_tri(300, ny, scale=1.15, label="×1")
    f.append(line(nx + 8, ny, bin_[0], bin_[1], color=POS, sw=2.2))
    f.append(btri)
    f.append(text((nx + 8 + bin_[0]) / 2, ny + 18, "сигнал (нічого не споживає)", size=10, color=MUTED, anchor="middle"))

    # вихід буфера → сторож (екран)
    sx = bout[0] + 54
    f.append(line(bout[0], bout[1], sx, ny, color=FIELD, sw=2.4))
    f.append(text(bout[0] + 6, ny - 12, "копія U", size=11, color=FIELD, bold=True, anchor="start"))

    # сторож — рамка навколо «вузла» праворуч (символічно прямокутник)
    gx, gy, gw, gh = sx, top + 20, 200, 200
    f.append(rect(gx, gy, gw, gh, fill="#eef7f0", stroke=FIELD, sw=2.4, rx=10))
    f.append(text(gx + gw / 2, gy + 20, "СТОРОЖ / екран", size=12, color=FIELD, bold=True))
    # копія вузла всередині сторожа
    inx, iny = gx + gw / 2, gy + gh / 2 + 6
    f.append(circle(inx, iny, 8, fill="#fdecea", stroke=POS, sw=2.2))
    f.append(text(inx, iny - 16, "той самий вузол", size=10, color=POS, anchor="middle"))
    f.append(line(sx, ny, inx, gy, color=FIELD, sw=2.0))

    # витік: від брудної шини у сторож (бере буфер), не у вузол
    railx = gx + gw + 40
    f.append(line(railx, top, railx, bot, color=INK, sw=2.4))
    f.append(text(railx + 6, top + 4, "+5 В", size=12, color=INK, bold=True, anchor="start"))
    # R_leak від шини до сторожа
    f.append(line(railx, iny, gx + gw, iny, color=MUTED, sw=1.6))
    f.append(text((railx + gx + gw) / 2, iny - 8, "R_leak", size=11, color=MUTED, anchor="middle"))
    f.append(arrow(railx - 4, iny, gx + gw + 4, iny, color=MUTED, sw=1.8))

    # підпис-суть
    body, w0, h0 = textbox(W / 2, H - 30,
                           "Витік падає між сторожем і шиною — його струм віддає ВИХІД буфера.\nМіж сигналом і сторожем напруги нема, тож у вузол витік не тече.",
                           size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "buffer.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. cable.svg — заземлений екран ↔ ведений екран (ємність)
# ════════════════════════════════════════════════════════════════════════════
def fig_cable():
    W, H = 700, 380
    f = []

    def panel(x0, title, driven):
        out = []
        midy = 150
        # джерело сигналу
        out.append(circle(x0 + 24, midy, 7, fill="#fdecea", stroke=POS, sw=2.0))
        out.append(text(x0 + 24, midy - 16, "сигнал", size=10, color=POS, anchor="middle"))
        # жила (центральна) — горизонтальна
        jx1, jx2 = x0 + 31, x0 + 250
        out.append(line(jx1, midy, jx2, midy, color=POS, sw=2.4))
        out.append(text((jx1 + jx2) / 2, midy - 10, "жила", size=10, color=POS, anchor="middle"))
        # екран — паралельна лінія нижче
        ey = midy + 46
        out.append(line(jx1, ey, jx2, ey, color=(FIELD if driven else INK), sw=2.4))
        # ємність кабелю між жилою та екраном (символічно дві ємності)
        for cxp in (x0 + 90, x0 + 190):
            out.append(line(cxp, midy, cxp, midy + 14, color=MUTED, sw=1.4))
            out.append(line(cxp - 9, midy + 14, cxp + 9, midy + 14, color=MUTED, sw=2.2))
            out.append(line(cxp - 9, midy + 20, cxp + 9, midy + 20, color=MUTED, sw=2.2))
            out.append(line(cxp, midy + 20, cxp, ey, color=MUTED, sw=1.4))
        out.append(text(x0 + 140, midy + 34, "C_каб", size=10, color=MUTED, anchor="middle"))

        if driven:
            # екран веде буфер
            btri, bin_, bout = buffer_tri(x0 + 40, ey + 56, scale=0.9, label="×1")
            out.append(line(x0 + 24, midy, x0 + 24, ey + 56, color=POS, sw=1.6))
            out.append(line(x0 + 24, ey + 56, bin_[0], bin_[1], color=POS, sw=1.6))
            out.append(btri)
            out.append(line(bout[0], bout[1], bout[0] + 14, ey + 56, color=FIELD, sw=2.0))
            out.append(line(bout[0] + 14, ey + 56, bout[0] + 14, ey, color=FIELD, sw=2.0))
            out.append(line(bout[0] + 14, ey, jx2, ey, color=FIELD, sw=2.4))
            out.append(text((jx1 + jx2) / 2 + 10, ey + 16, "екран веде буфер", size=10, color=FIELD, bold=True, anchor="middle"))
            out.append(text((jx1 + jx2) / 2, ey - 8, "обкладки рухаються РАЗОМ → ΔU = 0 → I_C = 0", size=10, color=FIELD, anchor="middle"))
        else:
            out.append(gnd((jx1 + jx2) / 2, ey + 6))
            out.append(text((jx1 + jx2) / 2 + 4, ey - 8, "екран на землі", size=10, color=INK, anchor="middle"))
            out.append(text((jx1 + jx2) / 2, ey + 44, "сигнал гойдається → C_каб тягне струм із джерела", size=10, color=NEG, anchor="middle"))

        out.append(text(x0 + 140, 60, title, size=13, bold=True,
                        color=(FIELD if driven else NEG)))
        return out

    f += panel(20, "Екран на землі: смуга зрізана", False)
    # роздільник
    f.append(line(W / 2, 80, W / 2, H - 40, color="#dfe3e8", sw=1.4, dash="5 5"))
    f += panel(360, "Ведений екран: ємності нема", True)

    f.append(text(W / 2, H - 14, "I_C = C · d(U_жила − U_екран)/dt.  Зрівняли напруги обкладок — і зарядний струм зник.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "cable.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. triax.svg — триаксіальний кабель у розрізі: три ролі трьох провідників
# ════════════════════════════════════════════════════════════════════════════
def fig_triax():
    W, H = 700, 380
    f = []
    cx, cy = 220, 195

    # три співвісні кільця
    f.append(circle(cx, cy, 130, fill="#ffffff", stroke=INK, sw=2.4))          # зовнішній екран
    f.append(circle(cx, cy, 122, fill="#f4f6f8", stroke="none", sw=0))
    f.append(circle(cx, cy, 86, fill="#eef7f0", stroke=FIELD, sw=2.4))          # guard
    f.append(circle(cx, cy, 78, fill="#eef7f0", stroke="none", sw=0))
    f.append(circle(cx, cy, 44, fill="#fdecea", stroke=POS, sw=2.4))            # ізоляція довкола жили
    f.append(circle(cx, cy, 12, fill=POS, stroke=POS, sw=1.6))                  # жила

    # підписи з виносками праворуч
    rows = [
        (cy - 96, POS,   "жила — сигнал", "високоомний вузол"),
        (cy - 10, FIELD, "внутрішній екран — GUARD", "веде буфер, на напрузі сигналу"),
        (cy + 86, INK,   "зовнішній екран — ЗЕМЛЯ", "ловить наводки, не пускає всередину"),
    ]
    lx = cx + 150
    for yy, col, t1, t2 in rows:
        f.append(circle(lx - 16, yy, 5, fill=col, stroke=col))
        f.append(text(lx, yy - 4, t1, size=12, color=col, bold=True, anchor="start"))
        f.append(text(lx, yy + 13, t2, size=11, color=MUTED, anchor="start"))

    # стрілка-виноска від жили
    f.append(line(cx, cy, cx + 9, cy, color=POS, sw=1.4))

    # пояснення «нуль вольтів / напруга є»
    body, w0, h0 = textbox(W / 2, H - 30,
                           "жила ↔ guard:  ΔU = 0  (нема витоку й ємності)\nguard ↔ земля:  ΔU є, але струм бере буфер",
                           size=11, color=INK, fill="#f4f6f8", stroke=LINE)
    f.append(body)

    f.append(text(W / 2, 34, "Триакс: три провідники — три різні роботи", size=15, bold=True))
    render(os.path.join(IMG, "triax.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. layout-ring.svg — замкнене кільце на платі: топ+бот, голий вузол, порожній вивід
# ════════════════════════════════════════════════════════════════════════════
def fig_layout_ring():
    W, H = 720, 410
    f = []

    # корпус мікросхеми (DIP/SOIC) ліворуч
    chx, chy, chw, chh = 70, 150, 120, 120
    f.append(rect(chx, chy, chw, chh, fill="#f4f6f8", stroke=INK, sw=2.0, rx=4))
    f.append(text(chx + chw / 2, chy - 10, "ОП (повторювач)", size=11, color=INK, bold=True))
    # виводи праворуч від корпусу: 3 шт, середній — високоомний +IN
    pin_y = [chy + 24, chy + 60, chy + 96]
    pin_lbl = ["вивід", "+IN (високоомний)", "вивід"]
    pin_col = [MUTED, POS, MUTED]
    for i, (py, lbl, col) in enumerate(zip(pin_y, pin_lbl, pin_col)):
        f.append(line(chx + chw, py, chx + chw + 26, py, color=col, sw=2.2))
        f.append(circle(chx + chw + 26, py, 4, fill=col, stroke=col))
    # сусідні виводи лишаємо «порожніми» — позначка
    f.append(text(chx + chw + 34, pin_y[0] + 4, "лишити порожнім", size=9, color=MUTED, anchor="start"))
    f.append(text(chx + chw + 34, pin_y[2] + 4, "лишити порожнім", size=9, color=MUTED, anchor="start"))

    # високоомний вузол-майданчик праворуч
    nodex, nodey = 470, pin_y[1]
    f.append(line(chx + chw + 26, pin_y[1], nodex - 16, nodey, color=POS, sw=2.4))
    f.append(circle(nodex, nodey, 13, fill="#fdecea", stroke=POS, sw=2.4))
    f.append(text(nodex, nodey + 4, "U", size=11, color=POS, bold=True))
    f.append(text(nodex, nodey - 22, "чутливий вузол", size=10, color=POS))

    # ЗАМКНЕНЕ кільце навколо вузла — суцільний прямокутник зі скругленням
    rgx, rgy, rgw, rgh = nodex - 70, nodey - 64, 200, 128
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="16" '
             'fill="none" stroke="%s" stroke-width="7"/>' % (rgx, rgy, rgw, rgh, FIELD))
    f.append(text(rgx + rgw - 8, rgy - 8, "GUARD (замкнене кільце)", size=11, color=FIELD, bold=True, anchor="end"))

    # підпис «з обох боків плати» — дублікат кільця штрихом нижче-правіше
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="16" '
             'fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="6 5"/>'
             % (rgx + 10, rgy + 10, rgw, rgh, FIELD))
    f.append(mtext(rgx + rgw + 20, rgy + rgh - 6, ["те саме кільце", "на звороті (bottom)"], size=9, color=FIELD, anchor="start"))

    # ведення кільця: на вихід буфера (низькоомний)
    f.append(arrow(rgx, rgy + rgh / 2, chx + chw / 2, chy + chh + 4, color=FIELD, sw=2.0))
    f.append(line(chx + chw / 2, chy + chh, chx + chw / 2, chy + chh + 4, color=FIELD, sw=2.0))
    f.append(text(chx + chw / 2, chy + chh + 22, "кільце → вихід буфера", size=10, color=FIELD, bold=True))
    f.append(text(chx + chw / 2, chy + chh + 38, "(низькоомний, на напрузі вузла)", size=9, color=MUTED))

    # знята маска — позначка під вузлом і кільцем
    body, w0, h0 = textbox(W / 2, H - 34,
                           "Маску й пасту під кільцем і вузлом ЗНЯТО — гола мідь.  Кільце замкнене, без щілин,  на обох боках.",
                           size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "layout-ring.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 6. mask-leak.svg — чому маску знімають: витік не лише в об'ємі, а ПОВЕРХНЕЮ маски
# ════════════════════════════════════════════════════════════════════════════
def fig_mask_leak():
    W, H = 700, 360
    f = []

    def stack(x0, title, masked, good):
        out = []
        basey = 220
        # підкладка FR-4
        out.append(rect(x0, basey, 240, 34, fill="#e8d9b5", stroke=MUTED, sw=1.4, rx=2))
        out.append(text(x0 + 120, basey + 22, "FR-4 (підкладка)", size=10, color=MUTED))
        # дві мідні площадки: вузол (ліво) і кільце (право)
        padw = 40
        node_x = x0 + 34
        ring_x = x0 + 240 - 34 - padw
        out.append(rect(node_x, basey - 8, padw, 8, fill=POS, stroke=POS, sw=1, rx=1))
        out.append(rect(ring_x, basey - 8, padw, 8, fill=FIELD, stroke=FIELD, sw=1, rx=1))
        out.append(text(node_x + padw / 2, basey - 14, "вузол", size=9, color=POS))
        out.append(text(ring_x + padw / 2, basey - 14, "кільце", size=9, color=FIELD))

        if masked:
            # суцільна маска поверх усього, з тонкою плівкою бруду/вологи
            out.append(rect(x0 + 2, basey - 16, 236, 8, fill="#3aa856", stroke="none", sw=0, rx=2))
            out.append(text(x0 + 120, basey - 22, "паяльна маска + флюс/волога зверху", size=9, color=NEG))
            # шлях витоку ПОВЕРХНЕЮ маски між площадками
            ly = basey - 22
            out.append(arrow(node_x + padw, ly, ring_x, ly, color=NEG, sw=2.0))
            out.append(text((node_x + padw + ring_x) / 2, ly - 6, "витік поверхнею маски", size=9, color=NEG))
        else:
            # маска ЗНЯТА над зазором — гола мідь і голий FR-4, кільце перехоплює
            out.append(text(x0 + 120, basey - 24, "маска знята — гола чиста мідь", size=9, color=FIELD))
            # витік упирається в кільце (перехоплено)
            out.append(line(node_x + padw, basey - 4, ring_x, basey - 4, color=MUTED, sw=1.4, dash="3 3"))
            out.append(arrow(node_x + padw + 4, basey - 4, ring_x - 2, basey - 4, color=FIELD, sw=2.0))
            out.append(text((node_x + padw + ring_x) / 2, basey + 2 + 14, "витік стікає в кільце, не у вузол", size=9, color=FIELD))

        out.append(text(x0 + 120, 70, title, size=12, bold=True, color=(NEG if not good else FIELD)))
        return out

    f += stack(40, "Маска лишена: вона САМА проводить", True, False)
    f.append(line(W / 2, 80, W / 2, H - 60, color="#dfe3e8", sw=1.4, dash="5 5"))
    f += stack(380, "Маска знята: кільце перехоплює витік", False, True)

    f.append(text(W / 2, H - 26, "Маска й засохлий флюс — теж скінченний опір. Їхньою поверхнею витік оминає кільце.",
                  size=11, color=MUTED))
    f.append(text(W / 2, H - 10, "Тому над вузлом і кільцем мідь лишають голою й відмивають від флюсу.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "mask-leak.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 7. configs.svg — куди вести кільце у трьох схемах: повторювач / неінв / інв
# ════════════════════════════════════════════════════════════════════════════
def fig_configs():
    W, H = 760, 360
    f = []

    def amp(x0, title, guard_to, guard_col, note):
        out = []
        cy = 150
        btri, bin_t, bout = buffer_tri(x0 + 80, cy, scale=1.0, label="")
        # символ ОП: дві вхідні лінії (+ і −)
        out.append(btri)
        out.append(text(x0 + 80 - 12, cy + 5, "−", size=14, color=NEG, bold=True))
        # +IN зверху-зліва
        out.append(line(x0 + 28, cy - 11, x0 + 80 - 23, cy - 11, color=POS, sw=2.0))
        out.append(text(x0 + 22, cy - 8, "+", size=13, color=POS, bold=True, anchor="end"))
        # −IN знизу-зліва
        out.append(line(x0 + 28, cy + 11, x0 + 80 - 23, cy + 11, color=NEG, sw=2.0))
        # вихід
        out.append(line(bout[0], cy, bout[0] + 34, cy, color=INK, sw=2.0))
        out.append(text(bout[0] + 40, cy + 4, "вихід", size=10, color=INK, anchor="start"))

        # де кільце беруть — кружок на потрібному вузлі + підпис
        out.append(text(x0 + 80, 64, title, size=12, bold=True, color=guard_col))
        body = fitbox(x0 + 8, 230, 200, 64, guard_to, size=11, fill="#eef7f0",
                      stroke=guard_col, color=INK)
        out.append(body)
        out.append(text(x0 + 108, 312, note, size=9, color=MUTED, anchor="middle"))
        return out

    f += amp(20, "Повторювач (×1)",
             "кільце → ВИХІД\n(−IN з'єднано з виходом)", FIELD,
             "вихід = напруга вузла")
    f.append(line(20 + 252, 80, 20 + 252, H - 70, color="#dfe3e8", sw=1.2, dash="5 5"))
    f += amp(20 + 252, "Неінвертувальний",
             "кільце → −IN\n(вузол подільника ЗЗ)", FIELD,
             "−IN ≈ напруга +IN, низькоомний")
    f.append(line(20 + 504, 80, 20 + 504, H - 70, color="#dfe3e8", sw=1.2, dash="5 5"))
    f += amp(20 + 504, "Інвертувальний",
             "кільце → ЗЕМЛЯ\n(+IN на землі, вузол = вірт. земля)", INK,
             "входи на ≈0 В")

    f.append(text(W / 2, 34, "Куди вести кільце: завжди на низькоомний вузол НАПРУГИ сигналу", size=14, bold=True))
    render(os.path.join(IMG, "configs.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 8. residual.svg — той самий R_leak: повна напруга ↔ залишкова напруга буфера
#    (для вставки math-guard-residual.md: звідки береться коефіцієнт послаблення)
# ════════════════════════════════════════════════════════════════════════════
def fig_residual():
    W, H = 720, 380
    f = []

    def panel(x0, driven):
        out = []
        topy, boty = 112, 248
        rx = x0 + 150          # вісь резистора
        # вузол угорі
        out.append(circle(rx, topy, 8, fill="#fdecea", stroke=POS, sw=2.2))
        out.append(text(rx, topy - 16, "вузол (сигнал)", size=11, color=POS, anchor="middle"))
        # R_leak — прямокутник між вузлом і нижнім кінцем
        out.append(line(rx, topy + 8, rx, topy + 20, color=MUTED, sw=1.8))
        out.append(rect(rx - 13, topy + 20, 26, boty - topy - 40, fill="#ffffff", stroke=MUTED, sw=1.8, rx=4))
        out.append(text(rx + 20, (topy + boty) / 2 + 4, "R_leak", size=11, color=MUTED, anchor="start"))
        out.append(line(rx, boty - 20, rx, boty, color=MUTED, sw=1.8))

        if driven:
            # нижній кінець тримає буфер на напрузі сигналу → залишок крихітний
            out.append(circle(rx, boty, 8, fill="#eef7f0", stroke=FIELD, sw=2.2))
            out.append(text(rx, boty + 22, "сторож (буфер)", size=11, color=FIELD, anchor="middle"))
            out.append(line(rx - 42, topy + 20, rx - 42, boty - 20, color=FIELD, sw=1.4))
            body, w0, h0 = textbox(x0 + 74, (topy + boty) / 2,
                                   ["U_залиш", "≈ U_os + U_сигн/A", "(мікровольти)"],
                                   size=10, color=INK, fill="#eef7f0", stroke=FIELD)
            out.append(body)
            out.append(text(x0 + 150, boty + 54, "I_залиш = U_залиш / R_leak", size=11, color=FIELD, anchor="middle"))
            out.append(text(x0 + 150, boty + 72, "→ піко-/фемтоампери", size=11, color=FIELD, bold=True, anchor="middle"))
            out.append(text(x0 + 150, 66, "Зі сторожем", size=14, bold=True, color=FIELD))
        else:
            # нижній кінець — брудна шина на повній напрузі
            out.append(line(rx - 18, boty, rx + 18, boty, color=INK, sw=2.6))
            out.append(text(rx, boty + 22, "+5 В (сусідня шина)", size=11, color=INK, anchor="middle"))
            out.append(line(rx - 42, topy + 20, rx - 42, boty - 20, color=NEG, sw=1.4))
            body, w0, h0 = textbox(x0 + 76, (topy + boty) / 2,
                                   ["U_пряма", "= 5 В", "(уся напруга шини)"],
                                   size=10, color=INK, fill="#eaf0fd", stroke=NEG)
            out.append(body)
            out.append(text(x0 + 150, boty + 54, "I_пряма = U_пряма / R_leak", size=11, color=NEG, anchor="middle"))
            out.append(text(x0 + 150, boty + 72, "→ наноампери", size=11, color=NEG, bold=True, anchor="middle"))
            out.append(text(x0 + 150, 66, "Без сторожа", size=14, bold=True, color=NEG))
        return out

    f += panel(20, False)
    f.append(line(W / 2, 86, W / 2, H - 70, color="#dfe3e8", sw=1.4, dash="5 5"))
    f += panel(380, True)

    f.append(text(W / 2, H - 14,
                  "R_leak той самий — змінилась лише напруга над ним.  G = I_пряма/I_залиш = U_пряма/U_залиш.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "residual.svg"), W, H, *f)


if __name__ == "__main__":
    fig_idea()
    fig_buffer()
    fig_cable()
    fig_triax()
    fig_layout_ring()
    fig_mask_leak()
    fig_configs()
    fig_residual()
    print("OK: 8 фігур у", IMG)
