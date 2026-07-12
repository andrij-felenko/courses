# -*- coding: utf-8 -*-
"""Фігури до кроку «DH як приймач-замовник вебхуків»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

RED_FILL = "#fdecea"
GREEN_FILL = "#eafaf0"
BLUE_FILL = "#e6eefb"
AMBER_FILL = "#fff4e0"
AMBER = "#c77800"
GRAY_FILL = "#f0f0f2"


def fig_consumer_flip():
    """Обіцянка провайдера дзеркально обертається на обов'язок приймача."""
    W, H = 1260, 640
    frags = []

    LX, RX, BW = 350, 910, 380
    LEDGE = LX + BW / 2      # правий край лівих коробок
    REDGE = RX - BW / 2      # лівий край правих коробок

    # заголовки колонок
    frags.append(text(LX, 92, "ОБІЦЯНКА ПРОВАЙДЕРА", size=16, bold=True, color=NEG))
    frags.append(text(RX, 92, "ОБОВ'ЯЗОК ПРИЙМАЧА", size=16, bold=True, color=FIELD))

    rows = [
        (170, "Підписує тіло секретом", "Перевір підпис\nна кожному POST"),
        (305, "Доставляє «щонайменше раз»,\nповторює при сумніві", "Стерпи дублі й повтори\n(дедуп за id)"),
        (440, "Кладе унікальний id події", "Упізнай той самий\nфакт удруге"),
    ]
    for y, ltxt, rtxt in rows:
        lb, _, _ = textbox(LX, y, ltxt, size=13.5, bold=True, fill=BLUE_FILL,
                           stroke=NEG, sw=1.8, color=INK, min_w=BW)
        rb, _, _ = textbox(RX, y, rtxt, size=13.5, bold=True, fill=GREEN_FILL,
                           stroke=FIELD, sw=1.8, color=INK, min_w=BW)
        frags.append(lb)
        frags.append(rb)
        frags.append(arrow(LEDGE + 8, y, REDGE - 8, y, color=INK, sw=2.2))

    # нижній банер: публічні двері / недовірений ввід
    banner = ("Приймальні двері — ПУБЛІЧНІ: стукає чужий сервер, не залогінений користувач.\n"
              "Тіло вебхука — недовірений ввід, доки підпис не доведе протилежне.")
    bb, _, _ = textbox(W / 2, 560, banner, size=14, bold=True, fill=AMBER_FILL,
                       stroke=AMBER, sw=2, color=AMBER, min_w=1020)
    frags.append(bb)

    render(os.path.join(IMG, "consumer-flip.svg"), W, H, *frags,
           title="Споживач обертає кожне правило провайдера на обов'язок")


