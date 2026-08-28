// Намір розкладу — правило+зона, а не застиглий момент.
type Schedule = { atLocal: string; zone: string };   // { "02:00", "Europe/Kyiv" }

// Вікно «вчора» = від локальної півночі до локальної півночі, у UTC-інстантах.
// Дві сусідні локальні півночі самі дають 23/24/25 год — DST враховано за побудовою.
function yesterdayWindow(zone: string, now: Temporal.ZonedDateTime) {
  const startLocal = now.withTimeZone(zone).startOfDay().subtract({ days: 1 });
  const endLocal   = startLocal.add({ days: 1 });      // наступна локальна північ
  return { fromUtc: startLocal.toInstant(), toUtc: endLocal.toInstant() };
}

// Задача ідемпотентна за (дім, доба): другий запуск ПЕРЕПИШЕ, а не додасть.
async function aggregateDay(homeId: string, day: string, w: Window) {
  const rows = await telemetry.readBetween(homeId, w.fromUtc, w.toUtc);   // виміри-інстанти
  const summary = rollUp(rows);                        // сума, макс, мінімум за добу
  await dailySummary.upsert({ homeId, day }, summary); // ключ (дім, доба) — не append
}
