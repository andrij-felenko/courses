# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_gop_structure():
    """GOP: як залежності кадрів визначають лаг, стійкість і можливість гортати."""
    W, H = 940, 470
    parts = [text(W / 2, 28, "Структура GOP: хто від кого залежить", size=17, bold=True)]

    # --- MJPEG рядок: усі I, незалежні ---
    y_mj = 90
    parts.append(text(70, y_mj - 22, "MJPEG (усі I)", size=13, bold=True, anchor="start", color=NEG))
    xs = [90 + i * 95 for i in range(8)]
    for x in xs:
        parts.append(fitbox(x, y_mj, 60, 46, "I", size=18, fill="#eaf0fd", stroke=NEG, sw=2))
    parts.append(text(90, y_mj + 74, "кожен кадр самостійний · збій гине в одному кадрі · гортати можна будь-куди",
                      size=11, color=MUTED, anchor="start"))

    # --- H.264 рядок: I P B B P B B P ... з дугами залежності ---
    y_h = 235
    parts.append(text(70, y_h - 22, "H.264 (GOP = I P B B P B B P)", size=13, bold=True, anchor="start", color=POS))
    types = ["I", "P", "B", "B", "P", "B", "B", "P"]
    colmap = {"I": ("#eaf0fd", NEG), "P": ("#fff1e6", "#c96a1b"), "B": ("#fdecea", POS)}
    cx = []
    for i, t in enumerate(types):
        x = 90 + i * 95
        cx.append(x + 30)
        fill, st = colmap[t]
        parts.append(fitbox(x, y_h, 60, 46, t, size=18, fill=fill, stroke=st, sw=2))

    def dep_arc(i_from, i_to, up=True, color=MUTED):
        x1, x2 = cx[i_from], cx[i_to]
        yb = y_h - 6 if up else y_h + 52
        mid = (x1 + x2) / 2
        ctrl = yb - 34 if up else yb + 34
        return ('<path d="M%.0f %.0f Q%.0f %.0f %.0f %.0f" fill="none" stroke="%s" '
                'stroke-width="1.6" marker-end="url(#arrow)"/>' % (x1, yb, mid, ctrl, x2, yb, color))

    # P залежить від попереднього опорного (назад)
    parts.append(dep_arc(1, 0, up=True, color="#c96a1b"))
    parts.append(dep_arc(4, 1, up=True, color="#c96a1b"))
    parts.append(dep_arc(7, 4, up=True, color="#c96a1b"))
    # B залежить від двох опорних (з двох боків) — знизу
    parts.append(dep_arc(2, 1, up=False, color=POS))
    parts.append(dep_arc(2, 4, up=False, color=POS))
    parts.append(dep_arc(5, 4, up=False, color=POS))
    parts.append(dep_arc(5, 7, up=False, color=POS))

    parts.append(text(90, y_h + 108, "P дивиться назад · B дивиться в обидва боки → декодер тримає майбутнє в буфері",
                      size=11, color=MUTED, anchor="start"))
    parts.append(text(90, y_h + 128, "втрата I чи P псує весь ланцюг до наступного I · гортати можна лише по I",
                      size=11, color=MUTED, anchor="start"))

    # легенда
    ly = 420
    parts.append(fitbox(90, ly, 40, 30, "I", size=13, fill="#eaf0fd", stroke=NEG, sw=2))
    parts.append(text(140, ly + 20, "повний кадр (ключовий)", size=11, anchor="start"))
    parts.append(fitbox(360, ly, 40, 30, "P", size=13, fill="#fff1e6", stroke="#c96a1b", sw=2))
    parts.append(text(410, ly + 20, "різниця від минулого", size=11, anchor="start"))
    parts.append(fitbox(620, ly, 40, 30, "B", size=13, fill="#fdecea", stroke=POS, sw=2))
    parts.append(text(670, ly + 20, "різниця від минулого й майбутнього", size=11, anchor="start"))

    render(os.path.join(OUT, "gop-structure.svg"), W, H, *parts)


