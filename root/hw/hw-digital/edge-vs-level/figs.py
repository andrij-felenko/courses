# -*- coding: utf-8 -*-
"""Фігури до теми «Фронт і рівень».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CLK = "#2457d6"   # такт — синій
DAT = "#1a1a1a"   # дані/виходи — чорний
HOT = "#c0392b"   # небезпека / гонка — червоний
OK  = "#27ae60"   # «правильно» — зелений


# ── helper: цифровий сигнал по точках (t, рівень 0/1) ───────────────────────
def wave(x0, ybase, hi, unit, samples, color=DAT, sw=2.4):
    """samples — список (індекс_часу, рівень). Малює прямокутний сигнал.
    ybase — лінія нуля; hi — висота піку (від'ємна вгору)."""
    pts = []
    for i, lvl in samples:
        x = x0 + i * unit
        y = ybase - (hi if lvl else 0)
        pts.append((x, y))
    out = []
    for k in range(len(pts) - 1):
        x1, y1 = pts[k]
        x2, y2 = pts[k + 1]
        # вертикальний перепад на зміні рівня
        if y1 != y2:
            out.append(line(x1, y1, x1, y2, color=color, sw=sw))
        out.append(line(x1, min(y1, y2) if y1 == y2 else y2, x2, y2, color=color, sw=sw)
                   if y1 != y2 else line(x1, y1, x2, y2, color=color, sw=sw))
    return "".join(out)


def rising_marks(x0, unit, idxs, ytop, ybot, color=HOT):
    """Вертикальні штрихи + трикутник ▲ на робочих фронтах такту."""
    out = []
    for i in idxs:
        x = x0 + i * unit
        out.append(line(x, ytop - 6, x, ybot + 6, color=color, sw=1.1, dash="3 4"))
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
                   % (x - 5, ytop - 8, x + 5, ytop - 8, x, ytop - 17, color))
    return "".join(out)


def lbl(x, y, s, color=MUTED, size=13, anchor="end", bold=False):
    return text(x, y, s, size=size, color=color, anchor=anchor, bold=bold)


# ── 1. Рівнева засувка проти тригера по фронту ──────────────────────────────
def fig_level_vs_edge():
    W, H = 720, 430
    f = [text(W / 2, 28, "Той самий такт і вхід — латч іде за рівнем, тригер ловить мить",
              size=16, bold=True)]
    x0, unit = 150, 62
    n = 8
    # такт: рівний меандр
    clk = [(0, 0), (1, 1), (2, 1), (3, 0), (3, 0), (4, 1), (5, 1), (6, 0), (7, 0)]
    clk_sq = [(0, 0), (1, 1), (3, 1), (3, 0)] if False else None
    # будуємо меандр такту вручну: 0 у [0..1], 1 у [1..3], 0 у [3..5], 1 у [5..7]
    clk_s = [(0, 0), (1, 0), (1, 1), (3, 1), (3, 0), (5, 0), (5, 1), (7, 1), (7, 0), (n, 0)]
    # D: 0, піднявся посеред першого високого такту (t=2), тримається 1
    d_s = [(0, 0), (2, 0), (2, 1), (n, 1)]
    # латч (рівневий): прозорий поки clk=1 → пішов за D у t=2 (бо clk ще 1 до t=3)
    latch_s = [(0, 0), (2, 0), (2, 1), (n, 1)]
    # тригер (фронт): на t=1 D=0 → лишився 0; на t=5 (наступний фронт) D=1 → 1
    edge_s = [(0, 0), (5, 0), (5, 1), (n, 1)]

    rows = [("такт", clk_s, CLK, 90),
            ("D", d_s, DAT, 175),
            ("латч (рівень)", latch_s, HOT, 270),
            ("тригер (фронт)", edge_s, OK, 360)]
    hi = 46
    for name, s, col, yb in rows:
        f.append(line(x0, yb, x0 + n * unit, yb, color=MUTED, sw=0.8))  # базова лінія
        f.append(wave(x0, yb, hi, unit, s, color=col))
        f.append(lbl(x0 - 12, yb - hi / 2 + 5, name, color=col, bold=True))
    # робочі фронти такту: наростання у t=1 і t=5
    f.append(rising_marks(x0, unit, [1, 5], 90 - hi, 360))
    # позначка «D піднявся тут»
    xd = x0 + 2 * unit
    f.append(text(xd, 175 - hi - 10, "D↑ посеред такту", size=12, color=MUTED))
    # пояснення розбіжності
    xmid = x0 + 3.4 * unit
    f.append(text(xmid, 405, "тут латч уже 1, а тригер ще 0 — чекає наступного фронту",
                  size=12.5, color=HOT))
    render(os.path.join(IMG, "level-vs-edge.svg"), W, H, *f)


