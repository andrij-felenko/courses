package webhook

import "sync"

type Subscriber struct {
	URL, Secret string
}

// Розкладаємо подію на НЕЗАЛЕЖНІ одиниці й женемо пулом ґорутин.
func FanOut(subs []Subscriber, payload any, concurrency int) {
	jobs := make(chan Subscriber)
	var wg sync.WaitGroup

	// Пул робітників: рівно `concurrency` доставок «у польоті» водночас.
	for i := 0; i < concurrency; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for s := range jobs {
				job := NewDeliveryJob(s.URL, payload)
				signed, _ := Sign(job.Payload, s.Secret)
				if !DeliverWithRetry(job.URL, signed, job.DeliveryID) {
					DeadLetter(job) // вичерпав спроби → мертві листи
				}
			}
		}()
	}
	for _, s := range subs {
		jobs <- s // мрець тримає СВОГО робітника; інші не чекають
	}
	close(jobs)
	wg.Wait()
}
