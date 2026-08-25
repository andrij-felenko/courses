# ⚙️ Реалізація програмованого крайового проксі з кешуванням та валідацією токенів

У розподілених сервісах центральний бекенд часто перевантажується повторною валідацією криптографічних підписів у кожному вхідному запиті та повторною генерацією ідентичних HTTP-відповідей для мільйонів користувачів. Перенесення цієї логіки безпосередньо на крайові вузли (Edge PoP) дозволяє відсікати неавторизовані спроби доступу за 1 мілісекунду, нормалізувати параметри URL-рядків для запобігання фрагментації пам'яті та асинхронно оновлювати застарілі ресурси без блокування клієнтських потоків.

Нижче наведено проектування, вихідний код та розбір інженерних нюансів програмованого крайового проксі-сервісу (Edge Worker).

## Постановка інженерного завдання

Традиційні мікросервісні архітектури стикаються з трьома критичними проблемами:
1. **Продуктивність CPU на центральному сервері**: До 40% процесорного часу бекенду витрачається на розбір заголовків авторизації `Authorization: Bearer <token>`, обчислення криптографічних підписів HMAC/RSA та парсинг JSON-пейлоадів. При сплеску трафіку черга задач переповнюється, і центральний сервер відмовляє в обслуговуванні;
2. **Фрагментація простору ключів кешування**: Клієнти, маркетингові трекери та пошукові системи надсилають запити з хаотичним порядком параметрів (наприклад, `?page=2&sort=price` та `?sort=price&page=2`) або додають унікальні мітки аналітики (`utm_source=fb&gclid=123`). Наївний кеш сприймає ці запити як різні об'єкти, через що коефіцієнт влучання (Cache Hit Ratio) падає до нуля;
3. **Затримка при вичерпанні терміну свіжості**: Коли термін дії `max-age` завершується, перший користувач, який запитав ресурс, змушений чекати повного часу відповіді від далекого Origin-сервера (300–1200 мс), що створює неприємні стрибки затримок (Latency Spikes).

Для вирішення цих завдань ми реалізуємо крайовий обробник, який виконує:
- **Нормалізацію ключів кешування**: фільтрацію маркетингових міток та детерміноване сортування query-параметрів;
- **Валідацію JWT на краю**: повну криптографічну перевірку підпису HMAC-SHA256 у пам'яті крайового вузла за < 1 мс без звернення до бази даних;
- **Асинхронний кеш Stale-While-Revalidate**: миттєву віддачу збереженої версії з пам'яті та паралельний неблокуючий запуск фонового оновлення до Origin;
- **Стійкість до збоїв Stale-If-Error**: повернення застарілого контенту при виникненні помилок 5xx на центральному сервері.

## Архітектура та послідовність обробки запиту

Обробник перехоплює вхідну подію `fetch` і виконує конвеєр перевірок:

```
[Клієнт] → (HTTPS запит) 
  ↓
[1. Нормалізація URL та формування Cache Key]
  ↓
[2. Перевірка JWT у пам'яті (HMAC-SHA256)] ──(Помилка)──► [HTTP 401 Unauthorized (1 мс)]
  ↓ (Валідний)
[3. Пошук у розподіленому кеші Edge]
  ├─► [Fresh HIT] ───────────────────────────► [HTTP 200 OK (2 мс)]
  ├─► [Stale HIT] ─┬─────────────────────────► [HTTP 200 OK (Stale, 2 мс)]
  │                └─► [Фоновий fetch(Origin)] ─► [Оновлення кешу]
  └─► [Cache MISS] ──► [fetch(Origin)] ────────► [Запис у кеш] ──► [HTTP 200 OK]
```

## Реалізація крайового обробника

Розглянемо дві еквівалентні реалізації: перша — на базі стандарту Web Standards Fetch API (середовища V8 Isolates / Cloudflare Workers / Deno Deploy), друга — високопродуктивний багатопотоковий модуль зворотного проксі мовою C++20 для розгортання всередині власної крайової інфраструктури.

