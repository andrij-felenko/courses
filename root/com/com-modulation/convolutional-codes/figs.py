# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── спільна модель коду (7,5), K=3, швидкість 1/2 ─────────────────────────────
# стани (за індексом): 0=00, 1=01, 2=10, 3=11  (біти пам'яті u₍ₖ₋₁₎u₍ₖ₋₂₎)
NEXT = {0: {0: 0, 1: 2}, 1: {0: 0, 1: 2}, 2: {0: 1, 1: 3}, 3: {0: 1, 1: 3}}
OBITS = {0: {0: "00", 1: "11"}, 1: {0: "11", 1: "00"},
         2: {0: "10", 1: "01"}, 3: {0: "01", 1: "10"}}
SNAME = ["00", "01", "10", "11"]

GRN = "#27ae60"   # FIELD — справжній шлях / вхід
RED = "#c0392b"   # POS — помилка / хибний шлях
BLU = "#2457d6"   # NEG — другий вихід
GREY = "#c2c8d0"

# приклад: вхід 1 0 1 1 0 0  →  вихід 11 10 00 01 01 11
EX_IN = [1, 0, 1, 1, 0, 0]
EX_ST = [0, 2, 1, 2, 3, 1, 0]
EX_OUT = ["11", "10", "00", "01", "01", "11"]


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, color, sw, d)


def xnode(cx, cy, r=15, color=INK):
    """Суматор XOR: кружок із ⊕."""
    return (circle(cx, cy, r, fill=BG, stroke=color, sw=2.2) +
            line(cx - r * 0.7, cy, cx + r * 0.7, cy, color=color, sw=1.6) +
            line(cx, cy - r * 0.7, cx, cy + r * 0.7, color=color, sw=1.6))


# ── encoder: зсувний регістр із відводами ────────────────────────────────────

def fig_encoder():
    W, H = 840, 430
    p = []

    # три комірки регістра
    cx = [230, 380, 530]
    cw, cy0, ch = 118, 150, 66
    labels = ["uₖ", "u₍ₖ₋₁₎", "u₍ₖ₋₂₎"]
    for i, x in enumerate(cx):
        p.append(rect(x - cw / 2, cy0, cw, ch, fill="#f4f6f8", stroke=INK, sw=2.0, rx=6))
        p.append(text(x, cy0 + ch / 2 + 6, labels[i], size=17, color=INK, bold=True))
    # стрілки зсуву між комірками
    for i in range(2):
        p.append(arrow(cx[i] + cw / 2 + 4, cy0 + ch / 2, cx[i + 1] - cw / 2 - 4, cy0 + ch / 2, sw=1.8))
    # вхідний потік
    p.append(text(150, 118, "вхідний потік даних", size=12.5, color=INK))
    p.append(arrow(96, cy0 + ch / 2, cx[0] - cw / 2 - 4, cy0 + ch / 2, sw=2.2))
    p.append(text(92, cy0 + ch / 2 + 5, "…u₃u₂u₁u₀", size=13, color=MUTED, anchor="end"))
    # дужка «пам'ять»
    my = cy0 + ch + 20
    p.append(line(cx[1] - cw / 2, my, cx[2] + cw / 2, my, color=MUTED, sw=1.4))
    p.append(line(cx[1] - cw / 2, my, cx[1] - cw / 2, my - 8, color=MUTED, sw=1.4))
    p.append(line(cx[2] + cw / 2, my, cx[2] + cw / 2, my - 8, color=MUTED, sw=1.4))
    p.append(text((cx[1] + cx[2]) / 2, my + 18, "пам'ять — 2 біти", size=12, color=MUTED, italic=True))

    # суматор v1 (усі три відводи) — угорі
    vy1 = 92
    sx1 = 668
    bus1 = 96
    for x in cx:                       # відводи з верху комірок
        p.append(circle(x, cy0, 3.3, fill=GRN, stroke=GRN, sw=1))
        p.append(line(x, cy0, x, bus1, color=GRN, sw=1.8))
    p.append(line(cx[0], bus1, sx1 - 16, bus1, color=GRN, sw=1.8))
    p.append(xnode(sx1, vy1, 15, GRN))
    p.append(arrow(sx1 + 16, vy1, sx1 + 74, vy1, color=GRN, sw=2.2))
    p.append(text(sx1 + 90, vy1 + 5, "v1", size=16, color=GRN, bold=True, anchor="start"))

    # суматор v2 (крайні відводи 0 і 2) — унизу
    vy2 = 316
    sx2 = 668
    bus2 = 300
    for x in (cx[0], cx[2]):
        p.append(circle(x, cy0 + ch, 3.3, fill=BLU, stroke=BLU, sw=1))
        p.append(line(x, cy0 + ch, x, bus2, color=BLU, sw=1.8))
    p.append(line(cx[0], bus2, sx2 - 16, bus2, color=BLU, sw=1.8))
    p.append(line(sx2, bus2, sx2, vy2 + 16, color=BLU, sw=1.8))
    p.append(xnode(sx2, vy2, 15, BLU))
    p.append(arrow(sx2 + 16, vy2, sx2 + 74, vy2, color=BLU, sw=2.2))
    p.append(text(sx2 + 90, vy2 + 5, "v2", size=16, color=BLU, bold=True, anchor="start"))

    # підписи генераторів біля суматорів
    p.append(text(sx1, vy1 - 30, "g1 = 111₂ = 7₈", size=12.5, color=GRN, bold=True))
    p.append(text(sx1, vy1 - 14, "усі три відводи", size=11, color=MUTED, italic=True))
    p.append(text(sx2, vy2 + 34, "g2 = 101₂ = 5₈", size=12.5, color=BLU, bold=True))
    p.append(text(sx2, vy2 + 50, "крайні відводи", size=11, color=MUTED, italic=True))

    box, bw, bh = textbox(W / 2, H - 40,
                          "один вхідний біт → два вихідні (v1, потім v2)  ·  швидкість 1/2  ·  довжина обмеження K = 3",
                          size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "encoder.svg"), W, H, *p,
           title="Кодер (7,5): зсувний регістр із відводами XOR")


