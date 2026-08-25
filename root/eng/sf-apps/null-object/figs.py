# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def dashed_circle(cx, cy, r, fill, stroke, sw=2, dash="6,5"):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"/>'
            % (cx, cy, r, fill, stroke, sw, dash))


# ── Дірка проти значення: перевіряти-перед-кожним  vs  кликати наосліп ────────
def fig_hole_vs_value():
    W, H = 1140, 610
    frags = []

    frags.append(text(W / 2, 40, "Дірка проти значення", size=18, bold=True, color=INK))
    frags.append(text(W / 2, 63, "як клієнт поводиться з тим, кого може не бути",
                      size=12.5, color=MUTED))

    # вертикальний роздільник
    frags.append(line(W / 2, 90, W / 2, 528, color="#d0d5db", sw=1.1))

    # ── Ліва колонка: null — діра ────────────────────────────────────────────
    lx = W * 0.265
    frags.append(text(lx, 112, "null — діра", size=15, bold=True, color=POS))

    cb, cbw, cbh = textbox(lx, 162, ["OrderService  (клієнт)"],
                           size=12.5, bold=True, fill="#eaf0fd", stroke=NEG,
                           sw=1.6, min_w=270)
    frags.append(cb)

    guard, gw, gh = textbox(lx, 300,
                            ["if logger ≠ null:  logger.write(a)",
                             "if logger ≠ null:  logger.write(b)",
                             "if logger ≠ null:  logger.write(c)"],
                            size=12, bold=False, fill="#fdecea", stroke=POS,
                            sw=1.5, min_w=360)
    frags.append(guard)
    frags.append(arrow(lx, 300 + gh / 2 + 6, lx, 452, color=POS, sw=1.6))

    frags.append(dashed_circle(lx, 490, 34, "#ffffff", POS, sw=2))
    frags.append(text(lx, 495, "null", size=13, bold=True, color=POS))
    frags.append(text(lx + 62, 490, "✗ не відповідає", size=12, color=MUTED, anchor="start"))
    frags.append(text(lx, 236, "мусить спершу спитати «а ти є?»", size=11.5, color=MUTED))

    # ── Права колонка: порожній об'єкт — значення ────────────────────────────
    rx = W * 0.735
    frags.append(text(rx, 112, "порожній об'єкт — значення", size=15, bold=True, color=FIELD))

    cb2, cbw2, cbh2 = textbox(rx, 162, ["OrderService  (клієнт)"],
                              size=12.5, bold=True, fill="#eaf0fd", stroke=NEG,
                              sw=1.6, min_w=270)
    frags.append(cb2)

    call, cw2, ch2 = textbox(rx, 300,
                             ["logger.write(a)",
                              "logger.write(b)",
                              "logger.write(c)"],
                             size=12, bold=False, fill="#e8f6ee", stroke=FIELD,
                             sw=1.5, min_w=360)
    frags.append(call)
    frags.append(arrow(rx, 300 + ch2 / 2 + 6, rx, 452, color=FIELD, sw=1.6))

    nb, nbw, nbh = textbox(rx, 490, ["NullLogger", "write(): нічого"],
                           size=12.5, bold=False, fill="#e8f6ee", stroke=FIELD,
                           sw=1.8, min_w=230)
    frags.append(nb)
    frags.append(text(rx + nbw / 2 + 12, 490, "✓ відповідає завжди",
                      size=12, color=MUTED, anchor="start"))
    frags.append(text(rx, 236, "кличе наосліп — воно завжди спрацює", size=11.5, color=MUTED))

    # ── Нижня плашка ─────────────────────────────────────────────────────────
    frags.append(line(40, 554, W - 40, 554, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 582,
                      "перевірки зникли не тому, що ми їх сховали — а тому, що перевіряти більше нічого",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'hole-vs-value.svg'), W, H, *frags)


