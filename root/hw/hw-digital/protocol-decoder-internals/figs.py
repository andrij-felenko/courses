# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Конвеєр декодера: від голої напруги на дроті до перевіреного слова ─────
def fig_pipeline():
    W, H = 900, 300
    f = []
    cy = 132
    stages = [
        ("Поріг\n(Шмітт)", "#eafaf1", FIELD, "напруга → 0/1"),
        ("Синхро-\nнізатор", FILL, INK, "прибрати\nметастабільність"),
        ("Пере-\nдискрет.\n×16", "#eafaf1", FIELD, "16 знімків\nна біт"),
        ("Пошук\nфронту", FILL, INK, "старт кадру"),
        ("Голос\n2-з-3", "#eafaf1", FIELD, "центр біта,\nбез глітчів"),
        ("Зсувний\nрегістр", FILL, INK, "біти → слово"),
        ("Автомат\n+ CRC", "#eafaf1", FIELD, "кадр,\nперевірка"),
    ]
    n = len(stages)
    x0 = 30
    slot = (W - 2 * x0) / n
    centers = []
    ws = []
    for i, (s, fill, col, note) in enumerate(stages):
        cx = x0 + slot * (i + 0.5)
        b, w, h = textbox(cx, cy, s, size=12, pad=9, fill=fill, stroke=col, sw=2.0, color=INK)
        centers.append(cx)
        ws.append(w)
        f.append(b)
        # підпис під блоком — що робить етап
        f.append(mtext(cx, cy + h / 2 + 22, note, size=10.5, color=MUTED, lh=1.15))
    for i in range(n - 1):
        x1 = centers[i] + ws[i] / 2
        x2 = centers[i + 1] - ws[i + 1] / 2
        f.append(arrow(x1, cy, x2, cy, color=INK, sw=1.8))
    # вхід/вихід
    f.append(arrow(x0 - 18, cy, centers[0] - ws[0] / 2, cy, color=MUTED, sw=2))
    f.append(mtext(x0 - 16, cy - 18, "дріт\n(аналог)", size=10.5, color=MUTED, lh=1.1, anchor="start"))
    f.append(arrow(centers[-1] + ws[-1] / 2, cy, W - 12, cy, color=MUTED, sw=2))
    f.append(mtext(W - 14, cy - 18, "байт +\nпрапор\nпомилки", size=10.5, color=MUTED, lh=1.1, anchor="end"))
    # три «болячки» вгорі — що саме декодер лагодить
    f.append(text(W / 2, 34, "Декодер відновлює три речі, яких на голому дроті нема:",
                  size=13, color=INK, bold=True))
    f.append(text(W / 2, 54,
                  "ЧАС (де центр біта) · ЧИСТОТУ (без глітчів) · СТРУКТУРУ (де кадр і чи цілий)",
                  size=12, color=MUTED))
    # три групи внизу
    f.append(line(centers[2] - ws[2] / 2, cy + h / 2 + 44, centers[4] + ws[4] / 2, cy + h / 2 + 44,
                  color=FIELD, sw=1.4))
    f.append(text((centers[2] + centers[4]) / 2, cy + h / 2 + 60,
                  "відновлення часу й чистоти (ядро DSP)", size=11, color=FIELD, bold=True))
    render(os.path.join(IMG, "pipeline.svg"), W, H, *f)


