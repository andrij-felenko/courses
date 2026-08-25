# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

AMBER = "#b7791f"   # оманливо-високе (мала небезпека, великий RPN)
EFFECT = "#fdecea"  # світло-червона заливка — там, де сідає тяжкість


# ── Фігура 1: ланцюг відмови причина → вид → наслідок, з осями O, D, S ─────────
# Ідея: відмова — не точка («згорів вузол»), а ланцюг із трьох ланок. Частоту
# міряють біля причини, тяжкість — біля наслідку, виявність — на контролі між
# видом і наслідком. Тяжкість живе на кінці, тому ланцюг читають справа наліво.

def block(x, y, w, h, header, body, hcol=INK, fill=FILL):
    out = rect(x, y, w, h, fill=fill, stroke=LINE, sw=1.7)
    out += text(x + w / 2, y + 26, header, size=15, color=hcol, bold=True)
    out += mtext(x + w / 2, y + 50, body, size=12, color=MUTED, lh=1.25)
    return out


def fig_chain():
    W, H = 980, 400
    p = []

    by, bh = 118, 104
    # три ланки
    p.append(block(40, by, 210, bh, "Причина", "повторний запит\nбез захисту\nвід дублювання"))
    p.append(block(340, by, 210, bh, "Вид відмови", "платіж\nпровівся двічі"))
    p.append(block(730, by, 210, bh, "Наслідок", "клієнта списано\nдвічі → втрата\nдовіри", hcol=POS, fill=EFFECT))

    cy = by + bh / 2
    # стрілки між ланками
    p.append(arrow(250, cy, 340, cy, color=LINE, sw=2.0))
    p.append(arrow(550, cy, 610, cy, color=LINE, sw=2.0))
    p.append(arrow(700, cy, 730, cy, color=LINE, sw=2.0))
    # контроль-ворота на ланці «вид → наслідок»
    p.append(rect(610, cy - 28, 90, 56, fill="#eef6ff", stroke=NEG, sw=1.7))
    p.append(text(655, cy + 5, "контроль", size=12, color=NEG, bold=True))

    # осі під ланцюгом: O біля причини, D біля контролю, S біля наслідку
    ay = by + bh + 40
    def axis(cx, top_from_y, letter, name, sub, col):
        out = line(cx, top_from_y, cx, ay - 16, color=col, sw=1.2, dash="4 4")
        out += text(cx, ay, "%s — %s" % (letter, name), size=13, color=col, bold=True)
        out += text(cx, ay + 20, sub, size=11, color=MUTED)
        return out
    p.append(axis(145, by + bh, "O", "частота", "як часто виникає причина", NEG))
    p.append(axis(655, cy + 28, "D", "виявність", "чи спіймаємо вчасно", NEG))
    p.append(axis(835, by + bh, "S", "тяжкість", "наскільки боляче наслідок", POS))

    # підказка «читати справа наліво»
    ry = ay + 52
    p.append(arrow(870, ry, 110, ry, color=MUTED, sw=1.6))
    p.append(text(W / 2, ry - 10, "тяжкість — на кінці ланцюга, тож читати варто справа наліво",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "chain.svg"), W, H, *p,
           title="Відмова — це ланцюг: причина → вид → наслідок")


# ── Фігура 2: три осі S/O/D і пастка їхнього перемноження в RPN ────────────────
# Ідея: три незалежні осі 1–10, прикріплені до різних точок ланцюга (виявність
# інвертована: 10 = «не спіймати»). RPN = S·O·D робить осі взаємозамінними —
# і менш небезпечний вид відмови дістає ВИЩИЙ RPN за небезпечніший.

def fig_axes_rpn():
    W, H = 980, 452
    p = []

    # ── ліворуч: три вертикальні шкали ──
    ytop, ybot = 108, 356
    def vscale(cx, letter, name, where, col):
        w = 50
        x = cx - w / 2
        out = rect(x, ytop, w, ybot - ytop, fill="#f1f4f9", stroke=col, sw=1.9)
        for i in range(0, 11):
            yy = ybot - (ybot - ytop) * i / 10.0
            long = (i % 5 == 0)
            out += line(x, yy, x + (w if long else 9), yy,
                        color=(col if long else "#cdd5df"), sw=(1.5 if long else 1.0))
        out += text(x - 9, ytop + 5, "10", size=11, color=MUTED, anchor="end")
        out += text(x - 9, ybot + 5, "1", size=11, color=MUTED, anchor="end")
        out += text(cx, ytop - 30, letter, size=19, color=col, bold=True)
        out += text(cx, ytop - 12, name, size=12, color=INK)
        out += text(cx, ybot + 24, where, size=10.5, color=MUTED)
        return out
    p.append(vscale(95, "S", "тяжкість", "біля наслідку", POS))
    p.append(vscale(205, "O", "частота", "біля причини", NEG))
    p.append(vscale(315, "D", "виявність", "10 = не спіймати", AMBER))

    # роздільник
    p.append(line(392, 84, 392, 392, color="#dfe4ea", sw=1.4, dash="6 6"))

    # ── праворуч: пастка RPN ──
    rx = 420
    p.append(text(690, 96, "Пастка: RPN = S · O · D", size=16, color=INK, bold=True))

    def card(y, name, s, o, d, rpn, tag, danger):
        fill = EFFECT if danger else "#f5f6f8"
        out = rect(rx, y, 520, 96, fill=fill, stroke=(POS if danger else LINE),
                   sw=(1.9 if danger else 1.5))
        out += text(rx + 18, y + 28, name, size=14, color=INK, bold=True, anchor="start")
        # рядок оцінок; S виділяємо кольором за тяжкістю
        scol = POS if s >= 8 else MUTED
        out += text(rx + 18, y + 56, "S=%d" % s, size=13, color=scol, bold=True, anchor="start")
        out += text(rx + 78, y + 56, "O=%d   D=%d" % (o, d), size=13, color=INK, anchor="start")
        out += text(rx + 18, y + 80, tag, size=11, color=MUTED, anchor="start")
        # бейдж RPN
        bcol = AMBER if (not danger) else MUTED
        out += rect(rx + 380, y + 26, 120, 44, fill=BG, stroke=bcol, sw=2.0)
        out += text(rx + 440, y + 45, "RPN", size=11, color=MUTED)
        out += text(rx + 440, y + 63, str(rpn), size=18, color=bcol, bold=True)
        return out

    p.append(card(120, "застаріла ціна на вітрині", 4, 6, 10, 240,
                  "лише втрата маржі — а стоїть угорі списку", danger=False))
    p.append(card(232, "подвійне списання", 9, 2, 8, 144,
                  "руйнує довіру, повернення платежів — а нижче", danger=True))

    # висновок
    p.append(rect(rx, 344, 520, 60, fill="#fff8e6", stroke=AMBER, sw=1.7))
    p.append(mtext(rx + 260, 368,
                   ["RPN 240 > 144 — та справжня небезпека внизу.",
                    "Тому тяжкість важать ПЕРШОЮ, а не голий добуток."],
                   size=12.5, color=INK, lh=1.3, bold=True))

    render(os.path.join(OUT, "axes-rpn.svg"), W, H, *p,
           title="Три осі ризику й пастка їхнього добутку")


