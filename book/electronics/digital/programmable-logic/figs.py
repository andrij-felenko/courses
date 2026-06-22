# -*- coding: utf-8 -*-
# Фігури теми «Програмована логіка» (book/electronics/digital/programmable-logic).
# svgkit імпортуємо, не переписуємо (AUTHORING §5). Вивід — у ./img/ зі slug-іменами.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні відтінки рамок (узгоджені з палітрою svgkit)
BLUE_F  = "#f3f5fd"   # заливка «процесор» (холодне)
GREEN_F = "#eef7ee"   # заливка «FPGA» (поле)
AMBER   = "#caa24a"   # проміжне (GPU)
GREY    = "#8a8a8a"


# ───────────────────────────────────────────────────────────────────────────
# 1. serial-bottleneck — час проти простору: одна АЛП за N тактів vs N блоків за 1
# ───────────────────────────────────────────────────────────────────────────
def fig_serial_bottleneck():
    W, H = 860, 380
    p = []
    p.append(text(W / 2, 50, "Та сама робота: у часі (одна АЛП) чи у просторі (багато блоків)",
                  size=12, color=MUTED, italic=True))

    # — Ліворуч: процесор, одна АЛП, кроки в часі —
    lx, ly, lw, lh = 60, 78, 360, 232
    p.append(rect(lx, ly, lw, lh, fill=BLUE_F, stroke=NEG, sw=2, rx=12))
    p.append(text(lx + lw / 2, ly + 24, "ПРОЦЕСОР: одна АЛП", size=13, color=NEG, bold=True))
    p.append(text(lx + lw / 2, ly + 42, "розкладає роботу в ЧАСІ", size=10, color=MUTED, italic=True))
    alu_x, alu_y = lx + lw / 2 - 34, ly + 60
    p.append(rect(alu_x, alu_y, 68, 40, fill="#fff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(alu_x + 34, alu_y + 24, "АЛП", size=12, color=NEG, bold=True))
    # стрічка тактів під АЛП
    ty = alu_y + 70
    for i in range(5):
        cx = lx + 40 + i * 60
        p.append(rect(cx, ty, 44, 30, fill="#fff", stroke=LINE, sw=1.3, rx=4))
        p.append(text(cx + 22, ty + 20, "крок %d" % (i + 1), size=9, color=INK))
        if i < 4:
            p.append(arrow(cx + 44, ty + 15, cx + 60, ty + 15, color=LINE, sw=1.4))
    p.append(text(lx + lw / 2, ty + 56, "N дій → N тактів", size=11, color=NEG, bold=True))

    # — Праворуч: FPGA, N блоків нараз —
    rx, ry, rw, rh = 440, 78, 360, 232
    p.append(rect(rx, ry, rw, rh, fill=GREEN_F, stroke=FIELD, sw=2, rx=12))
    p.append(text(rx + rw / 2, ry + 24, "FPGA: багато блоків", size=13, color=FIELD, bold=True))
    p.append(text(rx + rw / 2, ry + 42, "розкладає роботу в ПРОСТОРІ", size=10, color=MUTED, italic=True))
    # 6 однакових блоків 3×2, усі живляться входом одночасно
    bw, bh = 86, 40
    gx, gy = rx + 28, ry + 64
    for r in range(2):
        for c in range(3):
            bx = gx + c * (bw + 12)
            by = gy + r * (bh + 18)
            p.append(rect(bx, by, bw, bh, fill="#fff", stroke=FIELD, sw=1.6, rx=6))
            p.append(text(bx + bw / 2, by + 24, "блок %d" % (r * 3 + c + 1), size=10, color=INK))
    p.append(text(rx + rw / 2, gy + 2 * (bh + 18) + 16, "N дій → 1 такт",
                  size=11, color=FIELD, bold=True))

    p.append(text(W / 2, H - 14,
                  "Процесор торгує простором за час; FPGA торгує часом за простір.",
                  size=11, color=INK, bold=True, italic=True))
    render(os.path.join(OUT, "serial-bottleneck.svg"), W, H, *p,
           title="Послідовно в часі — чи паралельно в просторі")


# ───────────────────────────────────────────────────────────────────────────
# 2. throughput-math — пропускна здатність = (оп/такт) × (тактів/с)
# ───────────────────────────────────────────────────────────────────────────
def fig_throughput_math():
    W, H = 860, 410
    p = []
    p.append(text(W / 2, 50, "приклад: 200 млн відліків за секунду, по 10 операцій на кожен",
                  size=11.5, color=MUTED, italic=True))

    # процесор
    lx, ly, lw, lh = 60, 80, 350, 226
    p.append(rect(lx, ly, lw, lh, fill=BLUE_F, stroke=NEG, sw=2, rx=12))
    p.append(text(lx + lw / 2, ly + 26, "ПРОЦЕСОР @ 200 МГц", size=13, color=NEG, bold=True))
    rows_l = ["потрібно: 200·10⁶ × 10 = 2·10⁹ оп/с",
              "має: ~1 оп/такт × 2·10⁸ такт/с",
              "       = 2·10⁸ оп/с"]
    for i, t in enumerate(rows_l):
        p.append(text(lx + 20, ly + 60 + i * 30, t, size=11.5, color=INK, anchor="start"))
    p.append(text(lx + 20, ly + 60 + 3 * 30, "дефіцит: у 10 разів замало!",
                  size=11.5, color=POS, anchor="start", bold=True))
    p.append(text(lx + lw / 2, ly + lh - 14, "одна АЛП не дасть 2 млрд оп/с на 200 МГц",
                  size=9.5, color=MUTED, italic=True))

    # FPGA
    rx, ry, rw, rh = 450, 80, 350, 226
    p.append(rect(rx, ry, rw, rh, fill=GREEN_F, stroke=FIELD, sw=2, rx=12))
    p.append(text(rx + rw / 2, ry + 26, "FPGA @ 200 МГц", size=13, color=FIELD, bold=True))
    rows_r = ["ставимо 10 обчислювачів поряд",
              "кожен: 1 операція за такт",
              "разом: 10 оп/такт × 2·10⁸"]
    for i, t in enumerate(rows_r):
        p.append(text(rx + 20, ry + 60 + i * 30, t, size=11.5, color=INK, anchor="start"))
    p.append(text(rx + 20, ry + 60 + 3 * 30, "       = 2·10⁹ оп/с ✓",
                  size=11.5, color=FIELD, anchor="start", bold=True))
    p.append(text(rx + rw / 2, ry + rh - 14, "та сама частота, у 10 разів більше за такт",
                  size=9.5, color=MUTED, italic=True))

    # підсумкова стрічка
    bx, by, bw2, bh2 = 60, 326, 740, 52
    p.append(rect(bx, by, bw2, bh2, fill=FILL, stroke=FIELD, sw=1.7, rx=10))
    p.append(text(W / 2, by + 22, "Швидкодія = (операцій за такт) × (тактів за секунду).",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, by + 40, "Підняти частоту важко; додати паралельних блоків — легко.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "throughput-math.svg"), W, H, *p,
           title="«Не встигає по тактах» — це проста лічба")


# ───────────────────────────────────────────────────────────────────────────
# 3. latency — затримка реакції: переривання (плаває) vs проліт крізь вентилі
# ───────────────────────────────────────────────────────────────────────────
def fig_latency():
    W, H = 860, 380
    p = []
    p.append(text(W / 2, 50, "від «вхід змінився» до «вихід відреагував»",
                  size=11.5, color=MUTED, italic=True))

    # процесор: довгий ланцюг переривання + джитер
    lx, ly, lw, lh = 60, 78, 740, 120
    p.append(rect(lx, ly, lw, lh, fill=BLUE_F, stroke=NEG, sw=1.8, rx=10))
    p.append(text(lx + 16, ly + 24, "ПРОЦЕСОР: через переривання", size=12, color=NEG, anchor="start", bold=True))
    steps = ["вхід", "перервати", "зберегти стан", "код-обробник", "реакція"]
    sx = lx + 24
    for i, s in enumerate(steps):
        w = 116
        p.append(rect(sx, ly + 44, w, 34, fill="#fff", stroke=NEG, sw=1.4, rx=5))
        p.append(text(sx + w / 2, ly + 65, s, size=10, color=INK))
        if i < len(steps) - 1:
            p.append(arrow(sx + w, ly + 61, sx + w + 22, ly + 61, color=NEG, sw=1.4))
        sx += w + 22
    p.append(text(lx + lw - 16, ly + 24, "десятки–сотні тактів, час ПЛАВАЄ (джитер)",
                  size=10, color=POS, anchor="end", italic=True))

    # FPGA: проліт крізь кілька вентилів
    gx, gy, gw, gh = 60, 214, 740, 120
    p.append(rect(gx, gy, gw, gh, fill=GREEN_F, stroke=FIELD, sw=1.8, rx=10))
    p.append(text(gx + 16, gy + 24, "FPGA: комбінаційна схема", size=12, color=FIELD, anchor="start", bold=True))
    # вхід → 3 вентилі → вихід
    p.append(rect(gx + 24, gy + 44, 90, 34, fill="#fff", stroke=FIELD, sw=1.4, rx=5))
    p.append(text(gx + 24 + 45, gy + 65, "вхід", size=10, color=INK))
    vx = gx + 24 + 90 + 22
    for i in range(3):
        p.append(arrow(vx - 22, gy + 61, vx, gy + 61, color=FIELD, sw=1.4))
        p.append(circle(vx + 26, gy + 61, 20, fill="#fff", stroke=FIELD, sw=1.5))
        p.append(text(vx + 26, gy + 65, "&", size=13, color=INK, bold=True))
        vx += 26 * 2 + 22
    p.append(arrow(vx - 22, gy + 61, vx, gy + 61, color=FIELD, sw=1.4))
    p.append(rect(vx, gy + 44, 90, 34, fill="#fff", stroke=FIELD, sw=1.4, rx=5))
    p.append(text(vx + 45, gy + 65, "вихід", size=10, color=INK))
    p.append(text(gx + gw - 16, gy + 24, "одиниці–десятки нс, такт у такт ОДНАКОВО",
                  size=10, color=FIELD, anchor="end", italic=True))

    p.append(text(W / 2, H - 12,
                  "Де важлива гарантія «не пізніше ніж за стільки наносекунд» — виграє залізо.",
                  size=11, color=INK, bold=True, italic=True))
    render(os.path.join(OUT, "latency.svg"), W, H, *p,
           title="Затримка реакції: процесор проти FPGA")


# ───────────────────────────────────────────────────────────────────────────
# 4. where-used — п'ять класичних царин паралельного заліза
# ───────────────────────────────────────────────────────────────────────────
def fig_where_used():
    W, H = 880, 340
    p = []
    p.append(text(W / 2, 50, "спільне: потік даних надто широкий або реакція потрібна надто рання",
                  size=11.5, color=MUTED, italic=True))
    cards = [
        ("Обробка сигналу", "тисячі множень", "на кожен відлік"),
        ("Відео й зображення", "мільйони пікселів", "за один кадр"),
        ("Швидкі інтерфейси", "сотні Мбіт/с,", "біт за бітом"),
        ("Точний таймінг", "реакція за нс,", "багатофазний ШІМ"),
        ("Багато каналів", "сотні лічильників,", "кожен — копія"),
    ]
    cw, gap = 150, 16
    total = len(cards) * cw + (len(cards) - 1) * gap
    x0 = (W - total) / 2
    for i, (h, a, b) in enumerate(cards):
        x = x0 + i * (cw + gap)
        p.append(rect(x, 80, cw, 150, fill=GREEN_F, stroke=FIELD, sw=1.7, rx=10))
        p.append(text(x + cw / 2, 110, h, size=12, color=FIELD, bold=True))
        p.append(line(x + 16, 122, x + cw - 16, 122, color=FIELD, sw=1))
        p.append(text(x + cw / 2, 150, a, size=10.5, color=INK))
        p.append(text(x + cw / 2, 170, b, size=10.5, color=INK))
        p.append(text(x + cw / 2, 210, "× багато", size=10, color=POS, bold=True))
    p.append(text(W / 2, 280,
                  "Не «порахувати складне один раз» (там сильний процесор),",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 302,
                  "а «робити просте, але дуже багато й водночас» — рідна стихія заліза.",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "where-used.svg"), W, H, *p,
           title="Де паралельне залізо вирішує")


# ───────────────────────────────────────────────────────────────────────────
# 5. spectrum — від процесора до ASIC: гнучкість ↔ швидкість, FPGA посередині
# ───────────────────────────────────────────────────────────────────────────
def fig_spectrum():
    W, H = 900, 400
    p = []
    p.append(text(W / 2, 50, "від «усе вирішує програма» до «усе зашито в кремній»",
                  size=11.5, color=MUTED, italic=True))
    p.append(line(90, 150, 810, 150, color=GREY, sw=2))
    nodes = [
        (150, "Процесор / МК", "будь-яка програма,", "але послідовно", NEG, "гнучкий, повільніший", False),
        (380, "GPU", "тисячі ядер,", "дані-паралельно", AMBER, "", False),
        (560, "FPGA", "своя СХЕМА під", "задачу, паралельно", FIELD, "← наш герой", True),
        (770, "ASIC", "схема назавжди", "випалена в чип", POS, "найшвидший, негнучкий", False),
    ]
    for cx, h, a, b, col, note, hero in nodes:
        p.append(circle(cx, 150, 8, fill="#fff", stroke=col, sw=3))
        p.append(rect(cx - 70, 72, 140, 56, fill="#fafafa", stroke=col, sw=1.6, rx=8))
        p.append(text(cx, 92, h, size=12.5, color=col, bold=True))
        p.append(text(cx, 108, a, size=9, color=INK))
        p.append(text(cx, 122, b, size=9, color=INK))
        if note:
            p.append(text(cx, 180, note, size=9.5, color=(FIELD if hero else MUTED),
                          bold=hero, italic=not hero))
    p.append(arrow(250, 222, 110, 222, color=NEG, sw=1.8))
    p.append(text(180, 214, "більше ГНУЧКОСТІ", size=10, color=NEG, bold=True))
    p.append(arrow(650, 222, 790, 222, color=POS, sw=1.8))
    p.append(text(720, 214, "більше ШВИДКОСТІ й ефективності", size=10, color=POS, bold=True))
    bx, by, bw, bh = 60, 318, 780, 66
    p.append(rect(bx, by, bw, bh, fill=FILL, stroke=FIELD, sw=1.7, rx=10))
    p.append(text(W / 2, by + 26,
                  "Процесор гнучкий, бо програмований, але послідовний; ASIC найшвидший, та схема в ньому застигла.",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, by + 50,
                  "FPGA бере справжню паралельну СХЕМУ під задачу, яку до того ж можна переписати.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "spectrum.svg"), W, H, *p,
           title="Місце FPGA: гнучкість проти швидкості")


# ───────────────────────────────────────────────────────────────────────────
# comp-вставка: instrument-block — місце FPGA у тракті вимірювального приладу
# ───────────────────────────────────────────────────────────────────────────
def fig_instrument_block():
    W, H = 880, 380
    p = []
    p.append(text(W / 2, 50, "швидкий потік відліків іде СПЕРШУ у FPGA, процесор підхоплює зібране",
                  size=11.5, color=MUTED, italic=True))

    # головний тракт: входи → FPGA → буфер → процесор → екран
    y = 130
    def blk(x, w, t1, t2, col, fillc):
        p.append(rect(x, y, w, 70, fill=fillc, stroke=col, sw=1.8, rx=8))
        p.append(text(x + w / 2, y + 30, t1, size=12, color=col, bold=True))
        if t2:
            p.append(text(x + w / 2, y + 50, t2, size=9.5, color=INK))

    blk(60, 110, "Входи", "сотні Мвідл/с", NEG, "#fff")
    p.append(arrow(170, y + 35, 210, y + 35, color=LINE, sw=1.8))
    blk(210, 150, "FPGA", "ловить кожен відлік", FIELD, GREEN_F)
    p.append(arrow(360, y + 35, 400, y + 35, color=LINE, sw=1.8))
    blk(400, 120, "Буфер", "складає дані", INK, FILL)
    p.append(arrow(520, y + 35, 560, y + 35, color=LINE, sw=1.8))
    blk(560, 130, "Процесор", "малює екран", NEG, BLUE_F)
    p.append(arrow(690, y + 35, 730, y + 35, color=LINE, sw=1.8))
    blk(730, 90, "Екран", "", INK, "#fff")

    # «почет» FPGA знизу: флеш конфігурації, кварц, живлення
    p.append(text(285, y + 110, "обов'язковий «почет» FPGA:", size=10, color=MUTED, anchor="start", italic=True))
    sup = [("флеш конфігурації", 210), ("кварц такту", 400), ("кілька джерел живлення", 560)]
    for t, sx in sup:
        p.append(rect(sx, y + 124, 150, 34, fill="#fafafa", stroke=GREY, sw=1.3, rx=6))
        p.append(text(sx + 75, y + 145, t, size=9.5, color=INK))
        p.append(arrow(sx + 75, y + 124, 285, y + 70 + 18, color=GREY, sw=1.2))

    p.append(text(W / 2, H - 14,
                  "Передову лінію — швидкий потік — тримає FPGA; процесор уже потім спокійно рахує.",
                  size=11, color=INK, bold=True, italic=True))
    render(os.path.join(OUT, "instrument-block.svg"), W, H, *p,
           title="FPGA у тракті осцилографа чи логічного аналізатора")


# ───────────────────────────────────────────────────────────────────────────
# hist-вставка 1: timeline — як ідея визрівала й здійснювалася
# ───────────────────────────────────────────────────────────────────────────
def fig_hist_timeline():
    W, H = 900, 320
    p = []
    p.append(text(W / 2, 50, "не ПЕРЕБУДОВУВАТИ залізо під задачу, а ЗАВАНТАЖУВАТИ конфігурацію",
                  size=11.5, color=MUTED, italic=True))
    p.append(line(80, 150, 820, 150, color=GREY, sw=2))
    events = [
        (150, "поч. 1980-х", "ідея «чистої", "стрічки» у Zilog", MUTED, False),
        (360, "1984", "заснування Xilinx", "$4 млн, без заводу", POS, True),
        (610, "1 лист. 1985", "XC2064 — перша", "FPGA у кремнії", FIELD, False),
        (810, "далі", "індустрія на", "мільярди", MUTED, False),
    ]
    for cx, yr, a, b, col, hero in events:
        r = 9 if hero else 7
        p.append(circle(cx, 150, r, fill=("#fff" if not hero else col), stroke=col, sw=3))
        p.append(text(cx, 96, yr, size=12, color=col, bold=True))
        p.append(text(cx, 184, a, size=10, color=INK))
        p.append(text(cx, 200, b, size=10, color=INK))
    p.append(text(W / 2, 262,
                  "Усе почалося з відмови (у Zilog ідею не схотіли),",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 284,
                  "а вивершилося чипом, якому схему задають бітстрімом при ввімкненні.",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Шлях до FPGA: чип, якому схему завантажують")


# ───────────────────────────────────────────────────────────────────────────
# hist-вставка 2: founders — троє засновників, три різні ролі
# ───────────────────────────────────────────────────────────────────────────
def fig_hist_founders():
    W, H = 880, 330
    p = []
    p.append(text(W / 2, 50, "«придумати» ≠ «підняти компанію» ≠ «зробити так, щоб це можна було виробляти»",
                  size=11.5, color=MUTED, italic=True))
    people = [
        ("Росс Фріман", "ВИНАХІД", "сама ідея FPGA:", "чип, у який схему завантажують", FIELD),
        ("Джеймс Барнетт", "УПРАВЛІННЯ", "підняв компанію з нуля:", "гроші, команда, перший продукт", NEG),
        ("Берні Вондершмітт", "ВИРОБНИЦТВО", "як випускати чипи", "без власного заводу", POS),
    ]
    cw, gap = 250, 24
    total = len(people) * cw + (len(people) - 1) * gap
    x0 = (W - total) / 2
    for i, (name, role, a, b, col) in enumerate(people):
        x = x0 + i * (cw + gap)
        p.append(rect(x, 80, cw, 150, fill="#fafafa", stroke=col, sw=1.8, rx=10))
        p.append(text(x + cw / 2, 110, name, size=13, color=col, bold=True))
        p.append(rect(x + cw / 2 - 70, 122, 140, 26, fill=col, stroke=col, sw=0, rx=6))
        p.append(text(x + cw / 2, 140, role, size=11, color="#fff", bold=True))
        p.append(text(x + cw / 2, 178, a, size=10.5, color=INK))
        p.append(text(x + cw / 2, 198, b, size=10.5, color=INK))
    p.append(text(W / 2, 280, "Усі троє прийшли з Zilog. Внески різні — і всі необхідні.",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 304, "Прибери будь-кого — і FPGA лишилася б ідеєю в шухляді.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "founders.svg"), W, H, *p,
           title="Троє засновників — три ролі, а не «один геній»")


# ───────────────────────────────────────────────────────────────────────────
# hist-вставка 3: blank-tape — ASIC (запекти) vs «чиста стрічка» (завантажити)
# ───────────────────────────────────────────────────────────────────────────
def fig_hist_blank_tape():
    W, H = 880, 360
    p = []
    p.append(text(W / 2, 50, "дві відповіді на питання «звідки взяти потрібну схему»",
                  size=11.5, color=MUTED, italic=True))

    # ліворуч — ASIC
    lx, ly, lw, lh = 60, 78, 360, 210
    p.append(rect(lx, ly, lw, lh, fill="#fbeeee", stroke=POS, sw=2, rx=12))
    p.append(text(lx + lw / 2, ly + 26, "ASIC: ЗАПЕКТИ в кремній", size=13, color=POS, bold=True))
    for i, t in enumerate(["логіку впікають намертво",
                           "проєкт і виготовлення — місяці",
                           "помилка → нова маска,",
                           "нова партія, нові гроші"]):
        p.append(text(lx + 20, ly + 60 + i * 30, t, size=11, color=INK, anchor="start"))
    p.append(text(lx + lw / 2, ly + lh - 12, "схема застигла назавжди", size=10, color=POS, italic=True))

    # праворуч — чиста стрічка
    rx, ry, rw, rh = 460, 78, 360, 210
    p.append(rect(rx, ry, rw, rh, fill=GREEN_F, stroke=FIELD, sw=2, rx=12))
    p.append(text(rx + rw / 2, ry + 26, "«ЧИСТА СТРІЧКА»: завантажити", size=13, color=FIELD, bold=True))
    for i, t in enumerate(["універсальна болванка з клітинок",
                           "налаштовують бітстрімом — за години",
                           "помилка → новий файл,",
                           "та сама мікросхема"]):
        p.append(text(rx + 20, ry + 60 + i * 30, t, size=11, color=INK, anchor="start"))
    p.append(text(rx + rw / 2, ry + rh - 12, "право переробити знову", size=10, color=FIELD, italic=True))

    p.append(text(W / 2, H - 14,
                  "Та сама думка, що зробила універсальним процесор — але завантажують не програму, а саму СХЕМУ.",
                  size=10.5, color=INK, bold=True, italic=True))
    render(os.path.join(OUT, "blank-tape.svg"), W, H, *p,
           title="Запекти в кремній — чи завантажити в болванку")


# ───────────────────────────────────────────────────────────────────────────
# hist-вставка 4: fabless — фірма, що проєктує чипи, але не має заводу
# ───────────────────────────────────────────────────────────────────────────
def fig_hist_fabless():
    W, H = 880, 340
    p = []
    p.append(text(W / 2, 50, "«я не мав грошей побудувати фабрику» — суть винаходу однією фразою",
                  size=11.5, color=MUTED, italic=True))

    # Xilinx (проєктує) ←→ чужа фабрика (виготовляє)
    lx, ly, lw, lh = 80, 100, 280, 150
    p.append(rect(lx, ly, lw, lh, fill=GREEN_F, stroke=FIELD, sw=2, rx=12))
    p.append(text(lx + lw / 2, ly + 28, "XILINX", size=14, color=FIELD, bold=True))
    for i, t in enumerate(["архітектура, схема,", "компілятор схем, продаж", "— жодного власного кремнію"]):
        p.append(text(lx + lw / 2, ly + 58 + i * 24, t, size=10.5, color=INK))

    rx, ry, rw, rh = 520, 100, 280, 150
    p.append(rect(rx, ry, rw, rh, fill=BLUE_F, stroke=NEG, sw=2, rx=12))
    p.append(text(rx + rw / 2, ry + 28, "ЧУЖА ФАБРИКА", size=14, color=NEG, bold=True))
    p.append(text(rx + rw / 2, ry + 50, "(перший партнер — Seiko)", size=10, color=MUTED, italic=True))
    for i, t in enumerate(["дорогі лінії вже є", "стороннє замовлення", "лише дозавантажує їх"]):
        p.append(text(rx + rw / 2, ry + 78 + i * 24, t, size=10.5, color=INK))

    # стрілки між ними
    p.append(arrow(lx + lw, ly + 55, rx, ly + 55, color=LINE, sw=1.8))
    p.append(text((lx + lw + rx) / 2, ly + 46, "креслення кристала", size=10, color=INK))
    p.append(arrow(rx, ly + 105, lx + lw, ly + 105, color=LINE, sw=1.8))
    p.append(text((lx + lw + rx) / 2, ly + 122, "готові пластини", size=10, color=INK))

    p.append(text(W / 2, H - 16,
                  "Вигідно обом — отже, угода можлива. Так народилася модель «фаблес».",
                  size=11.5, color=INK, bold=True, italic=True))
    render(os.path.join(OUT, "fabless.svg"), W, H, *p,
           title="«Фаблес»: проєктуємо тут, виробляють там")


# ───────────────────────────────────────────────────────────────────────────
# hist-вставка 5: moore-bet — ставка на закон Мура: транзистори можна марнувати
# ───────────────────────────────────────────────────────────────────────────
def fig_hist_moore_bet():
    W, H = 880, 380
    p = []
    p.append(text(W / 2, 50, "проміняти ПЛОЩУ й ШВИДКІСТЬ на ГНУЧКІСТЬ і ЧАС",
                  size=11.5, color=MUTED, italic=True))

    # осі: ціна транзистора падає з роками (крива закону Мура)
    ox, oy = 90, 250
    aw, ah = 380, 170
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))           # X — роки
    p.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.6))           # Y — ціна транзистора
    p.append(text(ox + aw / 2, oy + 30, "роки →", size=10, color=MUTED))
    p.append(text(ox - 16, oy - ah - 6, "ціна 1 транзистора", size=10, color=MUTED, anchor="start"))
    # спадна крива (вдвічі що ~2 роки)
    import math
    pts = []
    for i in range(0, 41):
        t = i / 40.0
        x = ox + t * aw
        y = (oy - ah + 10) + (ah - 14) * (1 - 0.5 ** (t * 4))
        pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), NEG))
    # позначка ставки Фрімана (1984, на початку кривої)
    bx, by = ox + 0.18 * aw, (oy - ah + 10) + (ah - 14) * (1 - 0.5 ** (0.18 * 4))
    p.append(circle(bx, by, 7, fill=POS, stroke=POS, sw=2))
    p.append(text(bx + 12, by - 6, "ставка Фрімана, 1984", size=10, color=POS, anchor="start", bold=True))

    # права колонка: ціна гнучкості (червоне) проти виграшу (зелене)
    rx = 520
    p.append(rect(rx, 90, 320, 96, fill="#fbeeee", stroke=POS, sw=1.7, rx=10))
    p.append(text(rx + 160, 112, "ПЛАТА за гнучкість", size=12, color=POS, bold=True))
    for i, t in enumerate(["більша площа на кристалі", "нижча швидкість", "вища ціна за штуку"]):
        p.append(text(rx + 18, 134 + i * 18, "• " + t, size=10, color=INK, anchor="start"))
    p.append(rect(rx, 200, 320, 96, fill=GREEN_F, stroke=FIELD, sw=1.7, rx=10))
    p.append(text(rx + 160, 222, "ВИГРАШ", size=12, color=FIELD, bold=True))
    for i, t in enumerate(["схема за години замість місяців", "правлення помилок новим бітстрімом", "нуль витрат на маски"]):
        p.append(text(rx + 18, 244 + i * 18, "• " + t, size=10, color=INK, anchor="start"))

    p.append(text(W / 2, H - 14,
                  "Що дешевшим транзистор — то вигідніший обмін «трохи зайвого кремнію → миттєва гнучкість». Заклад виграно.",
                  size=10.5, color=INK, bold=True, italic=True))
    render(os.path.join(OUT, "moore-bet.svg"), W, H, *p,
           title="Заклад на закон Мура: транзистори можна марнувати")


if __name__ == "__main__":
    fig_serial_bottleneck()
    fig_throughput_math()
    fig_latency()
    fig_where_used()
    fig_spectrum()
    fig_instrument_block()
    fig_hist_timeline()
    fig_hist_founders()
    fig_hist_blank_tape()
    fig_hist_fabless()
    fig_hist_moore_bet()
    print("OK: figures written to", OUT)
