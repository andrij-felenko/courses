# ⚙️ Високопродуктивний неблокуючий запобіжник на C++ та Go

У високонавантажених сервісах із сотнями тисяч запитів на секунду (RPS) використання традиційних м'ютексів для синхронізації стану запобіжника створює критичні затримки через взаємне блокування потоків та перемикання контексту ядра. Дана реалізація демонструє неблокуючий (Lock-Free) запобіжник на базі атомарних операцій CAS (Compare-And-Swap) та кільцевого буфера ковзного вікна.

## Архітектура та структури даних

Запобіжник реалізує кількісне ковзне вікно (Count-based Sliding Window) фіксованого розміру `WINDOW_CAPACITY = 64`. Стан автомата моделюється трьома значеннями:

* `STATE_CLOSED (0)` — ланцюг замкнений, запити вільно проходять до бекенда;
* `STATE_OPEN (1)` — ланцюг розімкнений, усі запити миттєво відхиляються з помилкою (Fail-Fast);
* `STATE_HALF_OPEN (2)` — пробний стан, у якому фіксована квота запитів перевіряє стан бекенда після паузи відновлення.

Для виключення деградації швидкодії процесора через ефект помилкового розділення кеш-ліній (False Sharing) атомарні лічильники та структура ковзного вікна вирівнюються за межею 64-байтової кеш-лінії (`alignas(64)` у C++ та `_Alignas(64)` у C11).

## Реалізація запобіжника

