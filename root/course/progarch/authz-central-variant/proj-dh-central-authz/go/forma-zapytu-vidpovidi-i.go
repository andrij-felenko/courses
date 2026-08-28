type Role   string
type Action string

type User     struct{ ID string }
type Resource struct{ Kind, ID, HomeID string } // завантажений об'єкт: HomeID — з нашої БД

// Форма запиту рішення.
type Decision struct {
	Subject  string            `json:"subject"`  // хто — з автентифікованої сесії
	Action   Action            `json:"action"`   // що — з маршруту
	Resource string            `json:"resource"` // над чим — "door:42"
	Context  map[string]string `json:"context"`  // факти — лише з авторитетного джерела
}
type Verdict struct {
	Allow  bool   `json:"allow"`
	Reason string `json:"reason"`
	Home   string `json:"home,omitempty"` // дім, на якому тримався вердикт — ключ для кеша
}

// Клієнт до центру.
type PdpClient interface {
	Check(ctx context.Context, req Decision) (Verdict, error)
}

// ШОВ — той самий, що у Варіанті А.
type Authorizer interface {
	Can(ctx context.Context, u User, a Action, r Resource) bool
}
