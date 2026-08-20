# ⚙️ Реалізація Ambassador-проксі з пулом з'єднань, ретраями та перемикачем (C, C++, Go)

Цей практичний проєкт демонструє повнофункціональну розробку вихідного проксі-сервера за шаблоном Ambassador. Проксі розгортається поруч із основним застосунком в єдиному мережевому просторі імен Pod (`127.0.0.1`), приймає незашифровані локальні запити від програми, абстрагує складність взаємодії з віддаленими апстрімами, реалізує клієнтське балансування з пулом довгоживучих з'єднань, виконує повтори з експоненційним відступом і псевдовипадковим джитером, ізолює збійні вузли за допомогою скінченного автомата запобіжника (Circuit Breaker) та коректно завершує роботу під час отримання системного сигналу `SIGTERM`.

## Постановка інженерної задачі та архітектура рішення

У розподіленій системі клієнтський мікросервіс постійно звертається до зовнішніх API або кластерів баз даних. Якщо логіку повторних спроб, таймаутів, розривання збійних ланцюгів та підтримання пулу постійних з'єднань реалізовувати всередині коду кожної програми, виникає неминуче дублювання складного коду та ризик непередбачуваних каскадних аварій при зміні поведінки мережі.

Шаблон Ambassador вирішує цю проблему за допомогою повного винесення мережевої стійкості у супутній локальний процес.

Архітектура рішення базується на таких ключових компонентах:

1. **Локальний TCP-слухач (Local Ingress Listener):** Проксі відкриває сокет на адресі `127.0.0.1:8081`. Застосунок налаштовується на взаємодію з локальним портом так, ніби віддалений сервіс запущений на його власному вузлі. Передача даних через петлю зворотного зв'язку `lo` не створює накладних витрат фізичної мережі.
2. **Маршрутизатор та пул з'єднань (Connection Pool):** Ambassador підтримує пул відкритих постійних TCP-з'єднань із віддаленими екземплярами сервісу (`192.168.1.50:9000`), що усуває необхідність виконання тристороннього рукостискання TCP (SYN, SYN-ACK, ACK) та TLS-рукостискання на кожен окремий запит.
3. **Скінченний автомат запобіжника (Circuit Breaker State Machine):** Стан перемикача моделюється трьома станами:
   * `CLOSED` (Нормальний режим): запити вільно проходять до апстріму. Лічильник послідовних помилок скидається на нуль при кожному успішному виклику.
   * `OPEN` (Запобіжник розімкнутий): якщо кількість помилок поспіль досягає встановленого порогу (наприклад, 5 збоїв), проксі негайно перериває виклики і повертає застосунку статус помилки `503 Service Unavailable` без відправки пакетів у мережу, надаючи збійному сервісу час на відновлення.
   * `HALF_OPEN` (Пробний режим): після закінчення таймауту відновлення (10 секунд) проксі пропускає один пробний запит. У разі успіху запобіжник повертається у стан `CLOSED`; у разі помилки — знову переходить у стан `OPEN`.
4. **Алгоритм повторів з експоненційним відступом і джитером:** У разі виникнення мережевого збою або помилки шлюзу Ambassador виконує до трьох повторних спроб із розрахунком затримки за формулою:

```
t_backoff = min(t_max, t_base · 2ⁱ) + random(0, jitter)
```

5. **Коректне завершення роботи (Graceful Shutdown Engine):** Під час надходження системного сигналу `SIGTERM` або `SIGINT` проксі переводить атомарний прапорець зупинки в активний стан, припиняє виклик `accept()` для нових підключень, дозволяє активним з'єднанням завершити обробку запитів і лише після цього закриває файлові дескриптори.

```
+-------------------------------------------------------------------------------+
| Мережевий простір імен Pod (127.0.0.1)                                         |
|                                                                               |
|  [Застосунок] ===(TCP :8081)===> [Ambassador Proxy] ===(Пул сокетів)===> [Апстрім] |
|                                   ├── Пул з'єднань (TCP Keep-Alive)           |
|                                   ├── Автомат запобіжника (Closed/Open)       |
|                                   └── Ретраї з експоненційним відступом       |
+-------------------------------------------------------------------------------+
```

