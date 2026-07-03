# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: одна вибірка — лотерея; п'ять розбиттів дають різні числа ──────
def fig_one_split_lottery():
    W, H = 720, 330
    f = []
    f.append(text(W/2, 26, "Один поділ — лотерея: та сама модель, різні числа", size=16, bold=True))

    # смуга даних угорі
    bx, by, bw, bh = 60, 62, 600, 34
    n = 20
    cw = bw / n
    import random
    random.seed(11)
    f.append(text(W/2, by - 10, "той самий набір даних", size=12, color=MUTED))
    for i in range(n):
        f.append(rect(bx + i*cw, by, cw - 2, bh, fill="#eef2ff", stroke=NEG, sw=1))

    # три різні випадкові поділи → три різні точності
    rows = [
        ("поділ A", [4, 9, 13],       "точність 91%"),
        ("поділ B", [1, 7, 16],       "точність 78%"),
        ("поділ C", [10, 14, 18],     "точність 85%"),
    ]
    y0 = 140
    dy = 52
    for r, (name, holdout, acc) in enumerate(rows):
        cy = y0 + r*dy
        f.append(text(bx - 6, cy + bh/2 - 2, name, size=12, color=INK, anchor="end", bold=True))
        for i in range(n):
            fill = "#fdecea" if i in holdout else "#f4f6f8"
            st = POS if i in holdout else LINE
            f.append(rect(bx + i*cw, cy, cw - 2, bh - 8, fill=fill, stroke=st, sw=1))
        f.append(text(bx + bw + 10, cy + (bh-8)/2 - 2, acc, size=13, color=POS, bold=True, anchor="start"))

    box, _, _ = textbox(W/2, H - 20,
        "рожеве — приклади, що випали в «іспит»;  саме розбиття вирішує число → воно скаче на 13%",
        size=12, pad=9, fill="#fff8e1", stroke="#c9a227")
    f.append(box)
    render(os.path.join(OUT, 'one-split-lottery.svg'), W, H, *f)


# ── Фігура 2: 5-кратна крос-валідація — кожен блок раз побув «іспитом» ───────
def fig_kfold():
    W, H = 720, 360
    f = []
    f.append(text(W/2, 24, "5-кратна крос-валідація: кожен блок один раз — «іспит»", size=16, bold=True))

    k = 5
    bx = 150
    bw = 430
    blk = bw / k
    y0 = 62
    bh = 34
    dy = 46

    # заголовок блоків
    for j in range(k):
        f.append(text(bx + j*blk + blk/2, y0 - 8, "блок %d" % (j+1), size=11, color=MUTED))

    accs = ["88%", "84%", "90%", "86%", "87%"]
    for r in range(k):
        cy = y0 + r*dy
        f.append(text(bx - 10, cy + bh/2 - 2, "прохід %d" % (r+1), size=12, anchor="end", bold=True))
        for j in range(k):
            if j == r:
                fill, st, lab = "#fdecea", POS, "іспит"
            else:
                fill, st, lab = "#e9f7ef", FIELD, "навч."
            f.append(rect(bx + j*blk, cy, blk - 3, bh, fill=fill, stroke=st, sw=1.4))
            f.append(text(bx + j*blk + blk/2, cy + bh/2 + 3, lab, size=10,
                          color=(POS if j == r else FIELD)))
        f.append(text(bx + bw + 12, cy + bh/2 + 3, "→ " + accs[r], size=12,
                      color=INK, bold=True, anchor="start"))

    box, _, _ = textbox(W/2, H - 22,
        "кожен приклад перевірено РІВНО раз;  підсумок = середнє п'яти чисел ≈ 87%  (± розкид)",
        size=12, pad=10, fill="#fff8e1", stroke="#c9a227")
    f.append(box)
    render(os.path.join(OUT, 'kfold.svg'), W, H, *f)


