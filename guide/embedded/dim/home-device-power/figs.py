# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def power_path():
    # Ланцюг щаблів від розетки до чипа з бар'єром ізоляції посередині:
    # ліва половина (до бар'єра) — гарячий бік мережі, права — безпечний бік логіки.
    W, H = 760, 380
    p = []
    cy = 176
    bh = 92           # висота блоків
    top = cy - bh / 2

    # координати центрів чотирьох робочих блоків + позиція бар'єра
    xs = [92, 244, 430, 638]     # розетка, захист, AC/DC, регулятор+MCU
    barrier_x = (xs[1] + 22 + xs[2] - 22) / 2   # між захистом і AC/DC? ні — всередині AC/DC
    # бар'єр малюємо ВСЕРЕДИНІ блока AC/DC (він і є місцем розриву)

    # --- фонові півполя: гарячий (ліворуч) і безпечний (праворуч) ---
    split = xs[2]                 # вертикаль розриву проходить крізь AC/DC
    p.append(rect(24, 58, split - 24, H - 96, fill="#fdecea", stroke="none", sw=0, rx=8))
    p.append(rect(split, 58, W - 24 - split, H - 96, fill="#eafaf0", stroke="none", sw=0, rx=8))
    p.append(text((24 + split) / 2, 78, "НЕБЕЗПЕЧНИЙ БІК — мережа, не торкатися",
                  size=12, color=POS, bold=True))
    p.append(text((split + W - 24) / 2, 78, "БЕЗПЕЧНИЙ БІК — логіка, дотик дозволено",
                  size=12, color=FIELD, bold=True))

    bw = 128
    def block(cx, lines, col, fill):
        p.append(rect(cx - bw / 2, top, bw, bh, fill=fill, stroke=col, sw=2.2))
        p.append(mtext(cx, cy - (len(lines) - 1) * 8, lines, size=13, color=col, bold=True))

    # 1. розетка
    block(xs[0], ["Розетка", "230 В ~", "50 Гц"], POS, "#fff")
    # 2. вхідний захист
    block(xs[1], ["Вхідний захист", "запобіжник", "+ варистор"], POS, "#fff")
    # 3. ізольований AC/DC (широкий — крізь нього йде бар'єр)
    acw = 150
    p.append(rect(xs[2] - acw / 2, top, acw, bh, fill="#fff", stroke=INK, sw=2.2))
    p.append(text(xs[2], cy - 20, "Ізольований", size=13, color=INK, bold=True))
    p.append(text(xs[2], cy - 4, "AC/DC → 5 В", size=13, color=INK, bold=True))
    p.append(text(xs[2], cy + 16, "розрив землі", size=11, color=MUTED))
    # 4. точковий регулятор + MCU
    block(xs[3], ["Регулятор", "→ 3.3 В", "+ MCU"], FIELD, "#fff")

    # --- бар'єр ізоляції: жирна вертикаль крізь блок AC/DC ---
    p.append(line(xs[2], 58, xs[2], H - 38, color=INK, sw=3, dash="7 5"))
    p.append(text(xs[2], H - 22, "бар'єр гальванічної розв'язки",
                  size=12, color=INK, bold=True))

    # --- стрілки потоку між блоками ---
    p.append(arrow(xs[0] + bw / 2, cy, xs[1] - bw / 2, cy, color=POS, sw=2))
    p.append(arrow(xs[1] + bw / 2, cy, xs[2] - acw / 2, cy, color=POS, sw=2))
    p.append(arrow(xs[2] + acw / 2, cy, xs[3] - bw / 2, cy, color=FIELD, sw=2))

    # підпис під переходом крізь бар'єр: енергія лише полем
    p.append(text(xs[2], cy + 40, "енергія — лише полем", size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, 'power-path.svg'), W, H, *p,
           title="Тракт живлення: чотири щаблі від 230 В до 3.3 В")


