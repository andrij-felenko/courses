// Розкладаємо подію на НЕЗАЛЕЖНІ одиниці — по одній на підписника —
// і женемо їх пулом. Провал/зависання однієї не знає про інші.
async function fanOut(
  subscribers: { url: string; secret: string }[],
  payload: object,
  concurrency = 20,
): Promise<void> {
  const jobs = subscribers.map((s) => ({ ...newDeliveryJob(s.url, payload), secret: s.secret }));
  const queue = [...jobs];

  // Пул робітників: рівно `concurrency` доставок «у польоті» водночас.
  const workers = Array.from({ length: concurrency }, async () => {
    for (let job = queue.shift(); job; job = queue.shift()) {
      const signed = signWebhook(job.payload, job.secret);
      const ok = await deliverWithRetry(job.url, signed, job.deliveryId);
      if (!ok) await deadLetter(job);        // вичерпав спроби → у чергу мертвих листів
    }
  });

  await Promise.all(workers);  // мрець тримає СВОГО робітника; інші 19 не чекають
}
