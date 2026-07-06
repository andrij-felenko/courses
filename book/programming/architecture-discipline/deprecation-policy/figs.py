# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: три фази життя й вікно співіснування ──────────────────────────
def fig_lifecycle():
    W, H = 760, 300
    frags = []
    frags.append(text(W/2, 30, "Три фази життя можливості", size=17, bold=True))

    # координати смуг
    top = 70
    bh = 64
    x0 = 40
    # межі трьох фаз
    b1 = 250   # кінець «підтримується»
    b2 = 560   # кінець «застаріле» (=видалення)
    xe = W - 40

    # Фаза 1: підтримується
    frags.append(rect(x0, top, b1 - x0, bh, fill="#eaf7ef", stroke=FIELD, sw=1.8))
    frags.append(text((x0 + b1) / 2, top + 26, "Підтримується", size=14, bold=True, color="#1e7a44"))
    frags.append(text((x0 + b1) / 2, top + 46, "старий шлях — єдиний", size=12, color=MUTED))

    # Фаза 2: застаріле (обидва живі)
    frags.append(rect(b1, top, b2 - b1, bh, fill="#fdf3e7", stroke="#c98a2b", sw=1.8))
    frags.append(text((b1 + b2) / 2, top + 26, "Застаріле", size=14, bold=True, color="#a4670f"))
    frags.append(text((b1 + b2) / 2, top + 46, "обидва шляхи живі + попередження", size=12, color=MUTED))

    # Фаза 3: видалено
    frags.append(rect(b2, top, xe - b2, bh, fill="#fdecea", stroke=POS, sw=1.8))
    frags.append(text((b2 + xe) / 2, top + 26, "Видалено", size=14, bold=True, color="#a02419"))
    frags.append(text((b2 + xe) / 2, top + 46, "лишився новий", size=12, color=MUTED))

    # вертикальні події-віхи
    def milestone(x, label, sub):
        frags.append(line(x, top - 14, x, top + bh + 10, color=INK, sw=1.5, dash="4 3"))
        b, w, h = textbox(x, top - 30, label, size=12, bold=True, pad=6, fill=BG)
        frags.append(b)
        frags.append(text(x, top + bh + 26, sub, size=11, color=MUTED))

    milestone(b1, "Оголошення", "новий шлях готовий")
    milestone(b2, "Видалення", "після зникнення користувачів")

    # дужка вікна співіснування під смугою застарілого
    ay = top + bh + 44
    frags.append(line(b1, ay, b2, ay, color="#a4670f", sw=2))
    frags.append(line(b1, ay - 6, b1, ay + 6, color="#a4670f", sw=2))
    frags.append(line(b2, ay - 6, b2, ay + 6, color="#a4670f", sw=2))
    b, w, h = textbox((b1 + b2) / 2, ay + 22,
                      "вікно міграції: тут користувачі переходять самі",
                      size=12, bold=True, pad=7, fill="#fdf3e7", stroke="#c98a2b")
    frags.append(b)

    # вісь часу
    frags.append(arrow(x0, H - 16, xe, H - 16, color=MUTED))
    frags.append(text(xe, H - 22, "час", size=12, color=MUTED, anchor="end"))

    render(os.path.join(IMG, 'lifecycle.svg'), W, H, *frags)


