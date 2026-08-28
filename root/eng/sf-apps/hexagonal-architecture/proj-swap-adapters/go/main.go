// main.go ── ОДНА збірка на всі середовища. Вибір адаптера — тут, і тільки тут.
package main

// ↓ ЄДИНА розвилка на весь застосунок
func зібратиСховище() order.ЗамовленняСховище {
    if os.Getenv("STORE") == "memory" {
        return adapters.НовеПамятьСховище()
    }
    db, _ := pgxpool.New(ctx, os.Getenv("DATABASE_URL"))
    return &adapters.PgСховище{DB: db}
}

func main() {
    сервіс := &order.ЗамовленняСервіс{Сховище: зібратиСховище(), НID: uuidFunc}
    http := &adapters.ЗамовленняHttp{Застосунок: сервіс}
    mux := http2.NewServeMux()
    mux.HandleFunc("POST /orders", http.Post)
    http2.ListenAndServe(":8080", mux)
    // STORE=memory ./app → пам'ять; без STORE → Postgres
}
