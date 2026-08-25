# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

RED_T   = "#fdecea"
GREEN_T = "#f2faf5"
BLUE_T  = "#eaf0fd"
GREY_T  = "#f4f6f8"


# ── Анатомія трьох чисел: який розряд рухає яка зміна й що це для споживача ─────
def fig_semver_anatomy():
    W, H = 1160, 580
    frags = []
    frags.append(text(W / 2, 40, "Три розряди й одне питання: чи зламає мене оновлення?",
                      size=17, bold=True))

    # велика версія 2 . 4 . 1 із кольоровими розрядами
    yb = 108
    frags.append(text(500, yb + 14, "2", size=46, color=POS, bold=True))
    frags.append(text(545, yb + 14, ".", size=46, color=INK))
    frags.append(text(580, yb + 14, "4", size=46, color=FIELD, bold=True))
    frags.append(text(615, yb + 14, ".", size=46, color=INK))
    frags.append(text(650, yb + 14, "1", size=46, color=NEG, bold=True))

    cols = [
        (60,  POS,   RED_T,   "МАЖОРНЕ = 2",
         "ламка зміна:\nприбрав, переназвав\nчи змінив поведінку",
         "читай журнал і мігруй —\nбрати наосліп НЕ можна"),
        (415, FIELD, GREEN_T, "МІНОРНЕ = 4",
         "нова можливість\nпоряд зі старим;\nстаре — точно як було",
         "безпечно;\nнове — за бажанням"),
        (770, NEG,   BLUE_T,  "ЛАТКА = 1",
         "виправлення без зміни\nповедінки, на яку\nти спираєшся",
         "бери наосліп"),
    ]
    cw = 330
    for x, col, tint, head, grows, means in cols:
        frags.append(fitbox(x, 175, cw, 50, head, size=16, bold=True, fill=tint, stroke=col, sw=2.2))
        frags.append(text(x + cw / 2, 250, "коли росте", size=11.5, color=MUTED, italic=True))
        frags.append(fitbox(x, 258, cw, 82, grows, size=12.5, fill=BG, stroke=col, sw=1.5))
        frags.append(text(x + cw / 2, 360, "що це для тебе", size=11.5, color=MUTED, italic=True))
        frags.append(fitbox(x, 368, cw, 62, means, size=12.5, bold=True, fill=tint, stroke=col, sw=1.5))

    frags.append(fitbox(70, 470, 1020, 74,
                        "Правило скидання: піднявся старший розряд — молодші в нуль.\n"
                        "1.4.2  →  1.5.0 (нова можливість, латка в нуль)  →  2.0.0 (ламка, мінор і латка в нуль).\n"
                        "Кожен розряд лічить зміни свого роду від останньої старшої зміни.",
                        size=13, bold=True, fill=BLUE_T, stroke=NEG, sw=1.8))

    render(os.path.join(IMG, 'semver-anatomy.svg'), W, H, *frags)


# ── Старшинство версій на одній осі зростання, з двома неочевидними правилами ──
def fig_precedence_order():
    W, H = 1320, 430
    frags = []
    frags.append(text(W / 2, 38, "Старшинство версій: одна вісь зростання", size=17, bold=True))

    seq = [
        ("1.0.0-alpha",      MUTED, GREY_T),
        ("1.0.0-alpha.1",    MUTED, GREY_T),
        ("1.0.0-beta",       MUTED, GREY_T),
        ("1.0.0-rc.1",       NEG,   BLUE_T),
        ("1.0.0",            NEG,   BLUE_T),
        ("1.0.1",            INK,   GREY_T),
        ("1.2.0",            POS,   RED_T),
        ("1.10.0",           POS,   RED_T),
        ("2.0.0",            INK,   GREEN_T),
    ]
    n = len(seq)
    left, right = 40, W - 40
    span = right - left
    centers = [left + span * (i + 0.5) / n for i in range(n)]
    bw = 118

    baseline = 300
    frags.append(arrow(30, baseline, W - 20, baseline, color=LINE, sw=2.0))
    frags.append(text(40, baseline + 26, "молодше", size=12, color=MUTED, anchor="start", italic=True))
    frags.append(text(W - 40, baseline + 26, "старше →", size=12.5, color=INK, anchor="end", bold=True))

    ybox = 168
    for (lab, col, tint), cx in zip(seq, centers):
        frags.append(fitbox(cx - bw / 2, ybox, bw, 50, lab, size=12, bold=True, fill=tint, stroke=col, sw=1.6))
        frags.append(line(cx, ybox + 50, cx, baseline, color=col, sw=1.2, dash="4,4"))

    # виноска (a): передвипуск < випуск — над rc.1 (idx 3) та 1.0.0 (idx 4)
    xa1, xa2 = centers[3], centers[4]
    frags.append(line(xa1, 138, xa2, 138, color=NEG, sw=2.0))
    frags.append(line(xa1, 138, xa1, 150, color=NEG, sw=2.0))
    frags.append(line(xa2, 138, xa2, 150, color=NEG, sw=2.0))
    frags.append(text((xa1 + xa2) / 2, 128, "передвипуск < випуск", size=12, color=NEG, bold=True))

    # виноска (b): числами, не рядками — над 1.2.0 (idx 6) та 1.10.0 (idx 7)
    xb1, xb2 = centers[6], centers[7]
    frags.append(line(xb1, 138, xb2, 138, color=POS, sw=2.0))
    frags.append(line(xb1, 138, xb1, 150, color=POS, sw=2.0))
    frags.append(line(xb2, 138, xb2, 150, color=POS, sw=2.0))
    frags.append(text((xb1 + xb2) / 2, 128, "числами: 2 < 10", size=12, color=POS, bold=True))

    frags.append(fitbox(160, 344, 1000, 46,
                        "Метадані збірки (+build) на позицію не впливають: 1.0.0+build.9 — там само, де 1.0.0.",
                        size=12.5, fill=GREY_T, stroke=MUTED, sw=1.5))

    render(os.path.join(IMG, 'precedence-order.svg'), W, H, *frags)


