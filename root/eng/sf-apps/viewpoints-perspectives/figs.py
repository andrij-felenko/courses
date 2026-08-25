# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: в'ю — вертикальні зрізи; перспективи — горизонтальні смуги ──────
def fig_grid():
    W, H = 900, 470
    frags = []
    frags.append(text(W/2, 30, "В'ю ріжуть систему на структури; перспективи проходять крізь усі в'ю", size=17, bold=True))

    # сітка: 5 колонок-в'ю × поле, поверх — 3 горизонтальні смуги-перспективи
    views = ["Функційна", "Інформаційна", "Конкурентна", "Розгортання", "Операційна"]
    gx0, gy0 = 150, 90         # лівий верх сітки (лишаємо зліва місце під підписи перспектив)
    gw, gh = 560, 300          # розмір поля сітки
    cw = gw / len(views)

    # горизонтальні смуги-перспективи (малюємо ПІД колонками — як тло)
    persp = [("Безпека", "#fdecea", POS),
             ("Продуктивність", "#eef6ee", FIELD),
             ("Еволюція", "#eaf0fd", NEG)]
    ph = gh / len(persp)
    for i, (name, fill, col) in enumerate(persp):
        y = gy0 + i*ph
        frags.append(rect(gx0, y, gw, ph, fill=fill, stroke=col, sw=1.2, rx=0))
        # підпис перспективи — ліворуч від сітки, у своїй рамці (не накладається)
        b, bw, bh = textbox(gx0-72, y+ph/2, name, size=11.5, bold=True, fill="#ffffff", stroke=col, pad=6)
        frags.append(b)

    # вертикальні лінії колонок + підписи в'ю зверху
    for j, v in enumerate(views):
        x = gx0 + j*cw
        if j > 0:
            frags.append(line(x, gy0, x, gy0+gh, color="#ffffff", sw=2))
        # підпис в'ю — над колонкою, вертикально не тісно
        frags.append(text(x+cw/2, gy0-14, v, size=12, bold=True, color=INK))
    # рамка всього поля
    frags.append(rect(gx0, gy0, gw, gh, fill="none", stroke=INK, sw=2, rx=0))

    # пояснення праворуч
    b1, w1, h1 = textbox(800, 150, ["В'ю (viewpoint):", "структурний зріз —", "одна відповідь на", "«як воно влаштоване»"],
                         size=11.5, fill="#f4f6f8", stroke=INK, pad=9)
    frags.append(b1)
    b2, w2, h2 = textbox(800, 300, ["Перспектива:", "якість, що зачіпає", "КОЖНУ структуру —", "не окрема коробка"],
                         size=11.5, fill="#fff7ed", stroke=POS, pad=9)
    frags.append(b2)

    # підказка: клітинка = «як безпека лягає на конкурентну в'ю»
    cellx = gx0 + 2*cw + cw/2
    celly = gy0 + ph/2
    frags.append(circle(cellx, celly, 6, fill=INK, stroke=INK))
    b3, w3, h3 = textbox(cellx, gy0+gh+34, "клітинка = питання «як БЕЗПЕКА лягає на КОНКУРЕНТНУ в'ю»",
                         size=11, fill="#ffffff", stroke=MUTED, pad=7)
    frags.append(b3)

    render(os.path.join(OUT, "grid.svg"), W, H, *frags)


