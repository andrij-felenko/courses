import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_sched_deadline():
    path = os.path.join(os.path.dirname(__file__), 'img', 'sched-deadline.svg')
    os.makedirs(os.path.dirname(path), exist_ok=True)

    w, h = 840, 380
    frags = []

    # Title
    frags.append(text(w / 2, 28, "Поведінка SCHED_DEADLINE: Бюджет CBS та дедлайн EDF", size=16, bold=True))

    # Time Axis
    frags.append(line(50, 240, 780, 240, color=LINE, sw=2))
    frags.append(arrow(760, 240, 780, 240, color=LINE, sw=2))
    frags.append(text(770, 260, "Час (t)", size=13, color=MUTED, anchor="start"))

    # Period 1 markers
    frags.append(line(60, 80, 60, 250, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(60, 270, "t = 0 (Прибуття)", size=12, anchor="middle"))

    # Execution block (Runtime Q = 10ms)
    frags.append(fitbox(60, 120, 150, 40, "Виконання (Runtime Q)\n10 мс", size=12, fill="#eaf0fd", stroke=NEG, bold=True))

    # Throttled block (from t=10 to t=30)
    frags.append(fitbox(220, 120, 210, 40, "Дроселювання (Throttled)\nЧекає на поповнення", size=12, fill="#fdecea", stroke=POS))

    # Absolute deadline line
    frags.append(line(440, 70, 440, 250, color=POS, sw=2))
    frags.append(text(440, 60, "Абсолютний дедлайн (d₁ = 30 мс)", size=12, color=POS, bold=True, anchor="middle"))
    frags.append(text(440, 270, "t = 30 мс (Кінець періоду P)", size=12, anchor="middle"))

    # Replenishment at t=30
    frags.append(line(440, 80, 440, 250, color=FIELD, sw=1.5, dash="2,2"))
    frags.append(fitbox(450, 120, 150, 40, "Новий період (P₂)\nБюджет поповнено", size=12, fill="#e8f8f0", stroke=FIELD, bold=True))

    # Legend / explanatory text box at bottom
    frags.append(fitbox(60, 300, 720, 45, "CBS гарантує: Потік отримує максимум Q (10 мс) кожні P (30 мс). При вичерпанні Q потік дроселюється.\nEDF обирає для виконання потік із найближчим дедлайном d = r + D.", size=11, fill=FILL, stroke=MUTED))

    render(path, w, h, *frags)

def generate_dhall_effect():
    path = os.path.join(os.path.dirname(__file__), 'img', 'dhall-effect.svg')
    os.makedirs(os.path.dirname(path), exist_ok=True)

    w, h = 880, 360
    frags = []

    frags.append(text(w / 2, 28, "Ефект Далла (Global EDF) проти Partitioned EDF", size=16, bold=True))

    # Global EDF box boundary
    frags.append(rect(20, 50, 390, 270, fill=BG, stroke=POS, sw=1.5))
    frags.append(text(215, 75, "Global EDF (Міграція між ядрами)", size=14, color=POS, bold=True))
    frags.append(textbox(215, 120, "Спільна черга (Root Domain)", size=12, fill="#fdecea", stroke=POS)[0])
    frags.append(line(215, 140, 120, 180, color=POS, sw=1.5))
    frags.append(line(215, 140, 310, 180, color=POS, sw=1.5))
    frags.append(textbox(120, 200, "CPU 0\n(Короткі T₁)", size=12, fill=FILL)[0])
    frags.append(textbox(310, 200, "CPU 1\n(Короткі T₂)", size=12, fill=FILL)[0])
    frags.append(text(215, 275, "Довге завдання T₃ витісняється\nі пропускає дедлайн!", size=11, color=POS, bold=True))

    # Partitioned EDF box boundary
    frags.append(rect(430, 50, 430, 270, fill=BG, stroke=FIELD, sw=1.5))
    frags.append(text(645, 75, "Partitioned EDF (Прив'язка cpuset)", size=14, color=FIELD, bold=True))
    frags.append(textbox(530, 140, "Domain A\nCPU 0: Завдання T₁, T₂", size=11, fill="#e8f8f0", stroke=FIELD)[0])
    frags.append(textbox(750, 140, "Domain B\nCPU 1: Завдання T₃ (Ізольоване)", size=11, fill="#e8f8f0", stroke=FIELD)[0])
    frags.append(text(645, 275, "Ніяких витіснень з інших ядер:\nна кожному ядрі знову діє U ≤ U_max", size=11, color=FIELD, bold=True))

    render(path, w, h, *frags)

if __name__ == '__main__':
    generate_sched_deadline()
    generate_dhall_effect()
