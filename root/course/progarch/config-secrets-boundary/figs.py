# -*- coding: utf-8 -*-
"""Фігури до кроку «Конфіг проти секретів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER = "#f0a02e"


def elbow(pts, color=LINE, sw=2.2, dash=None, marker=True):
    """Ламана-стрілка через список точок (елбоу). marker — стрілка на кінці."""
    d = "M %.1f %.1f" % pts[0] + "".join(" L %.1f %.1f" % p for p in pts[1:])
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    mk = ' marker-end="url(#arrow)"' if marker else ''
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s%s/>'
            % (d, color, sw, da, mk))


def vtext(x, y, s, size=12, color=MUTED):
    """Вертикальний підпис (читається знизу вгору)."""
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">%s</text>'
            % (x, y, FONT, size, color, x, y, esc(s)))


def fig_two_doors():
    """Та сама форма — різні двері: конфіг оборотний (петля), секрет ні (один бік)."""
    W, H = 1000, 470
    frags = [line(500, 46, 500, 442, color=MUTED, sw=1, dash="5,7")]

    # ── ЛІВОРУЧ: конфіг — двері в обидва боки ──
    frags.append(text(250, 66, "Конфіг", size=18, bold=True))
    frags.append(text(250, 90, "двері в обидва боки", size=13, color=FIELD))
    bA, wA, _ = textbox(250, 150, "хибне значення", size=14)
    frags.append(bA)
    frags.append(arrow(250, 172, 250, 262, color=NEG, sw=2.2))
    bB, wB, _ = textbox(250, 292, "виправив і\nперезапустив", size=14)
    frags.append(bB)
    leftA, leftB = 250 - wA / 2, 250 - wB / 2
    frags.append(elbow([(leftB, 292), (145, 292), (145, 150), (leftA, 150)],
                       color=FIELD, sw=2.4))
    frags.append(mtext(135, 208, ["стан", "вертається"], size=12, color=FIELD, anchor="end"))
    frags.append(text(250, 366, "оборотно — відкотив і забув", size=12, color=MUTED))

    # ── ПРАВОРУЧ: секрет — двері в один бік ──
    frags.append(text(750, 66, "Секрет", size=18, bold=True))
    frags.append(text(750, 90, "двері в один бік", size=13, color=POS))
    aA, wA2, _ = textbox(750, 150, "секрет витік", size=14)
    frags.append(aA)
    frags.append(arrow(750, 172, 750, 262, color=POS, sw=2.2))
    aB, wB2, _ = textbox(750, 292, "хтось\nпобачив", size=14, fill="#fdecea", stroke=POS)
    frags.append(aB)
    rightA2, rightB2 = 750 + wA2 / 2, 750 + wB2 / 2
    # заблокований шлях назад — пунктир без стрілки + червоний хрест
    frags.append(elbow([(rightB2, 292), (858, 292), (858, 150), (rightA2, 150)],
                       color=MUTED, sw=1.8, dash="5,6", marker=False))
    frags.append(line(850, 210, 866, 232, color=POS, sw=2.6))
    frags.append(line(866, 210, 850, 232, color=POS, sw=2.6))
    frags.append(mtext(874, 214, ["назад", "ніяк"], size=12, color=POS, anchor="start"))
    # єдиний рух — уперед, до нового секрета
    frags.append(arrow(750, 322, 750, 374, color=POS, sw=2.2))
    frags.append(mtext(660, 348, ["лише", "нове"], size=11, color=MUTED, anchor="end"))
    cC, _, _ = textbox(750, 406, "новий секрет", size=14, fill="#eef7f0", stroke=FIELD)
    frags.append(cC)
    frags.append(text(750, 450, "незворотно — лише вперед, до нового", size=12, color=MUTED))

    render(os.path.join(IMG, "two-doors.svg"), W, H, *frags,
           title="Та сама форма — різні двері")


def fig_blast_radius():
    """Драбина радіуса ураження: смуги ростуть, колір густішає зелений→червоний."""
    W, H = 1000, 500
    frags = []
    rows = [
        ("рівень логів, хост", "конфіг — витік майже нічого не важить", 120, FIELD),
        ("токен на читання",   "доступ до одного чужого API",           250, "#7cb342"),
        ("пароль до бази",     "усі дані застосунку",                   400, AMBER),
        ("ключ TLS / підпису", "видати себе за систему",                540, "#e2622b"),
        ("майстер-ключ",       "відмикає всі інші секрети",             640, POS),
    ]
    x0, barh, y0, step = 340, 44, 92, 84
    frags.append(vtext(40, 282, "радіус росте вниз", size=12, color=MUTED))
    for i, (label, exposes, wbar, color) in enumerate(rows):
        yt = y0 + i * step
        frags.append(text(x0 + 10, yt - 9, exposes, size=12, color=MUTED, anchor="start"))
        frags.append(text(x0 - 15, yt + 28, label, size=13, color=INK, bold=True, anchor="end"))
        frags.append(rect(x0, yt, wbar, barh, fill=color, stroke=INK, sw=1, rx=5))
    frags.append(text(500, 492,
                      "Спільний старт зліва; захищай кожен секрет пропорційно тому, що за ним стоїть.",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "blast-radius.svg"), W, H, *frags,
           title="Радіус ураження: довжина смуги — скільки впаде за одним значенням")


def fig_reference_not_value():
    """Три ланки: у коді — посилання; значення живе у сховищі; в процес — на старті."""
    W, H = 1000, 320
    frags = []
    by, bh = 78, 152

    # Box1 — репозиторій / образ
    frags.append(rect(60, by, 240, bh, fill=FILL))
    frags.append(text(180, 102, "Репозиторій / образ", size=13, bold=True))
    frags.append(text(72, 132, "host = prod-db.internal", size=12, color=INK, anchor="start"))
    frags.append(text(84, 150, "→ звичайне значення", size=11, color=FIELD, anchor="start"))
    frags.append(text(72, 180, "pass = secret://dh/db", size=12, color=INK, anchor="start"))
    frags.append(text(84, 198, "→ лише посилання", size=11, color=MUTED, anchor="start"))

    # Box2 — сховище секретів
    frags.append(rect(380, by, 240, bh, fill=FILL))
    frags.append(text(500, 102, "Сховище секретів", size=13, bold=True))
    frags.append(text(392, 140, "dh/db/password", size=12, color=INK, anchor="start"))
    frags.append(text(392, 162, "= 7Kd9·x2Lm4…", size=12, color=POS, anchor="start"))
    frags.append(text(392, 196, "поза кодом і git", size=11, color=MUTED, anchor="start"))

    # Box3 — пам'ять процесу
    frags.append(rect(700, by, 240, bh, fill="#eef7f0", stroke=FIELD))
    frags.append(text(820, 102, "Пам'ять процесу", size=13, bold=True))
    frags.append(text(712, 140, "host = prod-db.internal", size=12, color=INK, anchor="start"))
    frags.append(text(712, 162, "pass = ●●●●●●", size=12, color=INK, anchor="start"))
    frags.append(text(712, 196, "лише в пам'яті,", size=11, color=MUTED, anchor="start"))
    frags.append(text(712, 214, "лише на старті", size=11, color=MUTED, anchor="start"))

    # стрілки: посилання (repo→store), значення (store→memory)
    frags.append(arrow(300, 150, 380, 150, color=NEG, sw=2.2))
    frags.append(text(340, 138, "посилання", size=11, color=MUTED))
    frags.append(text(340, 168, "за іменем", size=10, color=MUTED))
    frags.append(arrow(620, 150, 700, 150, color=INK, sw=2.2))
    frags.append(text(660, 138, "значення", size=11, color=MUTED))
    frags.append(text(660, 168, "на старті", size=10, color=MUTED))

    frags.append(text(500, 262, "У git та образі — тільки посилання, не саме значення.",
                      size=12, color=MUTED))
    frags.append(text(500, 284,
                      "При ротації сховище видає нове значення — процес перечитує без нової збірки.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "reference-not-value.svg"), W, H, *frags,
           title="Секрет: у коді — посилання; значення — лише в пам'яті на старті")


def fig_snapshot_swap():
    """Ротація = атомна підміна знімка: цілісний читач переживає її, торн-читач — ні."""
    W, H = 1040, 560
    sx = 560          # мить підміни
    ty = 214          # вісь часу
    frags = []

    # тригер → підміна
    tb, _, _ = textbox(sx, 92, "SIGHUP / вийшов TTL\n→ resolve() будує знімок B", size=12,
                       fill=BG, stroke=MUTED)
    frags.append(tb)
    frags.append(arrow(sx, 118, sx, 150, color=MUTED, sw=1.8))
    frags.append(line(sx, 150, sx, 512, color=POS, sw=2, dash="4,6"))

    # вісь часу
    frags.append(line(120, ty, 930, ty, color=MUTED, sw=1.4))
    frags.append(text(922, ty + 30, "час →", size=12, color=MUTED, anchor="end"))

    # смуга A (ліворуч) / смуга B (праворуч)
    frags.append(rect(150, ty - 28, (sx - 12) - 150, 56, fill="#eef7f0", stroke=FIELD, sw=1.5))
    frags.append(text((150 + sx - 12) / 2, ty - 4, "поточний → знімок A", size=13, bold=True))
    frags.append(text((150 + sx - 12) / 2, ty + 18, "pass = ●●●  (v1)", size=12, color=MUTED))
    frags.append(rect(sx + 12, ty - 28, 910 - (sx + 12), 56, fill=FILL, stroke=NEG, sw=1.5))
    frags.append(text((sx + 12 + 910) / 2, ty - 4, "поточний → знімок B", size=13, bold=True))
    frags.append(text((sx + 12 + 910) / 2, ty + 18, "pass = ●●●  (v2)", size=12, color=MUTED))

    # підпис підміни + fail-static
    frags.append(text(sx + 14, 300, "атомна підміна", size=12, color=POS, bold=True, anchor="start"))
    frags.append(text(sx + 14, 318, "одного посилання", size=11, color=POS, anchor="start"))
    frags.append(text(sx - 14, 300, "fail-static:", size=11, color=MUTED, anchor="end"))
    frags.append(text(sx - 14, 316, "збій → лишається A", size=11, color=MUTED, anchor="end"))

    # R1 — цілісний читач
    y1 = 384
    frags.append(text(140, y1 - 30, "R1: знімок = поточний()  ОДИН раз", size=12, bold=True, anchor="start"))
    frags.append(rect(360, y1 - 16, 400, 32, fill="#eef7f0", stroke=FIELD, sw=1.5))
    frags.append(text(560, y1 + 5, "тримає A на весь запит", size=12, color=INK))
    frags.append(circle(400, y1, 4.5, fill=FIELD, stroke=FIELD))
    frags.append(circle(720, y1, 4.5, fill=FIELD, stroke=FIELD))
    rb, _, _ = textbox(858, y1, "A.host + A.pass\nузгоджено", size=12, fill="#eef7f0", stroke=FIELD)
    frags.append(rb)

    # R2 — торн-читач (читає поле-за-полем через await)
    y2 = 484
    frags.append(text(140, y2 - 30, "R2: читає поле-за-полем через await", size=12, bold=True, anchor="start"))
    frags.append(line(470, y2, 650, y2, color=MUTED, sw=1.6, dash="3,5"))
    frags.append(circle(470, y2, 4.5, fill=FIELD, stroke=FIELD))
    frags.append(text(470, y2 - 12, ".host → з A", size=11, color=MUTED))
    frags.append(circle(650, y2, 4.5, fill=NEG, stroke=NEG))
    frags.append(text(650, y2 - 12, ".pass → з B", size=11, color=MUTED))
    frags.append(text(560, y2 + 20, "await перетнув підміну", size=10, color=MUTED))
    rb2, _, _ = textbox(858, y2, "A.host + B.pass\nрозʼїхалось", size=12, fill="#fdecea", stroke=POS)
    frags.append(rb2)

    render(os.path.join(IMG, "snapshot-swap.svg"), W, H, *frags,
           title="Ротація = підміна знімка: цілісний читач переживає її, торн-читач ні")


def fig_redaction_wall():
    """Secret: типові виходи впираються у стіну й дають ‹secret›; значення — лише через expose()."""
    W, H = 1020, 470
    wx = 430          # стіна
    frags = []

    # сховок значення (ліворуч)
    frags.append(rect(110, 150, 240, 130, fill="#eef7f0", stroke=FIELD, sw=1.6))
    frags.append(text(230, 182, "Secret", size=15, bold=True))
    frags.append(text(230, 210, "#value = 7Kd9·x2Lm4…", size=12, color=INK))
    frags.append(text(230, 234, "лише в памʼяті процесу", size=11, color=MUTED))

    # стіна
    frags.append(text(wx, 92, "стіна редакції", size=13, bold=True, color=POS))
    frags.append(line(wx, 110, wx, 330, color=INK, sw=3))

    # типові виходи (праворуч) → стрілка до стіни → ‹secret›
    paths = [
        ("рядок / шаблон", "String(s) · f\"{s}\"", 138),
        ("JSON", "stringify · dumps", 206),
        ("консоль / inspect", "console.log · repr", 274),
        ("логер", "обʼєкт у полі запису", 342),
    ]
    for title, sub, y in paths:
        pb, pw, _ = textbox(800, y, title + "\n" + sub, size=11, fill=FILL, stroke=MUTED)
        frags.append(pb)
        frags.append(arrow(800 - pw / 2, y, wx + 4, y, color=MUTED, sw=1.7))
        frags.append(text(wx - 8, y + 4, "‹secret›", size=12, color=POS, bold=True, anchor="end"))

    # навмисні двері: expose() → справжнє значення (вниз)
    frags.append(arrow(230, 280, 230, 372, color=POS, sw=2))
    frags.append(text(248, 330, "expose() / get_secret_value()", size=12, color=POS, bold=True, anchor="start"))
    frags.append(text(248, 350, "єдиний навмисний вихід — лічені місця", size=11, color=MUTED, anchor="start"))
    rb, _, _ = textbox(230, 404, "справжнє значення", size=13, fill="#fdecea", stroke=POS)
    frags.append(rb)

    render(os.path.join(IMG, "redaction-wall.svg"), W, H, *frags,
           title="Один сховок, багато виходів: за замовчуванням ‹secret›, значення — лише через expose()")


def fig_secrets_arms_race():
    """Часова смуга перегонів: виявити ПІСЛЯ → відкликати ШВИДКО → не пустити ДО."""
    W, H = 1100, 470
    frags = []
    ay = 225
    frags.append(arrow(66, ay, 1024, ay, color=MUTED, sw=2.2))
    frags.append(text(1030, ay + 5, "час", size=12, color=MUTED, anchor="start"))

    nodes = [
        (180, "2015", POS,   "#fdecea", "above",
         "боти на коміт-потоці\n2375 $ за ніч —\nмайнінг коштом жертви"),
        (430, "2016", FIELD, FILL, "below",
         "truffleHog · Дилан Ейрі\nсканер історії\nза ентропією"),
        (690, "2018", FIELD, "#eef7f0", "above",
         "gitleaks · Зак Райс\n+ сканування токенів GitHub\nпостачальник гасить ключ"),
        (920, "2023", FIELD, "#eef7f0", "below",
         "захист пуша\nблок ДО коміту"),
    ]
    for x, year, ring, boxfill, side, label in nodes:
        if side == "above":
            cy = 112
            box, bw, bh = textbox(x, cy, label, size=13, fill=boxfill, stroke=ring, sw=1.6)
            frags.append(line(x, ay - 26, x, cy + bh / 2, color=MUTED, sw=1.4))
            frags.append(box)
        else:
            cy = 348
            box, bw, bh = textbox(x, cy, label, size=13, fill=boxfill, stroke=ring, sw=1.6)
            frags.append(line(x, ay + 26, x, cy - bh / 2, color=MUTED, sw=1.4))
            frags.append(box)
        frags.append(circle(x, ay, 26, fill=BG, stroke=ring, sw=2.6))
        frags.append(text(x, ay + 5, year, size=15, color=INK, bold=True))

    py = 438
    frags.append(text(230, py, "виявити ПІСЛЯ факту", size=13, color=MUTED))
    frags.append(arrow(360, py - 4, 452, py - 4, color=MUTED, sw=1.6))
    frags.append(text(585, py, "відкликати ШВИДКО", size=13, color=INK))
    frags.append(arrow(710, py - 4, 802, py - 4, color=MUTED, sw=1.6))
    frags.append(text(905, py, "не пустити ДО", size=13, color=FIELD, bold=True))

    render(os.path.join(IMG, "secrets-arms-race.svg"), W, H, *frags,
           title="Перегони оборони: лінію захисту відсували назад у часі, ближче до джерела")


def fig_immutable_history():
    """git rm не стирає: старий коміт із секретом лишається досяжним трьома шляхами."""
    W, H = 1060, 470
    frags = []
    frags.append(text(530, 58,
                      "«Прибрати» — це додати НОВИЙ коміт (C4); старий (C2) нікуди не зникає.",
                      size=14, color=MUTED))
    cy = 170
    chain = [
        (150, "C1", MUTED, FILL, "початок"),
        (380, "C2", POS, "#fdecea", "секрет!"),
        (610, "C3", MUTED, FILL, "…"),
        (840, "C4", FIELD, "#eef7f0", "git rm"),
    ]
    for i in range(len(chain) - 1):
        frags.append(arrow(chain[i][0] + 30, cy, chain[i + 1][0] - 30, cy, color=MUTED, sw=2.0))
    for x, lbl, ring, fill, sub in chain:
        frags.append(circle(x, cy, 30, fill=fill, stroke=ring, sw=2.6))
        frags.append(text(x, cy + 6, lbl, size=18, color=INK, bold=True))
        if sub == "секрет!":                       # над вузлом — щоб не заважати стрілкам знизу
            frags.append(text(x, cy - 46, sub, size=13, color=POS, bold=True))
        else:
            frags.append(text(x, cy + 58, sub, size=13, color=MUTED))
    tag, tw, th = textbox(840, 95, "гілка main", size=12, fill=BG, stroke=FIELD, sw=1.5)
    frags.append(tag)
    frags.append(arrow(840, 95 + th / 2, 840, cy - 32, color=FIELD, sw=1.8))

    # три шляхи, якими старий C2 лишається живим — стрілки знизу вгору до C2
    revive = [
        (215, "досяжний за SHA\n(a1b2c3…)"),
        (400, "у кожному\nфорку"),
        (585, "у лозі\nGH Archive"),
    ]
    for x, label in revive:
        box, bw, bh = textbox(x, 350, label, size=12, fill=FILL, stroke=MUTED, sw=1.4)
        frags.append(box)
        frags.append(arrow(x, 350 - bh / 2, 380 + (x - 380) * 0.18, cy + 34, color=POS, sw=1.7))
    frags.append(text(530, 420,
                      "Секрет у C2 лишається живим — за SHA, у форках, у вічному журналі подій.",
                      size=13, color=MUTED))
    frags.append(text(530, 444,
                      "git rm / rebase / force-push воюють із рядком; шкода вже на іншому рівні.",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "immutable-history.svg"), W, H, *frags,
           title="Чому git rm не рятує: історію не переписати")


if __name__ == "__main__":
    fig_two_doors()
    fig_blast_radius()
    fig_reference_not_value()
    fig_snapshot_swap()
    fig_redaction_wall()
    fig_secrets_arms_race()
    fig_immutable_history()
    print("OK: two-doors.svg, blast-radius.svg, reference-not-value.svg, "
          "snapshot-swap.svg, redaction-wall.svg, "
          "secrets-arms-race.svg, immutable-history.svg")
