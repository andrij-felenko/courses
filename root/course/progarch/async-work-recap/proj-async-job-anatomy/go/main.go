const leaseSeconds = 30                 // оренда клейма: довше за очікуваний прогін
const base, cap = 2.0, 3600.0           // відступ: база 2 c, стеля — година

// full jitter (Marc Brooker, AWS, 2015): рівномірно [0, стеля), а не рівний крок
func backoff(attempts int) float64 {
	ceiling := math.Min(cap, base*math.Pow(2, float64(attempts)))
	return rand.Float64() * ceiling
}

func worker(ctx context.Context, db *sql.DB, run Handler) {
	for ctx.Err() == nil {
		job, err := claim(ctx, db, leaseSeconds)     // атомарний UPDATE ... SKIP LOCKED
		if err != nil || job == nil {
			time.Sleep(500 * time.Millisecond)       // черга без готових — перепочити
			continue
		}
		if err := run(ctx, job.Payload); err != nil {
			fail(ctx, db, job.ID, backoff(job.Attempts), err.Error()) // → retry або dead
			continue
		}
		complete(ctx, db, job.ID)                    // стан → done
	}
}
