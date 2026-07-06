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


if __name__ == "__main__":
    fig_one_actor()
    fig_axis_of_change()
    fig_srp_timeline()
    fig_hidden_dependency()
    fig_change_radius()
    fig_facade_trap()
    print("figures written to", IMG)
