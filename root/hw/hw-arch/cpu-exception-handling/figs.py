# -*- coding: utf-8 -*-
"""Фігури до теми «Обробка виключень у процесорі».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Синхронне (виключення) vs асинхронне (переривання) ─────────────────────
def fig_sync_async():
    W, H = 860, 380
    f = [text(W / 2, 30,
              "Звідки прийшла подія: виключення народжується ВСЕРЕДИНІ інструкції, переривання — ЗЗОВНІ",
              size=14, bold=True)]

    # спільна стрічка інструкцій
    ix, iw, ih = 60, 118, 46
    y = 110
    instrs = ["load", "add", "div ÷0", "store", "…"]
    hot = 2
    centers = []
    for i, lab in enumerate(instrs):
        x = ix + i * (iw + 6)
        col = POS if i == hot else INK
        f.append(rect(x, y, iw, ih, fill=("#fdecea" if i == hot else "#f4f6f8"),
                      stroke=col, sw=2 if i == hot else 1.4))
        f.append(text(x + iw / 2, y + 28, lab, size=12.5, color=col, bold=(i == hot)))
        centers.append(x + iw / 2)
    f.append(text(ix - 6, y + 28, "потік", size=10.5, color=MUTED, anchor="end"))
    f.append(text(ix - 6, y + 42, "команд", size=10.5, color=MUTED, anchor="end"))

    # виключення: стрілка ВГОРУ з винної інструкції
    ex_y = 250
    f.append(arrow(centers[hot], y + ih, centers[hot], ex_y - 4, color=POS, sw=2.4))
    eb, ew, eh = textbox(centers[hot], ex_y + 24,
                         "ВИКЛЮЧЕННЯ\nсама інструкція\nне може виконатись",
                         size=11, fill="#fdecea", stroke=POS, sw=1.8, bold=True, min_w=170)
    f.append(eb)
    f.append(text(centers[hot] + 150, ex_y - 30,
                  "синхронне: прив'язане до конкретної команди",
                  size=10.5, color=POS, italic=True))

    # переривання: стрілка ЗЗОВНІ (з правого поля) в проміжок між командами
    dev_x = W - 70
    f.append(rect(dev_x - 60, y - 6, 120, ih + 12, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(dev_x, y + 16, "таймер", size=11, color=FIELD, bold=True))
    f.append(text(dev_x, y + 34, "(зовні)", size=10, color=FIELD))
    gap_x = centers[3] + (iw + 6) / 2
    f.append(arrow(dev_x - 60, y + ih / 2, gap_x + 4, y + ih / 2, color=FIELD, sw=2.2))
    f.append(text(dev_x - 30, y - 16, "асинхронне: будь-коли між командами",
                  size=10.5, color=FIELD, italic=True, anchor="end"))

    b2, _, _ = textbox(W / 2, 350,
                       "виключення — «команда впала»; переривання — «прийшов зовнішній дзвінок». "
                       "далі механізм той самий",
                       size=11, fill=FILL, stroke=LINE)
    f.append(b2)
    render(os.path.join(IMG, "sync-async.svg"), W, H, *f)


# ── 2. Три класи за адресою повернення: fault / trap / abort ──────────────────
def fig_classes():
    W, H = 900, 430
    f = [text(W / 2, 30,
              "Три класи виключень різняться однією річчю: куди вказує адреса повернення",
              size=14, bold=True)]

    rows = [
        ("FAULT — збій", POS,
         "адреса → на ТУ САМУ команду",
         "усунь причину й повтори; команда виконається",
         "брак сторінки пам'яті"),
        ("TRAP — пастка", FIELD,
         "адреса → на НАСТУПНУ команду",
         "обслужи й іди далі, наче нічого",
         "точка зупину, системний виклик"),
        ("ABORT — аварія", NEG,
         "повернутись НЕМА КУДИ",
         "стан зіпсовано; безпечно продовжити не можна",
         "збій апаратної цілісності"),
    ]
    rh = 108
    ty = 78
    for i, (title, col, ret, act, ex) in enumerate(rows):
        y = ty + i * rh
        f.append(rect(50, y, 800, rh - 16,
                      fill=("#fdecea" if col == POS else ("#eef6ef" if col == FIELD else "#eaf0fd")),
                      stroke=col, sw=1.8, rx=10))
        f.append(text(70, y + 34, title, size=14, color=col, bold=True, anchor="start"))
        f.append(text(70, y + 62, "повернення: " + ret, size=11.5, color=INK, anchor="start"))
        f.append(text(70, y + 82, "дія: " + act, size=11, color=MUTED, anchor="start"))
        f.append(text(830, y + 34, "приклад", size=10, color=col, anchor="end", italic=True))
        f.append(text(830, y + 60, ex, size=11, color=INK, anchor="end", bold=True))

    b2, _, _ = textbox(W / 2, 408,
                       "fault можна перезапустити, trap — крок повз, abort — глуха стіна: усе вирішує сенс адреси повернення",
                       size=11, fill=FILL, stroke=LINE)
    f.append(b2)
    render(os.path.join(IMG, "classes.svg"), W, H, *f)


# ── 3. Точне vs неточне: буфер запису рве зв'язок «команда → збій» ────────────
def fig_precise():
    W, H = 880, 400
    f = [text(W / 2, 30,
              "Чому адресу винуватця буває втрачено: буфер запису відпускає команду раніше, ніж шина відповість",
              size=13.5, bold=True)]

    # ВЕРХ: точне — команда чекає відповіді шини
    yT = 92
    f.append(text(70, yT - 8, "ТОЧНЕ (precise)", size=12.5, color=POS, bold=True, anchor="start"))
    boxes = [("store", INK), ("шина відповіла:\nпомилка!", POS), ("ядро завмерло\nтут-таки", POS)]
    bx, bw2, bh2 = 70, 210, 46
    cx_prev = None
    for i, (lab, col) in enumerate(boxes):
        x = bx + i * (bw2 + 30)
        f.append(rect(x, yT, bw2, bh2, fill=("#fdecea" if col == POS else "#f4f6f8"),
                      stroke=col, sw=1.6, rx=8))
        for j, ln in enumerate(lab.split("\n")):
            f.append(text(x + bw2 / 2, yT + (26 if len(lab.split("\n")) == 1 else 20) + j * 18,
                          ln, size=11, color=col, bold=(col == POS)))
        if cx_prev is not None:
            f.append(arrow(cx_prev, yT + bh2 / 2, x, yT + bh2 / 2, sw=1.8))
        cx_prev = x + bw2
    f.append(text(W - 60, yT + bh2 / 2, "адреса\nвідома", size=10.5, color=POS,
                  italic=True, anchor="end"))

    # НИЗ: неточне — буфер відпускає команду, ядро побігло далі
    yB = 232
    f.append(text(70, yB - 8, "НЕТОЧНЕ (imprecise)", size=12.5, color=MUTED, bold=True, anchor="start"))
    boxes2 = [("store →\nбуфер запису", NEG), ("ядро вже виконує\nінші команди", INK),
              ("аж тепер шина\nкаже: помилка", POS)]
    cx_prev = None
    for i, (lab, col) in enumerate(boxes2):
        x = bx + i * (bw2 + 30)
        fillc = "#eaf0fd" if col == NEG else ("#fdecea" if col == POS else "#f4f6f8")
        f.append(rect(x, yB, bw2, bh2, fill=fillc, stroke=col, sw=1.6, rx=8))
        for j, ln in enumerate(lab.split("\n")):
            f.append(text(x + bw2 / 2, yB + 20 + j * 18, ln, size=11, color=col,
                          bold=(col in (NEG, POS))))
        if cx_prev is not None:
            f.append(arrow(cx_prev, yB + bh2 / 2, x, yB + bh2 / 2, sw=1.8))
        cx_prev = x + bw2
    f.append(text(W - 60, yB + bh2 / 2, "яка саме\nкоманда — ?", size=10.5, color=POS,
                  italic=True, anchor="end"))

    b2, _, _ = textbox(W / 2, 372,
                       "буфер запису пришвидшує ядро, але, відпустивши команду, стирає зв'язок «хто винен»: "
                       "звідси неточні збої",
                       size=11, fill="#fdecea", stroke=POS)
    f.append(b2)
    render(os.path.join(IMG, "precise.svg"), W, H, *f)


if __name__ == "__main__":
    fig_sync_async()
    fig_classes()
    fig_precise()
    print("OK: 3 figures ->", IMG)
