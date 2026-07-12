# -*- coding: utf-8 -*-
"""Фігури до кроку «Стилі інтеграції як рішення»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

RED_FILL   = "#fdecea"
GREEN_FILL = "#eafaf0"
BLUE_FILL  = "#eef2fb"


def fig_four_styles():
    """Одна межа A↔B, чотири стилі-труби; у кожного — свій профіль зчеплення."""
    W, H = 1220, 640
    frags = []

    ax, bx = 330, 610          # центри коробок A і B
    elemx = 470                # центр серединного елемента (файл / БД / брокер)
    prof_x = 700               # старт профілю зчеплення
    rows = [
        ("file",   "Передавання\nфайлів", FILL,
         ["розчеплені в часі · зчеплені форматом", "несвіже (пакет)"]),
        ("db",     "Спільна\nбаза", RED_FILL,
         ["зчеплені СХЕМОЮ — найтісніше", "миттєво, але приватного стану нема"]),
        ("rpc",    "RPC", FILL,
         ["зчеплені в часі · поведінка й відповідь ЗАРАЗ", "глибокий ланцюг крихкий"]),
        ("msg",    "Повідом-\nлення", GREEN_FILL,
         ["розчеплені в часі · віяло на багатьох", "кінцева узгодженість"]),
    ]
    cys = [100, 250, 400, 550]

    for (kind, name, nfill, prof), cy in zip(rows, cys):
        # назва стилю
        b, _, _ = textbox(150, cy, name, size=13, fill=nfill, bold=True, min_w=150)
        frags.append(b)
        # A та B
        b, _, _ = textbox(ax, cy, "A", size=14, bold=True, min_w=54); frags.append(b)
        b, _, _ = textbox(bx, cy, "B", size=14, bold=True, min_w=54); frags.append(b)

        if kind == "file":
            b, _, _ = textbox(elemx, cy, "файл", size=12, min_w=70); frags.append(b)
            frags.append(arrow(ax + 30, cy, elemx - 40, cy, color=LINE))
            frags.append(arrow(elemx + 40, cy, bx - 30, cy, color=LINE))
            frags.append(text((elemx + 40 + bx - 30) / 2, cy + 18, "пізніше",
                              size=10.5, color=MUTED))
        elif kind == "db":
            b, _, _ = textbox(elemx, cy, "спільна\nБД", size=12, fill=RED_FILL,
                              stroke=POS, min_w=78); frags.append(b)
            frags.append(arrow(ax + 30, cy, elemx - 44, cy, color=POS))   # обидві
            frags.append(arrow(bx - 30, cy, elemx + 44, cy, color=POS))   # У базу
        elif kind == "rpc":
            frags.append(arrow(ax + 30, cy - 8, bx - 30, cy - 8, color=LINE))  # запит →
            frags.append(arrow(bx - 30, cy + 8, ax + 30, cy + 8, color=MUTED)) # ← відповідь
            frags.append(text((ax + bx) / 2, cy - 16, "виклик →", size=10.5, color=MUTED))
            frags.append(text((ax + bx) / 2, cy + 26, "← відповідь", size=10.5, color=MUTED))
        else:  # msg
            b, _, _ = textbox(elemx, cy, "брокер", size=12, fill=GREEN_FILL,
                              stroke=FIELD, min_w=78); frags.append(b)
            frags.append(arrow(ax + 30, cy, elemx - 44, cy, color=FIELD))
            frags.append(arrow(elemx + 44, cy, bx - 30, cy, color=FIELD))

        # профіль зчеплення
        frags.append(mtext(prof_x, cy - 6, prof, size=12.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "four-styles.svg"), W, H, *frags,
           title="Чотири стилі інтеграції — чотири різні зчеплення на одній межі")


def fig_shared_db_trap():
    """Ліворуч спільна база = розподілений моноліт; праворуч власні дані + контракт."""
    W, H = 1240, 560
    frags = []

    # роздільник
    frags.append(line(620, 60, 620, 520, color=MUTED, sw=1.4, dash="5,6"))

    # ── ЛІВА панель: розподілений моноліт ──
    frags.append(text(320, 74, "Розподілений моноліт", size=15, color=POS, bold=True))
    svc = [("Пристрої", 150), ("Білінг", 320), ("Автоматизації", 500)]
    for name, x in svc:
        b, _, _ = textbox(x, 132, name, size=12.5, fill=RED_FILL, stroke=POS, min_w=120)
        frags.append(b)
    b, _, _ = textbox(320, 300, "спільна база — одна схема на всіх",
                      size=13, fill=RED_FILL, stroke=POS, bold=True, min_w=380)
    frags.append(b)
    for _, x in svc:
        frags.append(arrow(x, 156, 320 + (x - 320) * 0.25, 274, color=POS))
    frags.append(mtext(320, 372,
                       ["зміна схеми ламає всіх",
                        "ніхто не деплоїться сам",
                        "зчеплення моноліта + біль мережі"],
                       size=12.5, color=POS))

    # ── ПРАВА панель: власні дані + контракт ──
    frags.append(text(900, 74, "Власні дані + контракт", size=15, color=FIELD, bold=True))
    svc2 = [("Пристрої", 730), ("Білінг", 900), ("Автоматизації", 1080)]
    # контрактні стрілки НАД коробками
    frags.append(line(730, 96, 1080, 96, color=NEG, sw=1.5, dash="4,5"))
    frags.append('<path d="M740 91 L730 96 L740 101" fill="none" stroke="%s" stroke-width="1.5"/>' % NEG)
    frags.append('<path d="M1070 91 L1080 96 L1070 101" fill="none" stroke="%s" stroke-width="1.5"/>' % NEG)
    frags.append(text(905, 88, "контракт: API / подія", size=12, color=NEG, bold=True))
    for name, x in svc2:
        b, _, _ = textbox(x, 140, name, size=12.5, fill=GREEN_FILL, stroke=FIELD, min_w=120)
        frags.append(b)
        b2, _, _ = textbox(x, 224, "своя БД", size=11.5, fill=FILL, min_w=88)
        frags.append(b2)
        frags.append(arrow(x, 164, x, 206, color=FIELD, sw=1.5))
    frags.append(mtext(900, 320,
                       ["власник вільно міняє свою схему",
                        "кожен деплоїться нарізно",
                        "спираються лише на обіцяну форму"],
                       size=12.5, color=FIELD))

    render(os.path.join(IMG, "shared-db-trap.svg"), W, H, *frags,
           title="Спільна база повертає найтісніше зчеплення — власні дані з контрактом його рвуть")


def fig_integration_decision():
    """Дерево вибору стилю; спільна база поверх межі власності — перекреслена окремо."""
    W, H = 1240, 700
    frags = []

    qx = 430            # спина питань
    ox = 880            # виходи
    green = GREEN_FILL

    def q(cy, s):
        b, _, _ = textbox(qx, cy, s, size=12.5, fill=BLUE_FILL, stroke=NEG, min_w=430)
        frags.append(b)

    def outcome(cy, s, fill=FILL, stroke=LINE):
        b, _, _ = textbox(ox, cy, s, size=12.5, fill=fill, stroke=stroke, bold=True, min_w=360)
        frags.append(b)

    # Q1
    q(92, "Обидві частини в одному процесі?")
    frags.append(arrow(qx + 216, 92, ox - 182, 92, color=FIELD))
    frags.append(text(qx + 300, 78, "так", size=12, color=FIELD, bold=True))
    outcome(92, "виклик функції (нульовий стиль):\nбез мережі, без стилю", fill=green, stroke=FIELD)
    frags.append(arrow(qx, 118, qx, 214, color=LINE))
    frags.append(text(qx + 22, 168, "ні", size=12, color=MUTED, bold=True))

    # Q2
    q(238, "Потрібна ПОВЕДІНКА\nі відповідь ЗАРАЗ?")
    frags.append(arrow(qx + 216, 238, ox - 182, 238, color=FIELD))
    frags.append(text(qx + 300, 224, "так", size=12, color=FIELD, bold=True))
    outcome(238, "RPC — запит-відповідь:\nповедінка й відповідь тепер")
    frags.append(arrow(qx, 268, qx, 372, color=LINE))
    frags.append(text(qx + 78, 322, "ні, лише дані", size=12, color=MUTED, bold=True))

    # Q3
    q(400, "Потрібна свіжість\nблизько до реального часу?")
    frags.append(arrow(qx + 216, 388, ox - 182, 360, color=FIELD))
    frags.append(text(qx + 300, 356, "так", size=12, color=FIELD, bold=True))
    outcome(360, "Повідомлення — черга / тема / журнал:\nвіяло, переживає падіння")
    frags.append(arrow(qx + 216, 412, ox - 182, 468, color=LINE))
    frags.append(text(qx + 300, 452, "ні, пакет ОК", size=12, color=MUTED, bold=True))
    outcome(468, "Передавання файлів — нічний експорт:\nдешево, між організаціями")

    # заборонена спільна база: знак-заборона ЛІВОРУЧ від рамки (лінія — лише в колі, не по тексту)
    bx, by, bw, bh = 300, 566, 470, 84
    frags.append(rect(bx, by, bw, bh, fill=RED_FILL, stroke=POS, sw=1.6))
    frags.append(mtext(bx + bw / 2, by + 34,
                       ["Спільна база поверх межі власності",
                        "→ розподілений моноліт"], size=12.5, color=POS, bold=True))
    badge_cx, badge_cy, br = bx - 46, by + bh / 2, 24
    frags.append(circle(badge_cx, badge_cy, br, fill=BG, stroke=POS, sw=3))
    frags.append(line(badge_cx - br * 0.66, badge_cy - br * 0.66,
                      badge_cx + br * 0.66, badge_cy + br * 0.66, color=POS, sw=3))
    frags.append(text(bx + bw + 82, by + bh / 2 + 5, "майже ніколи", size=13, color=POS, bold=True))

    render(os.path.join(IMG, "integration-decision.svg"), W, H, *frags,
           title="Вибір стилю інтеграції на одній межі — і пастка, що стоїть окремо")


def fig_styles_lineage():
    """Родовід чотирьох стилів у часі: практика старша за імена, після 2003 — лише новий одяг."""
    W, H = 1340, 700
    frags = []

    # ── межа «до / після імен»: 2003, коли EIP дала четвірці спільні назви ──
    divx = 700
    b, _, bh = textbox(divx, 70, "2003 · Гопе й Вулф називають четвірку (EIP)",
                       size=13, fill=BLUE_FILL, stroke=NEG, bold=True, min_w=380)
    frags.append(b)
    frags.append(line(divx, 70 + bh / 2 + 4, divx, 662, color=NEG, sw=1.6, dash="6,7"))

    # підказки «до» / «після» обабіч межі
    frags.append(text(410, 120, "ДО імен — та сама практика, різні продавці",
                      size=12, color=MUTED, italic=True))
    frags.append(text(1000, 120, "ПІСЛЯ — четвірка з іменами, далі лише новий крій",
                      size=12, color=MUTED, italic=True))

    # ── чотири доріжки-стилі, кожна тече зліва направо крізь час ──
    lanes = [
        # (назва стилю, заливка, [ (cx, текст, рік) ... ] )
        ("Передавання\nфайлів", FILL, [
            (390, "нічні дампи,\nпакетний обмін", "1970-80-ті"),
            (1160, "CDC · Debezium —\nпотік змін замість пачки", "2016+"),
        ]),
        ("Спільна\nбаза", RED_FILL, [
            (430, "дефолт EAI:\nдвоє в одну БД", "1990-ті"),
            (910, "Фаулер: IntegrationDatabase —\nназваний антипатерн", "2004"),
            (1200, "той самий міст —\nрозподілений моноліт", "нині"),
        ]),
        ("RPC", FILL, [
            (400, "Sun RPC · CORBA", "1980-90-ті"),
            (1140, "REST · gRPC · GraphQL", "2000-2010-ті"),
        ]),
        ("Повідом-\nлення", GREEN_FILL, [
            (370, "TIB — шина на біржі ·\nMQSeries · MOM-брокери", "1987-1993"),
            (1150, "Apache Kafka —\nжурнал-лог", "2011"),
        ]),
    ]
    lane_y = [200, 350, 490, 615]

    for (name, nfill, boxes), cy in zip(lanes, lane_y):
        # спершу — геометрія коробок-«одягу» (щоб провести вісь ПОВЗ них, а не крізь напис)
        box_specs = []
        for (bx, label, yr) in boxes:
            b, w2, h2 = textbox(bx, cy, label, size=11.5, fill=nfill, min_w=120)
            box_specs.append((bx, yr, b, w2, h2))

        # часова вісь доріжки — сегментами між/довкола коробок, стрілка лише на останньому відрізку
        gap = 10
        edges = [250]
        for (bx, _, _, w2, _) in box_specs:
            edges += [bx - w2 / 2 - gap, bx + w2 / 2 + gap]
        edges.append(1300)
        last_i = len(edges) - 2
        for i in range(0, len(edges) - 1, 2):
            x1, x2 = edges[i], edges[i + 1]
            if x2 - x1 > 4:
                if i == last_i:
                    frags.append(arrow(x1, cy, x2, cy, color=MUTED, sw=1.4))
                else:
                    frags.append(line(x1, cy, x2, cy, color=MUTED, sw=1.4))

        # мітка стилю ліворуч
        b, _, _ = textbox(140, cy, name, size=12.5, fill=nfill, bold=True, min_w=118)
        frags.append(b)
        # «одяг» стилю в різні епохи
        for (bx, yr, b, w2, h2) in box_specs:
            frags.append(b)
            frags.append(text(bx, cy + h2 / 2 + 15, yr, size=10.5, color=MUTED))

    render(os.path.join(IMG, "styles-lineage.svg"), W, H, *frags,
           title="Родовід чотирьох стилів: старші за мікросервіси, лише мінять одяг")


def fig_rename_hit():
    """Одна зміна власника (active→status) — три різні наслідки на трьох стилях."""
    W, H = 1320, 748
    frags = []
    wall_x = 700

    # межа власності — на всю висоту
    frags.append(line(wall_x, 78, wall_x, H - 24, color=MUTED, sw=1.4, dash="5,7"))
    frags.append(text(wall_x, 66, "межа власності", size=12.5, color=MUTED, bold=True))
    frags.append(text(1075, 66, "власник міняє свою схему: active → status",
                      size=13, color=POS, bold=True))

    def dev_table(cx, cy):
        """Таблиця власника з «вибухом» зміни схеми."""
        b, _, _ = textbox(cx, cy, "devices\nactive → status", size=12,
                          fill=RED_FILL, stroke=POS, sw=2, min_w=190, bold=True)
        frags.append(b)
        for dx in (-70, 0, 70):
            frags.append(line(cx + dx, cy - 34, cx + dx * 1.25, cy - 52, color=POS, sw=2))

    def billing(cy):
        b, _, _ = textbox(150, cy, "Білінг", size=13, min_w=120, bold=True)
        frags.append(b)

    # ── Доріжка 1: спільна таблиця ──
    cy = 160
    billing(cy)
    dev_table(1130, cy)
    frags.append(arrow(216, cy, 980, cy, color=LINE))          # простромлює стіну в таблицю
    frags.append(line(992, cy - 10, 1012, cy + 10, color=POS, sw=2.8))   # тріщина ✕
    frags.append(line(1012, cy - 10, 992, cy + 10, color=POS, sw=2.8))
    frags.append(line(1016, cy, 1040, cy, color=MUTED, sw=1.2, dash="3,4"))
    frags.append(text(150, cy - 44, "спільна таблиця", size=12.5, color=POS,
                      bold=True, anchor="start"))
    frags.append(mtext(555, cy + 52,
                       ["стрілка простромила стіну власності просто в чужу схему —",
                        "тріщина: column \"active\" does not exist (або тихо не той набір)"],
                       size=12, color=POS))

    # ── Доріжка 2: RPC ──
    cy = 400
    billing(cy)
    b, _, _ = textbox(wall_x, cy, "activeCount\n→ count", size=12,
                      fill=BLUE_FILL, stroke=NEG, sw=2, min_w=150, bold=True)
    frags.append(b)
    dev_table(1130, cy)
    frags.append(arrow(216, cy, wall_x - 82, cy, color=LINE))            # білінг → контракт
    frags.append(arrow(wall_x + 82, cy, 1035, cy, color=MUTED))          # власник → своя таблиця
    frags.append(text((wall_x + 82 + 1035) / 2, cy - 14, "свій SQL: status='active'",
                      size=10.5, color=MUTED))
    frags.append(text(150, cy - 44, "RPC-виклик", size=12.5, color=FIELD,
                      bold=True, anchor="start"))
    frags.append(mtext(430, cy + 52,
                       ["зміна сталася за стіною контракту —",
                        "контракт той самий, виклик білінга цілий"],
                       size=12, color=FIELD))

    # ── Доріжка 3: проєкція ──
    cy = 640
    billing(cy)
    b, _, _ = textbox(430, cy, "home_device_state\n(таблиця білінга)", size=11.5,
                      fill=GREEN_FILL, stroke=FIELD, sw=1.8, min_w=210)
    frags.append(b)
    dev_table(1130, cy)
    frags.append(arrow(216, cy, 322, cy, color=FIELD))                   # білінг читає своє
    frags.append(text(269, cy - 12, "читає", size=10.5, color=MUTED))
    frags.append(arrow(1035, cy, 540, cy, color=FIELD))                  # подія: власник → білінгова таблиця
    frags.append(text(790, cy - 12, "device.activated", size=11, color=FIELD, bold=True))
    frags.append(text(150, cy - 44, "проєкція на подіях", size=12.5, color=FIELD,
                      bold=True, anchor="start"))
    frags.append(mtext(720, cy + 56,
                       ["білінг чужого сховища не читає взагалі;",
                        "подія тієї самої форми тече далі — проєкція недоторкана"],
                       size=12, color=FIELD))

    render(os.path.join(IMG, "rename-hit-three-styles.svg"), W, H, *frags,
           title="Власник перейменовує колонку — і три стилі відповідають по-різному")


def fig_coupling_surface():
    """Поверхня зчеплення: схема (широка) → контракт → факт-подія (вузька)."""
    W, H = 1360, 600
    frags = []

    frags.append(text(110, 62,
                      "ширина смуги = поверхня зчеплення: скільки всього мусить не змінитися, щоб білінг працював",
                      size=12.5, color=MUTED, anchor="start"))

    def bar(y, cap, cap_fill, cap_stroke, tiles, tile_w, caption, cap_color):
        capw = 150
        frags.append(fitbox(110, y, capw, 66, cap, size=13, fill=cap_fill,
                             stroke=cap_stroke, sw=2, bold=True))
        x = 110 + capw + 16
        for t in tiles:
            frags.append(fitbox(x, y + 8, tile_w, 50, t, size=11.5,
                                fill=FILL, stroke=cap_stroke))
            x += tile_w + 12
        frags.append(text(110, y + 92, caption, size=12.5, color=cap_color,
                          bold=True, anchor="start"))

    bar(96, "СХЕМА", RED_FILL, POS,
        ["таблиця\ndevices", "колонка\nhome_id", "колонка\nactive",
         "тип\nboolean", "зміст\nactive=true"], 128,
        "спільна таблиця — залежиш від УСЬОГО цього; будь-яка зміна може зачепити", POS)

    bar(248, "КОНТРАКТ", BLUE_FILL, NEG,
        ["activeCount(homeId) → count"], 300,
        "RPC — лише обіцяна форма; свою схему власник міняє вільно", NEG)

    bar(400, "ПОДІЯ", GREEN_FILL, FIELD,
        ["device.activated { deviceId, homeId, at }"], 300,
        "проєкція — лише форма факту; ще й розчеплена в часі", FIELD)

    # вісь ризик/клопіт праворуч
    ax = 1150
    frags.append(arrow(ax, 116, ax, 452, color=MUTED, sw=1.6))
    frags.append(mtext(ax + 20, 150,
                       ["згори вниз", "поверхня вужчає:", "• менше може зламатися",
                        "• більший клопіт вести"], size=12, color=INK, anchor="start"))

    render(os.path.join(IMG, "coupling-surface.svg"), W, H, *frags,
           title="До чого причеплений білінг: схема → контракт → факт-подія")


if __name__ == "__main__":
    fig_four_styles()
    fig_shared_db_trap()
    fig_integration_decision()
    fig_styles_lineage()
    fig_rename_hit()
    fig_coupling_surface()
    print("OK: four-styles.svg, shared-db-trap.svg, integration-decision.svg, styles-lineage.svg, "
          "rename-hit-three-styles.svg, coupling-surface.svg")
