# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── divergence: два ядра, два кеші, одна лінія — копії розходяться ─────────────
# Ідея: ядро A і ядро B тримають КОПІЮ тієї самої лінії RAM. A записало нове
# значення у свій кеш — його копія стала 8, а B досі бачить стару 5. Це і є
# некогерентність: одна адреса, різні значення.

def fig_divergence():
    W, H = 740, 400
    p = []

    # RAM внизу по центру
    rx, ry, rw, rh = 250, 300, 240, 66
    p.append(rect(rx, ry, rw, rh, fill="#fdf4f4", stroke=INK, sw=1.6))
    p.append(text(rx + rw / 2, ry + 24, "головна пам'ять (RAM)", size=12, color=INK, bold=True))
    p.append(rect(rx + rw / 2 - 26, ry + 34, 52, 24, fill="#fde9e7", stroke=POS, sw=1.4, rx=4))
    p.append(text(rx + rw / 2, ry + 51, "X = 5", size=11, color=INK, bold=True))
    p.append(text(rx + rw / 2, ry + rh + 18, "стара копія лишилася тут", size=9, color=MUTED))

    def core(cx, name, val, hot):
        out = []
        # кеш
        kx, ky, kw, kh = cx - 80, 90, 160, 100
        out.append(rect(kx, ky, kw, kh, fill=("#eef4ff" if not hot else "#eafaf0"),
                        stroke=(NEG if not hot else FIELD), sw=1.8))
        out.append(text(cx, ky + 22, name, size=12.5, color=INK, bold=True))
        out.append(text(cx, ky + 38, "приватний кеш", size=9, color=MUTED))
        col = FIELD if hot else NEG
        vfill = "#eafaf0" if hot else "#eef4ff"
        out.append(rect(cx - 30, ky + 52, 60, 30, fill=vfill, stroke=col, sw=1.6, rx=4))
        out.append(text(cx, ky + 72, "X = %d" % val, size=12, color=INK, bold=True))
        # лінія до RAM
        out.append(line(cx, ky + kh, cx, ry, color="#c7ccd2", sw=1.4, dash="4 4"))
        return out

    p += core(180, "ядро A", 8, True)
    p += core(560, "ядро B", 5, False)

    # підпис-стан над ядром A
    p.append(text(180, 66, "щойно записало X = 8", size=10, color=FIELD, bold=True))
    p.append(text(560, 66, "досі читає застаріле X = 5", size=10, color=POS, bold=True))

    # висновок посередині
    b = fitbox(300, 120, 140, 74,
               "Одна адреса X —\nтри РІЗНІ значення\nводночас.\nСистема некогерентна.",
               size=10, fill="#fdecea", stroke=POS, color=INK)
    p.append(b)

    render(os.path.join(OUT, "divergence.svg"), W, H, *p,
           title="Корінь біди: приватні кеші тримають копії тієї самої лінії")


# ── invalidate: snooping — запис однієї копії знеправлює решту ─────────────────
# Ідея: три ядра тримають лінію (S). Ядро A хоче писати → кидає в шину сигнал
# «invalidate»; інші, підслухавши його, викидають свою копію. Лишається одна
# правдива копія в A. Так відновлюється когерентність.

