# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Ієрархія Хомського».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

RED   = "#c0392b"
BLUE  = "#2457d6"
GREEN = "#27ae60"
AMBER = "#b7791f"
ACC   = "#eafaf0"

# рядкові тінти для чотирьох типів (від слабшого Тип 3 до найсильнішого Тип 0)
T3 = "#eafaf0"   # регулярні — зелений
T2 = "#eaf1ff"   # контекстно-вільні — синій
T1 = "#eef2fb"   # контекстно-залежні — блідо-синій
T0 = "#f2f3f5"   # рекурсивно-зліченні — сірий
HEAD = "#e9edf3"


def defs_arrows(*colors):
    out = ["<defs>"]
    for c in colors:
        mid = "ar_%s" % c.lstrip("#")
        out.append('<marker id="%s" viewBox="0 0 10 10" refX="8.4" refY="5" '
                   'markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse">'
                   '<path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>' % (mid, c))
    out.append("</defs>")
    return "".join(out)


def arrow_c(x1, y1, x2, y2, color, sw=2.2):
    mid = "ar_%s" % color.lstrip("#")
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#%s)"/>' % (x1, y1, x2, y2, color, sw, mid))


def cell(x, y, w, h, lines, fill, stroke=MUTED, size=13, bold=False, color=INK, sw=1.2):
    """Клітина таблиці з центрованим (можливо багаторядковим) написом."""
    if isinstance(lines, str):
        lines = lines.split("\n")
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=6)
    cy = y + h / 2 - (len(lines) - 1) * size * 1.28 / 2 + size * 0.34
    out += mtext(x + w / 2, cy, lines, size=size, color=color, bold=bold, lh=1.28)
    return out


# ── Фігура 1: майстер-таблиця — чотири поверхи, по рядку на кожен ─────────────
# Один рядок = один тип: форма правил граматики · машина-розпізнавач · пам'ять ·
# мова-свідок. Це головний довідковий об'єкт статті. Ліворуч — вісь пам'яті.
def fig_master_table():
    W, H = 1020, 476
    P = [defs_arrows(INK)]
    P.append(text(W / 2, 30, "Чотири поверхи ієрархії Хомського", size=18, bold=True))
    P.append(text(W / 2, 51, "кожен щабель угору купує новий вид пам'яті — і нові мови разом із ним",
                  size=12, color=MUTED))

    # координати стовпчиків
    cx_type, w_type = 72, 150
    cx_gram, w_gram = 222, 232
    cx_mach, w_mach = 454, 214
    cx_mem,  w_mem  = 668, 160
    cx_wit,  w_wit  = 828, 176
    y0, hh, rh = 68, 42, 80

    # заголовок таблиці
    heads = [(cx_type, w_type, "Тип"), (cx_gram, w_gram, "Граматика (форма правил)"),
             (cx_mach, w_mach, "Машина-розпізнавач"), (cx_mem, w_mem, "Пам'ять"),
             (cx_wit, w_wit, "Мова-свідок")]
    for x, w, h in heads:
        P.append(cell(x, y0, w, hh, h, HEAD, stroke="#c9ced6", size=12, bold=True, color=INK))

    rows = [
        (T3, GREEN, ("Тип 3", "Регулярні"), "A → a\nA → aB", "Скінченний\nавтомат",
         "скінченний\nстан", "a*b*\n«містить 101»"),
        (T2, BLUE, ("Тип 2", "Контекстно-вільні"), "A → α", "Магазинний\nавтомат",
         "стек\n(LIFO)", "aⁿbⁿ\nдужки, синтаксис"),
        (T1, "#4b5563", ("Тип 1", "Контекстно-залежні"), "αAβ → αγβ\n|права| ≥ |ліва|",
         "Лінійно-обмежений\nавтомат", "стрічка ≈\nдовжина входу", "aⁿbⁿcⁿ"),
        (T0, INK, ("Тип 0", "Рекурсивно-зліченні"), "γ → α\nγ ≠ ε", "Машина\nТюринга",
         "необмежена\nстрічка", "усе\nперелічуване"),
    ]
    for i, (tint, tcol, typ, gram, mach, mem, wit) in enumerate(rows):
        y = y0 + hh + i * rh
        # стовпчик «Тип» — сильніший тінт, дві лінії (номер + назва)
        P.append(rect(cx_type, y, w_type, rh, fill=tint, stroke=tcol, sw=1.8, rx=6))
        P.append(text(cx_type + w_type / 2, y + 32, typ[0], size=17, color=INK, bold=True))
        P.append(text(cx_type + w_type / 2, y + 55, typ[1], size=11.5, color=tcol, bold=True))
        P.append(cell(cx_gram, y, w_gram, rh, gram, "#ffffff", size=15, bold=True))
        P.append(cell(cx_mach, y, w_mach, rh, mach, tint, size=13, color=INK))
        P.append(cell(cx_mem, y, w_mem, rh, mem, "#ffffff", size=12, color=INK))
        P.append(cell(cx_wit, y, w_wit, rh, wit, tint, size=13, bold=True, color=tcol))

    # вісь пам'яті ліворуч (донизу — більше)
    ax = 36
    P.append(text(ax, y0 + 6, "менше", size=10.5, color=MUTED))
    P.append(arrow_c(ax, y0 + 18, ax, y0 + hh + 4 * rh - 4, INK, sw=2.2))
    P.append(text(ax - 2, y0 + hh + 4 * rh + 16, "більше", size=10.5, color=MUTED))
    P.append(text(ax - 2, y0 + hh + 4 * rh + 32, "пам'яті", size=10.5, color=MUTED))
    render("img/master-table.svg", W, H, *P)


