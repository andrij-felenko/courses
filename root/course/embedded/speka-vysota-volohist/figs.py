# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. density-altitude-concept: геометрична висота проти висоти за густиною ──
def fig_density_altitude_concept():
    W, H = 940, 480
    p = []

    # Заголовок і підзаголовок (без передачі title у render)
    p.append(text(W / 2, 28, "Концепція Density Altitude (висоти за густиною)", size=16, color=INK, bold=True))
    p.append(text(W / 2, 50, "Аеродинамічні сили й двигун відчувають не геометричну висоту, а фактичну густину повітря ρ", size=12, color=MUTED))

    col_w, col_h = 270, 350
    y_top = 75

    # Колонка 1: Рівень моря ISA
    x1 = 40
    p.append(rect(x1, y_top, col_w, col_h, fill="#f2f8f4", stroke=FIELD, sw=2, rx=8))
    p.append(text(x1 + col_w/2, y_top + 28, "Рівень моря (ISA)", size=15, color=FIELD, bold=True))
    p.append(text(x1 + col_w/2, y_top + 48, "Стандартна атмосфера", size=11, color=MUTED))
    p.append(line(x1 + 20, y_top + 60, x1 + col_w - 20, y_top + 60, color="#cde6d5", sw=1.5))

    p.append(text(x1 + 24, y_top + 88, "Геодезична висота: 0 м", size=11.5, color=INK, anchor="start", bold=True))
    p.append(text(x1 + 24, y_top + 112, "Тиск: 1013.25 гПа", size=11.5, color=INK, anchor="start"))
    p.append(text(x1 + 24, y_top + 136, "Температура: +15 °C", size=11.5, color=INK, anchor="start"))
    p.append(text(x1 + 24, y_top + 160, "Вологість: 0% (сухе)", size=11.5, color=INK, anchor="start"))

    p.append(rect(x1 + 20, y_top + 180, col_w - 40, 54, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(x1 + col_w/2, y_top + 200, "Густина повітря ρ₀:", size=11, color=MUTED))
    p.append(text(x1 + col_w/2, y_top + 222, "1.2250 кг/м³ (100%)", size=13.5, color=FIELD, bold=True))

    p.append(text(x1 + col_w/2, y_top + 262, "• 100% номінальної тяги", size=11, color=INK))
    p.append(text(x1 + col_w/2, y_top + 286, "• Штатний час польоту", size=11, color=INK))
    p.append(text(x1 + col_w/2, y_top + 310, "• Нормативне охолодження", size=11, color=INK))

    # Колонка 2: Реальний майданчик High & Hot
    x2 = 335
    p.append(rect(x2, y_top, col_w, col_h, fill="#fdf3f2", stroke=POS, sw=2, rx=8))
    p.append(text(x2 + col_w/2, y_top + 28, "Майданчик «High & Hot»", size=15, color=POS, bold=True))
    p.append(text(x2 + col_w/2, y_top + 48, "Гори + спека + вологість", size=11, color=MUTED))
    p.append(line(x2 + 20, y_top + 60, x2 + col_w - 20, y_top + 60, color="#f5c6cb", sw=1.5))

    p.append(text(x2 + 24, y_top + 88, "Геодезична висота: 1500 м", size=11.5, color=INK, anchor="start", bold=True))
    p.append(text(x2 + 24, y_top + 112, "Тиск: 845 гПа", size=11.5, color=INK, anchor="start"))
    p.append(text(x2 + 24, y_top + 136, "Температура: +38 °C (спека)", size=11.5, color=POS, anchor="start", bold=True))
    p.append(text(x2 + 24, y_top + 160, "Вологість: 65% (водяна пара)", size=11.5, color=POS, anchor="start"))

    p.append(rect(x2 + 20, y_top + 180, col_w - 40, 54, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    p.append(text(x2 + col_w/2, y_top + 200, "Фактична густина ρ:", size=11, color=MUTED))
    p.append(text(x2 + col_w/2, y_top + 222, "0.932 кг/м³ (−24%)", size=13.5, color=POS, bold=True))

    p.append(text(x2 + col_w/2, y_top + 262, "• Макс. тяга впала на 24%", size=11, color=POS, bold=True))
    p.append(text(x2 + col_w/2, y_top + 286, "• Оберти висіння зросли на 15%", size=11, color=INK))
    p.append(text(x2 + col_w/2, y_top + 310, "• Струм мотора зріс на 15%", size=11, color=INK))

    # Стрілка еквівалентності
    p.append(arrow(x2 + col_w + 3, y_top + 207, x2 + col_w + 22, y_top + 207, color=NEG, sw=2.2))
    p.append(text(x2 + col_w + 12, y_top + 194, "ρ рівні", size=9.5, color=NEG, bold=True))

    # Колонка 3: Еквівалент Density Altitude в ISA
    x3 = 630
    p.append(rect(x3, y_top, col_w, col_h, fill="#f0f4fd", stroke=NEG, sw=2, rx=8))
    p.append(text(x3 + col_w/2, y_top + 28, "Density Altitude (DA)", size=15, color=NEG, bold=True))
    p.append(text(x3 + col_w/2, y_top + 48, "Еквівалентна висота в ISA", size=11, color=MUTED))
    p.append(line(x3 + 20, y_top + 60, x3 + col_w - 20, y_top + 60, color="#cbd8f5", sw=1.5))

    p.append(text(x3 + 24, y_top + 88, "Еквівалентна DA: 3880 м", size=11.5, color=NEG, anchor="start", bold=True))
    p.append(text(x3 + 24, y_top + 112, "Перевищення DA: +2380 м!", size=11.5, color=POS, anchor="start", bold=True))
    p.append(text(x3 + 24, y_top + 136, "ISA Температура: −10.2 °C", size=11.5, color=INK, anchor="start"))
    p.append(text(x3 + 24, y_top + 160, "ISA Тиск: 630 гПа", size=11.5, color=INK, anchor="start"))

    p.append(rect(x3 + 20, y_top + 180, col_w - 40, 54, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(x3 + col_w/2, y_top + 200, "Еталонна густина ISA:", size=11, color=MUTED))
    p.append(text(x3 + col_w/2, y_top + 222, "0.932 кг/м³ на 3880 м", size=13.5, color=NEG, bold=True))

    p.append(text(x3 + col_w/2, y_top + 262, "Апарат летить так, ніби він", size=11, color=INK))
    p.append(text(x3 + col_w/2, y_top + 286, "піднявся на вершину гори", size=11, color=INK))
    p.append(text(x3 + col_w/2, y_top + 310, "висотою майже 4 кілометри!", size=11, color=NEG, bold=True))

    # Нижній висновок
    p.append(rect(40, 442, 860, 26, fill="#fafbfc", stroke="#d1d5db", sw=1, rx=4))
    p.append(text(W / 2, 459, "Підсумок: спека +38 °C на висоті 1500 м «піднімає» аеродинамічну висоту дрона майже на 2.4 км вгору", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "density-altitude-concept.svg"), W, H, *p, title=None)


# ── 2. thrust-power-vs-density: графік деградації характеристик від густини ──
def fig_thrust_power_vs_density():
    W, H = 940, 480
    p = []

    # Заголовок і підзаголовок
    p.append(text(W / 2, 28, "Деградація льотних та енергетичних показників від густини повітря (ρ / ρ₀)", size=16, color=INK, bold=True))
    p.append(text(W / 2, 48, "Падіння максимальної тяги, зростання потужності висіння та вибух теплових втрат I²R", size=12, color=MUTED))

    # Вісь координат
    x0, y0 = 90, 410
    xw, yh = 540, 320

    def px(rho_rel):
        return x0 + (rho_rel - 0.60) / 0.40 * xw

    def py(val):
        return y0 - (val - 0.50) / 1.30 * yh

    # Горизонтальні лінії сітки
    for v in [0.6, 0.8, 1.0, 1.2, 1.4, 1.6]:
        yy = py(v)
        p.append(line(x0, yy, x0 + xw, yy, color="#e5e7eb", sw=1))
        p.append(text(x0 - 10, yy + 4, "%.1f" % v, size=10, color=MUTED, anchor="end"))

    # Вертикальні лінії сітки
    for r in [0.60, 0.70, 0.80, 0.90, 1.00]:
        xx = px(r)
        p.append(line(xx, y0, xx, y0 - yh, color="#e5e7eb", sw=1))
        p.append(text(xx, y0 + 18, "%.2f" % r, size=10, color=MUTED))

    p.append(text(x0 + xw / 2, y0 + 38, "Відносна густина повітря ρ / ρ₀  (1.00 = рівень моря ISA) →", size=11, color=INK, bold=True))
    p.append(text(x0, y0 - yh - 12, "Відносна величина (1.0 = норма ISA) ↑", size=11, color=INK, bold=True, anchor="start"))

    # Осі
    p.append(line(x0, y0, x0 + xw, y0, color=INK, sw=1.8))
    p.append(line(x0, y0, x0, y0 - yh, color=INK, sw=1.8))

    # Побудова кривих
    import math

    # 1. Максимальна тяга: T_max / T_0 = rho / rho_0
    pts_tmax = "%.1f,%.1f %.1f,%.1f" % (px(0.60), py(0.60), px(1.00), py(1.00))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (pts_tmax, POS))

    # 2. Оберти висіння та потужність валу: n/n0 = sqrt(1 / rho_rel)
    steps = 40
    pts_power = []
    pts_heat = []
    for i in range(steps + 1):
        r = 0.60 + i * (0.40 / steps)
        p_val = math.sqrt(1.0 / r)
        pts_power.append("%.1f,%.1f" % (px(r), py(p_val)))
        h_val = 1.0 / r
        pts_heat.append("%.1f,%.1f" % (px(r), py(h_val)))

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts_power), NEG))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" stroke-dasharray="6,4"/>' % (" ".join(pts_heat), "#b45309"))

    # Маркери в точці rho = 1.0 (номінал)
    p.append(circle(px(1.0), py(1.0), 5, fill="#ffffff", stroke=FIELD, sw=2.5))
    p.append(text(px(1.0) + 12, py(1.0) - 8, "Номінал ISA", size=11, color=FIELD, anchor="start", bold=True))

    # Легенда справа
    lx, ly = 660, 85
    lw, lh = 250, 335
    p.append(rect(lx, ly, lw, lh, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=8))
    p.append(text(lx + lw/2, ly + 25, "Легенда графіків:", size=13, color=INK, bold=True))

    # Елемент 1
    p.append(line(lx + 15, ly + 55, lx + 48, ly + 55, color=POS, sw=2.8))
    p.append(text(lx + 56, ly + 52, "Максимальна тяга T_max", size=11, color=INK, anchor="start", bold=True))
    p.append(text(lx + 56, ly + 68, "T_max ∝ ρ (прямо пропорційно)", size=9.5, color=MUTED, anchor="start"))

    # Елемент 2
    p.append(line(lx + 15, ly + 105, lx + 48, ly + 105, color=NEG, sw=2.8))
    p.append(text(lx + 56, ly + 102, "Потужність висіння P_hov", size=11, color=INK, anchor="start", bold=True))
    p.append(text(lx + 56, ly + 118, "P_hov ∝ 1 / √(ρ/ρ₀)  (+29% при 0.6)", size=9.5, color=MUTED, anchor="start"))

    # Елемент 3
    p.append(line(lx + 15, ly + 155, lx + 48, ly + 155, color="#b45309", sw=2.8, dash="6,4"))
    p.append(text(lx + 56, ly + 152, "Теплові втрати міді I²·R", size=11, color=INK, anchor="start", bold=True))
    p.append(text(lx + 56, ly + 168, "I²·R ∝ 1 / (ρ/ρ₀)  (+67% нагріву!)", size=9.5, color=MUTED, anchor="start"))

    # Пояснювальний блок під легендою
    p.append(rect(lx + 10, ly + 195, lw - 20, 125, fill="#fff5f5", stroke="#fed7d7", sw=1, rx=6))
    p.append(text(lx + lw/2, ly + 218, "Критична небезпека:", size=11.5, color=POS, bold=True))
    p.append(text(lx + lw/2, ly + 240, "При ρ = 0.70 (гори 2.5 км + спека):", size=10, color=INK))
    p.append(text(lx + lw/2, ly + 260, "• TWR=2.0 падає до 1.40 (межа)", size=10, color=POS, bold=True))
    p.append(text(lx + lw/2, ly + 280, "• Струм росте → нагрів +43%", size=10, color=POS))
    p.append(text(lx + lw/2, ly + 300, "• Час польоту падає на ~35%", size=10, color=POS))

    render(os.path.join(OUT, "thrust-power-vs-density.svg"), W, H, *p, title=None)


