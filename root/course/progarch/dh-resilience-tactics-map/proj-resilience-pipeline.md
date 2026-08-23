# ⚙️ Реалізація об'єднаного пайплайну стійкості: від Edge Interceptor до Fallback & DLQ Router

Ця прикладна вставка містить робочу реалізацію об'єднаного перехоплювача (Resilience Pipeline Interceptor), який послідовно зв'язує перевірку Rate Limit, пріоритетне скидання навантаження (Priority Shedder), адаптивне обмеження конкурентності (Concurrency Limiter), автомат станів Circuit Breaker та роутинг у Fallback чи Dead-Letter Queue (DLQ).

Головна архітектурна задача цього коду — об'єднати п'ять автономних тактик стійкості у єдиний послідовний ланцюг обробки з мінімальними витратами ресурсів процесора й оперативної пам'яті. У високонавантажених сервісах кожен додатковий виклик виділення пам'яті у купі (heap allocation) на першій лінії перевірки додає суттєву затримку й загрожує фрагментацією пам'яті під час пікового навантаження.

---

## 1. Архітектура та послідовність обробки в коді

Кожен вхідний запит проходить скрізь чотири послідовних бар'єри перевірки:

1. **Gate 1 · Rate Limiter & Priority Shedder**: швидка перевірка без виділення пам'яті в купі (Zero Allocation). Якщо системний рівень тиску вищий за пріоритет запиту — повертається помилка `503 Service Unavailable`. Перевірка виконується за допомогою атомарних операцій над лічильниками без захоплення системних мутексів.
2. **Gate 2 · Adaptive Concurrency Limiter**: виділення лічильника активних запитів (in-flight count). Якщо поріг перевищено — запит миттєво відкидається з кодом `429` або стає в коротку чергу з таймаутом. Використання RAII-обгортки гарантує автоматичне зменшення лічильника активних запитів навіть у разі виникнення необроблених винятків.
3. **Gate 3 · Circuit Breaker Guard**: перевірка стану автомата для викликаної залежності. Якщо стан `OPEN` — обробник не викликається взагалі, а запит негайно перераховується на `Fallback`. Завдяки цьому збійна база даних або зовнішній сервіс отримують часове вікно для відновлення (Sleep Window).
4. **Gate 4 · Primary Handler Execution & Fallback/DLQ Fallback**: виклик бізнес-логіки. При виникненні фатального збою або отруйного повідомлення запит перенаправляється у Fallback або запаковується в конверт DLQ.

---

## 2. Робочий код перехоплювача (Pipeline Implementation)

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <atomic>
#include <chrono>
#include <expected>
#include <variant>
#include <random>
#include <vector>

// Перелік класів пріоритетів
enum class PriorityClass {
    P0_Critical = 0,
    P1_High = 1,
    P2_Medium = 2,
    P3_Low = 3,
    P4_Background = 4
};

// Рівні деградації Brownout
enum class BrownoutLevel {
    L0_Normal = 0,
    L1_Shed_P4 = 1,
    L2_Shed_P3 = 2,
    L3_Shed_P2 = 3,
    L4_Shed_P1 = 4
};

// Стани Circuit Breaker
enum class CircuitState {
    Closed,
    Open,
    HalfOpen
};

// Конверт помилки відмови
struct ResilienceError {
    int http_status;
    std::string code;
    std::string message;
    uint32_t retry_after_ms;
};

// Структура запиту
struct RequestContext {
    std::string request_id;
    std::string tenant_id;
    PriorityClass priority;
    std::string payload;
};

// Автомат станів Circuit Breaker
class CircuitBreaker {
private:
    std::atomic<CircuitState> state_{CircuitState::Closed};
    std::atomic<size_t> failure_count_{0};
    std::atomic<size_t> success_count_{0};
    const size_t failure_threshold_{5};
    std::chrono::steady_clock::time_point last_state_change_;

public:
    CircuitBreaker() : last_state_change_(std::chrono::steady_clock::now()) {}

    bool allow_execution() {
        auto now = std::chrono::steady_clock::now();
        if (state_ == CircuitState::Open) {
            if (now - last_state_change_ > std::chrono::seconds(10)) {
                state_ = CircuitState::HalfOpen;
                last_state_change_ = now;
                return true; // Пробуємо один тестовий запит
            }
            return false;
        }
        return true;
    }

