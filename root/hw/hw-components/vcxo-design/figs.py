# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

ACC = "#8e44ad"
TANK = "#27ae60"
ORANGE = "#d35400"
BLUE = "#2457d6"
RED = "#c0392b"


class Drawing:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.frags = []

    def rect(self, x, y, w, h, fill=FILL, stroke=LINE, sw=1, rx=0, dash=None):
        if dash:
            self.frags.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s" stroke="%s" stroke-width="%g" rx="%g" stroke-dasharray="%s"/>' % (x, y, w, h, fill, stroke, sw, rx, dash))
        else:
            self.frags.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=rx))

    def circle(self, cx, cy, r, fill=FILL, stroke=LINE, sw=1):
        self.frags.append(circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw))

    def line(self, x1, y1, x2, y2, color=LINE, sw=1, dash=None):
        self.frags.append(line(x1, y1, x2, y2, color=color, sw=sw, dash=dash))

    def path(self, d, fill="none", stroke=LINE, sw=1, dash=None):
        if dash:
            self.frags.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%g" stroke-dasharray="%s"/>' % (d, fill, stroke, sw, dash))
        else:
            self.frags.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%g"/>' % (d, fill, stroke, sw))

    def text(self, x, y, txt, size=12, bold=False, italic=False, color=INK, anchor="start"):
        self.frags.append(text(x, y, txt, size=size, bold=bold, italic=italic, color=color, anchor=anchor))

    def polyline(self, pts, color=LINE, sw=1, dash=None):
        if dash:
            self.frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%g" stroke-dasharray="%s"/>' % (" ".join("%.1f,%.1f" % (px, py) for px, py in pts), color, sw, dash))
        else:
            self.frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%g"/>' % (" ".join("%.1f,%.1f" % (px, py) for px, py in pts), color, sw))

    def save(self, filepath):
        render(filepath, self.w, self.h, *self.frags)


