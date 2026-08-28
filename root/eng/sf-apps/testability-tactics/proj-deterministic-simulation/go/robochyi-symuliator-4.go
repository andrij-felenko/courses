// Сервер-лічильник. seen == nil → наївний (застосовує все); інакше — дедуплікує за opID.
type Server struct {
	value uint64
	seen  map[uint64]bool
}

func (srv *Server) apply(opID uint64) {
	if srv.seen != nil {
		if srv.seen[opID] {
			return // ідемпотентність: той самий opID рахуємо один раз
		}
		srv.seen[opID] = true
	}
	srv.value++
}

// Клієнт шле операцію й повторює її, якщо не діждався підтвердження за timeout.
type Client struct {
	sim     *Sim
	net     *Net
	srv     *Server
	acked   map[uint64]bool
	timeout uint64
}

func (c *Client) sendOp(opID uint64, attempt int) {
	desc := fmt.Sprintf("op%d спроба%d", opID, attempt)
	c.net.send("cli→srv "+desc, func() {
		c.srv.apply(opID) // сервер застосовує
		c.net.send("srv→cli ack "+desc, func() {
			c.acked[opID] = true // …і підтверджує
		})
	})
	c.sim.after(c.timeout, func() { // таймер повтору
		if !c.acked[opID] && attempt < 3 {
			c.sendOp(opID, attempt+1) // не діждались ack → шлемо ТОЙ САМИЙ opID знову
		}
	})
}