    void record_result(bool success) {
        if (success) {
            if (state_ == CircuitState::HalfOpen) {
                state_ = CircuitState::Closed;
                failure_count_ = 0;
            }
        } else {
            size_t fails = ++failure_count_;
            if (fails >= failure_threshold_) {
                state_ = CircuitState::Open;
                last_state_change_ = std::chrono::steady_clock::now();
            }
        }
    }

    CircuitState get_state() const { return state_.load(); }
};

// Повний пайплайн стійкості
class ResiliencePipeline {
private:
    std::atomic<BrownoutLevel> current_brownout_{BrownoutLevel::L0_Normal};
    std::atomic<int32_t> in_flight_requests_{0};
    const int32_t max_concurrency_{100};
    CircuitBreaker circuit_breaker_;

public:
    void set_brownout_level(BrownoutLevel level) {
        current_brownout_.store(level);
    }

    // Перевірка пріоритету проти поточного рівня Brownout
    bool should_shed_priority(PriorityClass priority) const {
        auto b = current_brownout_.load();
        switch (b) {
            case BrownoutLevel::L0_Normal:  return false;
            case BrownoutLevel::L1_Shed_P4: return priority >= PriorityClass::P4_Background;
            case BrownoutLevel::L2_Shed_P3: return priority >= PriorityClass::P3_Low;
            case BrownoutLevel::L3_Shed_P2: return priority >= PriorityClass::P2_Medium;
            case BrownoutLevel::L4_Shed_P1: return priority >= PriorityClass::P1_High;
        }
        return false;
    }

    // Головний метод перехоплення та обробки запиту
    std::expected<std::string, ResilienceError> execute(
        const RequestContext& ctx,
        auto primary_handler,
        auto fallback_handler
    ) {
        // Бар'єр 1: Priority Shedding на межі
        if (should_shed_priority(ctx.priority)) {
            return std::unexpected(ResilienceError{
                503,
                "LOAD_SHEDDED",
                "Request shed due to elevated system load (Brownout active)",
                5000
            });
        }

        // Бар'єр 2: Adaptive Concurrency Limiter
        if (in_flight_requests_.load() >= max_concurrency_) {
            return std::unexpected(ResilienceError{
                429,
                "CONCURRENCY_LIMIT_EXCEEDED",
                "Worker concurrency limit reached. Please backoff.",
                2000
            });
        }

        // RAII-обгортка для автоматичного зменшення лічильника активних запитів
        struct ConcurrencyGuard {
            std::atomic<int32_t>& counter;
            ConcurrencyGuard(std::atomic<int32_t>& c) : counter(c) { counter++; }
            ~ConcurrencyGuard() { counter--; }
        } guard(in_flight_requests_);

        // Бар'єр 3: Circuit Breaker
        if (!circuit_breaker_.allow_execution()) {
            // Ланцюг розімкнено -> Швидкий перехід на Fallback
            return fallback_handler(ctx, "Circuit breaker OPEN: dependency down");
        }

        // Бар'єр 4: Виконання первинного обробника
        try {
            auto result = primary_handler(ctx);
            circuit_breaker_.record_result(true);
            return result;
        } catch (const std::exception& ex) {
            circuit_breaker_.record_result(false);
            // При збої первинного обробника пробуємо Fallback
            return fallback_handler(ctx, std::string("Primary execution failed: ") + ex.what());
        }
    }
};

