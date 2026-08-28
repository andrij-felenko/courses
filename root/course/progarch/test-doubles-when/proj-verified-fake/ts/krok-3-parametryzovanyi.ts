import { test } from "node:test";
import assert from "node:assert/strict";

// фабрика на кожну реалізацію — набір нижче про них нічого більше не знає
const impls: { name: string; make: () => ReadingStore }[] = [
  { name: "InMemoryStore", make: () => new InMemoryStore() },
  { name: "SqliteStore",   make: () => new SqliteStore() },
];

for (const { name, make } of impls) {
  test(`[${name}] save-then-recent повертає покладене`, () => {
    const s = make();
    s.save({ at: 1000, celsius: 20 });
    assert.deepEqual(s.recent(10), [{ at: 1000, celsius: 20 }]);
  });

  test(`[${name}] recent(n) — n найсвіжіших, найсвіжіше перше`, () => {
    const s = make();
    for (const at of [3000, 1000, 2000]) s.save({ at, celsius: at / 100 });  // БЕЗЛАДНО
    assert.deepEqual(s.recent(2).map(r => r.at), [3000, 2000]);
  });
}
