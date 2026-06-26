# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: міст із чотирьох діодів, шляхи струму на двох півхвилях ─────────
def fig_bridge_paths():
    W, H = 760, 380
    frags = []

    # геометрія ромба-моста (вузли A зліва, B справа, top, bot)
    cx, cy = 250, 200
    half = 95
    A = (cx - half, cy)          # лівий вузол — від трансформатора (~)
    B = (cx + half, cy)          # правий вузол — від трансформатора (~)
    T = (cx, cy - half)          # верх — «+»
    BT = (cx, cy + half)         # низ — «−»

    def diode(p1, p2, lit, label):
        # трикутник-діод посередині ребра p1->p2 (вістря в напрямку провідності, до p2)
        x1, y1 = p1; x2, y2 = p2
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
        px, py = -uy, ux
        s = 13
        # вістря — у точку p2 (напрямок струму через діод)
        tip = (mx + ux * s, my + uy * s)
        b1 = (mx - ux * s + px * s, my - uy * s + py * s)
        b2 = (mx - ux * s - px * s, my - uy * s - py * s)
        col = POS if lit else MUTED
        wir = 3.0 if lit else 1.6
        out = line(x1, y1, x2, y2, color=(INK if lit else "#bbbbbb"), sw=wir)
        out += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.5"/>'
                % (tip[0], tip[1], b1[0], b1[1], b2[0], b2[1], (FILL if not lit else "#fdecea"), col))
        # планка-катод
        bx, by = mx + ux * s, my + uy * s
        out += line(bx + px * s, by + py * s, bx - px * s, by - py * s, color=col, sw=2.2)
        out += text(mx + px * 22, my + py * 22 + 4, label, size=13, color=col, bold=lit)
        return out

    # додатна півхвиля: струм A(+)→через D1 до T, повертається B через D...
    # Класична розкладка: верхні два діоди вістрям до T (катоди на «+»),
    # нижні два вістрям від BT (аноди на «−»).
    # Провідна пара на цій півхвилі: A→T (лівий-верхній), BT→B (правий-нижній) — підсвічуємо.
    frags.append(diode(A, T, True,  "D1"))    # A → T  (горить)
    frags.append(diode(B, T, False, "D2"))    # B → T
    frags.append(diode(BT, A, False, "D3"))   # BT → A
    frags.append(diode(BT, B, True,  "D4"))   # BT → B (горить)

    # вузли
    for (px, py) in (A, B, T, BT):
        frags.append(circle(px, py, 4, fill=INK, stroke=INK))

    # підписи полюсів виходу
    frags.append(text(T[0], T[1] - 16, "+ вихід", size=13, color=POS, bold=True))
    frags.append(text(BT[0], BT[1] + 24, "− вихід", size=13, color=NEG, bold=True))

    # трансформатор зліва: вторинна обмотка ~ з двома виводами до A і до B.
    # Верхній вивід → A (лівий вузол). Нижній вивід обводимо знизу до B (правого вузла).
    tx = 70
    coil_top, coil_bot = A[1] - 26, A[1] + 26
    # символ обмотки (овал)
    frags.append('<ellipse cx="%d" cy="%d" rx="14" ry="40" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (tx, A[1], FILL, INK))
    frags.append(text(tx, A[1] + 5, "~", size=24, color=NEG, anchor="middle", bold=True))
    frags.append(text(tx, A[1] - 50, "вторинна", size=11, color=MUTED))
    # верхній вивід обмотки → лівий вузол A
    frags.append(line(tx + 14, coil_top, A[0], coil_top, color=INK, sw=2))
    frags.append(line(A[0], coil_top, A[0], A[1], color=INK, sw=2))
    # нижній вивід обмотки → вниз, попід мостом, угору до правого вузла B
    yb = 340
    frags.append(line(tx + 14, coil_bot, tx + 14, yb, color=INK, sw=2))
    frags.append(line(tx + 14, yb, B[0] + 30, yb, color=INK, sw=2))
    frags.append(line(B[0] + 30, yb, B[0] + 30, B[1], color=INK, sw=2))
    frags.append(line(B[0] + 30, B[1], B[0], B[1], color=INK, sw=2))
    # позначка A і B
    frags.append(text(A[0] - 12, A[1] - 8, "A", size=12, color=NEG, bold=True))
    frags.append(text(B[0] + 14, B[1] - 8, "B", size=12, color=NEG, bold=True))

    # вихід праворуч: від T і BT до навантаження
    rx = 560
    frags.append(line(T[0], T[1], rx + 40, T[1], color=INK, sw=2))
    frags.append(line(rx + 40, T[1], rx + 40, T[1] + 40, color=INK, sw=2))
    frags.append(line(BT[0], BT[1], rx + 40, BT[1], color=INK, sw=2))
    frags.append(line(rx + 40, BT[1], rx + 40, BT[1] - 40, color=INK, sw=2))
    # навантаження (резистор-блок)
    frags.append(rect(rx + 20, T[1] + 40, 40, BT[1] - T[1] - 80, fill=FILL, stroke=INK, sw=1.8))
    frags.append(text(rx + 40, cy + 4, "R", size=15, color=INK, bold=True))
    frags.append(text(rx + 40, cy + 60, "навантаження", size=11, color=MUTED))

    # напис умови півхвилі — праворуч угорі, щоб не перетинати дроти
    box, bw, bh = textbox(560, 70, ["Півхвиля: A додатна, B від'ємна",
                                    "→ струм біжить через D1 і D4"],
                          size=12, fill="#eef7ee", stroke=FIELD, color="#1e6b3a")
    frags.append(box)

    frags.append(text(W / 2, 30, "Міст Гретца: чотири діоди, дві провідні пари", size=16, bold=True))
    render(os.path.join(OUT, 'bridge-paths.svg'), W, H, *frags)


# ── Фігура 2: півхвильове vs двопівхвильове vs згладжене ──────────────────────
def fig_waveforms():
    W, H = 760, 480
    frags = [text(W / 2, 28, "Що бачить навантаження: пів- проти двопівхвильового", size=16, bold=True)]

    x0, x1 = 70, 720
    panels = [
        ("Двопівперіодний (міст) до конденсатора:", 130, "fullwave"),
        ("Двопівперіодний + конденсатор: пульсація замість провалів", 280, "smoothed"),
        ("Для порівняння — однопівперіодний (один діод): пів періоду глухо", 430, "halfwave"),
    ]
    span = 88   # піврозмах графіка
    cycles = 2.0

    for caption, ymid, kind in panels:
        frags.append(text(x0, ymid - span - 6, caption, size=12, color=MUTED, anchor="start"))
        # вісь часу
        frags.append(line(x0, ymid, x1, ymid, color="#cccccc", sw=1.2))
        N = 400
        pts = []
        for i in range(N + 1):
            t = i / N * cycles
            s = math.sin(2 * math.pi * t)
            if kind == "fullwave":
                v = abs(s)
            elif kind == "halfwave":
                v = max(0.0, s)
            else:
                v = abs(s)
            xx = x0 + (x1 - x0) * i / N
            yy = ymid - v * span * 0.92
            pts.append((xx, yy))
        path = "M " + " L ".join("%.1f,%.1f" % p for p in pts)
        frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path, INK))

        if kind == "smoothed":
            # огинаюча конденсатора: тримає пік, спадає по прямій до наступного піка
            ep = []
            peak = span * 0.92
            droop = 0.30   # глибина пульсації (частка піка)
            for i in range(N + 1):
                t = i / N * cycles
                # двопівперіод: піки на t = 0.25, 0.75, 1.25, 1.75 (період пульсації = 0.5)
                phase = (t + 0.25) % 0.5      # 0 у піку
                env = peak * (1 - droop * (phase / 0.5))
                xx = x0 + (x1 - x0) * i / N
                yy = ymid - env
                ep.append((xx, yy))
            pe = "M " + " L ".join("%.1f,%.1f" % p for p in ep)
            frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pe, POS))
            # стрілка-пульсація
            frags.append(line(x0 + 250, ymid - peak, x0 + 250, ymid - peak * (1 - droop),
                              color=NEG, sw=1.4, dash="3,3"))
            frags.append(text(x0 + 262, ymid - peak + 14, "пульсація", size=11, color=NEG, anchor="start"))

        if kind == "halfwave":
            frags.append(text(x0 + 330, ymid + 22, "пів періоду — нуль", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'waveforms.svg'), W, H, *frags)


