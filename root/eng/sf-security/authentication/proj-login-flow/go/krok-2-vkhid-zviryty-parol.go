import (
    "crypto/subtle"
    "encoding/base64"
    "errors"
    "fmt"
    "strings"

    "golang.org/x/crypto/argon2"
)

type argonParams struct {
    mem, time uint32
    par       uint8
}

// розібрати PHC-рядок назад на параметри, сіль і хеш
func decodeHash(encoded string) (p argonParams, salt, key []byte, err error) {
    parts := strings.Split(encoded, "$") // ["", "argon2id", "v=19", "m=..,t=..,p=..", сіль, хеш]
    if len(parts) != 6 {
        return p, nil, nil, errors.New("поганий формат хешу")
    }
    if _, err = fmt.Sscanf(parts[3], "m=%d,t=%d,p=%d", &p.mem, &p.time, &p.par); err != nil {
        return p, nil, nil, err
    }
    b64 := base64.RawStdEncoding
    if salt, err = b64.DecodeString(parts[4]); err != nil {
        return p, nil, nil, err
    }
    if key, err = b64.DecodeString(parts[5]); err != nil {
        return p, nil, nil, err
    }
    return p, salt, key, nil
}

func verifyPassword(encoded, password string) bool {
    p, salt, key, err := decodeHash(encoded)
    if err != nil {
        return false
    }
    calc := argon2.IDKey([]byte(password), salt, p.time, p.mem, p.par, uint32(len(key)))
    return subtle.ConstantTimeCompare(key, calc) == 1 // звірка за сталий час
}

// заздалегідь порахований фіктивний хеш (ті самі параметри)
var dummyHash, _ = hashPassword("dummy-password-never-matches")

func login(email, password string, db *DB) *User {
    norm := strings.ToLower(strings.TrimSpace(email))
    user := db.FindUser(norm) // nil, якщо немає
    stored := dummyHash
    if user != nil {
        stored = user.PwHash
    }
    if verifyPassword(stored, password) && user != nil {
        return user
    }
    return nil
}
