// ВЕРСІЯ РЯДКА (оптимістично): запис проходить, лише якщо version та сама, що прочитали
async function applyCas(db: Db, homeId: string, cmd: Cmd): Promise<void> {
  for (;;) {
    const row = await db.get("device_state", homeId);
    const changed = await db.update("device_state", {
      where: { homeId, version: row.version },               // ← умова CAS
      set: {
        bolt: cmd.kind === "lock" ? "locked" : "unlocked",
        version: row.version + 1,
        lastCmd: `${cmd.by}#${cmd.seq}`,
      },
    });
    if (changed === 1) return;        // ми виграли — рівно ми бумкнули version
    // changed === 0: хтось інший бумкнув version між нашим read і write → повторити
  }
}
