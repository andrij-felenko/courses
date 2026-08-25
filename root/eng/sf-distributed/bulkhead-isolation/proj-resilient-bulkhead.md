# ⚙️ Реалізація перебірки: семафорний та пуловий захист ресурсів

Розглянемо практичну реалізацію перебірки для високопродуктивного сервера. Програмний компонент повинен забезпечувати надійне обмеження одночасних викликів до зовнішнього сервісу (або бази даних), захищати від витоку дескрипторів та блокувань під час винятків, підтримувати швидке відхилення запитів (англ. *fast rejection*) та надавати телеметрію використання активних слотів.

## Архітектура рішення

Компонент реалізує комбіновану модель **семафорної перебірки з можливістю черги очікування та детермінованим звільненням ресурсів за патерном RAII (англ. *Resource Acquisition Is Initialization*)**.

Головні вимоги до реалізації:
1. **Атомарний облік дозволів:** захист від гонитви даних без важких глобальних блокувань на гарячому шляху.
2. **RAII-охоронник дозволу (`PermitGuard`):** дозвіл гарантовано повертається в семафор під час виходу з області видимості, зокрема у разі виникнення винятків, паніки або передчасного завершення функції.
3. **Обмежений час очікування (Try-Acquire з таймаутом):** якщо всі слоти зайняті, вхідний потік може почекати не більше заданого інтервалу (наприклад, 10 мс) перед остаточним відхиленням.
4. **Статистика та метрики:** фіксація поточного завантаження, кількості успішних захоплень та кількості відхилень для системи моніторингу.

## Реалізація перебірки

