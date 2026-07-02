# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SEL = "#8e44ad"   # колір лінії вибору (адреси)


# ── 1. Демультиплексор як роздавальний перемикач + символ-коробка ─────────────
def fig_selector():
    import math
    W, H = 720, 400
    f = []
    # -- ліворуч: механічна інтуїція (роздавальний перемикач) --
    cx, cy, R = 210, 210, 78
    f.append(text(210, 60, "Інтуїція: роздавальний перемикач", size=16, bold=True))
    # єдиний вхід знизу до осі
    f.append(line(cx, cy + 70, cx, cy, color=NEG, sw=2.5))
    f.append(circle(cx, cy + 70, 6, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(cx + 20, cy + 74, "D", size=14, color=NEG, bold=True))
    f.append(text(cx, cy + 104, "один вхід приходить сюди", size=12, color=MUTED))
    # чотири виходи-контакти по дузі вгорі
    outs = [("Y0", 150), ("Y1", 110), ("Y2", 70), ("Y3", 30)]  # кути в градусах
    for name, ang in outs:
        a = math.radians(ang)
        px, py = cx + R * math.cos(a), cy - R * math.sin(a)
        f.append(circle(px, py, 6, fill="#fdecea", stroke=POS, sw=2))
        f.append(text(px + 12, py - 6, name, size=13, color=POS, bold=True))
        f.append(line(px + 6, py, px + 26, py, color=MUTED, sw=1.5))
    # вісь і повзунок, що вказує на Y1
    f.append(circle(cx, cy, 8, fill=FILL, stroke=INK, sw=2))
    sel_a = math.radians(110)
    tx, ty = cx + (R - 8) * math.cos(sel_a), cy - (R - 8) * math.sin(sel_a)
    f.append(line(cx, cy, tx, ty, color=SEL, sw=4))
    f.append(text(cx - 6, cy - 96, "повзунок веде вхід на ОДИН вихід", size=12, color=MUTED, anchor="middle"))

    # -- праворуч: символ-коробка з лінією вибору --
    bx, by, bw, bh = 470, 120, 150, 200
    f.append(text(545, 60, "Умовне позначення", size=16, bold=True))
    # трапеція-коробка демультиплексора (розширюється до виходів — дзеркало MUX)
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.8"/>' % (
        bx, by + 40, bx + bw, by, bx + bw, by + bh, bx, by + bh - 40, FILL, LINE))
    f.append(text(bx + bw / 2, by + bh / 2 - 6, "DEMUX", size=15, bold=True))
    f.append(text(bx + bw / 2, by + bh / 2 + 16, "1 → 4", size=13, color=MUTED))
    # вхід D ліворуч
    ym = by + bh / 2
    f.append(line(bx - 40, ym, bx, ym, color=NEG, sw=1.8))
    f.append(text(bx - 50, ym + 5, "D", size=13, color=NEG, bold=True, anchor="end"))
    # виходи Y0..Y3 праворуч
    for i, nm in enumerate(["Y0", "Y1", "Y2", "Y3"]):
        yy = by + 30 + i * 44
        f.append(line(bx + bw, yy, bx + bw + 40, yy, color=POS, sw=1.8))
        f.append(text(bx + bw + 50, yy + 5, nm, size=12, color=POS, bold=True, anchor="start"))
    # лінія вибору знизу
    f.append(line(bx + bw / 2, by + bh, bx + bw / 2, by + bh + 34, color=SEL, sw=2))
    f.append(text(bx + bw / 2, by + bh + 52, "S1 S0", size=13, color=SEL, bold=True))
    f.append(text(bx + bw / 2, by + bh + 70, "адреса виходу", size=11, color=MUTED))

    render(os.path.join(OUT, 'demux-selector.svg'), W, H, *f)


