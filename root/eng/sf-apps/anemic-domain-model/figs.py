import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: анатомія — знекровлений об'єкт проти багатого ───────────────────
# Ліворуч: голий мішок полів, правила орбітують ЗЗОВНІ в сервісах, стрілки лізуть
# усередину читати й писати. Праворуч: дані + поведінка за однією стіною, один наказ.
def anatomy():
    W, H = 940, 470
    frags = []
    frags.append(text(235, 52, "Знекровлена модель", size=18, bold=True, color=POS))
    frags.append(text(705, 52, "Багата модель", size=18, bold=True, color=FIELD))
    frags.append(line(470, 78, 470, H - 24, color=MUTED, sw=1.2, dash="6 6"))

    # ЛІВА ПАНЕЛЬ ───────────────────────────────────────────────
    # голий об'єкт-дані по центру-низу лівої панелі
    ox, oy, ow, oh = 120, 300, 230, 118
    frags.append(rect(ox, oy, ow, oh, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(ox + ow / 2, oy + 24, "Order (самі дані)", size=14, bold=True, color=POS))
    frags.append(mtext(ox + ow / 2, oy + 52, ["status  total  discount", "items  customerId"],
                       size=12.5, color=INK, lh=1.35))
    frags.append(text(ox + ow / 2, oy + oh - 12, "геттери / сеттери на все", size=11.5,
                      italic=True, color=MUTED))

    # три сервіси-правила орбітують зверху
    svc = [("OrderService", 90), ("PricingService", 235), ("CheckoutService", 380)]
    for name, cx in svc:
        b, bw, bh = textbox(cx, 150, name, size=12, pad=9, fill=FILL, stroke=LINE, sw=1.5, bold=True)
        frags.append(b)
    frags.append(text(235, 108, "правила живуть ТУТ, зовні", size=12, italic=True, color=MUTED))
    # стрілки: сервіси лізуть у поля (читати й писати) — тонкі червоні, збігаються
    # на верхні кути об'єкта, ЖОДНА не проходить крізь підпис нижче
    frags.append(arrow(90, 168, 150, oy - 2, color=POS, sw=1.6))
    frags.append(arrow(235, 172, 175, oy - 2, color=POS, sw=1.6))
    frags.append(arrow(380, 168, 320, oy - 2, color=POS, sw=1.6))
    # підпис у чистій смузі праворуч від стрілок, поза їхніми лініями
    frags.append(mtext(360, 210, ["тягнуть поля,", "вирішують за них,", "вписують назад"],
                       size=11.5, color=POS, anchor="start", lh=1.35))

    # ПРАВА ПАНЕЛЬ ───────────────────────────────────────────────
    # один об'єкт: дані + поведінка за стіною
    rx, ry, rw, rh = 588, 132, 234, 250
    frags.append(rect(rx, ry, rw, rh, fill="#eafaf0", stroke=FIELD, sw=2.2))
    frags.append(text(rx + rw / 2, ry + 26, "Order", size=15, bold=True, color=FIELD))
    # дані
    frags.append(line(rx + 16, ry + 40, rx + rw - 16, ry + 40, color=FIELD, sw=1))
    frags.append(mtext(rx + rw / 2, ry + 62, ["дані: status  total", "discount  items"],
                       size=12, color=MUTED, lh=1.35))
    frags.append(line(rx + 16, ry + 96, rx + rw - 16, ry + 96, color=FIELD, sw=1))
    # поведінка
    frags.append(text(rx + rw / 2, ry + 118, "поведінка (правила тут):", size=11.5,
                      italic=True, color=INK))
    frags.append(mtext(rx + rw / 2, ry + 144, ["applyDiscount()", "checkout()", "cancel()"],
                       size=13, color=INK, bold=True, lh=1.35))
    frags.append(text(rx + rw / 2, ry + rh - 14, "інваріанти під охороною", size=11.5,
                      italic=True, color=FIELD))

    # викликач збоку каже ОДИН наказ
    b, bw, bh = textbox(600, 60, "викликач", size=12, pad=8, fill=FILL, stroke=LINE, sw=1.5)
    frags.append(b)
    frags.append(arrow(640, 72, 705, ry - 2, color=FIELD, sw=2))
    frags.append(text(760, 92, "checkout()", size=12.5, color=FIELD, bold=True))
    frags.append(text(760, 108, "лише наказ", size=11, italic=True, color=MUTED))

    render(os.path.join(OUT, 'anemic-vs-rich.svg'), W, H, *frags)


# ── Фігура 2: коли знекровлена модель доречна, а коли ні ──────────────────────
def when_ok():
    W, H = 900, 340
    frags = []
    # питання-різак угорі
    b, bw, bh = textbox(450, 52, "Скільки правил над цими даними?", size=15, pad=12,
                        fill=FILL, stroke=LINE, sw=1.8, bold=True)
    frags.append(b)

    # ліва гілка — мало правил → доречно
    frags.append(arrow(360, 78, 220, 128, color=NEG, sw=1.8))
    frags.append(text(255, 108, "майже нема", size=12.5, color=NEG, italic=True))
    lx, ly, lw, lh = 60, 132, 330, 168
    frags.append(rect(lx, ly, lw, lh, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(lx + lw / 2, ly + 26, "плаский об'єкт — доречно", size=13.5, bold=True, color=NEG))
    frags.append(mtext(lx + lw / 2, ly + 54,
                       ["CRUD-форма, довідник, звіт,",
                        "перекладання даних між шарами.",
                        "Правил обмаль — сервіс-процедура",
                        "простий, зрозумілий, легкий."],
                       size=12, color=INK, lh=1.4))
    frags.append(text(lx + lw / 2, ly + lh - 14, "це не хвороба, а вибір", size=11.5,
                      italic=True, color=NEG))

    # права гілка — багато правил → анти-патерн
    frags.append(arrow(540, 78, 690, 128, color=POS, sw=1.8))
    frags.append(text(660, 108, "багато й ростуть", size=12.5, color=POS, italic=True))
    px, py, pw, ph = 510, 132, 330, 168
    frags.append(rect(px, py, pw, ph, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(px + pw / 2, py + 26, "знекровлення — анти-патерн", size=13.5, bold=True, color=POS))
    frags.append(mtext(px + pw / 2, py + 54,
                       ["Стани, переходи, інваріанти.",
                        "Правило розсипане по сервісах:",
                        "дублюється або губиться,",
                        "об'єкт не володіє собою."],
                       size=12, color=INK, lh=1.4))
    frags.append(text(px + pw / 2, py + ph - 14, "правило шукає дім — сам об'єкт", size=11.5,
                      italic=True, color=POS))

    render(os.path.join(OUT, 'when-anemic-ok.svg'), W, H, *frags)


anatomy()
when_ok()
print("ok")
