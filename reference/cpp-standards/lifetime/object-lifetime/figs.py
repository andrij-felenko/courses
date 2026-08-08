# -*- coding: utf-8 -*-
"""Фігури теми «Час життя об'єкта»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_storage_vs_lifetime():
    """Сховище довше за час життя: дві щілини, у яких байти є, а об'єкта нема."""
    W, H = 900, 400
    f = []

    x0, x1 = 90, 800          # межі сховища
    xa, xb = 260, 630         # межі часу життя

    # ── смуга сховища
    f.append(rect(x0, 92, x1 - x0, 48, fill="#eef2f7", stroke=MUTED, sw=1.4))
    f.append(text(445, 122, "сховище: байти потрібного розміру й вирівнювання", size=14, color=MUTED))

    # ── смуга часу життя
    f.append(rect(xa, 178, xb - xa, 48, fill="#eef7ee", stroke=FIELD, sw=2))
    f.append(text(445, 208, "час життя об'єкта", size=15, color=FIELD, bold=True))

    # ── дві щілини
    f.append(fitbox(x0 + 6, 178, xa - x0 - 14, 48, "байти є —\nоб'єкта ще нема",
                    size=12, fill="#fdecea", stroke=POS, color=POS))
    f.append(fitbox(xb + 8, 178, x1 - xb - 14, 48, "об'єкта вже нема —\nбайти ще є",
                    size=12, fill="#fdecea", stroke=POS, color=POS))

    # ── вісь і позначки моментів
    f.append(line(50, 268, 850, 268, color=INK, sw=1.4))
    for x in (x0, xa, xb, x1):
        f.append(line(x, 84, x, 268, color=MUTED, sw=1, dash="4,4"))

    labels = [
        (x0, "отримано\nсховище"),
        (xa, "ініціалізацію\nзавершено"),
        (xb, "почався\nдеструктор"),
        (x1, "сховище\nзвільнено"),
    ]
    for x, s in labels:
        f.append(fitbox(x - 78, 284, 156, 52, s, size=12, fill=BG, stroke=LINE))

    f.append(text(450, 366,
                  "Вказівник на ці байти дійсний увесь час — але «об'єктом» вони є лише в зеленому проміжку.",
                  size=13, color=INK))

    render(os.path.join(IMG, 'storage-vs-lifetime.svg'), W, H, *f,
           title="Сховище й час життя — дві різні тривалості")


def fig_storage_durations():
    """Чотири тривалості зберігання: хто визначає момент кінця."""
    W, H = 920, 420
    f = []

    cols = [(40, 196), (252, 428), (696, 184)]
    heads = ["тривалість зберігання", "коли байти з'являються і зникають", "хто ставить кінець"]
    for (x, w), s in zip(cols, heads):
        f.append(fitbox(x, 48, w, 42, s, size=13, bold=True, fill="#eef2f7", stroke=MUTED, color=MUTED))

    rows = [
        ("автоматична", "вхід у блок → вихід із блока,\nу тому числі через виняток", "компілятор", FIELD),
        ("статична", "перед першим використанням →\nпісля виходу з main", "компілятор", FIELD),
        ("потокова", "початок потоку → кінець потоку", "компілятор", FIELD),
        ("динамічна", "виклик operator new →\nвиклик operator delete", "тільки ви", POS),
    ]

    y0, dy, bh = 102, 68, 56
    for i, (name, when, who, col) in enumerate(rows):
        y = y0 + i * dy
        hot = (col is POS)
        f.append(fitbox(cols[0][0], y, cols[0][1], bh, name, size=14, bold=True,
                        fill="#fdecea" if hot else FILL, stroke=col if hot else LINE,
                        color=col if hot else INK))
        f.append(fitbox(cols[1][0], y, cols[1][1], bh, when, size=12))
        f.append(fitbox(cols[2][0], y, cols[2][1], bh, who, size=13, bold=hot,
                        fill="#fdecea" if hot else "#eef7ee", stroke=col, color=col))

    f.append(text(460, 396,
                  "Питання «хто власник» існує лише в останньому рядку: тільки там мова не знає моменту кінця.",
                  size=13, color=INK))

    render(os.path.join(IMG, 'storage-durations.svg'), W, H, *f,
           title="Чотири джерела байтів і той, хто вирішує кінець")


