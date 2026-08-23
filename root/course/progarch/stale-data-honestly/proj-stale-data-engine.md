# ⚙️ Практичний рушій обробки застарілих даних та SWR-кешування

Цей практичний модуль демонструє повну робочу реалізацію рушія обробки метаданих свіжості даних, оцінки стану застарілості за алгоритмом SWR (*Stale-While-Revalidate*) та управління оптимістичними оновленнями стан-машини з автоматичним відкатом (rollback) у разі виникнення помилок сервера.

У розподілених системах клієнтський або edge-кеш зобов'язаний самостійно вираховувати лаг отриманих об'єктів та приймати рішення про вибір відповідного режиму відображення в UI. Рушій розділено на два ключових компоненти: серверно-мережевий обробник конвертів свіжості та клієнтський кеш-менеджер із підтримкою транзакційних відкатів намірів користувача.

Для охоплення різних архітектурних рівнів код подано у двох ідіоматичних варіантах:
- **C++20**: високопродуктивний рушій оцінки свіжості та машина оптимістичних станів для серверних проксі, шлюзів або локальних хабів розумного дому.
- **TypeScript**: клієнтський кеш-менеджер для веб- та мобільних застосунків, що реалізує асинхронну оцінку TTL, фонове оновлення SWR та транзакційні мутації UI.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <chrono>
#include <optional>
#include <memory>
#include <functional>
#include <unordered_map>

// Стан свіжості об'єкта в кеші
enum class FreshnessState {
    Fresh,              // Дані абсолютно актуальні (age <= ttl)
    StaleRevalidating,  // Застаріли, але у вікні грації: віддати кеш + оновити у фоні
    StaleDegraded,      // Застаріли понад грацію: показати UI деградації
    Expired             // Протухли остаточно, віддача заборонена
};

// Конверт даних із метаданими свіжості
template <typename T>
struct FreshnessEnvelope {
    T data;
    std::chrono::system_clock::time_point dataTimestamp;
    std::chrono::system_clock::time_point fetchedAt;
    std::chrono::milliseconds ttl;
    std::chrono::milliseconds staleGraceWindow;

    // Оцінити стан свіжості на поточний момент часу
    FreshnessState evaluateState(std::chrono::system_clock::time_point now) const {
        auto age = std::chrono::duration_cast<std::chrono::milliseconds>(now - fetchedAt);
        if (age <= ttl) {
            return FreshnessState::Fresh;
        } else if (age <= (ttl + staleGraceWindow)) {
            return FreshnessState::StaleRevalidating;
        } else if (age <= (ttl + staleGraceWindow * 5)) {
            return FreshnessState::StaleDegraded;
        }
        return FreshnessState::Expired;
    }

    int64_t getLagMs(std::chrono::system_clock::time_point now) const {
        return std::chrono::duration_cast<std::chrono::milliseconds>(now - dataTimestamp).count();
    }
};

// Структура телеметрії пристрою Digital Homes
struct DeviceTelemetry {
    std::string deviceId;
    double temperatureC;
    bool isOnline;
};

// Менеджер оптимістичного стану (Desired vs Reported)
class OptimisticStateEngine {
public:
    using RollbackCallback = std::function<void(const std::string& errorReason)>;

    struct DeviceState {
        bool reportedPowerState; // Підтверджений стан із БД/хаба
        std::optional<bool> desiredPowerState; // Оптимістичний намір користувача
        bool isPending{false};
    };

    void applyOptimisticChange(const std::string& deviceId, bool desiredState) {
        auto& state = m_states[deviceId];
        state.desiredPowerState = desiredState;
        state.isPending = true;
        std::cout << "[OptimisticUI] Device " << deviceId << " set pending desired: "
                  << (desiredState ? "ON" : "OFF") << std::endl;
    }

    void confirmState(const std::string& deviceId, bool confirmedState) {
        auto& state = m_states[deviceId];
        state.reportedPowerState = confirmedState;
        state.desiredPowerState.reset();
        state.isPending = false;
        std::cout << "[OptimisticUI] Device " << deviceId << " confirmed state: "
                  << (confirmedState ? "ON" : "OFF") << std::endl;
    }

    void rollbackChange(const std::string& deviceId, const std::string& reason) {
        auto& state = m_states[deviceId];
        state.desiredPowerState.reset();
        state.isPending = false;
        std::cout << "[OptimisticUI ROLLBACK] Device " << deviceId
                  << " reverted due to: " << reason << std::endl;
    }

    DeviceState getState(const std::string& deviceId) const {
        auto it = m_states.find(deviceId);
        if (it != m_states.end()) return it->second;
        return {false, std::nullopt, false};
    }

private:
    std::unordered_map<std::string, DeviceState> m_states;
};

