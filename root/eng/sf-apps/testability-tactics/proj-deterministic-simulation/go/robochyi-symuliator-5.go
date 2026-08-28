// Один прогін — чиста функція від зерна: та сама відповідь щоразу.
func runOnce(seed uint64, naive bool) (ok bool, value uint64, log []string) {
	s := NewSim(seed)
	net := &Net{sim: s, dropPct: 0, minLat: 1, maxLat: 12} // втрати тут вимкнені — ізолюємо гонитву таймауту
	srv := &Server{}
	if !naive {
		srv.seen = map[uint64]bool{}
	}
	cli := &Client{sim: s, net: net, srv: srv, acked: map[uint64]bool{}, timeout: 24}

	for i := uint64(0); i < K; i++ { // вкидаємо K операцій у різні моменти
		id := i
		s.after(i*10, func() { cli.sendOp(id, 1) })
	}
	s.run()

	// ІНВАРІАНТ БЕЗПЕКИ: жодну операцію не пораховано двічі.
	return srv.value <= K, srv.value, net.log
}
