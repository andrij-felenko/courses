# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GFILL = "#eafaf0"   # добрий стан
GSTRK = "#27ae60"
BFILL = "#fdecea"   # поганий стан
BSTRK = "#c0392b"


def cpath(d, color=INK, sw=2.2, dash=None, arrow=True):
    """Дуга/крива <path>; arrow=True вішає стрілку-маркер (є в defs render())."""
    a = ' marker-end="url(#arrow)"' if arrow else ''
    dd = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s%s/>' % (d, color, sw, dd, a)


# ── states: двостановий ланцюг Маркова G ⇄ B ─────────────────────────────────

def fig_states():
    W, H = 800, 440
    p = []

    Gx, Gy, R = 250, 210, 66
    Bx = 550

    # петля-самоперехід над G (стояти в доброму): 1−p
    p.append(cpath("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" %
                   (Gx - 30, Gy - 59, Gx - 78, Gy - 148, Gx + 78, Gy - 148, Gx + 30, Gy - 59),
                   color=GSTRK, sw=2.2))
    p.append(text(Gx, Gy - 128, "1 − p", size=14, color=GSTRK, bold=True))
    # петля над B: 1−r
    p.append(cpath("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" %
                   (Bx - 30, Gy - 59, Bx - 78, Gy - 148, Bx + 78, Gy - 148, Bx + 30, Gy - 59),
                   color=BSTRK, sw=2.2))
    p.append(text(Bx, Gy - 128, "1 − r", size=14, color=BSTRK, bold=True))

    # G → B (верхня дуга, стрілка в B): p
    mx = (Gx + Bx) / 2
    p.append(cpath("M %.1f %.1f Q %.1f %.1f %.1f %.1f" %
                   (Gx + 57, Gy - 33, mx, Gy - 92, Bx - 57, Gy - 33), color=INK, sw=2.4))
    p.append(text(mx, Gy - 86, "p", size=17, color=INK, bold=True))
    # B → G (нижня дуга, стрілка в G): r
    p.append(cpath("M %.1f %.1f Q %.1f %.1f %.1f %.1f" %
                   (Bx - 57, Gy + 33, mx, Gy + 92, Gx + 57, Gy + 33), color=INK, sw=2.4))
    p.append(text(mx, Gy + 100, "r", size=17, color=INK, bold=True))

    # вершини
    p.append(circle(Gx, Gy, R, fill=GFILL, stroke=GSTRK, sw=3.0))
    p.append(text(Gx, Gy - 6, "G", size=30, color=GSTRK, bold=True))
    p.append(text(Gx, Gy + 22, "добрий", size=13, color=GSTRK))
    p.append(circle(Bx, Gy, R, fill=BFILL, stroke=BSTRK, sw=3.0))
    p.append(text(Bx, Gy - 6, "B", size=30, color=BSTRK, bold=True))
    p.append(text(Bx, Gy + 22, "поганий", size=13, color=BSTRK))

    # ймовірність помилки під кожним станом
    b1, _, _ = textbox(Gx, Gy + R + 52, "помилка e_G\n(мала, у Гілберта = 0)",
                       size=12.5, fill=GFILL, stroke=GSTRK, sw=1.8, pad=10)
    p.append(b1)
    b2, _, _ = textbox(Bx, Gy + R + 52, "помилка e_B\n(велика, ≈ 0.5)",
                       size=12.5, fill=BFILL, stroke=BSTRK, sw=1.8, pad=10)
    p.append(b2)

    p.append(text(W / 2, H - 16,
                  "стан «липкий»: увійшовши, канал у ньому затримується — тому помилки збиваються в пачки",
                  size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "states.svg"), W, H, *p,
           title="Гілберт–Елліот: канал з двома настроями")


# ── trace: пачки проти рівномірного шуму, той самий середній рівень ──────────