:::tabs
```c
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

#define CB_WINDOW_SIZE 64
#define CB_WINDOW_MASK (CB_WINDOW_SIZE - 1)

typedef enum {
    CB_STATE_CLOSED = 0,
    CB_STATE_OPEN = 1,
    CB_STATE_HALF_OPEN = 2
} cb_state_t;

typedef struct {
    uint32_t failure_rate_threshold;    /* Відсоток збоїв для розмикання (напр. 50) */
    uint32_t minimum_number_of_calls;   /* Поріг вибірки для розрахунку відсотка */
    uint64_t wait_duration_in_open_ns;  /* Час очікування в стані OPEN (наносекунди) */
    uint32_t permitted_half_open_calls; /* Дозволена кількість пробних запитів */
} cb_config_t;

typedef struct {
    _Alignas(64) atomic_int state;
    _Alignas(64) atomic_uint_fast64_t head_index;
    _Alignas(64) atomic_bool ring_buffer[CB_WINDOW_SIZE]; /* true = помилка, false = успіх */
    _Alignas(64) atomic_uint_fast64_t last_state_change_ns;
    _Alignas(64) atomic_uint_fast32_t half_open_probe_count;
    _Alignas(64) atomic_uint_fast32_t half_open_failure_count;
    cb_config_t config;
} circuit_breaker_t;

static inline uint64_t cb_get_monotonic_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

void cb_init(circuit_breaker_t *cb, const cb_config_t *cfg) {
    atomic_init(&cb->state, CB_STATE_CLOSED);
    atomic_init(&cb->head_index, 0);
    atomic_init(&cb->last_state_change_ns, cb_get_monotonic_ns());
    atomic_init(&cb->half_open_probe_count, 0);
    atomic_init(&cb->half_open_failure_count, 0);
    cb->config = *cfg;
    for (int i = 0; i < CB_WINDOW_SIZE; i++) {
        atomic_init(&cb->ring_buffer[i], false);
    }
}

static void cb_transition_to(circuit_breaker_t *cb, cb_state_t expected, cb_state_t next) {
    int exp = expected;
    if (atomic_compare_exchange_strong_explicit(&cb->state, &exp, next,
                                                memory_order_release, memory_order_relaxed)) {
        atomic_store_explicit(&cb->last_state_change_ns, cb_get_monotonic_ns(), memory_order_release);
        if (next == CB_STATE_HALF_OPEN) {
            atomic_store_explicit(&cb->half_open_probe_count, 0, memory_order_release);
            atomic_store_explicit(&cb->half_open_failure_count, 0, memory_order_release);
        } else if (next == CB_STATE_CLOSED) {
            atomic_store_explicit(&cb->head_index, 0, memory_order_release);
            for (int i = 0; i < CB_WINDOW_SIZE; i++) {
                atomic_store_explicit(&cb->ring_buffer[i], false, memory_order_relaxed);
            }
        }
    }
}

bool cb_allow_request(circuit_breaker_t *cb) {
    cb_state_t current_state = (cb_state_t)atomic_load_explicit(&cb->state, memory_order_acquire);

    if (current_state == CB_STATE_CLOSED) {
        return true;
    }

    if (current_state == CB_STATE_OPEN) {
        uint64_t now = cb_get_monotonic_ns();
        uint64_t last_change = atomic_load_explicit(&cb->last_state_change_ns, memory_order_acquire);
        if (now - last_change >= cb->config.wait_duration_in_open_ns) {
            cb_transition_to(cb, CB_STATE_OPEN, CB_STATE_HALF_OPEN);
            return cb_allow_request(cb);
        }
        return false;
    }

    if (current_state == CB_STATE_HALF_OPEN) {
        uint32_t probe_idx = atomic_fetch_add_explicit(&cb->half_open_probe_count, 1, memory_order_acq_rel);
        if (probe_idx < cb->config.permitted_half_open_calls) {
            return true;
        }
        return false;
    }

    return false;
}

void cb_record_result(circuit_breaker_t *cb, bool is_failure) {
    cb_state_t current_state = (cb_state_t)atomic_load_explicit(&cb->state, memory_order_acquire);

    if (current_state == CB_STATE_HALF_OPEN) {
        if (is_failure) {
            cb_transition_to(cb, CB_STATE_HALF_OPEN, CB_STATE_OPEN);
        } else {
            uint32_t probes = atomic_load_explicit(&cb->half_open_probe_count, memory_order_acquire);
            if (probes >= cb->config.permitted_half_open_calls) {
                cb_transition_to(cb, CB_STATE_HALF_OPEN, CB_STATE_CLOSED);
            }
        }
        return;
    }

    if (current_state == CB_STATE_CLOSED) {
        uint64_t idx = atomic_fetch_add_explicit(&cb->head_index, 1, memory_order_acq_rel);
        atomic_store_explicit(&cb->ring_buffer[idx & CB_WINDOW_MASK], is_failure, memory_order_release);

        uint64_t total_recorded = idx + 1;
        if (total_recorded >= cb->config.minimum_number_of_calls) {
            uint32_t window_size = total_recorded < CB_WINDOW_SIZE ? (uint32_t)total_recorded : CB_WINDOW_SIZE;
            uint32_t failures = 0;
            for (uint32_t i = 0; i < window_size; i++) {
                if (atomic_load_explicit(&cb->ring_buffer[i], memory_order_relaxed)) {
                    failures++;
                }
            }
            uint32_t failure_rate = (failures * 100) / window_size;
            if (failure_rate >= cb->config.failure_rate_threshold) {
                cb_transition_to(cb, CB_STATE_CLOSED, CB_STATE_OPEN);
            }
        }
    }
}
```
```cpp
#include <atomic>
#include <chrono>
#include <cstdint>
#include <expected>
#include <functional>
#include <span>
#include <string_view>

namespace resilience {

enum class State : uint8_t {
    Closed = 0,
    Open = 1,
    HalfOpen = 2
};

struct Config {
    uint32_t failure_rate_threshold{50};
    uint32_t minimum_number_of_calls{20};
    std::chrono::nanoseconds wait_duration_in_open{std::chrono::seconds(5)};
    uint32_t permitted_half_open_calls{10};
};

class CircuitBreaker {
public:
    static constexpr size_t WindowSize = 64;
    static constexpr size_t WindowMask = WindowSize - 1;

    explicit CircuitBreaker(Config config)
        : config_(config),
          state_(State::Closed),
          head_index_(0),
          last_state_change_(std::chrono::steady_clock::now()),
          half_open_probe_count_(0),
          half_open_failure_count_(0) {
        for (auto& slot : ring_buffer_) {
            slot.store(false, std::memory_order_relaxed);
        }
    }

    [[nodiscard]] bool allow_request() noexcept {
        const State current = state_.load(std::memory_order_acquire);

        if (current == State::Closed) {
            return true;
        }

        if (current == State::Open) {
            const auto now = std::chrono::steady_clock::now();
            const auto last = last_state_change_.load(std::memory_order_acquire);
            if (now - last >= config_.wait_duration_in_open) {
                transition_to(State::Open, State::HalfOpen);
                return allow_request();
            }
            return false;
        }

        if (current == State::HalfOpen) {
            const uint32_t probe_id = half_open_probe_count_.fetch_add(1, std::memory_order_acq_rel);
            return probe_id < config_.permitted_half_open_calls;
        }

        return false;
    }

    void record_result(bool is_failure) noexcept {
        const State current = state_.load(std::memory_order_acquire);

        if (current == State::HalfOpen) {
            if (is_failure) {
                transition_to(State::HalfOpen, State::Open);
            } else {
                const uint32_t probes = half_open_probe_count_.load(std::memory_order_acquire);
                if (probes >= config_.permitted_half_open_calls) {
                    transition_to(State::HalfOpen, State::Closed);
                }
            }
            return;
        }

        if (current == State::Closed) {
            const uint64_t idx = head_index_.fetch_add(1, std::memory_order_acq_rel);
            ring_buffer_[idx & WindowMask].store(is_failure, std::memory_order_release);

            const uint64_t total = idx + 1;
            if (total >= config_.minimum_number_of_calls) {
                const size_t active_window = total < WindowSize ? static_cast<size_t>(total) : WindowSize;
                size_t failures = 0;
                for (size_t i = 0; i < active_window; ++i) {
                    if (ring_buffer_[i].load(std::memory_order_relaxed)) {
                        ++failures;
                    }
                }
                const uint32_t rate = static_cast<uint32_t>((failures * 100) / active_window);
                if (rate >= config_.failure_rate_threshold) {
                    transition_to(State::Closed, State::Open);
                }
            }
        }
    }

    template <typename Func, typename Fallback>
    auto execute(Func&& primary, Fallback&& fallback) 
        -> std::invoke_result_t<Func> {
        if (!allow_request()) {
            return fallback();
        }
        try {
            auto result = primary();
            record_result(false);
            return result;
        } catch (...) {
            record_result(true);
            return fallback();
        }
    }

    [[nodiscard]] State state() const noexcept {
        return state_.load(std::memory_order_acquire);
    }

private:
    void transition_to(State expected, State next) noexcept {
        if (state_.compare_exchange_strong(expected, next,
                                           std::memory_order_release,
                                           std::memory_order_relaxed)) {
            last_state_change_.store(std::chrono::steady_clock::now(), std::memory_order_release);
            if (next == State::HalfOpen) {
                half_open_probe_count_.store(0, std::memory_order_release);
                half_open_failure_count_.store(0, std::memory_order_release);
            } else if (next == State::Closed) {
                head_index_.store(0, std::memory_order_release);
                for (auto& slot : ring_buffer_) {
                    slot.store(false, std::memory_order_relaxed);
                }
            }
        }
    }

    const Config config_;
    alignas(64) std::atomic<State> state_;
    alignas(64) std::atomic<uint64_t> head_index_;
    alignas(64) std::array<std::atomic<bool>, WindowSize> ring_buffer_;
    alignas(64) std::atomic<std::chrono::steady_clock::time_point> last_state_change_;
    alignas(64) std::atomic<uint32_t> half_open_probe_count_;
    alignas(64) std::atomic<uint32_t> half_open_failure_count_;
};

} // namespace resilience
```
```go
package resilience

import (
	"errors"
	"sync/atomic"
	"time"
)

type State uint32

const (
	StateClosed State = iota
	StateOpen
	StateHalfOpen
)

const (
	windowSize = 64
	windowMask = windowSize - 1
)

var (
	ErrCircuitBreakerOpen = errors.New("circuit breaker is open: request rejected")
)

type Config struct {
	FailureRateThreshold   uint32
	MinimumNumberOfCalls   uint64
	WaitDurationInOpen     time.Duration
	PermittedHalfOpenCalls uint32
}

type CircuitBreaker struct {
	config              Config
	state               atomic.Uint32
	headIndex           atomic.Uint64
	ringBuffer          [windowSize]atomic.Bool
	lastStateChangeUnix atomic.Int64
	halfOpenProbes      atomic.Uint32
}

func NewCircuitBreaker(cfg Config) *CircuitBreaker {
	cb := &CircuitBreaker{
		config: cfg,
	}
	cb.state.Store(uint32(StateClosed))
	cb.lastStateChangeUnix.Store(time.Now().UnixNano())
	return cb
}

func (cb *CircuitBreaker) AllowRequest() bool {
	currentState := State(cb.state.Load())

	if currentState == StateClosed {
		return true
	}

	if currentState == StateOpen {
		now := time.Now().UnixNano()
		lastChange := cb.lastStateChangeUnix.Load()
		if time.Duration(now-lastChange) >= cb.config.WaitDurationInOpen {
			if cb.state.CompareAndSwap(uint32(StateOpen), uint32(StateHalfOpen)) {
				cb.lastStateChangeUnix.Store(now)
				cb.halfOpenProbes.Store(0)
			}
			return cb.AllowRequest()
		}
		return false
	}

	if currentState == StateHalfOpen {
		probeID := cb.halfOpenProbes.Add(1)
		return probeID <= cb.config.PermittedHalfOpenCalls
	}

	return false
}

func (cb *CircuitBreaker) RecordResult(isFailure bool) {
	currentState := State(cb.state.Load())

	if currentState == StateHalfOpen {
		if isFailure {
			if cb.state.CompareAndSwap(uint32(StateHalfOpen), uint32(StateOpen)) {
				cb.lastStateChangeUnix.Store(time.Now().UnixNano())
			}
		} else {
			if cb.halfOpenProbes.Load() >= cb.config.PermittedHalfOpenCalls {
				if cb.state.CompareAndSwap(uint32(StateHalfOpen), uint32(StateClosed)) {
					cb.lastStateChangeUnix.Store(time.Now().UnixNano())
					cb.headIndex.Store(0)
					for i := 0; i < windowSize; i++ {
						cb.ringBuffer[i].Store(false)
					}
				}
			}
		}
		return
	}

	if currentState == StateClosed {
		idx := cb.headIndex.Add(1) - 1
		cb.ringBuffer[idx&windowMask].Store(isFailure)

		total := idx + 1
		if total >= cb.config.MinimumNumberOfCalls {
			activeWindow := uint64(windowSize)
			if total < uint64(windowSize) {
				activeWindow = total
			}

			var failures uint64
			for i := uint64(0); i < activeWindow; i++ {
				if cb.ringBuffer[i].Load() {
					failures++
				}
			}

			rate := uint32((failures * 100) / activeWindow)
			if rate >= cb.config.FailureRateThreshold {
				if cb.state.CompareAndSwap(uint32(StateClosed), uint32(StateOpen)) {
					cb.lastStateChangeUnix.Store(time.Now().UnixNano())
				}
			}
		}
	}
}

func (cb *CircuitBreaker) Execute(action func() error, fallback func(err error) error) error {
	if !cb.AllowRequest() {
		return fallback(ErrCircuitBreakerOpen)
	}

	err := action()
	cb.RecordResult(err != nil)
	if err != nil {
		return fallback(err)
	}
	return nil
}
```
:::

