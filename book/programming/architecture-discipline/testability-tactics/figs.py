# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: керувати входом і бачити вихід ─────────────────────────────────
def fig_control_observe():
    W, H = 940, 380
    frags = []
    frags.append(text(W / 2, 60, "Тест мусить мати два важелі: задати вхід і побачити вихід",
                      size=15, bold=True))

    # центральний компонент
    comp_cx, comp_cy = W / 2, 210
    comp, cw, ch = textbox(comp_cx, comp_cy, "Компонент\n(логіка, яку перевіряємо)",
                           size=14, bold=True, fill="#eef4ff", stroke=NEG, sw=2.4,
                           pad=18, min_w=260)
    # ЛІВОРУЧ: керування (control) — ставимо вхід і стан
    ctrl, ctw, cth = textbox(150, comp_cy, "КЕРУВАННЯ\nзадати вхід\nі стан",
                             size=13, bold=True, fill="#eafaf1", stroke=FIELD, sw=2, pad=12,
                             min_w=170)
    frags.append(ctrl)
    frags.append(arrow(150 + ctw / 2, comp_cy, comp_cx - cw / 2 - 6, comp_cy,
                       color=FIELD, sw=2.6))
    frags.append(text((150 + ctw / 2 + comp_cx - cw / 2) / 2, comp_cy - 16,
                      "стимул", size=11, italic=True, color=MUTED))

    # ПРАВОРУЧ: спостереження (observe) — читаємо вихід і стан
    obs, obw, obh = textbox(W - 150, comp_cy, "СПОСТЕРЕЖЕННЯ\nпрочитати вихід\nі стан",
                            size=13, bold=True, fill="#eafaf1", stroke=FIELD, sw=2, pad=12,
                            min_w=170)
    frags.append(obs)
    frags.append(arrow(comp_cx + cw / 2 + 6, comp_cy, W - 150 - obw / 2, comp_cy,
                       color=FIELD, sw=2.6))
    frags.append(text((comp_cx + cw / 2 + W - 150 - obw / 2) / 2, comp_cy - 16,
                      "реакція", size=11, italic=True, color=MUTED))

    frags.append(comp)

    # висновок унизу
    frags.append(text(W / 2, 330,
                      "Тестовність = наскільки легко дотягтися до обох важелів.",
                      size=13, bold=True, color=NEG))
    render(os.path.join(IMG, 'control-observe.svg'), W, H, *frags,
           title="Що взагалі потрібно, щоб протестувати шматок системи")


# ── Фігура 2: дерево тактик тестовності (дві родини) ─────────────────────────
def fig_tactics_tree():
    W, H = 980, 660
    frags = []
    # корінь
    root, rw, rh = textbox(W / 2, 60, "Полегшити перевірку системи",
                           size=16, bold=True, fill="#eef4ff", stroke=NEG, sw=2.2, pad=14)
    frags.append(root)

    box_w = 268
    # родина, задана лівим краєм колонки боксів
    fam = [
        (60, "Керувати станом\nі спостерігати його", NEG,
         ["Спеціальні тестові інтерфейси",
          "Абстрагувати джерела даних",
          "Пісочниця (ізоляція)",
          "Запис / відтворення",
          "Локалізувати зберігання стану",
          "Виконувані твердження"]),
        (W - 60 - box_w, "Обмежити\nскладність", FIELD,
         ["Обмежити структурну складність",
          "Обмежити недетермінізм"]),
    ]
    head_y = 190
    for left, head, col, items in fam:
        hcx = left + box_w / 2
        frags.append(line(W / 2, 60 + rh / 2, hcx, head_y - 34, color=MUTED, sw=1.5))
        hb, hw, hh = textbox(hcx, head_y, head, size=14.5, bold=True, fill="#fbfbfb",
                             stroke=col, sw=2.2, pad=12, min_w=box_w)
        frags.append(hb)
        # вертикальна «жила» ліворуч від колонки боксів
        spine_x = left - 20
        item_h = 46
        gap = 12
        top_y = head_y + hh / 2 + 26
        centers = [top_y + item_h / 2 + i * (item_h + gap) for i in range(len(items))]
        # жила від низу заголовка до останнього бокса
        frags.append(line(hcx, head_y + hh / 2, hcx, top_y - 10, color=col, sw=1.4))
        frags.append(line(spine_x, top_y - 10, spine_x, centers[-1], color=col, sw=1.4))
        frags.append(line(hcx, top_y - 10, spine_x, top_y - 10, color=col, sw=1.4))
        for it, cyc in zip(items, centers):
            frags.append(line(spine_x, cyc, left, cyc, color=col, sw=1.3))
            frags.append(fitbox(left, cyc - item_h / 2, box_w, item_h, it, size=12.5,
                                fill=FILL, stroke=col, sw=1.5, pad=8))
    render(os.path.join(IMG, 'tactics-tree.svg'), W, H, *frags,
           title="Тактики тестовності: дві родини за спільною метою")


