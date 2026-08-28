// одна формула небезпеки — єдине місце, де живе це знання
export function dangerLevel(zone: string, now = Date.now()): number {
  const base = ZONE_RISK[zone] ?? 0;
  return isNight(now) ? base + 1 : base;         // ← правило ночі тепер в ОДНОМУ місці
}

// три користувачі кличуть ту саму формулу:
// notifyMotion:
text += ` — небезпека ${dangerLevel(ev.zone)}`;
// notifyOffline:
const channels = dangerLevel(ev.zone) >= 2 ? ["sms", "push"] : ["push"];
// armZone:
if (dangerLevel(zone) >= 2) requireSecondConfirm(zone);
