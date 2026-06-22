# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── tree-budget: кодове слово на глибині ℓ «займає» частку 2^(−ℓ) дерева ───────
# Ідея: нескінченне двійкове дерево; обравши слово на глибині ℓ, ми відрізаємо
# під ним цілу піддерево-гілку — це 2^(−ℓ) усіх нескінченних листків. Префіксність
# означає, що відрізані піддерева не перетинаються, тож сума часток ≤ 1.

def _dot(cx, cy, r, fill, stroke, p, sw=1.6):
    p.append(circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw))


def fig_tree_budget():
    W, H = 660, 380
    p = []
    r = 11
    # координати повного дерева на 3 рівні
    root = (330, 60)
    L1 = [(210, 130), (450, 130)]                       # глибина 1
    L2 = [(150, 205), (270, 205), (390, 205), (510, 205)]  # глибина 2
    # ребра кореня
    for (x, y) in L1:
        p.append(line(root[0], root[1] + r, x, y - r, color=MUTED, sw=1.4))
    # ребра рівня 1 → 2
    pairs = [(L1[0], L2[0]), (L1[0], L2[1]), (L1[1], L2[2]), (L1[1], L2[3])]
    for (a, b) in pairs:
        p.append(line(a[0], a[1] + r, b[0], b[1] - r, color=MUTED, sw=1.4))
    # під рівнем 2 — натяк на нескінченне продовження (трикутнички-піддерева)
    for (x, y) in L2:
        p.append(line(x, y + r, x - 22, y + 60, color="#c8ced6", sw=1.2))
        p.append(line(x, y + r, x + 22, y + 60, color="#c8ced6", sw=1.2))
        p.append(line(x - 22, y + 60, x + 22, y + 60, color="#c8ced6", sw=1.2, dash="3,3"))

    # позначка біта на ребрах кореня
    p.append(text(255, 92, "0", size=12, color=NEG, bold=True))
    p.append(text(405, 92, "1", size=12, color=POS, bold=True))

    # ВИДІЛЕНЕ слово A на глибині 1 (ліве): під ним відрізаємо все ліве піддерево
    # підсвітимо зону лівого піддерева
    p.append(rect(120, 112, 130, 158, fill="#fdecea", stroke=POS, sw=1.6, rx=10))
    p.append(text(185, 290, "слово на глибині 1", size=11, color=POS, bold=True))
    p.append(text(185, 307, "займає 1/2 дерева", size=11, color=POS))

    # ВИДІЛЕНЕ слово на глибині 2 (вузол L2[2]=390): займає 1/4
    p.append(rect(368, 188, 44, 82, fill="#eaf7ee", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(455, 250, "глибина 2", size=11, color=FIELD, bold=True))
    p.append(text(455, 267, "займає 1/4", size=11, color=FIELD))

    # вузли
    _dot(root[0], root[1], r, "#eaf2fb", INK, p)
    # L1: лівий — кодове слово (гаряче), правий — внутрішній
    _dot(L1[0][0], L1[0][1], r, "#f3c6bf", POS, p)
    _dot(L1[1][0], L1[1][1], r, "#eaf2fb", INK, p)
    # L2: третій — кодове слово (зелене), решта — внутрішні
    for i, (x, y) in enumerate(L2):
        if i == 2:
            _dot(x, y, r, "#d7f0de", FIELD, p)
        else:
            _dot(x, y, r, "#eaf2fb", INK, p)

    p.append(text(W / 2, H - 16,
                  "кодове слово на глибині ℓ відрізає під собою частку 2^(−ℓ) листків",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "tree-budget.svg"), W, H, *p,
           title="Бюджет дерева: слово глибини ℓ коштує 2^(−ℓ)")


# ── kraft-sum: набори довжин на «бюджеті» [0,1) — один влазить, інший ні ───────
# Ідея: кожне слово довжини ℓ — це блок ширини 2^(−ℓ). Якщо блоки вкладаються в
# одиничний відрізок без накладання — код існує; якщо переповнюють — ні.

def _budget_bar(x0, y0, width, blocks, p, ok):
    # blocks: список (мітка, частка). малюємо суміжні блоки зліва направо
    cx = x0
    for (lab, frac) in blocks:
        w = frac * width
        fill = "#cfe0f5"
        p.append(rect(cx, y0, w, 34, fill=fill, stroke=NEG, sw=1.4, rx=3))
        if w > 26:
            p.append(text(cx + w / 2, y0 + 16, lab, size=11, color=INK, bold=True))
            p.append(text(cx + w / 2, y0 + 30, "2^-%s" % lab[-1] if False else "", size=9, color=MUTED))
        cx += w
    # рамка одиничного бюджету
    p.append(rect(x0, y0 - 6, width, 46, fill="none", stroke=INK, sw=1.4, rx=4))
    # позначки 0 і 1
    p.append(text(x0, y0 + 58, "0", size=11, color=MUTED))
    p.append(text(x0 + width, y0 + 58, "1", size=11, color=MUTED))
    return cx  # права межа використаного


def fig_kraft_sum():
    W, H = 720, 360
    p = []
    width = 430
    x0 = 95

    # ВЕРХ: набір довжин 1,2,3,3 → 1/2+1/4+1/8+1/8 = 1 (рівно влазить)
    p.append(text(x0, 70, "довжини 1, 2, 3, 3", size=13, color=INK, bold=True, anchor="start"))
    blocks_ok = [("ℓ=1", 1 / 2.0), ("ℓ=2", 1 / 4.0), ("ℓ=3", 1 / 8.0), ("ℓ=3", 1 / 8.0)]
    _budget_bar(x0, 88, width, blocks_ok, p, True)
    p.append(text(x0 + width + 18, 108, "Σ = 1  ✓", size=13, color=FIELD, bold=True, anchor="start"))
    p.append(text(x0, 150, "блоки точно заповнюють бюджет — префіксний код існує",
                  size=11, color=MUTED, anchor="start"))

    # НИЗ: набір довжин 1,2,2 → 1/2+1/4+1/4 = 1 ... але спроба 1,1,2 переповнює
    p.append(text(x0, 226, "довжини 1, 1, 2", size=13, color=INK, bold=True, anchor="start"))
    # 1/2 + 1/2 = 1 вже заповнюють, третій блок 1/4 не має куди стати → виліз
    blocks_bad = [("ℓ=1", 1 / 2.0), ("ℓ=1", 1 / 2.0)]
    _budget_bar(x0, 244, width, blocks_bad, p, False)
    # третій блок «вилазить» за межу — червоний, поза рамкою
    ow = (1 / 4.0) * width
    p.append(rect(x0 + width + 6, 244, ow, 34, fill="#fdecea", stroke=POS, sw=1.6, rx=3))
    p.append(text(x0 + width + 6 + ow / 2, 261, "ℓ=2", size=11, color=POS, bold=True))
    p.append(text(x0 + width + 6, 306, "Σ = 5/4 > 1  ✗", size=13, color=POS, bold=True, anchor="start"))
    p.append(text(x0, 322, "блок не має куди стати без накладання — код неможливий",
                  size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "kraft-sum.svg"), W, H, *p,
           title="Нерівність Крафта як заповнення одиничного бюджету")


# ── converse: маючи довжини з Σ ≤ 1, розставляємо слова на дереві жадібно ──────
# Ідея: сортуємо довжини за зростанням і кладемо кожне слово в найлівіший вільний
# вузол потрібної глибини; під ним викреслюємо піддерево. Поки Σ ≤ 1 — місце є.

def fig_converse():
    W, H = 660, 360
    p = []
    r = 12
    root = (330, 56)
    L1 = [(210, 126), (450, 126)]
    L2 = [(150, 200), (270, 200), (390, 200), (510, 200)]
    # ребра
    for (x, y) in L1:
        p.append(line(root[0], root[1] + r, x, y - r, color=MUTED, sw=1.4))
    pairs = [(L1[0], L2[0]), (L1[0], L2[1]), (L1[1], L2[2]), (L1[1], L2[3])]
    for (a, b) in pairs:
        p.append(line(a[0], a[1] + r, b[0], b[1] - r, color=MUTED, sw=1.4))

    p.append(text(255, 90, "0", size=11, color=NEG, bold=True))
    p.append(text(405, 90, "1", size=11, color=POS, bold=True))
    p.append(text(180, 162, "0", size=11, color=NEG, bold=True))
    p.append(text(420, 162, "1", size=11, color=POS, bold=True))

    # розставляємо довжини 1, 2, 2 (Σ = 1/2+1/4+1/4 = 1)
    # слово a = "0" (глибина 1, лівий вузол L1[0]) — викреслюємо ліве піддерево
    p.append(rect(120, 108, 130, 150, fill="#fdecea", stroke=POS, sw=1.5, rx=10))
    # слово b = "10" (L2[2]), c = "11" (L2[3])
    p.append(rect(368, 184, 44, 74, fill="#eaf7ee", stroke=FIELD, sw=1.5, rx=8))
    p.append(rect(488, 184, 44, 74, fill="#fff6e0", stroke="#b8860b", sw=1.5, rx=8))

    # вузли
    _dot(root[0], root[1], r, "#eaf2fb", INK, p)
    _dot(L1[0][0], L1[0][1], r, "#f3c6bf", POS, p)     # a = 0 (лист)
    _dot(L1[1][0], L1[1][1], r, "#eaf2fb", INK, p)     # внутрішній
    _dot(L2[0][0], L2[0][1], r, "#eef0f3", "#c8ced6", p)  # під a — викреслено
    _dot(L2[1][0], L2[1][1], r, "#eef0f3", "#c8ced6", p)  # під a — викреслено
    _dot(L2[2][0], L2[2][1], r, "#d7f0de", FIELD, p)   # b = 10
    _dot(L2[3][0], L2[3][1], r, "#fff0c2", "#b8860b", p)  # c = 11

    # підписи кодів
    p.append(text(L1[0][0] - 22, L1[0][1] + 4, "a=0", size=11, color=POS, bold=True, anchor="end"))
    p.append(text(L2[2][0], L2[2][1] + 30, "b=10", size=11, color=FIELD, bold=True))
    p.append(text(L2[3][0], L2[3][1] + 30, "c=11", size=11, color="#b8860b", bold=True))

    p.append(text(W / 2, H - 36,
                  "довжини 1, 2, 2 (Σ = 1): кладемо слова в найлівіші вільні вузли,",
                  size=11, color=MUTED))
    p.append(text(W / 2, H - 18,
                  "під кожним викреслюємо піддерево — місце завжди лишається",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "converse.svg"), W, H, *p,
           title="Обернене: з довжин будуємо префіксний код")


# ── mcmillan: степеневий трюк поширює межу на всі однозначні коди ──────────────
# Ідея: піднявши Σ 2^(−ℓ) до n-го степеня, дістаємо суму по всіх n-словах; для
# однозначного коду в кожній довжині L не більш ніж 2^L рядків, тож сума ≤ Lmax·n.
# Якщо S = Σ 2^(−ℓ) > 1, то S^n росте експоненційно — а праворуч лише лінійно.
# Суперечність → S ≤ 1 навіть без префіксності.

def fig_mcmillan():
    W, H = 680, 340
    p = []
    # ліворуч — ланцюг рівнянь
    bx = 40
    lines = [
        ("(Σ 2^(−ℓᵢ))ⁿ  =  Σ 2^(−(ℓ_{i1}+…+ℓ_{in}))", INK, True),
        ("                =  Σ_L  N_L · 2^(−L)", INK, False),
        ("де N_L — скільки n-слів мають сумарну довжину L", MUTED, False),
        ("однозначність ⇒  N_L ≤ 2^L  (різні слова — різні рядки)", FIELD, True),
        ("⇒  (Σ 2^(−ℓᵢ))ⁿ  ≤  Σ_L 1  ≤  n · ℓ_max", POS, True),
    ]
    y = 80
    for (s, col, bold) in lines:
        p.append(text(bx, y, s, size=12, color=col, anchor="start", bold=bold))
        y += 34

    # рамка-висновок
    box, bw, bh = textbox(bx + 250, 250, "Sⁿ ≤ n·ℓ_max  для всіх n\n⇒  S ≤ 1",
                          size=13, bold=True, fill="#eaf7ee", stroke=FIELD, sw=1.8,
                          color=INK, min_w=300)
    p.append(box)

    # праворуч — наочно: експонента Sⁿ vs лінія n·ℓmax
    ox, oy = 470, 300
    aw, ah = 180, 200
    p.append(arrow(ox, oy, ox, oy - ah - 6, color=INK, sw=1.4))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.4))
    p.append(text(ox + aw, oy + 18, "n", size=11, color=INK, italic=True))
    # лінійна межа праворуч (n·ℓmax)
    p.append(line(ox, oy - 20, ox + aw, oy - ah + 30, color=NEG, sw=1.8))
    p.append(text(ox + aw - 4, oy - ah + 24, "n·ℓ_max", size=10, color=NEG, anchor="end", bold=True))
    # експонента Sⁿ при S>1 (швидко вгору) — ламана, що пробиває лінію
    pts = [(0, 8), (0.35, 22), (0.6, 55), (0.8, 120), (0.95, 200)]
    px = [ox + t * aw for (t, v) in pts]
    py = [oy - v for (t, v) in pts]
    for i in range(len(pts) - 1):
        p.append(line(px[i], py[i], px[i + 1], py[i + 1], color=POS, sw=2.0))
    p.append(text(ox + aw * 0.62, oy - 150, "Sⁿ, S>1", size=10, color=POS, bold=True))
    p.append(text(ox + aw / 2, oy + 36, "якби S>1 — суперечність", size=10, color=MUTED))

    render(os.path.join(OUT, "mcmillan.svg"), W, H, *p,
           title="Макміллан: степеневий трюк — межа без префіксності")


if __name__ == "__main__":
    fig_tree_budget()
    fig_kraft_sum()
    fig_converse()
    fig_mcmillan()
    print("OK: figures written to", OUT)
