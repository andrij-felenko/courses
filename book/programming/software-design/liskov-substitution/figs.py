# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: обіцянка підстановки ──────────────────────────────────────────
# Клієнт тримає посилання типу T; всередину підставляють об'єкт підтипу S;
# поведінка програми не змінюється — клієнт нічого не помічає.
def fig_substitution():
    W, H = 720, 330
    p = []

    # Клієнт — код, що працює через тип T
    cb, cw, ch = textbox(150, 120, ["Клієнт", "працює через тип T", "shape.area()"],
                         size=14, pad=14, min_w=210)
    p.append(cb)

    # «дірка» під T — контракт
    hb, hw, hh = textbox(150, 235, "очікує: контракт T", size=13, pad=11,
                         fill="#eef7ff", stroke=NEG, min_w=210)
    p.append(hb)
    p.append(line(150, 148, 150, 213, color=MUTED, dash="4 4"))

    # Два кандидати праворуч
    tb, tw, th = textbox(560, 90, ["об'єкт типу T", "(база)"], size=13, pad=12,
                         fill=FILL, min_w=200)
    p.append(tb)
    sb, sw2, sh = textbox(560, 235, ["об'єкт підтипу S", "(нащадок)"], size=13, pad=12,
                          fill="#eaf7ee", stroke=FIELD, min_w=200)
    p.append(sb)

    # Стрілки підстановки в ту саму дірку
    p.append(arrow(462, 100, 262, 200, color=MUTED))
    p.append(arrow(462, 232, 262, 240, color=FIELD))

    # Підпис на зеленій стрілці
    p.append(text(390, 205, "підставили S замість T", size=12, color=FIELD, bold=True))
    p.append(text(360, 300, "поведінка програми — та сама", size=13, color=INK, bold=True))

    render(os.path.join(IMG, 'substitution.svg'), W, H, *p,
           title="Підстановка: S годиться всюди, де очікували T")


# ── Фігура 2: правило контракту — вимоги вужче, обіцянки ширше ──────────────
# Precondition subtype: приймає БІЛЬШЕ (ширша пащека входу).
# Postcondition subtype: гарантує ВУЖЧЕ (тонший струмінь виходу).
def fig_contract():
    W, H = 760, 360
    p = []

    midy = 205

    # ── Вхід (передумова) ──
    # База: вужчий вхід. Нащадок: ширший (приймає більше) — це дозволено.
    bx = 90
    p.append(text(180, 60, "ВХІД — передумова", size=14, bold=True, color=NEG))
    # база: вузька рамка входу
    p.append(rect(bx, 150, 60, 40, fill="#eef2ff", stroke=NEG))
    p.append(text(bx + 30, 175, "база", size=12, color=NEG))
    # нащадок: ширша рамка — накриває базу й ще ширше
    p.append(rect(bx - 25, 235, 150, 46, fill="#eaf7ee", stroke=FIELD, sw=2))
    p.append(text(bx + 50, 263, "нащадок — ширший", size=12, color=FIELD, bold=True))
    p.append(text(180, 315, "приймає не менше, ніж база", size=12, color=INK))
    p.append(text(180, 333, "(передумову не посилюють)", size=11, color=MUTED))

    # роздільник
    p.append(line(W / 2, 80, W / 2, 300, color=MUTED, dash="3 5"))

    # ── Вихід (постумова) ──
    ox = 560
    p.append(text(ox, 60, "ВИХІД — обіцянка", size=14, bold=True, color=POS))
    # база: широка обіцянка
    p.append(rect(ox - 75, 150, 150, 40, fill="#fff0ee", stroke=POS))
    p.append(text(ox, 175, "база", size=12, color=POS))
    # нащадок: вужча (гарантує точніше) — накрита базою
    p.append(rect(ox - 30, 235, 60, 46, fill="#eaf7ee", stroke=FIELD, sw=2))
    p.append(text(ox, 263, "нащадок", size=12, color=FIELD, bold=True))
    p.append(text(ox, 315, "обіцяє не менше, ніж база", size=12, color=INK))
    p.append(text(ox, 333, "(постумову не послаблюють)", size=11, color=MUTED))

    render(os.path.join(IMG, 'contract.svg'), W, H, *p,
           title="Нащадок: вимагай не більше, обіцяй не менше")


