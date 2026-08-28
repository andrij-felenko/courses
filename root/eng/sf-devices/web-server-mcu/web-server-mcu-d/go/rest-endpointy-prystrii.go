// POST /led з тілом {"on":true} — прочитати тіло й перемкнути світло.
func ledPost(w http.ResponseWriter, r *http.Request) {
    r.Body = http.MaxBytesReader(w, r.Body, 64) // захист від завеликого тіла
    var data struct {
        On bool `json:"on"`
    }
    if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
        http.Error(w, "тіло завелике", http.StatusBadRequest)
        return
    }
    setLED(data.On)

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]bool{"led": data.On})
}