def fig_trace():
    W, H = 940, 470
    p = []

    tx0, tx1 = 300, 900          # доріжка часу
    N = 124
    B_INT = [(34, 47), (86, 96)]  # інтервали поганого стану (у стовпцях)

    def X(c):
        return tx0 + c / float(N) * (tx1 - tx0)

    yS, yE, yM = 96, 196, 292     # три доріжки
    strip_h = 34

    # фонові вертикальні смуги «поганого стану» під двома верхніми доріжками
    for a, b in B_INT:
        p.append(rect(X(a), yS - strip_h / 2 - 6, X(b) - X(a), (yE + strip_h / 2) - (yS - strip_h / 2) + 12,
                      fill="#fbeeec", stroke="none", sw=0, rx=6))

    # ── доріжка 1: стан каналу ──
    p.append(rect(tx0, yS - strip_h / 2, tx1 - tx0, strip_h, fill=GFILL, stroke=GSTRK, sw=1.8, rx=5))
    for a, b in B_INT:
        p.append(rect(X(a), yS - strip_h / 2, X(b) - X(a), strip_h, fill=BFILL, stroke=BSTRK, sw=2.0, rx=5))
    p.append(mtext(24, yS - 6, ["стан", "каналу"], size=12.5, color=INK, anchor="start", bold=True))
    p.append(text(X((B_INT[0][0] + B_INT[0][1]) / 2), yS + 5, "B", size=13, color=BSTRK, bold=True))
    p.append(text(X((B_INT[1][0] + B_INT[1][1]) / 2), yS + 5, "B", size=13, color=BSTRK, bold=True))
    p.append(text(X(14), yS + 5, "G", size=13, color=GSTRK, bold=True))

    # ── доріжка 2: помилки Гілберта–Елліота (у пачках, під станом B) ──
    p.append(line(tx0, yE, tx1, yE, color="#cfd4da", sw=1.4))
    ge_cols = [35, 37, 38, 41, 44, 87, 89, 90, 93]
    for c in ge_cols:
        p.append(line(X(c), yE - 15, X(c), yE + 15, color=BSTRK, sw=2.6))
    p.append(mtext(24, yE - 6, ["Гілберт–", "Елліот"], size=12.5, color=BSTRK, anchor="start", bold=True))

    # ── доріжка 3: канал без пам'яті (той самий рахунок, розсіяно) ──
    p.append(line(tx0, yM, tx1, yM, color="#cfd4da", sw=1.4))
    mem_cols = [7, 21, 34, 48, 62, 76, 90, 104, 118]
    for c in mem_cols:
        p.append(line(X(c), yM - 15, X(c), yM + 15, color=NEG, sw=2.6))
    p.append(mtext(24, yM - 6, ["без", "пам'яті"], size=12.5, color=NEG, anchor="start", bold=True))

    # підписи-леми праворуч від доріжок помилок
    p.append(text(tx1, yE + 34, "9 помилок — усі в двох пачках", size=11.5, color=BSTRK, anchor="end", italic=True))
    p.append(text(tx1, yM + 34, "ті самі 9 помилок — розсіяні рівно", size=11.5, color=NEG, anchor="end", italic=True))

    box, _, _ = textbox(W / 2, H - 52,
                        "однаковий середній рівень помилок — але Гілберт–Елліот збиває їх у пачки під поганим станом,\n"
                        "а канал без пам'яті розсіює рівно: код побачить дві геть різні задачі",
                        size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "trace.svg"), W, H, *p,
           title="Пачка чи розсип: те саме число, інша вдача")


# ── interleave: перемішування розтягує пачку по різних словах ────────────────

