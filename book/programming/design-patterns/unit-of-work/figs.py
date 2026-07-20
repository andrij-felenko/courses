# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

WARM = "#fdecea"   # заливка «погано»
COOL = "#e8f6ee"   # заливка «добре»
CALM = "#eaf0fd"   # нейтрально-холодне


# ── локальні примітиви ──────────────────────────────────────────────────────
def ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            'stroke="%s" stroke-width="%.1f"/>' % (cx, cy, rx, ry, fill, stroke, sw))


def cylinder(cx, cy, w, h, label="база", fill=CALM):
    """Циліндр-«база даних» із центром (cx,cy)."""
    rx = w / 2.0
    ry = max(7.0, h * 0.13)
    top = cy - h / 2.0
    out = []
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
               'stroke="%s" stroke-width="1.5"/>' % (cx - rx, top, w, h, fill, LINE))
    out.append(ellipse(cx, cy + h / 2.0, rx, ry, fill, LINE))   # низ
    out.append(ellipse(cx, top, rx, ry, fill, LINE))            # верх (поверх усього)
    out.append(text(cx, cy + 5, label, size=13, bold=True))
    return "".join(out)


# ── 1. Писати по дорозі  ⟷  одиниця роботи ──────────────────────────────────
def fig_scattered_vs_uow():
    W, H = 1340, 770
    f = []
    f.append(text(W / 2, 36, "Дві стратегії запису однієї ділової операції",
                  size=19, bold=True))
    f.append(line(670, 62, 670, 720, color=MUTED, sw=1.4, dash="7 6"))

    # ── ЛІВОРУЧ: писати по дорозі ──
    f.append(text(340, 92, "Писати по дорозі", size=17, bold=True, color=POS))

    ops = [
        (150, "INSERT  order",    FILL, LINE, False),
        (208, "INSERT  lines",    FILL, LINE, False),
        (266, "UPDATE  customer", FILL, LINE, False),
        (324, "DELETE  cart",     WARM, POS,  True),
    ]
    dbcx, dbcy = 545, 250
    for cy, label, fill, stroke, bad in ops:
        box, bw, bh = textbox(240, cy, label, size=13.5, bold=True,
                              fill=fill, stroke=stroke, sw=1.8, min_w=232, pad=11)
        f.append(box)
        rx = 240 + bw / 2
        if bad:
            f.append(line(rx, cy, dbcx - 72, cy - 10, color=POS, sw=2.0, dash="6 5"))
            f.append(text((rx + dbcx - 72) / 2, cy - 20, "✗ збій", size=13,
                          bold=True, color=POS))
        else:
            f.append(arrow(rx, cy, dbcx - 72, dbcy - 40 + (cy - 200) * 0.12,
                           color=LINE, sw=1.7))

    f.append(cylinder(dbcx, dbcy, 150, 150, "база"))
    f.append(text(dbcx, dbcy + 96, "кожен запис — окремий рейс", size=11.5,
                  color=MUTED))

    note1, nw, nh = textbox(340, 470,
                            ["перші три зміни вже зафіксовані,",
                             "четверта впала → напівстан:",
                             "замовлення є, а кошик повний"],
                            size=13.5, bold=True, fill=WARM, stroke=POS, sw=1.8,
                            min_w=440, pad=14)
    f.append(note1)

    # ── ПРАВОРУЧ: одиниця роботи ──
    f.append(text(1000, 92, "Одиниця роботи", size=17, bold=True, color=FIELD))

    lists = [
        (155, ["+ New", "order, lines"]),
        (245, ["~ Dirty", "customer"]),
        (335, ["− Removed", "cart"]),
    ]
    commit_cx, commit_cy = 1075, 245
    for cy, lines in lists:
        box, bw, bh = textbox(835, cy, lines, size=13, bold=True,
                              fill=COOL, stroke=FIELD, sw=1.7, min_w=176, pad=11)
        f.append(box)
        f.append(arrow(835 + bw / 2, cy, commit_cx - 128, commit_cy + (cy - 245) * 0.20,
                       color=LINE, sw=1.6))

    cbox, cw, ch = textbox(commit_cx, commit_cy,
                           ["BEGIN", "INSERT · UPDATE · DELETE", "COMMIT"],
                           size=13, bold=True, fill=CALM, stroke=NEG, sw=2.0,
                           min_w=248, pad=13)
    f.append(cbox)

    dbcx2 = 1268
    f.append(arrow(commit_cx + cw / 2, commit_cy, dbcx2 - 58, commit_cy,
                   color=LINE, sw=1.7))
    f.append(cylinder(dbcx2, commit_cy, 104, 140, "база"))

    note2, n2w, n2h = textbox(1000, 470,
                              ["збій будь-де → ROLLBACK,",
                               "база не бачить жодної зміни"],
                              size=13.5, bold=True, fill=COOL, stroke=FIELD, sw=1.8,
                              min_w=420, pad=14)
    f.append(note2)
    f.append(text(1000, 540, "один рейс замість багатьох · усе або нічого",
                  size=12.5, color=MUTED))

    render(os.path.join(IMG, "scattered-vs-uow.svg"), W, H, *f)


