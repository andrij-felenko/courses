import crypto from "node:crypto";

export interface ParsedAuthData {
  rpIdHash: Buffer;
  flags: {
    userPresent: boolean;
    userVerified: boolean;
    backupEligible: boolean;
    backupState: boolean;
    hasAttestedCredentialData: boolean;
  };
  signCount: number;
  aaguid?: string;
  credentialId?: Buffer;
  cosePublicKey?: Buffer;
}

export function parseAuthData(authData: Buffer): ParsedAuthData {
  if (authData.length < 37) {
    throw new Error("authData buffer is too small (< 37 bytes)");
  }

  const rpIdHash = authData.subarray(0, 32);
  const flagByte = authData[32];
  const signCount = authData.readUInt32BE(33);

  const flags = {
    userPresent: (flagByte & 0x01) !== 0,
    userVerified: (flagByte & 0x04) !== 0,
    backupEligible: (flagByte & 0x08) !== 0,
    backupState: (flagByte & 0x10) !== 0,
    hasAttestedCredentialData: (flagByte & 0x40) !== 0,
  };

  let offset = 37;
  let aaguid: string | undefined;
  let credentialId: Buffer | undefined;
  let cosePublicKey: Buffer | undefined;

  if (flags.hasAttestedCredentialData) {
    if (authData.length < offset + 18) {
      throw new Error("Truncated attested credential data header");
    }

    const aaguidBuf = authData.subarray(offset, offset + 16);
    aaguid = aaguidBuf.toString("hex").replace(
      /(.{8})(.{4})(.{4})(.{4})(.{12})/,
      "$1-$2-$3-$4-$5"
    );
    offset += 16;

    const credIdLen = authData.readUInt16BE(offset);
    offset += 2;

    if (authData.length < offset + credIdLen) {
      throw new Error("Truncated credentialId buffer");
    }

    credentialId = authData.subarray(offset, offset + credIdLen);
    offset += credIdLen;

    // Решта буфера містить бінарний CBOR COSE Public Key
    cosePublicKey = authData.subarray(offset);
  }

  return { rpIdHash, flags, signCount, aaguid, credentialId, cosePublicKey };
}

export function verifyRegistrationResponse(params: {
  clientDataJSON: Buffer;
  authData: Buffer;
  expectedChallenge: string;
  expectedOrigin: string;
  expectedRpId: string;
}) {
  // 1. Декодування та перевірка clientDataJSON
  const clientData = JSON.parse(params.clientDataJSON.toString("utf8"));
  if (clientData.type !== "webauthn.create") {
    throw new Error(`Invalid ceremony type: ${clientData.type}`);
  }
  if (clientData.challenge !== params.expectedChallenge) {
    throw new Error("Challenge mismatch");
  }
  if (clientData.origin !== params.expectedOrigin) {
    throw new Error(`Origin mismatch: expected ${params.expectedOrigin}, got ${clientData.origin}`);
  }

  // 2. Двійковий розбір та перевірка authData
  const parsed = parseAuthData(params.authData);

  const expectedRpIdHash = crypto.createHash("sha256").update(params.expectedRpId).digest();
  if (!parsed.rpIdHash.equals(expectedRpIdHash)) {
    throw new Error("rpIdHash does not match expected RP ID");
  }

  if (!parsed.flags.userPresent) {
    throw new Error("User Presence (UP) flag was not set");
  }
  if (!parsed.flags.hasAttestedCredentialData || !parsed.credentialId || !parsed.cosePublicKey) {
    throw new Error("Attested Credential Data is missing from registration");
  }

  return {
    credentialId: parsed.credentialId.toString("base64url"),
    cosePublicKey: parsed.cosePublicKey,
    signCount: parsed.signCount,
    aaguid: parsed.aaguid!,
    backupEligible: parsed.flags.backupEligible,
    backupState: parsed.flags.backupState,
  };
}
