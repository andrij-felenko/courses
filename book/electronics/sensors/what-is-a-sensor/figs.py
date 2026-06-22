# -*- coding: utf-8 -*-
"""Фігури до теми «Що таке давач».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Давач як перекладач: фізична величина → електричний сигнал ─────────────
def fig_translator():
    W, H = 680, 320
    f = []
    # центральна рамка «ДАВАЧ»
    f.append(rect(268, 92, 150, 152, fill="#eef6ef", stroke=FIELD, sw=2, rx=10))
    f.append(text(343, 162, "ДАВАЧ", size=19, color=FIELD, bold=True))
    f.append(text(343, 186, "перетворювач", size=12, italic=True))
    # лівий бік — фізичний світ
    f.append(text(118, 78, "ФІЗИЧНИЙ СВІТ", size=12, color=MUTED, bold=True))
    rows = [("температура", "ефект Зеебека", 122),
            ("світло", "фотоефект", 158),
            ("сила / тиск", "п'єзоефект", 194),
            ("відстань", "час відлуння", 230)]
    for name, eff, y in rows:
        f.append(text(52, y, name, size=13, anchor="start", bold=True))
        f.append(text(52, y + 15, eff, size=10, color=MUTED, anchor="start", italic=True))
        f.append(arrow(206, y - 4, 262, y - 4, color=INK, sw=2))
    # правий бік — електрика
    f.append(text(585, 78, "ЕЛЕКТРИКА", size=12, color=MUTED, bold=True))
    f.append(arrow(424, 168, 558, 168, color=FIELD, sw=2.5))
    # маленька синусоїда на виході
    import math
    pts = []
    for i in range(49):
        x = 470 + i * 1.8
        y = 134 - 12 * math.sin(i / 49.0 * 4 * math.pi)
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(pts), FIELD))
    f.append(text(588, 166, "напруга", size=14, color=FIELD, bold=True))
    f.append(text(588, 186, "→ число", size=11, italic=True))
    render(os.path.join(IMG, "translator.svg"), W, H, *f,
           title="Давач — перекладач: фізична величина → електричний сигнал")


# ── 2. Вимірювальний ланцюг: від величини до числа (без нумерації) ────────────
def fig_chain():
    W, H = 720, 210
    f = []
    boxes = [("величина", "T, світло…", MUTED),
             ("чутл. елемент", "давач", FIELD),
             ("нормування", "підсилювач", NEG),
             ("АЦП", "напруга → код", POS),
             ("число в МК", "зміст", INK)]
    x, y, bw, bh, gap = 30, 70, 116, 72, 20
    for i, (top, sub, col) in enumerate(boxes):
        bx = x + i * (bw + gap)
        f.append(rect(bx, y, bw, bh, fill=BG, stroke=col, sw=2, rx=8))
        f.append(text(bx + bw / 2, y + 30, top, size=12, bold=True))
        f.append(text(bx + bw / 2, y + 50, sub, size=10, color=col, italic=True))
        if i:
            f.append(arrow(bx - gap + 1, y + bh / 2, bx - 2, y + bh / 2, color=INK, sw=2))
    f.append(text(W / 2, 172, "сирий мкВ-сигнал → підсилений → відфільтрований → оцифрований → зміст",
                  size=12.5, italic=True))
    render(os.path.join(IMG, "chain.svg"), W, H, *f,
           title="Вимірювальний ланцюг: від величини до числа")


# ── 3. Дві сім'ї давачів ──────────────────────────────────────────────────────
def fig_families():
    W, H = 700, 320
    f = []
    # ліва панель — самогенерувальний
    f.append(rect(30, 50, 310, 246, fill="#fff0e2", stroke=POS, sw=1.6, rx=10))
    f.append(text(185, 74, "САМОГЕНЕРУВАЛЬНИЙ", size=13.5, color=POS, bold=True))
    f.append(text(185, 92, "сам джерело ЕРС — живлення не треба", size=11, italic=True))
    f.append(text(70, 138, "тепло/світло", size=10.5, color="#e8702a"))
    f.append(arrow(70, 150, 120, 150, color="#e8702a", sw=2.4))
    f.append(circle(150, 150, 22, fill=BG, stroke=INK, sw=2))
    f.append(text(150, 145, "+", size=15, color=POS, bold=True))
    f.append(line(143, 160, 157, 160, color=NEG, sw=2.4))
    f.append(line(150, 172, 150, 210, color=INK, sw=2))
    f.append(line(172, 150, 250, 150, color=INK, sw=2))
    f.append(line(250, 150, 250, 210, color=INK, sw=2))
    f.append(line(150, 210, 224, 210, color=INK, sw=2))
    f.append(circle(250, 210, 20, fill=BG, stroke=INK, sw=2))
    f.append(text(250, 216, "V", size=16, color=FIELD, bold=True))
    f.append(text(150, 250, "термопара · фотодіод · п'єзо", size=11, bold=True))
    f.append(text(185, 282, "сигнал малий, але автономний", size=11, color=MUTED, italic=True))
    # права панель — параметричний
    f.append(rect(360, 50, 310, 246, fill="#e8f1fb", stroke=NEG, sw=1.6, rx=10))
    f.append(text(515, 74, "ПАРАМЕТРИЧНИЙ", size=13.5, color=NEG, bold=True))
    f.append(text(515, 92, "змінний R/C/L — його треба живити", size=11, italic=True))
    f.append(circle(412, 187, 18, fill=BG, stroke=INK, sw=2))
    f.append(text(412, 182, "+", size=15, color=POS, bold=True))
    f.append(line(405, 195, 419, 195, color=NEG, sw=2.4))
    f.append(text(412, 158, "V_оп", size=11, bold=True))
    f.append(line(412, 169, 412, 118, color=INK, sw=2))
    f.append(line(412, 118, 560, 118, color=INK, sw=2))
    f.append(line(412, 205, 412, 256, color=INK, sw=2))
    f.append(line(412, 256, 560, 256, color=INK, sw=2))
    # верхній фіксований резистор (зигзаг)
    f.append('<polyline points="560,118 552,122.2 568,130.5 552,138.8 568,147.2 552,155.5 568,163.8 560,168" '
             'fill="none" stroke="%s" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>' % INK)
    f.append(text(576, 146, "R", size=12, anchor="start", bold=True))
    f.append(circle(560, 176, 4, fill=INK, stroke=INK, sw=1))
    f.append(line(560, 168, 560, 184, color=INK, sw=2))
    f.append(line(560, 176, 632, 176, color=FIELD, sw=2))
    f.append(text(636, 180, "→ АЦП", size=11, color=FIELD, anchor="start", bold=True))
    # нижній змінний резистор (зигзаг)
    f.append('<polyline points="560,184 552,188.2 568,196.5 552,204.8 568,213.2 552,221.5 568,229.8 560,234" '
             'fill="none" stroke="%s" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>' % FIELD)
    f.append(line(560, 234, 560, 256, color=INK, sw=2))
    f.append(arrow(600, 210, 572, 208, color=FIELD, sw=1.8))
    f.append(text(604, 214, "R(вимір.)", size=10.5, color=FIELD, anchor="start", bold=True))
    f.append(text(515, 282, "терморезистор · фоторезистор · ємнісний", size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "families.svg"), W, H, *f,
           title="Дві сім'ї давачів за джерелом енергії сигналу")


# ── 4. Оборотність: давач ↔ виконавчий пристрій ───────────────────────────────
def fig_duality():
    W, H = 680, 300
    PUR = "#6a4ea8"
    f = []
    f.append(rect(285, 78, 110, 80, fill="#f2f0fb", stroke=PUR, sw=2, rx=8))
    f.append(text(340, 112, "перетво-", size=12.5, color=PUR, bold=True))
    f.append(text(340, 130, "рювач", size=12.5, color=PUR, bold=True))
    f.append(text(120, 98, "ФІЗИЧНЕ", size=12.5, color=MUTED, bold=True))
    f.append(text(560, 98, "ЕЛЕКТРИЧНЕ", size=12.5, color=MUTED, bold=True))
    # давач: фізичне → електричне (зелені стрілки)
    f.append(text(340, 72, "давач:  фізичне → електричне", size=12, color=FIELD, bold=True))
    f.append(arrow(150, 118, 279, 118, color=FIELD, sw=2.4))
    f.append(arrow(401, 118, 540, 118, color=FIELD, sw=2.4))
    # виконавчий пристрій: електричне → фізичне (червоні стрілки)
    f.append(text(340, 196, "та сама фізика — два застосування:", size=12, italic=True))
    f.append(arrow(540, 194, 401, 194, color=POS, sw=2.4))
    f.append(arrow(279, 194, 150, 194, color=POS, sw=2.4))
    f.append(text(340, 216, "виконавчий пристрій:  електричне → фізичне", size=12, color=POS, bold=True))
    # пари
    pairs = [(147, "динамік", "мікрофон"), (287, "мотор", "генератор"),
             (427, "п'єзо-пищалка", "давач удару"), (567, "Пельтьє", "термопара")]
    for cx, a, b in pairs:
        f.append(rect(cx - 65, 230, 130, 36, fill="#fafafa", stroke=MUTED, sw=1, rx=6))
        f.append(text(cx, 247, a, size=11, color=POS, bold=True))
        f.append(text(cx, 261, b, size=11, color=FIELD, bold=True))
    render(os.path.join(IMG, "duality.svg"), W, H, *f,
           title="Перетворювач читається у два боки: давач ↔ виконавчий пристрій")


# ── 5. Форми вихідного сигналу ────────────────────────────────────────────────
def fig_output_forms():
    W, H = 700, 350
    PUR = "#6a4ea8"
    f = []
    rows = [("напруга", "просто на АЦП; боїться завад і падіння на дротах", 64),
            ("струм 4–20 мА", "однаковий уздовж кола → стійкий на відстані", 118),
            ("зміна R / C", "потребує дільника чи моста, далі АЦП", 172),
            ("частота / період", "рахує таймер — точно, без аналогу", 226),
            ("цифрове число", "давач уже містить АЦП; читаємо готове", 280)]
    for name, desc, y in rows:
        f.append(rect(28, y, 644, 46, fill="#fbfbfb", stroke="#e4e4e4", sw=1, rx=6))
        f.append(text(46, y + 28, name, size=13, anchor="start", bold=True))
        f.append(text(326, y + 28, desc, size=11.5, anchor="start"))
    # піктограми по центру кожного рядка (210..300)
    f.append(line(210, 97, 300, 77, color=FIELD, sw=2.2))                       # напруга — нахил
    f.append(rect(210, 132, 90, 22, fill="none", stroke=POS, sw=1.6, rx=4))     # струм — петля
    f.append(arrow(218, 143, 288, 143, color=POS, sw=1.8))
    f.append('<polyline points="210,196 217.5,188 232.5,204 247.5,188 262.5,204 277.5,188 292.5,204 300,196" '
             'fill="none" stroke="%s" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>' % INK)  # R/C — пила
    f.append('<polyline points="210,262 210,240 225,240 225,262 240,262 240,240 255,240 255,262 270,262 '
             '270,240 285,240 285,262 300,262" fill="none" stroke="%s" stroke-width="2" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % NEG)          # частота — меандр
    f.append(text(255, 310, "0 1 0 1 1 0", size=14, color=PUR, bold=True))      # цифра — біти
    render(os.path.join(IMG, "output-forms.svg"), W, H, *f,
           title="Форми вихідного сигналу давача — і чим читати кожну")


# ── 6. Кожна ланка щось спотворює (джерела похибок; без нумерації) ─────────────
def fig_imperfect_chain():
    W, H = 720, 250
    f = []
    boxes = [("величина", "істина", MUTED),
             ("чутл. елемент", "давач", FIELD),
             ("підсилювач", "тракт", NEG),
             ("АЦП", "крок", POS),
             ("число", "оцінка", INK)]
    x, y, bw, bh, gap = 30, 96, 116, 72, 20
    cx_list = []
    for i, (top, sub, col) in enumerate(boxes):
        bx = x + i * (bw + gap)
        cx_list.append(bx + bw / 2)
        f.append(rect(bx, y, bw, bh, fill=BG, stroke=col, sw=2, rx=8))
        f.append(text(bx + bw / 2, y + 30, top, size=12, bold=True))
        f.append(text(bx + bw / 2, y + 50, sub, size=10, color=col, italic=True))
        if i:
            f.append(arrow(bx - gap + 1, y + bh / 2, bx - 2, y + bh / 2, color=INK, sw=2))
    # підписи похибок над ланками (без номерів)
    errs = [(cx_list[1], "нелінійність / дрейф / шум"),
            (cx_list[2], "зсув, смуга"),
            (cx_list[3], "квантування")]
    for cx, lbl in errs:
        f.append(text(cx, 62, lbl, size=10.5, color=POS, bold=True))
        f.append(arrow(cx, 70, cx, y - 4, color=POS, sw=1.8))
    f.append(text(W / 2, 214, "давач дає не істину, а підказку — її треба грамотно витлумачити",
                  size=13, italic=True))
    render(os.path.join(IMG, "imperfect-chain.svg"), W, H, *f,
           title="Кожна ланка щось спотворює")


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Фігури до історичної вставки 📜 hist-seebeck.md                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝

HOT  = "#e8702a"   # полум'я/нагрів
BRONZE = "#b07a32"  # метал A
STEEL  = "#6f7e8c"  # метал B


def _flame(f, cx, cy):
    """Маленьке полум'я (дві накладені «краплі») із центром-вершиною (cx,cy)."""
    f.append('<path d="M %.1f,%.1f C %.1f,%.1f %.1f,%.1f %.1f,%.1f '
             'C %.1f,%.1f %.1f,%.1f %.1f,%.1f Z" fill="%s"/>'
             % (cx, cy + 26, cx - 11, cy + 16, cx - 7, cy - 9, cx, cy - 20,
                cx + 7, cy - 9, cx + 11, cy + 16, cx, cy + 26, HOT))
    f.append('<path d="M %.1f,%.1f C %.1f,%.1f %.1f,%.1f %.1f,%.1f '
             'C %.1f,%.1f %.1f,%.1f %.1f,%.1f Z" fill="#f6c84a"/>'
             % (cx, cy + 21, cx - 6, cy + 13, cx - 4, cy - 2, cx, cy - 11,
                cx + 4, cy - 2, cx + 6, cy + 13, cx, cy + 21))


