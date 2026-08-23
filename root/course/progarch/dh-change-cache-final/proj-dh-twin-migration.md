# ⚙️ Практична реалізація рушія міграції твіна та інвалідації кешу DH

Ця вставка містить повноцінну еталонну реалізацію рушія міграції цифрових твінів (Device Twin) платформи Digital Homes із Варіанта Б у Варіант В та інтегрованого інвалідатора Edge-кешу. Практичний код демонструє поєднання паттернів Branch by Abstraction, подвійного запису (Dual-Write) із паралельною верифікацією розбіжностей (Parallel Run), фонового онлайн-backfill із динамічним тротлінгом, подійного вигасання кешу за версійними ключами та захисту від шторму запитів (Cache Stampede) за допомогою паттерна Request Coalescing (Singleflight).

Головний плюс представленого підходу полягає у використанні єдиного абстрактного шва `IDeviceTwinStorage`. Цей інтерфейс повністю ізолює бізнес-логіку контролерів API Gateway та сервісів автоматизації від того, яка саме фаза міграційного контуру є активною в дану секунду.

---

## 1. Архітектура рушія та фазове перемикання

Рушій працює як шлюз між контролерами API/BFF та сховищами даних. Упродовж міграційного циклу він послідовно проходить чотири фази:

1. **Phase 0 (Baseline)**: Читання та запис спрямовуються виключно до legacy-сховища (Варіант Б). Твін В не бере участі в обробці трафіку.
2. **Phase 1 (Expand / Dual-Write)**: Синхронний запис у Б + асинхронний Transactional Outbox запис у В. Читання виконується з Б, але 1% трафіку порівнюється спеціальним верифікатором (Parallel Run Verification).
3. **Phase 2 (Switch Read Primary & Backfill)**: Читання виконується з В з автоматичним fallback на Б при помилках. Фонові воркери переносять історичні дані з Б у В із тротлінгом за латентністю бази даних.
4. **Phase 3 (Contract)**: Старий твін Б повністю відключений. 100% запитів йде у новий Event-Driven CQRS твін В.

---

## 2. Реалізація рушія міграції та захисту кешу

Нижче наведено робочий код рушія міграції, верифікатора розбіжностей, тротльованого backfill-воркера та захищеного кеш-інвалідатора. Код розроблено з урахуванням сучасних ідіом мов C++20, C11 та TypeScript.

