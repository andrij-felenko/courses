# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова гама за змістом
CLR_BASE = FIELD       # Зелений — низькочастотний сигнал (baseband)
CLR_PASS = NEG         # Синій — смуговий сигнал (passband)
CLR_I    = "#d97706"   # Помаранчевий — In-phase I(t)
CLR_Q    = "#9333ea"   # Фіолетовий — Quadrature Q(t)
CLR_NOISE= POS         # Червоний — акцент / шум / зсув
CLR_TEXT = INK         # Основний текст
CLR_MUTED= MUTED       # Вторинний текст

def polyline(pts, color, sw=2.0, fill="none"):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, color, sw)

def path(pts, color, sw=2.0, fill="none", dash=None):
    d = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, color, sw, da)

# ════════════════════════════════════════════════════════════════════════════
# 1. Фігура: Спектральне порівняння Baseband проти Passband
# ════════════════════════════════════════════════════════════════════════════

def fig_baseband_vs_passband_spectrum():
    W, H = 760, 380
    p = []

    # Верхній спектр: Baseband біля 0 Гц
    y_base = 150
    x_zero_b = 200
    p.append(line(50, y_base, 710, y_base, color=CLR_TEXT, sw=1.5))
    p.append(arrow(690, y_base, 710, y_base, color=CLR_TEXT, sw=1.5))
    p.append(text(715, y_base + 15, "f", size=13, color=CLR_TEXT, italic=True, anchor="start"))
    
    # Вертикальна вісь 0 Гц
    p.append(line(x_zero_b, y_base, x_zero_b, 75, color=CLR_MUTED, sw=1.0, dash="4,4"))
    p.append(text(x_zero_b, y_base + 18, "0", size=12, color=CLR_TEXT, bold=True))
    
    # Спектр Baseband (трикутник від -B до +B)
    bw = 70
    bh = 80
    pts_b = [
        (x_zero_b - bw, y_base),
        (x_zero_b, y_base - bh),
        (x_zero_b + bw, y_base)
    ]
    p.append(path(pts_b, color=CLR_BASE, sw=2.5, fill="#eef6ef"))
    p.append(text(x_zero_b, 55, "M(f)", size=12, color=CLR_BASE, bold=True))
    p.append(text(x_zero_b - bw, y_base + 18, "-B", size=11, color=CLR_MUTED))
    p.append(text(x_zero_b + bw, y_base + 18, "+B", size=11, color=CLR_MUTED))

    p.append(text(70, 50, "Низькочастотний сигнал (Baseband)", size=14, color=CLR_BASE, bold=True, anchor="start"))
    p.append(text(70, 70, "Енергія зосереджена біля 0 Гц: від 0 до B", size=11, color=CLR_MUTED, anchor="start"))

    # Нижній спектр: Passband біля fc
    y_pass = 310
    x_fc_pos = 520
    x_fc_neg = 200  # Для симетричної від'ємної частоти
    p.append(line(50, y_pass, 710, y_pass, color=CLR_TEXT, sw=1.5))
    p.append(arrow(690, y_pass, 710, y_pass, color=CLR_TEXT, sw=1.5))
    p.append(text(715, y_pass + 15, "f", size=13, color=CLR_TEXT, italic=True, anchor="start"))

    # Вісь 0 Гц для порівняння
    p.append(line(x_zero_b, y_pass, x_zero_b, 250, color=CLR_MUTED, sw=1.0, dash="4,4"))
    p.append(text(x_zero_b, y_pass + 18, "0", size=12, color=CLR_MUTED))

    # Спектр у додатній області навколо +fc
    pts_p_pos = [
        (x_fc_pos - bw, y_pass),
        (x_fc_pos, y_pass - bh/2),
        (x_fc_pos + bw, y_pass)
    ]
    p.append(path(pts_p_pos, color=CLR_PASS, sw=2.5, fill="#e8f0fe"))
    p.append(line(x_fc_pos, y_pass, x_fc_pos, y_pass - bh/2, color=CLR_PASS, sw=1.0, dash="3,3"))
    p.append(text(x_fc_pos, y_pass + 18, "+f_c", size=12, color=CLR_PASS, bold=True))
    p.append(text(x_fc_pos - bw, y_pass + 18, "f_c - B", size=10, color=CLR_MUTED))
    p.append(text(x_fc_pos + bw, y_pass + 18, "f_c + B", size=10, color=CLR_MUTED))

    # Спрощена стрілка переносу спектра
    p.append(path([(x_zero_b + 20, y_base + 30), (350, 215), (x_fc_pos - 30, y_pass - bh/2 - 10)], color=CLR_PASS, sw=1.8, dash="4,4"))
    p.append(arrow(x_fc_pos - 40, y_pass - bh/2 - 15, x_fc_pos - 30, y_pass - bh/2 - 10, color=CLR_PASS, sw=1.8))
    p.append(text(370, 205, "Модуляція (Up-conversion): зсув на f_c", size=11, color=CLR_PASS, bold=True, anchor="start"))

    p.append(text(70, 210, "Смуговий сигнал (Passband)", size=14, color=CLR_PASS, bold=True, anchor="start"))
    p.append(text(70, 230, "Ширина смуги 2B навколо несучої частоти f_c", size=11, color=CLR_MUTED, anchor="start"))

    # Описовий блок під фігурою
    b, bw_box, bh_box = textbox(W / 2, 360, "Низькочастотний спектр M(f) зсувається на частоту несучої f_c. Смуговий сигнал займає смугу 2B.",
                                size=11, color=CLR_TEXT, fill="#f8fafc", stroke=CLR_MUTED, min_w=W - 100)
    p.append(b)

    render(os.path.join(OUT, "baseband-vs-passband-spectrum.svg"), W, H, *p,
           title="Спектральне перетворення Baseband у Passband")


