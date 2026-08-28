type Kind = "compensatable" | "pivot" | "retriable";
type Dir  = "forward" | "back";

interface Ctx { homeId: string; idemKey: string }
interface Step {
  name: string; kind: Kind;
  run: (c: Ctx) => Promise<void>;
  compensate?: (c: Ctx) => Promise<void>;   // тільки у зворотних
}

// ВЕСЬ стан саги — персистентний рядок; на стеку не тримаємо нічого.
interface Saga {
  id: string; homeId: string;
  cursor: number;                            // індекс кроку, на якому стоїмо
  dir: Dir;                                  // forward | back
  status: "running" | "waiting" | "aborted" | "done" | "stuck";
  attempts: number;                          // повтори поточного повторюваного кроку
  deadline?: number;                         // строк людського очікування (awaitClaim)
}

interface Tx {}                              // ручка транзакції сховища
interface Ports {                            // усе, що машина пише у світ, — через ці дужки
  load(id: string): Promise<Saga>;
  persist(s: Saga): Promise<void>;           // звичайний тривкий запис стану
  txn<T>(fn: (tx: Tx) => Promise<T>): Promise<T>;   // ОДНА транзакція сховища
  seen(tx: Tx, key: string): Promise<boolean>;      // цей ключ уже застосовували?
  mark(tx: Tx, key: string): Promise<void>;
  saveIn(tx: Tx, s: Saga): Promise<void>;    // записати стан саги В ЦІЙ транзакції
  outbox(tx: Tx, ev: unknown): Promise<void>;// покласти подію в outbox В ЦІЙ транзакції
  alert(s: Saga, step: Step, err: unknown): Promise<void>;  // сигнал людині (DLQ)
}

// Порядок і є суть: усе зворотне ДО півота, усе обов'язкове — ПІСЛЯ.
// freeze, unfreeze, revokeOldKeys … — тонкі клієнти відповідних контекстів.
const STEPS: Step[] = [
  { name: "freeze",          kind: "compensatable", run: freeze,          compensate: unfreeze },
  { name: "revokeAccess",    kind: "compensatable", run: revokeOldKeys,   compensate: restoreOldKeys },
  { name: "awaitClaim",      kind: "compensatable", run: waitForNewOwner, compensate: cancelClaim },
  { name: "transferAndWipe", kind: "pivot",         run: transferAndShred },   // без compensate
  { name: "rebindDevices",   kind: "retriable",     run: reissueCerts },
  { name: "openBilling",     kind: "retriable",     run: switchBilling },
  { name: "welcome",         kind: "retriable",     run: notifyNewOwner },
];
const MAX_ATTEMPTS = 12;