def _compass(f, cx, cy, r=44):
    """Компас із відхиленою стрілкою (червоний/синій кінці)."""
    f.append(circle(cx, cy, r, fill=BG, stroke=INK, sw=2))
    f.append(circle(cx, cy, r + 5, fill="none", stroke=MUTED, sw=1))
    import math
    for k in range(8):
        a = k * math.pi / 4
        f.append(line(cx + (r - 6) * math.cos(a), cy + (r - 6) * math.sin(a),
                      cx + r * math.cos(a), cy + r * math.sin(a), color=MUTED, sw=1))
    ang = math.radians(-58)
    nx, ny = cx + (r - 8) * math.cos(ang), cy + (r - 8) * math.sin(ang)
    sx, sy = cx - (r - 8) * math.cos(ang), cy - (r - 8) * math.sin(ang)
    px, py = cx + 11 * math.cos(ang + math.pi / 2), cy + 11 * math.sin(ang + math.pi / 2)
    f.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="%s"/>'
             % (nx, ny, px, py, cx, cy, POS))
    f.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="%s"/>'
             % (sx, sy, px, py, cx, cy, NEG))
    f.append(circle(cx, cy, 3, fill=INK, stroke=INK, sw=1))


# ── 7. Дослід 1821: петля з двох металів і компас ─────────────────────────────
def fig_seebeck_loop():
    W, H = 680, 374
    f = []
    # замкнена петля: верхня гілка — метал A, нижня — метал B
    f.append('<polyline points="185,130 185,92 495,92 495,130" fill="none" '
             'stroke="%s" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>' % BRONZE)
    f.append('<polyline points="185,130 185,168 495,168 495,130" fill="none" '
             'stroke="%s" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>' % STEEL)
    f.append(text(340, 82, "метал A  (сурма, Sb)", size=13, color=BRONZE, bold=True))
    f.append(text(340, 190, "метал B  (вісмут, Bi)", size=13, color=STEEL, bold=True))
    f.append(circle(185, 130, 7, fill=INK, stroke=INK, sw=1))
    f.append(circle(495, 130, 7, fill=INK, stroke=INK, sw=1))
    # нагрів лівого спаю
    _flame(f, 185, 150)
    f.append(text(185, 206, "нагрів", size=12, color=HOT, bold=True))
    f.append(text(175, 116, "гарячий спай  T₁", size=12, color=POS, anchor="end", bold=True))
    f.append(text(505, 116, "холодний спай  T₂", size=12, color=NEG, anchor="start", bold=True))
    # термострум по петлі
    f.append(arrow(372, 92, 308, 92, color=FIELD, sw=2.4))
    f.append(arrow(308, 168, 372, 168, color=FIELD, sw=2.4))
    f.append(text(340, 70, "термострум  I", size=12.5, color=FIELD, italic=True))
    # пунктир до компаса
    f.append(line(340, 96, 340, 250, color=MUTED, sw=1.4, dash="3,4"))
    _compass(f, 340, 300)
    f.append(text(340, 360, "стрілка відхиляється", size=12.5, italic=True))
    # пояснювальна рамка
    box = ("Що бачив Зеебек:\n"
           "стрілка хитнулась —\n"
           "він вирішив, що це\n"
           "магнетизм. Насправді\n"
           "ΔT жене струм, а той\n"
           "хитає стрілку\n"
           "(Ерстед, 1820).")
    f.append(fitbox(508, 250, 162, 116, box, size=11, pad=9,
                    fill="#fbfbf6", stroke=MUTED, sw=1.2, color=INK))
    render(os.path.join(IMG, "seebeck-loop.svg"), W, H, *f,
           title="Дослід 1821 року: петля з двох металів і компас")


