# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def nibble_cell(x, y, bits, digit, w=44, h=44, good=True):
    """Одна тетрада: 4 біти зверху й десяткова цифра під нею."""
    col = FIELD if good else POS
    out = rect(x, y, w, h, fill="#eef7f0" if good else "#fdecea", stroke=col, sw=2)
    out += text(x + w / 2, y + h / 2 + 5, bits, size=15, color=INK, bold=True)
    if digit is not None:
        out += text(x + w / 2, y + h + 20, str(digit), size=20, color=col, bold=True)
    return out


# ── Фігура 1: цифра-на-тетраду проти суцільного двійкового ────────────────────
def fig_nibble_map():
    W, H = 706, 300
    frags = []
    frags.append(text(W / 2, 30, "Число 495", size=18, bold=True))

    # BCD-рядок
    frags.append(text(W / 2, 66, "BCD: кожна десяткова цифра — своя тетрада (4 біти)", size=13, color=MUTED))
    digs = [("0100", 4), ("1001", 9), ("0101", 5)]
    x0, y0 = 208, 84
    for i, (b, d) in enumerate(digs):
        frags.append(nibble_cell(x0 + i * 88, y0, b, d))
    frags.append(text(x0 + 3 * 88 + 4, y0 + 24, "→ читаємо прямо: 4·9·5", size=13, color=FIELD, anchor="start"))

    # межа
    frags.append(line(60, 176, W - 60, 176, color="#dddddd", sw=1))

    # чисте двійкове
    frags.append(text(W / 2, 206, "Чисте двійкове: те саме число одним блоком", size=13, color=MUTED))
    frags.append(rect(x0, 224, 3 * 88 - 44, 44, fill="#eef1fb", stroke=NEG, sw=2))
    frags.append(text(x0 + (3 * 88 - 44) / 2, 224 + 28, "1 1110 1111", size=16, color=INK, bold=True))
    frags.append(text(x0 + 3 * 88 - 44 + 8, 224 + 28, "→ треба ділити на 10, щоб дістати цифри", size=13, color=NEG, anchor="start"))

    render(os.path.join(IMG, "nibble-map.svg"), W, H, *frags)


# ── Фігура 2: пакований проти розпакованого ──────────────────────────────────
def fig_packed():
    W, H = 640, 250
    frags = []
    frags.append(text(W / 2, 30, "Два способи покласти число 72 у пам'ять", size=17, bold=True))

    # пакований: один байт, дві тетради
    frags.append(text(150, 70, "Пакований", size=14, bold=True))
    bx, by = 60, 84
    frags.append(rect(bx, by, 180, 50, fill=BG, stroke=INK, sw=2))
    frags.append(line(bx + 90, by, bx + 90, by + 50, color=INK, sw=1.5, dash="4,3"))
    frags.append(text(bx + 45, by + 31, "0111", size=15, bold=True))
    frags.append(text(bx + 135, by + 31, "0010", size=15, bold=True))
    frags.append(text(bx + 45, by + 68, "7", size=17, color=FIELD, bold=True))
    frags.append(text(bx + 135, by + 68, "2", size=17, color=FIELD, bold=True))
    frags.append(text(bx + 90, by + 92, "1 байт = 0x72", size=13, color=MUTED))

    # розпакований: два байти
    frags.append(text(470, 70, "Розпакований", size=14, bold=True))
    ux = 360
    for i, (nib, d) in enumerate([("0000 0111", 7), ("0000 0010", 2)]):
        x = ux + i * 130
        frags.append(rect(x, by, 110, 50, fill=BG, stroke=INK, sw=2))
        frags.append(text(x + 55, by + 31, nib, size=13, bold=True))
        frags.append(text(x + 55, by + 68, str(d), size=17, color=FIELD, bold=True))
    frags.append(text(ux + 120, by + 92, "2 байти: 0x07, 0x02", size=13, color=MUTED))

    frags.append(text(W / 2, 200, "Пакований щільніший удвічі; розпакований — цифра на байт, зручний для символів",
                      size=12.5, color=MUTED))
    render(os.path.join(IMG, "packed.svg"), W, H, *frags)