# ── 2. Побудова 1→4 із вентилів (дешифратор + гейти дозволу) ──────────────────
def fig_gates():
    W, H = 720, 400
    f = []
    f.append(text(W / 2, 32, "1→4 демультиплексор: Yᵢ = D · (мінітерм адреси)", size=15, bold=True))

    # вхід даних D (спільний для всіх чотирьох AND)
    f.append(line(60, 200, 120, 200, color=NEG, sw=2))
    f.append(text(48, 205, "D", size=14, color=NEG, bold=True, anchor="end"))
    f.append(line(120, 90, 120, 320, color=NEG, sw=1.6))  # вертикальна шина D
    f.append(circle(120, 200, 3.5, fill=NEG, stroke=NEG, sw=1))

    # адресні лінії S1 S0 знизу
    f.append(text(48, 375, "S1", size=13, color=SEL, bold=True, anchor="end"))
    f.append(line(60, 370, 200, 370, color=SEL, sw=1.5))
    f.append(text(48, 350, "S0", size=13, color=SEL, bold=True, anchor="end"))
    f.append(line(60, 350, 175, 350, color=SEL, sw=1.5))

    # чотири AND-гейти, кожен пропускає D для своєї комбінації
    def and_gate(x, y):
        s = ('<path d="M%d %d L%d %d A22 22 0 0 1 %d %d L%d %d Z" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (x, y - 22, x + 18, y - 22, x + 18, y + 22, x, y + 22, FILL, LINE))
        s += text(x + 9, y + 5, "&", size=15, bold=True)
        return s

    rows = [
        ("Y0", 90,  "S̄1 S̄0"),
        ("Y1", 160, "S̄1 S0"),
        ("Y2", 230, "S1 S̄0"),
        ("Y3", 300, "S1 S0"),
    ]
    for nm, y, lbl in rows:
        f.append(and_gate(240, y))
        # D у верхній вхід гейта
        f.append(line(120, y - 10, 240, y - 10, color=NEG, sw=1.4))
        # адресний терм у нижній вхід (умовна лінія-мітка)
        f.append(text(200, y + 30, lbl, size=11, color=SEL, bold=True, anchor="middle"))
        f.append(line(175, y + 12, 240, y + 12, color=SEL, sw=1.3))
        # вихід
        f.append(line(258, y, 320, y, color=POS, sw=1.8))
        f.append(circle(320, y, 5, fill="#fdecea", stroke=POS, sw=2))
        f.append(text(334, y + 5, nm, size=13, color=POS, bold=True, anchor="start"))

    # праворуч: таблиця маршруту
    tx, ty = 430, 78
    f.append(text(tx + 120, ty - 14, "куди йде D", size=13, bold=True))
    trows = [("00", "Y0 = D,  решта = 0"),
             ("01", "Y1 = D,  решта = 0"),
             ("10", "Y2 = D,  решта = 0"),
             ("11", "Y3 = D,  решта = 0")]
    for i, (a, r) in enumerate(trows):
        yy = ty + i * 46
        f.append(fitbox(tx, yy, 70, 38, "S1 S0\n" + a, size=12, fill="#efe8f7", stroke=SEL, color=SEL, bold=True))
        f.append(fitbox(tx + 80, yy, 200, 38, r, size=13, fill=FILL, stroke=LINE, color=INK))
    f.append(text(tx + 140, ty + 4 * 46 + 8, "адреса обирає ОДИН вихід; невибрані — «0»", size=11, color=MUTED))

    render(os.path.join(OUT, 'demux-gates.svg'), W, H, *f)


# ── 3. Демультиплексор = дешифратор із входом дозволу ─────────────────────────
def fig_decoder():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 30, "Демультиплексор — це дешифратор, у якого дозвіл = вхід даних", size=15, bold=True))

    # ліворуч: дешифратор
    bx, by, bw, bh = 90, 70, 150, 210
    f.append(rect(bx, by, bw, bh, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(bx + bw / 2, by + 26, "ДЕШИФРАТОР", size=13, bold=True))
    f.append(text(bx + bw / 2, by + 46, "2 → 4", size=12, color=MUTED))
    # адреса
    f.append(line(bx - 46, by + 90, bx, by + 90, color=SEL, sw=1.6))
    f.append(text(bx - 52, by + 94, "S0", size=12, color=SEL, bold=True, anchor="end"))
    f.append(line(bx - 46, by + 120, bx, by + 120, color=SEL, sw=1.6))
    f.append(text(bx - 52, by + 124, "S1", size=12, color=SEL, bold=True, anchor="end"))
    # вхід дозволу знизу — ОСЬ ГОЛОВНЕ
    f.append(line(bx + bw / 2, by + bh, bx + bw / 2, by + bh + 34, color=NEG, sw=2.4))
    f.append(text(bx + bw / 2, by + bh + 52, "EN", size=13, color=NEG, bold=True))
    f.append(text(bx + bw / 2, by + bh + 70, "дозвіл", size=11, color=MUTED))
    # виходи
    for i in range(4):
        yy = by + 40 + i * 44
        f.append(line(bx + bw, yy, bx + bw + 34, yy, color=POS, sw=1.6))
        f.append(text(bx + bw + 44, yy + 4, "Y%d" % i, size=11, color=POS, bold=True, anchor="start"))

    # стрілка-перетворення
    f.append(arrow(360, 175, 430, 175, color=INK, sw=2))
    f.append(text(395, 160, "подай D", size=12, color=INK, bold=True))
    f.append(text(395, 200, "на EN", size=12, color=INK, bold=True))

    # праворуч: той самий блок, але EN підписаний як D
    bx2 = 500
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.8"/>' % (
        bx2, by + 40, bx2 + bw, by, bx2 + bw, by + bh, bx2, by + bh - 40, FILL, LINE))
    f.append(text(bx2 + bw / 2, by + bh / 2 - 6, "DEMUX", size=14, bold=True))
    f.append(text(bx2 + bw / 2, by + bh / 2 + 14, "1 → 4", size=12, color=MUTED))
    ym = by + bh / 2
    f.append(line(bx2 - 40, ym, bx2, ym, color=NEG, sw=2))
    f.append(text(bx2 - 48, ym + 5, "D", size=13, color=NEG, bold=True, anchor="end"))
    for i in range(4):
        yy = by + 40 + i * 44
        f.append(line(bx2 + bw, yy, bx2 + bw + 34, yy, color=POS, sw=1.6))
        f.append(text(bx2 + bw + 44, yy + 4, "Y%d" % i, size=11, color=POS, bold=True, anchor="start"))
    f.append(line(bx2 + bw / 2, by + bh, bx2 + bw / 2, by + bh + 34, color=SEL, sw=2))
    f.append(text(bx2 + bw / 2, by + bh + 52, "S1 S0", size=12, color=SEL, bold=True))

    f.append(text(W / 2, 344, "Прив'яжеш дозвіл до 1 — вийде «1-з-N» дешифратор; прив'яжеш до D — вийде демультиплексор.",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'demux-decoder.svg'), W, H, *f)


