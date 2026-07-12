# -*- coding: utf-8 -*-
"""Фігури до кроку «Вибір: рантайм конкурентності»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

ACTOR = "#7c4dbf"   # фіолетовий — актори (поза базовою палітрою, як окремий колір)


def fig_runtime_anatomy():
    """Три рантайми поруч: спільна пам'ять крізь замок / цикл подій / актори."""
    W, H = 1020, 470
    frags = []

    # розділювачі панелей
    for sx in (340, 680):
        frags.append(line(sx, 48, sx, 442, color=MUTED, sw=1, dash="4,5"))

    frags.append(text(170, 62, "Потоки + спільна пам'ять", size=15, bold=True))
    frags.append(text(510, 62, "Цикл подій", size=15, bold=True))
    frags.append(text(850, 62, "Актори", size=15, bold=True))

    # ── Панель 1: три потоки крізь замок-ворота до спільного стану ──
    for x in (95, 170, 245):
        b, _, _ = textbox(x, 118, "потік", size=12, fill="#eef2fb", min_w=66)
        frags.append(b)
    # замок як ворота, крізь які всі проходять
    b, _, _ = textbox(170, 214, "замок", size=12, fill="#fdecea", stroke=POS, min_w=96)
    frags.append(b)
    # спільний стан
    b, _, _ = textbox(170, 312, "спільний\nстан", size=13, fill="#eafaf0",
                      stroke=FIELD, min_w=120)
    frags.append(b)
    # потоки -> замок (сходяться)
    frags.append(arrow(95, 137, 150, 196, color=POS, sw=1.8))
    frags.append(arrow(170, 137, 170, 196, color=POS, sw=1.8))
    frags.append(arrow(245, 137, 190, 196, color=POS, sw=1.8))
    # замок -> стан
    frags.append(arrow(170, 233, 170, 288, color=LINE, sw=1.8))
    frags.append(text(170, 372, "усі ядра одразу,", size=12, color=MUTED))
    frags.append(text(170, 392, "та замок ставить у чергу", size=12, color=MUTED))

    # ── Панель 2: один потік-петля над чергою; сплячі сокети збоку ──
    frags.append(circle(468, 148, 34, fill="#eef2fb", stroke=NEG, sw=2))
    frags.append(text(468, 144, "1 потік", size=11, color=NEG, bold=True))
    frags.append(text(468, 161, "петля", size=11, color=NEG))
    b, _, _ = textbox(468, 250, "черга готових\nподій", size=12, min_w=156)
    frags.append(b)
    frags.append(arrow(468, 184, 468, 224, color=NEG, sw=1.8))
    # колонка сокетів праворуч: сплячі сірі, один готовий (зелений)
    sy0 = 104
    for i in range(5):
        ready = (i == 2)
        col = FIELD if ready else MUTED
        fillc = "#eafaf0" if ready else "#eef1f4"
        b, _, _ = textbox(602, sy0 + i * 33, "сокет", size=10, fill=fillc,
                          stroke=col, min_w=66)
        frags.append(b)
    frags.append(text(602, sy0 + 5 * 33 + 4, "сплять", size=11, color=MUTED))
    # готовий сокет штовхає подію в чергу
    frags.append(arrow(569, 176, 548, 244, color=FIELD, sw=1.8))
    frags.append(text(510, 372, "тисячі сплячих зʼєднань", size=12, color=MUTED))
    frags.append(text(510, 392, "дешево, але одне ядро", size=12, color=MUTED))

    # ── Панель 3: три ізольовані комірки з поштою, листи між ними ──
    for (x, y) in ((790, 128), (910, 128), (850, 250)):
        b, _, _ = textbox(x, y, "стан\n+ пошта", size=11, fill="#f3eefb",
                          stroke=ACTOR, min_w=98)
        frags.append(b)
    frags.append(arrow(840, 128, 860, 128, color=ACTOR, sw=1.8))   # між верхніми
    frags.append(arrow(800, 152, 832, 224, color=ACTOR, sw=1.8))   # верх-лів -> низ
    frags.append(arrow(900, 152, 868, 224, color=ACTOR, sw=1.8))   # верх-прав -> низ
    frags.append(text(850, 170, "лист", size=11, color=ACTOR))
    frags.append(text(850, 372, "ізоляція + нагляд,", size=12, color=MUTED))
    frags.append(text(850, 392, "та копія повідомлення", size=12, color=MUTED))

    render(os.path.join(IMG, "runtime-anatomy.svg"), W, H, *frags,
           title="Три рантайми: що вони роблять із часом")


