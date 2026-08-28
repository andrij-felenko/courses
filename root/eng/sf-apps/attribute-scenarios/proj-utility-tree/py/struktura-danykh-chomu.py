from dataclasses import dataclass

# Трибальна шкала: Н=1, С=2, В=3 (низько / середньо / високо).

@dataclass(frozen=True)
class Scenario:
    title: str
    importance: int   # цінність для успіху системи (1..3)
    difficulty: int   # архітектурна складність досягти (1..3)

@dataclass
class Attribute:
    name: str                    # якісний атрибут — гілка дерева
    scenarios: list[Scenario]    # листя цієї гілки

@dataclass
class UtilityTree:
    root: str                    # «Корисність системи»
    attributes: list[Attribute]

tree = UtilityTree(
    root="Корисність системи",
    attributes=[
        Attribute("Продуктивність", [
            Scenario("Профіль за 200 мс у пік, p95",   importance=3, difficulty=3),
            Scenario("Річний звіт рахується за < 5 с",  importance=2, difficulty=1),
            Scenario("Пошук у піку віддає за < 300 мс", importance=3, difficulty=2),
        ]),
        Attribute("Доступність", [
            Scenario("Переживає втрату вузла БД, перерва <= 30 с", importance=3, difficulty=3),
            Scenario("Переживає втрату дата-центру без втрати даних", importance=3, difficulty=3),
            Scenario("Подія в журналі не губиться", importance=2, difficulty=2),
        ]),
        Attribute("Змінюваність", [
            Scenario("Нова валюта за <= 2 дні, без правки ядра платежів", importance=3, difficulty=2),
            Scenario("Новий канал сповіщень за <= тиждень", importance=1, difficulty=2),
        ]),
    ],
)