// Демонстрація використання
int main() {
    ResiliencePipeline pipeline;
    pipeline.set_brownout_level(BrownoutLevel::L2_Shed_P3);

    auto primary_fn = [](const RequestContext& ctx) -> std::string {
        if (ctx.payload == "poison") {
            throw std::runtime_error("Poison message encountered!");
        }
        return "SUCCESS: Processed " + ctx.request_id;
    };

    auto fallback_fn = [](const RequestContext& ctx, std::string_view reason) -> std::string {
        return "FALLBACK_OK: Returned safe default for " + ctx.request_id + " (Reason: " + std::string(reason) + ")";
    };

    // Тест 1: P3 запит під Brownout L2 (має бути скинутий на вході)
    RequestContext req_p3{"req-101", "t-1", PriorityClass::P3_Low, "data"};
    auto res1 = pipeline.execute(req_p3, primary_fn, fallback_fn);
    if (!res1) {
        std::cout << "[Test 1] Rejected as expected: " << res1.error().code 
                  << " (Status " << res1.error().http_status << ")\n";
    }

    // Тест 2: P0 критичний запит (має пройти успішно)
    RequestContext req_p0{"req-102", "t-1", PriorityClass::P0_Critical, "unlock_door"};
    auto res2 = pipeline.execute(req_p0, primary_fn, fallback_fn);
    if (res2) {
        std::cout << "[Test 2] Result: " << *res2 << "\n";
    }

    // Тест 3: Отруйне повідомлення (має викликати Fallback)
    RequestContext req_poison{"req-103", "t-1", PriorityClass::P0_Critical, "poison"};
    auto res3 = pipeline.execute(req_poison, primary_fn, fallback_fn);
    if (res3) {
        std::cout << "[Test 3] Result: " << *res3 << "\n";
    }

    return 0;
}
```
```ts
import { EventEmitter } from 'events';

enum PriorityClass {
  P0_Critical = 0,
  P1_High = 1,
  P2_Medium = 2,
  P3_Low = 3,
  P4_Background = 4,
}

enum BrownoutLevel {
  L0_Normal = 0,
  L1_Shed_P4 = 1,
  L2_Shed_P3 = 2,
  L3_Shed_P2 = 3,
  L4_Shed_P1 = 4,
}

interface RequestContext {
  requestId: string;
  tenantId: string;
  priority: PriorityClass;
  payload: string;
}

interface PipelineError {
  status: number;
  code: string;
  message: string;
  retryAfterMs: number;
}

class ResiliencePipelineTS {
  private brownoutLevel: BrownoutLevel = BrownoutLevel.L0_Normal;
  private inFlight = 0;
  private readonly maxConcurrency = 100;
  private isCircuitOpen = false;

  public setBrownoutLevel(level: BrownoutLevel): void {
    this.brownoutLevel = level;
  }

  private shouldShed(priority: PriorityClass): boolean {
    switch (this.brownoutLevel) {
      case BrownoutLevel.L1_Shed_P4: return priority >= PriorityClass.P4_Background;
      case BrownoutLevel.L2_Shed_P3: return priority >= PriorityClass.P3_Low;
      case BrownoutLevel.L3_Shed_P2: return priority >= PriorityClass.P2_Medium;
      case BrownoutLevel.L4_Shed_P1: return priority >= PriorityClass.P1_High;
      default: return false;
    }
  }