# ════════════════════════════════════════════════════════════════════════════
# 2. Фігура: Квадратурний вектор I/Q та комплексне представлення
# ════════════════════════════════════════════════════════════════════════════

def fig_quadrature_representation():
    W, H = 760, 400
    p = []

    # Ліва частина: Вектор на квадратурній площині I-Q
    cx, cy = 200, 200
    r = 120

    # Осі I та Q
    p.append(line(cx - r - 20, cy, cx + r + 30, cy, color=CLR_TEXT, sw=1.5))
    p.append(arrow(cx + r + 15, cy, cx + r + 30, cy, color=CLR_TEXT, sw=1.5))
    p.append(text(cx + r + 38, cy + 5, "I (In-phase)", size=12, color=CLR_I, bold=True, anchor="start"))

    p.append(line(cx, cy + r + 20, cx, cy - r - 30, color=CLR_TEXT, sw=1.5))
    p.append(arrow(cx, cy - r - 15, cx, cy - r - 30, color=CLR_TEXT, sw=1.5))
    p.append(text(cx, cy - r - 38, "Q (Quadrature)", size=12, color=CLR_Q, bold=True))

    # Вектор комплексного сигналу s_l(t) = I + jQ
    vx, vy = cx + 85, cy - 75
    p.append(line(cx, cy, vx, vy, color=CLR_PASS, sw=3.0))
    p.append(arrow(cx + 70, cy - 61.7, vx, vy, color=CLR_PASS, sw=3.0))
    p.append(circle(vx, vy, 4, fill=CLR_PASS, stroke=CLR_PASS))

    # Проекції I та Q
    p.append(line(vx, vy, vx, cy, color=CLR_Q, sw=1.5, dash="4,4"))
    p.append(line(vx, vy, cx, vy, color=CLR_I, sw=1.5, dash="4,4"))

    p.append(line(cx, cy, vx, cy, color=CLR_I, sw=2.5))
    p.append(line(cx, cy, cx, vy, color=CLR_Q, sw=2.5))

    p.append(text(vx / 2 + cx / 2, cy + 18, "I(t)", size=12, color=CLR_I, bold=True))
    p.append(text(cx - 20, vy / 2 + cy / 2, "Q(t)", size=12, color=CLR_Q, bold=True))

    # Кут фази phi
    p.append(path([(cx + 35, cy), (cx + 33, cy - 15), (cx + 26, cy - 23)], color=CLR_TEXT, sw=1.2))
    p.append(text(cx + 45, cy - 12, "φ(t)", size=11, color=CLR_TEXT, italic=True))

    # Довжина вектора A(t)
    p.append(text((cx + vx)/2 - 10, (cy + vy)/2 - 15, "A(t)", size=12, color=CLR_PASS, bold=True))

    # Права частина: Математична відповідність
    rx = 440
    p.append(rect(rx, 40, 290, 300, fill="#f8fafc", stroke=CLR_MUTED, sw=1.2, rx=8))
    p.append(text(rx + 145, 65, "Математичний зв'язок", size=14, color=CLR_TEXT, bold=True))

    p.append(text(rx + 20, 105, "Комплексна огинаюча (Baseband):", size=11, color=CLR_MUTED, anchor="start"))
    p.append(text(rx + 20, 128, "s_l(t) = I(t) + j·Q(t)", size=13, color=CLR_BASE, bold=True, anchor="start"))

    p.append(text(rx + 20, 160, "Огинаюча та миттєва фаза:", size=11, color=CLR_MUTED, anchor="start"))
    p.append(text(rx + 20, 182, "A(t) = √( I²(t) + Q²(t) )", size=12, color=CLR_PASS, bold=True, anchor="start"))
    p.append(text(rx + 20, 205, "φ(t) = arctan( Q(t) / I(t) )", size=12, color=CLR_PASS, bold=True, anchor="start"))

    p.append(text(rx + 20, 240, "Фізичний смуговий сигнал (Passband):", size=11, color=CLR_MUTED, anchor="start"))
    p.append(text(rx + 20, 265, "s(t) = Re{ s_l(t) · e^{j·2π·f_c·t} }", size=12, color=CLR_TEXT, bold=True, anchor="start"))
    p.append(text(rx + 20, 290, "= I(t)·cos(2π f_c t) - Q(t)·sin(2π f_c t)", size=11, color=CLR_TEXT, bold=True, anchor="start"))

    render(os.path.join(OUT, "quadrature-representation.svg"), W, H, *p,
           title="Квадратурна площина та огинаюча A(t), фаза φ(t)")