# ── Фігура 3: FMEA як повторюваний цикл (індуктивна процедура) ─────────────────
# Ідея: метод — не разова таблиця, а процедура з кроків, що замикається в петлю.
# Іде знизу вгору: від вузла до наслідку. Останній крок повертає до перебору,
# бо змінена система приносить нові види відмов — документ живий.

def fig_procedure():
    W, H = 980, 470
    p = []

    bw, bh = 196, 92
    def step(cx, y, n, lines, fill=FILL):
        x = cx - bw / 2
        out = rect(x, y, bw, bh, fill=fill, stroke=LINE, sw=1.7)
        out += circle(x + 20, y + 20, 14, fill=INK, sw=1.5)
        out += text(x + 20, y + 25, str(n), size=14, color=BG, bold=True)
        st = 12.5
        cyt = y + bh / 2 - (len(lines) - 1) * st * 1.2 / 2 + st * 0.35 + 4
        out += mtext(cx + 10, cyt, lines, size=st, color=INK, lh=1.2, bold=True)
        return out

    r1y, r2y = 120, 306
    # верхній ряд: зліва направо
    c1 = [140, 380, 620, 860]
    p.append(step(c1[0], r1y, 1, ["Розклади", "на вузли"]))
    p.append(step(c1[1], r1y, 2, ["Перелічи", "види відмов"]))
    p.append(step(c1[2], r1y, 3, ["Причина ·", "наслідок ·", "контроль"]))
    p.append(step(c1[3], r1y, 4, ["Оціни", "S · O · D"]))
    # нижній ряд: справа наліво
    c2 = [860, 500, 140]
    p.append(step(c2[0], r2y, 5, ["Впорядкуй", "за тяжкістю"], fill="#eef6ff"))
    p.append(step(c2[1], r2y, 6, ["Заходи на", "верхні рядки"], fill="#eef6ff"))
    p.append(step(c2[2], r2y, 7, ["Переоціни", "S · O · D"], fill="#eafaf0"))

    cyr1 = r1y + bh / 2
    cyr2 = r2y + bh / 2
    # стрілки верхнього ряду →
    for a, b in ((c1[0], c1[1]), (c1[1], c1[2]), (c1[2], c1[3])):
        p.append(arrow(a + bw / 2, cyr1, b - bw / 2, cyr1, sw=1.9))
    # спуск 4 → 5
    p.append(arrow(c1[3], r1y + bh, c2[0], r2y, sw=1.9))
    # стрілки нижнього ряду ←
    for a, b in ((c2[0], c2[1]), (c2[1], c2[2])):
        p.append(arrow(a - bw / 2, cyr2, b + bw / 2, cyr2, sw=1.9))

    # петля зворотного зв'язку: 7 → 2 (між рядами, пунктиром)
    fy = 250
    p.append(line(c2[2], r2y, c2[2], fy, color=FIELD, sw=1.9, dash="6 5"))
    p.append(line(c2[2], fy, c1[1], fy, color=FIELD, sw=1.9, dash="6 5"))
    p.append(arrow(c1[1], fy, c1[1], r1y + bh, color=FIELD, sw=1.9))
    p.append(text((c2[2] + c1[1]) / 2, fy - 10, "система змінилась → знову",
                  size=12, color=FIELD, bold=True, italic=True))

    # напрям індукції
    p.append(text(140, r1y - 22, "знизу вгору: від вузла до наслідку",
                  size=11.5, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "procedure.svg"), W, H, *p,
           title="FMEA — повторюваний цикл, а не разова таблиця")


# ── Фігура 4 (вставка hist): часова смуга — дві сплетені нитки родоводу ────────
# Ідея: FMEA сплетено з двох ліній. Воєнно-космічна (синя) дала методу сувору
# формальність — бо систему не перезапустиш, а одна відмова вбиває. Автопром
# (бурштинова) дав числа S/O/D і RPN заради масштабу — і сам же потім лагодив
# RPN, замінивши його на таблицю пріоритету дій.

MIL  = NEG     # воєнно-космічна нитка
AUTO = AMBER   # автопромислова нитка

