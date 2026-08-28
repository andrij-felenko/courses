export interface VerificationResult {
  valid: boolean;
  verifiedStep?: number;
}

export function verifyTOTPCode(
  secretBase32: string,
  userInputCode: string,
  currentTimestampSeconds: number,
  lastVerifiedStep: number = 0,
  window: number = 1,
  timeStep: number = 30
): VerificationResult {
  const cleanCode = userInputCode.trim();
  if (!/^\d{6}$/.test(cleanCode)) {
    return { valid: false };
  }

  const secretBytes = decodeBase32(secretBase32);
  const currentStep = Math.floor(currentTimestampSeconds / timeStep);

  for (let offset = -window; offset <= window; offset++) {
    const step = currentStep + offset;

    // Захист від повтору: крок уже використовувався в минулому
    if (step <= lastVerifiedStep) {
      continue;
    }

    const expectedCode = generateTOTPCode(secretBytes, step * timeStep, timeStep);
    
    // Безпечне порівняння за сталий час
    const a = Buffer.from(cleanCode);
    const b = Buffer.from(expectedCode);
    if (a.length === b.length && crypto.timingSafeEqual(a, b)) {
      return { valid: true, verifiedStep: step };
    }
  }

  return { valid: false };
}