def fig_invalidate():
    W, H = 760, 400
    p = []

    # шина — горизонтальна смуга посередині
    busy = 250
    p.append(line(70, busy, W - 40, busy, color=INK, sw=3))
    p.append(text(W - 40, busy - 8, "шина (bus)", size=10, color=INK, anchor="end", bold=True))

    # три ядра над шиною
    def core(cx, name, state, dropped):
        out = []
        kx, ky, kw, kh = cx - 62, 70, 124, 96
        col = POS if dropped else NEG
        fill = "#f0f1f3" if dropped else "#eef4ff"
        out.append(rect(kx, ky, kw, kh, fill=fill, stroke=(col if not dropped else "#c7ccd2"), sw=1.6))
        out.append(text(cx, ky + 22, name, size=12, color=INK, bold=True))
        # клітинка лінії
        cfill = "#f0f1f3" if dropped else "#eef4ff"
        out.append(rect(cx - 34, ky + 34, 68, 42, fill=cfill,
                        stroke=("#c7ccd2" if dropped else NEG), sw=1.4, rx=4))
        if dropped:
            out.append(text(cx, ky + 54, "X", size=11, color=MUTED, bold=True))
            out.append(text(cx, ky + 70, "викинуто", size=9, color=POS))
            # перекреслення
            out.append(line(cx - 30, ky + 38, cx + 30, ky + 72, color=POS, sw=2))
        else:
            out.append(text(cx, ky + 52, "X = 8", size=11, color=INK, bold=True))
            out.append(text(cx, ky + 68, state, size=9, color=NEG, bold=True))
        # стовбур до шини
        out.append(line(cx, ky + kh, cx, busy, color="#9aa0a6", sw=1.4))
        return out

    p += core(180, "ядро A", "Modified", False)
    p += core(400, "ядро B", "", True)
    p += core(620, "ядро C", "", True)

    # сигнал invalidate по шині від A
    p.append(text(180, busy + 26, "A: «пишу X — усі викиньте!»", size=10, color=POS, anchor="middle", bold=True))
    p.append(arrow(210, busy + 40, 380, busy + 40, color=POS, sw=1.8))
    p.append(arrow(210, busy + 56, 600, busy + 56, color=POS, sw=1.8))
    p.append(text(430, busy + 92, "B і C підслухали сигнал у шині й знеправили свою копію", size=10, color=INK, anchor="middle"))
    p.append(text(430, busy + 110, "лишилася ОДНА правдива копія — у ядра A", size=10.5, color=FIELD, anchor="middle", bold=True))

    render(os.path.join(OUT, "invalidate.svg"), W, H, *p,
           title="Підслуховування шини: запис однієї копії знеправлює решту")


# ── mesi: чотири стани лінії ───────────────────────────────────────────────────
# Ідея: компактна карта чотирьох станів MESI з двома осями змісту —
# «скільки копій» і «чи збігається з пам'яттю». Стрілки — ключові переходи.

def fig_mesi():
    W, H = 760, 440
    p = []

    bw, bh = 210, 92
    boxes = {
        "I": (200, 110, "Invalid", "копії немає /\nвона недійсна", "#f0f1f3", MUTED),
        "S": (560, 110, "Shared", "чиста копія; МОЖЕ бути\nтака сама в інших ядрах", "#eef4ff", NEG),
        "E": (200, 300, "Exclusive", "чиста копія, ЄДИНА,\nзбігається з пам'яттю", "#eafaf0", FIELD),
        "M": (560, 300, "Modified", "змінена копія, ЄДИНА,\nпам'ять уже застаріла", "#fdecea", POS),
    }
    # межі кожної рамки — для приєднання стрілок до країв, не до центрів
    def edges(cx, cy):
        return {"L": (cx - bw / 2, cy), "R": (cx + bw / 2, cy),
                "T": (cx, cy - bh / 2), "B": (cx, cy + bh / 2)}
    for k, (cx, cy, name, sub, fill, col) in boxes.items():
        p.append(rect(cx - bw / 2, cy - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.8))
        p.append(text(cx, cy - 20, "%s — %s" % (k, name), size=13, color=INK, bold=True))
        for i, ln in enumerate(sub.split("\n")):
            p.append(text(cx, cy + 4 + i * 15, ln, size=9.5, color=INK))

    def link(a, sa, b, sb, label, lx, ly, color=INK):
        (ax, ay) = edges(boxes[a][0], boxes[a][1])[sa]
        (bx, by) = edges(boxes[b][0], boxes[b][1])[sb]
        out = [arrow(ax, ay, bx, by, color=color, sw=1.7)]
        out.append(text(lx, ly, label, size=9.5, color=color, bold=True))
        return out

    # I → E : читання, коли лінію більше ніхто не має (ексклюзивно)
    p += link("I", "B", "E", "T", "читання (сам)", 130, 208, FIELD)
    # I → S : читання, коли лінія вже є в інших ядрах
    p += link("I", "R", "S", "L", "читання (спільне)", 380, 100, NEG)
    # E → M : запис у власну ексклюзивну копію — тихо, без шини
    p += link("E", "R", "M", "L", "запис (тихо, без шини)", 380, 292, POS)
    # S → M : запис — треба кинути invalidate у шину
    p += link("S", "B", "M", "T", "запис → invalidate у шину", 638, 208, POS)

    p.append(text(W / 2, H - 22, "чужий запис у цю лінію (invalidate з шини) → будь-який стан падає в Invalid",
                  size=10, color=MUTED, anchor="middle", italic=True))

    render(os.path.join(OUT, "mesi.svg"), W, H, *p,
           title="MESI: чотири стани, у яких кеш тримає лінію")


