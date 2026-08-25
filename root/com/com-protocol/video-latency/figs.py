# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── glass-to-glass: ланцюг кроків, аналог короткий, цифра з кодеком ────────────
# Ідея: затримка — це сума ланок. В аналозі ланцюг короткий; цифра вставляє
# дві ненажерливі ланки (кодек до передачі й декодер після) + буфери.
def fig_glass_to_glass():
    W, H = 760, 300
    p = []
    bw, bh, step = 96, 46, 110
    x0 = 40

    # верхній ряд — аналог
    ya = 95
    p.append(text(x0, ya - 42, "аналог  ≈ 8–40 мс", size=13, color=FIELD, bold=True, anchor="start"))
    analog = ["сенсор\n(експоз.+\nзчитування)", "передача\n(радіо)", "екран"]
    cx = x0
    prev = None
    for lab in analog:
        p.append(fitbox(cx, ya - bh / 2, bw, bh, lab, size=10, fill="#eafaf0", stroke=INK, sw=1.4, bold=False))
        if prev is not None:
            p.append(arrow(prev, ya, cx, ya, color=LINE, sw=1.6))
        prev = cx + bw
        cx += step
    p.append(text(prev + 10, ya, "→ скло", size=11, color=MUTED, anchor="start"))

    # нижній ряд — цифра (дві зайві ланки виділено гарячим)
    yd = 215
    p.append(text(x0, yd - 52, "цифра  ≈ 70–130 мс", size=13, color=POS, bold=True, anchor="start"))
    digital = [
        ("сенсор", "#eafaf0", False),
        ("КОДЕК\n(стиснення)", "#fdecea", True),
        ("передача", FILL, False),
        ("ДЕКОДЕР\n+ буфер", "#fdecea", True),
        ("екран", "#eafaf0", False),
    ]
    bw2, step2 = 92, 138
    cx = x0
    prev = None
    for lab, fill, hot in digital:
        col = POS if hot else INK
        p.append(fitbox(cx, yd - bh / 2, bw2, bh, lab, size=10, fill=fill, stroke=(POS if hot else INK),
                        sw=(1.8 if hot else 1.4), bold=hot, color=col))
        if prev is not None:
            p.append(arrow(prev, yd, cx, yd, color=LINE, sw=1.6))
        prev = cx + bw2
        cx += step2
    p.append(text((x0 + prev) / 2, yd + 48, "дві зайві ланки кодека + буфери = десятки зайвих мс",
                  size=11, color=POS))

    render(os.path.join(OUT, "glass-to-glass.svg"), W, H, *p,
           title="Затримка «скло-до-скла» — сума ланок; цифра додає кодек і буфери")


# ── flying-the-past: на екрані апарат у минулому, насправді далі по курсу ──────
# Ідея: поки кадр зняли/передали/показали, апарат уже зрушив; керуєш по тому,
# де він БУВ, а не де Є — звідси перекерування й розгойдування.
def fig_flying_the_past():
    W, H = 720, 280
    p = []
    # траєкторія
    y = 150
    p.append(line(60, y, 660, y, color=MUTED, sw=1.4, dash="5 5"))
    p.append(arrow(620, y, 670, y, color=MUTED, sw=1.6))
    p.append(text(670, y + 4, "курс", size=11, color=MUTED, anchor="start"))

    # позиція «на екрані» (минуле, сіре)
    xg = 250
    p.append(circle(xg, y, 16, fill="#e9ecef", stroke=MUTED, sw=2))
    p.append(text(xg, y - 30, "на екрані", size=12, color=MUTED, bold=True))
    p.append(text(xg, y + 38, "(де БУВ)", size=11, color=MUTED))

    # справжня позиція (далі, синій)
    xr = 470
    p.append(circle(xr, y, 16, fill="#eaf0fd", stroke=NEG, sw=2.4))
    p.append(text(xr, y - 30, "насправді", size=12, color=NEG, bold=True))
    p.append(text(xr, y + 38, "(де Є)", size=11, color=NEG))

    # розрив = пройдено за затримку
    p.append(line(xg, y - 52, xg, y - 44, color=INK, sw=1))
    p.append(line(xr, y - 52, xr, y - 44, color=INK, sw=1))
    p.append(line(xg, y - 48, xr, y - 48, color=POS, sw=1.6))
    p.append(text((xg + xr) / 2, y - 56, "за 100 мс @ 20 м/с ≈ 2 м наосліп", size=12, color=POS, bold=True))

    # підпис унизу — перекерування
    p.append(text(W / 2, 248, "пілот виправляє застаріле → апарат проскакує → розгойдування",
                  size=12, color=POS))

    render(os.path.join(OUT, "flying-the-past.svg"), W, H, *p,
           title="Керуєш по застарілій картинці: апарат уже далі, ніж на екрані")