# ── 4. Пара mux+demux: одна лінія, багато потоків (TDM) ───────────────────────
def fig_tdm():
    W, H = 740, 380
    f = []
    f.append(text(W / 2, 30, "Пара MUX↔DEMUX: багато потоків одним каналом (часове ущільнення)", size=14, bold=True))

    # ліворуч: MUX зводить 4 джерела
    mx, my, mw, mh = 120, 90, 90, 200
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.8"/>' % (
        mx, my, mx + mw, my + 34, mx + mw, my + mh - 34, mx, my + mh, FILL, LINE))
    f.append(text(mx + mw / 2, my + mh / 2 - 4, "MUX", size=14, bold=True))
    for i, nm in enumerate(["A", "B", "C", "D"]):
        yy = my + 28 + i * ((mh - 56) / 3)
        f.append(line(mx - 34, yy, mx, yy, color=NEG, sw=1.6))
        f.append(text(mx - 42, yy + 4, nm, size=12, color=NEG, bold=True, anchor="end"))
    f.append(text(mx + mw / 2 - 30, my - 8, "джерела", size=11, color=MUTED, anchor="middle"))

    # спільний канал (один дріт)
    chx1 = mx + mw
    chx2 = 540
    chy = my + mh / 2
    f.append(line(chx1, chy, chx2, chy, color=INK, sw=3))
    f.append(text((chx1 + chx2) / 2, chy - 12, "один канал", size=12, color=INK, bold=True))
    f.append(text((chx1 + chx2) / 2, chy + 22, "A B C D A B C D … по черзі", size=11, color=MUTED))

    # праворуч: DEMUX розкидає назад
    dx, dy, dw, dh = 540, 90, 90, 200
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.8"/>' % (
        dx, dy + 34, dx + dw, dy, dx + dw, dy + dh, dx, dy + dh - 34, FILL, LINE))
    f.append(text(dx + dw / 2, dy + dh / 2 - 4, "DEMUX", size=13, bold=True))
    for i, nm in enumerate(["A", "B", "C", "D"]):
        yy = dy + 28 + i * ((dh - 56) / 3)
        f.append(line(dx + dw, yy, dx + dw + 34, yy, color=POS, sw=1.6))
        f.append(text(dx + dw + 42, yy + 4, nm, size=12, color=POS, bold=True, anchor="start"))
    f.append(text(dx + dw / 2 + 30, dy - 8, "адресати", size=11, color=MUTED, anchor="middle"))

    # спільна адреса-лічильник знизу — синхронна для обох
    f.append(line(mx + mw / 2, my + mh, mx + mw / 2, 340, color=SEL, sw=2))
    f.append(line(dx + dw / 2, dy + dh, dx + dw / 2, 340, color=SEL, sw=2))
    f.append(line(mx + mw / 2, 340, dx + dw / 2, 340, color=SEL, sw=2, dash="5,4"))
    f.append(fitbox((mx + dx) / 2 + 20, 326, 160, 30, "спільна адреса (лічильник)", size=11,
                    fill="#efe8f7", stroke=SEL, color=SEL, bold=True))

    render(os.path.join(OUT, 'demux-tdm.svg'), W, H, *f)


