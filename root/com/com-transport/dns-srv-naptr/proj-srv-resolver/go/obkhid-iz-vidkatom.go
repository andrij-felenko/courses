// Dial іде готовим планом: цілі за порядком, адреси кожної цілі за порядком.
// Жодного нового запиту в DNS: план уже розіграний, перерозігрувати його не можна.
func Dial(ctx context.Context, domain string, plan []Target, budget int) (net.Conn, error) {
	last := errors.New("у плані немає жодної адреси")
	tries := 0

	for _, t := range plan {
		for _, a := range t.Addrs {
			if tries >= budget { // специфікація межі не ставить — ставимо ми
				return nil, fmt.Errorf("бюджет спроб вичерпано: %w", last)
			}
			tries++

			d := net.Dialer{Timeout: 2 * time.Second}
			conn, err := d.DialContext(ctx, "tcp",
				net.JoinHostPort(a.String(), strconv.Itoa(int(t.Port))))
			if err != nil {
				last = err // відмова або таймаут — просто наступна адреса
				continue
			}
			// Ім'я для TLS — ПОЧАТКОВИЙ домен, а не ціль, куди привів SRV.
			tc := tls.Client(conn, &tls.Config{ServerName: domain})
			if err := tc.HandshakeContext(ctx); err != nil {
				tc.Close()
				last = err
				continue
			}
			return tc, nil
		}
	}
	return nil, fmt.Errorf("жодна ціль не відповіла: %w", last)
}