def fig_interleave():
    W, H = 940, 540
    p = []

    ROWS = ["A", "B", "C", "D", "E"]
    NC = 8
    cw, ch = 36, 32

    def grid(ox, oy, burst_cells, title, order_note):
        out = []
        gw = NC * cw
        out.append(text(ox + gw / 2, oy - 40, title, size=14, color=INK, bold=True))
        out.append(text(ox + gw / 2, oy - 20, order_note, size=11.5, color=MUTED, italic=True))
        # заголовки стовпців
        for j in range(NC):
            out.append(text(ox + j * cw + cw / 2, oy - 4, str(j), size=10, color=MUTED))
        for i, rname in enumerate(ROWS):
            ry = oy + i * ch
            out.append(text(ox - 12, ry + ch / 2 + 4, rname, size=12, color=INK, bold=True, anchor="end"))
            for j in range(NC):
                bad = (i, j) in burst_cells
                out.append(rect(ox + j * cw, ry, cw, ch,
                                fill=BFILL if bad else "#f4f6f8",
                                stroke=BSTRK if bad else "#d4d8de", sw=2.0 if bad else 1.0, rx=3))
                if bad:
                    out.append(text(ox + j * cw + cw / 2, ry + ch / 2 + 5, "✗", size=14, color=BSTRK, bold=True))
        return out, gw

    # ЛІВОРУЧ: без перемішування — пачка = 5 підряд у рядку C
    lx, gy = 96, 128
    left_burst = {(2, j) for j in range(2, 7)}
    g1, gw = grid(lx, gy, left_burst, "без перемішування", "передаємо рядками →")
    p.extend(g1)
    # позначити пачку дужкою над рядком C
    by = gy + 2 * ch
    p.append(cpath("M %.1f %.1f L %.1f %.1f" % (lx + 2 * cw, by - 4, lx + 7 * cw, by - 4),
                   color=BSTRK, sw=2.4, arrow=False))
    b1, _, _ = textbox(lx + gw / 2, gy + 5 * ch + 46,
                       "слово C: 5 помилок > t = 2\nвтрачене  ✗",
                       size=12.5, bold=True, fill=BFILL, stroke=BSTRK, sw=2.2, pad=11)
    p.append(b1)

    # ПРАВОРУЧ: з перемішуванням — пачка = 5 підряд = один стовпець
    rx = 540
    right_burst = {(i, 4) for i in range(5)}
    g2, gw2 = grid(rx, gy, right_burst, "з перемішуванням (глибина 5)", "передаємо стовпцями ↓")
    p.extend(g2)
    b2, _, _ = textbox(rx + gw2 / 2, gy + 5 * ch + 46,
                       "кожне слово: 1 помилка ≤ t = 2\nусі виправлені  ✓",
                       size=12.5, bold=True, fill=GFILL, stroke=GSTRK, sw=2.2, pad=11)
    p.append(b2)

    p.append(text(W / 2, 70,
                  "код виправляє до t = 2 помилок у слові · та сама пачка з 5 збитих символів у ефірі",
                  size=12.5, color=INK, bold=True))

    p.append(text(W / 2, H - 16,
                  "перемішування не прибирає помилки — воно розкладає одну пачку по багатьох словах, і код знову дає раду",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "interleave.svg"), W, H, *p,
           title="Перемішування: розтягнути пачку, щоб код вижив")


# ── dwell hist: довжини пачок геометричні, середня 1/r ───────────────────────

