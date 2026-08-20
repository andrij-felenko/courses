# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ACC = "#7a4ea8"    # фіолетовий — акцент методу / рішень
ACCBG = "#f3edfb"
WARNBG = "#fff6e0"
WARN = "#d97706"

# ── 1. atam-nine-steps: 9 кроків ATAM, згрупованих у дві фази ─────────────────
def fig_atam_nine_steps():
    W, H = 960, 580
    p = []

    # Заголовок фаз
    p.append(text(250, 48, "Фаза 1: Оцінювачі та архітектурна група", size=13, color=ACC, bold=True))
    p.append(text(710, 48, "Фаза 2: Розширені стейкхолдери", size=13, color=FIELD, bold=True))

    # Розділювальна лінія між фазами
    p.append(line(480, 36, 480, H - 70, color="#d0d4da", sw=1.5, dash="6 5"))

    # Кроки Фази 1 (кроки 1-6)
    p1_steps = [
        ("1. Презентація ATAM", "Вирівнювання термінів, правил і меж оцінки", MUTED, "#f0f1f3"),
        ("2. Бізнес-драйвери", "Контекст, місія, функційні межі, цілі бізнесу", NEG, "#eaf0fd"),
        ("3. Презентація архітектури", "Діаграми поглядів, обмеження, патерни виконання", NEG, "#eaf0fd"),
        ("4. Каталогізація підходів", "Фіксація архітектурних стилів і тактик", ACC, ACCBG),
        ("5. Дерево корисності", "Формування та пріоритезація сценаріїв (В,В)", ACC, ACCBG),
        ("6. Аналіз підходів (Фаза 1)", "Трасування топ-сценаріїв → пошук S, T, R, NR", POS, "#fdecea"),
    ]

    bw1 = 400
    bh1 = 58
    y0_1 = 76
    gap1 = 16

    for i, (stitle, ssub, col, fill) in enumerate(p1_steps):
        y = y0_1 + i * (bh1 + gap1)
        p.append(rect(50, y, bw1, bh1, fill=fill, stroke=col, sw=1.6, rx=8))
        p.append(text(66, y + 22, stitle, size=11.5, color=col, anchor="start", bold=True))
        p.append(text(66, y + 43, ssub, size=9.5, color=INK, anchor="start"))
        if i < len(p1_steps) - 1:
            p.append(arrow(250, y + bh1 + 1, 250, y + bh1 + gap1 - 1, color=MUTED, sw=1.4))

    # Перехід від Фази 1 до Фази 2 (стрілка між кроком 6 і кроком 7)
    p.append(line(450, y0_1 + 5 * (bh1 + gap1) + bh1 / 2, 510, 105, color=ACC, sw=2, dash="4 4"))
    p.append(arrow(510, 105, 540, 105, color=ACC, sw=2))

    # Кроки Фази 2 (кроки 7-9)
    p2_steps = [
        ("7. Штурм сценаріїв", "Генерація сценаріїв ширшим колом (devs, ops, QA)", FIELD, "#eef6ef"),
        ("8. Аналіз підходів (Фаза 2)", "Перевірка архітектури на сценаріях стейкхолдерів", POS, "#fdecea"),
        ("9. Презентація результатів", "Каталог ризиків, компромісів та теми ризиків", WARN, WARNBG),
    ]

    bw2 = 380
    bh2 = 82
    y0_2 = 76
    gap2 = 46

    for j, (stitle, ssub, col, fill) in enumerate(p2_steps):
        y = y0_2 + j * (bh2 + gap2)
        p.append(rect(540, y, bw2, bh2, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(558, y + 26, stitle, size=12, color=col, anchor="start", bold=True))
        p.append(mtext(558, y + 50, ssub, size=9.8, color=INK, anchor="start", lh=1.3))
        if j < len(p2_steps) - 1:
            p.append(arrow(730, y + bh2 + 1, 730, y + bh2 + gap2 - 1, color=MUTED, sw=1.6))

    # Підсумковий блок результату
    cb, cw, ch = textbox(W / 2, H - 32,
                         "Результат ATAM: не оцінка «добре/погано», а точна мапа рішень — чутливості (S), компроміси (T), ризики (R) і теми ризиків.",
                         size=10.5, pad=12, fill="#f4f6f8", stroke=INK, sw=1.5, color=INK)
    p.append(cb)

    render(os.path.join(OUT, "atam-nine-steps.svg"), W, H, *p,
           title="Дев'ять кроків ATAM у двох фазах оцінювання")


# ── 2. utility-tree-distributed: Дерево корисності розподіленої системи ────────
def fig_utility_tree_distributed():
    W, H = 940, 520
    p = []

    # Корінь дерева
    rootx, rooty = 110, H / 2 - 15
    body, rw, rh = textbox(rootx, rooty, "Корисність\nрозподіленої\nсистеми", size=12, pad=12,
                           fill=ACCBG, stroke=ACC, sw=2, color=ACC, bold=True)
    p.append(body)

    # Атрибути якості
    attrs = [
        ("Доступність", 70),
        ("Швидкодія", 185),
        ("Узгодженість", 300),
        ("Змінюваність", 420),
    ]
    ax = 320

    # Сценарії: (текст, y, важливість_бізнесу, складність_архітектури)
    leaves = {
        "Доступність": [
            ("Падіння лідера: новий лідер < 3 с", 45, "В", "В"),
            ("Розділення 1 ДЦ: деградація читань без зупинки", 95, "В", "В")
        ],
        "Швидкодія": [
            ("Пік 25k rps: затримка запису p99 < 80 мс", 160, "В", "В"),
            ("Фонові звіти: вплив на OLTP < 5 % CPU", 210, "С", "Н")
        ],
        "Узгодженість": [
            ("Збій мережі під час 2PC: 0 подвійних списань", 275, "В", "В"),
            ("Читання після власного запису: lag < 100 мс", 325, "В", "С")
        ],
        "Змінюваність": [
            ("Новий платіжний провайдер: < 5 днів без ядра", 395, "В", "С"),
            ("Міграція схеми подій: 0 downtime версій", 445, "С", "В")
        ],
    }

    lx = 540
    leafw = 340

    for aname, ay in attrs:
        # Лінія від кореня до атрибута
        p.append(line(rootx + rw / 2, rooty, ax - 70, ay, color=MUTED, sw=1.6))
        ab, aw, ah = textbox(ax, ay, aname, size=11, pad=9,
                             fill="#eef1f5", stroke=INK, sw=1.4, color=INK, bold=True)
        p.append(ab)

        for stext, ly, imp, diff in leaves[aname]:
            p.append(line(ax + aw / 2, ay, lx - 6, ly, color="#c8ccd2", sw=1.2))
            is_critical = (imp == "В" and diff == "В")
            fill = "#fdecea" if is_critical else BG
            stroke = POS if is_critical else "#c8ccd2"
            p.append(rect(lx, ly - 15, leafw, 30, fill=fill, stroke=stroke, sw=1.5 if is_critical else 1.1, rx=6))
            p.append(text(lx + 10, ly + 4, stext, size=9.5, color=INK, anchor="start"))
            tag = "(%s, %s)" % (imp, diff)
            tcol = POS if is_critical else MUTED
            p.append(text(lx + leafw - 10, ly + 4, tag, size=9.5, color=tcol, anchor="end", bold=is_critical))

    # Легенда
    p.append(text(lx, H - 32, "Пара пріоритетів: (Важливість для бізнесу, Складність для архітектури)", size=9.5, color=MUTED, anchor="start"))
    p.append(text(lx, H - 16, "Сценарії (В, В) — червоні листки: ядро аналізу на кроках 6 та 8", size=9.5, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "utility-tree-distributed.svg"), W, H, *p,
           title="Дерево корисності: структурування та пріоритезація вимог до якості")


# ── 3. sensitivity-tradeoff-quadrant: Простір відкриттів ATAM ─────────────────
def fig_sensitivity_tradeoff_quadrant():
    W, H = 920, 520
    p = []

    # Чотири квадранти відкриттів ATAM
    box_w, box_h = 390, 190
    x_left, x_right = 55, 475
    y_top, y_bottom = 60, 275

    # 1. Точка чутливості
    p.append(rect(x_left, y_top, box_w, box_h, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=10))
    p.append(text(x_left + 20, y_top + 28, "Точка чутливості (Sensitivity Point, S)", size=12, color=NEG, anchor="start", bold=True))
    p.append(mtext(x_left + 20, y_top + 56,
                   "Параметр p суттєво змінює ОДИН якісний атрибут (|∂Q/∂p| >> 0).\n"
                   "Рішення концентрує вплив на одній шкалі.\n\n"
                   "Приклад: розмір буфера сокетів прямо задає стійкість до\n"
                   "мікровсплесків трафіку без втрати пакетів.",
                   size=9.5, color=INK, anchor="start", lh=1.3))

    # 2. Точка компромісу
    p.append(rect(x_right, y_top, box_w, box_h, fill=ACCBG, stroke=ACC, sw=2, rx=10))
    p.append(text(x_right + 20, y_top + 28, "Точка компромісу (Tradeoff Point, T)", size=12, color=ACC, anchor="start", bold=True))
    p.append(mtext(x_right + 20, y_top + 56,
                   "Параметр p тягне ДВА атрибути в ПРОТИЛЕЖНІ боки.\n"
                   "Неможливо покращити один, не погіршивши інший.\n\n"
                   "Приклад: синхронний кворум реплікації (R+W > N)\n"
                   "гарантує строгу консистентність, але збільшує затримку.",
                   size=9.5, color=INK, anchor="start", lh=1.3))

    # 3. Ризик
    p.append(rect(x_left, y_bottom, box_w, box_h, fill="#fdecea", stroke=POS, sw=2, rx=10))
    p.append(text(x_left + 20, y_bottom + 28, "Архітектурний ризик (Risk, R)", size=12, color=POS, anchor="start", bold=True))
    p.append(mtext(x_left + 20, y_bottom + 56,
                   "Рішення, що ставить під загрозу досягнення міри якості,\n"
                   "або наслідки якого команда не прорахувала.\n\n"
                   "Приклад: необмежена черга повідомлень без backpressure\n"
                   "загрожує OOM під час сплеску навантаження.",
                   size=9.5, color=INK, anchor="start", lh=1.3))

    # 4. Не-ризик
    p.append(rect(x_right, y_bottom, box_w, box_h, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(x_right + 20, y_bottom + 28, "Не-ризик / Обґрунтоване рішення (Non-Risk, NR)", size=12, color=FIELD, anchor="start", bold=True))
    p.append(mtext(x_right + 20, y_bottom + 56,
                   "Рішення надійно гарантує потрібну міру якості за рахунок\n"
                   "чітко визначеного архітектурного інваріанта.\n\n"
                   "Приклад: використання ідемпотентних ключів у Kafka-споживачах\n"
                   "виключає дублювання транзакцій при повторних відправках.",
                   size=9.5, color=INK, anchor="start", lh=1.3))

    # Висновок під квадрантами
    cb, cw, ch = textbox(W / 2, H - 28,
                         "Зв'язок: точки компромісу (T) без явного інваріанта стають ризиками (R); з доведеним інваріантом — не-ризиками (NR).",
                         size=10.5, pad=11, fill="#f4f6f8", stroke=LINE, sw=1.4, color=INK)
    p.append(cb)

    render(os.path.join(OUT, "sensitivity-tradeoff-quadrant.svg"), W, H, *p,
           title="Аналітичний простір ATAM: точки чутливості, компроміси, ризики та не-ризики")


# ── 4. risk-themes-synthesis: Синтез окремих ризиків у системні теми ризиків ──
def fig_risk_themes_synthesis():
    W, H = 940, 500
    p = []

    # Ліва колонка: сирі ризики зі сценаріїв
    p.append(text(180, 52, "Сирі ризики (рівень сценаріїв)", size=12, color=POS, bold=True))

    risks = [
        "R1: Відсутній таймаут на виклику платіжного шлюзу",
        "R2: Пул з'єднань БД спільний для читання й запису",
        "R3: Немає обмеження швидкості на публічному API",
        "R4: Каскадні повторні спроби (retry storm) при збоях",
        "R5: Реплікація без детектора розколу (split-brain)",
        "R6: Синхронний ланцюжок 6 мікросервісів при замовленні"
    ]

    rx0, ry0, rw, rh, rgap = 40, 78, 300, 48, 14
    for i, rtext in enumerate(risks):
        y = ry0 + i * (rh + rgap)
        p.append(rect(rx0, y, rw, rh, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
        p.append(mtext(rx0 + 12, y + 18, rtext, size=9.5, color=INK, anchor="start", lh=1.2))

    # Права колонка: системні теми ризиків (Risk Themes)
    p.append(text(720, 52, "Теми ризиків (Risk Themes — рівень бізнесу)", size=12, color=ACC, bold=True))

    themes = [
        ("Тема 1: Відсутність ізоляції відмов (Bulkhead)",
         "Поодинокий повільний сервіс чи запит монополізує\nспільні ресурси та паралізує всю систему."),
        ("Тема 2: Ілюзія надійності синхронних ланцюжків",
         "Складна синхронна взаємодія експоненційно\nмножить імовірність повної відмови системи."),
        ("Тема 3: Некерована поведінка під час перевантаження",
         "Відсутність узгодженої стратегії скидання навантаження\n(load shedding) перетворює піковий трафік на колапс.")
    ]

    tx0, ty0, tw, th, tgap = 520, 88, 380, 92, 34
    for j, (title, desc) in enumerate(themes):
        y = ty0 + j * (th + tgap)
        p.append(rect(tx0, y, tw, th, fill=ACCBG, stroke=ACC, sw=1.8, rx=8))
        p.append(text(tx0 + 16, y + 26, title, size=11.5, color=ACC, anchor="start", bold=True))
        p.append(mtext(tx0 + 16, y + 50, desc, size=9.5, color=INK, anchor="start", lh=1.3))

    # Стрілки агрегації від лівих ризиків до правих тем
    p.append(line(rx0 + rw + 2, ry0 + 0 * (rh + rgap) + rh / 2, tx0 - 6, ty0 + 0 * (th + tgap) + 26, color=MUTED, sw=1.3))
    p.append(line(rx0 + rw + 2, ry0 + 1 * (rh + rgap) + rh / 2, tx0 - 6, ty0 + 0 * (th + tgap) + th / 2, color=MUTED, sw=1.3))

    p.append(line(rx0 + rw + 2, ry0 + 4 * (rh + rgap) + rh / 2, tx0 - 6, ty0 + 1 * (th + tgap) + 26, color=MUTED, sw=1.3))
    p.append(line(rx0 + rw + 2, ry0 + 5 * (rh + rgap) + rh / 2, tx0 - 6, ty0 + 1 * (th + tgap) + th / 2, color=MUTED, sw=1.3))

    p.append(line(rx0 + rw + 2, ry0 + 2 * (rh + rgap) + rh / 2, tx0 - 6, ty0 + 2 * (th + tgap) + 26, color=MUTED, sw=1.3))
    p.append(line(rx0 + rw + 2, ry0 + 3 * (rh + rgap) + rh / 2, tx0 - 6, ty0 + 2 * (th + tgap) + th / 2, color=MUTED, sw=1.3))

    # Нижній висновок
    cb, cw, ch = textbox(W / 2, H - 28,
                         "Теми ризиків показують системні прогалини в архітектурному баченні, які неможливо вирішити латанням окремих сервісів.",
                         size=10.5, pad=11, fill="#f4f6f8", stroke=LINE, sw=1.4, color=INK)
    p.append(cb)

    render(os.path.join(OUT, "risk-themes-synthesis.svg"), W, H, *p,
           title="Синтез ризиків: перехід від конкретних дефектів до стратегічних тем ризиків")


# ── 5. pareto-tradeoff-math: Геометрія компромісу у просторі двох якостей ─────
def fig_pareto_tradeoff_math():
    W, H = 880, 520
    p = []

    ox, oy = 130, H - 90
    axx, axy = 640, 360

    # Осі
    p.append(arrow(ox, oy, ox + axx + 20, oy, color=INK, sw=2))
    p.append(arrow(ox, oy, ox, oy - axy - 20, color=INK, sw=2))
    p.append(text(ox + axx + 10, oy + 32, "Затримка p99 (мс) →  (менше = краще)", size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 10, oy - axy - 14, "Доступність (дев'ятки) ↑  (більше = краще)", size=11, color=MUTED, anchor="start"))

    # Крива Парето (Tradeoff frontier)
    import math
    pts = []
    for i in range(41):
        t = i / 40.0
        x = ox + 40 + t * 540
        y = oy - (30 + 320 * (1.0 - (1.0 - t) ** 2.2))
        pts.append((x, y))

    poly_str = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly_str, ACC))
    p.append(text(pts[-1][0] - 10, pts[-1][1] - 14, "Межа досяжного (Парето-фронтир)", size=11, color=ACC, anchor="end", bold=True))

    # Точка A (Асинхронний кворум)
    ax_pt, ay_pt = pts[8]
    p.append(circle(ax_pt, ay_pt, 7, fill=BG, stroke=NEG, sw=2.2))
    p.append(text(ax_pt - 14, ay_pt - 14, "A: Асинхронна реплікація (низька латентність, 99.9%)", size=10, color=NEG, anchor="end", bold=True))

    # Точка B (Синхронний Raft/Paxos)
    bx_pt, by_pt = pts[32]
    p.append(circle(bx_pt, by_pt, 7, fill=ACCBG, stroke=ACC, sw=2.4))
    p.append(text(bx_pt + 14, by_pt + 6, "B: Синхронний консенсус (висока доступність, 99.999%, більша затримка)", size=10, color=ACC, anchor="start", bold=True))

    # Стрілка компромісу між A та B
    p.append(arrow(ax_pt, ay_pt, bx_pt, by_pt, color=FIELD, sw=2))
    p.append(text((ax_pt + bx_pt) / 2 + 30, (ay_pt + by_pt) / 2 - 10, "Вектор компромісу (Tradeoff)", size=10, color=FIELD, bold=True))

    # Недосяжна зона
    p.append(circle(ax_pt, by_pt - 10, 6, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(ax_pt, by_pt - 26, "Недосяжна зона (ілюзія «все й одразу»)", size=10, color=POS, anchor="middle", bold=True))

    cb, cw, ch = textbox(W / 2, H - 28,
                         "Градієнти компромісу: на межі Парето будь-яке покращення доступності вимагає збільшення затримки або вартості.",
                         size=10.5, pad=11, fill="#f4f6f8", stroke=LINE, sw=1.4, color=INK)
    p.append(cb)

    render(os.path.join(OUT, "pareto-tradeoff-math.svg"), W, H, *p,
           title="Геометрія компромісу: простір якостей та межа Парето в розподілених системах")


if __name__ == "__main__":
    fig_atam_nine_steps()
    fig_utility_tree_distributed()
    fig_sensitivity_tradeoff_quadrant()
    fig_risk_themes_synthesis()
    fig_pareto_tradeoff_math()
    print("All figures generated successfully.")