# ── 3. high-hot-cooling-trap: подвійна теплова пастка ─────────────────────────
def fig_high_hot_cooling_trap():
    W, H = 940, 460
    p = []

    p.append(text(W / 2, 26, "Подвійна теплова пастка умов «High & Hot»", size=16, color=INK, bold=True))
    p.append(text(W / 2, 46, "Чому розріджене гаряче повітря призводить до лавинного перегріву двигунів та ESC", size=12, color=MUTED))

    # Лівий блок: Генерація тепла
    bx1, by1, bw1, bh1 = 40, 75, 260, 260
    p.append(rect(bx1, by1, bw1, bh1, fill="#fdf2f2", stroke=POS, sw=2, rx=8))
    p.append(text(bx1 + bw1/2, by1 + 25, "1. Зростання виділення тепла", size=13.5, color=POS, bold=True))
    p.append(line(bx1 + 15, by1 + 38, bx1 + bw1 - 15, by1 + 38, color="#fca5a5", sw=1.2))

    p.append(text(bx1 + 15, by1 + 62, "• Менша густина ρ:", size=11, color=INK, anchor="start", bold=True))
    p.append(text(bx1 + 25, by1 + 80, "гвинт захоплює менше маси", size=10.5, color=MUTED, anchor="start"))

    p.append(text(bx1 + 15, by1 + 104, "• Зростання обертів n:", size=11, color=INK, anchor="start", bold=True))
    p.append(text(bx1 + 25, by1 + 122, "n ∝ 1/√(ρ/ρ₀) для тієї ж тяги", size=10.5, color=MUTED, anchor="start"))

    p.append(text(bx1 + 15, by1 + 146, "• Зростання струму I:", size=11, color=POS, anchor="start", bold=True))
    p.append(text(bx1 + 25, by1 + 164, "I ∝ P/U → стрибок струму", size=10.5, color=MUTED, anchor="start"))

    p.append(text(bx1 + 15, by1 + 190, "• Джоулів нагрів обмоток:", size=11, color=POS, anchor="start", bold=True))
    p.append(text(bx1 + 25, by1 + 210, "P_loss = I²·R (+30..+70% тепла!)", size=11, color=POS, anchor="start", bold=True))

    p.append(text(bx1 + bw1/2, by1 + 242, "ВТРАТИ РОСТУТЬ В КВАДРАТІ", size=10, color=POS, bold=True))

    # Правий блок: Деградація охолодження
    bx2, by2, bw2, bh2 = 640, 75, 260, 260
    p.append(rect(bx2, by2, bw2, bh2, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    p.append(text(bx2 + bw2/2, by2 + 25, "2. Падіння тепловідведення", size=13.5, color=NEG, bold=True))
    p.append(line(bx2 + 15, by2 + 38, bx2 + bw2 - 15, by2 + 38, color="#bfdbfe", sw=1.2))

    p.append(text(bx2 + 15, by2 + 62, "• Менша масова витрата:", size=11, color=INK, anchor="start", bold=True))
    p.append(text(bx2 + 25, by2 + 80, "менше кг повітря обдуває мотор", size=10.5, color=MUTED, anchor="start"))

    p.append(text(bx2 + 15, by2 + 104, "• Падіння конвекції h_conv:", size=11, color=INK, anchor="start", bold=True))
    p.append(text(bx2 + 25, by2 + 122, "h_conv ∝ (ρ·v)^0.8 (на −20..−35%)", size=10.5, color=MUTED, anchor="start"))

    p.append(text(bx2 + 15, by2 + 146, "• Менший перепад ΔT:", size=11, color=NEG, anchor="start", bold=True))
    p.append(text(bx2 + 25, by2 + 164, "T_amb = +40 °C замість +15 °C", size=10.5, color=MUTED, anchor="start"))

    p.append(text(bx2 + 15, by2 + 190, "• Падіння об'ємної теплоємності:", size=11, color=NEG, anchor="start", bold=True))
    p.append(text(bx2 + 25, by2 + 210, "C_v = ρ·c_p нижча на 20–30%", size=11, color=NEG, anchor="start", bold=True))

    p.append(text(bx2 + bw2/2, by2 + 242, "ОХОЛОДЖЕННЯ ЕФЕКТИВНО ВПАЛО", size=10, color=NEG, bold=True))

    # Центральний підсумковий блок
    cx, cy, cw, ch = 330, 105, 280, 200
    p.append(rect(cx, cy, cw, ch, fill="#fffbeb", stroke="#d97706", sw=2.5, rx=10))
    p.append(text(cx + cw/2, cy + 28, "РЕЗУЛЬТАТ: ТЕРМО-РОЗГІН", size=13.5, color="#b45309", bold=True))
    p.append(line(cx + 20, cy + 40, cx + cw - 20, cy + 40, color="#fde68a", sw=1.5))

    p.append(text(cx + cw/2, cy + 65, "T_motor підскакує вище 110 °C:", size=11, color=INK, bold=True))
    p.append(text(cx + cw/2, cy + 88, "1. Деградація магнітів NdFeB", size=11, color=POS, bold=True))
    p.append(text(cx + cw/2, cy + 106, "(незворотна втрата магнітного поля)", size=9.5, color=MUTED))
    p.append(text(cx + cw/2, cy + 130, "2. Перегрів MOSFET регулятора", size=11, color=POS, bold=True))
    p.append(text(cx + cw/2, cy + 148, "(R_DS(on) росте → тепловий пробій)", size=9.5, color=MUTED))
    p.append(text(cx + cw/2, cy + 172, "3. Battery Sag & дострокова відсічка", size=10.5, color=INK, bold=True))

    # Стрілки від бічних блоків до центру
    p.append(arrow(bx1 + bw1 + 5, by1 + bh1/2, cx - 5, cy + ch/2, color=POS, sw=2.5))
    p.append(arrow(bx2 - 5, by2 + bh2/2, cx + cw + 5, cy + ch/2, color=NEG, sw=2.5))

    # Нижній висновок
    p.append(rect(40, 360, 860, 75, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=8))
    p.append(text(W / 2, 385, "Інженерне рішення для «High & Hot»:", size=13, color=FIELD, bold=True))
    p.append(text(W / 2, 408, "Зменшення злітної маси на 15–25% • Збільшення діаметра/кроку гвинта з контролем струму ESC", size=11, color=INK))
    p.append(text(W / 2, 426, "Охолодження батарей у тіні перед стартом • Моніторинг температури ESC по телеметрії", size=11, color=INK))

    render(os.path.join(OUT, "high-hot-cooling-trap.svg"), W, H, *p, title=None)


if __name__ == "__main__":
    fig_density_altitude_concept()
    fig_thrust_power_vs_density()
    fig_high_hot_cooling_trap()
    print("SVG generation finished successfully.")
