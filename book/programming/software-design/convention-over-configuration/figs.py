# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми 'convention-over-configuration'."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_explicit_vs_convention():
    w, h = 900, 420
    frags = []

    frags.append(text(w / 2, 28, "Явна конфігурація проти конвенції", size=18, bold=True))
    frags.append(line(440, 48, 440, 395, color="#d1d5db", sw=1.5, dash="4,4"))

    # Ліва колонка: Явна конфігурація
    frags.append(text(220, 58, "Явна реєстрація (XML / ручний мапінг)", size=15, color=NEG, bold=True))
    b1, _, _ = textbox(220, 105, ["Код застосунку", "class Post; class PostsController"], size=12, pad=8, min_w=280)
    b2, _, _ = textbox(220, 205, ["Конфігураційні файли (бойлерплейт)", "<bean id='post' class='Post'>", "<table-mapping entity='Post' table='posts'/>", "<route path='/posts' controller='PostsController'/>"], size=11, pad=8, min_w=340, fill="#fdf3f2", stroke=POS)
    b3, _, _ = textbox(220, 315, ["Виконавче середовище", "Таблиця 'posts' • URL '/posts' • View 'show'"], size=12, pad=8, min_w=280)
    frags.extend([b1, b2, b3])
    frags.append(arrow(220, 130, 220, 168, color=LINE, sw=1.5))
    frags.append(arrow(220, 248, 220, 290, color=LINE, sw=1.5))
    frags.append(text(220, 375, "Будь-яка зміна вимагає правок у 3–4 місцях одночасно", size=11, color=POS, bold=True, italic=True))

    # Права колонка: Конвенція понад конфігурацію
    frags.append(text(670, 58, "Конвенція понад конфігурацію (CoC)", size=15, color=FIELD, bold=True))
    b4, _, _ = textbox(630, 105, ["Код зі стандартними іменами", "class Post; app/routes/posts/[id].ts"], size=12, pad=8, min_w=270)
    b5, _, _ = textbox(630, 205, ["Стандартні правила фреймворку", "Ім'я класу → назва таблиці у множині", "Шлях у каталозі → HTTP-маршрут"], size=11, pad=8, min_w=280, fill="#f0faf4", stroke=FIELD)
    b6, _, _ = textbox(630, 315, ["Виконавче середовище", "Автоматичне зв'язування компонентів"], size=12, pad=8, min_w=270)
    b_ov, _, _ = textbox(820, 205, ["Виняток:", "table_name =", "'legacy_tbl'"], size=10, pad=6, min_w=85, fill="#fff9db", stroke="#e67e22")
    frags.extend([b4, b5, b6, b_ov])
    frags.append(arrow(630, 130, 630, 172, color=LINE, sw=1.5))
    frags.append(arrow(630, 242, 630, 290, color=LINE, sw=1.5))
    frags.append(arrow(770, 205, 740, 205, color="#e67e22", sw=1.2))
    frags.append(text(670, 375, "Конфігурація потрібна лише у разі відхилення від правила", size=11, color=FIELD, bold=True, italic=True))

    render(os.path.join(IMG_DIR, "explicit-vs-convention.svg"), w, h, *frags)


def fig_autoconfig_pipeline():
    w, h = 880, 320
    frags = []

    frags.append(text(w / 2, 28, "Конвеєр перевірки умов автоконфігурації", size=18, bold=True))

    # Крок 1: Запуск
    b1, _, _ = textbox(110, 150, ["1. Старт", "Сканування оточення", "(classpath / файли)"], size=12, pad=8, min_w=150)
    frags.append(b1)
    frags.append(arrow(190, 150, 235, 150, color=LINE, sw=1.5))

    # Крок 2: Перевірка умов
    b2, _, _ = textbox(325, 150, ["2. Умови наявності", "@ConditionalOnClass", "Драйвер / модуль є?"], size=12, pad=8, min_w=170)
    frags.append(b2)

    # Гілка 2: Ні -> Пропуск
    b2_no, _, _ = textbox(325, 65, ["Умова хибна", "Пропуск конфігурації"], size=11, pad=6, min_w=150, fill="#fdf3f2", stroke=POS)
    frags.append(b2_no)
    frags.append(arrow(325, 115, 325, 95, color=POS, sw=1.3))
    frags.append(text(338, 107, "Ні", size=11, color=POS, bold=True))

    frags.append(arrow(415, 150, 460, 150, color=FIELD, sw=1.5))
    frags.append(text(437, 140, "Так", size=11, color=FIELD, bold=True))

    # Крок 3: Перевірка явного біна
    b3, _, _ = textbox(555, 150, ["3. Перевірка явного біна", "@ConditionalOnMissingBean", "Чи створено свій?"], size=12, pad=8, min_w=180)
    frags.append(b3)

    # Гілка 3: Так (є свій) -> Поступитися
    b3_yes, _, _ = textbox(555, 65, ["Бін існує", "Поступитися користувачеві"], size=11, pad=6, min_w=160, fill="#fff9db", stroke="#e67e22")
    frags.append(b3_yes)
    frags.append(arrow(555, 115, 555, 95, color="#e67e22", sw=1.3))
    frags.append(text(570, 107, "Є свій", size=11, color="#e67e22", bold=True))

    frags.append(arrow(650, 150, 695, 150, color=FIELD, sw=1.5))
    frags.append(text(672, 140, "Немає", size=11, color=FIELD, bold=True))

    # Крок 4: Реєстрація дефолту
    b4, _, _ = textbox(780, 150, ["4. Реєстрація", "Створення дефолтного біна", "із типовими параметрами"], size=12, pad=8, min_w=160, fill="#f0faf4", stroke=FIELD)
    frags.append(b4)

    # Підсумок внизу
    frags.append(rect(100, 240, 680, 45, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(440, 268, "Результат: готовий до роботи стек без ручного XML або конфігураційного коду", size=12, color=INK, bold=True))

    render(os.path.join(IMG_DIR, "autoconfig-pipeline.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_explicit_vs_convention()
    fig_autoconfig_pipeline()
    print('All figures generated successfully.')
