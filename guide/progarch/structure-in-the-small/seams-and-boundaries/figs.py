# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER = "#e08a1e"


def fig_seam():
    """Без шва vs зі швом: де стоїть точка підміни."""
    W, H = 960, 400
    frags = []

    # роздільник панелей
    frags.append(line(478, 84, 478, 360, color=LINE, sw=1.2, dash="4 5"))

    # ── ЛІВА: без шва ──────────────────────────────────────────────
    frags.append(text(240, 70, "БЕЗ ШВА", size=15, bold=True, color=MUTED))
    frags.append(rect(120, 118, 250, 150, fill="#fbfcfd", stroke=INK, sw=2))
    frags.append(text(245, 150, "політика", size=15, bold=True))
    frags.append(fitbox(148, 172, 194, 52, "read_sensor()", size=14,
                        fill="#fdecea", stroke=POS))
    frags.append(mtext(245, 302, ["підмінити = правити", "всередині політики"],
                       size=13, color=POS, lh=1.35))

    # ── ПРАВА: зі швом ─────────────────────────────────────────────
    frags.append(text(720, 70, "ЗІ ШВОМ", size=15, bold=True, color=FIELD))

    # два постачальники ліворуч від шва
    frags.append(fitbox(512, 120, 150, 52, "справжній\nдавач", size=13,
                        fill="#eef2f6"))
    frags.append(fitbox(512, 205, 150, 52, "давач-\nпідробка", size=13,
                        fill="#eef2f6", stroke=NEG))

    # шов — пунктирна вертикаль
    frags.append(text(690, 104, "шов", size=14, bold=True, color=POS))
    frags.append(line(690, 116, 690, 276, color=POS, sw=2.6, dash="6 5"))

    # стрілки постачальник → шов, і шов → політика
    frags.append(arrow(662, 146, 686, 168))
    frags.append(arrow(662, 231, 686, 196))
    frags.append(arrow(694, 182, 726, 182))

    # політика праворуч — не чіпаємо
    frags.append(rect(730, 132, 180, 100, fill="#fbfcfd", stroke=INK, sw=2))
    frags.append(text(820, 172, "політика", size=15, bold=True))
    frags.append(text(820, 196, "(не чіпаємо)", size=12.5, color=FIELD))

    # точка ввімкнення — під швом
    frags.append(line(690, 276, 690, 300, color=MUTED, sw=1.2, dash="3 4"))
    frags.append(mtext(690, 320, ["точка ввімкнення:", "main() обирає, що під'єднати"],
                       size=12.5, color=MUTED, lh=1.35))

    render(os.path.join(OUT, 'seam.svg'), W, H, *frags,
           title="Шов: підмінити поведінку, не редагуючи політику")


def fig_levels():
    """Три роди швів — за рівнем збірки, де стається підміна."""
    W, H = 940, 350
    frags = []

    gx = 60
    cols_w = [220, 300, 300]          # шов · коли · що
    xs = [gx]
    for w in cols_w:
        xs.append(xs[-1] + w)          # межі: 60, 280, 580, 880
    centers = [(xs[i] + xs[i + 1]) / 2 for i in range(3)]

    # заголовки колонок
    heads = ["шов", "коли підміняєш", "що підміняєш"]
    for c, h in enumerate(heads):
        frags.append(text(centers[c], 84, h, size=14, bold=True, color=MUTED))

    gy0, rh = 100, 62
    rows = [
        ("препроцесорний", "до компіляції", "текст (#define / #ifdef)", POS),
        ("лінк", "при збірці / лінкуванні", "об'єктний файл чи бібліотека", AMBER),
        ("об'єктний", "під час виконання", "об'єкт за інтерфейсом (DI)", FIELD),
    ]

    # горизонтальні лінії
    for r in range(len(rows) + 1):
        y = gy0 + r * rh
        frags.append(line(xs[0], y, xs[-1], y, color=LINE, sw=1.2))
    # вертикальні лінії
    for x in xs:
        frags.append(line(x, gy0, x, gy0 + len(rows) * rh, color=LINE, sw=1.2))

    # клітини
    for r, (name, when, what, col) in enumerate(rows):
        cy = gy0 + (r + 0.5) * rh + 5
        frags.append(text(centers[0], cy, name, size=14, bold=True, color=col))
        frags.append(text(centers[1], cy, when, size=13, color=INK))
        frags.append(text(centers[2], cy, what, size=13, color=INK))

    frags.append(text(W / 2, gy0 + len(rows) * rh + 34,
                      "що пізніше по конвеєру — то менше початкового коду чіпаєш",
                      size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'seam-levels.svg'), W, H, *frags,
           title="Три шви — за рівнем, де стається підміна")


def fig_linkseam():
    """Лінк-шов через LD_PRELOAD: завантажувач бере підробку першою."""
    W, H = 960, 470
    frags = []
    cx = 480

    # hub — твій код, зверху; його не чіпаємо
    frags.append(rect(325, 62, 310, 66, fill="#fbfcfd", stroke=INK, sw=2))
    frags.append(text(cx, 88, "hub — твій код (не чіпаємо)", size=14, bold=True))
    frags.append(text(cx, 112, "t = sensor_read();", size=13, color=MUTED))

    # стрілка вниз до завантажувача; підпис праворуч від лінії
    frags.append(arrow(cx, 132, cx, 168))
    frags.append(text(cx + 14, 154, "sensor_read()", size=12.5, color=INK, anchor="start"))

    # динамічний завантажувач
    frags.append(rect(330, 170, 300, 66, fill="#eef2f6", stroke=INK, sw=1.8))
    frags.append(text(cx, 196, "динамічний завантажувач", size=13.5, bold=True))
    frags.append(text(cx, 218, "шукає символ sensor_read", size=12.5, color=MUTED))

    by, bw, bh = 322, 310, 96
    lbx, rbx = 88, 562

    # ліва рамка — підробка, обрана (зелена)
    frags.append(rect(lbx, by, bw, bh, fill="#eafaf1", stroke=FIELD, sw=2.4))
    frags.append(text(lbx + bw / 2, by + 28, "fake_sensor.so — обрано", size=14, bold=True, color=FIELD))
    frags.append(text(lbx + bw / 2, by + 52, "LD_PRELOAD — стоїть ПЕРШИМ", size=12, color=INK))
    frags.append(text(lbx + bw / 2, by + 76, "return 19.0;", size=12.5, color=MUTED))

    # права рамка — вендор, пропущено (приглушена)
    frags.append(rect(rbx, by, bw, bh, fill="#f4f6f8", stroke=MUTED, sw=1.6))
    frags.append(text(rbx + bw / 2, by + 28, "libsensor.so — вендор", size=14, bold=True, color=MUTED))
    frags.append(text(rbx + bw / 2, by + 52, "справжнє залізо", size=12, color=MUTED))
    frags.append(text(rbx + bw / 2, by + 76, "тіло НЕ виконується", size=12.5, color=POS))

    # стрілки від завантажувача до гілок
    frags.append(arrow(432, 238, lbx + bw / 2, by - 4, color=FIELD, sw=2.4))
    frags.append(line(528, 238, rbx + bw / 2, by - 4, color=MUTED, sw=1.5, dash="5 5"))

    # точка ввімкнення — унизу
    frags.append(text(cx, by + bh + 34,
                      "точка ввімкнення: змінна LD_PRELOAD — поза кодом hub",
                      size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'link-seam.svg'), W, H, *frags,
           title="Лінк-шов: завантажувач бере підробку першою")


if __name__ == '__main__':
    fig_seam()
    fig_levels()
    fig_linkseam()
    print("figures written to", OUT)
