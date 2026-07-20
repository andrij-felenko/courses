# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Регулярні мови».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

RED   = "#c0392b"   # вхід «1» / акцент
BLUE  = "#2457d6"   # вхід «0»
GREEN = "#27ae60"   # приймальний стан / «те саме»
STATE = "#eef2fb"   # заливка звичайного стану
ACC   = "#eafaf0"   # заливка приймального стану


def arrow_c(x1, y1, x2, y2, color, sw=2.2):
    mid = "ar_%s" % color.lstrip("#")
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#%s)"/>' % (x1, y1, x2, y2, color, sw, mid))


def curve(d, color, sw=2.2):
    mid = "ar_%s" % color.lstrip("#")
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'marker-end="url(#%s)"/>' % (d, color, sw, mid))


def defs_arrows(*colors):
    out = ["<defs>"]
    for c in colors:
        mid = "ar_%s" % c.lstrip("#")
        out.append('<marker id="%s" viewBox="0 0 10 10" refX="8.4" refY="5" '
                   'markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse">'
                   '<path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>' % (mid, c))
    out.append("</defs>")
    return "".join(out)


def state(cx, cy, label, sub=None, accept=False, r=30):
    col = GREEN if accept else INK
    fill = ACC if accept else STATE
    out = circle(cx, cy, r, fill=fill, stroke=col, sw=2.3)
    if accept:
        out += circle(cx, cy, r - 5, fill="none", stroke=col, sw=2.0)
    out += text(cx, cy + (0 if sub else 5), label, size=15, color=INK, bold=True)
    if sub:
        out += text(cx, cy + 16, sub, size=10, color=MUTED)
    return out


def loop_top(cx, cy, label, color, r=30, lift=40):
    x1, x2 = cx - 11, cx + 11
    y = cy - r
    d = "M %.1f,%.1f C %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        x1, y, x1 - 13, y - lift, x2 + 13, y - lift, x2, y)
    out = curve(d, color)
    out += text(cx, y - lift - 6, label, size=13, color=color, bold=True)
    return out


def start_mark(cx, cy, r=30):
    out = arrow_c(cx - r - 34, cy, cx - r - 4, cy, INK, sw=2.2)
    out += text(cx - r - 38, cy - 8, "старт", size=10.5, color=MUTED, anchor="end")
    return out


# ── Фігура 1: одна мова — три рівносильні описи ──────────────────────────────
# L = «двійкові слова з парним числом одиниць». Три картки-обличчя: регулярний
# вираз, скінченний автомат (парн/непарн), регулярна граматика. Внизу — теза:
# усі троє задають РІВНО ту саму множину слів — це й є «регулярна».
def fig_three_faces():
    W, H = 900, 470
    P = [defs_arrows(RED, BLUE, INK, GREEN)]
    P.append(text(W / 2, 32, "Одна мова — три рівносильні описи", size=17, bold=True))
    P.append(text(W / 2, 55, "L = «двійкові слова, у яких парне число одиниць»   (Σ = {0, 1})",
                  size=12.5, color=MUTED))
    cx = [30, 320, 610]
    cw, cy0, ch = 260, 82, 300
    heads = ["1 · Регулярний вираз", "2 · Скінченний автомат", "3 · Регулярна граматика"]
    cols = [BLUE, INK, RED]
    for x, hd, col in zip(cx, heads, cols):
        P.append(rect(x, cy0, cw, ch, fill="#fbfcfe", stroke=col, sw=1.8, rx=10))
        P.append(text(x + cw / 2, cy0 + 26, hd, size=12.5, color=col, bold=True))

    # Картка 1: регулярний вираз
    P.append(rect(cx[0] + 22, cy0 + 92, cw - 44, 46, fill="#eef4ff", stroke=BLUE, sw=1.6, rx=8))
    P.append(text(cx[0] + cw / 2, cy0 + 121, "0*(10*10*)*", size=19, bold=True))
    P.append(text(cx[0] + cw / 2, cy0 + 176, "три операції: вибір | ,", size=11.5, color=MUTED))
    P.append(text(cx[0] + cw / 2, cy0 + 194, "склейка · , зірка *", size=11.5, color=MUTED))
    P.append(text(cx[0] + cw / 2, cy0 + 232, "одиниці — тільки парами", size=11.5, color=INK))
    P.append(text(cx[0] + cw / 2, cy0 + 268, "коротка формула-правило", size=11, color=MUTED, italic=True))

    # Картка 2: автомат — 2 стани (парн/непарн)
    ax, bx, ay = cx[1] + 92, cx[1] + 198, cy0 + 150
    P.append(loop_top(ax, ay, "0", BLUE, r=27, lift=30))
    P.append(loop_top(bx, ay, "0", BLUE, r=27, lift=30))
    P.append(curve("M %.1f,%.1f Q %.1f,%.1f %.1f,%.1f" % (ax + 27, ay - 8, (ax + bx) / 2, ay - 34, bx - 27, ay - 8), RED))
    P.append(text((ax + bx) / 2, ay - 40, "1", size=12.5, color=RED, bold=True))
    P.append(curve("M %.1f,%.1f Q %.1f,%.1f %.1f,%.1f" % (bx - 27, ay + 8, (ax + bx) / 2, ay + 34, ax + 27, ay + 8), RED))
    P.append(text((ax + bx) / 2, ay + 48, "1", size=12.5, color=RED, bold=True))
    P.append(state(ax, ay, "парн", accept=True, r=27))
    P.append(state(bx, ay, "непарн", r=27))
    P.append(arrow_c(ax - 27 - 26, ay, ax - 27 - 3, ay, INK, sw=2))
    P.append(text(ax - 27 - 28, ay - 8, "старт", size=10, color=MUTED, anchor="end"))
    P.append(text(cx[1] + cw / 2, cy0 + 232, "перемикач: «1» міняє парність", size=11, color=INK))
    P.append(text(cx[1] + cw / 2, cy0 + 268, "машина, що читає й приймає", size=11, color=MUTED, italic=True))

    # Картка 3: граматика
    gx = cx[2] + 30
    P.append(text(gx, cy0 + 108, "П → 0 П", size=15, anchor="start", bold=True))
    P.append(text(gx + 96, cy0 + 108, "| 1 Н | ε", size=15, anchor="start"))
    P.append(text(gx, cy0 + 138, "Н → 0 Н", size=15, anchor="start", bold=True))
    P.append(text(gx + 96, cy0 + 138, "| 1 П", size=15, anchor="start"))
    P.append(text(cx[2] + cw / 2, cy0 + 176, "П — парно (старт, приймає)", size=10.5, color=MUTED))
    P.append(text(cx[2] + cw / 2, cy0 + 194, "Н — непарно", size=10.5, color=MUTED))
    P.append(text(cx[2] + cw / 2, cy0 + 232, "правила, що ПОРОДЖУЮТЬ слова", size=11, color=INK))
    P.append(text(cx[2] + cw / 2, cy0 + 268, "по одному символу зліва", size=11, color=MUTED, italic=True))

    # нижня теза
    body, w_, h_ = textbox(W / 2, 445, "Три різні описи → РІВНО та сама множина слів. Це і є «регулярна» мова.",
                           size=13, fill=ACC, stroke=GREEN, color=INK, bold=True)
    P.append(body)
    render("img/three-faces.svg", W, H, *P)


