package uuidv7

import (
	"crypto/rand"
	"time"
)

type UUID [16]byte

func New() (UUID, error) {
	var uuid UUID
	now := time.Now().UnixMilli()

	// 48 бітів часу
	uuid[0] = byte(now >> 40)
	uuid[1] = byte(now >> 32)
	uuid[2] = byte(now >> 24)
	uuid[3] = byte(now >> 16)
	uuid[4] = byte(now >> 8)
	uuid[5] = byte(now)

	// Заповнення випадковою ентропією
	if _, err := rand.Read(uuid[6:]); err != nil {
		return uuid, err
	}

	// ver = 7 (0111)
	uuid[6] = (uuid[6] & 0x0F) | 0x70
	// var = 2 (10)
	uuid[8] = (uuid[8] & 0x3F) | 0x80

	return uuid, nil
}
