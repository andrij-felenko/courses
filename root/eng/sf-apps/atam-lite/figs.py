# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ACC = "#7a4ea8"    # фіолетовий — акцент рішення
ACCBG = "#f3edfb"
WARN = "#caa24a"
WARNBG = "#fff6e0"


# ── scenario-parts: шість частин сценарію якості ──────────────────────────────
# Ідея: розмита вимога «має бути швидким» нічого не важить, бо її не перевірити.
# Сценарій робить її перевірною, розкладаючи на шість named-частин: джерело →
# стимул → середовище → артефакт → відгук → міра відгуку. Показуємо конвеєр:
# зліва подія входить, справа виходить ВИМІРНА межа, під якою рішення оцінюють.

def fig_scenario_parts():
    W, H = 900, 400
    p = []

    parts = [
        ("Джерело", "хто/що\nзапустило", NEG, "#eaf0fd"),
        ("Стимул", "яка подія\nприйшла", NEG, "#eaf0fd"),
        ("Середовище", "у якому\nстані система", MUTED, "#eef1f5"),
        ("Артефакт", "яка частина\nпід ударом", MUTED, "#eef1f5"),
        ("Відгук", "що система\nробить", FIELD, "#eef6ef"),
        ("Міра", "скільки саме —\nчисло й межа", POS, "#fdecea"),
    ]
    n = len(parts)
    bw, gap = 118, 18
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    cy = 190
    bh = 92
    for i, (name, sub, col, fill) in enumerate(parts):
        x = x0 + i * (bw + gap)
        p.append(rect(x, cy - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.8, rx=10))
        p.append(text(x + bw / 2, cy - 18, name, size=12.5, color=col, bold=True))
        p.append(mtext(x + bw / 2, cy + 4, sub, size=9.5, color=INK, lh=1.25))
        if i < n - 1:
            p.append(arrow(x + bw + 2, cy, x + bw + gap - 2, cy, color=MUTED, sw=1.6))

    # вхід і вихід
    p.append(text(x0 - 4, cy - bh / 2 - 16, "подія входить →", size=10.5, color=MUTED, anchor="start", italic=True))
    lastx = x0 + (n - 1) * (bw + gap) + bw
    p.append(text(lastx + 4, cy - bh / 2 - 16, "← вимірна межа", size=10.5, color=POS, anchor="end", italic=True))

    # приклад під конвеєром
    ex = ("оператор натиснув «стоп» · на повному ході · контролер приводу · "
          "мотор зупинено · за < 200 мс")
    body, w, h = textbox(W / 2, cy + bh / 2 + 68, ex, size=11, pad=13,
                          fill=ACCBG, stroke=ACC, sw=1.6, color=INK)
    p.append(text(W / 2, cy + bh / 2 + 34, "той самий сценарій одним рядком:", size=10.5, color=ACC, bold=True))
    p.append(body)

    render(os.path.join(OUT, "scenario-parts.svg"), W, H, *p,
           title="Сценарій якості: розмите «швидко» стає вимірним")


# ── utility-tree: дерево корисності — від атрибута до сценарію з пріоритетом ────
# Ідея: не всі якості однаково важать і не всі однаково важкі. Дерево розкладає
# «якість» на атрибути → уточнення → конкретні сценарії, і кожен лист дістає
# пару (важливість, складність). Аналіз іде не по всьому дереву, а по листках
# (В,В) — важливе І складне. Показуємо дерево, листки помічені парами.

def fig_utility_tree():
    W, H = 880, 470
    p = []

    # корінь
    rootx, rooty = 120, H / 2
    body, rw, rh = textbox(rootx, rooty, "Корисність\nсистеми", size=12.5, pad=12,
                           fill=ACCBG, stroke=ACC, sw=2, color=ACC, bold=True)
    p.append(body)

    # атрибути (гілки)
    attrs = [
        ("Швидкодія", 70),
        ("Доступність", 200),
        ("Змінюваність", 330),
        ("Безпека", 415),
    ]
    ax = 340
    # листки: (текст, y, важл, склад) — пара (важливість, складність), В=високо, С=середньо
    leaves = {
        "Швидкодія": [("стоп ← 200 мс", 45, "В", "В"),
                      ("телеметрія 10 Гц", 100, "С", "Н")],
        "Доступність": [("збій давача → політ триває", 175, "В", "В"),
                        ("перезавантаж ← 3 с", 230, "С", "С")],
        "Змінюваність": [("новий давач ← 1 файл", 300, "В", "С"),
                         ("зміна протоколу ланки", 350, "Н", "С")],
        "Безпека": [("пакет-команда підписана", 415, "В", "В")],
    }

    lx = 560
    leafw = 250
    for aname, ay in attrs:
        # гілка кореня → атрибут
        p.append(line(rootx + rw / 2, rooty, ax - 74, ay, color=MUTED, sw=1.6))
        ab, aw, ah = textbox(ax, ay, aname, size=11.5, pad=9,
                             fill="#eef1f5", stroke=INK, sw=1.4, color=INK, bold=True)
        p.append(ab)
        for txt, ly, imp, cmplx in leaves[aname]:
            p.append(line(ax + aw / 2, ay, lx - 6, ly, color="#c8ccd2", sw=1.2))
            hot = (imp == "В" and cmplx == "В")
            fill = "#fdecea" if hot else BG
            stroke = POS if hot else "#c8ccd2"
            p.append(rect(lx, ly - 16, leafw, 32, fill=fill, stroke=stroke, sw=1.5 if hot else 1.1, rx=7))
            p.append(text(lx + 12, ly + 4, txt, size=10, color=INK, anchor="start"))
            tag = "(%s,%s)" % (imp, cmplx)
            tcol = POS if hot else MUTED
            p.append(text(lx + leafw - 12, ly + 4, tag, size=10, color=tcol, anchor="end", bold=hot))

    # легенда пари
    ly0 = H - 26
    p.append(text(lx, ly0, "(важливість, складність): В-високо · С-середньо · Н-низько", size=9.5, color=MUTED, anchor="start"))
    p.append(text(lx, ly0 + 16, "червоні листки (В,В) — важливе І складне: сюди йде аналіз", size=9.5, color=POS, anchor="start"))

    render(os.path.join(OUT, "utility-tree.svg"), W, H, *p,
           title="Дерево корисності: куди спрямувати обмежену увагу")


# ── tradeoff-point: точка чутливості й точка компромісу ───────────────────────
# Ідея: одне рішення тягне за собою кілька якостей — часто в різні боки. Точка
# чутливості: якість сильно залежить від параметра. Точка компромісу: той самий
# параметр тягне ДВІ якості протилежно — не можна виграти обидві. Класика:
# резервна БД. Показуємо рішення в центрі, дві стрілки: одна вгору (+), одна вниз.