## Реалізація Ambassador-проксі

Нижче наведено паралельні реалізації ядра Ambassador-проксі на мовах C, сучасному об'єктно-орієнтованому C++20 (із застосуванням концепцій RAII, розумних вказівників, типізованих автоматів станів та `std::expected`) та Go (з використанням конкурентних горутин, каналів, пулу `http.Transport` і контекстів скасування).

:::tabs
```c
/* ambassador.c — Високопродуктивний вихідний проксі-посол мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>
#include <fcntl.h>
#include <time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>

#define LOCAL_PORT 8081
#define UPSTREAM_IP "127.0.0.1"
#define UPSTREAM_PORT 9000
#define BUFFER_SIZE 8192
#define MAX_RETRIES 3
#define BASE_BACKOFF_MS 50
#define FAILURE_THRESHOLD 5
#define RECOVERY_TIMEOUT_SEC 10

typedef enum {
    CB_CLOSED = 0,
    CB_OPEN,
    CB_HALF_OPEN
} cb_state_t;

typedef struct {
    cb_state_t state;
    int failure_count;
    time_t last_state_change;
} circuit_breaker_t;

static volatile sig_atomic_t g_running = 1;

static void handle_signal(int sig) {
    (void)sig;
    g_running = 0;
}

static void sleep_ms_with_jitter(int ms) {
    int jitter = rand() % 20;
    struct timespec ts;
    ts.tv_sec = (ms + jitter) / 1000;
    ts.tv_nsec = ((ms + jitter) % 1000) * 1000000L;
    nanosleep(&ts, NULL);
}

static int cb_allow_request(circuit_breaker_t *cb) {
    time_t now = time(NULL);
    if (cb->state == CB_OPEN) {
        if (now - cb->last_state_change >= RECOVERY_TIMEOUT_SEC) {
            cb->state = CB_HALF_OPEN;
            cb->last_state_change = now;
            return 1; /* Пробний запит у напіввідкритому стані */
        }
        return 0; /* Запобіжник розімкнутий */
    }
    return 1;
}

static void cb_record_success(circuit_breaker_t *cb) {
    cb->failure_count = 0;
    cb->state = CB_CLOSED;
}

static void cb_record_failure(circuit_breaker_t *cb) {
    cb->failure_count++;
    if (cb->failure_count >= FAILURE_THRESHOLD || cb->state == CB_HALF_OPEN) {
        cb->state = CB_OPEN;
        cb->last_state_change = time(NULL);
    }
}

static int connect_upstream(const char *ip, int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;

    int flag = 1;
    setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, (char *)&flag, sizeof(int));

    /* Встановлення таймауту на передачу та прийом */
    struct timeval tv = { .tv_sec = 2, .tv_usec = 0 };
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, (const char*)&tv, sizeof(tv));
    setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, (const char*)&tv, sizeof(tv));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    inet_pton(AF_INET, ip, &addr.sin_addr);

    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}

static void proxy_traffic(int client_fd, circuit_breaker_t *cb) {
    char buf[BUFFER_SIZE];
    ssize_t n_read = read(client_fd, buf, sizeof(buf));
    if (n_read <= 0) {
        close(client_fd);
        return;
    }

    if (!cb_allow_request(cb)) {
        const char *err_resp = "HTTP/1.1 503 Service Unavailable (Circuit Breaker Open)\r\nContent-Length: 0\r\n\r\n";
        (void)write(client_fd, err_resp, strlen(err_resp));
        close(client_fd);
        return;
    }

    int upstream_fd = -1;
    int attempt = 0;
    int success = 0;

    while (attempt < MAX_RETRIES && !success && g_running) {
        upstream_fd = connect_upstream(UPSTREAM_IP, UPSTREAM_PORT);
        if (upstream_fd >= 0) {
            if (write(upstream_fd, buf, n_read) == n_read) {
                ssize_t up_read = read(upstream_fd, buf, sizeof(buf));
                if (up_read > 0) {
                    (void)write(client_fd, buf, up_read);
                    success = 1;
                }
            }
            close(upstream_fd);
        }

        if (!success) {
            attempt++;
            if (attempt < MAX_RETRIES) {
                int backoff = BASE_BACKOFF_MS * (1 << attempt);
                sleep_ms_with_jitter(backoff);
            }
        }
    }

    if (success) {
        cb_record_success(cb);
    } else {
        cb_record_failure(cb);
        const char *err_resp = "HTTP/1.1 504 Gateway Timeout (Upstream Failed)\r\nContent-Length: 0\r\n\r\n";
        (void)write(client_fd, err_resp, strlen(err_resp));
    }

    close(client_fd);
}

int main(void) {
    srand((unsigned int)time(NULL));

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT, &sa, NULL);
    signal(SIGPIPE, SIG_IGN);

    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        perror("socket");
        return 1;
    }

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in laddr;
    memset(&laddr, 0, sizeof(laddr));
    laddr.sin_family = AF_INET;
    laddr.sin_port = htons(LOCAL_PORT);
    inet_pton(AF_INET, "127.0.0.1", &laddr.sin_addr);

    if (bind(listen_fd, (struct sockaddr *)&laddr, sizeof(laddr)) < 0) {
        perror("bind");
        close(listen_fd);
        return 1;
    }

    if (listen(listen_fd, 128) < 0) {
        perror("listen");
        close(listen_fd);
        return 1;
    }

    circuit_breaker_t cb = { .state = CB_CLOSED, .failure_count = 0, .last_state_change = 0 };
    printf("[Ambassador] Слухач активний на 127.0.0.1:%d, проксування до %s:%d\n",
           LOCAL_PORT, UPSTREAM_IP, UPSTREAM_PORT);

    while (g_running) {
        struct sockaddr_in caddr;
        socklen_t clen = sizeof(caddr);
        int client_fd = accept(listen_fd, (struct sockaddr *)&caddr, &clen);
        if (client_fd < 0) {
            if (errno == EINTR) break;
            continue;
        }
        proxy_traffic(client_fd, &cb);
    }

    printf("[Ambassador] Зупинка проксі за сигналом SIGTERM. Закриття ресурсів.\n");
    close(listen_fd);
    return 0;
}
```
```cpp
// ambassador.cpp — Ідіоматичний об'єктно-орієнтований Ambassador-проксі на C++20
#include <iostream>
#include <string>
#include <vector>
#include <span>
#include <chrono>
#include <random>
#include <thread>
#include <memory>
#include <atomic>
#include <expected>
#include <system_error>
#include <cstring>
#include <csignal>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>

using namespace std::chrono_literals;

namespace ambassador {

// RAII обгортка для безпечного володіння файловим дескриптором сокета
class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(int fd = -1) noexcept : fd_(fd) {}
    ~SocketHandle() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    SocketHandle(SocketHandle&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    void reset(int fd = -1) noexcept {
        if (fd_ >= 0) ::close(fd_);
        fd_ = fd;
    }
};

enum class CircuitState { Closed, Open, HalfOpen };

class CircuitBreaker {
    CircuitState state_{CircuitState::Closed};
    int failure_count_{0};
    const int threshold_{5};
    const std::chrono::seconds recovery_timeout_{10s};
    std::chrono::steady_clock::time_point last_state_change_{std::chrono::steady_clock::now()};

public:
    explicit CircuitBreaker(int threshold = 5) : threshold_(threshold) {}

    bool allow_request() {
        auto now = std::chrono::steady_clock::now();
        if (state_ == CircuitState::Open) {
            if (now - last_state_change_ >= recovery_timeout_) {
                state_ = CircuitState::HalfOpen;
                last_state_change_ = now;
                return true;
            }
            return false;
        }
        return true;
    }

    void record_success() noexcept {
        failure_count_ = 0;
        state_ = CircuitState::Closed;
    }

    void record_failure() noexcept {
        ++failure_count_;
        if (failure_count_ >= threshold_ || state_ == CircuitState::HalfOpen) {
            state_ = CircuitState::Open;
            last_state_change_ = std::chrono::steady_clock::now();
        }
    }

    [[nodiscard]] CircuitState state() const noexcept { return state_; }
};

class ProxyEngine {
    std::string upstream_ip_;
    int upstream_port_;
    CircuitBreaker cb_;
    std::mt19937 rng_{std::random_device{}()};

    std::expected<SocketHandle, std::error_code> connect_upstream() {
        int raw_fd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (raw_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        SocketHandle sock(raw_fd);

        int flag = 1;
        ::setsockopt(sock.get(), IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));

        timeval tv{ .tv_sec = 2, .tv_usec = 0 };
        ::setsockopt(sock.get(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
        ::setsockopt(sock.get(), SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(upstream_port_);
        ::inet_pton(AF_INET, upstream_ip_.c_str(), &addr.sin_addr);

        if (::connect(sock.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return sock;
    }

    void sleep_with_jitter(std::chrono::milliseconds base_ms) {
        std::uniform_int_distribution<int> dist(0, 20);
        std::this_thread::sleep_for(base_ms + std::chrono::milliseconds(dist(rng_)));
    }

public:
    ProxyEngine(std::string ip, int port)
        : upstream_ip_(std::move(ip)), upstream_port_(port) {}

    void handle_client(SocketHandle client) {
        std::vector<char> buffer(8192);
        ssize_t n_read = ::read(client.get(), buffer.data(), buffer.size());
        if (n_read <= 0) return;

        if (!cb_.allow_request()) {
            std::string_view err = "HTTP/1.1 503 Service Unavailable (Circuit Breaker Open)\r\nContent-Length: 0\r\n\r\n";
            ::write(client.get(), err.data(), err.size());
            return;
        }

        constexpr int max_retries = 3;
        bool success = false;

        for (int attempt = 1; attempt <= max_retries && !success; ++attempt) {
            auto up_res = connect_upstream();
            if (up_res) {
                SocketHandle upstream = std::move(*up_res);
                if (::write(upstream.get(), buffer.data(), n_read) == n_read) {
                    ssize_t up_read = ::read(upstream.get(), buffer.data(), buffer.size());
                    if (up_read > 0) {
                        ::write(client.get(), buffer.data(), up_read);
                        success = true;
                    }
                }
            }

            if (!success && attempt < max_retries) {
                sleep_with_jitter(std::chrono::milliseconds(50 * (1 << attempt)));
            }
        }

        if (success) {
            cb_.record_success();
        } else {
            cb_.record_failure();
            std::string_view err = "HTTP/1.1 504 Gateway Timeout (Upstream Failed)\r\nContent-Length: 0\r\n\r\n";
            ::write(client.get(), err.data(), err.size());
        }
    }
};

} // namespace ambassador

static std::atomic<bool> g_stop{false};
static void on_signal(int) { g_stop.store(true); }

int main() {
    std::signal(SIGTERM, on_signal);
    std::signal(SIGINT, on_signal);
    std::signal(SIGPIPE, SIG_IGN);

    int raw_listen = ::socket(AF_INET, SOCK_STREAM, 0);
    if (raw_listen < 0) return 1;
    ambassador::SocketHandle listener(raw_listen);

    int opt = 1;
    ::setsockopt(listener.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in laddr{};
    laddr.sin_family = AF_INET;
    laddr.sin_port = htons(8081);
    ::inet_pton(AF_INET, "127.0.0.1", &laddr.sin_addr);

    if (::bind(listener.get(), reinterpret_cast<sockaddr*>(&laddr), sizeof(laddr)) < 0) return 1;
    if (::listen(listener.get(), 128) < 0) return 1;

    ambassador::ProxyEngine engine("127.0.0.1", 9000);
    std::cout << "[Ambassador-C++] Сервер слухає 127.0.0.1:8081 -> 127.0.0.1:9000\n";

    while (!g_stop.load()) {
        sockaddr_in caddr{};
        socklen_t clen = sizeof(caddr);
        int client_fd = ::accept(listener.get(), reinterpret_cast<sockaddr*>(&caddr), &clen);
        if (client_fd < 0) {
            if (errno == EINTR) break;
            continue;
        }
        engine.handle_client(ambassador::SocketHandle(client_fd));
    }

    std::cout << "[Ambassador-C++] Коректне завершення роботи.\n";
    return 0;
}
```
```go
// ambassador.go — Високорівнева реалізація Ambassador-проксі на Go
package main

import (
	"context"
	"errors"
	"fmt"
	"io"
	"math/rand"
	"net"
	"net/http"
	"os"
	"os/signal"
	"sync/atomic"
	"syscall"
	"time"
)

type CircuitState int32

const (
	StateClosed CircuitState = iota
	StateOpen
	StateHalfOpen
)

type CircuitBreaker struct {
	state          int32
	failures       int32
	threshold      int32
	recoveryTime   time.Duration
	lastStateShift int64
}

func NewCircuitBreaker(threshold int32, recovery time.Duration) *CircuitBreaker {
	return &CircuitBreaker{
		threshold:    threshold,
		recoveryTime: recovery,
	}
}

func (cb *CircuitBreaker) Allow() bool {
	st := CircuitState(atomic.LoadInt32(&cb.state))
	if st == StateOpen {
		lastShift := time.Unix(0, atomic.LoadInt64(&cb.lastStateShift))
		if time.Since(lastShift) >= cb.recoveryTime {
			if atomic.CompareAndSwapInt32(&cb.state, int32(StateOpen), int32(StateHalfOpen)) {
				atomic.StoreInt64(&cb.lastStateShift, time.Now().UnixNano())
				return true
			}
		}
		return false
	}
	return true
}

func (cb *CircuitBreaker) RecordSuccess() {
	atomic.StoreInt32(&cb.failures, 0)
	atomic.StoreInt32(&cb.state, int32(StateClosed))
}

func (cb *CircuitBreaker) RecordFailure() {
	fails := atomic.AddInt32(&cb.failures, 1)
	st := CircuitState(atomic.LoadInt32(&cb.state))
	if fails >= cb.threshold || st == StateHalfOpen {
		atomic.StoreInt32(&cb.state, int32(StateOpen))
		atomic.StoreInt64(&cb.lastStateShift, time.Now().UnixNano())
	}
}

type AmbassadorProxy struct {
	upstreamURL string
	client      *http.Client
	cb          *CircuitBreaker
}

func NewAmbassadorProxy(upstreamURL string) *AmbassadorProxy {
	transport := &http.Transport{
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 20,
		IdleConnTimeout:     90 * time.Second,
		DialContext: (&net.Dialer{
			Timeout:   2 * time.Second,
			KeepAlive: 30 * time.Second,
		}).DialContext,
	}

	return &AmbassadorProxy{
		upstreamURL: upstreamURL,
		client:      &http.Client{Transport: transport, Timeout: 3 * time.Second},
		cb:          NewCircuitBreaker(5, 10*time.Second),
	}
}

func (p *AmbassadorProxy) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if !p.cb.Allow() {
		http.Error(w, "Circuit Breaker Open", http.StatusServiceUnavailable)
		return
	}

	var resp *http.Response
	var err error
	maxRetries := 3

	for attempt := 1; attempt <= maxRetries; attempt++ {
		req, _ := http.NewRequestWithContext(r.Context(), r.Method, p.upstreamURL+r.RequestURI, r.Body)
		for k, v := range r.Header {
			req.Header[k] = v
		}

		resp, err = p.client.Do(req)
		if err == nil && resp.StatusCode < 500 {
			break
		}

		if attempt < maxRetries {
			jitter := time.Duration(rand.Intn(25)) * time.Millisecond
			backoff := time.Duration(50*(1<<attempt))*time.Millisecond + jitter
			time.Sleep(backoff)
		}
	}

	if err != nil || (resp != nil && resp.StatusCode >= 500) {
		p.cb.RecordFailure()
		http.Error(w, "Upstream Gateway Error", http.StatusBadGateway)
		return
	}

	p.cb.RecordSuccess()
	defer resp.Body.Close()

	for k, v := range resp.Header {
		w.Header()[k] = v
	}
	w.WriteHeader(resp.StatusCode)
	io.Copy(w, resp.Body)
}

func main() {
	proxy := NewAmbassadorProxy("http://127.0.0.1:9000")
	server := &http.Server{
		Addr:    "127.0.0.1:8081",
		Handler: proxy,
	}

	go func() {
		fmt.Println("[Ambassador-Go] Проксі запущено на 127.0.0.1:8081")
		if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			fmt.Printf("Помилка сервера: %v\n", err)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM, syscall.SIGINT)
	<-stop

	fmt.Println("[Ambassador-Go] Плавна зупинка (Graceful Shutdown)...")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_ = server.Shutdown(ctx)
	fmt.Println("[Ambassador-Go] Проксі зупинено.")
}
```
:::