:::tabs
```cpp
#include <iostream>
#include <chrono>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <optional>
#include <functional>
#include <expected>
#include <string_view>

namespace resilience {

enum class BulkheadError {
    CapacityExceeded,
    TimeoutWaitingForSlot,
    CircuitBroken
};

class Bulkhead {
public:
    struct Metrics {
        std::size_t available_permits;
        std::size_t max_permits;
        uint64_t total_acquired;
        uint64_t total_rejected;
    };

    class PermitGuard {
    public:
        PermitGuard(Bulkhead& parent) noexcept : parent_(&parent) {}
        
        ~PermitGuard() noexcept {
            if (parent_ != nullptr) {
                parent_->release();
            }
        }

        PermitGuard(const PermitGuard&) = delete;
        PermitGuard& operator=(const PermitGuard&) = delete;

        PermitGuard(PermitGuard&& other) noexcept : parent_(other.parent_) {
            other.parent_ = nullptr;
        }

        PermitGuard& operator=(PermitGuard&& other) noexcept {
            if (this != &other) {
                if (parent_ != nullptr) {
                    parent_->release();
                }
                parent_ = other.parent_;
                other.parent_ = nullptr;
            }
            return *this;
        }

    private:
        Bulkhead* parent_{nullptr};
    };

    Bulkhead(std::string_view name, std::size_t max_concurrent_calls, 
             std::chrono::milliseconds max_wait_duration = std::chrono::milliseconds(0))
        : name_(name),
          max_permits_(max_concurrent_calls),
          available_permits_(max_concurrent_calls),
          max_wait_duration_(max_wait_duration),
          total_acquired_(0),
          total_rejected_(0) {}

    ~Bulkhead() = default;

    std::expected<PermitGuard, BulkheadError> try_acquire() {
        if (max_wait_duration_.count() == 0) {
            // Швидка спроба без очікування
            std::unique_lock<std::mutex> lock(mutex_);
            if (available_permits_ > 0) {
                --available_permits_;
                total_acquired_.fetch_add(1, std::memory_order_relaxed);
                return PermitGuard(*this);
            }
            total_rejected_.fetch_add(1, std::memory_order_relaxed);
            return std::unexpected(BulkheadError::CapacityExceeded);
        }

        // Спроба з очікуванням у межах бюджету часу
        std::unique_lock<std::mutex> lock(mutex_);
        if (available_permits_ == 0) {
            auto status = cv_.wait_for(lock, max_wait_duration_, [this]() {
                return available_permits_ > 0;
            });
            if (!status) {
                total_rejected_.fetch_add(1, std::memory_order_relaxed);
                return std::unexpected(BulkheadError::TimeoutWaitingForSlot);
            }
        }

        --available_permits_;
        total_acquired_.fetch_add(1, std::memory_order_relaxed);
        return PermitGuard(*this);
    }

    template <typename Func, typename Fallback>
    auto execute(Func&& action, Fallback&& fallback) 
        -> std::invoke_result_t<Func> {
        auto permit = try_acquire();
        if (permit.has_value()) {
            return std::forward<Func>(action)();
        }
        return std::forward<Fallback>(fallback)(permit.error());
    }

    Metrics get_metrics() const noexcept {
        std::unique_lock<std::mutex> lock(mutex_);
        return Metrics{
            available_permits_,
            max_permits_,
            total_acquired_.load(std::memory_order_relaxed),
            total_rejected_.load(std::memory_order_relaxed)
        };
    }

private:
    void release() noexcept {
        {
            std::unique_lock<std::mutex> lock(mutex_);
            if (available_permits_ < max_permits_) {
                ++available_permits_;
            }
        }
        cv_.notify_one();
    }

    std::string name_;
    const std::size_t max_permits_;
    std::size_t available_permits_;
    const std::chrono::milliseconds max_wait_duration_;
    mutable std::mutex mutex_;
    std::condition_variable cv_;
    std::atomic<uint64_t> total_acquired_;
    std::atomic<uint64_t> total_rejected_;
};

} // namespace resilience
```
```go
package resilience

import (
	"context"
	"errors"
	"sync/atomic"
	"time"
)

var (
	ErrBulkheadFull    = errors.New("bulkhead capacity exceeded")
	ErrBulkheadTimeout = errors.New("bulkhead acquisition timeout")
)

type Metrics struct {
	AvailablePermits int64
	MaxPermits       int64
	TotalAcquired    uint64
	TotalRejected    uint64
}

type Bulkhead struct {
	name            string
	maxPermits      int64
	semaphore       chan struct{}
	maxWaitDuration time.Duration
	totalAcquired   uint64
	totalRejected   uint64
}

type Permit struct {
	bulkhead *Bulkhead
	released uint32
}

func (p *Permit) Release() {
	if atomic.CompareAndSwapUint32(&p.released, 0, 1) {
		<-p.bulkhead.semaphore
	}
}

func NewBulkhead(name string, maxConcurrentCalls int, maxWait time.Duration) *Bulkhead {
	return &Bulkhead{
		name:            name,
		maxPermits:      int64(maxConcurrentCalls),
		semaphore:       make(chan struct{}, maxConcurrentCalls),
		maxWaitDuration: maxWait,
	}
}

func (b *Bulkhead) Acquire(ctx context.Context) (*Permit, error) {
	if b.maxWaitDuration <= 0 {
		select {
		case b.semaphore <- struct{}{}:
			atomic.AddUint64(&b.totalAcquired, 1)
			return &Permit{bulkhead: b}, nil
		default:
			atomic.AddUint64(&b.totalRejected, 1)
			return nil, ErrBulkheadFull
		}
	}

	timer := time.NewTimer(b.maxWaitDuration)
	defer timer.Stop()

	select {
	case b.semaphore <- struct{}{}:
		atomic.AddUint64(&b.totalAcquired, 1)
		return &Permit{bulkhead: b}, nil
	case <-timer.C:
		atomic.AddUint64(&b.totalRejected, 1)
		return nil, ErrBulkheadTimeout
	case <-ctx.Done():
		atomic.AddUint64(&b.totalRejected, 1)
		return nil, ctx.Err()
	}
}

func (b *Bulkhead) Execute(ctx context.Context, action func() error, fallback func(err error) error) error {
	permit, err := b.Acquire(ctx)
	if err != nil {
		if fallback != nil {
			return fallback(err)
		}
		return err
	}
	defer permit.Release()

	return action()
}

func (b *Bulkhead) GetMetrics() Metrics {
	currentInFlight := int64(len(b.semaphore))
	return Metrics{
		AvailablePermits: b.maxPermits - currentInFlight,
		MaxPermits:       b.maxPermits,
		TotalAcquired:    atomic.LoadUint64(&b.totalAcquired),
		TotalRejected:    atomic.LoadUint64(&b.totalRejected),
	}
}
```
:::

## Детальний аналіз реалізації та інваріанти конкурентності

Реалізація перебірки вимагає дотримання суворих інваріантів безпеки пам'яті та коректної синхронізації між багатьма потоками обробки.

### 1. Гарантії RAII та захист від витоку слотів (PermitGuard)

Найкритичнішим дефектом наївних реалізацій семафорних перебірок є витік дозволів (англ. *permit leak*). Якщо розробник захоплює дозвіл викликом `bulkhead.acquire()` і розраховує викликати `bulkhead.release()` наприкінці функції, будь-який неперехоплений виняток, ранній вихід за умовою `if (...) return;` або паніка (у Go) призводить до того, що лічильник вільних слотів ніколи не повертається до початкового стану. Після певної кількості таких подій перебірка назавжди блокується у стані вичерпання ресурсів.