# ── 2. Порядок запису диктують зовнішні ключі ───────────────────────────────
def fig_write_ordering():
    W, H = 1300, 700
    f = []
    f.append(text(W / 2, 36, "Порядок запису диктують зовнішні ключі",
                  size=19, bold=True))

    cx = 650
    rows = [(150, "Customer"), (330, "Order"), (510, "OrderLine")]
    boxw = 230
    ys = {}
    for cy, name in rows:
        box, bw, bh = textbox(cx, cy, name, size=15, bold=True,
                              fill=CALM, stroke=LINE, sw=1.8, min_w=boxw, pad=14)
        f.append(box)
        ys[name] = (cy, bh)

    # стрілки «посилається на» — від дитини вгору до батька
    def ref_arrow(child, parent):
        cyC, hC = ys[child]
        cyP, hP = ys[parent]
        y1 = cyC - hC / 2
        y2 = cyP + hP / 2 + 6
        f.append(arrow(cx, y1, cx, y2, color=MUTED, sw=1.7))
        f.append(text(cx + boxw / 2 + 20, (y1 + y2) / 2 + 4, "посилається на",
                      size=12, color=MUTED, anchor="start"))

    ref_arrow("OrderLine", "Order")
    ref_arrow("Order", "Customer")

    # ── ліворуч: вставка згори вниз ──
    f.append(text(235, 96, "Вставка — згори вниз", size=15, bold=True, color=FIELD))
    f.append(arrow(150, 130, 150, 545, color=FIELD, sw=3.0))
    ins = [(150, "1", "Customer"), (330, "2", "Order"), (510, "3", "OrderLine")]
    for cy, n, name in ins:
        f.append(text(200, cy + 5, n + " · " + name, size=13.5, bold=True,
                      color=INK, anchor="start"))
    f.append(text(235, 585, "того, на кого посилаються, — першим", size=11.5,
                  color=MUTED))

    # ── праворуч: видалення знизу вгору ──
    f.append(text(1065, 96, "Видалення — знизу вгору", size=15, bold=True, color=NEG))
    f.append(arrow(1150, 545, 1150, 130, color=NEG, sw=3.0))
    dele = [(510, "1", "OrderLine"), (330, "2", "Order"), (150, "3", "Customer")]
    for cy, n, name in dele:
        f.append(text(1100, cy + 5, n + " · " + name, size=13.5, bold=True,
                      color=INK, anchor="end"))
    f.append(text(1065, 585, "того, хто посилається, — першим", size=11.5,
                  color=MUTED))

    note, nw, nh = textbox(W / 2, 645,
                           ["наївний порядок вставив би OrderLine поперед Order — "
                            "база відкине його: посилання на неіснуючий рядок"],
                           size=13.5, bold=True, fill=WARM, stroke=POS, sw=1.8,
                           min_w=760, pad=13)
    f.append(note)

    render(os.path.join(IMG, "write-ordering.svg"), W, H, *f)


