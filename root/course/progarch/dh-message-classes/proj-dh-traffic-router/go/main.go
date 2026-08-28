// Робоча черга = буферизований канал; пул із n горутин-воркерів.
// Кожен таск дістає РІВНО один воркер — так канал арбітрує конкурентних споживачів.
func drain(jobs []Job, workers int, handle func(job Job, worker int)) {
	ch := make(chan Job, len(jobs))
	for _, j := range jobs {
		ch <- j
	}
	close(ch) // тасків більше не буде — воркери вийдуть, спорожнивши канал

	var wg sync.WaitGroup
	for id := 0; id < workers; id++ {
		wg.Add(1)
		go func(worker int) {
			defer wg.Done()
			for job := range ch { // кожен таск дістає лише ОДИН воркер із пулу
				handle(job, worker)
			}
		}(id)
	}
	wg.Wait()
}
