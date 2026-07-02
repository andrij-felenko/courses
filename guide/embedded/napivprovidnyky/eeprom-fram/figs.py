# -*- coding: utf-8 -*-
"""Фігури до теми «EEPROM і FRAM».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
GREEN = FIELD        # EEPROM/FRAM-перевага, «добре»
RED   = POS          # флеш-обмеження, «дорого»
BLUE  = NEG          # колонка EEPROM
AMBER = "#b9770e"    # тепле застереження (зайва робота)


# ── 1. Побайтовий запис: чому для дрібних налаштувань зручніша EEPROM/FRAM ────
def fig_byte_write():
    W, H = 1000, 470
    f = [text(W / 2, 32, "Побайтовий запис: чому дрібне оновлення любить EEPROM і FRAM",
              size=18, bold=True)]
    f.append(text(W / 2, 55, "Flash мусить СПЕРШУ стерти цілий блок, щоб змінити один байт; "
                  "EEPROM і FRAM міняють окремий байт напряму",
                  size=12.5, color=MUTED, italic=True))

    def cells(x0, y, hi, hi_fill, hi_stroke):
        out = []
        for i in range(16):
            cx = x0 + i * 34
            if i == hi:
                out.append(rect(cx, y, 30, 30, fill=hi_fill, stroke=hi_stroke, sw=1.6, rx=3))
            else:
                out.append(rect(cx, y, 30, 30, fill=BG, stroke="#cfcfcf", sw=1.0, rx=3))
        return out

    # --- Flash: рядок + процедура «стерти блок → переписати» ---
    f.append(text(90, 108, "Flash (NOR/NAND): один байт не змінити окремо",
                  size=13.5, color=RED, anchor="start", bold=True))
    f.append(text(295, 124, "хочу змінити цей", size=10, color=RED, bold=True))
    f += cells(110, 132, 5, "#fdecea", RED)

    f.append(text(382, 186, "крок 1: стерти ВЕСЬ блок (усі 16 → 0xFF)",
                  size=11, color=AMBER, bold=True))
    f.append(text(382, 206, "крок 2: записати блок наново", size=11, color=INK))
    f.append(rect(110, 220, 540, 26, fill="#fff7e6", stroke=AMBER, sw=1.4, rx=4))
    f.append(text(382, 237, "багато зайвої роботи заради одного байта",
                  size=10.5, color=AMBER, italic=True))

    # --- EEPROM / FRAM: один байт напряму ---
    f.append(text(90, 306, "EEPROM / FRAM: пишемо РІВНО потрібний байт",
                  size=13.5, color=GREEN, anchor="start", bold=True))
    f += cells(110, 322, 5, "#eaf7ee", GREEN)
    f.append(line(295, 300, 295, 320, color=GREEN, sw=2))   # стрілка вниз на потрібний байт
    f.append(text(295, 296, "записали — і все", size=10, color=GREEN, bold=True))
    f.append(text(484, 372, "решта байтів недоторкані; стирати нічого",
                  size=11, color=GREEN, bold=True))

    f.append(text(W / 2, 446, "Для лічильника напрацювання чи окремої уставки це безцінно: "
                  "оновив одне число — і не переписав увесь блок.", size=12, color=INK))
    render(os.path.join(IMG, "byte-write.svg"), W, H, *f)


# ── 2. EEPROM проти FRAM: ресурс, швидкість, енергія ─────────────────────────
def fig_eeprom_vs_fram():
    W, H = 1000, 470
    f = [text(W / 2, 32, "EEPROM проти FRAM: де межа ресурсу й чому FRAM швидша",
              size=19, bold=True)]
    f.append(text(W / 2, 55, "FRAM витримує практично необмежено перезаписів і пише миттєво; "
                  "EEPROM дешевша, але цикли її зношують",
                  size=12.5, color=MUTED, italic=True))

    # колонки
    cx_axis, cx_ee, cx_fr = 245, 545, 825
    x_axis, w_axis = 80, 330
    x_ee, w_ee = 410, 270
    x_fr, w_fr = 680, 290
    y0 = 92
    rh = 48

    # шапка
    def header(x, w, cx, label, color):
        out = [rect(x, y0, w, rh, fill="#eef0f4", stroke=MUTED, sw=1.6, rx=0)]
        out.append(text(cx, y0 + 30, label, size=14, color=color, bold=True))
        return out
    f += header(x_axis, w_axis, cx_axis, "Вісь порівняння", INK)
    f += header(x_ee, w_ee, cx_ee, "EEPROM", BLUE)
    f += header(x_fr, w_fr, cx_fr, "FRAM", GREEN)

    rows = [
        ("Ресурс перезапису комірки", "~10⁴–10⁶ циклів", "~10¹²–10¹⁴ (≈ безмежно)"),
        ("Час запису байта",          "мілісекунди",     "як читання, наносекунди"),
        ("Енергія на запис",          "помітна",         "дуже мала"),
        ("Нелеткість",                "так",             "так"),
        ("Ціна за біт",               "низька",          "вища"),
        ("Коли брати",                "рідкі уставки, дешево", "часті записи, лог по живленню"),
    ]
    for i, (axis, ee, fr) in enumerate(rows):
        y = y0 + rh * (i + 1)
        band = BG if i % 2 == 0 else "#fafafa"
        f.append(rect(x_axis, y, w_axis, rh, fill=band, stroke="#e4e4e4", sw=1, rx=0))
        f.append(rect(x_ee, y, w_ee, rh, fill=band, stroke="#e4e4e4", sw=1, rx=0))
        f.append(rect(x_fr, y, w_fr, rh, fill=band, stroke="#e4e4e4", sw=1, rx=0))
        f.append(text(x_axis + 16, y + 29, axis, size=12, color=INK, anchor="start"))
        f.append(text(cx_ee, y + 29, ee, size=12, color=BLUE, bold=True))
        f.append(text(cx_fr, y + 29, fr, size=12, color=GREEN, bold=True))

    # рамка довкола таблиці
    f.append(rect(x_axis, y0, (x_fr + w_fr) - x_axis, rh * (len(rows) + 1),
                  fill="none", stroke=MUTED, sw=1.6, rx=0))

    f.append(text(W / 2, 456, "FRAM сяє там, де треба часто й безпечно зберігати стан — "
                  "дописувати лічильник при кожному циклі чи рятувати дані при зникненні живлення.",
                  size=11.5, color=GREEN, bold=True))
    render(os.path.join(IMG, "eeprom-vs-fram.svg"), W, H, *f)


# ── 3. Петля гістерезису сегнетоелектрика: серце FRAM ────────────────────────
def fig_hysteresis():
    W, H = 1000, 560
    f = [text(W / 2, 32, "Петля гістерезису сегнетоелектрика: два стійкі стани без живлення",
              size=18, bold=True)]
    f.append(text(W / 2, 55, "Поляризація P проти поля E: при E=0 лишається ±Pr (два біти); "
                  "перемикання коштує подолати коерцитивне поле ±Ec",
                  size=12.5, color=MUTED, italic=True))

    # осі в центрі
    cx, cy = 500, 320
    ax_w, ax_h = 360, 200      # піввісь по E, по P
    # осі
    f.append(arrow(cx - ax_w - 20, cy, cx + ax_w + 20, cy, color=INK, sw=1.6))   # E
    f.append(arrow(cx, cy + ax_h + 30, cx, cy - ax_h - 30, color=INK, sw=1.6))   # P
    f.append(text(cx + ax_w + 30, cy + 5, "E", size=14, color=INK, bold=True, anchor="start"))
    f.append(text(cx + ax_w + 30, cy + 22, "поле", size=10.5, color=MUTED, anchor="start"))
    f.append(text(cx + 12, cy - ax_h - 34, "P", size=14, color=INK, bold=True, anchor="start"))
    f.append(text(cx + 12, cy - ax_h - 18, "поляризація", size=10.5, color=MUTED, anchor="start"))

    # рівні насичення й залишку
    Ps = ax_h * 0.86     # насичення
    Pr = ax_h * 0.62     # залишкова
    Ec = ax_w * 0.42     # коерцитивне

    # пунктири рівнів ±Pr і ±Ec
    for py, lbl, col in [(-Pr, "+Pr", FIELD), (Pr, "−Pr", FIELD)]:
        f.append(line(cx - ax_w, cy + py, cx, cy + py, color=col, sw=1.0, dash="4,4"))
    for px, lbl in [(-Ec, "−Ec"), (Ec, "+Ec")]:
        f.append(line(cx + px, cy, cx + px, cy + Pr if px < 0 else cy - Pr, color=AMBER, sw=1.0, dash="4,4"))

    # дві гілки петлі як кубічні криві Безьє (нижня зліва-направо, верхня справа-наліво)
    L, R = cx - ax_w, cx + ax_w
    yb = cy + Ps    # низ насичення
    yt = cy - Ps    # верх насичення
    # нижня гілка: від лівого-низу через (-? ) до правого-верху, різкий підйом біля +Ec
    lower = ('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f '
             'S %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="3"/>' % (
                 L, yb,
                 cx - Ec * 0.3, yb, cx + Ec, cy + Pr * 0.9,
                 cx + Ec, cy - Pr * 0.2,
                 R - 40, yt, R, yt, NEG))
    # верхня гілка: від правого-верху назад до лівого-низу, спад біля −Ec
    upper = ('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f '
             'S %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="3"/>' % (
                 R, yt,
                 cx + Ec * 0.3, yt, cx - Ec, cy - Pr * 0.9,
                 cx - Ec, cy + Pr * 0.2,
                 L + 40, yb, L, yb, POS))
    f.append(lower)
    f.append(upper)

    # стрілки напрямку обходу
    f.append(text(cx + Ec + 90, cy - Ps + 4, "→ запис «1»", size=11, color=NEG, bold=True))
    f.append(text(cx - Ec - 90, cy + Ps - 2, "← запис «0»", size=11, color=POS, bold=True))

    # точки залишкової поляризації (стани при E=0)
    f.append(circle(cx, cy - Pr, 6, fill="#eaf7ee", stroke=FIELD, sw=2.2))
    f.append(circle(cx, cy + Pr, 6, fill="#eaf7ee", stroke=FIELD, sw=2.2))
    f.append(text(cx - 14, cy - Pr - 8, "+Pr = «1»", size=11.5, color=FIELD, bold=True, anchor="end"))
    f.append(text(cx + 14, cy + Pr + 18, "−Pr = «0»", size=11.5, color=FIELD, bold=True, anchor="start"))

    # мітки коерцитивного поля
    f.append(text(cx + Ec, cy + 18, "+Ec", size=11, color=AMBER, bold=True))
    f.append(text(cx - Ec, cy - 8, "−Ec", size=11, color=AMBER, bold=True))

    # нижній підсумок
    box = fitbox(120, 502, 760, 48,
                 "При знятому полі (E=0) диполі не повертаються самі — лишаються в +Pr або −Pr.\n"
                 "Ось нелеткість: біт тримає застигла орієнтація диполів, а не струм чи заряд-що-стікає.",
                 size=12, fill="#eaf7ee", stroke=FIELD, sw=1.4, color=INK)
    f.append(box)
    render(os.path.join(IMG, "hysteresis.svg"), W, H, *f)


# ── 4. Руйнівне читання FRAM: подати поле, зміряти заряд, дописати назад ──────
def fig_destructive_read():
    W, H = 1000, 470
    f = [text(W / 2, 32, "Руйнівне читання FRAM: перемкнути, зміряти струм, дописати назад",
              size=18, bold=True)]
    f.append(text(W / 2, 55, "Читання силоміць заганяє комірку в один стан; біт впізнають "
                  "за РОЗМІРОМ струму перемикання — а потім відновлюють",
                  size=12.5, color=MUTED, italic=True))

    # три панелі-кроки
    xs = [70, 375, 680]
    w = 260
    y = 95
    h = 210
    titles = ["1 · подати поле читання", "2 · зміряти заряд на біт-лінії", "3 · дописати прочитане назад"]
    cols = [NEG, AMBER, FIELD]
    for x, t, c in zip(xs, titles, cols):
        f.append(rect(x, y, w, h, fill="#fbfbfd", stroke=c, sw=1.8, rx=8))
        f.append(text(x + w / 2, y + 24, t, size=12.5, color=c, bold=True))

    # панель 1: комірка + стрілка поля
    x = xs[0]
    f.append(rect(x + 40, y + 55, 80, 90, fill="#eef0f4", stroke=INK, sw=1.4, rx=4))
    f.append(text(x + 80, y + 48, "комірка", size=10.5, color=MUTED))
    # диполі вниз
    for dx in (-18, 0, 18):
        f.append(arrow(x + 80 + dx, y + 70, x + 80 + dx, y + 132, color=NEG, sw=2))
    f.append(text(x + 165, y + 100, "тиснемо\nполем\nу стан «1»", size=10.5, color=NEG, anchor="start"))
    f.append(text(x + 80, y + 175, "лінію слова — увімк.", size=10, color=MUTED))

    # панель 2: два різні імпульси струму
    x = xs[1]
    bx, by = x + 30, y + 150
    f.append(line(bx, by, bx + w - 70, by, color=INK, sw=1.2))          # вісь часу
    f.append(line(bx, by, bx, by - 90, color=INK, sw=1.2))              # вісь струму
    f.append(text(bx - 6, by - 92, "I", size=11, color=INK, anchor="end", bold=True))
    # великий пік (перемкнувся → був «0»)
    f.append('<path d="M %.1f %.1f Q %.1f %.1f, %.1f %.1f T %.1f %.1f" fill="none" stroke="%s" stroke-width="2.4"/>' % (
        bx + 8, by, bx + 30, by - 78, bx + 60, by, bx + 90, by, POS))
    f.append(text(bx + 46, by - 84, "великий", size=10, color=POS, bold=True))
    # малий пік (не перемкнувся → був «1»)
    f.append('<path d="M %.1f %.1f Q %.1f %.1f, %.1f %.1f T %.1f %.1f" fill="none" stroke="%s" stroke-width="2.4"/>' % (
        bx + 100, by, bx + 116, by - 30, bx + 140, by, bx + 168, by, FIELD))
    f.append(text(bx + 132, by - 38, "малий", size=10, color=FIELD, bold=True))
    f.append(text(x + w / 2, y + 178, "великий Q → був «0»;  малий Q → був «1»", size=10, color=INK))

    # панель 3: відновлення
    x = xs[2]
    f.append(rect(x + 40, y + 55, 80, 90, fill="#eef0f4", stroke=INK, sw=1.4, rx=4))
    # диполі назад у прочитаний стан (вгору = «1»)
    for dx in (-18, 0, 18):
        f.append(arrow(x + 80 + dx, y + 132, x + 80 + dx, y + 70, color=FIELD, sw=2))
    f.append(text(x + 165, y + 95, "контролер\nсам пише\nбіт назад", size=10.5, color=FIELD, anchor="start"))
    f.append(text(x + 80, y + 175, "читач цього не бачить", size=10, color=MUTED))

    # стрілки між панелями
    f.append(arrow(xs[0] + w + 6, y + h / 2, xs[1] - 6, y + h / 2, color=INK, sw=2))
    f.append(arrow(xs[1] + w + 6, y + h / 2, xs[2] - 6, y + h / 2, color=INK, sw=2))

    box = fitbox(90, 338, 820, 50,
                 "Тому «прочитати» у FRAM фізично означає «стерти й відновити» — як у DRAM. Кожне читання\n"
                 "витрачає цикл перемикання; рятує лише те, що ресурс FRAM ~10¹²–10¹⁴ практично невичерпний.",
                 size=12, fill="#fff7e6", stroke=AMBER, sw=1.4, color=INK)
    f.append(box)
    f.append(text(W / 2, 410, "Уся ця машинерія схована в чипі: назовні FRAM поводиться як звичайна "
                  "пам'ять «прочитав байт — і живи далі».", size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "destructive-read.svg"), W, H, *f)


# ── 5. Внутрішній цикл запису EEPROM: чому мілісекунди ────────────────────────
def fig_write_cycle():
    W, H = 1000, 430
    f = [text(W / 2, 32, "Внутрішній цикл запису EEPROM: звідки беруться мілісекунди",
              size=18, bold=True)]
    f.append(text(W / 2, 55, "Шинна передача байта — мікросекунди; а сам запис у комірку — "
                  "окремий повільний цикл, поки чип «зайнятий»",
                  size=12.5, color=MUTED, italic=True))

    # часова вісь
    x0, x1 = 90, 910
    ty = 300
    f.append(arrow(x0 - 10, ty, x1 + 20, ty, color=INK, sw=1.6))
    f.append(text(x1 + 25, ty + 5, "час", size=12, color=INK, anchor="start", bold=True))

    # фази (частка ширини) — передача крихітна, внутрішній цикл довгий
    segs = [
        ("передача\nбайта", 0.11, NEG, "~десятки мкс"),
        ("насос:\n~15–20 В", 0.21, AMBER, ""),
        ("тунелювання\nу комірку", 0.40, POS, "внутрішній цикл ~3–10 мс"),
        ("перевірка", 0.16, FIELD, ""),
        ("готовий\n(ACK)", 0.12, FIELD, ""),
    ]
    x = x0
    total = x1 - x0
    for name, frac, col, note in segs:
        w = total * frac
        f.append(rect(x, ty - 46, w, 46, fill="#fbfbfd", stroke=col, sw=1.6, rx=4))
        f.append(fitbox(x + 3, ty - 44, w - 6, 42, name, size=10, fill="none", stroke="none", color=col, bold=True))
        if note:
            f.append(text(x + w / 2, ty + 22, note, size=10, color=MUTED))
        x += w

    # дужка «чип зайнятий»
    busy_x0 = x0 + total * 0.10
    busy_x1 = x0 + total * (0.10 + 0.22 + 0.40 + 0.16)
    f.append(line(busy_x0, ty - 70, busy_x1, ty - 70, color=INK, sw=1.4))
    f.append(line(busy_x0, ty - 70, busy_x0, ty - 60, color=INK, sw=1.4))
    f.append(line(busy_x1, ty - 70, busy_x1, ty - 60, color=INK, sw=1.4))
    f.append(text((busy_x0 + busy_x1) / 2, ty - 78, "чип ЗАЙНЯТИЙ — нової команди не прийме (звідси ACK polling / біт WIP)",
                  size=11, color=INK, bold=True))

    box = fitbox(90, 338, 820, 52,
                 "У FRAM цієї довгої частини НЕМА взагалі: перемикання диполів завершується за час самої шинної\n"
                 "передачі, тож «зайнятого» стану не буває, чекати нічого — запис такий самий швидкий, як читання.",
                 size=12, fill="#eaf7ee", stroke=FIELD, sw=1.4, color=INK)
    f.append(box)
    render(os.path.join(IMG, "write-cycle.svg"), W, H, *f)


# ── 6. Карта життя: знос (цикли) × збереження (роки за температури) ───────────
def fig_life_map():
    W, H = 1000, 500
    f = [text(W / 2, 32, "Дві різні межі життя комірки: ЗНОС і ЗБЕРЕЖЕННЯ — не плутати",
              size=18, bold=True)]
    f.append(text(W / 2, 55, "Вісь X — скільки перезаписів витримає (endurance); "
                  "вісь Y — як довго тримає біт без живлення (retention)",
                  size=12.5, color=MUTED, italic=True))

    # осі
    ox, oy = 130, 400
    ax_w, ax_h = 720, 300
    f.append(arrow(ox, oy, ox + ax_w + 10, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - ax_h - 10, color=INK, sw=1.6))
    f.append(text(ox + ax_w + 12, oy + 6, "ЗНОС: перезаписів до відмови →", size=11.5, color=INK, anchor="end", bold=True))
    f.append(text(ox - 12, oy - ax_h - 14, "ЗБЕРЕЖЕННЯ ↑", size=11.5, color=INK, anchor="start", bold=True))

    # логарифмічні поділки по X (цикли)
    xticks = [("10⁴", 0.10), ("10⁶", 0.30), ("10⁸", 0.50), ("10¹⁰", 0.70), ("10¹²", 0.86), ("10¹⁴", 0.98)]
    for lbl, fr in xticks:
        xx = ox + ax_w * fr
        f.append(line(xx, oy, xx, oy + 6, color=INK, sw=1.2))
        f.append(text(xx, oy + 22, lbl, size=10.5, color=MUTED))
    # поділки по Y (роки збереження)
    yticks = [("1 рік", 0.18), ("10 років", 0.48), (">40 років", 0.82)]
    for lbl, fr in yticks:
        yy = oy - ax_h * fr
        f.append(line(ox - 6, yy, ox, yy, color=INK, sw=1.2))
        f.append(text(ox - 12, yy + 4, lbl, size=10.5, color=MUTED, anchor="end"))

    # блок EEPROM
    ex = ox + ax_w * 0.06
    ew = ax_w * 0.26
    ey = oy - ax_h * 0.86
    eh = ax_h * 0.30
    f.append(rect(ex, ey, ew, eh, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    f.append(text(ex + ew / 2, ey + 26, "EEPROM", size=14, color=NEG, bold=True))
    f.append(text(ex + ew / 2, ey + 46, "10⁴–10⁶ циклів", size=10.5, color=NEG))
    f.append(text(ex + ew / 2, ey + 62, "~10+ років (кімн.)", size=10.5, color=NEG))

    # стрілка «wear leveling розширює вправо»
    f.append(arrow(ex + ew, ey + eh * 0.5, ex + ew + 120, ey + eh * 0.5, color=AMBER, sw=2))
    f.append(text(ex + ew + 60, ey + eh * 0.5 - 10, "wear leveling", size=10.5, color=AMBER, bold=True))
    f.append(text(ex + ew + 60, ey + eh * 0.5 + 22, "розмазує знос → далі вправо", size=9.5, color=AMBER))

    # блок FRAM
    fx = ox + ax_w * 0.80
    fw = ax_w * 0.20
    fy = oy - ax_h * 0.62
    fh = ax_h * 0.30
    f.append(rect(fx, fy, fw, fh, fill="#eaf7ee", stroke=FIELD, sw=2, rx=8))
    f.append(text(fx + fw / 2, fy + 26, "FRAM", size=14, color=FIELD, bold=True))
    f.append(text(fx + fw / 2, fy + 46, "10¹²–10¹⁴", size=10.5, color=FIELD))
    f.append(text(fx + fw / 2, fy + 62, "~10 років*", size=10.5, color=FIELD))

    # виноска про збереження FRAM
    f.append(text(fx + fw / 2, fy + fh + 20, "*збереження FRAM НЕ безмежне", size=9.5, color=MUTED, italic=True))
    f.append(text(fx + fw / 2, fy + fh + 34, "деполяризація/imprint з часом", size=9.5, color=MUTED, italic=True))

    box = fitbox(140, 450, 720, 44,
                 "FRAM виграє по ЗНОСУ на порядки, але по ЗБЕРЕЖЕННЮ вони близькі (~роки):\n"
                 "«необмежений ресурс» не означає «вічне сховище» — це різні осі.",
                 size=12, fill="#fff7e6", stroke=AMBER, sw=1.4, color=INK)
    f.append(box)
    render(os.path.join(IMG, "life-map.svg"), W, H, *f)


# ── 7. [math] Заряд перемикання Q=2·Pr·A → напруга на біт-лінії → підлога площі ─
def fig_switching_charge():
    W, H = 1000, 560
    f = [text(W / 2, 32, "Сигнал читання: заряд перемикання Q = 2·Pr·A стає напругою на біт-лінії",
              size=17.5, bold=True)]
    f.append(text(W / 2, 55, "Перекид стану міняє поляризацію на ΔP = 2·Pr; цей заряд висипається "
                  "на ємність біт-лінії й дає крихітний стрибок напруги",
                  size=12.5, color=MUTED, italic=True))

    # --- зліва: два стани й різниця 2Pr як стовпчики ---
    lx = 90
    base = 250
    barw = 46
    # стовпчик +Pr (вгору) і −Pr (вниз) від осі
    f.append(line(lx - 20, base, lx + 190, base, color=INK, sw=1.2))         # вісь P=0
    f.append(text(lx - 24, base + 4, "P=0", size=10, color=MUTED, anchor="end"))
    f.append(rect(lx + 20, base - 88, barw, 88, fill="#eaf7ee", stroke=FIELD, sw=1.8, rx=3))
    f.append(text(lx + 20 + barw / 2, base - 96, "+Pr", size=11.5, color=FIELD, bold=True))
    f.append(text(lx + 20 + barw / 2, base - 44, "«1»", size=11, color=FIELD, bold=True))
    f.append(rect(lx + 110, base, barw, 88, fill="#fdecea", stroke=POS, sw=1.8, rx=3))
    f.append(text(lx + 110 + barw / 2, base + 104, "−Pr", size=11.5, color=POS, bold=True))
    f.append(text(lx + 110 + barw / 2, base + 48, "«0»", size=11, color=POS, bold=True))
    # дужка різниці 2Pr
    f.append(line(lx + 178, base - 88, lx + 178, base + 88, color=AMBER, sw=1.6))
    f.append(line(lx + 172, base - 88, lx + 178, base - 88, color=AMBER, sw=1.6))
    f.append(line(lx + 172, base + 88, lx + 178, base + 88, color=AMBER, sw=1.6))
    f.append(text(lx + 186, base + 4, "ΔP = 2·Pr", size=12, color=AMBER, bold=True, anchor="start"))
    f.append(text(lx + 40, base + 150, "різниця двох станів —", size=10.5, color=INK))
    f.append(text(lx + 40, base + 166, "ось що можна виміряти", size=10.5, color=INK))

    # --- посередині: множимо на площу → заряд ---
    mx = 420
    box1 = fitbox(mx, 150, 210, 66,
                  "заряд, що перетече:\nQ = ΔP · A = 2·Pr·A",
                  size=13, fill="#fff7e6", stroke=AMBER, sw=1.6, color=INK, bold=True)
    f.append(box1)
    f.append(arrow(lx + 250, base, mx - 6, 185, color=INK, sw=1.8))

    # --- справа: заряд на ємність біт-лінії → напруга ---
    rx = 700
    f.append(rect(rx, 150, 220, 92, fill="#fbfbfd", stroke=NEG, sw=1.8, rx=8))
    f.append(text(rx + 110, 176, "висипається на C_біт", size=12, color=NEG, bold=True))
    f.append(text(rx + 110, 206, "ΔV = Q / C_біт", size=14, color=NEG, bold=True))
    f.append(text(rx + 110, 228, "= 2·Pr·A / C_біт", size=11.5, color=NEG))
    f.append(arrow(mx + 215, 185, rx - 6, 190, color=INK, sw=1.8))

    # --- низ: числовий приклад і колапс при зменшенні A ---
    ny = 300
    f.append(rect(90, ny, 400, 168, fill="#f7f9fc", stroke=MUTED, sw=1.4, rx=8))
    f.append(text(290, ny + 24, "Числа (типовий FRAM-конденсатор)", size=12.5, color=INK, bold=True))
    ex = [
        "Pr ≈ 20 мкКл/см²  =  2·10⁻⁵ Кл/см²",
        "A ≈ 1 мкм² = 10⁻⁸ см²",
        "Q = 2·Pr·A ≈ 4·10⁻¹³ Кл = 0.4 пКл",
        "C_біт ≈ 200 фФ  →  ΔV ≈ 2 мВ",
    ]
    for i, ln in enumerate(ex):
        f.append(text(110, ny + 52 + i * 26, ln, size=11.5, color=INK, anchor="start"))
    f.append(text(290, ny + 158, "2 мВ — це вже близько до шуму підсилювача!", size=11, color=POS, bold=True))

    # права нижня: чому площу не можна зменшувати нескінченно
    f.append(rect(520, ny, 400, 168, fill="#fdecea", stroke=POS, sw=1.4, rx=8))
    f.append(text(720, ny + 24, "Чому це — підлога розміру комірки", size=12.5, color=POS, bold=True))
    reasons = [
        "A ↓ (менша комірка) → Q ↓ → ΔV ↓",
        "але C_біт майже не меншає",
        "(її задає довжина металевої лінії)",
        "ΔV мусить лишатися > шуму: ΔV ≳ 100 мВ·…",
        "→ є найменша A, нижче якої біт не",
        "   відрізнити від шуму. Pr — головна",
        "   ручка, що цю підлогу піднімає.",
    ]
    for i, ln in enumerate(reasons):
        f.append(text(540, ny + 50 + i * 17, ln, size=10.3, color=INK, anchor="start"))

    render(os.path.join(IMG, "switching-charge.svg"), W, H, *f)


# ── 8. [math] Підлога коерцитивного поля: imprint зсуває петлю, деполяризація гризе
def fig_ec_floor():
    W, H = 1000, 540
    f = [text(W / 2, 32, "Чому Ec не можна робити скільки завгодно малим",
              size=18, bold=True)]
    f.append(text(W / 2, 55, "Внутрішні поля — деполяризувальне E_dep та imprint E_imp — "
                  "нікуди не діваються; коерцитивне поле мусить лишатися більшим за них",
                  size=12.5, color=MUTED, italic=True))

    cx, cy = 340, 300
    ax_w, ax_h = 250, 150
    # осі
    f.append(arrow(cx - ax_w - 20, cy, cx + ax_w + 20, cy, color=INK, sw=1.5))
    f.append(arrow(cx, cy + ax_h + 25, cx, cy - ax_h - 25, color=INK, sw=1.5))
    f.append(text(cx + ax_w + 26, cy + 5, "E", size=13, color=INK, bold=True, anchor="start"))
    f.append(text(cx + 10, cy - ax_h - 28, "P", size=13, color=INK, bold=True, anchor="start"))

    Ps = ax_h * 0.82
    Pr = ax_h * 0.60
    Ec = ax_w * 0.34
    shift = ax_w * 0.16     # imprint-зсув петлі по осі E

    L, R = cx - ax_w, cx + ax_w
    yb, yt = cy + Ps, cy - Ps
    # ЗСУНУТА петля (imprint) — обидві гілки зсунуті праворуч на shift
    s = shift
    lower = ('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f S %.1f %.1f, %.1f %.1f" '
             'fill="none" stroke="%s" stroke-width="2.6"/>' % (
                 L, yb, cx - Ec * 0.3 + s, yb, cx + Ec + s, cy + Pr * 0.9,
                 cx + Ec + s, cy - Pr * 0.2, R - 40, yt, R, yt, NEG))
    upper = ('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f S %.1f %.1f, %.1f %.1f" '
             'fill="none" stroke="%s" stroke-width="2.6"/>' % (
                 R, yt, cx + Ec * 0.3 + s, yt, cx - Ec + s, cy - Pr * 0.9,
                 cx - Ec + s, cy + Pr * 0.2, L + 40, yb, L, yb, POS))
    f.append(lower)
    f.append(upper)

    # ідеальна (центрована) петля — тонким пунктиром для порівняння
    ideal = [
        (L, yb, cx - Ec * 0.3, yb, cx + Ec, cy + Pr * 0.9, cx + Ec, cy - Pr * 0.2, R - 40, yt, R, yt),
        (R, yt, cx + Ec * 0.3, yt, cx - Ec, cy - Pr * 0.9, cx - Ec, cy + Pr * 0.2, L + 40, yb, L, yb),
    ]
    for p in ideal:
        f.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f S %.1f %.1f, %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="1.1" stroke-dasharray="3,4"/>' % (p + (MUTED,)))

    # позначки Ec на зсунутій петлі
    f.append(line(cx + Ec + s, cy, cx + Ec + s, cy - 6, color=AMBER, sw=1.2))
    f.append(text(cx + Ec + s, cy + 16, "+Ec", size=10.5, color=AMBER, bold=True))
    f.append(line(cx - Ec + s, cy, cx - Ec + s, cy + 6, color=AMBER, sw=1.2))
    f.append(text(cx - Ec + s, cy - 8, "−Ec", size=10.5, color=AMBER, bold=True))
    # зсув imprint
    f.append(line(cx, cy - ax_h + 6, cx + s, cy - ax_h + 6, color=POS, sw=1.6))
    f.append(text(cx + s / 2, cy - ax_h - 4, "E_imp", size=10.5, color=POS, bold=True))
    f.append(text(cx + s / 2 + 40, cy - ax_h - 4, "(петля з'їхала)", size=9.5, color=POS, anchor="start"))

    # ілюстрація деполяризувального поля стрілкою всередині
    f.append(text(L + 4, yt - 8, "ідеальна (пунктир)", size=9.5, color=MUTED, anchor="start"))

    # права колонка — три формули-обмеження
    bx = 640
    f.append(text(bx, 118, "Три сили тиснуть на Ec знизу:", size=13, color=INK, anchor="start", bold=True))
    b1 = fitbox(bx, 132, 320, 78,
                "1) Деполяризувальне поле\n"
                "E_dep = −Pr / (ε₀·ε)\n"
                "тягне диполі назад у нуль — тобто розряджає біт",
                size=11, fill="#eaf0fd", stroke=NEG, sw=1.5, color=INK)
    f.append(b1)
    b2 = fitbox(bx, 224, 320, 78,
                "2) Imprint E_imp\n"
                "заряди-пастки зсувають петлю по E;\n"
                "один стан стає «улюбленим» — інший не дописується",
                size=11, fill="#fdecea", stroke=POS, sw=1.5, color=INK)
    f.append(b2)
    b3 = fitbox(bx, 316, 320, 78,
                "3) Теплові поштовхи (kT)\n"
                "з часом перекидають диполі через бар'єр,\n"
                "а бар'єр тим нижчий, чим менше Ec",
                size=11, fill="#fff7e6", stroke=AMBER, sw=1.5, color=INK)
    f.append(b3)

    box = fitbox(80, 430, 840, 78,
                 "Робоче поле запису мусить упевнено долати Ec, а сам Ec — з запасом перекривати "
                 "суму внутрішніх полів:  E_write  >  Ec  >  E_dep + E_imp.\n"
                 "Зробити Ec крихітним — означає, що деполяризація й imprint самі перекинуть біт: "
                 "запис легшає, але дані не тримаються. Тому Ec має свою ПІДЛОГУ, і живлення запису "
                 "мусить бути достатнім, щоб її подолати.",
                 size=12, fill="#f7f9fc", stroke=MUTED, sw=1.5, color=INK)
    f.append(box)
    render(os.path.join(IMG, "ec-floor.svg"), W, H, *f)


# ── 9. Кільце слотів: пошук голови за максимумом послідовності ────────────────
def fig_ring_head():
    import math
    W, H = 1000, 540
    f = [text(W / 2, 32, "Кільце слотів: як при старті знайти голову",
              size=19, bold=True)]
    f.append(text(W / 2, 55, "Кожен слот несе дані, послідовність і контрольну суму; "
                  "голова — дійсний слот із найбільшою послідовністю",
                  size=12.5, color=MUTED, italic=True))

    cx, cy, R = 330, 315, 158           # центр і радіус кільця
    N = 8
    # (послідовність, дійсний?)  — слот 5 недописаний (обрив живлення)
    slots = [(24, True), (25, True), (26, True), (27, True),
             (23, True), (0, False), (21, True), (22, True)]
    head = 3                            # слот із максимальною дійсною послідовністю

    for i in range(N):
        a = -math.pi / 2 + 2 * math.pi * i / N     # старт зверху, за годинником
        x = cx + R * math.cos(a)
        y = cy + R * math.sin(a)
        seq, ok = slots[i]
        if i == head:
            fill, stroke, sw = "#eaf7ee", FIELD, 2.4
        elif not ok:
            fill, stroke, sw = "#fdecea", POS, 2.0
        else:
            fill, stroke, sw = BG, "#cfcfcf", 1.4
        f.append(circle(x, y, 46, fill=fill, stroke=stroke, sw=sw))
        f.append(text(x, y - 20, "слот %d" % i, size=11, color=MUTED, bold=True))
        if ok:
            f.append(text(x, y - 1, "seq %d" % seq, size=14, color=INK, bold=True))
            f.append(text(x, y + 17, "crc ✓", size=10.5, color=FIELD, bold=True))
        else:
            f.append(text(x, y - 1, "seq ??", size=13, color=POS, bold=True))
            f.append(text(x, y + 17, "crc ✗", size=10.5, color=POS, bold=True))

    f.append(text(cx, cy - 6, "запис", size=12, color=MUTED, bold=True))
    f.append(text(cx, cy + 12, "по колу →", size=12, color=MUTED, bold=True))

    # позначки: голова й обрив
    hx = cx + R * math.cos(-math.pi / 2 + 2 * math.pi * head / N)
    hy = cy + R * math.sin(-math.pi / 2 + 2 * math.pi * head / N)
    f.append(text(hx + 92, hy - 6, "ГОЛОВА", size=13, color=FIELD, bold=True, anchor="start"))
    f.append(text(hx + 92, hy + 12, "max(seq) серед цілих", size=10.5, color=FIELD,
                  anchor="start"))
    bx_ = cx + R * math.cos(-math.pi / 2 + 2 * math.pi * 5 / N)
    by_ = cy + R * math.sin(-math.pi / 2 + 2 * math.pi * 5 / N)
    f.append(text(bx_ - 92, by_ + 4, "обрив живлення тут:", size=10.5, color=POS,
                  anchor="end"))
    f.append(text(bx_ - 92, by_ + 21, "crc не збіглась → пропускаємо", size=10.5,
                  color=POS, anchor="end"))

    # права колонка — алгоритм старту
    box = fitbox(640, 130, 330, 300,
                 "При старті (wl_mount):\n"
                 "\n"
                 "1) обійти ВСІ слоти\n"
                 "2) перерахувати crc кожного;\n"
                 "   не збіглась → слот недійсний\n"
                 "   (недописаний / вигорілий)\n"
                 "3) серед ДІЙСНИХ узяти той,\n"
                 "   де послідовність найбільша\n"
                 "   → це і є голова кільця\n"
                 "\n"
                 "Жодного стану в EEPROM,\n"
                 "крім самих слотів: голова\n"
                 "відновлюється з даних щоразу.\n"
                 "Новий запис ляже в слот\n"
                 "за головою (тут — слот 4).",
                 size=12, fill="#f7f9fc", stroke=MUTED, sw=1.5, color=INK)
    f.append(box)

    f.append(text(W / 2, 512, "Позиція в масиві нічого не значить (кільце циклічне) — "
                  "«останній» визначає лише максимум монотонної послідовності.",
                  size=12, color=INK))
    render(os.path.join(IMG, "ring-head.svg"), W, H, *f)


# ── 10. Розмір слота під сторінку EEPROM ─────────────────────────────────────
def fig_slot_page():
    W, H = 1000, 470
    f = [text(W / 2, 32, "Розмір слота під сторінку EEPROM: 13 vs 16 байтів",
              size=19, bold=True)]
    f.append(text(W / 2, 55, "Слот, що перелазить межу сторінки, коштує ДВОХ внутрішніх циклів; "
                  "слот-дільник сторінки — рівно одного",
                  size=12.5, color=MUTED, italic=True))

    PAGE = 32
    NPAGE = 2                    # показуємо дві сторінки (64 байти)
    x0 = 175                     # ліворуч — місце під підпис рядка
    cellw = (960 - x0) / (NPAGE * PAGE)   # 64 байти впишемо у ~785 px
    total = NPAGE * PAGE

    def byte_row(y, slot_len, label, good):
        out = [text(x0 - 12, y + 16, label, size=12, color=(FIELD if good else POS),
                    anchor="end", bold=True)]
        # межі сторінок — жирні вертикалі
        for p in range(NPAGE + 1):
            xx = x0 + p * PAGE * cellw
            out.append(line(xx, y - 4, xx, y + 38, color=INK, sw=2.2))
            if p < NPAGE:
                out.append(text(xx + 4, y - 8, "сторінка %d (32 Б)" % p, size=10,
                                color=MUTED, anchor="start"))
        # слоти — доки поміщаються в дві сторінки цілком
        colors = ["#eaf0fd", "#eaf7ee", "#fff7e6", "#f3e8fd", "#eafaf1", "#fdeaea"]
        s = 0
        idx = 0
        while s + slot_len <= total:
            sx = x0 + s * cellw
            crosses = (s // PAGE) != ((s + slot_len - 1) // PAGE)
            fill = colors[idx % len(colors)]
            out.append(rect(sx, y, slot_len * cellw, 34,
                            fill=fill, stroke=(POS if crosses else LINE),
                            sw=(2.6 if crosses else 1.4), rx=3))
            out.append(text(sx + slot_len * cellw / 2, y + 22,
                            "%d" % idx, size=11,
                            color=(POS if crosses else INK), bold=crosses))
            if crosses:
                out.append(text(sx + slot_len * cellw / 2, y + 52,
                                "↑ перелазить межу → 2 цикли", size=10, color=POS, bold=True))
            s += slot_len
            idx += 1
        return out

    f += byte_row(120, 13, "слот 13 Б\n(не дільник)", False)
    f.append(text(x0, 205, "13 не ділить 32 → слот №2 перелазить межу сторінки: "
                  "його запис = 2 внутрішні цикли (подвійний знос, ширше вікно обриву)",
                  size=11.5, color=POS, anchor="start"))

    f += byte_row(300, 16, "слот 16 Б\n(дільник)", True)
    f.append(text(x0, 385, "16 = 32 / 2 → рівно 2 слоти на сторінку, жоден не перетинає межі: "
                  "кожен запис = 1 цикл. Ціна — 3 байти набивки на слот",
                  size=11.5, color=FIELD, anchor="start"))

    f.append(text(W / 2, 440, "Правило: спершу дізнайся сторінку чипа з даташита, тоді "
                  "підганяй слот (дільник сторінки) і обсяг кільця (ціле число сторінок).",
                  size=12, color=INK))
    render(os.path.join(IMG, "slot-page.svg"), W, H, *f)


# ── [hist] Дві паралельні дороги до нелеткого біта ───────────────────────────
def fig_hist_timeline():
    W, H = 1020, 470
    f = [text(W / 2, 30, "Дві дороги до нелеткого біта: одна ідея чекала 40 років, "
              "інша завоювала світ за десятиліття", size=16, bold=True)]
    f.append(text(W / 2, 52, "Різницю зробив не задум, а зрілість матеріалу й технології",
                  size=12.5, color=MUTED, italic=True))

    x0, x1 = 80, 950
    total = x1 - x0
    axis_y = 250

    def X(year):
        return x0 + total * (year - 1915) / (2015 - 1915)

    f.append(line(x0, axis_y, x1 + 10, axis_y, color=MUTED, sw=1.2))
    for yr in range(1920, 2020, 10):
        xx = X(yr)
        f.append(line(xx, axis_y - 4, xx, axis_y + 4, color=MUTED, sw=1.0))
        f.append(text(xx, axis_y + 18, str(yr), size=9.5, color=MUTED))

    def milestone(year, up, title, sub, col):
        xx = X(year)
        f.append(circle(xx, axis_y, 4.5, fill=col, stroke=col, sw=1))
        cy = (axis_y - 78) if up else (axis_y + 72)
        b, bw, bh = textbox(xx, cy, title + "\n" + sub, size=9.5, pad=6,
                            fill="#ffffff", stroke=col, sw=1.5, color=INK, min_w=90)
        top_edge = cy + bh / 2 if up else cy - bh / 2
        f.append(line(xx, axis_y + (-6 if up else 6), xx, top_edge, color=col, sw=1.1, dash="3,3"))
        f.append(b)

    f.append(text(x0 - 4, 96, "СЕГНЕТОЕЛЕКТРИК (біт у поляризації)", size=12,
                  color=FIELD, anchor="start", bold=True))
    milestone(1920, True, "Валашек", "явище (сеґн. сіль)", FIELD)
    milestone(1952, True, "Бак · MIT", "ідея пам'яті", FIELD)
    milestone(1988, True, "Ramtron", "1-й FRAM · 1T1C", FIELD)
    milestone(2011, True, "HfO₂ / FeFET", "друге життя", FIELD)

    fx0, fx1 = X(1955), X(1985)
    f.append(rect(fx0, 108, fx1 - fx0, 15, fill="#fdecea", stroke="none", rx=4))
    f.append(text((fx0 + fx1) / 2, 119,
                  "Bell · IBM · RCA · Ford пробують → відступ: втома (fatigue) + imprint",
                  size=9.5, color=POS, bold=True))

    f.append(text(x0 - 4, axis_y + 148, "ПЛАВАЮЧИЙ ЗАТВОР (біт у захопленому заряді)",
                  size=12, color=NEG, anchor="start", bold=True))
    milestone(1967, False, "Канг · Сзе", "ідея затвора", NEG)
    milestone(1971, False, "Фроман", "EPROM · 1702", NEG)
    milestone(1978, False, "Гарарі · Перлегос", "EEPROM · FLOTOX", NEG)
    milestone(2000, False, "Flash", "стирання блоками", NEG)

    gy = 150
    f.append(line(X(1952), gy, X(1988), gy, color=INK, sw=1.4))
    f.append(line(X(1952), gy, X(1952), gy + 8, color=INK, sw=1.4))
    f.append(line(X(1988), gy, X(1988), gy + 8, color=INK, sw=1.4))
    f.append(text((X(1952) + X(1988)) / 2, gy - 6, "≈ 40 років від ідеї до продукту",
                  size=11, color=INK, bold=True))

    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_byte_write()
    fig_eeprom_vs_fram()
    fig_hysteresis()
    fig_destructive_read()
    fig_write_cycle()
    fig_life_map()
    fig_switching_charge()
    fig_ec_floor()
    fig_ring_head()
    fig_slot_page()
    fig_hist_timeline()
    print("OK: figs у", IMG)
