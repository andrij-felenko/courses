# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

RED_FILL  = "#fdecea"   # діра / небезпека
GRN_FILL  = "#e9f7ef"   # безпечно / законно
BLU_FILL  = "#eef4ff"   # нейтральна станція
ORNG      = "#e67e22"   # «важче, та тече»
ORNG_FILL = "#fef5e7"


def dashed_rect(x, y, w, h, color, sw, dash="7 6"):
    return (line(x, y, x + w, y, color, sw, dash) +
            line(x + w, y, x + w, y + h, color, sw, dash) +
            line(x + w, y + h, x, y + h, color, sw, dash) +
            line(x, y + h, x, y, color, sw, dash))


# ── Фігура 1: пропущений бар'єр авторизації об'єкта ──────────────────────────
def fig_missing_gate():
    W, H = 1040, 470
    frags = []
    y = 250   # спільна вісь потоку

    # Станція 1 — мешканець
    u, uw, uh = textbox(120, y, ["Мешканець", "дому #4021"], size=15, bold=True,
                        pad=15, fill=BLU_FILL, stroke=NEG, sw=2.2, min_w=180)

    # Станція 2 — бар'єр автентифікації (є, пропускає)
    g1x = 400
    g1, g1w, g1h = textbox(g1x, y, ["AuthN  ✓", "сесія дійсна", "знаємо ХТО"], size=14,
                           bold=True, pad=15, fill=GRN_FILL, stroke=FIELD, sw=2.4, min_w=200)

    # Станція 3 — бар'єр авторизації об'єкта ВІДСУТНІЙ (пунктирна рамка)
    g2x, g2w, g2h = 690, 240, 150
    frags.append(dashed_rect(g2x - g2w/2, y - g2h/2, g2w, g2h, POS, 2.4))
    frags.append(mtext(g2x, y - 28, ["AuthZ  ✗", "«4088 — твій?»", "питання не", "поставлено"],
                       size=14, bold=True, color=POS, lh=1.35))

    # Станція 4 — сервер піднімає чужий дім
    s4x = 940
    s4, s4w, s4h = textbox(s4x, y, ["Сервер підіймає", "Дім #4088", "(сусіда) за id"], size=14,
                           bold=True, pad=15, fill=RED_FILL, stroke=POS, sw=2.2, min_w=180)

    for b in (u, g1, s4):
        frags.append(b)

    # Стрілки потоку
    frags.append(arrow(120 + uw/2, y, g1x - g1w/2 - 6, y, color=INK, sw=1.8))
    frags.append(arrow(g1x + g1w/2, y, g2x - g2w/2 - 6, y, color=INK, sw=1.8))
    frags.append(arrow(g2x + g2w/2, y, s4x - s4w/2 - 6, y, color=POS, sw=1.8))

    # Підпис підробленого запиту — над першою стрілкою, вище за рамки
    mid1 = (120 + uw/2 + g1x - g1w/2) / 2
    frags.append(text(mid1, 150, "GET /homes/4088/devices", size=13, bold=True, color=INK))
    frags.append(text(mid1, 170, "4088 — не його дім", size=12, italic=True, color=POS))

    # Вихід — під сервером
    frags.append(text(s4x, y + s4h/2 + 30, "→ камера й історія", size=12, bold=True, color=POS))
    frags.append(text(s4x, y + s4h/2 + 48, "замків сусіда", size=12, bold=True, color=POS))

    frags.append(text(W/2, H - 22,
                      "пролом — це відсутній бар'єр, а не зла дія: сервер зробив рівно те, що сказали",
                      size=13, bold=True, color=MUTED))

    render(os.path.join(IMG, 'idor-missing-gate.svg'), W, H, *frags,
           title="Пропущений бар'єр: автентифікація пройшла, авторизацію об'єкта не спитали")


