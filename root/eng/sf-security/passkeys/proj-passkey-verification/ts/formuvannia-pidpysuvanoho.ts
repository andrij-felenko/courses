import crypto from "node:crypto";

export function importCoseP256Key(xCoord: Buffer, yCoord: Buffer): crypto.KeyObject {
  // Створюємо нестиснену точку еліптичної кривої: 0x04 || X (32B) || Y (32B)
  const uncompressedPoint = Buffer.concat([Buffer.from([0x04]), xCoord, yCoord]);

  // Заголовок ANSI X9.62 / PKIX для кривої prime256v1 (P-256)
  const ecP256DerHeader = Buffer.from([
    0x30, 0x59, // SEQUENCE (89 байтів)
    0x30, 0x13, // SEQUENCE (ідентифікатор алгоритму, 19 байтів)
    0x06, 0x07, 0x2a, 0x86, 0x48, 0xce, 0x3d, 0x02, 0x01, // OID id-ecPublicKey
    0x06, 0x08, 0x2a, 0x86, 0x48, 0xce, 0x3d, 0x03, 0x01, 0x07, // OID prime256v1
    0x03, 0x42, 0x00, // BIT STRING (66 байтів, 0 невикористаних бітів)
  ]);

  const spkiDer = Buffer.concat([ecP256DerHeader, uncompressedPoint]);
  return crypto.createPublicKey({ key: spkiDer, format: "der", type: "spki" });
}

export function verifyAuthenticationAssertion(params: {
  authData: Buffer;
  clientDataJSON: Buffer;
  signature: Buffer;
  publicKeySpki: Buffer;
  storedSignCount: number;
  expectedChallenge: string;
  expectedOrigin: string;
  expectedRpId: string;
}) {
  // 1. Валідація clientDataJSON
  const clientData = JSON.parse(params.clientDataJSON.toString("utf8"));
  if (clientData.type !== "webauthn.get") {
    throw new Error(`Invalid assertion type: ${clientData.type}`);
  }
  if (clientData.challenge !== params.expectedChallenge) {
    throw new Error("Challenge mismatch");
  }
  if (clientData.origin !== params.expectedOrigin) {
    throw new Error(`Origin mismatch: expected ${params.expectedOrigin}, got ${clientData.origin}`);
  }

  // 2. Валідація authData
  const parsed = parseAuthData(params.authData);
  const expectedRpIdHash = crypto.createHash("sha256").update(params.expectedRpId).digest();
  if (!parsed.rpIdHash.equals(expectedRpIdHash)) {
    throw new Error("rpIdHash does not match RP ID");
  }
  if (!parsed.flags.userPresent) {
    throw new Error("User Presence flag is not set");
  }

  // 3. Формування підписуваного повідомлення: authData || sha256(clientDataJSON)
  const clientDataHash = crypto.createHash("sha256").update(params.clientDataJSON).digest();
  const signedData = Buffer.concat([params.authData, clientDataHash]);

  // 4. Криптографічна перевірка підпису ECDSA (ASN.1 DER)
  const publicKey = crypto.createPublicKey({
    key: params.publicKeySpki,
    format: "der",
    type: "spki",
  });

  const isSignatureValid = crypto.verify(
    "sha256",
    signedData,
    publicKey,
    params.signature
  );

  if (!isSignatureValid) {
    throw new Error("Cryptographic signature verification failed");
  }

  // 5. Перевірка лічильника підписів (signCount)
  if (parsed.signCount > 0 || params.storedSignCount > 0) {
    if (parsed.signCount <= params.storedSignCount) {
      throw new Error(
        `Cloned authenticator detected: incoming signCount (${parsed.signCount}) <= stored (${params.storedSignCount})`
      );
    }
  }

  return {
    verified: true,
    newSignCount: parsed.signCount,
  };
}