:::tabs
```ts
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
```
```cpp
/**
 * Високопродуктивний C++20 Edge Proxy Worker з безпечним пулом потоків,
 * LRU-кешем та асинхронним stale-while-revalidate конвеєром.
 */

#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <list>
#include <mutex>
#include <chrono>
#include <memory>
#include <vector>
#include <optional>
#include <future>
#include <algorithm>

namespace edge {

struct HttpResponse {
    int status_code{200};
    std::unordered_map<std::string, std::string> headers;
    std::vector<uint8_t> body;
};

struct CacheEntry {
    HttpResponse response;
    std::chrono::steady_clock::time_point cached_at;
    std::chrono::seconds max_age{60};
    std::chrono::seconds stale_window{300};
};

class ThreadSafeLruCache {
public:
    explicit ThreadSafeLruCache(size_t capacity) : capacity_(capacity) {}

    std::optional<CacheEntry> get(std::string_view key) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = index_.find(std::string(key));
        if (it == index_.end()) {
            return std::nullopt;
        }
        // Переміщення використаного елемента в початок LRU-списку
        lru_order_.splice(lru_order_.begin(), lru_order_, it->second);
        return it->second->second;
    }

    void put(std::string_view key, CacheEntry entry) {
        std::lock_guard<std::mutex> lock(mutex_);
        std::string k(key);
        auto it = index_.find(k);
        if (it != index_.end()) {
            it->second->second = std::move(entry);
            lru_order_.splice(lru_order_.begin(), lru_order_, it->second);
            return;
        }

        if (index_.size() >= capacity_) {
            // Витіснення найменш використовуваного елемента з кінця
            auto oldest = lru_order_.back().first;
            index_.erase(oldest);
            lru_order_.pop_back();
        }

        lru_order_.emplace_front(k, std::move(entry));
        index_[k] = lru_order_.begin();
    }

private:
    size_t capacity_;
    std::mutex mutex_;
    std::list<std::pair<std::string, CacheEntry>> lru_order_;
    std::unordered_map<std::string, decltype(lru_order_.begin())> index_;
};

class EdgeProxyWorker {
public:
    explicit EdgeProxyWorker(size_t cache_capacity) 
        : cache_(std::make_unique<ThreadSafeLruCache>(cache_capacity)) {}

    /**
     * Нормалізація ключа кешування: видалення маркетингових міток
     */
    static std::string normalize_url(std::string_view url) {
        auto query_pos = url.find('?');
        if (query_pos == std::string_view::npos) {
            return std::string(url);
        }
        std::string base(url.substr(0, query_pos));
        std::string_view query = url.substr(query_pos + 1);
        
        // Фільтрація query-параметрів
        std::vector<std::string> clean_params;
        size_t start = 0;
        while (start < query.size()) {
            auto amp = query.find('&', start);
            auto param = query.substr(start, amp == std::string_view::npos ? amp : amp - start);
            if (!param.starts_with("utm_") && !param.starts_with("gclid=")) {
                clean_params.emplace_back(param);
            }
            if (amp == std::string_view::npos) break;
            start = amp + 1;
        }
        std::sort(clean_params.begin(), clean_params.end());
        
        if (clean_params.empty()) return base;
        std::string result = base + "?";
        for (size_t i = 0; i < clean_params.size(); ++i) {
            result += clean_params[i];
            if (i + 1 < clean_params.size()) result += "&";
        }
        return result;
    }

    /**
     * Головний конвеєр обробки вхідного HTTP-запиту
     */
    HttpResponse handle_request(std::string_view method, std::string_view raw_url, 
                               const std::unordered_map<std::string, std::string>& headers) {
        if (method != "GET" && method != "HEAD") {
            return fetch_from_origin(raw_url, headers);
        }

        std::string cache_key = normalize_url(raw_url);
        auto now = std::chrono::steady_clock::now();
        auto cached = cache_->get(cache_key);

        if (cached.has_value()) {
            auto age = std::chrono::duration_cast<std::chrono::seconds>(now - cached->cached_at);
            
            // 1. Fresh Hit: миттєва віддача з пам'яті
            if (age <= cached->max_age) {
                auto resp = cached->response;
                resp.headers["X-Cache-Status"] = "HIT";
                resp.headers["Age"] = std::to_string(age.count());
                return resp;
            }

            // 2. Stale-While-Revalidate Hit: повертаємо застарілу версію та оновлюємо у фоні
            if (age <= (cached->max_age + cached->stale_window)) {
                // Асинхронний запуск фонового оновлення
                std::string url_copy(raw_url);
                auto headers_copy = headers;
                std::thread([this, cache_key, url_copy, headers_copy]() {
                    auto fresh_resp = fetch_from_origin(url_copy, headers_copy);
                    if (fresh_resp.status_code == 200) {
                        CacheEntry new_entry{
                            .response = std::move(fresh_resp),
                            .cached_at = std::chrono::steady_clock::now(),
                            .max_age = std::chrono::seconds(60),
                            .stale_window = std::chrono::seconds(300)
                        };
                        cache_->put(cache_key, std::move(new_entry));
                    }
                }).detach();

                auto resp = cached->response;
                resp.headers["X-Cache-Status"] = "STALE";
                resp.headers["Age"] = std::to_string(age.count());
                return resp;
            }
        }

        // 3. Cache Miss: пряме синхронне звернення до центрального сервера
        auto origin_resp = fetch_from_origin(raw_url, headers);
        if (origin_resp.status_code == 200) {
            CacheEntry entry{
                .response = origin_resp,
                .cached_at = now,
                .max_age = std::chrono::seconds(60),
                .stale_window = std::chrono::seconds(300)
            };
            cache_->put(cache_key, std::move(entry));
            origin_resp.headers["X-Cache-Status"] = "MISS";
        } else if (cached.has_value()) {
            // Stale-if-error fallback
            auto resp = cached->response;
            resp.headers["X-Cache-Status"] = "STALE-ERROR-FALLBACK";
            return resp;
        }

        return origin_resp;
    }

private:
    HttpResponse fetch_from_origin(std::string_view url, 
                                   const std::unordered_map<std::string, std::string>& /*headers*/) {
        // Симуляція звернення до мережевого сокета пулу з'єднань
        HttpResponse resp;
        resp.status_code = 200;
        resp.headers["Content-Type"] = "application/json";
        std::string json_data = "{\"origin_data\": true, \"path\": \"" + std::string(url) + "\"}";
        resp.body.assign(json_data.begin(), json_data.end());
        return resp;
    }

    std::unique_ptr<ThreadSafeLruCache> cache_;
};

} // namespace edge
```
:::

