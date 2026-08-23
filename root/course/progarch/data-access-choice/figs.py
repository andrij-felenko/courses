# -*- coding: utf-8 -*-
"""Фігури до кроку «Компакт-вибір: доступ до даних»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_who_knows_db():
    W, H = 960, 400
    frags = []

    # вертикальні розділювачі між панелями
    for sx in (320, 640):
        frags.append(line(sx, 48, sx, 380, color=MUTED, sw=1, dash="4,5"))

    # підзаголовки панелей
    frags.append(text(160, 62, "Active Record", size=15, bold=True))
    frags.append(text(480, 62, "Data Mapper", size=15, bold=True))
    frags.append(text(800, 62, "SQL + Repository", size=15, bold=True))

    # ── Active Record: домен сам тягнеться до таблиці ──
    b, _, _ = textbox(160, 115, "Device\n+ save() / find()", size=13)
    frags.append(b)
    frags.append(arrow(160, 141, 160, 282, color=POS, sw=2.2))
    frags.append(text(172, 214, "знає", size=11, color=MUTED, anchor="start"))
    b, _, _ = textbox(160, 300, "таблиця devices", size=13, fill="#eef2f6")
    frags.append(b)

    # ── Data Mapper: посередник знає обидві сторони ──
    b, _, _ = textbox(480, 115, "Device\n(чистий домен)", size=13)
    frags.append(b)
    frags.append(line(480, 141, 480, 179, color=LINE, sw=1.8))
    b, _, _ = textbox(480, 205, "DeviceMapper\n(знає обидві сторони)", size=13, fill="#eaf0fd")
    frags.append(b)
    frags.append(line(480, 231, 480, 282, color=LINE, sw=1.8))
    b, _, _ = textbox(480, 300, "таблиця devices", size=13, fill="#eef2f6")
    frags.append(b)

    # ── SQL + Repository: знання про базу замкнене в репозиторії ──
    b, _, _ = textbox(800, 115, "Device\n(домен)", size=13)
    frags.append(b)
    frags.append(line(800, 141, 800, 179, color=LINE, sw=1.8))
    b, _, _ = textbox(800, 205, "DeviceRepository\n(SQL руками)", size=13, fill="#eafaf0")
    frags.append(b)
    frags.append(line(800, 231, 800, 282, color=LINE, sw=1.8))
    b, _, _ = textbox(800, 300, "таблиця devices", size=13, fill="#eef2f6")
    frags.append(b)

    render(os.path.join(IMG, "who-knows-db.svg"), W, H, *frags,
           title="Хто знає про базу")


def fig_choice_map():
    W, H = 760, 560
    ox, oy = 110, 470            # початок осей
    frags = []

    # осі
    frags.append(arrow(ox, oy, 690, oy, color=LINE, sw=1.8))   # X →
    frags.append(arrow(ox, oy, ox, 90, color=LINE, sw=1.8))    # Y ↑
    frags.append(text(400, 505, "складність поведінки домену  →", size=13, color=MUTED))
    frags.append(text(110, 76, "контроль над SQL  ↑", size=13, color=MUTED))

    # три варіанти в різних кутах мапи
    b, _, _ = textbox(232, 400, "Active Record\nтонкий запис", size=13)
    frags.append(b)
    b, _, _ = textbox(540, 300, "Data Mapper\nбагата поведінка", size=13, fill="#eaf0fd")
    frags.append(b)
    b, _, _ = textbox(250, 175, "SQL + Repository\nгарячі запити", size=13, fill="#eafaf0")
    frags.append(b)

    # нагадування про композицію
    frags.append(text(400, 535,
                      "реальні системи — суміш: дефолт + гарячий SQL за одним Repository",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "choice-map.svg"), W, H, *frags,
           title="Мапа вибору доступу")


def fig_timeline_debate():
    """Хронологія суперечки AR ↔ багатий домен (для вставки hist-)."""
    W, H = 1000, 300
    axis_y = 200
    xs = [150, 400, 650, 900]
    frags = [line(95, axis_y, 955, axis_y, color=MUTED, sw=2)]

    beats = [
        (xs[0], ["2002", "Фаулер називає", "Active Record", "(P of EAA)"], "#eef2fb", NEG),
        (xs[1], ["лист. 2003", "«Anemic Domain", "Model» —", "засторога"], "#eef2fb", NEG),
        (xs[2], ["лип. 2004", "Rails: ORM —", "Active Record"], "#eef7f0", FIELD),
        (xs[3], ["груд. 2005", "Rails 1.0 —", "термін у народ"], "#eef7f0", FIELD),
    ]
    cy = 108
    for x, lines, fillc, dotc in beats:
        b, w, h = textbox(x, cy, "\n".join(lines), size=13, fill=fillc)
        frags.append(line(x, cy + h / 2, x, axis_y - 7, color=MUTED, sw=1.4))
        frags.append(b)
        frags.append(circle(x, axis_y, 7, fill=fillc, stroke=dotc, sw=2.4))

    def bracket(x1, x2, color, label):
        y = 234
        return [line(x1, y, x2, y, color=color, sw=2),
                line(x1, 226, x1, y, color=color, sw=2),
                line(x2, 226, x2, y, color=color, sw=2),
                text((x1 + x2) / 2, 256, label, size=12, color=color)]

    frags += bracket(150, 400, NEG, "Фаулер: назвав патерн — і сам застеріг")
    frags += bracket(650, 900, FIELD, "Rails зробив термін щоденним")

    render(os.path.join(IMG, "timeline-debate.svg"), W, H, *frags,
           title="Хронологія: назва, засторога, дефолт")


def fig_test_shapes():
    """Три тести поруч: що мусить торкнутися кожен (жива база / домен / фейк-межа)."""
    W, H = 990, 440
    frags = []

    # вертикальні розділювачі між панелями
    for sx in (330, 660):
        frags.append(line(sx, 46, sx, 416, color=MUTED, sw=1, dash="4,5"))

    def panel(cx, header, target, cap1, cap2, hot):
        col = POS if hot else FIELD
        fillc = "#fdecea" if hot else "#eafaf0"
        out = [text(cx, 58, header, size=15, bold=True)]
        b, _, _ = textbox(cx, 120, "тест", size=13)
        out.append(b)
        out.append(arrow(cx, 150, cx, 238, color=col, sw=2.4))
        b, _, _ = textbox(cx, 300, target, size=13, fill=fillc)
        out.append(b)
        out.append(text(cx, 374, cap1, size=11, color=MUTED))
        out.append(text(cx, 396, cap2, size=11, color=MUTED))
        return out

    frags += panel(165, "Active Record", "жива SQLite",
                   "@pytest.mark.django_db", "без бази ніяк", hot=True)
    frags += panel(495, "Data Mapper", "Device у пам'яті",
                   "без бази —", "чистий домен", hot=False)
    frags += panel(825, "SQL + Repository", "InMemory\nDeviceRepository",
                   "підмінив межу —", "без бази", hot=False)

    render(os.path.join(IMG, "test-shapes.svg"), W, H, *frags)


def fig_n1_trap():
    """N+1: лінивий доступ (1 + N запитів) проти одного JOIN."""
    W, H = 820, 400
    frags = [line(410, 44, 410, 372, color=MUTED, sw=1, dash="4,5")]

    # ── ліворуч: лінивий доступ ──
    frags.append(text(205, 58, "лінивий доступ (Data Mapper)", size=14, bold=True))
    b, _, _ = textbox(150, 105, "SELECT * FROM devices", size=11)
    frags.append(b)
    frags.append(arrow(150, 124, 150, 171))
    b, _, _ = textbox(150, 190, "цикл: d.telemetry", size=11)
    frags.append(b)
    frags.append(arrow(150, 214, 150, 278, color=POS, sw=2.4))
    frags.append(text(190, 250, "× 30", size=13, color=POS, bold=True, anchor="start"))
    b, _, _ = textbox(150, 300, "SQLite", size=12, fill="#eef2f6")
    frags.append(b)
    frags.append(text(150, 356, "1 + 30 = 31 запит", size=15, color=POS, bold=True))

    # ── праворуч: один JOIN ──
    frags.append(text(610, 58, "один JOIN", size=14, bold=True))
    b, _, _ = textbox(610, 150, "SELECT … JOIN telemetry", size=11, fill="#eafaf0")
    frags.append(b)
    frags.append(arrow(610, 176, 610, 278, color=FIELD, sw=2.4))
    b, _, _ = textbox(610, 300, "SQLite", size=12, fill="#eef2f6")
    frags.append(b)
    frags.append(text(610, 356, "1 запит", size=15, color=FIELD, bold=True))

    render(os.path.join(IMG, "n1-trap.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_who_knows_db()
    fig_choice_map()
    fig_timeline_debate()
    fig_test_shapes()
    fig_n1_trap()
    print("OK: who-knows-db.svg, choice-map.svg, timeline-debate.svg, "
          "test-shapes.svg, n1-trap.svg")