def fig_timeline():
    W, H = 900, 772
    p = []

    sx = 182                       # вертикальний хребет часу
    p.append(line(sx, 80, sx, H - 26, color="#cdd5df", sw=2.2))

    # легенда двох ниток (над першою карткою)
    p.append(circle(300, 52, 7, fill=MIL, stroke=MIL))
    p.append(text(314, 57, "воєнно-космічна нитка", size=12, color=MUTED, anchor="start"))
    p.append(circle(560, 52, 7, fill=AUTO, stroke=AUTO))
    p.append(text(574, 57, "автопромислова нитка", size=12, color=MUTED, anchor="start"))

    rows = [
        (MIL,  "1949",          "MIL-P-1629",
               ["військова процедура США — перший формальний опис",
                "аналізу видів, наслідків і критичності відмов"]),
        (MIL,  "1966",          "NASA, «Аполлон»",
               ["FMECA бере на озброєння космічна програма;",
                "далі — Viking, Voyager, Magellan, Galileo"]),
        (MIL,  "1974",          "MIL-STD-1629 (SHIPS)",
               ["процедуру підняли до військового стандарту"]),
        (AUTO, "серед. 1970-х", "Ford → автопром",
               ["після справи «Пінто» Ford несе FMEA в галузь;",
                "додає PFMEA — відмови процесу виготовлення"]),
        (MIL,  "1980",          "MIL-STD-1629A",
               ["канонічна редакція стандарту (скасована 1998-го,",
                "уже без заміни — військові пішли в цивільні норми)"]),
        (AUTO, "1993",          "AIAG, 1-й автопосібник",
               ["єдині шкали S/O/D 1–10 та RPN = S · O · D"]),
        (AUTO, "2019",          "AIAG-VDA (об'єднання)",
               ["RPN → таблиця пріоритету дій (AP);",
                "7-кроковий процес, тяжкість важать першою"]),
    ]

    cy = 120
    step_y = 95
    cardw = 626
    for col, year, head, body in rows:
        x0 = sx + 42
        ch = 76
        y0 = cy - ch / 2
        p.append(line(sx, cy, x0, cy, color=col, sw=1.8))
        p.append(circle(sx, cy, 8, fill=col, stroke=col))
        p.append(text(sx - 22, cy + 4, year, size=12, color=col, bold=True, anchor="end"))
        fill = "#eef2fb" if col == MIL else "#fdf3e2"
        p.append(rect(x0, y0, cardw, ch, fill=fill, stroke=col, sw=1.7))
        p.append(text(x0 + 16, y0 + 27, head, size=14, color=INK, bold=True, anchor="start"))
        p.append(mtext(x0 + 16, y0 + 48, body, size=11.5, color=MUTED, anchor="start", lh=1.25))
        cy += step_y

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Родовід FMEA: дві сплетені нитки")


# ─────────────────────────────────────────────────────────────────────────────
#  ФІГУРА ДО ВСТАВКИ hist-fmea.md
# ─────────────────────────────────────────────────────────────────────────────

# ── Фігура: що сталося з формулою на кордоні між галузями ────────────────────
# Ідея вставки в одній картинці: воєнно-космічна критичність множила СПРАВЖНІ
# величини й давала число з одиницею; тяжкість була фільтром, а не множником,
# виявність — описом, а не числом. Автопром лишив знак ×, але не лишив величин.

def fig_substitution():
    W, H = 1240, 700
    p = []

    CW, CH = 186, 100
    RW = 310

    def card(cx, cy, sym, body, col, fill, w=CW):
        out = rect(cx - w / 2, cy - CH / 2, w, CH, fill=fill, stroke=col, sw=1.8)
        out += text(cx, cy - CH / 2 + 30, sym, size=19, color=col, bold=True)
        out += mtext(cx, cy - CH / 2 + 54, body, size=11.5, color=MUTED, lh=1.32)
        return out

    XS = [120, 332, 544, 756]          # центри карток-множників
    DOTS = [226, 438, 650]             # крапки множення між ними
    XEQ = 872                          # знак дорівнює (верхня смуга)
    XRES = 1040                        # центр картки-результату (верхня смуга)

    # ── ВЕРХНЯ СМУГА: воєнно-космічна критичність ───────────────────────────
    p.append(text(120, 40, "1966 · «Аполлон»   →   1980 · MIL-STD-1629A",
                  size=15, color=MIL, bold=True, anchor="start"))
    cy = 118
    p.append(card(XS[0], cy, "β", ["умовна ймовірність", "втрати · 0…1"], MIL, "#eef2fb"))
    p.append(card(XS[1], cy, "α", ["частка цього виду", "серед відмов · 0…1"], MIL, "#eef2fb"))
    p.append(card(XS[2], cy, "λp", ["ВИМІРЯНА інтенсивність", "відмов/год"], MIL, "#eef2fb"))
    p.append(card(XS[3], cy, "t", ["тривалість роботи", "години"], MIL, "#eef2fb"))
    for dx in DOTS:
        p.append(text(dx, cy + 7, "·", size=26, color=MIL, bold=True))
    p.append(text(XEQ, cy + 7, "=", size=24, color=MIL, bold=True))
    p.append(card(XRES, cy, "Cm", ["відмов на мільйон годин", "— число з одиницею"],
                  MIL, "#dde7fa", w=RW))

    # дві примітки: чого у формулі НЕМА
    p.append(text(120, 196, "тяжкість тут не множник — за категоріями I–IV відмови спершу розкладають на купки",
                  size=12.5, color=MUTED, anchor="start"))
    p.append(text(120, 218, "виявність тут узагалі не число — це графа з описом: «є сигналізація» / «немає»",
                  size=12.5, color=MUTED, anchor="start"))

    # ── СЕРЕДИНА: три підміни ───────────────────────────────────────────────
    bx, by, bw, bh = 120, 256, 1000, 178
    p.append(rect(bx, by, bw, bh, fill="#fbfbfd", stroke="#cdd5df", sw=1.8))
    p.append(text(bx + bw / 2, by + 30, "ТРИ ПІДМІНИ НА КОРДОНІ ГАЛУЗЕЙ", size=13.5,
                  color=INK, bold=True))
    rows = [
        ("λp — виміряна інтенсивність, відмов/год", "O — ранг від 1 до 10"),
        ("категорії I–IV — фільтр: спершу розклади", "S — ще один множник"),
        ("графа контролю — опис словами", "D — ще один множник"),
    ]
    ry = by + 66
    for left, right in rows:
        p.append(text(575, ry + 5, left, size=12.5, color=MIL, anchor="end"))
        p.append(arrow(590, ry, 655, ry, color="#9aa3af", sw=1.8))
        p.append(text(670, ry + 5, right, size=12.5, color=AUTO, anchor="start"))
        ry += 38

    p.append(text(bx + bw / 2, by + bh + 26,
                  "знак × переїхав через кордон; величини, що робили його законним, — ні",
                  size=12.5, color=MUTED, italic=True))

    # ── НИЖНЯ СМУГА: автопромисловий RPN ────────────────────────────────────
    p.append(text(120, 508, "1993 · перший автопосібник AIAG", size=15, color=AUTO,
                  bold=True, anchor="start"))
    cy = 596
    p.append(card(XS[0], cy, "S", ["ранг тяжкості", "1…10, без одиниць"], AUTO, "#fdf3e2"))
    p.append(card(XS[1], cy, "O", ["ранг частоти", "1…10, без одиниць"], AUTO, "#fdf3e2"))
    p.append(card(XS[2], cy, "D", ["ранг виявності", "1…10, без одиниць"], AUTO, "#fdf3e2"))
    for dx in DOTS[:2]:
        p.append(text(dx, cy + 7, "·", size=26, color=AUTO, bold=True))
    p.append(text(660, cy + 7, "=", size=24, color=AUTO, bold=True))
    p.append(card(830, cy, "RPN", ["число від 1 до 1000", "— без жодної одиниці"],
                  AUTO, "#fae8cd", w=RW))

    render(os.path.join(OUT, "substitution.svg"), W, H, *p,
           title="Що сталося з формулою на кордоні між галузями")


