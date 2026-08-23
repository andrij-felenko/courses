# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER = "#e08a1e"


def fig_weld():
    """v0: читання, рішення й дія зварені в один процес; поріг зашитий; цикл-полінг."""
    W, H = 820, 300
    frags = []

    fx, fy, fw, fh = 210, 76, 400, 150
    frags.append(rect(fx, fy, fw, fh, fill="#fbfcfd", stroke=INK, sw=2))
    frags.append(text(fx + fw / 2, 62, "один процес · один файл", size=14, bold=True, color=MUTED))

    # три зварені стадії всередині
    frags.append(fitbox(226, 116, 104, 64, "читати\nдавач", size=13))
    frags.append(fitbox(350, 116, 120, 64, "вирішити\nt < 20°", size=13, stroke=POS, fill="#fdecea"))
    frags.append(fitbox(490, 116, 104, 64, "діяти\nрозетка", size=13))
    frags.append(arrow(330, 148, 350, 148))
    frags.append(arrow(470, 148, 490, 148))
    frags.append(text(410, 202, "поріг зашитий у коді", size=11, color=POS))

    # давач і обігрівач — поза процесом
    frags.append(fitbox(60, 118, 110, 60, "давач t°", size=13, fill="#eef2f6"))
    frags.append(arrow(170, 148, 226, 148))
    frags.append(fitbox(650, 118, 120, 60, "обігрівач", size=13, fill="#eef2f6"))
    frags.append(arrow(594, 148, 650, 148))

    # цикл-полінг: act -> зачекати -> read знову
    frags.append(line(542, 180, 542, 250))
    frags.append(line(542, 250, 278, 250))
    frags.append(arrow(278, 250, 278, 182))
    frags.append(text(410, 270, "кожні 30 с — опитати знову", size=12, color=MUTED))

    render(os.path.join(OUT, 'v0-weld.svg'), W, H, *frags)


def fig_cost():
    """Ті самі зміни, вишикувані за тим, як далеко розходиться правка."""
    W, H = 900, 340
    frags = []
    frags.append(text(W / 2, 30, "Ціна зміни в v0 — не однакова", size=16, bold=True))
    frags.append(text(330, 54, "як далеко розходиться правка →", size=12, anchor="start", color=MUTED))

    rows = [
        ("«поріг 20 → 22°»", 40, FIELD, "один рядок"),
        ("«поріг удень / уночі»", 84, FIELD, "кілька рядків, той самий файл"),
        ("«другий датчик у спальні»", 200, AMBER, "ламає «датчик рівно один»"),
        ("«сповіщати, а не гріти»", 250, AMBER, "read→decide→act зварені"),
        ("«інший вендор давача»", 300, POS, "драйвер вплетений у логіку"),
    ]
    y0, rh = 92, 50
    label_r, bar_x, ann_x = 310, 330, 650
    for i, (lab, blen, col, ann) in enumerate(rows):
        cy = y0 + i * rh
        frags.append(text(label_r, cy + 5, lab, size=13, anchor="end"))
        frags.append(rect(bar_x, cy - 11, blen, 26, fill=col, stroke=LINE, sw=1, rx=4))
        frags.append(text(ann_x, cy + 5, ann, size=12, anchor="start", color=MUTED))

    render(os.path.join(OUT, 'change-cost.svg'), W, H, *frags)


def fig_blast():
    """Куди дістає кожна правка: 4 зміни × 5 ділянок файлу.
    Зафарбована клітина — правка торкається ділянки. Зелений рядок —
    зміна лягає в форму (той самий файл, структура ціла); червоні —
    розповзаються або тихо ламають."""
    W, H = 940, 430
    gx, cw = 178, 148            # ліва межа сітки, ширина колонки
    gy0, rh = 98, 76             # верх сітки, висота рядка
    frags = []

    cols = [
        ["поріг", "константа"],
        ["цикл", "форма"],
        ["рішення", "t < поріг"],
        ["read_sensor", "драйвер"],
        ["heater on/off", "драйвер"],
    ]
    # (підпис рядка, чи-лягає-в-форму, [торкання по 5 колонках])
    rows = [
        (["нічний", "поріг"],     True,  [1, 0, 1, 0, 0]),
        (["другий", "давач"],     False, [1, 1, 1, 1, 1]),
        (["сповіщати,", "не гріти"], False, [0, 1, 1, 0, 1]),
        (["інший", "вендор"],     False, [0, 0, 1, 1, 0]),
    ]

    # заголовки колонок (над сіткою, без рамок)
    for i, lab in enumerate(cols):
        cx = gx + (i + 0.5) * cw
        frags.append(mtext(cx, 62, lab, size=13, bold=True, color=MUTED, lh=1.25))

    # горизонтальні лінії сітки
    for r in range(len(rows) + 1):
        y = gy0 + r * rh
        frags.append(line(gx, y, gx + 5 * cw, y, color=LINE, sw=1.2))
    # вертикальні лінії сітки
    for i in range(6):
        x = gx + i * cw
        frags.append(line(x, gy0, x, gy0 + len(rows) * rh, color=LINE, sw=1.2))

    # рядки: підпис ліворуч + маркери в клітинах
    for r, (lab, fits, hits) in enumerate(rows):
        cy = gy0 + (r + 0.5) * rh
        frags.append(mtext(90, cy - 8, lab, size=14, bold=True,
                           color=(FIELD if fits else POS), lh=1.25))
        col = FIELD if fits else POS
        for i, hit in enumerate(hits):
            ccx = gx + (i + 0.5) * cw
            if hit:
                frags.append(circle(ccx, cy, 15, fill=col, stroke=INK, sw=1.3))
            else:
                frags.append(circle(ccx, cy, 4, fill="#dfe3e8", stroke="#dfe3e8", sw=1))

    render(os.path.join(OUT, 'blast-radius.svg'), W, H, *frags,
           title="Куди дістає правка: одна вимога — скільки ділянок файлу")


if __name__ == '__main__':
    fig_weld()
    fig_cost()
    fig_blast()
    print("figures written to", OUT)
