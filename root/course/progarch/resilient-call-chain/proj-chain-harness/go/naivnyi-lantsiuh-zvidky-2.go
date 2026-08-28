func runStorm() {
	cCalls = 0
	// C, що завжди відповідає минущою помилкою — кожна спроба «варта повтору».
	alwaysFail := func(cl *Clock) (Result, error) {
		cCalls++
		return Result{Latency: 300}, &Failure{Kind: "overloaded", Retryable: true}
	}
	cl := &Clock{Now: 0, Deadline: 1 << 30}
	retryNaive(func() (Result, error) {
		return retryNaive(func() (Result, error) {
			return retryNaive(func() (Result, error) { return alwaysFail(cl) }, 3)
		}, 3)
	}, 3)
	fmt.Printf("шторм: C дістав %d викликів\n", cCalls) // → 27
}
