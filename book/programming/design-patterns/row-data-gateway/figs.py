# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

HL = "#eafaf0"   # заливка виділеного рядка
COOL = "#eaf0fd"


# ── 1. Анатомія: рядок → шукач → шлюз (без правил) ──────────────────────────
def fig_anatomy():
    W, H = 1160, 470
    f = []
    f.append(text(W / 2, 32, "Шлюз рядка: об'єкт — це рядок; знаходить рядки окремий шукач",
                  size=17, bold=True))

    # ── ЛІВОРУЧ: таблиця orders ──
    TX, TW = 40, 320
    f.append(text(TX + TW / 2, 74, "таблиця orders у базі", size=12.5, color=MUTED))
    cols = [("id", 46), ("customer_id", 120), ("total", 70), ("status", 84)]
    rows = [
        (41, "c-77", "350", "new", False),
        (42, "c-19", "1200", "paid", True),
        (43, "c-19", "90", "shipped", False),
    ]
    HDR_Y, HDR_H, ROW_H = 92, 30, 34
    BODY_Y = HDR_Y + HDR_H
    f.append(rect(TX, HDR_Y, TW, HDR_H, fill=FILL, stroke=LINE, sw=1.5, rx=0))
    f.append(rect(TX, BODY_Y, TW, ROW_H * len(rows), fill=BG, stroke=LINE, sw=1.5, rx=0))
    for i, r in enumerate(rows):
        if r[4]:
            f.append(rect(TX, BODY_Y + i * ROW_H, TW, ROW_H, fill=HL, stroke=FIELD, sw=2.5, rx=0))
    xs = [TX]
    for _, w in cols:
        xs.append(xs[-1] + w)
    for x in xs[1:-1]:
        f.append(line(x, HDR_Y, x, BODY_Y + ROW_H * len(rows), color=MUTED, sw=1))
    for i in range(1, len(rows)):
        f.append(line(TX, BODY_Y + i * ROW_H, TX + TW, BODY_Y + i * ROW_H, color=MUTED, sw=1))
    centers = [(xs[i] + xs[i + 1]) / 2 for i in range(len(cols))]
    for c, (name, _) in zip(centers, cols):
        f.append(text(c, HDR_Y + 20, name, size=11, color=MUTED, bold=True))
    for i, r in enumerate(rows):
        y = BODY_Y + i * ROW_H + 22
        for c, val in zip(centers, r[:4]):
            f.append(text(c, y, str(val), size=11, color=INK))
    f.append(text(TX + TW / 2, BODY_Y + ROW_H * len(rows) + 30,
                  "один рядок = один об'єкт-шлюз", size=11.5, color=MUTED, italic=True))

    # ── ПОСЕРЕДИНІ: шукач ──
    FX, FY, FW, FH = 428, 150, 214, 104
    f.append(rect(FX, FY, FW, FH, fill=FILL, stroke=MUTED, sw=1.6, rx=8))
    f.append(text(FX + FW / 2, FY + 26, "OrderFinder", size=13, color=INK, bold=True))
    f.append(text(FX + FW / 2, FY + 48, "окремий клас-шукач", size=11, color=MUTED, italic=True))
    f.append(text(FX + FW / 2, FY + 72, "find(42)", size=12, color=NEG))
    f.append(text(FX + FW / 2, FY + 92, "findByStatus(...)", size=12, color=NEG))

    # табл → шукач (SELECT)
    f.append(arrow(FX - 6, FY + 52, TX + TW + 6, FY + 52, color=MUTED, sw=1.8))
    f.append(text((TX + TW + FX) / 2, FY + 40, "SELECT", size=11, color=MUTED))

    # ── ПРАВОРУЧ: об'єкт-шлюз ──
    GX, GW_, GY, GH = 700, 420, 92, 340
    f.append(rect(GX, GY, GW_, GH, fill=BG, stroke=FIELD, sw=2.2, rx=10))
    f.append(rect(GX, GY, GW_, 34, fill=HL, stroke=FIELD, sw=1.5, rx=10))
    f.append(text(GX + GW_ / 2, GY + 22, "OrderGateway — рядок id = 42", size=13, color=INK, bold=True))

    f.append(text(GX + 18, GY + 58, "поля = колонки того рядка", size=11, color=MUTED, anchor="start"))
    f.append(rect(GX + 18, GY + 68, 384, 92, fill=BG, stroke=MUTED, sw=1.2, rx=6))
    for i, s in enumerate(['id = 42', 'customerId = "c-19"', 'total = 1200', 'status = "paid"']):
        f.append(text(GX + 34, GY + 90 + i * 21, s, size=12, color=INK, anchor="start"))

    f.append(text(GX + 18, GY + 182, "методи = лише перенести рядок", size=11, color=MUTED, anchor="start"))
    f.append(rect(GX + 18, GY + 192, 384, 56, fill=BG, stroke=MUTED, sw=1.2, rx=6))
    f.append(text(GX + 34, GY + 214, "insert()", size=12, color=POS, anchor="start"))
    f.append(text(GX + 150, GY + 214, "update()", size=12, color=POS, anchor="start"))
    f.append(text(GX + 274, GY + 214, "delete()", size=12, color=POS, anchor="start"))
    f.append(text(GX + 34, GY + 236, "→ INSERT / UPDATE / DELETE того рядка", size=10.5, color=MUTED, anchor="start"))

    # немає предметних правил — позначаємо ✗, без лінії поверх тексту
    f.append(rect(GX + 18, GY + 262, 384, 40, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
    f.append(text(GX + 34, GY + 287, "✗", size=15, color=POS, anchor="start", bold=True))
    f.append(text(GX + 56, GY + 287, "canCancel()   taxAmount()", size=12, color=MUTED, anchor="start"))
    f.append(text(GX + GW_ - 18, GY + 287, "ПРАВИЛ НЕМАЄ", size=11.5, color=POS, anchor="end", bold=True))

    # шукач → шлюз (будує)
    f.append(arrow(FX + FW + 6, FY + 52, GX - 6, FY + 52, color=FIELD, sw=2))
    f.append(text((FX + FW + GX) / 2, FY + 40, "будує шлюз", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, 'rdg-anatomy.svg'), W, H, *f)


# ── 2. Межа: чистий шлюз → або Active Record, або Transaction Script над ним ──
def fig_boundary():
    W, H = 1100, 470
    f = []
    f.append(text(W / 2, 32, "Порожня від правил підлога — і два шляхи над нею", size=17, bold=True))

    # ── ЛІВОРУЧ: чистий шлюз ──
    LX, LY, LW, LH = 60, 176, 300, 150
    f.append(rect(LX, LY, LW, LH, fill=HL, stroke=FIELD, sw=2.2, rx=10))
    f.append(text(LX + LW / 2, LY + 30, "Row Data Gateway", size=14, color=INK, bold=True))
    f.append(text(LX + LW / 2, LY + 60, "поля рядка", size=12, color=INK))
    f.append(text(LX + LW / 2, LY + 84, "insert / update / delete", size=12, color=POS))
    f.append(text(LX + LW / 2, LY + 116, "правил немає", size=12.5, color=FIELD, bold=True, italic=True))

    # ── ПРАВОРУЧ ВГОРІ: Active Record ──
    AX, AY, AW, AH = 690, 74, 350, 150
    f.append(rect(AX, AY, AW, AH, fill=FILL, stroke=NEG, sw=2, rx=10))
    f.append(text(AX + AW / 2, AY + 30, "Active Record", size=14, color=INK, bold=True))
    f.append(text(AX + AW / 2, AY + 60, "ті самі поля + доступ", size=12, color=INK))
    f.append(text(AX + AW / 2, AY + 88, "+ canCancel(), taxAmount()", size=12, color=NEG, bold=True))
    f.append(text(AX + AW / 2, AY + 120, "доступ і правила — в одному класі", size=11, color=MUTED, italic=True))

    # ── ПРАВОРУЧ ВНИЗУ: Transaction Script ──
    TX_, TY, TW_, TH = 690, 300, 350, 118
    f.append(rect(TX_, TY, TW_, TH, fill=FILL, stroke=MUTED, sw=1.8, rx=10))
    f.append(text(TX_ + TW_ / 2, TY + 30, "Transaction Script", size=14, color=INK, bold=True))
    f.append(text(TX_ + TW_ / 2, TY + 58, "правило скасування — ТУТ, окремо", size=12, color=INK))
    f.append(text(TX_ + TW_ / 2, TY + 88, "а рядок бере через чистий шлюз", size=11.5, color=MUTED, italic=True))

    # форк-стрілки від шлюзу (підписи — чітко ПОЗА лініями стрілок)
    f.append(arrow(LX + LW + 8, LY + 40, AX - 8, AY + AH - 34, color=NEG, sw=2))
    f.append(mtext((LX + LW + AX) / 2 - 6, 150, ["+ правила В той", "самий об'єкт"],
                   size=11.5, color=NEG, bold=True))

    f.append(arrow(LX + LW + 8, LY + 108, TX_ - 8, TY + 30, color=MUTED, sw=2))
    f.append(mtext((LX + LW + TX_) / 2 - 6, 246, ["лиши чистим,", "правила зверху"],
                   size=11.5, color=MUTED, bold=True))

    # Transaction Script кличе шлюз (назад, нижче)
    f.append(arrow(TX_ - 8, TY + TH - 16, LX + LW + 8, LY + LH - 16, color=FIELD, sw=1.8))
    f.append(text((LX + LW + TX_) / 2, TY + TH + 4, "кличе insert / update", size=11,
                  color=FIELD, bold=True))

    f.append(text(W / 2, 452,
                  "Патерн — це саме нижній вибір: шлюз лишають порожнім навмисно.",
                  size=12.5, color=INK, bold=True))

    render(os.path.join(OUT, 'rdg-boundary.svg'), W, H, *f)


# ── 3. Рядок проти таблиці: одиниця доступу ─────────────────────────────────
def fig_row_vs_table():
    W, H = 1120, 480
    f = []
    f.append(text(W / 2, 32, "Два шлюзи PoEAA: одиниця доступу — рядок чи таблиця",
                  size=17, bold=True))
    f.append(line(560, 60, 560, 452, color=MUTED, sw=1.2, dash="5 5"))

    # ══ ЛІВОРУЧ: Шлюз ТАБЛИЦІ ══
    f.append(text(280, 78, "Шлюз ТАБЛИЦІ даних", size=14, color=NEG, bold=True))
    f.append(text(280, 100, "один екземпляр — на всю таблицю", size=11.5, color=MUTED, italic=True))

    GX, GY, GW_, GH = 120, 120, 320, 118
    f.append(rect(GX, GY, GW_, GH, fill=FILL, stroke=NEG, sw=2, rx=10))
    f.append(text(GX + GW_ / 2, GY + 28, "OrderTableGateway", size=13, color=INK, bold=True))
    f.append(text(GX + GW_ / 2, GY + 56, "find(id)   update(id, дані)", size=12, color=INK))
    f.append(text(GX + GW_ / 2, GY + 80, "delete(id)   — усі беруть ключ", size=12, color=INK))
    f.append(text(GX + GW_ / 2, GY + 104, "методи приймають id рядка", size=10.5, color=MUTED, italic=True))

    # маленька таблиця під ним
    TX, TW, TY = 175, 210, 300
    hh, rh = 24, 26
    f.append(rect(TX, TY, TW, hh, fill=FILL, stroke=LINE, sw=1.4))
    f.append(rect(TX, TY + hh, TW, rh * 3, fill=BG, stroke=LINE, sw=1.4))
    f.append(text(TX + TW / 2, TY + 16, "orders — усі рядки", size=11, color=MUTED, bold=True))
    for i, rid in enumerate((41, 42, 43)):
        f.append(text(TX + TW / 2, TY + hh + 18 + i * rh, "рядок %d" % rid, size=11, color=INK))
        if i:
            f.append(line(TX, TY + hh + i * rh, TX + TW, TY + hh + i * rh, color=MUTED, sw=1))
    f.append(arrow(280, GY + GH + 4, 280, TY - 6, color=MUTED, sw=1.8))
    f.append(text(295, (GY + GH + TY) / 2 + 4, "повертає сирі набори рядків",
                  size=10.5, color=MUTED, anchor="start"))
    f.append(text(280, TY + hh + rh * 3 + 26, "один об'єкт обслуговує ВСІ рядки",
                  size=11.5, color=NEG, bold=True))

    # ══ ПРАВОРУЧ: Шлюз РЯДКА ══
    f.append(text(840, 78, "Шлюз РЯДКА даних", size=14, color=FIELD, bold=True))
    f.append(text(840, 100, "свій екземпляр — на кожен рядок", size=11.5, color=MUTED, italic=True))

    def gw(x, y, rid, cust, tot, st):
        w, h = 230, 84
        out = [rect(x, y, w, h, fill=HL, stroke=FIELD, sw=1.8, rx=8)]
        out.append(text(x + w / 2, y + 22, "OrderGateway · рядок %d" % rid, size=11.5,
                        color=INK, bold=True))
        out.append(text(x + w / 2, y + 44, 'total = %s · status = "%s"' % (tot, st),
                        size=11, color=INK))
        out.append(text(x + w / 2, y + 66, "insert / update / delete", size=11, color=POS))
        return out

    f.extend(gw(725, 122, 41, "c-77", 350, "new"))
    f.extend(gw(725, 218, 42, "c-19", 1200, "paid"))
    f.extend(gw(725, 314, 43, "c-19", 90, "shipped"))
    f.append(text(840, 424, "об'єкт і Є рядок — окремий на кожен",
                  size=11.5, color=FIELD, bold=True))

    render(os.path.join(OUT, 'row-vs-table.svg'), W, H, *f)


# ── 4. Історія: дві спільноти, майже ті самі роки, та сама практика ──────────
def fig_timeline():
    W, H = 1200, 470
    f = []
    f.append(text(W / 2, 34, "Дві спільноти, майже ті самі роки — і одна спільна практика",
                  size=17, bold=True))

    # вісь часу
    AX_Y = 262
    f.append(line(90, AX_Y, 1120, AX_Y, color=LINE, sw=1.8))

    # позиції подій уздовж осі
    xA, xB, xD, xC = 200, 470, 780, 1040   # 2000, 2001, 2002(картка D), 2003
    for x, col in ((xA, NEG), (xB, NEG), (xD, FIELD), (xC, NEG)):
        f.append(line(x, AX_Y - 6, x, AX_Y + 6, color=MUTED, sw=1.4))
        f.append(circle(x, AX_Y, 5, fill=col, stroke=col, sw=1))

    # роки-підписи (2002 позначає сама картка D — щоб не збігтися з її стовпчиком)
    for x, yr in ((xA, "2000"), (xB, "2001"), (xC, "2003")):
        f.append(text(x, AX_Y + 26, yr, size=12.5, color=MUTED, bold=True))

    # підписи доріжок
    f.append(text(70, 72, "світ J2EE / Sun", size=12.5, color=NEG, bold=True, anchor="start"))
    f.append(mtext(70, 348, ["корпоративні", "патерни (Fowler)"], size=12.5, color=FIELD,
                   bold=True, anchor="start"))

    COOL_FILL = "#eaf0fd"

    # ── верхня доріжка (J2EE / Sun) ──
    def top_card(cx, w, y, h, txt):
        x0 = cx - w / 2
        f.append(fitbox(x0, y, w, h, txt, size=12, fill=COOL_FILL, stroke=NEG, sw=1.8,
                        color=INK, rx=9))
        f.append(line(cx, y + h, cx, AX_Y - 5, color=NEG, sw=1.4))

    top_card(xA, 220, 88, 92,
             "2000\nSun J2EE BluePrints\nпросуває DAO і MVC")
    top_card(xB, 254, 72, 112,
             "червень 2001\nCore J2EE Patterns (1-е вид.)\nDAO — патерн у каталозі\nAlur · Crupi · Malks, Sun")
    top_card(xC, 168, 108, 60,
             "травень 2003\n2-е вид. — 21 патерн")

    # ── нижня доріжка (Fowler / PoEAA) ──
    dW, dH = 292, 112
    dx, dy = xD - dW / 2, 312
    f.append(fitbox(dx, dy, dW, dH,
                    "5 листопада 2002\nPoEAA — Martin Fowler й колеги\nRow / Table Data Gateway\nActive Record · Data Mapper",
                    size=12, fill=HL, stroke=FIELD, sw=1.8, color=INK, rx=9))
    f.append(line(xD, AX_Y + 5, xD, dy, color=FIELD, sw=1.4))

    f.append(text(W / 2, 452,
                  "Жодна спільнота не «винайшла» патерн — обидві дали ім'я тому, що вже роками робили руками.",
                  size=12.5, color=INK, bold=True))

    render(os.path.join(OUT, 'hist-timeline.svg'), W, H, *f)


# ── 5. Життєвий цикл: прапорець «чи я вже в базі» керує save() ───────────────
def fig_lifecycle():
    W, H = 1080, 470
    f = []
    f.append(text(W / 2, 30, "Стан «чи я вже в базі» — і що з нього випливає",
                  size=17, bold=True))

    # ── ЛІВОРУЧ: новий (transient) ──
    LX, LY, LW, LH = 90, 155, 300, 140
    f.append(rect(LX, LY, LW, LH, fill=COOL, stroke=NEG, sw=2, rx=12))
    f.append(text(LX + LW / 2, LY + 35, "новий  ·  transient", size=15, color=INK, bold=True))
    f.append(text(LX + LW / 2, LY + 67, "id = null", size=13, color=INK))
    f.append(text(LX + LW / 2, LY + 93, "persisted = false", size=13, color=NEG, bold=True))
    f.append(text(LX + LW / 2, LY + 123, "рядка в базі ще немає", size=11.5, color=MUTED, italic=True))

    # ── ПРАВОРУЧ: у базі (persisted) ──
    RX, RY, RW, RH = 690, 155, 300, 140
    f.append(rect(RX, RY, RW, RH, fill=HL, stroke=FIELD, sw=2, rx=12))
    f.append(text(RX + RW / 2, RY + 35, "у базі  ·  persisted", size=15, color=INK, bold=True))
    f.append(text(RX + RW / 2, RY + 67, "id = 1", size=13, color=INK))
    f.append(text(RX + RW / 2, RY + 93, "persisted = true", size=13, color=FIELD, bold=True))
    f.append(text(RX + RW / 2, RY + 123, "рядок існує, ключ відомий", size=11.5, color=MUTED, italic=True))

    # ── стрілка INSERT: новий → у базі ──
    f.append(arrow(LX + LW + 4, 205, RX - 4, 205, color=POS, sw=2.2))
    f.append(text(W / 2, 192, "save()  →  INSERT", size=12.5, color=POS, bold=True))

    # ── стрілка DELETE: у базі → новий (нижче) ──
    f.append(arrow(RX - 4, 258, LX + LW + 4, 258, color=NEG, sw=2.2))
    f.append(text(W / 2, 278, "delete()  →  DELETE", size=12.5, color=NEG, bold=True))

    # ── петля UPDATE над правою рамкою (self-loop) ──
    f.append('<path d="M 785 %d C 775 102, 905 102, 895 %d" fill="none" '
             'stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>' % (RY, RY, FIELD))
    f.append(text(RX + RW / 2, 92, "save()  →  UPDATE", size=12.5, color=FIELD, bold=True))

    # ── вхід від шукача знизу ──
    f.append(rect(700, 360, 280, 56, fill=FILL, stroke=MUTED, sw=1.6, rx=10))
    f.append(mtext(840, 383, ["OrderFinder._load(row)", "рядок приходить ІЗ бази"],
                   size=11.5, color=MUTED))
    f.append(arrow(840, 358, 840, RY + RH + 2, color=FIELD, sw=1.8))
    f.append(text(858, 332, "одразу persisted = true", size=11, color=FIELD,
                  anchor="start", bold=True))

    # ── підпис під лівою рамкою ──
    f.append(text(LX + LW / 2, 330, "new OrderGateway(...) — стан за замовчуванням",
                  size=11.5, color=MUTED, italic=True))

    # ── підсумок ──
    f.append(text(W / 2, 448,
                  "Прапорець persisted вирішує, чим стане save() — INSERT чи UPDATE.",
                  size=12.5, color=INK, bold=True))

    render(os.path.join(OUT, 'rdg-lifecycle.svg'), W, H, *f)


if __name__ == '__main__':
    fig_anatomy()
    fig_boundary()
    fig_row_vs_table()
    fig_timeline()
    fig_lifecycle()
    print("figures written to", OUT)
