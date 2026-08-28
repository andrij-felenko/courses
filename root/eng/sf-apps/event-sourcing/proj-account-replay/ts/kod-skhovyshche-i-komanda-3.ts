// Повторюємо команду, доки її не приймуть або доки правило не відмовить остаточно.
function withdrawWithRetry(store: EventStore, streamId: string, amount: number,
                           tries = 5): boolean {
  for (let i = 0; i < tries; i++) {
    const history = store.read(streamId);
    if (amount > foldState(history).balance) return false;   // правило проти СВІЖОГО стану
    if (withdraw(store, streamId, amount)) return true;      // прийнято
    // інакше — конфлікт версій, крутимо ще раз зі свіжим журналом
  }
  throw new Error("забагато конкурентних записів — здаюся");
}
