// Наївний повтор: таймаут → ще раз. Небезпечно — таймаут ≠ «не виконалось».
func naiveRetry(l *Link, h *Hub, patience time.Duration, tries int) error {
	for i := 0; i < tries; i++ {
		if err := clientUnlock(l, h, patience); err == nil {
			return nil // почули «ok» — виходимо
		}
		// таймаут. Замок не чіпали — чи вже відчинили, а підтвердження зникло? Невідомо.
		// Якщо відчинили — цей повтор смикне реле ВДРУГЕ.
	}
	return errors.New("вичерпано спроби")
}

func runNaive() {
	hub := &Hub{}
	link := &Link{faults: []Fault{DropAck}} // збій раз, тоді канал чистий
	err := naiveRetry(link, hub, 100*time.Millisecond, 3)
	fmt.Printf("наївний повтор: клієнт: %s | реле смикнулось: %d\n", label(err), hub.firesCount())
	// → наївний повтор: клієнт: успіх | реле смикнулось: 2
}
