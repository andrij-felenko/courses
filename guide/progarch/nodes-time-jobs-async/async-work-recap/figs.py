# -*- coding: utf-8 -*-
"""Фігури до кроку «Асинхронна робота як клас рішень»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#dfe9fb"
GREEN_FILL = "#eafaf0"
GRAY_FILL = "#eceef1"
YELLOW_FILL = "#fff8e6"
RED_FILL = "#fdecea"


def cpath(d, color=INK, sw=1.8):
    """Довільна крива-стрілка (marker-end визначає render())."""
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'marker-end="url(#arrow)"/>' % (d, color, sw))


def fig_async_shape():
    """Різні функції — той самий рух: витягнути роботу із запиту у воркер."""
    W, H = 1260, 700
    frags = []
    frags.append(text(W / 2, 42, "Різні функції — той самий архітектурний рух",
                      size=18, bold=True, color=INK))

    # ── ліворуч: шість несхожих функцій DH ──
    feats = [
        "надіслати лист-вітання",
        "стиснути план дому",
        "нічний звіт про енергію",
        "розкотити прошивку",
        "застосувати сцену",
        "перерахувати статистику",
    ]
    fx, fw, fh = 70, 280, 52
    ys = [120, 205, 290, 375, 460, 545]
    for label, y in zip(feats, ys):
        frags.append(fitbox(fx, y - fh / 2, fw, fh, label, size=13, bold=True,
                            fill=BLUE_FILL, stroke=INK))
    frags.append(text(fx + fw / 2, 596, "різні домени", size=12, italic=True, color=MUTED))

    # ── центр: спільний рух (межа запиту) ──
    cx = 690
    node, nw, nh = textbox(cx, 335, "МЕЖА ЗАПИТУ\nзаписати намір → 202 «прийнято»",
                           size=13, bold=True, fill=YELLOW_FILL, stroke=INK, sw=2, min_w=270)
    # стрілки від кожної функції сходяться до лівого краю центру (цілі рознесені по краю)
    left_edge = cx - nw / 2
    for i, y in enumerate(ys):
        ty = 335 + (i - 2.5) * 13
        frags.append(arrow(fx + fw + 6, y, left_edge - 6, ty, color=INK, sw=1.5))
    frags.append(node)
    frags.append(text(cx, 335 + nh / 2 + 22, "межу робота перетинає щоразу",
                      size=12, italic=True, color=MUTED))

    # ── праворуч: воркер ──
    wnode, wnw, _ = textbox(1080, 335,
                            "ВОРКЕР\nвиконує роботу поза запитом\nчас не тисне · переживе запит",
                            size=13, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2, min_w=280)
    frags.append(arrow(cx + nw / 2 + 6, 335, 1080 - wnw / 2 - 6, 335, color=INK, sw=2.4))
    frags.append(wnode)

    frags.append(text(W / 2, 664,
                      "Функції з різних доменів, а рух ідентичний — тому це один клас рішень, а не шість окремих трюків.",
                      size=13, bold=True, color=MUTED))

    render(os.path.join(IMG, "async-shape.svg"), W, H, *frags, title=None)


def fig_job_anatomy():
    """Життєвий цикл фонової задачі й органи, що його ведуть."""
    W, H = 1380, 720
    frags = []
    frags.append(text(W / 2, 34, "Життєвий цикл фонової задачі — і органи, що його ведуть",
                      size=18, bold=True, color=INK))

    spine = 330
    bw, bh = 200, 64
    # три стани на хребті
    frags.append(fitbox(270 - bw / 2, spine - bh / 2, bw, bh, "У ЧЕРЗІ",
                        size=15, bold=True, fill=BLUE_FILL, stroke=NEG))
    frags.append(fitbox(690 - bw / 2, spine - bh / 2, bw, bh, "ВИКОНУЄТЬСЯ",
                        size=15, bold=True, fill=YELLOW_FILL, stroke=INK))
    frags.append(fitbox(1110 - bw / 2, spine - bh / 2, bw, bh, "ГОТОВО ✓",
                        size=15, bold=True, fill=GREEN_FILL, stroke=FIELD))
    frags.append(arrow(270 + bw / 2 + 6, spine, 690 - bw / 2 - 6, spine, color=INK, sw=2.0))
    frags.append(arrow(690 + bw / 2 + 6, spine, 1110 - bw / 2 - 6, spine, color=INK, sw=2.0))

    # ── над хребтом: органи ──
    trig, _, th = textbox(270, 138, "ТРИГЕР\nзараз · за розкладом (cron) · на подію",
                          size=12, bold=True, fill=GRAY_FILL, stroke=MUTED, sw=1.5, min_w=290)
    frags.append(trig)
    frags.append(arrow(270, 138 + th / 2, 270, spine - bh / 2 - 6, color=MUTED, sw=1.5))

    ded, _, dh = textbox(690, 132,
                         "at-least-once → той самий запис двічі\nдедуп-ворота за ключем ідемпотентності",
                         size=12, bold=True, fill=RED_FILL, stroke=POS, sw=1.5, min_w=400)
    frags.append(ded)
    frags.append(arrow(690, 132 + dh / 2, 690, spine - bh / 2 - 6, color=MUTED, sw=1.5))

    rep, _, rh = textbox(1110, 132,
                         "звіт назад: поллінг · колбек · вебхук\n(викликач давно пішов)",
                         size=12, bold=True, fill=GRAY_FILL, stroke=MUTED, sw=1.5, min_w=350)
    frags.append(rep)
    frags.append(arrow(1110, 132 + rh / 2, 1110, spine - bh / 2 - 6, color=MUTED, sw=1.5))

    # ── під хребтом: тривкий запис, петля повтору, мертва черга ──
    rec, _, rech = textbox(250, 476, "тривкий запис — намір\nпереживе смерть процесу",
                           size=12, fill=GRAY_FILL, stroke=MUTED, sw=1.4, min_w=300)
    frags.append(rec)
    frags.append(arrow(250, spine + bh / 2 + 6, 250, 476 - rech / 2 - 4, color=MUTED, sw=1.5))

    # петля повтору на RUNNING
    frags.append(cpath("M 668,%.0f C 636,438 604,438 596,%.0f" % (spine + bh / 2, spine + bh / 2 + 2),
                       color=POS, sw=1.8))
    frags.append(text(560, 452, "збій → повтор", size=11, bold=True, color=POS, anchor="middle"))
    frags.append(text(560, 468, "із відступом", size=11, bold=True, color=POS, anchor="middle"))

    # мертва черга — гілка з RUNNING униз-праворуч
    dl, _, dlh = textbox(960, 566, "МЕРТВА ЧЕРГА\nпісля N спроб — людина розбере",
                         size=12, bold=True, fill=RED_FILL, stroke=POS, sw=1.7, min_w=340)
    frags.append(arrow(752, spine + bh / 2, 918, 566 - dlh / 2 - 4, color=POS, sw=1.7))
    frags.append(text(880, 470, "здалися", size=11, italic=True, color=MUTED, anchor="middle"))
    frags.append(dl)

    # ── знизу: дві семантики часу ──
    tnote, _, _ = textbox(W / 2, 668,
                          "Монотонний годинник — «скільки вже біжить і коли здатися». "
                          "Настінний — «запустити о 02:00 за Києвом». Різні питання до різних годинників.",
                          size=12, bold=True, fill=GRAY_FILL, stroke=INK, sw=1.6, min_w=1200)
    frags.append(tnote)

    render(os.path.join(IMG, "job-anatomy.svg"), W, H, *frags, title=None)


def fig_async_decisions():
    """Шість осей рішення, щойно впізнав форму відкладеної роботи."""
    W, H = 1260, 700
    frags = []
    frags.append(text(W / 2, 44, "Шість осей рішення, щойно впізнав форму",
                      size=18, bold=True, color=INK))

    cells = [
        (330, 155, "1 · ТРИГЕР\nзараз / за розкладом (cron) / на подію", BLUE_FILL, NEG),
        (910, 155, "2 · ДЕ ЖИВЕ ЧЕРГА\nтаблиця в БД / Redis / брокер", BLUE_FILL, NEG),
        (330, 345, "3 · РЕЗУЛЬТАТ НАЗАД\nполлінг / колбек / вебхук", GREEN_FILL, FIELD),
        (910, 345, "4 · ГАРАНТІЯ + КЛЮЧ\nat-least-once → дедуп за ключем ідемпотентності",
         GREEN_FILL, FIELD),
        (330, 535, "5 · ВІДМОВА\nповтор+відступ → мертва черга; багатоетапне → сага",
         YELLOW_FILL, INK),
        (910, 535, "6 · ЧАС\nмонотонний (тривалість) / настінний (розклад); як зберегти",
         YELLOW_FILL, INK),
    ]
    for cx, cy, label, fill, stroke in cells:
        box, _, _ = textbox(cx, cy, label, size=13, bold=True, fill=fill,
                            stroke=stroke, sw=1.9, min_w=520)
        frags.append(box)

    frags.append(text(W / 2, 648,
                      "Не шість нових винаходів на кожну функцію — шість відповідей на той самий бланк.",
                      size=13, bold=True, color=MUTED))

    render(os.path.join(IMG, "async-decisions.svg"), W, H, *frags, title=None)


def fig_jobs_lineage():
    """Чотири покоління відкладеної роботи сходяться до однієї анатомії."""
    W, H = 1360, 560
    frags = []
    frags.append(text(W / 2, 40, "Чотири покоління — одна форма відкладеної роботи",
                      size=18, bold=True, color=INK))
    frags.append(text(W / 2, 70,
                      "інтерактивні й веб-обчислення сховали пакет — а він повернувся «фоновими задачами»",
                      size=13, italic=True, color=MUTED))

    eras = [
        (185, "ПАКЕТ · 1964\nIBM System/360 + JCL\nоператор JOB —\nпервісна відкладена робота",
         GRAY_FILL, MUTED),
        (510, "CRON · 1979 → 1987\nV7 Unix: Браян Керніган\nбагатокорист.: Purdue\nстандарт: Пол Віксі",
         BLUE_FILL, NEG),
        (835, "ВЕБ-ЧЕРГИ · 2009–2012\nResque — Кріс Ванстрат\nCelery — Аск Солем\nSidekiq — Майк Перем",
         GREEN_FILL, FIELD),
        (1160, "ТРИВКІ ВОРКФЛОУ · 2019\nAWS SWF → Cadence (Uber)\nМаксим Фатєєв,\nСамар Аббас → Temporal",
         YELLOW_FILL, INK),
    ]
    cy = 205
    xs, bottoms = [], []
    for cx, label, fill, stroke in eras:
        box, w, h = textbox(cx, cy, label, size=13, bold=True, fill=fill,
                            stroke=stroke, sw=1.9, min_w=300)
        frags.append(box)
        xs.append((cx, w))
        bottoms.append(cy + h / 2)

    # стрілки-еволюція між поколіннями
    for i in range(len(eras) - 1):
        x1 = xs[i][0] + xs[i][1] / 2 + 5
        x2 = xs[i + 1][0] - xs[i + 1][1] / 2 - 5
        frags.append(arrow(x1, cy, x2, cy, color=INK, sw=1.9))

    # спільна анатомія — стрічка внизу, куди сходяться всі покоління
    rib_cy = 472
    rib, rw, rh = textbox(W / 2, rib_cy,
                          "Щоразу наново відрощують ту саму анатомію задачі:\n"
                          "запис задачі · тригер (годинник / подія) · повтор і мертва черга · звіт назад",
                          size=14, bold=True, fill=FILL, stroke=INK, sw=2.2, min_w=1250)
    rib_top = rib_cy - rh / 2
    for i, (cx, _) in enumerate(xs):
        frags.append(arrow(cx, bottoms[i] + 6, cx, rib_top - 6, color=MUTED, sw=1.6))
    frags.append(rib)

    render(os.path.join(IMG, "jobs-lineage.svg"), W, H, *frags, title=None)


def fig_claim_race():
    """SKIP LOCKED: два воркери беруть різні рядки — не б'ються й не простоюють."""
    W, H = 1240, 620
    frags = []
    frags.append(text(W / 2, 40, "Клейм зі SKIP LOCKED — воркери не б'ються за той самий рядок",
                      size=18, bold=True))

    col_cx, row_w, row_h = 620, 300, 56
    left_e, right_e = col_cx - row_w / 2, col_cx + row_w / 2
    rows = [
        (210, "job #1 · running (A)", YELLOW_FILL, INK),
        (300, "job #2 · running (B)", YELLOW_FILL, INK),
        (390, "job #3 · queued",       BLUE_FILL,   NEG),
    ]
    frags.append(text(col_cx, 158, "таблиця job — готові до забору рядки",
                      size=13, italic=True, color=MUTED))
    for y, label, fill, st in rows:
        frags.append(fitbox(left_e, y - row_h / 2, row_w, row_h, label,
                            size=14, bold=True, fill=fill, stroke=st))

    # воркери обабіч, кожен на висоті свого рядка
    a_box, aw, _ = textbox(200, 210, "ВОРКЕР A", size=14, bold=True,
                           fill=GREEN_FILL, stroke=FIELD, sw=2, min_w=150)
    b_box, bw, _ = textbox(1040, 300, "ВОРКЕР B", size=14, bold=True,
                           fill=GREEN_FILL, stroke=FIELD, sw=2, min_w=150)
    frags.append(a_box)
    frags.append(b_box)

    # A → job #1 (клеймить)
    frags.append(arrow(200 + aw / 2 + 6, 210, left_e - 6, 210, color=FIELD, sw=2.4))
    frags.append(text((200 + aw / 2 + left_e) / 2, 199, "клеймить",
                      size=12, bold=True, color=FIELD))

    # B → job #2 (клеймить)
    frags.append(arrow(1040 - bw / 2 - 6, 300, right_e + 6, 300, color=FIELD, sw=2.4))
    frags.append(text((1040 - bw / 2 + right_e) / 2, 291, "клеймить",
                      size=12, bold=True, color=FIELD))

    # B ⇢ job #1 (зайнято → пропустити), пунктир повз рядок
    frags.append(line(1040 - bw / 2 - 6, 288, right_e + 6, 216, color=MUTED, sw=1.7, dash="6 5"))
    frags.append(text(right_e + 18, 205, "зайнято → SKIP LOCKED",
                      size=12, italic=True, color=MUTED, anchor="start"))

    note, _, _ = textbox(col_cx, 512,
                         "Зі SKIP LOCKED кожен воркер бере свій готовий рядок — ніхто не блокує іншого й ніхто не простоює.\n"
                         "Без нього десять воркерів вишикувалися б у чергу за першим-таки рядком (серіалізація й «стадо»).",
                         size=13, bold=True, fill=FILL, stroke=INK, sw=1.8, min_w=1080)
    frags.append(note)
    render(os.path.join(IMG, "claim-skip-locked.svg"), W, H, *frags, title=None)