# ── 8. Чому ΔT робить напругу: дифузія носіїв ─────────────────────────────────
def fig_seebeck_diffusion():
    import math
    W, H = 680, 360
    f = []
    # провідник: ліва половина «гаряча», права «холодна»
    f.append(rect(120, 110, 210, 78, fill="#fff0e2", stroke="none", sw=0))
    f.append(rect(330, 110, 210, 78, fill="#e8f1fb", stroke="none", sw=0))
    f.append(rect(120, 110, 420, 78, fill="none", stroke=INK, sw=2, rx=0))
    f.append(text(170, 100, "гарячий кінець (T↑)", size=12.5, color=POS, bold=True))
    f.append(text(490, 100, "холодний кінець (T↓)", size=12.5, color=NEG, bold=True))
    # носії, що дрейфують уліво→вправо (на гарячому боці зі стрілками)
    drift = [(155, 135), (180, 165), (215, 145), (255, 159), (300, 137)]
    for x, y in drift:
        f.append(arrow(x, y, x + 30, y - 2, color=INK, sw=1.6))
        f.append(circle(x, y, 7, fill="#dfe7f7", stroke=NEG, sw=1.5))
        f.append(line(x - 3.5, y, x + 3.5, y, color=NEG, sw=1.8))
    # скупчення на холодному кінці
    for x, y in [(510, 133), (510, 151), (510, 167), (488, 141), (488, 161), (526, 149)]:
        f.append(circle(x, y, 7, fill="#dfe7f7", stroke=NEG, sw=1.5))
        f.append(line(x - 3.5, y, x + 3.5, y, color=NEG, sw=1.8))
    f.append(text(136, 156, "+", size=26, color=POS, bold=True))
    f.append(text(532, 156, "−", size=26, color=NEG, bold=True))
    # виводи до вольтметра
    f.append(line(120, 188, 120, 250, color=INK, sw=2))
    f.append(line(540, 188, 540, 250, color=INK, sw=2))
    f.append(line(120, 250, 304, 250, color=INK, sw=2))
    f.append(line(540, 250, 356, 250, color=INK, sw=2))
    f.append(circle(330, 250, 26, fill=BG, stroke=INK, sw=2))
    f.append(text(330, 256, "V", size=17, color=FIELD, bold=True))
    f.append(text(330, 312, "ΔV = S · ΔT   (S — коефіцієнт Зеебека, мкВ/°C)",
                  size=15, color=FIELD, bold=True))
    f.append(text(330, 336, "гарячі носії енергійніші → дифундують до холодного → там надлишок (−), тут нестача (+)",
                  size=11.5, italic=True))
    render(os.path.join(IMG, "seebeck-diffusion.svg"), W, H, *f,
           title="Чому різниця температур робить напругу: дифузія носіїв")