# ── Фігура 2: горизонтальна проти вертикальної ескалації ─────────────────────
def fig_escalation_axes():
    W, H = 980, 600
    frags = []

    cols = [("Дім #4021", 300), ("Дім #4088", 520), ("Дім #4102", 740)]
    rows = [("Адмін платформи", 160), ("Власник", 320), ("Мешканець", 480)]
    cw, ch = 190, 118

    # Сітка клітин
    for cname, cx in cols:
        for rname, cy in rows:
            legit = (cx == 300 and cy == 480)
            fill = GRN_FILL if legit else FILL
            stroke = FIELD if legit else MUTED
            sw = 2.8 if legit else 1.3
            frags.append(rect(cx - cw/2, cy - ch/2, cw, ch, fill=fill, stroke=stroke, sw=sw, rx=10))
            if legit:
                frags.append(mtext(cx, cy - 4, ["ТИ ТУТ", "законно"], size=15, bold=True, color=FIELD))
            else:
                frags.append(text(cx, cy + 6, "·", size=22, color=MUTED))

    # Заголовки стовпців (орендарі) — над сіткою
    for cname, cx in cols:
        frags.append(text(cx, 92, cname, size=14, bold=True, color=INK))
    # Підписи рядків (рівень влади) — ПРАВОРУЧ від сітки, щоб звільнити лівий канал
    for rname, cy in rows:
        frags.append(text(858, cy, rname, size=13, bold=True, color=MUTED, anchor="start"))

    lx = 300  # центр колонки #4021
    # ГОРИЗОНТАЛЬНА: убік у сусідній дім тим самим рядком «Мешканець»
    frags.append(arrow(lx + cw/2 + 4, 480, 520 - cw/2 - 6, 480, color=POS, sw=2.8))
    frags.append(text(410, 566, "горизонтальна ескалація (IDOR) — убік, до дому рівні",
                      size=13, bold=True, color=POS))

    # ВЕРТИКАЛЬНА: угору за привілеєм — каналом ЛІВОРУЧ від колонки #4021 (обходить клітини)
    chx = 150   # канал ліворуч від сітки (край клітини #4021 = 205)
    frags.append(line(lx - cw/2, 480, chx, 480, color=NEG, sw=2.6))
    frags.append(line(chx, 480, chx, 160, color=NEG, sw=2.6))
    frags.append(arrow(chx, 160, lx - cw/2 - 4, 160, color=NEG, sw=2.6))
    frags.append(mtext(84, 300, ["вертикальна", "ескалація —", "вгору", "за владою"], size=12,
                       bold=True, color=NEG, lh=1.4))

    render(os.path.join(IMG, 'escalation-axes.svg'), W, H, *frags,
           title="Дві осі ескалації: убік до сусіда проти вгору за привілеєм")


# ── Фігура 3: матриця «пряме посилання × чек власності» ──────────────────────
def fig_ref_check_matrix():
    W, H = 860, 520
    frags = []

    rh_x, rh_w = 40, 200          # стовпчик підписів рядків
    cA_x, cB_x = 260, 560         # ліві краї двох стовпців клітин
    cell_w = 270
    r1_y, r2_y = 150, 330         # верхні краї двох рядків
    cell_h = 150

    # Заголовки стовпців
    frags.append(fitbox(cA_x, 74, cell_w, 56, ["Чек власності", "ВІДСУТНІЙ"], size=15,
                        bold=True, fill=RED_FILL, stroke=POS, sw=2))
    frags.append(fitbox(cB_x, 74, cell_w, 56, ["Чек власності", "Є"], size=15,
                        bold=True, fill=GRN_FILL, stroke=FIELD, sw=2))

    # Підписи рядків
    frags.append(fitbox(rh_x, r1_y, rh_w, cell_h, ["id передбачуваний", "1, 2, 3 …"], size=14,
                        bold=True, fill=BLU_FILL, stroke=MUTED, sw=1.6))
    frags.append(fitbox(rh_x, r2_y, rh_w, cell_h, ["id непрозорий", "UUID"], size=14,
                        bold=True, fill=BLU_FILL, stroke=MUTED, sw=1.6))

    # Клітини
    frags.append(fitbox(cA_x, r1_y, cell_w, cell_h,
                        ["ДІРА", "тривіально:", "перебір  id+1"], size=15, bold=True,
                        fill=RED_FILL, stroke=POS, sw=2.4, color=POS))
    frags.append(fitbox(cB_x, r1_y, cell_w, cell_h,
                        ["безпечно", "«не твоє»"], size=16, bold=True,
                        fill=GRN_FILL, stroke=FIELD, sw=2.4, color=FIELD))
    frags.append(fitbox(cA_x, r2_y, cell_w, cell_h,
                        ["ДІРА", "важче, та id тече:", "лінки · логи · списки"], size=14, bold=True,
                        fill=ORNG_FILL, stroke=ORNG, sw=2.4, color=ORNG))
    frags.append(fitbox(cB_x, r2_y, cell_w, cell_h,
                        ["безпечно", "«не твоє»"], size=16, bold=True,
                        fill=GRN_FILL, stroke=FIELD, sw=2.4, color=FIELD))

    frags.append(text(W/2, H - 22,
                      "рятує СТОВПЧИК «чек є», а не рядок «id непрозорий» — латка живе в стовпці",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'ref-check-matrix.svg'), W, H, *frags,
           title="Дві умови діри: пряме посилання × пропущений чек")


