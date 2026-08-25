# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PURPLE = "#8a5fb0"
GOLD   = "#b8860b"


# ── object: чотири механічні турботи навколо комірки ──────────────────────────
# Ідея: батарея — фізичне тіло; від комірки в центрі розходяться чотири турботи,
# кожна веде до конкретного механічного рішення.

def fig_object():
    W, H = 720, 360
    cx, cy = W / 2, 188
    p = []

    # центр — комірка
    cell = rect(cx - 52, cy - 42, 104, 84, fill="#eef8ef", stroke=FIELD, sw=2, rx=8)
    cap = rect(cx - 14, cy - 50, 28, 12, fill="#eef8ef", stroke=FIELD, sw=2, rx=3)
    p += [cell, cap, text(cx, cy + 4, "комірка", size=12, color=FIELD, bold=True)]

    cards = [
        (150, 96, "має вагу й об'єм", "тримати, не\nнавантажуючи виводи", NEG),
        (W - 150, 96, "надувається", "лишити місце\nна роздуття", POS),
        (150, H - 86, "проколюється,\nбоїться тиску", "інакше — пожежа", GOLD),
        (W - 150, H - 86, "потребує конектора", "полярність, струм,\nне закоротити", PURPLE),
    ]
    for gx, gy, head, sub, col in cards:
        b, bw, bh = textbox(gx, gy, head + "\n" + sub, size=11, bold=True,
                            color=col, fill=BG, stroke=col, sw=1.8, min_w=190)
        dirx = 1 if gx < cx else -1
        diry = 1 if gy < cy else -1
        ax = gx + dirx * bw / 2
        ay = gy + diry * bh / 2
        tx = cx - dirx * 56
        ty = cy - diry * 30
        p.append(line(ax, ay, tx, ty, color=MUTED, sw=1.5))
        p.append(b)

    p.append(text(cx, H - 18, "електрика — лише половина справи",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "object.svg"), W, H, *p,
           title="Батарея — це ще й фізичне тіло")


# ── holders: три форм-фактори і характер кріплення кожного ─────────────────────
# Ідея: форма комірки диктує спосіб тримати; під кожною формою — її головна
# пастка.

def fig_holders():
    W, H = 720, 320
    p = []
    cols = [W * 0.18, W * 0.5, W * 0.82]
    yc = 150

    # циліндрична
    p.append(rect(cols[0] - 22, yc - 60, 44, 120, fill=FILL, stroke=INK, sw=1.8, rx=14))
    p.append(rect(cols[0] - 9, yc - 70, 18, 12, fill=FILL, stroke=INK, sw=1.8, rx=3))
    # пакетна (м'який прямокутник з виводами)
    p.append(rect(cols[1] - 46, yc - 44, 92, 96, fill="#eef4ff", stroke=NEG, sw=1.8, rx=4))
    p.append(rect(cols[1] - 16, yc - 56, 12, 14, fill="#eef4ff", stroke=NEG, sw=1.5, rx=2))
    p.append(rect(cols[1] + 6, yc - 56, 12, 14, fill="#eef4ff", stroke=NEG, sw=1.5, rx=2))
    # монетна
    p.append(circle(cols[2], yc - 4, 40, fill="#fdf6e3", stroke=GOLD, sw=1.8))
    p.append(circle(cols[2], yc - 4, 24, fill=BG, stroke=GOLD, sw=1.2))

    heads = [(cols[0], "циліндрична", INK), (cols[1], "пакетна (LiPo)", NEG),
             (cols[2], "монетна", GOLD)]
    for x, lab, col in heads:
        p.append(text(x, 58, lab, size=13, color=col, bold=True))

    notes = [
        (cols[0], "пружинний тримач: гірший\nконтакт (росте Rвн); або\nприварені смужки — надійніше"),
        (cols[1], "м'яка, без корпусу: берегти\nвід проколу й тиску, не тягти\nза виводи, лишити роздуття"),
        (cols[2], "пружний контакт у гнізді;\nголовна пастка — переплутана\nполярність"),
    ]
    for x, lab in notes:
        p.append(mtext(x, yc + 86, lab, size=10, color=INK, lh=1.35))

    render(os.path.join(OUT, "holders.svg"), W, H, *p,
           title="Три форм-фактори — три способи тримати")


