package main

import ("io"; "net/http"; "strconv"; "sync")

// Найтонша нитка: браузер → API → канал → воркер → сховище → читання назад.
// Справжні тут — HTTP-стик і межа «API ↔ воркер» (канал між ґорутинами).
// Канал і Map — заглушки майбутніх брокера й бази; їхня заміна — вже м'ясо.
func main() {
	queue := make(chan int, 64)
	var mu sync.Mutex
	store := map[string]int{}

	go func() { // воркер — окрема частина: читає з каналу, пише у сховище
		for v := range queue {
			mu.Lock(); store["temp"] = v; mu.Unlock() // стик воркер → сховище
		}
	}()

	http.HandleFunc("/temp", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "POST" {
			b, _ := io.ReadAll(r.Body)
			v, _ := strconv.Atoi(string(b))
			queue <- v                        // стик API → канал
			io.WriteString(w, "ok"); return
		}
		mu.Lock(); v := store["temp"]; mu.Unlock()
		io.WriteString(w, strconv.Itoa(v))    // читання: нитка пройшла?
	})
	http.ListenAndServe(":8080", nil)
}
