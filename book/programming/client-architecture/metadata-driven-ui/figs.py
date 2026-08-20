# -*- coding: utf-8 -*-
"""Генератор діаграм для теми metadata-driven-ui."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, rect, line, arrow, text, mtext, fitbox,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD, FONT
)

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')


def fig_pipeline():
    """Конвеєр обробки Metadata-Driven UI: від сервера до нативного дерева віджетів."""
    w, h = 840, 370
    frags = []

    frags.append(text(w / 2, 25, "Конвеєр рендерингу Metadata-Driven UI (Server-Driven UI)", size=16, bold=True))

    # Блок 1: Серверний бекенд
    frags.append(rect(25, 55, 180, 285, fill="#fdfbf7", stroke="#e67e22", sw=1.5, rx=8))
    frags.append(text(115, 80, "Сервер / CMS / Rule Engine", size=13, color="#d35400", bold=True))
    frags.append(fitbox(40, 105, 150, 45, "Бізнес-контекст\nКористувач / Локаль / A/B", size=11, fill="#ffffff", stroke=LINE))
    frags.append(arrow(115, 150, 115, 175, color=LINE, sw=1.5))
    frags.append(fitbox(40, 175, 150, 50, "Генератор схеми (DSL)\nJSON Schema / AST дерев", size=11, fill="#ffffff", stroke=LINE))
    frags.append(arrow(115, 225, 115, 250, color=LINE, sw=1.5))
    frags.append(fitbox(40, 250, 150, 70, "HTTP-відповідь\n{ schema_version: 2,\n  layout: { type: 'Stack' },\n  rules: [...] }", size=10, fill="#fef5e7", stroke="#e67e22"))

    # Мережевий перехід
    frags.append(arrow(205, 195, 255, 195, color="#e67e22", sw=2.0))
    frags.append(text(230, 185, "JSON / AST", size=10, color=MUTED, bold=True))

    # Блок 2: Клієнтський рантайм (MDUI Runtime)
    frags.append(rect(255, 55, 330, 285, fill="#f4f8fd", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(420, 80, "Клієнтський інтерпретатор (MDUI Runtime)", size=13, color=NEG, bold=True))
    frags.append(fitbox(275, 105, 290, 45, "1. Валідація схеми та розбір AST\nПеревірка версій і типів вузлів", size=11, fill="#ffffff", stroke=LINE))
    frags.append(arrow(420, 150, 420, 170, color=LINE, sw=1.5))
    frags.append(fitbox(275, 170, 290, 48, "2. Обчислення виразів (Safe AST Eval)\nСтан форми + умови видимості", size=11, fill="#ffffff", stroke=LINE))
    frags.append(arrow(420, 218, 420, 238, color=LINE, sw=1.5))
    frags.append(fitbox(275, 238, 290, 52, "3. Реєстр компонентів (Component Registry)\nДиспетчеризація типу на нативний рендерер", size=11, fill="#ffffff", stroke=LINE))
    frags.append(fitbox(275, 296, 290, 32, "Керування подіями та диспетчер дій (Actions)", size=10, fill="#eaf0fd", stroke=NEG))

    # Перехід до платформи
    frags.append(arrow(585, 195, 635, 195, color=FIELD, sw=2.0))
    frags.append(text(610, 185, "Render", size=10, color=FIELD, bold=True))

    # Блок 3: Нативні платформи
    frags.append(rect(635, 55, 180, 285, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(725, 80, "Нативний інтерфейс", size=13, color=FIELD, bold=True))
    frags.append(fitbox(650, 105, 150, 45, "iOS\nSwiftUI / UIKit", size=11, fill="#ffffff", stroke=LINE))
    frags.append(fitbox(650, 160, 150, 45, "Android\nJetpack Compose", size=11, fill="#ffffff", stroke=LINE))
    frags.append(fitbox(650, 215, 150, 45, "Web / Desktop\nReact / Flutter / DOM", size=11, fill="#ffffff", stroke=LINE))
    frags.append(fitbox(650, 270, 150, 55, "60/120 FPS\nАпаратне прискорення\nНативна доступність", size=10, fill="#eef8f2", stroke=FIELD))

    render(os.path.join(OUT_DIR, "metadata-driven-ui-pipeline.svg"), w, h, *frags)


def fig_registry_tree():
    """Рекурсивний обхід дерева метаданих і диспетчеризація через реєстр компонентів."""
    w, h = 840, 350
    frags = []

    frags.append(text(w / 2, 25, "Рекурсивна диспетчеризація та деградація невідомих компонентів", size=16, bold=True))

    # Ліва колонка: Вхідний AST
    frags.append(rect(25, 50, 240, 280, fill="#fdfbf7", stroke="#d35400", sw=1.5, rx=8))
    frags.append(text(145, 75, "Вхідний AST-вузол", size=13, color="#d35400", bold=True))
    frags.append(fitbox(45, 95, 200, 50, "Node: { type: 'Stack',\n  direction: 'vertical' }", size=11, fill="#ffffff", stroke=LINE))
    frags.append(arrow(145, 145, 145, 175, color=LINE, sw=1.5))
    frags.append(fitbox(45, 175, 200, 50, "Child 1: { type: 'TextInput',\n  bind: 'user.email' }", size=11, fill="#ffffff", stroke=LINE))
    frags.append(arrow(145, 225, 145, 255, color=LINE, sw=1.5))
    frags.append(fitbox(45, 255, 200, 55, "Child 2: { type: 'BiometricAuth',\n  provider: 'face_id' }", size=11, fill="#fff0f0", stroke=POS))

    # Стрілки в центр
    frags.append(arrow(265, 190, 315, 190, color=LINE, sw=1.8))
    frags.append(text(290, 180, "type", size=11, color=MUTED, bold=True))

    # Центральна колонка: Реєстр компонентів
    frags.append(rect(315, 50, 230, 280, fill="#f4f8fd", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(430, 75, "Реєстр компонентів", size=13, color=NEG, bold=True))
    frags.append(fitbox(330, 100, 200, 42, "Stack → StackRenderer", size=11, fill="#ffffff", stroke=LINE))
    frags.append(fitbox(330, 148, 200, 42, "TextInput → InputRenderer", size=11, fill="#ffffff", stroke=LINE))
    frags.append(fitbox(330, 196, 200, 42, "Button → ButtonRenderer", size=11, fill="#ffffff", stroke=LINE))
    frags.append(fitbox(330, 244, 200, 68, "Пошук у словнику:\nif (registry.has(type)) render()\nelse fallbackHandler()", size=10, fill="#eaf0fd", stroke=NEG))

    # Стрілки з центру праворуч
    frags.append(arrow(545, 135, 605, 115, color=FIELD, sw=1.8))
    frags.append(text(575, 110, "Знайдено", size=10, color=FIELD, bold=True))

    frags.append(arrow(545, 240, 605, 260, color=POS, sw=1.8))
    frags.append(text(575, 265, "Невідомо", size=10, color=POS, bold=True))

    # Права колонка: Наслідок виконання
    frags.append(rect(605, 50, 210, 280, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(710, 75, "Результат рендерингу", size=13, color=INK, bold=True))

    frags.append(fitbox(620, 95, 180, 85, "Нативний віджет\nІнстанціювання компонента,\nпідключення реактивних пропсів\nта обробників подій", size=10, fill="#eef8f2", stroke=FIELD))

    frags.append(fitbox(620, 205, 180, 105, "Граційна деградація (Fallback)\n1. Пропуск невідомого вузла\n2. Відображення заглушки\n3. Web-посилання або оновлення\nЗапобігання падінню програми", size=10, fill="#fdecea", stroke=POS))

    render(os.path.join(OUT_DIR, "component-registry-tree.svg"), w, h, *frags)


def fig_safe_evaluator():
    """Безпечне виконання виразів: небезпечний eval проти ізольованого AST-інтерпретатора."""
    w, h = 840, 360
    frags = []

    frags.append(text(w / 2, 25, "Безпека виконання динамічної логіки: eval() проти Safe AST Interpreter", size=16, bold=True))

    # Ліва колонка: Небезпечний підхід eval()
    col1_x, col1_w = 30, 370
    frags.append(rect(col1_x, 50, col1_w, 290, fill="#fff7f7", stroke=POS, sw=1.5, rx=8))
    frags.append(text(col1_x + col1_w / 2, 75, "Небезпечний підхід: eval() / new Function()", size=13, color=POS, bold=True))
    frags.append(fitbox(col1_x + 20, 95, 330, 48, "Рядок коду з сервера:\n\"form.amount > 1000 && sendCookie()\"", size=11, fill="#ffffff", stroke=LINE))
    frags.append(arrow(col1_x + col1_w / 2, 143, col1_x + col1_w / 2, 168, color=POS, sw=1.8))
    frags.append(fitbox(col1_x + 20, 168, 330, 60, "Пряме виконання в JS VM\nДоступ до window, document, fetch,\nпам'яті процесу та системних API", size=11, fill="#fdecea", stroke=POS))
    frags.append(arrow(col1_x + col1_w / 2, 228, col1_x + col1_w / 2, 253, color=POS, sw=1.8))
    frags.append(fitbox(col1_x + 20, 253, 330, 72, "КАТАСТРОФА БЕЗПЕКИ\n• Remote Code Execution (RCE) / XSS\n• Викрадення сесійних токенів\n• Блокування в App Store (Guideline 2.5.2)", size=10, fill="#ffffff", stroke=POS))

    # Права колонка: Безпечний підхід Safe AST
    col2_x, col2_w = 440, 370
    frags.append(rect(col2_x, 50, col2_w, 290, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(col2_x + col2_w / 2, 75, "Безпечний підхід: Sandboxed AST Interpreter", size=13, color=FIELD, bold=True))
    frags.append(fitbox(col2_x + 20, 95, 330, 48, "Декларативне дерево правил (JSON AST):\n{ op: '>', left: { var: 'amount' }, right: 1000 }", size=11, fill="#ffffff", stroke=LINE))
    frags.append(arrow(col2_x + col2_w / 2, 143, col2_x + col2_x / 2, 168, color=FIELD, sw=1.8))
    frags.append(fitbox(col2_x + 20, 168, 330, 60, "Ізольований обчислювач операцій\nОбмежена граматика (Turing-incomplete),\nдоступ лише до переданого стану форми", size=11, fill="#eef8f2", stroke=FIELD))
    frags.append(arrow(col2_x + col2_w / 2, 228, col2_x + col2_w / 2, 253, color=FIELD, sw=1.8))
    frags.append(fitbox(col2_x + 20, 253, 330, 72, "ГАРАНТІЯ БЕЗПЕКИ\n• Нульовий доступ до мережі та пам'яті\n• Захист від нескінченних циклів\n• Повна сумісність із правилами App Store", size=10, fill="#ffffff", stroke=FIELD))

    render(os.path.join(OUT_DIR, "safe-expression-evaluator.svg"), w, h, *frags)


def fig_versioning_negotiation():
    """Узгодження версій схеми та можливостей клієнта (Capability Handshake)."""
    w, h = 840, 340
    frags = []

    frags.append(text(w / 2, 25, "Узгодження версій і можливостей клієнта (Capability Negotiation)", size=16, bold=True))

    # Клієнт (ліворуч)
    frags.append(rect(30, 60, 230, 260, fill="#f4f8fd", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(145, 85, "Клієнтський застосунок", size=13, color=NEG, bold=True))
    frags.append(fitbox(45, 105, 200, 80, "Реєстр нативних можливостей:\n• app_version: 3.2.0\n• schema_version: 4\n• widgets: [Stack, Text,\n  Input, Carousel, Card]", size=10, fill="#ffffff", stroke=LINE))
    frags.append(fitbox(45, 200, 200, 100, "Локальний кеш схем:\n• ETag: \"w/9f2a4b\"\n• Schema DB (IndexedDB)\nМиттєвий старт з кешу,\nфонова перевірка оновлень", size=10, fill="#eaf0fd", stroke=NEG))

    # Посередині: Мережеві запити / заголовки
    # Запит угорі
    frags.append(arrow(260, 130, 570, 130, color=NEG, sw=1.8))
    frags.append(text(415, 115, "GET /screen/checkout", size=11, color=NEG, bold=True))
    frags.append(text(415, 145, "X-Schema-Version: 4 | If-None-Match: \"w/9f2a4b\"", size=9, color=MUTED))

    # Відповідь внизу
    frags.append(arrow(570, 230, 260, 230, color=FIELD, sw=1.8))
    frags.append(text(415, 215, "200 OK (або 304 Not Modified)", size=11, color=FIELD, bold=True))
    frags.append(text(415, 245, "ETag: \"w/9f2a4b\" | Content-Type: application/sdui+json", size=9, color=MUTED))

    # Сервер (праворуч)
    frags.append(rect(570, 60, 240, 260, fill="#fdfbf7", stroke="#d35400", sw=1.5, rx=8))
    frags.append(text(690, 85, "Серверний компілятор SDUI", size=13, color="#d35400", bold=True))
    frags.append(fitbox(585, 105, 210, 80, "Фільтрація за можливостями:\nКомпіляція AST з урахуванням\nверсії клієнта. Нові віджети\nзамінюються на сумісні старі", size=10, fill="#ffffff", stroke=LINE))
    frags.append(fitbox(585, 200, 210, 100, "Оптимізація трафіку:\n• Генерація ETag / SHA-256\n• Стиснення Brotli / Gzip\n• Дельта-патчі (JSON Patch)\nмінімізація байтів у мережі", size=10, fill="#fef5e7", stroke="#d35400"))

    render(os.path.join(OUT_DIR, "schema-versioning-negotiation.svg"), w, h, *frags)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    fig_pipeline()
    fig_registry_tree()
    fig_safe_evaluator()
    fig_versioning_negotiation()
    print("Всі фігури згенеровано успішно.")
