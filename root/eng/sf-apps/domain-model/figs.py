# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GRN = "#eafaf0"    # багатий об'єкт (дані + поведінка)
VOF = "#eaf0fd"    # об'єкт-значення (холодний тон)
GRNBAND = "#f2fbf5"
GREYBAND = "#f5f6f8"


# ── 1. Операція як розмова об'єктів мережею ─────────────────────────────────
def fig_object_web():
    W, H = 1220, 620
    f = []
    f.append(text(W / 2, 32, "Предметна модель: операція — це розмова об'єктів", size=17, bold=True))

    def node(cx, cy, name, role, method, header=GRN, stroke=FIELD, sw=1.9):
        w, h = 184, 80
        x, y = cx - w / 2, cy - h / 2
        f.append(rect(x, y, w, h, fill=BG, stroke=stroke, sw=sw, rx=9))
        f.append(rect(x, y, w, 28, fill=header, stroke=stroke, sw=sw, rx=9))
        f.append(text(cx, y + 19, name, size=13, color=INK, bold=True))
        f.append(text(cx, y + 46, role, size=10.5, color=MUTED))
        f.append(text(cx, y + 66, method, size=11, color=NEG, bold=True))
        return (x, y, w, h)

    # координати вузлів
    Ord = (600, 150)
    Cus = (250, 340)
    Lin = (600, 390)
    Pro = (950, 340)
    Mon = (900, 510)

    # зв'язки мережі (структура) — плавні лінії повз рамки
    f.append(line(520, 182, 330, 306, color=MUTED, sw=1.5))     # Order–Customer
    f.append(line(600, 190, 600, 350, color=MUTED, sw=1.5))     # Order–OrderLine
    f.append(line(688, 158, 862, 308, color=MUTED, sw=1.5))     # Order–Product
    f.append(line(688, 372, 862, 352, color=MUTED, sw=1.5))     # OrderLine–Product
    f.append(line(650, 430, 812, 478, color=MUTED, sw=1.5))     # OrderLine–Money

    # вузли поверх ліній
    node(*Ord, "Order", "стан · життєвий цикл", "place(customer)", stroke=FIELD, sw=2.4)
    node(*Cus, "Customer", "рівень лояльності", "tier()")
    node(*Lin, "OrderLine", "кількість · товар", "subtotal()")
    node(*Pro, "Product", "ціна · залишок", "reserve(qty)")
    node(*Mon, "Money", "об'єкт-значення", "add() · ≥ 0", header=VOF, stroke=NEG)

    # нумеровані бейджі розмови
    def badge(n, x, y):
        f.append(circle(x, y, 13, fill=FIELD, stroke=BG, sw=2))
        f.append(text(x, y + 5, str(n), size=13, color=BG, bold=True))

    badge(1, 415, 244)     # Order → Customer: tier
    badge(2, 782, 362)     # OrderLine → Product: reserve + price
    badge(3, 726, 454)     # OrderLine → Money: build total
    badge(4, 688, 120)     # Order: перевірити інваріант, змінити стан

    # легенда розмови
    lx, ly, lw, lh = 60, 442, 384, 158
    f.append(rect(lx, ly, lw, lh, fill=FILL, stroke=MUTED, sw=1.4, rx=10))
    f.append(text(lx + 16, ly + 26, "Розмова операції «оформити»:", size=12.5, color=INK, anchor="start", bold=True))
    steps = [
        (1, "Order питає Customer про рівень лояльності"),
        (2, "OrderLine просить Product зарезервувати й дати ціну"),
        (3, "OrderLine складає підсумок у Money"),
        (4, "Order перевіряє інваріант і міняє стан"),
    ]
    for i, (n, s) in enumerate(steps):
        ry = ly + 54 + i * 26
        f.append(circle(lx + 24, ry - 4, 9, fill=FIELD, stroke=BG, sw=1.5))
        f.append(text(lx + 24, ry, str(n), size=10.5, color=BG, bold=True))
        f.append(text(lx + 42, ry, s, size=10.5, color=INK, anchor="start"))

    render(os.path.join(OUT, 'object-web.svg'), W, H, *f)


