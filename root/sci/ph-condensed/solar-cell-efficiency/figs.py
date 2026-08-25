# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Extra colors for svgkit palette
WARN   = "#d97706"
ACCENT = "#2563eb"

def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    stroke_dash = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{stroke_dash}/>'

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Дерево оптичних та електронних втрат енергії у сонячному елементі
# ═══════════════════════════════════════════════════════════════════════════
def fig_loss_tree():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Енергетичний баланс та втрати у кремнієвому сонячному елементі (AM1.5G)", 15, INK, 'middle', bold=True))

    # Ліва колона — Вхідна сонячна енергія 100%
    x_in = 40
    y_in = 60
    w_in = 160
    h_in = 320
    f.append(rect(x_in, y_in, w_in, h_in, fill="#fef3c7", stroke=WARN, sw=2, rx=6))
    f.append(text(x_in + w_in/2, y_in + 30, "Вхідний потік", 13, INK, 'middle', bold=True))
    f.append(text(x_in + w_in/2, y_in + 50, "сонячного світла", 13, INK, 'middle', bold=True))
    f.append(text(x_in + w_in/2, y_in + 85, "1000 Вт/м²", 16, WARN, 'middle', bold=True))
    f.append(text(x_in + w_in/2, y_in + 110, "(100% енергії)", 12, MUTED, 'middle'))

    # Середня частина — Блоки втрат
    x_loss = 250
    w_loss = 280

    losses = [
        ("1. Непоглинуті фотони (hν < Eg)", "33%", "#f1f5f9", MUTED, "Проходять крізь кристал"),
        ("2. Термалізація гарячих носіїв (hν > Eg)", "33%", "#ffedd5", NEG, "Перетворюється на тепло"),
        ("3. Оптичне відбиття та затінення", "3%", "#e0f2fe", ACCENT, "Відбиття від поверхні й шин"),
        ("4. Рекомбінація носіїв (SRH, Auger)", "5%", "#f3e8ff", FIELD, "Втрата електронів до збору"),
        ("5. Падіння напруги та контактний опір", "6%", "#fee2e2", NEG, "Омічні втрати Rs та Rsh")
    ]

    y_curr = 60
    h_block = 54
    gap = 12

    for title, val, bg_c, txt_c, desc in losses:
        f.append(rect(x_loss, y_curr, w_loss, h_block, fill=bg_c, stroke=LINE, sw=1.5, rx=4))
        f.append(text(x_loss + 12, y_curr + 22, title, 11, INK, 'start', bold=True))
        f.append(text(x_loss + w_loss - 12, y_curr + 24, val, 13, txt_c, 'end', bold=True))
        f.append(text(x_loss + 12, y_curr + 42, desc, 10, MUTED, 'start'))

        # Стрілки від входу до втрат
        y_mid_loss = y_curr + h_block/2
        f.append(arrow(x_in + w_in, y_mid_loss, x_loss - 2, y_mid_loss, color=LINE, sw=1.5))

        y_curr += h_block + gap

    # Права колона — Корисна електрична потужність
    x_out = 570
    y_out = 60
    w_out = 150
    h_out = 320
    f.append(rect(x_out, y_out, w_out, h_out, fill="#d1fae5", stroke=POS, sw=2, rx=6))
    f.append(text(x_out + w_out/2, y_out + 30, "Корисна", 13, INK, 'middle', bold=True))
    f.append(text(x_out + w_out/2, y_out + 50, "електроенергія", 13, INK, 'middle', bold=True))
    f.append(text(x_out + w_out/2, y_out + 85, "200 Вт/м²", 16, POS, 'middle', bold=True))
    f.append(text(x_out + w_out/2, y_out + 110, "ККД η ≈ 20%", 14, POS, 'middle', bold=True))
    f.append(text(x_out + w_out/2, y_out + 140, "P_max = Voc · Isc · FF", 11, INK, 'middle'))

    # Головна стрілка зв'язку
    f.append(arrow(x_loss + w_loss, y_out + h_out/2, x_out - 2, y_out + h_out/2, color=POS, sw=2.5))

    render(os.path.join(IMG, 'solar-cell-efficiency-loss-tree.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Вольт-амперна (IV) та потужнісна (PV) характеристики
# ═══════════════════════════════════════════════════════════════════════════
def fig_iv_and_power():
    W, H = 720, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Вольт-амперна (IV) та потужнісна (PV) характеристики сонячного елемента", 15, INK, 'middle', bold=True))

    x0, y0 = 80, 340
    pw, ph = 560, 260

    # Осі координат
    f.append(arrow(x0, y0, x0 + pw + 30, y0, color=INK, sw=1.8))
    f.append(text(x0 + pw + 30, y0 + 20, "Напруга V (В)", 12, INK, 'middle', bold=True))

    f.append(arrow(x0, y0, x0, y0 - ph - 20, color=INK, sw=1.8))
    f.append(text(x0 - 45, y0 - ph - 15, "Струм I (А) / Потужність P (Вт)", 11, INK, 'start', bold=True))

    # Параметри точки
    v_oc = pw * 0.85
    i_sc = ph * 0.85

    v_mp = pw * 0.70
    i_mp = ph * 0.72

    # Прямокутник P_max (FF)
    f.append(rect(x0, y0 - i_mp, v_mp, i_mp, fill="#d1fae5", stroke=POS, sw=1.5, rx=0))
    f.append(text(x0 + v_mp/2, y0 - i_mp/2, "P_max = V_mp · I_mp", 13, POS, 'middle', bold=True))

    # Прямокутник Voc * Isc (для порівняння FF)
    f.append(rect(x0, y0 - i_sc, v_oc, i_sc, fill="none", stroke=MUTED, sw=1.2, rx=0))

    # Крива IV: I(V) = I_sc - I_0 * (exp(V/Vt) - 1)
    pts_iv = []
    pts_pv = []
    n_pts = 60
    for i in range(n_pts + 1):
        v_norm = i / float(n_pts)
        v_px = v_norm * v_oc
        # модельльна крива IV
        i_norm = 1.0 - 0.02 * math.exp(v_norm * 4.2)
        if i_norm < 0: i_norm = 0
        i_px = i_norm * i_sc
        pts_iv.append((x0 + v_px, y0 - i_px))

        # крива потужності P = V * I
        p_norm = v_norm * i_norm * 1.4
        p_px = p_norm * ph
        pts_pv.append((x0 + v_px, y0 - p_px))

    # Малювання кривих
    path_iv = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_iv)
    path_pv = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_pv)

    f.append(path(path_iv, fill="none", stroke=ACCENT, sw=3))
    f.append(path(path_pv, fill="none", stroke=WARN, sw=2.5, dash="6 3"))

    # Позначення точок V_oc, I_sc, MPP
    # I_sc
    f.append(circle(x0, y0 - i_sc, 5, fill=ACCENT, stroke=BG, sw=1.5))
    f.append(text(x0 + 12, y0 - i_sc + 4, "I_sc (струм к.з.)", 11, ACCENT, 'start', bold=True))

    # V_oc
    f.append(circle(x0 + v_oc, y0, 5, fill=ACCENT, stroke=BG, sw=1.5))
    f.append(text(x0 + v_oc, y0 + 20, "V_oc (х.х.)", 11, ACCENT, 'middle', bold=True))

    # MPP point
    f.append(circle(x0 + v_mp, y0 - i_mp, 6, fill=POS, stroke=INK, sw=1.5))
    f.append(text(x0 + v_mp + 10, y0 - i_mp - 12, "Точка макс. потужності (MPP)", 12, POS, 'start', bold=True))

    # Пропунктирені лінії від MPP до осей
    f.append(line(x0 + v_mp, y0 - i_mp, x0 + v_mp, y0, color=POS, sw=1.2, dash="3 3"))
    f.append(line(x0 + v_mp, y0 - i_mp, x0, y0 - i_mp, color=POS, sw=1.2, dash="3 3"))

    f.append(text(x0 + v_mp, y0 + 20, "V_mp", 11, POS, 'middle', bold=True))
    f.append(text(x0 - 10, y0 - i_mp + 4, "I_mp", 11, POS, 'end', bold=True))

    # Легенда
    f.append(rect(460, 60, 220, 65, fill="#f8fafc", stroke=LINE, sw=1, rx=4))
    f.append(line(475, 78, 505, 78, color=ACCENT, sw=3))
    f.append(text(515, 82, "Крива струму I(V)", 11, INK, 'start'))
    f.append(line(475, 102, 505, 102, color=WARN, sw=2.5, dash="6 3"))
    f.append(text(515, 106, "Крива потужності P(V)", 11, INK, 'start'))

    # Текст про фактор заповнення FF
    f.append(text(460, 150, "Фактор заповнення:", 11, INK, 'start', bold=True))
    f.append(text(460, 168, "FF = (V_mp · I_mp) / (V_oc · I_sc)", 11, MUTED, 'start'))

    render(os.path.join(IMG, 'iv-and-power-curve.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Границя Шокли-Квіссера
# ═══════════════════════════════════════════════════════════════════════════
def fig_shockley_queisser():
    W, H = 720, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Фундаментальна границя Шокли-Квіссера для одноперехідних елементів", 15, INK, 'middle', bold=True))

    x0, y0 = 80, 330
    pw, ph = 580, 240

    # Осі
    f.append(arrow(x0, y0, x0 + pw + 25, y0, color=INK, sw=1.8))
    f.append(text(x0 + pw + 25, y0 + 20, "Ширина забороненої зони E_g (еВ)", 12, INK, 'middle', bold=True))

    f.append(arrow(x0, y0, x0, y0 - ph - 20, color=INK, sw=1.8))
    f.append(text(x0 - 45, y0 - ph - 15, "Граничний ККД η (%)", 11, INK, 'start', bold=True))

    # Спереду сітка
    for eta_val in [10, 20, 30, 40]:
        y_grid = y0 - (eta_val / 40.0) * ph
        f.append(line(x0, y_grid, x0 + pw, y_grid, color="#f1f5f9", sw=1))
        f.append(text(x0 - 10, y_grid + 4, f"{eta_val}%", 10, MUTED, 'end'))

    # Позиції еВ на осі X (від 0.4 еВ до 2.4 еВ)
    def eg_to_x(eg):
        return x0 + ((eg - 0.4) / 2.0) * pw

    def eta_to_y(eta):
        return y0 - (eta / 40.0) * ph

    # Спектральна крива Шокли-Квіссера для AM1.5G
    sq_data = [
        (0.4, 12.0), (0.6, 21.0), (0.8, 27.5), (1.0, 31.8), (1.12, 32.9),
        (1.34, 33.7), (1.42, 33.5), (1.6, 31.0), (1.8, 26.5), (2.0, 21.5),
        (2.2, 16.5), (2.4, 12.5)
    ]

    pts_sq = []
    for eg, eta in sq_data:
        pts_sq.append((eg_to_x(eg), eta_to_y(eta)))

    path_sq = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_sq)

    # Заповнення області під кривою
    path_fill = path_sq + f" L {eg_to_x(2.4):.1f},{y0:.1f} L {eg_to_x(0.4):.1f},{y0:.1f} Z"
    f.append(path(path_fill, fill="#eff6ff", stroke="none"))
    f.append(path(path_sq, fill="none", stroke=ACCENT, sw=3))

    # Виділення ключових матеріалів
    # Максимум 1.34 еВ
    x_max = eg_to_x(1.34)
    y_max = eta_to_y(33.7)
    f.append(circle(x_max, y_max, 6, fill=WARN, stroke=INK, sw=1.5))
    f.append(line(x_max, y_max, x_max, y0, color=WARN, sw=1.2, dash="3 3"))
    f.append(text(x_max, y_max - 14, "Теоретичний максимум 33.7%", 11, WARN, 'middle', bold=True))

    # Si point
    x_si = eg_to_x(1.12)
    y_si = eta_to_y(32.9)
    f.append(circle(x_si, y_si, 5, fill=POS, stroke=INK, sw=1.5))
    f.append(arrow(x_si - 50, y_si + 35, x_si - 4, y_si + 6, color=POS, sw=1.5))
    f.append(text(x_si - 55, y_si + 45, "Si (1.12 еВ): η_lim = 32.9%", 11, POS, 'end', bold=True))

    # GaAs point
    x_gaas = eg_to_x(1.42)
    y_gaas = eta_to_y(33.5)
    f.append(circle(x_gaas, y_gaas, 5, fill=FIELD, stroke=INK, sw=1.5))
    f.append(arrow(x_gaas + 50, y_gaas + 35, x_gaas + 4, y_gaas + 6, color=FIELD, sw=1.5))
    f.append(text(x_gaas + 55, y_gaas + 45, "GaAs (1.42 еВ): η_lim = 33.5%", 11, FIELD, 'start', bold=True))

    # Написи на осі X для матеріалів
    for eg_val in [0.5, 1.0, 1.5, 2.0]:
        x_val = eg_to_x(eg_val)
        f.append(line(x_val, y0, x_val, y0 + 5, color=INK, sw=1.2))
        f.append(text(x_val, y0 + 20, f"{eg_val}", 11, INK, 'middle'))

    render(os.path.join(IMG, 'shockley-queisser-limit.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Оптична інженерія: текстурування та просвітлення (ARC)
# ═══════════════════════════════════════════════════════════════════════════
def fig_anti_reflective_textures():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Оптичні методи зменшення відбиття та захоплення світла (Light Trapping)", 15, INK, 'middle', bold=True))

    # Ліва панель — Плоска поверхня (велике відбиття ~30%)
    x1, y1 = 40, 60
    w1, h1 = 310, 260
    f.append(rect(x1, y1, w1, h1, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(x1 + w1/2, y1 + 24, "а) Плоска поверхня Si без ARC", 13, INK, 'middle', bold=True))

    # Плоский кристал
    f.append(rect(x1 + 30, y1 + 140, 250, 90, fill="#e2e8f0", stroke=INK, sw=1.5))
    f.append(text(x1 + w1/2, y1 + 185, "Кремнієвий кристал (n = 3.8)", 12, MUTED, 'middle'))

    # Падаючий промінь
    f.append(arrow(x1 + 80, y1 + 50, x1 + 115, y1 + 138, color=WARN, sw=2.5))
    f.append(text(x1 + 65, y1 + 45, "Падаюче світло", 11, WARN, 'end'))

    # Одноразове відбиття 30%
    f.append(arrow(x1 + 115, y1 + 138, x1 + 155, y1 + 55, color=NEG, sw=2.2))
    f.append(text(x1 + 170, y1 + 50, "Відбиття R ≈ 30%", 11, NEG, 'start', bold=True))

    # Заломлений промінь всередину 70%
    f.append(arrow(x1 + 115, y1 + 138, x1 + 125, y1 + 215, color=POS, sw=1.8))
    f.append(text(x1 + 135, y1 + 205, "Поглинання 70%", 10, POS, 'start'))

    # Права панель — Пирамідальне текстурування + ARC + дзеркало
    x2, y2 = 390, 60
    w2, h2 = 310, 260
    f.append(rect(x2, y2, w2, h2, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(x2 + w2/2, y2 + 24, "б) Текстура пірамід + ARC + дзеркало", 13, INK, 'middle', bold=True))

    # Заднє дзеркало
    f.append(rect(x2 + 30, y2 + 225, 250, 10, fill="#cbd5e1", stroke=INK, sw=1.2))
    f.append(text(x2 + w2/2, y2 + 248, "Заднє дзеркальне покриття", 10, MUTED, 'middle'))

    # Кристал з пірамідами зверху
    pyramids_path = f"M {x2+30},{y2+140} L {x2+80},{y2+90} L {x2+130},{y2+140} L {x2+180},{y2+90} L {x2+230},{y2+140} L {x2+280},{y2+140} L {x2+280},{y2+225} L {x2+30},{y2+225} Z"
    f.append(path(pyramids_path, fill="#e2e8f0", stroke=INK, sw=1.5))

    # Рамка під напис Захоплення світла (textbox)
    tb, tw, th = textbox(x2 + 205, y2 + 195, "Захоплення світла", size=10, pad=4, fill="#e2e8f0", stroke="none", color=FIELD, bold=True)
    f.append(tb)

    # Тонке антивідбивальне покриття ARC поверх пірамід (лінія)
    arc_path = f"M {x2+30},{y2+138} L {x2+80},{y2+88} L {x2+130},{y2+138} L {x2+180},{y2+88} L {x2+230},{y2+138} L {x2+280},{y2+138}"
    f.append(path(arc_path, fill="none", stroke=ACCENT, sw=3))

    # Багатократне відбиття в піраміді
    # 1. Падіння на грань піраміди
    f.append(arrow(x2 + 50, y2 + 50, x2 + 65, y2 + 105, color=WARN, sw=2.2))
    # 2. Перше відбиття на сусідню грань
    f.append(arrow(x2 + 65, y2 + 105, x2 + 90, y2 + 115, color=WARN, sw=1.8))
    # 3. Друге заломлення всередину кристала!
    f.append(arrow(x2 + 90, y2 + 115, x2 + 105, y2 + 160, color=POS, sw=1.8))
    # 4. Відбиття від заднього дзеркала
    f.append(arrow(x2 + 105, y2 + 160, x2 + 125, y2 + 225, color=POS, sw=1.5))
    f.append(arrow(x2 + 125, y2 + 225, x2 + 145, y2 + 175, color=POS, sw=1.5))

    f.append(text(x2 + 225, y2 + 105, "R < 1.5%", 11, POS, 'start', bold=True))
    f.append(text(x2 + 180, y2 + 68, "Покриття SiN_x (ARC)", 10, ACCENT, 'start'))

    render(os.path.join(IMG, 'anti-reflective-textures.svg'), W, H, *f)

if __name__ == '__main__':
    fig_loss_tree()
    fig_iv_and_power()
    fig_shockley_queisser()
    fig_anti_reflective_textures()
    print("Figures generated successfully!")
