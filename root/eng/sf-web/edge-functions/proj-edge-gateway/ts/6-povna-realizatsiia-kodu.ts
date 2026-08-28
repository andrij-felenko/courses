// ============================================================================
// Edge API Gateway: TypeScript (WinterCG / Cloudflare Workers / Deno)
// ============================================================================

interface Env {
  JWT_SECRET: string;
  UPSTREAM_ORIGIN: string;
  ANALYTICS_ENDPOINT?: string;
}

interface JwtPayload {
  sub: string;
  role: string;
  exp: number;
  [key: string]: unknown;
}

// ── Допоміжні функції декодування Base64URL ──
function base64UrlDecode(str: string): Uint8Array {
  let base64 = str.replace(/-/g, '+').replace(/_/g, '/');
  while (base64.length % 4 !== 0) {
    base64 += '=';
  }
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

// ── Хешування FNV-1a для детермінованого A/B спліту ──
function hashFnv1a32(str: string): number {
  let hash = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    hash ^= str.charCodeAt(i);
    hash = Math.imul(hash, 0x01000193) >>> 0;
  }
  return hash;
}

// ── Кеш імпортованого криптографічного ключа ──
let cachedCryptoKey: CryptoKey | null = null;
let cachedSecretStr: string | null = null;

async function getHmacKey(secret: string): Promise<CryptoKey> {
  if (cachedCryptoKey && cachedSecretStr === secret) {
    return cachedCryptoKey;
  }
  const encoder = new TextEncoder();
  cachedCryptoKey = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['verify']
  );
  cachedSecretStr = secret;
  return cachedCryptoKey;
}

// ── Валідація токена JWT через WebCrypto ──
async function verifyJwt(token: string, secret: string): Promise<JwtPayload | null> {
  const parts = token.split('.');
  if (parts.length !== 3) return null;

  const [headerB64, payloadB64, signatureB64] = parts;

  // 1. Перевірка структури заголовка
  try {
    const headerJson = new TextDecoder().decode(base64UrlDecode(headerB64));
    const header = JSON.parse(headerJson);
    if (header.alg !== 'HS256' || header.typ !== 'JWT') return null;
  } catch {
    return null;
  }

  // 2. Отримання ключа
  const key = await getHmacKey(secret);

  // 3. Перевірка підпису через константний час WebCrypto
  const encoder = new TextEncoder();
  const data = encoder.encode(`${headerB64}.${payloadB64}`);
  const signature = base64UrlDecode(signatureB64);

  const isValid = await crypto.subtle.verify(
    'HMAC',
    key,
    signature,
    data
  );

  if (!isValid) return null;

  // 4. Перевірка строків придатності
  try {
    const payloadJson = new TextDecoder().decode(base64UrlDecode(payloadB64));
    const payload: JwtPayload = JSON.parse(payloadJson);
    const nowSec = Math.floor(Date.now() / 1000);
    if (payload.exp && payload.exp < nowSec) {
      return null; // Термін придатності токена вичерпано
    }
    return payload;
  } catch {
    return null;
  }
}

// ── Головний експорт обробника Edge Gateway ──
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const startTime = performance.now();
    const url = new URL(request.url);

    // Дозволяємо прямий доступ до службових маршрутів здоров'я
    if (url.pathname === '/healthz' || url.pathname.startsWith('/public/')) {
      return fetch(request);
    }

    // ── Крок 1: Автентифікація токена JWT ──
    const authHeader = request.headers.get('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return new Response(JSON.stringify({ error: 'Missing or malformed Authorization header' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json', 'WWW-Authenticate': 'Bearer' }
      });
    }

    const token = authHeader.substring(7);
    const payload = await verifyJwt(token, env.JWT_SECRET);
    if (!payload) {
      return new Response(JSON.stringify({ error: 'Invalid or expired JWT token' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // ── Крок 2: Детермінований A/B спліт та геолокація ──
    let abCookie = '';
    const cookieHeader = request.headers.get('Cookie') || '';
    const match = cookieHeader.match(/_ab_id=([a-zA-Z0-9_-]+)/);
    let userId = payload.sub;
    let isNewCookie = false;

    if (match) {
      abCookie = match[1];
    } else {
      abCookie = crypto.randomUUID();
      isNewCookie = true;
    }

    const hashVal = hashFnv1a32(abCookie);
    const bucket = hashVal % 100;
    const variant = bucket < 80 ? 'control-v1' : 'experiment-v2';
    const userCountry = request.cf?.country || 'UNKNOWN';

    // ── Крок 3: Перевірка крайового кешу (Cache API) ──
    const cache = caches.default;
    const cacheKey = new Request(url.toString(), request);
    let response = await cache.match(cacheKey);
    let cacheHit = false;

    if (response) {
      cacheHit = true;
    } else {
      // ── Крок 4: Запит до Origin-сервера при промаху кешу ──
      const originUrl = new URL(url.pathname + url.search, env.UPSTREAM_ORIGIN);
      const upstreamHeaders = new Headers(request.headers);
      upstreamHeaders.set('X-User-Id', userId);
      upstreamHeaders.set('X-User-Role', payload.role);
      upstreamHeaders.set('X-AB-Variant', variant);
      upstreamHeaders.set('X-Client-Country', userCountry);

      const originRequest = new Request(originUrl.toString(), {
        method: request.method,
        headers: upstreamHeaders,
        body: request.body,
        redirect: 'follow'
      });

      const originResponse = await fetch(originRequest);

      // ── Крок 5: Потокова модифікація заголовків та тіла через TransformStream ──
      const newHeaders = new Headers(originResponse.headers);
      newHeaders.set('X-Edge-Pop', request.cf?.colo || 'LOCAL');
      newHeaders.set('X-AB-Variant', variant);
      newHeaders.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
      newHeaders.set('X-Content-Type-Options', 'nosniff');

      if (isNewCookie) {
        newHeaders.append('Set-Cookie', `_ab_id=${abCookie}; Path=/; Max-Age=2592000; Secure; SameSite=Lax`);
      }

      // Створення потоку трансформації без буферизації всього тіла
      const { readable, writable } = new TransformStream();
      originResponse.body?.pipeTo(writable);

      response = new Response(readable, {
        status: originResponse.status,
        statusText: originResponse.statusText,
        headers: newHeaders
      });

      // Асинхронний запис у кеш успішних GET відповідей
      if (request.method === 'GET' && originResponse.status === 200) {
        const cacheControl = originResponse.headers.get('Cache-Control');
        if (cacheControl && cacheControl.includes('public')) {
          ctx.waitUntil(cache.put(cacheKey, response.clone()));
        }
      }
    }

    // ── Крок 6: Асинхронний збір та відправка метрик ──
    ctx.waitUntil((async () => {
      const durationMs = performance.now() - startTime;
      const logEntry = {
        timestamp: new Date().toISOString(),
        userId,
        country: userCountry,
        variant,
        cacheHit,
        status: response?.status,
        durationMs: Math.round(durationMs * 100) / 100
      };

      if (env.ANALYTICS_ENDPOINT) {
        await fetch(env.ANALYTICS_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(logEntry)
        }).catch(() => {});
      }
    })());

    return response;
  }
};
