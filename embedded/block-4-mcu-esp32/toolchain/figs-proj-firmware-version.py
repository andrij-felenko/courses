# -*- coding: utf-8 -*-
"""
Фігури для вставки «Версія всередині прошивки: git-хеш у образі і відтворювана збірка»
(⚙️ вставка до §4.2.4, файл ch21-s4-a-firmware-version.md).

Нумерація: Рис. 4.2.4a.7 і Рис. 4.2.4a.8 (a.1–a.2 — map-файл, a.3–a.6 — запас).
SVG-файли: fig-21-4av-1-inject.svg, fig-21-4av-2-reproducible.svg → ./img/

Запуск: python figs-ch21-s4-a-firmware-version.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ── Рис. 4.2.4a.7 — Шлях ідентичності в образ ────────────────────────────────
def fig_inject():
    """
    Горизонтальний конвеєр: git describe → configure_file → компілятор →
    Flash-образ (FIELD) → старт + лог.
    Усі рамки через fitbox(). Стрілки через arrow().
    """
    W, H = 1060, 310
    ARROW_GAP = 16   # горизонтальний зазор між блоком і стрілкою
    CY = 150         # центр рядка блоків
    BH = 78          # висота кожного блоку

    # Блоки: (x_left, ширина, рядки тексту, fill, stroke)
    # Розбиваємо ширину: 5 блоків + 4 стрілки = 1060 з невеликими полями
    specs = [
        (16,  140, "git describe\n--always\n--dirty --tags",  FILL,    LINE),
        (196, 196, "configure_file\napp_version.h:\n#define APP_GIT_VERSION",
                                                              FILL,    LINE),
        (432, 120, "компілятор:\nрядок\nу .rodata",           FILL,    LINE),
        (592, 186, "Flash-образ:\n.rodata (версія)\nesp_app_desc_t\n{version,date,idf}",
                                                              "#e8f5e9", FIELD),
        (818, 226, "старт:\nesp_ota_get_app_description()\n→ лог «git: a1b2c3d»",
                                                              FILL,    LINE),
    ]

    frags = []
    rights = []
    lefts  = []

    for x, bw, s, bfill, bstroke in specs:
        tcol = FIELD if bstroke == FIELD else INK
        box = fitbox(x, CY - BH / 2, bw, BH, s,
                     size=12, pad=9, fill=bfill, stroke=bstroke, sw=2.0,
                     color=tcol, rx=8)
        frags.append(box)
        rights.append(x + bw)
        lefts.append(x)

    # Стрілки між блоками
    for i in range(len(rights) - 1):
        x1 = rights[i] + 2
        x2 = lefts[i + 1] - 2
        frags.append(arrow(x1, CY, x2, CY, color=LINE, sw=2.0))

    # Підпис внизу
    frags.append(text(W / 2, H - 22,
                      "Ідентичність вкладається у Flash автоматично — людина її не проставляє, тож забути неможливо.",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "fig-21-4av-1-inject.svg"), W, H, *frags,
           title="Рис. 4.2.4a.7. Шлях git-хешу в образ прошивки")
    print("wrote fig-21-4av-1-inject.svg")


# ── Рис. 4.2.4a.8 — Детермінована збірка: чому два білди можуть різнитися ─────
def fig_reproducible():
    """
    Дві колонки: «наївно» (POS) — той самий комміт → різний .bin;
    «детерміновано» (FIELD) — SOURCE_DATE_EPOCH + -ffile-prefix-map → однакові .bin.
    Усі рамки через fitbox()/textbox(). Стрілки через arrow().
    """
    W, H = 940, 460

    COL_L = 230   # центр лівої колонки
    COL_R = 700   # центр правої колонки
    SEP   = (COL_L + COL_R) / 2  # ~465
    TOP   = 52    # верх робочої зони (під заголовком)
    MARGIN = 30   # ліве/праве поле для блоків у колонці

    frags = []

    # ── Заголовки колонок ─────────────────────────────────────────────────────
    frags.append(text(COL_L, TOP, "Наївна збірка", size=15, color=POS, bold=True))
    frags.append(text(COL_L, TOP + 20, "(той самий комміт, два білди)", size=11, color=MUTED, italic=True))

    frags.append(text(COL_R, TOP, "Детермінована збірка", size=15, color=FIELD, bold=True))
    frags.append(text(COL_R, TOP + 20, "(SOURCE_DATE_EPOCH + -ffile-prefix-map)", size=11, color=MUTED, italic=True))

    # ── Спільний вхід: один git-комміт ────────────────────────────────────────
    commit_y_top = TOP + 44
    commit_h = 44
    commit_box = fitbox(W / 2 - 140, commit_y_top, 280, commit_h,
                        "git commit abc123  (той самий код)",
                        size=13, pad=10, fill=FILL, stroke=LINE, sw=1.8, bold=True, rx=7)
    frags.append(commit_box)
    commit_bottom = commit_y_top + commit_h

    # Розгалуження вниз до двох колонок
    split_y = commit_bottom + 18
    frags.append(line(W / 2, commit_bottom + 1, W / 2, split_y, color=LINE, sw=1.6))
    frags.append(line(COL_L, split_y, COL_R, split_y, color=LINE, sw=1.6))
    frags.append(arrow(COL_L, split_y, COL_L, split_y + 22, color=LINE, sw=1.8))
    frags.append(arrow(COL_R, split_y, COL_R, split_y + 22, color=LINE, sw=1.8))

    # ── Ліва колонка: причини недетермінізму ──────────────────────────────────
    causes_y = split_y + 40
    causes_h = 86
    col_w = 380  # ширина блоків у колонці
    causes_box = fitbox(COL_L - col_w / 2, causes_y, col_w, causes_h,
                        "__DATE__ / __TIME__\n(годинник щоразу різний)\nC:\\Users\\...\\file.cpp  (__FILE__ — абс. шлях)",
                        size=12, pad=10, fill="#fdecea", stroke=POS, sw=2.0, color=INK, rx=7)
    frags.append(causes_box)

    arrow_mid_y = causes_y + causes_h + 10
    frags.append(arrow(COL_L, arrow_mid_y, COL_L, arrow_mid_y + 24, color=POS, sw=1.8))

    bins_l_y = arrow_mid_y + 42
    bins_l_h = 70
    bins_l_box = fitbox(COL_L - col_w / 2, bins_l_y, col_w, bins_l_h,
                        "build #1: MD5 = 3f8a…\nbuild #2: MD5 = c91e…\nРІЗНІ .bin!",
                        size=12, pad=10, fill="#fdecea", stroke=POS, sw=2.0, color=POS, bold=True, rx=7)
    frags.append(bins_l_box)

    # ── Права колонка: ліки ───────────────────────────────────────────────────
    fixes_box = fitbox(COL_R - col_w / 2, causes_y, col_w, causes_h,
                       "SOURCE_DATE_EPOCH\n(фіксований час збірки)\n-ffile-prefix-map=$src=.  (шляхи нормалізовано)",
                       size=12, pad=10, fill="#e8f5e9", stroke=FIELD, sw=2.0, color=INK, rx=7)
    frags.append(fixes_box)

    frags.append(arrow(COL_R, arrow_mid_y, COL_R, arrow_mid_y + 24, color=FIELD, sw=1.8))

    bins_r_box = fitbox(COL_R - col_w / 2, bins_l_y, col_w, bins_l_h,
                        "build #1: MD5 = 7b4d…\nbuild #2: MD5 = 7b4d…\nОДНАКОВІ .bin!",
                        size=12, pad=10, fill="#e8f5e9", stroke=FIELD, sw=2.0, color=FIELD, bold=True, rx=7)
    frags.append(bins_r_box)

    # ── Розділювач між колонками ──────────────────────────────────────────────
    sep_top = TOP + 36
    sep_bot = bins_l_y + bins_l_h + 8
    frags.append(line(SEP, sep_top, SEP, sep_bot, color="#cccccc", sw=1.2, dash="6,4"))

    # ── Підсумок внизу ────────────────────────────────────────────────────────
    footer_y = sep_bot + 18
    footer_box = fitbox(50, footer_y, W - 100, 40,
                        "Однаковий вхід → однаковий хеш лише коли збірка детермінована (зв'язок із вставкою про контрольні суми §4.2.4m).",
                        size=12, pad=9, fill=FILL, stroke=LINE, sw=1.4, rx=7)
    frags.append(footer_box)

    render(os.path.join(OUT, "fig-21-4av-2-reproducible.svg"), W, H, *frags,
           title="Рис. 4.2.4a.8. Детермінована збірка: чому однаковий код може дати різний .bin")
    print("wrote fig-21-4av-2-reproducible.svg")


if __name__ == "__main__":
    fig_inject()
    fig_reproducible()
