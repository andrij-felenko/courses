import crypto from 'node:crypto';

export interface SecretKeyring {
  primary: string;
  secondary?: string;
}

/**
 * Верифікує підпис вебхука з підтримкою безшовної ротації через кільце ключів.
 */
export function verifySignatureWithKeyring(
  rawBody: Buffer,
  timestamp: number,
  signatures: string[],
  keyring: SecretKeyring
): { isValid: boolean; matchedKey: 'primary' | 'secondary' | 'none' } {
  const signedPayload = Buffer.concat([
    Buffer.from(`${timestamp}.`, 'utf8'),
    rawBody,
  ]);

  // Перевірка основним активним ключем
  if (matchesHmac(signedPayload, signatures, keyring.primary)) {
    return { isValid: true, matchedKey: 'primary' };
  }

  // Якщо основний не підійшов, перевіряємо вторинний (перехідний) ключ
  if (keyring.secondary && matchesHmac(signedPayload, signatures, keyring.secondary)) {
    return { isValid: true, matchedKey: 'secondary' };
  }

  return { isValid: false, matchedKey: 'none' };
}

function matchesHmac(payload: Buffer, signatures: string[], secret: string): boolean {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  const expectedBuffer = Buffer.from(expectedSignature, 'utf8');

  for (const sig of signatures) {
    const clientBuffer = Buffer.from(sig, 'utf8');
    if (
      clientBuffer.length === expectedBuffer.length &&
      crypto.timingSafeEqual(clientBuffer, expectedBuffer)
    ) {
      return true;
    }
  }
  return false;
}
