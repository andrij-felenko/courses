# -*- coding: utf-8 -*-
"""Фігури до теми «Граф залежностей і порядок робіт»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

DIRTY = "#fdecea"     # червонуватий акцент / гаряче
CLEAN = "#eaf7ef"     # зелений / чинний / готовий
BLUE_FILL = "#eef4ff" # синій акцент
PURPLE_FILL = "#f5f0fa"
MUTED_FILL = "#f8fafc"

def node(cx, cy, label, fill=FILL, stroke=LINE, bold=False, size=14, sw=1.5, min_w=0):
    frag, w, h = textbox(cx, cy, label, size=size, fill=fill, stroke=stroke,
                         bold=bold, sw=sw, min_w=min_w)
    return frag, (cx, cy, w, h)

def connect(a, b, color=LINE, sw=1.8, dash=None):
    """Стрілка між центрами двох рамок із відступами від їхніх меж."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    dx = bx - ax
    dy = by - ay
    import math
    dist = math.hypot(dx, dy)
    if dist < 1e-4:
        return ""
    ux, uy = dx / dist, dy / dist
    
    # Відступ від межі a та b
    sa_x = ax + ux * (aw / 2 + 3)
    sa_y = ay + uy * (ah / 2 + 3)
    sb_x = bx - ux * (bw / 2 + 5)
    sb_y = by - uy * (bh / 2 + 5)
    
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arrow)"%s/>' % (sa_x, sa_y, sb_x, sb_y, color, sw, d))


# ── 1. Анатомія графа збірки: вузли та типи ребер ─────────────────────────────
def fig_dag_anatomy():
    W, H = 960, 520
    parts = []

    # Рівні Y
    y_src = 90
    y_gen = 205
    y_obj = 320
    y_bin = 430

    # Вузли
    sh_in, g_shin = node(140, y_src, "config.h.in", fill=MUTED_FILL, stroke=MUTED, size=13)
    sc_c,  g_scc  = node(370, y_src, "engine.cpp",  fill=CLEAN, stroke=FIELD, size=13)
    sh_h,  g_shh  = node(600, y_src, "engine.h",    fill=CLEAN, stroke=FIELD, size=13)
    sc_m,  g_scm  = node(820, y_src, "main.cpp",    fill=CLEAN, stroke=FIELD, size=13)

    gh_h,  g_ghh  = node(140, y_gen, "config.h\n(згенерований)", fill=BLUE_FILL, stroke=NEG, size=13, bold=True)
    
    ob_e,  g_obe  = node(370, y_obj, "engine.o",    fill=MUTED_FILL, stroke=LINE, size=14, bold=True)
    ob_m,  g_obm  = node(710, y_obj, "main.o",      fill=MUTED_FILL, stroke=LINE, size=14, bold=True)

    bn_a,  g_bna  = node(540, y_bin, "app\n(бінарник)", fill=DIRTY, stroke=POS, size=14, bold=True)
    ph_a,  g_pha  = node(850, y_bin, "all\n(phony)",   fill=PURPLE_FILL, stroke="#7c3aed", size=13, bold=True)

    parts += [sh_in, sc_c, sh_h, sc_m, gh_h, ob_e, ob_m, bn_a, ph_a]

    # Ребра
    # 1. Явні вхідні файли (суцільні товсті)
    parts.append(connect(g_shin, g_ghh, color=NEG, sw=2.0))
    parts.append(connect(g_scc,  g_obe, color=LINE, sw=2.0))
    parts.append(connect(g_scm,  g_obm, color=LINE, sw=2.0))
    parts.append(connect(g_obe,  g_bna, color=POS, sw=2.2))
    parts.append(connect(g_obm,  g_bna, color=POS, sw=2.2))

    # 2. Неявні заголовочні залежності (пунктирні)
    parts.append(connect(g_ghh, g_obe, color=NEG, sw=1.6, dash="5,4"))
    parts.append(connect(g_shh, g_obe, color=FIELD, sw=1.6, dash="5,4"))
    parts.append(connect(g_shh, g_obm, color=FIELD, sw=1.6, dash="5,4"))

    # 3. Phony / агрегація
    parts.append(connect(g_bna, g_pha, color="#7c3aed", sw=1.8, dash="3,3"))

    # Підписи колонок / шарів
    parts.append(text(70, 40, "Джерела (листки DAG)", size=13.5, bold=True, anchor="start", color=MUTED))
    parts.append(text(70, 485, "Легенда:", size=13.5, bold=True, anchor="start"))
    
    # Легенда
    leg_items = [
        (160, 485, "явний вхід", LINE, None),
        (330, 485, "неявний заголовок", FIELD, "5,4"),
        (540, 485, "генерований артефакт", NEG, "5,4"),
        (770, 485, "фіктивна ціль (phony)", "#7c3aed", "3,3"),
    ]
    for lx, ly, ltxt, lcol, ldash in leg_items:
        d = ' stroke-dasharray="%s"' % ldash if ldash else ''
        parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"%s/>' %
                     (lx, ly - 4, lx + 32, ly - 4, lcol, d))
        parts.append(text(lx + 40, ly, ltxt, size=13, anchor="start", color=INK))

    render(os.path.join(IMG, "dag-structure.svg"), W, H, *parts,
           title="Анатомія графа збірки: типи вузлів та характер залежностей")


