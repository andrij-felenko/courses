# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def promotion_map():
    """Які типи підіймаються й до чого: вузькі → знаковий int; int і ширше — ні."""
    W, H = 720, 400
    f = []
    f.append(text(W / 2, 30, "Просування: що підіймається до int — і чому", size=17, bold=True))

    # Ліва колонка: вузькі типи (підіймаються)
    lx = 60
    f.append(text(lx + 120, 66, "Вужчі за int — ПІДІЙМАЮТЬСЯ", size=13, bold=True, color=INK, anchor="middle"))
    narrow = [
        ("uint8_t  (0…255)", "→ int"),
        ("int8_t   (−128…127)", "→ int"),
        ("uint16_t (0…65535)", "→ int"),
        ("int16_t  (−32768…32767)", "→ int"),
    ]
    y = 92
    for name, arr in narrow:
        f.append(rect(lx, y, 240, 40, fill="#eef7f0", stroke=FIELD, sw=1.5))
        f.append(text(lx + 12, y + 25, name, size=13, color=INK, anchor="start"))
        y += 50

    # Питання-фільтр посередині
    mid = 355
    f.append(fitbox(mid - 75, 150, 150, 88,
                    "Чи влазять\nУСІ значення\nв знаковий int?",
                    size=13, fill="#fff7e6", stroke="#d99a00", bold=True))

    # Стрілки від питання до мети
    f.append(arrow(mid + 77, 172, 545, 130))
    f.append(arrow(mid + 77, 212, 545, 300))

    # Праворуч: два результати
    rx = 550
    f.append(rect(rx, 108, 150, 46, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(fitbox(rx, 108, 150, 46, "так → знаковий int\n(майже завжди)", size=12, fill="#eaf0fd", stroke=NEG, bold=True))

    f.append(rect(rx, 280, 150, 46, fill="#fdecea", stroke=POS, sw=2))
    f.append(fitbox(rx, 280, 150, 46, "ні → unsigned int\n(рідко)", size=12, fill="#fdecea", stroke=POS, bold=True))

    # Внизу: int і ширше — не підіймаються
    f.append(rect(60, 300, 240, 62, fill="#f0f0f0", stroke=MUTED, sw=1.5, rx=6))
    f.append(fitbox(60, 300, 240, 62, "int, unsigned, long, long long\n— уже ≥ int, НЕ підіймаються",
                    size=12, fill="#f0f0f0", stroke=MUTED, color=MUTED))

    render(os.path.join(IMG, "promotion-map.svg"), W, H, *f)


def two_faces():
    """Одне правило — рятує суму, ламає інверсію бітів."""
    W, H = 720, 380
    f = []
    f.append(text(W / 2, 30, "Те саме просування — два наслідки", size=17, bold=True))

    # Ліва половина — РЯТУЄ
    f.append(text(185, 62, "Рятує: сума байтів", size=14, bold=True, color=FIELD))
    lx = 40
    steps_l = [
        "uint8_t 200 + uint8_t 100",
        "у 8 бітах:  300 → 44  (завернулось)",
        "просування → int:  200 + 100",
        "= 300  вміщається — ПРАВДА",
    ]
    y = 84
    for i, s in enumerate(steps_l):
        good = (i == 3)
        col = "#eef7f0" if good else FILL
        stc = FIELD if good else LINE
        f.append(fitbox(lx, y, 300, 44, s, size=12, fill=col, stroke=stc, bold=good))
        if i < len(steps_l) - 1:
            f.append(arrow(lx + 150, y + 46, lx + 150, y + 56))
        y += 68

    # Роздільник
    f.append(line(360, 55, 360, 350, color=MUTED, sw=1.2, dash="4,4"))

    # Права половина — ШКОДИТЬ
    f.append(text(540, 62, "Шкодить: інверсія ~", size=14, bold=True, color=POS))
    rx = 380
    steps_r = [
        "~ над uint8_t 0x5a",
        "у 8 бітах хотіли:  0xa5",
        "просування → int:  0x0000005a",
        "~ інвертує 32 біти:  0xffffffa5",
        "(>> 4, → uint8_t) = 0xfa  ✗",
    ]
    y = 84
    for i, s in enumerate(steps_r):
        bad = (i == 4)
        col = "#fdecea" if bad else FILL
        stc = POS if bad else LINE
        f.append(fitbox(rx, y, 300, 40, s, size=12, fill=col, stroke=stc, bold=bad))
        if i < len(steps_r) - 1:
            f.append(arrow(rx + 150, y + 42, rx + 150, y + 50))
        y += 58

    render(os.path.join(IMG, "two-faces.svg"), W, H, *f)


if __name__ == "__main__":
    promotion_map()
    two_faces()
    print("ok")
