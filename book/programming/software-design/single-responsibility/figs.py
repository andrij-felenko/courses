# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Одна причина проти трьох: зіткнення акторів у класі vs розведення ─────────
def fig_one_actor():
    W, H = 1000, 560
    frags = []

    # Заголовки двох панелей
    frags.append(text(250, 40, "Три актори — один клас: зіткнення",
                      size=15, bold=True, color=POS))
    frags.append(text(760, 40, "Три актори — три класи: ізольовано",
                      size=15, bold=True, color=FIELD))
    frags.append(line(W / 2, 60, W / 2, H - 30, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВА панель: один God-class ──
    actors_L = [
        ("CFO · фінанси", "правила нарахування", 90),
        ("COO · операції", "формат звіту", 230),
        ("CTO · база даних", "спосіб зберігання", 370),
    ]
    ax = 60          # x лівого краю рамок-акторів
    aw = 190         # ширина рамки актора
    cls_x = 340      # x класу-мішені
    cls_cy = 300
    # клас-мішень
    cbox, cw, ch = textbox(cls_x + 55, cls_cy, "Employee\ncalculatePay()\nreportHours()\nsave()",
                           size=12, bold=True, fill="#fdecea", stroke=POS, sw=2.2, pad=12)
    for nm, desc, ay in actors_L:
        frags.append(fitbox(ax, ay, aw, 56, nm + "\n" + desc, size=12, bold=True,
                            fill=FILL, stroke=MUTED, sw=1.4))
        # стрілка від актора до класу
        frags.append(arrow(ax + aw + 4, ay + 28, cls_x - 4, cls_cy - 6 + (ay - 230) * 0.18,
                          color=POS, sw=2.0))
    frags.append(cbox)
    # позначка зіткнення
    frags.append(text(cls_x + 55, cls_cy + ch / 2 + 26,
                      "спільний код — правка одного ламає інших",
                      size=11, bold=True, color=POS))

    # ── ПРАВА панель: три окремі класи ──
    rx = W / 2 + 40      # x лівого краю акторів
    raw = 175            # ширина рамки актора
    rcx = W / 2 + 300    # x класів-мішеней
    rows = [
        ("CFO · фінанси", "PayCalculator", 96),
        ("COO · операції", "HourReporter", 246),
        ("CTO · база даних", "EmployeeRepo", 396),
    ]
    for nm, cls, ay in rows:
        frags.append(fitbox(rx, ay, raw, 52, nm, size=12, bold=True,
                            fill=FILL, stroke=MUTED, sw=1.4))
        cb, cbw, cbh = textbox(rcx + 65, ay + 26, cls, size=12, bold=True,
                               fill="#f2faf5", stroke=FIELD, sw=2.0, pad=11, min_w=150)
        frags.append(cb)
        frags.append(arrow(rx + raw + 4, ay + 26, rcx + 65 - cbw / 2 - 4, ay + 26,
                          color=FIELD, sw=2.0))

    render(os.path.join(IMG, 'one-actor.svg'), W, H, *frags,
           title="SRP: одна причина для зміни = один актор на модуль")


# ── Хибний зріз (за дієсловом) проти правильного (за актором) ────────────────
def fig_axis_of_change():
    W, H = 980, 470
    frags = []

    # Спільний вихідний блок поведінки
    frags.append(text(W / 2, 34, "Одна цілісна поведінка — де різати?",
                      size=15, bold=True, color=INK))

    # ── ЛІВОРУЧ: хибний зріз за технічним дієсловом ──
    frags.append(text(240, 74, "ХИБНО: різати за дієсловом", size=14, bold=True, color=POS))
    frags.append(text(240, 96, "усі міняються від ОДНОГО актора → штучне дроблення",
                      size=11, color=MUTED))
    verbs = ["Validator", "Calculator", "Formatter", "Coordinator"]
    vx0, vy = 60, 130
    for i, v in enumerate(verbs):
        yy = vy + i * 62
        frags.append(fitbox(vx0, yy, 210, 46, v, size=13, bold=True,
                            fill="#fdecea", stroke=POS, sw=1.8))
    # усі під однією дужкою «один актор»
    frags.append(line(vx0 + 224, vy, vx0 + 224, vy + 3 * 62 + 46, color=POS, sw=2.0))
    frags.append(fitbox(vx0 + 234, vy + 100, 150, 60,
                        "той самий\nактор і причина", size=12, bold=True,
                        fill=FILL, stroke=POS, sw=1.6))

    frags.append(line(W / 2, 70, W / 2, H - 24, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ПРАВОРУЧ: правильний зріз за причиною зміни ──
    frags.append(text(W / 2 + 240, 74, "ВІРНО: різати за причиною", size=14, bold=True, color=FIELD))
    frags.append(text(W / 2 + 240, 96, "різні актори тягнуть у різні боки → шов реальний",
                      size=11, color=MUTED))
    cuts = [
        ("Зміст звіту", "аналітика: інші цифри"),
        ("Подання (PDF)", "дизайн: шрифт, логотип"),
        ("Збереження", "БД: інша схема"),
    ]
    cx0, cy0 = W / 2 + 60, 150
    for i, (nm, who) in enumerate(cuts):
        yy = cy0 + i * 82
        frags.append(fitbox(cx0, yy, 230, 60, nm + "\n" + who, size=12, bold=True,
                            fill="#f2faf5", stroke=FIELD, sw=1.8))
        frags.append(fitbox(cx0 + 246, yy + 8, 120, 44, "свій\nактор", size=12, bold=True,
                            fill=FILL, stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, 'axis-of-change.svg'), W, H, *frags,
           title="Різати за причиною зміни, а не за технічним дієсловом")


# ── Дорога SRP: віхи в часі + яке непорозуміння кожна виправила ──────────────
def fig_srp_timeline():
    W, H = 1040, 560
    frags = []

    frags.append(text(W / 2, 30, "Дорога SRP: від зв'язності до «одного актора»",
                      size=17, bold=True, color=INK))

    # Вісь часу
    axis_y = 150
    x0, x1 = 70, W - 70
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.4))
    frags.append(arrow(x1 - 2, axis_y, x1 + 24, axis_y, color=INK, sw=2.4))
    frags.append(text(x1 + 20, axis_y - 12, "час", size=12, italic=True, color=MUTED))

    # Чотири віхи: (x, рік, хто/що; знизу — яку ваду виправив)
    miles = [
        (150, "1960–70-ті", "Ларрі Константин",
         "виміряв зв'язність\nі зчеплення",
         "ще лише «на око»:\nщабель відчувають,\nне міряють", NEG),
        (390, "кінець 1970-х", "ДеМарко · Пейдж-Джонс",
         "зв'язність —\nу практику",
         "настанова є,\nа точної лінійки\nще нема", NEG),
        (650, "2003", "Роберт Мартин",
         "ім'я SRP:\n«одна причина\nдля зміни»",
         "слово «причина»\nдвозначне —\nвидно всюди", POS),
        (890, "2014", "розбір Мартина",
         "уточнив:\n«один актор»",
         "причина = ЛЮДИ,\nщо просять зміну", FIELD),
    ]

    for mx, year, who, what, fix, col in miles:
        # верхня картка: хто + що зробив
        top, tw, th = textbox(mx, axis_y - 88, who + "\n" + what, size=11.5, bold=True,
                              fill=FILL, stroke=col, sw=1.8, pad=9, min_w=170)
        # конектор точка→картка (веде ПОВЗ рік, який стоїть збоку від точки)
        frags.append(line(mx, axis_y - 8, mx, axis_y - 88 + th / 2, color=col, sw=1.4))
        frags.append(top)
        # точка на осі (поверх конектора)
        frags.append(circle(mx, axis_y, 8, fill=col, stroke=INK, sw=1.6))
        # рік — над-праворуч від точки: осторонь і вертикального конектора (x=mx), і горизонтальної осі
        frags.append(text(mx + 14, axis_y - 14, year, size=12.5, bold=True, color=INK, anchor="start"))
        # нижня картка: яку ваду це виправило
        bot, bw, bh = textbox(mx, axis_y + 120, fix, size=11, bold=False,
                              fill="#fbfcfd", stroke=MUTED, sw=1.3, pad=9, min_w=170)
        frags.append(line(mx, axis_y + 8, mx, axis_y + 120 - bh / 2, color=MUTED, sw=1.2, dash="4,4"))
        frags.append(bot)

    # Підпис-смуга знизу: що визрівало наскрізь
    frags.append(text(W / 2, H - 66, "одна наскрізна нитка:",
                      size=12, bold=True, color=MUTED))
    frags.append(fitbox(W / 2 - 400, H - 52, 800, 34,
                        "«збери докупи те, що міняється разом»  —  функційна зв'язність на вершині драбини, "
                        "лише сказана дедалі точніше",
                        size=12, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, 'srp-timeline.svg'), W, H, *frags)


# ── Прихована спільна regularHours: правка звіту біжить назад у зарплату ──────
def fig_hidden_dependency():
    W, H = 940, 470
    frags = []
    frags.append(text(W / 2, 30, "Одна прихована regularHours — два актори",
                      size=16, bold=True, color=INK))

    # Актори згори
    cfo_x, coo_x, ay = 300, 700, 92
    frags.append(fitbox(cfo_x - 130, ay, 260, 50, "CFO · бухгалтерія\nправила нарахування",
                        size=12, bold=True, fill=FILL, stroke=MUTED, sw=1.4))
    frags.append(fitbox(coo_x - 130, ay, 260, 50, "COO · операції\nформат звіту",
                        size=12, bold=True, fill=FILL, stroke=MUTED, sw=1.4))

    # Методи-господарі
    my = 214
    pc, pcw, pch = textbox(cfo_x, my, "calculatePay()", size=13, bold=True,
                           fill="#fdecea", stroke=POS, sw=1.8, pad=11, min_w=190)
    hr, hrw, hrh = textbox(coo_x, my, "reportHours()", size=13, bold=True,
                           fill="#fdecea", stroke=POS, sw=1.8, pad=11, min_w=190)
    frags.append(arrow(cfo_x, ay + 52, cfo_x, my - pch / 2 - 4, color=MUTED, sw=1.8))
    frags.append(arrow(coo_x, ay + 52, coo_x, my - hrh / 2 - 4, color=MUTED, sw=1.8))
    frags.append(pc); frags.append(hr)

    # Спільна прихована одиниця внизу по центру
    ry = 382
    rb, rbw, rbh = textbox(W / 2, ry, "regularHours()\nприхований спільний хелпер",
                           size=13, bold=True, fill="#fff5e6", stroke="#b8860b",
                           sw=2.2, pad=12, min_w=320)
    # обидва методи тягнуться до спільного
    frags.append(arrow(cfo_x, my + pch / 2 + 4, W / 2 - rbw / 2 - 10, ry - 12, color=POS, sw=2.0))
    frags.append(arrow(coo_x, my + hrh / 2 + 4, W / 2 + rbw / 2 + 10, ry - 12, color=POS, sw=2.0))
    frags.append(rb)

    # «тріщина» правки: L-подібний маршрут лівим полем, ПОВЗ усі написи й рамки.
    # regularHours (лівий край) → вниз-ліворуч у поле → вгору → у calculatePay (лівий край).
    gx = 60  # ліве поле, вільне від рамок і тексту
    # два прямі сегменти (дашем) + фінальний сегмент зі стрілкою в calculatePay
    frags.append(line(W / 2 - rbw / 2 - 10, ry, gx, ry, color=NEG, sw=2.6, dash="7,5"))
    frags.append(line(gx, ry, gx, my, color=NEG, sw=2.6, dash="7,5"))
    frags.append(arrow(gx, my, cfo_x - pcw / 2 - 6, my, color=NEG, sw=2.6))
    # написи — у вільних зонах, осторонь маршруту, рамок і стрілок-конекторів
    frags.append(text(gx + 12, ry + 26, "правка для COO", size=12, bold=True,
                      color=NEG, anchor="start"))
    # «тихо ламає зарплату» — у вільному просвіті між calculatePay і reportHours,
    # осторонь вертикальної стрілки актора (x=cfo_x)
    frags.append(text((cfo_x + coo_x) / 2, my - 6, "тихо ламає", size=12, bold=True,
                      color=NEG))
    frags.append(text((cfo_x + coo_x) / 2, my + 12, "зарплату", size=12, bold=True,
                      color=NEG))

    render(os.path.join(IMG, 'hidden-dependency.svg'), W, H, *frags)


# ── Радіус зміни: God-клас (розтікається) проти розведеного (глухне) ──────────
def fig_change_radius():
    W, H = 980, 540
    frags = []
    frags.append(text(255, 34, "God-клас: зміна розтікається", size=15, bold=True, color=POS))
    frags.append(text(730, 34, "Розведено: зміна глухне на межі", size=15, bold=True, color=FIELD))
    frags.append(line(W / 2, 54, W / 2, H - 24, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВА: одна зміна б'є в усе ──
    frags.append(fitbox(70, 84, 210, 48, "зміна\n×1.5 → ×2.0", size=13, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=1.8))
    methods = ["calculatePay()", "reportHours()", "regularHours() — спільна"]
    mx, my0 = 70, 192
    for i, m in enumerate(methods):
        yy = my0 + i * 82
        frags.append(fitbox(mx, yy, 320, 56, m, size=12, bold=True,
                            fill="#fdecea", stroke=POS, sw=1.8))
        frags.append(arrow(175, 132, mx + 160, yy - 6, color=NEG, sw=1.8))
    frags.append(fitbox(70, my0 + 3 * 82 + 8, 400, 48,
                        "радіус ризику: увесь клас (3 методи)", size=12, bold=True,
                        fill=FILL, stroke=POS, sw=1.6))

    # ── ПРАВА: зміна впирається в один клас ──
    rx = W / 2 + 70
    frags.append(fitbox(rx, 84, 210, 48, "зміна\n×1.5 → ×2.0", size=13, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=1.8))
    # цільовий клас-актор
    frags.append(fitbox(rx, 192, 320, 56, "PayCalculator (CFO)", size=13, bold=True,
                        fill="#f2faf5", stroke=FIELD, sw=2.0))
    frags.append(arrow(rx + 105, 132, rx + 160, 188, color=FIELD, sw=2.0))
    # недосяжні сусіди — сірі
    frags.append(fitbox(rx, 284, 320, 50, "HourReporter (COO)", size=12, bold=True,
                        fill="#f1f2f4", stroke="#c2c7cf", sw=1.4, color=MUTED))
    frags.append(fitbox(rx, 348, 320, 50, "EmployeeRepository (CTO)", size=12, bold=True,
                        fill="#f1f2f4", stroke="#c2c7cf", sw=1.4, color=MUTED))
    frags.append(text(rx + 160, 428, "сусіди недосяжні — навіть", size=12, color=MUTED))
    frags.append(text(rx + 160, 448, "не перекомпілюються", size=12, color=MUTED))
    frags.append(fitbox(rx, 472, 320, 46, "радіус ризику: один клас", size=12, bold=True,
                        fill=FILL, stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, 'change-radius.svg'), W, H, *frags)


# ── Пастка фасаду: тонкий делегат проти розжирілого God-об'єкта ───────────────
def fig_facade_trap():
    W, H = 1000, 480
    frags = []
    frags.append(text(250, 34, "Тонкий фасад: лише делегує", size=15, bold=True, color=FIELD))
    frags.append(text(745, 34, "Розжирів: знову God-об'єкт", size=15, bold=True, color=POS))
    frags.append(line(W / 2, 54, W / 2, H - 24, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВА: тонкий фасад пропускає наскрізь ──
    fx = 135
    frags.append(fitbox(fx, 120, 200, 54, "EmployeeFacade\n(порожній)", size=12, bold=True,
                        fill="#f2faf5", stroke=FIELD, sw=1.8))
    targets = ["PayCalculator", "HourReporter", "EmployeeRepo"]
    tx = 340
    for i, t in enumerate(targets):
        yy = 104 + i * 92
        frags.append(fitbox(tx, yy, 160, 52, t, size=12, bold=True,
                            fill=FILL, stroke=MUTED, sw=1.4))
        frags.append(arrow(fx + 100, 147, tx - 4, yy + 26, color=FIELD, sw=1.8))
    frags.append(text(fx, 320, "логіки всередині нема", size=12, bold=True, color=FIELD))

    # ── ПРАВА: логіка осіла у фасаді ──
    gx = W / 2 + 265
    gb, gbw, gbh = textbox(gx, 200, "EmployeeFacade\n+ податок 0.18 (CFO)\n+ формат net (COO)",
                           size=12, bold=True, fill="#fdecea", stroke=POS, sw=2.4, pad=13, min_w=240)
    # два актори знову тягнуться в один об'єкт
    frags.append(fitbox(W / 2 + 45, 108, 150, 50, "CFO", size=12, bold=True,
                        fill=FILL, stroke=MUTED, sw=1.4))
    frags.append(fitbox(W / 2 + 45, 312, 150, 50, "COO", size=12, bold=True,
                        fill=FILL, stroke=MUTED, sw=1.4))
    frags.append(arrow(W / 2 + 120, 158, gx - gbw / 2 - 4, 186, color=POS, sw=2.0))
    frags.append(arrow(W / 2 + 120, 312, gx - gbw / 2 - 4, 214, color=POS, sw=2.0))
    frags.append(gb)
    frags.append(text(gx, 200 + gbh / 2 + 28, "два актори — знову God-клас",
                      size=12, bold=True, color=POS))

    render(os.path.join(IMG, 'facade-trap.svg'), W, H, *frags)


# ── Матриця сумісної зміни: відповідальність як блок в історії правок ─────────
def fig_cochange_matrix():
    W, H = 1060, 620
    frags = []
    frags.append(text(W / 2, 26,
                      "Матриця сумісної зміни: відповідальність видно з історії правок",
                      size=16, bold=True, color=INK))

    x0, y0 = 210, 120
    cw, ch = 64, 54
    cols, rows = 6, 5
    xR = x0 + cols * cw          # 594
    yB = y0 + rows * ch          # 390

    col_actor = [POS, POS, POS, FIELD, FIELD, FIELD]     # A A A | B B B
    col_lab = ["A₁", "A₂", "A₃", "B₁", "B₂", "B₃"]
    row_lab = ["calculatePay", "payRules", "reportRow", "reportFormat", "regularHours"]
    touch = {0: [0, 2], 1: [1], 2: [3, 5], 3: [4], 4: [2, 3]}   # рядок 4 — витік

    # заголовок над сіткою
    frags.append(text(x0 + 3 * cw, y0 - 60, "правки в часі →",
                      size=12, italic=True, color=MUTED))

    # порожня сітка
    for i in range(rows):
        for j in range(cols):
            cx = x0 + (j + 0.5) * cw
            cy = y0 + (i + 0.5) * ch
            frags.append(rect(cx - 24, cy - 20, 48, 40, fill="#fbfcfd",
                              stroke="#e3e7ec", sw=1.0, rx=5))
    # заповнені клітини — колір актора стовпця
    for i in range(rows):
        for j in touch[i]:
            cx = x0 + (j + 0.5) * cw
            cy = y0 + (i + 0.5) * ch
            col = col_actor[j]
            fillc = "#fdecea" if col == POS else "#eafaf0"
            frags.append(rect(cx - 24, cy - 20, 48, 40, fill=fillc, stroke=col, sw=2.2, rx=5))

    # заголовки стовпців: крапка актора + мітка
    for j in range(cols):
        cx = x0 + (j + 0.5) * cw
        frags.append(circle(cx, y0 - 20, 7, fill=col_actor[j], stroke=INK, sw=1.2))
        frags.append(text(cx, y0 - 34, col_lab[j], size=12, bold=True, color=INK))
    # мітки рядків
    for i in range(rows):
        cy = y0 + (i + 0.5) * ch
        frags.append(text(x0 - 14, cy + 4, row_lab[i], size=12, color=INK, anchor="end"))

    # роздільник акторів (між 3-м і 4-м стовпцями)
    dx = x0 + 3 * cw
    frags.append(line(dx, y0 - 8, dx, yB + 8, color=MUTED, sw=1.4, dash="5,5"))

    # межі-відповідальності (блоки) + підсвітка витоку
    frags.append(rect(x0 + 2, y0 + 2, 3 * cw - 4, 2 * ch - 4, fill="none", stroke=POS, sw=2.6, rx=8))
    frags.append(rect(x0 + 3 * cw + 2, y0 + 2 * ch + 2, 3 * cw - 4, 2 * ch - 4,
                      fill="none", stroke=FIELD, sw=2.6, rx=8))
    frags.append(rect(x0 + 2 * cw + 3, y0 + 4 * ch + 3, 2 * cw - 6, ch - 6,
                      fill="none", stroke=POS, sw=2.2, rx=8))

    # праві анотації, вирівняні по центрах блоків
    frags.append(fitbox(636, 148, 214, 56, "Відповідальність A\nнарахування · CFO",
                        size=12, bold=True, fill="#fdecea", stroke=POS, sw=1.8))
    frags.append(fitbox(636, 256, 214, 56, "Відповідальність B\nзвіт · COO",
                        size=12, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8))

    # підпис витоку під сіткою (нижче кінця роздільника)
    frags.append(text(x0 + 2.5 * cw, yB + 22,
                      "витік: спільний рядок тягнуть обидва актори", size=12, bold=True, color=POS))
    frags.append(text(x0 + 2.5 * cw, yB + 40,
                      "правка одного мовчки міняє іншого", size=11, color=MUTED))

    # легенда кольорів
    ly = 486
    frags.append(circle(250, ly, 7, fill=POS, stroke=INK, sw=1.2))
    frags.append(text(266, ly + 4, "правка від актора A (CFO)", size=12, color=INK, anchor="start"))
    frags.append(circle(560, ly, 7, fill=FIELD, stroke=INK, sw=1.2))
    frags.append(text(576, ly + 4, "правка від актора B (COO)", size=12, color=INK, anchor="start"))

    # підсумкова смуга
    frags.append(fitbox(W / 2 - 440, 545, 880, 44,
                        "Стовпці — правки в часі, рядки — елементи коду. Що завжди спалахує "
                        "разом — одна відповідальність; рядок, у який б'ють правки з обох боків, — "
                        "шов, що тече.",
                        size=12, fill="#f2faf5", stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, 'cochange-matrix.svg'), W, H, *frags)


# ── Один розріз на кожному масштабі: концентричні поверхи SRP ─────────────────
def fig_scales_of_srp():
    W, H = 940, 640
    frags = []
    frags.append(text(W / 2, 28, "Один розріз — на кожному масштабі", size=17, bold=True, color=INK))

    # концентричні коробки (від найбільшої до найменшої), усі центровані на x=470
    boxes = [
        (50, 80, 840, 520, "#eef4ff", NEG),
        (120, 180, 700, 380, "#f2faf5", FIELD),
        (200, 280, 540, 220, "#fff5e6", "#b8860b"),
        (290, 370, 360, 100, "#fdecea", POS),
    ]
    for x, y, w, h, fillc, stroke in boxes:
        frags.append(rect(x, y, w, h, fill=fillc, stroke=stroke, sw=2.2, rx=12))

    labels = [
        (112, "Служба / обмежений контекст", "одна служба — одна зона зміни й розгортання", NEG),
        (212, "Компонент / пакет — CCP", "класи, що міняються разом і в той самий час", FIELD),
        (312, "Клас — SRP", "один клас — один актор", "#b8860b"),
        (412, "Функція", "рахує АБО друкує — не те й те разом", POS),
    ]
    for ty, title, sub, col in labels:
        frags.append(text(470, ty, title, size=14, bold=True, color=col))
        frags.append(text(470, ty + 21, sub, size=11.5, color=MUTED))

    frags.append(text(470, 626,
                      "Та сама вісь «одна причина для зміни» — змінюється лише розмір коробки.",
                      size=12.5, italic=True, color=INK))

    render(os.path.join(IMG, 'scales-of-srp.svg'), W, H, *frags)


# ── Наскрізна турбота: розмазано по модулях vs зібрано в один шар ─────────────
def fig_cross_cutting():
    W, H = 1080, 560
    frags = []
    frags.append(text(W / 2, 26, "Наскрізна турбота: концерн, що не лягає «в одне місце»",
                      size=16, bold=True, color=INK))
    frags.append(text(285, 60, "Розмазано по кожному модулю", size=14, bold=True, color=POS))
    frags.append(text(810, 60, "Зібрано в один шар-обгортку", size=14, bold=True, color=FIELD))
    frags.append(line(540, 74, 540, 470, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВА: три модулі, у кожному ті самі три концерни ──
    centers = [190, 330, 470]
    titles = ["Замовлення", "Оплата", "Доставка"]
    chunks = [
        ("логіка", FILL, MUTED),
        ("журнал", "#eaf0fd", NEG),
        ("транзакція", "#fff5e6", "#b8860b"),
        ("авторизація", "#fdecea", POS),
    ]
    cy_rows = [168, 214, 260, 306]
    for k, cx in enumerate(centers):
        frags.append(rect(cx - 56, 140, 112, 250, fill="#ffffff", stroke=MUTED, sw=1.4, rx=8))
        frags.append(text(cx, 128, titles[k], size=12.5, bold=True, color=INK))
        for r, (lab, fillc, stroke) in enumerate(chunks):
            frags.append(rect(cx - 46, cy_rows[r] - 19, 92, 38, fill=fillc, stroke=stroke, sw=1.6, rx=6))
            if k == 0:                       # мітки лише в першому модулі
                frags.append(text(cx, cy_rows[r] + 4, lab, size=10.5, bold=True, color=stroke))
    frags.append(text(285, 418, "три однакові концерни — знову в кожному модулі",
                      size=12, color=MUTED))

    # ── ПРАВА: вертикальний конвеєр декораторів ──
    px = 800
    pipe = [
        (120, "запит", FILL, MUTED, 40),
        (176, "журнал", "#eaf0fd", NEG, 40),
        (232, "транзакція", "#fff5e6", "#b8860b", 40),
        (288, "авторизація", "#fdecea", POS, 40),
        (352, "ядро — будь-який модуль", "#eafaf0", FIELD, 52),
    ]
    prev_bottom = None
    for cy, lab, fillc, stroke, bh in pipe:
        top = cy - bh / 2
        if prev_bottom is not None:
            frags.append(arrow(px, prev_bottom, px, top - 2, color=MUTED, sw=1.8))
        frags.append(fitbox(px - 108, top, 216, bh, lab, size=12, bold=True,
                            fill=fillc, stroke=stroke, sw=1.8))
        prev_bottom = cy + bh / 2
    frags.append(text(810, 418, "кожен концерн — рівно один раз; ядро про них не знає",
                      size=12, color=MUTED))

    frags.append(fitbox(W / 2 - 445, 496, 890, 44,
                        "Наскрізний концерн прибирають з ядра не «в один модуль», а в один шар, що "
                        "ОБГОРТАЄ модулі — декоратор / аспект / middleware. Ядро лишається з єдиним актором.",
                        size=12, fill="#f2faf5", stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, 'cross-cutting.svg'), W, H, *frags)


# ── Граф методів: роз'єднані групи (LCOM4=3) vs спільний блоб (LCOM4=1) ───────
def fig_lcom_graphs():
    W, H = 1000, 560
    frags = []

    # Заголовки панелей + значення метрики
    frags.append(text(250, 40, "Роз'єднані групи полів → LCOM4 = 3",
                      size=15, bold=True, color=FIELD))
    frags.append(text(748, 40, "Спільний data_ → LCOM4 = 1 (акторів 3!)",
                      size=15, bold=True, color=POS))
    frags.append(line(W / 2, 60, W / 2, H - 60, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВА панель: клас-грабег, три пари без спільних полів між парами ──
    frags.append(text(250, 80, "клас Toolbox — три чужі одна одній роботи",
                      size=11.5, italic=True, color=MUTED))
    pairs = [
        ("add()", "average()", "спільне: total_, n_", 150, 1),
        ("store()", "fetch()", "спільне: slots_, head_", 280, 2),
        ("reseed()", "rand()", "спільне: state_", 410, 3),
    ]
    axL, bxL = 150, 330
    for a, b, fld, ry, idx in pairs:
        # підпис спільного поля — над парою, у вільному просвіті
        frags.append(text(240, ry - 40, fld, size=11.5, bold=True, color=INK))
        ba, baw, bah = textbox(axL, ry, a, size=12.5, bold=True,
                               fill=FILL, stroke=MUTED, sw=1.5, pad=11, min_w=112)
        bb, bbw, bbh = textbox(bxL, ry, b, size=12.5, bold=True,
                               fill=FILL, stroke=MUTED, sw=1.5, pad=11, min_w=112)
        # ребро (спільне поле) — між рамками, поза текстом
        frags.append(line(axL + baw / 2 + 2, ry, bxL - bbw / 2 - 2, ry,
                          color=FIELD, sw=2.4))
        frags.append(ba); frags.append(bb)
        # бейдж номера компоненти праворуч
        frags.append(circle(452, ry, 14, fill="#eafaf0", stroke=FIELD, sw=2.0))
        frags.append(text(452, ry + 5, str(idx), size=14, bold=True, color=FIELD))
    frags.append(text(250, H - 74, "три компоненти = три відповідальності",
                      size=12, bold=True, color=FIELD))

    # ── ПРАВА панель: клас Employee, повний граф через спільний data_ ──
    frags.append(text(748, 80, "клас Employee — усі методи читають data_",
                      size=11.5, italic=True, color=MUTED))
    top = (740, 178)
    bl = (632, 372)
    br = (850, 372)
    # три ребра трикутника (кінці — трохи ПОЗА рамками, не під текстом)
    frags.append(line(709, 205, 648, 344, color=POS, sw=2.4))  # top–bl
    frags.append(line(771, 205, 852, 344, color=POS, sw=2.4))  # top–br
    frags.append(line(709, 372, 773, 372, color=POS, sw=2.4))  # bl–br
    # спільне поле — коротка мітка в центрі трикутника, осторонь ребер
    frags.append(text(740, 300, "поле data_", size=11.5, bold=True, color="#b8860b"))
    # вузли-методи з актором другим рядком
    for (cx, cy), m, act in [(top, "calculatePay", "актор: CFO"),
                             (bl, "reportHours", "актор: COO"),
                             (br, "save", "актор: CTO")]:
        nb, nbw, nbh = textbox(cx, cy, m + "\n" + act, size=12, bold=True,
                               fill="#fdecea", stroke=POS, sw=1.9, pad=10, min_w=150)
        frags.append(nb)
    frags.append(text(748, H - 74, "повний граф = 1 компонента, хоч акторів троє",
                      size=12, bold=True, color=POS))

    # ── підсумкова смуга ──
    frags.append(fitbox(W / 2 - 462, H - 50, 924, 38,
                        "LCOM4 = число зв'язних компонент графа методів. Спільне поле склеює "
                        "методи в одну компоненту — тому спільний data_ ошукує метрику в «1», "
                        "хоча відповідальностей три.",
                        size=12, fill="#f2faf5", stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, 'lcom-graphs.svg'), W, H, *frags)


# ── Конвеєр аналізу сумісної зміни: git log → карта прихованих швів ───────────
def fig_cochange_pipeline():
    W, H = 1140, 450
    frags = []
    frags.append(text(W / 2, 30, "Конвеєр аналізу сумісної зміни: від git log до карти швів",
                      size=16, bold=True, color=INK))

    cy = 200
    w, h = 180, 96
    lefts = [40, 260, 480, 700, 920]
    stages = [
        ("git log\n--name-only\nкоміт → його файли", FILL, MUTED),
        ("відсів шуму\nкоміт > K файлів\n— геть", "#fdecea", POS),
        ("пари файлів\ncombinations(f, 2)\n+1 кожній парі", FILL, MUTED),
        ("метрика\nsupport = разом\nconfidence = разом / усіх", "#fff5e6", "#b8860b"),
        ("ранг\nкарта прихованих\nшвів SRP", "#f2faf5", FIELD),
    ]
    for x, (txt, fillc, stroke) in zip(lefts, stages):
        frags.append(fitbox(x, cy - h / 2, w, h, txt, size=12, bold=True,
                            fill=fillc, stroke=stroke, sw=1.8))
    for i in range(4):
        frags.append(arrow(lefts[i] + w + 2, cy, lefts[i + 1] - 2, cy, color=INK, sw=1.8))

    sx = lefts[1] + w / 2
    frags.append(arrow(sx, cy + h / 2 + 2, sx, 306, color=POS, sw=1.8))
    frags.append(fitbox(sx - 155, 308, 310, 56, "мега-рефактор · bulk-rename · merge\n→ у смітник",
                        size=11.5, bold=True, fill="#fdecea", stroke=POS, sw=1.6))

    frags.append(fitbox(W / 2 - 470, 396, 940, 40,
                        "Коміт — це «кошик»: файли, що лягли в один коміт, «купують разом». "
                        "Що частіше разом — то ймовірніше одна прихована відповідальність.",
                        size=12, fill="#f2faf5", stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, 'cochange-pipeline.svg'), W, H, *frags)


# ── Метрика сумісної зміни: support разом + асиметрична впевненість ───────────
def fig_support_confidence():
    W, H = 1000, 480
    frags = []
    frags.append(text(W / 2, 32, "Метрика: наскільки разом — і наскільки окремо",
                      size=16, bold=True, color=INK))

    a, aw, ah = textbox(250, 160, "pay_calculator.py\nмінявся 4×", size=13, bold=True,
                        fill="#fdecea", stroke=POS, sw=1.8, pad=12, min_w=240)
    b, bw, bh = textbox(750, 160, "hours_policy.py\nмінявся 7×", size=13, bold=True,
                        fill="#fff5e6", stroke="#b8860b", sw=1.8, pad=12, min_w=240)
    frags.append(a); frags.append(b)
    frags.append(arrow(250 + aw / 2 + 4, 160, 750 - bw / 2 - 4, 160, color=INK, sw=2.0))
    frags.append(arrow(750 - bw / 2 - 4, 160, 250 + aw / 2 + 4, 160, color=INK, sw=2.0))
    frags.append(text(500, 138, "разом: 4 коміти  (support)", size=13, bold=True, color=INK))

    frags.append(fitbox(120, 250, 760, 58,
        "впевненість  pay_calculator ⇒ hours_policy  =  4 / 4  =  1.00     "
        "(щоразу, як міняли pay, міняли й policy)",
        size=12.5, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.8))
    frags.append(fitbox(120, 330, 760, 58,
        "впевненість  hours_policy ⇒ pay_calculator  =  4 / 7  =  0.57     "
        "(policy тягне ще й звіт — назад тримає слабше)",
        size=12.5, bold=True, fill="#fbfcfd", stroke=MUTED, sw=1.6))

    frags.append(fitbox(W / 2 - 460, 410, 920, 44,
        "Та сама пара — різна впевненість у два боки. Слабший зворотний бік означає, що "
        "hours_policy служить не одному господареві: це хаб, крізь який тече спільний шов.",
        size=12, fill="#eef4ff", stroke=NEG, sw=1.4))

    render(os.path.join(IMG, 'support-confidence.svg'), W, H, *frags)


# ── Дві тіні: структурний граф полів (мовчить) vs історія комітів (кричить) ────
def fig_logical_vs_structural():
    W, H = 1040, 470
    frags = []
    frags.append(text(W / 2, 30, "Дві тіні відповідальності: граф полів мовчить — історія кричить",
                      size=15.5, bold=True, color=INK))
    frags.append(line(W / 2, 58, W / 2, H - 70, color="#d0d5db", sw=1.2, dash="5,5"))

    # ЛІВА: структурний граф (LCOM) — ребра нема
    frags.append(text(270, 84, "Структура: граф спільних полів (LCOM)",
                      size=13.5, bold=True, color=NEG))
    n1, n1w, n1h = textbox(270, 160, "order_service.py", size=12.5, bold=True,
                           fill=FILL, stroke=MUTED, sw=1.6, min_w=210)
    n2, n2w, n2h = textbox(270, 320, "payment_schema.sql", size=12.5, bold=True,
                           fill=FILL, stroke=MUTED, sw=1.6, min_w=210)
    frags.append(n1); frags.append(n2)
    frags.append(fitbox(270 - 95, 218, 190, 46, "нема спільного\nсимволу → ребра нема",
                        size=11.5, bold=True, fill="#ffffff", stroke="#c2c7cf", sw=1.2))

    # ПРАВА: історія (сумісна зміна) — товсте ребро
    frags.append(text(770, 84, "Історія: сумісна зміна (git log)",
                      size=13.5, bold=True, color=FIELD))
    m1, m1w, m1h = textbox(770, 160, "order_service.py", size=12.5, bold=True,
                           fill=FILL, stroke=MUTED, sw=1.6, min_w=210)
    m2, m2w, m2h = textbox(770, 320, "payment_schema.sql", size=12.5, bold=True,
                           fill=FILL, stroke=MUTED, sw=1.6, min_w=210)
    frags.append(line(770, 160 + m1h / 2 + 4, 770, 320 - m2h / 2 - 4, color=FIELD, sw=6))
    frags.append(m1); frags.append(m2)
    frags.append(fitbox(770 + 66, 218, 184, 46, "12× разом\nconf 0.9",
                        size=12.5, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.6))

    frags.append(fitbox(W / 2 - 470, H - 58, 940, 44,
        "Два файли без жодного спільного символу — граф полів не з'єднає їх нічим. "
        "Але міняються завжди разом: логічне зчеплення. Цю тінь бачить лише історія.",
        size=12, fill="#f2faf5", stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, 'logical-vs-structural.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_one_actor()
    fig_axis_of_change()
    fig_srp_timeline()
    fig_hidden_dependency()
    fig_change_radius()
    fig_facade_trap()
    fig_cochange_matrix()
    fig_scales_of_srp()
    fig_cross_cutting()
    fig_lcom_graphs()
    fig_cochange_pipeline()
    fig_support_confidence()
    fig_logical_vs_structural()
    print("figures written to", IMG)
