# -*- coding: utf-8 -*-
"""Фігури до кроку «Запит крізь DH» (progarch / nodes-identity-access).
П'ять фігур (3 — до статті, 2 — до вставки proj-dh-auth-path):
  1) request-road          — дорога одного запиту крізь дві брами (authn+груба / тонка об'єктна);
  2) two-gates-two-attacks — дві брами ловлять різні атаки (гість / IDOR);
  3) hybrid-one-rule       — гібрид: одне джерело правила, дві точки застосування;
  4) attestation-crossing  — [proj] межа хмари: суб'єкт перетинає її засвідченням, не токеном;
  5) four-ways-identity     — [proj] чотири способи сказати сервісу «хто це», переживає один.
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
GREY_TINT = "#eef2f7"


# ── Фігура 1: дорога запиту крізь дві брами ──────────────────────────────────
def fig_request_road():
    W, H = 1180, 486
    p = []
    ymid = 250
    # телефон
    p.append(fitbox(24, 196, 176, 108,
                    "телефон\nБогдана\nPOST /devices/\n42/unlock\n+ access-токен",
                    size=12, fill=FILL))
    p.append(arrow(202, ymid, 250, ymid))

    # ── Брама 1 — край хмари ──
    p.append(rect(254, 60, 356, 352, fill=BG, stroke=INK, sw=2))
    p.append(text(432, 88, "Брама 1 · край хмари (шлюз)", size=13.5, bold=True))
    p.append(fitbox(276, 104, 312, 78,
                    "Автентифікація\nтокен → суб'єкт: Богдан\nпротух / підроблено → 401",
                    size=12, fill=GREY_TINT))
    p.append(arrow(432, 184, 432, 208))
    p.append(fitbox(276, 210, 312, 96,
                    "Груба авторизація (центральна)\nчи роль узагалі дозволяє\nкоманди пристроям?\nгість → 403",
                    size=12, fill=BLUE_TINT, stroke=NEG, sw=1.8))
    p.append(mtext(432, 342, ["на руках: лише токен —", "об'єкта ще НЕ видно"],
                   size=11, color=MUTED))
    p.append(mtext(432, 384, ["об'єктну перевірку", "тут зробити НЕМОЖЛИВО"],
                   size=11, color=POS))

    p.append(arrow(612, ymid, 660, ymid))
    p.append(mtext(636, ymid - 14, ["несе", "суб'єкта"], size=10.5, color=MUTED))

    # ── Брама 2 — сервіс пристроїв ──
    p.append(rect(664, 60, 356, 352, fill=BG, stroke=INK, sw=2))
    p.append(text(842, 88, "Брама 2 · сервіс пристроїв", size=13.5, bold=True))
    p.append(fitbox(686, 104, 312, 78,
                    "Завантажити об'єкт:\nзамок #42  (у ньому homeId = 7)",
                    size=12, fill=GREY_TINT))
    p.append(arrow(842, 184, 842, 208))
    p.append(fitbox(686, 210, 312, 96,
                    "Тонка ОБ'ЄКТНА авторизація (PDP)\ncan(Богдан, unlock, замок#42)\n"
                    "член дому 7? роль дозволяє?\nчужий дім → 403",
                    size=12, fill=GREEN_TINT, stroke=FIELD, sw=2.2))
    p.append(mtext(842, 342, ["на руках: об'єкт + членство —", "тут IDOR нікуди сховатися"],
                   size=11, color=MUTED))
    p.append(mtext(842, 384, ["саме ця брама", "закриває чужий об'єкт"],
                   size=11, color=FIELD))

    p.append(arrow(1022, ymid, 1066, ymid))
    # замок
    p.append(fitbox(1070, 202, 96, 96, "дозволено\n→ хаб\n→ замок\nвідчинено",
                    size=11.5, fill=FILL))
    render(os.path.join(IMG, "request-road.svg"), W, H, *p,
           title="Дорога одного запиту: дві брами поспіль, кожна зі своїм питанням")


# ── Фігура 2: дві брами ловлять різні атаки ──────────────────────────────────
def fig_two_gates_two_attacks():
    W, H = 1180, 470
    p = []
    colx = [24, 250, 604, 958]  # left label, Брама 1, Брама 2, вихід
    # заголовки колонок
    p.append(text(360, 74, "Брама 1 · край (груба, без об'єкта)", size=12.5, bold=True))
    p.append(text(714, 74, "Брама 2 · сервіс (тонка, з об'єктом)", size=12.5, bold=True))

    # ── Ряд 1: гість ──
    y1 = 132
    p.append(fitbox(24, y1 - 34, 200, 70, "Гість\nтисне «відчинити»", size=12, fill=FILL))
    p.append(arrow(228, y1, 250, y1))
    p.append(fitbox(250, y1 - 40, 300, 80,
                    "роль «гість» не несе\nскоупу команд пристроям",
                    size=12, fill=RED_TINT, stroke=POS, sw=2))
    p.append(text(400, y1 + 58, "✗ СТОП → 403 на краю", size=12.5, color=POS, bold=True))
    p.append(fitbox(604, y1 - 34, 300, 66, "Брама 2 навіть\nне знадобилась", size=12,
                    fill=GREY_TINT, stroke=MUTED, sw=1.2, color=MUTED))
    p.append(fitbox(958, y1 - 30, 198, 60, "чужого\nнічого не сталося", size=11.5,
                    fill=GREEN_TINT, stroke=FIELD, sw=1.6))

    # роздільник
    p.append(line(24, 250, 1156, 250, color=MUTED, sw=1, dash="4 5"))

    # ── Ряд 2: мешканець → чужий замок (IDOR) ──
    y2 = 344
    p.append(fitbox(24, y2 - 44, 200, 92,
                    "Мешканець дому 7\nпросить замок #99\n(дім Марти)", size=12, fill=FILL))
    p.append(arrow(228, y2, 250, y2))
    p.append(fitbox(250, y2 - 44, 300, 88,
                    "він МЕШКАНЕЦЬ зі скоупом —\nоб'єкта Брама 1 не бачить",
                    size=12, fill=GREEN_TINT, stroke=FIELD, sw=1.8))
    p.append(text(400, y2 + 64, "✓ пропущено далі", size=12, color=FIELD, bold=True))
    p.append(arrow(556, y2, 604, y2))
    p.append(fitbox(604, y2 - 44, 300, 88,
                    "замок #99 належить дому Марти,\nа не дому 7 — не збіглося",
                    size=12, fill=RED_TINT, stroke=POS, sw=2))
    p.append(text(754, y2 + 64, "✗ СТОП → 403 у сервісі", size=12, color=POS, bold=True))
    p.append(fitbox(958, y2 - 40, 198, 80, "IDOR спіймано:\nчужий замок\nлишився замкнений",
                    size=11.5, fill=GREEN_TINT, stroke=FIELD, sw=1.6))

    p.append(mtext(590, 438,
                   ["Брама 1 ловить «не той КЛАС дії»; Брама 2 — «ЧУЖИЙ об'єкт».",
                    "Кожна ловить те, чого інша структурно не може, — тому їх дві, а не одна."],
                   size=11.5, color=INK))
    render(os.path.join(IMG, "two-gates-two-attacks.svg"), W, H, *p,
           title="Дві брами — дві різні атаки: жодна не зайва")


# ── Фігура 3: гібрид — одне правило, дві точки застосування ──────────────────
def fig_hybrid_one_rule():
    W, H = 1060, 452
    p = []
    # джерело правила зверху
    p.append(fitbox(300, 62, 460, 92,
                    "ПРАВИЛО — одне джерело\nчлен дому + роль ∈ {власник, мешканець} → unlock",
                    size=13, bold=True, fill=GREEN_TINT, stroke=FIELD, sw=2))
    p.append(mtext(530, 178, ["один погляд · без дрейфу копій · один аудит",
                              "«хто взагалі може відчиняти?» — одна відповідь"],
                   size=11.5, color=MUTED))

    # дві стрілки вниз до брам
    p.append(arrow(420, 200, 300, 250))
    p.append(arrow(640, 200, 760, 250))

    # Брама 1
    p.append(fitbox(96, 254, 372, 128,
                    "Брама 1 · край (шлюз)\n\nзастосовує ОБ'ЄКТО-НЕЗАЛЕЖНУ частину:\n"
                    "клас дії, скоуп ролі\n— дешево, до входу в сервіс",
                    size=12.5, fill=BLUE_TINT, stroke=NEG, sw=1.8))
    # Брама 2
    p.append(fitbox(592, 254, 372, 128,
                    "Брама 2 · сервіс пристроїв\n\nзастосовує ОБ'ЄКТНУ частину:\n"
                    "«цей замок — у ТВОЄМУ домі?»\n— поруч із даними, з об'єктом у руках",
                    size=12.5, fill=GREEN_TINT, stroke=FIELD, sw=1.8))

    p.append(mtext(530, 416,
                   ["Гібрид: єдине правило (як у Варіанті Б) + локальна об'єктна перевірка (як у Варіанті А).",
                    "Правило одне — точок застосування дві."],
                   size=11.5, color=INK))
    render(os.path.join(IMG, "hybrid-one-rule.svg"), W, H, *p,
           title="Гібрид DH: одне джерело правила, дві точки застосування")


# ── Фігура 4 [proj]: межа хмари — засвідчення замість сирого токена ───────────
def fig_attestation_crossing():
    W, H = 1300, 560
    p = []
    ymid = 250
    # телефон із клієнтським токеном
    p.append(fitbox(15, 185, 120, 130,
                    "телефон\nБогдана\naccess-токен\n(підпис клієнта)",
                    size=11.5, fill=FILL))
    p.append(arrow(139, ymid, 165, ymid))

    # ── Брама 1 — шлюз на краю хмари ──
    p.append(rect(170, 80, 400, 360, fill=BG, stroke=INK, sw=2))
    p.append(text(370, 108, "Брама 1 · шлюз (край хмари)", size=13.5, bold=True))
    p.append(fitbox(192, 124, 356, 78,
                    "Автентифікація\nverifyAccessToken(token)\nпідпис локально → суб'єкт, інакше 401",
                    size=11.5, fill=GREY_TINT))
    p.append(arrow(370, 202, 370, 222))
    p.append(fitbox(192, 224, 356, 80,
                    "Груба авторизація (скоуп)\nтокен несе device:command?\nгість (лише device:view) → 403",
                    size=11.5, fill=BLUE_TINT, stroke=NEG, sw=1.8))
    p.append(arrow(370, 304, 370, 320))
    p.append(fitbox(192, 322, 356, 72,
                    "Карбує внутрішнє засвідчення\nпідпис ключем ШЛЮЗУ · aud=devices · TTL≈10 с",
                    size=11, fill=GREEN_TINT, stroke=FIELD, sw=1.8))
    p.append(mtext(370, 470, ["на руках лише токен —", "об'єкта тут ще не видно"],
                   size=11, color=MUTED))

    # ── межа хмари (з розривом під перехід) ──
    p.append(line(610, 70, 610, 222, color=MUTED, sw=1.5, dash="6 6"))
    p.append(line(610, 278, 610, 500, color=MUTED, sw=1.5, dash="6 6"))
    p.append(text(610, 60, "межа хмари", size=12, color=MUTED, italic=True))
    p.append(arrow(575, ymid, 695, ymid, color=FIELD, sw=2.2))
    p.append(text(650, 240, "суб'єкт, засвідчений хмарою", size=10.5, color=FIELD, italic=True))

    # ── Брама 2 — сервіс пристроїв ──
    p.append(rect(700, 80, 400, 360, fill=BG, stroke=INK, sw=2))
    p.append(text(900, 108, "Брама 2 · сервіс пристроїв", size=13.5, bold=True))
    p.append(fitbox(722, 124, 356, 80,
                    "Прийняти засвідчення\nперевірити підписом ШЛЮЗУ → суб'єкт\n(сирий клієнтський токен НЕ читаємо)",
                    size=11, fill=GREY_TINT))
    p.append(arrow(900, 204, 900, 224))
    p.append(fitbox(722, 226, 356, 66,
                    "Завантажити об'єкт\nзамок #42 → homeId = 7",
                    size=11.5, fill=GREY_TINT))
    p.append(arrow(900, 292, 900, 312))
    p.append(fitbox(722, 314, 356, 80,
                    "Тонка ОБ'ЄКТНА перевірка (PDP)\ncan(суб'єкт, unlock, замок#42)\nчужий дім → 403",
                    size=11, fill=GREEN_TINT, stroke=FIELD, sw=2))
    p.append(mtext(900, 470, ["на руках і суб'єкт, і об'єкт —", "тут IDOR нікуди сховатися"],
                   size=11, color=MUTED))

    # вихід
    p.append(arrow(1100, ymid, 1126, ymid))
    p.append(fitbox(1130, 205, 150, 90, "дозволено\n→ хаб\n→ замок\nвідчинено", size=11, fill=FILL))

    # підсумковий рядок унизу
    p.append(mtext(650, 516,
                   ["Крізь межу йде СВІЖЕ внутрішнє засвідчення (підпис шлюзу · aud=devices · TTL≈10 с), не сирий клієнтський токен.",
                    "Сервіс вірить особі, засвідченій хмарою, — а не «місцю, звідки прийшов запит»."],
                   size=11, color=INK))
    render(os.path.join(IMG, "attestation-crossing.svg"), W, H, *p,
           title="Межа хмари: доведений суб'єкт перетинає її засвідченням, а не сирим токеном")


# ── Фігура 5 [proj]: чотири способи сказати сервісу «хто це» ─────────────────
def fig_four_ways_identity():
    W, H = 1280, 588
    p = []
    cols = [(20, 270), (298, 250), (556, 470), (1034, 226)]
    headers = ["Спосіб сказати «хто»", "Що перетинає межу", "Чим ламається", "Вердикт"]
    for (cx, cw), htext in zip(cols, headers):
        p.append(fitbox(cx, 52, cw, 48, htext, size=12.5, bold=True,
                        fill=GREY_TINT, stroke=MUTED, sw=1.2))

    rows = [
        ("Переслати сирий\nклієнтський токен",
         "клієнтський JWT\n(як є)",
         "сервіс розбирає ЧУЖИЙ токен: тягне більше влади,\nніж треба для цього стрибка, і чіпляє кожен\nсервіс до формату токена",
         "✗ надлишок\nі зчеплення", RED_TINT, POS),
        ("Простий заголовок\nX-User-Id: bohdan",
         "рядок «bohdan»\n(без підпису)",
         "будь-хто, хто дотягнувся до сервісу напряму,\nставить свій заголовок — і стає ким завгодно",
         "✗ підробний", RED_TINT, POS),
        ("«Дійшло крізь шлюз»\n(довіра за місцем\nу мережі)",
         "нічого —\nсама адреса\nджерела",
         "заплутаний заступник: усе, що дотяглося напряму\n(SSRF, сусідній сервіс, збій мережі), сервіс\nобслуговує від чийого завгодно імені",
         "✗ заплутаний\nзаступник", RED_TINT, POS),
        ("Підписане внутрішнє\nзасвідчення",
         "свіжий внутр. токен:\nпідпис шлюзу ·\naud=devices · TTL≈10 с",
         "перевіряється підписом; вузьке (лише сервіс\nпристроїв); короткоживе — підробити, розтягнути\nчи переграти нізвідки",
         "✓ засвідчено", GREEN_TINT, FIELD),
    ]
    ry, rh, gap = 108, 100, 6
    for i, (c0, c1, c2, c3, tint, accent) in enumerate(rows):
        y = ry + i * (rh + gap)
        p.append(fitbox(cols[0][0], y, cols[0][1], rh, c0, size=12, fill=tint, stroke=accent, sw=1.6))
        p.append(fitbox(cols[1][0], y, cols[1][1], rh, c1, size=12, fill=BG, stroke=MUTED, sw=1.1))
        p.append(fitbox(cols[2][0], y, cols[2][1], rh, c2, size=12, fill=BG, stroke=MUTED, sw=1.1))
        p.append(fitbox(cols[3][0], y, cols[3][1], rh, c3, size=12, bold=True,
                        fill=tint, stroke=accent, sw=1.6, color=accent))

    p.append(mtext(640, 556,
                   ["Три верхні способи кажуть «хто» так, що сервіс отримує зайве або вірить непідписаному.",
                    "Лише засвідчення підписом шлюзу перетинає межу так, що його не підробити й не розтягнути."],
                   size=11.5, color=INK))
    render(os.path.join(IMG, "four-ways-identity.svg"), W, H, *p,
           title="Чотири способи сказати сервісу «хто це» — переживає лише один")


if __name__ == "__main__":
    fig_request_road()
    fig_two_gates_two_attacks()
    fig_hybrid_one_rule()
    fig_attestation_crossing()
    fig_four_ways_identity()
    print("OK: 5 SVG ->", IMG)
