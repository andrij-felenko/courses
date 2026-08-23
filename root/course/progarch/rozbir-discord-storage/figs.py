# -*- coding: utf-8 -*-
"""Фігури для кроку «Розбір: як Discord зберігає трильйони повідомлень»
(guide progarch / time-order-consensus). Вивід — ./img/*.svg.
svgkit імпортуємо, не переписуємо."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

PURPLE = "#8e44ad"
ORANGE = "#d68910"
ORFILL = "#fdf2e0"
GRFILL = "#eafaf0"
BLFILL = "#eaf0fd"
RDFILL = "#fdecea"


def fig_the_key():
    """Ключ несе і час, і місце. Зверху — 64-бітний Snowflake: старші 42 біти є
    показом годинника, тож більший ID новіший (порядок за часом задарма). Знизу —
    канал ріжеться на відра по 10 діб, кожна пара (channel_id, відро) стає окремою
    партицією; усередині повідомлення впорядковані спадним message_id."""
    W, H = 1060, 610
    els = []
    els.append(text(W / 2, 34, "Ключ Discord: message_id дає час, (channel_id, відро) дає місце",
                    size=16, bold=True))

    # ── Верх: біти Snowflake ──
    els.append(text(W / 2, 66, "message_id — це Snowflake (64 біти)", size=13.5, bold=True, color=ORANGE))
    x0, sy, sh = 120, 80, 48
    segs = [(452, "42 біти — мітка часу (мс від епохи 2015)", ORANGE, ORFILL),
            (104, "5\nworker", MUTED, "#eef1f4"),
            (104, "5\nprocess", MUTED, "#eef1f4"),
            (150, "12 — лічильник", NEG, BLFILL)]
    cx = x0
    for w, lab, col, fl in segs:
        els.append(fitbox(cx, sy, w, sh, lab, size=12.5, fill=fl, stroke=col, sw=1.8, color=INK, bold=True))
        cx += w
    els.append(text(x0, sy + sh + 22, "◄ старші біти", size=11.5, color=ORANGE, anchor="start", bold=True))
    els.append(text(cx, sy + sh + 22, "молодші біти ►", size=11.5, color=NEG, anchor="end"))
    els.append(text(W / 2, sy + sh + 48,
                    "старші 42 біти — показ годинника · більший ID ⇒ пізніше створено ⇒ сортування за ID = сортування за часом",
                    size=12.5, italic=True, color=MUTED))

    # роздільник
    els.append(line(60, 224, W - 60, 224, color="#e0e4e9", sw=1.4))

    # ── Низ: відра й партиції ──
    els.append(text(W / 2, 256,
                    "партиційний ключ = (channel_id, відро) — ДЕ живе · кластерний ключ = message_id — ПОРЯДОК",
                    size=13, bold=True, color=FIELD))

    # канал
    els.append(fitbox(70, 350, 150, 62, "канал\nchannel_id", size=13.5, fill=BG, stroke=INK, sw=1.9, bold=True))
    els.append(arrow(222, 381, 300, 372, color=INK, sw=1.9))

    # три партиції-відра
    parts = [(300, "(channel_id, 48)   ·   10 діб", LINE, FILL, False),
             (360, "(channel_id, 49)   ·   10 діб", LINE, FILL, False),
             (420, "(channel_id, 50)   ·   10 діб   ← зараз", FIELD, GRFILL, True)]
    for py, lab, col, fl, hot in parts:
        els.append(fitbox(300, py, 268, 48, lab, size=13, fill=fl, stroke=col, sw=2.2 if hot else 1.6,
                          color=INK, bold=hot))
    els.append(text(300, 300 - 12, "партиції каналу (по 10 діб):", size=12, color=MUTED, anchor="start"))

    # опукла поточна партиція → рядки повідомлень
    els.append(arrow(570, 444, 636, 420, color=FIELD, sw=1.9))
    els.append(rect(636, 300, 356, 190, fill="#fbfdfb", stroke=FIELD, sw=1.6, rx=10))
    els.append(text(636 + 178, 324, "усередині партиції — за message_id спадно", size=12.5, bold=True, color=FIELD))
    rows = [("новіше", "181 193 950 000 000 000"),
            ("", "181 193 940 000 000 000"),
            ("старіше", "181 193 932 800 000 000")]
    for i, (tag, mid) in enumerate(rows):
        ry = 342 + i * 44
        els.append(rect(656, ry, 316, 34, fill=BG, stroke="#cdd4da", sw=1.3, rx=6))
        els.append(text(668, ry + 22, "message_id  " + mid, size=12, color=INK, anchor="start"))
        if tag:
            els.append(text(980, ry + 22, tag, size=11, color=MUTED, anchor="end", italic=True))
    els.append(arrow(646, 430, 646, 350, color=MUTED, sw=1.5))
    els.append(text(626, 392, "новіші згори", size=10.5, color=MUTED, anchor="end"))

    els.append(text(W / 2, H - 14,
                    "відро обмежує ріст партиції згори — без нього гарячий канал ріс би без краю роками",
                    size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "the-key.svg"), W, H, *els)


def fig_token_ring():
    """Консистентне хешування кладе партицію на кільце токенів: партиційний ключ
    хешується в точку, нею володіє вузол плюс дві наступні репліки (фактор 3),
    читання/запис — кворумом. Пастка: ключі розкладено рівномірно, але коли один
    канал вибухає, усе його навантаження б'є в ті самі три вузли (гаряча партиція).
    Розбіжність реплік лікують деревами Меркла."""
    W, H = 1020, 580
    els = []
    els.append(text(W / 2, 34, "Кільце токенів: рівні КЛЮЧІ, нерівне НАВАНТАЖЕННЯ", size=16, bold=True))

    cx, cy, R, r = 316, 322, 156, 27
    N = 8
    # кільце
    els.append(circle(cx, cy, R, fill="none", stroke="#c9d0d8", sw=2.4))

    # позиції вузлів
    def npos(i):
        a = math.radians(-90 + 360 / N * i)
        return cx + R * math.cos(a), cy + R * math.sin(a)

    replicas = {1, 2, 3}   # три репліки, що тримають гарячу партицію
    for i in range(N):
        x, y = npos(i)
        hot = i in replicas
        els.append(circle(x, y, r, fill=GRFILL if hot else BG, stroke=FIELD if hot else LINE,
                          sw=3.0 if hot else 1.6))
        els.append(text(x, y + 5, "N%d" % (i + 1), size=12.5, color=INK, bold=hot))

    # партиційний ключ → токен на кільці (між N1 і зоною реплік — беремо точку біля N1)
    tx, ty = npos(0.6)   # точка-токен трохи за N1
    els.append(fitbox(60, 84, 250, 54, "хеш((channel_id, 50))\n→ токен на кільці", size=13,
                      fill=ORFILL, stroke=ORANGE, sw=1.8, bold=True))
    els.append(arrow(185, 138, tx - 6, ty - 4, color=ORANGE, sw=2.0))
    els.append(circle(tx, ty, 7, fill=ORANGE, stroke=ORANGE, sw=1))

    # дужка «3 репліки, кворум»
    els.append(fitbox(300, 470, 300, 54, "N2·N3·N4 — 3 репліки\nчитання/запис кворумом (2 з 3)",
                      size=12.5, fill=GRFILL, stroke=FIELD, sw=1.7, bold=True))
    for i in replicas:
        x, y = npos(i)
        els.append(line(x, y + r, 450, 468, color=FIELD, sw=1.1, dash="4,3"))

    # гаряче навантаження — пучок червоних стрілок у ті самі репліки
    els.append(fitbox(716, 150, 260, 52, "тисячі читань\nодного вірусного каналу", size=12.5,
                      fill=RDFILL, stroke=POS, sw=1.8, bold=True))
    for i in replicas:
        x, y = npos(i)
        els.append(arrow(720, 176 + (i - 2) * 6, x + r - 2, y, color=POS, sw=1.7))
    els.append(text(632, 298, "усе навантаження → ті самі 3 вузли", size=12.5, color=POS, bold=True, anchor="middle"))
    els.append(text(632, 318, "з двохсот у кільці", size=12, color=POS, anchor="middle"))

    # нота Меркла
    els.append(fitbox(700, 372, 288, 96,
                      "коли репліка відстала —\nдоганяють деревами Меркла:\nзвіряють хеш-корені, шлють\nлише різницю, а не всю партицію",
                      size=12.5, fill=BLFILL, stroke=NEG, sw=1.6))

    els.append(text(W / 2, H - 14,
                    "консистентне хешування ділить дані рівно — але гарячий ключ розжарює саме свою трійку реплік",
                    size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "token-ring.svg"), W, H, *els)


def fig_coalescing():
    """Гарячу партицію гасять не залізом, а координацією перед сховищем. Ліворуч —
    без коалесингу: тисяча однакових читань = тисяча запитів у ті самі три гарячі
    вузли. Праворуч — з коалесингом: консистентний хеш за channel_id зводить увесь
    трафік каналу в один сервіс даних, той робить ОДИН запит, а результат роздає всім."""
    W, H = 1040, 520
    els = []
    els.append(text(W / 2, 32, "Гарячу партицію гасить координація перед сховищем, а не більше машин",
                    size=15.5, bold=True))

    users = [-3, -1, 1, 3]

    # ── Панель А: без коалесингу ──
    ax, aw = 28, 480
    els.append(rect(ax, 56, aw, 424, fill="#fbeceb", stroke="#e8b7b2", sw=1.4, rx=10))
    els.append(text(ax + aw / 2, 82, "Без коалесингу", size=14, bold=True, color=POS))
    acx = ax + aw / 2
    for k, u in enumerate(users):
        ux = acx + u * 74
        els.append(circle(ux, 128, 17, fill=BG, stroke=MUTED, sw=1.5))
        els.append(text(ux, 133, "%d" % (k + 1), size=12, color=INK))
    els.append(fitbox(acx - 150, 372, 300, 60, "3 гарячі вузли сховища\n(та сама партиція)",
                      size=13, fill=RDFILL, stroke=POS, sw=2.0, bold=True))
    for u in users:
        ux = acx + u * 74
        els.append(arrow(ux, 146, acx + u * 20, 370, color=POS, sw=1.6))
    els.append(text(acx, 240, "1000 однакових читань", size=13, bold=True, color=POS))
    els.append(text(acx, 260, "= 1000 запитів у ту саму трійку", size=12.5, color=POS))

    # ── Панель Б: з коалесингом ──
    bx, bw = 532, 480
    els.append(rect(bx, 56, bw, 424, fill="#eafaf0", stroke="#b6e2c6", sw=1.4, rx=10))
    els.append(text(bx + bw / 2, 82, "З коалесингом", size=14, bold=True, color=FIELD))
    bcx = bx + bw / 2
    for k, u in enumerate(users):
        ux = bcx + u * 74
        els.append(circle(ux, 128, 17, fill=BG, stroke=MUTED, sw=1.5))
        els.append(text(ux, 133, "%d" % (k + 1), size=12, color=INK))
    # сервіс даних
    els.append(fitbox(bcx - 165, 214, 330, 56, "сервіс даних  ·  маршрут за channel_id\n(консистентний хеш → той самий екземпляр)",
                      size=12, fill="#fff7e6", stroke=ORANGE, sw=2.0, bold=True))
    for u in users:
        ux = bcx + u * 74
        els.append(arrow(ux, 146, bcx + u * 10, 212, color=FIELD, sw=1.6))
    # один запит у базу
    els.append(fitbox(bcx - 150, 392, 300, 56, "3 вузли сховища\n(1 запит замість тисячі)",
                      size=13, fill=GRFILL, stroke=FIELD, sw=2.0, bold=True))
    els.append(arrow(bcx, 272, bcx, 390, color=FIELD, sw=2.4))
    els.append(text(bcx + 96, 336, "1 запит", size=12.5, color=FIELD, bold=True, anchor="start"))
    els.append(line(bcx - 20, 390, bcx - 20, 272, color=MUTED, sw=1.4, dash="5,3"))
    els.append(text(bcx - 150, 336, "решта підписуються\nна той самий результат", size=11.5, color=MUTED, anchor="middle"))

    els.append(text(W / 2, H - 14,
                    "той самий консистентний хеш працює двічі: розкладає дані по вузлах сховища — і запити по вузлах сервісу",
                    size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "coalescing.svg"), W, H, *els)


def fig_storage_timeline():
    """Хронологія сховища Discord: три двигуни (MongoDB → Cassandra → ScyllaDB) за
    2015–2023, з датами, людьми й двома первинними статтями. Знизу — незмінне крізь
    усі три двигуни рішення про розміщення (ключ + Snowflake-порядок)."""
    MONGO, MFILL = "#5b6b7a", "#eef1f4"
    CASS, CFILL = ORANGE, ORFILL
    SCY, SFILL = FIELD, GRFILL

    W, H = 1260, 610
    els = []
    els.append(text(W / 2, 36, "Сховище Discord: три двигуни, одне незмінне рішення (2015 → 2023)",
                    size=17, bold=True))

    y_ax = 320                 # вісь часу з маркерами
    st, sb = 332, 362          # смуга-стрічка ер (двигунів) — ПІД віссю, щоб не чіпати маркери
    ex = [100, 250, 399, 549, 698, 848, 997, 1147]

    # вісь часу
    els.append(line(70, y_ax, 1180, y_ax, color="#c9d0d8", sw=2.0))

    # ── стрічка ер (двигунів) під віссю ──
    bands = [(70, 325, "MongoDB", MONGO, MFILL),
             (325, 997, "Cassandra", CASS, CFILL),
             (997, 1180, "ScyllaDB", SCY, SFILL)]
    for x0, x1, name, col, fl in bands:
        els.append(rect(x0, st, x1 - x0, sb - st, fill=fl, stroke=col, sw=2.0, rx=4))
        els.append(text((x0 + x1) / 2, (st + sb) / 2 + 5, name, size=14, bold=True, color=col))

    # ── події: (індекс, ера-колір, ера-заливка, дата, [рядки опису]) ──
    events = [
        (0, MONGO, MFILL, "2015",          ["старт: MongoDB,", "один реплікасет"]),
        (1, MONGO, MFILL, "листопад 2015", ["стіна на 100 млн —", "індекс не влазить у RAM"]),
        (2, CASS, CFILL, "2016",           ["перехід на Cassandra:", "єдина, що підходила"]),
        (3, CASS, CFILL, "13 січня 2017",  ["стаття «Billions»,", "Вишневський · 12 вузлів"]),
        (4, CASS, CFILL, "близько 2020",   ["ScyllaDB — усі бази,", "окрім повідомлень"]),
        (5, CASS, CFILL, "початок 2022",   ["177 вузлів, трильйони;", "GC-паузи, гарячі партиції"]),
        (6, SCY, SFILL, "травень 2022",    ["повідомлення → ScyllaDB", "9 днів · 177→72 вузли"]),
        (7, SCY, SFILL, "6 березня 2023",  ["стаття «Trillions»,", "Бо Інґрам"]),
    ]
    BW = 196
    for i, col, fl, date, desc in events:
        x = ex[i]
        above = (i % 2 == 0)
        top = 112 if above else 452
        # рамка події
        els.append(rect(x - BW / 2, top, BW, 72, fill=fl, stroke=col, sw=1.9, rx=7))
        els.append(text(x, top + 22, date, size=13, bold=True, color=col))
        for k, ln in enumerate(desc):
            els.append(text(x, top + 42 + k * 17, ln, size=11.5, color=INK))
        # коннектор у порожньому коридорі (не перетинає текст)
        if above:
            els.append(line(x, top + 72, x, y_ax - 7, color=MUTED, sw=1.3))
        else:
            els.append(line(x, sb, x, top, color=MUTED, sw=1.3))
        # маркер на осі (над стрічкою ер)
        els.append(circle(x, y_ax, 7, fill=col, stroke=BG, sw=2.0))

    # ── низ: незмінне рішення ──
    els.append(rect(70, 556, 1110, 44, fill=FILL, stroke=INK, sw=1.6, rx=8))
    els.append(text(625, 573, "Незмінне крізь усі три двигуни:", size=13, bold=True, color=INK))
    els.append(text(625, 591,
                    "ключ (channel_id, відро) і порядок за Snowflake — рішення про РОЗМІЩЕННЯ пережило обидві заміни сховища",
                    size=12.5, color=FIELD))
    render(os.path.join(IMG, "storage-timeline.svg"), W, H, *els)


def fig_migration_feat():
    """Переливання трильйонів повідомлень: власний rust-мігратор проти стандартного
    інструмента. Дві смуги тривалості (≈3 місяці проти 9 днів) + ключові числа."""
    W, H = 1060, 490
    els = []
    els.append(text(W / 2, 34, "Переливання трильйонів: власний rust-мігратор — дні, не місяці",
                    size=16.5, bold=True))

    bx = 250                       # старт смуг
    els.append(line(bx, 74, bx, 236, color="#c9d0d8", sw=1.6))
    SCALE = 7.0                    # 1 доба = 7 px

    # смуга А: стандартний інструмент ~90 діб
    wa = int(90 * SCALE)
    els.append(rect(bx, 92, wa, 46, fill=RDFILL, stroke=POS, sw=2.0, rx=6))
    els.append(mtext(60, 108, ["стандартний", "інструмент"], size=12.5, color=MUTED, anchor="start"))
    els.append(text(bx + wa / 2, 121, "≈ 3 місяці (~90 діб) — лише ОЦІНКА", size=13, bold=True, color=POS))

    # смуга Б: rust-мігратор 9 діб
    wb = int(9 * SCALE)
    els.append(rect(bx, 176, wb, 46, fill=GRFILL, stroke=FIELD, sw=2.0, rx=6))
    els.append(mtext(60, 192, ["власний", "rust-мігратор"], size=12.5, color=MUTED, anchor="start"))
    els.append(text(bx + wb + 16, 205, "9 днів — фактично", size=13, bold=True, color=FIELD, anchor="start"))
    els.append(text(bx + wb + 16, 158, "×10 швидше", size=12.5, bold=True, color=FIELD, anchor="start"))

    # ── плитки-числа 2×2 ──
    def tile(x, y, big, small, col, fl):
        out = rect(x, y, 470, 76, fill=fl, stroke=col, sw=1.7, rx=8)
        out += text(x + 235, y + 33, big, size=17, bold=True, color=col)
        out += text(x + 235, y + 57, small, size=12, color=MUTED)
        return out

    els.append(tile(55, 272, "3.2 млн / с", "пікова швидкість переливу", NEG, BLFILL))
    els.append(tile(535, 272, "подвійний запис", "у стару й нову базу — для звірки", ORANGE, ORFILL))
    els.append(tile(55, 360, "177 → 72", "вузли після переходу", FIELD, GRFILL))
    els.append(tile(535, 360, "40–125 → 15 мс", "p99 читання історії", POS, RDFILL))

    els.append(text(W / 2, 466,
                    "rust-каркас сервісів даних розширили в мігратор «за пообіддя» — і три оцінені місяці стиснулися в дев'ять днів",
                    size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "migration-feat.svg"), W, H, *els)


def fig_bucket_scan():
    """Спадний скан відер для «останніх N»: від відра курсора before назад у часі,
    відро за відром; порожні пропускаємо (кеш), спиняємось, коли набрали N або
    дійшли до відра створення каналу (channel_id — теж Snowflake, тож він і є дно)."""
    W, H = 1200, 440
    els = []
    els.append(text(W / 2, 30,
                    "Спадний скан відер: назад у часі, поки не набрано N або не досягнуто дна",
                    size=16.5, bold=True))

    # ── легенда ──
    leg = [(250, "зібрано", GRFILL, FIELD),
           (430, "порожнє → пропуск (кеш)", "#eef1f4", MUTED),
           (740, "не скановано (стоп раніше)", BG, "#cdd4da")]
    for lx, lab, fl, st in leg:
        els.append(rect(lx, 52, 18, 18, fill=fl, stroke=st, sw=1.6, rx=3))
        els.append(text(lx + 26, 66, lab, size=12, color=MUTED, anchor="start"))

    # ── стрілка «назад у часі» (над відрами, у порожньому коридорі) ──
    els.append(text(W / 2, 132, "скан назад у часі — новіші відра першими",
                    size=12.5, italic=True, color=MUTED))
    els.append(arrow(1114, 150, 246, 150, color=INK, sw=2.0))

    # ── дно: стіна створення каналу ──
    els.append(text(233, 186, "дно", size=12.5, bold=True, color=POS))
    els.append(rect(224, 196, 18, 118, fill="#fdecea", stroke=POS, sw=2.0, rx=3))
    els.append(text(233, 330, "channel_id", size=10.5, color=POS))

    # ── відра (ліворуч старіші, праворуч новіші) ──
    cells = [
        (250, "48", ["не", "скановано"], BG, "#cdd4da", MUTED, False),
        (408, "49", ["не", "скановано"], BG, "#cdd4da", MUTED, False),
        (566, "50", ["приклад тут", "+35 → 50 = N", "СТОП"], GRFILL, FIELD, INK, True),
        (724, "51", ["порожнє", "пропущено"], "#eef1f4", MUTED, MUTED, False),
        (882, "52", ["12 повідомл.", "зібрано"], GRFILL, FIELD, INK, False),
        (1040, "53", ["3 повідомл.", "старт (before)"], ORFILL, ORANGE, INK, True),
    ]
    for cx, num, lines, fl, st, tc, strong in cells:
        els.append(text(cx + 74, 186, "відро " + num, size=12.5, bold=True,
                        color=st if strong else MUTED))
        els.append(fitbox(cx, 196, 148, 118, "\n".join(lines), size=13,
                          fill=fl, stroke=st, sw=2.6 if strong else 1.6, color=tc, bold=strong))

    # ── підсумок і два запобіжники ──
    els.append(text(W / 2, 348,
                    "набрано:  3 (відро 53)  +  12 (52)  +  пропуск (51)  +  35 (50)  =  50 = N",
                    size=12.5, bold=True, color=FIELD))
    els.append(text(W / 2, 376,
                    "Хода: від відра курсора «before» ліворуч; порожнє відро 51 пропущене з кешу; "
                    "на відрі 50 набрано N — і скан спинився, не дійшовши до дна.",
                    size=12.5, italic=True, color=INK))
    els.append(text(W / 2, 402,
                    "Два запобіжники від нескінченного скану: дно = відро створення каналу "
                    "(channel_id теж Snowflake) і пам'ять про порожні відра.",
                    size=12.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "bucket-scan.svg"), W, H, *els)


if __name__ == "__main__":
    fig_the_key()
    fig_token_ring()
    fig_coalescing()
    fig_storage_timeline()
    fig_migration_feat()
    fig_bucket_scan()
    print("OK: figures written to", IMG)