def standby_budget():
    # Дві стовпчасті колонки спокою (поганий vs добрий вузол); кожна — стек із
    # двох складових: власне споживання блока + сон MCU. Пунктир — межа нормативу.
    W, H = 720, 430
    p = []
    base_y = 350              # рівень «нуля» стовпчиків
    scale = 190.0 / 0.6       # 0.6 Вт → 190 px висоти

    def bar(cx, p_supply, p_mcu, label, good):
        w = 120
        # блок живлення (нижній сегмент — гарячий колір)
        hs = p_supply * scale
        hm = max(p_mcu * scale, 5)      # видимий мінімум для мікровата
        # нижній: supply
        p.append(rect(cx - w / 2, base_y - hs, w, hs,
                      fill="#fdecea", stroke=POS, sw=2))
        # верхній: MCU sleep
        p.append(rect(cx - w / 2, base_y - hs - hm, w, hm,
                      fill="#eafaf0", stroke=FIELD, sw=2))
        # підпис колонки
        p.append(text(cx, base_y + 22, label, size=13,
                      color=(POS if not good else FIELD), bold=True))
        p.append(text(cx, base_y + 40, "(спокій вузла)", size=11, color=MUTED))
        # сума зверху
        tot = p_supply + p_mcu
        p.append(text(cx, base_y - hs - hm - 12,
                      "разом ≈ %.2f Вт" % tot, size=12, color=INK, bold=True))
        return hs, hm

    # ліворуч — поганий: блок 0.5 Вт, MCU уві сні мізерний
    hs1, hm1 = bar(210, 0.5, 0.00003, "ПОГАНИЙ", good=False)
    # маркування сегментів лівої колонки
    p.append(text(210, base_y - hs1 / 2 + 4, "блок ж-ня", size=11, color=POS, bold=True))
    # виноска до тонкої смужки MCU збоку зверху колонки
    p.append(text(210 - 78, base_y - hs1 - hm1 / 2 - 2, "MCU уві сні", size=10,
                  color=FIELD, anchor="end"))
    p.append(line(210 - 76, base_y - hs1 - hm1 / 2, 210 - 60, base_y - hs1 - hm1 / 2,
                  color=FIELD, sw=1))

    # праворуч — добрий: блок 0.03 Вт, MCU так само мізерний
    hs2, hm2 = bar(510, 0.03, 0.00003, "ДОБРИЙ", good=True)
    # виноска до крихітного стовпчика збоку (щоб не налізла на «разом»)
    p.append(text(510 + 78, base_y - hs2 / 2, "блок тихий", size=11, color=POS,
                  anchor="start", bold=True))
    p.append(line(510 + 62, base_y - hs2 / 2, 510 + 76, base_y - hs2 / 2,
                  color=POS, sw=1))

    # межа нормативу standby (пунктир) — умовна лінія
    y_norm = base_y - 0.3 * scale
    p.append(line(120, y_norm, W - 60, y_norm, color=NEG, sw=1.8, dash="7 5"))
    p.append(text(W - 56, y_norm - 6, "межа нормативу", size=12, color=NEG,
                  anchor="end", bold=True))

    # вісь-нуль
    p.append(line(120, base_y, W - 60, base_y, color=INK, sw=1.2))

    # висновок
    p.append(text(W / 2, base_y + 66,
                  "сплячий чип не рятує, якщо блок живлення марнує сам по собі",
                  size=12, color=INK, bold=True))

    render(os.path.join(IMG, 'standby-budget.svg'), W, H, *p,
           title="Куди тікають міліватти в спокої: блок живлення проти сну чипа")


