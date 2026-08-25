# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Спільний приклад: блок даних 4×4 + парність рядків (RP) і стовпців (CP) ────
DATA = [
    [1, 0, 1, 1],
    [0, 1, 1, 0],
    [1, 1, 0, 1],
    [0, 0, 1, 1],
]
RP = [r[0] ^ r[1] ^ r[2] ^ r[3] for r in DATA]           # парність кожного рядка
CP = [DATA[0][c] ^ DATA[1][c] ^ DATA[2][c] ^ DATA[3][c] for c in range(4)]
CORNER = RP[0] ^ RP[1] ^ RP[2] ^ RP[3]                   # парність парностей

# ── Геометрія сітки (спільна для всіх фігур) ──────────────────────────────────
CW = 42            # ширина/висота клітинки
STEP = 47          # крок між клітинками даних
X0, Y0 = 186, 95   # лівий-верхній кут першого біта даних
XTRA = 18          # відступ перед колонкою/стрічкою парності

def col_x(c):      # x лівого краю стовпця c (0..3 — дані, 4 — парність)
    return X0 + c * STEP + (XTRA if c == 4 else 0)

def row_y(r):      # y верхнього краю рядка r (0..3 — дані, 4 — парність)
    return Y0 + r * STEP + (XTRA if r == 4 else 0)

PX = col_x(4)      # x колонки парності
PY = row_y(4)      # y стрічки парності
RIGHT = PX + CW    # правий край сітки
BOTTOM = PY + CW   # нижній край сітки

TINT_P = "#eafaf0"   # блідо-зелений — клітинки парності
TINT_C = "#fff5e6"   # блідо-бурштиновий — кутова клітинка
TINT_R = "#fdecea"   # блідо-червоний — підсвічений рядок/стовпець
HOT_R  = "#f7c8c1"   # насиченіший червоний — зіпсована клітинка


def cell(x, y, v, fill=BG, stroke="#cccccc", sw=1.2):
    col = POS if v else NEG
    return (rect(x, y, CW, CW, fill=fill, stroke=stroke, sw=sw, rx=5) +
            text(x + CW / 2, y + CW / 2 + 6, str(v), size=17, color=col, bold=True))


def band(x, y, w, h, color, op):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="5" '
            'fill="%s" opacity="%.2f"/>' % (x, y, w, h, color, op))


def headers(p, bad_cols=(), bad_rows=()):
    """Підписи стовпців (c0..c3, RP) і рядків (r0..r3, CP)."""
    names_c = ["c0", "c1", "c2", "c3", "RP"]
    for c in range(5):
        bad = c in bad_cols
        p.append(text(col_x(c) + CW / 2, Y0 - 16, names_c[c], size=13,
                      color=(POS if bad else MUTED), bold=bad))
    names_r = ["r0", "r1", "r2", "r3", "CP"]
    for r in range(5):
        bad = r in bad_rows
        p.append(text(X0 - 18, row_y(r) + CW / 2 + 5, names_r[r], size=13,
                      color=(POS if bad else MUTED), bold=bad, anchor="end"))


def dividers(p):
    xdiv = (col_x(3) + CW + PX) / 2
    ydiv = (row_y(3) + CW + PY) / 2
    p.append(line(xdiv, Y0 - 6, xdiv, BOTTOM, color="#d0d0d0", sw=1.4, dash="4 4"))
    p.append(line(X0 - 6, ydiv, RIGHT, ydiv, color="#d0d0d0", sw=1.4, dash="4 4"))


