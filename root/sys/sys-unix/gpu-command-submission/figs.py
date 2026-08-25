# -*- coding: utf-8 -*-
"""Фігури до теми «Подання роботи на графічний процесор: черги команд і планувальник»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_ring_and_batch():
    """Кільце тримає не команди, а стрибки на пакети; дзвінок посуває кінець черги."""
    W, H = 1120, 600
    f = []

    # ── пакети команд у пам'яті програми ──────────────────────────────────
    f.append(text(60, 78, "пам'ять програми", size=13, color=MUTED, anchor="start"))
    f.append(fitbox(140, 92, 320, 72,
                    "пакет команд кадру N\nстан · прив'язки · виклики малювання", size=12))
    f.append(fitbox(620, 92, 320, 72,
                    "пакет команд кадру N+1\nбудується просто зараз", size=12))

    # ── саме кільце ───────────────────────────────────────────────────────
    CELL_W, X0, Y0, CELL_H = 160, 140, 270, 58
    cells = [
        ("виконано", True),
        ("стрибок\nна пакет N", False),
        ("стрибок\nна пакет N+1", False),
        ("вільно", True),
        ("вільно", True),
    ]
    for i, (label, dim) in enumerate(cells):
        x = X0 + i * CELL_W
        f.append(fitbox(x, Y0, CELL_W, CELL_H, label, size=12,
                        fill="#f1f2f4" if dim else FILL,
                        color=MUTED if dim else INK))

    f.append(text(60, 250, "кільце команд у пам'яті, розмір сталий",
                  size=13, color=MUTED, anchor="start"))

    # стрибки з кільця в пакети
    f.append(arrow(380, Y0 - 6, 300, 166, color=NEG))
    f.append(arrow(560, Y0 - 6, 760, 166, color=NEG))

    # ── два вказівники ────────────────────────────────────────────────────
    READ_X = X0 + CELL_W              # 300 — межа «виконано / ще ні»
    WRITE_X = X0 + 3 * CELL_W         # 620 — межа «зайнято / вільно»
    f.append(arrow(READ_X, 372, READ_X, Y0 + CELL_H + 4, color=FIELD))
    f.append(text(READ_X, 394, "читає GPU", size=12, color=FIELD))
    f.append(arrow(WRITE_X, 372, WRITE_X, Y0 + CELL_H + 4, color=POS))
    f.append(text(WRITE_X + 130, 394, "сюди CPU допише наступний стрибок",
                  size=12, color=POS))

    # ── замикання кільця ──────────────────────────────────────────────────
    RIGHT = X0 + 5 * CELL_W           # 940
    f.append(line(RIGHT, Y0 + CELL_H + 4, RIGHT, 440, color=MUTED, sw=1.2, dash="6,5"))
    f.append(line(RIGHT, 440, X0, 440, color=MUTED, sw=1.2, dash="6,5"))
    f.append(arrow(X0, 440, X0, Y0 + CELL_H + 4, color=MUTED))
    f.append(text(540, 466, "кінець кільця — це його початок: місце не кінчається, воно повертається",
                  size=12, color=MUTED))

    # ── хто на що дивиться ────────────────────────────────────────────────
    f.append(fitbox(140, 500, 380, 66,
                    "командний процесор GPU\nчитає кільце й стрибає в пакет", size=12,
                    fill="#eaf7ee", stroke=FIELD))
    f.append(fitbox(620, 500, 320, 66,
                    "регістр-дзвінок\nCPU пише сюди новий кінець", size=12,
                    fill="#fdecea", stroke=POS))
    f.append(arrow(200, 496, 200, 336, color=FIELD))
    f.append(arrow(880, 496, 880, 336, color=POS))

    render(os.path.join(IMG, 'ring-and-batch.svg'), W, H, *f)


def fig_submit_path():
    """Шлях однієї порції роботи: виклик повертається обіцянкою, а не результатом."""
    W, H = 1220, 540
    f = []

    BW, BH, BY = 230, 92, 170
    boxes = [
        (40,  "програма\nбудує пакет, збирає список буферів", FILL, LINE),
        (330, "ядро\nперевіряє буфери, робить завдання", FILL, LINE),
        (620, "планувальник\nтримає завдання, доки не час", "#eef2ff", NEG),
        (910, "апаратне кільце\nдзвінок і виконання", "#eaf7ee", FIELD),
    ]
    for x, label, fill, stroke in boxes:
        f.append(fitbox(x, BY, BW, BH, label, size=12, fill=fill, stroke=stroke))
    for x in (270, 560, 850):
        f.append(arrow(x + 2, BY + BH / 2, x + 58, BY + BH / 2))

    f.append(text(155, 152, "простір користувача", size=12, color=MUTED))
    f.append(text(760, 152, "ядро й залізо", size=12, color=MUTED))

    # ── зворотний хід: виклик повернувся одразу ───────────────────────────
    f.append(text(280, 92, "виклик повертається одразу — з вихідною огорожею замість результату",
                  size=12, color=MUTED))
    f.append(line(400, BY - 4, 400, 110, color=MUTED, sw=1.2, dash="6,5"))
    f.append(line(400, 110, 155, 110, color=MUTED, sw=1.2, dash="6,5"))
    f.append(arrow(155, 110, 155, BY - 4, color=MUTED))

    # ── вхідні огорожі тримають завдання ──────────────────────────────────
    f.append(fitbox(600, 310, 300, 62,
                    "вхідні огорожі ще не впали:\nчужа робота не скінчилася", size=12,
                    fill="#eef2ff", stroke=NEG))
    f.append(arrow(750, 306, 750, BY + BH + 4, color=NEG))

    # ── завершення й вихідна огорожа ──────────────────────────────────────
    f.append(arrow(1025, BY + BH + 4, 1025, 306, color=FIELD))
    f.append(fitbox(930, 310, 250, 62, "переривання:\nробота скінчилася", size=12,
                    fill="#eaf7ee", stroke=FIELD))
    f.append(arrow(1055, 374, 1055, 414, color=FIELD))
    f.append(fitbox(860, 418, 320, 62,
                    "вихідна огорожа падає —\nхто чекав, той прокидається", size=12,
                    fill="#eaf7ee", stroke=FIELD))

    f.append(text(40, 508,
                  "Між поданням і виконанням лежить час, і завдання переживає його в ядрі, а не в програмі.",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'submit-path.svg'), W, H, *f)


def fig_pipeline_depth():
    """Процесор іде на кадр попереду — саме тому подання не блокує."""
    W, H = 1140, 430
    f = []

    ROW1, ROW2, BAR = 96, 208, 52

    f.append(text(40, ROW1 + 32, "процесор", size=13, anchor="start"))
    f.append(text(40, ROW2 + 32, "GPU", size=13, anchor="start"))

    cpu = [(160, 380, "будує кадр N"), (380, 600, "кадр N+1"), (600, 820, "кадр N+2")]
    for x0, x1, label in cpu:
        f.append(fitbox(x0, ROW1, x1 - x0, BAR, label, size=12, fill="#eef2ff", stroke=NEG))

    gpu = [(390, 700, "виконує кадр N"), (700, 1010, "виконує кадр N+1")]
    for x0, x1, label in gpu:
        f.append(fitbox(x0, ROW2, x1 - x0, BAR, label, size=12, fill="#eaf7ee", stroke=FIELD))

    for x, label in ((380, "подання N"), (600, "подання N+1")):
        f.append(line(x, ROW1 + BAR + 4, x, ROW2 - 6, color=MUTED, sw=1.2, dash="5,4"))
        f.append(text(x, ROW1 + BAR + 26, label, size=11, color=MUTED))

    f.append(text(650, 310,
                  "подання N+1 приходить, поки GPU ще жує кадр N, — цю різницю завдання пересидить у планувальнику",
                  size=12, color=MUTED))

    f.append(arrow(160, 344, 1050, 344, color=INK))
    f.append(text(1062, 348, "час", size=12, anchor="start"))

    f.append(text(40, 404,
                  "Глибина конвеєра — це і є запас, за рахунок якого GPU не простоює; платить за неї затримка кадру.",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'pipeline-depth.svg'), W, H, *f)


def fig_sched_callbacks():
    """Життєвий цикл завдання: де кличе драйвер, а де кличуть драйвера."""
    W, H = 1180, 766
    f = []

    COL_X, COL_W, BOX_H = 140, 620, 62
    CX = COL_X + COL_W // 2          # 450

    f.append(text(COL_X, 40,
                  "драйвер кличе планувальник — усе це в ioctl подання",
                  size=13, color=NEG, anchor="start"))

    push_steps = [
        (58,  "drm_sched_job_init()  ·  завести завдання, прив'язати до сутності, оголосити кредит"),
        (136, "drm_sched_job_add_dependency()  ·  віддати планувальникові вхідні огорожі"),
        (214, "drm_sched_job_arm()  ·  народилася вихідна огорожа — відступати вже пізно"),
        (292, "drm_sched_entity_push_job()  ·  завдання в черзі, ioctl повертається негайно"),
    ]
    for y, label in push_steps:
        f.append(fitbox(COL_X, y, COL_W, BOX_H, label, size=12,
                        fill="#eef2ff", stroke=NEG))
    for y, _ in push_steps[:-1]:
        f.append(arrow(CX, y + BOX_H, CX, y + BOX_H + 14, color=NEG))

    # ── очікування в планувальнику ────────────────────────────────────────
    f.append(arrow(CX, 354, CX, 370, color=MUTED))
    f.append(fitbox(180, 372, 540, 56,
                    "чекає: доки не впадуть усі вхідні огорожі, доки в кільці немає кредиту, "
                    "доки сутність зайнята попереднім",
                    size=12, fill=BG, stroke=MUTED))
    f.append(arrow(CX, 428, CX, 440, color=FIELD))

    f.append(text(COL_X, 466,
                  "планувальник кличе драйвер — у своєму потоці, у своєму темпі",
                  size=13, color=FIELD, anchor="start"))

    run_steps = [
        (480, "prepare_job()  ·  останнє «ще чогось чекаємо?» — або NULL"),
        (558, "run_job()  ·  покласти пакет у кільце, подзвонити, повернути апаратну огорожу"),
        (636, "free_job()  ·  огорожа впала — звільнити завдання"),
    ]
    for y, label in run_steps:
        f.append(fitbox(COL_X, y, COL_W, BOX_H, label, size=12,
                        fill="#eaf7ee", stroke=FIELD))
    for y, _ in run_steps[:-1]:
        f.append(arrow(CX, y + BOX_H, CX, y + BOX_H + 14, color=FIELD))

    # ── бічна гілка: строк вийшов ─────────────────────────────────────────
    f.append(text(790, 542, "строк", size=11, color=POS))
    f.append(arrow(762, 589, 818, 589, color=POS))
    f.append(fitbox(820, 558, 320, 90,
                    "timedout_job()  ·  спинити, скинути рушій або контекст, "
                    "повернути DRM_GPU_SCHED_STAT_*",
                    size=12, fill="#fdeeec", stroke=POS))

    f.append(text(COL_X, 730,
                  "Між четвертим і п'ятим кроком лежить уся робота планувальника — "
                  "драйвер про неї не знає нічого.",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'sched-callbacks.svg'), W, H, *f)


if __name__ == '__main__':
    fig_ring_and_batch()
    fig_submit_path()
    fig_pipeline_depth()
    fig_sched_callbacks()
    print("ok")