# ── Фігура 2: ієрархія Хомського (регулярні — найтісніше ядро) ───────────────
# Вкладені рамки: що ширша — то більше пам'яті в машини. Регулярні (Тип 3,
# скінченний автомат) — усередині; кожен наступний щабель додає пам'ять і нові
# мови (приклад, який живе вже поза меншим кільцем).
def fig_hierarchy():
    W, H = 820, 540
    P = [defs_arrows(INK, GREEN)]
    P.append(text(W / 2, 32, "Ієрархія Хомського: регулярні мови — найтісніше ядро", size=16, bold=True))
    rings = [
        (30,  58, 760, 452, "#f3f4f6", "Тип 0 · Рекурсивно-зліченні — Машина Тюринга (необмежена пам'ять)", INK),
        (95,  108, 630, 372, "#eef2fb", "Тип 1 · Контекстно-залежні — лінійно-обмежений автомат", INK),
        (160, 158, 500, 292, "#eaf1ff", "Тип 2 · Контекстно-вільні — Магазинний автомат (стек)", BLUE),
        (240, 214, 340, 196, "#eafaf0", "", GREEN),
    ]
    for x, y, w, h, fill, label, col in rings:
        P.append(rect(x, y, w, h, fill=fill, stroke=col, sw=2, rx=14))
        if label:
            P.append(text(x + 18, y + 22, label, size=12, color=col, anchor="start", bold=True))
    # приклади-мешканці кожного кільця (те, що живе поза меншим)
    P.append(text(64, 92, "напр.: «чи зупиниться програма» — розв'язне лише тут", size=10.5, color=MUTED, anchor="start"))
    P.append(text(128, 142, "напр.: aⁿbⁿcⁿ", size=10.5, color=MUTED, anchor="start"))
    P.append(text(190, 192, "напр.: aⁿbⁿ, збалансовані дужки, вкладеність", size=10.5, color=BLUE, anchor="start"))
    # ядро — регулярні
    P.append(text(W / 2, 250, "Тип 3 · РЕГУЛЯРНІ", size=15, color=GREEN, bold=True))
    P.append(text(W / 2, 275, "Скінченний автомат", size=12, color=INK))
    P.append(text(W / 2, 298, "пам'ять = скінченний стан", size=11, color=MUTED))
    P.append(rect(300, 316, 220, 76, fill="#ffffff", stroke=GREEN, sw=1.5, rx=8))
    P.append(text(W / 2, 338, "приклади:", size=10.5, color=MUTED))
    P.append(text(W / 2, 358, "a*b*  ·  парне число одиниць", size=12, bold=True))
    P.append(text(W / 2, 378, "«містить 101»  ·  regex", size=11.5, color=INK))
    # шкала пам'яті
    P.append(arrow_c(70, 512, 750, 512, INK, sw=2))
    P.append(text(70, 528, "менше пам'яті", size=11, color=MUTED, anchor="start"))
    P.append(text(750, 528, "більше пам'яті (аж до необмеженої)", size=11, color=MUTED, anchor="end"))
    render("img/hierarchy.svg", W, H, *P)