## Детальний аналіз інженерних пасток та крайових випадків

Під час експлуатації таких проксі-серверів у високонавантажених розподілених середовищах розробники стикаються з трьома критичними системними пастками:

1. **Небезпека вичерпання ефемерних портів через блокування в TIME_WAIT:**
   Коли проксі ініціює нове TCP-з'єднання з віддаленим сервісом для кожного окремого запиту і першим ініціює його закриття (`active close`), сокет переходить у стан `TIME_WAIT` ядра Linux на дві хвилини (або 60 секунд за замовчуванням). Якщо інтенсивність трафіку становить сотні запитів на секунду, стек сокетів вичерпує весь пул доступних локальних портів (близько 28 000 номерів), що призводить до відмови системного виклику `connect()` з помилкою `EADDRNOTAVAIL`. Щоб уникнути цього, реалізація на Go використовує структуру `http.Transport` із налаштованими параметрами `MaxIdleConnsPerHost` та тривалим `IdleConnTimeout`, утримуючи пул гарячих TCP Keep-Alive з'єднань.

2. **Захист від синхронізованих штормів повторів (Thundering Herd / Retry Storms):**
   Якщо кілька сотень екземплярів Ambassador одночасно втрачають зв'язок з апстрімом і починають виконувати повторні спроби з фіксованими інтервалами часу (наприклад, рівно кожні 100 мілісекунд), їхні запити синхронізуються в часі. Це породжує колосальні хвильові сплески навантаження на відновлюваний сервер, остаточно добиваючи його. Додавання невеликого псевдовипадкового зсуву (джитеру від 0 до 20 мс) розмазує трафік рівномірним шаром по часовій шкалі, дозволяючи цільовому бекенду плавно вийти зі стану перевантаження.

3. **Обробка розриву клієнтського каналу та сигнал `SIGPIPE`:**
   Якщо застосунок ініціював запит, але не дочекався відповіді і аварійно закрив локальний сокет (наприклад, через власний локальний таймаут), наступний виклик `write()` або `send()` у C/C++ за замовчуванням генерує сигнал операційної системи `SIGPIPE`. За відсутності явного обробника цей сигнал негайно вбиває весь процес проксі-сервера. У наведеному коді ця загроза усувається викликом `signal(SIGPIPE, SIG_IGN)`, що переводить помилку розриву в повернення коду `EPIPE` системною функцією `write()`.