# ── loop-delay: петля бачу→вирішую→дію; затримка на «бачу» розгойдує ──────────
# Ідея: керування — замкнена петля; затримка відео сидить на ланці «бачу».
# Мала — відхилення стихає; велика — кожне виправлення спізнюється, петля росте.
def fig_loop_delay():
    W, H = 740, 360
    p = []
    # петля з трьох блоків
    cx, cy, r = 200, 150, 92
    nodes = [("бачу", -90), ("вирішую", 30), ("дію", 150)]
    import math as _m
    pos = {}
    for lab, ang in nodes:
        a = _m.radians(ang)
        nx, ny = cx + r * _m.cos(a), cy + r * _m.sin(a)
        pos[lab] = (nx, ny)
    # дуги-стрілки по колу
    order = ["бачу", "вирішую", "дію", "бачу"]
    for i in range(3):
        ax, ay = pos[order[i]]
        bx, by = pos[order[i + 1]]
        # трохи всередину, щоб стрілки не лізли в текст
        p.append(arrow(ax + (bx - ax) * 0.22, ay + (by - ay) * 0.22,
                       ax + (bx - ax) * 0.78, ay + (by - ay) * 0.78, color=LINE, sw=1.8))
    for lab, ang in nodes:
        nx, ny = pos[lab]
        b, w, h = textbox(nx, ny, lab, size=12, bold=True, fill=FILL)
        p.append(b)
    # позначка затримки на ланці «бачу» (праворуч від вузла, щоб не лізти в заголовок)
    sx, sy = pos["бачу"]
    p.append(text(sx + 70, sy - 6, "⏱ затримка тут", size=12, color=POS, bold=True, anchor="start"))
    p.append(line(sx + 26, sy, sx + 66, sy - 8, color=POS, sw=1.2))

    # два маленьких графіки відгуку
    def mini(ox, oy, w, h, grow, label, col):
        out = [rect(ox, oy, w, h, fill=BG, stroke=MUTED, sw=1.2)]
        out.append(line(ox, oy + h / 2, ox + w, oy + h / 2, color=MUTED, sw=1, dash="3 3"))
        pts = []
        for i in range(0, 121):
            t = i / 120.0
            env = (0.42 * _m.exp(1.5 * t)) if grow else (0.42 * _m.exp(-2.2 * t))
            val = env * _m.sin(t * 7 * _m.pi)
            if grow and abs(val) > 0.46:
                val = 0.46 if val > 0 else -0.46
            px = ox + t * w
            py = oy + h / 2 - val * h
            pts.append("%.1f,%.1f" % (px, py))
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), col))
        out.append(text(ox + w / 2, oy + h + 18, label, size=11, color=col, bold=True))
        return out

    p += mini(420, 70, 280, 90, False, "мала затримка → стихає (стійко)", FIELD)
    p += mini(420, 215, 280, 90, True, "велика затримка → розгойдується", POS)

    render(os.path.join(OUT, "loop-delay.svg"), W, H, *p,
           title="Затримка на ланці «бачу»: мала — гасне, велика — росте")


# ── budget: шкала летабельності із зонами й мітками систем ─────────────────────
# Ідея: апарат терпить затримку лише поки вона мала проти його реакції;
# є груба межа летабельності, і кожна система лягає в свою зону шкали.
def fig_budget():
    W, H = 760, 270
    p = []
    x0, x1 = 70, 700
    y = 130
    msmax = 350.0  # права межа шкали, мс

    def xof(ms):
        return x0 + (min(ms, msmax) / msmax) * (x1 - x0)

    # три зони
    zones = [(0, 60, "#e9f8ef", "летабельно", FIELD),
             (60, 150, "#fdf6e3", "на межі", "#b8860b"),
             (150, msmax, "#fdecea", "нелетабельно", POS)]
    for a, b, fill, lab, col in zones:
        p.append(rect(xof(a), y - 22, xof(b) - xof(a), 44, fill=fill, stroke=col, sw=1.4, rx=4))
        p.append(text((xof(a) + xof(b)) / 2, y - 30, lab, size=12, color=col, bold=True))

    # шкала з поділками
    p.append(line(x0, y + 40, x1, y + 40, color=INK, sw=1.6))
    for ms in [0, 50, 100, 150, 200, 250, 300]:
        xx = xof(ms)
        p.append(line(xx, y + 36, xx, y + 44, color=INK, sw=1.2))
        p.append(text(xx, y + 60, str(ms), size=10, color=MUTED))
    p.append(text(x1, y + 60, "мс", size=11, color=INK, anchor="start"))

    # мітки систем (діапазони)
    marks = [(20, 40, "аналог", FIELD, 1),
             (70, 130, "цифрове HD", "#b8860b", -1),
             (300, 350, "стрім/телефон", POS, 1)]
    for a, b, lab, col, side in marks:
        mx = (xof(a) + xof(b)) / 2
        p.append(line(xof(a), y, xof(b), y, color=col, sw=4))
        ly = y - 4 if side < 0 else y + 4
        anch = "middle"
        ty = y + 88 if side > 0 else y - 44
        # щоб не накладалось на зони, винесемо підписи систем нижче/вище акуратно
        p.append(text(mx, (y + 92) if side > 0 else (y - 44), lab, size=11, color=col, bold=True))

    render(os.path.join(OUT, "budget.svg"), W, H, *p,
           title="Бюджет летабельності: до ~50 мс «миттєво», за ~150 — майже неможливо")