# ── Фігура 2: обрив проти керованого спуску ─────────────────────────────────
def fig_cliff_vs_ramp():
    W, H = 760, 340
    frags = []
    frags.append(text(W/2, 30, "Дві стратегії прибрати старе", size=17, bold=True))

    # дві панелі
    def panel(ox, title, tcolor, tfill, tstroke):
        pw, ph = 320, 200
        oy = 66
        # рамка панелі
        frags.append(rect(ox, oy, pw, ph, fill=BG, stroke=MUTED, sw=1.3))
        b, w, h = textbox(ox + pw/2, oy - 4, title, size=13, bold=True, pad=6,
                          fill=tfill, stroke=tstroke, color=tcolor)
        frags.append(b)
        # осі
        ax0, ay0 = ox + 42, oy + ph - 34
        axe, aye = ox + pw - 20, oy + 24
        frags.append(arrow(ax0, ay0, axe, ay0, color=MUTED))   # час
        frags.append(arrow(ax0, ay0, ax0, aye, color=MUTED))   # поломки
        frags.append(text(axe, ay0 + 18, "час", size=11, color=MUTED, anchor="end"))
        frags.append(text(ax0 - 8, aye - 4, "поломки", size=11, color=MUTED, anchor="start"))
        return ax0, ay0, axe, aye

    # Панель А — обрив
    ax0, ay0, axe, aye = panel(40, "Обрив: прибрали різко", "#a02419", "#fdecea", POS)
    # лінія: рівно низько, тоді різкий шпиль угору
    cxa = ax0 + (axe - ax0) * 0.42
    frags.append(line(ax0, ay0 - 6, cxa, ay0 - 6, color=POS, sw=2.6))
    frags.append(line(cxa, ay0 - 6, cxa, aye + 6, color=POS, sw=2.6))
    frags.append(line(cxa, aye + 6, axe, aye + 6, color=POS, sw=2.6, dash="5 4"))
    # підпис — праворуч від шпиля, у верхньому куті панелі, не торкаючись ліній
    b, w, h = textbox((cxa + axe) / 2 + 20, aye + 30, "усе падає\nв один день", size=11, bold=True,
                      pad=6, fill="#fdecea", stroke=POS, color="#a02419")
    frags.append(b)

    # Панель Б — керований спуск
    ax0, ay0, axe, aye = panel(400, "Керований спуск", "#1e7a44", "#eaf7ef", FIELD)
    # сходинки-етапи: оголошення → попередження → міграція → видалення, поломки рівні внизу
    steps_x = [ax0 + (axe - ax0) * f for f in (0.10, 0.36, 0.62, 0.88)]
    labels = ["оголоси", "попередь", "міруй", "прибери"]
    yline = ay0 - 6
    frags.append(line(ax0, yline, axe, yline, color=FIELD, sw=2.6))
    for sx, lb in zip(steps_x, labels):
        frags.append(line(sx, yline - 4, sx, yline + 4, color=FIELD, sw=2))
        frags.append(circle(sx, yline, 4.5, fill="#eaf7ef", stroke=FIELD, sw=2))
        frags.append(text(sx, ay0 + 18, lb, size=10.5, color="#1e7a44", bold=True))
    b, w, h = textbox((steps_x[0] + steps_x[-1]) / 2, aye + 30,
                      "поломок нема:\nвсі перейшли завчасно", size=11, bold=True,
                      pad=6, fill="#eaf7ef", stroke=FIELD, color="#1e7a44")
    frags.append(b)

    render(os.path.join(IMG, 'cliff_vs_ramp.svg'), W, H, *frags)


# ── Фігура 3: рішення деприкейшну — терези двох витрат ──────────────────────
def fig_balance():
    W, H = 720, 320
    frags = []
    frags.append(text(W/2, 30, "Рішення деприкейшну — це терези", size=17, bold=True))

    cx = W / 2
    fulcrum_y = 210
    beam_y = 120

    # опора (трикутник)
    frags.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" stroke="%s" stroke-width="1.5"/>'
                 % (cx, beam_y + 6, cx - 26, fulcrum_y, cx + 26, fulcrum_y, FILL, LINE))
    # коромисло
    frags.append(line(cx - 250, beam_y, cx + 250, beam_y, color=INK, sw=3))

    # ліва шалька — тримати старе (тонкий підвіс + рамка нижче нього)
    lx = cx - 200
    box_top = beam_y + 40
    frags.append(line(lx, beam_y, lx, box_top, color=MUTED, sw=1.5))
    b, w, h = textbox(lx, box_top + 62,
                      "тисне ПРИБРАТИ\nЦіна тримати старе:\nподвійний код і тести,\nгальмує зміни,\nплутає новачків",
                      size=12, bold=False, pad=10, fill="#fdf3e7", stroke="#c98a2b")
    frags.append(b)

    # права шалька — прибрати старе
    rx = cx + 200
    frags.append(line(rx, beam_y, rx, box_top, color=MUTED, sw=1.5))
    b, w, h = textbox(rx, box_top + 62,
                      "тисне ЛИШИТИ\nЦіна прибрати старе:\nчужий код ламається,\nвтрата довіри,\nробота лягає на всіх",
                      size=12, bold=False, pad=10, fill="#eaf0fd", stroke=NEG)
    frags.append(b)

    # підпис під опорою
    b, w, h = textbox(cx, fulcrum_y + 34, "керований процес зсуває терези:\nздешевлює обидві ціни, тоді прибирає",
                      size=12, bold=True, pad=9, fill="#eaf7ef", stroke=FIELD, color="#1e7a44")
    frags.append(b)

    render(os.path.join(IMG, 'balance.svg'), W, H, *frags)


