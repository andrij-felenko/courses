koval = Account(
    customer="Родина Коваль",
    active=True,
    lines=[
        Line("Кухня",  "day",   150),
        Line("Бойлер", "night", 320),
        Line("Гараж",  "day",   80),
    ],
)

EXPECTED = "\n".join([
    "Рахунок — Родина Коваль",
    "  Кухня: 150 кВт·год — 390.00 грн",
    "  Бойлер: 320 кВт·год — 384.00 грн",
    "  Гараж: 80 кВт·год — 200.00 грн",
    "Разом: 974.00 грн",
    "Бонусні кіловати: 120",
    "",
])

def test_statement_golden_master():
    assert statement(koval) == EXPECTED
