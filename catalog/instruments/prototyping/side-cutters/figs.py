# -*- coding: utf-8 -*-
"""Фігури для статті «Бокорізи» (catalog/instruments/prototyping/side-cutters).
Три фігури:
  (1) anatomy   — будова: губки, ріжучі кромки, вісь-заклепка «навскіс», важелі;
  (2) wedge     — принцип різання: два клини-кромки вдавлюються й розколюють дріт
                  (мідь розколюється; тверда струна викришує саму кромку);
  (3) flush     — flush проти semi-flush: профіль кромки й «защип» на виводі.
Запуск: python figs.py  →  ./img/*.svg
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 4 (для вставки hist): від колючого дроту до заводських кусачок ──────
def fig_history():
    """Смуга подій: різкий попит на дротяні кусачки (колючий дріт, телеграф)
    → ковальський інструмент → масовий заводський (Craftsman 1930).
    Картки стоять РІВНОМІРНО в ряд (не за роком), кожну з'єднує з її роком на осі
    ламана виноска, що обходить підписи десятиліть — тому написи не налазять."""
    W, H = 1000, 430
    frags = []

    x0, x1 = 80, 900          # межі осі років
    axis_y = 360              # вісь унизу, картки над нею в один ряд
    y0, y1 = 1855, 1932       # діапазон років на осі (з полем обабіч)

    def X(year):
        return x0 + (year - y0) / (y1 - y0) * (x1 - x0)

    # горизонтальна вісь років
    frags.append(line(x0 - 12, axis_y, x1 + 24, axis_y, color=INK, sw=2))
    frags.append(arrow(x1 + 10, axis_y, x1 + 30, axis_y, color=INK, sw=2))
    for yr in (1860, 1870, 1880, 1890, 1900, 1910, 1920, 1930):
        xx = X(yr)
        frags.append(line(xx, axis_y - 5, xx, axis_y + 5, color=MUTED, sw=1.4))
        frags.append(text(xx, axis_y + 22, str(yr), size=12, color=MUTED))

    # Події зліва направо; картки РІВНОМІРНО розкладені у верхній смузі,
    # тож текст ніколи не налазить, а справжній рік показує кружок + виноска.
    events = [
        (1857, "1857", "Клайн лагодить бокорізи\nтелеграфісту (Чикаго)", NEG),
        (1874, "1874", "патент Ґліддена\nна колючий дріт", POS),
        (1883, "1883", "техаські «війни за\nогорожі»: дріт ріжуть", POS),
        (1878, "1878", "Кройтер відкриває\nвласну майстерню", FIELD),
        (1916, "1916", "Кройтер: серійні\nбокорізи «Gripkut»", INK),
        (1930, "1930", "Craftsman: діагональні\nкусачки з каталогу", FIELD),
    ]
    events.sort(key=lambda e: e[0])           # за роком, щоб виноски не схрещувались

    n = len(events)
    card_w = 150
    top_y = 70                                # верх ряду карток
    slot0, slot1 = 90, 910                    # де стоятимуть центри карток
    for i, (yr, ylabel, label, col) in enumerate(events):
        cx = slot0 + (slot1 - slot0) * i / (n - 1)
        xx = X(yr)                            # справжня позиція року на осі
        # картка: рік жирним зверху + опис під ним
        by = top_y
        b, bw, bh = textbox(cx, by + 22, label, size=12, min_w=card_w,
                            fill="#ffffff", stroke=col)
        frags.append(text(cx, by - 4, ylabel, size=15, color=col, bold=True))
        frags.append(b)
        card_bottom = by + 22 + bh / 2
        # ламана виноска від низу картки до кружка на осі (обходить підписи років:
        # спускається вертикально до рівня трохи вище осі, тоді косо в точку року)
        elbow_y = axis_y - 46
        frags.append(line(cx, card_bottom + 4, cx, elbow_y, color=col, sw=1.2, dash="4,3"))
        frags.append(line(cx, elbow_y, xx, axis_y - 7, color=col, sw=1.2, dash="4,3"))
        frags.append(circle(xx, axis_y, 6, fill=col, stroke=INK, sw=1.5))

    render(os.path.join(OUT, "history.svg"), W, H, *frags,
           title="Як бокорізи стали стандартним інструментом монтажника")


# ── Фігура 1: будова бокорізів ───────────────────────────────────────────────
def fig_anatomy():
    W, H = 820, 470
    frags = []

    # вісь-заклепка — зсунута трохи ліворуч і вгору, щоб дати місце підписам
    piv = (330, 190)

    # ── дві половинки, кожна = губка + важіль, з'єднані на осі ──
    # Важелі ліворуч від осі, губки праворуч; ріжучі кромки сходяться праворуч.
    # важелі (ручки) ліворуч від осі
    frags.append(line(piv[0], piv[1], 110, piv[1] - 58, color="#8a8a8a", sw=16))   # верхній важіль
    frags.append(line(piv[0], piv[1], 110, piv[1] + 58, color="#8a8a8a", sw=16))   # нижній важіль
    frags.append(text(96, piv[1] - 74, "важелі (ручки)", size=13, color=MUTED, bold=True, anchor="start"))

    # губки праворуч від осі — коротші, сходяться в кромку
    jaw_tip = (500, piv[1])
    frags.append(line(piv[0], piv[1], jaw_tip[0], piv[1] - 30, color="#b7bfcc", sw=20))  # верхня губка
    frags.append(line(piv[0], piv[1], jaw_tip[0], piv[1] + 30, color="#b7bfcc", sw=20))  # нижня губка

    # РІЖУЧІ КРОМКИ — тонка лінія по внутрішньому боку губок, що сходяться
    frags.append(line(piv[0] + 8, piv[1] - 6, jaw_tip[0], piv[1] - 2, color=POS, sw=3))
    frags.append(line(piv[0] + 8, piv[1] + 6, jaw_tip[0], piv[1] + 2, color=POS, sw=3))

    # заклепка-вісь
    frags.append(circle(piv[0], piv[1], 12, fill="#6b7280", stroke="#33404f", sw=2))
    frags.append(circle(piv[0], piv[1], 3.5, fill="#33404f", stroke="#33404f", sw=1))

    # площина кромок «навскіс» до осі — пунктир від кромки крізь заклепку (лише лінія, без напису поруч)
    frags.append(line(jaw_tip[0] + 34, piv[1] - 48, piv[0] - 46, piv[1] + 48,
                      color=NEG, sw=1.6, dash="6,4"))

    # ── підписи розкладені по РІЗНИХ кутах, кожен з великим просвітом ──
    # 1) ріжучі кромки — праворуч угорі
    frags.append(line(jaw_tip[0] - 26, piv[1] - 2, 632, 96, color=MUTED, sw=1, dash="3,3"))
    b_edge, we, he = textbox(700, 84, "ріжучі кромки:\nсходяться в лінію",
                             size=12, fill="#fdecea", stroke=POS, min_w=180)
    frags.append(b_edge)

    # 2) діагональна площина — праворуч нижче, окремо від кромок
    frags.append(line(piv[0] + 46, piv[1] + 46, 640, 300, color=NEG, sw=1, dash="3,3"))
    b_diag, wd, hd = textbox(690, 320,
                             "площина кромок перетинає вісь\nНАВСКІС — звідси назва «діагональні»",
                             size=12, fill="#eaf0fd", stroke=NEG, min_w=250)
    frags.append(b_diag)

    # 3) вісь-заклепка — прямо вниз
    frags.append(line(piv[0], piv[1] + 12, piv[0], piv[1] + 96, color=MUTED, sw=1, dash="3,3"))
    b_piv, wp, hp = textbox(piv[0], piv[1] + 118, "вісь-заклепка (важіль)",
                            size=12, fill="#f4f6f8", stroke=LINE, min_w=180)
    frags.append(b_piv)

    render(os.path.join(OUT, "anatomy.svg"), W, H, *frags,
           title="Будова бокорізів: важіль складається двічі — на осі й на кромці")


# ── Фігура 2: принцип різання — два клини розколюють дріт ─────────────────────
def fig_wedge():
    W, H = 780, 430
    frags = []

    # ЛІВА сцена: м'яка мідь — клини сходяться, метал тече, дріт розколюється
    cxL = 210
    _wedge_scene(frags, cxL, 150,
                 wire_fill="#d98a3a", wire_stroke="#a5661f",
                 edge_color=POS, split=True)
    b1 = fitbox(cxL - 150, 300, 300, 58,
                "м'яка мідь: кромки-клини вдавлюються,\nметал «тече» вбік і жила розколюється навпіл",
                size=12, fill="#fbeede", stroke="#a5661f")
    frags.append(b1)
    frags.append(text(cxL, 60, "мідний вивід (м'який)", size=13, color="#a5661f", bold=True))

    # ПРАВА сцена: тверда струна — клин не входить, викришується сама кромка
    cxR = 570
    _wedge_scene(frags, cxR, 150,
                 wire_fill="#9aa3b0", wire_stroke="#5b6472",
                 edge_color=NEG, split=False, chip=True)
    b2 = fitbox(cxR - 150, 300, 300, 58,
                "загартована струна (тверда): клин не входить —\nвикришується сама кромка, інструмент зіпсовано",
                size=12, fill="#eef1f6", stroke="#5b6472")
    frags.append(b2)
    frags.append(text(cxR, 60, "сталева струна (твердіша за кромку)", size=13, color="#5b6472", bold=True))

    # роздільник
    frags.append(line(390, 90, 390, 288, color="#d0d5dd", sw=1.4, dash="4,4"))

    render(os.path.join(OUT, "wedge.svg"), W, H, *frags,
           title="Бокорізи не ріжуть, а РОЗКОЛЮЮТЬ клином — тому й бояться твердого")


def _wedge_scene(frags, cx, cy, wire_fill, wire_stroke, edge_color, split=False, chip=False):
    """Дві губки-клини зверху й знизу, між ними — жила дроту в перерізі."""
    half = 20            # піврозхил губок
    jaw_w = 120
    wire_r = 22

    # верхня губка (клин, вістрям униз)
    ytop = cy - half - 4
    frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                 'fill="#c8d0dc" stroke="#5b6a82" stroke-width="2"/>'
                 % (cx - jaw_w / 2, ytop - 46, cx + jaw_w / 2, ytop - 46, cx, ytop))
    # нижня губка (клин, вістрям угору)
    ybot = cy + half + 4
    frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                 'fill="#c8d0dc" stroke="#5b6a82" stroke-width="2"/>'
                 % (cx - jaw_w / 2, ybot + 46, cx + jaw_w / 2, ybot + 46, cx, ybot))
    # підсвітити самі кромки-вістря
    frags.append(line(cx - 14, ytop - 3, cx + 14, ytop - 3, color=edge_color, sw=3))
    frags.append(line(cx - 14, ybot + 3, cx + 14, ybot + 3, color=edge_color, sw=3))

    # стрілки тиску губок назустріч
    frags.append(arrow(cx + jaw_w / 2 + 8, ytop - 30, cx + jaw_w / 2 + 8, ytop - 8, color=MUTED))
    frags.append(arrow(cx + jaw_w / 2 + 8, ybot + 30, cx + jaw_w / 2 + 8, ybot + 8, color=MUTED))

    if split:
        # жила розколота: дві половинки розійшлися вбік із «потоком» металу
        frags.append(circle(cx - 8, cy, wire_r, fill=wire_fill, stroke=wire_stroke, sw=2))
        frags.append(circle(cx + 8, cy, wire_r, fill=wire_fill, stroke=wire_stroke, sw=2))
        # вм'ятини-клини зверху й знизу (світлий трикутник у місці входу)
        frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                     'fill="#ffffff" stroke="none" opacity="0.55"/>'
                     % (cx - 10, cy - wire_r, cx + 10, cy - wire_r, cx, cy - 4))
        frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                     'fill="#ffffff" stroke="none" opacity="0.55"/>'
                     % (cx - 10, cy + wire_r, cx + 10, cy + wire_r, cx, cy + 4))
    else:
        # цілий круглий дріт (клин не пройшов)
        frags.append(circle(cx, cy, wire_r, fill=wire_fill, stroke=wire_stroke, sw=2))
        if chip:
            # викришена кромка нижньої губки — вирваний шматочок
            frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                         'fill="#ffffff" stroke="%s" stroke-width="1.6"/>'
                         % (cx - 6, ybot + 3, cx + 8, ybot + 3, cx + 1, ybot + 18, edge_color))
            frags.append(text(cx + 44, ybot + 20, "щербина", size=11, color=edge_color, bold=True))
            frags.append(line(cx + 6, ybot + 12, cx + 30, ybot + 18, color=edge_color, sw=1, dash="3,3"))


# ── Фігура 3: flush проти semi-flush ─────────────────────────────────────────
def fig_flush():
    W, H = 760, 400
    frags = []

    # ЛІВА: semi-flush — фаска з обох боків, лишає «защип»
    cxL = 200
    _edge_profile(frags, cxL, 130, bevel_both=True)
    frags.append(text(cxL, 62, "semi-flush (напівврівень)", size=13, color=INK, bold=True))
    # результат — вивід із защипом
    _lead_result(frags, cxL, 250, pinch=True)
    frags.append(text(cxL, 344, "лишає «защип» — гострий вусик", size=12, color=POS, bold=True))

    # ПРАВА: flush — фаска лише з одного боку, пласка стінка до плати
    cxR = 560
    _edge_profile(frags, cxR, 130, bevel_both=False)
    frags.append(text(cxR, 62, "flush (врівень)", size=13, color=INK, bold=True))
    _lead_result(frags, cxR, 250, pinch=False)
    frags.append(text(cxR, 344, "зріз майже гладкий, без вусика", size=12, color=FIELD, bold=True))

    frags.append(line(380, 80, 380, 320, color="#d0d5dd", sw=1.4, dash="4,4"))

    render(os.path.join(OUT, "flush.svg"), W, H, *frags,
           title="Flush проти semi-flush: пласка стінка кромки лишає гладкий зріз")


def _edge_profile(frags, cx, cy, bevel_both):
    """Переріз однієї кромки: клин, приставлений до дроту. bevel_both — фаски з двох боків."""
    r = 26
    # дріт у перерізі
    frags.append(circle(cx, cy, r, fill="#d98a3a", stroke="#a5661f", sw=2))
    # кромка-клин приставлена ЗВЕРХУ до дроту
    tipx = cx
    if bevel_both:
        # симетричний клин (фаски з обох боків) — вістря по центру
        frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                     'fill="#c8d0dc" stroke="#5b6a82" stroke-width="2"/>'
                     % (tipx - 34, cy - r - 44, tipx + 34, cy - r - 44, tipx, cy - r + 3))
        frags.append(text(cx, cy - r - 54, "фаска з обох боків", size=11, color=MUTED))
    else:
        # клин із пласкою вертикальною стінкою праворуч (flush-бік)
        frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                     'fill="#c8d0dc" stroke="#5b6a82" stroke-width="2"/>'
                     % (tipx - 34, cy - r - 44, tipx, cy - r - 44, tipx, cy - r + 3))
        # пласка стінка
        frags.append(line(tipx, cy - r - 44, tipx, cy - r + 3, color=FIELD, sw=3))
        frags.append(text(cx + 30, cy - r - 20, "пласка", size=11, color=FIELD, bold=True))
        frags.append(text(cx + 30, cy - r - 6, "стінка", size=11, color=FIELD, bold=True))


def _lead_result(frags, cx, cy, pinch):
    """Вивід деталі, зрізаний біля плати: з защипом або гладко."""
    # плата
    frags.append(rect(cx - 90, cy + 26, 180, 16, fill="#2e7d32", stroke="#1b5e20", sw=1.5, rx=3))
    frags.append(text(cx, cy + 60, "плата", size=11, color=MUTED))
    # вивід — вертикальний стовпчик від плати вгору
    frags.append(line(cx, cy + 26, cx, cy - 18, color="#9aa3b0", sw=7))
    if pinch:
        # гострий вусик-защип на вершині
        frags.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
                     'fill="#c0392b" stroke="#a5661f" stroke-width="1"/>'
                     % (cx - 3, cy - 18, cx + 3, cy - 18, cx + 7, cy - 32))
    else:
        # рівний зріз
        frags.append(line(cx - 4, cy - 18, cx + 4, cy - 18, color=FIELD, sw=3))


if __name__ == "__main__":
    fig_anatomy()
    fig_wedge()
    fig_flush()
    fig_history()
    print("done:", os.listdir(OUT))
