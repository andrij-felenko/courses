# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SEL = "#8e44ad"   # підсвітка спільного вузла
Z0 = NEG          # гілка «0» — синій штрих
Z1 = INK          # гілка «1» — темна суцільна


def node(cx, cy, label, r=17, ring=None):
    out = ""
    if ring:
        out += circle(cx, cy, r + 5, fill="none", stroke=ring, sw=3)
    out += circle(cx, cy, r, fill=FILL, stroke=INK, sw=1.8)
    out += text(cx, cy + 5, label, size=15, bold=True)
    return out


def leaf(cx, cy, val, w=32, h=28, ring=None):
    out = ""
    if ring:
        out += rect(cx - w/2 - 4, cy - h/2 - 4, w + 8, h + 8, fill="none", stroke=ring, sw=3, rx=6)
    fill = "#eaf0fd" if val == "0" else "#fdecea"
    col = NEG if val == "0" else POS
    out += rect(cx - w/2, cy - h/2, w, h, fill=fill, stroke=col, sw=1.8, rx=5)
    out += text(cx, cy + 5, val, size=15, color=col, bold=True)
    return out


def branch(x1, y1, x2, y2, kind):
    if kind == 0:
        return line(x1, y1, x2, y2, color=Z0, sw=1.7, dash="5,4")
    return line(x1, y1, x2, y2, color=Z1, sw=1.9)


def legend(x, y):
    f = line(x, y, x + 30, y, color=Z0, sw=1.7, dash="5,4")
    f += text(x + 36, y + 4, "гілка 0 (за штрихом)", size=11, color=MUTED, anchor="start")
    f += line(x + 190, y, x + 220, y, color=Z1, sw=1.9)
    f += text(x + 226, y + 4, "гілка 1 (суцільна)", size=11, color=MUTED, anchor="start")
    return f


# ── 1. Канонічність: різні вирази → та сама діаграма ────────────────────────
def fig_canonical_collapse():
    W, H = 1000, 520
    f = [text(W/2, 28, "Канонічність: різні записи однієї функції злипаються в одну діаграму",
              size=16.5, bold=True)]

    # ── ЛІВОРУЧ: два вирази ──
    f.append(text(196, 92, "Три записи «більшості з a, b, c»", size=13, bold=True, color=MUTED))
    b, _, _ = textbox(196, 148, "a·b + b·c + a·c", size=15, pad=12,
                      fill="#f0f7f1", stroke=FIELD, bold=True)
    f.append(b)
    b, _, _ = textbox(196, 214, "a·b + c·(a + b)", size=15, pad=12,
                      fill="#f0f7f1", stroke=FIELD, bold=True)
    f.append(b)
    b, _, _ = textbox(196, 280, "(a+b)·(b+c)·(a+c)", size=15, pad=12,
                      fill="#f0f7f1", stroke=FIELD, bold=True)
    f.append(b)
    f.append(text(196, 336, "різні формули — одна функція", size=12, color=MUTED))
    f.append(text(196, 356, "порівняти їх як тексти — марно", size=12, color=MUTED))

    # ── стрілка ──
    f.append(arrow(322, 232, 452, 232, color=INK, sw=2.2))
    b, _, _ = textbox(388, 194, ["скоротити", "+ упорядкувати"], size=11.5, pad=7,
                      fill=BG, stroke=MUTED, color=MUTED)
    f.append(b)

    # ── ПРАВОРУЧ: єдина ROBDD більшості (порядок a → b → c) ──
    f.append(text(770, 92, "єдина скорочена впорядкована діаграма", size=13, bold=True, color=MUTED))
    # рівневі підказки
    for lv, yy in (("a", 150), ("b", 250), ("c", 350)):
        f.append(text(596, yy + 5, lv, size=12.5, color=MUTED, bold=True))
    f.append(text(596, 118, "порядок", size=11, color=MUTED))

    A = (770, 150)
    B0, B1 = (678, 250), (866, 250)
    C = (772, 350)
    T0, T1 = (678, 452), (866, 452)

    f.append(branch(A[0] - 9, A[1] + 15, B0[0] + 7, B0[1] - 17, 0))
    f.append(branch(A[0] + 9, A[1] + 15, B1[0] - 7, B1[1] - 17, 1))
    f.append(branch(B0[0] - 6, B0[1] + 16, T0[0], T0[1] - 17, 0))
    f.append(branch(B0[0] + 8, B0[1] + 15, C[0] - 13, C[1] - 16, 1))
    f.append(branch(B1[0] - 8, B1[1] + 15, C[0] + 13, C[1] - 16, 0))
    f.append(branch(B1[0] + 6, B1[1] + 16, T1[0], T1[1] - 17, 1))
    f.append(branch(C[0] - 8, C[1] + 15, T0[0] + 9, T0[1] - 17, 0))
    f.append(branch(C[0] + 8, C[1] + 15, T1[0] - 9, T1[1] - 17, 1))

    f.append(node(*A, "a"))
    f.append(node(*B0, "b"))
    f.append(node(*B1, "b"))
    f.append(node(*C, "c", ring=SEL))
    f.append(leaf(*T0, "0"))
    f.append(leaf(*T1, "1"))

    # пояснення спільного вузла — під терміналами, де немає гілок
    f.append(text(772, 490, "фіолетовий «c» — спільний вузол: два батьки, тож це граф, а не дерево",
                  size=11.5, color=SEL, bold=True))

    f.append(legend(150, 494))
    render(os.path.join(OUT, 'canonical-collapse.svg'), W, H, *f)


