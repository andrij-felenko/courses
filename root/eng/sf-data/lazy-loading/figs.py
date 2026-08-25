# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── дашована «заглушка»: легка рамка з написом «ще не завантажено» ─────────────
def dbox(cx, cy, lines, min_w=190, color=MUTED):
    lines = lines if isinstance(lines, list) else [lines]
    size = 11.5
    tw = max(text_width(l, size) for l in lines)
    w = max(min_w, tw + 22)
    h = len(lines) * size * 1.35 + 18
    x, y = cx - w / 2, cy - h / 2
    r = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="7" '
         'fill="#fbfbfc" stroke="%s" stroke-width="1.4" stroke-dasharray="5,4"/>'
         % (x, y, w, h, color))
    ty = cy - (len(lines) - 1) * size * 1.35 / 2 + size * 0.35
    return r + mtext(cx, ty, lines, size=size, color=color), w, h


# ── Фігура 1: граф зв'язаний наскрізь; жадібно тягне все, ліниво ріже на межі ──
def fig_graph_cut():
    W, H = 1280, 600
    f = []

    f.append(text(W / 2, 40, "Граф зв'язаний наскрізь — ліниве завантаження ріже його на межі",
                  size=16, bold=True, color=INK))
    f.append(text(W / 2, 64, "жадібно тягнеться вся павутина; ліниво — сам об'єкт плюс легкі заглушки",
                  size=12, color=MUTED))

    # роздільник панелей
    f.append(line(640, 92, 640, H - 66, color="#d0d5db", sw=1.0, dash="7,7"))

    f.append(text(330, 112, "Жадібно (eager)", size=14.5, bold=True, color=POS))
    f.append(text(970, 112, "Ліниво (lazy)", size=14.5, bold=True, color=FIELD))

    # ── ЛІВА панель: щільна павутина суцільних коробок ──
    def ob(cx, cy, s, main=False):
        return textbox(cx, cy, s, size=11.5, bold=main, min_w=150,
                       fill=("#e8eefc" if main else "#f4f6f8"),
                       stroke=(INK if main else LINE), sw=(1.9 if main else 1.4))

    order, ow, oh = ob(165, 300, ["Order 42", "(що просили)"], main=True)
    cust,  cw, ch = ob(345, 195, "Customer")
    line_, lw, lh = ob(345, 410, "LineItem")
    prod,  pw, ph = ob(520, 410, "Product")
    supp,  sw_, sh = ob(520, 195, "Supplier")

    # стрілки-павутина (суцільні): від замовлення розповзається все
    f.append(arrow(165 + ow / 2, 292, 345 - cw / 2 - 2, 205, color=INK, sw=1.6))
    f.append(arrow(165 + ow / 2, 308, 345 - lw / 2 - 2, 400, color=INK, sw=1.6))
    f.append(arrow(345 + cw / 2, 195, 520 - sw_ / 2 - 2, 195, color=INK, sw=1.6))
    f.append(arrow(345 + lw / 2, 410, 520 - pw / 2 - 2, 410, color=INK, sw=1.6))
    f.append(arrow(520, 410 - ph / 2, 520, 195 + sh / 2 + 2, color=INK, sw=1.6))
    # замикання кола назад до замовлення (показує, що граф циклічний)
    f.append(arrow(520 - sw_ / 2, 205, 165 + ow / 2 + 2, 288, color=MUTED, sw=1.3))
    f.append(text(360, 300, "…і так по колу", size=10.5, italic=True, color=MUTED))

    f += [order, cust, line_, prod, supp]
    f.append(text(330, H - 42, "один запит тягне всю павутину", size=12.5, bold=True, color=POS))

    # ── ПРАВА панель: сам об'єкт + дашовані заглушки ──
    orderR, owr, ohr = textbox(820, 300, ["Order 42", "(завантажено)"], size=11.5,
                               bold=True, min_w=150, fill="#e8eefc", stroke=INK, sw=1.9)
    gc, gcw, gch = dbox(1055, 195, ["Customer #7", "не завантажено"])
    gl, glw, glh = dbox(1055, 410, ["LineItems", "не завантажено"])

    # дашовані зв'язки: тримається лише ключ
    f.append(line(820 + owr / 2, 292, 1055 - gcw / 2 - 2, 205, color=MUTED, sw=1.5, dash="6,5"))
    f.append(line(820 + owr / 2, 308, 1055 - glw / 2 - 2, 400, color=MUTED, sw=1.5, dash="6,5"))
    f.append(text(900, 240, "лише ключ", size=10.5, italic=True, color=MUTED))
    f.append(text(900, 359, "лише ключ", size=10.5, italic=True, color=MUTED))

    f += [orderR, gc, gl]
    f.append(text(965, H - 42, "вантажимо Order, решту — лише на дотик", size=12.5, bold=True, color=FIELD))

    render(os.path.join(IMG, 'graph-cut.svg'), W, H, *f)


