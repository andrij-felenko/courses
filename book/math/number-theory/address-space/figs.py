# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#caa24a"
GOLDF = "#fde9c8"
BLUEF = "#eef3fc"
REDF = "#fbeceb"


# ── ladder: N бітів адреси → 2ᴺ комірок, кожен біт подвоює простір ─────────────
# Ідея: показати вибух 2ᴺ драбиною — рядок на ширину адреси, поруч 2ᴺ і скільки
# це байтів; зелені підписи між щаблями кажуть «+k біт → ×2ᵏ», щоб видно було, що
# крок 8→16 це не «вдвічі», а ×256.

def fig_ladder():
    W, H = 760, 470
    rows = [
        ("8 біт",  "2⁸",  "256 байтів",        8,  False),
        ("10 біт", "2¹⁰", "1 024 = 1 КіБ",     10, False),
        ("16 біт", "2¹⁶", "65 536 = 64 КіБ",   12, False),
        ("20 біт", "2²⁰", "1 048 576 = 1 МіБ", 12, False),
        ("24 біт", "2²⁴", "16 МіБ",            12, False),
        ("32 біт", "2³²", "4 294 967 296 = 4 ГіБ", 12, True),
    ]
    gaps = ["+2 біт → ×4", "+6 біт → ×64", "+4 біт → ×16", "+4 біт → ×16", "+8 біт → ×256"]
    p = []
    p.append(text(70, 70, "біти адреси (N)", size=12, color=MUTED, bold=True, anchor="start"))
    p.append(text(300, 70, "комірок = 2ᴺ", size=12, color=MUTED, bold=True))
    p.append(text(560, 70, "скільки це байтів", size=12, color=MUTED, bold=True))
    y0, dy = 100, 58
    bx0 = 70
    for i, (lbl, pw, byt, nbox, hot) in enumerate(rows):
        y = y0 + i * dy
        col = POS if hot else INK
        boxcol = POS if hot else MUTED
        boxfill = REDF if hot else "#eceff2"
        for j in range(nbox):
            p.append(rect(bx0 + j * 14, y - 11, 12.5, 12.5, fill=boxfill, stroke=boxcol, sw=1.3, rx=0))
        if nbox >= 12:
            p.append(text(bx0 + nbox * 14 + 4, y, "…", size=14, color=MUTED, anchor="start", bold=True))
        p.append(text(bx0 + 6, y + 24, lbl, size=14, color=col, bold=True, anchor="start"))
        p.append(text(300, y, pw, size=18, color=col, bold=True))
        p.append(text(420, y, "=", size=15, color=MUTED, anchor="start"))
        p.append(text(445, y, byt, size=15, color=col, bold=hot, anchor="start"))
        if i < len(gaps):
            gx = 360
            p.append(line(gx, y + 14, gx, y + dy - 14, color=FIELD, sw=1.6, ))
            p.append(arrow(gx, y + 14, gx, y + dy - 14, color=FIELD, sw=1.6))
            p.append(text(gx + 8, y + dy / 2 + 4, gaps[i], size=11, color=FIELD, anchor="start", italic=True))
    p.append(line(70, H - 56, W - 40, H - 56, color="#e4e4e4", sw=1.5))
    p.append(text(W / 2, H - 26, "+1 біт адреси = ×2 простору; 8→16 біт це не «вдвічі», а ×256",
                  size=13, color=POS, bold=True))
    render(os.path.join(OUT, "ladder.svg"), W, H, *p,
           title="N бітів адреси → 2ᴺ комірок: кожен біт подвоює простір")


# ── prefixes: десяткове ×1000 проти двійкового ×1024, розрив накопичується ─────
# Ідея: дві колонки префіксів поряд (СІ vs IEC), знизу — стовпчики розриву у %,
# що ростуть від кіло до тера; підпис про «250 ГБ диск ≈ 232 ГіБ».

