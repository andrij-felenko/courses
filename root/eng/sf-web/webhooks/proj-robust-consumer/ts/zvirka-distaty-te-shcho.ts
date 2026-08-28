const OVERLAP_MS = 10 * 60 * 1000;   // перекрити вікно на 10 хв — щоб не проґавити межу

async function reconcile() {
  const cursor = await loadCursor("payments");
  const since = cursor - OVERLAP_MS;                       // навмисно тягнемо ширше
  let maxSeen = cursor;

  for await (const event of provider.listEvents({ since })) {   // посторінково з чужого API
    const raw = Buffer.from(JSON.stringify(event));
    if (await inboxInsert(event.id, event.type, raw)) {
      await enqueue(event.id);          // цієї події ми не бачили — провайдер її облишив
    }                                   // бачили — insert віддав false, тихо пропускаємо
    maxSeen = Math.max(maxSeen, event.created * 1000);
  }
  await saveCursor("payments", maxSeen);                   // зрушуємо курсор уперед
}
