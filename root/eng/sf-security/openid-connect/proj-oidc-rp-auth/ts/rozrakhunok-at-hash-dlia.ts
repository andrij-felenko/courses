import crypto from 'crypto';

export async function validateIdToken(
  idTokenRaw: string,
  expectedIssuer: string,
  expectedClientId: string,
  expectedNonce: string,
  jwksManager: JwksManager,
  accessTokenRaw?: string,
  clockSkewSec: number = 60
): Promise<Record<string, any>> {
  const parts = idTokenRaw.split('.');
  if (parts.length !== 3) throw new Error('Некоректний формат JWT');
  const [headerB64, payloadB64, sigB64] = parts;

  // 1. Розбір заголовка
  const header = JSON.parse(Buffer.from(headerB64, 'base64url').toString('utf8'));
  if (header.alg !== 'RS256') throw new Error(`Недозволений алгоритм: ${header.alg}`);
  if (!header.kid) throw new Error('У заголовку токена відсутній kid');

  // 2. Верифікація підпису
  const publicKey = await jwksManager.getKey(header.kid);
  const verify = crypto.createVerify('RSA-SHA256');
  verify.update(`${headerB64}.${payloadB64}`, 'ascii');
  const sigBuffer = Buffer.from(sigB64, 'base64url');
  
  const isValid = verify.verify(publicKey, sigBuffer);
  if (!isValid) throw new Error('Цифровий підпис ID-токена недійсний');

  // 3. Розбір навантаження
  const payload = JSON.parse(Buffer.from(payloadB64, 'base64url').toString('utf8'));
  const now = Math.floor(Date.now() / 1000);

  // 4. Перевірка iss
  if (payload.iss !== expectedIssuer) {
    throw new Error(`Невідповідність iss: ${payload.iss} !== ${expectedIssuer}`);
  }

  // 5. Перевірка aud
  if (typeof payload.aud === 'string') {
    if (payload.aud !== expectedClientId) throw new Error(`Невідповідність aud: ${payload.aud}`);
  } else if (Array.isArray(payload.aud)) {
    if (!payload.aud.includes(expectedClientId)) throw new Error('client_id відсутній в aud');
    if (payload.aud.length > 1 && payload.azp !== expectedClientId) {
      throw new Error('azp не збігається з client_id для множинного aud');
    }
  } else {
    throw new Error('Некоректне поле aud у токені');
  }

  // 6. Перевірка часу
  if (!payload.exp || payload.exp + clockSkewSec < now) throw new Error('Токен протерміновано (exp)');
  if (payload.iat && payload.iat - clockSkewSec > now) throw new Error('Токен із майбутнього (iat)');

  // 7. Перевірка nonce
  if (payload.nonce !== expectedNonce) throw new Error('Невідповідність nonce');

  // 8. Перевірка at_hash
  if (accessTokenRaw && payload.at_hash) {
    const hash = crypto.createHash('sha256').update(accessTokenRaw, 'ascii').digest();
    const half = hash.subarray(0, hash.length / 2);
    const expectedAtHash = half.toString('base64url');
    if (payload.at_hash !== expectedAtHash) {
      throw new Error('at_hash не відповідає access_token');
    }
  }

  return payload;
}
