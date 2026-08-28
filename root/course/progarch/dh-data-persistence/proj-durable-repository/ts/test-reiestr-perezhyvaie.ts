import { test } from "node:test";
import assert from "node:assert";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

for (const kind of ["file", "sqlite"] as const) {
  test(`реєстр переживає рестарт (${kind})`, () => {
    const dir = mkdtempSync(join(tmpdir(), "dh-"));
    const open = () =>                            // відкрити репозиторій над тим самим шляхом
      kind === "file"
        ? new FileDeviceRepository(join(dir, "dh-devices.json"))
        : new SqliteDeviceRepository(join(dir, "dh.db"));

    let repo = open();
    repo.save({ id: "lock-1", kind: "lock", room: "вхідні двері", state: "unknown" });
    repo.save({ id: "plug-2", kind: "plug", room: "кухня", state: "unknown" });

    repo = open();                               // ← «смерть процесу»: новий обʼєкт, стара RAM стерта

    const ids = new Set(repo.all().map((d) => d.id));
    assert.deepStrictEqual(ids, new Set(["lock-1", "plug-2"]));   // реєстр уцілів
    assert.strictEqual(repo.get("plug-2")!.room, "кухня");        // і поля на місці
  });
}