# ── 2. Apply: розклад за спільною змінною + кеш ──────────────────────────────
def pairbox(cx, cy, s, dim=False):
    if dim:
        b, w, h = textbox(cx, cy, s, size=13.5, pad=9, fill=BG, stroke=MUTED,
                          color=MUTED, bold=True)
    else:
        b, w, h = textbox(cx, cy, s, size=13.5, pad=9, fill="#eef2fb", stroke=NEG,
                          color=NEG, bold=True)
    return b, w, h


def fig_apply_recursion():
    W, H = 1020, 560
    f = [text(W/2, 28, "Apply: комбінуємо дві діаграми розкладом за спільною змінною",
              size=16.5, bold=True)]

    b, _, _ = textbox(510, 82, "(f ∧ g)  =  ¬x·(f₀ ∧ g₀)  +  x·(f₁ ∧ g₁)", size=15.5, pad=12,
                      fill="#f0f7f1", stroke=FIELD, bold=True)
    f.append(b)
    f.append(text(510, 122, "розклали обидві за верхньою змінною x — і так само рекурсивно на кофакторах",
                  size=12, color=MUTED))

    # рівні дерева викликів
    L0 = (510, 178)
    L1a, L1b = (326, 288), (694, 288)
    L2 = [(214, 400), (416, 400), (604, 400), (806, 400)]
    labels2 = ["(p, q)", "(r, s)", "(r, s)", "(u, v)"]

    # ребра
    f.append(branch(L0[0] - 10, L0[1] + 16, L1a[0] + 10, L1a[1] - 16, 0))
    f.append(branch(L0[0] + 10, L0[1] + 16, L1b[0] - 10, L1b[1] - 16, 1))
    f.append(branch(L1a[0] - 10, L1a[1] + 16, L2[0][0] + 8, L2[0][1] - 16, 0))
    f.append(branch(L1a[0] + 10, L1a[1] + 16, L2[1][0] - 8, L2[1][1] - 16, 1))
    f.append(branch(L1b[0] - 10, L1b[1] + 16, L2[2][0] + 8, L2[2][1] - 16, 0))
    f.append(branch(L1b[0] + 10, L1b[1] + 16, L2[3][0] - 8, L2[3][1] - 16, 1))

    # вузли-пари
    b, _, _ = pairbox(*L0, "(f, g)"); f.append(b)
    b, _, _ = pairbox(*L1a, "(f₀, g₀)"); f.append(b)
    b, _, _ = pairbox(*L1b, "(f₁, g₁)"); f.append(b)
    for i, (pt, lab) in enumerate(zip(L2, labels2)):
        b, _, _ = pairbox(*pt, lab, dim=(i == 2))
        f.append(b)

    # кеш-стрілка: права (r,s) → ліва (r,s)
    f.append(line(L2[2][0] - 48, 400, L2[1][0] + 48, 400, color=SEL, sw=2, dash="6,4"))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
        L2[1][0] + 48, 400, L2[1][0] + 60, 395, L2[1][0] + 60, 405, SEL))
    f.append(text(510, 384, "кеш: та сама пара — не рахуємо вдруге", size=11.5, color=SEL, bold=True))

    # термінальне правило
    b, _, _ = textbox(214, 470, ["термінал:", "0 ∧ g = 0,  1 ∧ g = g"], size=12, pad=9,
                      fill="#eaf0fd", stroke=NEG, color=NEG)
    f.append(b)
    b, _, _ = textbox(760, 470, ["різних пар — щонайбільше |f|·|g|", "→ стільки ж і роботи"],
                      size=12.5, pad=10, fill="#f0f7f1", stroke=FIELD, color=FIELD, bold=True)
    f.append(b)

    f.append(text(W/2, 534, "Наївно розклад дав би дерево на 2ⁿ листків; кеш пар (f,g) робить його "
                            "лінійним за розміром обох діаграм.",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'apply-recursion.svg'), W, H, *f)