# ── Фігура 2: чотири способи побудувати ту саму заглушку ──────────────────────
def fig_four_techniques():
    W, H = 1300, 600
    f = []

    f.append(text(W / 2, 38, "Чотири способи — та сама заглушка", size=17, bold=True, color=INK))
    f.append(text(W / 2, 60, "різняться тим, хто тримає лінь, чи помітно це клієнтові й чи зберігається тотожність",
                  size=12, color=MUTED))

    cols = [W * 0.135, W * 0.385, W * 0.635, W * 0.885]
    for x in (W / 4, W / 2, 3 * W / 4):
        f.append(line(x, 84, x, H - 54, color="#d0d5db", sw=1.0, dash="6,6"))

    titles = [("Лінива ініціалізація", NEG), ("Віртуальний проксі", FIELD),
              ("Тримач значення", POS), ("Привид", INK)]
    notes = ["порожнє поле\nвсередині власника", "окремий заступник\nінша тотожність",
             "узагальнена обгортка\nклієнт знає про лінь", "той самий об'єкт\nусі поля за раз"]
    for cx, (t, c), note in zip(cols, titles, notes):
        f.append(text(cx, 112, t, size=14, bold=True, color=c))
        f.append(mtext(cx, 500, note.split("\n"), size=11.5, color=c, lh=1.35))

    def box(cx, cy, s, c, fill="#f4f6f8", mw=176):
        return textbox(cx, cy, s, size=11.5, bold=True, min_w=mw, fill=fill, stroke=c, sw=1.6)

    def down(cx, y1, y2, label, c):
        # розриваємо вертикальну стрілку на дві половини — напис сидить у ПРОГАЛИНІ
        # між ними, а не поверх лінії (щоб «лінія не перетинала текст»)
        size = 10.5
        ty = (y1 + y2) / 2 + 4
        top, bot = ty - size * 1.0, ty + size * 0.8
        f.append(line(cx, y1, cx, top, color=c, sw=1.6))
        f.append(arrow(cx, bot, cx, y2, color=c, sw=1.6))
        f.append(text(cx, ty, label, size=size, color=c))

    # 1) Лінива ініціалізація
    cx = cols[0]
    a, aw, ah = box(cx, 178, ["Order", "customer = null"], NEG)
    b, bw, bh = box(cx, 330, ["Order", "customer ✓"], NEG, fill="#eef7f0")
    f += [a, b]
    down(cx, 178 + ah / 2, 330 - bh / 2, "перше читання", NEG)

    # 2) Віртуальний проксі — три коробки
    cx = cols[1]
    a, aw, ah = box(cx, 168, "клієнт", FIELD, fill="#eef2f7")
    b, bw, bh = box(cx, 300, ["Proxy(id)", "той самий інтерфейс"], FIELD)
    c2, cw2, ch2 = box(cx, 428, ["Real Customer", "(створено)"], FIELD, fill="#eef7f0")
    f += [a, b, c2]
    down(cx, 168 + ah / 2, 300 - bh / 2, "тримає ключ", FIELD)
    y1s, y2s = 300 + bh / 2, 428 - ch2 / 2
    ty2 = (y1s + y2s) / 2 + 4
    top2, bot2 = ty2 - 10.5 * 1.0, ty2 + 10.5 * 0.8
    # так само розриваємо пунктир навколо підпису, тонкий хвіст зі стрілкою — окремо біля коробки
    f.append(line(cx, y1s, cx, top2, color=FIELD, sw=1.6, dash="5,4"))
    f.append(line(cx, bot2, cx, y2s - 10, color=FIELD, sw=1.6, dash="5,4"))
    f.append(text(cx, ty2, "перший виклик створює", size=10.5, color=FIELD))
    f.append("<line x1='%.1f' y1='%.1f' x2='%.1f' y2='%.1f' stroke='%s' stroke-width='1.6' stroke-dasharray='5,4' marker-end='url(#arrow)'/>"
             % (cx, y2s - 10, cx, y2s - 1, FIELD))

    # 3) Тримач значення
    cx = cols[2]
    a, aw, ah = box(cx, 178, ["Order", "тримає Holder<Customer>"], POS)
    b, bw, bh = box(cx, 330, ["Real Customer", "(завантажено)"], POS, fill="#eef7f0")
    f += [a, b]
    down(cx, 178 + ah / 2, 330 - bh / 2, "getValue()", POS)

    # 4) Привид — той самий об'єкт наповнює сам себе
    cx = cols[3]
    a, aw, ah = box(cx, 178, ["Customer(id)", "поля порожні"], INK)
    b, bw, bh = box(cx, 330, ["Customer(id)", "поля повні"], INK, fill="#eef7f0")
    f += [a, b]
    down(cx, 178 + ah / 2, 330 - bh / 2, "перший доступ → усі поля", INK)

    render(os.path.join(IMG, 'four-techniques.svg'), W, H, *f)


