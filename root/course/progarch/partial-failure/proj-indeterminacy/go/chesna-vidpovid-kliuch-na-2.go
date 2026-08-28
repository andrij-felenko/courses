// safeRetry: ОДИН ключ на всю логічну команду (у житті — UUID v4), той самий
// на кожній спробі. Дубль по дорозі хаб відсіє сам.
func safeRetry(l *Link, h *KeyedHub, patience time.Duration, tries int) error {
	key := "unlock-7:9f2c1a" // згенеровано РАЗ; той самий на всіх спробах
	for i := 0; i < tries; i++ {
		reply := l.send(func() string { return h.unlock(key) })
		select {
		case <-reply:
			return nil
		case <-time.After(patience):
			// таймаут → повтор із ТИМ САМИМ ключем
		}
	}
	return errors.New("вичерпано спроби")
}

func runSafe() {
	hub := NewKeyedHub()
	link := &Link{faults: []Fault{DropAck}} // той самий збій, що й у наївному прогоні
	err := safeRetry(link, hub, 100*time.Millisecond, 3)
	fmt.Printf("повтор із ключем: клієнт: %s | реле смикнулось: %d\n", label(err), hub.firesCount())
	// → повтор із ключем: клієнт: успіх | реле смикнулось: 1
}