# ─────────────────────────────────────────────────────────────────────────────
#  ФІГУРИ ДО ВСТАВКИ math-rpn-ordinal.md
# ─────────────────────────────────────────────────────────────────────────────

RANK = "#7c3aed"   # порядкове — те, що ми насправді маємо
REAL = "#0f766e"   # величина — те, чого ми не маємо


# ── Фігура: драбина шкал Стівенса й де законне множення ──────────────────────
# Ідея: множення легітимне лише на шкалі відношень. S/O/D сидять на порядковій —
# двома щаблями нижче. RPN перестрибує через щаблі, яких не заслужив.

def fig_scales_ladder():
    W, H = 1180, 655
    p = []

    x0 = 50
    cols = [200, 250, 320, 300]      # шкала · що фіксує · допустиме · що законно
    heads = ["Шкала", "Що справді фіксує", "Допустиме перетворення",
             "Що на ній законно рахувати"]
    xs = []
    x = x0
    for w in cols:
        xs.append(x); x += w
    tablew = sum(cols)

    hy = 62
    for i, h in enumerate(heads):
        p.append(text(xs[i] + cols[i] / 2, hy, h, size=13.5, color=MUTED, bold=True))
    p.append(line(x0, hy + 14, x0 + tablew, hy + 14, color=MUTED, sw=1.2))

    rows = [
        ("Відношень", "рівність відношень;\nє справжній нуль",
         "φ(x) = a·x,  a > 0", "усе: + − × ÷,\nсереднє, «удвічі більше»", REAL),
        ("Інтервальна", "рівність різниць;\nнуль умовний",
         "φ(x) = a·x + b", "різниці, середнє;\n× вже НЕ має сенсу", INK),
        ("Порядкова", "лише порядок:\nбільше / менше",
         "будь-яка зростна φ", "медіана, ранги;\nані +, ані ×", RANK),
        ("Називна", "лише тотожність:\nте саме / інше",
         "будь-яка взаємно\nоднозначна φ", "тільки «скільки штук»", MUTED),
    ]

    ry = hy + 30
    rh = 108
    y_ord = y_rat = None
    for name, fixes, tr, ops, col in rows:
        fill = "#f7f4ff" if col == RANK else ("#effaf7" if col == REAL else FILL)
        p.append(rect(x0, ry, tablew, rh, fill=fill, stroke=col if col in (RANK, REAL) else "#d8dde3",
                      sw=2.0 if col in (RANK, REAL) else 1.1, rx=8))
        for i in range(1, len(cols)):
            p.append(line(xs[i], ry + 8, xs[i], ry + rh - 8, color="#d8dde3", sw=1.0))
        p.append(text(xs[0] + cols[0] / 2, ry + rh / 2 + 5, name, size=16, color=col, bold=True))
        p.append(mtext(xs[1] + cols[1] / 2, ry + rh / 2 - 8, fixes, size=12, color=MUTED, lh=1.3))
        p.append(mtext(xs[2] + cols[2] / 2, ry + rh / 2 - 8, tr, size=12.5, color=INK, lh=1.3))
        p.append(mtext(xs[3] + cols[3] / 2, ry + rh / 2 - 8, ops, size=12, color=MUTED, lh=1.3))
        if name == "Порядкова": y_ord = ry + rh / 2
        if name == "Відношень": y_rat = ry + rh / 2
        ry += rh + 12

    # права дужка: розрив, який RPN перестрибує
    bx = x0 + tablew + 26
    p.append(line(bx, y_rat, bx + 16, y_rat, color=POS, sw=2.0))
    p.append(line(bx + 16, y_rat, bx + 16, y_ord, color=POS, sw=2.0))
    p.append(line(bx, y_ord, bx + 16, y_ord, color=POS, sw=2.0))
    p.append(arrow(bx + 8, y_ord - 6, bx + 8, y_rat + 6, color=POS, sw=2.0))

    p.append(mtext(x0 + tablew / 2, ry + 26,
                   "S, O, D живуть на ПОРЯДКОВІЙ шкалі — фіолетовий рядок. Множення стає законним аж на шкалі "
                   "ВІДНОШЕНЬ — зеленій.\nRPN = S · O · D мовчки перестрибує два щаблі, яких ранги не заслужили: "
                   "щоб множити, треба знати «у скільки разів»,\nа ранг знає лише «більше чи менше».",
                   size=13, color=INK, lh=1.5))

    render(os.path.join(OUT, "scales-ladder.svg"), W, H, *p,
           title="Драбина шкал: де множення законне, а де ні")