def fig_dwell_hist():
    import math
    W, H = 880, 500
    p = []
    # виміряні частки (20 млн бітів, seed=12345, p=0.001 r=0.1 eB=0.4), k = 1..22
    fracs = [0.1025, 0.0908, 0.0807, 0.0732, 0.0665, 0.0605, 0.0524, 0.0454,
             0.0421, 0.0378, 0.0330, 0.0310, 0.0280, 0.0255, 0.0225, 0.0215,
             0.0197, 0.0156, 0.0150, 0.0130, 0.0108, 0.0098]
    r = 0.1
    K = len(fracs)
    x0, x1 = 104, 820
    yb, yt = 408, 118
    ymax = 0.112
    colw = (x1 - x0) / K
    bw = colw * 0.60

    def X(i):
        return x0 + (i + 0.5) * colw

    def Y(v):
        return yb - v / ymax * (yb - yt)

    # осі
    p.append(line(x0, yb, x1 + 6, yb, color=INK, sw=2.0))
    p.append(line(x0, yb, x0, yt - 6, color=INK, sw=2.0))
    for v in (0.02, 0.04, 0.06, 0.08, 0.10):
        p.append(line(x0 - 6, Y(v), x0, Y(v), color=INK, sw=1.6))
        p.append(text(x0 - 11, Y(v) + 4, "%.2f" % v, size=11, color=MUTED, anchor="end"))

    # стовпці — виміряно
    for i, f in enumerate(fracs):
        p.append(rect(X(i) - bw / 2, Y(f), bw, yb - Y(f), fill=BFILL, stroke=BSTRK, sw=1.5, rx=2))
    for i in range(K):
        if i % 2 == 0 or i == K - 1:
            p.append(text(X(i), yb + 19, str(i + 1), size=10.5, color=MUTED))

    # геометричний закон r(1−r)^(k−1): крапки + пунктир
    pts = [(X(i), Y((1 - r) ** i * r)) for i in range(K)]
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="1,4" stroke-linecap="round"/>' % (d, INK))
    for x, y in pts:
        p.append(circle(x, y, 3.4, fill=BG, stroke=INK, sw=2.0))

    # вертикаль на середній = 1/r = 10  (k=10 → i=9)
    xm = X(9)
    p.append(line(xm, yb, xm, yt + 30, color=FIELD, sw=2.2, dash="6,4"))
    b, _, _ = textbox(xm + 74, yt + 22, "середня пачка\n= 1/r = 10 бітів", size=12, bold=True,
                      color=FIELD, fill=GFILL, stroke=FIELD, sw=1.8, pad=9)
    p.append(b)

    # легенда (верх-право)
    lx, ly = 566, 118
    p.append(rect(lx, ly - 12, 20, 16, fill=BFILL, stroke=BSTRK, sw=1.5, rx=2))
    p.append(text(lx + 30, ly + 2, "виміряно (симуляція 20 млн бітів)", size=12, color=INK, anchor="start"))
    p.append('<path d="M %d %d L %d %d" stroke="%s" stroke-width="2.4" stroke-dasharray="1,4" stroke-linecap="round"/>' % (lx + 2, ly + 22, lx + 18, ly + 22, INK))
    p.append(circle(lx + 10, ly + 22, 3.4, fill=BG, stroke=INK, sw=2.0))
    p.append(text(lx + 30, ly + 26, "геометричний закон  r·(1−r)^(k−1)", size=12, color=INK, anchor="start"))

    p.append(text(x0 - 6, yt - 20, "частка пачок такої довжини", size=12, color=MUTED, anchor="start", italic=True))
    p.append(text((x0 + x1) / 2, yb + 44, "довжина пачки k — скільки бітів поспіль канал сидить у стані B",
                  size=12.5, color=INK))
    p.append(text(W / 2, H - 16,
                  "виміряний спад лягає точно на геометричний закон — «липкий» стан породжує саме такий розподіл, із середньою 1/r",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "dwell-hist.svg"), W, H, *p,
           title="Довжини пачок: геометричний спад, середня ≈ 1/r")


# ── interleave gain: невиправні блоки без/з перемішуванням (лог-шкала) ────────