# ── Діапазони як проміжки на осі версій: каретка проти тильди ──────────────────
def fig_ranges_intervals():
    W, H = 1200, 470
    frags = []
    frags.append(text(W / 2, 38, "Діапазони як проміжки: що вбирає каретка, а що тильда",
                      size=17, bold=True))

    # доступні версії на осі (порядок, не масштаб)
    axis_y = 340
    vers = [("1.2.3", 150), ("1.2.7", 350), ("1.3.0", 545), ("1.9.4", 830), ("2.0.0", 1055)]
    frags.append(arrow(90, axis_y, 1140, axis_y, color=LINE, sw=2.0))
    frags.append(text(1150, axis_y + 4, "версії", size=12, color=MUTED, anchor="start", italic=True))
    for lab, x in vers:
        frags.append(circle(x, axis_y, 5.5, fill=INK, stroke=INK, sw=1))
        frags.append(text(x, axis_y + 26, lab, size=12.5, bold=True))

    # межі-виключення (пунктир угору): 1.3.0 і 2.0.0
    frags.append(line(545, 150, 545, axis_y - 6, color=NEG, sw=1.4, dash="5,4"))
    frags.append(line(1055, 150, 1055, axis_y - 6, color=POS, sw=1.6, dash="5,4"))
    frags.append(text(1055, 138, "2.0.0 — поза обома", size=12, color=POS, bold=True, anchor="middle"))

    # смуга каретки ^1.2.3: [1.2.3, 2.0.0)
    frags.append(rect(150, 172, 905, 44, fill=GREEN_T, stroke=FIELD, sw=2.2))
    frags.append(text(602, 199, "каретка  ^1.2.3   =   1.2.3 ≤ v < 2.0.0",
                      size=13.5, color=FIELD, bold=True))

    # смуга тильди ~1.2.3: [1.2.3, 1.3.0)
    frags.append(rect(150, 244, 395, 44, fill=BLUE_T, stroke=NEG, sw=2.2))
    frags.append(text(347, 271, "тильда  ~1.2.3  =  1.2.3 ≤ v < 1.3.0",
                      size=12.5, color=NEG, bold=True))

    # хто що бере (найвища в проміжку)
    frags.append(circle(830, axis_y, 9, fill=FIELD, stroke=FIELD, sw=1.5))
    frags.append(text(830, axis_y + 44, "каретка бере", size=11.5, color=FIELD, bold=True))
    frags.append(circle(350, axis_y, 9, fill=NEG, stroke=NEG, sw=1.5))
    frags.append(text(350, axis_y + 44, "тильда бере", size=11.5, color=NEG, bold=True))

    frags.append(fitbox(90, 396, 1020, 56,
                        "Розв'язувач бере НАЙВИЩУ версію, що влазить у проміжок: каретка — 1.9.4, тильда — 1.2.7.\n"
                        "Наступний мажор (2.0.0) лишається за стіною — його беруть лише навмисним підняттям.",
                        size=13, bold=True, fill=GREY_T, stroke=MUTED, sw=1.6))

    render(os.path.join(IMG, 'ranges-intervals.svg'), W, H, *frags)