# ════════════════════════════════════════════════════════════════════════════
# 3. Фігура: Блок-схема Up-conversion та Down-conversion
# ════════════════════════════════════════════════════════════════════════════

def fig_up_down_conversion_chain():
    W, H = 760, 420
    p = []

    # Верхня частина: Передавач (Up-conversion)
    p.append(text(60, 35, "Передавач: Up-conversion (Baseband → Passband)", size=13, color=CLR_PASS, bold=True, anchor="start"))

    # Входи I(t) та Q(t)
    p.append(text(60, 70, "I(t)", size=12, color=CLR_I, bold=True, anchor="start"))
    p.append(line(85, 70, 140, 70, color=CLR_I, sw=2.0))
    p.append(arrow(125, 70, 140, 70, color=CLR_I, sw=2.0))

    p.append(text(60, 150, "Q(t)", size=12, color=CLR_Q, bold=True, anchor="start"))
    p.append(line(85, 150, 140, 150, color=CLR_Q, sw=2.0))
    p.append(arrow(125, 150, 140, 150, color=CLR_Q, sw=2.0))

    # Змішувачі (помножувачі)
    # Змішувач I
    p.append(circle(160, 70, 18, fill="#fff", stroke=CLR_TEXT, sw=1.8))
    p.append(line(148, 58, 172, 82, color=CLR_TEXT, sw=1.8))
    p.append(line(148, 82, 172, 58, color=CLR_TEXT, sw=1.8))

    # Змішувач Q
    p.append(circle(160, 150, 18, fill="#fff", stroke=CLR_TEXT, sw=1.8))
    p.append(line(148, 138, 172, 162, color=CLR_TEXT, sw=1.8))
    p.append(line(148, 162, 172, 138, color=CLR_TEXT, sw=1.8))

    # Локальний гетеродин (LO)
    p.append(rect(220, 95, 75, 30, fill="#e2e8f0", stroke=CLR_TEXT, sw=1.5, rx=4))
    p.append(text(257, 114, "LO (f_c)", size=11, color=CLR_TEXT, bold=True))

    # Сигнали cos та -sin від гетеродина до змішувачів
    p.append(line(257, 95, 257, 70, color=CLR_TEXT, sw=1.5))
    p.append(line(257, 70, 178, 70, color=CLR_TEXT, sw=1.5))
    p.append(arrow(190, 70, 178, 70, color=CLR_TEXT, sw=1.5))
    p.append(text(215, 62, "cos(2π f_c t)", size=10, color=CLR_MUTED))

    p.append(line(257, 125, 257, 150, color=CLR_TEXT, sw=1.5))
    p.append(line(257, 150, 178, 150, color=CLR_TEXT, sw=1.5))
    p.append(arrow(190, 150, 178, 150, color=CLR_TEXT, sw=1.5))
    p.append(text(215, 163, "-sin(2π f_c t)", size=10, color=CLR_MUTED))

    # Виходи з змішувачів до суматора
    p.append(line(178, 70, 335, 70, color=CLR_TEXT, sw=1.5))
    p.append(line(335, 70, 335, 95, color=CLR_TEXT, sw=1.5))
    p.append(arrow(335, 85, 335, 95, color=CLR_TEXT, sw=1.5))

    p.append(line(178, 150, 335, 150, color=CLR_TEXT, sw=1.5))
    p.append(line(335, 150, 335, 125, color=CLR_TEXT, sw=1.5))
    p.append(arrow(335, 135, 335, 125, color=CLR_TEXT, sw=1.5))

    # Суматор (+)
    p.append(circle(335, 110, 15, fill="#fff", stroke=CLR_TEXT, sw=1.8))
    p.append(line(327, 110, 343, 110, color=CLR_TEXT, sw=1.8))
    p.append(line(335, 102, 335, 118, color=CLR_TEXT, sw=1.8))

    # Вихідний Passband сигнал s(t)
    p.append(line(350, 110, 440, 110, color=CLR_PASS, sw=2.5))
    p.append(arrow(425, 110, 440, 110, color=CLR_PASS, sw=2.5))
    p.append(text(450, 114, "s(t) Passband", size=12, color=CLR_PASS, bold=True, anchor="start"))


    # Нижня частина: Приймач (Down-conversion)
    y_dn = 240
    p.append(text(60, y_dn - 15, "Приймач: Down-conversion (Passband → Baseband)", size=13, color=CLR_BASE, bold=True, anchor="start"))

    # Вхідний Passband сигнал s(t)
    p.append(text(60, y_dn + 45, "s(t)", size=12, color=CLR_PASS, bold=True, anchor="start"))
    p.append(line(85, y_dn + 45, 140, y_dn + 45, color=CLR_PASS, sw=2.0))
    p.append(arrow(125, y_dn + 45, 140, y_dn + 45, color=CLR_PASS, sw=2.0))

    # Розгалуження входу на I та Q плечі
    p.append(circle(140, y_dn + 45, 3, fill=CLR_PASS, stroke=CLR_PASS))
    p.append(line(140, y_dn + 45, 140, y_dn + 10, color=CLR_PASS, sw=1.8))
    p.append(line(140, y_dn + 10, 180, y_dn + 10, color=CLR_PASS, sw=1.8))
    p.append(arrow(165, y_dn + 10, 180, y_dn + 10, color=CLR_PASS, sw=1.8))

    p.append(line(140, y_dn + 45, 140, y_dn + 80, color=CLR_PASS, sw=1.8))
    p.append(line(140, y_dn + 80, 180, y_dn + 80, color=CLR_PASS, sw=1.8))
    p.append(arrow(165, y_dn + 80, 180, y_dn + 80, color=CLR_PASS, sw=1.8))

    # Демодуляційні змішувачі
    p.append(circle(195, y_dn + 10, 15, fill="#fff", stroke=CLR_TEXT, sw=1.8))
    p.append(line(185, y_dn, 205, y_dn + 20, color=CLR_TEXT, sw=1.8))
    p.append(line(185, y_dn + 20, 205, y_dn, color=CLR_TEXT, sw=1.8))

    p.append(circle(195, y_dn + 80, 15, fill="#fff", stroke=CLR_TEXT, sw=1.8))
    p.append(line(185, y_dn + 70, 205, y_dn + 90, color=CLR_TEXT, sw=1.8))
    p.append(line(185, y_dn + 90, 205, y_dn + 70, color=CLR_TEXT, sw=1.8))

    # ФНЧ (Low-Pass Filter)
    p.append(rect(260, y_dn - 5, 60, 30, fill="#e2e8f0", stroke=CLR_TEXT, sw=1.5, rx=4))
    p.append(text(290, y_dn + 14, "ФНЧ", size=11, color=CLR_TEXT, bold=True))

    p.append(rect(260, y_dn + 65, 60, 30, fill="#e2e8f0", stroke=CLR_TEXT, sw=1.5, rx=4))
    p.append(text(290, y_dn + 84, "ФНЧ", size=11, color=CLR_TEXT, bold=True))

    # Лінії від змішувачів до ФНЧ
    p.append(line(210, y_dn + 10, 260, y_dn + 10, color=CLR_TEXT, sw=1.5))
    p.append(arrow(245, y_dn + 10, 260, y_dn + 10, color=CLR_TEXT, sw=1.5))

    p.append(line(210, y_dn + 80, 260, y_dn + 80, color=CLR_TEXT, sw=1.5))
    p.append(arrow(245, y_dn + 80, 260, y_dn + 80, color=CLR_TEXT, sw=1.5))

    # Відновлені I(t) та Q(t)
    p.append(line(320, y_dn + 10, 390, y_dn + 10, color=CLR_I, sw=2.0))
    p.append(arrow(375, y_dn + 10, 390, y_dn + 10, color=CLR_I, sw=2.0))
    p.append(text(400, y_dn + 14, "I(t) відновлений", size=11, color=CLR_I, bold=True, anchor="start"))

    p.append(line(320, y_dn + 80, 390, y_dn + 80, color=CLR_Q, sw=2.0))
    p.append(arrow(375, y_dn + 80, 390, y_dn + 80, color=CLR_Q, sw=2.0))
    p.append(text(400, y_dn + 84, "Q(t) відновлений", size=11, color=CLR_Q, bold=True, anchor="start"))

    render(os.path.join(OUT, "up-down-conversion-chain.svg"), W, H, *p,
           title="Блок-схема квадратурного перенесення частоти Up/Down Conversion")


if __name__ == "__main__":
    fig_baseband_vs_passband_spectrum()
    fig_quadrature_representation()
    fig_up_down_conversion_chain()
    print("Всі 3 фігури успішно згенеровано у ./img/")
