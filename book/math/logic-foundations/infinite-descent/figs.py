# -*- coding: utf-8 -*-
"""Фігури до статті «Нескінченний спуск Ферма».
Запуск:  python figs.py   → пише SVG у ./img/
  descent-machine, floor-vs-no-floor, sqrt2-chain, three-faces
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#eaf7ef"
REDFILL = "#fdecea"
BLUEFILL = "#eaf0fd"
ROW = "#f4f6f8"


# ── 1. Машина спуску: крок, петля, дно ───────────────────────────────────────
def fig_descent_machine():
    W, H = 980, 500
    f = [text(W / 2, 30, "Машина, що з'їдає власний розв'язок", size=18, bold=True),
         text(W / 2, 52, "крок робить менший розв'язок · його знову подають на вхід · міри спадають до дна",
              size=12, color=MUTED, italic=True)]

    # ── машина ──
    mx, my, mw, mh = 400, 120, 200, 78
    f.append(rect(mx, my, mw, mh, fill=ROW, stroke=INK, sw=2.0, rx=12))
    f.append(text(mx + mw / 2, my + 32, "КРОК", size=16, bold=True))
    f.append(text(mx + mw / 2, my + 56, "розв'язок → менший", size=12.5, color=INK))

    midy = my + mh / 2
    # вхід
    f.append(arrow(190, midy, mx - 6, midy, color=FIELD, sw=2.4))
    f.append(text(115, midy - 12, "розв'язок", size=12.5, bold=True, color=FIELD))
    f.append(text(115, midy + 8, "міра n", size=12, color=FIELD, italic=True))
    # вихід
    f.append(arrow(mx + mw + 6, midy, 800, midy, color=POS, sw=2.4))
    f.append(text(872, midy - 12, "розв'язок", size=12.5, bold=True, color=POS))
    f.append(text(872, midy + 8, "міра < n", size=12, color=POS, italic=True))

    # петля: вихід повертають на вхід — дуга ЗВЕРХУ
    f.append(('<path d="M 790 %d Q %d 34 190 %d" fill="none" stroke="%s" '
              'stroke-width="2.2" stroke-dasharray="7,4" marker-end="url(#arrow)"/>'
              % (my - 4, W / 2, my - 4, NEG)))
    f.append(text(W / 2, 74, "той самий вихід — знову на вхід, і так без кінця",
                  size=12.5, bold=True, color=NEG))

    # ── дно: спадні стовпчики мір ──
    fy = 430                       # рівень дна
    xs = [180, 330, 470, 590, 685]
    hs = [176, 134, 100, 72, 50]
    labs = ["n₁", "n₂", "n₃", "n₄", "n₅"]
    bw = 50
    for x, h, lab in zip(xs, hs, labs):
        f.append(rect(x - bw / 2, fy - h, bw, h, fill=GREENFILL, stroke=FIELD, sw=1.6, rx=5))
        f.append(text(x, fy - h - 10, lab, size=12.5, bold=True, color=FIELD))
    # знаки «>» між вершинами
    for i in range(len(xs) - 1):
        xm = (xs[i] + xs[i + 1]) / 2
        f.append(text(xm, fy - (hs[i] + hs[i + 1]) / 2 + 5, ">", size=15, bold=True, color=MUTED))
    f.append(text(745, fy - 18, "…", size=22, bold=True, color=MUTED))

    # лінія дна
    f.append(line(120, fy, 860, fy, color=INK, sw=2.2))
    f.append(text(490, fy + 22, "дно натуральних чисел — нижче за 1 сходинок немає",
                  size=12.5, bold=True, color=INK))

    # червона виноска: суперечність
    f.append(fitbox(700, fy - 118, 250, 74,
                    "Машина обіцяє ще менший —\nа під дном його вже нема.\nОтже входу не було зовсім.",
                    size=12.5, fill=REDFILL, stroke=POS, sw=1.6, color=INK))
    f.append(('<path d="M 748 %d Q 720 %d 690 %d" fill="none" stroke="%s" '
              'stroke-width="2" marker-end="url(#arrow)"/>' % (fy - 44, fy - 30, fy - 6, POS)))
    render(os.path.join(IMG, "descent-machine.svg"), W, H, *f)


# ── 2. Є дно чи нема: ℕ проти додатних дробів ────────────────────────────────
def fig_floor_vs_no_floor():
    W, H = 980, 470
    f = [text(W / 2, 30, "Уся сила — у дні: те саме падіння, дві різні множини", size=18, bold=True),
         text(W / 2, 52, "у натуральних спуск приречений спинитися · у дробах — триває вічно",
              size=12, color=MUTED, italic=True)]

    top, bot = 96, 392          # рівні високого й низького значення

    # ── лівий: ℕ, є дно ──
    LX = 245
    f.append(rect(40, 78, 430, 366, fill="#fbfcfd", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(245, 104, "ℕ — під падінням є дно", size=14.5, bold=True, color=FIELD))
    f.append(line(LX, top + 24, LX, bot, color=INK, sw=1.6))          # вертикальна вісь
    Nvals = [("5", top + 24), ("4", top + 78), ("3", top + 132), ("2", top + 186), ("1", top + 240)]
    prev = None
    for lab, y in Nvals:
        f.append(circle(LX, y, 8, fill=GREENFILL, stroke=FIELD, sw=2.2))
        f.append(text(LX - 26, y + 5, lab, size=13.5, bold=True, color=INK))
        if prev is not None:
            f.append(arrow(LX + 22, prev + 6, LX + 22, y - 6, color=MUTED, sw=1.8))
        prev = y
    floor_y = top + 240 + 30
    f.append(rect(LX - 70, floor_y, 140, 16, fill=INK, stroke=INK, sw=1, rx=3))
    f.append(text(LX, floor_y + 40, "далі нема куди", size=12.5, bold=True, color=INK))
    f.append(text(245, 430, "щонайбільше n кроків — і кінець", size=12.5, italic=True, color=FIELD))

    # ── правий: дроби, дна нема ──
    RX = 735
    f.append(rect(510, 78, 430, 366, fill="#fbfcfd", stroke=POS, sw=1.6, rx=10))
    f.append(text(735, 104, "додатні дроби — дна нема", size=14.5, bold=True, color=POS))
    f.append(line(RX, top + 24, RX, bot, color=INK, sw=1.6))
    # значення 1, 1/2, 1/4, 1/8, 1/16 — тиснуться до 0, кроки коротшають
    Fvals = [("1", top + 24), ("1/2", top + 132), ("1/4", top + 186),
             ("1/8", top + 213), ("1/16", top + 227)]
    prev = None
    for lab, y in Fvals:
        f.append(circle(RX, y, 7, fill=REDFILL, stroke=POS, sw=2.0))
        f.append(text(RX - 34, y + 5, lab, size=12.5, bold=True, color=INK))
        if prev is not None:
            f.append(arrow(RX + 20, prev + 5, RX + 20, y - 5, color=MUTED, sw=1.6))
        prev = y
    # пунктирний 0-рівень, якого не досягти
    zero_y = bot
    f.append(line(RX - 80, zero_y, RX + 80, zero_y, color=POS, sw=1.6, dash="6,4"))
    f.append(text(RX, zero_y + 20, "0 — недосяжне", size=12.5, bold=True, color=POS))
    f.append(text(RX + 24, top + 250, "…", size=20, bold=True, color=MUTED))
    f.append(text(735, 430, "спуск не обірветься ніколи", size=12.5, italic=True, color=POS))

    render(os.path.join(IMG, "floor-vs-no-floor.svg"), W, H, *f)


# ── 3. Спуск на рівнянні a²=2b² (√2 не дріб) ─────────────────────────────────
def fig_sqrt2_chain():
    W, H = 960, 430
    f = [text(W / 2, 30, "Один крок спуску для √2: з (a, b) виходить менша (b, c)", size=18, bold=True),
         text(W / 2, 52, "та сама рівність a² = 2b² відроджується як b² = 2c² — тільки з меншим числом",
              size=12, color=MUTED, italic=True)]

    ty = 150
    # ── ліва пара ──
    f.append(rect(60, ty - 40, 190, 96, fill=GREENFILL, stroke=FIELD, sw=1.8, rx=10))
    f.append(text(155, ty - 6, "( a , b )", size=20, bold=True, color=INK))
    f.append(text(155, ty + 30, "a² = 2 b²", size=15, bold=True, color=FIELD))

    # ── середина: алгебра кроку ──
    px, pw = 330, 300
    f.append(rect(px, ty - 66, pw, 156, fill="#fbfcfd", stroke=MUTED, sw=1.5, rx=10))
    f.append(text(px + pw / 2, ty - 44, "крок", size=13, bold=True, color=MUTED))
    moves = ["a²  парне  ⇒  a  парне",
             "a = 2c",
             "4c² = 2b²",
             "b² = 2c²"]
    for i, mv in enumerate(moves):
        yy = ty - 20 + i * 28
        f.append(text(px + pw / 2, yy, mv, size=14, bold=(i == 3), color=(FIELD if i == 3 else INK)))

    # ── права пара ──
    rx = 700
    f.append(rect(rx, ty - 40, 190, 96, fill=GREENFILL, stroke=FIELD, sw=1.8, rx=10))
    f.append(text(rx + 95, ty - 6, "( b , c )", size=20, bold=True, color=INK))
    f.append(text(rx + 95, ty + 30, "b² = 2 c²", size=15, bold=True, color=FIELD))

    # стрілки між блоками
    f.append(arrow(252, ty + 4, px - 6, ty + 4, color=INK, sw=2.2))
    f.append(arrow(px + pw + 6, ty + 4, rx - 6, ty + 4, color=INK, sw=2.2))

    # позначка «менша»
    f.append(('<path d="M 800 %d Q 500 %d 155 %d" fill="none" stroke="%s" '
              'stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrow)"/>'
              % (ty + 70, ty + 128, ty + 70, POS)))
    f.append(text(W / 2, ty + 120, "b < a  (бо a² = 2b² > b²) — перший компонент строго меншає",
                  size=12.5, bold=True, color=POS))

    # нижня смуга: висновок
    f.append(fitbox(60, 350, 840, 58,
                    "Повторюй крок:  a > b > c > d > …  —  нескінченний спадний ланцюг у ℕ, а такого не буває.\n"
                    "Отже пари (a, b) з рівністю a² = 2b² не існує зовсім: √2 не записати дробом.",
                    size=13, fill=ROW, stroke=MUTED, sw=1.4, color=INK))
    render(os.path.join(IMG, "sqrt2-chain.svg"), W, H, *f)


# ── 4. Три одежі однієї властивості ℕ ────────────────────────────────────────
def fig_three_faces():
    W, H = 1000, 450
    f = [text(W / 2, 30, "Індукція, найменший елемент і спуск — одна властивість ℕ", size=18, bold=True),
         text(W / 2, 52, "«немає нескінченного спуску вниз» — три способи нею скористатися, кожен виводиться з кожного",
              size=12, color=MUTED, italic=True)]

    PY, PH, PW = 80, 250, 300
    cols = [
        (30, "ІНДУКЦІЯ", FIELD, GREENFILL, "від бази вгору", "накриває всі числа — довести, що властивість Є"),
        (350, "НАЙМЕНШИЙ ЕЛЕМЕНТ", NEG, BLUEFILL, "вказати крайнє", "у будь-якому наборі є найменший — вхопитися за край"),
        (670, "СПУСК", POS, REDFILL, "вниз, у дно", "розбивається об 1 — довести, що розв'язку НЕМА"),
    ]
    for px, title, col, bg, tag, desc in cols:
        f.append(rect(px, PY, PW, PH, fill="#fbfcfd", stroke=col, sw=1.7, rx=10))
        f.append(rect(px, PY, PW, 34, fill=bg, stroke=col, sw=1.5, rx=10))
        f.append(text(px + PW / 2, PY + 22, title, size=13.5, bold=True, color=col))

        cx = px + PW / 2
        axis_top, axis_bot = PY + 60, PY + 190
        dots_y = [axis_bot - i * 30 for i in range(5)]   # 1 внизу … 5 вгорі

        if title == "ІНДУКЦІЯ":
            f.append(line(cx, axis_top, cx, axis_bot, color=INK, sw=1.5))
            for i, y in enumerate(dots_y):
                f.append(circle(cx, y, 7, fill=bg, stroke=col, sw=2.0))
            f.append(arrow(cx, axis_bot + 4, cx, axis_top - 4, color=col, sw=2.4))  # вгору
            f.append(text(cx + 24, axis_bot + 4, "база", size=12, bold=True, color=col, anchor="start"))
        elif title == "НАЙМЕНШИЙ ЕЛЕМЕНТ":
            # розкидані точки, найменша — виділена внизу
            pts = [(cx - 40, axis_top + 10), (cx + 30, axis_top + 30), (cx - 10, axis_top + 64),
                   (cx + 46, axis_top + 90), (cx, axis_bot)]
            for i, (x, y) in enumerate(pts):
                least = (i == len(pts) - 1)
                f.append(circle(x, y, 8 if least else 6, fill=(bg if least else BG),
                                stroke=col, sw=(2.4 if least else 1.5)))
            f.append(text(cx, axis_bot + 22, "найменший", size=12, bold=True, color=col))
        else:  # СПУСК
            f.append(line(cx, axis_top, cx, axis_bot, color=INK, sw=1.5))
            for i, y in enumerate(dots_y):
                f.append(circle(cx, y, 7, fill=bg, stroke=col, sw=2.0))
            f.append(arrow(cx, axis_top + 4, cx, axis_bot - 4, color=col, sw=2.4))   # вниз
            f.append(rect(cx - 40, axis_bot + 12, 80, 12, fill=INK, stroke=INK, sw=1, rx=3))
            f.append(text(cx, axis_bot + 40, "дно", size=12, bold=True, color=col))

        f.append(text(px + PW / 2, PY + 218, tag, size=12.5, bold=True, color=col))

    # нижня смуга
    f.append(fitbox(30, 350, 940, 66,
                    "Довели одне — безкоштовно маєте всі три. Тому не питають, що «сильніше»: вибір — питання зручності.\n"
                    "Доводите наявність — беріть індукцію; доводите неможливість — беріть спуск; зручно за край — найменший елемент.",
                    size=12.5, fill=ROW, stroke=MUTED, sw=1.4, color=INK))
    render(os.path.join(IMG, "three-faces.svg"), W, H, *f)


# ── 5. Родовід методу: від Евкліда до Ейлера (для вставки hist) ───────────────
def fig_descent_lineage():
    W, H = 900, 580
    f = [text(W / 2, 32, "Чий спуск: одне поняття крізь дві тисячі років", size=18, bold=True),
         text(W / 2, 54, "Евклід ним рахує · Ферма дає ім'я і заявки · Ейлер доводить обіцяне",
              size=12, color=MUTED, italic=True)]

    sx = 214                              # вертикальна вісь часу
    f.append(line(sx, 96, sx, 520, color="#cbd2da", sw=3.2))
    f.append(text(sx, 548, "час ↓", size=12, bold=True, color=MUTED))

    rows = [
        ("~300 до н.е.", MUTED, 8, "Евклід, «Начала», книга VII, твердження 31",
         "спуском показує: кожне складене число має простий дільник — імені методу ще нема"),
        ("1659", FIELD, 8, "Лист до П'єра де Каркаві — «науковий заповіт»",
         "метод дістає назву descente infinie; заявлено п'ять теорем"),
        ("1665", INK, 8, "Ферма помирає в Кастрі",
         "майже всі його доведення лишилися усною обіцянкою, без рядка викладу"),
        ("1670", POS, 11, "Син друкує «Арифметику» Діофанта з нотатками батька",
         "уціліле єдине повне доведення — площа трикутника не квадрат (Observatio XLV)"),
        ("1749", NEG, 8, "Ейлер доводить теорему про суму двох квадратів",
         "тим самим спуском; заявку Ферма вперше замкнено на папері"),
        ("1770", NEG, 8, "Ейлер закриває показник куба, n = 3",
         "метод реконструйовано з уламків і повернуто в живу науку"),
    ]
    ys = [125, 204, 283, 362, 441, 505]
    for (year, col, r, head, sub), y in zip(rows, ys):
        f.append(text(sx - 30, y + 5, year, size=13.5, bold=True, color=col, anchor="end"))
        fillc = {MUTED: ROW, FIELD: GREENFILL, INK: ROW, POS: REDFILL, NEG: BLUEFILL}[col]
        f.append(circle(sx, y, r, fill=fillc, stroke=col, sw=2.4))
        f.append(text(sx + 30, y - 4, head, size=13.5, bold=True, color=INK, anchor="start"))
        f.append(text(sx + 30, y + 16, sub, size=12, color=MUTED, anchor="start"))

    f.append(text(W / 2, 566, "ідея — Евклідова · ім'я — Ферма · доведення — спільні",
                  size=12.5, bold=True, italic=True, color=INK))
    render(os.path.join(IMG, "descent-lineage.svg"), W, H, *f)


# ── 6. Крок спуску для трикутника (для вставки math-right-triangle-area) ──────
def _rtri(x, y, w, h, fill, stroke, sw=2.0):
    """Прямокутний трикутник, прямий кут ліворуч унизу (просто іконка)."""
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" '
            'stroke="%s" stroke-width="%.1f"/>' % (x, y + h, x + w, y + h, x, y, fill, stroke, sw))


def fig_triangle_descent_step():
    W, H = 1060, 560
    f = [text(W / 2, 32, "Крок спуску: із квадратної площі народжується менший трикутник", size=18, bold=True),
         text(W / 2, 54, "чотири взаємно прості множники площі мусять бути квадратами — з них і складається новий трикутник",
              size=12, color=MUTED, italic=True)]

    # іконки-трикутники над крайніми блоками: великий ліворуч, малий праворуч
    f.append(_rtri(70, 92, 96, 62, GREENFILL, FIELD))
    f.append(text(118, 172, "трикутник із площею-□", size=11.5, color=MUTED))
    f.append(_rtri(922, 108, 58, 40, GREENFILL, FIELD))
    f.append(text(951, 172, "менший — теж площа-□", size=11.5, color=MUTED))

    # три стадії
    by, bh = 196, 176
    s1x, s2x, s3x, bw = 40, 388, 736, 284
    f.append(fitbox(s1x, by, bw, bh,
                    "1 · ПЛОЩА — КВАДРАТ\n\nпримітивний трикутник\n(m²−n², 2mn, m²+n²)\n\nплоща = mn(m−n)(m+n) = □",
                    size=14, fill="#fbfcfd", stroke=FIELD, sw=1.7, color=INK, bold=False))
    f.append(fitbox(s2x, by, bw, bh,
                    "2 · ЧОТИРИ КВАДРАТИ\n\nm, n, m−n, m+n —\nпопарно взаємно прості,\nа добуток їхній — квадрат\n\n⇒  m=p², n=q², m+n=r², m−n=s²",
                    size=14, fill="#fbfcfd", stroke=NEG, sw=1.7, color=INK))
    f.append(fitbox(s3x, by, bw, bh,
                    "3 · МЕНШИЙ ТРИКУТНИК\n\nкатети (r+s)/2 та (r−s)/2,\nгіпотенуза p\n\nU² + V² = m = p²\nплоща = n/4 = (q/2)² = □",
                    size=14, fill="#fbfcfd", stroke=POS, sw=1.7, color=INK))
    # стрілки між стадіями
    f.append(arrow(s1x + bw + 4, by + bh / 2, s2x - 4, by + bh / 2, color=INK, sw=2.4))
    f.append(arrow(s2x + bw + 4, by + bh / 2, s3x - 4, by + bh / 2, color=INK, sw=2.4))

    # нижня смуга: спад гіпотенузи
    f.append(fitbox(40, 420, 980, 58,
                    "Гіпотенуза впала:  p = √m  <  m² + n² = c.  Новий трикутник знову має площу-квадрат — годуй його тим самим кроком.\n"
                    "Гіпотенузи дають спадний ланцюг натуральних чисел c₁ > c₂ > c₃ > … — а такого не буває. Отже жодного трикутника з площею-квадратом нема.",
                    size=13, fill=ROW, stroke=MUTED, sw=1.4, color=INK, bold=False))
    render(os.path.join(IMG, "triangle-descent-step.svg"), W, H, *f)


# ── 7. Наслідок: x⁴−y⁴=z² і показник 4 (для тієї ж вставки) ───────────────────
def fig_quartic_corollary():
    W, H = 1020, 520
    f = [text(W / 2, 32, "Від трикутника — до великої теореми Ферма для четвертого степеня", size=18, bold=True),
         text(W / 2, 54, "розв'язок x⁴−y⁴=z² збудував би трикутник із площею-квадратом, якого не буває",
              size=12, color=MUTED, italic=True)]

    by, bh = 92, 190
    s1x, s2x, s3x, bw = 40, 372, 704, 276
    f.append(fitbox(s1x, by, bw, bh,
                    "ПРИПУСТИМО РОЗВ'ЯЗОК\n\nx⁴ − y⁴ = z²\nу ненульових цілих\n(x > y ≥ 1,  z ≥ 1)",
                    size=14.5, fill="#fbfcfd", stroke=NEG, sw=1.7, color=INK))
    f.append(fitbox(s2x, by, bw, bh,
                    "ЗБУДУЙ ТРИКУТНИК\n\nкатети  x⁴−y⁴  та  2x²y²,\nгіпотенуза  x⁴+y⁴\n\nплоща = (x⁴−y⁴)·x²y²\n= z²·x²y² = (xyz)² = □",
                    size=14, fill="#fbfcfd", stroke=FIELD, sw=1.7, color=INK))
    f.append(fitbox(s3x, by, bw, bh,
                    "СУПЕРЕЧНІСТЬ\n\nале піфагорів трикутник\nніколи не має площі-□\n\n⇒  x⁴ − y⁴ = z²\nрозв'язків не має",
                    size=14, fill="#fbfcfd", stroke=POS, sw=1.7, color=INK))
    f.append(arrow(s1x + bw + 4, by + bh / 2, s2x - 4, by + bh / 2, color=INK, sw=2.4))
    f.append(arrow(s2x + bw + 4, by + bh / 2, s3x - 4, by + bh / 2, color=INK, sw=2.4))

    # нижня смуга: перехід до FLT n=4
    f.append(fitbox(40, 322, 940, 92,
                    "Показник 4 задарма.  Нехай x⁴ + y⁴ = z⁴.  Перенесемо:  z⁴ − y⁴ = x⁴ = (x²)².\n"
                    "Тоді трійка (z, y, x²) розв'язує заборонене a⁴ − b⁴ = c² — а воно розв'язків не має.\n"
                    "Отже x⁴ + y⁴ = z⁴ неможливе в ненульових цілих: велика теорема Ферма для n = 4 доведена.",
                    size=13.5, fill=GREENFILL, stroke=FIELD, sw=1.6, color=INK, bold=False))
    f.append(text(W / 2, 452, "той самий спуск, що заборонив квадратну площу, закриває й показник чотири",
                  size=12.5, italic=True, bold=True, color=INK))
    render(os.path.join(IMG, "quartic-corollary.svg"), W, H, *f)


# ── 8. Дешевий фільтр mod 4 (для вставки math-two-squares-descent) ────────────
def fig_mod4_filter():
    W, H = 1000, 470
    f = [text(W / 2, 32, "Дешевий фільтр за модулем 4: 4n+3 відпадає, вага лягає на 4n+1", size=18, bold=True),
         text(W / 2, 54, "квадрат дає остачу лише 0 або 1 — тож сума двох квадратів ніколи не буває ≡ 3 (mod 4)",
              size=12, color=MUTED, italic=True)]

    # ── ліва панель: таблиця сум остач ──
    px, py, pw, ph = 60, 88, 380, 336
    f.append(rect(px, py, pw, ph, fill="#fbfcfd", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(px + pw / 2, py + 28, "остача суми  a² + b²  (mod 4)", size=14, bold=True, color=FIELD))

    gx, gy, cell = px + 150, py + 74, 84            # сітка 2×2 з запасом на підписи
    f.append(text(gx + cell * 0.5, gy - 16, "b² ≡ 0", size=12.5, bold=True, color=MUTED))
    f.append(text(gx + cell * 1.5, gy - 16, "b² ≡ 1", size=12.5, bold=True, color=MUTED))
    f.append(text(gx - 48, gy + cell * 0.5 + 5, "a² ≡ 0", size=12.5, bold=True, color=MUTED))
    f.append(text(gx - 48, gy + cell * 1.5 + 5, "a² ≡ 1", size=12.5, bold=True, color=MUTED))
    sums = [[0, 1], [1, 2]]
    for r in range(2):
        for c in range(2):
            cx, cy = gx + c * cell, gy + r * cell
            f.append(rect(cx, cy, cell, cell, fill=GREENFILL, stroke=FIELD, sw=1.5, rx=8))
            f.append(text(cx + cell / 2, cy + cell / 2 + 9, str(sums[r][c]), size=26, bold=True, color=INK))
    f.append(text(px + pw / 2, py + ph - 46, "серед остач — 0, 1, 2.  Трійки немає ніде.", size=13, bold=True, color=INK))
    f.append(text(px + pw / 2, py + ph - 22, "отже число ≡ 3 (mod 4) — не сума двох квадратів",
                  size=12.5, italic=True, color=POS))

    # ── права панель: прості надвоє ──
    qx, qy, qw, qh = 560, 88, 380, 336
    f.append(rect(qx, qy, qw, qh, fill="#fbfcfd", stroke=MUTED, sw=1.6, rx=10))
    f.append(text(qx + qw / 2, py + 28, "непарні прості за остачею (mod 4)", size=14, bold=True, color=INK))
    f.append(fitbox(qx + 24, qy + 52, qw - 48, 82,
                    "4n+3:  3, 7, 11, 19, 23, 31, …\nостача 3 — не сума двох квадратів,\nвідпадають задарма, без спуску",
                    size=12.5, fill=REDFILL, stroke=POS, sw=1.5, color=INK))
    f.append(fitbox(qx + 24, qy + 148, qw - 48, 82,
                    "4n+1:  5, 13, 17, 29, 37, 41, …\nостача 1 — фільтр не вирішує,\nсаме тут потрібен спуск",
                    size=12.5, fill=GREENFILL, stroke=FIELD, sw=1.5, color=INK))
    f.append(fitbox(qx + 24, qy + 244, qw - 48, 56,
                    "2 = 1² + 1²  —  єдине парне просте,\nрозкладається одразу",
                    size=12.5, fill=ROW, stroke=MUTED, sw=1.4, color=INK))
    render(os.path.join(IMG, "mod4-filter.svg"), W, H, *f)


# ── 9. Спуск на поганому простому 4n+1 до дна = 5 (для вставки math-two-squares) ─
def fig_bad_prime_descent():
    W, H = 1020, 500
    f = [text(W / 2, 32, "Спуск на ствердному: погане 4n+1 родить менше погане 4n+1", size=18, bold=True),
         text(W / 2, 54, "припустили, що якесь просте 4n+1 — не сума двох квадратів; крок робить менше таке саме — і розбивається об п'ятірку",
              size=11.5, color=MUTED, italic=True)]

    # ── ліворуч: спадні погані прості до дна ──
    LX, bw, bh = 250, 240, 50
    for lab, y in [("p₁", 112), ("p₂", 192), ("p₃", 272)]:
        f.append(fitbox(LX - bw / 2, y - bh / 2, bw, bh, lab + " — погане 4n+1",
                        size=14, fill=REDFILL, stroke=POS, sw=1.8, color=INK, bold=True))
    for y0, y1 in [(137, 165), (217, 245)]:
        f.append(arrow(LX, y0, LX, y1, color=POS, sw=2.2))
    f.append(arrow(LX, 297, LX, 322, color=POS, sw=2.2))
    f.append(text(LX, 340, "…", size=26, bold=True, color=MUTED))

    fy = 424                                    # рівень дна
    f.append(arrow(LX, 352, LX, fy - 58, color=POS, sw=2.2))
    f.append(fitbox(LX - 160, fy - 56, 320, 46,
                    "5 = 1² + 2²  —  найменше просте 4n+1,  і воно НЕ погане",
                    size=12.5, fill=GREENFILL, stroke=FIELD, sw=1.8, color=INK, bold=True))
    f.append(rect(LX - 160, fy, 320, 15, fill=INK, stroke=INK, sw=1, rx=3))
    f.append(text(LX, fy + 36, "приземлятися нема на що — поганого простого немає",
                  size=12.5, bold=True, color=INK))

    # ── праворуч: один крок машини ──
    RX0, RW = 560, 430
    f.append(rect(RX0, 96, RW, 352, fill="#fbfcfd", stroke=MUTED, sw=1.6, rx=10))
    f.append(text(RX0 + RW / 2, 122, "один крок: з поганого p — менше погане q", size=13.5, bold=True, color=INK))
    steps = [
        ("іскра", FIELD, "−1 — квадрат (mod p)  ⇒  p ділить a² + 1 = p·m\nсума двох ВЗАЄМНО ПРОСТИХ квадратів,  1 ≤ m < p"),
        ("жорна", NEG, "якби всі прості дільники m були сумами двох\nквадратів — тотожність зробила б і p таким.\nОтже серед них є погане q"),
        ("фільтр", POS, "q ділить a²+1 (взаємно прості) ⇒ q ≠ 4n+3;\nа q ≤ m < p.  Значить, q — погане 4n+1,  менше за p"),
    ]
    yy = 150
    for tag, col, body in steps:
        f.append(rect(RX0 + 20, yy, 62, 68, fill=BG, stroke=col, sw=1.6, rx=8))
        f.append(text(RX0 + 51, yy + 39, tag, size=12.5, bold=True, color=col))
        f.append(fitbox(RX0 + 94, yy, RW - 114, 68, body, size=11.5,
                        fill="#fbfcfd", stroke=col, sw=1.2, color=INK))
        yy += 94
    render(os.path.join(IMG, "bad-prime-descent.svg"), W, H, *f)


if __name__ == "__main__":
    fig_descent_machine()
    fig_floor_vs_no_floor()
    fig_sqrt2_chain()
    fig_three_faces()
    fig_descent_lineage()
    fig_triangle_descent_step()
    fig_quartic_corollary()
    fig_mod4_filter()
    fig_bad_prime_descent()
    print("OK: 9 figures ->", IMG)
