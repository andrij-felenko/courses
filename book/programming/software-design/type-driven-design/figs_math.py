# -*- coding: utf-8 -*-
"""Фігури до математичної вставки «Алгебра типів». Вивід — ./img/*.svg.
Окремий файл, щоб не чіпати figs.py/figs_d.py інших версій статті."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#eafaf1"
RED_FILL = "#fdecea"
BLUE_FILL = "#eaf0fd"


def fig_function_as_table():
    """Функція = заповнена таблиця пошуку: на кожен вхід — незалежний вибір
    виходу, тому кількість функцій = |B| у степені |A|."""
    W, H = 800, 330
    frags = []
    frags.append(text(W / 2, 36, "Функція — це заповнена таблиця пошуку",
                      size=16, bold=True))

    # заголовки колонок
    frags.append(text(110, 84, "вхід з A", size=12, color=MUTED))
    frags.append(text(360, 84, "вихід з B", size=12, color=MUTED))

    # два входи (рядки таблиці)
    frags.append(rect(60, 105, 100, 46, fill=FILL, stroke=INK, sw=1.6))
    frags.append(text(110, 133, "a₁", size=16, color=INK, bold=True))
    frags.append(rect(60, 205, 100, 46, fill=FILL, stroke=INK, sw=1.6))
    frags.append(text(110, 233, "a₂", size=16, color=INK, bold=True))

    # рамка вибору виходу — спільна на обидва рядки
    frags.append(rect(270, 100, 200, 156, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    frags.append(mtext(370, 168, ["обрати один", "із {x, y, z}"],
                       size=15, color=INK, lh=1.4, bold=True))

    # стрілки від входів до рамки вибору (у порожньому просторі, повз написи)
    frags.append(arrow(162, 128, 266, 150, color=INK, sw=1.8))
    frags.append(arrow(162, 228, 266, 206, color=INK, sw=1.8))

    # права панель з підрахунком
    frags.append(rect(520, 100, 250, 156, fill=FILL, stroke=MUTED, sw=1.4))
    frags.append(mtext(645, 138,
                       ["рядків |A| = 2",
                        "у кожному вибір з |B| = 3",
                        "3 · 3 = 3² = 9 функцій",
                        "|A → B| = |B| ^ |A|"],
                       size=13, color=INK, lh=1.7))

    render(os.path.join(IMG, "function-as-table.svg"), W, H, *frags)


def fig_distributivity():
    """Розкладання A×(B+C) ≅ A×B + A×C: спільне поле можна тримати винесеним
    або втягнутим у кожен випадок суми — інформація та сама."""
    W, H = 820, 340
    frags = []
    frags.append(text(W / 2, 36, "Спільне поле можна втягнути в кожен випадок",
                      size=16, bold=True))

    # ── Ліворуч: A × (B + C) — спільне поле + сума ──────────────────────────
    frags.append(text(190, 82, "A × (B + C)", size=16, bold=True))
    frags.append(rect(55, 100, 270, 200, fill=BG, stroke=INK, sw=1.6))
    # спільне поле A
    frags.append(rect(80, 120, 220, 44, fill=GREEN_FILL, stroke=FIELD, sw=1.6))
    frags.append(text(190, 148, "спільне поле A", size=14, color=INK, bold=True))
    # сума B | C
    frags.append(text(190, 194, "вибір: B  або  C", size=12, color=MUTED))
    frags.append(rect(80, 206, 100, 74, fill=FILL, stroke=INK, sw=1.4))
    frags.append(text(130, 248, "B", size=16, color=INK, bold=True))
    frags.append(rect(200, 206, 100, 74, fill=FILL, stroke=INK, sw=1.4))
    frags.append(text(250, 248, "C", size=16, color=INK, bold=True))

    # ── Знак ізоморфізму ───────────────────────────────────────────────────
    frags.append(text(410, 208, "≅", size=34, color=INK, bold=True))

    # ── Праворуч: A×B + A×C — сума двох структур зі втягнутим A ─────────────
    frags.append(text(625, 82, "A×B  +  A×C", size=16, bold=True))
    frags.append(rect(495, 105, 270, 80, fill=BG, stroke=INK, sw=1.6))
    frags.append(rect(512, 120, 110, 50, fill=GREEN_FILL, stroke=FIELD, sw=1.4))
    frags.append(text(567, 150, "A", size=15, color=INK, bold=True))
    frags.append(rect(637, 120, 110, 50, fill=FILL, stroke=INK, sw=1.4))
    frags.append(text(692, 150, "B", size=15, color=INK, bold=True))

    frags.append(text(630, 205, "або", size=12, color=MUTED))

    frags.append(rect(495, 218, 270, 80, fill=BG, stroke=INK, sw=1.6))
    frags.append(rect(512, 233, 110, 50, fill=GREEN_FILL, stroke=FIELD, sw=1.4))
    frags.append(text(567, 263, "A", size=15, color=INK, bold=True))
    frags.append(rect(637, 233, 110, 50, fill=FILL, stroke=INK, sw=1.4))
    frags.append(text(692, 263, "C", size=15, color=INK, bold=True))

    render(os.path.join(IMG, "distributivity.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_function_as_table()
    fig_distributivity()
    print("ok")
