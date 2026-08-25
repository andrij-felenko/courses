# -*- coding: utf-8 -*-
"""Фігури до теми «Параболічна антена».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки
WAVE = "#c0392b"       # випромінювання / хвильовий фронт
WAVE_REF = "#2457d6"   # відбита паралельна хвиля
ACCENT_BG = "#eaf2fd"  # панель підкреслення

def path(d, fill="none", color=None, stroke=LINE, sw=1.5):
    strk = color if color else stroke
    return f'<path d="{d}" fill="{fill}" stroke="{strk}" stroke-width="{sw:.1f}"/>'

# ── 1. Геометрія параболи та рівність оптичних шляхів ───────────────────────
def fig_parabola_focus():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke="none")]
    f.append(text(W / 2, 28, "Параболічний рефлектор: перетворення сферичного фронту на плоский", size=16, bold=True))

    foc_x, foc_y = 200, 210  # Фокус F
    f_len = 120              # focal length f
    vertex_x = foc_x - f_len # вершина V (80, 210)
    
    # Побудова параболи x = vertex_x + (y - foc_y)^2 / (4 * f_len)
    parabola_pts = []
    for y_val in range(40, 381, 4):
        dy = y_val - foc_y
        x_val = vertex_x + (dy * dy) / (4.0 * f_len)
        parabola_pts.append(f"{x_val:.1f},{y_val:.1f}")
    
    # Лист параболоїда (товста лінія)
    f.append(f'<polyline points="{" ".join(parabola_pts)}" fill="none" stroke="{INK}" stroke-width="4.0"/>')

    # Оптична вісь (пунктир)
    f.append(line(40, foc_y, 720, foc_y, color=MUTED, sw=1.5, dash="6,4"))
    f.append(text(680, foc_y - 10, "Оптична вісь Z", size=11, color=MUTED))

    # Площина апертури / плоский фазовий фронт (вертикальна лінія)
    aperture_x = 580
    f.append(line(aperture_x, 40, aperture_x, 380, color=WAVE_REF, sw=3.0))
    f.append(text(aperture_x, 30, "Площина апертури (плоский фазовий фронт)", size=12, color=WAVE_REF, bold=True, anchor="middle"))

    # Фокус F (опромінювач)
    f.append(circle(foc_x, foc_y, 6, fill=WAVE, stroke=INK, sw=1.5))
    tb_foc, _, _ = textbox(foc_x + 85, foc_y + 35, "Фокус F (опромінювач)", size=11, pad=5, fill=FILL, stroke=LINE, color=WAVE, bold=True)
    f.append(tb_foc)

    # Промені від фокуса до параболи та відбиття
    y_targets = [70, 120, 210, 300, 350]
    for y_t in y_targets:
        dy = y_t - foc_y
        px = vertex_x + (dy * dy) / (4.0 * f_len)
        py = y_t
        # Промінь F -> P
        f.append(line(foc_x, foc_y, px, py, color=WAVE, sw=1.8))
        # Стрілка на падаючому промені
        mx, my = (foc_x + px) / 2, (foc_y + py) / 2
        if px != foc_x or py != foc_y:
            f.append(line(foc_x, foc_y, mx, my, color=WAVE, sw=1.8))
        # Промінь P -> Апертура
        f.append(arrow(px, py, aperture_x, py, color=WAVE_REF, sw=2.0))

    # Риски однакової фази на відбитому фронті
    for x_phase in [400, 490, 580]:
        f.append(line(x_phase, 55, x_phase, 365, color=WAVE_REF, sw=1.2, dash="3,3"))

    # Підпис рівності шляхів
    tb, _, _ = textbox(440, 385, "Оптичний шлях L1 + L2 = const для всіх променів → сумарна фаза однакова!",
                       size=12, pad=8, fill=ACCENT_BG, stroke=WAVE_REF, color=INK, bold=True)
    f.append(tb)

    render(os.path.join(IMG, "parabola-focus.svg"), W, H, *f)


# ── 2. Конфігурації живлення: прямофокусна, офсетна, Кассегрена, Грегорі ───
def fig_feed_geometries():
    W, H = 760, 480
    f = [rect(0, 0, W, H, fill=BG, stroke="none")]
    f.append(text(W / 2, 24, "Основні конфігурації параболічних антен", size=16, bold=True))

    # 4 блоки у сітці 2x2
    configs = [
        (190, 130, "Прямофокусна (Prime Focus)", "Опромінювач у фокусі.\nПрисутнє затінення апертури."),
        (570, 130, "Офсетна (Offset Feed)", "Виріз збоку від осі.\nНемає затінення променя."),
        (190, 360, "Двозеркальна Кассегрена", "Гіперболічний субрефлектор.\nКороткий хвилевід живлення."),
        (570, 360, "Двозеркальна Грегорі", "Еліптичний субрефлектор.\nНизький рівень шуму."),
    ]

    for cx, cy, title, desc in configs:
        # Рамка для кожного типу
        f.append(rect(cx - 175, cy - 100, 350, 200, fill=FILL, stroke=LINE, sw=1.2, rx=8))
        f.append(text(cx, cy - 80, title, size=13, bold=True, color=INK))
        
        # Мініатюрні схеми
        if "Прямофокусна" in title:
            # Дзеркало
            f.append(path("M %d %d Q %d %d %d %d" % (cx - 100, cy - 40, cx - 130, cy, cx - 100, cy + 40), color=INK, sw=3))
            # Фокус та опромінювач
            f.append(circle(cx - 30, cy, 5, fill=WAVE, stroke=INK, sw=1))
            # Спиці тримача
            f.append(line(cx - 100, cy - 35, cx - 30, cy, color=MUTED, sw=1.2))
            f.append(line(cx - 100, cy + 35, cx - 30, cy, color=MUTED, sw=1.2))
            # Промені
            f.append(line(cx - 30, cy, cx - 115, cy - 25, color=WAVE, sw=1.2))
            f.append(arrow(cx - 115, cy - 25, cx + 50, cy - 25, color=WAVE_REF, sw=1.2))
            f.append(line(cx - 30, cy, cx - 115, cy + 25, color=WAVE, sw=1.2))
            f.append(arrow(cx - 115, cy + 25, cx + 50, cy + 25, color=WAVE_REF, sw=1.2))
        elif "Офсетна" in title:
            # Верхня асиметрична частина параболи
            f.append(path("M %d %d Q %d %d %d %d" % (cx - 110, cy - 50, cx - 130, cy - 10, cx - 100, cy + 30), color=INK, sw=3))
            # Опромінювач знизу поза променем
            f.append(circle(cx - 40, cy + 50, 5, fill=WAVE, stroke=INK, sw=1))
            # Промені (не затінюються)
            f.append(line(cx - 40, cy + 50, cx - 120, cy - 30, color=WAVE, sw=1.2))
            f.append(arrow(cx - 120, cy - 30, cx + 50, cy - 30, color=WAVE_REF, sw=1.2))
            f.append(line(cx - 40, cy + 50, cx - 105, cy + 20, color=WAVE, sw=1.2))
            f.append(arrow(cx - 105, cy + 20, cx + 50, cy + 20, color=WAVE_REF, sw=1.2))
        elif "Кассегрена" in title:
            # Головне дзеркало
            f.append(path("M %d %d Q %d %d %d %d" % (cx - 100, cy - 40, cx - 130, cy, cx - 100, cy + 40), color=INK, sw=3))
            # Опромінювач у вершині
            f.append(circle(cx - 125, cy, 5, fill=WAVE, stroke=INK, sw=1))
            # Субрефлектор (опуклий гіперболоїд)
            f.append(path("M %d %d Q %d %d %d %d" % (cx - 45, cy - 15, cx - 40, cy, cx - 45, cy + 15), color=INK, sw=2.5))
            # Промені
            f.append(line(cx - 125, cy, cx - 42, cy - 10, color=WAVE, sw=1.2))
            f.append(line(cx - 42, cy - 10, cx - 110, cy - 30, color=WAVE, sw=1.2))
            f.append(arrow(cx - 110, cy - 30, cx + 50, cy - 30, color=WAVE_REF, sw=1.2))
        else: # Грегорі
            # Головне дзеркало
            f.append(path("M %d %d Q %d %d %d %d" % (cx - 100, cy - 40, cx - 130, cy, cx - 100, cy + 40), color=INK, sw=3))
            # Опромінювач у вершині
            f.append(circle(cx - 125, cy, 5, fill=WAVE, stroke=INK, sw=1))
            # Субрефлектор (угнутий еліпсоїд за фокусом)
            f.append(path("M %d %d Q %d %d %d %d" % (cx - 35, cy - 15, cx - 40, cy, cx - 35, cy + 15), color=INK, sw=2.5))
            # Промені
            f.append(line(cx - 125, cy, cx - 37, cy - 10, color=WAVE, sw=1.2))
            f.append(line(cx - 37, cy - 10, cx - 110, cy - 30, color=WAVE, sw=1.2))
            f.append(arrow(cx - 110, cy - 30, cx + 50, cy - 30, color=WAVE_REF, sw=1.2))

        # Опис під схемою
        f.append(mtext(cx, cy + 65, desc, size=11, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, "feed-geometries.svg"), W, H, *f)


# ── 3. Компроміс між спаданням опромінення та переливанням енергії ─────────
def fig_illumination_taper():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke="none")]
    f.append(text(W / 2, 26, "Компроміс опромінювання: спадання (Taper) проти переливання (Spillover)", size=16, bold=True))

    # Схема параболічного дзеркала та діаграми випромінювання опромінювача
    cx, cy = 220, 190
    # Дзеркало
    f.append(path("M %d %d Q %d %d %d %d" % (cx + 120, cy - 130, cx, cy, cx + 120, cy + 130), color=INK, sw=3.5))
    f.append(text(cx + 140, cy, "Рефлектор", size=12, color=INK, bold=True))

    # Опромінювач у фокусі
    foc_x = cx + 80
    f.append(circle(foc_x, cy, 6, fill=WAVE, stroke=INK, sw=1.5))
    tb_feed, _, _ = textbox(foc_x + 10, cy + 45, "Опромінювач", size=11, pad=5, fill=FILL, stroke=LINE, color=WAVE, bold=True)
    f.append(tb_feed)

    # Діаграма опромінювача (пелюстка в бік дзеркала)
    # Частина енергії влучає в дзеркало, частина вилітає за краї (Spillover)
    f.append(path("M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d Z" %
                  (foc_x, cy, foc_x - 50, cy - 80, cx + 110, cy - 150, cx + 130, cy - 155,
                   cx + 110, cy + 150, foc_x - 50, cy + 80, foc_x, cy),
                  fill="#fdecea", stroke=POS, sw=1.8))

    # Затінені області переливання (Spillover)
    f.append(text(foc_x + 60, cy - 145, "Переливання (Spillover)", size=11, color=POS, bold=True))
    f.append(arrow(foc_x + 50, cy - 135, cx + 135, cy - 165, color=POS, sw=1.5))
    f.append(arrow(foc_x + 50, cy + 135, cx + 135, cy + 165, color=POS, sw=1.5))

    # Графік залежності ефективностей від спадання на краю (Edge Taper)
    gx0, gy0 = 460, 280
    gw, gh = 250, 200
    f.append(line(gx0, gy0, gx0 + gw, gy0, color=INK, sw=1.8))
    f.append(line(gx0, gy0, gx0, gy0 - gh, color=INK, sw=1.8))
    f.append(text(gx0 + gw / 2, gy0 + 35, "Спадання на краю (Edge Taper, dB)", size=11, bold=True))
    f.append(text(gx0 - 30, gy0 - gh / 2, "Ефективність η", size=11, bold=True))

    # Криві: η_i (згасає), η_s (росте), η_total (максимум при -10...-12 dB)
    pts_i, pts_s, pts_tot = [], [], []
    for step in range(21):
        t = step / 20.0
        db = t * 20.0 # 0..20 dB
        x = gx0 + t * gw
        # η_i: від 1.0 до 0.55
        eta_i = 1.0 - 0.45 * (t ** 1.2)
        # η_s: від 0.5 до 0.98
        eta_s = 0.5 + 0.48 * (1.0 - (1.0 - t) ** 2)
        # η_tot = η_i * η_s
        eta_tot = eta_i * eta_s

        pts_i.append(f"{x:.1f},{gy0 - eta_i * gh * 0.9:.1f}")
        pts_s.append(f"{x:.1f},{gy0 - eta_s * gh * 0.9:.1f}")
        pts_tot.append(f"{x:.1f},{gy0 - eta_tot * gh * 0.9:.1f}")

    f.append(f'<polyline points="{" ".join(pts_i)}" fill="none" stroke="{MUTED}" stroke-width="1.8" stroke-dasharray="4,3"/>')
    f.append(f'<polyline points="{" ".join(pts_s)}" fill="none" stroke="{POS}" stroke-width="1.8" stroke-dasharray="4,3"/>')
    f.append(f'<polyline points="{" ".join(pts_tot)}" fill="none" stroke="{FIELD}" stroke-width="3.0"/>')

    # Підписи кривих
    f.append(text(gx0 + 40, gy0 - 180, "η_s (переливання)", size=10, color=POS, bold=True))
    f.append(text(gx0 + 170, gy0 - 120, "η_i (апертурна)", size=10, color=MUTED, bold=True))
    f.append(text(gx0 + 110, gy0 - 150, "Оптимум η_заг ≈ 65-75%", size=11, color=FIELD, bold=True))

    # Вертикальна пунктирна лінія оптимуму (-10..-12 dB)
    opt_x = gx0 + (11.0 / 20.0) * gw
    f.append(line(opt_x, gy0, opt_x, gy0 - gh, color=FIELD, sw=1.5, dash="4,4"))
    f.append(text(opt_x, gy0 + 16, "-11 dB", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG, "illumination-taper.svg"), W, H, *f)


# ── 4. Діаграма спрямованості та рівні бічних пелюсток ──────────────────────
def fig_radiation_pattern_sidelobes():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke="none")]
    f.append(text(W / 2, 26, "Діаграма спрямованості параболічної антени (децибельна шкала)", size=16, bold=True))

    cx0, cy0 = W / 2, 310
    gw, gh = 660, 240
    gx0 = cx0 - gw / 2

    # Вісі координат
    f.append(line(gx0, cy0, gx0 + gw, cy0, color=INK, sw=1.8))
    f.append(line(cx0, cy0, cx0, cy0 - gh - 20, color=INK, sw=1.8))
    f.append(text(cx0 + 10, cy0 - gh - 10, "Підсилення (dBi)", size=11, bold=True))
    f.append(text(gx0 + gw - 40, cy0 + 20, "Кут θ (°)", size=11, bold=True))

    # Головна пелюстка та бічні пелюстки (функція |2*J1(x)/x|^2 у дБ)
    pattern_pts = []
    for i in range(201):
        t = (i - 100) / 100.0  # -1..+1
        angle_deg = t * 15.0   # -15..+15 deg
        u = math.pi * 1.2 * math.sin(math.radians(angle_deg)) * 8.0
        if abs(u) < 1e-4:
            val_linear = 1.0
        else:
            # наближення Bessel J1(u)/u
            j1 = math.sin(u) / (u * u) - math.cos(u) / u if abs(u) > 0.1 else 0.5 * u
            val_linear = abs(2.0 * j1 / u)
        
        db_val = 20.0 * math.log10(max(val_linear, 1e-3)) # floor -30 dB
        # Нормалізація на графіку: 0 dB = cy0 - gh, -30 dB = cy0
        y_graph = cy0 - (db_val + 30.0) / 30.0 * gh
        x_graph = cx0 + t * (gw / 2)
        pattern_pts.append(f"{x_graph:.1f},{y_graph:.1f}")

    f.append(f'<polyline points="{" ".join(pattern_pts)}" fill="none" stroke="{WAVE_REF}" stroke-width="2.5"/>')

    # Рівень -3 dB (ширина променя HPBW)
    y_3db = cy0 - 27.0 / 30.0 * gh
    f.append(line(cx0 - 35, y_3db, cx0 + 35, y_3db, color=POS, sw=2.0))
    f.append(text(cx0, y_3db - 8, "HPBW (θ_3dB)", size=11, color=POS, bold=True))

    # Перша бічна пелюстка (-13.2 dB до -25 dB залежно від спадання)
    y_side = cy0 - 16.8 / 30.0 * gh
    f.append(line(cx0 + 40, y_side, cx0 + 130, y_side, color=MUTED, sw=1.5, dash="3,3"))
    f.append(text(cx0 + 140, y_side + 4, "Перша бічна пелюстка (-17…-25 dB)", size=11, color=MUTED, bold=True, anchor="start"))

    # Задній промінь (Backlobe)
    f.append(text(gx0 + 50, cy0 - 30, "Задня пелюстка (Backlobe)", size=11, color=MUTED))

    # Текстовий блок параметрів
    tb, _, _ = textbox(150, 100, "Параметри:\n• Головний промінь дуже вузький (< 2°)\n• Висока спрямованість (> 35 dBi)\n• Низький рівень бокових завад",
                       size=11, pad=8, fill=FILL, stroke=LINE, color=INK)
    f.append(tb)

    render(os.path.join(IMG, "radiation-pattern-sidelobes.svg"), W, H, *f)


# ── 5. Вплив шорсткості поверхні за формулою Рузе ───────────────────────────
def fig_ruze_surface_loss():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke="none")]
    f.append(text(W / 2, 26, "Втрати підсилення від відхилень поверхні (Формула Рузе)", size=16, bold=True))

    gx0, gy0 = 100, 300
    gw, gh = 560, 230

    f.append(line(gx0, gy0, gx0 + gw, gy0, color=INK, sw=1.8))
    f.append(line(gx0, gy0, gx0, gy0 - gh, color=INK, sw=1.8))

    f.append(text(gx0 + gw / 2, gy0 + 38, "Нормована відносна шорсткість поверхні ε / λ", size=12, bold=True))
    f.append(text(gx0 - 45, gy0 - gh / 2, "Втрати η_r (dB)", size=12, bold=True))

    # Графік падіння ефективності від ε/λ за формулою Ruze: η_r = exp(-(4π ε/λ)^2)
    # у dB: Loss_dB = 10 log10(η_r) = 10 * (- (4π ε/λ)^2 ) * log10(e) = -54.57 * (ε/λ)^2
    ruze_pts = []
    for i in range(101):
        ratio = i / 100.0 * 0.12 # ε/λ від 0 до 0.12
        loss_db = -54.575 * (ratio ** 2)
        if loss_db < -15.0:
            loss_db = -15.0
        x = gx0 + (ratio / 0.12) * gw
        y = gy0 - (-loss_db / 15.0) * gh
        ruze_pts.append(f"{x:.1f},{y:.1f}")

    f.append(f'<polyline points="{" ".join(ruze_pts)}" fill="none" stroke="{POS}" stroke-width="3.0"/>')

    # Поріг допуску ε = λ / 16 ≈ 0.0625 λ (втрати ~ 0.68 dB)
    opt_ratio = 1.0 / 16.0
    x_opt = gx0 + (opt_ratio / 0.12) * gw
    y_opt = gy0 - (0.68 / 15.0) * gh

    f.append(line(x_opt, gy0, x_opt, gy0 - gh, color=FIELD, sw=1.5, dash="4,4"))
    f.append(circle(x_opt, y_opt, 6, fill=FIELD, stroke=INK, sw=1.5))
    
    tb, _, _ = textbox(x_opt + 120, y_opt - 40, "Допустима межа: ε ≤ λ / 16\nВтрати підсилення < 0.7 dB",
                       size=11, pad=8, fill=ACCENT_BG, stroke=FIELD, color=INK, bold=True)
    f.append(tb)

    # Зауваження про високі частоти
    f.append(text(gx0 + gw - 80, gy0 - gh + 20, "Критичне падіння при ε > λ/10 !", size=11, color=POS, bold=True))

    render(os.path.join(IMG, "ruze-surface-loss.svg"), W, H, *f)


if __name__ == "__main__":
    fig_parabola_focus()
    fig_feed_geometries()
    fig_illumination_taper()
    fig_radiation_pattern_sidelobes()
    fig_ruze_surface_loss()
    print("Усі 5 SVG-фігур успішно згенеровано у ./img/")
