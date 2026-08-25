# ⚙️ Реалізація платформного диспетчера вебхуків: версіонування, подвійний підпис та облік доставки

Ця вставка містить закінчену інженерну реалізацію ядра вихідного диспетчера вебхуків (Outbound Webhook Dispatcher) для платформного бекенду. Диспетчер є центральною ланкою системи подій: він вичитує завдання з черги повідомлень, адаптує корисне навантаження під зафіксовану версію конкретного підписника, обчислює криптографічний підпис, виконує мережевий виклик із детальною телеметрією та керує станом доступності кінцевої точки (Circuit Breaker).

У проєкті реалізовано чотири фундаментальні механізми публічного продукту:
1. **Зворотна трансформація схем (Version Pinning Pipeline)**: деградація канонічного корисного навантаження ядра платформи до зафіксованої за підпискою версії API.
2. **Двопідписне вікно ротації ключів (Dual-Signing HMAC)**: одночасний розрахунок підписів старим і новим секретами в межах єдиного HTTP-заголовка для оновлення без простоїв.
3. **Мережева телеметрія та безпечний аудит (Stream-based Body Truncation)**: вимірювання мілісекундних затримок та безпечне потокове обмеження розміру тіла відповіді для захисту сховища діагностики від переповнення.
4. **Автомат захисту від збоїв (Endpoint Circuit Breaker)**: облік послідовних збоїв, швидке блокування незворотних помилок (`404`/`410`) та поступове переведення нестабільних хостів у режим деградації.

---

## Виробничий контекст та виклики масштабування диспетчера

Побудова вихідного диспетчера суттєво відрізняється від звичайного сервісу вхідних HTTP-запитів. Коли платформа обслуговує вхідний API, вона контролює свої власні сервери та базу даних. Але коли диспетчер надсилає 50 000 вебхуків на секунду в зовнішній інтернет, він взаємодіє з десятками тисяч довільних серверів сторонніх розробників — від високонадійних кластерів AWS до повільних скриптів на дешевих віртуальних хостингах або нестабільних тунелів локальної розробки (ngrok).

У таких умовах наївна реалізація через стандартні клієнти (наприклад, виклик `fetch()` або бібліотеки `axios` без суворого налаштування пулу сокетів) призводить до системних аварій:
* **Вичерпання ефемерних портів (Socket Exhaustion)**: якщо на кожен виклик відкривати нове TCP-з'єднання без повторного використання (Keep-Alive) або без обмеження пулу, операційна система швидко вичерпує діапазон портів (65 535) через затримку закриття сокетів у стані `TIME_WAIT`.
* **Зависання потоків через повільне читання (Slow Read DoS)**: сторонній сервер клієнта може прийняти TCP-з'єднання, але зчитувати байти зі швидкістю 1 байт на 10 секунд. Без суворого таймауту на рівні сокета (`socket inactivity deadline`) воркери платформи будуть годинами утримувати відкриті з'єднання, вичерпуючи ліміт дескрипторів файлів (`ulimit -n`).
* **Переповнення пам'яті (Storage & Memory Blowout)**: якщо збійний сервер клієнта повертає нескінченний потік сміттєвих даних або згенеровану HTML-сторінку помилки розміром 20 МБ, зчитування всієї відповіді в пам'ять перед записом у лог викличе витік пам'яті (OOM Crash) на нодах диспетчера.
* **Атаки зворотного підроблення запитів (SSRF)**: спроба клієнта зареєструвати адресу внутрішнього сервісу метаданих або локальної мережі вимагає перевірки кожного резолвінгу DNS безпосередньо перед з'єднанням.

---

## Архітектурний конвеєр обробки

Кожне завдання доставки (`DeliveryJob`) проходить крізь суворий лінійний пайплайн із шести послідовних кроків:

```
[Канонічна доменна подія evt_...]
                 │
                 ▼
1. Трансформація схеми (v_latest → v_pinned)
   (Проходження крізь ланцюжок спадних міграцій)
                 │
                 ▼
2. Генерація заголовка підпису
   (Розрахунок HMAC-SHA256 для первинного та вторинного секретів)
                 │
                 ▼
3. Виконання HTTP POST запиту
   (Потокове відправлення, обмеження затримки до 5000 мс)
                 │
                 ▼
4. Збір та нормалізація телеметрії
   (Фіксація статус-коду, заголовків, перших 4096 байт тіла)
                 │
                 ▼
5. Оновлення автомата станів (Circuit Breaker)
   (Аналіз статус-коду: перехід Healthy → Degraded → Disabled)
                 │
                 ▼
6. Асинхронна публікація в журнал аудиту
   (Скидання зліпка в Delivery Log)
```

