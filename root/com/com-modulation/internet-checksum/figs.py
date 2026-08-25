# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ACC = "#caa24a"   # акцент контрольної суми — теплий жовтий


# ── pipeline: сума слів → загорнути перенос → інверсія → перевірка ─────────────
# Ідея: 16-бітні слова заголовка складають у широкий акумулятор; верхній перенос
# завертають униз; результат інвертують. На приймачі сума ВСЬОГО разом із сумою
# дає 0xFFFF — «нуль» в оберненому коді, тобто пакет цілий.

def fig_pipeline():
    W, H = 760, 396
    p = []
    words = ["0x4500", "0x003c", "0x1c46", "0x4000", "0x4006", "…"]
    bw, bh = 76, 32
    step = bw + 18
    x0 = 42
    y = 92
    for i, w in enumerate(words):
        p.append(rect(x0 + i * step, y, bw, bh, fill="#eaf0ff", stroke=NEG, sw=1.4, rx=5))
        p.append(text(x0 + i * step + bw / 2, y + bh / 2 + 5, w, size=12.5, color=INK, bold=True))
        if i < len(words) - 1:
            p.append(text(x0 + i * step + bw + 4, y + bh / 2 + 5, "+", size=14, color=INK, bold=True))
    p.append(text(x0, y - 14, "16-бітні слова (поля заголовка IPv4; поле суми занулене)",
                  size=11.5, color=MUTED, anchor="start", italic=True))

    b1, w1, h1 = textbox(W / 2, 172, "32-бітний акумулятор: складаємо всі слова",
                         size=12.5, bold=True, fill=FILL, stroke=INK, sw=1.6)
    p.append(b1)
    p.append(arrow(W / 2, y + bh + 4, W / 2, 172 - h1 / 2 - 2, color=INK, sw=1.6))

    b2, w2, h2 = textbox(W / 2, 228, "загорнути перенос:  s = (s & 0xFFFF) + (s >> 16),  доки є верхні біти",
                         size=12.5, bold=True, fill="#eef7f0", stroke=FIELD, sw=1.8, color=FIELD)
    p.append(b2)
    p.append(arrow(W / 2, 172 + h1 / 2, W / 2, 228 - h2 / 2 - 2, color=INK, sw=1.6))

    b3, w3, h3 = textbox(W / 2, 284, "інвертувати  ~s  →  контрольна сума = 0xB1E6",
                         size=12.5, bold=True, fill="#fff8e8", stroke=ACC, sw=2.0, color="#8a6d1f")
    p.append(b3)
    p.append(arrow(W / 2, 228 + h2 / 2, W / 2, 284 - h3 / 2 - 2, color=INK, sw=1.6))

    p.append(line(60, 328, 700, 328, color="#e4e4e4", sw=1.4))
    p.append(text(W / 2, 350, "приймач складає ВСІ слова разом із контрольною сумою → 0xFFFF",
                  size=12.5, color=INK, bold=True))
    p.append(text(W / 2, 372, "0xFFFF — це «−0», тобто нуль в оберненому коді: пакет цілий",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "pipeline.svg"), W, H, *p,
           title="Обчислення й перевірка інтернет-суми")


# ── byteorder: та сама сума в двох порядках байтів — дзеркала одна одної ───────
# Ідея: один і той самий буфер байтів, прочитаний як BE-слова й LE-слова, дає суми,
# що є побайтною перестановкою одна одної. Тож машини з різним порядком байтів
# рахують сумісно, не перевертаючи кожне слово.

