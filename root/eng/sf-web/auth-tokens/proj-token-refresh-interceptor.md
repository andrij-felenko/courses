# ⚙️ Потокобезпечний HTTP-перехоплювач з автоматичним оновленням токенів

У багатопотоковому клієнтському застосунку (мобільний застосунок, десктопний GUI чи серверний мікросервіс) десятки паралельних потоків надсилають HTTP-запити до захищеного API. Коли термін дії короткоживучого Access-токена завершується, ці запити одночасно стикаються зі статусом `401 Unauthorized` або локально фіксують прострочення токена.

Без централізованої координації виникає стан гонитви (*race condition*): кожен потік окремо ініціює виклик точки оновлення токенів (`/oauth/token`). При увімкненій ротації одноразових Refresh-токенів (*Refresh Token Rotation*) перший запит оновить сесію, а всі інші надішлють уже інвалідований токен — сервер авторизації сприйме це як спробу зламу сесії та заблокує користувача.

Задача перехоплювача (*HTTP Interceptor / Transport Adapter*) — забезпечити патерн **Single-Flight Refresh**: прозоро скоординувати потоки, виконати рівно один мережевий запит на оновлення токена, оновити локальний стан та відновити виконання всіх заблокованих запитів без повернення помилок прикладному коду.

## Архітектурний конвеєр перехоплювача

Конвеєр перехоплювача вбудовується між прикладним кодом застосунку та мережевим сокетом HTTP-клієнта (libcurl, Boost.Beast чи Python Requests). Він діє за принципом автомата скінченних станів:

```
                      ┌─────────────────────────────────┐
                      │    Прикладний HTTP-виклик       │
                      └────────────────┬────────────────┘
                                       │
                                       ▼
                   ┌───────────────────────────────────────┐
                   │ Чи дійсний токен?                     │
                   │ (t_now < expires_at - clock_skew_sec) │
                   └───────┬───────────────────────┬───────┘
                           │ ТАК                   │ НІ (прострочено)
                           ▼                       ▼
            ┌──────────────────────────┐    ┌──────────────────────────┐
            │ Додати Authorization     │    │ Захоплення Mutex         │
            │ Виконати мережевий запит │    │ Чи інший потік оновлює?  │
            └──────────────┬───────────┘    └──────┬────────────┬──────┘
                           │                       │ НІ (Leader)│ ТАК (Waiter)
                           ▼                       ▼            ▼
                   ┌───────────────┐        ┌──────────────┐ ┌─────────────┐
                   │ Відповідь 401?│        │ POST /token  │ │ Чекати Cond │
                   └───┬───────┬───┘        └──────┬───────┘ └──────┬──────┘
                   НІ  │       │ ТАК               │ Успіх          │ Прокинувся
                       ▼       ▼                   ▼                ▼
                ┌──────────┐ ┌─────────────────────────────────────────────┐
                │ 200 OK   │ │ Оновити Access/Refresh токени у сховищі    │
                │ Результат│ │ Сповістити всі очікуючі потоки (broadcast)  │
                └──────────┘ │ Повторити первинний запит (глибина = 1)     │
                             └─────────────────────────────────────────────┘
```

## Реалізація перехоплювача

Нижче наведено робочу реалізацію потокобезпечного клієнтського адаптера трьома мовами: Python, C (POSIX Threads) та ідіоматичний C++20.

