import { DateTime } from "luxon";

// А: рахуємо мить ЗАРАЗ, за сьогоднішнім зсувом, і морозимо її.
function freezeUtc(local: string, zone: string): DateTime {
  return DateTime.fromISO(local, { zone }).toUTC();   // 07:00 Києва → 05:00Z (взимку +02:00)
}

const frozen = freezeUtc("2026-01-10T07:00", "Europe/Kyiv");   // 2026-01-10T05:00:00Z

// щоденне спрацювання: та сама година UTC, +24 години щодня
function nextFireA(after: DateTime): DateTime {
  let fire = frozen;
  while (fire <= after) fire = fire.plus({ days: 1 });   // на UTC-зоні days=1 і є рівно 24 год
  return fire;
}
