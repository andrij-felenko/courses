# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Спільний рядок-приклад для обох фігур: дані 1011011 (одиниць п'ять — непарно).
DATA = [1, 0, 1, 1, 0, 1, 1]          # 5 одиниць → непарно
PBIT = sum(DATA) % 2                   # парна парність: добиваємо до парного → P = 1


def bit_cell(x, y, v, w=34, h=34, hot=False):
    """Клітинка з бітом: «1» — червоне, «0» — синє; hot=обведена (перевернутий біт)."""
    col = POS if v else NEG
    stroke = POS if hot else "#cccccc"
    sw = 3.0 if hot else 1.2
    return (rect(x, y, w, h, fill=BG, stroke=stroke, sw=sw, rx=4) +
            text(x + w / 2, y + h / 2 + 5.6, str(v), size=16, color=col, bold=True))


def row_of_bits(bits, x0, y, gap=6, w=34, hot=None):
    """Ряд клітинок; hot — множина індексів перевернутих бітів."""
    hot = hot or set()
    out, x = [], x0
    for i, v in enumerate(bits):
        out.append(bit_cell(x, y, v, w=w, hot=(i in hot)))
        x += w + gap
    return "".join(out), x


# ── 1. parity: як рахується біт парності + перевірка на приймачі ──────────────
def fig_parity():
    W, H = 760, 430
    p = []
    p.append(text(W / 2, 30, "Біт парності: один зайвий біт робить кількість одиниць парною",
                  size=17, bold=True))
    p.append(text(W / 2, 52, "парність = XOR усіх бітів даних; додаємо його — і одиниць стає парне число",
                  size=12.5, color=MUTED, italic=True))

    # ряд: дані + клітинка P
    x0 = 150
    p.append(text(x0 - 14, 121, "дані", size=13, color=INK, anchor="end"))
    frag, xend = row_of_bits(DATA, x0, 100)
    p.append(frag)
    # клітинка парності (виділена зеленим полем)
    px = xend + 20
    p.append(rect(px, 100, 34, 34, fill="#eafaf0", stroke=FIELD, sw=2.6, rx=4))
    p.append(text(px + 17, 121.6, str(PBIT), size=16, color=FIELD, bold=True))
    p.append(text(px + 17, 150, "P", size=12, color=FIELD, bold=True))
    p.append(text(px + 44, 121, "= біт парності", size=12.5, color=FIELD, anchor="start"))

    # підрахунок
    ones = sum(DATA)
    p.append(text(x0 - 14, 198, "лічимо", size=13, color=INK, anchor="end"))
    p.append(text(x0, 198, "одиниць у даних = %d (непарно)" % ones, size=13.5, color=INK, anchor="start"))
    p.append(text(x0, 220, "щоб разом стало ПАРНО, ставимо P = %d" % PBIT,
                  size=13.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(x0, 242, "тепер одиниць = %d — парно (even parity)" % (ones + PBIT),
                  size=13.5, color=FIELD, bold=True, anchor="start"))

    # роздільник + перевірка на приймачі
    p.append(line(60, 300, W - 60, 300, color="#e4e4e4", sw=1.4))
    p.append(text(60, 326, "Приймач рахує одиниці в усіх 8 бітах:", size=13.5, color=INK, bold=True, anchor="start"))
    p.append(text(80, 352, "сума парна  → помилки (однієї) не було", size=13, color=FIELD, anchor="start"))
    p.append(text(80, 374, "сума непарна → один біт перевернувся — кадр битий", size=13, color=POS, anchor="start"))
    p.append(text(80, 402, "Самого P досить, щоб ПОБАЧИТИ помилку, але не щоб знати, ДЕ вона.",
                  size=12.5, color=MUTED, italic=True, anchor="start"))

    render(os.path.join(OUT, "parity.svg"), W, H, *p)


# ── 2. blindspot: 0/1/2 помилки — парність ловить непарне, пропускає парне ────
def fig_blindspot():
    W, H = 760, 440
    p = []
    p.append(text(W / 2, 30, "Сліпа пляма: дві помилки маскують одна одну", size=17, bold=True))
    p.append(text(W / 2, 52, "парність ловить НЕПАРНЕ число помилок (1, 3, 5…) і ПРОПУСКАЄ парне (2, 4…)",
                  size=12.5, color=MUTED, italic=True))

    word = DATA + [PBIT]              # повне слово 8 біт (дані + P)
    x0, gap, w = 210, 6, 32

    def scene(y, label, hot, verdict, ok):
        out = []
        out.append(text(x0 - 16, y + 21, label, size=13, color=INK, bold=True, anchor="end"))
        bits = list(word)
        for i in hot:
            bits[i] ^= 1
        frag, xend = row_of_bits(bits, x0, y, gap=gap, w=w, hot=set(hot))
        out.append(frag)
        col = FIELD if ok else POS
        out.append(text(xend + 12, y + 21, verdict, size=13.5, color=col, bold=True, anchor="start"))
        return "".join(out)

    p.append(scene(100, "0 помилок", [], "сума парна → OK", True))
    p.append(scene(190, "1 помилка", [2], "сума непарна → ВИЯВЛЕНО", True))
    p.append(scene(280, "2 помилки", [2, 6], "сума знову ПАРНА → пропущено", False))

    p.append(text(W / 2, 372, "Перевернути будь-які ДВА біти — і кількість одиниць лишається парною.",
                  size=13, color=POS, bold=True))
    p.append(text(W / 2, 392, "Детектор мовчить, хоча дані зіпсовано.", size=13, color=POS, bold=True))
    p.append(text(W / 2, 418, "Тому парність — для каналів, де помилки рідкі й поодинокі; для пакетних завад її замало.",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "blindspot.svg"), W, H, *p)


if __name__ == "__main__":
    fig_parity()
    fig_blindspot()
    print("OK: parity.svg, blindspot.svg  (P=%d)" % PBIT)