# ── Кістяк: порожній — просто ще одна реалізація інтерфейсу ───────────────────
def fig_null_object_skeleton():
    W, H = 1060, 560
    frags = []

    frags.append(text(W / 2, 40, "Порожній — ще одна реалізація, а не виняток",
                      size=18, bold=True, color=INK))
    frags.append(text(W / 2, 63, "клієнт бачить лише інтерфейс і не розрізняє реалізацій",
                      size=12.5, color=MUTED))

    # ── Інтерфейс (центр угорі) ──────────────────────────────────────────────
    iface_cx = W * 0.60
    iface_cy = 150
    iface, iw, ih = textbox(iface_cx, iface_cy,
                            ["«interface» Logger", "write(msg)"],
                            size=13, bold=True, fill="#e8f6ee", stroke=FIELD,
                            sw=1.8, min_w=270)
    frags.append(iface)

    # ── Дві реалізації (нижче, у ряд) ────────────────────────────────────────
    impl_cy = 380
    file_cx = W * 0.44
    null_cx = W * 0.78
    fb, fbw, fbh = textbox(file_cx, impl_cy, ["FileLogger", "пише рядок у файл"],
                           size=12.5, bold=False, fill=FILL, stroke=LINE,
                           sw=1.4, min_w=240)
    nb, nbw, nbh = textbox(null_cx, impl_cy, ["NullLogger", "нічого не робить"],
                           size=12.5, bold=False, fill=FILL, stroke=LINE,
                           sw=1.4, min_w=240)
    frags.append(fb)
    frags.append(nb)
    # стрілки-узагальнення від кожної реалізації вгору до інтерфейсу
    frags.append(arrow(file_cx, impl_cy - fbh / 2 - 4, iface_cx - 40, iface_cy + ih / 2 + 2,
                       color=FIELD, sw=1.5))
    frags.append(arrow(null_cx, impl_cy - nbh / 2 - 4, iface_cx + 40, iface_cy + ih / 2 + 2,
                       color=FIELD, sw=1.5))
    frags.append(text((file_cx + null_cx) / 2, impl_cy - 92,
                      "обидві однаково виконують інтерфейс", size=11.5, color=MUTED))

    # ── Клієнт (ліворуч) ─────────────────────────────────────────────────────
    cli_cx = W * 0.155
    cli_cy = 250
    cb, cbw, cbh = textbox(cli_cx, cli_cy,
                           ["OrderService", "logger: Logger", "logger.write(…)"],
                           size=12, bold=False, fill="#eaf0fd", stroke=NEG,
                           sw=1.6, min_w=210)
    frags.append(cb)
    frags.append(line(cli_cx + cbw / 2, cli_cy - 8, iface_cx - iw / 2 - 6, iface_cy,
                      color=NEG, sw=1.5, dash="5,5"))
    frags.append(text(cli_cx, cli_cy + cbh / 2 + 22, "кличе наосліп,", size=11.5, color=INK))
    frags.append(text(cli_cx, cli_cy + cbh / 2 + 40, "не розгалужуючись", size=11.5, color=INK))

    # ── Нижня плашка ─────────────────────────────────────────────────────────
    frags.append(line(40, H - 60, W - 40, H - 60, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 32,
                      "підставити NullLogger замість FileLogger — змінити поведінку, не чіпаючи клієнта",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'null-object-skeleton.svg'), W, H, *frags)


# ── Три способи зустріти відсутність ─────────────────────────────────────────
def fig_three_ways_absence():
    W, H = 1180, 560
    frags = []

    frags.append(text(W / 2, 40, "Три способи зустріти відсутність", size=18, bold=True, color=INK))
    frags.append(text(W / 2, 63, "«значення може бути відсутнє» — і що з цим робити",
                      size=12.5, color=MUTED))

    cols = [
        (W * 0.185, POS, "#fdecea",
         "null + перевірка", ["значення АБО null", "if x ≠ null: …"],
         [("✗", POS, "можна забути перевірку"), ("", MUTED, "→ падіння в рантаймі")]),
        (W * 0.5, FIELD, "#e8f6ee",
         "порожній об'єкт", ["об'єкт завжди є", "кличеш наосліп"],
         [("✓", FIELD, "безпечно, без розгалужень"),
          ("⚠", "#b8860b", "може тихо сховати помилку")]),
        (W * 0.815, FIELD, "#e8f6ee",
         "Optional / сума-тип", ["тип: значення АБО нічого", "compiler вимагає розбір"],
         [("✓", FIELD, "змушує обробити обидва"), ("", MUTED, "забути неможливо")]),
    ]

    for cx, accent, fill, title, body, verdicts in cols:
        frags.append(text(cx, 118, title, size=14.5, bold=True, color=accent))
        bb, bw, bh = textbox(cx, 200, body, size=12.5, bold=False,
                             fill=fill, stroke=accent, sw=1.7, min_w=300)
        frags.append(bb)
        vy = 300
        for mark, mcol, txt in verdicts:
            if mark:
                frags.append(text(cx - 130, vy, mark, size=14, bold=True,
                                  color=mcol, anchor="start"))
            frags.append(text(cx - 108, vy, txt, size=12, color=INK, anchor="start"))
            vy += 26

    # роздільники між колонками
    frags.append(line(W * 0.34, 100, W * 0.34, 360, color="#e2e5e9", sw=1.0))
    frags.append(line(W * 0.66, 100, W * 0.66, 360, color="#e2e5e9", sw=1.0))

    # ── Нижня плашка ─────────────────────────────────────────────────────────
    frags.append(line(40, H - 74, W - 40, H - 74, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 46,
                      "порожній об'єкт прибирає розгалуження; Optional його вимагає — обирай за важливістю відсутності",
                      size=13, bold=True, color=INK))
    frags.append(text(W / 2, H - 22,
                      "нейтральна поведінка чесна → порожній об'єкт;  відсутність щоразу важлива → Optional",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'three-ways-absence.svg'), W, H, *frags)


