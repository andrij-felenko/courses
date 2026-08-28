// Мережа під повним контролем симулятора: він сам вирішує долю кожного повідомлення.
type Net struct {
	sim     *Sim
	dropPct uint64
	minLat  uint64
	maxLat  uint64
	log     []string
}

// send доставляє deliver() КОЛИСЬ — або не доставляє зовсім. Усе рішення — із зерна.
func (n *Net) send(desc string, deliver func()) {
	if n.sim.rng.chance(n.dropPct) { // втрата
		n.log = append(n.log, fmt.Sprintf("t=%2d  ВТРАТА   %s", n.sim.now, desc))
		return
	}
	lat := n.minLat + n.sim.rng.intn(n.maxLat-n.minLat+1) // затримка з засіяного діапазону
	n.sim.after(lat, func() {
		n.log = append(n.log, fmt.Sprintf("t=%2d  доставка %s", n.sim.now, desc))
		deliver()
	})
}