:::tabs
```py
import time
import threading
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class TokenState:
    access_token: str
    refresh_token: str
    expires_at: float  # UNIX timestamp в секундах


class AuthInterceptor:
    def __init__(self, auth_endpoint: str, client_id: str, clock_skew_sec: float = 30.0):
        self.auth_endpoint = auth_endpoint
        self.client_id = client_id
        self.clock_skew_sec = clock_skew_sec
        self.token_state: Optional[TokenState] = None

        self._lock = threading.Lock()
        self._cv = threading.Condition(self._lock)
        self._is_refreshing = False

    def set_tokens(self, access_token: str, refresh_token: str, expires_in_sec: float) -> None:
        with self._lock:
            self.token_state = TokenState(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=time.time() + expires_in_sec
            )

    def get_valid_access_token(self) -> str:
        """Повертає дійсний токен, оновлюючи його при потребі (Single-Flight)."""
        with self._lock:
            while True:
                if self.token_state is None:
                    raise RuntimeError("Користувач не автентифікований")

                now = time.time()
                is_expired = now >= (self.token_state.expires_at - self.clock_skew_sec)

                if not is_expired:
                    return self.token_state.access_token

                if not self._is_refreshing:
                    # Цей потік стає лідером оновлення
                    self._is_refreshing = True
                    break
                else:
                    # Інші потоки очікують завершення лідера
                    self._cv.wait()

        # Виконуємо мережевий запит оновлення поза блокуванням основного стану
        try:
            new_tokens = self._perform_network_refresh(self.token_state.refresh_token)
            with self._lock:
                self.token_state = new_tokens
                self._is_refreshing = False
                self._cv.notify_all()
                return self.token_state.access_token
        except Exception as err:
            with self._lock:
                self._is_refreshing = False
                self._cv.notify_all()
            raise RuntimeError(f"Помилка оновлення токена: {err}") from err

    def handle_401_unauthorized(self, failed_token: str) -> str:
        """Реактивне оновлення: якщо запит отримав 401 зі старим токеном."""
        with self._lock:
            # Якщо токен уже був оновлений іншим потоком, просто беремо новий
            if self.token_state and self.token_state.access_token != failed_token:
                return self.token_state.access_token

        # Примусово запускаємо оновлення
        return self.get_valid_access_token()

    def _perform_network_refresh(self, refresh_token: str) -> TokenState:
        # Імітація HTTP POST /oauth/v2/token
        time.sleep(0.05)  # Імітація затримки мережі
        now = time.time()
        return TokenState(
            access_token=f"new_access_{int(now * 1000)}",
            refresh_token=f"new_refresh_{int(now * 1000)}",
            expires_at=now + 900.0  # +15 хвилин
        )
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

#define TOKEN_BUF_LEN 256

typedef struct {
    char access_token[TOKEN_BUF_LEN];
    char refresh_token[TOKEN_BUF_LEN];
    time_t expires_at;
} token_state_t;

typedef struct {
    token_state_t state;
    bool has_tokens;
    bool is_refreshing;
    double clock_skew_sec;
    pthread_mutex_t mutex;
    pthread_cond_t cond;
} auth_interceptor_t;

void auth_interceptor_init(auth_interceptor_t *interceptor, double skew_sec) {
    memset(&interceptor->state, 0, sizeof(token_state_t));
    interceptor->has_tokens = false;
    interceptor->is_refreshing = false;
    interceptor->clock_skew_sec = skew_sec;
    pthread_mutex_init(&interceptor->mutex, NULL);
    pthread_cond_init(&interceptor->cond, NULL);
}

void auth_interceptor_set_tokens(auth_interceptor_t *in, const char *acc, const char *ref, int expires_in) {
    pthread_mutex_lock(&in->mutex);
    strncpy(in->state.access_token, acc, TOKEN_BUF_LEN - 1);
    strncpy(in->state.refresh_token, ref, TOKEN_BUF_LEN - 1);
    in->state.expires_at = time(NULL) + expires_in;
    in->has_tokens = true;
    pthread_mutex_unlock(&in->mutex);
}

static bool perform_network_refresh(const char *old_ref, token_state_t *out_state) {
    usleep(50000); // Імітація виклику POST /oauth/token (50 мс)
    time_t now = time(NULL);
    snprintf(out_state->access_token, TOKEN_BUF_LEN, "c_acc_%ld", (long)now);
    snprintf(out_state->refresh_token, TOKEN_BUF_LEN, "c_ref_%ld", (long)now);
    out_state->expires_at = now + 900;
    return true;
}

bool auth_interceptor_get_token(auth_interceptor_t *in, char *out_buf, size_t buf_size) {
    pthread_mutex_lock(&in->mutex);

    while (1) {
        if (!in->has_tokens) {
            pthread_mutex_unlock(&in->mutex);
            return false;
        }

        time_t now = time(NULL);
        bool is_expired = (now >= (in->state.expires_at - (time_t)in->clock_skew_sec));

        if (!is_expired) {
            strncpy(out_buf, in->state.access_token, buf_size - 1);
            out_buf[buf_size - 1] = '\0';
            pthread_mutex_unlock(&in->mutex);
            return true;
        }

        if (!in->is_refreshing) {
            in->is_refreshing = true;
            break;
        } else {
            pthread_cond_wait(&in->cond, &in->mutex);
        }
    }

    char current_refresh[TOKEN_BUF_LEN];
    strncpy(current_refresh, in->state.refresh_token, TOKEN_BUF_LEN - 1);
    pthread_mutex_unlock(&in->mutex);

    token_state_t new_state;
    bool ok = perform_network_refresh(current_refresh, &new_state);

    pthread_mutex_lock(&in->mutex);
    if (ok) {
        in->state = new_state;
        strncpy(out_buf, in->state.access_token, buf_size - 1);
        out_buf[buf_size - 1] = '\0';
    }
    in->is_refreshing = false;
    pthread_cond_broadcast(&in->cond);
    pthread_mutex_unlock(&in->mutex);

    return ok;
}
```
```cpp
#include <string>
#include <chrono>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <stdexcept>
#include <thread>
#include <iostream>

struct TokenState {
    std::string access_token;
    std::string refresh_token;
    std::chrono::system_clock::time_point expires_at;
};

class AuthInterceptor {
public:
    explicit AuthInterceptor(std::chrono::seconds clock_skew = std::chrono::seconds(30))
        : clock_skew_(clock_skew), is_refreshing_(false) {}

    void set_tokens(std::string access_token, std::string refresh_token, std::chrono::seconds expires_in) {
        std::lock_guard<std::mutex> lock(mutex_);
        state_ = TokenState{
            std::move(access_token),
            std::move(refresh_token),
            std::chrono::system_clock::now() + expires_in
        };
    }

    [[nodiscard]] std::string get_valid_access_token() {
        std::string current_refresh_token;

        {
            std::unique_lock<std::mutex> lock(mutex_);
            while (true) {
                if (!state_.has_value()) {
                    throw std::runtime_error("Користувач не авторизований");
                }

                auto now = std::chrono::system_clock::now();
                bool is_expired = (now >= (state_->expires_at - clock_skew_));

                if (!is_expired) {
                    return state_->access_token;
                }

                if (!is_refreshing_) {
                    is_refreshing_ = true;
                    current_refresh_token = state_->refresh_token;
                    break;
                } else {
                    cv_.wait(lock);
                }
            }
        }

        // Оновлення виконується поза м'ютексом
        try {
            TokenState new_state = perform_network_refresh(current_refresh_token);

            std::lock_guard<std::mutex> lock(mutex_);
            state_ = std::move(new_state);
            is_refreshing_ = false;
            cv_.notify_all();
            return state_->access_token;
        } catch (...) {
            std::lock_guard<std::mutex> lock(mutex_);
            is_refreshing_ = false;
            cv_.notify_all();
            throw;
        }
    }

    [[nodiscard]] std::string handle_401(const std::string& failed_token) {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (state_.has_value() && state_->access_token != failed_token) {
                return state_->access_token; // Токен уже оновлено іншим потоком
            }
        }
        return get_valid_access_token();
    }

private:
    static TokenState perform_network_refresh(const std::string& refresh_token) {
        std::this_thread::sleep_for(std::chrono::milliseconds(50)); // Мережевий виклик
        auto now = std::chrono::system_clock::now();
        return TokenState{
            "cpp_access_token_" + std::to_string(now.time_since_epoch().count()),
            "cpp_refresh_token_" + std::to_string(now.time_since_epoch().count()),
            now + std::chrono::seconds(900)
        };
    }

    std::chrono::seconds clock_skew_;
    std::optional<TokenState> state_;
    bool is_refreshing_;
    std::mutex mutex_;
    std::condition_variable cv_;
};
```
:::

