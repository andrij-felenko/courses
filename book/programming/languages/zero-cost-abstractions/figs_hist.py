# -*- coding: utf-8 -*-
# Фігури для hist-вставки (окремий файл, щоб не конфліктувати з figs.py).
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── two-worlds: дві школи 1980-х сходяться в C with Classes ───────────────────
def fig_two_worlds():
    W, H = 760, 404
    p = []
    # ліворуч — світ Simula (абстракція)
    p.append(rect(40, 60, 320, 152, fill="#f3faf4", stroke=FIELD, sw=2, rx=10))
    p.append(text(200, 86, "світ Simula (1967)", size=14, color=FIELD, bold=True))
    p.append(text(200, 106, "абстракція", size=11, color=MUTED, italic=True))
    for i, s in enumerate(["класи, об'єкти, успадкування",
                           "віртуальні методи",
                           "+ виражальність",
                           "− прихована ціна виконання"]):
        col = FIELD if s.startswith("+") else (POS if s.startswith("−") else INK)
        p.append(text(200, 132 + i * 19, s, size=10.5, color=col, bold=s[0] in "+−"))

    # праворуч — світ C (метал)
    p.append(rect(400, 60, 320, 152, fill=FILL, stroke=NEG, sw=2, rx=10))
    p.append(text(560, 86, "світ C (1972)", size=14, color=NEG, bold=True))
    p.append(text(560, 106, "метал", size=11, color=MUTED, italic=True))
    for i, s in enumerate(["точний контроль над машиною",
                           "рядок → кілька інструкцій",
                           "+ передбачувана швидкість",
                           "− жодних розкошів"]):
        col = FIELD if s.startswith("+") else (POS if s.startswith("−") else INK)
        p.append(text(560, 132 + i * 19, s, size=10.5, color=col, bold=s[0] in "+−"))

    # донизу сходяться в C with Classes
    p.append(arrow(200, 216, 355, 270, color=INK, sw=1.8))
    p.append(arrow(560, 216, 405, 270, color=INK, sw=1.8))
    p.append(rect(228, 274, 304, 58, fill="#eafaf0", stroke=FIELD, sw=2.2, rx=10))
    p.append(text(380, 298, "C with Classes (1979) → C++", size=13, color="#1a1a1a", bold=True))
    p.append(text(380, 318, "виражальність зліва за ціною справа", size=10, color=INK))

    # правило, що втримало поєднання
    p.append(arrow(380, 334, 380, 358, color=FIELD, sw=2.4))
    p.append(text(380, 380, "правило нульових витрат — щоб не сповзти до повільного",
                  size=10.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "two-worlds.svg"), W, H, *p,
           title="Дві школи 1980-х і спроба їх поєднати")


if __name__ == "__main__":
    fig_two_worlds()
    print("OK: hist figure written to", OUT)