# ── 3. Життя одиниці роботи = один запит ────────────────────────────────────
def fig_lifecycle():
    W, H = 1340, 430
    f = []
    f.append(text(W / 2, 36, "Одиниця роботи живе рівно один запит",
                  size=19, bold=True))

    phases = [
        (285, ["Народження", "порожня UoW"], CALM, LINE),
        (670, ["Робота", "+ new · ~ dirty · − removed", "зміни збираються в пам'яті"], FILL, LINE),
        (1055, ["Фіксація", "commit — одна транзакція", "або rollback — нічого не лягло"], COOL, FIELD),
    ]
    cy = 150
    xs = []
    for pcx, lines, fill, stroke in phases:
        box, bw, bh = textbox(pcx, cy, lines, size=13.5, bold=True,
                              fill=fill, stroke=stroke, sw=1.8, min_w=300, pad=14)
        f.append(box)
        xs.append((pcx, bh))

    # вісь часу
    ty = 268
    f.append(arrow(120, ty, 1240, ty, color=LINE, sw=1.8))
    f.append(text(150, ty - 12, "час", size=12, color=MUTED, anchor="start"))
    f.append(text(1210, ty - 12, "UoW викидається", size=12, color=MUTED, anchor="end"))

    # тики від фаз до осі
    for pcx, bh in xs:
        f.append(line(pcx, cy + bh / 2, pcx, ty - 6, color=MUTED, sw=1.3, dash="4 4"))

    # дужка транзакції від народження до фіксації
    by = 320
    x1, x2 = 285, 1055
    f.append(line(x1, ty + 8, x1, by, color=NEG, sw=1.6))
    f.append(line(x2, ty + 8, x2, by, color=NEG, sw=1.6))
    f.append(line(x1, by, x2, by, color=NEG, sw=1.6))
    f.append(text((x1 + x2) / 2, by + 24, "межа транзакції = життя одиниці роботи",
                  size=13.5, bold=True, color=NEG))

    render(os.path.join(IMG, "lifecycle.svg"), W, H, *f)


# ── 4. Родовід: реалізація випередила назву (для hist-вставки) ───────────────
def fig_genealogy():
    W, H = 1380, 560
    f = []
    f.append(text(W / 2, 34, "Родовід одиниці роботи: реалізація випередила назву",
                  size=19, bold=True))

    # шкала років → x
    def X(year):
        return 130 + (year - 1993) * 72.5

    axis_y = 340
    f.append(arrow(100, axis_y, 1320, axis_y, color=LINE, sw=1.8))
    f.append(text(1315, axis_y - 12, "час", size=12, color=MUTED, anchor="end"))

    # тики на осі під кожен рік події (роки — у самих рамках, тож без підписів)
    for yr in (1994, 1996, 2001, 2002, 2004, 2006, 2008):
        x = X(yr)
        f.append(line(x, axis_y - 6, x, axis_y + 6, color=MUTED, sw=1.4))

    def stem(x, box_cy, box_h, up=True):
        if up:
            f.append(line(x, box_cy + box_h / 2, x, axis_y - 6, color=MUTED, sw=1.2, dash="4 4"))
        else:
            f.append(line(x, box_cy - box_h / 2, x, axis_y + 6, color=MUTED, sw=1.2, dash="4 4"))

    # ── над віссю: гілка «одиниця роботи» (сесія / контекст) ──
    # витік — TopLink 1994, підкреслено
    xt = X(1994)
    tb, tw, th = textbox(xt + 62, 172,
                         ["TopLink «UnitOfWork»",
                          "1994 Smalltalk · 1996 Java",
                          "The Object People, Оттава"],
                         size=13, bold=True, fill=COOL, stroke=FIELD, sw=2.2,
                         min_w=252, pad=12)
    f.append(tb)
    stem(xt + 62, 172, th, up=True)

    hb, hw, hh = textbox(X(2001), 148, ["Hibernate", "Session · 2001"],
                         size=13, bold=True, fill=CALM, stroke=FIELD, sw=1.8,
                         min_w=150, pad=11)
    f.append(hb)
    stem(X(2001), 148, hh, up=True)

    pb, pw, ph = textbox(X(2006), 138,
                         ["JPA EntityManager · 2006", "SQLAlchemy Session · 2006"],
                         size=13, bold=True, fill=CALM, stroke=FIELD, sw=1.8,
                         min_w=234, pad=11)
    f.append(pb)
    stem(X(2006), 138, ph, up=True)

    eb, ew, eh = textbox(X(2008) + 4, 246, ["Entity Framework", "DbContext · 2008"],
                         size=13, bold=True, fill=CALM, stroke=FIELD, sw=1.8,
                         min_w=170, pad=11)
    f.append(eb)
    stem(X(2008) + 4, 246, eh, up=True)

    f.append(text(X(2001) + 30, 96, "гілка «одиниця роботи»: сесія · контекст",
                  size=12.5, bold=True, color=FIELD, anchor="start"))

    # ── подія називання на осі: Фаулер, 2002 ──
    xn = X(2002)
    f.append(circle(xn, axis_y, 10, fill=WARM, stroke=POS, sw=2.6))
    nb, nw, nh = textbox(xn, 262,
                         ["Фаулер називає патерн", "«Unit of Work» — PoEAA · 2002"],
                         size=13, bold=True, fill=FILL, stroke=POS, sw=2.0,
                         min_w=250, pad=11)
    f.append(nb)
    f.append(line(xn, 262 + nh / 2, xn, axis_y - 11, color=POS, sw=1.3, dash="4 4"))

    # ── під віссю: 8-річна прогалина між реалізацією й назвою ──
    gap_y = 392
    f.append(line(xt, axis_y + 6, xt, gap_y, color=MUTED, sw=1.1, dash="3 4"))
    f.append(line(xn, axis_y + 11, xn, gap_y, color=MUTED, sw=1.1, dash="3 4"))
    xm = (xt + xn) / 2
    f.append(arrow(xm - 8, gap_y, xt, gap_y, color=POS, sw=1.6))
    f.append(arrow(xm + 8, gap_y, xn, gap_y, color=POS, sw=1.6))
    f.append(text(xm, gap_y - 8, "8 років", size=13.5, bold=True, color=POS))
    f.append(text(xm, gap_y + 18, "працююча реалізація випередила назву",
                  size=12, color=MUTED))

    # ── під віссю: гілка Active Record, що свідомо відмовилась ──
    rb, rw, rh = textbox(X(2004) + 40, 470,
                         ["Rails ActiveRecord · 2004",
                          "Django — теж негайний save",
                          "без сесії · без одиниці роботи"],
                         size=13, bold=True, fill=WARM, stroke=POS, sw=2.0,
                         min_w=272, pad=12)
    f.append(rb)
    stem(X(2004) + 40, 470, rh, up=False)
    f.append(text(X(2004) + 40, 470 + rh / 2 + 22,
                  "інша гілка: зберігати одразу, кожен save — окремий рейс",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "genealogy.svg"), W, H, *f)


