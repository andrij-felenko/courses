# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def diamond(cx, cy, w, h, s, size=13, fill="#eef7f0", stroke=FIELD, sw=2, color=INK):
    """Ромб-розвилка з написом усередині."""
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        cx, cy - h / 2, cx + w / 2, cy, cx, cy + h / 2, cx - w / 2, cy)
    body = ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (pts, fill, stroke, sw))
    fs = fit_font(s, w * 0.72, size, bold=True)
    body += text(cx, cy + fs * 0.35, s, size=fs, color=color, bold=True)
    return body


# ── Фігура 1: if/else — розвилка потоку ─────────────────────────────────────
def fig_branch():
    W, H = 660, 430
    parts = []
    cx = W / 2
    # вхідний потік
    parts.append(fitbox(cx - 90, 44, 180, 40, "виконання йде\nзверху вниз", size=13,
                        fill="#f4f6f8", stroke=MUTED))
    parts.append(arrow(cx, 84, cx, 116))
    # розвилка
    dcy = 158
    parts.append(diamond(cx, dcy, 220, 84, "умова істинна?", size=15))
    # дві гілки
    lx, rx = 150, 510
    by = 300
    parts.append(arrow(cx - 30, dcy + 30, lx + 40, by - 30))
    parts.append(arrow(cx + 30, dcy + 30, rx - 40, by - 30))
    parts.append(text(cx - 118, dcy + 66, "так", size=14, color=FIELD, bold=True, anchor="start"))
    parts.append(text(cx + 118, dcy + 66, "ні", size=14, color=POS, bold=True, anchor="end"))
    parts.append(fitbox(lx - 90, by - 30, 180, 60, "гілка if\nробимо одне", size=14,
                        fill="#eef7f0", stroke=FIELD, bold=True))
    parts.append(fitbox(rx - 90, by - 30, 180, 60, "гілка else\nробимо інше", size=14,
                        fill="#fdecea", stroke=POS, bold=True))
    # злиття
    jy = 388
    parts.append(arrow(lx, by + 30, cx - 30, jy - 8))
    parts.append(arrow(rx, by + 30, cx + 30, jy - 8))
    b, w, h = textbox(cx, jy + 6, "далі — спільний шлях", size=13, fill="#f4f6f8", stroke=INK)
    parts.append(b)
    return render(os.path.join(IMG, 'branch-fork.svg'), W, H, *parts)


# ── Фігура 2: три форми циклу — де стоїть перевірка ──────────────────────────
def loop_col(x, w, title, order, note):
    """Колонка-цикл: заголовок, стрілки-послідовність із перевіркою у своєму місці."""
    parts = []
    cx = x + w / 2
    parts.append(text(cx, 64, title, size=16, bold=True, color=NEG))
    y = 90
    boxes = []
    for kind, label in order:
        if kind == "test":
            b = diamond(cx, y + 26, w - 40, 56, label, size=12)
            parts.append(b)
            boxes.append((y, y + 52))
            y += 52
        else:
            fill = "#eef7f0" if kind == "body" else "#f4f6f8"
            stroke = FIELD if kind == "body" else MUTED
            parts.append(fitbox(cx - (w - 50) / 2, y, w - 50, 40, label, size=12,
                                fill=fill, stroke=stroke, bold=(kind == "body")))
            boxes.append((y, y + 40))
            y += 40
        y += 26
        if y < 320:
            parts.append(arrow(cx, boxes[-1][1], cx, boxes[-1][1] + 22))
    # нотатка внизу — багаторядкова (явні переноси), щоб текст стовпця не налазив на сусідній
    parts.append(fitbox(cx - (w - 40) / 2, 334, w - 40, 66, note, size=11,
                        fill="#fff", stroke=MUTED, color=MUTED))
    return parts


def fig_loops():
    W, H = 720, 420
    cols = [
        (10, 220, "while", [("test", "умова?"), ("body", "тіло циклу"), ("back", "назад до перевірки")],
         "перевірка ПЕРЕД тілом:\nякщо умова хибна одразу —\nтіло не виконається ні разу"),
        (250, 220, "do…while", [("body", "тіло циклу"), ("test", "умова?"), ("back", "назад")],
         "перевірка ПІСЛЯ тіла:\nтіло виконається\nщонайменше один раз"),
        (490, 220, "for", [("body", "init: i = 0"), ("test", "i < N?"), ("body", "тіло + i++")],
         "три частини поруч:\nстарт, перевірка, крок —\nусе на очах"),
    ]
    parts = [text(W / 2, 28, "Три форми циклу: різниця — де стоїть перевірка", size=16, bold=True)]
    for x, w, t, order, note in cols:
        parts += loop_col(x, w, t, order, note)
    # розділові лінії
    parts.append(line(240, 50, 240, 320, color="#dfe3e8", sw=1))
    parts.append(line(480, 50, 480, 320, color="#dfe3e8", sw=1))
    return render(os.path.join(IMG, 'loop-shapes.svg'), W, H, *parts)


# ── Фігура 3: суперцикл прошивки ─────────────────────────────────────────────
def fig_superloop():
    W, H = 560, 470
    parts = [text(W / 2, 28, "Суперцикл: серце будь-якої прошивки", size=16, bold=True)]
    cx = W / 2
    # setup — один раз
    parts.append(fitbox(cx - 130, 52, 260, 44, "setup(): один раз на старті\n(тактування, GPIO, периферія)",
                        size=12, fill="#f4f6f8", stroke=MUTED))
    parts.append(arrow(cx, 96, cx, 128))
    # кільце
    ring_top = 140
    steps = [
        ("зчитати", "давачі, кнопки, час", "#eef7f0", FIELD),
        ("вирішити", "if / else за станом", "#eef7f0", FIELD),
        ("подіяти", "мотори, світло, вивід", "#eef7f0", FIELD),
    ]
    y = ring_top
    for i, (t, sub, fill, stroke) in enumerate(steps):
        parts.append(fitbox(cx - 130, y, 260, 52, "%s\n%s" % (t, sub), size=13,
                            fill=fill, stroke=stroke, bold=True))
        if i < len(steps) - 1:
            parts.append(arrow(cx, y + 52, cx, y + 74))
        y += 74
    # стрілка повернення (петля)
    loop_x = cx + 165
    bottom = y - 74 + 52
    parts.append(line(cx + 130, bottom - 26, loop_x, bottom - 26, color=NEG, sw=2))
    parts.append(line(loop_x, bottom - 26, loop_x, ring_top + 26, color=NEG, sw=2))
    parts.append(arrow(loop_x, ring_top + 26, cx + 130, ring_top + 26, color=NEG, sw=2))
    parts.append(text(loop_x + 8, (ring_top + bottom) / 2, "while(1)", size=14,
                     color=NEG, bold=True, anchor="start"))
    parts.append(text(loop_x + 8, (ring_top + bottom) / 2 + 20, "нескінченно", size=11,
                     color=MUTED, anchor="start"))
    return render(os.path.join(IMG, 'superloop.svg'), W, H, *parts)


if __name__ == "__main__":
    fig_branch()
    fig_loops()
    fig_superloop()
    print("figures written to", IMG)