# ── Фігура 3: брижі запитів (N+1) проти жадібного з'єднання ────────────────────
def fig_ripple():
    W, H = 1220, 560
    f = []

    f.append(text(W / 2, 38, "Ліниво в циклі → злива дрібних запитів (N+1)", size=17, bold=True, color=INK))
    f.append(text(W / 2, 60, "той самий екран — у сто разів менше походів у базу, коли зв'язок беруть наперед",
                  size=12, color=MUTED))

    f.append(line(70, 300, W - 70, 300, color="#d0d5db", sw=1.0, dash="7,7"))

    def db(cx, cy, label, c):
        # «база» як циліндр-натяк: рамка з підписом
        b, bw, bh = textbox(cx, cy, ["БАЗА", label], size=11.5, bold=True,
                            min_w=150, fill="#eef2f7", stroke=c, sw=1.7)
        return b, bw, bh

    # ── Верх: ліниво в циклі ──
    f.append(text(120, 100, "Ліниво в циклі", size=14, bold=True, color=POS))

    q1, q1w, q1h = textbox(210, 190, ["1 запит:", "SELECT orders"], size=11.5, bold=True,
                           min_w=170, fill="#f4f6f8", stroke=INK, sw=1.6)
    orders, ow, oh = textbox(440, 190, ["100", "замовлень"], size=11.5, bold=True,
                             min_w=130, fill="#e8eefc", stroke=INK, sw=1.6)
    dbT, dbTw, dbTh = db(1010, 190, "customers", POS)

    f.append(arrow(210 + q1w / 2, 190, 440 - ow / 2 - 2, 190, color=INK, sw=1.8))
    f += [q1, orders, dbT]

    # злива дрібних запитів: багато тонких стрілок orders → база
    x0 = 440 + ow / 2 + 2
    x1 = 1010 - dbTw / 2 - 2
    for i in range(7):
        yy = 150 + i * 14
        f.append(line(x0, yy, x1, yy, color=POS, sw=1.1))
        f.append("<circle cx='%.1f' cy='%.1f' r='2.4' fill='%s'/>" % (x1, yy, POS))
    f.append(text((x0 + x1) / 2, 132, "+100 запитів (по 1 на замовлення)", size=11.5, bold=True, color=POS))
    f.append(text((x0 + x1) / 2, 264, "цикл: торкнувся order.customer → окремий SELECT", size=11, italic=True, color=MUTED))

    f.append(text(W - 120, 190, "= 101", size=20, bold=True, color=POS))
    f.append(text(W - 120, 214, "запит", size=12, color=POS))

    # ── Низ: жадібно наперед ──
    f.append(text(120, 350, "Жадібно наперед", size=14, bold=True, color=FIELD))

    q2, q2w, q2h = textbox(250, 440, ["1 запит-з'єднання:", "orders JOIN customers"], size=11.5,
                           bold=True, min_w=210, fill="#f4f6f8", stroke=INK, sw=1.6)
    both, bw2, bh2 = textbox(560, 440, ["замовлення +", "покупці разом"], size=11.5, bold=True,
                             min_w=170, fill="#e8f6ee", stroke=FIELD, sw=1.6)
    dbB, dbBw, dbBh = db(1010, 440, "одним махом", FIELD)

    f.append(arrow(250 + q2w / 2, 440, 560 - bw2 / 2 - 2, 440, color=INK, sw=1.8))
    f.append(arrow(560 + bw2 / 2, 440, 1010 - dbBw / 2 - 2, 440, color=FIELD, sw=1.8))
    f += [q2, both, dbB]

    f.append(text(W - 120, 440, "= 1", size=20, bold=True, color=FIELD))
    f.append(text(W - 120, 464, "запит", size=12, color=FIELD))

    render(os.path.join(IMG, 'ripple-nplus1.svg'), W, H, *f)


