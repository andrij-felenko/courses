# ⚙️ Клієнт із геджуванням: затримка, бюджет токенів і скасування

Практична реалізація геджованого клієнта вимагає точної координації паралельних спроб, асинхронного таймера затримки, атомарного контролю бюджету навантаження (Token Bucket) та негайного скасування повільних дублів для запобігання марним обчисленням. Нижче наведено повнофункціональну реалізацію клієнтської бібліотеки геджування трьома мовами (C++, C та Go), яка демонструє роботу відкладеного старту, безпечну конкуренцію за першу відповідь та захист бекенду від лавиноподібного перевантаження.

## Задача: низька затримка без ризику лавини запитів

Спроектувати надійний клієнтський модуль виклику віддалених реплік розподіленого сервісу зі збереженням таких суворих інваріантів:

1. **Основна спроба (Primary Request):** запит надсилається на першу випадково або за балансувальником обрану репліку в момент `t = 0`.
2. **Відкладений гедж (Delayed Hedge):** якщо відповідь не надійшла за заданий час `hedging_delay` (наприклад, 25 мс, що відповідає P95 затримки), клієнт перевіряє наявність токенів у локальному бюджеті. Якщо токен є, він атомарно списується, і надсилається дублюючий запит на другу незалежну репліку.
3. **Гонка відповідей (Response Racing):** хто з двох серверів відповів першим із валідним результатом, той і повертає значення викликачу, завершуючи загальний дедлайн операції.
4. **Кооперативне скасування (Active Cancellation):** щойно один із потоків отримав валідну відповідь, він негайно виставляє прапорець скасування (`stop_token` або `context.Cancel`), сигналізуючи мережевому драйверу про необхідність відправити на повільний сервер фрейм скасування `RST_STREAM` для негайного звільнення його потоку та ресурсів бази даних.
5. **Захисний бюджет токенів (Token Bucket Rate Limiter):** кожен успішний основний запит повертає у відро дробову частку токена (наприклад, 0.1 токена при квоті 10%). Кожен гедж списує 1 цілий токен. Якщо відро порожнє, геджування блокується, і клієнт залишається очікувати на відповідь первинної репліки аж до повного вичерпання загального таймауту.

## Архітектура синхронізації та модель пам'яті

Координація двох паралельних мережевих викликів всередині одного клієнтського запиту містить класичну проблему гонки (англ. *race condition*). Якщо обидва сервери завершують обробку майже одночасно (наприклад, з різницею в 50 мікросекунд), клієнтська бібліотека повинна гарантувати:
* **Атомарність вибору переможця:** рівно один результат записується в результуючу структуру, а другий коректно відкидається без витоку виділеної динамічної пам'яті.
* **Бар'єри пам'яті (Memory Fences):** прапорець завершення `has_result` повинен встановлюватися з семантикою `release`, а читатися викликачем з семантикою `acquire`, щоб гарантувати видимість сформованого буфера відповіді між різними ядрами процесора без звернення до важких системних м'ютексів операційної системи на гарячому шляху.
* **Звільнення дескрипторів:** фонові потоки або горутини не повинні ставати «зомбі-обчисленнями». Якщо клієнтська функція повертає результат викликачу, всі дочірні потоки зобов'язані завершити свою роботу (`join` у C/C++ або природний вихід із горутини в Go) до повернення з функції або у фоновому пулі без блокування викликача.

## Реалізація клієнта

Погляньмо на реалізацію патерну в різних парадигмах багатопотоковості.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <thread>
#include <future>
#include <atomic>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <random>

// Атомарний бюджет токенів для захисту від шторму дублюючих запитів
class TokenBucket {
public:
    explicit TokenBucket(double max_tokens, double refill_ratio)
        : max_tokens_(max_tokens),
          tokens_(max_tokens),
          refill_ratio_(refill_ratio) {}

    // Спроба списати 1 токен для запуску гедж-запиту
    bool try_consume() {
        std::lock_guard<std::mutex> lock(mutex_);
        if (tokens_ >= 1.0) {
            tokens_ -= 1.0;
            return true;
        }
        return false;
    }

