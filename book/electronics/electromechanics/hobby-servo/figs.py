# -*- coding: utf-8 -*-
"""Фігури до теми «Сервопривід» (хобі-серво).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Замкнений контур усередині серво ─────────────────────────────────────
def fig_loop():
    """Головна фігура: ШІМ → схема порівняння → H-міст → мотор → редуктор →
    вал/качалка → потенціометр → назад у схему. Зворотний зв'язок видно."""
    W, H = 760, 430
    f = [text(W / 2, 30, "Усередині серво: замкнений контур, що тримає кут", size=17, bold=True)]

    # вхід: ШІМ-імпульс
    f.append(text(70, 92, "ШІМ-вхід", size=12, bold=True, anchor="middle", color=MUTED))
    # маленький імпульс як іконка
    px = 30
    f.append(line(px, 110, px + 14, 110, color=NEG, sw=2))
    f.append(line(px + 14, 110, px + 14, 86, color=NEG, sw=2))
    f.append(line(px + 14, 86, px + 30, 86, color=NEG, sw=2))
    f.append(line(px + 30, 86, px + 30, 110, color=NEG, sw=2))
    f.append(line(px + 30, 110, px + 56, 110, color=NEG, sw=2))
    f.append(text(px + 35, 126, "1–2 мс", size=10, color=MUTED))

    # блок «схема порівняння»
    b1 = fitbox(150, 78, 168, 66, "Схема порівняння\n(задане − виміряне)",
                size=12, bold=True, fill="#eef6ef", stroke=FIELD)
    f.append(b1)

    # H-міст
    b2 = fitbox(390, 78, 150, 66, "H-міст\n(драйвер мотора)",
                size=12, bold=True, fill="#fbeee6", stroke=POS)
    f.append(b2)

    # мотор
    f.append(circle(640, 111, 36, fill=FILL, stroke=LINE, sw=2))
    f.append(text(640, 116, "M", size=22, bold=True, color=INK))
    f.append(text(640, 60, "мотор", size=12, bold=True, color=MUTED))

    # стрілки верхнього ряду (прямий хід)
    f.append(arrow(86, 111, 148, 111))
    f.append(arrow(320, 111, 388, 111))
    f.append(arrow(542, 111, 602, 111))

    # редуктор (вниз від мотора)
    b3 = fitbox(566, 210, 148, 56, "редуктор\n(сильніше, повільніше)",
                size=12, bold=True, fill="#f4f6f8", stroke=LINE)
    f.append(b3)
    f.append(arrow(640, 147, 640, 208))

    # вихідний вал + качалка
    cx, cy = 360, 300
    f.append(circle(cx, cy, 30, fill="#dfe6ee", stroke=LINE, sw=2))
    f.append(circle(cx, cy, 5, fill=INK, stroke=INK))
    # качалка (важіль)
    ang = math.radians(-32)
    hx, hy = cx + 70 * math.cos(ang), cy + 70 * math.sin(ang)
    f.append(line(cx, cy, hx, hy, color=INK, sw=6))
    f.append(circle(hx, hy, 5, fill=POS, stroke=POS))
    f.append(text(cx, cy + 52, "вихідний вал + качалка", size=12, bold=True, anchor="middle"))
    f.append(arrow(564, 238, 392, 290))

    # потенціометр на валу
    b4 = fitbox(96, 274, 150, 56, "потенціометр\n(міряє кут вала)",
                size=12, bold=True, fill="#eef6ef", stroke=FIELD)
    f.append(b4)
    f.append(arrow(330, 300, 248, 300))

    # зворотний зв'язок: потенціометр → схема порівняння (вгору)
    f.append(line(171, 274, 171, 200, color=FIELD, sw=2.2, dash="5,5"))
    f.append(line(171, 200, 234, 200, color=FIELD, sw=2.2, dash="5,5"))
    f.append(line(234, 200, 234, 145, color=FIELD, sw=2.2, dash="5,5"))
    f.append(text(150, 192, "зворотний зв'язок (виміряний кут)", size=11,
                  color=FIELD, anchor="start", bold=True))
    # маркер-стрілка на кінці зворотного зв'язку
    f.append(arrow(234, 162, 234, 145, color=FIELD))

    # підпис-висновок унизу
    f.append(text(W / 2, 408,
                  "помилка → корекція → новий вимір → знову помилка, поки кут не співпаде",
                  size=12, color=MUTED, anchor="middle", italic=True))
    render(os.path.join(IMG, "loop.svg"), W, H, *f)