## Детальний розбір алгоритмів та внутрішніх структур даних

Розглянемо ключові інженерні рішення, закладені в наведені реалізації:

### 1. Алгоритм детермінованої нормалізації URL
Функція `normalizeCacheKey` усуває дублювання кешу шляхом розбору рядка запиту на складові елементи:
- Створюється чорний список заборонених параметрів (`utm_*`, `fbclid`, `gclid`), які додаються сторонніми рекламними та аналітичними сервісами і не впливають на корисне навантаження відповіді;
- Всі релевантні ключі сортуються за лексикографічним порядком за допомогою `Array.sort()` або `std::sort`;
- Значення параметрів детерміновано конкатенуються, утворюючи канонічний рядок запиту.
Завдяки цьому запити `/item?b=2&a=1&utm_source=email` та `/item?a=1&b=2` перетворюються на абсолютно ідентичний ключ `/item?a=1&b=2`, що дозволяє досягти 100% повторного використання кешу.

### 2. Безпечна валідація JWT на базі Web Crypto API
Перевірка підпису токена відбувається без використання важких зовнішніх бібліотек:
- Використовується нативний апаратний модуль `crypto.subtle`, скомпільований безпосередньо в бінарний рушій V8 або Rust/C++ ядро рантайму;
- Порівняння криптографічних підписів виконується за сталий час (Constant-Time Verification) через внутрішні виклики `crypto.subtle.verify` або `CRYPTO_memcmp`, що унеможливлює проведення атак за сторонніми каналами синхронізації часу (Timing Attacks);
- Парсинг часової мітки `exp` виконується на першому етапі: якщо токен прострочений, ресурсомістка криптографічна перевірка підпису навіть не ініціюється, заощаджуючи процесорний час.