# ── 5. Згортання: що писати — вирішують лише кінці (math-вставка) ─────────────
def fig_net_endpoints():
    W, H = 1220, 710
    f = []
    f.append(text(W / 2, 38, "Що писати — вирішують лише кінці, а не шлях",
                  size=19, bold=True))

    col1x, col2x = 500, 830
    row1y, row2y = 255, 420

    f.append(text((col1x + col2x) / 2, 92, "наприкінці операції…",
                  size=13.5, bold=True, color=MUTED))
    f.append(text(col1x, 120, "рядка НЕМА", size=14, bold=True))
    f.append(text(col2x, 120, "рядок Є", size=14, bold=True))

    f.append(text(150, row1y - 8, "на початку", size=13, color=MUTED))
    f.append(text(150, row1y + 12, "рядка НЕМА", size=14, bold=True))
    f.append(text(150, row2y - 8, "на початку", size=13, color=MUTED))
    f.append(text(150, row2y + 12, "рядок Є", size=14, bold=True))

    cells = [
        (col1x, row1y, ["нічого", "new + removed"], CALM, MUTED),
        (col2x, row1y, ["INSERT", "new (+ dirty вливається)"], COOL, FIELD),
        (col1x, row2y, ["DELETE", "removed (dirty — марно)"], "#eaf0fd", NEG),
        (col2x, row2y, ["UPDATE — якщо змінилось", "інакше нічого"], CALM, LINE),
    ]
    for cx, cy, lines, fill, stroke in cells:
        box, bw, bh = textbox(cx, cy, lines, size=14, bold=True,
                              fill=fill, stroke=stroke, sw=2.0, min_w=300, pad=15)
        f.append(box)

    f.append(line(120, 525, W - 120, 525, color=MUTED, sw=1.2, dash="5 5"))
    f.append(text(W / 2, 558,
                  "будь-який шлях реєстрацій між тими самими кінцями дає той самий рядок",
                  size=14, bold=True))

    paths = [
        (320, "new · dirty · dirty", "INSERT", FIELD),
        (620, "new · removed", "нічого", MUTED),
        (920, "dirty · removed", "DELETE", NEG),
    ]
    for px, seq, res, col in paths:
        pb, pw, ph = textbox(px, 612, seq, size=12.5, fill=FILL, stroke=LINE,
                             sw=1.4, min_w=214, pad=10)
        f.append(pb)
        f.append(arrow(px, 634, px, 662, color=col, sw=1.9))
        f.append(text(px, 686, res, size=13.5, bold=True, color=col))

    render(os.path.join(IMG, "net-endpoints.svg"), W, H, *f)


