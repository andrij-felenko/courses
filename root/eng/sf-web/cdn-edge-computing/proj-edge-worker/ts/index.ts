/**
 * Edge Worker: Перехоплення запитів, валідація JWT та stale-while-revalidate кеш.
 * Сумісний зі стандартами Web Fetch API (Cloudflare Workers, Fastly Compute, Node.js).
 */

interface CacheEntry {
  body: ArrayBuffer;
  headers: Record<string, string>;
  status: number;
  cachedAt: number;
  maxAge: number;
  staleWindow: number;
}

// In-Memory LRU сховище для крайового вузла
const memoryCache = new Map<string, CacheEntry>();
const MAX_CACHE_ITEMS = 5000;

// Секретний ключ для перевірки підпису HMAC-SHA256
const JWT_SECRET = "super-secret-edge-signing-key-2026";

/**
 * Нормалізація URL: видалення маркетингових параметрів та сортування ключів
 */
function normalizeCacheKey(urlStr: string): string {
  const url = new URL(urlStr);
  const ignoredParams = new Set(["utm_source", "utm_medium", "utm_campaign", "gclid", "fbclid"]);
  
  const sortedParams = new URLSearchParams();
  const keys = Array.from(url.searchParams.keys()).sort();
  
  for (const k of keys) {
    if (!ignoredParams.has(k.toLowerCase())) {
      const values = url.searchParams.getAll(k);
      for (const v of values) {
        sortedParams.append(k, v);
      }
    }
  }
  
  url.search = sortedParams.toString();
  return url.origin + url.pathname + (url.search ? "?" + url.search : "");
}

/**
 * Валідація JWT-токена за алгоритмом HMAC-SHA256 через Web Crypto API
 */
async function verifyJwtAtEdge(authHeader: string | null): Promise<boolean> {
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return false;
  }
  
  const token = authHeader.slice(7).trim();
  const parts = token.split(".");
  if (parts.length !== 3) {
    return false;
  }
  
  const [encodedHeader, encodedPayload, signature] = parts;
  
  try {
    // 1. Перевірка терміну придатності з payload
    const payloadStr = atob(encodedHeader.replace(/-/g, "+").replace(/_/g, "/"));
    const payloadJson = JSON.parse(atob(encodedPayload.replace(/-/g, "+").replace(/_/g, "/")));
    const nowSec = Math.floor(Date.now() / 1000);
    
    if (payloadJson.exp && payloadJson.exp < nowSec) {
      return false; // Токен прострочений
    }
    
    // 2. Криптографічна перевірка підпису через WebCrypto
    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
      "raw",
      encoder.encode(JWT_SECRET),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["verify"]
    );
    
    const dataToSign = encoder.encode(`${encodedHeader}.${encodedPayload}`);
    const binarySignature = Uint8Array.from(
      atob(signature.replace(/-/g, "+").replace(/_/g, "/")),
      (c) => c.charCodeAt(0)
    );
    
    return await crypto.subtle.verify("HMAC", key, binarySignature, dataToSign);
  } catch {
    return false;
  }
}

/**
 * Асинхронне оновлення кешу у фоні без блокування клієнта
 */
async function revalidateInBackground(cacheKey: string, originUrl: string, request: Request): Promise<void> {
  try {
    const originResponse = await fetch(originUrl, {
      method: "GET",
      headers: request.headers,
    });
    
    if (originResponse.ok) {
      const responseBuffer = await originResponse.arrayBuffer();
      const headersMap: Record<string, string> = {};
      originResponse.headers.forEach((val, key) => {
        headersMap[key] = val;
      });
      
      // Парсинг директив Cache-Control
      const cc = originResponse.headers.get("cache-control") || "";
      let maxAge = 60;
      let staleWindow = 300;
      
      const maxAgeMatch = cc.match(/s-maxage=(\d+)|max-age=(\d+)/);
      if (maxAgeMatch) {
        maxAge = parseInt(maxAgeMatch[1] || maxAgeMatch[2], 10);
      }
      
      const staleMatch = cc.match(/stale-while-revalidate=(\d+)/);
      if (staleMatch) {
        staleWindow = parseInt(staleMatch[1], 10);
      }
      
      // Оновлення кешу
      if (memoryCache.size >= MAX_CACHE_ITEMS) {
        const oldestKey = memoryCache.keys().next().value;
        if (oldestKey) memoryCache.delete(oldestKey);
      }
      
      memoryCache.set(cacheKey, {
        body: responseBuffer,
        headers: headersMap,
        status: originResponse.status,
        cachedAt: Date.now(),
        maxAge,
        staleWindow,
      });
    }
  } catch (err) {
    console.error("Background revalidation failed for", cacheKey, err);
  }
}

