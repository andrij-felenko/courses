# -*- coding: utf-8 -*-
"""Фігури до теми «GraphQL».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"
GRAY  = "#9aa0a6"
PURPLE = "#8e44ad"
BLUE_BG = "#eef2fb"
GREEN_BG = "#eafaf1"
AMBER_BG = "#fef9e7"
RED_BG = "#fdf2e9"


# ── 1. REST надлишкове/недостатнє завантаження проти точного дерева GraphQL ───
def fig_rest_vs_graphql():
    W, H = 880, 420
    f = [text(W / 2, 28, "Порівняння отримання даних: каскад REST проти одного запиту GraphQL", size=15, bold=True)]

    # Ліва колонка — REST
    f.append(rect(30, 52, 395, 345, fill="#fdfdfd", stroke=LINE, sw=1.2, rx=8))
    f.append(text(227, 76, "REST: три послідовні виклики та зайві поля", size=12.5, color=POS, bold=True))

    # REST Запит 1
    f.append(rect(45, 96, 365, 75, fill=RED_BG, stroke=POS, sw=1.2, rx=6))
    f.append(text(55, 114, "1. GET /users/42", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(55, 132, "Потрібно: name", size=10.5, color=MUTED, anchor="start"))
    f.append(text(55, 150, "Отримано: { id, name, email, address, phone, regDate, ... } (28 полів!)", size=10, color=INK, anchor="start"))

    # REST Запит 2
    f.append(rect(45, 180, 365, 75, fill=RED_BG, stroke=POS, sw=1.2, rx=6))
    f.append(text(55, 198, "2. GET /users/42/posts", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(55, 216, "Потрібно: id, title", size=10.5, color=MUTED, anchor="start"))
    f.append(text(55, 234, "Отримано: [{ id, title, body, slug, tags, views, ... }, ...] (надлишок)", size=10, color=INK, anchor="start"))

    # REST Запит 3
    f.append(rect(45, 264, 365, 75, fill=RED_BG, stroke=POS, sw=1.2, rx=6))
    f.append(text(55, 282, "3. GET /posts/101/commentsCount", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(55, 300, "Потрібно: кількість коментарів", size=10.5, color=MUTED, anchor="start"))
    f.append(text(55, 318, "Немає окремого лічильника: качаємо всі коментарі (under-fetching)", size=10, color=INK, anchor="start"))

    f.append(text(227, 365, "Підсумок: 3 мережеві затримки (RTT) + 85% зайвого трафіку", size=10.5, color=POS, bold=True))

    # Права колонка — GraphQL
    f.append(rect(455, 52, 395, 345, fill="#fdfdfd", stroke=LINE, sw=1.2, rx=8))
    f.append(text(652, 76, "GraphQL: єдиний запит за точною структурою", size=12.5, color=FIELD, bold=True))

    # GraphQL Запит
    f.append(rect(470, 96, 180, 243, fill=GREEN_BG, stroke=FIELD, sw=1.2, rx=6))
    f.append(text(480, 116, "POST /graphql (Запит)", size=10.5, color=FIELD, bold=True, anchor="start"))
    query_lines = [
        "query {",
        "  user(id: 42) {",
        "    name",
        "    posts {",
        "      title",
        "      commentsCount",
        "    }",
        "  }",
        "}"
    ]
    for i, ln in enumerate(query_lines):
        f.append(text(480, 138 + i * 18, ln, size=10, color=INK, anchor="start"))

    # Стрілка посередині
    f.append(arrow(656, 217, 678, 217, color=LINE, sw=1.8))

    # GraphQL Відповідь
    f.append(rect(685, 96, 150, 243, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(695, 116, "JSON (Відповідь)", size=10.5, color=FIELD, bold=True, anchor="start"))
    resp_lines = [
        "{",
        '  "data": {',
        '    "user": {',
        '      "name": "Олена",',
        '      "posts": [',
        '        { "title": "...",',
        '          "commentsCount": 4',
        "        }",
        "      ]",
        "    }",
        "  }",
        "}"
    ]
    for i, ln in enumerate(resp_lines):
        f.append(text(695, 136 + i * 16, ln, size=9.5, color=INK, anchor="start"))

    f.append(text(652, 365, "Підсумок: 1 RTT, 0 зайвих байтів, точна форма для UI", size=10.5, color=FIELD, bold=True))

    render(os.path.join(IMG, "rest-overfetching-vs-graphql.svg"), W, H, *f)


# ── 2. Конвеєр обробки та дерево виконання запиту (AST & Resolvers) ───────────
def fig_execution_pipeline():
    W, H = 880, 390
    f = [text(W / 2, 28, "Конвеєр обробки GraphQL-запиту: від тексту до резолверного дерева", size=15, bold=True)]

    # 4 стадії вгорі
    stages = [
        ("1. Парсинг (Lex & Parse)", "Текст запиту -> AST", 40, 180, NEG),
        ("2. Валідація (Validate)", "Звірка AST зі схемою SDL", 250, 180, AMBER),
        ("3. Виконання (Execute)", "Обхід резолверів зверху вниз", 460, 180, PURPLE),
        ("4. Формування JSON", "{ data, errors }", 670, 170, FIELD),
    ]

    for title, desc, x, w, col in stages:
        f.append(rect(x, 52, w, 58, fill="#fafafa", stroke=col, sw=1.5, rx=6))
        f.append(text(x + w / 2, 74, title, size=11, color=col, bold=True))
        f.append(text(x + w / 2, 94, desc, size=9.5, color=MUTED))

    f.append(arrow(222, 81, 248, 81, color=GRAY, sw=1.5))
    f.append(arrow(432, 81, 458, 81, color=GRAY, sw=1.5))
    f.append(arrow(642, 81, 668, 81, color=GRAY, sw=1.5))

    # Дерево резолверів унизу
    f.append(rect(40, 130, 800, 235, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))
    f.append(text(440, 152, "Дерево виконання резолверів: (source, args, context, info)", size=12, color=PURPLE, bold=True))

    # Рівень 0: Root Query
    f.append(rect(360, 168, 160, 38, fill=BLUE_BG, stroke=NEG, sw=1.3, rx=6))
    f.append(text(440, 191, "Query.user(id: 42)", size=11, color=NEG, bold=True))

    # Рівень 1: Поля об'єкта User (виконуються паралельно)
    f.append(line(440, 206, 260, 234, color=GRAY, sw=1.3))
    f.append(line(440, 206, 620, 234, color=GRAY, sw=1.3))

    f.append(rect(180, 234, 160, 38, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(260, 252, "User.name", size=11, color=INK, bold=True))
    f.append(text(260, 266, "Скаляр: пряме читання з parent", size=9, color=MUTED))

    f.append(rect(540, 234, 160, 38, fill=BLUE_BG, stroke=NEG, sw=1.3, rx=6))
    f.append(text(620, 252, "User.posts", size=11, color=NEG, bold=True))
    f.append(text(620, 266, "Об'єктний список: запит до БД", size=9, color=MUTED))

    # Рівень 2: Елементи масиву Post
    f.append(line(620, 272, 510, 302, color=GRAY, sw=1.3))
    f.append(line(620, 272, 730, 302, color=GRAY, sw=1.3))

    f.append(rect(430, 302, 160, 38, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(510, 320, "Post.title", size=11, color=INK, bold=True))
    f.append(text(510, 334, "Скалярний листок дерева", size=9, color=MUTED))

    f.append(rect(650, 302, 160, 38, fill=GREEN_BG, stroke=FIELD, sw=1.3, rx=6))
    f.append(text(730, 320, "Post.commentsCount", size=11, color=FIELD, bold=True))
    f.append(text(730, 334, "Обчислюваний резолвер (COUNT)", size=9, color=MUTED))

    render(os.path.join(IMG, "graphql-execution-ast-tree.svg"), W, H, *f)


# ── 3. Проблема N+1 та коалесценція через DataLoader ──────────────────────────
def fig_dataloader():
    W, H = 880, 390
    f = [text(W / 2, 28, "Проблема N+1 у резолверах і оптимізація через DataLoader", size=15, bold=True)]

    # Ліва частина — Наївні резолвери (N+1 запитів)
    f.append(rect(30, 52, 395, 315, fill="#fdfdfd", stroke=LINE, sw=1.2, rx=8))
    f.append(text(227, 76, "Наївний підхід: N+1 окремих запитів", size=12.5, color=POS, bold=True))

    f.append(rect(45, 95, 365, 36, fill=BLUE_BG, stroke=NEG, sw=1.2, rx=6))
    f.append(text(227, 118, "1 запит: SELECT * FROM posts LIMIT 10", size=10.5, color=NEG, bold=True))

    f.append(text(227, 146, "Далі для кожного з 10 постів викликається Post.author:", size=10, color=MUTED, italic=True))

    y_start = 160
    for i in range(4):
        f.append(rect(45, y_start + i * 32, 365, 26, fill=RED_BG, stroke=POS, sw=1.1, rx=4))
        f.append(text(227, y_start + i * 32 + 18, f"Запит #{i+2}: SELECT * FROM users WHERE id = {10+i}", size=9.5, color=POS))

    f.append(text(227, y_start + 4 * 32 + 10, "... ще 6 окремих SQL-запитів ...", size=10, color=MUTED))

    f.append(rect(45, 315, 365, 40, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
    f.append(text(227, 338, "Разом: 1 + 10 = 11 запитів до БД (водоспад I/O)", size=11, color=POS, bold=True))

    # Права частина — DataLoader (2 батч-запити)
    f.append(rect(455, 52, 395, 315, fill="#fdfdfd", stroke=LINE, sw=1.2, rx=8))
    f.append(text(652, 76, "З DataLoader: збирання ключів і батчинг", size=12.5, color=FIELD, bold=True))

    f.append(rect(470, 95, 365, 36, fill=BLUE_BG, stroke=NEG, sw=1.2, rx=6))
    f.append(text(652, 118, "1 запит: SELECT * FROM posts LIMIT 10", size=10.5, color=NEG, bold=True))

    f.append(rect(470, 145, 365, 80, fill=AMBER_BG, stroke=AMBER, sw=1.2, rx=6))
    f.append(text(652, 165, "DataLoader (черга у мікротасці Event Loop):", size=10.5, color=AMBER, bold=True))
    f.append(text(652, 185, "loader.load(10), loader.load(11), loader.load(12)...", size=10, color=INK))
    f.append(text(652, 205, "-> Об'єднання ключів у множину: { 10, 11, 12, ... }", size=10, color=MUTED))

    f.append(rect(470, 240, 365, 58, fill=GREEN_BG, stroke=FIELD, sw=1.2, rx=6))
    f.append(text(652, 260, "2 батч-запит до бази даних:", size=10.5, color=FIELD, bold=True))
    f.append(text(652, 282, "SELECT * FROM users WHERE id IN (10, 11, 12, ...)", size=10, color=INK, bold=True))

    f.append(rect(470, 315, 365, 40, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(652, 338, "Разом: рівно 2 запити до БД + кеш у межах запиту", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "n-plus-one-dataloader.svg"), W, H, *f)


# ── 4. Граф типізованої схеми (SDL Type System Graph) ─────────────────────────
def fig_schema_graph():
    W, H = 880, 390
    f = [text(W / 2, 28, "Типізована схема GraphQL: граф сутностей, інтерфейсів і скалярів", size=15, bold=True)]

    # Root Query
    f.append(rect(40, 160, 140, 70, fill=PURPLE, stroke=LINE, sw=1.5, rx=8))
    f.append(text(110, 188, "Query", size=13, color="#ffffff", bold=True))
    f.append(text(110, 208, "user(id: ID!): User\nfeed: [Post!]!", size=9.5, color="#ffffff"))

    # Interface Node
    f.append(rect(230, 48, 160, 56, fill="#f0f3f6", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(310, 68, "interface Node", size=11, color=MUTED, bold=True, italic=True))
    f.append(text(310, 88, "id: ID!", size=10, color=INK))

    # Type User
    f.append(rect(230, 135, 170, 125, fill=BLUE_BG, stroke=NEG, sw=1.5, rx=8))
    f.append(text(315, 158, "type User implements Node", size=10.5, color=NEG, bold=True))
    f.append(text(245, 180, "id: ID!", size=10, color=INK, anchor="start"))
    f.append(text(245, 198, "name: String!", size=10, color=INK, anchor="start"))
    f.append(text(245, 216, "email: String", size=10, color=INK, anchor="start"))
    f.append(text(245, 234, "posts: [Post!]!", size=10, color=FIELD, bold=True, anchor="start"))

    # Type Post
    f.append(rect(470, 135, 170, 125, fill=BLUE_BG, stroke=NEG, sw=1.5, rx=8))
    f.append(text(555, 158, "type Post implements Node", size=10.5, color=NEG, bold=True))
    f.append(text(485, 180, "id: ID!", size=10, color=INK, anchor="start"))
    f.append(text(485, 198, "title: String!", size=10, color=INK, anchor="start"))
    f.append(text(485, 216, "author: User!", size=10, color=FIELD, bold=True, anchor="start"))
    f.append(text(485, 234, "comments: [Comment!]!", size=10, color=FIELD, bold=True, anchor="start"))

    # Type Comment
    f.append(rect(700, 150, 150, 95, fill=BLUE_BG, stroke=NEG, sw=1.5, rx=8))
    f.append(text(775, 172, "type Comment", size=11, color=NEG, bold=True))
    f.append(text(715, 194, "id: ID!", size=10, color=INK, anchor="start"))
    f.append(text(715, 212, "body: String!", size=10, color=INK, anchor="start"))
    f.append(text(715, 230, "author: User!", size=10, color=FIELD, bold=True, anchor="start"))

    # Скаляри внизу
    f.append(rect(230, 310, 620, 50, fill="#fbfbfb", stroke=LINE, sw=1.1, rx=6))
    f.append(text(540, 330, "Базові скаляри (листки графа): String · Int · Float · Boolean · ID", size=11, color=INK, bold=True))
    f.append(text(540, 348, "Модифікатори: ! (non-null), [ ] (масив), [Type!]! (непорожній масив обов'язкових елементів)", size=9.5, color=MUTED))

    # Зв'язки
    f.append(arrow(180, 185, 226, 185, color=LINE, sw=1.5))
    f.append(arrow(400, 220, 466, 220, color=FIELD, sw=1.8))
    f.append(arrow(470, 190, 404, 190, color=FIELD, sw=1.8))
    f.append(arrow(640, 200, 696, 200, color=FIELD, sw=1.8))

    f.append(line(315, 135, 315, 106, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(555, 135, 360, 106, color=MUTED, sw=1.2, dash="4,4"))

    render(os.path.join(IMG, "schema-type-system-graph.svg"), W, H, *f)


if __name__ == "__main__":
    fig_rest_vs_graphql()
    fig_execution_pipeline()
    fig_dataloader()
    fig_schema_graph()
    print("All figures generated successfully.")
