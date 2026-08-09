# -*- coding: utf-8 -*-
"""Фігури до теми «Керовані ресурси драйвера: сімейство devm_ і автоматичне звільнення»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

ZONE_DEV = "#eef4fb"    # об'єкт пристрою
ZONE_HDR = "#f3f0fa"    # службова шапка вузла
ZONE_DAT = "#fdf3ea"    # корисні дані вузла
ZONE_OK  = "#eff7ef"    # успішна гілка
ZONE_BAD = "#fdeeec"    # гілка помилки


def box(cx, cy, s, size=13, **kw):
    body, w, h = textbox(cx, cy, s, size=size, **kw)
    return body


# ── 1. Будова списку керованих ресурсів ─────────────────────────────────────
def fig_devres_anatomy():
    W, H = 1240, 640
    f = []

    # Об'єкт пристрою
    f.append(rect(60, 90, 250, 190, fill=ZONE_DEV, stroke=MUTED, sw=1.2))
    f.append(text(185, 122, "struct device", size=15, bold=True))
    f.append(box(185, 168, "devres_lock", size=12, min_w=200))
    f.append(box(185, 226, "devres_head", size=12, min_w=200))

    # Вузли
    xs = [430, 720, 1010]
    payload = [
        "вказівник\nвід ioremap()",
        "номер лінії\nі dev_id",
        "стан драйвера\n(самі дані)",
    ]
    rel = [
        "release =\niounmap",
        "release =\nfree_irq",
        "release =\nнічого",
    ]
    src = [
        "devm_ioremap()",
        "devm_request_irq()",
        "devm_kzalloc()",
    ]
    for i, x in enumerate(xs):
        f.append(rect(x - 125, 100, 250, 210, fill=BG, stroke=LINE, sw=1.6))
        f.append(fitbox(x - 108, 118, 216, 74, rel[i], size=12,
                        fill=ZONE_HDR, stroke=MUTED))
        f.append(fitbox(x - 108, 208, 216, 84, payload[i], size=12,
                        fill=ZONE_DAT, stroke=MUTED))
        f.append(text(x, 348, src[i], size=13, color=MUTED))
        f.append(line(x, 316, x, 334, color=MUTED, sw=1.2, dash="4 4"))

    f.append(text(430, 92, "шапка вузла", size=11, color=MUTED, anchor="start"))

    # Зв'язки списку
    f.append(arrow(316, 226, 300, 226, color=MUTED, sw=1.4))
    f.append(line(300, 226, 300, 400, color=MUTED, sw=1.4))
    f.append(line(300, 400, 340, 400, color=MUTED, sw=1.4))
    f.append(arrow(340, 400, 340, 316, color=MUTED, sw=1.4))
    f.append(arrow(555, 205, 592, 205, color=MUTED, sw=1.4))
    f.append(arrow(845, 205, 882, 205, color=MUTED, sw=1.4))

    f.append(text(620, 464,
                  "звільнення йде у зворотному порядку: спершу останній вузол",
                  size=13, color=INK))
    f.append(arrow(1010, 500, 430, 500, color=POS, sw=2.0))
    f.append(text(720, 540, "devres_release_all()", size=14, bold=True, color=POS))

    f.append(text(620, 596,
                  "вузол не знає, що в ньому лежить — він знає, кого покликати "
                  "і що тому передати",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "devres-anatomy.svg"), W, H, *f,
           title="Список devres: шапка з функцією звільнення плюс дані саме для неї")


# ── 2. Три двері до звільнення ──────────────────────────────────────────────
def fig_release_points():
    W, H = 1200, 700
    f = []

    # Двері 1
    f.append(rect(60, 80, 320, 250, fill=ZONE_BAD, stroke=MUTED, sw=1.2))
    f.append(text(220, 112, "probe() повернув помилку", size=14, bold=True))
    f.append(box(220, 165, "драйвер устиг узяти\nчастину ресурсів", size=12, min_w=280))
    f.append(box(220, 258, "каркас знімає зв'язок\nі кличе звільнення", size=12, min_w=280))
    f.append(arrow(220, 197, 220, 224, color=INK, sw=1.6))

    # Двері 2
    f.append(rect(440, 80, 320, 250, fill=ZONE_DEV, stroke=MUTED, sw=1.2))
    f.append(text(600, 112, "відв'язка драйвера", size=14, bold=True))
    f.append(box(600, 165, "виконується remove()\nПОВНІСТЮ", size=12, min_w=280))
    f.append(box(600, 258, "і аж тоді — звільнення\nусього списку", size=12, min_w=280))
    f.append(arrow(600, 197, 600, 224, color=INK, sw=1.6))

    # Двері 3
    f.append(rect(820, 80, 320, 250, fill=ZONE_OK, stroke=MUTED, sw=1.2))
    f.append(text(980, 112, "пристрій видаляють", size=14, bold=True))
    f.append(box(980, 165, "драйвера не було\nвзагалі", size=12, min_w=280))
    f.append(box(980, 258, "device_del() кличе\nте саме звільнення", size=12, min_w=280))
    f.append(arrow(980, 197, 980, 224, color=INK, sw=1.6))

    # Зведення
    f.append(box(600, 440, "devres_release_all(dev)", size=16, bold=True,
                 min_w=460, fill=BG, stroke=POS, sw=2.0))
    f.append(arrow(220, 292, 420, 415, color=MUTED, sw=1.7))
    f.append(arrow(600, 292, 600, 415, color=MUTED, sw=1.7))
    f.append(arrow(980, 292, 780, 415, color=MUTED, sw=1.7))

    f.append(box(600, 556, "усі вузли зняті, кожному покликано його release",
                 size=13, min_w=560, fill=ZONE_OK, stroke=FIELD))
    f.append(arrow(600, 468, 600, 532, color=FIELD, sw=1.9))

    f.append(text(600, 646,
                  "драйвер не кличе звільнення сам — тому пропустити його "
                  "неможливо навіть у гілці, яку ніхто не тестував",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "release-points.svg"), W, H, *f,
           title="Три шляхи, якими каркас приходить до звільнення керованих ресурсів")


# ── 3. remove() спершу, devres потім ────────────────────────────────────────
def fig_remove_then_devres():
    W, H = 1160, 620
    f = []

    # Вісь часу
    f.append(line(120, 300, 1050, 300, color=MUTED, sw=1.6))
    f.append(text(120, 340, "початок відв'язки", size=12, color=MUTED, anchor="start"))
    f.append(text(1050, 340, "пристрій вільний", size=12, color=MUTED, anchor="end"))

    # Смуга remove()
    f.append(rect(150, 150, 380, 110, fill=ZONE_BAD, stroke=MUTED, sw=1.2))
    f.append(text(340, 182, "тіло remove() драйвера", size=14, bold=True))
    f.append(text(340, 216, "kfree(a->ring)", size=13))
    f.append(text(340, 242, "зупинка робочої черги", size=12, color=MUTED))

    # Смуга devres
    f.append(rect(620, 150, 400, 110, fill=ZONE_DEV, stroke=MUTED, sw=1.2))
    f.append(text(820, 182, "devres_release_all()", size=14, bold=True))
    f.append(text(820, 216, "free_irq()  →  iounmap()", size=13))
    f.append(text(820, 242, "зворотний порядок захоплення", size=12, color=MUTED))

    f.append(arrow(536, 205, 612, 205, color=INK, sw=1.8))

    # Небезпечне вікно
    f.append(rect(150, 390, 470, 96, fill=BG, stroke=POS, sw=2.0))
    f.append(text(385, 424, "кероване переривання ще зареєстроване", size=14,
                  bold=True, color=POS))
    f.append(text(385, 458, "обробник може вистрелити в цю мить", size=13, color=POS))
    f.append(line(150, 300, 150, 384, color=POS, sw=1.4, dash="5 5"))
    f.append(line(620, 300, 620, 384, color=POS, sw=1.4, dash="5 5"))

    f.append(text(580, 552,
                  "усе, чого торкається обробник, має звільнятися тим самим "
                  "механізмом, що й саме переривання",
                  size=13, color=MUTED))

    render(os.path.join(OUT, "remove-then-devres.svg"), W, H, *f,
           title="На відв'язці remove() виконується повністю до першого звільнення devres")


if __name__ == "__main__":
    fig_devres_anatomy()
    fig_release_points()
    fig_remove_then_devres()
    print("готово:", OUT)
