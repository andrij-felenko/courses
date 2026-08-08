# -*- coding: utf-8 -*-
"""Фігури до теми «constexpr і consteval: обчислення під час компіляції»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Одна функція, два шляхи — обирає контекст, не ключове слово ──────────
def fig_two_paths():
    W, H = 1020, 545
    f = []

    f.append(fitbox(310, 40, 400, 56,
                    "constexpr int square(int x) { return x * x; }",
                    size=13, bold=True))

    f.append(arrow(430, 98, 250, 148))
    f.append(arrow(590, 98, 770, 148))

    # лівий шлях — контекст вимагає сталої
    f.append(fitbox(40, 156, 320, 64,
                    "контекст вимагає сталої\nstatic_assert(square(7) == 49)", size=12))
    f.append(arrow(200, 222, 200, 266))
    f.append(fitbox(40, 272, 320, 64,
                    "обчислювач сталих\nусередині компілятора", size=13,
                    fill="#e8f6ee", stroke=FIELD, bold=True))
    f.append(arrow(200, 338, 200, 382))
    f.append(fitbox(40, 388, 320, 56, "у код лягає готове 49", size=12))

    # правий шлях — звичайний контекст
    f.append(fitbox(660, 156, 320, 64,
                    "звичайний контекст\nint m = square(n);", size=12))
    f.append(arrow(820, 222, 820, 266))
    f.append(fitbox(660, 272, 320, 64,
                    "звичайна функція\nв машинному коді", size=13,
                    fill="#eaf0fd", stroke=NEG, bold=True))
    f.append(arrow(820, 338, 820, 382))
    f.append(fitbox(660, 388, 320, 56, "множення в час виконання", size=12))

    f.append(mtext(510, 482,
                   ["Шлях обирає не ключове слово, а місце виклику.",
                    "Правий шлях оптимізатор теж може згорнути — але це вже правило «ніби»,",
                    "а не обіцянка мови."],
                   size=11, color=MUTED, lh=1.5))

    render(os.path.join(OUT, 'two-paths.svg'), W, H, *f,
           title="Один і той самий constexpr обчислюється або компілятором, або процесором")


# ── 2. Герметичність сталого обчислення ────────────────────────────────────
def fig_sealed_box():
    W, H = 1020, 530
    f = []

    # серцевина
    f.append(rect(340, 88, 340, 202, fill="#e8f6ee", stroke=FIELD, sw=2.5))
    f.append(text(510, 124, "СТАЛЕ ОБЧИСЛЕННЯ", size=14, color=FIELD, bold=True))
    f.append(mtext(510, 162,
                   ["результат залежить лише від",
                    "аргументів і від того,",
                    "що створене тут-таки"],
                   size=12, color=INK, lh=1.5))

    # що входить
    f.append(fitbox(40, 100, 250, 52, "аргументи-сталі", size=12))
    f.append(fitbox(40, 170, 250, 52, "літерали й constexpr-змінні", size=12))
    f.append(fitbox(40, 240, 250, 52, "об'єкти, створені всередині", size=12))
    for y in (126, 196, 266):
        f.append(arrow(296, y, 334, y))

    # що виходить
    f.append(arrow(686, 190, 762, 190))
    f.append(fitbox(770, 164, 210, 52, "одне значення", size=13, bold=True))

    # що обчислення зупиняє
    f.append(rect(40, 344, 940, 136, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(510, 376, "Що зупиняє стале обчислення", size=13, color=POS, bold=True))
    f.append(mtext(72, 412,
                   ["• читання змінної, яка живе лише в час виконання",
                    "• ввід-вивід і будь-який системний виклик"],
                   size=12, color=INK, anchor="start", lh=1.9))
    f.append(mtext(536, 412,
                   ["• пам'ять із new, не звільнена до кінця обчислення",
                    "• невизначена поведінка — тут це помилка збірки"],
                   size=12, color=INK, anchor="start", lh=1.9))

    render(os.path.join(OUT, 'sealed-box.svg'), W, H, *f,
           title="Стале обчислення замкнене: усе, чого воно торкається, або аргумент, або створене всередині")


# ── 3. Чотири слова, які плутають ──────────────────────────────────────────
def fig_four_words():
    W, H = 1010, 424
    f = []

    XL, WL = 40, 250
    XC = [306, 532, 758]
    WC = 210

    heads = ["Коли обчислюється", "Якщо сталою\nне виходить", "Чи стає\nнезмінним"]
    for x, s in zip(XC, heads):
        f.append(fitbox(x, 36, WC, 76, s, size=12, color=MUTED,
                        fill="#ffffff", stroke=MUTED))

    rows = [
        ("constexpr\nна змінній",
         ["до запуску, завжди", "помилка компіляції", "так"], False),
        ("constexpr\nна функції",
         ["залежить від контексту", "звичайний виклик", "ні"], True),
        ("consteval\nна функції",
         ["до запуску, завжди", "помилка компіляції", "ні"], False),
        ("constinit\nна змінній",
         ["до запуску, завжди", "помилка компіляції", "ні"], False),
    ]

    y = 122
    for label, cells, soft in rows:
        f.append(fitbox(XL, y, WL, 58, label, size=12, bold=True))
        style = dict(fill="#e8f6ee", stroke=FIELD) if soft else dict()
        for x, s in zip(XC, cells):
            f.append(fitbox(x, y, WC, 58, s, size=12, **style))
        y += 66

    render(os.path.join(OUT, 'four-words.svg'), W, H, *f,
           title="constexpr, consteval і constinit: що кожне слово вимагає")


# ── 4. Скільки копій таблиці лишається в бінарнику ─────────────────────────
def fig_inline_table():
    W, H = 1020, 402
    f = []

    def panel(x0, title, header, cell, summary, tone):
        w = 460
        f.append(fitbox(x0, 30, w, 44, title, size=13, bold=True,
                        fill="#ffffff", stroke=tone, color=tone))
        f.append(fitbox(x0 + 60, 92, w - 120, 58, header, size=11))
        # три одиниці трансляції
        bw, gap = 136, 20
        xs = [x0 + 6 + i * (bw + gap) for i in range(3)]
        for x in xs:
            f.append(arrow(x + bw / 2, 152, x + bw / 2, 190))
        for x, s in zip(xs, cell):
            f.append(fitbox(x, 196, bw, 58, s, size=11))
        for x in xs:
            f.append(arrow(x + bw / 2, 256, x + bw / 2, 292))
        f.append(fitbox(x0 + 30, 298, w - 60, 62, summary, size=12, bold=True,
                        fill="#f4f6f8", stroke=tone))

    panel(40, "Без inline — прихована копія в кожній .o",
          "crc32.hpp\nconstexpr auto crc32_table = …",
          ["main.o\n1 КіБ, символ r", "net.o\n1 КіБ, символ r", "log.o\n1 КіБ, символ r"],
          "три різні локальні символи —\nлінкер не має права їх злити: 3 КіБ",
          POS)

    panel(520, "inline constexpr — одна копія на програму",
          "crc32.hpp\ninline constexpr auto crc32_table = …",
          ["main.o\nслабкий символ V", "net.o\nслабкий символ V", "log.o\nслабкий символ V"],
          "усі копії в одній COMDAT-групі —\nлінкер лишає одну: 1 КіБ",
          FIELD)

    render(os.path.join(OUT, 'inline-table-copies.svg'), W, H, *f,
           title="Одна й та сама constexpr-таблиця: три копії без inline і одна з ним")


if __name__ == '__main__':
    fig_two_paths()
    fig_sealed_box()
    fig_four_words()
    fig_inline_table()
    print("ok")
