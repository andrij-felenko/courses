TODAY    = date(2026, 4, 12)
DEADLINE = date(2026, 5, 15)   # оголошено НАПЕРЕД, ще до першого факта

journal: list[Event] = [
    Considered(date(2026,3,1), Option("in-process",    2_000,     1,  False), "нічого не ставити"),
    Considered(date(2026,3,1), Option("managed-queue", 50_000,    3,  False), "черга як послуга"),
    Considered(date(2026,3,1), Option("kafka",         1_000_000, 12, True),  "стеля на виріст"),
]

# 1. Здогад із наради — і набір «збігся» за один день
f1 = Fact("F1", "потрібна доставка «точно раз»", ASSUMED, "нарада, ніхто не перевіряв",
          date(2026,3,2), lambda o: o.exactly_once)
journal = land(journal, f1)
print(verdict(replay(journal), date(2026,3,3), DEADLINE))

# 2. Пішли й перевірили: вимога хибна → факт відкликано
journal = journal + [Retracted(date(2026,3,20), "F1",
    "бізнес вимагає ідемпотентних споживачів, а не «точно раз»: TICKET-412")]
print([o.name for o in replay(journal).alive])   # набір розправився САМ

# 3-4. Тепер факти з доказами
f2 = Fact("F2", "пік навантаження 20 000 повідомлень/с", MEASURED,
          "прогін ходячого кістяка 2026-03-27, звіт LOAD-7",
          date(2026,3,28), lambda o: o.max_throughput >= 20_000)
journal = land(journal, f2)
f3 = Fact("F3", "бюджет експлуатації — 5 год/тиждень", QUOTED,
          "прайс + рішення тимліда, DOC-31",
          date(2026,4,10), lambda o: o.ops_cost_week <= 5)
journal = land(journal, f3)
st = replay(journal)
print(verdict(st, TODAY, DEADLINE))

# Що якби F3 так і не приземлився — питаємо минуле
mid = replay(journal, upto=date(2026,4,1))
print(verdict(mid, DEADLINE + timedelta(days=1), DEADLINE))

# 5. Хтось затягує межу «щоб напевно»
f4 = Fact("F4", "бюджет експлуатації — 2 год/тиждень", ASSUMED, "хотілося б",
          date(2026,4,11), lambda o: o.ops_cost_week <= 2)
try:
    land(journal, f4)
except OverConstrained as e:
    print(e)

print(explain(st, "kafka"))
print(explain(st, "in-process"))
