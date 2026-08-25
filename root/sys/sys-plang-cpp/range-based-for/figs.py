# -*- coding: utf-8 -*-
"""Фігури до теми «Цикл for за діапазоном і в що він розгортається»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_expansion():
    """Що компілятор пише замість циклу за діапазоном."""
    W, H = 1020, 470
    f = []

    f.append(text(230, 52, "що пише програміст", size=13, color=MUTED))
    f.append(text(775, 52, "у що це розгортається", size=13, color=MUTED))

    # ── ліва панель: вихідний запис ────────────────────────────────────────
    f.append(rect(30, 64, 400, 150, fill="#ffffff", stroke=MUTED, sw=1.2))
    src = ["for (auto& item : basket)",
           "{",
           "    total += item.price;",
           "}"]
    for i, ln in enumerate(src):
        f.append(text(52, 100 + i * 28, ln, size=15, anchor="start", bold=(i == 0)))

    # ── права панель: розгортання ──────────────────────────────────────────
    f.append(rect(560, 64, 430, 300, fill="#ffffff", stroke=MUTED, sw=1.2))
    exp = ["{",
           "  auto&& __range = basket;",
           "  auto __begin = __range.begin();",
           "  auto __end   = __range.end();",
           "  for ( ; __begin != __end; ++__begin)",
           "  {",
           "    auto& item = *__begin;",
           "    total += item.price;",
           "  }",
           "}"]
    for i, ln in enumerate(exp):
        f.append(text(578, 96 + i * 28, ln, size=14, anchor="start"))

    # ── зв'язки ────────────────────────────────────────────────────────────
    f.append(arrow(438, 100, 552, 124, color=NEG))
    f.append(arrow(438, 156, 552, 292, color=NEG))

    f.append(mtext(510, 400,
                   ["Діапазон обчислюють один раз, кінець — теж один раз,",
                    "а змінна циклу народжується заново на кожному кроці."],
                   size=13, color=MUTED))

    render(os.path.join(OUT, 'expansion.svg'), W, H, *f,
           title="Цикл за діапазоном — правило переписування, а не окремий вид циклу")


def fig_begin_end_choice():
    """Три шляхи, якими компілятор шукає begin і end."""
    W, H = 1000, 440
    f = []

    f.append(textbox(500, 74, "тип виразу-діапазону", size=15, bold=True, min_w=260)[0])

    cols = [
        (170, "масив T[N]",
              "__range\n__range + N"),
        (500, "клас, де знайдено ОБИДВА\nімені-члени begin і end",
              "__range.begin()\n__range.end()"),
        (830, "усе інше",
              "begin(__range)\nend(__range)\nпошук лише за ADL"),
    ]
    for cx, cond, res in cols:
        f.append(textbox(cx, 176, cond, size=13.5, fill="#eef3f8")[0])
        f.append(textbox(cx, 288, res, size=13.5, bold=True, fill="#f4f6f8")[0])
        f.append(arrow(500, 98, cx, 148, color=MUTED))
        f.append(arrow(cx, 206, cx, 254, color=NEG))

    f.append(mtext(500, 372,
                   ["Перевірка йде зліва направо: спрацював варіант — решту не розглядають.",
                    "Знайдено лише одне з двох імен-членів — члени не беруть узагалі (з C++20)."],
                   size=13, color=MUTED))

    render(os.path.join(OUT, 'begin-end-choice.svg'), W, H, *f,
           title="Звідки компілятор бере begin і end")


def fig_temporary_lifetime():
    """Тимчасовий об'єкт усередині виразу-діапазону."""
    W, H = 1020, 430
    f = []

    f.append(text(510, 62, "for (auto& s : load_config().sections())", size=16, bold=True))

    gx = [270, 500, 920]
    for x in gx:
        f.append(line(x, 96, x, 306, color=MUTED, sw=1.1, dash="4 4"))

    # ── рядок 1: до C++23 ──────────────────────────────────────────────────
    f.append(text(248, 158, "до C++23", size=14, anchor="end", bold=True))
    f.append(rect(270, 138, 230, 36, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(385, 162, "Config живий", size=13.5, color=POS))
    f.append(line(500, 156, 916, 156, color=POS, sw=1.6, dash="6 5"))
    f.append(text(710, 128, "s посилається в нікуди", size=13, color=POS))

    # ── рядок 2: з C++23 ───────────────────────────────────────────────────
    f.append(text(248, 258, "з C++23", size=14, anchor="end", bold=True))
    f.append(rect(270, 238, 650, 36, fill="#eaf7ee", stroke=FIELD, sw=1.5))
    f.append(text(700, 262, "Config живий увесь цикл", size=13.5, color=FIELD))

    labels = [(270, "вираз обчислено"), (500, "кінець повного виразу"), (920, "кінець циклу")]
    for x, s in labels:
        f.append(text(x, 332, s, size=13, color=MUTED))

    f.append(mtext(510, 384,
                   ["До C++23 життя продовжували лише результату всього виразу, а не тимчасовим усередині нього.",
                    "P2718R0 поширив продовження на всі тимчасові об'єкти виразу-діапазону."],
                   size=13, color=MUTED))

    render(os.path.join(OUT, 'temporary-lifetime.svg'), W, H, *f,
           title="Тимчасовий об'єкт усередині виразу-діапазону")


def fig_split_windows():
    """Вставка proj: piece_ і rest_ — вікна в один буфер, без виділення пам'яті."""
    W, H = 960, 452
    f = []

    f.append(text(480, 42, 'std::string_view text = "usr:bin:opt";', size=15, bold=True))

    X0, CW, TOP = 210, 44, 66
    chars = list("usr:bin:opt")
    for i, ch in enumerate(chars):
        sep = (ch == ':')
        f.append(rect(X0 + i * CW, TOP, CW, 38,
                      fill="#fdecea" if sep else "#ffffff",
                      stroke=MUTED, sw=1.0, rx=0))
        f.append(text(X0 + i * CW + CW / 2.0, TOP + 26, ch, size=16,
                      color=POS if sep else INK, bold=sep))
    f.append(text(196, TOP + 26, "буфер", size=13, color=MUTED, anchor="end"))

    steps = [
        (0, 3, 4, 11, '*it = "usr"'),
        (4, 7, 8, 11, '*it = "bin"'),
        (8, 11, None, None, '*it = "opt"'),
    ]
    for k, (pa, pb, ra, rb, note) in enumerate(steps):
        cy = 168 + k * 74
        f.append(text(196, cy + 5, "крок %d" % (k + 1), size=13,
                      color=MUTED, anchor="end"))
        px, pw = X0 + pa * CW, (pb - pa) * CW
        f.append(rect(px, cy - 16, pw, 32, fill="#eaf7ee", stroke=FIELD, sw=1.5))
        f.append(text(px + pw / 2.0, cy + 5, "piece_", size=13, color=FIELD, bold=True))
        if ra is not None:
            rx, rw = X0 + ra * CW, (rb - ra) * CW
            f.append(rect(rx, cy - 16, rw, 32, fill="#eaf0fd", stroke=NEG, sw=1.5))
            f.append(text(rx + rw / 2.0, cy + 5, "rest_", size=13, color=NEG))
        else:
            f.append(text(550, cy + 5, "rest_ вичерпано →", size=13,
                          color=MUTED, anchor="end"))
        f.append(text(710, cy + 5, note, size=13, anchor="start", bold=True))

    f.append(mtext(480, 396,
                   ["Жодного нового байта: piece_ і rest_ — пари «покажчик + довжина» в той самий буфер.",
                    "Коли роздільника більше немає, more_ гасне; наступний ++ виставляє finished_ — і вартовий каже «кінець»."],
                   size=13, color=MUTED))

    render(os.path.join(OUT, 'split-windows.svg'), W, H, *f,
           title="Розбиття рядка вікнами: стан ітератора на кожному кроці")


if __name__ == '__main__':
    fig_expansion()
    fig_begin_end_choice()
    fig_temporary_lifetime()
    fig_split_windows()
    print('ok')