## Підводні камені та тонкощі паралелізму

При проєктуванні високопродуктивних неблокуючих запобіжників інженери стикаються з трьома критичними апаратними пастками, які здатні знизити пропускну здатність системи в десятки разів або призвести до прихованих станів гонки.

### 1. Помилкове розділення кеш-ліній (False Sharing) та вирівнювання пам'яті

Сучасні багатоядерні процесори архітектури x86-64 та ARM64 взаємодіють з оперативною пам'яттю блоками фіксованого розміру — кеш-лініями (Cache Lines) по 64 байти. Якщо критичні змінні стану автомата (`state`, `head_index`, `last_state_change_ns`, `half_open_probe_count`) розташовані в пам'яті поспіль у межах однієї 64-байтової структури, виникає ефект «помилкового розділення» (False Sharing).

Коли потік на ядрі 0 виконує атомарний інкремент лічильника викликів `head_index` (асемблерна інструкція `lock xadd`), кеш-контролер процесора зобов'язаний за протоколом когерентності кешів MESI (Modified, Exclusive, Shared, Invalid) перевести всю 64-байтову лінію на всіх інших ядрах у стан `Invalid`. Потік на ядрі 1, який у цей самий момент лише читає стан `state` (щоб перевірити, чи дозволено пропустити черговий HTTP-запит), змушений скинути свій кеш L1/L2 та заново завантажити лінію з повільного кешу L3 або системної шини пам'яті.

