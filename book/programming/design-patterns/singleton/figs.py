# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_two_jobs():
    """Сінглтон склеює дві незалежні відповідальності в одному класі."""
    W, H = 720, 340
    frags = []

    # центральний клас
    cbody, cw, ch = textbox(360, 90, ["class Config", "(сінглтон)"],
                            size=15, bold=True, fill="#eef2ff", stroke=NEG, sw=2)
    frags.append(cbody)

    # ліва відповідальність
    lb, lw, lh = textbox(180, 240,
                         ["Відповідальність 1:", "«існує лиш один»", "(керує власним", "життєвим циклом)"],
                         size=13, fill="#e8f7ee", stroke=FIELD)
    frags.append(lb)
    # права відповідальність
    rb, rw, rh = textbox(560, 240,
                         ["Відповідальність 2:", "«доступний звідусіль»", "(глобальна точка", "доступу)"],
                         size=13, fill="#fdecea", stroke=POS)
    frags.append(rb)

    # стрілки від класу вниз до кожної відповідальності
    frags.append(arrow(320, 90 + ch / 2, 180, 240 - lh / 2, color=FIELD))
    frags.append(arrow(400, 90 + ch / 2, 560, 240 - rh / 2, color=POS))

    # підпис-висновок унизу
    frags.append(text(360, 318,
                      "Один патерн вирішує два різні питання — тому й тягне за собою два різні болі.",
                      size=13, italic=True, color=MUTED))

    render(os.path.join(OUT, 'two-jobs.svg'), W, H, *frags,
           title="Сінглтон поєднує дві незалежні речі в одному класі")


def fig_race():
    """Гонитва двох потоків на лінивій ініціалізації: народжуються ДВА об'єкти."""
    W, H = 760, 400
    frags = []

    # дві доріжки потоків
    ax, bx = 250, 560          # осі потоків A і B
    top, bot = 78, 348
    frags.append(text(ax, 58, "Потік A", size=14, bold=True))
    frags.append(text(bx, 58, "Потік B", size=14, bold=True))

    # події з центрами по y; осі малюємо СЕГМЕНТАМИ у проміжках, не крізь рамки
    yA1, yB2, yA3, yB4 = 115, 185, 255, 325
    half = 24  # пів_висота рамки події (2 рядки, size=12) з запасом

    def seg(cx, y_from, y_to):
        if y_to - y_from > 4:
            frags.append(line(cx, y_from, cx, y_to, color=MUTED, sw=1.2, dash="4 4"))

    # вісь A: top → подія1 → подія3 → bot (обходимо рамки)
    seg(ax, top, yA1 - half)
    seg(ax, yA1 + half, yA3 - half)
    seg(ax, yA3 + half, bot)
    # вісь B: top → подія2 → подія4 → bot
    seg(bx, top, yB2 - half)
    seg(bx, yB2 + half, yB4 - half)
    seg(bx, yB4 + half, bot)

    def event(cx, y, s, fill, stroke):
        b, w, h = textbox(cx, y, s, size=12, pad=8, fill=fill, stroke=stroke)
        frags.append(b)

    event(ax, yA1, ["1. бачить", "instance == null"], "#fff8e1", "#d9a400")
    event(bx, yB2, ["2. теж бачить", "instance == null"], "#fff8e1", "#d9a400")
    event(ax, yA3, ["3. створює", "об'єкт #1"], "#fdecea", POS)
    event(bx, yB4, ["4. створює", "об'єкт #2"], "#fdecea", POS)

    # стрілка часу (окремою колонкою ліворуч, повз усі рамки)
    frags.append(arrow(90, top, 90, bot, color=INK, sw=1.6))
    frags.append(text(90, bot + 22, "час", size=12, color=MUTED))

    # висновок
    frags.append(text(W / 2, 384,
                      "Обидва пройшли перевірку, поки жоден ще не записав instance — гарантія «один» зламана.",
                      size=13, italic=True, color=POS))

    render(os.path.join(OUT, 'race.svg'), W, H, *frags,
           title="Дві перевірки проскочили одночасно — і об'єктів стало два")


