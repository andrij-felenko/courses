# ⚙️ Реалізація відмовостійкого клієнта: таймаути, джитер та ідемпотентність

Наївний мережевий виклик створює небезпечну ілюзію звичайної функції: програма відкриває блокуючий сокет, записує байти структури й чекає на відповідь у системному виклику ядра `recv()`. Якщо мережевий комутатор переповнений або віддалений сервер завис під час тривалої паузи збирача сміття (*garbage collection stop-the-world*), потік виконання клієнта блокується на невизначений час. Якщо ж розробник намагається вирішити проблему, додавши наївний цикл повторних спроб (*retries*) через фіксовані інтервали часу, тисячі клієнтів одночасно починають бомбардувати відновлюваний сервер, створюючи катастрофічну резонансну лавину повторів (*thundering herd problem* або шторм повторів).

Щоб перетворити ненадійний фізичний канал на передбачувану розподілену систему, клієнтський рівень повинен реалізувати чотири взаємопов'язані фундаментальні механізми захисту:
1. **Монотонний бюджет часу (*deadline budget*):** вимірювання залишку допустимого часу виконання за допомогою монотонних апаратних лічильників процесора, що повністю виключає вплив стрибків системного годинника NTP.
2. **Експоненційне відтермінування з повним джитером (*exponential backoff with full jitter*):** випадкове розсіювання повторних спроб у часі для усунення фазової синхронізації між клієнтами.
3. **Ідемпотентний ідентифікатор транзакції (*idempotency key / nonce*):** унікальний токен запиту, що дозволяє серверу однозначно розпізнати дублікат і повернути раніше збережений результат без повторного виконання бізнес-логіки.
4. **Запобіжник (*circuit breaker*):** трипозиційний скінченний автомат, який миттєво обриває запити до деградованого сервісу без звернення до сокета, запобігаючи вичерпанню локальних пулів потоків і надаючи серверу час на відновлення.

---

### Фізична природа та математика джитера: ліквідація резонансу повторів