# ── 2. Гонка крізь прозорий латч ────────────────────────────────────────────
def fig_racethrough():
    W, H = 752, 400
    f = [text(W / 2, 28, "Прозорий латч у петлі: значення оббігає коло багато разів за такт",
              size=16, bold=True)]
    # схема: латч, вихід Q через інвертор назад на D
    bx, by, bw, bh = 250, 90, 150, 90
    f.append(rect(bx, by, bw, bh, fill=FILL))
    f.append(text(bx + bw / 2, by + 26, "латч", size=15, bold=True))
    f.append(text(bx + 14, by + 58, "D", size=14, anchor="start"))
    f.append(text(bx + bw - 14, by + 58, "Q", size=14, anchor="end"))
    f.append(text(bx + bw / 2, by + bh - 12, "EN = такт", size=12, color=CLK))
    # інвертор знизу
    iy = by + bh + 70
    ix = bx + bw / 2
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" stroke="%s" stroke-width="1.5"/>'
             % (ix + 26, iy, ix - 26, iy - 18, ix - 26, iy + 18, "#eaf0fd", NEG))
    f.append(circle(ix + 33, iy, 5, fill=BG, stroke=NEG, sw=1.5))
    f.append(text(ix, iy + 40, "інвертор", size=12, color=NEG))
    # дроти петлі: Q вниз → інвертор → вгору в D
    f.append(line(bx + bw, by + bh / 2, bx + bw + 70, by + bh / 2, color=HOT, sw=2))
    f.append(line(bx + bw + 70, by + bh / 2, bx + bw + 70, iy, color=HOT, sw=2))
    f.append(arrow(bx + bw + 70, iy, ix + 40, iy, color=HOT, sw=2))
    f.append(line(ix - 26, iy, bx - 70, iy, color=HOT, sw=2))
    f.append(line(bx - 70, iy, bx - 70, by + bh / 2, color=HOT, sw=2))
    f.append(arrow(bx - 70, by + bh / 2, bx, by + bh / 2, color=HOT, sw=2))
    # коло-стрілка «×N»
    f.append(text(bx - 78, iy - 36, "↻", size=30, color=HOT, anchor="middle"))
    f.append(text(bx - 78, iy - 8, "×N", size=15, color=HOT, bold=True, anchor="middle"))
    # підпис праворуч
    msg = ("Поки такт = 1, латч відкритий.\n"
           "Нове Q інвертується, вертається на D,\n"
           "знову міняє Q — і так багато разів\n"
           "за ОДИН високий такт. Скільки —\n"
           "залежить від затримок вентилів.")
    f.append(mtext(bx + bw + 95, by + 18, msg, size=13, color=INK, anchor="start", lh=1.45))
    f.append(text(bx + bw + 95, iy + 30, "Результат непередбачуваний — гонка (race-through).",
                  size=13, color=HOT, anchor="start", bold=True))
    render(os.path.join(IMG, "racethrough.svg"), W, H, *f)