# ── Фігура 3: чому 0ⁿ1ⁿ не регулярна (принцип шухляд → цикл → накачування) ────
# Довгий блок нулів мусить провести пробіг через ЦИКЛ (станів скінченно). Цикл
# можна пройти будь-скільки разів — тож машина не розрізняє довжини нулів і
# приймає слова з нерівним числом 0 і 1. Розклад слова: x · y · z.
def fig_pumping():
    W, H = 880, 420
    P = [defs_arrows(RED, BLUE, INK, GREEN)]
    P.append(text(W / 2, 32, "Чому 0ⁿ1ⁿ не під силу скінченному автомату", size=16, bold=True))
    P.append(text(W / 2, 55, "станів скінченно (k), а нулів у 0ᵏ⁺¹ більше → якийсь стан мусить повторитися",
                  size=12, color=MUTED))
    y = 150
    q0, S, acc = 150, 420, 700
    # старт → q0 → S → accept
    P.append(start_mark(q0, y, r=30))
    P.append(arrow_c(q0 + 32, y, S - 32, y, BLUE, sw=2.4))
    P.append(text((q0 + S) / 2, y - 14, "x  (кілька 0)", size=12.5, color=BLUE, bold=True))
    P.append(arrow_c(S + 32, y, acc - 32, y, INK, sw=2.4))
    P.append(text((S + acc) / 2, y - 14, "z  (решта: 0…0 далі 1…1)", size=12, color=INK, bold=True))
    # цикл на S
    P.append(loop_top(S, y, "y  (цикл із самих 0)", BLUE, r=30, lift=54))
    P.append(state(q0, y, "q₀", r=30))
    P.append(state(S, y, "S", "повтор", r=30))
    P.append(state(acc, y, "прийом", accept=True, r=34))
    # ключова теза
    P.append(text(W / 2, 250, "Цикл y можна пройти 0, 1, 2, … разів — машина щоразу приймає.", size=12.5, color=INK, bold=True))
    P.append(fitbox(150, 272, 580, 96,
        "Отже приймається не лише 0ⁿ1ⁿ, а й слова, де нулів більше чи менше за одиниці\n"
        "(накачали або прибрали цикл). Але такі слова НЕ належать мові {0ⁿ1ⁿ}.\n"
        "Суперечність → жоден скінченний автомат мови не розпізнає → вона не регулярна.",
        size=12, fill="#fff8f7", stroke=RED, color=INK))
    render("img/pumping.svg", W, H, *P)


# ── Фігури до вставки proj-product-construction ──────────────────────────────
# Наскрізний приклад: A = «закінчується на .log» (стани 0..4 — довжина збігу),
# B = «непорожнє й не починається з крапки» (поч / ок / мертв).

BST = ["поч", "ок", "мертв"]        # стани B у сталому порядку


def node(cx, cy, label, accept=False, r=22, fs=13, col=None):
    """Кружечок-стан із написом (шрифт задається — на відміну від state())."""
    c = col if col else (GREEN if accept else INK)
    out = circle(cx, cy, r, fill=(ACC if accept else STATE), stroke=c, sw=2.2)
    if accept:
        out += circle(cx, cy, r - 4, fill="none", stroke=c, sw=1.6)
    out += text(cx, cy + fs * 0.35, label, size=fs, color=INK, bold=True)
    return out


# ── Фігура 4: пробіг у ногу — стан добутку є ПАРОЮ станів ────────────────────
# Два слова, що різняться ЛИШЕ першим символом, тож видно рівно той внесок,
# який робить другий автомат. Пара «де перший, де другий» — і є нова машина.
def fig_lockstep():
    W, H = 960, 600
    P = [defs_arrows(RED, BLUE, INK, GREEN)]
    P.append(text(W / 2, 30, "Стан добутку — це ПАРА станів", size=17, bold=True))
    P.append(text(W / 2, 54, "два автомати читають ОДНЕ слово в ногу; слова різняться лише ПЕРШИМ символом",
                  size=12, color=MUTED))

    x0, colw = 175, 110
    def col(i):
        return x0 + i * colw

    def panel(py, word, ok):
        out = []
        edge = GREEN if ok else RED
        out.append(rect(24, py, W - 48, 215, fill="#fbfcfe", stroke=edge, sw=1.8, rx=10))
        out.append(text(46, py + 24, "слово:  " + word, size=13, color=INK, anchor="start", bold=True))
        verdict = ("A: так  ·  B: так   →   ПРИЙНЯТО" if ok else "A: так  ·  B: НІ   →   відхилено")
        out.append(text(W - 46, py + 24, verdict, size=13, color=edge, anchor="end", bold=True))

        # прогін обома автоматами
        pa, qb = [0], ["поч"]
        for ch in word:
            i = pa[-1]
            cand = ".log"[:i] + ch
            k = 0
            for k2 in range(min(len(cand), 4), 0, -1):
                if cand.endswith(".log"[:k2]):
                    k = k2
                    break
            pa.append(k)
            qb.append(qb[-1] if qb[-1] != "поч" else ("мертв" if ch == "." else "ок"))

        ya, yb, yp = py + 84, py + 140, py + 192
        out.append(text(100, ya + 5, "A", size=14, color=BLUE, anchor="end", bold=True))
        out.append(text(100, yb + 5, "B", size=14, color=RED, anchor="end", bold=True))
        out.append(text(100, yp + 5, "пара", size=12, color=INK, anchor="end", bold=True))
        out.append(text(col(0), py + 44, "старт", size=11, color=MUTED))

        for i in range(len(word) + 1):
            cx = col(i)
            if i > 0:
                out.append(text(cx - colw / 2, py + 44, "«%s»" % word[i - 1], size=13, color=INK, bold=True))
                out.append(arrow_c(col(i - 1) + 25, ya, cx - 25, ya, BLUE, sw=2))
                dead = qb[i] == "мертв"
                out.append(arrow_c(col(i - 1) + 27, yb, cx - 27, yb, RED if dead else GREEN, sw=2))
            out.append(node(cx, ya, str(pa[i]), accept=(pa[i] == 4 and i == len(word)), r=22, fs=14))
            out.append(node(cx, yb, qb[i], accept=(qb[i] == "ок" and i == len(word)), r=24, fs=10.5,
                            col=(RED if qb[i] == "мертв" else None)))
            body, _, _ = textbox(cx, yp, "(%s, %s)" % (pa[i], qb[i]), size=11,
                                 fill=(ACC if (pa[i] == 4 and qb[i] == "ок") else "#ffffff"),
                                 stroke=(GREEN if (pa[i] == 4 and qb[i] == "ок") else MUTED), sw=1.4, pad=7)
            out.append(body)
        return out

    P += panel(78, "_x.log", True)
    P += panel(308, ".x.log", False)
    P.append(fitbox(150, 538, 660, 46,
                    "Нова машина не робить НІЧОГО, крім як тримає обидва стани нарізно.\n"
                    "Приймає, коли в кінці приймають ОБИДВА — це й є перетин мов.",
                    size=12.5, fill=ACC, stroke=GREEN, color=INK, bold=True))
    render("img/lockstep.svg", W, H, *P)