# ── Дерево рішень порівняння передвипусків (для проєкту-прикладу) ──────────────
def fig_prerelease_rules():
    W, H = 1200, 650
    frags = []
    frags.append(text(W / 2, 40, "Порівняння передвипусків, коли ядро вже рівне", size=17, bold=True))

    # два «крайні» правила зверху
    frags.append(fitbox(60, 62, 520, 68,
                        "Готовий випуск  >  будь-який передвипуск\n1.0.0-rc.1   <   1.0.0",
                        size=13.5, bold=True, fill=GREEN_T, stroke=FIELD, sw=2.0))
    frags.append(fitbox(620, 62, 520, 68,
                        "За рівного префікса довший набір старший\n1.0.0-alpha   <   1.0.0-alpha.1",
                        size=13.5, bold=True, fill=GREY_T, stroke=MUTED, sw=2.0))

    frags.append(text(W / 2, 166,
                      "інакше — ідентифікатор за ідентифікатором, і кожну пару за трьома правилами:",
                      size=13.5, italic=True, color=MUTED))

    cols = [
        (60,  NEG,   BLUE_T,  "обидва числові",
         "порівнюй ЧИСЛАМИ,\nне рядками",
         "beta.2  <  beta.11"),
        (420, POS,   RED_T,   "один числовий,\nодин буквений",
         "числовий ЗАВЖДИ\nнижчий за буквений",
         "alpha.1  <  alpha.beta"),
        (780, FIELD, GREEN_T, "обидва буквені",
         "лексично,\nв ASCII-порядку",
         "alpha  <  beta"),
    ]
    cw = 340
    for x, col, tint, head, rule, ex in cols:
        frags.append(fitbox(x, 194, cw, 58, head, size=15, bold=True, fill=tint, stroke=col, sw=2.2))
        frags.append(text(x + cw / 2, 286, "правило", size=11, color=MUTED, italic=True))
        frags.append(fitbox(x, 294, cw, 66, rule, size=13, bold=True, fill=BG, stroke=col, sw=1.5))
        frags.append(text(x + cw / 2, 392, "приклад", size=11, color=MUTED, italic=True))
        frags.append(fitbox(x, 400, cw, 50, ex, size=14.5, bold=True, fill=tint, stroke=col, sw=1.5))

    frags.append(fitbox(60, 488, 1080, 62,
                        "Перша ж пара ідентифікаторів, що відрізняється, вирішує все — далі не дивимось.\n"
                        "Якщо всі спільні рівні, спрацьовує правило довшого набору (зверху праворуч).",
                        size=13, fill=GREY_T, stroke=MUTED, sw=1.6))

    frags.append(fitbox(60, 564, 1080, 54,
                        "Метадані збірки (+…) у старшинстві не беруть участі зовсім:  1.0.0+build.9  =  1.0.0",
                        size=13.5, bold=True, fill=BLUE_T, stroke=NEG, sw=1.8))

    render(os.path.join(IMG, 'prerelease-rules.svg'), W, H, *frags)


# ── Дві схеми однієї ідеї: OSGi (2010) проти SemVer Престона-Веннера ───────────
def fig_osgi_vs_semver():
    W, H = 1180, 600
    frags = []
    frags.append(text(W / 2, 34, "Дві схеми однієї ідеї: точніше проти простішого",
                      size=17, bold=True))

    # рамки колонок
    frags.append(rect(55, 70, 515, 420, fill=BG, stroke=POS, sw=2.4))
    frags.append(rect(610, 70, 515, 420, fill=BG, stroke=NEG, sw=2.4))

    # ── ліва колонка: OSGi ──
    lx, lw = 73, 479
    frags.append(fitbox(lx, 82, lw, 46,
                        "OSGi Alliance · вайтпейпер «Semantic Versioning», 2010",
                        size=13.5, bold=True, fill=RED_T, stroke=POS, sw=1.8))
    lrows = [
        "версія: major . minor . micro . qualifier  (чотири розряди)",
        "два роди клієнта: хто ВИКЛИКАЄ · хто РЕАЛІЗУЄ інтерфейс",
        "мінор: сумісний для викликача, ламкий для реалізатора",
        "діапазони різні: викликач [1.5, 2)  ·  реалізатор [1.5, 1.6)",
    ]
    ry = 140
    for r in lrows:
        frags.append(fitbox(lx, ry, lw, 56, r, size=12.5, fill=BG, stroke=POS, sw=1.4))
        ry += 66
    frags.append(fitbox(lx, 404, lw, 44, "точніше — і саме тому важче ухвалити",
                        size=13, bold=True, fill=RED_T, stroke=POS, sw=1.6))

    # ── права колонка: SemVer ──
    rx, rwd = 628, 479
    frags.append(fitbox(rx, 82, rwd, 46,
                        "Том Престон-Веннер · semver.org, від грудня 2009",
                        size=13.5, bold=True, fill=BLUE_T, stroke=NEG, sw=1.8))
    rrows = [
        "версія: MAJOR . MINOR . PATCH  (три розряди)",
        "один рід клієнта — одне правило на всіх",
        "мінор сумісний — і по всьому, без ролей",
        "усі беруть один діапазон: [1.2.3, 2.0.0)",
    ]
    ry = 140
    for r in rrows:
        frags.append(fitbox(rx, ry, rwd, 56, r, size=12.5, fill=BG, stroke=NEG, sw=1.4))
        ry += 66
    frags.append(fitbox(rx, 404, rwd, 44, "простіше — і саме тому поширилося",
                        size=13, bold=True, fill=BLUE_T, stroke=NEG, sw=1.6))

    # підсумкова смуга
    frags.append(fitbox(55, 508, 1070, 64,
                        "Ідея одна — кодувати сумісність у номері.\n"
                        "Переміг не найточніший запис, а найпростіший названий, що влучив у мить найбільшої потреби.",
                        size=13.5, bold=True, fill=GREY_T, stroke=MUTED, sw=1.8))

    render(os.path.join(IMG, 'osgi-vs-semver.svg'), W, H, *frags)