def fig_motion_comp():
    """Компенсація руху: блок шукається у попередньому кадрі, кодуємо вектор + залишок."""
    W, H = 900, 430
    parts = [text(W / 2, 28, "Компенсація руху: вектор + залишок замість цілого блока", size=17, bold=True)]

    # два кадри
    fx1, fy, fw, fh = 70, 70, 300, 260
    fx2 = 500
    parts.append(rect(fx1, fy, fw, fh, fill="#f7f9fc", stroke=MUTED, sw=1.4, rx=8))
    parts.append(rect(fx2, fy, fw, fh, fill="#f7f9fc", stroke=MUTED, sw=1.4, rx=8))
    parts.append(text(fx1 + fw / 2, fy - 12, "опорний кадр (минулий)", size=12, bold=True, color=NEG))
    parts.append(text(fx2 + fw / 2, fy - 12, "поточний кадр", size=12, bold=True, color=POS))

    # сітка блоків
    def grid(ox):
        g = []
        for i in range(1, 5):
            g.append(line(ox + i * fw / 5, fy, ox + i * fw / 5, fy + fh, color="#dfe4ea", sw=1))
        for j in range(1, 5):
            g.append(line(ox, fy + j * fh / 5, ox + fw, fy + j * fh / 5, color="#dfe4ea", sw=1))
        return g
    parts += grid(fx1)
    parts += grid(fx2)

    bw, bh = fw / 5, fh / 5
    # блок у поточному кадрі (рядок 1, стовпець 3)
    cur_x = fx2 + 3 * bw
    cur_y = fy + 1 * bh
    parts.append(rect(cur_x, cur_y, bw, bh, fill="#fdecea", stroke=POS, sw=2.4, rx=3))
    parts.append(text(cur_x + bw / 2, cur_y + bh / 2 + 4, "блок", size=11, bold=True, color=POS))

    # найкращий збіг у опорному (рядок 2, стовпець 1) — зсув
    ref_x = fx1 + 1 * bw
    ref_y = fy + 2 * bh
    parts.append(rect(ref_x, ref_y, bw, bh, fill="#eaf0fd", stroke=NEG, sw=2.4, rx=3))
    parts.append(text(ref_x + bw / 2, ref_y + bh / 2 + 4, "збіг", size=11, bold=True, color=NEG))

    # вектор руху всередині опорного кадру: від позиції-як-у-поточному до збігу
    same_x = fx1 + 3 * bw + bw / 2
    same_y = fy + 1 * bh + bh / 2
    parts.append(circle(same_x, same_y, 3, fill=MUTED, stroke=MUTED))
    parts.append(arrow(same_x, same_y, ref_x + bw / 2, ref_y + bh / 2, color=FIELD, sw=2.2))
    parts.append(text((same_x + ref_x) / 2 - 6, (same_y + ref_y) / 2 - 8,
                      "MV=(−2,+1)", size=11, bold=True, color=FIELD, anchor="end"))

    # стрілка між кадрами
    parts.append(arrow(fx1 + fw + 10, fy + fh / 2, fx2 - 10, fy + fh / 2, color=MUTED, sw=1.6))

    # формула-висновок унизу
    parts.append(fitbox(150, 360, 620, 44,
                        "кодуємо: вектор (−2,+1)  +  залишок (поточний − зсунутий збіг)  →  часто майже нулі",
                        size=12, fill="#eafaf0", stroke=FIELD, sw=1.6))
    render(os.path.join(OUT, "motion-comp.svg"), W, H, *parts)


