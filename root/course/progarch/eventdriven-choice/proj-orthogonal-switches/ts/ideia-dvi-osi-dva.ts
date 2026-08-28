// ── Спільний домен: команда → факт, і згортка факту в стан ──
type LockState = { locked: boolean; lastActor: string | null; at: number };
const INITIAL: LockState = { locked: false, lastActor: null, at: 0 };

type Command =
  | { kind: "lock";   actor: string; at: number }
  | { kind: "unlock"; actor: string; at: number };

// подія — доконаний ФАКТ (те, що вже сталося), а не наказ
type DoorEvent =
  | { type: "DoorLocked";   actor: string; at: number }
  | { type: "DoorUnlocked"; actor: string; at: number };

// доменне правило: команда обертається на факт (або відкидається)
function decide(s: LockState, c: Command): DoorEvent {
  if (c.kind === "lock"   && s.locked)  throw new Error("вже зачинено");
  if (c.kind === "unlock" && !s.locked) throw new Error("вже відчинено");
  return c.kind === "lock"
    ? { type: "DoorLocked",   actor: c.actor, at: c.at }
    : { type: "DoorUnlocked", actor: c.actor, at: c.at };
}

// згортка: факт зсуває стан на один крок
function apply(s: LockState, e: DoorEvent): LockState {
  return e.type === "DoorLocked"
    ? { locked: true,  lastActor: e.actor, at: e.at }
    : { locked: false, lastActor: e.actor, at: e.at };
}
