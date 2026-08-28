// НЕ РОБИМО так — JOIN через стіну зшиває схеми навіки:
//   SELECT d.*, r.value FROM control.device d
//   JOIN telemetry.reading r ON r.device_id = d.id     ← заборонено

// РОБИМО так — читання-композиція через два фасади:
function deviceCard(id: DeviceId): DeviceCard {
  const device = control.getDevice(id);        // свій фасад control
  const last = telemetry.lastReading(id);       // свій фасад telemetry
  return { ...device, lastReading: last };      // склеюємо вже в читачі
}
