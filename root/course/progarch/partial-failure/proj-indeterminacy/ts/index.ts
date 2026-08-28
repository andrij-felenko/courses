// Стенд (Hub, Link, clientUnlock) — прямий переклад Go (в однопотоковому рантаймі — без мьютекса).
// Наївний повтор: таймаут → ще раз. Небезпечно — таймаут ≠ «не виконалось».
async function naiveRetry(link: Link, hub: Hub, patienceMs: number, tries: number) {
  for (let i = 0; i < tries; i++) {
    try {
      await clientUnlock(link, hub, patienceMs); // чекаємо ack або таймаут
      return;                                    // почули «ok» — виходимо
    } catch {
      // таймаут. Не чіпали — чи вже відчинили, а ack зник? Невідомо.
      // Якщо відчинили — цей повтор смикне реле ВДРУГЕ.
    }
  }
  throw new Error("вичерпано спроби");
}

const hub = new Hub();
const link = new Link(["dropAck"]);              // збій раз, тоді канал чистий
await naiveRetry(link, hub, 100, 3);
console.log(`клієнт: успіх | реле смикнулось: ${hub.fires}`); // → 2
