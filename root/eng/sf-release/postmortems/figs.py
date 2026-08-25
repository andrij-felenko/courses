# -*- coding: utf-8 -*-
"""Фігури до теми «Постмортем без винних».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"
GRAY  = "#9aa0a6"
PANEL = "#fbfbfb"


# ── 1. Модель швейцарського сиру (Swiss Cheese Model) ─────────────────────────
def fig_swiss_cheese():
    W, H = 960, 530
    f = [text(W / 2, 28, "Модель швейцарського сиру: збіг прихованих дефектів замість «єдиної вини»", size=16, bold=True)]

    # 5 захисних шарів (скибок сиру)
    layers = [
        (60,  "1. Статичний аналіз", "Пропущено крайовий\nвипадок у типах", POS),
        (220, "2. Тестове середовище", "Мок бази повертав\nінший код помилки", POS),
        (380, "3. Канарковий реліз", "Поріг трафіку 1%\nне виявив деградації", POS),
        (540, "4. Моніторинг і телеметрія", "Алерт замасковано\nплаваючим порогом", POS),
        (700, "5. Аварійний захист", "Circuit breaker мав\nпомилку в таймауті", POS),
    ]

    # Малюємо шари
    hole_y_coords = [130, 165, 200, 235, 270]
    
    for i, (lx, ltitle, lhole_desc, col) in enumerate(layers):
        # Тіло скибки
        f.append(rect(lx, 56, 140, 310, fill="#fdf6e3", stroke="#d3a03e", sw=2, rx=8))
        f.append(fitbox(lx + 6, 64, 128, 40, ltitle, size=10.5, stroke="#d3a03e", fill="#ffffff", bold=True))
        
        # Отвори в сирі (латентні дефекти)
        hy = hole_y_coords[i]
        f.append(circle(lx + 70, hy, 22, fill="#ffffff", stroke=POS, sw=1.8))
        # Опис дефекту під отвором або над отвором
        f.append(fitbox(lx + 8, 308, 124, 50, lhole_desc, size=10, stroke=GRAY, fill="#ffffff", color=INK))

    # Траєкторія небезпеки (Червоний вектор збою, що проходить крізь усі отвори)
    f.append(fitbox(10, 108, 42, 44, "Тригер\n(дія)", size=9.5, stroke=POS, fill="#fdecea", color=POS, bold=True))
    f.append(arrow(52, 130, 110, 130, color=POS, sw=2.6))
    f.append(line(110, 130, 270, 165, color=POS, sw=2.6))
    f.append(line(270, 165, 430, 200, color=POS, sw=2.6))
    f.append(line(430, 200, 590, 235, color=POS, sw=2.6))
    f.append(line(590, 235, 750, 270, color=POS, sw=2.6))
    f.append(arrow(750, 270, 850, 290, color=POS, sw=3.0))
    
    f.append(rect(854, 266, 94, 52, fill="#fdecea", stroke=POS, sw=2, rx=6))
    f.append(text(901, 288, "КАТАСТРОФА", size=11, color=POS, bold=True))
    f.append(text(901, 304, "Відмова сервісу", size=9.5, color=POS))

    # Нижній аналітичний блок
    py = 384
    f.append(rect(24, py, W - 48, 126, fill=PANEL, stroke=LINE, sw=1.4, rx=8))
    f.append(text(44, py + 22, "Системний висновок інженерії безпеки (Джеймс Різон, Сідні Деккер):", size=12, color=INK, anchor="start", bold=True))
    
    concl_items = [
        ("Помилка людини — симптом, а не причина", "Дія інженера є лише спусковим гачком; аварія відбувається тому, що захисні шари містили латентні пробоїни."),
        ("Покарання маскує вразливості", "Звільнення інженера не закриває жодного отвору в системі: наступний інженер зіткнеться з тією ж пасткою."),
    ]
    cy = py + 36
    for ct, cd in concl_items:
        f.append(fitbox(40, cy, 876, 36, ct + " · " + cd, size=10.5, stroke=GRAY, fill="#ffffff", anchor="start"))
        cy += 42

    render(os.path.join(IMG, "swiss-cheese-incident.svg"), W, H, *f)


# ── 2. Омана ретроспективного погляду (Hindsight Bias) ────────────────────────
def fig_hindsight_bias():
    W, H = 960, 500
    f = [text(W / 2, 28, "Омана ретроспективного погляду: сприйняття в момент дії проти погляду постфактум", size=16, bold=True)]

    # Лівий блок: Реальний контекст у момент дії (тунель сприйняття)
    f.append(rect(24, 56, 436, 420, fill="#f4f6f8", stroke=NEG, sw=1.8, rx=10))
    f.append(text(242, 84, "ПІД ЧАС ІНЦИДЕНТУ (ПОГЛЯД ЗСЕРЕДИНИ)", size=13, color=NEG, bold=True))
    f.append(text(242, 102, "Принцип локальної раціональності (Local Rationality)", size=11, color=MUTED, italic=True))

    in_moment = [
        ("Шум та неповнота даних", "Десятки суперечливих алертів, графіки латентності зростають у 15 сервісах одночасно."),
        ("Психологічний тиск часу", "Падіння SLO, кожна хвилина простою коштує бізнесу тисячі доларів, черговий діє швидко."),
        ("Локальна обґрунтованість", "Вибрана гіпотеза повністю відповідала даним і документації, доступним черговому о 03:15."),
        ("Розпорошена увага", "Інженер оперує поточною робочою пам'яттю і не може знати про паралельний реліз сусідньої команди."),
    ]
    iy = 120
    for t_box, d_box in in_moment:
        f.append(fitbox(40, iy, 404, 76, t_box + "\n" + d_box, size=11, stroke=NEG, fill="#ffffff"))
        iy += 86

    # Правий блок: Омана ретроспективного погляду (Hindsight Bias)
    f.append(rect(500, 56, 436, 420, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    f.append(text(718, 84, "ПІСЛЯ ІНЦИДЕНТУ (РЕТРОСПЕКТИВНА ОМАНА)", size=13, color=POS, bold=True))
    f.append(text(718, 102, "Ілюзія очевидності та неминучості наслідків", size=11, color=MUTED, italic=True))

    post_moment = [
        ("Знання результату спотворює аналіз", "Коли фінал відомий, ланцюг подій здається простим, лінійним і заздалегідь визначеним."),
        ("Ігнорування інформаційного шуму", "Критики бачать лише один ключовий лог, забуваючи про 10 000 паралельних нерелевантних повідомлень."),
        ("Звинувачення інженера («як можна було...»)", "«Чому він не перевірив рядок 42?» — хоча до аварії рядок 42 ніколи не викликав збоїв."),
        ("Хибне відчуття безпеки", "Покарання «винного» створює ілюзію вирішення проблеми, залишаючи системну пастку незмінною."),
    ]
    py = 120
    for t_box, d_box in post_moment:
        f.append(fitbox(516, py, 404, 76, t_box + "\n" + d_box, size=11, stroke=POS, fill="#ffffff"))
        py += 86

    render(os.path.join(IMG, "hindsight-bias-divergence.svg"), W, H, *f)


# ── 3. Фази інциденту на часовій шкалі (Timeline Lifecycle) ───────────────────
def fig_timeline_phases():
    W, H = 960, 520
    f = [text(W / 2, 28, "Хронологія життєвого циклу інциденту: ключові інтервали та метрики SRE", size=16, bold=True)]

    # Вісь часу
    f.append(line(40, 190, 920, 190, color=LINE, sw=2.5))
    f.append(arrow(890, 190, 930, 190, color=LINE, sw=2.5))
    f.append(text(920, 214, "Час (t)", size=11, color=LINE, anchor="end", italic=True))

    # Точки на осі часу
    points = [
        (70,  "T_inject",   "Дефект внесено",   "Мердж коду / зміна конфігу", GRAY),
        (200, "T_trigger",  "Тригер збою",      "Сплеск трафіку / cron-завдання", AMBER),
        (330, "T_impact",   "Початок впливу",   "Перші 5xx помилки у клієнтів", POS),
        (460, "T_detect",   "Виявлення (алерт)","Спрацював SLI burn-rate алерт", POS),
        (590, "T_ack",      "Прийом черговим",  "Формування командного каналу", NEG),
        (730, "T_mitigate", "Пом'якшення",      "Трафік перемкнуто / відкат", FIELD),
        (870, "T_resolve",  "Повне відновлення","База оновлена, стан у нормі", FIELD),
    ]

    for x, tag, label, desc, col in points:
        # Вертикальний маркер
        f.append(line(x, 140, x, 240, color=col, sw=1.8, dash="4,4"))
        f.append(circle(x, 190, 6, fill=col, stroke="#ffffff", sw=2))
        
        # Підпис зверху
        f.append(fitbox(x - 55, 96, 110, 38, tag + "\n" + label, size=10, stroke=col, fill="#ffffff", bold=True))
        # Підпис знизу
        f.append(fitbox(x - 55, 248, 110, 56, desc, size=9.5, stroke=GRAY, fill="#ffffff"))

    # Інтервали (MTTD, MTTA, MTTM, MTTR)
    intervals = [
        (330, 460, 54,  "MTTD (Mean Time to Detect)", "13 хв · час сліпоти моніторингу", POS),
        (460, 590, 54,  "MTTA (Time to Acknowledge)", "6 хв · реакція чергового інженера", NEG),
        (590, 730, 54,  "MTTM (Time to Mitigate)", "24 хв · локалізація радіуса ураження", AMBER),
        (330, 870, 318, "MTTR (Mean Time to Resolve) — повний час відновлення (68 хв)", "Спалено 38% місячного бюджету помилок (Error Budget)", FIELD),
    ]

    # Верхні дужки інтервалів
    for x1, x2, y, name_i, desc_i, col in intervals[:3]:
        f.append(line(x1 + 4, y, x2 - 4, y, color=col, sw=1.6))
        f.append(line(x1 + 4, y - 4, x1 + 4, y + 4, color=col, sw=1.6))
        f.append(line(x2 - 4, y - 4, x2 - 4, y + 4, color=col, sw=1.6))
        f.append(fitbox((x1 + x2) / 2 - 60, y - 24, 120, 22, name_i.split(" ")[0], size=10, stroke=col, fill="#ffffff", bold=True))

    # Нижній сумарний інтервал MTTR
    x_start, x_end, y_sum = 330, 870, 330
    f.append(line(x_start, y_sum, x_end, y_sum, color=POS, sw=2.2))
    f.append(line(x_start, y_sum - 6, x_start, y_sum + 6, color=POS, sw=2.2))
    f.append(line(x_end, y_sum - 6, x_end, y_sum + 6, color=POS, sw=2.2))
    f.append(fitbox((x_start + x_end) / 2 - 200, y_sum + 10, 400, 44, intervals[3][3] + "\n" + intervals[3][4], size=10.5, stroke=POS, fill="#ffffff", bold=True))

    # Нижня інформаційна панель
    py = 410
    f.append(rect(24, py, W - 48, 92, fill=PANEL, stroke=LINE, sw=1.4, rx=8))
    f.append(text(44, py + 24, "Цінність точного таймлайну для постмортему:", size=12, color=INK, anchor="start", bold=True))
    f.append(fitbox(40, py + 34, 876, 44, "Таймлайн дає змогу розділити інцидент на незалежні фази: оптимізація MTTD вимагає покращення алертів, MTTA — налаштування чергувань, а MTTM — автоматизації відкату та розгортання захисних контурів.", size=10.5, stroke=GRAY, fill="#ffffff", anchor="start"))

    render(os.path.join(IMG, "incident-timeline-phases.svg"), W, H, *f)


# ── 4. Ієрархія надійності коригувальних дій ──────────────────────────────────
def fig_action_hierarchy():
    W, H = 960, 520
    f = [text(W / 2, 28, "Ієрархія надійності коригувальних дій (Hierarchy of Action Items)", size=16, bold=True)]

    # 4 рівні піраміди заходів
    tiers = [
        (1, "1 · Архітектурне усунення (Elimination)",
            "Повне вилучення класу вразливості: статична типізація, незмінна інфраструктура, закриття небезпечних CLI-команд.",
            "#eafaf1", FIELD, "Найвища стійкість"),
        (2, "2 · Інженерна автоматизація (Automation & Guardrails)",
            "Автоматичний відкіт при деградації метрик, валідаційні вебхуки у k8s, обмеження ретраїв, circuit breakers.",
            "#eef2fb", NEG, "Висока стійкість"),
        (3, "3 · Діагностика та спостережуваність (Detection & Alerts)",
            "Додавання гранулярних SLI-метрик, нові правила алертів, розподілене трасування вузьких місць.",
            "#fdf6e3", AMBER, "Середня стійкість"),
        (4, "4 · Процедурні вимоги та інструкції (Administrative & Runbooks)",
            "Оновлення регламентів, документації, заклик «бути уважнішим під час деплою», додатковий ручний чеклист.",
            "#fdecea", POS, "Найнижча стійкість (крихкість)"),
    ]

    ty = 64
    for lvl, title_t, desc_t, bg_t, col_t, rank_t in tiers:
        # Рамка рівня
        f.append(rect(40, ty, 880, 92, fill=bg_t, stroke=col_t, sw=1.8, rx=8))
        f.append(text(60, ty + 28, title_t, size=13, color=col_t, anchor="start", bold=True))
        
        # Плашка рейтингу надійності
        f.append(rect(730, ty + 12, 174, 26, fill="#ffffff", stroke=col_t, sw=1.2, rx=4))
        f.append(text(817, ty + 29, rank_t, size=10.5, color=col_t, bold=True))
        
        # Опис та приклад
        f.append(fitbox(60, ty + 40, 840, 42, desc_t, size=11, stroke=GRAY, fill="#ffffff", anchor="start"))
        ty += 104

    # Стрілка ефективності праворуч / знизу
    f.append(rect(40, 484, 880, 24, fill=PANEL, stroke=LINE, sw=1, rx=4))
    f.append(text(W / 2, 500, "▲ ЕФЕКТИВНІСТЬ ЗРОСТАЄ: Від пасивного покладання на пам'ять людини до автоматичних системних гарантій", size=10.5, color=LINE, bold=True))

    render(os.path.join(IMG, "action-items-hierarchy.svg"), W, H, *f)


if __name__ == "__main__":
    fig_swiss_cheese()
    fig_hindsight_bias()
    fig_timeline_phases()
    fig_action_hierarchy()
    print("All figures generated successfully.")
