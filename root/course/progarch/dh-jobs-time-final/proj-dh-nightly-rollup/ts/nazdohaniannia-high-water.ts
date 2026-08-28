type MissPolicy = "skip" | "catchup" | "coalesce";

// Локальні доби, ще НЕ згорнуті: інтервал (lastDone, сьогодні), обидва кінці виключно.
function dueDays(zone: string, lastDoneIso: string): Temporal.PlainDate[] {
  const today = Temporal.Now.zonedDateTimeISO(zone).toPlainDate();
  const days: Temporal.PlainDate[] = [];
  let cur = Temporal.PlainDate.from(lastDoneIso).add({ days: 1 });  // перша НЕзгорнута
  while (Temporal.PlainDate.compare(cur, today) < 0) {             // строго ДО «сьогодні»
    days.push(cur);
    cur = cur.add({ days: 1 });        // чиста календарна арифметика — DST тут не живе
  }
  return days;
}

// Політика вирішує, ЩО робити з провалом у кілька діб.
function applyPolicy(days: Temporal.PlainDate[], p: MissPolicy): Temporal.PlainDate[] {
  if (days.length <= 1 || p === "catchup") return days;   // усі по черзі
  if (p === "skip") return days.slice(-1);                // лише найсвіжіша, решта — дірки
  return days;                            // coalesce: усі, але далі зіллються в ОДНЕ вікно
}