# ── Фігура 3: витік — масштабування ДО поділу заглядає в «іспит» ─────────────
def fig_leakage():
    W, H = 720, 340
    f = []
    f.append(text(W/2, 24, "Витік даних: підготовка ДО поділу підглядає в «іспит»", size=15, bold=True))

    # ліва панель — НЕПРАВИЛЬНО
    lx = 40
    b, w, _ = textbox(lx + 150, 78, "НЕПРАВИЛЬНО", size=13, pad=8,
                      fill="#fdecea", stroke=POS, bold=True, color=POS)
    f.append(b)
    steps_bad = [
        ("порахувати норму", "на ВСІХ даних", "#fdecea", POS),
        ("поділити", "навч. | іспит", "#f4f6f8", MUTED),
        ("навчити й оцінити", "оцінка ЗАВИЩЕНА", "#fdecea", POS),
    ]
    y = 118
    for title, sub, fill, col in steps_bad:
        f.append(fitbox(lx + 20, y, 260, 42, title + "\n" + sub, size=12, fill=fill, stroke=col))
        if y < 118 + 2*58:
            f.append(arrow(lx + 150, y + 42, lx + 150, y + 58, color=MUTED, sw=1.8))
        y += 58

    # права панель — ПРАВИЛЬНО
    rx = 400
    b, w, _ = textbox(rx + 150, 78, "ПРАВИЛЬНО", size=13, pad=8,
                      fill="#e9f7ef", stroke=FIELD, bold=True, color=FIELD)
    f.append(b)
    steps_ok = [
        ("поділити", "навч. | іспит", "#f4f6f8", MUTED),
        ("порахувати норму", "лише на НАВЧ.", "#e9f7ef", FIELD),
        ("застосувати й оцінити", "оцінка ЧЕСНА", "#e9f7ef", FIELD),
    ]
    y = 118
    for title, sub, fill, col in steps_ok:
        f.append(fitbox(rx + 20, y, 260, 42, title + "\n" + sub, size=12, fill=fill, stroke=col))
        if y < 118 + 2*58:
            f.append(arrow(rx + 150, y + 42, rx + 150, y + 58, color=MUTED, sw=1.8))
        y += 58

    box, _, _ = textbox(W/2, H - 20,
        "будь-яка підготовка (норма, відбір ознак) живе ВСЕРЕДИНІ навчального блоку — інакше «іспит» уже підглянуто",
        size=11, pad=9, fill="#fff8e1", stroke="#c9a227")
    f.append(box)
    render(os.path.join(OUT, 'leakage.svg'), W, H, *f)


# ── Фігура 4: нарізка N=203 на k=5 — залишок роздано першим блокам ───────────
def fig_fold_sizes():
    W, H = 720, 300
    f = []
    f.append(text(W/2, 26, "N=203 на 5 блоків: залишок r=3 роздано першим блокам", size=16, bold=True))

    # рядок формули
    f.append(text(W/2, 54, "203 / 5  →  база 40,  залишок r = 203 mod 5 = 3", size=13, color=MUTED))

    k = 5
    sizes = [41, 41, 41, 40, 40]     # перші r=3 — по 41, решта по 40
    base = 40
    bx = 70
    gap = 16
    slot = (W - 2*bx - (k-1)*gap) / k   # ширина колонки блоку
    top = 90
    unit = 2.4                          # px на приклад по висоті
    maxh = base * unit                  # висота бази

    for j in range(k):
        cx = bx + j*(slot + gap)
        # базова частина (40) — сіра
        bh = base * unit
        by = top + (maxh - bh)
        f.append(rect(cx, by, slot, bh, fill="#eef2ff", stroke=NEG, sw=1.4))
        # «довгий» блок дістав +1 із залишку — зелена шапка згори
        if sizes[j] > base:
            eh = unit * 6            # намалюємо шапку помітно (символічно 1 приклад)
            f.append(rect(cx, by - eh, slot, eh, fill="#e9f7ef", stroke=FIELD, sw=1.6))
        # підпис розміру
        f.append(text(cx + slot/2, top + maxh + 20, "%d" % sizes[j], size=15, bold=True,
                      color=(FIELD if sizes[j] > base else INK)))
        f.append(text(cx + slot/2, top + maxh + 38, "блок %d" % (j+1), size=11, color=MUTED))

    # легенда «+1 із залишку»
    f.append(rect(bx, top - 6, 14, 10, fill="#e9f7ef", stroke=FIELD, sw=1.4))
    f.append(text(bx + 20, top + 3, "+1 приклад із залишку", size=11, color=FIELD, anchor="start"))

    box, _, _ = textbox(W/2, H - 20,
        "41·3 + 40·2 = 203  —  жоден приклад не пропав;  найбільший блок лише на 1 більший за найменший",
        size=12, pad=9, fill="#fff8e1", stroke="#c9a227")
    f.append(box)
    render(os.path.join(OUT, 'fold-sizes.svg'), W, H, *f)


