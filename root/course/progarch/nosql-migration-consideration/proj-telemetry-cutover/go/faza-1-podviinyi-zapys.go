// WriteReading пише спершу в старе (джерело правди), потім «як вийде» в нове.
// Збій нового НЕ валить запис користувача — прогалину дожене беквіл/звірка.
func (w *TelemetryWriter) WriteReading(ctx context.Context, r Reading) error {
    if err := w.old.Insert(ctx, r); err != nil {
        return err // старе не прийняло — це справжня помилка, повертаємо як є
    }
    if err := w.new.Upsert(ctx, r); err != nil {
        w.divergence.Inc() // лічильник розбіжності — під безперервним оком
        log.Warn("new-store write failed", "device", r.DeviceID, "ts", r.TS, "err", err)
        // навмисно НЕ повертаємо: нове ще не джерело правди
    }
    return nil
}