# ── 3. Фронт дає рівно одне оновлення за такт ───────────────────────────────
def fig_edge_solves():
    W, H = 720, 360
    f = [text(W / 2, 28, "Та сама петля через тригер по фронту: рівно одне оновлення за такт",
              size=16, bold=True)]
    x0, unit = 150, 64
    n = 8
    clk_s = [(0, 0), (1, 0), (1, 1), (3, 1), (3, 0), (5, 0), (5, 1), (7, 1), (7, 0), (n, 0)]
    # Q ділить такт навпіл: перемикається на кожному фронті (t=1,5) → toggle
    q_s = [(0, 0), (1, 0), (1, 1), (5, 1), (5, 0), (n, 0)]
    rows = [("такт", clk_s, CLK, 110), ("Q (= toggle)", q_s, OK, 230)]
    hi = 48
    for name, s, col, yb in rows:
        f.append(line(x0, yb, x0 + n * unit, yb, color=MUTED, sw=0.8))
        f.append(wave(x0, yb, hi, unit, s, color=col))
        f.append(lbl(x0 - 12, yb - hi / 2 + 5, name, color=col, bold=True))
    f.append(rising_marks(x0, unit, [1, 5], 110 - hi, 230))
    f.append(text(W / 2, 300,
                  "Захоплення триває лише мить — нове Q не встигає оббігти петлю на ЦЬОМУ ж фронті;",
                  size=13, color=INK))
    f.append(text(W / 2, 322,
                  "воно вплине аж на наступному. Один фронт — один крок.",
                  size=13, color=OK, bold=True))
    render(os.path.join(IMG, "edge-solves.svg"), W, H, *f)


# ── 4. Зсувний регістр: біт крокує на щабель за такт ────────────────────────
def fig_shift():
    W, H = 962, 410
    f = [text(W / 2, 28, "Зсувний регістр: на тригерах біт крокує по одному щаблю за фронт",
              size=16, bold=True)]
    # три тригери в ряд
    bw, bh = 120, 70
    gap = 50
    y = 70
    xs = [120, 120 + bw + gap, 120 + 2 * (bw + gap)]
    names = ["DFF 1", "DFF 2", "DFF 3"]
    outs = ["Q1", "Q2", "Q3"]
    f.append(text(60, y + bh / 2 + 5, "IN", size=14, bold=True, anchor="start"))
    f.append(arrow(95, y + bh / 2, xs[0], y + bh / 2, color=DAT, sw=2))
    for k, x in enumerate(xs):
        f.append(rect(x, y, bw, bh, fill=FILL))
        f.append(text(x + bw / 2, y + 28, names[k], size=14, bold=True))
        # трикутник такту
        f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" stroke="%s" stroke-width="1.6"/>'
                 % (x + 8, y + bh - 20, x + 8, y + bh - 4, x + 20, y + bh - 12, CLK))
        f.append(text(x + bw - 12, y + bh - 10, outs[k], size=13, anchor="end", color=DAT))
        if k < 2:
            f.append(arrow(x + bw, y + bh / 2, xs[k + 1], y + bh / 2, color=DAT, sw=2))
    # спільний такт знизу
    cy = y + bh + 26
    f.append(line(xs[0] + 14, cy, xs[2] + 14, cy, color=CLK, sw=2))
    for x in xs:
        f.append(line(x + 14, cy, x + 14, y + bh, color=CLK, sw=2))
    f.append(text(xs[2] + bw, cy + 4, "спільний такт", size=12, color=CLK, anchor="start"))
    # таблиця кроків: одиничка крокує
    tx, ty = 120, cy + 60
    cellw, cellh = 70, 30
    head = ["фронт", "Q1", "Q2", "Q3"]
    data = [["1", "1", "0", "0"], ["2", "0", "1", "0"], ["3", "0", "0", "1"]]
    cols = len(head)
    for c in range(cols):
        f.append(rect(tx + c * cellw, ty, cellw, cellh, fill="#eef2ff", stroke=LINE))
        f.append(text(tx + c * cellw + cellw / 2, ty + 20, head[c], size=13, bold=True, color=CLK))
    for r, row in enumerate(data):
        yy = ty + (r + 1) * cellh
        for c, val in enumerate(row):
            hot = (c >= 1 and val == "1")
            f.append(rect(tx + c * cellw, yy, cellw, cellh, fill="#fdecea" if hot else BG, stroke=LINE))
            f.append(text(tx + c * cellw + cellw / 2, yy + 20, val, size=13,
                          bold=hot, color=HOT if hot else INK))
    f.append(text(tx + cols * cellw + 24, ty + cellh + 40,
                  "Кожен ловить СТАРЕ\nзначення сусіда\nперед фронтом —\nтож одиничка крокує,\nа не прослизає.",
                  size=12.5, color=INK, anchor="start"))
    render(os.path.join(IMG, "shift.svg"), W, H, *f)