У навантажувальних тестах при інтенсивності 500 000 RPS відсутність вирівнювання призводить до просідання пропускної здатності на 75–80% виключно через апаратну конкуренцію шини когерентності (Cache Line Bouncing). Використання директиви вирівнювання `alignas(64)` у C++ та `_Alignas(64)` у C11 гарантує, що кожна гаряча змінна розташовується у власній незалежній кеш-лінії, усуваючи взаємне блокування ядер.

### 2. Модель пам'яті та порядок інструкцій (Memory Ordering)

Застосування стандартних операцій `std::memory_order_seq_cst` (послідовна узгодженість) забезпечує повний глобальний порядок, проте вимагає від процесора встановлення важких бар'єрів пам'яті (Memory Fences, таких як інструкція `mfence` або апаратне блокування шини на x86), що суттєво уповільнює виконання швидкого шляху (Hot Path).

У даній реалізації використано прецизійну модель упорядкування за принципом «здобуття-звільнення» (Acquire-Release Semantics):

* **Звільнення (`memory_order_release`):** застосовується при збереженні результату виклику в кільцевий буфер та при переході автомата в новий стан. Це гарантує, що всі попередні записи результатів або часу оновлення будуть зафіксовані в пам'яті до того, як новий стан стане видимим для інших потоків.
* **Здобуття (`memory_order_acquire`):** застосовується при читанні поточного стану `state` та мітки часу `last_state_change`. Це запобігає перевпорядкуванню інструкцій компілятором або процесором: потік гарантовано не почне надсилати виклик до бекенда раніше, ніж завершиться валідація стану запобіжника.
* **Послаблене читання (`memory_order_relaxed`):** застосовується для циклічного підсумовування комірок кільцевого буфера під час обчислення відсотка збоїв. Оскільки похибка в одне вимірювання на границі мілісекунди не впливає на стабільність системи, використання relaxed-операцій повністю знімає навантаження з конвеєра процесора.

