# -*- coding: utf-8 -*-
# Фігура для вставки hist-fiducial-lineage.md — родовід фідуційних міток.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_lineage():
    """Часова стрічка: ARToolKit → ARTag → (ArUco, AprilTag). Що кожен додав."""
    W, H = 900, 500
    p = []
    p.append(text(W / 2, 30, "родовід фідуційних міток: що кожна система додала", size=15.5, bold=True))

    # горизонтальна вісь часу; засічки років вирівняно з центрами карток
    axis_y = 90
    cw, ch = 205, 175
    card_x = [30, 245, 480, 665]                 # ліві краї карток
    centers = [cx + cw / 2 for cx in card_x]     # 132.5, 347.5, 582.5, 767.5
    x0, x1 = 60, W - 40
    p.append(line(x0, axis_y, x1, axis_y, color=MUTED, sw=2))
    for yr, lx in zip(["1999", "2005", "2011", "2014"], centers):
        p.append(line(lx, axis_y - 6, lx, axis_y + 6, color=MUTED, sw=2))
        p.append(text(lx, axis_y - 14, yr, size=12, bold=True, color=MUTED))

    # чотири картки-віхи
    cards = [
        (30,  135, "#f4f6f8", INK,
         "ARToolKit",
         "Като й Біллінґгерст, 1999\n(HIT Lab, Вашингтон)\n\n"
         "перша масова система:\nквадратна рамка +\nзіставлення картинки\nз бібліотекою (кореляція)",
         "БЕНТЕЖИЛО: мітки\nплутались між собою й\nз фоном; поріг гуляв\nвід світла"),
        (245, 135, "#fdf6e3", "#b8860b",
         "ARTag",
         "Марк Фіала, 2004–05\n(NRC Канади)\n\n"
         "перше ЦИФРОВЕ кодування:\nID як число з контрольними\nбітами; рамку шукають\nпо краях, не порогом",
         "ДОДАВ: строге\nвиправлення помилок;\nчисельно малий\nхибний спрацьовок"),
        (480, 135, "#eafaf0", FIELD,
         "AprilTag",
         "Едвін Олсон, 2011\n(лаб. APRIL, Мічиган)\nv2 — Ван і Олсон, 2016\n\n"
         "наголос на РОБОТОТЕХНІЦІ:\nловить далеко, крізь\nрозмиття, перекриття,\nспотворення об'єктива",
         "ДОДАВ: дальність\nі стійкість у полі;\nвідкритий код і\nнабори тегів"),
        (665, 135, "#eef2ff", NEG,
         "ArUco",
         "Гаррідо-Хурадо та ін.,\n2014 (Ун-т Кордови)\n\n"
         "словники ГЕНЕРУЮТЬ під\nзамовлення: стільки міток\nі така завадостійкість,\nяк треба",
         "ДОДАВ: керовані\nсловники; увійшов\nу OpenCV — став\nстандартом де-факто"),
    ]
    for cx, cy, fillc, ac, name, body, gain in cards:
        # вертикальна ніжка від осі до картки
        p.append(line(cx + cw / 2, axis_y + 6, cx + cw / 2, cy, color=MUTED, sw=1.4, dash="3,3"))
        p.append(rect(cx, cy, cw, ch, fill=fillc, stroke=ac, sw=1.8))
        p.append(text(cx + cw / 2, cy + 24, name, size=15, bold=True, color=ac))
        p.append(mtext(cx + cw / 2, cy + 46, body, size=10.5, color=INK, lh=1.25))
        # смужка «що додав/бентежило» знизу картки
        gy = cy + ch + 12
        b, bw, bh = textbox(cx + cw / 2, gy + 26, gain, size=10, pad=8,
                            fill="#ffffff", stroke=ac, sw=1.3)
        p.append(b)
        p.append(arrow(cx + cw / 2, cy + ch + 2, cx + cw / 2, gy + 6, color=ac, sw=1.5))

    # стрілки спадкоємності: ARToolKit→ARTag і ARTag→AprilTag ідуть по самій осі.
    # ARTag живить і ArUco теж — цю ведемо трохи НИЖЧЕ осі (там чисто до карток),
    # щоб не злитися зі стрілкою на AprilTag.
    seg = 44  # відступ від засічок, щоб стрілка не налазила на текст року
    p.append(arrow(centers[0] + seg, axis_y, centers[1] - seg, axis_y, color=INK, sw=1.6))
    p.append(arrow(centers[1] + seg, axis_y, centers[2] - seg, axis_y, color=INK, sw=1.6))
    p.append(arrow(centers[1] + seg, axis_y + 16, centers[3] - seg, axis_y + 16, color=INK, sw=1.6))

    p.append(text(W / 2, H - 16,
                  "спільна нитка: квадрат із рамкою → все точніше й надійніше кодування ID та пошук рамки",
                  size=11.5, italic=True, color=MUTED))

    render(os.path.join(OUT, "fiducial-lineage.svg"), W, H, *p)


if __name__ == "__main__":
    fig_lineage()
    print("hist figs done")
