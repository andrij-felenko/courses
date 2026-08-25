# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GLASS = "#eaf2fb"   # оптично щільніше середовище (n1)
AIR   = "#f9fafb"   # рідше середовище (n2)
GOLD  = "#fef3c7"   # шар золота для плазмонного резонансу


def polygon(pts, fill=FILL, stroke=LINE, sw=1.0, opacity=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    op_str = ' opacity="%.2f"' % opacity if opacity < 1.0 else ''
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (pts_str, fill, stroke, sw, op_str)

def path_cmd(cmds, fill='none', stroke=LINE, sw=1.5, dash=None):
    if isinstance(cmds, str):
        d = cmds
    else:
        d_parts = []
        for c in cmds:
            cmd_type = c[0]
            coords = " ".join("%.1f" % x for x in c[1:])
            d_parts.append("%s %s" % (cmd_type, coords))
        d = " ".join(d_parts)
    dash_str = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, stroke, sw, dash_str)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Профіль еванесцентного поля на межі розділу двох середовищ
# ═══════════════════════════════════════════════════════════════════════════
def fig_field_decay():
    W, H = 720, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'Еванесцентна хвиля: поширення уздовж межі та згасання вглиб', 16, INK, 'middle', bold=True))

    py = 220    # Межа z = 0
    w_left = 440

    # Нижнє середовище n1 (скло)
    f.append(rect(40, py, w_left, H - py - 40, fill=GLASS, stroke='none', sw=0, rx=0))
    # Верхнє середовище n2 (повітря/вода)
    f.append(rect(40, 50, w_left, py - 50, fill=AIR, stroke='none', sw=0, rx=0))

    # Межа розділу z = 0
    f.append(line(40, py, 40 + w_left, py, color=INK, sw=2))
    f.append(text(60, py - 12, 'Середовище 2 (n₂)', 12, MUTED, 'start'))
    f.append(text(60, py + 24, 'Середовище 1 (n₁ > n₂)', 12, INK, 'start', bold=True))

    # Похилий падаючий промінь в n1
    f.append(arrow(90, py + 110, 220, py, color=POS, sw=2.5))
    f.append(text(60, py + 50, 'Падаюча хвиля (θ₁ > θ_c)', 12, POS, 'start', bold=True))

    # Відбитий промінь у n1
    f.append(arrow(220, py, 350, py + 110, color=NEG, sw=2.5))
    f.append(text(360, py + 95, 'Відбита хвиля (100% енергії)', 12, NEG, 'start'))

    # Нормаль до межі (пунктир)
    f.append(line(220, 70, 220, py + 130, color=MUTED, sw=1.2, dash='4,4'))

    # Хвильові фронти еванесцентної хвилі (нижча висота, щоб не перетинати стрелку)
    for x_wave in range(230, 440, 28):
        f.append(line(x_wave, py, x_wave, py - 60, color=FIELD, sw=1.8))

    # Стрелка поширення уздовж поверхні (вище штрихів)
    f.append(arrow(240, py - 75, 420, py - 75, color=FIELD, sw=2))
    f.append(text(330, py - 88, 'Біжуча фаза exp(i k_x x)', 11, FIELD, 'middle', bold=True))

    # Згасання амплітуди вгору (текст зліва від стрілки, end-anchor)
    f.append(arrow(445, py, 445, 70, color=NEG, sw=1.5))
    f.append(text(435, 110, 'Згасання exp(-κ_z z)', 11, NEG, 'end'))

    # Правий графік — експоненційна крива амплітуди E(z)
    gx0 = 530
    gy0 = py
    gw = 150
    gh = 140

    # Осі графіка
    f.append(line(gx0, gy0, gx0 + gw, gy0, color=INK, sw=1.5))       # вісь амплітуди/x
    f.append(line(gx0, gy0, gx0, gy0 - gh, color=INK, sw=1.5))       # вісь z (вглиб n2)
    f.append(text(gx0 - 10, gy0 - gh + 10, 'z', 12, INK, 'end', bold=True))
    f.append(text(gx0 + gw + 10, gy0 + 4, 'E(z)', 12, INK, 'start', bold=True))

    # Точки кривої E(z) = E0 * exp(-z / dp)
    pts = []
    dp_scale = 45.0
    for iz in range(0, 130, 3):
        ez = math.exp(-iz / dp_scale)
        px = gx0 + ez * 120
        py_pt = gy0 - iz
        pts.append((px, py_pt))

    poly_pts = [(gx0, gy0)] + pts + [(gx0, gy0 - 129)]
    f.append(polygon(poly_pts, fill=FIELD, stroke='none', opacity=0.15))
    
    # Лінія кривої
    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=FIELD, sw=2.5))

    # Позначка E0 на межі z = 0
    f.append(circle(gx0 + 120, gy0, 3.5, fill=FIELD, stroke=INK, sw=1))
    f.append(text(gx0 + 120, gy0 + 18, 'E₀', 12, FIELD, 'middle', bold=True))

    # Позначка d_p (відстань де E = E0 / e)
    z_dp = int(dp_scale)
    e_dp_x = gx0 + (120.0 / math.e)
    f.append(line(gx0, gy0 - z_dp, e_dp_x, gy0 - z_dp, color=MUTED, sw=1, dash='3,3'))
    f.append(circle(e_dp_x, gy0 - z_dp, 3.5, fill=NEG, stroke=INK, sw=1))
    f.append(text(gx0 - 8, gy0 - z_dp + 4, 'd_p', 11, NEG, 'end', bold=True))
    f.append(text(e_dp_x + 10, gy0 - z_dp + 4, 'E₀ / e ≈ 0.37 E₀', 10, MUTED, 'start'))

    # Підписи осей та загальний підпис
    f.append(text(W / 2, H - 12, 'Глибина проникнення d_p залежить від довжини хвилі λ та перевищення критичного кута θ₁ > θ_c', 12, INK, 'middle'))

    render(os.path.join(IMG, 'field-decay.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Порушене повне внутрішнє відбиття (FTIR) та тунелювання
# ═══════════════════════════════════════════════════════════════════════════
def fig_ftir_tunneling():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'Порушене повне внутрішнє відбиття (FTIR) та оптичне тунелювання', 16, INK, 'middle', bold=True))

    panels = [
        (190, 90, 'a) Зазор d >> d_p: 100% відбиття', 0.0),
        (530, 25, 'b) Зазор d ~ d_p: тунелювання світла', 0.55),
    ]

    for cx, gap, title, t_coeff in panels:
        p_w = 310
        x0 = cx - p_w / 2
        
        # Верхня призма n1
        f.append(rect(x0, 55, p_w, 80, fill=GLASS, stroke='none', sw=0, rx=0))
        f.append(line(x0, 135, x0 + p_w, 135, color=INK, sw=1.5))
        f.append(text(x0 + 10, 75, 'Призма 1 (n₁)', 11, INK, 'start', bold=True))

        # Зазор n2 (повітря)
        f.append(rect(x0, 135, p_w, gap, fill=AIR, stroke='none', sw=0, rx=0))
        f.append(text(x0 + 10, 135 + gap / 2 + 4, 'Зазор (n₂)', 10, MUTED, 'start'))

        # Нижня призма n1
        y_bot = 135 + gap
        f.append(rect(x0, y_bot, p_w, 270 - y_bot, fill=GLASS, stroke='none', sw=0, rx=0))
        f.append(line(x0, y_bot, x0 + p_w, y_bot, color=INK, sw=1.5))
        f.append(text(x0 + 10, y_bot + 20, 'Призма 2 (n₁)', 11, INK, 'start', bold=True))

        # Падаючий промінь
        ix0, iy0 = cx - 90, 65
        ix1, iy1 = cx - 20, 135
        f.append(arrow(ix0, iy0, ix1, iy1, color=POS, sw=2.5))
        f.append(text(ix0 - 5, iy0 - 4, 'Падаючий', 10, POS, 'end'))

        # Відбитий промінь
        rx0, ry0 = cx - 20, 135
        rx1, ry1 = cx + 50, 65
        r_sw = max(1.0, 2.5 * math.sqrt(1.0 - t_coeff))
        f.append(arrow(rx0, ry0, rx1, ry1, color=NEG, sw=r_sw))
        f.append(text(rx1 + 5, ry1 - 4, 'Відбитий', 10, NEG, 'start'))

        # Згасаюча хвиля у зазорі
        if t_coeff == 0.0:
            for y_s in range(137, int(135 + gap - 5), 8):
                f.append(line(cx - 20, y_s, cx + 20, y_s, color=FIELD, sw=1.2))
        else:
            for y_s in range(136, int(y_bot), 5):
                f.append(line(cx - 20, y_s, cx + 20, y_s, color=FIELD, sw=1.5))
            
            # Пройшовший (тунельований) промінь у нижній призмі
            tx0, ty0 = cx - 20, y_bot
            tx1, ty1 = cx + 50, y_bot + 70
            t_sw = max(1.0, 2.5 * math.sqrt(t_coeff))
            f.append(arrow(tx0, ty0, tx1, ty1, color=FIELD, sw=t_sw))
            f.append(text(tx1 + 5, ty1 + 12, 'Пройшовший (тунельований)', 10, FIELD, 'start', bold=True))

        # Позначка ширини d
        if gap > 40:
            f.append(arrow(cx + 110, 135, cx + 110, 135 + gap, color=INK, sw=1.2))
            f.append(text(cx + 122, 135 + gap / 2 + 4, 'd >> d_p', 11, INK, 'start'))
        else:
            f.append(arrow(cx + 110, 135, cx + 110, y_bot, color=INK, sw=1.2))
            f.append(text(cx + 122, 135 + gap / 2 + 4, 'd ~ d_p', 11, INK, 'start', bold=True))

        # Заголовок панелі
        f.append(text(cx, 305, title, 12, INK, 'middle', bold=True))

    f.append(text(W / 2, H - 12, 'Експоненційне малювання зазору d призводить до тунелювання коефіцієнта проходження T(d) ∝ exp(-2κ_z d)', 11, MUTED, 'middle'))

    render(os.path.join(IMG, 'ftir-tunneling.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Ефект Гуса — Хенхен (Goos-Hänchen shift)
# ═══════════════════════════════════════════════════════════════════════════
def fig_goos_hanchen():
    W, H = 700, 350
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'Ефект Гуса — Хенхен: просторове зміщення відбитого пучка', 16, INK, 'middle', bold=True))

    py = 180
    w_box = 620

    # Середовище 1 (скло)
    f.append(rect(40, py, w_box, H - py - 40, fill=GLASS, stroke='none', sw=0, rx=0))
    # Середовище 2 (повітря)
    f.append(rect(40, 50, w_box, py - 50, fill=AIR, stroke='none', sw=0, rx=0))

    # Межа z = 0
    f.append(line(40, py, 40 + w_box, py, color=INK, sw=2))
    f.append(text(60, py - 12, 'Рідше середовище (n₂)', 12, MUTED, 'start'))
    f.append(text(60, py + 120, 'Щільніше середовище (n₁)', 12, INK, 'start', bold=True))

    # Точка падіння за геометричною оптикою
    x_geom = 240
    f.append(line(x_geom, py - 40, x_geom, py + 60, color=MUTED, sw=1, dash='4,4'))

    # Падаючий світловий пучок (початок x=100, кінцева точка x_geom=240, py=180)
    f.append(arrow(100, py + 110, x_geom, py, color=POS, sw=3))
    f.append(text(60, py + 35, 'Падаючий пучок', 12, POS, 'start', bold=True))

    # Уявний промінь, що проникає на глибину d_p і повертається
    x_shift = 380
    f.append(line(x_shift, py - 40, x_shift, py + 60, color=MUTED, sw=1, dash='4,4'))

    # Траєкторія пучка в середовищі 2
    f.append(path_cmd([('M', x_geom, py), ('C', x_geom + 40, py - 50, x_shift - 40, py - 50, x_shift, py)],
                      fill='none', stroke=FIELD, sw=2.5, dash='5,3'))
    f.append(text((x_geom + x_shift) / 2, py - 60, 'Проникаюче еванесцентне поле', 11, FIELD, 'middle', bold=True))

    # Глибина проникнення d_p
    f.append(arrow((x_geom + x_shift) / 2, py, (x_geom + x_shift) / 2, py - 45, color=NEG, sw=1.2))
    f.append(text((x_geom + x_shift) / 2 + 10, py - 22, 'd_p', 11, NEG, 'start', bold=True))

    # Реальний відбитий пучок зі зміщенням D_GH
    f.append(arrow(x_shift, py, x_shift + 140, py + 110, color=NEG, sw=3))
    f.append(text(x_shift + 110, py + 75, 'Реальний відбитий пучок', 12, NEG, 'start', bold=True))

    # Ідеалізований геометричний відбитий пучок (пунктир)
    f.append(line(x_geom, py, x_geom + 140, py + 110, color=MUTED, sw=1.5, dash='3,3'))

    # Позначка зсуву D_GH між двома точками на межі
    f.append(arrow(x_geom, py + 25, x_shift, py + 25, color=INK, sw=1.8))
    f.append(arrow(x_shift, py + 25, x_geom, py + 25, color=INK, sw=1.8))
    f.append(text((x_geom + x_shift) / 2 + 15, py + 42, 'Зміщення D_GH ≈ 2 d_p tan θ₁', 11, INK, 'middle', bold=True))

    f.append(text(W / 2, H - 12, 'Відбита хвиля зазнає просторового зсуву D_GH уздовж межі через затримку енергії в еванесцентній зоні', 11, MUTED, 'middle'))

    render(os.path.join(IMG, 'goos-hanchen.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Застосування: TIRF-мікроскопія та сенсори SPR
# ═══════════════════════════════════════════════════════════════════════════
def fig_tirf_spr():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'Практичні застосування: TIRF-мікроскопія та сенсори SPR', 16, INK, 'middle', bold=True))

    # Panel A: TIRF
    cx1 = 190
    f.append(rect(30, 55, 320, 240, fill=BG, stroke=MUTED, sw=1, rx=4))
    f.append(text(cx1, 75, 'a) TIRF-мікроскопія клітин', 13, INK, 'middle', bold=True))

    # Скло покривного скельця
    f.append(rect(45, 180, 290, 80, fill=GLASS, stroke='none', sw=0, rx=0))
    f.append(line(45, 180, 335, 180, color=INK, sw=1.5))
    f.append(text(55, 220, 'Покривне скло (n₁ ≈ 1.52)', 10, INK, 'start'))

    # Водне середовище з клітиною
    f.append(rect(45, 95, 290, 85, fill=AIR, stroke='none', sw=0, rx=0))
    f.append(text(55, 115, 'Вода / цитоплазма (n₂ ≈ 1.33)', 10, MUTED, 'start'))

    # Лазерний промінь під кутом ПВВ
    f.append(arrow(60, 250, 160, 180, color=POS, sw=2.5))
    f.append(arrow(160, 180, 260, 250, color=NEG, sw=2.5))

    # Згасаюче еванесцентне поле товщиною ~100 нм
    f.append(rect(45, 162, 290, 18, fill=FIELD, stroke='none'))
    f.append(text(285, 172, 'Зона збудження (~100 нм)', 9, FIELD, 'end', bold=True))

    # Клітина та флуорофори
    f.append(path_cmd([('M', 80, 120), ('Q', 160, 172, 300, 130)], fill='none', stroke=INK, sw=2))
    f.append(text(210, 135, 'Мембрана клітини', 10, INK, 'start'))

    # Флуоресцентні мітки
    f.append(circle(140, 174, 4, fill=FIELD, stroke=INK, sw=1))  # світиться!
    f.append(circle(190, 168, 4, fill=FIELD, stroke=INK, sw=1))  # світиться!
    f.append(circle(230, 172, 4, fill=FIELD, stroke=INK, sw=1))  # світиться!
    f.append(circle(120, 125, 4, fill=MUTED, stroke=INK, sw=1))  # темний поза зоною
    f.append(circle(250, 115, 4, fill=MUTED, stroke=INK, sw=1))  # темний поза зоною

    f.append(text(cx1, 280, 'Збуджуються ЛИШЕ молекули у мембрані', 11, POS, 'middle', bold=True))

    # Panel B: SPR
    cx2 = 550
    f.append(rect(390, 55, 320, 240, fill=BG, stroke=MUTED, sw=1, rx=4))
    f.append(text(cx2, 75, 'b) Плазмонний біосенсор (SPR)', 13, INK, 'middle', bold=True))

    # Призма Кретчманна
    f.append(rect(405, 190, 290, 70, fill=GLASS, stroke='none', sw=0, rx=0))
    f.append(line(405, 190, 695, 190, color=INK, sw=1.5))
    f.append(text(415, 230, 'Скляна призма (n₁)', 10, INK, 'start'))

    # Шар золота ~50 нм
    f.append(rect(405, 180, 290, 10, fill=GOLD, stroke=INK, sw=0.8))
    f.append(text(685, 187, 'Au (50 нм)', 9, INK, 'end', bold=True))

    # Рідинний канал (аналіт)
    f.append(rect(405, 95, 290, 85, fill=AIR, stroke='none', sw=0, rx=0))
    f.append(text(415, 115, 'Рідинний канал (аналіт)', 10, MUTED, 'start'))

    # Лазер під кутом резонансу θ_SPR
    f.append(arrow(430, 250, 550, 185, color=POS, sw=2.5))
    f.append(arrow(550, 185, 670, 250, color=NEG, sw=1.2))

    # Еванесцентна хвиля збуджує плазмони на поверхні золота
    for x_p in range(500, 600, 12):
        f.append(circle(x_p, 180, 2.5, fill=NEG, stroke='none'))
    f.append(text(550, 168, 'Поверхневий плазмон', 10, NEG, 'middle', bold=True))

    # Біомолекули (антитіла + ліганди), що зв'язуються на поверхні
    f.append(rect(520, 172, 8, 8, fill=POS, stroke=INK, sw=0.8))
    f.append(rect(570, 172, 8, 8, fill=POS, stroke=INK, sw=0.8))
    f.append(text(550, 148, 'Специфічне зв\'язування білків', 10, INK, 'middle'))

    f.append(text(cx2, 280, 'Зміна показника n₂ зсуває кут резонансу θ_SPR', 11, NEG, 'middle', bold=True))

    f.append(text(W / 2, H - 12, 'Висока локалізація еванесцентного поля забезпечує нанометрову точність вимірювань', 11, MUTED, 'middle'))

    render(os.path.join(IMG, 'tirf-spr.svg'), W, H, *f)


if __name__ == '__main__':
    fig_field_decay()
    fig_ftir_tunneling()
    fig_goos_hanchen()
    fig_tirf_spr()
    print("All figures generated successfully.")
