# -*- coding: utf-8 -*-
"""Фігури до кроку «Ризик-реєстр Digital Homes». Вивід — ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: реєстр DH на сітці загрози (ймовірність × вплив) ───────────────
def fig_grid():
    W, H = 760, 660
    gx, gy = 150, 70
    gw, gh = 520, 500
    cw, ch = gw / 2, gh / 2
    frags = []

    # осі
    frags.append(text(gx + gw / 2, gy + gh + 42,
                      "Вплив, якщо станеться:  малий  →  великий", size=15, bold=True))
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="15" fill="%s" '
                 'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">'
                 'Імовірність:  низька  →  висока</text>'
                 % (gx - 42, gy + gh / 2, FONT, INK, gx - 42, gy + gh / 2))

    # (col, row, заливка, колір рамки, дві короткі лінії-дія)
    cells = [
        (1, 0, "#fdecea", POS,           ["часто й боляче", "вся увага сюди"]),
        (1, 1, "#fef6e7", "#b8860b",     ["рідко, та катастрофа", "тримай план"]),
        (0, 0, "#eaf3ec", FIELD,         ["часто, але дрібно", "гаси по ходу"]),
        (0, 1, "#eef1f5", MUTED,         ["рідко й дрібно", "прийми й забудь"]),
    ]
    # ризик-теги по кутах: (col,row) -> список підписів
    tags = {
        (1, 0): ["розум дому — у хмарі", "замок: двічі або пізно", "прошивку не полагодиш"],
        (1, 1): ["вендор вимкне сервіс"],
        (0, 0): ["дірки в телеметрії"],
        (0, 1): ["перейменування кімнати"],
    }

    for col, row, fill, br, head in cells:
        x = gx + col * cw
        y = gy + row * ch
        frags.append(rect(x, y, cw, ch, fill=fill, stroke=br, sw=2, rx=10))
        cx = x + cw / 2
        # заголовок-дія (дві короткі лінії, кольором рамки)
        frags.append(mtext(cx, y + 28, head, size=14, color=br, bold=True, lh=1.25))
        # ризик-теги
        tg = tags[(col, row)]
        start = y + 78
        for i, t in enumerate(tg):
            cyi = start + i * 52
            frags.append(fitbox(cx - 119, cyi - 17, 238, 34, t,
                                size=13, fill=BG, stroke=br, sw=1.5, rx=17))

    return render(os.path.join(IMG, "grid.svg"), W, H, *frags,
                  title="Реєстр Digital Homes на сітці загрози")


# ── Фігура 2: живий рядок сповзає по сітці — зріз збив ймовірність ───────────
def fig_living():
    W, H = 640, 560
    gx, gy = 150, 90
    gw, gh = 360, 360
    cw, ch = gw / 2, gh / 2
    frags = []

    # клітини (ті самі осі, що й у сітці загрози)
    frags.append(rect(gx, gy, cw, ch, fill="#eef1f5", stroke=MUTED, sw=1.5, rx=8))
    frags.append(rect(gx + cw, gy, cw, ch, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    frags.append(rect(gx, gy + ch, cw, ch, fill="#eef1f5", stroke=MUTED, sw=1.5, rx=8))
    frags.append(rect(gx + cw, gy + ch, cw, ch, fill="#fef6e7", stroke="#b8860b", sw=1.8, rx=8))

    # осі
    frags.append(text(gx + gw / 2, gy + gh + 42, "Вплив:  малий  →  великий", size=14, bold=True))
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="14" fill="%s" '
                 'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">'
                 'Імовірність:  низька  →  висока</text>'
                 % (gx - 40, gy + gh / 2, FONT, INK, gx - 40, gy + gh / 2))

    # стрілка руху (спершу, щоб маркери лягли зверху)
    frags.append(arrow(420, 214, 420, 326))

    # маркер тижня 1 — велика загроза, ймовірність туманна (верх-право)
    frags.append(circle(420, 160, 16, fill="#fdecea", stroke=POS, sw=2.5))
    frags.append(text(420, 166, "1", size=17, color=POS, bold=True))
    frags.append(text(420, 126, "тиждень 1", size=13, bold=True))
    frags.append(text(420, 200, "ймовірність: ?", size=12, color=MUTED))

    # маркер тижня 3 — ймовірність збита зрізом (низ-право)
    frags.append(circle(420, 380, 16, fill="#eaf3ec", stroke=FIELD, sw=2.5))
    frags.append(text(420, 386, "3", size=17, color=FIELD, bold=True))
    frags.append(text(420, 350, "тиждень 3", size=13, bold=True))
    frags.append(text(420, 420, "ймовірність: низька", size=12, color=MUTED))

    # підпис до руху (ліворуч від стрілки, подалі від ліній)
    frags.append(mtext(238, 236, ["зріз збив", "невизначеність"],
                       size=13, color=INK, bold=True, lh=1.25))

    return render(os.path.join(IMG, "living.svg"), W, H, *frags,
                  title="Живий рядок сповзає по сітці: зріз збив ймовірність")


# ── Фігура 3 (вставка hist): десять років — той самий урок ───────────────────
def fig_timeline():
    W, H = 800, 560
    sx, r = 110, 26                     # хребет часу і радіус вузла-року
    cardx, cardw = 150, 620
    tx = cardx + 20
    y0, rowh, cardh = 74, 116, 92
    GOLD = "#b8860b"                    # колір кута «вендор вимкне сервіс» із сітки DH
    events = [
        ("2016", GOLD, "Revolv (Nest): хмару вимкнено 15.05.2016",
         "хаб за $299 став цеглою — місяць попередження",
         "→ реєстр DH: «вендор вимкне сервіс»"),
        ("2017", POS,  "LockState: крива прошивка, 7 серпня 2017",
         "~500 замків, ~200 хостів Airbnb; ключ рятував",
         "→ реєстр DH: «прошивку не полагодиш», «команда замку»"),
        ("2020", GOLD, "Wink: раптова підписка $4.99/міс, травень 2020",
         "«без абонплати» на коробці — і хаб за платіж",
         "→ реєстр DH: «вендор підніме ціну»"),
        ("2022", GOLD, "Insteon: сервери зникли без слова, квітень 2022",
         "локальні хаби мертві — конфіг ходив у хмару",
         "→ реєстр DH: «вендор вимкне сервіс»"),
    ]
    frags = []
    cys = [y0 + i * rowh + cardh / 2 for i in range(len(events))]
    # хребет часу — відрізками МІЖ вузлами (лінія не заходить під текст року)
    for i in range(len(cys) - 1):
        frags.append(line(sx, cys[i] + r, sx, cys[i + 1] - r, color=MUTED, sw=2.5))
    for i, (yr, accent, l1, l2, l3) in enumerate(events):
        y = y0 + i * rowh
        cy = cys[i]
        frags.append(rect(cardx, y, cardw, cardh, fill=BG, stroke=accent, sw=1.8, rx=10))
        frags.append(rect(cardx, y, 7, cardh, fill=accent, stroke=accent, sw=0, rx=3))
        frags.append(circle(sx, cy, r, fill=BG, stroke=accent, sw=2.5))
        frags.append(text(sx, cy + 5, yr, size=15, color=accent, bold=True))
        frags.append(text(tx, y + 30, l1, size=14, color=INK, anchor="start", bold=True))
        frags.append(text(tx, y + 53, l2, size=13, color=MUTED, anchor="start"))
        frags.append(text(tx, y + 76, l3, size=13, color=accent, anchor="start", bold=True))
    return render(os.path.join(IMG, "timeline.svg"), W, H, *frags,
                  title="Десять років, той самий урок")


# ── Фігура 4 (вставка proj): реєстр як конвеєр, що впирається в гейт CI ──────
def fig_lintgate():
    W, H = 720, 600
    cx = 360
    frags = []

    def box(x, y, w, h, s, fill=FILL, stroke=INK, size=15, bold=False):
        return fitbox(x, y, w, h, s, size=size, fill=fill, stroke=stroke,
                      sw=1.8, rx=10, bold=bold)

    # 1 — реєстр як дані
    frags.append(box(140, 52, 440, 46, "реєстр DH — список рядків-даних", bold=True))
    frags.append(arrow(cx, 98, cx, 132))

    # 2 — експозиція з трьох щаблів
    frags.append(box(170, 134, 380, 56,
                     ["1 · експозиція = ймовірність × вплив",
                      "щаблі  1·2·3   ×   1·3·4"], size=14))
    frags.append(arrow(cx, 190, cx, 224))

    # 3 — сортування за загрозою
    frags.append(box(190, 226, 340, 44, "2 · сортувати за загрозою (спад)", size=14))
    frags.append(arrow(cx, 270, cx, 300))

    # 4 — гейт лінта живості
    frags.append(rect(86, 302, 548, 156, fill="#fbfbfc", stroke=POS, sw=2, rx=12))
    frags.append(text(cx, 330, "3 · лінт живості — падає від першого «так»",
                      size=15, color=POS, bold=True))
    checks = [
        "•  рядок не чіпали > N днів  →  застій",
        "•  важкий відкритий ризик без тригера",
        "•  важкий відкритий ризик без власника",
    ]
    frags.append(mtext(120, 366, checks, size=14, color=INK, anchor="start", lh=2.0))

    # 5 — розвилка CI
    frags.append(arrow(325, 462, 240, 500))
    frags.append(arrow(395, 462, 480, 500))
    frags.append(fitbox(104, 502, 232, 66, ["жодного «так»", "CI зелений · exit 0"],
                        size=13, fill="#eaf3ec", stroke=FIELD, sw=1.8, rx=10, bold=True))
    frags.append(fitbox(384, 502, 232, 66, ["є «так»", "CI падає · exit 1"],
                        size=13, fill="#fdecea", stroke=POS, sw=1.8, rx=10, bold=True))

    return render(os.path.join(IMG, "lintgate.svg"), W, H, *frags,
                  title="Реєстр як конвеєр, що впирається в гейт CI")


if __name__ == "__main__":
    print(fig_grid())
    print(fig_living())
    print(fig_timeline())
    print(fig_lintgate())
