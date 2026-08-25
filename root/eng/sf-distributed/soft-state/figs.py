# -*- coding: utf-8 -*-
"""Фігури до теми «М'який стан: запис, що живе, доки його оновлюють»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # погано / мертве
COOL = "#eaf0fd"   # нейтральне пояснення
GOOD = "#e8f6ee"   # живе / правильне


# ── 1. Твердий стан проти м'якого: доля запису після раптової смерті ─────────
def hard_vs_soft():
    W, H = 1180, 640
    f = []

    x0, x1 = 300.0, 1120.0
    span = x1 - x0
    tdeath = x0 + span * 0.46          # мить раптової смерті копії
    step = span / 12.0                 # один період T

    # ── доріжка А: твердий стан
    yA = 120.0
    f.append(fitbox(40, yA - 34, 235, 68,
                    "ТВЕРДИЙ СТАН\nпам'ятай, доки не скажу забути",
                    size=13, bold=True, fill=COOL))

    # смуга «запис у реєстрі»
    f.append(rect(x0, yA - 16, tdeath - x0, 32, fill=GOOD, stroke=FIELD, sw=1.6))
    f.append(text((x0 + tdeath) / 2, yA + 5, "запис чинний і правдивий", size=12.5))
    f.append(rect(tdeath, yA - 16, x1 - tdeath, 32, fill=WARM, stroke=POS, sw=1.8))
    f.append(text((tdeath + x1) / 2, yA + 5, "запис чинний і БРЕХЛИВИЙ — назавжди",
                  size=12.5, color=POS, bold=True))

    # подія реєстрації
    f.append(arrow(x0, yA - 62, x0, yA - 20, color=FIELD))
    f.append(text(x0, yA - 72, "«я тут»", size=12, color=FIELD, bold=True))

    # ── доріжка Б: м'який стан
    yB = 360.0
    f.append(fitbox(40, yB - 34, 235, 68,
                    "М'ЯКИЙ СТАН\nзабувай, якщо не нагадаю",
                    size=13, bold=True, fill=COOL))

    tgone = tdeath + step * 3          # смерть запису через D = 3T після тиші
    f.append(rect(x0, yB - 16, tgone - x0, 32, fill=GOOD, stroke=FIELD, sw=1.6))
    f.append(text((x0 + tgone) / 2, yB + 5, "запис чинний", size=12.5))
    f.append(rect(tgone, yB - 16, x1 - tgone, 32, fill="#ffffff", stroke=MUTED,
                  sw=1.4, rx=6))
    f.append(text((tgone + x1) / 2, yB + 5, "запису немає", size=12.5, color=MUTED))

    # тики оновлення до смерті вузла
    k = 0
    while x0 + step * k < tdeath - 1:
        x = x0 + step * k
        f.append(arrow(x, yB - 58, x, yB - 20, color=FIELD))
        k += 1
    f.append(text(x0 + step * 1.0, yB - 68, "«я тут» кожні T", size=12,
                  color=FIELD, bold=True, anchor="start"))

    # позначка періоду T між двома тиками
    yT = yB - 96
    f.append(line(x0 + step * 3, yT, x0 + step * 4, yT, color=NEG, sw=1.4))
    f.append(line(x0 + step * 3, yT - 6, x0 + step * 3, yT + 6, color=NEG, sw=1.4))
    f.append(line(x0 + step * 4, yT - 6, x0 + step * 4, yT + 6, color=NEG, sw=1.4))
    f.append(text(x0 + step * 3.5, yT - 12, "T", size=13, color=NEG, bold=True))

    # строк D від останнього оновлення до зникнення
    yD = yB + 62
    f.append(line(tdeath, yD, tgone, yD, color=NEG, sw=1.6))
    f.append(line(tdeath, yD - 7, tdeath, yD + 7, color=NEG, sw=1.6))
    f.append(line(tgone, yD - 7, tgone, yD + 7, color=NEG, sw=1.6))
    f.append(text((tdeath + tgone) / 2, yD + 26, "строк D — тиша ще не вирок",
                  size=12.5, color=NEG))

    # спільна вертикаль смерті машини
    f.append(line(tdeath, 92, tdeath, 470, color=POS, sw=2, dash="6,5"))
    f.append(fitbox(tdeath - 150, 40, 300, 44,
                    "живлення зникло — сказати «я йду» нікому",
                    size=12.5, bold=True, fill=WARM, stroke=POS, sw=1.8))

    f.append(text(x1, 500, "час →", size=13, color=MUTED, anchor="end"))

    f.append(fitbox(300, 540, 820, 68,
                    "той самий збій, різна доля запису: твердий стан зберігає брехню, "
                    "поки хтось не прийде руками;\nм'який повертається до правди сам, "
                    "щойно мине строк — без жодного повідомлення про видалення",
                    size=13, fill=FILL))

    render(os.path.join(OUT, 'hard-vs-soft.svg'), W, H, *f)


# ── 2. Що витримує строк: втрати, смерть і вікно застарілости ────────────────
def refresh_window():
    W, H = 1180, 690
    f = []

    x0, x1 = 320.0, 1120.0
    span = x1 - x0
    step = span / 10.0        # період T
    D = step * 3              # строк D = 3T

    def lane(y, label, arrivals, lost, death=None, gone=None):
        """arrivals/lost — індекси тиків; death — індекс смерті вузла."""
        g = []
        g.append(fitbox(40, y - 36, 250, 72, label, size=12.5, bold=True, fill=COOL))
        g.append(line(x0, y, x1, y, color=MUTED, sw=1.2))
        for i in range(11):
            x = x0 + step * i
            g.append(line(x, y - 5, x, y + 5, color=MUTED, sw=1.1))
        for i in arrivals:
            x = x0 + step * i
            g.append(arrow(x, y - 46, x, y - 8, color=FIELD))
        for i in lost:
            x = x0 + step * i
            g.append(line(x - 9, y - 40, x + 9, y - 22, color=POS, sw=2.4))
            g.append(line(x - 9, y - 22, x + 9, y - 40, color=POS, sw=2.4))
        if death is not None:
            xd = x0 + step * death
            g.append(line(xd, y - 60, xd, y + 34, color=POS, sw=2, dash="5,4"))
        if gone is None:
            g.append(rect(x0, y + 12, span, 22, fill=GOOD, stroke=FIELD, sw=1.5))
            g.append(text(x0 + span / 2, y + 28, "запис живий увесь час", size=12))
        else:
            xg = x0 + step * gone
            g.append(rect(x0, y + 12, xg - x0, 22, fill=GOOD, stroke=FIELD, sw=1.5))
            g.append(rect(xg, y + 12, x1 - xg, 22, fill="#ffffff", stroke=MUTED, sw=1.3))
            g.append(text(x1 - 8, y + 28, "запису немає", size=12, color=MUTED,
                          anchor="end"))
        return g

    # доріжка 1 — усе доходить
    y1 = 118.0
    f += lane(y1, "усі оновлення доходять", list(range(11)), [])

    # доріжка 2 — дві втрати поспіль, третє доходить
    y2 = 300.0
    f += lane(y2, "дві втрати поспіль\n(D = 3T терпить k−1 = 2)",
              [0, 1, 2, 3, 6, 7, 8, 9, 10], [4, 5])
    xs, xe = x0 + step * 3, x0 + step * 6
    f.append(line(xs, y2 + 58, xe, y2 + 58, color=NEG, sw=1.6))
    f.append(line(xs, y2 + 51, xs, y2 + 65, color=NEG, sw=1.6))
    f.append(line(xe, y2 + 51, xe, y2 + 65, color=NEG, sw=1.6))
    f.append(text((xs + xe) / 2, y2 + 82, "тиша 3T — строк добіг краю, але не вичерпався",
                  size=12.5, color=NEG))

    # доріжка 3 — вузол помер, запис витікає через D
    y3 = 500.0
    f += lane(y3, "вузол помер на 4-му такті", [0, 1, 2, 3], [], death=4, gone=7)
    xd, xg = x0 + step * 4, x0 + step * 7
    f.append(rect(xd, y3 + 12, xg - xd, 22, fill=WARM, stroke=POS, sw=1.6))
    f.append(line(xd, y3 + 58, xg, y3 + 58, color=POS, sw=1.8))
    f.append(line(xd, y3 + 51, xd, y3 + 65, color=POS, sw=1.8))
    f.append(line(xg, y3 + 51, xg, y3 + 65, color=POS, sw=1.8))
    f.append(text((xd + xg) / 2, y3 + 82,
                  "вікно застарілости: мертвого ще вважають живим", size=12.5,
                  color=POS, bold=True))

    f.append(text(x1, y3 + 118, "час →", size=13, color=MUTED, anchor="end"))
    f.append(fitbox(40, 620, 250, 46, "→ оновлення дійшло\n✗ оновлення загублено",
                    size=12, fill=FILL))

    render(os.path.join(OUT, 'refresh-window.svg'), W, H, *f)


# ── 3. Спіраль хибного витікання і поріг недовіри ────────────────────────────
def expiry_spiral():
    W, H = 1180, 640
    f = []

    # чотири вузли кола — прямокутником із широкими проміжками
    bw, bh = 330.0, 92.0
    lx, rx = 60.0, 480.0        # ліва межа лівої та правої колонок
    ty, by = 120.0, 400.0

    boxes = [
        (lx, ty, "сплеск навантаження\nчерги наповнюються"),
        (rx, ty, "фонові оновлення відкидають\nпершими — вони найдешевші"),
        (rx, by, "живі вузли зникають зі списку\n(хибне витікання)"),
        (lx, by, "трафік тисне на менше вузлів\nїм стає ще гірше"),
    ]
    for x, y, s in boxes:
        f.append(fitbox(x, y, bw, bh, s, size=13.5, fill=WARM, stroke=POS, sw=1.8))

    # стрілки по колу
    f.append(arrow(lx + bw + 8, ty + bh / 2, rx - 8, ty + bh / 2, color=POS))
    f.append(arrow(rx + bw / 2, ty + bh + 8, rx + bw / 2, by - 8, color=POS))
    f.append(arrow(rx - 8, by + bh / 2, lx + bw + 8, by + bh / 2, color=POS))
    f.append(arrow(lx + bw / 2, by - 8, lx + bw / 2, ty + bh + 8, color=POS))

    f.append(text((lx + bw + rx) / 2, ty + bh / 2 - 16, "1", size=15, color=POS, bold=True))
    f.append(text(rx + bw / 2 + 18, (ty + bh + by) / 2, "2", size=15, color=POS, bold=True))
    f.append(text((lx + bw + rx) / 2, by + bh / 2 - 16, "3", size=15, color=POS, bold=True))
    f.append(text(lx + bw / 2 - 18, (ty + bh + by) / 2, "4", size=15, color=POS, bold=True))

    f.append(fitbox(lx + 40, (ty + bh + by) / 2 - 34, 670, 68,
                    "коло замикається: причина могла тривати п'ять секунд, "
                    "а система лишається в цьому стані назавжди",
                    size=13, fill=FILL, stroke=MUTED, sw=1.3))

    # запобіжник: поріг недовіри
    gx, gy, gw, gh = 880.0, 250.0, 250.0, 150.0
    f.append(fitbox(gx, gy, gw, gh,
                    "ПОРІГ НЕДОВІРИ\n\nзникло понад 50 % одразу?\n"
                    "ймовірніше зламався\nспостерігач, ніж усі\nспостережувані —\n"
                    "не вірити витіканню",
                    size=12.5, bold=True, fill=GOOD, stroke=FIELD, sw=2))
    f.append(arrow(gx - 10, gy + gh / 2, rx + bw + 12, (by + bh / 2)- 30, color=FIELD, sw=2.2))
    f.append(text(gx + gw / 2, gy - 22, "розрив кола", size=13, color=FIELD, bold=True))

    f.append(fitbox(60, 540, 1060, 60,
                    "механізм, що мав лише реєструвати життя, під навантаженням "
                    "починає ховати живих — і цим навантаження збільшує",
                    size=13.5, bold=True, fill=FILL))

    render(os.path.join(OUT, 'expiry-spiral.svg'), W, H, *f)


# ── 4. Дві структури реєстру: таблиця й купа подій ──────────────────────────
def registry_structure():
    W, H = 1240, 700
    f = []

    # ── ліва колонка: хеш-таблиця
    f.append(fitbox(70, 60, 430, 56, "ХЕШ-ТАБЛИЦЯ:  ключ → запис",
                    size=15, bold=True, fill=COOL))
    rows = [
        ("api-3   epoch 41   строк +38 с   ЖИВИЙ", GOOD),
        ("api-7   epoch 12   строк +12 с   ЖИВИЙ", GOOD),
        ("api-9   epoch 55   строк −3 с   ПІДОЗРЮВАНИЙ", WARM),
        ("api-2   epoch 8   строк +25 с   ЖИВИЙ", GOOD),
    ]
    y = 150.0
    for label, col in rows:
        f.append(fitbox(70, y, 430, 54, label, size=12.5, fill=col))
        y += 64

    # ── права колонка: купа подій
    f.append(fitbox(640, 60, 490, 56, "КУПА ПОДІЙ:  мінімум за часом угорі",
                    size=15, bold=True, fill=COOL))
    nodes = [(885.0, 175.0, "api-7 · +12 с", GOOD),
             (785.0, 265.0, "api-2 · +25 с", GOOD),
             (985.0, 265.0, "api-9 · +37 с", WARM),
             (735.0, 355.0, "api-3 · +38 с", GOOD)]
    nw, nh = 185.0, 44.0
    f.append(line(885, 197, 785, 243, color=MUTED, sw=1.4))
    f.append(line(885, 197, 985, 243, color=MUTED, sw=1.4))
    f.append(line(785, 287, 735, 333, color=MUTED, sw=1.4))
    for cx, cy, label, col in nodes:
        f.append(fitbox(cx - nw / 2, cy - nh / 2, nw, nh, label, size=12.5, fill=col))

    # ── два шляхи, розведені навмисно
    f.append(fitbox(70, 490, 430, 90,
                    "«я тут» — N/T разів за секунду\n"
                    "знайти запис і переписати строк\n"
                    "O(1) у середньому, купи НЕ чіпає",
                    size=13, bold=True, fill=GOOD, stroke=FIELD, sw=2))
    f.append(arrow(285, 486, 285, 404, color=FIELD, sw=2.2))

    f.append(fitbox(640, 490, 490, 90,
                    "підмітання — приблизно N/D подій за секунду\n"
                    "зняти вершину й вирішити долю запису\n"
                    "O(log N) на подію, у k = D/T разів рідше",
                    size=13, bold=True, fill=COOL, stroke=NEG, sw=2))
    f.append(line(1130, 535, 1195, 535, color=NEG, sw=2.2))
    f.append(line(1195, 535, 1195, 175, color=NEG, sw=2.2))
    f.append(arrow(1195, 175, 982, 175, color=NEG, sw=2.2))

    f.append(fitbox(70, 615, 1100, 62,
                    "інваріант: на кожен запис у таблиці — РІВНО ОДИН вузлик у купі;\n"
                    "вузлик, чий epoch не збігся з записом, — осиротілий і мовчки викидається",
                    size=13.5, bold=True, fill=FILL))

    render(os.path.join(OUT, 'registry-structure.svg'), W, H, *f)


# ── 5. Життєвий цикл запису: живий → підозрюваний → стертий ─────────────────
def entry_lifecycle():
    W, H = 1200, 700
    f = []

    f.append(fitbox(70, 150, 190, 80, "НЕМАЄ", size=15, bold=True, fill="#ffffff",
                    stroke=MUTED, color=MUTED))
    f.append(fitbox(400, 150, 220, 80, "ЖИВИЙ\nстрок попереду", size=14, bold=True, fill=GOOD))
    f.append(fitbox(790, 150, 280, 80, "ПІДОЗРЮВАНИЙ\nстрок минув, запис лишається",
                    size=13.5, bold=True, fill=WARM))
    f.append(fitbox(400, 520, 220, 80, "СТЕРТИЙ", size=15, bold=True, fill="#ffffff",
                    stroke=MUTED, color=MUTED))

    # НЕМАЄ → ЖИВИЙ
    f.append(arrow(262, 190, 396, 190, color=FIELD, sw=2))
    f.append(text(329, 172, "«я тут» вперше", size=12.5, color=FIELD, bold=True))

    # ЖИВИЙ → ПІДОЗРЮВАНИЙ
    f.append(arrow(622, 190, 786, 190, color=POS, sw=2))
    f.append(text(704, 172, "строк вичерпано", size=12.5, color=POS, bold=True))
    f.append(text(704, 214, "живих −1", size=12, color=MUTED))

    # ПІДОЗРЮВАНИЙ → ЖИВИЙ
    f.append(line(870, 232, 870, 278, color=FIELD, sw=2))
    f.append(line(870, 278, 510, 278, color=FIELD, sw=2))
    f.append(arrow(510, 278, 510, 234, color=FIELD, sw=2))
    f.append(text(690, 302, "«я тут» знову — живих +1", size=12.5, color=FIELD, bold=True))

    # ПІДОЗРЮВАНИЙ → ворота
    f.append(arrow(990, 232, 990, 336, color=POS, sw=2))
    f.append(text(1085, 292, "пільга минула", size=12.5, color=POS, bold=True))

    # ворота недовіри
    f.append(fitbox(760, 340, 340, 110,
                    "ПОРІГ НЕДОВІРИ\n"
                    "живих менше за половину відомих?\n"
                    "так → тримати · ні → стерти",
                    size=13, bold=True, fill=COOL, stroke=NEG, sw=2.2))

    # ворота → тримати (назад у підозрюваних)
    f.append(line(1100, 395, 1150, 395, color=NEG, sw=2))
    f.append(line(1150, 395, 1150, 190, color=NEG, sw=2))
    f.append(arrow(1150, 190, 1076, 190, color=NEG, sw=2))
    f.append(text(1150, 168, "тримати", size=12, color=NEG, bold=True))

    # ворота → СТЕРТИЙ
    f.append(line(830, 452, 830, 560, color=MUTED, sw=2))
    f.append(arrow(830, 560, 624, 560, color=MUTED, sw=2))
    f.append(text(740, 540, "віримо собі — стерти", size=12.5, color=MUTED, bold=True))

    # ЖИВИЙ → СТЕРТИЙ навпростець
    f.append(arrow(440, 232, 440, 516, color=MUTED, sw=2))
    f.append(mtext(420, 360, ["«я йду» — підказка:", "стерти одразу,",
                              "живих −1 і відомих −1"],
                   size=12.5, color=MUTED, anchor="end"))

    f.append(fitbox(70, 615, 1060, 62,
                    "підозрюваний ЛИШАЄТЬСЯ в таблиці — саме він тримає знаменник порога;\n"
                    "стирати відразу — значить ніколи не побачити масового витікання",
                    size=13.5, bold=True, fill=FILL))

    render(os.path.join(OUT, 'entry-lifecycle.svg'), W, H, *f)


# ── Бюджет строку: з чого складається D (вставка math-refresh-timing) ───────
def refresh_budget():
    W, H = 1180, 560
    f = []

    x0, x1 = 80.0, 1020.0
    Dtot = 24.3                      # с
    sc = (x1 - x0) / Dtot            # px на секунду
    T, jj, k = 5.0, 0.2, 4

    f.append(fitbox(80, 46, 940, 44,
                    "бюджет строку D при T = 5 с, розкид ±20 %, ΔL = 0.3 с, k = 4",
                    size=14.5, bold=True, fill=COOL))

    ybar, hbar = 210.0, 56.0

    for i in range(k):
        xs = x0 + sc * T * i
        f.append(rect(xs, ybar, sc * T, hbar, fill=GOOD, stroke=FIELD, sw=1.6))
        f.append(text(xs + sc * T / 2, ybar + hbar / 2 + 5, "T = 5 с", size=14))

    xj = x0 + sc * T * k
    wj = sc * (k * jj * T)
    f.append(rect(xj, ybar, wj, hbar, fill=COOL, stroke=NEG, sw=1.6))
    f.append(text(xj + wj / 2, ybar + hbar / 2 + 5, "k·j·T", size=14, color=NEG,
                  bold=True))

    xl = xj + wj
    wl = x1 - xl
    f.append(rect(xl, ybar, wl, hbar, fill=WARM, stroke=POS, sw=1.6))

    for i in range(1, k + 1):
        x = x0 + sc * (1 + jj) * T * i
        f.append(arrow(x, 132, x, ybar - 6, color=FIELD))
        f.append(text(x, 122, str(i), size=13, color=FIELD, bold=True))
    f.append(text(x0, 122, "найпізніший прихід оновлення №", size=13, color=FIELD,
                  anchor="start", bold=True))

    yD = ybar + hbar + 36
    f.append(line(x0, yD, x1, yD, color=INK, sw=1.8))
    f.append(line(x0, yD - 8, x0, yD + 8, color=INK, sw=1.8))
    f.append(line(x1, yD - 8, x1, yD + 8, color=INK, sw=1.8))
    f.append(text((x0 + x1) / 2, yD + 26, "D = 24.3 с", size=15, bold=True))

    f.append(line(xl + wl / 2, ybar - 12, xl + wl / 2 + 34, ybar - 44, color=POS, sw=1.4))
    f.append(text(xl + wl / 2 + 40, ybar - 48, "ΔL", size=13, color=POS, bold=True,
                  anchor="end"))

    ley = 360.0
    items = [
        (GOOD, FIELD, "k·T = 20 с — стільки оновлень мусить умістити вікно, "
                      "щоб пережити k−1 = 3 мовчазні втрати"),
        (COOL, NEG,   "k·j·T = 4.0 с — інтервали розмазані випадково, "
                      "тож кожен буває на 20 % довшим за номінал"),
        (WARM, POS,   "ΔL = 0.3 с — РІЗНИЦЯ найдовшої й найкоротшої затримки, "
                      "а не сама затримка"),
    ]
    for i, (fl, st, s) in enumerate(items):
        y = ley + i * 42
        f.append(rect(80, y, 30, 24, fill=fl, stroke=st, sw=1.6))
        f.append(text(124, y + 18, s, size=13.5, anchor="start"))

    f.append(fitbox(80, 496, 940, 44,
                    "хід годинників додає ще k·T·ρ = 2 мс при ρ = 10⁻⁴ — "
                    "у цьому масштабі сегмент невидимий, зате росте разом із k·T",
                    size=13.5, fill=FILL))

    render(os.path.join(OUT, 'refresh-budget.svg'), W, H, *f)


# ── Коліно: два доданки хибних витікань проти строку D ──────────────────────
def false_expiry_knee():
    import math
    W, H = 1180, 660
    f = []

    xa, xb = 165.0, 1090.0
    Da, Db = 18.0, 85.0
    ya, yb = 140.0, 540.0
    la, lb = 1.0, -3.0

    def X(d): return xa + (d - Da) / (Db - Da) * (xb - xa)
    def Y(v):
        l = max(min(math.log10(v), la), lb)
        return ya + (la - l) / (la - lb) * (yb - ya)

    tick = {1: "10¹", 0: "10⁰", -1: "10⁻¹", -2: "10⁻²", -3: "10⁻³"}
    for e in range(-3, 2):
        y = Y(10.0 ** e)
        f.append(line(xa, y, xb, y, color="#dde2e8", sw=1.0))
        f.append(text(xa - 12, y + 5, tick[e], size=13, color=MUTED, anchor="end"))
    for d in (20, 30, 40, 50, 60, 70, 80):
        f.append(line(X(d), yb, X(d), yb + 6, color=MUTED, sw=1.2))
        f.append(text(X(d), yb + 24, str(d), size=13, color=MUTED))
    f.append(line(xa, ya, xa, yb, color=INK, sw=1.6))
    f.append(line(xa, yb, xb, yb, color=INK, sw=1.6))
    f.append(text(xb, yb + 48, "строк D, с →", size=13.5, color=MUTED, anchor="end"))
    f.append(text(xa - 60, ya - 26, "хибних витікань за добу на 2000 записів",
                  size=13.5, color=MUTED, anchor="start"))

    T, jr, dL, p, N = 5.0, 1.2, 0.3, 0.005, 2000

    def ind(D):
        kk = int((D - dL) // (jr * T))
        return N * (1 - p) * p ** kk / T * 86400.0

    edges = [Da]
    kk = 3
    while jr * T * kk + dL < Db:
        edges.append(jr * T * kk + dL)
        kk += 1
    edges.append(Db)
    prev = None
    for i in range(len(edges) - 1):
        d0, d1 = edges[i], edges[i + 1]
        v = ind((d0 + d1) / 2)
        if v < 10 ** lb:
            if prev is not None:
                f.append(line(X(d0), prev, X(d0), yb, color=NEG, sw=2.4))
                f.append(text(X(d0) + 12, yb - 14, "↓ нижче 10⁻³", size=12.5,
                              color=NEG, anchor="start"))
            break
        y = Y(v)
        f.append(line(X(d0), y, X(d1), y, color=NEG, sw=2.6))
        if prev is not None:
            f.append(line(X(d0), prev, X(d0), y, color=NEG, sw=2.4))
        prev = y

    lam = 1 / 30.0
    d = Da
    pts = []
    while d <= Db + 0.01:
        pts.append((X(d), Y(N * lam / (d - T / 2))))
        d += 1.0
    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                      color=POS, sw=2.6))

    d = Da
    tot = []
    while d <= Db + 0.01:
        tot.append((X(d), Y(ind(d) + N * lam / (d - T / 2))))
        d += 0.5
    for i in range(len(tot) - 1):
        f.append(line(tot[i][0], tot[i][1], tot[i + 1][0], tot[i + 1][1],
                      color=INK, sw=1.6, dash="6,4"))

    xk = X(24.3)
    f.append(line(xk, ya - 6, xk, yb, color=MUTED, sw=1.6, dash="5,5"))
    f.append(fitbox(xk + 18, 166, 340, 76,
                    "коліно: D = 24.3 с (k = 4)\nлівіше вирішує експонента,\n"
                    "правіше — лише хвіст вибоїв",
                    size=13, bold=True, fill=FILL, stroke=MUTED, sw=1.3))

    lg = [(NEG, "незалежні втрати: (1−p)·pᵏ/T — на кожен крок k у 200 разів менше"),
          (POS, "вибої з важким хвостом: спадає лише як 1/D"),
          (INK, "разом")]
    for i, (c, s) in enumerate(lg):
        y = 592 + i * 22
        f.append(line(xa, y - 4, xa + 40, y - 4, color=c, sw=2.6))
        f.append(text(xa + 52, y, s, size=12.5, anchor="start"))

    render(os.path.join(OUT, 'false-expiry-knee.svg'), W, H, *f)


# ── Оптимум за T: фон проти застарілости ────────────────────────────────────
def cost_optimum():
    import math
    W, H = 1120, 580
    f = []

    xa, xb = 165.0, 1030.0
    ya, yb = 120.0, 450.0
    la, lb = -0.6, 0.6
    Cmax = 3.0

    def X(t): return xa + (math.log10(t) - la) / (lb - la) * (xb - xa)
    def Y(c): return yb - min(c, Cmax) / Cmax * (yb - ya)

    yband = Y(1.35)
    f.append(rect(X(0.5), yband, X(2.0) - X(0.5), yb - yband, fill="#f0f7f2",
                  stroke="#cfe3d7", sw=1.2, rx=4))

    for c in (0, 1, 2, 3):
        f.append(line(xa, Y(c), xb, Y(c), color="#dde2e8", sw=1.0))
        f.append(text(xa - 12, Y(c) + 5, ("%d·C*" % c) if c else "0", size=13,
                      color=MUTED, anchor="end"))
    for t, s in ((0.25, "T*/4"), (0.5, "T*/2"), (1.0, "T*"), (2.0, "2·T*"),
                 (4.0, "4·T*")):
        f.append(line(X(t), yb, X(t), yb + 6, color=MUTED, sw=1.2))
        f.append(text(X(t), yb + 24, s, size=13, color=MUTED))
    f.append(line(xa, ya, xa, yb, color=INK, sw=1.6))
    f.append(line(xa, yb, xb, yb, color=INK, sw=1.6))

    def curve(fn, color, sw=2.6, dash=None):
        n = 120
        pts = []
        for i in range(n + 1):
            t = 10 ** (la + (lb - la) * i / n)
            pts.append((X(t), Y(fn(t))))
        for i in range(n):
            f.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                          color=color, sw=sw, dash=dash))

    curve(lambda t: 0.5 / t, NEG)
    curve(lambda t: 0.5 * t, POS)
    curve(lambda t: 0.5 * (t + 1 / t), INK, 2.0, dash="7,4")

    f.append(line(X(1.0), ya, X(1.0), yb, color=MUTED, sw=1.5, dash="5,5"))
    f.append(circle(X(1.0), Y(1.0), 6, fill="#ffffff", stroke=INK, sw=2))

    f.append(fitbox(X(1.0) + 24, 138, 330, 72,
                    "у мінімумі доданки рівні:\nфон коштує рівно стільки ж,\n"
                    "скільки застарілість",
                    size=13, bold=True, fill=FILL, stroke=MUTED, sw=1.3))
    f.append(fitbox(X(0.5), yb - 76, X(2.0) - X(0.5), 44,
                    "помилка вдвічі в будь-який бік — переплата 25 %",
                    size=12.5, fill="#ffffff", stroke=FIELD, sw=1.4))

    lg = [(NEG, "фон оновлень: c_m·N/T"),
          (POS, "застарілість: c_s·N·λ_d·(r − ½)·T"),
          (INK, "разом: C(T)/C* = ½·(T/T* + T*/T)")]
    for i, (c, s) in enumerate(lg):
        y = 512 + i * 22
        f.append(line(xa, y - 4, xa + 40, y - 4, color=c, sw=2.6))
        f.append(text(xa + 52, y, s, size=12.5, anchor="start"))

    f.append(text(xb, yb + 48, "період T у частках оптимального T* →", size=13.5,
                  color=MUTED, anchor="end"))

    render(os.path.join(OUT, 'cost-optimum.svg'), W, H, *f)


# ── Родовід ідеї: три спільноти, один механізм (вставка hist) ────────────────
def lineage_timeline():
    W, H = 1250, 910
    f = []

    cols = [
        (140.0, "СИГНАЛІЗАЦІЯ В МЕРЕЖІ"),
        (500.0, "СХОВИЩА Й ФАЙЛОВІ СИСТЕМИ"),
        (860.0, "СЛУЖБИ Й ТЕОРІЯ"),
    ]
    CW = 340.0          # ширина колонки
    BW = CW - 24        # ширина картки в колонці
    BH = 88.0

    for cx, name in cols:
        f.append(fitbox(cx + 12, 20, BW, 48, name, size=12.5, bold=True, fill=COOL))

    # вертикальні межі колонок — поза картками, тексту не чіпають
    for x in (132.0, 492.0, 852.0, 1212.0):
        f.append(line(x, 82, x, 880, color=MUTED, sw=0.9, dash="4,6"))

    rows = [
        (100.0, "1988", 0, "Кларк, SIGCOMM 1988\nfate-sharing і назва «soft state»\n"
                           "описано прикладом, без визначення"),
        (210.0, "1989", 1, "Ґрей і Черітон, SOSP 1989\nліза: право з обмеженим строком\n"
                           "інша спільнота, та сама механіка"),
        (320.0, "1993", 0, "Чжан, Дірінг, Естрін, Шенкер, Заппала\n"
                           "RSVP, IEEE Network 1993\nперше велике втілення"),
        (430.0, "1997", 0, "RFC 2205 — RSVP стає стандартом\n"
                           "PathTear і ResvTear лише рекомендовані"),
        (430.0, None,  2, "Фокс, Ґріббл, Чаватхе, Бревер, Ґот'є\nBASE, SOSP 1997\n"
                          "м'який стан у кластері служб"),
        (540.0, "1999", 2, "Раман і Мак-Кенн, SIGCOMM 1999\n"
                           "формальна модель і міра узгоджености"),
        (650.0, "2001", 0, "RFC 2961 — ціна фону падає:\n"
                           "зведені рефреші, підтвердження змін"),
        (760.0, "2003", 2, "Джі, Ґе, Куроуз, Тауслі, SIGCOMM 2003\n"
                           "виміряний спектр між м'яким і твердим"),
    ]

    for y, year, col, s in rows:
        if year is not None:
            f.append(line(30, y - 14, 1212, y - 14, color=MUTED, sw=0.9, dash="3,7"))
            f.append(text(112, y + 34, year, size=17, bold=True, color=NEG, anchor="end"))
        cx = cols[col][0]
        f.append(fitbox(cx + 12, y, BW, BH, s, size=12.5, fill=FILL, stroke=LINE, sw=1.4))

    f.append(text(1212, 898, "час →", size=13, color=MUTED, anchor="end"))
    render(os.path.join(OUT, 'lineage-timeline.svg'), W, H, *f)


# ── Відрізок від чистого м'якого до чистого твердого стану (вставка hist) ────
def soft_hard_spectrum():
    W, H = 1250, 430
    f = []

    ax = 215.0
    xs = [165.0, 470.0, 775.0, 1080.0]
    BW, BH = 250.0, 130.0

    labels = [
        ("чистий м'який стан\n\nлише періодичні оновлення\nі строк на боці приймача", GOOD),
        ("+ явне видалення\n\nPathTear і ResvTear у RSVP\nбез підтвердження доставки", GOOD),
        ("+ надійна доставка змін\n\nRFC 2961: ідентифікатори,\nзведені рефреші, квитанції", COOL),
        ("чистий твердий стан\n\nвстановлення й розбирання\nпо разу: Q.2931, ST-II", WARM),
    ]

    f.append(line(90, ax, 1170, ax, color=INK, sw=2))
    for x, (s, bg) in zip(xs, labels):
        f.append(fitbox(x - BW / 2, 55, BW, BH, s, size=12.5, fill=bg,
                        stroke=LINE, sw=1.4))
        f.append(arrow(x, 190, x, ax - 8, color=MUTED, sw=1.5))
        f.append(circle(x, ax, 7, fill=BG, stroke=INK, sw=2))

    f.append(text(92, ax + 30, "менше зобов'язань, більше фону", size=12.5,
                  color=MUTED, anchor="start"))
    f.append(text(1168, ax + 30, "більше зобов'язань, менше фону", size=12.5,
                  color=MUTED, anchor="end"))

    f.append(fitbox(70, 285, 1110, 110,
                    "SIGCOMM 2003: одна модель накрила весь відрізок. Явне видалення "
                    "коштує майже нічого, а розходження станів зменшує різко;\n"
                    "з надійною доставкою змін м'який стан наздоганяє твердий за "
                    "узгодженістю — тож протоколи не такі різні, як здається.",
                    size=13.5, fill=FILL, stroke=MUTED, sw=1.3))

    render(os.path.join(OUT, 'soft-hard-spectrum.svg'), W, H, *f)


hard_vs_soft()
refresh_window()
expiry_spiral()
registry_structure()
entry_lifecycle()
refresh_budget()
false_expiry_knee()
cost_optimum()
lineage_timeline()
soft_hard_spectrum()
print("готово:", ", ".join(sorted(os.listdir(OUT))))
