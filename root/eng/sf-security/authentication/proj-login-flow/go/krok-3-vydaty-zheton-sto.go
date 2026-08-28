import (
    "crypto/rand"
    "encoding/base64"
)

func newSessionToken() (string, error) {
    b := make([]byte, 16) // 128 бітів
    if _, err := rand.Read(b); err != nil { // crypto/rand, НЕ math/rand
        return "", err
    }
    return base64.RawURLEncoding.EncodeToString(b), nil
}
