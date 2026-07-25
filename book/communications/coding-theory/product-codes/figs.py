# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Наскрізний приклад: блок даних 4×4 + парність рядків (RP) і стовпців (CP) ──
DATA = [
    [1, 0, 1, 1],
    [0, 1, 1, 0],
    [1, 1, 0, 1],
    [0, 0, 1, 1],
]
RP = [r[0] ^ r[1] ^ r[2] ^ r[3] for r in DATA]           # парність кожного рядка
CP = [DATA[0][c] ^ DATA[1][c] ^ DATA[2][c] ^ DATA[3][c] for c in range(4)]
CORNER = RP[0] ^ RP[1] ^ RP[2] ^ RP[3]                   # парність парностей

# ── Геометрія сітки ───────────────────────────────────────────────────────────
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


# ── 1. product-distance: чому відстань перемножується ─────────────────────────
def fig_product_distance():
    """Двобічний доказ d = d₁·d₂: знизу — оцінка, зверху — досяжність."""
    W, H = 940, 560
    p = [text(W / 2, 30, "Чому відстань добутку дорівнює добутку відстаней", size=17, bold=True),
         text(W / 2, 52, "ліворуч — жодне слово не легше за d₁·d₂;  праворуч — рівно d₁·d₂ досяжно",
              size=12.5, color=MUTED, italic=True)]

    S = 30              # крок дрібної клітинки
    Z = 26              # розмір дрібної клітинки
    ROWS, COLS = 6, 6

    def mini(px, py, ones, tint_rows=(), tint_cols=(), stroke_ones=POS):
        """Дрібна сітка ROWS×COLS; ones — множина (r,c) з одиницями."""
        out = []
        for r in range(ROWS):
            for c in range(COLS):
                x, y = px + c * S, py + r * S
                f = BG
                if c in tint_cols: f = TINT_R
                if r in tint_rows: f = TINT_P
                if (r, c) in ones:
                    out.append(rect(x, y, Z, Z, fill="#f7c8c1", stroke=stroke_ones, sw=2.4, rx=4))
                    out.append(text(x + Z / 2, y + Z / 2 + 5, "1", size=13, color=POS, bold=True))
                else:
                    out.append(rect(x, y, Z, Z, fill=f, stroke="#d8d8d8", sw=1.0, rx=4))
        return out

    # ── ЛІВА ПАНЕЛЬ: нижня межа ──────────────────────────────────────────────
    LX, LY = 96, 132
    p.append(text(LX + COLS * S / 2 - 4, LY - 62, "нижня межа", size=14.5, color=INK, bold=True))
    p.append(text(LX + COLS * S / 2 - 4, LY - 42,
                  "візьмімо БУДЬ-ЯКЕ ненульове слово", size=12, color=MUTED))
    # ненульовий рядок r1 має ≥ d₂ = 3 одиниць → стовпці 1,3,4 ненульові;
    # кожен такий стовпець — слово C₁, отже теж ≥ d₁ = 3 одиниць
    ones_L = {(1, 1), (1, 3), (1, 4),
              (3, 1), (5, 1),
              (2, 3), (4, 3),
              (3, 4), (5, 4)}
    for f in mini(LX, LY, ones_L, tint_rows={1}, tint_cols={1, 3, 4}):
        p.append(f)
    LR, LB = LX + COLS * S, LY + ROWS * S
    # анотація рядка
    p.append(text(LX - 12, LY + 1 * S + Z / 2 + 5, "рядок", size=12, color=FIELD, bold=True, anchor="end"))
    p.append(text(LX - 12, LY + 1 * S + Z / 2 + 21, "≠ 0", size=12, color=FIELD, anchor="end"))
    p.append(mtext(LR + 14, LY + 1 * S + Z / 2 - 4,
                   ["— це слово коду C₂,", "отже в ньому ≥ d₂ одиниць"],
                   size=11.5, color=FIELD, anchor="start"))
    # анотація стовпців
    p.append(mtext(LX + COLS * S / 2 - 4, LB + 30,
                   ["значить ≥ d₂ стовпців ненульові,",
                    "а кожен із них — слово коду C₁,",
                    "отже в кожному ≥ d₁ одиниць"],
                   size=12, color=INK))
    p.append(text(LX + COLS * S / 2 - 4, LB + 104,
                  "вага ≥ d₂ · d₁", size=15, color=POS, bold=True))

    # ── ПРАВА ПАНЕЛЬ: досяжність через зовнішній добуток ──────────────────────
    RX, RY = 560, 132
    p.append(text(RX + COLS * S / 2 - 4, RY - 62, "досяжність", size=14.5, color=INK, bold=True))
    p.append(text(RX + COLS * S / 2 - 4, RY - 42, "складімо слово НАВМИСНЕ", size=12, color=MUTED))
    c1_rows = [1, 3, 5]       # c₁ — слово C₁ ваги d₁ = 3 (вертикальне)
    c2_cols = [1, 3, 4]       # c₂ — слово C₂ ваги d₂ = 3 (горизонтальне)
    ones_R = {(r, c) for r in c1_rows for c in c2_cols}
    for f in mini(RX, RY, ones_R, stroke_ones=FIELD):
        p.append(f)
    RR, RB = RX + COLS * S, RY + ROWS * S
    # вектор c₂ над сіткою
    for c in range(COLS):
        v = 1 if c in c2_cols else 0
        p.append(rect(RX + c * S, RY - 34, Z, Z, fill=("#eafaf0" if v else BG),
                      stroke=FIELD if v else "#d8d8d8", sw=1.8 if v else 1.0, rx=4))
        p.append(text(RX + c * S + Z / 2, RY - 34 + Z / 2 + 5, str(v), size=12,
                      color=(FIELD if v else MUTED), bold=bool(v)))
    p.append(text(RR + 14, RY - 34 + Z / 2 + 5, "c₂  (вага d₂)", size=12, color=FIELD,
                  anchor="start", bold=True))
    # вектор c₁ ліворуч від сітки
    for r in range(ROWS):
        v = 1 if r in c1_rows else 0
        p.append(rect(RX - 40, RY + r * S, Z, Z, fill=("#eafaf0" if v else BG),
                      stroke=FIELD if v else "#d8d8d8", sw=1.8 if v else 1.0, rx=4))
        p.append(text(RX - 40 + Z / 2, RY + r * S + Z / 2 + 5, str(v), size=12,
                      color=(FIELD if v else MUTED), bold=bool(v)))
    p.append(text(RX - 54, RY + ROWS * S / 2 - 8, "c₁", size=12, color=FIELD, bold=True, anchor="end"))
    p.append(text(RX - 54, RY + ROWS * S / 2 + 10, "(вага d₁)", size=10.5, color=FIELD, anchor="end"))
    p.append(mtext(RX + COLS * S / 2 - 4, RB + 30,
                   ["одиниця стоїть там, де c₁ і c₂ разом дають 1:",
                    "кожен рядок — або 0, або c₂;  кожен стовпець —",
                    "або 0, або c₁. Це слово коду, і в ньому"],
                   size=12, color=INK))
    p.append(text(RX + COLS * S / 2 - 4, RB + 104,
                  "рівно d₁ · d₂ одиниць", size=15, color=FIELD, bold=True))

    # ── ВИСНОВОК унизу ───────────────────────────────────────────────────────
    by = H - 46
    p.append(line(60, by - 34, W - 60, by - 34, color="#dddddd", sw=1.2))
    p.append(text(W / 2, by - 8, "d = d₁ · d₂", size=16, color=INK, bold=True))
    p.append(text(W / 2, by + 14,
                  "для двовимірної парності обидва співмножники — проста парність: d₁ = d₂ = 2,  отже d = 2 · 2 = 4,"
                  "  а слово мінімальної ваги — прямокутник 2×2",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "product-distance.svg"), W, H, *p)


