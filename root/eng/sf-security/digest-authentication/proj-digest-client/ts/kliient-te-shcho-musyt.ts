const QUOTED = new Set(['username', 'realm', 'nonce', 'uri', 'response', 'cnonce', 'opaque']);
const field = (k: string, v: string) =>
  QUOTED.has(k)
    ? `${k}="${v.replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`
    : `${k}=${v}`;                       // algorithm, qop, nc — БЕЗ лапок

export type Ctx = { H: (d: string) => string; secret: string; nonce: string;
                    nc: string; cnonce: string; qop: string; uri: string };

export class DigestClient {
  readonly #counts = new Map<string, number>();      // nonce → скільки запитів уже пішло
  readonly #sess = new Map<string, { key: string; cnonce: string }>();
  readonly #user: string;
  readonly #password: string;

  constructor(user: string, password: string) { this.#user = user; this.#password = password; }

  authorization(ch: Challenge, method: string, target: string, body = Buffer.alloc(0)) {
    const p = ch.params;
    const declared = p.algorithm ?? 'MD5';
    const { base, sess } = splitAlg(declared);
    const name = ALGORITHMS[base].hash;
    const Hb = (b: Buffer) => createHash(name).update(b).digest('hex');
    const H = (s: string) => Hb(Buffer.from(s, 'utf8'));   // пароль — саме UTF-8

    const nonce = p.nonce;
    const n = (this.#counts.get(nonce) ?? 0) + 1;
    this.#counts.set(nonce, n);
    const nc = n.toString(16).padStart(8, '0');            // рівно 8 шістнадцяткових цифр
    let cnonce = randomBytes(16).toString('hex');          // непередбачуване, не «щоразу інше»

    let secret = H(`${this.#user}:${p.realm}:${this.#password}`);
    if (sess) {                                    // ключ сеансу рахуємо ОДИН раз на виклик
      if (!this.#sess.has(nonce))
        this.#sess.set(nonce, { key: H(`${secret}:${nonce}:${cnonce}`), cnonce });
      const kept = this.#sess.get(nonce)!;
      secret = kept.key; cnonce = kept.cnonce;             // і cnonce більше не міняємо
    }

    const offered = (p.qop ?? 'auth').split(',').map((s) => s.trim());
    const qop = offered.includes('auth') ? 'auth' : 'auth-int';
    const a2 = qop === 'auth' ? `${method}:${target}` : `${method}:${target}:${Hb(body)}`;
    const response = H(`${secret}:${nonce}:${nc}:${cnonce}:${qop}:${H(a2)}`);

    const fields: Record<string, string> = {
      username: this.#user, realm: p.realm, uri: target, algorithm: declared,
      nonce, nc, cnonce, qop, response,
      ...(p.opaque !== undefined ? { opaque: p.opaque } : {}),   // повертаємо як є
    };
    const header = 'Digest ' + Object.entries(fields).map(([k, v]) => field(k, v)).join(', ');
    return { header, ctx: { H, secret, nonce, nc, cnonce, qop, uri: target } as Ctx };
  }

  /** Authentication-Info: чи знає співрозмовник те саме H(A1). */
  verifyRspauth(ctx: Ctx, infoHeader: string): boolean {
    const rspauth = parseParams(infoHeader).rspauth;
    if (!rspauth) return false;
    const ha2 = ctx.H(`:${ctx.uri}`);              // ← БЕЗ методу: його обирали не ми
    const want = ctx.H(`${ctx.secret}:${ctx.nonce}:${ctx.nc}:${ctx.cnonce}:${ctx.qop}:${ha2}`);
    const a = Buffer.from(want), b = Buffer.from(rspauth);
    return a.length === b.length && timingSafeEqual(a, b);
  }
}