# ── Фігура 3 (proj): брехлива ієрархія проти розділеної ──────────────────────
# Ліворуч: одна лінія List → ImmutableList, чий add кидає виняток (баг у runtime).
# Праворуч: ReadableList (чесний мінімум) ← MutableList (додає add); незмінний
# реалізує лише Readable, тож у місце під add його не підставиш — блокує КОМПІЛЯТОР.
def fig_split():
    W, H = 860, 470
    p = []

    # ── Ліва половина: ДО (брехлива ієрархія) ──
    p.append(text(215, 62, "ДО: одна ієрархія — брехня", size=15, bold=True, color=POS))

    lb, lw, lh = textbox(215, 120, ["List<T>", "get() · add()"], size=13, pad=12,
                         fill=FILL, min_w=190)
    p.append(lb)

    ib, iw, ih = textbox(215, 235, ["ImmutableList<T>", "add() → кидає виняток"], size=13,
                         pad=12, fill="#fdecea", stroke=POS, sw=2, min_w=220)
    p.append(ib)
    # стрілка спадкування (нащадок → база)
    p.append(arrow(215, 213, 215, 150, color=MUTED))
    p.append(text(300, 185, "extends", size=11, color=MUTED, italic=True, anchor="start"))

    # клієнт fill(List) кличе add — і летить у виняток
    cb, cw, ch = textbox(215, 355, ["клієнт: fill(list: List)", "викликає list.add(i)"], size=12,
                         pad=11, fill="#eef2ff", stroke=NEG, min_w=230)
    p.append(cb)
    p.append(arrow(215, 258, 215, 331, color=POS, sw=2))
    p.append(text(215, 425, "вибух під час роботи", size=13, color=POS, bold=True))

    # роздільник
    p.append(line(W / 2, 80, W / 2, 445, color=MUTED, dash="3 6"))

    # ── Права половина: ПІСЛЯ (розділені типи) ──
    # Два стовпці: ліворуч Readable→Mutable (ієрархія типів), праворуч — незмінний
    # список, що тягнеться зеленою стрілкою до Readable (реалізує) і червоною,
    # перекресленою — до Mutable (спроба підставити під add, яку блокує компілятор).
    p.append(text(650, 62, "ПІСЛЯ: типи розділено", size=15, bold=True, color=FIELD))

    tx = 560   # стовпець типів
    rlb, rlw, rlh = textbox(tx, 120, ["ReadableList<T>", "get() · size()"], size=13, pad=12,
                           fill="#eaf7ee", stroke=FIELD, min_w=180)
    p.append(rlb)

    mlb, mlw, mlh = textbox(tx, 235, ["MutableList<T>", "+ add()"], size=13, pad=12,
                           fill="#eaf7ee", stroke=FIELD, sw=2, min_w=180)
    p.append(mlb)
    p.append(arrow(tx, 213, tx, 150, color=FIELD))
    p.append(text(tx + 96, 185, "розширює", size=11, color=FIELD, italic=True, anchor="start"))

    # незмінний список — окремий стовпець праворуч, унизу
    imx = 770
    imb, imbw, imbh = textbox(imx, 355, ["незмінний", "список"], size=13, pad=11,
                             fill=FILL, min_w=130)
    p.append(imb)
    p.append(text(imx, 405, "реалізує лише", size=11, color=MUTED))
    p.append(text(imx, 421, "ReadableList", size=11, color=MUTED))

    # зелена: незмінний РЕАЛІЗУЄ Readable (стрілка в правий бік Readable)
    p.append(arrow(imx + 6, 333, tx + rlw / 2 + 6, 132, color=FIELD))
    p.append(text(imx + 30, 240, "реалізує", size=11, color=FIELD, italic=True, bold=True, anchor="start"))

    # червона, перекреслена: спроба підставити під Mutable — блок
    p.append(line(imx - 20, 335, tx + mlw / 2 + 8, 258, color=POS, sw=2, dash="6 4"))
    # хрестик-заборона на середині червоної лінії
    xc, yc = (imx - 20 + tx + mlw / 2 + 8) / 2, (335 + 258) / 2
    p.append(line(xc - 9, yc - 9, xc + 9, yc + 9, color=POS, sw=2.5))
    p.append(line(xc - 9, yc + 9, xc + 9, yc - 9, color=POS, sw=2.5))

    p.append(text(650, 452, "під add його не підставиш — компілятор не пустить",
                  size=13, color=FIELD, bold=True))

    render(os.path.join(IMG, 'split.svg'), W, H, *p,
           title="Розділити тип, щоб порушення стало неможливим")


