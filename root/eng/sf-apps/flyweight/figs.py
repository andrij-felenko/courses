# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

LIGHT_POS   = "#fdecea"
LIGHT_FIELD = "#e8f6ee"
LIGHT_NEG   = "#eaf0fd"
GOLD        = "#b8860b"
LIGHT_GOLD  = "#fff7e6"


# ── Фігура 1: розріз стану — наївно (дублювання) проти легковаговика (спільне) ─
def fig_split():
    W, H = 1200, 700
    f = []
    f.append(text(W / 2, 32, "Той самий важкий стан — зберігати мільйон разів чи один раз?",
                  size=17, bold=True))
    f.append(line(W / 2, 60, W / 2, H - 30, color="#d0d5db", sw=1.2, dash="7,7"))

    # ── ЛІВОРУЧ: наївно ──
    f.append(text(305, 86, "Наївно: кожен об'єкт носить усе своє", size=14, bold=True, color=POS))
    lx, bw = 70, 470
    for i in range(4):
        by = 112 + i * 122
        f.append(fitbox(lx, by, bw, 52, "вид: сітка · текстура · колір   (~1 МБ)",
                        size=12.5, fill=LIGHT_POS, stroke=POS, sw=1.6, bold=True))
        f.append(fitbox(lx, by + 56, bw, 34, "x, y, scale   (24 Б)",
                        size=11.5, fill=FILL, stroke=LINE, sw=1.2))
    f.append(text(305, H - 44, "важкий вид скопійовано в КОЖНЕ дерево", size=12.5, color=POS))
    f.append(text(305, H - 24, "→ ~1 ТБ, у пам'ять не влазить", size=12.5, bold=True, color=POS))

    # ── ПРАВОРУЧ: легковаговик ──
    f.append(text(895, 86, "Легковаговик: важке — спільне, легке — окреме",
                  size=14, bold=True, color=FIELD))
    # спільні вузли-види (2 показані)
    sbx, sbw = 650, 260
    f.append(text(sbx + sbw / 2, 132, "збережено ОДИН раз на вид", size=11.5, color=FIELD))
    shared = [("ВИД «дуб»\nсітка · текстура · колір", 150),
              ("ВИД «сосна»\nсітка · текстура · колір", 350)]
    scy = []
    for lab, sy in shared:
        f.append(fitbox(sbx, sy, sbw, 82, lab, size=12.5,
                        fill=LIGHT_FIELD, stroke=FIELD, sw=1.9, bold=True))
        scy.append(sy + 41)
    # легкі контексти праворуч, кожен указує на свій вид
    cbx, cbw = 1000, 158
    for cy0, ti in [(114, 0), (218, 0), (352, 1), (456, 1)]:
        f.append(fitbox(cbx, cy0, cbw, 46, "x,y,scale + •", size=11.5,
                        fill=FILL, stroke=NEG, sw=1.4))
        f.append(arrow(cbx, cy0 + 23, sbx + sbw + 5, scy[ti], color=NEG, sw=1.4))
    f.append(text(895, H - 44, "мільйон легких контекстів,", size=12.5, color=FIELD))
    f.append(text(895, H - 24, "кожен лише вказує на спільний вид  →  ~27 МБ",
                  size=12.5, bold=True, color=FIELD))

    render(os.path.join(IMG, 'split.svg'), W, H, *f)


