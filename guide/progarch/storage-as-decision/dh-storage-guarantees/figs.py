# -*- coding: utf-8 -*-
"""Фігури до кроку «Гарантії сховища DH»
(guide/progarch/storage-as-decision/dh-storage-guarantees).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_F = "#eafaf1"
AMBER_F = "#fdf3e7"; AMBER_S = "#e08a3c"
RED_F = "#fdecea"
BLUE_F = "#eaf0fd"
GRAY_F = "#f0f2f4"
TRACK = "#d3d8de"


def box_c(cx, cy, w, h, s, **kw):
    return fitbox(cx - w / 2.0, cy - h / 2.0, w, h, s, **kw)


def slider(lx, ly, tx0, tx1, label, frac, accent, show_q=False):
    """Один важіль-повзунок: підпис ліворуч, доріжка, кулька-ручка на позиції frac."""
    f = []
    f.append(text(lx, ly + 4, label, size=12.5, color=INK, anchor="start"))
    f.append(line(tx0, ly, tx1, ly, color=TRACK, sw=5))
    kx = tx0 + frac * (tx1 - tx0)
    f.append(circle(kx, ly, 8, fill=accent, stroke=BG, sw=2))
    if show_q:
        f.append(text(kx, ly - 15, "?", size=16, color=accent, bold=True))
    return f


# ───────── Фіг. 1: панель важелів і дві погані рефлекторні відповіді ─────────
def guarantee_dials():
    W, H = 1100, 620
    f = []
    labels = ["тривкість", "атомарність", "ізоляція", "цілісність"]

    # ── Панель A: усе на максимум ──
    ax, ay, aw, ah = 40, 60, 490, 258
    f.append(rect(ax, ay, aw, ah, fill="#fbfbfd", stroke="#c9ced4", sw=1.4))
    f.append(text(ax + aw / 2, ay + 30, "усе на максимум", size=14.5, bold=True, color=INK))
    rows = [128, 168, 208, 248]
    for lab, ry in zip(labels, rows):
        f += slider(ax + 22, ry, ax + 178, ax + 462, lab, 1.0, POS)
    f.append(text(ax + aw / 2, ay + ah - 14,
                  "ціна: fsync і замок на КОЖЕН запис — затримка, менша пропускна",
                  size=11.5, color=POS))

    # ── Панель B: дефолти наосліп ──
    bx, by, bw, bh = 570, 60, 490, 258
    f.append(rect(bx, by, bw, bh, fill="#fbfbfd", stroke="#c9ced4", sw=1.4))
    f.append(text(bx + bw / 2, by + 30, "дефолти наосліп", size=14.5, bold=True, color=INK))
    fracs = [0.35, 0.8, 0.2, 0.55]
    for lab, ry, fr in zip(labels, rows, fracs):
        f += slider(bx + 22, ry, bx + 178, bx + 462, lab, fr, MUTED, show_q=True)
    f.append(text(bx + bw / 2, by + bh - 14,
                  "тихо ризикуєш там, де дефолт слабкий («ОК» ≠ «на диску»)",
                  size=11.5, color=MUTED))

    # ── стрілки вниз до правильної панелі ──
    f.append(arrow(ax + aw / 2, ay + ah + 4, 520, 350, color=FIELD, sw=2))
    f.append(arrow(bx + bw / 2, by + bh + 4, 580, 350, color=FIELD, sw=2))

    # ── Панель C: свій набір під кожен клас ──
    cx0, cy0, cw, chh = 40, 356, 1020, 214
    f.append(rect(cx0, cy0, cw, chh, fill=GREEN_F, stroke=FIELD, sw=2))
    f.append(text(cx0 + cw / 2, cy0 + 30, "правильно: свій набір важелів під кожен клас даних",
                  size=14.5, bold=True, color=INK))
    crows = [424, 464, 504, 544]
    cfracs = [0.9, 1.0, 0.45, 1.0]
    for lab, ry, fr in zip(labels, crows, cfracs):
        f += slider(cx0 + 26, ry, cx0 + 210, cx0 + 830, lab, fr, FIELD)
    f.append(text(cx0 + cw - 24, cy0 + chh - 16,
                  "різні класи → різні позиції\n(див. таблицю нижче)",
                  size=11.5, color=MUTED, anchor="end"))

    render(os.path.join(IMG, "guarantee-dials.svg"), W, H, *f,
           title="Гарантія — не прапорець, а панель важелів, і кожен має ціну")


# ───────── Фіг. 2: матриця «клас даних DH → яка гарантія» ─────────
def guarantee_matrix():
    W, H = 1200, 512
    f = []
    # колонки
    cols = [
        ("Клас даних DH", 30, 224),
        ("Тривкість", 264, 158),
        ("Атомарність", 432, 158),
        ("Ізоляція", 600, 150),
        ("Цілісність", 760, 158),
        ("Ціна помилки", 928, 242),
    ]
    hy, hh = 46, 42
    for name, x, w in cols:
        f.append(fitbox(x, hy, w, hh, name, size=13, bold=True,
                        fill="#eef1f6", stroke=MUTED, color=INK))

    rows = [
        ("Реєстр і власність\n(пристрої, власник, поріг)",
         "максимум\n(fsync, FULL)", "увесь агрегат\n— одна транзакція",
         "сувора\nна запис", "UNIQUE · FK\n(тотожність)",
         "КАТАСТРОФА\nдім забув, чий він", FIELD, GREEN_F),
        ("Інваріант під\nконкурентністю (бюджет)",
         "як у реєстру", "один оператор\nUPDATE…WHERE",
         "замок рядка\nсеріалізує", "вартовий · CHECK\n(база — суддя)",
         "ПОРУШЕНЕ ПРАВИЛО\nперевитрата, дубль", POS, RED_F),
        ("Телеметрія\n(потік показів давача)",
         "послаблена\n(NORMAL, батч)", "рядок сам\nсобі атом",
         "низька —\nне сперечаються", "майже нема",
         "дрібна\nсвіт дошле ще", NEG, BLUE_F),
        ("Похідне\n(середні, «востаннє…»)",
         "жодної", "—", "—", "—",
         "нуль\nперерахуємо", MUTED, GRAY_F),
    ]
    ry, rh, gap = 94, 84, 6
    for i, r in enumerate(rows):
        cls, dur, ato, iso, integ, price, accent, tint = r
        y = ry + i * (rh + gap)
        vals = [cls, dur, ato, iso, integ, price]
        for (name, x, w), v in zip(cols, vals):
            is_first = (x == 30)
            is_last = (name == "Ціна помилки")
            f.append(fitbox(x, y, w, rh, v, size=12,
                            bold=(is_first or is_last),
                            fill=(tint if (is_first or is_last) else FILL),
                            stroke=(accent if (is_first or is_last) else "#d7dbe0"),
                            color=INK, sw=(1.8 if (is_first or is_last) else 1)))

    ny = ry + 4 * (rh + gap) + 4
    f.append(fitbox(30, ny, 1140, 46,
                    "Один SQLite несе всі чотири — з РІЗНИМИ важелями. Гарантію купуємо на ФАКТ за ціною помилки, а не одну на всю базу.",
                    size=13.5, bold=True, fill="#fbfbe8", stroke="#c9b458", color=INK, sw=1.8))

    render(os.path.join(IMG, "guarantee-matrix.svg"), W, H, *f,
           title="Один дім — чотири різні зобовʼязання перед сховищем")


# ───────── Фіг. 3: той самий диск, різні важелі (реєстр vs телеметрія) ─────────
def two_writes():
    W, H = 1000, 590
    f = []
    LX, RX = 268, 712
    bw = 320

    # заголовки колонок
    f.append(box_c(LX, 70, bw, 52, "запис РЕЄСТРУ\nрідко · ціна помилки — катастрофа",
                   size=13, bold=True, fill=GREEN_F, stroke=FIELD, sw=1.8))
    f.append(box_c(RX, 70, bw, 52, "потік ТЕЛЕМЕТРІЇ\nлавина · кожен рядок дешевий",
                   size=13, bold=True, fill=BLUE_F, stroke=NEG, sw=1.8))

    # ліва колонка — реєстр (усе по максимуму)
    left = [
        (168, "BEGIN … COMMIT\nувесь агрегат атомарно", FILL, "#d7dbe0"),
        (266, "synchronous = FULL\nfsync на КОЖЕН коміт", AMBER_F, AMBER_S),
        (364, "на диску — переживе\nнавіть відмову живлення", GREEN_F, FIELD),
    ]
    for cy, s, fill, stroke in left:
        f.append(box_c(LX, cy, bw, 62, s, size=12.5, bold=True, fill=fill, stroke=stroke, sw=1.7))
    f.append(arrow(LX, 98, LX, 135, color=INK))
    f.append(arrow(LX, 199, LX, 233, color=INK))
    f.append(arrow(LX, 297, LX, 331, color=INK))
    f.append(box_c(LX, 452, bw, 44, "повільніше на запис —\nале записів обмаль", size=12,
                   fill="#f7f9fb", stroke="#d7dbe0", color=MUTED))
    f.append(arrow(LX, 397, LX, 428, color=FIELD))

    # права колонка — телеметрія (свідомо послаблено)
    right = [
        (168, "коміти ГРУПУЮТЬСЯ\nбагато рядків за раз", FILL, "#d7dbe0"),
        (266, "synchronous = NORMAL\nfsync не на кожен коміт", AMBER_F, AMBER_S),
        (364, "на диску — на відмові живлення\nгубимо лише ХВІСТ", BLUE_F, NEG),
    ]
    for cy, s, fill, stroke in right:
        f.append(box_c(RX, cy, bw, 62, s, size=12.5, bold=True, fill=fill, stroke=stroke, sw=1.7))
    f.append(arrow(RX, 98, RX, 135, color=INK))
    f.append(arrow(RX, 199, RX, 233, color=INK))
    f.append(arrow(RX, 297, RX, 331, color=INK))
    f.append(box_c(RX, 452, bw, 44, "швидко — і це\nсвідома угода, не недбалість", size=12,
                   fill="#f7f9fb", stroke="#d7dbe0", color=MUTED))
    f.append(arrow(RX, 397, RX, 428, color=NEG))

    # нижній банер
    f.append(fitbox(80, 520, 840, 48,
                    "Той самий SQLite, той самий диск — різні важелі під різну ціну помилки.",
                    size=14, bold=True, fill="#fbfbe8", stroke="#c9b458", color=INK, sw=1.8))

    render(os.path.join(IMG, "two-writes.svg"), W, H, *f,
           title="Два записи, два налаштування тривкості — під ціну помилки")


# ───────── Фіг. 4 (до вставки hist): дві історії дефолту тривкості ─────────
def durability_timeline():
    W, H = 1180, 600
    f = []
    x0, x1 = 300, 1140          # вісь часу: 2001 ← → 2022
    Y0, Y1 = 2001, 2022
    def X(yr):
        return x0 + (yr - Y0) * (x1 - x0) / float(Y1 - Y0)
    myL, moL = 210, 380         # дві доріжки

    # доріжки
    f.append(line(x0 - 40, myL, x1, myL, color=TRACK, sw=4))
    f.append(line(x0 - 40, moL, x1, moL, color=TRACK, sw=4))

    # ліві бирки доріжок
    b, _, _ = textbox(150, myL, "MySQL\nдвигун за\nзамовчуванням",
                      size=12.5, bold=True, fill="#eef1f6", stroke=MUTED, sw=1.6)
    f.append(b)
    b, _, _ = textbox(150, moL, "MongoDB\nwrite concern\nза замовчуванням",
                      size=12.5, bold=True, fill="#eef1f6", stroke=MUTED, sw=1.6)
    f.append(b)

    # напрям галузі (між доріжками)
    f.append(text((x0 + x1) / 2, 292,
                  "куди рухалася галузь: назад до «безпечно за замовчуванням»",
                  size=13, bold=True, color=FIELD))
    f.append(arrow(x0 - 10, 306, x1 - 10, 306, color=FIELD, sw=2.4))

    def mstone(cx, laneY, above, yr, s, accent, tint):
        dot = circle(X(yr), laneY, 9, fill=accent, stroke=BG, sw=2)
        cy = (laneY - 90) if above else (laneY + 90)
        body, w, h = textbox(X(yr), cy, s, size=12, fill=tint,
                             stroke=accent, sw=1.8, bold=False)
        if above:
            conn = line(X(yr), laneY - 8, X(yr), cy + h / 2, color=accent, sw=1.6)
        else:
            conn = line(X(yr), laneY + 8, X(yr), cy - h / 2, color=accent, sw=1.6)
        return dot + conn + body

    # MySQL — підписи зверху
    f.append(mstone(0, myL, True, 2001,
                    "2001\nInnoDB — лише ОПЦІЯ\n(дефолт — MyISAM,\nбез журналу)",
                    AMBER_S, AMBER_F))
    f.append(mstone(0, myL, True, 2010,
                    "2010 · MySQL 5.5\nInnoDB — ДЕФОЛТ\n(журнал, крах-безпека)",
                    FIELD, GREEN_F))

    # MongoDB — підписи знизу, зі зсувом по висоті проти накладань
    f.append(mstone(0, moL, False, 2009,
                    "≈2009 · Mongo 1.x\nдефолт w=0\n«вистрелив і забув»",
                    POS, RED_F))
    # 2012 опускаємо нижче, щоб не налізло на 2009
    dot = circle(X(2012), moL, 9, fill=AMBER_S, stroke=BG, sw=2)
    body, w, h = textbox(X(2012), moL + 158,
                         "лист. 2012\nдефолт w=1\n(підтверджено)",
                         size=12, fill=AMBER_F, stroke=AMBER_S, sw=1.8)
    conn = line(X(2012), moL + 8, X(2012), moL + 158 - h / 2, color=AMBER_S, sw=1.6)
    f.append(dot + conn + body)
    f.append(mstone(0, moL, False, 2021,
                    "2021 · Mongo 5.0\nдефолт w=majority\n(на реплік-сеті)",
                    FIELD, GREEN_F))

    # легенда кольорів (верх, праворуч від підзаголовка)
    lg = [("небезпечний дефолт", POS), ("півкроку", AMBER_S), ("безпечний дефолт", FIELD)]
    lx = 470
    for name, col in lg:
        f.append(circle(lx, 66, 7, fill=col, stroke=BG, sw=1.5))
        f.append(text(lx + 14, 70, name, size=12, color=INK, anchor="start"))
        lx += text_width(name, 12) + 60

    render(os.path.join(IMG, "durability-timeline.svg"), W, H, *f,
           title="Дві історії про те, як «підтверджено» довго не означало «збережено»")


# ───────── Фіг. 5 (вставка proj): карта трьох катувань ─────────
def torture_map():
    W, H = 1260, 566
    f = []
    cols = [
        ("Клас даних", 30, 214),
        ("Катування (як убиваємо)", 258, 292),
        ("Важіль", 564, 236),
        ("Що доводимо", 814, 416),
    ]
    hy, hh = 46, 44
    for name, x, w in cols:
        f.append(fitbox(x, hy, w, hh, name, size=13.5, bold=True,
                        fill="#eef1f6", stroke=MUTED, color=INK))

    rows = [
        ("Реєстр  ·  FULL\nдім · пристрої · поріг",
         "kill посеред транзакції,\nще ДО COMMIT",
         "BEGIN … COMMIT\n+ synchronous=FULL",
         "дім або цілком старий, або цілком новий —\nніколи піврозібраний;\nзакомічений переживе й відмову живлення",
         FIELD, GREEN_F),
        ("Телеметрія  ·  NORMAL\nпотік показів",
         "kill посеред\nлавини дописів",
         "батч-коміт\n+ synchronous=NORMAL",
         "закомічені рядки цілі,\nгубимо лише незакомічений хвіст;\nбаза не пошкоджена",
         NEG, BLUE_F),
        ("Бюджет нагріву\nінваріант під натовпом",
         "8 процесів разом\nбʼють один бюджет",
         "UPDATE … WHERE\n+ busy_timeout",
         "heat_left НІКОЛИ < 0,\nсума списань точна\n(вартовий серіалізує писарів)",
         POS, RED_F),
    ]
    ry, rh, gap = 100, 118, 8
    for i, r in enumerate(rows):
        cls, tort, lev, proof, accent, tint = r
        y = ry + i * (rh + gap)
        vals = [cls, tort, lev, proof]
        for (name, x, w), v in zip(cols, vals):
            first = (x == 30)
            f.append(fitbox(x, y, w, rh, v, size=12.5,
                            bold=first,
                            fill=(tint if first else FILL),
                            stroke=(accent if first else "#d7dbe0"),
                            color=INK, sw=(1.9 if first else 1)))
    ny = ry + 3 * (rh + gap) + 2
    f.append(fitbox(30, ny, 1200, 46,
                    "Кожну гарантію доводить ВЛАСНЕ катування — не цитата з документації.",
                    size=14, bold=True, fill="#fbfbe8", stroke="#c9b458", color=INK, sw=1.9))
    render(os.path.join(IMG, "torture-map.svg"), W, H, *f,
           title="Три класи даних — три різні важелі — три різні катування")


# ───────── Фіг. 6 (вставка proj): kill процесу — не відмова живлення ─────────
def kill_vs_powerloss():
    W, H = 1240, 604
    f = []
    APPX, CACHEX, DISKX = 215, 615, 1015
    cw = 226
    f.append(text(APPX, 108, "буфер застосунку", size=13, bold=True, color=INK))
    f.append(text(CACHEX, 108, "кеш ОС", size=13, bold=True, color=INK))
    f.append(text(DISKX, 108, "диск (носій)", size=13, bold=True, color=INK))

    def lane(cy, tag, tag_col, cache_txt, cache_tint, cache_stroke,
             disk_txt, disk_tint, disk_stroke, dashed):
        g = []
        g.append(text(28, cy + 5, tag, size=14, bold=True, color=tag_col, anchor="start"))
        g.append(box_c(APPX, cy, cw, 74, "коміт вийшов\nз памʼяті процеса",
                       size=12, fill=FILL, stroke="#d7dbe0"))
        g.append(box_c(CACHEX, cy, cw, 74, cache_txt, size=12,
                       fill=cache_tint, stroke=cache_stroke, sw=1.7))
        g.append(box_c(DISKX, cy, cw, 74, disk_txt, size=12,
                       fill=disk_tint, stroke=disk_stroke, sw=1.7))
        g.append(arrow(APPX + cw / 2, cy, CACHEX - cw / 2, cy, color=INK))
        if dashed:
            g.append(line(CACHEX + cw / 2, cy, DISKX - cw / 2, cy, color=MUTED, sw=2, dash="7 6"))
        else:
            g.append(arrow(CACHEX + cw / 2, cy, DISKX - cw / 2, cy, color=FIELD, sw=2.4))
        return g

    f += lane(200, "FULL", FIELD,
              "проходить кеш\nі йде далі", "#eef7f0", FIELD,
              "НА ДИСКУ\nfsync на КОЖЕН коміт", GREEN_F, FIELD, dashed=False)
    f += lane(392, "NORMAL", NEG,
              "СПИНИВСЯ тут\nбез fsync на комітах", BLUE_F, NEG,
              "лише на контрольній\nточці (не на комітах)", "#f7f9fb", "#c9ced4", dashed=True)

    cut1 = (APPX + CACHEX) / 2      # межа процеса: kill
    cut2 = (CACHEX + DISKX) / 2     # межа летючості: відмова живлення
    f.append(line(cut1, 128, cut1, 470, color=INK, sw=2.4, dash="3 5"))
    f.append(line(cut2, 128, cut2, 470, color=POS, sw=2.6, dash="3 5"))
    f.append(text(cut1, 78, "kill процесу", size=13.5, bold=True, color=INK))
    f.append(text(cut2, 78, "відмова живлення", size=13.5, bold=True, color=POS))

    f.append(fitbox(cut1 - 205, 490, 410, 70,
                    "процес мертвий, а кеш ОС живий →\nзакомічене ЦІЛЕ в ОБОХ профілях\n(тому kill не бачить різниці FULL/NORMAL)",
                    size=12, fill="#f4f6f8", stroke=MUTED, color=INK))
    f.append(fitbox(cut2 - 150, 490, 360, 70,
                    "кеш ОС СТЕРТО →\nNORMAL губить свіжий хвіст,\nFULL уже на диску — цілий",
                    size=12, fill=RED_F, stroke=POS, color=INK, sw=1.7))
    render(os.path.join(IMG, "kill-vs-powerloss.svg"), W, H, *f,
           title="Kill процесу — це НЕ відмова живлення (дві різні межі летючості)")


if __name__ == "__main__":
    guarantee_dials()
    guarantee_matrix()
    two_writes()
    durability_timeline()
    torture_map()
    kill_vs_powerloss()
    print("OK: guarantee-dials.svg, guarantee-matrix.svg, two-writes.svg, "
          "durability-timeline.svg, torture-map.svg, kill-vs-powerloss.svg")