def fig_vcxo_architecture():
    """Архітектура VCXO (схема генератора Пірса з варикапним контуром навантаження)."""
    w, h = 820, 430
    dwg = Drawing(w, h)
    dwg.rect(0, 0, w, h, fill=BG)

    # Заголовок
    dwg.text(410, 28, "Схемотехнічна архітектура генератора VCXO (топологія Пірса)", size=16, bold=True, anchor="middle")

    # Основні блоки / рамки
    # Блок інвертора / підсилювача
    dwg.rect(480, 110, 120, 110, fill="#f8f9fa", stroke=LINE, sw=1.5, rx=6)
    dwg.text(540, 135, "Активний каскад", size=12, bold=True, anchor="middle", color=INK)
    # Символ інвертора всередині
    # трикутник інвертора
    dwg.path("M 515 155 L 515 195 L 555 175 Z", fill="#ffffff", stroke=LINE, sw=1.5)
    dwg.circle(560, 175, 5, fill="#ffffff", stroke=LINE, sw=1.5)
    dwg.text(540, 212, "Інвертор (CMOS)", size=11, anchor="middle", color=MUTED)

    # Резистор зворотного зв'язку Rf над інвертором
    dwg.rect(500, 75, 70, 20, fill="#ffffff", stroke=LINE, sw=1.5)
    dwg.text(535, 89, "Rf (1..10 MΩ)", size=10, anchor="middle", color=INK)
    dwg.line(460, 175, 460, 85, color=LINE, sw=1.5)
    dwg.line(460, 85, 500, 85, color=LINE, sw=1.5)
    dwg.line(570, 85, 620, 85, color=LINE, sw=1.5)
    dwg.line(620, 85, 620, 175, color=LINE, sw=1.5)

    # Вихідний буфер
    dwg.line(565, 175, 660, 175, color=LINE, sw=1.5)
    dwg.circle(620, 175, 3.5, fill=INK)
    dwg.path("M 660 155 L 660 195 L 700 175 Z", fill="#ffffff", stroke=LINE, sw=1.5)
    dwg.circle(705, 175, 5, fill="#ffffff", stroke=LINE, sw=1.5)
    dwg.line(710, 175, 780, 175, color=LINE, sw=2)
    dwg.text(745, 160, "F_out (Clock)", size=12, bold=True, anchor="middle", color=BLUE)

    # Лінія зворотного зв'язку через кварцовий резонатор і варикапи
    # Вхід інвертора (вузол X_IN на 460, 175)
    dwg.circle(460, 175, 3.5, fill=INK)
    dwg.text(445, 165, "X_IN", size=11, bold=True, anchor="end", color=MUTED)
    dwg.line(460, 175, 480, 175, color=LINE, sw=1.5)

    # Конденсатор C2 на вході X_IN на землю
    dwg.line(460, 175, 460, 260, color=LINE, sw=1.5)
    # Конденсатор C2
    dwg.line(445, 260, 475, 260, color=LINE, sw=2)
    dwg.line(445, 266, 475, 266, color=LINE, sw=2)
    dwg.line(460, 266, 460, 290, color=LINE, sw=1.5)
    dwg.line(448, 290, 472, 290, color=LINE, sw=1.5)
    dwg.line(453, 294, 467, 294, color=LINE, sw=1.5)
    dwg.line(457, 298, 463, 298, color=LINE, sw=1.5)
    dwg.text(485, 266, "C2 (15..33 pF)", size=11, anchor="start", color=INK)

    # Лінія від виходу інвертора (X_OUT на 620, 175) до кварцу
    dwg.line(620, 175, 620, 340, color=LINE, sw=1.5)
    dwg.line(620, 340, 400, 340, color=LINE, sw=1.5)

    # Кварцовий резонатор XTAL
    dwg.rect(320, 320, 60, 40, fill="#ffffff", stroke=ACC, sw=2, rx=3)
    # Пластини кварцу
    dwg.line(330, 326, 330, 354, color=ACC, sw=2.5)
    dwg.line(370, 326, 370, 354, color=ACC, sw=2.5)
    dwg.rect(338, 328, 24, 24, fill="#f4ecf7", stroke=ACC, sw=1.5)
    dwg.text(350, 380, "XTAL (Кварц)", size=12, bold=True, anchor="middle", color=ACC)
    dwg.line(400, 340, 380, 340, color=LINE, sw=1.5)
    dwg.line(320, 340, 280, 340, color=LINE, sw=1.5)

    # Розділовий конденсатор C_block
    dwg.line(280, 330, 280, 350, color=LINE, sw=2)
    dwg.line(286, 330, 286, 350, color=LINE, sw=2)
    dwg.text(283, 318, "Cb", size=11, anchor="middle", color=MUTED)
    dwg.line(286, 340, 240, 340, color=LINE, sw=1.5)

    # Блок варикапної пари
    dwg.rect(50, 220, 180, 155, fill="#eaf2f8", stroke=BLUE, sw=1.5, rx=6, dash="5,3")
    dwg.text(140, 240, "Зустрічна пара варикапів", size=11, bold=True, anchor="middle", color=BLUE)

    # Два зустрічні варикапи D1 і D2 (катод до катода)
    # Лівий варикап D1
    dwg.line(90, 340, 90, 280, color=LINE, sw=1.5)
    # земля для D1
    dwg.line(78, 340, 102, 340, color=LINE, sw=1.5)
    dwg.line(83, 344, 97, 344, color=LINE, sw=1.5)
    dwg.line(87, 348, 93, 348, color=LINE, sw=1.5)

    # Варикап D1 (анод внизу, катод вгорі)
    dwg.path("M 78 305 L 102 305 L 90 285 Z", fill="#ffffff", stroke=BLUE, sw=1.5)
    dwg.line(78, 285, 102, 285, color=BLUE, sw=1.5)
    dwg.line(76, 280, 104, 280, color=BLUE, sw=1.5) # лінія ємності варикапа
    dwg.text(68, 295, "D1", size=11, bold=True, anchor="end", color=BLUE)

    # Правий варикап D2 (катод вгорі, анод праворуч/внизу)
    dwg.line(190, 340, 240, 340, color=LINE, sw=1.5)
    dwg.line(190, 340, 190, 280, color=LINE, sw=1.5)
    dwg.path("M 178 305 L 202 305 L 190 285 Z", fill="#ffffff", stroke=BLUE, sw=1.5)
    dwg.line(178, 285, 202, 285, color=BLUE, sw=1.5)
    dwg.line(176, 280, 204, 280, color=BLUE, sw=1.5)
    dwg.text(212, 295, "D2", size=11, bold=True, anchor="start", color=BLUE)

    # З'єднання катодів D1 і D2
    dwg.line(90, 280, 190, 280, color=LINE, sw=1.5)
    dwg.circle(140, 280, 3.5, fill=INK)

    # Лінія подачі напруги керування V_ctrl через дросель/резистор Rb
    dwg.line(140, 280, 140, 160, color=LINE, sw=1.5)
    # Резистор / дросель розв'язки Rb
    dwg.rect(125, 120, 30, 40, fill="#ffffff", stroke=ORANGE, sw=1.5)
    dwg.text(105, 142, "Rb (10..100 kΩ)", size=10, bold=True, anchor="end", color=ORANGE)
    dwg.line(140, 120, 140, 75, color=LINE, sw=1.5)
    dwg.circle(140, 75, 4, fill=RED)
    dwg.text(140, 60, "V_ctrl (Керуюча напруга 0..3.3V)", size=12, bold=True, anchor="middle", color=RED)

    # Блокувальний конденсатор по лінії керування C_filt
    dwg.line(140, 95, 200, 95, color=LINE, sw=1.5)
    dwg.circle(140, 95, 3, fill=INK)
    dwg.line(200, 85, 200, 105, color=LINE, sw=2)
    dwg.line(206, 85, 206, 105, color=LINE, sw=2)
    dwg.line(206, 95, 225, 95, color=LINE, sw=1.5)
    dwg.line(225, 87, 225, 103, color=LINE, sw=1.5)
    dwg.line(229, 90, 229, 100, color=LINE, sw=1.5)
    dwg.line(233, 93, 233, 97, color=LINE, sw=1.5)
    dwg.text(203, 120, "C_filt", size=10, anchor="middle", color=MUTED)

    # З'єднання варикапного вузла назад до X_IN
    dwg.line(240, 340, 240, 175, color=LINE, sw=1.5)
    dwg.line(240, 175, 460, 175, color=LINE, sw=1.5)

    dwg.save(os.path.join(OUT, "vcxo-architecture.svg"))