def fig_sensitivity_map():
    """Трикутник I/O / CPU / стан; роботи DH падають у різні кути (без ребер —
    щоб жодна лінія не перетнула написи; трикутник задає саме розстановка кутів)."""
    W, H = 860, 620
    frags = []

    # кутові рамки — рантайм + домінантна риса роботи
    b, _, _ = textbox(430, 108, "Цикл подій\nчекання на I/O", size=13,
                      fill="#eef2fb", stroke=NEG, min_w=214)
    frags.append(b)
    b, _, _ = textbox(180, 512, "Потоки + пул\nрахунок на ядрах", size=13,
                      fill="#fdecea", stroke=POS, min_w=214)
    frags.append(b)
    b, _, _ = textbox(680, 512, "Актори\nбагато окремих станів + збій", size=13,
                      fill="#f3eefb", stroke=ACTOR, min_w=214)
    frags.append(b)

    # центральна підказка
    frags.append(text(430, 318, "розклади за тим, де живе час",
                      size=13, color=MUTED, italic=True))

    # роботи DH — пілюлі у своїх рамках біля відповідного кута
    b, _, _ = textbox(430, 214, "хаб:\nсотні сплячих залізяк", size=12,
                      fill=BG, stroke=NEG, min_w=200)
    frags.append(b)
    b, _, _ = textbox(232, 400, "телеметрія:\nважка агрегація", size=12,
                      fill=BG, stroke=POS, min_w=176)
    frags.append(b)
    b, _, _ = textbox(628, 400, "твін + правила:\nстан на кожен дім", size=12,
                      fill=BG, stroke=ACTOR, min_w=186)
    frags.append(b)

    render(os.path.join(IMG, "sensitivity-map.svg"), W, H, *frags,
           title="Де живе час твоєї роботи")


