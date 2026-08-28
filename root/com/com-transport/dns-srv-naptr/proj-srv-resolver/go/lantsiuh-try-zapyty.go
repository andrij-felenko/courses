var errDenied = errors.New("домен не надає цієї служби") // ціль "."

// prefer — що цей клієнт узагалі вміє. Порядок домену (order, потім preference)
// головніший за наш смак: ми тільки викидаємо те, чого не потягнемо.
var prefer = map[string]bool{"SIPS+D2T": true, "SIP+D2T": true, "SIP+D2U": true}

// Крок 1: голий домен → імена, під якими лежать записи SRV.
func serviceNames(ctx context.Context, c *dns.Client, server, domain string) []string {
	m := new(dns.Msg)
	m.SetQuestion(dns.Fqdn(domain), dns.TypeNAPTR)
	resp, _, err := c.ExchangeContext(ctx, m, server)

	var recs []*dns.NAPTR
	if err == nil {
		for _, a := range resp.Answer {
			n, ok := a.(*dns.NAPTR)
			// S-NAPTR: прапорець «S» (далі буде SRV), регулярні вирази заборонені.
			if ok && strings.EqualFold(n.Flags, "S") && n.Regexp == "" &&
				prefer[strings.ToUpper(n.Service)] {
				recs = append(recs, n)
			}
		}
	}
	sort.SliceStable(recs, func(i, j int) bool {
		if recs[i].Order != recs[j].Order {
			return recs[i].Order < recs[j].Order
		}
		return recs[i].Preference < recs[j].Preference
	})

	names := make([]string, 0, len(recs))
	for _, n := range recs {
		names = append(names, dns.Fqdn(n.Replacement))
	}
	if len(names) == 0 { // NAPTR немає — транспорт доводиться припустити самим
		names = append(names, "_sips._tcp."+dns.Fqdn(domain))
	}
	return names
}

// Крок 2: ім'я служби → сирі записи SRV.
func srvTargets(ctx context.Context, c *dns.Client, server, name string) ([]Target, error) {
	m := new(dns.Msg)
	m.SetQuestion(name, dns.TypeSRV)
	resp, _, err := c.ExchangeContext(ctx, m, server)
	if err != nil {
		return nil, err
	}
	var ts []Target
	for _, a := range resp.Answer {
		s, ok := a.(*dns.SRV)
		if !ok {
			continue
		}
		if s.Target == "." { // не «не знаю», а «ні» — і жодних обхідних шляхів
			return nil, errDenied
		}
		ts = append(ts, Target{Host: dns.Fqdn(s.Target), Port: s.Port,
			Priority: s.Priority, Weight: s.Weight})
	}
	return ts, nil
}

// legacy — відкат на вшитий порт. Дозволений ЛИШЕ коли записів немає зовсім.
func legacy(ctx context.Context, domain string) ([]Target, error) {
	addrs, err := net.DefaultResolver.LookupNetIP(ctx, "ip", domain)
	if err != nil {
		return nil, err
	}
	return []Target{{Host: dns.Fqdn(domain), Port: 5061, Addrs: addrs}}, nil
}

// Resolve — увесь ланцюг. Викликається ОДИН раз на серію спроб.
func Resolve(ctx context.Context, server, domain string) ([]Target, error) {
	c := new(dns.Client)
	var plan []Target
	denied := false

	for _, name := range serviceNames(ctx, c, server, domain) {
		ts, err := srvTargets(ctx, c, server, name)
		switch {
		case errors.Is(err, errDenied):
			denied = true
		case err == nil && len(ts) > 0:
			plan = append(plan, orderRFC2782(ts)...)
		}
	}

	if len(plan) == 0 {
		if denied {
			return nil, errDenied // домен сказав «ні»: на вшитий порт іти НЕ можна
		}
		return legacy(ctx, domain) // записів просто немає — дозволений старий шлях
	}

	for i := range plan { // крок 3: адреси; порядок родин лишаємо резолверу
		host := strings.TrimSuffix(plan[i].Host, ".")
		if addrs, err := net.DefaultResolver.LookupNetIP(ctx, "ip", host); err == nil {
			plan[i].Addrs = addrs
		}
	}
	return plan, nil
}
