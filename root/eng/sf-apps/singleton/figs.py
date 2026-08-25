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


# ── фігури детальної статті ──────────────────────────────────────────────────

def fig_design_matrix():
    """Дві осі проєктного простору: кардинальність × досяжність. Сінглтон — лише одна клітина."""
    W, H = 860, 478
    frags = []
    c1x, c2x, cw = 190, 505, 300
    r1y, r2y, ch = 95, 230, 120

    frags.append(fitbox(c1x, r1y, cw, ch,
                        ["Єдиний екземпляр,", "переданий явно", "(здоровий випадок)"],
                        size=13, fill="#e8f7ee", stroke=FIELD))
    frags.append(fitbox(c2x, r1y, cw, ch,
                        ["СІНГЛТОН", "«один» + доступ звідусіль", "(патерн GoF)"],
                        size=13, fill="#fdecea", stroke=POS, sw=2.6))
    frags.append(fitbox(c1x, r2y, cw, ch,
                        ["Звичайні обʼєкти", "(буденне ООП)"],
                        size=13, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(c2x, r2y, cw, ch,
                        ["Глобальний реєстр,", "розсіяний спільний стан"],
                        size=13, fill="#fff8e1", stroke="#d9a400"))

    frags.append(text(105, 82, "КІЛЬКІСТЬ", size=12, bold=True, color=MUTED))
    frags.append(text(105, r1y + ch / 2 + 5, "ОДИН", size=13, bold=True))
    frags.append(text(105, r2y + ch / 2 + 5, "БАГАТО", size=13, bold=True))

    coly = r2y + ch + 24
    frags.append(text(c1x + cw / 2, coly, "передають руками", size=13))
    frags.append(text(c2x + cw / 2, coly, "доступний глобально", size=13))
    frags.append(text(W / 2, coly + 28, "ДОСЯЖНІСТЬ", size=12, bold=True, color=MUTED))

    frags.append(text(W / 2, 456,
                      "Сінглтон — лише одна клітина; у рядку «один» ліворуч стоїть здоровіша заміна — єдиний обʼєкт, переданий руками.",
                      size=12.5, italic=True, color=MUTED))

    render(os.path.join(OUT, 'design-matrix.svg'), W, H, *frags,
           title="Дві незалежні осі: скільки екземплярів і як до них дотягуються")


def fig_scope_ladder():
    """«Один» — відносно якої межі: від потоку до кластера static тримає «один» лише вузько."""
    W, H = 900, 500
    frags = []
    bx, bw, bh, gap, y0 = 150, 690, 60, 16, 66
    bands = [
        (["потік (thread-local)",
          "по одному екземпляру на КОЖЕН потік — «один» лише в межах потоку"],
         "#e8f7ee", FIELD),
        (["завантажувач класів / бібліотека .so",
          "сюди дістає static: рівно один на кожен loader — кілька loader-ів дають кілька «єдиних»"],
         "#e8f7ee", FIELD),
        (["процес",
          "звична мовчазна умова сінглтона: «один» — якщо в процесі один завантажувач"],
         "#eef2ff", NEG),
        (["машина / хост — кілька процесів",
          "кожен процес тримає свою копію: «один» уже не тримається"],
         "#fff8e1", "#d9a400"),
        (["кластер — багато машин",
          "спільної памʼяті немає зовсім → потрібна зовнішня координація (вибір лідера)"],
         "#fdecea", POS),
    ]
    for i, (lines, fill, stroke) in enumerate(bands):
        y = y0 + i * (bh + gap)
        frags.append(fitbox(bx, y, bw, bh, lines, size=12.5, fill=fill, stroke=stroke))

    ytop, ybot = y0 + 6, y0 + 4 * (bh + gap) + bh - 6
    frags.append(arrow(95, ytop, 95, ybot, color=INK, sw=1.6))
    frags.append(text(95, ytop - 12, "вужче", size=11, color=MUTED))
    frags.append(text(95, ybot + 20, "ширше", size=11, color=MUTED))

    frags.append(text(W / 2, ybot + 48,
                      "static дає один екземпляр лише в межах одного завантажувача класів; ширші межі «один» не тримають.",
                      size=12.5, italic=True, color=MUTED))

    render(os.path.join(OUT, 'scope-ladder.svg'), W, H, *frags,
           title="Межа єдиності: у яких рамках «один» справді один")


def fig_identity_state():
    """Сінглтон обмежує ідентичність (один обʼєкт); моностейт — стан (один спільний на багато обʼєктів)."""
    W, H = 920, 400
    frags = []

    def border_pt(bx, by, bw, bh, tx, ty, pad=0):
        dx, dy = tx - bx, ty - by
        hw, hh = bw / 2 + pad, bh / 2 + pad
        if dx == 0 and dy == 0:
            return bx, by
        sx = hw / abs(dx) if dx else float('inf')
        sy = hh / abs(dy) if dy else float('inf')
        s = min(sx, sy)
        return bx + dx * s, by + dy * s

    frags.append(line(460, 46, 460, 344, color=MUTED, sw=1.2, dash="5 5"))

    # ── ліворуч: СІНГЛТОН ──
    frags.append(text(235, 58, "СІНГЛТОН", size=15, bold=True))
    cboxes = []
    for i, cx in enumerate([120, 235, 350]):
        b, w, h = textbox(cx, 102, ["клієнт %d" % (i + 1)], size=12, fill="#eef2ff", stroke=NEG)
        cboxes.append((cx, 102, w, h))
    ob, ow, oh = textbox(235, 250, ["єдиний", "обʼєкт"], size=14, bold=True,
                         fill="#e8f7ee", stroke=FIELD, sw=2.5)
    for cx, cy, w, h in cboxes:
        ex, ey = border_pt(235, 250, ow, oh, cx, cy, pad=6)
        frags.append(arrow(cx, cy + h / 2, ex, ey, color=MUTED, sw=1.5))
    for cx, cy, w, h in cboxes:
        b, _, _ = textbox(cx, cy, ["клієнт %d" % ([120, 235, 350].index(cx) + 1)],
                          size=12, fill="#eef2ff", stroke=NEG)
        frags.append(b)
    frags.append(ob)
    frags.append(text(235, 305, "одна ідентичність — один стан", size=12.5, italic=True, color=MUTED))

    # ── праворуч: МОНОСТЕЙТ ──
    frags.append(text(690, 58, "МОНОСТЕЙТ (Borg)", size=15, bold=True))
    oboxes = []
    for i, cx in enumerate([560, 690, 820]):
        oboxes.append((cx, 102, "ABC"[i]))
    sb, sw_, sh = textbox(690, 250, ["спільний стан", "(static-поля класу)"], size=13, bold=True,
                          fill="#fff8e1", stroke="#d9a400", sw=2.5)
    for cx, cy, letter in oboxes:
        b, w, h = textbox(cx, cy, ["обʼєкт %s" % letter], size=12, fill="#eef2ff", stroke=NEG)
        ex, ey = border_pt(690, 250, sw_, sh, cx, cy, pad=6)
        frags.append(arrow(cx, cy + h / 2, ex, ey, color=MUTED, sw=1.5))
    for cx, cy, letter in oboxes:
        b, w, h = textbox(cx, cy, ["обʼєкт %s" % letter], size=12, fill="#eef2ff", stroke=NEG)
        frags.append(b)
    frags.append(sb)
    frags.append(text(690, 305, "різні ідентичності — ОДИН спільний стан", size=12.5, italic=True, color=MUTED))

    frags.append(text(W / 2, 378,
                      "Сінглтон обмежує кількість обʼєктів; моностейт — кількість станів. Обидва лишаються глобальним станом.",
                      size=12.5, italic=True, color=MUTED))

    render(os.path.join(OUT, 'identity-state.svg'), W, H, *frags,
           title="Дві різні «єдиності»: один обʼєкт проти одного спільного стану")


def fig_init_order_fiasco():
    """Фіаско порядку статичної ініціалізації: A у конструкторі читає ще не збудований B."""
    W, H = 820, 372
    frags = []

    a, aw, ah = textbox(230, 140, ["глобальний обʼєкт A", "(файл a.cpp)"], size=13,
                        fill="#eef2ff", stroke=NEG)
    b, bw2, bh2 = textbox(590, 140, ["глобальний обʼєкт B", "(файл b.cpp)"], size=13,
                          fill="#e8f7ee", stroke=FIELD)

    frags.append(text(410, 116, "конструктор A читає B", size=12, color=INK))
    frags.append(arrow(230 + aw / 2, 140, 590 - bw2 / 2, 140, color=INK, sw=1.6))
    frags.append(a)
    frags.append(b)

    ban, banw, banh = textbox(410, 232, ["Порядок ініціалізації A і B між файлами",
                                          "стандартом C++ НЕ визначений"],
                              size=13, fill="#fdecea", stroke=POS, sw=2)
    frags.append(ban)

    fix, fw, fh = textbox(410, 320, ["Ліки: сінглтон Меєрса — B живе у функції як локальний static",
                                      "й будується при першому зверненні (construct-on-first-use)"],
                          size=12.5, fill="#e8f7ee", stroke=FIELD)
    frags.append(fix)

    render(os.path.join(OUT, 'init-order-fiasco.svg'), W, H, *frags,
           title="Якщо B ще не збудований, конструктор A читає порожнечу")


# ── фігури вставки proj-multiton-registry ────────────────────────────────────

def fig_one_to_many():
    """Сінглтон — одне статичне поле; мультитон — словник ключ→екземпляр."""
    W, H = 900, 430
    frags = []

    # ── ліворуч: сінглтон ──
    frags.append(text(215, 62, "СІНГЛТОН", size=15, bold=True))
    a, aw, ah = textbox(215, 128, ["getInstance()"], size=13, fill="#eef2ff", stroke=NEG)
    b, bw, bh = textbox(215, 236, ["єдиний", "екземпляр"], size=13, bold=True,
                        fill="#e8f7ee", stroke=FIELD, sw=2.2)
    frags.append(arrow(215, 128 + ah / 2, 215, 236 - bh / 2, color=MUTED))
    frags.append(a)
    frags.append(b)
    frags.append(text(215, 316, "одне статичне поле на весь клас", size=12, italic=True, color=MUTED))

    # роздільник
    frags.append(line(445, 46, 445, 372, color=MUTED, sw=1.2, dash="5 5"))

    # ── праворуч: мультитон / реєстр ──
    frags.append(text(670, 62, "МУЛЬТИТОН / РЕЄСТР", size=15, bold=True))
    hdr, hw, hh = textbox(670, 122, ["getInstance(ключ)"], size=13, fill="#eef2ff", stroke=NEG)
    frags.append(hdr)
    frags.append(arrow(670, 122 + hh / 2, 670, 170, color=MUTED))

    rows = [("«orders»", "Logger #1"), ("«billing»", "Logger #2"), ("«auth»", "Logger #3")]
    ys = [192, 252, 312]
    kx, ix = 585, 782
    for (k, inst), y in zip(rows, ys):
        kb, kw, kh = textbox(kx, y, [k], size=12, fill="#fff8e1", stroke="#d9a400")
        ib, iw, ih = textbox(ix, y, [inst], size=12, bold=True, fill="#e8f7ee", stroke=FIELD)
        frags.append(arrow(kx + kw / 2, y, ix - iw / 2, y, color=MUTED))
        frags.append(kb)
        frags.append(ib)

    frags.append(text(W / 2, 410,
                      "Один екземпляр на КОЖЕН ключ: та сама «єдиність», лише проіндексована іменем.",
                      size=13, italic=True, color=MUTED))

    render(os.path.join(OUT, 'one-to-many.svg'), W, H, *frags,
           title="Від «одного» до «одного на ключ»")


def fig_get_or_create():
    """Наївний get-or-create гониться на однаковому ключі; атомарний дає один."""
    W, H = 900, 470
    frags = []
    frags.append(line(450, 60, 450, 388, color=MUTED, sw=1.2, dash="5 5"))

    # ── ліворуч: наївно (два кроки) ──
    frags.append(fitbox(60, 70, 340, 50,
                        ["Наївно: «глянути, потім створити»", "— два окремі кроки"],
                        size=13, fill="#fdecea", stroke=POS, bold=True))
    a1, a1w, a1h = textbox(160, 168, ["потік A:", "ключа нема"], size=12, fill="#fff8e1", stroke="#d9a400")
    b1, b1w, b1h = textbox(320, 168, ["потік B:", "ключа нема"], size=12, fill="#fff8e1", stroke="#d9a400")
    frags.append(a1)
    frags.append(b1)
    a2, a2w, a2h = textbox(160, 258, ["A створює", "pool"], size=12, fill="#eef2ff", stroke=NEG)
    b2, b2w, b2h = textbox(320, 258, ["B створює", "pool"], size=12, fill="#eef2ff", stroke=NEG)
    frags.append(arrow(160, 168 + a1h / 2, 160, 258 - a2h / 2, color=MUTED))
    frags.append(arrow(320, 168 + b1h / 2, 320, 258 - b2h / 2, color=MUTED))
    frags.append(a2)
    frags.append(b2)
    res, rw, rh = textbox(240, 346, ["два пули на одну БД —", "ліміт з'єднань подвоєно"],
                          size=12.5, fill="#fdecea", stroke=POS, sw=2)
    frags.append(arrow(160, 258 + a2h / 2, 240 - rw / 2 + 24, 346 - rh / 2, color=MUTED))
    frags.append(arrow(320, 258 + b2h / 2, 240 + rw / 2 - 24, 346 - rh / 2, color=MUTED))
    frags.append(res)

    # ── праворуч: атомарно ──
    frags.append(fitbox(510, 70, 340, 50,
                        ["Атомарно: перевірка й створення", "— одним неподільним кроком"],
                        size=13, fill="#e8f7ee", stroke=FIELD, bold=True))
    c1, c1w, c1h = textbox(680, 175, ["computeIfAbsent(ключ, build)"], size=12.5,
                           fill="#eef2ff", stroke=NEG)
    c2, c2w, c2h = textbox(680, 258, ["перевірка + створення", "під одним замком"], size=12.5,
                           fill="#fff8e1", stroke="#d9a400")
    c3, c3w, c3h = textbox(680, 346, ["рівно один pool", "на ключ"], size=12.5, bold=True,
                           fill="#e8f7ee", stroke=FIELD, sw=2)
    frags.append(arrow(680, 175 + c1h / 2, 680, 258 - c2h / 2, color=MUTED))
    frags.append(arrow(680, 258 + c2h / 2, 680, 346 - c3h / 2, color=MUTED))
    frags.append(c1)
    frags.append(c2)
    frags.append(c3)

    frags.append(text(W / 2, 444,
                      "Гонитва сінглтона вертається на кожен ключ; лікують її тим самим — атомарним get-or-create.",
                      size=12.5, italic=True, color=MUTED))

    render(os.path.join(OUT, 'get-or-create.svg'), W, H, *frags,
           title="Get-or-create: наївно двоїть, атомарно — один")


def fig_unbounded_growth():
    """Обмежені ключі — мапа мала; необмежені — росте без меж (витік)."""
    W, H = 900, 462
    frags = []
    frags.append(line(450, 60, 450, 360, color=MUTED, sw=1.2, dash="5 5"))

    # ── ліворуч: обмежені ключі ──
    frags.append(fitbox(70, 70, 320, 46, ["Обмежені ключі: БД, модулі"],
                        size=13, bold=True, fill="#e8f7ee", stroke=FIELD))
    mx, my, mw = 240, 150, 250
    frags.append(rect(mx - mw / 2, my, mw, 118, fill="#f4f6f8", stroke=FIELD, sw=1.8))
    for i, k in enumerate(["orders  →  pool", "billing  →  pool", "auth  →  pool"]):
        yy = my + 16 + i * 32
        frags.append(fitbox(mx - mw / 2 + 14, yy, mw - 28, 24, [k],
                            size=12, fill="#ffffff", stroke=MUTED))
    frags.append(text(240, 300, "скінченна множина — мапа лишається малою",
                      size=12, italic=True, color=MUTED))

    # ── праворуч: необмежені ключі ──
    frags.append(fitbox(510, 70, 320, 46, ["Необмежені ключі: на юзера / запит"],
                        size=13, bold=True, fill="#fdecea", stroke=POS))
    mx2, my2, mw2 = 690, 128, 260
    frags.append(rect(mx2 - mw2 / 2, my2, mw2, 196, fill="#f4f6f8", stroke=POS, sw=1.8))
    labels = ["user:1041 → pool", "user:1042 → pool", "user:1043 → pool",
              "user:1044 → pool", "…  росте без меж"]
    for i, k in enumerate(labels):
        yy = my2 + 16 + i * 33
        st = POS if i == len(labels) - 1 else MUTED
        frags.append(fitbox(mx2 - mw2 / 2 + 14, yy, mw2 - 28, 24, [k],
                            size=12, fill="#ffffff", stroke=st))
    frags.append(text(690, 348, "кожен колись побачений ключ лишається назавжди → витік",
                      size=11.5, italic=True, color=POS))

    # ── нижня смуга: ліки ──
    frags.append(fitbox(90, 388, 720, 54,
                        ["Ліки: евікція — LRU / межа розміру / TTL. І при видаленні ЗАКРИВАТИ ресурс",
                         "(pool.close, файл, сокет), а не лише кидати посилання — інакше витік дескрипторів."],
                        size=12.5, fill="#eef2ff", stroke=NEG))

    render(os.path.join(OUT, 'unbounded-growth.svg'), W, H, *frags,
           title="Мультитон живе вічно: обмежені ключі — дрібниця, необмежені — витік")


def fig_registry_di():
    """Купа прихованих сінглтонів проти одного реєстру, переданого явно."""
    W, H = 940, 470
    frags = []
    frags.append(line(470, 56, 470, 400, color=MUTED, sw=1.2, dash="5 5"))

    # ── ліворуч: приховані глобальні ──
    frags.append(fitbox(60, 70, 360, 46, ["Купа прихованих сінглтонів"],
                        size=13.5, bold=True, fill="#fdecea", stroke=POS))
    svcs = [("OrderSvc", 130), ("BillingSvc", 245), ("AuthSvc", 360)]
    sboxes = []
    for name, x in svcs:
        b, w, h = textbox(x, 165, [name], size=12, fill="#eef2ff", stroke=NEG)
        sboxes.append((x, w, h))
        frags.append(b)
    globs = [("Logger.get(k)", 130), ("Config.get()", 245), ("Clock.get()", 360)]
    for (name, x), (sx, sw_, sh) in zip(globs, sboxes):
        gb, gw, gh = textbox(x, 300, [name], size=12, fill="#fff8e1", stroke="#d9a400")
        frags.append(arrow(x, 165 + sh / 2, x, 300 - gh / 2, color=POS, sw=1.4))
        frags.append(gb)
    frags.append(text(245, 356, "3 приховані залежності · 0 точок підміни",
                      size=12, italic=True, color=POS))

    # ── праворуч: один реєстр ──
    frags.append(fitbox(510, 70, 370, 46, ["Один реєстр, переданий явно"],
                        size=13.5, bold=True, fill="#e8f7ee", stroke=FIELD))
    root, rtw, rth = textbox(705, 150, ["корінь збірки"], size=12, fill="#eef2ff", stroke=NEG)
    reg, regw, regh = textbox(705, 228, ["LoggerRegistry", "(один на програму)"], size=12,
                              bold=True, fill="#e8f7ee", stroke=FIELD, sw=2.2)
    frags.append(arrow(705, 150 + rth / 2, 705, 228 - regh / 2, color=MUTED))
    frags.append(root)
    frags.append(reg)
    for name, x in [("OrderSvc", 595), ("BillingSvc", 705), ("AuthSvc", 815)]:
        b, w, h = textbox(x, 332, [name], size=12, fill="#eef2ff", stroke=NEG)
        frags.append(arrow(705, 228 + regh / 2, x, 332 - h / 2, color=FIELD, sw=1.4))
        frags.append(b)
    frags.append(text(705, 388, "одна точка збірки · у тесті — один fakeRegistry",
                      size=12, italic=True, color=FIELD))

    render(os.path.join(OUT, 'registry-di.svg'), W, H, *frags,
           title="N прихованих сінглтонів → один реєстр як залежність")


if __name__ == '__main__':
    fig_two_jobs()
    fig_race()
    fig_reorder_writes()
    fig_barrier()
    fig_attack_surface()
    fig_design_matrix()
    fig_scope_ladder()
    fig_identity_state()
    fig_init_order_fiasco()
    fig_one_to_many()
    fig_get_or_create()
    fig_unbounded_growth()
    fig_registry_di()
    print('figures written to', OUT)
