# -*- coding: utf-8 -*-
"""Фігури до теми «Сервомеханізм» (загальний принцип замкненого контуру).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Замкнений контур позиції: давач → порівняння → привід → об'єкт → давач ─
def fig_loop():
    """Каркас будь-якого серворушія: уставка й виміряне сходяться у вузол
    порівняння, помилка йде на привід, привід рухає об'єкт, давач міряє
    результат і вертає його назад. Видно саме кільце зворотного зв'язку."""
    W, H = 780, 410
    f = [text(W / 2, 30, "Серворушій: замкнений контур, що тримає ціль", size=17, bold=True)]

    # уставка (ціль) зліва
    f.append(text(64, 92, "ціль", size=12, bold=True, color=MUTED))
    f.append(text(64, 110, "(уставка)", size=11, color=MUTED))

    # вузол порівняння (суматор)
    sx, sy = 175, 132
    f.append(circle(sx, sy, 26, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(text(sx, sy + 6, "−", size=22, color=NEG, bold=True))
    f.append(text(sx, sy - 40, "порівняння", size=12, bold=True, color=INK))
    f.append(arrow(108, sy, sx - 28, sy))

    # блок «привід» (мотор + підсилювач потужності)
    pb = fitbox(285, sy - 33, 150, 66, "привід\n(сила/момент)",
                size=13, bold=True, fill="#fbeee6", stroke=POS)
    f.append(pb)
    f.append(arrow(sx + 27, sy, 283, sy))
    f.append(text(245, sy - 12, "помилка", size=11, color=POS))

    # блок «об'єкт» (керована маса / поверхня)
    ob = fitbox(500, sy - 33, 168, 66, "об'єкт керування\n(вал, поверхня, вісь)",
                size=13, bold=True, fill="#f4f6f8", stroke=LINE)
    f.append(ob)
    f.append(arrow(436, sy, 498, sy))

    # вихід (справжня позиція) праворуч
    f.append(arrow(669, sy, 740, sy))
    f.append(text(715, sy - 12, "вихід", size=12, bold=True, color=INK))
    f.append(text(715, sy + 26, "(позиція)", size=11, color=MUTED))

    # збурення згори в об'єкт
    f.append(text(584, 56, "збурення", size=12, bold=True, color=POS))
    f.append(text(584, 73, "(вітер, вага)", size=11, color=MUTED))
    f.append(arrow(584, 80, 584, sy - 36))

    # давач — нижній ряд, повертає виміряне у вузол порівняння
    db = fitbox(430, 298, 170, 58, "давач\n(міряє вихід)",
                size=13, bold=True, fill="#eef2f7", stroke=NEG)
    f.append(db)
    # відведення з виходу вниз до давача
    f.append(line(715, sy + 34, 715, 327, color=NEG, sw=2))
    f.append(arrow(715, 327, 602, 327))
    # від давача назад до вузла порівняння (вгору в суматор)
    f.append(line(428, 327, sx, 327, color=NEG, sw=2))
    f.append(arrow(sx, 327, sx, sy + 28))
    f.append(text(300, 350, "виміряне (зворотний зв'язок)", size=12, bold=True, color=NEG))

    return render(os.path.join(IMG, "loop.svg"), W, H, *f)


# ── 2. Чому зворотний зв'язок тримає ціль попри збурення ─────────────────────
def fig_reject():
    """Дві відповіді на однаковий поштовх-збурення. Розімкнений: вихід поїхав
    і не вернувся. Замкнений: давач засік відхил, контур повернув до цілі.
    Це і є відмінність наосліп ↔ з вимірюванням."""
    W, H = 780, 380
    f = [text(W / 2, 30, "Той самий поштовх: чому замкнений контур вертає до цілі", size=16, bold=True)]

    # спільна шкала часу
    ox, oy = 70, 250          # початок осей
    axw, axh = 650, 170
    f.append(line(ox, oy, ox + axw, oy, color=LINE, sw=1.5))           # вісь часу
    f.append(line(ox, oy, ox, oy - axh, color=LINE, sw=1.5))           # вісь позиції
    f.append(text(ox + axw - 6, oy + 20, "час →", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 12, oy - axh + 6, "позиція", size=12, color=MUTED, anchor="end"))

    # лінія цілі
    ty = oy - 110
    f.append(line(ox, ty, ox + axw, ty, color=FIELD, sw=1.6, dash="7 5"))
    f.append(text(ox + axw - 4, ty - 8, "ціль", size=12, bold=True, color=FIELD, anchor="end"))

    # момент збурення
    dx = ox + 250
    f.append(line(dx, oy - axh + 10, dx, oy, color=POS, sw=1.4, dash="3 4"))
    f.append(text(dx, oy - axh + 4, "поштовх", size=12, bold=True, color=POS, anchor="middle"))

    # розімкнений: тримався на цілі, після поштовху поїхав і лишився внизу
    pts_open = [(ox, ty), (dx, ty), (dx + 40, ty + 55), (dx + 120, ty + 70), (ox + axw, ty + 72)]
    d_open = "M " + " L ".join("%.0f %.0f" % p for p in pts_open)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d_open, MUTED))
    f.append(text(ox + axw - 4, ty + 90, "розімкнений: поїхав і лишився", size=12, color=MUTED, anchor="end"))

    # замкнений: після поштовху просів і вернувся до цілі
    pts_cl = [(ox, ty), (dx, ty), (dx + 26, ty + 40), (dx + 70, ty + 18),
              (dx + 130, ty + 4), (ox + axw, ty + 1)]
    d_cl = "M " + " L ".join("%.0f %.0f" % p for p in pts_cl)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d_cl, NEG))
    f.append(text(dx + 150, ty + 30, "замкнений: вернувся", size=12, bold=True, color=NEG, anchor="start"))

    return render(os.path.join(IMG, "reject.svg"), W, H, *f)