# ── Фігура 3: геометрія пульсації на конденсаторі (розрахунок) ────────────────
def fig_ripple():
    W, H = 720, 360
    frags = [text(W / 2, 28, "Звідки береться формула пульсації", size=16, bold=True)]

    x0, x1 = 80, 660
    ytop, ybot = 80, 250
    # рівень піка й рівень мінімуму
    Vp = ytop + 10
    dV = 60
    Vmin = Vp + dV
    frags.append(line(x0, Vp, x1, Vp, color="#cccccc", sw=1, dash="4,4"))
    frags.append(line(x0, Vmin, x1, Vmin, color="#cccccc", sw=1, dash="4,4"))
    frags.append(text(x0 - 8, Vp + 4, "Vпік", size=12, color=MUTED, anchor="end"))
    frags.append(text(x0 - 8, Vmin + 4, "Vмін", size=12, color=MUTED, anchor="end"))

    # пилоподібна напруга на конденсаторі: швидкий заряд до піка, повільний розряд по прямій
    period = (x1 - x0) / 3.0
    pts = []
    x = x0
    pts.append((x, Vmin))
    for k in range(3):
        xs = x0 + k * period
        # стрімкий фронт заряду
        pts.append((xs + 6, Vp))
        # лінійний спад розряду (нахил = I/C)
        pts.append((xs + period, Vmin))
    path = "M " + " L ".join("%.1f,%.1f" % p for p in pts)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path, POS))

    # синусоїдні «горбки» зверху — джерело підзарядки (бліда)
    N = 240
    sp = []
    for i in range(N + 1):
        t = i / N * 3.0
        v = abs(math.sin(math.pi * t))
        xx = x0 + (x1 - x0) * i / N
        yy = Vp - (Vp - (ytop - 30)) * 0 + (Vmin - Vp) * 0  # лишаємо біля піка
        yy = Vp - v * 0  # не малюємо — нижче окремо
    # натомість покажемо двопівперіодну криву, що «годує» пік
    sp = []
    for i in range(N + 1):
        t = i / N * 3.0
        v = abs(math.sin(math.pi * t))
        xx = x0 + (x1 - x0) * i / N
        yy = Vmin - v * (dV + 22)
        sp.append((xx, yy))
    spath = "M " + " L ".join("%.1f,%.1f" % p for p in sp)
    frags.append('<path d="%s" fill="none" stroke="#bcd8c4" stroke-width="1.6"/>' % spath)

    # позначка ΔV (пульсація)
    xa = x0 + period * 1.5
    frags.append(line(xa, Vp, xa, Vmin, color=NEG, sw=1.6))
    frags.append(line(xa - 4, Vp, xa + 4, Vp, color=NEG, sw=1.6))
    frags.append(line(xa - 4, Vmin, xa + 4, Vmin, color=NEG, sw=1.6))
    frags.append(text(xa + 8, (Vp + Vmin) / 2 + 4, "ΔV", size=14, color=NEG, anchor="start", bold=True))

    # позначка часу розряду T
    frags.append(line(x0 + period + 6, Vmin + 16, x0 + 2 * period, Vmin + 16, color=INK, sw=1.4))
    frags.append(line(x0 + period + 6, Vmin + 12, x0 + period + 6, Vmin + 20, color=INK, sw=1.4))
    frags.append(line(x0 + 2 * period, Vmin + 12, x0 + 2 * period, Vmin + 20, color=INK, sw=1.4))
    frags.append(text(x0 + 1.5 * period, Vmin + 32, "T ≈ 1 / (2·f)", size=12, color=INK))

    # формула в рамці
    box, bw, bh = textbox(W / 2, 320,
                          "розряд лінійний:  ΔV = I·T / C = I / (2·f·C)",
                          size=14, fill=FILL, stroke=INK, bold=True)
    frags.append(box)

    render(os.path.join(OUT, 'ripple.svg'), W, H, *frags)