def fig_byteorder():
    W, H = 760, 372
    p = []
    p.append(text(W / 2, 64, "один буфер:   байти  01 02 03 04", size=13, color=INK, bold=True))

    def column(cx, header, w1, w2, ssum, col):
        p.append(fitbox(cx - 120, 84, 240, 30, header, size=12, fill="#f4f6f8",
                        stroke=col, sw=1.4, bold=True, color=col))
        bw, bh = 104, 32
        p.append(rect(cx - bw / 2, 128, bw, bh, fill="#eaf0ff", stroke=NEG, sw=1.4, rx=5))
        p.append(text(cx, 128 + bh / 2 + 5, w1, size=13, color=INK, bold=True))
        p.append(text(cx, 182, "+", size=15, color=INK, bold=True))
        p.append(rect(cx - bw / 2, 190, bw, bh, fill="#eaf0ff", stroke=NEG, sw=1.4, rx=5))
        p.append(text(cx, 190 + bh / 2 + 5, w2, size=13, color=INK, bold=True))
        p.append(line(cx - bw / 2 - 6, 234, cx + bw / 2 + 6, 234, color=INK, sw=1.4))
        p.append(rect(cx - bw / 2 - 6, 242, bw + 12, 34, fill="#fff8e8", stroke=ACC, sw=2.0, rx=5))
        p.append(text(cx, 242 + 34 / 2 + 5, ssum, size=13.5, color="#8a6d1f", bold=True))

    column(210, "читаємо як BE-слова", "0x0102", "0x0304", "0x0406", NEG)
    column(550, "читаємо як LE-слова", "0x0201", "0x0403", "0x0604", FIELD)

    # подвійна стрілка «дзеркало» між сумами
    p.append(line(268, 259, 492, 259, color=MUTED, sw=1.6, dash="5 4"))
    p.append(text(380, 250, "побайтна", size=10.5, color=MUTED, bold=True))
    p.append(text(380, 296, "0x0406  ↔  0x0604   —   дзеркала одна одної", size=12.5, color=INK, bold=True))

    p.append(line(60, 318, 700, 318, color="#e4e4e4", sw=1.4))
    p.append(text(W / 2, 340, "тож обидва боки рахують СУМІСНО — не перевертаючи кожне слово перед сумою",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 361, "саме за це проєктувальники й обрали суму в оберненому коді",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "byteorder.svg"), W, H, *p,
           title="Чому інтернет-сума не залежить від порядку байтів")


# ── coverage: що накриває кожна сума; псевдозаголовок TCP/UDP ──────────────────
# Ідея: сума IP накриває ЛИШЕ заголовок (бо TTL міняється щохопу); сума TCP/UDP
# накриває свій заголовок + дані + віртуальний псевдозаголовок з IP-полів.

def fig_coverage():
    W, H = 880, 430
    p = []

    # ── верх: IP ──
    p.append(text(70, 66, "IPv4-датаграма", size=13, color=INK, anchor="start", bold=True))
    p.append(rect(70, 82, 360, 42, fill="#eef2fb", stroke=NEG, sw=1.5, rx=6))
    p.append(text(250, 100, "заголовок IPv4 (20 байтів)", size=12.5, color=INK, bold=True))
    p.append(text(250, 117, "…  TTL  ·  proto  ·  checksum  …", size=10.5, color=MUTED))
    p.append(rect(444, 82, 360, 42, fill="#f4f4f4", stroke="#c9c9c9", sw=1.4, rx=6))
    p.append(text(624, 106, "дані (TCP/UDP-сегмент)", size=12.5, color=MUTED))

    # дужка під самим заголовком
    p.append(line(70, 138, 70, 146, color=NEG, sw=1.6))
    p.append(line(430, 138, 430, 146, color=NEG, sw=1.6))
    p.append(line(70, 146, 430, 146, color=NEG, sw=1.6))
    p.append(text(250, 164, "IP checksum — лише заголовок", size=12, color=NEG, bold=True))
    p.append(text(250, 184, "TTL спадає щохопу → перераховують тільки заголовок, не дані",
                  size=10.8, color=MUTED, italic=True))

    p.append(line(60, 208, 820, 208, color="#e4e4e4", sw=1.4))

    # ── низ: TCP/UDP із псевдозаголовком ──
    p.append(text(70, 240, "псевдозаголовок (віртуальний — НЕ передається)", size=12,
                  color=FIELD, anchor="start", bold=True))
    ph = ["src IP", "dst IP", "0 · proto", "length"]
    bx, bw, bh, gap = 70, 86, 38, 8
    y = 252
    for i, lbl in enumerate(ph):
        x = bx + i * (bw + gap)
        p.append(rect(x, y, bw, bh, fill="#eef7f0", stroke=FIELD, sw=1.5, rx=5))
        p.append(text(x + bw / 2, y + bh / 2 + 5, lbl, size=11.5, color=INK, bold=True))
    xt = bx + 4 * (bw + gap) + 6
    p.append(rect(xt, y, 150, bh, fill="#eef2fb", stroke=NEG, sw=1.5, rx=5))
    p.append(text(xt + 75, y + bh / 2 + 5, "TCP/UDP заголовок", size=11, color=INK, bold=True))
    xd = xt + 150 + 10
    p.append(rect(xd, y, 170, bh, fill="#f4f4f4", stroke="#c9c9c9", sw=1.4, rx=5))
    p.append(text(xd + 85, y + bh / 2 + 5, "дані", size=12, color=MUTED, bold=True))

    # дужка через усе
    xr = xd + 170
    p.append(line(bx, y + bh + 8, bx, y + bh + 16, color=ACC, sw=1.8))
    p.append(line(xr, y + bh + 8, xr, y + bh + 16, color=ACC, sw=1.8))
    p.append(line(bx, y + bh + 16, xr, y + bh + 16, color=ACC, sw=1.8))
    p.append(text((bx + xr) / 2, y + bh + 36, "TCP/UDP checksum — псевдозаголовок + заголовок + дані",
                  size=12, color="#8a6d1f", bold=True))
    p.append(text((bx + xr) / 2, y + bh + 58,
                  "псевдозаголовок прив'язує суму до IP-адрес і протоколу — хибно доставлений пакет не пройде",
                  size=10.8, color=MUTED, italic=True))

    render(os.path.join(OUT, "coverage.svg"), W, H, *p,
           title="Що накриває кожна сума — і навіщо псевдозаголовок")