# ── 2. Непроникність для збереження: шар помічників між моделлю й базою ──────
def fig_persistence_ignorance():
    W, H = 1220, 620
    f = []
    f.append(text(W / 2, 30, "Модель тримають чистою — тому між нею й базою стоїть шар помічників",
                  size=16, bold=True))

    # ── смуга 1: предметна модель ──
    f.append(rect(40, 58, 1140, 148, fill=GRNBAND, stroke=FIELD, sw=1.5, rx=12))
    f.append(text(60, 86, "ПРЕДМЕТНА МОДЕЛЬ", size=13.5, color=FIELD, anchor="start", bold=True))
    f.append(text(60, 106, "чисті об'єкти — про базу не знають нічого", size=11, color=MUTED, anchor="start", italic=True))

    def mininode(cx, name):
        w, h = 118, 44
        x, y = cx - w / 2, 168 - h / 2
        f.append(rect(x, y, w, h, fill=BG, stroke=FIELD, sw=1.6, rx=8))
        f.append(text(cx, 164, name, size=11.5, color=INK, bold=True))
        f.append(text(cx, 180, "дані + правила", size=9, color=MUTED))

    for cx in (419, 501):
        pass
    f.append(line(419, 168, 501, 168, color=MUTED, sw=1.4))   # Customer–Order
    f.append(line(619, 168, 701, 168, color=MUTED, sw=1.4))   # Order–OrderLine
    f.append(line(819, 168, 901, 168, color=MUTED, sw=1.4))   # OrderLine–Product
    mininode(360, "Customer")
    mininode(560, "Order")
    mininode(760, "OrderLine")
    mininode(960, "Product")

    # перехід смуга1 → смуга2
    f.append(arrow(300, 208, 300, 246, color=INK, sw=1.8))
    f.append(arrow(920, 208, 920, 246, color=INK, sw=1.8))
    f.append(text(610, 230, "лише крізь помічників — не до бази напряму", size=11, color=MUTED, italic=True))

    # ── смуга 2: помічники ──
    f.append(rect(40, 250, 1140, 150, fill=FILL, stroke=MUTED, sw=1.5, rx=12))
    helpers = [
        (165, "Репозиторій", "колекція об'єктів:\nзнайти · додати"),
        (388, "Мапер даних", "об'єкт ⇄ рядок;\nзнає обидва світи"),
        (611, "Одиниця роботи", "стежить за змінами;\nодин запис разом"),
        (834, "Мапа тотожності", "один об'єкт\nна один рядок"),
        (1057, "Ліниве завантаження", "вантажить частину\nна перший дотик"),
    ]
    for cx, name, role in helpers:
        w, h = 196, 96
        x, y = cx - w / 2, 274
        f.append(rect(x, y, w, h, fill=BG, stroke=FIELD, sw=1.6, rx=9))
        f.append(text(cx, y + 24, name, size=11.5, color=INK, bold=True))
        f.append(fitbox(x + 12, y + 38, w - 24, 46, role, size=10, pad=5,
                        fill=BG, stroke=BG, sw=0, color=MUTED))

    # перехід смуга2 → смуга3
    f.append(arrow(300, 402, 300, 442, color=INK, sw=1.8))
    f.append(arrow(920, 402, 920, 442, color=INK, sw=1.8))
    f.append(text(610, 426, "SQL · рядки · JOIN", size=11, color=MUTED, italic=True))

    # ── смуга 3: база ──
    f.append(rect(40, 444, 1140, 140, fill=GREYBAND, stroke=LINE, sw=1.4, rx=12))
    f.append(text(60, 470, "РЕЛЯЦІЙНА БАЗА — пласкі таблиці, ключі, JOIN", size=13, color=INK, anchor="start", bold=True))

    def table_glyph(cx, name):
        w, h = 156, 60
        x, y = cx - w / 2, 520 - h / 2
        f.append(rect(x, y, w, h, fill=BG, stroke=LINE, sw=1.5, rx=6))
        f.append(rect(x, y, w, 22, fill="#eef1f4", stroke=LINE, sw=1.2, rx=6))
        f.append(text(cx, y + 15, name, size=11, color=INK, bold=True))
        f.append(line(x, y + 41, x + w, y + 41, color=MUTED, sw=1))
        f.append(line(x + w / 2, y + 22, x + w / 2, y + h, color=MUTED, sw=1))

    table_glyph(360, "orders")
    table_glyph(610, "order_lines")
    table_glyph(860, "products")

    render(os.path.join(OUT, 'persistence-ignorance.svg'), W, H, *f)