def standby_history():
    # Часова смуга: як стеля дозволеного standby падала від «нерегульованого»
    # (10–15 Вт на пристрій) через One-Watt (1 Вт), EC 1275/2008 (1 → 0.5 Вт)
    # до (EU) 2023/826 (0.3 Вт). Вертикаль — стеля у ватах (лог-подібна шкала
    # вручну, бо діапазон від 15 до 0.3 Вт), точки-віхи на осі часу.
    W, H = 780, 430
    p = []
    x0, x1 = 96, W - 40          # межі осі часу
    y_base = 300                 # рівень осі часу
    y_top = 70                   # верх поля стелі

    # роки-віхи на осі часу
    yr0, yr1 = 1990, 2028
    def X(year):
        return x0 + (year - yr0) / (yr1 - yr0) * (x1 - x0)

    # стеля standby → висота (ручна «стисла» шкала: 15 Вт високо, 0.3 Вт низько)
    import math
    def Y(watt):
        # log10: 15→1.176, 1→0, 0.3→-0.523; мапимо [−0.6 .. 1.2] у [y_base .. y_top]
        lo, hi = -0.6, 1.2
        v = max(min(math.log10(watt), hi), lo)
        return y_base - (v - lo) / (hi - lo) * (y_base - y_top)

    # горизонтальні орієнтири стелі
    for wv, lab in [(10, "10 Вт"), (1, "1 Вт"), (0.5, "0.5 Вт"), (0.3, "0.3 Вт")]:
        yy = Y(wv)
        p.append(line(x0, yy, x1, yy, color="#e2e6ea", sw=1))
        p.append(text(x0 - 8, yy + 4, lab, size=11, color=MUTED, anchor="end"))

    # спадна «сходинкова» лінія стелі дозволеного standby
    steps = [
        (1990, 12), (1999, 12),          # до регулювання — 10–15 Вт (беремо 12)
        (1999, 12),                       # One-Watt лише мета, не норма
        (2010, 1.0), (2013, 1.0),         # EC 1275/2008: 1 Вт від 2010
        (2013, 0.5), (2025, 0.5),         # халвінг 2013 → 0.5 Вт
        (2025, 0.5), (2027, 0.5),
        (2027, 0.3), (2028, 0.3),         # (EU) 2023/826: 0.3 Вт від 2027
    ]
    for i in range(len(steps) - 1):
        (ya, wa), (yb, wb) = steps[i], steps[i + 1]
        p.append(line(X(ya), Y(wa), X(yb), Y(wb), color=POS, sw=2.6))

    # підпис зони: ЛІВОРУЧ від початку спадної лінії (x < X(1999)) і нижче
    # горизонтальної полиці 12 Вт — двома короткими рядками, щоб жодна лінія
    # стелі не перетнула напис
    p.append(mtext(104, Y(12) + 20, ["нерегульовано:", "10–15 Вт/пристрій"],
                   size=11, color=POS, bold=True, anchor="start", lh=1.25))

    # вісь часу
    p.append(line(x0, y_base, x1, y_base, color=INK, sw=1.4))
    for yr in [1990, 1999, 2008, 2013, 2025, 2027]:
        xx = X(yr)
        p.append(line(xx, y_base - 4, xx, y_base + 4, color=INK, sw=1.2))
        p.append(text(xx, y_base + 20, str(yr), size=11, color=INK))

    # віхи-події (кружечок на лінії стелі + виноска)
    def milestone(year, watt, lines, dy, dx=0):
        xx, yy = X(year), Y(watt)
        bx, by = xx + dx, yy + dy
        p.append(circle(xx, yy, 5, fill="#fff", stroke=POS, sw=2.2))
        box, bw, bh = textbox(bx, by, "\n".join(lines), size=11,
                              pad=7, fill="#fff", stroke=INK, sw=1.4, color=INK)
        # з'єднати кружечок із краєм рамки (діагональ, якщо є зсув)
        edge_y = by - (bh / 2 if dy > 0 else -bh / 2)
        p.append(line(xx, yy, bx, edge_y, color=MUTED, sw=1, dash="3 3"))
        p.append(box)

    milestone(1999, 12, ["One-Watt (IEA)", "мета: 1 Вт до 2010"], -46)
    # EC 1275: рамку зсуваємо ПРАВОРУЧ від кружечка, щоб спадна лінія стелі
    # (яка приходить згори-зліва) не перетнула напис
    milestone(2010, 1.0, ["EC 1275/2008", "1 Вт від 2010"], -30, dx=92)
    # халвінг: рамку зсуваємо праворуч у чистий проміжок під віссю (щоб не
    # налізти на мітку року «2013» і не перетнути її лінією-виноскою)
    milestone(2013, 0.5, ["халвінг 2013", "→ 0.5 Вт"], 96, dx=74)
    milestone(2027, 0.3, ["(EU) 2023/826", "0.3 Вт від 2027"], -46)

    # підпис-стрілка «напрямок»
    p.append(text(W / 2, H - 24,
                  "стеля дозволеного standby падала в десятки разів за чверть століття",
                  size=12, color=INK, bold=True))

    render(os.path.join(IMG, 'standby-history.svg'), W, H, *p,
           title="Як стягували гайку: дозволений standby від 15 Вт до 0.3 Вт")


