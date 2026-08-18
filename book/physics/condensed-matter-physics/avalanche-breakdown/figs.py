# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Зонні діаграми: тунелювання Зенера проти лавинного пробою
# ════════════════════════════════════════════════════════════════════════════
def fig_comparison():
    W, H = 840, 420
    f = []

    # Тло та межа між двома панелями
    f.append(line(420, 25, 420, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Тунелювання Зенера ──
    f.append(text(210, 45, "Тунелювання Зенера (сильне легування)", size=14, bold=True, color=INK))
    f.append(text(210, 65, "Вузька збіднена область W < 10 нм", size=12, color=MUTED))

    # Зонна структура для Зенера
    f.append(svg_path("M 40 120 L 140 120 C 170 120 180 270 210 270 L 380 270", stroke="#c0392b", sw=2.5, fill="none")) # Ec
    f.append(svg_path("M 40 210 L 140 210 C 170 210 180 360 210 360 L 380 360", stroke="#2980b9", sw=2.5, fill="none")) # Ev

    f.append(text(80, 112, "E_c (n-бік / p-бік)", size=11, color="#c0392b", bold=True))
    f.append(text(80, 202, "E_v (валентна зона)", size=11, color="#2980b9", bold=True))

    # Вузький бар'єр тунелювання (пунктир відстані W)
    f.append(line(140, 375, 210, 375, color=DARK, sw=1.5))
    f.append(line(140, 370, 140, 380, color=DARK, sw=1.5))
    f.append(line(210, 370, 210, 380, color=DARK, sw=1.5))
    f.append(text(175, 393, "W < 10 нм", size=11, bold=True, color=DARK))

    # Стрілка тунелювання: горизонтальний перехід з Ev(p) в Ec(n)
    f.append(line(120, 210, 225, 210, color="#8e44ad", sw=2.5, dash="3 3"))
    f.append(polygon([(225, 206), (235, 210), (225, 214)], fill="#8e44ad"))
    f.append(circle(120, 210, 5, fill="#2980b9", stroke="#1a5276", sw=1.5)) # електрон у Ev
    f.append(circle(245, 210, 5, fill="#c0392b", stroke="#7b241c", sw=1.5)) # тунельований електрон у Ec
    f.append(text(175, 198, "квантове тунелювання", size=11, bold=True, color="#8e44ad"))

    # ── Права панель: Лавинний пробій ──
    f.append(text(630, 45, "Лавинний пробій (помірне легування)", size=14, bold=True, color=INK))
    f.append(text(630, 65, "Широка збіднена область W > 100 нм", size=12, color=MUTED))

    # Зонна структура для Лавини (широка область вигину)
    f.append(svg_path("M 450 110 L 510 110 L 730 270 L 800 270", stroke="#c0392b", sw=2.5, fill="none")) # Ec
    f.append(svg_path("M 450 200 L 510 200 L 730 360 L 800 360", stroke="#2980b9", sw=2.5, fill="none")) # Ev

    # Широкий бар'єр W
    f.append(line(510, 375, 730, 375, color=DARK, sw=1.5))
    f.append(line(510, 370, 510, 380, color=DARK, sw=1.5))
    f.append(line(730, 370, 730, 380, color=DARK, sw=1.5))
    f.append(text(620, 393, "W > 100 нм", size=11, bold=True, color=DARK))

    # Прискорення електрона полем у зонах
    f.append(line(520, 118, 610, 182, color="#d35400", sw=2, dash="4 2"))
    f.append(circle(520, 118, 5, fill="#e67e22", stroke="#d35400", sw=1.5))

    # Точка зіткнення / ударної іонізації
    f.append(circle(610, 182, 7, fill="#f1c40f", stroke="#d35400", sw=2))
    f.append(text(610, 168, "ударна іонізація", size=11, bold=True, color="#d35400"))

    # Породжені носії: 2 електрони продовжують у Ec, 1 дірка летить у Ev
    f.append(line(610, 182, 680, 233, color="#c0392b", sw=2))
    f.append(line(610, 182, 690, 240, color="#c0392b", sw=2))
    f.append(circle(680, 233, 5, fill="#c0392b", stroke="#7b241c", sw=1.5))
    f.append(circle(690, 240, 5, fill="#c0392b", stroke="#7b241c", sw=1.5))

    # Породжена дірка прямує вгору по Ev (ліворуч)
    f.append(line(610, 273, 540, 222, color="#2980b9", sw=2))
    f.append(circle(540, 222, 5, fill="#3498db", stroke="#1f618d", sw=1.5))
    f.append(text(525, 238, "h⁺", size=11, bold=True, color="#2980b9"))
    f.append(text(705, 245, "e⁻, e⁻", size=11, bold=True, color="#c0392b"))

    render(os.path.join(OUT, "breakdown-comparison.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Температурний коефіцієнт напруги пробою
# ════════════════════════════════════════════════════════════════════════════
def fig_tempco():
    W, H = 760, 400
    f = []

    # Осі координат
    f.append(line(80, 320, 700, 320, color=DARK, sw=1.5)) # T (температура)
    f.append(line(80, 320, 80, 40, color=DARK, sw=1.5))   # V_BR (напруга пробою)

    # Стрілки осей
    f.append(polygon([(700, 316), (710, 320), (700, 324)], fill=DARK))
    f.append(polygon([(76, 40), (80, 30), (84, 40)], fill=DARK))

    f.append(text(710, 340, "Температура T (°C)", size=12, bold=True, color=DARK))
    f.append(text(35, 30, "Напруга пробою V_BR (В)", size=12, bold=True, color=DARK))

    # Позначка кімнатної температури T0
    f.append(line(350, 320, 350, 326, color=DARK, sw=1.5))
    f.append(text(350, 342, "25 °C", size=11, color=MUTED))
    f.append(line(350, 50, 350, 315, color=MUTED, sw=1, dash="3 3"))

    # Лінія 1: Зенерівський пробій (< 5 В) — від'ємний ТКН (від'ємний нахил)
    f.append(svg_path("M 120 100 L 650 160", stroke="#8e44ad", sw=2.5, fill="none"))
    f.append(circle(350, 125, 5, fill="#8e44ad", stroke="#5b2c6f", sw=1.5))
    f.append(text(520, 135, "Зенерівський пробій (V_BR < 5 В): dV/dT < 0", size=12, bold=True, color="#8e44ad"))
    f.append(text(520, 153, "Звуження E_g при нагріванні полегшує тунелювання", size=10.5, color=MUTED))

    # Лінія 2: Термокомпенсований стабілітрон (~ 5.6 В) — нульовий ТКН
    f.append(svg_path("M 120 200 L 650 200", stroke="#27ae60", sw=2.5, fill="none"))
    f.append(circle(350, 200, 5, fill="#27ae60", stroke="#1e8449", sw=1.5))
    f.append(text(520, 192, "Точка компенсації (V_BR ≈ 5.6 В): dV/dT ≈ 0", size=12, bold=True, color="#27ae60"))
    f.append(text(520, 215, "Зенерівський і лавинний ефекти взаємно гасяться", size=10.5, color=MUTED))

    # Лінія 3: Лавинний пробій (> 6 В) — додатний ТКН
    f.append(svg_path("M 120 300 L 650 230", stroke="#d35400", sw=2.5, fill="none"))
    f.append(circle(350, 268, 5, fill="#d35400", stroke="#a04000", sw=1.5))
    f.append(text(520, 275, "Лавинний пробій (V_BR > 6 В): dV/dT > 0", size=12, bold=True, color="#d35400"))
    f.append(text(520, 293, "Підсилення фононного розсіювання зменшує пробіг", size=10.5, color=MUTED))

    render(os.path.join(OUT, "tempco-graph.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Вольт-амперна характеристика з ділянкою зворотного пробою
# ════════════════════════════════════════════════════════════════════════════
def fig_iv_curve():
    W, H = 780, 440
    f = []

    # Осі координат V та I
    cx, cy = 480, 160

    # Вісь напруги V (горизонтальна)
    f.append(line(60, cy, 740, cy, color=DARK, sw=1.5))
    f.append(polygon([(740, cy - 4), (750, cy), (740, cy + 4)], fill=DARK))
    f.append(text(730, cy + 22, "Пряма напруга V_F (В)", size=11.5, bold=True, color=DARK))
    f.append(text(120, cy - 12, "Зворотна напруга -V_R (В)", size=11.5, bold=True, color=DARK))

    # Вісь струму I (вертикальна)
    f.append(line(cx, 390, cx, 30, color=DARK, sw=1.5))
    f.append(polygon([(cx - 4, 30), (cx, 20), (cx + 4, 30)], fill=DARK))
    f.append(text(cx + 12, 32, "Прямий струм I_F (мА)", size=11.5, bold=True, color=DARK))
    f.append(text(cx + 12, 385, "Зворотний струм -I_R (мА)", size=11.5, bold=True, color=DARK))

    # Крива ВАХ
    f.append(svg_path("M %d %d L %d %d C %d %d %d %d %d %d" % (cx, cy, cx + 50, cy, cx + 70, cy, cx + 80, cy - 30, cx + 110, cy - 120), stroke="#27ae60", sw=2.5, fill="none"))

    vx_br = cx - 260
    f.append(svg_path("M %d %d L %d %d C %d %d %d %d %d %d" % (cx, cy, vx_br + 30, cy + 8, vx_br + 10, cy + 10, vx_br, cy + 30, vx_br - 10, cy + 200), stroke="#c0392b", sw=2.5, fill="none"))

    # Позначення точки коліна пробою V_BR
    f.append(line(vx_br, cy - 6, vx_br, cy + 6, color=DARK, sw=1.5))
    f.append(text(vx_br, cy - 14, "-V_BR", size=12, bold=True, color="#c0392b"))

    # Позначення струму витоку Is
    f.append(line(cx - 5, cy + 8, cx + 5, cy + 8, color=MUTED, sw=1, dash="2 2"))
    f.append(text(cx + 12, cy + 12, "-I_s (струм витоку)", size=10.5, color=MUTED))

    # Визначення динамічного опору R_z = dV / dI
    y1, y2 = cy + 60, cy + 160
    x1, x2 = vx_br - 3, vx_br - 8
    f.append(line(x1, y1, x2, y2, color="#2980b9", sw=2))
    f.append(line(x1, y1, x1, y2, color="#2980b9", sw=1.2, dash="3 3"))
    f.append(line(x1, y2, x2, y2, color="#2980b9", sw=1.2, dash="3 3"))

    f.append(text(vx_br - 150, cy + 110, "R_z = ΔV / ΔI (динамічний опір)", size=11.5, bold=True, color="#2980b9"))
    f.append(text(vx_br - 150, cy + 128, "Крутий нахил → малий R_z (стабілізація)", size=10.5, color=MUTED))

    # Область робочого режиму стабілітрона (затінений прямокутник)
    f.append(rect(vx_br - 25, cy + 30, 30, 160, fill="#fadbd8", stroke="none"))
    f.append(text(vx_br - 90, cy + 180, "Робоча область", size=11, bold=True, color="#c0392b"))
    f.append(text(vx_br - 90, cy + 195, "стабілітрона / TVS", size=11, color="#c0392b"))

    render(os.path.join(OUT, "iv-curve.svg"), W, H, *f)


if __name__ == '__main__':
    fig_comparison()
    fig_tempco()
    fig_iv_curve()
    print("Figures generated successfully.")