# ── 5. Нарощування деревом: 1→4 з трьох 1→2 ──────────────────────────────────
def fig_tree():
    W, H = 700, 360
    f = []
    f.append(text(W / 2, 32, "Дерево: три 1→2 демультиплексори дають 1→4", size=15, bold=True))

    def demux12(x, y, in_lbl, sel_lbl, up_lbl, dn_lbl, in_color=NEG):
        # маленька трапеція 1→2 (розширюється праворуч)
        w, h = 50, 74
        f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
            x, y + 14, x + w, y, x + w, y + h, x, y + h - 14, FILL, LINE))
        f.append(text(x + w / 2, y + h / 2 + 4, "1→2", size=11, bold=True))
        # вхід ліворуч
        f.append(line(x - 26, y + h / 2, x, y + h / 2, color=in_color, sw=1.6))
        if in_lbl:
            f.append(text(x - 32, y + h / 2 + 4, in_lbl, size=11, color=in_color, bold=True, anchor="end"))
        # вибір знизу
        f.append(line(x + w / 2, y + h, x + w / 2, y + h + 16, color=SEL, sw=1.6))
        f.append(text(x + w / 2, y + h + 30, sel_lbl, size=11, color=SEL, bold=True))
        # два виходи
        f.append(line(x + w, y + 16, x + w + 26, y + 16, color=POS, sw=1.5))
        f.append(line(x + w, y + h - 16, x + w + 26, y + h - 16, color=POS, sw=1.5))
        return (x + w + 26, y + 16), (x + w + 26, y + h - 16)

    # перший ярус: один 1→2 керований СТАРШИМ бітом S1
    up, dn = demux12(120, 140, "D", "S1", "", "")
    # другий ярус: два 1→2 керовані МОЛОДШИМ бітом S0
    (y0, y1) = demux12(300, 70, None, "S0", "", "")
    (y2, y3) = demux12(300, 210, None, "S0", "", "")
    # з'єднати виходи першого ярусу у входи другого
    f.append(line(up[0], up[1], 300 - 26, 70 + 37, color=POS, sw=1.5))
    f.append(line(dn[0], dn[1], 300 - 26, 210 + 37, color=POS, sw=1.5))
    # підписати чотири фінальні виходи
    for (pt, nm) in [(y0, "Y0"), (y1, "Y1"), (y2, "Y2"), (y3, "Y3")]:
        f.append(circle(pt[0], pt[1], 5, fill="#fdecea", stroke=POS, sw=2))
        f.append(text(pt[0] + 14, pt[1] + 4, nm, size=12, color=POS, bold=True, anchor="start"))

    f.append(text(W / 2, 340, "S1 обирає гілку (верх/низ), S0 — вихід усередині гілки", size=12, color=MUTED))

    render(os.path.join(OUT, 'demux-tree.svg'), W, H, *f)