# ── Фігура 2: вкладені кільця + свідки в щілинах + прихований поверх ──────────
# Строгі включення: кожне більше кільце ловить рівно ту мову-свідка, що впала з
# меншого. Окремо підсвічено РОЗВ'ЯЗНІ мови — поверх між Тип 1 і Тип 0, який
# номерна ієрархія пропускає.
def fig_rings():
    W, H = 940, 648
    P = [defs_arrows(INK, GREEN, BLUE, RED, AMBER)]
    P.append(text(W / 2, 30, "Драбина не провалюється: кожне включення строге", size=17, bold=True))
    P.append(text(W / 2, 51, "у кожній щілині живе мова-свідок — вона є в більшому класі, але не в меншому",
                  size=11.5, color=MUTED))

    # п'ять вкладених рамок (зовні RE → всередині регулярні), рівномірний інсет
    rings = [
        (30,  72, 880, 540, T0,   INK,   "Тип 0 · Рекурсивно-зліченні  —  Машина Тюринга"),
        (96,  128, 748, 428, "#fffdf5", AMBER, "Розв'язні (рекурсивні) мови"),
        (162, 184, 616, 316, T1,   "#4b5563", "Тип 1 · Контекстно-залежні  —  лінійно-обмежений автомат"),
        (228, 240, 484, 204, T2,   BLUE,  "Тип 2 · Контекстно-вільні  —  магазинний автомат"),
        (294, 296, 352, 92,  ACC,  GREEN, ""),   # ядро — регулярні
    ]
    for x, y, w, h, fill, col, label in rings:
        P.append(rect(x, y, w, h, fill=fill, stroke=col, sw=2.0, rx=14))
        if label:
            P.append(text(x + 18, y + 24, label, size=12, color=col, anchor="start", bold=True))

    # свідки в щілинах (у верхній смузі кожного кільця, під його назвою)
    P.append(text(48, 108, "свідок: «проблема зупинки» — перелічна, але НЕ розв'язна",
                  size=11, color=INK, anchor="start"))
    P.append(text(114, 164, "цей поверх номерна ієрархія ПРОПУСКАЄ · свідок: розв'язна мова, що не контекстно-залежна",
                  size=10.5, color=AMBER, anchor="start"))
    P.append(text(180, 220, "свідок: aⁿbⁿcⁿ  (рівне число a, b, c)",
                  size=11, color=INK, anchor="start"))
    P.append(text(246, 276, "свідок: aⁿbⁿ · збалансовані дужки · вкладеність",
                  size=11, color=BLUE, anchor="start"))

    # ядро — регулярні
    P.append(text(W / 2, 326, "Тип 3 · РЕГУЛЯРНІ", size=14, color=GREEN, bold=True))
    P.append(text(W / 2, 348, "скінченний автомат · пам'ять = стан", size=11, color=INK))
    P.append(text(W / 2, 370, "a*b* · «містить 101» · будь-який regex", size=11, color=MUTED))

    # підсумкові підписи-стрілки праворуч
    P.append(rect(628, 456, 286, 76, fill="#ffffff", stroke=INK, sw=1.4, rx=10))
    P.append(mtext(771, 480, ["що ширше кільце — то",
                              "більше пам'яті в машини;",
                              "свідок доводить, що межа реальна"],
                   size=11, color=INK, lh=1.4))

    P.append(fitbox(30, 556, 880, 72,
                    "Включення строгі: Тип 3 ⊊ Тип 2 ⊊ Тип 1 ⊊ розв'язні ⊊ Тип 0. Стрілка «регулярна ⇒ ширший клас»\n"
                    "йде лише вниз — угору не повертає. Тому знайдений свідок у щілині — не приклад, а ДОКАЗ межі.",
                    size=12, fill="#fbfcfe", stroke=INK, color=INK))
    render("img/rings.svg", W, H, *P)