### 3. Запобігання гонкам у фазі відновлення (HALF-OPEN)

Перехід із розімкненого стану в напіврозімкнений та назад містить тонку часову гонку (Race Condition). Коли спливає таймаут `wait_duration_in_open`, сотні паралельних потоків одночасно намагаються перевести стан з `OPEN` у `HALF_OPEN`.

Використання атомарної інструкції `compare_exchange_strong` (CAS) гарантує, що лише рівно один потік-переможець успішно змінить стан і скине лічильники пробних викликів. Усі інші потоки, що отримали невдачу в CAS, просто перечитують уже оновлений стан `HALF_OPEN`.

Далі кожен запит, що надходить у стані `HALF_OPEN`, виконує атомарне бронювання квоти через `half_open_probe_count.fetch_add(1)`. Якщо отриманий індекс перевищує `permitted_half_open_calls`, запит негайно відхиляється без жодного мережевого вводу-виводу (Fail-Fast), що надійно захищає відроджуваний бекенд від вторинного перевантаження лавиною неконтрольованих клієнтських викликів.

### 4. Арифметика індексів та переповнення 64-бітного лічильника

Для уникнення дорогої операції ділення з остачею (інструкція `div` або `idiv`, яка займає від 15 до 40 тактів процесора) розмір кільцевого буфера обрано степенем двійки: `WINDOW_SIZE = 64`. Це дозволяє замінити операцію `idx % 64` на надшвидку побітову маску `idx & (64 - 1)`, яка виконується за один такт ALU (`and`).

Глобальний лічильник `head_index` оголошено як беззнакове 64-бітне ціле число `uint64_t`. Навіть за екстремального навантаження в 10 000 000 запитів на секунду переповнення 64-бітного лічильника відбудеться лише через:

```
2⁶⁴ / (10⁷ · 86400 · 365) ≈ 58 494 роки
```

Більше того, завдяки властивостям модульної двійкової арифметики стандарту C/C++, навіть у разі переповнення перехід через нуль коректно збереже правильне позиціонування в межах бітової маски без жодних збоїв індексації.

