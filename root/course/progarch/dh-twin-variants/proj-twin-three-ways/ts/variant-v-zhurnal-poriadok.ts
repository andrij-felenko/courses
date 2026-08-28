type Event = { type: "Locked" | "Unlocked"; seq: number; by: string };

// ЗАПИС: дописати факт. Лог сам присвоює позицію — вона й є порядок.
async function record(log: Log, homeId: string, cmd: Cmd): Promise<void> {
  await log.append(homeId, {
    type: cmd.kind === "lock" ? "Locked" : "Unlocked",
    seq: cmd.seq, by: cmd.by,
  });                                  // durable: fsync до підтвердження
}

// ЧИТАННЯ: поточний стан = згортка журналу. «Як зараз» рахуємо, а не зберігаємо.
function apply(s: LockState, e: Event): LockState {
  return {
    bolt: e.type === "Locked" ? "locked" : "unlocked",
    version: s.version + 1,
    lastCmd: `${e.by}#${e.seq}`,
  };
}
function project(events: Event[]): LockState {
  return events.reduce(apply, INITIAL);
}
