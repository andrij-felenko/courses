import (
    "crypto/rand"
    "encoding/base64"
    "fmt"
    "strings"

    "golang.org/x/crypto/argon2"
)

const (
    argonMem  = 19 * 1024 // 19 МіБ у КіБ = 19456
    argonTime = 2
    argonPar  = 1
    keyLen    = 32
)

// збираємо PHC-рядок вручну: $argon2id$v=..$m=..,t=..,p=..$<сіль>$<хеш>
func hashPassword(password string) (string, error) {
    salt := make([]byte, 16)
    if _, err := rand.Read(salt); err != nil { // crypto/rand — CSPRNG
        return "", err
    }
    key := argon2.IDKey([]byte(password), salt, argonTime, argonMem, argonPar, keyLen)
    b64 := base64.RawStdEncoding
    return fmt.Sprintf("$argon2id$v=%d$m=%d,t=%d,p=%d$%s$%s",
        argon2.Version, argonMem, argonTime, argonPar,
        b64.EncodeToString(salt), b64.EncodeToString(key)), nil
}

func register(email, password string, db *DB) error {
    norm := strings.ToLower(strings.TrimSpace(email))
    h, err := hashPassword(password)
    if err != nil {
        return err
    }
    return db.InsertUser(norm, h)
}