# ── Нитка історії: від винаходу null до патерна, що вчить без нього ───────────
def fig_null_birth_timeline():
    W, H = 1140, 812
    frags = []

    frags.append(text(W / 2, 44, "Нитка: від винаходу null до патерна, що вчить без нього",
                      size=18, bold=True, color=INK))
    frags.append(text(W / 2, 68, "одна лінія коду 1965-го — і десятиліття, витрачені на те, щоб її обійти",
                      size=12.5, color=MUTED))

    spine_x = 176
    top_y = 138
    gap = 96

    # (рік, акцент, заливка, рядки опису)
    rows = [
        ("1965", POS, "#fdecea",
         ["Тоні Гоар вбудовує null-посилання в систему типів для ALGOL W",
          "(мову запропонував із Ніклаусом Віртом) — «бо це було до смішного легко»"]),
        ("1988", MUTED, FILL,
         ["Роберт Седжвік описує вартового-«z-node» в «Algorithms»",
          "процедурний предок: об'єкт-заглушка замість спецперевірок у структурах"]),
        ("1995", NEG, "#eaf0fd",
         ["Брюс Андерсон піднімає ім'я «Null Object» у списку розсилки патернів UIUC",
          "ідея визріває спільно, ще до жодної статті"]),
        ("1996", FIELD, "#e8f6ee",
         ["Боббі Вулф читає «The Null Object Pattern» на PLoP '96 (Аллертон-Парк, Іллінойс)",
          "патерн уперше оформлено як патерн; наскрізний приклад — NoController зі Smalltalk"]),
        ("1998", FIELD, "#eaf7ef",
         ["Патерн виходить друком у «Pattern Languages of Program Design 3» (Addison-Wesley)",
          "усталена, багато цитована публікація"]),
        ("2002", NEG, "#eaf0fd",
         ["Мартін Фаулер узагальнює його до «особливого випадку» (Special Case) у PoEAA",
          "порожній об'єкт виявляється лише одним із багатьох особливих станів"]),
        ("2009", POS, "#fdecea",
         ["Гоар привселюдно зве null своєю «помилкою на мільярд доларів» (QCon London)",
          "коло замкнулося: сам винахідник діри публічно за неї перепрошує"]),
    ]

    last_y = top_y + (len(rows) - 1) * gap
    # хребет
    frags.append(line(spine_x, top_y, spine_x, last_y, color="#cbd0d6", sw=2.2))

    for i, (year, accent, fill, lines) in enumerate(rows):
        y = top_y + i * gap
        # рік ліворуч від хребта
        frags.append(text(spine_x - 34, y + 5, year, size=16, bold=True,
                          color=accent, anchor="end"))
        # опис праворуч — у фіксовану рамку, щоб лівий край рівний і шрифт великий
        frags.append(fitbox(spine_x + 44, y - 34, W - (spine_x + 44) - 44, 68,
                            lines, size=13.5, fill=fill, stroke=accent, sw=1.6))
        # вузол на хребті поверх усього
        frags.append(circle(spine_x, y, 9, fill=fill, stroke=accent, sw=2.6))

    # нижня плашка-підсумок
    frags.append(line(44, H - 58, W - 44, H - 58, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 30,
                      "один винайшов діру · спільнота патернів дала спосіб її обходити · винахідник за неї перепросив",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'null-birth-timeline.svg'), W, H, *frags)