def fig_prefixes():
    W, H = 760, 470
    p = []
    lx, rx, bw, bh = 60, 400, 300, 220
    p.append(rect(lx, 80, bw, bh, fill=BLUEF, stroke=NEG, sw=1.6, rx=10))
    p.append(rect(rx, 80, bw, bh, fill=REDF, stroke=POS, sw=1.6, rx=10))
    p.append(text(lx + bw / 2, 106, "десяткові (СІ): крок ×1000", size=14, color=NEG, bold=True))
    p.append(text(lx + bw / 2, 124, "диски, швидкості, маркетингові байти", size=11, color=MUTED, italic=True))
    p.append(text(rx + bw / 2, 106, "двійкові (IEC): крок ×1024", size=14, color=POS, bold=True))
    p.append(text(rx + bw / 2, 124, "адреси, RAM, розміри в пам'яті", size=11, color=MUTED, italic=True))
    dec = [("кБ  (kB)", "10³", "= 1 000"),
           ("МБ  (MB)", "10⁶", "= 1 000 000"),
           ("ГБ  (GB)", "10⁹", "= 1 000 000 000")]
    bina = [("КіБ (KiB)", "2¹⁰", "= 1 024"),
            ("МіБ (MiB)", "2²⁰", "= 1 048 576"),
            ("ГіБ (GiB)", "2³⁰", "= 1 073 741 824")]
    for i, ((dn, dp, dv), (bn, bp, bv)) in enumerate(zip(dec, bina)):
        y = 168 + i * 50
        p.append(text(lx + 16, y, dn, size=14, color=INK, bold=True, anchor="start"))
        p.append(text(lx + 120, y, dp, size=15, color=NEG, bold=True, anchor="start"))
        p.append(text(lx + 160, y, dv, size=13, color=INK, anchor="start"))
        p.append(text(rx + 16, y, bn, size=14, color=INK, bold=True, anchor="start"))
        p.append(text(rx + 120, y, bp, size=15, color=POS, bold=True, anchor="start"))
        p.append(text(rx + 160, y, bv, size=13, color=INK, anchor="start"))
    # стовпчики розриву
    p.append(text(W / 2, 330, "розрив росте з кожним щаблем (двійкове більше):", size=13, color=INK, bold=True))
    bars = [("кіло", "+2.4 %", 18), ("мега", "+4.9 %", 34), ("гіга", "+7.4 %", 50), ("тера", "+10 %", 66)]
    base = 410
    for i, (nm, pc, h) in enumerate(bars):
        cx = 200 + i * 130
        p.append(rect(cx - 35, base - h, 70, h, fill=GOLDF, stroke=GOLD, sw=1.4, rx=0))
        p.append(text(cx, base - h - 8, pc, size=12, color=POS, bold=True))
        p.append(text(cx, base + 18, nm, size=12, color=INK, bold=True))
    p.append(text(W / 2, H - 14, "тому диск «250 ГБ» система показує як ≈ 232 ГіБ — байти ті самі, лінійка інша",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "prefixes.svg"), W, H, *p,
           title="Два «кіло»: десяткове (×1000) і двійкове (×1024)")


# ── fourgig: розклад 2³² = 2²·2³⁰ = 4 ГіБ + три тверезі ремарки ────────────────
# Ідея: одним рядком показати, звідки береться «4» (це 2², залишок над 30 бітами
# «гіга»), точне число в байтах, і трьома картками відокремити стелю від RAM.

def fig_fourgig():
    W, H = 760, 430
    p = []
    p.append(rect(90, 80, W - 180, 80, fill=BLUEF, stroke=NEG, sw=2, rx=12))
    yb = 130
    seg = [("2³²", NEG, 28, True), ("=", MUTED, 22, False), ("2²", INK, 22, True),
           ("·", MUTED, 20, False), ("2³⁰", POS, 22, True), ("=", MUTED, 22, False),
           ("4", INK, 24, True), ("×", MUTED, 18, False), ("1 ГіБ", POS, 22, True),
           ("=", MUTED, 22, False), ("4 ГіБ", FIELD, 26, True)]
    x = 120
    for s, c, sz, b in seg:
        p.append(text(x, yb, s, size=sz, color=c, bold=b, anchor="start"))
        x += text_width(s, sz, b) + 16
    p.append(text(W / 2, 210, "точно в байтах:", size=14, color=INK, bold=True))
    p.append(rect(200, 226, W - 400, 46, fill=REDF, stroke=POS, sw=1.6, rx=8))
    p.append(text(W / 2, 255, "2³² = 4 294 967 296 байтів", size=21, color=POS, bold=True))
    cards = [
        ("Стеля, не обіцянка", ["32 біти АДРЕСУЮТЬ 4 ГіБ — це", "максимум; скільки RAM реально", "стоїть, окреме питання"]),
        ("Звідси перехід на 64 біти", ["4 ГіБ стали тісними для ПК → 2⁶⁴", "це 16 ЕіБ, межа зникла на", "десятиліття"]),
        ("На МК межа геть інша", ["адреса там широка, та фізичної", "SRAM лиш кілобайти — стелю", "ставить залізо, не біти"]),
    ]
    cw, cy, ch = 226, 312, 100
    for i, (h, body) in enumerate(cards):
        cx = 30 + i * (cw + 12)
        p.append(rect(cx, cy, cw, ch, fill="#fcfcfc", stroke="#e4e4e4", sw=1.4, rx=8))
        p.append(text(cx + 14, cy + 24, h, size=13, color=INK, bold=True, anchor="start"))
        for k, ln in enumerate(body):
            p.append(text(cx + 14, cy + 48 + k * 18, ln, size=11, color=INK, anchor="start"))
    render(os.path.join(OUT, "fourgig.svg"), W, H, *p,
           title="Чому 32-бітна адреса бачить рівно 4 ГіБ")


