package session

import "time"

type Session struct {
    UserID    string
    CreatedAt time.Time // початок відліку абсолютного строку
}

// Store ховає, ДЕ лежать сесії. Політика (строки, ротація) — вище, над ним.
type Store interface {
    Create(userID string) (sid string, err error)
    Lookup(sid string) (*Session, error)           // nil — немає/згасла; усередині ковзає idle
    Rotate(sid string) (newSid string, err error)  // новий номер, ті самі дані, старий мертвий
    Destroy(sid string) error
}
