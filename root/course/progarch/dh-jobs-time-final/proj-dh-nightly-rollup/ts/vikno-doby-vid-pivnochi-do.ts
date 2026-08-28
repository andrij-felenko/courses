// Temporal — стандарт ES2026, у Node 26 доступний без прапорців.
type Window = { fromUtc: Temporal.Instant; toUtc: Temporal.Instant; hours: number };

// Вікно однієї ЛОКАЛЬНОЇ доби `date` у зоні `zone`, у UTC-інстантах.
// startOfDay() дає ПЕРШУ наявну мить доби — тож зона, що колись переводила
// стрілки опівночі (і 00:00 не існувало), врахована сама, без «if DST».
function localDayWindow(zone: string, date: Temporal.PlainDate): Window {
  const start = date.toZonedDateTime(zone).startOfDay();
  const end   = date.add({ days: 1 }).toZonedDateTime(zone).startOfDay();
  const hours = start.until(end, { largestUnit: "hour" }).hours;
  return { fromUtc: start.toInstant(), toUtc: end.toInstant(), hours };
}

// «Вчора» для дому — попередня локальна доба відносно поточної миті в його зоні.
function yesterday(zone: string): Temporal.PlainDate {
  return Temporal.Now.zonedDateTimeISO(zone).toPlainDate().subtract({ days: 1 });
}