def fig_interleave_gain():
    import math
    W, H = 880, 500
    p = []
    # той самий потік 20 млн бітів; блок L=100, виправляє t=4
    bars = [("без\nперемішування", 6471, "3.24 %", BFILL, BSTRK),
            ("D = 10",              357,  "0.18 %", GFILL, GSTRK),
            ("D = 20",              50,   "0.025 %", GFILL, GSTRK),
            ("D = 40",              17,   "0.0085 %", GFILL, GSTRK)]
    floor = 12
    x0, x1 = 150, 806
    yb, yt = 410, 116
    slot = (x1 - x0) / len(bars)
    bw = slot * 0.56

    def Ylog(v):
        return yb - math.log10(v) / 4.0 * (yb - yt)

    # осі + лог-сітка
    p.append(line(x0 - 8, yb, x1, yb, color=INK, sw=2.0))
    p.append(line(x0 - 8, yb, x0 - 8, yt - 6, color=INK, sw=2.0))
    # верхню (10⁴) сітку-лінію не малюємо: жоден стовпець туди не сягає (макс. 6471),
    # а лінія впритул до підпису над найвищим стовпцем перетинала б його текст
    for e in range(0, 4):
        v = 10 ** e
        yy = Ylog(v)
        p.append(line(x0 - 8, yy, x1, yy, color="#e6e8ec", sw=1.2))
        p.append(text(x0 - 14, yy + 4, "%d" % v, size=11, color=MUTED, anchor="end"))

    # стовпці
    for j, (lab, val, rate, fill, strk) in enumerate(bars):
        cx = x0 + (j + 0.5) * slot
        yy = Ylog(val)
        p.append(rect(cx - bw / 2, yy, bw, yb - yy, fill=fill, stroke=strk, sw=2.2, rx=4))
        p.append(text(cx, yy - 26, "%d" % val, size=15, color=strk, bold=True))
        p.append(text(cx, yy - 10, "блоків  " + rate, size=11.5, color=MUTED))
        p.append(mtext(cx, yb + 22, lab.split("\n"), size=12.5, color=INK, bold=True))

    # межа каналу без пам'яті
    yf = Ylog(floor)
    p.append(line(x0 - 8, yf, x1, yf, color=NEG, sw=2.2, dash="7,5"))
    # підпис — у вільному куті над стовпцями (жоден стовпець туди не сягає,
    # так уникаємо накладання на D=40 і його цифри)
    b, _, _ = textbox(x1 - 132, yt + 28, "межа каналу без пам'яті\n(той самий BER) ≈ 12 блоків", size=11.5,
                      color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.6, pad=8, min_w=210)
    p.append(b)

    p.append(text(x0 - 14, yt - 22, "невиправних блоків (лог-шкала)", size=12, color=MUTED, anchor="start", italic=True))
    p.append(text(W / 2, H - 16,
                  "той самий потік і той самий код — глибша перемішка розтягує пачку сильніше, аж поки втрати не сядуть на межу рівномірного шуму",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "interleave-gain.svg"), W, H, *p,
           title="Перемішування зводить пачковий канал до межі каналу без пам'яті")


# ── timeline: шість віхів історії моделі ──────────────────────────────────────

