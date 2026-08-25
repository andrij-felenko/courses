# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def host_plugins_clean():
    W, H = 780, 480
    f = []
    cx, cy = W / 2, H / 2
    core_w, core_h = 210, 120

    # плагіни навколо: (кут-сторона) верх, низ, ліво, право
    gap = 30
    pw, ph = 150, 58

    layout = [
        # (sx, sy, dx, dy, name)
        (cx,              cy - core_h/2, 0, -1, "Python"),
        (cx,              cy + core_h/2, 0,  1, "Markdown"),
        (cx - core_w/2,   cy,           -1,  0, "Темна тема"),
        (cx + core_w/2,   cy,            1,  0, None),
    ]

    # спершу штекери (під усім), потім гнізда, ядро, плагіни, підписи
    for sx, sy, dx, dy, name in layout:
        ex = sx + dx * gap
        ey = sy + dy * gap
        col = FIELD if name else MUTED
        f.append(line(sx, sy, ex, ey, color=col, sw=3))

    # ядро
    f.append(rect(cx - core_w/2, cy - core_h/2, core_w, core_h,
                  fill="#eef2f7", stroke=INK, sw=2.4, rx=12))
    f.append(text(cx, cy - 14, "ЯДРО", size=20, bold=True))
    f.append(text(cx, cy + 10, "(host)", size=14, color=MUTED))
    f.append(text(cx, cy + 32, "гукає всіх через одну форму", size=11, color=MUTED, italic=True))

    # гнізда-пази на краях ядра
    for sx, sy, dx, dy, name in layout:
        if dx == 0:
            gw, gh = 38, 16
        else:
            gw, gh = 16, 38
        f.append(rect(sx - gw/2, sy - gh/2, gw, gh, fill="#ffffff", stroke=INK, sw=2, rx=3))

    # плагіни
    for sx, sy, dx, dy, name in layout:
        px = sx + dx * (gap + pw/2)
        py = sy + dy * (gap + ph/2)
        bx, by = px - pw/2, py - ph/2
        if name is None:
            f.append(rect(bx, by, pw, ph, fill=BG, stroke=MUTED, sw=1.6, rx=9))
            f.append(mtext(px, py - 2, ["вільне гніздо —", "тієї самої форми"],
                           size=11, color=MUTED))
        else:
            f.append(rect(bx, by, pw, ph, fill="#eaf6ee", stroke=FIELD, sw=2.2, rx=9))
            f.append(text(px, py - 6, "плагін", size=11, color=MUTED))
            f.append(text(px, py + 13, name, size=15, bold=True))

    return W, H, f


def loader_pipeline():
    """Конвеєр завантажувача: сканування -> завантаження -> звірка версії ->
    register(host). Кожна фаза може відхилити плагін у 'пропустити', не валячи ядро.
    Широкі колонки й окремий стовпчик відмов — щоб написи не накладалися."""
    W, H = 860, 560
    f = []

    # чотири фази-станції в один стовпець зліва
    col_x = 210          # центр колонки фаз
    box_w, box_h = 300, 66
    ys = [70, 175, 280, 385]
    labels = [
        ("1. Сканувати plugins/", "знайти файли-кандидати"),
        ("2. Завантажити модуль", "importlib / import() / dlopen"),
        ("3. Звірити версію контракту", "плагін.API == HOST_API?"),
        ("4. register(host)", "плагін вписує себе в реєстр"),
    ]

    # стрілки згори вниз між фазами (малюємо перші, щоб рамки лягли зверху)
    for i in range(len(ys) - 1):
        y1 = ys[i] + box_h
        y2 = ys[i + 1]
        f.append(arrow(col_x, y1, col_x, y2 - 2, color=INK, sw=2.2))

    # стовпчик відмов справа
    skip_x = 660
    skip_w, skip_h = 320, 66

    # де від кожної фази відходить гілка «не так»
    reject_from = [
        (1, "не Python-модуль / биткий файл", "виняток при завантаженні"),
        (2, "API 2, а ядро дає лише 3", "несумісна версія контракту"),
        (3, "register кинув виняток", "плагін упав під час реєстрації"),
    ]
    skip_ys = [175, 280, 385]

    # спершу горизонтальні стрілки-відгалуження (під рамками)
    for (fase_idx, _t, _s), sy in zip(reject_from, skip_ys):
        y_mid = ys[fase_idx] + box_h / 2
        # від правого краю фази — вправо, з вигином до станції відмови
        f.append(line(col_x + box_w/2, y_mid, skip_x - skip_w/2 - 40, y_mid, color=POS, sw=2))
        f.append(arrow(skip_x - skip_w/2 - 40, y_mid, skip_x - skip_w/2 - 2, sy + skip_h/2, color=POS, sw=2))

    # станції-відмови (червонясті)
    for (fase_idx, t, s), sy in zip(reject_from, skip_ys):
        bx, by = skip_x - skip_w/2, sy
        f.append(rect(bx, by, skip_w, skip_h, fill="#fdecea", stroke=POS, sw=2, rx=8))
        f.append(text(skip_x, sy + 26, t, size=13, bold=True, color="#a02419"))
        f.append(text(skip_x, sy + 47, s, size=11.5, color=MUTED))

    # фази-станції (поверх стрілок)
    for (t, s), y in zip(labels, ys):
        bx = col_x - box_w/2
        col = FIELD if "register" in t else INK
        fill = "#eaf6ee" if "register" in t else "#eef2f7"
        f.append(rect(bx, y, box_w, box_h, fill=fill, stroke=col, sw=2.2, rx=8))
        f.append(text(col_x, y + 26, t, size=14, bold=True))
        f.append(text(col_x, y + 47, s, size=11.5, color=MUTED))

    # спільний підсумок унизу: усі відмови течуть у «залогувати й далі»
    log_y = 480
    log_w, log_h = 300, 60
    lbx = skip_x - log_w/2
    f.append(rect(lbx, log_y, log_w, log_h, fill=BG, stroke=MUTED, sw=1.8, rx=8))
    f.append(text(skip_x, log_y + 25, "залогувати причину", size=13.5, bold=True, color=MUTED))
    f.append(text(skip_x, log_y + 45, "і взяти НАСТУПНИЙ плагін", size=12, color=MUTED))
    # вертикальна лінія від нижньої станції-відмови до підсумку
    last_skip_bottom = skip_ys[-1] + skip_h
    f.append(arrow(skip_x, last_skip_bottom, skip_x, log_y - 2, color=MUTED, sw=1.8))

    # ядро лишається живим — стрілка від register вниз-праворуч у «ядро працює далі»
    ok_y = 480
    ok_w, ok_h = 300, 60
    obx = col_x - ok_w/2
    f.append(rect(obx, ok_y, ok_w, ok_h, fill="#eaf6ee", stroke=FIELD, sw=2, rx=8))
    f.append(text(col_x, ok_y + 25, "ядро працює далі", size=13.5, bold=True, color="#1e7a43"))
    f.append(text(col_x, ok_y + 45, "з тими, що завантажились", size=12, color=MUTED))
    f.append(arrow(col_x, ys[-1] + box_h, col_x, ok_y - 2, color=FIELD, sw=2))

    return W, H, f


if __name__ == "__main__":
    W, H, frags = host_plugins_clean()
    render(os.path.join(OUT, "host-plugins.svg"), W, H, *frags)
    print("host-plugins.svg written")

    W, H, frags = loader_pipeline()
    render(os.path.join(OUT, "loader-pipeline.svg"), W, H, *frags)
    print("loader-pipeline.svg written")