# ── Фігура 5: решітка пар — скільки з них справді досяжні ────────────────────
# 5 станів A × 3 стани B = 15 клітин, але 4 недосяжні: «поч» живе лише до
# першого символу, коли A ще в 0. Лінива побудова їх навіть не створює.
def fig_grid():
    W, H = 780, 500
    P = [defs_arrows(INK, GREEN, RED)]
    P.append(text(W / 2, 30, "Решітка пар: 15 клітин, досяжних 11", size=17, bold=True))
    P.append(text(W / 2, 54, "рядок — стан B, стовпчик — стан A; клітина — стан добутку",
                  size=12, color=MUTED))

    gx, gy, cw, ch = 190, 116, 108, 70
    P.append(text(gx + 2.5 * cw, 96, "A — «закінчується на .log»:  довжина вже зібраного збігу",
                  size=11.5, color=BLUE))
    for j, a in enumerate(range(5)):
        P.append(text(gx + j * cw + cw / 2, gy - 6, str(a), size=14, color=BLUE, bold=True))
    for i, b in enumerate(BST):
        P.append(text(gx - 14, gy + i * ch + ch / 2 + 5, b, size=12.5, color=RED, anchor="end", bold=True))
    P.append(text(28, gy + 1.5 * ch - 14, "B —", size=11.5, color=RED, anchor="start", bold=True))
    P.append(text(28, gy + 1.5 * ch + 4, "«не з", size=11.5, color=RED, anchor="start"))
    P.append(text(28, gy + 1.5 * ch + 22, "крапки»", size=11.5, color=RED, anchor="start"))

    for i, b in enumerate(BST):
        for j in range(5):
            x, y = gx + j * cw, gy + i * ch
            reach = not (b == "поч" and j > 0)
            acc = (j == 4 and b == "ок")
            start = (j == 0 and b == "поч")
            fill = ACC if acc else ("#f0f1f3" if not reach else "#ffffff")
            stroke = GREEN if acc else (BLUE if start else (MUTED if reach else "#c9ccd1"))
            P.append(rect(x + 4, y + 4, cw - 8, ch - 8, fill=fill, stroke=stroke,
                          sw=2.2 if (acc or start) else 1.3, rx=7))
            P.append(text(x + cw / 2, y + ch / 2 - 4, "(%d, %s)" % (j, b), size=11.5,
                          color=(MUTED if not reach else INK), bold=reach))
            if not reach:
                P.append(text(x + cw / 2, y + ch / 2 + 16, "недосяжна", size=10, color=MUTED, italic=True))
            elif acc:
                P.append(text(x + cw / 2, y + ch / 2 + 16, "ПРИЙМАЄ", size=10, color=GREEN, bold=True))
            elif start:
                P.append(text(x + cw / 2, y + ch / 2 + 16, "старт", size=10, color=BLUE, bold=True))

    P.append(fitbox(80, 356, 620, 110,
                    "Недосяжні — рівно ті чотири пари, що самі собі суперечать: B ще «поч» (не прочитано\n"
                    "жодного символу), а A вже зібрав частину збігу. Так не буває — «поч» живе лише до\n"
                    "першого символу, коли A конче в 0. Лінива побудова (обхід від стартової пари) таких\n"
                    "клітин навіть не створює: 11 замість 15. Приймальна клітина — рівно одна.",
                    size=12, fill="#fbfcfe", stroke=INK, color=INK))
    render("img/grid.svg", W, H, *P)


# ── Фігура 6: одна побудова — чотири булеві операції ─────────────────────────
# Змінюється РІВНО предикат прийняття; пари, переходи й обхід — ті самі.
def fig_four_ops():
    W, H = 940, 450
    P = [defs_arrows(INK, GREEN)]
    P.append(text(W / 2, 30, "Одна побудова — чотири операції", size=17, bold=True))
    P.append(text(W / 2, 54, "решітка й переходи ті самі; змінюється РІВНО предикат прийняття",
                  size=12, color=MUTED))

    ops = [
        ("L₁ ∩ L₂", "приймають ОБИДВА", lambda x, y: x and y),
        ("L₁ ∪ L₂", "приймає БОДАЙ ОДИН", lambda x, y: x or y),
        ("L₁ ∖ L₂", "перший так, другий ні", lambda x, y: x and not y),
        ("L₁ ⊕ L₂", "рівно ОДИН із двох", lambda x, y: x != y),
    ]
    pw, gap = 214, 26
    x0 = (W - (4 * pw + 3 * gap)) / 2
    cw, ch = 36, 27
    for k, (name, rule, op) in enumerate(ops):
        px = x0 + k * (pw + gap)
        P.append(rect(px, 78, pw, 220, fill="#fbfcfe", stroke=INK, sw=1.6, rx=9))
        P.append(text(px + pw / 2, 104, name, size=16, bold=True))
        P.append(text(px + pw / 2, 126, rule, size=10.5, color=MUTED))
        ox, oy = px + (pw - 5 * cw) / 2, 142
        cnt = 0
        for i, b in enumerate(BST):
            for j in range(5):
                reach = not (b == "поч" and j > 0)
                acc = op(j == 4, b == "ок") and reach
                if acc:
                    cnt += 1
                P.append(rect(ox + j * cw + 2, oy + i * ch + 2, cw - 4, ch - 4,
                              fill=(ACC if acc else ("#f0f1f3" if not reach else "#ffffff")),
                              stroke=(GREEN if acc else "#c9ccd1"), sw=1.8 if acc else 1.1, rx=4))
        P.append(text(px + pw / 2, oy + 3 * ch + 26, "приймальних пар: %d" % cnt, size=11.5, color=GREEN, bold=True))
        P.append(text(px + pw / 2, oy + 3 * ch + 46, "accept = %s" % ["x and y", "x or y", "x and not y", "x != y"][k],
                      size=11, color=INK))

    P.append(fitbox(90, 330, 760, 92,
                    "Зелене — приймальні пари (сіре — недосяжні). Пари станів, переходи й обхід — однакові\n"
                    "в усіх чотирьох; різниця вміщається в один рядок. Звідси й безкоштовні висновки:\n"
                    "порожній L₁ ∖ L₂  ⟺  L₁ ⊆ L₂ ;   порожній L₁ ⊕ L₂  ⟺  мови рівні.",
                    size=12.5, fill=ACC, stroke=GREEN, color=INK))
    render("img/four-ops.svg", W, H, *P)


