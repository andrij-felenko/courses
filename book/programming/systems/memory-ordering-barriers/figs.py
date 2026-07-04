# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_reorder():
    """Класична передача повідомлення: потік B побачив ready=1, а data ще стара."""
    W, H = 760, 430
    frags = []
    frags.append(text(W / 2, 30, "Потік A пише data, тоді ready — а потік B бачить це у зворотному порядку", size=15, bold=True))

    # Ліва колонка — потік A (writer)
    ax = 60
    aw = 300
    frags.append(fitbox(ax, 60, aw, 34, "Потік A (пише)", size=14, bold=True, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(ax, 108, aw, 40, "data = 42;   // велике корисне значення", size=12, fill=FILL))
    frags.append(fitbox(ax, 156, aw, 40, "ready = 1;   // прапорець «готово»", size=12, fill=FILL))
    frags.append(text(ax + aw / 2, 220, "порядок у коді: спершу data, потім ready", size=12, color=MUTED, italic=True))

    # Права колонка — потік B (reader)
    bx = 420
    bw = 280
    frags.append(fitbox(bx, 60, bw, 34, "Потік B (читає)", size=14, bold=True, fill="#fdecea", stroke=POS))
    frags.append(fitbox(bx, 108, bw, 40, "while (ready == 0) {}   // чекає", size=12, fill=FILL))
    frags.append(fitbox(bx, 156, bw, 40, "use(data);   // очікує 42…", size=12, fill=FILL))

    # Що реально побачив B — стрілки видимості
    frags.append(line(60, 268, W - 60, 268, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(W / 2, 292, "Що дійшло до потоку B (видимість записів):", size=13, bold=True))

    # timeline
    ty = 350
    frags.append(line(70, ty, W - 70, ty, color=INK, sw=2))
    frags.append(text(70, ty + 26, "раніше", size=11, color=MUTED, anchor="start"))
    frags.append(text(W - 70, ty + 26, "пізніше", size=11, color=MUTED, anchor="end"))

    # ready видимий першим, data пізніше
    frags.append(circle(250, ty, 7, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(250, ty - 16, "ready = 1", size=12, color=POS, bold=True))
    frags.append(circle(560, ty, 7, fill="#eef2ff", stroke=NEG, sw=2))
    frags.append(text(560, ty - 16, "data = 42", size=12, color=NEG, bold=True))

    frags.append(text(W / 2, ty + 56, "B побачив ready=1, коли data ще стара → use(data) читає сміття", size=13, color=POS, bold=True))

    render(os.path.join(IMG, 'reorder.svg'), W, H, *frags)


def fig_layers():
    """Три шари між порядком у коді і тим, що бачить інше ядро."""
    W, H = 780, 360
    frags = []
    frags.append(text(W / 2, 30, "Порядок у коді проходить крізь два шари, що вільно його переставляють", size=15, bold=True))

    cols = [
        (70,  "#eef2ff", NEG, "Порядок у коді", ["store data", "store ready"]),
        (280, "#fff7e6", "#b8860b", "Компілятор", ["store ready", "store data"]),
        (490, "#fdecea", POS, "Процесор", ["ready видимий", "data ще в буфері"]),
    ]
    boxw = 190
    for (x, fill, stroke, title, rows) in cols:
        frags.append(fitbox(x, 70, boxw, 34, title, size=14, bold=True, fill=fill, stroke=stroke))
        yy = 120
        for r in rows:
            frags.append(fitbox(x, yy, boxw, 38, r, size=12, fill=FILL))
            yy += 48

    # стрілки між колонками
    frags.append(arrow(70 + boxw + 4, 150, 280 - 4, 150, color=INK))
    frags.append(text((70 + boxw + 280) / 2, 138, "as-if", size=11, color=MUTED, italic=True))
    frags.append(arrow(280 + boxw + 4, 150, 490 - 4, 150, color=INK))
    frags.append(text((280 + boxw + 490) / 2, 138, "буфер, OoO", size=11, color=MUTED, italic=True))

    # висновок
    frags.append(line(70, 262, W - 90, 262, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(W / 2, 292, "Модель пам'яті — це договір: які з цих перестановок дозволені,", size=13))
    frags.append(text(W / 2, 314, "а де ти командою-бар'єром кажеш «саме тут переставляти не можна».", size=13))

    render(os.path.join(IMG, 'layers.svg'), W, H, *frags)


def fig_acqrel():
    """Release і acquire як однобічні бар'єри, що зшивають happens-before між потоками."""
    W, H = 780, 440
    frags = []
    frags.append(text(W / 2, 30, "release і acquire — однобічні бар'єри, що зшивають два потоки", size=15, bold=True))

    # дві вертикальні доріжки часу
    ax = 200
    bx = 560
    top = 70
    bot = 380
    frags.append(line(ax, top, ax, bot, color=INK, sw=2))
    frags.append(line(bx, top, bx, bot, color=INK, sw=2))
    frags.append(text(ax, top - 14, "Потік A", size=14, bold=True, color=NEG))
    frags.append(text(bx, top - 14, "Потік B", size=14, bold=True, color=POS))
    frags.append(text(ax - 150, top + 6, "час ↓", size=11, color=MUTED, anchor="start"))

    # A: записи, потім release
    frags.append(fitbox(ax - 155, 90, 150, 32, "data = 42", size=12, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(ax - 155, 132, 150, 32, "cfg = ok", size=12, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(ax - 175, 186, 170, 36, "ready.store(1,\n release)", size=12, fill=FILL, stroke=INK, bold=True))
    # бар'єр-риска release: нічого зверху не проштовхнути вниз
    frags.append(line(ax - 15, 176, ax + 55, 176, color=INK, sw=2.5))
    frags.append(text(ax + 60, 172, "↑ записи не спускаються нижче release", size=11, color=MUTED, anchor="start"))

    # B: acquire, потім читання
    frags.append(fitbox(bx + 5, 240, 175, 36, "ready.load(\n acquire) == 1", size=12, fill=FILL, stroke=INK, bold=True))
    frags.append(line(bx - 55, 284, bx + 15, 284, color=INK, sw=2.5))
    frags.append(text(bx - 60, 300, "читання не піднімаються вище acquire ↓", size=11, color=MUTED, anchor="end"))
    frags.append(fitbox(bx + 5, 300, 150, 32, "use(data) → 42", size=12, fill="#fdecea", stroke=POS))
    frags.append(fitbox(bx + 5, 340, 150, 32, "use(cfg) → ok", size=12, fill="#fdecea", stroke=POS))

    # синхронізаційне ребро
    frags.append(arrow(ax + 5, 204, bx - 5, 258, color=FIELD, sw=2.4))
    frags.append(text((ax + bx) / 2 + 10, 218, "synchronizes-with", size=12, color=FIELD, bold=True, italic=True))

    frags.append(line(60, 398, W - 60, 398, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(W / 2, 424, "Побачив ready через acquire → усе, що A написав перед release, вже видиме B", size=13, color=FIELD, bold=True))

    render(os.path.join(IMG, 'acquire-release.svg'), W, H, *frags)


def fig_timeline():
    """Шлях моделі пам'яті: від умови коректності заліза (1979) до пункту стандарту мови (2011)."""
    W, H = 900, 430
    frags = []
    frags.append(text(W / 2, 30, "Як упорядкування пам'яті переїхало із заліза в текст мови", size=16, bold=True))

    # горизонтальна вісь часу
    ty = 150
    frags.append(line(70, ty, W - 70, ty, color=INK, sw=2.5))
    frags.append(text(70, ty - 14, "1979", size=12, color=MUTED, anchor="start"))
    frags.append(text(W - 70, ty - 14, "2011", size=12, color=MUTED, anchor="end"))

    # чотири віхи; x рівномірно
    marks = [
        (150, "1979", "Лемпорт", "послідовна\nузгодженість —\nумова коректності", NEG),
        (390, "1995–96", "Java 1.0", "перша модель\nу мові —\nі вона зламана", MUTED),
        (620, "2004", "JSR-133", "happens-before;\nмодель Java\nполагоджено", FIELD),
        (830, "2011", "C++11", "std::atomic —\nупорядкування\nв стандарті C++", POS),
    ]
    for (x, yr, who, what, col) in marks:
        frags.append(circle(x, ty, 8, fill="#ffffff", stroke=col, sw=3))
        # рік і хто — над віссю
        frags.append(text(x, ty - 40, yr, size=13, bold=True, color=col))
        frags.append(text(x, ty - 24, who, size=12, color=INK))
        # опис — під віссю, широкою колонкою (щоб рядки не налазили)
        frags.append(mtext(x, ty + 34, what, size=12, color=INK, lh=1.3))

    # нижня смуга-висновок: два світи
    frags.append(line(70, 356, W - 70, 356, color=MUTED, sw=1, dash="5,5"))
    frags.append(mtext(W / 2, 384,
                       ["Ліворуч від JSR-133 порядок був турботою лише архітектури заліза.",
                        "Праворуч він став частиною договору самої мови — переносним між машинами."],
                       size=13, lh=1.35))

    render(os.path.join(IMG, 'timeline.svg'), W, H, *frags)


def fig_alpha():
    """Що унікально дозволяла DEC Alpha: переставити навіть ЗАЛЕЖНІ читання."""
    W, H = 880, 470
    frags = []
    frags.append(text(W / 2, 30, "Єдине, що дозволяла тільки Alpha: прочитати покажчик — і взяти стару ціль", size=15, bold=True))

    # Ліворуч — код litmus-тесту
    lx = 55
    lw = 360
    frags.append(fitbox(lx, 60, lw, 30, "Виробник (ядро 1)", size=13, bold=True, fill="#eef2ff", stroke=NEG))
    frags.append(fitbox(lx, 98, lw, 34, "node.val = 42;              // 1) заповнили вузол", size=12, fill=FILL))
    frags.append(fitbox(lx, 138, lw, 34, "smp_wmb();                  //    бар'єр запису", size=12, fill=FILL))
    frags.append(fitbox(lx, 178, lw, 34, "head = &node;               // 2) опублікували", size=12, fill=FILL))

    frags.append(fitbox(lx, 236, lw, 30, "Споживач (ядро 2)", size=13, bold=True, fill="#fdecea", stroke=POS))
    frags.append(fitbox(lx, 274, lw, 34, "p = head;                   // A) взяли покажчик", size=12, fill=FILL))
    frags.append(fitbox(lx, 314, lw, 34, "v = p->val;                 // B) взяли ціль", size=12, fill=FILL))
    frags.append(mtext(lx + lw / 2, 372,
                       ["B залежить від A: адресу для B дало саме A.",
                        "Скрізь, крім Alpha, ця залежність тримає порядок."],
                       size=12, color=MUTED, lh=1.3))

    # Праворуч — чому Alpha їх усе одно розриває: банки кешу
    rx = 470
    rw = 355
    frags.append(fitbox(rx, 60, rw, 30, "Чому Alpha розриває навіть це", size=13, bold=True, fill="#fff7e6", stroke="#b8860b"))
    frags.append(fitbox(rx, 100, rw, 40, "Кеш ядра 2 поділений на незалежні БАНКИ.\nА і B можуть впасти в різні банки.", size=12, fill=FILL))
    frags.append(fitbox(rx, 150, rw, 40, "Банк із p->val оновлюється повільніше\nза банк із head — і віддає СТАРУ копію.", size=12, fill=FILL))
    frags.append(fitbox(rx, 200, rw, 40, "Наслідок: p = &node (свіже),\nа p->val = 0 (застаріле). Абсурд, але легальний.", size=12, fill=FILL, stroke=POS))

    # стрілка-результат
    frags.append(text(rx + rw / 2, 268, "v == 0, хоча node.val давно = 42", size=13, bold=True, color=POS))

    frags.append(line(rx, 292, rx + rw, 292, color=MUTED, sw=1, dash="4,4"))
    frags.append(fitbox(rx, 308, rw, 78,
                        "Тому в Linux між A і B стоїть окремий бар'єр залежних читань. На всіх інших архітектурах він — пусте місце (no-op); ціну платить лише Alpha.",
                        size=12, fill="#eef7ee", stroke=FIELD))

    render(os.path.join(IMG, 'alpha.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_reorder()
    fig_layers()
    fig_acqrel()
    fig_timeline()
    fig_alpha()
    print('figures written to', IMG)
