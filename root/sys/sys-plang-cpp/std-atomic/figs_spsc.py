# -*- coding: utf-8 -*-
# Фігури для вставки proj-spsc-ring-buffer.md (тема std-atomic).
# Окремий скрипт, щоб не чіпати відпрацьований figs.py статті-власника.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: два покажчики, дисципліна власності, публікація/підхоплення ────
def fig_spsc_flow():
    W, H = 820, 470
    p = []
    p.append(text(W / 2, 30, "SPSC-кільце: head пише продюсер, tail читає консюмер", size=16, bold=True))

    # кільце-масив посередині
    cx, cy, r = W / 2, 235, 92
    p.append(circle(cx, cy, r, fill="none", stroke=MUTED, sw=2))
    # 8 клітин по колу
    import math
    N = 8
    filled = {5, 6, 7}          # непрочитані елементи (між tail і head)
    for i in range(N):
        a = -math.pi / 2 + i * 2 * math.pi / N
        px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        fl = "#eafaf1" if i in filled else FILL
        st = FIELD if i in filled else LINE
        p.append(circle(px, py, 15, fill=fl, stroke=st, sw=1.6))
        p.append(text(px, py + 4, str(i), size=11, color=INK))
    # покажчики head (куди писати наступний = 0) і tail (звідки читати = 5)
    def cell_pos(i):
        a = -math.pi / 2 + i * 2 * math.pi / N
        return cx + r * math.cos(a), cy + r * math.sin(a)
    hx, hy = cell_pos(0)
    tx, ty = cell_pos(5)
    p.append(text(hx, hy - 30, "head → 0", size=12, bold=True, color=NEG))
    p.append(text(tx - 18, ty + 30, "tail → 5", size=12, bold=True, color=FIELD))

    # ── продюсер ліворуч ──
    lx = 30
    p.append(text(lx + 120, 78, "ПРОДЮСЕР (пише head)", size=13, bold=True, color=NEG))
    prod = [
        "buf[head] = x;",
        "head.store(next,",
        "     release);",
    ]
    for i, s in enumerate(prod):
        st = NEG if i >= 1 else LINE
        fl = "#eaf0fd" if i >= 1 else FILL
        b, w, h = textbox(lx + 120, 112 + i * 40, s, size=12, pad=6, min_w=210,
                          stroke=st, fill=fl, bold=(i >= 1), color=(NEG if i >= 1 else INK))
        p.append(b)
    p.append(text(lx + 120, 262, "1) ДАНІ у слот", size=11, color=MUTED))
    p.append(text(lx + 120, 280, "2) публікує head", size=11, color=MUTED))
    # стрілка «кладе у слот 0»
    p.append(arrow(lx + 200, 150, cx - r - 4, cy - 20, color=NEG, sw=2))

    # ── консюмер праворуч ──
    rx = W - 270
    p.append(text(rx + 120, 78, "КОНСЮМЕР (пише tail)", size=13, bold=True, color=FIELD))
    cons = [
        "h = head.load(",
        "     acquire);",
        "x = buf[tail];",
    ]
    for i, s in enumerate(cons):
        st = FIELD if i <= 1 else LINE
        fl = "#eafaf1" if i <= 1 else FILL
        b, w, h = textbox(rx + 120, 112 + i * 40, s, size=12, pad=6, min_w=210,
                          stroke=st, fill=fl, bold=(i <= 1), color=(FIELD if i <= 1 else INK))
        p.append(b)
    p.append(text(rx + 120, 262, "1) підхоплює head", size=11, color=MUTED))
    p.append(text(rx + 120, 280, "2) бере ДАНІ", size=11, color=MUTED))
    p.append(arrow(rx + 40, 200, cx + r + 4, cy + 24, color=FIELD, sw=2))

    # нижній підпис
    b, w, h = textbox(W / 2, 415, ["кожен покажчик має ОДНОГО хазяїна: head — продюсер, tail — консюмер;",
                                   "чуже читають atomic-ом, тож гонки за запис немає — замок зайвий"],
                      size=12, pad=9, stroke=FIELD, fill="#eafaf1", bold=True)
    p.append(b)

    render(os.path.join(OUT, 'spsc-flow.svg'), W, H, *p)


# ── Фігура 2: чому relaxed ламається — публікація head обганяє запис даних ───
def fig_relaxed_breaks():
    W, H = 800, 400
    p = []
    p.append(text(W / 2, 30, "Чому relaxed тут ламає: публікація head обганяє запис у слот", size=15, bold=True))

    # ліворуч: як написано
    lx = 40
    p.append(text(lx + 130, 66, "як написано (продюсер)", size=13, bold=True))
    src = ["buf[0] = 42;", "head = 1;   // relaxed"]
    for i, s in enumerate(src):
        b, w, h = textbox(lx + 130, 100 + i * 44, s, size=13, pad=8, min_w=230)
        p.append(b)
    p.append(text(lx + 130, 190, "намір: дані у слот", size=11, color=MUTED))
    p.append(text(lx + 130, 206, "ПЕРЕД публікацією", size=11, color=MUTED))

    # стрілка перестановки
    p.append(arrow(lx + 260, 130, lx + 320, 130, color=POS, sw=2.2))
    p.append(text(lx + 292, 116, "relaxed →", size=10, color=POS))
    p.append(text(lx + 292, 208, "переставлено", size=10, color=POS))

    # посередині: як виконалось
    mx = 350
    p.append(text(mx + 110, 66, "як виконалось", size=13, bold=True, color=POS))
    src2 = ["head = 1;", "buf[0] = 42;"]
    for i, s in enumerate(src2):
        b, w, h = textbox(mx + 110, 100 + i * 44, s, size=13, pad=8, min_w=200,
                          stroke=(POS if i == 0 else LINE), fill=("#fdecea" if i == 0 else FILL),
                          color=(POS if i == 0 else INK), bold=(i == 0))
        p.append(b)

    # роздільник
    p.append(line(mx + 225, 55, mx + 225, 300, color=MUTED, sw=1, dash="4,4"))

    # праворуч: консюмер ловить діру
    cx = W - 220
    p.append(text(cx + 90, 66, "консюмер", size=13, bold=True, color=NEG))
    b, w, h = textbox(cx + 90, 100, "head == 1 ?", size=12, pad=7, min_w=170, fill="#eaf0fd", stroke=NEG)
    p.append(b)
    b, w, h = textbox(cx + 90, 152, ["читає buf[0]", "→ ще СМІТТЯ!"], size=11, pad=7, min_w=170,
                      fill="#fdecea", stroke=POS, bold=True)
    p.append(b)

    b, w, h = textbox(W / 2, 340, "relaxed НЕ обіцяє порядку: 42 ще не в слоті, а head уже опубліковано — консюмер бере сміття",
                      size=12, pad=9, stroke=POS, fill="#fdecea", bold=True)
    p.append(b)

    render(os.path.join(OUT, 'relaxed-breaks.svg'), W, H, *p)


