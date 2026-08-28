const overlap = 10 * time.Minute   // перекрити вікно — щоб не проґавити межу

func reconcile(ctx context.Context) error {
    cursor := loadCursor("payments")
    since := cursor.Add(-overlap)                            // навмисно тягнемо ширше
    maxSeen := cursor

    events, err := provider.ListEvents(ctx, since)           // посторінково з чужого API
    if err != nil {
        return err
    }
    for _, event := range events {
        raw, _ := json.Marshal(event)
        isNew, err := inboxInsert(ctx, event.ID, event.Type, raw)
        if err != nil {
            return err
        }
        if isNew {
            enqueue(event.ID)            // цієї події ми не бачили — провайдер її облишив
        }
        if t := time.Unix(event.Created, 0); t.After(maxSeen) {
            maxSeen = t
        }
    }
    saveCursor("payments", maxSeen)                          // зрушуємо курсор уперед
    return nil
}
