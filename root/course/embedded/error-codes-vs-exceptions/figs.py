# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── two-paths: код повернення тече крізь усі рамки, виняток перестрибує ────────
# Ідея: той самий ланцюг викликів A→B→C→D. Ліворуч помилка йде вгору руками,
# рядок за рядком (видима, але багатослівна). Праворуч throw з D перестрибує
# B і C одним стрибком прямо до catch в A — щасливі шляхи чисті, але потік
# керування невидимий між рамками.

def fig_two_paths():
    W, H = 720, 360
    p = []
    names = ["A: catch / if", "B", "C", "D: збій"]
    bw, bh = 150, 40
    gap = 22
    total = len(names) * bh + (len(names) - 1) * gap
    top = 78
    # дві колонки
    colx = [60, 430]
    titles = ["Коди повернення", "Винятки"]
    tcol = [INK, POS]
    for c in range(2):
        cx = colx[c] + bw / 2
        p.append(text(cx, 50, titles[c], size=14, bold=True, color=tcol[c]))
        ys = []
        for i, nm in enumerate(names):
            y = top + i * (bh + gap)
            ys.append(y)
            fill = "#fdecea" if i == len(names) - 1 else FILL
            p.append(fitbox(colx[c], y, bw, bh, nm, size=12, fill=fill, stroke=INK, sw=1.5, bold=(i == 0 or i == 3)))
        # стрілки виклику вниз (тонкі, сірі) — спільні для обох
        for i in range(len(names) - 1):
            xx = colx[c] + 28
            p.append(arrow(xx, ys[i] + bh, xx, ys[i + 1], color=MUTED, sw=1.3))
        if c == 0:
            # коди повернення: повернення вгору рамка за рамкою (червоні короткі)
            for i in range(len(names) - 1, 0, -1):
                xx = colx[c] + bw - 24
                p.append(arrow(xx, ys[i], xx, ys[i - 1] + bh, color=POS, sw=2.0))
            p.append(mtext(colx[c] + bw + 6, top + total / 2 - 18, "err повертають\nруками\nкрізь B і C",
                           size=10, color=POS, anchor="start"))
        else:
            # винятки: один довгий стрибок від D до A повз B,C
            xx = colx[c] + bw - 22
            p.append(arrow(xx, ys[-1], xx, ys[0] + bh, color=POS, sw=2.6))
            p.append(mtext(colx[c] + bw + 6, (ys[0] + ys[-1]) / 2 + bh / 2 - 18,
                           "throw\nперестрибує B і C\nодним махом",
                           size=10, color=POS, anchor="start"))

    p.append(text(W / 2, H - 18,
                  "ліворуч помилка видима в кожній рамці; праворуч проміжні рамки її не бачать",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "two-paths.svg"), W, H, *p,
           title="Дві дороги нагору: рядок за рядком проти одного стрибка")


# ── cost-ledger: ціна на щасливому шляху проти шляху помилки ───────────────────
# Ідея: чотири смуги-вартості. Коди: дешево і там, і там. Винятки: майже нуль на
# щасливому шляху (zero-cost), але дорого, коли throw (розкрутка стека).

def fig_cost_ledger():
    W, H = 700, 320
    p = []
    bx = 250                       # початок смуг
    maxw = 380                     # повна ширина = найдорожче
    rows = [
        ("Коди · щасливий шлях", 0.10, FIELD, "одне порівняння"),
        ("Коди · шлях помилки", 0.14, FIELD, "ще одне порівняння"),
        ("Винятки · щасливий шлях", 0.04, NEG, "майже нуль (zero-cost)"),
        ("Винятки · throw", 0.95, POS, "розкрутка стека — на порядки дорожче"),
    ]
    y = 70
    rh = 42
    for lab, frac, col, note in rows:
        p.append(text(bx - 12, y + rh / 2 + 4, lab, size=11, color=INK, anchor="end", bold=True))
        p.append(rect(bx, y, maxw, rh, fill="#f3f3f3", stroke="#dddddd", sw=1.0))
        w = max(8, maxw * frac)
        p.append(rect(bx, y, w, rh, fill=col, stroke=col, sw=1.0))
        # підпис вартості: усередині, якщо влазить, інакше праворуч
        if w > 150:
            p.append(text(bx + 10, y + rh / 2 + 4, note, size=10, color=BG, anchor="start", bold=True))
        else:
            p.append(text(bx + w + 8, y + rh / 2 + 4, note, size=10, color=col, anchor="start"))
        y += rh + 18

    p.append(text(W / 2, H - 18,
                  "коди — рівно дешево завжди; винятки переносять усю ціну на момент throw",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "cost-ledger.svg"), W, H, *p,
           title="Куди подівся кошт: щасливий шлях проти шляху помилки")


