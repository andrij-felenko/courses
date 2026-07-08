# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_spectrum():
    """Три форми одного застосунку на осі: клубок-моноліт → модульний моноліт → мікросервіси.
    Показує, що модульний моноліт має ті самі МЕЖІ, що й мікросервіси, але один процес."""
    W, H = 940, 430
    frags = []

    # заголовки трьох колонок
    col_x = [160, 470, 780]
    titles = ["Моноліт-клубок", "Модульний моноліт", "Мікросервіси"]
    subt = ["один процес,\nмеж немає", "один процес,\nмежі є", "багато процесів,\nмежі є"]
    for i, cx in enumerate(col_x):
        frags.append(text(cx, 40, titles[i], size=16, bold=True))
        frags.append(mtext(cx, 62, subt[i], size=12, color=MUTED))

    # ── колонка 1: клубок (модулі є, але все з усім переплетено) ──
    box = rect(40, 90, 240, 250, fill="#ffffff", stroke=LINE, sw=2)
    frags.append(box)
    pts = [(100, 150), (220, 150), (100, 240), (220, 240), (160, 300)]
    # хаотичні лінії між усіма
    import itertools
    for a, b in itertools.combinations(pts, 2):
        frags.append(line(a[0], a[1], b[0], b[1], color="#c9ced6", sw=1.2))
    for (x, y) in pts:
        frags.append(circle(x, y, 16, fill=FILL, stroke=LINE, sw=1.5))

    # ── колонка 2: модульний моноліт (один процес-рамка, чисті модулі, вузькі стрілки) ──
    box2 = rect(350, 90, 240, 250, fill="#ffffff", stroke=LINE, sw=2.5)
    frags.append(box2)
    frags.append(text(470, 110, "один процес", size=11, color=FIELD, italic=True))
    m2 = [(415, 160), (525, 160), (415, 250), (525, 250)]
    labels = ["Замов.", "Склад", "Оплата", "Пошта"]
    for (x, y), lb in zip(m2, labels):
        b, w, h = textbox(x, y, lb, size=12, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.8)
        frags.append(b)
    # лише дозволені виклики через межу (вертикальні/горизонтальні, повз написи)
    frags.append(arrow(415, 178, 415, 232, color=INK))   # Замов -> Оплата
    frags.append(arrow(525, 178, 525, 232, color=INK))   # Склад -> Пошта
    frags.append(arrow(447, 250, 493, 250, color=INK))   # Оплата -> Пошта

    # ── колонка 3: мікросервіси (ті самі модулі, кожен у своїй рамці + мережа) ──
    m3 = [(720, 150), (840, 150), (720, 250), (840, 250)]
    for (x, y), lb in zip(m3, labels):
        b, w, h = textbox(x, y, lb, size=12, pad=8, fill="#eef2fd", stroke=NEG, sw=1.8)
        frags.append(b)
    # мережеві виклики — пунктир (через мережу)
    frags.append(line(720, 172, 720, 228, color=NEG, sw=1.6, dash="4 3"))
    frags.append(line(840, 172, 840, 228, color=NEG, sw=1.6, dash="4 3"))
    frags.append(line(752, 250, 808, 250, color=NEG, sw=1.6, dash="4 3"))
    frags.append(text(780, 300, "виклики йдуть по мережі", size=11, color=NEG, italic=True))

    # нижній підпис-вісь
    frags.append(line(40, 370, 900, 370, color=MUTED, sw=1))
    frags.append(text(160, 392, "межі немає", size=12, color=MUTED))
    frags.append(text(470, 392, "межі в коді", size=12, color=FIELD, bold=True))
    frags.append(text(780, 392, "межі в коді + мережі", size=12, color=NEG))
    frags.append(text(470, 414, "та сама різанина на модулі — різна ціна за перетин межі",
                      size=12, color=INK))

    render(os.path.join(OUT, 'spectrum.svg'), W, H, *frags)