def fig_tradeoff_point():
    W, H = 820, 420
    p = []

    # рішення в центрі
    dx, dy = W / 2, H / 2 + 10
    body, dw, dh = textbox(dx, dy, "Рішення:\nтримати резервну БД\nсинхронною", size=12.5, pad=14,
                           fill=ACCBG, stroke=ACC, sw=2, color=ACC, bold=True)

    # угору — надійність росте (+)
    upx, upy = W / 2, 74
    ub, uw, uh = textbox(upx, upy, "Надійність ↑", size=13, pad=12,
                         fill="#eef6ef", stroke=FIELD, sw=1.8, color=FIELD, bold=True)
    p.append(ub)
    p.append(arrow(dx, dy - dh / 2, upx, upy + uh / 2 + 2, color=FIELD, sw=2.2))
    p.append(text(dx + 96, (dy - dh / 2 + upy + uh / 2) / 2, "копія переживе\nвтрату вузла", size=9.5, color=FIELD, anchor="start"))
    # плюс на стрілці
    p.append(plus(dx - 16, (dy - dh / 2 + upy + uh / 2) / 2))

    # униз — швидкодія падає (−)
    dnx, dny = W / 2, H - 60
    nb, nw, nh = textbox(dnx, dny, "Швидкодія ↓", size=13, pad=12,
                         fill="#fdecea", stroke=POS, sw=1.8, color=POS, bold=True)
    p.append(nb)
    p.append(arrow(dx, dy + dh / 2, dnx, dny - nh / 2 - 2, color=POS, sw=2.2))
    p.append(text(dx + 96, (dy + dh / 2 + dny - nh / 2) / 2, "кожен запис жде\nпідтвердження копії", size=9.5, color=POS, anchor="start"))
    p.append(minus(dx - 16, (dy + dh / 2 + dny - nh / 2) / 2))

    p.append(body)

    # підписи зліва: що це за точки
    p.append(text(60, dy - 26, "точка чутливості:", size=11, color=INK, anchor="start", bold=True))
    p.append(mtext(60, dy - 6, "надійність СИЛЬНО\nзалежить від цього\nрішення", size=9.5, color=MUTED, anchor="start", lh=1.25))
    p.append(text(60, dy + 44, "точка компромісу:", size=11, color=ACC, anchor="start", bold=True))
    p.append(mtext(60, dy + 64, "те саме рішення тягне\nДВІ якості в різні боки", size=9.5, color=ACC, anchor="start", lh=1.25))

    render(os.path.join(OUT, "tradeoff-point.svg"), W, H, *p,
           title="Точка компромісу: одне рішення — дві якості навхрест")


# ── atam-lineage: історична лінія розвитку методу ─────────────────────────────
# Ідея (для hist-вставки): метод не з'явився готовим — виростав шарами. 1992
# Перрі-Вольф означили сам предмет (що таке архітектура). 1994 SAAM навчився
# оцінювати ОДНУ якість (змінюваність) через сценарії. 1997 ATAM ще «визріває»:
# кілька окремих аналізів атрибутів поруч. 1998 TR-008 зшиває їх у метод про
# КОМПРОМІСИ між атрибутами й дає назву. Показуємо горизонтальну вісь часу з
# чотирма віхами; підпис під кожною — що саме додав цей шар. Розставляємо з
# запасом, щоб написи не накладалися (широкі колонки, текст у своїх textbox).

def fig_atam_lineage():
    W, H = 940, 430
    p = []

    axis_y = 150
    x0, x1 = 70, W - 70
    p.append(line(x0, axis_y, x1, axis_y, color=MUTED, sw=2))
    p.append(arrow(x1 - 2, axis_y, x1 + 20, axis_y, color=MUTED, sw=2))
    p.append(text(x1 + 22, axis_y + 4, "час", size=10.5, color=MUTED, anchor="start", italic=True))

    # чотири віхи: (рік, заголовок, підпис-що-додав, колір, гарячий?)
    miles = [
        ("1992", "Перрі й Вольф",
         "означено сам предмет:\nщо таке архітектура\n(елементи · форма · чому)", MUTED, False),
        ("1994", "SAAM",
         "оцінка ОДНІЄЇ якості —\nзмінюваності — через\nсценарії, а не смак", NEG, False),
        ("1997", "ATAM визріває",
         "кілька аналізів атрибутів\nстоять поруч (звіт-97):\nще не злиті в одне", MUTED, False),
        ("1998", "ATAM (TR-008)",
         "метод про КОМПРОМІСИ\nміж атрибутами —\nстрижень і назва", ACC, True),
    ]
    n = len(miles)
    slot = (x1 - x0) / n
    for i, (year, title, sub, col, hot) in enumerate(miles):
        cx = x0 + slot * (i + 0.5)
        # точка на осі
        p.append(circle(cx, axis_y, 8 if hot else 6,
                        fill=(ACCBG if hot else BG), stroke=col, sw=2.4 if hot else 1.8))
        # рік — над віссю, у рамці
        yb, yw, yh = textbox(cx, axis_y - 54, year, size=13, pad=8,
                             fill=(ACCBG if hot else "#eef1f5"),
                             stroke=col, sw=2 if hot else 1.4, color=col, bold=True)
        p.append(yb)
        p.append(line(cx, axis_y - 54 + yh / 2, cx, axis_y - 8, color=col, sw=1.4,
                      dash=None if hot else "3 3"))
        # заголовок — під віссю
        p.append(text(cx, axis_y + 40, title, size=12.5, color=col, bold=True))
        # підпис-пояснення — ще нижче, кожен у власному просторі
        p.append(mtext(cx, axis_y + 66, sub, size=9.8, color=INK, lh=1.3))

    # нижня плашка-висновок
    concl = ("три шари: означити структуру  →  перевіряти сценаріями  →  "
             "бачити, що якості тягнуться навхрест")
    cb, cw, ch = textbox(W / 2, H - 34, concl, size=10.5, pad=11,
                         fill="#eef6ef", stroke=FIELD, sw=1.6, color=INK)
    p.append(cb)

    render(os.path.join(OUT, "atam-lineage.svg"), W, H, *p,
           title="Як виростав ATAM: від означення до методу про компроміси")


# ── nine-to-four: дев'ять кроків повного ATAM → чотири живі малої команди ──────
# Ідея: повний метод (9 кроків, 2 фази) стискається до скелета з 4 кроків. Ліворуч
# усі дев'ять, праворуч чотири; тонкі лінії показують, у який живий крок зливається
# кожен (крок 1 випадає). Виживає серце: дерево (5) і аналіз (6/8).