# ── Фігури до вставки hist-chomsky-hierarchy ─────────────────────────────────
# 1) Дві статті — дві різні драбини: що було 1956-го й що з'явилося аж 1959-го.
# 2) Родовід правил-продукцій: Тип 3 — точка зустрічі гілки правил і гілки машин.

def fig_hist_two_papers():
    W, H = 980, 600
    P = [defs_arrows(INK, RED)]
    P.append(text(W / 2, 32, "Дві статті — дві різні драбини", size=17, bold=True))
    P.append(text(W / 2, 56, "номерну ієрархію Тип 0–3 означено 1959 року, а не 1956-го",
                  size=12, color=MUTED))

    # ── ліва панель: 1956 ────────────────────────────────────────────────────
    P.append(rect(28, 80, 444, 402, fill="#fbfcfe", stroke=BLUE, sw=1.8, rx=12))
    P.append(text(250, 108, "1956 · «Три моделі опису мови»", size=13.5, color=BLUE, bold=True))
    P.append(text(250, 128, "IRE Trans. on Information Theory, IT-2(3), 113–124",
                  size=10, color=MUTED))
    P.append(fitbox(48, 146, 404, 72,
                    "Модель 3 · Трансформаційна граматика\nте, заради чого писалася стаття",
                    size=12.5, fill="#eef4ff", stroke=BLUE, color=INK))
    P.append(fitbox(48, 232, 404, 72,
                    "Модель 2 · Граматика структури складників\n(phrase structure)",
                    size=12.5, fill="#eef4ff", stroke=BLUE, color=INK))
    P.append(fitbox(48, 318, 404, 72,
                    "Модель 1 · Скінченне джерело Маркова\nмішень: показати, що ЦЕ не тягне англійську",
                    size=12.5, fill="#fff3f2", stroke=RED, color=INK))
    P.append(text(250, 416, "три моделі, а не чотири типи; номерів немає",
                  size=11, color=MUTED, italic=True))
    P.append(text(250, 444, "«ієрархії Чомського» тут ще немає", size=12.5, color=INK, bold=True))

    # ── права панель: 1959 ───────────────────────────────────────────────────
    P.append(rect(508, 80, 444, 402, fill="#fbfcfe", stroke=INK, sw=1.8, rx=12))
    P.append(text(730, 108, "1959 · «Про деякі формальні властивості граматик»",
                  size=12, bold=True))
    P.append(text(730, 128, "Information and Control, 2(2), 137–167", size=10, color=MUTED))
    P.append(fitbox(528, 146, 404, 58, "Тип 0 · без обмежень   =   машина Тюринга",
                    size=12.5, fill="#f3f4f6", stroke=INK, color=INK))
    P.append(fitbox(528, 214, 404, 58, "Тип 1 · Обмеження 1:   φ₁Aφ₂ → φ₁ωφ₂",
                    size=12.5, fill="#eef2fb", stroke=INK, color=INK))
    P.append(fitbox(528, 282, 404, 58, "Тип 2 · Обмеження 2:   A → ω",
                    size=12.5, fill="#eaf1ff", stroke=BLUE, color=INK))
    P.append(fitbox(528, 350, 404, 58,
                    "Тип 3 · Обмеження 3:   A → aB   або   A → a\n"
                    "= скінченний автомат = «регулярні події» Кліні",
                    size=11.5, fill=ACC, stroke=GREEN, color=INK))
    P.append(text(730, 434, "номер = скільки обмежень накладено", size=12.5, color=INK, bold=True))
    P.append(text(730, 458, "тому більший номер = слабша граматика",
                  size=11, color=MUTED, italic=True))

    # ── низ: підсумкова теза ─────────────────────────────────────────────────
    P.append(fitbox(28, 500, 924, 80,
                    "Трансформаційна граматика — головна модель 1956-го — у номерну ієрархію не потрапила зовсім.\n"
                    "Зате Тип 3, збудований як мішень, збігся з класом Кліні — і пережив усю суперечку про англійську.",
                    size=12.5, fill="#fffdf5", stroke="#b7791f", color=INK))
    render("img/hist-two-papers.svg", W, H, *P)