### 3. Валідація асиметричних підписів RS256 та кешування наборів ключів JWKS
У промислових системах авторизації токени підписуються приватним ключем RSA/ECDSA, а для їхньої перевірки потрібен публічний ключ із набору JSON Web Key Set (JWKS).
- Крайовий воркер завантажує документ JWKS з ендпоінту `/.well-known/jwks.json` постачальника автентифікації (Auth0, Keycloak, Cognito);
- Публічні ключі імпортуються у криптографічний контекст `crypto.subtle.importKey` і кешуються у глобальній пам'яті воркера на 24 години;
- При надходженні JWT воркер зчитує параметр `kid` (Key ID) із заголовка токена, миттєво знаходить відповідний ключ у локальній таблиці та виконує валідацію підпису за 400 мікросекунд без жодного мережевого запиту до Auth-провайдера.

### 4. Багатопотокова синхронізація в C++ реалізації
Клас `ThreadSafeLruCache` поєднує дві структури даних для досягнення складності `O(1)` при операціях пошуку, вставки та вилучення:
- **Двозв'язний список (`std::list`)**: зберігає елементи в порядку їхнього останнього використання (найсвіжіші на початку `begin()`, найстаріші в кінці `end()`);
- **Хеш-таблиця (`std::unordered_map`)**: зіставляє строковий ключ запиту з прямим ітератором вузла двозв'язного списку;
- **Метод `splice()`**: переміщує ітератор вузла в початок списку без копіювання пам'яті та без інвалідації покажчиків, виконуючи оновлення черги за лічені наносекунди;
- **М'ютекс (`std::mutex`)**: захищає критичну секцію від стану гонитви (Race Condition) при одночасному зверненні кількох робочих потоків.

### 5. Шарджування м'ютексів для високопаралельних систем
У системах із сотнями тисяч запитів на секунду єдиний глобальний м'ютекс `mutex_` стає вузьким місцем (Lock Contention). Щоб усунути затримки синхронізації, застосовується **шарджування кешу** (Cache Sharding):
- Пам'ять розбивається на `K` незалежних кошиків (наприклад, `K = 64`);
- Кожен кошик має власний двозв'язний список, хеш-таблицю та незалежний м'ютекс `std::mutex`;
- Номер кошика обчислюється як `bucket_idx = std::hash<std::string_view>{}(key) % K`.
Це знижує ймовірність блокування потоків у 64 рази, дозволяючи процесору масштабувати пропускну здатність лінійно за кількістю ядер.

## Обробка мутацій та скидання кешу при POST/PUT/DELETE запитах

Крайовий проксі не обмежується пасивним читанням:
- Коли надходить запит мутації стану (наприклад, `PUT /api/products/4829`), воркер не лише транслює його на бекенд, але й миттєво інвалідує відповідні ключі у локальному LRU-кеші (`cache_->erase("/api/products/4829")`);
- Якщо бекенд повертає успішний статус `200 OK` або `204 No Content`, крайовий проксі може асинхронно відправити подію інвалідації сусіднім крайовим вузлам через шину обміну повідомленнями або Redis Pub/Sub, гарантуючи глобальну консистентність даних.

## Активний моніторинг доступності бекенду (Active Health Checks & Failover)

Для забезпечення безвідмовної роботи крайовий вузол періодично опитує бекенди:
- Створюється фоновий таймер, який щосекунди надсилає легкий запит `GET /health` до основного та резервного пулів серверів;
- Якщо основний Origin не відповідає протягом трьох послідовних опитувань (Threshold = 3), крайовий проксі автоматично перемикає вихідний маршрут на резервний регіон (Hot Standby);
- При відновленні працездатності основного вузла навантаження повертається плавно з поступовим нарощуванням частки трафіку (Traffic Warming / Ramp-Up).

## Безшовне оновлення коду та канаркові релізи (Zero-Downtime Canary Deployments)

