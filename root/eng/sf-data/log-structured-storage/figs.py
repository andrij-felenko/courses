# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def cell(x, y, w, h, s, fill=FILL, stroke=LINE, size=13, color=INK, bold=False, sw=1.5):
    """Клітина з написом рівно по центру (без автопідгону ширини)."""
    return fitbox(x, y, w, h, s, size=size, fill=fill, stroke=stroke, color=color, bold=bold, sw=sw)


# ── Фігура 1: чому не переписати на місці — журнал обходить стирання ──────────
def fig_why_append():
    W, H = 780, 340
    f = []
    f.append(text(W/2, 26, "Змінити значення на місці — не можна; дописати нове в кінець — можна", size=16, bold=True))

    # Зліва: спроба переписати на місці
    lx = 40
    f.append(text(lx + 155, 62, "Переписати на місці", size=14, bold=True, color=POS))
    # сектор із кількома записами
    sy = 82
    cw, ch = 74, 40
    labels = [("A=1", FILL), ("B=7", "#fdecea"), ("C=3", FILL), ("D=9", FILL)]
    for i, (lab, fl) in enumerate(labels):
        f.append(cell(lx + i*(cw+4), sy, cw, ch, lab, fill=fl))
    f.append(text(lx + 155, sy + ch + 22, "щоб змінити лише B →", size=12, color=MUTED))
    f.append(text(lx + 155, sy + ch + 40, "стерти ВЕСЬ сектор (і A,C,D)", size=12, color=POS, bold=True))
    # зображення стирання всього
    ey = sy + ch + 56
    f.append(rect(lx, ey, 4*(cw)+3*4, ch, fill="#fdecea", stroke=POS, sw=1.8, rx=6))
    f.append(text(lx + 155, ey + ch/2 + 5, "весь сектор → 0xFF, тоді писати наново", size=11.5, color=POS))
    f.append(text(lx + 155, ey + ch + 24, "знос, повільно, ризик на півдорозі", size=12, color=MUTED, italic=True))

    # роздільник
    f.append(line(W/2, 60, W/2, H-24, color="#d0d4d8", sw=1.5, dash="4 5"))

    # Справа: дописати нове в кінець
    rx = W/2 + 26
    f.append(text(rx + 150, 62, "Дописати в кінець (журнал)", size=14, bold=True, color=FIELD))
    ry = 82
    seq = [("A=1", FILL), ("B=7", FILL), ("C=3", FILL), ("D=9", FILL)]
    for i, (lab, fl) in enumerate(seq):
        f.append(cell(rx + i*(cw+4), ry, cw, ch, lab, fill=fl))
    # нове B дописане далі
    ay = ry + ch + 30
    f.append(text(rx + 150, ay - 8, "змінити B → просто допишемо новий B", size=12, color=FIELD))
    f.append(cell(rx, ay, cw, ch, "B=8", fill="#e8f7ee", stroke=FIELD, bold=True, sw=2))
    f.append(text(rx + cw + 12, ay + ch/2 + 5, "у чисте місце, старе не чіпаємо", size=11.5, color=MUTED, anchor="start"))
    f.append(text(rx + 150, ay + ch + 26, "без стирання, швидко, старе ціле", size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, 'why-append.svg'), W, H, *f)


# ── Фігура 2: журнал росте, найновіший запис перемагає ───────────────────────
def fig_newest_wins():
    W, H = 800, 300
    f = []
    f.append(text(W/2, 26, "Журнал росте лише в кінець; для ключа чинний — НАЙНОВІШИЙ запис", size=15.5, bold=True))

    x0, y0 = 30, 74
    cw, ch, gap = 118, 52, 6
    # live: чинна версія ключа; dead: перекрита пізнішим записом того ж ключа
    recs = [
        ("гучність=5", "dead"),
        ("яскр.=8",     "dead"),
        ("гучність=7", "dead"),
        ("яскр.=8",     "live"),   # остання «яскр.» — чинна
        ("гучність=9", "live"),   # остання «гучність» — чинна
    ]
    for i, (lab, kind) in enumerate(recs):
        x = x0 + i*(cw+gap)
        if kind == "live":
            f.append(cell(x, y0, cw, ch, lab, fill="#e8f7ee", stroke=FIELD, bold=True, sw=2))
        else:
            f.append(cell(x, y0, cw, ch, lab, fill="#f0f1f2", stroke="#c3c7cc", color=MUTED))
    # стрілка напрямку росту
    endx = x0 + len(recs)*(cw+gap)
    f.append(arrow(x0, y0 + ch + 20, endx - 6, y0 + ch + 20, color=INK))
    f.append(text(endx - 6, y0 + ch + 38, "напрям запису →", size=12, color=MUTED, anchor="end"))
    f.append(text(x0, y0 - 16, "старе ← сірі: перекриті пізнішим записом того ж ключа; зелені: чинні", size=12, color=MUTED, anchor="start"))

    # висновок унизу
    yy = y0 + ch + 74
    f.append(text(W/2, yy, "Читаємо ключ «гучність» → сканом знаходимо ОСТАННІЙ його запис = 9.", size=13.5, color=INK))
    f.append(text(W/2, yy + 24, "Старі версії лишилися лежати як мертвий баласт — їх приберуть згодом.", size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'newest-wins.svg'), W, H, *f)


