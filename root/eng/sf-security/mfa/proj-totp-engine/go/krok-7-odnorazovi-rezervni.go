package totp

import (
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"fmt"
	"strings"
)

type BackupCodeRecord struct {
	Hash string
	Used bool
}

func GenerateBackupCodes(count int) ([]string, error) {
	codes := make([]string, count)
	for i := 0; i < count; i++ {
		b := make([]byte, 5)
		if _, err := rand.Read(b); err != nil {
			return nil, err
		}
		raw := hex.EncodeToString(b)
		codes[i] = fmt.Sprintf("%s-%s", raw[:5], raw[5:])
	}
	return codes, nil
}

func HashBackupCode(plain string) string {
	clean := strings.ToLower(strings.ReplaceAll(strings.ReplaceAll(plain, "-", ""), " ", ""))
	h := sha256.Sum256([]byte(clean))
	return hex.EncodeToString(h[:])
}

func VerifyAndConsumeBackupCode(input string, records []BackupCodeRecord) (bool, []BackupCodeRecord) {
	inputHash := HashBackupCode(input)
	for i := range records {
		if !records[i].Used {
			if subtle.ConstantTimeCompare([]byte(records[i].Hash), []byte(inputHash)) == 1 {
				records[i].Used = true
				return true, records
			}
		}
	}
	return false, records
}