# ── map: адресний простір — суцільна лінійка адрес, у яку лягають RAM і пристрої ─
# Ідея: простір 0…2ᴺ−1 як вертикальна стрічка; у неї відображено RAM, ПЗП і
# реєстри периферії (memory-mapped). Видно: пристрої «з'їдають» частину простору,
# тому для RAM лишається менше, ніж уся стеля.

def fig_map():
    W, H = 760, 470
    p = []
    bx, by, bw, bh = 120, 80, 150, 330
    # суцільна стрічка простору, поділена на області
    regions = [
        ("ПЗП / Flash\n(код)", "#eef3fc", NEG, 0.18),
        ("RAM\n(дані, стек)", "#eaf7ee", FIELD, 0.40),
        ("вільна\nдірка", "#fcfcfc", "#cfcfcf", 0.14),
        ("реєстри\nпериферії\n(MMIO)", "#fbeceb", POS, 0.28),
    ]
    y = by
    for nm, fill, stroke, frac in regions:
        h = bh * frac
        p.append(rect(bx, y, bw, h, fill=fill, stroke=stroke, sw=1.6, rx=0))
        p.append(mtext(bx + bw / 2, y + h / 2 - (nm.count(chr(10))) * 6 + 4, nm,
                       size=12, color=INK, bold=True))
        y += h
    # вісь адрес ліворуч
    p.append(text(bx - 12, by + 6, "0x0000", size=11, color=MUTED, anchor="end"))
    p.append(text(bx - 12, by + bh, "0xFFFF…", size=11, color=MUTED, anchor="end"))
    p.append(text(bx - 60, by + bh / 2, "адреси", size=12, color=MUTED, bold=True, anchor="middle"))
    p.append(arrow(bx - 30, by, bx - 30, by + bh, color=MUTED, sw=1.4))
    # пояснення праворуч
    ex = 320
    box1, w1, h1 = textbox(ex + 190, 130,
                           ["Адресний простір — одна суцільна",
                            "лінійка з 2ᴺ номерів. У неї",
                            "відображають усе, що процесор",
                            "адресує: пам'ять І пристрої."],
                           size=12.5, fill=FILL, stroke=LINE)
    p.append(box1)
    box2, w2, h2 = textbox(ex + 190, 250,
                           ["Реєстри периферії живуть",
                            "за СВОЇМИ адресами в тому ж",
                            "просторі (memory-mapped):",
                            "читання комірки = доступ до GPIO,",
                            "таймера, АЦП — не до пам'яті."],
                           size=12.5, fill=REDF, stroke=POS, color=INK)
    p.append(box2)
    box3, w3, h3 = textbox(ex + 190, 372,
                           ["Тому пристрої «з'їдають» частину",
                            "простору — для RAM лишається",
                            "менше, ніж уся стеля 2ᴺ."],
                           size=12.5, fill="#eaf7ee", stroke=FIELD, color=INK)
    p.append(box3)
    render(os.path.join(OUT, "map.svg"), W, H, *p,
           title="Адресний простір: одна лінійка, у яку лягають і пам'ять, і пристрої")


if __name__ == "__main__":
    fig_ladder()
    fig_prefixes()
    fig_fourgig()
    fig_map()
    print("OK: ladder, prefixes, fourgig, map")
