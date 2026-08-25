# -*- coding: utf-8 -*-
"""Фігури теми «Design docs і RFC». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── 1. Ескалація вартості виправлення дефекту за стадіями ─────────────────────
def fig_cost_of_change():
    W, H = 960, 480
    f = []

    f.append(text(W / 2, 40, "Ескалація вартості виправлення архітектурного дефекту",
                  size=16, bold=True, color=INK))

    stages = [
        ("1. Проектування (RFC)", "1×", "$100", "Виправити абзац тексту,\nуточнити модель даних", "#d4edda", FIELD),
        ("2. Розробка коду", "10×", "$1 000", "Переписати модулі,\nоновити тести", "#fff9e6", "#e0a800"),
        ("3. Тестування (QA/Staging)", "30×", "$3 000", "Регресія, блокування\nрелізного конвеєра", "#fdecea", "#d9534f"),
        ("4. Продакшен", "100×", "$10 000+", "Аварійний відкат, міграція БД,\nпростій, втрата репутації", "#fdecea", POS),
    ]

    xs = [135, 365, 595, 825]
    for i, (st_name, mult, cost, desc, fillc, col) in enumerate(stages):
        x = xs[i]
        # Заголовок стадії
        f.append(fitbox(x - 100, 75, 200, 42, st_name, size=13, bold=True,
                        fill="#eef2ff", stroke=MUTED, sw=1.8))
        
        # Блок коефіцієнта вартості
        f.append(rect(x - 90, 130, 180, 100, fill=fillc, stroke=col, sw=2.2))
        f.append(text(x, 172, mult, size=30, bold=True, color=col))
        f.append(text(x, 210, "вартість: " + cost, size=12, bold=True, color=INK))

        # Стрілка між стадіями
        if i < 3:
            f.append(arrow(x + 92, 180, xs[i+1] - 92, 180, color=MUTED, sw=2))

        # Опис наслідків
        b, bw, bh = textbox(x, 290, desc, size=12, fill=FILL, stroke=LINE, sw=1.4, pad=10)
        f.append(b)

    f.append(line(50, 365, 910, 365, color=MUTED, sw=1.2, dash="6,5"))
    b, bw, bh = textbox(W / 2, 415,
                        "Design Doc ловить прорахунки на стадії 1× — до того, як вони затверднуть у коді та базах даних",
                        size=13, bold=True, fill="#eaf7ef", stroke=FIELD, sw=2, pad=12)
    f.append(b)

    render(out("cost-of-change.svg"), W, H, *f,
           title="Ескалація вартості виправлення дефектів за фазами розробки")


# ── 2. Анатомія Design Doc / RFC ─────────────────────────────────────────────
def fig_design_doc_anatomy():
    W, H = 960, 500
    f = []

    f.append(text(W / 2, 38, "Анатомія та каркас розділів Design Doc / RFC",
                  size=16, bold=True, color=INK))

    blocks = [
        (160, 100, 260, 110, "Контекст і проблема",
         "Чому система змінюється зараз?\nЯкі бізнес-драйвери та обмеження?\nЧислові метрики поточного стану.",
         "#eef2ff", NEG),
        (480, 100, 260, 110, "Цілі та не-цілі (Non-Goals)",
         "Goals: що проект гарантовано зробить.\nNon-Goals: що свідомо НЕ робиться,\nзахист від розмивання меж.",
         "#d4edda", FIELD),
        (800, 100, 260, 110, "Пропонований дизайн",
         "Архітектурна топологія, потоки даних,\nконтракти API, схеми моделей,\nповедінка у разі збоїв.",
         "#fff9e6", "#e0a800"),
        (160, 250, 260, 110, "Наскрізні вимоги",
         "Безпека, авторизація, приватність,\nспостережуваність (метрики/трейси),\nліміти ресурсів і деградація.",
         "#f4f6f8", LINE),
        (480, 250, 260, 110, "Розглянуті альтернативи",
         "Які інші варіанти були на столі?\nЧому вони відкинуті?\nТаблиця компромісів (trade-offs).",
         "#fdecea", POS),
        (800, 250, 260, 110, "План запуску й міграції",
         "Feature flags, dark launch, тіньовий рух,\nміграція схеми даних (expand-contract),\nплан аварійного відкату.",
         "#eef2ff", NEG),
    ]

    for cx, cy, bw, bh, title_s, desc_s, fillc, col in blocks:
        f.append(rect(cx - bw / 2, cy - bh / 2, bw, bh, fill=fillc, stroke=col, sw=2))
        f.append(text(cx, cy - bh / 2 + 22, title_s, size=13, bold=True, color=col))
        lines = desc_s.split("\n")
        f.append(mtext(cx, cy - bh / 2 + 46, lines, size=11, color=INK, lh=1.35))

    f.append(line(50, 395, 910, 395, color=MUTED, sw=1.2, dash="6,5"))
    b, bw, bh = textbox(W / 2, 445,
                        "Головний критерій повноти: кожен розділ відповідає на питання, яке на рев'ю обов'язково поставлять",
                        size=13, bold=True, fill=FILL, stroke=LINE, sw=1.6, pad=12)
    f.append(b)

    render(out("design-doc-anatomy.svg"), W, H, *f,
           title="Анатомія інженерного документу проектування")


# ── 3. Життєвий цикл RFC: від чернетки до впровадження ────────────────────────
def fig_rfc_lifecycle():
    W, H = 960, 470
    f = []

    f.append(text(W / 2, 38, "Життєвий цикл технічної пропозиції (RFC Lifecycle)",
                  size=16, bold=True, color=INK))

    def node(cx, cy, title_s, sub_s, col, fillc, w=150, h=64):
        f.append(rect(cx - w / 2, cy - h / 2, w, h, fill=fillc, stroke=col, sw=2.2))
        f.append(text(cx, cy - 8, title_s, size=13, bold=True, color=col))
        f.append(text(cx, cy + 14, sub_s, size=11, color=MUTED))
        return w, h

    # 1. Draft
    node(120, 140, "1. Чернетка", "Draft / WIP", MUTED, FILL)
    f.append(arrow(195, 140, 275, 140, color=MUTED, sw=1.8))
    f.append(text(235, 125, "публікація", size=11, color=MUTED))

    # 2. Review
    node(350, 140, "2. Рев'ю", "Under Review", "#e0a800", "#fff9e6", w=150)
    f.append(arrow(425, 140, 505, 140, color=FIELD, sw=2))
    f.append(text(465, 125, "консенсус", size=11, color=FIELD, bold=True))

    # 3. Approved
    node(580, 140, "3. Ухвалено", "Approved / Accepted", FIELD, "#d4edda", w=150)
    f.append(arrow(655, 140, 735, 140, color=FIELD, sw=2))
    f.append(text(695, 125, "реалізація", size=11, color=FIELD))

    # 4. Implemented
    node(810, 140, "4. Впроваджено", "Implemented / Live", FIELD, "#eaf7ef", w=150)

    # Гілка відхилення
    f.append(arrow(350, 172, 350, 255, color=POS, sw=1.8))
    f.append(text(350, 218, "блокуючі ризики", size=11, color=POS, bold=True, anchor="start"))
    node(350, 285, "Відхилено", "Rejected / Withdrawn", POS, "#fdecea", w=150)

    # Гілка заміщення
    f.append(arrow(810, 172, 810, 255, color=MUTED, sw=1.8))
    f.append(text(810, 218, "новий дизайн", size=11, color=MUTED, anchor="start"))
    node(810, 285, "Замінено", "Superseded by RFC-XX", MUTED, FILL, w=150)

    # Петля доопрацювання
    f.append(line(310, 172, 310, 210, color="#e0a800", sw=1.5))
    f.append(line(310, 210, 160, 210, color="#e0a800", sw=1.5))
    f.append(arrow(160, 210, 160, 172, color="#e0a800", sw=1.5))
    f.append(text(235, 226, "ітерація за зауваженнями", size=11, color="#e0a800"))

    f.append(line(50, 355, 910, 355, color=MUTED, sw=1.2, dash="6,5"))
    b, bw, bh = textbox(W / 2, 410,
                        "RFC не є довічним законом: це узгоджений план, який переходить у стан коду та архівується",
                        size=13, bold=True, fill=FILL, stroke=LINE, sw=1.6, pad=12)
    f.append(b)

    render(out("rfc-lifecycle.svg"), W, H, *f,
           title="Стани та переходи життєвого циклу інженерної пропозиції")


# ── 4. Rough Consensus проти Одностайності ────────────────────────────────────
def fig_consensus_vs_unanimity():
    W, H = 960, 480
    f = []

    f.append(text(W / 2, 38, "Прийняття рішень: Одностайність vs Прагматичний консенсус (Rough Consensus)",
                  size=16, bold=True, color=INK))

    # Ліва панель: Одностайність
    f.append(rect(60, 75, 400, 270, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(260, 105, "Одностайність (Unanimity)", size=15, bold=True, color=POS))
    f.append(text(260, 130, "«Кожен учасник повинен погодитися»", size=12, italic=True, color=MUTED))

    left_points = [
        "Будь-який учасник має право вето",
        "Блокування через суб'єктивні смаки (bike-shedding)",
        "Параліч аналізу: місяці безкінечних суперечок",
        "Дизайн розмивається на догоду всім компромісам",
    ]
    for i, pt in enumerate(left_points):
        f.append(minus(95, 170 + i * 36))
        f.append(text(115, 175 + i * 36, pt, size=12, color=INK, anchor="start"))

    f.append(fitbox(80, 310, 360, 26, "Результат: затягування або компромісний монстр",
                    size=11, bold=True, fill="#ffffff", stroke=POS, sw=1.2))

    # Права панель: Rough Consensus
    f.append(rect(500, 75, 400, 270, fill="#d4edda", stroke=FIELD, sw=2))
    f.append(text(700, 105, "Rough Consensus (IETF)", size=15, bold=True, color=FIELD))
    f.append(text(700, 130, "«Усі заперечення почуті, блокуючі ризики зняті»", size=12, italic=True, color=MUTED))

    right_points = [
        "Рішення не вимагає 100% однакових думок",
        "Відхилення незгоди, якщо немає технічного доказу збою",
        "Обмежений у часі період обговорення (time-box)",
        "Фінальне слово за відповідальним архітектором / TL",
    ]
    for i, pt in enumerate(right_points):
        f.append(plus(535, 170 + i * 36))
        f.append(text(555, 175 + i * 36, pt, size=12, color=INK, anchor="start"))

    f.append(fitbox(520, 310, 360, 26, "Результат: швидке просування з контролем ризиків",
                    size=11, bold=True, fill="#ffffff", stroke=FIELD, sw=1.2))

    f.append(line(50, 375, 910, 375, color=MUTED, sw=1.2, dash="6,5"))
    b, bw, bh = textbox(W / 2, 425,
                        "Принцип IETF: «We reject: kings, presidents and voting. We believe in: rough consensus and running code»",
                        size=13, bold=True, fill="#eef2ff", stroke=NEG, sw=1.8, pad=12)
    f.append(b)

    render(out("consensus-vs-unanimity.svg"), W, H, *f,
           title="Порівняння моделей прийняття рішень під час рев'ю")


if __name__ == "__main__":
    fig_cost_of_change()
    fig_design_doc_anatomy()
    fig_rfc_lifecycle()
    fig_consensus_vs_unanimity()
    print("готово:", ", ".join(sorted(os.listdir(IMG))))