# ── Рефакторинг: чотири копії нейтральної гілки згортаються в один клас ───────
def fig_refactor_collapse():
    W, H = 1220, 660
    frags = []

    frags.append(text(W / 2, 40, "Згортання: одна нейтральна гілка, скопійована чотири рази",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 63, "той самий else «вільний тариф» повторено в кожному методі",
                      size=12.5, color=MUTED))

    # ── ДО ───────────────────────────────────────────────────────────────────
    lx = W * 0.255
    frags.append(text(lx, 110, "ДО — 4 перевірки, гілка ×4", size=14.5, bold=True, color=POS))

    guarded, gw, gh = textbox(
        lx, 300,
        ["price   : sub≠null ? sub.price()      : 0",
         "storage : sub≠null ? sub.storageGb()  : 1",
         "seats   : sub≠null ? sub.seats()      : 1",
         "feature : sub≠null ? sub.includes(f)  : BASIC"],
        size=12, bold=False, fill="#fdecea", stroke=POS, sw=1.6, min_w=500)
    frags.append(guarded)
    frags.append(text(lx, 300 + gh / 2 + 26,
                      "нейтральна гілка (0, 1, 1, BASIC) скопійована чотири рази",
                      size=11.5, color=MUTED))

    # ── стрілка згортання ──────────────────────────────────────────────────────
    frags.append(text(W / 2, 268, "згортаємо", size=12.5, bold=True, color=INK))
    frags.append(arrow(lx + gw / 2 + 14, 300, W * 0.745 - 250, 300, color=INK, sw=1.8))
    frags.append(text(W / 2, 332, "гілку в клас", size=11.5, color=MUTED))

    # ── ПІСЛЯ ──────────────────────────────────────────────────────────────────
    rx = W * 0.745
    frags.append(text(rx, 110, "ПІСЛЯ — гілка в одному класі, 0 перевірок",
                      size=14.5, bold=True, color=FIELD))

    freeb, fw, fh = textbox(
        rx, 210,
        ["FreeSubscription  (порожній об'єкт)",
         "price()=0   storageGb()=1",
         "seats()=1   includes(f)=BASIC.has(f)"],
        size=12, bold=False, fill="#e8f6ee", stroke=FIELD, sw=1.7, min_w=420)
    frags.append(freeb)

    acc, aw, ah = textbox(
        rx, 400,
        ["price   : sub.price()",
         "storage : sub.storageGb()",
         "seats   : sub.seats()",
         "feature : sub.includes(f)"],
        size=12, bold=False, fill="#eaf0fd", stroke=NEG, sw=1.6, min_w=420)
    frags.append(acc)
    frags.append(arrow(rx, 210 + fh / 2 + 4, rx, 400 - ah / 2 - 4, color=FIELD, sw=1.5))
    frags.append(text(rx, 400 + ah / 2 + 24,
                      "жодного розгалуження — Account лише делегує", size=11.5, color=MUTED))

    # ── нижня плашка ───────────────────────────────────────────────────────────
    frags.append(line(40, H - 60, W - 40, H - 60, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 32,
                      "чотири копії однієї політики → одне джерело правди; новий метод не тягне нової перевірки",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'refactor-collapse.svg'), W, H, *frags)