# ── Фігура: шкала частоти — це стиснутий логарифм, ще й кривий ───────────────
# Ідея: власна таблиця стандарту прив'язує ранги O до реальних частот, і ці
# частоти йдуть НЕ рівним кроком: +1 ранга — це десь ×10, а десь ×2.

def fig_occurrence_log():
    import math
    W, H = 1060, 660
    p = []

    rate = {1: 1e-7, 2: 1e-6, 3: 1e-5, 4: 1e-4, 5: 5e-4,
            6: 2e-3, 7: 1e-2, 8: 2e-2, 9: 5e-2, 10: 1e-1}

    px0, px1 = 150, 900
    py0, py1 = 95, 430           # py0 — верх (log = -1), py1 — низ (log = -7)
    LO, HI = -7.0, -1.0

    def X(o): return px0 + (o - 1) * (px1 - px0) / 9.0
    def Y(lg): return py0 + (HI - lg) * (py1 - py0) / (HI - LO)

    # сітка й вісь Y: реальна частота
    for lg in range(-7, 0):
        y = Y(lg)
        p.append(line(px0 - 8, y, px1 + 20, y, color="#e5e7eb", sw=1.0))
        p.append(text(px0 - 18, y + 4, "10%s" % _sup(lg), size=12, color=REAL, anchor="end"))
    p.append(text(px0 - 18, py0 - 34, "справжня частота", size=12.5, color=REAL,
                  anchor="end", bold=True))
    p.append(text(px0 - 18, py0 - 16, "(на одиницю)", size=11, color=MUTED, anchor="end"))

    # вісь X: ранг
    p.append(line(px0 - 8, py1 + 26, px1 + 20, py1 + 26, color=LINE, sw=1.6))
    for o in range(1, 11):
        p.append(line(X(o), py1 + 22, X(o), py1 + 30, color=LINE, sw=1.4))
        p.append(text(X(o), py1 + 50, str(o), size=13, color=RANK, bold=True))
    p.append(text((px0 + px1) / 2, py1 + 76, "ранг O — рівні кроки на папері",
                  size=13, color=RANK, bold=True))

    # крива
    pts = [(X(o), Y(math.log10(rate[o]))) for o in range(1, 11)]
    for i in range(len(pts) - 1):
        p.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=REAL, sw=2.2))
    for o in range(1, 11):
        p.append(circle(X(o), Y(math.log10(rate[o])), 5.5, fill=REAL, stroke=REAL))

    # підписи кроків ×N — над серединою кожного відрізка, через один рівень, щоб не злипались
    for o in range(1, 10):
        k = rate[o + 1] / rate[o]
        lab = "×%g" % round(k, 1)
        mx = (X(o) + X(o + 1)) / 2
        my = (Y(math.log10(rate[o])) + Y(math.log10(rate[o + 1]))) / 2
        p.append(text(mx, my - 14, lab, size=12.5, color=INK, bold=True))

    # дві однакові «+2» сходинки з різною реальністю
    def bracket(oa, ob, label, col, ybase):
        xa, xb = X(oa), X(ob)
        p.append(line(xa, ybase, xa, ybase - 10, color=col, sw=1.8))
        p.append(line(xb, ybase, xb, ybase - 10, color=col, sw=1.8))
        p.append(line(xa, ybase, xb, ybase, color=col, sw=1.8))
        p.append(text((xa + xb) / 2, ybase + 20, label, size=12.5, color=col, bold=True))

    by = py1 + 100
    bracket(2, 4, "O: 2→4  —  насправді ×100", POS, by)
    bracket(8, 10, "O: 8→10  —  насправді ×5", NEG, by)

    p.append(mtext(W / 2, py1 + 160,
                   "Той самий крок «+2» на шкалі рангів означає ×100 внизу і ×5 угорі — розбіжність у 20 разів. "
                   "Отже ранг O — навіть не інтервальна шкала:\nрівні відрізки на ній НЕ дорівнюють рівним "
                   "відрізкам у реальності. Числа взято з власної таблиці стандарту, де O=2 — це «1 на мільйон», "
                   "а O=10 — «1 на 10».\nВісім кроків рангу вкривають п'ять порядків величини — тому «O» ближче "
                   "до логарифма частоти, ніж до самої частоти.",
                   size=12.5, color=INK, lh=1.5))

    render(os.path.join(OUT, "occurrence-log.svg"), W, H, *p,
           title="Ранг частоти — стиснутий і кривий логарифм")


def _sup(n):
    m = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
         "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
    return "".join(m[c] for c in str(n))


# ── Фігура: гребінець досяжних RPN — 120 значень і 880 дірок ────────────────
# Ідея: висота зубця = скільки трійок дають це значення. Внизу тиснява,
# угорі пустеля; між 900 і 1000 немає жодного значення.

