# ⚙️ Алгоритм адаптивного допуску та захисту від шторму повторних спроб

Цей практичний проєкт розглядає математичні моделі, архітектурні варіанти та програмну реалізацію двох ключових механізмів захисту високонавантажених розподілених систем від метастабільних відмов: клієнтського експоненційного зсуву з повним джиттером (Full Jitter Backoff) та серверного адаптивного шлюзу допуску (Staged Admission Gate / Token Bucket Rate-Limiter).

## Математичне обґрунтування та порівняння стратегій повтору (Backoff Strategies)

Коли розподілена система із тисячами вузлів втрачає працездатність, усі активні клієнти переходять у режим відновлення зв'язку. Якщо клієнти виконують повторні спроби (retries) через фіксовані інтервали часу (наприклад, кожні 500 мс), виникає фазова синхронізація запитів. Це явище має назву **шторм повторних спроб (Thundering Herd Problem)**.

У дослідженні Марка Брукера (Marc Brooker, AWS) виділяють три основні стратегії розмазування повторних запитів по часовій осі:

### 1. Простий експоненційний зсув (No Jitter)
Формула інтервалу для `i`-ї спроби:
```
sleep = min(max_backoff, base_backoff · 2^i)
```
Попри те, що інтервал між спробами зростає у 2 рази з кожним кроком, **фаза запитів між клієнтами залишається синхронною**. Якщо 10 000 агентів одночасно отримали відмову в момент `t_0`, вони разом зроблять наступну спробу у момент `t_0 + base`, потім разом у `t_0 + 2·base`, створюючи потужні періодичні піки навантаження, які знову й знову валять відновлюваний сервер.

### 2. Рівномірний зсув (Equal Jitter)
Формула розбиває інтервал на дві рівні частини — детерміновану та випадкову:
```
temp = min(max_backoff, base_backoff · 2^i)
sleep = (temp / 2) + random_range(0, temp / 2)
```
Ця стратегія зменшує амплітуду піків удвічі, проте зберігає базовану синхронізацію навколо детермінованої половини `temp / 2`.

### 3. Повний зсув (Full Jitter)
Формула обирає випадковий інтервал на всьому відрізку від 0 до експоненційної межі:
```
temp = min(max_backoff, base_backoff · 2^i)
sleep = random_range(0, temp)
```
Математичне очікування затримки при Full Jitter становить `E[sleep] = temp / 2`. Завдяки абсолютно рівномірному розподілу у діапазоні `[0, temp]`, фазова синхронізація між тисячами клієнтів повністю руйнується. Піки навантаження згладжуються у плаский потік запитів, що дає серверу змогу розігріти кеші й обробити запити без повторного падіння.

## Архітектура серверного шлюзу допуску (Adaptive Token Bucket Gate)

Клієнтський джиттер згладжує піки, але не зменшує сумарну кількість запитів, якщо у мережі перебувають 18 000 агентів. Для захисту сервера у момент старта застосовується серверний **Token Bucket (ведро токенів)** із механікою покрокового розширюваного ліміту.

Принцип роботи Token Bucket:
- Ведро має максимальну ємність `capacity` (максимальний заплеск запитів) та швидкість поповнення `rate` (кількість токенів на секунду).
- Кожен вхідний запит від агента вимагає 1 токен.
- Якщо токени є (`tokens >= 1.0`), запит пропускається до ядра (Consul Raft).
- Якщо токенів немає, запит відкидається негайно (HTTP 429 Too Many Requests або сирцевий `iptables DROP`), не витрачаючи ресурсів процесора на обробку бізнес-логіки.

Під час відновлення після інциденту параметр `rate` регулюється оператором або автоматичним запобіжником (Circuit Breaker): від 1% від номінальної потужності до 100% у міру стабілізації затримки комітів у сховище.

## Порівняння алгоритмів обмеження швидкості (Rate Limiting Algorithms)

У розробці інфраструктурних шлюзів застосовують чотири основні алгоритми обмеження трафіку:

1. **Fixed Window Counter (Лічильник фіксованого вікна):** Простий лічильник на проміжку в 1 секунду. Недоліком є можливість дворазового спалаху трафіку на межі секунд.
2. **Sliding Window Log (Журнал ковзного вікна):** Зберігає часові мітки всіх запитів. Забезпечує точність, але вимагає `O(N)` пам'яті під високим навантаженням.
3. **Sliding Window Counter (Лічильник ковзного вікна):** Апроксимує кількість запитів на основі попереднього та поточного вікна. Економний до пам'яті, але дає невелику похибку.
4. **Token Bucket (Ведро токенів):** Дозволяє короткі спалахи (bursts) до розміру `capacity`, вимагає лише двох змінних у пам'яті (`tokens` та `lastUpdate`) і працює за `O(1)` часу. Саме цей алгоритм обрано для шлюзу допуску.

## Інтеграція із запобіжником (Circuit Breaker)

Шлюз допуску Token Bucket працює найефективніше, коли він керований зворотним зв'язком від **запобіжника (Circuit Breaker)**. Запобіжник має три класичні стани:

- **Closed (Зачинено):** Нормальна робота. Усі запити проходять через шлюз, ліміт `rate` встановлено на 100%.
- **Open (Відчинено):** Виявлено колапс (наприклад, затримка коміту у BoltDB перевищила 2 секунди або відсоток помилок > 50%). Шлюз негайно скидає `rate` до 0 або 1%, відсікаючи трафік наході.
- **Half-Open (Напіввідчинено):** Після виходу з паузи шлюз переходить у стан канареєчного пропуску, піднімаючи `rate` до 5% і спостерігаючи за реакцією системи. Якщо метрики стабільні, завіса відкривається повністю; якщо затримка зростає — повертається у стан Open.

## Особливості системної реалізації

При написанні системного коду для Backoff та Token Bucket необхідно враховувати два критичні крайові випадки:

1. **Монотонний годинник (Monotonic Clock):** Обчислення інтервалів часу та поповнення токенів мусить використовувати монотонне джерело часу (`steady_clock` у C++, `CLOCK_MONOTONIC` у POSIX C, `time.Now()` у Go). Використання астрономічного системного часу (`wall clock` / `CLOCK_REALTIME`) призведе до заклинювання або вибуху токенів під час корекції часу протоколом NTP.
2. **Потокобезпечність та атомарність (Thread Safety):** У багатонаправленому середовищі генератор випадкових чисел та лічильник токенів є спільними ресурсами. Захист через мутекси чи безлокові атомарні операції запобігає перегонам даних (data races).

## Робочі приклади реалізації мовами Go, C та C++