    // Поповнення бюджету при успішному виконанні основного запиту
    void record_primary_success() {
        std::lock_guard<std::mutex> lock(mutex_);
        tokens_ = std::min(max_tokens_, tokens_ + refill_ratio_);
    }

    double current_tokens() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return tokens_;
    }

private:
    mutable std::mutex mutex_;
    double max_tokens_;
    double tokens_;
    double refill_ratio_; // наприклад, 0.1 (10% квота геджування)
};

// Стан виконання одного геджованого запиту
template <typename T>
class HedgedRequestContext {
public:
    void set_result(T value) {
        std::unique_lock<std::mutex> lock(mutex_);
        if (!has_result_) {
            result_ = std::move(value);
            has_result_ = true;
            cv_.notify_all();
        }
    }

    bool is_completed() const {
        return has_result_.load(std::memory_order_relaxed);
    }

    std::optional<T> wait_result(std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_.wait_for(lock, timeout, [this] { return has_result_; });
        return result_;
    }

private:
    std::mutex mutex_;
    std::condition_variable cv_;
    std::atomic<bool> has_result_{false};
    std::optional<T> result_;
};

// Симуляція мережевого запиту до віддаленої репліки
std::string call_replica(const std::string& endpoint,
                         std::stop_token stop_tok,
                         int simulated_delay_ms) {
    auto start = std::chrono::steady_clock::now();
    while (true) {
        if (stop_tok.stop_requested()) {
            return ""; // Операцію скасовано, звільняємо сокет/потік
        }
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - start).count();
        if (elapsed >= simulated_delay_ms) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(2));
    }
    return "Response from " + endpoint;
}

// Функція геджованого виклику
std::string execute_hedged_request(
    const std::vector<std::string>& replicas,
    std::chrono::milliseconds hedge_delay,
    std::chrono::milliseconds overall_timeout,
    TokenBucket& budget)
{
    if (replicas.empty()) {
        throw std::invalid_argument("Empty replica list");
    }

    auto ctx = std::make_shared<HedgedRequestContext<std::string>>();
    std::stop_source stop_source;

    // 1. Запуск першого запиту (Репліка 1)
    std::jthread thread_primary([ctx, stop_tok = stop_source.get_token(), endpoint = replicas[0]]() {
        // Умовна затримка: 80 мс (зависла в хвості)
        std::string res = call_replica(endpoint, stop_tok, 80);
        if (!res.empty()) {
            ctx->set_result(res);
        }
    });

    // 2. Очікування на порозі геджування
    auto primary_res = ctx->wait_result(hedge_delay);
    if (primary_res.has_value()) {
        budget.record_primary_success();
        stop_source.request_stop();
        return *primary_res;
    }

    // 3. Відкладений гедж (якщо дозволяє бюджет)
    std::unique_ptr<std::jthread> thread_hedge;
    if (replicas.size() > 1 && budget.try_consume()) {
        thread_hedge = std::make_unique<std::jthread>(
            [ctx, stop_tok = stop_source.get_token(), endpoint = replicas[1]]() {
                // Швидка друга репліка: 10 мс
                std::string res = call_replica(endpoint, stop_tok, 10);
                if (!res.empty()) {
                    ctx->set_result(res);
                }
            });
    }

    // 4. Очікування залишкового дедлайну
    auto final_res = ctx->wait_result(overall_timeout - hedge_delay);
    stop_source.request_stop(); // Скасовуємо того, хто ще виконується

    if (final_res.has_value()) {
        return *final_res;
    }

    throw std::runtime_error("Deadline exceeded for all hedged replicas");
}

