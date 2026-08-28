import crypto from 'crypto';

interface JwkKey {
  kty: string;
  use?: string;
  kid?: string;
  alg?: string;
  n: string;
  e: string;
}

export class JwksManager {
  private jwksUri: string;
  private ttlMs: number;
  private keys: Map<string, crypto.KeyObject> = new Map();
  private lastFetched: number = 0;
  private minIntervalMs: number = 10000;

  constructor(jwksUri: string, ttlSeconds: number = 86400) {
    this.jwksUri = jwksUri;
    this.ttlMs = ttlSeconds * 1000;
  }

  private async fetchKeys(): Promise<void> {
    const res = await fetch(this.jwksUri, {
      headers: { 'User-Agent': 'OIDC-RelyingParty-Engine/1.0', Accept: 'application/json' },
    });
    if (!res.ok) throw new Error(`Помилка отримання JWKS: HTTP ${res.status}`);
    const data = (await res.json()) as { keys: JwkKey[] };

    const newMap = new Map<string, crypto.KeyObject>();
    for (const key of data.keys || []) {
      if (key.kty === 'RSA' && (key.use === undefined || key.use === 'sig')) {
        const jwkObj: crypto.JsonWebKey = {
          kty: 'RSA',
          n: key.n,
          e: key.e,
        };
        const keyObject = crypto.createPublicKey({ key: jwkObj, format: 'jwk' });
        if (key.kid) {
          newMap.set(key.kid, keyObject);
        }
      }
    }
    this.keys = newMap;
    this.lastFetched = Date.now();
  }

  public async getKey(kid: string): Promise<crypto.KeyObject> {
    const now = Date.now();
    if (now - this.lastFetched > this.ttlMs || this.keys.size === 0) {
      await this.fetchKeys();
    }

    if (!this.keys.has(kid)) {
      if (now - this.lastFetched > this.minIntervalMs) {
        await this.fetchKeys();
      }
    }

    const key = this.keys.get(kid);
    if (!key) throw new Error(`Відкритий ключ kid='${kid}' відсутній у наборі JWKS`);
    return key;
  }
}
