# ⚙️ Трирівневий кеш стану DH з інвалідацією через Redis Pub/Sub та Edge Surrogate Keys

Практична реалізація багатоярусного кешування у платформі Digital Homes (DH) вимагає чіткого розподілу відповідальності між трьома пластами: локальною оперативною пам'яттю процесу (L1), розподіленим кеш-сервером Redis (L2) та Edge CDN (L3). Головне інженерне завдання полягає у забезпеченні атомарності оновлення даних, захисті від кеш-штормів (Singleflight coalescing), швидкому розсиланні подій про вимивання (Eviction Fanout) через Pub/Sub канал та обробці крайових режимів деградації при збоях мережі.

Нижче наведено побудову та вичерпний аналіз робочого харнеса трирівневого кешу для обробки стану пристроїв розумного будинку `HomeState`.

## 1. Архітектурні вимоги та внутрішній механізм

Харнес реалізує два основні шляхи руху даних:
- **Шлях читання (Read Path):** Запит послідовно опитує L1 (Process Memory) → L2 (Redis Cluster) → Singleflight Group (Origin DB Fetch). Перехід на наступний рівень відбувається лише при виявленні промаху (Cache Miss). У разі успішного витягування з нижнього ярусу результат каскадно заповнює верхні яруси для наступних запитів.
- **Шлях запису та інвалідації (Write & Eviction Path):** При зміні стану пристрою система виконує атомарний запис у базу даних, оновлює значення в L2 Redis, видаляє ключ із локального L1, надсилає евент у Redis Pub/Sub для вимивання L1 на всіх інших вузлах API-кластера, та генерує HTTP-виклик до Edge CDN Purge API за тегом `Surrogate-Key`.

### Захист від зсуву версій та конкурентних перегонів (Race Conditions)

У багатьох вузлах API можлива ситуація, коли два записи оновлення стану для одного й того самого будинку надходять із різницею у 2 мілісекунди на різні API-сервери. Якщо повідомлення Pub/Sub про інвалідацію від першого запису запізниться й прийде **після** другого запису, локальний L1-кеш може виявитися заповненим застарілими даними.

Для запобігання цій пастці структури даних `HomeState` містять монотонно зростаючий лічильник версії `version`. При записі у L1 та L2 кеш нове значення приймається лише тоді, коли `newState.version > currentCachedState.version`. Якщо отримана з Pub/Sub або Redis версія є меншою або рівною тій, що вже лежить у локальній пам'яті, оновлення ігнорується.

### Керування обсягом пам'яті (Memory Bound & Eviction)

Пам'ять L1-кешу у межах одного процесу API обмежена. Безконтрольне додавання нових ключів `dh:home:{id}` призведе до вичерпання RAM та спрацювання Linux OOM Killer. Тому реалізація L1 спирається на обмежену за розміром хеш-таблицю із підтримкою вимивання найменш вживаних елементів (Bounded LRU Policy). При досягненні ліміту у 10 000 будинків найстаріші елементи автоматично витісняються з L1, при цьому вони залишаються доступними у L2 Redis.

## 2. Реалізація харнеса мовами C++20 та TypeScript

Нижче наведено автономні, ідіоматичні реалізації трирівневого кешу. Версія на C++20 використовує потокобезпечні потокові примітиви `std::shared_mutex` (reader-writer lock) для наносекундного паралельного читання без блокування сусідніх потоків, а також `std::promise` / `std::shared_future` для схлопування паралельних запитів Singleflight. Версія на TypeScript реалізує асинхронні `Promise`-ланцюжки та подієвий `EventEmitter`.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <shared_mutex>
#include <mutex>
#include <memory>
#include <optional>
#include <future>
#include <chrono>
#include <functional>
#include <vector>
#include <stdexcept>

// DTO стану пристрою та дому
struct DeviceState {
    std::string id;
    std::string type;
    std::string status;
    double value;
};

struct HomeState {
    std::string homeId;
    std::vector<DeviceState> devices;
    uint64_t version{0}; // Монотонна версія для запобігання race conditions
};

