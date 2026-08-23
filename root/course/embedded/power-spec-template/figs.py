# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── spec-spine: чотири межі ТЗ навколо вузла ───────────────────────────────────
# Ідея: ТЗ на живлення — не довгий список, а ВІДПОВІДІ на чотири питання-межі.
# Вхід (звідки), вихід (що віддаємо), поведінка навантаження (як воно смикає),
# середовище (де живе). Пропустив одну межу — вона і вкусить. Кладемо вузол
# у центр, чотири межі — навколо, кожна з ключовим питанням.
def fig_spine():
    W, H = 760, 470
    p = []
    cx, cy = 380, 215

    # центр — сам вузол живлення
    b, _, _ = textbox(cx, cy, "вузол\nживлення", size=14, bold=True,
                      color=INK, fill="#f0f2f5", stroke=INK, sw=2.2, pad=14)
    p.append(b)

    # чотири межі навколо
    nodes = [
        (380, 78,  "1 · ВХІД", "Vвх min…max,\nдопустиме просідання,\nпуск і перехідні", NEG, "#eaf0fd"),
        (610, 215, "2 · ВИХІД", "Vвих ± допуск,\nIвих, пульсація,\nшум, точність", FIELD, "#eafaf1"),
        (380, 350, "3 · НАВАНТАЖЕННЯ", "статичний і піковий струм,\nстрибки (transient),\nцикл і середнє", POS, "#fdecea"),
        (150, 215, "4 · СЕРЕДОВИЩЕ", "темп. діапазон,\nтепловідведення,\nЕМС, термін служби", MUTED, "#f3f4f6"),
    ]
    pts = []
    for x, y, head, body, col, fill in nodes:
        b, w, h = textbox(x, y, head, size=12, bold=True, color=col, fill=fill, stroke=col, sw=2, pad=9)
        p.append(b)
        p.append(text(x, y + h / 2 + 16, body.split("\n")[0], size=9.5, color=MUTED))
        for i, ln in enumerate(body.split("\n")[1:], start=1):
            p.append(text(x, y + h / 2 + 16 + i * 13, ln, size=9.5, color=MUTED))
        pts.append((x, y, w, h))

    # стрілки від кожної межі до центру (двобічні: межа задає вузол, вузол її поважає)
    import math
    for x, y, w, h in pts:
        dx, dy = cx - x, cy - y
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        sx, sy = x + ux * (w / 2 + 6), y + uy * (h / 2 + 28)
        ex, ey = cx - ux * 58, cy - uy * 34
        p.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" '
                 'stroke-width="1.8" stroke-dasharray="5 4"/>' % (sx, sy, ex, ey, MUTED))

    p.append(text(W / 2, H - 14,
                  "ТЗ — це відповіді на чотири межі; пропущена межа повертається помилкою на столі",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "spec-spine.svg"), W, H, *p,
           title="Чотири межі технічного завдання на живлення")