## Інженерні пастки реалізації та захист від збоїв

### 1. Нескінченний цикл повторів при відхиленні бекендом
Якщо обліковий запис користувача було заблоковано або видалено на сервері, успішне отримання нового токена неможливе, або навіть свіжий токен знову викличе відповідь `401 Unauthorized`.

Якщо перехоплювач не контролює глибину повтору запиту, клієнт увійде в нескінченний цикл блокувань:
```
Запит ➔ 401 ➔ Refresh ➔ Повтор запиту ➔ 401 ➔ Refresh ➔ Повтор запиту ...
```

**Правило ліміту повторів:** кожен оригінальний HTTP-запит повинен мати лічильник спроб авторизації `auth_retry_count`. Дозволяється строго одна спроба повтору (`auth_retry_count < 1`). Якщо після оновлення токена повторний запит знову повертає 401, клієнт вважає сесію остаточно втраченою, викидає фатальний виняток `AuthenticationFailedException` і сповіщає користувача про необхідність повторного введення облікових даних.

### 2. Експоненційна витримка з випадковим джитером (Exponential Backoff and Jitter)
Під час масового збою сервера авторизації (наприклад, перевантаження бази Redis на боці бекенда) тисячі клієнтів можуть одночасно повторювати запити оновлення токенів. Щоб уникнути добивання несправного сервера, клієнтський перехоплювач застосовує алгоритм експоненційної витримки з додаванням випадкового зсуву (*jitter*):