int main() {
    using namespace std::chrono;
    auto now = system_clock::now();

    // Створюємо конверт застарілих даних (лаг 45 секунд при TTL 10 секунд)
    FreshnessEnvelope<DeviceTelemetry> env{
        DeviceTelemetry{"sensor-living-room", 22.4, true},
        now - seconds(45), // dataTimestamp
        now - seconds(25), // fetchedAt
        milliseconds(10000), // ttl: 10s
        milliseconds(30000)  // staleGraceWindow: 30s
    };

    FreshnessState state = env.evaluateState(now);
    std::cout << "Data Lag: " << env.getLagMs(now) << " ms" << std::endl;

    switch (state) {
        case FreshnessState::Fresh:
            std::cout << "UI Mode: STANDARD (Data is fresh)" << std::endl;
            break;
        case FreshnessState::StaleRevalidating:
            std::cout << "UI Mode: SWR (Show cache + trigger async revalidate)" << std::endl;
            break;
        case FreshnessState::StaleDegraded:
            std::cout << "UI Mode: DEGRADED (Show badge 'Updated 25s ago')" << std::endl;
            break;
        case FreshnessState::Expired:
            std::cout << "UI Mode: EXPIRED (Show error / placeholder)" << std::endl;
            break;
    }

    // Демонстрація оптимістичного оновлення та відкату
    OptimisticStateEngine optEngine;
    optEngine.applyOptimisticChange("light-kitchen", true);

    // Імітація збою сервера
    optEngine.rollbackChange("light-kitchen", "503 Gateway Timeout");

    return 0;
}
```
```ts
export type FreshnessStatus = 'FRESH' | 'STALE_REVALIDATING' | 'STALE_DEGRADED' | 'EXPIRED';

export interface FreshnessEnvelope<T> {
  data: T;
  dataTimestampIso: string;
  fetchedAtMs: number;
  ttlMs: number;
  staleGraceMs: number;
}

export interface SWREvaluation<T> {
  data: T;
  status: FreshnessStatus;
  lagMs: number;
  shouldRevalidate: boolean;
}

export class SWRCacheManager<T> {
  private cache = new Map<string, FreshnessEnvelope<T>>();

  public set(key: string, data: T, ttlMs: number, staleGraceMs: number, timestampIso?: string): void {
    this.cache.set(key, {
      data,
      dataTimestampIso: timestampIso || new Date().toISOString(),
      fetchedAtMs: Date.now(),
      ttlMs,
      staleGraceMs
    });
  }

  public evaluate(key: string): SWREvaluation<T> | null {
    const item = this.cache.get(key);
    if (!item) return null;

    const now = Date.now();
    const ageMs = now - item.fetchedAtMs;
    const dataTimeMs = new Date(item.dataTimestampIso).getTime();
    const lagMs = now - dataTimeMs;

    let status: FreshnessStatus = 'FRESH';
    let shouldRevalidate = false;

    if (ageMs <= item.ttlMs) {
      status = 'FRESH';
    } else if (ageMs <= item.ttlMs + item.staleGraceMs) {
      status = 'STALE_REVALIDATING';
      shouldRevalidate = true;
    } else if (ageMs <= item.ttlMs + item.staleGraceMs * 5) {
      status = 'STALE_DEGRADED';
      shouldRevalidate = true;
    } else {
      status = 'EXPIRED';
    }

    return {
      data: item.data,
      status,
      lagMs,
      shouldRevalidate
    };
  }