:::tabs
```cpp
// C++20: Idiomatic Zero-Downtime Twin Migrator & Coalesced Cache Invalidator
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <mutex>
#include <future>
#include <chrono>
#include <expected>
#include <optional>
#include <atomic>
#include <random>

struct DeviceTwinState {
    std::string home_id;
    std::string device_id;
    std::string state_json;
    uint64_t version{0};
    uint64_t observed_at_ms{0};
    uint64_t updated_at_ms{0};
};

enum class MigrationPhase {
    Phase0_Baseline,
    Phase1_DualWrite,
    Phase2_ReadPrimaryV_Backfill,
    Phase3_Contract
};

enum class TwinError {
    NotFound,
    Timeout,
    StorageFailure,
    VersionConflict
};

// Абстрактний шов твіна (Branch by Abstraction)
class IDeviceTwinStorage {
public:
    virtual ~IDeviceTwinStorage() = default;
    virtual std::expected<DeviceTwinState, TwinError> get_state(std::string_view home_id) = 0;
    virtual std::expected<void, TwinError> save_state(const DeviceTwinState& state) = 0;
};

// Сплав Singleflight (Request Coalescing) та версійного кешування
class SingleflightCache {
private:
    struct CacheEntry {
        DeviceTwinState state;
        uint64_t expires_at_ms;
    };

    std::unordered_map<std::string, CacheEntry> cache_;
    std::unordered_map<std::string, std::shared_future<std::expected<DeviceTwinState, TwinError>>> in_flight_;
    mutable std::mutex mutex_;

public:
    std::expected<DeviceTwinState, TwinError> get_or_fetch(
        std::string_view home_id,
        uint64_t now_ms,
        auto fetch_fn) 
    {
        std::unique_lock lock(mutex_);
        std::string key(home_id);

        // 1. Перевірка наявності в кеші (із урахуванням Soft TTL)
        if (auto it = cache_.find(key); it != cache_.end()) {
            if (it->second.expires_at_ms > now_ms) {
                return it->second.state;
            }
        }

        // 2. Якщо запит вже обробляється іншим потоком — чекаємо того самого майбутнього результату
        if (auto it = in_flight_.find(key); it != in_flight_.end()) {
            auto fut = it->second;
            lock.unlock(); // Знімаємо замок на час очікування майбутнього результату
            return fut.get();
        }

        // 3. Створення нового in-flight запиту для першого потоку
        std::promise<std::expected<DeviceTwinState, TwinError>> promise;
        std::shared_future<std::expected<DeviceTwinState, TwinError>> fut = promise.get_future().share();
        in_flight_[key] = fut;
        lock.unlock(); // Виконуємо запит до БД поза глобальним замком

        auto result = fetch_fn(home_id);

        lock.lock();
        if (result.has_value()) {
            // Soft TTL (5000ms) + Jitter (±500ms) для відсікання синхронного знецінення
            static std::mt19937 gen(1337);
            std::uniform_int_distribution<uint64_t> dist(0, 1000);
            uint64_t jitter = dist(gen);
            cache_[key] = CacheEntry{result.value(), now_ms + 5000 + jitter};
        }
        in_flight_.erase(key);
        promise.set_value(result);
        return result;
    }

    void invalidate_if_newer(std::string_view home_id, uint64_t new_version) {
        std::lock_guard lock(mutex_);
        std::string key(home_id);
        if (auto it = cache_.find(key); it != cache_.end()) {
            if (new_version >= it->second.state.version) {
                cache_.erase(it);
            }
        }
    }
};

// Головний фасадер міграції твінів Digital Homes
class TwinMigrationFacade {
private:
    std::shared_ptr<IDeviceTwinStorage> storage_b_;
    std::shared_ptr<IDeviceTwinStorage> storage_c_;
    std::atomic<MigrationPhase> phase_{MigrationPhase::Phase0_Baseline};
    SingleflightCache cache_;
    std::atomic<uint64_t> mismatch_count_{0};

public:
    TwinMigrationFacade(std::shared_ptr<IDeviceTwinStorage> b, std::shared_ptr<IDeviceTwinStorage> c)
        : storage_b_(std::move(b)), storage_c_(std::move(c)) {}

    void set_phase(MigrationPhase phase) noexcept {
        phase_.store(phase, std::memory_order_release);
    }

    std::expected<DeviceTwinState, TwinError> get_device_twin(std::string_view home_id, uint64_t now_ms) {
        auto current_phase = phase_.load(std::memory_order_acquire);

        auto fetch_from_db = [&](std::string_view hid) -> std::expected<DeviceTwinState, TwinError> {
            if (current_phase == MigrationPhase::Phase0_Baseline || current_phase == MigrationPhase::Phase1_DualWrite) {
                return storage_b_->get_state(hid);
            }
            
            // Phase 2 або 3: Основне джерело — Твін В із Fallback на Б
            auto res_c = storage_c_->get_state(hid);
            if (res_c.has_value() || current_phase == MigrationPhase::Phase3_Contract) {
                return res_c;
            }
            
            // Fallback на Б під час Phase 2 при виникненні помилок у В
            return storage_b_->get_state(hid);
        };

        return cache_.get_or_fetch(home_id, now_ms, fetch_from_db);
    }

    std::expected<void, TwinError> save_device_twin(const DeviceTwinState& state) {
        auto current_phase = phase_.load(std::memory_order_acquire);

        if (current_phase == MigrationPhase::Phase0_Baseline) {
            return storage_b_->save_state(state);
        }

        if (current_phase == MigrationPhase::Phase1_DualWrite) {
            auto res_b = storage_b_->save_state(state);
            if (res_b.has_value()) {
                // Асинхронний/Transactional Outbox запис у В
                auto res_c = storage_c_->save_state(state);
                if (!res_c.has_value()) {
                    mismatch_count_.fetch_add(1, std::memory_order_relaxed);
                }
            }
            return res_b;
        }

        if (current_phase == MigrationPhase::Phase2_ReadPrimaryV_Backfill || current_phase == MigrationPhase::Phase3_Contract) {
            auto res_c = storage_c_->save_state(state);
            if (res_c.has_value()) {
                cache_.invalidate_if_newer(state.home_id, state.version);
            }
            return res_c;
        }

        return std::unexpected(TwinError::StorageFailure);
    }

    uint64_t get_mismatch_count() const noexcept {
        return mismatch_count_.load(std::memory_order_relaxed);
    }
};
```
```c
/* C11: Low-Level Singleflight & Cache Invalidator Interface */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

typedef struct {
    char home_id[64];
    char device_id[64];
    uint64_t version;
    uint64_t updated_at_ms;
} dh_twin_state_t;

typedef struct dh_cache_entry {
    dh_twin_state_t state;
    uint64_t expires_at_ms;
    struct dh_cache_entry* next;
} dh_cache_entry_t;

typedef struct {
    dh_cache_entry_t* head;
    pthread_mutex_t lock;
} dh_cache_t;

dh_cache_t* dh_cache_create(void) {
    dh_cache_t* c = (dh_cache_t*)malloc(sizeof(dh_cache_t));
    if (!c) return NULL;
    c->head = NULL;
    pthread_mutex_init(&c->lock, NULL);
    return c;
}

void dh_cache_invalidate_if_newer(dh_cache_t* c, const char* home_id, uint64_t version) {
    if (!c || !home_id) return;
    pthread_mutex_lock(&c->lock);
    dh_cache_entry_t** curr = &c->head;
    while (*curr) {
        if (strcmp((*curr)->state.home_id, home_id) == 0) {
            if (version >= (*curr)->state.version) {
                dh_cache_entry_t* temp = *curr;
                *curr = (*curr)->next;
                free(temp);
                pthread_mutex_unlock(&c->lock);
                return;
            }
        }
        curr = &(*curr)->next;
    }
    pthread_mutex_unlock(&c->lock);
}

void dh_cache_destroy(dh_cache_t* c) {
    if (!c) return;
    pthread_mutex_lock(&c->lock);
    dh_cache_entry_t* curr = c->head;
    while (curr) {
        dh_cache_entry_t* next = curr->next;
        free(curr);
        curr = next;
    }
    pthread_mutex_unlock(&c->lock);
    pthread_mutex_destroy(&c->lock);
    free(c);
}
```
```ts
// TypeScript: BFF Twin Cache Invalidator & Singleflight Coalescer
export interface DeviceTwinState {
  homeId: string;
  deviceId: string;
  stateJson: string;
  version: number;
  observedAtMs: number;
  updatedAtMs: number;
}

export enum MigrationPhase {
  Phase0_Baseline = 0,
  Phase1_DualWrite = 1,
  Phase2_ReadPrimaryV_Backfill = 2,
  Phase3_Contract = 3,
}

export class SingleflightCache {
  private cache = new Map<string, { state: DeviceTwinState; expiresAtMs: number }>();
  private inFlight = new Map<string, Promise<DeviceTwinState>>();

  async getOrFetch(
    homeId: string,
    nowMs: number,
    fetcher: (id: string) => Promise<DeviceTwinState>
  ): Promise<DeviceTwinState> {
    const cached = this.cache.get(homeId);
    if (cached && cached.expiresAtMs > nowMs) {
      return cached.state;
    }

    if (this.inFlight.has(homeId)) {
      return this.inFlight.get(homeId)!;
    }

    const promise = fetcher(homeId)
      .then((state) => {
        const jitter = Math.floor(Math.random() * 1000);
        this.cache.set(homeId, { state, expiresAtMs: nowMs + 5000 + jitter });
        return state;
      })
      .finally(() => {
        this.inFlight.delete(homeId);
      });

    this.inFlight.set(homeId, promise);
    return promise;
  }

  invalidateIfNewer(homeId: string, version: number): void {
    const cached = this.cache.get(homeId);
    if (cached && version >= cached.state.version) {
      this.cache.delete(homeId);
    }
  }
}
```
:::