# ── connectors: три правила під'єднання ───────────────────────────────────────
# Ідея: три незалежні правила конектора, кожне з механізмом біди при порушенні.

def fig_connectors():
    W, H = 720, 300
    p = []
    cw = W / 3
    yhead = 78
    cards = [
        ("полярність", "ключований роз'єм —\nфізично не вставити\nнавпаки", NEG,
         "переполюсування\nгубить пристрій"),
        ("струм за піком", "добирати під ПІКОВИЙ\nструм, не середній", POS,
         "тонкий роз'єм гріється\nй просідає під піком"),
        ("не закоротити", "ізолювати виводи,\nфіксувати дроти", GOLD,
         "голий вивід об метал —\nкоротке, ризик пожежі"),
    ]
    for i, (head, body, col, bad) in enumerate(cards):
        cx = cw * (i + 0.5)
        p.append(text(cx, yhead, head, size=13, color=col, bold=True))
        b, bw, bh = textbox(cx, 150, body, size=11, bold=False, color=INK,
                            fill=BG, stroke=col, sw=1.8, min_w=cw - 40)
        p.append(b)
        p.append(mtext(cx, 224, bad, size=10, color=POS, lh=1.3))

    render(os.path.join(OUT, "connectors.svg"), W, H, *p,
           title="Три правила конектора (порушив — біда)")


# ── swelling: чому надувається і що робити ────────────────────────────────────
# Ідея: ліворуч причина (газ із розкладеного електроліту), праворуч — чіткий
# алгоритм дій із наголосом «не проколювати».

def fig_swelling():
    W, H = 720, 320
    p = []

    # ліворуч: надутий пакет + причина
    bx, by = 150, 150
    # «пухла» оболонка
    p.append('<path d="M%.0f,%.0f Q%.0f,%.0f %.0f,%.0f L%.0f,%.0f Q%.0f,%.0f %.0f,%.0f Z" '
             'fill="#fdecea" stroke="%s" stroke-width="2"/>'
             % (bx - 60, by - 44, bx, by - 78, bx + 60, by - 44,
                bx + 60, by + 44, bx, by + 78, bx - 60, by + 44, POS))
    p.append(text(bx, by + 4, "газ усередині", size=11, color=POS, bold=True))
    p.append(mtext(bx, by + 96, "електроліт розклався →\nвиділив горючий газ\n(перезаряд, перегрів, прокол,\nглибокий розряд, старість)",
                   size=10, color=INK, lh=1.3))
    p.append(text(bx, 70, "чому надувається", size=12, color=POS, bold=True))

    # праворуч: алгоритм
    ax = W * 0.66
    p.append(text(ax, 70, "що робити", size=12, color=FIELD, bold=True))
    steps = [
        ("1", "припинити заряд\nі використання", FIELD),
        ("2", "ізолювати у\nвогнетривкій ємності", FIELD),
        ("3", "НЕ проколювати,\nне тиснути, не «здувати»", POS),
        ("4", "здати на утилізацію", FIELD),
    ]
    sy = 104
    for num, lab, col in steps:
        p.append(circle(ax - 96, sy, 12, fill=col, stroke=col, sw=1))
        p.append(text(ax - 96, sy + 4, num, size=12, color=BG, bold=True))
        p.append(mtext(ax - 74, sy - (0 if "\n" not in lab else 4), lab,
                       size=10, color=(POS if col == POS else INK), anchor="start",
                       bold=(col == POS), lh=1.25))
        sy += 50

    render(os.path.join(OUT, "swelling.svg"), W, H, *p,
           title="Надутий LiPo: причина і чіткий алгоритм")


