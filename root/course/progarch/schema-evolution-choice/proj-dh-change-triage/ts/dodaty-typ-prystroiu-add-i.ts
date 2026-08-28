// ❌ читач, що вибухне на новому значенні:
function render(d: Device) {
  switch (d.type) {
    case "lamp":   return renderLamp(d);
    case "lock":   return renderLock(d);
    case "sensor": return renderSensor(d);
    default: throw new Error(`невідомий тип ${d.type}`);   // ← ev_charger = виняток
  }
}

// ✓ forward-сумісний: незнайоме ДЕГРАДУЄ, а не падає
function render(d: Device) {
  switch (d.type) {
    case "lamp":   return renderLamp(d);
    case "lock":   return renderLock(d);
    case "sensor": return renderSensor(d);
    default: return renderGeneric(d);   // показуємо як загальний пристрій
  }
}
