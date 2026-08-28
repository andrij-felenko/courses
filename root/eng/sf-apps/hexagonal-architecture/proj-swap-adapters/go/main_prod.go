// main_prod.go ── ТОЧКА ЗБІРКИ (прод). ЄДИНЕ місце, де звучить слово "Postgres".
package main

func main() {
    db, _ := pgxpool.New(ctx, os.Getenv("DATABASE_URL"))

    сервіс := &order.ЗамовленняСервіс{
        Сховище: &adapters.PgСховище{DB: db}, // ← база сюди
        НID:     uuidFunc,
    }
    http := &adapters.ЗамовленняHttp{Застосунок: сервіс} // ← ядро сюди

    mux := http2.NewServeMux()
    mux.HandleFunc("POST /orders", http.Post)
    http2.ListenAndServe(":8080", mux)
}
