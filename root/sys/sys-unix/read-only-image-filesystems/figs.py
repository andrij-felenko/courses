# -*- coding: utf-8 -*-
"""Фігури до теми «Стиснені образи лише для читання: SquashFS і EROFS»."""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def grid_strip(f, x, y, w, h, step):
    """Схематична сітка блоків носія."""
    f.append(rect(x, y, w, h, fill="#ffffff", stroke=MUTED, sw=1.2, rx=0))
    k = x + step
    while k < x + w - 1:
        f.append(line(k, y, k, y + h, color=MUTED, sw=1.0))
        k += step


def fig_fixed_input_vs_output():
    W, H = 960, 610
    f = []

    # ─────────── SquashFS: рівні порції на вході ───────────
    f.append(text(480, 32, "SquashFS: рівний вхід", size=18, bold=True))

    x0 = 90
    f.append(text(46, 82, "вхід", size=12, color=MUTED))
    for i in range(4):
        f.append(fitbox(x0 + i * 195, 56, 195, 46, "128 КіБ", size=14))

    chunks = [(150, "48 КіБ"), (230, "74 КіБ"), (90, "29 КіБ"), (250, "80 КіБ")]
    in_centers = [x0 + i * 195 + 97 for i in range(4)]
    cx = x0
    out_centers = []
    f.append(text(46, 168, "вихід", size=12, color=MUTED))
    for w, lab in chunks:
        out_centers.append(cx + w / 2)
        f.append(fitbox(cx, 146, w, 46, lab, size=13, fill="#eef3fb"))
        cx += w
    for a, b in zip(in_centers, out_centers):
        f.append(arrow(a, 106, b, 142))

    # сітка блоків носія + межі шматків
    grid_strip(f, x0, 216, 780, 26, 40)
    f.append(text(x0, 264, "схематична сітка блоків носія", size=12,
                  color=MUTED, anchor="start"))
    bx = x0
    for w, _ in chunks:
        f.append(line(bx, 192, bx, 246, color=POS, sw=1.6, dash="5,4"))
        bx += w
    f.append(line(bx, 192, bx, 246, color=POS, sw=1.6, dash="5,4"))
    f.append(text(480, 296, "межі шматків падають куди випало", size=13, color=POS))

    # ─────────── EROFS: рівні порції на виході ───────────
    f.append(text(480, 358, "EROFS: рівний вихід", size=18, bold=True))

    ins = [(250, "16 КіБ"), (140, "9 КіБ"), (210, "13 КіБ"), (180, "11 КіБ")]
    cx = x0
    in_centers2 = []
    f.append(text(46, 408, "вхід", size=12, color=MUTED))
    for w, lab in ins:
        in_centers2.append(cx + w / 2)
        f.append(fitbox(cx, 382, w, 46, lab, size=13))
        cx += w

    f.append(text(46, 494, "вихід", size=12, color=MUTED))
    out_centers2 = []
    for i in range(4):
        f.append(fitbox(x0 + i * 120, 468, 120, 46, "4 КіБ", size=13, fill="#eef3fb"))
        out_centers2.append(x0 + i * 120 + 60)
    for a, b in zip(in_centers2, out_centers2):
        f.append(arrow(a, 432, b, 464))

    grid_strip(f, x0, 538, 780, 26, 40)
    f.append(text(x0, 586, "схематична сітка блоків носія", size=12,
                  color=MUTED, anchor="start"))
    for i in range(5):
        f.append(line(x0 + i * 120, 514, x0 + i * 120, 568, color=FIELD, sw=1.6, dash="5,4"))
    f.append(text(620, 586, "кожен кластер сідає рівно на блок", size=13, color=FIELD))

    render(os.path.join(IMG, "fixed-input-vs-output.svg"), W, H, *f)