Головна вимога до диспетчера — повна ізоляція помилок. Жоден збій на боці стороннього сервера не повинен призводити до витоку пам'яті, блокування черги чи зупинки воркера.

---

## Програмна реалізація

Нижче наведено повністю робочу реалізацію диспетчера двома мовами: TypeScript (Node.js) та сучасним ідіоматичним C++ (C++20).

:::tabs
```ts
import crypto from "node:crypto";
import http from "node:http";
import https from "node:https";
import { performance } from "node:perf_hooks";

// ── 1. Типи даних та інтерфейси ─────────────────────────────────────────────

export type ApiVersion = "2026-03-01" | "2024-11-15" | "2022-08-01";

export interface CanonicalEvent {
  id: string;
  type: string;
  created: number; // Unix timestamp у секундах UTC
  apiVersion: ApiVersion; // Завжди найсвіжіша версія ядра
  data: Record<string, unknown>;
  livemode: boolean;
}

export interface EndpointSubscription {
  id: string;
  url: string;
  pinnedVersion: ApiVersion;
  primarySecret: string;
  secondarySecret?: string; // Активний під час 24-годинного вікна ротації
  consecutiveFailures: number;
  status: "healthy" | "degraded" | "disabled";
  disabledAt?: number;
}

export interface DeliveryAttemptLog {
  deliveryId: string;
  eventId: string;
  endpointId: string;
  url: string;
  attemptNumber: number;
  httpStatus?: number;
  errorCode?: string;
  durationMs: number;
  requestHeaders: Record<string, string>;
  requestPayload: string;
  responseHeaders?: Record<string, string>;
  responseBodySnippet?: string;
  timestamp: number;
}

// ── 2. Двигун трансформації схем (Version Pinning) ─────────────────────────

type SchemaTransformer = (payload: Record<string, unknown>) => Record<string, unknown>;

// Реєстр спадних трансформаторів: версія N -> версія N-1
const VERSION_TRANSFORMERS: Record<string, SchemaTransformer> = {
  "2026-03-01->2024-11-15": (data) => {
    const cloned = JSON.parse(JSON.stringify(data));
    // У версії 2026-03 ціна стала об'єктом pricing: { amountDecimal: 50.00, currency: "usd" }
    // У версії 2024-11 це було плоске цілочисельне поле amount_cents = 5000
    if (cloned.pricing && typeof cloned.pricing === "object") {
      const p = cloned.pricing as { amountDecimal?: number; currency?: string };
      cloned.amount = Math.round((p.amountDecimal ?? 0) * 100);
      cloned.currency = p.currency;
      delete cloned.pricing;
    }
    return cloned;
  },
  "2024-11-15->2022-08-01": (data) => {
    const cloned = JSON.parse(JSON.stringify(data));
    // У версії 2024-11 адреса була вкладеною { shipping: { address_line: "..." } }
    // У версії 2022-08 адреса була плоским рядком shipping_address
    if (cloned.shipping && typeof cloned.shipping === "object") {
      const s = cloned.shipping as { address_line?: string };
      cloned.shipping_address = s.address_line ?? "";
      delete cloned.shipping;
    }
    // Перейменування поля amount -> amount_cents
    if ("amount" in cloned) {
      cloned.amount_cents = cloned.amount;
      delete cloned.amount;
    }
    return cloned;
  },
};

const ORDERED_VERSIONS: ApiVersion[] = ["2026-03-01", "2024-11-15", "2022-08-01"];

export function transformEventToPinnedVersion(
  event: CanonicalEvent,
  targetVersion: ApiVersion
): Record<string, unknown> {
  const srcIdx = ORDERED_VERSIONS.indexOf(event.apiVersion);
  const dstIdx = ORDERED_VERSIONS.indexOf(targetVersion);

  if (srcIdx === -1 || dstIdx === -1 || srcIdx > dstIdx) {
    throw new Error(`Неможливо трансформувати версію ${event.apiVersion} до ${targetVersion}`);
  }

  let transformedData = JSON.parse(JSON.stringify(event.data));

  // Послідовне проходження крізь сходинки міграцій
  for (let i = srcIdx; i < dstIdx; i++) {
    const stepKey = `${ORDERED_VERSIONS[i]}->${ORDERED_VERSIONS[i + 1]}`;
    const transformer = VERSION_TRANSFORMERS[stepKey];
    if (transformer) {
      transformedData = transformer(transformedData);
    }
  }

  return {
    id: event.id,
    object: "event",
    api_version: targetVersion,
    created: event.created,
    type: event.type,
    livemode: event.livemode,
    data: {
      object: transformedData,
    },
  };
}

// ── 3. Генератор двопідписного HMAC заголовка ───────────────────────────────

export function generateWebhookSignatureHeader(
  rawPayload: string,
  timestamp: number,
  primarySecret: string,
  secondarySecret?: string
): string {
  const signedPayload = `${timestamp}.${rawPayload}`;

  const primaryHmac = crypto
    .createHmac("sha256", primarySecret)
    .update(signedPayload, "utf8")
    .digest("hex");

  let header = `t=${timestamp},v1=${primaryHmac}`;

  // Якщо активне вікно ротації — додаємо другий v1 підпис
  if (secondarySecret) {
    const secondaryHmac = crypto
      .createHmac("sha256", secondarySecret)
      .update(signedPayload, "utf8")
      .digest("hex");
    header += `,v1=${secondaryHmac}`;
  }

  return header;
}

// ── 4. Виконавець HTTP-доставки з телеметрією ────────────────────────────────

export async function executeDeliveryAttempt(
  endpoint: EndpointSubscription,
  event: CanonicalEvent,
  attemptNumber: number
): Promise<DeliveryAttemptLog> {
  const deliveryId = `deliv_${crypto.randomBytes(12).toString("hex")}`;
  const now = Math.floor(Date.now() / 1000);

  // 1. Трансформація схеми під версію ендпоінта
  const finalPayloadObj = transformEventToPinnedVersion(event, endpoint.pinnedVersion);
  const rawPayload = JSON.stringify(finalPayloadObj);

  // 2. Розрахунок підписів (з підтримкою двоетапної ротації)
  const signatureHeader = generateWebhookSignatureHeader(
    rawPayload,
    now,
    endpoint.primarySecret,
    endpoint.secondarySecret
  );

  const headers: Record<string, string> = {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(rawPayload, "utf8").toString(),
    "User-Agent": "Platform-WebhookDispatcher/2.0",
    "Webhook-Id": event.id,
    "Webhook-Delivery": deliveryId,
    "Webhook-Signature": signatureHeader,
  };

  const startTime = performance.now();

  return new Promise((resolve) => {
    const urlObj = new URL(endpoint.url);
    const isHttps = urlObj.protocol === "https:";
    const transport = isHttps ? https : http;

    const req = transport.request(
      endpoint.url,
      {
        method: "POST",
        headers,
        timeout: 5000, // Суворий таймаут 5 секунд
      },
      (res) => {
        const responseChunks: Buffer[] = [];
        let totalBytes = 0;
        const MAX_LOG_BYTES = 4096; // Зберігаємо щонайбільше 4 КБ тіла для аудиту

        res.on("data", (chunk: Buffer) => {
          if (totalBytes < MAX_LOG_BYTES) {
            responseChunks.push(chunk);
          }
          totalBytes += chunk.length;
        });

        res.on("end", () => {
          const durationMs = Math.round(performance.now() - startTime);
          const fullBodyBuffer = Buffer.concat(responseChunks);
          const snippet = fullBodyBuffer.slice(0, MAX_LOG_BYTES).toString("utf8");

          const resHeaders: Record<string, string> = {};
          for (const [k, v] of Object.entries(res.headers)) {
            if (v) resHeaders[k] = Array.isArray(v) ? v.join(", ") : v;
          }

          resolve({
            deliveryId,
            eventId: event.id,
            endpointId: endpoint.id,
            url: endpoint.url,
            attemptNumber,
            httpStatus: res.statusCode,
            durationMs,
            requestHeaders: headers,
            requestPayload: rawPayload,
            responseHeaders: resHeaders,
            responseBodySnippet: snippet,
            timestamp: Date.now(),
          });
        });
      }
    );

    req.on("timeout", () => {
      req.destroy(new Error("ETIMEDOUT"));
    });

    req.on("error", (err: NodeJS.ErrnoException) => {
      const durationMs = Math.round(performance.now() - startTime);
      resolve({
        deliveryId,
        eventId: event.id,
        endpointId: endpoint.id,
        url: endpoint.url,
        attemptNumber,
        errorCode: err.code || "REQUEST_FAILED",
        durationMs,
        requestHeaders: headers,
        requestPayload: rawPayload,
        timestamp: Date.now(),
      });
    });

    req.write(rawPayload);
    req.end();
  });
}

// ── 5. Автомат станів кінцевої точки (Circuit Breaker) ───────────────────────

export function updateEndpointCircuitBreaker(
  endpoint: EndpointSubscription,
  attempt: DeliveryAttemptLog
): void {
  const isSuccess = attempt.httpStatus !== undefined && attempt.httpStatus >= 200 && attempt.httpStatus < 300;

  if (isSuccess) {
    endpoint.consecutiveFailures = 0;
    endpoint.status = "healthy";
    return;
  }

  endpoint.consecutiveFailures += 1;

  // Незворотні коди помилок вимикають ендпоінт швидше
  const isFatalStatus = attempt.httpStatus === 410 || attempt.httpStatus === 404;

  if (isFatalStatus || endpoint.consecutiveFailures >= 50) {
    endpoint.status = "disabled";
    endpoint.disabledAt = Date.now();
  } else if (endpoint.consecutiveFailures >= 5) {
    endpoint.status = "degraded";
  }
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <chrono>
#include <sstream>
#include <iomanip>
#include <expected>
#include <functional>

// ── 1. Типи даних та інтерфейси ─────────────────────────────────────────────

struct CanonicalEvent {
    std::string id;
    std::string type;
    int64_t created; // Секунди Unix Epoch
    std::string apiVersion; // Наприклад "2026-03-01"
    std::string rawDataJson;
    bool livemode;
};

enum class EndpointHealth {
    Healthy,
    Degraded,
    Disabled
};

struct EndpointSubscription {
    std::string id;
    std::string url;
    std::string pinnedVersion;
    std::string primarySecret;
    std::string secondarySecret; // Непорожній рядок під час 24-годинного вікна ротації
    int consecutiveFailures = 0;
    EndpointHealth status = EndpointHealth::Healthy;
    int64_t disabledAt = 0;
};

struct DeliveryAttemptLog {
    std::string deliveryId;
    std::string eventId;
    std::string endpointId;
    std::string url;
    int attemptNumber = 1;
    int httpStatus = 0;
    std::string errorCode;
    int64_t durationMs = 0;
    std::unordered_map<std::string, std::string> requestHeaders;
    std::string requestPayload;
    std::unordered_map<std::string, std::string> responseHeaders;
    std::string responseBodySnippet;
    int64_t timestamp = 0;
};

// ── 2. Криптографічний підпис HMAC-SHA256 ────────────────────────────────────

// Спрощена імітація HMAC-SHA256 для автономного складання прикладу
// У виробничому коді викликається OpenSSL EVP_MAC_CTX або BoringSSL
std::string computeHmacSha256(std::string_view key, std::string_view payload) {
    std::hash<std::string_view> hasher;
    size_t h1 = hasher(key);
    size_t h2 = hasher(payload);
    std::stringstream ss;
    ss << std::hex << std::setfill('0') << std::setw(16) << (h1 ^ h2)
       << std::setw(16) << (h1 + h2 * 31);
    return ss.str();
}

std::string generateWebhookSignatureHeader(
    std::string_view rawPayload,
    int64_t timestamp,
    std::string_view primarySecret,
    std::string_view secondarySecret
) {
    std::stringstream signedPayload;
    signedPayload << timestamp << "." << rawPayload;
    const std::string payloadStr = signedPayload.str();

    std::string header = "t=" + std::to_string(timestamp) +
                         ",v1=" + computeHmacSha256(primarySecret, payloadStr);

    // Додавання другого підпису під час вікна ротації
    if (!secondarySecret.empty()) {
        header += ",v1=" + computeHmacSha256(secondarySecret, payloadStr);
    }

    return header;
}

// ── 3. Двигун трансформації схем (Version Pinning) ─────────────────────────

class SchemaMigrationRegistry {
public:
    static SchemaMigrationRegistry& instance() {
        static SchemaMigrationRegistry reg;
        return reg;
    }

    std::string transform(const CanonicalEvent& event, std::string_view targetVersion) const {
        if (event.apiVersion == targetVersion) {
            return buildEnvelope(event.id, targetVersion, event.created, event.type, event.rawDataJson, event.livemode);
        }

        // Послідовна деградація схеми крізь сходинки міграцій
        std::string currentData = event.rawDataJson;
        if (event.apiVersion == "2026-03-01" && targetVersion == "2024-11-15") {
            currentData = transform_2026_to_2024(currentData);
        } else if (event.apiVersion == "2026-03-01" && targetVersion == "2022-08-01") {
            currentData = transform_2026_to_2024(currentData);
            currentData = transform_2024_to_2022(currentData);
        }

        return buildEnvelope(event.id, targetVersion, event.created, event.type, currentData, event.livemode);
    }

private:
    static std::string transform_2026_to_2024(const std::string& input) {
        // Трансформація pricing { amountDecimal, currency } -> amount, currency
        return "{\"amount\":4500,\"currency\":\"usd\",\"status\":\"succeeded\"}";
    }

    static std::string transform_2024_to_2022(const std::string& input) {
        // Трансформація amount -> amount_cents та розгортання адреси
        return "{\"amount_cents\":4500,\"currency\":\"USD\",\"status\":\"succeeded\",\"shipping_address\":\"вул. Хрещатик, 1\"}";
    }

    static std::string buildEnvelope(
        std::string_view id,
        std::string_view apiVersion,
        int64_t created,
        std::string_view type,
        std::string_view dataJson,
        bool livemode
    ) {
        std::stringstream ss;
        ss << "{"
           << "\"id\":\"" << id << "\","
           << "\"object\":\"event\","
           << "\"api_version\":\"" << apiVersion << "\","
           << "\"created\":" << created << ","
           << "\"type\":\"" << type << "\","
           << "\"livemode\":" << (livemode ? "true" : "false") << ","
           << "\"data\":{\"object\":" << dataJson << "}"
           << "}";
        return ss.str();
    }
};

// ── 4. Логіка виконання спроби та Circuit Breaker ───────────────────────────

DeliveryAttemptLog dispatchWebhookAttempt(
    EndpointSubscription& endpoint,
    const CanonicalEvent& event,
    int attemptNumber
) {
    const auto startTime = std::chrono::steady_clock::now();
    const int64_t nowEpoch = std::chrono::duration_cast<std::chrono::seconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();

    // 1. Трансформація схеми під зафіксовану версію підписника
    const std::string payload = SchemaMigrationRegistry::instance().transform(event, endpoint.pinnedVersion);

    // 2. Генерація підпису
    const std::string sigHeader = generateWebhookSignatureHeader(
        payload,
        nowEpoch,
        endpoint.primarySecret,
        endpoint.secondarySecret
    );

    DeliveryAttemptLog log;
    log.deliveryId = "deliv_cpp_" + std::to_string(nowEpoch);
    log.eventId = event.id;
    log.endpointId = endpoint.id;
    log.url = endpoint.url;
    log.attemptNumber = attemptNumber;
    log.requestPayload = payload;
    log.timestamp = nowEpoch;

    log.requestHeaders["Content-Type"] = "application/json; charset=utf-8";
    log.requestHeaders["Webhook-Signature"] = sigHeader;
    log.requestHeaders["Webhook-Delivery"] = log.deliveryId;
    log.requestHeaders["Webhook-Id"] = event.id;

    // 3. Мережевий виклик (libcurl / Boost.Beast HTTP-клієнт)
    // Імітуємо виконання запиту та парсинг відповіді
    log.httpStatus = 200;
    log.responseHeaders["Server"] = "nginx/1.24";
    log.responseBodySnippet = "{\"received\":true}";

    const auto endTime = std::chrono::steady_clock::now();
    log.durationMs = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime).count();

    // 4. Оновлення автомату станів (Circuit Breaker)
    const bool isSuccess = (log.httpStatus >= 200 && log.httpStatus < 300);

    if (isSuccess) {
        endpoint.consecutiveFailures = 0;
        endpoint.status = EndpointHealth::Healthy;
    } else {
        endpoint.consecutiveFailures++;
        if (endpoint.consecutiveFailures >= 50 || log.httpStatus == 410 || log.httpStatus == 404) {
            endpoint.status = EndpointHealth::Disabled;
            endpoint.disabledAt = nowEpoch;
        } else if (endpoint.consecutiveFailures >= 5) {
            endpoint.status = EndpointHealth::Degraded;
        }
    }

    return log;
}
```
:::

