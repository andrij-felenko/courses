# -*- coding: utf-8 -*-
"""Фігури до кроку «Що в DH строго, а що зрештою» (root/course/progarch)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

RED_FILL = "#fdecea"
BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eafaf1"
GREY_FILL = "#eef0f2"


# ── Фігура 1: лінійка консистентності з фактами DH ──────────────────────────
def fig_spectrum():
    W, H = 1000, 660
    f = []

    def band(y0, y1, fill, stroke):
        f.append(rect(90, y0, 870, y1 - y0, fill=fill, stroke=stroke, sw=1.6, rx=10))

    # СТРОГО
    band(70, 200, RED_FILL, POS)
    f.append(text(112, 108, "СТРОГО", size=17, color=POS, anchor="start", bold=True))
    f.append(text(112, 132, "лінеаризовано", size=12, color=MUTED, anchor="start"))
    f.append(text(112, 156, "усі бачать те саме", size=12, color=MUTED, anchor="start"))
    f.append(text(112, 174, "негайно", size=12, color=MUTED, anchor="start"))
    f.append(textbox(560, 135, "Доступ: дозволи\nй відкликання", size=15, bold=True,
                     fill="#fff", stroke=POS, color=POS)[0])
    f.append(textbox(810, 135, "Власність\nна пристрій", size=15, bold=True,
                     fill="#fff", stroke=POS, color=POS)[0])

    # ПРИЧИННО / СЕСІЙНО
    band(220, 350, BLUE_FILL, NEG)
    f.append(text(112, 262, "ПРИЧИННО /", size=16, color=NEG, anchor="start", bold=True))
    f.append(text(112, 284, "СЕСІЙНО", size=16, color=NEG, anchor="start", bold=True))
    f.append(text(112, 308, "твій власний вид", size=12, color=MUTED, anchor="start"))
    f.append(text(112, 326, "цілісний", size=12, color=MUTED, anchor="start"))
    f.append(textbox(560, 285, "Стан пристрою\nв застосунку", size=15, bold=True,
                     fill="#fff", stroke=NEG, color=NEG)[0])
    f.append(textbox(810, 285, "Автоматизації\n(порядок подій)", size=15, bold=True,
                     fill="#fff", stroke=NEG, color=NEG)[0])

    # ЗРЕШТОЮ
    band(370, 580, GREEN_FILL, FIELD)
    f.append(text(112, 430, "ЗРЕШТОЮ", size=17, color=FIELD, anchor="start", bold=True))
    f.append(text(112, 454, "eventual", size=12, color=MUTED, anchor="start"))
    f.append(text(112, 478, "світ тримає", size=12, color=MUTED, anchor="start"))
    f.append(text(112, 496, "правду", size=12, color=MUTED, anchor="start"))
    # ряд 1
    f.append(textbox(430, 432, "Телеметрія", size=15, bold=True,
                     fill="#fff", stroke=FIELD, color="#1e7a45")[0])
    f.append(textbox(650, 432, "Твін:\nостанній стан", size=15, bold=True,
                     fill="#fff", stroke=FIELD, color="#1e7a45")[0])
    f.append(textbox(860, 432, "Похідні\nзведення", size=15, bold=True,
                     fill="#fff", stroke=FIELD, color="#1e7a45")[0])
    # ряд 2
    f.append(textbox(500, 520, "Білінг:\nлічба пристроїв", size=15, bold=True,
                     fill="#fff", stroke=FIELD, color="#1e7a45")[0])
    f.append(textbox(740, 520, "Сповіщення", size=15, bold=True,
                     fill="#fff", stroke=FIELD, color="#1e7a45")[0])

    # вертикальна стрілка ліворуч: строго → зрештою
    f.append(arrow(58, 90, 58, 560, color=INK, sw=2.2))

    # нижній підпис
    cap = ("Що вище — то суворіша згода й вища ціна (затримка, менша доступність під час розколу); "
           "що нижче — то дешевше й доступніше, а розбіжність зводимо згодом.")
    f.append(fitbox(90, 600, 870, 44, cap, size=13, color=MUTED, fill=BG, stroke=BG, pad=6))

    render(os.path.join(IMG, "consistency-spectrum.svg"), W, H, *f,
           title="Факти Digital Homes на лінійці консистентності")


# ── Фігура 2: розкол хаб↔хмара ──────────────────────────────────────────────
def fig_partition():
    W, H = 1000, 580
    f = []

    # дім (ліворуч)
    f.append(rect(60, 78, 350, 322, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=12))
    f.append(text(235, 108, "ДІМ — хаб і пристрої", size=16, color="#1e7a45", bold=True))
    for cy, s in [(168, "✓ Локальне керування\nпристроями"),
                  (248, "✓ Локальні\nавтоматизації"),
                  (328, "✓ Телеметрія у чергу —\nдоллється потім")]:
        f.append(textbox(235, cy, s, size=13.5, bold=True, fill="#fff",
                         stroke=FIELD, color="#1e7a45", min_w=240)[0])

    # хмара (праворуч)
    f.append(rect(640, 78, 300, 322, fill=GREY_FILL, stroke=MUTED, sw=1.8, rx=12))
    f.append(text(790, 108, "ХМАРА — недосяжна", size=16, color=MUTED, bold=True))
    for cy, s in [(178, "репліки твіна"), (248, "ідентичність"), (318, "білінг")]:
        f.append(textbox(790, cy, s, size=13.5, fill="#fff", stroke=MUTED,
                         color=MUTED, min_w=190)[0])

    # блискавка-розкол між регіонами (проміжок 410..640)
    f.append(text(525, 70, "мережевий розкол", size=13, color=POS, bold=True))
    zig = [(525, 84), (503, 150), (543, 214), (509, 278), (547, 342),
           (513, 396)]
    for i in range(len(zig) - 1):
        f.append(line(zig[i][0], zig[i][1], zig[i + 1][0], zig[i + 1][1],
                      color=POS, sw=4))

    # строгий запит, що впирається в розкол (нижче регіонів)
    f.append(textbox(180, 452, "Запит: впустити гостя,\nзмінити тариф", size=13,
                     bold=True, fill="#fff", stroke=POS, color=POS, min_w=230)[0])
    f.append(line(300, 452, 500, 452, color=POS, sw=2.2))
    f.append(text(527, 461, "✗", size=28, color=POS, bold=True))
    f.append(text(566, 448, "не підтвердити → відмова", size=12.5, color=POS,
                  anchor="start", bold=True))

    cap = ("Строге замикається (обрали згоду, C → fail-closed): те, що мусить підтвердити "
           "авторитет у хмарі, під час розколу радше відмовляє. Зрештою-факти лишаються доступні.")
    f.append(fitbox(70, 512, 860, 46, cap, size=13, color=MUTED, fill=BG, stroke=BG, pad=6))

    render(os.path.join(IMG, "partition-split.svg"), W, H, *f,
           title="Розкол хаб↔хмара: що працює, а що замикається")


# ── Фігура 3: гонка відкликання ─────────────────────────────────────────────
def fig_revoke_race():
    W, H = 1060, 500
    f = []

    T0, T1, T2 = 320, 560, 800
    top, bot = 205, 355
    lane_l, lane_r = 190, 720

    # вертикальні маркери часу
    f.append(line(T0, 100, T0, 410, color=MUTED, sw=1.3, dash="5,5"))
    f.append(line(T1, 100, T1, 410, color=MUTED, sw=1.3, dash="5,5"))
    f.append(fitbox(T0 - 135, 72, 270, 38, "T0: власник відкликає доступ",
                    size=13, bold=True, fill=BG, stroke=BG, color=INK, pad=4))
    f.append(fitbox(T1 - 135, 72, 270, 38, "T1: підрядник тягне двері",
                    size=13, bold=True, fill=BG, stroke=BG, color=INK, pad=4))

    # смуга лагу на нижній доріжці
    f.append(rect(T0, bot - 24, T2 - T0, 48, fill=RED_FILL, stroke=RED_FILL, sw=1, rx=6))
    f.append(text((T0 + T1) / 2 - 20, bot - 30, "репліка ще каже «дозволено»",
                  size=12, color=POS))
    f.append(line(T2, bot - 24, T2, bot + 40, color=POS, sw=1.4, dash="4,4"))
    f.append(text(T2 + 6, bot - 4, "T2: репліка", size=11, color=MUTED, anchor="start"))
    f.append(text(T2 + 6, bot + 12, "наздогнала", size=11, color=MUTED, anchor="start"))

    # доріжка СТРОГО
    f.append(line(lane_l, top, lane_r, top, color=INK, sw=2))
    f.append(text(70, top - 6, "Строгий", size=13, color=INK, anchor="start", bold=True))
    f.append(text(70, top + 12, "шлях", size=13, color=INK, anchor="start", bold=True))
    f.append(circle(T1, top, 7, fill=INK, stroke=INK))
    f.append(fitbox(T1 + 22, top - 30, 190, 60,
                    "звіряється з авторитетом\n(лідер / кворум):\nбачить відкликання",
                    size=12, fill=BG, stroke="#d5d8dc", color=INK, pad=4))
    f.append(textbox(910, top, "ВІДМОВА\n(безпечно)", size=14, bold=True,
                     fill=GREEN_FILL, stroke=FIELD, color="#1e7a45", min_w=160)[0])

    # доріжка ЗРЕШТОЮ
    f.append(line(lane_l, bot, lane_r, bot, color=INK, sw=2))
    f.append(text(70, bot - 6, "Зрештою:", size=13, color=INK, anchor="start", bold=True))
    f.append(text(70, bot + 12, "застаріла", size=13, color=INK, anchor="start", bold=True))
    f.append(text(70, bot + 30, "репліка", size=13, color=INK, anchor="start", bold=True))
    f.append(circle(T1, bot, 7, fill=POS, stroke=POS))
    f.append(fitbox(T1 + 22, bot + 34, 200, 46,
                    "читає ближчу репліку:\nще «дозволено»",
                    size=12, fill=BG, stroke="#f0cfca", color=POS, pad=4))
    f.append(textbox(910, bot, "ДВЕРІ\nВІДЧИНЯЮТЬСЯ", size=14, bold=True,
                     fill=RED_FILL, stroke=POS, color=POS, min_w=160)[0])

    cap = ("Той самий момент, дві дороги читання. Строгий шлях звіряється з авторитетом і відмовляє; "
           "читання застарілої репліки впускає відкликаного — тому шлях доступу тримаємо строгим.")
    f.append(fitbox(70, 452, 920, 40, cap, size=13, color=MUTED, fill=BG, stroke=BG, pad=5))

    render(os.path.join(IMG, "revocation-race.svg"), W, H, *f,
           title="Гонка відкликання: чому шлях доступу мусить бути строгим")


# ── Фігура 4 (до proj-вставки): перетин кворумів ────────────────────────────
def fig_quorum_intersection():
    W, H = 1080, 700
    f = []
    GD = "#1e7a45"

    # формула зверху
    f.append(fitbox(70, 48, 940, 40,
        "N = 3 копії  ·  W = 2 (запис)  ·  R = 2 (читання)   →   R + W = 4 > 3   →   "
        "кожен кворум читання перетинає кожен кворум запису",
        size=14, bold=True, fill=BLUE_FILL, stroke=NEG, color=NEG, pad=8))

    # підсвітка стовпця B (перетин): зелена смуга від верхнього дужка до нижнього
    f.append(rect(435, 178, 210, 182, fill=GREEN_FILL, stroke=GREEN_FILL, sw=1, rx=8))
    f.append(text(540, 200, "перетин", size=12, color=GD, bold=True))

    # кворум запису над A,B
    f.append(text(395, 162, "кворум запису W=2  →  відкликання v2", size=13, color=NEG, bold=True))
    f.append(line(145, 178, 645, 178, color=INK, sw=1.6))
    f.append(line(145, 178, 145, 192, color=INK, sw=1.6))
    f.append(line(645, 178, 645, 192, color=INK, sw=1.6))

    # три коробки-репліки
    def repbox(cx, head, val, badge, bfill, bstroke, bcol, hot=False):
        x = cx - 105
        f.append(rect(x, 210, 210, 130, fill=BG, stroke=(FIELD if hot else INK),
                      sw=(2.6 if hot else 1.8), rx=10))
        f.append(text(cx, 238, head, size=15, color=INK, bold=True))
        f.append(text(cx, 266, "grant …:pidryadnyk", size=11.5, color=MUTED))
        f.append(text(cx, 294, val, size=15, color=INK, bold=True))
        f.append(textbox(cx, 320, badge, size=12.5, fill=bfill, stroke=bstroke,
                         color=bcol, bold=True, min_w=120)[0])

    repbox(250, "A · лідер", "grant = false", "v2 · свіже", GREEN_FILL, FIELD, GD)
    repbox(540, "B · репліка", "grant = false", "v2 · свіже", GREEN_FILL, FIELD, GD, hot=True)
    repbox(830, "E · край (біля дверей)", "grant = true", "v1 · застаріле", RED_FILL, POS, POS)

    # кворум читання під B,E
    f.append(line(435, 360, 935, 360, color=INK, sw=1.6))
    f.append(line(435, 348, 435, 360, color=INK, sw=1.6))
    f.append(line(935, 348, 935, 360, color=INK, sw=1.6))
    f.append(text(685, 382, "кворум читання R=2  (навмисне без лідера)", size=13, color=GD, bold=True))

    # результати
    f.append(fitbox(145, 424, 790, 42,
        "Строге читання {B, E}:  max(v2, v1) = v2 = false  →  ВІДМОВА (безпечно)",
        size=14, bold=True, fill=GREEN_FILL, stroke=FIELD, color=GD, pad=8))
    f.append(fitbox(145, 478, 790, 42,
        "Зрештою, лише E:  v1 = true  →  ВІДЧИНЯЄ (відкликаного впущено)",
        size=14, bold=True, fill=RED_FILL, stroke=POS, color=POS, pad=8))

    cap = ("Будь-які R копій перетинають будь-які W (Gifford, 1979): у наборі {B, E} копія B несе "
           "відкликання v2, тож строге читання ловить його навіть без лідера. Версії кажуть, котра "
           "копія свіжа. Одну ж застарілу копію E, прочитану наодинці, ніщо не поправить — вона впускає.")
    f.append(fitbox(70, 540, 940, 56, cap, size=13, color=MUTED, fill=BG, stroke=BG, pad=8))

    render(os.path.join(IMG, "quorum-intersection.svg"), W, H, *f,
           title="Перетин кворумів: чому строге читання ловить відкликання")


# ── Фігура 5 (вставка hist): об'єднання кошиків при читанні ──────────────────
def fig_cart_merge():
    W, H = 1060, 645
    f = []

    # спільний початок
    f.append(textbox(530, 66, "Спільний початок кошика:  хліб · яйця",
                     size=14, fill=GREY_FILL, stroke=MUTED, color=INK, min_w=380)[0])

    # ── дві розбіжні версії під час розколу ──
    f.append(rect(70, 110, 380, 182, BLUE_FILL, NEG, sw=1.8, rx=12))
    f.append(text(260, 138, "Репліка A", size=16, color=NEG, bold=True))
    f.append(text(260, 160, "користувач ДОДАЄ молоко", size=12.5, color=MUTED))
    f.append(text(260, 198, "хліб", size=15, color=INK))
    f.append(text(260, 224, "яйця", size=15, color=INK))
    f.append(text(260, 256, "+ молоко", size=15, color="#1e7a45", bold=True))

    f.append(rect(610, 110, 380, 182, BLUE_FILL, NEG, sw=1.8, rx=12))
    f.append(text(800, 138, "Репліка B", size=16, color=NEG, bold=True))
    f.append(text(800, 160, "користувач ВИДАЛЯЄ яйця", size=12.5, color=MUTED))
    f.append(text(800, 198, "хліб", size=15, color=INK))
    f.append(text(800, 230, "− яйця  (видалено)", size=15, color=POS, bold=True))

    # розкол між ними
    f.append(line(530, 114, 530, 290, color=POS, sw=2, dash="6,6"))
    f.append(text(530, 104, "розкол мережі", size=12.5, color=POS, bold=True))

    # ── стрілки до злиття ──
    f.append(arrow(260, 294, 468, 356, color=INK, sw=2))
    f.append(arrow(800, 294, 592, 356, color=INK, sw=2))
    f.append(textbox(530, 382, "ОБ'ЄДНАННЯ (union)\nпри читанні", size=14, bold=True,
                     fill="#fff", stroke=INK, color=INK, min_w=250)[0])

    # ── результат ──
    f.append(arrow(530, 412, 530, 454, color=INK, sw=2))
    f.append(text(530, 478, "Кошик після зведення = union версій", size=15, bold=True, color=INK))
    f.append(rect(205, 492, 650, 98, fill=BG, stroke=MUTED, sw=1.4, rx=12))
    f.append(textbox(318, 541, "хліб\nбув у обох", size=13.5, bold=True,
                     fill=GREY_FILL, stroke=MUTED, color=INK, min_w=150)[0])
    f.append(textbox(530, 541, "молоко\n✓ додане збережено", size=13.5, bold=True,
                     fill=GREEN_FILL, stroke=FIELD, color="#1e7a45", min_w=195)[0])
    f.append(textbox(742, 541, "яйця\n✗ видалене воскресло", size=13.5, bold=True,
                     fill=RED_FILL, stroke=POS, color=POS, min_w=195)[0])

    cap = ("Об'єднання ніколи не губить «додав» (жоден продаж не втрачено), але може воскресити «видалив» "
           "— дрібна поправна незручність. Асиметрія навмисна: втратити додаток дорого, зайвий рядок — ні.")
    f.append(fitbox(80, 604, 900, 32, cap, size=13, color=MUTED, fill=BG, stroke=BG, pad=6))

    render(os.path.join(IMG, "cart-merge.svg"), W, H, *f,
           title="Кошик Amazon: об'єднання версій при читанні")


if __name__ == "__main__":
    fig_spectrum()
    fig_partition()
    fig_revoke_race()
    fig_quorum_intersection()
    fig_cart_merge()
    print("OK: 5 figures ->", IMG)
