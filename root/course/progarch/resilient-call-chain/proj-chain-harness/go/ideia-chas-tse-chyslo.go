// ── Стенд: усе детерміноване, час — це число, а не реальний сон ──
// Віртуальний МОНОТОННИЙ годинник. Now, Deadline — модельні мілісекунди.
type Clock struct{ Now, Deadline int }

// Спроба повертає значення + скільки коштувала (для таймаута й p99).
type Result struct {
	Value   string
	Latency int
}

// Помилка несе сигнал «чи варто повторювати» — він тече ВГОРУ по ланцюгу.
type Failure struct {
	Kind      string
	Retryable bool
}

func (f *Failure) Error() string { return f.Kind }

func retryable(err error) bool {
	var f *Failure
	if errors.As(err, &f) {
		return f.Retryable
	}
	return err != nil // невідому помилку вважаємо минущою
}

type Call func(cl *Clock) (Result, error)

// Детермінований генератор — щоб «27» і p99 повторювались.
var seed int64 = 1

func rnd() float64 {
	seed = (seed*1103515245 + 12345) & 0x7fffffff
	return float64(seed) / float64(0x7fffffff)
}

var cCalls int  // ЄДИНА метрика навантаження на дно ланцюга
var sick bool   // драйвер вмикає «інцидент» на частину запитів

// ── C — квола й подеколи повільна залежність ──
func rawCallC(_ *Clock) (Result, error) {
	cCalls++
	pFail, pSlow := 0.05, 0.01
	if sick {
		pFail, pSlow = 0.90, 0.70
	}
	latency := 20
	if rnd() < pSlow {
		latency = 600
	}
	if rnd() < pFail {
		return Result{Latency: latency}, &Failure{Kind: "overloaded", Retryable: true}
	}
	return Result{Value: "camera-frame", Latency: latency}, nil
}