Для розв'язання цієї проблеми в C++ реалізовано клас-охоронник `PermitGuard` із використанням ідіоми RAII:
- Конструктор копіювання та оператор присвоєння копіюванням видалені (`= delete`), що виключає можливість випадкового подвоєння дозволу при передачі за значенням.
- Реалізовано семантику переміщення (англ. *move semantics*): при переміщенні об'єкта `PermitGuard` володіння дозволом переходить до нового екземпляра, а у старого вказівник `parent_` скидається в `nullptr`.
- Деструктор `~PermitGuard()` перевіряє `parent_ != nullptr` і гарантовано викликає приватний метод `release()`. Деструктор позначено специфікатором `noexcept`, оскільки звільнення ресурсу ні за яких умов не повинно генерувати вторинних винятків під час розкручування стека (англ. *stack unwinding*).

У Go аналогічний інваріант досягається через `atomic.CompareAndSwapUint32(&p.released, 0, 1)`, що гарантує рівно одноразове вичитування з каналу `<-p.bulkhead.semaphore`, навіть якщо метод `Release()` викликається багаторазово або конкурентно з різних горутин.

### 2. Модель пам'яті та оптимізація лічильників телеметрії

Операції над лічильниками загальної кількості успішних захоплень `total_acquired_` та відхилень `total_rejected_` виконуються з упорядкуванням пам'яті `std::memory_order_relaxed` (у C++) та через пакет `sync/atomic` (у Go).

Оскільки ці лічильники використовуються виключно для телеметрії та моніторингу, вони не керують порядком виконання критичних секцій програми і не вимагають дорогих бар'єрів пам'яті `acquire-release` чи повної послідовної узгодженості `std::memory_order_seq_cst`. Це усуває зайве скидання конвеєра інструкцій процесора на гарячому шляху виконання викликів.

### 3. Синхронізація очікування та запобігання хибним пробудженням

У гілці з ненульовим часом очікування `max_wait_duration_ > 0` метод `try_acquire()` використовує умовну змінну `std::condition_variable::wait_for()`.

Предикат `[this]() { return available_permits_ > 0; }` передається безпосередньо у виклик `wait_for`. Це захищає систему від **хибних пробуджень (англ. *spurious wakeups*)**, коли потік операційної системи прокидається сигналом ядра за відсутності реального виклику `notify_one()`. Доки умова предикату не стане істинною або не спливе таймер, потік повертається у стан сну.

### 4. Неблокуюче скидання через Go-канали

У реалізації мовою Go для семафора використовується буферизований канал `chan struct{}` фіксованої місткості `maxConcurrentCalls`:
- Спроба захоплення слота реалізована через оператор `select` із неблокуючою гілкою `default`. Якщо буфер каналу заповнений, запис `b.semaphore <- struct{}{}` не може виконатися негайно, керування миттєво переходить у гілку `default`, повертаючи помилку `ErrBulkheadFull` за лічені наносекунди без створення черг у пам'яті.
- Якщо налаштовано час очікування `maxWaitDuration`, оператор `select` мультиплексує три канали: успішний запис у семафор, спрацьовування таймера `timer.C` та скасування контексту `ctx.Done()`. Це забезпечує наскрізну підтримку клієнтських дедлайнів.

## Інженерні пастки та правила використання

Під час впровадження перебірок у виробничих сервісах важливо уникати таких типових помилок:

1. **Небезпека ручного виклику `release()`:** якщо звільнення дозволу семафора не прив'язане до деструктора (RAII у C++) або відкладеного виклику (`defer permit.Release()` у Go), будь-який необроблений виняток чи достроковий `return` призведе до постійного витоку дозволів. Через кілька годин лічильник вільних слотів досягне нуля, і перебірка заблокується назавжди.

2. **Використання політики `CallerRuns` у неблокуючих серверах:** якщо черга пулу потоків переповнюється, і система застосовує стандартну політику `CallerRunsPolicy`, викликаючий потік (наприклад, потік циклу подій Netty або Epoll-акцептор) починає виконувати важкий повільний запит самостійно. Це миттєво паралізує прийом нових TCP-з'єднань на всьому сервері, знищуючи саму ідею ізоляції.

3. **Гонтва закриття сокетів та вичерпання пулу горутин:** коли запит відхиляється перебіркою за таймаутом очікування слота, HTTP-клієнт повинен отримати статус `429 Too Many Requests` негайно, а не тримати відкритим з'єднання з браузером. У разі асинхронного клієнта відхилений запит повинен негайно скасовувати свій контекст `context.WithCancel()`, сигналізуючи віддаленому сокету про припинення читання.

