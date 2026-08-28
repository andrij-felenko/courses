const NONCE_TTL = 30_000;              // мс — скільки живе виклик
const ALLOWED = 'SHA-256';             // рівень захисту обираємо МИ

/** Виклик, який нікуди не треба класти: мітка часу відкрито + підпис її ж. */
export function makeNonce(secret: Buffer, etag = ''): string {
  const stamp = String(Date.now());
  const mark = createHmac('sha256', secret).update(`${stamp}:${etag}`).digest('hex');
  return Buffer.from(`${stamp}:${mark}`).toString('base64');
}

export type NonceState = 'fresh' | 'stale' | 'bad';

export function checkNonce(secret: Buffer, etag: string, nonce: string,
                           ttl = NONCE_TTL): NonceState {
  const raw = Buffer.from(nonce, 'base64').toString('utf8');
  const i = raw.indexOf(':');
  if (i < 0) return 'bad';
  const [stamp, mark] = [raw.slice(0, i), raw.slice(i + 1)];
  const want = createHmac('sha256', secret).update(`${stamp}:${etag}`).digest('hex');
  const a = Buffer.from(want), b = Buffer.from(mark);
  if (a.length !== b.length || !timingSafeEqual(a, b)) return 'bad';  // не наш виклик
  const age = Date.now() - Number(stamp);
  return Number.isFinite(age) && age >= 0 && age < ttl ? 'fresh' : 'stale';
}

export type Verdict = 'ok' | 'stale' | 'challenge' | 'bad-request';

/** method і target беремо З САМОГО ЗАПИТУ; заголовок — лише заявка. */
export function authenticate(
  secret: Buffer, ha1Store: Map<string, string>, seen: Map<string, number>,
  method: string, target: string, header: string | undefined, etag = '',
): Verdict {
  const ch = parseChallenges(header ?? '')[0];
  if (!ch || ch.scheme !== 'digest') return 'challenge';
  const p = ch.params;

  if (p.uri !== target) return 'bad-request';        // доказ порахований під інший шлях
  if ((p.algorithm ?? 'MD5').toUpperCase() !== ALLOWED) return 'challenge';

  const state = checkNonce(secret, etag, p.nonce ?? '');
  if (state !== 'fresh') return state === 'stale' ? 'stale' : 'challenge';

  const nc = /^[0-9a-fA-F]{8}$/.test(p.nc ?? '') ? parseInt(p.nc, 16) : NaN;
  if (!Number.isFinite(nc) || nc <= (seen.get(p.nonce) ?? 0)) return 'challenge';

  const ha1 = ha1Store.get(`${p.username} ${p.realm} ${ALLOWED}`);
  if (!ha1) return 'challenge';                      // хто це — не пояснюємо

  const H = (s: string) => createHash(ALGORITHMS[ALLOWED].hash).update(s, 'utf8').digest('hex');
  const ha2 = H(`${method}:${target}`);              // ← з запиту, не з p.uri
  const want = H(`${ha1}:${p.nonce}:${p.nc}:${p.cnonce ?? ''}:${p.qop ?? ''}:${ha2}`);
  const a = Buffer.from(want), b = Buffer.from(p.response ?? '');
  if (a.length !== b.length || !timingSafeEqual(a, b)) return 'challenge';

  seen.set(p.nonce, nc);                             // запам'ятовуємо ЛИШЕ підтверджений
  return 'ok';
}