def fig_hist_lineage():
    W, H = 1000, 640
    P = [defs_arrows(INK, GREEN, BLUE)]
    P.append(text(W / 2, 32, "Звідки взялися правила, що переписують рядки", size=17, bold=True))
    P.append(text(W / 2, 56, "Тип 3 — точка, де гілка правил зустріла гілку машин",
                  size=12, color=MUTED))

    # ── хребет: родовід продукцій ────────────────────────────────────────────
    spine = [
        (84,  "Аксель Туе · 1914\nчи звести рядок X до Y заміною підрядків?", "#f3f4f6", INK),
        (172, "Еміль Пост · 1943\nканонічні системи: правила-«продукції»", "#eef2fb", INK),
        (260, "Еміль Пост · 1947\nнапів-туе правила = Тип 0 за 12 років до назви", "#eef2fb", INK),
        (348, "Пол Розенблум · 1950\nпідручник: прикласти системи Поста до мови", "#eef2fb", INK),
        (436, "Ноам Чомський · 1956 → 1959\nтри моделі → Обмеження 1, 2, 3 → Типи 0–3", "#eef4ff", BLUE),
    ]
    for y, s, fill, col in spine:
        P.append(fitbox(50, y, 360, 62, s, size=11.5, fill=fill, stroke=col, color=INK))
    for y, _, _, _ in spine[:-1]:
        P.append(arrow_c(230, y + 62, 230, y + 84, INK, sw=2))

    # ── бічна гілка: Пост → Бекус → BNF ──────────────────────────────────────
    P.append(arrow_c(412, 203, 458, 200, BLUE, sw=2))
    P.append(fitbox(460, 166, 480, 70,
                    "Джон Бекус · 1959 — BNF для ALGOL\n"
                    "продукції Поста — через курс Мартіна Девіса (IBM)\n"
                    "BNF і Тип 2 — двоюрідні брати, знайдені нарізно",
                    size=11.5, fill="#eef4ff", stroke=BLUE, color=INK))

    # ── гілка машин: МакКаллок–Піттс → Кліні ─────────────────────────────────
    P.append(fitbox(460, 296, 480, 96,
                    "Стівен Кліні · 1951 — RAND RM-704\n"
                    "над нервовими сітками МакКаллока й Піттса (1943)\n"
                    "назвав ці множини «регулярними подіями»\n"
                    "і одразу попросив кращого слова; 1956 — Automata Studies",
                    size=11.5, fill=ACC, stroke=GREEN, color=INK))
    P.append(arrow_c(700, 392, 700, 536, GREEN, sw=2))

    # ── точка зустрічі ───────────────────────────────────────────────────────
    P.append(arrow_c(230, 498, 230, 536, INK, sw=2))
    P.append(fitbox(60, 540, 880, 76,
                    "ТИП 3   =   «РЕГУЛЯРНІ ПОДІЇ» КЛІНІ   =   СКІНЧЕННИЙ АВТОМАТ\n"
                    "дві незалежні гілки — правила й машини — зійшлися на тій самій множині слів",
                    size=13, fill=ACC, stroke=GREEN, color=INK, bold=True))
    render("img/hist-lineage.svg", W, H, *P)


# ── Фігури до вставки math-pumping-lemma ─────────────────────────────────────
# 1) Гра на чотири ходи: заперечення леми — це чергування кванторів, і кожен
#    квантор — чийсь хід. Твоя свобода — рівно два ходи: слово s і кратність i.
# 2) Два кільця: регулярні ⊊ накачувані ⊊ усі мови. У щілині живе F.
# 3) Таблиця «префікс × хвіст»: скільки різних рядків — стільки й станів.

AMBER = "#b7791f"


def fig_pump_game():
    W, H = 1000, 580
    P = [defs_arrows(INK, RED, GREEN)]
    P.append(text(W / 2, 32, "Лема про накачування — це гра на чотири ходи", size=17, bold=True))
    P.append(text(W / 2, 56, "нерегулярність доводять ЗАПЕРЕЧЕННЯМ леми:   ∀p  ∃s  ∀(x, y, z)  ∃i",
                  size=12.5, color=MUTED))
    P.append(fitbox(30, 74, 940, 30,
                    "правило простеньке: квантор ∀ — хід СУПЕРНИКА (мусиш побити всі варіанти) · "
                    "квантор ∃ — ТВІЙ хід (досить одного вдалого)",
                    size=11.5, fill="#fbfcfe", stroke=MUTED, color=INK))

    bands = [
        ("∀p", "СУПЕРНИК", RED, "#fff6f5",
         "обирає довжину накачування  p ≥ 1",
         ["Ти цього p НЕ бачиш.", "Доведення мусить годитися", "для БУДЬ-ЯКОГО p."]),
        ("∃s", "ТИ", GREEN, "#f2fbf6",
         "обираєш ОДНЕ слово  s ∈ L,  |s| ≥ p",
         ["ТВІЙ ХІД — і головний.", "s вільно будувати З p:", "напр. s = 0ᵖ10ᵖ."]),
        ("∀(x, y, z)", "СУПЕРНИК", RED, "#fff6f5",
         "ріже  s = x · y · z :   |y| ≥ 1,   |xy| ≤ p",
         ["Мусиш побити ВСІ розрізи.", "Зате |xy| ≤ p прибиває y", "у перші p символів — подарунок."]),
        ("∃i", "ТИ", GREEN, "#f2fbf6",
         "обираєш кратність  i ≥ 0",
         ["ТВІЙ ХІД. Виграв, якщо", "x · yⁱ · z ∉ L. Годиться", "й i = 0 — «здути» цикл."]),
    ]
    for k, (q, who, col, fill, move, note) in enumerate(bands):
        y0 = 116 + k * 96
        P.append(rect(30, y0, 940, 84, fill=fill, stroke=col, sw=1.6, rx=10))
        # ліворуч: квантор і хто ходить
        P.append(rect(42, y0 + 12, 148, 60, fill="#ffffff", stroke=col, sw=1.4, rx=8))
        P.append(text(116, y0 + 38, q, size=17, color=INK, bold=True))
        P.append(text(116, y0 + 60, who, size=11, color=col, bold=True))
        # посередині: сам хід
        P.append(text(206, y0 + 48, move, size=13.5, color=INK, anchor="start", bold=True))
        # праворуч: що це означає для тебе
        P.append(rect(636, y0 + 10, 322, 64, fill="#ffffff", stroke="#c9ced6", sw=1.2, rx=8))
        P.append(mtext(797, y0 + 30, note, size=11.5, color=INK, lh=1.35))

    P.append(fitbox(30, 508, 940, 60,
                    "Твоя свобода — рівно два ходи: слово s і кратність i. Розріз обирає СУПЕРНИК —\n"
                    "тому «нехай y складається з нулів» без посилання на |xy| ≤ p доведенням не є.",
                    size=12.5, fill="#fffdf5", stroke=AMBER, color=INK, bold=True))
    render("img/pump-game.svg", W, H, *P)