# ── Вставка hist: фігури лінії назв ──────────────────────────────────────────

# ── Фігура H1: заплутаний заступник — та сама помилка через 42 роки ───────────
def fig_confused_deputy_shape():
    W, H = 1160, 560
    frags = []

    def deputy_row(y, era, caller_lines, dep_lines, obj_lines, req, own_note, out_note):
        cx, dx, ox = 205, 570, 960
        cbox, cw, ch = textbox(cx, y, caller_lines, size=15, bold=True, pad=14,
                               fill=BLU_FILL, stroke=NEG, sw=2.2, min_w=150)
        dbox, dw, dh = textbox(dx, y, dep_lines, size=15, bold=True, pad=14,
                               fill=FILL, stroke=INK, sw=2.4, min_w=200)
        obox, ow, oh = textbox(ox, y, obj_lines, size=15, bold=True, pad=14,
                               fill=RED_FILL, stroke=POS, sw=2.2, min_w=185)
        frags.extend([cbox, dbox, obox])
        frags.append(arrow(cx + cw / 2, y, dx - dw / 2 - 6, y, color=INK, sw=1.9))
        frags.append(arrow(dx + dw / 2, y, ox - ow / 2 - 6, y, color=POS, sw=2.3))
        m1 = (cx + cw / 2 + dx - dw / 2) / 2
        frags.append(text(m1, y - dh / 2 - 15, req, size=13, bold=True, color=INK))
        m2 = (dx + dw / 2 + ox - ow / 2) / 2
        frags.append(text(m2, y - oh / 2 - 15, "вживає ВЛАСНЕ право", size=13, bold=True, color=POS))
        frags.append(mtext(78, y - 6, era, size=12, bold=True, color=MUTED, lh=1.3))
        frags.append(text(dx, y + dh / 2 + 22, own_note, size=12, italic=True, color=MUTED))
        frags.append(text(ox, y + oh / 2 + 22, out_note, size=12, bold=True, color=POS))

    deputy_row(200, ["Tymshare", "≈1977"],
               ["Користувач"], ["Компілятор", "заступник"], ["Файл «BILL»", "облік оплат"],
               "вивід статистики → у файл «BILL»",
               "має власне право писати в «BILL»", "облік перезаписано")
    frags.append(line(60, 310, W - 60, 310, MUTED, 1.2, "4 6"))
    deputy_row(420, ["веб-сервер", "2019"],
               ["Клієнт DH"], ["Сервер", "заступник"], ["Дім #4088", "сусіда"],
               "дай дім «4088»",
               "має повний доступ до бази", "пристрої віддано")

    frags.append(text(W / 2, H - 22,
                      "заступник питає «чи маю право Я?» замість «чи має право ТОЙ, ХТО ПОПРОСИВ?»",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'confused-deputy-shape.svg'), W, H, *frags,
           title="Заплутаний заступник: та сама помилка через 42 роки")