# ── Фігура 3: марнування кодового простору ───────────────────────────────────
def fig_waste():
    W, H = 660, 250
    frags = []
    frags.append(text(W / 2, 30, "16 комбінацій тетради: 10 корисних, 6 заборонених", size=16, bold=True))
    x0, y0, w, h, gap = 30, 74, 36, 30, 3
    for v in range(16):
        x = x0 + v * (w + gap)
        good = v <= 9
        col = FIELD if good else POS
        frags.append(rect(x, y0, w, h, fill="#eef7f0" if good else "#fdecea", stroke=col, sw=2))
        frags.append(text(x + w / 2, y0 + h / 2 + 4, format(v, "04b"), size=10, color=INK, bold=True))
        frags.append(text(x + w / 2, y0 + h + 20, ("%X" % v), size=14, color=col, bold=True))
    frags.append(text(x0 + 5 * (w + gap), y0 + h + 52, "0…9 — десяткові цифри",
                      size=13, color=FIELD, anchor="middle"))
    frags.append(text(x0 + 12.5 * (w + gap), y0 + h + 52, "A…F — не бувають",
                      size=13, color=POS, anchor="middle"))
    frags.append(text(W / 2, y0 + h + 88,
                      "Плата за десяткову зручність: 6 із 16 кодів (37%) марно, число займає більше бітів",
                      size=12.5, color=MUTED))
    render(os.path.join(IMG, "waste.svg"), W, H, *frags)


# ── Фігура 4: корекція +6 при додаванні BCD ──────────────────────────────────
def fig_add_six():
    W, H = 620, 300
    frags = []
    frags.append(text(W / 2, 30, "Додавання BCD: 5 + 7 і навіщо +6", size=17, bold=True))

    def row(y, label, bits, val, col, note):
        frags.append(text(70, y + 5, label, size=14, anchor="end", color=MUTED))
        frags.append(rect(90, y - 18, 130, 32, fill=BG, stroke=col, sw=2))
        frags.append(text(155, y + 4, bits, size=15, bold=True))
        frags.append(text(240, y + 5, val, size=14, anchor="start", color=col, bold=True))
        if note:
            frags.append(text(340, y + 5, note, size=12.5, anchor="start", color=MUTED))

    row(80, "5", "0101", "= 5", INK, "")
    row(120, "+ 7", "0111", "= 7", INK, "")
    frags.append(line(90, 138, 470, 138, color=INK, sw=1.3))
    row(162, "сума", "1100", "= 0xC ✗", POS, "нема такої цифри — тетрада «перескочила» 9")
    row(210, "+ 6", "0110", "= 6", NEG, "штовхаємо тетраду за межу 16")
    frags.append(line(90, 228, 470, 228, color=INK, sw=1.3))
    # результат: перенос + 2
    frags.append(text(70, 257, "= 12", size=14, anchor="end", color=MUTED))
    frags.append(rect(90, 234, 62, 32, fill="#eef7f0", stroke=FIELD, sw=2))
    frags.append(text(121, 256, "0001", size=15, bold=True))
    frags.append(rect(158, 234, 62, 32, fill="#eef7f0", stroke=FIELD, sw=2))
    frags.append(text(189, 256, "0010", size=15, bold=True))
    frags.append(text(240, 257, "= 1 і 2 → 12 ✓", size=14, anchor="start", color=FIELD, bold=True))
    frags.append(text(W / 2, 290, "Перенос із молодшої тетради дає старшу цифру — рівно як у стовпчик на папері",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "add-six.svg"), W, H, *frags)


