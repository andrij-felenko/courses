# -*- coding: utf-8 -*-
"""Фігури до кроку «Де живе стан» (guide/progarch/structure-in-the-small/state-inventory)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")

GREEN_F = "#eafaf1"
AMBER_F = "#fdf3e7"; AMBER_S = "#e08a3c"
RED_F = "#fdecea"


def box_c(cx, cy, w, h, s, **kw):
    return fitbox(cx - w / 2.0, cy - h / 2.0, w, h, s, **kw)


def state_map():
    W, H = 720, 480
    frags = []
    # осі
    frags.append(arrow(95, 405, 705, 405))
    frags.append(arrow(95, 405, 95, 50))
    # підписи осей — поділки
    for x, lab in [(175, "виклик"), (320, "обʼєкт"), (470, "процес"), (610, "перезапуск")]:
        frags.append(text(x, 428, lab, size=13, color=MUTED))
    frags.append(text(400, 456, "час життя  →", size=13, color=MUTED))
    for y, lab in [(360, "1 функція"), (275, "1 обʼєкт"), (190, "весь процес"), (110, "парк машин")]:
        frags.append(text(87, y + 4, lab, size=12, color=MUTED, anchor="end"))
    frags.append(text(152, 42, "охоплення  ↑", size=13, color=MUTED))
    # клітини стану (колір = складність)
    frags.append(box_c(175, 360, 140, 44, "локальна\nзмінна", size=13, fill=GREEN_F, stroke=FIELD))
    frags.append(box_c(320, 275, 140, 44, "поле обʼєкта", size=13))
    frags.append(box_c(470, 190, 162, 46, "модульний /\nглобальний", size=13, fill=AMBER_F, stroke=AMBER_S))
    frags.append(box_c(610, 110, 140, 44, "база / файл", size=13, fill=RED_F, stroke=POS))
    render(os.path.join(IMG, "state-map.svg"), W, H, *frags)


def source_derived():
    W, H = 700, 380
    frags = []
    # єдине джерело
    frags.append(box_c(140, 190, 160, 100, "єдине\nджерело\nправди", size=15,
                       fill=GREEN_F, stroke=FIELD, bold=True))
    # похідні
    frags.append(box_c(520, 80, 200, 50, "кеш у памʼяті", size=14, fill=RED_F, stroke=POS))
    frags.append(box_c(520, 190, 200, 50, "матеріалізована вʼю", size=14))
    frags.append(box_c(520, 300, 200, 50, "індекс", size=14))
    # однобічні стрілки джерело → похідне
    frags.append(arrow(222, 190, 418, 82, color=FIELD))
    frags.append(arrow(222, 190, 418, 190, color=FIELD))
    frags.append(arrow(222, 190, 418, 298, color=FIELD))
    frags.append(text(322, 176, "виводиться", size=12, color=FIELD))
    # небезпека: прямий запис повз джерело
    frags.append(arrow(520, 28, 520, 53, color=POS))
    frags.append(text(520, 20, "прямий запис повз джерело", size=12, color=POS))
    render(os.path.join(IMG, "source-derived.svg"), W, H, *frags)


def hub_state_map():
    """Той самий інвентар, але на конкретному підрослому хабі: 7 шматків стану
    розставлені на осях час-життя × охоплення, колір = ризик."""
    W, H = 940, 600
    frags = []
    # осі
    frags.append(arrow(120, 520, 900, 520))
    frags.append(arrow(120, 520, 120, 60))
    # поділки часу життя (під віссю)
    for x, lab in [(200, "виклик"), (470, "процес"), (760, "тривкий (диск)")]:
        frags.append(text(x, 545, lab, size=13, color=MUTED))
    frags.append(text(510, 575, "час життя  →", size=13, color=MUTED))
    # поділки охоплення (ліворуч від осі)
    for y, lab in [(470, "1 функція"), (385, "поле сесії"),
                   (275, "увесь процес"), (150, "застосунок")]:
        frags.append(text(112, y + 4, lab, size=12, color=MUTED, anchor="end"))
    frags.append(text(176, 52, "охоплення  ↑", size=13, color=MUTED))
    # шматки стану (колір = ризик)
    frags.append(box_c(200, 470, 150, 52, "t · want_on\nлокальні", size=12,
                       fill=GREEN_F, stroke=FIELD))
    frags.append(box_c(430, 385, 178, 52, "dev.online\nпохідне, збережене", size=12,
                       fill=AMBER_F, stroke=AMBER_S))
    frags.append(box_c(430, 275, 160, 52, "devices у памʼяті\nдубль БД", size=12,
                       fill=AMBER_F, stroke=AMBER_S))
    frags.append(box_c(430, 150, 160, 52, "status_cache\nдруга правда", size=12,
                       fill=RED_F, stroke=POS))
    frags.append(box_c(620, 275, 160, 52, "heated_since\nмусить бути тривким", size=12,
                       fill=RED_F, stroke=POS))
    frags.append(box_c(810, 275, 150, 52, "devices у БД\nджерело правди", size=12,
                       fill=GREEN_F, stroke=FIELD))
    frags.append(box_c(810, 150, 150, 52, "schedule.json\nдва писарі", size=12,
                       fill=AMBER_F, stroke=AMBER_S))
    render(os.path.join(IMG, "hub-state-map.svg"), W, H, *frags)


def state_lineage():
    """Часова нитка: як поле сходилося на думці, що стан — головна складність."""
    W, H = 790, 560
    frags = []
    sx = 96
    # хребет-стрілка: час тече вниз
    frags.append(arrow(sx, 52, sx, 516))
    nodes = [
        (92, "1975 · Тарова яма", "Брукс: велика система грузне, як звір у смолі", FILL, LINE),
        (192, "1977 · Бекус проти присвоєнки", "присвоєнка — «пляшкове горло»; заклик до функційного стилю", FILL, LINE),
        (292, "1986 · «Срібної кулі немає»", "Брукс: сутнісна проти випадкової складності", FILL, LINE),
        (392, "2006 · «Out of the Tar Pit»", "Мозлі й Маркс: винуватець №1 — змінюваний стан", RED_F, POS),
        (492, "2007+ · Clojure, незмінність", "мінімізуй і заморозь стан — тепер буденна практика", GREEN_F, FIELD),
    ]
    bx, bw, bh = 150, 610, 62
    for y, head, desc, fill, stroke in nodes:
        frags.append(rect(bx, y - bh / 2, bw, bh, fill=fill, stroke=stroke, sw=1.5))
        frags.append(line(sx + 8, y, bx, y, color=MUTED))
        frags.append(circle(sx, y, 8, fill=stroke, stroke=BG, sw=2))
        frags.append(text(bx + 18, y - 6, head, size=15, color=INK, anchor="start", bold=True))
        frags.append(text(bx + 18, y + 17, desc, size=13, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "state-lineage.svg"), W, H, *frags)


def essence_accident():
    """Та сама повна складність, поділена по-різному: Брукс проти Мозлі-Маркса."""
    W, H = 720, 470
    frags = []
    top, bot = 96, 388
    bw = 176
    # Брукс, 1986: майже все — сутнісне
    cx1 = 200
    x1 = cx1 - bw / 2
    frags.append(text(cx1, 78, "Брукс · 1986", size=15, color=INK, bold=True))
    frags.append(fitbox(x1, top, bw, 52, "випадкова", size=14, fill=AMBER_F, stroke=AMBER_S))
    frags.append(fitbox(x1, top + 52, bw, bot - top - 52, "сутнісна\nскладність",
                        size=15, fill=GREEN_F, stroke=FIELD, bold=True))
    frags.append(text(cx1, 414, "«срібної кулі немає»", size=13, color=MUTED))
    # Мозлі й Маркс, 2006: більшість тієї «сутності» — насправді випадкова
    cx2 = 510
    x2 = cx2 - bw / 2
    frags.append(text(cx2, 78, "Мозлі й Маркс · 2006", size=15, color=INK, bold=True))
    frags.append(fitbox(x2, top, bw, 74, "випадкове\nкерування", size=14, fill=AMBER_F, stroke=AMBER_S))
    frags.append(fitbox(x2, top + 74, bw, 130, "випадковий\nстан", size=17,
                        fill=RED_F, stroke=POS, bold=True))
    frags.append(fitbox(x2, top + 204, bw, bot - top - 204, "сутнісне\nядро",
                        size=14, fill=GREEN_F, stroke=FIELD))
    frags.append(text(cx2, 414, "головна частка — стан", size=13, color=MUTED))
    render(os.path.join(IMG, "essence-accident.svg"), W, H, *frags)


if __name__ == "__main__":
    state_map()
    source_derived()
    hub_state_map()
    state_lineage()
    essence_accident()
    print("ok")