# ── Фігура 3: чому номери йдуть навспак — накопичення обмежень ────────────────
# З Тип 0 (без обмежень) послідовно додаємо Обмеження 1, 2, 3. Кожне тісніше →
# клас мов вужчий. Номер типу = скільки обмежень накладено, тому більший номер =
# слабша граматика. Смуги внизу показують, як клас звужується.
def fig_restrictions():
    W, H = 980, 486
    P = [defs_arrows(INK, GREEN)]
    P.append(text(W / 2, 30, "Чому номери йдуть навспак: номер рахує обмеження", size=17, bold=True))
    P.append(text(W / 2, 51, "Чомський (1959) починає з довільних правил і накладає дедалі тісніші умови",
                  size=11.5, color=MUTED))

    boxes = [
        (INK,   "Тип 0", "без обмежень", "γ → α"),
        ("#4b5563", "Тип 1", "не вкорочувати", "αAβ → αγβ"),
        (BLUE,  "Тип 2", "ліворуч — 1 нетермінал", "A → α"),
        (GREEN, "Тип 3", "праворуч — a або aB", "A → aB | a"),
    ]
    bw, gap = 196, 44
    x0 = (W - (4 * bw + 3 * gap)) / 2
    by, bh = 90, 148
    fills = [T0, T1, T2, T3]
    for k, (col, name, cond, form) in enumerate(boxes):
        x = x0 + k * (bw + gap)
        P.append(rect(x, by, bw, bh, fill=fills[k], stroke=col, sw=1.9, rx=11))
        P.append(text(x + bw / 2, by + 34, name, size=17, color=INK, bold=True))
        P.append(rect(x + 20, by + 50, bw - 40, 34, fill="#ffffff", stroke=col, sw=1.3, rx=7))
        P.append(text(x + bw / 2, by + 72, form, size=15, color=INK, bold=True))
        if k > 0:
            P.append(text(x + bw / 2, by + 108, "+ обмеження " + str(k), size=11.5, color=col, bold=True))
            P.append(text(x + bw / 2, by + 128, cond, size=11, color=INK))
        else:
            P.append(text(x + bw / 2, by + 118, cond, size=12, color=MUTED))
        # стрілка й підпис між боксами
        if k > 0:
            xa = x0 + k * (bw + gap) - gap
            P.append(arrow_c(xa - gap + bw + 4, by + bh / 2, xa - 4, by + bh / 2, INK, sw=2.2))

    # смуги: клас мов звужується щокроку
    barY = by + bh + 44
    P.append(text(W / 2, barY - 18, "клас мов, який породжують такі граматики", size=12, color=INK, bold=True))
    widths = [860, 620, 400, 190]
    tints  = [T0, T1, T2, ACC]
    strokes = [INK, "#4b5563", BLUE, GREEN]
    labels = ["усі перелічувані", "контекстно-залежні", "контекстно-вільні", "регулярні"]
    for i, (bwid, tint, stc, lab) in enumerate(zip(widths, tints, strokes, labels)):
        x = W / 2 - bwid / 2
        y = barY + i * 26
        P.append(rect(x, y, bwid, 22, fill=tint, stroke=stc, sw=1.5, rx=5))
        P.append(text(W / 2, y + 15, lab, size=11.5, color=INK, bold=(i == 3)))

    P.append(fitbox(60, barY + 4 * 26 + 14, W - 120, 44,
                    "Три обмеження — три сходинки вниз. «Тип 3» означає буквально «граматика, що задовольняє "
                    "Обмеження 3»,\nнайтісніше з трьох, — тому найбільший номер відповідає НАЙслабшій граматиці.",
                    size=12, fill="#fffdf5", stroke=AMBER, color=INK))
    render("img/restrictions.svg", W, H, *P)