def creepage_clearance():
    # Дві відстані бар'єра: зазор (пряма крізь повітря) vs шлях витоку (уздовж
    # поверхні). Внизу — слот у платі, що подовжує creepage, не змінюючи clearance.
    W, H = 760, 430
    p = []

    # ── верхня сцена: дві доріжки на платі, розріз збоку ──
    board_y = 150
    board_h = 26
    hot_x0, hot_x1 = 70, 300        # гаряча доріжка
    cold_x0, cold_x1 = 430, 690     # холодна доріжка
    gap_l, gap_r = hot_x1, cold_x0  # проміжок

    # тіло плати (текстоліт)
    p.append(rect(60, board_y, W - 120, board_h, fill="#f0ead6", stroke=MUTED, sw=1.5, rx=3))
    # мідні доріжки зверху плати
    p.append(rect(hot_x0, board_y - 8, hot_x1 - hot_x0, 8, fill="#fdecea", stroke=POS, sw=2, rx=2))
    p.append(rect(cold_x0, board_y - 8, cold_x1 - cold_x0, 8, fill="#eafaf0", stroke=FIELD, sw=2, rx=2))
    p.append(text((hot_x0 + hot_x1) / 2, board_y - 16, "гаряча (230 В)", size=12, color=POS, bold=True))
    p.append(text((cold_x0 + cold_x1) / 2, board_y - 16, "холодна (5 В)", size=12, color=FIELD, bold=True))

    # ЗАЗОР — пряма повітрям між краями доріжок (над платою)
    y_clear = board_y - 40
    p.append(line(gap_l, board_y - 4, gap_l, y_clear, color=MUTED, sw=1, dash="3 3"))
    p.append(line(gap_r, board_y - 4, gap_r, y_clear, color=MUTED, sw=1, dash="3 3"))
    p.append(arrow(gap_l, y_clear, gap_r, y_clear, color=NEG, sw=2))
    p.append(arrow(gap_r, y_clear, gap_l, y_clear, color=NEG, sw=2))
    p.append(text((gap_l + gap_r) / 2, y_clear - 8, "ЗАЗОР — пряма крізь повітря", size=13, color=NEG, bold=True))

    # ШЛЯХ ВИТОКУ — по поверхні плати (під доріжками, огинає край)
    y_creep = board_y + board_h + 10
    # ламана лінія вздовж поверхні від гарячого краю до холодного
    p.append(line(gap_l, board_y, gap_l, y_creep, color=POS, sw=2.4))
    p.append(line(gap_l, y_creep, gap_r, y_creep, color=POS, sw=2.4))
    p.append(line(gap_r, y_creep, gap_r, board_y, color=POS, sw=2.4))
    p.append(text((gap_l + gap_r) / 2, y_creep + 18, "ШЛЯХ ВИТОКУ — уздовж поверхні (довший!)",
                  size=13, color=POS, bold=True))

    # ── нижня сцена: той самий проміжок, але з прорізаним слотом ──
    by = 320
    bh = 26
    p.append(rect(60, by, W - 120, bh, fill="#f0ead6", stroke=MUTED, sw=1.5, rx=3))
    p.append(rect(hot_x0, by - 8, hot_x1 - hot_x0, 8, fill="#fdecea", stroke=POS, sw=2, rx=2))
    p.append(rect(cold_x0, by - 8, cold_x1 - cold_x0, 8, fill="#eafaf0", stroke=FIELD, sw=2, rx=2))
    # слот (наскрізна щілина в платі посередині проміжку)
    slot_cx = (gap_l + gap_r) / 2
    slot_w = 40
    p.append(rect(slot_cx - slot_w / 2, by - 3, slot_w, bh + 6, fill=BG, stroke=INK, sw=1.6, rx=2))
    # подовжений шлях витоку: униз у слот, по дну, вгору, і далі
    sy = by + bh + 14
    p.append(line(gap_l, by, gap_l, sy, color=POS, sw=2.4))
    p.append(line(gap_l, sy, slot_cx - slot_w / 2, sy, color=POS, sw=2.4))
    p.append(line(slot_cx - slot_w / 2, sy, slot_cx - slot_w / 2, by - 3, color=POS, sw=2.4))
    p.append(line(slot_cx - slot_w / 2, by - 3, slot_cx + slot_w / 2, by - 3, color=POS, sw=2.4))
    p.append(line(slot_cx + slot_w / 2, by - 3, slot_cx + slot_w / 2, sy, color=POS, sw=2.4))
    p.append(line(slot_cx + slot_w / 2, sy, gap_r, sy, color=POS, sw=2.4))
    p.append(line(gap_r, sy, gap_r, by, color=POS, sw=2.4))
    p.append(text(slot_cx, by + bh + 30, "слот подовжує шлях витоку — зазор незмінний",
                  size=12, color=INK, bold=True))
    p.append(text(slot_cx, by - 20, "проріз", size=11, color=INK))

    render(os.path.join(IMG, 'creepage-clearance.svg'), W, H, *p,
           title="Бар'єр тримають дві відстані: зазор і шлях витоку")