# ── Фігура 5 (hist): лінія від грошей до System/360 ──────────────────────────
def fig_hist_timeline():
    W, H = 720, 470
    frags = []
    frags.append(text(W / 2, 32, "Чому десяткове залізо породило BCD", size=18, bold=True))
    frags.append(text(W / 2, 54, "гроші вимагають точної десятки → машини рахують десятково → BCD успадковує це",
                      size=12.5, color=MUTED))

    # вертикальна вісь часу
    axx = 96
    top, bot = 92, 424
    frags.append(line(axx, top, axx, bot, color="#c9ccd1", sw=2))

    # (рік, заголовок, підпис, колір-вузла)
    rows = [
        ("1890", "Табулятори Голлеріта",
         "перепис США: десяткові диски-лічильники, перфокарта", MUTED),
        ("1934", "Бухгалтерські машини IBM",
         "рахунки клієнтів у десяткових цифрах, а не у двійковій", MUTED),
        ("1944", "Гарвардський Mark I",
         "релейний обчислювач, 23-значні ДЕСЯТКОВІ лічильники", INK),
        ("1959", "IBM 1401 — BCD",
         "цифра = 6 бітів (BCDIC); десяткова машина для бізнесу", FIELD),
        ("1963–64", "EBCDIC",
         "6-бітний BCD розширено до 8 бітів заради сумісності", FIELD),
        ("1964", "System/360",
         "пакований BCD убудовано в набір команд — під спадкове залізо", POS),
    ]
    n = len(rows)
    for i, (yr, head, sub, col) in enumerate(rows):
        cy = top + (bot - top) * (i + 0.5) / n
        # вузол
        frags.append(circle(axx, cy, 7, fill=BG, stroke=col, sw=3))
        # рік ліворуч від осі
        frags.append(text(axx - 16, cy + 5, yr, size=13, color=col, anchor="end", bold=True))
        # заголовок і підпис праворуч
        frags.append(text(axx + 22, cy - 6, head, size=14.5, color=INK, anchor="start", bold=True))
        frags.append(text(axx + 22, cy + 13, sub, size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *frags)


# ── Фігура (math): чому саме +6 — три зони суми 0..18 ─────────────────────────
def fig_why_six():
    W, H = 700, 320
    frags = []
    frags.append(text(W / 2, 30, "Сума двох цифр 0…18: три зони й стала різниця 6", size=16, bold=True))

    x0, y0 = 40, 120
    step = (W - 80) / 18.0
    zones = [(0, 9, "#e9f7ee", FIELD, "0…9: чесна"),
             (10, 15, "#fdf3d8", "#c9a227", "10…15: A…F, +6 дає перенос"),
             (16, 18, "#fde6d8", "#d2691e", "16…18: +6 добирає залишок")]
    for lo, hi, fill, col, _ in zones:
        zx = x0 + lo * step
        zw = (hi - lo + 1) * step
        frags.append(rect(zx, y0 - 26, zw, 52, fill=fill, stroke=col, sw=1.6))
    for v in range(19):
        x = x0 + v * step
        frags.append(line(x, y0 - 26, x, y0 + 26, color="#ffffff", sw=1))
        frags.append(text(x + step / 2, y0 + 6, str(v), size=11, color=INK,
                          bold=(v in (10, 16))))
    # легенда зон одним рядком, центрованим як група (щоб не вилазило за поле)
    ly = y0 + 62
    sw_box, gap_sc, gap_it = 15, 6, 20
    items = [(col, cap) for _, _, _, col, cap in zones]
    widths = [sw_box + gap_sc + text_width(cap, 12, True) for col, cap in items]
    total = sum(widths) + gap_it * (len(items) - 1)
    cx = W / 2 - total / 2
    for (col, cap), wd in zip(items, widths):
        frags.append(rect(cx, ly - 11, sw_box, sw_box, fill=col, stroke=col, sw=1, rx=3))
        frags.append(text(cx + sw_box + gap_sc, ly + 3, cap, size=12, color=INK,
                          anchor="start", bold=True))
        cx += wd + gap_it
    frags.append(text(W / 2, ly + 40,
                      "16 − 10 = 6  —  наскільки тетрада (mod 16) відстає від десяткової цифри (mod 10)",
                      size=13.5, color=INK, bold=True))
    frags.append(text(W / 2, ly + 64,
                      "тому одна поправка +6 лікує і застряглі коди, і закороткий залишок після переносу",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "why-six.svg"), W, H, *frags)


# ── Фігура (math): самодоповняльність через NOT (Excess-3 і Aiken) ────────────
def fig_self_complement():
    W, H = 700, 400
    frags = []
    frags.append(text(W / 2, 30, "Самодоповняльні коди: NOT усіх бітів = дев'яткове доповнення",
                      size=15.5, bold=True))

    xs3 = {0: "0011", 1: "0100", 2: "0101", 3: "0110", 4: "0111",
           5: "1000", 6: "1001", 7: "1010", 8: "1011", 9: "1100"}
    aik = {0: "0000", 1: "0001", 2: "0010", 3: "0011", 4: "0100",
           5: "1011", 6: "1100", 7: "1101", 8: "1110", 9: "1111"}

    def column(cx, table, title):
        out = text(cx, 66, title, size=14, bold=True, color=INK)
        y0, dy = 88, 30
        for d in range(10):
            y = y0 + d * dy
            out += rect(cx - 62, y - 13, 44, 24, fill="#eef7f0", stroke=FIELD, sw=1.4)
            out += text(cx - 40, y + 4, str(d), size=13, color=INK, bold=True)
            out += rect(cx - 12, y - 13, 74, 24, fill=BG, stroke=INK, sw=1.4)
            out += text(cx + 25, y + 4, table[d], size=13, color=INK, bold=True)
        return out, y0, dy

    cxL, cxR = 210, 500
    colL, y0, dy = column(cxL, xs3, "Excess-3  (8421 + 3)")
    colR, _, _ = column(cxR, aik, "Aiken 2421  (ваги 2·4·2·1)")
    frags.append(colL)
    frags.append(colR)

    midx = (cxL + cxR) / 2
    for d, e in [(0, 9), (1, 8), (2, 7), (3, 6), (4, 5)]:
        yd = y0 + d * dy
        ye = y0 + e * dy
        x1 = cxL + 62
        x2 = cxR - 62
        cy = (yd + ye) / 2
        frags.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                     'stroke="%s" stroke-width="1.4" stroke-dasharray="4,3"/>'
                     % (x1, yd, midx, cy, x2, ye, NEG))
    frags.append(text(midx, y0 - 8, "NOT ↕", size=12, color=NEG, bold=True))
    frags.append(text(midx, y0 + 10 * dy - 6, "d ↔ 9−d", size=11.5, color=NEG))

    frags.append(text(W / 2, H - 16,
                      "Сума ваг бітів = 9 в обох кодах → перевертання всіх бітів дає код цифри 9−d задарма",
                      size=12.5, color=MUTED))
    render(os.path.join(IMG, "self-complement.svg"), W, H, *frags)