# ── 2. Ширина імпульсу = кут ────────────────────────────────────────────────
def fig_pulse():
    """Три імпульси (1.0 / 1.5 / 2.0 мс) і відповідні положення качалки + період."""
    W, H = 760, 400
    f = [text(W / 2, 30, "Мова серво: ширина імпульсу задає кут", size=17, bold=True)]

    base_y = 150
    amp = 46
    cols = [(150, 1.0, -45, "один край"),
            (380, 1.5, 0, "центр (нейтраль)"),
            (610, 2.0, +45, "інший край")]

    for cx, ms, deg, label in cols:
        # імпульс
        x0 = cx - 70
        w_pulse = 24 + (ms - 1.0) * 40      # ширше = довший імпульс (наочно)
        f.append(line(x0, base_y, x0 + 18, base_y, color=NEG, sw=2.4))
        f.append(line(x0 + 18, base_y, x0 + 18, base_y - amp, color=NEG, sw=2.4))
        f.append(line(x0 + 18, base_y - amp, x0 + 18 + w_pulse, base_y - amp, color=NEG, sw=2.4))
        f.append(line(x0 + 18 + w_pulse, base_y - amp, x0 + 18 + w_pulse, base_y, color=NEG, sw=2.4))
        f.append(line(x0 + 18 + w_pulse, base_y, x0 + 140, base_y, color=NEG, sw=2.4))
        f.append(text(cx, base_y + 22, "%.1f мс" % ms, size=13, bold=True, color=INK))

        # качалка під імпульсом
        oy = 300
        f.append(circle(cx, oy, 24, fill="#dfe6ee", stroke=LINE, sw=2))
        a = math.radians(deg - 90)          # 0° = вгору
        hx, hy = cx + 52 * math.cos(a), oy + 52 * math.sin(a)
        f.append(line(cx, oy, hx, hy, color=INK, sw=6))
        f.append(circle(hx, hy, 5, fill=POS, stroke=POS))
        f.append(text(cx, oy + 46, label, size=11, color=MUTED, anchor="middle"))

    # стрілка-вісь «ширше = більший кут»
    f.append(arrow(80, 96, 700, 96, color=MUTED))
    f.append(text(W / 2, 86, "ширший імпульс  →  більший кут", size=12, color=MUTED, anchor="middle"))

    # період знизу
    f.append(text(W / 2, 372, "імпульс повторюється кожні ~20 мс  (≈50 Гц)",
                  size=12, color=MUTED, anchor="middle", italic=True))
    render(os.path.join(IMG, "pulse-angle.svg"), W, H, *f)


# ── 3. Робочий діапазон: межі ходу, мертва зона, момент ──────────────────────
def fig_range():
    """Дуга ходу качалки: упори на краях, мертва зона навколо цілі, момент утримання."""
    W, H = 740, 380
    f = [text(W / 2, 30, "Робочий діапазон серво: межі, мертва зона, момент", size=17, bold=True)]

    cx, cy, R = 370, 300, 150
    # дуга ходу (від -60 до +60 від вертикалі)
    def pt(deg, r):
        a = math.radians(deg - 90)
        return cx + r * math.cos(a), cy + r * math.sin(a)
    x1, y1 = pt(-60, R)
    x2, y2 = pt(60, R)
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="3"/>' % (x1, y1, R, R, x2, y2, LINE))

    # вісь обертання
    f.append(circle(cx, cy, 26, fill="#dfe6ee", stroke=LINE, sw=2))
    f.append(circle(cx, cy, 5, fill=INK, stroke=INK))

    # упори на краях
    for deg, lab, off in [(-60, "механічний\nупор", -1), (60, "механічний\nупор", 1)]:
        ex, ey = pt(deg, R)
        sx, sy = pt(deg, R - 22)
        f.append(line(sx, sy, *pt(deg, R + 22), color=POS, sw=4))
        b = fitbox(cx + off * 250 - 70, cy - 40, 140, 50, lab, size=11,
                   bold=True, fill="#fbeee6", stroke=POS)
        f.append(b)
    # стрілки від упорів до підписів
    f.append(arrow(*pt(-60, R + 8), *(cx - 110, cy - 22), color=MUTED))
    f.append(arrow(*pt(60, R + 8), *(cx + 110, cy - 22), color=MUTED))

    # ціль + мертва зона (вузький сектор біля +18°)
    tgt = 18
    f.append(line(cx, cy, *pt(tgt, R - 8), color=INK, sw=6))
    f.append(circle(*pt(tgt, R - 8), 5, fill=POS, stroke=POS))
    # сектор мертвої зони
    da, db = pt(tgt - 7, R - 8), pt(tgt + 7, R - 8)
    f.append('<path d="M %.1f %.1f L %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f Z" '
             'fill="#eef6ef" stroke="%s" stroke-width="1.4"/>'
             % (cx, cy, da[0], da[1], R - 8, R - 8, db[0], db[1], FIELD))
    b, _, _ = textbox(*pt(tgt, R + 48), "мертва зона:\nтут не смикається", size=11,
                      fill="#eef6ef", stroke=FIELD)
    f.append(b)

    # момент утримання: стрілки навколо вала
    f.append(text(cx, cy + 60, "момент утримання", size=12, bold=True, anchor="middle"))
    f.append(text(cx, cy + 78, "опір спробі зрушити вал", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, "range.svg"), W, H, *f)


