# -*- coding: utf-8 -*-
"""Фігури до теми «Двійковий логарифм».
Імпортує спільний svgkit зі scripts/ (НЕ копіювати функції).
Три фігури теми:
  1) ladder.svg   — місткість 2ᴺ і log₂: драбина у два боки (біти ↔ значення).
  2) msb.svg      — ⌊log₂n⌋ = позиція старшого одиничного біта (на прикладі 100).
  3) halving.svg  — log₂n = скільки разів поділити навпіл до 1 (64→1 за 6 кроків).
Дві фігури вставки math-change-of-base.md:
  4) rulers.svg   — одна множинна вісь, три лінійки (біти / розряди / нати).
  5) drift.svg    — 2¹⁰ᵏ проти 10³ᵏ: наближення 10/3 до log₂10 розповзається.
Три фігури вставки hist-binary-logarithm.md:
  6) hist-timeline.svg — форма історії: ланцюг (log₁₀) проти окремих точок (log₂).
  7) hist-law.svg      — Ac і log₂ проходять той самий закон f(m·n)=f(m)+f(n).
  8) hist-euler.svg    — таблиця «Tentamen» (1739, §VII): октави дають цілі.
Три фігури вставки proj-ilog2.md:
  9) proj-wheel.svg — B(2,3) = 00010111: усі вісім вікон по три біти різні.
 10) proj-slide.svg — множення 2ᵏ·C прокручує вікно; таблиця — обернена перестановка.
 11) proj-smear.svg — каскад n |= n >> s: смуга одиниць подвоюється щокроку.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

_SUP = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}


def sup(n):
    """Число → рядок з надрядкових цифр Unicode: 10 → '¹⁰'."""
    return ''.join(_SUP[c] for c in str(n))

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — драбина 2ᴺ ↔ log₂
# Ліворуч біти N, праворуч значення 2ᴺ; верхня стрілка (вправо) — піднесення
# до степеня, нижня (вліво) — двійковий логарифм. Округлення вгору в підписі.
# ════════════════════════════════════════════════════════════════════════════
def fig_ladder():
    W, H = 720, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    lx, rx = 205, 515          # центри колонок
    lw, rw = 120, 150          # ширини клітин

    # верхня стрілка: біти → значення (вправо)
    f.append(text(W / 2, 60, 'піднесення до степеня  2ᴺ    (N бітів → 2ᴺ значень)',
                  13, POS, 'middle', bold=True))
    f.append(arrow(lx - 40, 78, rx + 55, 78, color=POS, sw=2))

    # заголовки колонок
    f.append(text(lx, 110, 'біти  N', 14, INK, 'middle', bold=True))
    f.append(text(rx, 110, 'значень  2ᴺ', 14, INK, 'middle', bold=True))

    biti = ['1', '2', '3', '8', '10']
    vals = ['2', '4', '8', '256', '1024']
    y0, dy, bh = 130, 44, 34
    for i in range(5):
        cy = y0 + i * dy
        # тонкий з'єднувач між парою
        f.append(line(lx + lw / 2, cy + bh / 2, rx - rw / 2, cy + bh / 2,
                      color=MUTED, sw=1, dash='4,4'))
        f.append(fitbox(lx - lw / 2, cy, lw, bh, biti[i], size=15,
                        fill=FILL, stroke=LINE, bold=True))
        f.append(fitbox(rx - rw / 2, cy, rw, bh, vals[i], size=15,
                        fill='#eef6ee', stroke=FIELD, bold=True))

    # нижня стрілка: значення → біти (вліво)
    ay = y0 + 5 * dy + 8
    f.append(arrow(rx + 55, ay, lx - 40, ay, color=NEG, sw=2))
    f.append(text(W / 2, ay + 22, 'двійковий логарифм  log₂    (M значень → log₂M бітів)',
                  13, NEG, 'middle', bold=True))

    # підпис-висновок
    box, bw, bh2 = textbox(W / 2, ay + 70,
                           'M рідко є точним степенем двійки — тоді бітів беруть на один\n'
                           'більше: рівно ⌈log₂M⌉ (округлення вгору).',
                           size=12.5, pad=11, fill=FILL, stroke=LINE)
    f.append(box)

    render(os.path.join(IMG, 'ladder.svg'), W, H, *f,
           title='Місткість 2ᴺ і двійковий логарифм — драбина у два боки')


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — ⌊log₂n⌋ = позиція старшого біта (n = 100)
# 100 = 1100100₂; старший одиничний біт на позиції 6 → ⌊log₂100⌋ = 6.
# ════════════════════════════════════════════════════════════════════════════
def fig_msb():
    W, H = 680, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    bits = ['0', '1', '1', '0', '0', '1', '0', '0']   # позиції 7..0 числа 100
    pos = ['7', '6', '5', '4', '3', '2', '1', '0']
    cw, ch = 60, 54
    x0 = (W - 8 * cw) / 2
    ytop = 98
    for i in range(8):
        x = x0 + i * cw
        cx = x + cw / 2
        hi = (i == 1)                       # позиція 6 — старший одиничний біт
        f.append(rect(x, ytop, cw, ch,
                      fill='#fdecea' if hi else FILL,
                      stroke=POS if hi else LINE, sw=2 if hi else 1.4, rx=6))
        f.append(text(cx, ytop + ch / 2 + 8, bits[i], 22,
                      POS if hi else INK, 'middle', bold=True))
        f.append(text(cx, ytop - 14, pos[i], 12,
                      POS if hi else MUTED, 'middle', bold=hi))

    yb = ytop + ch
    f.append(text(W / 2, yb + 42, '100  =  64 + 32 + 4  =  1100100₂',
                  15, INK, 'middle', bold=True))
    box, bw, bh = textbox(W / 2, yb + 100,
                          '2⁶ = 64  ≤  100  <  128 = 2⁷         ⌊log₂100⌋ = 6\n'
                          'на запис числа треба  6 + 1 = 7  бітів',
                          size=13, pad=12, fill=FILL, stroke=LINE)
    f.append(box)

    render(os.path.join(IMG, 'msb.svg'), W, H, *f,
           title='Ціла частина log₂ — позиція старшого біта')


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — log₂n = скільки разів поділити навпіл (64 → 1 за 6 кроків)
# ════════════════════════════════════════════════════════════════════════════
def fig_halving():
    W, H = 780, 300
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    vals = [64, 32, 16, 8, 4, 2, 1]
    n = len(vals)
    x0, step, y, r = 90, 100, 122, 24
    for i, v in enumerate(vals):
        cx = x0 + i * step
        f.append(circle(cx, y, r, fill=FILL, stroke=INK, sw=2))
        f.append(text(cx, y + 6, str(v), 16, INK, 'middle', bold=True))
        if i < n - 1:
            xa = cx + r + 5
            xb = x0 + (i + 1) * step - r - 5
            f.append(arrow(xa, y, xb, y, color=NEG, sw=1.8))
            f.append(text((xa + xb) / 2, y - 15, '÷2', 12, NEG, 'middle', bold=True))

    f.append(text(W / 2, 62, 'log₂ 64 = 6 — від 64 до 1 рівно шість ділень навпіл',
                  14, INK, 'middle', bold=True))
    box, bw, bh = textbox(W / 2, 214,
                          'Стільки ж кроків робить двійковий пошук і така висота збалансованого дерева.\n'
                          'Мільярд елементів долається за ~30 кроків, бо 2³⁰ ≈ 10⁹.',
                          size=12.5, pad=12, fill=FILL, stroke=LINE)
    f.append(box)

    render(os.path.join(IMG, 'halving.svg'), W, H, *f,
           title='log₂ n — скільки разів поділити навпіл до 1')


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 (вставка) — одна вісь, три лінійки
# Множинна вісь 1…1024; під нею три лінійки з РІЗНОЮ ціною поділки:
# біти (крок ×2), десяткові розряди (крок ×10), нати (крок ×e).
# Показує, що основа = ціна поділки, а перехід між основами = зміна лінійки.
# ════════════════════════════════════════════════════════════════════════════
def fig_rulers():
    W, H = 940, 452
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    X0, SPAN = 196, 672          # вісь: log₂ від 0 (x=X0) до 10 (x=X0+SPAN)
    TOP = 10.0                   # верх шкали у бітах

    def xof(bits):
        return X0 + (bits / TOP) * SPAN

    # ── верх: самі числа на множинній осі ─────────────────────────────────
    f.append(text(98, 96, 'число', 13, INK, 'middle', bold=True))
    f.append(text(98, 114, '(множення)', 11, MUTED, 'middle'))
    for k in range(11):
        x = xof(k)
        f.append(text(x, 100, str(2 ** k), 12, INK, 'middle', bold=True))
        f.append(line(x, 110, x, 124, color=MUTED, sw=1))
    f.append(line(X0 - 16, 124, X0 + SPAN + 16, 124, color=INK, sw=2))
    f.append(text((X0 + SPAN) / 2 + 98, 146,
                  'крок праворуч — це множення, а не додавання: сусіди різняться вдвічі',
                  11.5, MUTED, 'middle'))

    # ── три лінійки ───────────────────────────────────────────────────────
    # (назва, підпис-основа, крок у бітах, скільки поділок, колір)
    rulers = [
        ('біти',    'log₂  ·  крок ×2', 1.0,                 10, NEG),
        ('розряди', 'log₁₀ ·  крок ×10', math.log2(10),        3, POS),
        ('нати',    'ln    ·  крок ×e', math.log2(math.e),    6, FIELD),
    ]
    y = 178
    for name, sub, step_bits, nticks, col in rulers:
        bh = 30
        f.append(text(98, y + 12, name, 13, col, 'middle', bold=True))
        f.append(text(98, y + 30, sub, 10.5, MUTED, 'middle'))
        f.append(rect(X0, y, SPAN, bh, fill='#fbfcfd', stroke=col, sw=1.6, rx=4))
        for j in range(nticks + 1):
            x = xof(j * step_bits)
            f.append(line(x, y, x, y + bh, color=col, sw=1.4))
            f.append(text(x, y + bh + 15, str(j), 11.5, col, 'middle', bold=True))
        # хвіст поділки, що не влізла до кінця осі
        xlast = xof(nticks * step_bits)
        if X0 + SPAN - xlast > 3:
            f.append(rect(xlast, y, X0 + SPAN - xlast, bh,
                          fill='#eceff3', stroke='none', sw=0, rx=0))
        y += 76

    # ── висновок ──────────────────────────────────────────────────────────
    box, bw, bh2 = textbox(W / 2, 414,
                           'Вісь одна — лінійки три. На числі 1024 біти показують рівно 10, '
                           'розряди — 3.0103, нати — 6.9315.\n'
                           'Ціна поділки різна, вимірюване — те саме, тож перевести показ '
                           'однієї лінійки в іншу можна множенням на сталу.',
                           size=12, pad=11, fill=FILL, stroke=LINE)
    f.append(box)

    render(os.path.join(IMG, 'rulers.svg'), W, H, *f,
           title='Одна вісь, три лінійки — основа задає лише ціну поділки')


# ════════════════════════════════════════════════════════════════════════════
# Фігура 5 (вставка) — 2¹⁰ᵏ проти 10³ᵏ
# 10/3 = 3.333… — наближення до log₂10 = 3.3219…; похибка 2.4% на крок
# накопичується множенням і на йоті доходить до 20.9%.
# ════════════════════════════════════════════════════════════════════════════
def fig_drift():
    W, H = 880, 448
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    names = ['кіло', 'мега', 'гіга', 'тера', 'пета', 'екса', 'зета', 'йота']
    xbar, maxw = 320, 396
    y0, dy, bh = 74, 42, 24

    excess = [(2 ** (10 * k)) / (10 ** (3 * k)) - 1 for k in range(1, 9)]
    scale = maxw / max(excess)

    for i, (nm, ex) in enumerate(zip(names, excess)):
        y = y0 + i * dy
        f.append(text(26, y + bh / 2 + 5, nm, 12.5, INK, 'start', bold=True))
        f.append(text(104, y + bh / 2 + 5,
                      '2%s  ÷  10%s' % (sup(10 * (i + 1)), sup(3 * (i + 1))),
                      12.5, MUTED, 'start'))
        w = ex * scale
        f.append(rect(xbar, y, w, bh, fill='#fdecea', stroke=POS, sw=1.4, rx=3))
        f.append(text(xbar + w + 10, y + bh / 2 + 5,
                      '+%.1f %%' % (ex * 100), 12, POS, 'start', bold=True))

    f.append(line(xbar, y0 - 12, xbar, y0 + 8 * dy - 12, color=INK, sw=1.6))
    f.append(text(xbar, y0 - 20, 'збіг', 11, MUTED, 'middle'))

    box, bw, bh2 = textbox(W / 2, 410,
                           'log₂10 = 3.3219…, а 10/3 = 3.3333… — розбіжність лише 0.34 %, '
                           'тому 2¹⁰ = 1024 так спокусливо звати «тисячею».\n'
                           'Та похибка накопичується множенням: на йоті двійкова драбина '
                           'уже на п\'яту частину вища за десяткову.',
                           size=12, pad=11, fill=FILL, stroke=LINE)
    f.append(box)

    render(os.path.join(IMG, 'drift.svg'), W, H, *f,
           title='2¹⁰ ≈ 10³ — наближення, що розповзається')


# ════════════════════════════════════════════════════════════════════════════
# Фігура 6 (вставка hist) — форма історії: ланцюг проти окремих точок
# Теза вставки: log₂ — не теорема (яку успадковують), а одиниця (яку заводять
# під нагоду). Тому вгорі суцільна лінія зі стрілками, унизу — самі точки.
# ════════════════════════════════════════════════════════════════════════════
def fig_hist_timeline():
    W, H = 980, 452
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    x0, x1 = 118, 918

    # ── верхня вісь: десятковий логарифм — ланцюг ───────────────────────────
    yt = 122
    f.append(text(x0 - 8, yt - 60, 'ДЕСЯТКОВИЙ ЛОГАРИФМ — ланцюг: кожна ланка тримає попередню',
                  13.5, FIELD, 'start', bold=True))
    f.append(line(x0, yt, x1, yt, color=FIELD, sw=3))

    chain = [(x0 + 42, '1614', ['Непер']),
             (x0 + 226, '1617', ['Бріґс:', 'основа 10']),
             (x0 + 410, '1620', ['Бюрґі', 'друкує']),
             (x0 + 594, '1622', ['логарифмічна', 'лінійка']),
             (x0 + 762, 'до 1970-х', ['триста років', 'у кишені'])]
    for i, (cx, yr, lab) in enumerate(chain):
        f.append(circle(cx, yt, 8, fill=FIELD, stroke=FIELD, sw=2))
        f.append(text(cx, yt - 20, yr, 12, INK, 'middle', bold=True))
        f.append(mtext(cx, yt + 32, lab, size=11.5, color=MUTED, lh=1.3))
        if i < len(chain) - 1:
            f.append(arrow(cx + 14, yt, chain[i + 1][0] - 14, yt, color=FIELD, sw=2))

    # ── нижня вісь: двійковий логарифм — окремі точки ───────────────────────
    yb = 312
    f.append(text(x0 - 8, yb - 66, 'ДВІЙКОВИЙ ЛОГАРИФМ — чотири окремі зустрічі, жодної стрілки',
                  13.5, POS, 'start', bold=True))
    f.append(line(x0, yb, x1, yb, color=MUTED, sw=1.5, dash='3,7'))

    pts = [(x0 + 60, '200—600', ['джайнські книжники:', 'ардхаччхеда']),
           (x0 + 320, '1544', ['Штіфель:', 'таблиця степенів 2']),
           (x0 + 550, '1739', ['Ейлер:', 'октава = 1']),
           (x0 + 760, '1948', ['Шеннон:', 'біт'])]
    for cx, yr, lab in pts:
        f.append(circle(cx, yb, 9, fill='#fdecea', stroke=POS, sw=2.5))
        f.append(text(cx, yb - 21, yr, 12, POS, 'middle', bold=True))
        f.append(mtext(cx, yb + 34, lab, size=11.5, color=INK, lh=1.3))

    # провалля між точками — підписані над віссю, поміж датами
    gaps = [((pts[0][0] + pts[1][0]) / 2, '≈1000 років'),
            ((pts[1][0] + pts[2][0]) / 2, '195 років'),
            ((pts[2][0] + pts[3][0]) / 2, '209 років')]
    for cx, lab in gaps:
        f.append(text(cx, yb - 21, lab, 11.5, MUTED, 'middle', italic=True))

    box, bw, bh = textbox(W / 2, 414,
                          'Теорему успадковують — тому вона тягне ланцюг. Одиницю виміру заводять під нагоду:\n'
                          'нагода минула — одиницю поклали. Тому в log₂ немає лінії, є самі точки.',
                          size=12.5, pad=11, fill=FILL, stroke=LINE)
    f.append(box)

    render(os.path.join(IMG, 'hist-timeline.svg'), W, H, *f,
           title='Дві форми історії: ланцюг і окремі точки')


# ════════════════════════════════════════════════════════════════════════════
# Фігура 7 (вставка hist) — закон, який не розрізняє
# Ac (2-адичний порядок) і log₂ обидва ТОЧНО виконують f(m·n)=f(m)+f(n);
# розрізняє їх лише пряме питання про ЗНАЧЕННЯ (сотня: 2 проти 6.64).
# ════════════════════════════════════════════════════════════════════════════
def fig_hist_law():
    W, H = 900, 424
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    lx, rx = 258, 642
    cw = 320

    f.append(fitbox(lx - cw / 2, 60, cw, 34, 'ардхаччхеда Ac (2-адичний порядок)',
                    size=13, fill='#fdecea', stroke=POS, bold=True))
    f.append(fitbox(rx - cw / 2, 60, cw, 34, 'двійковий логарифм log₂',
                    size=13, fill='#eef6ee', stroke=FIELD, bold=True))

    # ── спільний закон ──────────────────────────────────────────────────────
    f.append(text(W / 2, 132, 'ОДИН І ТОЙ САМИЙ ЗАКОН:   f(m · n)  =  f(m) + f(n)',
                  14, INK, 'middle', bold=True))

    rows_l = ['Ac(12) = 2', 'Ac(40) = 3', 'Ac(480) = 5 = 2 + 3   ✔']
    rows_r = ['log₂12 = 3.5850', 'log₂40 = 5.3219', 'log₂480 = 8.9069 = сума   ✔']
    y0, dy = 164, 32
    for i in range(3):
        last = (i == 2)
        f.append(text(lx, y0 + i * dy, rows_l[i], 13,
                      POS if last else INK, 'middle', bold=last))
        f.append(text(rx, y0 + i * dy, rows_r[i], 13,
                      FIELD if last else INK, 'middle', bold=last))

    yline = y0 + 3 * dy - 2
    f.append(line(64, yline, W - 64, yline, color=MUTED, sw=1, dash='4,4'))

    # ── розрізняє лише значення ─────────────────────────────────────────────
    f.append(text(W / 2, yline + 32, 'РОЗРІЗНЯЄ ЛИШЕ ПРЯМЕ ПИТАННЯ ПРО ЗНАЧЕННЯ:',
                  14, INK, 'middle', bold=True))
    f.append(text(W / 2, yline + 54, 'скільки це для сотні?', 13, MUTED, 'middle', italic=True))

    yv = yline + 74
    f.append(fitbox(lx - 130, yv, 260, 44, '100 → 50 → 25  стоп       2',
                    size=14, fill='#fdecea', stroke=POS, bold=True))
    f.append(fitbox(rx - 130, yv, 260, 44, 'log₂100 = 6.6439',
                    size=14, fill='#eef6ee', stroke=FIELD, bold=True))

    box, bw, bh = textbox(W / 2, 388,
                          'Виконаний закон не називає функцію: він їй не портрет, '
                          'а лише прикмета, спільна з іншими.',
                          size=12.5, pad=11, fill=FILL, stroke=LINE)
    f.append(box)

    render(os.path.join(IMG, 'hist-law.svg'), W, H, *f,
           title='Закон, який не розрізняє: Ac і log₂ проходять ту саму перевірку')


# ════════════════════════════════════════════════════════════════════════════
# Фігура 8 (вставка hist) — Ейлерова таблиця («Tentamen», 1739, розділ VII)
# Відношення частот → log₂ → назва інтервалу. Стовпчик октав читається
# цілими 0,1,2,3 — основа перестала бути параметром і стала НАЗВОЮ ОДИНИЦІ.
# ════════════════════════════════════════════════════════════════════════════
def fig_hist_euler():
    W, H = 820, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    cx1, cx2, cx3 = 168, 388, 632
    w1, w2, w3 = 150, 170, 250
    hh, dy = 36, 46
    ytop = 102

    f.append(text(cx1, ytop - 18, 'відношення частот', 12.5, MUTED, 'middle', bold=True))
    f.append(text(cx2, ytop - 18, 'двійковий логарифм', 12.5, MUTED, 'middle', bold=True))
    f.append(text(cx3, ytop - 18, 'інтервал', 12.5, MUTED, 'middle', bold=True))

    rows = [('1 : 1', '0.000000', 'унісон', True),
            ('2 : 1', '1.000000', 'ОКТАВА — одиниця шкали', True),
            ('4 : 1', '2.000000', 'подвійна октава', True),
            ('8 : 1', '3.000000', 'потрійна октава', True),
            ('3 : 2', '0.584962', 'квінта', False),
            ('5 : 4', '0.321928', 'велика терція', False)]

    for i, (r, lg, name, whole) in enumerate(rows):
        cy = ytop + i * dy
        col = FIELD if whole else NEG
        bgc = '#eef6ee' if whole else '#eef1fd'
        f.append(fitbox(cx1 - w1 / 2, cy, w1, hh, r, size=14,
                        fill=FILL, stroke=LINE, bold=True))
        f.append(fitbox(cx2 - w2 / 2, cy, w2, hh, lg, size=14,
                        fill=bgc, stroke=col, bold=True))
        f.append(fitbox(cx3 - w3 / 2, cy, w3, hh, name, size=12.5,
                        fill=BG, stroke=MUTED, bold=whole))

    yb = ytop + len(rows) * dy

    f.append(text(W / 2, yb + 24,
                  'октави дають цілі 0, 1, 2, 3 — бо октава і Є одиниця цієї шкали',
                  13, FIELD, 'middle', bold=True))

    box, bw, bh = textbox(W / 2, yb + 72,
                          'Ейлер (§4): узяти можна будь-який канон логарифмів — але найзручніше той,\n'
                          'де логарифм двійки покладено за одиницю. Основа перестала бути параметром\n'
                          'і стала НАЗВОЮ ОДИНИЦІ: відповідь дається просто в октавах.',
                          size=12, pad=11, fill=FILL, stroke=LINE)
    f.append(box)

    render(os.path.join(IMG, 'hist-euler.svg'), W, H, *f,
           title='Ейлер, «Tentamen» (1739), розділ VII')


# ════════════════════════════════════════════════════════════════════════════
# Фігури вставки proj-ilog2.md — іграшковий масштаб B(2,3): вісім бітів,
# вікно три. Усе те саме, що й на 64 бітах з вікном шість, лише видно оком.
# ════════════════════════════════════════════════════════════════════════════
_C8 = 0b00010111          # де-Брейнова послідовність B(2,3), три нулі вгорі
_S8 = [int(b) for b in format(_C8, '08b')]      # _S8[0] — старший біт


def _bitcells(x0, y, bits, cw, ch, hi=(), size=15):
    """Рядок клітин-бітів; hi — індекси виділених (лічба від старшого)."""
    out = []
    for i, b in enumerate(bits):
        x = x0 + i * cw
        on = i in hi
        out.append(rect(x, y, cw, ch, fill='#fdecea' if on else FILL,
                        stroke=POS if on else LINE, sw=2 if on else 1.2, rx=4))
        out.append(text(x + cw / 2, y + ch / 2 + size * 0.36, str(b), size,
                        POS if on else INK, 'middle', bold=True))
    return out


# ── Фігура 9 — колесо де Брейна: усі вісім вікон різні ──────────────────────
def fig_proj_wheel():
    W, H = 880, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    cx, cy, R = 215, 255, 108
    f.append(circle(cx, cy, R, fill=BG, stroke=MUTED, sw=1.4))
    for p in range(8):
        a = math.radians(-90 + p * 45)
        bx, by = cx + R * math.cos(a), cy + R * math.sin(a)
        f.append(circle(bx, by, 21, fill=FILL, stroke=INK, sw=1.6))
        f.append(text(bx, by + 6, str(_S8[p]), 17, INK, 'middle', bold=True))
        lx, ly = cx + (R + 40) * math.cos(a), cy + (R + 40) * math.sin(a)
        f.append(text(lx, ly + 5, str(p), 12.5, MUTED, 'middle'))

    f.append(text(cx, cy - 8, 'по колу', 12.5, MUTED, 'middle'))
    f.append(text(cx, cy + 12, 'за годинниковою', 12.5, MUTED, 'middle'))
    f.append(text(cx, cy + 190, 's = 00010111', 15, INK, 'middle', bold=True))

    tx = 470
    f.append(text(tx + 175, 92, 'три підряд, починаючи з позиції p', 13.5,
                  INK, 'middle', bold=True))
    for p in range(8):
        y = 112 + p * 40
        win = ''.join(str(_S8[(p + i) % 8]) for i in range(3))
        f.append(rect(tx, y, 350, 32, fill=FILL if p % 2 == 0 else BG,
                      stroke='none', sw=0, rx=4))
        f.append(text(tx + 18, y + 21, 'p = %d' % p, 13.5, MUTED, 'start'))
        f.append(text(tx + 165, y + 21, win, 15, INK, 'middle', bold=True))
        f.append(text(tx + 290, y + 21, '= %d' % int(win, 2), 13.5, FIELD,
                      'middle', bold=True))

    box, bw, bh = textbox(W / 2, 458,
                          'Вісім вікон — вісім різних чисел 0…7, кожне рівно раз. Оце й є послідовність\n'
                          'де Брейна B(2,3). На 64 бітах те саме: B(2,6), усі 64 вікна по шість бітів різні.',
                          size=12.5, pad=11, fill=FILL, stroke=LINE)
    f.append(box)

    render(os.path.join(IMG, 'proj-wheel.svg'), W, H, *f,
           title='Послідовність де Брейна: кожне вікно трапляється рівно раз')


# ── Фігура 10 — множення прокручує вікно, таблиця = обернена перестановка ───
def fig_proj_slide():
    W, H = 900, 600
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 56, 'C = 00010111₂ — множення на 2ᵏ зсуває стрічку вліво на k, '
                             'зайве обрізається',
                  13, MUTED, 'middle'))

    x0, cw, ch = 120, 33, 34
    f.append(text(60, 96, 'k', 13, INK, 'middle', bold=True))
    f.append(text(x0 + 4 * cw, 96, '2ᵏ · C  (вісім бітів)', 13, INK, 'middle', bold=True))
    f.append(text(560, 96, 'верхні три', 13, POS, 'middle', bold=True))
    f.append(text(740, 96, 'таблиця', 13, FIELD, 'middle', bold=True))

    tab = [None] * 8
    for k in range(8):
        y = 112 + k * 46
        prod = ((1 << k) * _C8) & 0xFF
        idx = prod >> 5
        tab[idx] = k
        bits = format(prod, '08b')
        f.append(text(60, y + ch / 2 + 5, 'k = %d' % k, 13.5, MUTED, 'middle'))
        f.extend(_bitcells(x0, y, bits, cw, ch, hi=(0, 1, 2)))
        f.append(arrow(x0 + 8 * cw + 12, y + ch / 2, 500, y + ch / 2, color=MUTED, sw=1.4))
        f.append(text(560, y + ch / 2 + 5, '%s₂ = %d' % (bits[:3], idx), 13.5,
                      POS, 'middle', bold=True))
        f.append(arrow(620, y + ch / 2, 660, y + ch / 2, color=MUTED, sw=1.4))
        f.append(text(740, y + ch / 2 + 5, 'tab[%d] = %d' % (idx, k), 13.5,
                      FIELD, 'middle', bold=True))

    box, bw, bh = textbox(W / 2, 540,
                          'Вісім різних вікон дають вісім різних індексів — жодної колізії.\n'
                          'tab = [0, 1, 2, 4, 7, 3, 6, 5] — просто обернена перестановка: за індексом віддає k.\n'
                          'На 64 бітах усе те саме: вікно шість бітів, зсув «>> 58», таблиця на 64 числа.',
                          size=12.5, pad=11, fill=FILL, stroke=LINE)
    f.append(box)

    render(os.path.join(IMG, 'proj-slide.svg'), W, H, *f,
           title='Множення на 2ᵏ прокручує вікно — і воно називає k')


# ── Фігура 11 — каскад n |= n >> s: смуга одиниць подвоюється ───────────────
def fig_proj_smear():
    W, H = 880, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 54, 'n = 0010 0000 0000 0000 — старший біт на позиції 13',
                  13, MUTED, 'middle'))

    n = 0x2000
    rows = [('n', n, 1)]
    for sh in (1, 2, 4, 8):
        n |= n >> sh
        rows.append(('n |= n >> %d' % sh, n, min(2 * rows[-1][2], 14)))

    x0, cw, ch = 200, 27, 32
    for i, (lab, val, run) in enumerate(rows):
        y = 86 + i * 42
        f.append(text(30, y + ch / 2 + 5, lab, 13.5, INK, 'start', bold=(i == 0)))
        bits = format(val, '016b')
        f.extend(_bitcells(x0, y, bits, cw, ch, hi=tuple(range(2, 2 + run)), size=13))
        f.append(text(x0 + 16 * cw + 22, y + ch / 2 + 5, 'смуга: %d' % run, 13,
                      MUTED, 'start'))

    box, bw, bh = textbox(W / 2, 372,
                          'Смуга одиниць подвоюється щокроку: 1 → 2 → 4 → 8 → 16. Тому шістнадцять бітів\n'
                          'беруть чотири кроки, а 64 — шість (1, 2, 4, 8, 16, 32), бо 2⁶ = 64: скільки кроків\n'
                          'треба, каже сам двійковий логарифм ширини слова. Наприкінці n = 2¹⁴ − 1 — суцільна\n'
                          'смуга від старшого біта вниз, і n − (n >> 1) лишає з неї сам старший біт.',
                          size=12, pad=11, fill=FILL, stroke=LINE)
    f.append(box)

    render(os.path.join(IMG, 'proj-smear.svg'), W, H, *f,
           title='Каскад n |= n >> s — розмазати старший біт донизу')


if __name__ == '__main__':
    fig_ladder()
    fig_msb()
    fig_halving()
    fig_rulers()
    fig_drift()
    fig_hist_timeline()
    fig_hist_law()
    fig_hist_euler()
    fig_proj_wheel()
    fig_proj_slide()
    fig_proj_smear()
    print('OK: ladder.svg, msb.svg, halving.svg, rulers.svg, drift.svg, '
          'hist-timeline.svg, hist-law.svg, hist-euler.svg, '
          'proj-wheel.svg, proj-slide.svg, proj-smear.svg')