# ── Фігура 4 (hist): шлях імені від keynote до SOLID ────────────────────────
# Вертикальна вісь часу: чотири віхи народження й іменування принципу.
def fig_lsp_lineage():
    W, H = 820, 560
    p = []
    p.append(text(W / 2, 30, "Шлях принципу: від keynote 1987 до SOLID", size=17, bold=True))

    axis_x = 175
    y0, y1 = 78, 520
    p.append(line(axis_x, y0, axis_x, y1, color=MUTED, sw=2))

    milestones = [
        ("1987 · 1988",
         ["Барбара Лісков, keynote", "«Data Abstraction and Hierarchy»",
          "(OOPSLA 1987 → SIGPLAN Notices,", "травень 1988). Перша, неформальна",
          "властивість підстановки."],
         NEG),
        ("1994",
         ["Лісков і Жанет Вінг,", "«A Behavioral Notion of Subtyping»",
          "(ACM TOPLAS, листопад 1994).", "Строга теорія: контракти,",
          "інваріанти, обмеження історії."],
         FIELD),
        ("1996",
         ["Роберт Мартин, «The Liskov", "Substitution Principle»",
          "(C++ Report, березень 1996).", "Тут уперше в обіг — назва «LSP»",
          "як інженерне правило."],
         POS),
        ("≈ 2004",
         ["Майкл Фезерс складає п'ять", "принципів Мартина в акронім",
          "SOLID. «L» у ньому — саме LSP.", "Так назва розходиться світом."],
         INK),
    ]

    n = len(milestones)
    span = (y1 - y0)
    for i, (year, lines, col) in enumerate(milestones):
        cy = y0 + span * (i + 0.5) / n
        # вузол на осі
        p.append(circle(axis_x, cy, 8, fill=BG, stroke=col, sw=2.5))
        # рік — ліворуч від осі
        p.append(text(axis_x - 22, cy + 5, year, size=13, bold=True, color=col, anchor="end"))
        # картка-опис — праворуч від осі
        bx = axis_x + 40
        bw = W - bx - 30
        bh = len(lines) * 16 + 22
        p.append(rect(bx, cy - bh / 2, bw, bh, fill=FILL, stroke=col, sw=1.6))
        ty = cy - (len(lines) - 1) * 16 / 2 + 5
        p.append(mtext(bx + 16, ty, lines, size=12.5, color=INK, anchor="start", lh=1.28))

    return render(os.path.join(IMG, 'lsp-lineage.svg'), W, H, *p)


# ── Фігура 5 (hist): хто що зробив — і чому назва трохи несправедлива ────────
def fig_attribution():
    W, H = 780, 340
    p = []
    p.append(text(W / 2, 30, "Хто що зробив у цій історії", size=17, bold=True))

    rows = [
        ("Барбара Лісков", "MIT",
         "сформулювала неформальну властивість підстановки (1987/88)", NEG),
        ("Жанет Вінг", "CMU",
         "співавторка строгої теорії поведінкової підтипізації (1994)", FIELD),
        ("Роберт Мартин", "практик",
         "пустив у обіг назву «LSP» і вписав її в SOLID", POS),
    ]
    y = 70
    rh = 66
    namew = 200
    for name, aff, what, col in rows:
        p.append(rect(40, y, namew, rh - 12, fill="#f4f6f8", stroke=col, sw=1.8))
        p.append(text(40 + namew / 2, y + (rh - 12) / 2 - 4, name, size=14, bold=True, color=col))
        p.append(text(40 + namew / 2, y + (rh - 12) / 2 + 16, aff, size=11.5, color=MUTED))
        p.append(fitbox(40 + namew + 24, y, W - (40 + namew + 24) - 30, rh - 12, what,
                        size=12.5, fill=BG, stroke=col, sw=1.2))
        y += rh

    p.append(text(W / 2, y + 18,
                  "Ім'я на принципі — одне; авторів теорії — двоє.",
                  size=13, bold=True, color=INK))

    return render(os.path.join(IMG, 'lsp-attribution.svg'), W, H, *p)


if __name__ == '__main__':
    fig_substitution()
    fig_contract()
    fig_split()
    fig_lsp_lineage()
    fig_attribution()
    print("figures written")