def fig_boundary():
    """Що таке межа модуля: публічний фасад (вузькі двері) проти прямого лазу в нутрощі."""
    W, H = 940, 440
    frags = []

    # МОДУЛЬ А (клієнт) — ліворуч
    frags.append(rect(40, 110, 280, 210, fill="#ffffff", stroke=LINE, sw=2))
    frags.append(text(180, 100, "Модуль «Замовлення»", size=14, bold=True))
    b, w, h = textbox(180, 215, "код замовлення", size=12, pad=10, fill=FILL)
    frags.append(b)

    # МОДУЛЬ Б (сервер) — праворуч, має фасад і нутрощі
    frags.append(rect(620, 110, 280, 210, fill="#ffffff", stroke=LINE, sw=2))
    frags.append(text(760, 100, "Модуль «Склад»", size=14, bold=True))
    # фасад — вузька зелена смуга-двері на лівому краї модуля Б
    frags.append(rect(618, 150, 30, 130, fill="#eef6ef", stroke=FIELD, sw=2.5, rx=4))
    frags.append(mtext(633, 200, "Ф\nА\nС\nА\nД", size=12, color=FIELD, bold=True, lh=1.15))
    # нутрощі — правіше фасаду, з великим відступом
    b2, w2, h2 = textbox(775, 215, "приватні\nтаблиці й класи", size=12, pad=10, fill=FILL)
    frags.append(b2)

    # дозволена стрілка — через фасад (входить у зелену смугу)
    frags.append(arrow(320, 200, 616, 200, color=FIELD))
    frags.append(text(468, 185, "дозволено", size=13, color=FIELD, bold=True))
    frags.append(text(468, 226, "reserve(id, n)", size=12, color=INK))

    # заборонена стрілка — прямо в нутрощі, нижче й далеко від решти написів
    frags.append(line(320, 300, 700, 300, color=POS, sw=2, dash="6 4"))
    # хрестик по центру забороненої лінії
    frags.append(line(503, 292, 517, 306, color=POS, sw=3))
    frags.append(line(517, 292, 503, 306, color=POS, sw=3))
    # підпис забороненої — окремим рядком нижче, по центру всієї фігури
    frags.append(text(470, 350, "заборонено: лізти повз фасад у приватні таблиці",
                      size=13, color=POS, bold=True))

    render(os.path.join(OUT, 'boundary.svg'), W, H, *frags)


def fig_timeline():
    """Хронологія народження форми: від «моноліт — лайка» до промислового доказу.
    Горизонтальна вісь; віхи чергуються над/під лінією з ЗАПАСОМ, щоб написи не накладались."""
    W, H = 960, 560
    frags = []

    # вісь
    ax_y = 280
    x0, x1 = 70, 890
    frags.append(line(x0, ax_y, x1, ax_y, color=MUTED, sw=2.5))
    frags.append(text(x1, ax_y - 12, "час", size=12, color=MUTED, italic=True, anchor="end"))

    # віхи: (x, рік, хто, рядки-опис, над_лінією?, колір-рамки)
    milestones = [
        (150, "~2013", "Simon Brown",
         ["говорить про", "«modular monolith»", "на конференціях"], True, FIELD),
        (355, "2015", "Martin Fowler",
         ["MonolithFirst +", "MicroservicePremium:", "починай з моноліта"], False, NEG),
        (560, "2016", "DHH",
         ["«majestic monolith»:", "Basecamp — цілісний", "моноліт малою командою"], True, FIELD),
        (785, "2019—2020", "Shopify",
         ["мільйони рядків Ruby;", "межі стереже Packwerk", "(промисловий доказ)"], False, NEG),
    ]

    for x, yr, who, desc, above, col in milestones:
        # вузол на осі
        frags.append(circle(x, ax_y, 9, fill=col, stroke="#ffffff", sw=2))
        # картка над або під віссю, з відступом від осі
        card_w = 178
        card_h = 96
        if above:
            cy = ax_y - 40 - card_h / 2       # центр картки вище осі
            stem_top = cy + card_h / 2
            frags.append(line(x, ax_y - 9, x, stem_top, color=col, sw=1.6))
        else:
            cy = ax_y + 40 + card_h / 2       # центр картки нижче осі
            stem_bot = cy - card_h / 2
            frags.append(line(x, ax_y + 9, x, stem_bot, color=col, sw=1.6))
        cx = x
        # рамка картки
        frags.append(rect(cx - card_w / 2, cy - card_h / 2, card_w, card_h,
                          fill="#ffffff", stroke=col, sw=2))
        # рік — жирний угорі картки
        frags.append(text(cx, cy - card_h / 2 + 20, yr, size=14, bold=True, color=col))
        # хто
        frags.append(text(cx, cy - card_h / 2 + 40, who, size=13, bold=True, color=INK))
        # опис — три рядки дрібніше
        frags.append(mtext(cx, cy - card_h / 2 + 58, desc, size=11, color=MUTED, lh=1.28))

    # рамка-мораль унизу, окремо, з великим відступом від нижньої картки
    moral = "спільна теза всіх чотирьох: спершу чисті МЕЖІ, і лише потім — питання про мережу"
    b, bw, bh = textbox(W / 2, 512, moral, size=13, pad=12,
                        fill="#eef6ef", stroke=FIELD, sw=2, color=INK, bold=True)
    frags.append(b)

    render(os.path.join(OUT, 'timeline.svg'), W, H, *frags)


