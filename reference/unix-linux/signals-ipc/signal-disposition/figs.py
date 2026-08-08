# -*- coding: utf-8 -*-
"""Фігури до теми «Диспозиція сигналу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def three_answers():
    """Доставка сигналу розгалужується за вмістом рядка таблиці диспозицій."""
    f = []
    b, _, _ = textbox(460, 36, "Ядро доставляє сигнал N процесові", size=14, bold=True)
    f.append(b)
    f.append(arrow(460, 58, 460, 82))
    b, _, _ = textbox(460, 104, "Рядок N у таблиці диспозицій процесу", size=14)
    f.append(b)

    f.append(arrow(430, 128, 180, 160))
    f.append(arrow(460, 128, 460, 160))
    f.append(arrow(490, 128, 740, 160))

    b, _, _ = textbox(160, 192, "SIG_DFL\nтипова дія", size=14, bold=True, min_w=190)
    f.append(b)
    b, _, _ = textbox(460, 192, "SIG_IGN\nігнорувати", size=14, bold=True, min_w=190)
    f.append(b)
    b, _, _ = textbox(760, 192, "адреса функції\nобробник", size=14, bold=True, min_w=190)
    f.append(b)

    acts = ["завершити процес", "завершити + дамп пам'яті",
            "нічого не робити", "зупинити", "продовжити зупинений"]
    y = 258
    for a in acts:
        b, _, _ = textbox(160, y, a, size=13, min_w=210, fill="#eef3fb")
        f.append(b)
        y += 42

    b, _, _ = textbox(460, 262, "сигнал відкинуто\nв момент породження", size=13, fill="#eef3fb")
    f.append(b)
    b, _, _ = textbox(460, 332, "процес про нього\nне дізнається ніколи", size=13, fill="#eef3fb")
    f.append(b)

    b, _, _ = textbox(760, 262, "виконати функцію\nу просторі користувача", size=13, fill="#eef3fb")
    f.append(b)
    f.append(arrow(760, 296, 760, 316))
    b, _, _ = textbox(760, 344, "повернутися в перервану\nточку виконання", size=13, fill="#eef3fb")
    f.append(b)

    render(os.path.join(IMG, 'three-answers.svg'), 920, 480, *f)


def three_nothings():
    """Три способи «нічого не сталося» і чим вони різняться."""
    f = []
    xs = (300, 400, 500)
    x0, x1 = 210, 720

    rows = [
        (70, "диспозиція\nSIG_IGN",
         "відкинуто в момент породження — сигнал не потрапляє навіть у набір очікуваних",
         "0 доставлень"),
        (190, "типова дія —\nігнорувати",
         "ядро робить те саме, але це рішення ядра, а не процесу: рядок таблиці порожній",
         "0 доставлень"),
        (320, "сигнал\nзаблоковано",
         "лежить у наборі очікуваних, доки процес не зніме блокування",
         "доставлять пізніше"),
    ]

    for y, label, note, res in rows:
        b, _, _ = textbox(110, y, label, size=13, bold=True, min_w=170)
        f.append(b)
        f.append(line(x0, y, x1, y, sw=1.6))
        for x in xs:
            f.append(circle(x, y, 6, fill=POS, stroke=POS))
        b, _, _ = textbox(465, y + 50, note, size=12, fill="#f7f8fa")
        f.append(b)
        b, _, _ = textbox(810, y, res, size=13, min_w=180)
        f.append(b)

    y3 = rows[2][0]
    b, _, _ = textbox(600, y3 - 42, "розблокування", size=12, fill="#eef3fb")
    f.append(b)
    f.append(line(600, y3 - 16, 600, y3 + 16, color=NEG, sw=1.6, dash="5,4"))

    b, _, _ = textbox(355, 24, "три надсилання того самого сигналу", size=12, fill="#f7f8fa")
    f.append(b)

    render(os.path.join(IMG, 'three-nothings.svg'), 940, 430, *f)


def fork_exec_fate():
    """Що стається з таблицею диспозицій при fork і при exec."""
    f = []
    cols = [(150, "процес-батько"), (490, "після fork — дитина"), (830, "після exec — новий образ")]
    for cx, title in cols:
        b, _, _ = textbox(cx, 40, title, size=14, bold=True, min_w=260)
        f.append(b)

    rows = [
        (120, ["SIGINT → обробник", "SIGINT → обробник", "SIGINT → SIG_DFL"], [FILL, FILL, "#fdecea"]),
        (180, ["SIGPIPE → SIG_IGN", "SIGPIPE → SIG_IGN", "SIGPIPE → SIG_IGN"], [FILL, FILL, "#e8f6ee"]),
        (240, ["SIGTERM → SIG_DFL", "SIGTERM → SIG_DFL", "SIGTERM → SIG_DFL"], [FILL, FILL, FILL]),
    ]
    for y, cells, fills in rows:
        for (cx, _), s, fl in zip(cols, cells, fills):
            f.append(fitbox(cx - 130, y - 21, 260, 42, s, size=13, fill=fl))

    f.append(arrow(292, 180, 348, 180))
    b, _, _ = textbox(320, 132, "fork", size=12, fill="#eef3fb")
    f.append(b)
    f.append(arrow(632, 180, 688, 180))
    b, _, _ = textbox(660, 132, "exec", size=12, fill="#eef3fb")
    f.append(b)

    b, _, _ = textbox(490, 320, "адреса обробника після exec безглузда: старого коду в пам'яті вже немає,\n"
                                "а рішення «ігнорувати» не залежить від жодної адреси", size=12,
                      fill="#f7f8fa")
    f.append(b)

    render(os.path.join(IMG, 'fork-exec-fate.svg'), 1000, 370, *f)


if __name__ == '__main__':
    three_answers()
    three_nothings()
    fork_exec_fate()
    print("ok")