def fig_pulling_curve_apr():
    """Характеристика перестроювання частоти та розрахунок Absolute Pull Range (APR)."""
    w, h = 820, 440
    dwg = Drawing(w, h)
    dwg.rect(0, 0, w, h, fill=BG)

    dwg.text(410, 28, "Характеристика перестроювання VCXO: Pull Range та APR", size=16, bold=True, anchor="middle")

    # Вісі графіка
    ox, oy = 110, 225  # центр графіка (0 ppm, V_mid)
    gx0, gx1 = 80, 520
    gy0, gy1 = 60, 390

    # Сітка та вісі
    dwg.line(gx0, oy, gx1, oy, color=MUTED, sw=1.2, dash="3,3") # лінія 0 ppm
    dwg.line(300, gy0, 300, gy1, color=MUTED, sw=1.2, dash="3,3") # лінія V_mid = 1.65 V

    # Стрілки осей
    dwg.line(gx0, 380, gx1 + 20, 380, color=LINE, sw=1.8) # вісь X: V_ctrl
    dwg.line(80, gy1, 80, gy0 - 15, color=LINE, sw=1.8)  # вісь Y: Δf/f0 (ppm)

    dwg.text(gx1 + 25, 384, "V_ctrl (В)", size=12, bold=True, anchor="start", color=INK)
    dwg.text(80, gy0 - 25, "Δf / f₀ (ppm)", size=12, bold=True, anchor="middle", color=INK)

    # Підписи на осях
    dwg.text(120, 398, "0 В (V_min)", size=11, anchor="middle", color=MUTED)
    dwg.text(300, 398, "1.65 В (V_nom)", size=11, anchor="middle", color=MUTED)
    dwg.text(480, 398, "3.3 В (V_max)", size=11, anchor="middle", color=MUTED)

    dwg.text(70, oy + 4, "0", size=11, anchor="end", color=MUTED)
    dwg.text(70, oy - 120, "+100", size=11, anchor="end", color=BLUE)
    dwg.text(70, oy + 120, "-100", size=11, anchor="end", color=BLUE)

    # Крива перестроювання (S-подібна характеристика через нелінійність варикапа)
    # f(V_ctrl): при V=0 -> -100 ppm, при V=1.65 -> 0 ppm, при V=3.3 -> +100 ppm
    # Точки кривої
    curve_pts = [
        (120, oy + 115),
        (160, oy + 95),
        (200, oy + 70),
        (250, oy + 35),
        (300, oy),
        (350, oy - 35),
        (400, oy - 70),
        (440, oy - 95),
        (480, oy - 115),
    ]
    d_curve = "M " + " L ".join(["%.1f %.1f" % pt for pt in curve_pts])
    dwg.path(d_curve, fill="none", stroke=BLUE, sw=3)

    # Дотична крутизни перестроювання K_vcxo в робочій точці
    dwg.line(220, oy + 55, 380, oy - 55, color=RED, sw=1.8, dash="4,3")
    dwg.circle(300, oy, 4, fill=RED)
    dwg.text(360, oy - 15, "Крутизна K_vcxo = df/dV (ppm/V)", size=11, bold=True, anchor="start", color=RED)

    # Діапазон Total Pull Range (±100 ppm)
    dwg.line(505, oy - 115, 505, oy + 115, color=BLUE, sw=2)
    dwg.line(495, oy - 115, 515, oy - 115, color=BLUE, sw=1.5)
    dwg.line(495, oy + 115, 515, oy + 115, color=BLUE, sw=1.5)
    dwg.text(525, oy + 4, "Загальний діапазон (Pull Range): ±100 ppm", size=11, bold=True, anchor="start", color=BLUE)

    # Права панель: Бюджет нестабільностей та розрахунок APR
    bx, by = 550, 75
    dwg.rect(bx, by, 250, 315, fill="#fef9e7", stroke=ORANGE, sw=1.5, rx=6)
    dwg.text(bx + 125, by + 24, "Бюджет похибок і APR", size=13, bold=True, anchor="middle", color=ORANGE)

    # Таблиця компонентів нестабільності
    y_row = by + 52
    items = [
        ("Початкова точність (Tolerance)", "±20 ppm"),
        ("Температурний дрейф (-40..+85°C)", "±20 ppm"),
        ("Старіння кристала (за 10 років)", "±10 ppm"),
        ("Нестабільність живлення та V_ctrl", "±5 ppm"),
    ]
    for label, val in items:
        dwg.text(bx + 15, y_row, label, size=10.5, color=INK)
        dwg.text(bx + 235, y_row, val, size=10.5, bold=True, anchor="end", color=RED)
        y_row += 24

    dwg.line(bx + 15, y_row, bx + 235, y_row, color=MUTED, sw=1)
    y_row += 18
    dwg.text(bx + 15, y_row, "Сумарний зсув (Worst Case):", size=11, bold=True, color=INK)
    dwg.text(bx + 235, y_row, "±55 ppm", size=11.5, bold=True, anchor="end", color=RED)

    y_row += 35
    # Формула APR
    dwg.rect(bx + 12, y_row - 10, 226, 75, fill="#e8f8f5", stroke=TANK, sw=1.5, rx=4)
    dwg.text(bx + 125, y_row + 12, "Абсолютний діапазон APR:", size=11.5, bold=True, anchor="middle", color=TANK)
    dwg.text(bx + 125, y_row + 32, "APR = Pull Range - Сумарний зсув", size=10, italic=True, anchor="middle", color=INK)
    dwg.text(bx + 125, y_row + 52, "APR = ±100 - 55 = ±45 ppm", size=12, bold=True, anchor="middle", color=TANK)

    # Індикатор запасу захвату ФАПЧ
    y_row += 95
    dwg.text(bx + 125, y_row, "✓ APR > 0 : Гарантований захват ФАПЧ", size=10.5, bold=True, anchor="middle", color=TANK)

    dwg.save(os.path.join(OUT, "pulling-curve-apr.svg"))