# ── 3. Множина — це булева функція (символьна перевірка) ─────────────────────
def fig_set_as_function():
    W, H = 1040, 520
    f = [text(W/2, 28, "Множина станів — це булева функція, а функція — це діаграма",
              size=16.5, bold=True)]

    # ── ЛІВОРУЧ: таблиця S як χ ──
    f.append(text(196, 74, "множина S ⊆ усіх станів", size=13, bold=True, color=MUTED))
    f.append(text(196, 94, "χ(s) = 1  ⟺  s належить S", size=12, color=MUTED))
    states = ["000", "001", "010", "011", "100", "101", "110", "111"]
    chi = [0, 0, 0, 1, 0, 1, 1, 1]   # «більшість бітів = 1»
    x0, rw, rh = 92, 208, 40
    y0 = 122
    f.append(text(x0 + 58, y0 - 10, "s₂s₁s₀", size=11.5, color=MUTED))
    f.append(text(x0 + rw - 42, y0 - 10, "χ", size=11.5, color=MUTED))
    for i, (s, c) in enumerate(zip(states, chi)):
        y = y0 + i * (rh + 3)
        on = c == 1
        fill = "#fdecea" if on else FILL
        stroke = POS if on else "#d5d9de"
        f.append(rect(x0, y, rw, rh, fill=fill, stroke=stroke, sw=1.5))
        f.append(line(x0 + rw - 66, y, x0 + rw - 66, y + rh, color="#d5d9de", sw=1.1))
        f.append(text(x0 + 40, y + rh/2 + 5, s, size=14, anchor="middle",
                      bold=on, color=(POS if on else INK)))
        f.append(text(x0 + rw - 34, y + rh/2 + 5, str(c), size=14, anchor="middle",
                      bold=True, color=(POS if on else MUTED)))
    f.append(text(196, y0 + 8*(rh+3) + 16, "S = стани, де більшість бітів = 1", size=12, color=MUTED))

    # ── стрілка ──
    f.append(arrow(330, 300, 470, 300, color=INK, sw=2.2))
    b, _, _ = textbox(400, 262, ["та сама", "діаграма"], size=11.5, pad=7,
                      fill=BG, stroke=MUTED, color=MUTED)
    f.append(b)

    # ── ПРАВОРУЧ: компактна ROBDD ──
    f.append(text(772, 74, "ROBDD характеристичної функції", size=13, bold=True, color=MUTED))
    A = (772, 122)
    B0, B1 = (690, 210), (854, 210)
    C = (774, 300)
    T0, T1 = (690, 392), (854, 392)
    f.append(branch(A[0] - 9, A[1] + 14, B0[0] + 7, B0[1] - 16, 0))
    f.append(branch(A[0] + 9, A[1] + 14, B1[0] - 7, B1[1] - 16, 1))
    f.append(branch(B0[0] - 6, B0[1] + 15, T0[0], T0[1] - 16, 0))
    f.append(branch(B0[0] + 8, B0[1] + 14, C[0] - 12, C[1] - 15, 1))
    f.append(branch(B1[0] - 8, B1[1] + 14, C[0] + 12, C[1] - 15, 0))
    f.append(branch(B1[0] + 6, B1[1] + 15, T1[0], T1[1] - 16, 1))
    f.append(branch(C[0] - 8, C[1] + 14, T0[0] + 9, T0[1] - 16, 0))
    f.append(branch(C[0] + 8, C[1] + 14, T1[0] - 9, T1[1] - 16, 1))
    f.append(node(*A, "s₂", r=17))
    f.append(node(*B0, "s₁", r=17))
    f.append(node(*B1, "s₁", r=17))
    f.append(node(*C, "s₀", r=17, ring=SEL))
    f.append(leaf(*T0, "0"))
    f.append(leaf(*T1, "1"))

    b, _, _ = textbox(772, 462, ["8 станів → 6 вузлів.", "структурована множина з 10²⁰ станів",
                                 "теж уміщається в дрібну діаграму"],
                      size=12, pad=10, fill="#f0f7f1", stroke=FIELD, color=FIELD, bold=True)
    f.append(b)
    render(os.path.join(OUT, 'set-as-function.svg'), W, H, *f)