# ── window-vs-point: ТЗ — це вікно (min/typ/max), а не одне число ───────────────
# Ідея (серце теми): «5 В, 3 А» — брехня про спокій. Реальність — вхід ГУЛЯЄ
# смугою, вихід дозволено гуляти у вузькому допуску, навантаження СМИКАЄ.
# Малюємо вхід як широку синю смугу, вихід як вузьку зелену з ± допуском,
# і одну «точку», що бреше посередині.
def fig_window():
    W, H = 760, 420
    p = []
    left = 120
    right = 690
    axis_top = 70
    axis_bot = 330

    # вертикальна вісь напруги
    p.append(line(left, axis_top, left, axis_bot, color=INK, sw=2))
    p.append(text(left - 12, axis_top - 8, "В", size=12, color=INK, anchor="end"))

    def yv(v, vmin=0, vmax=18):  # 0..18 В у пікселі
        return axis_bot - (v - vmin) / (vmax - vmin) * (axis_bot - axis_top)

    # ── колонка ВХІД: широка смуга 12.0…16.8 В (4S LiPo) ──
    cin = left + 130
    p.append(rect(cin - 40, yv(16.8), 80, yv(12.0) - yv(16.8), fill="#eaf0fd", stroke=NEG, sw=2, rx=4))
    p.append(text(cin, yv(16.8) - 12, "16.8 В", size=10, color=NEG))
    p.append(text(cin, yv(12.0) + 16, "12.0 В", size=10, color=NEG))
    p.append(text(cin, axis_bot + 24, "ВХІД", size=12, bold=True, color=NEG))
    p.append(text(cin, axis_bot + 42, "гуляє цілою смугою", size=10, color=MUTED, italic=True))
    # стрілка-розмах
    p.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="1.6" '
             'marker-end="url(#arrow)" marker-start="url(#arrow)"/>'
             % (cin + 54, yv(16.8), cin + 54, yv(12.0), NEG))

    # ── колонка ВИХІД: вузька смуга 5 В ± 2 % ──
    cout = left + 360
    vmid, tol = 5.0, 0.1  # ±2 % ≈ ±0.1 В
    p.append(rect(cout - 40, yv(vmid + tol), 80, yv(vmid - tol) - yv(vmid + tol),
                  fill="#eafaf1", stroke=FIELD, sw=2.4, rx=4))
    p.append(line(cout - 52, yv(vmid), cout + 52, yv(vmid), color=FIELD, sw=1.4, dash="4 3"))
    p.append(text(cout, yv(vmid) + 4, "5.00 В", size=11, bold=True, color=FIELD, anchor="middle"))
    p.append(text(cout + 60, yv(vmid + tol) - 2, "+2 %", size=9.5, color=FIELD, anchor="start"))
    p.append(text(cout + 60, yv(vmid - tol) + 10, "−2 %", size=9.5, color=FIELD, anchor="start"))
    p.append(text(cout, axis_bot + 24, "ВИХІД", size=12, bold=True, color=FIELD))
    p.append(text(cout, axis_bot + 42, "вузьке вікно допуску", size=10, color=MUTED, italic=True))

    # ── колонка «одне число»: оманлива точка ──
    cp = left + 520
    p.append(circle(cp, yv(5.0), 6, fill=POS, stroke=POS, sw=2))
    p.append(text(cp, yv(5.0) - 14, "«5 В»", size=12, bold=True, color=POS))
    b, _, _ = textbox(cp, yv(5.0) + 46, "одне число\nприховує\nі смугу, і допуск,\nі струм", size=10,
                      bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.6, pad=8)
    p.append(b)

    p.append(text(W / 2, H - 16,
                  "кожен рядок ТЗ — діапазон (min · typ · max), а не точка; точка завжди бреше про межі",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "window-vs-point.svg"), W, H, *p,
           title="Специфікація — це вікно, а не одне число")


# ── absmax-vs-operating: дві зони — робоча всередині гранично-допустимої ────────
# Ідея: даташит дає ДВІ межі, і їх плутають. Recommended Operating — де працює як
# написано. Absolute Maximum — де ще не вмирає, але вже без гарантій. Між ними —
# заборонена смуга «живе, але поза ТЗ». ТЗ пишемо в зелену зону з запасом.
def fig_absmax():
    W, H = 720, 430
    p = []
    cx = 360
    top = 70

    # три концентричні смуги по висоті: операційна (зелена) ⊂ запас ⊂ absmax (червона)
    def band(y0, y1, fill, stroke, label, sub, col):
        p.append(rect(cx - 230, y0, 460, y1 - y0, fill=fill, stroke=stroke, sw=2, rx=8))
        p.append(text(cx, y0 + 22, label, size=13, bold=True, color=col))
        p.append(text(cx, y0 + 40, sub, size=10, color=MUTED, italic=True))

    band(top + 0,   top + 300, "#fdecea", POS, "Absolute Maximum Ratings", "за цим — миттєва або накопичена смерть", POS)
    band(top + 60,  top + 240, "#fff7e6", "#d68910", "заборонена смуга", "живе, але поза специфікацією — без гарантій", "#d68910")
    band(top + 120, top + 180, "#eafaf1", FIELD, "Recommended Operating", "тут працює як у даташиті", FIELD)

    # робоча точка ТЗ — у зеленій зоні, ліворуч від підпису смуги, з запасом
    py = top + 150
    px = cx - 150
    p.append(circle(px, py, 7, fill=FIELD, stroke=INK, sw=2))
    p.append(text(px, py + 22, "точка ТЗ", size=10.5, bold=True, color=FIELD))

    # стрілка-запас від робочої точки вгору до краю absmax
    p.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="1.8" '
             'marker-end="url(#arrow)"/>' % (px, py - 8, px, top + 8, POS))
    p.append(text(px - 8, (py + top + 8) / 2, "запас", size=10, color=POS, anchor="end", italic=True))

    p.append(text(W / 2, H - 16,
                  "ТЗ цілиться в зелену зону із запасом до червоної межі — не в саму межу",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "absmax-vs-operating.svg"), W, H, *p,
           title="Гранично-допустиме проти рекомендованого робочого")