:::tabs
```go
package main

import (
	"fmt"
	"math"
	"math/rand"
	"sync"
	"time"
)

// BackoffCalculator розраховує затримку з Full Jitter.
type BackoffCalculator struct {
	Base float64
	Max  float64
	rnd  *rand.Rand
	mu   sync.Mutex
}

func NewBackoff(base, max time.Duration) *BackoffCalculator {
	return &BackoffCalculator{
		Base: base.Seconds(),
		Max:  max.Seconds(),
		rnd:  rand.New(rand.NewSource(time.Now().UnixNano())),
	}
}

func (b *BackoffCalculator) Calculate(attempt int) time.Duration {
	b.mu.Lock()
	defer b.mu.Unlock()

	temp := math.Min(b.Max, b.Base*math.Pow(2, float64(attempt)))
	sleepSeconds := b.rnd.Float64() * temp
	return time.Duration(sleepSeconds * float64(time.Second))
}

// AdmissionGate регулює покроковий допуск вузлів через Token Bucket.
type AdmissionGate struct {
	rate       float64 // токенів на секунду
	capacity   float64 // максимальна ємність
	tokens     float64
	lastUpdate time.Time
	mu         sync.Mutex
}

func NewAdmissionGate(rate, capacity float64) *AdmissionGate {
	return &AdmissionGate{
		rate:       rate,
		capacity:   capacity,
		tokens:     capacity,
		lastUpdate: time.Now(),
	}
}

func (g *AdmissionGate) Allow() bool {
	g.mu.Lock()
	defer g.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(g.lastUpdate).Seconds()
	g.lastUpdate = now

	g.tokens = math.Min(g.capacity, g.tokens+elapsed*g.rate)
	if g.tokens >= 1.0 {
		g.tokens -= 1.0
		return true
	}
	return false
}

func main() {
	backoff := NewBackoff(100*time.Millisecond, 10*time.Second)
	gate := NewAdmissionGate(50.0, 100.0) // 50 вузлів/сек

	fmt.Println("--- (Go) Розрахунок інтервалів Backoff з Full Jitter ---")
	for i := 0; i < 5; i++ {
		d := backoff.Calculate(i)
		fmt.Printf("Спроба %d: затримка %v\n", i, d)
	}

	fmt.Println("\n--- (Go) Перевірка шлюзу допуску ---")
	allowed, rejected := 0, 0
	for i := 0; i < 120; i++ {
		if gate.Allow() {
			allowed++
		} else {
			rejected++
		}
	}
	fmt.Printf("Дозволено запитів: %d, Відхилено (перелито): %d\n", allowed, rejected)
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <time.h>
#include <pthread.h>

typedef struct {
    double base_sec;
    double max_sec;
    unsigned int seed;
    pthread_mutex_t lock;
} backoff_t;

void backoff_init(backoff_t *b, double base_sec, double max_sec) {
    b->base_sec = base_sec;
    b->max_sec = max_sec;
    b->seed = (unsigned int)time(NULL);
    pthread_mutex_init(&b->lock, NULL);
}

double backoff_calculate_sec(backoff_t *b, int attempt) {
    pthread_mutex_lock(&b->lock);
    double temp = b->base_sec * pow(2.0, (double)attempt);
    if (temp > b->max_sec) {
        temp = b->max_sec;
    }
    double r = (double)rand_r(&b->seed) / (double)RAND_MAX;
    double sleep_sec = r * temp;
    pthread_mutex_unlock(&b->lock);
    return sleep_sec;
}

typedef struct {
    double rate;       // токенів/сек
    double capacity;   // максимальна ємність
    double tokens;
    struct timespec last_update;
    pthread_mutex_t lock;
} admission_gate_t;

void admission_gate_init(admission_gate_t *g, double rate, double capacity) {
    g->rate = rate;
    g->capacity = capacity;
    g->tokens = capacity;
    clock_gettime(CLOCK_MONOTONIC, &g->last_update);
    pthread_mutex_init(&g->lock, NULL);
}

bool admission_gate_allow(admission_gate_t *g) {
    pthread_mutex_lock(&g->lock);
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);

    double elapsed = (now.tv_sec - g->last_update.tv_sec) +
                     (now.tv_nsec - g->last_update.tv_nsec) / 1e9;
    g->last_update = now;

    g->tokens += elapsed * g->rate;
    if (g->tokens > g->capacity) {
        g->tokens = g->capacity;
    }

    bool allowed = false;
    if (g->tokens >= 1.0) {
        g->tokens -= 1.0;
        allowed = true;
    }
    pthread_mutex_unlock(&g->lock);
    return allowed;
}

int main(void) {
    backoff_t b;
    backoff_init(&b, 0.1, 10.0);

    printf("--- (C) Розрахунок інтервалів Backoff ---\n");
    for (int i = 0; i < 5; i++) {
        double delay = backoff_calculate_sec(&b, i);
        printf("Спроба %d: затримка %.3f сек\n", i, delay);
    }

    admission_gate_t gate;
    admission_gate_init(&gate, 50.0, 100.0);

    int allowed = 0, rejected = 0;
    for (int i = 0; i < 120; i++) {
        if (admission_gate_allow(&gate)) {
            allowed++;
        } else {
            rejected++;
        }
    }
    printf("Дозволено: %d, Відхилено: %d\n", allowed, rejected);

    pthread_mutex_destroy(&b.lock);
    pthread_mutex_destroy(&gate.lock);
    return 0;
}
```
```cpp
#include <iostream>
#include <chrono>
#include <random>
#include <cmath>
#include <algorithm>
#include <mutex>

class BackoffCalculator {
public:
    BackoffCalculator(std::chrono::duration<double> base, std::chrono::duration<double> max)
        : base_sec_(base.count()), max_sec_(max.count()), rng_(std::random_device{}()) {}

    std::chrono::duration<double> calculate(int attempt) {
        std::lock_guard<std::mutex> lock(mutex_);
        double temp = std::min(max_sec_, base_sec_ * std::pow(2.0, attempt));
        std::uniform_real_distribution<double> dist(0.0, temp);
        return std::chrono::duration<double>(dist(rng_));
    }

private:
    double base_sec_;
    double max_sec_;
    std::mt19937 rng_;
    std::mutex mutex_;
};

class AdmissionGate {
public:
    AdmissionGate(double rate_per_sec, double capacity)
        : rate_(rate_per_sec), capacity_(capacity), tokens_(capacity),
          last_update_(std::chrono::steady_clock::now()) {}

    bool allow() {
        std::lock_guard<std::mutex> lock(mutex_);
        auto now = std::chrono::steady_clock::now();
        std::chrono::duration<double> elapsed = now - last_update_;
        last_update_ = now;

        tokens_ = std::min(capacity_, tokens_ + elapsed.count() * rate_);
        if (tokens_ >= 1.0) {
            tokens_ -= 1.0;
            return true;
        }
        return false;
    }

private:
    double rate_;
    double capacity_;
    double tokens_;
    std::chrono::steady_clock::time_point last_update_;
    std::mutex mutex_;
};

int main() {
    BackoffCalculator backoff(std::chrono::milliseconds(100), std::chrono::seconds(10));
    AdmissionGate gate(50.0, 100.0);

    std::cout << "--- (C++) Розрахунок інтервалів Backoff з Full Jitter ---\n";
    for (int i = 0; i < 5; ++i) {
        auto delay = backoff.calculate(i);
        std::cout << "Спроба " << i << ": затримка " << delay.count() * 1000.0 << " мс\n";
    }

    int allowed = 0, rejected = 0;
    for (int i = 0; i < 120; ++i) {
        if (gate.allow()) {
            allowed++;
        } else {
            rejected++;
        }
    }
    std::cout << "Дозволено: " << allowed << ", Відхилено: " << rejected << "\n";

    return 0;
}
```
:::

## Тестування та інтеграція в системні агенти

Для гарантії того, що клієнтські агенти не створять шторму навантаження під час масового відновлення, реалізовані структури охоплюються фітнес-тестами (Fitness Tests):
1. **Тест фазової десинхронізації:** Запуск 1000 паралельних екземплярів `BackoffCalculator` для перевірки того, що розподіл спроб у часі є рівномірним і не утворює скупчень (clusters).
2. **Тест захисту шлюзу від переповнення:** Подача 10 000 запитів за секунду на `AdmissionGate` для підтвердження того, що середня кількість пропущених запитів строго відповідає налаштованому виходу `rate`.

Поєднання цих двох алгоритмів на стороні клієнта та сервера гарантує, що інфраструктура може відновитися після будь-якого масштабного інциденту без ризику потрапляння в метастабільний затор.
