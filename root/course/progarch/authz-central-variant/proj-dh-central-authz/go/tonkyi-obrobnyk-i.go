// Обробник: гейт (PEP) лишився локальним, рішення (PDP) — у центрі.
func UnlockDoor(w http.ResponseWriter, r *http.Request) {
	door, err := devices.Load(r.PathValue("id")) // door.HomeID — з НАШОЇ БД
	if err != nil {
		http.Error(w, "not found", http.StatusNotFound)
		return
	}
	if !authz.Can(r.Context(), user(r), "unlock", door.Resource()) {
		http.Error(w, "forbidden", http.StatusForbidden)
		return
	}
	door.Unlock()
	writeJSON(w, map[string]bool{"ok": true})
}

// Реалізація шва: похід у центр, а будь-яка помилка → deny (fail-closed).
type CentralAuthorizer struct{ pdp PdpClient }

func (a *CentralAuthorizer) Can(ctx context.Context, u User, act Action, r Resource) bool {
	v, err := a.pdp.Check(ctx, Decision{
		Subject:  u.ID,
		Action:   act,
		Resource: r.Kind + ":" + r.ID,
		Context:  map[string]string{"homeId": r.HomeID}, // факт із ЗАВАНТАЖЕНОГО об'єкта
	})
	if err != nil {
		metrics.Inc("authz.fail_closed") // збій ВИДНО в моніторингу, а не тихо
		return false                     // центр мовчить → DENY (fail-closed)
	}
	return v.Allow
}