# ── 4. Дві — і лише дві — неоднозначності, що їх знімають R1 і R2 ─────────────
def fig_two_reductions():
    W, H = 1060, 430
    f = [text(W/2, 30, "Рівно дві локальні неоднозначності — рівно два правила скорочення",
              size=16.5, bold=True)]

    # роздільник між панелями
    f.append(line(530, 74, 530, 366, color="#d5d9de", sw=1.4, dash="4,5"))

    # ── ЛІВА панель: R1 ──
    f.append(text(255, 68, "R1 — зайве питання", size=14, bold=True))
    f.append(text(255, 90, "обидві гілки — в одне місце", size=12, color=MUTED))

    # before: v → w двома гілками
    V = (150, 150)
    Wn = (150, 278)
    f.append(branch(V[0] - 10, V[1] + 15, Wn[0] - 8, Wn[1] - 18, 0))
    f.append(branch(V[0] + 10, V[1] + 15, Wn[0] + 8, Wn[1] - 18, 1))
    f.append(node(*V, "xᵢ"))
    f.append(node(*Wn, "w"))

    # arrow
    f.append(arrow(258, 214, 350, 214, color=INK, sw=2.2))

    # after: сам w, зверху перенаправлені стрілки
    Wa = (438, 238)
    f.append(arrow(438, 158, 438, 214, color=MUTED, sw=1.8))
    f.append(text(438, 148, "батьки — прямо сюди", size=10.5, color=MUTED))
    f.append(node(*Wa, "w"))
    f.append(text(255, 348, "вузол нічого не вирішує — прибрати", size=11.5, color=INK))

    # ── ПРАВА панель: R2 ──
    f.append(text(800, 68, "R2 — двійники", size=14, bold=True))
    f.append(text(800, 90, "однаковий підпис (xᵢ, p, q)", size=12, color=MUTED))

    # before: u, v з однаковими дітьми p, q
    U = (648, 152)
    Vr = (762, 152)
    P = (648, 280)
    Q = (762, 280)
    f.append(text(U[0], U[1] - 26, "u", size=11, color=MUTED))
    f.append(text(Vr[0], Vr[1] - 26, "v", size=11, color=MUTED))
    # u: lo→p, hi→q ;  v: lo→p, hi→q
    f.append(branch(U[0] - 8, U[1] + 16, P[0] - 6, P[1] - 18, 0))
    f.append(branch(U[0] + 10, U[1] + 15, Q[0] - 8, Q[1] - 18, 1))
    f.append(branch(Vr[0] - 10, Vr[1] + 15, P[0] + 8, P[1] - 18, 0))
    f.append(branch(Vr[0] + 8, Vr[1] + 16, Q[0] + 6, Q[1] - 18, 1))
    f.append(node(*U, "xᵢ"))
    f.append(node(*Vr, "xᵢ"))
    f.append(node(*P, "p"))
    f.append(node(*Q, "q"))

    # arrow
    f.append(arrow(828, 214, 900, 214, color=INK, sw=2.2))

    # after: один вузол m, два батьки, ті самі p, q
    M = (988, 150)
    Pa = (960, 282)
    Qa = (1016, 282)
    f.append(arrow(968, 104, 980, 133, color=MUTED, sw=1.7))
    f.append(arrow(1008, 104, 996, 133, color=MUTED, sw=1.7))
    f.append(text(988, 96, "два батьки", size=10.5, color=SEL, bold=True))
    f.append(branch(M[0] - 8, M[1] + 15, Pa[0] + 4, Pa[1] - 18, 0))
    f.append(branch(M[0] + 8, M[1] + 15, Qa[0] - 4, Qa[1] - 18, 1))
    f.append(node(*M, "xᵢ", ring=SEL))
    f.append(node(*Pa, "p"))
    f.append(node(*Qa, "q"))
    f.append(text(800, 348, "та сама трійка — один спільний вузол", size=11.5, color=INK))

    f.append(legend(255, 392))
    f.append(text(800, 396, "Решту випадків розрізняє сам порядок — без правил.",
                  size=11.5, color=MUTED))
    render(os.path.join(OUT, 'two-reductions.svg'), W, H, *f)


