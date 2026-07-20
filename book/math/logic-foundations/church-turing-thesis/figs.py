# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Теза Черча–Тюринга».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

RED   = "#c0392b"   # Тюринг / гаряче / виклик
BLUE  = "#2457d6"   # холодне / межа швидкості
GREEN = "#27ae60"   # обчислюване / збіг / основна теза
AMBER = "#b9770e"   # загальнорекурсивні


# ── Фігура 1: збіг чотирьох означень в один клас ─────────────────────────────
def fig_confluence():
    W, H = 1040, 560
    P = []
    box, bw, bh = textbox(W / 2, 68,
                          "Гільбертове питання: що таке «механічна процедура» взагалі?",
                          size=13.5, fill=FILL, stroke=INK, color=INK)
    P.append(box)
    # рейка роздачі
    P.append(line(W / 2, 68 + bh / 2, W / 2, 120, color=MUTED, sw=1.6))
    P.append(line(140, 120, 900, 120, color=MUTED, sw=1.6))

    cols = [
        (140, BLUE,  "λ-числення", "Алонзо Черч",
         ["самі функції та", "правило підставити", "одне в одне"]),
        (393, AMBER, "загальнорекурсивні", "Ербран · Гедель",
         ["нуль і «+1», а з них —", "функції, означені", "через самих себе"]),
        (647, RED,   "машина Тюринга", "Алан Тюринг",
         ["стрічка, голівка,", "скінченна таблиця", "правил"]),
        (900, GREEN, "робітник у коробках", "Еміль Пост",
         ["ставить і стирає", "позначки за", "списком інструкцій"]),
    ]
    for cx, col, head, who, body in cols:
        P.append(arrow(cx, 120, cx, 150, color=MUTED, sw=1.6))
        P.append(rect(cx - 110, 152, 220, 150, fill=BG, stroke=col, sw=1.8, rx=9))
        P.append(text(cx, 177, head, size=13, color=col, bold=True))
        P.append(text(cx, 196, who, size=11, color=MUTED))
        for i, ln in enumerate(body):
            P.append(text(cx, 222 + i * 19, ln, size=11, color=INK))
        P.append(line(cx, 304, cx, 344, color=MUTED, sw=1.6))   # збірка донизу

    P.append(line(140, 344, 900, 344, color=MUTED, sw=1.6))
    P.append(arrow(W / 2, 344, W / 2, 374, color=MUTED, sw=1.6))
    box2, _, _ = textbox(W / 2, 412, "ОДИН І ТОЙ САМИЙ клас обчислюваних функцій",
                         size=15, fill="#eafaf0", stroke=GREEN, color=INK, bold=True)
    P.append(box2)
    P.append(text(W / 2, 472, "Чотири несхожі дороги — різні люди, різні мотиви, різні конструкції —",
                  size=12, color=MUTED))
    P.append(text(W / 2, 494, "збіглися в одній точці. Цей збіг і є доказовим хребтом тези.",
                  size=12.5, color=INK, bold=True))
    render("img/confluence.svg", W, H, *P,
           title="Чотири дороги до одного означення обчислення")


# ── Фігура 2: теза, а не теорема — інтуїтивне ↔ строге ───────────────────────
def fig_thesis_not_theorem():
    W, H = 1000, 470
    P = []
    # ліворуч: інтуїтивне поняття — «розмита» пунктирна рамка
    lx, ly, lw, lh = 66, 116, 336, 196
    P.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="26" '
             'fill="#fbfcfe" stroke="%s" stroke-width="2" stroke-dasharray="8,7"/>'
             % (lx, ly, lw, lh, MUTED))
    lcx = lx + lw / 2
    P.append(text(lcx, ly - 12, "ІНТУЇТИВНЕ поняття", size=13, color=MUTED, bold=True))
    P.append(text(lcx, ly + 44, "«ефективно обчислюване»", size=15, color=INK, bold=True))
    P.append(text(lcx, ly + 78, "алгоритм · механічна процедура", size=12, color=INK))
    P.append(text(lcx, ly + 108, "рецепт зі скінченних кроків", size=12, color=INK))
    P.append(text(lcx, ly + 146, "означення НЕМАЄ —", size=12.5, color=MUTED, bold=True))
    P.append(text(lcx, ly + 166, "це те, що ми й хочемо означити", size=11.5, color=MUTED))
    # праворуч: строгий об'єкт — суцільна рамка
    rx, ry, rw, rh = 598, 116, 336, 196
    rcx = rx + rw / 2
    P.append(rect(rx, ry, rw, rh, fill="#eafaf0", stroke=GREEN, sw=2.2, rx=10))
    P.append(text(rcx, ry - 12, "СТРОГИЙ об'єкт", size=13, color=GREEN, bold=True))
    P.append(text(rcx, ry + 44, "обчислюване машиною Тюринга", size=13.5, color=INK, bold=True))
    P.append(text(rcx, ry + 78, "задана сімкою ⟨Q, Σ, Γ, δ, …⟩", size=12, color=INK))
    P.append(text(rcx, ry + 108, "можна доводити теореми", size=12, color=INK))
    P.append(text(rcx, ry + 146, "межа точна —", size=12.5, color=GREEN, bold=True))
    P.append(text(rcx, ry + 166, "видно, що всередині, а що ні", size=11.5, color=INK))
    # місток-теза між ними (пунктирна двобічна стрілка)
    my = ly + lh / 2
    P.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.4" '
             'stroke-dasharray="7,6" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
             % (lx + lw + 8, my, rx - 8, my, INK))
    tb, _tw, _th = textbox(W / 2, my - 34, "ТЕЗА:\nце одне й те саме",
                           size=12.5, fill=FILL, stroke=INK, color=INK, bold=True)
    P.append(tb)
    # статус унизу
    P.append(text(W / 2, 360, "Рівність строгого з інтуїтивним НЕ доводять — ліворуч нема з чого будувати доведення.",
                  size=12.5, color=INK, bold=True))
    P.append(text(W / 2, 388, "Спростувати легко — досить одного «рецепта», що виходить за машину Тюринга.",
                  size=12, color=RED))
    P.append(text(W / 2, 414, "За майже сто років такого не знайшли: теза недоказовна — але нездоланна.",
                  size=12.5, color=GREEN, bold=True))
    render("img/thesis-not-theorem.svg", W, H, *P, title="Чому це теза, а не теорема")