# ── 6. Цикл FK: конденсація завжди ациклічна (math-вставка) ───────────────────
def fig_scc_condensation():
    W, H = 1300, 650
    f = []
    f.append(text(W / 2, 38, "Цикл зовнішніх ключів: конденсація завжди ациклічна",
                  size=19, bold=True))

    # ── ліворуч: граф із циклом ──
    f.append(text(390, 92, "Граф зовнішніх ключів", size=15, bold=True))
    boxw = 160
    cust = textbox(390, 175, "Customer", size=14, bold=True, fill=CALM,
                   stroke=LINE, sw=1.8, min_w=boxw, pad=13)
    ordr = textbox(390, 345, "Order", size=14, bold=True, fill=CALM,
                   stroke=LINE, sw=1.8, min_w=boxw, pad=13)
    olin = textbox(390, 515, "OrderLine", size=14, bold=True, fill=CALM,
                   stroke=LINE, sw=1.8, min_w=boxw, pad=13)
    f.append(cust[0]); f.append(ordr[0]); f.append(olin[0])

    # 2-цикл Customer ⇄ Order у проміжку між боксами
    f.append(arrow(362, 312, 362, 210, color=POS, sw=2.0))   # Order → Customer
    f.append(text(348, 262, "посилається на", size=11.5, color=MUTED, anchor="end"))
    f.append(arrow(418, 210, 418, 312, color=NEG, sw=2.0))   # Customer → Order
    f.append(text(432, 262, "last_order", size=11.5, color=MUTED, anchor="start"))
    f.append(arrow(390, 482, 390, 380, color=LINE, sw=1.8))  # OrderLine → Order
    f.append(text(404, 432, "посилається на", size=11.5, color=MUTED, anchor="start"))
    f.append(text(390, 585, "Customer ⇄ Order — цикл: лінійного порядку немає",
                  size=12.5, bold=True, color=POS))

    # ── стрілка конденсації ──
    f.append(arrow(605, 345, 735, 345, color=LINE, sw=2.4))
    f.append(text(670, 327, "конденсація", size=12.5, bold=True, color=MUTED))

    # ── праворуч: конденсація-DAG ──
    f.append(text(1000, 92, "Конденсація — DAG", size=15, bold=True, color=FIELD))
    scc, sw_, sh_ = textbox(1000, 215, ["SCC", "{ Customer, Order }"], size=13.5,
                            bold=True, fill=COOL, stroke=FIELD, sw=2.4,
                            min_w=270, pad=16, rx=16)
    f.append(scc)
    ol2 = textbox(1000, 385, "OrderLine", size=14, bold=True, fill=CALM,
                  stroke=LINE, sw=1.8, min_w=boxw, pad=13)
    f.append(ol2[0])
    f.append(arrow(1000, 352, 1000, 255, color=LINE, sw=1.8))
    f.append(text(1120, 320, "посилається на", size=11.5, color=MUTED, anchor="start"))

    note, nw, nh = textbox(1000, 520,
                           ["усередині SCC порядку немає — два виходи:",
                            "• відкласти перевірку FK до COMMIT",
                            "• два проходи: INSERT з NULL → UPDATE"],
                           size=12.5, bold=True, fill=FILL, stroke=LINE,
                           sw=1.6, min_w=400, pad=14)
    f.append(note)

    render(os.path.join(IMG, "scc-condensation.svg"), W, H, *f)


