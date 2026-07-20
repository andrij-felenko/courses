# -*- coding: utf-8 -*-
"""Фігури до статті «Математичне доведення».
Запуск:  python figs.py   → пише SVG у ./img/
  стаття: tower, methods, sqrt2
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#eaf7ef"
REDFILL = "#fdecea"
BLUEFILL = "#eaf0fd"
ROW = "#f4f6f8"


# ── 1. Будова математики: фундамент аксіом → теореми ─────────────────────────
def fig_tower():
    W, H = 900, 452
    cx = W / 2
    f = [text(cx, 30, "Математика стоїть на явно названому фундаменті", size=18, bold=True),
         text(cx, 52, "аксіоми й означення — унизу без доведення; усе вище зводять доведеннями",
              size=12, color=MUTED, italic=True)]

    # ── верхня смуга: ТЕОРЕМИ (найвужча) ──
    tw, th = 380, 66
    ty = 92
    f.append(fitbox(cx - tw / 2, ty, tw, th, "ТЕОРЕМИ\nдоведені твердження — готові цеглини",
                    size=13.5, fill=GREENFILL, stroke=FIELD, sw=2.0, color=INK, bold=True))

    # ── середня смуга: ЛЕМИ ──
    mw, mh = 540, 62
    my = 206
    f.append(fitbox(cx - mw / 2, my, mw, mh, "ЛЕМИ · раніше доведене",
                    size=13.5, fill=ROW, stroke=LINE, sw=1.8, color=INK, bold=True))

    # ── нижня смуга: фундамент, дві клітини ──
    by, bh = 316, 82
    lc_x, rc_x, cw = cx - 360, cx + 40, 320
    f.append(fitbox(lc_x, by, cw, bh, "АКСІОМИ\nприймаємо без доведення\n(правила гри)",
                    size=13, fill=BLUEFILL, stroke=NEG, sw=1.8, color=INK, bold=True))
    f.append(fitbox(rc_x, by, cw, bh, "ОЗНАЧЕННЯ\nточний зміст слів\n(що таке «парне» тощо)",
                    size=13, fill=BLUEFILL, stroke=NEG, sw=1.8, color=INK, bold=True))
    f.append(text(cx, by + bh + 22, "фундамент — приймаємо без доведення",
                  size=12.5, color=NEG, bold=True))

    # ── стрілки «доведення» знизу вгору (у проміжках між смугами) ──
    # проміжок фундамент(316) ↔ леми(низ 268): стрілка вгору
    f.append(arrow(cx, by - 4, cx, my + mh + 4, color=MUTED, sw=2.2))
    f.append(text(cx + 66, (by + my + mh) / 2 + 4, "доведення", size=11.5, color=MUTED, italic=True, anchor="start"))
    # проміжок леми(206) ↔ теореми(низ 158): стрілка вгору
    f.append(arrow(cx, my - 4, cx, ty + th + 4, color=MUTED, sw=2.2))
    f.append(text(cx + 66, (my + ty + th) / 2 + 4, "доведення", size=11.5, color=MUTED, italic=True, anchor="start"))

    # ── права виноска: істина тече вгору ──
    ax = 852
    f.append(arrow(ax, by + bh - 6, ax, ty + 6, color=FIELD, sw=2.4))
    f.append(('<text x="%d" y="%d" font-size="12" fill="%s" font-style="italic" font-weight="700" '
              'text-anchor="middle" transform="rotate(-90 %d %d)">певність тече вгору</text>'
              % (ax - 14, (by + ty) / 2 + 30, FIELD, ax - 14, (by + ty) / 2 + 30)))

    render(os.path.join(IMG, "tower.svg"), W, H, *f)


# ── 2. П'ять форм доведення ──────────────────────────────────────────────────
def fig_methods():
    W, H = 1080, 452
    f = [text(W / 2, 30, "П'ять форм доведення — різні ключі до різних замків", size=18, bold=True),
         text(W / 2, 52, "три перші доводять «P ⟹ Q» по-різному; індукція — про всі n; контрприклад лише СПРОСТОВУЄ",
              size=12, color=MUTED, italic=True)]

    cw, ch = 330, 156
    xs = [30, 380, 730]
    ys = [78, 250]

    def cell(col, row, title, body, tcol, bg):
        x, y = xs[col], ys[row]
        g = [rect(x, y, cw, ch, fill=bg, stroke=tcol, sw=1.8, rx=10)]
        g.append(text(x + cw / 2, y + 30, title, size=14.5, bold=True, color=tcol))
        g.append(line(x + 20, y + 42, x + cw - 20, y + 42, color="#d7dbe0", sw=1.2))
        g.append(mtext(x + cw / 2, y + 72, body, size=13, color=INK, lh=1.32))
        return g

    f += cell(0, 0, "ПРЯМЕ",
              ["припусти P,", "чинними кроками", "дійди до Q"], INK, BG)
    f += cell(1, 0, "КОНТРАПОЗИЦІЯ",
              ["P ⟹ Q   рівносильне", "¬Q ⟹ ¬P", "— доводь зручніший бік"], NEG, BLUEFILL)
    f += cell(2, 0, "ВІД СУПРОТИВНОГО",
              ["припусти, що теза ХИБНА", "виведи безглуздя", "отже теза правдива"], POS, REDFILL)
    f += cell(0, 1, "ІНДУКЦІЯ",
              ["база P(1)  +", "крок P(k) ⟹ P(k+1)", "⟹ усі натуральні n"], FIELD, GREENFILL)
    f += cell(1, 1, "КОНТРПРИКЛАД",
              ["щоб СПРОСТУВАТИ", "«для всіх n» —", "досить ОДНОГО винятку"], POS, BG)

    # шоста клітина — виноска про несиметрію
    x, y = xs[2], ys[1]
    f.append(rect(x, y, cw, ch, fill="#f9fafb", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(x + cw / 2, y + 30, "ГОЛОВНА НЕСИМЕТРІЯ", size=13.5, bold=True, color=MUTED))
    f.append(line(x + 20, y + 42, x + cw - 20, y + 42, color="#d7dbe0", sw=1.2))
    f.append(mtext(x + cw / 2, y + 70, ["«для всіх» важко", "довести, але легко", "повалити — єдиний", "виняток убиває все"],
                   size=13, color=INK, lh=1.32))

    render(os.path.join(IMG, "methods.svg"), W, H, *f)


# ── 3. √2 нераціональне: доведення від супротивного ──────────────────────────
def fig_sqrt2():
    W, H = 760, 566
    cx = W / 2
    f = [text(cx, 30, "√2 не є дробом — доведення від супротивного", size=18, bold=True),
         text(cx, 52, "припущення чесно веде до прямої суперечності з самим собою",
              size=12, color=MUTED, italic=True)]

    bw, bh = 540, 46
    bx = cx - bw / 2
    gap = 30

    boxes = [
        ("Припустимо:  √2 = p/q,  дріб НЕСКОРОТНИЙ", BLUEFILL, NEG, True),
        ("2 = p²/q²   ⟹   p² = 2q²   ⟹   p² парне", ROW, LINE, False),
        ("p² парне  ⟹  p парне  ⟹  p = 2m", ROW, LINE, False),
        ("4m² = 2q²   ⟹   q² = 2m²   ⟹   q парне", ROW, LINE, False),
        ("отже p і q ОБИДВА парні → спільний дільник 2", ROW, "#d7dbe0", False),
    ]
    y = 80
    positions = []
    for txt, bg, col, bold in boxes:
        f.append(fitbox(bx, y, bw, bh, txt, size=14, fill=bg, stroke=col,
                        sw=(1.9 if bold else 1.4), color=INK, bold=bold))
        positions.append(y)
        y += bh + gap

    # стрілки вниз між боксами
    for i in range(len(boxes) - 1):
        ytop = positions[i] + bh
        f.append(arrow(cx, ytop + 4, cx, ytop + gap - 4, color=MUTED, sw=2.0))

    # стрілка до суперечності
    ytop = positions[-1] + bh
    f.append(arrow(cx, ytop + 6, cx, ytop + gap + 8, color=POS, sw=2.4))

    # червона рамка суперечності
    ry = y + 10
    rh = 70
    f.append(rect(bx - 10, ry, bw + 20, rh, fill=REDFILL, stroke=POS, sw=2.0, rx=10))
    f.append(text(cx, ry + 26, "СУПЕРЕЧНІСТЬ: дріб і нескоротний, і скоротний",
                  size=13.5, bold=True, color=POS))
    f.append(text(cx, ry + 50, "⟹ припущення хибне  ⟹  √2 нераціональне",
                  size=13, color=INK, italic=True))

    render(os.path.join(IMG, "sqrt2.svg"), W, H, *f)


# ═══ Вставка «math-proof-methods»: логічний апарат доведень ══════════════════

def _ttable(x0, y0, cols, fills, rows, rowh=46, headh=48, mark=None):
    """Таблиця істинності. cols=[(підпис, ширина)]; fills=[колір стовпця];
    rows=[[значення…]]; mark=set (r, c) — клітини з червоною рамкою-наголосом.
    Повертає (фрагменти, xs, y_низу)."""
    g = []
    xs = [x0]
    for _, w in cols:
        xs.append(xs[-1] + w)
    for i, (label, w) in enumerate(cols):
        g.append(rect(xs[i], y0, w, headh, fill=fills[i], stroke=LINE, sw=1.4, rx=0))
        g.append(text(xs[i] + w / 2, y0 + headh / 2 + 6, label, size=15, bold=True))
    for r, row in enumerate(rows):
        yy = y0 + headh + r * rowh
        for i, (label, w) in enumerate(cols):
            base = fills[i]
            cf = base if base != BG else (ROW if r % 2 else BG)
            g.append(rect(xs[i], yy, w, rowh, fill=cf, stroke=LINE, sw=1.0, rx=0))
            g.append(text(xs[i] + w / 2, yy + rowh / 2 + 6, row[i], size=16, bold=True))
            if mark and (r, i) in mark:
                g.append(rect(xs[i] + 3, yy + 3, w - 6, rowh - 6, fill="none",
                              stroke=POS, sw=2.4, rx=4))
    return g, xs, y0 + headh + len(rows) * rowh


# ── 4. Контрапозиція: тотожні стовпці, конверсія — інша ───────────────────────
def fig_contrapos():
    W, H = 780, 404
    cols = [("P", 78), ("Q", 78), ("P ⟹ Q", 150), ("¬Q ⟹ ¬P", 178), ("Q ⟹ P", 152)]
    fills = [BG, BG, GREENFILL, GREENFILL, REDFILL]
    rows = [["T", "T", "T", "T", "T"],
            ["T", "F", "F", "F", "T"],
            ["F", "T", "T", "T", "F"],
            ["F", "F", "T", "T", "T"]]
    total = sum(w for _, w in cols)
    x0 = (W - total) / 2
    f = [text(W / 2, 30, "Рівносильність = тотожні стовпці, рядок у рядок", size=18, bold=True),
         text(W / 2, 54, "P ⟹ Q і контрапозиція ¬Q ⟹ ¬P дають ту саму колонку; конверсія Q ⟹ P — вже НІ",
              size=12, color=MUTED, italic=True)]
    g, xs, yb = _ttable(x0, 86, cols, fills, rows, mark={(1, 4), (2, 4)})
    f += g
    f.append(text((xs[2] + xs[4]) / 2, yb + 26,
                  "однакові в кожному рядку → рівносильні", size=12.5, color=FIELD, bold=True))
    f.append(text((xs[4] + xs[5]) / 2, yb + 26,
                  "конверсія: інша!", size=12.5, color=POS, bold=True))
    render(os.path.join(IMG, "contrapos.svg"), W, H, *f)


# ── 5. Чому reductio законне: (¬S ⟹ ⊥) ≡ S ───────────────────────────────────
def fig_reductio():
    W, H = 920, 408
    f = [text(W / 2, 30, "Чому «від супротивного» законне", size=18, bold=True),
         text(W / 2, 54, "довести S = довести, що ¬S тягне безглуздя: стовпці S і (¬S ⟹ ⊥) тотожні",
              size=12, color=MUTED, italic=True)]
    cols = [("S", 84), ("¬S", 84), ("R ∧ ¬R", 132), ("¬S ⟹ (R∧¬R)", 200)]
    fills = [GREENFILL, BG, REDFILL, GREENFILL]
    rows = [["T", "F", "F", "T"], ["F", "T", "F", "F"]]
    g, xs, yb = _ttable(60, 96, cols, fills, rows, rowh=48, headh=50)
    f += g
    f.append(mtext((xs[0] + xs[-1]) / 2, yb + 26,
                   ["стовпці S та (¬S ⟹ безглуздя) — тотожні:", "довести праве = довести S"],
                   size=12.5, color=FIELD, bold=True, lh=1.35))
    px, pw = 640, 250
    steps = [("1 · Виключене третє", "S або ¬S — третього нема", BLUEFILL, NEG),
             ("2 · Припущення", "беремо ¬S (теза хибна)", ROW, LINE),
             ("3 · Безглуздя", "¬S ⟹ R ∧ ¬R (завжди хиба)", REDFILL, POS),
             ("4 · Висновок", "¬S хибне ⟹ лишається S", GREENFILL, FIELD)]
    py, bh, gap = 92, 56, 18
    for i, (t, b, bg, col) in enumerate(steps):
        yy = py + i * (bh + gap)
        f.append(rect(px, yy, pw, bh, fill=bg, stroke=col, sw=1.7, rx=8))
        f.append(text(px + pw / 2, yy + 23, t, size=13, bold=True, color=col))
        f.append(text(px + pw / 2, yy + 43, b, size=11.5))
        if i < len(steps) - 1:
            f.append(arrow(px + pw / 2, yy + bh + 2, px + pw / 2, yy + bh + gap - 2, color=MUTED, sw=2.0))
    render(os.path.join(IMG, "reductio.svg"), W, H, *f)


# ── 6. Заперечення кванторів: Де Морган для ∀ / ∃ ─────────────────────────────
def fig_qneg():
    W, H = 960, 428
    f = [text(W / 2, 30, "Заперечення кванторів — Де Морган для «для всіх» і «існує»", size=18, bold=True),
         text(W / 2, 54, "¬ міняє ∀ на ∃ (і навпаки) та заганяє «не» всередину", size=12, color=MUTED, italic=True)]
    cx = W / 2

    def ident(y, left, right):
        f.append(fitbox(cx - 300, y, 250, 52, left, size=18, fill=BLUEFILL, stroke=NEG, sw=1.8, color=INK, bold=True))
        f.append(text(cx, y + 35, "⟺", size=26, bold=True, color=FIELD))
        f.append(fitbox(cx + 50, y, 250, 52, right, size=18, fill=GREENFILL, stroke=FIELD, sw=1.8, color=INK, bold=True))

    ident(80, "¬ ∀x P(x)", "∃x ¬P(x)")
    ident(146, "¬ ∃x P(x)", "∀x ¬P(x)")

    f.append(text(cx, 232, "чому — розгорнімо квантор у скінченну низку:", size=13, color=MUTED, italic=True))
    f.append(fitbox(120, 250, 720, 44, "∀x P(x)   ≡   P₁ ∧ P₂ ∧ P₃ ∧ … ∧ Pₙ        (∀ — довгий AND)",
                    size=15, fill=ROW, stroke=LINE, sw=1.4, color=INK))
    f.append(arrow(cx, 296, cx, 316, color=POS, sw=2.4))
    f.append(text(cx + 96, 310, "¬  (Де Морган: AND ↔ OR)", size=12, color=POS, italic=True, anchor="start"))
    f.append(fitbox(120, 318, 720, 44, "¬P₁ ∨ ¬P₂ ∨ ¬P₃ ∨ … ∨ ¬Pₙ   ≡   ∃x ¬P(x)   (OR «не» — тобто виняток)",
                    size=15, fill=GREENFILL, stroke=FIELD, sw=1.4, color=INK))
    f.append(fitbox(120, 376, 720, 40, "¬(усі прості непарні)   =   ∃ просте, що НЕ непарне   =   2  ✓",
                    size=14, fill=REDFILL, stroke=POS, sw=1.6, color=INK, bold=True))
    render(os.path.join(IMG, "qneg.svg"), W, H, *f)


# ═══ Вставка «proj-proof-checker»: перевіряч чинності міркувань ══════════════

# ── 7. Дерево розбору формули: пріоритет операцій ─────────────────────────────
def fig_ast():
    W, H = 720, 500
    f = [text(W / 2, 30, "Формула — це дерево: пріоритет вирішує, хто кого накриває", size=17, bold=True),
         text(W / 2, 52, "¬ в'яже найтісніше, далі ∧, потім ∨, найслабший ⟹ — тому він сидить у корені",
              size=12, color=MUTED, italic=True)]

    # вузли: id -> (x, y, підпис, тип)   тип: "op" — операція, "var" — змінна
    nodes = {
        "imp": (430, 100, "⟹", "op"),
        "or":  (300, 180, "∨", "op"),
        "s":   (560, 180, "s", "var"),
        "and": (205, 260, "∧", "op"),
        "r":   (405, 260, "r", "var"),
        "not": (135, 340, "¬", "op"),
        "q":   (295, 340, "q", "var"),
        "p":   (135, 420, "p", "var"),
    }
    edges = [("imp", "or"), ("imp", "s"), ("or", "and"), ("or", "r"),
             ("and", "not"), ("and", "q"), ("not", "p")]

    for a, b in edges:              # спершу ребра, щоб кружки лягли зверху
        f.append(line(nodes[a][0], nodes[a][1], nodes[b][0], nodes[b][1], color=MUTED, sw=1.8))

    r = 25
    for x, y, lab, kind in nodes.values():
        if kind == "op":
            f.append(circle(x, y, r, fill=BLUEFILL, stroke=NEG, sw=2.0))
            f.append(text(x, y + 7, lab, size=19, color=NEG, bold=True))
        else:
            f.append(circle(x, y, r, fill=GREENFILL, stroke=FIELD, sw=2.0))
            f.append(text(x, y + 7, lab, size=18, color=INK, bold=True))

    f.append(fitbox(150, 452, 420, 34, "¬p ∧ q ∨ r ⟹ s   =   ((¬p ∧ q) ∨ r) ⟹ s",
                    size=14, fill=ROW, stroke=LINE, sw=1.4, color=INK, bold=True))
    render(os.path.join(IMG, "ast.svg"), W, H, *f)


# ── 8. Таблиця істинності: пошук «поганого рядка» ────────────────────────────
def fig_truthtable():
    W, H = 700, 384
    f = [text(W / 2, 28, "Чинність — це пошук «поганого рядка»", size=17, bold=True),
         text(W / 2, 50, "де ВСІ посилки істинні (І), а висновок хибний (Х): є такий рядок — аргумент падає",
              size=12, color=MUTED, italic=True)]
    colw = [44, 44, 72, 56, 56]

    def panel(ox, oy, title, headers, rows, verdict, vfill, vstroke):
        xe = [ox]
        for w in colw:
            xe.append(xe[-1] + w)
        tw = xe[-1] - ox
        f.append(text(ox + tw / 2, oy, title, size=14, bold=True))
        gy = oy + 22
        f.append(text((xe[0] + xe[2]) / 2, gy, "світ (p, q)", size=10.5, color=MUTED, italic=True))
        f.append(text((xe[2] + xe[4]) / 2, gy, "посилки", size=10.5, color=NEG, italic=True))
        f.append(text((xe[4] + xe[5]) / 2, gy, "висновок", size=10.5, color=FIELD, italic=True))
        hy, rh = oy + 30, 31
        for i, h in enumerate(headers):
            f.append(rect(xe[i], hy, colw[i], rh, fill="#eef1f4", stroke=LINE, sw=1.1, rx=0))
            f.append(text((xe[i] + xe[i + 1]) / 2, hy + rh / 2 + 5, h, size=13, bold=True))
        for ri, (vals, kind) in enumerate(rows):
            ry = hy + rh * (ri + 1)
            fill = {"bad": REDFILL, "ok": GREENFILL, "skip": BG}[kind]
            for i, v in enumerate(vals):
                f.append(rect(xe[i], ry, colw[i], rh, fill=fill, stroke="#c9ced4", sw=1.0, rx=0))
                f.append(text((xe[i] + xe[i + 1]) / 2, ry + rh / 2 + 5, v,
                              size=13, color=INK, bold=(kind == "bad")))
            if kind != "skip":
                oc = POS if kind == "bad" else FIELD
                f.append(rect(xe[0], ry, tw, rh, fill="none", stroke=oc,
                              sw=(2.2 if kind == "bad" else 1.6), rx=0))
        vy = hy + rh * (len(rows) + 1) + 12
        f.append(fitbox(ox, vy, tw, 34, verdict, size=12, fill=vfill, stroke=vstroke, sw=1.8,
                        color=INK, bold=True))

    mp_rows = [(["Х", "Х", "І", "Х", "Х"], "skip"),
               (["Х", "І", "І", "Х", "І"], "skip"),
               (["І", "Х", "Х", "І", "Х"], "skip"),
               (["І", "І", "І", "І", "І"], "ok")]
    panel(40, 84, "p ⟹ q,  p   ⊢   q", ["p", "q", "p⟹q", "p", "q"], mp_rows,
          "ЧИННИЙ — поганого рядка нема", GREENFILL, FIELD)

    ac_rows = [(["Х", "Х", "І", "Х", "Х"], "skip"),
               (["Х", "І", "І", "І", "Х"], "bad"),
               (["І", "Х", "Х", "Х", "І"], "skip"),
               (["І", "І", "І", "І", "І"], "ok")]
    panel(388, 84, "p ⟹ q,  q   ⊢   p", ["p", "q", "p⟹q", "q", "p"], ac_rows,
          "НЕЧИННИЙ — контрприклад p=Х, q=І", REDFILL, POS)

    render(os.path.join(IMG, "truthtable.svg"), W, H, *f)


# ═══ Вставка «hist-birth-of-proof»: часова вісь народження доведення ═════════

# ── 9. Часова вісь: від Фалеса до Геделя ──────────────────────────────────────
def fig_timeline():
    W, H = 940, 690
    ax = 300                      # вертикальна вісь часу
    top, bot = 92, 648
    f = [text(W / 2, 32, "Народження доведення — двадцять п'ять століть", size=18, bold=True),
         text(W / 2, 54, "синє — кроки, що будували метод; червоне — кризи й межі строгості",
              size=12, color=MUTED, italic=True)]

    f.append(line(ax, top, ax, bot, color="#c4c9d0", sw=2.4))

    # (епоха, назва, опис, колір, заливка кружка)
    rows = [
        ("бл. 600 до н. е.", "Фалес", "перші дедуктивні докази (за традицією)", NEG, BLUEFILL),
        ("V ст. до н. е.",   "Піфагорійці", "криза несумірності: √2 — не дріб", POS, REDFILL),
        ("бл. 300 до н. е.", "Евклід · «Начала»", "аксіоматичний зразок: 5+5 засад → 465 тверджень", NEG, BLUEFILL),
        ("XVII–XIX ст.",     "Криза строгості", "нескінченно малі → ε–δ означення границі", POS, REDFILL),
        ("1900–1920-ті",     "Програма Гільберта", "формалізувати всю математику: несуперечлива + повна", NEG, BLUEFILL),
        ("1931",             "Теореми Геделя", "неповнота: «доведене» вужче за «правдиве»", POS, REDFILL),
    ]
    n = len(rows)
    y0 = 132
    dy = (bot - y0 - 30) / (n - 1)
    for i, (era, name, desc, col, fill) in enumerate(rows):
        y = y0 + i * dy
        f.append(text(ax - 22, y - 4, era, size=12.5, color=MUTED, anchor="end", bold=True))
        f.append(circle(ax, y, 9, fill=fill, stroke=col, sw=2.4))
        f.append(text(ax + 24, y - 4, name, size=14.5, color=col, anchor="start", bold=True))
        f.append(text(ax + 24, y + 15, desc, size=12.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "timeline-proof.svg"), W, H, *f)


if __name__ == "__main__":
    fig_tower()
    fig_methods()
    fig_sqrt2()
    fig_contrapos()
    fig_reductio()
    fig_qneg()
    fig_ast()
    fig_truthtable()
    fig_timeline()
    print("OK: 9 figures ->", IMG)
