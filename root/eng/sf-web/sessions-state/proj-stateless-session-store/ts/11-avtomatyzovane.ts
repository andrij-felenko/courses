import { StatelessRedisSessionStore, mutateSessionWithRetry } from "./sessionStore";
import Redis from "ioredis";

async function runConcurrencyTest() {
  const redis = new Redis();
  const store = new StatelessRedisSessionStore(redis);

  // Створюємо початкову сесію з порожнім списком товарів
  const session = await store.create({ items: [] });
  const sessionId = session.id;

  const CONCURRENT_REQUESTS = 20;

  // Запускаємо 20 паралельних воркерів, кожен з яких додає свій унікальний товар
  const tasks = Array.from({ length: CONCURRENT_REQUESTS }, (_, i) =>
    mutateSessionWithRetry(store, sessionId, (data) => {
      const items = (data.items as string[]) || [];
      return {
        ...data,
        items: [...items, `item_${i + 1}`],
      };
    })
  );

  await Promise.all(tasks);

  // Перевіряємо фінальний стан сесії в Redis
  const finalSession = await store.get(sessionId);
  const items = (finalSession?.data.items as string[]) || [];

  console.log(`Очікувалось товарів: ${CONCURRENT_REQUESTS}, фактично в сесії: ${items.length}`);
  console.log(`Фінальна версія сесії: ${finalSession?.version}`);

  if (items.length === CONCURRENT_REQUESTS) {
    console.log("ТЕСТ ПРОЙДЕНО: жоден товар не було втрачено завдяки CAS-повторам!");
  } else {
    console.error("ТЕСТ ПРОВАЛЕНО: виявлено втрачені оновлення (Lost Updates)!");
  }

  await store.destroy(sessionId);
  await redis.quit();
}
