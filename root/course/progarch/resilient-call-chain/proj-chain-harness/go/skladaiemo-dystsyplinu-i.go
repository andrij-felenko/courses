const minWork = 25

func makeDisciplined() Call {
	budget := &Budget{ratio: 0.10}
	br := &Breaker{state: "closed", failsToOpen: 5, cooldown: 200}
	cClient := br.Wrap(WithTimeout(rawCallC, 300)) // таймаут ВСЕРЕДИНІ запобіжника, БЕЗ повтору
	bHop := func(cl *Clock) (Result, error) {      // B: своя робота + ОДИН виклик до C
		if cl.Deadline-cl.Now < minWork {
			return Result{}, &Failure{Kind: "deadline", Retryable: false}
		}
		cl.Now += 5
		return cClient(cl)
	}
	aRetry := WithRetry(bHop, 3, minWork, budget) // ПОВТОР ЛИШЕ ТУТ
	return func(cl *Clock) (Result, error) { cl.Now += 5; return aRetry(cl) }
}

// Драйвер: жене n запитів, вмикає «інцидент» на середину прогону, рахує p99.
func benchmark(chain Call, n int) (int, int) {
	cCalls, seed = 0, 1 // однакові умови «до» і «після»
	lat := make([]int, n)
	for i := 0; i < n; i++ {
		sick = i >= n*3/10 && i < n*6/10 // 30% прогону — C хворіє
		cl := &Clock{Now: 0, Deadline: 1000}
		chain(cl)
		lat[i] = cl.Now // наскрізна затримка = витрачений час
	}
	sort.Ints(lat)
	return cCalls, lat[int(0.99*float64(n))-1]
}

func main() {
	runStorm()
	c1, p1 := benchmark(naiveChain, 10000)
	fmt.Printf("наївно:      C=%d  p99=%dмс\n", c1, p1)
	c2, p2 := benchmark(makeDisciplined(), 10000)
	fmt.Printf("дисципліна:  C=%d  p99=%dмс\n", c2, p2)
}
