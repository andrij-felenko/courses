# -*- coding: utf-8 -*-
"""Фігури до теми «Креденшели процесів: Real, Effective, Saved UID/GID»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_cred_types_and_transitions():
    """Види ідентифікаторів процесу та переходи між ними при скиданні й відновленні привілеїв."""
    W, H = 1000, 560
    f = []

    # Верхній блок: Опис чотирьох UID
    f.append(text(500, 35, "Ідентифікатори процесу (UID / GID)", size=16, bold=True, anchor="middle"))

    col_w = 215
    col_gap = 20
    start_x = 30

    uids = [
        ("Real UID (ruid)", "Справжній власник", "Хто запустив процес;\nвизначає ліміти\nі право на kill()", "#eef3fd", POS),
        ("Effective UID (euid)", "Поточні привілеї", "Ядро дивиться сюди\nпри DAC перевірках\n(файли, сокети)", "#fdecea", NEG),
        ("Saved Set-UID (suid)", "Збережений привілей", "Фіксує привілей при\nexecve SUID-файлу;\nдозволяє повернення", "#fff8e7", "#d97706"),
        ("Filesystem UID (fsuid)", "Файлові перевірки", "Використовується в\nNFS/FS перевірках;\nавто-слідує за euid", "#f0fdf4", "#16a34a"),
    ]

    for i, (title, sub, desc, bg, border) in enumerate(uids):
        x = start_x + i * (col_w + col_gap)
        f.append(fitbox(x, 60, col_w, 130, f"{title}\n{sub}\n\n{desc}", size=12, fill=bg, stroke=border))

    # Нижня частина: Переходи привілеїв (SUID cycle)
    f.append(text(500, 220, "Переходи привілеїв у SUID-програмі (наприклад, passwd)", size=14, bold=True, anchor="middle"))

    steps = [
        ("1. Запуск SUID-файлу", "ruid = 1000\neuid = 0 (root)\nsuid = 0 (root)", "#fff8e7", "#d97706"),
        ("2. Тимчасове скидання", "seteuid(1000)\nruid = 1000, euid = 1000\nsuid = 0 (збережено!)", "#eef3fd", POS),
        ("3. Відновлення привілеїв", "seteuid(0)\nruid = 1000, euid = 0\nsuid = 0", "#fdecea", NEG),
        ("4. Остаточне скидання", "setresuid(1000, 1000, 1000)\nruid = 1000, euid = 1000\nsuid = 1000 (без повернення)", "#f3f4f6", MUTED)
    ]

    box_w = 215
    for i, (stitle, sbody, sbg, sborder) in enumerate(steps):
        x = start_x + i * (box_w + col_gap)
        f.append(fitbox(x, 260, box_w, 140, f"{stitle}\n\n{sbody}", size=11, fill=sbg, stroke=sborder))

        if i < 3:
            ax = x + box_w + 2
            ay = 330
            f.append(arrow(ax, ay, ax + 16, ay, color=MUTED, sw=1.8))

    # Нижній висновок
    f.append(fitbox(35, 430, 930, 80,
                    "Ключове правило: непривілейований процес може змінювати euid лише між ruid та suid.\n"
                    "Остаточне скидання setresuid(ruid, ruid, ruid) перезаписує suid, роблячи повернення привілеїв неможливим.",
                    size=12, fill="#f8fafc", stroke=MUTED))

    render(os.path.join(OUT, 'cred-types-and-transitions.svg'), W, H, *f,
           title="Види UID/GID та переходи привілеїв у процесі")


def fig_kernel_cred_rcu():
    """Зберігання credentials у ядрі Linux та RCU-модифікація struct cred."""
    W, H = 960, 480
    f = []

    f.append(text(480, 30, "Структура struct cred у ядрі Linux та RCU-модифікація", size=16, bold=True, anchor="middle"))

    # Справа task_struct
    f.append(fitbox(30, 100, 200, 140, "task_struct\n(процес / нитка)\n\nreal_cred ──┐\ncred ────────┼──►", size=12, fill="#f8fafc", stroke=POS))

    # Стара struct cred
    f.append(fitbox(280, 100, 260, 140, "Стара struct cred (read-only)\n\nruid: 1000   euid: 0\nsuid: 0      fsuid: 0\nusage counter > 0", size=12, fill="#fdecea", stroke=NEG))

    # Нова struct cred (RCU)
    f.append(fitbox(280, 280, 260, 140, "Нова struct cred (prepare_creds)\n\nruid: 1000   euid: 1000\nsuid: 1000   fsuid: 1000\n(копіюється і змінюється)", size=12, fill="#eef3fd", stroke=POS))

    # Покроковий RCU процес справа
    rcu_steps = (
        "1. prepare_creds(): створюється дублікат struct cred\n"
        "2. Зміна полів (наприклад, setresuid)\n"
        "3. commit_creds(): атомарно task->cred = new_cred\n"
        "4. Стара структура звільняється через RCU callback"
    )
    f.append(fitbox(590, 100, 330, 320, f"RCU Патерн у ядрі:\n\n{rcu_steps}", size=11, fill="#fff8e7", stroke="#d97706"))

    # Стрілки
    f.append(arrow(230, 150, 280, 150, color=POS, sw=2))
    f.append(line(250, 150, 250, 350, color=POS, sw=2, dash="4,4"))
    f.append(arrow(250, 350, 280, 350, color=POS, sw=2))
    f.append(text(250, 250, "commit_creds()", size=11, color=POS, anchor="middle"))

    # Текст знизу
    f.append(fitbox(30, 430, 890, 40,
                    "Незмінність (immutability) struct cred унеможливлює race condition: інші нитки бачать старі чи нові креденшели повністю.",
                    size=11, fill="#f8fafc", stroke=MUTED))

    render(os.path.join(OUT, 'kernel-cred-rcu.svg'), W, H, *f,
           title="Структура struct cred та RCU оновлення у ядрі")


if __name__ == '__main__':
    fig_cred_types_and_transitions()
    fig_kernel_cred_rcu()
    print("Figures generated successfully.")