# ── false-sharing: пінг-понг лінії між ядрами та лік вирівнюванням ─────────────
# Ідея: угорі — дві незалежні змінні в ОДНІЙ лінії; кожен запис одного ядра
# знеправлює лінію в іншого, лінія «літає» шиною. Унизу — розвели по різних
# лініях вирівнюванням, ядра більше не заважають одне одному.

def fig_false_sharing():
    W, H = 760, 420
    p = []

    # ── верх: спільна лінія ──
    p.append(text(W / 2, 60, "Одна кеш-лінія на дві незалежні змінні", size=13, color=POS, bold=True))
    # лінія з двох комірок
    lx, ly, cw = 300, 82, 80
    p.append(rect(lx - 6, ly - 6, cw * 2 + 12, 44, fill="none", stroke=NEG, sw=1.4, rx=6))
    p.append(rect(lx, ly, cw - 4, 32, fill="#eef4ff", stroke=NEG, sw=1.2, rx=3))
    p.append(text(lx + (cw - 4) / 2, ly + 21, "a (ядро A)", size=10, color=INK))
    p.append(rect(lx + cw, ly, cw - 4, 32, fill="#eef4ff", stroke=NEG, sw=1.2, rx=3))
    p.append(text(lx + cw + (cw - 4) / 2, ly + 21, "b (ядро B)", size=10, color=INK))
    p.append(text(lx + cw, ly - 16, "одна лінія (64 байти)", size=9, color=MUTED))

    # два ядра з пінг-понгом
    p.append(rect(70, 150, 120, 54, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(text(130, 172, "ядро A", size=12, color=INK, bold=True))
    p.append(text(130, 190, "пише лише a", size=9, color=MUTED))
    p.append(rect(W - 190, 150, 120, 54, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(text(W - 130, 172, "ядро B", size=12, color=INK, bold=True))
    p.append(text(W - 130, 190, "пише лише b", size=9, color=MUTED))

    # пінг-понг стрілки
    p.append('<path d="M 195 168 A 180 60 0 0 1 %d 168" fill="none" stroke="%s" '
             'stroke-width="2" marker-end="url(#arrow)"/>' % (W - 195, POS))
    p.append('<path d="M %d 196 A 180 60 0 0 1 195 196" fill="none" stroke="%s" '
             'stroke-width="2" marker-end="url(#arrow)"/>' % (W - 195, POS))
    p.append(text(W / 2, 232, "запис у a знеправлює лінію в B, запис у b — в A:", size=10, color=POS, anchor="middle", bold=True))
    p.append(text(W / 2, 248, "лінія «літає» шиною туди-сюди, хоч дані незалежні (хибне спільне)", size=9.5, color=INK, anchor="middle"))

    # роздільник
    p.append(line(60, 272, W - 40, 272, color="#d8dde3", sw=1.2, dash="5 4"))

    # ── низ: розвели по різних лініях ──
    p.append(text(W / 2, 300, "Вирівнювання: кожна змінна — у своїй лінії", size=13, color=FIELD, bold=True))
    l1x = 180
    p.append(rect(l1x - 6, 318, cw + 8, 40, fill="none", stroke=FIELD, sw=1.4, rx=6))
    p.append(rect(l1x, 324, cw - 4, 28, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=3))
    p.append(text(l1x + (cw - 4) / 2, 343, "a", size=11, color=INK, bold=True))
    p.append(text(l1x + (cw - 4) / 2, 372, "лінія A", size=9, color=MUTED))
    l2x = 480
    p.append(rect(l2x - 6, 318, cw + 8, 40, fill="none", stroke=FIELD, sw=1.4, rx=6))
    p.append(rect(l2x, 324, cw - 4, 28, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=3))
    p.append(text(l2x + (cw - 4) / 2, 343, "b", size=11, color=INK, bold=True))
    p.append(text(l2x + (cw - 4) / 2, 372, "лінія B", size=9, color=MUTED))
    p.append(text(W / 2, 400, "ядра більше не чіпають спільної лінії — пінг-понг зник, кожне мчить своєю",
                  size=10, color=FIELD, anchor="middle", bold=True))

    render(os.path.join(OUT, "false-sharing.svg"), W, H, *p,
           title="Хибне спільне (false sharing): лінія літає шиною задарма")


# ── why-exclusive: MSI vs MESI на «прочитав своє, тоді записав» ────────────────
# Ідея історичної вставки: показати РІВНО те, заради чого 1984-го додали стан E.
# Типовий випадок — ядро само читає лінію, якої більше ні в кого нема, потім у неї
# ж пише. У MSI чиста копія завжди Shared, тож запис мусить кинути в шину другий
# сигнал (upgrade/invalidate) «про всяк випадок». У MESI читання-наодинці дає
# Exclusive, і перший запис тихий — жодного оголошення. Дві шинні дії проти однієї.

def fig_why_exclusive():
    W, H = 760, 380
    p = []

    midx = W / 2
    p.append(line(midx, 54, midx, H - 30, color="#d8dde3", sw=1.4, dash="5 4"))

    # спільний сценарій угорі
    p.append(text(midx, 46, "Ядро САМО читає лінію, тоді пише в неї (типовий випадок)",
                  size=12, color=MUTED, anchor="middle", italic=True))

    def side(x0, title, col, states, bus_reads, bus_writes, verdict, vcol):
        out = []
        cx = x0 + 175
        out.append(text(cx, 84, title, size=14, color=col, anchor="middle", bold=True))

        # крок 1: читання
        y1 = 118
        out.append(text(cx, y1, "1) читає (промах)", size=10.5, color=INK, anchor="middle", bold=True))
        out.append(fitbox(cx - 135, y1 + 10, 270, 30,
                          "BusRd → принесли копію, стан = %s" % states[0],
                          size=9.5, fill="#eef4ff", stroke=NEG, color=INK))

        # крок 2: запис
        y2 = 180
        out.append(text(cx, y2, "2) пише в ту саму лінію", size=10.5, color=INK, anchor="middle", bold=True))
        out.append(fitbox(cx - 135, y2 + 10, 270, 30, states[1],
                          size=9.5, fill=("#fdecea" if bus_writes else "#eafaf0"),
                          stroke=(POS if bus_writes else FIELD), color=INK))

        # лічильник шинних дій
        y3 = 246
        total = bus_reads + bus_writes
        out.append(text(cx, y3, "дій у шині на цей сценарій:", size=10, color=MUTED, anchor="middle"))
        out.append(fitbox(cx - 60, y3 + 8, 120, 34, "%d" % total,
                          size=20, fill=("#fdecea" if total > 1 else "#eafaf0"),
                          stroke=(POS if total > 1 else FIELD), color=INK, bold=True))

        # вирок
        out.append(fitbox(cx - 150, 306, 300, 40, verdict,
                          size=10, fill="#ffffff", stroke=vcol, color=INK, bold=True))
        return out

    p += side(0, "MSI (три стани)", POS,
              ["Shared", "чиста копія — то Shared;\nу шину: BusUpgr «раптом хтось має»"],
              1, 1,
              "Другий сигнал — ЗАЙВИЙ: копія й так була одна,\nа система про це не знала.", POS)

    p += side(midx, "MESI (+ Exclusive)", FIELD,
              ["Exclusive", "єдиний власник → Exclusive;\nперший запис ТИХИЙ, E → M"],
              1, 0,
              "Стан Exclusive «пам'ятає», що копія одна,\nтож зайвого оголошення нема.", FIELD)

    render(os.path.join(OUT, "why-exclusive.svg"), W, H, *p,
           title="Заради чого додали Exclusive: тихий перший запис")


# ── scaling: підпис хибного спільного — крива «швидкодія vs ядра» ──────────────
# Ідея: головний діагностичний слід. У наївній версії додавання потоків НЕ
# пришвидшує, а ГАЛЬМУЄ (лінія літає між кешами); у вирівняній — майже лінійне
# прискорення. Дві криві на одних осях — одразу видно різницю.

def fig_scaling():
    W, H = 760, 440
    p = []

    ox, oy = 118, 350          # початок координат (низ-ліворуч)
    axw, axh = 552, 268        # довжина осей
    p.append(arrow(ox, oy, ox + axw + 10, oy, color=INK, sw=1.8))     # X
    p.append(arrow(ox, oy, ox, oy - axh - 10, color=INK, sw=1.8))     # Y
    p.append(text(ox + axw / 2, oy + 46, "потоків (ядер) у роботі", size=11, color=INK, bold=True))
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">%s</text>'
             % (ox - 66, oy - axh / 2, FONT, INK, ox - 66, oy - axh / 2,
                esc("сумарна швидкодія (× одного ядра)")))

    ticks = [1, 2, 3, 4, 6, 8]
    def xpos(n):
        return ox + (n - 1) / 7.0 * axw
    for n in ticks:
        x = xpos(n)
        p.append(line(x, oy, x, oy + 6, color=INK, sw=1.4))
        p.append(text(x, oy + 22, str(n), size=10, color=MUTED))

    def ypos(v):               # 0..8 → піксель
        return oy - v / 8.0 * axh
    for v in [1, 2, 4, 6, 8]:
        y = ypos(v)
        p.append(line(ox - 6, y, ox, y, color=INK, sw=1.4))
        p.append(text(ox - 16, y + 4, "%d×" % v, size=9.5, color=MUTED, anchor="end"))

    # пунктир «ідеал»
    p.append(line(xpos(1), ypos(1), xpos(8), ypos(8), color="#c7ccd2", sw=1.3, dash="5 4"))
    p.append(text(xpos(8) - 6, ypos(8) - 10, "ідеал (лінійно)", size=9, color=MUTED, anchor="end", italic=True))
    # риска «одне ядро»
    p.append(line(ox, ypos(1), xpos(8), ypos(1), color="#e3b7b2", sw=1.1, dash="3 4"))

    # вирівняна — майже лінійно
    pad_pts = {1: 1.0, 2: 1.95, 3: 2.85, 4: 3.7, 6: 5.3, 8: 6.7}
    d = "M %.1f %.1f" % (xpos(1), ypos(pad_pts[1]))
    for n in ticks[1:]:
        d += " L %.1f %.1f" % (xpos(n), ypos(pad_pts[n]))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, FIELD))
    for n in ticks:
        p.append(circle(xpos(n), ypos(pad_pts[n]), 3.4, fill=FIELD, stroke=FIELD, sw=1))

    # наївна — падає нижче одного ядра й лежить
    naive_pts = {1: 1.0, 2: 0.55, 3: 0.42, 4: 0.36, 6: 0.30, 8: 0.27}
    d = "M %.1f %.1f" % (xpos(1), ypos(naive_pts[1]))
    for n in ticks[1:]:
        d += " L %.1f %.1f" % (xpos(n), ypos(naive_pts[n]))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, POS))
    for n in ticks:
        p.append(circle(xpos(n), ypos(naive_pts[n]), 3.4, fill=POS, stroke=POS, sw=1))

    # легенда
    lx, ly = 156, 92
    p.append(line(lx, ly, lx + 30, ly, color=FIELD, sw=3))
    p.append(text(lx + 38, ly + 4, "вирівняні лічильники — масштабується", size=10.5, color=INK, anchor="start", bold=True))
    p.append(line(lx, ly + 22, lx + 30, ly + 22, color=POS, sw=3))
    p.append(text(lx + 38, ly + 26, "наївний масив — гальмує від зайвих ядер", size=10.5, color=INK, anchor="start", bold=True))

    render(os.path.join(OUT, "scaling.svg"), W, H, *p,
           title="Підпис хибного спільного: більше ядер — повільніше")


