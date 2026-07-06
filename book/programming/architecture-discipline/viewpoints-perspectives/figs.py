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


if __name__ == "__main__":
    fig_grid()
    fig_viewpoints()
    fig_chain()
    fig_lineage()
    print("figures written to", OUT)
