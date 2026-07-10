# -*- coding: utf-8 -*-
"""Фігури до кроку «Перше рев'ю» (dh-v0-scenario-audit).
Дві фігури: (1) прогін сценаріїв крізь структуру v0; (2) карта пріоритету знахідок."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#e8f6ee"
RED_FILL = "#fdecea"


# ── Фігура 1: прогін сценаріїв крізь структуру ──────────────────────────────
def fig_walk():
    W, H = 880, 450
    rows = [
        # (сценарій, вердикт-рядки, is_risk)
        ("Хмара лягла —\nдім гріє далі", "не-ризик\nусе локально", False),
        ("Реакція\nза < 100 мс", "не-ризик\nодин локальний цикл", False),
        ("Змінити поріг чи\nдодати давач", "РИЗИК R1\nправка б'є робочий цикл", True),
        ("Давач завис\nна 20 °C", "РИЗИК R2\nсліпа довіра даним", True),
    ]
    ys = [105, 190, 275, 360]
    frags = []

    # центральна структура v0
    bx, by, bw, bh = 330, 82, 180, 300
    frags.append(rect(bx, by, bw, bh, fill=FILL, stroke=INK, sw=2))
    frags.append(mtext(bx + bw / 2, by + bh / 2 - 6,
                       ["DH v0", "один файл", "на хабі"], size=14, bold=True))

    for (scen, verdict, is_risk), y in zip(rows, ys):
        col = POS if is_risk else FIELD
        vfill = RED_FILL if is_risk else GREEN_FILL
        # сценарій зліва
        frags.append(fitbox(20, y - 26, 250, 52, scen, size=13))
        # стрілка сценарій → структура
        frags.append(arrow(270, y, bx, y, color=LINE, sw=1.8))
        # стрілка структура → вердикт (кольором вердикту)
        frags.append(arrow(bx + bw, y, 590, y, color=col, sw=2.0))
        # вердикт праворуч
        frags.append(fitbox(590, y - 26, 270, 52, verdict, size=13,
                            fill=vfill, stroke=col, color=INK, bold=True))

    render(os.path.join(IMG, 'audit-walk.svg'), W, H, *frags,
           title="Рев'ю — це прогін: сценарій крізь структуру")


# ── Фігура 2: карта пріоритету знахідок ─────────────────────────────────────
def fig_rank():
    W, H = 760, 560
    x0, x1 = 90, 680          # plot X
    y0, y1 = 70, 470          # plot Y (y0 — верх)
    midx = (x0 + x1) / 2
    midy = (y0 + y1) / 2
    frags = []

    # зони: верх-право (лагодити), низ-право (берегти)
    frags.append(rect(midx, y0, x1 - midx, midy - y0, fill=RED_FILL, stroke="none", rx=0))
    frags.append(rect(midx, midy, x1 - midx, y1 - midy, fill=GREEN_FILL, stroke="none", rx=0))
    # рамка + осьові пунктири
    frags.append(rect(x0, y0, x1 - x0, y1 - y0, fill="none", stroke=LINE, sw=1.5, rx=0))
    frags.append(line(midx, y0, midx, y1, color=MUTED, sw=1, dash="5,4"))
    frags.append(line(x0, midy, x1, midy, color=MUTED, sw=1, dash="5,4"))

    def px(fx, fy):
        return x0 + fx * (x1 - x0), y1 - fy * (y1 - y0)

    # точки: (важливість, провал), колір, підпис, підпис-зверху?
    pts = [
        (0.82, 0.85, POS, "R1 змінюваність", True),
        (0.70, 0.60, POS, "R2 надійність давача", True),
        (0.85, 0.18, FIELD, "N1 офлайн", False),
        (0.58, 0.20, FIELD, "N2 швидкодія", False),
    ]
    for fx, fy, col, lab, above in pts:
        cx, cy = px(fx, fy)
        frags.append(circle(cx, cy, 11, fill=col, stroke=INK, sw=1.5))
        ly = cy - 22 if above else cy + 30
        frags.append(text(cx, ly, lab, size=13, color=INK, bold=True))

    # підписи осей
    frags.append(text(midx, y1 + 40, "Важливість сценарію (з дерева корисності)  →",
                     size=13, color=MUTED))
    frags.append('<text x="34" y="%.0f" transform="rotate(-90 34 %.0f)" '
                 'font-family="%s" font-size="13" fill="%s" text-anchor="middle">'
                 'Наскільки погано v0 провалює  →</text>' % (midy, midy, FONT, MUTED))

    render(os.path.join(IMG, 'risk-rank.svg'), W, H, *frags,
           title="Знахідки рев'ю на карті пріоритету")


# ── Фігура 3: сценарій (6 частин) ↔ тест (arrange/act/assert) ────────────────
def fig_scenario_to_test():
    W, H = 940, 500
    frags = []

    # заголовки колонок
    frags.append(text(170, 66, "Сценарій — 6 частин", size=15, bold=True))
    frags.append(text(770, 66, "Тест (pytest)", size=15, bold=True))

    # ліва колонка: 6 частин, згруповані по 3-1-2
    lx, lw = 40, 260
    left = [
        ("Джерело", "хто дає стимул"),
        ("Стимул", "що коїться"),
        ("Середовище", "у яких умовах"),
        ("Артефакт", "що саме випробуємо"),
        ("Відповідь", "як має повестися"),
        ("Міра", "число-межа"),
    ]
    lys = [90, 148, 206, 272, 336, 394]     # проміжок після 3-ї (розрив груп)
    for (head, sub), y in zip(left, lys):
        frags.append(fitbox(lx, y, lw, 48, head + "\n" + sub, size=12))

    # права колонка: 3 частини тесту, кожна проти своєї групи
    rx, rw = 620, 280
    right = [
        (108, 132, ["Підготувати (arrange)",
                    "monkeypatch давача,",
                    "вбити мережу, лічильник тиків"]),
        (272,  48, ["Діяти (act)", "hub.step()"]),
        (318, 124, ["Перевірити (assert)",
                    "assert — і є число,",
                    "що тримається або падає"]),
    ]
    for ry, rh, lines in right:
        frags.append(fitbox(rx, ry, rw, rh, "\n".join(lines), size=13, bold=True))

    # згруповані стрілки: центр групи ліворуч → центр блоку праворуч
    for gy, ry, rh in [(172, 108, 132), (296, 272, 48), (375, 318, 124)]:
        frags.append(arrow(lx + lw, gy, rx - 2, ry + rh / 2, color=LINE, sw=1.8))

    render(os.path.join(IMG, 'scenario-to-test.svg'), W, H, *frags,
           title="Сценарій і тест — одна фігура")


# ── Фігура 4: сліпа пляма зеленого тесту латентності ────────────────────────
def fig_latency_blindspot():
    W, H = 900, 300
    frags = []

    # два кроки рішення (зелені, мікросекундні) — самі й формують вісь часу
    for bx in (70, 752):
        frags.append(rect(bx, 118, 64, 64, fill=GREEN_FILL, stroke=FIELD, sw=2))
        frags.append(mtext(bx + 32, 140, ["step()", "≈0.02 мс"], size=10, bold=True))

    # пауза між читаннями — те, що тест НЕ міряє
    frags.append(rect(138, 126, 610, 48, fill="#f6f7f9", stroke=MUTED, sw=1))
    frags.append(text(443, 154, "пауза 30 000 мс між читаннями — цього тест НЕ міряє",
                      size=13, color=MUTED))

    # подія в кімнаті (клац вимикача) чекає обробки аж до наступного читання
    frags.append(circle(300, 100, 7, fill=RED_FILL, stroke=POS, sw=2))
    frags.append(text(300, 84, "подія (клац вимикача)", size=12, color=POS, bold=True))
    frags.append(arrow(300, 108, 300, 124, color=POS, sw=1.6))

    frags.append(text(784, 226, "оброблено аж тут", size=11, color=POS, bold=True))
    frags.append(arrow(784, 205, 784, 186, color=POS, sw=1.6))

    frags.append(text(450, 262,
                      "Зелений тест бачить лише крок рішення; 30 с очікування — його сліпа пляма.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'latency-blindspot.svg'), W, H, *frags,
           title="Що зелений тест латентності не бачить")


if __name__ == "__main__":
    fig_walk()
    fig_rank()
    fig_scenario_to_test()
    fig_latency_blindspot()
    print("ok:", os.listdir(IMG))
