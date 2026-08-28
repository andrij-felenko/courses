// ── Довірений доменний об'єкт. Кожне поле — вже перевірений тип. ──
type Command = {
  readonly deviceId: DeviceId;
  readonly target:   Celsius;
  readonly action:   Action;
};
type FieldError = { field: string; message: string };

function parseCommand(body: string): Result<Command, FieldError[]> {
  // 1. РОЗБІР ФОРМИ: чи це взагалі JSON-об'єкт?
  let root: unknown;
  try {
    root = JSON.parse(body);              // єдиний throw у всьому конвеєрі — тут і ловимо
  } catch {
    return err([{ field: "(корінь)", message: "не валідний JSON" }]);
  }
  if (typeof root !== "object" || root === null || Array.isArray(root))
    return err([{ field: "(корінь)", message: "очікувано об'єкт" }]);
  const obj = root as Record<string, unknown>;

  // 2. РОЗБІР ПОЛІВ: кожне — незалежно, у свій Result. Жодного throw.
  const id     = DeviceId.parse(obj.deviceId);
  const target = Celsius.parse(obj.targetTemp);
  const action = parseAction(obj.action);

  // 3. АГРЕГАЦІЯ + РОЗВИЛКА: є Err — вертаємо ВЕСЬ список; усі Ok — падаємо нижче.
  if (!id.ok || !target.ok || !action.ok) {
    const errors: FieldError[] = [];
    if (!id.ok)     errors.push({ field: "deviceId",   message: id.error });
    if (!target.ok) errors.push({ field: "targetTemp", message: target.error });
    if (!action.ok) errors.push({ field: "action",     message: action.error });
    return err(errors);
  }

  // 4. СКЛАДАННЯ: сюди компілятор пускає ЛИШЕ коли всі три звузилися до Ok.
  return ok({ deviceId: id.value, target: target.value, action: action.value });
}
