# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def dashrect(x, y, w, h, stroke=MUTED, sw=1.6, rx=16, fill=BG, dash="6 5"):
    """Прямокутник із пунктирною рамкою (svgkit.rect суцільний)."""
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" fill="%s" '
            'stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>'
            % (x, y, w, h, rx, fill, stroke, sw, dash))


# ── Фігура 1: один роздутий Product проти трьох контекстів ────────────────────
def fig_one_model_vs_contexts():
    W, H = 1000, 620
    frags = []

    # ── ЛІВОРУЧ: один роздутий Product ──────────────────────────────────────
    lx = 60
    top = 90
    frags.append(text(lx + 130, top - 26, "Один Product на все",
                      size=17, bold=True, color=POS))

    # стовпчик полів (частина порожня)
    fields = [
        ("title", False), ("description", False), ("photos", False),
        ("reviews", False), ("weightKg", True), ("shelf", True),
        ("stock", True), ("fragile", True), ("canLayFlat", True),
        ("...ще 60 полів", True),
    ]
    fw, fh, gap = 210, 30, 6
    box_x = lx
    col_top = top
    # рамка-контейнер класу
    total_h = len(fields) * (fh + gap) + 16
    frags.append(rect(box_x - 12, col_top - 12, fw + 24, total_h + 40,
                      fill="#fdf0ee", stroke=POS, sw=2.4, rx=14))
    frags.append(text(box_x + fw / 2, col_top + total_h + 18,
                      "половина полів завжди порожня", size=12, color=MUTED))
    for i, (name, empty) in enumerate(fields):
        y = col_top + i * (fh + gap)
        fill = "#fbe4e0" if empty else "#ffffff"
        note = "  (порожнє)" if empty else ""
        frags.append(rect(box_x, y, fw, fh, fill=fill, stroke=MUTED, sw=1.2, rx=5))
        frags.append(text(box_x + 10, y + fh / 2 + 5, name + note,
                          size=12, color=INK, anchor="start"))

    # два правила збоку, що конфліктують
    r1x = box_x + fw + 40
    ry1 = col_top + 40
    b1 = fitbox(r1x, ry1, 150, 46, "правило каталогу:\nбез опису — не публікувати",
                size=11, fill="#eef4ff", stroke=NEG, sw=1.6)
    frags.append(b1)
    ry2 = ry1 + 150
    b2 = fitbox(r1x, ry2, 150, 46, "правило складу:\nбез ваги — не прийняти",
                size=11, fill="#eef4ff", stroke=NEG, sw=1.6)
    frags.append(b2)
    # лінія конфлікту між правилами — з розривом під напис (щоб не перетинала текст)
    lxm = r1x + 75
    mid = (ry1 + 46 + ry2) / 2
    frags.append(line(lxm, ry1 + 46, lxm, mid - 12, color=POS, sw=1.8, dash="5 4"))
    frags.append(line(lxm, mid + 12, lxm, ry2, color=POS, sw=1.8, dash="5 4"))
    # напис збоку від лінії, у розриві — жодна лінія його не перетинає
    frags.append(text(lxm + 8, mid + 4, "конфлікт", size=11, bold=True,
                      color=POS, anchor="start"))

    # ── ПРАВОРУЧ: три контексти ─────────────────────────────────────────────
    contexts = [
        ("Каталог", ["title", "description", "photos"],
         "без фото — товару немає", 640, 70),
        ("Склад", ["sku", "weightKg", "shelf"],
         "без ваги — не прийняти", 640, 270),
        ("Доставка", ["volume", "fragile", "canLayFlat"],
         "крихке — окрема коробка", 640, 470),
    ]
    cw, ch = 300, 150
    for title, flds, rule, cx, cy in contexts:
        frags.append(rect(cx, cy, cw, ch, fill="#eef7f0", stroke=FIELD, sw=2.2, rx=14))
        frags.append(text(cx + cw / 2, cy - 12,
                          "Контекст «%s»" % title, size=15, bold=True, color=FIELD))
        frags.append(text(cx + 16, cy + 26, "Product {", size=12, bold=True,
                          color=INK, anchor="start"))
        for j, f in enumerate(flds):
            frags.append(text(cx + 34, cy + 26 + (j + 1) * 22, f,
                              size=12, color=INK, anchor="start"))
        frags.append(text(cx + 16, cy + 26 + (len(flds) + 1) * 22, "}",
                          size=12, bold=True, color=INK, anchor="start"))
        # єдине правило контексту
        frags.append(text(cx + cw / 2, cy + ch - 10, rule,
                          size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, 'one-model-vs-contexts.svg'), W, H, *frags,
           title="Один клас на все проти моделі на контекст")


