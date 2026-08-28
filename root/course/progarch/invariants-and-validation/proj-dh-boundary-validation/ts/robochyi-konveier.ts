// ── Хребет: результат — це значення, успіх АБО помилка, ніколи не виняток ──
type Ok<T>  = { ok: true;  value: T };
type Err<E> = { ok: false; error: E };
type Result<T, E> = Ok<T> | Err<E>;

const ok  = <T>(value: T): Result<T, never> => ({ ok: true,  value });
const err = <E>(error: E): Result<never, E> => ({ ok: false, error });

// ── Об'єкти-значення: у кожного єдині двері — parse(), інших немає ──
class DeviceId {
  private constructor(readonly value: string) {}
  static parse(raw: unknown): Result<DeviceId, string> {
    if (typeof raw !== "string")   return err("очікувано рядок");
    if (raw.length === 0)          return err("порожній");
    if (raw.length > 32)           return err("задовгий (>32)");
    if (!/^[a-z0-9-]+$/.test(raw))  return err("лише a–z, 0–9 та дефіс");
    return ok(new DeviceId(raw));
  }
}

// Той самий Celsius, що в статті: число в межах кімнатного давача, −50…80.
class Celsius {
  private constructor(readonly value: number) {}
  static parse(raw: unknown): Result<Celsius, string> {
    if (typeof raw !== "number" || Number.isNaN(raw)) return err("не число");
    if (raw < -50 || raw > 80)  return err(`поза межами −50…80: ${raw}`);
    return ok(new Celsius(raw));
  }
}

// Action — тип-сума: рівно один із трьох режимів, і нічого «поміж».
type Action = "heat" | "cool" | "off";
const ACTIONS = ["heat", "cool", "off"] as const;
function parseAction(raw: unknown): Result<Action, string> {
  if (typeof raw !== "string")
    return err("очікувано рядок");
  if (!(ACTIONS as readonly string[]).includes(raw))
    return err(`невідома дія «${raw}»; дозволені: ${ACTIONS.join(", ")}`);
  return ok(raw as Action);
}