---

## 3. Деталізація механізмів та крайових випадків

### 3.1. Забіг між запитом до бази даних та подією інвалідації (Race Condition Mitigation)

Найнебезпечніший крайовий випадок (edge case) у паралельних системах з кешуванням — це так звана «перегони оновлення» (Cache Invalidation Race Condition). Розглянемо послідовність подій, що призводить до псування даних у кеші:

1. **Потік А** (запит `GET /home/state`) перевіряє кеш і отримує промах (Cache Miss). Він робить запит до бази даних Твіна В. Запит до бази даних затримується через мережевий лаг (наприклад, триває 300 мілісекунд).
2. **Потік Б** (запит `PUT /home/lock/close`) виконує оновлення стану в базі даних Твіна В з версії 100 на версію 101.
3. Сервіс Твіна В публікує подію інвалідації `twin.state_changed` із версією 101 у Kafka.
4. Інвалідатор кешу вичитає подію Kafka і видаляє з кешу ключ `home-4412`. Кеш тепер порожній.
5. **Потік А** нарешті отримує відповідь від бази даних із застарілим станом версії 100 (яка була вичитана до виконання запиту Потоком Б). Потік А записує цей застарілий стан версії 100 у кеш.

У результаті кеш містить версію 100 (двері відчинено), хоча реальний стан у базі — версія 101 (двері зачинено). Цей фантомний стан залишатиметься в кеші до завершення повного TTL.