# ── 2. miscorrect: три помилки → декодер добудовує прямокутник ────────────────
def fig_miscorrect():
    W, H = 640, 560
    p = [text(W / 2, 30, "Три помилки: декодер мовчки псує блок", size=17, bold=True),
         text(W / 2, 52, "три кути прямокутника дають той самий синдром, що й ОДНА помилка в четвертому",
              size=12.5, color=MUTED, italic=True)]

    ERRS = {(0, 0), (0, 1), (1, 0)}      # три справжні помилки
    INNOCENT = (1, 1)                     # непричетна клітинка, яку переверне декодер
    disp = [row[:] for row in DATA]
    for (r, c) in ERRS:
        disp[r][c] ^= 1

    headers(p, bad_cols={1}, bad_rows={1})
    dividers(p)

    # сітка вручну: три помилки — червоні, непричетна — бурштинова пунктирна
    for r in range(4):
        for c in range(4):
            if (r, c) in ERRS:
                p.append(cell(col_x(c), row_y(r), disp[r][c], fill=HOT_R, stroke=POS, sw=3.2))
            elif (r, c) == INNOCENT:
                p.append(rect(col_x(c), row_y(r), CW, CW, fill=TINT_C, stroke="#e08a1e", sw=3.0, rx=5))
                p.append(text(col_x(c) + CW / 2, row_y(r) + CW / 2 + 6, str(disp[r][c]),
                              size=17, color=POS, bold=True))
            else:
                p.append(cell(col_x(c), row_y(r), disp[r][c]))
    for r in range(4):
        p.append(cell(PX, row_y(r), RP[r], fill=TINT_P, stroke=FIELD, sw=2.2))
    for c in range(4):
        p.append(cell(col_x(c), PY, CP[c], fill=TINT_P, stroke=FIELD, sw=2.2))
    p.append(cell(PX, PY, CORNER, fill=TINT_C, stroke=FIELD, sw=2.2))

    # синдроми: винен рівно один рядок (r1) і рівно один стовпець (c1)
    for r in range(4):
        bad = (r == 1)
        p.append(text(RIGHT + 16, row_y(r) + CW / 2 + 5, "✗" if bad else "✓",
                      size=16 if bad else 15, color=POS if bad else FIELD, bold=True))
    for c in range(4):
        bad = (c == 1)
        p.append(text(col_x(c) + CW / 2, BOTTOM + 20, "✗" if bad else "✓",
                      size=16 if bad else 15, color=POS if bad else FIELD, bold=True))

    # пунктирний прямокутник по рядках 0–1, стовпцях 0–1
    rx0, ry0 = col_x(0), row_y(0)
    rw = (col_x(1) + CW) - rx0
    rh = (row_y(1) + CW) - ry0
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="none" '
             'stroke="#e08a1e" stroke-width="2.2" stroke-dasharray="6 4"/>' % (rx0, ry0, rw, rh))

    # легенда над сіткою — з великим запасом, повз написи
    p.append(rect(col_x(0) - 2, Y0 - 44, CW * 2 + 6, 18, fill="#fdf1dd", stroke="none", sw=0))
    p.append(text(col_x(0) + CW, Y0 - 31, "три помилки + непричетний", size=10.5, color="#8a5a10"))

    cy = BOTTOM + 52
    p.append(text(W / 2, cy, "синдром: винен рівно ОДИН рядок (r1) і рівно ОДИН стовпець (c1)",
                  size=13, color=INK, bold=True))
    p.append(text(W / 2, cy + 24, "правило «один рядок ∩ один стовпець» спрацьовує → декодер перевертає (r1, c1)",
                  size=12.5, color="#8a5a10"))
    p.append(text(W / 2, cy + 48, "але (r1, c1) був ЦІЛИЙ — тепер зіпсовано всі чотири кути,",
                  size=12.5, color=POS, bold=True))
    p.append(text(W / 2, cy + 70, "а це вже дозволене слово коду: усі перевірки проходять, тривоги немає",
                  size=12.5, color=POS, bold=True))
    render(os.path.join(OUT, "miscorrect.svg"), W, H, *p)


if __name__ == "__main__":
    fig_product_distance()
    fig_miscorrect()
    print("OK: product-distance.svg, miscorrect.svg  (RP=%s CP=%s corner=%d)" % (RP, CP, CORNER))
