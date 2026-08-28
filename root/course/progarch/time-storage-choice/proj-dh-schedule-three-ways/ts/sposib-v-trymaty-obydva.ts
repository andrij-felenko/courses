class ScheduleV {
  nextFireUtc: DateTime | null = null;          // КЕШ: похідна мить для індексу
  constructor(public time: string, public zone: string) {}  // ДЖЕРЕЛО ПРАВДИ: намір

  resolve(after: DateTime): void {
    // перекувати кеш із наміру за ЧИННИМИ правилами (той самий nextFireB)
    this.nextFireUtc = nextFireB(after, { time: this.time, zone: this.zone });
  }

  due(now: DateTime): boolean {
    // планувальник питає дешево, за готовою міттю — як у способі А
    return this.nextFireUtc !== null && this.nextFireUtc <= now;
  }
}

// ПІСЛЯ ОНОВЛЕННЯ tzdata — перекувати ВСІ ще не запущені розклади:
function onTzdataUpdate(schedules: ScheduleV[], now: DateTime): void {
  for (const s of schedules) s.resolve(now);    // ← без цього рядка В тихо стає А
}