# ── Фігура 5: стратифікований round-robin — кожен клас роздано по колу ────────
def fig_stratified():
    W, H = 720, 350
    f = []
    f.append(text(W/2, 24, "Стратифікований поділ по колу: пропорція класів у кожнім блоці", size=15, bold=True))

    k = 5
    bx = 90
    gap = 18
    slot = (W - 2*bx - (k-1)*gap) / k
    top = 74
    bh = 150
    dot = 9

    # у кожен блок: 2 червоні (брак) + 8 сірих (добрі)
    for j in range(k):
        cx = bx + j*(slot + gap)
        f.append(rect(cx, top, slot, bh, fill="#fbfbfd", stroke=LINE, sw=1.4))
        f.append(text(cx + slot/2, top - 8, "блок %d" % (j+1), size=11, color=MUTED))
        # 2 червоні згори
        for r in range(2):
            f.append(circle(cx + slot/2, top + 22 + r*22, dot, fill="#fdecea", stroke=POS, sw=1.8))
        # 8 сірих нижче (2 стовпчики по 4)
        for idx in range(8):
            col = idx % 2
            row = idx // 2
            ddx = -14 if col == 0 else 14
            f.append(circle(cx + slot/2 + ddx, top + 74 + row*18, dot - 1,
                            fill="#eceef2", stroke=MUTED, sw=1.4))
        f.append(text(cx + slot/2, top + bh + 16, "2 : 8", size=13, bold=True, color=INK))

    # легенда
    f.append(circle(bx + 6, top + bh + 44, 8, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(bx + 20, top + bh + 48, "брак (10 усього → по 2)", size=11, color=POS, anchor="start"))
    f.append(circle(bx + 300, top + bh + 44, 7, fill="#eceef2", stroke=MUTED, sw=1.4))
    f.append(text(bx + 314, top + bh + 48, "добрі (40 усього → по 8)", size=11, color=MUTED, anchor="start"))

    box, _, _ = textbox(W/2, H - 18,
        "кожен клас роздано по колу ОКРЕМО → у кожнім блоці та сама пропорція 1:4, що й у наборі",
        size=12, pad=9, fill="#fff8e1", stroke="#c9a227")
    f.append(box)
    render(os.path.join(OUT, 'stratified.svg'), W, H, *f)


# ── Фігура (hist): родина розбиттів — навпіл / k-кратне / викидання одного ────
def fig_split_family():
    W, H = 720, 330
    f = []
    f.append(text(W/2, 24, "Три способи розрізати дані: навпіл → k блоків → по одному",
                  size=15, bold=True))

    n = 12                      # клітинок у смузі даних
    panel_w = 200
    gap = 30
    x0 = 30
    top = 78
    bh = 26                     # висота рядка-смуги
    dy = 34

    def strip(px, py, holdout_set):
        cw = panel_w / n
        for i in range(n):
            fill = "#fdecea" if i in holdout_set else "#e9f7ef"
            st = POS if i in holdout_set else FIELD
            f.append(rect(px + i*cw, py, cw - 2, bh, fill=fill, stroke=st, sw=1))

    titles = ["поділ навпіл", "k-кратне (k=4)", "викидання одного"]
    for p, t in enumerate(titles):
        px = x0 + p*(panel_w + gap)
        f.append(text(px + panel_w/2, top - 10, t, size=12, color=INK, bold=True))

    # Панель A — поділ навпіл: один рядок, права половина — іспит
    pxA = x0
    strip(pxA, top, set(range(n//2, n)))
    f.append(text(pxA + panel_w/2, top + bh + 18, "один іспит (пів даних)",
                  size=10, color=MUTED))

    # Панель B — k=4: чотири рядки, у кожному свій блок (3 клітинки) — іспит
    pxB = x0 + (panel_w + gap)
    kk = 4
    blk = n // kk
    for r in range(kk):
        py = top + r*dy
        hold = set(range(r*blk, r*blk + blk))
        strip(pxB, py, hold)
    f.append(text(pxB + panel_w/2, top + kk*dy + 4, "кожен блок раз — іспит",
                  size=10, color=MUTED))

    # Панель C — leave-one-out: кілька рядків, у кожному ОДНА клітинка
    pxC = x0 + 2*(panel_w + gap)
    show = 4
    for r in range(show):
        py = top + r*dy
        strip(pxC, py, {r})
    f.append(text(pxC + panel_w/2, top + show*dy - 6, "…", size=14, color=MUTED))
    f.append(text(pxC + panel_w/2, top + show*dy + 10, "кожен приклад — окремий іспит",
                  size=10, color=MUTED))

    box, _, _ = textbox(W/2, H - 20,
        "рожеве — «іспит», зелене — «навчання»;  думка рухалася зліва направо: усе ощадніше з даними",
        size=11, pad=9, fill="#fff8e1", stroke="#c9a227")
    f.append(box)
    render(os.path.join(OUT, 'split-family.svg'), W, H, *f)


# ── Фігура (hist): два незалежні формулювання 1974–75 сходяться ──────────────
def fig_two_1974():
    W, H = 720, 320
    f = []
    f.append(text(W/2, 24, "1974–75: два незалежні шляхи до методу", size=16, bold=True))

    # ліва картка — Стоун
    lb, lw, lh = textbox(190, 96, "Мервін Стоун\nUCL, Лондон · JRSS-B · 1974",
                         size=12, pad=10, fill="#eaf0fd", stroke=NEG, bold=True, color=NEG)
    f.append(lb)
    f.append(fitbox(60, 132, 260, 66,
                    "кут: ОЦІНИТИ й ВИБРАТИ передбачення\nволів «assessment», не «validation»",
                    size=11, fill="#f4f6f8", stroke=MUTED))

    # права картка — Гайсер
    rb, rw, rh = textbox(530, 96, "Сеймур Гайсер\nМіннесота · JASA · 1975",
                         size=12, pad=10, fill="#fdecea", stroke=POS, bold=True, color=POS)
    f.append(rb)
    f.append(fitbox(400, 132, 260, 66,
                    "кут: ЗРОБИТИ передбачення (ціль)\nдозволяє загальніші розбиття",
                    size=11, fill="#f4f6f8", stroke=MUTED))

    # обидві стрілки донизу до спільного блоку
    f.append(arrow(190, 198, 305, 238, color=MUTED, sw=2))
    f.append(arrow(530, 198, 415, 238, color=MUTED, sw=2))
    conv, cw, ch = textbox(W/2, 258,
        "та сама ідея: повторне використання вибірки → КРОС-ВАЛІДАЦІЯ як МЕТОД",
        size=12, pad=10, fill="#e9f7ef", stroke=FIELD, bold=True, color=FIELD)
    f.append(conv)

    f.append(text(W/2, H - 14,
                  "незалежно, майже водночас, у двох країнах і двох головних журналах",
                  size=11, color=MUTED))
    render(os.path.join(OUT, 'two-1974.svg'), W, H, *f)


if __name__ == '__main__':
    fig_one_split_lottery()
    fig_kfold()
    fig_leakage()
    fig_fold_sizes()
    fig_stratified()
    fig_split_family()
    fig_two_1974()
    print("OK: 7 figures written to", OUT)
