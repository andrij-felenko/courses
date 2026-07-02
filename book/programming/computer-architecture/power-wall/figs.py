# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

HOT  = "#fdecea"; S_HOT = POS          # гаряче / активне
COLD = "#eaf0fd"; S_COLD = NEG         # холодне
GRN  = "#eaf6ef"; S_GRN = FIELD        # добре / поле
GREY = "#eef1f4"; S_GREY = MUTED       # темне / вимкнене
DARK = "#e3e6ea"                       # темний кремній (сірий, «вимкнено»)


# ── 1. Звідки тепло: конденсатор-вентиль + формула ───────────────────────────
def fig_power_source():
    W, H = 760, 380
    p = []
    p.append(text(W / 2, 30, "Звідки в чипі береться тепло", size=16, bold=True))

    # один вентиль як конденсатор
    p.append(rect(70, 70, 260, 150, fill=HOT, stroke=S_HOT, sw=1.6, rx=10))
    p.append(text(200, 92, "один вентиль = конденсатор", size=12, color="#8a2820", bold=True))
    # пластини конденсатора
    p.append(line(150, 120, 250, 120, color=INK, sw=3))
    p.append(line(150, 165, 250, 165, color=INK, sw=3))
    p.append(text(200, 112, "V", size=13, color=POS, bold=True))
    p.append(text(266, 145, "заряд ↑", size=11, color=POS, anchor="start"))
    p.append(text(266, 162, "= «1»", size=11, color=POS, anchor="start", bold=True))
    p.append(text(200, 198, "зарядити → розрядити = порція тепла", size=10.5, color=INK))

    # множення
    p.append(text(410, 130, "×", size=22, color=MUTED, bold=True))
    p.append(rect(440, 70, 260, 150, fill=GREY, stroke=MUTED, sw=1.5, rx=10))
    p.append(text(570, 96, "мільярди вентилів", size=12.5, color=INK, bold=True))
    p.append(text(570, 122, "× мільярди перемикань", size=12.5, color=INK, bold=True))
    p.append(text(570, 148, "за секунду", size=12.5, color=INK, bold=True))
    p.append(text(570, 186, "= гаряча пічка на долоні", size=11, color=POS, bold=True, italic=True))

    # формула
    p.append(rect(150, 250, 460, 60, fill=GRN, stroke=S_GRN, sw=1.8, rx=10))
    p.append(text(W / 2, 288, "P = C · V² · f", size=24, color=INK, bold=True))
    p.append(text(W / 2, 340, "V у квадраті — головна пружина: удвічі вища напруга → вчетверо більше тепла.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 362, "C — ємність, V — напруга, f — частота такту (перемикань за секунду).",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "power-source.svg"), W, H, *p)


# ── 2. Чому зламалося масштабування Деннарда ─────────────────────────────────
def fig_dennard_break():
    W, H = 780, 430
    p = []
    p.append(text(W / 2, 28, "Чому зламалося масштабування Деннарда", size=16, bold=True))

    # осі: X — час/техпроцес, Y — напруга
    ox, oy = 90, 300
    ax_w, ax_h = 620, 230
    p.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    p.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    p.append(text(ox - 6, oy - ax_h - 4, "напруга V", size=11.5, color=INK, bold=True, anchor="end"))
    p.append(text(ox + ax_w, oy + 22, "менший транзистор → →", size=11.5, color=INK, bold=True, anchor="end"))

    # порогова напруга — підлога
    yth = oy - 40
    p.append(line(ox, yth, ox + ax_w, yth, color=POS, sw=1.6, dash="6 4"))
    p.append(text(ox + ax_w - 4, yth - 8, "порогова напруга — нижче не можна", size=10.5, color=POS, bold=True, anchor="end"))

    # V падає, тоді впирається
    p.append('<polyline points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (ox + 10, oy - ax_h + 20, ox + 250, yth + 55, ox + 420, yth + 12, ox + ax_w - 10, yth + 6, NEG))
    p.append(text(ox + 150, oy - ax_h + 44, "V падає разом із розміром", size=10.5, color=NEG, bold=True, anchor="start"))
    p.append(text(ox + 470, yth + 30, "падати нікуди", size=10.5, color=NEG, bold=True, anchor="start"))

    # витоки ростуть експоненційно від точки впирання
    xk = ox + 420
    p.append(line(xk, oy, xk, oy - ax_h, color=MUTED, sw=1.2, dash="3 4"))
    p.append(text(xk, oy - ax_h - 2, "≈2004–2006", size=10, color=MUTED, bold=True))
    p.append('<polyline points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (xk, oy - 6, xk + 70, oy - 30, xk + 140, oy - 90, ox + ax_w - 6, oy - ax_h + 30, POS))
    p.append(text(ox + ax_w - 6, oy - ax_h + 24, "струм витоку ↑↑", size=10.5, color=POS, bold=True, anchor="end"))
    p.append(text(ox + ax_w - 6, oy - ax_h + 42, "(експоненційно)", size=9.5, color=POS, anchor="end", italic=True))

    p.append(text(W / 2, 350, "Квадрат V у формулі тримав густину потужності сталою, поки V падала.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 372, "Коли V уперлася в поріг, падіння спинилось — і витоки поповзли вгору.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 398, "Обидві частини потужності потягли густину вгору — магія Деннарда скінчилася.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "dennard-break.svg"), W, H, *p)


# ── 3. Темний кремній: активна лише частина ──────────────────────────────────
def fig_dark_silicon():
    W, H = 760, 380
    p = []
    p.append(text(W / 2, 30, "Темний кремній: світиться лише частина чипа", size=16, bold=True))

    # сітка транзисторів; частина «світла», решта «темна»
    gx, gy = 250, 70
    cols, rows, cell = 8, 6, 30
    # шаблон активних клітинок (розкидані «острівці»)
    active = {(1, 1), (2, 1), (1, 2), (5, 0), (6, 0), (6, 1),
              (3, 4), (4, 4), (4, 5), (0, 4), (7, 3), (2, 3)}
    for r in range(rows):
        for c in range(cols):
            x, y = gx + c * cell, gy + r * cell
            if (c, r) in active:
                p.append(rect(x, y, cell - 4, cell - 4, fill=HOT, stroke=S_HOT, sw=1.4, rx=3))
            else:
                p.append(rect(x, y, cell - 4, cell - 4, fill=DARK, stroke="#c4c8cd", sw=1.0, rx=3))
    # легенда
    p.append(rect(gx + cols * cell + 26, gy + 6, 18, 18, fill=HOT, stroke=S_HOT, sw=1.4, rx=3))
    p.append(text(gx + cols * cell + 50, gy + 20, "активний (світлий)", size=11, color=INK, anchor="start"))
    p.append(rect(gx + cols * cell + 26, gy + 36, 18, 18, fill=DARK, stroke="#c4c8cd", sw=1.0, rx=3))
    p.append(text(gx + cols * cell + 50, gy + 50, "вимкнений (темний)", size=11, color=MUTED, anchor="start"))

    # ліва підпис-колонка
    p.append(text(70, gy + 40, "Мур напихає", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(70, gy + 60, "чип транзисторами", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(70, gy + 96, "стіна потужності", size=12, color=POS, bold=True, anchor="start"))
    p.append(text(70, gy + 116, "не дає ввімкнути", size=12, color=POS, bold=True, anchor="start"))
    p.append(text(70, gy + 136, "всі одразу", size=12, color=POS, bold=True, anchor="start"))

    p.append(text(W / 2, 300, "Увімкнути весь кремній одночасно = пробити стелю охолодження й згоріти.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 324, "Тож у кожну мить активна лише частина, решта мусить спати.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 350, "З кожним поколінням транзисторів більшає, а тепловий бюджет той самий — темного більшає.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "dark-silicon.svg"), W, H, *p)


# ── 4. Три відповіді на стіну ────────────────────────────────────────────────
def fig_mitigations():
    W, H = 800, 350
    p = []
    p.append(text(W / 2, 28, "Три способи обійти стіну потужності", size=16, bold=True))

    bw, bh, by = 240, 210, 58
    xs = [20, 280, 540]

    # 1 багатоядерність
    p.append(rect(xs[0], by, bw, bh, fill=COLD, stroke=S_COLD, sw=1.8, rx=12))
    p.append(text(xs[0] + bw / 2, by + 26, "Багатоядерність", size=13.5, color=NEG, bold=True))
    # два невеликі ядра
    p.append(rect(xs[0] + 40, by + 48, 70, 50, fill=GRN, stroke=S_GRN, sw=1.4, rx=6))
    p.append(text(xs[0] + 75, by + 78, "ядро", size=11, color=S_GRN, bold=True))
    p.append(rect(xs[0] + 130, by + 48, 70, 50, fill=GRN, stroke=S_GRN, sw=1.4, rx=6))
    p.append(text(xs[0] + 165, by + 78, "ядро", size=11, color=S_GRN, bold=True))
    p.append(text(xs[0] + bw / 2, by + 128, "два повільніші замість", size=10.5, color=INK, bold=True))
    p.append(text(xs[0] + bw / 2, by + 145, "одного шаленого", size=10.5, color=INK, bold=True))
    p.append(text(xs[0] + bw / 2, by + 172, "те саме тепло, більше", size=10, color=MUTED, italic=True))
    p.append(text(xs[0] + bw / 2, by + 188, "роботи — якщо паралельно", size=10, color=MUTED, italic=True))

    # 2 DVFS
    p.append(rect(xs[1], by, bw, bh, fill=GRN, stroke=S_GRN, sw=1.8, rx=12))
    p.append(text(xs[1] + bw / 2, by + 26, "DVFS", size=13.5, color=S_GRN, bold=True))
    # хвиля розгону/спаду
    base = by + 80
    p.append('<polyline points="%d,%d %d,%d %d,%d %d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (xs[1] + 30, base, xs[1] + 70, base - 34, xs[1] + 110, base - 34,
                xs[1] + 150, base, xs[1] + 190, base, xs[1] + 210, base, INK))
    p.append(text(xs[1] + 90, by + 34, "сплеск", size=9.5, color=POS, bold=True))
    p.append(text(xs[1] + 180, by + 74, "спад", size=9.5, color=NEG, bold=True))
    p.append(text(xs[1] + bw / 2, by + 128, "знижуй f і V разом", size=10.5, color=INK, bold=True))
    p.append(text(xs[1] + bw / 2, by + 145, "(квадрат V!)", size=10.5, color=INK, bold=True))
    p.append(text(xs[1] + bw / 2, by + 172, "розганяйся лише", size=10, color=MUTED, italic=True))
    p.append(text(xs[1] + bw / 2, by + 188, "короткими сплесками", size=10, color=MUTED, italic=True))

    # 3 спеціалізація
    p.append(rect(xs[2], by, bw, bh, fill=HOT, stroke=S_HOT, sw=1.8, rx=12))
    p.append(text(xs[2] + bw / 2, by + 26, "Спеціалізація", size=13.5, color=POS, bold=True))
    labs = ["CPU", "GPU", "кодек", "крипто", "NPU", "FPU"]
    fills = [GRN, DARK, DARK, GRN, DARK, DARK]
    for i, (lab, fl) in enumerate(zip(labs, fills)):
        cx = xs[2] + 30 + (i % 3) * 64
        cy = by + 48 + (i // 3) * 44
        st = S_GRN if fl == GRN else "#c4c8cd"
        p.append(rect(cx, cy, 56, 34, fill=fl, stroke=st, sw=1.3, rx=5))
        p.append(text(cx + 28, cy + 22, lab, size=10, color=(S_GRN if fl == GRN else MUTED), bold=True))
    p.append(text(xs[2] + bw / 2, by + 150, "мозаїка економних блоків", size=10.5, color=INK, bold=True))
    p.append(text(xs[2] + bw / 2, by + 174, "світиться лише потрібний,", size=10, color=MUTED, italic=True))
    p.append(text(xs[2] + bw / 2, by + 190, "решта — темна", size=10, color=MUTED, italic=True))

    p.append(text(W / 2, 300, "Жодна не скасовує фізику — усі живуть у тому самому тепловому бюджеті, лиш розумніше.",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, 324, "Ось чому сучасний чип — багато різних ядер із режимами розгону й купою прискорювачів.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "mitigations.svg"), W, H, *p)


# ── 5. Tejas проти Prescott: тепло на 2.8 ГГц (для hist-вставки 2004) ─────────
def fig_tejas_power():
    W, H = 760, 430
    p = []
    p.append(text(W / 2, 30, "Тепло на 2.8 ГГц: Prescott проти зразка Tejas", size=16, bold=True))

    # осі стовпчиків
    base = 300          # низ стовпчиків
    ax_left = 120
    p.append(line(ax_left - 30, base, W - 60, base, color=INK, sw=1.8))
    p.append(text(ax_left - 34, base - 175, "тепловий пакет, Вт", size=11, color=INK, bold=True, anchor="end"))

    # шкала: 150 Вт → 175 px
    def h_of(w):
        return w / 150.0 * 175.0

    # стовпчик Prescott (84 Вт)
    x1 = ax_left + 40
    bw = 120
    h1 = h_of(84)
    p.append(rect(x1, base - h1, bw, h1, fill=COLD, stroke=S_COLD, sw=1.8, rx=6))
    p.append(text(x1 + bw / 2, base - h1 - 12, "≈84 Вт", size=13, color=NEG, bold=True))
    p.append(text(x1 + bw / 2, base + 22, "Prescott", size=12.5, color=INK, bold=True))
    p.append(text(x1 + bw / 2, base + 40, "(90 нм)", size=10, color=MUTED, italic=True))

    # стовпчик Tejas (150 Вт)
    x2 = x1 + bw + 90
    h2 = h_of(150)
    p.append(rect(x2, base - h2, bw, h2, fill=HOT, stroke=S_HOT, sw=1.8, rx=6))
    p.append(text(x2 + bw / 2, base - h2 - 12, "≈150 Вт", size=13, color=POS, bold=True))
    p.append(text(x2 + bw / 2, base + 22, "зразок Tejas", size=12.5, color=INK, bold=True))
    p.append(text(x2 + bw / 2, base + 40, "(90 нм)", size=10, color=MUTED, italic=True))

    # стрілка «майже вдвічі»
    ymid = base - h1 - 26
    p.append(line(x1 + bw + 8, ymid, x2 - 8, ymid, color=MUTED, sw=1.4, dash="5 4"))
    p.append(text((x1 + bw + x2) / 2, ymid - 8, "майже ×2", size=11, color=POS, bold=True))

    # примітка: і це ще не повна частота
    p.append(rect(150, base + 62, 460, 56, fill=GREY, stroke=MUTED, sw=1.4, rx=10))
    p.append(text(W / 2, base + 84, "І це ще НЕ цільові 7 ГГц — лише 2.8, менша половина задуму.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, base + 104, "Дотягти таку архітектуру до гігагерців масове охолодження не змогло б.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "tejas-power.svg"), W, H, *p)


# ── 6. Таблиця масштабування: як меншає кожна величина (для вставки math) ─────
def fig_scaling_table():
    W, H = 720, 470
    p = []
    p.append(text(W / 2, 30, "Масштабування Деннарда: усе меншає узгоджено", size=16, bold=True))
    p.append(text(W / 2, 52, "поділили розміри й напругу на k — ось що стало з рештою (k ≈ 1.4)",
                  size=11, color=MUTED, italic=True))

    rows = [
        ("розмір (кожна сторона)", "× 1/k", NEG, "менше"),
        ("площа транзистора", "× 1/k²", NEG, "менше"),
        ("транзисторів на площі", "× k²", POS, "БІЛЬШЕ"),
        ("напруга V", "× 1/k", NEG, "менше"),
        ("ємність C", "× 1/k", NEG, "менше"),
        ("струм I", "× 1/k", NEG, "менше"),
        ("затримка (перемикання)", "× 1/k", NEG, "швидше"),
        ("частота f", "× k", POS, "вище"),
        ("енергія клацання C·V²", "× 1/k³", FIELD, "втричі менше"),
        ("потужність 1 транзистора", "× 1/k²", NEG, "менше"),
    ]
    x0, y0 = 60, 74
    rw, rh = W - 120, 30
    p.append(text(x0 + 8, y0 + 20, "величина", size=11, color=INK, bold=True, anchor="start"))
    p.append(text(x0 + 340, y0 + 20, "× за крок", size=11, color=INK, bold=True))
    p.append(text(x0 + rw - 8, y0 + 20, "напрям", size=11, color=INK, bold=True, anchor="end"))
    y = y0 + rh
    for name, fac, col, note in rows:
        p.append(rect(x0, y, rw, rh, fill="#fbfcfd", stroke="#d9dee3", sw=1.0, rx=4))
        p.append(text(x0 + 8, y + 20, name, size=11.5, color=INK, anchor="start"))
        p.append(text(x0 + 340, y + 20, fac, size=13, color=col, bold=True))
        p.append(text(x0 + rw - 8, y + 20, note, size=10.5, color=col, anchor="end", italic=True))
        y += rh

    # підсумок — густина стала
    y += 8
    p.append(rect(x0, y, rw, 44, fill=GRN, stroke=S_GRN, sw=2.0, rx=8))
    p.append(text(x0 + 8, y + 19, "ГУСТИНА ПОТУЖНОСТІ (тепло на мм²)", size=11.5, color=INK, bold=True, anchor="start"))
    p.append(text(x0 + rw - 8, y + 27, "× 1  — СТАЛА", size=15, color=S_GRN, bold=True, anchor="end"))
    p.append(text(W / 2, y + 40, "(1/k²) × k² скорочуються: кожен транзистор охолов у k², а їх стало в k² більше",
                  size=9.5, color=MUTED, anchor="middle"))
    render(os.path.join(OUT, "scaling-table.svg"), W, H, *p)


# ── 7. Баланс степенів k: до і після зламу (для вставки math) ─────────────────
def fig_exponent_balance():
    W, H = 760, 430
    p = []
    p.append(text(W / 2, 30, "Уся стіна — в одному множнику: квадрат напруги", size=16, bold=True))
    p.append(text(W / 2, 52, "густина = C · V² · f · (транзисторів на площі) — рахуємо степені k у кожного",
                  size=11, color=MUTED, italic=True))

    def panel(x, w, title, tcol, items, total_txt, total_col, verdict, vcol, vfill):
        q = []
        q.append(rect(x, 80, w, 300, fill="#fbfcfd", stroke=tcol, sw=1.8, rx=12))
        q.append(text(x + w / 2, 106, title, size=13, color=tcol, bold=True))
        yy = 138
        for lab, powr, col in items:
            q.append(text(x + 22, yy, lab, size=12, color=INK, anchor="start"))
            q.append(text(x + w - 22, yy, powr, size=13, color=col, bold=True, anchor="end"))
            yy += 34
        q.append(line(x + 22, yy - 12, x + w - 22, yy - 12, color="#c9ced3", sw=1.2))
        q.append(text(x + 22, yy + 12, "сума степенів k:", size=11.5, color=INK, anchor="start", bold=True))
        q.append(text(x + w - 22, yy + 12, total_txt, size=15, color=total_col, bold=True, anchor="end"))
        q.append(rect(x + 18, 322, w - 36, 44, fill=vfill, stroke=vcol, sw=1.8, rx=8))
        q.append(fitbox(x + 20, 324, w - 40, 40, verdict, size=11.5, pad=6,
                        fill=vfill, stroke=vfill, sw=0, color=vcol, bold=True))
        return q

    p.extend(panel(
        40, 320, "ПОКИ V падає на k", S_GRN,
        [("C → 1/k", "−1", NEG),
         ("V² → 1/k²", "−2", NEG),
         ("f → k", "+1", POS),
         ("транз./площа → k²", "+2", POS)],
        "0", S_GRN,
        "k⁰ = 1 → густина СТАЛА", S_GRN, GRN))

    p.extend(panel(
        400, 320, "КОЛИ V завмерла (≈2004–06)", S_HOT,
        [("C → 1/k", "−1", NEG),
         ("V² → 1 (не падає!)", "0", POS),
         ("f → k", "+1", POS),
         ("транз./площа → k²", "+2", POS)],
        "+2", S_HOT,
        "k² → густина РОСТЕ вдвічі/крок", S_HOT, HOT))

    p.append(text(W / 2, 214, "→", size=28, color=MUTED, bold=True))
    p.append(text(W / 2, 240, "зник −2", size=9.5, color=POS, bold=True))

    p.append(text(W / 2, 404, "Прибери один множник V² — і показник стрибає з 0 до +2. Плюс зверху статичний витік.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "exponent-balance.svg"), W, H, *p)


if __name__ == "__main__":
    fig_power_source()
    fig_dennard_break()
    fig_dark_silicon()
    fig_mitigations()
    fig_tejas_power()
    fig_scaling_table()
    fig_exponent_balance()
    print("OK: figs written to", OUT)