def fig_anti_series_varactors():
    """Порівняння: Одиночний варикап проти зустрічної (anti-series) пари варикапів."""
    w, h = 820, 420
    dwg = Drawing(w, h)
    dwg.rect(0, 0, w, h, fill=BG)

    dwg.text(410, 26, "Придушення нелінійності: одиночний варикап vs зустрічна пара", size=16, bold=True, anchor="middle")

    # Ліва колонка: Одиночний варикап (несиметрична модуляція ємності)
    dwg.rect(40, 60, 350, 335, fill="#fdf2e9", stroke=RED, sw=1.5, rx=6)
    dwg.text(215, 85, "Одиночний варикап (Single Varactor)", size=13, bold=True, anchor="middle", color=RED)

    # Схема
    dwg.line(100, 135, 160, 135, color=LINE, sw=1.5)
    dwg.path("M 160 120 L 160 150 L 185 135 Z", fill="#ffffff", stroke=RED, sw=1.5)
    dwg.line(185, 120, 185, 150, color=RED, sw=1.5)
    dwg.line(190, 118, 190, 152, color=RED, sw=1.5) # варикапна лінія
    dwg.line(190, 135, 250, 135, color=LINE, sw=1.5)
    dwg.line(250, 135, 250, 160, color=LINE, sw=1.5)
    # земля
    dwg.line(240, 160, 260, 160, color=LINE, sw=1.5)
    dwg.line(244, 164, 256, 164, color=LINE, sw=1.5)
    dwg.line(247, 168, 253, 168, color=LINE, sw=1.5)
    dwg.text(100, 125, "ВЧ-сигнал V_rf", size=10.5, color=INK)
    dwg.text(180, 168, "D1", size=11, bold=True, color=RED)

    # Осцилограма ємності одиночного варикапа
    dwg.text(215, 205, "Динамічна ємність під дією ВЧ-напруги:", size=11, bold=True, anchor="middle", color=INK)
    # Вісь
    dwg.line(80, 270, 350, 270, color=MUTED, sw=1, dash="3,3")
    # Викривлена синусоїда (стиснутий додатний півперіод, роздутий від'ємний)
    curve_single = "M 80 270 Q 110 230 145 270 Q 180 325 215 270 Q 245 230 280 270 Q 315 325 350 270"
    dwg.path(curve_single, fill="none", stroke=RED, sw=2.2)
    dwg.text(215, 335, "Несиметрична зміна C(t)", size=10.5, bold=True, anchor="middle", color=RED)

    # Наслідки
    dwg.text(215, 360, "✖ Генерація 2-ї гармоніки (HD2)", size=10.5, color=RED, anchor="middle")
    dwg.text(215, 378, "✖ AM-to-PM конверсія (шум амплітуди → шум фази)", size=10, color=RED, anchor="middle")

    # Права колонка: Зустрічна пара (anti-series)
    dwg.rect(430, 60, 350, 335, fill="#eafaf1", stroke=TANK, sw=1.5, rx=6)
    dwg.text(605, 85, "Зустрічна пара (Back-to-Back)", size=13, bold=True, anchor="middle", color=TANK)

    # Схема пари: катод до катода
    dwg.line(470, 135, 510, 135, color=LINE, sw=1.5)
    # D1 (анод зліва, катод справа)
    dwg.path("M 510 120 L 510 150 L 535 135 Z", fill="#ffffff", stroke=TANK, sw=1.5)
    dwg.line(535, 120, 535, 150, color=TANK, sw=1.5)
    dwg.line(538, 118, 538, 152, color=TANK, sw=1.5)
    # Середня точка (V_ctrl)
    dwg.line(538, 135, 600, 135, color=LINE, sw=1.5)
    dwg.circle(569, 135, 3.5, fill=INK)
    dwg.line(569, 135, 569, 105, color=LINE, sw=1.5)
    dwg.text(569, 100, "V_ctrl", size=10, bold=True, anchor="middle", color=BLUE)

    # D2 (катод зліва, анод справа)
    dwg.line(600, 118, 600, 152, color=TANK, sw=1.5)
    dwg.line(603, 120, 603, 150, color=TANK, sw=1.5)
    dwg.path("M 628 120 L 628 150 L 603 135 Z", fill="#ffffff", stroke=TANK, sw=1.5)
    dwg.line(628, 135, 670, 135, color=LINE, sw=1.5)
    dwg.line(670, 135, 670, 160, color=LINE, sw=1.5)
    # земля
    dwg.line(660, 160, 680, 160, color=LINE, sw=1.5)
    dwg.line(664, 164, 676, 164, color=LINE, sw=1.5)
    dwg.line(667, 168, 673, 168, color=LINE, sw=1.5)

    dwg.text(525, 168, "D1", size=11, bold=True, color=TANK)
    dwg.text(615, 168, "D2", size=11, bold=True, color=TANK)

    # Осцилограма ємності пари
    dwg.text(605, 205, "Еквівалентна ємність пари C_eq(t):", size=11, bold=True, anchor="middle", color=INK)
    dwg.line(470, 270, 740, 270, color=MUTED, sw=1, dash="3,3")
    # Майже ідеальна пряма лінія (взаємна компенсація змін C1 і C2)
    curve_pair = "M 470 270 Q 505 268 537 270 Q 572 272 605 270 Q 640 268 672 270 Q 705 272 740 270"
    dwg.path(curve_pair, fill="none", stroke=TANK, sw=2.5)
    dwg.text(605, 335, "C_eq ≈ const протягом ВЧ-періоду", size=10.5, bold=True, anchor="middle", color=TANK)

    # Переваги
    dwg.text(605, 360, "✓ Взаємна компенсація парних нелінійностей", size=10.5, color=TANK, anchor="middle")
    dwg.text(605, 378, "✓ Придушення AM-to-PM та висока чистота спектра", size=10, color=TANK, anchor="middle")

    dwg.save(os.path.join(OUT, "anti-series-varactors.svg"))