# ── Три нитки, що зійшлися: часова смуга народження SemVer ─────────────────────
def fig_semver_birth_timeline():
    W, H = 1340, 560
    frags = []
    frags.append(text(W / 2, 30, "Три нитки, що зійшлися у народженні SemVer", size=17, bold=True))

    # легенда: чотири кольори — чотири роди подій
    leg = [
        (150,  MUTED, "тиск екосистеми"),
        (400,  NEG,   "стандарт (Престон-Веннер)"),
        (770,  POS,   "паралельно: OSGi"),
        (1075, FIELD, "ухвалення"),
    ]
    for dx, col, lab in leg:
        frags.append(circle(dx, 58, 6, fill=col, stroke=col, sw=1))
        frags.append(text(dx + 14, 62, lab, size=12.5, color=INK, anchor="start"))

    # вісь часу
    baseline = 300
    frags.append(arrow(70, baseline, 1300, baseline, color=LINE, sw=2.0))
    frags.append(text(74, baseline + 26, "раніше", size=12, color=MUTED, anchor="start", italic=True))
    frags.append(text(1298, baseline + 26, "час →", size=12.5, color=INK, anchor="end", bold=True))

    def X(year):
        return 130 + (year - 2004) * (1120.0 / 11.0)

    # (рік-позиція, ярус, колір, тінт, заголовок, підпис)
    A_HIGH, A_MID, B_MID, B_LOW = 95, 178, 395, 478
    events = [
        (2004.0, B_LOW,  MUTED, GREY_T,  "2004 · RubyGems",        "пакети стають нормою"),
        (2008.0, A_MID,  MUTED, GREY_T,  "2008 · GitHub",          "обмін кодом — один клік"),
        (2009.8, A_HIGH, NEG,   BLUE_T,  "кін. 2009 · semver.org", "Престон-Веннер починає"),
        (2010.2, B_MID,  POS,   RED_T,   "2010 · OSGi whitepaper", "паралельна, точніша схема"),
        (2011.0, A_MID,  NEG,   BLUE_T,  "2011 · SemVer 1.0.0",    "перша стабільна редакція"),
        (2013.0, A_HIGH, NEG,   BLUE_T,  "18.06.2013 · SemVer 2.0.0", "чинна дотепер"),
        (2014.0, B_MID,  FIELD, GREEN_T, "2014+ · Cargo та інші",  "SemVer за замовчуванням"),
    ]
    bw, bh = 216, 58
    for year, cy, col, tint, head, desc in events:
        x = X(year)
        cx = min(max(x, bw / 2 + 8), W - bw / 2 - 8)
        # конектор від осі до рамки
        if cy < baseline:
            frags.append(line(x, baseline, cx, cy + bh / 2, color=col, sw=1.2, dash="4,4"))
        else:
            frags.append(line(x, baseline, cx, cy - bh / 2, color=col, sw=1.2, dash="4,4"))
        frags.append(circle(x, baseline, 5.5, fill=col, stroke=col, sw=1))
        frags.append(fitbox(cx - bw / 2, cy - bh / 2, bw, bh,
                            head + "\n" + desc, size=12.5, bold=True, fill=tint, stroke=col, sw=1.6))

    render(os.path.join(IMG, 'semver-birth-timeline.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_semver_anatomy()
    fig_precedence_order()
    fig_ranges_intervals()
    fig_prerelease_rules()
    fig_osgi_vs_semver()
    fig_semver_birth_timeline()
    print("figures written to", IMG)