def fig_pump_vs_regular():
    W, H = 1020, 600
    P = [defs_arrows(INK, RED, GREEN, BLUE)]
    P.append(text(W / 2, 32, "Накачування — симптом, а не діагноз", size=17, bold=True))
    P.append(text(W / 2, 56, "стрілка йде лише в один бік: регулярна ⇒ накачується", size=12.5, color=MUTED))

    # три вкладені кільця
    P.append(rect(30, 76, 650, 404, fill="#f3f4f6", stroke=INK, sw=1.8, rx=14))
    P.append(rect(56, 148, 598, 306, fill="#fffdf5", stroke=AMBER, sw=1.8, rx=12))
    P.append(rect(82, 226, 546, 200, fill=ACC, stroke=GREEN, sw=2, rx=10))

    # кільце 1: усі мови (лема їх ловить)
    P.append(text(46, 98, "Усі мови над Σ*", size=12.5, color=MUTED, anchor="start", bold=True))
    P.append(text(46, 120, "0ⁿ1ⁿ · збалансовані дужки · паліндроми · 0ⁿ при простому n",
                  size=12, color=RED, anchor="start", bold=True))
    P.append(text(46, 139, "накачування ПРОВАЛЮЄТЬСЯ → лема доводить нерегулярність",
                  size=11, color=RED, anchor="start"))

    # кільце 2: накачувані, але не регулярні — щілина
    P.append(text(72, 170, "Мови, ЩО НАКАЧУЮТЬСЯ (проходять лему)",
                  size=12.5, color=AMBER, anchor="start", bold=True))
    P.append(text(72, 192, "F = { aⁱbʲcᵏ  :  якщо i = 1, то j = k }",
                  size=12, color=INK, anchor="start", bold=True))
    P.append(text(72, 211, "накачується з p = 2 — і все одно НЕ регулярна: тут лема сліпа",
                  size=11, color=AMBER, anchor="start"))

    # ядро: регулярні
    P.append(text(355, 258, "РЕГУЛЯРНІ МОВИ", size=15, color=GREEN, bold=True))
    P.append(text(355, 281, "пам'ять = скінченний стан", size=12, color=MUTED))
    P.append(rect(140, 302, 430, 78, fill="#ffffff", stroke=GREEN, sw=1.4, rx=8))
    P.append(text(355, 330, "парне число одиниць · a*b* · «містить 101»", size=12.5, color=INK))
    P.append(text(355, 354, "усе, що взагалі описує регулярний вираз", size=11.5, color=MUTED))

    # де ріже лема, а де — Майгілл і Нероуд
    P.append(rect(700, 128, 290, 118, fill="#fffdf5", stroke=AMBER, sw=1.6, rx=10))
    P.append(text(845, 152, "ЛЕМА РІЖЕ ТУТ", size=12.5, color=AMBER, bold=True))
    P.append(mtext(845, 176, ["провал накачування  ⇒  нерегулярна ✓",
                              "накачується  ⇒  не відомо НІЧОГО ✗",
                              "необхідна умова, не достатня"], size=11, color=INK, lh=1.5))
    P.append(arrow_c(698, 187, 660, 187, AMBER, sw=2))

    P.append(rect(700, 298, 290, 118, fill=ACC, stroke=GREEN, sw=1.6, rx=10))
    P.append(text(845, 322, "МАЙГІЛЛ — НЕРОУД РІЖЕ ТУТ", size=12.5, color=GREEN, bold=True))
    P.append(mtext(845, 346, ["індекс ≡ₗ скінченний  ⟺  регулярна",
                              "нескінченний  ⟺  нерегулярна",
                              "критерій, а не симптом"], size=11, color=INK, lh=1.5))
    P.append(arrow_c(698, 357, 634, 357, GREEN, sw=2))

    P.append(fitbox(30, 500, 960, 76,
                    "Між двома межами лежить щілина: мови, що вміють накачуватися, не будучи регулярними.\n"
                    "Тому провал накачування — доказ, а успіх — не доказ нічого.\n"
                    "Точну межу проводить лише індекс відношення ≡ₗ.",
                    size=12.5, fill="#ffffff", stroke=INK, color=INK))
    render("img/pump-vs-regular.svg", W, H, *P)


def _cell(x, y, w, h, s, fill, size=13, bold=False, color=INK):
    out = rect(x, y, w, h, fill=fill, stroke="#c9ced6", sw=1.0, rx=0)
    out += text(x + w / 2, y + h / 2 + size * 0.35, s, size=size, color=color, bold=bold)
    return out