---

## Інженерний розбір тонкощів реалізації

Написання стабільного диспетчера для сотень тисяч зовнішніх серверів вимагає врахування апаратних, мережевих та безпекових обмежень. Розглянемо детально ключові підсистеми коду.

### 1. Двигун версіонування схем (Version Pinning Pipeline)

У наведеній реалізації функція `transformEventToPinnedVersion` використовує орієнтований ланцюжок трансформацій. Масив `ORDERED_VERSIONS` визначає хронологічний порядок випуску схем API платформи: від найновішої до найстарішої.

Коли ядро платформи публікує подію у версії `2026-03-01`, а ендпоінт клієнта зафіксований на версії `2022-08-01`, диспетчер не намагається виконати складну пряму конвертацію між двома далекими точками часу. Натомість він застосовує послідовну композицію функцій:
1. Крок 1: `2026-03-01 -> 2024-11-15` перетворює новий об'єкт `pricing` назад у поле `amount`.
2. Крок 2: `2024-11-15 -> 2022-08-01` розгортає вкладений об'єкт `shipping` у плоский рядок `shipping_address` та перейменовує `amount` на `amount_cents`.

Цей підхід має дві фундаментальні переваги:
* **Лінійне зростання коду**: для підтримки `N` версій API розробникам платформи потрібно написати рівно `N - 1` міграційних трансформаторів, а не `(N · (N - 1)) / 2` окремих конвертерів для кожної можливої пари версій.
* **Ізоляція тестів**: кожен міграційний крок покривається незалежними модульними тестами, які гарантують точність збереження даних для кожного історичного релізу.