# ── 4. Де працює: качалка → тяга → поверхня ─────────────────────────────────
def fig_linkage():
    """Серво позиціює механізм: оберт качалки через тягу відхиляє поверхню/кермо."""
    W, H = 740, 330
    f = [text(W / 2, 30, "Серво позиціює механізм: качалка → тяга → поверхня", size=17, bold=True)]

    # серво-корпус
    f.append(rect(70, 150, 110, 90, fill="#f4f6f8", stroke=LINE, sw=2))
    f.append(text(125, 200, "серво", size=13, bold=True, anchor="middle"))
    # вісь + качалка серво
    sx, sy = 125, 150
    f.append(circle(sx, sy, 12, fill="#dfe6ee", stroke=LINE, sw=2))
    a = math.radians(-25)
    qx, qy = sx + 60 * math.cos(a), sy + 60 * math.sin(a)
    f.append(line(sx, sy, qx, qy, color=INK, sw=5))
    f.append(circle(qx, qy, 5, fill=POS, stroke=POS))
    f.append(text(150, 120, "качалка серво", size=11, color=MUTED, anchor="middle"))

    # шарнір поверхні
    hingex, hingey = 520, 170
    f.append(circle(hingex, hingey, 7, fill=INK, stroke=INK))
    f.append(text(hingex, hingey + 28, "шарнір", size=11, color=MUTED, anchor="middle"))
    # качалка керма
    ka = math.radians(-150)
    kx, ky = hingex + 55 * math.cos(ka), hingey + 55 * math.sin(ka)
    f.append(line(hingex, hingey, kx, ky, color=INK, sw=5))

    # тяга (пушрод) між качалками
    f.append(line(qx, qy, kx, ky, color=NEG, sw=3))
    f.append(text((qx + kx) / 2, (qy + ky) / 2 - 12, "тяга (пушрод)", size=11,
                  color=NEG, anchor="middle", bold=True))

    # поверхня (кермо), що відхиляється
    pa = math.radians(22)
    px2, py2 = hingex + 150 * math.cos(pa), hingey + 150 * math.sin(pa)
    f.append(line(hingex, hingey, px2, py2, color=FIELD, sw=8))
    f.append(text(px2 - 10, py2 + 24, "поверхня / кермо", size=12, bold=True,
                  color=FIELD, anchor="middle"))
    # пунктир нейтралі
    f.append(line(hingex, hingey, hingex + 150, hingey, color=MUTED, sw=1.4, dash="5,5"))

    # підпис-висновок
    f.append(text(W / 2, 308,
                  "де треба «стати в кут і триматися»: рулі, підвіси, шасі, заслінки",
                  size=12, color=MUTED, anchor="middle", italic=True))
    render(os.path.join(IMG, "linkage.svg"), W, H, *f)


if __name__ == "__main__":
    fig_loop()
    fig_pulse()
    fig_range()
    fig_linkage()
    print("OK: fig_loop, fig_pulse, fig_range, fig_linkage -> ./img/")
