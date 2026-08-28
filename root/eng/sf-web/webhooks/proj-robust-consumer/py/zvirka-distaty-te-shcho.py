OVERLAP = timedelta(minutes=10)   # перекрити вікно — щоб не проґавити межу

def reconcile():
    cursor = load_cursor("payments")
    since = cursor - OVERLAP                                  # навмисно тягнемо ширше
    max_seen = cursor

    for event in provider.list_events(since=since):          # посторінково з чужого API
        raw = json.dumps(event).encode()
        if inbox_insert(event["id"], event["type"], raw):
            enqueue(event["id"])         # цієї події ми не бачили — провайдер її облишив
        # бачили — inbox_insert віддав False, тихо пропускаємо
        max_seen = max(max_seen, datetime.fromtimestamp(event["created"], tz=timezone.utc))
    save_cursor("payments", max_seen)                        # зрушуємо курсор уперед
