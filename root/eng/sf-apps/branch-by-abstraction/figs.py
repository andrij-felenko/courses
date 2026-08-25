# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, size=13, pad=9, **kw):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return frag


# ── Фігура 1: п'ять станів міграції ────────────────────────────────────────
# Клієнт → (абстракція) → реалізація. Колонки-стани зліва направо.
def fig_states():
    W, H = 940, 470
    frags = []
    cols = [90, 260, 450, 645, 838]        # центри п'яти колонок
    top = 70
    cap_y = H - 24
    labels = [
        "1. Було",
        "2. Вставили шов",
        "3. Нове поряд",
        "4. Перемкнули",
        "5. Прибрали старе",
    ]
    for cx, lab in zip(cols, labels):
        frags.append(box(cx, top - 26, lab, size=12, bold=True,
                         fill="#eef2f7", stroke=MUTED, pad=6))

    yC = top + 40      # клієнт
    yA = top + 130     # абстракція
    yOld = top + 235   # стара реалізація
    yNew = top + 315   # нова реалізація
    bw = 150

    def client(cx):
        return box(cx, yC, "Клієнти", size=13, bold=True, min_w=bw,
                   fill="#e8f0ff", stroke=NEG)

    def absl(cx):
        return box(cx, yA, "Абстракція\n(інтерфейс)", size=12, min_w=bw,
                   fill="#eafaf0", stroke=FIELD, bold=True)

    def old(cx, live=True):
        col = "#fff3e0" if live else "#f0f0f0"
        stk = POS if live else MUTED
        return box(cx, yOld, "Старе", size=12, min_w=bw, fill=col, stroke=stk)

    def new(cx):
        return box(cx, yNew, "Нове", size=12, min_w=bw, fill="#fff3e0", stroke=POS)

    # Стан 1: клієнт прямо на старе
    cx = cols[0]
    frags += [client(cx), old(cx)]
    frags.append(arrow(cx, yC + 22, cx, yOld - 22, color=NEG, sw=2))

    # Стан 2: вставлена абстракція, старе під нею
    cx = cols[1]
    frags += [client(cx), absl(cx), old(cx)]
    frags.append(arrow(cx, yC + 22, cx, yA - 26, color=NEG, sw=2))
    frags.append(arrow(cx, yA + 26, cx, yOld - 22, color=INK, sw=1.8))

    # Стан 3: нове поряд зі старим, обидва під абстракцією; прапорець → старе
    cx = cols[2]
    frags += [client(cx), absl(cx), old(cx), new(cx)]
    frags.append(arrow(cx, yC + 22, cx, yA - 26, color=NEG, sw=2))
    # прапорець-ромб між абстракцією і реалізаціями
    fy = (yA + yOld) / 2 + 6
    frags.append(box(cx, fy, "прапорець", size=10, pad=5,
                     fill="#fdf6e3", stroke=POS))
    frags.append(line(cx - 30, yA + 24, cx - 30, yOld - 20, color=INK, sw=2))  # активна гілка → старе
    frags.append(line(cx + 30, yA + 24, cx + 30, yNew - 20, color=MUTED, sw=1.4, dash="5 4"))  # спляча → нове

    # Стан 4: прапорець перемкнено на нове; старе ще є, але спить
    cx = cols[3]
    frags += [client(cx), absl(cx), old(cx, live=False), new(cx)]
    frags.append(arrow(cx, yC + 22, cx, yA - 26, color=NEG, sw=2))
    fy = (yA + yOld) / 2 + 6
    frags.append(box(cx, fy, "прапорець", size=10, pad=5,
                     fill="#fdf6e3", stroke=POS))
    frags.append(line(cx - 30, yA + 24, cx - 30, yOld - 20, color=MUTED, sw=1.4, dash="5 4"))
    frags.append(line(cx + 30, yA + 24, cx + 30, yNew - 20, color=INK, sw=2))

    # Стан 5: старого нема, абстракцію теж прибрали (клієнт → нове або лишили шов)
    cx = cols[4]
    frags += [client(cx), new(cx)]
    frags.append(arrow(cx, yC + 22, cx, yNew - 22, color=NEG, sw=2))

    # Нижній підпис-нитка
    frags.append(text(W / 2, cap_y,
                      "На кожному кроці система збирається й випускається — гілка живе в коді, не у гіллі системи контролю версій",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'states.svg'), W, H, *frags,
           title="Заміна реалізації без розгалуження: п'ять станів на одному стовбурі")


