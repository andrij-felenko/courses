# -*- coding: utf-8 -*-
"""Фігури до кроку «Де живе черга задач» (jobs-placement-variants)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_placement_axis():
    """Вісь розміщення черги: від «нуль машинерії» (памʼять) через базу до окремої
    інфри. Праворуч більше потужності й фіч, але між базою та інфрою ламається
    межа транзакції — головний розрив кроку."""
    W, H = 1320, 560
    frags = []

    x0, x1 = 90, 1230
    axis_y = 300
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=1.8))
    frags.append(text(x0 + 8, axis_y + 34, "менше окремої машинерії", size=12.5,
                      color=MUTED, anchor="start"))
    frags.append(text(x1 - 8, axis_y + 34, "більше окремої машинерії", size=12.5,
                      color=MUTED, anchor="end"))

    # три станції: центр по осі, тік на осі, картка-заголовок вище, нота нижче
    stations = [
        (250, "#eef2fb", NEG, "у памʼяті процесу",
         ["0 інфри · субмілісекунда", "випаровується на рестарті", "не виходить за процес"]),
        (660, "#eafaf0", FIELD, "у твоїй базі даних",
         ["нічого нового не ставиш", "АТОМАРНА з бізнес-записом", "чергу видно як таблицю"]),
        (1070, "#fdecea", POS, "окремий брокер · Redis · SQS",
         ["throughput + повна коробка фіч", "нова залежність під нагляд", "дуалрайт вертається"]),
    ]
    for cx, fill, stroke, title, notes in stations:
        frags.append(circle(cx, axis_y, 6, fill=stroke, stroke=stroke, sw=1))
        b, _, h = textbox(cx, 150, title, size=13.5, fill=fill, stroke=stroke,
                          bold=True, min_w=280)
        frags.append(b)
        frags.append(line(cx, 150 + h / 2, cx, axis_y - 6, color=MUTED, sw=1.2, dash="3,4"))
        frags.append(mtext(cx, axis_y + 78, notes, size=12, color=INK))

    # розрив межі транзакції між станцією 2 і 3
    bx = 865
    frags.append(line(bx, 96, bx, axis_y + 118, color=POS, sw=2, dash="6,6"))
    b, _, _ = textbox(bx, 74, "тут ламається\nмежа транзакції", size=12, fill="#fdecea",
                      stroke=POS, bold=True, min_w=200)
    frags.append(b)

    render(os.path.join(IMG, "placement-axis.svg"), W, H, *frags,
           title="Де живе черга: одна вісь, три субстрати")


def fig_transactional_enqueue():
    """Осердя кроку: одна транзакція (база) проти двох систем (брокер). Ліворуч
    запис факту й постановка задачі неподільні; праворуч розходяться на кожному
    падінні, і лік — знову таблиця-черга (outbox) у транзакції."""
    W, H = 1280, 620
    frags = []

    frags.append(line(W / 2, 60, W / 2, 560, color=MUTED, sw=1, dash="4,6"))
    frags.append(text(330, 84, "Одна система: черга в базі", size=15, bold=True, color=FIELD))
    frags.append(text(955, 84, "Дві системи: брокер осторонь", size=15, bold=True, color=POS))

    # ── ліворуч: одна рамка транзакції охоплює обидва записи ──
    frags.append(rect(120, 120, 420, 210, fill="#f2fbf6", stroke=FIELD, sw=2.4, rx=12))
    frags.append(text(330, 150, "ОДНА ТРАНЗАКЦІЯ", size=13, bold=True, color=FIELD))
    b, _, _ = textbox(330, 200, "записати кліп  (бізнес-факт)", size=12.5,
                      fill="#eef2fb", min_w=330)
    frags.append(b)
    b, _, _ = textbox(330, 268, "поставити задачу  (INSERT у jobs)", size=12.5,
                      fill="#eafaf0", stroke=FIELD, min_w=330)
    frags.append(b)
    b, _, _ = textbox(330, 392, "COMMIT разом  або  ROLLBACK разом", size=13,
                      fill="#eafaf0", stroke=FIELD, bold=True, min_w=380)
    frags.append(b)
    frags.append(mtext(330, 452, ["задачу неможливо ні загубити,",
                                  "ні лишити фактом-сиротою"], size=12.5, color=INK))

    # ── праворуч: дві окремі коробки, спільної рамки нема ──
    b, _, _ = textbox(770, 175, "БАЗА\nзаписати кліп", size=12.5, fill="#eef2fb",
                      stroke=NEG, bold=True, min_w=210)
    frags.append(b)
    b, _, _ = textbox(1130, 175, "БРОКЕР\nпоставити задачу", size=12.5, fill="#fff4e6",
                      stroke=POS, bold=True, min_w=210)
    frags.append(b)
    frags.append(line(875, 175, 1025, 175, color=MUTED, sw=1.4, dash="5,5"))
    frags.append(text(950, 160, "нема спільної транзакції", size=11.5, color=MUTED))

    # два збої
    b, _, _ = textbox(950, 300, "база ✓, enqueue ✗", size=12.5, fill="#fdecea",
                      stroke=POS, bold=True, min_w=260)
    frags.append(b)
    frags.append(text(950, 340, "→ задача загублена", size=12.5, color=POS))
    b, _, _ = textbox(950, 388, "база ✗, enqueue ✓", size=12.5, fill="#fdecea",
                      stroke=POS, bold=True, min_w=260)
    frags.append(b)
    frags.append(text(950, 428, "→ задача-привид", size=12.5, color=POS))

    # лік — outbox
    b, _, _ = textbox(950, 495, "лік — OUTBOX: знову таблиця-черга\nв тій самій транзакції бази",
                      size=12, fill="#eafaf0", stroke=FIELD, min_w=380)
    frags.append(b)

    render(os.path.join(IMG, "transactional-enqueue.svg"), W, H, *frags,
           title="Справжній розріз: одна транзакція проти двох систем")


def fig_placement_matrix():
    """Лінійка трьох варіантів за шістьма ознаками: жоден не бере всі стовпці —
    класична точка компромісу."""
    W, H = 1580, 470
    frags = []

    cols = [
        (150, "варіант"),
        (368, "переживе\nрестарт?"),
        (585, "атомарна\nіз записом?"),
        (802, "між\nінстансами?"),
        (1005, "нова\nінфра?"),
        (1215, "стеля\nпропускної"),
        (1440, "вбудовані\nретраї / DLQ"),
    ]
    for cx, head in cols:
        frags.append(mtext(cx, 88, head.split("\n"), size=12.5, bold=True, color=MUTED, lh=1.25))

    G, R, N = "#eafaf0", "#fdecea", FILL   # добре / ціна / нюанс
    rows = [
        ("у памʼяті\nпроцесу", [
            ("ні", R), ("ні", R), ("ні", R), ("жодної", G),
            ("найвища,\nбез гарантій", N), ("ні — руками", R)]),
        ("у твоїй\nбазі", [
            ("так", G), ("ТАК", G), ("так", G), ("жодної", G),
            ("помірна", N), ("частково", N)]),
        ("окрема\nінфра", [
            ("так —\nвід налаштувань", N), ("ні —\nтреба outbox", R), ("так", G),
            ("ще один\nрушій", R), ("найвища", G), ("так —\nповна коробка", G)]),
    ]
    ys = [175, 285, 395]
    xs = [c[0] for c in cols]
    for (name, cells), y in zip(rows, ys):
        b, _, _ = textbox(xs[0], y, name, size=13, fill="#eef2fb", bold=True, min_w=190)
        frags.append(b)
        for cx, (val, fill) in zip(xs[1:], cells):
            stroke = FIELD if fill == G else (POS if fill == R else LINE)
            b, _, _ = textbox(cx, y, val, size=12, fill=fill, stroke=stroke, min_w=196)
            frags.append(b)

    render(os.path.join(IMG, "placement-matrix.svg"), W, H, *frags,
           title="Три розміщення черги за шістьма ознаками — жодне не бере всі")


def fig_queue_pendulum():
    """Маятник субстрату черги в часі: почалося в базі (delayed_job), хитнулося в
    брокери (Resque, Sidekiq), і з приходом SKIP LOCKED (Postgres 9.5, 2016)
    гойднулося назад у базу (Oban, solid_queue, River). Тонка течія — база ніколи
    й не вмирала (queue_classic, que на advisory locks)."""
    W, H = 1500, 770
    frags = []

    broker_y, db_y = 230, 508
    div_x = 300
    x_lo, x_hi = 312, 1430

    # дві смуги-орієнтири (перервані під підписами, щоб лінія не різала текст)
    frags.append(line(650, broker_y, x_hi, broker_y, color=MUTED, sw=1, dash="2,7"))
    frags.append(line(590, db_y, x_hi, db_y, color=MUTED, sw=1, dash="2,7"))
    b, _, _ = textbox(480, broker_y, "окремий брокер · Redis / RabbitMQ", size=12.5,
                      fill="#fdecea", stroke=POS, bold=True, min_w=330)
    frags.append(b)
    b, _, _ = textbox(445, db_y, "у базі даних (Postgres)", size=12.5,
                      fill="#eafaf0", stroke=FIELD, bold=True, min_w=280)
    frags.append(b)

    # передісторія: cron / at — відкладена робота ще до бібліотек-черг
    frags.append(line(div_x, 120, div_x, 600, color=MUTED, sw=1, dash="3,6"))
    frags.append(circle(165, 380, 6, fill=MUTED, stroke=MUTED))
    frags.append(mtext(165, 322, ["cron · at", "відкладена робота",
                                  "Unix V7 1979", "Vixie 1987"], size=11,
                       color=MUTED, lh=1.35))

    # маятникова лінія: база → брокери → база
    dj, rq, sk = (620, db_y), (735, broker_y), (860, broker_y)
    ob, sq, rv = (1120, db_y), (1245, db_y), (1365, db_y)
    path_pts = [dj, rq, sk, ob, sq, rv]
    for (ax, ay), (bx, by) in zip(path_pts, path_pts[1:]):
        frags.append(line(ax, ay, bx, by, color=INK, sw=3))

    # тонка течія: база не вмирала (advisory locks) — 2011..2016
    frags.append(line(665, db_y - 14, 985, db_y - 14, color=FIELD, sw=1.6, dash="5,5"))
    frags.append(mtext(820, db_y - 56, ["queue_classic (2011) · que (2013):",
                                        "база й не вмирала — advisory locks"],
                       size=10.5, color=FIELD))

    # вузли (broker — підпис вгорі, база — внизу)
    def node(cx, cy, name, year, stroke, up):
        out = circle(cx, cy, 7, fill=BG, stroke=stroke, sw=2.4)
        ny = cy - 46 if up else cy + 34
        out += text(cx, ny, name, size=12.5, bold=True)
        out += text(cx, ny + (-16 if up else 16), year, size=11, color=MUTED)
        return out

    frags.append(node(*dj, "delayed_job", "2008 · Shopify", FIELD, up=False))
    frags.append(node(*rq, "Resque", "2009 · GitHub", POS, up=True))
    frags.append(node(*sk, "Sidekiq", "2012", POS, up=True))
    frags.append(node(*ob, "Oban", "2019 · Elixir", FIELD, up=False))
    frags.append(node(*sq, "solid_queue", "2023 · Rails", FIELD, up=False))
    frags.append(node(*rv, "River", "2023 · Go", FIELD, up=False))

    # осердя-поворот: SKIP LOCKED
    px = 1005
    frags.append(line(px, 192, px, 566, color=FIELD, sw=2, dash="6,5"))
    b, _, _ = textbox(px, 162, "FOR UPDATE SKIP LOCKED\nPostgres 9.5 · січень 2016",
                      size=11.5, fill="#eafaf0", stroke=FIELD, bold=True, min_w=250)
    frags.append(b)

    # чому вгору / чому вниз — теза фігури
    b, _, _ = textbox(700, 92,
                      "▲ вгору (2009–15): пропускна, push-доставка, готова коробка фіч —\n"
                      "а база тоді ще без зручного конкурентного забору",
                      size=12, fill="#fff4e6", stroke=POS, min_w=540)
    frags.append(b)
    b, _, _ = textbox(1085, 700,
                      "▼ назад у базу (2016+): SKIP LOCKED зробив забір чистим,\n"
                      "повернулась атомарна постановка, впала операційна поверхня",
                      size=12, fill="#eafaf0", stroke=FIELD, min_w=600)
    frags.append(b)

    frags.append(arrow(320, 744, 1400, 744, color=MUTED, sw=1.4))
    frags.append(text(1405, 748, "час", size=11.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "queue-pendulum.svg"), W, H, *frags,
           title="Маятник субстрату черги: база → брокери → знову база")


def fig_orphan_vs_outbox():
    """Таймлайн тесту: наївний подвійний запис сиротить кліп у точці падіння, а
    transactional outbox переживає ту саму точку, бо намір закомічено з кліпом.
    (Фігура вставки proj-jobs-three-ways.)"""
    W, H = 1400, 560
    frags = []

    crash_x = 665
    frags.append(line(crash_x, 122, crash_x, 500, color=POS, sw=2, dash="7,7"))
    b, _, _ = textbox(crash_x, 84, "тут падає процес\n(після COMMIT, до enqueue)",
                      size=12, fill="#fdecea", stroke=POS, bold=True, min_w=300)
    frags.append(b)

    laneA_y, laneB_y = 240, 430
    frags.append(text(96, laneA_y - 72, "наївний подвійний запис", size=13.5,
                      bold=True, color=NEG, anchor="start"))
    frags.append(text(96, laneB_y - 72, "транзакційний outbox", size=13.5,
                      bold=True, color=FIELD, anchor="start"))

    def box(cx, cy, s, **kw):
        b, w, h = textbox(cx, cy, s, **kw)
        frags.append(b)
        return cx - w / 2, cx + w / 2

    def connect(xr, xl, y):
        frags.append(arrow(xr + 6, y, xl - 6, y, color=MUTED, sw=1.6))

    # ── доріжка А (наївна) ──
    _, a1r = box(215, laneA_y, "INSERT clip", size=12.5, fill="#eef2fb", min_w=150)
    a2l, a2r = box(430, laneA_y, "COMMIT ✓", size=12.5, fill="#eef2fb", stroke=NEG,
                   bold=True, min_w=150)
    connect(a1r, a2l, laneA_y)
    a3l, a3r = box(840, laneA_y, "enqueue transcode\n— НЕ сталося", size=12,
                   fill="#f4f6f8", stroke=MUTED, min_w=215)
    connect(a2r, a3l, laneA_y)
    a4l, _ = box(1175, laneA_y, "кліп ✓, задача ✗\nОСИРОТІЛИЙ КЛІП", size=12.5,
                 fill="#fdecea", stroke=POS, bold=True, min_w=255)
    connect(a3r, a4l, laneA_y)

    # ── доріжка Б (outbox) ──
    _, b1r = box(258, laneB_y, "INSERT clip + рядок outbox\n(одна транзакція)",
                 size=12, fill="#eafaf0", stroke=FIELD, min_w=295)
    b2l, b2r = box(535, laneB_y, "COMMIT ✓", size=12.5, fill="#eafaf0", stroke=FIELD,
                   bold=True, min_w=150)
    connect(b1r, b2l, laneB_y)
    b3l, b3r = box(855, laneB_y, "relay: 1-ша ✗ → retry\n→ enqueue ✓", size=12,
                   fill="#eafaf0", stroke=FIELD, min_w=245)
    connect(b2r, b3l, laneB_y)
    b4l, _ = box(1185, laneB_y, "0 сиріт\nнамір був у базі", size=12.5,
                 fill="#eafaf0", stroke=FIELD, bold=True, min_w=225)
    connect(b3r, b4l, laneB_y)

    render(os.path.join(IMG, "orphan-vs-outbox.svg"), W, H, *frags,
           title="Та сама точка падіння: наївний запис сиротить, outbox гоїть")


def fig_at_least_once():
    """Дві доставки тієї самої задачі: перша проходить крізь кодек, друга впирається
    в наявний результат. Природний ключ (clip_id, profile) = ефект рівно раз.
    (Фігура вставки proj-jobs-three-ways.)"""
    W, H = 1220, 520
    frags = []

    jb, _, _ = textbox(610, 74, "задача  transcode { clipId: 42 }", size=13,
                       fill="#eef2fb", stroke=NEG, bold=True, min_w=300)
    frags.append(jb)

    L, R = 335, 885
    frags.append(arrow(560, 96, L + 55, 156, color=MUTED, sw=1.7))
    frags.append(arrow(660, 96, R - 55, 156, color=MUTED, sw=1.7))
    frags.append(text(L, 148, "доставка 1", size=12.5, bold=True, color=FIELD))
    frags.append(text(R, 148, "доставка 2 — той самий job", size=12.5, bold=True, color=POS))

    def box(cx, cy, s, **kw):
        b, w, h = textbox(cx, cy, s, **kw)
        frags.append(b)
        return cy - h / 2, cy + h / 2

    def down(x, yb, yt):
        frags.append(arrow(x, yb + 5, x, yt - 5, color=MUTED, sw=1.6))

    y1, y2, y3 = 205, 300, 388
    # ── доставка 1: реально кодує ──
    _, l1b = box(L, y1, "перевір renditions(42)\n→ порожньо", size=12,
                 fill="#f4f6f8", min_w=240)
    l2t, l2b = box(L, y2, "encode() — дорогий кодек", size=12.5, fill="#eafaf0",
                   stroke=FIELD, bold=True, min_w=240)
    down(L, l1b, l2t)
    l3t, l3b = box(L, y3, "INSERT rendition(42,\n'h264-720p')", size=12,
                   fill="#eafaf0", stroke=FIELD, min_w=240)
    down(L, l2b, l3t)

    # ── доставка 2: дубль, кодек не чіпає ──
    _, r1b = box(R, y1, "перевір renditions(42)\n→ вже є", size=12,
                 fill="#f4f6f8", min_w=250)
    r2t, r2b = box(R, y2, "encode ПРОПУЩЕНО", size=12.5, fill="#eef0f2",
                   stroke=MUTED, min_w=250)
    down(R, r1b, r2t)
    r3t, r3b = box(R, y3, "INSERT … ON CONFLICT\nDO NOTHING → 0 рядків", size=12,
                   fill="#eef0f2", stroke=MUTED, min_w=250)
    down(R, r2b, r3t)

    # спільний результат унизу — ОДИН рядок
    tb, tw, _ = textbox(610, 470, "renditions → ОДИН рядок:  (42, 'h264-720p')",
                        size=13, fill="#eafaf0", stroke=FIELD, bold=True, min_w=440)
    frags.append(arrow(L, l3b + 5, 610 - tw / 2 + 45, 458, color=FIELD, sw=1.7))
    frags.append(arrow(R, r3b + 5, 610 + tw / 2 - 45, 458, color=MUTED, sw=1.7))
    frags.append(tb)

    render(os.path.join(IMG, "at-least-once.svg"), W, H, *frags,
           title="Щонайменше раз × ключ ідемпотентності = ефект рівно раз")


if __name__ == "__main__":
    fig_placement_axis()
    fig_transactional_enqueue()
    fig_placement_matrix()
    fig_queue_pendulum()
    fig_orphan_vs_outbox()
    fig_at_least_once()
    print("OK: placement-axis.svg, transactional-enqueue.svg, placement-matrix.svg, "
          "queue-pendulum.svg, orphan-vs-outbox.svg, at-least-once.svg")
