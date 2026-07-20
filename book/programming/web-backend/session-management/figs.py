# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_pointer():
    """Клієнт тримає беззмістовний номер; правда — у сховищі сесій на сервері."""
    W, H = 880, 390
    frags = []
    frags.append(text(W / 2, 30, "Сесія: клієнт носить указівник, правда живе на сервері",
                      size=17, bold=True))

    # ── клієнт ліворуч
    cb, _, _ = textbox(160, 195, "клієнт\n\ncookie:\nsid = a8f3…9c", size=13, min_w=175)
    frags.append(cb)
    frags.append(text(160, 300, "беззмістовний номер", size=12, color=MUTED))

    # ── стрілка запиту
    frags.append(arrow(262, 175, 468, 175, color=FIELD, sw=2.3))
    frags.append(text(365, 164, "запит везе cookie", size=12, color=INK))

    # ── сервер праворуч зі сховищем
    frags.append(rect(478, 92, 384, 236, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(670, 118, "сервер", size=14, bold=True))
    frags.append(text(670, 140, "сховище сесій", size=12, color=MUTED))
    r1, _, _ = textbox(670, 188, "a8f3…9c → Марія · адмін · 14:03", size=12,
                       min_w=344, fill="#eafaf1", stroke=FIELD)
    r2, _, _ = textbox(670, 238, "b71c…4e → Іван · читач · 13:40", size=12,
                       min_w=344, fill=FILL, stroke=LINE, color=MUTED)
    r3, _, _ = textbox(670, 288, "5d90…2a → Оля · читач · 12:05", size=12,
                       min_w=344, fill=FILL, stroke=LINE, color=MUTED)
    frags += [r1, r2, r3]

    frags.append(text(W / 2, 366,
                      "клієнт тримає лише вказівник — правда живе на сервері",
                      size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "pointer.svg"), W, H, *frags)


def fig_lifecycle():
    """Життя сесії: вхід, два таймаути (ковзний простій + абсолют), знищення запису."""
    W, H = 960, 360
    frags = []
    frags.append(text(W / 2, 30, "Життя сесії: два лічильники стережуть її з різних боків",
                      size=17, bold=True))

    # ── вісь часу
    ay = 130
    frags.append(arrow(100, ay, 830, ay, color=INK, sw=2))
    frags.append(text(838, ay - 4, "час", size=12, color=MUTED, anchor="start"))

    # вхід
    frags.append(circle(150, ay, 7, fill=BG, stroke=INK, sw=2.2))
    frags.append(text(150, ay - 18, "вхід", size=13, bold=True))
    frags.append(mtext(150, ay + 32, "створити запис\n+ Set-Cookie", size=10, color=MUTED))

    # активні запити
    for x in (300, 380, 460, 540):
        frags.append(circle(x, ay, 5, fill=BG, stroke=MUTED, sw=1.8))
    frags.append(text(420, ay - 18, "активні запити", size=12, color=MUTED))

    # кінець
    frags.append(circle(760, ay, 7, fill=BG, stroke=POS, sw=2.2))
    frags.append(text(760, ay - 18, "вихід / згасання", size=12, color=POS))

    # ── бар А: ковзний таймаут простою
    frags.append(arrow(150, 214, 560, 214, color=FIELD, sw=2.4))
    for x in (300, 380, 460):
        frags.append(line(x, 208, x, 220, color=FIELD, sw=1.6))
    frags.append(text(350, 242, "таймаут простою — кожна дія зсуває дедлайн уперед",
                      size=11, color=FIELD))

    # ── бар Б: абсолютний строк
    frags.append(line(150, 288, 700, 288, color=INK, sw=2.4))
    frags.append(line(700, 278, 700, 298, color=POS, sw=3))
    frags.append(text(400, 314, "абсолютний строк — тверда стеля, не рухається",
                      size=11, color=MUTED))

    # ── розв'язка
    ob, _, _ = textbox(770, 214, "запис знищено\nна сервері →\nномер мертвий", size=11,
                       min_w=170, fill="#fdecea", stroke=POS)
    frags.append(ob)

    render(os.path.join(IMG, "lifecycle.svg"), W, H, *frags)


def fig_fixation():
    """Фіксація сесії: без ротації номера вхід зламано; з ротацією на вході — захищено."""
    W, H = 1000, 430
    frags = []
    frags.append(text(W / 2, 30, "Фіксація сесії живе доти, доки номер переживає вхід",
                      size=16, bold=True))

    cols = [240, 530, 820]

    # ── верхній ряд: без ротації (зламано)
    ty = 150
    frags.append(mtext(70, ty - 8, "без\nротації", size=12, color=POS, bold=True))
    b1, _, _ = textbox(cols[0], ty, "зловмисник має\nномер X (анонімний)", size=12,
                       min_w=200, stroke=POS)
    b2, _, _ = textbox(cols[1], ty, "жертва входить,\nномер лишається X", size=12,
                       min_w=200, stroke=MUTED)
    b3, _, _ = textbox(cols[2], ty, "зловмисник\nзаходить як жертва", size=12,
                       min_w=200, stroke=POS, fill="#fdecea")
    frags += [b1, b2, b3]
    frags.append(arrow(345, ty, 428, ty, color=MUTED))
    frags.append(text(386, ty - 12, "підсовує", size=10, color=MUTED))
    frags.append(arrow(635, ty, 718, ty, color=MUTED))
    frags.append(text(cols[2], ty + 40, "✗ вхід зламано", size=12, color=POS, bold=True))

    # роздільник
    frags.append(line(40, 240, 960, 240, color=LINE, sw=1, dash="2 5"))

    # ── нижній ряд: з ротацією на вході (захищено)
    by = 330
    frags.append(mtext(70, by - 8, "з ротацією\nна вході", size=12, color=FIELD, bold=True))
    c1, _, _ = textbox(cols[0], by, "жертва входить", size=12, min_w=200, stroke=FIELD)
    c2, _, _ = textbox(cols[1], by, "у жертви — новий Y,\nстарий X мертвий", size=12,
                       min_w=200, stroke=FIELD, fill="#eafaf1")
    c3, _, _ = textbox(cols[2], by, "копія X у зловмисника\nнічого не варта", size=12,
                       min_w=200, stroke=FIELD)
    frags += [c1, c2, c3]
    frags.append(arrow(345, by, 428, by, color=FIELD))
    frags.append(text(386, by - 12, "X → Y", size=10, color=FIELD))
    frags.append(arrow(635, by, 718, by, color=FIELD))
    frags.append(text(cols[2], by + 42, "✓ вхід захищено", size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, "fixation.svg"), W, H, *frags)


def fig_scaling():
    """Багато серверів: липкі сесії проти спільного сховища."""
    W, H = 1000, 430
    frags = []
    frags.append(text(W / 2, 30, "Коли серверів багато: де тримати сховище сесій",
                      size=16, bold=True))

    # роздільник панелей
    frags.append(line(500, 62, 500, 402, color=LINE, sw=1, dash="2 5"))

    # ── ЛІВА панель: липкі сесії
    frags.append(text(250, 70, "липкі сесії", size=14, bold=True, color=POS))
    lb, _, _ = textbox(250, 112, "балансувальник", size=12, min_w=180)
    frags.append(lb)
    s1, _, _ = textbox(150, 205, "сервер 1", size=11, min_w=95)
    s2, _, _ = textbox(250, 205, "сервер 2", size=11, min_w=95, stroke=POS, fill="#fdecea")
    s3, _, _ = textbox(350, 205, "сервер 3", size=11, min_w=95)
    frags += [s1, s2, s3]
    frags.append(arrow(250, 134, 250, 188, color=INK))
    frags.append(text(300, 160, "прив'язка", size=10, color=MUTED, anchor="start"))
    mb, _, _ = textbox(250, 270, "сесія в пам'яті\nсервера 2", size=11, min_w=150,
                       fill="#fdecea", stroke=POS)
    frags.append(mb)
    frags.append(text(250, 322, "сервер 2 помер → сесію втрачено", size=11, color=POS))

    # ── ПРАВА панель: спільне сховище
    frags.append(text(750, 70, "спільне сховище", size=14, bold=True, color=FIELD))
    rb, _, _ = textbox(750, 112, "балансувальник", size=12, min_w=180)
    frags.append(rb)
    t1, _, _ = textbox(650, 205, "сервер 1", size=11, min_w=95)
    t2, _, _ = textbox(750, 205, "сервер 2", size=11, min_w=95)
    t3, _, _ = textbox(850, 205, "сервер 3", size=11, min_w=95)
    frags += [t1, t2, t3]
    frags.append(arrow(730, 134, 662, 188, color=MUTED))
    frags.append(arrow(750, 134, 750, 188, color=MUTED))
    frags.append(arrow(770, 134, 838, 188, color=MUTED))
    store, _, _ = textbox(750, 290, "спільне сховище (Redis)", size=12, min_w=260,
                          fill="#eafaf1", stroke=FIELD)
    frags.append(store)
    frags.append(arrow(650, 222, 706, 268, color=FIELD))
    frags.append(arrow(750, 222, 750, 268, color=FIELD))
    frags.append(arrow(850, 222, 794, 268, color=FIELD))
    frags.append(text(750, 336, "будь-який сервер — будь-яка сесія", size=11, color=FIELD))

    frags.append(text(W / 2, 414,
                      "у пам'яті сервера сесія прив'язує до нього; у спільному сховищі сервери взаємозамінні",
                      size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "scaling.svg"), W, H, *frags)


def fig_store_layers():
    """Проєкт: один інтерфейс сховища, дві реалізації, політика й HTTP над ним."""
    W, H = 940, 480
    frags = []
    frags.append(text(W / 2, 32, "Склад сесій: політика незмінна, механізм сховища — змінний",
                      size=16, bold=True))

    cx = 470
    # ── HTTP-шар
    b1, _, _ = textbox(cx, 92, "HTTP-шар:  login · logout · кожен запит", size=13, min_w=540)
    frags.append(b1)
    frags.append(arrow(cx, 114, cx, 152, color=INK, sw=2))

    # ── SessionManager (політика)
    b2, _, _ = textbox(cx, 196,
                       "SessionManager — політика\n"
                       "номер із CSPRNG · ковзний простій + абсолютний строк\n"
                       "ротація на вході · відкликання на виході",
                       size=12, min_w=560, fill="#eafaf1", stroke=FIELD)
    frags.append(b2)
    frags.append(arrow(cx, 232, cx, 270, color=INK, sw=2))
    frags.append(text(cx + 16, 255, "інтерфейс:  create · lookup · rotate · destroy",
                      size=11, color=MUTED, anchor="start"))

    # ── Store (інтерфейс)
    b3, _, _ = textbox(cx, 300, "Store — інтерфейс сховища", size=13, min_w=320)
    frags.append(b3)

    # ── дві реалізації
    frags.append(arrow(cx - 70, 322, 290, 368, color=MUTED, sw=1.8))
    frags.append(arrow(cx + 70, 322, 650, 368, color=MUTED, sw=1.8))
    m1, _, _ = textbox(290, 396, "у пам'яті: Map\n+ прибирання (sweep)", size=12,
                       min_w=230, stroke=MUTED)
    m2, _, _ = textbox(650, 396, "Redis: спільне сховище\nкілька серверів", size=12,
                       min_w=250, stroke=MUTED)
    frags += [m1, m2]
    frags.append(text(290, 438, "розробка / один процес", size=11, color=MUTED))
    frags.append(text(650, 438, "прод / горизонталь", size=11, color=MUTED))

    frags.append(text(W / 2, 466,
                      "поміняти сховище — не торкнувшись ні політики, ні HTTP: обидва бачать лише інтерфейс",
                      size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "store-layers.svg"), W, H, *frags)


def fig_lookup_flow():
    """Мозок сховища: lookup зводить обидва таймаути в одну точку рішення."""
    W, H = 900, 540
    frags = []
    frags.append(text(W / 2, 32, "lookup(sid): обидва лічильники сходяться в одному рішенні",
                      size=16, bold=True))

    cx = 310
    # старт
    s0, _, _ = textbox(cx, 82, "lookup(sid)", size=13, min_w=190, bold=True)
    frags.append(s0)
    frags.append(arrow(cx, 104, cx, 146, color=INK, sw=2))

    # D1 — чи є запис
    d1, _, _ = textbox(cx, 178, "є запис sess:sid\nу сховищі?", size=12, min_w=240)
    frags.append(d1)
    frags.append(arrow(cx + 122, 178, 585, 178, color=POS, sw=1.8))
    frags.append(text(470, 168, "ні", size=11, color=POS))
    r1, _, _ = textbox(690, 178, "null — анонім", size=12, min_w=185,
                       stroke=POS, fill="#fdecea")
    frags.append(r1)
    frags.append(arrow(cx, 204, cx, 246, color=FIELD, sw=2))
    frags.append(text(cx + 14, 230, "так", size=11, color=FIELD, anchor="start"))

    # D2 — абсолютна стеля
    d2, _, _ = textbox(cx, 282, "now − createdAt ≥\nабсолютний строк?", size=12, min_w=260)
    frags.append(d2)
    frags.append(arrow(cx + 132, 282, 585, 282, color=POS, sw=1.8))
    frags.append(text(470, 272, "так", size=11, color=POS))
    r2, _, _ = textbox(690, 282, "destroy(sid)\n→ null", size=12, min_w=185,
                       stroke=POS, fill="#fdecea")
    frags.append(r2)
    frags.append(arrow(cx, 308, cx, 350, color=FIELD, sw=2))
    frags.append(text(cx + 14, 334, "ні", size=11, color=FIELD, anchor="start"))

    # A3 — ковзання, обмежене абсолютом
    a3, _, _ = textbox(cx, 388, "ковзання: EXPIRE sess:sid\n= min(idle, абсолют − now)",
                       size=12, min_w=340, fill="#eafaf1", stroke=FIELD)
    frags.append(a3)
    frags.append(arrow(cx, 416, cx, 458, color=INK, sw=2))

    # результат
    r3, _, _ = textbox(cx, 490, "повернути Session", size=13, min_w=240, stroke=FIELD)
    frags.append(r3)

    frags.append(text(W / 2, 524,
                      "idle — це TTL ключа, що ковзає; абсолют — поле createdAt, що обмежує ковзання",
                      size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "lookup-flow.svg"), W, H, *frags)


def fig_timeline():
    """Народження стану поверх безпам'ятного HTTP — сім віх від Unix-cookie до фіксації сесії."""
    W, H = 1240, 400
    frags = []
    frags.append(text(W / 2, 32, "Як стан наклали на HTTP: сім віх", size=17, bold=True))

    ay = 205
    frags.append(line(90, ay, 1150, ay, color=INK, sw=2))
    frags.append(arrow(1150, ay, 1176, ay, color=INK, sw=2))
    frags.append(text(1184, ay + 4, "час", size=12, color=MUTED, anchor="start"))

    xs = [140, 300, 460, 620, 780, 940, 1100]
    events = [
        ("1979", "Unix: «magic cookie»\n(fseek / ftell)"),
        ("1991", "HTTP без стану\n(CERN)"),
        ("літо 1994", "Монтуллі: cookie\nдля кошика"),
        ("лют. 1996", "Financial Times\nрозкриває cookie"),
        ("лют. 1997", "RFC 2109\n(Крістол, Монтуллі)"),
        ("кін. 1990-х", "HttpSession:\nсерверна сесія"),
        ("груд. 2002", "«фіксація сесії»\n(Колшек)"),
    ]
    for i, (x, (yr, desc)) in enumerate(zip(xs, events)):
        above = (i % 2 == 0)
        frags.append(circle(x, ay, 6, fill=BG, stroke=INK, sw=2.2))
        if above:
            frags.append(line(x, ay - 6, x, 136, color=MUTED, sw=1.2))
            b, _, _ = textbox(x, 110, desc, size=11, min_w=200)
            frags.append(b)
            frags.append(text(x, ay + 22, yr, size=12, bold=True))
        else:
            frags.append(line(x, ay + 6, x, 274, color=MUTED, sw=1.2))
            b, _, _ = textbox(x, 300, desc, size=11, min_w=200)
            frags.append(b)
            frags.append(text(x, ay - 14, yr, size=12, bold=True))

    frags.append(text(W / 2, 378,
                      "кожна латка — відповідь на брак пам'яті, якого HTTP не мусив закривати",
                      size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "timeline.svg"), W, H, *frags)


def fig_entropy_vs_length():
    """Довжина — не ентропія: та сама ентропія в різних кодуваннях; довгий передбачуваний рядок."""
    W, H = 1000, 452
    frags = []
    frags.append(text(W / 2, 32, "Довжина — не ентропія: стійкість живе в бітах, не в символах",
                      size=17, bold=True))

    # ── верх: той самий випадок, три кодування
    frags.append(text(610, 80, "той самий випадок, різні кодування → та сама ентропія",
                      size=12, color=MUTED))
    frags.append(mtext(112, 150, "той самий\n128-бітний\nвипадок", size=12, bold=True))

    b1, _, _ = textbox(380, 150, "16 сирих байтів\na3 f2 … 4e", size=12, min_w=185)
    b2, _, _ = textbox(610, 150, "32 hex-символи\na3f2 … 9c4e", size=12, min_w=185)
    b3, _, _ = textbox(840, 150, "24 base64-символи\no8_K … Tg", size=12, min_w=185)
    frags += [b1, b2, b3]
    for x in (380, 610, 840):
        frags.append(text(x, 200, "= 128 біт ентропії", size=12, color=FIELD, bold=True))

    # ── роздільник
    frags.append(line(60, 244, 940, 244, color=LINE, sw=1, dash="2 5"))

    # ── низ: довгий, але передбачуваний
    frags.append(mtext(112, 336, "довгий, але\nпередбачуваний", size=12, bold=True, color=POS))
    frags.append(text(575, 296, "стала + лічильник + дата — усе вгадується",
                      size=11, color=MUTED))
    lb, _, _ = textbox(575, 338, "sess_user_10427_20260718_prod", size=13, min_w=390,
                       stroke=POS, fill="#fdecea")
    frags.append(lb)
    frags.append(text(575, 390, "29 символів · лише ~10 біт справжньої ентропії",
                      size=12, color=POS, bold=True))

    frags.append(text(W / 2, 436,
                      "довжину задає кодування, стійкість — ентропія від CSPRNG",
                      size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "entropy-vs-length.svg"), W, H, *frags)


def fig_entropy_wall():
    """Стіна подвоєння: рівні кроки по бітах, час стрибає в 65 536 разів."""
    W, H = 1000, 402
    frags = []
    frags.append(text(W / 2, 32, "Стіна подвоєння: +16 бітів множать час перебору на 65 536",
                      size=17, bold=True))

    x0 = 262
    k = 6.4
    rows = [
        (32, "≈ 4 секунди", POS, False),
        (48, "≈ 3.3 дня", POS, False),
        (64, "≈ 585 років", FIELD, True),
        (80, "≈ 38 мільйонів років", FIELD, False),
    ]
    ys = [100, 170, 240, 310]
    for (bits, tlabel, tcol, hi), y in zip(rows, ys):
        w = bits * k
        if hi:  # підсвітити робочий поріг
            frags.append(rect(60, y - 26, 880, 52, fill="#eafaf1", stroke=FIELD,
                              sw=1.4, rx=7))
        frags.append(text(238, y + 5, "%d біти" % bits, size=13, bold=True, anchor="end"))
        frags.append(rect(x0, y - 13, w, 26, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=5))
        frags.append(text(x0 + w + 16, y + 5, tlabel, size=13, color=tcol, bold=True,
                          anchor="start"))

    frags.append(text(W / 2, 378,
                      "кроки по осі бітів рівні — час стрибає в 65 536 разів на кожному "
                      "(темп 10 000/с, 100 000 сесій)",
                      size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "entropy-wall.svg"), W, H, *frags)


def fig_two_bounds():
    """Дві межі 2^b: вгадування (2^b/(A·S)) проти колізії (2^(b/2))."""
    W, H = 1040, 462
    frags = []
    frags.append(text(W / 2, 32, "Дві різні межі того самого простору 2^b",
                      size=17, bold=True))

    # роздільник панелей
    frags.append(line(520, 58, 520, 404, color=LINE, sw=1, dash="2 5"))

    # ── ЛІВА: вгадування ────────────────────────────────────────────────
    frags.append(text(260, 74, "вгадування (нападник ззовні)", size=14, bold=True, color=POS))
    frags.append(rect(128, 92, 264, 132, fill="#f9fbff", stroke=LINE, sw=1.4))
    frags.append(text(260, 110, "простір 2^b значень", size=11, color=MUTED))
    # чинні сесії — зелені клітини
    for x, y in ((178, 150), (258, 188), (338, 158)):
        frags.append(rect(x - 7, y - 7, 14, 14, fill=FIELD, stroke=FIELD, sw=1, rx=2))
    frags.append(text(258, 214, "S чинних цілей", size=10, color=FIELD))
    # промахи-спроби
    for x, y in ((208, 138), (300, 176), (162, 198), (356, 196), (222, 206), (320, 140)):
        frags.append(text(x, y + 4, "×", size=12, color=MUTED))
    # стрілка перебору
    frags.append(arrow(96, 128, 150, 150, color=POS, sw=2))
    frags.append(text(92, 116, "A·t пострілів", size=10, color=POS, anchor="start"))

    fb1, _, _ = textbox(260, 300, "стійкість ≈ 2^b / (A·S)", size=14, min_w=250,
                        stroke=POS, fill="#fdecea", bold=True)
    frags.append(fb1)
    frags.append(text(260, 344, "64 біти → 585 років марно", size=12, color=FIELD, bold=True))
    frags.append(text(260, 372, "більше живих сесій → легше нападнику", size=11, color=MUTED))

    # ── ПРАВА: колізія ──────────────────────────────────────────────────
    frags.append(text(780, 74, "колізія (сервер сам, зсередини)", size=14, bold=True, color=NEG))
    frags.append(text(780, 108, "видає номери один за одним", size=11, color=MUTED))
    xs = [612, 664, 716, 768, 820, 872]
    match = {664, 820}
    for x in xs:
        f = "#eaf0fd" if x in match else FILL
        st = NEG if x in match else LINE
        frags.append(rect(x - 20, 152, 40, 34, fill=f, stroke=st, sw=1.6, rx=4))
    # дуга-збіг між двома однаковими
    frags.append(line(664, 150, 742, 128, color=POS, sw=2))
    frags.append(line(742, 128, 820, 150, color=POS, sw=2))
    frags.append(text(742, 120, "той самий номер!", size=11, color=POS, bold=True))
    frags.append(text(780, 208, "n виданих ID", size=10, color=MUTED))

    fb2, _, _ = textbox(780, 300, "збіг на n ≈ 2^(b/2) = √(2^b)", size=14, min_w=250,
                        stroke=NEG, fill="#eaf0fd", bold=True)
    frags.append(fb2)
    frags.append(text(780, 344, "64 біти → ~4 млрд ID до ~50%", size=12, color=POS, bold=True))
    frags.append(text(780, 372, "більше виданих ID → важче тобі", size=11, color=MUTED))

    frags.append(text(W / 2, 440,
                      "вгадування масштабується з 2^b, колізія — з коренем 2^(b/2); "
                      "128-бітне тягнення ховає обидві межі",
                      size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "two-bounds.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_pointer()
    fig_lifecycle()
    fig_fixation()
    fig_scaling()
    fig_store_layers()
    fig_lookup_flow()
    fig_timeline()
    fig_entropy_vs_length()
    fig_entropy_wall()
    fig_two_bounds()
    print("ok")