# ── spectrum: способи донести помилку від найтихішого до найгучнішого ──────────
# Ідея: горизонтальна вісь «локальне → глобальне». П'ять позначок: код повернення,
# Result/Either, errno, виняток, паніка. Дві філософії підписані під смугою.

def fig_spectrum():
    W, H = 720, 280
    p = []
    ax0, ax1, ay = 70, 650, 130
    p.append(line(ax0, ay, ax1, ay, color=INK, sw=2.0))
    p.append(arrow(ax1 - 1, ay, ax1 + 1, ay, color=INK, sw=2.0))

    stops = [
        (0.04, "код\nповернення", FIELD),
        (0.28, "Result /\nEither", FIELD),
        (0.50, "errno", MUTED),
        (0.74, "виняток", POS),
        (0.97, "паніка /\nreset", POS),
    ]
    for frac, lab, col in stops:
        x = ax0 + (ax1 - ax0) * frac
        p.append(circle(x, ay, 5, fill=col, stroke=col, sw=1))
        p.append(mtext(x, ay - 30, lab, size=11, color=col, bold=True))

    p.append(text(ax0, ay + 40, "явне, локальне, дешеве", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(ax1, ay + 40, "неявне, глобальне, дороге", size=11, color=POS, anchor="end", bold=True))

    # дужки двох філософій
    p.append(text(ax0 + (ax1 - ax0) * 0.18, ay + 78,
                  "значення-результат: помилку видно в типі", size=11, color=INK))
    p.append(text(ax0 + (ax1 - ax0) * 0.82, ay + 78,
                  "окремий канал: помилку видно осторонь коду", size=11, color=INK))

    render(os.path.join(OUT, "spectrum.svg"), W, H, *p,
           title="Спектр способів донести помилку")


# ── decision: одне питання — який стиль обрати на МК ───────────────────────────
# Ідея: коренева умова «детермінованість і кожен кілобайт критичні?» → так веде
# до кодів повернення (вбудоване), ні — до «винятки дозволені» (хост/десктоп).

def fig_decision():
    W, H = 700, 320
    p = []
    cx = W / 2
    root, rw, rh = textbox(cx, 70, "Потрібні передбачуваний час\nі найменший розмір коду?",
                           size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=12)
    p.append(root)

    # ліва гілка — ТАК → коди повернення
    lx = 175
    lb, lw, lh = textbox(lx, 210, "ТАК → коди повернення\n(вбудоване: ESP-IDF за\nзамовчуванням без винятків)",
                         size=11, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.8, pad=10)
    p.append(line(cx - rw * 0.18, 70 + rh / 2, lx, 210 - lh / 2, color=FIELD, sw=1.7))
    p.append(text((cx - rw * 0.18 + lx) / 2 - 16, (70 + rh / 2 + 210 - lh / 2) / 2 - 4,
                  "так", size=11, color=FIELD, bold=True, anchor="end"))
    p.append(lb)

    # права гілка — НІ → винятки дозволені
    rx = W - 175
    rbx, rbw, rbh = textbox(rx, 210, "НІ → винятки доречні\n(хост, десктоп, де чисті\nщасливі шляхи цінніші)",
                            size=11, bold=True, color=NEG, fill="#eef4ff", stroke=NEG, sw=1.8, pad=10)
    p.append(line(cx + rw * 0.18, 70 + rh / 2, rx, 210 - rbh / 2, color=NEG, sw=1.7))
    p.append(text((cx + rw * 0.18 + rx) / 2 + 16, (70 + rh / 2 + 210 - rbh / 2) / 2 - 4,
                  "ні", size=11, color=NEG, bold=True, anchor="start"))
    p.append(rbx)

    p.append(text(W / 2, H - 16,
                  "на мікроконтролері відповідь майже завжди «так» — звідси канон кодів повернення",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "decision.svg"), W, H, *p,
           title="Який стиль обрати: одне питання")


if __name__ == "__main__":
    fig_two_paths()
    fig_cost_ledger()
    fig_spectrum()
    fig_decision()
    print("OK: figures written to", OUT)
