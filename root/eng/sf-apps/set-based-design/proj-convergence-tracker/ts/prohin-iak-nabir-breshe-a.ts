const TODAY: Day = "2026-04-12";
const DEADLINE: Day = "2026-05-15";   // оголошено НАПЕРЕД, ще до першого факта

let journal: readonly Event[] = [
  { kind: "considered", when: "2026-03-01", why: "нічого не ставити",
    option: { name: "in-process", maxThroughput: 2_000, opsCostWeek: 1, exactlyOnce: false } },
  { kind: "considered", when: "2026-03-01", why: "черга як послуга",
    option: { name: "managed-queue", maxThroughput: 50_000, opsCostWeek: 3, exactlyOnce: false } },
  { kind: "considered", when: "2026-03-01", why: "стеля на виріст",
    option: { name: "kafka", maxThroughput: 1_000_000, opsCostWeek: 12, exactlyOnce: true } },
];

// 1. Здогад із наради — і набір «збігся» за один день
const f1: Fact = { id: "F1", says: "потрібна доставка «точно раз»", evidence: "здогад",
  source: "нарада, ніхто не перевіряв", when: "2026-03-02", holds: (o) => o.exactlyOnce };
const r1 = land(journal, f1);
if (r1.ok) journal = r1.journal;
console.log(verdict(replay(journal), "2026-03-03", DEADLINE));

// 2. Пішли й перевірили: вимога хибна → факт відкликано
journal = [...journal, { kind: "retracted", when: "2026-03-20", factId: "F1",
  why: "бізнес вимагає ідемпотентних споживачів, а не «точно раз»: TICKET-412" }];
console.log(replay(journal).alive.map((o) => o.name));   // набір розправився САМ

// 3-4. Тепер факти з доказами
const f2: Fact = { id: "F2", says: "пік навантаження 20 000 повідомлень/с", evidence: "виміряно",
  source: "прогін ходячого кістяка 2026-03-27, звіт LOAD-7",
  when: "2026-03-28", holds: (o) => o.maxThroughput >= 20_000 };
const r2 = land(journal, f2);
if (r2.ok) journal = r2.journal;
const f3: Fact = { id: "F3", says: "бюджет експлуатації — 5 год/тиждень", evidence: "документ",
  source: "прайс + рішення тимліда, DOC-31",
  when: "2026-04-10", holds: (o) => o.opsCostWeek <= 5 };
const r3 = land(journal, f3);
if (r3.ok) journal = r3.journal;
const st = replay(journal);
console.log(verdict(st, TODAY, DEADLINE));

// Що якби F3 так і не приземлився — питаємо минуле
console.log(verdict(replay(journal, "2026-04-01"), "2026-05-16", DEADLINE));

// 5. Хтось затягує межу «щоб напевно»
const f4: Fact = { id: "F4", says: "бюджет експлуатації — 2 год/тиждень", evidence: "здогад",
  source: "хотілося б", when: "2026-04-11", holds: (o) => o.opsCostWeek <= 2 };
const r4 = land(journal, f4);
if (!r4.ok) console.log(r4.why);

console.log(explain(st, "kafka"));
console.log(explain(st, "in-process"));