# ── Фігура 3: збирання сміття / ущільнення ───────────────────────────────────
def fig_compaction():
    W, H = 800, 360
    f = []
    f.append(text(W/2, 26, "Журнал заповнився мертвими версіями → ущільнення звільняє місце", size=15.5, bold=True))

    # ДО: повний журнал, багато мертвих
    x0, y0 = 30, 66
    cw, ch, gap = 70, 46, 5
    before = [
        ("a=1", True), ("b=2", True), ("a=5", True), ("c=3", False),
        ("b=8", True), ("a=9", False), ("d=4", False), ("b=6", False),
    ]  # True = мертвий (застарілий), False = живий (чинна версія)
    f.append(text(x0, y0 - 12, "ДО: журнал повний, живих мало", size=13, bold=True, anchor="start"))
    for i, (lab, dead) in enumerate(before):
        x = x0 + i*(cw+gap)
        if dead:
            f.append(cell(x, y0, cw, ch, lab, fill="#f0f1f2", stroke="#c3c7cc", color=MUTED))
        else:
            f.append(cell(x, y0, cw, ch, lab, fill="#e8f7ee", stroke=FIELD, bold=True, sw=2))
    f.append(text(x0, y0 + ch + 22, "сірі — мертві (старі версії, вже нікому не потрібні); зелені — живі (чинні)", size=11.5, color=MUTED, anchor="start"))

    # стрілка вниз
    f.append(arrow(W/2, y0 + ch + 42, W/2, y0 + ch + 76, color=INK))
    f.append(text(W/2 + 12, y0 + ch + 64, "ущільнення: переписати ЛИШЕ живі в чисте місце, старе стерти", size=12, color=INK, anchor="start"))

    # ПІСЛЯ: тільки живі, компактно, багато вільного
    y1 = y0 + ch + 100
    live = [("a=9", False), ("c=3", False), ("d=4", False), ("b=6", False)]
    f.append(text(x0, y1 - 12, "ПІСЛЯ: лишилися тільки чинні, решта — вільно", size=13, bold=True, anchor="start"))
    for i, (lab, _dead) in enumerate(live):
        x = x0 + i*(cw+gap)
        f.append(cell(x, y1, cw, ch, lab, fill="#e8f7ee", stroke=FIELD, bold=True, sw=2))
    # вільне місце
    free_x = x0 + len(live)*(cw+gap)
    free_w = (len(before)-len(live))*(cw+gap) - gap
    f.append(rect(free_x, y1, free_w, ch, fill=BG, stroke="#c3c7cc", sw=1.5, rx=6))
    f.append(text(free_x + free_w/2, y1 + ch/2 + 5, "вільне — під нові записи", size=12.5, color=FIELD))

    render(os.path.join(IMG, 'compaction.svg'), W, H, *f)


# ── Фігура 4: один прийом — багато домівок ───────────────────────────────────
def fig_where():
    W, H = 780, 300
    f = []
    f.append(text(W/2, 26, "Один прийом «пиши в кінець, старе не чіпай» — у багатьох сховищах", size=15.5, bold=True))

    # центральна ідея
    body, bw, bh = textbox(W/2, 96, ["append-only журнал", "+ найновіше перемагає", "+ ущільнення"],
                           size=13.5, fill="#e8f7ee", stroke=FIELD, bold=True, pad=12)
    f.append(body)

    homes = [
        ("NVS", "ключ→значення\nу Flash МК"),
        ("LittleFS", "файлова система,\ncopy-on-write"),
        ("SSD / картка", "FTL мапить\nблоки всередині"),
        ("Бази даних", "WAL і LSM-дерева\n(RocksDB тощо)"),
    ]
    n = len(homes)
    bw2, bh2 = 168, 62
    total = n*bw2 + (n-1)*18
    x0 = (W - total)/2
    y = 200
    for i, (name, desc) in enumerate(homes):
        x = x0 + i*(bw2+18)
        f.append(rect(x, y, bw2, bh2, fill=FILL, stroke=LINE, sw=1.5, rx=8))
        f.append(text(x + bw2/2, y + 20, name, size=13.5, bold=True))
        f.append(mtext(x + bw2/2, y + 38, desc.split("\n"), size=11, color=MUTED, lh=1.25))
        # лінія від ідеї
        f.append(line(W/2, 96 + bh/2, x + bw2/2, y, color="#b7bcc2", sw=1.4))

    render(os.path.join(IMG, 'where.svg'), W, H, *f)