def fig_reorder_writes():
    """Переупорядкування записів: посилання стає видимим ДО добудови об'єкта."""
    W, H = 820, 470
    frags = []

    # дві колонки: як написано в коді  /  як дозволено виконати
    lx, rx = 220, 600
    frags.append(text(lx, 62, "Як написано в коді", size=15, bold=True))
    frags.append(text(rx, 62, "Один із дозволених порядків", size=15, bold=True))

    # ── ліва колонка: три логічні кроки одного присвоєння ──
    steps_l = [
        (["1. виділити пам'ять", "під об'єкт"], "#eef2ff", NEG),
        (["2. викликати конструктор", "(заповнити поля)"], "#e8f7ee", FIELD),
        (["3. записати посилання", "helper = адреса"], "#fff8e1", "#d9a400"),
    ]
    yl = [120, 210, 300]
    hboxL = 40
    for (s, fl, st), y in zip(steps_l, yl):
        b, w, h = textbox(lx, y, s, size=12, pad=8, fill=fl, stroke=st)
        frags.append(b)
    # порядок 1→2→3 ліворуч
    frags.append(arrow(lx, yl[0] + hboxL, lx, yl[1] - hboxL, color=MUTED))
    frags.append(arrow(lx, yl[1] + hboxL, lx, yl[2] - hboxL, color=MUTED))

    # ── права колонка: 3 перед 2 (запис посилання випередив заповнення полів) ──
    steps_r = [
        (["1. виділити пам'ять", "під об'єкт"], "#eef2ff", NEG),
        (["3. записати посилання", "helper = адреса"], "#fff8e1", "#d9a400"),
        (["2. викликати конструктор", "(заповнити поля)"], "#e8f7ee", FIELD),
    ]
    yr = [120, 210, 300]
    for (s, fl, st), y in zip(steps_r, yr):
        b, w, h = textbox(rx, y, s, size=12, pad=8, fill=fl, stroke=st)
        frags.append(b)
    frags.append(arrow(rx, yr[0] + hboxL, rx, yr[1] - hboxL, color=MUTED))
    frags.append(arrow(rx, yr[1] + hboxL, rx, yr[2] - hboxL, color=MUTED))

    # вікно небезпеки праворуч: між кроком 3 і кроком 2
    frags.append(text(rx + 175, 210, "◄ тут helper", size=11.5, color=POS, bold=True, anchor="middle"))
    frags.append(text(rx + 175, 228, "вже не null,", size=11.5, color=POS, anchor="middle"))
    frags.append(text(rx + 175, 246, "а поля ще", size=11.5, color=POS, anchor="middle"))
    frags.append(text(rx + 175, 264, "порожні", size=11.5, color=POS, anchor="middle"))

    # інший потік зазирає саме у це вікно
    ob, ow, oh = textbox(W / 2, 390,
                         ["Інший потік бачить helper != null → пропускає створення →",
                          "повертає напівготовий об'єкт із полями за замовчуванням"],
                         size=12.5, pad=10, fill="#fdecea", stroke=POS, bold=False)
    frags.append(ob)

    frags.append(text(W / 2, 452,
                      "«Записати посилання» і «заповнити поля» — різні записи; ніщо не тримає їхній порядок.",
                      size=12.5, italic=True, color=MUTED))

    render(os.path.join(OUT, 'reorder-writes.svg'), W, H, *frags,
           title="Переупорядкування: адреса стала видимою раніше, ніж об'єкт готовий")


def fig_barrier():
    """Бар'єр пам'яті (volatile): усі записи об'єкта — ДО публікації посилання."""
    W, H = 780, 420
    frags = []

    cx = W / 2
    # верх: записи полів (мають статися першими)
    b1, w1, h1 = textbox(cx, 105,
                         ["записати всі поля об'єкта", "(конструктор до кінця)"],
                         size=13, pad=10, fill="#e8f7ee", stroke=FIELD)
    frags.append(b1)

    # бар'єр — суцільна смуга з написом
    by = 190
    frags.append(rect(cx - 300, by - 18, 600, 36, fill="#fdecea", stroke=POS, sw=2, rx=8))
    frags.append(text(cx, by + 5, "БАР'ЄР ПАМ'ЯТІ (release): нічого згори не перетне його вниз",
                      size=12.5, bold=True, color=POS))

    # низ: публікація посилання (лише ПІСЛЯ бар'єра)
    b2, w2, h2 = textbox(cx, 285,
                         ["опублікувати посилання", "helper = адреса"],
                         size=13, pad=10, fill="#fff8e1", stroke="#d9a400")
    frags.append(b2)

    frags.append(arrow(cx, 105 + h1 / 2, cx, by - 20, color=INK, sw=1.6))
    frags.append(arrow(cx, by + 20, cx, 285 - h2 / 2, color=INK, sw=1.6))

    # висновок
    frags.append(text(cx, 355,
                      "Хто прочитав ненульове helper, той (через парний acquire-бар'єр) бачить і всі поля.",
                      size=13, italic=True, color=FIELD))
    frags.append(text(cx, 388,
                      "volatile у Java (з JSR-133) і std::atomic у C++ ставлять цю пару бар'єрів за тебе.",
                      size=12.5, italic=True, color=MUTED))

    render(os.path.join(OUT, 'barrier.svg'), W, H, *frags,
           title="Бар'єр не дає публікації випередити заповнення полів")


