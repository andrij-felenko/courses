# -*- coding: utf-8 -*-
"""Фігури до статті «Комутований конденсатор» (book/electronics/analog/switched-cap-filter).
Чотири фігури:
  idea.svg        — суть: резистор на кристалі поганий → конденсатор + такт = точний керований опір
  commutator.svg  — механізм: два ключі φ1/φ2 переносять пакет заряду зліва направо щотакту
  packet.svg      — звідки R = 1/(f·C): пакет ΔQ = C·ΔU, частота f → струм I = f·ΔQ
  integrator.svg  — комутований інтегратор: зріз = (C1/C2)·f_такт, задається ВІДНОШЕННЯМ
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи схем ───────────────────────────────────────────────────
def node(cx, cy, label=None, color=INK, dx=0, dy=-12, anchor="middle"):
    out = [circle(cx, cy, 3.4, fill=color, stroke=color)]
    if label:
        out.append(text(cx + dx, cy + dy, label, size=12, color=color, bold=True, anchor=anchor))
    return "".join(out)


def cap_v(cx, cy, gap=10, plen=18, label=None, color=INK, lab_side="right"):
    """Вертикальний конденсатор із центром (cx,cy): дві горизонтальні пластини.
    Повертає (svg, top_node, bot_node)."""
    out = [line(cx - plen / 2, cy - gap / 2, cx + plen / 2, cy - gap / 2, color=color, sw=2.4),
           line(cx - plen / 2, cy + gap / 2, cx + plen / 2, cy + gap / 2, color=color, sw=2.4)]
    if label:
        if lab_side == "right":
            out.append(text(cx + plen / 2 + 6, cy + 4, label, size=13, color=color, bold=True, anchor="start"))
        else:
            out.append(text(cx - plen / 2 - 6, cy + 4, label, size=13, color=color, bold=True, anchor="end"))
    return "".join(out), (cx, cy - gap / 2), (cx, cy + gap / 2)


def switch(cx, cy, length=34, on=False, label=None, color=INK, lab_dy=-14, horiz=True):
    """Ключ (розімкнений/замкнений) між двома точками; горизонтальний.
    Повертає (svg, left, right)."""
    half = length / 2
    a = (cx - half, cy)
    b = (cx + half, cy)
    out = [circle(a[0], a[1], 2.8, fill="#ffffff", stroke=color, sw=1.6),
           circle(b[0], b[1], 2.8, fill="#ffffff", stroke=color, sw=1.6)]
    if on:
        out.append(line(a[0] + 2, cy, b[0] - 2, cy, color=color, sw=2.2))
    else:
        # важіль під кутом (розімкнено)
        out.append(line(a[0] + 2, cy, a[0] + length * 0.7, cy - 12, color=color, sw=2.2))
    if label:
        out.append(text(cx, cy + lab_dy, label, size=12, color=color, bold=True))
    return "".join(out), a, b


def gnd(cx, y, label=None):
    out = [line(cx, y, cx, y + 6, color=INK, sw=1.8),
           line(cx - 11, y + 6, cx + 11, y + 6, color=INK, sw=2.3),
           line(cx - 7, y + 10, cx + 7, y + 10, color=INK, sw=2.0),
           line(cx - 3, y + 14, cx + 3, y + 14, color=INK, sw=1.8)]
    if label:
        out.append(text(cx, y + 28, label, size=11, color=MUTED))
    return "".join(out)


def opamp(cx, cy, w=58, h=64, label=None):
    """Трикутник ОП вершиною вправо. Повертає (svg, in_minus, in_plus, out)."""
    x0 = cx - w / 2
    out = ['<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#ffffff" stroke="%s" stroke-width="1.8"/>'
           % (x0, cy - h / 2, x0, cy + h / 2, cx + w / 2, cy, INK)]
    im = (x0, cy - h / 4)
    ip = (x0, cy + h / 4)
    op = (cx + w / 2, cy)
    out.append(text(x0 + 11, im[1] + 4, "−", size=15, color=NEG, bold=True))
    out.append(text(x0 + 11, ip[1] + 5, "+", size=14, color=POS, bold=True))
    if label:
        out.append(text(cx - 2, cy + 4, label, size=11, color=MUTED))
    return "".join(out), im, ip, op


# ════════════════════════════════════════════════════════════════════════════
# 1. idea.svg — суть: резистор на кристалі поганий → конденсатор+такт = точний опір
# ════════════════════════════════════════════════════════════════════════════
def fig_idea():
    W, H = 680, 320
    f = []
    f.append(text(W / 2, 34, "Як зробити «резистор» на кристалі", size=16, bold=True))

    # ліва картка — звичайний резистор: погано
    lx, ly, lw, lh = 60, 70, 250, 190
    f.append(rect(lx, ly, lw, lh, fill="#fdecea", stroke=POS, sw=2, rx=12))
    f.append(text(lx + lw / 2, ly + 28, "дифузійний резистор", size=13, bold=True, color=POS))
    # зигзаг-резистор
    rx = lx + lw / 2
    zz = ["M %.0f %.0f" % (rx, ly + 48)]
    yy = ly + 48
    amp = 16
    for i in range(6):
        nx = rx + (amp if i % 2 == 0 else -amp)
        zz.append("L %.0f %.0f" % (nx, yy + 11))
        yy += 11
    zz.append("L %.0f %.0f" % (rx, yy + 11))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(zz), INK))
    b1, _, _ = textbox(lx + lw / 2, ly + 158,
                       "абсолютний опір «гуляє» ±30 %\nвеликий R з’їдає купу площі",
                       size=11, color=INK, fill="#ffffff", stroke=POS)
    f.append(b1)

    # права картка — конденсатор + такт: добре
    gx, gy, gw, gh = 370, 70, 250, 190
    f.append(rect(gx, gy, gw, gh, fill="#eef7f0", stroke=FIELD, sw=2, rx=12))
    f.append(text(gx + gw / 2, gy + 28, "конденсатор + тактовий ключ", size=12, bold=True, color=FIELD))
    # маленький конденсатор + хвилька такту
    csvg, ct, cb = cap_v(gx + gw / 2 - 30, gy + 64, gap=12, plen=30)
    f.append(csvg)
    # хвилька такту
    clkx = gx + gw / 2 + 26
    cl = ["M %.0f %.0f" % (clkx, gy + 52)]
    step = 12
    hi, lo = gy + 52, gy + 76
    seq = [hi, hi, lo, lo, hi, hi, lo, lo]
    px = clkx
    py = seq[0]
    for s in seq[1:]:
        cl.append("L %.0f %.0f" % (px, s))
        px += step
        cl.append("L %.0f %.0f" % (px, s))
        py = s
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(cl), NEG))
    f.append(text(clkx + 40, gy + 70, "такт f", size=11, color=NEG, bold=True, anchor="start"))
    b2, _, _ = textbox(gx + gw / 2, gy + 158,
                       "опір = 1 / (f·C) — точний і керований\nточність із ВІДНОШЕННЯ ємностей",
                       size=11, color=INK, fill="#ffffff", stroke=FIELD)
    f.append(b2)

    # стрілка-перехід
    f.append(arrow(lx + lw + 6, ly + lh / 2, gx - 6, gy + gh / 2, color=INK, sw=2.6))
    f.append(text((lx + lw + gx) / 2, ly + lh / 2 - 12, "той самий опір,", size=11, color=MUTED))
    f.append(text((lx + lw + gx) / 2, ly + lh / 2 + 2, "інакше зроблений", size=11, color=MUTED))

    render(os.path.join(IMG, "idea.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. commutator.svg — механізм: два ключі по черзі переносять заряд
# ════════════════════════════════════════════════════════════════════════════
def fig_commutator():
    W, H = 700, 340
    f = []
    f.append(text(W / 2, 32, "Конденсатор між двома ключами = резистор", size=16, bold=True))

    yline = 150
    # лівий вузол A (вхід, напруга U_A)
    ax = 90
    f.append(node(ax, yline, "U_A", color=POS, dy=-16))
    f.append(line(ax, yline, ax, yline + 70, color=POS, sw=1.6))
    f.append(text(ax, yline + 92, "вхід", size=11, color=MUTED))

    # фаза φ1 (лівий ключ, замкнений — заряджаємо C від A)
    s1x = 200
    sv1, s1a, s1b = switch(s1x, yline, length=44, on=True, label="φ1", color=POS, lab_dy=-16)
    f.append(line(ax, yline, s1a[0], yline, color=POS, sw=1.8))
    f.append(sv1)

    # конденсатор посередині (плаваюча «бочка» заряду)
    cx = 350
    csvg, ct, cb = cap_v(cx, yline + 16, gap=12, plen=40, label="C", color=INK)
    f.append(csvg)
    f.append(line(s1b[0], yline, cx, yline, color=INK, sw=1.8))
    f.append(line(cx, yline, cx, ct[1], color=INK, sw=1.8))
    f.append(line(cx, cb[1], cx, yline + 70, color=INK, sw=1.8))
    f.append(gnd(cx, yline + 70))
    f.append(text(cx, yline - 30, "«відро»\nзаряду", size=11, color=MUTED) if False else
             mtext(cx, yline - 28, ["«відро»", "заряду"], size=11, color=MUTED))

    # фаза φ2 (правий ключ — виливаємо C у B)
    s2x = 500
    sv2, s2a, s2b = switch(s2x, yline, length=44, on=False, label="φ2", color=NEG, lab_dy=-16)
    f.append(line(cx, yline, s2a[0], yline, color=INK, sw=1.8))
    f.append(sv2)

    # правий вузол B (вихід, U_B)
    bx = 620
    f.append(line(s2b[0], yline, bx, yline, color=NEG, sw=1.8))
    f.append(node(bx, yline, "U_B", color=NEG, dy=-16))
    f.append(line(bx, yline, bx, yline + 70, color=NEG, sw=1.6))
    f.append(text(bx, yline + 92, "вихід", size=11, color=MUTED))

    # підпис двох фаз під схемою
    b1, _, _ = textbox(s1x, yline + 130, "φ1: C набирає заряд від A", size=11,
                       color=POS, fill="#fdecea", stroke=POS)
    f.append(b1)
    b2, _, _ = textbox(s2x, yline + 130, "φ2: C віддає заряд у B", size=11,
                       color=NEG, fill="#eaf0fd", stroke=NEG)
    f.append(b2)
    f.append(text(W / 2, H - 18,
                  "Ключі НІКОЛИ не замкнені разом — щотакту з A в B перетікає рівно один пакет заряду",
                  size=11, color=MUTED))

    render(os.path.join(IMG, "commutator.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. packet.svg — звідки R = 1/(f·C): пакет ΔQ = C·ΔU, частота f → струм
# ════════════════════════════════════════════════════════════════════════════
def fig_packet():
    W, H = 660, 330
    f = []
    f.append(text(W / 2, 32, "Чому виходить опір 1 / (f·C)", size=16, bold=True))

    # три «відерця» заряду в часі — пакети, що перетікають
    y = 120
    x0 = 90
    pitch = 150
    for i in range(3):
        bx = x0 + i * pitch
        # пакет = маленький прямокутник заряду
        f.append(rect(bx - 22, y - 18, 44, 36, fill="#eef7f0", stroke=FIELD, sw=2, rx=6))
        f.append(text(bx, y + 5, "ΔQ", size=13, color=FIELD, bold=True))
        if i < 2:
            f.append(arrow(bx + 24, y, bx + pitch - 24, y, color=INK, sw=2.2))
    f.append(text(x0 + 3 * pitch - 40, y, "…", size=20, color=INK, anchor="start"))

    # таймлайн такту під пакетами
    ty = y + 56
    f.append(line(x0 - 30, ty, x0 + 2 * pitch + 40, ty, color=MUTED, sw=1.4))
    for i in range(3):
        bx = x0 + i * pitch
        f.append(line(bx, ty - 5, bx, ty + 5, color=NEG, sw=2))
    f.append(text(x0 + pitch / 2, ty + 20, "1 такт = 1/f", size=11, color=NEG, anchor="middle"))
    f.append(text(x0 + pitch + pitch / 2, ty + 20, "1 такт = 1/f", size=11, color=NEG, anchor="middle"))

    # рамки-формули праворуч (виведення)
    fx = 470
    steps = [
        ("один пакет:", "ΔQ = C · ΔU", FIELD),
        ("за секунду f пакетів:", "I = f · ΔQ = f·C·ΔU", NEG),
        ("опір = ΔU / I:", "R = 1 / (f · C)", POS),
    ]
    sy = 96
    for cap, formula, col in steps:
        f.append(text(fx, sy, cap, size=11, color=MUTED, anchor="middle"))
        bb, w0, h0 = textbox(fx, sy + 22, formula, size=13, color=col, bold=True,
                             fill="#ffffff", stroke=col)
        f.append(bb)
        sy += 74

    f.append(text(W / 2, H - 16,
                  "Більший такт f або більший C → дрібніший «крок» опору → менший еквівалентний R",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "packet.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. integrator.svg — комутований інтегратор: зріз задає ВІДНОШЕННЯ ємностей
# ════════════════════════════════════════════════════════════════════════════
def fig_integrator():
    W, H = 700, 360
    f = []
    f.append(text(W / 2, 32, "Комутований інтегратор: «резистор» — це C1 з ключами", size=15, bold=True))

    yin = 150
    # вхід
    inx = 70
    f.append(node(inx, yin, "U_вх", color=POS, dy=-16))

    # комутований конденсатор C1 на місці вхідного резистора
    s1x = 150
    sv1, s1a, s1b = switch(s1x, yin, length=34, on=True, color=POS, lab_dy=-14, label="φ1")
    f.append(line(inx, yin, s1a[0], yin, color=POS, sw=1.8))
    f.append(sv1)
    c1x = 220
    c1svg, c1t, c1b = cap_v(c1x, yin + 14, gap=11, plen=34, label="C1", color=INK)
    f.append(c1svg)
    f.append(line(s1b[0], yin, c1x, yin, color=INK, sw=1.8))
    f.append(line(c1x, yin, c1x, c1t[1], color=INK, sw=1.8))
    f.append(line(c1x, c1b[1], c1x, yin + 64, color=INK, sw=1.8))
    f.append(gnd(c1x, yin + 64))
    s2x = 290
    sv2, s2a, s2b = switch(s2x, yin, length=34, on=False, color=NEG, lab_dy=-14, label="φ2")
    f.append(line(c1x, yin, s2a[0], yin, color=INK, sw=1.8))
    f.append(sv2)
    f.append(mtext(c1x, yin + 92, ["«резистор»", "R = 1/(f·C1)"], size=11, color=MUTED))

    # ОП
    opx = 430
    osvg, im, ip, op = opamp(opx, yin)
    f.append(osvg)
    f.append(line(s2b[0], yin, im[0], im[1], color=INK, sw=1.8))
    # вузол інвертувального входу (віртуальна земля)
    f.append(node(im[0], im[1], color=NEG))
    # + вхід на землю
    f.append(line(ip[0], ip[1], ip[0] - 18, ip[1], color=INK, sw=1.6))
    f.append(gnd(ip[0] - 18, ip[1] + 4))

    # інтегрувальний конденсатор C2 у зворотному зв'язку
    fbx0 = im[0] - 4
    fby = yin - 70
    c2x = (im[0] + op[0]) / 2
    f.append(line(im[0], im[1], im[0], fby, color=INK, sw=1.6))
    f.append(line(im[0], fby, c2x - 8, fby, color=INK, sw=1.6))
    # горизонтальний конденсатор C2
    f.append(line(c2x - 8, fby - 9, c2x - 8, fby + 9, color=INK, sw=2.4))
    f.append(line(c2x + 8, fby - 9, c2x + 8, fby + 9, color=INK, sw=2.4))
    f.append(text(c2x, fby - 16, "C2", size=13, color=INK, bold=True))
    f.append(line(c2x + 8, fby, op[0], fby, color=INK, sw=1.6))
    f.append(line(op[0], fby, op[0], op[1], color=INK, sw=1.6))

    # вихід
    f.append(line(op[0], op[1], op[0] + 50, op[1], color=FIELD, sw=1.8))
    f.append(node(op[0] + 50, op[1], "U_вих", color=FIELD, dy=-16, dx=4, anchor="start"))

    # головний підпис-висновок
    bb, w0, h0 = textbox(W / 2, H - 56,
                         "частота зрізу  f_зріз ≈ (C1 / C2) · f_такт",
                         size=14, color=POS, bold=True, fill="#fdecea", stroke=POS)
    f.append(bb)
    f.append(text(W / 2, H - 16,
                  "Залежить тільки від ВІДНОШЕННЯ C1/C2 і такту — а відношення на кристалі тримається до ~0.1 %",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "integrator.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. staircase.svg — ЧОМУ R=1/(fC) лише наближення: порційний заряд vs гладкий струм
#    (вставка math-sc-resistor): сходинки заряду зливаються в рівний потік
#    лише коли такт НАБАГАТО частіший за сигнал
# ════════════════════════════════════════════════════════════════════════════
def fig_staircase():
    W, H = 700, 360
    f = []
    f.append(text(W / 2, 30, "Чому 1/(f·C) — лише усереднення", size=16, bold=True))

    # дві панелі: ліворуч такт >> сигнал (добре), праворуч такт ~ сигнал (погано)
    import math

    def panel(ox, oy, pw, ph, n_steps, title, ok):
        g = []
        col = FIELD if ok else POS
        g.append(rect(ox, oy, pw, ph, fill=("#eef7f0" if ok else "#fdecea"),
                      stroke=col, sw=2, rx=10))
        g.append(text(ox + pw / 2, oy + 22, title, size=12, bold=True, color=col))
        # осі
        bx, by = ox + 26, oy + ph - 30          # початок координат
        ax_w, ax_h = pw - 52, ph - 78
        g.append(line(bx, by, bx + ax_w, by, color=MUTED, sw=1.4))     # вісь часу
        g.append(line(bx, by, bx, by - ax_h, color=MUTED, sw=1.4))     # вісь струму/заряду
        g.append(text(bx + ax_w, by + 14, "час", size=10, color=MUTED, anchor="end"))
        # гладкий «справжній» струм крізь резистор — синусоїда-обвідна (повільний сигнал)
        pts = []
        for k in range(ax_w + 1):
            tt = k / ax_w
            val = 0.5 + 0.42 * math.sin(2 * math.pi * 0.85 * tt)
            pts.append((bx + k, by - val * ax_h))
        g.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2" '
                 'stroke-dasharray="5 4"/>'
                 % (" L ".join("%.1f %.1f" % p for p in pts), NEG))
        # сходинки заряду: вертикальні «уколи» струму щотакту, висота ~ обвідна
        for i in range(n_steps):
            tt = (i + 0.5) / n_steps
            xx = bx + tt * ax_w
            val = 0.5 + 0.42 * math.sin(2 * math.pi * 0.85 * tt)
            g.append(line(xx, by, xx, by - val * ax_h, color=col, sw=2.4))
            g.append(line(xx - 2, by - val * ax_h, xx + 2, by - val * ax_h, color=col, sw=2.4))
        return "".join(g), (bx, by)

    p1, _ = panel(46, 60, 300, 250, 13, "такт ≫ сигнал — сходинки зливаються", True)
    f.append(p1)
    p2, _ = panel(372, 60, 300, 250, 4, "такт ≈ сигнал — видно порції", False)
    f.append(p2)

    # легенда
    f.append(line(150, H - 18, 178, H - 18, color=NEG, sw=2, dash="5 4"))
    f.append(text(184, H - 14, "струм крізь ідеальний резистор", size=10,
                  color=MUTED, anchor="start"))
    f.append(line(440, H - 18, 468, H - 18, color=FIELD, sw=2.4))
    f.append(text(474, H - 14, "пакети заряду щотакту", size=10,
                  color=MUTED, anchor="start"))
    render(os.path.join(IMG, "staircase.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 6. parasitic.svg — чутлива vs нечутлива до паразитів топологія
#    (вставка math-sc-resistor): ліворуч паразит Cp додається до сигналу;
#    праворуч 4 ключі тримають обидві пластини між сигналом і землею →
#    паразит щотакту скидається в землю, у заряд не входить
# ════════════════════════════════════════════════════════════════════════════
def fig_parasitic():
    W, H = 700, 380
    f = []
    f.append(text(W / 2, 28, "Паразитна ємність: чутлива vs нечутлива топологія", size=15, bold=True))

    # ── ліва панель: чутлива (2 ключі) ──────────────────────────────────────
    lx, ly, lw, lh = 40, 56, 300, 250
    f.append(rect(lx, ly, lw, lh, fill="#fdecea", stroke=POS, sw=2, rx=10))
    f.append(text(lx + lw / 2, ly + 22, "чутлива (2 ключі)", size=12, bold=True, color=POS))
    yl = ly + 120
    f.append(node(lx + 36, yl, "A", color=POS, dy=-14))
    sv, sa, sb = switch(lx + 96, yl, length=34, on=True, color=POS, label="φ1", lab_dy=-14)
    f.append(line(lx + 36, yl, sa[0], yl, color=POS, sw=1.8))
    f.append(sv)
    ccx = lx + 160
    csvg, ct, cb = cap_v(ccx, yl + 14, gap=11, plen=34, label="C", color=INK)
    f.append(csvg)
    f.append(line(sb[0], yl, ccx, yl, color=INK, sw=1.8))
    f.append(line(ccx, yl, ccx, ct[1], color=INK, sw=1.8))
    sv2, sa2, sb2 = switch(lx + 224, yl, length=34, on=False, color=NEG, label="φ2", lab_dy=-14)
    f.append(line(ccx, yl, sa2[0], yl, color=INK, sw=1.8))
    f.append(sv2)
    f.append(node(lx + 270, yl, "B", color=NEG, dy=-14))
    f.append(line(sb2[0], yl, lx + 270, yl, color=NEG, sw=1.8))
    # паразит від нижньої пластини: але вузол гойдається з сигналом → Cp домішує заряд
    f.append(line(ccx, cb[1], ccx, yl + 56, color=INK, sw=1.8))
    # паразитна ємність Cp на «гарячому» вузлі (верхня пластина)
    f.append(line(ct[0], ct[1], ct[0] + 40, ct[1], color=MUTED, sw=1.4, dash="3 3"))
    f.append(line(ct[0] + 40, ct[1] - 8, ct[0] + 40, ct[1] + 8, color=POS, sw=2.2))
    f.append(line(ct[0] + 48, ct[1] - 8, ct[0] + 48, ct[1] + 8, color=POS, sw=2.2))
    f.append(text(ct[0] + 44, ct[1] - 14, "Cp", size=11, color=POS, bold=True))
    f.append(gnd(ct[0] + 44, ct[1] + 10))
    f.append(gnd(ccx, yl + 56))
    b1, _, _ = textbox(lx + lw / 2, ly + lh - 28,
                       "Cp на гарячому вузлі домішує\nсвій заряд → C → C + Cp",
                       size=10, color=POS, fill="#ffffff", stroke=POS)
    f.append(b1)

    # ── права панель: нечутлива (4 ключі) ───────────────────────────────────
    gx, gy, gw, gh = 360, 56, 300, 250
    f.append(rect(gx, gy, gw, gh, fill="#eef7f0", stroke=FIELD, sw=2, rx=10))
    f.append(text(gx + gw / 2, gy + 22, "нечутлива (4 ключі)", size=12, bold=True, color=FIELD))
    yg = gy + 120
    f.append(node(gx + 28, yg, "A", color=POS, dy=-14))
    # верхня пластина: φ1→вхід, φ2→земля
    s_a, _, sab = switch(gx + 80, yg, length=28, on=True, color=POS, label="φ1", lab_dy=-13)
    f.append(line(gx + 28, yg, gx + 80 - 14, yg, color=POS, sw=1.6))
    f.append(s_a)
    ccx2 = gx + 150
    csvg2, ct2, cb2 = cap_v(ccx2, yg + 14, gap=11, plen=34, label="C", color=INK)
    f.append(csvg2)
    f.append(line(sab[0], yg, ccx2, yg, color=INK, sw=1.6))
    f.append(line(ccx2, yg, ccx2, ct2[1], color=INK, sw=1.6))
    # φ2 від верхньої пластини в землю
    f.append(line(ccx2, yg, ccx2, yg - 30, color=INK, sw=1.6))
    s_g1, _, sg1b = switch(ccx2 + 34, yg - 30, length=26, on=False, color=NEG, label="φ2", lab_dy=-12)
    f.append(line(ccx2, yg - 30, ccx2 + 34 - 13, yg - 30, color=INK, sw=1.6))
    f.append(s_g1)
    f.append(gnd(ccx2 + 34 + 13, yg - 30))
    # нижня пластина: φ1→земля, φ2→вірт.земля (вихід B)
    f.append(line(ccx2, cb2[1], ccx2, yg + 44, color=INK, sw=1.6))
    s_g2, sg2a, sg2b = switch(ccx2 - 36, yg + 44, length=26, on=True, color=POS, label="φ1", lab_dy=14)
    f.append(line(ccx2, yg + 44, ccx2 - 36 + 13, yg + 44, color=INK, sw=1.6))
    f.append(s_g2)
    f.append(gnd(ccx2 - 36 - 13, yg + 44 - 2))
    s_b, sba, _ = switch(ccx2 + 40, yg + 44, length=26, on=False, color=NEG, label="φ2", lab_dy=14)
    f.append(line(ccx2, yg + 44, ccx2 + 40 - 13, yg + 44, color=INK, sw=1.6))
    f.append(s_b)
    f.append(node(ccx2 + 40 + 26, yg + 44, "B", color=NEG, dy=-12))
    f.append(line(sba[0] if False else ccx2 + 40 + 13, yg + 44, ccx2 + 40 + 26, yg + 44, color=NEG, sw=1.6))
    b2, _, _ = textbox(gx + gw / 2, gy + gh - 28,
                       "обидві пластини ходять лише\nміж сигналом і землею →\nпаразит скидається в землю",
                       size=10, color=FIELD, fill="#ffffff", stroke=FIELD)
    f.append(b2)

    f.append(text(W / 2, H - 14,
                  "Нечутлива топологія дала точність на практиці: переноситься рівно C·ΔU, без домішку паразитів",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "parasitic.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 7. maxwell-bridge.svg — задум Максвелла 1873: комутатор хитає C між батареєю
#    й гальванометром n разів/с → середній струм як крізь R = 1/(n·C)
#    (для вставки hist-maxwell-commutator.md)
# ════════════════════════════════════════════════════════════════════════════
def battery(cx, cy, label=None):
    """Гальванічний елемент (батарея): довга+коротка риски, виводи зверху/знизу."""
    out = [line(cx - 13, cy - 4, cx + 13, cy - 4, color=INK, sw=2.6),   # довга (+)
           line(cx - 7, cy + 4, cx + 7, cy + 4, color=INK, sw=1.8)]     # коротка (−)
    out.append(text(cx + 18, cy - 5, "+", size=12, color=POS, bold=True, anchor="start"))
    out.append(text(cx + 18, cy + 11, "−", size=12, color=NEG, bold=True, anchor="start"))
    if label:
        out.append(text(cx, cy + 30, label, size=11, color=MUTED))
    return "".join(out)


def galvano(cx, cy, r=18, label=None):
    """Гальванометр: коло зі стрілкою-вказівником."""
    import math
    out = [circle(cx, cy, r, fill="#ffffff", stroke=INK, sw=1.8)]
    ang = math.radians(58)
    out.append(line(cx, cy + r * 0.55, cx + r * 0.75 * math.cos(ang),
                    cy - r * 0.75 * math.sin(ang), color=NEG, sw=2.0))
    out.append(circle(cx, cy + r * 0.55, 1.8, fill=INK, stroke=INK))
    out.append(text(cx, cy + 1, "G", size=13, color=MUTED, bold=True))
    if label:
        out.append(text(cx, cy + r + 16, label, size=11, color=MUTED))
    return "".join(out)


def fig_maxwell():
    W, H = 700, 360
    f = []
    f.append(text(W / 2, 30, "Задум Максвелла (1873): перемикач робить із конденсатора резистор",
                  size=15, bold=True))

    yline = 170
    cx = 350           # центр — конденсатор
    topx_b = 200       # ліворуч — гілка до батареї (заряд)
    topx_g = 500       # праворуч — гілка до гальванометра (розряд)

    # полюс комутатора над конденсатором
    px, py = cx, yline - 54
    f.append(node(px, py, color=INK))

    # конденсатор під полюсом
    csvg, ct, cb = cap_v(cx, yline, gap=13, plen=42, label="C", color=INK)
    f.append(csvg)
    f.append(line(px, py, ct[0], ct[1], color=INK, sw=1.8))
    f.append(line(cx, cb[1], cx, yline + 52, color=INK, sw=1.8))
    f.append(gnd(cx, yline + 52))
    f.append(mtext(cx + 66, yline + 4, ["заряд", "Q = C·U"], size=11, color=MUTED, anchor="start"))

    # дві контактні точки комутатора
    cLx, cRx = px - 70, px + 70
    cy_contact = py - 26
    f.append(circle(cLx, cy_contact, 3.0, fill="#ffffff", stroke=POS, sw=1.8))
    f.append(circle(cRx, cy_contact, 3.0, fill="#ffffff", stroke=NEG, sw=1.8))
    # важіль перекинутий ЛІВОРУЧ (заряд від батареї); пунктир — друге положення
    f.append(line(px, py, cLx, cy_contact, color=POS, sw=2.6))
    f.append(line(px, py, cRx, cy_contact, color=NEG, sw=1.6, dash="4 4"))
    f.append(text(px, py + 18, "комутатор", size=11, color=MUTED))

    # ліва гілка: контакт → батарея
    f.append(line(cLx, cy_contact, cLx, cy_contact - 24, color=POS, sw=1.8))
    f.append(line(cLx, cy_contact - 24, topx_b, cy_contact - 24, color=POS, sw=1.8))
    f.append(line(topx_b, cy_contact - 24, topx_b, yline + 12, color=POS, sw=1.8))
    f.append(battery(topx_b, yline + 28, "батарея U"))
    f.append(line(topx_b, yline + 40, topx_b, yline + 52, color=INK, sw=1.8))
    f.append(gnd(topx_b, yline + 52))

    # права гілка: контакт → гальванометр
    f.append(line(cRx, cy_contact, cRx, cy_contact - 24, color=NEG, sw=1.8))
    f.append(line(cRx, cy_contact - 24, topx_g, cy_contact - 24, color=NEG, sw=1.8))
    f.append(line(topx_g, cy_contact - 24, topx_g, yline + 6, color=NEG, sw=1.8))
    f.append(galvano(topx_g, yline + 26, label="середній струм"))
    f.append(line(topx_g, yline + 44, topx_g, yline + 52, color=INK, sw=1.8))
    f.append(gnd(topx_g, yline + 52))

    # підпис фаз
    f.append(text(topx_b, cy_contact - 34, "положення 1: C набирає заряд", size=10,
                  color=POS, anchor="middle"))
    f.append(text(topx_g, cy_contact - 34, "положення 2: C віддає в G", size=10,
                  color=NEG, anchor="middle"))

    # головний висновок
    bb, w0, h0 = textbox(W / 2, H - 52,
                         "перекидаємо n разів/с  →  I = n·C·U  →  опір  R = 1 / (n·C)",
                         size=13, color=FIELD, bold=True, fill="#eef7f0", stroke=FIELD)
    f.append(bb)
    f.append(text(W / 2, H - 16,
                  "Гальванометр бачить рівний струм — конденсатор «прикинувся» резистором; так Максвелл міряв ємність",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "maxwell-bridge.svg"), W, H, *f)


if __name__ == "__main__":
    fig_idea()
    fig_commutator()
    fig_packet()
    fig_integrator()
    fig_staircase()
    fig_parasitic()
    fig_maxwell()
    print("OK: 7 фігур у", IMG)
