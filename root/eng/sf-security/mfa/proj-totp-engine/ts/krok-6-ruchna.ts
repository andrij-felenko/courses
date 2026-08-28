export function resynchronizeClock(
  secretBase32: string,
  code1: string,
  code2: string,
  currentTimestampSeconds: number,
  maxDriftSteps: number = 50,
  timeStep: number = 30
): { success: boolean; driftOffset?: number } {
  const secretBytes = decodeBase32(secretBase32);
  const currentStep = Math.floor(currentTimestampSeconds / timeStep);

  for (let drift = -maxDriftSteps; drift <= maxDriftSteps; drift++) {
    const expected1 = generateTOTPCode(secretBytes, (currentStep + drift) * timeStep, timeStep);
    const expected2 = generateTOTPCode(secretBytes, (currentStep + drift + 1) * timeStep, timeStep);

    const a1 = Buffer.from(code1.trim());
    const b1 = Buffer.from(expected1);
    const a2 = Buffer.from(code2.trim());
    const b2 = Buffer.from(expected2);

    if (
      a1.length === b1.length && crypto.timingSafeEqual(a1, b1) &&
      a2.length === b2.length && crypto.timingSafeEqual(a2, b2)
    ) {
      return { success: true, driftOffset: drift };
    }
  }

  return { success: false };
}
