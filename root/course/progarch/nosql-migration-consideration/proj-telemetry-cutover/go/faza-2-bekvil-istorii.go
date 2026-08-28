// Партиції беквілимо кількома робітниками: серійний темп 260 млрд рядків не витягне,
// але старе сховище не можна затопити — ширина пулу = скільки паралельного читання
// воно стерпить, лишивши смугу живому трафіку.
func runBackfill(ctx context.Context, parts []Partition, workers int) {
    sem := make(chan struct{}, workers)
    var wg sync.WaitGroup
    for _, p := range parts {
        if checkpoint.Done(p.ID) {   // партицію вже добито — пропускаємо (ідемпотентність і тут)
            continue
        }
        wg.Add(1)
        sem <- struct{}{}
        go func(p Partition) {
            defer wg.Done()
            defer func() { <-sem }()
            if err := backfillPartition(ctx, p); err != nil {
                log.Error("backfill failed", "part", p.ID, "err", err) // впав — просто перезапустять
            }
        }(p)
    }
    wg.Wait()
}

// Одна партиція: курсор із чекпойнта, читаємо з репліки, пишемо ідемпотентно,
// чекпойнт рухаємо ПІСЛЯ успішного запису.
func backfillPartition(ctx context.Context, p Partition) error {
    last := checkpoint.Load(p.ID)
    for {
        rows, err := oldReplica.ReadBatch(ctx, p, last, batchSize, ltTS(T0))
        if err != nil {
            return err
        }
        if len(rows) == 0 {
            break
        }
        if err := newStore.UpsertMany(ctx, rows); err != nil {
            return err // впали до чекпойнта — повтор пачки безпечний
        }
        last = rows[len(rows)-1].Key      // (device_id, ts)
        checkpoint.Save(p.ID, last)       // рухаємо курсор лише після запису
    }
    return checkpoint.MarkDone(ctx, p.ID)
}