# ── Фігура 2: каталог семи в'ю — що питає, кого хвилює ────────────────────────
def fig_viewpoints():
    rows = [
        ("Контекстна", "де межі системи, з ким вона говорить", "замовник, інтегратори"),
        ("Функційна", "з яких частин і як вони взаємодіють", "усі, аналітики"),
        ("Інформаційна", "які дані, де живуть, як течуть", "власники даних, DBA"),
        ("Конкурентна", "що працює паралельно, де синхронізація", "розробники, тестувальники"),
        ("Розробки", "як улаштований код, збірка, модулі", "команда розробки"),
        ("Розгортання", "на якому залізі це крутиться", "інфраструктура, DevOps"),
        ("Операційна", "як це запускати, стежити, лікувати", "експлуатація, підтримка"),
    ]
    W = 900
    top = 66
    rh = 46
    H = top + rh*len(rows) + 30
    frags = []
    frags.append(text(W/2, 30, "Сім в'ю Rozanski/Woods: кожна відповідає на одне питання про структуру", size=16, bold=True))

    # колонки з ЗАПАСОМ по ширині, щоб написи не накладались
    cx_name, w_name = 30, 150
    cx_q,    w_q    = 190, 470
    cx_who,  w_who  = 672, 208

    # шапка
    frags.append(text(cx_name+w_name/2, top-12, "В'Ю", size=11.5, bold=True, color=MUTED))
    frags.append(text(cx_q+w_q/2,       top-12, "НА ЯКЕ ПИТАННЯ ВІДПОВІДАЄ", size=11.5, bold=True, color=MUTED))
    frags.append(text(cx_who+w_who/2,   top-12, "КОГО НАЙБІЛЬШЕ ХВИЛЮЄ", size=11.5, bold=True, color=MUTED))

    for i, (name, q, who) in enumerate(rows):
        y = top + i*rh
        band = "#f4f6f8" if i % 2 == 0 else "#ffffff"
        frags.append(rect(cx_name, y, w_name+w_q+w_who+12, rh-6, fill=band, stroke="none", rx=4))
        frags.append(fitbox(cx_name, y, w_name, rh-6, name, size=12.5, bold=True, fill="#eef2f7", stroke=INK, pad=6))
        frags.append(text(cx_q+8, y+(rh-6)/2+4, q, size=12, color=INK, anchor="start"))
        frags.append(text(cx_who+8, y+(rh-6)/2+4, who, size=11.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "viewpoints.svg"), W, H, *frags)


# ── Фігура 3: ланцюг понять стейкхолдер → турбота → в'ю → погляд ──────────────
def fig_chain():
    W, H = 900, 300
    frags = []
    frags.append(text(W/2, 32, "Ланцюг ISO 42010: турбота стейкхолдера керує вибором в'ю", size=16, bold=True))

    y = 150
    boxes = [
        ("Стейкхолдер", "той, у кого\nє турбота", "#eef2f7", INK),
        ("Турбота\n(concern)", "«чи витримає\nпік навантаження»", "#fff7ed", POS),
        ("Viewpoint", "готовий шаблон:\nщо і як показати", "#eef6ee", FIELD),
        ("View\n(погляд)", "заповнений шаблон\nдля ЦІЄЇ системи", "#eaf0fd", NEG),
    ]
    n = len(boxes)
    margin = 40
    gap = 46
    bw = (W - 2*margin - (n-1)*gap) / n
    xs = []
    for i, (title, sub, fill, col) in enumerate(boxes):
        x = margin + i*(bw+gap)
        xs.append(x)
        frags.append(fitbox(x, y-40, bw, 42, title, size=13, bold=True, fill=fill, stroke=col, pad=6))
        frags.append(fitbox(x, y+8, bw, 44, sub, size=10.5, fill="#ffffff", stroke=MUTED, pad=6))
        if i > 0:
            xprev = xs[i-1]
            frags.append(arrow(xprev+bw+4, y-19, x-4, y-19, color=INK, sw=1.8))

    # підпис-висновок під ланцюгом, у рамці — без накладань
    b, bw2, bh2 = textbox(W/2, 250, "не «намалюймо всі діаграми», а «яка турбота → та в'ю її покриває»",
                         size=12, bold=True, fill="#ffffff", stroke=INK, pad=9)
    frags.append(b)

    render(os.path.join(OUT, "chain.svg"), W, H, *frags)