def fig_phase_noise_breakdown():
    """Спектральна густина фазового шуму VCXO та вплив шуму керуючої напруги."""
    w, h = 820, 440
    dwg = Drawing(w, h)
    dwg.rect(0, 0, w, h, fill=BG)

    dwg.text(410, 28, "Спектральний фазовий шум VCXO та вплив шуму напруги керування", size=16, bold=True, anchor="middle")

    # Графік фазового шуму L(f_m) у dBc/Hz vs f_m (Log scale)
    ox, oy = 90, 360
    gx0, gx1 = 90, 750
    gy0, gy1 = 70, 360

    # Вісі
    dwg.line(gx0, gy1, gx1, gy1, color=LINE, sw=1.8) # вісь X
    dwg.line(gx0, gy1, gx0, gy0, color=LINE, sw=1.8) # вісь Y

    dwg.text(gx1, gy1 + 35, "Відбудова від носія f_m (Гц, логарифмічна шкала)", size=11, bold=True, anchor="end", color=INK)
    dwg.text(gx0 - 15, gy0 - 15, "L(f_m) [дБн/Гц]", size=12, bold=True, anchor="start", color=INK)

    # Відмітки по X (декади)
    decades = [
        (90, "10"),
        (220, "100"),
        (350, "1 k"),
        (480, "10 k"),
        (610, "100 k"),
        (740, "1 M"),
    ]
    for x_pos, label in decades:
        dwg.line(x_pos, gy1, x_pos, gy1 + 6, color=LINE, sw=1.2)
        dwg.line(x_pos, gy1, x_pos, gy0, color="#eceff1", sw=1, dash="2,2")
        dwg.text(x_pos, gy1 + 20, label, size=10.5, anchor="middle", color=MUTED)

    # Відмітки по Y (dBc/Hz)
    y_levels = [
        (100, "-60"),
        (160, "-90"),
        (220, "-120"),
        (280, "-140"),
        (340, "-160"),
    ]
    for y_pos, label in y_levels:
        dwg.line(gx0 - 6, y_pos, gx0, y_pos, color=LINE, sw=1.2)
        dwg.line(gx0, y_pos, gx1, y_pos, color="#eceff1", sw=1, dash="2,2")
        dwg.text(gx0 - 12, y_pos + 4, label, size=10.5, anchor="end", color=MUTED)

    # Власний фазовий шум кварцового генератора (без шуму керування) - зелена крива
    # 1/f^3 схил -> 1/f^2 схил -> поличка шуму (floor -160 dBc/Hz)
    pts_xo = "M 90 95 L 220 175 L 350 240 L 480 300 L 610 335 L 740 340"
    dwg.path(pts_xo, fill="none", stroke=TANK, sw=2.5)
    dwg.text(710, 328, "Власний шум кварцу", size=10.5, bold=True, anchor="end", color=TANK)

    # Внесок шуму лінії керування: S_phi = (K_vcxo / f_m)^2 * S_vn(f_m) - червона штрихова
    pts_ctrl_noise = "M 90 80 L 220 145 L 350 215 L 480 290 L 610 355"
    dwg.path(pts_ctrl_noise, fill="none", stroke=RED, sw=2, dash="5,3")
    dwg.text(260, 130, "Модуляційний шум від V_ctrl (S_v / f_m²)", size=10.5, bold=True, color=RED)

    # Результуючий шум VCXO - синя товста крива
    pts_total = "M 90 75 L 220 140 L 350 210 L 480 285 L 610 330 L 740 340"
    dwg.path(pts_total, fill="none", stroke=BLUE, sw=3)
    dwg.text(370, 195, "Сумарний фазовий шум VCXO", size=11, bold=True, color=BLUE)

    # Пояснювальні ділянки моделі Лісона
    dwg.rect(130, 245, 140, 50, fill="#ffffff", stroke=MUTED, sw=1, rx=4)
    dwg.text(200, 265, "1/f³ (Флікер-шум)", size=10, bold=True, anchor="middle", color=INK)
    dwg.text(200, 282, "Схил -30 дБ/дек", size=9.5, anchor="middle", color=MUTED)

    dwg.rect(360, 290, 140, 50, fill="#ffffff", stroke=MUTED, sw=1, rx=4)
    dwg.text(430, 310, "1/f² (Білий шум f)", size=10, bold=True, anchor="middle", color=INK)
    dwg.text(430, 327, "Схил -20 дБ/дек", size=9.5, anchor="middle", color=MUTED)

    dwg.rect(590, 250, 145, 50, fill="#ffffff", stroke=MUTED, sw=1, rx=4)
    dwg.text(662, 270, "Шумовий поріг (Floor)", size=10, bold=True, anchor="middle", color=INK)
    dwg.text(662, 287, "-155..-165 дБн/Гц", size=9.5, anchor="middle", color=MUTED)

    dwg.save(os.path.join(OUT, "phase-noise-breakdown.svg"))


if __name__ == "__main__":
    fig_vcxo_architecture()
    fig_pulling_curve_apr()
    fig_anti_series_varactors()
    fig_phase_noise_breakdown()
    print("All VCXO figures generated successfully in ./img/")