def fig_subobject_order():
    """Побудова згори вниз, руйнування знизу вгору; життя цілого — між тілами."""
    W, H = 940, 520
    f = []

    f.append(fitbox(70, 46, 340, 40, "побудова: згори вниз", size=14, bold=True,
                    fill="#eef2f7", stroke=MUTED, color=MUTED))
    f.append(fitbox(530, 46, 340, 40, "руйнування: знизу вгору", size=14, bold=True,
                    fill="#eef2f7", stroke=MUTED, color=MUTED))

    rows = [
        ("1 · базовий підоб'єкт Base", "4 · Base::~Base()"),
        ("2 · член a (за порядком оголошення)", "3 · a.~A()"),
        ("3 · член b", "2 · b.~B()"),
        ("4 · тіло Widget::Widget() { }", "1 · тіло Widget::~Widget() { }"),
    ]
    y0, dy, bh = 102, 66, 54
    for i, (left, right) in enumerate(rows):
        y = y0 + i * dy
        f.append(fitbox(70, y, 340, bh, left, size=13))
        f.append(fitbox(530, y, 340, bh, right, size=13))

    ylast = y0 + 3 * dy + bh
    f.append(arrow(50, 106, 50, ylast - 6, color=MUTED))
    f.append(arrow(890, ylast - 6, 890, 106, color=MUTED))

    f.append(fitbox(70, ylast + 26, 800, 52,
                    "між кінцем тіла конструктора й початком тіла деструктора — і тільки тут — живий сам Widget",
                    size=13, bold=True, fill="#eef7ee", stroke=FIELD, color=FIELD))

    f.append(fitbox(70, ylast + 92, 800, 52,
                    "виняток на кроці 3: кроки 2 і 1 руйнуються у зворотному порядку, "
                    "а тіло ~Widget() не виконається зовсім",
                    size=13, fill="#fdecea", stroke=POS, color=POS))

    render(os.path.join(IMG, 'subobject-order.svg'), W, H, *f,
           title="Порядок підоб'єктів і те, коли живе ціле")


def fig_temporary_life():
    """Той самий тимчасовий: гине на крапці з комою чи доживає до кінця області."""
    W, H = 920, 430
    f = []

    def panel(y, code, bar_split, bar1, bar2, verdict, ok):
        col = FIELD if ok else POS
        fill = "#eef7ee" if ok else "#fdecea"
        g = [rect(30, y, 860, 158, fill=BG, stroke=MUTED, sw=1.2)]
        g.append(fitbox(52, y + 18, 500, 38, code, size=13, fill=FILL))
        if bar_split:
            g.append(fitbox(52, y + 74, 214, 40, bar1, size=12,
                            fill="#eef7ee", stroke=FIELD, color=FIELD))
            g.append(fitbox(282, y + 74, 270, 40, bar2, size=12,
                            fill="#fdecea", stroke=POS, color=POS))
        else:
            g.append(fitbox(52, y + 74, 500, 40, bar1, size=12,
                            fill="#eef7ee", stroke=FIELD, color=FIELD))
        g.append(fitbox(586, y + 46, 282, 66, verdict, size=13, bold=True,
                        fill=fill, stroke=col, color=col))
        return g

    f += panel(44, "const char* p = make().c_str();",
               True,
               "тимчасовий рядок\nживий",
               "крапка з комою —\nтимчасовий знищено, p висить",
               "звернення за p —\nневизначена поведінка", False)

    f += panel(230, "const std::string& r = make();",
               False,
               "тимчасовий живе рівно стільки, скільки посилання r — до кінця блока",
               None,
               "продовження життя\nспрацювало", True)

    f.append(text(460, 406,
                  "Різниця не в типі результату, а в тому, що зв'язали: посилання з самим тимчасовим "
                  "чи вказівник з його нутрощами.",
                  size=13, color=INK))

    render(os.path.join(IMG, 'temporary-life.svg'), W, H, *f,
           title="Тимчасовий об'єкт: повний вираз проти продовження життя")