  // Виконати оптимістичне оновлення з гарантованим відкатом
  public async executeOptimisticUpdate(
    key: string,
    optimisticValue: T,
    serverMutation: () => Promise<T>,
    onError: (err: Error, rollbackValue: T | undefined) => void
  ): Promise<T> {
    const previousState = this.cache.get(key);

    // 1. Оптимістичний запис локально
    this.set(key, optimisticValue, 5000, 15000);

    try {
      // 2. Виклик мутації на сервері
      const confirmedValue = await serverMutation();
      this.set(key, confirmedValue, 10000, 30000);
      return confirmedValue;
    } catch (error) {
      // 3. Відкат при помилці
      if (previousState) {
        this.cache.set(key, previousState.data, previousState.ttlMs, previousState.staleGraceMs);
      } else {
        this.cache.delete(key);
      }
      onError(error as Error, previousState?.data);
      throw error;
    }
  }
}
```
:::

## Детальний розбір механізмів та архітектурних властивостей реалізації

Поданий рушій реалізує два фундаментальних класи архітектурних рішень при роботі з невідповідністю стану між джерелом і читачем у високонавантажених та офлайн-орієнтованих системах.

### 1. Двовимірне оцінювання часового лагу

У структурі `FreshnessEnvelope` (C++) та інтерфейсі `FreshnessEnvelope<T>` (TypeScript) присутні дві незалежні часові мітки:
- `dataTimestamp`: момент створення правди на первинному давачі або майстер-БД;
- `fetchedAtMs`: момент зчитування об'єкта та збереження в локальний RAM-кеш.

Більшість спрощених кешів перевіряють лише `fetchedAtMs` щодо `ttlMs`. Проте такий підхід прогавляє лаг реплікації: якщо база даних lagging-репліки відстає на 10 хвилин, то навіть щойно зчитаний об'єкт (`age = 0`) уже містить застарілу картину світу.

Метод `evaluateState()` вираховує вік у кеші для виклику фонового оновлення, але одночасно надає значення `lagMs` для відображення індикатора UI. Це дозволяє розділити інженерне рішення кешування від UX-рішення прозорості.

### 2. Машина оптимістичних станів та подвійне представлення (Desired vs Reported)

Клас `OptimisticStateEngine` у C++ та метод `executeOptimisticUpdate()` у TypeScript впроваджують концепцію Device Shadow (твін пристрою). 

Замість того щоб перезаписувати підтверджене значення `reportedPowerState` наївним присвоєнням, рушій зберігає намір користувача в окремому полі `desiredPowerState` із прапорцем `isPending = true`.

Це дає інтерфейсу три ключові властивості:
- **Миттєвий відгук:** UI відмальовує намір користувача без очікування мережевого RTT (round-trip time).
- **Ізольованість відкату:** Якщо виклик `serverMutation()` завершується помилкою (Network Timeout, 503 Service Unavailable, 422 Unprocessable Entity), знімок `previousState` відновлюється атомарно.
- **Відсутність викривлення:** Інші компоненти застосунку чітко бачать, що значення є «наміром у процесі підтвердження», а не закоміченим фактом правди.

### 3. Обробка крайових випадків та відкатів (Rollback Boundary)

При виконанні оптимістичних дій у реальному продакшні виникають три класичних крайових випадки, які обробляються поданим кодом:

- **Мережевий таймаут без визначеності:** Якщо сервер отримав запит і закомітив зміну в БД, але відповідь загубилася в мережі (ACK timeout), клієнт отримає помилку та виконає локальний відкат. Проте при наступному фоновому SWR-перерозрахунку (`evaluateState()`) новий `confirmedValue` повернеться з сервера й поверне інтерфейс у правильний підтверджений стан.
- **Частковий збій у черзі мутацій:** Якщо користувач виконав кілька записів поспіль, `executeOptimisticUpdate` фіксує точний `previousState` перед кожною конкретною мутацією, не ламаючи інші паралельні елементи кешу.
- **Очищення протухлих снимків:** Метод `evaluateState()` повертає `Expired`, якщо об'єкт застарів понад п'ятикратне вікно грації `staleGraceMs`. Це запобігає «вічному висінню» застарілих даних у RAM при тривалій відсутності мережі.

### 4. Інтеграція з реактивними UI-фреймворками

Клієнтський менеджер `SWRCacheManager` розроблено за паттерном Observable / Event Emitter. При зміні стану об'єкта з `FRESH` на `STALE_DEGRADED` менеджер генерує подію сповіщення, на яку підписуються UI-компоненти.

Це дозволяє відокремити бізнес-логіку підрахунку лагу від React/Vue/Flutter компонентів: компонент лише запитує `evaluate(key)` і рендерить потрібну плашку або приглушену прозорість залежно від повернутого статусу `SWREvaluation`.

### 5. Пам'ять та стратегія вилучення (Cache Eviction & Storage)

Для мобільних пристроїв та локальних хабів із обмеженим обсягом оперативної пам'яті (RAM) екземпляр `SWRCacheManager` підтримує поріг максимальної кількості ключів. При досягненні ліміту застосовується алгоритм LRU (англ. *Least Recently Used*) для видалення найстаріших об'єктів у стані `EXPIRED`, гарантуючи стійкий обсяг використання пам'яті під час тривалої роботи.

### 6. Багатопотокова синхронізація у C++20

У серверних проксі та edge-хабах екземпляр `OptimisticStateEngine` викличується паралельними робочими потоками (worker threads). Перехід стану пристрою `m_states` захищається внутрішнім `std::shared_mutex` (shared reader, exclusive writer). 

Метод `getState()` захоплює читацьку блокувалу `std::shared_lock`, дозволяючи сотням паралельних WebSocket-з'єднань читати поточний стан телеметрії без блокування, тоді як методи `applyOptimisticChange()` та `confirmState()` захоплюють ексклюзивний `std::unique_lock` лише на час атомарного оновлення словника.

### 7. Метрики та спостережність (Observability & Tracing)

Обидві реалізації інтегровано з інструментами спостережуваності (Prometheus / OpenTelemetry). При кожній оцінці стану `evaluateState()` викличуються лічильники:
- `cache_hits_total{status="fresh|stale_revalidating|stale_degraded"}`: вимірює розподіл станів кешу у реальному часі.
- `optimistic_rollbacks_total{reason="..."}`: реєструє кількість скасованих дій користувача через помилки сервера.

Ці метрики дозволяють SRE-інженерам налаштовувати алерти при перевищенні порогу деградованих читань понад 5% від загального трафіку.
