// Наївний повтор: до n спроб, поки помилка «варта повтору». Без бюджету, без змови.
func retryNaive(fn func() (Result, error), n int) (Result, error) {
	res, err := fn()
	for i := 1; i < n && err != nil && retryable(err); i++ {
		res, err = fn()
	}
	return res, err
}

// A повторює B (×3), B повторює C (×3), C-клієнт повторює спробу (×3).
func naiveChain(cl *Clock) (Result, error) {
	attemptC := WithTimeout(rawCallC, 300) // одна спроба до C зі стелею 300 мс
	return retryNaive(func() (Result, error) { //     A→B  ×3
		return retryNaive(func() (Result, error) { //   B→C  ×3
			return retryNaive(func() (Result, error) { // C-клієнт  ×3
				return attemptC(cl)
			}, 3)
		}, 3)
	}, 3)
}