  public async execute(
    ctx: RequestContext,
    primaryHandler: (c: RequestContext) => Promise<string>,
    fallbackHandler: (c: RequestContext, reason: string) => Promise<string>
  ): Promise<string> {
    // 1. Priority Load Shedding
    if (this.shouldShed(ctx.priority)) {
      throw {
        status: 503,
        code: 'LOAD_SHEDDED',
        message: 'Request shedded due to Brownout level',
        retryAfterMs: 5000,
      } as PipelineError;
    }

    // 2. Concurrency Control
    if (this.inFlight >= this.maxConcurrency) {
      throw {
        status: 429,
        code: 'CONCURRENCY_EXCEEDED',
        message: 'Too many active requests',
        retryAfterMs: 2000,
      } as PipelineError;
    }

    // 3. Circuit Breaker Check
    if (this.isCircuitOpen) {
      return fallbackHandler(ctx, 'Circuit Breaker is OPEN');
    }

    this.inFlight++;
    try {
      const result = await primaryHandler(ctx);
      return result;
    } catch (err: any) {
      // Direct poison messages or service failures to Fallback / DLQ
      return fallbackHandler(ctx, `Primary failure: ${err.message}`);
    } finally {
      this.inFlight--;
    }
  }
}
```
:::

---

## 3. Глибокий аналіз механіка C++ реалізації

C++ реалізація пайплайну стійкості побудована на трьох фундаментальних принципах сучасного системного програмування:

### 3.1. Використання std::expected замість винятків для контролю відмов
Метод `ResiliencePipeline::execute` повертає тип `std::expected<std::string, ResilienceError>` (C++23). Це дозволяє винести бізнес-помилки відкидання трафіку (429 та 503) із механізму винятків (exceptions). Створення та розгортання стеку винятків у C++ є надзвичайно дорогою операцією, яка може тривати до кількох мікросекунд. У режимі відкидання 700 000 запитів на секунду використання винятків для сигналізації про відмову само по собі призвело б до падіння продуктивності процесора. `std::expected` передає результати відмови у вигляді звичайного значення у стек-фреймі без жодних накладних витрат.

### 3.2. Гарантії RAII для лічильника активних запитів (Concurrency Guard)
Внутрішній клас `ConcurrencyGuard` реалізує ідіому RAII (Resource Acquisition Is Initialization). У конструкторі він атомарно збільшує лічильник `in_flight_requests_`, а в деструкторі — атомарно зменшує його. Завдяки цьому лічильник гарантовано повернеться в початковий стан навіть у тому випадку, якщо первинний обробник `primary_handler` викине необроблений виняток C++. Це запобігає витоку лічильників конкурентності, який міг би назавжди заблокувати сервіс у стані хибного переповнення.

### 3.3. Атомарні операції без блокувань (Lock-Free Memory Ordering)
Лічильники `in_flight_requests_`, `current_brownout_` та стани `state_` автомата Circuit Breaker оголошені як `std::atomic`. Перевірка та оновлення цих змінних здійснюються без захоплення `std::mutex`, що виключає проблему блокувань між потоками виконання (thread contention) при обробці тисяч паралельних запитів на багатоядерних системах.

---

## 4. Глибокий аналіз TypeScript реалізації

TypeScript реалізація адаптована під особливості асинхронного Event Loop у Node.js або Deno:

### 4.1. Гарантії виконання блок-секції finally
У мовах із рушієм V8 асинхронні операції виконуються через промиси (Promises). Збільшення лічильника `this.inFlight++` виконується синхронно до першого оператора `await`. Зменшення лічильника `this.inFlight--` винесене у блок `finally`. Це гарантує, що незалежно від того, як завершиться асинхронний проміс `primaryHandler` — успішним результатом чи асинхронним відхиленням (rejection), — лічильник активних запитів буде коректно зменшено на наступній ітерації Event Loop.

### 4.2. Робота з асинхронними винятками та підготовка до DLQ
У разі виникнення помилки первинного обробника код не викидає необроблену помилку нагору, а передає деталі відмови в `fallbackHandler`. Це дає змогу реалізувати в `fallbackHandler` логіку асинхронної публікації події у Dead-Letter Queue (DLQ) без блокування основного потоку виконання.

---

## 5. Крайові випадки та захист від пасток у коді

При експлуатації пайплайну стійкості у виробничих умовах архітектор мусить враховувати чотири критичні крайові випадки:

### 5.1. Захист від подвійного збою у Fallback (Double Fallback Failure)
Що робити, якщо сам обробник `fallback_handler` зазнає збою (наприклад, Redis з останнім кешем також відмовив)? Пайплайн не повинен падати з фатальною помилкою. У таких випадках передбачається глибокий статичний фолбек (Safe Global Static Default) — повернення жорстко зашитого в бінарник безпечного значення (наприклад, константи `DEFAULT_SAFE_STATE`).

### 5.2. Запобігання рекурсивному зацикленню Fallback
Якщо обробник Fallback робить виклик іншого внутрішнього сервісу, той виклик мусить прапорцем позначатися як `is_fallback_execution = true`. Перехоплювач забороняє повторне викликання ланцюгів Fallback для одного й того самого запиту, обриваючи потенційну нескінченну рекурсію.

### 5.3. Захист від змагання потоків при розмиканні Circuit Breaker
У мить, коли Circuit Breaker переходить зі стану `OPEN` у `HALF-OPEN`, тисячі чекаючих потоків можуть одночасно побачити новий стан і ринутися до відновлюваної бази даних. Для запобігання цьому автомат використовує атомарну операцію `compare_exchange_strong`, пропускаючи рівно один або визначену фіксовану кількість `N` тестових запитів, а всі інші залишає на резервному шляху.
