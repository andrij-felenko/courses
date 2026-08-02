# -*- coding: utf-8 -*-
"""Фігури до теми «Лямбди й захоплення: що живе скільки»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

GREEN_FILL = "#eafaf0"
RED_FILL = "#fdecea"
BLUE_FILL = "#eef3fd"


def codepanel(x, y, w, lines, size=14, lh=22, pad=14, fill=FILL, stroke=LINE):
    """Рамка з рядками коду, вирівняними ліворуч."""
    h = len(lines) * lh + 2 * pad
    out = rect(x, y, w, h, fill=fill, stroke=stroke)
    ty = y + pad + size
    out += mtext(x + pad, ty, lines, size=size, anchor="start", lh=lh / float(size))
    return out, h


# ── 1. Лямбда-вираз створює об'єкт ─────────────────────────────────────────
def fig_closure_object():
    W, H = 1020, 400
    frags = []

    frags.append(text(230, 78, "що написано", size=15, bold=True, color=MUTED))
    left, hl = codepanel(40, 90, 380, [
        "int limit = 10;",
        "auto f = [limit](int x) {",
        "    return x > limit;",
        "};",
    ])
    frags.append(left)

    frags.append(text(780, 58, "який тип і об'єкт створює компілятор",
                      size=15, bold=True, color=MUTED))
    right, hr = codepanel(580, 70, 400, [
        "class /* без імені */ {",
        "    int limit;",
        "public:",
        "    bool operator()(int x) const",
        "    { return x > limit; }",
        "} f{ limit };",
    ], fill=BLUE_FILL)
    frags.append(right)

    frags.append(text(500, 145, "компілятор", size=13, color=MUTED))
    frags.append(arrow(430, 162, 570, 162))

    frags.append(text(510, 320, "Захоплення стає полем об'єкта, а не аргументом функції.",
                      size=15))
    frags.append(text(510, 350, "Копію зроблено там, де обчислено лямбда-вираз, — не в момент виклику.",
                      size=15))

    render(os.path.join(IMG, 'closure-object.svg'), W, H, *frags)


# ── 2. Що переживає кінець області ─────────────────────────────────────────
def fig_capture_lifetime():
    W, H = 1160, 470
    frags = [text(W / 2, 28, "Одна й та сама послідовність подій, два види захоплення",
                  size=17, bold=True)]

    cols = [210, 450, 690, 930]
    cw = 200
    heads = [
        "1. локальна\nзмінна x = 5",
        "2. створено\nзамикання",
        "3. область\nскінчилася",
        "4. замикання\nвикликали",
    ]
    for x, h in zip(cols, heads):
        frags.append(fitbox(x, 55, cw, 60, h, size=14, fill=BG, stroke=MUTED, color=MUTED))

    rows = [
        (140, "[x]\nза значенням", [
            ("x = 5 живе", FILL, LINE),
            ("у замиканні\nсвоя копія 5", FILL, LINE),
            ("x зникає —\nзамиканню байдуже", FILL, LINE),
            ("читає свою копію\n→ 5", GREEN_FILL, FIELD),
        ]),
        (290, "[&x]\nза посиланням", [
            ("x = 5 живе", FILL, LINE),
            ("у замиканні\nадреса x", FILL, LINE),
            ("x зникає,\nадреса лишається", FILL, LINE),
            ("читає мертву\nпам'ять", RED_FILL, POS),
        ]),
    ]
    for y, label, cells in rows:
        frags.append(fitbox(30, y, 160, 110, label, size=14, fill=BG, stroke=MUTED, bold=True))
        for i, (s, fl, st) in enumerate(cells):
            frags.append(fitbox(cols[i], y, cw, 110, s, size=14, fill=fl, stroke=st))
            if i < 3:
                frags.append(arrow(cols[i] + cw + 5, y + 55, cols[i + 1] - 5, y + 55))

    frags.append(text(W / 2, 440,
                      "Різниця тільки в тому, що лежить у полі замикання: власна копія чи чужа адреса.",
                      size=15))

    render(os.path.join(IMG, 'capture-lifetime.svg'), W, H, *frags)


# ── 3. Куди піде замикання — те й вирішує спосіб захоплення ────────────────
def fig_where_closure_lives():
    W, H = 1140, 510
    frags = []

    body, bw, bh = textbox(570, 52, "Куди піде це замикання?", size=16, bold=True,
                           fill=BLUE_FILL)
    frags.append(body)

    cols = [190, 570, 950]
    frags.append(line(570, 52 + bh / 2, 570, 100))
    frags.append(line(cols[0], 100, cols[2], 100))
    for x in cols:
        frags.append(arrow(x, 100, x, 128))

    dest = [
        "викликається тут-таки\n(алгоритм, цикл, ranges)",
        "зберігається:\nstd::function, контейнер,\nобробник події",
        "їде в іншу нитку\nабо в корутину",
    ]
    life = [
        "гине наприкінці\nповного виразу",
        "переживає область,\nде його створили",
        "живе непередбачувано\nдовго",
    ]
    rule = [
        "[&] безпечне\nй найдешевше",
        "тільки володіння: копія\nабо [p = std::move(p)];\nна себе — через weak_ptr",
        "тільки володіння;\nбудь-яке посилання —\nперегони або мертва адреса",
    ]
    tones = [(GREEN_FILL, FIELD), (BLUE_FILL, NEG), (RED_FILL, POS)]

    for i, x in enumerate(cols):
        left = x - 160
        frags.append(fitbox(left, 130, 320, 80, dest[i], size=14, fill=FILL, stroke=LINE))
        frags.append(arrow(x, 212, x, 244))
        frags.append(fitbox(left, 246, 320, 70, life[i], size=14, fill=BG, stroke=MUTED))
        frags.append(arrow(x, 318, x, 350))
        fl, st = tones[i]
        frags.append(fitbox(left, 352, 320, 100, rule[i], size=14, fill=fl, stroke=st))

    frags.append(text(W / 2, 486,
                      "Спосіб захоплення обирає не смак, а те, чи може замикання пережити те, на що дивиться.",
                      size=15))

    render(os.path.join(IMG, 'where-closure-lives.svg'), W, H, *frags)


# ── 4. Один і той самий предикат у чотирьох записах (вставка hist) ─────────
def fig_syntax_eras():
    W, H = 1180, 500
    frags = [text(W / 2, 30, "Один і той самий предикат «x < i» у чотирьох редакціях пропозиції",
                  size=17, bold=True)]

    rows = [
        ("N1968\nлютий 2006",
         "<>(int x) -> bool extern(i) { return x < i; }",
         "ромб замість імені;\nextern(...) — список\nпосилань, решта — копії",
         FILL, LINE),
        ("N2529\nлютий 2008",
         "<&>(int x) (x < i)",
         "кутові дужки з режимом\nзахоплення; тіло —\nвираз без return",
         FILL, LINE),
        ("N2550\nберезень 2008",
         "[&](int x) { return x < i; }",
         "квадратні дужки й тіло-блок;\nсаме це проголосували\nв Bellevue",
         GREEN_FILL, FIELD),
        ("C++11\nфінальний вигляд",
         "[i](int x) mutable { return x < i; }",
         "поіменні захоплення\nй ключове слово mutable\n(папір N2658)",
         BLUE_FILL, NEG),
    ]

    for i, (label, code, note, fl, st) in enumerate(rows):
        y = 70 + i * 100
        frags.append(fitbox(30, y, 170, 76, label, size=14, fill=BG, stroke=MUTED, bold=True))
        panel, ph = codepanel(220, y + 13, 560, [code], size=14, fill=fl, stroke=st)
        frags.append(panel)
        frags.append(fitbox(810, y, 340, 76, note, size=13, fill=BG, stroke=MUTED, color=MUTED))

    frags.append(text(W / 2, 478,
                      "Змінювався не сенс, а запис: об'єктом із полями замикання було в усіх редакціях.",
                      size=15))

    render(os.path.join(IMG, 'syntax-eras.svg'), W, H, *frags)


# ── 5. Чотири часи життя однієї підписки (вставка proj) ────────────────────
def fig_subscription_lifetimes():
    W, H = 1240, 520
    frags = []

    cols = [330, 510, 700, 890, 1080]
    heads = [
        "EventBus\nстворено",
        "Chart створено,\nпідписка",
        "publish #1",
        "Chart\nзнищено",
        "publish #2",
    ]
    for x, h in zip(cols, heads):
        frags.append(fitbox(x - 84, 48, 168, 64, h, size=14, fill=BG, stroke=MUTED, color=MUTED))
        frags.append(line(x, 114, x, 146, color=MUTED, dash="4,4"))
        frags.append(line(x, 286, x, 308, color=MUTED, dash="4,4"))

    L, R = 330, 1160
    BH = 34

    # ── ряд A: наївна підписка ──
    frags.append(fitbox(20, 150, 230, 130, "НАЇВНО\n[=] у методі —\nзахоплено this",
                        size=14, fill=RED_FILL, stroke=POS, bold=True))
    frags.append(fitbox(L, 155, R - L, BH, "EventBus — живий увесь час",
                        size=14, fill=BLUE_FILL, stroke=NEG))
    frags.append(fitbox(510, 200, 890 - 510, BH, "Chart — живий",
                        size=14, fill=FILL, stroke=LINE))
    frags.append(fitbox(510, 245, 890 - 510, BH, "замикання: копія вказівника this",
                        size=13, fill=GREEN_FILL, stroke=FIELD))
    frags.append(fitbox(890, 245, R - 890, BH, "той самий this — мертвий",
                        size=13, fill=RED_FILL, stroke=POS, color=POS, bold=True))

    # ── ряд B: підписка з токеном ──
    frags.append(fitbox(20, 310, 230, 130, "З ТОКЕНОМ\nSubscription —\nчлен Chart",
                        size=14, fill=GREEN_FILL, stroke=FIELD, bold=True))
    frags.append(fitbox(L, 315, R - L, BH, "EventBus — живий увесь час",
                        size=14, fill=BLUE_FILL, stroke=NEG))
    frags.append(fitbox(510, 360, 890 - 510, BH, "Chart — живий, тримає токен",
                        size=13, fill=FILL, stroke=LINE))
    frags.append(fitbox(510, 405, 890 - 510, BH, "замикання у слоті шини",
                        size=13, fill=GREEN_FILL, stroke=FIELD))
    frags.append(fitbox(900, 405, R - 900, BH, "слота немає — publish #2 тихий",
                        size=13, fill=BG, stroke=MUTED, color=MUTED))

    frags.append(text(W / 2, 480,
                      "Замикання живе стільки, скільки живе слот, — а не стільки, скільки живе той, хто підписався.",
                      size=15))

    render(os.path.join(IMG, 'subscription-lifetimes.svg'), W, H, *frags,
           title="Скільки живе підписка й скільки — підписник")


# ── 5. Порядок слотів у граматиці лямбда-виразу (вставка api) ──────────────
def fig_lambda_slots():
    W, H = 1180, 430
    frags = []

    slots = [
        "[ захоплення ]\nсписок захоплень\nC++11",
        "< параметри шаблону >\nявний список типів\nC++20",
        "requires ...\nобмеження\nC++20",
        "( параметри )\nсписок параметрів\nC++11, пропускається",
        "mutable  constexpr\nconsteval  static\nC++11 / 17 / 20 / 23",
        "noexcept ( ... )\nспецифікація винятків\nC++11",
        "-> тип\nтип результату\nC++11, типово auto",
        "{ тіло }\nтіло оператора виклику\nC++11",
    ]
    tones = [
        (BLUE_FILL, NEG), (FILL, LINE), (FILL, LINE), (FILL, LINE),
        (FILL, LINE), (FILL, LINE), (FILL, LINE), (GREEN_FILL, FIELD),
    ]

    xs = [25, 315, 605, 895]
    bw, bh = 260, 90
    rows = [90, 250]

    for i, s in enumerate(slots):
        x = xs[i % 4]
        y = rows[i // 4]
        fl, st = tones[i]
        frags.append(fitbox(x, y, bw, bh, s, size=14, fill=fl, stroke=st))
        if i % 4 < 3:
            frags.append(arrow(x + bw + 4, y + bh / 2, x + bw + 26, y + bh / 2))

    # перехід з першого рядка на другий
    frags.append(line(xs[3] + bw, rows[0] + bh / 2, 1168, rows[0] + bh / 2))
    frags.append(line(1168, rows[0] + bh / 2, 1168, 205))
    frags.append(line(1168, 205, 12, 205))
    frags.append(line(12, 205, 12, rows[1] + bh / 2))
    frags.append(arrow(12, rows[1] + bh / 2, xs[0] - 4, rows[1] + bh / 2))

    frags.append(text(W / 2, 385,
                      "Пропустити слот можна майже будь-який — поміняти слоти місцями не можна.",
                      size=15))

    render(os.path.join(IMG, 'lambda-slots.svg'), W, H, *frags,
           title="Порядок слотів у лямбда-виразі й версія стандарту для кожного")


if __name__ == '__main__':
    fig_lambda_slots()
    fig_closure_object()
    fig_capture_lifetime()
    fig_where_closure_lives()
    fig_syntax_eras()
    fig_subscription_lifetimes()
    print("ok")