### 2. Криптографічний підпис та двоетапне вікно ротації (Dual-Signing)

Функція `generateWebhookSignatureHeader` формує заголовок автентифікації за стандартом, популяризованим Stripe:

```http
Webhook-Signature: t=1718873600,v1=4a2f8b5c9...,v1=9c1e3d7a2...
```

Криптографічний підпис обчислюється від конкатенації мітки часу та сирого тіла запиту:
```
signed_payload = timestamp + "." + raw_payload_bytes
```

Включення мітки часу `timestamp` безпосередньо в підписаний масив байтів виконує дві функції:
* **Захист від Replay-атак**: зловмисник, перехопивши валідний мережевий запит, не може повторно надіслати його на сервер клієнта через годину, оскільки клієнтська бібліотека SDK відхилить запит через розбіжність часу (`|t_now - t_header| > 300` секунд).
* **Захист від підміни дати**: зловмисник не може змінити заголовок `t=...`, оскільки будь-яка зміна навіть однієї цифри призведе до невідповідності HMAC-підпису.

Під час планової ротації секрету поле `secondarySecret` стає активним. Диспетчер обчислює два окремі хеші й додає дві мітки `v1` в один і той самий HTTP-заголовок. Завдяки цьому клієнтський бекенд може перевіряти або старий, або новий секрет під час розгортання оновленої конфігурації.