# ── 3. Жорсткість і точність: помилка, мертва зона, два класи контурів ────────
def fig_classes():
    """Ліворуч — звідки береться жорсткість: що крутіший нахил «сила від
    помилки», то менший залишковий відхил під тим самим навантаженням.
    Праворуч — два класи: контур позиції (тримає кут) і контур швидкості
    (тримає оберти)."""
    W, H = 780, 380
    f = [text(W / 2, 30, "Жорсткість, точність і два класи контурів", size=16, bold=True)]

    # ── ліва панель: сила як функція помилки ──
    ox, oy = 70, 250
    axw, axh = 280, 170
    f.append(line(ox, oy, ox + axw, oy, color=LINE, sw=1.5))
    f.append(line(ox, oy, ox, oy - axh, color=LINE, sw=1.5))
    f.append(text(ox + axw - 4, oy + 20, "помилка", size=12, color=MUTED, anchor="end"))
    f.append(text(ox + 4, oy - axh + 4, "сила корекції", size=12, color=MUTED, anchor="start"))

    # мертва зона біля нуля
    dz = 34
    f.append(rect(ox, oy - axh, dz, axh, fill="#f0f0f0", stroke="none", rx=0))
    f.append(text(ox + dz + 4, oy - axh + 14, "мертва зона", size=11, color=MUTED, anchor="start"))

    # жорстка характеристика (крутий нахил) і м'яка (пологий)
    f.append(line(ox + dz, oy, ox + axw - 30, oy - axh + 12, color=POS, sw=2.6))
    f.append(text(ox + axw - 26, oy - axh + 18, "жорстка", size=12, bold=True, color=POS, anchor="start"))
    f.append(line(ox + dz, oy, ox + axw - 4, oy - 56, color=NEG, sw=2.2, dash="6 5"))
    f.append(text(ox + axw - 4, oy - 50, "м'яка", size=12, bold=True, color=NEG, anchor="end"))

    f.append(text(ox + axw / 2, oy + 44, "крутіший нахил → менший", size=11, color=INK, anchor="middle"))
    f.append(text(ox + axw / 2, oy + 60, "залишковий відхил під вагою", size=11, color=INK, anchor="middle"))

    # ── права панель: два класи контурів ──
    rx = 440
    f.append(text(rx + 150, 70, "два класи серворушіїв", size=13, bold=True, anchor="middle"))

    p1 = fitbox(rx, 92, 300, 70,
                "контур ПОЗИЦІЇ\nдавач кута → тримає КУТ",
                size=12, bold=True, fill="#eef2f7", stroke=NEG)
    f.append(p1)

    p2 = fitbox(rx, 182, 300, 70,
                "контур ШВИДКОСТІ\nдавач обертів → тримає ОБЕРТИ",
                size=12, bold=True, fill="#fbeee6", stroke=POS)
    f.append(p2)

    f.append(text(rx + 150, 300, "та сама петля, інша вимірювана величина",
                  size=12, color=MUTED, anchor="middle"))
    f.append(text(rx + 150, 320, "(часто вкладені: позиція над швидкістю)",
                  size=11, color=MUTED, anchor="middle"))

    return render(os.path.join(IMG, "classes.svg"), W, H, *f)


if __name__ == "__main__":
    fig_loop()
    fig_reject()
    fig_classes()
    print("OK: 3 фігури у", IMG)
