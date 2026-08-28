// Один шов постановки: усе йде через enqueue(),
// а куди задача фізично ляже — вирішує маршрут за КЛАСОМ роботи.
const route: Record<JobClass, Substrate> = {
  cacheWarm:    memory,   // втратне — хай гине на рестарті
  transcode:    dbQueue,  // народжене із записом кліпа → атомарно в тій же транзакції
  notify:       dbQueue,  // теж із бізнес-запису → дефолт
  report:       dbQueue,  // cron кладе сюди ж
  fleetRollout: broker,   // переріс базу: фан-аут на тисячі, throttle+DLQ з коробки
  telemetry:    broker,   // потік із пристроїв — не для гарячої таблиці jobs
};

function enqueue(job: Job) {
  return route[job.cls].put(job);   // виклику байдуже, який субстрат унизу
}
