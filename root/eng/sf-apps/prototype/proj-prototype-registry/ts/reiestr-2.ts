const bestiary = new PrototypeRegistry<Monster>();
bestiary.register("орк",
  new Monster("орк", 30,
    new Stats(8, 4, new Map([["вогонь", -2]])),
    ["монета", "шкура"]));

const a = bestiary.create("орк");
const b = bestiary.create("орк");

a.loot.push("щит");                 // чіпаємо здобич ОДНІЄЇ копії
console.log(b.loot);                // ['монета','шкура'] — інша копія недоторкана
console.log(a.stats === b.stats);   // false — кожна має власний Stats
a.stats.resist.set("вогонь", 0);    // міняємо опір однієї...
console.log(b.stats.resist.get("вогонь")); // -2 — інша не змінилась