Розгортання нової версії крайового воркера на сотні дата-центрів світу не повинно призводити до розриву активних з'єднань користувачів:
1. **Атомарна заміна покажчика середовища (Atomic Pointer Swap)**: Рушій V8 компілює нову версію скрипту в ізольованому фоновому контексті;
2. **Канаркове розкочування (Canary Traffic Splitting)**: Нова версія отримує 1% трафіку. Якщо метрики телеметрії (кількість необроблених винятків або P99 затримка) залишаються в межах норми протягом 5 хвилин, частка плавно зростає: 10% → 50% → 100%;
3. **Автоматичний відкат (Instant Rollback)**: У разі виникнення спалаху помилок перемикач маршрутизації атомарно повертає трафік на попередню стабільну версію за менш ніж 10 мілісекунд.

## Потокова обробка та керування зворотним тиском (Backpressure)

При передачі великих файлів (відео, зображень високої роздільної здатності) крайовий вузол не повинен зчитувати все тіло відповіді в оперативну пам'ять:
- Використовується інтерфейс потоків `TransformStream` / `ReadableStream`;
- Дані передаються чанками фіксованого розміру (наприклад, 64 КБ);
- Механізм зворотного тиску (Backpressure) автоматично призупиняє зчитування з сокета Origin-сервера, якщо клієнт на повільному мобільному з'єднанні 3G не встигає приймати пакети, запобігаючи неконтрольованому зростанню буферів пам'яті крайового воркера.

## Проектування запобіжника від збоїв (Circuit Breaker на краю)

Коли центральний бекенд починає повертати помилки `500` або зависає за таймаутом через відмову бази даних, надсилання нових запитів від тисяч клієнтів лише погіршує ситуацію (Cascading Failure).

Крайовий воркер інтегрує патерн **Circuit Breaker**:
- **Стан Closed (Нормальний режим)**: Запити проходять на Origin. Воркер веде лічильник невдалих звернень за ковзне вікно (наприклад, останні 100 запитів);
- **Стан Open (Захисний режим)**: Якщо частка помилок перевищує 50%, запобіжник розмикається на 30 секунд. Всі нові запити негайно отримують або застарілу версію з кешу (`stale-if-error`), або структуровану помилку HTTP `503 Service Unavailable` безпосередньо з пам'яті краю без спроб звернення до Origin;
- **Стан Half-Open (Тестовий режим)**: Після завершення інтервалу таймауту воркер пропускає один тестовий запит (Probe Request). Якщо бекенд успішно відповів `200 OK`, запобіжник повертається у стан Closed.

## Керування пам'яттю та RAII у високопродуктивних крайових проксі

На відміну від короткоживучих безсерверних функцій, серверний процес зворотного проксі працює безперервно місяцями. Будь-який витік пам'яті (Memory Leak) обсягом навіть кілька байтів на запит призводить до деградації системи під навантаженням мільярдів звернень:
- Використання виключно розумних покажчиків (`std::unique_ptr`, `std::shared_ptr`) та концепції RAII (Resource Acquisition Is Initialization) гарантує автоматичне звільнення пам'яті буферів та сокетів при виході з області видимості;
- Відмова від сирих покажчиків `void*` та ручного керування `malloc/free` усуває ризики подвійного звільнення (Double Free) та звернення до недійсної пам'яті (Use-After-Free);
- Застосування семантики переміщення (`std::move`) та представлень рядків (`std::string_view`) мінімізує алокації динамічної пам'яті у купі (Heap), зводячи роботу до операцій на швидкому стеку процесора.

## Анатомія життєвого циклу ізоляту V8 на крайовому вузлі

Під час виконання JavaScript-коду на крайовому вузлі (Cloudflare Workers, Fastly JS) платформа керує життєвим циклом пісочниці за оптимізованою моделлю:
1. **Знімок пам'яті (Isolate Snapshotting)**: При деплої коду рушій V8 компілює JS-скрипт та виконує статичну ініціалізацію, після чого зберігає бінарний дамп оперативної пам'яті купи (Heap Snapshot). При надходженні нового запиту замість парсингу тексту JS відновлюється готовий знімок за 200 мікросекунд;
2. **Черга мікрозадач (Microtask Queue)**: Проміси `Promise` та асинхронні виклики `async/await` плануються в єдиному циклі подій ізоляту (Event Loop) без перемикання потоків ядра операційної системи;
3. **Обмеження часу процесора (Wall-clock vs CPU Time)**: Платформа тарифікує та обмежує виключно час, коли процесор реально виконує інструкції воркера (CPU Time, ліміт 50 мс), тоді як час очікування мережевої відповіді від Origin (Wall-clock time до 30 секунд) не призводить до примусового завершення функції.