# ── Фігура 2: довга гілка VCS проти гілки-в-коді ───────────────────────────
def fig_vcs():
    W, H = 960, 400
    frags = []
    xs = [230, 330, 430, 530, 630, 730]     # вузли стовбура (лишили місце під підпис зліва)

    # Верх: довга гілка у VCS — розходиться і болісно зливається
    y1 = 120
    frags.append(box(112, y1, "Гілка\nу VCS", size=13, bold=True,
                     fill="#fdecea", stroke=POS, pad=8))
    for i in range(len(xs) - 1):
        frags.append(line(xs[i], y1, xs[i + 1], y1, color=INK, sw=2))
    for x in xs:
        frags.append(circle(x, y1, 5, fill=BG, stroke=INK, sw=2))
    frags.append(text(xs[-1] + 16, y1 + 4, "стовбур", size=11, color=MUTED, anchor="start"))
    # відгалуження вниз і болісне злиття назад
    by = y1 + 78
    frags.append(line(xs[1], y1, xs[1] + 26, by, color=POS, sw=2))
    seg = 100
    x0 = xs[1] + 26
    for i in range(3):
        frags.append(line(x0 + i * seg, by, x0 + (i + 1) * seg, by, color=POS, sw=2))
        frags.append(circle(x0 + (i + 1) * seg, by, 5, fill="#fdecea", stroke=POS, sw=2))
    frags.append(line(x0 + 3 * seg, by, xs[5], y1, color=POS, sw=2, dash="6 4"))
    frags.append(box(x0 + 1.5 * seg, by + 40,
                     "місяці нарізно → конфлікти злиття",
                     size=11, color=POS, fill="#fff", stroke=POS, pad=6))

    # Низ: усі коміти на стовбурі, «гілка» живе абстракцією в коді
    y2 = H - 95
    frags.append(box(112, y2, "Branch by\nabstraction", size=13, bold=True,
                     fill="#eafaf0", stroke=FIELD, pad=8))
    for i in range(len(xs) - 1):
        frags.append(line(xs[i], y2, xs[i + 1], y2, color=INK, sw=2))
    for x in xs:
        frags.append(circle(x, y2, 5, fill="#eafaf0", stroke=FIELD, sw=2))
    frags.append(box(xs[1], y2 - 34, "шов", size=10, pad=4, fill="#eafaf0", stroke=FIELD))
    frags.append(box(xs[4], y2 - 34, "перемкнули", size=10, pad=4, fill="#fdf6e3", stroke=POS))
    frags.append(text(W / 2, H - 22,
                      "кожен крихітний крок одразу на стовбурі — розходитися нема з чим, зливати нічого",
                      size=12, color=FIELD))
    render(os.path.join(IMG, 'vcs-vs-bba.svg'), W, H, *frags,
           title="Де живе «гілка»: у гіллі VCS чи в коді на стовбурі")


# ── Фігура 3: часова смуга назви (для hist-вставки) ────────────────────────
# Практика стара → Curl дав назву (2007) → Hammant задокументував (2007/2009)
# → Fowler закріпив у каноні (2014). Анкери: ThoughtWorks / BofA / Go.
def fig_naming_timeline():
    W, H = 960, 470
    frags = []
    axis_y = 190
    x0, x1 = 70, 890
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2))
    frags.append(arrow(x1 - 2, axis_y, x1 + 2, axis_y, color=INK, sw=2))

    # Позначки років уздовж осі (нерівномірно, але читабельно).
    ticks = [
        (150, "≈2005"),
        (360, "2007"),
        (560, "2009"),
        (770, "2014"),
    ]
    for tx, lab in ticks:
        frags.append(line(tx, axis_y - 7, tx, axis_y + 7, color=INK, sw=2))
        # рік — ЛІВОРУЧ від позначки, щоб вертикальний конектор виноски не різав напис
        frags.append(text(tx - 11, axis_y + 22, lab, size=13, color=INK,
                          bold=True, anchor="end"))

    # «Практика стара» — розмита смужка ліворуч від першої мітки.
    frags.append(line(x0, axis_y, 140, axis_y, color=MUTED, sw=6, dash="2 6"))
    frags.append(text(x0 + 4, axis_y - 18, "техніка вже стара",
                      size=11, color=MUTED, anchor="start"))

    # Події над віссю (виноски вгору) і під віссю (вниз) — щоб не налізали.
    # Конектор зупиняємо ПОЗА рамкою: рахуємо пів-висоту боксу як у textbox.
    def _halfh(s, size=11, pad=7):
        n = len(s.split("\n"))
        return (n * size * 1.3 + 2 * pad - size * 0.3) / 2

    def flag_up(tx, y, s, stroke):        # бокс НАД віссю (y < axis_y)
        stop = y + _halfh(s) + 4
        frags.append(line(tx, axis_y - 4, tx, stop, color=stroke, sw=1.6))
        frags.append(box(tx, y, s, size=11, pad=7, fill="#fff", stroke=stroke))

    def flag_dn(tx, y, s, stroke):        # бокс ПІД віссю (y > axis_y)
        stop = y - _halfh(s) - 4
        frags.append(line(tx, axis_y + 4, tx, stop, color=stroke, sw=1.6))
        frags.append(box(tx, y, s, size=11, pad=7, fill="#fff", stroke=stroke))

    flag_dn(150, axis_y + 92,
            "ThoughtWorks у клієнта\n(Bank of America)", MUTED)
    flag_up(360, axis_y - 78,
            "Stacy Curl\nдав НАЗВУ", NEG)
    flag_dn(360, axis_y + 92,
            "Paul Hammant\nзадокументував (блог)", FIELD)
    flag_up(560, axis_y - 78,
            "Hammant: велике\nоновлення допису", FIELD)
    flag_up(770, axis_y - 78,
            "Martin Fowler:\nзакріплено в каноні", POS)
    flag_dn(770, axis_y + 92,
            "приклад команди «Go»\n(iBatis→Hibernate)", POS)

    frags.append(box(W / 2, 40,
                     "Техніка стара — назва молода: шлях слова «Branch by Abstraction»",
                     size=13, bold=True, fill="#eef2f7", stroke=MUTED, pad=8))
    frags.append(text(W / 2, H - 16,
                      "практику робили роками мовчки; назва зробила її переказовою — тим і закріпилася",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'naming-timeline.svg'), W, H, *frags,
           title="Часова смуга назви Branch by Abstraction: практика, коінінг, документація, канон")


