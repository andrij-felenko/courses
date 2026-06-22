# -*- coding: utf-8 -*-
"""Фігури теми «Біполярний транзистор» (book/electronics/microelectronics/bjt).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def npn(cx, cy, label, color=INK):
    """Маленький символ NPN: вертикальна база-смужка, колектор угорі, емітер зі стрілкою вниз."""
    out = []
    bx = cx                       # вертикальна смужка бази
    out.append(line(bx, cy - 22, bx, cy + 22, color=color, sw=2.4))
    out.append(line(bx - 26, cy, bx, cy, color=color, sw=1.8))            # вивід бази
    out.append(line(bx, cy - 14, cx + 22, cy - 30, color=color, sw=1.8))  # до колектора
    out.append(line(cx + 22, cy - 30, cx + 22, cy - 44, color=color, sw=1.8))
    out.append(line(bx, cy + 14, cx + 22, cy + 30, color=color, sw=1.8))  # до емітера (стрілка)
    out.append(arrow(cx + 8, cy + 20, cx + 22, cy + 30, color=color, sw=1.8))
    out.append(line(cx + 22, cy + 30, cx + 22, cy + 44, color=color, sw=1.8))
    out.append(text(bx - 30, cy + 4, label, size=13, color=color, anchor="end", bold=True))
    return "".join(out), (cx + 22, cy - 44), (cx + 22, cy + 44)  # вузли колектора й емітера


# ════════════════════════════════════════════════════════════════════════════
#  ОГЛЯДОВА СТАТТЯ «Біполярний транзистор»
# ════════════════════════════════════════════════════════════════════════════

# ── 1. Чотири числа, що вирішують вибір транзистора ───────────────────────────
def fig_pick_params():
    W, H = 720, 470
    f = [text(W / 2, 30, "Що питають у транзистора перед тим, як його взяти",
              size=17, bold=True)]

    # центр — корпус транзистора з трьома виводами
    cx, cy = W / 2, 235
    # тіло (півколо TO-92): пласка грань ліворуч
    f.append('<path d="M%.0f %.0f A 52 52 0 0 1 %.0f %.0f L %.0f %.0f Z" '
             'fill="%s" stroke="%s" stroke-width="2"/>'
             % (cx, cy - 52, cx, cy + 52, cx - 18, cy + 52, FILL, LINE))
    f.append(line(cx - 18, cy - 52, cx - 18, cy + 52, color=LINE, sw=2))  # пласка грань
    f.append(text(cx + 14, cy + 5, "BJT", size=15, bold=True, color=MUTED))
    # три ніжки
    for dx, lab in ((-12, "E"), (0, "B"), (12, "C")):
        f.append(line(cx + dx, cy + 52, cx + dx, cy + 84, color=INK, sw=2))
        f.append(text(cx + dx, cy + 98, lab, size=12, color=MUTED, bold=True))

    # чотири картки-параметри довкола
    cards = [
        (60, 70, "#fdecea", POS, "U_CE (напруга)",
         "скільки вольтів витримає\nзакритий перехід C-E"),
        (430, 70, "#fff4e0", "#b9770e", "I_C (струм)",
         "який струм пропустить\nкрізь колектор"),
        (60, 320, "#eef7ef", FIELD, "β = h_FE (підсилення)",
         "у скільки разів колектор\nсильніший за базу"),
        (430, 320, "#eaf0fd", NEG, "f_T (частота)",
         "до якої частоти ще\nпідсилює — ВЧ чи звук"),
    ]
    anchors = {0: (cx - 18, cy - 30), 1: (cx + 30, cy - 30),
               2: (cx - 18, cy + 30), 3: (cx + 30, cy + 30)}
    for i, (x, y, fill, stroke, head, body) in enumerate(cards):
        f.append(rect(x, y, 230, 96, fill=fill, stroke=stroke, sw=1.8))
        f.append(text(x + 115, y + 26, head, size=14, bold=True, color=stroke))
        f.append(mtext(x + 115, y + 50, body, size=12, color=INK))
        ax, ay = anchors[i]
        sx = x + 230 if x < cx else x
        f.append(line(sx, y + 48, ax, ay, color=MUTED, sw=1.3, dash="4 3"))

    f.append(fitbox(cx - 150, 432, 300, 30,
                    "+ корпус: пробіг ніжок під твій монтаж",
                    size=12, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, "pick-params.svg"), W, H, *f)


# ── 2. Місце BJT серед транзисторів: кероване струмом vs полем ────────────────
def fig_current_vs_field():
    W, H = 720, 360
    f = [text(W / 2, 30, "Дві сім'ї транзисторів: чим керують потоком",
              size=17, bold=True)]

    # ── ліворуч: BJT — керує СТРУМ бази ──
    lx = 70
    f.append(text(lx + 120, 64, "Біполярний (BJT)", size=15, bold=True, anchor="middle", color=POS))
    q, c, e = npn(lx + 70, 150, "")
    f.append(q)
    # маленький струмок у базу
    f.append(arrow(lx + 4, 150, lx + 70 - 26, 150, color=FIELD, sw=2.4))
    f.append(text(lx + 30, 138, "Iб", size=13, color=FIELD, bold=True, anchor="middle"))
    f.append(fitbox(lx, 230, 240, 70,
                    "Кермо — СТРУМ бази.\nБаза весь час бере свій струмок\n(податок на рекомбінацію).",
                    size=12, fill="#fdecea", stroke=POS))

    # ── праворуч: MOSFET — керує НАПРУГА на затворі ──
    rx = 410
    f.append(text(rx + 120, 64, "Польовий (MOSFET)", size=15, bold=True, anchor="middle", color=NEG))
    gx, gy = rx + 70, 150
    f.append(line(gx, gy - 30, gx, gy + 30, color=INK, sw=2.4))       # канал
    f.append(line(gx - 18, gy - 24, gx - 18, gy + 24, color=INK, sw=2.4))  # затвор-пластина
    f.append(line(gx - 40, gy, gx - 18, gy, color=INK, sw=1.8))       # вивід затвора
    f.append(line(gx, gy - 30, gx + 24, gy - 30, color=INK, sw=1.8))  # стік
    f.append(line(gx, gy + 30, gx + 24, gy + 30, color=INK, sw=1.8))  # витік
    # «напруга» біля затвора — плюс без струму
    f.append(text(rx + 20, 138, "U_GS", size=13, color=NEG, bold=True, anchor="middle"))
    f.append(circle(rx + 30, 150, 3, fill=NEG, stroke=NEG))
    f.append(fitbox(rx, 230, 240, 70,
                    "Кермо — НАПРУГА на затворі.\nЗатвор ізольований: у статиці\nструму майже не бере.",
                    size=12, fill="#eaf0fd", stroke=NEG))

    # роздільна риса
    f.append(line(W / 2, 80, W / 2, 300, color=MUTED, sw=1, dash="3 4"))
    render(os.path.join(IMG, "current-vs-field.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА «Малопотужні NPN: 2N3904, BC547, 2N2222» (comp-small-signal-npn.md)
# ════════════════════════════════════════════════════════════════════════════

# ── 3. Три робочі конячки і їхні PNP-пари ────────────────────────────────────
def fig_workhorses():
    W, H = 720, 380
    f = [text(W / 2, 30, "Трійця малопотужних NPN та їхні дзеркальні PNP-пари",
              size=17, bold=True)]

    cols = [
        (130, "2N3904", "2N3906", FIELD, ["40 В · 200 мА", "загальна конячка", "копійчаний"]),
        (360, "BC547",  "BC557",  NEG,   ["45 В · 100 мА", "тихий, сигнальний", "групи β: A/B/C"]),
        (590, "2N2222", "2N2907", POS,   ["40 В · ~0.8 А", "швидкий, ВЧ", "трохи потужніший"]),
    ]
    for cx, npn_name, pnp_name, color, lines in cols:
        # символ NPN
        q, c, e = npn(cx, 130, "")
        f.append(q)
        f.append(text(cx + 4, 86, npn_name, size=15, bold=True, color=color, anchor="middle"))
        # картка з трьома фактами
        f.append(rect(cx - 92, 196, 184, 86, fill=FILL, stroke=color, sw=1.8))
        f.append(mtext(cx, 222, "\n".join(lines), size=12, color=INK))
        # PNP-пара
        f.append(text(cx, 318, "PNP-пара:", size=11, color=MUTED, anchor="middle"))
        f.append(text(cx, 338, pnp_name, size=14, bold=True, color=MUTED, anchor="middle"))
    render(os.path.join(IMG, "workhorses.svg"), W, H, *f)


# ── 4. Головна пастка: дзеркальна розпіновка TO-92 ───────────────────────────
def fig_pinout_trap():
    W, H = 720, 400
    f = [text(W / 2, 30, "Пастка TO-92: ніжки європейських і американських серій ДЗЕРКАЛЬНІ",
              size=15, bold=True)]

    def to92(cx, cy, order, color, title):
        out = [text(cx, cy - 70, title, size=14, bold=True, color=color, anchor="middle")]
        # півкорпус: пласка грань донизу (дивимось на грань, ніжки вниз)
        out.append('<path d="M%.0f %.0f A 46 46 0 0 1 %.0f %.0f Z" '
                   'fill="%s" stroke="%s" stroke-width="2"/>'
                   % (cx - 46, cy, cx + 46, cy, FILL, LINE))
        out.append(line(cx - 46, cy, cx + 46, cy, color=LINE, sw=2.4))  # пласка грань
        # три ніжки з підписами зліва-направо
        for i, lab in enumerate(order):
            lx = cx - 30 + i * 30
            out.append(line(lx, cy, lx, cy + 46, color=INK, sw=2.6))
            col = POS if lab == "C" else (NEG if lab == "E" else INK)
            out.append(circle(lx, cy + 62, 11, fill="#fff", stroke=col, sw=2))
            out.append(text(lx, cy + 66, lab, size=13, bold=True, color=col))
        return "".join(out)

    f.append(to92(200, 150, ["C", "B", "E"], NEG,
                  "BC547 / BC557 (європа): C–B–E"))
    f.append(to92(520, 150, ["E", "B", "C"], POS,
                  "2N3904 / 2N2222 (америка): E–B–C"))

    # стрілки-«перевертень» між C та E
    f.append(text(W / 2, 150, "≠", size=40, bold=True, color=POS, anchor="middle"))

    f.append(fitbox(90, 250, 540, 84,
                    "Дивимось на ПЛАСКУ грань, ніжки вниз. C і E помінялись місцями.\n"
                    "Встромив 2N3904 у схему під BC547, не звіривши, — переплутав\n"
                    "колектор з емітером. Перехід база–емітер у зворотному ввімкненні\n"
                    "пробивається вже за ~5–6 В і деградує за частку секунди.",
                    size=12.5, fill="#fdecea", stroke=POS))
    f.append(text(W / 2, 360, "Правило: щоразу звіряй розпіновку з даташитом САМЕ свого номера.",
                  size=13, bold=True, color=INK, anchor="middle"))
    render(os.path.join(IMG, "pinout-trap.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА «Дарлінгтонова пара» (comp-darlington-uln.md) — НЕ ЧІПАТИ (done)
# ════════════════════════════════════════════════════════════════════════════

# ── Множення β: вихід першого стає базою другого ─────────────────────────────
def fig_beta_multiply():
    W, H = 720, 420
    f = [text(W / 2, 28, "Дарлінгтонова пара: вихід першого транзистора живить базу другого",
              size=16, bold=True)]

    # спільний колектор угорі (обидва колектори разом)
    col_y = 70
    f.append(line(150, col_y, 600, col_y, color=POS, sw=2.4))
    f.append(text(610, col_y + 4, "C", size=14, color=POS, anchor="start", bold=True))
    f.append(text(150, col_y - 10, "спільний колектор", size=12, color=MUTED, anchor="start"))

    # Q1 (вхідний, слабкий) та Q2 (вихідний, силовий)
    q1, c1, e1 = npn(250, 200, "Q1")
    q2, c2, e2 = npn(470, 230, "Q2")
    f.append(q1)
    f.append(q2)

    # колектори обох — до спільної шини
    f.append(line(c1[0], c1[1], c1[0], col_y, color=POS, sw=1.8))
    f.append(line(c2[0], c2[1], c2[0], col_y, color=POS, sw=1.8))

    # емітер Q1 → база Q2 (КЛЮЧ: підсилений струм першого = базовий струм другого)
    f.append(line(e1[0], e1[1], e1[0], 230, color=FIELD, sw=2.4))
    f.append(line(e1[0], 230, 470 - 26, 230, color=FIELD, sw=2.4))   # у базу Q2
    f.append(text(335, 222, "e1 → b2", size=12, color=FIELD, anchor="middle", bold=True))

    # спільний емітер унизу
    em_y = 330
    f.append(line(e2[0], e2[1], e2[0], em_y, color=NEG, sw=2.4))
    f.append(line(220, em_y, 600, em_y, color=NEG, sw=2.4))
    f.append(text(610, em_y + 4, "E", size=14, color=NEG, anchor="start", bold=True))

    # вхід бази Q1
    f.append(line(150, 200, 250 - 26, 200, color=INK, sw=1.8))
    f.append(text(140, 204, "B", size=14, color=INK, anchor="end", bold=True))
    f.append(text(150, 184, "крихітний Iб", size=12, color=MUTED, anchor="start"))

    # підписи струмів — наростання
    bx1, by1, bw1, bh1 = 70, 360, 260, 44
    f.append(fitbox(bx1, by1, bw1, bh1,
                    "Q1 підсилює Iб у β1 разів;\nцей струм — уже база для Q2",
                    size=12, fill="#eef7ef", stroke=FIELD))
    bx2, by2, bw2, bh2 = 390, 360, 280, 44
    f.append(fitbox(bx2, by2, bw2, bh2,
                    "Q2 підсилює ще в β2 разів →\nзагальне β ≈ β1 · β2",
                    size=12, fill="#fdecea", stroke=POS))

    render(os.path.join(IMG, "darlington-beta.svg"), W, H, *f)


# ── Ціна пари: подвійний Vbe і повільне вимкнення ────────────────────────────
def fig_price():
    W, H = 720, 360
    f = [text(W / 2, 28, "Чим платимо: подвійний поріг і застрягання при вимкненні",
              size=16, bold=True)]

    # ── ліворуч: стек двох переходів = ~1.2–1.4 В ──
    lx = 60
    f.append(text(lx + 120, 64, "Поріг = два переходи в стопку", size=13, bold=True, anchor="middle"))
    f.append(fitbox(lx, 86, 240, 40, "Vбе(Q1) ≈ 0.7 В", size=13, fill=FILL, stroke=LINE))
    f.append(text(lx + 120, 142, "+", size=20, color=POS, bold=True))
    f.append(fitbox(lx, 152, 240, 40, "Vбе(Q2) ≈ 0.7 В", size=13, fill=FILL, stroke=LINE))
    f.append(line(lx, 206, lx + 240, 206, color=INK, sw=1.6))
    f.append(fitbox(lx, 216, 240, 44, "разом ≈ 1.2–1.4 В,\nщоб пара відкрилась", size=13,
                    fill="#fdecea", stroke=POS, bold=True))

    # ── праворуч: вимкнення — нікому стягнути заряд із бази Q2 ──
    rx = 380
    f.append(text(rx + 150, 64, "Вимкнення: база Q2 «висить»", size=13, bold=True, anchor="middle"))
    # символ Q2 з відкритою базою
    q2, c2, e2 = npn(rx + 70, 150, "Q2")
    f.append(q2)
    f.append(line(c2[0], c2[1], c2[0], 92, color=MUTED, sw=1.6))
    f.append(line(e2[0], e2[1], e2[0], 220, color=MUTED, sw=1.6))
    # хрест на виводі бази — нема куди витекти струму
    bxn = rx + 70 - 26
    f.append(line(bxn - 16, 150 - 12, bxn - 4, 150 + 12, color=POS, sw=2.4))
    f.append(line(bxn - 16, 150 + 12, bxn - 4, 150 - 12, color=POS, sw=2.4))
    f.append(text(bxn - 22, 138, "нема куди", size=11, color=POS, anchor="end"))
    f.append(fitbox(rx, 240, 300, 64,
                    "Q1, закрившись, перестає давати струм,\n"
                    "але вже накопичений заряд бази Q2\n"
                    "розсотується сам → вимкнення повільне",
                    size=12, fill="#eef1f5", stroke=LINE))

    render(os.path.join(IMG, "darlington-price.svg"), W, H, *f)


if __name__ == "__main__":
    # огляд
    fig_pick_params()
    fig_current_vs_field()
    # вставка малопотужних NPN
    fig_workhorses()
    fig_pinout_trap()
    # вставка Дарлінгтон (done) — лишаємо без змін
    fig_beta_multiply()
    fig_price()
    print("OK: figs у", IMG)