def fig_arrows():
    """Інваріант межі: КУДИ стрілці можна, куди ні (для proj-module-boundaries).
    orders -> warehouse ЧЕРЕЗ фасад (можна); orders -> WarehouseImpl (не можна);
    прямий SELECT з чужої таблиці (не можна)."""
    W, H = 960, 470
    frags = []

    frags.append(text(W / 2, 34, "Куди дозволено стрілку, куди ні", size=17, bold=True))

    # ── МОДУЛЬ orders (ліворуч) ──
    frags.append(rect(50, 90, 300, 300, fill="#ffffff", stroke=LINE, sw=2))
    frags.append(text(200, 82, "модуль orders", size=14, bold=True))
    b, w, h = textbox(200, 160, "OrderService", size=13, pad=10, fill="#eef2fd", stroke=NEG, sw=1.8)
    frags.append(b)
    b, w, h = textbox(200, 320, "приватна\ntable orders_db", size=12, pad=10, fill=FILL)
    frags.append(b)

    # ── МОДУЛЬ warehouse (праворуч): фасад-смуга + нутрощі ──
    frags.append(rect(610, 90, 300, 300, fill="#ffffff", stroke=LINE, sw=2))
    frags.append(text(760, 82, "модуль warehouse", size=14, bold=True))
    frags.append(rect(608, 130, 34, 130, fill="#eef6ef", stroke=FIELD, sw=2.5, rx=4))
    frags.append(mtext(625, 172, "Ф\nА\nС\nА\nД", size=12, color=FIELD, bold=True, lh=1.15))
    b, w, h = textbox(790, 165, "WarehouseImpl\n(package-private)", size=12, pad=10, fill=FILL)
    frags.append(b)
    b, w, h = textbox(790, 320, "приватна\ntable stock_db", size=12, pad=10, fill=FILL)
    frags.append(b)

    # ── дозволена стрілка: OrderService -> фасад ──
    frags.append(arrow(255, 155, 606, 150, color=FIELD, sw=2.2))
    frags.append(text(430, 130, "дозволено", size=13, color=FIELD, bold=True))
    frags.append(text(430, 148, "warehouse.reserve(id, n)", size=11, color=INK))

    # ── заборонена 1: OrderService -> WarehouseImpl (повз фасад у клас) ──
    frags.append(line(255, 178, 735, 178, color=POS, sw=2, dash="6 4"))
    frags.append(line(487, 171, 501, 185, color=POS, sw=3))
    frags.append(line(501, 171, 487, 185, color=POS, sw=3))
    frags.append(text(430, 205, "заборонено: імпорт чужого класу повз фасад", size=12, color=POS, bold=True))

    # ── заборонена 2: orders_db читає stock_db (спільна база) ──
    frags.append(line(255, 335, 735, 335, color=POS, sw=2, dash="6 4"))
    frags.append(line(487, 328, 501, 342, color=POS, sw=3))
    frags.append(line(501, 328, 487, 342, color=POS, sw=3))
    frags.append(text(430, 362, "заборонено: SELECT з чужої таблиці", size=12, color=POS, bold=True))

    frags.append(line(50, 410, 910, 410, color=MUTED, sw=1))
    frags.append(text(W / 2, 434, "інваріант: стрілка входить ЛИШЕ у фасад — ніколи в клас чи таблицю сусіда",
                      size=13, color=INK, bold=True))
    frags.append(text(W / 2, 456, "напрям теж не байдужий: у модель предмету стрілки сходяться, з неї — ні",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, 'arrows.svg'), W, H, *frags)


def fig_enforce_layers():
    """Три рівні вимушеної межі як ешелони оборони: що кожен ловить, чого не дістає."""
    W, H = 960, 470
    frags = []
    frags.append(text(W / 2, 34, "Три ешелони вимушеної межі", size=17, bold=True))

    rows = [
        ("1. Видимість мови", "#eef6ef", FIELD,
         "package-private (Java) · internal (C#)",
         "компілятор: чужий клас просто НЕ ВИДНО за іменем",
         "не дістає: Python / TS / Ruby — там public усе"),
        ("2. Сторож у конвеєрі", "#fef6e7", "#b9770e",
         "fitness-function: ArchUnit · Packwerk",
         "тест архітектури червоніє на забороненій залежності",
         "ловить і непрямі, і межу таблиць — головний ешелон"),
        ("3. Лінт імпортів", "#eef2fd", NEG,
         "no-restricted-imports (TS) · import-linter (Py)",
         "збірка падає на імпорті з чужих нутрощів",
         "де мова слабша — найдешевший сторож, ставиться першим"),
    ]
    y = 80
    for title, fill, stroke, tech, catches, miss in rows:
        frags.append(rect(60, y, 840, 110, fill=fill, stroke=stroke, sw=2))
        frags.append(text(90, y + 30, title, size=15, bold=True, anchor="start"))
        frags.append(text(90, y + 54, tech, size=12, color=INK, anchor="start"))
        frags.append(text(90, y + 78, "ловить: " + catches, size=12, color=INK, anchor="start"))
        frags.append(text(90, y + 98, miss, size=11, color=MUTED, italic=True, anchor="start"))
        y += 128

    frags.append(text(W / 2, 462, "ешелони складають: слабший на мові компенсуй сторожем і лінтом",
                      size=12, color=INK, bold=True))

    render(os.path.join(OUT, 'enforce-layers.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_spectrum()
    fig_boundary()
    fig_timeline()
    fig_arrows()
    fig_enforce_layers()
    print('figs done')
