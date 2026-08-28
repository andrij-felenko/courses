# Повторюємо команду, доки її не приймуть або доки правило не відмовить остаточно.
def withdraw_with_retry(store: EventStore, stream_id: str, amount: float,
                        tries: int = 5) -> bool:
    for _ in range(tries):
        history = store.read(stream_id)
        if amount > fold_state(history).balance:
            return False                          # правило проти СВІЖОГО стану
        if withdraw(store, stream_id, amount):
            return True                           # прийнято
        # інакше — конфлікт версій, крутимо ще раз зі свіжим журналом
    raise RuntimeError("забагато конкурентних записів — здаюся")