```
t_очікування = min(t_макс, t_базовий · 2^номер_спроби) + випадкове(0, Δt_джитеру)
```

де `t_базовий` становить зазвичай 500 мс, а випадковий джитер `Δt_джитеру` (від 100 до 300 мс) розносить сплески трафіку в часі. Без джитеру всі клієнтські потоки прокидаються в один і той самий момент часу, створюючи періодичні резонансні піки навантаження на шлюз.

### 3. Компенсація розсинхронізації системного годинника (Clock Skew)
Мобільні телефони та вбудовані пристрої IoT нерідко мають розсинхронізований системний час: користувач міг виставити годинник вручну, або батарейка RTC вийшла з ладу.
* Якщо годинник клієнта **поспішає на 10 хвилин**: токен із TTL 15 хвилин клієнт вважатиме простроченим уже через 5 хвилин після отримання. Це призведе до трикратного збільшення навантаження на сервер авторизації.
* Якщо годинник клієнта **відстає на 10 хвилин**: клієнт вважатиме прострочений токен дійсним і надсилатиме його до ресурсного API, отримуючи постійні помилки 401.

**Інженерне розв'язання:** під час кожної відповіді сервера (у заголовку `Date: Tue, 25 Aug 2026 18:00:00 GMT`) клієнт розраховує поправку часу:
```
Поправка_часу = t_сервера - t_клієнта_локальний
```
Усі наступні розрахунки `expires_at` виконуються з додаванням цієї поправки, що повністю нівелює помилки локального годинника пристрою.

### 4. Гарантоване затирання секретів у пам'яті (Memory Zeroization)
Токени автентифікації є короткоживучими, але критичними секретами. Якщо процес застосунку завершується аварійно, операційна система може зберегти дамп пам'яті (*core dump*), у якому залишаться відкриті рядки токенів.

У мовах C та C++ звичайний виклик `memset()` часто оптимізується й видаляється компілятором, якщо пам'ять звільняється одразу після цього (видалення мертвого запису, *Dead Store Elimination*). Для гарантованого знищення токенів у деструкторах використовують захищені від оптимізації системні виклики:
* Linux / POSIX: `explicit_bzero(buf, size)`
* Windows: `SecureZeroMemory(buf, size)`
* C11: `memset_s(buf, size, 0, size)`
* C++20: власні бар'єри пам'яті з `volatile pointer`.

### 5. Обробка таймаутів мережі під час оновлення токена
Якщо виклик `POST /oauth/token` зависає через розрив TCP-з'єднання чи високу затримку на маршрутизаторі, потік-лідер не повинен блокувати всі інші потоки нескінченно. Мережевий виклик оновлення обов'язково конфігурується суворим таймаутом (наприклад, 5–10 секунд). Якщо таймаут спрацьовує, перехоплювач звільняє блокування м'ютекса, скидає прапорець `is_refreshing` і надсилає сповіщення `notify_all()`, щоб потоки-очікувачі могли спробувати повторити запит або повернути керовану помилку мережі.

### 6. Асинхронна черга очікування в подієвих циклах (Event-Loop Promises)
В однопотокових асинхронних рушіях (Node.js, Chromium V8, Python AsyncIO) блокування через м'ютекс операційної системи є неприпустимим, оскільки воно заморозить увесь головний цикл обробки подій (*Event Loop*).

Замість системного м'ютекса застосовують патерн **Promise Coalescing** (злиття обіцянок):
1. Перехоплювач зберігає єдине посилання на активну обіцянку `refresh_promise: Optional[Future]`.
2. Коли перший асинхронний запит стикається з потребою оновлення, він ініціює асинхронну операцію `fetch('/oauth/token')` і зберігає цей `Promise` у полі класу.
3. Усі паралельні асинхронні запити, які виникають під час польоту першого запиту, не створюють власних мережевих викликів, а просто підписуються на той самий екземпляр `refresh_promise.then(...)`.
4. Після завершення мережевого оновлення єдиний результат автоматично активує всі призупинені корутини, які паралельно продовжують виконання своїх викликів з новим токеном.
