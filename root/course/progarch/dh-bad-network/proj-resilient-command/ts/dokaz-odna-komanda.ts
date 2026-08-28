import assert from "node:assert/strict";

async function proveExactlyOnce() {
  let executions = 0;
  const execute = async (_cmd: Command): Promise<Result> => {
    executions += 1;              // рахуємо КОЖНЕ справжнє виконання
    await sleep(50);              // «робота» триває — саме поки летять повтори
    return { ok: true, ranAt: executions };
  };

  const hub = new IdempotentExecutor(execute);
  const key = "unlock-front-7f3"; // ОДИН ключ на всі повтори однієї команди
  const cmd: Command = { type: "unlock", door: "front" };

  // Хвиля 1: 10 ОДНОЧАСНИХ повторів — гонка на in-flight.
  const wave1 = await Promise.all(
    Array.from({ length: 10 }, () => hub.handle(key, cmd)),
  );
  // Хвиля 2: ще 5 повторів ПІСЛЯ завершення — влучають у пам'ять про завершене.
  const wave2 = await Promise.all(
    Array.from({ length: 5 }, () => hub.handle(key, cmd)),
  );

  const all = [...wave1, ...wave2];
  assert.equal(executions, 1, `мало бути рівно одне виконання, а було ${executions}`);
  assert.ok(all.every((r) => r === all[0]), "усі 15 повторів — той самий результат");
  console.log(`✓ 15 повторів (10 одночасних + 5 пізніх) → виконань: ${executions}`);
}

proveExactlyOnce();
