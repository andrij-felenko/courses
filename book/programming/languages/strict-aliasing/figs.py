# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_assumption():
    """Компілятор припускає: покажчики різних типів НЕ дивляться на одну комірку."""
    W, H = 720, 340
    body = []
    body.append(text(W/2, 30, "Припущення компілятора: різні типи — різна пам'ять", size=17, bold=True))

    # дві змінні-покажчики зверху
    b1, w1, h1 = textbox(160, 90, "float* f", size=15, bold=True,
                         fill="#fdecea", stroke=POS)
    b2, w2, h2 = textbox(560, 90, "int* p", size=15, bold=True,
                         fill="#eaf0fd", stroke=NEG)
    body += [b1, b2]

    # дві окремі комірки пам'яті — «переконаний, що вони РІЗНІ»
    body.append(fitbox(90, 190, 140, 60, "комірка A\n(float)", size=13,
                       fill=FILL, stroke=POS))
    body.append(fitbox(490, 190, 140, 60, "комірка B\n(int)", size=13,
                       fill=FILL, stroke=NEG))

    body.append(arrow(160, 118, 160, 188, color=POS))
    body.append(arrow(560, 118, 560, 188, color=NEG))

    # висновок
    b3, w3, h3 = textbox(W/2, 300, "«запис через f не чіпає B → перечитувати B не треба»",
                        size=13, fill="#eafaf1", stroke=FIELD)
    body.append(b3)

    render(os.path.join(OUT, "assumption.svg"), W, H, *body)


def fig_bug():
    """Ту саму комірку чіпають float* і int*; компілятор переставляє/кешує — сміття."""
    W, H = 720, 360
    body = []
    body.append(text(W/2, 30, "Порушення: два типи на ОДНІЙ комірці", size=17, bold=True))

    # одна спільна комірка в центрі
    body.append(fitbox(280, 150, 160, 70, "одна комірка\nпам'яті", size=14,
                       fill="#fff7e6", stroke="#b8860b", sw=2))

    # float* пише
    b1, _, _ = textbox(150, 95, "float* f\n(пише)", size=13,
                       fill="#fdecea", stroke=POS)
    body.append(b1)
    body.append(arrow(150, 120, 285, 150, color=POS))

    # int* читає
    b2, _, _ = textbox(575, 95, "int* p\n(читає)", size=13,
                       fill="#eaf0fd", stroke=NEG)
    body.append(b2)
    body.append(arrow(575, 120, 435, 150, color=NEG))

    # що робить оптимізатор
    body.append(fitbox(120, 270, 220, 64,
                       "думає: f і p — різне,\nтож читання p можна\nне оновлювати", size=12,
                       fill=FILL, stroke=MUTED))
    body.append(fitbox(380, 270, 220, 64,
                       "результат: p читає\nстаре значення →\nсміття (це UB)", size=12,
                       fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, "bug.svg"), W, H, *body)


def fig_safe():
    """Законний шлях: байти через char*/memcpy — компілятор мусить враховувати."""
    W, H = 720, 320
    body = []
    body.append(text(W/2, 30, "Законний міст між типами: копія байтів", size=17, bold=True))

    body.append(fitbox(70, 120, 150, 64, "float\n(4 байти)", size=13,
                       fill=FILL, stroke=POS))
    # memcpy як міст
    b, w, h = textbox(360, 152, "memcpy\n(копія байт-у-байт)", size=13, bold=True,
                     fill="#eafaf1", stroke=FIELD)
    body.append(b)
    body.append(fitbox(500, 120, 150, 64, "int\n(ті самі 4 байти)", size=13,
                       fill=FILL, stroke=NEG))

    body.append(arrow(222, 152, 300, 152, color=FIELD))
    body.append(arrow(420, 152, 498, 152, color=FIELD))

    b2, _, _ = textbox(W/2, 260,
                      "char/unsigned char дивиться на будь-який тип → правило дотримано",
                      size=13, fill="#eafaf1", stroke=FIELD)
    body.append(b2)

    render(os.path.join(OUT, "safe.svg"), W, H, *body)


def fig_timeline():
    """Історична хронологія: правило в стандарті vs коли GCC почав ним користуватися."""
    W, H = 760, 430
    body = []
    body.append(text(W/2, 28, "Хронологія: правило старе, оптимізація нова", size=17, bold=True))

    # вертикальна вісь часу
    ax = 190
    body.append(line(ax, 60, ax, 400, color=MUTED, sw=2))

    def node(y, color, when, what):
        body.append(circle(ax, y, 7, fill=color, stroke=color))
        body.append(text(ax - 16, y + 4, when, size=13, bold=True, color=color, anchor="end"))
        body.append(fitbox(ax + 20, y - 22, 540, 44, what, size=12,
                           fill=FILL, stroke=color))

    node(80,  MUTED, "1989–90", "Правило вже в C90 (розділ 6.3): читати об'єкт лише сумісним типом. Тихий пункт — компілятори ним не користуються.")
    node(160, NEG,   "чер. 1998", "Патч Марка Мітчелла: type-based alias analysis у GCC. Прапорець -fstrict-aliasing «увімкнений типово під -O2».")
    node(240, POS,   "лип. 1999", "GCC 2.95: аналіз типово увімкнено. Сторінка релізу прямо: «expose bugs in the Linux kernel».")
    node(310, FIELD, "жовт. 1999", "GCC 2.95.2: під тиском багів прапорець типово ВИМКНЕНО. «Знайдіть і виправте код, що порушує стандарт».")
    node(380, NEG,   "груд. 1999", "Аж тепер виходить C99 (розділ 6.5, «ефективний тип») — уже після того, як GCC це впровадив і відкотив.")

    render(os.path.join(OUT, "timeline.svg"), W, H, *body)