# ── Фігура H2: одна вада — низка імен (1988 → 2023) ──────────────────────────
def fig_name_lineage():
    W, H = 1180, 540
    frags = []
    TOPY, BOTY, ROOTY = 168, 432, 300

    rx = 180
    rbox, rw, rh = textbox(rx, ROOTY, ["«Заплутаний", "заступник»", "Norm Hardy · 1988"],
                           size=13, bold=True, pad=13, fill=BLU_FILL, stroke=NEG, sw=2.2, min_w=185)
    frags.append(rbox)

    def tb(cx, y, lines, fill, stroke):
        b, w, h = textbox(cx, y, lines, size=13, bold=True, pad=12, fill=fill, stroke=stroke,
                          sw=2, min_w=215)
        frags.append(b)
        return w, h

    tw1, th1 = tb(475, TOPY, ["IDOR = A4", "OWASP Top 10", "2007 · 2010 · 2013"], FILL, MUTED)
    tw2, th2 = tb(755, TOPY, ["влито в A5", "«Broken Access", "Control» · 2017"], ORNG_FILL, ORNG)
    tw3, th3 = tb(1035, TOPY, ["A01 — ризик №1", "(піднявсь з 5-го)", "2021"], RED_FILL, POS)
    bw1, bh1 = tb(755, BOTY, ["BOLA = API1", "OWASP API", "Security · 2019"], FILL, MUTED)
    bw2, bh2 = tb(1035, BOTY, ["BOLA = API1", "лишилась №1", "2023"], RED_FILL, POS)

    # гілки від кореня до обох доріжок
    frags.append(arrow(rx + rw / 2, ROOTY - 18, 475 - tw1 / 2 - 6, TOPY + th1 / 2, color=INK, sw=1.9))
    frags.append(arrow(rx + rw / 2, ROOTY + 18, 755 - bw1 / 2 - 6, BOTY - bh1 / 2, color=INK, sw=1.9))
    # рух уздовж доріжок
    frags.append(arrow(475 + tw1 / 2, TOPY, 755 - tw2 / 2 - 6, TOPY, color=INK, sw=1.9))
    frags.append(arrow(755 + tw2 / 2, TOPY, 1035 - tw3 / 2 - 6, TOPY, color=INK, sw=1.9))
    frags.append(arrow(755 + bw1 / 2, BOTY, 1035 - bw2 / 2 - 6, BOTY, color=INK, sw=1.9))

    frags.append(text(475, TOPY - th1 / 2 - 16, "вебзастосунки", size=12, italic=True, color=MUTED))
    frags.append(text(755, BOTY + bh1 / 2 + 20, "світ API", size=12, italic=True, color=MUTED))

    frags.append(text(W / 2, H - 20,
                      "IDOR · A4 · Broken Access Control · A01 · BOLA · API1 — одне: пропущений чек права на об'єкт",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'name-lineage.svg'), W, H, *frags,
           title="Одна вада — низка імен (1988 → 2023)")


# ── Фігура H3: три витоки, той самий пропуск ─────────────────────────────────
def fig_breach_arc():
    W, H = 1060, 560
    frags = []
    cw = 300
    # (cx, назва, рік, authN-стан, колір-фон, колір-край, результат-рядки)
    cards = [
        (200, "First American", "2019", ["AuthN — «хто ти»", "✗ нема: ні логіна"], RED_FILL, POS,
              ["≈885 млн файлів;", "+1 до номера → чужа угода"]),
        (530, "USPS", "2018", ["AuthN — «хто ти»", "✓ є: будь-який вхід"], GRN_FILL, FIELD,
              ["≈60 млн акаунтів;", "будь-хто читав чужий"]),
        (860, "Peloton", "2021", ["AuthN — «хто ти»", "✓ є: «латка» = вхід"], GRN_FILL, FIELD,
              ["приватні профілі;", "вхід діру не зачинив"]),
    ]
    for cx, name, year, an_lines, an_fill, an_stroke, result in cards:
        frags.append(rect(cx - cw / 2, 78, cw, 424, fill=BG, stroke=MUTED, sw=1.6, rx=12))
        frags.append(mtext(cx, 118, [name, year], size=16, bold=True, color=INK, lh=1.35))
        frags.append(fitbox(cx - 135, 162, 270, 80, an_lines, size=14, bold=True,
                            fill=an_fill, stroke=an_stroke, sw=2.2, color=an_stroke))
        frags.append(fitbox(cx - 135, 258, 270, 80, ["AuthZ об'єкта", "✗ нема: чуже відкрите"],
                            size=14, bold=True, fill=RED_FILL, stroke=POS, sw=2.2, color=POS))
        frags.append(mtext(cx, 380, result, size=12, color=MUTED, lh=1.4))

    frags.append(text(W / 2, H - 22,
                      "AuthN мінявся: нема → є → «долатали». AuthZ об'єкта бракувало ЗАВЖДИ — тому й текло.",
                      size=13, bold=True, color=INK))

    render(os.path.join(IMG, 'breach-arc.svg'), W, H, *frags,
           title="Три витоки, той самий пропуск")