# ─────────────────────────────────────────────────────────────────────────────
# ФІГУРИ ДО ВСТАВКИ math-strict-inclusions.md (строгі докази чотирьох включень)
# ─────────────────────────────────────────────────────────────────────────────

def tri(xa, ya, xl, xr, yb, fill, stroke=INK, sw=1.6):
    """Трикутник-піддерево: вершина (xa,ya), основа [xl..xr] на висоті yb."""
    return ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" '
            'stroke="%s" stroke-width="%.1f"/>' % (xa, ya, xl, yb, xr, yb, fill, stroke, sw))


# ── Вставка / Фігура 1: лема про накачування для КВ-мов через дерево розбору ──
# Високе дерево розбору мусить двічі пройти той самий нетермінал A. Кільце між
# двома A породжує v і y, піддерево під нижнім A — x. Тому кільце можна крутити:
# A ⇒* vⁱ x yⁱ, і слово лишається в мові. Це механізм, а не твердження.
def fig_cf_pump_tree():
    W, H = 980, 604
    PT_S, PT_A1, PT_A2 = "#eaf1ff", "#d3e2ff", "#b7d0ff"
    HL = "#fdecea"
    P = [defs_arrows(INK)]
    P.append(text(W / 2, 30, "Лема про накачування для контекстно-вільних мов", size=18, bold=True))
    P.append(text(W / 2, 51, "високе дерево розбору двічі проходить той самий нетермінал — і кільце між ними качається",
                  size=12, color=MUTED))

    # ── ліва панель: дерево розбору ──
    apex_x = 322
    yb = 462
    P.append(tri(apex_x, 96, 70, 574, yb, PT_S, stroke=BLUE, sw=1.8))    # усе дерево від S
    P.append(tri(apex_x, 160, 162, 482, yb, PT_A1, stroke=BLUE, sw=1.7)) # піддерево верхнього A
    P.append(tri(apex_x, 266, 252, 392, yb, PT_A2, stroke=BLUE, sw=1.7)) # піддерево нижнього A → x

    # шлях S → A → A (пунктир по осі)
    P.append(line(apex_x, 96, apex_x, yb, color=INK, sw=1.6, dash="4 4"))
    # вузли
    for (yy, lab) in [(96, "S"), (160, "A"), (266, "A")]:
        P.append(circle(apex_x, yy, 5.5, fill="#ffffff", stroke=INK, sw=1.8))
    P.append(text(apex_x, 88, "S", size=15, color=INK, bold=True))
    P.append(text(apex_x + 20, 156, "A", size=15, color=BLUE, bold=True))
    P.append(text(apex_x + 20, 262, "A", size=15, color=BLUE, bold=True))

    # смужки-підсвітки під качуваними частинами v та y
    P.append(rect(162, yb, 90, 12, fill=HL, stroke=RED, sw=1.2, rx=2))   # v
    P.append(rect(392, yb, 90, 12, fill=HL, stroke=RED, sw=1.2, rx=2))   # y

    # поділ основи: u | v | x | y | z (тік-лінії)
    for xv in (162, 252, 392, 482):
        P.append(line(xv, yb, xv, yb + 24, color=MUTED, sw=1.2))
    segs = [(116, "u"), (207, "v"), (322, "x"), (437, "y"), (528, "z")]
    for cx, lab in segs:
        col = RED if lab in ("v", "y") else INK
        P.append(text(cx, yb + 44, lab, size=17, color=col, bold=True))
    P.append(text(322, yb + 74, "s  =  u · v · x · y · z", size=15, color=INK, bold=True))
    P.append(text(322, yb + 98, "|v·x·y| ≤ p        |v·y| ≥ 1", size=12.5, color=MUTED))

    # ── права панель: чому качається ──
    bx, by, bw, bh = 640, 96, 316, 300
    P.append(rect(bx, by, bw, bh, fill="#fbfcff", stroke=BLUE, sw=1.6, rx=12))
    P.append(text(bx + bw / 2, by + 28, "Чому кільце качається", size=14, color=BLUE, bold=True))
    lines = [
        ("A ⇒* v A y", "кільце між двома A", INK),
        ("A ⇒* x", "піддерево під нижнім A", INK),
        ("———————————————", "", MUTED),
        ("A ⇒* vⁱ x yⁱ", "кільце крутиться i разів", RED),
        ("S ⇒* u A z", "", INK),
        ("   ⇒* u vⁱ x yⁱ z ∈ L", "для кожного i ≥ 0", INK),
    ]
    ly = by + 58
    for code, note, col in lines:
        P.append(text(bx + 20, ly, code, size=13.5, color=col, anchor="start", bold=(col == RED)))
        if note:
            P.append(text(bx + bw - 16, ly, note, size=10.5, color=MUTED, anchor="end"))
        ly += 30
    # приклади кратностей
    P.append(line(bx + 16, ly - 2, bx + bw - 16, ly - 2, color="#dfe6f2", sw=1.2))
    ex = [("i = 0 :", "u x z"), ("i = 1 :", "u v x y z   (вихідне s)"), ("i = 2 :", "u v² x y² z")]
    ly += 20
    for a, b in ex:
        P.append(text(bx + 20, ly, a, size=12.5, color=MUTED, anchor="start"))
        P.append(text(bx + 78, ly, b, size=12.5, color=INK, anchor="start"))
        ly += 24

    P.append(fitbox(40, 560, W - 80, 34,
                    "Нетерміналів скінченно, тож у досить довгому слові якийсь із них на шляху повторюється. "
                    "Повтор — кільце A ⇒* v A y; крутиш його — і породжуєш ту саму мову з іншими v, y.",
                    size=12, fill="#f6f8fc", stroke=BLUE, color=INK))
    render("img/cf-pump-tree.svg", W, H, *P)


