# -*- coding: utf-8 -*-
"""Фігури до статті «Порядкові числа (ординали)».
Запуск:  python figs.py   → пише SVG у ./img/
  reorder     — та сама ℕ, перевпорядкована → довший ординал (ω·2), розмір той самий
  ladder      — драбина ординалів: наступники (плоскі) vs границі (зелені)
  von_neumann — ординал як множина всіх менших; наступник α∪{α}; порядок = належність
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#eaf7ef"
REDFILL   = "#fdecea"
BLUEFILL  = "#eaf0fd"
ROW       = "#f4f6f8"


def bracket(x0, x1, y, color=MUTED, sw=1.6, drop=8):
    """Горизонтальна дужка [ ___ ] під відрізком (кінці загнуті вниз)."""
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (x0, y - drop, x0, y, x1, y, x1, y - drop, color, sw))


# ── 1. Та сама множина, інша форма порядку ───────────────────────────────────
def fig_reorder():
    W, H = 1000, 490
    f = [text(W / 2, 34, "Та сама множина, інший порядок — інший ординал", size=19, bold=True),
         text(W / 2, 58, "перевпорядкуй ℕ як «спершу парні, потім непарні»: розмір той самий, а форма порядку довша",
              size=12.5, color=MUTED, italic=True)]

    # ── верхня лінія: натуральний порядок → ω ──
    f.append(text(400, 112, "Натуральний порядок  0, 1, 2, 3, …", size=14.5, bold=True, color=NEG))
    yt = 152
    f.append(line(90, yt, 740, yt, color=INK, sw=1.7))
    for x, lab in zip([130, 205, 280, 355, 430, 505], ["0", "1", "2", "3", "4", "5"]):
        f.append(circle(x, yt, 7, fill=BG, stroke=INK, sw=1.5))
        f.append(text(x, yt - 20, lab, size=13))
    f.append(text(580, yt + 6, "…", size=20, bold=True, color=MUTED))
    box, w, h = textbox(885, yt, "ω", size=18, bold=True, fill=BLUEFILL, stroke=NEG, color=NEG, min_w=74)
    f.append(box)
    f.append(text(95, yt + 34, "у кожного елемента — скінченно багато попередників",
                  size=11.5, color=MUTED, italic=True, anchor="start"))

    # ── нижня лінія: парні, потім непарні → ω·2 ──
    f.append(text(400, 250, "Те саме, але «спершу всі парні, тоді всі непарні»", size=14.5, bold=True, color=FIELD))
    yb = 330
    f.append(line(90, yb, 740, yb, color=INK, sw=1.7))
    # блок парних
    for x, lab in zip([130, 200, 270, 340], ["0", "2", "4", "6"]):
        f.append(circle(x, yb, 7, fill=BG, stroke=INK, sw=1.5))
        f.append(text(x, yb - 20, lab, size=13))
    f.append(text(398, yb + 6, "…", size=20, bold=True, color=MUTED))
    # блок непарних
    odds = [(512, "1"), (582, "3"), (652, "5")]
    for i, (x, lab) in enumerate(odds):
        first = (i == 0)
        f.append(circle(x, yb, 10 if first else 7,
                        fill=(GREENFILL if first else BG),
                        stroke=(FIELD if first else INK), sw=(2.6 if first else 1.5)))
        f.append(text(x, yb - 20, lab, size=13, bold=first, color=(FIELD if first else INK)))
    f.append(text(710, yb + 6, "…", size=20, bold=True, color=MUTED))
    box2, w2, h2 = textbox(885, yb, "ω·2", size=18, bold=True, fill=GREENFILL, stroke=FIELD, color=FIELD, min_w=74)
    f.append(box2)
    # виноска до «1»: перед ним ціле ω парних
    f.append(text(512, 296, "перед «1» стоїть ціле ω парних", size=11.5, bold=True, color=FIELD))
    f.append(arrow(512, 312, 512, yb - 12, color=FIELD, sw=1.8))
    # дужки: копія ω + копія ω
    f.append(bracket(128, 400, yb + 26, color=NEG, sw=1.5))
    f.append(text(264, yb + 48, "копія ω", size=11.5, bold=True, color=NEG))
    f.append(bracket(500, 712, yb + 26, color=NEG, sw=1.5))
    f.append(text(606, yb + 48, "друга копія ω", size=11.5, bold=True, color=NEG))

    # синтез унизу
    f.append(mtext(W / 2, 442,
                   ["Точок стільки ж — уся ℕ, розмір ℵ₀ (зліченна множина).",
                    "Змінилася лише ФОРМА порядку: тепер є елемент із нескінченністю попередників."],
                   size=12.5, color=INK))

    render(os.path.join(IMG, "reorder.svg"), W, H, *f)


# ── 2. Драбина ординалів: наступники й границі ───────────────────────────────
def fig_ladder():
    W, H = 1040, 430
    f = [text(W / 2, 34, "Драбина ординалів: наступники й границі", size=19, bold=True),
         text(W / 2, 58, "кожен ординал — або 0, або наступник β+1 (є найбільший менший), або границя (найбільшого меншого немає)",
              size=12, color=MUTED, italic=True)]

    ay = 205
    f.append(line(70, ay, 965, ay, color=INK, sw=1.7))
    f.append(arrow(945, ay, 978, ay, color=INK, sw=1.7))

    def succ(x, lab):
        f.append(circle(x, ay, 6, fill=BG, stroke=INK, sw=1.5))
        f.append(text(x, ay - 18, lab, size=12))

    def dots(x):
        f.append(text(x, ay + 6, "…", size=20, bold=True, color=MUTED))

    def limit(x, lab):
        f.append(circle(x, ay, 9, fill=GREENFILL, stroke=FIELD, sw=2.6))
        f.append(text(x, ay - 20, lab, size=13.5, bold=True, color=FIELD))
        f.append(arrow(x, ay + 42, x, ay + 13, color=FIELD, sw=1.7))
        f.append(text(x, ay + 60, "гранична", size=10.5, bold=True, color=FIELD))

    # скінченні
    for x, lab in [(100, "0"), (150, "1"), (200, "2"), (250, "3")]:
        succ(x, lab)
    dots(292)
    # ω — перша границя
    limit(360, "ω")
    # наступники ω
    for x, lab in [(422, "ω+1"), (486, "ω+2")]:
        succ(x, lab)
    dots(534)
    limit(610, "ω·2")
    dots(680)
    limit(772, "ω²")
    dots(848)
    f.append(text(910, ay - 18, "ω^ω, ε₀, …", size=12, color=MUTED, italic=True))

    # анотація «немає ω−1» над ω (лінія від хвоста скінченних до ω, обходить напис)
    f.append(text(300, 126, "щоб дістатися ω, треба зібрати ВСЮ низку 0,1,2,… — «ω−1» не існує",
                  size=11.5, bold=True, color=FIELD, anchor="start"))
    f.append(('<path d="M 296 136 Q 326 168 350 198" fill="none" stroke="%s" '
              'stroke-width="1.5" stroke-dasharray="4,4" marker-end="url(#arrow)"/>' % FIELD))
    # анотація наступника — праворуч від ω+1, стрілка діагонально в кружок (повз напис)
    f.append(text(452, 150, "наступник: +1 крок,", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(452, 166, "найбільший менший — ω", size=11, bold=True, color=NEG, anchor="start"))
    f.append(arrow(460, 172, 432, 198, color=NEG, sw=1.5))

    # синтез унизу
    f.append(mtext(W / 2, 322,
                   ["Крок уперед завжди дає наступника. Але щоб перескочити за ВСЮ нескінченну низку,",
                    "потрібен новий сорт числа — границя, яку видно лише «знизу», зібравши все, що менше."],
                   size=12.5, color=INK))
    # легенда
    f.append(circle(360, 370, 6, fill=GREENFILL, stroke=FIELD, sw=2.4))
    f.append(text(374, 374, "гранична (попередника нема)", size=11.5, color=INK, anchor="start"))
    f.append(circle(620, 370, 6, fill=BG, stroke=INK, sw=1.5))
    f.append(text(634, 374, "наступник (є найбільший менший)", size=11.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "ladder.svg"), W, H, *f)


# ── 3. Ординал як множина всіх менших ────────────────────────────────────────
def fig_von_neumann():
    W, H = 1040, 440
    f = [text(W / 2, 34, "Ординал — це множина всіх менших за нього", size=19, bold=True),
         text(W / 2, 58, "0 = ∅;   наступник  α+1 = α ∪ {α};   «менше» — це «належить»:  α < β  ⟺  α ∈ β",
              size=12.5, color=MUTED, italic=True)]

    # верхній ряд — скінченні
    top = [(70, 130, "0 = ∅"),
           (220, 140, "1 = {0}"),
           (380, 170, "2 = {0, 1}"),
           (570, 200, "3 = {0, 1, 2}")]
    yt, ht = 96, 60
    prev_right = None
    for x, w, s in top:
        f.append(fitbox(x, yt, w, ht, s, size=13.5, fill=ROW, stroke=LINE, color=INK))
        if prev_right is not None:
            f.append(arrow(prev_right + 4, yt + ht / 2, x - 6, yt + ht / 2, color=INK, sw=1.6))
        prev_right = x + w
    f.append(arrow(prev_right + 4, yt + ht / 2, prev_right + 40, yt + ht / 2, color=INK, sw=1.6))
    f.append(text(prev_right + 58, yt + ht / 2 + 5, "…", size=20, bold=True, color=MUTED, anchor="start"))
    # ланцюг належності під верхнім рядом
    f.append(text(W / 2, yt + ht + 34, "0 ∈ 1 ∈ 2 ∈ 3 ∈ …    (тобто  0 < 1 < 2 < 3 < …)",
                  size=13, bold=True, color=NEG))

    # нижній ряд — ω і його наступник
    yb, hb = 250, 96
    f.append(fitbox(120, yb, 350, hb,
                    "ω = {0, 1, 2, 3, …}\n\nперша границя:\nусі скінченні разом",
                    size=13.5, fill=GREENFILL, stroke=FIELD, color=INK))
    f.append(arrow(478, yb + hb / 2, 556, yb + hb / 2, color=INK, sw=1.7))
    f.append(text(517, yb + hb / 2 - 10, "α∪{α}", size=11.5, bold=True, color=NEG))
    f.append(fitbox(564, yb, 380, hb,
                    "ω+1 = ω ∪ {ω} = {0, 1, 2, …, ω}\n\nнаступник ω:\nдокинули в множину саме ω",
                    size=13.5, fill=BLUEFILL, stroke=NEG, color=INK))

    # підсумковий рядок
    f.append(text(W / 2, 408,
                  "Наступник — «докинь себе». Границя — об'єднай усе нижче:  ω = 0 ∪ 1 ∪ 2 ∪ …",
                  size=13, bold=True, color=INK))

    render(os.path.join(IMG, "von-neumann.svg"), W, H, *f)


# ── 4. Як народилося ω: похідні множини, що не кінчаються ─────────────────────
def fig_derived():
    W, H = 1060, 430
    f = [text(W / 2, 30, "Як народилося ω: похідні множини, що не кінчаються", size=19, bold=True),
         text(W / 2, 54, "Кантор лічив кроки «лишити самі граничні точки». Коли кроки не уриваються, показник тікає за всі скінченні числа.",
              size=12, color=MUTED, italic=True)]

    # ── перший рід: похідна колись порожніє ──
    f.append(text(72, 96, "Перший рід — похідна кінець кінцем порожніє", size=14, bold=True, color=NEG, anchor="start"))
    yt = 150
    b1, w1, h1 = textbox(150, yt, "P", size=13.5, min_w=54, fill=ROW)
    b2, w2, h2 = textbox(332, yt, "P′ = {0}", size=13.5, min_w=54, fill=ROW)
    b3, w3, h3 = textbox(512, yt, "P″ = ∅", size=13.5, min_w=54, fill=REDFILL, stroke=POS, color=POS)
    f += [b1, b2, b3]
    f.append(arrow(150 + w1 / 2 + 5, yt, 332 - w2 / 2 - 6, yt, color=INK, sw=1.6))
    f.append(arrow(332 + w2 / 2 + 5, yt, 512 - w3 / 2 - 6, yt, color=INK, sw=1.6))
    f.append(text(512, yt - h3 / 2 - 9, "кінець", size=10.5, bold=True, color=POS))
    f.append(text(612, yt - 5, "за скінченне число кроків похідна порожніє —", size=11.5, color=MUTED, italic=True, anchor="start"))
    f.append(text(612, yt + 13, "показник лишається звичайним натуральним числом.", size=11.5, color=MUTED, italic=True, anchor="start"))
    f.append(text(72, 198, "напр.: точки 1, ½, ⅓, ¼, … збігаються до 0, тож P′ = {0}, а наступна похідна вже порожня.",
                  size=11.5, color=MUTED, italic=True, anchor="start"))

    # роздільник
    f.append(line(72, 228, 988, 228, color=MUTED, sw=1.0, dash="5,5"))

    # ── другий рід: похідна не порожніє ніколи ──
    f.append(text(72, 266, "Другий рід — похідна не порожніє НІКОЛИ", size=14, bold=True, color=FIELD, anchor="start"))
    ay = 340
    f.append(line(80, ay, 992, ay, color=INK, sw=1.7))
    f.append(arrow(972, ay, 1006, ay, color=INK, sw=1.7))

    def fin(x, lab):
        f.append(circle(x, ay, 6, fill=BG, stroke=INK, sw=1.5))
        f.append(text(x, ay - 16, lab, size=12.5))

    def inf(x, lab):
        f.append(circle(x, ay, 9, fill=GREENFILL, stroke=FIELD, sw=2.6))
        f.append(text(x, ay - 18, lab, size=13, bold=True, color=FIELD))

    for x, lab in [(115, "P"), (192, "P′"), (269, "P″"), (346, "P‴")]:
        fin(x, lab)
    f.append(text(400, ay + 6, "…", size=20, bold=True, color=MUTED))
    for x, lab in [(486, "P^∞"), (602, "P^(∞+1)"), (714, "P^(∞+2)")]:
        inf(x, lab)
    f.append(text(775, ay + 6, "…", size=20, bold=True, color=MUTED))
    inf(872, "P^(∞·2)")
    f.append(text(942, ay + 6, "…", size=20, bold=True, color=MUTED))

    # анотація до першого трансфінітного показника
    f.append(text(360, 282, "показник вискочив за ВСІ скінченні —", size=11.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(360, 298, "його довелося ВИГАДАТИ", size=11.5, bold=True, color=FIELD, anchor="start"))
    f.append(('<path d="M 446 303 Q 460 316 481 331" fill="none" stroke="%s" '
              'stroke-width="1.6" marker-end="url(#arrow)"/>' % FIELD))

    # дужка під трансфінітним хвостом
    f.append(bracket(456, 906, ay + 24, color=FIELD, sw=1.5))
    f.append(text(681, ay + 46, "ці показники — майбутні ординали; символ ∞ Кантор 1883 р. переназве на ω",
                  size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, "derived.svg"), W, H, *f)


# ── 5. Додавання: 1+ω=ω (всмоктування) vs ω+1>ω (новий останній) ──────────────
def fig_add_asym():
    W, H = 1020, 452
    f = [text(W / 2, 34, "Додавання ординалів: склей шеренги — і дивись на форму", size=19, bold=True),
         text(W / 2, 58, "точка спереду всмоктується (1+ω = ω); точка ззаду додає новий останній елемент (ω+1 > ω)",
              size=12, color=MUTED, italic=True)]

    # ── Рядок A: 1 + ω = ω ──
    f.append(text(78, 112, "1 + ω   —   одна точка ПЕРЕД усією ω", size=14.5, bold=True, color=NEG, anchor="start"))
    ya = 162
    f.append(line(150, ya, 705, ya, color=INK, sw=1.7))
    f.append(circle(150, ya, 10, fill=REDFILL, stroke=POS, sw=2.6))
    f.append(text(150, ya - 20, "1", size=13, bold=True, color=POS))
    for x, lab in zip([232, 302, 372, 442, 512], ["0", "1", "2", "3", "4"]):
        f.append(circle(x, ya, 7, fill=BG, stroke=INK, sw=1.5))
        f.append(text(x, ya - 20, lab, size=13))
    f.append(text(578, ya + 6, "…", size=20, bold=True, color=MUTED))
    f.append(mtext(150, ya + 34, ["всмоктується —", "стає «новим 0»"], size=11, color=POS, bold=True))
    f.append(arrow(720, ya, 838, ya, color=INK, sw=1.6))
    box, w, h = textbox(918, ya, "= ω", size=18, bold=True, fill=BLUEFILL, stroke=NEG, color=NEG, min_w=96)
    f.append(box)

    # ── Рядок B: ω + 1 = ω+1 > ω ──
    f.append(text(78, 276, "ω + 1   —   одна точка ПІСЛЯ усієї ω", size=14.5, bold=True, color=FIELD, anchor="start"))
    yb = 340
    f.append(line(120, yb, 700, yb, color=INK, sw=1.7))
    for x, lab in zip([160, 230, 300, 370, 440], ["0", "1", "2", "3", "4"]):
        f.append(circle(x, yb, 7, fill=BG, stroke=INK, sw=1.5))
        f.append(text(x, yb - 20, lab, size=13))
    f.append(text(508, yb + 6, "…", size=20, bold=True, color=MUTED))
    f.append(circle(662, yb, 10, fill=GREENFILL, stroke=FIELD, sw=2.6))
    f.append(text(662, yb - 20, "остання", size=11.5, bold=True, color=FIELD))
    f.append(mtext(662, yb + 34, ["новий найбільший —", "у ω його не було"], size=11, color=FIELD, bold=True))
    f.append(arrow(760, yb - 30, 838, yb - 8, color=INK, sw=1.6))
    box2, w2, h2 = textbox(918, yb, "= ω+1 > ω", size=16, bold=True, fill=GREENFILL, stroke=FIELD, color=FIELD, min_w=96)
    f.append(box2)

    render(os.path.join(IMG, "add-asym.svg"), W, H, *f)


# ── 6. Множення: 2·ω=ω vs ω·2=ω+ω (лексичний добуток) ─────────────────────────
def fig_mult_asym():
    W, H = 1020, 470
    f = [text(W / 2, 34, "Множення ординалів: заміни кожну точку цілою копією", size=19, bold=True),
         text(W / 2, 58, "домовленість:  α · β = β копій α  (правий множник — СКІЛЬКИ копій, лівий — ЧОГО копії)",
              size=12.5, color=MUTED, italic=True)]

    # ── Рядок A: 2 · ω = ω → ω блоків по дві точки ──
    f.append(text(78, 118, "2 · ω   =   ω копій двійки", size=14.5, bold=True, color=NEG, anchor="start"))
    ya = 172
    f.append(line(120, ya, 700, ya, color=INK, sw=1.7))
    for bx in [150, 232, 314, 396, 478]:
        f.append(circle(bx - 9, ya, 6.5, fill=REDFILL, stroke=POS, sw=1.8))
        f.append(circle(bx + 9, ya, 6.5, fill=REDFILL, stroke=POS, sw=1.8))
        f.append(text(bx, ya + 30, "2", size=11, color=POS, bold=True))
    f.append(text(560, ya + 6, "…", size=20, bold=True, color=MUTED))
    f.append(text(78, ya - 30, "нескінченно багато крихітних блоків → перенумеруй у суцільну ω",
                  size=11, color=MUTED, italic=True, anchor="start"))
    f.append(arrow(715, ya, 833, ya, color=INK, sw=1.6))
    b1, _, _ = textbox(913, ya, "= ω", size=18, bold=True, fill=BLUEFILL, stroke=NEG, color=NEG, min_w=110)
    f.append(b1)

    # ── Рядок B: ω · 2 = ω + ω → дві копії ω ──
    f.append(text(78, 292, "ω · 2   =   дві копії ω", size=14.5, bold=True, color=FIELD, anchor="start"))
    yb = 356
    f.append(line(110, yb, 700, yb, color=INK, sw=1.7))
    for x, lab in zip([150, 210, 270, 330], ["0", "1", "2", "3"]):
        f.append(circle(x, yb, 7, fill=BG, stroke=INK, sw=1.5))
        f.append(text(x, yb - 18, lab, size=12))
    f.append(text(378, yb + 6, "…", size=20, bold=True, color=MUTED))
    seconds = [(470, "0′"), (530, "1′"), (590, "2′")]
    for i, (x, lab) in enumerate(seconds):
        first = (i == 0)
        f.append(circle(x, yb, 10 if first else 7,
                        fill=(GREENFILL if first else BG),
                        stroke=(FIELD if first else INK), sw=(2.6 if first else 1.5)))
        f.append(text(x, yb - 18, lab, size=12, bold=first, color=(FIELD if first else INK)))
    f.append(text(648, yb + 6, "…", size=20, bold=True, color=MUTED))
    f.append(bracket(148, 372, yb + 26, color=NEG, sw=1.5))
    f.append(text(260, yb + 48, "копія ω", size=11.5, bold=True, color=NEG))
    f.append(bracket(458, 660, yb + 26, color=NEG, sw=1.5))
    f.append(text(559, yb + 48, "друга копія ω", size=11.5, bold=True, color=NEG))
    f.append(text(520, yb - 44, "перед 0′ — ціле ω", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(arrow(520, yb - 34, 476, yb - 12, color=FIELD, sw=1.6))
    f.append(arrow(715, yb, 833, yb, color=INK, sw=1.6))
    b2, _, _ = textbox(913, yb, "= ω+ω > ω", size=15.5, bold=True, fill=GREENFILL, stroke=FIELD, color=FIELD, min_w=110)
    f.append(b2)

    render(os.path.join(IMG, "mult-asym.svg"), W, H, *f)


# ── 7. Канторова нормальна форма й стеля ε₀ ───────────────────────────────────
def fig_cnf_tower():
    W, H = 1060, 486
    f = [text(W / 2, 34, "Канторова нормальна форма й стеля ε₀", size=19, bold=True),
         text(W / 2, 58, "ординал за основою ω — як число за основою 10; вежа степенів упирається в нерухому точку",
              size=12, color=MUTED, italic=True)]

    f.append(line(560, 82, 560, 456, color=LINE, sw=1.2, dash="4,5"))

    # ── ЛІВОРУЧ: позиційний запис ──
    f.append(text(70, 104, "Позиційний запис за основою ω", size=14.5, bold=True, color=INK, anchor="start"))
    f.append(text(70, 140, "2026  =  10³·2 + 10²·0 + 10·2 + 6", size=13, color=MUTED, anchor="start"))
    f.append(text(70, 158, "(розряди — степені 10, цифри — скінченні)", size=10.5, color=MUTED, italic=True, anchor="start"))
    yE = 214
    f.append(text(70, yE, "α  =  ω^ω·2 + ω³·5 + ω·7 + 4", size=17, bold=True, color=INK, anchor="start"))
    f.append(text(70, yE + 40, "показники:  ω > 3 > 1 > 0", size=12.5, bold=True, color=NEG, anchor="start"))
    f.append(text(70, yE + 60, "СТРОГО спадають — інакше молодший розряд", size=11, color=NEG, anchor="start"))
    f.append(text(70, yE + 76, "всмоктався б:  ω^мале + ω^велике = ω^велике", size=11, color=NEG, anchor="start"))
    f.append(text(70, yE + 108, "цифри:  2, 5, 7, 4", size=12.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(70, yE + 128, "скінченні — бо  ω^β·ω = ω^(β+1)", size=11, color=FIELD, anchor="start"))
    f.append(fitbox(70, yE + 150, 456, 44,
                    "нижче ε₀ показники самі менші за α → запис зводиться до скінченного дерева чисел",
                    size=11.5, fill=ROW, stroke=LINE, color=INK))

    # ── ПРАВОРУЧ: вежа до ε₀ ──
    cx = 810
    f.append(text(cx, 104, "Вежа степенів  →  ε₀", size=14.5, bold=True, color=INK))
    for y, lab in [(430, "ω"), (388, "ω^ω"), (346, "ω^ω^ω"), (304, "ω^ω^ω^ω")]:
        f.append(text(cx - 40, y, lab, size=14, bold=True, color=INK))
    f.append(text(cx - 40, 268, "⋮", size=20, bold=True, color=MUTED))
    f.append(arrow(cx + 78, 436, cx + 78, 250, color=FIELD, sw=1.8))
    f.append(text(cx + 92, 350, "sup усієї вежі", size=11.5, bold=True, color=FIELD, anchor="start"))
    b, _, _ = textbox(cx, 224, "ε₀ = ω^ε₀", size=17, bold=True, fill=GREENFILL, stroke=FIELD, color=INK, min_w=150)
    f.append(b)
    f.append(text(cx, 176, "перша нерухома точка  α = ω^α", size=12, bold=True, color=FIELD))
    f.append(fitbox(cx - 150, 130, 300, 30,
                    "тут запис за основою ω кусає власний хвіст", size=11.5, fill=ROW, stroke=LINE, color=INK))

    render(os.path.join(IMG, "cnf-tower.svg"), W, H, *f)


# ── 8. Ядро доказу Ґудстейна: число вгору, ординал-тінь униз ──────────────────
def fig_goodstein_tracks():
    W, H = 1180, 560
    f = [text(W / 2, 34, "Ядро доказу: число летить угору, ординал-тінь строго спадає", size=19, bold=True),
         text(W / 2, 58, "послідовність Ґудстейна від 4 — і поряд її тінь: заміни основу на ω, дістанеш ординал у КНФ, що меншає щокроку",
              size=12, color=MUTED, italic=True)]

    steps = [
        (150, "4",  "ω^ω"),
        (400, "26", "ω²·2 + ω·2 + 2"),
        (650, "41", "ω²·2 + ω·2 + 1"),
        (880, "60", "ω²·2 + ω·2"),
    ]
    xf = 1090  # стовпчик нуля

    # верхня стрічка — значення Ґудстейна (натуральне число, вибух)
    f.append(text(60, 104, "Число Ґудстейна — натуральне, РОСТЕ вибухово", size=13.5, bold=True, color=POS, anchor="start"))
    yt = 150
    for x, val, _ in steps:
        f.append(textbox(x, yt, val, size=15, bold=True, fill=REDFILL, stroke=POS, color=POS, min_w=64)[0])
    f.append(arrow(965, yt, 1040, yt, color=POS, sw=1.9))
    f.append(text(1000, yt - 17, "… пік 3·2⁴⁰²⁶⁵³²¹⁰−1 …", size=10.5, color=POS, italic=True))
    f.append(textbox(xf, yt, "0", size=15, bold=True, fill=ROW, stroke=INK, min_w=64)[0])

    # середня плашка — дві операції кроку
    f.append(fitbox(150, 222, 890, 56,
                    "щокроку тінь робить дві речі:\n① основа n→n+1 — ординал НЕ змінюється (і там, і там основа стає ω)     ② відняти 1 — ординал строго меншає",
                    size=12.5, fill=BLUEFILL, stroke=NEG, color=INK, bold=True))

    # нижня стрічка — ординал-тінь (строго спадає)
    f.append(text(60, 324, "Ординал-тінь (канторова нормальна форма) — СТРОГО СПАДАЄ", size=13.5, bold=True, color=FIELD, anchor="start"))
    yb = 372
    prev_right = None
    for x, _, ordn in steps:
        b, w, h = textbox(x, yb, ordn, size=13, bold=True, fill=GREENFILL, stroke=FIELD, color=INK, min_w=64)
        f.append(b)
        if prev_right is not None:
            f.append(text((prev_right + x - w / 2) / 2, yb + 5, ">", size=17, bold=True, color=FIELD))
        prev_right = x + w / 2
    f.append(arrow(965, yb, 1040, yb, color=FIELD, sw=1.9))
    f.append(text(1000, yb - 17, "… усе < ω^ω …", size=10.5, color=FIELD, italic=True))
    f.append(textbox(xf, yb, "0", size=15, bold=True, fill=ROW, stroke=INK, min_w=64)[0])

    # синтез унизу
    f.append(mtext(W / 2, 462,
                   ["Число вільне рости хоч до небес. Але тінь — ординал, а ординали не спадають вічно (повне впорядкування):",
                    "строго спадна низка ординалів завжди скінченна. Тож і кроків скінченно — послідовність мусить дійти 0."],
                   size=12.5, color=INK))
    render(os.path.join(IMG, "goodstein-tracks.svg"), W, H, *f)


# ── 9. Гра в Гідру: рубаєш голову — виростають копії, а тінь спадає ───────────
def fig_hydra():
    W, H = 1080, 520
    f = [text(W / 2, 34, "Споріднене диво: гра в Гідру (Кірбі–Періс, 1982)", size=19, bold=True),
         text(W / 2, 58, "рубаєш голову — Гідра відрощує цілі копії гілки; та сама ординал-тінь строго спадає, тож Геракл завжди перемагає",
              size=12, color=MUTED, italic=True)]

    def head(x, y):
        return circle(x, y, 7, fill=POS, stroke=POS, sw=1.8)

    def dot(x, y, green=False):
        return circle(x, y, 7, fill=(GREENFILL if green else BG),
                      stroke=(FIELD if green else INK), sw=(2.4 if green else 1.8))

    # ── ліворуч: до удару ──
    cx = 235
    f.append(text(cx, 108, "до удару", size=13.5, bold=True))
    ry, ay = 360, 278
    h1x, h2x, hy = cx - 48, cx + 48, 198
    f.append(line(cx, ry, cx, ay, color=INK, sw=1.8))
    f.append(line(cx, ay, h1x, hy, color=INK, sw=1.8))
    f.append(line(cx, ay, h2x, hy, color=INK, sw=1.8))
    f.append(dot(cx, ry)); f.append(text(cx + 15, ry + 4, "корінь", size=11, color=MUTED, anchor="start"))
    f.append(dot(cx, ay)); f.append(text(cx - 15, ay + 4, "a", size=11.5, italic=True, color=MUTED, anchor="end"))
    f.append(head(h1x, hy)); f.append(head(h2x, hy))
    f.append(text(h2x + 4, hy - 12, "голова", size=10.5, color=POS, anchor="middle"))
    # позначка удару по лівій голові
    f.append(line(h1x - 13, hy - 9, h1x + 13, hy + 9, color=POS, sw=2.4))
    f.append(text(h1x - 20, hy + 4, "рубаємо", size=10.5, bold=True, color=POS, anchor="end"))
    f.append(textbox(cx, 424, "тінь = ω²", size=15, bold=True, fill=GREENFILL, stroke=FIELD, color=INK, min_w=96)[0])

    # ── стрілка переходу ──
    f.append(arrow(410, 300, 560, 300, color=INK, sw=2.0))
    f.append(text(485, 282, "рубаєш 1 голову —", size=11.5, bold=True, anchor="middle"))
    f.append(text(485, 322, "виростає n копій гілки", size=11.5, bold=True, color=FIELD, anchor="middle"))
    f.append(text(485, 338, "(тут крок n = 1)", size=11.5, bold=True, color=FIELD, anchor="middle"))

    # ── праворуч: після удару ──
    cx2 = 780
    f.append(text(cx2, 108, "після удару", size=13.5, bold=True))
    a1x, a2x, ay2 = cx2 - 58, cx2 + 58, 278
    f.append(line(cx2, ry, a1x, ay2, color=INK, sw=1.8))
    f.append(line(cx2, ry, a2x, ay2, color=FIELD, sw=2.6))
    f.append(line(a1x, ay2, a1x, hy, color=INK, sw=1.8))
    f.append(line(a2x, ay2, a2x, hy, color=FIELD, sw=2.6))
    f.append(dot(cx2, ry)); f.append(text(cx2 + 15, ry + 4, "корінь", size=11, color=MUTED, anchor="start"))
    f.append(dot(a1x, ay2)); f.append(head(a1x, hy))
    f.append(dot(a2x, ay2, green=True)); f.append(head(a2x, hy))
    f.append(text(a2x + 14, ay2 + 4, "копія", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(textbox(cx2, 424, "тінь = ω·2", size=15, bold=True, fill=GREENFILL, stroke=FIELD, color=INK, min_w=96)[0])

    # ── підсумок ──
    f.append(text(W / 2, 470, "Гілок побільшало — а ординал-тінь упав:  ω² > ω·2.", size=13.5, bold=True))
    f.append(text(W / 2, 494,
                  "Листок = 0;  вузол з піддеревами β₁ ≥ … ≥ βₖ  →  ω^β₁ + … + ω^βₖ.  Спад той самий, що в Ґудстейна — і так само не довести в PA.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "hydra.svg"), W, H, *f)


if __name__ == "__main__":
    fig_reorder()
    fig_ladder()
    fig_von_neumann()
    fig_derived()
    fig_add_asym()
    fig_mult_asym()
    fig_cnf_tower()
    fig_goodstein_tracks()
    fig_hydra()
    print("OK: reorder, ladder, von_neumann, derived, add_asym, mult_asym, cnf_tower, goodstein_tracks, hydra ->", IMG)
