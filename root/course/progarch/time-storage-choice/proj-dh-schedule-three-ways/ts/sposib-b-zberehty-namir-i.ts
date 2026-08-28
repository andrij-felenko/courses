// Б: зберігаємо НАМІР — стінний час + назву зони. Мить рахуємо в останню секунду.
const schedule = { time: "07:00", zone: "Europe/Kyiv" };

function nextFireB(after: DateTime, sched: { time: string; zone: string }): DateTime {
  const [hh, mm] = sched.time.split(":").map(Number);
  let day = after.setZone(sched.zone).startOf("day");
  for (;;) {
    // 07:00 у зоні, зібране ЗА ЧИННИМ tzdata саме на цей день
    const fire = day.set({ hour: hh, minute: mm }).toUTC();
    if (fire > after) return fire;
    day = day.plus({ days: 1 });
  }
}
