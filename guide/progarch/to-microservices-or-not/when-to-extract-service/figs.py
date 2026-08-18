# -*- coding: utf-8 -*-
"""Фігури до кроку «Коли виділяти сервіс: критерії та хибні приводи» (guide/progarch/monolith-vs-microservices)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_TINT = "#eafaf0"
RED_TINT = "#fdecea"
BLUE_TINT = "#eef2fb"
NEUT = "#f7f8fa"

def fig_four_criteria():
    """Чотири обґрунтовані критерії проти п'яти хибних приводів виділення сервісу."""
    W, H = 960, 520
    frags = []

    # Тітул / підзаголовок
    frags.append(text(W / 2, 32, "Порівняльний фільтр: обґрунтовані критерії vs хибні приводи", size=15, bold=True))

    # Ліва колонка — обґрунтовані критерії
    frags.append(rect(40, 60, 420, 420, fill=GREEN_TINT, stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(250, 92, "🟢 Обґрунтовані критерії (мережева межа купує)", size=14, color=FIELD, bold=True))

    criteria = [
        ("1. Різна швидкість деплою", "незалежний реліз-цикл для автономних фіч"),
        ("2. Асиметричний масштаб", "різний профіль ресурсів (CPU / RAM / GPU / IO)"),
        ("3. Ізоляція відмов та безпека", "PCI-DSS / HIPAA комплаєнс, захист ядра"),
        ("4. Автономія команд (Конвей)", "зменшення міжкомандного когнітивного тертя")
    ]

    for i, (title, desc) in enumerate(criteria):
        cy = 145 + i * 82
        b, _, _ = textbox(250, cy, "%s\n%s" % (title, desc), size=12, fill="#ffffff", stroke=FIELD, bold=False)
        frags.append(b)

    # Права колонка — хибні приводи
    frags.append(rect(500, 60, 420, 420, fill=RED_TINT, stroke=POS, sw=1.8, rx=10))
    frags.append(text(710, 92, "🔴 Хибні приводи (передчасний розпил)", size=14, color=POS, bold=True))

    pretenses = [
        ("1. «Для чистоти коду»", "чистоту дає модуль у моноліті, а не мережа"),
        ("2. «На майбутній масштаб»", "передчасний податок за гіпотетичний трафік"),
        ("3. «Для перевикористання»", "це вирішується бібліотекою, не RPC"),
        ("4. «Бо інша мова / мода»", "зоопарк стеків без виміряного профілю"),
        ("5. «Сервіс на кожну таблицю»", "наносервіси та розподілений N+1 / CRUD")
    ]

    for i, (title, desc) in enumerate(pretenses):
        cy = 132 + i * 68
        b, _, _ = textbox(710, cy, "%s\n%s" % (title, desc), size=11, fill="#ffffff", stroke=POS, bold=False)
        frags.append(b)

    render(os.path.join(IMG, "four-criteria-vs-pretenses.svg"), W, H, *frags,
           title="Обґрунтовані критерії проти хибних приводів виділення сервісу")


def fig_extraction_pipeline():
    """Покроковий конвеєр безпечного виділення сервісу з моноліта."""
    W, H = 1000, 440
    frags = []

    frags.append(text(W / 2, 30, "Чотири етапи безпечного виділення сервісу", size=15, bold=True))

    steps = [
        ("1. Модуль у моноліті", "Чистий мовний інтерфейс\nта приватні класи", BLUE_TINT, LINE),
        ("2. Асинхронні події", "Асинхронний Outbox pattern\nзамість прямого виклику", BLUE_TINT, LINE),
        ("3. Розділення даних", "Окремі схеми/БД,\nприватний доступ", GREEN_TINT, FIELD),
        ("4. Фізичний виніс", "Процес за gRPC/HTTP\nіз проксі (Strangler Fig)", GREEN_TINT, FIELD)
    ]

    for i, (title, desc, bg, stroke_color) in enumerate(steps):
        cx = 130 + i * 240
        cy = 180
        frags.append(rect(cx - 100, cy - 70, 200, 150, fill=bg, stroke=stroke_color, sw=1.8, rx=8))
        frags.append(text(cx, cy - 40, title, size=13, bold=True, color=INK))
        
        # Опис у декілька рядків
        lines = desc.split('\n')
        for j, line in enumerate(lines):
            frags.append(text(cx, cy + j * 20, line, size=11, color=MUTED))

        # Стрілка до наступного кроку
        if i < 3:
            frags.append(arrow(cx + 105, cy, cx + 135, cy, color=FIELD, sw=2.5))

    # Нижня пояснювальна смуга
    frags.append(rect(50, 310, 900, 90, fill=NEUT, stroke=LINE, sw=1.2, rx=8))
    frags.append(text(W / 2, 335, "⚠️ Ключове правило безпечного виділення", size=13, bold=True, color=INK))
    frags.append(text(W / 2, 365, "Якщо шов між модулями в моноліті не брудний — виносити в мережу НЕ МОЖНА. Спочатку робимо чистий модуль і розділяємо дані, і лише наприкінці ставить мережу.", size=11, color=MUTED))

    render(os.path.join(IMG, "extraction-pipeline-steps.svg"), W, H, *frags,
           title="Покроковий конвеєр безпечного виділення сервісу")

if __name__ == "__main__":
    fig_four_criteria()
    fig_extraction_pipeline()
    print("Figures generated successfully.")