# ── failsafe: ланцюг відмови і як його розірвати ──────────────────────────────
# Ідея: горизонтальний ланцюг ескалації згори; знизу — чотири конструктивні
# розриви ланцюга.

def fig_failsafe():
    W, H = 740, 330
    p = []
    chain = [
        ("ушкодження /\nперегрів", GOLD),
        ("вихід газу\n(venting)", POS),
        ("тепловий\nрозгін", POS),
        ("займання,\nкаскад", PURPLE),
    ]
    n = len(chain)
    bw, bh = 132, 50
    gap = (W - 60 - n * bw) / (n - 1)
    x = 30
    yc = 92
    centers = []
    for i, (lab, col) in enumerate(chain):
        p.append(fitbox(x, yc - bh / 2, bw, bh, lab, size=11, bold=True,
                        color=col, fill=BG, stroke=col, sw=1.8))
        centers.append((x, x + bw))
        if i > 0:
            p.append(arrow(centers[i - 1][1], yc, x - 2, yc, color=INK, sw=1.8))
        x += bw + gap

    p.append(text(W / 2, 156, "завдання конструкції — розірвати ланцюг або локалізувати наслідки:",
                  size=11, color=INK, bold=True))

    guards = [
        ("шлях для газу", "вентиляція, не\nгерметичний короб", FIELD),
        ("розділяти комірки", "щоб розгін не\nпередався сусіднім", NEG),
        ("без горючого поруч", "матеріали, що не\nпідтримують горіння", GOLD),
        ("не затискати", "тиск на надуту\nкомірку — прискорювач", POS),
    ]
    gw = (W - 60) / 4
    for i, (head, sub, col) in enumerate(guards):
        gx = 30 + gw * (i + 0.5)
        p.append(rect(gx - 16, 178, 14, 14, fill=col, stroke=col, sw=0, rx=3))
        p.append(text(gx + 2, 190, head, size=11, color=col, anchor="start", bold=True))
        p.append(mtext(gx - 16, 214, sub, size=9, color=INK, anchor="start", lh=1.3))

    p.append(text(W / 2, H - 20, "відмова однієї комірки має лишитися локальним інцидентом, а не пожежею виробу",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "failsafe.svg"), W, H, *p,
           title="Поведінка при відмові: проєктувати на «безпечно згоріти»")


# ── storage: зберігання / транспорт / утилізація ──────────────────────────────
# Ідея: три фази життя поза пристроєм, у кожній — головне правило і головна біда.

def fig_storage():
    W, H = 720, 300
    p = []
    cw = W / 3
    cards = [
        ("зберігати", FIELD,
         "≈50% заряду, прохолодно,\nу вогнетривкій ємності",
         "подалі від металу:\nмонета чи ключ закоротить!"),
        ("перевозити", NEG,
         "низький заряд, у межах\nза ват-годинами",
         "авіа — суворі норми;\nпошкоджені везти не можна"),
        ("утилізувати", GOLD,
         "лише в пункти прийому\nбатарей",
         "ніколи в смітник:\nпожежа у відходах"),
    ]
    for i, (head, col, rule, bad) in enumerate(cards):
        cx = cw * (i + 0.5)
        p.append(text(cx, 74, head, size=14, color=col, bold=True))
        b, bw, bh = textbox(cx, 142, rule, size=11, bold=True, color=INK,
                            fill=BG, stroke=col, sw=1.8, min_w=cw - 36)
        p.append(b)
        p.append(mtext(cx, 218, bad, size=10, color=POS, lh=1.3))

    p.append(text(W / 2, H - 18, "заряджений літій носить енергію скрізь — і на полиці, і у валізі, і в смітті",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "storage.svg"), W, H, *p,
           title="Літій поза пристроєм: три фази, три правила")


if __name__ == "__main__":
    fig_object()
    fig_holders()
    fig_connectors()
    fig_swelling()
    fig_failsafe()
    fig_storage()
    print("OK: figures written to", OUT)