# ── 5. По якому фронту — і чому фронт мусить бути чистим ─────────────────────
def fig_rise_fall():
    W, H = 720, 380
    f = [text(W / 2, 28, "По якому фронту спрацьовує тригер — і чому фронт мусить бути чистим",
              size=16, bold=True)]
    # ліва половина: наростання, права: спад
    # такт зліва
    x0, unit = 90, 46
    clk_s = [(0, 0), (1, 0), (1, 1), (3, 1), (3, 0), (4, 0)]
    yb = 110
    hi = 44
    f.append(line(x0, yb, x0 + 4 * unit, yb, color=MUTED, sw=0.8))
    f.append(wave(x0, yb, hi, unit, clk_s, color=CLK))
    f.append(lbl(x0 - 8, yb - hi / 2 + 5, "такт", color=CLK, bold=True))
    f.append(rising_marks(x0, unit, [1], yb - hi, yb))
    f.append(text(x0 + 1 * unit, yb + 28, "наростання ▲", size=13, color=OK, bold=True))
    f.append(text(x0 + 1.6 * unit, 70, "трикутник ❯ без кружка", size=12, color=MUTED))

    # права: спад з кружком
    x1 = 410
    f.append(line(x1, yb, x1 + 4 * unit, yb, color=MUTED, sw=0.8))
    f.append(wave(x1, yb, hi, unit, clk_s, color=CLK))
    # позначити спад (t=3) трикутником ▼
    xs = x1 + 3 * unit
    f.append(line(xs, yb - hi - 6, xs, yb + 6, color=HOT, sw=1.1, dash="3 4"))
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
             % (xs - 5, yb + 8, xs + 5, yb + 8, xs, yb + 17, HOT))
    f.append(text(xs, yb + 36, "спад ▼", size=13, color=HOT, bold=True))
    f.append(text(x1 + 2 * unit, 70, "кружок на тактовому вході", size=12, color=MUTED))

    # внизу: крутий проти кволого фронту
    yb2 = 280
    f.append(line(120, yb2, 320, yb2, color=MUTED, sw=0.8))
    # крутий: майже вертикаль
    f.append(line(200, yb2, 200, yb2 - 56, color=OK, sw=3))
    f.append(line(200, yb2 - 56, 300, yb2 - 56, color=OK, sw=3))
    f.append(text(220, yb2 + 22, "крутий — чітка мить", size=12.5, color=OK, bold=True))
    # кволий: похила лінія + дрижання
    f.append(line(420, yb2, 470, yb2 - 56, color=HOT, sw=3))
    f.append(line(470, yb2 - 56, 540, yb2 - 56, color=HOT, sw=3))
    # дрижання біля порога
    f.append(line(443, yb2 - 28, 448, yb2 - 22, color=HOT, sw=1.4))
    f.append(line(448, yb2 - 22, 452, yb2 - 34, color=HOT, sw=1.4))
    f.append(line(452, yb2 - 34, 457, yb2 - 26, color=HOT, sw=1.4))
    f.append(text(470, yb2 + 22, "кволий — момент розмазаний", size=12.5, color=HOT, bold=True))
    f.append(text(W / 2, 350, "Кволий чи зашумлений фронт — тригер може смикнутися двічі або застрягти.",
                  size=13, color=INK))
    render(os.path.join(IMG, "rise-fall.svg"), W, H, *f)


if __name__ == "__main__":
    fig_level_vs_edge()
    fig_racethrough()
    fig_edge_solves()
    fig_shift()
    fig_rise_fall()
    print("OK figs.py -> img/")