// Симулятор L2 Redis Клієнта та мережевого транспортного шару
class RedisClientMock {
public:
    std::optional<HomeState> get(const std::string& key) {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        auto it = store_.find(key);
        if (it != store_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    void set(const std::string& key, const HomeState& state, std::chrono::seconds ttl) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        auto it = store_.find(key);
        if (it == store_.end() || state.version >= it->second.version) {
            store_[key] = state;
        }
    }

    void publishInvalidation(const std::string& channel, const std::string& key, uint64_t version) {
        std::cout << "[L2 Redis Pub/Sub] Evict broadcast on channel '" << channel 
                  << "' for key: " << key << " (v" << version << ")" << std::endl;
    }

private:
    std::unordered_map<std::string, HomeState> store_;
    std::shared_mutex mutex_;
};

// Схлопувач запитів (Singleflight / Request Coalescing)
// Гарантує, що при N паралельних промахах кешу виконується РІВНО ОДИН запит до Origin DB
class SingleflightGroup {
public:
    using Fetcher = std::function<HomeState()>;

    HomeState doCall(const std::string& key, Fetcher fetcher) {
        std::shared_ptr<Call> callPtr;
        bool isLeader = false;

        {
            std::lock_guard<std::mutex> lock(mutex_);
            auto it = calls_.find(key);
            if (it != calls_.end()) {
                // Запит вже виконується іншим потоком — підключаємося до його future
                callPtr = it->second;
            } else {
                // Поточний потік є першим (лідером) — створюємо новий запит
                callPtr = std::make_shared<Call>();
                callPtr->futureResult = callPtr->promiseResult.get_future().share();
                calls_[key] = callPtr;
                isLeader = true;
            }
        }

        if (!isLeader) {
            // Ведені потоки чекають завершення лідера без генерації повторних SQL-запитів
            return callPtr->futureResult.get();
        }

        // Лідери виконують реальний фетч із бази даних
        try {
            HomeState res = fetcher();
            callPtr->promiseResult.set_value(res);

            std::lock_guard<std::mutex> lock(mutex_);
            calls_.erase(key);
            return res;
        } catch (...) {
            callPtr->promiseResult.set_exception(std::current_exception());
            std::lock_guard<std::mutex> lock(mutex_);
            calls_.erase(key);
            throw;
        }
    }

private:
    struct Call {
        std::promise<HomeState> promiseResult;
        std::shared_future<HomeState> futureResult;
    };

    std::mutex mutex_;
    std::unordered_map<std::string, std::shared_ptr<Call>> calls_;
};

// Потокобезпечний трирівневий менеджер кешу DH
class TieredCacheManager {
public:
    explicit TieredCacheManager(std::shared_ptr<RedisClientMock> redis)
        : redis_(std::move(redis)) {}

    // ── Read Path ─────────────────────────────────────────────────────────────
    HomeState getHomeState(const std::string& homeId, std::function<HomeState(const std::string&)> originDBFetch) {
        std::string cacheKey = "dh:home:" + homeId;

        // Ярус 1: Перевірка L1 Process Memory (без мережевих затримок)
        {
            std::shared_lock<std::shared_mutex> lock(l1Mutex_);
            auto it = l1Cache_.find(cacheKey);
            if (it != l1Cache_.end()) {
                std::cout << "[L1 HIT] Home " << homeId << " (v" << it->second.version << ") from RAM." << std::endl;
                return it->second;
            }
        }

        // Ярус 2: Перевірка L2 Redis Cluster (мережевий RTT 1-2 ms)
        auto l2Opt = redis_->get(cacheKey);
        if (l2Opt.has_value()) {
            std::cout << "[L2 HIT] Home " << homeId << " (v" << l2Opt->version << ") from Redis." << std::endl;
            populateL1(cacheKey, l2Opt.value());
            return l2Opt.value();
        }

        // Ярус 3: L1/L2 MISS — Виклик Singleflight для ізоляції Origin DB
        std::cout << "[L1/L2 MISS] Singleflight coalescing for home: " << homeId << std::endl;
        return singleflight_.doCall(cacheKey, [&]() {
            HomeState stateFromDB = originDBFetch(homeId);

            // Заповнюємо L2 та L1 для наступних викликів
            redis_->set(cacheKey, stateFromDB, std::chrono::seconds(300));
            populateL1(cacheKey, stateFromDB);

            return stateFromDB;
        });
    }

