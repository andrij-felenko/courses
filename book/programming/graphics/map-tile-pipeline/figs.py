# -*- coding: utf-8 -*-
"""Фігури до теми «Тайловий конвеєр карти»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

HL = "#fdecea"   # підсвічений тайл
HL2 = "#eaf0fd"  # другий відтінок
SOFT = "#eef7ee"


# ── 1. Піраміда й вкладеність ───────────────────────────────────────────────
def pyramid():
    W, H = 1040, 500
    parts = []
    grids = [
        (70,  1, "рівень z",   "1 тайл на весь світ",  (0, 0)),
        (405, 2, "рівень z+1", "4 тайли",              (1, 1)),
        (740, 4, "рівень z+2", "16 тайлів",            (3, 2)),
    ]
    side, y0 = 230, 104
    for x0, n, top, bottom, hi in grids:
        cell = side / float(n)
        parts.append(text(x0 + side / 2, 84, top, size=15, bold=True))
        for r in range(n):
            for c in range(n):
                cx, cy = x0 + c * cell, y0 + r * cell
                if (c, r) == hi:
                    lab = "(%d,%d)" % (c, r)
                    fs = 14 if n == 1 else (13 if n == 2 else 11)
                    parts.append(fitbox(cx, cy, cell, cell, lab,
                                        size=fs, pad=6, fill=HL, sw=2, rx=3))
                else:
                    parts.append(rect(cx, cy, cell, cell, fill=BG, sw=1.2, rx=3))
        parts.append(text(x0 + side / 2, y0 + side + 30, bottom, size=13, color=MUTED))

    # стрілки «до предка» між сітками
    for xr, xl in ((740, 635), (405, 300)):
        mid = (xl + xr) / 2.0
        parts.append(text(mid, 196, "x ≫ 1,  y ≫ 1", size=13))
        parts.append(arrow(xr - 16, 224, xl + 16, 224))

    parts.append(text(W / 2, 452,
                      "рівень z містить 4ᶻ тайлів · уся піраміда 0…z коштує 4ᶻ · 4/3, тобто лише на третину більше за свій нижній рівень",
                      size=13, color=MUTED))
    render(os.path.join(IMG, 'pyramid.svg'), W, H, *parts,
           title="Вкладеність рівнів: предка знаходять зсувом індексів")


# ── 2. Конвеєр станцій ──────────────────────────────────────────────────────
def pipeline():
    W, H = 980, 660
    parts = []
    rows = [
        ("1.  Скласти потребу кадру",
         ["процесор, мікросекунди, у потоці інтерфейсу",
          "скасовувати нічого — потребу рахують наново щокадру"]),
        ("2.  Пошук у кеші розпакованих",
         ["оперативна пам'ять, наносекунди",
          "влучання — тайл одразу йде малюватися"]),
        ("3.  Байти: диск, потім мережа",
         ["канал і затримка, від одиниць до сотень мілісекунд",
          "у черзі — скасувати; у польоті — дати завершити"]),
        ("4.  Розпакування картинки",
         ["фонові потоки, ~2 мс на тайл, ×13 за обсягом",
          "застарілий результат усе одно кладемо в кеш"]),
        ("5.  Завантаження текстури",
         ["шина до GPU й час кадру, ~0.1 мс на тайл",
          "квота на кадр: кілька штук, решта чекає"]),
    ]
    x0, bw, bh, step, top = 56, 320, 64, 116, 74
    ax = 60 + 320 + 60
    for i, (name, notes) in enumerate(rows):
        y = top + i * step
        parts.append(fitbox(x0, y, bw, bh, name, size=15, pad=10, fill=FILL, sw=2, bold=True))
        parts.append(line(x0 + bw + 8, y + bh / 2, ax - 8, y + bh / 2,
                          color=MUTED, sw=1.0, dash="4,4"))
        parts.append(fitbox(ax, y, 480, bh, notes, size=13, pad=10, fill=BG, sw=1.2))
        if i < len(rows) - 1:
            parts.append(arrow(x0 + bw / 2, y + bh + 4, x0 + bw / 2, y + step - 4))

    parts.append(text(W / 2, 630,
                      "між станціями — черги з обмеженою довжиною; кожна станція має власну межу паралельности",
                      size=13, color=MUTED))
    render(os.path.join(IMG, 'pipeline.svg'), W, H, *parts,
           title="Станції конвеєра: у кожної свій дефіцитний ресурс")


# ── 3. Поверхи зберігання ───────────────────────────────────────────────────
def cache_levels():
    W, H = 960, 480
    parts = []
    rows = [
        ("GPU-текстура",            "256 КіБ на тайл · сотні МіБ · доступ миттєвий",   HL),
        ("растр в оперативній",     "256 КіБ на тайл · сотні МіБ · віддати ~0.1 мс",   HL),
        ("стиснуті байти на диску", "~20 КіБ на тайл · гігабайти · розпакувати ~2 мс", HL2),
        ("джерело в мережі",        "чуже й нескінченне · 100…1000 мс на тайл",        SOFT),
    ]
    y0, bh, step = 86, 64, 88
    for i, (name, nums, col) in enumerate(rows):
        y = y0 + i * step
        parts.append(fitbox(60, y, 250, bh, name, size=14, pad=10, fill=col, sw=1.8, bold=True))
        parts.append(fitbox(322, y, 318, bh, nums, size=12, pad=8, fill=BG, sw=1.2))

    yb = y0 + 2 * step - (step - bh) / 2.0
    parts.append(line(52, yb, 648, yb, color=POS, sw=1.8, dash="7,5"))
    parts.append(fitbox(668, yb - 26, 240, 52, ["межа розпакування:", "×13 за обсягом"],
                        size=13, pad=8, fill=BG, stroke=POS, sw=1.8))

    parts.append(text(W / 2, 448,
                      "що ближче до екрана — то дорожчий байт і то менше їх поміщається",
                      size=13, color=MUTED))
    render(os.path.join(IMG, 'cache-levels.svg'), W, H, *parts,
           title="Один тайл у чотирьох іпостасях")


# ── 4. Заповнення дір ───────────────────────────────────────────────────────
def substitution():
    W, H = 980, 520
    parts = []
    cell = 100

    def grid(x0, y0, hole_fill):
        out = []
        for r in range(3):
            for c in range(3):
                x, y = x0 + c * cell, y0 + r * cell
                if (c, r) == (1, 1):
                    continue
                out.append(rect(x, y, cell, cell, fill=BG, sw=1.2, rx=3))
        out.extend(hole_fill(x0 + cell, y0 + cell))
        return out

    def by_parent(x, y):
        return [fitbox(x, y, cell, cell, ["чверть", "предка", "×2"],
                       size=12, pad=6, fill=HL, sw=2, rx=3)]

    def by_children(x, y):
        out = [rect(x, y, cell, cell, fill=BG, sw=2, rx=3)]
        h = cell / 2.0
        for r in range(2):
            for c in range(2):
                out.append(rect(x + c * h + 3, y + r * h + 3, h - 6, h - 6,
                                fill=HL2, sw=1.2, rx=2))
        return out

    parts.append(text(210, 82, "діру закриває предок", size=15, bold=True))
    parts.extend(grid(60, 100, by_parent))
    parts.append(mtext(210, 432, ["чверть грубішого тайла, розтягнута вдвічі:",
                                  "розмито, але з правильними кольорами"],
                       size=12, color=MUTED))

    parts.append(text(710, 82, "діру закривають діти", size=15, bold=True))
    parts.extend(grid(560, 100, by_children))
    parts.append(mtext(710, 432, ["чотири вже наявні дитини, стиснуті вдвічі:",
                                  "навіть різкіше за належне"],
                       size=12, color=MUTED))

    parts.append(text(W / 2, 494,
                      "ланцюг предків доходить до рівня 0, де тайл один на весь світ — тому незакритої діри не буває ніколи",
                      size=13, color=MUTED))
    render(os.path.join(IMG, 'substitution.svg'), W, H, *parts,
           title="Картинка ціла завжди — змінюється лише різкість")


# ── 5. Скільки клітинок накриває вікно (вставка math-tile-pyramid) ──────────
def window_tiles():
    import math
    W, H = 1020, 420
    parts = []
    n_cells = 16
    cw = 50.0
    ch = 52.0
    x0 = 40.0
    wlen = 12.5 * cw

    def strip(y, u, count, note, cap):
        out = []
        start = x0 + u * cw
        first = int(math.floor(u))
        last = int(math.ceil(u + 12.5)) - 1
        out.append(text(x0, y - 20, cap, size=14, bold=True, anchor="start"))
        for c in range(n_cells):
            fill = HL if first <= c <= last else BG
            out.append(rect(x0 + c * cw, y, cw, ch, fill=fill, sw=1.1, rx=2))
        out.append(rect(start, y - 8, wlen, ch + 16,
                        fill="none", stroke=POS, sw=3, rx=4))
        out.append(text(x0 + n_cells * cw + 16, y + ch / 2 + 5, count,
                        size=15, bold=True, color=POS, anchor="start"))
        out.append(text(start + wlen / 2, y + ch + 40, note, size=13, color=MUTED))
        return out

    parts.extend(strip(90, 0.0, "13 клітинок",
                       "вікно збіглося з межами: 13 = ⌈12.5⌉",
                       "зсув u = 0"))
    parts.extend(strip(250, 0.75, "14 клітинок",
                       "вікно звисає з обох боків: 14 = ⌊12.5⌋ + 2",
                       "зсув u = 0.75 клітинки"))
    parts.append(mtext(W / 2, 385,
                       ["мінімум ⌈W/T⌉ = 13   ·   максимум ⌊W/T⌋ + 2 = 14   ·   "
                        "середнє по всіх зсувах W/T + 1 = 13.5"],
                       size=14))
    render(os.path.join(IMG, 'window-tiles.svg'), W, H, *parts,
           title="Скільки клітинок сітки накриває вікно завдовжки 12.5 клітинки")


# ── 6. Вибір цілого рівня (вставка math-tile-pyramid) ───────────────────────
def level_choice():
    W, H = 1020, 400
    parts = []
    ax_y = 250

    def X(z):
        return 90 + (z - 14) * 168.0

    vals = {14: "6.08", 15: "3.04", 16: "1.52", 17: "0.76", 18: "0.38", 19: "0.19"}
    parts.append(line(50, ax_y, 985, ax_y, sw=2))
    for z in range(14, 20):
        x = X(z)
        parts.append(line(x, ax_y - 8, x, ax_y + 8, sw=2))
        parts.append(text(x, ax_y + 32, "z = %d" % z, size=14, bold=True))
        parts.append(text(x, ax_y + 54, vals[z], size=13, color=MUTED))

    xt = X(16.2831)
    parts.append(line(xt, 112, xt, ax_y - 12, color=POS, sw=2, dash="6 5"))
    parts.append(circle(xt, ax_y, 6.5, fill=HL, stroke=POS, sw=2.5))
    parts.append(text(xt, 100, "потрібно 1.25 м/px   →   z* = 16.28",
                      size=15, bold=True, color=POS))

    parts.append(fitbox(110, 120, 270, 76,
                        ["округлення ВНИЗ:  z = 16",
                         "1.52 м/px — розтяг ×1.22",
                         "тайлів 0.68 від ідеалу"],
                        size=13, fill=HL2, rx=5))
    parts.append(fitbox(625, 120, 270, 76,
                        ["округлення ВГОРУ:  z = 17",
                         "0.76 м/px — запас різкости ×1.65",
                         "тайлів 2.70 від ідеалу"],
                        size=13, fill=SOFT, rx=5))
    parts.append(arrow(250, 200, 420, 240))
    parts.append(arrow(760, 200, 600, 240))

    parts.append(mtext(W / 2, 336,
                       ["під кожним рівнем — S(z, 50.45°) у метрах на піксель для тайла 256 px",
                        "сусідні цілі рівні різняться рівно вчетверо за кількістю тайлів: "
                        "2.70 / 0.68 = 4",
                        "z* = log₂( 40 075 016.686 · cos φ / (T · S) )"],
                       size=13, color=MUTED))
    render(os.path.join(IMG, 'level-choice.svg'), W, H, *parts,
           title="Дробовий рівень і два його цілих сусіди")


# ── Ядро: хто чим володіє (вставка proj-tile-cache) ─────────────────────────
def tile_core():
    W, H = 1140, 650
    parts = []

    lanes = [
        (40, 300, "потік малювання", FILL, [
            ["скласти потребу кадру,", "підняти покоління g"],
            ["пошук у кеші:", "влучання — малюємо,", "промах — замовляємо"],
            ["request(id, vp):", "відсіяти те, що вже", "в польоті або в купі"],
            ["кінець кадру: злити ready,", "вставити в кеш, trim,", "квота завантажень текстур"],
        ]),
        (420, 300, "спільне під коротким замком", HL2, [
            ["pending — адреси,", "що чекають у купі"],
            ["купа запитів, ключ", "(−g, |Δz|, d²);", "живе одне покоління"],
            ["inFlight — адреса → політ:", "прапорець аборту,", "лічильник байтів"],
            ["ready — розпаковані растри;", "замок лише на обмін", "двома векторами"],
        ]),
        (800, 300, "фонові потоки", SOFT, [
            ["take(): зняти найкращий,", "зайняти з'єднання"],
            ["байти: спершу диск,", "потім мережа"],
            ["розпакувати в растр"],
            ["publish() у ready;", "FlightGuard стирає запис", "у будь-якому разі"],
        ]),
    ]

    for x0, w, head, col, boxes in lanes:
        parts.append(rect(x0, 84, w, 480, fill=BG, sw=1.6, rx=10))
        parts.append(text(x0 + w / 2, 70, head, size=15, bold=True))
        for i, b in enumerate(boxes):
            parts.append(fitbox(x0 + 14, 104 + i * 112, w - 28, 96, b,
                                size=13, pad=10, fill=col, sw=1.4))

    for gx, l, r, yr, yl, lab_r, lab_l in (
            (380, 340, 420, 196, 468, "потреба", "готове"),
            (760, 720, 800, 196, 468, "робота",  "растр"),
    ):
        parts.append(text(gx, yr - 12, lab_r, size=12, color=MUTED))
        parts.append(arrow(l + 4, yr, r - 4, yr))
        parts.append(text(gx, yl - 12, lab_l, size=12, color=MUTED))
        parts.append(arrow(r - 4, yl, l + 4, yl))

    parts.append(mtext(W / 2, 596,
                       ["кеш розпакованих тайлів належить ЛИШЕ потокові малювання — фонові його не бачать;",
                        "спільні тільки чотири структури посередині, і жоден замок не тримають довше "
                        "за перестановку покажчиків"],
                       size=13, color=MUTED))
    render(os.path.join(IMG, 'tile-core.svg'), W, H, *parts,
           title="Ядро кешу й планувальника: хто чим володіє")


# ── Поле цінности для витіснення (вставка proj-tile-cache) ──────────────────
def _blend(hex_to, t):
    """Змішати білий із кольором hex_to у пропорції t (0…1)."""
    r2, g2, b2 = (int(hex_to[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(255 + (r2 - 255) * t),
                              int(255 + (g2 - 255) * t),
                              int(255 + (b2 - 255) * t))


def evict_value():
    W, H = 1060, 600
    parts = []
    cols, rows, cell = 6, 4, 92
    x0, y0 = 60, 112
    ccx, ccy = 3.0, 2.0        # центр екрана в клітинках
    halfW, halfH = 1.5, 1.0    # піврозміри екрана в клітинках

    vals = {}
    for r in range(rows):
        for c in range(cols):
            dx = ((c + 0.5) - ccx) / halfW
            dy = ((r + 0.5) - ccy) / halfH
            vals[(c, r)] = -(dx * dx + dy * dy)
    lo, hi = min(vals.values()), max(vals.values())

    for r in range(rows):
        for c in range(cols):
            v = vals[(c, r)]
            t = (v - lo) / (hi - lo)
            x, y = x0 + c * cell, y0 + r * cell
            worst = abs(v - lo) < 1e-9
            parts.append(rect(x, y, cell, cell,
                              fill=_blend(POS, 0.10 + 0.42 * t),
                              stroke=POS if worst else LINE,
                              sw=2.8 if worst else 1.2, rx=3))
            parts.append(text(x + cell / 2, y + cell / 2 + 5,
                              "%.1f" % v, size=15, bold=worst))

    parts.append(rect(x0 + (ccx - halfW) * cell, y0 + (ccy - halfH) * cell,
                      2 * halfW * cell, 2 * halfH * cell,
                      fill="none", stroke=NEG, sw=3, rx=4))

    parts.append(text(x0 + cols * cell / 2, 92,
                      "тайли поточного рівня; синій прямокутник — екран",
                      size=13, color=MUTED))

    px = 664
    notes = [
        ["цінність =", "−2 · |z − z_екрана| − d²", "d = 1 на краю екрана"],
        ["предок (z−1):", "−2 − d² + 2 ≈ −0.5", "тримаємо майже завжди"],
        ["чужий variant —", "стиль, щільність, мова:", "−10³⁰⁰, летить перед усім"],
        ["товста рамка —", "найнижча цінність:", "ці чотири й витіснять"],
    ]
    for i, n in enumerate(notes):
        parts.append(fitbox(px, y0 + i * 96, 336, 80, n, size=13, pad=10,
                            fill=FILL if i < 3 else HL, sw=1.4))

    parts.append(mtext(W / 2, 552,
                       ["порядок витіснення — не давність, а поле цінности навколо екрана;",
                        "воно змінюється щокадру, тому його не зберігають, "
                        "а рахують одним проходом у мить перебору"],
                       size=13, color=MUTED))
    render(os.path.join(IMG, 'evict-value.svg'), W, H, *parts,
           title="Що витісняти: поле цінности, а не черга давности")


# ── Стрічка часу (вставка hist-slippy-map) ─────────────────────────────────
def hist_timeline():
    W, H = 1100, 780
    parts = []
    rows = [
        ("червень 1993", "Xerox PARC Map Viewer",
         ["сервер малює унікальну картинку", "на кожен запит"]),
        ("лютий 1996", "MapQuest",
         ["карта як комерційна послуга;", "крок по карті = нова сторінка"]),
        ("березень 1999", "XMLHTTP в Internet Explorer 5.0",
         ["сторінка вміє питати сервер", "без перезавантаження"]),
        ("1999–2004", "Keyhole EarthViewer",
         ["піраміда даних їде мережею,", "але у власному 3D-клієнті"]),
        ("2003", "Where 2 Technologies · Expedition",
         ["тайл-сервер і настільний клієнт", "на C++, Сідней"]),
        ("вересень–жовтень 2004", ["Google купує ZipDash,", "Where 2 і Keyhole"],
         ["три шматки майбутньої карти", "сходяться в одній компанії"]),
        ("8 лютого 2005", "Google Maps",
         ["тайли плюс фонові запити", "у звичайному браузері"]),
        ("18 лютого 2005", "есей Джессі Джеймса Ґарретта",
         ["прийом дістає назву «Ajax» —", "через десять днів після запуску"]),
        ("з 2004", "OpenStreetMap",
         ["угоду z/x/y записано як", "Slippy map tilenames"]),
        ("з 2010", "iPhone 4 і подвійна щільність",
         ["з'являються @2x-тайли", "та сітка з плиткою 512"]),
    ]
    x_d, w_d = 46, 180
    x_e, w_e = 242, 340
    x_c, w_c = 598, 462
    y0, bh, step = 76, 54, 66

    parts.append(text(x_d + w_d / 2, 62, "коли", size=12, color=MUTED))
    parts.append(text(x_e + w_e / 2, 62, "що сталося", size=12, color=MUTED))
    parts.append(text(x_c + w_c / 2, 62, "що саме змінилося", size=12, color=MUTED))

    ylast = y0 + (len(rows) - 1) * step + bh / 2
    parts.append(line(26, y0 + bh / 2, 26, ylast, color=MUTED, sw=1.6))
    for i, (d, e, c) in enumerate(rows):
        y = y0 + i * step
        parts.append(circle(26, y + bh / 2, 5, fill=HL, stroke=POS, sw=2))
        parts.append(fitbox(x_d, y, w_d, bh, d, size=12, pad=8, fill=BG, sw=1.1))
        parts.append(fitbox(x_e, y, w_e, bh, e, size=13, pad=8,
                            fill=FILL, sw=1.8, bold=True))
        parts.append(fitbox(x_c, y, w_c, bh, c, size=12, pad=8, fill=BG, sw=1.1))

    parts.append(text(W / 2, 758,
                      "усі складники існували нарізно щонайменше з 1999 року; "
                      "у 2005-му їх уперше поєднали в одному продукті",
                      size=13, color=MUTED))
    render(os.path.join(IMG, 'hist-timeline.svg'), W, H, *parts,
           title="Від картинки на замовлення до слизької карти")


# ── Дві моделі взаємодії (вставка hist-slippy-map) ─────────────────────────
def hist_request_models():
    W, H = 1100, 560
    parts = []

    parts.append(text(255, 66, "картинка на замовлення (1993–2004)",
                      size=15, bold=True))
    steps = [
        "запит: центр, масштаб, розмір вікна",
        "сервер малює саме цю картинку",
        "одна GIF на все вікно, адреса неповторна",
    ]
    for i, s in enumerate(steps):
        y = 96 + i * 74
        parts.append(fitbox(70, y, 370, 48, s, size=13, pad=10, fill=FILL, sw=1.6))
        if i < len(steps) - 1:
            parts.append(arrow(255, y + 52, 255, y + 68))
    parts.append(mtext(255, 348,
                       ["крок на один піксель коштує стільки ж,",
                        "скільки стрибок через океан;",
                        "кеш не має за що вхопитися, бо другого",
                        "такого самого запиту вже не буде"],
                       size=12, color=MUTED))

    parts.append(text(845, 66, "слизька карта (з 2005)", size=15, bold=True))
    cw = 66
    gx, gy = 646, 96
    for r in range(4):
        for c in range(5):
            x, y = gx + c * cw, gy + r * cw
            if c == 0:
                parts.append(rect(x, y, cw, cw, fill=HL, stroke=POS, sw=1.8, rx=3))
            else:
                parts.append(rect(x, y, cw, cw, fill=SOFT, sw=1.1, rx=3))
    parts.append(arrow(gx + 5 * cw + 24, gy + 2 * cw, gx + 5 * cw + 74, gy + 2 * cw))
    parts.append(text(gx + 5 * cw + 49, gy + 2 * cw - 16, "рух", size=12, color=MUTED))
    parts.append(text(gx + 2.5 * cw, gy + 4 * cw + 28,
                      "зелені вже в кеші · червоні щойно з'явилися з краю",
                      size=12, color=MUTED))
    parts.append(mtext(845, 428,
                       ["адреса z/x/y стала й повторювана, тому те саме",
                        "сховище обслуговує різних людей і різні сеанси:",
                        "працюють кеш браузера, проксі й CDN"],
                       size=12, color=MUTED))

    parts.append(line(548, 56, 548, 480, color=MUTED, sw=1.0, dash="5,5"))
    parts.append(text(W / 2, 534,
                      "змінилася не швидкість каналу, а те, чи можна перевикористати вже завантажене",
                      size=13, color=MUTED))
    render(os.path.join(IMG, 'hist-request-models.svg'), W, H, *parts,
           title="Що саме зламав 2005 рік")


# ── Ціна розміру плитки у 2005-му (вставка hist-slippy-map) ────────────────
def hist_tile_size_cost():
    W, H = 1000, 570
    parts = []
    base = 436.0
    k = 300.0 / 21.0          # пікселів на секунду
    data = [
        (64,   252, 18.90, 1.93),
        (128,   80,  6.00, 2.45),
        (256,   30,  2.25, 3.68),
        (512,   12,  0.90, 5.89),
        (1024,   6,  0.45, 11.78),
    ]
    bw = 100
    for i, (T, n, lat, byt) in enumerate(data):
        x = 110 + i * 175
        hb, hl = byt * k, lat * k
        parts.append(rect(x, base - hb, bw, hb, fill=HL2, stroke=NEG, sw=1.6, rx=3))
        parts.append(rect(x, base - hb - hl, bw, hl, fill=HL, stroke=POS, sw=1.6, rx=3))
        parts.append(text(x + bw / 2, base - hb - hl - 12, "%.1f с" % (lat + byt),
                          size=14, bold=True, color=POS if T == 256 else INK))
        parts.append(text(x + bw / 2, base + 26, "T = %d" % T, size=14, bold=True))
        parts.append(text(x + bw / 2, base + 48, "%d тайлів" % n, size=12, color=MUTED))
    parts.append(line(84, base, 936, base, sw=1.8))

    parts.append(rect(556, 52, 15, 15, fill=HL, stroke=POS, sw=1.6, rx=2))
    parts.append(text(580, 65, "кола затримки: ⌈n/2⌉ · 150 мс", size=13,
                      anchor="start"))
    parts.append(rect(556, 78, 15, 15, fill=HL2, stroke=NEG, sw=1.6, rx=2))
    parts.append(text(580, 91, "передавання байтів каналом 1 Мбіт/с", size=13,
                      anchor="start"))

    parts.append(mtext(W / 2, 508,
                       ["вікно 1024 × 768 · двоє з'єднань на сервер · "
                        "затримка 150 мс · ~0.234 байта на піксель карти",
                        "дрібніша плитка — більше кіл затримки; більша — більше "
                        "зайвих пікселів; найнижча сума припадає на 256"],
                       size=13, color=MUTED))
    render(os.path.join(IMG, 'hist-tile-size-cost.svg'), W, H, *parts,
           title="Два протилежні коштування й долина між ними (числа 2005 року)")


if __name__ == '__main__':
    pyramid()
    pipeline()
    cache_levels()
    substitution()
    window_tiles()
    level_choice()
    tile_core()
    evict_value()
    hist_timeline()
    hist_request_models()
    hist_tile_size_cost()
    print("ok:", os.listdir(IMG))