# ── 9. Три термоелектричні ефекти — одне сімейство ────────────────────────────
def fig_three_effects():
    W, H = 720, 320
    f = []
    # Зеебек
    f.append(rect(27, 56, 210, 168, fill="#fff0e2", stroke=POS, sw=1.6, rx=8))
    f.append(text(132, 80, "Зеебек · 1821", size=14, color=POS, bold=True))
    f.append(text(132, 100, "тепло → напруга", size=12.5, italic=True))
    f.append('<polyline points="98,170 132,148 166,170" fill="none" stroke="%s" '
             'stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>' % BRONZE)
    f.append('<polyline points="132,148 166,170" fill="none" stroke="%s" '
             'stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>' % STEEL)
    f.append(circle(132, 148, 5, fill=INK, stroke=INK, sw=1))
    _flame(f, 132, 176)
    f.append(arrow(57, 154, 92, 154, color=POS, sw=2))
    f.append(text(45, 142, "ΔT", size=13, color=POS, bold=True))
    f.append(circle(203, 154, 16, fill=BG, stroke=INK, sw=1.6))
    f.append(text(203, 159, "V", size=13, color=FIELD, bold=True))
    f.append(arrow(172, 154, 185, 154, color=FIELD, sw=2))
    f.append(text(132, 214, "термопара", size=11.5, color=MUTED, italic=True))
    # Пельтьє
    f.append(rect(255, 56, 210, 168, fill="#e8f1fb", stroke=NEG, sw=1.6, rx=8))
    f.append(text(360, 80, "Пельтьє · 1834", size=14, color=NEG, bold=True))
    f.append(text(360, 100, "струм → тепло/холод", size=12.5, italic=True))
    f.append('<polyline points="326,178 360,156 394,178" fill="none" stroke="%s" '
             'stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>' % BRONZE)
    f.append('<polyline points="360,156 394,178" fill="none" stroke="%s" '
             'stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>' % STEEL)
    f.append(circle(360, 156, 5, fill=INK, stroke=INK, sw=1))
    f.append(arrow(279, 162, 320, 162, color=INK, sw=2))
    f.append(text(273, 150, "I", size=13, bold=True))
    f.append(text(360, 138, "▲ гріється", size=11.5, color=POS, bold=True))
    f.append(text(360, 198, "▼ холоне", size=11.5, color=NEG, bold=True))
    f.append(text(360, 214, "елемент Пельтьє", size=11.5, color=MUTED, italic=True))
    # Томсон
    f.append(rect(483, 56, 210, 168, fill="#fbf3e2", stroke="#caa24a", sw=1.6, rx=8))
    f.append(text(588, 80, "Томсон · 1851", size=14, color="#9a7a1e", bold=True))
    f.append(text(588, 100, "струм + градієнт → тепло", size=11.5, italic=True))
    f.append(rect(511, 150, 154, 20, fill=BG, stroke=INK, sw=1.6, rx=0))
    f.append(arrow(517, 140, 653, 140, color=POS, sw=1.8))
    f.append(text(588, 132, "градієнт T", size=11, color=POS))
    f.append(arrow(517, 160, 649, 160, color=INK, sw=2))
    f.append(text(505, 184, "I", size=12.5, bold=True))
    f.append(text(588, 200, "тепло вздовж дроту", size=11.5, color="#9a7a1e"))
    f.append(text(588, 214, "(передбачив теорією)", size=11.5, color=MUTED, italic=True))
    # підсумкова смуга
    f.append(rect(27, 248, 666, 40, fill="#f2f6ff", stroke=INK, sw=1.4, rx=8))
    f.append(text(360, 273, "Кельвін (В. Томсон): термодинаміка зв'язала всі три — співвідношення Кельвіна",
                  size=13, bold=True))
    render(os.path.join(IMG, "three-effects.svg"), W, H, *f,
           title="Три термоелектричні ефекти — одне сімейство")


