# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Зміна розтікається (за шаром) проти зміна замкнена (за причиною) ───────────
def fig_change_scatter():
    W, H = 1080, 580
    frags = []

    frags.append(text(280, 42, "Групування за шаром: зміна розтікається",
                      size=15, bold=True, color=POS))
    frags.append(text(800, 42, "Групування за причиною: зміна замкнена",
                      size=15, bold=True, color=FIELD))
    frags.append(line(W / 2, 62, W / 2, H - 66, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВА панель: три компоненти-шари, податок розмазаний по всіх ──
    chg_l = fitbox(55, 246, 150, 74, "зміна:\nправило\nподатку", size=12.5, bold=True,
                   fill="#eaf0fd", stroke=NEG, sw=2.0)
    boxes_L = [
        (300, 96, "Перевірки\n(тут: сума податку)"),
        (300, 248, "Подання\n(тут: показ податку)"),
        (300, 400, "Сховище\n(тут: запис податку)"),
    ]
    bw, bh = 210, 68
    for bx, by, lab in boxes_L:
        frags.append(fitbox(bx, by, bw, bh, lab, size=12, bold=True,
                            fill="#fdecea", stroke=POS, sw=2.0))
        # стрілка від зміни до лівого краю компонента
        frags.append(arrow(205, 283, bx - 4, by + bh / 2, color=NEG, sw=2.0))
    frags.append(chg_l)
    frags.append(fitbox(70, 496, 400, 44, "3 компоненти перебудувати й розгорнути",
                        size=12.5, bold=True, fill=FILL, stroke=POS, sw=1.8))

    # ── ПРАВА панель: три компоненти-здатності, торкається лише податок ──
    chg_r = fitbox(560, 246, 150, 74, "зміна:\nправило\nподатку", size=12.5, bold=True,
                   fill="#eaf0fd", stroke=NEG, sw=2.0)
    rx = 800
    # той, що міняється — зелений
    frags.append(fitbox(rx, 96, bw, bh, "Податок\nперевірка · показ · запис",
                        size=12, bold=True, fill="#f2faf5", stroke=FIELD, sw=2.2))
    frags.append(arrow(710, 283, rx - 4, 96 + bh / 2, color=FIELD, sw=2.2))
    # сусіди — закриті, сірі
    frags.append(fitbox(rx, 248, bw, bh, "Доставка\n(закрита)", size=12, bold=True,
                        fill="#f1f2f4", stroke="#c2c7cf", sw=1.4, color=MUTED))
    frags.append(fitbox(rx, 400, bw, bh, "Знижка\n(закрита)", size=12, bold=True,
                        fill="#f1f2f4", stroke="#c2c7cf", sw=1.4, color=MUTED))
    frags.append(text(rx + bw / 2, 356, "сусіди не перекомпілюються", size=11.5, color=MUTED))
    frags.append(fitbox(560, 496, 450, 44, "1 компонент перебудувати й розгорнути",
                        size=12.5, bold=True, fill=FILL, stroke=FIELD, sw=1.8))

    frags.append(fitbox(W / 2 - 470, H - 50, 940, 40,
                        "CCP: згрупуй в один компонент те, що міняється з однієї причини — "
                        "тоді зміна замикається в ньому, а не розтікається системою.",
                        size=12.5, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, 'change-scatter.svg'), W, H, *frags)


# ── Трикутник напруг REP · CCP · CRP ──────────────────────────────────────────
def fig_tension_triangle():
    W, H = 1000, 620
    frags = []

    # вершини (центри) — REP згори, CRP зліва-внизу, CCP справа-внизу
    rep = (500, 150)
    crp = (235, 470)
    ccp = (765, 470)

    # сторони трикутника (малюємо ПЕРШИМИ, рамки-вершини накриють кінці)
    frags.append(line(rep[0], rep[1], crp[0], crp[1], color=MUTED, sw=2.0))   # ліва
    frags.append(line(rep[0], rep[1], ccp[0], ccp[1], color=MUTED, sw=2.0))   # права
    frags.append(line(crp[0], crp[1], ccp[0], ccp[1], color=MUTED, sw=2.0))   # низ

    # вершини-рамки (поверх ліній)
    frags.append(fitbox(rep[0] - 130, rep[1] - 42, 260, 84,
                        "REP\nеквівалентність\nвипуску й повтору\n(↑ більший компонент)",
                        size=11.5, bold=True, fill=FILL, stroke=MUTED, sw=1.8))
    frags.append(fitbox(crp[0] - 130, crp[1] - 40, 260, 80,
                        "CRP\nспільне повторне\nвикористання\n(↓ менший компонент)",
                        size=11.5, bold=True, fill=FILL, stroke=MUTED, sw=1.8))
    frags.append(fitbox(ccp[0] - 130, ccp[1] - 40, 260, 80,
                        "CCP\nспільне закриття\n(↑ більший компонент)",
                        size=11.5, bold=True, fill="#f2faf5", stroke=FIELD, sw=2.4))

    # підписи сторін — ЦІНА відмови від протилежної вершини (поза трикутником)
    frags.append(fitbox(18, 262, 236, 74,
                        "знехтувати CCP →\nзміна б'є в багато\nкомпонентів",
                        size=12, bold=True, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(fitbox(746, 262, 236, 74,
                        "знехтувати CRP →\nтягнеш зайве,\nзайві випуски",
                        size=12, bold=True, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(fitbox(316, 506, 368, 40,
                        "знехтувати REP → нема чого повторно використати",
                        size=12, bold=True, fill="#fdecea", stroke=POS, sw=1.6))

    # примітка про дозрівання
    frags.append(fitbox(120, 566, 760, 40,
                        "Молодий проєкт тулиться до CCP (швидко міняти важливіше за повтор); "
                        "зрілий — зсувається до REP / CRP.",
                        size=12, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, 'tension-triangle.svg'), W, H, *frags,
           title="Три сили зв'язності компонента — і їхнє натягування")


# ── Шість колонок «Engineering Notebook» і те, що було далі ───────────────────
def fig_notebook_timeline():
    W, H = 1200, 545
    frags = []

    frags.append(text(W / 2, 32, "«Engineering Notebook» у The C++ Report: шість колонок",
                      size=17, bold=True))

    cols = [
        ("січень 1996", "The Open-Closed\nPrinciple\n\nOCP", False),
        ("березень 1996", "The Liskov Substitution\nPrinciple\n\nLSP", False),
        ("червень 1996", "The Dependency\nInversion Principle\n\nDIP", False),
        ("серпень 1996", "The Interface\nSegregation Principle\n\nISP", False),
        ("листопад/грудень 1996", "Granularity\nс. 57–62\n\nREP · CRP · CCP · ADP", True),
        ("лютий 1997", "Large-scale stability\nс. 54–60\n\nSDP · SAP", False),
    ]
    bw, bh, by = 165, 104, 92
    for i, (date, body, hot) in enumerate(cols):
        bx = 55 + i * 185
        cx = bx + bw / 2
        frags.append(text(cx, 78, date, size=11, color=MUTED))
        frags.append(fitbox(bx, by, bw, bh, body, size=12, bold=True,
                            fill="#f2faf5" if hot else FILL,
                            stroke=FIELD if hot else MUTED,
                            sw=2.4 if hot else 1.6))
        frags.append(line(cx, by + bh, cx, 214, color="#c2c7cf", sw=1.2))

    frags.append(line(45, 214, 1155, 214, color=MUTED, sw=1.8))
    frags.append(line(785, 66, 785, 236, color=NEG, sw=1.6, dash="6,5"))

    frags.append(fitbox(55, 244, 720, 40,
                        "колонки 1–4: мікроструктура — принципи КЛАСУ",
                        size=12.5, bold=True, fill=FILL, stroke=MUTED, sw=1.6))
    frags.append(fitbox(795, 244, 350, 40,
                        "колонки 5–6: макроструктура — ПАКЕТА",
                        size=12.5, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.8))

    frags.append(text(W / 2, 330, "Далі — уже поза журналом", size=15, bold=True))
    later = [
        (55, "2000 · «Design Principles\nand Design Patterns»\n\nнапругу названо вголос:\n"
             "три принципи взаємно виключні,\nбо служать різним людям"),
        (425, "2002 · «Agile Software Development:\nPrinciples, Patterns, and Practices»\n\n"
              "обіцяну 1996-го книжку нарешті\nвидано — під іншою назвою"),
        (795, "2017 · «Clean Architecture»\n\n«пакет» → «компонент»;\nтрикутник напруг;\n"
              "у формулюванні CCP слова\n«закриття» вже немає"),
    ]
    for lx, body in later:
        frags.append(fitbox(lx, 348, 350, 150, body, size=12, fill=FILL, stroke=MUTED, sw=1.6))

    render(os.path.join(IMG, 'notebook-timeline.svg'), W, H, *frags)


# ── Один і той самий REP у двох різних поділах ────────────────────────────────
def fig_rep_switches_camp():
    W, H = 1120, 445
    frags = []

    frags.append(text(W / 2, 30, "Три ті самі принципи — два різні поділи на табори",
                      size=17, bold=True))
    frags.append(line(560, 58, 560, 272, color="#d0d5db", sw=1.2, dash="5,5"))

    def camp(gx, cap_small, cap_big, chips, stroke):
        out = [rect(gx, 96, 210, 160, fill="#fbfcfd", stroke=stroke, sw=1.6),
               text(gx + 105, 118, cap_small, size=11, color=MUTED),
               text(gx + 105, 137, cap_big, size=12.5, bold=True, color=stroke)]
        for k, (lab, col) in enumerate(chips):
            out.append(fitbox(gx + 25, 152 + k * 48, 160, 40, lab, size=14, bold=True,
                              fill="#eaf0fd" if col is NEG else FILL,
                              stroke=col, sw=2.2))
        return out

    frags.append(text(285, 78, "2000 · вісь: КОМУ це полегшує життя", size=13, bold=True))
    frags += camp(60, "легше тим, хто", "БЕРЕ ЧУЖЕ", [("REP", NEG), ("CRP", MUTED)], MUTED)
    frags += camp(300, "легше тим, хто", "СУПРОВОДЖУЄ", [("CCP", FIELD)], FIELD)

    frags.append(text(825, 78, "2017 · вісь: ЩО це робить з розміром", size=13, bold=True))
    frags += camp(600, "об'єднавчі", "↑ БІЛЬШИЙ", [("REP", NEG), ("CCP", FIELD)], FIELD)
    frags += camp(840, "роздільний", "↓ МЕНШИЙ", [("CRP", MUTED)], MUTED)

    frags.append(fitbox(60, 296, 990, 62,
                        "REP не змінював змісту — змінилася ВІСЬ поділу.\n"
                        "За тим, «кому легше» (2000), REP стоїть із CRP; за тим, "
                        "«що робить з розміром» (2017) — із CCP.",
                        size=12.5, fill="#eaf0fd", stroke=NEG, sw=1.6))
    frags.append(fitbox(60, 372, 990, 44,
                        "Незмінне за обома поділами одне: CCP і CRP завжди у ворожих "
                        "таборах. Це і є справжня напруга.",
                        size=12.5, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, 'rep-switches-camp.svg'), W, H, *frags)


# ── Замикання перезбирання: граф до/після переносу (вставка proj) ─────────────
def fig_rebuild_closure():
    W, H = 1280, 700
    frags = []

    EDIT = dict(fill="#fdecea", stroke=POS, sw=2.4)                     # редаговано
    REBLD = dict(fill="#eaf0fd", stroke=NEG, sw=2.2)                    # тягне перезбирання
    SHUT = dict(fill="#f1f2f4", stroke="#c2c7cf", sw=1.4, color=MUTED)  # закрите

    # ── легенда ──
    frags.append(fitbox(285, 54, 130, 30, "редаговано", size=11.5, bold=True, **EDIT))
    frags.append(fitbox(435, 54, 340, 30, "не редаговано, але перезбирається",
                        size=11.5, bold=True, **REBLD))
    frags.append(fitbox(795, 54, 200, 30, "закрите — не рухається", size=11.5, bold=True, **SHUT))

    frags.append(line(635, 100, 635, 640, color="#d0d5db", sw=1.2, dash="5,5"))

    frags.append(text(340, 112, "До: компоненти за технічним шаром", size=14, bold=True, color=POS))
    frags.append(text(960, 112, "Після: компоненти за віссю зміни", size=14, bold=True, color=FIELD))

    # ── ЛІВОРУЧ: шарова розкладка ──
    frags.append(fitbox(75, 130, 190, 52, "api\ncheckout.ts", size=12, bold=True, **REBLD))
    frags.append(fitbox(75, 242, 150, 52, "validation\n3 файли", size=12, bold=True, **EDIT))
    frags.append(fitbox(265, 242, 150, 52, "presentation\n3 файли", size=12, bold=True, **EDIT))
    frags.append(fitbox(455, 242, 150, 52, "persistence\n3 файли", size=12, bold=True, **EDIT))
    frags.append(fitbox(75, 354, 530, 52, "model — money.ts · order.ts (2 файли)",
                        size=12, bold=True, **SHUT))

    frags.append(arrow(150, 182, 150, 238))
    frags.append(arrow(210, 182, 336, 238))
    frags.append(arrow(240, 182, 524, 238))
    frags.append(arrow(261, 268, 231, 268))
    frags.append(arrow(150, 294, 150, 350))
    frags.append(arrow(340, 294, 340, 350))
    frags.append(arrow(530, 294, 530, 350))
    # api → model: смугою повз рамки, щоб нічого не перетинати
    frags.append(line(75, 156, 50, 156))
    frags.append(line(50, 156, 50, 380))
    frags.append(arrow(50, 380, 71, 380))

    frags.append(fitbox(75, 440, 530, 76,
                        "зміна правила податку\n"
                        "торкнулися: 3 компоненти · перезбирається: 4 з 5\n"
                        "10 із 12 файлів = 83% коду",
                        size=12.5, bold=True, fill=FILL, stroke=POS, sw=1.8))

    # ── ПРАВОРУЧ: за віссю зміни ──
    frags.append(fitbox(695, 130, 190, 52, "api\ncheckout.ts", size=12, bold=True, **REBLD))
    frags.append(fitbox(695, 242, 150, 52, "tax\n3 файли", size=12, bold=True, **EDIT))
    frags.append(fitbox(885, 242, 150, 52, "shipping\n3 файли", size=12, bold=True, **SHUT))
    frags.append(fitbox(1075, 242, 150, 52, "discount\n3 файли", size=12, bold=True, **SHUT))
    frags.append(fitbox(695, 354, 530, 52, "model — money.ts · order.ts (2 файли)",
                        size=12, bold=True, **SHUT))

    frags.append(arrow(770, 182, 770, 238))
    frags.append(arrow(830, 182, 956, 238))
    frags.append(arrow(860, 182, 1144, 238))
    frags.append(arrow(770, 294, 770, 350))
    frags.append(arrow(960, 294, 960, 350))
    frags.append(arrow(1150, 294, 1150, 350))
    frags.append(line(695, 156, 670, 156))
    frags.append(line(670, 156, 670, 380))
    frags.append(arrow(670, 380, 691, 380))

    frags.append(fitbox(695, 440, 530, 76,
                        "та сама зміна правила податку\n"
                        "торкнулися: 1 компонент · перезбирається: 2 з 5\n"
                        "4 із 12 файлів = 33% коду",
                        size=12.5, bold=True, fill=FILL, stroke=FIELD, sw=1.8))

    frags.append(fitbox(75, 556, 1150, 76,
                        "Перезбирається не те, що ти редагував, а транзитивне замикання вгору "
                        "по стрілках: усі, хто посередньо залежить від зміненого.\n"
                        "Звідси різниця 83% проти 33% коду на ту саму вимогу. "
                        "api спирається на все — тож він у радіусі в обох розкладках.",
                        size=12.5, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, 'rebuild-closure.svg'), W, H, *frags,
           title="Що перезбереться від зміни правила податку — замикання вгору по графу")


# ── Метрику компонентів легко обдурити, метрику коду — ні (вставка proj) ──────
def fig_metric_gaming():
    W, H = 1100, 540
    frags = []

    COLS = [(60, 240), (320, 210), (550, 250), (820, 230)]
    HEAD = dict(fill=FILL, stroke=MUTED, sw=1.4)
    PLAIN = dict(fill=BG, stroke="#c2c7cf", sw=1.4)
    GOOD = dict(fill="#f2faf5", stroke=FIELD, sw=1.8)
    BAD = dict(fill="#fdecea", stroke=POS, sw=2.4)

    def cell(col, y, s, size=13, **kw):
        x, w = COLS[col]
        return fitbox(x, y, w, 56, s, size=size, bold=True, **kw)

    heads = ["розкладка", "торкнулися\nкомпонентів",
             "перезбирається\nкомпонентів", "частка коду\nв перезбиранні"]
    for i, h in enumerate(heads):
        frags.append(cell(i, 70, h, size=12.5, **HEAD))

    rows = [
        (140, "за шаром",                ("3", PLAIN), ("4 з 5", PLAIN), ("83%", BAD)),
        (210, "за віссю зміни",          ("1", GOOD),  ("2 з 5", GOOD),  ("33%", GOOD)),
        (280, "усе в одному компоненті", ("1", GOOD),  ("1 з 1", GOOD),  ("100%", BAD)),
    ]
    for y, name, c1, c2, c3 in rows:
        frags.append(cell(0, y, name, **PLAIN))
        for i, (val, style) in enumerate((c1, c2, c3), start=1):
            frags.append(cell(i, y, val, **style))

    frags.append(fitbox(60, 380, 470, 90,
                        "Метрику можна обдурити:\n"
                        "зліпи все в один компонент —\n"
                        "і в перших двох стовпцях назавжди «1».",
                        size=12.5, bold=True, fill="#fdecea", stroke=POS, sw=1.8))
    frags.append(fitbox(570, 380, 470, 90,
                        "Третій стовпець не обдуриш:\n"
                        "у блобі кожна зміна перезбирає весь код.\n"
                        "Його й став метрикою.",
                        size=12.5, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.8))

    render(os.path.join(IMG, 'metric-gaming.svg'), W, H, *frags,
           title="Чому метрикою треба брати частку коду, а не кількість компонентів")


if __name__ == "__main__":
    fig_change_scatter()
    fig_tension_triangle()
    fig_notebook_timeline()
    fig_rep_switches_camp()
    fig_rebuild_closure()
    fig_metric_gaming()
    print("figures written to", IMG)