def fig_nerode_table():
    W, H = 1040, 560
    P = [defs_arrows(INK, GREEN)]
    P.append(text(W / 2, 32, "Що машина мусить пам'ятати: таблиця «префікс × хвіст»", size=17, bold=True))
    P.append(text(W / 2, 56, "у клітинці — чи належить мові склейка «префікс + хвіст». "
                             "Два префікси різні лише тоді, коли різні їхні РЯДКИ.",
                  size=12, color=MUTED))

    HD, CH = 34, 34
    YES, NO = "✓", "✗"
    HEAD = "#e9edf3"

    # ── ліва таблиця: парне число одиниць (регулярна) ───────────────────────
    x0, y0, hw, cw = 44, 110, 78, 66
    P.append(text(x0 + (hw + 4 * cw) / 2, 92, "L = «парне число одиниць»  —  регулярна",
                  size=13, color=INK, bold=True))
    P.append(_cell(x0, y0, hw, HD, "хвіст z →", HEAD, size=11, color=MUTED))
    for j, z in enumerate(["ε", "1", "11", "0"]):
        P.append(_cell(x0 + hw + j * cw, y0, cw, HD, z, HEAD, size=13, bold=True))
    rowsL = [("ε", "AAAA"), ("0", "AAAA"), ("11", "AAAA"),
             ("1", "BBBB"), ("01", "BBBB"), ("111", "BBBB")]
    valsL = {"A": [1, 0, 1, 1], "B": [0, 1, 0, 0]}
    tintA, tintB = "#eafaf0", "#eef2fb"
    for i, (px, grp) in enumerate(rowsL):
        yy = y0 + HD + i * CH
        g = grp[0]
        tint = tintA if g == "A" else tintB
        col = GREEN if g == "A" else BLUE
        P.append(_cell(x0, yy, hw, CH, px, tint, size=13, bold=True, color=col))
        for j, v in enumerate(valsL[g]):
            P.append(_cell(x0 + hw + j * cw, yy, cw, CH, YES if v else NO, "#ffffff",
                           size=15, bold=True, color=GREEN if v else "#b6bcc6"))
    yL = y0 + HD + len(rowsL) * CH
    P.append(text(x0 + (hw + 4 * cw) / 2, yL + 26, "різних рядків — рівно 2 (зелені й сині)",
                  size=12, color=INK, bold=True))
    P.append(text(x0 + (hw + 4 * cw) / 2, yL + 48, "2 класи → мінімальний автомат має 2 стани",
                  size=11.5, color=MUTED))

    # ── права таблиця: 0ⁿ1ⁿ (нерегулярна) ───────────────────────────────────
    x1, hw1, cw1 = 566, 86, 74
    P.append(text(x1 + (hw1 + 4 * cw1) / 2, 92, "L = 0ⁿ1ⁿ  —  нерегулярна", size=13, color=INK, bold=True))
    P.append(_cell(x1, y0, hw1, HD, "хвіст z →", HEAD, size=11, color=MUTED))
    for j, z in enumerate(["1", "11", "111", "1111"]):
        P.append(_cell(x1 + hw1 + j * cw1, y0, cw1, HD, z, HEAD, size=13, bold=True))
    rowsR = ["ε", "0", "00", "000", "0000"]
    for i, px in enumerate(rowsR):
        yy = y0 + HD + i * CH
        P.append(_cell(x1, yy, hw1, CH, px, "#f7f8fa", size=13, bold=True, color=INK))
        for j in range(4):
            hit = (i == j + 1)      # 0ⁿ + 1ⁿ ∈ L рівно на діагоналі
            P.append(_cell(x1 + hw1 + j * cw1, yy, cw1, CH, YES if hit else NO,
                           "#eafaf0" if hit else "#ffffff",
                           size=15, bold=True, color=GREEN if hit else "#b6bcc6"))
    yR = y0 + HD + len(rowsR) * CH
    P.append(text(x1 + (hw1 + 4 * cw1) / 2, yR + 26, "усі рядки різні — ✓ лише на діагоналі",
                  size=12, color=INK, bold=True))
    P.append(text(x1 + (hw1 + 4 * cw1) / 2, yR + 48, "діагональ не кінчається → класів нескінченно",
                  size=11.5, color=MUTED))
    P.append(text(x1 + (hw1 + 4 * cw1) / 2, yR + 70, "→ скінченного автомата не існує",
                  size=11.5, color=RED, bold=True))

    P.append(fitbox(44, 448, 952, 92,
                    "Про прочитаний префікс стан може забути все, крім ОДНОГО: які хвости доводять слово до прийняття.\n"
                    "Рядки однакові — префікси можна злити в один стан. Рядки різні — стани мусять бути різні.\n"
                    "Скільки різних рядків, стільки й станів: скінченно — мова регулярна, нескінченно — ні.",
                    size=12.5, fill="#fbfcfe", stroke=INK, color=INK))
    render("img/nerode-table.svg", W, H, *P)


if __name__ == "__main__":
    fig_three_faces()
    fig_hierarchy()
    fig_pumping()
    fig_lockstep()
    fig_grid()
    fig_four_ops()
    fig_hist_two_papers()
    fig_hist_lineage()
    fig_pump_game()
    fig_pump_vs_regular()
    fig_nerode_table()
    print("OK: three-faces.svg, hierarchy.svg, pumping.svg, lockstep.svg, grid.svg, "
          "four-ops.svg, hist-two-papers.svg, hist-lineage.svg, pump-game.svg, "
          "pump-vs-regular.svg, nerode-table.svg")