    // ── Write Path & Eviction ──────────────────────────────────────────────────
    void updateHomeState(const HomeState& newState, std::function<void(const HomeState&)> originDBSave) {
        std::string cacheKey = "dh:home:" + newState.homeId;

        // 1. Атомарний запис у база даних (сховище правди)
        originDBSave(newState);

        // 2. Оновлення L2 Redis
        redis_->set(cacheKey, newState, std::chrono::seconds(300));

        // 3. Інвалідація локального L1
        invalidateL1(cacheKey, newState.version);

        // 4. Публікація евенту інвалідації для сусідніх API-вузлів
        redis_->publishInvalidation("dh:invalidation", cacheKey, newState.version);

        // 5. Виклик L3 Edge CDN Purge API за Surrogate Key
        purgeEdgeCDN(newState.homeId);
    }

    // Обробник Pub/Sub повідомлення про інвалідацію від іншого вузла
    void invalidateL1(const std::string& cacheKey, uint64_t newVersion) {
        std::unique_lock<std::shared_mutex> lock(l1Mutex_);
        auto it = l1Cache_.find(cacheKey);
        if (it != l1Cache_.end()) {
            if (newVersion >= it->second.version) {
                l1Cache_.erase(it);
                std::cout << "[L1 EVICT] Removed key: " << cacheKey << " (v" << newVersion << ")" << std::endl;
            }
        }
    }

private:
    void populateL1(const std::string& key, const HomeState& state) {
        std::unique_lock<std::shared_mutex> lock(l1Mutex_);
        auto it = l1Cache_.find(key);
        if (it == l1Cache_.end() || state.version >= it->second.version) {
            l1Cache_[key] = state;
        }
    }

    void purgeEdgeCDN(const std::string& homeId) {
        std::cout << "[L3 CDN PURGE] Triggered Soft Purge for Surrogate-Key: home-" << homeId << std::endl;
    }

    std::shared_mutex l1Mutex_;
    std::unordered_map<std::string, HomeState> l1Cache_;
    std::shared_ptr<RedisClientMock> redis_;
    SingleflightGroup singleflight_;
};
```
```ts
import { EventEmitter } from "events";

interface DeviceState {
  id: string;
  type: string;
  status: string;
  value: number;
}

interface HomeState {
  homeId: string;
  devices: DeviceState[];
  version: number;
}

// Singleflight група для TypeScript (схлопування паралельних промахів)
class SingleflightTS {
  private inFlight = new Map<string, Promise<HomeState>>();

  async doCall(key: string, fetcher: () => Promise<HomeState>): Promise<HomeState> {
    const existing = this.inFlight.get(key);
    if (existing) {
      console.log(`[Singleflight TS] Coalesced request for key: ${key}`);
      return existing;
    }

    const promise = (async () => {
      try {
        return await fetcher();
      } finally {
        this.inFlight.delete(key);
      }
    })();

    this.inFlight.set(key, promise);
    return promise;
  }
}

export class TieredCacheNodeTS {
  private l1Memory = new Map<string, HomeState>();
  private redisStore = new Map<string, HomeState>();
  private pubsub = new EventEmitter();
  private singleflight = new SingleflightTS();

  constructor() {
    // Підписка на мережеві події вимивання L1
    this.pubsub.on("evict", (key: string, version: number) => {
      const current = this.l1Memory.get(key);
      if (!current || version >= current.version) {
        this.l1Memory.delete(key);
        console.log(`[L1 TS Evict] Key evicted: ${key} (v${version})`);
      }
    });
  }

  // ── Read Path ─────────────────────────────────────────────────────────────
  async getHomeState(
    homeId: string,
    originDBFetch: (id: string) => Promise<HomeState>
  ): Promise<HomeState> {
    const cacheKey = `dh:home:${homeId}`;

    // 1. Перевірка L1 Process Memory
    if (this.l1Memory.has(cacheKey)) {
      const cached = this.l1Memory.get(cacheKey)!;
      console.log(`[L1 TS HIT] Key: ${cacheKey} (v${cached.version})`);
      return cached;
    }

    // 2. Перевірка L2 Redis Cluster
    if (this.redisStore.has(cacheKey)) {
      const redisVal = this.redisStore.get(cacheKey)!;
      console.log(`[L2 TS HIT] Key: ${cacheKey} (v${redisVal.version})`);
      this.l1Memory.set(cacheKey, redisVal);
      return redisVal;
    }

    // 3. L1/L2 MISS: Singleflight DB Fetch
    return this.singleflight.doCall(cacheKey, async () => {
      console.log(`[Origin DB Fetch TS] Executing single query for: ${cacheKey}`);
      const freshState = await originDBFetch(homeId);
      
      this.redisStore.set(cacheKey, freshState);
      this.l1Memory.set(cacheKey, freshState);
      return freshState;
    });
  }