# ── Фігура 4 (comp): чотири виводи готового моста і як їх упізнати ─────────────
def fig_module_pinout():
    W, H = 760, 380
    frags = [text(W / 2, 28, "Готовий міст: чотири виводи й значки на корпусі", size=16, bold=True)]

    # ── зліва: корпус-«цеглинка» з чотирма виводами в ряд ─────────────────────
    bx, by, bw, bh = 90, 90, 200, 150
    frags.append(rect(bx, by, bw, bh, fill=FILL, stroke=INK, sw=2, rx=10))
    frags.append(text(bx + bw / 2, by + 34, "готовий", size=13, color=MUTED))
    frags.append(text(bx + bw / 2, by + 52, "міст", size=13, color=MUTED))
    # зрізаний кут — ключ корпусу (біля «+»)
    frags.append('<path d="M%d,%d L%d,%d L%d,%d Z" fill="#fdecea" stroke="%s" stroke-width="1.5"/>'
                 % (bx, by, bx + 26, by, bx, by + 26, POS))
    # чотири виводи знизу, підписані за типовим порядком ~ + ~ −
    labels = [("~", NEG), ("+", POS), ("~", NEG), ("−", NEG)]
    n = len(labels)
    for i, (lab, col) in enumerate(labels):
        px = bx + bw * (i + 0.5) / n
        frags.append(line(px, by + bh, px, by + bh + 34, color=INK, sw=2.4))
        frags.append(text(px, by + bh + 52, lab, size=20, color=col, bold=True))
    frags.append(text(bx + bw / 2, by + bh + 78, "позначки штампують на корпусі", size=11, color=MUTED))
    frags.append(text(bx + 14, by + bh + 100, "зрізаний кут / + поряд", size=10, color=POS, anchor="start"))

    # ── праворуч: правило впізнавання у рамці ─────────────────────────────────
    box, bw2, bh2 = textbox(560, 130,
                            ["Як читати виводи:",
                             "•  два «~» — вхід змінної (байдуже",
                             "    який куди, полярності немає)",
                             "•  «+» і «−» — постійний вихід",
                             "•  ключ-кут / скіс позначає «+»"],
                            size=12.5, fill="#eef7ee", stroke=FIELD, color="#1e6b3a")
    frags.append(box)
    box2, _, _ = textbox(560, 270,
                         ["Пастка: переплутати «~» і «+/−».",
                          "Змінну — на пару «~»; вихід беруть",
                          "з «+»/«−». Подаси мережу на «+/−»",
                          "— міст у коротке, дим."],
                         size=12.5, fill="#fdecea", stroke=POS, color="#8a1f14")
    frags.append(box2)

    render(os.path.join(OUT, 'module-pinout.svg'), W, H, *frags)