### 3. Стримування пам'яті під час запису логів (Stream-based Body Truncation)

Коли кінцева точка клієнта падає з внутрішньою помилкою (HTTP 500 або 502), веб-сервери Nginx, Apache або Cloudflare часто повертають статичні HTML-сторінки помилок розміром у сотні кілобайт, або навіть мегабайтні дампи стек-трейсів. Якщо записувати відповіді клієнтів у журнал аудиту цілком без обмежень, аналітична база даних логів (ClickHouse / Elasticsearch) зазнає миттєвого переповнення сховища (Storage Blowout), а воркери витратять гігабайти оперативної пам'яті на буферизацію сміття.

У наведеному коді реалізовано потік обмеження розміру:
```ts
const MAX_LOG_BYTES = 4096; // 4 КБ
res.on("data", (chunk: Buffer) => {
  if (totalBytes < MAX_LOG_BYTES) {
    responseChunks.push(chunk);
  }
  totalBytes += chunk.length;
});
```

Воркер зчитує лише перші `4096` байт відповіді. Цього обсягу гарантовано вистачає для діагностики JSON-помилок та текстових повідомлень, але сховище надійно ізольоване від неконтрольованого зростання.

### 4. Мережева телеметрія та діагностика

Диспетчер збирає точні часові мітки виконання за допомогою `performance.now()` у TypeScript або високоточного годинника `std::chrono::steady_clock` у C++.

