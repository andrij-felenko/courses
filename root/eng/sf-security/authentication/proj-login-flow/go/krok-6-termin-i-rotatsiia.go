const (
    idle     = 7 * 24 * time.Hour  // без активності — просрочка
    absolute = 14 * 24 * time.Hour // від входу — жорстка стеля
)

func authenticate(token string, db *DB) *Session {
    s := db.GetSession(tokenHash(token))
    if s == nil {
        return nil
    }
    now := time.Now()
    if now.Sub(s.LastSeen) > idle || now.Sub(s.CreatedAt) > absolute {
        db.DeleteSession(tokenHash(token)) // мертву — прибрати
        return nil
    }
    db.TouchSession(tokenHash(token), now) // ковзне вікно бездіяльності
    return s
}

// РОТАЦІЯ під час входу — проти фіксації сесії:
func loginAndStart(user *User, oldToken string, db *DB) (string, error) {
    if oldToken != "" {
        db.DeleteSession(tokenHash(oldToken)) // старий ідентифікатор — мертвий
    }
    return createSession(user.ID, db) // свіжий, невідомий нападнику
}