def fig_attack_surface():
    """П'ять дверей до другого екземпляра й що кожні з них замикає."""
    W, H = 900, 500
    frags = []

    # центр — «єдиний екземпляр», який усі атаки намагаються роздвоїти
    cx, cy = W / 2, 258
    cbody, cw, ch = textbox(cx, cy, ["ЄДИНИЙ", "екземпляр"],
                            size=15, bold=True, fill="#e8f7ee", stroke=FIELD, sw=2.5,
                            min_w=150)

    # п'ять дверей навколо. «Замок» вписано ТРЕТІМ рядком у ту саму рамку —
    # тож жодного вільного напису, який могла б перетнути стрілка.
    doors = [
        (168, 128, ["1. Гонитва потоків", "два потоки — два new",
                    "→ замок: ідіом платформи"], "#fff8e1", "#d9a400"),
        (732, 128, ["2. Серіалізація", "readObject робить новий",
                    "→ замок: readResolve / enum"], "#fdecea", POS),
        (168, 388, ["3. Рефлексія", "setAccessible(true) в обхід",
                    "→ замок: перевірка / enum"], "#fdecea", POS),
        (732, 388, ["4. Клонування", "clone() віддає копію",
                    "→ замок: заборонити clone"], "#fdecea", POS),
        (cx, 74,   ["5. Кілька завантажувачів класів",
                    "клас × loader = свій екземпляр",
                    "→ замок: один спільний loader"], "#eef2ff", NEG),
    ]

    # спершу рахуємо рамки, потім стрілки (лягають ПІД рамки); стрілка йде
    # від краю рамки-двері до краю центральної рамки — повз чужі написи.
    boxes = []
    for dx, dy, lines, fill, stroke in doors:
        b, w, h = textbox(dx, dy, lines, size=12, pad=9, fill=fill, stroke=stroke)
        boxes.append((dx, dy, w, h, b, stroke))

    def border_pt(bx, by, bw, bh, tx, ty, pad=0):
        """Точка на межі прямокутника (центр bx,by; розмір bw×bh + pad)
        у напрямку до (tx,ty). Так стрілка стартує/впирається РІВНО в край,
        а не всередині рамки."""
        dx, dy = tx - bx, ty - by
        hw, hh = bw / 2 + pad, bh / 2 + pad
        if dx == 0 and dy == 0:
            return bx, by
        sx = hw / abs(dx) if dx else float('inf')
        sy = hh / abs(dy) if dy else float('inf')
        s = min(sx, sy)
        return bx + dx * s, by + dy * s

    for dx, dy, w, h, b, stroke in boxes:
        sx, sy = border_pt(dx, dy, w, h, cx, cy)               # край двері → центр
        ex, ey = border_pt(cx, cy, cw, ch, dx, dy, pad=8)      # край центру → двері
        frags.append(arrow(sx, sy, ex, ey, color=stroke, sw=1.6))

    frags.append(cbody)
    for dx, dy, w, h, b, stroke in boxes:
        frags.append(b)

    frags.append(text(W / 2, H - 18,
                      "Наївний замок закриває лише двері 1; решта чотири відчиняються незалежно.",
                      size=13, italic=True, color=MUTED))

    render(os.path.join(OUT, 'attack-surface.svg'), W, H, *frags,
           title="П'ять дверей до другого екземпляра — і що кожні замикає")


if __name__ == '__main__':
    fig_two_jobs()
    fig_race()
    fig_reorder_writes()
    fig_barrier()
    fig_attack_surface()
    print('figures written to', OUT)
