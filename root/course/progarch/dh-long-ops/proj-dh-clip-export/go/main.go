// Робітник у контексті Відео: забрати, тримати оренду, урвати за згодою, закрити чесно.
const (
	leaseTTL  = 30 * time.Second
	beatEvery = 10 * time.Second // втричі частіше за оренду → переживе один пропуск серцебиття
	hardCap   = 5 * time.Minute
	maxTries  = 3
)

func (w *Worker) runOne(parent context.Context) (bool, error) {
	op, ok, err := w.store.Claim(parent, w.id, leaseTTL) // атомарний SELECT…SKIP LOCKED + UPDATE
	if err != nil || !ok {
		return false, err // черга порожня — піти поспати
	}
	if op.Attempt > maxTries { // падало забагато разів — закриваємо чесною помилкою
		w.store.Finish(parent, op.ID, op.LeaseID, "failed", nil, &OpError{Code: "too_many_attempts"})
		return true, nil
	}

	// Тверда стеля тривалості на МОНОТОННОМУ годиннику: WithTimeout рахує від time.Now(),
	// таймер рантайму глухий до стрибків настінного часу й корекцій NTP.
	ctx, cancel := context.WithTimeout(parent, hardCap)
	defer cancel()

	// Серцебиття у власній горутині — ЗА ГОДИННИКОМ, не між шматками: подовжує оренду,
	// несе поступ і саме воно ловить фенс.
	var progress atomic.Int64
	beat := time.NewTicker(beatEvery)
	defer beat.Stop()
	go func() {
		for {
			select {
			case <-ctx.Done():
				return
			case <-beat.C:
				mine, _ := w.store.Heartbeat(ctx, op.ID, op.LeaseID, int(progress.Load()), leaseTTL)
				if !mine { // 0 рядків → нас перехопили (у рядку інший lease_id) → фенс
					cancel() // рвемо ctx — головний цикл побачить це на межі шматка
					return
				}
			}
		}
	}()

	for _, chunk := range planChunks(op.Request) {
		select {
		case <-ctx.Done(): // стеля часу, фенс або зупинка процесу — НЕ пишемо succeeded
			return true, nil
		default:
		}
		if canceled, _ := w.store.CancelRequested(ctx, op.ID); canceled {
			w.store.Finish(ctx, op.ID, op.LeaseID, "canceled", nil, nil)
			return true, nil
		}
		if err := transcode(ctx, chunk); err != nil {
			return true, err // не пишемо failed самі: відпускаємо — оренда згасне, задачу заберуть знову
		}
		progress.Store(int64(chunk.Percent)) // атомарно — серцебиття прочитає свіже число
	}

	// Результат — у об'єктне сховище; у рядок — лише підписане тимчасове посилання.
	key := "clips/" + op.ID + ".mp4" // ДЕТЕРМІНОВАНИЙ ключ → повторний рендер перезапише той самий об'єкт
	if err := w.objects.Put(ctx, key, renderedBytes(op.ID)); err != nil {
		return true, err
	}
	url := w.objects.SignedURL(key, 15*time.Minute) // підпис діє 15 хв
	result := &OpResult{URL: url, ExpiresAt: time.Now().Add(15 * time.Minute)}

	// Finish із ФЕНСОМ (WHERE lease_id = наш): якщо нас перехопили — запис відкинуть, пуш не піде.
	if done, _ := w.store.Finish(ctx, op.ID, op.LeaseID, "succeeded", result, nil); done {
		w.notify.ClipReady(op.UserID, op.ID) // штовх пушу ЛИШЕ якщо ми справді закрили операцію
	}
	return true, nil
}