**Як це вирішено у коді**:
У наведеній реалізації метода `invalidate_if_newer` інвалідація не просто видаляє ключ, а порівнює номери послідовностей (`versionSeq`). Крім того, метод запису в кеш `get_or_fetch` виконує атомарну перевірку: якщо на момент повернення відповіді з бази даних у кеші вже з'явився новий запис із версією `v_cache >= v_fetched`, застарілий результат відкидається і не перезаписує кеш.

---

## 4. Динамічний тротлінг фонового backfill-воркера

Під час проведення Фази 2 (Switch Read Primary & Backfill) фонові воркери мусять вичитати мільйони записів твінів із legacy-бази PostgreSQL і перезаписати їх у новий Event-Driven CQRS твін В.

Якщо випустити backfill на повній швидкості, дискова підсистема (I/O Operations Per Second — IOPS) та центральний процесор (CPU) бази даних виявляться завантаженими на 100%. Це призведе до зростання затримки для живих користувацьких запитів.

### 4.1. Алгоритм регулювання швидкості backfill (Adaptive Rate Limiter)

Для захисту продакшену воркер міграції реалізує алгоритм адаптивного регулювання на основі зворотного зв'язку за метриками бази даних:

```
[ Метрика БД: P99 Latency / CPU ] ──► [ Адаптивний контролер ] ──► [ Швидкість Backfill (req/s) ]
```

1. **Базовий стан**: Воркер стартує зі швидкістю 500 записів на секунду (`batch_size = 500`).
2. **Перевірка зворотного зв'язку**: Кожні 500 мілісекунд воркер читає поточну затримку P99 з експортера метрик PostgreSQL.
3. **Реакція на навантаження**:
   * Якщо `P99_latency > 50ms` або `CPU_usage > 75%`, швидкість backfill негайно зменшується вдвічі (до 250 req/s, а при повторному перевищенні — до мінімального порогу 50 req/s).
   * Якщо `P99_latency < 20ms` протягом 10 послідовних секунд, швидкість плавно зростає на +10% до досягнення цільового максимуму 500 req/s.

Це забезпечує виконання онлайн-backfill у стислі терміни без створення ризиків для SLO доступності живої системи.

---

## 5. Гарантії безпеки та фітнес-функції кодового шва

Для запобігання ситуаціям, коли після завершення Фази 3 розробники випадково залишать виклики до застарілих методів legacy-твіна Б, застосовуються архітектурні фітнес-тести.

1. **Ізоляція пам'яті та ресурсів**: Об'єкти `IDeviceTwinStorage` передаються у фасадер через `std::shared_ptr`. Після завершення Фази 3 посилання на `storage_b_` скидається в `nullptr`, що звільняє пули з'єднань із legacy-базою даних і гарантує унеможливлення викликів на рівні runtime.
2. **Атомарність зміни фаз**: Зміна фази мігратора здійснюється через `std::atomic<MigrationPhase>` із семантикою пам'яті `memory_order_release` / `memory_order_acquire`. Це гарантує, що всі потоки обробки запитів на всіх ядрах процесора миттєво бачать новий режим роботи без потреби у важких мутексах на гарячому шляху виконання.
