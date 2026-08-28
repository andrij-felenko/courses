{ // Доказ 1: реєстр переживає рестарт
  const path = tmpFile();
  const reg1 = connect(path, "FULL");            // перший «запуск»
  runMigrations(reg1);
  new SqliteDeviceRepository(reg1).saveHome({
    id: "h1", ownerId: "ada", plan: "free", deviceCap: 5, threshold: 21.0, usedSlots: 0,
    devices: [{ id: "lock-1", kind: "lock", room: "двері", state: "Locked", pairedAt: "…" },
              { id: "plug-2", kind: "plug", room: "кухня", state: "On",     pairedAt: "…" }],
  });
  reg1.close();                                  // ← процес помер

  const reg2 = connect(path, "FULL");            // другий «запуск» над тим самим файлом
  assert.strictEqual(runMigrations(reg2), 2);    // ідемпотентно: накочувати нема чого
  const home = new SqliteDeviceRepository(reg2).load("h1")!;
  assert.strictEqual(home.threshold, 21.0);
  assert.deepStrictEqual(new Set(home.devices.map(d => d.id)), new Set(["lock-1", "plug-2"]));
}