# ── Фігура 4: обгортка-звіряч (shadow/compare) ─────────────────────────────
# Клієнт → ComparingNotifier {control, candidate}. Control → користувач;
# candidate → в тінь → звірка → розбіжність у лог.
def fig_shadow():
    W, H = 960, 480
    frags = []

    # Клієнт зліва
    xC = 118
    yMid = 220
    frags.append(box(xC, yMid, "Клієнт", size=13, bold=True,
                     fill="#e8f0ff", stroke=NEG, min_w=110))

    # Рамка-обгортка (велика) посередині
    boxL, boxT, boxW, boxH = 250, 100, 300, 280
    frags.append(rect(boxL, boxT, boxW, boxH, fill="#f6f8fb", stroke=FIELD, sw=2, rx=10))
    frags.append(box(boxL + boxW / 2, boxT - 20, "ComparingNotifier  (сам — Notifier)",
                     size=12, bold=True, fill="#eafaf0", stroke=FIELD, pad=6))

    xImpl = boxL + boxW / 2
    yOld = boxT + 66
    yNew = boxT + 156
    yCmp = boxT + 234
    frags.append(box(xImpl, yOld, "Стара (control)", size=12, min_w=210,
                     fill="#fff3e0", stroke=POS))
    frags.append(box(xImpl, yNew, "Нова (candidate)", size=12, min_w=210,
                     fill="#fff3e0", stroke=POS))
    frags.append(box(xImpl, yCmp, "звірити суть", size=11, min_w=150,
                     fill="#fdf6e3", stroke=MUTED, pad=6))

    # Клієнт → обгортка (виклик notify) — у верхній край рамки, повз написи
    frags.append(arrow(xC + 55, yMid - 40, boxL - 4, boxT + 20, color=NEG, sw=2))
    frags.append(text((xC + boxL) / 2 - 4, yMid - 58, "notify()", size=11,
                      color=MUTED, italic=True))

    # всередині: обидві реалізації живлять звірку (короткі конектори, збоку від центру)
    frags.append(arrow(xImpl - 70, yOld + 18, xImpl - 70, yCmp - 16, color=INK, sw=1.5))
    frags.append(arrow(xImpl - 70, yNew + 18, xImpl - 70, yCmp - 16, color=INK, sw=1.5))

    # Праворуч: користувач (від control) і лог (від звірки)
    xUser = 830
    yUser = boxT + 24
    yLog = boxT + 226
    frags.append(box(xUser, yUser, "Користувач", size=12, bold=True, min_w=170,
                     fill="#e8f0ff", stroke=NEG))
    frags.append(box(xUser, yLog, "Лог розбіжностей", size=12, bold=True, min_w=170,
                     fill="#fdecea", stroke=POS))

    # control → користувачеві (суцільна, «це віддаємо»)
    frags.append(arrow(boxL + boxW + 2, yOld, xUser - 92, yUser, color=NEG, sw=2))
    frags.append(text((boxL + boxW + xUser) / 2 + 10, yOld - 14,
                      "вихід старої", size=11, color=NEG, italic=True))

    # candidate → в тінь (пунктир, гаситься) — вбік, не до правого стовпця
    frags.append(line(xImpl + 110, yNew, 640, yNew, color=MUTED, sw=1.4, dash="5 4"))
    frags.append(box(700, yNew, "тінь: гаситься", size=10, pad=5,
                     fill="#f0f0f0", stroke=MUTED))

    # звірка → лог (лише розбіжність)
    frags.append(arrow(boxL + boxW + 2, yCmp, xUser - 92, yLog, color=POS, sw=2))
    frags.append(text((boxL + boxW + xUser) / 2 + 10, yCmp + 22,
                      "лише розбіжність", size=11, color=POS, italic=True))

    frags.append(text(W / 2, H - 20,
                      "Користувач бачить лише вихід старої; нова працює в тіні, а її незбіг зі старою осідає в логу",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'shadow-compare.svg'), W, H, *frags,
           title="Затінення: обгортка жене обидві реалізації, віддає стару, звіряє нову")


if __name__ == '__main__':
    fig_states()
    fig_vcs()
    fig_naming_timeline()
    fig_shadow()
    print("ok")