# ── layout: розкладка в пам'яті наївного масиву проти вирівняного ──────────────
# Ідея: показати БАЙТИ. Наївно — 4×int64 (32 Б) в одній 64-байтовій лінії; усі
# четверо ділять лінію. Вирівняно — кожен int64 на початку своєї лінії, решта
# 56 Б — набивка. Це видно словами погано, а очима — миттєво.

def fig_layout():
    W, H = 760, 450
    p = []

    byte = 7.3                 # піксель на байт (64 байти ≈ 467 px)
    x0 = 56
    cellh = 30
    linew = 64 * byte

    def draw_frame(y, label):
        p.append(rect(x0, y, linew, cellh, fill="none", stroke=INK, sw=1.6, rx=4))
        p.append(text(x0, y - 8, label, size=10.5, color=INK, anchor="start", bold=True))
        for b in range(0, 65, 16):
            xx = x0 + b * byte
            p.append(line(xx, y + cellh, xx, y + cellh + 5, color=MUTED, sw=1))
            p.append(text(xx, y + cellh + 16, str(b), size=9, color=MUTED))

    cols = [POS, NEG, FIELD, "#8e44ad"]

    # ── наївно ──
    yn = 78
    p.append(text(W / 2, 50, "Наївно: counters[4] — чотири int64 в ОДНІЙ лінії (64 Б)", size=12.5, color=POS, bold=True))
    draw_frame(yn, "одна кеш-лінія (64 байти)")
    for i in range(4):
        bx = x0 + i * 8 * byte
        p.append(rect(bx + 1, yn + 1, 8 * byte - 2, cellh - 2,
                      fill=("#fdecea" if i == 0 else "#eef4ff"), stroke=cols[i], sw=1.4, rx=2))
        p.append(text(bx + 4 * byte, yn + cellh + 34, "[%d]" % i, size=9, color=cols[i], bold=True))
        p.append(text(bx + 4 * byte, yn + cellh + 46, "ядро %d" % i, size=9, color=cols[i]))
    p.append(text(W / 2, yn + cellh + 70, "усі чотири лічильники → одна лінія → кожен запис знеправлює її в решти (пінг-понг)",
                  size=9.5, color=POS, anchor="middle", bold=True))

    # ── вирівняно ──
    p.append(text(W / 2, 218, "Вирівняно: alignas(64) — кожен лічильник на ПОЧАТКУ своєї лінії", size=12.5, color=FIELD, bold=True))
    for i in range(2):         # дві з чотирьох ліній
        yy = 250 + i * 88
        draw_frame(yy, "лінія лічильника %d" % i)
        p.append(rect(x0 + 1, yy + 1, 8 * byte - 2, cellh - 2, fill="#eafaf0", stroke=cols[i], sw=1.6, rx=2))
        p.append(text(x0 + 4 * byte, yy + cellh + 16, "value (8 Б)", size=9, color=cols[i], bold=True))
        p.append(rect(x0 + 8 * byte + 1, yy + 1, 56 * byte - 2, cellh - 2, fill="#f4f6f8", stroke="#c7ccd2", sw=1.2, rx=2))
        p.append(text(x0 + 8 * byte + 28 * byte, yy + cellh / 2 + 4, "набивка 56 байтів — щоб сусід не потрапив у цю лінію", size=9, color=MUTED))
    p.append(text(W / 2, 250 + 88 + cellh + 34, "різні лінії → жоден запис не чіпає чужу лінію → гонки нема (ціна — витрачена пам'ять)",
                  size=9.5, color=FIELD, anchor="middle", bold=True))

    render(os.path.join(OUT, "layout.svg"), W, H, *p,
           title="Розкладка в пам'яті: наївний масив проти вирівняного")


if __name__ == "__main__":
    fig_divergence()
    fig_invalidate()
    fig_mesi()
    fig_false_sharing()
    fig_why_exclusive()
    fig_scaling()
    fig_layout()
    print("figs: готово")