# ── Не кожна відсутність — вільний тариф ─────────────────────────────────────
def fig_absence_fork():
    W, H = 1140, 590
    frags = []

    frags.append(text(W / 2, 40, "Не кожна відсутність — вільний тариф", size=17, bold=True, color=INK))
    frags.append(text(W / 2, 63, "перш ніж підставити порожній об'єкт, спитай: ця відсутність ДОЗВОЛЕНА?",
                      size=12.5, color=MUTED))

    top, tw, th = textbox(W / 2, 118, ["loadSubscription(userId)"],
                          size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.6, min_w=300)
    frags.append(top)

    dec, dw, dh = textbox(W / 2, 240, ["підписки немає — ЧОМУ?"],
                          size=13, bold=True, fill=FILL, stroke=INK, sw=1.8, min_w=320)
    frags.append(dec)
    frags.append(arrow(W / 2, 118 + th / 2 + 4, W / 2, 240 - dh / 2 - 4, color=INK, sw=1.6))

    # ── ліва гілка: дозволена ─────────────────────────────────────────────────
    lx = W * 0.255
    frags.append(arrow(W / 2 - dw / 2 - 4, 250, lx + 70, 384, color=FIELD, sw=1.6))
    frags.append(text((W / 2 + lx) / 2 - 28, 312, "дозволена", size=12, bold=True, color=FIELD))

    okb, okw, okh = textbox(lx, 420, ["FreeSubscription", "законна відсутність"],
                            size=12.5, bold=False, fill="#e8f6ee", stroke=FIELD, sw=1.8, min_w=300)
    frags.append(okb)
    frags.append(text(lx, 420 + okh / 2 + 24, "юзер справді на вільному тарифі",
                      size=11.5, color=MUTED))

    # ── права гілка: помилкова ────────────────────────────────────────────────
    rx = W * 0.745
    frags.append(arrow(W / 2 + dw / 2 + 4, 250, rx - 70, 384, color=POS, sw=1.6))
    frags.append(text((W / 2 + rx) / 2 + 28, 312, "помилкова", size=12, bold=True, color=POS))

    errb, ew, eh = textbox(rx, 420, ["throw / alert", "боронь глушити"],
                           size=12.5, bold=False, fill="#fdecea", stroke=POS, sw=1.8, min_w=300)
    frags.append(errb)
    frags.append(text(rx, 420 + eh / 2 + 24, "збій БД чи enterprise без плану — це БАГ",
                      size=11.5, color=MUTED))

    # ── нижня плашка ───────────────────────────────────────────────────────────
    frags.append(line(40, H - 56, W - 40, H - 56, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 28,
                      "порожній об'єкт легалізує лише ДОЗВОЛЕНУ відсутність — помилкову впіймай ДО підстановки",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'absence-fork.svg'), W, H, *frags)


# ── МАТЕМАТИЧНА НОТАТКА: нейтральний і поглинальний елемент ───────────────────

def _math_tok(cx, cy, s, accent=LINE, fill=FILL, w=58, h=44, tcolor=INK, dash=False, size=16):
    x, y = cx - w / 2, cy - h / 2
    d = ' stroke-dasharray="5,4"' if dash else ''
    r = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="9" fill="%s" '
         'stroke="%s" stroke-width="2"%s/>' % (x, y, w, h, fill, accent, d))
    return r + text(cx, cy + size * 0.35, s, size=size, bold=True, color=tcolor)


# ── Таблиця: та сама позначка — нейтральна чи поглинальна залежно від операції ─
def fig_neutral_absorbing_table():
    W, H = 1160, 650
    frags = []
    frags.append(text(W / 2, 42, "Нейтральний і поглинальний елемент операції",
                      size=18, bold=True, color=INK))
    frags.append(text(W / 2, 66, "e лишає операнд незмінним;  z стягує будь-що до себе",
                      size=12.5, color=MUTED))

    x_op, x_neu, x_abs = 80, 620, 940
    hy = 108
    frags.append(text(x_op, hy, "операція", size=13.5, bold=True, color=INK, anchor="start"))
    frags.append(text(x_neu, hy, "нейтральний  e", size=13.5, bold=True, color=FIELD))
    frags.append(text(x_abs, hy, "поглинальний  z", size=13.5, bold=True, color=POS))
    frags.append(line(70, hy + 13, W - 70, hy + 13, color="#c9ced4", sw=1.3))

    rows = [
        ("додавання   a + b",     "0",                     "—"),
        ("множення   a · b",      "1",                     "0"),
        ("конкатенація   a ⧺ b",  "\"\" — порожній рядок", "—"),
        ("І (AND)   a ∧ b",       "true",                  "false"),
        ("АБО (OR)   a ∨ b",      "false",                 "true"),
        ("композиція   f ∘ g",    "id — тотожність",       "—"),
        ("ланцюг ефектів",        "ε — нічого не роблю",   "—"),
    ]
    y = hy + 16
    rh = 50
    for op_s, neu, absb in rows:
        y += rh
        frags.append(text(x_op, y, op_s, size=12.5, color=INK, anchor="start"))
        frags.append(text(x_neu, y, neu, size=12.5, color=FIELD, bold=True))
        has = absb != "—"
        frags.append(text(x_abs, y, absb if has else "— (немає)", size=12.5,
                          color=(POS if has else MUTED), bold=has))
        frags.append(line(70, y + rh / 2 - 2, W - 70, y + rh / 2 - 2, color="#eef0f2", sw=1.0))

    cy = y + rh / 2 + 12
    frags.append(fitbox(70, cy, W - 140, 108,
                        ["⚠  Та сама позначка — різна роль, залежно від операції:",
                         "0 — нейтральний для + , але поглинальний для ×",
                         "false — нейтральний для ∨, поглинальний для ∧;   true — навпаки",
                         "коректність задає ПАРА (значення, операція), а не значення саме собою"],
                        size=13, fill="#fff8e1", stroke="#b8860b", sw=1.5))
    render(os.path.join(IMG, 'neutral-absorbing-table.svg'), W, H, *frags)


