# -*- coding: utf-8 -*-
"""Фігури до статті «Cloud cost як архітектурний драйвер».
Вивід у ./img/. Імпортує svgkit зі scripts/ (не переписує)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_meters():
    """Власний сервер (одна фіксована ціна) проти хмари (чотири лічильники)."""
    W, H = 780, 430
    frags = []
    # Заголовки колонок
    frags.append(text(200, 52, "Куплений сервер", size=17, bold=True))
    frags.append(text(575, 52, "Хмара", size=17, bold=True))
    # Роздільна вертикаль
    frags.append(line(390, 74, 390, H - 26, color=MUTED, sw=1.2, dash="6 6"))

    # ── Ліва колонка: одна коробка, фіксована ціна ──
    bx, by, bw, bh = 90, 96, 220, 150
    frags.append(rect(bx, by, bw, bh, fill="#eef2f7", stroke=LINE, sw=2))
    frags.append(text(bx + bw / 2, by + 40, "заплатив раз", size=15, bold=True))
    frags.append(text(bx + bw / 2, by + 72, "0.10 $/год незмінно", size=13, color=MUTED))
    frags.append(text(bx + bw / 2, by + 100, "хоч працює, хоч спить", size=13, color=MUTED))
    # підпис-висновок під коробкою
    box, bwd, bhd = textbox(200, 300, "рахунок НЕ залежить\nвід того, що всередині",
                            size=13, fill="#eafaf1", stroke=FIELD, sw=1.6)
    frags.append(box)
    frags.append(text(200, 372, "стеля, поставлена наперед", size=12, color=MUTED, italic=True))

    # ── Права колонка: чотири лічильники ──
    meters = [
        ("Обчислення", "секунди × ядра"),
        ("Трафік", "ГБ, що вийшли/між зон"),
        ("Сховище", "ГБ × місяці"),
        ("Запити", "кожен виклик"),
    ]
    mx = 430
    mw = 300
    my0 = 92
    gap = 62
    for i, (name, unit) in enumerate(meters):
        y = my0 + i * gap
        frags.append(rect(mx, y, mw, 46, fill=FILL, stroke=LINE, sw=1.4))
        # кружок-лічильник
        frags.append(circle(mx + 26, y + 23, 13, fill="#fdf0e6", stroke=POS, sw=2))
        frags.append(text(mx + 26, y + 28, "⟳", size=15, color=POS, bold=True))
        frags.append(text(mx + 52, y + 20, name, size=13, bold=True, anchor="start"))
        frags.append(text(mx + 52, y + 37, unit, size=11, color=MUTED, anchor="start"))
    frags.append(text(mx + mw / 2, my0 + 4 * gap + 4, "форма системи задає швидкість кожного",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'meters.svg'), W, H, *frags)


def fig_always_on():
    """Профіль навантаження вирішує форму: рівний потік vs рідкі сплески."""
    W, H = 780, 470
    frags = []
    frags.append(text(W / 2, 40, "Профіль навантаження вирішує форму", size=17, bold=True))

    # Дві панелі-графіки
    def panel(ox, oy, pw, ph, title, bars, winner, sub):
        out = []
        # рамка панелі
        out.append(rect(ox, oy, pw, ph, fill=BG, stroke=MUTED, sw=1.2))
        out.append(text(ox + pw / 2, oy - 12, title, size=14, bold=True))
        # осі
        base_y = oy + ph - 40
        axis_x = ox + 34
        out.append(line(axis_x, oy + 24, axis_x, base_y, color=LINE, sw=1.4))     # Y
        out.append(line(axis_x, base_y, ox + pw - 20, base_y, color=LINE, sw=1.4))  # X
        out.append(text(ox + pw / 2, base_y + 26, "час доби (24 год)", size=11, color=MUTED))
        # стовпчики навантаження
        n = len(bars)
        slot = (pw - 60) / n
        maxbar = ph - 80
        for i, v in enumerate(bars):
            bh = maxbar * v
            bx = axis_x + 8 + i * slot
            out.append(rect(bx, base_y - bh, slot * 0.7, bh, fill="#dbe6f6", stroke=NEG, sw=1.2, rx=2))
        # переможець — рамка внизу
        wb, ww, wh = textbox(ox + pw / 2, oy + ph + 34, winner, size=12,
                             fill="#eafaf1", stroke=FIELD, sw=1.6, bold=True)
        out.append(wb)
        out.append(text(ox + pw / 2, oy + ph + 68, sub, size=11, color=MUTED, italic=True))
        return out

    # Ліва: рівний потік
    even = [0.75, 0.8, 0.78, 0.82, 0.79, 0.81, 0.77, 0.8]
    frags += panel(50, 90, 320, 200, "Рівний потік цілодобово", even,
                   "виграє машина,\nщо завжди напоготові",
                   "за секунду роботи вона дешевша")
    # Права: рідкі сплески
    spikes = [0.05, 0.9, 0.06, 0.05, 0.85, 0.05, 0.04, 0.7]
    frags += panel(410, 90, 320, 200, "Рідкі сплески з паузами", spikes,
                   "виграє код,\nщо вмикається на виклик",
                   "не платить за години простою")

    render(os.path.join(IMG, 'always-on-vs-ondemand.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_meters()
    fig_always_on()
    print("OK: meters.svg, always-on-vs-ondemand.svg")
