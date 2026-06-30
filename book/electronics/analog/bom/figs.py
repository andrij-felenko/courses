# -*- coding: utf-8 -*-
"""Фігури до статті «Перелік компонентів (BOM)» (book/electronics/analog/bom).
П'ять фігур:
  bridge.svg         — BOM як міст від задуму (схема + плата) до коробки реальних деталей
  refdes.svg         — позиційне позначення як єдина нитка: символ → шовкографія → рядок BOM → деталь
  row.svg            — анатомія рядка BOM: що означає кожна колонка
  three-sets.svg     — три множини позначень (схема/плата/BOM) і різниці = класи помилок (вставка proj)
  check-pipeline.svg — конвеєр перевірки: CSV → нормалізація → множини → коди (вставка proj)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# 1. bridge.svg — BOM стоїть між задумом і реальними деталями
# ════════════════════════════════════════════════════════════════════════════
def fig_bridge():
    W, H = 720, 330
    f = []

    # лівий бік — задум (що з'єднано + де лежить), але не що купувати
    lx, lw = 40, 150
    f.append(rect(lx, 70, lw, 170, fill="#eef2fb", stroke=NEG, sw=2, rx=10))
    f.append(text(lx + lw / 2, 96, "ЗАДУМ", size=14, bold=True, color=NEG))
    f.append(mtext(lx + lw / 2, 128, ["Схема:", "що з чим", "з'єднано"], size=12, color=INK))
    f.append(mtext(lx + lw / 2, 192, ["Плата:", "де кожне", "сидить"], size=12, color=INK))
    f.append(text(lx + lw / 2, 256, "(але не що купувати)", size=10, color=MUTED))

    # центр — BOM-міст
    cx, cw = 285, 150
    f.append(rect(cx, 90, cw, 130, fill="#eef7f0", stroke=FIELD, sw=2.4, rx=12))
    f.append(text(cx + cw / 2, 124, "BOM", size=20, bold=True, color=FIELD))
    f.append(mtext(cx + cw / 2, 150, ["перелік", "компонентів"], size=12, color=INK))
    f.append(text(cx + cw / 2, 200, "міст задум → річ", size=11, color=MUTED))

    # правий бік — коробка реальних деталей
    rx, rw = 530, 150
    f.append(rect(rx, 70, rw, 170, fill="#fdf0ea", stroke=POS, sw=2, rx=10))
    f.append(text(rx + rw / 2, 96, "КОРОБКА", size=14, bold=True, color=POS))
    f.append(mtext(rx + rw / 2, 130, ["конкретні", "деталі від", "конкретного", "виробника"], size=12, color=INK))
    f.append(text(rx + rw / 2, 214, "те, що паяють", size=10, color=MUTED))

    # стрілки
    f.append(arrow(lx + lw + 6, 155, cx - 6, 155, color=INK, sw=2.6))
    f.append(arrow(cx + cw + 6, 155, rx - 6, 155, color=INK, sw=2.6))

    f.append(text(W / 2, 290, "Схема й плата кажуть «як» і «де». BOM каже «що саме і скільки» —",
                  size=12, color=MUTED))
    f.append(text(W / 2, 308, "без нього з правильного креслення не вийде жодної правильної плати",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "bridge.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. refdes.svg — позиційне позначення як наскрізна нитка крізь усі документи
# ════════════════════════════════════════════════════════════════════════════
def fig_refdes():
    W, H = 700, 360
    f = []
    f.append(text(W / 2, 32, "Одне позначення R7 — крізь усі чотири документи", size=16, bold=True))

    # чотири «станції», які поєднує один R7
    cols = [
        (95,  "СХЕМА",       ["символ резистора", "з міткою R7"],        NEG),
        (270, "ШОВКОГРАФІЯ", ["напис «R7» на платі", "біля контактних", "майданчиків"], INK),
        (445, "РЯДОК BOM",   ["R7 → 10 кОм,", "MPN, корпус,", "кількість"],  FIELD),
        (620, "ДЕТАЛЬ",      ["потрібний", "резистор", "припаяно сюди"], POS),
    ]
    cy = 150
    boxw = 140
    for x, head, body, col in cols:
        f.append(rect(x - boxw / 2, 70, boxw, 120, fill="#ffffff", stroke=col, sw=2, rx=10))
        f.append(text(x, 96, head, size=12, bold=True, color=col))
        f.append(mtext(x, 122, body, size=11, color=INK))
        # «бирка» R7
        bb, _, _ = textbox(x, 218, "R7", size=15, color=col, bold=True,
                           fill="#f4f6f8", stroke=col, min_w=54)
        f.append(bb)

    # нитка, що проходить крізь усі бирки
    f.append(line(95, 218, 620, 218, color=MUTED, sw=1.4, dash="5 5"))
    for x, _, _, _ in cols:
        f.append(arrow(x, 190, x, 200, color=MUTED, sw=1.6))

    f.append(text(W / 2, 268, "Позиційне позначення — спільний ключ. Поки R7 однаковий усюди,",
                  size=12, color=MUTED))
    f.append(text(W / 2, 286, "людина й машина знають, що це та сама деталь у тому самому місці",
                  size=12, color=MUTED))
    f.append(text(W / 2, 322, "Розбіжність хоч в одному документі — і на плату сяде не те або не туди",
                  size=11, color=POS, bold=True))
    render(os.path.join(IMG, "refdes.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. row.svg — анатомія одного рядка BOM: що означає кожна колонка
# ════════════════════════════════════════════════════════════════════════════
def fig_row():
    W, H = 720, 320
    f = []
    f.append(text(W / 2, 30, "Анатомія одного рядка переліку компонентів", size=16, bold=True))

    # шапка таблиці
    cols = [
        ("Позначення", "R7, R8", 0.16),
        ("К-сть",      "2",       0.07),
        ("Номінал",    "10 кОм",  0.13),
        ("Корпус",     "0603",    0.11),
        ("MPN",        "RC0603…", 0.20),
        ("Виробник",   "Yageo",   0.16),
        ("Прим.",      "DNP?",    0.17),
    ]
    x0, x1 = 30, 690
    total = x1 - x0
    y_head, y_row = 70, 120
    rh = 50
    # рахуємо межі
    xs = [x0]
    for _, _, frac in cols:
        xs.append(xs[-1] + total * frac)

    # тіло шапки
    f.append(rect(x0, y_head, total, rh, fill="#eef2fb", stroke=NEG, sw=2, rx=6))
    f.append(rect(x0, y_row, total, rh, fill="#ffffff", stroke=INK, sw=1.6, rx=6))
    for i, (head, val, _) in enumerate(cols):
        cx = (xs[i] + xs[i + 1]) / 2
        if i > 0:
            f.append(line(xs[i], y_head, xs[i], y_row + rh, color="#cdd3da", sw=1.2))
        f.append(text(cx, y_head + 30, head, size=12, bold=True, color=NEG))
        f.append(text(cx, y_row + 30, val, size=12, color=INK))

    # пояснення під кожною колонкою
    notes = [
        "які саме\nмісця",
        "скільки\nтаких",
        "що це за\nномінал",
        "розмір на\nплаті",
        "точний номер\nдеталі",
        "хто робить\n(+ заміни)",
        "ставити чи\nпропустити",
    ]
    cols_col = [NEG, INK, INK, INK, POS, FIELD, MUTED]
    for i, (note, col) in enumerate(zip(notes, cols_col)):
        cx = (xs[i] + xs[i + 1]) / 2
        f.append(arrow(cx, y_row + rh + 4, cx, y_row + rh + 22, color=col, sw=1.4))
        f.append(mtext(cx, y_row + rh + 40, note.split("\n"), size=10, color=col))

    f.append(text(W / 2, 300, "Серце рядка — MPN: тільки він однозначно каже, яку фізичну деталь замовити",
                  size=12, color=POS, bold=True))
    render(os.path.join(IMG, "row.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. three-sets.svg — три множини позначень; різниці множин = класи помилок
#    (фігура до вставки proj-bom-consistency)
# ════════════════════════════════════════════════════════════════════════════
def fig_three_sets():
    W, H = 720, 430
    f = []
    f.append(text(W / 2, 30, "Три множини позначень — а різниці між ними є помилки", size=16, bold=True))

    # три кола, що частково перекриваються (Венн): схема, плата, BOM
    r = 120
    cxS, cyS = 270, 200          # схема (верх-ліво)
    cxB, cyB = 450, 200          # плата (верх-право)
    cxM, cyM = 360, 300          # BOM (низ)
    f.append('<circle cx="%d" cy="%d" r="%d" fill="#2457d6" fill-opacity="0.10" stroke="%s" stroke-width="2"/>' % (cxS, cyS, r, NEG))
    f.append('<circle cx="%d" cy="%d" r="%d" fill="#1a1a1a" fill-opacity="0.07" stroke="%s" stroke-width="2"/>' % (cxB, cyB, r, INK))
    f.append('<circle cx="%d" cy="%d" r="%d" fill="#27ae60" fill-opacity="0.10" stroke="%s" stroke-width="2"/>' % (cxM, cyM, r, FIELD))

    # підписи множин
    f.append(text(cxS - 70, cyS - 95, "СХЕМА", size=13, bold=True, color=NEG))
    f.append(text(cxS - 70, cyS - 78, "(задум)", size=10, color=MUTED))
    f.append(text(cxB + 70, cyB - 95, "ПЛАТА", size=13, bold=True, color=INK))
    f.append(text(cxB + 70, cyB - 78, "(мідь)", size=10, color=MUTED))
    f.append(text(cxM, cyM + 100, "ПЕРЕЛІК (BOM)", size=13, bold=True, color=FIELD))
    f.append(text(cxM, cyM + 117, "(що замовляти)", size=10, color=MUTED))

    # здорове ядро — перетин усіх трьох
    f.append(text(360, 233, "усе", size=12, bold=True, color=INK))
    f.append(text(360, 250, "збігається", size=11, color=INK))

    # підписи різниць у відповідних «пелюстках»
    f.append(mtext(cxB + 38, 215, ["B−M:", "майданчик", "без рядка", "(E4)"], size=10, color=POS, anchor="middle"))
    f.append(mtext(cxM - 70, 320, ["M−B:", "рядок без", "майданчика", "(E5)"], size=10, color=POS, anchor="middle"))
    f.append(mtext(cxS - 38, 215, ["S−B:", "у схемі,", "не на платі", "(E7)"], size=10, color=POS, anchor="middle"))

    f.append(text(W / 2, 400, "Перетин усіх трьох — здорове ядро. Кожна частина поза ним — окремий клас помилки.",
                  size=12, color=MUTED))
    f.append(text(W / 2, 418, "Інструмент рахує саме ці різниці множин і друкує їх кодами E4–E7.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "three-sets.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. check-pipeline.svg — конвеєр перевірки: розбір → нормалізація → множини → коди
#    (фігура до вставки proj-bom-consistency)
# ════════════════════════════════════════════════════════════════════════════
def fig_check_pipeline():
    W, H = 720, 380
    f = []
    f.append(text(W / 2, 30, "Від трьох файлів до коду виходу", size=16, bold=True))

    # три входи зліва
    ins = [
        (70, "bom.csv",   FIELD),
        (70, "schem.txt", NEG),
        (70, "board.txt", INK),
    ]
    ys = [80, 150, 220]
    for (x, lbl, col), y in zip(ins, ys):
        bb, w, _ = textbox(x + 40, y, lbl, size=12, color=col, bold=True,
                           fill="#ffffff", stroke=col, min_w=110)
        f.append(bb)

    # етап 1: розбір (CSV — з лапками; списки — просто рядки)
    s1x = 210
    f.append(rect(s1x, 70, 150, 180, fill="#eef7f0", stroke=FIELD, sw=2, rx=10))
    f.append(text(s1x + 75, 96, "РОЗБІР", size=12, bold=True, color=FIELD))
    f.append(mtext(s1x + 75, 120, ["CSV: лапки →", "кома в полі", "не ділить"], size=10, color=INK))
    f.append(mtext(s1x + 75, 175, ["+ розгортання", "R1-R4 →", "R1,R2,R3,R4"], size=10, color=INK))
    f.append(mtext(s1x + 75, 226, ["+ нормалізація", "r7/ R7 → R7"], size=10, color=INK))

    # етап 2: три множини
    s2x = 400
    f.append(rect(s2x, 90, 130, 140, fill="#eef2fb", stroke=NEG, sw=2, rx=10))
    f.append(text(s2x + 65, 116, "МНОЖИНИ", size=12, bold=True, color=NEG))
    f.append(mtext(s2x + 65, 142, ["S — схема", "B — плата", "M — перелік"], size=11, color=INK))
    f.append(mtext(s2x + 65, 200, ["різниці:", "B−M, M−B…"], size=10, color=MUTED))

    # етап 3: звіт із кодами
    s3x = 565
    f.append(rect(s3x, 70, 130, 180, fill="#fdf0ea", stroke=POS, sw=2, rx=10))
    f.append(text(s3x + 65, 96, "ЗВІТ", size=12, bold=True, color=POS))
    f.append(mtext(s3x + 65, 120, ["E1 к-сть", "E2 без MPN", "E3 дублікат"], size=10, color=INK))
    f.append(mtext(s3x + 65, 178, ["E4–E7", "різниці", "множин"], size=10, color=INK))
    f.append(text(s3x + 65, 234, "код виходу", size=10, bold=True, color=POS))

    # стрілки між етапами
    for y in ys:
        f.append(arrow(160, y, s1x - 6, 160, color=MUTED, sw=1.6))
    f.append(arrow(s1x + 150 + 4, 160, s2x - 6, 160, color=INK, sw=2.2))
    f.append(arrow(s2x + 130 + 4, 160, s3x - 6, 160, color=INK, sw=2.2))

    f.append(text(W / 2, 300, "DNP-рядок без MPN проходить як НОРМА — інструмент його не сварить.",
                  size=12, color=MUTED))
    f.append(text(W / 2, 340, "Нуль помилок → код 0 → відправлення дозволене. Будь-що інше спиняє конвеєр.",
                  size=12, color=POS, bold=True))
    render(os.path.join(IMG, "check-pipeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_bridge()
    fig_refdes()
    fig_row()
    fig_three_sets()
    fig_check_pipeline()
    print("OK: 5 фігур у", IMG)