# ── 7. Атомарність: зовні видно лише кінці (math-вставка) ─────────────────────
def fig_commit_trajectory():
    W, H = 1300, 460
    f = []
    f.append(text(W / 2, 38, "Атомарність: зовні видно лише кінці, не шлях",
                  size=19, bold=True))

    base, bw, bh = textbox(215, 205, ["База", "стан-початок"], size=14, bold=True,
                           fill=CALM, stroke=LINE, sw=1.9, min_w=190, pad=15)
    targ, tw, th = textbox(1085, 205, ["База", "стан-ціль"], size=14, bold=True,
                           fill=COOL, stroke=FIELD, sw=1.9, min_w=190, pad=15)
    f.append(base); f.append(targ)

    # проміжна зона — шлях, якого ніхто не бачить
    f.append(rect(430, 150, 440, 130, fill="#f6f7f9", stroke=MUTED, sw=1.4, rx=10))
    f.append(mtext(650, 200, ["проміжні стани", "можуть порушувати посилкову цілість"],
                   size=12.5, color=MUTED, bold=True))
    f.append(text(650, 258, "ззовні транзакції їх не видно", size=12,
                  color=MUTED, italic=True))
    for i in range(5):
        f.append(circle(478 + i * 86, 232, 3.4, fill=MUTED, stroke=MUTED))

    # COMMIT — стрибок понад шляхом
    f.append(arrow(320, 118, 985, 118, color=FIELD, sw=2.6))
    f.append(text(650, 104, "COMMIT — усе або нічого", size=14, bold=True, color=FIELD))

    # ROLLBACK — назад у початок
    f.append(arrow(865, 320, 320, 320, color=POS, sw=2.0))
    f.append(text(590, 342, "ROLLBACK → стан-початок", size=13, bold=True, color=POS))

    triples = [
        (270, ["згортання:", "кінці вирішують ЩО"]),
        (650, ["відкладені перевірки:", "кінці — КОЛИ цілість"]),
        (1030, ["атомарність:", "кінці — усе, що ВИДНО"]),
    ]
    for tx, lines in triples:
        f.append(mtext(tx, 405, lines, size=12.5, color=INK, bold=True))

    render(os.path.join(IMG, "commit-trajectory.svg"), W, H, *f)


# ── 8. Що діється всередині зливу (для proj-вставки) ─────────────────────────
def fig_flush_pipeline():
    W, H = 1500, 540
    f = []
    f.append(text(W / 2, 34, "Що діється всередині зливу", size=19, bold=True))

    cy = 190
    stages = [
        (190, ["Вхід", "карта тотожності + знімки", "списки new · removed"], CALM, LINE),
        (525, ["1 · Звірка", "поле ≠ знімок", "→ dirty"], FILL, LINE),
        (825, ["2 · Топосорт", "батьки перед дітьми", "за зовнішніми ключами"], FILL, LINE),
        (1140, ["3 · Виконати", "INSERT призначає ключ", "UPDATE · DELETE"], COOL, FIELD),
    ]
    boxes = []
    for pcx, lines, fill, stroke in stages:
        box, bw, bh = textbox(pcx, cy, lines, size=13, bold=True,
                              fill=fill, stroke=stroke, sw=1.8, min_w=248, pad=13)
        f.append(box)
        boxes.append((pcx, bw, bh))

    # стрілки між стадіями
    for i in range(len(boxes) - 1):
        cx1, bw1, _ = boxes[i]
        cx2, bw2, _ = boxes[i + 1]
        f.append(arrow(cx1 + bw1 / 2, cy, cx2 - bw2 / 2 - 4, cy, color=LINE, sw=1.8))

    # база наприкінці
    lastcx, lastbw, _ = boxes[-1]
    dbcx = 1430
    f.append(arrow(lastcx + lastbw / 2, cy, dbcx - 58, cy, color=LINE, sw=1.8))
    f.append(cylinder(dbcx, cy, 104, 126, "база"))
    f.append(text(dbcx, cy + 82, "в транзакції — ще не commit", size=11, color=MUTED))

    # зворотна стрілка: переснімкувати (D → A)
    ry = 332
    ax, _, abh = boxes[0]
    dx, _, dbh = boxes[-1]
    f.append(line(dx, cy + dbh / 2, dx, ry, color=FIELD, sw=1.6, dash="6 5"))
    f.append(line(dx, ry, ax, ry, color=FIELD, sw=1.6, dash="6 5"))
    f.append(arrow(ax, ry, ax, cy + abh / 2, color=FIELD, sw=1.6))
    f.append(text((ax + dx) / 2, ry - 11,
                  "4 · переснімкувати — скинути базу «брудності»",
                  size=13, bold=True, color=FIELD))

    # нижній підпис
    cap, cw, ch = textbox(W / 2, 462,
                          ["commit = злив + завершити транзакцію     ·     "
                           "збій → rollback і скинути карту та знімки"],
                          size=13.5, bold=True, fill=WARM, stroke=POS, sw=1.8,
                          min_w=860, pad=13)
    f.append(cap)

    render(os.path.join(IMG, "flush-pipeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_scattered_vs_uow()
    fig_write_ordering()
    fig_lifecycle()
    fig_genealogy()
    fig_net_endpoints()
    fig_scc_condensation()
    fig_commit_trajectory()
    fig_flush_pipeline()
    print("OK: figs written to", IMG)
