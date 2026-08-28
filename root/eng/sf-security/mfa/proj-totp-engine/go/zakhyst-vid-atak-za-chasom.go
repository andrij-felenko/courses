package totp

import (
	"crypto/subtle"
	"strings"
)

type VerificationResult struct {
	Valid        bool
	VerifiedStep int64
}

func VerifyTOTPCode(
	secretBase32 string,
	userInputCode string,
	currentTimestamp int64,
	lastVerifiedStep int64,
	window int,
	timeStep int64,
) VerificationResult {
	cleanCode := strings.TrimSpace(userInputCode)
	if len(cleanCode) != 6 {
		return VerificationResult{Valid: false}
	}

	secretBytes, err := DecodeBase32(secretBase32)
	if err != nil {
		return VerificationResult{Valid: false}
	}

	currentStep := currentTimestamp / timeStep

	for offset := -window; offset <= window; offset++ {
		step := currentStep + int64(offset)

		if step <= lastVerifiedStep {
			continue
		}

		expected := GenerateTOTPCode(secretBytes, step*timeStep, timeStep, 6)

		if subtle.ConstantTimeCompare([]byte(cleanCode), []byte(expected)) == 1 {
			return VerificationResult{Valid: true, VerifiedStep: step}
		}
	}

	return VerificationResult{Valid: false}
}