# ── Фігура 2: три різні межі, що не зобов'язані збігатися ─────────────────────
def fig_three_boundaries():
    W, H = 960, 560
    frags = []

    # Верхній ряд: типовий випадок — три межі збігаються
    frags.append(text(W / 2, 62, "Часто збігаються — і це зручно",
                      size=15, bold=True, color=FIELD))
    # три вкладені рамки навколо однієї команди
    cx = 250
    # зовнішня: розгортання
    frags.append(dashrect(cx - 150, 90, 300, 130))
    frags.append(text(cx, 108, "розгортання (сервіс + база)", size=11, color=MUTED))
    # середня: контекст
    frags.append(rect(cx - 110, 126, 220, 70, fill="#eef7f0", stroke=FIELD, sw=2.2, rx=12))
    frags.append(text(cx, 142, "контекст (одна модель)", size=11, bold=True, color=FIELD))
    # внутрішня: команда
    tb = fitbox(cx - 70, 155, 140, 34, "команда (люди)", size=11,
                fill="#eef4ff", stroke=NEG, sw=1.8)
    frags.append(tb)

    frags.append(text(cx, 250, "одна команда — один контекст — один сервіс",
                      size=12, color=INK))

    # Нижній ряд: розходяться
    frags.append(text(W / 2, 320, "Але не зобов'язані — межі різні",
                      size=15, bold=True, color=POS))

    # Випадок А: одна команда, два контексти
    ax = 210
    frags.append(rect(ax - 150, 352, 300, 150, fill="#eef4ff", stroke=NEG, sw=2.0, rx=16))
    frags.append(text(ax, 372, "одна команда", size=12, bold=True, color=NEG))
    c1 = fitbox(ax - 130, 392, 120, 90, "контекст\nКаталог", size=12,
                fill="#eef7f0", stroke=FIELD, sw=2.0)
    frags.append(c1)
    c2 = fitbox(ax + 10, 392, 120, 90, "контекст\nПромо", size=12,
                fill="#eef7f0", stroke=FIELD, sw=2.0)
    frags.append(c2)
    frags.append(text(ax, 520, "межа команди ≠ межа контексту",
                      size=11, italic=True, color=MUTED))

    # Випадок Б: один контекст як модуль у спільному процесі
    bx = 700
    frags.append(dashrect(bx - 150, 352, 300, 150))
    frags.append(text(bx, 372, "один процес (моноліт)", size=12, bold=True, color=MUTED))
    m1 = fitbox(bx - 130, 392, 120, 90, "контекст\nЗамовлення", size=12,
                fill="#eef7f0", stroke=FIELD, sw=2.0)
    frags.append(m1)
    m2 = fitbox(bx + 10, 392, 120, 90, "контекст\nСклад", size=12,
                fill="#eef7f0", stroke=FIELD, sw=2.0)
    frags.append(m2)
    frags.append(text(bx, 520, "два контексти — одне розгортання",
                      size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, 'three-boundaries.svg'), W, H, *frags,
           title="Контекст, команда, розгортання — три різні межі")