# ── Фігура 4 (вставка hist): дорога слова від молитви до компілятора ─────────
def fig_term_timeline():
    W, H = 860, 300
    frags = []
    frags.append(text(W / 2, 30, "Дорога слова «deprecation»: від молитви до коду", size=17, bold=True))

    # горизонтальна вісь часу
    axy = 150
    x0, xe = 60, W - 60
    frags.append(line(x0, axy, xe, axy, color=MUTED, sw=2))
    frags.append(text(xe + 4, axy + 4, "час", size=12, color=MUTED, anchor="start"))

    # чотири станції: (частка осі, підпис-дата, що додалося, колір рамки/заливка, напрям)
    stations = [
        (0.06, "лат. deprecari",   "молитва\nвідвернути біду",      NEG,      "#eaf0fd", +1),
        (0.34, "англ. 1620-ті",    "молитовний сенс\nв англійській", "#7a5cc8", "#efeafc", -1),
        (0.62, "англ. 1640-ві",    "несхвалення,\nзастереження",     "#c98a2b", "#fdf3e7", +1),
        (0.90, "код: 1984 · 1991", "Usenet (4.2BSD, C),\nJargon File", FIELD,   "#eaf7ef", -1),
    ]

    for f, when, what, col, fill, up in stations:
        x = x0 + (xe - x0) * f
        # вузол на осі
        frags.append(circle(x, axy, 6, fill=fill, stroke=col, sw=2.4))
        # дата — по інший бік осі, ніж картка
        dy = axy + 30 if up > 0 else axy - 22
        frags.append(text(x, dy, when, size=12, bold=True, color=col))
        # картка «що додалося» — над або під віссю
        boxcy = axy - 66 if up > 0 else axy + 74
        b, w, h = textbox(x, boxcy, what, size=12, bold=False, pad=8, fill=fill, stroke=col)
        frags.append(b)
        # тонкий підвіс від осі до картки
        edge = boxcy + h / 2 if up > 0 else boxcy - h / 2
        frags.append(line(x, axy, x, edge, color=col, sw=1.3, dash="3 3"))

    # спільна серцевина — стрічка під усім
    b, w, h = textbox(W / 2, H - 26,
                      "серцевина незмінна: «застерігаю проти цього — але проханням, не силою»",
                      size=12.5, bold=True, pad=9, fill=BG, stroke=INK)
    frags.append(b)

    render(os.path.join(IMG, 'term_timeline.svg'), W, H, *frags)


# ── Фігура 5 (вставка hist): зворотний відлік робить дату невблаганною ───────
def fig_countdown():
    W, H = 880, 372
    frags = []
    frags.append(text(W / 2, 30, "Зворотний відлік робить дату невблаганною", size=17, bold=True))

    # Ліворуч — три віхи оголошення (рядок за рядком, згори вниз)
    lx = 158
    ys = [96, 158, 220]
    milestones = [
        ("2008: захід сонця у 2015", "#eaf0fd", NEG, INK),
        ("2014: відсунуто на 2020", "#fdf3e7", "#c98a2b", INK),
        ("сайт-годинник: N днів", "#eaf7ef", FIELD, "#1e7a44"),
    ]
    for y, (label, fill, stroke, col) in zip(ys, milestones):
        b, w, h = textbox(lx, y, label, size=12, bold=True, pad=8,
                          fill=fill, stroke=stroke, color=col, min_w=250)
        frags.append(b)

    # Стрілка від стосу віх до табло
    frags.append(arrow(lx + 132, ys[1], 342, ys[1], color=MUTED))

    # Центр — велике табло відліку
    bx, by, bw, bh = 352, 100, 216, 158
    frags.append(rect(bx, by, bw, bh, fill="#1a1a1a", stroke=INK, sw=2, rx=10))
    frags.append(text(bx + bw / 2, by + 30, "до 1 січня 2020", size=13, color="#e5e7eb"))
    frags.append(text(bx + bw / 2, by + 84, "412", size=46, color="#ffffff", bold=True))
    frags.append(text(bx + bw / 2, by + 112, "днів · год · хв · сек", size=12, color="#9ca3af"))
    frags.append(text(bx + bw / 2, by + 138, "цокає в реальному часі", size=11, color="#9ca3af", italic=True))

    # Праворуч — дві стрілки-наслідки (видима дата ↔ розмита дата)
    frags.append(arrow(bx + bw, by + 46, 686, by + 46, color=FIELD, sw=2))
    b, w, h = textbox(776, by + 46, "видимо й\nневблаганно →\nчас переходити",
                      size=12, bold=True, pad=9, fill="#eaf7ef", stroke=FIELD, color="#1e7a44", min_w=176)
    frags.append(b)

    frags.append(arrow(bx + bw, by + 118, 686, by + 118, color=POS, sw=2))
    b, w, h = textbox(776, by + 118, "розмито й\nдалеко →\nвідкладу на потім",
                      size=12, bold=True, pad=9, fill="#fdecea", stroke=POS, color="#a02419", min_w=176)
    frags.append(b)

    # Підпис-висновок унизу
    b, w, h = textbox(W / 2, H - 30,
                      "сама дата — рядок, що легко забути; годинник тисне не на код, а на людину, що вагається",
                      size=12, bold=True, pad=9, fill="#fdf3e7", stroke="#c98a2b")
    frags.append(b)

    render(os.path.join(IMG, 'countdown.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_lifecycle()
    fig_cliff_vs_ramp()
    fig_balance()
    fig_term_timeline()
    fig_countdown()
    print("figures written")
