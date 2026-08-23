# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

BROWN = "#b07a35"
PURPLE = "#8e44ad"


# ── Фігура A: чому інкремент-після-запису роздвоює номери при збої живлення ──
def fig_double_serial():
    W, H = 860, 508
    f = [text(W / 2, 30, "Чому «зашити, тоді збільшити лічильник» роздвоює номери",
              size=15, bold=True)]

    # дві колонки-таймлайни: зліва «інкремент після» (біда), справа двофазний (безпечно)
    colw = 380
    xL, xR = 44, 476
    ytop = 74

    def head(x, s, col, bad):
        f.append(fitbox(x, ytop, colw, 40,
                        s, size=13, bold=True, color=col,
                        fill=("#fdecea" if bad else "#eafaf1"),
                        stroke=col, sw=1.7))

    head(xL, "інкремент ПІСЛЯ запису — роздвоює", POS, True)
    head(xR, "зарезервувати ПЕРЕД, підтвердити ПІСЛЯ", FIELD, False)

    # кроки лівої колонки (біда)
    stepL = [
        ("прочитати лічильник → 42", INK),
        ("зашити 42 у плату", INK),
        ("⚡ збій живлення ТУТ", POS),
        ("лічильник ще 42 (не зріс)", POS),
        ("наступна плата теж дістане 42", POS),
    ]
    stepR = [
        ("ЗАРЕЗЕРВУВАТИ 42 у БД (атомарно)", NEG),
        ("зашити 42 у плату", INK),
        ("⚡ збій живлення ТУТ", BROWN),
        ("42 лишився 'в роботі' → завислий", BROWN),
        ("наступна дістане 43; 42 — пропуск", FIELD),
    ]

    def column(x, steps):
        bh, gap = 44, 16
        y = ytop + 58
        cx = x + colw / 2
        for i, (s, col) in enumerate(steps):
            fill = "#fbfbfb"
            if "збій" in s:
                fill = "#fff3d6"
            if col in (POS,) and "збій" not in s:
                fill = "#fdecea"
            if col == FIELD:
                fill = "#eafaf1"
            f.append(fitbox(x + 20, y, colw - 40, bh, s, size=11.5, color=col,
                            fill=fill, stroke=col, sw=1.4, bold=("збій" in s)))
            if i < len(steps) - 1:
                f.append(arrow(cx, y + bh, cx, y + bh + gap, color=MUTED, sw=1.6))
            y += bh + gap
        return y

    yend = column(xL, stepL)
    column(xR, stepR)

    # підсумок унизу
    f.append(fitbox(xL, yend + 6, colw, 46,
                    "БІДА: два вироби в полі з номером 42.\nБаза бреше, який з них який.",
                    size=11, color=POS, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(fitbox(xR, yend + 6, colw, 46,
                    "БЕЗПЕЧНО: гірше — дірка в нумерації.\nДублікатів немає НІКОЛИ.",
                    size=11, color=FIELD, fill="#eafaf1", stroke=FIELD, sw=1.5))

    render(os.path.join(OUT, 'double-serial.svg'), W, H, *f)


# ── Фігура B: два стани життя номера — reserved → used (машина станів) ────────
def fig_serial_states():
    W, H = 820, 360
    f = [text(W / 2, 30, "Життя одного серійного номера — це маленька машина станів",
              size=15, bold=True)]

    bw, bh = 150, 62
    y = 120
    xs = [70, 330, 590]
    labels = [
        ("вільний", "ще ніким\nне взятий", MUTED, "#f4f6f8"),
        ("в роботі\n(reserved)", "зарезервований,\nплата шиється", BROWN, "#fff3d6"),
        ("виданий\n(used)", "плата підтверджена,\nномер закріплено", FIELD, "#eafaf1"),
    ]
    cx = []
    for i, (name, sub, col, fill) in enumerate(labels):
        x = xs[i]
        f.append(fitbox(x, y, bw, bh, name, size=12.5, bold=True, color=col,
                        fill=fill, stroke=col, sw=1.8))
        f.append(fitbox(x, y + bh + 8, bw, 40, sub, size=10, color=MUTED,
                        fill="#ffffff", stroke=MUTED, sw=1.0))
        cx.append(x + bw / 2)

    # переходи
    f.append(arrow(xs[0] + bw, y + bh / 2, xs[1] - 2, y + bh / 2, color=NEG, sw=2))
    f.append(text((xs[0] + bw + xs[1]) / 2, y + bh / 2 - 12, "ЗАРЕЗЕРВУВАТИ", size=10.5, color=NEG, bold=True))
    f.append(text((xs[0] + bw + xs[1]) / 2, y - 28, "фаза 1", size=10, color=NEG))

    f.append(arrow(xs[1] + bw, y + bh / 2, xs[2] - 2, y + bh / 2, color=FIELD, sw=2))
    f.append(text((xs[1] + bw + xs[2]) / 2, y + bh / 2 - 12, "ПІДТВЕРДИТИ", size=10.5, color=FIELD, bold=True))
    f.append(text((xs[1] + bw + xs[2]) / 2, y - 28, "фаза 2", size=10, color=FIELD))

    # петля відкату: reserved → (застряг) → пропуск
    ax = xs[1] + bw / 2
    f.append(line(ax, y + bh + 48, ax, y + bh + 78, color=BROWN, sw=1.6, dash="5,4"))
    f.append(line(ax, y + bh + 78, ax + 150, y + bh + 78, color=BROWN, sw=1.6, dash="5,4"))
    f.append(arrow(ax + 150, y + bh + 78, ax + 150, y + bh + 60, color=BROWN, sw=1.6))
    f.append(fitbox(ax + 74, y + bh + 88, 220, 40,
                    "завис надовго → відкат прибиральником:\nномер лишається пропуском, НЕ дублікатом",
                    size=10, color=BROWN, fill="#fff8e6", stroke=BROWN, sw=1.3))

    f.append(fitbox(70, H - 46, W - 140, 34,
                    "Ключ теми: серійник — не 'наступне число', а ЗАПИС у БД, що переходить станами під захистом транзакції.",
                    size=11.5, bold=True, fill="#eef2f7", stroke=INK, sw=1.5))
    render(os.path.join(OUT, 'serial-states.svg'), W, H, *f)


# ── Фігура C: транзакція серіалізує паралельні голови (без роздвоєння) ─────────
def fig_serialize_heads():
    W, H = 840, 400
    f = [text(W / 2, 30, "Дві станції просять номер одночасно — транзакція шикує їх у чергу",
              size=15, bold=True)]

    # дві голови ліворуч
    hw, hh = 130, 50
    f.append(fitbox(50, 90, hw, hh, "Голова A", size=12, bold=True, color=NEG,
                    fill="#eaf0fd", stroke=NEG, sw=1.7))
    f.append(fitbox(50, 250, hw, hh, "Голова B", size=12, bold=True, color=POS,
                    fill="#fdecea", stroke=POS, sw=1.7))

    # БД посередині — серіалізатор
    dbx, dby, dbw, dbh = 330, 150, 180, 130
    f.append(rect(dbx, dby, dbw, dbh, fill="#eef2f7", stroke=INK, sw=2))
    f.append(text(dbx + dbw / 2, dby + 26, "БАЗА ДАНИХ", size=13, bold=True))
    f.append(text(dbx + dbw / 2, dby + 48, "транзакція = замок", size=10.5, color=INK))
    f.append(fitbox(dbx + 16, dby + 62, dbw - 32, 52,
                    "поки A всередині —\nB чекає (SQLITE_BUSY /\nFOR UPDATE), не лізе",
                    size=10, color=MUTED, fill="#ffffff", stroke=MUTED, sw=1.0))

    # запити всередину
    f.append(arrow(50 + hw, 115, dbx - 2, dby + 30, color=NEG, sw=1.8))
    f.append(text(50 + hw + 40, 118, "дай номер", size=10, color=NEG, anchor="start"))
    f.append(arrow(50 + hw, 275, dbx - 2, dby + dbh - 20, color=POS, sw=1.8))
    f.append(text(50 + hw + 40, 288, "дай номер", size=10, color=POS, anchor="start"))

    # результати праворуч — різні номери, без колізії
    rx = dbx + dbw + 40
    f.append(fitbox(rx, 120, 240, 46, "A ← 42\n(зайшла першою, взяла замок)",
                    size=11, color=NEG, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.6))
    f.append(fitbox(rx, 230, 240, 46, "B ← 43\n(дочекалась, взяла наступний)",
                    size=11, color=POS, bold=True, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(arrow(dbx + dbw, dby + 30, rx - 2, 143, color=NEG, sw=1.8))
    f.append(arrow(dbx + dbw, dby + dbh - 20, rx - 2, 253, color=POS, sw=1.8))

    f.append(fitbox(50, H - 44, W - 100, 32,
                    "Без транзакції обидві прочитали б 42 і зашили б 42 у ДВІ плати. Транзакція робить 'прочитати+збільшити' неподільним.",
                    size=11, fill="#f4f6f8", stroke=INK, sw=1.4))
    render(os.path.join(OUT, 'serialize-heads.svg'), W, H, *f)


# ── Фігура D: пре-алокація БЛОКІВ офлайн-станціям ────────────────────────────
def fig_block_prealloc():
    W, H = 820, 380
    f = [text(W / 2, 30, "Офлайн-станція без зв'язку з базою: видати їй БЛОК номерів наперед",
              size=15, bold=True)]

    # центральна база з великим діапазоном
    dbx, dby, dbw, dbh = 300, 70, 220, 70
    f.append(rect(dbx, dby, dbw, dbh, fill="#eef2f7", stroke=INK, sw=2))
    f.append(text(dbx + dbw / 2, dby + 28, "ЦЕНТРАЛЬНА БАЗА", size=12.5, bold=True))
    f.append(text(dbx + dbw / 2, dby + 50, "єдиний реєстр усіх блоків", size=10, color=MUTED))

    # два блоки, видані двом станціям
    blocks = [
        (70, "Станція 1 (офлайн)", "блок 1000–1999", NEG, "#eaf0fd"),
        (470, "Станція 2 (офлайн)", "блок 2000–2999", POS, "#fdecea"),
    ]
    for x, name, rng, col, fill in blocks:
        by = 210
        f.append(fitbox(x, by, 280, 44, name, size=12, bold=True, color=col,
                        fill=fill, stroke=col, sw=1.7))
        f.append(fitbox(x, by + 52, 280, 40, rng + "  (1000 номерів наперед)",
                        size=11, color=col, fill="#ffffff", stroke=col, sw=1.2))
        f.append(fitbox(x, by + 98, 280, 44,
                        "роздає зі свого блоку локально,\nбез запиту до бази щоразу",
                        size=10, color=MUTED, fill="#fbfbfb", stroke=MUTED, sw=1.0))
        # стрілка видачі блоку
        f.append(arrow(dbx + (30 if x < 300 else dbw - 30), dby + dbh,
                       x + 140, by - 2, color=col, sw=1.8))

    f.append(text(dbx + 30, dby + dbh + 24, "видати блок", size=10, color=NEG))
    f.append(text(dbx + dbw - 70, dby + dbh + 24, "видати блок", size=10, color=POS))

    f.append(fitbox(70, H - 46, W - 140, 34,
                    "База ділить простір номерів на НЕПЕРЕСІЧНІ блоки. Блоки не перетинаються → станції ніколи не видадуть однаковий номер, навіть офлайн.",
                    size=11, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.5))
    render(os.path.join(OUT, 'block-prealloc.svg'), W, H, *f)


if __name__ == '__main__':
    fig_double_serial()
    fig_serial_states()
    fig_serialize_heads()
    fig_block_prealloc()
    print("ok")
