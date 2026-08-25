# -*- coding: utf-8 -*-
"""Фігури до статті «Аксіома вибору».
Запуск:  python figs.py   → пише SVG у ./img/
  socks-shoes      — черевики (є правило) проти шкарпеток (правила нема)
  choice-function  — функція вибору: по представнику з кожної множини
  three-faces      — рівносильність: вибір ⟺ повне впорядкування ⟺ лема Цорна
  independence     — ZF не доводить і не спростовує вибір (Гедель / Коен)
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


def dbl(x1, y1, x2, y2, color=INK, sw=2.2):
    """Двобічна стрілка ⟷ (маркер на обох кінцях)."""
    return ('<path d="M %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" '
            'stroke-width="%.1f" marker-start="url(#arrow)" '
            'marker-end="url(#arrow)"/>' % (x1, y1, x2, y2, color, sw))


# ── 1. Черевики (правило є) проти шкарпеток (правила нема) ────────────────────
def fig_socks_shoes():
    W, H = 1000, 500
    f = [text(W / 2, 34, "Вибір із пари: коли правило є, а коли ні", size=19, bold=True),
         text(W / 2, 56, "черевики різняться на лівий і правий — шкарпетки однакові між собою",
              size=12.5, color=MUTED, italic=True)]
    f.append(line(W / 2, 82, W / 2, 470, color="#d7dbe0", sw=1.4, dash="5,5"))

    rows = [172, 244, 316]

    # ── ліва панель: ЧЕРЕВИКИ — правило «бери лівий» ──
    f.append(text(258, 112, "Черевики: лівий ≠ правий", size=15, bold=True, color=FIELD))
    lc = 258
    for y in rows:
        # лівий (обраний) — зелений; правий — білий
        f.append(circle(lc - 46, y, 17, fill=GREENFILL, stroke=FIELD, sw=2.6))
        f.append(text(lc - 46, y + 5, "Л", size=14, bold=True, color=FIELD))
        f.append(circle(lc + 46, y, 17, fill=BG, stroke=INK, sw=1.6))
        f.append(text(lc + 46, y + 5, "П", size=14, color=INK))
    f.append(text(lc, rows[-1] + 44, "…", size=22, bold=True))
    f.append(fitbox(72, 400, 372, 66,
                    "Правило «бери лівий» вибирає з усіх\nпар заразом — аксіоми не треба.",
                    size=13, fill=GREENFILL, stroke=FIELD, color=INK))

    # ── права панель: ШКАРПЕТКИ — правила немає ──
    f.append(text(742, 112, "Шкарпетки: обидві однакові", size=15, bold=True, color=POS))
    rc = 742
    for y in rows:
        f.append(text(rc, y - 30, "котру?", size=11.5, italic=True, color=POS))
        f.append(circle(rc - 46, y, 17, fill=ROW, stroke=MUTED, sw=1.8))
        f.append(circle(rc + 46, y, 17, fill=ROW, stroke=MUTED, sw=1.8))
    f.append(text(rc, rows[-1] + 44, "…", size=22, bold=True))
    f.append(fitbox(556, 400, 372, 66,
                    "Спільного правила немає; для нескінченної\nкількості пар потрібна аксіома вибору.",
                    size=13, fill=REDFILL, stroke=POS, color=INK))

    render(os.path.join(IMG, "socks-shoes.svg"), W, H, *f)


# ── 2. Функція вибору: по представнику з кожної множини ───────────────────────
def fig_choice_function():
    W, H = 1000, 500
    f = [text(W / 2, 34, "Функція вибору", size=19, bold=True),
         text(W / 2, 56, "бере рівно по одному елементу з кожної непорожньої множини — усі заразом",
              size=12.5, color=MUTED, italic=True)]

    f.append(text(212, 104, "Родина множин", size=14, bold=True))
    f.append(text(566, 104, "Представники", size=14, bold=True, color=FIELD))

    rows = [162, 250, 338, 426]
    dots_x = [176, 212, 248, 284]
    chosen_idx = [1, 2, 0, 3]           # який елемент обрано в кожній множині
    for r, (y, ci) in enumerate(zip(rows, chosen_idx)):
        # «мішок» — множина Aᵣ
        f.append(rect(78, y - 29, 272, 58, fill=BG, stroke=LINE, sw=1.6, rx=28))
        f.append(text(110, y + 5, "A%d" % (r + 1), size=14, bold=True, color=MUTED))
        for j, dx in enumerate(dots_x):
            if j == ci:
                f.append(circle(dx, y, 8, fill=GREENFILL, stroke=FIELD, sw=2.6))
            else:
                f.append(circle(dx, y, 5, fill=INK, stroke=INK, sw=1))
        # стрілка до представника праворуч
        f.append(arrow(356, y, 542, y, color=FIELD, sw=1.8))
        f.append(circle(560, y, 13, fill=GREENFILL, stroke=FIELD, sw=2.4))
        f.append(text(586, y + 5, "f(%d)" % (r + 1), size=13, bold=True,
                      color=FIELD, anchor="start"))
    f.append(text(212, rows[-1] + 52, "…  (множин скільки завгодно)",
                  size=12, color=MUTED, italic=True))

    f.append(fitbox(690, 190, 288, 200,
                    "Уся вибірка — це один\nоб'єкт  f:  по представнику\nз кожної множини нараз.\n\n"
                    "Аксіома вибору: така  f\nіснує завжди — навіть коли\nправила вибору немає.",
                    size=13, fill=ROW, stroke=LINE, color=INK))

    render(os.path.join(IMG, "choice-function.svg"), W, H, *f)


# ── 3. Три рівносильні обличчя аксіоми вибору ─────────────────────────────────
def fig_three_faces():
    W, H = 1000, 470
    f = [text(W / 2, 34, "Три обличчя однієї сили", size=19, bold=True),
         text(W / 2, 56, "у теорії множин без вибору кожне з трьох тверджень тягне два інші",
              size=12.5, color=MUTED, italic=True)]

    top = (500, 152)
    bl = (256, 352)
    br = (744, 352)
    b_top, wt, ht = textbox(top[0], top[1],
                            "Аксіома вибору\nпо представнику з кожної\nнепорожньої множини",
                            size=13.5, bold=True, fill=GREENFILL, stroke=FIELD, color=INK, min_w=300)
    b_bl, wl, hl = textbox(bl[0], bl[1],
                           "Повне впорядкування\n(Цермело): будь-яку множину\nвишикувати з найменшим",
                           size=13.5, bold=True, fill=BLUEFILL, stroke=NEG, color=INK, min_w=300)
    b_br, wr, hr = textbox(br[0], br[1],
                           "Лема Цорна: ланцюги мають\nмежу — отже, є\nмаксимальний елемент",
                           size=13.5, bold=True, fill=ROW, stroke=LINE, color=INK, min_w=300)

    # двобічні стрілки по сторонах трикутника (з відступом від рамок)
    f.append(dbl(top[0] - 96, top[1] + ht / 2 + 4, bl[0] + 96, bl[1] - hl / 2 - 4, INK))
    f.append(dbl(top[0] + 96, top[1] + ht / 2 + 4, br[0] - 96, br[1] - hr / 2 - 4, INK))
    f.append(dbl(bl[0] + wl / 2 + 6, bl[1], br[0] - wr / 2 - 6, br[1], INK))

    # значок рівносильності на кожній стороні, осторонь ліній
    f.append(text(352, 250, "⟺", size=20, bold=True, color=FIELD))
    f.append(text(648, 250, "⟺", size=20, bold=True, color=FIELD))
    f.append(text(500, 340, "⟺", size=20, bold=True, color=FIELD))

    f.extend([b_top, b_bl, b_br])
    f.append(text(W / 2, 442, "прийняти одне з трьох означає прийняти всі три",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "three-faces.svg"), W, H, *f)


# ── 4. Незалежність вибору від ZF (Гедель / Коен) ─────────────────────────────
def fig_independence():
    W, H = 1000, 460
    f = [text(W / 2, 34, "Аксіома вибору незалежна від теорії множин", size=19, bold=True),
         text(W / 2, 56, "ZF не може її ні довести, ні спростувати — обидві добудови несуперечливі",
              size=12.5, color=MUTED, italic=True)]

    mid = (500, 150)
    b_mid, wm, hm = textbox(mid[0], mid[1],
                            "ZF\nзвичайна теорія множин\nбез аксіоми вибору",
                            size=13.5, bold=True, fill=ROW, stroke=LINE, color=INK, min_w=300)

    left = (260, 336)
    right = (740, 336)
    b_left, wlf, hlf = textbox(left[0], left[1],
                               "+ аксіома вибору  =  ZFC\nГедель (1938):\nсуперечності не вносить",
                               size=13, bold=True, fill=GREENFILL, stroke=FIELD, color=INK, min_w=306)
    b_right, wrt, hrt = textbox(right[0], right[1],
                                "+ заперечення вибору\nКоен (1963):\nтеж несуперечливо",
                                size=13, bold=True, fill=BLUEFILL, stroke=NEG, color=INK, min_w=306)

    f.append(arrow(mid[0] - 60, mid[1] + hm / 2 + 2, left[0] + 70, left[1] - hlf / 2 - 4, color=FIELD, sw=2.0))
    f.append(arrow(mid[0] + 60, mid[1] + hm / 2 + 2, right[0] - 70, right[1] - hrt / 2 - 4, color=NEG, sw=2.0))
    f.append(text(318, 250, "додаємо вибір", size=11.5, bold=True, color=FIELD, anchor="end"))
    f.append(text(682, 250, "додаємо заперечення", size=11.5, bold=True, color=NEG, anchor="start"))

    f.extend([b_mid, b_left, b_right])
    f.append(fitbox(150, 410, 700, 40,
                    "Обидві несуперечливі  ⇒  вибір НЕЗАЛЕЖНИЙ від ZF — як п'ятий постулат Евкліда від інших чотирьох.",
                    size=13, fill=BG, stroke=BG, color=INK))
    render(os.path.join(IMG, "independence.svg"), W, H, *f)


# ── 5. Спрямоване коло імплікацій (вставка про рівносильності) ────────────────
def fig_cycle_implications():
    W, H = 1040, 560
    f = [text(W / 2, 34, "Коло імплікацій: три твердження — одне", size=19, bold=True),
         text(W / 2, 56, "по стрілках з будь-якого дійдеш до кожного — отже, вони рівносильні",
              size=12.5, color=MUTED, italic=True)]

    T = (520, 172)
    BL = (252, 412)
    BR = (788, 412)
    b_t, wt, ht = textbox(T[0], T[1],
                          "Повне впорядкування\nкожну множину шикуємо\nз найменшим у кожній частині",
                          size=13.5, bold=True, fill=BLUEFILL, stroke=NEG, color=INK, min_w=300)
    b_bl, wl, hl = textbox(BL[0], BL[1],
                           "Аксіома вибору\nпо представнику\nз кожної множини",
                           size=13.5, bold=True, fill=GREENFILL, stroke=FIELD, color=INK, min_w=284)
    b_br, wr, hr = textbox(BR[0], BR[1],
                           "Лема Цорна\nланцюги мають межу\n⟹ є максимум",
                           size=13.5, bold=True, fill=ROW, stroke=LINE, color=INK, min_w=284)

    # спрямований цикл  T → BL → BR → T  (стрілки осторонь від рамок)
    f.append(arrow(T[0] - wt / 2 + 40, T[1] + ht / 2 + 4, BL[0], BL[1] - hl / 2 - 4, color=FIELD, sw=2.2))
    f.append(arrow(BL[0] + wl / 2 + 8, BL[1], BR[0] - wr / 2 - 8, BR[1], color=FIELD, sw=2.2))
    f.append(arrow(BR[0], BR[1] - hr / 2 - 4, T[0] + wt / 2 - 40, T[1] + ht / 2 + 4, color=FIELD, sw=2.2))

    # підписи ребер — ЗОВНІ трикутника, осторонь ліній
    f.append(text(300, 286, "бери найменший", size=12.5, bold=True, color=FIELD, anchor="end"))
    f.append(text(520, 472, "трансфінітне сходження", size=12.5, bold=True, color=FIELD))
    f.append(mtext(726, 268, ["порядок на", "початкових", "відрізках"],
                   size=12.5, bold=True, color=FIELD, anchor="start"))

    f.extend([b_t, b_bl, b_br])
    render(os.path.join(IMG, "cycle-implications.svg"), W, H, *f)


# ── 6. Лема Цорна добуває базис (вставка про рівносильності) ───────────────────
def fig_zorn_basis():
    W, H = 1040, 588
    f = [text(W / 2, 34, "Лема Цорна добуває базис", size=19, bold=True),
         text(W / 2, 56, "ланцюг лінійно незалежних множин росте включенням; його межа — об'єднання",
              size=12.5, color=MUTED, italic=True)]

    cx = 250
    rungs = [(506, "∅"), (426, "{v₁}"), (346, "{v₁, v₂}"), (266, "{v₁, v₂, v₃}")]
    for i, (y, lab) in enumerate(rungs):
        f.append(fitbox(cx - 118, y - 21, 236, 42, lab, size=15,
                        bold=True, fill=GREENFILL, stroke=FIELD, color=INK))
        if i > 0:
            py = rungs[i - 1][0]
            f.append(arrow(cx, py - 21, cx, y + 21, color=FIELD, sw=1.8))
            f.append(text(cx + 30, (py + y) / 2 + 5, "⊆", size=15, bold=True,
                          color=FIELD, anchor="start"))

    # об'єднання ланцюга — верхня межа
    f.append(arrow(cx, rungs[-1][0] - 21, cx, 214, color=NEG, sw=1.8))
    f.append(text(cx + 30, 232, "⋮", size=18, bold=True, color=MUTED, anchor="start"))
    b_u, wu, hu = textbox(cx, 168,
                          "⋃ ланцюга = верхня межа\n(залежність скінченна ⟹ теж незалежна)",
                          size=12.5, bold=True, fill=BLUEFILL, stroke=NEG, color=INK, min_w=330)
    f.append(b_u)

    # стрілка «лема Цорна» до висновку праворуч
    f.append(arrow(cx + wu / 2 + 6, 168, 560, 250, color=INK, sw=2.0))
    f.append(text((cx + wu / 2 + 566) / 2, 196, "лема Цорна", size=12, bold=True, color=INK))

    f.append(fitbox(566, 150, 430, 232,
                    "Є МАКСИМАЛЬНА незалежна множина M.\n\n"
                    "Якби вона не породжувала весь V,\n"
                    "до неї можна було б додати ще вектор —\n"
                    "і вона лишилася б незалежною,\n"
                    "тобто не була б максимальна.\n\n"
                    "Отже M породжує V і незалежна:\n"
                    "M — це БАЗИС.",
                    size=13, fill=BG, stroke=LINE, color=INK))

    f.append(fitbox(90, 520, 860, 46,
                    "Той самий рух дає максимальний ідеал у кільці — з умовою «1 ∉ I» замість «немає нової залежності».",
                    size=13, fill=ROW, stroke=LINE, color=INK))

    render(os.path.join(IMG, "zorn-basis.svg"), W, H, *f)


# ── 7. Класи еквівалентності на [0,1) і вибір представників → V ────────────────
def fig_vitali_classes():
    PURPLE, PURPLEFILL = "#7b4fbf", "#f3eafd"
    ORANGE, ORANGEFILL = "#c77a1f", "#fdf0e6"
    W, H = 1000, 540
    f = [text(W / 2, 34, "Розбиття [0, 1) на класи еквівалентності", size=19, bold=True),
         text(W / 2, 56, "x ~ y  ⟺  x − y раціональне;  з кожного класу вибір бере одного представника → V",
              size=12.5, color=MUTED, italic=True)]

    x0, x1 = 168, 866
    rows = [136, 210, 284, 358]
    labels = ["клас C₁", "клас C₂", "клас C₃", "клас C₄"]
    fills = [BLUEFILL, GREENFILL, ORANGEFILL, PURPLEFILL]
    strokes = [NEG, FIELD, ORANGE, PURPLE]
    dotpos = [
        [0.06, 0.19, 0.31, 0.47, 0.58, 0.73, 0.88],
        [0.10, 0.23, 0.38, 0.51, 0.66, 0.79, 0.92],
        [0.04, 0.17, 0.29, 0.44, 0.61, 0.75, 0.85],
        [0.12, 0.25, 0.35, 0.49, 0.63, 0.77, 0.90],
    ]
    chosen = [3, 1, 4, 5]

    f.append(line(x0, 116, x0, 382, color="#d7dbe0", sw=1.4, dash="4,5"))
    f.append(line(x1, 116, x1, 382, color="#d7dbe0", sw=1.4, dash="4,5"))
    f.append(text(x0, 104, "0", size=12, color=MUTED))
    f.append(text(x1, 104, "1", size=12, color=MUTED))

    for r, y in enumerate(rows):
        f.append(text(96, y + 5, labels[r], size=13, bold=True, color=strokes[r]))
        f.append(line(x0, y, x1, y, color="#e4e7eb", sw=1.4))
        for j, p in enumerate(dotpos[r]):
            cx = x0 + p * (x1 - x0)
            if j == chosen[r]:
                f.append(circle(cx, y, 12.5, fill="none", stroke=FIELD, sw=3.0))
                f.append(circle(cx, y, 5.5, fill=strokes[r], stroke=strokes[r], sw=1))
            else:
                f.append(circle(cx, y, 5.5, fill=fills[r], stroke=strokes[r], sw=1.8))

    f.append(text(W / 2, 406, "… класів незліченно багато — усіх не намалювати",
                  size=12.5, color=MUTED, italic=True))
    b, w, h = textbox(W / 2, 470, "V  =  { по одному представнику (обведеному) з кожного класу }",
                      size=14, bold=True, fill=GREENFILL, stroke=FIELD, color=INK, min_w=560)
    f.append(b)
    render(os.path.join(IMG, "vitali-classes.svg"), W, H, *f)


# ── 8. Суперечність: сума копій дає 0 або ∞, а треба 1 ─────────────────────────
def fig_vitali_contradiction():
    W, H = 1000, 500
    f = [text(W / 2, 34, "Чому V неможливо приписати довжину", size=19, bold=True),
         text(W / 2, 56, "зсуви V на всі раціональні q заповнюють [0,1) зліченною кількістю неперетинних копій довжини c",
              size=12, color=MUTED, italic=True)]

    x0, x1 = 92, 908
    ytop, hbar = 92, 40
    labels = ["V⊕q₀", "V⊕q₁", "V⊕q₂", "V⊕q₃", "V⊕q₄", "V⊕q₅", "V⊕q₆", "V⊕q₇"]
    fills = [BLUEFILL, GREENFILL]
    n = len(labels)
    seg = (x1 - x0 - 46) / (n + 1)
    for i, lb in enumerate(labels):
        sx = x0 + i * seg
        f.append(rect(sx, ytop, seg - 3, hbar, fill=fills[i % 2], stroke=LINE, sw=1.3, rx=3))
        f.append(text(sx + (seg - 3) / 2, ytop + hbar / 2 + 4, lb, size=10.5, color=INK))
    f.append(text(x0 + n * seg + 22, ytop + hbar / 2 + 5, "…", size=22, bold=True))
    f.append(text(x0 - 4, ytop - 8, "0", size=11, color=MUTED))
    f.append(text(x1 + 2, ytop - 8, "1", size=11, color=MUTED))
    f.append(text(W / 2, ytop + hbar + 26,
                  "[0, 1) = ⊔ (V ⊕ q),   q ∈ ℚ ∩ [0,1)   —   кожна копія завдовжки  c = m(V)",
                  size=13, italic=True, color=INK))

    f.append(text(W / 2, 216, "1 = m([0,1)) = Σ m(V ⊕ q) = c + c + c + …",
                  size=17, bold=True, color=INK))

    b1, w1, h1 = textbox(292, 306, "c = 0\n0 + 0 + 0 + …  =  0",
                         size=14, bold=True, fill=REDFILL, stroke=POS, color=INK, min_w=300)
    b2, w2, h2 = textbox(708, 306, "c > 0\nc + c + c + …  =  ∞",
                         size=14, bold=True, fill=REDFILL, stroke=POS, color=INK, min_w=300)
    f.extend([b1, b2])
    f.append(text(292, 356, "✗  не 1", size=13, bold=True, color=POS))
    f.append(text(708, 356, "✗  не 1", size=13, bold=True, color=POS))

    b3, w3, h3 = textbox(W / 2, 430, "а треба рівно 1  →  такого c немає  →  V невимірна",
                         size=14.5, bold=True, fill=GREENFILL, stroke=FIELD, color=INK, min_w=520)
    f.append(b3)
    render(os.path.join(IMG, "vitali-contradiction.svg"), W, H, *f)


# ── 9. Банах–Тарський: самоподібність вільної групи → подвоєна куля ────────────
def fig_banach_tarski():
    PURPLE, PURPLEFILL = "#7b4fbf", "#f3eafd"
    ORANGE, ORANGEFILL = "#c77a1f", "#fdf0e6"
    W, H = 1120, 580
    f = [text(W / 2, 34, "Подвоєння: з будови вільної групи обертань — до кулі", size=19, bold=True),
         text(W / 2, 56, "чотири шматки групи, два крутнуті обертаннями, дають дві повні копії — і так само куля",
              size=12, color=MUTED, italic=True)]
    f.append(line(596, 82, 596, 548, color="#d7dbe0", sw=1.5, dash="5,6"))

    f.append(text(300, 104, "Вільна група F₂ розбита за першою літерою", size=13.5, bold=True))
    ex, ey = 300, 250
    sat = [((300, 168), "S(b)", GREENFILL, FIELD),
           ((300, 332), "S(b⁻¹)", PURPLEFILL, PURPLE),
           ((452, 250), "S(a)", BLUEFILL, NEG),
           ((148, 250), "S(a⁻¹)", ORANGEFILL, ORANGE)]
    for (sx, sy), lb, fl, st in sat:
        f.append(line(ex, ey, sx, sy, color="#c7ccd2", sw=1.6))
    for (sx, sy), lb, fl, st in sat:
        b, w, h = textbox(sx, sy, lb, size=13, bold=True, fill=fl, stroke=st, color=INK, min_w=96)
        f.append(b)
    f.append(circle(ex, ey, 22, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(ex, ey + 5, "e", size=15, bold=True, italic=True))

    f.append(fitbox(64, 410, 480, 122,
                    "a · S(a⁻¹)  =  усе, крім S(a)   (початкова a⁻¹ гаситься)\n"
                    "S(a) ∪ a·S(a⁻¹) = F₂ ;   S(b) ∪ b·S(b⁻¹) = F₂\n"
                    "чотири шматки → дві копії групи, самі обертання",
                    size=13, fill="#fbfcfd", stroke=LINE, color=INK))

    f.append(text(858, 104, "Та сама самоподібність на кулі", size=13.5, bold=True))
    f.append(circle(858, 214, 66, fill=BLUEFILL, stroke=NEG, sw=2.2))
    f.append(text(858, 208, "куля", size=14, bold=True, color=INK))
    f.append(text(858, 228, "об'єм 1", size=12, color=MUTED))

    f.append(arrow(858, 288, 858, 356, color=LINE, sw=2.0))
    f.append(text(1016, 320, "5 невимірних", size=11.5, bold=True, color=POS))
    f.append(text(1016, 336, "шматків", size=11.5, bold=True, color=POS))

    f.append(circle(790, 440, 46, fill=BLUEFILL, stroke=NEG, sw=2.0))
    f.append(text(790, 445, "куля", size=12.5, bold=True))
    f.append(circle(926, 440, 46, fill=BLUEFILL, stroke=NEG, sw=2.0))
    f.append(text(926, 445, "куля", size=12.5, bold=True))
    f.append(text(858, 446, "+", size=20, bold=True, color=INK))

    f.append(fitbox(648, 506, 420, 46,
                    "шматки невимірні → об'єм не визначений, зберігати нема чого",
                    size=12.5, fill="#fbfcfd", stroke=LINE, color=INK))
    render(os.path.join(IMG, "banach-tarski.svg"), W, H, *f)


if __name__ == "__main__":
    fig_socks_shoes()
    fig_choice_function()
    fig_three_faces()
    fig_independence()
    fig_cycle_implications()
    fig_zorn_basis()
    fig_vitali_classes()
    fig_vitali_contradiction()
    fig_banach_tarski()
    print("OK: socks-shoes, choice-function, three-faces, independence, "
          "cycle-implications, zorn-basis, vitali-classes, vitali-contradiction, "
          "banach-tarski ->", IMG)