# ── Фігура 4 (для hist-вставки): родовід рамок — що додав кожен крок ──────────
def fig_lineage():
    W, H = 940, 470
    frags = []
    frags.append(text(W/2, 30, "Родовід рамок опису архітектури: кожен крок доклав своє", size=17, bold=True))

    # горизонтальна вісь часу
    axis_y = 92
    frags.append(line(60, axis_y, W-60, axis_y, color=MUTED, sw=2))
    for x, yr in [(150, "1995"), (415, "2000"), (620, "2011"), (820, "2011")]:
        frags.append(circle(x, axis_y, 5, fill=INK, stroke=INK))
        frags.append(text(x, axis_y-14, yr, size=12.5, bold=True, color=INK))

    # чотири віхи: заголовок-плашка + що саме додала (у своїй рамці, з запасом)
    cols = [
        (150, "4+1\nКручтен", "#eef2f7", INK,
         ["узаконив саму ідею:", "не одна діаграма,", "а КІЛЬКА узгоджених", "в'ю + сценарії"]),
        (415, "IEEE 1471\n(2000)", "#fff7ed", POS,
         ["ввів строгу мову:", "стейкхолдер → турбота", "→ viewpoint → view;", "перший стандарт"]),
        (620, "ISO 42010\n(2011)", "#eef6ee", FIELD,
         ["зробив міжнародним;", "правило: КОЖНА", "турбота покрита", "хоч однією в'ю"]),
        (820, "Rozanski\n/ Woods", "#eaf0fd", NEG,
         ["наповнив: 7 в'ю", "+ ПЕРСПЕКТИВИ як", "осібне поняття", "(чого в 4+1 не було)"]),
    ]
    for x, head, fill, col, body in cols:
        # плашка-заголовок під точкою осі
        frags.append(fitbox(x-88, axis_y+22, 176, 46, head, size=13, bold=True, fill=fill, stroke=col, pad=6))
        # тіло — що додав крок
        b, bw, bh = textbox(x, axis_y+150, body, size=11, fill="#ffffff", stroke=col, pad=9)
        frags.append(b)
        # тонка вертикаль від плашки до тіла
        frags.append(line(x, axis_y+68, x, axis_y+150-bh/2, color=MUTED, sw=1, dash="3,3"))

    # стрілки «додає до попереднього» між плашками
    for x0, x1 in [(150, 415), (415, 620)]:
        frags.append(arrow(x0+90, axis_y+45, x1-90, axis_y+45, color=INK, sw=1.8))
    # Rozanski/Woods — не наступний стандарт, а НАПОВНЕННЯ 42010: окрема стрілка
    frags.append(arrow(620+90, axis_y+108, 820-90, axis_y+108, color=NEG, sw=1.6))
    frags.append(text(720, axis_y+100, "наповнює 42010", size=10.5, italic=True, color=NEG))

    # підпис-висновок унизу, у рамці
    b, bw, bh = textbox(W/2, H-26, "стандарт дав КАРКАС (мову й правило покриття) — Rozanski/Woods дали ПЛОТЬ (готові в'ю й перспективи)",
                        size=11.5, bold=True, fill="#ffffff", stroke=INK, pad=9)
    frags.append(b)

    render(os.path.join(OUT, "lineage.svg"), W, H, *frags)


# ── Фігура 5 (detailed): анатомія viewpoint'а — це специфікація, не картинка ──
def fig_viewpoint_anatomy():
    rows = [
        ("Визначення", "що саме цей зріз описує — і що свідомо лишає іншим зрізам"),
        ("Турботи (concerns)", "на які питання стейкхолдерів цей зріз відповідає"),
        ("Стейкхолдери", "кого з людей цей зріз обходить найбільше"),
        ("Моделі й нотація", "які діаграми/таблиці будувати (model kinds за ISO 42010)"),
        ("Дії побудови", "кроки, якими цю в'ю збирають, і поради з практики"),
        ("Проблеми й пастки", "типові помилки саме цього зрізу — і як їх обійти"),
    ]
    W = 900
    top = 82
    rh = 50
    H = top + rh * len(rows) + 74
    frags = []
    frags.append(text(W/2, 30, "Анатомія viewpoint'а: не картинка, а специфікація класу картинок", size=16, bold=True))
    frags.append(text(W/2, 56, "той самий бланк для будь-якої системи — заповниш під свою, дістанеш view", size=12, italic=True, color=MUTED))

    cx_name, w_name = 30, 210
    cx_desc, w_desc = 250, 620
    for i, (name, desc) in enumerate(rows):
        y = top + i*rh
        band = "#f4f6f8" if i % 2 == 0 else "#ffffff"
        frags.append(rect(cx_name, y, w_name+w_desc, rh-8, fill=band, stroke="none", rx=4))
        frags.append(fitbox(cx_name, y, w_name, rh-8, name, size=12.5, bold=True, fill="#eef2f7", stroke=INK, pad=6))
        frags.append(text(cx_desc+10, y+(rh-8)/2+4, desc, size=12, color=INK, anchor="start"))

    b, bw, bh = textbox(W/2, top+rh*len(rows)+32,
                        "viewpoint = багаторазовий бланк · застосований до системи → view (заповнений бланк)",
                        size=12, bold=True, fill="#fff7ed", stroke=POS, pad=9)
    frags.append(b)
    render(os.path.join(OUT, "viewpoint-anatomy.svg"), W, H, *frags)


