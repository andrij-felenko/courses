// НАЇВНО: прочитали рядок, змінили, записали назад. Гонка ховається саме тут.
async function applyNaive(db: Db, homeId: string, cmd: Cmd): Promise<void> {
  const row = await db.get("device_state", homeId);          // read  (version = 5)
  row.bolt = cmd.kind === "lock" ? "locked" : "unlocked";    // modify
  row.version += 1;                                          //        (5 → 6)
  row.lastCmd = `${cmd.by}#${cmd.seq}`;
  await db.put("device_state", homeId, row);                 // write (version = 6)
}
// дві такі команди водночас: ОБИДВІ прочитали version=5, ОБИДВІ пишуть version=6.
// друга затерла першу — «загублене оновлення». version=6, а команд було дві.