# ── spec-to-design: кожен рядок ТЗ обирає реальну деталь ───────────────────────
# Ідея: ТЗ — не папір, а керівні числа. Показуємо стрілки «рядок ТЗ → що він
# вибирає в схемі». Vвх-min → вибір топології; Iпік+просідання → вхідний конд.;
# допуск+пульсація → котушка/вихідний конд.; темп.+потужність → корпус і мідь.
def fig_to_design():
    W, H = 770, 420
    p = []
    lx = 80
    rx = 470
    rows = [
        ("Vвх min · напрямок",     "→ клас топології (buck / boost / …)", NEG, "#eaf0fd"),
        ("Iпік · просідання входу", "→ вхідний конденсатор і його ESR", POS, "#fdecea"),
        ("допуск · пульсація",      "→ котушка й вихідний конденсатор", FIELD, "#eafaf1"),
        ("стрибок струму (transient)", "→ петля ЗЗ і вихідна ємність", "#d68910", "#fff7e6"),
        ("потужність · темп. серед.", "→ корпус, мідь, тепловідведення", MUTED, "#f3f4f6"),
    ]
    y = 80
    dy = 62
    for left_lab, right_lab, col, fill in rows:
        b, lw, lh = textbox(lx + 130, y, left_lab, size=11.5, bold=True, color=col, fill=fill, stroke=col, sw=1.8, pad=9)
        p.append(b)
        b2, rw, rh = textbox(rx + 150, y, right_lab, size=11.5, bold=True, color=INK, fill="#f7f8fa", stroke=INK, sw=1.6, pad=9)
        p.append(b2)
        p.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" '
                 'stroke-width="2.0" marker-end="url(#arrow)"/>'
                 % (lx + 130 + lw / 2 + 4, y, rx + 150 - rw / 2 - 8, y, col))
        y += dy

    p.append(text(W / 2, H - 16,
                  "жоден рядок ТЗ не «папір» — кожен прямо призначає номінал чи деталь у схемі",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "spec-to-design.svg"), W, H, *p,
           title="Кожен рядок ТЗ обирає реальну деталь")