# ── Фігура 6 (detailed): correspondences — один елемент у п'яти в'ю ────────────
def fig_correspondence_web():
    W, H = 960, 560
    frags = []
    frags.append(text(W/2, 30, "Один елемент — п'ять в'ю: correspondences тримають зрізи несуперечливими", size=15, bold=True))

    hub_cx, hub_cy = W/2, 98
    hb, hbw, hbh = textbox(hub_cx, hub_cy, ["Функційна в'ю", "елемент OrderValidator"],
                           size=12.5, bold=True, fill="#eef2f7", stroke=INK, pad=10)

    sats = [
        ("Розробки",     ["модуль", "order/validation"],                       FIELD, False),
        ("Інформаційна", ["володіє даними", "«чернетка замовлення»"],          FIELD, False),
        ("Конкурентна",  ["пул воркерів:", "N потоків, спільний кеш"],         FIELD, False),
        ("Розгортання",  ["вузол svc-order —", "2 репліки за балансувальником:", "мережевий стрибок!"], POS, True),
        ("Операційна",   ["метрика validator_errors,", "алерт на сплеск"],     FIELD, False),
    ]
    n = len(sats)
    margin, gap = 24, 16
    bw = (W - 2*margin - (n-1)*gap) / n
    row_y = 362
    for i, (vname, body, col, hot) in enumerate(sats):
        x = margin + i*(bw+gap)
        cx = x + bw/2
        frags.append(arrow(hub_cx, hub_cy+hbh/2+2, cx, row_y-44, color=(POS if hot else MUTED), sw=1.5))
        frags.append(fitbox(x, row_y-42, bw, 30, vname, size=12, bold=True,
                            fill=("#fdecea" if hot else "#eef6ee"), stroke=col, pad=5))
        frags.append(fitbox(x, row_y, bw, 78, "\n".join(body), size=10.5,
                            fill="#ffffff", stroke=col, pad=6))
    frags.append(hb)

    b1, w1, h1 = textbox(W/2, 472, "стрілка = correspondence: «той самий елемент, показаний у цій в'ю»",
                         size=11.5, fill="#ffffff", stroke=MUTED, pad=7)
    frags.append(b1)
    b2, w2, h2 = textbox(W/2, 522,
                         "неузгодженість тут (червоне) = баг архітектури: функційна в'ю не бачить мережевого стрибка, який ввела в'ю розгортання",
                         size=11.5, bold=True, fill="#fff7ed", stroke=POS, pad=9)
    frags.append(b2)
    render(os.path.join(OUT, "correspondence-web.svg"), W, H, *frags)


# ── Фігура 7 (detailed): яка перспектива найдужче б'є в яку в'ю ───────────────
def fig_interaction_matrix():
    persp = [
        ("Безпека",        ["С", "В", "В", "Н", "Н", "В", "С"]),
        ("Продуктивність", ["Н", "С", "С", "В", "Н", "В", "С"]),
        ("Доступність",    ["Н", "С", "С", "С", "Н", "В", "В"]),
        ("Еволюція",       ["Н", "В", "С", "Н", "В", "С", "С"]),
    ]
    views = ["Контекст", "Функційна", "Інформац.", "Конкур.", "Розробки", "Розгорт.", "Операц."]
    W = 980
    top = 92
    left = 200
    cw = (W - left - 20) / len(views)
    rh = 54
    H = top + rh*len(persp) + 78
    frags = []
    frags.append(text(W/2, 30, "Яка якість найдужче б'є в яку в'ю: перспектива — не рівна пляма", size=16, bold=True))
    frags.append(text(W/2, 55, "рядок — перспектива, стовпець — в'ю; клітинка — сила впливу", size=12, italic=True, color=MUTED))

    for j, v in enumerate(views):
        x = left + j*cw
        frags.append(text(x+cw/2, top-10, v, size=11, bold=True, color=INK))

    shade = {"В": "#f0a58f", "С": "#f8dcc6", "Н": "#f2f4f6"}
    for i, (pname, cells) in enumerate(persp):
        y = top + i*rh
        frags.append(fitbox(20, y+4, left-44, rh-12, pname, size=12.5, bold=True, fill="#eef2f7", stroke=INK, pad=6))
        for j, cval in enumerate(cells):
            x = left + j*cw
            frags.append(rect(x+4, y+4, cw-8, rh-12, fill=shade[cval], stroke="#ffffff", sw=1.5, rx=4))
            frags.append(text(x+cw/2, y+4+(rh-12)/2+5, cval, size=14, bold=True, color=INK))

    items = [("В", "високий"), ("С", "середній"), ("Н", "низький")]
    ly = top + rh*len(persp) + 34
    for k, (sym, word) in enumerate(items):
        gx = 30 + k*180
        frags.append(rect(gx, ly-14, 16, 16, fill=shade[sym], stroke=MUTED, sw=1, rx=3))
        frags.append(text(gx+24, ly, "%s — %s вплив" % (sym, word), size=11.5, color=INK, anchor="start"))
    frags.append(text(W-20, ly, "Rozanski/Woods дають таку таблицю під кожну перспективу", size=11, italic=True, color=MUTED, anchor="end"))
    render(os.path.join(OUT, "interaction-matrix.svg"), W, H, *frags)