Коли група клієнтів стикається з короткочасним збоєм мережі (наприклад, перемиканням маршруту BGP або скиданням пулу з'єднань на балансувальнику), усі клієнти фіксують помилку одночасно в момент часу `t = 0`. Якщо кожен клієнт застосовує класичне експоненційне відтермінування без рандомізації, інтервал очікування перед спробою `n` обчислюється строго детерміновано:

```
T_backoff(n) = min(T_max, T_base · 2ⁿ)
```

При такому підході всі клієнти одночасно чекають `T_base` мілісекунд і синхронно виконують повторний залп у момент `t = T_base`. Оскільки сервер ще не встиг розвантажити внутрішні черги, усі запити знову падають із таймаутом. Наступний залп відбувається в момент `t = T_base + 2 · T_base = 3 · T_base`, наступний — у момент `7 · T_base`. Утворюється хвиля резонансу: трафік являє собою серію надпотужних імпульсів із нульовим навантаженням між ними.

Дослідження інженерів Amazon (зокрема аналіз Марка Брукера, *Marc Brooker*) виділяє чотири базові математичні моделі відтермінування:
1. **Без джитера (*No Jitter*):** фіксований час `T = min(T_max, T_base · 2ⁿ)`. Повна синхронізація клієнтів, найгірший показник пікового навантаження.
2. **Рівний джитер (*Equal Jitter*):** половина інтервалу фіксована, половина випадкова:
   ```
   T_sleep = (T_backoff / 2) + random_uniform(0, T_backoff / 2)
   ```
   Зменшує синхронізацію, але зберігає імпульсну природу навантаження.
3. **Повний джитер (*Full Jitter*):** випадковий вибір із усього інтервалу від 0 до експоненційного максимуму:
   ```
   T_sleep = random_uniform(0, min(T_max, T_base · 2ⁿ))
   ```
   Повністю ліквідує пікові сплески трафіку, перетворюючи імпульси на рівномірний розподіл Пуассона на осі часу.
4. **Декорельований джитер (*Decorrelated Jitter*):** поточний інтервал залежить від попереднього випадкового значення:
   ```
   T_sleep(n) = min(T_max, random_uniform(T_base, T_sleep(n-1) · 3))
   ```
   Забезпечує максимальний розкид часу очікування, зменшуючи сумарний час відновлення кластера.

У наведеній нижче реалізації використовується алгоритм **Full Jitter**, оскільки він забезпечує оптимальний компроміс між простотою обчислення та ефективністю розсіювання клієнтського навантаження.

---

### Анатомія станів запобіжника (Circuit Breaker)

Запобіжник запобігає ситуації, коли клієнт марно витрачає процесорний час, пам'ять та дескриптори сокетів на виклики завідомо мертвого сервісу. Скінченний автомат запобіжника функціонує у трьох станах:

1. **Closed (Замкнений):** Нормальний робочий стан. Усі запити безперешкодно надсилаються до мережі. Якщо запит завершується успішно, лічильник помилок скидається в 0. Якщо запит падає з мережевою помилкою або таймаутом, лічильник помилок інкрементується. Коли кількість послідовних помилок досягає порогу `failure_threshold` (наприклад, 3 помилки поспіль), запобіжник перемикається в стан `Open` і фіксує мітку часу перемикання `open_time_ms`.
2. **Open (Розімкнений):** Стан активного захисту. Усі вхідні виклики негайно завершуються локальною помилкою (наприклад, `CircuitOpenError` або HTTP 503) взагалі без відкриття сокета чи надсилання мережевих пакетів. Клієнт миттєво повертає помилку користувачу або переходить на локальний кеш (деградація функціональності, *graceful degradation*). Стан `Open` утримується протягом періоду охолодження `cooloff_period_ms` (наприклад, 5000 мс).
3. **Half-Open (Напіврозімкнений):** Пробний стан. Після завершення періоду охолодження запобіжник пропускає рівно один пробний запит до реального сервера. Якщо пробний запит завершується успіхом, автомат вважає, що сервер відновив працездатність, скидає лічильник помилок і повертається в стан `Closed`. Якщо ж пробний запит зазнає невдачі, запобіжник миттєво повертається в стан `Open` на новий повний період охолодження.

---

### Ідемпотентність: запобігання дублюванню операцій

Головна пастка віддаленого виклику полягає в тому, що мережевий таймаут не означає, що операція не виконана. Якщо клієнт надіслав запит на переказ $100, сервер списав кошти з балансу, але пакет з відповіддю HTTP 200 OK був відкинутий проміжним маршрутизатором, клієнт фіксує помилку `Timeout`. Якщо клієнт просто повторить запит без ідентифікатора, сервер спише кошти вдруге.

Для запобігання дублюванню кожне повідомлення постачається унікальним криптографічним ключем ідемпотентності (*Idempotency Key*), який генерується клієнтом (зазвичай UUIDv4 або комбінація ідентифікатора клієнта та монотонного номера транзакції). Сервер зберігає пари `(idempotency_key, result)` у швидкому сховищі (наприклад, Redis або DynamoDB) з обмеженим часом життя (TTL). При отриманні запиту з відомим ключем сервер не виконує бізнес-транзакцію вдруге, а негайно повертає збережену відповідь попередньої успішної операції.

---

### Реалізація відмовостійкого клієнта на мовах C та C++

Нижче наведено промислові реалізації клієнтського рівня, що об'єднують монотонні таймери, повний джитер, запобіжник та ідемпотентність.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>

/* Стани скінченного автомата запобіжника (Circuit Breaker) */
typedef enum {
    CB_STATE_CLOSED,    /* Нормальний режим: пропускає всі запити */
    CB_STATE_OPEN,      /* Режим ізоляції: миттєво відхиляє запити */
    CB_STATE_HALF_OPEN  /* Пробний режим: пропускає один тестовий запит */
} CircuitState;

typedef struct {
    CircuitState state;
    uint32_t failure_count;
    uint32_t failure_threshold;
    uint64_t open_time_ms;
    uint64_t cooloff_period_ms;
} CircuitBreaker;

typedef struct {
    uint64_t deadline_ms;
    uint32_t max_retries;
    uint64_t base_backoff_ms;
    uint64_t max_backoff_ms;
} RpcPolicy;

typedef struct {
    char idempotency_key[37];
    const char *payload;
    size_t payload_len;
} RpcRequest;

typedef struct {
    int status_code;
    char body[256];
    bool is_success;
} RpcResponse;

/* Отримання монотонного часу в мілісекундах для виключення дрейфу NTP */
static uint64_t get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

/* Генерація псевдовипадкового джитера у діапазоні [0, max_val] */
static uint64_t full_jitter(uint64_t base_ms, uint64_t max_ms, uint32_t attempt) {
    uint64_t exp_limit = base_ms * (1ULL << (attempt > 20 ? 20 : attempt));
    if (exp_limit > max_ms) {
        exp_limit = max_ms;
    }
    double r = (double)rand() / (double)RAND_MAX;
    return (uint64_t)(r * (double)exp_limit);
}

void cb_init(CircuitBreaker *cb, uint32_t threshold, uint64_t cooloff_ms) {
    cb->state = CB_STATE_CLOSED;
    cb->failure_count = 0;
    cb->failure_threshold = threshold;
    cb->open_time_ms = 0;
    cb->cooloff_period_ms = cooloff_ms;
}

bool cb_allow_request(CircuitBreaker *cb) {
    uint64_t now = get_monotonic_ms();
    if (cb->state == CB_STATE_OPEN) {
        if (now - cb->open_time_ms >= cb->cooloff_period_ms) {
            cb->state = CB_STATE_HALF_OPEN;
            return true;
        }
        return false;
    }
    return true;
}

void cb_record_result(CircuitBreaker *cb, bool success) {
    if (success) {
        cb->failure_count = 0;
        cb->state = CB_STATE_CLOSED;
    } else {
        cb->failure_count++;
        if (cb->state == CB_STATE_HALF_OPEN || cb->failure_count >= cb->failure_threshold) {
            cb->state = CB_STATE_OPEN;
            cb->open_time_ms = get_monotonic_ms();
        }
    }
}

/* Імітація ненадійного віддаленого виклику з імовірністю відмови */
static bool mock_network_call(const RpcRequest *req, RpcResponse *res) {
    /* 40% імовірність мережевого скидання / таймауту */
    int roll = rand() % 100;
    if (roll < 40) {
        res->status_code = 503;
        res->is_success = false;
        snprintf(res->body, sizeof(res->body), "Service Unavailable (Timeout)");
        return false;
    }
    res->status_code = 200;
    res->is_success = true;
    snprintf(res->body, sizeof(res->body), "Processed [%s] OK", req->idempotency_key);
    return true;
}

bool rpc_invoke_resilient(CircuitBreaker *cb, const RpcPolicy *policy,
                          const RpcRequest *req, RpcResponse *out_res) {
    uint64_t start_time = get_monotonic_ms();
    uint64_t deadline = start_time + policy->deadline_ms;

    for (uint32_t attempt = 0; attempt < policy->max_retries; attempt++) {
        uint64_t now = get_monotonic_ms();
        if (now >= deadline) {
            out_res->status_code = 504;
            out_res->is_success = false;
            snprintf(out_res->body, sizeof(out_res->body), "Client Deadline Exceeded");
            return false;
        }

        if (!cb_allow_request(cb)) {
            out_res->status_code = 503;
            out_res->is_success = false;
            snprintf(out_res->body, sizeof(out_res->body), "Circuit Breaker OPEN - Short Circuited");
            return false;
        }

        bool ok = mock_network_call(req, out_res);
        cb_record_result(cb, ok);

        if (ok) {
            return true;
        }

        /* Неповторювані клієнтські помилки (4xx) не потребують ретраю */
        if (out_res->status_code >= 400 && out_res->status_code < 500) {
            return false;
        }

        /* Обчислення інтервалу паузи з урахуванням залишку бюджету часу */
        uint64_t sleep_ms = full_jitter(policy->base_backoff_ms, policy->max_backoff_ms, attempt);
        now = get_monotonic_ms();
        if (now + sleep_ms >= deadline) {
            out_res->status_code = 504;
            out_res->is_success = false;
            snprintf(out_res->body, sizeof(out_res->body), "Deadline would be exceeded during backoff");
            return false;
        }

        usleep((useconds_t)(sleep_ms * 1000ULL));
    }
    return false;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <random>
#include <optional>
#include <expected>
#include <thread>
#include <format>

enum class CircuitState {
    Closed,
    Open,
    HalfOpen
};

struct RpcPolicy {
    std::chrono::milliseconds timeout{2000};
    uint32_t max_retries{4};
    std::chrono::milliseconds base_backoff{50};
    std::chrono::milliseconds max_backoff{800};
};

struct RpcRequest {
    std::string idempotency_key;
    std::string payload;
};

struct RpcResponse {
    int status_code{200};
    std::string body;
};

enum class RpcError {
    Timeout,
    CircuitOpen,
    ServerError,
    ClientError
};

class CircuitBreaker {
public:
    CircuitBreaker(uint32_t failure_threshold, std::chrono::milliseconds cooloff)
        : threshold_(failure_threshold), cooloff_(cooloff) {}

    bool allow_request() {
        auto now = std::chrono::steady_clock::now();
        if (state_ == CircuitState::Open) {
            if (now - last_state_change_ >= cooloff_) {
                state_ = CircuitState::HalfOpen;
                return true;
            }
            return false;
        }
        return true;
    }

    void record_result(bool is_success) {
        auto now = std::chrono::steady_clock::now();
        if (is_success) {
            failure_count_ = 0;
            state_ = CircuitState::Closed;
        } else {
            failure_count_++;
            if (state_ == CircuitState::HalfOpen || failure_count_ >= threshold_) {
                state_ = CircuitState::Open;
                last_state_change_ = now;
            }
        }
    }

    CircuitState state() const { return state_; }

private:
    CircuitState state_{CircuitState::Closed};
    uint32_t failure_count_{0};
    uint32_t threshold_{3};
    std::chrono::milliseconds cooloff_{5000};
    std::chrono::steady_clock::time_point last_state_change_{std::chrono::steady_clock::now()};
};

class ResilientRpcClient {
public:
    explicit ResilientRpcClient(CircuitBreaker& cb, std::mt19937& rng)
        : cb_(cb), rng_(rng) {}

    std::expected<RpcResponse, RpcError> invoke(const RpcRequest& req, const RpcPolicy& policy) {
        const auto start = std::chrono::steady_clock::now();
        const auto deadline = start + policy.timeout;

        for (uint32_t attempt = 0; attempt < policy.max_retries; ++attempt) {
            if (std::chrono::steady_clock::now() >= deadline) {
                return std::unexpected(RpcError::Timeout);
            }

            if (!cb_.allow_request()) {
                return std::unexpected(RpcError::CircuitOpen);
            }

            auto result = mock_network_io(req);
            cb_.record_result(result.has_value());

            if (result.has_value()) {
                return result.value();
            }

            if (result.error() == RpcError::ClientError) {
                return std::unexpected(RpcError::ClientError);
            }

            auto backoff = compute_full_jitter(policy.base_backoff, policy.max_backoff, attempt);
            if (std::chrono::steady_clock::now() + backoff >= deadline) {
                return std::unexpected(RpcError::Timeout);
            }

            std::this_thread::sleep_for(backoff);
        }

        return std::unexpected(RpcError::ServerError);
    }

private:
    std::chrono::milliseconds compute_full_jitter(
        std::chrono::milliseconds base,
        std::chrono::milliseconds max_val,
        uint32_t attempt)
    {
        uint64_t multiplier = 1ULL << std::min(attempt, 20U);
        auto limit_ms = std::min(max_val.count(), base.count() * multiplier);
        std::uniform_int_distribution<uint64_t> dist(0, limit_ms);
        return std::chrono::milliseconds(dist(rng_));
    }

    std::expected<RpcResponse, RpcError> mock_network_io(const RpcRequest& req) {
        std::uniform_int_distribution<int> dist(0, 99);
        if (dist(rng_) < 40) {
            return std::unexpected(RpcError::ServerError);
        }
        return RpcResponse{
            .status_code = 200,
            .body = "Transaction completed for: " + req.idempotency_key
        };
    }

    CircuitBreaker& cb_;
    std::mt19937& rng_;
};
```
:::

---

### Простеження крізь ядро: чому сокети зависають на рівні ОС

Більшість розробників вважають, що встановлення таймауту на клієнтському сокеті (`SO_RCVTIMEO` або `SO_SNDTIMEO`) повністю гарантує повернення керування у програму. Це небезпечна помилка.

У стандартному мережевому стеку Linux системний виклик `connect()` за замовчуванням є блокуючим. Якщо цільовий сервер вимкнено або мережевий кабель відрізано, ядро ОС не отримує ані відповіді `SYN-ACK`, ані пакета скидання `RST`. Ядро починає цикл повторного надсилання `SYN`-пакетів із експоненційним відтермінуванням згідно з системним параметром `tcp_syn_retries` (за замовчуванням 6 спроб). У результаті виклик `connect()` зависає в очікуванні на **127 секунд**, повністю ігноруючи `SO_RCVTIMEO`.

Щоб уникнути блокування клієнтського пулу потоків на рівні ядра, промисловий клієнт зобов'язаний:
1. Перевести файловий дескриптор сокета в неблокуючий режим через системний виклик `fcntl(fd, F_SETFL, O_NONBLOCK)`.
2. Ініціювати з'єднання через `connect()`, який негайно повертає код `-1` з помилкою `EINPROGRESS`.
3. Очікувати готовності сокета до запису через `poll()` або `epoll_wait()` із передачею залишкового бюджету часу `deadline_ms`.
4. Встановити параметр сокета `TCP_USER_TIMEOUT` (впроваджений у Linux 2.6.37 згідно з RFC 5482). Цей параметр задає максимальний час у мілісекундах, протягом якого передані дані можуть залишатися без підтвердження (ACK), перш ніж ядро примусово закриє з'єднання й поверне додатку помилку `ETIMEDOUT`. Без `TCP_USER_TIMEOUT` звичайний TCP Keep-Alive може виявляти «мовчазну смерть» каналу зв'язку від кількох хвилин до кількох годин.

---

### Бюджет ретраїв (Retry Budget): запобігання посиленню навантаження

Навіть якщо кожен окремий клієнт використовує експоненційне відтермінування з повним джитером, масовий збій на бекенді створює математичну мультиплікацію запитів. Якщо в системі 1000 клієнтів і кожен робить до 4 спроб (`max_retries = 4`), то під час падіння бази даних сумарне навантаження на сервери зростає вчетверо: замість 1000 запитів на секунду бекенд отримує 4000 запитів на секунду. Це явище називається **каскадним множенням відмов** (*retry amplification*).

Для запобігання цьому використовується патерн **Retry Budget (Бюджет повторів)**, реалізований на базі алгоритму маркерного кошика (*Token Bucket*):
* Клієнт відстежує відношення кількості повторних спроб до загальної кількості запитів у ковзному вікні (наприклад, за останні 60 секунд).
* Клієнту дозволяється витрачати на ретраї не більше фіксованого відсотка трафіку (стандартний ліміт у бібліотеках gRPC та Finagle — **10% від загального обсягу запитів**).
* Якщо через масову деградацію бекенда частка ретраїв перевищує 10%, кошик токенів спустошується. Клієнт негайно блокує всі подальші повторні спроби, повертаючи помилку додатку після першої ж невдачі. Це гарантує, що клієнти ніколи не збільшать навантаження на сервери більш ніж на 10%.

---

### Життєвий цикл ідемпотентного токена та паралелізм виконання

У розподілених транзакціях ідентифікатор ідемпотентності проходить складний життєвий цикл на стороні сервера. Розглянемо крайовий випадок, коли перший запит клієнта ще виконується в базі даних (наприклад, важкий запит триває 800 мс), а клієнт через короткий таймаут у 500 мс уже надсилає повторну спробу з тим самим `idempotency_key`.

Якщо сервер наївно перевіряє лише наявність готового фінального результату в кеші, повторний запит почне паралельне виконання тієї самої транзакції. Утворюється стан перегонів (*race condition*), який призведе до подвійного списання балансу або конфлікту блокувань у СУБД.

Коректний життєвий цикл токена ідемпотентності складається з трьох фаз:
1. **Фаза фіксації наміру (In-Flight / Pending):** Отримавши запит, сервер виконує атомарну операцію вставки у швидке сховище (наприклад, `SET key "PROCESSING" NX EX 30` у Redis або атомарний `INSERT` в SQL-таблицю ідемпотентності). Якщо ключ уже існує зі статусом `PROCESSING`, сервер не починає повторну обробку, а стає в очікування завершення першого запиту або повертає клієнту статус HTTP 409 Conflict / HTTP 425 Too Early.
2. **Фаза виконання бізнес-логіки:** Сервер виконує транзакцію в базі даних.
3. **Фаза фіксації результату (Completed):** Сервер атомарно оновлює стан ключа, записуючи статус-код та тіло відповіді (`SET key '{"status": 200, "body": "OK"}' XX EX 86400`). Час життя ключа (TTL) встановлюється з запасом (наприклад, 24 години), щоб перекрити будь-які можливі затримки клієнтських повторів.

---

---

### Управління пулами з'єднань (Connection Pooling) та вичерпання портів

Наївна реалізація клієнта відкриває новий TCP-сокет на кожен виклик функції й закриває його після отримання відповіді. У високонавантажених розподілених системах це призводить до системного колапсу через вичерпання ефемерних портів операційної системи.

Коли клієнт закриває TCP-з'єднання через системний виклик `close()`, сокет переходить у стан ядра `TIME_WAIT` згідно зі стандартом TCP (RFC 793). Цей стан утримується протягом подвоєного максимального часу життя сегмента (`2 * MSL`, у Linux за замовчуванням **60 секунд**), щоб переконатися, що запізнілі пакети з мережі не будуть помилково прийняті новим з'єднанням на тому самому порті. Діапазон виділення клієнтських портів ядра (`/proc/sys/net/ipv4/ip_local_port_range`) зазвичай обмежений приблизно 28 000 портами (від 32768 до 60999). Якщо сервіс генерує 1000 запитів на секунду з відкриттям і закриттям сокетів, усі доступні локальні порти вичерпуються за 28 секунд, після чого виклики сокета падають із системною помилкою `EADDRNOTAVAIL` (*Cannot assign requested address*).

Крім того, кожне нове з'єднання вимагає повного тристороннього рукостискання TCP (*Three-Way Handshake: SYN -> SYN-ACK -> ACK*), а при шифруванні — додаткового криптографічного рукостискання TLS 1.3, що додає від 1 до 3 додаткових циклів кругової затримки (RTT) до кожного виклику.

Щоб запобігти вичерпанню портів і знизити накладні витрати на підключення, промисловий клієнт використовує **Пул з'єднань (Connection Pool)**:
* З'єднання підтримуються у відкритому стані (*Keep-Alive*) і використовуються повторно для наступних запитів.
* Пул обмежує максимальну кількість відкритих з'єднань до одного віддаленого вузла (`max_connections_per_host`), запобігаючи неконтрольованому зростанню споживання дескрипторів файлів (`fd leak`).
* Неактивні з'єднання закриваються за таймаутом бездіяльності (`idle_timeout`), а фонові периодичні зонди Keep-Alive перевіряють фізичну цілісність каналу зв'язку.

---

### Розподілений дедлайн і каскадне скасування (Context Propagation)

У складних сервіс-орієнтованих архітектурах один вхідний запит користувача може породжувати дерево з десятків викликів між внутрішніми мікросервісами:
```
Клієнт (бюджет 500 мс) ──► Сервіс А ──► Сервіс Б ──► База Даних
```

Якщо користувач встановив загальний бюджет часу в 500 мс, а сервіс А витратив на свою локальну обробку 450 мс, то сервісу Б залишається всього 50 мс. Якщо сервіс А передасть сервісу Б стандартний фіксований таймаут у 500 мс, сервіс Б почне виконувати важкий SQL-запит до бази даних на 400 мс, хоча клієнт уже через 50 мс відмовиться від відповіді через таймаут. База даних виконує непотрібну роботу, марно споживаючи ресурси процесора та диска.

Для запобігання цій проблемі клієнтський стек застосовує **Прокидання контексту розподіленого дедлайну (*Deadline Propagation*)**:
1. Клієнт обчислює абсолютний час дедлайну або передає залишковий час у спеціальному HTTP/gRPC заголовку (наприклад, `grpc-timeout: 50m` або `X-Request-Deadline: 1718902800500`).
2. Кожен проміжний сервіс вираховує час, витрачений на власну обробку, віднімає його від отриманого бюджету й передає оновлений зменшений залишок наступному сервісу в ланцюжку.
3. Якщо на будь-якому етапі залишок часу падає до нуля, запит негайно скасовується без надсилання подальших викликів до бази даних чи наступних мікросервісів.

---

### Детальний аналіз інженерних механізмів та крайових випадків

1. **Ізоляція за часом через монотонний таймер:**
   У коді C застосовується виклик ядра `clock_gettime(CLOCK_MONOTONIC, &ts)`, а в C++ — тип `std::chrono::steady_clock`. На відміну від астрономічного годинника `CLOCK_REALTIME` (у C++ `std::chrono::system_clock`), монотонний таймер гарантує безперервне строго додатне зростання лічильника тактів. Він фізично захищений від стрибків часу, які виникають під час корекції системного годинника демоном `ntpd` або при переході на секунди координації (*leap seconds*). Якби клієнт використовував `gettimeofday()`, корекція часу назад на 500 мс призвела б до того, що умова `now >= deadline` ніколи не спрацювала б, заблокувавши клієнтський потік у нескінченному циклі.

2. **Перевірка дедлайну перед фазою сну:**
   Перед виконанням системного виклику паузи `usleep()` або `std::this_thread::sleep_for()` алгоритм обов'язково перевіряє умову `now + sleep_ms >= deadline`. Якщо обчислений інтервал джитера виходить за межі залишку бюджету часу клієнта, спати немає сенсу: клієнт негайно перериває цикл із помилкою `DeadlineExceeded`. Це зберігає десятки мілісекунд процесорного часу для наступних завдань.

3. **Класифікація помилок на тимчасові та термінальні:**
   У клієнті вбудовано фільтр статус-кодів. Помилки сімейства 4xx (наприклад, 400 Bad Request, 401 Unauthorized, 404 Not Found) позначають помилку вхідних даних клієнта. Повторення такого запиту знову поверне ту саму помилку 400. Клієнт негайно припиняє роботу без ретраїв, запобігаючи паразитному навантаженню на сервер. Повторюються виключно тимчасові помилки мережевого транспорту або внутрішні збої сервера (500 Internal Error, 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout).

4. **Потокобезпечність та розподілені запобіжники:**
   У наведеному навчальному модулі стан запобіжника змінюється синхронно. У високопродуктивних багатопотокових серверах доступ до змінних `failure_count` та `state` захищається атомарними операціями (`std::atomic<CircuitState>`, `std::atomic<uint32_t>`) або неблокуючими структурами даних, щоб виключити блокування м'ютексів на гарячому шляху виконання тисяч паралельних запитів.



