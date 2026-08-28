func (p *Proxy) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	rcc := ParseCacheControl(r.Header.Get("Cache-Control"))

	if r.Method != http.MethodGet && r.Method != http.MethodHead {
		up, err := p.origin.RoundTrip(r)
		if err != nil {
			http.Error(w, "bad gateway", http.StatusBadGateway)
			return
		}
		if up.StatusCode < 400 {
			p.store.Invalidate(r.URL.String()) // RFC 9111 §4.4
		}
		copyResponse(w, up)
		return
	}

	e := p.store.Lookup(r.Method, r.URL.String(), r.Header)
	if e == nil {
		if rcc.OnlyIfCached {
			w.WriteHeader(http.StatusGatewayTimeout)
			return
		}
		p.fetchAndStore(w, r)
		return
	}

	now := time.Now() // time.Time несе монотонний відлік, тож Sub тут не боїться NTP
	switch Decide(e, rcc, now, p.shared) {
	case Serve:
		p.serve(w, e, CurrentAge(e, now))
	case ServeStaleAsync:
		// контекст запиту скасується, щойно ServeHTTP поверне керування,
		// тому фонова валідація йде з власним контекстом і копією запиту
		go p.revalidate(r.Clone(context.Background()))
		p.serve(w, e, CurrentAge(e, now))
	default:
		if rcc.OnlyIfCached {
			w.WriteHeader(http.StatusGatewayTimeout)
			return
		}
		p.revalidateNow(w, r, e)
	}
}

func (p *Proxy) serve(w http.ResponseWriter, e *Entry, age time.Duration) {
	h := w.Header()
	for k, v := range e.Header {
		h[k] = v
	}
	// §5.1: Age виставляє кеш, і саме current_age
	h.Set("Age", strconv.FormatInt(int64(age/time.Second), 10))
	w.WriteHeader(e.Status)
	w.Write(e.Body)
}