# ── Фігура 3: смуга переходу пари через чотири світи ──────────────────────────
def fig_testability_lineage():
    W, H = 1000, 560
    frags = []
    frags.append(text(W / 2, 34,
                      "Одна пара «керованість / спостережуваність» — чотири світи",
                      size=16, bold=True))

    # вертикальна вісь часу ліворуч; віхи йдуть згори вниз
    axis_x = 250
    top_y = 90
    bot_y = 520
    frags.append(line(axis_x, top_y, axis_x, bot_y, color=MUTED, sw=2.2))

    # (рік, підпис-віха, колір рамки, текст праворуч)
    stops = [
        ("1959–60", "Теорія керування", NEG,
         "Калман уводить керованість\nі спостережуваність як\nвластивості стану системи"),
        ("1979–80", "Апаратне тестування", NEG,
         "SCOAP (Сандія): перший алгоритм,\nщо рахує ці міри для кожної\nлінії кристала"),
        ("1990", "Плати (JTAG)", NEG,
         "IEEE 1149.1: граничний скан\nвбудовує доступ у залізо, коли\nщупом уже не дотягтися"),
        ("1991", "Програмне забезпечення", FIELD,
         "Фрідман переносить пару в код\n(доменна тестовність); Біндер, ~1994:\n«керуй входом — спостерігай вихід»"),
        ("2012", "Канон тактик", FIELD,
         "Бас, Клементс, Казман: пара стає\nкоренем дерева тактик тестовності\n(розділ якісних атрибутів)"),
    ]
    n = len(stops)
    span = bot_y - top_y
    ys = [top_y + span * i / (n - 1) for i in range(n)]

    yr_x = 150            # центр рамки-року (ліворуч від осі)
    box_left = axis_x + 60  # ліва межа рамки-опису (праворуч від осі)
    box_w = 640
    for (yr, milestone, col, desc), cy in zip(stops, ys):
        # вузол на осі
        frags.append(circle(axis_x, cy, 7, fill=BG, stroke=col, sw=2.6))
        # рік + віха ліворуч
        yb, yw, yh = textbox(yr_x, cy, yr + "\n" + milestone, size=12.5, bold=True,
                             fill="#eef4ff" if col == NEG else "#eafaf1",
                             stroke=col, sw=2, pad=9, min_w=150)
        frags.append(line(yr_x + yw / 2, cy, axis_x, cy, color=col, sw=1.6))
        frags.append(yb)
        # опис праворуч
        lines = desc.split("\n")
        bh = len(lines) * 12.5 * 1.3 + 18
        frags.append(line(axis_x, cy, box_left, cy, color=col, sw=1.6))
        frags.append(fitbox(box_left, cy - bh / 2, box_w, bh, desc, size=12.5,
                            fill=FILL, stroke=col, sw=1.5, pad=10))
    render(os.path.join(IMG, 'testability-lineage.svg'), W, H, *frags,
           title=None)


if __name__ == "__main__":
    fig_control_observe()
    fig_tactics_tree()
    fig_testability_lineage()
    print("figures written to", IMG)
