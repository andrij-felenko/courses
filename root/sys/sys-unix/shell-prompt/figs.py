# -*- coding: utf-8 -*-
"""Фігури до теми «Запрошення: PS1, PS2 і що в них тримати»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_prompt_hierarchy():
    """Ієрархія змінних запрошення оболонки та контекст їхнього виклику."""
    W, H = 1060, 480
    g = []

    g.append(text(W / 2, 40, "Ієрархія змінних запрошення командної оболонки (PS1–PS4)",
                  size=15, color=INK, bold=True))

    prompts = [
        (40, 75, 230, 340, "PS1", "Первинне запрошення",
         "Дефолт: \\s-\\v\\$ або \\u@\\h:\\w\\$\n\n"
         "• Головний цикл REPL\n"
         "• Відображається перед введенням\n"
         "  нової команди\n"
         "• Підтримує динамічні команди\n"
         "  та коди кольорів",
         "#eaf7ee", FIELD),
        (290, 75, 230, 340, "PS2", "Вторинне продовження",
         "Дефолт: > \n\n"
         "• Незавершені синтаксичні блоки\n"
         "• Непарні лапки (' або \")\n"
         "• Багаторядкові конструкції\n"
         "  (while, if, for, heredoc)\n"
         "• Екранований перенос (\\)",
         FILL, LINE),
        (540, 75, 230, 340, "PS3", "Меню циклу select",
         "Дефолт: #? \n\n"
         "• Інтерактивний вибір варіанта\n"
         "• Використовується вбудованою\n"
         "  конструкцією select ... in\n"
         "• Відображається після списку\n"
         "  нумерованих пунктів",
         "#fff8e6", MUTED),
        (790, 75, 230, 340, "PS4", "Префікс трасування",
         "Дефолт: + \n\n"
         "• Режим налагодження set -x\n"
         "• Друкується перед кожною\n"
         "  виконуваною інструкцією\n"
         "• Перший символ множиться\n"
         "  на глибину вкладеності ($SHLVL)",
         "#fdecea", POS),
    ]

    for x, y, w, h, title, subtitle, desc, fill, stroke in prompts:
        g.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=8))
        g.append(text(x + w / 2, y + 36, title, size=20, color=stroke, bold=True))
        g.append(text(x + w / 2, y + 60, subtitle, size=12, color=MUTED, bold=True))
        g.append(line(x + 16, y + 74, x + w - 16, y + 74, color=stroke, sw=1.0))
        g.append(fitbox(x + 12, y + 86, w - 24, h - 100, desc, size=12, fill=fill, stroke="none", color=INK))

    g.append(text(W / 2, 448,
                  "Кожна змінна активується на окремому етапі життєвого циклу інтерпретатора",
                  size=13, color=MUTED, italic=True))

    return render(os.path.join(IMG, 'prompt-hierarchy.svg'), W, H, *g,
                  title="Ієрархія змінних запрошення оболонки")


def fig_readline_length_calculation():
    """Чому колірні коди без дужок ламають розрахунок позиції курсора в Readline."""
    W, H = 1060, 480
    g = []

    g.append(text(W / 2, 38, "Розрахунок позиції курсора в Readline: з дужками \\[ \\] і без них",
                  size=15, color=INK, bold=True))

    # Секція 1: Без дужок (Помилка)
    g.append(rect(40, 65, 980, 185, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
    g.append(text(60, 92, "1. Без обгортки \\[ \\]: Readline рахує керівні байти як видимі символи",
                  size=13, color=POS, anchor="start", bold=True))

    # Байти в пам'яті
    g.append(text(60, 122, "Рядок у пам'яті:", size=12, color=MUTED, anchor="start"))
    g.append(fitbox(180, 106, 820, 28,
                    "\\033[32m  u  s  e  r  @  h  o  s  t  :  ~  $  \\033[0m  _",
                    size=12, fill="#ffffff", stroke=POS, bold=True))

    g.append(text(60, 162, "Оцінка Readline:", size=12, color=MUTED, anchor="start"))
    g.append(fitbox(180, 146, 380, 30,
                    "Довжина промпту = 26 символів (18 байт ANSI + 13 тексту)",
                    size=11.5, fill="#ffffff", stroke=POS))

    g.append(text(580, 162, "Екран термінала:", size=12, color=MUTED, anchor="start"))
    g.append(fitbox(700, 146, 300, 30,
                    "Фактична ширина = 13 знакомісць",
                    size=11.5, fill="#ffffff", stroke=POS))

    g.append(text(60, 218, "Наслідок: зміщення на 13 знакомісць; курсор перескакує на новий рядок завчасно, історія затирає промпт",
                  size=12, color=POS, anchor="start"))

    # Секція 2: З дужками (Коректно)
    g.append(rect(40, 270, 980, 175, fill="#eaf7ee", stroke=FIELD, sw=1.5, rx=8))
    g.append(text(60, 298, "2. З обгорткою \\[ \\]: керівні байти маркуються як нульова ширина",
                  size=13, color=FIELD, anchor="start", bold=True))

    # Байти в пам'яті
    g.append(text(60, 328, "Рядок у пам'яті:", size=12, color=MUTED, anchor="start"))
    g.append(fitbox(180, 312, 820, 28,
                    "\\[ \\033[32m \\]  u  s  e  r  @  h  o  s  t  :  ~  $  \\[ \\033[0m \\]  _",
                    size=12, fill="#ffffff", stroke=FIELD, bold=True))

    g.append(text(60, 368, "Оцінка Readline:", size=12, color=MUTED, anchor="start"))
    g.append(fitbox(180, 352, 380, 30,
                    "Ігнорує вміст між \\[ і \\] -> Довжина = 13 символів",
                    size=11.5, fill="#ffffff", stroke=FIELD))

    g.append(text(580, 368, "Екран термінала:", size=12, color=MUTED, anchor="start"))
    g.append(fitbox(700, 352, 300, 30,
                    "Фактична ширина = 13 знакомісць",
                    size=11.5, fill="#ffffff", stroke=FIELD))

    g.append(text(60, 422, "Наслідок: ідеальна синхронізація довжини рядка, коректне перенесення та чисте редагування",
                  size=12, color=FIELD, anchor="start"))

    return render(os.path.join(IMG, 'readline-length-calculation.svg'), W, H, *g,
                  title="Розрахунок довжини промпту в Readline")


def fig_prompt_lifecycle():
    """Життєвий цикл формування та рендерингу динамічного промпту."""
    W, H = 1060, 440
    g = []

    g.append(text(W / 2, 38, "Фази обчислення та відображення динамічного промпту в оболонці",
                  size=15, color=INK, bold=True))

    h = 280
    stages = [
        (40, 80, 210, "1. Фіксація стану",
         "Команда завершилась\n\n"
         "• Збереження $?\n"
         "• Збереження $PIPESTATUS\n"
         "• Фіксація часу виконання\n"
         "• Повернення керування tty",
         "#f4f6f8", LINE),
        (295, 80, 210, "2. PROMPT_COMMAND",
         "Виконання хуків\n\n"
         "• Запуск функцій-хуків\n"
         "• Опитування Git/VCS\n"
         "• Збір статусу venv/k8s\n"
         "• Запис проміжних змінних",
         "#fff8e6", MUTED),
        (550, 80, 210, "3. Розкриття PS1",
         "Інтерпретація шаблону\n\n"
         "• Розкриття \\u, \\h, \\w\n"
         "• Виконання $(...)\n"
         "• Підстановка змінних ${...}\n"
         "• Вставка ANSI-кольорів",
         "#eaf7ee", FIELD),
        (805, 80, 210, "4. Readline & TTY",
         "Рендеринг у термінал\n\n"
         "• rl_expand_prompt()\n"
         "• Відкидання \\[ і \\]\n"
         "• Розрахунок знакомісць\n"
         "• Вивід і очікування вводу",
         FILL, LINE),
    ]

    for x, y, w, title, desc, fill, stroke in stages:
        g.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=8))
        g.append(text(x + w / 2, y + 36, title, size=15, color=stroke, bold=True))
        g.append(line(x + 16, y + 54, x + w - 16, y + 54, color=stroke, sw=1.0))
        g.append(fitbox(x + 10, y + 68, w - 20, h - 82, desc, size=12, fill=fill, stroke="none", color=INK))

    g.append(arrow(252, 220, 292, 220))
    g.append(arrow(507, 220, 547, 220))
    g.append(arrow(762, 220, 802, 220))

    g.append(text(W / 2, 400,
                  "Помилка у фазі 2 (незбережений $? або затримка утиліт) ламає весь подальший конвеєр",
                  size=12.5, color=POS, italic=True))

    return render(os.path.join(IMG, 'prompt-lifecycle.svg'), W, H, *g,
                  title="Життєвий цикл формування промпту")


if __name__ == '__main__':
    fig_prompt_hierarchy()
    fig_readline_length_calculation()
    fig_prompt_lifecycle()
    print("Готово. Згенеровано файли у:", IMG)
