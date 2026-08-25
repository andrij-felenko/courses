# -*- coding: utf-8 -*-
"""Фігури до статті «Контроль версій і git». Вивід — ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def commit_node(cx, cy, label, hid, r=26, fill=FILL, stroke=INK):
    """Кружок-коміт із коротким хешем під ним."""
    s = circle(cx, cy, r, fill=fill, stroke=stroke, sw=2)
    s += text(cx, cy + 5, label, size=15, bold=True)
    s += text(cx, cy + r + 16, hid, size=12, color=MUTED)
    return s


# ── 1. Історія як ланцюг знімків з іменем-хешем ─────────────────────────────
def fig_snapshots():
    W, H = 760, 300
    parts = []
    parts.append(text(W / 2, 30, "Кожен коміт — повний знімок, названий за вмістом", size=16, bold=True))

    ys = 130
    xs = [130, 330, 530]
    ids = ["a3f1c2", "7e0b94", "d51ff8"]
    labels = ["C1", "C2", "C3"]
    # стрілки «дитина → батько» (проти течії часу)
    for i in range(1, 3):
        parts.append(arrow(xs[i] - 26, ys, xs[i - 1] + 26, ys, color=NEG, sw=2))
    for x, lab, hid in zip(xs, labels, ids):
        parts.append(commit_node(x, ys, lab, hid))
    parts.append(text(xs[0], ys - 46, "перший", size=12, color=MUTED))
    parts.append(text((xs[1] + xs[2]) / 2, ys - 18, "parent", size=12, color=NEG))

    # знімок під кожним комітом: три файли, змінений — червоний
    snap_y = 210
    files = [["main.c", "led.c", "cfg.h"],
             ["main.c", "led.c", "cfg.h"],
             ["main.c", "led.c", "cfg.h"]]
    changed = [set(), {"led.c"}, {"main.c"}]
    for x, fs, ch in zip(xs, files, changed):
        for j, fn in enumerate(fs):
            hot = fn in ch
            b = fitbox(x - 55, snap_y + j * 24, 110, 20, fn,
                       size=12, pad=4,
                       fill=("#fdecea" if hot else FILL),
                       stroke=(POS if hot else LINE),
                       color=(POS if hot else INK))
            parts.append(b)
    parts.append(text(W / 2, H - 8,
                      "змінив один файл — інші два коміт переписує на той самий вміст (той самий хеш)",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "snapshots.svg"), W, H, *parts)


# ── 2. Гілка й злиття: граф комітів ─────────────────────────────────────────
def fig_branch_merge():
    W, H = 780, 340
    parts = []
    parts.append(text(W / 2, 30, "Гілка — рухома мітка; злиття зводить дві лінії в один коміт", size=16, bold=True))

    main_y = 130
    feat_y = 240
    # головна лінія
    mx = [110, 250, 660]  # C1, C2, M(merge)
    # гілка feature
    fx = [400, 540]       # F1, F2

    # ребра головної: C1<-C2
    parts.append(line(mx[0] + 24, main_y, mx[1] - 24, main_y, color=INK, sw=2))
    # відгалуження від C2 вниз до F1
    parts.append(line(mx[1] + 18, main_y + 14, fx[0] - 20, feat_y - 14, color=FIELD, sw=2))
    parts.append(line(fx[0] + 24, feat_y, fx[1] - 24, feat_y, color=FIELD, sw=2))
    # merge-коміт M має двох батьків: з C2 (через верх) і з F2 (знизу)
    parts.append(line(mx[1] + 24, main_y, mx[2] - 24, main_y, color=INK, sw=2))
    parts.append(line(fx[1] + 18, feat_y - 14, mx[2] - 20, main_y + 14, color=FIELD, sw=2))

    parts.append(commit_node(mx[0], main_y, "C1", "a3f1c2"))
    parts.append(commit_node(mx[1], main_y, "C2", "7e0b94"))
    parts.append(commit_node(mx[2], main_y, "M", "b2c9e1", fill="#eafaf0", stroke=FIELD))
    parts.append(commit_node(fx[0], feat_y, "F1", "10ab55", fill="#eafaf0", stroke=FIELD))
    parts.append(commit_node(fx[1], feat_y, "F2", "9d7c3a", fill="#eafaf0", stroke=FIELD))

    # мітки-гілки
    b1 = fitbox(mx[2] + 44, main_y - 14, 70, 26, "main", size=13, pad=4, fill=FILL, stroke=INK, bold=True)
    parts.append(b1)
    b2 = fitbox(fx[1] + 44, feat_y - 14, 84, 26, "feature", size=13, pad=4, fill="#eafaf0", stroke=FIELD, bold=True)
    parts.append(b2)

    parts.append(text(fx[0] - 40, feat_y + 44, "відгалужено від C2", size=12, color=FIELD))
    parts.append(text(mx[2], main_y - 46, "два батьки", size=12, color=FIELD))
    render(os.path.join(IMG, "branch-merge.svg"), W, H, *parts)


# ── 3. Розподілена модель: кожна копія — повний репозиторій ──────────────────
def fig_distributed():
    W, H = 780, 330
    parts = []
    parts.append(text(W / 2, 30, "Розподілена модель: у кожного — повна історія, не лише робоча копія", size=15, bold=True))

    # центральний віддалений
    cx, cy = W / 2, 120
    r = 40
    parts.append(circle(cx, cy, r, fill="#eef2ff", stroke=NEG, sw=2))
    parts.append(text(cx, cy - 4, "remote", size=13, bold=True, color=NEG))
    parts.append(text(cx, cy + 14, "(origin)", size=12, color=MUTED))

    # три розробники внизу
    devs = [("Аня", 150), ("Богдан", W / 2), ("Влад", W - 150)]
    dy = 250
    for name, x in devs:
        parts.append(circle(x, dy, 34, fill=FILL, stroke=INK, sw=2))
        parts.append(text(x, dy - 2, name, size=13, bold=True))
        parts.append(text(x, dy + 15, "повна копія", size=11, color=MUTED))
        # двобічний обмін
        parts.append(line(x, dy - 34, cx + (x - cx) * 0.28, cy + 30, color=INK, sw=1.6, dash="5,4"))
    parts.append(text(cx, cy + 66, "push / fetch — обмін комітами, а не «отримати дозвіл»",
                      size=12, color=MUTED))
    parts.append(text(W / 2, H - 12,
                      "працювати, комітити й дивитися історію можна без мережі — усе локально",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "distributed.svg"), W, H, *parts)


# ── 4. Три точки злиття: база й дві сторони; таблиця рішень по рядку ─────────
def fig_three_points():
    W, H = 780, 470
    parts = []
    parts.append(text(W / 2, 30, "Три версії одного файлу — і рішення по кожному рядку", size=16, bold=True))

    # три колонки-версії
    col_w = 150
    xs = [140, 390, 640]     # BASE, OURS, THEIRS
    top = 66
    row_h = 30
    n = 5
    heads = ["БАЗА", "НАШЕ (HEAD)", "ЇХНЄ (MERGE_HEAD)"]
    hcol = [MUTED, NEG, POS]
    # рядки-приклади: (base, ours, theirs)
    rows = [
        ("init();",   "init();",     "init();"),      # ніхто не чіпав
        ("setup();",  "setup(2);",   "setup();"),     # лише наше
        ("loop();",   "loop();",     "loop(10);"),    # лише їхнє
        ("a=1;",      "a=1;",        "a=1;"),          # ніхто (спокій)
        ("led(0);",   "led(HI);",    "led(LO);"),     # обидва інакше → конфлікт
    ]
    verdict = ["без змін", "беремо НАШЕ", "беремо ЇХНЄ", "без змін", "КОНФЛІКТ"]
    vcol = [MUTED, NEG, POS, MUTED, POS]

    # заголовки колонок
    for x, hd, c in zip(xs, heads, hcol):
        parts.append(fitbox(x - col_w / 2, top, col_w, 24, hd, size=12, pad=4,
                            fill=FILL, stroke=c, color=c, bold=True))

    # клітинки
    for r, (b, o, t) in enumerate(rows):
        y = top + 30 + r * row_h
        cells = [b, o, t]
        # де змінено відносно бази?
        changed = [False, o != b, t != b]
        conflict = (o != b and t != b and o != t)
        for k, (x, val, ch) in enumerate(zip(xs, cells, changed)):
            if conflict and k > 0:
                fill, st, cl = "#fdecea", POS, POS
            elif ch:
                fill, st, cl = ("#eaf0fd", NEG, NEG) if k == 1 else ("#fdecea", POS, POS)
            else:
                fill, st, cl = FILL, LINE, INK
            parts.append(fitbox(x - col_w / 2, y, col_w, row_h - 6, val,
                                size=12, pad=4, fill=fill, stroke=st, color=cl))

    # стрілка й вердикт праворуч
    vx = W - 60
    for r in range(n):
        y = top + 30 + r * row_h + (row_h - 6) / 2
        parts.append(text(xs[2] + col_w / 2 + 12, y + 4, "→", size=15, color=MUTED, anchor="start"))
    # підписи-вердикти під таблицею окремим стовпчиком праворуч від THEIRS зробили б тісно —
    # виносимо їх у легенду знизу
    ly = top + 30 + n * row_h + 24
    parts.append(text(W / 2, ly, "правило по рядку (зіставлення з базою):", size=13, bold=True))
    leg = [
        ("жоден бік ≠ бази — лишаємо як є", INK, FILL, LINE),
        ("змінив лише один бік — беремо його версію", NEG, "#eaf0fd", NEG),
        ("обидва змінили той самий рядок по-різному — КОНФЛІКТ", POS, "#fdecea", POS),
    ]
    for i, (s, cl, fill, st) in enumerate(leg):
        yy = ly + 22 + i * 30
        parts.append(fitbox(90, yy, W - 180, 24, s, size=12, pad=6, fill=fill, stroke=st, color=cl))

    render(os.path.join(IMG, "three-points.svg"), W, H, *parts)


# ── 5. Merge base у графі: найближчий спільний предок ───────────────────────
def fig_merge_base():
    W, H = 780, 300
    parts = []
    parts.append(text(W / 2, 30, "Merge base — найближчий спільний предок двох гілок", size=16, bold=True))

    y_main = 120
    y_feat = 220
    # спільний стовбур: A ← B(=base)
    A = (110, y_main)
    B = (260, y_main)     # merge base
    # main тягнеться далі вправо: M1, M2(=HEAD)
    M1 = (430, y_main)
    M2 = (600, y_main)
    # feature вниз: F1, F2(=MERGE_HEAD)
    F1 = (430, y_feat)
    F2 = (600, y_feat)

    def edge(p, q, c, sw=2):
        parts.append(line(q[0] - 26, q[1], p[0] + 26, p[1], color=c, sw=sw) if p[1] == q[1]
                     else line(q[0] - 20, q[1] - 14 if q[1] > p[1] else q[1] + 14,
                               p[0] + 20, p[1] + 14 if q[1] > p[1] else p[1] - 14, color=c, sw=sw))

    edge(A, B, INK)
    edge(B, M1, INK); edge(M1, M2, INK)
    edge(B, F1, FIELD); edge(F1, F2, FIELD)

    parts.append(commit_node(*A, "A", "a3f1c2"))
    parts.append(commit_node(*B, "B", "7e0b94", fill="#fff6da", stroke="#b8860b"))
    parts.append(commit_node(*M1, "M1", "c11d02"))
    parts.append(commit_node(*M2, "M2", "d51ff8"))
    parts.append(commit_node(*F1, "F1", "10ab55", fill="#eafaf0", stroke=FIELD))
    parts.append(commit_node(*F2, "F2", "9d7c3a", fill="#eafaf0", stroke=FIELD))

    parts.append(text(B[0], B[1] - 42, "merge base", size=12, bold=True, color="#b8860b"))
    parts.append(fitbox(M2[0] - 20, y_main - 66, 96, 24, "HEAD (наше)", size=12, pad=4,
                        fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))
    parts.append(fitbox(F2[0] - 20, y_feat + 30, 128, 24, "MERGE_HEAD (їхнє)", size=12, pad=4,
                        fill="#fdecea", stroke=POS, color=POS, bold=True))
    parts.append(text(W / 2, H - 14,
                      "найдальша точка, звідки обидві гілки дійшли до своїх кінців — від неї й міряють різницю",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "merge-base.svg"), W, H, *parts)


# ── 6. Хроніка народження git (вставка hist-git-bitkeeper) ──────────────────
def fig_git_birth_timeline():
    W, H = 880, 350
    parts = []
    parts.append(text(W / 2, 30, "Десять днів, що народили git — від кризи BitKeeper до 1.0", size=16, bold=True))

    # три смуги-фази
    phases = [
        (40, 250, "#eef2ff", NEG, "Криза BitKeeper"),
        (272, 566, "#eafaf0", FIELD, "Десять днів git"),
        (588, 840, "#fdf3e6", "#b8860b", "Дозрівання"),
    ]
    band_y, band_h = 74, 200
    for x0, x1, fill, edge, cap in phases:
        parts.append(rect(x0, band_y, x1 - x0, band_h, fill=fill, stroke=edge, sw=1.6, rx=8))
        parts.append(text((x0 + x1) / 2, band_y - 9, cap, size=13, bold=True, color=edge))

    # горизонтальна вісь часу
    axis_y = 165
    parts.append(line(52, axis_y, W - 30, axis_y, color=MUTED, sw=2))

    # події: (x, дата, суть, колір, бік)
    events = [
        (100, "2002",      "ядро на\nBitKeeper",             NEG,       "up"),
        (190, "квіт. 2005", "SourcePuller —\nліцензію відкликано", NEG,  "down"),
        (320, "3 квіт.",    "старт\nрозробки",               FIELD,     "up"),
        (405, "6 квіт.",    "оголошення",                    FIELD,     "down"),
        (490, "7 квіт.",    "самохостинг",                   FIELD,     "up"),
        (635, "16 черв.",   "ядро 2.6.12\nна git",           "#b8860b", "down"),
        (720, "26 лип.",    "супровід —\nХамано",            "#b8860b", "up"),
        (805, "21 груд.",   "версія 1.0",                    "#b8860b", "down"),
    ]
    for x, d, s, col, side in events:
        parts.append(circle(x, axis_y, 6, fill=BG, stroke=col, sw=2.4))
        if side == "up":
            parts.append(line(x, axis_y - 6, x, axis_y - 22, color=col, sw=1.4))
            parts.append(text(x, axis_y - 28, d, size=12, bold=True, color=col))
            parts.append(mtext(x, axis_y - 28 - 15, s, size=11, color=MUTED))
        else:
            parts.append(line(x, axis_y + 6, x, axis_y + 22, color=col, sw=1.4))
            parts.append(text(x, axis_y + 34, d, size=12, bold=True, color=col))
            parts.append(mtext(x, axis_y + 34 + 15, s, size=11, color=MUTED))

    parts.append(text(W / 2, H - 12,
                      "розподіленість і швидкість git — це відповіді на цю кризу, а не смаки автора",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "git-birth-timeline.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_snapshots()
    fig_branch_merge()
    fig_distributed()
    fig_three_points()
    fig_merge_base()
    fig_git_birth_timeline()
    print("figures written to", IMG)