# ── Фігура 4 (hist): родовід тримача значення — від містка в MVC до Lazy Load ──
def fig_vh_timeline():
    W, H = 1360, 470
    f = []
    f.append(text(W / 2, 40, "Родовід тримача значення: від містка в MVC до різновиду Lazy Load",
                  size=17, bold=True, color=INK))
    f.append(text(W / 2, 64, "той самий об'єкт-посередник — під новим завданням у кожну епоху",
                  size=12, color=MUTED))

    axis_y = 250
    f.append(line(80, axis_y, W - 80, axis_y, color="#c9ced6", sw=2.2))

    xs = [165, 431, 697, 964, 1230]
    data = [
        ("1978–79",     "MVC",             ["Reenskaug у Xerox PARC:", "модель окремо від подання"], NEG),
        ("1983",        "Smalltalk-80 v2", ["механізм залежних —", "об'єкт сповіщає про зміну"],     NEG),
        ("1988",        "ParcPlace",       ["Adele Goldberg виносить", "Smalltalk на ринок"],        FIELD),
        ("поч. 1990-х", "VisualWorks 1.0", ["ValueHolder як клас:", "value / value: + сповіщення"],  INK),
        ("2002",        "Fowler, PoEAA",   ["Value Holder —", "1 із 4 різновидів Lazy Load"],        POS),
    ]
    for x, (yr, title, cap, c) in zip(xs, data):
        box, bw, bh = textbox(x, 165, [yr, title], size=13, bold=True, min_w=205,
                              fill="#f4f6f8", stroke=c, sw=1.7)
        f.append(line(x, 165 + bh / 2, x, axis_y - 11, color=c, sw=1.4, dash="4,4"))
        f.append(box)
        f.append(circle(x, axis_y, 9, fill=BG, stroke=c, sw=2.4))
        f.append(circle(x, axis_y, 3.4, fill=c, stroke=c, sw=1))
        f.append(mtext(x, axis_y + 34, cap, size=11, color=MUTED, lh=1.3))

    f.append(text(W / 2, H - 24,
                  "Той самий посередник: спершу місток між вікном і моделлю, згодом — відкладений похід у базу.",
                  size=12, italic=True, color=INK))
    render(os.path.join(IMG, 'vh-timeline.svg'), W, H, *f)