# ── Фігура 5 (proj): порядок запису, печатка останньою = точка фіксації ───────
def fig_record_layout():
    W, H = 820, 320
    f = []
    f.append(text(W/2, 26, "Запис лягає по черзі; печатка ОСТАННЯ = точка фіксації", size=15.5, bold=True))

    # три частини запису одна за одною
    x0, y0 = 40, 70
    ch = 54
    parts = [
        ("заголовок",  "magic, ключ,\nдовжина", 150, FILL, LINE, INK),
        ("значення",   "самі дані",             200, FILL, LINE, INK),
        ("печатка CRC", "скріплює все\nперед нею", 150, "#e8f7ee", FIELD, INK),
    ]
    x = x0
    xs = []
    for name, desc, w, fl, st, col in parts:
        f.append(rect(x, y0, w, ch, fill=fl, stroke=st, sw=2 if st == FIELD else 1.5, rx=6))
        f.append(text(x + w/2, y0 + 21, name, size=13, bold=True, color=col))
        f.append(mtext(x + w/2, y0 + 38, desc.split("\n"), size=10.5, color=MUTED, lh=1.2))
        xs.append((x, w))
        x += w + 6
    # номери кроків над частинами
    for i, (px, pw) in enumerate(xs):
        f.append(text(px + pw/2, y0 - 12, "%d" % (i+1), size=13, bold=True, color=INK))

    # стрілка напрямку запису
    endx = xs[-1][0] + xs[-1][1]
    f.append(arrow(x0, y0 + ch + 20, endx, y0 + ch + 20, color=INK))
    f.append(text(endx, y0 + ch + 38, "порядок запису в пам'ять →", size=11.5, color=MUTED, anchor="end"))

    # дві долі: збій до печатки і після
    yy = y0 + ch + 82
    b1, w1, h1 = textbox(x0 + 210, yy + 20, ["Збій ДО кроку 3:", "печатки нема → CRC не сходиться", "→ запис відкинуто, старе чинне"],
                         size=12, fill="#fdecea", stroke=POS, color=INK, pad=11)
    f.append(b1)
    b2, w2, h2 = textbox(W - 250, yy + 20, ["Збій ПІСЛЯ кроку 3:", "печатка стоїть і сходиться", "→ запис цілий і чинний"],
                         size=12, fill="#e8f7ee", stroke=FIELD, color=INK, pad=11)
    f.append(b2)

    render(os.path.join(IMG, 'record-layout.svg'), W, H, *f)


