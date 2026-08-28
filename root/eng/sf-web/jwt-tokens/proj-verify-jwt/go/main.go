package jwt

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"strings"
	"time"
)

// RawURLEncoding — це base64url БЕЗ службових '=', саме як у JWT.
var b64 = base64.RawURLEncoding

func hs256(msg, secret []byte) []byte {
	m := hmac.New(sha256.New, secret)
	m.Write(msg)
	return m.Sum(nil)
}

var ErrInvalid = errors.New("невалідний токен")

// ── ВИДАЧА ─────────────────────────────────────────────────────────────────
func Issue(claims map[string]any, secret []byte, ttl time.Duration) (string, error) {
	now := time.Now().Unix()
	claims["iat"] = now
	claims["nbf"] = now
	claims["exp"] = now + int64(ttl.Seconds())

	h, _ := json.Marshal(map[string]string{"alg": "HS256", "typ": "JWT"})
	p, err := json.Marshal(claims)
	if err != nil {
		return "", err
	}
	signingInput := b64.EncodeToString(h) + "." + b64.EncodeToString(p)
	sig := b64.EncodeToString(hs256([]byte(signingInput), secret))
	return signingInput + "." + sig, nil
}

// ── ПЕРЕВІРКА ────────────────────────────────────────────────────────────────
func Verify(token string, secret []byte, leeway time.Duration) (map[string]any, error) {
	parts := strings.Split(token, ".")
	if len(parts) != 3 {
		return nil, ErrInvalid
	}
	headerJSON, err := b64.DecodeString(parts[0])
	if err != nil {
		return nil, ErrInvalid
	}
	var header struct {
		Alg string `json:"alg"`
	}
	if json.Unmarshal(headerJSON, &header) != nil {
		return nil, ErrInvalid
	}
	// (1) АЛГОРИТМ ПРИБИТО
	if header.Alg != "HS256" {
		return nil, ErrInvalid
	}
	// (2) СТАЛИЙ ЧАС: hmac.Equal порівнює до кінця незалежно від вмісту
	sig, err := b64.DecodeString(parts[2])
	if err != nil {
		return nil, ErrInvalid
	}
	if !hmac.Equal(hs256([]byte(parts[0]+"."+parts[1]), secret), sig) {
		return nil, ErrInvalid
	}
	// (3) ЧАСОВІ ТВЕРДЖЕННЯ
	payloadJSON, err := b64.DecodeString(parts[1])
	if err != nil {
		return nil, ErrInvalid
	}
	var claims map[string]any
	if json.Unmarshal(payloadJSON, &claims) != nil {
		return nil, ErrInvalid
	}
	now, skew := time.Now().Unix(), int64(leeway.Seconds())
	if exp, ok := asUnix(claims["exp"]); ok && now > exp+skew {
		return nil, ErrInvalid
	}
	if nbf, ok := asUnix(claims["nbf"]); ok && now+skew < nbf {
		return nil, ErrInvalid
	}
	if iat, ok := asUnix(claims["iat"]); ok && now+skew < iat {
		return nil, ErrInvalid
	}
	return claims, nil
}

// JSON-числа в Go розпаковуються у float64 — обережно з ними.
func asUnix(v any) (int64, bool) {
	f, ok := v.(float64)
	return int64(f), ok
}