# ── Фігура 3: дві межі — «чи можна» проти «чи швидко» ────────────────────────
def fig_what_vs_fast():
    W, H = 900, 560
    cxm = W / 2
    P = []
    # зовнішнє коло — усе обчислюване (основна теза)
    P.append(circle(cxm, 285, 190, fill="#eafaf0", stroke=GREEN, sw=2.4))
    P.append(text(cxm, 70, "Усе, що взагалі обчислюване", size=15, color=GREEN, bold=True))
    P.append(text(cxm, 90, "= обчислюване машиною Тюринга", size=12.5, color=INK))
    # внутрішнє коло — обчислюване швидко (пунктир)
    P.append('<circle cx="%.1f" cy="%.1f" r="92" fill="#eef4ff" stroke="%s" '
             'stroke-width="2.2" stroke-dasharray="7,6"/>' % (cxm, 320, BLUE))
    P.append(text(cxm, 312, "обчислюване ШВИДКО", size=12.5, color=BLUE, bold=True))
    P.append(text(cxm, 332, "(поліноміальний час)", size=11, color=MUTED))
    P.append(text(cxm, 366, "розширена / фізична теза", size=10.5, color=BLUE))
    # квантовий виклик — у кільці зверху, стрілка вниз до пунктирної межі
    qb, qw, qh = textbox(cxm, 158, "квантовий комп'ютер\n(алгоритм Шора)", size=11.5,
                         fill=FILL, stroke=RED, color=INK, bold=True)
    P.append(qb)
    P.append(arrow(cxm, 158 + qh / 2, cxm, 226, color=RED, sw=2))
    P.append(text(cxm + 110, 198, "б'є лише сюди —", size=11, color=RED, bold=True))
    P.append(text(cxm + 110, 215, "по межі швидкості", size=10.5, color=RED))
    # підписи знизу (поза колом)
    P.append(text(cxm, 500, "ОСНОВНА теза — про те, ЩО взагалі обчислюване: майже беззаперечна.",
                  size=12.5, color=GREEN, bold=True))
    P.append(text(cxm, 524, "РОЗШИРЕНА — про те, що обчислюване ШВИДКО; саме її й випробовує квант.",
                  size=12, color=INK))
    P.append(text(cxm, 546, "Квантова машина не обчислює більшого — лише подекуди швидше: зовнішньої межі не руше.",
                  size=11, color=MUTED))
    render("img/what-vs-fast.svg", W, H, *P,
           title="Дві різні межі: «чи можна» проти «чи швидко»")


