# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── pipeline: три кроки CABAC ─────────────────────────────────────────────────
# Ідея: символ кодека (коефіцієнт, вектор руху) проходить три станції —
# бінаризація → вибір контексту → двійкове арифметичне кодування, а від кодера
# назад іде стрілка оновлення моделі (адаптація).

def fig_pipeline():
    W, H = 760, 300
    p = []
    y = 120
    bw, bh = 150, 70
    xs = [30, 275, 520]
    labs = [
        "бінаризація\n(число → біти)",
        "вибір контексту\n(яка модель біта)",
        "двійкове арифм.\nкодування біта",
    ]
    fills = ["#eef4ff", "#eafaf0", "#fdf6e3"]
    centers = []
    for i, (x, lab, fill) in enumerate(zip(xs, labs, fills)):
        p.append(fitbox(x, y - bh / 2, bw, bh, lab, size=12, fill=fill, stroke=INK, sw=1.6, bold=True))
        centers.append((x, x + bw))
        if i > 0:
            p.append(arrow(centers[i - 1][1] + 2, y, x - 4, y, color=INK, sw=1.8))

    # вхід
    p.append(text(xs[0] + bw / 2, y - bh / 2 - 16, "символ кодека", size=11, color=MUTED, bold=True))
    p.append(text(xs[0] + bw / 2, y - bh / 2 - 2, "коефіцієнт, вектор руху…", size=9, color=MUTED))
    # вихід
    p.append(arrow(centers[2][1] + 2, y, centers[2][1] + 46, y, color=INK, sw=1.8))
    p.append(text(centers[2][1] + 50, y - 4, "біти", size=11, color=INK, anchor="start", bold=True))
    p.append(text(centers[2][1] + 50, y + 12, "у потік", size=9, color=MUTED, anchor="start"))

    # зворотна стрілка адаптації від кодера до контексту
    ax0 = xs[2] + bw / 2
    ax1 = xs[1] + bw / 2
    yb = y + bh / 2 + 44
    p.append(line(ax0, y + bh / 2, ax0, yb, color=POS, sw=1.8))
    p.append(line(ax0, yb, ax1, yb, color=POS, sw=1.8))
    p.append(arrow(ax1, yb, ax1, y + bh / 2 + 2, color=POS, sw=1.8))
    p.append(text((ax0 + ax1) / 2, yb + 18, "оновлення моделі: бачив біт → підправ імовірність контексту",
                  size=11, color=POS, bold=True))

    render(os.path.join(OUT, "pipeline.svg"), W, H, *p,
           title="Три кроки CABAC, замкнені петлею адаптації")


# ── binarization: число → ланцюжок двійкових рішень ───────────────────────────
# Ідея: арифметичний рушій CABAC жере лише біти (0/1), тож будь-яке число
# спершу розкладають на ланцюжок «так/ні». Показано унарний код малих значень.