# ── Фігура 2: фабрика — один ключ завжди дає той самий примірник ──────────────
def fig_factory():
    W, H = 1140, 560
    f = []
    f.append(text(W / 2, 32, "Фабрика легковаговиків: один ключ — завжди той самий примірник",
                  size=16, bold=True))

    # клієнт → фабрика → рішення
    f.append(fitbox(50, 218, 175, 62, "клієнт\nдай вид «дуб»",
                    size=12.5, fill=LIGHT_NEG, stroke=NEG, sw=1.6, bold=True))
    f.append(arrow(225, 249, 305, 249, color=LINE))
    f.append(fitbox(305, 214, 205, 70, "factory.get(«дуб»)",
                    size=13, fill=FILL, stroke=INK, sw=1.7, bold=True))
    f.append(arrow(510, 249, 590, 249, color=LINE))
    f.append(fitbox(590, 214, 200, 70, "«дуб» уже\nу мапі?",
                    size=13, fill=LIGHT_GOLD, stroke=GOLD, sw=1.8, bold=True))

    # гілка «так» — угору
    f.append(arrow(690, 214, 690, 160, color=FIELD))
    f.append(text(706, 190, "так", size=12.5, anchor="start", bold=True, color=FIELD))
    f.append(fitbox(560, 104, 320, 56, "повернути наявний примірник",
                    size=12.5, fill=LIGHT_FIELD, stroke=FIELD, sw=1.7, bold=True))

    # гілка «ні» — униз
    f.append(arrow(690, 284, 690, 342, color=POS))
    f.append(text(706, 316, "ні", size=12.5, anchor="start", bold=True, color=POS))
    f.append(fitbox(548, 342, 344, 62, "завантажити вид РАЗ,\nпокласти в мапу",
                    size=12.5, fill=LIGHT_POS, stroke=POS, sw=1.7, bold=True))
    f.append(arrow(720, 404, 720, 452, color=LINE))
    f.append(fitbox(560, 452, 320, 50, "повернути новий примірник",
                    size=12.5, fill=FILL, stroke=LINE, sw=1.4))

    # мапа ліворуч-унизу
    mx, my = 120, 372
    f.append(text(mx + 115, my - 16, "мапа: ключ → примірник", size=12.5, bold=True, color=MUTED))
    for i, r in enumerate(["«дуб»    → ●", "«сосна»  → ●", "«береза» → ●"]):
        f.append(fitbox(mx, my + i * 42, 230, 36, r, size=12.5,
                        fill=FILL, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'factory.svg'), W, H, *f)


# ── Фігура 3: пам'ять на мільйон дерев — наївно проти легковаговика ───────────
def fig_memory():
    W, H = 1000, 560
    f = []
    f.append(text(W / 2, 32, "Пам'ять на мільйон дерев: наївно проти легковаговика",
                  size=16, bold=True))
    base_y = 452
    f.append(line(110, base_y, 900, base_y, color=INK, sw=1.6))

    # наївний стовпчик — упирається у стелю
    nx, bw, ntop = 270, 160, 96
    f.append(rect(nx, ntop, bw, base_y - ntop, fill=LIGHT_POS, stroke=POS, sw=1.7))
    f.append(text(nx + bw / 2, ntop - 16, "≈ 1 000 000 МБ", size=13, bold=True, color=POS))
    f.append(mtext(nx + bw / 2, ntop + (base_y - ntop) / 2 - 8,
                   ["не влазить", "у пам'ять"], size=13.5, bold=True, color=POS))
    f.append(text(nx + bw / 2, base_y + 26, "Наївно  (~1 ТБ)", size=13, bold=True))
    f.append(text(nx + bw / 2, base_y + 46, "1 000 000 × ~1 МБ", size=11.5, color=MUTED))

    # легковаговик — тонкий стовпчик
    fx, ftop = 640, base_y - 28
    f.append(rect(fx, ftop, bw, 28, fill=LIGHT_FIELD, stroke=FIELD, sw=1.7))
    f.append(text(fx + bw / 2, ftop - 14, "≈ 27 МБ", size=13, bold=True, color=FIELD))
    f.append(text(fx + bw / 2, base_y + 26, "Легковаговик", size=13, bold=True))
    f.append(text(fx + bw / 2, base_y + 46, "3 × 1 МБ  +  1 000 000 × 24 Б", size=11.5, color=MUTED))

    f.append(text(W / 2, base_y + 84, "≈ 37 000× менше — сцена нарешті вміщається",
                  size=13.5, bold=True, color=FIELD))

    render(os.path.join(IMG, 'memory.svg'), W, H, *f)