# ── Ланцюг: нейтральний зникає, поглинальний поглинає весь ланцюг ─────────────
def fig_chain_neutral_vs_absorbing():
    W, H = 1060, 560
    frags = []
    frags.append(text(W / 2, 44, "Підстановка в ланцюг: нейтральний зникає, поглинальний поглинає",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 68, "що бачить решта програми, коли на місце учасника стає порожній об'єкт",
                      size=12.5, color=MUTED))

    def op(x, y, s):
        return text(x, y + 6, s, size=17, color=MUTED, bold=True)

    # нейтральний рядок
    ly = 190
    frags.append(text(70, ly - 70, "нейтральний  e = ε", size=14, bold=True, color=FIELD, anchor="start"))
    frags.append(_math_tok(120, ly, "e₁"))
    frags.append(op(165, ly, "·"))
    frags.append(_math_tok(212, ly, "ε", accent=FIELD, fill="#e8f6ee", tcolor=FIELD, dash=True))
    frags.append(text(212, ly - 38, "порожній", size=10.5, color=FIELD))
    frags.append(op(257, ly, "·"))
    frags.append(_math_tok(304, ly, "e₂"))
    frags.append(op(372, ly, "="))
    frags.append(_math_tok(442, ly, "e₁"))
    frags.append(op(487, ly, "·"))
    frags.append(_math_tok(534, ly, "e₂"))
    frags.append(text(650, ly - 6, "слот розчинився —", size=13, color=INK, anchor="start"))
    frags.append(text(650, ly + 16, "ланцюг той самий", size=13, color=INK, anchor="start"))

    # поглинальний рядок
    ay = 400
    frags.append(text(70, ay - 70, "поглинальний  z", size=14, bold=True, color=POS, anchor="start"))
    frags.append(_math_tok(120, ay, "e₁"))
    frags.append(op(165, ay, "·"))
    frags.append(_math_tok(212, ay, "z", accent=POS, fill="#fdecea", tcolor=POS))
    frags.append(op(257, ay, "·"))
    frags.append(_math_tok(304, ay, "e₂"))
    frags.append(op(372, ay, "="))
    frags.append(_math_tok(442, ay, "z", accent=POS, fill="#fdecea", tcolor=POS))
    frags.append(text(650, ay - 6, "увесь ланцюг стягнуто до z —", size=13, color=INK, anchor="start"))
    frags.append(text(650, ay + 16, "e₁ і e₂ проковтнуто мовчки", size=13, color=INK, anchor="start"))

    frags.append(line(44, 300, W - 44, 300, color="#e2e5e9", sw=1.0))
    frags.append(line(44, H - 58, W - 44, H - 58, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 30,
                      "порожній об'єкт коректний ⟺ його внесок = нейтральний елемент саме цієї операції",
                      size=13, bold=True, color=INK))
    render(os.path.join(IMG, 'chain-neutral-vs-absorbing.svg'), W, H, *frags)


