// Сервіс пристроїв: гейт (PEP) лишився локальним, а рішення (PDP) — за мережею.
func UnlockDoor(w http.ResponseWriter, r *http.Request) {
    door, _ := devices.Load(r.PathValue("id")) // об'єкт іще під рукою

    verdict, err := authz.Check(r.Context(), Decision{ // ← стрибок у центр
        Subject:  user(r).ID,                          // хто: Богдан
        Action:   "unlock",                            // що: відчинити
        Resource: "door:" + door.ID,                   // над чим: замок #42
        Context:  map[string]any{"homeId": door.HomeID}, // факти — з собою
    })
    if err != nil || !verdict.Allow { // помилка теж означає «ні» (про це нижче)
        http.Error(w, "forbidden", http.StatusForbidden)
        return
    }
    door.Unlock()
    writeJSON(w, ok{true})
}
