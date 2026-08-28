package totp

import (
	"crypto/subtle"
	"strings"
)

func ResynchronizeClock(
	secretBase32 string,
	code1, code2 string,
	currentTimestamp int64,
	maxDriftSteps int,
	timeStep int64,
) (bool, int) {
	secretBytes, err := DecodeBase32(secretBase32)
	if err != nil {
		return false, 0
	}

	currentStep := currentTimestamp / timeStep
	c1, c2 := strings.TrimSpace(code1), strings.TrimSpace(code2)

	for drift := -maxDriftSteps; drift <= maxDriftSteps; drift++ {
		exp1 := GenerateTOTPCode(secretBytes, (currentStep+int64(drift))*timeStep, timeStep, 6)
		exp2 := GenerateTOTPCode(secretBytes, (currentStep+int64(drift)+1)*timeStep, timeStep, 6)

		m1 := subtle.ConstantTimeCompare([]byte(c1), []byte(exp1))
		m2 := subtle.ConstantTimeCompare([]byte(c2), []byte(exp2))

		if m1 == 1 && m2 == 1 {
			return true, drift
		}
	}

	return false, 0
}