# ── rating-systems: одне число «300 В» означає РІЗНЕ в двох системах ────────────
# Ідея вставки 📜: до окремої absMax-таблиці існували дві несумісні «системи
# максимумів». design-center: у число вже втоплено запас на ±10 % мережі —
# конструктор ставить його як є. absolute: число — гола фізична стеля, запас
# накручує сам інженер. Малюємо спільну вісь напруги, фізичну стелю деталі
# згори (червона) і дві колонки-тлумачення того самого довідкового «300 В».
def fig_rating_systems():
    W, H = 760, 470
    p = []
    axis_top = 95
    axis_bot = 360

    # фізична стеля деталі — спільна для обох систем, угорі
    ceil_y = axis_top + 18
    p.append(line(70, ceil_y, W - 40, ceil_y, color=POS, sw=2.4, dash="7 4"))
    p.append(text(W - 44, ceil_y - 9, "фізична стеля деталі (тут вона гине)",
                  size=10.5, color=POS, anchor="end", italic=True))

    def column(cx, head, headcol, headfill, num_y, num_label, op_y,
               margin_owner, margin_col, sub):
        # рамка-заголовок системи
        b, w, h = textbox(cx, axis_top - 42, head, size=12.5, bold=True,
                          color=headcol, fill=headfill, stroke=headcol, sw=2, pad=9)
        p.append(b)
        # вертикальна вісь колонки
        p.append(line(cx, ceil_y, cx, axis_bot, color=INK, sw=1.6))
        # довідкове число «300 В» — позначка-риска на осі
        p.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" '
                 'stroke-width="2.6"/>' % (cx - 26, num_y, cx + 26, num_y, INK))
        same = abs(num_y - op_y) < 4  # робоча точка збігається з довідковим числом?
        if same:
            # design-center: число Й Є робочою точкою — один зелений маркер, ясний підпис
            p.append(circle(cx, num_y, 6, fill=FIELD, stroke=INK, sw=2))
            p.append(text(cx + 34, num_y + 4, num_label + " = робоча", size=11,
                          bold=True, color=INK, anchor="start"))
        else:
            # absolute: число (стеля) і робоча точка — РІЗНІ, розводимо по осі
            p.append(circle(cx, num_y, 5, fill=BG, stroke=INK, sw=2))
            p.append(text(cx + 34, num_y + 4, num_label, size=11, bold=True,
                          color=INK, anchor="start"))
            p.append(circle(cx, op_y, 6, fill=FIELD, stroke=INK, sw=2))
            p.append(text(cx - 34, op_y + 4, "робоча\nточка", size=9.5,
                          color=FIELD, anchor="end"))
        # де лежить запас на реальний світ:
        # design-center — між довідковим числом і стелею (втоплено в число);
        # absolute      — між стелею й робочою точкою (накручує сам інженер).
        if margin_owner == "design":
            m_a, m_b = ceil_y, num_y
        else:
            m_a, m_b = num_y, op_y  # num_y == рівень стелі
        p.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" '
                 'stroke-width="1.8" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
                 % (cx + 64, m_a, cx + 64, m_b, margin_col))
        p.append(text(cx + 70, (m_a + m_b) / 2 - 6, "запас", size=10,
                      color=margin_col, anchor="start", italic=True))
        p.append(text(cx + 70, (m_a + m_b) / 2 + 9, margin_owner == "design"
                      and "у числі" or "рахує інженер", size=9,
                      color=margin_col, anchor="start", italic=True))
        # підпис під колонкою
        p.append(text(cx, axis_bot + 24, sub.split("\n")[0], size=9.5, color=MUTED))
        for i, ln in enumerate(sub.split("\n")[1:], start=1):
            p.append(text(cx, axis_bot + 24 + i * 13, ln, size=9.5, color=MUTED))

    # DESIGN-CENTER: число сидить НИЖЧЕ стелі (запас уже втоплено), робоча = число
    column(230, "design-center\n(пізніша система)", FIELD, "#eafaf1",
           num_y=axis_top + 150, num_label="«300 В»",
           op_y=axis_top + 150,           # робоча точка = довідкове число (як є)
           margin_owner="design", margin_col=FIELD,
           sub="число = робоче;\nзапас на ±10 % мережі\nвже всередині — став як є")

    # ABSOLUTE: число = сама стеля; інженер сам відступає вниз
    column(540, "absolute\n(найдавніша система)", POS, "#fdecea",
           num_y=ceil_y,                  # довідкове число = фізична стеля
           num_label="«300 В»",
           op_y=axis_top + 175,           # робоча точка — далеко нижче, накручена вручну
           margin_owner="absolute", margin_col=POS,
           sub="число = гола стеля;\nвесь запас на мережу\nконструктор накручує сам")

    p.append(text(W / 2, H - 16,
                  "те саме довідкове «300 В» — у двох системах фізично різний дозвіл; звідси й дві колонки даташита",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "rating-systems.svg"), W, H, *p,
           title="Дві ранні системи максимумів: одне число — різний дозвіл")


if __name__ == "__main__":
    fig_spine()
    fig_window()
    fig_absmax()
    fig_to_design()
    fig_rating_systems()
    print("OK: figures written to", OUT)