# ── Вставка proj: полювання на IDOR (харнес · чек · тест) ─────────────────────

# ── Фігура P1: автоматичний перебір + реєстр витоку ──────────────────────────
def fig_harness_sweep():
    W, H = 1020, 560
    frags = []

    # Ліворуч: власна сесія → цикл
    s, sw_, sh = textbox(175, 140, ["Сесія мешканця", "#4021 (власна)"], size=14, bold=True,
                         pad=14, fill=BLU_FILL, stroke=NEG, sw=2.2, min_w=230)
    frags.append(s)
    l, lw, lh = textbox(180, 345, ["for id = 4022 … 4030:",
                                   "GET /homes/{id}/devices",
                                   "та сама сесія на КОЖЕН id"],
                        size=13, bold=True, pad=14, fill=FILL, stroke=INK, sw=2.0, min_w=290)
    frags.append(l)
    frags.append(arrow(175, 140 + sh / 2, 180, 345 - lh / 2 - 4, color=INK, sw=1.8))

    # Праворуч: реєстр відповідей вразливого сервера
    tx, tw = 540, 440
    frags.append(text(tx + tw / 2, 96, "що вертає ВРАЗЛИВИЙ сервер", size=14, bold=True, color=POS))
    rows = [
        ("home 4022", "200", "7 пристроїв",  True),
        ("home 4023", "200", "4 пристрої",   True),
        ("home 4024", "404", "—",            False),
        ("home 4025", "200", "12 пристроїв", True),
        ("home 4026", "200", "5 пристроїв",  True),
        ("home 4027", "404", "—",            False),
    ]
    ry, rh, gap = 125, 54, 8
    for name, code, payload, leak in rows:
        fill   = RED_FILL if leak else FILL
        stroke = POS if leak else MUTED
        frags.append(rect(tx, ry, tw, rh, fill=fill, stroke=stroke, sw=2.0 if leak else 1.2, rx=8))
        frags.append(text(tx + 16, ry + rh / 2 + 5, name, size=14, bold=True, color=INK, anchor="start"))
        frags.append(text(tx + 150, ry + rh / 2 + 5, code, size=14, bold=True,
                          color=POS if leak else MUTED, anchor="start"))
        frags.append(text(tx + 214, ry + rh / 2 + 5, payload, size=13, color=INK, anchor="start"))
        if leak:
            frags.append(text(tx + tw - 14, ry + rh / 2 + 5, "← ВИТІК", size=13, bold=True,
                              color=POS, anchor="end"))
        ry += rh + gap
    ledger_mid = 125 + (rh + gap) * len(rows) / 2 - gap / 2
    frags.append(arrow(180 + lw / 2, 345, tx - 6, ledger_mid, color=POS, sw=1.8))

    frags.append(text(W / 2, H - 24,
                      "одна сесія + цикл = інвентар пристроїв цілого кварталу; жодного «злому»",
                      size=13, bold=True, color=MUTED))
    render(os.path.join(IMG, 'idor-harness-sweep.svg'), W, H, *frags,
           title="Харнес: цікавість «змінити цифру» стає автоматичним перебором")