# ── 10. Термопара як давач: різниця спаїв і опорна точка ──────────────────────
def fig_thermocouple_sensor():
    W, H = 720, 300
    f = []
    # піч / процес
    f.append(rect(40, 80, 120, 120, fill="#fff0e2", stroke=HOT, sw=1.6, rx=6))
    f.append(text(100, 98, "піч / процес", size=12, color=HOT, bold=True))
    _flame(f, 100, 168)
    # вимірювальний спай
    f.append(circle(155, 135, 7, fill=INK, stroke=INK, sw=1))
    f.append(text(155, 121, "вимір. спай", size=11.5, color=POS, bold=True))
    f.append(text(155, 165, "T_вимір", size=12, color=POS, italic=True))
    # два дроти до опорного спаю
    f.append('<polyline points="155,135 260,105 430,105" fill="none" stroke="%s" '
             'stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>' % BRONZE)
    f.append('<polyline points="155,135 260,165 430,165" fill="none" stroke="%s" '
             'stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>' % STEEL)
    f.append(text(345, 96, "метал A", size=11.5, color=BRONZE, bold=True))
    f.append(text(345, 182, "метал B", size=11.5, color=STEEL, bold=True))
    # опорний спай / клеми
    f.append(rect(430, 85, 120, 100, fill="#e8f1fb", stroke=NEG, sw=1.6, rx=6))
    f.append(circle(430, 105, 6, fill=INK, stroke=INK, sw=1))
    f.append(circle(430, 165, 6, fill=INK, stroke=INK, sw=1))
    f.append(text(490, 77, "опорний спай  T_оп", size=11.5, color=NEG, bold=True))
    f.append(line(550, 105, 610, 105, color="#b5651d", sw=4))
    f.append(line(550, 165, 610, 165, color="#b5651d", sw=4))
    f.append(text(580, 97, "мідь", size=10.5, color="#b5651d"))
    f.append(rect(452, 127, 76, 30, fill=BG, stroke=INK, sw=1.4, rx=4))
    f.append(text(490, 147, "ХКК-давач", size=11, bold=True))
    f.append(text(490, 199, "(або лазня з льодом 0 °C)", size=10.5, color=MUTED, italic=True))
    # підсилювач
    f.append('<polyline points="610,90 660,135 610,180" fill="%s" stroke="%s" '
             'stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>' % (BG, INK))
    f.append(text(632, 140, "×", size=16, color=FIELD, bold=True))
    f.append(text(636, 200, "мкВ → В", size=11, color=FIELD, italic=True))
    # формула
    f.append(text(360, 244, "V ≈ S · (T_вимір − T_оп)      сигнал — десятки мкВ/°C",
                  size=14, color=FIELD, bold=True))
    f.append(text(360, 268, "термопара міряє РІЗНИЦЮ спаїв → опорну треба знати окремо",
                  size=12.5, italic=True))
    render(os.path.join(IMG, "thermocouple-sensor.svg"), W, H, *f,
           title="Термопара як давач: різниця спаїв і опорна точка")


if __name__ == "__main__":
    fig_translator()
    fig_chain()
    fig_families()
    fig_duality()
    fig_output_forms()
    fig_imperfect_chain()
    # фігури історичної вставки 📜 hist-seebeck.md
    fig_seebeck_loop()
    fig_seebeck_diffusion()
    fig_three_effects()
    fig_thermocouple_sensor()
    print("Готово: 10 SVG у", IMG)