def fig_binarization():
    W, H = 700, 300
    p = []
    # таблиця унарного коду
    rows = [("0", "0"), ("1", "10"), ("2", "110"), ("3", "1110"), ("4", "11110")]
    x0 = 70
    y0 = 92
    rh = 36
    p.append(text(x0, y0 - 28, "значення", size=12, color=INK, anchor="start", bold=True))
    p.append(text(x0 + 170, y0 - 28, "унарні біти (ланцюжок рішень)", size=12, color=INK, anchor="start", bold=True))
    for i, (v, bits) in enumerate(rows):
        yy = y0 + i * rh
        p.append(text(x0 + 30, yy, v, size=14, color=INK, anchor="middle", bold=True))
        # намалюємо біти кружечками: 1 = «ще є», 0 = «стоп»
        bx = x0 + 170
        for b in bits:
            col = FIELD if b == "1" else POS
            fill = "#eafaf0" if b == "1" else "#fdecea"
            p.append(circle(bx + 10, yy - 5, 11, fill=fill, stroke=col, sw=1.8))
            p.append(text(bx + 10, yy - 0.5, b, size=12, color=col, bold=True))
            bx += 30
    # легенда
    p.append(circle(x0 + 12, H - 44, 10, fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(text(x0 + 12, H - 40, "1", size=11, color=FIELD, bold=True))
    p.append(text(x0 + 28, H - 40, "= «значення ще більше» (рахуй далі)", size=11, color=INK, anchor="start"))
    p.append(circle(x0 + 12, H - 22, 10, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(x0 + 12, H - 18, "0", size=11, color=POS, bold=True))
    p.append(text(x0 + 28, H - 18, "= «стоп, дійшли» (кінець числа)", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "binarization.svg"), W, H, *p,
           title="Бінаризація: число стає ланцюжком «так/ні»")


# ── context-adapt: дві черги бітів дають дві різні моделі ──────────────────────
# Ідея: один і той самий біт за різним сусідством має різну ймовірність бути 1;
# CABAC тримає окрему модель на кожен контекст і підкручує її після кожного біта.

def fig_context_adapt():
    W, H = 720, 320
    p = []
    # дві «скриньки контексту», кожна зі своїм нахилом імовірності
    def ctx(cx, label, p1, seq, col, fill):
        b, bw, bh = textbox(cx, 70, label, size=12, bold=True, fill=fill, stroke=col, sw=1.8, color=col)
        out = [b]
        # шкала ймовірності p(біт=1)
        sx, sw_, sy = cx - 110, 220, 150
        out.append(line(sx, sy, sx + sw_, sy, color=INK, sw=1.6))
        out.append(text(sx, sy + 20, "0", size=10, color=MUTED))
        out.append(text(sx + sw_, sy + 20, "1", size=10, color=MUTED, anchor="end"))
        out.append(text(cx, sy + 22, "p(біт = 1)", size=10, color=MUTED))
        mx = sx + sw_ * p1
        out.append(circle(mx, sy, 7, fill=fill, stroke=col, sw=2))
        out.append(line(mx, sy - 26, mx, sy - 8, color=col, sw=1.6))
        out.append(text(mx, sy - 30, "%.2f" % p1, size=11, color=col, bold=True))
        # приклад спостережених бітів
        out.append(text(cx, sy + 52, "бачили: " + seq, size=11, color=INK))
        return out

    p += ctx(190, "контекст A\n(сусіди = нулі)", 0.85, "1 1 1 0 1 1", FIELD, "#eafaf0")
    p += ctx(530, "контекст B\n(сусіди = ненулі)", 0.30, "0 0 1 0 0 0", NEG, "#eef4ff")

    p.append(text(W / 2, H - 26, "той самий біт, різне сусідство → різна модель; кожен біт ще й підкручує свою",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "context-adapt.svg"), W, H, *p,
           title="Контекстне моделювання: модель на кожне сусідство")


# ── worked: інтервал звужується на двійкових рішеннях ─────────────────────────
# Ідея: показати один прохід — стартовий діапазон [low,low+range), поділ на
# MPS/LPS за поточною p, вибір частки бітом, і звуження.

def fig_worked():
    W, H = 700, 330
    p = []
    # три яруси інтервалу згори вниз
    x0, x1 = 90, 620
    span = x1 - x0
    yA, yB, yC = 90, 180, 270
    barh = 34

    def split_bar(y, lo_frac, mps_frac, take_mps, p_mps, label):
        out = []
        # уся смуга
        out.append(rect(x0, y, span, barh, fill=BG, stroke=INK, sw=1.4, rx=0))
        # межа MPS|LPS
        mx = x0 + span * mps_frac
        out.append(rect(x0, y, span * mps_frac, barh, fill="#eafaf0", stroke=INK, sw=1.2, rx=0))
        out.append(rect(mx, y, span * (1 - mps_frac), barh, fill="#fdecea", stroke=INK, sw=1.2, rx=0))
        out.append(text(x0 + span * mps_frac / 2, y + barh / 2 + 4, "MPS (p=%.2f)" % p_mps, size=10, color=FIELD, bold=True))
        out.append(text(mx + span * (1 - mps_frac) / 2, y + barh / 2 + 4, "LPS", size=10, color=POS, bold=True))
        out.append(text(x0 - 8, y + barh / 2 + 4, label, size=11, color=INK, anchor="end", bold=True))
        return out, mx

    # ярус 1: range=1.0, p(MPS)=0.8, прийшов біт MPS
    b1, mx1 = split_bar(yA, 0.0, 0.8, True, 0.8, "старт")
    p += b1
    p.append(text(x1 + 10, yA + barh / 2 + 4, "біт = MPS", size=11, color=FIELD, anchor="start", bold=True))
    # стрілка вниз від MPS-частки до наступного ярусу (розтягуємо обрану частку)
    p.append(arrow(x0 + span * 0.4, yA + barh + 2, x0 + span * 0.5, yB - 6, color=INK, sw=1.5))

    # ярус 2: обрана MPS-частка стала новим повним діапазоном; p(MPS)=0.83 (підросла)
    b2, mx2 = split_bar(yB, 0.0, 0.83, True, 0.83, "звузили,\nмодель ↑")
    p += b2
    p.append(text(x1 + 10, yB + barh / 2 + 4, "біт = LPS", size=11, color=POS, anchor="start", bold=True))
    p.append(arrow(mx2 + span * (1 - 0.83) / 2, yB + barh + 2, x0 + span * 0.5, yC - 6, color=INK, sw=1.5))

    # ярус 3: обрана LPS-частка; після LPS модель смикнулась назад p(MPS)=0.74
    b3, mx3 = split_bar(yC, 0.0, 0.74, False, 0.74, "звузили,\nмодель ↓")
    p += b3

    p.append(text(W / 2, H - 18, "кожен біт обирає частку (MPS широка / LPS вузька) і зсуває p; renormalization тримає точність",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "worked.svg"), W, H, *p,
           title="Двійкове арифметичне кодування: частка на кожен біт")


# ── sequential: петля зворотного зв'язку — вузьке місце ───────────────────────
# Ідея: біт n не почати, доки не оновлено модель після біта n−1; звідси
# суто послідовний ланцюг, який важко паралелити.

def fig_sequential():
    W, H = 720, 250
    p = []
    y = 110
    r = 26
    xs = [110, 250, 390, 530]
    labs = ["біт 1", "біт 2", "біт 3", "біт 4"]
    for i, (x, lab) in enumerate(zip(xs, labs)):
        p.append(circle(x, y, r, fill="#fdf6e3", stroke=INK, sw=1.8))
        p.append(text(x, y + 5, lab, size=12, color=INK, bold=True))
        if i > 0:
            p.append(arrow(xs[i - 1] + r + 2, y, x - r - 2, y, color=INK, sw=1.8))
            mid = (xs[i - 1] + xs[i]) / 2
            p.append(text(mid, y - r - 10, "оновити", size=9, color=POS, bold=True))
            p.append(text(mid, y - r + 2, "модель", size=9, color=POS))

    p.append(text(W / 2, y + r + 36, "кожен біт чекає на оновлену після попереднього модель — ланцюг не розірвати",
                  size=11, color=MUTED, italic=True))
    p.append(text(W / 2, y + r + 56, "(GPU любить незалежні задачі; CABAC дає одну довгу залежність)",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "sequential.svg"), W, H, *p,
           title="Чому CABAC послідовний: петля заважає паралелити")


# ════════════════ фігури для детальної версії (-d) ════════════════════════════

# ── states: 64 стани ймовірності, перехід MPS/LPS ─────────────────────────────
# Ідея: драбина станів від «майже 50/50» до «майже певно MPS»; біт MPS повзе до
# впевненості, біт LPS відкидає назад; на найвпевненішому стані можлива зміна MPS.

def fig_states():
    W, H = 720, 320
    p = []
    n = 12                      # показуємо 12 представницьких станів із 64
    x0, x1 = 70, 650
    y = 150
    dx = (x1 - x0) / (n - 1)
    # драбина: висота кружечка = впевненість
    for i in range(n):
        x = x0 + i * dx
        p.append(circle(x, y, 12, fill="#eef4ff", stroke=INK, sw=1.5))
        p.append(text(x, y + 4, str(i), size=10, color=INK))
    # підписи країв
    p.append(text(x0, y + 40, "стан 0:\np(LPS) ≈ 0.5", size=10, color=MUTED))
    p.append(text(x1, y + 40, "стан 63:\np(LPS) → 0", size=10, color=MUTED, anchor="end"))
    p.append(text(x0, y - 36, "невпевнено", size=11, color=POS, bold=True))
    p.append(text(x1, y - 36, "майже певно MPS", size=11, color=FIELD, anchor="end", bold=True))

    # стрілка MPS: уперед на 1 (повзе до впевненості)
    xa = x0 + 4 * dx
    p.append(arrow(xa + 12, y - 18, xa + dx - 12, y - 18, color=FIELD, sw=2))
    p.append(text(xa + dx / 2, y - 24, "біт MPS: +1", size=10, color=FIELD, bold=True))
    # стрілка LPS: назад на кілька (відкидає)
    xb = x0 + 7 * dx
    p.append(line(xb - 12, y + 20, xb - 3 * dx + 12, y + 20, color=POS, sw=2))
    p.append(arrow(xb - 3 * dx + 12, y + 20, xb - 3 * dx + 11, y + 20, color=POS, sw=2))
    p.append(text(xb - 1.5 * dx, y + 34, "біт LPS: назад", size=10, color=POS, bold=True))

    p.append(text(W / 2, H - 18, "64 стани замість дробу p: біт MPS додає впевненості, рідкий LPS її збиває",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "states.svg"), W, H, *p,
           title="Драбина 64 станів імовірності (LPS/MPS)")


# ── renorm: множення-вільне звуження таблицею ─────────────────────────────────
# Ідея: range ділять не множенням range·p, а вибором з таблиці rangeLPS[стан][2
# старші біти range]; коли range замалий — подвоюють і виштовхують біт.

def fig_renorm():
    W, H = 720, 300
    p = []
    # ліворуч: таблиця rangeLPS (схематично)
    tx, ty = 70, 90
    p.append(text(tx, ty - 16, "rangeLPS[стан][qRange]  — 64×4 готових чисел",
                  size=12, color=INK, anchor="start", bold=True))
    cols = ["q0", "q1", "q2", "q3"]
    cellw, cellh = 52, 30
    for c, cl in enumerate(cols):
        p.append(text(tx + 70 + c * cellw + cellw / 2, ty, cl, size=10, color=MUTED))
    rows = [("стан s", ["110", "128", "146", "164"]),
            ("…", ["…", "…", "…", "…"]),
            ("стан 62", ["6", "7", "8", "9"])]
    for r, (rl, vals) in enumerate(rows):
        yy = ty + 18 + r * cellh
        p.append(text(tx, yy + cellh / 2, rl, size=10, color=INK, anchor="start"))
        for c, v in enumerate(vals):
            p.append(rect(tx + 70 + c * cellw, yy, cellw, cellh, fill="#eef4ff", stroke=INK, sw=1.1, rx=0))
            p.append(text(tx + 70 + c * cellw + cellw / 2, yy + cellh / 2 + 4, v, size=10, color=INK))
    p.append(text(tx, ty + 18 + 3 * cellh + 18,
                  "беремо 2 старші біти range як індекс qRange — замість range·p", size=10, color=MUTED, anchor="start"))

    # праворуч: renormalization як подвоєння
    rx = 470
    p.append(text(rx, ty - 16, "renormalization", size=12, color=INK, anchor="start", bold=True))
    by = ty + 20
    widths = [22, 44, 88, 176]
    labels = ["замало", "×2", "×2", "досить"]
    for i, (w, lb) in enumerate(zip(widths, labels)):
        yy = by + i * 40
        col = POS if i < len(widths) - 1 else FIELD
        p.append(rect(rx, yy, w, 22, fill="#fdecea" if i < 3 else "#eafaf0", stroke=col, sw=1.5, rx=0))
        p.append(text(rx + w + 8, yy + 16, lb, size=10, color=col, anchor="start", bold=True))
        if i < len(widths) - 1:
            p.append(text(rx + 150, yy + 16, "→ виштовхнути біт", size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "renorm.svg"), W, H, *p,
           title="Множення-вільне ядро: таблиця замість range·p")


# ── bypass: рівноймовірний біт повз модель ────────────────────────────────────
# Ідея: дві колії — звичайна (через контекст + оновлення) і обвідна (bypass:
# range ділиться навпіл, без моделі), для бітів, де 0 і 1 майже рівноймовірні.

def fig_bypass():
    W, H = 700, 280
    p = []
    # розвилка
    sx, sy = 90, 140
    p.append(fitbox(sx, sy - 28, 110, 56, "біт на\nкодування", size=11, fill=FILL, stroke=INK, sw=1.6, bold=True))
    jx = sx + 110

    # верхня колія — regular
    ry = 80
    p.append(arrow(jx + 2, sy - 6, 250, ry + 24, color=INK, sw=1.6))
    p.append(fitbox(260, ry, 200, 50, "звичайна: контекст +\nоновлення моделі", size=11, fill="#eafaf0", stroke=FIELD, sw=1.6, bold=True, color=FIELD))
    p.append(text(360, ry - 8, "є перекіс імовірності", size=10, color=MUTED))

    # нижня колія — bypass
    py = 196
    p.append(arrow(jx + 2, sy + 6, 250, py + 4, color=INK, sw=1.6))
    p.append(fitbox(260, py - 24, 200, 50, "bypass: range / 2,\nбез моделі", size=11, fill="#fdf6e3", stroke=POS, sw=1.6, bold=True, color="#a06a00"))
    p.append(text(360, py + 36, "0 і 1 майже рівноймовірні (знак, хвости)", size=10, color=MUTED))

    # обидві у потік
    p.append(arrow(460, ry + 24, 600, 120, color=INK, sw=1.6))
    p.append(arrow(460, py, 600, 150, color=INK, sw=1.6))
    p.append(text(610, 138, "потік", size=11, color=INK, anchor="start", bold=True))

    render(os.path.join(OUT, "bypass.svg"), W, H, *p,
           title="Дві колії: модель там, де є що моделювати")


if __name__ == "__main__":
    fig_pipeline()
    fig_binarization()
    fig_context_adapt()
    fig_worked()
    fig_sequential()
    fig_states()
    fig_renorm()
    fig_bypass()
    print("OK: figures written to", OUT)