# ── Дуальність: порожній об'єкт (нейтральний) проти Option-Nothing (поглинальний)
def fig_neutral_vs_absorbing_duality():
    W, H = 1120, 600
    frags = []
    frags.append(text(W / 2, 44, "Дві ставки на відсутність: нейтральність проти поглинання",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 68, "порожній об'єкт хоче зникнути в обчисленні;  Option — спинити його на видноті",
                      size=12.5, color=MUTED))

    def step(cx, cy, s, accent=LINE, fill=FILL, tcolor=INK):
        return _math_tok(cx, cy, s, accent=accent, fill=fill, w=100, h=46, tcolor=tcolor, size=14)

    xs = [150, 340, 530, 720]

    # смуга 1: порожній об'єкт (нейтральний, зелений)
    y1 = 210
    frags.append(text(60, y1 - 80, "порожній об'єкт — ставка на нейтральність",
                      size=14, bold=True, color=FIELD, anchor="start"))
    labels = ["крок 1", "порожній", "крок 3", "крок 4"]
    for i, (x, lb) in enumerate(zip(xs, labels)):
        acc = FIELD if i == 1 else LINE
        fl = "#e8f6ee" if i == 1 else FILL
        frags.append(step(x, y1, lb, accent=acc, fill=fl, tcolor=(FIELD if i == 1 else INK)))
        if i < len(xs) - 1:
            frags.append(arrow(x + 52, y1, xs[i + 1] - 52, y1, color=FIELD, sw=1.8))
    frags.append(arrow(xs[3] + 52, y1, 910 - 52, y1, color=FIELD, sw=1.8))
    frags.append(step(910, y1, "результат", accent=FIELD, fill="#e8f6ee", tcolor=FIELD))
    frags.append(text(150, y1 + 54, "значення тече наскрізь — «порожній» лишає його незмінним",
                      size=11.5, color=MUTED, anchor="start"))
    frags.append(text(150, y1 + 74, "інертний і невидимий; якщо випадково поглинальний — тихо ламає",
                      size=11.5, color=POS, anchor="start"))

    # смуга 2: Option / Maybe (поглинальний, червоний)
    y2 = 420
    frags.append(text(60, y2 - 80, "Option / Maybe — поглинання видиме в типі",
                      size=14, bold=True, color=POS, anchor="start"))
    labels2 = ["крок 1", "Nothing", "крок 3", "крок 4"]
    for i, (x, lb) in enumerate(zip(xs, labels2)):
        if i == 1:
            frags.append(step(x, y2, lb, accent=POS, fill="#fdecea", tcolor=POS))
        elif i > 1:
            frags.append(step(x, y2, lb, accent="#c9ced4", fill="#f7f8fa", tcolor=MUTED))
        else:
            frags.append(step(x, y2, lb))
    frags.append(arrow(xs[0] + 52, y2, xs[1] - 52, y2, color=LINE, sw=1.8))
    frags.append(step(910, y2, "Nothing", accent=POS, fill="#fdecea", tcolor=POS))
    frags.append(arrow(xs[1] + 52, y2 - 44, 910 - 52, y2 - 44, color=POS, sw=2.0))
    frags.append(text((xs[1] + 910) / 2, y2 - 52, "коротке замикання — решту кроків пропущено",
                      size=11, color=POS))
    frags.append(text(150, y2 + 54, "тип каже «тут або значення, або нічого» — наприкінці мусиш розібрати Nothing",
                      size=11.5, color=MUTED, anchor="start"))
    frags.append(text(150, y2 + 74, "поглинання те саме, але видиме й перевірене — забути неможливо",
                      size=11.5, color=FIELD, anchor="start"))

    frags.append(line(44, 306, W - 44, 306, color="#e2e5e9", sw=1.0))
    frags.append(line(44, H - 48, W - 44, H - 48, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 24,
                      "нейтральний ⇒ відсутність інертна й невидима · поглинальний-у-типі ⇒ спиняє й вимагає уваги",
                      size=12.5, bold=True, color=INK))
    render(os.path.join(IMG, 'neutral-vs-absorbing-duality.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_hole_vs_value()
    fig_null_object_skeleton()
    fig_three_ways_absence()
    fig_null_birth_timeline()
    fig_refactor_collapse()
    fig_absence_fork()
    fig_neutral_absorbing_table()
    fig_chain_neutral_vs_absorbing()
    fig_neutral_vs_absorbing_duality()
    print("figs done")
