# -*- coding: utf-8 -*-
"""Генератор векторних ілюстрацій для теми «Патерн Сага».
Використовує спільну бібліотеку svgkit з каталогу scripts/.
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_saga_vs_2pc():
    """Порівняння 2PC (блокуючі замки) та Саги (локальні транзакції)."""
    w, h = 880, 430
    frags = []

    # Заголовок блоку 2PC
    frags.append(fitbox(20, 15, 405, 395, "", fill="#fff8f7", stroke="#e0b4b0", sw=1.5, rx=8))
    frags.append(text(222, 42, "Двофазний коміт (2PC): синхронний розподілений замок", size=13, color=POS, bold=True))

    # Складові 2PC
    frags.append(textbox(222, 85, "Координатор 2PC\n(Central Coordinator)", size=12, pad=8, fill="#ffffff", stroke=LINE, min_w=240)[0])

    frags.append(textbox(110, 190, "Сервіс A (БД)\n[Prepare -> Commit]\nЗамок на час T_all", size=11, pad=7, fill="#ffffff", stroke=POS, min_w=150)[0])
    frags.append(textbox(335, 190, "Сервіс B (БД)\n[Prepare -> Commit]\nЗамок на час T_all", size=11, pad=7, fill="#ffffff", stroke=POS, min_w=150)[0])

    frags.append(arrow(180, 115, 120, 155, color=LINE, sw=1.5))
    frags.append(arrow(265, 115, 325, 155, color=LINE, sw=1.5))

    # Небезпека 2PC
    frags.append(fitbox(40, 270, 365, 125,
                        "Властивості 2PC:\n"
                        "• Сувора атомарність та ізоляція (ACID)\n"
                        "• Блокування тримаються до фіналу всіх вузлів\n"
                        "• Збій координатора заморожує всі сервіси\n"
                        "• Низька пропускна здатність, висока латентність",
                        size=11, pad=8, fill="#fdecea", stroke=POS, sw=1.2, color=INK))

    # Заголовок блоку Saga
    frags.append(fitbox(455, 15, 405, 395, "", fill="#f4faf6", stroke="#a3d9b8", sw=1.5, rx=8))
    frags.append(text(657, 42, "Патерн «Сага»: ланцюг локальних транзакцій", size=13, color=FIELD, bold=True))

    frags.append(textbox(657, 85, "Оркестратор Саги / Події\n(Saga Coordinator / Event Bus)", size=12, pad=8, fill="#ffffff", stroke=LINE, min_w=240)[0])

    frags.append(textbox(545, 190, "Сервіс A (БД)\nЛокальна транзакція T1\nКоміт негайно (no lock)", size=11, pad=7, fill="#ffffff", stroke=FIELD, min_w=150)[0])
    frags.append(textbox(770, 190, "Сервіс B (БД)\nЛокальна транзакція T2\nКоміт негайно (no lock)", size=11, pad=7, fill="#ffffff", stroke=FIELD, min_w=150)[0])

    frags.append(arrow(615, 115, 555, 155, color=LINE, sw=1.5))
    frags.append(arrow(700, 115, 760, 155, color=LINE, sw=1.5))

    # Переваги Саги
    frags.append(fitbox(475, 270, 365, 125,
                        "Властивості Саги:\n"
                        "• Кінцева узгодженість замість ізоляції (ACD)\n"
                        "• Негайне звільнення локальних ресурсів\n"
                        "• Збій кроку -> запуск компенсацій (C_i)\n"
                        "• Висока масштабованість та відмовостійкість",
                        size=11, pad=8, fill="#e8f8f0", stroke=FIELD, sw=1.2, color=INK))

    render(os.path.join(OUT_DIR, "saga-vs-2pc.svg"), w, h, *frags)


def fig_saga_forward_backward():
    """Прямий поступ саги та зворотний каскад компенсацій."""
    w, h = 880, 380
    frags = []

    # Прямий шлях
    frags.append(text(160, 35, "1. Прямий хід (Forward Execution)", size=13, color=FIELD, bold=True))

    frags.append(textbox(150, 95, "Транзакція T1\nСписання коштів\n[Коміт виконано]", size=11, pad=8, fill="#e8f8f0", stroke=FIELD, min_w=140)[0])
    frags.append(textbox(380, 95, "Транзакція T2\nРезерв на складі\n[Коміт виконано]", size=11, pad=8, fill="#e8f8f0", stroke=FIELD, min_w=140)[0])
    frags.append(textbox(610, 95, "Транзакція T3\nВиклик доставки\n[ПОМИЛКА API 500]", size=11, pad=8, fill="#fdecea", stroke=POS, bold=True, min_w=140)[0])

    frags.append(arrow(230, 95, 300, 95, color=FIELD, sw=2.0))
    frags.append(arrow(460, 95, 530, 95, color=FIELD, sw=2.0))

    # Зворотний хід
    frags.append(text(210, 205, "2. Зворотний хід компенсацій (Backward Compensation)", size=13, color=POS, bold=True))

    frags.append(textbox(380, 275, "Компенсація C2\nЗняття резерву на складі\n[Семантичне скасування T2]", size=11, pad=8, fill="#fef5f4", stroke=POS, min_w=165)[0])
    frags.append(textbox(150, 275, "Компенсація C1\nПовернення грошей на картку\n[Семантичне скасування T1]", size=11, pad=8, fill="#fef5f4", stroke=POS, min_w=165)[0])

    # Зв'язок від збою T3 до запуску C2
    frags.append(arrow(610, 140, 480, 235, color=POS, sw=2.0))
    frags.append(arrow(290, 275, 240, 275, color=POS, sw=2.0))

    # Підсумковий статус
    frags.append(textbox(750, 275, "Фінальний стан Саги:\nFAILED / COMPENSATED\n(Система узгоджена)", size=11, pad=8, fill="#f4f6f8", stroke=LINE, min_w=170)[0])
    frags.append(arrow(680, 140, 730, 235, color=MUTED, sw=1.5))

    render(os.path.join(OUT_DIR, "saga-forward-backward-flow.svg"), w, h, *frags)


def fig_orchestration_vs_choreography():
    """Порівняння двох стилів координації саг: Оркестрація та Хореографія."""
    w, h = 880, 420
    frags = []

    # Лівий блок: Хореографія
    frags.append(fitbox(20, 15, 405, 385, "", fill="#f9fafb", stroke="#d1d5db", sw=1.5, rx=8))
    frags.append(text(222, 42, "Хореографія (Choreography / Events)", size=13, color=INK, bold=True))

    frags.append(textbox(110, 110, "Order Service\n(Емітує OrderCreated)", size=11, pad=7, fill="#ffffff", stroke=LINE, min_w=140)[0])
    frags.append(textbox(335, 110, "Payment Service\n(Слухає OrderCreated,\nемітує PaymentDone)", size=11, pad=7, fill="#ffffff", stroke=LINE, min_w=140)[0])
    frags.append(textbox(222, 230, "Inventory Service\n(Слухає PaymentDone,\nемітує OutOfStock)", size=11, pad=7, fill="#ffffff", stroke=LINE, min_w=150)[0])

    frags.append(arrow(190, 110, 255, 110, color=LINE, sw=1.5))
    frags.append(arrow(335, 155, 275, 195, color=LINE, sw=1.5))
    frags.append(arrow(170, 195, 110, 155, color=POS, sw=1.5))

    frags.append(fitbox(35, 305, 375, 80,
                        "• Немає центрального вузла відмови\n"
                        "• Складно відстежувати потік виконання\n"
                        "• Ризик циклічних залежностей між подіями\n"
                        "• Підходить для простих саг (2–4 кроки)",
                        size=11, pad=6, fill="#ffffff", stroke="#e5e7eb", sw=1.0, color=INK))

    # Правий блок: Оркестрація
    frags.append(fitbox(455, 15, 405, 385, "", fill="#f9fafb", stroke="#d1d5db", sw=1.5, rx=8))
    frags.append(text(657, 42, "Оркестрація (Orchestration / State Machine)", size=13, color=INK, bold=True))

    frags.append(textbox(657, 110, "Saga Orchestrator\n[Керівний автомат станів + SEC Log]", size=11, pad=8, fill="#e8f0fe", stroke=NEG, bold=True, min_w=230)[0])

    frags.append(textbox(530, 230, "Payment Service\n[Command -> Reply]", size=11, pad=7, fill="#ffffff", stroke=LINE, min_w=130)[0])
    frags.append(textbox(657, 230, "Inventory Service\n[Command -> Reply]", size=11, pad=7, fill="#ffffff", stroke=LINE, min_w=130)[0])
    frags.append(textbox(785, 230, "Shipping Service\n[Command -> Reply]", size=11, pad=7, fill="#ffffff", stroke=LINE, min_w=130)[0])

    frags.append(arrow(600, 150, 545, 195, color=NEG, sw=1.5))
    frags.append(arrow(657, 150, 657, 195, color=NEG, sw=1.5))
    frags.append(arrow(715, 150, 770, 195, color=NEG, sw=1.5))

    frags.append(fitbox(470, 305, 375, 80,
                        "• Централізований контроль і журнал станів\n"
                        "• Простий моніторинг, тайм-аути та компенсації\n"
                        "• Оркестратор знає повний сценарій бізнес-процесу\n"
                        "• Підходить для складних ланцюгів транзакцій",
                        size=11, pad=6, fill="#ffffff", stroke="#e5e7eb", sw=1.0, color=INK))

    render(os.path.join(OUT_DIR, "orchestration-vs-choreography.svg"), w, h, *frags)


def fig_step_classification():
    """Класифікація кроків саги: компенсовні, поворотна та повторювані дії."""
    w, h = 880, 370
    frags = []

    frags.append(fitbox(20, 20, 270, 325, "", fill="#fff8f7", stroke="#e0b4b0", sw=1.5, rx=8))
    frags.append(text(155, 48, "1. Компенсовні транзакції", size=12, color=POS, bold=True))
    frags.append(text(155, 66, "(Compensable Steps)", size=11, color=POS))
    frags.append(textbox(155, 130, "Кроки T1, T2\n• Списання з рахунку\n• Резервування товару", size=11, pad=8, fill="#ffffff", stroke=POS, min_w=220)[0])
    frags.append(fitbox(35, 205, 240, 125,
                        "Особливість:\n"
                        "Дії можуть бути скасовані\n"
                        "компенсаціями C1, C2.\n"
                        "Виконуються ДО точки\n"
                        "неповернення.",
                        size=11, pad=8, fill="#fdecea", stroke=POS, sw=1.0, color=INK))

    frags.append(fitbox(305, 20, 270, 325, "", fill="#fffdf0", stroke="#e6cf73", sw=1.5, rx=8))
    frags.append(text(440, 48, "2. Поворотна транзакція", size=12, color="#9c7a00", bold=True))
    frags.append(text(440, 66, "(Pivot Transaction)", size=11, color="#9c7a00"))
    frags.append(textbox(440, 130, "Крок T3 (Точка неповернення)\n• Авторизація фінального чека\n• Підпис договору", size=11, pad=8, fill="#ffffff", stroke="#9c7a00", min_w=230)[0])
    frags.append(fitbox(320, 205, 240, 125,
                        "Особливість:\n"
                        "Якщо T3 вдалася — сага\n"
                        "гарантовано йде до кінця.\n"
                        "Якщо T3 зазнала невдачі —\n"
                        "запускається компенсація C2, C1.",
                        size=11, pad=8, fill="#fcf8e3", stroke="#9c7a00", sw=1.0, color=INK))

    frags.append(fitbox(590, 20, 270, 325, "", fill="#f4faf6", stroke="#a3d9b8", sw=1.5, rx=8))
    frags.append(text(725, 48, "3. Повторювані транзакції", size=12, color=FIELD, bold=True))
    frags.append(text(725, 66, "(Retryable / Forward)", size=11, color=FIELD))
    frags.append(textbox(725, 130, "Кроки T4, T5\n• Друк квитанції\n• Відправка сповіщення SMS", size=11, pad=8, fill="#ffffff", stroke=FIELD, min_w=220)[0])
    frags.append(fitbox(605, 205, 240, 125,
                        "Особливість:\n"
                        "Виконуються ПІСЛЯ pivot.\n"
                        "Не можуть зазнати фатальної\n"
                        "бізнес-відмови: при збоях\n"
                        "повторюються до успіху.",
                        size=11, pad=8, fill="#e8f8f0", stroke=FIELD, sw=1.0, color=INK))

    frags.append(arrow(295, 130, 320, 130, color=LINE, sw=2.0))
    frags.append(arrow(580, 130, 605, 130, color=LINE, sw=2.0))

    render(os.path.join(OUT_DIR, "saga-step-classification.svg"), w, h, *frags)


def fig_isolation_anomalies():
    """Аномалії відсутності ізоляції в сагах та засоби їх подолання."""
    w, h = 880, 390
    frags = []

    # Аномалія
    frags.append(fitbox(20, 20, 405, 350, "", fill="#fff8f7", stroke="#e0b4b0", sw=1.5, rx=8))
    frags.append(text(222, 48, "Аномалія: Брудне читання (Dirty Read)", size=12, color=POS, bold=True))

    frags.append(textbox(222, 105, "Сага №1: T1 списала 10 000 грн\n[Баланс тимчасово 0 грн]", size=11, pad=8, fill="#ffffff", stroke=POS, min_w=240)[0])
    frags.append(textbox(222, 195, "Паралельна Сага №2: бачить баланс 0 грн\nі відхиляє іншу критичну операцію", size=11, pad=8, fill="#ffffff", stroke=POS, min_w=260)[0])
    frags.append(textbox(222, 285, "Сага №1 зазнає збою на кроці T3\nі виконує C1 (повертає 10 000 грн)", size=11, pad=8, fill="#ffffff", stroke=POS, min_w=240)[0])

    frags.append(arrow(222, 140, 222, 160, color=POS, sw=1.5))
    frags.append(arrow(222, 230, 222, 250, color=POS, sw=1.5))

    # Контрзахід
    frags.append(fitbox(455, 20, 405, 350, "", fill="#f4faf6", stroke="#a3d9b8", sw=1.5, rx=8))
    frags.append(text(657, 48, "Контрзахід: Семантичний замок (Semantic Lock)", size=12, color=FIELD, bold=True))

    frags.append(textbox(657, 105, "Сага №1: встановлює стан PENDING_APPROVAL\n[Сума заблокована у hold-балансі]", size=11, pad=8, fill="#ffffff", stroke=FIELD, min_w=260)[0])
    frags.append(textbox(657, 195, "Паралельна Сага №2: бачить стан PENDING\nі чекає або читає доступний залишок", size=11, pad=8, fill="#ffffff", stroke=FIELD, min_w=260)[0])
    frags.append(textbox(657, 285, "Сага №1 скасовує hold при збої\nабо фіналізує при успіху без аномалій", size=11, pad=8, fill="#ffffff", stroke=FIELD, min_w=260)[0])

    frags.append(arrow(657, 140, 657, 160, color=FIELD, sw=1.5))
    frags.append(arrow(657, 230, 657, 250, color=FIELD, sw=1.5))

    render(os.path.join(OUT_DIR, "saga-isolation-anomalies.svg"), w, h, *frags)


if __name__ == "__main__":
    print("Генерація діаграм для теми saga-pattern...")
    fig_saga_vs_2pc()
    fig_saga_forward_backward()
    fig_orchestration_vs_choreography()
    fig_step_classification()
    fig_isolation_anomalies()
    print("Усі 5 діаграм успішно згенеровано.")
