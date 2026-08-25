# -*- coding: utf-8 -*-
"""Фігури до теми «Узгоджувальні ланки (Г- і П-ланки)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b9770e"   # проміжний/віртуальний опір — тепле, але читабельне


# ── 1. Коло Сміта: дві сім'ї дуг і два рухи точки до центру ───────────────────
def fig_smith_moves():
    """Спрощене коло Сміта: показуємо ЛИШЕ дві сім'ї дуг (сталий R, стала G)
    і як послідовна / шунтова реактивність жене точку вздовж них до центру 50 Ω."""
    import math
    W, H = 940, 500
    f = [text(W / 2, 30, "Як реактивність жене точку по колу Сміта до центру", size=18, bold=True),
         text(W / 2, 52, "послідовний елемент рухає вздовж кола сталого R; шунтовий — вздовж кола сталої G (провідності)",
              size=11.5, color=MUTED, italic=True)]

    # геометрія кола Сміта (нормовані опори z = Z/50)
    R0 = 175                       # радіус великого кола (|Γ|=1)
    cx, cy = 300, 300             # центр діаграми = узгоджені 50 Ω (Γ=0)

    # межове коло |Γ|=1
    f.append(circle(cx, cy, R0, fill="#fcfefc", stroke=MUTED, sw=1.6))
    # горизонтальна вісь дійсних опорів
    f.append(line(cx - R0, cy, cx + R0, cy, color=MUTED, sw=1.2))
    # центр — ціль
    f.append(circle(cx, cy, 5, fill=FIELD, stroke=FIELD, sw=0))
    f.append(text(cx, cy - 12, "50 Ω", size=11, color=FIELD, bold=True))
    # крайні точки осі
    f.append(text(cx - R0 - 4, cy + 4, "0", size=10, color=MUTED, anchor="end"))
    f.append(text(cx + R0 + 4, cy + 4, "∞", size=11, color=MUTED, anchor="start"))

    # кола СТАЛОГО R (нормованого r): центр (cx + R0*r/(1+r), cy), радіус R0/(1+r)
    def r_circle(r, color, sw=1.6, dash=None):
        rc = R0 / (1 + r)
        ccx = cx + R0 * r / (1 + r)
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                'stroke-width="%.1f"%s/>' % (ccx, cy, rc, color, sw, d))

    # кола СТАЛОЇ G (нормованої g): дзеркальні — центр (cx − R0*g/(1+g), cy)
    def g_circle(g, color, sw=1.6, dash=None):
        rc = R0 / (1 + g)
        ccx = cx - R0 * g / (1 + g)
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                'stroke-width="%.1f"%s/>' % (ccx, cy, rc, color, sw, d))

    # кілька фонових кіл сталого R (сині) і сталого G (червоні), бліді
    for r in (0.5, 1.0, 2.0):
        f.append(r_circle(r, "#c9d6f5", 1.3))
    for g in (0.5, 1.0, 2.0):
        f.append(g_circle(g, "#f2cfca", 1.3))

    # позначки: робоча точка джерела z=(30+j10)/50 = 0.6 + j0.2
    # положення точки на діаграмі: Γ = (z−1)/(z+1)
    def pt(zr, zi):
        zden_r, zden_i = zr + 1, zi
        znum_r, znum_i = zr - 1, zi
        den = zden_r * zden_r + zden_i * zden_i
        gr = (znum_r * zden_r + znum_i * zden_i) / den
        gi = (znum_i * zden_r - znum_r * zden_i) / den
        return cx + gr * R0, cy - gi * R0     # y вниз

    # робоча точка джерела
    px, py = pt(0.6, 0.2)
    f.append(circle(px, py, 6, fill=NEG, stroke=NEG, sw=0))
    f.append(text(px - 10, py - 10, "(30+j10) Ω", size=10.5, color=NEG, bold=True, anchor="end"))

    # виділене коло сталого R через цю точку (r=0.6) — синє, товсте
    f.append(r_circle(0.6, NEG, 2.4))
    # виділене коло сталої G через центр (g=1) — червоне, товсте (по ньому доводимо до 50)
    f.append(g_circle(1.0, POS, 2.4))

    # стрілки-руху: 1) серія (по синьому колу R), 2) шунт (по червоному колу G) до центру
    # проміжна точка — перетин кола r=0.6 з колом g=1 (беремо приблизно на нижній півкулі)
    mx, my = pt(0.6, -0.49)       # та сама r=0.6, іде вниз реактивністю до кола g=1
    f.append(arrow(px, py, mx, my, color=NEG, sw=2.6))
    f.append(text(mx + 12, my + 6, "серія: вздовж кола R", size=10.5, color=NEG, anchor="start", bold=True))
    f.append(arrow(mx, my, cx, cy, color=POS, sw=2.6))
    f.append(text((mx + cx) / 2 + 8, (my + cy) / 2 + 18, "шунт: вздовж кола G", size=10.5, color=POS, anchor="start", bold=True))

    # легенда праворуч
    box, _, _ = textbox(720, 250,
                        "Дві сім'ї дуг:\n\n• коло СТАЛОГО R\n  (сине) — по ньому\n  жене ПОСЛІДОВНА\n  реактивність;\n\n• коло СТАЛОЇ G\n  (червоне) — по ньому\n  жене ШУНТОВА.\n\nЗадача — двома\nкроками дійти\nз точки джерела\nв центр (50 Ω).",
                        size=11, pad=14, fill="#fbfdff", stroke=NEG, sw=1.4)
    f.append(box)

    return render(os.path.join(IMG, 'smith-moves.svg'), W, H, *f)


# ── 2. П-ланка = дві Г-ланки навколо віртуального опору R_вірт < обох кінців ──
def fig_pi_as_two_l():
    W, H = 940, 470
    f = [text(W / 2, 30, "П-ланка = дві Г-ланки, склеєні через віртуальний опір", size=18, bold=True),
         text(W / 2, 52, "кожна половина знижує свій кінець до спільного R_вірт; що глибше R_вірт — то вища Q і вужча смуга",
              size=11.5, color=MUTED, italic=True)]

    # горизонтальна «драбина опорів»: R_дж — R_вірт (внизу) — R_н, з двома Г-ланками
    axy = 250
    x_src, x_v, x_load = 150, 470, 790

    # три вузли-опори
    def node(x, y, label, sub, color):
        return [circle(x, y, 30, fill="#fcfcfc", stroke=color, sw=2.2),
                text(x, y - 2, label, size=12, color=color, bold=True),
                text(x, y + 15, sub, size=9, color=MUTED)]

    f += node(x_src, axy, "R_дж", "≈ 30 Ω", NEG)
    f += node(x_load, axy, "R_н", "≈ 50 Ω", FIELD)
    # віртуальний вузол — нижче, підкреслено, бо R_вірт МЕНШИЙ за обидва
    f += node(x_v, axy + 120, "R_вірт", "< 30 Ω", GOLD)

    # ліва Г-ланка: R_дж → R_вірт
    f.append(arrow(x_src + 28, axy + 10, x_v - 22, axy + 108, color=NEG, sw=2.2))
    box, _, _ = textbox((x_src + x_v) / 2 - 20, axy + 30,
                        "Г-ланка №1\nзнижує 30 Ω\nдо R_вірт",
                        size=10.5, pad=10, fill="#f4f7ff", stroke=NEG, sw=1.3)
    f.append(box)

    # права Г-ланка: R_вірт → R_н
    f.append(arrow(x_v + 22, axy + 108, x_load - 28, axy + 10, color=FIELD, sw=2.2))
    box, _, _ = textbox((x_v + x_load) / 2 + 20, axy + 30,
                        "Г-ланка №2\nпіднімає R_вірт\nдо 50 Ω",
                        size=10.5, pad=10, fill="#f2fbf5", stroke=FIELD, sw=1.3)
    f.append(box)

    # вертикальна шкала «глибина R_вірт → Q»
    sx = 880
    f.append(line(sx, 110, sx, 400, color=MUTED, sw=1.6))
    f.append(text(sx + 6, 110, "Q мала", size=9.5, color=MUTED, anchor="start"))
    f.append(text(sx + 6, 122, "смуга широка", size=9.5, color=FIELD, anchor="start"))
    f.append(text(sx + 6, 392, "Q велика", size=9.5, color=MUTED, anchor="start"))
    f.append(text(sx + 6, 404, "смуга вузька", size=9.5, color=POS, anchor="start"))
    f.append('<path d="M %d,120 L %d,395" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
             % (sx, sx, MUTED))

    # підпис-висновок знизу
    box, _, _ = textbox(W / 2 - 60, 430,
                        "Проміжний R_вірт — вільний параметр, якого в Г-ланці нема. Обираючи його ГЛИБШЕ за обидва кінці,\n"
                        "піднімаємо перепад кожної половини, а з ним і сумарну Q; вужчаючи, це і є плата за керовану смугу.\n"
                        "Виберемо R_вірт близько до кінців — П розширює смугу; заженемо глибоко — звужує й піднімає підсилення на краях.",
                        size=10.3, pad=12, fill="#fcfcfc", stroke=MUTED, sw=1.3)
    f.append(box)

    return render(os.path.join(IMG, 'pi-as-two-l.svg'), W, H, *f)


if __name__ == '__main__':
    fig_smith_moves()
    fig_pi_as_two_l()
    print('OK: smith-moves, pi-as-two-l')