def base_grid(p, disp, flips=frozenset(), row_tint=frozenset(),
              col_tint=frozenset(), mark_ok=False):
    """Малює всю сітку 5×5. disp — показувані значення даних (з урахуванням flips)."""
    # дані
    for r in range(4):
        for c in range(4):
            f = BG
            if r in row_tint or c in col_tint:
                f = TINT_R
            if (r, c) in flips:
                f = HOT_R
            hot = (r, c) in flips
            p.append(cell(col_x(c), row_y(r), disp[r][c], fill=f,
                          stroke=(POS if hot else "#cccccc"), sw=(3.2 if hot else 1.2)))
    # колонка парності рядків (RP)
    for r in range(4):
        f = TINT_R if r in row_tint else TINT_P
        p.append(cell(PX, row_y(r), RP[r], fill=f, stroke=FIELD, sw=2.2))
    # стрічка парності стовпців (CP)
    for c in range(4):
        f = TINT_R if c in col_tint else TINT_P
        p.append(cell(col_x(c), PY, CP[c], fill=f, stroke=FIELD, sw=2.2))
    # кут — парність парностей
    p.append(cell(PX, PY, CORNER, fill=TINT_C, stroke=FIELD, sw=2.2))
    # зелені галочки на цілих перевірках
    if mark_ok:
        for r in range(4):
            p.append(text(RIGHT + 16, row_y(r) + CW / 2 + 5, "✓", size=15, color=FIELD, bold=True))
        for c in range(4):
            p.append(text(col_x(c) + CW / 2, BOTTOM + 20, "✓", size=15, color=FIELD, bold=True))


# ── 1. grid: будова коду ──────────────────────────────────────────────────────
def fig_grid():
    W, H = 600, 430
    p = [text(W / 2, 30, "Двовимірна парність: решітка з простих перевірок", size=17, bold=True),
         text(W / 2, 52, "парність окремо вздовж кожного рядка (RP) і кожного стовпця (CP)",
              size=12.5, color=MUTED, italic=True)]
    headers(p)
    dividers(p)
    base_grid(p, DATA)
    # анотація кута
    p.append(text(RIGHT + 14, PY + CW / 2 + 5, "← кут:", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(RIGHT + 14, PY + CW / 2 + 22, "парність", size=12, color=FIELD, anchor="start"))
    p.append(text(RIGHT + 14, PY + CW / 2 + 38, "парностей", size=12, color=FIELD, anchor="start"))
    # легенда
    ly = BOTTOM + 44
    p.append(text(W / 2, ly, "У кожному рядку й у кожному стовпці кількість одиниць — парна.",
                  size=13, color=INK))
    p.append(text(W / 2, ly + 22, "RP — парність рядка   ·   CP — парність стовпця   ·   1 — червоне, 0 — синє",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "grid.svg"), W, H, *p)


# ── 2. locate: одна помилка → перетин рядка й стовпця ─────────────────────────
def fig_locate():
    W, H = 600, 470
    p = [text(W / 2, 30, "Одна помилка: перетин називає винуватця", size=17, bold=True),
         text(W / 2, 52, "зіпсований біт робить непарними парність СВОГО рядка і СВОГО стовпця",
              size=12.5, color=MUTED, italic=True)]
    # перевертаємо біт (r1, c2): 1 → 0
    disp = [row[:] for row in DATA]
    disp[1][2] ^= 1
    headers(p, bad_cols={2}, bad_rows={1})
    dividers(p)
    base_grid(p, disp, flips={(1, 2)}, row_tint={1}, col_tint={2})
    # позначки ✗ на винних перевірках
    p.append(text(RIGHT + 16, row_y(1) + CW / 2 + 5, "✗", size=16, color=POS, bold=True))
    p.append(text(col_x(2) + CW / 2, BOTTOM + 20, "✗", size=16, color=POS, bold=True))
    # висновок під сіткою
    cy = BOTTOM + 52
    p.append(text(W / 2, cy, "винен рядок r1  ✗   ∩   винен стовпець c2  ✗",
                  size=13.5, color=INK, bold=True))
    p.append(text(W / 2, cy + 22, "перетин — клітинка (r1, c2): перевертаємо 0 → 1, блок відновлено",
                  size=13, color=FIELD, bold=True))
    render(os.path.join(OUT, "locate.svg"), W, H, *p)


# ── 3. rectangle: сліпа пляма — чотири кути прямокутника ──────────────────────
def fig_rectangle():
    W, H = 600, 470
    p = [text(W / 2, 30, "Сліпа пляма: прямокутник із чотирьох помилок", size=17, bold=True),
         text(W / 2, 52, "кожен зачеплений рядок і стовпець дістає по ДВІ зміни — парність ціла",
              size=12.5, color=MUTED, italic=True)]
    flips = {(1, 0), (1, 2), (3, 0), (3, 2)}
    disp = [row[:] for row in DATA]
    for (r, c) in flips:
        disp[r][c] ^= 1
    headers(p)
    dividers(p)
    base_grid(p, disp, flips=flips, mark_ok=True)
    # пунктирний прямокутник, чиї кути збігаються з чотирма зіпсованими клітинками
    rx0, ry0 = col_x(0), row_y(1)
    rw = (col_x(2) + CW) - rx0
    rh = (row_y(3) + CW) - ry0
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="none" '
             'stroke="%s" stroke-width="2.2" stroke-dasharray="6 4"/>' % (rx0, ry0, rw, rh, POS))
    # висновок під сіткою
    cy = BOTTOM + 52
    p.append(text(W / 2, cy, "усі парності проходять — детектор мовчить, хоча зіпсовано 4 біти",
                  size=13.5, color=POS, bold=True))
    p.append(text(W / 2, cy + 22, "це найлегша непомітна помилка → мінімальна відстань коду = 4",
                  size=13, color=MUTED, italic=True))
    render(os.path.join(OUT, "rectangle.svg"), W, H, *p)