# ── Фігура 8 (proj): конвеєр перевірника — опис→групи→2 перевірки→ворота ──────
def fig_check_pipeline():
    W, H = 1000, 340
    frags = []
    frags.append(text(W/2, 30, "Перевірник консистентності: опис як дані → групи → дві перевірки → ворота", size=16, bold=True))
    y = 165
    boxes = [
        ("1. Опис як дані", ["маніфестації в усіх в'ю", "+ відповідності (ISO 42010)", "+ вузли й мережеві зв'язки"], "#eef2f7", INK),
        ("2. Резолвер груп", ["обхід графа відповідностей", "з visited-set —", "стійкий до циклів"], "#eaf0fd", NEG),
        ("3. Дві перевірки", ["покриття E×V (сироти)", "+ хибно-локальні виклики", "(local проти мережі)"], "#e9f5ee", FIELD),
        ("4. Вердикт", ["список порушень +", "код виходу: 0 або 1", "= ворота складання"], "#fff7ed", POS),
    ]
    n = len(boxes); margin = 30; gap = 34
    bw = (W - 2*margin - (n-1)*gap) / n
    xs = []
    for i, (title, body, fill, col) in enumerate(boxes):
        x = margin + i*(bw+gap); xs.append(x)
        frags.append(fitbox(x, y-58, bw, 40, title, size=13, bold=True, fill=fill, stroke=col, pad=6))
        b, _, _ = textbox(x+bw/2, y+30, body, size=10.5, fill="#ffffff", stroke=col, pad=8)
        frags.append(b)
        if i > 0:
            frags.append(arrow(xs[i-1]+bw+3, y-38, x-3, y-38, color=INK, sw=1.8))
    b, _, _ = textbox(W/2, H-24, "усе, що зловлено, — на кресленні, а не в проді: ворота падають на неузгодженому описі",
                      size=11.5, bold=True, fill="#ffffff", stroke=INK, pad=9)
    frags.append(b)
    render(os.path.join(OUT, "check-pipeline.svg"), W, H, *frags)


