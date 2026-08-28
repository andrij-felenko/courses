func orderHandler(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")

    // версія береться з бази одним дешевим читанням, без збирання тіла
    version, err := db.OrderVersion(id)
    if err != nil {
        http.Error(w, "not found", http.StatusNotFound)
        return
    }

    etag := fmt.Sprintf("\"order-%s-v%d\"", id, version)
    w.Header().Set("ETag", etag)
    w.Header().Set("Cache-Control", "private, no-cache")

    if r.Header.Get("If-None-Match") == etag {
        w.WriteHeader(http.StatusNotModified) // тіло не збирали взагалі
        return
    }

    order, err := db.LoadOrder(id)            // ось тут дорога робота
    if err != nil {
        http.Error(w, "internal", http.StatusInternalServerError)
        return
    }
    json.NewEncoder(w).Encode(order)
}