# ═════════════════════════════════════════════════════════════════════════════
#  Фігури вставки hist-tape-vrc-lrc: геометрія магнітної стрічки
# ═════════════════════════════════════════════════════════════════════════════
import math

TINT_V = "#fdecea"   # блідо-червоний — поперечна вісь (кадр, VRC)
TINT_L = "#e8eefc"   # блідо-синій — поздовжня вісь (доріжка, LRC)
TINT_X = "#f3e8f5"   # перетин двох осей
TINT_G = "#eafaf0"   # блідо-зелений — контрольний символ


def ahead(x, y, dx, dy, color, s=7.0):
    """Наконечник стрілки у точці (x,y), напрямок (dx,dy). Свій, бо svgkit-івський
    marker пофарбований у LINE й кольорових стрілок не дає."""
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    return ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' %
            (x, y,
             x - ux * s * 1.7 + px * s * 0.8, y - uy * s * 1.7 + py * s * 0.8,
             x - ux * s * 1.7 - px * s * 0.8, y - uy * s * 1.7 - py * s * 0.8,
             color))


def carrow(x1, y1, x2, y2, color=LINE, sw=2.2, s=7.0):
    """Кольорова стрілка: лінія + власний наконечник."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ex, ey = x2 - dx / L * s * 1.6, y2 - dy / L * s * 1.6
    return line(x1, y1, ex, ey, color=color, sw=sw) + ahead(x2, y2, dx, dy, color, s)


def bits(seed, n):
    """Детермінований потік бітів (без random — щоб фігури не «дихали»)."""
    out, x = [], seed
    for _ in range(n):
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        out.append((x >> 16) & 1)
    return out


# ── 6. tape-axes: дві фізичні осі стрічки — звідки взялися назви ──────────────
def fig_tape_axes():
    """Семидоріжкова стрічка: кадр стоїть УПОПЕРЕК (VRC), доріжка йде УЗДОВЖ (LRC)."""
    W, H = 720, 500
    NF = 14                      # кадрів даних
    NT = 7                       # доріжок: 6 даних + P
    CWX, CHX = 26, 26
    X0, Y0 = 122, 158
    HOT_F = 5                    # підсвічений кадр (поперечна вісь)
    HOT_T = 3                    # підсвічена доріжка (поздовжня вісь)

    # дані: 6 доріжок × NF кадрів; сьома доріжка — НЕПАРНА парність кадру (правило IBM 726)
    D = [bits(7 + t, NF) for t in range(6)]
    P = [1 ^ D[0][f] ^ D[1][f] ^ D[2][f] ^ D[3][f] ^ D[4][f] ^ D[5][f] for f in range(NF)]
    FRAME = D + [P]                                   # 7 доріжок × NF кадрів
    LRCC = [0] * NT
    for t in range(NT):
        v = 0
        for f in range(NF):
            v ^= FRAME[t][f]
        LRCC[t] = v

    def fx(f):
        return X0 + f * CWX

    GAPX = fx(NF) + 4 * CWX          # кінець порожнього проміжку
    LX = GAPX                        # x кадру LRCC
    BOT = Y0 + NT * CHX

    p = [text(W / 2, 30, "Дві осі магнітної стрічки — і дві назви", size=17, bold=True),
         text(W / 2, 52, "решітку тут не вигадали: її поклала механіка — сім головок упоперек, довжина вздовж",
              size=12.5, color=MUTED, italic=True)]

    # рух стрічки (праворуч угорі, далеко від інших написів)
    p.append(text(596, 76, "рух стрічки", size=11.5, color=MUTED, italic=True))
    p.append(carrow(548, 92, 646, 92, color=MUTED, sw=1.8))

    # клітинки
    for t in range(NT):
        for f in range(NF):
            fill = BG
            if f == HOT_F and t == HOT_T:
                fill = TINT_X
            elif f == HOT_F:
                fill = TINT_V
            elif t == HOT_T:
                fill = TINT_L
            v = FRAME[t][f]
            p.append(rect(fx(f), Y0 + t * CHX, CWX, CHX, fill=fill,
                          stroke="#d5d5d5", sw=1.0, rx=3))
            p.append(text(fx(f) + CWX / 2, Y0 + t * CHX + CHX / 2 + 5, str(v),
                          size=12.5, color=(POS if v else NEG)))

    # рамки навколо підсвічених осей
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="none" '
             'stroke="%s" stroke-width="2.4"/>' % (fx(HOT_F), Y0, CWX, NT * CHX, POS))
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="none" '
             'stroke="%s" stroke-width="2.4"/>' % (X0, Y0 + HOT_T * CHX, NF * CWX, CHX, NEG))

    # підписи доріжок
    names = ["дані 0", "дані 1", "дані 2", "дані 3", "дані 4", "дані 5", "P"]
    for t in range(NT):
        hot = (t == HOT_T)
        p.append(text(X0 - 12, Y0 + t * CHX + CHX / 2 + 5, names[t], size=11.5,
                      color=(NEG if hot else MUTED), bold=hot, anchor="end"))
    p.append(text(X0 - 12, Y0 + 6 * CHX + CHX / 2 + 20, "парність", size=9.5,
                  color=FIELD, anchor="end"))

    # кадр LRCC після проміжку
    for t in range(NT):
        p.append(rect(LX, Y0 + t * CHX, CWX, CHX, fill=TINT_G, stroke=FIELD, sw=1.6, rx=3))
        p.append(text(LX + CWX / 2, Y0 + t * CHX + CHX / 2 + 5, str(LRCC[t]),
                      size=12.5, color=(POS if LRCC[t] else NEG), bold=True))
    p.append(text(LX + CWX / 2, Y0 - 12, "LRCC", size=12, color=FIELD, bold=True))

    # поперечна вісь: стрілка згори в підсвічений кадр
    cxv = fx(HOT_F) + CWX / 2
    p.append(mtext(cxv, 88, ["VRC — упоперек стрічки", "парність одного кадру"],
                   size=12, color=POS, bold=True))
    p.append(carrow(cxv, 116, cxv, Y0 - 6, color=POS, sw=2.2))

    # проміжок
    p.append(text((fx(NF) + GAPX) / 2, BOT + 18, "чотири порожні кадри", size=10.5,
                  color=MUTED, italic=True))

    # поздовжня вісь: стрілка під стрічкою вздовж запису
    ay = BOT + 44
    p.append(carrow(X0, ay, fx(NF) - 2, ay, color=NEG, sw=2.2))
    p.append(mtext((X0 + fx(NF)) / 2, ay + 26,
                   ["LRC — уздовж стрічки: парність однієї доріжки за весь запис",
                    "(тут — доріжки 3; сім таких бітів і складають кадр LRCC)"],
                   size=12, color=NEG, bold=False))

    p.append(text(W / 2, H - 26,
                  "«вертикально» і «поздовжньо» — це напрямки пальця по реальній речі, а не метафори",
                  size=12, color=INK, italic=True))
    render(os.path.join(OUT, "tape-axes.svg"), W, H, *p)


# ── 7. dead-track: чому поздовжньої ПАРНОСТІ не вистачило ─────────────────────
def fig_dead_track():
    """Пакет у доріжці парної ваги лишає біт LRCC чистим — парність бреше."""
    W, H = 880, 500
    NF, NT = 9, 7
    CWX, CHX = 24, 24
    Y0 = 152
    HOT_T = 3

    def panel(px, hits, head, verdict, ok):
        """hits — множина кадрів, побитих у доріжці HOT_T."""
        D = [bits(7 + t, NF) for t in range(6)]
        P = [1 ^ D[0][f] ^ D[1][f] ^ D[2][f] ^ D[3][f] ^ D[4][f] ^ D[5][f] for f in range(NF)]
        F = [row[:] for row in D] + [P[:]]
        for f in hits:                       # порошинка перевертає біт доріжки HOT_T
            F[HOT_T][f] ^= 1
        L = []
        for t in range(NT):
            v = 0
            for f in range(NF):
                v ^= F[t][f]
            L.append(v)

        out = []
        gx = px + 26                          # ліворуч — підписи доріжок
        lx = gx + NF * CWX + 14               # колонка LRCC
        bot = Y0 + NT * CHX

        out.append(text(gx + NF * CWX / 2, 100, head, size=13, color=INK, bold=True))
        for t in range(NT):
            for f in range(NF):
                bad = (t == HOT_T and f in hits)
                fill = HOT_R if bad else (TINT_L if t == HOT_T else BG)
                out.append(rect(gx + f * CWX, Y0 + t * CHX, CWX, CHX, fill=fill,
                                stroke=(POS if bad else "#d5d5d5"),
                                sw=(2.4 if bad else 1.0), rx=3))
                out.append(text(gx + f * CWX + CWX / 2, Y0 + t * CHX + CHX / 2 + 5,
                                str(F[t][f]), size=11.5,
                                color=(POS if F[t][f] else NEG), bold=bad))
            out.append(text(px + 18, Y0 + t * CHX + CHX / 2 + 5,
                            ("3" if t == HOT_T else ("P" if t == 6 else str(t))),
                            size=11, color=(NEG if t == HOT_T else MUTED),
                            bold=(t == HOT_T), anchor="end"))
        # LRCC
        out.append(text(lx + CWX / 2, Y0 - 12, "LRCC", size=11.5, color=FIELD, bold=True))
        for t in range(NT):
            mark = (t == HOT_T)
            out.append(rect(lx, Y0 + t * CHX, CWX, CHX, fill=TINT_G,
                            stroke=(POS if (mark and not ok) else FIELD),
                            sw=(2.4 if mark else 1.4), rx=3))
            out.append(text(lx + CWX / 2, Y0 + t * CHX + CHX / 2 + 5, str(L[t]),
                            size=11.5, color=(POS if L[t] else NEG), bold=mark))
        # вердикт біля біта LRCC мертвої доріжки
        out.append(text(lx + CWX + 10, Y0 + HOT_T * CHX + CHX / 2 + 5,
                        ("✗" if not ok else "✓"), size=16,
                        color=(POS if not ok else FIELD), bold=True, anchor="start"))
        # VRC кричать під побитими кадрами
        for f in hits:
            out.append(text(gx + f * CWX + CWX / 2, bot + 18, "✗", size=13, color=POS, bold=True))
        out.append(text(gx + NF * CWX / 2, bot + 40,
                        "VRC кричить у %d кадрах" % len(hits), size=11.5, color=POS))
        out.append(mtext(gx + NF * CWX / 2, bot + 66, verdict, size=12,
                         color=(FIELD if ok else POS), bold=True))
        return out

    p = [text(W / 2, 30, "Чому поздовжньої парності стрічці не вистачило", size=17, bold=True),
         text(W / 2, 52, "порошинка сидить в ОДНІЙ доріжці й тягнеться вздовж; біт LRCC цієї доріжки "
                         "червоніє лише при НЕПАРНІЙ кількості збоїв",
              size=12.5, color=MUTED, italic=True)]
    p += panel(70, {2, 4, 5},
               "порошинка вбила 3 кадри — непарно",
               ["біт LRCC доріжки 3 зіпсовано",
                "мертву доріжку названо → лагодимо"], ok=True)
    p += panel(500, {2, 4, 5, 6},
               "порошинка вбила 4 кадри — парно",
               ["біт LRCC доріжки 3 ЦІЛИЙ",
                "«помилка є, а винних немає»"], ok=False)

    p.append(line(462, 96, 462, 400, color="#dddddd", sw=1.4, dash="5 5"))
    p.append(text(W / 2, H - 46,
                  "пакет має рівно 50 % шансів на парну вагу — як шукач мертвої доріжки парність нікуди не годиться",
                  size=12.5, color=INK, bold=True))
    p.append(text(W / 2, H - 22,
                  "саме тому IBM поставила вздовж доріжки циклічний код (CRCC), лишивши парність кадру на ремонті",
                  size=12, color=FIELD, italic=True))
    render(os.path.join(OUT, "dead-track.svg"), W, H, *p)


# ── 8. names-flip: чому назви почали суперечити малюнку ───────────────────────
def fig_names_flip():
    """Той самий код у двох орієнтаціях — назви лишаються, картинка транспонується."""
    W, H = 820, 580
    Z = 26

    def grid(px, py, rows, cols, hot_r=None, hot_c=None):
        out = []
        for r in range(rows):
            for c in range(cols):
                fill = BG
                if r == hot_r and c == hot_c:
                    fill = TINT_X
                elif c == hot_c:
                    fill = TINT_V if hot_c is not None else BG
                elif r == hot_r:
                    fill = TINT_L
                out.append(rect(px + c * Z, py + r * Z, Z, Z, fill=fill,
                                stroke="#d5d5d5", sw=1.0, rx=3))
        return out

    p = [text(W / 2, 30, "Чому назви почали суперечити малюнку", size=17, bold=True),
         text(W / 2, 52, "код той самий — повернуто лише аркуш; назви лишилися від стрічки",
              size=12.5, color=MUTED, italic=True)]

    # ── ЛІВА ПАНЕЛЬ: орієнтація стрічки (доріжки — рядки, кадри — стовпці) ─────
    LPX, LPY, LR, LC = 100, 196, 6, 8
    p.append(text(LPX + LC * Z / 2, 84, "як лежить на стрічці", size=13.5, bold=True))
    p += grid(LPX, LPY, LR, LC, hot_r=2, hot_c=3)
    # VRC — вертикально, згори
    cxv = LPX + 3 * Z + Z / 2
    p.append(mtext(cxv, 122, ["VRC («vertical»)", "справді вертикально ✓"],
                   size=11.5, color=POS, bold=True))
    p.append(carrow(cxv, 152, cxv, LPY - 6, color=POS, sw=2.2))
    # LRC — горизонтально, знизу
    ay = LPY + LR * Z + 30
    p.append(carrow(LPX, ay, LPX + LC * Z - 2, ay, color=NEG, sw=2.2))
    p.append(mtext(LPX + LC * Z / 2, ay + 26, ["LRC («longitudinal»)", "справді вздовж ✓"],
                   size=11.5, color=NEG, bold=True))

    # ── ПРАВА ПАНЕЛЬ: орієнтація підручника (символи — рядки, біти — стовпці) ──
    RPX, RPY, RR, RC = 592, 196, 8, 6
    p.append(text(RPX + RC * Z / 2, 84, "як малює підручник", size=13.5, bold=True))
    p += grid(RPX, RPY, RR, RC, hot_r=3, hot_c=2)
    # LRC — тепер вертикально, згори
    cxl = RPX + 2 * Z + Z / 2
    p.append(mtext(cxl, 122, ["LRC («longitudinal»)", "а йде вертикально ✗"],
                   size=11.5, color=NEG, bold=True))
    p.append(carrow(cxl, 152, cxl, RPY - 6, color=NEG, sw=2.2))
    # VRC — тепер горизонтально, стрілка входить зліва
    ry = RPY + 3 * Z + Z / 2
    p.append(carrow(RPX - 84, ry, RPX - 6, ry, color=POS, sw=2.2))
    p.append(mtext(RPX - 92, ry - 8, ["VRC («vertical»)", "а йде горизонтально ✗"],
                   size=11.5, color=POS, bold=True, anchor="end"))

    # підписи осей панелей
    p.append(text(LPX + LC * Z / 2, LPY + LR * Z + 96, "рядок = доріжка · стовпець = кадр",
                  size=11, color=MUTED, italic=True))
    p.append(text(RPX + RC * Z / 2, RPY + RR * Z + 22, "рядок = символ · стовпець = номер біта",
                  size=11, color=MUTED, italic=True))

    p.append(text(W / 2, H - 62, "той самий код, та сама арифметика — і назви кажуть рівно навпаки",
                  size=13, color=INK, bold=True))
    p.append(mtext(W / 2, H - 36,
                   ["звідси дублери: VRC = TRC (transverse, «поперечна») · LRC = horizontal redundancy check",
                    "«поперечна» — це втеча від картинки: упоперек лишається впоперек, хоч як поверни аркуш"],
                   size=11.5, color=MUTED))
    render(os.path.join(OUT, "names-flip.svg"), W, H, *p)


def fig_packed():
    """Бітпакування: рядок = машинне слово; стовпцеві парності — XOR слів."""
    W, H = 1000, 560
    p = [text(W / 2, 32, "Бітпакування: рядок — це машинне слово", size=17, bold=True),
         text(W / 2, 56, "усі стовпцеві парності виходять одним XOR-ом на рядок, а кут — задарма",
              size=12, color=MUTED, italic=True)]

    SX, GAP, GX = 48, 18, 170          # крок, відступ перед RP, лівий край
    def cx_(c):
        return GX + c * SX + (GAP if c == 4 else 0)
    R_EDGE = cx_(4) + CW               # правий край сітки
    RY = [105, 163, 221, 279]          # рядки даних
    CPY = 360                          # рядок cp

    # блідо-зелена смуга під колонкою RP
    p.append(band(cx_(4) - 5, RY[0] - 6, CW + 10, (RY[3] + CW) - RY[0] + 12, FIELD, 0.10))

    for c, nm in enumerate(["c0", "c1", "c2", "c3", "RP"]):
        p.append(text(cx_(c) + CW / 2, 90, nm, size=13,
                      color=(FIELD if c == 4 else MUTED), bold=(c == 4)))

    for i, y in enumerate(RY):
        p.append(text(60, y + CW / 2 + 5, "w[%d]" % i, size=13, color=INK, anchor="start"))
        for c in range(4):
            p.append(cell(cx_(c), y, DATA[i][c]))
        p.append(cell(cx_(4), y, RP[i], fill=TINT_P, stroke=FIELD, sw=2.2))

    for y in [(RY[0] + CW + RY[1]) / 2, (RY[1] + CW + RY[2]) / 2, (RY[2] + CW + RY[3]) / 2]:
        p.append(text(145, y + 7, "⊕", size=20, color=NEG, bold=True))

    p.append(line(140, 340, R_EDGE + 10, 340, color=LINE, sw=2))
    p.append(text(60, CPY + CW / 2 + 5, "cp", size=13, color=INK, anchor="start", bold=True))
    for c in range(4):
        p.append(cell(cx_(c), CPY, CP[c], fill=TINT_P, stroke=FIELD, sw=2.2))
    p.append(cell(cx_(4), CPY, CORNER, fill=TINT_C, stroke="#e08a1e", sw=3.0))

    b1, _, _ = textbox(780, 126, "рядок даних = одне слово:\nмолодші біти — дані,\nбіт c — парність рядка",
                       size=13, pad=12)
    p.append(b1)
    p.append(arrow(650, 126, 430, 126))

    b2, _, _ = textbox(780, 242, "cp ^= w[r]\nодин XOR на рядок —\nусі стовпці рахуються разом",
                       size=13, pad=12)
    p.append(b2)
    p.append(arrow(650, 242, 430, 242))

    b3, _, _ = textbox(780, 381, "кут — це просто біт RP\nу слові cp: окремої гілки\nдля нього НЕМАЄ",
                       size=13, pad=12, fill="#fff5e6", stroke="#e08a1e")
    p.append(b3)
    p.append(arrow(650, 381, 430, 381))

    p.append(text(296, 428, "c0 намальовано ліворуч; у машинному слові це молодші біти",
                  size=11, color=MUTED, italic=True))
    p.append(text(W / 2, 476, "кодування всієї сітки: 4 фолди парності + 4 XOR-и слів",
                  size=13, color=INK, bold=True))
    p.append(text(W / 2, 504, "жодного циклу по бітах стовпця — стовпці їдуть паралельно, по 64 за такт",
                  size=12, color=MUTED))
    render(os.path.join(OUT, "packed.svg"), W, H, *p)


def fig_decision():
    """Карта рішень декодера: (поганих рядків, поганих стовпців) → вердикт."""
    W, H = 940, 660
    p = [text(W / 2, 32, "Карта рішень декодера", size=17, bold=True),
         text(W / 2, 56, "половина клітинок недосяжна — і це безкоштовний самоконтроль",
              size=12, color=MUTED, italic=True)]

    BX, BY = 200, 140          # лівий-верхній кут карти
    BW, BH = 100, 58           # клітинка
    SXX, SYY = 108, 68         # крок

    p.append(text((BX + BX + 5 * SXX + BW) / 2, 96, "поганих стовпців →", size=13, color=MUTED))
    p.append(mtext(105, 112, ["поганих", "рядків ↓"], size=12, color=MUTED))

    for c in range(6):
        p.append(text(BX + c * SXX + BW / 2, 124, str(c), size=13, color=MUTED, bold=True))
    for r in range(6):
        p.append(text(185, BY + r * SYY + BH / 2 + 5, str(r), size=13, color=MUTED,
                      bold=True, anchor="end"))

    for r in range(6):
        for c in range(6):
            x, y = BX + c * SXX, BY + r * SYY
            if (r + c) % 2 == 1:                      # суперечить тотожності синдромів
                p.append(rect(x, y, BW, BH, fill="#f2f3f5", stroke="#dcdfe3", sw=1.2, rx=5))
                p.append(text(x + BW / 2, y + BH / 2 + 4, "неможливо", size=11, color="#9aa1a9"))
            elif r == 0 and c == 0:
                p.append(rect(x, y, BW, BH, fill="#eafaf0", stroke=FIELD, sw=2.4, rx=5))
                p.append(text(x + BW / 2, y + BH / 2 + 5, "ЦІЛЕ", size=13, color=FIELD, bold=True))
            elif r == 1 and c == 1:
                p.append(rect(x, y, BW, BH, fill="#fff5e6", stroke="#e08a1e", sw=2.6, rx=5))
                p.append(mtext(x + BW / 2, y + BH / 2 - 3, ["ВИПРАВИТИ", "перетин"],
                               size=11, color="#a8620a", bold=True))
            else:
                p.append(rect(x, y, BW, BH, fill="#fdecea", stroke="#e6a49c", sw=1.6, rx=5))
                p.append(text(x + BW / 2, y + BH / 2 + 4, "виявлено", size=11, color=POS))

    p.append(text(W / 2, 584,
                  "кількість поганих рядків і поганих стовпців — завжди однакової парності,",
                  size=12, color=MUTED))
    p.append(text(W / 2, 608,
                  "тож 18 із 36 клітинок карти не трапляються ніколи: спрацював assert — шукай баг",
                  size=12, color=MUTED))
    render(os.path.join(OUT, "decision.svg"), W, H, *p)


if __name__ == "__main__":
    fig_grid()
    fig_locate()
    fig_rectangle()
    fig_tape_axes()
    fig_dead_track()
    fig_names_flip()
    fig_packed()
    fig_decision()
    print("OK: grid.svg, locate.svg, rectangle.svg,"
          " tape-axes.svg, dead-track.svg, names-flip.svg, packed.svg, decision.svg"
          "  (RP=%s CP=%s corner=%d)" % (RP, CP, CORNER))