# ── Фігура 3: false sharing head/tail в одній лінії проти рознесення ─────────
def fig_false_sharing():
    W, H = 800, 400
    p = []
    p.append(text(W / 2, 30, "false sharing: head і tail в одній кеш-лінії пінг-понгують", size=15, bold=True))

    # верх: разом в одній лінії
    p.append(text(70, 78, "разом (одна 64-байтова лінія)", size=13, bold=True, color=POS, anchor="start"))
    lx, ly, cw = 70, 92, 90
    labels = ["head", "tail", "…", "…"]
    for i, lab in enumerate(labels):
        fl = "#fdecea" if i < 2 else FILL
        st = POS if i < 2 else LINE
        p.append(rect(lx + i * cw, ly, cw - 6, 46, fill=fl, stroke=st, sw=1.6, rx=6))
        p.append(text(lx + i * cw + (cw - 6) / 2, ly + 28, lab, size=12,
                      bold=(i < 2), color=(POS if i < 2 else MUTED)))
    # рамка «одна лінія»
    p.append(rect(lx - 4, ly - 4, 4 * cw + 2, 54, fill="none", stroke=POS, sw=2, rx=8))
    p.append(text(lx + 4 * cw + 14, ly + 30, "ОДНА лінія", size=11, color=POS, anchor="start", bold=True))
    # пінг-понг стрілки між ядрами
    p.append(text(lx + 40, ly + 78, "ядро-продюсер", size=11, color=NEG, anchor="start"))
    p.append(text(lx + 3 * cw - 30, ly + 78, "ядро-консюмер", size=11, color=FIELD, anchor="start"))
    p.append(arrow(lx + 90, ly + 66, lx + 3 * cw - 30, ly + 66, color=POS, sw=2))
    p.append(arrow(lx + 3 * cw - 30, ly + 90, lx + 90, ly + 90, color=POS, sw=2))
    p.append(text(lx + 1.9 * cw, ly + 100, "лінія «літає» туди-сюди на КОЖЕН крок", size=11, color=POS, bold=True))

    # низ: рознесено alignas
    p.append(text(70, 246, "рознесено (alignas — кожен у своїй лінії)", size=13, bold=True, color=FIELD, anchor="start"))
    by = 260
    p.append(rect(lx, by, cw - 6, 46, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=6))
    p.append(text(lx + (cw - 6) / 2, by + 28, "head", size=12, bold=True, color=NEG))
    p.append(rect(lx, by + 4, cw - 6, 46, fill="none", stroke="none"))
    # набивка head
    p.append(rect(lx + cw, by, cw - 6, 46, fill=FILL, stroke=LINE, sw=1, rx=6, ))
    p.append(text(lx + cw + (cw - 6) / 2, by + 28, "набивка", size=10, color=MUTED))
    p.append(rect(lx - 4, by - 4, 2 * cw + 2, 54, fill="none", stroke=NEG, sw=2, rx=8))
    # tail у другій лінії
    p.append(rect(lx + 2 * cw + 20, by, cw - 6, 46, fill="#eafaf1", stroke=FIELD, sw=1.6, rx=6))
    p.append(text(lx + 2 * cw + 20 + (cw - 6) / 2, by + 28, "tail", size=12, bold=True, color=FIELD))
    p.append(rect(lx + 3 * cw + 20, by, cw - 6, 46, fill=FILL, stroke=LINE, sw=1, rx=6))
    p.append(text(lx + 3 * cw + 20 + (cw - 6) / 2, by + 28, "набивка", size=10, color=MUTED))
    p.append(rect(lx + 2 * cw + 16, by - 4, 2 * cw + 2, 54, fill="none", stroke=FIELD, sw=2, rx=8))
    p.append(text(lx + cw + 8, by + 78, "лінія A", size=11, color=NEG, anchor="middle"))
    p.append(text(lx + 3 * cw + 28, by + 78, "лінія B", size=11, color=FIELD, anchor="middle"))

    b, w, h = textbox(W / 2, 372, "кожен покажчик у СВОЇЙ лінії → ядра не знеправлюють чужу лінію, пінг-понг зникає",
                      size=12, pad=9, stroke=FIELD, fill="#eafaf1", bold=True)
    p.append(b)

    render(os.path.join(OUT, 'spsc-false-sharing.svg'), W, H, *p)


if __name__ == '__main__':
    fig_spsc_flow()
    fig_relaxed_breaks()
    fig_false_sharing()
    print("spsc figures written to", OUT)
