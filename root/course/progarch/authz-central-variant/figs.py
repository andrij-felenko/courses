# -*- coding: utf-8 -*-
"""Фігури до кроку «Варіант Б: рішення ухвалює один центр» (progarch / nodes-identity-access).
П'ять фігур (три — до статті, дві — до вставки hist-zanzibar-lineage):
  1) pdp-split             — топологію перевернуто: PEP у кожному сервісі, PDP один на всіх;
  2) decision-data-gap     — центр знає запит, але не факти — вони живуть у сервісах;
  3) three-ways-central    — «централізувати» = три різні архітектури (рішення / політика / дані);
  4) policy-vs-data-lineage — дві гілки центру: політика (XACML→OPA→Cedar) і дані (Zanzibar→…);
  5) new-enemy-problem     — чому центр даних мусить поважати ПОРЯДОК подій (zookie).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_TINT = "#eaf7ef"
BLUE_TINT = "#eaf0fd"
RED_TINT = "#fdecea"
HEAD_TINT = "#eef2f7"
PURPLE = "#7d3c98"
PURPLE_TINT = "#f4ecfb"


# ── Фігура 1: PEP у кожному сервісі, PDP один на всіх ─────────────────────────
def fig_pdp_split():
    W, H = 940, 470
    p = []
    # три сервіси ліворуч — кожен лишає собі лише гейт (PEP)
    svc = ["Сервіс пристроїв", "Сервіс камер", "Сервіс правил"]
    ys = [92, 210, 328]
    edge_y = [190, 250, 310]   # куди приходить стрілка на лівому краї PDP
    for name, y in zip(svc, ys):
        p.append(rect(48, y, 250, 92, fill=BG, stroke=INK, sw=1.8))
        p.append(text(173, y + 30, name, size=13, bold=True))
        p.append(fitbox(70, y + 44, 206, 34, "лише гейт (PEP)", size=11.5,
                        fill=HEAD_TINT, stroke=MUTED, sw=1.1, color=MUTED))
    # центральний сервіс авторизації праворуч
    p.append(rect(596, 150, 300, 200, fill=GREEN_TINT, stroke=FIELD, sw=2.4))
    p.append(text(746, 186, "Центральний сервіс", size=14, bold=True))
    p.append(text(746, 208, "авторизації (PDP)", size=14, bold=True))
    p.append(fitbox(628, 236, 236, 46, "правило — в ОДНОМУ місці\n(для всіх сервісів)",
                    size=12, fill=BG, stroke=FIELD, sw=1.6))
    p.append(fitbox(628, 292, 236, 34, "журнал усіх рішень", size=11.5,
                    fill=BG, stroke=MUTED, sw=1.1, color=MUTED))
    # стрілки «питає / вердикт» від кожного сервіса в центр
    for y, ey in zip(ys, edge_y):
        p.append(arrow(302, y + 46, 594, ey, sw=1.6))
    p.append(text(446, 124, "усі питають: «чи можна?»", size=11.5, color=MUTED, bold=True))
    p.append(text(446, 424, "вердикт — той самий для всіх, хто спитав",
                  size=11.5, color=MUTED))
    render(os.path.join(IMG, "pdp-split.svg"), W, H, *p,
           title="Топологію перевернуто: PEP лишився в сервісах, PDP — один на всіх")


# ── Фігура 2: центр знає запит, але не факти ──────────────────────────────────
def fig_decision_data_gap():
    W, H = 960, 470
    p = []
    # центр угорі з отриманим запитом
    p.append(rect(330, 62, 300, 104, fill=BLUE_TINT, stroke=NEG, sw=2))
    p.append(text(480, 88, "Центральний PDP отримав запит", size=13, bold=True))
    p.append(fitbox(352, 100, 256, 52, "Богдан · «відчинити» · door:42",
                    size=13, fill=BG, stroke=NEG, sw=1.4))
    p.append(text(480, 196, "…але для вердикту бракує двох фактів, яких у центрі немає:",
                  size=12, color=POS, bold=True))
    # два «бракує факту» + сервіс-власник під кожним; стрілки «бракує» виходять із коробки PDP
    cols = [
        (60, 404, "чий це замок door:42?\n(потрібен власник об'єкта)",
             "Сервіс пристроїв\nтут живе власник #42"),
        (520, 556, "Богдан — член дому 7?\n(потрібне членство)",
              "Сервіс домогосподарств\nтут живе членство"),
    ]
    for x, exit_x, need, home in cols:
        p.append(fitbox(x, 224, 380, 60, need, size=12.5, fill=RED_TINT,
                        stroke=POS, sw=1.6))
        p.append(arrow(exit_x, 166, x + 190, 222, sw=1.5))       # PDP (низ коробки) → бракує факту
        p.append(arrow(x + 190, 286, x + 190, 344, color=FIELD, sw=1.6))  # факт → сервіс
        p.append(fitbox(x, 346, 380, 60, home, size=12.5, fill=GREEN_TINT,
                        stroke=FIELD, sw=1.6))
    # підпис-мораль
    p.append(text(480, 438,
                  "PDP мусить або дотягтися по ці факти (стрибок + застарілість), "
                  "або отримати їх у контексті запиту.",
                  size=11.5, color=MUTED))
    render(os.path.join(IMG, "decision-data-gap.svg"), W, H, *p,
           title="Центр знає запит, але не знає фактів — вони живуть у сервісах")


# ── Фігура 3: три способи «винести в центр» ──────────────────────────────────
def fig_three_ways_central():
    W, H = 1040, 470
    p = []
    panels = [
        (28,  "Центр ВИРІШУЄ", BLUE_TINT, NEG,
         "централізуємо\nРІШЕННЯ",
         ["сервіс (PEP)", "центр (PDP)"],
         "ціна: стрибок на кожен\nзапит + залежність від центру"),
        (368, "Центр — ПОЛІТИКУ", GREEN_TINT, FIELD,
         "централізуємо\nПОЛІТИКУ",
         ["центр політик", "sidecar: оцінка ТУТ"],
         "ціна: потрібні локальні\nдані; стрибка на рішення нема"),
        (708, "Центр — ДАНІ", "#f6eefb", "#7d3c98",
         "централізуємо\nДАНІ відносин",
         ["сервіси пишуть", "граф кортежів"],
         "ціна: злити дані в центр +\nмашинерія причинності (zookie)"),
    ]
    pw = 304
    for x, head, tint, col, tag, boxes, price in panels:
        p.append(rect(x, 60, pw, 386, fill=tint, stroke=col, sw=1.8))
        p.append(text(x + pw / 2, 92, head, size=14, bold=True))
        p.append(fitbox(x + 40, 108, pw - 80, 46, tag, size=12, bold=True,
                        fill=BG, stroke=col, sw=1.6, color=col))
        # мінідіаграма: два боксики зі стрілкою вниз
        p.append(fitbox(x + 44, 182, pw - 88, 48, boxes[0], size=12,
                        fill=BG, stroke=INK, sw=1.4))
        p.append(arrow(x + pw / 2, 232, x + pw / 2, 276, sw=1.6))
        p.append(fitbox(x + 44, 278, pw - 88, 48, boxes[1], size=12,
                        fill=BG, stroke=INK, sw=1.4))
        # ціна
        p.append(fitbox(x + 24, 350, pw - 48, 72, price, size=11.5,
                        fill=BG, stroke=MUTED, sw=1.1, color=MUTED))
    render(os.path.join(IMG, "three-ways-central.svg"), W, H, *p,
           title="«Централізувати» — це три різні архітектури: рішення, політика або дані")


# ── Фігура 4 (вставка): дві гілки центру — політика й дані ────────────────────
def fig_policy_vs_data_lineage():
    W, H = 1080, 430
    p = []
    # --- лейн «політика» (верхній, зелений) ---
    p.append(fitbox(24, 64, 200, 104, "ЦЕНТР — ПОЛІТИКА\nзводимо ПРАВИЛО",
                    size=13, bold=True, fill=GREEN_TINT, stroke=FIELD, sw=2, color=FIELD))
    pol = [
        (400, "XACML 1.0 · 2003\nOASIS · XML\nвинесений PDP-сервер"),
        (660, "OPA · 2016 · Styra\nмова Rego (з Datalog)\nвипуск CNCF · 2021"),
        (920, "Cedar · 2023 · AWS\nмова Cedar (Rust)\nVerified Permissions"),
    ]
    p.append(arrow(224, 116, 290, 116, sw=1.6))
    prev_r = None
    for cx, txt in pol:
        p.append(fitbox(cx - 110, 64, 220, 104, txt, size=12.5, fill=BG, stroke=FIELD, sw=1.6))
        if prev_r is not None:
            p.append(arrow(prev_r, 116, cx - 110, 116, sw=1.6))
        prev_r = cx + 110
    # --- лейн «дані» (нижній, фіолетовий) ---
    p.append(fitbox(24, 284, 200, 104, "ЦЕНТР — ДАНІ\nзводимо ЗВ'ЯЗКИ",
                    size=13, bold=True, fill=PURPLE_TINT, stroke=PURPLE, sw=2, color=PURPLE))
    dat = [
        (400, "Zanzibar · 2019\nGoogle (USENIX ATC)\nкортежі зв'язку"),
        (660, "Ory Keto · 2021\nSpiceDB / AuthZed · 2021\nперші відкриті"),
        (920, "OpenFGA · 2022\nAuth0 / Okta\nCNCF Sandbox"),
    ]
    p.append(arrow(224, 336, 290, 336, sw=1.6))
    prev_r = None
    for cx, txt in dat:
        p.append(fitbox(cx - 110, 284, 220, 104, txt, size=12.5, fill=BG, stroke=PURPLE, sw=1.6))
        if prev_r is not None:
            p.append(arrow(prev_r, 336, cx - 110, 336, sw=1.6))
        prev_r = cx + 110
    # --- містковий підпис між лейнами ---
    p.append(text(600, 233, "те саме «в центр» — але центр тримає РІЗНЕ",
                  size=13, color=MUTED, bold=True))
    render(os.path.join(IMG, "policy-vs-data-lineage.svg"), W, H, *p,
           title="Дві гілки «центру»: одні винесли ПРАВИЛО, інші — ГРАФ ЗВ'ЯЗКІВ")


# ── Фігура 5 (вставка): проблема нового ворога — центр даних поважає порядок ──
def fig_new_enemy_problem():
    W, H = 1080, 470
    p = []
    # дві події в часі
    p.append(fitbox(60, 62, 400, 82, "t1 — відкликали гостя Богдана\n−  home:7#member@user:bohdan",
                    size=13, fill=RED_TINT, stroke=POS, sw=1.8))
    p.append(fitbox(600, 62, 400, 82,
                    "t2 — додали новий замок #99\ndoor:99#home@home:7 (успадкує ACL дому 7)",
                    size=13, fill=BLUE_TINT, stroke=NEG, sw=1.8))
    p.append(arrow(462, 103, 598, 103, sw=1.7))
    p.append(text(530, 92, "згодом", size=11, color=MUTED))
    # перевірка
    p.append(fitbox(360, 188, 340, 66, "перевірка: Богдан · «відчинити» · door:99 ?",
                    size=13, bold=True, fill=HEAD_TINT, stroke=INK, sw=1.6))
    # дві розв'язки (підписи — обіч стрілок, не на них)
    p.append(arrow(452, 254, 320, 322, sw=1.6))
    p.append(text(316, 286, "без порядку", size=11.5, color=POS, bold=True, anchor="end"))
    p.append(arrow(608, 254, 762, 322, sw=1.6))
    p.append(text(766, 286, "zookie (порядок)", size=11.5, color=FIELD, bold=True, anchor="start"))
    p.append(fitbox(44, 324, 476, 112,
                    "Знімок СТАРИЙ (до t1):\nБогдан іще «член дому 7» →\nВІДЧИНЯЄ новий замок.\n"
                    "Це і є «проблема нового ворога».",
                    size=13, fill=RED_TINT, stroke=POS, sw=1.8))
    p.append(fitbox(560, 324, 476, 112,
                    "zookie: знімок НЕ старіший за t2 →\nвідкликання вже враховане →\n"
                    "ВІДМОВА.\nПорядок подій збережено.",
                    size=13, fill=GREEN_TINT, stroke=FIELD, sw=1.8))
    render(os.path.join(IMG, "new-enemy-problem.svg"), W, H, *p,
           title="Проблема нового ворога: центр даних мусить поважати ПОРЯДОК подій")


# ── Фігура 6 (вставка proj): межа довіри до фактів рішення ────────────────────
def fig_trust_boundary():
    W, H = 1000, 548
    p = []
    colw, lx, rx = 436, 40, 524
    top, ph = 58, 456

    # ліва панель — наївно віримо контексту
    p.append(rect(lx, top, colw, ph, fill=RED_TINT, stroke=POS, sw=2))
    p.append(text(lx + colw / 2, top + 28, "Наївно: віримо контексту як є",
                  size=14, bold=True, color=POS))
    p.append(fitbox(lx + 24, 104, colw - 48, 76,
                    "запит у центр:\nОксана · unlock · door:42\n"
                    "context.homeId = home:12   (ПІДРОБЛЕНО)",
                    size=12, fill=BG, stroke=POS, sw=1.4))
    p.append(arrow(lx + colw / 2, 182, lx + colw / 2, 214, sw=1.6))
    p.append(fitbox(lx + 24, 216, colw - 48, 78,
                    "наївний PDP довіряє контексту:\nОксана — власниця home:12? так\n"
                    "→ власнику unlock можна → ALLOW",
                    size=12, fill=BG, stroke=MUTED, sw=1.2, color=MUTED))
    p.append(arrow(lx + colw / 2, 296, lx + colw / 2, 330, sw=1.6))
    p.append(fitbox(lx + 24, 332, colw - 48, 64,
                    "чужий замок #42 (дім 7) ВІДЧИНЕНО\nIDOR через підроблений факт",
                    size=12.5, bold=True, fill=RED_TINT, stroke=POS, sw=1.8, color=POS))
    p.append(fitbox(lx + 24, 410, colw - 48, 92,
                    "корінь біди: факт для рішення прийшов від того,\n"
                    "хто за нього НЕ відповідає — клієнт вибрав\n"
                    "і замок, і «його» дім воднораз",
                    size=11.5, fill=BG, stroke=POS, sw=1.1, color=POS))

    # права панель — факт лише з авторитетного джерела
    p.append(rect(rx, top, colw, ph, fill=GREEN_TINT, stroke=FIELD, sw=2))
    p.append(text(rx + colw / 2, top + 28, "Правильно: факт — з авторитетного джерела",
                  size=13, bold=True, color=FIELD))
    p.append(fitbox(rx + 24, 104, colw - 48, 76,
                    "claim клієнта homeId=home:12 — ІГНОРУЄМО;\n"
                    "джерело правди: door:42 → home:7\n"
                    "(кортеж графа / сервіс пристроїв)",
                    size=12, fill=BG, stroke=FIELD, sw=1.4))
    p.append(arrow(rx + colw / 2, 182, rx + colw / 2, 214, sw=1.6))
    p.append(fitbox(rx + 24, 216, colw - 48, 78,
                    "PDP питає ГРАФ, а не контекст:\nОксана — член home:7? ні\n"
                    "(її членство у home:12, не тут)",
                    size=12, fill=BG, stroke=INK, sw=1.3))
    p.append(arrow(rx + colw / 2, 296, rx + colw / 2, 330, sw=1.6))
    p.append(fitbox(rx + 24, 332, colw - 48, 64,
                    "жодне правило не збіглося → DENY 403\nзамок лишається замкненим",
                    size=12.5, bold=True, fill=GREEN_TINT, stroke=FIELD, sw=1.8, color=FIELD))
    p.append(fitbox(rx + 24, 410, colw - 48, 92,
                    "правило: факт входить у рішення лише від\n"
                    "джерела, яке за нього ВІДПОВІДАЄ;\n"
                    "клієнт не відповідає ні за що",
                    size=11.5, fill=BG, stroke=FIELD, sw=1.1, color=FIELD))
    render(os.path.join(IMG, "trust-boundary.svg"), W, H, *p,
           title="Проблема даних для рішення: кому можна вірити на слово")


# ── Фігура 7 (вставка proj): зібраний гарячий шлях вердикту ───────────────────
def fig_verdict_path():
    W, H = 1060, 452
    p = []
    my, bw = 196, 180
    boxes = [
        (24,  "обробник (PEP)\nзавантажив об'єкт", BG, INK),
        (232, "шов Authorizer\nCentralAuthorizer", GREEN_TINT, FIELD),
        (440, "кеш вердиктів\nчесна свіжість", BLUE_TINT, NEG),
        (648, "стійкий клієнт\nbreaker + дедлайн", HEAD_TINT, INK),
        (856, "центр PDP\nграф кортежів", PURPLE_TINT, PURPLE),
    ]
    for x, label, tint, col in boxes:
        p.append(fitbox(x, my, bw, 76, label, size=12, bold=True,
                        fill=tint, stroke=col, sw=1.7, color=col))
    for x in (204, 412, 620, 828):
        p.append(arrow(x, my + 38, x + 26, my + 38, sw=1.7))

    # вхід зверху
    p.append(fitbox(24, 58, bw, 48, "запит користувача\n«відчинити door:42»",
                    size=11, fill=BG, stroke=MUTED, sw=1.1, color=MUTED))
    p.append(arrow(114, 106, 114, my - 2, sw=1.6))

    # кеш-хіт — коротке замикання без мережі
    p.append(fitbox(400, 96, 260, 46, "кеш-хіт → вердикт без мережі",
                    size=11, fill=BG, stroke=FIELD, sw=1.2, color=FIELD))
    p.append(arrow(530, 194, 530, 144, color=FIELD, sw=1.5))

    # подія revoke чистить кеш
    p.append(fitbox(360, 336, 224, 78,
                    "подія: мешканця виключили →\nчистимо запис ОДРАЗУ\n"
                    "(TTL — лише страховка)",
                    size=11, fill=BG, stroke=NEG, sw=1.3, color=NEG))
    p.append(arrow(472, 334, 472, my + 78, color=NEG, sw=1.6))

    # fail-closed гілка
    p.append(fitbox(612, 336, 300, 78,
                    "breaker відкрито / дедлайн / помилка →\nDENY (fail-closed):\n"
                    "новий чек замкнено, кеш ще тримає своє",
                    size=11, bold=True, fill=RED_TINT, stroke=POS, sw=1.6, color=POS))
    p.append(arrow(738, my + 78, 738, 334, color=POS, sw=1.6))

    render(os.path.join(IMG, "verdict-path.svg"), W, H, *p,
           title="Зібраний гарячий шлях: шов → кеш → стійкий клієнт → центр")


if __name__ == "__main__":
    fig_pdp_split()
    fig_decision_data_gap()
    fig_three_ways_central()
    fig_policy_vs_data_lineage()
    fig_new_enemy_problem()
    fig_trust_boundary()
    fig_verdict_path()
    print("OK: 7 SVG ->", IMG)