# ── stage-budget: складання бюджету затримки по ланках (worked) ────────────────
# Ідея: показати, що сума ланок дає підсумок; кодек+буфер — найбільші стовпчики.
def fig_stage_budget():
    W, H = 760, 320
    p = []
    stages = [("сенсор", 18, FIELD),
              ("кодек", 22, POS),
              ("канал", 8, NEG),
              ("буфер", 25, POS),
              ("декодер", 12, "#b8860b"),
              ("екран", 12, NEG)]
    total = sum(v for _, v, _ in stages)
    bx = 80
    bw, gap = 86, 26
    base = 250
    scale = 5.2  # px на мс
    for lab, ms, col in stages:
        h = ms * scale
        p.append(rect(bx, base - h, bw, h, fill=col, stroke=INK, sw=1.2, rx=3))
        p.append(text(bx + bw / 2, base - h - 8, "%d мс" % ms, size=12, color=INK, bold=True))
        p.append(text(bx + bw / 2, base + 22, lab, size=12, color=INK))
        bx += bw + gap

    # підсумок
    p.append(line(60, base, bx - gap + 6, base, color=INK, sw=1.6))
    p.append(text(W - 40, 70, "сума ≈ %d мс" % total, size=15, color=POS, bold=True, anchor="end"))
    p.append(text(W - 40, 92, "(кодек + буфер — найбільші)", size=11, color=MUTED, anchor="end"))

    render(os.path.join(OUT, "stage-budget.svg"), W, H, *p,
           title="Бюджет затримки по ланках: усе додається, кодек і буфер з'їдають найбільше")


# ── exposure-readout: rolling shutter — рядки експонуються й зчитуються зсувом ──
# Ідея: затримка сенсора = час експозиції + час зчитування; за rolling shutter
# низ кадру готовий пізніше за верх, тож «вік» кадру залежить ще й від рядка.
def fig_exposure_readout():
    W, H = 760, 320
    p = []
    ox, oy = 90, 70          # лівий-верхній кут діаграми
    rows = 8
    rh = 26
    expo_w = 150             # ширина смуги експозиції (час)
    read_w = 60             # ширина зчитування
    shift = 18              # зсув старту рядка вниз (rolling)
    # вісь часу
    p.append(arrow(ox, oy - 18, ox + 470, oy - 18, color=INK, sw=1.6))
    p.append(text(ox + 470, oy - 24, "час →", size=12, color=INK, anchor="end"))
    p.append(text(ox - 14, oy + rows * rh / 2, "рядки", size=12, color=INK, anchor="end"))
    for r in range(rows):
        ry = oy + r * rh
        sx = ox + r * shift
        # смуга експозиції
        p.append(rect(sx, ry + 3, expo_w, rh - 8, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=2))
        # зчитування
        p.append(rect(sx + expo_w, ry + 3, read_w, rh - 8, fill="#fdecea", stroke=POS, sw=1.2, rx=2))
    # підписи
    p.append(text(ox + 70, oy + rows * rh + 22, "експозиція", size=12, color=NEG, bold=True))
    p.append(text(ox + (rows - 1) * shift + expo_w + read_w / 2, oy + rows * rh + 22,
                  "зчитування", size=12, color=POS, bold=True))
    # стрілка «вік низу більший»
    topx = ox + expo_w + read_w + 30
    boty = oy + (rows - 1) * rh + rh / 2
    p.append(text(560, oy + 10, "верхній рядок", size=11, color=MUTED, anchor="start"))
    p.append(text(560, boty, "нижній — пізніше", size=11, color=POS, anchor="start"))
    p.append(line(550, oy + 6, ox + expo_w + read_w + (0) * shift, oy + 6, color=MUTED, sw=1, dash="3 3"))
    render(os.path.join(OUT, "exposure-readout.svg"), W, H, *p,
           title="Сенсор: затримка = експозиція + зчитування; за rolling shutter низ готовий пізніше")


