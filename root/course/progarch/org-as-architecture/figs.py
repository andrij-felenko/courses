# -*- coding: utf-8 -*-
"""Фігури до теми «Організація як архітектура».
Запуск: python figs.py  → створює SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ───────── Фіг. 1: Соціотехнічний ізоморфізм ─────────
def fig_sociotechnical_isomorphism():
    W, H = 920, 450
    f = [text(W / 2, 28, "Соціотехнічний ізоморфізм: граф комунікацій та граф архітектурних залежностей", size=16, bold=True)]

    # Ліва панель: Соціотехнічний розрив (Mismatch)
    box_w, box_h = 420, 390
    lx, ly = 30, 45

    f.append(rect(lx, ly, box_w, box_h, fill="#fdf2f2", stroke="#e74c3c", sw=1.5, rx=8))
    f.append(text(lx + box_w / 2, ly + 25, "Соціотехнічний розрив (Mismatch)", size=14, bold=True, color="#c0392b"))
    f.append(text(lx + box_w / 2, ly + 42, "Функціональні колодязі vs Мікросервіси", size=11, color=MUTED, italic=True))

    # Команди (зліва)
    f.append(rect(lx + 20, ly + 60, 110, 45, fill="#ffffff", stroke="#c0392b", sw=1.2, rx=4))
    f.append(text(lx + 75, ly + 78, "Команда UI", size=11, bold=True, color=INK))
    f.append(text(lx + 75, ly + 93, "(Frontend)", size=9.5, color=MUTED))

    f.append(rect(lx + 20, ly + 120, 110, 45, fill="#ffffff", stroke="#c0392b", sw=1.2, rx=4))
    f.append(text(lx + 75, ly + 138, "Команда Backend", size=11, bold=True, color=INK))
    f.append(text(lx + 75, ly + 153, "(Core API)", size=9.5, color=MUTED))

    f.append(rect(lx + 20, ly + 180, 110, 45, fill="#ffffff", stroke="#c0392b", sw=1.2, rx=4))
    f.append(text(lx + 75, ly + 198, "Команда DBA", size=11, bold=True, color=INK))
    f.append(text(lx + 75, ly + 213, "(БД і схеми)", size=9.5, color=MUTED))

    # Лінії міжкомандного тертя (зліва)
    f.append(line(lx + 75, ly + 105, lx + 75, ly + 120, color="#c0392b", sw=1.5, dash="3,3"))
    f.append(line(lx + 75, ly + 165, lx + 75, ly + 180, color="#c0392b", sw=1.5, dash="3,3"))

    # Сервіси (справа від команд у лівому боксі)
    f.append(rect(lx + 260, ly + 60, 135, 45, fill="#ffffff", stroke="#2980b9", sw=1.2, rx=4))
    f.append(text(lx + 327, ly + 78, "Сервіс твіна", size=11, bold=True, color=INK))
    f.append(text(lx + 327, ly + 93, "(Digital Twin)", size=9.5, color=MUTED))

    f.append(rect(lx + 260, ly + 120, 135, 45, fill="#ffffff", stroke="#2980b9", sw=1.2, rx=4))
    f.append(text(lx + 327, ly + 138, "Сервіс автоматизацій", size=11, bold=True, color=INK))
    f.append(text(lx + 327, ly + 153, "(Rule Engine)", size=9.5, color=MUTED))

    f.append(rect(lx + 260, ly + 180, 135, 45, fill="#ffffff", stroke="#2980b9", sw=1.2, rx=4))
    f.append(text(lx + 327, ly + 198, "Сервіс білінгу", size=11, bold=True, color=INK))
    f.append(text(lx + 327, ly + 213, "(Payments)", size=9.5, color=MUTED))

    # Перехресні ручні тикети (хаос володіння)
    f.append(arrow(lx + 130, ly + 82, lx + 260, ly + 82, color="#c0392b", sw=1.2))
    f.append(arrow(lx + 130, ly + 82, lx + 260, ly + 142, color="#c0392b", sw=1.2))
    f.append(arrow(lx + 130, ly + 142, lx + 260, ly + 82, color="#c0392b", sw=1.2))
    f.append(arrow(lx + 130, ly + 142, lx + 260, ly + 202, color="#c0392b", sw=1.2))
    f.append(arrow(lx + 130, ly + 202, lx + 260, ly + 202, color="#c0392b", sw=1.2))

    # Опис проблеми у нижньому затіненому блоці
    f.append(rect(lx + 15, ly + 240, box_w - 30, 135, fill="#ffffff", stroke="#e74c3c", sw=1.0, rx=4))
    f.append(text(lx + 25, ly + 258, "Наслідки розриву:", size=11, bold=True, color="#c0392b", anchor="start"))
    f.append(text(lx + 25, ly + 278, "• 1 фіча вимагає synchronized PR у 3 командах", size=10, color=INK, anchor="start"))
    f.append(text(lx + 25, ly + 296, "• Неперервні міжкомандні затримки й черги Jira", size=10, color=INK, anchor="start"))
    f.append(text(lx + 25, ly + 314, "• Сервіси деградують у розподілений моноліт", size=10, color=INK, anchor="start"))
    f.append(text(lx + 25, ly + 332, "• Низька автономність та вигорання інженерів", size=10, color=INK, anchor="start"))
    f.append(text(lx + 25, ly + 350, "• Висока частота міжсервісних дефектів", size=10, color="#c0392b", bold=True, anchor="start"))

    # Права панель: Соціотехнічна гармонізація (Alignment)
    rx = 470
    f.append(rect(rx, ly, box_w, box_h, fill="#f2f9f5", stroke="#27ae60", sw=1.5, rx=8))
    f.append(text(rx + box_w / 2, ly + 25, "Соціотехнічна гармонізація (Alignment)", size=14, bold=True, color="#1e8449"))
    f.append(text(rx + box_w / 2, ly + 42, "Stream-Aligned команди & Гармонійні сервіси", size=11, color=MUTED, italic=True))

    # Автономний домен 1 (Твін)
    f.append(rect(rx + 20, ly + 60, box_w - 40, 55, fill="#ffffff", stroke="#27ae60", sw=1.2, rx=6))
    f.append(rect(rx + 30, ly + 70, 160, 35, fill="#e8f8f5", stroke="#16a085", sw=1.0, rx=4))
    f.append(text(rx + 110, ly + 83, "Команда домену Твіна", size=10, bold=True, color=INK))
    f.append(text(rx + 110, ly + 97, "(Stream-Aligned)", size=9, color=MUTED))
    f.append(arrow(rx + 190, ly + 87, rx + 225, ly + 87, color="#16a085", sw=1.5))
    f.append(rect(rx + 225, ly + 70, 145, 35, fill="#d4efdf", stroke="#27ae60", sw=1.0, rx=4))
    f.append(text(rx + 297, ly + 83, "Сервіс Твіна & DB", size=10, bold=True, color=INK))
    f.append(text(rx + 297, ly + 97, "(Повне володіння)", size=9, color=MUTED))

    # Автономний домен 2 (Автоматизації)
    f.append(rect(rx + 20, ly + 120, box_w - 40, 55, fill="#ffffff", stroke="#27ae60", sw=1.2, rx=6))
    f.append(rect(rx + 30, ly + 130, 160, 35, fill="#e8f8f5", stroke="#16a085", sw=1.0, rx=4))
    f.append(text(rx + 110, ly + 143, "Команда автоматизацій", size=10, bold=True, color=INK))
    f.append(text(rx + 110, ly + 157, "(Stream-Aligned)", size=9, color=MUTED))
    f.append(arrow(rx + 190, ly + 147, rx + 225, ly + 147, color="#16a085", sw=1.5))
    f.append(rect(rx + 225, ly + 130, 145, 35, fill="#d4efdf", stroke="#27ae60", sw=1.0, rx=4))
    f.append(text(rx + 297, ly + 143, "Сервіс правил & DB", size=10, bold=True, color=INK))
    f.append(text(rx + 297, ly + 157, "(Повне володіння)", size=9, color=MUTED))

    # Платформена команда (Self-Service)
    f.append(rect(rx + 20, ly + 180, box_w - 40, 50, fill="#eaedf1", stroke="#2c3e50", sw=1.2, rx=6))
    f.append(text(rx + box_w / 2, ly + 198, "Платформена команда (Platform Team)", size=11, bold=True, color="#2c3e50"))
    f.append(text(rx + box_w / 2, ly + 214, "Внутрішня платформа як продукт (IDP Self-Service APIs)", size=9.5, color=MUTED))

    # Стрілки споживання платформи
    f.append(arrow(rx + 110, ly + 180, rx + 110, ly + 175, color="#2c3e50", sw=1.2))
    f.append(arrow(rx + 297, ly + 180, rx + 297, ly + 175, color="#2c3e50", sw=1.2))

    # Опис переваг
    f.append(rect(rx + 15, ly + 240, box_w - 30, 135, fill="#ffffff", stroke="#27ae60", sw=1.0, rx=4))
    f.append(text(rx + 25, ly + 258, "Результат гармонізації:", size=11, bold=True, color="#1e8449", anchor="start"))
    f.append(text(rx + 25, ly + 278, "• 1 команда випускає фічу без міжкомандних черг", size=10, color=INK, anchor="start"))
    f.append(text(rx + 25, ly + 296, "• Межі коду збігаються з межами контексту спілкування", size=10, color=INK, anchor="start"))
    f.append(text(rx + 25, ly + 314, "• Чітко визначені API-контракти замість ручних квитків", size=10, color=INK, anchor="start"))
    f.append(text(rx + 25, ly + 332, "• Платформа надає інфраструктуру як сервіс (Paved Road)", size=10, color=INK, anchor="start"))
    f.append(text(rx + 25, ly + 350, "• Максимальна автономність та Lead Time < 1 день", size=10, color="#1e8449", bold=True, anchor="start"))

    render(os.path.join(IMG, "sociotechnical-isomorphism.svg"), W, H, *f)


# ───────── Фіг. 2: П'ятикроковий пайплайн зворотного маневру Конвея ─────────
def fig_inverse_conway_pipeline():
    W, H = 900, 390
    f = [text(W / 2, 28, "П'ятикроковий пайплайн зворотного маневру Конвея (Inverse Conway Maneuver)", size=16, bold=True)]

    step_w = 155
    step_h = 220
    gap = 20
    start_x = 25
    start_y = 60

    steps = [
        {
            "num": "Крок 1",
            "title": "Доменні контексти",
            "sub": "DDD & Subdomains",
            "bg": "#ebf5fb",
            "border": "#2980b9",
            "bullets": ["Аналіз домену", "Визначення Contexts", "Модель сутностей", "Виділення ядра"]
        },
        {
            "num": "Крок 2",
            "title": "Когнітивні межі",
            "sub": "Cognitive Load",
            "bg": "#fef9e7",
            "border": "#f39c12",
            "bullets": ["Оцінка навантаження", "Межі Sweller/Dunbar", "Видалення зайвого", "Фокус на домені"]
        },
        {
            "num": "Крок 3",
            "title": "Топологія команд",
            "sub": "Team Topologies",
            "bg": "#e8f8f5",
            "border": "#16a085",
            "bullets": ["Stream-Aligned", "Platform teams", "Enabling teams", "Режими взаємодії"]
        },
        {
            "num": "Крок 4",
            "title": "Арх. межі",
            "sub": "Module & API Gates",
            "bg": "#f4ecf7",
            "border": "#8e44ad",
            "bullets": ["Автономні сервіси", "Жорсткі API контракти", "Ізольовані БД", "Event-driven зв'язок"]
        },
        {
            "num": "Крок 5",
            "title": "Платформа IDP",
            "sub": "Self-Service Road",
            "bg": "#eaedf1",
            "border": "#2c3e50",
            "bullets": ["Self-Service API", "CI/CD шаблони", "Мережа & безпека", "Автоматичний SLO"]
        }
    ]

    for i, st in enumerate(steps):
        x = start_x + i * (step_w + gap)
        y = start_y

        f.append(rect(x, y, step_w, step_h, fill=st["bg"], stroke=st["border"], sw=1.5, rx=6))
        f.append(rect(x, y, step_w, 30, fill=st["border"], stroke="none", rx=6))
        f.append(text(x + step_w / 2, y + 19, st["num"], size=12, bold=True, color="#ffffff"))

        f.append(text(x + step_w / 2, y + 48, st["title"], size=11, bold=True, color=INK))
        f.append(text(x + step_w / 2, y + 63, st["sub"], size=9.5, color=MUTED, italic=True))
        f.append(line(x + 10, y + 72, x + step_w - 10, y + 72, color=st["border"], sw=0.8, dash="2,2"))

        for j, bullet in enumerate(st["bullets"]):
            by = y + 92 + j * 28
            f.append(text(x + 10, by, "• " + bullet, size=9.5, color=INK, anchor="start"))

        if i < len(steps) - 1:
            ax = x + step_w
            ay = y + step_h / 2
            f.append(arrow(ax + 2, ay, ax + gap - 2, ay, color=INK, sw=1.8))

    # Нижній висновок
    f.append(rect(start_x, start_y + step_h + 15, W - 2 * start_x, 55, fill="#f8f9fa", stroke="#bdc3c7", sw=1.0, rx=4))
    f.append(text(W / 2, start_y + step_h + 36, "Головний принцип маневру: Організаційна структура передує архітектурній системі.", size=12, bold=True, color=INK))
    f.append(text(W / 2, start_y + step_h + 53, "Спершу будуємо автономні соціотехнічні межі, пізніше — закріплюємо їх у коді й контрактах сервісів.", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, "inverse-conway-pipeline.svg"), W, H, *f)


# ───────── Фіг. 3: Матриця соціотехнічних відповідностей та компромісів ─────────
def fig_sociotechnical_conway_matrix():
    W, H = 940, 440
    f = [text(W / 2, 28, "Матриця відповідності організаційної структури та архітектури систем", size=16, bold=True)]

    col_w = 260
    row_h = 100
    start_x = 130
    start_y = 80

    headers_x = ["Моноліт коду", "Мікросервіси", "Модульний моноліт / IDP"]
    headers_y = [
        ["Функціональні", "колодязі"],
        ["Компонентні", "команди"],
        ["Stream-Aligned", "команди"]
    ]

    # Колонки заголовків
    for j, hx in enumerate(headers_x):
        x = start_x + j * col_w
        f.append(rect(x, start_y - 30, col_w, 30, fill="#2c3e50", stroke="#ffffff", sw=1.0))
        f.append(text(x + col_w / 2, start_y - 10, hx, size=11, bold=True, color="#ffffff"))

    # Рядки заголовків
    for i, hy_lines in enumerate(headers_y):
        y = start_y + i * row_h
        f.append(rect(start_x - 120, y, 120, row_h, fill="#34495e", stroke="#ffffff", sw=1.0))
        f.append(text(start_x - 60, y + row_h / 2 - 8, hy_lines[0], size=10, bold=True, color="#ffffff"))
        f.append(text(start_x - 60, y + row_h / 2 + 10, hy_lines[1], size=10, bold=True, color="#ffffff"))

    matrix_data = [
        # Рядок 0: Функціональні колодязі
        [
            {"title": "Класичний моноліт", "badge": "Високе тертя", "color": "#e74c3c", "bg": "#fdf2f2", "desc": ["Затримки в чергах DBA/QA.", "Повільний Lead Time.", "Зрозуміла локальна якість."]},
            {"title": "Розподілений моноліт", "badge": "Катастрофа", "color": "#c0392b", "bg": "#f9ebea", "desc": ["Найгірша комбінація.", "Синхронні каскади PR.", "Міжкомандне вигорання."]},
            {"title": "Передчасна платформа", "badge": "Неефективно", "color": "#d35400", "bg": "#fef5e7", "desc": ["Бюрократична платформа.", "Платформа як колодязь.", "Високий overhead."]}
        ],
        # Рядок 1: Компонентні команди
        [
            {"title": "Компонентний моноліт", "badge": "Середне тертя", "color": "#d35400", "bg": "#fef5e7", "desc": ["Бійка за єдиний репозиторій.", "Конфлікти злиття (Merge).", "Блокування релізів."]},
            {"title": "Сервісні колодязі", "badge": "Високий overhead", "color": "#e67e22", "bg": "#fdfefe", "desc": ["Низький потік цінності.", "Вузькі місця у господарях.", "Втрата контексту."]},
            {"title": "InnerSource модель", "badge": "Прийнятно", "color": "#27ae60", "bg": "#eafaf1", "desc": ["Гнучкі Pull Requests.", "Хранителі компонентів.", "Потрібна культура."]}
        ],
        # Рядок 2: Stream-Aligned команди
        [
            {"title": "Модульний моноліт", "badge": "Чудовий старт", "color": "#27ae60", "bg": "#eafaf1", "desc": ["Високий потік цінності.", "Чіткі межі модулів у коді.", "Легкий деплойment."]},
            {"title": "Автономні сервіси", "badge": "Ідеальний масштаб", "color": "#1e8449", "bg": "#d4efdf", "desc": ["Повна автономність.", "Low Lead Time (<1d).", "Self-service платформа."]},
            {"title": "Соціотехнічний оптимум", "badge": "Золотий стандарт", "color": "#196f3d", "bg": "#d5f5e3", "desc": ["Гармонія коду й людей.", "Низьке навантаження.", "Максимальна еволюційність."]}
        ]
    ]

    for i in range(3):
        for j in range(3):
            cell = matrix_data[i][j]
            x = start_x + j * col_w
            y = start_y + i * row_h

            f.append(rect(x, y, col_w, row_h, fill=cell["bg"], stroke=cell["color"], sw=1.2))

            # Title & Badge
            f.append(text(x + 10, y + 20, cell["title"], size=11, bold=True, color=INK, anchor="start"))
            f.append(rect(x + col_w - 105, y + 6, 95, 18, fill=cell["color"], stroke="none", rx=3))
            f.append(text(x + col_w - 57, y + 18, cell["badge"], size=9, bold=True, color="#ffffff"))

            # Desc lines
            for idx, line_str in enumerate(cell["desc"]):
                f.append(text(x + 10, y + 42 + idx * 16, "• " + line_str, size=9.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "sociotechnical-conway-matrix.svg"), W, H, *f)


if __name__ == "__main__":
    fig_sociotechnical_isomorphism()
    fig_inverse_conway_pipeline()
    fig_sociotechnical_conway_matrix()
    print("Всі фігури успішно згенеровано у ./img/")
