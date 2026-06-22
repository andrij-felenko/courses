# -*- coding: utf-8 -*-
"""Фігури до теми «Характеристики давача».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREY = "#8a8a8a"


def _axes(f, ox, oy, top, right, ylab="вихід U", xlab="величина x"):
    """Осі координат зі стрілками: вертикаль угору від (ox,oy), горизонталь управо."""
    f.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    f.append(arrow(ox, oy, right, oy, color=INK, sw=1.6))
    f.append(text(ox - 8, top + 8, ylab, size=12, anchor="end", bold=True))
    f.append(text(right - 6, oy + 18, xlab, size=12, bold=True))


# ── 1. Передавальна характеристика: вихід як функція величини ─────────────────
def fig_transfer():
    W, H = 620, 330
    f = []
    _axes(f, 96, 280, 48, 560)
    # ідеальна пряма U = U0 + S*x
    f.append('<polyline points="96.0,245.1 546.0,79.4" fill="none" stroke="%s" '
             'stroke-width="2.8" stroke-linejoin="round" stroke-linecap="round"/>' % FIELD)
    # позначка зсуву нуля U0 на осі
    f.append(line(90, 245.1, 102, 245.1, color=POS, sw=2))
    f.append(text(86, 249.1, "U₀", size=12.5, color=POS, anchor="end", bold=True))
    f.append(text(166, 239.1, "зсув нуля (offset)", size=11, color=POS, anchor="start", italic=True))
    # трикутник нахилу: Δx, ΔU
    f.append(line(298.5, 166.6, 433.5, 166.6, color=INK, sw=1.6, dash="3,3"))
    f.append(line(433.5, 166.6, 433.5, 127.4, color=INK, sw=1.6, dash="3,3"))
    f.append(text(366, 182.6, "Δx", size=11, bold=True))
    f.append(text(441.5, 147.0, "ΔU", size=11, anchor="start", bold=True))
    f.append(text(346, 70, "S = ΔU/Δx  (чутливість)", size=12, color=FIELD, anchor="start", bold=True))
    f.append(text(310, 318, "ідеальний давач: пряма U = U₀ + S·x", size=11.5, italic=True))
    render(os.path.join(IMG, "transfer.svg"), W, H, *f,
           title="Передавальна характеристика: вихід як функція величини")


# ── 2. Чутливість — нахил: крута крива дає більший сигнал ─────────────────────
def fig_sensitivity():
    W, H = 620, 320
    f = []
    _axes(f, 90, 270, 46, 564, ylab="U", xlab="x")
    f.append('<polyline points="90.0,253.2 550.0,70.5" fill="none" stroke="%s" '
             'stroke-width="2.8" stroke-linejoin="round" stroke-linecap="round"/>' % FIELD)
    f.append('<polyline points="90.0,253.2 550.0,173.4" fill="none" stroke="%s" '
             'stroke-width="2.8" stroke-linejoin="round" stroke-linecap="round"/>' % NEG)
    f.append(text(467.2, 89.4, "велика S", size=12, color=FIELD, anchor="start", bold=True))
    f.append(text(467.2, 181.8, "мала S", size=12, color=NEG, anchor="start", bold=True))
    f.append(line(343, 270, 343, 89.4, color=GREY, sw=1, dash="3,3"))
    f.append(text(343, 288, "та сама Δx", size=11, italic=True))
    f.append(text(310, 308, "більша S → легше прочитати, але швидше насичує вихід", size=11.5, italic=True))
    render(os.path.join(IMG, "sensitivity.svg"), W, H, *f,
           title="Чутливість — це нахил: крута крива дає більший сигнал")


# ── 3. Діапазон — робоче вікно; поза ним мертва зона й насичення ──────────────
def fig_range():
    W, H = 640, 320
    f = []
    _axes(f, 80, 262, 48, 594, ylab="U", xlab="x")
    f.append('<polyline points="80.0,250.0 140.0,250.0 470.0,90.0 580.0,82.0" fill="none" '
             'stroke="%s" stroke-width="2.8" stroke-linejoin="round" stroke-linecap="round"/>' % FIELD)
    f.append(text(100, 242, "мертва зона", size=9, color=NEG, anchor="start", italic=True))
    # дужка робочого діапазону
    f.append(line(140, 292, 470, 292, color=FIELD, sw=2))
    f.append(line(140, 288, 140, 296, color=FIELD, sw=2))
    f.append(line(470, 288, 470, 296, color=FIELD, sw=2))
    f.append(text(305, 308, "робочий діапазон (повна шкала FS)", size=11.5, color=FIELD, bold=True))
    f.append(text(526, 74, "насичення", size=11, color=POS, anchor="start", bold=True))
    f.append(text(526, 90, "(вихід уперся в стелю)", size=10, color=POS, anchor="start", italic=True))
    render(os.path.join(IMG, "range.svg"), W, H, *f,
           title="Діапазон — робоче вікно; поза ним мертва зона й насичення")


# ── 4. Лінійність: відхилення реальної кривої від опорної прямої ──────────────
def fig_linearity():
    W, H = 620, 320
    f = []
    _axes(f, 90, 268, 48, 564, ylab="U", xlab="x")
    f.append('<polyline points="90.0,247.4 550.0,82.6" fill="none" stroke="%s" '
             'stroke-width="2" stroke-dasharray="6,4" stroke-linejoin="round" stroke-linecap="round"/>' % GREY)
    f.append(text(412, 107.3, "опорна пряма", size=11, color=GREY, anchor="start", italic=True))
    f.append('<polyline points="90.0,247.4 182.0,200.0 274.0,165.0 320.0,152.6 366.0,142.3 458.0,115.6 550.0,82.6" '
             'fill="none" stroke="%s" stroke-width="2.8" stroke-linejoin="round" stroke-linecap="round"/>' % FIELD)
    f.append(text(218.8, 173.2, "реальна крива", size=11, color=FIELD, anchor="start", bold=True))
    # позначка найбільшого відхилення
    f.append(line(320, 165.0, 320, 152.6, color=POS, sw=2))
    f.append(line(316, 165.0, 324, 165.0, color=POS, sw=2))
    f.append(text(328, 142.8, "нелінійність", size=11, color=POS, anchor="start", bold=True))
    f.append(text(328, 156.8, "(макс., % FS)", size=10, color=POS, anchor="start", italic=True))
    render(os.path.join(IMG, "linearity.svg"), W, H, *f,
           title="Лінійність: відхилення реальної кривої від опорної прямої")


# ── 5. Точність ≠ прецизійність: чотири випадки на мішені ─────────────────────
def fig_accuracy_precision():
    W, H = 560, 360
    f = []

    def target(cx, cy, dots, label):
        f.append(circle(cx, cy, 46, fill=BG, stroke=INK, sw=1.4))
        f.append(circle(cx, cy, 28.5, fill="none", stroke=GREY, sw=1.1))
        f.append(circle(cx, cy, 12, fill="#f3dada", stroke=POS, sw=1.1))
        for dx, dy in dots:
            f.append('<circle cx="%.1f" cy="%.1f" r="2.6" fill="%s"/>' % (cx + dx, cy + dy, POS))
        f.append(text(cx, cy + 70, label, size=12, bold=True))

    # точно + прецизійно — тісна купка в центрі
    target(150, 110, [(-3, -2), (2, -3), (-1, 3), (3, 2), (0, 0)], "точно + прецизійно")
    # прецизійно, не точно — тісна купка збоку
    target(410, 110, [(12, -15), (17, -16), (14, -10), (18, -11), (15, -13)], "прецизійно, не точно")
    # точно, не прецизійно — розкид навколо центру
    target(150, 270, [(-15, -11), (13, -14), (-16, 10), (16, 12), (1, -2)], "точно, не прецизійно")
    # ні те, ні те — розкид збоку
    target(410, 270, [(0, -24), (28, -27), (-1, -3), (31, -1), (16, -15)], "ні те, ні те")

    f.append(text(280, 348, "тіснота купки = прецизійність · де купка = точність",
                  size=11.5, color=GREY, italic=True))
    render(os.path.join(IMG, "accuracy-precision.svg"), W, H, *f,
           title="Точність ≠ прецизійність: чотири випадки на мішені")


# ── 6. Роздільність: гладку величину вихід бачить сходинками ──────────────────
def fig_resolution():
    W, H = 620, 300
    f = []
    _axes(f, 80, 250, 46, 574, ylab="U", xlab="час →")
    # справжня гладка величина (пунктир)
    f.append('<polyline points="80.0,234.8 560.0,79.0" fill="none" stroke="%s" '
             'stroke-width="1.8" stroke-dasharray="5,4" stroke-linejoin="round" stroke-linecap="round"/>' % GREY)
    f.append(text(396.8, 101.8, "справжня величина", size=10.5, color=GREY, anchor="start", italic=True))
    # оцифрований вихід — сходинки
    steps = "80.0,234.8 140.0,234.8 140.0,215.3 200.0,215.3 200.0,195.8 260.0,195.8 260.0,176.4 320.0,176.4 320.0,156.9 380.0,156.9 380.0,137.4 440.0,137.4 440.0,118.0 500.0,118.0 500.0,98.5 560.0,98.5 560.0,79.0"
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (steps, FIELD))
    # висота сходинки = роздільність
    f.append(line(350, 156.9, 350, 137.4, color=POS, sw=2))
    f.append(line(346, 156.9, 354, 156.9, color=POS, sw=2))
    f.append(line(346, 137.4, 354, 137.4, color=POS, sw=2))
    f.append(text(360, 151.2, "крок = роздільність", size=11, color=POS, anchor="start", bold=True))
    render(os.path.join(IMG, "resolution.svg"), W, H, *f,
           title="Роздільність: гладку величину вихід бачить сходинками")


# ── 7. Як читати даташит: усі числа — на одній кривій ────────────────────────
def fig_datasheet():
    W, H = 640, 350
    f = []
    _axes(f, 96, 286, 46, 550)
    # смуга нелінійності (товста сіра) + сама характеристика
    f.append('<polyline points="140.0,245.3 470.0,100.7" fill="none" stroke="#e4e4e4" '
             'stroke-width="9" stroke-linejoin="round" stroke-linecap="round"/>')
    f.append('<polyline points="140.0,245.3 470.0,100.7" fill="none" stroke="%s" '
             'stroke-width="2.8" stroke-linejoin="round" stroke-linecap="round"/>' % FIELD)
    # зсув нуля
    f.append('<circle cx="140.0" cy="245.3" r="4.0" fill="%s"/>' % POS)
    f.append(text(134, 249.3, "U₀", size=12, color=POS, anchor="end", bold=True))
    f.append(text(228, 161.7, "нахил = S", size=11.5, color=FIELD, anchor="start", bold=True))
    f.append(text(360, 182.0, "смуга нелінійності", size=10.5, color="#9a7a1e", anchor="start", italic=True))
    # дужка діапазону
    f.append(line(140, 316, 470, 316, color=INK, sw=1.8))
    f.append(line(140, 312, 140, 320, color=INK, sw=1.8))
    f.append(line(470, 312, 470, 320, color=INK, sw=1.8))
    f.append(text(305, 332, "діапазон / повна шкала", size=11.5, bold=True))
    # крок роздільності
    f.append(line(478, 100.7, 478, 86.7, color=NEG, sw=2))
    f.append(line(474, 100.7, 482, 100.7, color=NEG, sw=2))
    f.append(line(474, 86.7, 482, 86.7, color=NEG, sw=2))
    f.append(text(486, 96.7, "крок", size=10, color=NEG, anchor="start", bold=True))
    render(os.path.join(IMG, "datasheet.svg"), W, H, *f,
           title="Як читати даташит: усі числа — на одній кривій")


if __name__ == "__main__":
    fig_transfer()
    fig_sensitivity()
    fig_range()
    fig_linearity()
    fig_accuracy_precision()
    fig_resolution()
    fig_datasheet()
    print("Готово: 7 SVG у", IMG)
