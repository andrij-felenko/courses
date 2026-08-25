# -*- coding: utf-8 -*-
"""Фігури до теми «Користувачі, групи й ідентичність процесу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_four_ids():
    """Чотири числа замість одного: на яке питання відповідає кожне."""
    W, H = 1060, 530
    f = []
    rows = [
        (80,  "реальний UID\n(ruid)",
              "чий це процес: кому дозволено слати йому сигнали,\nчиї ліміти він витрачає і на чий рахунок іде облік"),
        (185, "діючий UID\n(euid)",
              "від чийого імені він діє: саме це число ядро порівнює\nна кожній перевірці доступу"),
        (290, "збережений UID\n(suid)",
              "куди дозволено повернутися: копія колишнього діючого,\nщоб знову підняти права після тимчасового зниження"),
        (395, "файловий UID\n(fsuid)",
              "доступ саме до файлів; у Linux тягнеться за діючим сам,\nокремо його крутить хіба сервер NFS"),
    ]
    for y, left, right in rows:
        b, w, h = textbox(190, y, left, size=14, min_w=240)
        f.append(b)
        f.append(arrow(315, y, 405, y))
        f.append(fitbox(415, y - 38, 600, 76, right, size=13, fill="#f7f9fc"))
    b, _, _ = textbox(530, 480,
                      "той самий набір із чотирьох є й для групи (rgid, egid, sgid, fsgid),\n"
                      "а поверх нього — список додаткових груп",
                      size=13, fill="#eef3fd", stroke=NEG)
    f.append(b)
    render(os.path.join(OUT, 'four-ids.svg'), W, H, *f,
           title="Чотири ідентифікатори користувача і призначення кожного")


def fig_cred_swap():
    """Набір повноважень не правлять — його заміняють цілим."""
    W, H = 1120, 480
    f = []
    b, _, _ = textbox(140, 250, "задача\n(task_struct)", size=14, min_w=190)
    f.append(b)

    f.append(fitbox(420, 92, 430, 112,
                    "старий cred — публічний, незмінний\n"
                    "uid 1000 · euid 1000 · suid 1000\n"
                    "групи: 1000, 27, 44",
                    size=13, fill="#f4f4f5", stroke=MUTED))
    f.append(fitbox(420, 300, 430, 112,
                    "новий cred\n"
                    "uid 1000 · euid 0 · suid 1000\n"
                    "групи: 1000, 27, 44",
                    size=13, fill="#eef3fd", stroke=NEG))

    f.append(arrow(635, 210, 635, 294, color=MUTED))
    b, _, _ = textbox(965, 252, "копія, якої\nще ніхто не бачив", size=12, fill="#f7f9fc")
    f.append(b)
    f.append(line(855, 252, 880, 252, color=MUTED, sw=1.2))

    f.append(arrow(236, 214, 414, 160, color=MUTED, sw=1.6))
    f.append(text(300, 128, "було", size=12, color=MUTED))
    f.append(arrow(236, 288, 414, 342, color=NEG))
    f.append(text(300, 382, "стало", size=12, color=NEG))

    b, _, _ = textbox(545, 445,
                      "інша задача читає вказівник через RCU: бачить або весь старий набір, "
                      "або весь новий — ніколи половину",
                      size=13, fill="#f7f9fc")
    f.append(b)
    render(os.path.join(OUT, 'cred-swap.svg'), W, H, *f,
           title="Зміна повноважень як підміна вказівника на незмінний блок")


def fig_identity_flow():
    """Ідентичність тече вниз по дереву процесів і тільки звужується."""
    W, H = 1100, 560
    f = []
    b, _, _ = textbox(300, 70, "PID 1  ·  uid 0", size=14, min_w=210)
    f.append(b)
    b, _, _ = textbox(300, 190, "sshd  ·  uid 0", size=14, min_w=210)
    f.append(b)
    b, _, _ = textbox(300, 320, "оболонка  ·  uid 1000", size=14, min_w=210)
    f.append(b)
    b, _, _ = textbox(160, 445, "make · uid 1000", size=13)
    f.append(b)
    b, _, _ = textbox(430, 445, "cc · uid 1000", size=13)
    f.append(b)
    b, _, _ = textbox(830, 445, "passwd\nruid 1000 · euid 0", size=13, stroke=POS)
    f.append(b)

    f.append(arrow(300, 95, 300, 163))
    f.append(arrow(300, 218, 300, 293))
    f.append(arrow(268, 344, 190, 418))
    f.append(arrow(334, 344, 418, 418))
    f.append(arrow(390, 350, 726, 428, color=POS))

    b, _, _ = textbox(640, 255, "PAM звірив пароль —\nі процес звузив себе\nдо uid 1000",
                      size=12, fill="#f7f9fc")
    f.append(b)
    b, _, _ = textbox(880, 300, "єдиний виняток:\nбіт set-user-ID на файлі\nпідняв euid при exec",
                      size=12, fill="#fdecea", stroke=POS)
    f.append(b)
    b, _, _ = textbox(500, 528,
                      "ідентичність тільки успадковується або звужується; узяти чужу процес сам не може",
                      size=13, fill="#eef3fd", stroke=NEG)
    f.append(b)
    render(os.path.join(OUT, 'identity-flow.svg'), W, H, *f,
           title="Звідки процес бере свою ідентичність")


if __name__ == '__main__':
    fig_four_ids()
    fig_cred_swap()
    fig_identity_flow()
    print("ok")