# ── Вставка / Фігура 2: чому aⁿbⁿcⁿ ламає лему про накачування ────────────────
# Три блоки по p літер. Вікно v·x·y завширшки ≤ p не дістає водночас a і c —
# між ними цілий блок b завдовжки p. Тож качання зачіпає щонайбільше два блоки з
# трьох, третій лишається, і рівність кількостей рветься.
def fig_abc_window():
    W, H = 980, 452
    GA, GB, GC = "#eafaf0", "#eaf1ff", "#fdf3e0"
    P = [defs_arrows(INK, RED)]
    P.append(text(W / 2, 30, "Чому aⁿbⁿcⁿ не контекстно-вільна: вікно ≤ p не дістає трьох блоків", size=17, bold=True))
    P.append(text(W / 2, 51, "накачувана частина v·x·y вужча за p — а між блоком a і блоком c лежить цілий блок b завдовжки p",
                  size=11.5, color=MUTED))

    y0, bh = 168, 66
    xa, xb, xc, bw = 120, 400, 680, 200   # три блоки по 200 px (= p літер)
    P.append(rect(xa, y0, bw, bh, fill=GA, stroke=GREEN, sw=1.8, rx=8))
    P.append(rect(xb, y0, bw, bh, fill=GB, stroke=BLUE, sw=1.8, rx=8))
    P.append(rect(xc, y0, bw, bh, fill=GC, stroke=AMBER, sw=1.8, rx=8))
    P.append(text(xa + bw / 2, y0 + 32, "a a a … a", size=16, color=GREEN, bold=True))
    P.append(text(xa + bw / 2, y0 + 54, "p разів", size=11, color=MUTED))
    P.append(text(xb + bw / 2, y0 + 32, "b b b … b", size=16, color=BLUE, bold=True))
    P.append(text(xb + bw / 2, y0 + 54, "p разів", size=11, color=MUTED))
    P.append(text(xc + bw / 2, y0 + 32, "c c c … c", size=16, color=AMBER, bold=True))
    P.append(text(xc + bw / 2, y0 + 54, "p разів", size=11, color=MUTED))

    # два дозволені вікна ≤ p над межами a|b та b|c
    def window(cx, label, col):
        wx, ww = cx - 80, 160          # ширина 160 < 200 = p
        wy = y0 - 58
        P.append(rect(wx, wy, ww, 30, fill="#ffffff", stroke=col, sw=1.8, rx=6))
        P.append(text(cx, wy + 20, "v·x·y", size=13, color=col, bold=True))
        P.append(line(wx, wy + 30, wx, y0, color=col, sw=1.3, dash="3 3"))
        P.append(line(wx + ww, wy + 30, wx + ww, y0, color=col, sw=1.3, dash="3 3"))
        P.append(text(cx, wy - 8, label, size=11, color=col))
    window(xb, "лише a і b", RED)                     # межа a|b (xb = 400)
    window(xc, "або лише b і c", RED)                 # межа b|c (xc = 680)

    # заборонений «місток» через блок b
    by2 = y0 + bh + 26
    P.append(text((xa + xc + bw) / 2, by2 + 4, "відстань від a до c = увесь блок b = p", size=12, color=INK, bold=True))
    P.append(arrow_c(xa + bw, by2 + 22, xc, by2 + 22, RED, sw=2.0))
    P.append(arrow_c(xc, by2 + 22, xa + bw, by2 + 22, RED, sw=2.0))
    P.append(text((xb + bw / 2), by2 + 42, "щоб зачепити і a, і c, вікну треба ширина > p — заборонено", size=11.5, color=RED))

    P.append(fitbox(120, 372, W - 240, 56,
                    "Отже v·y лежить щонайбільше у двох сусідніх блоках. Беремо i = 2: кількість зачеплених літер росте, "
                    "а третій блок не змінюється —\nтепер a, b, c уже НЕ порівну  →  слово вилетіло з aⁿbⁿcⁿ.  Лема провалена  →  мова не контекстно-вільна.",
                    size=12, fill="#fbfcfe", stroke=INK, color=INK))
    render("img/abc-window.svg", W, H, *P)


