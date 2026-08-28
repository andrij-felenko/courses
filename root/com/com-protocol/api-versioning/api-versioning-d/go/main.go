// Позначка версії зі шляху веде запит до потрібного оброблювача.
mux.HandleFunc("GET /v1/orders/{id}", serveOrderV1)
mux.HandleFunc("GET /v2/orders/{id}", serveOrderV2)

// Або з заголовка — коли адреса лишається чистою:
mux.HandleFunc("GET /orders/{id}", func(w http.ResponseWriter, r *http.Request) {
	v := r.Header.Get("API-Version") // без позначки — усталена версія
	if v == "2" {
		serveOrderV2(w, r)
	} else {
		serveOrderV1(w, r)
	}
})
