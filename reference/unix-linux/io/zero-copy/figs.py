# -*- coding: utf-8 -*-
"""Фігури до теми «Передача без копіювання: sendfile і splice»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_copy_path():
    """Три шляхи байтів: read+write, sendfile, sendfile зі збиранням картою."""
    W, H = 980, 430
    f = []

    # колонки
    c1x, c1w = 150, 160          # кеш сторінок
    c2x, c2w = 380, 160          # буфер програми
    c3x, c3w = 610, 160          # черга сокета
    c4x, c4w = 840, 125          # мережева карта
    rows = [78, 208, 338]
    bh = 58

    titles = [
        "read() + write(): дві копії процесором",
        "sendfile(): одна копія, всередині ядра",
        "sendfile() зі збиранням картою: жодної копії процесором",
    ]

    for i, ry in enumerate(rows):
        f.append(text(18, ry - 16, titles[i], size=14, bold=True, anchor="start"))
        f.append(fitbox(c1x, ry, c1w, bh, "Кеш сторінок", size=13))
        f.append(fitbox(c4x, ry, c4w, bh, "Мережева\nкарта", size=13))
        ay = ry + bh / 2
        ly = ry + 13
        if i == 0:
            f.append(fitbox(c2x, ry, c2w, bh, "Буфер\nпрограми", size=13))
            f.append(fitbox(c3x, ry, c3w, bh, "Черга сокета\n(байти)", size=13))
            f.append(arrow(c1x + c1w, ay, c2x, ay, color=POS))
            f.append(text((c1x + c1w + c2x) / 2, ly, "копія", size=12, color=POS))
            f.append(arrow(c2x + c2w, ay, c3x, ay, color=POS))
            f.append(text((c2x + c2w + c3x) / 2, ly, "копія", size=12, color=POS))
        elif i == 1:
            f.append(fitbox(c3x, ry, c3w, bh, "Черга сокета\n(байти)", size=13))
            f.append(arrow(c1x + c1w, ay, c3x, ay, color=POS))
            f.append(text((c1x + c1w + c3x) / 2, ly, "копія всередині ядра", size=12, color=POS))
        else:
            f.append(fitbox(c3x, ry, c3w, bh, "Черга сокета\n(вказівники)", size=13))
            f.append(arrow(c1x + c1w, ay, c3x, ay, color=NEG))
            f.append(text((c1x + c1w + c3x) / 2, ly, "посилання на сторінки", size=12, color=NEG))
        f.append(arrow(c3x + c3w, ay, c4x, ay, color=FIELD))
        f.append(text((c3x + c3w + c4x) / 2, ly, "DMA", size=12, color=FIELD))

    f.append(text(150, 410, "— копія процесором", size=12, color=POS, anchor="start"))
    f.append(text(430, 410, "— DMA пристроєм", size=12, color=FIELD, anchor="start"))
    f.append(text(700, 410, "— лише посилання", size=12, color=NEG, anchor="start"))

    render(os.path.join(IMG, 'copy-path.svg'), W, H, *f)


def fig_pipe_refs():
    """Канал як кільце записів «сторінка + зсув + довжина»."""
    W, H = 880, 380
    f = []

    f.append(fitbox(60, 40, 180, 50, "дескриптор файлу", size=13))
    f.append(fitbox(650, 40, 180, 50, "сокет", size=13))

    f.append(arrow(150, 90, 150, 145))
    f.append(text(170, 120, "splice(файл → канал)", size=12, anchor="start"))
    f.append(arrow(730, 145, 730, 90))
    f.append(text(710, 120, "splice(канал → сокет)", size=12, anchor="end"))

    f.append(text(440, 136, "канал (pipe): кільце записів", size=13, bold=True))
    f.append(rect(80, 145, 720, 80, fill="#ffffff"))

    xs = [105, 285, 465, 645]
    for i, x in enumerate(xs):
        f.append(fitbox(x, 160, 150, 50, "запис %d\nсторінка, зсув, довжина" % (i + 1), size=11))
        f.append(fitbox(x, 280, 150, 50, "сторінка кеша", size=12))
        f.append(arrow(x + 75, 210, x + 75, 280, color=NEG))

    f.append(text(440, 358, "байти лишаються на місці — рухаються лише записи",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'pipe-refs.svg'), W, H, *f)


def fig_ownership():
    """Чотири моменти: коли sendfile повернувся, байти ще належать не лише вам."""
    W, H = 980, 300
    f = []

    xs = [20, 265, 510, 755]
    pw = 205
    heads = ["t₁ виклик", "t₂ повернення", "t₃ у мережі", "t₄ втрата й повтор"]
    bodies = [
        "sendfile()\nядро бере посилання\nна сторінки кеша",
        "виклик повернув\nчисло байтів\nу дротах ще нічого\nсторінки — в черзі TCP",
        "карта прочитала\nсторінки прямо з кеша\nсегмент пішов",
        "ACK не прийшов\nTCP шле ті самі сторінки\nз їхнім теперішнім\nвмістом",
    ]
    for i, x in enumerate(xs):
        f.append(fitbox(x, 40, pw, 34, heads[i], size=14, bold=True))
        f.append(fitbox(x, 84, pw, 150, bodies[i], size=14))

    f.append(fitbox(265, 250, 695, 40,
                    "запис у файл між t₂ і t₄ змінює те, що піде в повторній передачі",
                    size=13, fill="#fdecea", stroke=POS, color=POS))

    render(os.path.join(IMG, 'ownership.svg'), W, H, *f)


if __name__ == '__main__':
    fig_copy_path()
    fig_pipe_refs()
    fig_ownership()
    print("ok")
