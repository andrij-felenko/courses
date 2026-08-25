# -*- coding: utf-8 -*-
"""Фігури до теми «HTTP-кешування: Cache-Control, ETag й умовні запити».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"
GRAY  = "#9aa0a6"
PANEL = "#fbfbfb"


# ── 1. Три дороги за ту саму відповідь ────────────────────────────────────────
# Ідея: свіжа копія — нуль мережі; валідація — один обмін без тіла; промах — усе.
def fig_three_paths():
    W, H = 940, 520
    f = [text(W / 2, 30, "Три дороги за ту саму відповідь", size=16, bold=True)]

    panels = [
        dict(y=52, name="СВІЖА КОПІЯ", col=FIELD,
             cost="0 обмінів\n0 байтів у мережі\n0 роботи сервера",
             kind="fresh"),
        dict(y=204, name="ВАЛІДАЦІЯ", col=AMBER,
             cost="1 обмін\n~300 байтів\nбез тіла й без рендера",
             kind="revalidate"),
        dict(y=356, name="ПРОМАХ", col=POS,
             cost="1 обмін\nповне тіло\nповна робота сервера",
             kind="miss"),
    ]

    PW, PH = 900, 138
    px = 20
    for p in panels:
        y = p["y"]
        f.append(rect(px, y, PW, PH, fill=PANEL, stroke=p["col"], sw=1.8, rx=10))
        f.append(text(px + 20, y + 28, p["name"], size=12.5, color=p["col"],
                      anchor="start", bold=True))

        row = y + 88                      # висота, на якій стоять коробки й лінії
        # клієнт
        f.append(fitbox(px + 20, row - 26, 118, 52, "клієнт", size=12))
        # кеш
        f.append(fitbox(px + 178, row - 26, 138, 52, "кеш", size=12,
                        stroke=NEG, fill="#eef2fb"))
        # сервер
        srv_stroke = GRAY if p["kind"] == "fresh" else LINE
        srv_fill = "#f2f3f4" if p["kind"] == "fresh" else FILL
        f.append(fitbox(px + 520, row - 26, 148, 52, "сервер", size=12,
                        stroke=srv_stroke, fill=srv_fill,
                        color=(MUTED if p["kind"] == "fresh" else INK)))

        # клієнт → кеш
        f.append(arrow(px + 142, row, px + 174, row, color=INK, sw=1.6))

        if p["kind"] == "fresh":
            # запит далі не йде: коротка пунктирна нитка й стоп-риска
            f.append(line(px + 320, row, px + 392, row, color=GRAY, sw=1.6, dash="6 5"))
            f.append(line(px + 396, row - 17, px + 396, row + 17, color=POS, sw=3.4))
            f.append(text(px + 358, row + 44, "далі запит не йде", size=11,
                          color=MUTED, italic=True))
        elif p["kind"] == "revalidate":
            f.append(text(px + 420, row - 22, "GET + If-None-Match: \"v7\"", size=11.5, color=INK))
            f.append(arrow(px + 320, row, px + 516, row, color=INK, sw=1.6))
            f.append(text(px + 420, row + 44, "304 Not Modified — заголовки без тіла",
                          size=11.5, color=FIELD))
            f.append(arrow(px + 516, row + 22, px + 320, row + 22, color=FIELD, sw=1.6))
        else:
            f.append(text(px + 420, row - 22, "GET (кеш нічим не може допомогти)",
                          size=11.5, color=INK))
            f.append(arrow(px + 320, row, px + 516, row, color=INK, sw=1.6))
            f.append(text(px + 420, row + 44, "200 OK + усі 180 КБ тіла", size=11.5, color=POS))
            f.append(arrow(px + 516, row + 22, px + 320, row + 22, color=POS, sw=1.6))

        # ціна — окрема колонка праворуч, без сусідів
        f.append(fitbox(px + 690, y + 40, 192, 84, p["cost"], size=11,
                        fill="#ffffff", stroke=p["col"], sw=1.4, color=p["col"]))

    render(os.path.join(IMG, "three-paths.svg"), W, H, *f)


# ── 2. Ланцюг кешів: хто зберігає копію ───────────────────────────────────────
# Ідея: копія лежить у кількох місцях, і директиви адресовані РІЗНИМ місцям.
def fig_cache_chain():
    W, H = 960, 500
    f = [text(W / 2, 30, "Ланцюг кешів: кому саме адресована директива", size=16, bold=True)]

    cols = [
        dict(x=24,  w=150, t="клієнт",            sub="",                     col=LINE,  fill=FILL),
        dict(x=204, w=170, t="кеш браузера",      sub="приватний",            col=NEG,   fill="#eef2fb"),
        dict(x=404, w=170, t="CDN",               sub="спільний",             col=AMBER, fill="#fdf6e3"),
        dict(x=604, w=170, t="зворотний проксі",  sub="спільний",             col=AMBER, fill="#fdf6e3"),
        dict(x=804, w=132, t="origin",            sub="джерело правди",       col=POS,   fill="#fdecea"),
    ]
    ytop, bh = 66, 62
    for c in cols:
        f.append(fitbox(c["x"], ytop, c["w"], bh, c["t"], size=12.5,
                        stroke=c["col"], fill=c["fill"], bold=True))
        if c["sub"]:
            f.append(text(c["x"] + c["w"] / 2, ytop + bh + 22, c["sub"],
                          size=11, color=MUTED, italic=True))
    for a, b in zip(cols, cols[1:]):
        f.append(arrow(a["x"] + a["w"] + 4, ytop + bh / 2, b["x"] - 4, ytop + bh / 2,
                       color=GRAY, sw=1.6))

    # хто скільки бачить копію — рядок «вік»
    yage = ytop + bh + 62
    f.append(text(24, yage, "Age у відповіді, що йде назад:", size=11.5,
                  color=MUTED, anchor="start"))
    ages = [("289 → клієнтові", 204, 170), ("289 c", 404, 170), ("240 c", 604, 170), ("0 c", 804, 132)]
    for lbl, x, w in ages:
        f.append(text(x + w / 2, yage + 26, lbl, size=11.5, color=INK))

    # нижня панель — директиви
    py, ph = yage + 52, 232
    f.append(rect(24, py, W - 48, ph, fill=PANEL, stroke=LINE, sw=1.4, rx=10))
    f.append(text(44, py + 28, "директива в Cache-Control відповіді", size=12,
                  color=MUTED, anchor="start", bold=True))
    rows = [
        ("max-age=600",   "строк для будь-якого кеша — і приватного, і спільного", NEG),
        ("s-maxage=60",   "строк лише для СПІЛЬНИХ; браузер його не читає",        AMBER),
        ("private",       "зберігає тільки кеш браузера; CDN і проксі — ні",       NEG),
        ("no-store",      "не записує ніхто, зокрема й браузер",                   POS),
    ]
    ry = py + 48
    for name, meaning, col in rows:
        f.append(fitbox(44, ry, 210, 38, name, size=12, stroke=col,
                        fill="#ffffff", color=col, bold=True))
        f.append(text(276, ry + 24, meaning, size=12, color=INK, anchor="start"))
        ry += 46

    render(os.path.join(IMG, "cache-chain.svg"), W, H, *f)


# ── 3. Життя копії на осі часу ────────────────────────────────────────────────
# Ідея: три зони після народження відповіді й те, що 304 повертає на початок.
def fig_freshness_timeline():
    W, H = 940, 420
    f = [text(W / 2, 30, "Життя однієї копії після того, як сервер її віддав", size=16, bold=True)]

    ax0, ax1, ay = 70, 880, 210
    zones = [
        (70,  360, FIELD, "#eafaf1", "СВІЖА",
         "віддається одразу,\nмережі немає"),
        (360, 590, AMBER, "#fdf6e3", "ПРОСТРОЧЕНА, але з stale-while-revalidate",
         "віддається одразу,\nоновлення — у фоні"),
        (590, 880, POS,   "#fdecea", "ПРОСТРОЧЕНА",
         "без валідації\nвіддавати не можна"),
    ]
    zh = 74
    for x0, x1, col, fill, name, note in zones:
        f.append(rect(x0, ay - zh, x1 - x0, zh, fill=fill, stroke=col, sw=1.8, rx=8))
        f.append(text((x0 + x1) / 2, ay - zh + 24, name, size=11.5, color=col, bold=True))
        f.append(mtext((x0 + x1) / 2, ay - zh + 44, note, size=10.5, color=MUTED))

    f.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    ticks = [(70, "0"), (360, "max-age=300"), (590, "+ swr=200"), (880, "час")]
    for x, lbl in ticks:
        f.append(line(x, ay - 6, x, ay + 8, color=INK, sw=2))
        f.append(text(x, ay + 28, lbl, size=11.5, color=INK))

    f.append(text(ax0 + 6, ay + 56, "вік копії (Age) росте зліва направо — і в браузері, і в CDN",
                  size=11.5, color=MUTED, anchor="start", italic=True))

    # нижня панель — що робить успішна валідація
    py = ay + 78
    f.append(rect(24, py, W - 48, 92, fill=PANEL, stroke=NEG, sw=1.6, rx=10))
    f.append(text(44, py + 30, "304 Not Modified", size=13, color=NEG,
                  anchor="start", bold=True))
    f.append(text(44, py + 58,
                  "сервер надсилає свіжі заголовки без тіла — лічильник віку стартує з нуля,",
                  size=12, color=INK, anchor="start"))
    f.append(text(44, py + 78,
                  "та сама копія знову опиняється в зеленій зоні, не переїхавши мережею вдруге",
                  size=12, color=INK, anchor="start"))

    render(os.path.join(IMG, "freshness-timeline.svg"), W, H, *f)


# ── 4. Ключ кеша — не сама адреса ─────────────────────────────────────────────
# Ідея: Vary добудовує ключ; забутий Vary віддає чужий варіант.
def fig_cache_key_vary():
    W, H = 920, 470
    f = [text(W / 2, 30, "Ключ кеша: адреса плюс те, що назвав Vary", size=16, bold=True)]

    f.append(fitbox(60, 52, 800, 52,
                    "ключ  =  метод  +  повна адреса  +  значення заголовків, перелічених у Vary",
                    size=13, stroke=NEG, fill="#eef2fb", bold=True))

    # одна адреса
    f.append(fitbox(60, 138, 250, 56, "GET /report\nVary: Accept-Encoding", size=12,
                    stroke=LINE, fill=FILL))

    # два варіанти під нею
    variants = [
        (400, 130, FIELD, "Accept-Encoding: gzip", "тіло 42 КБ, стиснене"),
        (400, 208, AMBER, "Accept-Encoding відсутній", "тіло 180 КБ, як є"),
    ]
    for x, y, col, head, body in variants:
        f.append(fitbox(x, y, 440, 62, head + "\n" + body, size=12, stroke=col,
                        fill="#ffffff", color=col))
        f.append(arrow(316, 166, x - 6, y + 31, color=GRAY, sw=1.5))

    f.append(text(180, 216, "два записи під однією адресою", size=11.5,
                  color=MUTED, italic=True))

    # пастка
    py = 300
    f.append(rect(24, py, W - 48, 146, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    f.append(text(44, py + 30, "Пастка: відповідь залежить від заголовка, якого немає у Vary",
                  size=13, color=POS, anchor="start", bold=True))
    f.append(text(44, py + 62,
                  "сервер віддає різний вміст за X-Country, але пише лише Vary: Accept-Encoding",
                  size=12, color=INK, anchor="start"))
    f.append(text(44, py + 88,
                  "→ спільний кеш вважає обидві відповіді одним записом",
                  size=12, color=INK, anchor="start"))
    f.append(text(44, py + 114,
                  "→ наступний відвідувач дістає чужу країну, і це вже не помилка швидкості",
                  size=12, color=INK, anchor="start"))

    render(os.path.join(IMG, "cache-key-vary.svg"), W, H, *f)


# ── 5. Порядок оцінювання передумов (RFC 9110 §13.2.2) ────────────────────────
# Ідея: умовні заголовки перевіряють НЕ всі підряд, а драбинкою з відсіканням.
def fig_precondition_order():
    W, H = 1000, 636
    f = [text(W / 2, 30, "Порядок оцінювання умовних заголовків", size=16, bold=True),
         text(W / 2, 54, "перевіряють згори вниз; хибна умова обриває драбину відразу",
              size=11.5, color=MUTED, italic=True)]

    SX, SW, SH = 36, 430, 62
    OX, OW = 560, 404
    steps = [
        (76,  "1 · If-Match\nлише origin · суворе порівняння",
              "хибно → 412 Precondition Failed", POS),
        (166, "2 · If-Unmodified-Since\nлише origin · лише якщо If-Match немає",
              "хибно → 412 Precondition Failed", POS),
        (256, "3 · If-None-Match\nбудь-який метод · слабке порівняння",
              "збіг → 304 для GET і HEAD\nінші методи → 412", FIELD),
        (346, "4 · If-Modified-Since\nлише GET/HEAD · лише якщо If-None-Match немає",
              "не змінювалося → 304 Not Modified", FIELD),
        (436, "5 · If-Range разом із Range\nлише GET · суворе порівняння",
              "збіглося → 206 Partial Content\nні → Range відкидають, 200 OK", AMBER),
    ]
    for i, (y, left, right, col) in enumerate(steps):
        f.append(fitbox(SX, y, SW, SH, left, size=12.5, stroke=NEG, fill="#eef2fb"))
        f.append(fitbox(OX, y, OW, SH, right, size=12, stroke=col,
                        fill="#ffffff", color=col))
        f.append(arrow(SX + SW + 6, y + SH / 2, OX - 6, y + SH / 2, color=col, sw=1.5))
        if i < len(steps) - 1:
            f.append(arrow(140, y + SH + 4, 140, y + SH + 24, color=INK, sw=1.6))
            f.append(text(154, y + SH + 20, "істина", size=10.5,
                          color=MUTED, anchor="start", italic=True))

    f.append(arrow(140, 436 + SH + 4, 140, 436 + SH + 24, color=INK, sw=1.6))
    f.append(text(154, 436 + SH + 20, "істина", size=10.5,
                  color=MUTED, anchor="start", italic=True))
    f.append(fitbox(36, 526, 928, 56,
                    "6 · усі передумови справдилися → виконати метод і відповісти як звичайно",
                    size=13, stroke=LINE, fill=PANEL, bold=True))
    render(os.path.join(IMG, "precondition-order.svg"), W, H, *f)


# ── 6. Звідки береться freshness_lifetime ─────────────────────────────────────
# Ідея: чотири джерела строку з жорстким пріоритетом + звуження з боку запиту.
def fig_freshness_precedence():
    W, H = 940, 566
    f = [text(W / 2, 30, "Звідки береться freshness_lifetime", size=16, bold=True),
         text(W / 2, 54, "перший рядок, що справдився, дає відповідь — нижче вже не дивляться",
              size=11.5, color=MUTED, italic=True)]

    RX, RW, RH = 36, 470, 64
    FX, FW = 546, 358
    rows = [
        (78,  "s-maxage=N\nтільки коли кеш СПІЛЬНИЙ", "freshness_lifetime = N", AMBER),
        (156, "max-age=N\nбудь-який кеш", "freshness_lifetime = N", NEG),
        (234, "Expires: <дата>\nчитають, тільки якщо max-age немає", "= Expires − Date", NEG),
        (312, "нічого з переліченого немає\nевристична свіжість", "≈ 10 % від (Date − Last-Modified)", MUTED),
    ]
    for y, left, right, col in rows:
        f.append(fitbox(RX, y, RW, RH, left, size=12.5, stroke=col, fill="#ffffff", color=col))
        f.append(fitbox(FX, y, FW, RH, right, size=12.5, stroke=LINE, fill=PANEL))
        f.append(arrow(RX + RW + 6, y + RH / 2, FX - 6, y + RH / 2, color=GRAY, sw=1.5))

    py, ph = 404, 132
    f.append(rect(24, py, W - 48, ph, fill="#eef2fb", stroke=NEG, sw=1.6, rx=10))
    f.append(text(44, py + 28, "Свіжість — ще не дозвіл видати копію: запит уміє звузити результат",
                  size=12.5, color=NEG, anchor="start", bold=True))
    notes = [
        "min-fresh=N — копія має лишатися свіжою ще щонайменше N секунд",
        "max-age=N у ЗАПИТІ — вік копії має бути не більший за N",
        "max-stale=N — навпаки, приймаю прострочену на ≤ N с (без значення — на будь-скільки)",
    ]
    ny = py + 56
    for s in notes:
        f.append(text(44, ny, s, size=12, color=INK, anchor="start"))
        ny += 25

    render(os.path.join(IMG, "freshness-precedence.svg"), W, H, *f)


# ── Машина станів кеша-посередника (вставка proj) ────────────────────
# Ідея: увесь RFC 9111 у коді — це три впорядковані розвилки, а не перелік директив.
def fig_proxy_state_machine():
    W, H = 980, 776
    f = [text(W / 2, 30, "Машина станів кеша-посередника: три розвилки поспіль",
              size=16, bold=True)]

    f.append(rect(20, 50, 940, 176, fill=PANEL, stroke=LINE, sw=1.4, rx=10))
    f.append(text(44, 80, "1 · знайти запис", size=12.5, color=MUTED,
                  anchor="start", bold=True))
    rows1 = [
        (94,  "первинний ключ = метод + URL",
              "запису під ключем немає  →  повний запит до origin"),
        (152, "серед варіантів під ключем — відбір за Vary",
              "жоден варіант не збігся  →  повний запит до origin"),
    ]
    for y, left, right in rows1:
        f.append(fitbox(44, y, 330, 52, left, size=12, stroke=NEG, fill="#eef2fb"))
        f.append(arrow(378, y + 26, 414, y + 26, color=GRAY, sw=1.5))
        f.append(fitbox(418, y, 520, 52, right, size=12, stroke=GRAY, fill="#ffffff",
                        color=MUTED))

    f.append(rect(20, 244, 940, 246, fill=PANEL, stroke=LINE, sw=1.4, rx=10))
    f.append(text(44, 274, "2 · вирішити долю збереженого запису", size=12.5,
                  color=MUTED, anchor="start", bold=True))
    rows2 = [
        (290, "no-cache не стоїть\nі current_age < freshness_lifetime", FIELD,
              "ВІДДАТИ зі сховища — мережі немає;\nдописати Age: current_age"),
        (356, "прострочена не більш ніж на\nstale-while-revalidate", AMBER,
              "ВІДДАТИ одразу,\nа валідацію запустити у фоні"),
        (422, "решта випадків", NEG,
              "УМОВНИЙ ЗАПИТ до origin:\nIf-None-Match  ·  If-Modified-Since"),
    ]
    for y, left, col, right in rows2:
        f.append(fitbox(44, y, 390, 56, left, size=12, stroke=col, fill="#ffffff",
                        color=col))
        f.append(arrow(438, y + 28, 470, y + 28, color=GRAY, sw=1.5))
        f.append(fitbox(474, y, 464, 56, right, size=12, stroke=col, fill="#ffffff"))

    f.append(rect(20, 508, 940, 246, fill=PANEL, stroke=LINE, sw=1.4, rx=10))
    f.append(text(44, 538, "3 · що зробити з відповіддю origin на умовний запит",
                  size=12.5, color=MUTED, anchor="start", bold=True))
    rows3 = [
        (554, "304 Not Modified", NEG,
              "вписати заголовки в запис, КРІМ Content-Length;\nвік стартує з нуля — і віддати збережене тіло"),
        (620, "200 OK", FIELD,
              "замінити запис новим тілом і новими заголовками"),
        (686, "5xx або тиша", POS,
              "stale-if-error ще чинний → віддати стару копію;\nінакше прокинути помилку — запис НЕ чіпати"),
    ]
    for y, left, col, right in rows3:
        f.append(fitbox(44, y, 210, 56, left, size=12.5, stroke=col, fill="#ffffff",
                        color=col, bold=True))
        f.append(arrow(258, y + 28, 286, y + 28, color=GRAY, sw=1.5))
        f.append(fitbox(290, y, 648, 56, right, size=12, stroke=col, fill="#ffffff"))

    render(os.path.join(IMG, "proxy-state-machine.svg"), W, H, *f)


# ── Арифметика віку: два різні годинники (вставка proj) ───────────────
# Ідея: apparent_age — стінним годинником, resident_time — монотонним, беремо max.
def fig_age_arithmetic():
    W, H = 940, 452
    f = [text(W / 2, 30, "Звідки береться current_age: дві оцінки, беремо більшу",
              size=16, bold=True)]

    ax0, ax1, ay = 60, 890, 178
    f.append(line(ax0, ay, ax1, ay, color=INK, sw=2))

    above = [
        (90,  "Date: 09:00:00\nвідповідь створив origin"),
        (545, "upstream відправив,\nAge: 240"),
        (855, "now\nresident_time = 60 c"),
    ]
    beneath = [
        (400, "request_time\nми надіслали запит"),
        (665, "response_time\nвідповідь у нас, 09:04:07"),
    ]
    for x, lbl in above:
        f.append(line(x, ay - 8, x, ay + 8, color=INK, sw=2))
        f.append(mtext(x, ay - 34, lbl, size=11.5, color=INK))
    for x, lbl in beneath:
        f.append(line(x, ay - 8, x, ay + 8, color=INK, sw=2))
        f.append(mtext(x, ay + 30, lbl, size=11.5, color=INK))

    f.append(line(400, ay + 76, 665, ay + 76, color=AMBER, sw=1.8))
    f.append(line(400, ay + 70, 400, ay + 82, color=AMBER, sw=1.8))
    f.append(line(665, ay + 70, 665, ay + 82, color=AMBER, sw=1.8))
    f.append(text(532, ay + 100, "response_delay = 5 c", size=11.5, color=AMBER))

    py = 306
    f.append(rect(20, py, W - 40, 128, fill=PANEL, stroke=NEG, sw=1.6, rx=10))
    rows = [
        "apparent_age = 09:04:07 − 09:00:00 = 247 c        (наш годинник спішить на 2 c)",
        "corrected_age_value = Age + response_delay = 240 + 5 = 245 c",
        "corrected_initial_age = max(247, 245) = 247 c     ← беремо БІЛЬШУ оцінку",
        "current_age = 247 + 60 = 307 c                    → при max-age=300 прострочено на 7 c",
    ]
    ly = py + 30
    for ln in rows:
        f.append(text(44, ly, ln, size=12, color=INK, anchor="start"))
        ly += 26

    render(os.path.join(IMG, "age-arithmetic.svg"), W, H, *f)


if __name__ == "__main__":
    fig_three_paths()
    fig_cache_chain()
    fig_freshness_timeline()
    fig_cache_key_vary()
    fig_precondition_order()
    fig_freshness_precedence()
    fig_proxy_state_machine()
    fig_age_arithmetic()
    print("готово:", IMG)
