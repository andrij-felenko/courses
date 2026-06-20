# -*- coding: utf-8 -*-
"""Фігури до теми «Оптичний інкрементний енкодер».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Щілинний диск + оптопереривач → потік імпульсів ───────────────────────
def fig_disk():
    W, H = 760, 430
    f = [text(W / 2, 28, "Щілинний диск перетворює обертання на імпульси", size=16, bold=True)]

    # --- диск зі щілинами на валу ---
    cx, cy = 210, 230
    R_out, R_in = 130, 92          # зовнішній край і дно щілин
    f.append(circle(cx, cy, R_out, fill="#eef2f8", stroke=INK, sw=2))
    f.append(circle(cx, cy, R_in, fill=BG, stroke=MUTED, sw=1.2))
    # щілини (наскрізні прорізи) — світлі сектори у темному вінці
    n = 24
    for i in range(n):
        if i % 2:                  # через одну — щілина
            continue
        a0 = math.radians(i * 360.0 / n)
        a1 = math.radians((i + 1) * 360.0 / n)
        x0o, y0o = cx + R_out * math.cos(a0), cy + R_out * math.sin(a0)
        x1o, y1o = cx + R_out * math.cos(a1), cy + R_out * math.sin(a1)
        x1i, y1i = cx + R_in * math.cos(a1), cy + R_in * math.sin(a1)
        x0i, y0i = cx + R_in * math.cos(a0), cy + R_in * math.sin(a0)
        d = ("M%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f L%.1f %.1f A%.1f %.1f 0 0 0 %.1f %.1f Z"
             % (x0o, y0o, R_out, R_out, x1o, y1o, x1i, y1i, R_in, R_in, x0i, y0i))
        f.append('<path d="%s" fill="#ffffff" stroke="%s" stroke-width="1"/>' % (d, MUTED))
    # маточина й вал
    f.append(circle(cx, cy, 20, fill="#d8dde4", stroke=INK, sw=1.5))
    f.append(circle(cx, cy, 6, fill=INK, stroke=INK, sw=1))
    f.append(text(cx, cy + 4, "вал", size=10.5, color=BG, bold=True))
    # стрілка обертання
    f.append('<path d="M%.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2.2" marker-end="url(#arrow)"/>'
             % (cx + 150, cy - 30, 150, 150, cx + 150, cy + 30, FIELD))
    f.append(text(cx + 168, cy + 4, "оберт", size=11, color=FIELD, bold=True, anchor="start"))

    # --- оптопереривач: світлодіод над краєм, приймач під краєм ---
    ex = cx                         # промінь б'є крізь верхній край диска
    ey_led, ey_pd = cy - R_out - 36, cy - R_in + 22
    led = fitbox(ex - 46, ey_led - 16, 92, 30, "світлодіод", size=10.5,
                 fill="#fdf3e2", stroke="#b8801f", color="#8a5f12")
    f.append(led)
    pd = fitbox(ex - 52, ey_pd - 4, 104, 30, "фотоприймач", size=10.5,
                fill="#eef6ef", stroke=FIELD, color="#1e7a43")
    f.append(pd)
    # промінь крізь щілину (жовтий пунктир)
    f.append(line(ex, ey_led + 16, ex, ey_pd - 4, color="#e0a93c", sw=2.4, dash="4 3"))
    f.append(text(ex + 8, (ey_led + ey_pd) / 2, "промінь", size=9.5,
                  color="#b8801f", anchor="start"))

    # --- потік імпульсів праворуч ---
    gx, gy = 430, 250              # лівий-низ осі сигналу
    gw, amp = 290, 56
    f.append(text(gx + gw / 2, gy - amp - 26, "сигнал фотоприймача", size=12.5, bold=True))
    f.append(line(gx, gy, gx + gw + 8, gy, color=MUTED, sw=1.2))           # вісь часу
    f.append(text(gx + gw + 14, gy + 4, "t", size=12, color=MUTED, anchor="start", italic=True))
    # прямокутна хвиля: щілина=1 (світло), перемичка=0 (темрява)
    seg = gw / 8.0
    lvl = [1, 0, 1, 0, 1, 0, 1, 0]
    px, py = gx, gy - lvl[0] * amp
    path = "M%.1f %.1f" % (px, py)
    for k in range(8):
        ny = gy - lvl[k] * amp
        if ny != py:
            path += " L%.1f %.1f" % (px, ny)
        px += seg
        path += " L%.1f %.1f" % (px, ny)
        py = ny
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path, NEG))
    f.append(text(gx + seg * 0.5, gy - amp - 8, "1", size=11, color=NEG))
    f.append(text(gx + seg * 1.5, gy + 16, "0", size=11, color=NEG))
    f.append(text(gx, gy + amp - 8, "світло", size=9.5, color=MUTED, anchor="start"))
    # підписати «одна щілина = один імпульс»
    f.append(line(gx + seg * 0, gy + 26, gx + seg * 2, gy + 26, color=INK, sw=1))
    f.append(line(gx + seg * 0, gy + 22, gx + seg * 0, gy + 30, color=INK, sw=1))
    f.append(line(gx + seg * 2, gy + 22, gx + seg * 2, gy + 30, color=INK, sw=1))
    f.append(text(gx + seg, gy + 40, "одна щілина = один імпульс", size=10.5, color=INK))

    render(os.path.join(IMG, "disk.svg"), W, H, *f)


# ── 2. Квадратура A/B: напрям із порядку фронтів + кільце станів ──────────────
def _wave(f, x0, y0, w, levels, color, amp=30):
    """Намалювати прямокутний сигнал за списком рівнів 0/1; повертає нічого."""
    seg = w / float(len(levels))
    px, py = x0, y0 - levels[0] * amp
    path = "M%.1f %.1f" % (px, py)
    for lv in levels:
        ny = y0 - lv * amp
        if ny != py:
            path += " L%.1f %.1f" % (px, ny)
        px += seg
        path += " L%.1f %.1f" % (px, ny)
        py = ny
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path, color))


def fig_quadrature():
    W, H = 760, 470
    f = [text(W / 2, 28, "Квадратура A/B: порядок фронтів видає напрям", size=16, bold=True)]

    # рівні A та B зі зсувом на чверть періоду (8 півклітинок = 2 періоди)
    A = [1, 1, 0, 0, 1, 1, 0, 0]
    B = [0, 1, 1, 0, 0, 1, 1, 0]        # B зсунуто на чверть відносно A

    # --- блок «уперед» ---
    bx, gw = 70, 330
    yA, yB = 92, 150
    f.append(text(bx, 70, "вал ВПЕРЕД:  A випереджає B", size=12.5, bold=True,
                  color=FIELD, anchor="start"))
    f.append(text(bx - 18, yA - 6, "A", size=12, bold=True, color=POS, anchor="middle"))
    f.append(text(bx - 18, yB - 6, "B", size=12, bold=True, color=NEG, anchor="middle"))
    f.append(line(bx, yA + 4, bx + gw + 6, yA + 4, color=MUTED, sw=1))
    f.append(line(bx, yB + 4, bx + gw + 6, yB + 4, color=MUTED, sw=1))
    _wave(f, bx, yA, gw, A, POS)
    _wave(f, bx, yB, gw, B, NEG)
    # позначити, що фронт A раніше за фронт B на першому кроці
    seg = gw / 8.0
    f.append(line(bx + seg * 0, yA - 30, bx + seg * 0, 178, color=FIELD, sw=1, dash="3 3"))
    f.append(line(bx + seg * 1, yB - 30, bx + seg * 1, 178, color=FIELD, sw=1, dash="3 3"))
    f.append(text(bx + seg * 0.5, 192, "A↑", size=10, color=POS))
    f.append(text(bx + seg * 1.5, 192, "B↑", size=10, color=NEG))

    # --- блок «назад» ---
    yA2, yB2 = 268, 326
    f.append(text(bx, 244, "вал НАЗАД:  B випереджає A", size=12.5, bold=True,
                  color=POS, anchor="start"))
    f.append(text(bx - 18, yA2 - 6, "A", size=12, bold=True, color=POS, anchor="middle"))
    f.append(text(bx - 18, yB2 - 6, "B", size=12, bold=True, color=NEG, anchor="middle"))
    f.append(line(bx, yA2 + 4, bx + gw + 6, yA2 + 4, color=MUTED, sw=1))
    f.append(line(bx, yB2 + 4, bx + gw + 6, yB2 + 4, color=MUTED, sw=1))
    # назад = той самий рисунок, але читаємо так, що B попереду: дзеркалимо рівні
    _wave(f, bx, yA2, gw, A[::-1], POS)
    _wave(f, bx, yB2, gw, B[::-1], NEG)

    # --- кільце станів (A,B) праворуч ---
    rcx, rcy, rr = 590, 230, 92
    f.append(text(rcx, 70, "кільце станів (A,B)", size=12.5, bold=True))
    states = ["00", "01", "11", "10"]      # порядок обходу вперед
    ang = [-90, 0, 90, 180]
    pts = []
    for s, a in zip(states, ang):
        ax = rcx + rr * math.cos(math.radians(a))
        ay = rcy + rr * math.sin(math.radians(a))
        pts.append((ax, ay))
        b, _, _ = textbox(ax, ay, s, size=13, bold=True, fill=BG, stroke=INK, min_w=44)
        f.append(b)
    # дуги-стрілки по колу (вперед, зелені)
    for i in range(4):
        a0 = math.radians(ang[i] + 22)
        a1 = math.radians(ang[(i + 1) % 4] - 22)
        # нормалізувати, щоб дуга йшла коротким шляхом за годинниковою
        x0 = rcx + rr * math.cos(a0); y0 = rcy + rr * math.sin(a0)
        x1 = rcx + rr * math.cos(a1); y1 = rcy + rr * math.sin(a1)
        f.append('<path d="M%.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
                 % (x0, y0, rr, rr, x1, y1, FIELD))
    f.append(text(rcx, rcy - 4, "вперед", size=11, color=FIELD, bold=True))
    f.append(text(rcx, rcy + 14, "↻", size=16, color=FIELD, bold=True))
    f.append(text(rcx, rcy + rr + 56, "назад — те саме кільце", size=10.5, color=POS))
    f.append(text(rcx, rcy + rr + 72, "у протилежний бік", size=10.5, color=POS))

    # підсумковий рядок
    f.append(text(W / 2, H - 18,
                  "за крок змінюється рівно один біт — кільце однозначне, а бік обходу = напрям",
                  size=11.5, color=INK, italic=True))

    render(os.path.join(IMG, "quadrature.svg"), W, H, *f)


if __name__ == "__main__":
    fig_disk()
    fig_quadrature()
    print("OK: disk.svg, quadrature.svg")
