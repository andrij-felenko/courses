# -*- coding: utf-8 -*-
"""Фігури до статті «Математична індукція» та вставки hist-induction-history.
Запуск:  python figs.py   → пише SVG у ./img/
  стаття: dominoes, anatomy, wellorder
  вставка hist: induction-timeline, karaji-vs-modern
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#eaf7ef"
REDFILL = "#fdecea"
ROW = "#f4f6f8"


# ── 1. Доміно: база штовхає, крок передає, падають усі ───────────────────────
def fig_dominoes():
    W, H = 940, 400
    f = [text(W / 2, 30, "Дві частини валять увесь нескінченний ряд", size=18, bold=True),
         text(W / 2, 52, "база штовхає першу кісточку · крок гарантує, що кожна валить наступну",
              size=12, color=MUTED, italic=True)]

    dom_y, dom_h, dom_w = 175, 72, 64
    centers = [130, 300, 470, 640, 810]
    labels = ["P(1)", "P(2)", "P(3)", "P(4)", "P(5)"]

    # горизонтальні стрілки «крок» між кісточками
    for i in range(len(centers) - 1):
        x1 = centers[i] + dom_w / 2 + 8
        x2 = centers[i + 1] - dom_w / 2 - 8
        f.append(arrow(x1, dom_y + dom_h / 2, x2, dom_y + dom_h / 2, color=INK, sw=2.0))
        f.append(text((x1 + x2) / 2, dom_y + dom_h / 2 - 12, "крок", size=11, color=MUTED, italic=True))

    # кісточки
    for i, (cx, lab) in enumerate(zip(centers, labels)):
        x = cx - dom_w / 2
        first = (i == 0)
        f.append(rect(x, dom_y, dom_w, dom_h, fill=(GREENFILL if first else FILL),
                      stroke=(FIELD if first else LINE), sw=(2.4 if first else 1.5), rx=8))
        f.append(text(cx, dom_y + dom_h / 2 + 6, lab, size=16, bold=True,
                      color=(FIELD if first else INK)))

    # багатокрапка «і так усі»
    f.append(text(880, dom_y + dom_h / 2 + 6, "…", size=24, bold=True))
    f.append(text(880, dom_y + dom_h + 26, "усі", size=12, color=MUTED, italic=True))

    # база: вертикальна стрілка-поштовх згори в P(1)
    f.append(arrow(130, dom_y - 48, 130, dom_y - 6, color=FIELD, sw=2.6))
    f.append(text(130, dom_y - 58, "база: штовхаємо першу", size=12.5, bold=True, color=FIELD))

    # два попередження знизу
    by = 320
    f.append(fitbox(70, by, 380, 52,
                    "Прибрати БАЗУ — ніщо не почнеться:\nкроки справджуються вхолосту.",
                    size=12.5, fill=ROW, stroke=MUTED, sw=1.3, color=INK))
    f.append(fitbox(490, by, 380, 52,
                    "Пропуск у КРОЦІ хоч в одному місці —\nланцюг обірветься саме там.",
                    size=12.5, fill=ROW, stroke=MUTED, sw=1.3, color=INK))
    render(os.path.join(IMG, "dominoes.svg"), W, H, *f)


# ── 2. Будова доказу індукцією (з прикладом суми) ────────────────────────────
def fig_anatomy():
    W, H = 880, 470
    f = [text(W / 2, 30, "Скелет будь-якого доказу індукцією", size=18, bold=True),
         text(W / 2, 52, "ліворуч — роль частини, праворуч — вона ж на прикладі суми 1+2+…+n = n(n+1)/2",
              size=12, color=MUTED, italic=True)]

    bx, bw = 120, 640
    box_h, gap = 76, 22
    top = 84
    stages = [
        ("БАЗА", "перевіряємо P(1) прямо", "1 = 1·2/2 = 1  ✓", FIELD, GREENFILL),
        ("ПРИПУЩЕННЯ", "нехай P(k) правда — для довільного k", "1 + 2 + … + k = k(k+1)/2", NEG, "#eaf0fd"),
        ("КРОК", "звідси виводимо P(k+1)", "… + (k+1) = (k+1)(k+2)/2", INK, ROW),
        ("ВИСНОВОК", "отже P(n) правдиве для всіх n", "формула справджується завжди", FIELD, GREENFILL),
    ]
    for i, (role, desc, ex, col, bg) in enumerate(stages):
        y = top + i * (box_h + gap)
        f.append(rect(bx, y, bw, box_h, fill=bg, stroke=col, sw=1.8, rx=10))
        # ліва колонка — роль + опис
        f.append(text(bx + 22, y + 30, role, size=15, bold=True, color=col, anchor="start"))
        f.append(text(bx + 22, y + 54, desc, size=12.5, color=INK, anchor="start"))
        # роздільник
        f.append(line(bx + 330, y + 14, bx + 330, y + box_h - 14, color="#d7dbe0", sw=1.3))
        # права колонка — приклад
        f.append(text(bx + 350, y + 44, ex, size=14.5, color=INK, anchor="start", bold=True))
        # стрілка вниз до наступної
        if i < len(stages) - 1:
            cx = bx + bw / 2
            f.append(arrow(cx, y + box_h + 2, cx, y + box_h + gap - 2, color=MUTED, sw=2.0))
    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 3. Чому законно: немає найменшого порушника ──────────────────────────────
def fig_wellorder():
    W, H = 920, 400
    f = [text(W / 2, 30, "Чому стрибок законний: найменшого порушника бути не може", size=18, bold=True),
         text(W / 2, 52, "якби P десь хибнило, серед хибних був би найменший m — і саме він приводить до суперечності",
              size=12, color=MUTED, italic=True)]

    # числова пряма
    ly = 200
    xs = [150, 250, 350, 470, 590, 710]
    labs = ["1", "2", "3", "m−1", "m", "m+1"]
    f.append(line(110, ly, 800, ly, color=INK, sw=1.6))
    # зелена смуга «тут P правда» під 1..m-1
    f.append(rect(120, ly + 8, 470 - 120 + 30, 26, fill=GREENFILL, stroke=FIELD, sw=1.4, rx=6))
    f.append(text((120 + 500) / 2, ly + 26, "тут P правда (порушників немає)", size=12, color=FIELD, bold=True))

    for x, lab in zip(xs, labs):
        red = (lab == "m")
        f.append(line(x, ly - 6, x, ly + 6, color=INK, sw=1.6))
        f.append(circle(x, ly, 7, fill=(REDFILL if red else BG),
                        stroke=(POS if red else INK), sw=(2.2 if red else 1.4)))
        f.append(text(x, ly - 16, lab, size=13, bold=red, color=(POS if red else INK)))
    # три-крапка між 3 і m-1
    f.append(text(410, ly - 16, "…", size=18, bold=True))

    # порушник m — виноска справа-вгорі, стрілка обходить цифру «m»
    f.append(text(662, 140, "найменший, де P хибне", size=12.5, bold=True, color=POS))
    f.append(('<path d="M 655 150 L 599 194" fill="none" stroke="%s" '
              'stroke-width="2" marker-end="url(#arrow)"/>' % POS))

    # крок від m-1 до m — дуга згори
    f.append(('<path d="M 470 164 Q 530 126 590 164" fill="none" stroke="%s" '
              'stroke-width="2" marker-end="url(#arrow)"/>' % NEG))
    f.append(text(524, 116, "крок:  P(m−1) ⟹ P(m)", size=12.5, bold=True, color=NEG))

    # висновок
    by = 300
    f.append(rect(90, by, 740, 60, fill="#f1f8f3", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(W / 2, by + 25,
                  "m ≠ 1 (база дала P(1)); отже m−1 не порушник → P(m−1) правда → кроком P(m) правда.",
                  size=12.5, bold=True))
    f.append(text(W / 2, by + 46,
                  "Але m — порушник, де P хибне. Суперечність: порушників немає зовсім.",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "wellorder.svg"), W, H, *f)


# ── 4. Хроніка: не один винахід, а п'ять різних здобутків ────────────────────
def fig_timeline():
    W = 1080
    BANDS = [
        ("Користуються — не називаючи", "#eef2f7", MUTED, [
            ("бл. 300 до н.е.", "Евклід", "нескінченність обходить словами: «простих більше за будь-яку кількість»"),
            ("бл. 1000", "аль-Караджі, Багдад", "перший відомий доказ із базою й переходом — але сходами ВНИЗ від 10"),
            ("бл. 1150", "аль-Самавʼаль", "переписує аль-Караджі: єдине джерело, що вціліло — оригінал утрачено"),
        ]),
        ("Усвідомлюють і формулюють", "#eaf0fd", NEG, [
            ("1321", "Леві бен Ґершон, Прованс", "дає прийомові ім'я: «підіймання сходинка за сходинкою», іврит"),
            ("бл. 1557, друк 1575", "Франческо Мауроліко, Мессіна", "сума непарних = n² у європейському друці — першість оскаржена"),
            ("1654, друк 1665", "Блез Паскаль, Париж", "СХЕМУ вголос: дві леми, «…і так до нескінченності»"),
            ("1659", "П'єр Ферма", "те саме доміно, тільки вниз: «нескінченний спуск»"),
        ]),
        ("Сперечаються за ім'я", "#fdf3e7", "#b06a12", [
            ("1656", "Джон Волліс", "пускає в обіг слово «індукція» — але для геть іншого прийому: того, що вгадує"),
            ("1686", "Якоб Бернуллі", "показує, що Воллісове міркування не доводить, і ставить перехід n → n+1"),
            ("1830", "Джордж Пікок", "«демонстративна індукція» — назва, що не прижилася"),
            ("1838", "Оґастес Де Морґан", "«математична індукція» — мимохідь, у кінці статті популярної енциклопедії"),
        ]),
        ("Питають: а чому це взагалі законно?", "#eaf7ef", FIELD, [
            ("1888", "Ріхард Дедекінд", "ДОВОДИТЬ індукцію — з означення того, чим є натуральні числа"),
            ("1889", "Джузеппе Пеано", "БЕРЕ індукцію за аксіому — і саме його ім'я лишається на списку"),
            ("1894", "Анрі Пуанкаре", "а може, це і є математичне мислення, яке нізвідки не виводиться?"),
        ]),
    ]

    X_DATE, X_SPINE, X_NAME, X_WHAT = 46, 250, 272, 560
    ROW_H, HEAD_H, GAP = 42, 30, 16

    f = [text(W / 2, 32, "Не один винахід, а п'ять різних здобутків", size=19, bold=True),
         text(W / 2, 55, "«хто винайшов індукцію» — питання, що склеїло докупи кілька окремих досягнень; ось вони нарізно",
              size=12.5, color=MUTED, italic=True)]

    y = 78
    for band_title, band_bg, band_col, rows in BANDS:
        f.append(rect(30, y, W - 60, HEAD_H, fill=band_bg, stroke=band_col, sw=1.4, rx=7))
        f.append(text(46, y + HEAD_H / 2 + 5, band_title.upper(), size=12.5, bold=True,
                      color=band_col, anchor="start"))
        y += HEAD_H
        top_of_rows = y
        for date, who, what in rows:
            cy = y + ROW_H / 2
            f.append(text(X_DATE, cy + 5, date, size=12, color=MUTED, anchor="start", bold=True))
            f.append(circle(X_SPINE, cy, 5.5, fill=band_bg, stroke=band_col, sw=2.2))
            f.append(text(X_NAME, cy + 5, who, size=13.5, bold=True, color=INK, anchor="start"))
            f.append(text(X_WHAT, cy + 5, what, size=12, color=INK, anchor="start"))
            y += ROW_H
        # вертикальний хребет усередині смуги — за спиною кружечків
        f.insert(2, line(X_SPINE, top_of_rows + 6, X_SPINE, y - 6, color=band_col, sw=1.6))
        y += GAP

    H = y + 46
    f.append(fitbox(30, y - GAP + 12, W - 60, 40,
                    "Між першим ужитком і першим формулюванням — вісімсот років. Не через тупість: бракувало алгебри, "
                    "щоб записати твердження про безіменне n, і згоди, що скінченний доказ дає нескінченний висновок.",
                    size=12.5, fill="#f9fafb", stroke=MUTED, sw=1.2, color=INK))
    render(os.path.join(IMG, "induction-timeline.svg"), W, H, *f)


# ── 5. Що саме мав аль-Караджі і чого бракувало ──────────────────────────────
def fig_karaji_vs_modern():
    W, H = 1000, 520
    f = [text(W / 2, 32, "Чого бракувало доказові аль-Караджі", size=19, bold=True),
         text(W / 2, 55, "обидві частини — база й перехід — уже на місці; немає ЗАГАЛЬНОСТІ: теорема сказана про число 10, а не про n",
              size=12.5, color=MUTED, italic=True)]

    PL_X, PR_X, PW = 40, 530, 430
    PY, PH = 80, 344
    f.append(rect(PL_X, PY, PW, PH, fill="#fbfcfd", stroke=MUTED, sw=1.5, rx=10))
    f.append(rect(PR_X, PY, PW, PH, fill="#fbfcfd", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(PL_X + PW / 2, PY + 26, "бл. 1000 — сходами ВНИЗ від десятки", size=14, bold=True, color=MUTED))
    f.append(text(PR_X + PW / 2, PY + 26, "сучасна схема — одна обіцянка про безіменне k", size=14, bold=True, color=FIELD))

    # позначення
    f.append(text(PL_X + PW / 2, PY + 50, "позначмо  S(n) = 1 + 2 + … + n", size=12.5, italic=True, color=INK))

    # ── лівий стовпчик: спуск
    steps = ["S(10)²  =  S(9)²  +  10³",
             "S(9)²   =  S(8)²  +  9³",
             "S(8)²   =  S(7)²  +  8³",
             "⋮",
             "S(1)²   =  1³      ✓"]
    sy = PY + 76
    for i, s in enumerate(steps):
        yy = sy + i * 40
        last = (i == len(steps) - 1)
        f.append(rect(PL_X + 74, yy, 322, 32, fill=(GREENFILL if last else ROW),
                      stroke=(FIELD if last else "#d7dbe0"), sw=(1.8 if last else 1.2), rx=6))
        f.append(text(PL_X + 235, yy + 21, s, size=13.5, bold=last, color=INK))
    # довга стрілка спуску
    f.append(arrow(PL_X + 48, sy + 6, PL_X + 48, sy + 4 * 40 + 26, color=MUTED, sw=2.2))
    f.append(('<text x="%d" y="%d" font-size="11.5" fill="%s" font-style="italic" '
              'text-anchor="middle" transform="rotate(-90 %d %d)">спуск від 10 до 1</text>'
              % (PL_X + 30, sy + 90, MUTED, PL_X + 30, sy + 90)))

    # ── правий стовпчик: схема
    parts = [("База", "P(1)  —  правда", GREENFILL, FIELD),
             ("Крок", "P(k)  ⟹  P(k+1)   для БУДЬ-ЯКОГО k", "#eaf0fd", NEG),
             ("", "", None, None),
             ("Висновок", "P(n)  для всіх n  одразу", GREENFILL, FIELD)]
    ry = PY + 76
    for i, (role, body, bg, col) in enumerate(parts):
        yy = ry + i * 40
        if bg is None:
            f.append(arrow(PR_X + PW / 2, yy + 4, PR_X + PW / 2, yy + 28, color=MUTED, sw=2.0))
            continue
        f.append(rect(PR_X + 24, yy, 382, 32, fill=bg, stroke=col, sw=1.6, rx=6))
        f.append(text(PR_X + 40, yy + 21, role, size=12.5, bold=True, color=col, anchor="start"))
        f.append(text(PR_X + 130, yy + 21, body, size=13, color=INK, anchor="start"))

    # підсумкові виноски під панелями
    f.append(fitbox(PL_X, PY + PH + 14, PW, 56,
                    "База й перехід є. Але теорема сказана про 10:\nдля 11 усе доводиться наново.",
                    size=12.5, fill="#f9fafb", stroke=MUTED, sw=1.2, color=INK))
    f.append(fitbox(PR_X, PY + PH + 14, PW, 56,
                    "k не має номера — тому одне міркування\nнакриває всю нескінченну шкалу відразу.",
                    size=12.5, fill=GREENFILL, stroke=FIELD, sw=1.2, color=INK))

    f.append(text(W / 2, H - 18,
                  "Різниця не в кмітливості, а в мові: щоб сказати «для будь-якого k», потрібна алгебра, якої в Багдаді ще не було.",
                  size=12.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "karaji-vs-modern.svg"), W, H, *f)


# ── Спуск рекурсії: чому звичайної гіпотези замало (вставка proj) ────────────
def fig_descent_strong():
    W, H = 980, 470
    f = [text(W / 2, 30, "Виклик стрибає на n//2 — тому потрібна СИЛЬНА гіпотеза", size=18, bold=True),
         text(W / 2, 52, "power(x, 13) кличе power(x, 6), а не power(x, 12): сусід тут ні до чого",
              size=12, color=MUTED, italic=True)]

    ly = 268
    x = lambda i: 100 + i * 62          # 0 → 100 … 13 → 906

    def arc(i, j, apex, color, sw):
        x1, x2 = x(i), x(j)
        cy = 2 * apex - (ly - 10)
        return ('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
                'stroke-width="%.1f" marker-end="url(#arrow)"/>'
                % (x1, ly - 10, (x1 + x2) / 2, cy, x2, ly - 10, color, sw))

    f.append(arc(13, 6, 122, POS, 2.6))
    f.append(text((x(13) + x(6)) / 2, 100, "power(x, 13) → power(x, 6)", size=13, bold=True, color=POS))
    for (i, j, ap) in ((6, 3, 198), (3, 1, 216), (1, 0, 230)):
        f.append(arc(i, j, ap, MUTED, 1.8))
    f.append(text(x(1) + 30, 168, "…і далі вниз до бази", size=11.5, color=MUTED, italic=True))

    # числова пряма; мітки — ПІД нею, щоб написи не лягли на лінію
    f.append(line(76, ly, 934, ly, color=INK, sw=1.6))
    for i in range(14):
        landing = (i in (6, 3, 1, 0))
        plain = (i == 12)
        f.append(circle(x(i), ly, 7,
                        fill=(REDFILL if plain else (GREENFILL if landing else BG)),
                        stroke=(POS if plain else (FIELD if landing else INK)),
                        sw=(2.4 if (plain or landing) else 1.3)))
        f.append(text(x(i), ly + 30, str(i), size=13,
                      bold=(plain or landing or i == 13),
                      color=(POS if plain else (FIELD if landing else INK))))

    by = 316
    f.append(rect(82, by, x(12) - 82 + 18, 34, fill=GREENFILL, stroke=FIELD, sw=1.6, rx=8))
    f.append(text((82 + x(12) + 18) / 2, by + 22,
                  "СИЛЬНА гіпотеза: P(m) правдиве для ВСІХ m ≤ 12 — отже й для 6",
                  size=13, bold=True, color=FIELD))

    ny = 376
    f.append(fitbox(76, ny, 415, 76,
                    "ЗВИЧАЙНА індукція дає лише P(12) —\nсусіда. Виклик пішов на 6, і про 6\nвона не каже нічого. Крок стоїть.",
                    size=12.5, fill=REDFILL, stroke=POS, sw=1.6, color=INK))
    f.append(fitbox(519, ny, 415, 76,
                    "СИЛЬНА індукція дає все нижче за 13.\nСеред «усього» є й 6 — саме те, що\nповернув виклик. Крок проходить.",
                    size=12.5, fill=GREENFILL, stroke=FIELD, sw=1.6, color=INK))
    render(os.path.join(IMG, "descent-strong.svg"), W, H, *f)


# ── Заслабка гіпотеза не стикується з кроком (вставка proj) ──────────────────
def fig_hypothesis_gap():
    W, H = 1000, 440
    f = [text(W / 2, 30, "Чому сильніше твердження довести ЛЕГШЕ", size=18, bold=True),
         text(W / 2, 52, "крок питає про acc + n; гіпотеза мусить дотягтися саме туди",
              size=12, color=MUTED, italic=True)]

    def panel(px, title, tcol, all_green):
        g = [rect(px, 76, 440, 246, fill=BG, stroke=tcol, sw=1.8, rx=10)]
        g.append(text(px + 220, 102, title, size=13.5, bold=True, color=tcol))
        g.append(text(px + 220, 130, "значення акумулятора acc", size=11.5, color=MUTED, italic=True))

        ay = 190
        if all_green:
            g.append(rect(px + 40, ay - 13, 360, 26, fill=GREENFILL, stroke=FIELD, sw=1.6, rx=6))
        g.append(line(px + 34, ay, px + 406, ay, color=INK, sw=1.5))

        zx, nx = px + 110, px + 320
        g.append(circle(zx, ay, 8, fill=GREENFILL, stroke=FIELD, sw=2.2))
        g.append(text(zx, ay - 26, "acc = 0", size=12, bold=True, color=FIELD))
        col = FIELD if all_green else POS
        g.append(circle(nx, ay, 8, fill=(GREENFILL if all_green else REDFILL), stroke=col, sw=2.2))
        g.append(text(nx, ay - 26, "acc = n", size=12, bold=True, color=col))
        g.append(text(nx, ay + 32, ("накрито ✓" if all_green else "сюди гіпотеза не дістає"),
                      size=12, bold=True, color=col))
        g.append(arrow(zx + 16, ay + 62, nx - 12, ay + 62, color=col, sw=2.0))
        g.append(text((zx + nx) / 2, ay + 84, "крок питає sum(n−1, acc+n)", size=11.5,
                      color=col, italic=True))
        return g

    f += panel(30, "ЗАСЛАБКА: «sum(n−1, 0) = (n−1)n/2»", POS, False)
    f += panel(530, "ПОСИЛЕНА: «для БУДЬ-ЯКОГО acc»", FIELD, True)

    f.append(fitbox(30, 344, 940, 68,
                    "Сильніше твердження дає більше не лише ДОВОДИТИ, а й ВЖИВАТИ: у кроці ти дістаєш ширшу гіпотезу.\n"
                    "Саме тому вузьке «про acc = 0» не доводиться, а ширше «про всі acc» — доводиться відразу.",
                    size=12.5, fill=ROW, stroke=MUTED, sw=1.4, color=INK))
    render(os.path.join(IMG, "hypothesis-gap.svg"), W, H, *f)


# ── Доказ доводить модель, а не машину (вставка proj) ────────────────────────
def fig_model_vs_machine():
    W, H = 990, 510
    f = [text(W / 2, 30, "Доказ доводить модель, а не машину", size=18, bold=True),
         text(W / 2, 52, "той самий power(3, 40) у двох світах арифметики", size=12,
              color=MUTED, italic=True)]

    # світ доказу: ℕ, без стелі
    f.append(text(70, 100, "ℕ — світ доказу: множення завжди дає точний добуток", size=13,
                  bold=True, color=FIELD, anchor="start"))
    ny = 150
    f.append(line(70, ny, 856, ny, color=FIELD, sw=2.0))
    f.append(arrow(856, ny, 926, ny, color=FIELD, sw=2.0))
    f.append(text(946, ny + 5, "∞", size=17, bold=True, color=FIELD))
    f.append(circle(600, ny, 8, fill=GREENFILL, stroke=FIELD, sw=2.4))
    f.append(text(600, ny - 22, "3⁴⁰ = 12 157 665 459 056 928 801  ✓", size=12.5, bold=True, color=FIELD))

    # світ машини: int64, зі стелею
    f.append(text(70, 232, "int64 — світ машини: за стелею добуток обрізається", size=13,
                  bold=True, color=POS, anchor="start"))
    my = 296
    f.append(rect(70, my - 26, 630, 52, fill=ROW, stroke=INK, sw=1.6, rx=8))
    f.append(text(385, my + 6, "−2⁶³ … 2⁶³−1  =  9 223 372 036 854 775 807", size=13, bold=True))
    f.append(('<path d="M 600 186 L 690 262" fill="none" stroke="%s" stroke-width="2.2" '
              'marker-end="url(#arrow)"/>' % POS))
    f.append(text(866, 254, "не влазить", size=12.5, bold=True, color=POS))
    f.append(circle(756, my, 8, fill=REDFILL, stroke=POS, sw=2.4))
    f.append(text(848, my + 5, "переповнення", size=12, color=POS, italic=True))
    f.append(('<path d="M 756 318 Q 470 384 150 336" fill="none" stroke="%s" stroke-width="2.2" '
              'stroke-dasharray="6,4" marker-end="url(#arrow)"/>' % POS))
    f.append(text(452, 402, "машина віддає  −6 289 078 614 652 622 815", size=13, bold=True, color=POS))

    f.append(fitbox(70, 424, 860, 68,
                    "Доказ не збрехав: він доводив твердження про ℕ, а машина рахує не в ℕ. Полагодити можна двома способами —\n"
                    "узяти тип без стелі (цілі Python, BigInt) або рахувати за модулем: mod m тримає кожне значення в [0, m).",
                    size=12.5, fill=ROW, stroke=MUTED, sw=1.4, color=INK))
    render(os.path.join(IMG, "model-vs-machine.svg"), W, H, *f)


if __name__ == "__main__":
    fig_dominoes()
    fig_anatomy()
    fig_wellorder()
    fig_timeline()
    fig_karaji_vs_modern()
    fig_descent_strong()
    fig_hypothesis_gap()
    fig_model_vs_machine()
    print("OK: 8 figures ->", IMG)
