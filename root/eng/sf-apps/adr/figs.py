# -*- coding: utf-8 -*-
"""Фігури теми «Запис архітектурного рішення (ADR)». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── adr: незаписане рішення vs записане як ADR ────────────────────────────────
# Ідея: ліворуч рішення замкнене в голові/Slack-нитці — три дії (перевірити,
# заперечити, успадкувати) недоступні. Праворуч те саме рішення як ADR — усі
# три відкриті. Різниця не в якості рішення, а у видимості.
def fig_invisible_vs_visible():
    W, H = 960, 480
    f = []

    f.append(text(240, 56, "Незаписане рішення", size=16, bold=True, color=NEG))
    f.append(text(720, 56, "Записане як ADR", size=16, bold=True, color=FIELD))

    # ліва панель: голова + Slack-нитка, замкнені хмаркою
    b, bw, bh = textbox(240, 150, "рішення\nу голові інженера\nта в Slack-нитці",
                        size=13, fill="#fdecea", stroke=NEG, sw=2, pad=14)
    f.append(b)
    for i, s in enumerate(["перевірити", "заперечити", "успадкувати"]):
        cy = 260 + i * 62
        f.append(minus(90, cy))
        f.append(text(120, cy + 5, s + " — недоступно", size=13, color=NEG, anchor="start"))
        f.append(line(240, 150 + bh / 2, 240, cy - 18, color=NEG, sw=1.2, dash="4,4"))

    f.append(line(480, 90, 480, 440, color=MUTED, sw=1.2, dash="6,5"))

    # права панель: той самий запис, тепер відкритий
    b, bw, bh = textbox(720, 150, "те саме рішення,\nзаписане як ADR",
                        size=13, fill="#d4edda", stroke=FIELD, sw=2, pad=14)
    f.append(b)
    for i, s in enumerate(["перевірити", "заперечити", "успадкувати"]):
        cy = 260 + i * 62
        f.append(plus(870, cy))
        f.append(text(840, cy + 5, s + " — можна", size=13, color=FIELD, anchor="end"))
        f.append(line(720, 150 + bh / 2, 720, cy - 18, color=FIELD, sw=1.2, dash="4,4"))

    render(out("invisible-vs-visible.svg"), W, H, *f,
           title="Різниця не в якості рішення, а в його видимості")


# ── adr: позиції — драйвери породжують варіанти, програші підписують ─────────
# Ідея: драйвери тиснуть, з них виростають кілька позицій; одну обирають
# (обведено зелено), решту відкидають з явним підписом причини. Через рік
# наступний інженер натикається на вже підписаний програш.
def fig_positions():
    W, H = 960, 520
    f = []

    b, bw, bh = textbox(480, 60, "драйвери (сили в грі)", size=14, bold=True,
                        fill="#eef2ff", stroke=MUTED, sw=1.8, pad=12)
    f.append(b)

    xs = [160, 480, 800]
    for x in xs:
        f.append(arrow(480, 60 + bh / 2, x, 150, color=MUTED, sw=1.5))

    rows = [
        (160, "черга подій", True,
         "розчеплює служби,\nпереживає падіння складу"),
        (480, "синхронний виклик", False,
         "жорстке зчеплення —\nвалить оформлення каскадом"),
        (800, "спільна таблиця", False,
         "приховане зчеплення схемою —\nпереоблік блокує читання"),
    ]
    for x, name, won, why in rows:
        col = FIELD if won else NEG
        fillc = "#d4edda" if won else "#fdecea"
        f.append(fitbox(x - 110, 150, 220, 46, name, size=13, bold=True,
                        fill=fillc, stroke=col, sw=2.2))
        b, bw, bh = textbox(x, 260, why, size=12, fill=fillc, stroke=col, sw=1.6, pad=10)
        f.append(b)
        f.append(line(x, 196, x, 260 - bh / 2, color=col, sw=1.5))
        tag = "ОБРАНО" if won else "ВІДКИНУТО — причина підписана"
        f.append(text(x, 260 + bh / 2 + 22, tag, size=12, bold=True, color=col))

    f.append(line(60, 350, 900, 350, color=MUTED, sw=1.2, dash="6,5"))
    b, bw, bh = textbox(480, 410, "через рік: наступний інженер пропонує «синхронний виклик»",
                        size=13, fill=FILL, stroke=LINE, sw=1.6, pad=12)
    f.append(b)
    f.append(text(480, 465, "запис відповідає одразу — причиною програшу, а не переказом чиєїсь пам'яті",
                  size=12, color=MUTED))

    render(out("positions.svg"), W, H, *f,
           title="Несуча цінність запису — не обраний варіант, а підписані програші")


# ── adr: життєвий цикл одного запису ──────────────────────────────────────────
# Ідея: запропоновано → рев'ю → ухвалено/відхилено; ухвалене згодом може
# застаріти чи бути заміненим новим записом. «Запропоновано» — запрошення
# заперечити, не наказ.
def fig_lifecycle():
    W, H = 960, 460
    f = []

    def state(x, y, s, col, fillc):
        b, bw, bh = textbox(x, y, s, size=13, bold=True, fill=fillc, stroke=col,
                            sw=2.2, pad=12)
        f.append(b)
        return bw, bh

    x0, y0 = 150, 130
    bw0, bh0 = state(x0, y0, "запропоновано", "#e0a800", "#fff9e6")
    f.append(text(x0, y0 + bh0 / 2 + 22, "запрошення заперечити,\nне наказ", size=11, color=MUTED))

    x1, y1 = 480, 130
    f.append(arrow(x0 + bw0 / 2, y0, x1 - 90, y1, color="#e0a800", sw=1.8))
    f.append(text((x0 + x1) / 2, 100, "рев'ю", size=12, color=MUTED))
    bw1, bh1 = state(x1, y1, "ухвалено", FIELD, "#d4edda")

    x2, y2 = 800, 130
    f.append(arrow(x0 + bw0 / 2 + 20, y0 + 30, x2 - 90, y2 - 10, color=NEG, sw=1.8))
    f.append(text((x0 + x2) / 2 + 40, 200, "не переконало", size=12, color=NEG))
    bw2, bh2 = state(x2, y2, "відхилено", NEG, "#fdecea")
    f.append(text(x2, y2 + bh2 / 2 + 22, "лишається —\nвідхилене теж знання", size=11, color=MUTED))

    x3, y3 = 350, 330
    f.append(arrow(x1, y1 + bh1 / 2, x3 + 90, y3 - 20, color=MUTED, sw=1.8))
    bw3, bh3 = state(x3, y3, "застаріло", MUTED, FILL)

    x4, y4 = 720, 330
    f.append(arrow(x1 + 30, y1 + bh1 / 2 + 10, x4 - 100, y4 - 25, color=MUTED, sw=1.8))
    f.append(text((x1 + x4) / 2 + 60, 260, "нове рішення\nлягає поверх старого", size=11, color=MUTED))
    bw4, bh4 = state(x4, y4, "замінено ADR-00xx", MUTED, FILL)

    f.append(text(W / 2, 420,
                  "причина минулого рішення не стирається ніколи, навіть коли саме рішення вже змінили",
                  size=13, bold=True, color=INK))

    render(out("lifecycle.svg"), W, H, *f,
           title="Статус робить запис живим у часі")


# ── proj-decision-matrix: скільки зарубок незгоди витримує відповідь ─────────
def fig_notches():
    W, H = 920, 600
    X0, X1 = 130, 850          # 0..4 зарубки
    Y0, Y1 = 110, 450          # запас +9..-6
    PX = (X1 - X0) / 4.0       # 180 px на зарубку
    PY = (Y1 - Y0) / 15.0      # 22.667 px на бал запасу
    X = lambda t: X0 + PX * t
    Y = lambda m: Y0 + (9 - m) * PY

    f = []
    # смуга «незгода на одну зарубку»
    f.append(rect(X(0), Y0, PX, Y1 - Y0, fill="#fdecea", stroke="none", sw=0, rx=0))
    f.append(text(X(0.5), 436, "незгода на одну зарубку", size=12, color=MUTED))

    # осі
    f.append(line(X0, Y0, X0, Y1, color=LINE, sw=1.5))
    f.append(line(X0, Y1, X1, Y1, color=LINE, sw=1.5))
    f.append(text(X0, 100, "запас переможця (зважені бали)", size=12,
                  color=MUTED, anchor="start"))
    for m in (8, 4, 0, -4):
        f.append(text(X0 - 8, Y(m) + 4, ("%+d" % m) if m else "0", size=12,
                      color=MUTED, anchor="end"))
    for t in range(5):
        f.append(text(X(t), 470, str(t), size=12, color=MUTED))
    f.append(text((X0 + X1) / 2, 496, "зарубок незгоди у вагах  (1 зарубка = ×1)",
                  size=13, color=MUTED))

    # лінія нічиєї
    f.append(line(X0, Y(0), X1, Y(0), color=INK, sw=2, dash="7,4"))
    f.append(text(X1 + 10, Y(0) + 4, "нічия", size=12, color=INK,
                  anchor="start", bold=True))

    # запас = 8 − 3u : совається ОДНА вага (проста експлуатація, d = −3)
    f.append(line(X(0), Y(8), X(3.5), Y(8 - 3 * 3.5), color=NEG, sw=2.6))
    f.append(circle(X(8 / 3.0), Y(0), 6, fill=BG, stroke=NEG, sw=2.6))
    f.append(text(600, 340, "2.67 зарубки", size=13, color=NEG,
                  anchor="end", bold=True))
    b, bw, bh = textbox(640, 200, "совання однієї ваги (OAT)", size=12,
                        fill="#eaf0fd", stroke=NEG, color=NEG)
    f.append(b)
    f.append(line(640 - bw / 2, 205, 412, 232, color=NEG, sw=1.2))

    # запас = 8 − 11t : усі чотири ваги на t зарубок в найгіршу сторону
    f.append(line(X(0), Y(8), X(1.25), Y(8 - 11 * 1.25), color=POS, sw=3.2))
    f.append(circle(X(8 / 11.0), Y(0), 6, fill=BG, stroke=POS, sw=3))
    f.append(text(250, 340, "0.73 зарубки", size=13, color=POS,
                  anchor="end", bold=True))
    b, bw, bh = textbox(470, 425, "узгоджений зсув\nусіх чотирьох ваг", size=12,
                        fill="#fdecea", stroke=POS, color=POS, bold=True)
    f.append(b)
    f.append(line(470 - bw / 2, 428, 358, 442, color=POS, sw=1.2))

    render(out("notches.svg"), W, H, *f,
           title="Скільки незгоди витримує «40 проти 32»")


# ── proj-decision-matrix: вимога як критерій vs вимога як ворота ─────────────
def fig_gate():
    W, H = 900, 600
    f = []

    # ── Панель А: вимогу можна викупити ──────────────────────────────────
    f.append(text(450, 76, "Вимога сидить критерієм — її можна викупити балами",
                  size=15, bold=True, color=POS))
    cells = [("зчеплення ×3", "2", FILL, LINE, 1.5, INK),
             ("затримка ×2", "5", "#eaf7ef", FIELD, 1.5, FIELD),
             ("експлуатація ×2", "5", "#eaf7ef", FIELD, 1.5, FIELD),
             ("стійкість ×3", "2", "#fdecea", POS, 2.5, POS)]
    f.append(text(172, 152, "синхр. виклик", size=13, anchor="end", bold=True))
    for i, (cap, val, fill, stroke, sw, tc) in enumerate(cells):
        x, cx = 180 + 150 * i, 255 + 150 * i
        f.append(text(cx, 110, cap, size=11, color=MUTED))
        f.append(rect(x, 120, 150, 54, fill=fill, stroke=stroke, sw=sw))
        f.append(text(cx, 156, val, size=24, bold=True, color=tc))
    f.append(text(480, 192, "тут густо балів", size=11, color=FIELD, bold=True))
    f.append(text(705, 192, "вимогу ПРОВАЛЕНО", size=11, color=POS, bold=True))
    f.append(text(450, 222, "5·×2 + 5·×2 = 20 балів за швидкість і зручність…", size=13))
    f.append(text(450, 246, "…купують провалену вимогу: разом 32, програш лише 8 — «майже переміг»",
                  size=13))

    f.append(line(60, 285, 840, 285, color=MUTED, sw=1.2, dash="6,5"))

    # ── Панель Б: вимога стоїть ворітьми ─────────────────────────────────
    f.append(text(450, 330, "Вимога стоїть ворітьми — викупити неможливо",
                  size=15, bold=True, color=FIELD))
    b, bw, bh = textbox(450, 382, "оформлення живе, коли склад недоступний?",
                        size=13, fill="#eef4ff", stroke=NEG, sw=2, bold=True)
    f.append(b)
    f.append(arrow(380, 398, 215, 444, color=POS))
    f.append(arrow(450, 398, 450, 444, color=FIELD))
    f.append(arrow(520, 398, 685, 444, color=FIELD))
    f.append(text(270, 415, "НІ", size=12, color=POS, bold=True))
    f.append(text(478, 425, "ТАК", size=12, color=FIELD, bold=True))
    f.append(text(630, 415, "ТАК", size=12, color=FIELD, bold=True))
    for cx, s, fill, stroke in [(200, "синхр. виклик\nЗНЯТО ВИМОГОЮ", "#fdecea", POS),
                                (450, "черга подій\nу суму", "#eaf7ef", FIELD),
                                (700, "спільна табл.\nу суму", "#eaf7ef", FIELD)]:
        b, bw, bh = textbox(cx, 478, s, size=12, fill=fill, stroke=stroke, sw=2)
        f.append(b)
    f.append(text(450, 545, "сума лише між тими, хто пройшов: 40 проти 25 → витримує 1.5 зарубки",
                  size=13, bold=True))
    f.append(text(450, 572, "синхр. виклик не програв за балами — він вибув за вимогою",
                  size=12, color=MUTED))

    render(out("requirement-gate.svg"), W, H, *f)


# ── hist-adr-origin: два корені запису рішення ───────────────────────────────
# Ідея: ADR не має одного винахідника. Ліва смуга — дослідницька лінія (Ріттель →
# design rationale → «архітектура це рішення» → Тайрі й Акерман). Права — лінія
# щоденної практики: від патерна Александера до Найгарда. Сходяться аж у MADR.
# Смуги свідомо рознесені (між ними ~190 px порожнечі), щоб довга стрілка
# Александер → Найгард ішла порожнім полем і нічого не перетинала.
def fig_genealogy():
    W, H = 960, 900
    RX, PX = 290, 700          # центри смуг: дослідження / практика
    f = []

    f.append(text(RX, 62, "дослідження рішень", size=14, color=NEG, bold=True))
    f.append(text(PX, 62, "щоденна практика", size=14, color="#b8860b", bold=True))

    # ── ліва смуга: дослідницька лінія ──
    research = [
        (120, "1968–70 · IBIS\nКунц і Ріттель:\nпитання · позиції · аргументи"),
        (215, "1986 · Парнас і Клементс\nраціонального процесу нема —\nале його варто вдавати"),
        (310, "1988–91 · gIBIS · QOC · DRL\nнотації є, а записів нема:\nписьмо надто дороге"),
        (405, "1992 · Перрі й Вулф\nархітектура = елементи +\nформа + ОБҐРУНТУВАННЯ"),
        (500, "2004–05 · Крухтен, Янсен і Бош\nрішення — першокласні;\n«випаровування знання»"),
    ]
    for cy, s in research:
        b, bw, bh = textbox(RX, cy, s, size=12, fill="#eef2ff", stroke=NEG, sw=1.8, pad=11)
        f.append(b)
    # Тайрі й Акерман — вузол-міст: тут народився розділ «позиції»
    b, bw, bh = textbox(RX, 600, "2005 · Тайрі й Акерман\n14 полів, розділ «позиції»\n(народжений за столом рев'ю)",
                        size=12, fill="#d4edda", stroke=FIELD, sw=2.4, pad=11)
    f.append(b)
    # стрілки лише в проміжках між рамками — крізь текст не йде жодна
    for y1, y2 in [(157, 178), (252, 273), (347, 368), (442, 463), (537, 563)]:
        f.append(arrow(RX, y1, RX, y2, color=NEG, sw=1.8))

    # ── права смуга: лінія практики ──
    for cy, s, sw in [(215, "1977 · Александер\nпатерн: контекст,\nсили, рішення", 1.8),
                      (600, "2011 · Найгард\n5 заголовків, 1–2 сторінки,\nmarkdown у репозиторії", 2.4),
                      (700, "2016–17 · adr-tools,\nRadar → «adopt»", 1.8)]:
        b, bw, bh = textbox(PX, cy, s, size=12, fill="#fff9e6", stroke="#e0a800", sw=sw, pad=11)
        f.append(b)
    # довга стрілка порожнім полем смуги; підпис збоку, лінії не торкається
    f.append(arrow(PX, 252, PX, 563, color="#e0a800", sw=1.8))
    f.append(mtext(PX + 24, 386, ["форма патерна:", "контекст і «сили»", "через 34 роки"],
                   size=11, color=MUTED, anchor="start"))
    f.append(arrow(PX, 636, PX, 671, color="#e0a800", sw=1.8))

    # ── сходження: MADR ──
    b, bw, bh = textbox(490, 830, "2017–18 · MADR\nпрограші повертаються:\nConsidered Options",
                        size=12, fill="#d4edda", stroke=FIELD, sw=2.4, pad=11)
    f.append(b)
    f.append(arrow(330, 636, 452, 795, color=FIELD, sw=2.0))
    f.append(arrow(662, 729, 545, 795, color=FIELD, sw=2.0))

    render(out("adr-genealogy.svg"), W, H, *f,
           title="У запису рішення два корені — і сходяться вони пізно")


# ── hist-adr-origin: чи несе шаблон перелік відкинутих варіантів ──────────────
# Ідея: найцінніший розділ не накопичувався рівно — він ВИПАВ у найпопулярнішій
# формі й був свідомо повернений. Один рядок — один шаблон.
def fig_positions_thread():
    W, H = 960, 430
    f = []

    rows = [
        ("IBIS · 1970", True,
         "позиції (positions) — одна з трьох\nнесучих частин моделі Ріттеля"),
        ("Тайрі й Акерман · 2005", True,
         "Positions: «щоб на рев'ю не почути\n„а ви думали про…?“»"),
        ("Найгард · 2011", False,
         "контекст · рішення · статус · наслідки —\nпереліку варіантів у формі немає"),
        ("Y-твердження · 2013", True,
         "«…і відкинули <інші варіанти>» —\nпрямо в тілі речення"),
        ("MADR · 2017", True,
         "Considered Options + «добре, бо…» /\n«погано, бо…» до кожного"),
    ]

    y = 95
    for name, has, desc in rows:
        col = FIELD if has else POS
        fillc = "#d4edda" if has else "#fdecea"
        f.append(fitbox(40, y - 24, 250, 48, name, size=13, bold=True,
                        fill="#eef1f4", stroke=MUTED, sw=1.8))
        b, bw, bh = textbox(345, y, "є" if has else "нема", size=13, bold=True,
                            fill=fillc, stroke=col, sw=2.2, pad=10, min_w=76)
        f.append(b)
        f.append(fitbox(410, y - 24, 520, 48, desc, size=12,
                        fill=fillc, stroke=col, sw=1.8))
        y += 65

    f.append(text(W / 2, 400,
                  "MADR повернув програші свідомо: автори закинули формі Найгарда, що «відкинуті варіанти не показані».",
                  size=12, color=INK, bold=True))

    render(out("positions-thread.svg"), W, H, *f,
           title="Доля розділу про відкинуті варіанти: не накопичення, а розрив")


if __name__ == "__main__":
    fig_invisible_vs_visible()
    fig_positions()
    fig_lifecycle()
    fig_notches()
    fig_gate()
    fig_genealogy()
    fig_positions_thread()
    print("готово:", ", ".join(sorted(os.listdir(IMG))))