# ── 2. Алгоритм Кана: черга готових задач і виявлення паралелізму ──────────────
def fig_topological_kahn():
    W, H = 980, 480
    parts = []

    # Ліва частина: граф із лічильниками in-degree
    parts.append(rect(30, 40, 430, 400, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(245, 68, "Граф із лічильниками in-degree", size=15, bold=True))

    na, ga = node(90,  140, "A.c\n[in=0]", fill=CLEAN, stroke=FIELD, bold=True, size=13)
    nb, gb = node(230, 140, "B.c\n[in=0]", fill=CLEAN, stroke=FIELD, bold=True, size=13)
    nc, gc = node(370, 140, "C.h\n[in=0]", fill=CLEAN, stroke=FIELD, bold=True, size=13)

    nd, gd = node(150, 260, "A.o\n[in=2]", fill=MUTED_FILL, stroke=LINE, size=13)
    ne, ge = node(310, 260, "B.o\n[in=2]", fill=MUTED_FILL, stroke=LINE, size=13)

    nf, gf = node(230, 380, "app\n[in=2]", fill=MUTED_FILL, stroke=POS, size=13)

    parts += [na, nb, nc, nd, ne, nf]

    parts.append(connect(ga, gd, color=LINE))
    parts.append(connect(gc, gd, color=FIELD, dash="4,3"))
    parts.append(connect(gb, ge, color=LINE))
    parts.append(connect(gc, ge, color=FIELD, dash="4,3"))
    parts.append(connect(gd, gf, color=LINE))
    parts.append(connect(ge, gf, color=LINE))

    # Права частина: робота планувальника (черга ready queue та пул робітників)
    parts.append(rect(490, 40, 460, 400, fill="#ffffff", stroke=NEG, sw=1.5, rx=8))
    parts.append(text(720, 68, "Диспетчеризація робіт (Worker Pool)", size=15, bold=True, color=NEG))

    # Крок 1: черга in=0
    parts.append(rect(515, 95, 410, 80, fill=CLEAN, stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(530, 120, "1. Черга готових (in-degree == 0):", size=13.5, bold=True, anchor="start", color=FIELD))
    parts.append(fitbox(530, 135, 380, 28, "Готові до запуску: [ A.c,  B.c,  C.h ]", size=13, fill=BG, stroke=FIELD, bold=True))

    # Крок 2: виконання та декремент
    parts.append(rect(515, 195, 410, 115, fill=MUTED_FILL, stroke=MUTED, sw=1.5, rx=6))
    parts.append(text(530, 220, "2. Завершення задачі C.h:", size=13.5, bold=True, anchor="start"))
    parts.append(text(530, 245, "• Зменшуємо in-degree у сусідів:", size=13, anchor="start"))
    parts.append(text(550, 268, "A.o: in=2 → in=1    |    B.o: in=2 → in=1", size=13, bold=True, anchor="start", color=INK))
    parts.append(text(530, 292, "• Жоден сусід ще не досяг in=0 (чекають на .c)", size=12.5, italic=True, anchor="start", color=MUTED))

    # Крок 3: розблокування наступного шару
    parts.append(rect(515, 330, 410, 95, fill=BLUE_FILL, stroke=NEG, sw=1.5, rx=6))
    parts.append(text(530, 355, "3. Завершення A.c та B.c:", size=13.5, bold=True, anchor="start", color=NEG))
    parts.append(text(530, 380, "• A.o: in=1 → in=0  ⟹  додати A.o в Ready Queue", size=13, bold=True, anchor="start"))
    parts.append(text(530, 405, "• B.o: in=1 → in=0  ⟹  додати B.o в Ready Queue", size=13, bold=True, anchor="start"))

    render(os.path.join(IMG, "topological-kahn.svg"), W, H, *parts,
           title="Алгоритм Кана як двигун планувальника паралельної збірки")


# ── 3. Критичний шлях, ширина графа та хвіст збірки ─────────────────────────
def fig_critical_path():
    W, H = 960, 480
    parts = []

    # Верхня панель: Граф із тривалостями
    parts.append(rect(30, 35, 900, 160, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(50, 60, "Граф задач із тривалістю виконання (вага вершин)", size=14, bold=True, anchor="start"))

    t_gen, g_tgen = node(130, 120, "gen_tables.py\n(8 с)", fill=DIRTY, stroke=POS, bold=True, size=12)
    t_c1,  g_tc1  = node(360, 85,  "heavy_parser.cpp\n(16 с)", fill=DIRTY, stroke=POS, bold=True, size=12)
    t_c2,  g_tc2  = node(360, 155, "util_math.cpp\n(3 с)", fill=CLEAN, stroke=FIELD, size=12)
    t_c3,  g_tc3  = node(580, 155, "net_client.cpp\n(4 с)", fill=CLEAN, stroke=FIELD, size=12)
    t_lnk, g_tlnk = node(810, 120, "link app\n(6 с)", fill=DIRTY, stroke=POS, bold=True, size=12)

    parts += [t_gen, t_c1, t_c2, t_c3, t_lnk]

    parts.append(connect(g_tgen, g_tc1, color=POS, sw=2.5))
    parts.append(connect(g_tgen, g_tc2, color=LINE, sw=1.5))
    parts.append(connect(g_tc1,  g_tlnk, color=POS, sw=2.5))
    parts.append(connect(g_tc2,  g_tc3, color=LINE, sw=1.5))
    parts.append(connect(g_tc3,  g_tlnk, color=LINE, sw=1.5))

    parts.append(text(540, 60, "Критичний шлях (Span S = 8 + 16 + 6 = 30 с): виділено червоним",
                      size=13, color=POS, bold=True, anchor="start"))

    # Нижня панель: Порівняння планування на 2 ядрах (FIFO проти Critical Path First)
    parts.append(rect(30, 215, 900, 240, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    parts.append(text(50, 240, "Розклад на 2 воркерах (-j2): наївний FIFO проти пріоритизації глибини", size=14, bold=True, anchor="start"))

    # Варіант 1: Наївний FIFO (погана черга) -> довгий хвіст
    y_f1 = 280
    parts.append(text(50, y_f1 + 18, "FIFO (без ваги):", size=13, bold=True, anchor="start", color=POS))
    # W1
    parts.append(rect(170, y_f1, 80, 24, fill=DIRTY, stroke=POS))
    parts.append(text(210, y_f1 + 16, "gen (8c)", size=11, bold=True, color=POS))
    parts.append(rect(250, y_f1, 40, 24, fill=CLEAN, stroke=FIELD))
    parts.append(text(270, y_f1 + 16, "u (3)", size=10))
    parts.append(rect(290, y_f1, 50, 24, fill=CLEAN, stroke=FIELD))
    parts.append(text(315, y_f1 + 16, "net (4)", size=10))
    # W2 стоїть чекає gen, потім бере heavy
    parts.append(rect(250, y_f1 + 28, 160, 24, fill=DIRTY, stroke=POS))
    parts.append(text(330, y_f1 + 44, "heavy_parser (16 c)", size=11, bold=True, color=POS))
    # Link
    parts.append(rect(410, y_f1 + 28, 70, 24, fill=DIRTY, stroke=POS))
    parts.append(text(445, y_f1 + 44, "link (6 c)", size=11, bold=True, color=POS))
    parts.append(text(500, y_f1 + 35, "Загальний час: 37 с (хвіст через запізнілий старт heavy)", size=12.5, color=POS, bold=True, anchor="start"))

    # Варіант 2: Пріоритет за критичним шляхом
    y_f2 = 365
    parts.append(text(50, y_f2 + 18, "Пріоритет ваги:", size=13, bold=True, anchor="start", color=FIELD))
    # W1
    parts.append(rect(170, y_f2, 80, 24, fill=DIRTY, stroke=POS))
    parts.append(text(210, y_f2 + 16, "gen (8c)", size=11, bold=True, color=POS))
    parts.append(rect(250, y_f2, 160, 24, fill=DIRTY, stroke=POS))
    parts.append(text(330, y_f2 + 16, "heavy_parser (16 c)", size=11, bold=True, color=POS))
    parts.append(rect(410, y_f2, 70, 24, fill=DIRTY, stroke=POS))
    parts.append(text(445, y_f2 + 16, "link (6 c)", size=11, bold=True, color=POS))
    # W2 бере util і net паралельно з heavy
    parts.append(rect(250, y_f2 + 28, 40, 24, fill=CLEAN, stroke=FIELD))
    parts.append(text(270, y_f2 + 44, "u (3)", size=10))
    parts.append(rect(290, y_f2 + 28, 50, 24, fill=CLEAN, stroke=FIELD))
    parts.append(text(315, y_f2 + 44, "net (4)", size=10))
    parts.append(text(500, y_f2 + 25, "Загальний час: 30 с (ідеальне насичення критичного шляху)", size=12.5, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(IMG, "critical-path-span.svg"), W, H, *parts,
           title="Критичний шлях зваженого графа та вплив евристик черги на хвіст збірки")


# ── 4. Динамічне розширення графа через Depfile ──────────────────────────────
def fig_depfile_flow():
    W, H = 940, 460
    parts = []

    # 1. Початковий стан графа
    parts.append(rect(30, 40, 260, 390, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(160, 68, "1. Початковий статичний граф", size=14, bold=True))
    parts.append(text(160, 92, "(до першої компіляції)", size=12.5, color=MUTED, italic=True))

    s1_c, g_s1c = node(160, 160, "engine.cpp", fill=CLEAN, stroke=FIELD, size=13)
    s1_o, g_s1o = node(160, 300, "engine.o", fill=MUTED_FILL, stroke=LINE, size=13, bold=True)
    parts += [s1_c, s1_o]
    parts.append(connect(g_s1c, g_s1o, color=LINE, sw=2))
    parts.append(text(160, 380, "Система знає лише\nпро прямий файл .cpp", size=12.5, color=MUTED))

    # Стрілка переходу
    parts.append(arrow(295, 230, 345, 230, color=NEG, sw=2.5))

    # 2. Крок компіляції з прапорцями -MD -MF
    parts.append(rect(350, 40, 240, 390, fill="#f0f7ff", stroke=NEG, sw=1.5, rx=8))
    parts.append(text(470, 68, "2. Компілятор виявляє #include", size=14, bold=True, color=NEG))
    parts.append(text(470, 92, "cc -MD -MF engine.d ...", size=12.5, color=NEG, bold=True))

    cmd_box = fitbox(365, 125, 210, 80, "Компілятор парсить\nвсі #include під час\nтрансляції коду", size=12, fill=BG, stroke=NEG)
    parts.append(cmd_box)

    df_box = fitbox(365, 240, 210, 120, "Згенеровано engine.d:\nengine.o: \\\n  engine.cpp \\\n  engine.h \\\n  config.h \\\n  /usr/include/math.h", size=11.5, fill=BG, stroke=LINE, bold=False)
    parts.append(df_box)

    # Стрілка переходу
    parts.append(arrow(595, 230, 645, 230, color=NEG, sw=2.5))

    # 3. Мутований граф на наступному кроці
    parts.append(rect(650, 40, 260, 390, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=8))
    parts.append(text(780, 68, "3. Збагачений граф залежностей", size=14, bold=True, color=FIELD))
    parts.append(text(780, 92, "(для наступних інкрементів)", size=12.5, color=FIELD, italic=True))

    s2_c, g_s2c = node(710, 145, "engine.cpp", fill=CLEAN, stroke=FIELD, size=12)
    s2_h, g_s2h = node(850, 145, "engine.h", fill=CLEAN, stroke=FIELD, size=12)
    s2_g, g_s2g = node(780, 225, "config.h", fill=BLUE_FILL, stroke=NEG, size=12)
    s2_o, g_s2o = node(780, 330, "engine.o", fill=DIRTY, stroke=POS, size=13, bold=True)

    parts += [s2_c, s2_h, s2_g, s2_o]
    parts.append(connect(g_s2c, g_s2o, color=LINE, sw=1.8))
    parts.append(connect(g_s2h, g_s2o, color=FIELD, sw=1.8, dash="4,3"))
    parts.append(connect(g_s2g, g_s2o, color=NEG, sw=1.8, dash="4,3"))

    parts.append(text(780, 400, "Тепер зміна config.h\nгарантовано перезбере .o", size=12.5, color=FIELD, bold=True))

    render(os.path.join(IMG, "depfile-dynamic-mutation.svg"), W, H, *parts,
           title="Динамічне збагачення графа залежностей через вивантаження depfile")


def main():
    fig_dag_anatomy()
    fig_topological_kahn()
    fig_critical_path()
    fig_depfile_flow()
    print("Усі 4 фігури успішно згенеровано.")

if __name__ == "__main__":
    main()