# ── 5. Дві таблиці ядра пакета: унікальна + кеш операцій ─────────────────────
def fig_two_tables():
    W, H = 1040, 560
    f = [text(W/2, 30, "Дві таблиці ядра: унікальна тримає граф малим, кеш — обчислення швидкими",
              size=16, bold=True)]

    # ── ЛІВА панель: унікальна таблиця ──
    lx, lw = 60, 430
    f.append(rect(lx, 66, lw, 300, fill=BG, stroke=NEG, sw=1.6, rx=10))
    f.append(text(lx + lw/2, 96, "Унікальна таблиця", size=14.5, bold=True, color=NEG))
    f.append(text(lx + lw/2, 116, "hash-consing — канонічність", size=11.5, color=MUTED))
    b, _, _ = textbox(lx + 118, 170, "(var, lo, hi)", size=13, pad=10,
                      fill="#eef2fb", stroke=NEG, color=NEG, bold=True)
    f.append(b)
    f.append(arrow(lx + 210, 170, lx + 300, 170, color=INK, sw=2))
    b, _, _ = textbox(lx + 358, 170, "наявний #k", size=13, pad=10, fill=FILL, stroke=INK, bold=True)
    f.append(b)
    f.append(text(lx + lw/2, 232, "діє у make_node — перед народженням вузла", size=11.5, color=MUTED))
    f.append(text(lx + lw/2, 266, "двійників не існує:", size=12, color=INK, bold=True))
    f.append(text(lx + lw/2, 286, "структурна рівність = рівність індексів", size=12, color=INK))
    f.append(text(lx + lw/2, 326, "кошики вплетено в сам пул через поле next", size=11.5, color=MUTED))
    f.append(text(lx + lw/2, 346, "(гібридна структура, Brace–Rudell–Bryant, 1990)", size=11, color=MUTED))

    # ── ПРАВА панель: кеш операцій ──
    rx, rw = 550, 430
    f.append(rect(rx, 66, rw, 300, fill=BG, stroke=FIELD, sw=1.6, rx=10))
    f.append(text(rx + rw/2, 96, "Кеш операцій", size=14.5, bold=True, color=FIELD))
    f.append(text(rx + rw/2, 116, "computed table — швидкість", size=11.5, color=MUTED))
    b, _, _ = textbox(rx + 112, 170, "(f, g, h)", size=13, pad=10,
                      fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    f.append(b)
    f.append(arrow(rx + 188, 170, rx + 300, 170, color=INK, sw=2))
    b, _, _ = textbox(rx + 360, 170, "результат #r", size=13, pad=10, fill=FILL, stroke=INK, bold=True)
    f.append(b)
    f.append(text(rx + rw/2, 232, "діє у ite — до рекурсії", size=11.5, color=MUTED))
    f.append(text(rx + rw/2, 266, "та сама трійка — не рахуємо вдруге:", size=12, color=INK, bold=True))
    f.append(text(rx + rw/2, 286, "експонента згортається в O(|f|·|g|)", size=12, color=INK))
    f.append(text(rx + rw/2, 326, "втратний: слот вільно перезаписуємо —", size=11.5, color=MUTED))
    f.append(text(rx + rw/2, 346, "промах лише сповільнює, ніколи не псує", size=11.5, color=MUTED))

    # ── СПІЛЬНИЙ пул вузлів унизу ──
    py = 428
    f.append(text(W/2, py - 4, "спільний пул вузлів nodes[] — вузол це індекс", size=12,
                  color=MUTED, bold=True))
    chips = [("#0", "0"), ("#1", "1"), ("#4", "c"), ("#5", "b"), ("#6", "b"), ("#7", "a")]
    n = len(chips); cw, gap = 118, 24
    total = n * cw + (n - 1) * gap
    x0 = (W - total) / 2
    for i, (idx, lab) in enumerate(chips):
        cx = x0 + i * (cw + gap)
        shared = idx == "#4"
        f.append(rect(cx, py + 8, cw, 50, fill=("#f3ecfa" if shared else FILL),
                      stroke=(SEL if shared else INK), sw=(2.4 if shared else 1.4), rx=8))
        f.append(text(cx + cw/2, py + 29, idx, size=13, bold=True, color=(SEL if shared else INK)))
        f.append(text(cx + cw/2, py + 48, lab, size=12, color=MUTED))
    f.append(text(W/2, py + 88, "вузол #4 (c) має двох батьків — його тримають #5 і #6; "
                                "унікальна таблиця не дала його задублювати",
                  size=11.5, color=SEL, bold=True))
    render(os.path.join(OUT, 'two-tables.svg'), W, H, *f)


# ── 6. Часова дуга: як символьне подання відкоркувало перевірку моделей ──────
def fig_symbolic_breakthrough():
    W, H = 1080, 600
    PX0, PX1 = 132, 992          # межі осі x (роки)
    PY0, PY1 = 108, 486          # верх / низ поля (лог-шкала станів)

    def xf(yr):
        return PX0 + (yr - 1980) / 28.0 * (PX1 - PX0)

    def yf(l):
        return PY1 - l / 21.0 * (PY1 - PY0)

    f = [text(W / 2, 32, "Стеля перевірки моделей за роками: що змінила канонічна форма",
              size=16.5, bold=True)]
    f.append(text(W / 2, 54, "скільки станів реально під силу охопити (лог-шкала)",
                  size=12, color=MUTED))

    # ── бліді горизонтальні лінії сітки (під кривою) ──
    # l=5 обриваємо перед карткою після 1990 (772±183, тобто ~589..955) — інакше
    # лінія сітки проходить наскрізь під текстом картки
    card_after_left = 772 - 366.86 / 2 - 14
    for l in (5, 10, 15, 20):
        x_end = card_after_left if l == 5 else PX1
        f.append(line(PX0, yf(l), x_end, yf(l), color="#eef0f2", sw=1))

    # ── осі ──
    f.append(line(PX0, PY0 - 6, PX0, PY1, color=INK, sw=1.6))
    f.append(line(PX0, PY1, PX1, PY1, color=INK, sw=1.6))
    for l, lab in ((0, "10⁰"), (5, "10⁵"), (10, "10¹⁰"), (15, "10¹⁵"), (20, "10²⁰")):
        yy = yf(l)
        f.append(line(PX0 - 5, yy, PX0, yy, color=INK, sw=1.3))
        f.append(text(PX0 - 11, yy + 4, lab, size=11, color=MUTED, anchor="end"))
    for yr in (1981, 1986, 1990, 1994, 2000, 2007):
        xx = xf(yr)
        f.append(line(xx, PY1, xx, PY1 + 5, color=INK, sw=1.3))
        f.append(text(xx, PY1 + 21, str(yr), size=11, color=MUTED))

    # ── стеля прямого перебору ──
    yc = yf(6.7)
    f.append(line(PX0, yc, xf(1990.3), yc, color=POS, sw=1.5, dash="6,4"))
    f.append(text(xf(1981.4), yc - 9, "стеля прямого перебору ≈ 10⁶–10⁷ станів",
                  size=11, color=POS, anchor="start"))

    # ── крива «під силу»: десятиліття повзе, 1990 — вертикальний стрибок ──
    pts = [(xf(1981), yf(4.0)), (xf(1986), yf(5.6)), (xf(1989), yf(6.2)),
           (xf(1990), yf(6.4)), (xf(1990), yf(20.0)), (xf(1994), yf(20.2)),
           (xf(2007), yf(20.6))]
    f.append('<polyline fill="none" stroke="%s" stroke-width="3" points="%s"/>'
             % (NEG, " ".join("%.1f,%.1f" % p for p in pts)))

    # ── стрибок 1990: підпис збоку ──
    f.append(text(xf(1990) + 12, yf(13.2), "×10¹⁴", size=16, color=FIELD, bold=True, anchor="start"))
    f.append(text(xf(1990) + 12, yf(11.6), "за чотири роки", size=11, color=FIELD, anchor="start"))

    # ── концептуальні підписи двох режимів ──
    f.append(text(xf(1981.4), yf(2.0), "перебір: увесь граф станів — у пам'ять",
                  size=11.5, color=MUTED, anchor="start"))
    f.append(text(xf(1995.4), yf(18.3), "символьно: множина станів — одна діаграма",
                  size=11.5, color=FIELD, anchor="start", bold=True))

    # ── віхи до 1990: крапки на кривій + одна зведена картка (без збігів) ──
    for yr, l in ((1981, 4.0), (1986, 5.6), (1989, 6.2)):
        f.append(circle(xf(yr), yf(l), 4.2, fill=NEG, stroke=BG, sw=1.3))
    pre_card = ["1981 · перевірка моделей народжується",
                "          — стани перебираються поодинці",
                "1986 · канонічна діаграма — двигун чекає",
                "1989 · символьний обхід (Bull, Франція)"]
    pb, pbw, pbh = textbox(300, 236, pre_card, size=11.5, pad=13,
                           fill="#fbf6f4", stroke=MUTED, color=INK)
    # поводок від картки до точки 1986 обходить праворуч підпис «стеля прямого
    # перебору» (він тягнеться від x≈175 до x≈390) — інакше пряма перетинала б напис
    ly0 = 236 + pbh / 2
    lx, ly = xf(1986), yf(5.6) - 9
    f.append(line(300, ly0, 420, ly0 + 20, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(420, ly0 + 20, 420, ly, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(420, ly, lx, ly, color=MUTED, sw=1.2, dash="4,4"))
    f.append(pb)

    # ── віхи після 1990: крапки + єдина зведена картка (без нагромадження) ──
    for yr, l in ((1990, 20.0), (1992, 20.1), (1994, 20.2), (2007, 20.6)):
        f.append(circle(xf(yr), yf(l), 4.2, fill=NEG, stroke=BG, sw=1.3))
    card = ["1990 · «10²⁰ станів і далі»",
            "         Burch · Clarke · McMillan · Dill · Hwang",
            "1992 · SMV — перший символьний інструмент (McMillan)",
            "1994 · Pentium FDIV, $475 млн → індустрія",
            "2007 · Тюрінгова премія за перевірку моделей"]
    b, bw, bh = textbox(772, 404, card, size=11.5, pad=13,
                        fill="#f4faf6", stroke=FIELD, color=INK)
    # тонкий поводок від картки до плато
    f.append(line(772, 404 - bh / 2, xf(1993.5), yf(20.1) + 9, color=FIELD, sw=1.2, dash="4,4"))
    f.append(b)

    render(os.path.join(OUT, 'symbolic-breakthrough.svg'), W, H, *f)


if __name__ == "__main__":
    fig_canonical_collapse()
    fig_apply_recursion()
    fig_set_as_function()
    fig_two_reductions()
    fig_two_tables()
    fig_symbolic_breakthrough()
    print("OK: figures written to", OUT)