def fig_fast_ack():
    """Інлайн-обробка провокує шторм повторів; тонкий приймач ріже коло."""
    W, H = 1280, 560
    frags = []

    X0 = 300          # t = 0
    PXS = 96          # px на секунду
    def tx(s): return X0 + s * PXS
    THR = tx(5)       # поріг таймауту провайдера

    # спільний поріг таймауту — вертикаль крізь обидві доріжки
    frags.append(line(THR, 96, THR, 452, color=MUTED, sw=1.4, dash="6,6"))
    frags.append(text(THR, 86, "провайдер чекає ≤ 5 с, тоді вважає невдачею й повторює",
                      size=12.5, bold=True, color=MUTED))

    # ── ВЕРХНЯ доріжка: інлайн-обробка ──
    frags.append(text(140, 150, "ОБРОБКА", size=14, bold=True, color=POS, anchor="start"))
    frags.append(text(140, 170, "ІНЛАЙН", size=14, bold=True, color=POS, anchor="start"))
    # POST-мітка
    frags.append(arrow(tx(0), 118, tx(0), 150, color=INK, sw=1.8))
    frags.append(text(tx(0), 112, "POST", size=12, bold=True, color=INK))
    # смуга важкої роботи (0..8 с)
    frags.append(rect(tx(0), 158, tx(8) - tx(0), 30, fill=RED_FILL, stroke=POS, sw=1.8))
    frags.append(text(tx(0) + 14, 178, "база + твін + пуш — 8 с", size=12.5, bold=True,
                      color=POS, anchor="start"))
    # повтор після таймауту
    frags.append(arrow(THR, 196, tx(5.4), 224, color=POS, sw=1.9))
    frags.append(rect(tx(5.4), 230, tx(8) - tx(5.4) + 40, 28, fill=RED_FILL, stroke=POS, sw=1.6))
    frags.append(text(tx(5.4) + 12, 249, "повтор → та сама робота ВДРУГЕ", size=12,
                      bold=True, color=POS, anchor="start"))
    rb, _, _ = textbox(1120, 178, "подвійна робота,\nшторм повторів", size=12.5, bold=True,
                       fill=RED_FILL, stroke=POS, sw=1.9, color=POS, min_w=250)
    frags.append(rb)

    # роздільник доріжок
    frags.append(line(90, 300, W - 90, 300, color=MUTED, sw=1, dash="4,6"))

    # ── НИЖНЯ доріжка: тонкий приймач ──
    frags.append(text(140, 372, "ТОНКИЙ", size=14, bold=True, color=FIELD, anchor="start"))
    frags.append(text(140, 392, "ПРИЙМАЧ", size=14, bold=True, color=FIELD, anchor="start"))
    frags.append(arrow(tx(0), 340, tx(0), 372, color=INK, sw=1.8))
    frags.append(text(tx(0), 334, "POST", size=12, bold=True, color=INK))
    # крихітна смуга ~50 мс
    frags.append(rect(tx(0), 380, 26, 28, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    frags.append(text(tx(0) + 40, 399, "перевір + у чергу ≈ 50 мс", size=12.5, bold=True,
                      color=FIELD, anchor="start"))
    frags.append(text(tx(0) + 40, 420, "→ ACK 200 задовго до порога", size=12, color=FIELD, anchor="start"))
    # окрема асинхронна робота
    frags.append(rect(tx(3), 432, tx(6) - tx(3), 26, fill=BLUE_FILL, stroke=NEG, sw=1.5))
    frags.append(text(tx(3) + 12, 450, "обробка — у черзі, свій темп", size=12, color=INK, anchor="start"))

    frags.append(text(W / 2, 520,
        "Поки робота сидить усередині відповіді, повільна база штовхає провайдера на повтор, "
        "а повтор — на нову важку роботу. Швидкий ACK ріже це коло.",
        size=13, color=MUTED))

    render(os.path.join(IMG, "fast-ack.svg"), W, H, *frags,
           title="Підтверди швидко: інлайн-шторм проти тонкого приймача")


def fig_reconcile():
    """Пуш може зникнути й лишити твін у брехні; звірка стягує його до правди."""
    W, H = 1260, 620
    frags = []

    # ── ВЕРХ: пуш загубився ──
    frags.append(text(W / 2, 70, "ПУШ — найкращих зусиль: може зникнути безслідно",
                      size=16, bold=True, color=POS))

    lk, _, _ = textbox(170, 150, "замок\n«відчинено»", size=13, bold=True,
                       fill=FILL, stroke=INK, sw=1.6, color=INK, min_w=210)
    ep, _, _ = textbox(500, 150, "ендпоінт DH\nдеплой — мертвий порт", size=13, bold=True,
                       fill=RED_FILL, stroke=POS, sw=1.9, color=POS, min_w=260)
    frags += [lk, ep]
    frags.append(arrow(170 + 105 + 6, 150, 500 - 130 - 6, 150, color=INK, sw=1.9))
    # хрест — втрачено
    frags.append(text(700, 138, "✗", size=30, bold=True, color=POS))
    frags.append(text(700, 172, "подія втрачена", size=12.5, bold=True, color=POS))

    # твін проти реальності
    tw, _, _ = textbox(1030, 120, "твін: 🔒 зачинено\n(стара правда)", size=13, bold=True,
                       fill=GRAY_FILL, stroke=INK, sw=1.6, color=INK, min_w=250)
    rl, _, _ = textbox(1030, 200, "дім: 🔓 відчинено", size=13, bold=True,
                       fill=RED_FILL, stroke=POS, sw=1.9, color=POS, min_w=250)
    frags += [tw, rl]
    frags.append(text(1030, 258, "≠  застосунок бреше", size=13.5, bold=True, color=POS))

    # ── роздільник ──
    frags.append(line(70, 320, W - 70, 320, color=MUTED, sw=1.3, dash="7,7"))

    # ── НИЗ: звірка ловить ──
    frags.append(text(W / 2, 368, "ЗВІРКА — періодичний pull ловить те, що пуш пропустив",
                      size=16, bold=True, color=FIELD))

    rc, _, _ = textbox(180, 460, "звірка DH\nраз на N хв", size=13, bold=True,
                       fill=GREEN_FILL, stroke=FIELD, sw=1.9, color=FIELD, min_w=220)
    api, _, _ = textbox(520, 460, "API партнера", size=13, bold=True,
                        fill=FILL, stroke=INK, sw=1.6, color=INK, min_w=220)
    cmp, _, _ = textbox(830, 460, "твін = зачинено\nAPI = відчинено\n≠", size=12.5, bold=True,
                        fill=AMBER_FILL, stroke=AMBER, sw=1.9, color=AMBER, min_w=230)
    fix, _, _ = textbox(1110, 460, "виправити твін → 🔓\nправда відновлена", size=12.5, bold=True,
                        fill=GREEN_FILL, stroke=FIELD, sw=2, color=FIELD, min_w=240)
    frags += [rc, api, cmp, fix]

    frags.append(arrow(180 + 110 + 6, 448, 520 - 110 - 6, 448, color=FIELD, sw=1.9))
    frags.append(text((290 + 410) / 2, 438, "стан замка?", size=11.5, color=FIELD))
    frags.append(arrow(520 + 110 + 6, 472, 830 - 115 - 6, 472, color=FIELD, sw=1.9))
    frags.append(text((630 + 715) / 2, 462, "«відчинено»", size=11.5, color=FIELD))
    frags.append(arrow(830 + 115 + 6, 460, 1110 - 120 - 6, 460, color=FIELD, sw=1.9))

    frags.append(text(W / 2, 585,
        "Один пуш може зникнути, і твін тихо розійдеться з реальністю; "
        "періодична звірка порівнює твін із джерелом і стягує їх назад.",
        size=13, color=MUTED))

    render(os.path.join(IMG, "reconcile.svg"), W, H, *frags,
           title="Пуш — підказка, звірка — правда")


def fig_pipeline():
    """Зібраний вузол: тонкий роут у транзакції → черга → робітник → твін+пуш; poison → мертва черга."""
    W, H = 1320, 620
    frags = []

    # ── тонкий роут в одній транзакції ──
    # дашкова рамка транзакції (малюємо ПЕРШОЮ, щоб сабокси лягли зверху)
    frags.append(rect(210, 72, 452, 182, fill="#fbfdff", stroke=NEG, sw=1.6, rx=10))
    frags.append(line(210, 72, 662, 72, color=NEG, sw=1.6, dash="7,6"))
    frags.append(text(436, 62, "ОДНА ТРАНЗАКЦІЯ — обидва записи або жоден", size=13.5,
                      bold=True, color=NEG))

    ib, _, _ = textbox(436, 122, "inbox\nINSERT … ON CONFLICT DO NOTHING", size=13,
                       bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.8, color=INK, min_w=400)
    jb, _, _ = textbox(436, 206, "jobs (черга)\nдодати, лише якщо id новий", size=13,
                       bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.8, color=INK, min_w=400)
    frags += [ib, jb]

    # POST → транзакція
    frags.append(text(120, 150, "POST", size=13, bold=True, color=INK))
    frags.append(text(120, 170, "підписаний", size=11.5, color=MUTED))
    frags.append(arrow(150, 160, 208, 160, color=INK, sw=1.9))

    # транзакція → ACK
    ack, _, _ = textbox(890, 122, "ACK 200\n≈ десятки мс", size=13, bold=True,
                        fill=GREEN_FILL, stroke=FIELD, sw=1.9, color=FIELD, min_w=210)
    frags.append(ack)
    frags.append(arrow(664, 122, 782, 122, color=INK, sw=1.9))

    # jobs → робітник
    wk, _, _ = textbox(436, 362, "Робітник\nSELECT … FOR UPDATE SKIP LOCKED", size=13,
                       bold=True, fill=FILL, stroke=INK, sw=1.8, color=INK, min_w=400)
    frags.append(wk)
    frags.append(arrow(436, 232, 436, 330, color=INK, sw=1.9))
    frags.append(text(452, 288, "тягне з черги у своєму темпі", size=11.5, color=MUTED, anchor="start"))

    # робітник → твін, робітник → пуш
    tw, _, _ = textbox(900, 330, "твін\nupsert WHERE новіший seq", size=13, bold=True,
                       fill=GREEN_FILL, stroke=FIELD, sw=1.9, color=INK, min_w=320)
    nt, _, _ = textbox(900, 430, "сповіщення родині\nлише як твін ЗМІНИВСЯ", size=13, bold=True,
                       fill=BLUE_FILL, stroke=NEG, sw=1.8, color=INK, min_w=320)
    frags += [tw, nt]
    frags.append(arrow(638, 350, 738, 332, color=INK, sw=1.9))
    frags.append(arrow(638, 376, 738, 424, color=INK, sw=1.9))

    # робітник → мертва черга (poison)
    dl, _, _ = textbox(436, 524, "мертва черга (dead-letter)\nposion-подія: N спроб — і сюди", size=13,
                       bold=True, fill=AMBER_FILL, stroke=AMBER, sw=1.9, color=AMBER, min_w=400)
    frags.append(dl)
    frags.append(arrow(436, 394, 436, 490, color=AMBER, sw=1.9))
    frags.append(text(452, 448, "N-та невдача — геть із черги", size=11.5, color=AMBER, anchor="start"))

    render(os.path.join(IMG, "pipeline.svg"), W, H, *frags,
           title="Зібраний приймач: роут у транзакції → черга → робітник → твін і пуш")


def fig_atomic():
    """Два окремі записи лишають діру (позначено-бачене, але не оброблено); одна транзакція її закриває."""
    W, H = 1340, 620
    frags = []

    # ── ВЕРХ: два окремі кроки — небезпечно ──
    frags.append(text(W / 2, 66, "ДВА ОКРЕМІ ЗАПИСИ — між ними може впасти процес", size=16,
                      bold=True, color=POS))

    b1, _, _ = textbox(180, 152, "1. inbox ✓\nпозначив «бачене»", size=12.5, bold=True,
                       fill=GREEN_FILL, stroke=FIELD, sw=1.8, color=INK, min_w=210)
    b2, _, _ = textbox(455, 152, "CRASH\nдо запису в чергу", size=12.5, bold=True,
                       fill=RED_FILL, stroke=POS, sw=2, color=POS, min_w=210)
    b3, _, _ = textbox(735, 152, "2. jobs ✗\nзадачу не створено", size=12.5, bold=True,
                       fill=RED_FILL, stroke=POS, sw=1.8, color=POS, min_w=210)
    b4, _, _ = textbox(1035, 152, "повтор → inbox\nCONFLICT → пропуск", size=12.5, bold=True,
                       fill=GRAY_FILL, stroke=INK, sw=1.6, color=INK, min_w=220)
    frags += [b1, b2, b3, b4]
    frags.append(arrow(180 + 105 + 6, 152, 455 - 105 - 6, 152, color=INK, sw=1.9))
    frags.append(arrow(455 + 105 + 6, 152, 735 - 105 - 6, 152, color=INK, sw=1.9))
    frags.append(arrow(735 + 105 + 6, 152, 1035 - 110 - 6, 152, color=INK, sw=1.9))

    ban1, _, _ = textbox(W / 2, 240, "подія позначена «бачена», але НІКОЛИ не оброблена — "
                         "загублена назавжди, дедуп тепер її ховає", size=13.5, bold=True,
                         fill=RED_FILL, stroke=POS, sw=2, color=POS, min_w=980)
    frags.append(ban1)

    # ── роздільник ──
    frags.append(line(70, 306, W - 70, 306, color=MUTED, sw=1.3, dash="7,7"))

    # ── НИЗ: одна транзакція — правильно ──
    frags.append(text(W / 2, 352, "ОДНА ТРАНЗАКЦІЯ — обидва записи народжуються разом", size=16,
                      bold=True, color=FIELD))

    tx, _, _ = textbox(240, 452, "BEGIN\ninbox + jobs\nCOMMIT", size=13.5, bold=True,
                       fill=GREEN_FILL, stroke=FIELD, sw=2, color=FIELD, min_w=250)
    frags.append(tx)
    o1, _, _ = textbox(760, 420, "крах ДО COMMIT →\nобидва відкотились →\nповтор робить обидва",
                       size=12.5, bold=True, fill=FILL, stroke=INK, sw=1.7, color=INK, min_w=380)
    o2, _, _ = textbox(760, 512, "крах ПІСЛЯ COMMIT →\nобидва є, ACK згублено →\nповтор: CONFLICT, без дублю",
                       size=12.5, bold=True, fill=FILL, stroke=INK, sw=1.7, color=INK, min_w=380)
    frags += [o1, o2]
    frags.append(arrow(240 + 125 + 6, 442, 760 - 190 - 6, 420, color=FIELD, sw=1.9))
    frags.append(arrow(240 + 125 + 6, 462, 760 - 190 - 6, 512, color=FIELD, sw=1.9))

    render(os.path.join(IMG, "atomic-inbox.svg"), W, H, *frags,
           title="Позначка «бачене» і задача в черзі — атомарно, або ніяк")


def fig_two_roads():
    """Дві дороги з наївного вебхука 2007-го: відкритий стандарт (стрічки) проти вендорського діалекту (інтеграції)."""
    W, H = 1320, 700
    frags = []

    root, _, _ = textbox(660, 112, "2007 · Джефф Ліндсей\n«просто зроби POST\nна задану тобою адресу»",
                         size=14, bold=True, fill=AMBER_FILL, stroke=AMBER, sw=2, color=AMBER, min_w=340)
    frags.append(root)

    # дороги розходяться
    frags.append(arrow(560, 150, 360, 272, color=INK, sw=2))
    frags.append(arrow(760, 150, 972, 272, color=INK, sw=2))

    # ── ЛІВА: відкритий стандарт ──
    l1, _, _ = textbox(360, 312, "ВІДКРИТИЙ СТАНДАРТ\nPubSubHubbub · 2009 · Google\nФітцпатрик і Слаткін · хаб + підпис",
                       size=13, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.9, color=INK, min_w=380)
    frags.append(l1)
    frags.append(arrow(360, 352, 360, 410, color=FIELD, sw=1.9))
    l2, _, _ = textbox(360, 452, "WebSub · Рекомендація W3C\n23.01.2018 · Женесту, Парекі\nвидавці · підписники · хаби",
                       size=13, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.9, color=INK, min_w=380)
    frags.append(l2)
    frags.append(arrow(360, 492, 360, 548, color=FIELD, sw=1.9))
    l3, _, _ = textbox(360, 590, "ПЕРЕМІГ У СТРІЧКАХ\nYouTube · WordPress · Google Alerts",
                       size=13, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2, color=FIELD, min_w=380)
    frags.append(l3)

    # ── ПРАВА: вендорський діалект ──
    r1, _, _ = textbox(972, 312, "КОЖЕН ВЕНДОР — СВІЙ ДІАЛЕКТ\nGitHub · Twitter (2018) · Stripe\nсвій URL · свій підпис · свій формат",
                       size=13, bold=True, fill=BLUE_FILL, stroke=NEG, sw=1.9, color=INK, min_w=400)
    frags.append(r1)
    frags.append(arrow(972, 352, 972, 452, color=NEG, sw=1.9))
    r2, _, _ = textbox(972, 494, "ПЕРЕМІГ В ІНТЕГРАЦІЯХ застосунків\nспільного хаба й формату немає",
                       size=13, bold=True, fill=BLUE_FILL, stroke=NEG, sw=2, color=NEG, min_w=400)
    frags.append(r2)

    banner = ("У світі застосунків переміг НЕ єдиний стандарт, а вендорський діалект — "
              "тому споживач учить схему підпису кожного провайдера окремо.")
    bb, _, _ = textbox(660, 662, banner, size=13.5, bold=True, fill=AMBER_FILL,
                       stroke=AMBER, sw=2, color=AMBER, min_w=1180)
    frags.append(bb)

    render(os.path.join(IMG, "two-roads.svg"), W, H, *frags,
           title="Дві дороги з наївного вебхука 2007-го")


def fig_security_skin():
    """Наївний POST 2007-го обростає шкірою: підпис, час, id, звірка — по шару за кожен урок."""
    W, H = 1340, 660
    frags = []

    r0, _, _ = textbox(680, 108, "2007 · ГОЛИЙ POST — «довірся мені»",
                       size=15, bold=True, fill=RED_FILL, stroke=POS, sw=2, color=POS, min_w=520)
    frags.append(r0)

    # вісь накопичення
    frags.append(line(180, 150, 180, 560, color=MUTED, sw=1.6, dash="6,7"))
    frags.append(text(180, 588, "шар за шаром", size=12, color=MUTED))

    rows = [
        (222, "ПІДПИС · HMAC над точними байтами", "двері публічні → «ХТО ти?»"),
        (320, "ПОЗНАЧКА ЧАСУ + вікно ≈ 5 хв", "захоплений POST → «це не ПОВТОР?»"),
        (418, "id ПОДІЇ + дедуп (вхідна скринька)", "«щонайменше раз» → «вже це БАЧИВ?»"),
        (516, "ЗВІРКА · список подій через API", "пуш зникає тихо → «а ПРИЙШЛО?»"),
    ]
    for y, mech, lesson in rows:
        mb, _, _ = textbox(480, y, mech, size=13, bold=True, fill=GREEN_FILL,
                           stroke=FIELD, sw=1.9, color=INK, min_w=440)
        lb, _, _ = textbox(1010, y, lesson, size=13, bold=True, fill=AMBER_FILL,
                           stroke=AMBER, sw=1.8, color=AMBER, min_w=360)
        frags.append(mb)
        frags.append(lb)
        frags.append(arrow(180, y, 254, y, color=FIELD, sw=1.8))    # вісь → механізм
        frags.append(arrow(706, y, 824, y, color=INK, sw=1.7))      # механізм → урок

    bottom = ("Сучасний зразок — Stripe:  Stripe-Signature: t=…, v1 = HMAC-SHA256(секрет, «t.тіло»)  "
              "— усі шари в одному заголовку.")
    frags.append(text(680, 632, bottom, size=13, bold=True, color=INK))

    render(os.path.join(IMG, "security-skin.svg"), W, H, *frags,
           title="Наївний POST обростає шкірою — по шару за кожен урок")


if __name__ == "__main__":
    fig_consumer_flip()
    fig_fast_ack()
    fig_reconcile()
    fig_pipeline()
    fig_atomic()
    fig_two_roads()
    fig_security_skin()
    print("OK: consumer-flip, fast-ack, reconcile, pipeline, atomic-inbox, two-roads, security-skin")