# ── 6. Запис у одну комірку: спільна шина + дешифратор роздає строб ────────────
def fig_write_strobe():
    W, H = 760, 430
    f = []
    f.append(text(W / 2, 30, "Запис у ОДНУ комірку: спільна шина даних + дешифратор роздає строб дозволу", size=13.5, bold=True))

    # -- дешифратор 74HC138 (роздавач строба) --
    dx, dy, dw, dh = 70, 90, 130, 260
    f.append(rect(dx, dy, dw, dh, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(dx + dw / 2, dy + 26, "74HC138", size=13, bold=True))
    f.append(text(dx + dw / 2, dy + 44, "дешифратор", size=11, color=MUTED))
    f.append(text(dx + dw / 2, dy + 58, "1 → 8", size=11, color=MUTED))
    # адреса зліва
    f.append(line(dx - 44, dy + 96, dx, dy + 96, color=SEL, sw=1.6))
    f.append(text(dx - 50, dy + 100, "A0", size=11, color=SEL, bold=True, anchor="end"))
    f.append(line(dx - 44, dy + 120, dx, dy + 120, color=SEL, sw=1.6))
    f.append(text(dx - 50, dy + 124, "A1", size=11, color=SEL, bold=True, anchor="end"))
    f.append(line(dx - 44, dy + 144, dx, dy + 144, color=SEL, sw=1.6))
    f.append(text(dx - 50, dy + 148, "A2", size=11, color=SEL, bold=True, anchor="end"))
    f.append(text(dx - 30, dy + 176, "адреса\nкомірки", size=10, color=MUTED, anchor="middle"))
    # СТРОБ на вхід дозволу знизу
    f.append(line(dx + dw / 2, dy + dh, dx + dw / 2, dy + dh + 40, color=NEG, sw=2.6))
    f.append(text(dx + dw / 2, dy + dh + 58, "СТРОБ → Ē", size=12, color=NEG, bold=True))
    f.append(text(dx + dw / 2, dy + dh + 74, "«зараз записуй»", size=10, color=MUTED))

    # -- вісім засувок-комірок праворуч; спільна шина даних заходить у кожну --
    cellx, celltop, cellw, cellh, gap = 470, 74, 120, 30, 8
    # вертикальна спільна шина даних
    busx = 360
    f.append(line(busx, celltop - 6, busx, celltop + 8 * (cellh + gap), color=POS, sw=4))
    f.append(text(busx, celltop - 14, "спільна шина даних (8 біт)", size=11, color=POS, bold=True))
    for i in range(8):
        cy = celltop + i * (cellh + gap)
        active = (i == 3)   # приклад: пишемо в комірку 3
        fill_c = "#eafaf1" if active else FILL
        stroke_c = FIELD if active else LINE
        f.append(rect(cellx, cy, cellw, cellh, fill=fill_c, stroke=stroke_c, sw=1.8 if active else 1.4))
        f.append(text(cellx + cellw / 2, cy + cellh / 2 + 4, "комірка %d" % i, size=11,
                      color=(FIELD if active else INK), bold=active))
        # відгалуження шини даних у вхід D комірки
        f.append(line(busx, cy + cellh / 2, cellx, cy + cellh / 2, color=POS, sw=1.4))
        f.append(circle(busx, cy + cellh / 2, 3, fill=POS, stroke=POS, sw=1))
        # вихід дешифратора -> вхід дозволу защіпки цієї комірки
        oy = dy + 40 + i * ((dh - 70) / 7)
        f.append(line(dx + dw, oy, dx + dw + 24, oy, color=(NEG if active else MUTED), sw=1.8 if active else 1.2))
        # ламана від виходу дешифратора до нижнього краю комірки (вхід LE/WE)
        lex = cellx + 24
        f.append(line(dx + dw + 24, oy, lex, oy, color=(NEG if active else MUTED), sw=1.2, dash=None if active else "3,3"))
        f.append(line(lex, oy, lex, cy + cellh, color=(NEG if active else MUTED), sw=1.6 if active else 1.0,
                      dash=None if active else "3,3"))
        f.append(text(dx + dw + 30, oy - 5, "Y%d̄" % i, size=9,
                      color=(NEG if active else MUTED), anchor="start"))

    # мітка активного шляху
    f.append(fitbox(250, 376, 400, 44,
                    "адреса = 3 → падає лише вихід Y3 → защіпує ЛИШЕ комірку 3;\nрешта сім тримають старе значення",
                    size=11, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True))

    render(os.path.join(OUT, 'demux-write-strobe.svg'), W, H, *f)


if __name__ == '__main__':
    fig_selector()
    fig_gates()
    fig_decoder()
    fig_tdm()
    fig_tree()
    fig_write_strobe()
    print("ok: 6 figures")