def fig_manual_slots():
    """Смуга слотів контейнера: живий префікс, сирий хвіст і відкат при виняткові."""
    W, H = 900, 380
    f = []

    x0, sw_, sh = 70, 96, 54
    gap = 8

    def slot(i, y, fill, stroke, label, bold=False):
        x = x0 + i * sw_
        g = [rect(x, y, sw_ - gap, sh, fill=fill, stroke=stroke, sw=1.8)]
        g.append(text(x + (sw_ - gap) / 2, y + 32, label, size=12, color=stroke, bold=bold))
        return g

    def indices(y):
        g = []
        for i in range(8):
            g.append(text(x0 + i * sw_ + (sw_ - gap) / 2, y, str(i), size=11, color=MUTED))
        return g

    # ── ряд A: звичайний стан
    f.append(text(450, 34, "Стан контейнера: одне число ділить смугу байтів надвоє",
                  size=14, color=INK, bold=True))
    f += indices(66)
    yA = 76
    for i in range(8):
        if i < 3:
            f += slot(i, yA, "#eef7ee", FIELD, "T живий", bold=True)
        else:
            f += slot(i, yA, "#f4f6f8", MUTED, "сирі байти")
    xb = x0 + 3 * sw_ - gap / 2
    f.append(line(xb, yA - 22, xb, yA + sh + 12, color=POS, sw=1.6, dash="5,4"))
    f.append(text(xb, yA + sh + 32, "size_ = 3", size=13, color=POS, bold=True))

    # ── ряд B: виняток посеред заповнення
    f.append(text(450, 200, "Заповнення обірвано: конструктор кинув на слоті 4",
                  size=14, color=INK, bold=True))
    f += indices(232)
    yB = 242
    for i in range(8):
        if i < 2:
            f += slot(i, yB, "#eef7ee", FIELD, "було")
        elif i < 4:
            f += slot(i, yB, "#eef7ee", FIELD, "створено", bold=True)
        elif i == 4:
            f += slot(i, yB, "#fdecea", POS, "виняток", bold=True)
        else:
            f += slot(i, yB, "#f4f6f8", MUTED, "сирі байти")

    xr1 = x0 + 3 * sw_ + (sw_ - gap) / 2
    xr2 = x0 + 2 * sw_ + (sw_ - gap) / 2
    f.append(arrow(xr1, yB + sh + 16, xr2, yB + sh + 16, color=POS, sw=2))
    f.append(text(xr1 + 24, yB + sh + 21, "зворотний порядок руйнування",
                  size=12, color=POS, anchor="start"))

    f.append(text(450, 366,
                  "Слот 4 так і не став об'єктом — конструктор не завершився, "
                  "тож size_ його ніколи не рахував.",
                  size=13, color=INK))

    render(os.path.join(IMG, 'manual-slots.svg'), W, H, *f,
           title="Слоти контейнера: живий префікс, сирий хвіст і відкат")


def fig_extension_chain():
    """Продовження життя тримається лише на цілому ланцюгу дозволених кроків."""
    W, H = 980, 480
    f = []

    def panel(px, code, steps, verdict, ok):
        col = FIELD if ok else POS
        fill = "#eef7ee" if ok else "#fdecea"
        g = [rect(px, 44, 450, 356, fill=BG, stroke=MUTED, sw=1.2)]
        g.append(fitbox(px + 18, 58, 414, 36, code, size=13, fill=FILL, stroke=LINE))
        y = 108
        for kind, s in steps:
            if kind == 'node':
                g.append(fitbox(px + 18, y, 414, 36, s, size=13, bold=True))
                y += 44
            else:
                good = (kind == 'ok')
                g.append(fitbox(px + 18, y, 414, 32, s, size=12,
                                fill="#eef7ee" if good else "#fdecea",
                                stroke=FIELD if good else POS,
                                color=FIELD if good else POS))
                y += 40
        g.append(fitbox(px + 18, 336, 414, 50, verdict, size=13, bold=True,
                        fill=fill, stroke=col, color=col))
        return g

    f += panel(20, "const Point& r = make_box().tl;",
               [('node', "посилання r"),
                ('ok', "крок «.tl» — доступ до члена: у списку"),
                ('node', "підоб'єкт tl усередині тимчасового"),
                ('ok', "крок «матеріалізація prvalue»: у списку"),
                ('node', "тимчасовий Box")],
               "ланцюг цілий: увесь Box живе стільки, скільки r", True)

    f += panel(510, "const std::string& r = std::min(make(), s);",
               [('node', "посилання r"),
                ('bad', "крок «виклик min()»: у списку його немає"),
                ('node', "ланцюг обірвано на першому ж кроці"),
                ('bad', "далі діє звичайне правило повного виразу"),
                ('node', "тимчасовий std::string")],
               "тимчасовий гине на «;» — r висить, а код збирається", False)

    f.append(text(490, 444,
                  "Продовження вмикає не тип і не намір, а форма шляху: кожен крок "
                  "від посилання до тимчасового мусить бути зі списку.",
                  size=13, color=INK))

    render(os.path.join(IMG, 'extension-chain.svg'), W, H, *f,
           title="Продовження життя тримається лише на цілому ланцюгу")


if __name__ == '__main__':
    fig_storage_vs_lifetime()
    fig_storage_durations()
    fig_subobject_order()
    fig_temporary_life()
    fig_manual_slots()
    fig_extension_chain()
    print('ok')
