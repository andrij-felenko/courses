// Readiness: передумова тесту, що крутиться вічно.
// Готові приймати трафік — ЛИШЕ коли шов до пристроїв відповідає.
func (a *API) Readyz(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
	defer cancel()
	if err := a.Devices.Ping(ctx); err != nil {
		http.Error(w, "not ready: device gateway", http.StatusServiceUnavailable)
		return
	}
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte("ready"))
}
