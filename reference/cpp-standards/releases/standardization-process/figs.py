# -*- coding: utf-8 -*-
"""Фігури до теми «Як робиться стандарт C++: комітет, папери, цикл»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_wg21_funnel():
    """Схема проходження пропозиції крізь робочі підгрупи WG21."""
    W, H = 1000, 480
    out = []

    # Підзаголовок під автоматичним заголовком render(..., title=...)
    out.append(text(W / 2, 50, "Ієрархічна структура груп: від інкубації ідеї до міжнародного стандарту", size=13, color=MUTED))

    # Рівні воронки. 4 послідовні колонки-етапи.
    col_w = 210
    gap = 35
    start_x = 40
    y_top = 75
    h_col = 370

    stages = [
        {
            "num": "Етап 1",
            "title": "Інкубація та дослідження",
            "group": "Study Groups (SG)",
            "items": ["SG1 (Паралелізм)", "SG7 (Рефлексія)", "SG14 (Низька затримка)", "SG15 (Інструменти)", "SG16 (Unicode)", "SG21 (Контракти)"],
            "fill": "#eef4ff",
            "stroke": NEG,
            "desc": ["Дослідження предметної", "галузі, прототипування", "й архітектурний пошук"]
        },
        {
            "num": "Етап 2",
            "title": "Еволюція та дизайн",
            "group": "EWG / LEWG",
            "items": ["EWG (Синтаксис ядра)", "LEWG (Дизайн STL)", "EWGI / LEWGI (Інкубатор)", "Оцінка доцільності", "Узгодження з моделлю"],
            "fill": "#f0fdf4",
            "stroke": FIELD,
            "desc": ["Чи потрібна фіча мові?", "Затвердження синтаксису", "і поведінкового дизайну"]
        },
        {
            "num": "Етап 3",
            "title": "Нормативне формулювання",
            "group": "CWG / LWG",
            "items": ["CWG (Формулювання ядра)", "LWG (Формулювання STL)", "Перевірка однозначності", "Взаємодія з граматикою", "Аналіз крайових станів"],
            "fill": "#fffbeb",
            "stroke": "#d97706",
            "desc": ["Складання точного", "нормативного тексту", "мови або бібліотеки"]
        },
        {
            "num": "Етап 4",
            "title": "Пленарне голосування",
            "group": "Plenary & ISO NBs",
            "items": ["Пленарне засідання WG21", "Національні органи (NBs)", "Голосування за зміни", "Внесення в Working Draft", "Підготовка CD / DIS"],
            "fill": "#fdf2f8",
            "stroke": POS,
            "desc": ["Офіційне ухвалення", "в робочу чернетку", "стандарту ISO"]
        }
    ]

    for i, st in enumerate(stages):
        cx = start_x + i * (col_w + gap) + col_w / 2

        # Фонова картка
        out.append(rect(cx - col_w / 2, y_top, col_w, h_col, fill=st["fill"], stroke=st["stroke"], sw=2, rx=8))

        # Заголовки етапу
        out.append(text(cx, y_top + 24, st["num"], size=12, color=st["stroke"], bold=True))
        out.append(text(cx, y_top + 46, st["title"], size=13, bold=True))
        out.append(text(cx, y_top + 68, st["group"], size=12, color=MUTED, bold=True))

        # Роздільник
        out.append(line(cx - col_w / 2 + 12, y_top + 80, cx + col_w / 2 - 12, y_top + 80, color=st["stroke"], sw=1))

        # Список елементів
        item_y = y_top + 106
        for item in st["items"]:
            bb, _, _ = textbox(cx, item_y, item, size=11, pad=5, fill="#ffffff", stroke="#d1d5db", sw=1, min_w=col_w - 24)
            out.append(bb)
            item_y += 34

        # Опис цілі внизу
        out.append(line(cx - col_w / 2 + 12, y_top + 312, cx + col_w / 2 - 12, y_top + 312, color="#d1d5db", sw=1))
        out.append(mtext(cx, y_top + 332, st["desc"], size=11, color=INK, lh=1.35, bold=False))

        # Стрілка між етапами
        if i < len(stages) - 1:
            arr_x1 = cx + col_w / 2 + 4
            arr_x2 = arr_x1 + gap - 8
            arr_y = y_top + 180
            out.append(arrow(arr_x1, arr_y, arr_x2, arr_y, color=LINE, sw=2))

    render(os.path.join(IMG, 'wg21-funnel.svg'), W, H, *out,
           title="Конвеєр розробки пропозицій у комітеті WG21")


def fig_train_model():
    """Схема трирічного циклу стандарту (Train Model)."""
    W, H = 980, 440
    out = []

    # Підзаголовок під автоматичним заголовком render
    out.append(text(W / 2, 54, "Потяг відправляється строго за розкладом: неготові фічі чекають наступного потяга", size=13, color=MUTED))

    # Смуга часу
    timeline_y = 130
    W_tl = 880
    x0 = 50
    out.append(line(x0, timeline_y, x0 + W_tl, timeline_y, color=LINE, sw=3))

    # Три роки
    year_w = W_tl / 3
    years = [
        ("Рік 1 (Старт циклу)", ["Розробка дизайну,", "подання пропозицій (P-papers),", "інкубація в підгрупах SG"], "#eff6ff", NEG),
        ("Рік 2 (Стабілізація)", ["Завершення дизайну", "в EWG/LEWG, передача", "формулювань у CWG/LWG"], "#f0fdf4", FIELD),
        ("Рік 3 (Фіксація й ISO)", ["Feature Freeze (заморозка),", "балотування CD / DIS,", "виправлення дефектів"], "#fff7ed", POS)
    ]

    for i, (title, desc_lines, fill, col) in enumerate(years):
        bx = x0 + i * year_w
        # Віха на лінії
        out.append(circle(bx + year_w / 2, timeline_y, 8, fill=col, stroke=LINE, sw=2))
        out.append(text(bx + year_w / 2, timeline_y - 18, f"Фаза {i+1}", size=12, color=col, bold=True))

        # Картка опису під лінією
        card_cx = bx + year_w / 2
        out.append(rect(bx + 8, 160, year_w - 16, 120, fill=fill, stroke=col, sw=1.5, rx=6))
        out.append(text(card_cx, 185, title, size=13, bold=True, color=col))
        out.append(mtext(card_cx, 210, desc_lines, size=11, color=INK, lh=1.35))

    # Ключові контрольні точки
    milestones_y = 320
    out.append(text(W / 2, milestones_y, "Ключові контрольні точки 3-річного вікна:", size=14, bold=True))

    ms_boxes = [
        (170, 375, ["Feature Cutoff (Кінець 2 року)", "Жодних нових фіч у реліз"], "#fee2e2", POS),
        (500, 375, ["CD Ballot (Початок 3 року)", "Коментарі національних органів"], "#fef3c7", "#b45309"),
        (810, 375, ["DIS / IS (Кінець 3 року)", "Офіційне затвердження ISO"], "#dcfce7", FIELD)
    ]

    for cx, cy, txt_lines, fill, col in ms_boxes:
        bb, _, _ = textbox(cx, cy, txt_lines, size=11, pad=8, fill=fill, stroke=col, sw=1.5, min_w=240)
        out.append(bb)

    render(os.path.join(IMG, 'train-model-cycle.svg'), W, H, *out,
           title="Трирічний цикл випуску стандартів C++ (Train Model)")


def fig_paper_lifecycle():
    """Життєвий цикл документа (від D-paper до стандарту)."""
    W, H = 340, 320
    W = 980
    out = []

    nodes = [
        (110, 120, ["Чернетка автора", "DXXXXR0", "(Робоча версія)"], "#f3f4f6", LINE),
        (305, 120, ["Перша публікація", "PXXXXR0", "(Подання в розсилку)"], "#eff6ff", NEG),
        (500, 120, ["Доопрацювання", "PXXXXRn", "(EWG/LEWG ревізії)"], "#f0fdf4", FIELD),
        (695, 120, ["Формулювання", "CWG / LWG", "(Текст у стандарт)"], "#fffbeb", "#d97706"),
        (880, 120, ["Working Draft", "Ухвалено Plenary", "(Стандарт ISO)"], "#fdf2f8", POS)
    ]

    for i, (cx, cy, txt_lines, fill, col) in enumerate(nodes):
        bb, _, _ = textbox(cx, cy, txt_lines, size=11, pad=8, fill=fill, stroke=col, sw=1.8, min_w=125)
        out.append(bb)

        if i < len(nodes) - 1:
            next_cx = nodes[i+1][0]
            out.append(arrow(cx + 65, cy, next_cx - 65, cy, color=LINE, sw=1.8))

    # Пояснення знизу
    out.append(rect(60, 205, 860, 85, fill="#fafafa", stroke="#e5e7eb", sw=1, rx=6))
    out.append(text(W / 2, 228, "Ключовий принцип версіонування документів WG21:", size=12, bold=True))
    out.append(mtext(W / 2, 252,
                     ["Номер PXXXX закріплюється за ідеєю назавжди. Кожна зміна дизайну чи формулювань отримує новий номер ревізії (R0 → R1 → R2...).",
                      "Історичні папери до 2015 року мали префікс N (наприклад, N3337) і єдину наскрізну нумерацію."],
                     size=11, color=MUTED, lh=1.35))

    render(os.path.join(IMG, 'paper-lifecycle.svg'), W, H, *out,
           title="Еволюція документа: шлях пропозиції від чернетки до стандарту")


def main():
    fig_wg21_funnel()
    fig_train_model()
    fig_paper_lifecycle()
    print("Усі фігури згенеровано успішно.")


if __name__ == '__main__':
    main()