int main() {
    TokenBucket budget(10.0, 0.1); // Макс 10 токенів, 10% квота
    std::vector<std::string> replicas = {"replica-1.internal:50051", "replica-2.internal:50051"};

    try {
        std::string result = execute_hedged_request(
            replicas,
            std::chrono::milliseconds(25),  // P95 поріг
            std::chrono::milliseconds(200), // загальний дедлайн
            budget
        );
        std::cout << "Успіх: " << result << std::endl;
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << std::endl;
    }
    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/time.h>
#include <errno.h>

typedef struct {
    pthread_mutex_t mutex;
    double max_tokens;
    double tokens;
    double refill_ratio;
} token_bucket_t;

void token_bucket_init(token_bucket_t *b, double max_t, double ratio) {
    pthread_mutex_init(&b->mutex, NULL);
    b->max_tokens = max_t;
    b->tokens = max_t;
    b->refill_ratio = ratio;
}

bool token_bucket_try_consume(token_bucket_t *b) {
    pthread_mutex_lock(&b->mutex);
    bool ok = false;
    if (b->tokens >= 1.0) {
        b->tokens -= 1.0;
        ok = true;
    }
    pthread_mutex_unlock(&b->mutex);
    return ok;
}

void token_bucket_record_success(token_bucket_t *b) {
    pthread_mutex_lock(&b->mutex);
    b->tokens += b->refill_ratio;
    if (b->tokens > b->max_tokens) {
        b->tokens = b->max_tokens;
    }
    pthread_mutex_unlock(&b->mutex);
}

typedef struct {
    pthread_mutex_t mutex;
    pthread_cond_t cond;
    bool completed;
    char result[256];
    bool cancel_requested;
} hedged_context_t;

typedef struct {
    const char *endpoint;
    int simulated_delay_ms;
    hedged_context_t *ctx;
} worker_args_t;

void* replica_worker(void *arg) {
    worker_args_t *args = (worker_args_t*)arg;
    int step = 5;
    int elapsed = 0;

    while (elapsed < args->simulated_delay_ms) {
        pthread_mutex_lock(&args->ctx->mutex);
        if (args->ctx->cancel_requested) {
            pthread_mutex_unlock(&args->ctx->mutex);
            return NULL; // Скасовано іншою реплікою
        }
        pthread_mutex_unlock(&args->ctx->mutex);

        usleep(step * 1000);
        elapsed += step;
    }

    pthread_mutex_lock(&args->ctx->mutex);
    if (!args->ctx->completed) {
        args->ctx->completed = true;
        snprintf(args->ctx->result, sizeof(args->ctx->result),
                 "Response from %s", args->endpoint);
        pthread_cond_broadcast(&args->ctx->cond);
    }
    pthread_mutex_unlock(&args->ctx->mutex);
    return NULL;
}

bool execute_hedged_call_c(
    const char *ep1, int delay1_ms,
    const char *ep2, int delay2_ms,
    int hedge_delay_ms, int timeout_ms,
    token_bucket_t *budget, char *out_buf, size_t out_len)
{
    hedged_context_t ctx;
    pthread_mutex_init(&ctx.mutex, NULL);
    pthread_cond_init(&ctx.cond, NULL);
    ctx.completed = false;
    ctx.cancel_requested = false;
    ctx.result[0] = '\0';

    pthread_t t1, t2;
    bool t2_started = false;

    worker_args_t args1 = { ep1, delay1_ms, &ctx };
    pthread_create(&t1, NULL, replica_worker, &args1);

    // Очікуємо P95 затримку
    struct timeval now;
    struct timespec ts;
    gettimeofday(&now, NULL);
    ts.tv_sec = now.tv_sec + (now.tv_usec + hedge_delay_ms * 1000) / 1000000;
    ts.tv_nsec = ((now.tv_usec + hedge_delay_ms * 1000) % 1000000) * 1000;

    pthread_mutex_lock(&ctx.mutex);
    while (!ctx.completed) {
        int rc = pthread_cond_timedwait(&ctx.cond, &ctx.mutex, &ts);
        if (rc == ETIMEDOUT) break;
    }

    // Якщо первинний встиг
    if (ctx.completed) {
        token_bucket_record_success(budget);
        snprintf(out_buf, out_len, "%s", ctx.result);
        ctx.cancel_requested = true;
        pthread_mutex_unlock(&ctx.mutex);
        pthread_join(t1, NULL);
        return true;
    }

    // Відкладений гедж
    if (token_bucket_try_consume(budget)) {
        worker_args_t args2 = { ep2, delay2_ms, &ctx };
        pthread_create(&t2, NULL, replica_worker, &args2);
        t2_started = true;
    }

    // Залишковий таймаут
    gettimeofday(&now, NULL);
    int rem_ms = timeout_ms - hedge_delay_ms;
    ts.tv_sec = now.tv_sec + (now.tv_usec + rem_ms * 1000) / 1000000;
    ts.tv_nsec = ((now.tv_usec + rem_ms * 1000) % 1000000) * 1000;

    while (!ctx.completed) {
        int rc = pthread_cond_timedwait(&ctx.cond, &ctx.mutex, &ts);
        if (rc == ETIMEDOUT) break;
    }

    bool success = false;
    if (ctx.completed) {
        snprintf(out_buf, out_len, "%s", ctx.result);
        success = true;
    }

    ctx.cancel_requested = true;
    pthread_mutex_unlock(&ctx.mutex);

    pthread_join(t1, NULL);
    if (t2_started) {
        pthread_join(t2, NULL);
    }
    pthread_mutex_destroy(&ctx.mutex);
    pthread_cond_destroy(&ctx.cond);
    return success;
}

int main(void) {
    token_bucket_t budget;
    token_bucket_init(&budget, 10.0, 0.1);

    char response[256];
    bool ok = execute_hedged_call_c(
        "replica-1.internal", 80,  // повільна
        "replica-2.internal", 10,  // швидка
        25, 200, &budget, response, sizeof(response));

    if (ok) {
        printf("Успіх (C): %s\n", response);
    } else {
        printf("Помилка (C): Timeout\n");
    }
    return 0;
}
```
```go
package main

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

// TokenBucket забезпечує атомарний ліміт частки геджування
type TokenBucket struct {
	maxTokens   float64
	refillRatio float64
	tokens      uint64 // зберігається як помножене на 1000 ціле для атомарності
}

func NewTokenBucket(maxTokens, refillRatio float64) *TokenBucket {
	tb := &TokenBucket{
		maxTokens:   maxTokens,
		refillRatio: refillRatio,
	}
	atomic.StoreUint64(&tb.tokens, uint64(maxTokens*1000))
	return tb
}

func (tb *TokenBucket) TryConsume() bool {
	for {
		curr := atomic.LoadUint64(&tb.tokens)
		if curr < 1000 {
			return false // менше 1.0 токена
		}
		next := curr - 1000
		if atomic.CompareAndSwapUint64(&tb.tokens, curr, next) {
			return true
		}
	}
}

func (tb *TokenBucket) RecordSuccess() {
	add := uint64(tb.refillRatio * 1000)
	max := uint64(tb.maxTokens * 1000)
	for {
		curr := atomic.LoadUint64(&tb.tokens)
		next := curr + add
		if next > max {
			next = max
		}
		if atomic.CompareAndSwapUint64(&tb.tokens, curr, next) {
			return
		}
	}
}

// CallReplica симулює клієнтський RPC із підтримкою Context Cancellation
func CallReplica(ctx context.Context, endpoint string, delay time.Duration) (string, error) {
	select {
	case <-time.After(delay):
		return fmt.Sprintf("Response from %s", endpoint), nil
	case <-ctx.Done():
		return "", ctx.Err()
	}
}

// ExecuteHedgedRequest виконує виклик із відкладеним геджуванням і бюджетом
func ExecuteHedgedRequest(
	ctx context.Context,
	replicas []string,
	hedgeDelay time.Duration,
	budget *TokenBucket,
) (string, error) {
	if len(replicas) == 0 {
		return "", errors.New("empty replicas list")
	}

	// Створюємо контекст скасування для другорядних гілок
	reqCtx, cancel := context.WithCancel(ctx)
	defer cancel()

	type result struct {
		val string
		err error
	}
	resChan := make(chan result, len(replicas))
	var once sync.Once

	sendRPC := func(endpoint string, simulatedDelay time.Duration) {
		val, err := CallReplica(reqCtx, endpoint, simulatedDelay)
		if err == nil {
			once.Do(func() {
				resChan <- result{val: val}
				cancel() // миттєво скасовуємо іншу спробу
			})
		}
	}

	// 1. Старт основного запиту
	go sendRPC(replicas[0], 80*time.Millisecond)

	// 2. Таймер відкладеного геджу
	hedgeTimer := time.NewTimer(hedgeDelay)
	defer hedgeTimer.Stop()

	// Очікуємо або відповіді, або таймера P95
	select {
	case res := <-resChan:
		budget.RecordSuccess()
		return res.val, nil
	case <-hedgeTimer.C:
		// Таймер сплив — перевіряємо бюджет
		if len(replicas) > 1 && budget.TryConsume() {
			go sendRPC(replicas[1], 10*time.Millisecond)
		}
	case <-ctx.Done():
		return "", ctx.Err()
	}

	// 3. Очікування фінальної відповіді від будь-якої репліки
	select {
	case res := <-resChan:
		return res.val, nil
	case <-ctx.Done():
		return "", ctx.Err()
	}
}

func main() {
	budget := NewTokenBucket(10.0, 0.1)
	replicas := []string{"replica-1.internal:50051", "replica-2.internal:50051"}

	ctx, cancel := context.WithTimeout(context.Background(), 200*time.Millisecond)
	defer cancel()

	res, err := ExecuteHedgedRequest(ctx, replicas, 25*time.Millisecond, budget)
	if err != nil {
		fmt.Printf("Помилка (Go): %v\n", err)
	} else {
		fmt.Printf("Успіх (Go): %s\n", res)
	}
}
```
:::

## Покроковий розбір чотирьох життєвих сценаріїв

Для повного розуміння поведінки клієнта простежимо стан змінних, таймерів і потоків у чотирьох типових сценаріях експлуатації:

### Сценарій 1: Швидка первинна репліка (Happy Path)
1. У момент `t = 0` клієнт запускає потік Репліки 1 і виставляє таймер `hedgeTimer` на 25 мс.
2. О 12-й мілісекунді Репліка 1 повертає успішну відповідь.
3. Потік 1 захоплює м'ютекс / атомарний прапорець і записує результат.
4. Клієнт негайно зупиняє `hedgeTimer` (`hedgeTimer.Stop()`), поповнює бюджет токенів (`tokens = min(10.0, tokens + 0.1)`) і повертає результат викликачу.
5. Репліка 2 навіть не ініціалізується, мережевий трафік становить рівно 1 запит.

### Сценарій 2: Повільна первинна репліка та успішний гедж (Hedging Win)
1. У момент `t = 0` Репліка 1 стартує, але застрягає в паузі збирача сміття (GC pause) тривалістю 80 мс.
2. О 25-й мілісекунді спрацьовує `hedgeTimer`. Клієнт перевіряє `budget.TryConsume()`. Оскільки токени є (`tokens >= 1.0`), списується 1 токен.
3. О 25-й мс запускається Репліка 2. Вона потрапляє на вільний сервер і повертає відповідь за 10 мс (тобто в абсолютний момент `t = 35` мс).
4. Репліка 2 першою встановлює результат і викликає `stop_source.request_stop()` (або `cancel()`).
5. Клієнт миттєво віддає результат викликачу о 35-й мс.
6. Потік Репліки 1 бачить сигнал зупинки і перериває очікування, не витрачаючи пам'ять. Користувач отримав відповідь за 35 мс замість 80 мс.

### Сценарій 3: Вичерпання бюджету під час загального перевантаження (Safety Fallback)
1. Бекенд перебуває під піковим навантаженням, через що останні 10 запитів поспіль уже запустили гедж-дублі й вичерпали всі доступні токени (`tokens < 1.0`).
2. Приходить новий запит. Репліка 1 стартує в `t = 0`.
3. О 25-й мс спливає `hedgeTimer`, але `budget.TryConsume()` повертає `false`.
4. Клієнт **не запускає** другу репліку, запобігаючи множенню трафіку на перевантажений кластер.
5. Запит залишається очікувати Репліку 1 і повертає відповідь, щойно вона надійде, або завершується за загальним дедлайном (200 мс).

### Сценарій 4: Подвійна відмова або вичерпання дедлайну
1. Обидва віддалені вузли стали недосяжними через розрив міжсерверного комутатора.
2. Репліка 1 стартує в `t = 0`, о 25-й мс стартує Репліка 2.
3. О 200-й мс спливає загальний таймаут виклику (`overall_timeout`).
4. Метод `wait_result()` повертає `std::nullopt` (або `ctx.Err()`), клієнт генерує виняток `DeadlineExceeded`, закриває сокети обох спроб і звільняє пам'ять.

## Протокол мережевого скасування: HTTP/2 та gRPC

Просте переривання локального потоку клієнта є недостатнім у високонавантажених системах. Якщо клієнт припинив чекати відповіді, але не повідомив про це сервер, сервер продовжуватиме сканувати таблиці бази даних, утримувати блокування пам'яті та спалювати CPU.

У сучасних бінарних протоколах скасування працює на транспортному рівні:
* **HTTP/2 фрейм `RST_STREAM`:** Клієнтський транспортний рушій надсилає у відкритий TCP-потік спеціальний службовий фрейм `RST_STREAM` із кодом помилки `CANCEL (0x08)`. Ядро віддаленого сервера миттєво закриває логічний потік HTTP/2, не розриваючи базове TCP-з'єднання.
* **gRPC `context.Done()`:** На стороні сервера диспетчер gRPC транслює отримання `RST_STREAM` у закриття каналу контексту обробника (`ctx.Done()`).
* **Кооперативне опитування в базі даних:** Обробник бізнес-логіки періодично перевіряє стан контексту під час ітерації по курсору бази даних (`if (ctx.is_stopped()) break;`). Якщо контекст закрито, SQL-транзакція негайно надсилає `ROLLBACK` або `DISCARD`, звільняючи дискові буфери.

## Динамічне обчислення порога P95 через гістограми

У наведених прикладах поріг геджування `hedge_delay` був зафіксований на статичній величині (25 мс). У промисловому продакшені затримка бекенду змінюється протягом доби: вночі P95 може становити 8 мс, а вдень — 30 мс.

Для адаптивного геджування клієнтська бібліотека інтегрує потокову структуру даних — ковзну гістограму затримок (англ. *HDRHistogram* або *Exponentially Decaying Reservoir*):
* Кожна успішна відповідь записує виміряний час у локальну кільцеву чергу з вікном у 60 секунд.
* Фонові обчислення кожні 5 секунд перераховують значення `P95 = histogram.value_at_percentile(95.0)`.
* Нові запити використовують свіжо розраховане значення `hedge_delay`, що утримує частку геджування на строго заданому рівні (рівно 5%) незалежно від добових коливань навантаження.

## Типові пастки реалізації

1. **Витік ресурсів при відсутності кооперативного скасування:** Якщо клієнт кидає потік або сокет без відправки HTTP/2 сигналу `RST_STREAM` чи закриття контексту, віддалений сервер продовжує виконувати SQL-запити й навантажувати диски, хоча результат уже нікому не потрібен.
2. **Гонка запису результату (Data Race):** Коли обидві репліки відповідають майже одночасно (наприклад, із різницею в 100 мікросекунд), доступ до каналу результату або змінної повинен захищатися атомарним прапорцем або м'ютексом (`std::call_once` або `sync.Once`), щоб уникнути подвійного читання або корупції пам'яті.
3. **Хибне геджування неідемпотентних запитів:** Якщо функція `execute_hedged_request` викликається для HTTP POST операції списання коштів без унікального ключа ідемпотентності, обидва сервери спишуть гроші, коли перший сервер затримався лише через повільне надсилання TCP ACK відповіді.
4. **Некоректний розрахунок залишку часу (Deadline Deficit):** Якщо для другого запиту виставляється повний таймаут 200 мс замість залишкового часу `200 − 25 = 175` мс, загальний час виконання функції може роздутися до `25 + 200 = 225` мс, порушуючи SLA вищого рівня.
5. **Спільне використання пулу потоків:** Якщо для гедж-запитів використовується той самий обмежений пул потоків, що й для основних операцій, затримка в мережі призведе до вичерпання пулу потоків самими геджами, паралізуючи прийом нових запитів.