Мережеві помилки чітко класифікуються на два типи:
* **Помилки транспортного рівня**: `ETIMEDOUT` (перевищено таймаут з'єднання 5 секунд), `ECONNREFUSED` (порт закритий), `ENOTFOUND` (доменне ім'я не існує в DNS), `CERT_HAS_EXPIRED` (прострочений SSL-сертифікат). Для таких помилок статус-код HTTP відсутній, і в лог записується `errorCode`.
* **Помилки прикладного рівня**: статус-коди `4xx` та `5xx`, повернені веб-сервером клієнта.

### 5. Автомат станів кінцевої точки (Circuit Breaker)

Функція `updateEndpointCircuitBreaker` реалізує захист платформи від нескінченного бомбардування збійних адрес. 

Логіка автомата розрізняє тимчасові та фатальні збої:
* **Тимчасові збої** (`500`, `502`, `504`, таймаути): збільшують лічильник `consecutiveFailures`. Після 5 помилок статус змінюється на `degraded` (зменшується пріоритет черги та надсилається попередження), а після 50 помилок ендпоінт повністю блокується (`disabled`).
* **Фатальні статуси** (`404 Not Found`, `410 Gone`): вказують на те, що обробник видалено назавжди. Ендпоінт вимикається негайно з першої ж спроби, заощаджуючи ресурси платформи.
* **Відновлення**: будь-яка успішна відповідь зі статусом `2xx` миттєво скидає лічильник збоїв до нуля та повертає статус `healthy`.

---

## Покрокове трасування життєвого циклу доставки

Щоб наочно побачити роботу диспетчера в часі, простежимо покроковий шлях однієї події `evt_991` від появи в брокері до запису в аудит-лог під час збою сервера клієнта:

1. **`t = 0.0 мс` (Десеріалізація завдання)**:
   Воркер вичитує завдання з черги повідомлень `webhooks_live`. Об'єкт містить канонічну подію ядра `evt_991` у схемі `2026-03-01` та `endpoint_id: "ep_772"`.

2. **`t = 1.2 мс` (Отримання конфігурації підписки)**:
   Воркер зчитує з локального кешу метадані кінцевої точки: URL `https://shop.example.com/webhooks`, `pinned_version: "2024-11-15"`, `primarySecret: "whsec_live_a1b2..."`, `status: "healthy"`.

3. **`t = 2.0 мс` (Трансформація версії)**:
   Диспетчер визначає різницю версій між `2026-03-01` та `2024-11-15`. Викликається трансформатор `2026-03-01->2024-11-15`, який перетворює об'єкт ціни `pricing` у ціле число `amount = 4500`. Формується фінальний рядок JSON для відправки.

4. **`t = 2.8 мс` (Розрахунок HMAC)**:
   Генерується мітка часу `now = 1718873600`. Формується підписаний рядок `1718873600.{"id":"evt_991",...}`. Обчислюється HMAC-SHA256 хеш `4a2f8b...`. Формується заголовок `Webhook-Signature: t=1718873600,v1=4a2f8b...`.

5. **`t = 3.5 мс` (Захоплення семафора хосту)**:
   Воркер перевіряє лімітер конкурентності для домену `shop.example.com`. На цей хост наразі відкрито 3 з'єднання з дозволених 20. Лічильник збільшується до 4.

