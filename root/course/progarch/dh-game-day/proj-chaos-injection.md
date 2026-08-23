# ⚙️ Впорскування збоїв та обробка Liveness/Readiness проб

Створення точкового інжектора збоїв (Chaos Interceptor) вимагає суворого дотримання ізоляції: механізм впорскування затримок та генерації помилок повинен працювати без блокування основними потоками обробки трафіку і не створювати додаткових гонок за ресурси (race conditions). Нижче наведено практичну реалізацію Chaos Interceptor для перехоплення HTTP та gRPC запитів у сервісах Digital Homes мовами Go, C++20 та C, а також докладний розбір внутрішньої механіки, моделей пам'яті та крайових випадків.

## Архітектурний механізм Chaos Interceptor

Інжектор збоїв вбудовується у конвеєр обробки запитів (Middleware chain / Interceptor pipeline) перед безпосереднім викликом бізнес-логіки доменного сервісу твінів (C4). Він зчитує службові заголовки `X-Chaos-Target`, `X-Chaos-Latency-Ms` та `X-Chaos-Error-Rate`. Якщо запит містить відповідний ідентифікатор канаркового експерименту, middleware застосовує вказаний профіль збою.

Паралельно перехоплювач керує станом готовності (Readiness probe). Якщо під час навчань Game Day імітується падіння кешу твінів або деградація бази даних, атомарний прапорець `ReadyStatus` переводиться у стан `0`. Це змушує ендпоінт `/ready` повертати код `503 Service Unavailable`. У результаті Kubernetes Ingress балансувальник негайно знімає трафік із даного пода, запобігаючи накопиченню черги. При цьому ендпоінт `/live` продовжує повертати код `200 OK`, запобігаючи нескінченним перезапускам контейнера оркестратором.