# ── Фігура 4 (proj): одна функція 2+3 трьома моделями сходиться на 5 ──────────
def fig_three_roads():
    W, H = 1140, 632
    P = []
    P.append(text(W / 2, 54, "Одна функція — 2 + 3 — трьома несхожими моделями",
                  size=16, bold=True))

    colw = 320
    cols = [
        (208, BLUE,  "λ-числення", "спрощуй вираз",
         ["add «2» «3»",
          "→ λf.λx. «2» f («3» f x)",
          "→ λf.λx. f(f(f(f(f x))))",
          "= «5»    (6 β-кроків)"]),
        (570, AMBER, "загальнорекурсивна", "розкручуй рекурсію",
         ["add(2, 3)",
          "= S(add(2, 2))",
          "= S(S(add(2, 1)))",
          "= S(S(S(add(2, 0))))",
          "= S(S(S(2))) = 5"]),
        (932, RED,   "машина Тюринга", "переписуй стрічку",
         ["110111    старт",
          "111111    0 → 1",
          "11111_    стерли 1",
          "= 5       (8 кроків)"]),
    ]
    top = 84
    y0 = 178
    dy = 33
    for cx, col, head, sub, body in cols:
        P.append(rect(cx - colw / 2, top, colw, 44, fill=BG, stroke=col, sw=2, rx=9))
        P.append(text(cx, top + 20, head, size=14.5, color=col, bold=True))
        P.append(text(cx, top + 37, sub, size=11, color=MUTED))
        lx = cx - colw / 2 + 18
        for i, ln in enumerate(body):
            P.append(text(lx, y0 + i * dy, ln, size=13, color=INK, anchor="start"))
        # рейка вниз до збірної лінії
        P.append(line(cx, 372, cx, 452, color=MUTED, sw=1.6))
        P.append(arrow(cx, 452, cx, 486, color=col, sw=1.8))

    P.append(line(208, 452, 932, 452, color=MUTED, sw=1.6))
    box, _, _ = textbox(W / 2, 520, "усі три дороги приходять у 5",
                        size=16, fill="#eafaf0", stroke=GREEN, color=INK, bold=True)
    P.append(box)
    P.append(text(W / 2, 578,
                  "Різні світи — функції, рекурсія, стрічка — а результат той самий на кожному вході.",
                  size=12.5, color=INK))
    P.append(text(W / 2, 600,
                  "Це і є той збіг, що його теза підносить у принцип: усі означують один клас.",
                  size=12, color=MUTED))
    render("img/three-roads.svg", W, H, *P,
           title="Три моделі — одна відповідь")


# ── Фігура 5 (proj): покроковий біг машини Тюринга (3 + 2 в унарному) ─────────
def fig_tm_trace():
    W, H = 760, 560
    P = []
    P.append(text(W / 2, 48, "Машина Тюринга додає 2 + 3 (унарний запис)",
                  size=16, bold=True))
    P.append(text(W / 2, 72, "стрічка «11 0 111» → «11111»: роздільник 0 стає 1, зайву 1 стерто",
                  size=11.5, color=MUTED))

    rows = [
        ("q0", "110111", 0), ("q0", "110111", 1), ("q0", "110111", 2),
        ("q1", "111111", 3), ("q1", "111111", 4), ("q1", "111111", 5),
        ("q1", "111111", 6),
        ("q2", "111111", 5),
        ("qH", "11111",  5),
    ]
    cs = 40                 # розмір клітини
    gx = 214                # ліва межа сітки
    gy = 96                 # верх сітки
    rh = 44                 # висота рядка
    STATE_COL = {"q0": INK, "q1": AMBER, "q2": BLUE, "qH": GREEN}

    for r, (st, tape, head) in enumerate(rows):
        ry = gy + r * rh
        col = STATE_COL.get(st, INK)
        # мітка стану ліворуч
        P.append(text(gx - 30, ry + cs * 0.62, st, size=13.5, color=col,
                      anchor="end", bold=True))
        row = (tape + "_______")[:7]
        for c in range(7):
            x = gx + c * cs
            sym = row[c]
            shown = "·" if sym == "_" else sym
            is_head = (c == head)
            P.append(rect(x, ry, cs, cs, fill=("#fdecea" if is_head else BG),
                          stroke=(col if is_head else MUTED),
                          sw=(2.6 if is_head else 1.2), rx=4))
            P.append(text(x + cs / 2, ry + cs * 0.66, shown, size=16,
                          color=(col if is_head else INK),
                          bold=is_head))
        # голівка: підпис праворуч
        if r == 0:
            P.append(text(gx + 7 * cs + 26, ry + cs * 0.62, "← голівка",
                          size=11.5, color=RED, anchor="start"))
    # підсумок під сіткою
    fy = gy + len(rows) * rh + 20
    P.append(text(W / 2, fy, "п'ять одиниць лишилось на стрічці  =  2 + 3  =  5",
                  size=13.5, color=GREEN, bold=True))
    P.append(text(W / 2, fy + 24,
                  "вісім кроків на суму 5: кроків лінійно від m+n — унарна плата за прості правила",
                  size=11.5, color=MUTED))
    render("img/tm-trace.svg", W, H, *P, title="Стрічка крок за кроком")