# ── Фігура (proj): крок double dabble на одній тетраді (+3 наперед) ────────────
def fig_dabble_step():
    W, H = 660, 320
    frags = []
    frags.append(text(W / 2, 30, "Крок double dabble на одній тетраді: чому +3 перед зсувом", size=16, bold=True))

    def nib(x, y, bits, val, col, w=110, h=40):
        frags.append(rect(x, y, w, h, fill="#f4f6f8", stroke=col, sw=2))
        frags.append(text(x + w / 2, y + h / 2 + 5, bits, size=15, color=INK, bold=True))
        if val is not None:
            frags.append(text(x + w / 2, y - 8, val, size=13, color=col, bold=True))

    # ── ліва колонка: без корекції ──
    lx = 70
    frags.append(text(lx + 55, 66, "Без поправки", size=14, bold=True, color=POS))
    nib(lx, 84, "0101", "цифра 5", INK)
    frags.append(arrow(lx + 55, 130, lx + 55, 160, color=NEG))
    frags.append(text(lx + 128, 150, "зсув · 2", size=12.5, color=NEG, anchor="start"))
    nib(lx, 166, "1010", "= 10 ✗", POS)
    frags.append(text(lx + 55, 238, "тетрада зламалась:", size=12.5, color=POS))
    frags.append(text(lx + 55, 256, "цифри понад 9 не буває", size=12.5, color=POS))

    # ── межа ──
    frags.append(line(W / 2, 78, W / 2, 272, color="#dddddd", sw=1, dash="4,4"))

    # ── права колонка: з корекцією +3 ──
    rx = 400
    frags.append(text(rx + 55, 66, "З поправкою +3 наперед", size=14, bold=True, color=FIELD))
    nib(rx, 84, "0101", "5 + 3 = 8", INK)
    frags.append(text(rx + 128, 108, "→ 1000", size=12.5, color=MUTED, anchor="start"))
    frags.append(arrow(rx + 55, 130, rx + 55, 160, color=NEG))
    frags.append(text(rx + 128, 150, "зсув · 2", size=12.5, color=NEG, anchor="start"))
    # результат: перенос 1 | тетрада 0000
    frags.append(text(rx - 26, 158, "перенос", size=11, color=FIELD))
    frags.append(rect(rx - 46, 166, 40, 40, fill="#eef7f0", stroke=FIELD, sw=2))
    frags.append(text(rx - 26, 191, "1", size=16, color=FIELD, bold=True))
    nib(rx, 166, "0000", "= 0", FIELD)
    frags.append(text(rx + 55, 238, "перенос 1 → у старшу цифру,", size=12.5, color=FIELD))
    frags.append(text(rx + 55, 256, "0 лишається тут  →  разом 10 ✓", size=12.5, color=FIELD))

    frags.append(text(W / 2, 300, "+3 перед зсувом = +6 після подвоєння: старший біт стає переносом, різницю мод-16 vs мод-10 знято",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "dabble-step.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_nibble_map()
    fig_packed()
    fig_waste()
    fig_add_six()
    fig_hist_timeline()
    fig_why_six()
    fig_self_complement()
    fig_dabble_step()
    print("figs done")