# ── Фігура 4 (hist): дві нитки — InterViews і ET++ — сходяться в каноні GoF ────
def fig_lineage():
    W, H = 1200, 560
    f = []
    f.append(text(W / 2, 32, "Дві нитки сходяться в канон: як гліфи стали Легковаговиком",
                  size=17, bold=True))

    # джерела ліворуч
    f.append(fitbox(60, 95, 320, 108,
                    "1988 · InterViews\nоб'єктний GUI-тулкіт на C++ (Стенфорд)\nЛінтон · Вліссідес · Колдер",
                    size=13, fill=LIGHT_NEG, stroke=NEG, sw=1.7))
    f.append(fitbox(60, 380, 320, 108,
                    "1988 · ET++\nоб'єктний фреймворк на C++ (Цюрих)\nВайнанд · Гамма · Марті",
                    size=13, fill=LIGHT_NEG, stroke=NEG, sw=1.7))
    # віха «гліфи» — золота
    f.append(fitbox(470, 96, 300, 106,
                    "1990 · «Glyphs» — UIST\nслово «flyweight»\nКолдер · Лінтон",
                    size=13.5, fill=LIGHT_GOLD, stroke=GOLD, sw=2.0, bold=True))
    # канон GoF — золотий
    f.append(fitbox(860, 232, 300, 132,
                    "1994 · «Design Patterns» (GoF)\nГамма · Гелм · Джонсон · Вліссідес\nЛегковаговик — 1 з 23 патернів",
                    size=13.5, fill=LIGHT_GOLD, stroke=GOLD, sw=2.0, bold=True))

    # стрілки
    f.append(arrow(380, 150, 466, 150, color=NEG, sw=2.2))      # InterViews → Glyphs
    f.append(arrow(770, 158, 856, 262, color=GOLD, sw=2.2))     # Glyphs → GoF
    f.append(arrow(380, 430, 856, 335, color=MUTED, sw=1.8))    # ET++ → GoF (паралельно)

    f.append(text(605, 452, "паралельна нитка — незалежно", size=12, color=MUTED))
    f.append(text(W / 2, 522,
                  "Двоє з «банди чотирьох»: Вліссідес — з InterViews, Гамма — з ET++.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'lineage.svg'), W, H, *f)


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def polygon(pts, fill, stroke="none", sw=0, opacity=0.16):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return ('<polygon points="%s" fill="%s" fill-opacity="%.2f"%s/>'
            % (p, fill, opacity, st))


# ── Фігура 5 (math): точка беззбитковості — пам'ять як функція K ───────────────
def fig_savings():
    W, H = 1140, 660
    f = []
    f.append(text(W / 2, 34, "Пам'ять легковаговика росте з K і врешті переганяє наївну",
                  size=17, bold=True))

    x0, x1 = 150, 1040       # вісь K
    ytop, ybot = 110, 540    # вісь пам'яті
    yfloor = 494             # підлога N·s_ctx (контексти)
    ynaive = 168             # рівень M_наївно
    # осі
    f.append(line(x0, ytop, x0, ybot, color=INK, sw=1.6))
    f.append(line(x0, ybot, x1, ybot, color=INK, sw=1.6))
    f.append(text(x0 - 12, ytop - 20, "пам'ять", size=12.5, anchor="start", color=MUTED))
    f.append(text(x1, ybot + 44, "K — різних видів  →", size=12.5, anchor="end", color=MUTED))
    f.append(text(x0, ybot + 44, "K=0", size=11.5, anchor="middle", color=MUTED))
    f.append(text(x1 - 8, ybot + 24, "K=N", size=11.5, anchor="middle", color=MUTED))

    # лінія M_наївно (стала)
    f.append(line(x0, ynaive, x1, ynaive, color=POS, sw=2.2))
    # лінія M_легк — росте від підлоги до трохи вище наївної на K=N
    yfwR = 138
    f.append(line(x0, yfloor, x1, yfwR, color=FIELD, sw=2.4))
    # точка перетину K*
    # y = yfloor + (yfwR-yfloor)*(x-x0)/(x1-x0) == ynaive
    xstar = x0 + (ynaive - yfloor) * (x1 - x0) / (yfwR - yfloor)
    # зона виграшу (трикутник між лініями, ліворуч від K*)
    f.append(polygon([(x0, ynaive), (xstar, ynaive), (x0, yfloor)], FIELD, opacity=0.15))
    # зона програшу (вузький трикутник праворуч від K*)
    f.append(polygon([(xstar, ynaive), (x1, ynaive), (x1, yfwR)], POS, opacity=0.18))
    # підлога-пунктир
    f.append(line(x0, yfloor, x1, yfloor, color=MUTED, sw=1.1, dash="5,6"))
    f.append(text(x1, yfloor - 8, "підлога N·s_ctx", size=11, anchor="end", color=MUTED))
    # вертикаль K*
    f.append(line(xstar, ynaive, xstar, ybot, color=INK, sw=1.3, dash="4,5"))
    f.append(text(xstar, ybot + 24, "K*", size=13, bold=True))
    # підписи ліній
    f.append(text(x0 + 120, ynaive - 14, "M_наївно = N·S_full", size=12.5, bold=True,
                  anchor="start", color=POS))
    f.append(fitbox(300, 360, 300, 40, "M_легк = N·s_ctx + K·s_intr",
                    size=12.5, fill="#eef9f1", stroke=FIELD, sw=1.5, bold=True))
    # підписи зон
    f.append(text((x0 + xstar) / 2 - 40, ynaive + 120, "виграш", size=15, bold=True, color=FIELD))
    f.append(text(x1 - 30, ynaive + 66, "програш", size=13, bold=True, color=POS, anchor="end"))
    # точка «ліс»
    f.append(circle(x0 + 8, yfloor - 3, 5.5, fill=LIGHT_FIELD, stroke=FIELD, sw=2))
    f.append(text(x0 + 22, yfloor - 12, "ліс: K=3  (глибоко у виграші)", size=11.5,
                  anchor="start", color=FIELD))

    f.append(text(W / 2, H - 24,
                  "Схематично (s_intr ≫ s_ctx): за важкого виду перетин K* майже при N — виграш майже завжди.",
                  size=12.5, color=MUTED))
    render(os.path.join(IMG, 'savings.svg'), W, H, *f)


# ── Фігура 6 (math): скільки РІЗНИХ значень дає розподіл — рівномірно vs Zipf ──
def fig_distinct():
    W, H = 1140, 640
    f = []
    f.append(text(W / 2, 34, "Скільки різних видів (K) дають N об'єктів — вирішує розподіл значень",
                  size=17, bold=True))

    x0, x1 = 130, 1030
    ytop, ybot = 100, 500
    f.append(line(x0, ytop, x0, ybot, color=INK, sw=1.6))
    f.append(line(x0, ybot, x1, ybot, color=INK, sw=1.6))
    f.append(text(x0 - 12, ytop - 18, "K — різних значень", size=12.5, anchor="start", color=MUTED))
    f.append(text(x1, ybot + 42, "N — об'єктів  →", size=12.5, anchor="end", color=MUTED))

    Wp, Hp = x1 - x0, ybot - ytop
    # діагональ K = N (рівномірно з великого всесвіту)
    diag = [(x0, ybot), (x1, ytop)]
    f.append(line(diag[0][0], diag[0][1], diag[1][0], diag[1][1], color=POS, sw=2.2, dash="7,6"))
    # крива K = c·√N (Zipf / важкий хвіст, β≈0.5) — лишається низько
    import math
    pts = []
    for i in range(0, 61):
        t = i / 60.0
        k = 0.20 * math.sqrt(t)        # нормовано: при N=1 → K=0.20
        pts.append((x0 + t * Wp, ybot - k * Hp))
    f.append(polyline(pts, color=FIELD, sw=3.0))
    # зафарбувати «спільність» — зазор між діагоналлю і кривою
    fillpts = [(x0, ybot)] + pts[::-1] + [(x1, ytop)]
    # спрощено: смуга між кривою і діагоналлю
    band = pts + [(x1, ytop), (x0, ybot)]
    f.append(polygon(band, FIELD, opacity=0.10))

    # підписи ліній
    f.append(fitbox(x0 + 250, ytop + 6, 360, 40,
                    "рівномірно з великого всесвіту:  K ≈ N",
                    size=12.5, fill="#fdeeec", stroke=POS, sw=1.5, bold=True))
    f.append(text(x0 + 300, ytop + 70, "спільності майже нема (σ ≈ 1)", size=11.5,
                  anchor="start", color=POS))
    f.append(fitbox(x0 + 470, ybot - 96, 420, 40,
                    "Zipf / важкий хвіст:  K ≈ c·N^β,  β<1  (закон Гіпса)",
                    size=12.5, fill="#eef9f1", stroke=FIELD, sw=1.5, bold=True))
    f.append(text(x0 + 480, ybot - 40, "K росте повільно → σ = N/K величезне", size=11.5,
                  anchor="start", color=FIELD))
    # callout на кінці кривої
    ex, ey = pts[-1]
    f.append(circle(ex, ey, 5.5, fill=LIGHT_FIELD, stroke=FIELD, sw=2))
    f.append(text(ex - 10, ey - 14, "N=10⁶ → K≈10³", size=11.5, anchor="end", bold=True, color=FIELD))

    f.append(text(W / 2, H - 22,
                  "Що важчий хвіст розподілу, то повільніше росте K — і то більше об'єктів припадає на один спільний вид.",
                  size=12.5, color=MUTED))
    render(os.path.join(IMG, 'distinct.svg'), W, H, *f)


# ── Фігура (proj): куди насправді йде виміряна пам'ять легковаговика ──────────
def fig_realmem():
    W, H = 1000, 620
    f = []
    f.append(text(W / 2, 32, "Куди йде виміряна пам'ять лісу з мільйона дерев",
                  size=16, bold=True))

    bx, bw = 180, 150
    base_y = 540
    right = bx + bw                       # права межа стовпчика
    f.append(line(120, base_y, 980, base_y, color=INK, sw=1.6))
    f.append(text(bx + bw / 2, 78, "абсолютний RSS ≈ 31 МБ", size=13.5, bold=True))

    # сегменти знизу вгору: дерева (24) · сітки (2.9) · фон рантайму (3.5)
    segs = [
        (185, 540, LIGHT_FIELD, FIELD,
         "вектор дерев: 1 000 000 × 24 Б  ≈  24.0 МБ", 362),
        (142, 185, LIGHT_NEG,  NEG,
         "сітки 3 видів  ≈  2.9 МБ", 170),
        (90, 142, LIGHT_GOLD, GOLD,
         "незмінний фон рантайму  ≈  3.5 МБ  (код, libc; не залежить від N)", 110),
    ]
    for top, bot, fill, stroke, lab, laby in segs:
        f.append(rect(bx, top, bw, bot - top, fill=fill, stroke=stroke, sw=1.7))
        f.append(line(right, (top + bot) / 2, 420, laby, color=MUTED, sw=1.0))
        f.append(text(430, laby + 4, lab, size=12.5, anchor="start"))

    # серветкова лінія на межі «живих даних» (дерева+сітки = 26.9 ≈ 27)
    f.append(line(120, 142, 900, 142, color=POS, sw=1.7, dash="7,6"))
    f.append(text(760, 130, "серветка ≈ 27 МБ  =  приріст RSS (after − before)",
                  size=12.5, bold=True, color=POS, anchor="middle"))

    f.append(text(W / 2, base_y + 34,
                  "приріст RSS ≈ серветковому підрахунку; абсолютний RSS вищий рівно на фон рантайму",
                  size=12.5, color=MUTED))
    f.append(text(W / 2, base_y + 56,
                  "рахуючи пам'ять — рахуй буфери на купі, а фон відкидай різницею до/після",
                  size=12.5, bold=True))

    render(os.path.join(IMG, 'realmem.svg'), W, H, *f)


# ── Фігура (proj): перегони в get() і виправлення подвійною перевіркою ────────
def fig_getrace():
    W, H = 1080, 690
    f = []
    f.append(text(W / 2, 30, "get() на двох потоках: перегони — і як їх прибрати",
                  size=16, bold=True))

    # вісь часу
    f.append(text(60, 92, "час", size=12, color=MUTED))
    f.append(arrow(60, 104, 60, 316, color=MUTED, sw=1.4))

    cAx, cBx, cw = 155, 555, 250
    midA, midB = cAx + cw / 2, cBx + cw / 2
    f.append(text(midA, 74, "Потік A", size=13.5, bold=True, color=NEG))
    f.append(text(midB, 74, "Потік B", size=13.5, bold=True, color=NEG))

    rows = [
        (88,  "find(«дуб»)  →  промах", LIGHT_NEG, NEG, False),
        (168, "load(«дуб») — дорого, ДВІЧІ", LIGHT_POS, POS, True),
        (248, "insert у мапу", LIGHT_POS, POS, False),
    ]
    for y, lab, fill, stroke, bold in rows:
        f.append(fitbox(cAx, y, cw, 58, lab, size=13, fill=fill, stroke=stroke, sw=1.6, bold=bold))
        f.append(fitbox(cBx, y, cw, 58, lab, size=13, fill=fill, stroke=stroke, sw=1.6, bold=bold))
    for y in (146, 226):
        f.append(arrow(midA, y, midA, y + 22, color=MUTED, sw=1.3))
        f.append(arrow(midB, y, midB, y + 22, color=MUTED, sw=1.3))

    f.append(fitbox(cAx, 330, cBx + cw - cAx, 56,
                    "вид завантажено ДВІЧІ · конкурентний insert руйнує unordered_map",
                    size=13, fill=LIGHT_POS, stroke=POS, sw=1.7, bold=True))
    f.append(arrow(midA, 306, midA, 330, color=POS, sw=1.4))
    f.append(arrow(midB, 306, midB, 330, color=POS, sw=1.4))

    # роздільник
    f.append(line(60, 412, 1020, 412, color="#c9ced6", sw=1.3, dash="6,6"))
    f.append(text(80, 406, "правильно:", size=13, anchor="start", bold=True, color=FIELD))

    fx, fw = 155, cBx + cw - cAx
    fmid = fx + fw / 2
    f.append(fitbox(fx, 430, fw, 58,
                    "shared_lock  →  find паралельно (багато читачів одночасно)",
                    size=13, fill=LIGHT_FIELD, stroke=FIELD, sw=1.6))
    f.append(arrow(fmid, 488, fmid, 512, color=LINE, sw=1.3))
    f.append(fitbox(fx, 512, fw, 58,
                    "промах  →  unique_lock  +  ПОВТОРНА перевірка (хтось міг уже вставити)",
                    size=13, fill=FILL, stroke=INK, sw=1.6, bold=True))
    f.append(arrow(fmid, 570, fmid, 594, color=LINE, sw=1.3))
    f.append(fitbox(fx, 594, fw, 56,
                    "другий потік бачить уже вставлений вид  →  без дубля, мапа ціла",
                    size=13, fill=LIGHT_FIELD, stroke=FIELD, sw=1.7, bold=True))

    render(os.path.join(IMG, 'getrace.svg'), W, H, *f)


# ── Фігура (proj): життя виду під слабким посиланням і витісненням ────────────
def fig_weaklife():
    W, H = 1220, 470
    f = []
    f.append(text(W / 2, 30, "Життя виду: сильні тримають, слабке спостерігає, витіснення відпускає",
                  size=15.5, bold=True))

    xs = [170, 395, 620, 845, 1070]
    titles = ["1 · перший запит", "2 · багато дерев", "3 · дерева зникають",
              "4 · останнє зникло", "5 · запит знову"]

    # тонкі роздільники між стадіями
    for mx in (282, 507, 732, 957):
        f.append(line(mx, 52, mx, 332, color="#d7dbe1", sw=1.0, dash="4,5"))

    for x, t in zip(xs, titles):
        f.append(text(x, 64, t, size=12.5, bold=True, color=MUTED))

    kw = 190
    # рядок «вид»
    kinds = [
        ("ВИД «дуб-осінь»\n@0xA1", LIGHT_FIELD, FIELD),
        ("ВИД «дуб-осінь»\n@0xA1", LIGHT_FIELD, FIELD),
        ("ВИД «дуб-осінь»\n@0xA1", LIGHT_FIELD, FIELD),
        ("знищено\nсітку звільнено", LIGHT_POS, POS),
        ("ВИД «дуб-осінь»\n@0xF7", LIGHT_FIELD, FIELD),
    ]
    for x, (lab, fill, stroke) in zip(xs, kinds):
        f.append(fitbox(x - kw / 2, 82, kw, 58, lab, size=12, fill=fill, stroke=stroke, sw=1.7, bold=True))

    # рядок лічильника власників
    counts = [("власників: 1", FIELD), ("власників: N", FIELD), ("власників: 2", FIELD),
              ("власників: 0", POS), ("власників: 1", FIELD)]
    for x, (lab, col) in zip(xs, counts):
        f.append(text(x, 168, lab, size=12.5, bold=True, color=col))

    # рядок сильних (дерева)
    strong = [("1 дерево → @0xA1", LIGHT_NEG, NEG), ("N дерев → @0xA1", LIGHT_NEG, NEG),
              ("2 дерева → @0xA1", LIGHT_NEG, NEG), ("0 дерев", LIGHT_POS, POS),
              ("1 дерево → @0xF7", LIGHT_NEG, NEG)]
    for x, (lab, fill, stroke) in zip(xs, strong):
        f.append(fitbox(x - kw / 2, 188, kw, 44, lab, size=11.5, fill=fill, stroke=stroke, sw=1.4))

    # рядок слабкого (мапа фабрики)
    weak = [("мапа: weak → @0xA1", FILL, MUTED), ("мапа: weak → @0xA1", FILL, MUTED),
            ("мапа: weak → @0xA1", FILL, MUTED), ("weak ПРОТУХ → null", LIGHT_GOLD, GOLD),
            ("мапа: weak → @0xF7", FILL, MUTED)]
    for x, (lab, fill, stroke) in zip(xs, weak):
        f.append(fitbox(x - kw / 2, 264, kw, 44, lab, size=11.5, fill=fill, stroke=stroke, sw=1.4))
    f.append(text(xs[2], 328, "слабке посилання НЕ володіє видом", size=11, color=MUTED))

    # злам тотожності: 5 проти 1
    f.append(text(xs[4], 360, "@0xF7 ≠ @0xA1", size=12.5, bold=True, color=POS))
    f.append(text(xs[4], 378, "старий shared_ptr не дорівнює", size=11, color=POS))

    f.append(text(W / 2, 420,
                  "Вид живе, доки його тримає хоч одне дерево; помер — сітку звільнено й weak протух;",
                  size=12.5, color=INK))
    f.append(text(W / 2, 440,
                  "попросили знову — перезавантаження за НОВОЮ адресою, тож порівнювати види треба за КЛЮЧЕМ, не за адресою",
                  size=12.5, bold=True))

    render(os.path.join(IMG, 'weaklife.svg'), W, H, *f)


if __name__ == '__main__':
    fig_split()
    fig_factory()
    fig_memory()
    fig_lineage()
    fig_savings()
    fig_distinct()
    fig_realmem()
    fig_getrace()
    fig_weaklife()
    print("OK: split.svg, factory.svg, memory.svg, lineage.svg, savings.svg, distinct.svg, "
          "realmem.svg, getrace.svg, weaklife.svg")
