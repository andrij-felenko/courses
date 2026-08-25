# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: що таке legacy насправді — не «старе», а «не можу міняти безпечно» ──
def fig_what_is_legacy():
    W, H = 760, 470
    els = []
    els.append(text(W/2, 30, "«Старе» — не та вісь. Справжня — «чи можу міняти безпечно?»", size=16, bold=True))

    # Хибна вісь (закреслена): вік. Рамки-обгортки без тексту-по-центру,
    # напис — угорі рамки, а закреслення веде нижнім порожнім поясом (повз текст).
    els.append(text(W/2, 66, "хибний поділ — за віком", size=13, color=MUTED, italic=True))
    els.append(rect(70, 80, 290, 58, fill="#eef1f4", stroke=LINE))
    els.append(rect(400, 80, 290, 58, fill="#eef1f4", stroke=LINE))
    els.append(text(215, 100, "старий код", size=15, color=MUTED, bold=True))
    els.append(text(545, 100, "новий код", size=15, color=MUTED, bold=True))
    # закреслення проходить нижнім поясом рамок (y≈124), під написами (y≈100)
    els.append(line(78, 128, 352, 118, color=MUTED, sw=2))
    els.append(line(408, 118, 682, 128, color=MUTED, sw=2))

    # Справжня вісь: безпека зміни
    els.append(text(W/2, 186, "справжній поділ", size=13, color=INK, italic=True))

    # Ліва колонка: НЕ-legacy (зелена)
    els.append(fitbox(70, 204, 290, 46, "не-legacy", size=16, fill="#eafaf1", stroke=FIELD, sw=2, color=FIELD, bold=True))
    els.append(fitbox(70, 262, 290, 42, "намір відновлюваний", size=13, fill=BG, stroke=FIELD))
    els.append(fitbox(70, 312, 290, 42, "є страхувальна сітка (тести)", size=13, fill=BG, stroke=FIELD))
    els.append(fitbox(70, 362, 290, 46, "зміну видно — впевнено", size=13, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True))

    # Права колонка: legacy (червона)
    els.append(fitbox(400, 204, 290, 46, "legacy", size=16, fill="#fdecea", stroke=POS, sw=2, color=POS, bold=True))
    els.append(fitbox(400, 262, 290, 42, "намір втрачено", size=13, fill=BG, stroke=POS))
    els.append(fitbox(400, 312, 290, 42, "сітки немає", size=13, fill=BG, stroke=POS))
    els.append(fitbox(400, 362, 290, 46, "зміна наосліп — страшно", size=13, fill="#fdecea", stroke=POS, color=POS, bold=True))

    # вертикальна межа
    els.append(line(W/2, 200, W/2, 412, color=MUTED, sw=1, dash="4,4"))

    els.append(text(W/2, 440, "Код без сітки й без відновлюваного наміру — legacy, навіть якщо йому тиждень.",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, 'what-is-legacy.svg'), W, H, *els)


# ── Фігура 2: страти — файл legacy як шари минулих виправлень ──
def fig_strata():
    W, H = 760, 470
    els = []
    els.append(text(W/2, 30, "Рядок legacy — це шари минулих виправлень, кожен колись щось лагодив",
                    size=15, bold=True))

    # стовпчик страт, зверху вниз — від нового до старого
    strata = [
        ("верхній шар: свіжа латка на баг #4821", "#eef1f4", INK),
        ("обхід крашу драйвера — тимчасово, 3 роки тому", "#e9edf2", INK),
        ("+300 мс затримки: чекаємо повільний диск", "#e3e8ee", INK),
        ("if (year==1999) — фікс Y2K-подібного вузла", "#dde3ea", INK),
        ("нижній шар: первісний намір, документів нема", "#d6dde6", INK),
    ]
    x, w = 70, 470
    y = 70
    hgt = 60
    for i, (s, fill, col) in enumerate(strata):
        els.append(fitbox(x, y, w, hgt-8, s, size=13, fill=fill, stroke=LINE, color=col))
        y += hgt

    # стрілка-«розкоп» униз ліворуч від стовпчика
    els.append(text(x-22, 60, "нове", size=12, color=MUTED, anchor="end"))
    els.append(text(x-22, y-8, "старе", size=12, color=MUTED, anchor="end"))
    els.append(arrow(x-14, 74, x-14, y-16, color=MUTED, sw=2))

    # праворуч — застереження Честертона
    fx = 570
    els.append(fitbox(fx, 96, 150, 96,
                      "Не знаєш,\nнавіщо цей\nпаркан —\nне зноси", size=13,
                      fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True))
    els.append(text(fx+75, 214, "паркан Честертона", size=11, color=MUTED, italic=True))
    els.append(arrow(fx-6, 150, x+w+8, 150, color=FIELD, sw=1.8))
    els.append(arrow(fx-6, 168, x+w+8, 280, color=FIELD, sw=1.8))

    els.append(text(W/2, 456, "Археолог читає згори вниз: кожен «дивний» рядок мав причину, яку треба знайти до правки.",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, 'strata.svg'), W, H, *els)