def fig_timeline():
    W, H = 980, 460
    p = []

    x0, x1 = 90, 890
    ay = 230

    # позиції — за ПОРЯДКОМ подій (рівні слоти), не пропорційно рокам:
    # травень і вересень 1960-го лягли б майже впритул на істинній шкалі часу
    # і написи наклались би одне на одне, тож вісь тут схематична, не метрична
    events = [
        (0, "1948", "Шеннон:\nпропускна здатність\nдля каналу без пам'яті", False, "up"),
        (1, "1958", "Bell 101:\nперший модем\nдля комп'ютерів", False, "down"),
        (2, "трав. 1960", "Александер–Гриб–Наст:\nпольовий вимір лінії", False, "up"),
        (3, "вер. 1960", "Гілберт, BSTJ т.39:\nдвостановий канал,\nдобрий стан бездоганний", True, "down"),
        (4, "1963", "Елліот, BSTJ т.42:\nпомилки й у доброму стані", True, "up"),
        (5, "1967", "Фрічман:\nбільше станів", False, "down"),
    ]
    NSLOT = len(events) - 1

    def X(i):
        return x0 + i / float(NSLOT) * (x1 - x0)

    p.append(line(x0 - 10, ay, x1 + 10, ay, color=INK, sw=2.4))
    p.append(text(x1 + 10, ay + 5, "→", size=18, color=INK, anchor="start"))

    for i, lab, note, framed, side in events:
        xx = X(i)
        p.append(circle(xx, ay, 6.5, fill=(BFILL if framed else GFILL), stroke=(BSTRK if framed else GSTRK), sw=2.4))
        if side == "up":
            ty = ay - 30
            p.append(line(xx, ay - 8, xx, ty + 14, color=MUTED, sw=1.4))
            p.append(text(xx, ty, lab, size=13.5, color=INK, bold=True))
            box, bw, bh = textbox(xx, ty - 46, note, size=11, fill=(BFILL if framed else "#f4f6f8"),
                                  stroke=(BSTRK if framed else "#c9ced6"), sw=(2.4 if framed else 1.4), pad=9)
            p.append(box)
        else:
            ty = ay + 34
            p.append(line(xx, ay + 8, xx, ty - 14, color=MUTED, sw=1.4))
            p.append(text(xx, ty, lab, size=13.5, color=INK, bold=True))
            box, bw, bh = textbox(xx, ty + 50, note, size=11, fill=(BFILL if framed else "#f4f6f8"),
                                  stroke=(BSTRK if framed else "#c9ced6"), sw=(2.4 if framed else 1.4), pad=9)
            p.append(box)

    p.append(text(W / 2, H - 16,
                  "дві виділені замітки — Гілберт і Елліот — не в порожнечі: перед ними Шеннонова межа й потреба гнати дані телефоном,\n"
                  "поруч — той самий вимір поля, що показав пачки; по тому — багатші моделі",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Від Шеннонової межі до моделі, що клубиться")


# ── runlen: геометричний розподіл довжини пачки ───────────────────────────────

def fig_runlen():
    W, H = 880, 480
    p = []
    r = 0.1
    K = 22
    x0, x1 = 104, 830
    yb, yt = 400, 110
    probs = [(1 - r) ** (k - 1) * r for k in range(1, K + 1)]
    ymax = max(probs) * 1.12
    colw = (x1 - x0) / K
    bw = colw * 0.62

    def X(k):
        return x0 + (k - 1 + 0.5) * colw

    def Y(v):
        return yb - v / ymax * (yb - yt)

    p.append(line(x0, yb, x1 + 6, yb, color=INK, sw=2.0))
    p.append(line(x0, yb, x0, yt - 6, color=INK, sw=2.0))
    for v in (0.02, 0.04, 0.06, 0.08, 0.10):
        p.append(line(x0 - 6, Y(v), x0, Y(v), color=INK, sw=1.6))
        p.append(text(x0 - 11, Y(v) + 4, "%.2f" % v, size=11, color=MUTED, anchor="end"))

    for k, v in enumerate(probs, start=1):
        p.append(rect(X(k) - bw / 2, Y(v), bw, yb - Y(v), fill=BFILL, stroke=BSTRK, sw=1.5, rx=2))
    for k in range(1, K + 1):
        if k % 2 == 1 or k == K:
            p.append(text(X(k), yb + 19, str(k), size=10.5, color=MUTED))

    xm = X(10)
    p.append(line(xm, yb, xm, yt + 26, color=FIELD, sw=2.2, dash="6,4"))
    b, _, _ = textbox(xm + 92, yt + 20, "середнє 1/r = 10\n(правіше за моду k=1)", size=12, bold=True,
                      color=FIELD, fill=GFILL, stroke=FIELD, sw=1.8, pad=9)
    p.append(b)

    p.append(text(x0 - 6, yt - 20, "P(пачка = k)", size=12, color=MUTED, anchor="start", italic=True))
    p.append(text((x0 + x1) / 2, yb + 44, "довжина пачки k тактів  ·  P(пачка = k) = (1 − r)^(k−1) · r,  r = 0.1",
                  size=12.5, color=INK))
    p.append(text(W / 2, H - 16,
                  "одиночок найбільше — найвищий стовпчик при k = 1, — але довгий геометричний хвіст тягне середнє далеко праворуч від моди",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "runlen.svg"), W, H, *p,
           title="Геометричний розподіл довжини пачки")


# ── autocorr: коефіцієнт автокореляції ρ(k), пачковий проти безпам'ятного ─────

def fig_autocorr():
    W, H = 880, 480
    p = []
    lam = 0.899
    rho1 = 0.36
    Kmax = 30
    x0, x1 = 110, 826
    yb, yt = 400, 110

    def X(k):
        return x0 + k / float(Kmax) * (x1 - x0)

    def Y(v):
        return yb - v * (yb - yt)

    p.append(line(x0, yb, x1 + 6, yb, color=INK, sw=2.0))
    p.append(line(x0, yb, x0, yt - 6, color=INK, sw=2.0))
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        p.append(line(x0 - 6, Y(v), x0, Y(v), color=INK, sw=1.6))
        p.append(text(x0 - 11, Y(v) + 4, "%.2f" % v, size=11, color=MUTED, anchor="end"))
    for k in (0, 5, 10, 15, 20, 25, 30):
        p.append(text(X(k), yb + 20, str(k), size=10.5, color=MUTED))

    # крива Гілберта–Елліота: стрибок 1 → rho1 на k=1, далі геометрично
    ge_pts = [(X(0), Y(1.0))]
    for k in range(1, Kmax + 1):
        ge_pts.append((X(k), Y(rho1 * lam ** (k - 1))))
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in ge_pts[:2])
    p.append('<path d="M %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="2,3"/>' %
             (ge_pts[0][0], ge_pts[0][1], ge_pts[1][0], ge_pts[1][1], BSTRK))
    d2 = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in ge_pts[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d2, BSTRK))
    p.append(circle(ge_pts[0][0], ge_pts[0][1], 3.6, fill=BG, stroke=BSTRK, sw=2.0))
    for x, y in ge_pts[1::3]:
        p.append(circle(x, y, 3.2, fill=BG, stroke=BSTRK, sw=1.8))

    # крива каналу без пам'яті: стрибок 1 → 0 на k=1, далі нуль
    p.append('<path d="M %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="2,3"/>' %
             (X(0), Y(1.0), X(1), Y(0.0), NEG))
    p.append(line(X(1), Y(0.0), X(Kmax), Y(0.0), color=NEG, sw=2.6))
    p.append(circle(X(0), Y(1.0), 3.6, fill=BG, stroke=NEG, sw=2.0))

    # спільна точка при k=0
    p.append(circle(X(0), Y(1.0), 4.2, fill=BG, stroke=INK, sw=2.2))

    # час кореляції ≈ 10
    xc = X(10)
    p.append(line(xc, yb, xc, yt + 24, color=FIELD, sw=2.0, dash="6,4"))
    b, _, _ = textbox(xc + 96, yt + 46, "час кореляції\n≈ 1/(p+r) ≈ 10", size=12, bold=True,
                      color=FIELD, fill=GFILL, stroke=FIELD, sw=1.8, pad=9)
    p.append(b)

    # легенда
    lx, ly = 560, 132
    p.append(line(lx, ly, lx + 30, ly, color=BSTRK, sw=2.6))
    p.append(text(lx + 38, ly + 4, "Гілберт–Елліот: спад геометрично, темп λ", size=12, color=INK, anchor="start"))
    p.append(line(lx, ly + 26, lx + 30, ly + 26, color=NEG, sw=2.6))
    p.append(text(lx + 38, ly + 30, "без пам'яті: обвал у 0 одразу", size=12, color=INK, anchor="start"))

    p.append(text(x0 - 6, yt - 20, "ρ(k)", size=13, color=MUTED, anchor="start", italic=True))
    p.append(text((x0 + x1) / 2, yb + 46, "лаг k (бітів)", size=12.5, color=INK))
    p.append(text(W / 2, H - 16,
                  "той самий ⟨BER⟩ у обох каналів при k = 0 — але за парами видно все: пачковий тримає додатну кореляцію, незалежний обвалюється в нуль",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "autocorr.svg"), W, H, *p,
           title="Автокореляція помилок: підпис пачки")


if __name__ == "__main__":
    fig_states()
    fig_trace()
    fig_interleave()
    fig_dwell_hist()
    fig_interleave_gain()
    fig_timeline()
    fig_runlen()
    fig_autocorr()
    print("OK: figures written to", OUT)
