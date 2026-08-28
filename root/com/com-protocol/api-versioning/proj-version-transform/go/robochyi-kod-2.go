// import "math"

func upcast(req Req, from string) Req {
	for _, c := range changes { // від старих до нових
		if c.Version > from && c.UpRequest != nil {
			req = c.UpRequest(req)
		}
	}
	return req
}

func downcast(res Res, to string) Res {
	for i := len(changes) - 1; i >= 0; i-- { // від нових до старих
		c := changes[i]
		if c.Version > to && c.DownResponse != nil {
			res = c.DownResponse(res)
		}
	}
	return res
}

func handle(clientVersion string, params map[string]string, body map[string]any) Res {
	coreReq := upcast(Req{Params: params, Body: body}, clientVersion)
	coreRes := core(coreReq) // ядро — лише поточна форма
	return downcast(coreRes, clientVersion)
}

func core(r Req) Res { // знає тільки сьогоднішню форму
	return Res{Status: 200, Body: map[string]any{"id": "or_42", "total": r.Body["total"]}}
}

// handle("2023-05-10", nil, map[string]any{"amount": 500.0})
// → Res{Status: 200, Body: {"id": "or_42", "amount": 500}}