# ── Фігура 6 (вставка hist-thesis-birth): диво-рік — вертикальна смуга подій ──
def fig_miracle_year():
    W, H = 980, 700
    spine = 250
    P = []
    rows = [
        ("1934 · Прінстон", MUTED,
         "Черч пропонує λ-визначність — Гедель: «геть незадовільно»",
         "Гедель означує загальнорекурсивні функції (за ідеєю Ербрана)"),
        ("19 квіт. 1935", BLUE,
         "Черч виступає перед AMS + абстракт у Bull. AMS",
         "перша прилюдна поява майбутньої тези"),
        ("1936", BLUE,
         "Черч, «Нерозв'язна задача…» (Amer. J. Math., т. 58)",
         "знаряддя: λ-числення й загальнорекурсивні функції"),
        ("28 трав. 1936", RED,
         "Тюринг, «Про обчислювані числа» (надійшла до LMS)",
         "знаряддя: машина зі стрічкою, голівкою й таблицею"),
        ("7 жовт. 1936", AMBER,
         "Пост, «Скінченні комбінаторні процеси» (до JSL)",
         "знаряддя: робітник, що ставить і стирає позначки"),
        ("1936–37", GREEN,
         "Кліні доводить рівності формалізмів",
         "Тюринг у Прінстоні зводить три означення в одне"),
    ]
    y0, step = 92, 100
    ybot = y0 + step * (len(rows) - 1)
    P.append(line(spine, y0 - 22, spine, ybot + 22, color=MUTED, sw=2))
    # зелений відрізок спини — тісний кластер 1936 (рядки 3–5)
    P.append(line(spine, y0 + step * 2, spine, y0 + step * 4, color=GREEN, sw=5))
    for i, (yr, col, ttl, det) in enumerate(rows):
        y = y0 + i * step
        P.append(text(spine - 28, y + 4, yr, size=12.5, color=INK, anchor="end", bold=True))
        P.append(circle(spine, y, 8, fill=BG, stroke=col, sw=3))
        cx, cw = spine + 30, 660
        P.append(rect(cx, y - 34, cw, 68, fill=BG, stroke=col, sw=1.8, rx=8))
        P.append(text(cx + 16, y - 8, ttl, size=13, color=col, anchor="start", bold=True))
        P.append(text(cx + 16, y + 16, det, size=12, color=INK, anchor="start"))
    render("img/miracle-year.svg", W, H, *P,
           title="Диво-рік обчислюваності: 1934–1937")


# ── Фігура 7 (вставка hist-thesis-birth): ланцюг найменування тези ───────────
def fig_naming_chain():
    W, H = 1120, 372
    P = []
    cols = [
        (205, MUTED, "1943", "«Теза I»",
         ["«Рекурсивні предикати", "й квантори»", "Trans. AMS, т. 53"],
         ["поняттю дано статус тези"]),
        (560, BLUE, "1952", "«теза Черча»",
         ["«Вступ до", "метаматематики»"],
         ["названо на честь того,", "хто виступив першим"]),
        (915, GREEN, "1967", "«теза Черча–Тюринга»",
         ["«Математична логіка»"],
         ["долучено ім'я Тюринга —", "за доказ, що переконав"]),
    ]
    boxy, boxh, boxw = 74, 150, 300
    for cx, col, yr, name, work, note in cols:
        ncol = INK if col == MUTED else col
        x = cx - boxw / 2
        P.append(rect(x, boxy, boxw, boxh, fill=BG, stroke=col, sw=2, rx=10))
        P.append(text(cx, boxy + 27, yr, size=13, color=MUTED, bold=True))
        nsize = fit_font(name, boxw - 28, 17, bold=True)
        P.append(text(cx, boxy + 60, name, size=nsize, color=ncol, bold=True))
        for j, ln in enumerate(work):
            P.append(text(cx, boxy + 88 + j * 19, ln, size=12, color=INK))
        for j, ln in enumerate(note):
            P.append(text(cx, boxy + boxh + 30 + j * 19, ln, size=12, color=MUTED))
    my = boxy + boxh / 2
    P.append(arrow(205 + boxw / 2 + 6, my, 560 - boxw / 2 - 6, my, color=INK, sw=2))
    P.append(arrow(560 + boxw / 2 + 6, my, 915 - boxw / 2 - 6, my, color=INK, sw=2))
    P.append(text(W / 2, 356, "усі три хрещення — рука Стівена Кліні", size=12.5, color=INK, bold=True))
    render("img/naming-chain.svg", W, H, *P,
           title="Хрещення тези: три заходи одного імені")


if __name__ == "__main__":
    fig_confluence()
    fig_thesis_not_theorem()
    fig_what_vs_fast()
    fig_three_roads()
    fig_tm_trace()
    fig_miracle_year()
    fig_naming_chain()
    print("OK: confluence, thesis-not-theorem, what-vs-fast, three-roads, "
          "tm-trace, miracle-year, naming-chain")
