var seen sync.Map                         // насправді — стійке сховище, не пам'ять

func receive(w http.ResponseWriter, r *http.Request) {
    raw, _ := io.ReadAll(r.Body)          // сирі байти тіла, не розібраний JSON

    mac := hmac.New(sha256.New, secret)
    mac.Write(raw)
    expected := hex.EncodeToString(mac.Sum(nil))
    sig := r.Header.Get("X-Signature")
    if !hmac.Equal([]byte(sig), []byte(expected)) {   // порівняння сталого часу
        w.WriteHeader(http.StatusUnauthorized)
        return
    }

    var event Event
    json.Unmarshal(raw, &event)
    if _, dup := seen.LoadOrStore(event.ID, true); dup {  // вже бачили — тихо
        w.WriteHeader(http.StatusOK)
        return
    }

    queue <- event                        // зняти роботу з гарячого шляху
    w.WriteHeader(http.StatusOK)          // підтвердити ОДРАЗУ
}