/**
 * Головний обробник подій крайового рантайму
 */
export default {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    
    // 1. Пропускаємо мутаційні запити (POST, PUT, DELETE) напряму на Origin
    if (request.method !== "GET" && request.method !== "HEAD") {
      return fetch(request);
    }
    
    // 2. Валідація JWT-авторизації на захищених маршрутах
    if (url.pathname.startsWith("/api/protected/")) {
      const isValid = await verifyJwtAtEdge(request.headers.get("Authorization"));
      if (!isValid) {
        return new Response(JSON.stringify({ error: "Unauthorized: Invalid or expired JWT" }), {
          status: 401,
          headers: { "Content-Type": "application/json", "X-Edge-Auth": "Rejected" },
        });
      }
    }
    
    // 3. Формування нормалізованого ключа кешування
    const cacheKey = normalizeCacheKey(request.url);
    const now = Date.now();
    const entry = memoryCache.get(cacheKey);
    
    if (entry) {
      const ageSeconds = Math.floor((now - entry.cachedAt) / 1000);
      
      // А. Свіжий кеш (Fresh Hit)
      if (ageSeconds <= entry.maxAge) {
        const resHeaders = new Headers(entry.headers);
        resHeaders.set("X-Cache-Status", "HIT");
        resHeaders.set("Age", ageSeconds.toString());
        return new Response(entry.body, { status: entry.status, headers: resHeaders });
      }
      
      // Б. Застарілий кеш у вікні revalidation (Stale Hit)
      if (ageSeconds <= entry.maxAge + entry.staleWindow) {
        // Запуск неблокуючого оновлення
        revalidateInBackground(cacheKey, request.url, request);
        
        const resHeaders = new Headers(entry.headers);
        resHeaders.set("X-Cache-Status", "STALE");
        resHeaders.set("Age", ageSeconds.toString());
        return new Response(entry.body, { status: entry.status, headers: resHeaders });
      }
    }
    
    // 4. Промах повз кеш (Cache Miss): прямий синхронний запит до Origin
    try {
      const originRes = await fetch(request);
      if (!originRes.ok && entry) {
        // Відкат до Stale-if-error при падінні бекенду
        const resHeaders = new Headers(entry.headers);
        resHeaders.set("X-Cache-Status", "STALE-ERROR-FALLBACK");
        return new Response(entry.body, { status: entry.status, headers: resHeaders });
      }
      
      // Збереження в кеш для наступних користувачів
      if (originRes.ok) {
        const bodyBuf = await originRes.arrayBuffer();
        const headersObj: Record<string, string> = {};
        originRes.headers.forEach((v, k) => { headersObj[k] = v; });
        
        memoryCache.set(cacheKey, {
          body: bodyBuf,
          headers: headersObj,
          status: originRes.status,
          cachedAt: now,
          maxAge: 60,
          staleWindow: 300,
        });
        
        const outHeaders = new Headers(originRes.headers);
        outHeaders.set("X-Cache-Status", "MISS");
        return new Response(bodyBuf, { status: originRes.status, headers: outHeaders });
      }
      
      return originRes;
    } catch (err) {
      if (entry) {
        const resHeaders = new Headers(entry.headers);
        resHeaders.set("X-Cache-Status", "STALE-NETWORK-FALLBACK");
        return new Response(entry.body, { status: entry.status, headers: resHeaders });
      }
      throw err;
    }
  },
};
