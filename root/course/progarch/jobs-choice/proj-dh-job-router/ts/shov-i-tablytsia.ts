// ── ОДИН ШОВ + таблиця маршрутів (ЄДИНЕ місце, де клас зустрічає субстрат) ──
function makeSystem() {
  const db     = new Db();
  const broker = new Broker();
  const dbQueue = new DbQueue(db);
  const outbox  = new OutboxBridge(db, broker);

  const route: Record<JobClass, Substrate> = {
    cacheWarm:    new MemoryQueue(),  // втратне — хай гине на рестарті
    transcode:    dbQueue,            // народжене із записом кліпа → атомарно в тій же транзакції
    notify:       dbQueue,            // теж із бізнес-запису → дефолт
    report:       dbQueue,            // cron кладе сюди ж (без tx — свій)
    fleetRollout: outbox,             // корінець у базі атомарно, relay розсіює в брокер
    telemetry:    broker,             // потік із пристроїв — не для гарячої таблиці jobs
  };

  const enqueue = (job: Job, tx?: Tx): void => { route[job.cls].put(job, tx); };
  return { db, broker, outbox, route, enqueue };   // виклику байдуже, який субстрат унизу
}