def fig_visibility_timeout():
    """Оренда клейма повертає роботу за мертвим воркером — і краде її в повільного."""
    W, H = 1360, 780
    frags = []
    frags.append(text(W / 2, 38, "Visibility-timeout: оренда клейма проти загубленого клейма",
                      size=18, bold=True))

    x0, scale = 165, 20.6
    def X(t): return x0 + t * scale
    t_end = 50

    # ── Стрічка 1: воркер упав, роботу повернено ──
    frags.append(text(W / 2, 92, "Воркер упав — і наступний клейм підбирає протухлу оренду",
                      size=15, bold=True, color=FIELD))
    ay1 = 250
    frags.append(line(X(0), ay1, X(t_end), ay1, color=INK, sw=2.0))
    frags.append(text(X(t_end) + 10, ay1 + 5, "час", size=12, italic=True,
                      color=MUTED, anchor="start"))
    frags.append(rect(X(0), ay1 - 74, X(30) - X(0), 24, fill=BLUE_FILL, stroke=NEG, sw=1.6))
    frags.append(text((X(0) + X(30)) / 2, ay1 - 57, "оренда клейма — 30 c",
                      size=12, bold=True, color=NEG))
    ev1 = [
        (0,  "A клеймить",      285, INK),
        (12, "A падає ✗",       320, POS),
        (30, "оренда протухла", 285, INK),
        (34, "B переклеймлює",  320, FIELD),
        (48, "B: done ✓",       285, FIELD),
    ]
    for t, lbl, ly, col in ev1:
        frags.append(line(X(t), ay1 - 10, X(t), ay1 + 10, color=col, sw=2.0))
        frags.append(text(X(t), ly, lbl, size=12, bold=True, color=col))
    out1, _, _ = textbox(1130, ay1 - 58, "роботу\nНЕ втрачено", size=12, bold=True,
                         fill=GREEN_FILL, stroke=FIELD, sw=1.8, min_w=150)
    frags.append(out1)

    # ── Стрічка 2: A живий, лише повільний — задача біжить двічі ──
    frags.append(text(W / 2, 470, "Той самий механізм, небезпечний бік: A живий, лише повільний",
                      size=15, bold=True, color=POS))
    ay2 = 620
    frags.append(line(X(0), ay2, X(t_end), ay2, color=INK, sw=2.0))
    frags.append(text(X(t_end) + 10, ay2 + 5, "час", size=12, italic=True,
                      color=MUTED, anchor="start"))
    frags.append(rect(X(0), ay2 - 74, X(30) - X(0), 24, fill=BLUE_FILL, stroke=NEG, sw=1.6))
    frags.append(text((X(0) + X(30)) / 2, ay2 - 57, "оренда клейма — 30 c",
                      size=12, bold=True, color=NEG))
    # A ще прошиває — смуга під віссю 0..42, з червоним хвостом 34..42 (обоє біжать)
    frags.append(rect(X(0), ay2 + 16, X(42) - X(0), 24, fill=GRAY_FILL, stroke=MUTED, sw=1.6))
    frags.append(rect(X(34), ay2 + 16, X(42) - X(34), 24, fill=RED_FILL, stroke=POS, sw=1.8))
    frags.append(text((X(0) + X(34)) / 2, ay2 + 33, "A ще прошиває (повільно)",
                      size=12, bold=True, color=MUTED))
    frags.append(text((X(34) + X(42)) / 2, ay2 + 62, "біжать ОБОЄ",
                      size=12, bold=True, color=POS))
    ev2 = [
        (0,  "A клеймить",      585, INK),
        (30, "оренда протухла", 585, NEG),
        (34, "B переклеймлює",  560, FIELD),
    ]
    for t, lbl, ly, col in ev2:
        frags.append(line(X(t), ay2 - 10, X(t), ay2 + 10, color=col, sw=2.0))
        frags.append(text(X(t), ly, lbl, size=12, bold=True, color=col))
    out2, _, _ = textbox(1150, ay2 - 40,
                         "at-least-once у дії:\nрятує ідемпотентність\nабо heartbeat",
                         size=12, bold=True, fill=RED_FILL, stroke=POS, sw=1.8, min_w=250)
    frags.append(out2)

    render(os.path.join(IMG, "visibility-timeout.svg"), W, H, *frags, title=None)


if __name__ == "__main__":
    fig_async_shape()
    fig_job_anatomy()
    fig_async_decisions()
    fig_jobs_lineage()
    fig_claim_race()
    fig_visibility_timeout()
    print("OK: async-shape, job-anatomy, async-decisions, jobs-lineage, "
          "claim-skip-locked, visibility-timeout")