# ── Фігура 3: характеризаційний тест — сітка ДО того, як торкнутись ──
def fig_safety_net():
    W, H = 780, 430
    els = []
    els.append(text(W/2, 30, "Спершу — сітка, тоді зміна: характеризаційний тест ловить регресії",
                    size=15, bold=True))

    # крок 1: сфотографувати поведінку
    els.append(fitbox(40, 70, 210, 88,
                      "1. Сфотографувати\nповедінку як є\n(не як мала б бути)", size=13,
                      fill="#eef1f4", stroke=LINE, bold=False))
    # крок 2: шов
    els.append(fitbox(285, 70, 210, 88,
                      "2. Прорізати шов —\nточку, де підставити\nтест", size=13,
                      fill="#eef1f4", stroke=LINE))
    # крок 3: міняти під сіткою
    els.append(fitbox(530, 70, 210, 88,
                      "3. Міняти код —\nсітка тримає\nстару поведінку", size=13,
                      fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True))
    els.append(arrow(250, 114, 285, 114, sw=2))
    els.append(arrow(495, 114, 530, 114, sw=2))

    # нижня частина: сама сітка — зафіксовані пари вхід→вихід, стовпчиком
    els.append(text(230, 202, "сітка = зафіксовані пари вхід → поточний вихід", size=13, color=INK, italic=True))
    cells = [
        ("вхід A", "0x1F"),
        ("вхід B", "-273"),
        ("вхід C", '"ok"'),
    ]
    lx = 60          # ліва рамка (вхід)
    rx = 300         # права рамка (вихід)
    bw = 130
    ry = 220
    for a, b in cells:
        els.append(fitbox(lx, ry, bw, 40, a, size=13, fill=BG, stroke=LINE))
        els.append(text(lx+bw+27, ry+26, "→", size=18, color=INK))
        els.append(fitbox(rx, ry, bw, 40, b, size=13, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True))
        ry += 52

    # праворуч від сітки — «зламав → падає одразу»
    els.append(fitbox(540, 236, 210, 108,
                      "Зміна зламала\nповедінку C →\nтест падає\nтут-таки", size=13,
                      fill="#fdecea", stroke=POS, color=POS, bold=True))
    els.append(arrow(rx+bw+8, 350, 540, 320, color=POS, sw=1.8))

    els.append(text(W/2, 414, "Тест описує, що код РОБИТЬ зараз, а не що мав би. Це страховка на час перебудови.",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, 'safety-net.svg'), W, H, *els)


# ── Фігура 4 (для вставки proj-): чотири кроки алгоритму Фезерса ──
def fig_feathers_algorithm():
    W, H = 820, 500
    els = []
    els.append(text(W/2, 32, "Алгоритм зміни legacy за Фезерсом: порядок незламний",
                    size=16, bold=True))

    # чотири кроки згори вниз; широкі рамки, щоб написи не тислися
    bx, bw = 250, 320          # ліва межа й ширина рамок кроків
    steps = [
        ("1. Знайти точку зміни\nй точку відчуття", "#eef1f4", INK, LINE, False),
        ("2. Прорізати шов —\nрозірвати приховані залежності", "#eef1f4", INK, LINE, False),
        ("3. Накинути\nхарактеризаційну сітку", "#eef1f4", INK, LINE, False),
        ("4. І лише тоді —\nміняти по-справжньому", "#eafaf1", FIELD, FIELD, True),
    ]
    y, hgt, gap = 66, 74, 30
    centers = []
    for s, fill, col, st, bold in steps:
        els.append(fitbox(bx, y, bw, hgt, s, size=14, fill=fill, stroke=st, color=col, bold=bold, sw=2 if bold else 1.5))
        centers.append(y + hgt/2)
        y += hgt + gap
    # стрілки між кроками (по центру стовпчика, у проміжках)
    for i in range(3):
        y0 = 66 + (i+1)*hgt + i*gap
        els.append(arrow(bx+bw/2, y0, bx+bw/2, y0+gap, sw=2))

    # ліворуч від кроку 2 — застереження: поведінку НЕ чіпаємо
    els.append(fitbox(20, centers[1]-34, 200, 68,
                      "поведінку тут\nне міняємо —\nні на копійку", size=12.5,
                      fill=BG, stroke=POS, color=POS, bold=True))
    els.append(arrow(222, centers[1], bx-4, centers[1], color=POS, sw=1.8))

    # ліворуч від кроку 3 — фіксуємо ФАКТИЧНЕ, не правильне
    els.append(fitbox(20, centers[2]-34, 200, 68,
                      "фіксуємо\nфактичну поведінку,\nне «правильну»", size=12.5,
                      fill=BG, stroke=FIELD, color=FIELD, bold=True))
    els.append(arrow(222, centers[2], bx-4, centers[2], color=FIELD, sw=1.8))

    # праворуч від кроку 4 — під сіткою зміну ВИДНО
    els.append(fitbox(bx+bw+24, centers[3]-30, 210, 60,
                      "будь-яку регресію\nвидно в мить появи", size=12.5,
                      fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True))
    els.append(arrow(bx+bw+22, centers[3], bx+bw+4, centers[3], color=FIELD, sw=1.8))

    els.append(text(W/2, H-16,
                    "Переставиш кроки — накидатимеш сітку на код, який щойно сам і зсунув.",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, 'feathers-algorithm.svg'), W, H, *els)


