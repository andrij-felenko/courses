# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

BLUE_T  = "#eaf0fd"
GREEN_T = "#e7f6ec"
AMBER_T = "#fdf0dd"
RED_T   = "#fdecea"
PURP_T  = "#f3e8ff"
NEUT    = "#eef2f6"

AMBER   = "#e08a1e"
GREEN   = "#2e7d32"
BLUE    = "#1565c0"
RED     = "#c62828"
PURPLE  = "#7b1fa2"
INK     = "#1c2b36"


def fig_reversibility_matrix():
    """Матриця рішення: Ціна відкату vs Невизначеність."""
    W, H = 1020, 460
    f = []

    # Квадранти
    # Top-Left: Висока зворотність / Низька невизначеність
    f.append(fitbox(40, 50, 450, 170,
                    "ДЕЛЕГУВАННЯ ТА ШВИДКИЙ ПУСК (Two-Way Door)\n\n• Висока зворотність, низька невизначеність\n• Дія: Делегувати розробнику, вирішити за 10 хв\n• Приклад: Внутрішня структура модуля, логування",
                    size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Top-Right: Висока зворотність / Висока невизначеність
    f.append(fitbox(530, 50, 450, 170,
                    "TIMEBOXED СПАЙК ТА ПРОТОТИП\n\n• Висока зворотність, висока невизначеність\n• Дія: Купити інформацію спайком на 2 дні\n• Приклад: Перевірка продуктивності бібліотеки",
                    size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))

    # Bottom-Left: Низька зворотність / Низька невизначеність
    f.append(fitbox(40, 240, 450, 170,
                    "СТАНДАРТНЕ ВИКОНАННЯ (Boring Standard)\n\n• Низька зворотність, низька невизначеність\n• Дія: Застосувати перевірений патерн/БД\n• Приклад: Реляційна модель для фінансового леджера",
                    size=12, fill=NEUT, stroke=INK, color=INK))

    # Bottom-Right: Низька зворотність / Висока невизначеність
    f.append(fitbox(530, 240, 450, 170,
                    "УВАГА: ONE-WAY DOOR (Глибокий аналіз)\n\n• Низька зворотність, висока невизначеність\n• Дія: Pre-Mortem сесія, RFC, колегія архітекторів\n• Приклад: Публічний API, формат баз, криптографія",
                    size=12, bold=True, fill=RED_T, stroke=RED, color=RED))

    # Підписи осей
    f.append(fitbox(40, 15, 940, 30, "ВЕРТИКАЛЬ: ЗВОРОТНІСТЬ (Верх = Висока ціна відкату легко уникається | Нижче = Односторонні двері)",
                    size=11, bold=True, fill=NEUT, stroke=INK, color=INK))

    render(os.path.join(OUT, 'reversibility-matrix.svg'), W, H, *f,
           title="Матриця прийняття рішень: Ціна відкату проти Невизначеності")


def fig_boring_tech_spectrum():
    """Бюджет інноваційних жетонів (Boring Technology Credit)."""
    W, H = 1020, 380
    f = []

    # Блок 1: Інноваційні жетони
    f.append(fitbox(40, 40, 290, 220,
                    "БЮДЖЕТ ІННОВАЦІЙ\n(Максимум 2–3 жетони)\n\n• Витрачаються ЛИШЕ на ядро бізнесу\n• Унікальна цінність продукту\n• Приклад: Власний алгоритм розпізнавання відео в DH",
                    size=12, bold=True, fill=BLUE_T, stroke=BLUE, color=BLUE))

    # Блок 2: Нудні технології
    f.append(fitbox(365, 40, 290, 220,
                    "НУДНИЙ СТАНДАРТ\n(0 жетонів, дефолт)\n\n• Зрозумілі відмови й моніторинг\n• Наявність спеціалістів на ринку\n• Приклад: PostgreSQL, Redis, Linux, C++/Go/TS",
                    size=12, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Блок 3: Зона операційного колапсу
    f.append(fitbox(690, 40, 290, 220,
                    "ЗОНА ОПЕРАЦІЙНОГО КОЛАПСУ\n(Перевитрата 5+ жетонів)\n\n• Нова експериментальна БД\n• Нова мова програмування\n• Необкатаний кастомний RPC\n• Свої розробки замість SaaS",
                    size=12, fill=RED_T, stroke=RED, color=RED))

    # Стрілки
    f.append(arrow(330, 150, 365, 150, color=GREEN, sw=2))
    f.append(arrow(655, 150, 690, 150, color=RED, sw=2))

    # Нижній висновок
    f.append(fitbox(40, 290, 940, 60,
                    "Правило: Купуй інновацію там, де робиш гроші; в решті місць використовуй технології із 10-річною історією",
                    size=12, bold=True, fill=NEUT, stroke=INK, color=INK))

    render(os.path.join(OUT, 'boring-tech-spectrum.svg'), W, H, *f,
           title="Бюджет інноваційних жетонів та нудні технології")


def fig_premortem_flow():
    """Алгоритм проведення сесії Pre-Mortem."""
    W, H = 1020, 380
    f = []

    # Крок 1
    f.append(fitbox(20, 60, 180, 140,
                    "1. ГІПОТЕЗА\n\nФормулювання One-Way Door рішення",
                    size=12, bold=True, fill=BLUE_T, stroke=BLUE, color=BLUE))

    # Крок 2
    f.append(fitbox(220, 60, 180, 140,
                    "2. КАТАСТРОФА\n\n«Уявімо, що минув 1 рік і система впала»",
                    size=12, bold=True, fill=RED_T, stroke=RED, color=RED))

    # Крок 3
    f.append(fitbox(420, 60, 180, 140,
                    "3. СПИСОК ПРИЧИН\n\nМовчазне виписування прихованих ризиків",
                    size=12, fill=AMBER_T, stroke=AMBER, color=AMBER))

    # Крок 4
    f.append(fitbox(620, 60, 180, 140,
                    "4. РАНЖУВАННЯ\n\nМатриця ймовірності та важкості відмови",
                    size=12, fill=PURP_T, stroke=PURPLE, color=PURPLE))

    # Крок 5
    f.append(fitbox(820, 60, 180, 140,
                    "5. ЗМІНА ДИЗАЙНУ\n\nПеретворення у Two-Way Door або захист",
                    size=12, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Стрілки зв'язку
    f.append(arrow(200, 130, 220, 130, color=INK, sw=2))
    f.append(arrow(400, 130, 420, 130, color=INK, sw=2))
    f.append(arrow(600, 130, 620, 130, color=INK, sw=2))
    f.append(arrow(800, 130, 820, 130, color=INK, sw=2))

    # Нижній пояснювальний блок
    f.append(fitbox(20, 240, 980, 80,
                    "Результат сесії: Виявлення прихованих загрожень до інвестування ресурсів та заміна засліплення авторитетом на факт-базований аналіз",
                    size=12, bold=True, fill=NEUT, stroke=INK, color=INK))

    render(os.path.join(OUT, 'premortem-flow.svg'), W, H, *f,
           title="Алгоритм проведення сесії Pre-Mortem")


def fig_decision_compass():
    """Компас щоденних рішень архітектора."""
    W, H = 1020, 440
    f = []

    # Центральний вузол
    f.append(fitbox(370, 170, 280, 100,
                    "КОМПАС РІШЕНЬ\n\nШвидка триада дій архітектора\nу ситуації невизначеності",
                    size=13, bold=True, fill=AMBER_T, stroke=AMBER, color=AMBER))

    # 5 Променів евристик
    # 1. One-way vs Two-way
    f.append(fitbox(40, 40, 280, 100,
                    "1. ЗВОРОТНІСТЬ (Reversibility)\n\nОдносторонні двері? → Уповільнись.\nДвосторонні? → Делегуй негайно.",
                    size=11, fill=BLUE_T, stroke=BLUE, color=BLUE))
    f.append(arrow(320, 90, 410, 170, color=BLUE, sw=2))

    # 2. YAGNI
    f.append(fitbox(700, 40, 280, 100,
                    "2. YAGNI (Default to NO)\n\nЧи потрібна ця складність зараз?\nНі → Не будуй, збережи простір.",
                    size=11, fill=GREEN_T, stroke=GREEN, color=GREEN))
    f.append(arrow(700, 90, 610, 170, color=GREEN, sw=2))

    # 3. Boring Tech
    f.append(fitbox(40, 300, 280, 100,
                    "3. НУДНА ТЕХНОЛОГІЯ\n\nЄ вільний інноваційний жетон?\nНі → Бери PostgreSQL / C++ / Go.",
                    size=11, fill=PURP_T, stroke=PURPLE, color=PURPLE))
    f.append(arrow(320, 350, 410, 270, color=PURPLE, sw=2))

    # 4. Pre-Mortem
    f.append(fitbox(700, 300, 280, 100,
                    "4. PRE-MORTEM AUDIT\n\nЩО зламає цю систему через рік?\nПроведи 30-хв сесію до коду.",
                    size=11, fill=RED_T, stroke=RED, color=RED))
    f.append(arrow(700, 350, 610, 270, color=RED, sw=2))

    # 5. Measure First
    f.append(fitbox(370, 20, 280, 75,
                    "5. MEASURE FIRST\n\nЄ виміряні метрики? Ні → Не оптимізуй.",
                    size=11, bold=True, fill=NEUT, stroke=INK, color=INK))
    f.append(arrow(510, 95, 510, 170, color=INK, sw=2))

    render(os.path.join(OUT, 'decision-compass.svg'), W, H, *f,
           title="П'ять правил компасу щоденних рішень архітектора")


if __name__ == "__main__":
    fig_reversibility_matrix()
    fig_boring_tech_spectrum()
    fig_premortem_flow()
    fig_decision_compass()
    print("Decision heuristics figures generated successfully.")