def fig_nine_to_four():
    W, H = 940, 560
    p = []

    # ── ліворуч: дев'ять кроків (з фазовими дужками) ──
    lx = 44
    lw = 300
    steps = [
        ("1. Презентувати метод", "drop"),
        ("2. Бізнес-драйвери", "A"),
        ("3. Презентувати архітектуру", "A"),
        ("4. Виявити підходи", "C"),
        ("5. Дерево корисності", "B"),
        ("6. Аналіз підходів", "C"),
        ("7. Штурм сценаріїв", "D"),
        ("8. Аналіз підходів (знову)", "C"),
        ("9. Презентувати результати", "D"),
    ]
    dest_col = {"A": NEG, "B": ACC, "C": FIELD, "D": WARN, "drop": MUTED}
    dest_fill = {"A": "#eaf0fd", "B": ACCBG, "C": "#eef6ef", "D": WARNBG, "drop": "#f0f1f3"}

    y0, sh, sgap = 74, 40, 8
    p.append(text(lx + lw / 2, 54, "Повний ATAM — 9 кроків, 2 фази", size=12, color=INK, bold=True))
    row_y = {}
    for i, (name, dest) in enumerate(steps):
        y = y0 + i * (sh + sgap)
        row_y[i] = y + sh / 2
        col = dest_col[dest]
        p.append(rect(lx, y, lw, sh, fill=dest_fill[dest], stroke=col, sw=1.4, rx=7))
        p.append(text(lx + 12, y + sh / 2 + 4, name, size=10.5, color=INK, anchor="start"))
        lab = "✕" if dest == "drop" else dest
        p.append(text(lx + lw - 14, y + sh / 2 + 4, lab, size=11, color=col, anchor="end", bold=True))

    # фазові дужки зліва
    p.append(line(lx - 16, row_y[1] - sh / 2, lx - 16, row_y[5] + sh / 2, color=MUTED, sw=2))
    p.append(text(lx - 22, (row_y[1] + row_y[5]) / 2, "Фаза 1", size=9.5, color=MUTED, anchor="end", italic=True))
    p.append(line(lx - 16, row_y[6] - sh / 2, lx - 16, row_y[8] + sh / 2, color=MUTED, sw=2))
    p.append(text(lx - 22, (row_y[6] + row_y[8]) / 2, "Фаза 2", size=9.5, color=MUTED, anchor="end", italic=True))

    # ── праворуч: чотири живі кроки ──
    rx = 636
    rw = 258
    live = [
        ("A", "Драйвери + структура", "синхронізувати · 15 хв", NEG, "#eaf0fd"),
        ("B", "Дерево корисності", "пріоритет (В,В) · 60 хв", ACC, ACCBG),
        ("C", "Провести сценарії", "точки, ризики · 90 хв", FIELD, "#eef6ef"),
        ("D", "Зібрати ризики й теми", "два списки · 30 хв", WARN, WARNBG),
    ]
    ry0, rh, rgap = 124, 74, 30
    p.append(text(rx + rw / 2, 54, "Мала команда — 4 живі кроки", size=12, color=INK, bold=True))
    dest_cy = {}
    for i, (tag, name, sub, col, fill) in enumerate(live):
        y = ry0 + i * (rh + rgap)
        dest_cy[tag] = y + rh / 2
        p.append(rect(rx, y, rw, rh, fill=fill, stroke=col, sw=1.9, rx=9))
        p.append(text(rx + 20, y + 28, tag, size=15, color=col, anchor="start", bold=True))
        p.append(text(rx + 46, y + 28, name, size=11.5, color=INK, anchor="start", bold=True))
        p.append(text(rx + 20, y + 53, sub, size=9.5, color=MUTED, anchor="start"))

    # лінії злиття: крок ліворуч → живий крок праворуч
    for i, (name, dest) in enumerate(steps):
        if dest == "drop":
            p.append(text(lx + lw + 16, row_y[i] + 4, "→ випадає", size=9.5, color=MUTED, anchor="start", italic=True))
            continue
        p.append(line(lx + lw + 6, row_y[i], rx - 6, dest_cy[dest], color=dest_col[dest], sw=1.1))

    render(os.path.join(OUT, "nine-to-four.svg"), W, H, *p,
           title="Дев'ять кроків ATAM стискаються в чотири")


# ── stop-paths: два архітектурні шляхи аварійного стопу ────────────────────────
# Ідея: та сама команда «стоп» — крізь спільну чергу (заручник телеметрії, ризик)
# або окремим перериванням поза чергою (гарантований час, неризик; ціна — складність).
# Матеріалізований компроміс: гарантія часу купується складнішою структурою.

def fig_stop_paths():
    W, H = 940, 440
    p = []

    # роздільник по центру
    p.append(line(W / 2, 46, W / 2, H - 18, color="#d0d4da", sw=1.4, dash="6 5"))

    # ── ліворуч: шлях 1 — крізь спільну чергу ──
    lcx = W / 4 + 20
    p.append(text(lcx, 58, "Шлях 1: крізь спільну чергу", size=12.5, color=POS, bold=True))

    b1, w1, h1 = textbox(lcx - 90, 112, "«Стоп»\nз радіо", size=11, pad=10,
                         fill="#eaf0fd", stroke=NEG, sw=1.6, color=NEG, bold=True)
    p.append(b1)
    qcells = ["телем.", "команда", "телем.", "СТОП"]
    cw, qy = 66, 186
    qtotal = len(qcells) * cw
    qx = lcx - qtotal / 2
    p.append(text(lcx, qy - 10, "черга команд (стоп у хвості)", size=9.5, color=MUTED))
    for i, cell in enumerate(qcells):
        hot = (cell == "СТОП")
        p.append(rect(qx + i * cw, qy, cw - 5, 34,
                      fill="#fdecea" if hot else "#eef1f5",
                      stroke=POS if hot else MUTED, sw=1.7 if hot else 1.2, rx=5))
        p.append(text(qx + i * cw + (cw - 5) / 2, qy + 22, cell, size=9,
                      color=POS if hot else INK, bold=hot))
    p.append(arrow(lcx - 90, 112 + h1 / 2, lcx - 90, qy - 4, color=MUTED, sw=1.6))

    b1o, w1o, h1o = textbox(lcx, 296, "Обробник зайнятий\nтелеметрією (~44 мс)", size=10, pad=11,
                            fill=FILL, stroke=MUTED, sw=1.4, color=INK)
    p.append(arrow(lcx, qy + 34 + 2, lcx, 296 - h1o / 2 - 2, color=MUTED, sw=1.6))
    p.append(b1o)
    p.append(text(lcx, 296 + h1o / 2 + 24, "стоп ЧЕКАЄ → час не гарантований", size=10.5, color=POS, bold=True))
    p.append(text(lcx, 296 + h1o / 2 + 44, "РИЗИК", size=11.5, color=POS, bold=True))

    # ── праворуч: шлях 2 — окреме переривання ──
    rcx = 3 * W / 4 - 20
    p.append(text(rcx, 58, "Шлях 2: окреме переривання", size=12.5, color=FIELD, bold=True))

    b2, w2, h2 = textbox(rcx - 100, 112, "«Стоп»\nокремий пін", size=11, pad=10,
                         fill="#eef6ef", stroke=FIELD, sw=1.6, color=FIELD, bold=True)
    p.append(b2)
    b2i, w2i, h2i = textbox(rcx, 200, "ISR стопу —\nвищий пріоритет,\nвитісняє все", size=10, pad=11,
                            fill="#eef6ef", stroke=FIELD, sw=1.9, color=FIELD, bold=True)
    p.append(arrow(rcx - 100, 112 + h2 / 2, rcx - w2i / 2 - 4, 200 - h2i / 2, color=FIELD, sw=1.8))
    p.append(b2i)
    b2m, w2m, h2m = textbox(rcx, 300, "Мотори = 0\nнегайно", size=10.5, pad=11,
                            fill=FILL, stroke=INK, sw=1.4, color=INK, bold=True)
    p.append(arrow(rcx, 200 + h2i / 2 + 2, rcx, 300 - h2m / 2 - 2, color=FIELD, sw=1.8))
    p.append(b2m)
    p.append(text(rcx, 300 + h2m / 2 + 24, "час ГАРАНТОВАНИЙ · ціна — складність", size=10.5, color=FIELD, bold=True))
    p.append(text(rcx, 300 + h2m / 2 + 44, "НЕРИЗИК", size=11.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "stop-paths.svg"), W, H, *p,
           title="Точка компромісу: два шляхи аварійного стопу")