def fig_rpn_comb():
    from collections import Counter
    W, H = 1120, 500
    p = []

    prod = Counter(s * o * d for s in range(1, 11) for o in range(1, 11) for d in range(1, 11))
    vals = sorted(prod)

    ax0, ax1 = 80, 1050
    base = 330
    maxh = 190
    mx = max(prod.values())

    def X(v): return ax0 + (v / 1000.0) * (ax1 - ax0)

    # зони густини — підкладка
    for lo, hi, col in [(0, 100, "#fdecea"), (900, 1000, "#eef2fb")]:
        p.append(rect(X(lo), base - maxh - 16, X(hi) - X(lo), maxh + 16,
                      fill=col, stroke="none", sw=0, rx=4))

    # вісь
    p.append(line(ax0, base, ax1, base, color=LINE, sw=1.8))
    for v in range(0, 1001, 100):
        p.append(line(X(v), base, X(v), base + 8, color=LINE, sw=1.3))
        p.append(text(X(v), base + 26, str(v), size=11.5, color=MUTED))

    # зубці
    for v in vals:
        h = 16 + (prod[v] / mx) * (maxh - 16)
        p.append(line(X(v), base, X(v), base - h, color=RANK, sw=1.6))

    # анотації зон
    p.append(text(X(50), base - maxh - 30, "46 значень", size=12.5, color=POS, bold=True))
    p.append(text(X(50), base - maxh - 12, "тиснява", size=11, color=POS))
    p.append(text(X(950), base - maxh - 30, "1 значення", size=12.5, color=NEG, bold=True))
    p.append(text(X(950), base - maxh - 12, "пустеля", size=11, color=NEG))

    # порожнеча 900→1000
    gy = base - maxh - 52
    p.append(line(X(900), gy, X(1000), gy, color=NEG, sw=1.8))
    p.append(line(X(900), gy - 6, X(900), gy + 6, color=NEG, sw=1.8))
    p.append(line(X(1000), gy - 6, X(1000), gy + 6, color=NEG, sw=1.8))
    p.append(text(X(950), gy - 12, "жодного RPN", size=11.5, color=NEG, bold=True))

    # найвищий зубець — підпис віднесено правіше від тісного лівого кутка (там вже
    # «46 значень» / «тиснява»), щоб не сідати на них; сусідні зубці там низькі
    top = max(vals, key=lambda v: prod[v])
    p.append(text(X(top) + 90, base - maxh - 30, "RPN=60: 24 трійки", size=12, color=RANK,
                  bold=True, anchor="start"))

    p.append(text(ax0, base - maxh - 44, "висота зубця = скільки трійок (S,O,D) дають це значення",
                  size=11.5, color=MUTED, anchor="start", italic=True))

    p.append(mtext(W / 2, base + 68,
                   "Усі 120 досяжних значень RPN на відрізку 1…1000. Решта 880 цілих — недосяжні: 11 не вийде ніколи "
                   "(просте, більше за 10),\n625 = 5⁴ теж (чотири п'ятірки не вкласти у три множники ≤ 10). Шкала "
                   "«від 1 до 1000» — ілюзія: справжніх поділок 120,\nвони збиті внизу й розсіяні вгорі, а між 900 і "
                   "1000 зяє провал завширшки в десяту частину шкали.\nТому «RPN = 240» і «RPN = 200» — не сусіди на "
                   "рівномірній лінійці, а дві сходинки нерівної та щербатої драбини.",
                   size=12.5, color=INK, lh=1.5))

    render(os.path.join(OUT, "rpn-comb.svg"), W, H, *p,
           title="120 досяжних значень і 880 дірок")


# ── Фігура: одне число RPN нічого не каже про тяжкість ───────────────────────
# Ідея: RPN=60 сумісний із S=1 (нічого) і з S=10 (шкода людині) водночас.

