// main_local.go ── ТОЧКА ЗБІРКИ (локально). Слова "Postgres" тут НЕМА зовсім.
package main

func main() {
    сервіс := &order.ЗамовленняСервіс{
        Сховище: adapters.НовеПамятьСховище(), // ← пам'ять сюди
        НID:     uuidFunc,
    }
    http := &adapters.ЗамовленняHttp{Застосунок: сервіс}

    mux := http2.NewServeMux()
    mux.HandleFunc("POST /orders", http.Post)
    http2.ListenAndServe(":8080", mux)
}
