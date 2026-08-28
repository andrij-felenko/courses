// Хендлери на net/http: гілка /static/ і параметр запиту /led?state=on.
func staticGet(w http.ResponseWriter, r *http.Request) {
    // r.URL.Path = "/static/app.js" → відрізаємо префікс, лишається "app.js"
    name := strings.TrimPrefix(r.URL.Path, "/static/")
    sendFileFromFS(w, name) // читаємо файл і віддаємо (нижче)
}

func ledGet(w http.ResponseWriter, r *http.Request) { // /led?state=on
    state := r.URL.Query().Get("state") // окремий ключ query string
    if state != "" {
        setLED(state == "on") // вмикаємо/вимикаємо
    }
    io.WriteString(w, "ok")
}
