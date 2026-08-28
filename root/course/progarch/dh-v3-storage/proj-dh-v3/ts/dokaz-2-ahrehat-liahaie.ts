{ // Доказ 2: агрегат лягає весь або ніяк
  const path = tmpFile();
  const reg = connect(path, "FULL"); runMigrations(reg);
  const repo = new SqliteDeviceRepository(reg);

  repo.saveHome({ id: "h1", ownerId: "ada", plan: "free", deviceCap: 5, threshold: 21.0,
    usedSlots: 0, devices: [{ id: "lock-1", kind: "lock", room: "двері", state: "Locked", pairedAt: "t0" }] });

  const poisoned = { id: "h1", ownerId: "ada", plan: "free", deviceCap: 5, threshold: 24.0, usedSlots: 0,
    devices: [{ id: "plug-2", kind: "plug", room: "кухня", state: "On", pairedAt: "t1" },   // добрий
              { id: "bad-3", kind: "???", room: "гараж", state: "On", pairedAt: "t2" }] };   // ЛАМАЄ CHECK

  assert.throws(() => repo.saveHome(poisoned));      // поганий пристрій підриває транзакцію

  const survivor = repo.load("h1")!;
  assert.strictEqual(survivor.threshold, 21.0);      // ← поріг НЕ змінився
  assert.deepStrictEqual(new Set(survivor.devices.map(d => d.id)), new Set(["lock-1"]));  // plug-2 зник
}
