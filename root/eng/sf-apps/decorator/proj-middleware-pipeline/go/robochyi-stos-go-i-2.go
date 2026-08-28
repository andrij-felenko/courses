// Auth: немає права → 401 і ВИХІД, next не викликаний (обрив ланцюга).
func Auth(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Authorization") == "" {
			http.Error(w, "unauthorized", http.StatusUnauthorized) // 401
			return                                                 // ← next НЕ викликаний
		}
		next.ServeHTTP(w, r)
	})
}

// Cache: на влученні віддаємо збережене й не йдемо глибше; на промаху —
// делегуємо, перехоплюємо тіло й кладемо в сховище на майбутнє.
func Cache(store map[string][]byte) Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if r.Method == http.MethodGet {
				if body, ok := store[r.URL.Path]; ok {
					w.Header().Set("X-Cache", "HIT")
					w.Write(body) // ← віддали з кешу, next НЕ викликаний
					return
				}
			}
			cw := &capture{ResponseWriter: w, status: 200} // ловимо, що напише глибина
			next.ServeHTTP(cw, r)
			if r.Method == http.MethodGet && cw.status == 200 {
				store[r.URL.Path] = cw.body.Bytes() // зберегли сире тіло
			}
		})
	}
}