# ── Фігура 9 (proj): хибно-локальний виклик — local проти мережевого стрибка ──
def fig_local_vs_remote():
    W, H = 1000, 560
    frags = []
    frags.append(text(W/2, 30, "Хибно-локальний виклик: та сама стрілка — «local» у функційній, мережа в розгортанні", size=15, bold=True))

    # ── ліва панель: функційна в'ю ──
    frags.append(rect(30, 58, 440, 350, fill="#f7f9fb", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(250, 84, "Функційна в'ю каже:", size=13.5, bold=True, color=INK))
    frags.append(fitbox(175, 118, 150, 44, "OrderApi", size=13, bold=True, fill="#eef2f7", stroke=INK, pad=6))
    frags.append(fitbox(175, 250, 150, 44, "OrderValidator", size=13, bold=True, fill="#eef2f7", stroke=INK, pad=6))
    frags.append(arrow(250, 164, 250, 246, color=POS, sw=2.2))
    frags.append(text(272, 200, "validate()", size=12, color=INK, anchor="start"))
    frags.append(text(272, 220, "kind: local", size=12, bold=True, color=POS, anchor="start"))
    b, _, _ = textbox(250, 352, ["обіцянка: «миттєвий,", "надійний, локальний виклик»"], size=11, fill="#ffffff", stroke=MUTED, pad=8)
    frags.append(b)

    # ── права панель: в'ю розгортання ──
    frags.append(rect(530, 58, 440, 350, fill="#f7f9fb", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(750, 84, "В'ю розгортання каже:", size=13.5, bold=True, color=INK))
    frags.append(fitbox(675, 110, 150, 40, "вузол svc-api", size=12, bold=True, fill="#eef2f7", stroke=INK, pad=5))
    frags.append(fitbox(660, 200, 180, 40, "балансувальник\nlb-order", size=11.5, bold=True, fill="#fbeee6", stroke=POS, pad=5))
    frags.append(fitbox(575, 320, 160, 40, "svc-order-1", size=12, bold=True, fill="#fdecea", stroke=POS, pad=5))
    frags.append(fitbox(765, 320, 160, 40, "svc-order-2", size=12, bold=True, fill="#fdecea", stroke=POS, pad=5))
    frags.append(arrow(750, 150, 750, 196, color=NEG, sw=1.8))
    frags.append(arrow(730, 240, 655, 316, color=NEG, sw=1.8))
    frags.append(arrow(770, 240, 845, 316, color=NEG, sw=1.8))
    frags.append(text(750, 288, "мережа", size=10.5, italic=True, color=NEG))
    b, _, _ = textbox(750, 388, "OrderValidator = 2 репліки за балансувальником", size=11, fill="#ffffff", stroke=MUTED, pad=7)
    frags.append(b)

    # ── низ: правило рішення ──
    b, _, _ = textbox(W/2, 468,
                      ["Ціль реплікована на 2 вузли  →  виклик іде МЕРЕЖЕЮ через балансувальник  →  має бути remote.",
                       "Оголошено «local»  →  ХИБНО-ЛОКАЛЬНИЙ виклик: баг, якого функційна в'ю сама не бачить."],
                      size=11.5, bold=True, fill="#fff7ed", stroke=POS, pad=11)
    frags.append(b)
    render(os.path.join(OUT, "local-vs-remote.svg"), W, H, *frags)


# ── Фігура 10 (proj): матриця покриття — елемент × в'ю, сирота в порожній клітинці ──
def fig_coverage_grid():
    elems = ["OrderApi", "OrderValidator", "PricingEngine", "AuditLog"]
    views = ["Функційна", "Розробки", "Конкурентна", "Розгортання"]
    cov = {
        "OrderApi":       [True, True, True, True],
        "OrderValidator": [True, True, True, True],
        "PricingEngine":  [True, True, True, True],
        "AuditLog":       [True, True, False, True],   # ← немає прояву в конкурентній
    }
    W = 860
    top = 100
    left = 40
    lw = 190
    cw = (W - left - lw - 20) / len(views)
    rh = 52
    H = top + rh*len(elems) + 96
    frags = []
    frags.append(text(W/2, 30, "Перевірка покриття: кожен елемент × кожна обов'язкова в'ю", size=16, bold=True))
    frags.append(text(W/2, 55, "✓ прояв є · ✗ сирота: елемент завис без місця в цій в'ю", size=12, italic=True, color=MUTED))
    for j, v in enumerate(views):
        x = left + lw + j*cw
        frags.append(text(x+cw/2, top-14, v, size=11.5, bold=True, color=INK))
    for i, e in enumerate(elems):
        y = top + i*rh
        frags.append(fitbox(left, y+4, lw-16, rh-12, e, size=12.5, bold=True, fill="#eef2f7", stroke=INK, pad=6))
        for j in range(len(views)):
            x = left + lw + j*cw
            ok = cov[e][j]
            stroke = FIELD if ok else POS
            frags.append(rect(x+4, y+4, cw-8, rh-12, fill=("#e9f5ee" if ok else "#fdecea"), stroke=stroke, sw=1.6, rx=5))
            frags.append(text(x+cw/2, y+4+(rh-12)/2+6, "✓" if ok else "✗", size=17, bold=True, color=stroke))
    b, _, _ = textbox(W/2, top+rh*len(elems)+48,
                      ["AuditLog є у функційній, розробці й розгортанні — але завис без конкурентної в'ю: хто його виконує?",
                       "Обхід «елемент × в'ю» ловить порожню клітинку за один прохід."],
                      size=11.5, bold=True, fill="#ffffff", stroke=POS, pad=9)
    frags.append(b)
    render(os.path.join(OUT, "coverage-grid.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_grid()
    fig_viewpoints()
    fig_chain()
    fig_lineage()
    fig_viewpoint_anatomy()
    fig_correspondence_web()
    fig_interaction_matrix()
    fig_check_pipeline()
    fig_local_vs_remote()
    fig_coverage_grid()
    print("figures written to", OUT)
