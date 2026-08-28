// Chain: h — діловий обробник; mw — шари ЗЗОВНІ всередину.
// Нанизуємо з кінця списку: останній шар лягає найглибше, перший — найзовні.
func Chain(h http.Handler, mw ...Middleware) http.Handler {
	for i := len(mw) - 1; i >= 0; i-- {
		h = mw[i](h)
	}
	return h
}

func main() {
	business := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("привіт зі справжнього обробника"))
	})
	store := map[string][]byte{}

	app := Chain(business,
		Recover, Logger, Timer, Auth, Gzip, Cache(store), // зовні → всередину
	)
	http.ListenAndServe(":8080", app)
}
