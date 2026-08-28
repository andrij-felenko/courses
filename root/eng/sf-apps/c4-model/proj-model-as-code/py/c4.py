# c4.py — модель як дані. Тут немає рендерингу: лише вузли й ребра графа.
from dataclasses import dataclass
from enum import Enum

class Kind(str, Enum):
    PERSON = "person"
    SYSTEM = "system"
    CONTAINER = "container"
    COMPONENT = "component"

@dataclass(frozen=True)
class Element:
    id: str                       # СТАБІЛЬНИЙ ключ — на нього посилається все інше
    kind: Kind
    name: str                     # показове ім'я; його можна міняти будь-коли
    parent: str | None = None     # власник: контейнер → система, компонент → контейнер
    technology: str | None = None # "React", "PostgreSQL" — лише де є сенс
    external: bool = False         # поза межею нашої системи

@dataclass(frozen=True)
class Relation:
    src: str                      # id елемента-джерела
    dst: str                      # id елемента-цілі
    label: str
    technology: str | None = None

@dataclass
class Model:
    root: str                     # id нашої системи — scope за замовчуванням
    elements: list[Element]
    relations: list[Relation]

    def by_id(self, eid: str) -> Element:
        return next(e for e in self.elements if e.id == eid)

    def children(self, eid: str) -> list[Element]:
        return [e for e in self.elements if e.parent == eid]


# --- та сама система, що на діаграмах теми, як звичайні дані ---
C = Kind
shop = Model(
    root="shop",
    elements=[
        Element("customer", C.PERSON, "Покупець", external=True),
        Element("shop",     C.SYSTEM, "Інтернет-магазин"),
        Element("payments", C.SYSTEM, "Платіжний шлюз", external=True),
        Element("email",    C.SYSTEM, "Пошта", external=True),

        Element("web",   C.CONTAINER, "Веб-застосунок", parent="shop", technology="React"),
        Element("api",   C.CONTAINER, "API-сервіс",     parent="shop", technology="Java/Spring"),
        Element("db",    C.CONTAINER, "База даних",      parent="shop", technology="PostgreSQL"),
        Element("queue", C.CONTAINER, "Черга задач",     parent="shop", technology="RabbitMQ"),
    ],
    relations=[
        Relation("customer", "web",      "переглядає й купує", "HTTPS"),
        Relation("web",      "api",      "надсилає запити",    "HTTPS/JSON"),
        Relation("api",      "db",       "читає й пише",       "SQL"),
        Relation("api",      "queue",    "кладе задачі",       "AMQP"),
        Relation("api",      "payments", "проводить оплату",   "API"),
        Relation("queue",    "email",    "шле листи",          "SMTP"),
    ],
)