def fig_rpn_ties():
    W, H = 1120, 608
    p = []

    cx, cy = 190, 240
    p.append(circle(cx, cy, 66, fill="#f7f4ff", stroke=RANK, sw=2.4))
    p.append(text(cx, cy - 6, "RPN", size=15, color=MUTED, bold=True))
    p.append(text(cx, cy + 22, "60", size=30, color=RANK, bold=True))
    p.append(text(cx, cy + 96, "24 різні трійки", size=12.5, color=MUTED, bold=True))
    p.append(text(cx, cy + 116, "дають це саме число", size=11.5, color=MUTED))

    rows = [
        ((10, 6, 1), "шкода людині", "часто, але ловиться миттєво", POS),
        ((10, 1, 6), "шкода людині", "рідко, ловиться так собі", POS),
        ((6, 2, 5), "втрата функції", "рідко, контроль середній", AMBER),
        ((3, 4, 5), "дрібна прикрість", "нечасто, контроль середній", INK),
        ((1, 6, 10), "жодного ефекту", "часто й зовсім невидиме", MUTED),
    ]

    bx = 420
    bw = 640
    by = 78
    bh = 68
    gap = 18
    for (S, O, D), what, note, col in rows:
        fill = "#fdecea" if col == POS else ("#fdf3e2" if col == AMBER else FILL)
        p.append(rect(bx, by, bw, bh, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(arrow(cx + 70, cy, bx - 8, by + bh / 2, color="#c9ced6", sw=1.4))
        p.append(text(bx + 16, by + 27, "S=%d" % S, size=16, color=col, bold=True, anchor="start"))
        p.append(text(bx + 16, by + 50, "O=%d  D=%d" % (O, D), size=12, color=MUTED, anchor="start"))
        p.append(text(bx + 106, by + 27, what, size=13.5, color=INK, bold=True, anchor="start"))
        p.append(text(bx + 106, by + 50, note, size=11.5, color=MUTED, anchor="start"))
        p.append(text(bx + bw - 16, by + 40, "%d·%d·%d = 60" % (S, O, D),
                      size=12, color=MUTED, anchor="end"))
        by += bh + gap

    # вертикальна дужка «тяжкість від 1 до 10»
    sx = bx - 26
    p.append(line(sx, 78, sx, by - gap, color=RANK, sw=2.0))
    p.append(line(sx, 78, sx + 10, 78, color=RANK, sw=2.0))
    p.append(line(sx, by - gap, sx + 10, by - gap, color=RANK, sw=2.0))

    p.append(mtext(W / 2, by + 26,
                   "Одне й те саме «RPN = 60» однаково сумісне з відмовою, якої ніхто не помітить (S=1), і з тією, що "
                   "калічить людину (S=10).\nЧисло не приховує тяжкість — воно її СТИРАЄ: за добутком неможливо "
                   "відновити, з яких множників він склався.\nТе саме з числами зі списку крамниці: RPN=144 дають і "
                   "{2,8,9}, і {4,6,6}, а RPN=240 — і {4,6,10}, і {3,8,10}, де S=10.\nСортуючи за RPN, команда "
                   "впорядковує саме те, що втратило сенс під час множення.",
                   size=12.5, color=INK, lh=1.5))

    render(os.path.join(OUT, "rpn-ties.svg"), W, H, *p,
           title="RPN=60 однаково сумісний із S=1 і S=10")


# ── Фігура 9: дві черги — за голим RPN і за пріоритетом дій ───────────────────
# Ідея: на тих самих трьох рядках крамниці показати, що сортування за добутком
# ставить косметичну відмову поперед тієї, що руйнує довіру, а пошук у таблиці
# пріоритету дій це виправляє. Перші два місця міняються.

def fig_ap_queue():
    W, H = 1180, 580
    p = []

    ROW_H, GAP = 92, 22
    ys = [110 + i * (ROW_H + GAP) for i in range(3)]
    LX, RX, BW = 70, 640, 470

    p.append(text(LX + BW / 2, 84, "черга за голим RPN", size=15, color=AMBER, bold=True))
    p.append(text(RX + BW / 2, 84, "черга за пріоритетом дій", size=15, color=FIELD, bold=True))

    left = [
        ("показано стару ціну з кешу", "S=4  O=6  D=10", "RPN 240", AMBER, "#fdf3e2"),
        ("суму списано двічі", "S=9  O=2  D=8", "RPN 144", POS, EFFECT),
        ("відповідь не прийшла за таймаут", "S=6  O=5  D=3", "RPN 90", MUTED, FILL),
    ]
    right = [
        ("суму списано двічі", "тяжкість 9: довіра, повернення", "AP  H", POS, EFFECT),
        ("показано стару ціну з кешу", "тяжкість 4: втрата маржі", "AP  M", AMBER, "#fdf3e2"),
        ("відповідь не прийшла за таймаут", "тяжкість 6: продаж утрачено", "AP  L", MUTED, FILL),
    ]

    def panel(x, rows):
        out = []
        for i, (mode, note, tag, col, fill) in enumerate(rows):
            y = ys[i]
            out.append(rect(x, y, BW, ROW_H, fill=fill, stroke=col, sw=1.8, rx=8))
            out.append(circle(x + 30, y + ROW_H / 2, 17, fill=BG, stroke=col, sw=1.8))
            out.append(text(x + 30, y + ROW_H / 2 + 6, str(i + 1), size=16, color=col, bold=True))
            out.append(text(x + 60, y + 36, mode, size=13.5, color=INK, bold=True, anchor="start"))
            out.append(text(x + 60, y + 62, note, size=12, color=MUTED, anchor="start"))
            out.append(text(x + BW - 16, y + ROW_H / 2 + 6, tag, size=16, color=col,
                            bold=True, anchor="end"))
        return out

    p += panel(LX, left)
    p += panel(RX, right)

    cy = [y + ROW_H / 2 for y in ys]
    p.append(arrow(LX + BW + 8, cy[0], RX - 10, cy[1], color=AMBER, sw=2.0))
    p.append(arrow(LX + BW + 8, cy[1], RX - 10, cy[0], color=POS, sw=2.4))
    p.append(arrow(LX + BW + 8, cy[2], RX - 10, cy[2], color="#c9ced6", sw=1.6))

    p.append(mtext(W / 2, 466,
                   "Ті самі три рядки, два різні впорядкування. Ліворуч добуток підняв «застарілу ціну» нагору: вона "
                   "часта (O=6) і зовсім невидима (D=10),\nі 4·6·10 = 240 перебиває 9·2·8 = 144. Праворуч пошук у "
                   "таблиці бачить тяжкість 9 і ставить «подвійне списання» першим — незалежно від того,\nяке там "
                   "рідкісне (O=2) і як погано ловиться. Перші два місця міняються, і саме ця заміна — уся користь "
                   "інструмента.\nТретій рядок не зрушив: за обома правилами він останній, тільки RPN каже «90», а "
                   "таблиця каже прямо — «дій не вимагаємо».",
                   size=12.5, color=INK, lh=1.5))

    render(os.path.join(OUT, "ap-queue.svg"), W, H, *p,
           title="Дві черги на тих самих даних: добуток проти таблиці")


# ── Фігура 10: уся політика в п'яти пластинах — тяжкість тримає ворота ────────
# Ідея: розгорнути таблицю пріоритету дій у п'ять пластин за смугами тяжкості.
# Видно те, чого не видно в коді: верхня пластина майже суцільно червона, нижня
# суцільно сіра. Тяжкість вирішує СПОЧАТКУ, частота й виявність — лише всередині.

_D_BANDS = ((7, 10), (5, 6), (2, 4), (1, 1))
_O_BANDS = ((8, 10), (6, 7), (4, 5), (2, 3), (1, 1))
_S_BANDS = ((9, 10), (7, 8), (4, 6), (2, 3), (1, 1))
_POLICY = {
    (9, 10): {(8, 10): "HHHH", (6, 7): "HHHH", (4, 5): "HHHH", (2, 3): "HHHM", (1, 1): "MMLL"},
    (7, 8):  {(8, 10): "HHHH", (6, 7): "HHHM", (4, 5): "HMMM", (2, 3): "MMLL", (1, 1): "LLLL"},
    (4, 6):  {(8, 10): "HHMM", (6, 7): "MMML", (4, 5): "MLLL", (2, 3): "LLLL", (1, 1): "LLLL"},
    (2, 3):  {(8, 10): "MMLL", (6, 7): "LLLL", (4, 5): "LLLL", (2, 3): "LLLL", (1, 1): "LLLL"},
    (1, 1):  {(8, 10): "LLLL", (6, 7): "LLLL", (4, 5): "LLLL", (2, 3): "LLLL", (1, 1): "LLLL"},
}
_CELLCOL = {"H": (EFFECT, POS), "M": ("#fdf3e2", AMBER), "L": (FILL, "#c9ced6")}


def _band_row(bands, v):
    for i, (lo, hi) in enumerate(bands):
        if lo <= v <= hi:
            return i
    raise ValueError(v)


def fig_ap_plates():
    W, H = 1240, 600
    p = []

    CW, CH = 40, 34
    GX, GY = 176, 132
    PW = CW * 4
    STEP = PW + 44

    # позначені рядки крамниці: (S, O, D, підпис)
    marks = [(9, 2, 8, "P-02  подвійне списання"),
             (4, 6, 10, "P-03  застаріла ціна"),
             (6, 5, 3, "P-01  таймаут шлюзу")]

    # підписи смуг частоти — ліворуч від першої пластини
    p.append(text(GX - 22, GY - 14, "частота O", size=11.5, color=MUTED, anchor="end"))
    for r, (lo, hi) in enumerate(_O_BANDS):
        label = "%d–%d" % (lo, hi) if lo != hi else str(lo)
        p.append(text(GX - 22, GY + r * CH + CH / 2 + 4, label, size=11.5,
                      color=MUTED, anchor="end"))

    callouts = {}
    for s, o, d, name in marks:
        callouts.setdefault(_band_row(_S_BANDS, s), []).append(name)

    for pi, sb in enumerate(_S_BANDS):
        x = GX + pi * STEP
        lo, hi = sb
        head = "S = %d–%d" % (lo, hi) if lo != hi else "S = %d" % lo
        p.append(text(x + PW / 2, GY - 42, head, size=13.5, color=INK, bold=True))
        for c, (dlo, dhi) in enumerate(_D_BANDS):
            lab = "%d–%d" % (dlo, dhi) if dlo != dhi else str(dlo)
            p.append(text(x + c * CW + CW / 2, GY - 14, lab, size=11, color=MUTED))
        for r, ob in enumerate(_O_BANDS):
            cells = _POLICY[sb][ob]
            for c in range(4):
                ch = cells[c]
                fill, col = _CELLCOL[ch]
                p.append(rect(x + c * CW, GY + r * CH, CW, CH, fill=fill, stroke=col,
                              sw=1.2, rx=3))
                p.append(text(x + c * CW + CW / 2, GY + r * CH + CH / 2 + 5, ch,
                              size=13, color=col, bold=True))

    p.append(text(GX + 2 * STEP + PW / 2, GY - 66, "виявність D — колонки кожної пластини",
                  size=11.5, color=MUTED))

    # обвести клітини трьох рядків крамниці
    for s, o, d, _ in marks:
        pi = _band_row(_S_BANDS, s)
        r = _band_row(_O_BANDS, o)
        c = _band_row(_D_BANDS, d)
        x = GX + pi * STEP + c * CW
        y = GY + r * CH
        p.append(rect(x - 3, y - 3, CW + 6, CH + 6, fill="none", stroke=INK, sw=2.4, rx=5))

    for pi, names in callouts.items():
        x = GX + pi * STEP + PW / 2
        p.append(mtext(x, GY + 5 * CH + 26, names, size=11, color=INK, lh=1.5))

    p.append(mtext(W / 2, 400,
                   "Уся таблиця в п'яти пластинах — по одній на смугу тяжкості. Кожна пластина: рядки — смуги частоти, "
                   "колонки — смуги виявності.\nВидно те, чого не видно у формулі: пластина S=9–10 майже суцільно "
                   "червона, пластина S=1 суцільно сіра. Тяжкість тримає ворота — вона\nвирішує СПОЧАТКУ, а частота й "
                   "виявність рухають пріоритет лише всередині своєї пластини й ніколи не виносять рядок за її межі.\n"
                   "Обведені три клітини — рядки крамниці. «Подвійне списання» сидить на червоній пластині й дістає H, "
                   "хоч воно й рідкісне;\n«застаріла ціна» — на середній, і найгірша можлива виявність (D=10) підіймає "
                   "її лише до M. Саме тому черга виходить правильна.\nСмуги (9–10, 7–8, 4–6 …) — не лінощі укладачів: "
                   "розрізняти сусідні ранги всередині смуги вхідні дані не дають права.",
                   size=12.5, color=INK, lh=1.5))

    render(os.path.join(OUT, "ap-plates.svg"), W, H, *p,
           title="Таблиця пріоритету дій: тяжкість вирішує спочатку")


if __name__ == "__main__":
    fig_chain()
    fig_axes_rpn()
    fig_procedure()
    fig_timeline()
    fig_substitution()
    fig_scales_ladder()
    fig_occurrence_log()
    fig_rpn_comb()
    fig_rpn_ties()
    fig_ap_queue()
    fig_ap_plates()
    print("OK figs")
