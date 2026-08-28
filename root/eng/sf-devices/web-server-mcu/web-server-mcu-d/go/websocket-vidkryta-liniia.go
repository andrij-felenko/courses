// WebSocket на gorilla/websocket: ловить кадр і сам штовхає показання.
var upgrader = websocket.Upgrader{}
var clients = map[*websocket.Conn]bool{} // множина підключених

func wsHandler(w http.ResponseWriter, r *http.Request) {
    ws, _ := upgrader.Upgrade(w, r, nil) // рукостискання: HTTP → WebSocket
    clients[ws] = true
    defer delete(clients, ws)
    for {
        _, frame, err := ws.ReadMessage() // кожен кадр від браузера
        if err != nil {
            break
        }
        handle(frame) // ... обробити ...
    }
}

// Штовхнути свіже показання ВСІМ підключеним клієнтам (з іншої ґорутини).
func wsPushTemperature(t float64) {
    msg, _ := json.Marshal(map[string]float64{"temp": t})
    for ws := range clients { // сервер сам ініціює відправку
        ws.WriteMessage(websocket.TextMessage, msg)
    }
}