# ── 3. Проста модель проти багатої ──────────────────────────────────────────
def fig_simple_vs_rich():
    W, H = 1200, 540
    f = []
    f.append(text(W / 2, 30, "Проста модель і багата: що складніша логіка, то далі модель від бази",
                  size=16, bold=True))

    # вісь складності згори
    f.append(text(600, 54, "що більше правил і глибший граф →", size=11.5, color=MUTED, italic=True))
    f.append(arrow(150, 68, 1050, 68, color=INK, sw=2))

    # роздільник
    f.append(line(600, 88, 600, 500, color=MUTED, sw=1.2, dash="6 6"))

    # ══ ЛІВОРУЧ: проста модель ══
    f.append(text(330, 108, "ПРОСТА МОДЕЛЬ", size=14, color=FIELD, bold=True))
    f.append(text(330, 128, "граф ≈ схема бази", size=11, color=MUTED, italic=True))

    simple = [(240, "Order"), (330, "Line"), (420, "Product")]
    for cx, nm in simple:
        f.append(rect(cx - 42, 158, 84, 40, fill=GRN, stroke=FIELD, sw=1.7, rx=8))
        f.append(text(cx, 182, nm, size=10.5, color=INK, bold=True))
    for cx, _ in simple:
        f.append(arrow(cx, 200, cx, 252, color=MUTED, sw=1.5))
        f.append(rect(cx - 42, 254, 84, 50, fill=BG, stroke=LINE, sw=1.4, rx=5))
        f.append(rect(cx - 42, 254, 84, 18, fill="#eef1f4", stroke=LINE, sw=1.1, rx=5))
        f.append(line(cx - 42, 254 + 36, cx + 42, 254 + 36, color=MUTED, sw=0.9))
    f.append(text(375, 228, "1 : 1", size=10, color=FIELD, bold=True))
    f.append(fitbox(178, 372, 304, 74,
                    "активний запис\nоб'єкт сам знає й береже свій рядок — order.save()",
                    size=11.5, pad=10, fill=GRN, stroke=FIELD, sw=1.7, color=INK, rx=10, bold=False))

    # ══ ПРАВОРУЧ: багата модель ══
    f.append(text(880, 108, "БАГАТА МОДЕЛЬ", size=14, color=NEG, bold=True))
    f.append(text(880, 128, "граф розходиться зі схемою", size=11, color=MUTED, italic=True))

    def robj(cx, cy, nm, header=GRN, stroke=FIELD):
        w, h = 96, 38
        f.append(rect(cx - w / 2, cy - h / 2, w, h, fill=header, stroke=stroke, sw=1.7, rx=8))
        f.append(text(cx, cy + 4, nm, size=10.5, color=INK, bold=True))

    # зв'язки графа
    f.append(line(768, 240, 800, 189, color=MUTED, sw=1.4))          # PremiumOrder → Order (успадкування)
    f.append(line(873, 168, 942, 168, color=MUTED, sw=1.4))          # Order – Money
    f.append(line(848, 187, 902, 221, color=MUTED, sw=1.4))          # Order – OrderLine
    robj(825, 168, "Order")
    robj(990, 168, "Money", header=VOF, stroke=NEG)
    robj(735, 240, "PremiumOrder")
    robj(915, 240, "OrderLine")
    f.append(text(690, 214, "успадковує", size=9, color=MUTED, anchor="start", italic=True))

    # мапер
    f.append(rect(705, 296, 350, 34, fill=FILL, stroke=NEG, sw=1.8, rx=8))
    f.append(text(880, 318, "мапер даних", size=12.5, color=INK, bold=True))

    # об'єкти → мапер (4 входи)
    for x0, x1 in [(825, 825), (915, 915), (735, 770), (990, 990)]:
        f.append(arrow(x0, 189 if x0 in (825, 990) else 259, x1, 294, color=MUTED, sw=1.4))
    # мапер → таблиці (2 виходи) — перехрестя 4→2
    f.append(arrow(820, 330, 800, 371, color=MUTED, sw=1.4))
    f.append(arrow(985, 330, 985, 371, color=MUTED, sw=1.4))

    for cx, nm in [(800, "orders"), (985, "products")]:
        f.append(rect(cx - 42, 373, 84, 48, fill=BG, stroke=LINE, sw=1.4, rx=5))
        f.append(rect(cx - 42, 373, 84, 18, fill="#eef1f4", stroke=LINE, sw=1.1, rx=5))
        f.append(text(cx, 386, nm, size=10, color=INK, bold=True))

    f.append(fitbox(715, 458, 330, 62,
                    "мапер даних\nусе знання про базу винесене в окремий шар",
                    size=11.5, pad=10, fill=VOF, stroke=NEG, sw=1.7, color=INK, rx=10))

    render(os.path.join(OUT, 'simple-vs-rich.svg'), W, H, *f)


