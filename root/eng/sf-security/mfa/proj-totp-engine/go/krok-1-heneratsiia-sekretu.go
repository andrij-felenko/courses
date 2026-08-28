package totp

import (
	"crypto/rand"
	"encoding/base32"
	"fmt"
	"net/url"
	"strings"
)

var b32Encoding = base32.StdEncoding.WithPadding(base32.NoPadding)

func GenerateBase32Secret(byteLength int) (string, error) {
	buf := make([]byte, byteLength)
	if _, err := rand.Read(buf); err != nil {
		return "", err
	}
	return b32Encoding.EncodeToString(buf), nil
}

func DecodeBase32(secret string) ([]byte, error) {
	clean := strings.ToUpper(strings.ReplaceAll(strings.ReplaceAll(secret, " ", ""), "-", ""))
	return b32Encoding.DecodeString(clean)
}

func BuildTotpURI(issuer, accountName, secretBase32 string) string {
	label := fmt.Sprintf("%s:%s", issuer, accountName)
	v := url.Values{}
	v.Set("secret", secretBase32)
	v.Set("issuer", issuer)
	v.Set("algorithm", "SHA1")
	v.Set("digits", "6")
	v.Set("period", "30")

	return fmt.Sprintf("otpauth://totp/%s?%s", url.PathEscape(label), v.Encode())
}
