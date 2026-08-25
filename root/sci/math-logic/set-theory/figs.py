# -*- coding: utf-8 -*-
"""Фігури до статті «Теорія множин».
Запуск:  python figs.py   → пише SVG у ./img/
  anatomy-set · set-operations · sizes-of-infinity · russell-paradox
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#eaf7ef"
REDFILL = "#fdecea"
BLUEFILL = "#eaf0fd"
YELLOWFILL = "#fdf3d7"
ROW = "#f4f6f8"


def node(cx, cy, lab, r=18, fill=FILL, stroke=LINE, sw=1.8, tcol=INK, ts=15, bold=True):
    return circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw) + \
           text(cx, cy + ts * 0.36, lab, size=ts, bold=bold, color=tcol)


def vcircle(cx, cy, r, fill, op=0.16, stroke=INK, sw=1.8):
    """Напівпрозоре коло — для перекриття Венна."""
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="%.2f" '
            'stroke="%s" stroke-width="%.1f"/>' % (cx, cy, r, fill, op, stroke, sw))


# ── 1. Будова множини: належність, два записи, порожня, байдужість ────────────
def fig_anatomy_set():
    W, H = 940, 440
    f = [text(W / 2, 34, "Множина: чистий факт «лежить / не лежить»", size=19, bold=True),
         text(W / 2, 57, "єдине первинне поняття — належність ∈; усе інше випливає з нього",
              size=12.5, color=MUTED, italic=True)]

    # ── ліворуч: коло A з елементами + належність ──
    acx, acy, ar = 210, 190, 92
    f.append(text(acx, acy - ar - 16, "A", size=20, bold=True, color=NEG))
    f.append(circle(acx, acy, ar, fill=BLUEFILL, stroke=NEG, sw=2.0))
    elems = [(170, 160, "2"), (250, 165, "3"), (172, 222, "5"), (248, 220, "7")]
    for ex, ey, lab in elems:
        f.append(node(ex, ey, lab, r=17, fill=BG, stroke=NEG, tcol=NEG, ts=15))
    # 3 ∈ A
    f.append(text(acx, acy + ar + 26, "3 ∈ A  —  трійка належить A", size=12.5, color=NEG))
    # 4 ∉ A — назовні
    ox, oy = 372, 150
    f.append(node(ox, oy, "4", r=17, fill=BG, stroke=MUTED, tcol=MUTED, ts=15))
    f.append(text(ox, oy - 26, "4 ∉ A", size=12.5, color=MUTED))
    f.append(line(ox - 15, oy + 8, acx + ar - 6, acy - 4, color=MUTED, sw=1.2, dash="4,4"))

    # ── праворуч-угорі: два записи — одна множина ──
    rx = 620
    f.append(text(rx + 150, 108, "Два записи — одна множина", size=14, bold=True))
    b1, w1, h1 = textbox(rx + 150, 150, "{ 2, 3, 5, 7 }", size=16, fill=ROW, stroke=LINE,
                         sw=1.4, bold=True, min_w=250)
    f.append(b1)
    f.append(text(rx + 150, 182, "перелік", size=11.5, color=MUTED, italic=True))
    b2, w2, h2 = textbox(rx + 150, 224, "{ x : x — просте,  x < 10 }", size=15, fill=ROW,
                         stroke=LINE, sw=1.4, min_w=250)
    f.append(b2)
    f.append(text(rx + 150, 256, "властивість «такі, що…»", size=11.5, color=MUTED, italic=True))
    f.append(text(rx + 150, 202, "=", size=20, bold=True, color=FIELD))

    # ── низ: три картки-факти ──
    cards = [
        ("∅  — порожня множина", "нічого всередині — але сама реальна", GREENFILL, FIELD),
        ("{1, 2, 3} = {3, 2, 1}", "порядок байдужий", ROW, MUTED),
        ("{1, 2, 2, 3} = {1, 2, 3}", "повтори байдужі", ROW, MUTED),
    ]
    cw, gap, ch, by = 288, 16, 66, 336
    x0 = (W - (cw * 3 + gap * 2)) / 2
    for i, (t1, t2, fill, st) in enumerate(cards):
        x = x0 + i * (cw + gap)
        f.append(rect(x, by, cw, ch, fill=fill, stroke=st, sw=1.4, rx=8))
        f.append(text(x + cw / 2, by + 27, t1, size=14.5, bold=True))
        f.append(text(x + cw / 2, by + 49, t2, size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "anatomy-set.svg"), W, H, *f)


# ── 2. Дії над множинами: перекриття Венна + результати на бігучому прикладі ───
def fig_set_operations():
    W, H = 980, 440
    f = [text(W / 2, 34, "Дії над множинами — логіка, записана предметами", size=19, bold=True),
         text(W / 2, 57, "A = {1, 2, 3},   B = {3, 4, 5};   за кожною дією стоїть зв'язка «або», «і», «не»",
              size=12.5, color=MUTED, italic=True)]

    # дві напівпрозорі бульбашки, що перекриваються
    acx, bcx, cy, r = 415, 565, 190, 100
    f.append(vcircle(acx, cy, r, NEG, op=0.13, stroke=NEG, sw=2.0))
    f.append(vcircle(bcx, cy, r, FIELD, op=0.15, stroke=FIELD, sw=2.0))
    f.append(text(acx - 66, cy - r - 8, "A", size=19, bold=True, color=NEG))
    f.append(text(bcx + 66, cy - r - 8, "B", size=19, bold=True, color=FIELD))
    # елементи: A-лише (1,2) · спільне (3) · B-лише (4,5)
    for ex, ey, lab, col in [(348, 170, "1", NEG), (348, 215, "2", NEG),
                             (490, 192, "3", INK),
                             (632, 170, "4", FIELD), (632, 215, "5", FIELD)]:
        f.append(node(ex, ey, lab, r=17, fill=BG, stroke=col, tcol=col, ts=15))
    f.append(text(490, cy + r + 4, "спільне", size=11, color=MUTED, italic=True))

    # п'ять карток-результатів
    cards = [
        ("Об'єднання   A ∪ B", "{1, 2, 3, 4, 5}", "«або»: усе з обох", GREENFILL, FIELD),
        ("Переріз   A ∩ B", "{3}", "«і»: лише спільне", BLUEFILL, NEG),
        ("Різниця   A \\ B", "{1, 2}", "«і не»: A без B", ROW, MUTED),
        ("Підмножина   A ⊆ B", "ні", "чи все A всередині B", ROW, MUTED),
        ("Степенева   P({a,b,c})", "8 = 2³", "усі підмножини: кожен так/ні", YELLOWFILL, "#b8860b"),
    ]
    cw, gap, ch, by = 178, 13, 92, 316
    x0 = (W - (cw * 5 + gap * 4)) / 2
    for i, (t1, res, t3, fill, st) in enumerate(cards):
        x = x0 + i * (cw + gap)
        f.append(rect(x, by, cw, ch, fill=fill, stroke=st, sw=1.5, rx=8))
        f.append(text(x + cw / 2, by + 24, t1, size=12.5, bold=True))
        f.append(text(x + cw / 2, by + 52, res, size=17, bold=True, color=st))
        f.append(text(x + cw / 2, by + 76, t3, size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "set-operations.svg"), W, H, *f)


# ── 3. Нескінченність різного розміру: бієкція проти діагоналі ─────────────────
def fig_sizes_of_infinity():
    W, H = 1000, 450
    f = [text(W / 2, 34, "Нескінченність буває різного розміру", size=19, bold=True),
         text(W / 2, 57, "розмір міряють паруванням, а не лічбою: однакова потужність ⟺ є бієкція",
              size=12.5, color=MUTED, italic=True)]

    f.append(line(W / 2, 84, W / 2, 392, color="#dcdfe4", sw=1.3))

    # ── ЛІВОРУЧ: порівну (ℕ ↔ парні) ──
    f.append(text(255, 108, "Порівну:  натуральні ↔ парні", size=14.5, bold=True))
    cols = [95, 175, 255, 335, 415]
    ny, ey = 168, 268
    nats = ["0", "1", "2", "3", "4"]
    evens = ["0", "2", "4", "6", "8"]
    for x, lab in zip(cols, nats):
        f.append(node(x, ny, lab, r=20, fill=BLUEFILL, stroke=NEG, tcol=NEG, ts=16))
    for x, lab in zip(cols, evens):
        f.append(node(x, ey, lab, r=20, fill=GREENFILL, stroke=FIELD, tcol=FIELD, ts=16))
    for x in cols:
        f.append(arrow(x, ny + 22, x, ey - 22, color=MUTED, sw=1.6))
    f.append(text(465, ny + 6, "…", size=24, bold=True, color=NEG))
    f.append(text(465, ey + 6, "…", size=24, bold=True, color=FIELD))
    f.append(text(255, 316, "кожному n — своя пара 2n; нікого не забуто", size=12, color=MUTED, italic=True))
    box, _, _ = textbox(255, 356, "частина (парні) = ціле (усі натуральні)",
                        size=13.5, fill=GREENFILL, stroke=FIELD, sw=1.4, bold=True)
    f.append(box)

    # ── ПРАВОРУЧ: більше (діагональ Кантора) ──
    f.append(text(755, 108, "Більше:  дійсних не перелічити", size=14.5, bold=True))
    digits = [["3", "1", "4"], ["1", "5", "9"], ["2", "6", "5"]]
    rows_y = [148, 200, 252]
    cw, gx0 = 42, 620
    colx = [gx0, gx0 + 52, gx0 + 104]
    subs = ["r₁", "r₂", "r₃"]
    for i, (ry, sub) in enumerate(zip(rows_y, subs)):
        f.append(text(gx0 - 22, ry + 6, sub + " = 0.", size=15, anchor="end"))
        for j, dg in enumerate(digits[i]):
            diag = (i == j)
            if diag:
                f.append(rect(colx[j] - cw / 2, ry - 19, cw, 38, fill=REDFILL,
                              stroke=POS, sw=1.8, rx=6))
            f.append(text(colx[j], ry + 6, dg, size=17, bold=diag,
                          color=(POS if diag else INK)))
        f.append(text(colx[2] + 34, ry + 6, "…", size=18, bold=True, color=MUTED))
    # збудоване нове число — кожну діагональну цифру змінили (+1)
    nry = 316
    f.append(text(gx0 - 22, nry + 6, "нове = 0.", size=15, anchor="end", bold=True, color=POS))
    for j, dg in enumerate(["4", "6", "6"]):
        f.append(rect(colx[j] - cw / 2, nry - 19, cw, 38, fill=BG, stroke=POS, sw=1.8, rx=6))
        f.append(text(colx[j], nry + 6, dg, size=17, bold=True, color=POS))
    f.append(text(colx[2] + 34, nry + 6, "…", size=18, bold=True, color=POS))
    f.append(arrow(gx0 + 52, 274, gx0 + 30, nry - 22, color=POS, sw=1.6))
    box2, _, _ = textbox(760, 392,
                         "різниться з кожним рядком у його цифрі → у списку його нема",
                         size=12.5, fill=REDFILL, stroke=POS, sw=1.4)
    f.append(box2)

    render(os.path.join(IMG, "sizes-of-infinity.svg"), W, H, *f)


# ── 4. Парадокс Рассела: правило, що вбиває себе ──────────────────────────────
def fig_russell_paradox():
    W, H = 940, 430
    f = [text(W / 2, 34, "Парадокс Рассела: правило, що вбиває себе", size=19, bold=True),
         text(W / 2, 57, "R = { x : x ∉ x } — множина всіх множин, які не містять себе",
              size=12.5, color=MUTED, italic=True)]

    # верхня рамка-означення
    top, tw, th = textbox(W / 2, 100, "R = усі множини, що НЕ містять себе самих",
                          size=14, fill=ROW, stroke=LINE, sw=1.5, bold=True)
    f.append(top)

    def branch(cx, title, lines, tcol):
        cw, cyt, ch = 360, 158, 148
        x = cx - cw / 2
        out = rect(x, cyt, cw, ch, fill=BG, stroke=tcol, sw=1.7, rx=10)
        out += rect(x, cyt, cw, 34, fill=(BLUEFILL if tcol == NEG else REDFILL),
                    stroke=tcol, sw=1.7, rx=10)
        out += rect(x, cyt + 22, cw, 12, fill=(BLUEFILL if tcol == NEG else REDFILL), stroke="none", sw=0)
        out += text(cx, cyt + 23, title, size=15, bold=True, color=tcol)
        for k, ln in enumerate(lines):
            out += text(cx, cyt + 60 + k * 26, ln, size=13)
        return out

    lx, rx = 258, 682
    f.append(branch(lx, "Припустимо   R ∈ R",
                    ["R містить себе,", "отже R не «звичайна»,",
                     "а R бере лише звичайні —", "тож  R ∉ R"], NEG))
    f.append(branch(rx, "Припустимо   R ∉ R",
                    ["R не містить себе,", "отже R «звичайна»,",
                     "а всі звичайні беруть у R —", "тож  R ∈ R"], POS))
    # стрілки від означення до гілок
    f.append(arrow(W / 2 - 90, 118, lx + 60, 156, color=MUTED, sw=1.6))
    f.append(arrow(W / 2 + 90, 118, rx - 60, 156, color=MUTED, sw=1.6))
    # двобічна стрілка суперечності між гілками
    f.append(arrow(lx + 182, 232, rx - 182, 232, color=INK, sw=1.8))
    f.append(arrow(rx - 182, 246, lx + 182, 246, color=INK, sw=1.8))
    f.append(text(W / 2, 226, "⟺", size=20, bold=True, color=POS))

    box, _, _ = textbox(W / 2, 372,
                        "R ∈ R  ⟺  R ∉ R  — суперечність: множини R не існує.\n"
                        "Отже не будь-яка властивість задає множину.",
                        size=13.5, fill=REDFILL, stroke=POS, sw=1.6, bold=True)
    f.append(box)

    render(os.path.join(IMG, "russell-paradox.svg"), W, H, *f)


# ── 5. Життєва дуга Кантора: відкриття проти опору (до hist-cantor) ────────────
def fig_cantor_timeline():
    W, H = 1080, 560
    f = [text(W / 2, 34, "Ґеорґ Кантор: відкриття проти опору", size=19, bold=True),
         text(W / 2, 57, "кожен прорив у теорію нескінченного наражався на люту протидію — а виправдання прийшло по смерті",
              size=12.5, color=MUTED, italic=True)]

    sy = 250
    x0, x1 = 120, 960
    f.append(line(x0, sy, x1, sy, color="#c9ced6", sw=3))

    miles = [
        ("1845", "Народження в С.-Петербурзі;\nбатько данець, матір — з роду\nмузикантів Бемів", "up"),
        ("1870", "Задача Гайне: чи єдиний\nтригонометричний ряд функції;\nвихід на множини точок", "down"),
        ("1874", "Дійсних БІЛЬШЕ за натуральні —\nперший доказ незліченності\n(журнал Крелле)", "up"),
        ("1883", "Трансфінітні ординали;\n«суть математики —\nу її свободі»", "down"),
        ("1891", "Діагональний метод:\nпростий доказ і ціла\nсходинка нескінченностей", "up"),
        ("1884+", "Напади хвороби; смерть\nсина 1899; шпиталі до кінця", "down"),
        ("1918", "Смерть у клініці Галле,\nу злиднях воєнного часу", "up"),
    ]
    n = len(miles)
    xs = [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]
    cw, chh = 202, 86
    for x, (yr, desc, side) in zip(xs, miles):
        f.append(circle(x, sy, 8, fill=BG, stroke=INK, sw=2.2))
        if side == "up":
            f.append(text(x, sy - 20, yr, size=15, bold=True, color=NEG))
            f.append(fitbox(x - cw / 2, sy - 46 - chh, cw, chh, desc, size=11.5,
                            fill=BLUEFILL, stroke=NEG, sw=1.4))
        else:
            f.append(text(x, sy + 30, yr, size=15, bold=True, color=FIELD))
            f.append(fitbox(x - cw / 2, sy + 44, cw, chh, desc, size=11.5,
                            fill=GREENFILL, stroke=FIELD, sw=1.4))

    # два підсумкові банери: протидія ↔ виправдання
    f.append(text(305, 404, "Люта протидія за життя", size=14, bold=True, color=POS))
    f.append(fitbox(70, 414, 470, 104,
                    "Леопольд Кронекер, впливовий берлінець,\n"
                    "звав Кантора «розбещувачем молоді»\n"
                    "й роками блокував йому кафедру в Берліні —\n"
                    "лишивши доживати у провінційному Галле.",
                    size=13, fill=REDFILL, stroke=POS, sw=1.5))
    f.append(text(775, 404, "Пізнє виправдання", size=14, bold=True, color=FIELD))
    f.append(fitbox(540, 414, 470, 104,
                    "Давід Гільберт, 1925:\n"
                    "«Із раю, що його створив нам Кантор,\n"
                    "нас не вижене ніхто».\n"
                    "Теорія множин стала основою математики.",
                    size=13, fill=GREENFILL, stroke=FIELD, sw=1.5))

    render(os.path.join(IMG, "cantor-arc.svg"), W, H, *f)


# ── 6. Належність: список O(n) сканує vs гешмножина O(1) стрибає ───────────────
def fig_membership_cost():
    W, H = 980, 430
    f = [text(W / 2, 34, "Належність за одну дію: чому «чи є воно там» майже безплатне",
              size=19, bold=True),
         text(W / 2, 57, "список: сканувати всі елементи — O(n);   гешмножина: обчислити комірку — O(1)",
              size=12.5, color=MUTED, italic=True)]
    f.append(line(490, 84, 490, 372, color="#dcdfe4", sw=1.3))

    # ── ЛІВОРУЧ: список — сканувати поспіль ──
    f.append(text(230, 108, "Список: шукати 42 — сканувати поспіль", size=14.5, bold=True))
    vals = ["7", "19", "3", "88", "42", "5"]
    x0, pitch, cw, ch, cy = 48, 62, 54, 44, 168
    tgt = 4  # індекс, де лежить 42
    for i, v in enumerate(vals):
        x = x0 + i * pitch
        hit = (i == tgt)
        f.append(rect(x, cy, cw, ch, fill=(GREENFILL if hit else BG),
                      stroke=(FIELD if hit else LINE), sw=(2.0 if hit else 1.4), rx=6))
        f.append(text(x + cw / 2, cy + 28, v, size=16, bold=True,
                      color=(FIELD if hit else INK)))
        if i <= tgt:  # лічильник порівнянь над сканованими комірками
            f.append(text(x + cw / 2, cy - 12, str(i + 1), size=12,
                          color=(FIELD if hit else MUTED), bold=hit))
    f.append(text(x0 + len(vals) * pitch + 6, cy + 28, "…", size=20, color=MUTED, bold=True))
    f.append(arrow(x0 + 4, cy + ch + 22, x0 + tgt * pitch + cw, cy + ch + 22, color=MUTED, sw=1.6))
    f.append(text(232, cy + ch + 46, "5 порівнянь, доки знайшли; якого нема — усі n",
                  size=12, color=MUTED, italic=True))

    # ── ПРАВОРУЧ: гешмножина — обчислити комірку й стрибнути ──
    f.append(text(730, 108, "Гешмножина: обчислити, де воно лежить", size=14.5, bold=True))
    eb, ew, _ = textbox(560, 145, "42", size=16, fill=BG, stroke=NEG, sw=1.6, bold=True, min_w=44)
    f.append(eb)
    hb, hw, _ = textbox(710, 145, "h(42) = 4", size=15, fill=YELLOWFILL, stroke="#b8860b",
                        sw=1.5, bold=True)
    f.append(hb)
    f.append(arrow(560 + ew / 2, 145, 710 - hw / 2, 145, color=INK, sw=1.6))
    # рядок комірок (buckets) 0..6
    bx0, bpitch, bw, bh, by = 520, 56, 52, 34, 208
    bhit = 4
    for i in range(7):
        x = bx0 + i * bpitch
        hit = (i == bhit)
        f.append(rect(x, by, bw, bh, fill=(GREENFILL if hit else ROW),
                      stroke=(FIELD if hit else LINE), sw=(2.0 if hit else 1.3), rx=6))
        f.append(text(x + bw / 2, by + bh + 18, str(i), size=11.5, color=MUTED))
        if hit:
            f.append(text(x + bw / 2, by + 22, "42", size=15, bold=True, color=FIELD))
    f.append(arrow(710, 163, bx0 + bhit * bpitch + bw / 2, by - 4, color="#b8860b", sw=1.6))
    f.append(text(730, by + bh + 44, "комірка 4 — один стрибок, скільки б не було елементів",
                  size=12, color=MUTED, italic=True))

    # ── низ: два підсумки ──
    b1, _, _ = textbox(232, 392, "Список:  до n порівнянь  —  O(n)",
                       size=13.5, fill=REDFILL, stroke=POS, sw=1.5, bold=True)
    f.append(b1)
    b2, _, _ = textbox(730, 392, "Гешмножина:  1 стрибок  —  O(1) амортизовано",
                       size=13.5, fill=GREENFILL, stroke=FIELD, sw=1.5, bold=True)
    f.append(b2)

    render(os.path.join(IMG, "membership-cost.svg"), W, H, *f)


# ── 7. Степенева множина бітовою маскою: 0..2ⁿ−1 → підмножини {a,b,c} ──────────
def fig_powerset_bitmask():
    W, H = 780, 510
    f = [text(W / 2, 34, "Степенева множина бітовою маскою:  0 … 2³−1", size=19, bold=True),
         text(W / 2, 57, "кожен біт — брати елемент чи ні; 3 біти дають 2³ = 8 підмножин",
              size=12.5, color=MUTED, italic=True)]

    elems = ["a", "b", "c"]              # a=біт 0, b=біт 1, c=біт 2
    tx0, tw = 150, 480                   # таблиця: x 150..630
    mcx = 200                            # колонка «маска»
    bitcx = [285, 335, 385]              # позиції бітів c b a (зліва старший)
    scx = 530                            # колонка «підмножина»

    # заголовок
    f.append(text(mcx, 100, "маска", size=13.5, bold=True))
    f.append(text(335, 84, "біти  (c b a)", size=12, color=MUTED))
    for lab, bx in zip(["c", "b", "a"], bitcx):
        f.append(text(bx, 104, lab, size=13.5, bold=True, color=NEG))
    f.append(text(scx, 100, "підмножина", size=13.5, bold=True))
    f.append(line(tx0, 110, tx0 + tw, 110, color=LINE, sw=1.4))

    ry0, rh = 130, 40
    for m in range(8):
        y = ry0 + m * rh
        if m % 2 == 1:                   # зебра
            f.append(rect(tx0, y, tw, rh, fill=ROW, stroke="none", sw=0, rx=0))
        # маска (десяткова)
        f.append(text(mcx, y + rh / 2 + 5, str(m), size=15, bold=True))
        # три біти c b a
        bits = [(m >> 2) & 1, (m >> 1) & 1, m & 1]   # c, b, a
        for bit, bx in zip(bits, bitcx):
            on = bool(bit)
            f.append(rect(bx - 15, y + rh / 2 - 13, 30, 26,
                          fill=(GREENFILL if on else BG),
                          stroke=(FIELD if on else "#cfd4da"), sw=1.5, rx=5))
            f.append(text(bx, y + rh / 2 + 5, str(bit), size=14, bold=on,
                          color=(FIELD if on else MUTED)))
        # підмножина
        chosen = [elems[i] for i in range(3) if m >> i & 1]
        sub = "{ " + ", ".join(chosen) + " }" if chosen else "∅"
        f.append(text(scx, y + rh / 2 + 5, sub, size=15,
                      bold=bool(chosen), color=(FIELD if chosen else MUTED)))

    f.append(line(tx0, ry0 + 8 * rh, tx0 + tw, ry0 + 8 * rh, color="#dcdfe4", sw=1.2))
    box, _, _ = textbox(W / 2, ry0 + 8 * rh + 30,
                        "лічильник 0 … 2ⁿ−1 сам перебирає всі підмножини — рівно 2ⁿ, без пропусків і повторів",
                        size=12.5, fill=BLUEFILL, stroke=NEG, sw=1.4)
    f.append(box)

    render(os.path.join(IMG, "powerset-bitmask.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anatomy_set()
    fig_set_operations()
    fig_sizes_of_infinity()
    fig_russell_paradox()
    fig_cantor_timeline()
    fig_membership_cost()
    fig_powerset_bitmask()
    print("OK: anatomy-set, set-operations, sizes-of-infinity, russell-paradox, cantor-arc,",
          "membership-cost, powerset-bitmask ->", IMG)


# ── everything-is-a-set (math-вставка): пара · ординали · класи пар · вежа ─────
def fig_ordered_pair():
    W, H = 1000, 480
    f = [text(W / 2, 34, "Впорядкована пара: порядок, схований у множинах", size=19, bold=True),
         text(W / 2, 57, "(a, b) = { {a}, {a, b} } — множина порядку не знає, а пара його зберігає",
              size=12.5, color=MUTED, italic=True)]
    f.append(line(W / 2, 82, W / 2, 456, color="#dcdfe4", sw=1.3))

    lcx = 258
    f.append(text(lcx, 110, "Будова  (1, 2)", size=15, bold=True))
    ox, oy, ow, oh = lcx - 200, 132, 400, 118
    f.append(rect(ox, oy, ow, oh, fill=BLUEFILL, stroke=NEG, sw=1.8, rx=12))
    f.append(text(ox + 16, oy + 30, "{", size=28, color=NEG, anchor="start"))
    f.append(text(ox + ow - 16, oy + 30, "}", size=28, color=NEG, anchor="end"))
    bA, _, _ = textbox(lcx - 92, oy + 58, "{ 1 }", size=16, fill=BG, stroke=FIELD, sw=1.7, bold=True, min_w=104)
    bB, _, _ = textbox(lcx + 96, oy + 58, "{ 1, 2 }", size=16, fill=BG, stroke=INK, sw=1.7, bold=True, min_w=128)
    f.append(bA)
    f.append(bB)
    f.append(text(lcx - 92, oy + 98, "самотній", size=11.5, color=MUTED, italic=True))
    f.append(text(lcx + 96, oy + 98, "пара", size=11.5, color=MUTED, italic=True))
    r1, _, _ = textbox(lcx, 300, "⋂ = { 1 }   →   перший = 1", size=13.5, fill=GREENFILL,
                       stroke=FIELD, sw=1.5, bold=True, min_w=340)
    f.append(r1)
    r2, _, _ = textbox(lcx, 344, "решта з ⋃ = { 2 }   →   другий = 2", size=13.5, fill=ROW,
                       stroke=MUTED, sw=1.4, min_w=340)
    f.append(r2)
    r3, _, _ = textbox(lcx, 400, "порядок читається із самої будови", size=12.5, fill=BG,
                       stroke=NEG, sw=1.4, bold=True, min_w=340)
    f.append(r3)

    rcx = 742
    f.append(text(rcx, 110, "Порядок справді закодовано", size=15, bold=True))
    c1, _, _ = textbox(rcx, 156, "(1, 2) = { {1}, {1, 2} }", size=15, fill=ROW, stroke=LINE,
                       sw=1.4, bold=True, min_w=310)
    c2, _, _ = textbox(rcx, 200, "(2, 1) = { {2}, {1, 2} }", size=15, fill=ROW, stroke=LINE,
                       sw=1.4, bold=True, min_w=310)
    f.append(c1)
    f.append(c2)
    d, _, _ = textbox(rcx, 254, "різні множини   ⇒   (1, 2) ≠ (2, 1)", size=13.5, fill=REDFILL,
                      stroke=POS, sw=1.5, bold=True, min_w=310)
    f.append(d)
    f.append(text(rcx, 322, "Вироджений випадок  a = b:", size=13, bold=True))
    e, _, _ = textbox(rcx, 364, "(a, a) = { {a}, {a} } = { {a} }", size=14, fill=YELLOWFILL,
                      stroke="#b8860b", sw=1.4, min_w=310)
    f.append(e)
    f.append(text(rcx, 406, "одна множина — теж коректна пара", size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "ordered-pair.svg"), W, H, *f)


def fig_von_neumann_ordinals():
    W, H = 1010, 480
    f = [text(W / 2, 34, "Числа з порожнечі: ординали фон Неймана", size=19, bold=True),
         text(W / 2, 57, "0 = ∅,  а далі кожне число — множина всіх попередніх:  n+1 = n ∪ {n}",
              size=12.5, color=MUTED, italic=True)]

    rows = [
        ("0", "= ∅", "нуль елементів"),
        ("1", "= {0} = {∅}", "один елемент"),
        ("2", "= {0, 1} = {∅, {∅}}", "два елементи"),
        ("3", "= {0, 1, 2}", "три елементи"),
    ]
    y0, dy, lx, lw = 112, 60, 66, 566
    for i, (n, body, note) in enumerate(rows):
        y = y0 + i * dy
        f.append(rect(lx, y, lw, 46, fill=(ROW if i % 2 else BG), stroke=LINE, sw=1.2, rx=8))
        f.append(text(lx + 34, y + 30, n, size=21, bold=True, color=NEG))
        f.append(text(lx + 74, y + 30, body, size=16, anchor="start"))
        f.append(text(lx + lw - 16, y + 30, note, size=11.5, color=MUTED, italic=True, anchor="end"))

    px = 800
    p1, _, _ = textbox(px, 150, "n має рівно\nn елементів", size=14.5, fill=GREENFILL,
                       stroke=FIELD, sw=1.7, bold=True, min_w=250)
    f.append(p1)
    f.append(text(px, 202, "число саме собі — лічба", size=11.5, color=MUTED, italic=True))
    p2, _, _ = textbox(px, 268, "m < n   ⇔   m ∈ n", size=15, fill=BLUEFILL, stroke=NEG,
                       sw=1.7, bold=True, min_w=250)
    f.append(p2)
    f.append(text(px, 306, "порядок — це належність", size=11.5, color=MUTED, italic=True))

    ch, _, _ = textbox(W / 2, 420, "0 ∈ 1 ∈ 2 ∈ 3 ∈ …   —   уся драбина «менше» вкладена в знак ∈",
                       size=13.5, fill=BG, stroke=NEG, sw=1.5, bold=True, min_w=720)
    f.append(ch)

    render(os.path.join(IMG, "von-neumann-ordinals.svg"), W, H, *f)


def fig_pairs_quotient():
    W, H = 1020, 510
    f = [text(W / 2, 34, "Цілі та раціональні — це класи пар", size=19, bold=True),
         text(W / 2, 57, "склей усі пари, що означають те саме число: клас пар = одне нове число",
              size=12.5, color=MUTED, italic=True)]
    f.append(line(W / 2, 82, W / 2, 486, color="#dcdfe4", sw=1.3))

    def grid(ox, oy, step, nmax, xlab, ylab):
        g = [arrow(ox - 10, oy, ox + nmax * step + 24, oy, color=INK, sw=1.6),
             arrow(ox, oy + 10, ox, oy - nmax * step - 24, color=INK, sw=1.6),
             text(ox + nmax * step + 32, oy + 5, xlab, size=13, bold=True, anchor="start"),
             text(ox - 4, oy - nmax * step - 30, ylab, size=13, bold=True)]
        for k in range(nmax + 1):
            g.append(text(ox + k * step, oy + 20, str(k), size=10.5, color=MUTED))
            if k > 0:
                g.append(text(ox - 16, oy - k * step + 4, str(k), size=10.5, color=MUTED))
        return g

    step, nmax = 30, 6

    ox, oy = 120, 330
    f.append(text(255, 106, "Ціле = різниця, що чекає:  (a, b) ≈ a − b", size=13.5, bold=True))
    f += grid(ox, oy, step, nmax, "a", "b")
    for a in range(nmax + 1):
        for b in range(nmax + 1):
            f.append(circle(ox + a * step, oy - b * step, 3.0, fill="#c8ccd2", stroke="none", sw=0))
    clsz = [(0, 2), (1, 3), (2, 4), (3, 5), (4, 6)]
    f.append(line(ox + clsz[0][0] * step, oy - clsz[0][1] * step,
                  ox + clsz[-1][0] * step, oy - clsz[-1][1] * step, color=POS, sw=2.0))
    for a, b in clsz:
        f.append(circle(ox + a * step, oy - b * step, 5.5, fill=REDFILL, stroke=POS, sw=2))
    nz, _, _ = textbox(400, 176, "клас −2:\n(0,2) (1,3)\n(2,4) (3,5)…\nусі → ціле −2",
                       size=11.5, fill=REDFILL, stroke=POS, sw=1.3, min_w=150)
    f.append(nz)
    fz, _, _ = textbox(255, 412, "(a, b) ~ (c, d)  ⇔  a + d = b + c", size=13.5, fill=GREENFILL,
                       stroke=FIELD, sw=1.5, bold=True, min_w=360)
    f.append(fz)
    f.append(text(255, 454, "ℤ = (ℕ × ℕ) / ~", size=15, bold=True, color=NEG))

    ox2, oy2 = 630, 330
    f.append(text(765, 106, "Раціональне = відношення:  (p, q) ≈ p / q", size=13.5, bold=True))
    f += grid(ox2, oy2, step, nmax, "p", "q")
    for p in range(nmax + 1):
        for q in range(nmax + 1):
            f.append(circle(ox2 + p * step, oy2 - q * step, 3.0, fill="#c8ccd2", stroke="none", sw=0))
    clsq = [(1, 2), (2, 4), (3, 6)]
    f.append(line(ox2, oy2, ox2 + 3 * step, oy2 - 6 * step, color=POS, sw=2.0))
    for p, q in clsq:
        f.append(circle(ox2 + p * step, oy2 - q * step, 5.5, fill=REDFILL, stroke=POS, sw=2))
    nq, _, _ = textbox(905, 176, "клас ½:\n(1,2) (2,4)\n(3,6)…\nусі → дріб 1/2",
                       size=11.5, fill=REDFILL, stroke=POS, sw=1.3, min_w=140)
    f.append(nq)
    fq, _, _ = textbox(765, 412, "(p, q) ~ (r, s)  ⇔  p · s = q · r", size=13.5, fill=GREENFILL,
                       stroke=FIELD, sw=1.5, bold=True, min_w=360)
    f.append(fq)
    f.append(text(765, 454, "ℚ = (ℤ × ℤ*) / ~     (q ≠ 0)", size=15, bold=True, color=NEG))

    render(os.path.join(IMG, "pairs-quotient.svg"), W, H, *f)


def fig_set_tower():
    W, H = 1000, 520
    f = [text(W / 2, 34, "Уся математика з ∅ і ∈", size=19, bold=True),
         text(W / 2, 57, "одна субстанція (множина) плюс одне відношення (належність) — і більше нічого",
              size=12.5, color=MUTED, italic=True)]
    cx = 428
    layers = [
        (108, "уся математика: простори, функції, аналіз, геометрія…", YELLOWFILL, "#b8860b", 560),
        (172, "ℝ — перерізи або послідовності раціональних", BLUEFILL, NEG, 470),
        (236, "ℤ, ℚ — класи еквівалентних пар", BLUEFILL, NEG, 400),
        (300, "ℕ — ординали фон Неймана:  0 = ∅,  n+1 = n ∪ {n}", GREENFILL, FIELD, 490),
        (364, "функція = однозначне відношення  ⊆  A × B", ROW, LINE, 430),
        (428, "впорядкована пара  (a, b) = { {a}, {a, b} }", ROW, LINE, 430),
    ]
    for cy, s, fill, st, w in layers:
        f.append(rect(cx - w / 2, cy - 22, w, 44, fill=fill, stroke=st, sw=1.6, rx=10))
        f.append(text(cx, cy + 5, s, size=13.5, bold=True))
    base, _, _ = textbox(cx, 494, "порожня множина ∅   ·   належність ∈", size=15, fill=BG,
                         stroke=POS, sw=2.4, bold=True, min_w=440)
    f.append(base)

    seq = [494, 428, 364, 300, 236, 172, 108]
    for i in range(len(seq) - 1):
        y_low = seq[i] - (18 if i == 0 else 22)
        y_high = seq[i + 1] + 22
        f.append(arrow(cx, y_low, cx, y_high, color=MUTED, sw=1.8))
    f.append(text(cx + 20, 336, "будується з", size=10.5, color=MUTED, italic=True, anchor="start"))

    note, _, _ = textbox(818, 300, "жодної\nнової\nсутності —\nтільки\nмножини\nй  ∈",
                         size=13, fill=GREENFILL, stroke=FIELD, sw=1.6, bold=True, min_w=150)
    f.append(note)

    render(os.path.join(IMG, "set-tower.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ordered_pair()
    fig_von_neumann_ordinals()
    fig_pairs_quotient()
    fig_set_tower()
    print("OK (everything-is-a-set): ordered-pair, von-neumann-ordinals, pairs-quotient, set-tower ->", IMG)
