// Хаб і хмара котяться нарізно. Тому читач ТЕРПЛЯЧИЙ:
// невідомі поля ігнорує, відсутні — підставляє за замовчуванням.
function fromWire(raw: any): CloudDevice {
  return new CloudDevice(
    raw.id,
    raw.type      ?? "unknown",
    raw.room      ?? "?",
    raw.state     ?? "unknown",
    raw.brightness ?? 0,
    raw.lastSeen  ?? 0,
    // raw.signal (нове поле v2) старий читач просто НЕ помічає — і не падає
  );
}