# ── Фігура 5 (comp): родини корпусів за струмом і тепловідводом ────────────────
def fig_package_ladder():
    W, H = 760, 360
    frags = [text(W / 2, 28, "Корпуси моста: від дрібного SMD до плити на радіатор", size=16, bold=True)]

    # горизонтальна вісь струму
    ax0, ax1, ay = 70, 690, 300
    frags.append(line(ax0, ay, ax1, ay, color=INK, sw=1.6))
    frags.append(arrow(ax1 - 2, ay, ax1 + 18, ay, color=INK))
    frags.append(text(ax1 + 6, ay + 22, "робочий струм →", size=12, color=MUTED, anchor="end"))

    # сходинки: (підпис, частка струму 0..1, висота прямокутника)
    steps = [
        ("SMD-мінімісток", 0.10, 26, "частки А\nна платі"),
        ("круглий / inline", 0.30, 40, "до ~1 А\nбез радіатора"),
        ("KBP плаский", 0.52, 56, "1–4 А\nмідь плати гріє"),
        ("KBU / GBU", 0.78, 86, "5–25 А\nотвір під радіатор"),
    ]
    for lab, fx, ph, note in steps:
        cx = ax0 + (ax1 - ax0 - 60) * fx + 30
        pw = 34 + ph * 0.5
        x = cx - pw / 2
        y = ay - ph
        frags.append(rect(x, y, pw, ph, fill="#eef2f7", stroke=INK, sw=1.8, rx=4))
        # отвір під гвинт у великих
        if ph >= 80:
            frags.append(circle(cx, y + 12, 4, fill=BG, stroke=INK, sw=1.4))
        frags.append(text(cx, ay + 20, lab, size=12, color=INK, bold=True))
        for j, ln in enumerate(note.split("\n")):
            frags.append(text(cx, ay + 38 + j * 14, ln, size=10.5, color=MUTED))

    # підпис тенденції згори
    box, _, _ = textbox(W / 2, 78,
                        "більший струм → більший корпус → більше тепла → радіатор",
                        size=12.5, fill=FILL, stroke=INK)
    frags.append(box)
    render(os.path.join(OUT, 'package-ladder.svg'), W, H, *frags)