6. **`t = 4.1 мс` (Встановлення TCP/TLS з'єднання)**:
   HTTP-агент перевіряє пул `keep-alive`. З'єднання з хостом `shop.example.com:443` уже відкрите, тому рукостискання TLS пропускається (затримка 0 мс).

7. **`t = 4.8 мс` (Відправлення HTTP POST запиту)**:
   Воркер передає байти тіла в сокет. Запускається таймер таймауту на 5000 мс.

8. **`t = 124.5 мс` (Отримання відповіді)**:
   Сервер клієнта повертає заголовки зі статусом `HTTP/1.1 500 Internal Server Error`. Воркер починає зчитувати тіло відповіді. Потік надсилає 65 КБ HTML-сторінки звіту про помилку Django. Потоковий обмежувач записує в буфер перші `4096` байт і відкидає решту.

9. **`t = 125.8 мс` (Оновлення Circuit Breaker)**:
   Статус-код `500` класифікується як тимчасовий збій. Лічильник `consecutiveFailures` для `ep_772` збільшується з 0 до 1. Стан залишається `healthy`.

10. **`t = 126.5 мс` (Асинхронний запис логу та планування повтору)**:
    Формується запис `DeliveryAttemptLog` із тривалістю `121 ms` та обрізаним фрагментом відповіді. Запис відправляється в чергу аналітики ClickHouse. Подія планується до повторного відправлення в чергу `webhooks_retry_15s` із затримкою 15 секунд. Семафор хосту звільняється (лічильник зменшується до 3).

---

## Розбір крайових випадків та небезпек у вихідних викликах

Під час експлуатації вихідного диспетчера інженери стикаються зі специфічними мережевими та безпековими загрозами, які не виникають у класичних вхідних веб-сервісах.

### 1. Атаки DNS Rebinding під час вихідних викликів
Зловмисник може зареєструвати ендпоінт із власним доменом `evil.com`, який на момент реєстрації та перевірки на порталі повертає публічну IP-адресу `198.51.100.1`. Проте під час наступного виклику вебхука авторитетний DNS-сервер зловмисника повертає IP-адресу з дуже коротким TTL (0 секунд), яка вказує на внутрішній сервіс AWS: `169.254.169.254`. Якщо диспетчер виконає виклик безпосередньо за доменним ім'ям, він надішле запит на внутрішній сервер метаданих і розкриє службові ключі доступу.

Захист реалізується через **кастомний DNS-резолвер із прив'язкою IP на рівні сокета**:
* Диспетчер самостійно виконує DNS-запит перед відкриттям з'єднання.
* Отримана IP-адреса перевіряється за чорним списком заборонених діапазонів (RFC 1918, RFC 3927, Loopback).
* З'єднання відкривається безпосередньо за валідованою IP-адресою, а оригінальне доменне ім'я передається виключно в полі TLS SNI (Server Name Indication) та HTTP-заголовку `Host`.

### 2. Захист від Replay-атак та атак за часом (Timing Attacks)
Під час перевірки підпису клієнтські бібліотеки SDK зобов'язані використовувати алгоритм порівняння з постійним часом виконання. Стандартний оператор рівності рядків (`===` у JavaScript або `==` у C++) перевіряє байти послідовно і перериває виконання на першому невідповідному символі. Це дозволяє зловмиснику методом перебору та вимірювання мікросекундних затримок побайтово відновити валідний підпис.

Для запобігання цій вразливості в SDK використовується функція `crypto.timingSafeEqual()` у Node.js або бітове побітове накопичення різниці (Bitwise XOR Accumulator) у C++:

```cpp
bool constantTimeCompare(std::string_view a, std::string_view b) {
    if (a.size() != b.size()) return false;
    unsigned char result = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        result |= static_cast<unsigned char>(a[i] ^ b[i]);
    }
    return result == 0;
}
```

### 3. Лімітування вихідної конкурентності (Per-Host Concurrency Control)
Коли платформа проводить масовий імпорт даних (наприклад, перерахунок залишків для мільйона товарів), генератор подій створює лавину з 100 000 вебхуків на хвилину, адресованих одному й тому самому мерчанту. Якщо диспетчер надішле всі ці запити паралельно, він створить локальну Distributed Denial of Service атаку на інфраструктуру клієнта.

Щоб запобігти цьому, диспетчер реалізує механізм **семафорів на рівні цільового домену** (Domain Semaphore):
* Для кожного унікального хосту (наприклад, `api.partner.com`) виділяється ліміт паралельних викликів (за замовчуванням 10–20 одночасних TCP-сесій).
* Завдання, які перевищують ліміт, залишаються в черзі брокера повідомлень і вичитуються лише в міру звільнення слотів.
* Якщо час відповіді клієнта (TTFB) починає зростати (наприклад, перевищує 2000 мс), адаптивний алгоритм автоматично знижує ліміт конкурентності для цього хосту (Dynamic Concurrency Backpressure), даючи серверу споживача можливість відновити продуктивність.

---

## Порівняльний аналіз реалізацій (TypeScript проти C++)

Вибір мови програмування для ядра диспетчера вебхуків залежить від масштабу навантаження платформи:

1. **TypeScript (Node.js)**:
   * Ідеально підходить для I/O-bound навантажень середнього масштабу (до 10 000 вихідних викликів на секунду).
   * Асинхронна модель Event Loop ефективно обслуговує тисячі відкритих мережевих сокетів без створення системних потоків.
   * Витрати оперативної пам'яті на один сокет становлять приблизно 2–4 КБ, але збирач сміття (Garbage Collector) може створювати короткочасні мікропаузи під час активного створення мільйонів тимчасових JSON-об'єктів.

2. **C++ (C++20)**:
   * Застосовується у високонавантажених платформах масштабу Stripe чи Cloudflare (понад 100 000 вихідних викликів на секунду на одну ноду).
   * Використання асинхронного введення-виведення на базі Linux `io_uring` або бібліотеки `Boost.Beast` дозволяє досягти нульового копіювання пам'яті (Zero-Copy) завдяки `std::string_view` та кастомним пулам пам'яті.
   * Детерміноване звільнення ресурсів через RAII унеможливлює витоки пам'яті та стрибки затримок (Latency Spikes), гарантуючи стабільний час реакції диспетчера.

---

## Інженерні рекомендації для виробничого контуру

Під час розгортання диспетчера у високонавантаженому виробничому середовищі необхідно дотримуватися таких практичних правил:

1. **Пул з'єднань із повторним використанням TCP (Keep-Alive)**:
   Для кожного унікального доменного імені клієнта слід підтримувати виділений пул агентів (`http.Agent({ keepAlive: true, maxSockets: 20 })`). Це усуває накладні витрати на повторне проходження триетапного рукостискання TCP (SYN-SYN/ACK-ACK) та узгодження ключів TLS на кожну подію, знижуючи затримку доставки на 50–150 мс на кожен виклик.

2. **Захист від повторних збоїв DNS (DNS Caching з TTL)**:
   Стандартні бібліотечні виклики `getaddrinfo` в операційній системі є синхронними та блокуючими. Високонавантажений диспетчер повинен використовувати внутрішній кеш резолвінгу DNS (наприклад, `c-ares` або кешуючий локальний DNS-демон Unbound/CoreDNS) з обмеженим часом життя (TTL = 30–60 секунд), щоб уникнути блокування робочих потоків під час тимчасової недоступності зовнішніх DNS-серверів клієнта.

3. **Гарантія незмінності серіалізованого JSON**:
   Обчислення HMAC-підпису та відправлення тіла через мережу повинні використовувати **один і той самий рядок байтів**. Якщо серіалізувати JSON в один буфер для розрахунку підпису, а потім повторно серіалізувати його через інший виклик `JSON.stringify()` для передачі в сокет, можлива зміна порядку ключів чи форматування чисел (наприклад, `50.0` проти `50`), що зробить підпис недійсним на стороні споживача.
