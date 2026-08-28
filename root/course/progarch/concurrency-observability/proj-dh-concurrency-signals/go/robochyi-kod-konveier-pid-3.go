// observe — єдиний спостерігач: щосекунди знімає прилади, звіряє L = λ·W
// і керує протитиском за НАХИЛОМ черги.
func (p *Pool) observe(every time.Duration) {
	rt := []metrics.Sample{
		{Name: "/sched/latencies:seconds"},       // лаг планувальника — Go-аналог «лагу циклу»
		{Name: "/sync/mutex/wait/total:seconds"}, // сумарне чекання на замках
	}
	var prevDepth, rising int
	var accPrev, donePrev, nsPrev int64

	for range time.NewTicker(every).C {
		depth := len(p.jobs)
		queueDepth.Set(float64(depth))
		poolBusy.Set(float64(p.busy.Load()))
		L := float64(p.live.Load())
		inflight.Set(L)

		// суперництво рантайму — читаємо готові прилади Go
		metrics.Read(rt)
		schedLatencyP99.Set(p99(rt[0].Value.Float64Histogram()))
		mutexWaitTotal.Set(rt[1].Value.Float64())

		// ── сторож консистентності: виміряне L проти передбаченого λ·W ──
		acc, done, ns := p.accepted.Load(), p.done.Load(), p.sojournNs.Load()
		lambda := float64(acc-accPrev) / every.Seconds() // впущено за секунду
		var W float64
		if n := done - donePrev; n > 0 {
			W = float64(ns-nsPrev) / float64(n) / 1e9 // сер. час у системі, с
		}
		if L > 2 { // на майже порожній системі рівність шумить — не чіпаємо
			llResidual.Set(math.Abs(L-lambda*W) / L)
		}
		accPrev, donePrev, nsPrev = acc, done, ns

		// ── алерт на РІСТ (нахил), не на рівень ──
		if depth > prevDepth {
			rising++
		} else {
			rising = 0
		}
		switch {
		case rising >= 3: // черга росте три виміри поспіль — надходження обганяє обслугу
			p.brake.Store(true)
		case depth == 0: // спорожніла — відпускаємо протитиск
			p.brake.Store(false)
		}
		prevDepth = depth
	}
}

// p99 — грубий 99-й перцентиль із кошикового гістограма runtime/metrics.
func p99(h *metrics.Float64Histogram) float64 {
	var total uint64
	for _, c := range h.Counts {
		total += c
	}
	if total == 0 {
		return 0
	}
	target, cum := uint64(float64(total)*0.99), uint64(0)
	for i, c := range h.Counts {
		if cum += c; cum >= target {
			return h.Buckets[i+1] // верхня межа кошика, у який упав квантиль
		}
	}
	return h.Buckets[len(h.Buckets)-1]
}