def fig_read_amplification():
    W, H = 900, 360
    f = []
    f.append(text(450, 34, "Що коштує віддати одну сторінку 4 КіБ", size=17, bold=True))

    px_per_kib = 5.0
    x0 = 170

    # ── SquashFS
    f.append(text(x0, 76, "SquashFS, шматок 128 КіБ", size=14, bold=True, anchor="start"))
    f.append(rect(x0, 88, 128 * px_per_kib, 46, fill="#eef3fb"))
    f.append(rect(x0, 88, 4 * px_per_kib, 46, fill="#d8f0e0", stroke=FIELD, sw=1.6))
    f.append(text(x0 + 128 * px_per_kib + 14, 118, "×32", size=16,
                  color=POS, bold=True, anchor="start"))
    f.append(text(x0, 158, "прочитано й розтиснено 128 КіБ", size=12,
                  color=MUTED, anchor="start"))

    # ── EROFS
    f.append(text(x0, 218, "EROFS, кластер 4 КіБ", size=14, bold=True, anchor="start"))
    f.append(rect(x0, 230, 8 * px_per_kib, 46, fill="#eef3fb"))
    f.append(rect(x0, 230, 4 * px_per_kib, 46, fill="#d8f0e0", stroke=FIELD, sw=1.6))
    f.append(text(x0 + 8 * px_per_kib + 14, 260, "×2", size=16,
                  color=FIELD, bold=True, anchor="start"))
    f.append(text(x0, 300, "прочитано й розтиснено 8 КіБ", size=12,
                  color=MUTED, anchor="start"))

    # легенда
    f.append(rect(x0, 326, 20, 18, fill="#d8f0e0", stroke=FIELD, sw=1.4, rx=3))
    f.append(text(x0 + 32, 340, "сторінка, яку справді просили", size=12,
                  color=MUTED, anchor="start"))

    render(os.path.join(IMG, "read-amplification.svg"), W, H, *f)


def fig_image_stack():
    W, H = 820, 620
    f = []
    cx = 280
    rows = [
        ("Дерево, яке бачать програми", "звичайні open і read"),
        ("overlayfs", "верхній шар приймає всі зміни"),
        ("SquashFS або EROFS", "стиснена, лише для читання"),
        ("dm-verity", "хеш блока проти підпису"),
        ("/dev/loop0", "файл у вигляді блокового пристрою"),
        ("system.sqfs", "звичайний файл на носії"),
    ]
    ys = [50, 150, 250, 350, 450, 550]
    fills = [FILL, FILL, "#eef3fb", "#fdecea", FILL, FILL]

    for (label, note), y, fill in zip(rows, ys, fills):
        f.append(fitbox(cx - 155, y - 26, 310, 52, label, size=15, bold=True, fill=fill))
        f.append(text(470, y + 5, note, size=13, color=MUTED, anchor="start"))

    for i in range(len(ys) - 1):
        f.append(arrow(cx, ys[i + 1] - 30, cx, ys[i] + 30))

    render(os.path.join(IMG, "image-stack.svg"), W, H, *f)


def fig_two_amplifications():
    """Надлишок вводу (що бачить лічильник петлі) і надлишок розтискання."""
    W, H = 1000, 452
    f = []
    f.append(text(500, 34, "Два різні надлишки на одне читання 4 КіБ", size=17, bold=True))

    px = 4.6          # пікселів на КіБ
    x0 = 255
    labx = 238

    def band(y, kib, left_lines, right, color):
        h = 42
        f.append(rect(x0, y, 4 * px, h, fill="#d8f0e0", stroke=FIELD, sw=1.6))
        f.append(rect(x0 + 4 * px, y, (kib - 4) * px, h, fill="#eef3fb"))
        f.append(mtext(labx, y + h / 2 - 3, left_lines, size=12,
                       color=MUTED, anchor="end"))
        f.append(text(x0 + kib * px + 16, y + h / 2 + 5, right, size=14,
                      color=color, bold=True, anchor="start"))

    f.append(text(x0, 76, "SquashFS, -b 128K, zstd", size=15, bold=True, anchor="start"))
    band(90, 43, ["прочитано з пристрою", "лічильник loopN"], "43 КіБ → ×10.9", POS)
    band(152, 128, ["розтиснено", "системний час"], "128 КіБ → ×32", POS)

    f.append(text(x0, 246, "EROFS, -zlz4hc", size=15, bold=True, anchor="start"))
    band(260, 5, ["прочитано з пристрою", "лічильник loopN"], "5 КіБ → ×1.2", FIELD)
    band(322, 11, ["розтиснено", "системний час"], "11 КіБ → ×2.8", FIELD)

    f.append(rect(x0, 404, 22, 18, fill="#d8f0e0", stroke=FIELD, sw=1.4, rx=3))
    f.append(text(x0 + 34, 418, "4 КіБ, які програма справді просила", size=12,
                  color=MUTED, anchor="start"))

    render(os.path.join(IMG, "two-amplifications.svg"), W, H, *f)


def _r_model(x):
    """Модель байтів образу на байт даних; x = log2(розмір шматка)."""
    return 0.2125 + 1.990 / x + 490.0 / (2.0 ** x)