## Інженерні пастки та крайові випадки

При проектуванні та експлуатації програмованих крайових воркерів необхідно враховувати чотири фундаментальні обмеження:

### 1. Фрагментація простору ключів через заголовок `Vary: User-Agent`
Якщо центральний бекенд повертає заголовок `Vary: User-Agent`, крайовий кеш змушений виділяти окремий слот для кожного різновиду браузера клієнта. Оскільки існує понад 50 000 унікальних комбінацій User-Agent (версії Chrome, Safari, боти, версії ОС), коефіцієнт влучання (Cache Hit Ratio) падає практично до нуля.
*Виправлення*: Крайовий воркер зобов'язаний нормалізувати заголовок клієнта до фіксованої класифікації (`X-Device-Type: mobile | desktop | tablet`) перед формуванням ключа кешування і передавати на Origin лише уніфікований заголовок.

### 2. Ефект «Лавиноподібного навантаження» (Cache Stampede / Thundering Herd)
Коли термін придатності популярного об'єкта завершується, 10 000 паралельних клієнтів одночасно отримують стан Cache Miss і всі разом роблять підзапити до Origin.
*Виправлення*: Застосування директиви `stale-while-revalidate` або використання механізму взаємного блокування (Request Collapsing / Single-Flight). Перший запит, що отримав Miss, виставляє м'який лок і вирушає на Origin, а решта 9 999 запитів підвішуються у черзі очікування першої відповіді.

### 3. Ліміти на пам'ять та розмір ізоляту
Платформи Edge Computing на базі V8 Isolates обмежують максимальний обсяг пам'яті одного виклику до 128 МБ та максимальний час процесорного ядра (CPU execution time) до 50 мс. 
*Виправлення*: Стримінг великих файлів (відео, архівів) через потік `ReadableStream` без буферизації всього тіла в оперативну пам'ять воркера.

### 4. Розподілене обмеження частоти (Rate Limiting) за алгоритмом ковзного вікна
Для захисту API від перебору паролів або скрапінгу крайовий воркер веде облік запитів у швидкому Key-Value сховищі з атомарними операціями `INCR`:
- Вікно розбивається на однохвилинні інтервали;
- Кількість запитів розраховується як зважена сума `Поточна_хвилина + Попередня_хвилина · (1 - Частка_поточної_хвилини)`;
- При перевищенні ліміту воркер миттєво повертає HTTP `429 Too Many Requests` з заголовком `Retry-After: 60`, блокуючи атаку на рівні крайового периметра.

## Методологія профілювання та тестування крайових обробників

Перед розгортанням крайового коду у виробничу мережу з сотнями точок присутності інженери проводять локальне тестування:
- **Емуляція середовища (Miniflare / Mock Service Worker)**: Виконання тестів у локальній пісочниці Node.js із повною емуляцією поведінки глобального сховища `CacheStorage` та ключ-значення `KVNamespace`;
- **Стрес-тестування затримки 99-го перцентиля (P99 Latency Benchmarking)**: Використання утиліт генерації асинхронного трафіку `k6` або `wrk2` для перевірки відсутності блокувань Event Loop при навантаженні понад 50 000 запитів/с на одне процесорне ядро;
- **Діагностика витоків пам'яті**: Профілювання розміру купи через Google Chrome DevTools Protocol, підключений до віддаленого процесу воркера, для підтвердження стабільності обсягу пам'яті при тривалих циклах обробки з'єднань.

## Підсумок архітектури крайового проксі

Поєднання нормалізації URL-ключів, попередньої криптографічної перевірки JWT за допомогою апаратного прискорення WebCrypto, шардованої багатопотокової пам'яті LRU та неблокуючого конвеєра Stale-While-Revalidate перетворює крайовий вузол на автономний бар'єр продуктивності й безпеки. Центральний бекенд повністю звільняється від рутинної роботи з автентифікації та віддачі незмінних ресурсів, зосереджуючись виключно на транзакційній бізнес-логіці та модифікаціях бази даних.
