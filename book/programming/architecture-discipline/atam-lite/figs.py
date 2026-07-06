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


if __name__ == "__main__":
    fig_scenario_parts()
    fig_utility_tree()
    fig_tradeoff_point()
    fig_atam_lineage()
    fig_nine_to_four()
    fig_stop_paths()
    print("OK: figures written to", OUT)
