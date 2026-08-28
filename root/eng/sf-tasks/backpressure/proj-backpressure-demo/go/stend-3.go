// Репортер: раз на секунду — шість чисел.
func reporter(q queue, m *meters, stop <-chan struct{}, wg *sync.WaitGroup) {
	defer wg.Done()
	fmt.Printf("%4s %9s %9s %10s %11s %7s %10s\n",
		"t", "черга", "обробка", "затримка", "зроблено/с", "у put", "купа")

	tick := time.NewTicker(time.Second)
	defer tick.Stop()
	start := time.Now()
	prevDone, prevBlocked := 0, time.Duration(0)

	for {
		select {
		case <-stop:
			return
		case now := <-tick.C:
			done, service, sojourn, blocked := m.snapshot()

			// GC перед заміром — щоб побачити ЖИВИЙ набір, а не сміття,
			// яке збирач ще не встиг прибрати. У службі так не роблять:
			// це спиняє світ. Тут це чесність заміру, а не спосіб жити.
			runtime.GC()
			var ms runtime.MemStats
			runtime.ReadMemStats(&ms)

			fmt.Printf("%3.0fс %9d %6.0f мс %8.2f с %9d/с %5.0f %% %6.1f МіБ\n",
				now.Sub(start).Seconds(), q.length(),
				float64(service.Milliseconds()), sojourn.Seconds(),
				done-prevDone,                       // пропускна здатність за секунду
				100*(blocked-prevBlocked).Seconds(), // частка секунди, яку виробник простояв у put
				float64(ms.HeapAlloc)/(1<<20))
			prevDone, prevBlocked = done, blocked
		}
	}
}

func main() {
	mode, capacity := "bounded", 32
	if len(os.Args) > 1 {
		mode = os.Args[1]
	}
	if len(os.Args) > 2 {
		capacity, _ = strconv.Atoi(os.Args[2])
	}

	var q queue
	switch mode {
	case "unbounded":
		q = newUnbounded()
	case "bounded":
		q = newBounded(capacity)
	default:
		fmt.Println("вжиток: go run backpressure_demo.go [unbounded | bounded <місткість>]")
		return
	}

	m := &meters{}
	stop := make(chan struct{})
	var wg sync.WaitGroup
	start := time.Now()

	wg.Add(2)
	go consumer(q, m, &wg)
	go reporter(q, m, stop, &wg)
	go producer(q, m, stop) // отримавши stop, сам закриє чергу

	time.Sleep(runFor)
	close(stop)

	// Штатне вимкнення: чесно дочекатися, поки черга спорожніє.
	// Ось тут і з'ясується справжня ціна черги без стелі.
	fmt.Printf("\nвимикаємось: у черзі лишилося %d — це ще %v роботи\n",
		q.length(), time.Duration(q.length())*handleCost)
	t0 := time.Now()
	wg.Wait()

	done, _, _, blocked := m.snapshot()
	fmt.Printf("злив забрав %v; оброблено %d за %v (%.0f/с); виробник простояв у put %.1f с\n",
		time.Since(t0).Round(time.Millisecond), done,
		time.Since(start).Round(time.Second), float64(done)/time.Since(start).Seconds(),
		blocked.Seconds())
}