# ── 2. Передискретизація ×16, центр біта і голос 2-з-3 виправляє глітч ────────
def fig_oversample_vote():
    W, H = 880, 380
    f = []
    x0, y0 = 60, 70
    N = 16                         # тіків на біт
    bitW = 640
    tick = bitW / N
    hiY = y0 + 10
    loY = y0 + 70
    # рівень лінії по тіках: у центрі один глітч (тік 8 «стрибнув» у 1)
    lvl = [0] * N                  # умовно біт даних = 0 (низький рівень)
    glitch_i = 8
    lvl[glitch_i] = 1              # завада — один тік підскочив
    # намалювати ступінчастий сигнал
    def yy(v): return hiY if v == 1 else loY
    px = x0
    for i in range(N):
        x1 = x0 + i * tick
        x2 = x1 + tick
        f.append(line(x1, yy(lvl[i]), x2, yy(lvl[i]), color=NEG, sw=2.4))
        if i > 0 and lvl[i] != lvl[i - 1]:
            f.append(line(x1, yy(lvl[i - 1]), x1, yy(lvl[i]), color=NEG, sw=2.4))
    # рамка біта
    f.append(line(x0, y0 - 14, x0, loY + 24, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(x0 + bitW, y0 - 14, x0 + bitW, loY + 24, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(x0 + bitW / 2, y0 - 20, "один період біта = 16 тіків локального годинника",
                  size=12, color=INK, bold=True))
    # тіки-знімки: точки під сигналом
    sy = loY + 40
    samples = [7, 8, 9]
    for i in range(N):
        cx = x0 + (i + 0.5) * tick
        is_center = i in samples
        f.append(line(cx, hiY - 6, cx, loY + 6, color="#dfe4ea", sw=1))
        col = POS if is_center else "#9aa4af"
        r = 4.5 if is_center else 2.6
        f.append(circle(cx, sy, r, fill=col, stroke=col))
        if i in (0, 7, 8, 9, 15):
            f.append(text(cx, sy + 18, str(i), size=10, color=MUTED))
    # рамка навколо трьох центральних
    csx = x0 + (samples[0]) * tick
    cw = 3 * tick
    f.append(rect(csx, sy - 16, cw, 32, fill="none", stroke=POS, sw=1.8, rx=6))
    f.append(text(csx + cw / 2, sy - 24, "3 знімки в центрі", size=11, color=POS, bold=True))
    # таблиця голосування праворуч
    bx, by = x0 + bitW + 24, y0 + 6
    votes = [("тік 7", 0), ("тік 8", 1), ("тік 9", 0)]
    f.append(text(bx, by, "Голос 2-з-3:", size=13, color=INK, bold=True, anchor="start"))
    yy2 = by + 26
    for lab, v in votes:
        col = POS if v == 1 else NEG
        f.append(text(bx, yy2, "%s → %d" % (lab, v), size=12, color=col, anchor="start"))
        if v == 1:
            f.append(text(bx + 96, yy2, "(глітч)", size=11, color=POS, anchor="start"))
        yy2 += 22
    f.append(line(bx, yy2 - 6, bx + 150, yy2 - 6, color=MUTED, sw=1))
    f.append(text(bx, yy2 + 14, "більшість = 0", size=13, color=FIELD, anchor="start", bold=True))
    f.append(text(bx, yy2 + 32, "глітч переголосовано", size=11, color=MUTED, anchor="start"))
    # висновок унизу
    f.append(text(W / 2, H - 22,
                  "Один збійний тік у центрі не псує біт: два справні знімки перемагають один хибний",
                  size=11, color=INK))
    render(os.path.join(IMG, "oversample-vote.svg"), W, H, *f)


# ── 3. Вирівнювання на старт-біт: фронт → півбіта до центру → крок по біту ────
def fig_start_align():
    W, H = 880, 360
    f = []
    x0, y0 = 60, 90
    tick = 20
    N = 16
    bitW = N * tick
    hiY = y0
    loY = y0 + 60
    # послідовність: спокій(1) → старт-біт(0) → біт даних b0(1) → ...
    # намалюємо: хвіст спокою + старт + перший біт
    def draw_level(xa, xb, v):
        yv = hiY if v == 1 else loY
        f.append(line(xa, yv, xb, yv, color=NEG, sw=2.4))
        return yv
    x = x0
    # спокій (лінія у 1) — короткий хвіст
    idle_w = 60
    draw_level(x, x + idle_w, 1)
    edge_x = x + idle_w
    # спад: фронт старт-біта
    f.append(line(edge_x, hiY, edge_x, loY, color=NEG, sw=2.4))
    # старт-біт (0) на 16 тіків
    draw_level(edge_x, edge_x + bitW, 0)
    # перший біт даних = 1
    draw_level(edge_x + bitW, edge_x + bitW, 0)
    f.append(line(edge_x + bitW, loY, edge_x + bitW, hiY, color=NEG, sw=2.4))
    draw_level(edge_x + bitW, edge_x + 2 * bitW, 1)
    # мітки бітів
    f.append(text(edge_x - 30, hiY - 14, "спокій = 1", size=11, color=MUTED, anchor="middle"))
    f.append(text(edge_x + bitW / 2, loY + 22, "старт-біт = 0", size=12, color=INK, bold=True))
    f.append(text(edge_x + bitW + bitW / 2 - 70, hiY - 14, "біт даних", size=12, color=INK, bold=True, anchor="middle"))
    # 1) фронт помічено
    f.append(arrow(edge_x, hiY - 42, edge_x, hiY - 8, color=POS, sw=2))
    f.append(text(edge_x, hiY - 50, "1) спадний фронт — можливий старт", size=11, color=POS, bold=True))
    # 2) відлічити півбіта (8 тіків) до центру старт-біта
    center1 = edge_x + 8 * tick
    f.append(line(center1, loY - 6, center1, loY + 40, color=FIELD, sw=1.6, dash="4,3"))
    f.append(circle(center1, loY, 5, fill=FIELD, stroke=FIELD))
    f.append(text(center1, loY + 56, "2) +8 тіків → центр:", size=11, color=FIELD, bold=True))
    f.append(text(center1, loY + 70, "тут ще 0? так → старт справжній", size=10.5, color=MUTED))
    # дужка «8 тіків = півбіта»
    f.append(line(edge_x, loY + 34, center1, loY + 34, color=FIELD, sw=1.2))
    f.append(text((edge_x + center1) / 2, loY + 32, "8 тіків = півбіта", size=10, color=FIELD, anchor="middle"))
    # 3) далі крок рівно по 16 тіків — центр кожного наступного біта
    center2 = center1 + bitW
    f.append(line(center2, hiY - 6, center2, loY + 6, color=POS, sw=1.6, dash="4,3"))
    f.append(circle(center2, hiY, 5, fill=POS, stroke=POS))
    f.append(text(center2, hiY - 30, "3) +16 → центр даних", size=11, color=POS, bold=True))
    f.append(line(center1, hiY + 84, center2, hiY + 84, color=POS, sw=1.2))
    f.append(text((center1 + center2) / 2, hiY + 98, "далі крок = 16 тіків (цілий біт)", size=10.5, color=POS, anchor="middle"))
    render(os.path.join(IMG, "start-align.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pipeline()
    fig_oversample_vote()
    fig_start_align()
    print("figs done")