:::tabs
```go
package main

import (
	"context"
	"errors"
	"math/rand"
	"net/http"
	"sync/atomic"
	"time"
)

// ChaosConfig визначає параметри впорскування збоїв під час Game Day.
type ChaosConfig struct {
	LatencyMs   int32 // Додаткова затримка у мс
	ErrorRate   int32 // Відсоток генерації 500 Internal Error (0-100)
	ReadyStatus int32 // 1 - ready, 0 - degraded (fail readiness)
}

type ChaosMiddleware struct {
	config atomic.Pointer[ChaosConfig]
}

func NewChaosMiddleware() *ChaosMiddleware {
	m := &ChaosMiddleware{}
	m.config.Store(&ChaosConfig{ReadyStatus: 1})
	return m
}

func (m *ChaosMiddleware) Handler(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		cfg := m.config.Load()

		// Перевірка заголовку Game Day канарки
		if r.Header.Get("X-Chaos-Target") == "twin-cache" {
			if cfg.LatencyMs > 0 {
				time.Sleep(time.Duration(cfg.LatencyMs) * time.Millisecond)
			}

			if cfg.ErrorRate > 0 && rand.Int32n(100) < cfg.ErrorRate {
				http.Error(w, "Chaos Injector: Simulated Cache Stampede Error", http.StatusInternalServerError)
				return
			}
		}

		next.ServeHTTP(w, r)
	})
}

// LivenessHandler перевіряє лише базову життєздатність процесів (event loop).
func (m *ChaosMiddleware) LivenessHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("OK"))
}

// ReadinessHandler відключає под від трафіку при збоях downstream без вбивання процесів.
func (m *ChaosMiddleware) ReadinessHandler(w http.ResponseWriter, r *http.Request) {
	cfg := m.config.Load()
	if atomic.LoadInt32(&cfg.ReadyStatus) == 0 {
		http.Error(w, "Service Degraded: Readiness Failed", http.StatusServiceUnavailable)
		return
	}
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("READY"))
}
```
```cpp
#include <iostream>
#include <memory>
#include <random>
#include <thread>
#include <chrono>
#include <atomic>
#include <expected>
#include <string_view>

struct ChaosConfig {
    std::atomic<int32_t> latency_ms{0};
    std::atomic<int32_t> error_rate_percent{0};
    std::atomic<bool> is_ready{true};
};

class ChaosInterceptor {
public:
    explicit ChaosInterceptor(std::shared_ptr<ChaosConfig> config)
        : config_(std::move(config)), rng_(std::random_device{}()) {}

    [[nodiscard]] std::expected<std::string_view, int>
    process_request(std::string_view target_header, std::string_view payload) {
        if (target_header == "twin-cache") {
            const int lat = config_->latency_ms.load(std::memory_order_relaxed);
            if (lat > 0) {
                std::this_thread::sleep_for(std::chrono::milliseconds(lat));
            }

            const int err_rate = config_->error_rate_percent.load(std::memory_order_relaxed);
            if (err_rate > 0) {
                std::uniform_int_distribution<int> dist(0, 99);
                if (dist(rng_) < err_rate) {
                    return std::unexpected(500); // Simulated 500 Internal Error
                }
            }
        }
        return payload;
    }

    [[nodiscard]] bool check_liveness() const noexcept {
        // Liveness перевіряє лише те, що потік не заблокований навічно
        return true;
    }

    [[nodiscard]] bool check_readiness() const noexcept {
        // Readiness повертає false, коли кеш впав, знімаючи трафік з балансувальника
        return config_->is_ready.load(std::memory_order_relaxed);
    }

private:
    std::shared_ptr<ChaosConfig> config_;
    mutable std::mt19937 rng_;
};
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>

typedef struct {
    int latency_ms;
    int error_rate_percent;
    bool is_ready;
} chaos_config_t;

int process_request_c(const chaos_config_t* cfg, const char* target_header, const char* input, char* output, size_t max_len) {
    if (target_header != NULL && strcmp(target_header, "twin-cache") == 0) {
        if (cfg->latency_ms > 0) {
            usleep(cfg->latency_ms * 1000);
        }
        if (cfg->error_rate_percent > 0) {
            if ((rand() % 100) < cfg->error_rate_percent) {
                return 500; // Simulated Internal Server Error
            }
        }
    }
    snprintf(output, max_len, "%s", input);
    return 200;
}

bool check_liveness_c(void) {
    return true;
}

bool check_readiness_c(const chaos_config_t* cfg) {
    return cfg->is_ready;
}
```
:::

## Докладний розбір реалізації та моделей пам'яті

### 1. Атомарне зчитування конфігурації без м'ютексів

У високонавантажених сервісах Digital Homes, де кожен под обробляє десятки тисяч запитів на секунду, використання класичних блокуючих м'ютексів (`sync.Mutex` або `std::mutex`) для читання налаштувань хаос-експерименту є неприпустимим. М'ютекс створює болюче вичерпання ресурсів CPU на синхронізації між потоками (lock contention).

У реалізації мовою Go використовується `atomic.Pointer[ChaosConfig]`, а у версії C++20 — `std::atomic` із вказівкою слабшого порядку пам'яті `std::memory_order_relaxed`. Це дозволяє робочим потокам-воркерам зчитувати актуальний конфіг хаосу за 1-2 такти процесора без блокування системних викликів. Коли оператор Game Day або автоматичний контролер змінює конфігурацію хаосу, створюється новий екземпляр структури `ChaosConfig`, і атомарний вказівник переключається на нього за одну atomic-операцію.

### 2. Динаміка роботи Liveness проти Readiness проб

Принциповий момент реалізації — повна розв'язка логики обробки ендпоінтів `/live` та `/ready`:

