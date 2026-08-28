// ── ДРАЙВЕР-АДАПТЕР: перекладає HTTP на виклик вхідного порту ──
type ЗамовленняHttp struct{ застосунок ОформленняЗамовлення } // залежить від ПОРТУ

func (h *ЗамовленняHttp) Post(w http.ResponseWriter, r *http.Request) {
    var тіло requestBody
    json.NewDecoder(r.Body).Decode(&тіло)
    з, _ := h.застосунок.Оформити(тіло.Товари, тіло.Пошта)
    w.WriteHeader(201)
    json.NewEncoder(w).Encode(map[string]string{"id": з.ID}) // назад у HTTP
}