# ── codec-frames: I-кадр самодостатній, P спирається назад, B чекає майбутній ──
# Ідея: тип кадру задає затримку. I/P течуть уперед; B-кадр мусить дочекатися
# наступного — звідси зайва затримка, тож low-latency викидає B.
def fig_codec_frames():
    W, H = 760, 300
    p = []
    y = 120
    bw, gap = 64, 26
    seq = [("I", FIELD), ("P", NEG), ("P", NEG), ("B", POS), ("P", NEG), ("P", NEG)]
    xs = []
    x = 70
    for lab, col in seq:
        p.append(rect(x, y - 26, bw, 52, fill="#f4f6f8", stroke=col, sw=2, rx=5))
        p.append(text(x + bw / 2, y + 7, lab, size=20, color=col, bold=True))
        xs.append(x + bw / 2)
        x += bw + gap
    # залежності P → назад
    def dep(a, b, col, up):
        ya = y - 30 if up else y + 30
        midy = ya - 26 if up else ya + 26
        p.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
                 'stroke-width="1.6" marker-end="url(#arrow)"/>'
                 % (xs[a], ya, (xs[a] + xs[b]) / 2, midy, xs[b], ya, col))
    dep(1, 0, NEG, True)
    dep(2, 1, NEG, True)
    dep(4, 2, NEG, True)
    dep(5, 4, NEG, True)
    # B чекає майбутній P (вниз, гаряче)
    dep(3, 2, POS, False)
    dep(3, 4, POS, False)
    p.append(text(W / 2, y + 86, "B-кадр мусить дочекатися наступного P → зайва затримка", size=12, color=POS, bold=True))
    p.append(text(W / 2, y - 70, "I самодостатній · P спирається на минуле", size=12, color=NEG))
    render(os.path.join(OUT, "codec-frames.svg"), W, H, *p,
           title="Типи кадрів: I/P течуть уперед, B чекає майбутній — тому low-latency без B")


# ── jitter-buffer: буфер гасить ривки ціною затримки (компроміс) ──────────────
# Ідея: пакети приходять нерівно; буфер вирівнює подачу, але кожен запасений
# кадр = додана затримка. Малий буфер — менший лаг, але ривки/випадання.
def fig_jitter_buffer():
    W, H = 760, 300
    p = []
    # вхід — нерівні пакети
    yin = 80
    p.append(text(70, yin - 26, "приходять нерівно (jitter)", size=12, color=POS, anchor="start"))
    import random as _r
    _r.seed(7)
    xs = [90, 120, 138, 185, 250, 268, 300, 360, 372]
    for xx in xs:
        p.append(rect(xx, yin, 12, 18, fill="#fdecea", stroke=POS, sw=1.2, rx=2))
    p.append(arrow(70, yin + 40, 470, yin + 40, color=MUTED, sw=1.4))

    # буфер
    by = 150
    p.append(rect(150, by, 260, 40, fill="#fff8e6", stroke="#b8860b", sw=1.6, rx=6))
    p.append(text(280, by + 25, "буфер: запас кадрів", size=13, color="#b8860b", bold=True))

    # вихід — рівно
    yout = 240
    p.append(text(70, yout - 26, "віддаються рівно (плавно)", size=12, color=FIELD, anchor="start"))
    for i in range(9):
        xx = 90 + i * 42
        p.append(rect(xx, yout, 12, 18, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=2))
    p.append(arrow(70, yout + 30, 470, yout + 30, color=MUTED, sw=1.4))

    # підпис компромісу справа
    p.append(text(W - 40, 120, "більший буфер", size=12, color=INK, bold=True, anchor="end"))
    p.append(text(W - 40, 140, "→ плавніше,", size=11, color=FIELD, anchor="end"))
    p.append(text(W - 40, 158, "але більша затримка", size=11, color=POS, anchor="end"))
    render(os.path.join(OUT, "jitter-buffer.svg"), W, H, *p,
           title="Буфер вирівнює нерівний потік ціною доданої затримки")


if __name__ == "__main__":
    fig_glass_to_glass()
    fig_flying_the_past()
    fig_loop_delay()
    fig_budget()
    fig_stage_budget()
    fig_exposure_readout()
    fig_codec_frames()
    fig_jitter_buffer()
    print("done: video-latency figures ->", OUT)