# ── допоміжне для кривих (raw SVG, бо svgkit не має path/polyline) ─────────────
def _poly(pts, color=INK, sw=2.0, fill="none", dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, fill, color, sw, d))

def _qarrow(x1, y1, cx, cy, x2, y2, color=INK, sw=2.0):
    return ('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arrow)"/>'
            % (x1, y1, cx, cy, x2, y2, color, sw))


# ── quality-space: геометрія компромісу — межа Парето й діагональний рух ───────
# Ідея (глибший шар за базову): якості живуть у просторі, структура — точка, рішення
# — вектор. На МЕЖІ досяжного не можна рухатися прямо вгору (додати доступність
# задарма) — лише навскіс (доступність↑ ↔ затримка↑). Це й є компроміс. Чутливість
# — крутизна нахилу; компроміс — протилежні нахили за двома осями на одному параметрі.
def fig_quality_space():
    W, H = 860, 560
    p = []
    ox, oy = 150, H - 96          # початок осей
    axx, axy = 600, 400
    # осі
    p.append(arrow(ox, oy, ox + axx, oy, color=INK, sw=2))
    p.append(arrow(ox, oy, ox, oy - axy, color=INK, sw=2))
    p.append(text(ox + axx, oy + 30, "затримка запису →  (гірше)", size=11.5, color=MUTED, anchor="end"))
    p.append(text(ox - 12, oy - axy - 14, "доступність ↑  (краще)", size=11.5, color=MUTED, anchor="start"))

    # межа Парето: увігнута (дедалі менша віддача) — доступність купується затримкою
    import math
    fr = []
    for i in range(41):
        t = i / 40.0
        x = ox + 40 + t * 500
        y = oy - (40 + 350 * (t ** 0.62))
        fr.append((x, y))
    p.append(_poly(fr, color=ACC, sw=2.6))
    p.append(text(fr[-1][0] - 6, fr[-1][1] - 14, "межа досяжного (Парето)", size=11, color=ACC, anchor="end", bold=True))

    # точка A — поточна структура (на межі, t=0.22)
    tA = 0.22
    Ax = ox + 40 + tA * 500
    Ay = oy - (40 + 350 * (tA ** 0.62))
    p.append(circle(Ax, Ay, 7, fill=BG, stroke=INK, sw=2.2))
    p.append(text(Ax - 12, Ay - 12, "A: поточна структура", size=10.5, color=INK, anchor="end"))

    # точка B — синхронна репліка (t=0.66): доступність↑, затримка↑ — рух НАВСКІС
    tB = 0.66
    Bx = ox + 40 + tB * 500
    By = oy - (40 + 350 * (tB ** 0.62))
    p.append(circle(Bx, By, 7, fill=ACCBG, stroke=ACC, sw=2.4))
    p.append(arrow(Ax, Ay, Bx, By, color=FIELD, sw=2.2))
    p.append(text(Bx + 14, By + 4, "B: синхронна репліка", size=10.5, color=FIELD, anchor="start", bold=True))
    p.append(text(Bx + 14, By + 22, "доступність↑ · затримка↑", size=9.5, color=FIELD, anchor="start"))

    # бажаний рух прямо вгору — за межу (недосяжно задарма)
    Wx, Wy = Ax, By - 6
    p.append(line(Ax, Ay, Wx, Wy, color=POS, sw=1.8, dash="5 5"))
    p.append(circle(Wx, Wy, 5, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(Wx - 12, Wy - 8, "хотілося б: лише доступність↑", size=10, color=POS, anchor="end"))
    p.append(text(Wx - 12, Wy + 8, "— за межею досяжного", size=10, color=POS, anchor="end"))

    render(os.path.join(OUT, "quality-space.svg"), W, H, *p,
           title="Простір якостей: на межі доступність купується лише затримкою")


# ── priority-exposure: (важливість × складність) як експозиція ризику E = p·V ───
# Ідея: фільтр уваги базової статті має кількісний хребет. Важливість ≈ ціна на кону
# V, складність ≈ ймовірність, що структура НЕ витягне, p. Очікувана експозиція
# E = p·V. Сітка 3×3 гаряча в куті (В,В): туди й іде бюджет аналізу, бо там майже
# вся ΣE. Показуємо сітку-теплокарту з підписаними осями поза клітинами.
def fig_priority_exposure():
    W, H = 740, 560
    p = []
    n = 3
    cell = 132
    gx, gy = 190, 90            # лівий-верхній кут сітки
    labs = ["Н", "С", "В"]
    # тепло за добутком рангів (1..3)×(1..3)=1..9
    heat = {
        1: "#eef1f5", 2: "#f6f0e6", 3: "#fdeede",
        4: "#fbe6d2", 6: "#f7cdb0", 9: "#e79a72",
    }
    for iy in range(n):           # iy: 0 внизу (Н важл) … 2 вгорі (В важл)
        for ix in range(n):       # ix: 0 ліворуч (Н склад) … 2 праворуч (В склад)
            imp = iy + 1
            cmp_ = ix + 1
            e = imp * cmp_
            x = gx + ix * cell
            y = gy + (n - 1 - iy) * cell
            hot = (imp == 3 and cmp_ == 3)
            fill = heat.get(e, "#f6f0e6")
            p.append(rect(x, y, cell - 8, cell - 8, fill=fill,
                          stroke=(ACC if hot else "#c8ccd2"), sw=2.4 if hot else 1.2, rx=8))
            p.append(text(x + (cell - 8) / 2, y + (cell - 8) / 2 - 6, "E = %d" % e,
                          size=15 if hot else 12.5, color=(ACC if hot else INK), bold=hot))
            if hot:
                p.append(text(x + (cell - 8) / 2, y + (cell - 8) / 2 + 18, "сюди — аналіз",
                              size=10, color=ACC, bold=True))
            elif e == 1:
                p.append(text(x + (cell - 8) / 2, y + (cell - 8) / 2 + 18, "не чіпаємо",
                              size=9.5, color=MUTED))
    # осі (підписи винесено з запасом, щоб не накладались на клітини)
    p.append(text(78, gy + n * cell / 2 - 4, "важливість", size=12, color=INK, anchor="middle", bold=True))
    p.append(text(78, gy + n * cell / 2 + 14, "(ціна V)", size=9.5, color=MUTED, anchor="middle"))
    for iy in range(n):
        y = gy + (n - 1 - iy) * cell + (cell - 8) / 2
        p.append(text(gx - 42, y + 4, labs[iy], size=12.5, color=MUTED, bold=True))
    p.append(text(gx + n * cell / 2 - 4, gy + n * cell + 38, "складність  (ймовірність недотягнути p)",
                  size=12, color=INK, bold=True))
    for ix in range(n):
        x = gx + ix * cell + (cell - 8) / 2
        p.append(text(x, gy + n * cell + 12, labs[ix], size=12.5, color=MUTED, bold=True))

    render(os.path.join(OUT, "priority-exposure.svg"), W, H, *p,
           title="Куди йде аналіз: очікувана експозиція E = важливість · складність")


# ── spiral-evaluation: оцінювання як спіраль, що передає естафету експерименту ──
# Ідея (глибший шар за hist-вставку): ATAM — не разова експертиза, а цикл: запропонувати
# → проаналізувати → побачити ризики → уточнити → знову. Кожен виток дешевий і НА ПАПЕРІ.
# Вихід: коли найдешевша наступна інформація вже емпірична — будуємо найменший експеримент.
def fig_spiral_evaluation():
    W, H = 860, 560
    p = []
    cx, cy = 430, 230
    # чотири станції циклу
    top, r = (cx, 96), 150
    st = {
        "n": textbox(cx, 96, "Структура-\nкандидат", size=11, pad=11, fill=ACCBG, stroke=ACC, sw=1.9, color=ACC, bold=True),
        "e": textbox(cx + 210, cy, "Аналіз:\nсценарії крізь\nструктуру", size=11, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.9, color=FIELD, bold=True),
        "s": textbox(cx, 372, "Ризики й точки\nкомпромісу", size=11, pad=11, fill="#fdecea", stroke=POS, sw=1.9, color=POS, bold=True),
        "w": textbox(cx - 210, cy, "Уточнити\nструктуру", size=11, pad=11, fill=WARNBG, stroke=WARN, sw=1.9, color=WARN, bold=True),
    }
    # центр
    cbody, cw, ch = textbox(cx, cy, "розуміння дозріває\n· нічого не збудовано ·", size=10, pad=10,
                            fill=BG, stroke=MUTED, sw=1.3, color=MUTED)
    # криві-стрілки за годинниковою: n→e→s→w→n (контроль назовні)
    p.append(_qarrow(cx + 60, 96, cx + 210, 150, cx + 210, cy - 40, color=INK, sw=1.8))
    p.append(_qarrow(cx + 210, cy + 40, cx + 210, 372, cx + 66, 372, color=INK, sw=1.8))
    p.append(_qarrow(cx - 66, 372, cx - 210, 372, cx - 210, cy + 40, color=INK, sw=1.8))
    p.append(_qarrow(cx - 210, cy - 40, cx - 210, 96, cx - 62, 96, color=INK, sw=1.8))
    p.append(cbody)
    for k in ("n", "e", "s", "w"):
        p.append(st[k][0])

    # вихід до експерименту
    ex, exy = cx, 476
    eb, ew, eh = textbox(ex, exy, "коли найдешевша наступна інформація — вже емпірична:\nбудуй найменший експеримент (walking skeleton), не аналізуй далі",
                         size=10.5, pad=12, fill="#eef1f5", stroke=NEG, sw=1.7, color=INK)
    p.append(arrow(cx, 372 + st["s"][2] / 2 + 2, ex, exy - eh / 2 - 2, color=NEG, sw=2))
    p.append(text(cx + 14, (372 + st["s"][2] / 2 + exy - eh / 2) / 2 + 4, "вихід", size=10, color=NEG, anchor="start", italic=True))
    p.append(eb)

    render(os.path.join(OUT, "spiral-evaluation.svg"), W, H, *p,
           title="Оцінювання — спіраль на папері, що вчасно передає естафету експерименту")


# ── utility-response: неперервна крива корисності проти порога «так/ні» ─────────
# Ідея: сценарій дає ПОРІГ (так/ні), але корисність відгуку насправді неперервна й
# нелінійна — плато, потім обрив, потім дно. Поріг — лише одна точка кривої. На
# неперервній кривій уже можна рахувати вигоду й ROI (місток до економіки/CBAM).
def fig_utility_response():
    W, H = 860, 500
    p = []
    ox, oy = 110, H - 90
    axx, axy = 660, 350
    p.append(arrow(ox, oy, ox + axx, oy, color=INK, sw=2))
    p.append(arrow(ox, oy, ox, oy - axy, color=INK, sw=2))
    p.append(text(ox + axx, oy + 30, "затримка p99, мс →", size=11.5, color=MUTED, anchor="end"))
    p.append(text(ox - 6, oy - axy - 14, "корисність", size=11.5, color=MUTED, anchor="start"))

    import math
    x0, k = 200.0, 0.022         # поріг-центр обриву й крутизна
    def U(ms):
        return 100.0 / (1.0 + math.exp(k * (ms - x0)))
    def px(ms):
        return ox + (ms / 400.0) * axx
    def py(u):
        return oy - (u / 100.0) * axy
    curve = [(px(ms), py(U(ms))) for ms in range(0, 401, 8)]
    p.append(_poly(curve, color=ACC, sw=2.8))

    # поріг сценарію «так/ні» на 200 мс
    p.append(line(px(200), oy, px(200), py(U(200)), color=POS, sw=1.6, dash="5 4"))
    p.append(text(px(200), oy + 22, "поріг сценарію (так/ні)", size=10.5, color=POS, bold=True))

    # дві робочі точки: A (варіант дешевший, 150 мс) і B (дорожчий, 90 мс)
    for ms, name, u_dy in [(150, "A", -18), (90, "B", -18)]:
        u = U(ms)
        p.append(circle(px(ms), py(u), 6, fill=ACCBG, stroke=ACC, sw=2.2))
        p.append(text(px(ms) - 10, py(u) + u_dy, "%s (%d мс, U≈%d)" % (name, ms, round(u)),
                      size=10, color=INK, anchor="end"))

    # підпис зони
    p.append(text(px(40), 48, "плато: майже байдуже", size=10, color=MUTED, anchor="start"))
    p.append(text(px(322), py(10) - 6, "дно: втрата вигоди", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "utility-response.svg"), W, H, *p,
           title="Крива корисності: поріг «так/ні» — лише одна точка неперервної кривої")


# ── product-not-sum: чому експозиція — ДОБУТОК p·V, а не сума ───────────────────
# Ідея (глибший шар за priority-exposure): E=p·V — це очікувана втрата (ціна × шанс),
# а не евристика. Сума p+V безрозмірно недоладна (додає ціну до ймовірності) і не
# зануляється, коли один множник ~0. Гіперболи E=const тиснуться в кут (В,В); дві
# точки на СПІЛЬНІЙ лінії суми мають різне E — сума їх не розрізняє, добуток розрізняє.
def fig_product_not_sum():
    W, H = 880, 590
    p = []
    ox, oy = 150, H - 120
    axx, axy = 520, 400
    p.append(arrow(ox, oy, ox + axx + 26, oy, color=INK, sw=2))
    p.append(arrow(ox, oy, ox, oy - axy - 22, color=INK, sw=2))
    p.append(text(ox + axx + 22, oy + 32, "ймовірність провалу  p →", size=11.5, color=MUTED, anchor="end"))
    p.append(text(ox - 6, oy - axy - 16, "ціна провалу  V ↑", size=11.5, color=MUTED, anchor="start"))
    p.append(text(ox, oy + 20, "0", size=10, color=MUTED))
    p.append(text(ox + axx, oy + 20, "1", size=10, color=MUTED))
    p.append(text(ox - 18, oy + 4, "0", size=10, color=MUTED))
    p.append(text(ox - 18, oy - axy + 4, "1", size=10, color=MUTED))

    def X(pp): return ox + pp * axx
    def Y(vv): return oy - vv * axy

    # ізо-експозиційні гіперболи E=p·V=const, від холодного до гарячого
    for e, col in [(0.1, "#8f99a6"), (0.25, "#d6a15e"), (0.5, "#e0793a"), (0.75, POS)]:
        pts = []
        i = 0
        while True:
            pp = e + i * 0.01
            if pp > 1.0:
                break
            vv = e / pp
            if vv <= 1.0:
                pts.append((X(pp), Y(vv)))
            i += 1
        if pts:
            p.append(_poly(pts, color=col, sw=2.2))
        p.append(text(ox + axx + 12, Y(e) + 4, "E=%.2f" % e, size=10, color=col, anchor="start"))

    # ізо-сумна лінія p+V=1 (проходить через S₁ і S₂)
    p.append(line(X(0.02), Y(0.98), X(0.98), Y(0.02), color=NEG, sw=1.8, dash="6 5"))
    p.append(text(X(0.045), Y(0.58), "лінія суми  p + V = const", size=10, color=NEG, anchor="start"))

    def dot(pp, vv, col, r, fillc):
        p.append(circle(X(pp), Y(vv), r, fill=fillc, stroke=col, sw=2.4))
    dot(0.9, 0.1, NEG, 7, "#eaf0fd")   # S₁ — напевно провалиться, але ціна ≈ 0
    dot(0.5, 0.5, NEG, 7, "#eaf0fd")   # S₂ — помірні обидва
    dot(0.9, 0.9, POS, 9, "#fdecea")   # S₃ — дорого І ймовірно (кут В,В)
    p.append(text(X(0.9), Y(0.1) + 26, "S₁: E = 0.09", size=10.5, color=INK))
    p.append(text(X(0.5) - 12, Y(0.5) + 28, "S₂: E = 0.25", size=10.5, color=INK))
    p.append(text(X(0.9) + 14, Y(0.9) - 2, "S₃ (кут В,В): E = 0.81", size=10.5, color=POS, anchor="start", bold=True))

    cb, cw, ch = textbox(W / 2, H - 34,
        "S₁ і S₂ — на спільній лінії суми (p+V=1), але E різниться майже втричі.\n"
        "Сума не розрізняє ризики; добуток розрізняє — і вся вага стягується в кут (В,В).",
        size=10.5, pad=11, fill="#eef1f5", stroke=MUTED, sw=1.5, color=INK)
    p.append(cb)

    render(os.path.join(OUT, "product-not-sum.svg"), W, H, *p,
           title="Чому добуток, а не сума: E = p·V гасне, щойно один множник малий")


# ── response-quantiles: міра відгуку — поріг на розподілі, а не на крапці ───────
# Ідея: відгук — не число, а розподіл. «< 200 мс» недоказане, доки не сказано, ПРО
# ЯКУ статистику йдеться. Та сама система вкладається за avg/p95 і провалює за
# p99/max. Вибір статистики = скільки хвоста свідомо жертвуєш (форма Value-at-Risk).
def fig_response_quantiles():
    import math
    W, H = 900, 470
    p = []
    ox, oy = 90, H - 100
    axx, axy = 740, 280
    p.append(arrow(ox, oy, ox + axx + 24, oy, color=INK, sw=2))
    p.append(arrow(ox, oy, ox, oy - axy - 20, color=INK, sw=2))
    p.append(text(ox + axx + 20, oy + 32, "затримка відгуку, мс →", size=11.5, color=MUTED, anchor="end"))
    p.append(text(ox - 6, oy - axy - 16, "щільність запитів", size=11.5, color=MUTED, anchor="start"))

    MS = 500.0
    def X(ms): return ox + (ms / MS) * axx
    mu, sig = 4.44, 0.62
    def pdf(ms):
        if ms <= 0:
            return 0.0
        return (1.0 / (ms * sig * math.sqrt(2 * math.pi))) * math.exp(-((math.log(ms) - mu) ** 2) / (2 * sig * sig))
    peak = max(pdf(ms) for ms in range(1, int(MS) + 1))
    def Y(ms): return oy - (pdf(ms) / peak) * (axy * 0.82)

    curve = [(X(ms), Y(ms)) for ms in range(1, int(MS) + 1, 3)]

    T = 200
    tail = [(X(T), oy)] + [(X(ms), Y(ms)) for ms in range(T, int(MS) + 1, 3)] + [(X(MS), oy)]
    p.append(_poly(tail, color="none", sw=0.0, fill="#fbe0da"))
    p.append(_poly(curve, color=ACC, sw=2.6))

    # поріг T=200
    ttop = oy - axy * 0.92
    p.append(line(X(T), oy, X(T), ttop, color=POS, sw=2.2))
    p.append(text(X(T), ttop - 14, "поріг T = 200 мс", size=11, color=POS, bold=True))

    # квантилі — тонкі лінії + підпис ВИЩЕ верху лінії
    for ms, col, lab, topy in [(90, FIELD, "avg 90", 150), (180, NEG, "p95 180", 122),
                               (320, "#b23b6f", "p99 320", 150)]:
        p.append(line(X(ms), oy, X(ms), topy + 12, color=col, sw=1.5, dash="4 4"))
        p.append(text(X(ms), topy, lab, size=10.5, color=col, bold=True))

    p.append(text(X(MS) - 4, oy - 34, "хвіст → max 900 мс", size=10, color=MUTED, anchor="end", italic=True))

    cb, cw, ch = textbox(W / 2, H - 30,
        "Та сама система, та сама межа «< 200 мс»: вкладається за avg і p95, провалює за p99 і max.\n"
        "Який бік розподілу тримати під T — і є вибір статистики: скільки хвоста ти свідомо жертвуєш.",
        size=10.5, pad=11, fill="#eef1f5", stroke=MUTED, sw=1.5, color=INK)
    p.append(cb)

    render(os.path.join(OUT, "response-quantiles.svg"), W, H, *p,
           title="Міра відгуку — поріг на розподілі: avg/p95/p99/max дають різний вердикт")


# ── equimarginal: оптимум CBAM — рівність граничних віддач на межі ─────────────
# Ідея: під бюджетом оптимум НЕ там, де абсолютна вигода найбільша, а там, де гранична
# вигода на гривню зрівнюється між варіантами. «Рівень води» λ — тіньова ціна бюджету;
# фінансуємо кожен варіант, поки його спадна гранична крива вища за λ. Правило рівних
# граничних віддач (Госсен, 1854; те саме, що умова множника Лагранжа).
def fig_equimarginal():
    W, H = 900, 520
    p = []
    ox, oy = 110, H - 100
    axx, axy = 680, 330
    p.append(arrow(ox, oy, ox + axx + 24, oy, color=INK, sw=2))
    p.append(arrow(ox, oy, ox, oy - axy - 20, color=INK, sw=2))
    p.append(text(ox + axx + 20, oy + 38, "сукупна витрата (бюджет) →", size=11.5, color=MUTED, anchor="end"))
    p.append(text(ox - 6, oy - axy - 16, "гранична вигода на одиницю витрати ↑", size=11.5, color=MUTED, anchor="start"))

    CMAX, MMAX = 10.0, 10.0
    def X(c): return ox + (c / CMAX) * axx
    def Y(m): return oy - (m / MMAX) * axy
    def mbA(c): return 10.0 - 1.4 * c
    def mbB(c): return 7.0 - 0.9 * c
    lam = 4.0
    cA = (10.0 - lam) / 1.4
    cB = (7.0 - lam) / 0.9
    cA0, cB0 = 10.0 / 1.4, 7.0 / 0.9

    # заливка вигоди (площа під граничною кривою до розподілу)
    fa = [(X(0), oy)]
    c = 0.0
    while c <= cA + 1e-9:
        fa.append((X(c), Y(mbA(c)))); c += 0.1
    fa += [(X(cA), oy)]
    p.append(_poly(fa, color="none", sw=0.0, fill="#eaf0fd"))
    fb = [(X(0), oy)]
    c = 0.0
    while c <= cB + 1e-9:
        fb.append((X(c), Y(mbB(c)))); c += 0.1
    fb += [(X(cB), oy)]
    p.append(_poly(fb, color="none", sw=0.0, fill="#fff1d6"))

    # граничні криві (лінійні спадні)
    p.append(line(X(0), Y(10), X(cA0), Y(0), color=NEG, sw=2.6))
    p.append(line(X(0), Y(7), X(cB0), Y(0), color=WARN, sw=2.6))

    # рівень води λ
    p.append(line(X(0), Y(lam), X(9.4), Y(lam), color=INK, sw=1.4, dash="6 5"))
    p.append(text(X(9.5), Y(lam) + 4, "λ = 4", size=11, color=INK, anchor="start", bold=True))

    # точки рівності на межі + вертикалі-розподіли
    p.append(line(X(cA), Y(lam), X(cA), oy, color=NEG, sw=1.4, dash="3 3"))
    p.append(line(X(cB), Y(lam), X(cB), oy, color=WARN, sw=1.4, dash="3 3"))
    p.append(circle(X(cA), Y(lam), 5, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(circle(X(cB), Y(lam), 5, fill="#fff1d6", stroke=WARN, sw=2))
    p.append(text(X(cA), oy + 22, "A: ≈4.3", size=10, color=NEG, bold=True))
    p.append(text(X(cB), oy + 22, "B: ≈3.3", size=10, color=WARN, bold=True))

    # легенда (верх-право, де криві вже низько)
    lx, ly = X(6.2), Y(9.4)
    p.append(line(lx, ly, lx + 26, ly, color=NEG, sw=2.6))
    p.append(text(lx + 32, ly + 4, "варіант A", size=10.5, color=NEG, anchor="start", bold=True))
    p.append(line(lx, ly + 24, lx + 26, ly + 24, color=WARN, sw=2.6))
    p.append(text(lx + 32, ly + 28, "варіант B", size=10.5, color=WARN, anchor="start", bold=True))

    # виноска рівності
    p.append(mtext(X(6.05), Y(6.2), "на межі гранична\nвіддача обох = λ\n(рівні граничні\nвіддачі, Госсен)",
                   size=10, color=INK, anchor="middle", lh=1.3))

    cb, cw, ch = textbox(W / 2, H - 24,
        "Фінансуємо кожен варіант, поки його гранична вигода вища за λ; спиняємось, коли впала до λ.\n"
        "В оптимумі гранична віддача на гривню однакова для всіх варіантів — це і є λ, тіньова ціна бюджету.",
        size=10.5, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.5, color=INK)
    p.append(cb)

    render(os.path.join(OUT, "equimarginal.svg"), W, H, *p,
           title="Оптимум CBAM: гранична вигода на гривню зрівнюється між варіантами")


# ── staleness-window: вікно застарілості читання з репліки vs read-your-writes ─
# Ідея (для proj-вставки про бекенд-компроміс): після запису на основну репліка
# ще ЛАГ мілісекунд віддає старе. Читання в це вікно бачить старе (✗). Read-your-
# writes натомість пришпилює читання до основної на вікно W — те саме раннє
# читання стає свіжим (✓). Дві доріжки часу спільного t0; смуга лага (червона)
# проти вікна W (зелене). Написи розставлено з запасом, поза чужими лініями.
def fig_staleness_window():
    W, H = 980, 560
    p = []
    t0 = 235
    catchup = 560          # репліка наздогнала
    wend = 615             # кінець вікна W
    axL, axR = 120, 880
    r1, r2 = 345, 700      # раннє й пізнє читання

    # t0 вертикаль через обидві доріжки
    p.append(line(t0, 92, t0, 470, color=INK, sw=1.5, dash="4 4"))
    tb, tw, th = textbox(t0, 74, "t0: запис підтверджено", size=11, pad=8,
                         fill=ACCBG, stroke=ACC, sw=1.6, color=ACC, bold=True)
    p.append(tb)

    # ── доріжка A: читання з репліки ──
    ay = 200
    p.append(text(axL, 128, "Шлях 1: читання з репліки", size=12.5, color=POS, anchor="start", bold=True))
    p.append(line(axL, ay, axR, ay, color=MUTED, sw=1.5))
    p.append(arrow(axR, ay, axR + 18, ay, color=MUTED, sw=1.5))
    p.append(text(axR + 20, ay + 4, "час", size=10, color=MUTED, anchor="start", italic=True))
    # смуга застарілості (над лінією)
    p.append(rect(t0, ay - 34, catchup - t0, 30, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    p.append(text((t0 + catchup) / 2, ay - 15, "лаг: репліка ще НЕ має запису", size=10, color=POS, bold=True))
    # репліка наздогнала (тік)
    p.append(line(catchup, ay - 38, catchup, ay + 6, color=FIELD, sw=1.5))
    p.append(text(catchup + 8, ay - 44, "репліка наздогнала", size=9.5, color=FIELD, anchor="start"))
    # читання знизу вгору до осі
    p.append(arrow(r1, ay + 52, r1, ay + 3, color=POS, sw=2))
    p.append(text(r1, ay + 70, "✗ старе", size=11, color=POS, bold=True))
    p.append(arrow(r2, ay + 52, r2, ay + 3, color=FIELD, sw=2))
    p.append(text(r2, ay + 70, "✓ свіже", size=11, color=FIELD, bold=True))

    # ── доріжка B: read-your-writes ──
    by = 400
    p.append(text(axL, 328, "Шлях 2: read-your-writes — пришпилити до основної на W", size=12.5, color=FIELD, anchor="start", bold=True))
    p.append(line(axL, by, axR, by, color=MUTED, sw=1.5))
    p.append(arrow(axR, by, axR + 18, by, color=MUTED, sw=1.5))
    p.append(text(axR + 20, by + 4, "час", size=10, color=MUTED, anchor="start", italic=True))
    # вікно W (над лінією)
    p.append(rect(t0, by - 34, wend - t0, 30, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=4))
    p.append(text((t0 + wend) / 2, by - 15, "вікно W: читання → на ОСНОВНУ", size=10, color=FIELD, bold=True))
    p.append(line(wend, by - 38, wend, by + 6, color=MUTED, sw=1.4, dash="3 3"))
    p.append(text(wend + 8, by - 44, "далі знову репліки", size=9.5, color=MUTED, anchor="start"))
    # те саме раннє читання — тепер свіже
    p.append(arrow(r1, by + 52, r1, by + 3, color=FIELD, sw=2))
    p.append(text(r1, by + 70, "✓ свіже (з основної)", size=11, color=FIELD, bold=True))

    # нижня плашка — масштаб лага
    note = "лаг реплікації: p50 ≈ 20 мс · p99 ≈ 250 мс · хвіст 2…30 с — саме хвіст ламає гарантію"
    nb, nw, nh = textbox(W / 2, H - 30, note, size=10, pad=10,
                         fill=FILL, stroke=MUTED, sw=1.3, color=INK)
    p.append(nb)

    render(os.path.join(OUT, "staleness-window.svg"), W, H, *p,
           title="Вікно застарілості: коли читання з репліки не бачить власного запису")


# ── read-paths-web: два шляхи читання на бекенді (реплікою vs read-your-writes) ─
# Ідея: та сама пара «зберегти → перечитати», два архітектурні шляхи. Ліворуч усі
# читання з реплік (латентність блиск, свіжість — заручник лага, РИЗИК). Праворуч
# read-your-writes: гарячі читання → основна, холодні → репліки, з числами
# навантаження (обидві половини міри пройдено). Унизу названо точку компромісу:
# вікно W тягне свіжість проти навантаження на основну.
def fig_read_paths_web():
    W, H = 1000, 580
    p = []
    p.append(line(W / 2, 46, W / 2, 508, color="#d0d4da", sw=1.4, dash="6 5"))

    # ── ліворуч: шлях 1 — усі читання з реплік ──
    lcx = 250
    p.append(text(lcx, 58, "Шлях 1: усі читання з реплік", size=12.5, color=POS, bold=True))
    g1, gw1, gh1 = textbox(lcx, 104, "GET /profile", size=11.5, pad=10,
                           fill="#eaf0fd", stroke=NEG, sw=1.6, color=NEG, bold=True)
    rp, rpw, rph = textbox(lcx, 178, "пул реплік ×4", size=11.5, pad=11,
                           fill=FILL, stroke=MUTED, sw=1.5, color=INK, bold=True)
    p.append(arrow(lcx, 104 + gh1 / 2, lcx, 178 - rph / 2 - 2, color=MUTED, sw=1.7))
    p.append(g1)
    p.append(rp)
    n1, n1w, n1h = textbox(lcx, 270, "12 500 читань/с на репліку\n(< 20 000 — з запасом)\np99 ≈ 8 мс",
                           size=10.5, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.5, color=INK)
    p.append(arrow(lcx, 178 + rph / 2, lcx, 270 - n1h / 2 - 2, color=MUTED, sw=1.7))
    p.append(n1)
    v1, v1w, v1h = textbox(lcx, 382, "латентність ✓\nсвіжість ✗ — заручник лага",
                           size=11, pad=11, fill="#fdecea", stroke=POS, sw=1.7, color=INK)
    p.append(arrow(lcx, 270 + n1h / 2, lcx, 382 - v1h / 2 - 2, color=MUTED, sw=1.7))
    p.append(v1)
    p.append(text(lcx, 382 + v1h / 2 + 28, "РИЗИК: застаріле під піком", size=11.5, color=POS, bold=True))

    # ── праворуч: шлях 2 — read-your-writes ──
    rcx = 750
    p.append(text(rcx, 58, "Шлях 2: read-your-writes", size=12.5, color=FIELD, bold=True))
    g2, gw2, gh2 = textbox(rcx, 104, "GET /profile", size=11.5, pad=10,
                           fill="#eaf0fd", stroke=NEG, sw=1.6, color=NEG, bold=True)
    d2, d2w, d2h = textbox(rcx, 176, "писав < W тому?", size=11, pad=10,
                           fill=ACCBG, stroke=ACC, sw=1.7, color=ACC, bold=True)
    p.append(arrow(rcx, 104 + gh2 / 2, rcx, 176 - d2h / 2 - 2, color=MUTED, sw=1.7))
    p.append(g2)
    p.append(d2)
    prx, rex = rcx - 105, rcx + 105
    pb, pbw, pbh = textbox(prx, 266, "ОСНОВНА\nсвіжо", size=10.5, pad=10,
                           fill="#eef6ef", stroke=FIELD, sw=1.7, color=FIELD, bold=True)
    rb, rbw, rbh = textbox(rex, 266, "репліки\nдешево", size=10.5, pad=10,
                           fill=FILL, stroke=MUTED, sw=1.5, color=INK, bold=True)
    p.append(arrow(rcx - 20, 176 + d2h / 2, prx, 266 - pbh / 2 - 2, color=FIELD, sw=1.6))
    p.append(arrow(rcx + 20, 176 + d2h / 2, rex, 266 - rbh / 2 - 2, color=MUTED, sw=1.6))
    p.append(pb)
    p.append(rb)
    n2, n2w, n2h = textbox(rcx, 372, "основна: 10 000/с (< 40 000)\nрепліки: 11 250/с кожна\np99 ≈ 8–12 мс",
                           size=10.5, pad=11, fill="#eef6ef", stroke=FIELD, sw=1.5, color=INK)
    p.append(arrow(prx, 266 + pbh / 2, rcx - 40, 372 - n2h / 2 - 2, color=MUTED, sw=1.3))
    p.append(arrow(rex, 266 + rbh / 2, rcx + 40, 372 - n2h / 2 - 2, color=MUTED, sw=1.3))
    p.append(n2)
    p.append(text(rcx, 372 + n2h / 2 + 30, "свіжо ✓ · латентність ✓ — НЕРИЗИК, поки лаг < W",
                  size=11, color=FIELD, bold=True))

    # ── точка компромісу — плашка внизу по центру ──
    tbx, tbw, tbh = textbox(W / 2, 545, "точка компромісу — вікно W:   свіжість ↕ навантаження на основну",
                            size=11, pad=12, fill=ACCBG, stroke=ACC, sw=1.8, color=ACC, bold=True)
    p.append(tbx)

    render(os.path.join(OUT, "read-paths-web.svg"), W, H, *p,
           title="Два шляхи читання: реплікою (дешево, застаріло) чи read-your-writes")


if __name__ == "__main__":
    fig_scenario_parts()
    fig_utility_tree()
    fig_tradeoff_point()
    fig_atam_lineage()
    fig_nine_to_four()
    fig_stop_paths()
    fig_quality_space()
    fig_priority_exposure()
    fig_spiral_evaluation()
    fig_utility_response()
    fig_product_not_sum()
    fig_response_quantiles()
    fig_equimarginal()
    fig_staleness_window()
    fig_read_paths_web()
    print("OK: figures written to", OUT)