def fig_bitrate_math():
    """Звідки береться бітрейт: піксельний потік → поділити на коефіцієнт стиску."""
    W, H = 920, 400
    parts = [text(W / 2, 28, "Скільки важить потік: піксельний потік ÷ стиск", size=17, bold=True)]

    # ліворуч: сирий потік
    parts.append(fitbox(60, 70, 250, 150,
                        "СИРИЙ ПОТІК\n1280 × 720\n× 30 к/с\n× 12 біт/піксель (YUV420)\n= 331 Мбіт/с",
                        size=13, fill="#fdecea", stroke=POS, sw=1.8))

    parts.append(arrow(320, 145, 380, 145, color=MUTED, sw=2))

    # посередині два дільники
    parts.append(fitbox(390, 60, 220, 70, "MJPEG\n÷ 10\n= 33 Мбіт/с", size=13, fill="#eaf0fd", stroke=NEG, sw=1.8))
    parts.append(fitbox(390, 160, 220, 70, "H.264\n÷ 100\n= 3.3 Мбіт/с", size=13, fill="#eafaf0", stroke=FIELD, sw=1.8))

    parts.append(arrow(610, 95, 670, 95, color=MUTED, sw=2))
    parts.append(arrow(610, 195, 670, 195, color=MUTED, sw=2))

    # праворуч: наслідок для каналу
    parts.append(fitbox(680, 60, 200, 70, "Wi-Fi тягне\nледве-ледве", size=12, fill="#fff4e8", stroke="#c96a1b", sw=1.6))
    parts.append(fitbox(680, 160, 200, 70, "лізе навіть\nу вузький радіоканал", size=12, fill="#eafaf0", stroke=FIELD, sw=1.6))

    # формула внизу
    parts.append(fitbox(120, 300, 680, 60,
                        "бітрейт ≈ (ширина × висота × к/с × біт-на-піксель) ÷ коефіцієнт_стиску\n"
                        "менший коефіцієнт → більший файл, але простіше й стійкіше",
                        size=12, fill=FILL, stroke=LINE, sw=1.4))
    render(os.path.join(OUT, "bitrate-math.svg"), W, H, *parts)


def fig_latency_pipeline():
    """Конвеєр затримки: де накопичуються мілісекунди в MJPEG проти H.264."""
    W, H = 940, 430
    parts = [text(W / 2, 28, "Бюджет затримки: де накопичуються мілісекунди", size=17, bold=True)]

    stages = ["захоплення\nсенсора", "кодування", "буфер\n(реордер B)", "мережа /\nпакування", "декодування", "показ"]
    n = len(stages)
    x0 = 60
    slot = (W - 2 * x0) / n
    y = 90
    boxh = 60
    for i, s in enumerate(stages):
        x = x0 + i * slot
        parts.append(fitbox(x + 6, y, slot - 12, boxh, s, size=11, fill=FILL, stroke=MUTED, sw=1.3))
        if i < n - 1:
            parts.append(arrow(x + slot - 6, y + boxh / 2, x + slot + 6, y + boxh / 2, color=MUTED, sw=1.6))

    # смуга MJPEG
    def bar(cy, label, vals, color):
        parts.append(text(x0, cy - 16, label, size=12, bold=True, anchor="start", color=color))
        total = 0
        for i, v in enumerate(vals):
            x = x0 + i * slot
            wv = slot - 12
            parts.append(rect(x + 6, cy, wv, 26, fill=color, stroke="none", sw=0, rx=4))
            parts.append(text(x + 6 + wv / 2, cy + 18, "%g" % v, size=11, color=BG, bold=True))
            total += v
        parts.append(text(W - x0, cy - 16, "≈ %g мс" % total, size=12, bold=True, anchor="end", color=color))

    # значення в мс під кожну стадію
    parts.append(rect(x0, 175, W - 2 * x0, 1, fill=MUTED, stroke=MUTED))
    bar(220, "MJPEG", [5, 3, 0, 4, 2, 8], "#5b8def")
    bar(300, "H.264 (з B-кадрами)", [5, 18, 33, 4, 6, 8], "#e07a3f")

    parts.append(fitbox(120, 360, 700, 46,
                        "головна різниця — кодування й буфер реордерингу B-кадрів: саме там H.264 набирає лаг",
                        size=12, fill="#fff4e8", stroke="#c96a1b", sw=1.4))
    render(os.path.join(OUT, "latency-pipeline.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_gop_structure()
    fig_motion_comp()
    fig_bitrate_math()
    fig_latency_pipeline()
    print("done")