# ── two-zeros: два нулі оберненого коду і наслідки ────────────────────────────
# Ідея: 0x0000 (+0) і 0xFFFF (−0) — той самий нуль. Звідси елегантна перевірка
# й трюк UDP: 0 означає «суми нема», тож справжній нуль шлють як 0xFFFF.

def fig_two_zeros():
    W, H = 720, 336
    p = []

    def zerobox(cx, sign, hexv, bits, col, fill):
        p.append(rect(cx - 150, 72, 300, 60, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(cx, 96, "%s  =  %s" % (sign, hexv), size=15, color=col, bold=True))
        p.append(text(cx, 118, bits, size=10.5, color=MUTED))

    zerobox(200, "+0", "0x0000", "0000 0000 0000 0000", NEG, "#eef2fb")
    zerobox(520, "−0", "0xFFFF", "1111 1111 1111 1111", POS, "#fdeceb")
    p.append(text(W / 2, 158, "в оберненому коді це той самий нуль", size=13, color=INK, bold=True))

    b1, w1, h1 = textbox(W / 2, 202,
                         "перевірка:  Σ(усі слова + контрольна сума) = 0xFFFF  →  пакет цілий",
                         size=12, bold=True, fill="#eef7f0", stroke=FIELD, sw=1.7, color=FIELD)
    p.append(b1)
    b2, w2, h2 = textbox(W / 2, 252,
                         "UDP:  порахована сума 0x0000  →  у пакет кладуть 0xFFFF",
                         size=12, bold=True, fill="#fff8e8", stroke=ACC, sw=1.9, color="#8a6d1f")
    p.append(b2)

    p.append(line(60, 288, 660, 288, color="#e4e4e4", sw=1.4))
    p.append(text(W / 2, 310, "нуль означав би «суми нема»; в IPv6 сума обов'язкова, тож 0 там заборонено",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "two-zeros.svg"), W, H, *p,
           title="Два нулі оберненого коду: перевірка й трюк UDP")


# ── incr-update: точкове оновлення суми при зміні одного поля ──────────────────
# Ідея: сума лінійна, тож при зміні одного слова m → m' нову суму C' дістають
# із готової C, додавши ~m (відняти старе) і m' (додати нове); HC' = ~C'.

def fig_incr_update():
    W, H = 860, 372
    p = []
    words = ["w₁", "w₂", "m", "w₄", "w₅", "…"]
    bw, bh, gap = 88, 34, 18
    total = len(words) * bw + (len(words) - 1) * gap
    x0 = (W - total) / 2
    y = 96
    for i, w in enumerate(words):
        hot = (w == "m")
        p.append(rect(x0 + i * (bw + gap), y, bw, bh,
                      fill="#fff8e8" if hot else "#eef2fb",
                      stroke=ACC if hot else NEG, sw=2.0 if hot else 1.4, rx=5))
        p.append(text(x0 + i * (bw + gap) + bw / 2, y + bh / 2 + 5, w,
                      size=13, color="#8a6d1f" if hot else INK, bold=True))
        if i < len(words) - 1:
            p.append(text(x0 + i * (bw + gap) + bw + gap / 2, y + bh / 2 + 5, "+",
                          size=13, color=MUTED, bold=True))
    p.append(text(W / 2, y - 18,
                  "змінюється лише одне 16-бітне поле  —  решту суми не переобчислюємо",
                  size=12, color=MUTED, italic=True))

    cy = 236
    b1, w1, h1 = textbox(150, cy, "C = ~HC", size=13.5, bold=True,
                         fill=FILL, stroke=INK, sw=1.6, color=INK)
    b2, w2, h2 = textbox(470, cy, "C′", size=14, bold=True,
                         fill="#eef7f0", stroke=FIELD, sw=1.8, color=FIELD)
    b3, w3, h3 = textbox(762, cy, "HC′", size=14, bold=True,
                         fill="#fff8e8", stroke=ACC, sw=2.0, color="#8a6d1f")
    p += [b1, b2, b3]
    ax1a, ax1b = 150 + w1 / 2 + 6, 470 - w2 / 2 - 6
    ax2a, ax2b = 470 + w2 / 2 + 6, 762 - w3 / 2 - 6
    p.append(arrow(ax1a, cy, ax1b, cy, color=INK, sw=1.7))
    p.append(arrow(ax2a, cy, ax2b, cy, color=INK, sw=1.7))
    p.append(text((ax1a + ax1b) / 2, cy - 16, "+₁ ~m +₁ m′", size=12.5, color=INK, bold=True))
    p.append(text((ax1a + ax1b) / 2, cy + 26, "відняти старе, додати нове",
                  size=11, color=MUTED, italic=True))
    p.append(text((ax2a + ax2b) / 2, cy - 16, "~", size=16, color=INK, bold=True))
    p.append(text((ax2a + ax2b) / 2, cy + 26, "інвертувати один раз",
                  size=11, color=MUTED, italic=True))

    p.append(line(60, 306, 800, 306, color="#e4e4e4", sw=1.4))
    p.append(text(W / 2, 330, "одне-два додавання замість повного проходу по всьому заголовку",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 352, "сума лінійна: зсунулося одне слово — рівно на стільки ж зсувається й C",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "incr-update.svg"), W, H, *p,
           title="Точкове оновлення інтернет-суми")


# ── pm-zero: розвилка ±0 — RFC 1141 (хибно) проти RFC 1624 (правильно) ─────────
# Ідея: коли правильна нова сума — нуль, гола сума RFC 1141 дає −0 (0xFFFF), бо
# сума ненульових доданків не буває +0; RFC 1624 інвертує в кінці й дає +0.

def fig_pm_zero():
    W, H = 860, 432
    p = []
    p.append(text(W / 2, 46, "коли правильна нова сума — це нуль", size=13.5, color=INK, bold=True))
    b0, w0, h0 = textbox(W / 2, 90, "HC′  має бути  +0 = 0x0000",
                         size=12.5, bold=True, fill=FILL, stroke=INK, sw=1.6)
    p.append(b0)

    lx, rx = 232, 628
    p.append(arrow(W / 2 - 34, 90 + h0 / 2, lx + 60, 150, color=POS, sw=1.7))
    p.append(arrow(W / 2 + 34, 90 + h0 / 2, rx - 60, 150, color=FIELD, sw=1.7))

    def branch(cx, tag, col, tagfill, formula, note, result, ok):
        p.append(fitbox(cx - 176, 152, 352, 30, tag, size=12, bold=True,
                        fill=tagfill, stroke=col, sw=1.5, color=col))
        p.append(fitbox(cx - 176, 194, 352, 38, formula, size=12.5, bold=True,
                        fill="#f6f7f9", stroke=INK, sw=1.4, color=INK))
        p.append(text(cx, 256, note, size=11, color=MUTED, italic=True))
        p.append(rect(cx - 112, 276, 224, 44,
                      fill="#eef7f0" if ok else "#fdeceb", stroke=col, sw=2.0, rx=8))
        p.append(text(cx, 303, result, size=14, color=col, bold=True))
        p.append(text(cx, 338, "✓ правильно" if ok else "✗ хибно (−0 замість +0)",
                      size=11.5, color=col, bold=True))

    branch(lx, "RFC 1141 (1990) — гола сума", POS, "#fdeceb",
           "HC′ = HC +₁ m +₁ ~m′",
           "сума ненульових доданків не буває +0", "0xFFFF  (−0)", ok=False)
    branch(rx, "RFC 1624 (1994) — інверсія в кінці", FIELD, "#eef7f0",
           "HC′ = ~(~HC +₁ ~m +₁ m′)",
           "фінальне  ~  повертає −0 у +0", "0x0000  (+0)", ok=True)

    p.append(line(60, 374, 800, 374, color="#e4e4e4", sw=1.4))
    p.append(text(W / 2, 398,
                  "припущена дистрибутивність  ~  над сумою ламається саме на нулі — двоїстість оберненого коду",
                  size=11.6, color=INK, bold=True))
    p.append(text(W / 2, 418,
                  "RFC 1141 не «повертається» в область суми й не інвертує наприкінці, тож застряє на −0",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "pm-zero.svg"), W, H, *p,
           title="Помилка ±0: RFC 1141 проти RFC 1624")


# ── timeline: життєпис інтернет-суми від першого TCP до перевірки реальністю ───
# Ідея: наскрізна лінія історії — сума з'являється в першому TCP (1974),
# обґрунтована Пламмером (1978), канонізована Постелом (1980–81), зібрана в
# RFC 1071 (1988) і виміряна Стоуном–Партріджем (2000). Останній вузол —
# теплим/червоним, бо це поворот від задуму до перевірки реальністю.

def fig_timeline():
    W, H = 860, 620
    p = []
    x_spine = 214
    rows = [
        ("1974", "RFC 675 — перша специфікація TCP",
                 "Серф, Далал, Саншайн: сума вже вбудована", NEG, "#eef2fb"),
        ("1978", "IEN-45 — записка Вільяма Пламмера, BBN",
                 "чому обернена сума, а не XOR чи проста", NEG, "#eef2fb"),
        ("1980–81", "Постел канонізує стек: UDP · IP · TCP",
                 "RFC 768, 791, 793 — сума в усіх трьох", NEG, "#eef2fb"),
        ("1988", "RFC 1071 «Computing the Internet Checksum»",
                 "Бреден · Борман · Партрідж: швидкий рахунок", NEG, "#eef2fb"),
        ("2000", "Стоун і Партрідж, SIGCOMM: протверезіння",
                 "1 з 1100…32000 пакетів не проходить суму", POS, "#fdeceb"),
    ]
    yc = [96, 204, 312, 420, 540]   # останній вузол трохи нижче — відділяє поворот
    p.append(line(x_spine, yc[0], x_spine, yc[-1], color="#d7dbe0", sw=2.4))
    for (yr, l1, l2, col, fillc), y in zip(rows, yc):
        # рік — пігулка ліворуч
        p.append(fitbox(48, y - 18, 136, 36, yr, size=14, bold=True,
                        fill=fillc, stroke=col, sw=1.6, color=col))
        p.append(line(184, y, x_spine - 9, y, color=col, sw=1.6))     # рік → вузол
        p.append(circle(x_spine, y, 8, fill=fillc, stroke=col, sw=2.6))
        p.append(line(x_spine + 9, y, 252, y, color=col, sw=1.6))     # вузол → картка
        # картка праворуч
        p.append(rect(252, y - 30, 566, 60, fill=FILL, stroke=col, sw=1.7, rx=7))
        p.append(text(268, y - 6, l1, size=13.5, color=INK, anchor="start", bold=True))
        p.append(text(268, y + 15, l2, size=11.8, color=MUTED, anchor="start"))
    # тонкий підпис-роздільник перед поворотом
    p.append(text(268, 486, "задум і канон ↑     перевірка реальністю ↓",
                  size=11, color=MUTED, anchor="start", italic=True))
    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Життєпис інтернет-суми: від першого TCP до перевірки реальністю")


# ── pseudo-layout: побайтна розкладка псевдозаголовка IPv4 проти IPv6 ─────────
# Ідея (вставка proj): не «що накриває сума» (це показує coverage), а РІВНО які
# байти й у якому порядку викласти в акумулятор. IPv4 — 12 байтів, IPv6 — 40.

def fig_pseudo_layout():
    W, H = 828, 500
    p = []

    def column(x0, header, hcol, rows):
        p.append(fitbox(x0, 50, 348, 32, header, size=13, bold=True,
                        fill="#f4f6f8", stroke=hcol, sw=1.7, color=hcol))
        y = 100
        for row in rows:
            if isinstance(row, str):
                name, nb = row.split("|")
                p.append(rect(x0, y, 348, 46, fill="#eaf0ff", stroke=NEG, sw=1.5, rx=5))
                p.append(text(x0 + 14, y + 29, name, size=13, color=INK,
                              anchor="start", bold=True))
                p.append(text(x0 + 334, y + 29, nb, size=12.5, color=NEG,
                              anchor="end", bold=True))
            else:                                   # складений рядок із часток
                total = sum(n for _, n in row)
                cx = x0
                for label, nb in row:
                    w = 348.0 * nb / total
                    p.append(rect(cx, y, w, 46, fill="#fff8e8", stroke=ACC, sw=1.5, rx=5))
                    p.append(fitbox(cx + 4, y + 5, w - 8, 36,
                                    "%s\n%d б" % (label, nb), size=12, pad=4,
                                    fill="#fff8e8", stroke="#fff8e8", sw=0,
                                    color="#8a6d1f", bold=True))
                    cx += w
            y += 56

    column(40, "IPv4 — 12 байтів  (RFC 768 · RFC 9293)", NEG, [
        "Адреса відправника|4 б",
        "Адреса отримувача|4 б",
        [("нулі", 1), ("протокол", 1), ("довжина TCP/UDP", 2)],
    ])
    column(440, "IPv6 — 40 байтів  (RFC 8200, §8.1)", FIELD, [
        "Адреса відправника|16 б",
        "Адреса отримувача|16 б",
        "Довжина верхнього рівня|4 б",
        [("нулі", 3), ("Next Header", 1)],
    ])

    p.append(line(40, 388, 788, 388, color="#e4e4e4", sw=1.4))
    notes = [
        "Довжина тут — це довжина TCP/UDP (заголовок + дані), а НЕ довжина IP-пакета.",
        "Протокол / Next Header — це 6 (TCP) або 17 (UDP); в IPv6 з розширеннями воно",
        "НЕ дорівнює полю Next Header самого заголовка IPv6.",
    ]
    yy = 412
    for i, n in enumerate(notes):
        p.append(text(W / 2, yy + i * 20, n, size=12,
                      color=INK if i == 0 else MUTED, bold=(i == 0)))
    p.append(text(W / 2, 480, "Ці байти НІКОЛИ не йдуть у дріт — їх складають однаково "
                  "на обох кінцях лише щоб згодувати в суму",
                  size=12, color="#8a6d1f", italic=True))

    render(os.path.join(OUT, "pseudo-layout.svg"), W, H, *p,
           title="Що саме викласти в акумулятор: псевдозаголовок IPv4 і IPv6")


# ── odd-tail: акумулятор ковтає шматки; непарний хвіст доповнює НУЛЬ ──────────
# Ідея: не треба збирати суцільний буфер — додавання асоціативне, тож шматки
# ллють в один акумулятор. Нульовий добавок — віртуальний, у дріт не йде.

def fig_odd_tail():
    W, H = 828, 428
    p = []

    chunks = [(40, 214, "псевдозаголовок", "12 б", "#fff8e8", ACC, "#8a6d1f"),
              (270, 180, "заголовок UDP", "8 б", "#eef7f0", FIELD, FIELD),
              (466, 150, "дані «hello»", "5 б — НЕПАРНО", "#eaf0ff", NEG, NEG)]
    for x, w, name, nb, fill, col, tcol in chunks:
        p.append(rect(x, 62, w, 52, fill=fill, stroke=col, sw=1.7, rx=6))
        p.append(text(x + w / 2, 84, name, size=12.5, color=tcol, bold=True))
        p.append(text(x + w / 2, 103, nb, size=11.5, color=MUTED))
    # віртуальний нульовий добавок — пунктиром
    p.append(rect(632, 62, 74, 52, fill="#fdecea", stroke=POS, sw=1.7, rx=6))
    p.append(text(669, 84, "0x00", size=12.5, color=POS, bold=True))
    p.append(text(669, 103, "віртуальний", size=11, color=POS))
    p.append(text(724, 84, "домальовано", size=11.5, color=MUTED, anchor="start"))
    p.append(text(724, 103, "лише для суми", size=11.5, color=MUTED, anchor="start"))

    # шматки ллються в один акумулятор
    b, bw, bh = textbox(W / 2, 186, "один 32-бітний акумулятор: sum_words(шматок, sum)",
                        size=13, bold=True, fill=FILL, stroke=INK, sw=1.8)
    for x, w, *_ in chunks:
        p.append(arrow(x + w / 2, 118, W / 2 - 60 + (x / 8), 186 - bh / 2 - 3,
                       color=MUTED, sw=1.4))
    p.append(b)

    # деталь хвоста
    p.append(text(52, 246, "хвіст даних побайтно → 16-бітні слова:",
                  size=12, color=INK, anchor="start", bold=True))
    cells = [("68", "#eaf0ff", NEG), ("65", "#eaf0ff", NEG), ("6c", "#eaf0ff", NEG),
             ("6c", "#eaf0ff", NEG), ("6f", "#eaf0ff", NEG), ("00", "#fdecea", POS)]
    x0, cw = 52, 46
    for i, (t, fill, col) in enumerate(cells):
        p.append(rect(x0 + i * (cw + 6), 262, cw, 34, fill=fill, stroke=col, sw=1.5, rx=4))
        p.append(text(x0 + i * (cw + 6) + cw / 2, 284, t, size=12.5, color=col, bold=True))
    # дужки слів
    for i, w in enumerate(["0x6865", "0x6C6C", "0x6F00"]):
        cx = x0 + (2 * i) * (cw + 6) + cw + 3
        p.append(line(cx - cw / 2 - 3, 306, cx + cw / 2 + 3, 306, color=MUTED, sw=1.4))
        p.append(text(cx, 324, w, size=12.5, color=INK, bold=True))
    p.append(text(x0 + 6 * (cw + 6) + 16, 284, "← нуль справа: 0x6F → 0x6F00",
                  size=11.5, color=POS, anchor="start"))

    p.append(line(40, 348, 788, 348, color="#e4e4e4", sw=1.4))
    p.append(text(W / 2, 372, "У дріт іде лише заголовок UDP + дані — 13 байтів.",
                  size=12.5, color=INK, bold=True))
    p.append(text(W / 2, 394, "Псевдозаголовок і нульовий добавок віртуальні; "
                  "доповнювати нулем можна ЛИШЕ спільний хвіст, не кожен шматок.",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "odd-tail.svg"), W, H, *p,
           title="Шматки в один акумулятор і непарний хвіст")


if __name__ == "__main__":
    fig_pipeline()
    fig_byteorder()
    fig_coverage()
    fig_two_zeros()
    fig_incr_update()
    fig_pm_zero()
    fig_timeline()
    fig_pseudo_layout()
    fig_odd_tail()
    print("OK: figures written to", OUT)