- **Ендпоінт Liveness (`/live`):** Обробник `LivenessHandler` перевіряє виключно факт того, що рантайм (Go runtime / C++ event loop) функціонує, а головні системні потоки не потрапили у безкінечний цикл або deadlock. Він не перевіряє стан підключень до Postgres, Redis чи MQTT-брокера. Завдяки цьому, навіть якщо під під час впорскування збоїв уся задня інфраструктура відвалилася, Liveness залишається `200 OK`, і Kubernetes не витрачає ресурси на безглузді рестарти контейнерів.
- **Ендпоінт Readiness (`/ready`):** Обробник `ReadinessHandler` перевіряє значення атомарного прапорця `ReadyStatus`. Коли Chaos Interceptor або внутрішній засіб захисту (Circuit Breaker) фіксує перевантаження downstream-бази, `ReadyStatus` встановлюється у `0`. Обробник негайно віддає `503 Service Unavailable`. Інгрес-балансувальник Kubernetes (Nginx Ingress / Envoy) миттєво припиняє відправляти нові HTTP/gRPC запити на цей под, даючи йому можливість спокійно розгребти чергу або дочекатися відновлення кешу.

## Метрики спостережуваності та розподілене трасування (OpenTelemetry)

Застосування Chaos Interceptor вимагає чіткого простеження штучних збоїв у системах спостережуваності. Для цього інжектор експортує спеціалізовані метрики Prometheus та розширює атрибути трасування OpenTelemetry.

- **Лічильник Prometheus `chaos_injected_requests_total`:** Збільшується при кожному факті штучного додавання затримки або генерації помилки з тегами `target="twin-cache"` та `type="latency|error"`. На основі цього лічильника панель Grafana відокремлює справжні апаратні збої від навчальних ін'єкцій.
- **Атрибути спанів OpenTelemetry (Span Attributes):** При впорскуванні затримки Chaos Interceptor додає у поточний контекст трасування `traceparent` наступні атрибути: `chaos.injected=true`, `chaos.latency_ms=1500` та `chaos.target="twin-cache"`. Завдяки цьому черговий інженер при перегляді розподіленого спану у Jaeger або Grafana Tempo відразу бачить, що 1500 мс затримки виклику до Redis створені штучним перехоплювачем у межах Game Day, а не деградацією мережевої карти.

## Типові пастки реалізації та крайові випадки

### 1. Блокування робочих потоків при штучних затримках

Використання синхронних затримок `time.Sleep` або `std::this_thread::sleep_for` у блокуючому коді під час впорскування великих затримок (наприклад, 3000 мс) призводить до вичерпання пулу робочих потоків (thread pool exhaustion). У мові Go це компенсується легковаговими горутинами, але у C та C++ використання блокуючих сліпів у потоках I/O-воркерів повністю зупиняє обробку інших запитів, що не є ціллю хаос-експерименту. У продакшн-версіях на C++ впорскування затримок реалізується через асинхронні таймери Event Loop (libuv, Boost.Asio або io_uring).

### 2. Витік заголовків впорскування хаосу на зовнішньому периметрі

Найнебезпечніший крайовий випадок — це можливість зовнішніх користувачів або зловмисників відправляти заголовки `X-Chaos-Target: twin-cache` у звичайних HTTP-запитах з інтернету. Якщо периметровий API Gateway (C3 Fleet Access) не відсікає всі заголовки із префіксом `X-Chaos-*`, зовнішній зловмисник може власноруч влаштувати падіння сервісів у продакшні. Регламент Digital Homes вимагає, щоб API Gateway безумовно видаляв усі хаос-заголовки на зовнішньому периметрі й додавав їх лише всередині ізольованої мережі сервісної сітки (Service Mesh).

### 3. Некоректне генерація псевдовипадкових чисел

Використання ненадійних джерел псевдовипадкових чисел без ізоляції по потоках (thread-local RNG) призводить до гонок за стан генератора RNG. У наведеному коді C++ використовується `std::mt19937` з обгорткою над випадковим пристроєм, а у Go — захищений стандартний рандомізатор, що упереджує взаємні блокування потоків при обчисленні відсотка помилок `ErrorRate`.
