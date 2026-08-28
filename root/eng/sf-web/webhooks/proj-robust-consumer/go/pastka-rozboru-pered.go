func receive(w http.ResponseWriter, r *http.Request) {
    raw, err := io.ReadAll(r.Body)                     // сирі байти ПЕРШЕ
    if err != nil {
        w.WriteHeader(http.StatusBadRequest)
        return
    }
    if !verify(raw, r.Header.Get("X-Signature")) {
        w.WriteHeader(http.StatusUnauthorized)         // підпис не збігся — геть
        return
    }

    var ev struct{ ID, Type string }
    if json.Unmarshal(raw, &ev) != nil {               // розбір ЛИШЕ після перевірки
        w.WriteHeader(http.StatusBadRequest)           // криве тіло — не наша подія
        return
    }

    isNew, err := inboxInsert(r.Context(), ev.ID, ev.Type, raw)
    if err != nil {
        w.WriteHeader(http.StatusInternalServerError)  // не зберегли — хай ПОВТОРЯТЬ, не 200!
        return
    }
    if isNew {
        enqueue(ev.ID)                                 // роботу знімемо з гарячого шляху
    }
    w.WriteHeader(http.StatusOK)                       // 200 і новій, і дублю
}

func verify(raw []byte, sig string) bool {
    mac := hmac.New(sha256.New, secret)
    mac.Write(raw)
    expected := hex.EncodeToString(mac.Sum(nil))
    return hmac.Equal([]byte(sig), []byte(expected))   // сталий час
}
