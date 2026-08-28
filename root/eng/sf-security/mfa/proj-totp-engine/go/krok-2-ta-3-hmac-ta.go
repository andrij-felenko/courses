package totp

import (
	"crypto/hmac"
	"crypto/sha1"
	"encoding/binary"
	"fmt"
	"math"
)

func GenerateTOTPCode(secret []byte, timestamp int64, timeStep int64, digits int) string {
	counter := uint64(timestamp / timeStep)
	buf := make([]byte, 8)
	binary.BigEndian.PutUint64(buf, counter)

	mac := hmac.New(sha1.New, secret)
	mac.Write(buf)
	digest := mac.Sum(nil)

	offset := digest[len(digest)-1] & 0x0f
	binaryCode := binary.BigEndian.Uint32(digest[offset:offset+4]) & 0x7fffffff

	mod := uint32(math.Pow10(digits))
	otp := binaryCode % mod

	format := fmt.Sprintf("%%0%dd", digits)
	return fmt.Sprintf(format, otp)
}
