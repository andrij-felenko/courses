// adapters/http.go ── ДРАЙВЕР-АДАПТЕР. Залежить від ПОРТУ, не від сервісу.
package adapters

import (
    "encoding/json"
    "net/http"

    "example/order"
)

type ЗамовленняHttp struct {
    Застосунок order.ОформленняЗамовлення // ← порт, не клас
}

func (h *ЗамовленняHttp) Post(w http.ResponseWriter, r *http.Request) {
    var тіло struct {
        Пошта   string          `json:"пошта"`
        Позиції []order.Позиція `json:"позиції"`
    }
    json.NewDecoder(r.Body).Decode(&тіло)

    з, err := h.Застосунок.Оформити(тіло.Пошта, тіло.Позиції)
    if err != nil {
        w.WriteHeader(400)
        json.NewEncoder(w).Encode(map[string]string{"помилка": err.Error()})
        return
    }
    w.WriteHeader(201)
    json.NewEncoder(w).Encode(map[string]any{"id": з.ID, "сума": з.Сума()}) // домен → HTTP
}
