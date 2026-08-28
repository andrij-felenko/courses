bestiary = PrototypeRegistry()
bestiary.register("орк",
    Monster("орк", 30, Stats(8, 4, {"вогонь": -2}), ["монета", "шкура"]))

a = bestiary.create("орк")
b = bestiary.create("орк")

a.loot.append("щит")                    # чіпаємо здобич ОДНІЄЇ копії
print(b.loot)                           # ['монета','шкура'] — інша недоторкана
print(a.stats is b.stats)               # False — кожна має власний Stats
a.stats.resist["вогонь"] = 0            # міняємо опір однієї...
print(b.stats.resist["вогонь"])         # -2 — інша не змінилась
