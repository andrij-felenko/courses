func runWorlds() {
	patience := 100 * time.Millisecond
	cases := []struct {
		name  string
		fault Fault
	}{
		{"(1) запит зник туди", DropReq},
		{"(2) підтвердження зникло", DropAck},
		{"(3) запит повзе", SlowReq},
	}
	for _, c := range cases {
		hub := &Hub{}
		link := &Link{faults: []Fault{c.fault}, slow: 300 * time.Millisecond}

		err := clientUnlock(link, hub, patience)
		time.Sleep(350 * time.Millisecond) // дати «повільному» доповзти — щоб побачити правду

		fmt.Printf("%-24s клієнт: %-8s реле: %d\n", c.name, label(err), hub.firesCount())
	}
}

func label(err error) string {
	if err == nil {
		return "успіх"
	}
	return err.Error()
}