def fig_read_window():
    """Скільки шматків зачіпає одне читання S байтів із випадкового відступу."""
    W, H = 940, 330
    f = []
    f.append(text(470, 32, "Скільки шматків зачіпає одне читання", size=17, bold=True))

    cw, n = 130, 5
    sx, sy, sh = 190, 76, 46
    f.append(text(178, sy + 28, "шматки", size=12, color=MUTED, anchor="end"))
    for i in range(n):
        f.append(rect(sx + i * cw, sy, cw, sh, fill="#eef3fb"))
    edges = [sx + i * cw for i in range(n + 1)]

    sw_ = 58
    wy, wh = 168, 38
    f.append(text(178, wy + 24, "читання", size=12, color=MUTED, anchor="end"))
    cases = [
        (sx + cw + 34, "1 шматок", FIELD),
        (edges[3] - 27, "2 шматки", POS),
        (edges[4], "1 шматок", FIELD),
    ]
    for wx, lab, col in cases:
        f.append(rect(wx, wy, sw_, wh, fill="#d8f0e0", stroke=col, sw=1.8))
        f.append(text(wx + sw_ / 2, 238, lab, size=13, color=col, bold=True))
        f.append(line(wx, wy - 2, wx, sy + sh + 2, color=MUTED, sw=1.0, dash="4,4"))
        f.append(line(wx + sw_, wy - 2, wx + sw_, sy + sh + 2, color=MUTED, sw=1.0, dash="4,4"))

    f.append(text(470, 292,
                  "у середньому розтискається  B + S − 4 КіБ  байтів",
                  size=15, bold=True))
    render(os.path.join(IMG, "read-window-chunks.svg"), W, H, *f)


def fig_size_vs_cost():
    """Дві криві від розміру шматка: пласка щільність і лінійний надлишок."""
    W, H = 940, 516
    f = []
    f.append(text(470, 30, "Що купує й що коштує кожне подвоєння шматка",
                  size=17, bold=True))

    x0, x1 = 130, 850
    ybot, ytop = 400, 70            # ybot ↔ ×0.25, ytop ↔ ×256 (10 октав)
    per_unit = (x1 - x0) / 8.0
    per_oct = (ybot - ytop) / 10.0

    def px_(x):
        return x0 + (x - 12.0) * per_unit

    def py_(v):
        return ybot - (math.log(v, 2) + 2.0) * per_oct

    for v, lab in [(0.25, "×0.25"), (1, "×1"), (4, "×4"),
                   (16, "×16"), (64, "×64"), (256, "×256")]:
        y = py_(v)
        f.append(line(x0, y, x1, y, color="#d5d9df", sw=1.0))
        f.append(text(x0 - 14, y + 5, lab, size=12, color=MUTED, anchor="end"))

    f.append(line(x0, ybot, x1, ybot, color=INK, sw=1.4))
    xlabs = ["4К", "8К", "16К", "32К", "64К", "128К", "256К", "512К", "1М"]
    for i, lab in enumerate(xlabs):
        f.append(text(px_(12 + i), 424, lab, size=12, color=MUTED))

    base = _r_model(12.0)
    pts_amp = [(px_(12 + i), py_(2.0 ** i)) for i in range(9)]
    pts_sz = [(px_(12 + i), py_(_r_model(12.0 + i) / base)) for i in range(9)]
    for pts, col in ((pts_amp, POS), (pts_sz, FIELD)):
        for a, b in zip(pts, pts[1:]):
            f.append(line(a[0], a[1], b[0], b[1], color=col, sw=2.6))

    for x, lab in [(math.log(9950, 2), "EROFS ≈ 10 КіБ"),
                   (17.0, "SquashFS 128 КіБ")]:
        f.append(line(px_(x), 194, px_(x), ybot, color=MUTED, sw=1.2, dash="5,5"))
        f.append(text(px_(x), 452, lab, size=12, color=MUTED))

    f.append(rect(x0 + 18, 84, 322, 86, fill="#ffffff", stroke="#d5d9df", sw=1.2))
    f.append(line(x0 + 34, 110, x0 + 70, 110, color=POS, sw=2.6))
    f.append(mtext(x0 + 82, 105, ["надлишкове читання на одне",
                                  "випадкове читання 4 КіБ"],
                   size=12, color=MUTED, anchor="start"))
    f.append(line(x0 + 34, 145, x0 + 70, 145, color=FIELD, sw=2.6))
    f.append(mtext(x0 + 82, 140, ["розмір образу",
                                  "(частка від варіанта 4 КіБ)"],
                   size=12, color=MUTED, anchor="start"))

    f.append(text(470, 488, "розмір шматка B — вхід на одиницю стиснення",
                  size=13, color=MUTED))
    render(os.path.join(IMG, "size-vs-cost-curves.svg"), W, H, *f)


if __name__ == "__main__":
    fig_fixed_input_vs_output()
    fig_read_amplification()
    fig_image_stack()
    fig_two_amplifications()
    fig_read_window()
    fig_size_vs_cost()
    print("ok")