# ── Вставка / Фігура 3: діагоналізація Патнема — розв'язна мова поза КЗ ────────
# Рядки — усі КЗ-граматики G₁,G₂,… (їх перелічувано), стовпці — усі слова
# w₁,w₂,… Клітина: чи wⱼ ∈ L(Gᵢ). Уздовж діагоналі будуємо D, перевертаючи
# кожну клітину (Gᵢ,wᵢ). D розв'язна (членство в КЗ розв'язне), але різниться з
# кожним рядком → жодна КЗ-граматика її не породжує.
def fig_diagonal_cs():
    W, H = 900, 600
    P = [defs_arrows(INK)]
    P.append(text(W / 2, 30, "Діагоналізація: розв'язна мова, якої не породжує жодна КЗ-граматика", size=16, bold=True))
    P.append(text(W / 2, 51, "рядок — контекстно-залежна граматика, стовпець — слово; клітина: чи слово в мові граматики",
                  size=11.5, color=MUTED))

    # матриця членства (рядки G1..G5, стовпці w1..w6); діагональ виділяємо
    M = [
        [1, 0, 1, 1, 0, 1],
        [0, 0, 1, 0, 1, 0],
        [1, 1, 1, 0, 0, 1],
        [0, 1, 0, 0, 1, 1],
        [1, 0, 1, 1, 1, 0],
    ]
    x0, y0 = 150, 96
    cw, ch = 96, 44
    ncol = 6
    # заголовки стовпців
    for j in range(ncol):
        P.append(text(x0 + j * cw + cw / 2, y0 - 14, "w%d" % (j + 1), size=13, color=INK, bold=True))
    # рядки
    for i, row in enumerate(M):
        yy = y0 + i * ch
        P.append(text(x0 - 22, yy + ch / 2 + 5, "G%d" % (i + 1), size=13, color=INK, bold=True, anchor="end"))
        for j, v in enumerate(row):
            xx = x0 + j * cw
            on_diag = (i == j)
            fill = "#fff6d8" if on_diag else "#ffffff"
            stroke = AMBER if on_diag else "#cfd6e0"
            P.append(rect(xx, yy, cw, ch, fill=fill, stroke=stroke, sw=(2.0 if on_diag else 1.1), rx=5))
            mark = "∈" if v else "∉"
            col = GREEN if v else RED
            P.append(text(xx + cw / 2, yy + ch / 2 + 6, mark, size=17, color=col, bold=True))
    # стрілка по діагоналі
    P.append(text(x0 + 5 * cw + 16, y0 + 4 * ch + 8, "діагональ", size=11.5, color=AMBER, anchor="start", bold=True))

    # рядок D — перевертаємо діагональ
    yD = y0 + 5 * ch + 22
    P.append(text(x0 - 22, yD + ch / 2 + 5, "D", size=14, color=INK, bold=True, anchor="end"))
    for j in range(ncol):
        xx = x0 + j * cw
        if j < 5:
            v = 1 - M[j][j]          # перевернута діагональ
            mark = "∈" if v else "∉"
            col = GREEN if v else RED
            fill = "#eef7ff"
        else:
            mark, col, fill = "…", MUTED, "#f4f6f8"
        P.append(rect(xx, yD, cw, ch, fill=fill, stroke=NEG, sw=1.6, rx=5))
        P.append(text(xx + cw / 2, yD + ch / 2 + 6, mark, size=17, color=col, bold=(j < 5)))
    P.append(text(x0 + ncol * cw + 18, yD + ch / 2 + 1, "рядок D —", size=11, color=NEG, anchor="start", bold=True))
    P.append(text(x0 + ncol * cw + 18, yD + ch / 2 + 16, "перевернута", size=11, color=NEG, anchor="start"))
    P.append(text(x0 + ncol * cw + 18, yD + ch / 2 + 31, "діагональ", size=11, color=NEG, anchor="start"))

    P.append(fitbox(60, yD + ch + 22, W - 120, 70,
                    "D = { wᵢ : wᵢ ∉ L(Gᵢ) }.  Рядок D різниться від КОЖНОГО рядка Gᵢ рівно в діагональній клітині (Gᵢ, wᵢ) —\n"
                    "тож D ≠ L(Gᵢ) для всіх i, і жодна КЗ-граматика її не породжує.  Але членство в КЗ-мові розв'язне, а граматики\n"
                    "перелічувано — тож саму D розв'язати можна.  Розв'язна, а не контекстно-залежна.",
                    size=12, fill="#fbfcfe", stroke=INK, color=INK))
    render("img/diagonal-cs.svg", W, H, *P)


if __name__ == "__main__":
    fig_master_table()
    fig_rings()
    fig_restrictions()
    fig_cf_pump_tree()
    fig_abc_window()
    fig_diagonal_cs()
    print("OK: master-table.svg, rings.svg, restrictions.svg, "
          "cf-pump-tree.svg, abc-window.svg, diagonal-cs.svg")