# ── Фігура 5 (hist): та сама форма — дві різні роботи (UI-місток проти DB-ліні) ─
def fig_vh_two_jobs():
    W, H = 1320, 540
    f = []
    f.append(text(W / 2, 40, "Та сама форма — дві різні роботи", size=17, bold=True, color=INK))
    f.append(text(W / 2, 63, "тримач значення нічого не знає про те, де живе значення — у слоті моделі чи в рядку бази",
                  size=12, color=MUTED))
    f.append(line(660, 92, 660, 452, color="#d0d5db", sw=1.0, dash="7,7"))
    f.append(text(330, 116, "Звідки родом: світ вікон (MVC)", size=14, bold=True, color=NEG))
    f.append(text(990, 116, "Куди перекотився: світ даних (ORM)", size=14, bold=True, color=POS))

    def chain(cx, top_s, mid_s, bot_s, c):
        a, aw, ah = textbox(cx, 175, top_s, size=12, bold=True, min_w=205,
                            fill="#eef2f7", stroke=c, sw=1.6)
        b, bw, bh = textbox(cx, 300, mid_s, size=12, bold=True, min_w=205,
                            fill=("#e8eefc" if c == NEG else "#fdecea"), stroke=c, sw=1.9)
        d, dw, dh = textbox(cx, 425, bot_s, size=12, bold=True, min_w=205,
                            fill="#eef7f0", stroke=c, sw=1.6)
        f.append(arrow(cx, 175 + ah / 2, cx, 300 - bh / 2 - 1, color=c, sw=1.7))
        f.append(arrow(cx, 300 + bh / 2, cx, 425 - dh / 2 - 1, color=c, sw=1.7))
        f.extend([a, b, d])

    chain(330, "Подання (віджет)", ["ValueHolder", "value / value:"], "слот у моделі", NEG)
    chain(990, "Order (у пам'яті)", ["ValueHolder", "getValue()"], "рядок у базі", POS)

    f.append(mtext(330, 480, ["Робота: з'єднати віджет зі слотом моделі",
                              "й сповістити про зміну (onChangeSend:)."], size=11, color=INK, lh=1.3))
    f.append(mtext(990, 480, ["Робота: відкласти похід у базу — getValue()",
                              "робить SELECT аж на перший доступ."], size=11, color=INK, lh=1.3))

    f.append(text(W / 2, H - 20,
                  "Спільна форма — посилання на значення плюс спосіб дістати; різна робота — сповіщати проти відкладати.",
                  size=12.5, bold=True, color=INK))
    render(os.path.join(IMG, 'vh-two-jobs.svg'), W, H, *f)


# ── Фігура 6 (для proj-вставки): драбина числа запитів над тим самим графом ────
def fig_query_ladder():
    import math
    W, H = 1160, 470
    f = []

    f.append(text(W / 2, 40, "Той самий екран, той самий граф — різне число запитів",
                  size=17, bold=True, color=INK))
    f.append(text(W / 2, 64, "100 замовлень, лише 3 різні покупці; під лічильником запитів до бази",
                  size=12.5, color=MUTED))

    AMBER = "#d98c0a"
    x0 = 380                      # старт стовпчиків
    span = 330                    # довжина стовпчика для найбільшого значення (лог-шкала)
    lo = math.log10(101)
    def bw(n):                    # ширина за логарифмом — щоб 1, 2, 4 лишались видимі поряд зі 101
        return 46 + span * (math.log10(n) / lo)

    f.append(text(350, 108, "стратегія", size=11.5, italic=True, color=MUTED, anchor="end"))
    f.append(text(845, 108, "запитів", size=11.5, italic=True, color=MUTED, anchor="end"))

    rows = [
        (["Ліниво в циклі", "(без спільної мапи)"], 101, POS,
         "1 список + по 1 на кожне зі 100"),
        (["Ліниво + мапа тотожності"], 4, AMBER,
         "100 дотиків склеєні у 3 покупці"),
        (["Пакетний IN-запит наперед"], 2, NEG,
         "усі потрібні id — одним запитом"),
        (["Жадібне з'єднання (JOIN)"], 1, FIELD,
         "покупці приїхали разом із замовленнями"),
    ]

    y = 152
    for label, n, c, note in rows:
        f.append(mtext(350, y - (len(label) - 1) * 8 + 4, label, size=12.5,
                       bold=True, color=INK, anchor="end", lh=1.2))
        w = bw(n)
        f.append(rect(x0, y - 17, w, 34, fill=c, stroke=c, sw=1.0, rx=6))
        f.append(text(845, y + 8, str(n), size=25, bold=True, color=c, anchor="end"))
        f.append(text(W - 40, y + 5, note, size=11.5, color=MUTED, anchor="end"))
        y += 78

    f.append(text(W / 2, H - 26,
                  "101 → 4 → 2 → 1: лінь сама по собі не рятує — рятує знання свого сценарію",
                  size=12.5, italic=True, color=INK))

    render(os.path.join(IMG, 'query-ladder.svg'), W, H, *f)


if __name__ == '__main__':
    fig_graph_cut()
    fig_four_techniques()
    fig_ripple()
    fig_vh_timeline()
    fig_vh_two_jobs()
    fig_query_ladder()
    print("figs done")