# ── trellis: розгорнутий у часі автомат ──────────────────────────────────────

def fig_trellis():
    W, H = 1120, 470
    p = []

    ncol = 7
    x = [110 + i * 150 for i in range(ncol)]      # такти 0..6
    yr = [96, 186, 276, 366]                       # рядки станів 00,01,10,11

    # підписи станів ліворуч
    for s in range(4):
        p.append(text(x[0] - 54, yr[s] + 5, SNAME[s], size=14, color=INK, bold=True, anchor="middle"))
    p.append(text(x[0] - 54, yr[0] - 34, "стан", size=12, color=MUTED, italic=True))
    # мітки тактів
    for t in range(ncol):
        p.append(text(x[t], H - 74, "t%d" % t, size=11.5, color=MUTED))

    # усі можливі переходи — тонко (структура автомата)
    for t in range(ncol - 1):
        for s in range(4):
            for u in (0, 1):
                ns = NEXT[s][u]
                p.append(line(x[t] + 11, yr[s], x[t + 1] - 11, yr[ns],
                              color=GREY, sw=1.2, dash="5 4" if u else None))

    # вузли станів
    for t in range(ncol):
        for s in range(4):
            p.append(circle(x[t], yr[s], 8, fill=BG, stroke=MUTED, sw=1.6))

    # підсвічений шлях прикладу
    for t in range(len(EX_ST) - 1):
        s, ns = EX_ST[t], EX_ST[t + 1]
        p.append(line(x[t] + 10, yr[s], x[t + 1] - 10, yr[ns], color=GRN, sw=3.4))
    for t in range(len(EX_ST)):
        p.append(circle(x[t], yr[EX_ST[t]], 8.5, fill="#eafaf0", stroke=GRN, sw=2.8))
    # підписи виходів уздовж шляху (над серединою ребра, збоку від лінії)
    for t in range(len(EX_OUT)):
        s, ns = EX_ST[t], EX_ST[t + 1]
        mx, midy = (x[t] + x[t + 1]) / 2, (yr[s] + yr[ns]) / 2
        off = -14 if ns <= s else 16
        p.append(text(mx, midy + off, EX_OUT[t], size=13, color=GRN, bold=True))

    # легенда — рядком унизу
    ly = H - 34
    lx = x[0] - 54
    p.append(line(lx, ly, lx + 26, ly, color=GREY, sw=2.0))
    p.append(text(lx + 32, ly + 4, "вхід 0", size=11.5, color=INK, anchor="start"))
    lx += 130
    p.append(line(lx, ly, lx + 26, ly, color=GREY, sw=2.0, dash="5 4"))
    p.append(text(lx + 32, ly + 4, "вхід 1", size=11.5, color=INK, anchor="start"))
    lx += 130
    p.append(line(lx, ly, lx + 26, ly, color=GRN, sw=3.4))
    p.append(text(lx + 32, ly + 4, "шлях прикладу 1 0 1 1 0 0  →  11 10 00 01 01 11", size=11.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "trellis.svg"), W, H, *p,
           title="Ґратка: автомат кодера, розгорнутий у часі")