def ldo_buck_crossover():
    # Дві прямі втрат від струму: крута LDO (нахил = Vdrop) і полога buck
    # (нахил = недобір ККД). Горизонталь — теплова стеля корпусу LDO; де вона
    # ріже лінію LDO — струм перелому.
    W, H = 740, 440
    p = []
    x0, x1 = 90, W - 60          # вісь струму
    y0, y1 = 360, 70             # вісь потужності (низ..верх)
    Imax = 0.6                   # А (правий край осі)
    Pmax_axis = 0.9              # Вт (верх осі)

    def X(i):  return x0 + i / Imax * (x1 - x0)
    def Y(pw): return y0 - pw / Pmax_axis * (y0 - y1)

    # осі
    p.append(line(x0, y0, x1, y0, color=INK, sw=1.4))       # вісь X
    p.append(line(x0, y0, x0, y1, color=INK, sw=1.4))       # вісь Y
    p.append(text((x0 + x1) / 2, y0 + 42, "струм навантаження I, А", size=12, color=INK))
    # мітки осі X
    for iv in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
        p.append(line(X(iv), y0, X(iv), y0 + 4, color=INK, sw=1))
        p.append(text(X(iv), y0 + 20, "%.1f" % iv, size=10, color=INK))
    # підпис осі Y (вертикально збоку)
    p.append(text(x0 - 62, (y0 + y1) / 2, "втрати", size=12, color=INK))
    p.append(text(x0 - 62, (y0 + y1) / 2 + 16, "P, Вт", size=12, color=INK))
    for pv in [0, 0.2, 0.4, 0.6, 0.8]:
        p.append(line(x0 - 4, Y(pv), x0, Y(pv), color=INK, sw=1))
        p.append(text(x0 - 12, Y(pv) + 4, "%.1f" % pv, size=10, color=INK, anchor="end"))

    # теплова стеля корпусу LDO (Pmax ≈ 0.34 Вт)
    Pceil = 0.34
    p.append(line(x0, Y(Pceil), x1, Y(Pceil), color=MUTED, sw=1.6, dash="7 5"))
    p.append(text(x1 - 6, Y(Pceil) - 8, "теплова стеля корпусу LDO", size=11,
                  color=MUTED, anchor="end", bold=True))

    # лінія LDO: P = 1.7 * I
    p.append(line(X(0), Y(0), X(Imax), Y(1.7 * Imax), color=POS, sw=2.8))
    # лінія buck: P = 0.367 * I
    p.append(line(X(0), Y(0), X(Imax), Y(0.367 * Imax), color=FIELD, sw=2.8))

    # точка перелому: 1.7 * I = 0.34 → I = 0.20
    Icross = Pceil / 1.7
    p.append(circle(X(Icross), Y(Pceil), 5.5, fill="#fff", stroke=POS, sw=2.4))
    p.append(line(X(Icross), y0, X(Icross), Y(Pceil), color=POS, sw=1, dash="3 3"))
    p.append(text(X(Icross), y0 + 34, "перелом ≈ 0.20 А", size=11, color=POS, bold=True))

    # підписи ліній (біля правих кінців, рознесені по вертикалі з запасом)
    box1, _, _ = textbox(X(0.46), Y(1.7 * 0.46) + 4, "LDO: нахил = 1.7 В\n(усе падіння в тепло)",
                         size=11, color=POS, stroke=POS, fill="#fff", pad=6)
    p.append(box1)
    box2, _, _ = textbox(X(0.46), Y(0.367 * 0.6) - 22, "buck: нахил = 0.37\n(лише недобір ККД)",
                         size=11, color=FIELD, stroke=FIELD, fill="#fff", pad=6)
    p.append(box2)

    render(os.path.join(IMG, 'ldo-buck-crossover.svg'), W, H, *p,
           title="Струм перелому: де тепло LDO пробиває стелю корпусу")