# ── Фігура 6 (proj): ущільнення поряд + один перемикач ───────────────────────
def fig_compaction_swap():
    W, H = 840, 400
    f = []
    f.append(text(W/2, 26, "Ущільнення поряд: живе → чистий журнал B; один перемикач робить B активним", size=14.5, bold=True))

    cw, ch, gap = 66, 44, 5

    # Журнал A (старий, активний) — суміш живого й мертвого
    ax, ay = 40, 78
    f.append(text(ax, ay - 12, "Журнал A (активний): живе + мертве", size=12.5, bold=True, anchor="start"))
    a_recs = [("a=1", True), ("b=2", True), ("a=5", True), ("c=3", False),
              ("b=8", False), ("a=9", False)]  # True = мертвий, False = живий
    for i, (lab, dead) in enumerate(a_recs):
        x = ax + i*(cw+gap)
        if dead:
            f.append(cell(x, ay, cw, ch, lab, fill="#f0f1f2", stroke="#c3c7cc", color=MUTED))
        else:
            f.append(cell(x, ay, cw, ch, lab, fill="#e8f7ee", stroke=FIELD, bold=True, sw=2))
    f.append(text(ax, ay + ch + 20, "стоїть НЕДОТОРКАНИМ, поки збираємо B", size=11.5, color=MUTED, anchor="start"))

    # стрілка «переписуємо лише живе»
    f.append(arrow(W/2, ay + ch + 40, W/2, ay + ch + 74, color=INK))
    f.append(text(W/2 + 12, ay + ch + 62, "переписуємо ЛИШЕ живе (за покажчиком)", size=12, color=INK, anchor="start"))

    # Журнал B (новий) — тільки живе, компактно
    by = ay + ch + 98
    f.append(text(ax, by - 12, "Журнал B (чистий): тільки живі версії", size=12.5, bold=True, anchor="start"))
    b_recs = [("c=3", False), ("b=8", False), ("a=9", False)]
    for i, (lab, _d) in enumerate(b_recs):
        x = ax + i*(cw+gap)
        f.append(cell(x, by, cw, ch, lab, fill="#e8f7ee", stroke=FIELD, bold=True, sw=2))
    free_x = ax + len(b_recs)*(cw+gap)
    f.append(rect(free_x, by, 3*(cw+gap) - gap, ch, fill=BG, stroke="#c3c7cc", sw=1.5, rx=6))
    f.append(text(free_x + (3*(cw+gap)-gap)/2, by + ch/2 + 5, "вільне", size=12, color=FIELD))

    # перемикач — окрема печатка
    sw_y = by + ch + 40
    sb, sw_w, sw_h = textbox(W/2, sw_y + 14, ["ПЕРЕМИКАЧ (окрема печатка): активний = B"],
                             size=12.5, fill="#e8f7ee", stroke=FIELD, bold=True, pad=11)
    f.append(sb)
    f.append(text(W/2, sw_y + 44, "один атомарний запис фіксує все: до нього чинний A, після — B; лише тоді стираємо A",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(IMG, 'compaction-swap.svg'), W, H, *f)


# ── Фігура 7 (hist): нитка журнального прийому крізь роки ─────────────────────
def fig_hist_timeline():
    W, H = 900, 430
    f = []
    f.append(text(W/2, 28, "Одна ідея, три хвилі: диски → бази даних → всюдисущість", size=16, bold=True))

    # горизонтальна вісь часу
    axy = 150
    ax0, ax1 = 60, W - 60
    f.append(line(ax0, axy, ax1, axy, color="#c3c7cc", sw=2))
    f.append(arrow(ax1 - 40, axy, ax1, axy, color=INK))
    f.append(text(ax1, axy - 12, "час", size=12, color=MUTED, anchor="end"))

    # чотири віхи: (x-частка, рік, заголовок, підпис-рядки, колір)
    miles = [
        (0.11, "1988", "Маніфест",
         ["Остергаут + Дуґліс,", "Берклі: «пиши в кінець", "заради швидкості диска»"], NEG),
        (0.37, "1991", "Sprite LFS",
         ["Розенблум + Остергаут:", "жива файлова система,", "70% швидкодії диска"], FIELD),
        (0.63, "1996", "LSM-дерево",
         ["О'Нілі, Ченґ, Ґавлік:", "той самий прийом —", "у базах даних"], "#8e44ad"),
        (0.89, "2006-11", "Bigtable →",
         ["LevelDB, далі RocksDB,", "Cassandra, HBase —", "половина інтернету"], POS),
    ]
    cw, chh = 178, 96
    for frac, yr, head, lines, col in miles:
        cx = ax0 + frac * (ax1 - ax0)
        # точка на осі
        f.append(circle(cx, axy, 7, fill=col, stroke=col, sw=2))
        # рік — над віссю, великий
        f.append(text(cx, axy - 28, yr, size=17, bold=True, color=col))
        # картка під віссю
        bx, by = cx - cw/2, axy + 34
        f.append(rect(bx, by, cw, chh, fill=FILL, stroke=col, sw=1.8, rx=8))
        f.append(text(cx, by + 24, head, size=14, bold=True, color=INK))
        f.append(mtext(cx, by + 44, lines, size=11.5, color=MUTED, lh=1.28))
        # тонкий поводок від точки до картки
        f.append(line(cx, axy + 7, cx, by, color=col, sw=1.2, dash="3 4"))

    # нижній підсумок — наскрізне серце ідеї
    yy = axy + 34 + chh + 42
    band, bw, bh = textbox(W/2, yy,
                           "серце всю дорогу те саме: пиши послідовно в кінець · старе не чіпай · найновіше чинне · сміття прибирай",
                           size=12.5, fill="#eef7f1", stroke=FIELD, bold=True, pad=13)
    f.append(band)

    render(os.path.join(IMG, 'hist-timeline.svg'), W, H, *f)


if __name__ == '__main__':
    fig_why_append()
    fig_newest_wins()
    fig_compaction()
    fig_where()
    fig_record_layout()
    fig_compaction_swap()
    fig_hist_timeline()
    print("figs done")