# ── Фігура 5 (для вставки hist-): шлях думки в часі — Честертон → Кеннеді → інженерія ──
def fig_fence_timeline():
    W, H = 780, 430
    els = []
    els.append(text(W/2, 30, "Одна думка, три форми: як «спершу зрозумій, тоді чіпай» дійшло до коду",
                    size=15, bold=True))

    # горизонтальна вісь часу
    axis_y = 250
    els.append(line(60, axis_y, 720, axis_y, color=MUTED, sw=2))
    els.append(arrow(700, axis_y, 724, axis_y, color=MUTED, sw=2))
    els.append(text(722, axis_y + 24, "час", size=12, color=MUTED, anchor="end", italic=True))

    # три віхи: x-координата вузла, рік, хто, що це, заливка/колір
    nodes = [
        (170, "1929", ["Честертон,", "«The Thing»"],
         "розгорнутий діалог\nреформаторів про паркан", "#eef1f4", INK),
        (400, "1945", ["Кеннеді,", "щоденник"],
         "пружне гасло-парафраз:\n«не знімай паркан…»", "#eef1f4", INK),
        (630, "2004", ["Фезерс,", "legacy-код"],
         "техніка: характери-\nзаційний тест —\nсітка на поведінку", "#eafaf1", FIELD),
    ]

    for nx, year, label, note, fill, col in nodes:
        # картка-хто — над віссю, з запасом ширини під написи
        bw, bh = 190, 54
        els.append(fitbox(nx - bw/2, 70, bw, bh, "\n".join(label), size=14,
                          fill=fill, stroke=col, color=col, bold=True))
        # нотатка-що це — між карткою і віссю
        els.append(fitbox(nx - bw/2, 138, bw, 74, note, size=12,
                          fill=BG, stroke=col, color=INK))
        # штрихова лінія від нотатки до вузла (у порожньому поясі, повз написи)
        els.append(line(nx, 212, nx, axis_y - 8, color=col, sw=1.4, dash="3,3"))
        # вузол на осі — малюємо ПІСЛЯ лінії, щоб кружок був згори
        els.append(circle(nx, axis_y, 7, fill=col, stroke=col, sw=2))
        # рік — під віссю
        els.append(text(nx, axis_y + 26, year, size=15, color=col, bold=True))

    # стрілки переходу між віхами — уздовж осі, у порожніх проміжках між вузлами
    els.append(arrow(285, axis_y, 315, axis_y, color=MUTED, sw=1.8))
    els.append(arrow(515, axis_y, 545, axis_y, color=MUTED, sw=1.8))
    els.append(text(300, axis_y - 12, "стиснули", size=11, color=MUTED, italic=True))
    els.append(text(530, axis_y - 12, "оснастили", size=11, color=MUTED, italic=True))

    els.append(text(W/2, 352, "Ідея — Честертонова; знамените гасло — парафраз Кеннеді; робочий інструмент дала інженерія.",
                    size=12.5, color=INK, italic=True))
    els.append(text(W/2, 388, "У кожному переході форма мінялась, а суть лишалась незмінною.",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, 'fence-timeline.svg'), W, H, *els)


if __name__ == '__main__':
    fig_what_is_legacy()
    fig_strata()
    fig_safety_net()
    fig_feathers_algorithm()
    fig_fence_timeline()
    print("ok")
