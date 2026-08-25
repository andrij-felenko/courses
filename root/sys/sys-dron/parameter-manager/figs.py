# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Менеджер параметрів: завантаження, кеш, запис».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

OK_FILL = "#eaf7ef"      # успішна гілка
BAD_FILL = "#fdecea"     # провал / втрата
WAIT_FILL = "#fff8e1"    # очікування


# ── Фігура 1: шлях параметра від байтів до екрана ────────────────────────────
# Ідея: менеджер — лише третій крок із чотирьох; до нього кадр треба розібрати
# й НОРМАЛІЗУВАТИ діалект прошивки, після нього — вдягнути значення в метадані.
def fig_param_path():
    W, H = 1120, 400
    P = []

    stages = [
        (["Канал", "байти в ефірі"],
         ["серійний порт,", "UDP, TCP"]),
        (["Розбір MAVLink", "кадр → повідомлення"],
         ["PARAM_VALUE:", "ім'я, значення,", "тип, номер, усього"]),
        (["Розширення", "прошивки"],
         ["зводить діалект", "борту до одного:", "байтове подання"]),
        (["Менеджер", "параметрів"],
         ["карта:", "компонент → ім'я", "→ факт"]),
        (["Факт + метадані", "на екрані"],
         ["одиниці, межі,", "перелік варіантів,", "опис"]),
    ]

    bw, gap = 180, 42
    total = len(stages) * bw + (len(stages) - 1) * gap
    x0 = (W - total) / 2.0
    by, bh = 96, 96          # верх і висота рамок
    cy = by + bh / 2.0

    for i, (title_lines, note_lines) in enumerate(stages):
        x = x0 + i * (bw + gap)
        fill = FILL
        if i == 3:
            fill = OK_FILL
        P.append(fitbox(x, by, bw, bh, title_lines, size=15, bold=True, fill=fill))
        # пояснення під рамкою — окремим блоком тексту, з відступом
        P.append(mtext(x + bw / 2.0, by + bh + 34, note_lines, size=12, color=MUTED))
        if i < len(stages) - 1:
            P.append(arrow(x + bw + 6, cy, x + bw + gap - 6, cy))

    # підпис до третього кроку — де саме гаситься розбіжність прошивок
    hint_y = 300
    P.append(line(x0 + 2 * (bw + gap) + bw / 2.0, hint_y - 44,
                  x0 + 2 * (bw + gap) + bw / 2.0, hint_y - 14, color=MUTED, sw=1.2, dash="4,4"))
    b, bwid, bht = textbox(W / 2.0, hint_y + 6,
                           ["PX4 передає ціле побайтово, ArduPilot — числовим перетворенням.",
                            "Менеджер бачить лише одну домовленість — розбіжність гасять до нього."],
                           size=13, fill=WAIT_FILL)
    P.append(b)

    render("img/param-path.svg", W, H, *P,
           title="Від байтів у каналі до числа з одиницями на екрані")


