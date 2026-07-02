# -*- coding: utf-8 -*-
"""Фігури до статті «Тактове стробування» (book/electronics/digital/clock-gating).

Кут статті: такт — найненажерливіший сигнал у синхронній схемі; глушити його
дешево, але наївний AND дає глітч, тож перед вентилем ставлять засувку (ICG).

Фігури:
  clock-tree-power.svg — тактове дерево до кожного тригера; воно цокає завжди
  naive-and-glitch.svg — голий AND: спад дозволу при високому такті ріже глітч
  glitch-free-icg.svg  — засувка перед вентилем: дозвіл застигає на високому такті
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CLK = "#2457d6"   # такт — синім
GATED = "#c0392b" # глітч / небезпека — червоним
OK = "#27ae60"    # чистий результат — зеленим


# ── маленькі символи ────────────────────────────────────────────────────────
def and_gate(cx, cy, w=52, h=54):
    """Вентиль «І»: пряма ліва грань, півколо праворуч. Повертає (svg, nodes)."""
    x0 = cx - w / 2
    top, bot = cy - h / 2, cy + h / 2
    r = h / 2
    xflat = x0 + w * 0.42
    d = ('M %.1f %.1f L %.1f %.1f L %.1f %.1f '
         'A %.1f %.1f 0 0 1 %.1f %.1f L %.1f %.1f Z') % (
        x0, top, xflat, top, xflat, top, r, r, xflat, bot, x0, bot)
    svg = ('<path d="%s" fill="#ffffff" stroke="%s" stroke-width="1.8"/>' % (d, INK))
    svg += text(x0 + w * 0.28, cy + 5, "&", size=15, color=MUTED, bold=True)
    nodes = {"in_a": (x0, cy - h * 0.24), "in_b": (x0, cy + h * 0.24),
             "out": (xflat + r, cy)}
    return svg, nodes


def ff(cx, cy, w=48, h=58, label="D"):
    """Тригер-прямокутник із трикутником-тактом унизу зліва."""
    x0, y0 = cx - w / 2, cy - h / 2
    svg = rect(x0, y0, w, h, fill="#ffffff", stroke=INK, sw=1.6, rx=4)
    svg += text(cx, cy - 4, label, size=13, color=INK, bold=True)
    svg += text(cx, cy + 13, "Q", size=11, color=MUTED)
    # символ такту — маленький трикутник біля нижнього лівого входу
    ty = y0 + h * 0.72
    svg += ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="1.4"/>' % (
                x0, ty - 5, x0 + 8, ty, x0, ty + 5, INK))
    nodes = {"clk": (x0, ty), "in": (x0, cy - h * 0.28), "out": (x0 + w, cy)}
    return svg, nodes


def wave(x, y, seq, unit=17, hi=20, color=CLK, sw=2.0):
    """Цифрова хвиля зі списку рівнів 0/1. seq — рядок '0101…'.
    Повертає (svg, кінцевий x)."""
    pts = []
    cx = x
    lvl = int(seq[0])
    pts.append((cx, y - hi * lvl))
    for ch in seq[1:]:
        nl = int(ch)
        if nl != lvl:
            pts.append((cx, y - hi * lvl))   # вертикальний фронт
            pts.append((cx, y - hi * nl))
            lvl = nl
        cx += unit
        pts.append((cx, y - hi * lvl))
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    svg = '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)
    return svg, cx


# ── 1) Тактове дерево: один сигнал до кожного тригера ────────────────────────
def fig_clock_tree():
    W, H = 720, 360
    body = []
    body.append(text(W / 2, 26, "Такт розводиться до кожного тригера — і цокає завжди", size=16, bold=True))

    # джерело такту зліва
    sx, sy = 70, H / 2 + 6
    b, w, h = textbox(sx, sy, "джерело\nтакту", size=12, fill="#eaf0fd", stroke=CLK, sw=1.8)
    body.append(b)
    root_x = sx + w / 2

    # два рівні повторювачів (дерево)
    lvl1_x = 250
    lvl1_y = [H / 2 - 70, H / 2 + 82]
    lvl2_x = 430
    leaves_y = [70, 130, 205, 265, 320]

    def buf(cx, cy):
        # трикутник-повторювач вершиною вправо
        s = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#ffffff" '
             'stroke="%s" stroke-width="1.6"/>' % (cx - 12, cy - 12, cx - 12, cy + 12, cx + 14, cy, CLK))
        return s, (cx - 12, cy), (cx + 14, cy)

    # корінь → два буфери рівня 1
    for ly in lvl1_y:
        body.append(line(root_x, sy, lvl1_x - 12, ly, color=CLK, sw=2.0))
    l1nodes = []
    for ly in lvl1_y:
        s, i, o = buf(lvl1_x, ly)
        body.append(s); l1nodes.append((i, o, ly))

    # кожен буфер1 → кілька листків через буфери рівня 2 (спрощено: прямі до тригерів)
    # верхній буфер живить перші 2-3 листки, нижній — решту
    groups = [leaves_y[:2], leaves_y[2:]]
    for (i, o, ly), grp in zip(l1nodes, groups):
        s2, i2, o2 = buf(lvl2_x, ly)
        body.append(line(o[0], o[1], lvl2_x - 12, ly, color=CLK, sw=1.8))
        body.append(s2)
        for gy in grp:
            body.append(line(o2[0], o2[1], 560, gy, color=CLK, sw=1.6))

    # тригери-листки
    for gy in leaves_y:
        s, n = ff(600, gy, w=44, h=40, label="FF")
        body.append(s)
        # вхід такту в тригер
        body.append(line(560, gy, n["clk"][0], n["clk"][1], color=CLK, sw=1.6))

    # підпис-акцент (дві короткі стрічки, щоб не налазити на тригери справа)
    b2, _, _ = textbox(300, H - 28,
                       "α максимальна · велика ємність дерева\nцокає, навіть коли тригери переписують те саме",
                       size=11, fill="#fff6f5", stroke=GATED, sw=1.4, color=INK)
    body.append(b2)
    render(os.path.join(IMG, "clock-tree-power.svg"), W, H, *body)


# ── 2) Наївний AND: глітч на спаді дозволу під час високого такту ───────────
def fig_naive_glitch():
    W, H = 720, 380
    body = []
    body.append(text(W / 2, 26, "Голий «І» на такті: спад дозволу під час високого такту ріже глітч", size=15, bold=True))

    # схема зверху-зліва
    g, gn = and_gate(150, 92)
    body.append(g)
    body.append(line(70, gn["in_a"][1], gn["in_a"][0], gn["in_a"][1], color=CLK, sw=1.8))
    body.append(text(60, gn["in_a"][1] + 4, "такт", size=12, color=CLK, anchor="end", bold=True))
    body.append(line(70, gn["in_b"][1], gn["in_b"][0], gn["in_b"][1], color=INK, sw=1.6))
    body.append(text(60, gn["in_b"][1] + 4, "дозвіл", size=12, color=INK, anchor="end"))
    body.append(line(gn["out"][0], gn["out"][1], 250, gn["out"][1], color=GATED, sw=2.0))
    body.append(text(258, gn["out"][1] + 4, "на тригери", size=12, color=GATED, anchor="start"))

    # часові діаграми знизу
    x0 = 120
    lab_x = 105
    # такт: 8 клітин, чергування
    yt = 200
    body.append(text(lab_x, yt - 6, "такт", size=12, color=CLK, anchor="end", bold=True))
    ws, _ = wave(x0, yt, "0110110110", color=CLK)
    body.append(ws)

    # дозвіл: був 1, падає в 0 у момент, коли такт високий
    ye = 265
    body.append(text(lab_x, ye - 6, "дозвіл", size=12, color=INK, anchor="end"))
    we, _ = wave(x0, ye, "1111100000", color=INK)
    body.append(we)

    # вихід = такт AND дозвіл: поки дозвіл 1 повторює такт, тоді 0 — АЛЕ обрубаний куций фронт
    yo = 335
    body.append(text(lab_x, yo - 6, "вихід", size=12, color=GATED, anchor="end", bold=True))
    # вихід повторює такт, доки дозвіл=1; фронт спаду дозволу приходить під час високого такту → куций імпульс
    wo, _ = wave(x0, yo, "0110100000", color=GATED)
    body.append(wo)

    # позначити глітч стрілкою
    unit = 17
    gx = x0 + unit * 4.5
    body.append(('<path d="M %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" '
                 'stroke-width="1.4" marker-end="url(#arrow)"/>' % (gx + 34, yo - 46, gx + 4, yo - 22, GATED)))
    b, _, _ = textbox(gx + 78, yo - 52, "глітч:\nхибний фронт", size=10.5, fill="#fff6f5",
                      stroke=GATED, sw=1.4, color=GATED)
    body.append(b)

    render(os.path.join(IMG, "naive-and-glitch.svg"), W, H, *body)


# ── 3) Безглітчева ICG: засувка защіпує дозвіл, вихід чистий ─────────────────
def fig_icg():
    W, H = 720, 390
    body = []
    body.append(text(W / 2, 26, "Засувка перед «І»: на високому такті дозвіл застигає — глітчу нізвідки взятися", size=14.5, bold=True))

    # схема: дозвіл → засувка (прозора при низькому такті) → AND(такт) → чистий такт
    ly = 90
    # засувка як прямокутник
    lb = rect(120, ly - 26, 92, 52, fill="#ffffff", stroke=INK, sw=1.6, rx=5)
    body.append(lb)
    body.append(text(166, ly - 4, "засувка", size=11.5, color=INK, bold=True))
    body.append(text(166, ly + 12, "(прозора при 0)", size=9.5, color=MUTED))
    # вхід дозволу
    body.append(line(48, ly, 120, ly, color=INK, sw=1.6))
    body.append(text(44, ly + 4, "дозвіл", size=12, color=INK, anchor="end"))
    # такт у нижній вхід засувки (керує прозорістю)
    body.append(line(166, ly + 26, 166, ly + 60, color=CLK, sw=1.6))
    body.append(text(166, ly + 74, "такт", size=11, color=CLK, anchor="middle", bold=True))

    # AND
    g, gn = and_gate(330, ly)
    body.append(g)
    body.append(line(212, ly, gn["in_a"][0], gn["in_a"][1], color=INK, sw=1.6))
    body.append(text(232, ly - 18, "дозвіл_защ", size=10, color=MUTED, anchor="middle"))
    # такт у другий вхід AND
    body.append(line(230, ly + 92, 230, gn["in_b"][1], color=CLK, sw=1.6))
    body.append(line(230, gn["in_b"][1], gn["in_b"][0], gn["in_b"][1], color=CLK, sw=1.6))
    body.append(text(215, ly + 96, "такт", size=11, color=CLK, anchor="end", bold=True))
    # вихід
    body.append(line(gn["out"][0], gn["out"][1], 430, gn["out"][1], color=OK, sw=2.0))
    body.append(mtext(438, gn["out"][1] - 5, ["чистий", "строб. такт"], size=11, color=OK, anchor="start"))

    # часові діаграми
    x0 = 120
    lab_x = 105
    yt = 210
    body.append(text(lab_x, yt - 6, "такт", size=12, color=CLK, anchor="end", bold=True))
    ws, _ = wave(x0, yt, "0110110110", color=CLK)
    body.append(ws)

    ye = 275
    body.append(text(lab_x, ye - 6, "дозвіл", size=12, color=INK, anchor="end"))
    # дозвіл смикається під час високого такту (небезпечно) — але засувка це проковтне
    we, _ = wave(x0, ye, "1110100000", color=INK)
    body.append(we)

    yl = 335
    body.append(text(lab_x, yl - 6, "вихід", size=12, color=OK, anchor="end", bold=True))
    # засувка защіпує дозвіл на підйомі, тому спад «переноситься» на низьку фазу такту →
    # вихід — чисті повні такти, доки защіпнутий дозвіл 1, тоді рівний нуль
    wo, _ = wave(x0, yl, "0110110000", color=OK)
    body.append(wo)

    b, _, _ = textbox(560, 300, "дозвіл змінюється,\nале вихід — тільки\nповні такти або нуль",
                      size=10.5, fill="#eafaf1", stroke=OK, sw=1.4, color=INK)
    body.append(b)

    render(os.path.join(IMG, "glitch-free-icg.svg"), W, H, *body)


if __name__ == "__main__":
    fig_clock_tree()
    fig_naive_glitch()
    fig_icg()
    print("OK: figures written to", IMG)