# ── Фігура 6 (comp): куди йде тепло ≈2·Vf·I і ланцюг тепловідводу ──────────────
def fig_thermal_path():
    W, H = 760, 340
    frags = [text(W / 2, 28, "Тепло в мості: ≈2·Vf·I і шлях до повітря", size=16, bold=True)]

    # ланцюг блоків: перехід → корпус → радіатор → повітря
    blocks = [
        ("перехід\n(кремній)", "#fdecea", POS),
        ("корпус\nмоста", "#eef2f7", INK),
        ("радіатор", "#eef2f7", INK),
        ("повітря", "#eef7ee", FIELD),
    ]
    bw, bh = 120, 64
    gap = 56
    total = len(blocks) * bw + (len(blocks) - 1) * gap
    x = (W - total) / 2
    cy = 150
    centers = []
    for lab, fill, col in blocks:
        frags.append(rect(x, cy - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.8, rx=8))
        for j, ln in enumerate(lab.split("\n")):
            frags.append(text(x + bw / 2, cy - 4 + j * 16, ln, size=12.5, color=col, bold=(j == 0)))
        centers.append(x + bw / 2)
        x += bw + gap
    # стрілки тепла між блоками + підписи теплових опорів
    rths = ["Rθ(j-c)", "Rθ(c-s)", "Rθ(s-a)"]
    for i in range(len(blocks) - 1):
        x1 = centers[i] + bw / 2
        x2 = centers[i + 1] - bw / 2
        frags.append(arrow(x1, cy, x2, cy, color=POS, sw=2.4))
        frags.append(text((x1 + x2) / 2, cy - 18, rths[i], size=11, color=MUTED))

    # джерело тепла зверху
    box, _, _ = textbox(centers[0], 70,
                        ["потужність втрат:", "P ≈ 2 · Vf · I"],
                        size=12.5, fill="#fdecea", stroke=POS, color="#8a1f14", bold=True)
    frags.append(box)
    frags.append(line(centers[0], 96, centers[0], cy - bh / 2, color=POS, sw=1.6, dash="4,3"))

    # підсумок знизу
    box2, _, _ = textbox(W / 2, 280,
                         "немає радіатора → тепло впирається в корпус → перехід перегрівається",
                         size=12.5, fill=FILL, stroke=INK)
    frags.append(box2)
    render(os.path.join(OUT, 'thermal-path.svg'), W, H, *frags)


# ── Фігура 7 (hist): пріоритет проти назви на осі часу ────────────────────────
def fig_priority_timeline():
    W, H = 760, 380
    frags = [text(W / 2, 28, "Пріоритет і назва моста на осі часу", size=16, bold=True)]

    # вісь часу 1893..1900
    x0, x1 = 90, 660
    y = 185
    t0, t1 = 1893, 1900

    def X(year):
        return x0 + (x1 - x0) * (year - t0) / (t1 - t0)

    frags.append(line(x0 - 10, y, x1 + 20, y, color=INK, sw=2))
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                 % (x1 + 20, y, x1 + 10, y - 5, x1 + 10, y + 5, INK))
    for yr in range(t0, t1 + 1):
        xx = X(yr)
        frags.append(line(xx, y - 4, xx, y + 4, color=MUTED, sw=1.2))
        frags.append(text(xx, y + 19, str(yr), size=10, color=MUTED))

    def event(year, up, lines, color, dashed=False):
        xx = X(year)
        bh = len(lines) * 11 * 1.3 + 18
        stem = 40
        if up:
            boxcy = y - stem - bh / 2
            yend = y - stem
        else:
            boxcy = y + stem + bh / 2
            yend = y + stem
        out = line(xx, y, xx, yend, color=color, sw=1.8, dash="4,3" if dashed else None)
        out += circle(xx, y, 4.5, fill=color, stroke=color)
        fill = ("#fdecea" if color == POS else "#eaf0fd" if color == NEG else FILL)
        box, bw, _ = textbox(xx, boxcy, "\n".join(lines), size=11,
                             fill=fill, stroke=color, color=INK)
        out += box
        return out

    # Поллак — пріоритет (червоний, угору)
    frags.append(event(1895, True,
                       ["Поллак: ПАТЕНТ", "міст, Британія № 24398", "(+ Німеччина 1896)"], POS))
    # Гретц — публікація (синій, униз)
    frags.append(event(1897, False,
                       ["Гретц: публікація", "ETZ, 22 лип. 1897", "→ назва закріпиться"], NEG))
    # Гретцова неперевірена заява (~1893, сірий пунктир, угору)
    frags.append(event(1893, True,
                       ["Гретц: «випробував»", "лише власне слово,", "без патенту — не доказ"],
                       MUTED, dashed=True))

    cap, _, _ = textbox(W / 2, 348,
                        "Пріоритет — Поллаків (патент).   Назва — Гретцова (популяризація).",
                        size=12.5, fill=FILL, stroke=INK, bold=True)
    frags.append(cap)
    render(os.path.join(OUT, 'priority-timeline.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_bridge_paths()
    fig_waveforms()
    fig_ripple()
    fig_module_pinout()
    fig_package_ladder()
    fig_thermal_path()
    fig_priority_timeline()
    print("ok")