# ── viterbi: два повні шляхи, менша відстань перемагає ───────────────────────

def hd(a, b):
    return sum(1 for i in range(len(a)) if a[i] != b[i])


def fig_viterbi():
    W, H = 1120, 500
    p = []

    ncol = 7
    x = [130 + i * 148 for i in range(ncol)]
    yr = [150, 232, 314, 396]

    recv = ["11", "11", "00", "01", "01", "11"]   # прийняте (2-й біт 2-ї пари перевернуто)
    # справжній шлях
    tr_st = EX_ST
    tr_out = EX_OUT
    # найближчий хибний шлях (вхід 1 1 1 0 0 0), теж старт/фініш у 00
    fa_st = [0, 2, 3, 3, 1, 0, 0]
    fa_out = ["11", "01", "10", "01", "11", "00"]

    # прийняті пари над відповідними тактами-переходами
    for t in range(len(recv)):
        mx = (x[t] + x[t + 1]) / 2
        b0, b1 = recv[t][0], recv[t][1]
        # 2-й біт 2-ї пари (t==1) — перевернутий, малюємо червоним
        c1 = RED if t == 1 else INK
        p.append(text(mx - 6, 74, b0, size=15, color=INK, bold=True))
        p.append(text(mx + 6, 74, b1, size=15, color=c1, bold=True))
    p.append(text(x[0] - 70, 74, "прийнято:", size=12.5, color=MUTED, anchor="end"))
    p.append(text((x[1] + x[2]) / 2, 52, "↑ перевернутий біт", size=11, color=RED, bold=True))

    # мітки станів ліворуч + сітка вузлів
    for s in range(4):
        p.append(text(x[0] - 58, yr[s] + 5, SNAME[s], size=13, color=MUTED, bold=True))
    for t in range(ncol):
        for s in range(4):
            p.append(circle(x[t], yr[s], 6.5, fill=BG, stroke="#dfe3e8", sw=1.4))

    # хибний шлях (червоний, трохи нижче)
    for t in range(len(fa_st) - 1):
        s, ns = fa_st[t], fa_st[t + 1]
        p.append(line(x[t] + 9, yr[s] + 4, x[t + 1] - 9, yr[ns] + 4, color=RED, sw=2.6))
    # справжній шлях (зелений)
    for t in range(len(tr_st) - 1):
        s, ns = tr_st[t], tr_st[t + 1]
        p.append(line(x[t] + 9, yr[s], x[t + 1] - 9, yr[ns], color=GRN, sw=3.2))
    for t in range(len(tr_st)):
        p.append(circle(x[t], yr[tr_st[t]], 7, fill="#eafaf0", stroke=GRN, sw=2.4))

    # відстані на кожному ребрі справжнього шляху (зелені) і хибного (червоні)
    for t in range(len(recv)):
        mx = (x[t] + x[t + 1]) / 2
        dt = hd(tr_out[t], recv[t])
        s, ns = tr_st[t], tr_st[t + 1]
        p.append(text(mx, (yr[s] + yr[ns]) / 2 - 12, "+%d" % dt, size=12, color=GRN, bold=True))
        df = hd(fa_out[t], recv[t])
        s2, ns2 = fa_st[t], fa_st[t + 1]
        p.append(text(mx, (yr[s2] + yr[ns2]) / 2 + 24, "+%d" % df, size=12, color=RED, bold=True))

    tot_t = sum(hd(tr_out[t], recv[t]) for t in range(len(recv)))
    tot_f = sum(hd(fa_out[t], recv[t]) for t in range(len(recv)))

    # підсумкові плашки
    b, bw, bh = textbox(x[0] + 130, H - 66,
                        "справжній шлях:  відстань = %d" % tot_t, size=12.5, bold=True,
                        fill="#eafaf0", stroke=GRN, sw=2.0, pad=10)
    p.append(b)
    b, bw, bh = textbox(x[0] + 130, H - 30,
                        "найближчий хибний:  відстань = %d" % tot_f, size=12.5, bold=True,
                        fill="#fdecea", stroke=RED, sw=2.0, pad=10)
    p.append(b)

    b, bw, bh = textbox(W - 300, H - 48,
                        "%d < %d  →  перемагає зелений шлях\nповідомлення 1 0 1 1 0 0 відновлено" % (tot_t, tot_f),
                        size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(b)

    render(os.path.join(OUT, "viterbi.svg"), W, H, *p,
           title="Декодування: найближчий за відстанню шлях перемагає")


# ── pmtable: DP-таблиця метрик шляху + простеження назад (для proj) ──────────

def fig_pmtable():
    """Те, що декодер реально тримає в памʼяті: метрика на кожен стан на кожному
    такті (add-compare-select заповнює клітини зліва направо) + вцілілий шлях,
    простежений назад від переможця. Числа пораховано з прикладу статті."""
    W, H = 1120, 590
    p = []

    recv = ["11", "11", "00", "01", "01", "11"]   # прийняте, 2-й біт 2-ї пари побито
    ncol = 7
    x = [170 + i * 130 for i in range(ncol)]       # такти 0..6
    yr = [140, 224, 308, 392]                      # стани 00,01,10,11
    cw, chh = 74, 50

    # ── ACS уперед: заповнюємо pm[t][s] і back[t][s] = (prev, u) ──
    INF = float("inf")
    pm = [[INF] * 4 for _ in range(ncol)]
    back = [[None] * 4 for _ in range(ncol)]
    pm[0][0] = 0
    for t in range(len(recv)):
        for s in range(4):
            if pm[t][s] == INF:
                continue
            for u in (0, 1):
                ns = NEXT[s][u]
                bm = hd(OBITS[s][u], recv[t])
                c = pm[t][s] + bm
                if c < pm[t + 1][ns]:
                    pm[t + 1][ns] = c
                    back[t + 1][ns] = (s, u)
    # простеження назад від стану 00
    surv = [0] * ncol
    s = 0
    surv[ncol - 1] = 0
    for t in range(ncol - 1, 0, -1):
        ps, _ = back[t][s]
        surv[t - 1] = ps
        s = ps

    # ── прийняті пари над стовпцями-переходами ──
    p.append(text(x[0] - 88, 78, "прийнято:", size=12.5, color=MUTED, anchor="end"))
    for t in range(len(recv)):
        mx = (x[t] + x[t + 1]) / 2
        c1 = RED if t == 1 else INK
        p.append(text(mx - 8, 82, recv[t][0], size=16, color=INK, bold=True))
        p.append(text(mx + 8, 82, recv[t][1], size=16, color=c1, bold=True))
    p.append(text((x[1] + x[2]) / 2, 56, "↑ побитий біт", size=11.5, color=RED, bold=True))

    # ── мітки станів ліворуч ──
    p.append(text(x[0] - 88, yr[0] - 40, "стан", size=12, color=MUTED, italic=True))
    for s in range(4):
        p.append(text(x[0] - 88, yr[s] + 5, SNAME[s], size=14, color=INK, bold=True, anchor="middle"))

    # ── зелений вцілілий шлях (лінії між центрами survivor-клітин) ──
    for t in range(ncol - 1):
        p.append(line(x[t], yr[surv[t]], x[t + 1], yr[surv[t + 1]], color=FIELD, sw=3.4))

    # ── клітини з метриками ──
    for t in range(ncol):
        for s in range(4):
            cx, cy = x[t], yr[s]
            val = pm[t][s]
            on_surv = (surv[t] == s)
            if val == INF:
                p.append(rect(cx - cw / 2, cy - chh / 2, cw, chh, fill="#f1f3f5", stroke="#d3d8de", sw=1.4, rx=8))
                p.append(text(cx, cy + 6, "∞", size=18, color="#aeb4bc"))
            elif on_surv:
                p.append(rect(cx - cw / 2, cy - chh / 2, cw, chh, fill="#eafaf0", stroke=FIELD, sw=2.8, rx=8))
                p.append(text(cx, cy + 6, str(val), size=19, color=FIELD, bold=True))
            else:
                p.append(rect(cx - cw / 2, cy - chh / 2, cw, chh, fill=BG, stroke="#c2c8d0", sw=1.6, rx=8))
                p.append(text(cx, cy + 6, str(val), size=18, color=INK))

    # переможець — обвід і тег
    wx, wy = x[6], yr[0]
    p.append(rect(wx - cw / 2 - 5, wy - chh / 2 - 5, cw + 10, chh + 10, fill="none", stroke=FIELD, sw=2.2, rx=10))
    p.append(text(wx, wy - chh / 2 - 14, "переможець", size=11.5, color=FIELD, bold=True))

    # стрілка «простеження назад» уздовж верху
    ay = 108
    p.append(arrow(x[6], ay, x[1], ay, color=FIELD, sw=2.2))
    p.append(text((x[3] + x[4]) / 2, ay - 8, "простеження назад від найменшої метрики", size=11.5, color=FIELD, bold=True))

    # мітки тактів під сіткою
    for t in range(ncol):
        p.append(text(x[t], yr[3] + chh / 2 + 26, "t%d" % t, size=11.5, color=MUTED))

    # ── дві підсумкові плашки внизу ──
    b, bw, bh = textbox(x[0] + 210, H - 44,
                        "add-compare-select у стан 00 на t6:  3+2 = 5  проти  1+0 = 1  →  лишаємо 1",
                        size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=11)
    p.append(b)
    b, bw, bh = textbox(W - 300, H - 44,
                        "вцілілий шлях → 1 0 1 1 0 0\nпомилку стерто",
                        size=12.5, bold=True, fill="#eafaf0", stroke=FIELD, sw=2.0, pad=11)
    p.append(b)

    render(os.path.join(OUT, "pmtable.svg"), W, H, *p,
           title="Таблиця метрик: що декодер тримає в памʼяті на кожному такті")


# ── history: код 1955 → декодер 1967, і шлях між ними (для hist-вставки) ──────

def fig_history():
    W, H = 1080, 815
    p = []

    AX = 312                     # вертикальна вісь часу
    p.append(line(AX, 66, AX, 762, color=MUTED, sw=2.2))

    # рядки-віхи: (y, рік, колір-точки, велика?, заливка, обвід, рядок1, рядок2)
    rows = [
        (100, "1948", MUTED, False, FILL, MUTED,
         "Шеннон — теорема кодування каналу: надійність нижче межі досяжна",
         "обіцянка без рецепту: самого коду теорема не дає"),
        (190, "1955", FIELD, False, "#eafaf0", FIELD,
         "Еліас — згорткові коди: надлишок вплетено в потік, а не в блоки",
         "код народжено; доброго декодера до нього ще немає"),
        (280, "1957", NEG, False, "#eef2fd", NEG,
         "Возенкрафт — послідовне декодування, перший практичний метод",
         "майже оптимальне, та обсяг лічби — випадковий, з важким хвостом"),
        (370, "1963", NEG, False, "#eef2fd", NEG,
         "Фано — послідовне декодування без стека, ощадніше на пам'ять",
         "вище порогової швидкості лічба вибухає — буфер переповнюється"),
        (460, "1963", NEG, False, "#eef2fd", NEG,
         "Мессі — порогове (мажоритарне) декодування: просте й швидке",
         "лічба обмежена, зате код помітно слабший за оптимум"),
        (550, "1967", FIELD, True, "#eafaf0", FIELD,
         "Вітербі — асимптотично оптимальний алгоритм, СТАЛА лічба на такт",
         "народжений як доказ меж помилки й засіб пояснити студентам"),
        (640, "1969", INK, False, FILL, MUTED,
         "Омура — це пряме динамічне програмування (ML для автомата)",
         "оптимальність випливає одразу, щойно впізнати в ньому DP"),
        (730, "1973", INK, False, FILL, MUTED,
         "Форні — це декодування за максимумом правдоподібності; ґратка",
         "дає ім'я «алгоритм Вітербі» і вжиток далеко за межами кодів"),
    ]

    cx0, cw = 356, 690           # картка події
    for (y, yr, dot, big, fill, stroke, l1, l2) in rows:
        p.append(line(AX + 8, y, cx0 - 4, y, color=MUTED, sw=1.4))
        p.append(text(AX - 26, y + 5, yr, size=15, color=(FIELD if big else INK),
                      bold=big, anchor="end"))
        if big:
            p.append(circle(AX, y, 13, fill="#eafaf0", stroke=FIELD, sw=1.6))
            p.append(circle(AX, y, 7.5, fill=FIELD, stroke=FIELD, sw=1.6))
        else:
            p.append(circle(AX, y, 7, fill=BG, stroke=dot, sw=2.4))
        p.append(fitbox(cx0, y - 30, cw, 60, l1 + "\n" + l2, size=13.5, pad=10,
                        fill=fill, stroke=stroke, sw=1.8))

    # брекет прогалини 1955 → 1967 (ліворуч від осі)
    bx, y1, y2 = 200, 190, 550
    p.append(line(bx, y1, bx, y2, color=POS, sw=2.2))
    p.append(line(bx, y1, bx + 14, y1, color=POS, sw=2.2))
    p.append(line(bx, y2, bx + 14, y2, color=POS, sw=2.2))
    p.append(line(bx, (y1 + y2) / 2, bx - 14, (y1 + y2) / 2, color=POS, sw=2.2))
    b, bw, bh = textbox(116, (y1 + y2) / 2,
                        "≈ 12 років\nпошуку\nпрактичного\nдекодера",
                        size=13, bold=True, color=POS,
                        fill="#fdecea", stroke=POS, sw=1.8, pad=11)
    p.append(b)

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Код 1955 — декодер 1967: дванадцять років між кодом і його переможним декодером")


# ── math-вставка: множення=згортка, спектр відстаней, катастрофічний виток ────

def _cmarker(idn, color):
    return ('<marker id="%s" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>' % (idn, color))


def _carrow(x1, y1, x2, y2, bend=0.0, color=INK, sw=1.8, mid="arrow"):
    """Дугова стрілка (квадратична крива), контрольна точка збоку на bend px."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = (dx * dx + dy * dy) ** 0.5 or 1.0
    nx, ny = -dy / L, dx / L
    cx, cy = mx + nx * bend, my + ny * bend
    frag = ('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f" marker-end="url(#%s)"/>'
            % (x1, y1, cx, cy, x2, y2, color, sw, mid))
    return frag, (cx, cy)


def _selfloop(cx, cy, ux, uy, color=INK, sw=1.8, mid="arrow", reach=54, spread=20):
    px, py = -uy, ux
    x1 = cx + px * spread * 0.5 + ux * 8
    y1 = cy + py * spread * 0.5 + uy * 8
    x2 = cx - px * spread * 0.5 + ux * 8
    y2 = cy - py * spread * 0.5 + uy * 8
    c1x, c1y = cx + px * spread + ux * reach, cy + py * spread + uy * reach
    c2x, c2y = cx - px * spread + ux * reach, cy - py * spread + uy * reach
    return ('<path d="M%.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f" marker-end="url(#%s)"/>'
            % (x1, y1, c1x, c1y, c2x, c2y, x2, y2, color, sw, mid))


def _trim(x1, y1, x2, y2, r1, r2):
    dx, dy = x2 - x1, y2 - y1
    L = (dx * dx + dy * dy) ** 0.5 or 1.0
    ux, uy = dx / L, dy / L
    return x1 + ux * r1, y1 + uy * r1, x2 - ux * r2, y2 - uy * r2


def fig_polymul():
    W, H = 900, 470
    p = []
    ncol = 6
    x0, cw = 262, 92
    xc = [x0 + i * cw for i in range(ncol)]
    pw = ["D⁰", "D¹", "D²", "D³", "D⁴", "D⁵"]
    hy = 92
    for i in range(ncol):
        p.append(text(xc[i], hy, pw[i], size=15, color=MUTED, bold=True))
    p.append(text(x0 - 110, hy, "степінь →", size=12.5, color=MUTED, italic=True))

    shifts = [0, 2, 3]
    rlbl = ["g₁ · D⁰", "g₁ · D²", "g₁ · D³"]
    ry = [140, 186, 232]
    for r, sh in enumerate(shifts):
        p.append(text(x0 - 110, ry[r] + 5, rlbl[r], size=13.5, color=INK, bold=True))
        for i in range(ncol):
            bit = "1" if sh <= i <= sh + 2 else "·"
            col = GRN if bit == "1" else "#cfd6de"
            p.append(text(xc[i], ry[r] + 5, bit, size=17, color=col, bold=(bit == "1")))

    ly = 262
    p.append(line(x0 - 158, ly, xc[-1] + 34, ly, color=INK, sw=1.6))
    p.append(text(x0 - 176, ly - 6, "⊕", size=18, color=INK, bold=True))

    res = ["1", "1", "0", "0", "0", "1"]
    ry2 = 296
    p.append(text(x0 - 110, ry2 + 5, "v₁", size=16, color=BLU, bold=True))
    for i in range(ncol):
        hot = res[i] == "1"
        p.append(text(xc[i], ry2 + 5, res[i], size=18, color=(BLU if hot else "#9aa3ad"), bold=True))

    b, bw, bh = textbox(W / 2, 360,
                        "коефіцієнт при Dⁿ  =  Σ  uᵢ · g₍ₙ₋ᵢ₎   (сума за модулем 2)",
                        size=14, bold=True, fill="#eef2f7", stroke=INK, sw=1.6, pad=12)
    p.append(b)
    b, bw, bh = textbox(W / 2, 412,
                        "u = 1 + D² + D³   ·   g₁ = 1 + D + D²   →   v₁ = 1 + D + D⁵  =  1 1 0 0 0 1",
                        size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=1.6, pad=11)
    p.append(b)

    render(os.path.join(OUT, "polymul.svg"), W, H, *p,
           title="Кодування — це множення многочленів, тобто згортка")


def fig_distspec():
    W, H = 860, 470
    p = []
    base = 360
    left = 150
    ad = [(5, 1), (6, 2), (7, 4), (8, 8)]
    scale = 20.0
    bw = 74
    gap = 150
    bx = [left + 46 + i * gap for i in range(len(ad))]

    p.append(line(left, base, left, 96, color=MUTED, sw=1.6))
    p.append(line(left, base, W - 60, base, color=MUTED, sw=1.6))
    p.append(text(left + 6, 84, "a_d — число шляхів ваги d", size=12, color=MUTED, italic=True, anchor="start"))
    p.append(text(W - 60, base + 24, "вага d", size=12.5, color=MUTED, italic=True, anchor="end"))

    for i, (d, a) in enumerate(ad):
        h = a * scale
        col = GRN if d == 5 else BLU
        p.append(rect(bx[i] - bw / 2, base - h, bw, h, fill=(col if d == 5 else "#eaf0fd"),
                      stroke=col, sw=2.2, rx=4))
        p.append(text(bx[i], base - h - 12, "%d" % a, size=15, color=col, bold=True))
        p.append(text(bx[i], base + 22, "d=%d" % d, size=13.5, color=INK, bold=(d == 5)))

    p.append(text(bx[0], base + 44, "= d_free", size=12.5, color=GRN, bold=True))
    p.append(text(bx[-1] + 92, base - 78, "· · ·", size=22, color=MUTED, bold=True))
    p.append(text(bx[-1] + 92, base - 44, "подвоюється", size=11.5, color=MUTED, italic=True))

    b, bw2, bh2 = textbox(W / 2, 418,
                          "T(D) = D⁵ / (1 − 2D) = D⁵ + 2D⁶ + 4D⁷ + 8D⁸ + …    →    a_d = 2^(d−5)",
                          size=14, bold=True, fill="#f6f4ec", stroke=INK, sw=1.6, pad=12)
    p.append(b)

    render(os.path.join(OUT, "distspec.svg"), W, H, *p,
           title="Спектр відстаней коду (7, 5): один шлях ваги 5, далі — вибух")


def fig_catastrophic():
    W, H = 900, 560
    p = [_cmarker("arrRED", RED), _cmarker("arrMUT", MUTED)]

    R = 32
    pos = {"00": (250, 150), "10": (620, 150), "01": (250, 380), "11": (620, 380)}

    def edge(a, b, lbl, color=MUTED, mid="arrMUT", bend=0.0, loff=(0, 0), sw=1.8, bold=False):
        (x1, y1), (x2, y2) = pos[a], pos[b]
        tx1, ty1, tx2, ty2 = _trim(x1, y1, x2, y2, R + 3, R + 8)
        frag, (cxp, cyp) = _carrow(tx1, ty1, tx2, ty2, bend=bend, color=color, sw=sw, mid=mid)
        p.append(frag)
        lx = (cxp + (x1 + x2) / 2) / 2 + loff[0]
        ly = (cyp + (y1 + y2) / 2) / 2 + loff[1]
        p.append(text(lx, ly, lbl, size=13, color=color, bold=bold))

    edge("00", "10", "1 / 11", loff=(0, -12))
    edge("01", "00", "0 / 01", loff=(-24, 0))
    edge("01", "10", "1 / 10", bend=-48, loff=(-12, 6))
    edge("10", "01", "0 / 10", bend=-48, loff=(16, -4))
    edge("10", "11", "1 / 01", loff=(32, 0))
    edge("11", "01", "0 / 11", loff=(0, 24))

    p.append(_selfloop(*pos["11"], 0.72, 0.72, color=RED, sw=2.6, mid="arrRED", reach=62, spread=22))
    p.append(text(pos["11"][0] + 78, pos["11"][1] + 74, "1 / 00", size=15, color=RED, bold=True))
    p.append(_selfloop(*pos["00"], -0.72, -0.72, color=MUTED, sw=1.6, mid="arrMUT", reach=52, spread=20))
    p.append(text(pos["00"][0] - 70, pos["00"][1] - 62, "0 / 00", size=12.5, color=MUTED))

    for s, (cx, cy) in pos.items():
        hot = (s == "11")
        p.append(circle(cx, cy, R, fill=("#fdecea" if hot else "#f4f6f8"),
                        stroke=(RED if hot else INK), sw=(2.8 if hot else 2.0)))
        p.append(text(cx, cy + 6, s, size=17, color=(RED if hot else INK), bold=True))

    b, bw, bh = textbox(W / 2, 500,
                        "вхід 1 1 1 …:  00 → 10 → 11, далі вічний виток 11 → 11 з виходом 00\n"
                        "нескінченна вага входу  →  скінченна вага виходу  =  катастрофічний кодер",
                        size=13.5, bold=True, fill="#fdecea", stroke=RED, sw=2.0, pad=13)
    p.append(b)

    render(os.path.join(OUT, "catastrophic.svg"), W, H, *p,
           title="Пастка: кодер (1+D, 1+D²) з витком нульової ваги")


if __name__ == "__main__":
    fig_encoder()
    fig_trellis()
    fig_viterbi()
    fig_pmtable()
    fig_history()
    fig_polymul()
    fig_distspec()
    fig_catastrophic()
    print("OK: figures written to", OUT)
