# -*- coding: utf-8 -*-
"""Фігури до компонентної вставки «Компаратор-мікросхема: LM393-клас».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def npn(cx, cy, label="NPN"):
    """Маленький NPN-символ у колі: база ліворуч, колектор угору, емітер униз."""
    out = [circle(cx, cy, 22, fill="#fff", stroke=INK, sw=1.6)]
    # вертикальна риска (база), колектор угору-праворуч, емітер униз-праворуч
    out.append(line(cx - 6, cy - 12, cx - 6, cy + 12, color=INK, sw=2.4))   # база-планка
    out.append(line(cx - 18, cy, cx - 6, cy, color=INK, sw=1.6))            # вивід бази
    out.append(line(cx - 6, cy - 6, cx + 12, cy - 16, color=INK, sw=1.6))   # до колектора
    out.append(line(cx - 6, cy + 6, cx + 12, cy + 16, color=INK, sw=1.6))   # до емітера
    # стрілка емітера (NPN — від бази назовні)
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
               % (cx + 4, cy + 9, cx + 12, cy + 16, cx + 2, cy + 16, INK))
    return "".join(out)


# ── 1. Відкритий колектор: транзистор лише стягує вниз; «1» дає підтяжка ──────
def fig_open_collector():
    W, H = 720, 420
    f = [text(W / 2, 30, "Відкритий колектор: вихід уміє лише СТЯГУВАТИ вниз",
              size=16, bold=True)]

    # рамка мікросхеми (ліворуч) із вихідним транзистором
    f.append(rect(60, 80, 250, 290, fill="#f4f6f8", stroke=LINE, sw=1.4, rx=10))
    f.append(text(185, 104, "усередині компаратора", size=12, color=MUTED, bold=True))

    # вузол OUT (правий край мікросхеми) на середині
    out_y = 230
    out_x = 310
    # NPN: колектор → OUT, емітер → GND
    tx, ty = 185, 250
    f.append(npn(tx, ty))
    f.append(text(tx, ty + 40, "вихідний NPN", size=11, color=MUTED))
    # колектор угору до лінії OUT
    f.append(line(tx + 12, ty - 16, tx + 12, out_y, color=LINE, sw=1.8))
    f.append(line(tx + 12, out_y, out_x, out_y, color=LINE, sw=1.8))
    # емітер униз до землі
    f.append(line(tx + 12, ty + 16, tx + 12, 350, color=LINE, sw=1.8))
    f.append(line(tx - 2, 350, tx + 26, 350, color=INK, sw=2.2))   # символ землі
    f.append(line(tx + 3, 356, tx + 21, 356, color=INK, sw=1.8))
    f.append(line(tx + 8, 362, tx + 16, 362, color=INK, sw=1.4))
    f.append(text(tx + 12, 380, "GND", size=11, color=MUTED))
    # керування базою (від компаратора всередині)
    f.append(line(120, ty, tx - 18, ty, color=MUTED, sw=1.4, dash="4,3"))
    f.append(text(116, ty + 4, "рішення", size=10, color=MUTED, anchor="end"))

    # лінія OUT назовні
    f.append(line(out_x, out_y, 470, out_y, color=LINE, sw=2))
    f.append(circle(470, out_y, 4, fill=INK, stroke=INK, sw=1))
    f.append(text(out_x + 6, out_y - 12, "OUT", size=12, bold=True, anchor="start"))

    # підтяжка вгору до Vpull
    pull_x = 470
    f.append(line(pull_x, out_y, pull_x, 150, color=LINE, sw=1.8))
    rb, _, _ = textbox(pull_x, 175, "Rпідт", size=12, fill="#fff7e6",
                       stroke="#b8860b", min_w=40)
    # ховаємо стандартну textbox-рамку поверх лінії: малюємо її поверх
    f.append(rb)
    f.append(line(pull_x, 150, pull_x, 120, color=POS, sw=2))
    f.append(text(pull_x, 110, "+Vпідт (3.3 чи 5 В)", size=12, color=POS, bold=True))

    # далі на логіку
    f.append(line(pull_x, out_y, 560, out_y, color=LINE, sw=2))
    f.append(arrow(560, out_y, 600, out_y, color=LINE, sw=2))
    b, _, _ = textbox(652, out_y, "до логіки\n/ MCU", size=12,
                      fill="#eef2fc", stroke=NEG)
    f.append(b)

    # два стани — підпис унизу
    f.append(text(W / 2, 408,
                  "«0»: транзистор відкритий, садить OUT на землю    •    "
                  "«1»: транзистор закритий, OUT підтягує резистор",
                  size=12, color=INK))
    return render(os.path.join(IMG, "open-collector.svg"), W, H, *f)


# ── 2. Монтажне «І»: кілька відкритих колекторів на одній підтяжці ───────────
def fig_wired_and():
    W, H = 720, 430
    f = [text(W / 2, 30, "Монтажне «І»: один тягне вниз — уся лінія внизу",
              size=16, bold=True)]

    line_x = 470          # спільна вертикальна лінія
    top_y = 90
    bot_y = 360

    # спільна підтяжка вгорі
    f.append(line(line_x, top_y, line_x, 70, color=POS, sw=2))
    f.append(text(line_x, 58, "+Vпідт", size=12, color=POS, bold=True))
    rb, _, _ = textbox(line_x, 110, "Rпідт", size=12, fill="#fff7e6",
                       stroke="#b8860b", min_w=44)
    f.append(rb)

    # спільна шина «лінія тривоги»
    f.append(line(line_x, 132, line_x, bot_y, color=INK, sw=2.4))
    f.append(text(line_x + 14, (132 + bot_y) / 2, "спільна лінія", size=12,
                  bold=True, anchor="start"))
    f.append(text(line_x + 14, (132 + bot_y) / 2 + 18, "(«1» лише коли ВСІ мовчать)",
                  size=11, color=MUTED, anchor="start"))

    # три компаратори ліворуч, виходи на спільну лінію
    ys = [165, 245, 325]
    labels = ["комп. A", "комп. B", "комп. C"]
    states = ["закр.", "ВІДКР.", "закр."]
    colors = [MUTED, POS, MUTED]
    for y, lab, st, col in zip(ys, labels, states, colors):
        f.append(rect(70, y - 26, 150, 52, fill="#f4f6f8", stroke=LINE, sw=1.3, rx=8))
        f.append(text(145, y - 4, lab, size=12, bold=True))
        f.append(text(145, y + 14, "транз. " + st, size=11, color=col))
        # вивід на спільну лінію
        f.append(line(220, y, line_x, y, color=col, sw=2 if col == POS else 1.6))
        f.append(circle(line_x, y, 3.5, fill=INK, stroke=INK, sw=1))

    # «винуватець» тягне лінію вниз — підкреслимо стрілкою до землі
    f.append(text(300, ys[1] - 12, "тягне ↓", size=11, color=POS, bold=True))

    # вихід лінії на читача
    f.append(line(line_x, bot_y, 560, bot_y, color=INK, sw=2))
    f.append(arrow(560, bot_y, 600, bot_y, color=INK, sw=2))
    b, _, _ = textbox(652, bot_y, "1 вхід\nMCU", size=12,
                      fill="#eef2fc", stroke=NEG)
    f.append(b)

    f.append(text(W / 2, 414,
                  "Будь-який спрацьований вихід садить спільний провід на землю — "
                  "логіка без жодного вентиля",
                  size=12, color=INK))
    return render(os.path.join(IMG, "wired-and.svg"), W, H, *f)


# ── 3. Зовнішній гістерезис: додатний зв'язок розсуває поріг на два ──────────
def fig_external_hysteresis():
    W, H = 720, 400
    f = [text(W / 2, 30, "Зовнішній гістерезис: один поріг → два, із «мертвою зоною»",
              size=16, bold=True)]

    # осі: вхідна напруга (гориз.), вихід (верт.)
    ox, oy = 110, 320          # початок осей
    axw, axh = 480, 210
    f.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))      # вісь входу
    f.append(arrow(ox + axw, oy, ox + axw + 16, oy, color=INK, sw=2))
    f.append(text(ox + axw + 6, oy + 22, "Vвх", size=12, anchor="end"))
    f.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))      # вісь виходу
    f.append(arrow(ox, oy - axh, ox, oy - axh - 16, color=INK, sw=2))
    f.append(text(ox - 10, oy - axh - 6, "Vвих", size=12, anchor="end"))

    hi_y = oy - axh + 20       # рівень «1»
    lo_y = oy - 20             # рівень «0»
    f.append(text(ox - 10, hi_y + 4, "«1»", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 10, lo_y + 4, "«0»", size=12, color=MUTED, anchor="end"))

    # два пороги
    th_lo = ox + 200           # нижній поріг (повернення)
    th_hi = ox + 300           # верхній поріг (спрацювання)
    f.append(line(th_lo, oy, th_lo, oy - axh, color=NEG, sw=1.2, dash="5,4"))
    f.append(line(th_hi, oy, th_hi, oy - axh, color=POS, sw=1.2, dash="5,4"))
    f.append(text(th_lo, oy + 22, "Vн", size=12, color=NEG, bold=True))
    f.append(text(th_hi, oy + 22, "Vв", size=12, color=POS, bold=True))

    # мертва зона між порогами
    f.append(rect(th_lo, oy - axh, th_hi - th_lo, axh, fill="#eef6ef",
                  stroke="none", sw=0, rx=0))
    f.append(text((th_lo + th_hi) / 2, oy - axh - 4, "мертва зона",
                  size=11, color=FIELD, bold=True))

    # петля гістерезису: нижня гілка «0» зліва, стрибок угору на Vв,
    # верхня гілка «1» справа, стрибок униз на Vн
    # нижня гілка (вихід «0») від лівого краю до верхнього порога
    f.append(line(ox + 8, lo_y, th_hi, lo_y, color=INK, sw=2.6))
    # стрибок угору на верхньому порозі
    f.append(arrow(th_hi, lo_y, th_hi, hi_y, color=POS, sw=2.6))
    # верхня гілка (вихід «1») управо
    f.append(line(th_hi, hi_y, ox + axw - 10, hi_y, color=INK, sw=2.6))
    # верхня гілка вліво до нижнього порога
    f.append(line(th_lo, hi_y, th_hi, hi_y, color=INK, sw=2.6))
    # стрибок униз на нижньому порозі
    f.append(arrow(th_lo, hi_y, th_lo, lo_y, color=NEG, sw=2.6))
    # нижня гілка вліво
    f.append(line(ox + 8, lo_y, th_lo, lo_y, color=INK, sw=2.6))

    # стрілки напрямку обходу
    f.append(text((th_lo + th_hi) / 2, hi_y - 10, "→ вгору тільки на Vв",
                  size=10, color=POS))
    f.append(text((th_lo + th_hi) / 2, lo_y + 18, "← вниз тільки на Vн",
                  size=10, color=NEG))

    return render(os.path.join(IMG, "external-hysteresis.svg"), W, H, *f)


if __name__ == "__main__":
    fig_open_collector()
    fig_wired_and()
    fig_external_hysteresis()
    print("OK: figures ->", IMG)