# ── 4. Родовід ідеї: часова стрічка (hist-вставка) ──────────────────────────
def fig_lineage_timeline():
    W, H = 1280, 580
    f = []
    f.append(text(W / 2, 32, "Родовід предметної моделі: ідея стара, назва молода", size=18, bold=True))
    f.append(text(W / 2, 56,
                  "Об'єкти моделюють предмет ще від Сімули (1967). Назву «предметна модель» дав Фаулер (2002); методологію на ній — Еванс (2003).",
                  size=12, color=MUTED, italic=True))

    AX = 292
    xs = [110, 322, 534, 746, 958, 1170]
    f.append(arrow(72, AX, 1214, AX, color=INK, sw=2))
    f.append(text(1208, AX - 12, "час", size=11, color=MUTED, italic=True, anchor="end"))

    acts  = [FIELD, FIELD, FIELD, FIELD, POS, NEG]
    ups   = [True, False, True, False, True, False]
    years = ["1967", "1980", "1991", "1997", "2002", "2003"]
    titles = ["Сімула 67", "Смолток-80", "ООА/П — три методи", "UML 1.1", "PoEAA", "DDD"]
    whos  = ["Дал · Нюґор", "Кей · Інґаллс · Ґолдберг", "Буч · Рамбо · Джекобсон",
             "«три друзі» · Rational", "Мартін Фаулер", "Ерік Еванс"]
    notes = ["клас = вид речі світу", "об'єкти й повідомлення", "як знайти об'єкти",
             "одна нотація моделі", "НАЗВАНО патерн", "тактика на моделі"]

    bw, bh = 202, 104
    for i, x in enumerate(xs):
        col = acts[i]
        if ups[i]:
            yt = AX - 70 - bh
            f.append(line(x, AX - 8, x, yt + bh, color=col, sw=2))
        else:
            yt = AX + 70
            f.append(line(x, AX + 8, x, yt, color=col, sw=2))
        f.append(circle(x, AX, 8, fill=col, stroke=BG, sw=2))
        bx = x - bw / 2
        f.append(rect(bx, yt, bw, bh, fill=BG, stroke=col, sw=2, rx=10))
        f.append(text(x, yt + 30, years[i], size=19, color=col, bold=True))
        f.append(text(x, yt + 52, titles[i], size=12.5, color=INK, bold=True))
        f.append(text(x, yt + 72, whos[i], size=10.3, color=MUTED))
        f.append(text(x, yt + 92, notes[i], size=10.8, color=col, bold=True))

    ly = 520
    leg = [(FIELD, "ІДЕЯ / практика — визрівала десятиліттями"),
           (POS,   "КАТАЛОГІЗАЦІЯ — Фаулер назвав і впорядкував"),
           (NEG,   "МЕТОДОЛОГІЯ — Еванс збудував тактику")]
    lx = [90, 545, 990]
    for (c, s), xx in zip(leg, lx):
        f.append(rect(xx, ly - 12, 18, 18, fill=c, stroke=c, sw=0, rx=4))
        f.append(text(xx + 26, ly + 3, s, size=11.5, color=INK, anchor="start"))

    render(os.path.join(OUT, 'lineage-timeline.svg'), W, H, *f)


# ── 5. Об'єкт-значення проти сутності (для вставки proj-rich-domain-model) ───
def fig_value_vs_entity():
    W, H = 1180, 470
    f = []

    def box(cx, cy, title, body, header, edge):
        w, h = 190, 76
        x, y = cx - w / 2, cy - h / 2
        f.append(rect(x, y, w, h, fill=BG, stroke=edge, sw=2, rx=10))
        f.append(rect(x, y, w, 28, fill=header, stroke=edge, sw=2, rx=10))
        f.append(text(cx, y + 19, title, size=12.5, color=INK, bold=True))
        f.append(text(cx, y + 56, body, size=12, color=MUTED))

    # роздільник двох світів
    f.append(line(590, 72, 590, 424, color=MUTED, sw=1.2, dash="6 6"))

    # ── ліворуч: об'єкт-значення ──
    f.append(text(300, 104, "ОБ'ЄКТ-ЗНАЧЕННЯ — тотожність за ВМІСТОМ",
                  size=13, color=NEG, bold=True))
    box(200, 205, "Money", "5.00 UAH", VOF, NEG)
    box(415, 205, "Money", "5.00 UAH", VOF, NEG)
    f.append(text(307, 214, "=", size=32, color=FIELD, bold=True))
    f.append(fitbox(110, 300, 390, 104,
                    "рівні за вмістом → взаємозамінні\nнезмінні: особи нема,\nміняти нема чого — лише творити нові",
                    size=12, pad=14, fill=GRNBAND, stroke=FIELD, sw=1.4, color=INK, rx=10))

    # ── праворуч: сутність ──
    f.append(text(882, 104, "СУТНІСТЬ — тотожність за id",
                  size=13, color=FIELD, bold=True))
    box(782, 205, "Order · #A17", "1 × ноутбук", GRN, FIELD)
    box(997, 205, "Order · #B42", "1 × ноутбук", GRN, FIELD)
    f.append(text(889, 214, "≠", size=32, color=POS, bold=True))
    f.append(fitbox(692, 300, 396, 104,
                    "однаковий вміст, різні id → різні замовлення\nмають стан і життєвий цикл:\nстан тече в часі, його стережуть",
                    size=12, pad=14, fill=FILL, stroke=MUTED, sw=1.4, color=INK, rx=10))

    render(os.path.join(OUT, 'value-vs-entity.svg'), W, H, *f,
           title="Дві природи об'єктів моделі: значення і сутність")


