import (
    "crypto/sha256"
    "encoding/hex"
    "time"
)

type Session struct {
    UserID    string
    CreatedAt time.Time
    LastSeen  time.Time
}

func tokenHash(token string) string {
    sum := sha256.Sum256([]byte(token))
    return hex.EncodeToString(sum[:])
}

func createSession(userID string, db *DB) (string, error) {
    token, err := newSessionToken()
    if err != nil {
        return "", err
    }
    now := time.Now()
    db.PutSession(tokenHash(token), Session{UserID: userID, CreatedAt: now, LastSeen: now})
    return token, nil // повертаємо сам жетон — він піде в cookie
}