# ── Фігура 2: чеклист номерів і доборка дір ──────────────────────────────────
# Ідея: param_count + param_index перетворюють потік без підтверджень на список
# комірок; лічильник спроб не дає доборці крутитися вічно.
def fig_index_checklist():
    W, H = 1060, 640
    P = []

    # стан комірок: 0 — отримано, 1 — чекаємо, 2 — здалися
    state = [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0,
             0, 0, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    cols, cw, ch, cg = 12, 46, 42, 10
    grid_w = cols * cw + (cols - 1) * cg
    gx0, gy0 = 60, 96

    P.append(text(gx0, gy0 - 18, "чеклист номерів (param_count = 24)",
                  size=13, color=MUTED, anchor="start"))

    for i, st in enumerate(state):
        r, c = divmod(i, cols)
        x = gx0 + c * (cw + cg)
        y = gy0 + r * (ch + 22)
        fill = OK_FILL if st == 0 else (WAIT_FILL if st == 1 else BAD_FILL)
        stroke = FIELD if st == 0 else (MUTED if st == 1 else POS)
        P.append(rect(x, y, cw, ch, fill=fill, stroke=stroke, sw=1.6))
        P.append(text(x + cw / 2.0, y + ch / 2.0 + 5, str(i), size=13,
                      color=INK if st != 1 else MUTED))

    # легенда — праворуч від сітки, з великим запасом
    lx = gx0 + grid_w + 46
    for k, (fill, stroke, cap) in enumerate([
            (OK_FILL, FIELD, "отримано"),
            (WAIT_FILL, MUTED, "чекаємо"),
            (BAD_FILL, POS, "здалися")]):
        y = gy0 + k * 40
        P.append(rect(lx, y, 26, 24, fill=fill, stroke=stroke, sw=1.6))
        P.append(text(lx + 36, y + 17, cap, size=13, color=MUTED, anchor="start"))

    # ── нижній ряд: цикл доборки ─────────────────────────────────────────────
    row_y = 320
    b1, w1, h1 = textbox(180, row_y, ["Потік замовк:", "таймер тиші 3 с"], size=14, fill=WAIT_FILL)
    b2, w2, h2 = textbox(470, row_y, ["Пачка ≤ 10 запитів", "за номером"], size=14)
    b3, w3, h3 = textbox(790, row_y, ["Відповідь за 1 с?", "номер викреслено"], size=14, fill=OK_FILL)
    P += [b1, b2, b3]
    P.append(arrow(180 + w1 / 2.0 + 8, row_y, 470 - w2 / 2.0 - 8, row_y))
    P.append(arrow(470 + w2 / 2.0 + 8, row_y, 790 - w3 / 2.0 - 8, row_y))

    # гілка невдачі — вниз від середньої рамки
    fy = row_y + 130
    b4, w4, h4 = textbox(470, fy, ["Тиші не було чим зарадити:", "лічильник спроб цього номера +1"],
                         size=13, fill=BAD_FILL)
    P.append(b4)
    P.append(arrow(470, row_y + h2 / 2.0 + 6, 470, fy - h4 / 2.0 - 6))

    b5, w5, h5 = textbox(470, fy + 108, ["Понад 5 спроб — номер визнають утраченим,",
                                         "набір оголошують неповним"], size=13, fill=BAD_FILL)
    P.append(b5)
    P.append(arrow(470, fy + h4 / 2.0 + 6, 470, fy + 108 - h5 / 2.0 - 6))

    # зворотний зв'язок: викреслений номер одразу звільняє місце в пачці
    rx = 790 + w3 / 2.0 + 30
    P.append(line(790 + w3 / 2.0 + 8, row_y, rx, row_y, color=FIELD, sw=1.6))
    P.append(line(rx, row_y, rx, row_y - 74, color=FIELD, sw=1.6))
    P.append(line(rx, row_y - 74, 470, row_y - 74, color=FIELD, sw=1.6))
    P.append(arrow(470, row_y - 74, 470, row_y - h2 / 2.0 - 8, color=FIELD))
    P.append(text(640, row_y - 84, "місце в пачці звільнилося — беремо наступну діру",
                  size=12, color=FIELD))

    render("img/index-checklist.svg", W, H, *P,
           title="Чеклист номерів: як із потоку без підтверджень зробити повний набір")


# ── Фігура 3: три дороги завантаження ────────────────────────────────────────
# Ідея: дорогу обирають до першого запиту, а КОЖЕН провал швидкої дороги
# веде в ту саму звичайну — тож швидкість утратити можна, параметри — ні.
def fig_download_routes():
    W, H = 1140, 620
    P = []

    colx = [200, 570, 940]
    y1, y2, y3 = 100, 226, 352

    # колонка A — канал, на якому не вантажать узагалі
    a1, aw1, ah1 = textbox(colx[0], y1, ["Канал із високою затримкою", "або відтворення логу"],
                           size=14, fill=BAD_FILL)
    a2, aw2, ah2 = textbox(colx[0], y2, ["Не вантажимо взагалі:", "готовність + ознака",
                                         "«набір неповний»"], size=14, fill=BAD_FILL)
    P += [a1, a2]
    P.append(arrow(colx[0], y1 + ah1 / 2.0 + 6, colx[0], y2 - ah2 / 2.0 - 6))

    # колонка B — ArduPilot через передачу файлу
    b1, bw1, bh1 = textbox(colx[1], y1, ["ArduPilot"], size=15, bold=True)
    b2, bw2, bh2 = textbox(colx[1], y2, ["Файл параметрів по MAVFTP:", "@PARAM/param.pck"], size=14)
    b3, bw3, bh3 = textbox(colx[1], y3, ["Розібрали файл —", "набір і значення",
                                         "за замовчуванням"], size=14, fill=OK_FILL)
    P += [b1, b2, b3]
    P.append(arrow(colx[1], y1 + bh1 / 2.0 + 6, colx[1], y2 - bh2 / 2.0 - 6))
    P.append(arrow(colx[1], y2 + bh2 / 2.0 + 6, colx[1], y3 - bh3 / 2.0 - 6))

    # колонка C — PX4 через хеш-звірку
    c1, cw1, ch1 = textbox(colx[2], y1, ["PX4"], size=15, bold=True)
    c2, cw2, ch2 = textbox(colx[2], y2, ["Читаємо _HASH_CHECK,", "звіряємо суму з кешем"], size=14)
    c3, cw3, ch3 = textbox(colx[2], y3, ["Сума збіглася —", "факти просто з диска"],
                           size=14, fill=OK_FILL)
    P += [c1, c2, c3]
    P.append(arrow(colx[2], y1 + ch1 / 2.0 + 6, colx[2], y2 - ch2 / 2.0 - 6))
    P.append(arrow(colx[2], y2 + ch2 / 2.0 + 6, colx[2], y3 - ch3 / 2.0 - 6))

    # спільна нижня рамка — звичайне завантаження
    bot_y = 552
    bx, bwid, bht = textbox(W / 2.0, bot_y,
                            ["PARAM_REQUEST_LIST → потік PARAM_VALUE → чеклист і доборка"],
                            size=15, bold=True, min_w=860)
    P.append(bx)

    # провали швидких доріг — збоку від колонок, щоб лінії нічого не перетинали
    fy = 452
    f1, fw1, fh1 = textbox(385, fy, ["немає файлу,", "надто повільно,", "забагато повторів"],
                           size=12, fill=BAD_FILL)
    P.append(f1)
    P.append(line(colx[1] - bw2 / 2.0 - 6, y2, 385, y2, color=POS, sw=1.5))
    P.append(line(385, y2, 385, fy - fh1 / 2.0 - 6, color=POS, sw=1.5))
    P.append(arrow(385, fy + fh1 / 2.0 + 6, 385, bot_y - bht / 2.0 - 6, color=POS))

    f2, fw2, fh2 = textbox(755, fy, ["сума не збіглася,", "немає кешу,", "тиша 1 с"],
                           size=12, fill=BAD_FILL)
    P.append(f2)
    P.append(line(colx[2] - cw2 / 2.0 - 6, y2, 755, y2, color=POS, sw=1.5))
    P.append(line(755, y2, 755, fy - fh2 / 2.0 - 6, color=POS, sw=1.5))
    P.append(arrow(755, fy + fh2 / 2.0 + 6, 755, bot_y - bht / 2.0 - 6, color=POS))

    render("img/download-routes.svg", W, H, *P,
           title="Три дороги завантаження — і одна спільна запасна")


# ── Фігура 4: автомат запису параметра ───────────────────────────────────────
# Ідея: успішна гілка коротка, уся решта — дві різні невдачі (тиша й відмова),
# що сходяться в перечитуванні з борту.
def fig_param_set_fsm():
    W, H = 1060, 700
    P = []

    mx = 430          # головна колонка
    rx = 830          # права колонка (явна відмова)
    lx = 96           # ліва доріжка повтору

    s1, w1, h1 = textbox(mx, 92, ["Користувач правив факт"], size=14)
    s2, w2, h2 = textbox(mx, 196, ["Надіслати PARAM_SET,", "лічильник записів +1"], size=14)
    s3, w3, h3 = textbox(mx, 312, ["Чекати відлуння PARAM_VALUE", "одну секунду"],
                         size=14, fill=WAIT_FILL)
    s4, w4, h4 = textbox(mx, 432, ["Ім'я і значення збіглися —", "успіх, лічильник −1"],
                         size=14, fill=OK_FILL)
    P += [s1, s2, s3, s4]
    P.append(arrow(mx, 92 + h1 / 2.0 + 6, mx, 196 - h2 / 2.0 - 6))
    P.append(arrow(mx, 196 + h2 / 2.0 + 6, mx, 312 - h3 / 2.0 - 6))
    P.append(arrow(mx, 312 + h3 / 2.0 + 6, mx, 432 - h4 / 2.0 - 6))

    # ліва доріжка: тиша → повтор (до двох), потім невдача
    P.append(line(mx - w3 / 2.0 - 6, 312, lx, 312, color=MUTED, sw=1.5))
    P.append(arrow(lx, 312, lx, 196 + 4, color=MUTED))
    P.append(line(lx, 196, mx - w2 / 2.0 - 6, 196, color=MUTED, sw=1.5))
    P.append(mtext(lx + 18, 244, ["тиша:", "повтор,", "до двох"], size=12, color=MUTED,
                   anchor="start"))

    # права колонка: явна відмова
    r1, rw1, rh1 = textbox(rx, 312, ["PARAM_ERROR:", "не існує, поза межами,", "лише для читання"],
                           size=13, fill=BAD_FILL)
    P.append(r1)
    P.append(arrow(mx + w3 / 2.0 + 6, 312, rx - rw1 / 2.0 - 6, 312, color=POS))
    P.append(text((mx + rx) / 2.0, 288, "без повторів", size=12, color=POS))

    # сходження невдач
    f1, fw1, fh1 = textbox(rx, 452, ["Спроби вичерпано", "або відмова"], size=13, fill=BAD_FILL)
    P.append(f1)
    P.append(arrow(rx, 312 + rh1 / 2.0 + 6, rx, 452 - fh1 / 2.0 - 6, color=POS))
    P.append(line(lx, 384, lx, 452, color=POS, sw=1.5))
    P.append(arrow(lx, 452, rx - fw1 / 2.0 - 6, 452, color=POS))
    P.append(text(lx + 18, 402, "спроб більше немає", size=12, color=POS, anchor="start"))

    f2, fw2, fh2 = textbox(rx, 556, ["Сказати людині"], size=13, fill=BAD_FILL)
    f3, fw3, fh3 = textbox(rx, 650, ["Перечитати параметр із борту:", "у факті знову правда"],
                           size=13, fill=OK_FILL)
    P += [f2, f3]
    P.append(arrow(rx, 452 + fh1 / 2.0 + 6, rx, 556 - fh2 / 2.0 - 6, color=POS))
    P.append(arrow(rx, 556 + fh2 / 2.0 + 6, rx, 650 - fh3 / 2.0 - 6, color=POS))

    render("img/param-set-fsm.svg", W, H, *P,
           title="Запис параметра: коротка успішна гілка й дві різні невдачі")


# ── Фігура 5 (до вставки proj-param-sync): три стратегії добору на осі часу ──
# Ідея: пачка виграє в ОБОХ сусідів — «усе одразу» топить канал власними
# запитами, «по одному» перетворює втрати на послідовний ланцюжок затримок.
def fig_batch_timeline():
    W, H = 1180, 610
    P = []

    x0, unit, ticks = 340, 100, 7
    x1 = x0 + ticks * unit          # 1040
    bh = 52
    yA, yB, yC = 110, 250, 390

    # ── підписи доріжок ліворуч (колонка 30…320, доріжки починаються з 340) ──
    labels = [
        (yA, "Усе одразу", ["сорок запитів у ту саму", "мить, у той самий канал"]),
        (yB, "По одному", ["наступний запит — тільки", "після відповіді"]),
        (yC, "Пачка ≤ 10", ["десять у польоті завжди,", "звільнилось — беремо ще"]),
    ]
    for y, name, note in labels:
        P.append(text(30, y + 16, name, size=15, bold=True, anchor="start"))
        P.append(mtext(30, y + 38, note, size=12, color=MUTED, anchor="start"))

    # ── доріжка A: залп, усі дедлайни спливають разом, залп знову ────────────
    for k in (0.0, 1.5, 3.0):
        P.append(rect(x0 + k * unit, yA, 18, bh, fill="#f5b7b1", stroke=POS, sw=1.6))
    P.append(fitbox(x0 + 3.5 * unit, yA, x1 - (x0 + 3.5 * unit), bh,
                    ["усі 40 дедлайнів спливають разом —",
                     "залп повторюється цілком"],
                    size=13, fill=BAD_FILL, stroke=POS))
    P.append(arrow(x1 + 8, yA + bh / 2.0, x1 + 62, yA + bh / 2.0, color=POS))
    P.append(text(x0, yA + bh + 24,
                  "у каналі немає нічого, крім наших запитів: відповідям нема коли пройти",
                  size=12, color=POS, anchor="start"))

    # ── доріжка B: запит — очікування — запит ────────────────────────────────
    for k in range(6):
        xk = x0 + k * unit
        P.append(rect(xk, yB + 10, 14, bh - 20, fill=FILL, stroke=MUTED, sw=1.5))
        if k < 5:
            P.append(line(xk + 14, yB + bh / 2.0, xk + unit, yB + bh / 2.0,
                          color=MUTED, sw=1.4, dash="5,5"))
    P.append(text(x0 + 5 * unit + 24, yB + bh / 2.0 + 5,
                  "… ще 35 кроків — разом 40 RTT", size=13, color=MUTED, anchor="start"))
    P.append(text(x0, yB + bh + 24,
                  "запит → відповідь → наступний запит: затримки складаються",
                  size=12, color=MUTED, anchor="start"))

    # ── доріжка C: чотири пачки по десять ────────────────────────────────────
    for k, cap in enumerate(["діри 1–10", "11–20", "21–30", "31–40"]):
        P.append(fitbox(x0 + k * unit + 4, yC, unit - 8, bh, [cap],
                        size=13, fill=OK_FILL, stroke=FIELD))
    P.append(line(x0 + 4 * unit, yC - 8, x0 + 4 * unit, 498,
                  color=FIELD, sw=1.5, dash="6,5"))
    P.append(text(x0 + 4 * unit + 16, yC + bh / 2.0 + 5, "усі 40 добрано",
                  size=13, color=FIELD, anchor="start"))
    P.append(text(x0, yC + bh + 24, "кожна відповідь одразу звільняє місце в пачці",
                  size=12, color=FIELD, anchor="start"))

    # ── вісь часу ────────────────────────────────────────────────────────────
    P.append(line(x0 - 12, 490, x1 + 30, 490, color=MUTED, sw=1.4))
    for k in range(ticks + 1):
        xk = x0 + k * unit
        P.append(line(xk, 490, xk, 498, color=MUTED, sw=1.4))
        P.append(text(xk, 516, str(k), size=12, color=MUTED))
    P.append(text(30, 516, "час, у затримках туди-назад", size=12, color=MUTED, anchor="start"))

    b, bw, bh2 = textbox(W / 2.0, 566,
                         ["40 дір, затримка туди-назад 0.4 с:",
                          "по одному — 40 · 0.4 = 16 с   ·   пачкою по 10 — ⌈40/10⌉ · 0.4 = 1.6 с"
                          "   ·   усе одразу — 0.4 с на ідеальному каналі й лавина повторів на реальному"],
                         size=13, fill=WAIT_FILL)
    P.append(b)

    render("img/batch-timeline.svg", W, H, *P,
           title="Сорок дір, три способи їх добрати: чому пачка виграє в обох сусідів")


# ── Фігура (вставка proj-param-pck): розкладка байтів param.pck ──────────────
# Ідея: увесь формат — це 6 байтів заголовка плюс записи змінної довжини, де
# ДВА керівні байти розрізані на напівбайти; саме напівбайти й треба показати.
def fig_pck_layout():
    W, H = 1180, 560
    P = []

    # ── заголовок файлу ──────────────────────────────────────────────────────
    hw, hg = 200, 24
    hx0 = (W - (3 * hw + 2 * hg)) / 2.0
    P.append(text(hx0, 70, "заголовок — 6 байтів, порядок little-endian",
                  size=13, color=MUTED, anchor="start"))
    heads = [
        ("magic", ["0x671B — без замовчувань", "0x671C — із ними"]),
        ("num_params", ["скільки записів у файлі"]),
        ("total_params", ["скільки параметрів на борту"]),
    ]
    for i, (cap, note) in enumerate(heads):
        x = hx0 + i * (hw + hg)
        P.append(rect(x, 90, hw, 56))
        P.append(text(x + hw / 2.0, 125, cap, size=15, bold=True))
        P.append(mtext(x + hw / 2.0, 172, note, size=12, color=MUTED))

    # ── запис одного параметра ───────────────────────────────────────────────
    P.append(text(80, 232, "запис параметра — довжина змінна, межі задають самі поля",
                  size=13, color=MUTED, anchor="start"))
    cells = [
        (90,  "набивка",      "не завжди",               WAIT_FILL, True),
        (110, "байт 0",       "тип + прапорці",          FILL,      False),
        (110, "байт 1",       "довжини імені",           FILL,      False),
        (250, "ім'я",         "лише НЕспільний хвіст",   FILL,      False),
        (190, "значення",     "1, 2 або 4 байти",        OK_FILL,   False),
        (230, "замовчування", "лише коли прапорець = 1", WAIT_FILL, True),
    ]
    x = 80
    for cw, cap, note, fill, dashed in cells:
        P.append(rect(x, 252, cw, 56, fill=fill,
                      stroke=(MUTED if dashed else LINE), sw=1.6))
        P.append(text(x + cw / 2.0, 287, cap, size=14, bold=True))
        P.append(text(x + cw / 2.0, 332, note, size=11, color=MUTED))
        x += cw + 8

    # ── напівбайти двох керівних байтів (справжній перший запис набору) ───────
    panels = [
        (140, "байт 0 = 0x11",
         ["старший напівбайт", "прапорці = 1", "(замовчування є)"],
         ["молодший напівбайт", "тип = 1", "(int8)"]),
        (700, "байт 1 = 0xB0",
         ["старший напівбайт", "name_len − 1 = 0xB", "(ім'я 12 байтів)"],
         ["молодший напівбайт", "common_len = 0", "(спільного нема)"]),
    ]
    for px, title, hi, lo in panels:
        P.append(text(px + 170, 404, title, size=14, bold=True))
        P.append(fitbox(px, 422, 170, 84, hi, size=12))
        P.append(fitbox(px + 170, 422, 170, 84, lo, size=12, fill=BG))

    render("img/pck-layout.svg", W, H, *P,
           title="param.pck по байтах: заголовок, запис і напівбайти двох керівних байтів")


# ── Фігура (вставка proj-param-pck): набивка й межа блока ────────────────────
# Ідея: набивка існує НЕ заради вирівнювання, а щоб повторне читання блока
# ніколи не склеїло значення з двох різних моментів часу.
def fig_pck_padding():
    W, H = 1180, 500
    P = []

    BPX = 40.0            # пікселів на байт
    O0 = 20               # ліворуч показуємо зі зсуву 20
    x0 = 190

    def bx(ofs):
        return x0 + (ofs - O0) * BPX

    P.append(text(bx(32), 56, "межа блока читання", size=13, color=POS))
    P.append(line(bx(32), 118, bx(32), 366, color=POS, sw=2.4))

    for o in range(O0, 41, 4):        # лінійка зсувів у файлі
        P.append(text(bx(o), 100, str(o), size=12, color=MUTED))

    rows = [
        (150, "якби набивки не було", 21, None, 31, BAD_FILL,
         "значення int32 розірване межею: 1 байт тут, 3 — у наступному блоці"),
        (290, "як воно насправді", 21, 21, 32, OK_FILL,
         "один нульовий байт набивки — і значення цілком у новому блоці"),
    ]
    for ry, cap, rec_beg, pad_ofs, val_beg, val_fill, note in rows:
        P.append(text(x0, ry - 16, cap, size=14, bold=True, anchor="start"))
        P.append(rect(bx(rec_beg), ry, bx(val_beg + 4) - bx(rec_beg), 54))
        if pad_ofs is not None:
            P.append(rect(bx(pad_ofs), ry, BPX, 54, fill=WAIT_FILL, stroke=MUTED, sw=1.6))
            P.append(text(bx(pad_ofs) + BPX / 2.0, ry + 84, "00", size=13, color=MUTED))
        P.append(rect(bx(val_beg), ry, 4 * BPX, 54, fill=val_fill, sw=1.6))
        P.append(text((bx(rec_beg) + bx(val_beg)) / 2.0, ry + 33,
                      "байт 0 · байт 1 · ім'я", size=12))
        P.append(text(bx(val_beg) + 2 * BPX, ry + 33, "значення", size=13, bold=True))
        P.append(text(bx(val_beg) + 2 * BPX, ry + 84, note, size=13, color=MUTED))

    b, bw, bh = textbox(W / 2.0, 452,
                        ["На рисунку блок узято 16-байтовим, щоб він уміщався; насправді станція",
                         "читає по 239 байтів — стільки даних несе один кадр передачі файлів."],
                        size=13, fill=FILL)
    P.append(b)

    render("img/pck-padding.svg", W, H, *P,
           title="Навіщо нульова набивка: значення не сміє лежати у двох блоках одразу")


# ── Фігура 6 (до вставки api-param-manager): бюджет часу зі сталих ───────────
# Ідея: числові сталі поодинці нічого не кажуть — вага в тому, скільки часу
# кожна з них дозволяє підсистемі мовчати, перш ніж визнати невдачу.
def fig_timeout_budget():
    W, H = 1180, 600
    P = []

    x0, x1 = 430, 1120
    tmax = 25.0
    unit = (x1 - x0) / tmax          # px на секунду
    bh = 34

    rows = [
        (1.0, "Хеш-звірка з кешем",
         ["kHashCheckTimeoutMs 1000 мс,", "спроба одна, без повторів"],
         "1 с → падаємо на звичайне завантаження", WAIT_FILL, MUTED),
        (25.0, "Запит списку без відповіді",
         ["kParamRequestListTimeoutMs 5000 мс ×", "(1 + kMaxInitialRequestListRetry 4)"],
         "25 с → «апарат не відповів на запит»", BAD_FILL, POS),
        (3.0, "Тиша посеред потоку",
         ["таймер 3000 мс, перезапуск", "на кожному PARAM_VALUE"],
         "3 с → вмикається доборка дір", WAIT_FILL, MUTED),
        (15.0, "Один номер у доборці",
         ["1000 мс × (1 + 2) на коло,", "до 5 кіл на один номер"],
         "15 с → номер визнано втраченим", BAD_FILL, POS),
        (3.0, "Запис одного параметра",
         ["kWaitForParamValueAckMs 1000 мс ×", "(1 + kParamSetRetryCount 2)"],
         "3 с → невдача й перечитування", BAD_FILL, POS),
        (7.0, "Паузи між колами bulkRefresh",
         ["kRetryBaseDelayMs 1000 мс,", "подвоєння щокола: 1 + 2 + 4"],
         "7 с самих лише пауз на 3 кола", OK_FILL, FIELD),
    ]

    y = 78
    for secs, name, note, cap, fill, stroke in rows:
        bw = secs * unit
        P.append(text(30, y + 12, name, size=15, bold=True, anchor="start"))
        P.append(mtext(30, y + 32, note, size=12, color=MUTED, anchor="start"))
        if bw >= 300:
            # підпис влазить у саму смугу — окремої рамки не треба
            P.append(fitbox(x0, y, bw, bh, [cap], size=13, fill=fill, stroke=stroke, sw=1.8))
        else:
            P.append(rect(x0, y, bw, bh, fill=fill, stroke=stroke, sw=1.8))
            P.append(text(x0 + bw + 14, y + 22, cap, size=13, color=stroke, anchor="start"))
        y += 78

    # ── вісь часу під усіма доріжками ────────────────────────────────────────
    ay = 545
    P.append(line(x0 - 14, ay, x1 + 24, ay, color=MUTED, sw=1.4))
    for k in range(0, 26, 5):
        xk = x0 + k * unit
        P.append(line(xk, ay, xk, ay + 9, color=MUTED, sw=1.4))
        P.append(text(xk, ay + 27, str(k), size=12, color=MUTED))
    P.append(text(30, ay + 27, "час мовчання, секунди", size=12, color=MUTED, anchor="start"))

    render("img/timeout-budget.svg", W, H, *P,
           title="Скільки часу кожна стала дозволяє мовчати, перш ніж це визнають невдачею")


fig_param_path()
fig_index_checklist()
fig_download_routes()
fig_param_set_fsm()
fig_batch_timeline()
fig_timeout_budget()
fig_pck_layout()
fig_pck_padding()
print("figs.py: готово —", ", ".join(sorted(os.listdir("img"))))