# ── Фігура P2: 404 проти 403 як оракул існування ─────────────────────────────
def fig_404_oracle():
    W, H = 960, 590
    frags = []

    c0x, c0w = 40, 300
    c1x, c1w = 360, 240
    c2x, c2w = 620, 240

    frags.append(fitbox(c1x, 74, c1w, 56, ["403 «заборонено»", "(наївно)"], size=15, bold=True,
                        fill=ORNG_FILL, stroke=ORNG, sw=2))
    frags.append(fitbox(c2x, 74, c2w, 56, ["404 «нема»", "(правильно)"], size=15, bold=True,
                        fill=GRN_FILL, stroke=FIELD, sw=2))

    # (клас проби, відповідь-403, відповідь-404, чи-403-маяк)
    classes = [
        ("власний дім, існує",   "200",        "200", False),
        ("власний, нема такого", "404",        "404", False),
        ("ЧУЖИЙ, ІСНУЄ",         "403 ← маяк", "404", True),
        ("чужого нема зовсім",   "404",        "404", False),
    ]
    ry, rh, gap = 150, 76, 12
    for label, a403, a404, beacon in classes:
        frags.append(fitbox(c0x, ry, c0w, rh, [label], size=14, bold=True,
                            fill=BLU_FILL, stroke=MUTED, sw=1.4))
        fa = RED_FILL if beacon else GRN_FILL
        sa = POS if beacon else FIELD
        frags.append(fitbox(c1x, ry, c1w, rh, [a403], size=15, bold=True,
                            fill=fa, stroke=sa, sw=2.2, color=sa))
        frags.append(fitbox(c2x, ry, c2w, rh, [a404], size=15, bold=True,
                            fill=GRN_FILL, stroke=FIELD, sw=2.2, color=FIELD))
        ry += rh + gap

    frags.append(mtext(W / 2, H - 54, [
        "403 на «чужий, існує» — маяк: підтверджує, що дім Є, лише не твій.",
        "404 зливає «чужий існує» і «чужого нема» в одну відповідь — оракула немає."],
        size=13, bold=True, color=INK, lh=1.5))
    render(os.path.join(IMG, 'idor-404-oracle.svg'), W, H, *frags,
           title="Чому 404, а не 403: не підтверджувати існування об'єкта")


# ── Фігура P3: пропущений тест — та сама форма, що пропущений чек ─────────────
def fig_check_test_mirror():
    W, H = 1040, 560
    frags = []

    colL, colR, cw, ch = 345, 765, 320, 156
    rowTop, rowBot = 185, 385

    frags.append(text(colL, 78, "пропуск: щасливий шлях зелений", size=14, bold=True, color=POS))
    frags.append(text(colR, 78, "повно: негатив на місці", size=14, bold=True, color=FIELD))

    frags.append(text(58, rowTop, "ЧЕК", size=16, bold=True, color=INK, anchor="start"))
    frags.append(fitbox(colL - cw / 2, rowTop - ch / 2, cw, ch,
                        ["обробник без belongsTo", "власний → 200 ✓", "сусід → 200  ВИТІК"],
                        size=14, bold=True, fill=RED_FILL, stroke=POS, sw=2.2, color=INK))
    frags.append(fitbox(colR - cw / 2, rowTop - ch / 2, cw, ch,
                        ["+ belongsTo(session.userId)", "власний → 200", "сусід → 404"],
                        size=14, bold=True, fill=GRN_FILL, stroke=FIELD, sw=2.2, color=INK))

    frags.append(text(58, rowBot, "ТЕСТ", size=16, bold=True, color=INK, anchor="start"))
    frags.append(fitbox(colL - cw / 2, rowBot - ch / 2, cw, ch,
                        ["лише «власний → 200»", "зелено — а діру", "НЕ ловить"],
                        size=14, bold=True, fill=RED_FILL, stroke=POS, sw=2.2, color=INK))
    frags.append(fitbox(colR - cw / 2, rowBot - ch / 2, cw, ch,
                        ["+ «чужий існує → 404»", "+ перебір → 404", "вартовий ловить регрес"],
                        size=14, bold=True, fill=GRN_FILL, stroke=FIELD, sw=2.2, color=INK))

    frags.append(text(W / 2, H - 26,
                      "пропущений тест має ту саму форму, що пропущений чек — обидва зелені на щасливому шляху",
                      size=13, bold=True, color=MUTED))
    render(os.path.join(IMG, 'idor-check-test-mirror.svg'), W, H, *frags,
           title="Латка й вартовий: чек і тест — дзеркальна пара")


if __name__ == "__main__":
    fig_missing_gate()
    fig_escalation_axes()
    fig_ref_check_matrix()
    fig_confused_deputy_shape()
    fig_name_lineage()
    fig_breach_arc()
    fig_harness_sweep()
    fig_404_oracle()
    fig_check_test_mirror()
    print("figures written to", IMG)
