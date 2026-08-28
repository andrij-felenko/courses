import crypto from "node:crypto";

export interface RegistrationOptions {
  rp: { name: string; id: string };
  user: { id: string; name: string; displayName: string };
  challenge: string; // Base64URL
  pubKeyCredParams: Array<{ type: "public-key"; alg: number }>;
  timeout: number;
  authenticatorSelection: {
    residentKey: "required";
    userVerification: "preferred";
  };
}

export function generateRegistrationOptions(
  user: { id: string; email: string; displayName: string },
  rpId: string
): RegistrationOptions {
  // Генеруємо 32 байти випадкового виклику через CSPRNG
  const challengeBuffer = crypto.randomBytes(32);
  const challenge = challengeBuffer.toString("base64url");

  return {
    rp: {
      name: "Acme Cloud Platform",
      id: rpId,
    },
    user: {
      id: Buffer.from(user.id).toString("base64url"),
      name: user.email,
      displayName: user.displayName,
    },
    challenge,
    pubKeyCredParams: [
      { type: "public-key", alg: -7 },   // ES256 (ECDSA поверх NIST P-256 з SHA-256)
      { type: "public-key", alg: -8 },   // Ed25519 (EdDSA)
      { type: "public-key", alg: -257 }, // RS256 (RSA 2048 з SHA-256)
    ],
    timeout: 60000,
    authenticatorSelection: {
      residentKey: "required", // Вимагаємо створення Passkey для входу в один клік
      userVerification: "preferred",
    },
  };
}
