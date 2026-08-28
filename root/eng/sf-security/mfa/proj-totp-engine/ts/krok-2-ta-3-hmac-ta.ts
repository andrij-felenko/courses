export function generateTOTPCode(
  secretBytes: Buffer,
  timestampSeconds: number,
  timeStep: number = 30,
  digits: number = 6
): string {
  const counter = Math.floor(timestampSeconds / timeStep);
  
  // 64-бітний лічильник у форматі Big-Endian (8 байтів)
  const counterBuffer = Buffer.alloc(8);
  counterBuffer.writeBigUInt64BE(BigInt(counter), 0);

  const hmac = crypto.createHmac("sha1", secretBytes);
  hmac.update(counterBuffer);
  const digest = hmac.digest();

  // Dynamic Truncation за RFC 4226 §5.4
  const offset = digest[digest.length - 1] & 0x0f;
  const binaryCode =
    ((digest[offset] & 0x7f) << 24) |
    ((digest[offset + 1] & 0xff) << 16) |
    ((digest[offset + 2] & 0xff) << 8) |
    (digest[offset + 3] & 0xff);

  const otp = binaryCode % Math.pow(10, digits);
  return otp.toString().padStart(digits, "0");
}
