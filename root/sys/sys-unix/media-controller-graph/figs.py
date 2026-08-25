# -*- coding: utf-8 -*-
"""Фігури до теми «Media Controller: граф пристроїв замість одного вузла»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

PAD_FILL = "#dceffe"


def pad(x0, y0, s=18, stroke=NEG):
    """Квадратик пада, що сидить на межі рамки сутності."""
    return rect(x0, y0, s, s, fill=PAD_FILL, stroke=stroke, sw=1.5, rx=3)


def fig_anatomy():
    """Із чого складається граф: сутність, пади на її межах, зв'язок, окремий вузол-інтерфейс."""
    W, H = 940, 380
    f = []

    # сусідня сутність зліва
    f.append(fitbox(60, 120, 210, 100, "Приймач CSI-2", size=14))
    f.append(pad(272, 161))

    # головна сутність
    f.append(fitbox(420, 110, 300, 120, "Масштабувач\n(сутність)", size=15))
    f.append(pad(400, 161))
    f.append(pad(722, 161))

    # зв'язок між ними
    f.append(arrow(292, 170, 398, 170))
    f.append(text(345, 152, "зв'язок увімкнено", size=11, color=MUTED))

    # вихід далі в граф
    f.append(arrow(742, 170, 855, 170))
    f.append(text(798, 152, "далі в граф", size=11, color=MUTED))

    # підписи падів
    f.append(text(281, 100, "пад-джерело", size=12, color=NEG))
    f.append(text(409, 100, "пад-приймач", size=12, color=NEG))
    f.append(text(731, 100, "пад-джерело", size=12, color=NEG))

    # інтерфейс
    f.append(line(570, 230, 570, 290, color=MUTED, dash="6 5"))
    f.append(fitbox(450, 290, 240, 50, "/dev/v4l-subdev2", size=14))
    f.append(mtext(710, 310, ["інтерфейс — вузол, через який",
                              "цій сутності задають формат"],
                   size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


def fig_graph():
    """Граф камери на платі: одне залізо, кілька можливих трактів, увімкнено лише частину."""
    W, H = 1080, 500
    f = []

    # головний тракт
    f.append(fitbox(30, 90, 160, 64, "Сенсор\nov5640", size=13))
    f.append(fitbox(240, 90, 170, 64, "Приймач\nCSI-2", size=13))
    f.append(fitbox(460, 82, 200, 80, "ISP: корекція,\nдемозаїка,\nбаланс білого", size=12))
    f.append(fitbox(710, 90, 160, 64, "Масштабувач", size=13))
    f.append(fitbox(910, 90, 150, 64, "/dev/video0\nкадр NV12", size=12))

    f.append(arrow(190, 122, 240, 122))
    f.append(arrow(410, 122, 460, 122))
    f.append(arrow(660, 122, 710, 122))
    f.append(arrow(870, 122, 910, 122))

    # гілка статистики
    f.append(fitbox(710, 240, 160, 64, "Збір\nстатистики", size=13))
    f.append(fitbox(910, 240, 150, 64, "/dev/video1\nстатистика", size=12))
    f.append(line(560, 162, 560, 272))
    f.append(arrow(560, 272, 710, 272))
    f.append(arrow(870, 272, 910, 272))

    # вимкнений тракт сирого Bayer
    f.append(fitbox(910, 390, 150, 64, "/dev/video2\nсирий Bayer", size=12))
    f.append(line(325, 154, 325, 422, color=MUTED, dash="7 5"))
    f.append(line(325, 422, 875, 422, color=MUTED, dash="7 5"))
    f.append(arrow(875, 422, 910, 422, color=MUTED))
    f.append(text(600, 406, "зв'язок є в залізі, але вимкнений", size=12, color=MUTED))

    # легенда
    f.append(line(30, 466, 80, 466))
    f.append(text(90, 470, "увімкнений зв'язок — дані течуть", size=12, color=MUTED, anchor="start"))
    f.append(line(360, 466, 410, 466, color=MUTED, dash="7 5"))
    f.append(text(420, 470, "вимкнений — залізо вміє, але зараз ні", size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "graph.svg"), W, H, *f)


def fig_formats():
    """Формат живе на паді; на вмиканні потоку ядро звіряє кінці кожного зв'язку."""
    W, H = 1000, 310
    f = []

    f.append(fitbox(40, 70, 220, 80, "Сенсор\nпад-джерело 0", size=13))
    f.append(fitbox(380, 70, 240, 80, "Приймач CSI-2\nпади 0 і 1", size=13))
    f.append(fitbox(740, 70, 220, 80, "ISP\nпад-приймач 0", size=13))

    f.append(arrow(260, 110, 380, 110))
    f.append(arrow(620, 110, 740, 110, color=POS))
    f.append(text(680, 142, "✗", size=20, color=POS, bold=True))

    f.append(mtext(150, 185, ["SGRBG10_1X10", "1920×1080"], size=12, color=MUTED))
    f.append(mtext(500, 185, ["на обох падах", "SGRBG10_1X10 1920×1080"], size=12, color=MUTED))
    f.append(mtext(850, 185, ["SGRBG10_1X10", "1280×720"], size=12, color=MUTED))

    f.append(text(500, 250, "VIDIOC_STREAMON → EPIPE: кінці зв'язку описують різні кадри",
                  size=14, color=POS, bold=True))

    render(os.path.join(IMG, "formats.svg"), W, H, *f)


def fig_padwalk():
    """До вставки: вузол обходу — пад, а ребер два різні види."""
    W, H = 1020, 400
    f = []

    # вхід у граф
    f.append(arrow(60, 190, 176, 190))

    # сутність A
    f.append(rect(200, 90, 280, 180))
    f.append(text(340, 122, "Приймач CSI-2", size=15, bold=True))
    f.append(pad(181, 181))
    f.append(pad(481, 161))
    f.append(pad(481, 216))

    # переходи всередині сутности
    f.append(arrow(212, 192, 476, 175, color=NEG))
    f.append(arrow(212, 198, 476, 222, color=NEG))
    f.append(text(345, 258, "перехід усередині сутности", size=11, color=NEG))

    # сутність B
    f.append(rect(680, 110, 250, 150))
    f.append(text(805, 142, "ISP", size=15, bold=True))
    f.append(pad(661, 171))
    f.append(pad(931, 171))

    # зв'язок даних
    f.append(arrow(501, 170, 655, 180))
    f.append(text(578, 152, "зв'язок даних", size=11, color=MUTED))

    # гілка, яку обхід теж побачить
    f.append(arrow(501, 228, 600, 258))
    f.append(text(608, 266, "інша гілка", size=11, color=MUTED, anchor="start"))

    f.append(text(510, 335, "черга обходу тримає пади, а не сутності", size=12, color=MUTED))

    render(os.path.join(IMG, "padwalk.svg"), W, H, *f)


def fig_identity():
    """До вставки: як від сутности дійти до її вузла в /dev."""
    W, H = 1305, 270
    f = []

    bw, gap, y, h = 195, 70, 80, 110
    xs = [25 + i * (bw + gap) for i in range(5)]
    boxes = ["сутність 12\nipu1_ic_prpvf",
             "зв'язок-інтерфейс\nsink_id = 12",
             "інтерфейс\nV4L_VIDEO\nmajor 81 · minor 3",
             "/sys/dev/char/81:3/\nuevent",
             "/dev/video3"]
    for x, s in zip(xs, boxes):
        f.append(fitbox(x, y, bw, h, s, size=13))

    for x, lab in zip(xs[:-1], ["у зв'язках", "source_id", "sysfs", "DEVNAME"]):
        f.append(arrow(x + bw + 5, 135, x + bw + gap - 5, 135))
        f.append(text(x + bw + gap / 2, 118, lab, size=11, color=MUTED))

    render(os.path.join(IMG, "identity.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anatomy()
    fig_graph()
    fig_formats()
    fig_padwalk()
    fig_identity()
    print("ok")