def fig_napkin_walls():
    """Серветка: сонне зʼєднання — стек 8 МБ (віртуально, + стіни лічильника)
    проти дрібного heap-обʼєкта; чому потоки не доходять до 50k, а цикл — доходить."""
    W, H = 1060, 560
    frags = []

    x0, x1 = 130, 960          # вісь: 0 … 50 000 зʼєднань
    def X(n):
        return x0 + (n / 50000.0) * (x1 - x0)

    # ── вісь ──
    axis_y = 476
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=1.6))
    for n in (0, 10000, 20000, 30000, 40000, 50000):
        frags.append(line(X(n), axis_y, X(n), axis_y + 6, color=INK, sw=1.4))
        frags.append(text(X(n), axis_y + 24, "%dk" % (n // 1000), size=12, color=MUTED))
    frags.append(text((x0 + x1) / 2, axis_y + 48, "число сонних зʼєднань",
                      size=13, color=MUTED))

    # ── смуга «Потоки» ──
    ty, th = 150, 58
    frags.append(text(x0, ty - 20, "Потоки  (стек на кожне зʼєднання)",
                      size=15, bold=True, anchor="start"))
    # комфортна ділянка
    frags.append(rect(X(0), ty, X(12000) - X(0), th, fill="#eafaf0", stroke=FIELD, sw=1.6))
    frags.append(text((X(0) + X(12000)) / 2, ty + th / 2 + 5, "ще живі", size=12, color=FIELD))
    # зона стін
    frags.append(rect(X(12000), ty, X(30000) - X(12000), th, fill="#fdecea",
                      stroke=POS, sw=1.6))
    frags.append(text((X(12000) + X(30000)) / 2, ty + th / 2 + 5, "стіни", size=12,
                      color=POS, bold=True))
    # рвана межа й «не доходять»
    frags.append(line(X(30000), ty - 4, X(30000), ty + th + 4, color=POS, sw=2.4))
    frags.append(text((X(38000) + x1) / 2 - 10, ty + th / 2 + 5,
                      "потоки сюди не доходять", size=12.5, color=MUTED))

    # вертикальні «стіни» з підписами (рознесено по висоті, щоб не накладались)
    frags.append(line(X(12000), ty - 30, X(12000), ty + th + 10, color=POS, sw=1.4, dash="4,5"))
    b, _, _ = textbox(X(12000), 78, "systemd TasksMax\n≈ 12 288", size=11.5,
                      fill="#fff6f5", stroke=POS, min_w=160)
    frags.append(b)
    frags.append(line(X(30000), ty - 52, X(30000), ty - 30, color=POS, sw=1.4, dash="4,5"))
    b, _, _ = textbox(X(30000) + 6, 108, "vm.max_map_count / планувальник\nтасує десятки тисяч потоків",
                      size=11.5, fill="#fff6f5", stroke=POS, min_w=300)
    frags.append(b)
    # приписка над смугою
    frags.append(text(x0, ty + th + 26, "8 МБ стек × N — це ВІРТУАЛЬНА адреса, не RAM; "
                      "стоп не об памʼять, а об лічильник потоків",
                      size=12, color=MUTED, anchor="start"))

    # ── смуга «Цикл подій / горутини» ──
    ly, lh = 296, 40
    frags.append(text(x0, ly - 16, "Цикл подій / горутини  (дрібний обʼєкт на сокет)",
                      size=15, bold=True, anchor="start"))
    frags.append(rect(X(0), ly, X(50000) - X(0), lh, fill="#eafaf0", stroke=FIELD, sw=1.8))
    frags.append(text((X(0) + X(50000)) / 2, ly + lh / 2 + 5,
                      "кілька КБ на сокет · один потік + epoll · 50k влазить у коробку",
                      size=12.5, color=FIELD))
    frags.append(text(X(50000) + 6, ly + lh / 2 + 5, "✓", size=20, color=FIELD,
                      bold=True, anchor="start"))

    # ── серветкова арифметика (кутик) ──
    b, _, _ = textbox(x0 + 168, 402, "50 000 × 8 МБ  = 390 ГБ  (віртуально)\n"
                      "50 000 × ~8 КБ = ~400 МБ  (heap, resident)",
                      size=12.5, fill="#f7f9fc", stroke=MUTED, min_w=430)
    frags.append(b)

    render(os.path.join(IMG, "napkin-walls.svg"), W, H, *frags,
           title="Серветка: чому 50k сонних зʼєднань — стіна для потоків і прогулянка для циклу")


def fig_heartbeat_freeze():
    """Серцебиття циклу: важкий батч У ЦИКЛІ морозить край на весь свій час;
    той самий батч У ПУЛІ — край живе, рахунок біжить на всіх ядрах."""
    W, H = 1060, 470
    frags = []

    x0, x1 = 130, 980

    def ticks(y, xs, color=FIELD):
        out = []
        for x in xs:
            out.append(line(x, y - 13, x, y + 13, color=color, sw=3))
        return out

    # ── Сценарій A: батч у циклі ──
    ay = 132
    frags.append(text(x0, ay - 40, "Батч перерахунку правил — У ЦИКЛІ ПОДІЙ",
                      size=15, bold=True, anchor="start"))
    bx0, bx1 = x0 + 24 + 4 * 34, x0 + 24 + 4 * 34 + 470
    # лінію ведемо ПОВЗ бокс батчу (двома відрізками), а не суцільно під ним
    frags.append(line(x0, ay, bx0, ay, color=MUTED, sw=1.2, dash="3,4"))
    frags.append(line(bx1, ay, x1, ay, color=MUTED, sw=1.2, dash="3,4"))
    # серцебиття до батчу
    frags.extend(ticks(ay, [x0 + 24 + i * 34 for i in range(4)]))
    frags.append(rect(bx0, ay - 22, bx1 - bx0, 44, fill="#fdecea", stroke=POS, sw=1.8))
    frags.append(text((bx0 + bx1) / 2, ay + 6, "батч правил — 800 мс чистого CPU",
                      size=13, color=POS, bold=True))
    # серцебиття після
    frags.extend(ticks(ay, [bx1 + 22 + i * 34 for i in range(4)]))
    # підпис розриву
    frags.append(line(bx0, ay + 40, bx1, ay + 40, color=POS, sw=1.3))
    frags.append(line(bx0, ay + 34, bx0, ay + 46, color=POS, sw=1.3))
    frags.append(line(bx1, ay + 34, bx1, ay + 46, color=POS, sw=1.3))
    frags.append(text((bx0 + bx1) / 2, ay + 60, "серцебиття завмерло ≈ 800 мс — усі сокети ждуть",
                      size=12.5, color=POS))

    # ── Сценарій B: батч у пулі ──
    by = 320
    frags.append(text(x0, by - 46, "Той самий батч — У ПУЛІ РОБІТНИКІВ",
                      size=15, bold=True, anchor="start"))
    frags.append(line(x0, by, x1, by, color=MUTED, sw=1.2, dash="3,4"))
    # рівне серцебиття на всю ширину
    frags.extend(ticks(by, [x0 + 24 + i * 34 for i in range(int((x1 - x0 - 24) / 34))]))
    frags.append(text(x1, by - 22, "цикл вільний — край живий", size=12.5,
                      color=FIELD, anchor="end"))
    # чотири ядра паралельно
    wx0 = x0 + 24 + 4 * 34
    ww = 180
    for i in range(4):
        wy = by + 26 + i * 24
        frags.append(rect(wx0, wy, ww, 16, fill="#eafaf0", stroke=FIELD, sw=1.4))
        frags.append(text(wx0 - 8, wy + 12, "ядро %d" % (i + 1), size=11,
                          color=MUTED, anchor="end"))
    frags.append(text(wx0 + ww + 14, by + 62, "рахунок на всіх ядрах ≈ 200 мс",
                      size=12.5, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "heartbeat-freeze.svg"), W, H, *frags,
           title="Куди подіти важкий рахунок: у цикл (морозить) чи в пул (ні)")


def fig_runtime_lineage():
    """Три родоводи на одній осі часу: потоки (базова модель ОС, «завжди»),
    актори (1973 теорія → 1986 Erlang → 1998 AXD301),
    цикл подій (1999 C10K → 2004 nginx → 2009 Node.js).
    Показує перевернутий вік: async — наймолодший, актори — найстарші."""
    W, H = 1160, 560
    frags = []

    x0, x1 = 160.0, 1090.0          # 1965 .. 2010 на осі
    def X(year):
        return x0 + (year - 1965) * (x1 - x0) / 45.0

    # ── ліві підписи-заголовки доріжок ──
    b, _, _ = textbox(84, 118, "Потоки\n(модель ОС)", size=13, fill="#fdecea",
                      stroke=POS, min_w=124)
    frags.append(b)
    b, _, _ = textbox(84, 250, "Актори\n(теорія → Erlang)", size=13, fill="#f3eefb",
                      stroke=ACTOR, min_w=124)
    frags.append(b)
    b, _, _ = textbox(84, 400, "Цикл\nподій", size=13, fill="#eef2fb",
                      stroke=NEG, min_w=124)
    frags.append(b)

    # ── доріжка 1: потоки — суцільна смуга через увесь час ──
    b, _, _ = textbox(625, 118,
                      "рідна модель ОС — лежить під усіма іншими\n"
                      "процеси й багатозадачність — 1960-і · потоки в ядрі — Mach 1986, POSIX 1995",
                      size=12, fill="#fdecea", stroke=POS, min_w=930)
    frags.append(b)

    # ── доріжка 2: актори (y=250), три вузли + стрілки ──
    a1, _, _ = textbox(X(1973), 250, "1973\nконцепція\nHewitt · Bishop · Steiger",
                       size=12, fill="#f3eefb", stroke=ACTOR, min_w=150)
    a2, _, _ = textbox(X(1986), 250, "1986\nErlang\nArmstrong · Virding · Williams",
                       size=12, fill="#f3eefb", stroke=ACTOR, min_w=150)
    a3, _, _ = textbox(X(1998), 250, "1998\nAXD301: «9 дев'яток»\n(заявлено)",
                       size=12, fill="#f3eefb", stroke=ACTOR, min_w=150)
    frags.append(arrow(X(1973) + 92, 250, X(1986) - 110, 250, color=ACTOR, sw=1.8))
    frags.append(arrow(X(1986) + 110, 250, X(1998) - 90, 250, color=ACTOR, sw=1.8))
    frags += [a1, a2, a3]

    # ── доріжка 3: цикл подій (y≈400), три вузли зиґзаґом ──
    e1, _, _ = textbox(X(1999), 385, "1999 · C10K\nDan Kegel · cdrom.com",
                       size=12, fill="#eef2fb", stroke=NEG, min_w=150)
    e2, _, _ = textbox(X(2004), 440, "2004 · nginx\nІгор Сисоєв",
                       size=12, fill="#eef2fb", stroke=NEG, min_w=140)
    e3, _, _ = textbox(X(2009), 385, "2009 · Node.js\nRyan Dahl",
                       size=12, fill="#eef2fb", stroke=NEG, min_w=140)
    frags.append(arrow(X(1999) + 42, 402, X(2004) - 46, 422, color=NEG, sw=1.8))
    frags.append(arrow(X(2004) + 46, 422, X(2009) - 42, 402, color=NEG, sw=1.8))
    frags += [e1, e2, e3]

    # ── вісь десятиліть ──
    frags.append(line(x0, 500, x1, 500, color=MUTED, sw=1.4))
    for yr in (1970, 1980, 1990, 2000, 2010):
        frags.append(line(X(yr), 495, X(yr), 505, color=MUTED, sw=1.4))
        frags.append(text(X(yr), 522, str(yr), size=12, color=MUTED))
    frags.append(text(x1 + 30, 504, "час →", size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "runtime-lineage.svg"), W, H, *frags,
           title="Три родоводи рантаймів на одній осі часу")


if __name__ == "__main__":
    fig_runtime_anatomy()
    fig_sensitivity_map()
    fig_napkin_walls()
    fig_heartbeat_freeze()
    fig_runtime_lineage()
    print("OK: runtime-anatomy.svg, sensitivity-map.svg, napkin-walls.svg, heartbeat-freeze.svg, runtime-lineage.svg")