# ── 6. Життєвий цикл замовлення: переходи під вартою (для тієї ж вставки) ─────
def fig_order_lifecycle():
    W, H = 1180, 560
    f = []
    f.append(text(W / 2, 52, "стан приватний — зрушити його можна лише методом-командою",
                  size=12.5, color=MUTED, italic=True))

    def state(cx, cy, name, sub, fill=GRN):
        w, h = 172, 64
        x, y = cx - w / 2, cy - h / 2
        f.append(rect(x, y, w, h, fill=fill, stroke=FIELD, sw=2, rx=11))
        f.append(text(cx, cy - 6, name, size=14, color=INK, bold=True))
        f.append(text(cx, cy + 16, sub, size=10.5, color=MUTED))

    D = (232, 214)
    P = (582, 214)
    S = (932, 214)
    C = (582, 436)

    # ── дозволені переходи (суцільні) ──
    f.append(arrow(318, 214, 496, 214))                     # Draft → Placed
    f.append(text(407, 199, "place()", size=11.5, color=INK, bold=True))
    f.append(arrow(668, 214, 846, 214))                     # Placed → Shipped
    f.append(text(757, 199, "ship()", size=11.5, color=INK, bold=True))
    f.append(arrow(582, 246, 582, 404))                     # Placed → Cancelled
    f.append(text(600, 330, "cancel()", size=11.5, color=INK, anchor="start", bold=True))
    f.append(arrow(280, 246, 505, 410))                     # Draft → Cancelled
    f.append(text(322, 352, "cancel()", size=11.5, color=INK, bold=True))

    # ── стани поверх стрілок ──
    state(*D, "Чернетка", "Draft")
    state(*P, "Оформлене", "Placed")
    state(*S, "Відвантажене", "Shipped")
    state(*C, "Скасоване", "Cancelled", fill=FILL)

    # ── заборонені переходи (червона штрихова + ✕) ──
    f.append(line(250, 178, 916, 138, color=POS, sw=1.7, dash="7 5"))   # Draft ⇢ Shipped
    f.append(text(582, 150, "✕", size=17, color=POS, bold=True))
    f.append(line(872, 240, 664, 408, color=POS, sw=1.7, dash="7 5"))   # Shipped ⇢ Cancelled
    f.append(text(772, 322, "✕", size=17, color=POS, bold=True))

    # ── легенда ──
    lx, ly, lw, lh = 60, 476, 720, 66
    f.append(rect(lx, ly, lw, lh, fill=FILL, stroke=MUTED, sw=1.3, rx=10))
    f.append(line(lx + 22, ly + 24, lx + 70, ly + 24, color=LINE, sw=2))
    f.append(text(lx + 82, ly + 28, "дозволений перехід — метод-команда виконується",
                  size=11.5, color=INK, anchor="start"))
    f.append(line(lx + 22, ly + 48, lx + 70, ly + 48, color=POS, sw=1.7, dash="7 5"))
    f.append(text(lx + 82, ly + 52, "заборонений — вартовий усередині методу кидає DomainError",
                  size=11.5, color=INK, anchor="start"))

    render(os.path.join(OUT, 'order-lifecycle.svg'), W, H, *f,
           title="Життєвий цикл замовлення: кожен перехід під вартою")


if __name__ == '__main__':
    fig_object_web()
    fig_persistence_ignorance()
    fig_simple_vs_rich()
    fig_lineage_timeline()
    fig_value_vs_entity()
    fig_order_lifecycle()
    print("figures written to", OUT)