def fig_restrict_guard():
    """Однаковий тип: компілятор мусить припускати можливе перекриття out з a/b."""
    W, H = 720, 380
    body = []
    body.append(text(W / 2, 30, "Однаковий тип не дає підказки: out може перекриватися", size=16, bold=True))

    b1, _, _ = textbox(140, 80, "float* out", size=13, bold=True, fill=FILL, stroke=INK)
    b2, _, _ = textbox(360, 80, "float* a", size=13, bold=True, fill=FILL, stroke=INK)
    b3, _, _ = textbox(580, 80, "float* b", size=13, bold=True, fill=FILL, stroke=INK)
    body += [b1, b2, b3]

    body.append(fitbox(210, 150, 300, 46, "той самий буфер (можливе перекриття)", size=12,
                       fill="#fff7e6", stroke="#b8860b", sw=2))
    body.append(arrow(140, 108, 250, 150, color=MUTED))
    body.append(arrow(360, 108, 360, 150, color=MUTED))
    body.append(arrow(580, 108, 470, 150, color=MUTED))

    body.append(fitbox(70, 250, 270, 90,
                       "варіант 1:\nобережний скалярний цикл\nчитай-пиши строго по черзі\n(без векторизації)", size=12,
                       fill=FILL, stroke=MUTED))
    body.append(fitbox(380, 250, 270, 90,
                       "варіант 2:\nперевірка адрес під час\nвиконання -> дві гілки\n(швидка + повільна)", size=12,
                       fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, "restrict-guard.svg"), W, H, *body)


def fig_restrict_codegen():
    """Той самий цикл: без restrict — скалярно по черзі; з restrict — векторно."""
    W, H = 720, 380
    body = []
    body.append(text(W / 2, 30, "Той самий цикл копіювання, різний машинний код", size=16, bold=True))

    b1, _, _ = textbox(185, 75, "БЕЗ restrict", size=14, bold=True, fill="#fdecea", stroke=POS)
    body.append(b1)
    body.append(fitbox(50, 110, 270, 210,
                       "перекриття не виключене\n-> строго по черзі:\n\nload  src[0]\nstore dst[0]\nload  src[1]\nstore dst[1]\n...  (n разів, скалярно)", size=12,
                       fill=FILL, stroke=POS))

    b2, _, _ = textbox(535, 75, "З restrict", size=14, bold=True, fill="#eafaf1", stroke=FIELD)
    body.append(b2)
    body.append(fitbox(400, 110, 270, 210,
                       "перекриття виключене\n-> укрупнено, векторно:\n\nvload  src[0..3]\nvstore dst[0..3]\nvload  src[4..7]\nvstore dst[4..7]\n... (n/4 разів)", size=12,
                       fill=FILL, stroke=FIELD))

    render(os.path.join(OUT, "restrict-codegen.svg"), W, H, *body)


def fig_restrict_lie():
    """Брехлива обіцянка: restrict сказав 'окремі', а буфери в одному масиві зі зсувом."""
    W, H = 720, 400
    body = []
    body.append(text(W / 2, 30, "Брехлива обіцянка: restrict сказав «окремі», а вони — ні", size=16, bold=True))

    b0, _, _ = textbox(W / 2, 72, "restrict: «dst і src не перетинаються»", size=13, bold=True,
                       fill="#eafaf1", stroke=FIELD)
    body.append(b0)

    body.append(text(W / 2, 118, "реальність: dst = buf+1, src = buf — одна пам'ять зі зсувом", size=12, color=POS))
    cells = ["buf0", "buf1", "buf2", "buf3", "buf4"]
    x0, cw = 190, 70
    for i, c in enumerate(cells):
        body.append(rect(x0 + i * cw, 140, cw - 6, 40, fill="#fff7e6", stroke="#b8860b", sw=1.5))
        body.append(text(x0 + i * cw + (cw - 6) / 2, 165, c, size=12))
    body.append(text(x0 + (cw - 6) / 2, 205, "src", size=12, color=NEG))
    body.append(text(x0 + cw + (cw - 6) / 2, 205, "dst", size=12, color=POS))

    body.append(fitbox(70, 250, 270, 110,
                       "компілятор повірив:\nчитає всі src наперед\nу регістри, тоді розкладає\n(векторно, з переставленням)", size=12,
                       fill=FILL, stroke=MUTED))
    body.append(fitbox(380, 250, 270, 110,
                       "але src і dst — та сама\nпам'ять: частину вже\nзатерто -> результат не той\n(UB, без попередження)", size=12,
                       fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, "restrict-lie.svg"), W, H, *body)


if __name__ == "__main__":
    fig_assumption()
    fig_bug()
    fig_safe()
    fig_timeline()
    fig_restrict_guard()
    fig_restrict_codegen()
    fig_restrict_lie()
    print("figures written")
