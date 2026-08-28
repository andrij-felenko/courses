import { test } from "node:test";
import assert from "node:assert/strict";

test("валідний вхід → довірена команда", () => {
  const r = parseCommand('{"deviceId":"kitchen-1","targetTemp":21.5,"action":"heat"}');
  assert.ok(r.ok);                                   // розбір удався
  assert.equal(r.value.deviceId.value, "kitchen-1"); // .value — бо тип уже DeviceId
  assert.equal(r.value.target.value, 21.5);
  assert.equal(r.value.action, "heat");
});

test("три хиби одразу → ПОВНИЙ список, не перша-ліпша", () => {
  const r = parseCommand('{"deviceId":"","targetTemp":2000,"action":"melt"}');
  assert.ok(!r.ok);
  assert.equal(r.error.length, 3);                   // усі три, а не одна
  assert.deepEqual(r.error.map(e => e.field).sort(),
                   ["action", "deviceId", "targetTemp"]);
});

test("часткова валідність → команди НЕ існує зовсім", () => {
  const r = parseCommand('{"deviceId":"kitchen-1","targetTemp":2000,"action":"heat"}');
  assert.ok(!r.ok);                                  // два добрі поля НЕ рятують третє
  assert.equal(r.error.length, 1);
  assert.equal(r.error[0].field, "targetTemp");
});

test("не JSON → одна помилка форми, БЕЗ винятку назовні", () => {
  const r = parseCommand("{зламано");
  assert.ok(!r.ok);
  assert.equal(r.error[0].field, "(корінь)");        // throw від JSON.parse спіймано всередині
});