def no_load_sources():
    # Дерево п'яти джерел власного споживання блока на холостому ходу (ліворуч),
    # і як burst-режим гасить більшість із них (праворуч).
    W, H = 780, 440
    p = []

    # ── ліва колонка: п'ять струмочків «готовності» ──
    lx = 60
    lw = 320
    p.append(text(lx + lw / 2, 60, "СТАРА архітектура: тече постійно", size=13, color=POS, bold=True))
    items = [
        ("Пусковий + розрядний резистор", "висить під 230 В, гріє завжди", POS),
        ("Живлення контролера", "схема керування споживає завжди", INK),
        ("Снабер", "гасить викид на кожному такті ключа", INK),
        ("Оптрон зворотного зв'язку", "світлодіод світить постійно", INK),
        ("Струм крізь Y-конденсатор", "тихо стікає на землю", MUTED),
    ]
    ry = 90
    rh = 54
    for i, (title_s, sub, col) in enumerate(items):
        y = ry + i * (rh + 8)
        p.append(rect(lx, y, lw, rh, fill="#fdf3f2" if col == POS else FILL,
                      stroke=col, sw=1.8))
        p.append(text(lx + 12, y + 22, title_s, size=12, color=col, bold=True, anchor="start"))
        p.append(text(lx + 12, y + 40, sub, size=10, color=MUTED, anchor="start"))
    # сумарна дужка праворуч від лівої колонки
    sum_x = lx + lw + 16
    p.append(line(sum_x, ry, sum_x, ry + 5 * (rh + 8) - 8, color=POS, sw=2))
    p.append(text(sum_x + 8, (ry + ry + 5 * (rh + 8) - 8) / 2 - 8, "разом", size=12, color=POS, bold=True, anchor="start"))
    p.append(text(sum_x + 8, (ry + ry + 5 * (rh + 8) - 8) / 2 + 10, "≈ 0.5 Вт", size=13, color=POS, bold=True, anchor="start"))

    # ── стрілка-перехід burst ──
    ax = 470
    p.append(arrow(ax - 8, H / 2, ax + 46, H / 2, color=INK, sw=2.4))
    p.append(text(ax + 20, H / 2 - 12, "burst-", size=12, color=INK, bold=True))
    p.append(text(ax + 20, H / 2 + 26, "режим", size=12, color=INK, bold=True))

    # ── права колонка: як burst гасить ──
    rx2 = 540
    rw2 = 200
    p.append(text(rx2 + rw2 / 2, 60, "НОВА: burst + HV-пуск", size=13, color=FIELD, bold=True))
    news = [
        ("Ключ мовчить між пачками", "снабер не гріє, контролер спить"),
        ("HV-пуск вимикається зовсім", "пусковий резистор не тече"),
        ("Розряд X-cap — активний", "лише коли зникла мережа"),
        ("Струмочки течуть частку часу", "середня потужність падає в рази"),
    ]
    for i, (t, s) in enumerate(news):
        y = 90 + i * 66
        p.append(rect(rx2, y, rw2, 56, fill="#eefaf2", stroke=FIELD, sw=1.8))
        p.append(fitbox(rx2 + 4, y + 4, rw2 - 8, 24, t, size=11, color=FIELD, bold=True,
                        fill="#eefaf2", stroke="none", sw=0))
        p.append(fitbox(rx2 + 4, y + 30, rw2 - 8, 22, s, size=9, color=MUTED,
                        fill="#eefaf2", stroke="none", sw=0))
    p.append(text(rx2 + rw2 / 2, 90 + 4 * 66 + 6, "разом ≈ десятки мВт", size=13, color=FIELD, bold=True))

    render(os.path.join(IMG, 'no-load-sources.svg'), W, H, *p,
           title="Куди течуть власні міліватти блока на холостому ходу")


if __name__ == '__main__':
    power_path()
    standby_budget()
    standby_history()
    creepage_clearance()
    ldo_buck_crossover()
    no_load_sources()
    print("ok")