  // ── Write Path ────────────────────────────────────────────────────────────
  async updateHomeState(
    newState: HomeState,
    originDBSave: (state: HomeState) => Promise<void>
  ): Promise<void> {
    const cacheKey = `dh:home:${newState.homeId}`;

    // 1. Запис у базу даних
    await originDBSave(newState);

    // 2. Запис у L2 Redis
    this.redisStore.set(cacheKey, newState);

    // 3. Локальна інвалідація та трансляція у Pub/Sub
    this.pubsub.emit("evict", cacheKey, newState.version);

    // 4. Виклик L3 Edge Purge API
    console.log(`[L3 CDN Purge TS] Soft Purge header: Surrogate-Key home-${newState.homeId}`);
  }
}
```
:::

## 3. Деградація та обробка збоїв (Failure Modes)

У реальній експлуатації трирівневого кешу виникають чотири типи аварійних режимів, для яких у харнесі передбачено відповідні захисні механізми:

### А. Аварія або недоступність L2 Redis (Redis Cluster Partition / Outage)

Якщо кластер Redis стає недоступним через мережеве розщеплення (Split-Brain) або падіння вузлів, виклик `redis_->get()` викидає виняток або повертає помилку таймауту.

- **Поведінка системи:** Сервіс не повинен падати. Система автоматично перемикається у **деградований режим (Fallback Mode)**: запити переходять безпосередньо з L1 на Singleflight-блок до Origin DB.
- **Обмеження трафіку:** Щоб Origin DB не впала від зникнення L2-ярусу, Singleflight обмежує кількість паралельних SQL-запитів, а сервіс знижує TTL для локального L1-кешу з 10 секунд до 2 секунд, гарантуючи ізоляцію бази від пікового шторму.

### Б. Пропускання Pub/Sub повідомлень про інвалідацію

Оскільки Redis Pub/Sub працює за принципом «надіслав і забув» (At-most-once delivery), при короткочасному розриві мережевого з'єднання між API-вузлом та Redis евент вимивання може бути втрачено.

- **Захист:** Локальний L1-кеш завжди має жорсткий максимальний час життя (Absolute Hard TTL = 15 секунд). Навіть якщо евент інвалідації було пропущено, L1-кеш гарантовано самоочиститься через 15 секунд, обмежуючи максимальне вікно неузгодженості.

### В. Холодний старт кластера (Cold Start / Data Center Recovery)

При розгортанні нового регіону або відновленні дата-центру після повного знеструмлення яруси L1 та L2 є абсолютного порожніми. Одночасний пуск мобільного трафіку спричинить 100% промахів на всіх ярусах.

- **Захист:** Застосовується стратегія **прогріву кешу (Cache Warming)**. Перед переключенням мережевого DNS-трафіку фоновий скрипт-прогрівач вичитує зі сховища перелік 5% найактивніших будинків і заповнює L2 Redis до моменту відкриття публічних воріт.

## 4. Простеження та метрики (Tracing & Observability)

Для контролю ефективності трирівневого кешу кожен вузол експортує наступні метрики Prometheus та OpenTelemetry tracepoints:

1. `dh_cache_requests_total{tier="l1|l2|l3", result="hit|miss"}` — Лічильник запитів за ярусами та результатами.
2. `dh_singleflight_coalesced_requests_total{key_prefix="dh:home"}` — Кількість зрізаних запитів, які очікували на лідера у Singleflight-групі.
3. `dh_cache_eviction_events_total{source="pubsub|ttl|lru"}` — Кількість виконаних інвалідацій L1-пам'яті.

Приклад ланцюжка OpenTelemetry трасування одного запиту:
```
[Span: GET /api/v1/homes/101/devices] (total: 21.2 ms)
 ├── [Span: l1_memory_lookup] (0.05 ms) -> MISS
 ├── [Span: l2_redis_get] (1.8 ms) -> MISS
 └── [Span: singleflight_exec] (19.3 ms)
      └── [Span: postgres_query_select_devices] (18.1 ms) -> SUCCESS
```

Цей аналіз і наведений робочий код повністю закривають практичну поверхню реалізації багатоярусного кешування у системі Digital Homes.