# ── Фігура 3 (для proj): сам рух рефакторингу — розріз надвоє з перекладачем ──
def fig_refactor_move():
    W, H = 1040, 560
    frags = []

    # ── ЛІВОРУЧ: один спільний User зі «словом-вилкою» посередині ────────────
    lx = 60
    top = 96
    fw, fh, gap = 200, 28, 6
    frags.append(text(lx + fw / 2, top - 30, "ДО: спільний User",
                      size=16, bold=True, color=POS))
    fields = [
        ("source  ← вилка!", "fork"),
        ("stage", "sales"),
        ("probability", "sales"),
        ("owner", "sales"),
        ("taxId", "bill"),
        ("creditLimit", "bill"),
        ("iban", "bill"),
        ("...ще 30 полів", "null"),
    ]
    total_h = len(fields) * (fh + gap) + 12
    frags.append(rect(lx - 12, top - 12, fw + 24, total_h + 46,
                      fill="#fdf0ee", stroke=POS, sw=2.4, rx=14))
    frags.append(text(lx + fw / 2, top + total_h + 22,
                      "if source == ... — валідація вгадує світ",
                      size=11, italic=True, color=MUTED))
    palette = {"fork": "#f7dccf", "sales": "#eaf0fd",
               "bill": "#eef7f0", "null": "#f0f0f0"}
    for i, (name, kind) in enumerate(fields):
        y = top + i * (fh + gap)
        frags.append(rect(lx, y, fw, fh, fill=palette[kind], stroke=MUTED, sw=1.2, rx=5))
        frags.append(text(lx + 10, y + fh / 2 + 5, name,
                          size=11, color=INK, anchor="start"))

    # ── СТРІЛКА-перехід із підписом (підпис ПІД стрілкою, не на ній) ─────────
    ax0 = lx + fw + 30
    ax1 = ax0 + 150
    ay = top + total_h / 2
    frags.append(arrow(ax0, ay, ax1, ay, color=INK, sw=2.2))
    frags.append(text((ax0 + ax1) / 2, ay - 40, "розрізати",
                      size=13, bold=True, color=INK))
    frags.append(text((ax0 + ax1) / 2, ay - 20, "по слову-вилці",
                      size=12, color=MUTED))
    frags.append(text((ax0 + ax1) / 2, ay + 34, "+ перекладач",
                      size=12, color=FIELD))
    frags.append(text((ax0 + ax1) / 2, ay + 52, "на межі",
                      size=12, color=FIELD))

    # ── ПРАВОРУЧ: дві чисті моделі + стіна + перекладач у стіні ──────────────
    rx0 = ax1 + 46
    bw, bh = 210, 150
    # Продажі
    sales_y = 84
    frags.append(rect(rx0, sales_y, bw, bh, fill="#eef4ff", stroke=NEG, sw=2.2, rx=14))
    frags.append(text(rx0 + bw / 2, sales_y - 12,
                      "Контекст «Продажі»", size=14, bold=True, color=NEG))
    frags.append(text(rx0 + 16, sales_y + 28, "Lead {", size=12, bold=True,
                      color=INK, anchor="start"))
    for j, f in enumerate(["stage", "probability", "owner"]):
        frags.append(text(rx0 + 34, sales_y + 28 + (j + 1) * 22, f,
                          size=12, color=INK, anchor="start"))
    frags.append(text(rx0 + 16, sales_y + 28 + 4 * 22, "}", size=12, bold=True,
                      color=INK, anchor="start"))

    # Бухгалтерія
    bill_y = sales_y + bh + 92
    frags.append(rect(rx0, bill_y, bw, bh, fill="#eef7f0", stroke=FIELD, sw=2.2, rx=14))
    frags.append(text(rx0 + bw / 2, bill_y - 12,
                      "Контекст «Бухгалтерія»", size=14, bold=True, color=FIELD))
    frags.append(text(rx0 + 16, bill_y + 28, "Payer {", size=12, bold=True,
                      color=INK, anchor="start"))
    for j, f in enumerate(["taxId", "creditLimit", "iban"]):
        frags.append(text(rx0 + 34, bill_y + 28 + (j + 1) * 22, f,
                          size=12, color=INK, anchor="start"))
    frags.append(text(rx0 + 16, bill_y + 28 + 4 * 22, "}", size=12, bold=True,
                      color=INK, anchor="start"))

    # Перекладач — коробка НА межі між двома контекстами (двері в стіні)
    seam_y = (sales_y + bh + bill_y) / 2
    tbh = 44
    tb = fitbox(rx0 + bw / 2 - 90, seam_y - tbh / 2, 180, tbh,
                "перекладач\ntoPayer(lead)", size=12,
                fill="#fff8e6", stroke="#b8860b", sw=2.0)
    frags.append(tb)
    # тонкі стрілки Lead → перекладач → Payer у ЛІВІЙ смузі коробки,
    # осторонь від центрованого напису (повз текст, не крізь нього)
    lane = rx0 + 22
    frags.append(arrow(lane, sales_y + bh + 2, lane, seam_y - tbh / 2 - 2,
                       color=MUTED, sw=1.6))
    frags.append(arrow(lane, seam_y + tbh / 2 + 2, lane, bill_y - 2,
                       color=MUTED, sw=1.6))

    render(os.path.join(IMG, 'refactor-split-with-translator.svg'), W, H, *frags,
           title="Розрізати спільну модель надвоє з перекладачем на межі")


if __name__ == "__main__":
    fig_one_model_vs_contexts()
    fig_three_boundaries()
    fig_refactor_move()
    print("figures written to", IMG)
