# -*- coding: utf-8 -*-
"""Фігура до вставки «hist-finops-foundation».
Окремий генератор (щоб не змагатися з figs.py статті-власника).
Вивід у ./img/. Імпортує svgkit зі scripts/ (не переписує)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_finops_birth():
    """Хронологія народження FinOps: від оплати за спожите до практики з ім'ям.
    Верхні віхи — про залізо й термін; нижні — про народження практики.
    Кожен підпис — у власній рамці textbox, розставлені з запасом, лінії осі повз написи."""
    W, H = 940, 470
    frags = []
    frags.append(text(W / 2, 34, "Як розрізнені оптимізації стали практикою з ім'ям", size=17, bold=True))

    # Горизонтальна вісь часу
    ax_y = 175
    x0, x1 = 60, W - 40
    frags.append(line(x0, ax_y, x1 - 4, ax_y, color=LINE, sw=2.4))
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                 % (x1, ax_y, x1 - 14, ax_y - 7, x1 - 14, ax_y + 7, LINE))

    # Віхи рівномірно й із запасом по осі; підписи чергуються вгору/вниз, щоб не тіснитися.
    # (частка 0..1, рік, підпис, бік, колір)
    events = [
        (0.00, "2006", "EC2: перша\nмашина\nза годину", "up", FIELD),
        (0.22, "~2012", "Adobe, Intuit:\nрозрізнена\ncost optimization", "down", MUTED),
        (0.46, "2015+", "постачальники:\ncloud financial\nmanagement", "up", NEG),
        (0.68, "лют. 2019", "засновано\nFinOps\nFoundation", "down", POS),
        (0.83, "груд. 2019", "книга\nCloud\nFinOps", "up", NEG),
        (1.00, "черв. 2020", "перехід у\nLinux\nFoundation", "down", FIELD),
    ]

    span = (x1 - x0 - 30)
    for frac, year, label, side, col in events:
        x = x0 + frac * span
        frags.append(circle(x, ax_y, 7, fill=col, stroke=col, sw=1))
        # рік — впритул до осі, з боку, протилежного тексту
        yr_y = ax_y + 24 if side == "up" else ax_y - 14
        frags.append(text(x, yr_y, year, size=12, bold=True, color=col))
        # виносний блок — далеко від осі, у власній рамці
        by = ax_y - 78 if side == "up" else ax_y + 84
        bx, w_, h_ = textbox(x, by, label, size=11, fill=FILL, stroke=col, sw=1.4)
        frags.append(bx)

    # Дві смуги-підписи внизу: дві причини, чому саме тоді
    b1, _, _ = textbox(258, H - 34,
                       "хмара: рахунок — наслідок щоденних рішень інженерів",
                       size=12, fill="#eafaf1", stroke=FIELD, sw=1.4)
    frags.append(b1)
    b2, _, _ = textbox(686, H - 34,
                       "стара модель «купив залізо наперед» перестала працювати",
                       size=12, fill="#fdecea", stroke=POS, sw=1.4)
    frags.append(b2)

    render(os.path.join(IMG, 'finops-birth.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_finops_birth()
    print("OK: finops-birth.svg")
