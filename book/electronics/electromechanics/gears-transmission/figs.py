# -*- coding: utf-8 -*-
"""Фігури до теми «Редуктори й передачі».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

import math


def gear(cx, cy, r, teeth, color=LINE, fill=FILL, sw=1.6, phase=0.0):
    """Намалювати зубчасте колесо: тіло-коло + короткі зубці по обводу."""
    out = [circle(cx, cy, r, fill=fill, stroke=color, sw=sw)]
    th = r * 0.18           # довжина зубця
    for k in range(teeth):
        a = phase + k * 2 * math.pi / teeth
        x1, y1 = cx + r * math.cos(a), cy + r * math.sin(a)
        x2, y2 = cx + (r + th) * math.cos(a), cy + (r + th) * math.sin(a)
        out.append(line(x1, y1, x2, y2, color=color, sw=sw + 0.4))
    out.append(circle(cx, cy, r * 0.16, fill=BG, stroke=color, sw=sw))  # вісь
    return "".join(out)


# ── 1. Головний компроміс: важіль міняє момент на оберти ────────────────────
def fig_lever():
    W, H = 720, 380
    f = [text(W / 2, 28, "Передача — це важіль: виграш у моменті = програш в обертах",
              size=16, bold=True)]

    # ліве колесо мале (швидке, слабке), праве велике (повільне, сильне)
    cyl = 210
    cxs, rs, ts = 200, 52, 10        # мале (вхід)
    cxb, rb, tb = 470, 104, 20       # велике (вихід)
    # зачеплення по дотичній лінії центрів
    f.append(gear(cxs, cyl, rs, ts, color=NEG, fill="#eef2f8"))
    f.append(gear(cxb, cyl, rb, tb, color=POS, fill="#fbeee6"))

    # стрілки обертання: мале крутиться швидко, велике — повільно й назад
    f.append('<path d="M%.0f %.0f a36 36 0 1 1 -1 0" fill="none" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
             % (cxs + 36, cyl - 8, NEG))
    f.append('<path d="M%.0f %.0f a64 64 0 1 0 1 0" fill="none" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
             % (cxb - 64, cyl - 8, POS))

    # підписи входу/виходу
    f.append(text(cxs, cyl + rs + 44, "ВХІД: мотор", size=13, bold=True, color=NEG))
    f.append(text(cxs, cyl + rs + 62, "10 зубців", size=11, color=MUTED))
    f.append(text(cxs, cyl - rs - 30, "швидко, слабко", size=11.5, color=NEG))

    f.append(text(cxb, cyl + rb + 44, "ВИХІД: вал", size=13, bold=True, color=POS))
    f.append(text(cxb, cyl + rb + 62, "20 зубців", size=11, color=MUTED))
    f.append(text(cxb, cyl - rb - 14, "удвічі повільніше, удвічі сильніше", size=11.5, color=POS))

    # підсумок-формула знизу
    b, _, _ = textbox(W / 2, 350, "20 / 10 = 2  →  оберти ×(1/2),  момент ×2",
                      size=13, bold=True, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "lever.svg"), W, H, *f)


# ── 2. Чому момент×оберти зберігається (потужність крізь передачу) ───────────
def fig_power():
    W, H = 720, 360
    f = [text(W / 2, 28, "Потужність крізь передачу зберігається — міняється лише її форма",
              size=16, bold=True)]

    # вхід
    b0, w0, _ = textbox(130, 150, "ВХІД\nмомент M\nоберти n\nP = M·n", size=12,
                        fill="#eef2f8", stroke=NEG, bold=False)
    f.append(b0)
    # коробка передач
    b1, w1, h1 = textbox(360, 150, "ПЕРЕДАЧА\nміняє M ↔ n\n(− тертя)", size=12,
                         fill=FILL, stroke=LINE)
    f.append(b1)
    # вихід
    b2, w2, _ = textbox(600, 150, "ВИХІД\nмомент M×2\nоберти n÷2\nP та сама", size=12,
                        fill="#fbeee6", stroke=POS, bold=False)
    f.append(b2)

    f.append(arrow(130 + w0 / 2, 150, 360 - w1 / 2, 150, color=NEG, sw=2.4))
    f.append(arrow(360 + w1 / 2, 150, 600 - w2 / 2, 150, color=POS, sw=2.4))

    # «втрати» вниз
    f.append(arrow(360, 150 + h1 / 2, 360, 150 + h1 / 2 + 46, color=MUTED, sw=2))
    f.append(text(360, 150 + h1 / 2 + 64, "втрати → тепло (тертя зубців)", size=11, color=MUTED))

    # пояснення-нитка знизу
    f.append(text(W / 2, 300, "добуток момент·оберти на вході ≈ добуток момент·оберти на виході",
                  size=12.5, color=INK))
    f.append(text(W / 2, 322, "більший момент даровий не буває — за нього платимо обертами",
                  size=11.5, color=MUTED))
    render(os.path.join(IMG, "power.svg"), W, H, *f)


# ── 3. Три типи передачі: зубчаста, пас, черв'як ────────────────────────────
def fig_types():
    W, H = 720, 360
    f = [text(W / 2, 26, "Три способи передати обертання — і чим вони різні", size=16, bold=True)]

    # 3а зубчаста пара
    f.append(gear(120, 150, 40, 10, color=INK, fill=FILL))
    f.append(gear(196, 150, 30, 8, color=INK, fill=FILL))
    f.append(text(150, 230, "Зубчаста", size=13, bold=True))
    f.append(text(150, 248, "тверда, точна,", size=10.5, color=MUTED))
    f.append(text(150, 263, "без проковзування", size=10.5, color=MUTED))

    # 3б пас
    f.append(circle(330, 150, 36, fill=FILL, stroke=INK, sw=1.6))
    f.append(circle(330, 150, 6, fill=BG, stroke=INK, sw=1.4))
    f.append(circle(430, 150, 22, fill=FILL, stroke=INK, sw=1.6))
    f.append(circle(430, 150, 5, fill=BG, stroke=INK, sw=1.4))
    # пас — дві дотичні
    f.append(line(330, 114, 430, 128, color=FIELD, sw=3))
    f.append(line(330, 186, 430, 172, color=FIELD, sw=3))
    f.append(text(380, 232, "Пасова", size=13, bold=True))
    f.append(text(380, 250, "тиха, гнучка,", size=10.5, color=MUTED))
    f.append(text(380, 265, "може ковзати", size=10.5, color=MUTED))

    # 3в черв'як + колесо
    # черв'як — горизонтальний гвинт
    wx, wy = 560, 120
    f.append(rect(wx - 38, wy - 12, 76, 24, fill=FILL, stroke=INK, sw=1.6, rx=4))
    for i in range(6):
        f.append(line(wx - 32 + i * 13, wy - 12, wx - 26 + i * 13, wy + 12, color=INK, sw=1.4))
    f.append(text(wx, wy - 22, "черв'як", size=10.5, color=MUTED))
    # колесо під ним
    f.append(gear(wx, wy + 58, 34, 14, color=INK, fill=FILL))
    f.append(text(wx, 232, "Черв'ячна", size=13, bold=True))
    f.append(text(wx, 250, "велике сповільнення,", size=10.5, color=MUTED))
    f.append(text(wx, 265, "самогальмівна", size=10.5, color=MUTED))

    # роздільники
    f.append(line(250, 95, 250, 280, color="#e0e5ec", sw=1.2, dash="4,4"))
    f.append(line(480, 95, 480, 280, color="#e0e5ec", sw=1.2, dash="4,4"))

    # спільний підпис-висновок
    f.append(text(W / 2, 320, "усі троє роблять одне — змінюють момент↔оберти; різняться тертям, тишею і точністю",
                  size=11.5, color=INK))
    render(os.path.join(IMG, "types.svg"), W, H, *f)


# ── 4. Люфт (мертвий хід): зуби не торкаються, поки не виберуть зазор ────────
def fig_backlash():
    W, H = 720, 320
    f = [text(W / 2, 28, "Люфт: між зубцями є зазор — вхід рушив, вихід ще стоїть", size=16, bold=True)]

    TW = 13          # ширина зуба
    def panel(x0, gap, caption, sub, col):
        cx1, cy = x0 + 78, 150
        cx2 = cx1 + 128
        r = 42
        # ведуче колесо (вхід)
        f.append(circle(cx1, cy, r, fill="#eef2f8", stroke=NEG, sw=1.8))
        f.append(circle(cx1, cy, 7, fill=BG, stroke=NEG, sw=1.4))
        # ведене колесо (вихід)
        f.append(circle(cx2, cy, r, fill="#fbeee6", stroke=POS, sw=1.8))
        f.append(circle(cx2, cy, 7, fill=BG, stroke=POS, sw=1.4))
        # зуб веденого (нерухомий, стирчить ліворуч від правого колеса)
        out_x = cx2 - r - TW
        f.append(rect(out_x, cy - 10, TW, 20, fill="#f2d9c8", stroke=POS, sw=1.7, rx=2))
        # зуб ведучого (стирчить праворуч від лівого колеса; gap = відстань до зуба веденого)
        in_x = out_x - gap - TW
        f.append(rect(in_x, cy - 10, TW, 20, fill="#dfe6ee", stroke=NEG, sw=1.7, rx=2))
        # позначка зазору
        if gap > 3:
            f.append(line(in_x + TW, cy + 30, out_x, cy + 30, color=MUTED, sw=1.4))
            f.append(line(in_x + TW, cy + 26, in_x + TW, cy + 34, color=MUTED, sw=1.2))
            f.append(line(out_x, cy + 26, out_x, cy + 34, color=MUTED, sw=1.2))
            f.append(text((in_x + TW + out_x) / 2, cy + 46, "зазор", size=10.5, color=MUTED))
        else:
            f.append(text((in_x + out_x) / 2 + TW / 2, cy + 46, "зуби торкнулись", size=10.5, color=POS))
        f.append(text((cx1 + cx2) / 2, cy + 82, caption, size=12.5, bold=True, color=col))
        f.append(text((cx1 + cx2) / 2, cy + 100, sub, size=10.5, color=MUTED))
        f.append(text(cx1, cy - 54, "вхід", size=10.5, color=NEG))
        f.append(text(cx2, cy - 54, "вихід", size=10.5, color=POS))

    panel(20, 26, "Зазор не вибрано", "вхід повернувся, а вихід ще стоїть", MUTED)
    f.append(arrow(335, 150, 378, 150, color=FIELD, sw=2.4))
    panel(378, 0, "Зазор вибрано — тягне", "зуби зійшлися, вихід пішов", POS)
    render(os.path.join(IMG, "backlash.svg"), W, H, *f)


if __name__ == "__main__":
    fig_lever()
    fig_power()
    fig_types()
    fig_backlash()
    print("OK: 4 figures ->", IMG)
