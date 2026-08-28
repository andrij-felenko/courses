// Значення з JSON приходять у map[string]any; числа — як float64 (пастка Go).
type Req struct {
	Params map[string]string
	Body   map[string]any
}
type Res struct {
	Status int
	Body   map[string]any
}

type VersionChange struct {
	Version      string        // дата набуття чинності (ISO)
	Description  string
	UpRequest    func(Req) Req // форма ДО → форма ПІСЛЯ (запит); nil, якщо не стосується
	DownResponse func(Res) Res // форма ПІСЛЯ → форма ДО (відповідь); nil, якщо не стосується
}

// Від найстарішої до найновішої.
var changes = []VersionChange{
	{
		Version:     "2024-02-20",
		Description: "amount → total",
		UpRequest: func(r Req) Req {
			if v, ok := r.Body["amount"]; ok {
				r.Body["total"] = v
				delete(r.Body, "amount")
			}
			return r
		},
		DownResponse: func(r Res) Res {
			if v, ok := r.Body["total"]; ok {
				r.Body["amount"] = v
				delete(r.Body, "total")
			}
			return r
		},
	},
	{
		Version:     "2024-11-05",
		Description: "долари → центи",
		UpRequest: func(r Req) Req {
			if v, ok := r.Body["total"].(float64); ok {
				r.Body["total"] = v * 100
			}
			return r
		},
		DownResponse: func(r Res) Res {
			if v, ok := r.Body["total"].(float64); ok {
				r.Body["total"] = math.Round(v / 100)
			}
			return r
		},
	},
}
