# -*- coding: utf-8 -*-
"""Фігури до теми «Стик із відеоконвеєром: формати пікселів і передача кадру»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

GREEN_FILL = "#e3f6ea"
GREY_FILL  = "#eef1f4"
RED_FILL   = "#fdecea"
BLUE_FILL  = "#eaf0fd"
PAD_FILL   = "#f6ddd8"


# ─────────────────────────────────────────────────────────────────────────────
# 1. Хибний крок рядка зсуває картинку по діагоналі
# ─────────────────────────────────────────────────────────────────────────────
def fig_shear():
    W, H = 1080, 560
    f = []

    fw, fh = 330, 250
    ax, ay = 90, 108          # ліва панель — правильний крок
    bx, by = 610, 108         # права панель — крок за замовчуванням

    f.append(text(ax + fw / 2, 92, "крок узято з конвеєра: 4100",
                  size=15, bold=True, color=FIELD))
    f.append(text(bx + fw / 2, 92, "крок порахував Mat сам: 4098",
                  size=15, bold=True, color=POS))

    f.append(rect(ax, ay, fw, fh, fill="#ffffff", stroke=LINE, sw=1.6))
    f.append(rect(bx, by, fw, fh, fill="#ffffff", stroke=LINE, sw=1.6))

    n = 25
    band_h = fh / n
    band_w = 44
    for i in range(n):
        f.append(rect(ax + 70, ay + i * band_h, band_w, band_h,
                      fill=NEG, stroke=NEG, sw=0.4, rx=0))
        f.append(rect(bx + 70 + i * 4.8, by + i * band_h, band_w, band_h,
                      fill=NEG, stroke=NEG, sw=0.4, rx=0))

    f.append(text(ax + fw / 2, ay + fh + 30,
                  "вертикальний край лишається вертикальним",
                  size=13, color=MUTED))
    f.append(text(bx + fw / 2, by + fh + 30,
                  "кожен рядок з'їжджає ще на два байти",
                  size=13, color=MUTED))

    box = fitbox(150, 448, 780, 84,
                 "Кадр 1366 пікселів завширшки, BGR: рядок займає 4098 байтів, а конвеєр\n"
                 "розкладає його по 4100. На останньому рядку накопичений зсув — 1534 байти,\n"
                 "тобто 511 пікселів: понад третину ширини кадру.",
                 size=13, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK)
    f.append(box)

    render(os.path.join(OUT, 'stride-shear.svg'), W, H, *f,
           title="Два байти на рядок, яких ніхто не помітив")


# ─────────────────────────────────────────────────────────────────────────────
# 2. NV12 у пам'яті й два способи описати її заголовками Mat
# ─────────────────────────────────────────────────────────────────────────────
def fig_nv12():
    W, H = 1160, 620
    f = []

    # ── ліворуч: що насправді лежить у пам'яті ──
    cx, cw = 80, 240
    f.append(text(cx + cw / 2, 84, "як лежить у пам'яті", size=15, bold=True, color=INK))

    y_top, y_h = 108, 208
    f.append(rect(cx, y_top, cw - 34, y_h, fill=BLUE_FILL, stroke=NEG, sw=1.6))
    f.append(rect(cx + cw - 34, y_top, 34, y_h, fill=PAD_FILL, stroke=POS, sw=1.2))
    f.append(text(cx + (cw - 34) / 2, y_top + y_h / 2 + 5, "площина Y", size=14, color=NEG, bold=True))

    gap_top = y_top + y_h
    f.append(rect(cx, gap_top, cw, 30, fill=GREY_FILL, stroke=MUTED, sw=1.2))
    f.append(text(cx + cw / 2, gap_top + 20, "порожнеча вирівнювання", size=11, color=MUTED))

    uv_top, uv_h = gap_top + 30, 106
    f.append(rect(cx, uv_top, cw - 34, uv_h, fill=GREEN_FILL, stroke=FIELD, sw=1.6))
    f.append(rect(cx + cw - 34, uv_top, 34, uv_h, fill=PAD_FILL, stroke=POS, sw=1.2))
    f.append(text(cx + (cw - 34) / 2, uv_top + uv_h / 2 + 5, "площина UV", size=14, color=FIELD, bold=True))

    f.append(fitbox(cx - 10, uv_top + uv_h + 26, cw + 20, 88,
                    "рожеве праворуч — доповнення\nрядка до кроку;\nсіре — зсув початку\nдругої площини",
                    size=12, fill="#ffffff", stroke=MUTED, sw=1.2, color=MUTED))

    # ── праворуч: два описи ──
    px, pw = 400, 690
    f.append(text(px + pw / 2, 84, "як це описати заголовками Mat", size=15, bold=True, color=INK))

    f.append(fitbox(px, 104, pw, 150,
                    "ДВА ЗАГОЛОВКИ: Mat над Y і Mat над UV\n"
                    "cvtColorTwoPlane(y, uv, bgr, COLOR_YUV2BGR_NV12)\n"
                    "Кожен заголовок несе власний покажчик і власний крок,\n"
                    "тож ані доповнення рядка, ані зсув другої площини\n"
                    "нічого не ламають.",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=2, color=INK))

    f.append(fitbox(px, 288, pw, 176,
                    "ОДИН ВИСОКИЙ ЗАГОЛОВОК: Mat(H·3/2, W, CV_8UC1, база, крок)\n"
                    "cvtColor(yuv, bgr, COLOR_YUV2BGR_NV12)\n"
                    "Опис вважає, що UV — це просто продовження рядків Y.\n"
                    "Правда ЛИШЕ коли крок UV дорівнює кроку Y\n"
                    "І друга площина починається рівно там, де скінчилася перша.\n"
                    "Інакше замість кольору читається порожнеча вирівнювання.",
                    size=14, fill=RED_FILL, stroke=POS, sw=2, color=INK))

    f.append(fitbox(px, 496, pw, 96,
                    "Апаратні буфери вирівнюють початок кожної площини окремо —\n"
                    "саме там високий заголовок і бреше найчастіше,\n"
                    "фарбуючи нижню частину кадру рівною кольоровою смугою.",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))

    render(os.path.join(OUT, 'nv12-two-views.svg'), W, H, *f,
           title="NV12: одна пам'ять, два способи назвати її матрицею")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Скільки копій кадру між декодером і алгоритмом
# ─────────────────────────────────────────────────────────────────────────────
def fig_copies():
    W, H = 1180, 600
    f = []

    lx, lw = 70, 400          # ліва колонка — етапи
    rx, rw = 550, 560         # права колонка — ціна
    ys = [76, 176, 276, 376, 476]
    bh = 74

    stages = [
        ("Апаратний декодер пише кадр\nу власний буфер (NV12)",
         "2.97 МіБ запису на кадр — неминуче", GREY_FILL, LINE, MUTED),
        ("Буфер стає видимим процесору:\nмапування або звантаження",
         "0 або 2.97 МіБ — залежить від того,\nчи пам'ять декодера спільна з процесором",
         GREY_FILL, LINE, MUTED),
        ("Площини перепаковують\nв один суцільний блок",
         "2.97 МіБ читання + 2.97 запису\nУСУВНО: два заголовки замість одного",
         GREEN_FILL, FIELD, FIELD),
        ("Перетворення NV12 → BGR",
         "2.97 МіБ читання + 5.93 запису\nУСУВНО, якщо алгоритмові досить площини Y",
         GREEN_FILL, FIELD, FIELD),
        ("Алгоритм зору",
         "читає рівно стільки, скільки йому треба", "#ffffff", INK, INK),
    ]

    for i, (left, right, fill, stroke, rcolor) in enumerate(stages):
        y = ys[i]
        f.append(fitbox(lx, y, lw, bh, left, size=14, fill=fill, stroke=stroke, sw=1.8))
        f.append(fitbox(rx, y, rw, bh, right, size=13, fill="#ffffff",
                        stroke=rcolor, sw=1.4, color=rcolor))
        f.append(line(lx + lw + 14, y + bh / 2, rx - 14, y + bh / 2,
                      color=MUTED, sw=1.0, dash="3,4"))
        if i < len(stages) - 1:
            f.append(arrow(lx + lw / 2, y + bh, lx + lw / 2, ys[i + 1], color=LINE, sw=1.6))

    f.append(fitbox(70, 562, 1040, 30,
                    "Зелене — копії, які прибирають без утрати змісту; сіре — плата за апаратне декодування.",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))

    render(os.path.join(OUT, 'copy-path.svg'), W, H, *f,
           title="Кадр 1920×1080 NV12: де саме витрачається пам'ять")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Що у Windows справді лежить у пам'яті задом наперед (вставка hist-bgr-order)
# ─────────────────────────────────────────────────────────────────────────────
def fig_windows_bytes():
    W, H = 1180, 520
    f = []

    R_CELL = ("#fdecea", POS)
    G_CELL = ("#e3f6ea", FIELD)
    B_CELL = ("#eaf0fd", NEG)
    N_CELL = (GREY_FILL, MUTED)

    lx, lw = 40, 296          # ліва колонка з назвою
    cx0, cw, gap = 360, 126, 6
    vx, vw = 950, 190         # права колонка з висновком
    bh = 60

    # спільна вісь адрес — підписи лише над верхнім рядом
    f.append(text(cx0 + (4 * (cw + gap) - gap) / 2, 66,
                  "адреса в пам'яті росте вправо →", size=13, color=MUTED))

    rows = [
        # (y, назва зліва, клітинки, висновок, колір висновку, ширина клітинки, к-сть)
        (96, "COLORREF\nзаписують як 0x00bbggrr",
         [("rr\nчервоний", R_CELL), ("gg\nзелений", G_CELL),
          ("bb\nсиній", B_CELL), ("00\nнуль", N_CELL)],
         "у пам'яті це RGB\nмолодший байт — червоний", POS, cw, 4),

        (238, "RGBQUAD\nструктура з wingdi.h",
         [("rgbBlue\nсиній", B_CELL), ("rgbGreen\nзелений", G_CELL),
          ("rgbRed\nчервоний", R_CELL), ("rgbReserved\nнуль", N_CELL)],
         "у пам'яті це BGR\nпорядок оголошення полів", FIELD, cw, 4),
    ]

    for (y, name, cells, verdict, vcol, w, n) in rows:
        f.append(fitbox(lx, y, lw, bh, name, size=14, fill="#ffffff",
                        stroke=LINE, sw=1.6))
        for i, (label, (fill, stroke)) in enumerate(cells):
            x = cx0 + i * (w + gap)
            f.append(fitbox(x, y, w, bh, label, size=13, fill=fill,
                            stroke=stroke, sw=1.6, color=INK))
            if y == 96:
                f.append(text(x + w / 2, 78, "+%d" % i, size=12, color=MUTED))
        f.append(arrow(cx0 + n * (w + gap) - gap + 12, y + bh / 2, vx - 12, y + bh / 2,
                       color=MUTED, sw=1.4))
        f.append(fitbox(vx, y, vw, bh, verdict, size=12, fill="#ffffff",
                        stroke=vcol, sw=1.8, color=vcol, bold=True))

    # третій ряд — піксельний масив DIB, шість байтів
    y3, cw3 = 380, 82
    f.append(fitbox(lx, y3, lw, bh, "піксельний масив\n24-бітного DIB і BMP",
                    size=14, fill="#ffffff", stroke=LINE, sw=1.6))
    seq = [("B", B_CELL), ("G", G_CELL), ("R", R_CELL),
           ("B", B_CELL), ("G", G_CELL), ("R", R_CELL)]
    for i, (label, (fill, stroke)) in enumerate(seq):
        x = cx0 + i * (cw3 + gap)
        f.append(fitbox(x, y3, cw3, bh, label, size=17, fill=fill,
                        stroke=stroke, sw=1.6, color=INK))
    f.append(text(cx0 + (3 * (cw3 + gap) - gap) / 2, y3 + bh + 22,
                  "піксель 0", size=12, color=MUTED))
    f.append(text(cx0 + 3 * (cw3 + gap) + (3 * (cw3 + gap) - gap) / 2, y3 + bh + 22,
                  "піксель 1", size=12, color=MUTED))
    f.append(arrow(cx0 + 6 * (cw3 + gap) - gap + 12, y3 + bh / 2, vx - 12, y3 + bh / 2,
                   color=MUTED, sw=1.4))
    f.append(fitbox(vx, y3, vw, bh, "у пам'яті це BGR\nсаме звідси спадок",
                    size=12, fill="#ffffff", stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    render(os.path.join(OUT, 'windows-byte-order.svg'), W, H, *f,
           title="Найчастіше цитований доказ — найслабший")


# ─────────────────────────────────────────────────────────────────────────────
# Вікно map…unmap і три способи з нього вийти (вставка proj-zero-copy-bridge)
# ─────────────────────────────────────────────────────────────────────────────
def fig_bridge_window():
    W, H = 1080, 560
    f = []

    X0, MAPX, UNMAPX, ENDX = 90.0, 380.0, 700.0, 1010.0
    AMBER = "#fdf3dc"

    # ── події над смугами ────────────────────────────────────────────────────
    f.append(text(200, 66, "pull_sample", size=13, bold=True, color=MUTED))
    f.append(text(MAPX, 66, "gst_video_frame_map", size=13, bold=True, color=FIELD))
    f.append(text(UNMAPX, 66, "gst_video_frame_unmap", size=13, bold=True, color=POS))
    f.append(text(900, 66, "gst_sample_unref", size=13, bold=True, color=MUTED))

    # ── смуга часу: до вікна, вікно, після вікна ─────────────────────────────
    by, bh = 88, 62
    f.append(fitbox(X0, by, MAPX - 6 - X0, bh,
                    "семпл уже наш,\nпокажчиків ще нема",
                    size=13, fill=GREY_FILL, stroke=MUTED, sw=1.4, color=INK))
    f.append(fitbox(MAPX, by, UNMAPX - MAPX, bh,
                    "покажчики на площини дійсні —\nтут і тільки тут живуть заголовки Mat",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.8, color=INK))
    f.append(fitbox(UNMAPX + 6, by, ENDX - UNMAPX - 6, bh,
                    "пул віддає той самий буфер\nнаступному кадрові",
                    size=13, fill=RED_FILL, stroke=POS, sw=1.8, color=INK))

    # ── три виходи з вікна ───────────────────────────────────────────────────
    lane_h = 58
    ys = [176, 262, 348]
    lw = MAPX - 16 - X0

    f.append(fitbox(X0, ys[0], lw, lane_h, "1 · синхронно\n0 копій",
                    size=14, fill="#ffffff", stroke=FIELD, sw=1.8, color=FIELD, bold=True))
    f.append(fitbox(MAPX, ys[0], UNMAPX - MAPX, lane_h,
                    "уся обробка тут;\nMat помирає до unmap",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.6, color=INK))

    f.append(fitbox(X0, ys[1], lw, lane_h, "2 · clone()\n+1 копія кадру",
                    size=14, fill="#ffffff", stroke=NEG, sw=1.8, color=NEG, bold=True))
    f.append(fitbox(MAPX, ys[1], UNMAPX - MAPX, lane_h,
                    "у вікні лише clone()",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.6, color=INK))
    f.append(arrow(UNMAPX + 2, ys[1] + lane_h / 2, UNMAPX + 26, ys[1] + lane_h / 2,
                   color=NEG, sw=1.8))
    f.append(fitbox(UNMAPX + 32, ys[1], ENDX - UNMAPX - 32, lane_h,
                    "копія живе стільки,\nскільки треба",
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.6, color=INK))

    f.append(fitbox(X0, ys[2], lw, lane_h, "3 · тримати GstSample\n0 копій, −1 буфер із пулу",
                    size=13, fill="#ffffff", stroke="#b8860b", sw=1.8, color="#8a6100", bold=True))
    f.append(fitbox(MAPX, ys[2], ENDX - MAPX, lane_h,
                    "вікно не закривається, доки тримаєш семпл:\nбуфер не повертається в пул",
                    size=13, fill=AMBER, stroke="#b8860b", sw=1.6, color=INK))

    f.append(fitbox(X0, 438, ENDX - X0, 48,
                    "Заголовок над чужим буфером мусить померти раніше за unmap: інакше або чесна копія, "
                    "або притриманий буфер із пулу.",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))

    render(os.path.join(OUT, 'bridge-window.svg'), W, H, *f,
           title="Вікно, у якому заголовок Mat має право існувати")


fig_shear()
fig_nv12()
fig_copies()
fig_windows_bytes()
fig_bridge_window()
print("ok")
