# ⚙️ Оркестратор автоматичного failover на основі лізингу та виявлення збоїв

Автоматичне перемикання бази даних вимагає безперервного контролю стану лідера, синхронізації з розподіленим сховищем консенсусу (DCS) та виконання атомарного промоушену репліки з найсвіжішою позицією журналу попереднього запису (LSN).

Нижче наведено повнофункціональний системний координатор високої доступності на рівні простору користувача, який реалізує життєвий цикл Patroni: утримання оренди (heartbeat loop), детекцію збоїв, порівняння LSN кандидатів, ізоляцію старого лідера (fencing) та безпечне підвищення ролі.

## Архітектура супервізора та автомат станів

Координатор працює як незалежний фоновий процес на кожному вузлі кластера, керуючи локальним екземпляром СКБД через POSIX-сигнали, SQL-з'єднання та виклики зовнішнього API розподіленого консенсусу.

Вузол може перебувати в одному з п'яти станів:
1. `STATE_STANDBY_FOLLOWER` — вузол перебуває в режимі Read-Only, транслює та застосовує журнал WAL/binlog від лідера, періодично опитує DCS для контролю наявності активного лідера.
2. `STATE_LEADER_ACTIVE` — вузол успішно захопив ключ лідера в DCS, перевів локальну СКБД у режим Read-Write і запускає фоновий потік оновлення оренди (Heartbeat Thread).
3. `STATE_LEADER_DEMOTING` — спроба оновлення оренди в DCS провалилася (втрата кворуму, мережева ізоляція). Вузол негайно блокує клієнтський трафік і примусово переводить СКБД у Read-Only.
4. `STATE_FAILOVER_ELECTING` — ліз у DCS вичерпано. Вузол бере участь у виборах нового лідера: публікує свій поточний LSN, порівнює його з LSN інших реплік і намагається атомарно захопити ключ лідера.
5. `STATE_FENCED_ISOLATED` — вузол ізольовано після split-brain або апаратної аварії до ручного чи автоматичного виправлення розбіжності таймлайнів.

## Реалізація координатора

Код демонструє багатопотокову взаємодію: потік оновлення лізингу лідера, потік моніторингу репліки та логіку порівняння позицій журналу.

:::tabs
```c
/* ha_orchestrator.c — Демон координатора відмовостійкості баз даних */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <time.h>
#include <errno.h>

#define CLUSTER_NAME     "batman_cluster"
#define LEASE_TTL_MS     10000
#define HEARTBEAT_INT_MS 2000
#define RETRY_TIMEOUT_MS 5000

typedef uint64_t lsn_t;

typedef enum {
    STATE_STANDBY_FOLLOWER,
    STATE_LEADER_ACTIVE,
    STATE_LEADER_DEMOTING,
    STATE_FAILOVER_ELECTING,
    STATE_FENCED_ISOLATED
} node_state_t;

typedef struct {
    char node_id[64];
    node_state_t state;
    lsn_t current_lsn;
    uint64_t lease_expiry_mono_ms;
    bool is_healthy;
    pthread_mutex_t lock;
    pthread_cond_t cond;
    bool running;
} orchestrator_ctx_t;

/* Отримання поточного монотонного часу в мілісекундах */
static uint64_t get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

/* Імітація виклику до Distributed Consensus Store (etcd / Consul) */
static bool dcs_try_acquire_or_renew_lease(const char* node_id, uint32_t ttl_ms, uint64_t* new_expiry_ms) {
    /* Симуляція мережевого запису в DCS: атомарна транзакція CAS (Compare-And-Swap) */
    uint64_t now = get_monotonic_ms();
    *new_expiry_ms = now + ttl_ms;
    return true;
}

/* Імітація безпечної ізоляції (Fencing / STONITH) */
static bool execute_node_fencing(const char* target_node_id) {
    /* У реальній системі: виклик IPMI / AWS StopInstances / анулювання сесії */
    fprintf(stdout, "[FENCING] Успішно ізольовано вузол: %s (живлення вимкнено)\n", target_node_id);
    return true;
}

/* Промоушен локальної СКБД (перехід у Read-Write) */
static bool pg_promote_local_db(orchestrator_ctx_t* ctx) {
    fprintf(stdout, "[PROMOTION] Виконання pg_promote() для вузла %s (LSN: 0x%lX)\n",
            ctx->node_id, ctx->current_lsn);
    /* Імітація успішного перемикання таймлайну */
    return true;
}

/* Примусовий перевід у Read-Only / зупинка для уникнення Split-Brain */
static void pg_demote_local_db(orchestrator_ctx_t* ctx) {
    fprintf(stderr, "[DEMOTION] Втрата лізу! Примусова ізоляція лідера %s (Read-Only mode)\n",
            ctx->node_id);
}

/* Потік утримання оренди лідером (Heartbeat Loop) */
static void* leader_heartbeat_thread(void* arg) {
    orchestrator_ctx_t* ctx = (orchestrator_ctx_t*)arg;

    while (ctx->running) {
        pthread_mutex_lock(&ctx->lock);
        if (ctx->state != STATE_LEADER_ACTIVE) {
            pthread_mutex_unlock(&ctx->lock);
            break;
        }

        uint64_t new_exp = 0;
        bool ok = dcs_try_acquire_or_renew_lease(ctx->node_id, LEASE_TTL_MS, &new_exp);
        if (ok) {
            ctx->lease_expiry_mono_ms = new_exp;
            ctx->current_lsn += 0x1000; /* Імітація генерації WAL транзакціями */
            pthread_mutex_unlock(&ctx->lock);
        } else {
            /* Якщо не змогли продовжити ліз за час безпеки — аварійний Demote */
            ctx->state = STATE_LEADER_DEMOTING;
            pthread_mutex_unlock(&ctx->lock);
            pg_demote_local_db(ctx);
            break;
        }

        usleep(HEARTBEAT_INT_MS * 1000);
    }
    return NULL;
}

/* Виконання процедури виборів та Failover */
bool orchestrator_run_failover_cycle(orchestrator_ctx_t* ctx, const char* failed_leader_id, lsn_t max_known_lsn) {
    pthread_mutex_lock(&ctx->lock);
    
    if (ctx->state != STATE_STANDBY_FOLLOWER) {
        pthread_mutex_unlock(&ctx->lock);
        return false;
    }

    ctx->state = STATE_FAILOVER_ELECTING;
    fprintf(stdout, "[ELECTION] Початок виборів. Локальний LSN: 0x%lX, Максимальний у кластері: 0x%lX\n",
            ctx->current_lsn, max_known_lsn);

    /* Кандидат має право обиратися лише якщо його LSN не відстає від найсвіжішого */
    if (ctx->current_lsn < max_known_lsn) {
        fprintf(stderr, "[ELECTION] Відхилено: локальний вузол відстає за LSN від найсвіжішої репліки\n");
        ctx->state = STATE_STANDBY_FOLLOWER;
        pthread_mutex_unlock(&ctx->lock);
        return false;
    }

    /* 1. Обов'язкова ізоляція старого лідера перед промоушеном */
    if (!execute_node_fencing(failed_leader_id)) {
        fprintf(stderr, "[ELECTION] Помилка fencing старого лідера. Промоушен скасовано для безпеки\n");
        ctx->state = STATE_STANDBY_FOLLOWER;
        pthread_mutex_unlock(&ctx->lock);
        return false;
    }

    /* 2. Захоплення лізу в DCS */
    uint64_t expiry = 0;
    if (!dcs_try_acquire_or_renew_lease(ctx->node_id, LEASE_TTL_MS, &expiry)) {
        fprintf(stderr, "[ELECTION] Не вдалося захопити ключ лідера в DCS (конфлікт CAS)\n");
        ctx->state = STATE_STANDBY_FOLLOWER;
        pthread_mutex_unlock(&ctx->lock);
        return false;
    }

    /* 3. Промоушен бази даних */
    if (!pg_promote_local_db(ctx)) {
        fprintf(stderr, "[FATAL] Помилка команди pg_promote()!\n");
        ctx->state = STATE_FENCED_ISOLATED;
        pthread_mutex_unlock(&ctx->lock);
        return false;
    }

    ctx->state = STATE_LEADER_ACTIVE;
    ctx->lease_expiry_mono_ms = expiry;
    pthread_mutex_unlock(&ctx->lock);

    /* Запуск потоку оновлення оренди для нового лідера */
    pthread_t hb_tid;
    pthread_create(&hb_tid, NULL, leader_heartbeat_thread, ctx);
    pthread_detach(hb_tid);

    fprintf(stdout, "[SUCCESS] Вузол %s успішно підвищено до Primary лідера кластера!\n", ctx->node_id);
    return true;
}

int main(void) {
    orchestrator_ctx_t ctx;
    memset(&ctx, 0, sizeof(ctx));
    strncpy(ctx.node_id, "pg-node-02.prod", sizeof(ctx.node_id) - 1);
    ctx.state = STATE_STANDBY_FOLLOWER;
    ctx.current_lsn = 0x1A004F00;
    ctx.running = true;
    pthread_mutex_init(&ctx.lock, NULL);
    pthread_cond_init(&ctx.cond, NULL);

    fprintf(stdout, "Запуск HA оркестратора для вузла %s...\n", ctx.node_id);
    
    /* Імітація виявлення аварії лідера pg-node-01 */
    lsn_t cluster_max_lsn = 0x1A004F00;
    bool promoted = orchestrator_run_failover_cycle(&ctx, "pg-node-01.prod", cluster_max_lsn);

    if (promoted) {
        /* Імітація роботи лідера протягом 4 секунд */
        sleep(4);
    }

    ctx.running = false;
    pthread_mutex_destroy(&ctx.lock);
    pthread_cond_destroy(&ctx.cond);
    return 0;
}
```
```cpp
// ha_orchestrator.cpp — Об'єктно-орієнтований супервізор високої доступності C++20
#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <mutex>
#include <memory>
#include <atomic>
#include <expected>
#include <cstdint>

namespace ha {

using lsn_t = uint64_t;
using namespace std::chrono_literals;

enum class NodeState {
    StandbyFollower,
    LeaderActive,
    LeaderDemoting,
    FailoverElecting,
    FencedIsolated
};

enum class FailoverError {
    LsnLaggingBehind,
    FencingFailed,
    DcsAcquireFailed,
    PromotionExecutionFailed
};

class DistributedConsensusClient {
public:
    virtual ~DistributedConsensusClient() = default;
    virtual bool try_acquire_or_renew_lease(std::string_view node_id, std::chrono::milliseconds ttl,
                                            std::chrono::steady_clock::time_point& out_expiry) = 0;
};

class MockDcsClient final : public DistributedConsensusClient {
public:
    bool try_acquire_or_renew_lease(std::string_view /*node_id*/, std::chrono::milliseconds ttl,
                                    std::chrono::steady_clock::time_point& out_expiry) override {
        out_expiry = std::chrono::steady_clock::now() + ttl;
        return true;
    }
};

class FencingAgent {
public:
    virtual ~FencingAgent() = default;
    virtual bool isolate_node(std::string_view target_node_id) = 0;
};

class HardwarePduFencing final : public FencingAgent {
public:
    bool isolate_node(std::string_view target_node_id) override {
        std::cout << "[FENCING] Успішно ізольовано вузол через IPMI: " << target_node_id << '\n';
        return true;
    }
};

class FailoverOrchestrator {
public:
    FailoverOrchestrator(std::string node_id,
                         std::shared_ptr<DistributedConsensusClient> dcs,
                         std::shared_ptr<FencingAgent> fencing)
        : node_id_(std::move(node_id)),
          dcs_(std::move(dcs)),
          fencing_(std::move(fencing)),
          state_(NodeState::StandbyFollower),
          current_lsn_(0x1A004F00),
          running_(true) {}

    ~FailoverOrchestrator() {
        stop();
    }

    void stop() {
        running_ = false;
        if (heartbeat_thread_.joinable()) {
            heartbeat_thread_.join();
        }
    }

    std::expected<void, FailoverError> execute_failover(std::string_view failed_leader_id, lsn_t max_cluster_lsn) {
        std::unique_lock<std::mutex> lock(mutex_);

        if (state_ != NodeState::StandbyFollower) {
            return std::unexpected(FailoverError::PromotionExecutionFailed);
        }

        state_ = NodeState::FailoverElecting;
        std::cout << "[ELECTION] Кандидат " << node_id_ 
                  << " (LSN: 0x" << std::hex << current_lsn_ 
                  << ") перевіряє свіжість проти 0x" << max_cluster_lsn << std::dec << '\n';

        if (current_lsn_ < max_cluster_lsn) {
            state_ = NodeState::StandbyFollower;
            return std::unexpected(FailoverError::LsnLaggingBehind);
        }

        // 1. Атомарний Fencing попереднього лідера
        if (!fencing_->isolate_node(failed_leader_id)) {
            state_ = NodeState::StandbyFollower;
            return std::unexpected(FailoverError::FencingFailed);
        }

        // 2. Захоплення лізингу в консенсусі
        std::chrono::steady_clock::time_point expiry;
        if (!dcs_->try_acquire_or_renew_lease(node_id_, 10000ms, expiry)) {
            state_ = NodeState::StandbyFollower;
            return std::unexpected(FailoverError::DcsAcquireFailed);
        }

        // 3. Підвищення локального екземпляра
        if (!promote_database_instance()) {
            state_ = NodeState::FencedIsolated;
            return std::unexpected(FailoverError::PromotionExecutionFailed);
        }

        state_ = NodeState::LeaderActive;
        lease_expiry_ = expiry;

        // Запуск RAII-керованого потоку heartbeat
        if (heartbeat_thread_.joinable()) {
            heartbeat_thread_.join();
        }
        heartbeat_thread_ = std::jthread([this](std::stop_token st) {
            heartbeat_loop(st);
        });

        std::cout << "[SUCCESS] Вузол " << node_id_ << " активовано як новий Primary!\n";
        return {};
    }

private:
    bool promote_database_instance() {
        std::cout << "[PROMOTION] Виклик pg_promote() для " << node_id_ << '\n';
        return true;
    }

    void demote_database_instance() {
        std::cerr << "[DEMOTION] Втрата зв'язку з DCS. Переведення " << node_id_ << " у Read-Only!\n";
    }

    void heartbeat_loop(std::stop_token st) {
        while (!st.stop_requested() && running_) {
            {
                std::unique_lock<std::mutex> lock(mutex_);
                if (state_ != NodeState::LeaderActive) {
                    break;
                }

                std::chrono::steady_clock::time_point new_expiry;
                if (dcs_->try_acquire_or_renew_lease(node_id_, 10000ms, new_expiry)) {
                    lease_expiry_ = new_expiry;
                    current_lsn_ += 0x1000;
                } else {
                    state_ = NodeState::LeaderDemoting;
                    demote_database_instance();
                    break;
                }
            }
            std::this_thread::sleep_for(2000ms);
        }
    }

    std::string node_id_;
    std::shared_ptr<DistributedConsensusClient> dcs_;
    std::shared_ptr<FencingAgent> fencing_;
    NodeState state_;
    lsn_t current_lsn_;
    std::chrono::steady_clock::time_point lease_expiry_;
    std::atomic<bool> running_;
    std::mutex mutex_;
    std::jthread heartbeat_thread_;
};

} // namespace ha

int main() {
    auto dcs = std::make_shared<ha::MockDcsClient>();
    auto fencing = std::make_shared<ha::HardwarePduFencing>();

    ha::FailoverOrchestrator orchestrator("pg-node-02.prod", dcs, fencing);

    std::cout << "Запуск C++ HA координатора...\n";
    auto result = orchestrator.execute_failover("pg-node-01.prod", 0x1A004F00);

    if (result.has_value()) {
        std::this_thread::sleep_for(4000ms);
    } else {
        std::cerr << "Помилка Failover!\n";
    }

    return 0;
}
```
:::

## Механіка розподіленого консенсусу та протокол CAS

Основою безпеки оркестратора є операція Compare-And-Swap (CAS) у розподіленому сховищі ключів і значень (etcd або Consul).

Коли лідер утримує ключ `/service/batman/leader`, запис у DCS має внутрішню версію модифікації (в etcd це поле `mod_revision`). При продовженні оренди клієнт надсилає атомарну транзакцію:

```
If:   Key("/service/batman/leader").Version == Current_Known_Version
Then: Put("/service/batman/leader", Node_ID, Lease=TTL_10s)
Else: Abort_Transaction
```

Якщо мережева затримка призвела до того, що DCS уже визнав ключ протермінованим і видалив його, спроба лідера оновити ключ із застарілим значенням `mod_revision` зазнає невдачі. Отримавши відмову транзакції, координатор миттєво фіксує втрату лідерства та ініціює процедуру самодемоушену (Demotion).

## Апаратний сторожовий таймер (Linux Watchdog) та системна інтеграція

У промислових кластерах потік heartbeat не може покладатися лише на безперебійність роботи процесу в просторі користувача. Якщо операційна система Linux зазнає вичерпання пам'яті (OOM) або зависає в дисковому драйвері під час масивного скидання брудних сторінок пам'яті (`fsync hang`), планувальник ядра може не виділяти кванти часу процесу координатора протягом десятків секунд. У цей час процес СКБД продовжує приймати клієнтські транзакції через активні сокети, хоча термін дії лізу в DCS уже сплив.

Для запобігання цьому критичному збою застосовують системний драйвер Linux Watchdog (`/dev/watchdog` або модуль `softdog`):

1. **Ініціалізація:** Під час старту координатор відкриває спеціальний файловий дескриптор пристрою сторожового таймера `int fd = open("/dev/watchdog", O_WRONLY)`. Драйвер ядра запускає зворотний відлік апаратного або ядерного таймера (наприклад, 5 секунд).
2. **Періодичний скид (Keep-Alive Ping):** У кожній ітерації циклу утримання оренди, лише після успішного підтвердження від кворуму etcd, процес записує будь-який байт у файл дескриптора через виклик `write(fd, "\0", 1)` або ioctl `ioctl(fd, WDIOC_KEEPALIVE, 0)`.
3. **Апаратне самогубство (Kernel Panic / Hardware Reset):** Якщо потік завис або втратив зв'язок із DCS, скидання таймера припиняється. Через 5 секунд драйвер watchdog ядра або контролер BMC/IPMI материнської плати надсилає прямий апаратний сигнал `RESET` на шину живлення процесора. Сервер миттєво знеструмлюється, унеможливлюючи появу двох лідерів (Split-Brain).
4. **Штатне вимкнення:** Якщо координатор зупиняється адміністратором штатно, він записує спеціальний магічний символ `'V'` (`Magic Close`) у `/dev/watchdog`, що сигналізує ядру про безпечне вимкнення сторожового таймера без перезавантаження вузла.

## Простеження аварійного сценарію: часова шкала та системні події

Розглянемо покроковий журнал реального інциденту, зафіксований системним демоном координатора під час раптового виходу з ладу процесора лідера:

```
[00:00:00.000] [INFO]  Вузол 1 (Primary) успішно оновив ліз у etcd (монотонний час: 10452300, TTL: 10000ms).
[00:00:01.850] [FATAL] Апаратна відмова CPU на Вузлі 1. Процес PostgreSQL та координатор миттєво гинуть.
[00:00:02.000] [DEBUG] Вузол 2 (Standby) опитує DCS: ключ /service/batman/leader існує, залишок TTL = 8000ms.
[00:00:04.000] [DEBUG] Вузол 2 опитує DCS: залишок TTL = 6000ms. Оновлення від лідера відсутні.
[00:00:10.005] [WARN]  DCS etcd фіксує вичерпання TTL. Ключ лідера автоматично видаляється за таймаутом.
[00:00:10.020] [INFO]  Вузол 2 виявляє зникнення ключа лідера. Перехід у стан STATE_FAILOVER_ELECTING.
[00:00:10.035] [INFO]  Вузол 2 зчитує свій LSN (0x1A004F00) та запитує LSN у Вузла 3 (0x1A004E80). Вузол 2 найсвіжіший.
[00:00:10.050] [ACTION] Виклик агента Fencing: відправка сигналу знеструмлення IPMI Power Off на Вузол 1.
[00:00:10.850] [CONFIRM] IPMI підтверджує: Вузол 1 знеструмлено (Chassis Power is OFF).
[00:00:10.865] [ACTION] Атомарна транзакція etcd CAS: спроба створити ключ /service/batman/leader із значенням "node-02".
[00:00:10.880] [SUCCESS] etcd транзакцію підтверджено. Вузол 2 володіє лізом лідера.
[00:00:10.885] [ACTION] Виконання pg_promote() через локальний Unix-сокет PostgreSQL.
[00:00:11.450] [INFO]  PostgreSQL завершив відновлення, відкрив Timeline 2 і перейшов у режим Read-Write.
[00:00:11.460] [ACTION] HTTP REST API Patroni на Вузлі 2 починає відповідати кодом 200 OK на /primary.
[00:00:12.000] [INFO]  HAProxy надсилає черговий health-check, бачить 200 OK і спрямовує клієнтський трафік на Вузол 2.
```

Сумарний час недоступності запису (RTO) для клієнтських застосунків склав рівно 12.0 секунд, з яких 10.0 секунд припало на очікування закінчення оренди в DCS.

## Мережеві сокети, низькорівневий тюнінг та таймаути TCP

Найпоширенішою причиною «зависання» процесу виборів є блокування мережевих сокетів за замовчуванням у ядрі Linux.

Якщо координатор або клієнтська бібліотека відкриває звичайний TCP-сокет до бази даних або DCS без спеціальних прапорців, і посеред передачі даних мережевий комутатор мовчки скидає таблицю маршрутизації (blackhole):
1. Стандартний таймер TCP retransmission у Linux намагається повторно надіслати непідтверджений сегмент через експоненційний backoff (`tcp_retries2 = 15`).
2. Сокет зависає у стані блокуючого виклику `read()` або `write()` на **13–30 хвилин**.
3. Весь процес оркестратора виявляється паралізованим, не здатним ні оновити ліз, ні ініціювати failover.

Для запобігання цій катастрофі всі мережеві з'єднання координатора налаштовуються з обов'язковими низькорівневими опціями сокетів:

```c
int enable_socket_safety_timeouts(int sockfd) {
    int keepalive = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_KEEPALIVE, &keepalive, sizeof(keepalive));

    int keepidle = 2;    /* Почати надсилати probe-пакети після 2 секунд тиші */
    setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPIDLE, &keepidle, sizeof(keepidle));

    int keepintvl = 1;   /* Інтервал між повторними probe-пакетами: 1 секунда */
    setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPINTVL, &keepintvl, sizeof(keepintvl));

    int keepcnt = 3;     /* Визнати сокет мертвим після 3 пропущених відповідей */
    setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPCNT, &keepcnt, sizeof(keepcnt));

    /* Граничний таймаут утримання непідтверджених даних у мілісекундах (Linux 2.6.37+) */
    unsigned int user_timeout_ms = 4000;
    setsockopt(sockfd, IPPROTO_TCP, TCP_USER_TIMEOUT, &user_timeout_ms, sizeof(user_timeout_ms));
    return 0;
}
```

Завдяки параметру `TCP_USER_TIMEOUT = 4000` ядро примусово закриває сокет з помилкою `ETIMEDOUT` рівно через 4 секунди після втрати зв'язку, дозволяючи координатору вчасно зреагувати на збій і не допустити простою.

## Анатомія планового перемикання (Planned Switchover)

На відміну від аварійного failover під час катастрофи, плановий перехід (Switchover) виконується для планового обслуговування (оновлення ОС, заміна заліза, міграція в інший дата-центр) і гарантує суворе **RPO = 0** без примусового знеструмлення через STONITH.

Процедура планового перемикання виконується за строго детермінованим протоколом:
1. **Ініціація:** Адміністратор або CI/CD пайплайн надсилає HTTP POST-запит на кінцеву точку `/switchover` активного лідера з вказівкою імені цільового кандидата.
2. **Блокування запису на старому лідері:** Лідер переводить локальний PostgreSQL у стан `READ ONLY` або скидає сесії через PgBouncer `PAUSE`.
3. **Фіксація контрольної точки:** Лідер виконує виклик `SELECT pg_switch_wal();` та фіксує точний фінальний LSN журналу (наприклад, `0/1B000000`).
4. **Очікування застосування (Catch-Up Barrier):** Координатор опитує цільову репліку через функцію `pg_last_wal_replay_lsn()`, поки її позиція не досягне значення `0/1B000000`. Це гарантує нульову втрату зафіксованих даних.
5. **Добровільне звільнення лізу:** Старий лідер видаляє свій запис у DCS або передає ключ безпосередньо кандидату через атомарну транзакцію CAS.
6. **Промоушен цільового вузла:** Репліка виконує `pg_promote()` і стає новим Primary.
7. **Перепідключення старого лідера:** Старий лідер перезапускається як звичайна репліка `Standby` і починає транслювати журнал від нового Primary без виклику `pg_rewind` (оскільки історії таймлайнів не розійшлися).

## Тестування відмовостійкості (Chaos Engineering)

Надійність конфігурації високої доступності неможливо перевірити аналітично без проведення регулярних ін'єкцій хаосу у тестовому середовищі:
1. **Імітація апаратного знеструмлення (Kernel Crash):** Виконання команди `echo b > /proc/sysrq-trigger` на активному лідері викликає миттєве перезавантаження ядра без скидання буферів файлової системи. Тест перевіряє коректність детекції аварії за таймаутом `TTL` та успішність промоушену репліки.
2. **Імітація розриву мережі (Network Partition):** Виконання правил фільтрації iptables `iptables -A INPUT -p tcp --dport 2379 -j DROP` (блокування зв'язку з etcd) або додавання штучної затримки через планувальник трафіку ядра `tc qdisc add dev eth0 root netem delay 8000ms`. Тест перевіряє, чи своєчасно старий лідер знімає з себе повноваження (Demotion) і чи не виникає подвійний запис.
3. **Імітація зависання диска (I/O Freeze):** Заморожування операцій введення-виведення через утиліту `dmsetup suspend` на розділі з журналом WAL. Тест перевіряє роботу сторожового таймера `/dev/watchdog` та автоматичне спрацьовування апаратного перезавантаження.

## Інженерні пастки реалізації відмовостійкості

Практична експлуатація автоматичних оркестраторів failover пов'язана з низкою тонких крайових випадків, нехтування якими призводить до розпаду кластера або пошкодження даних.

### 1. Пастка мертвої точки годинника (Monotonic Clock vs Wall-Clock)
Усі обчислення лізингу та таймаутів зобов'язані спиратися виключно на монотонний таймер (`CLOCK_MONOTONIC` у C або `std::chrono::steady_clock` у C++).
Використання системного годинника реального часу (`CLOCK_REALTIME` або `gettimeofday()`) є фатальною помилкою: якщо демон синхронізації часу NTP коригує час стрибком назад (наприклад, на 3 секунди через дрейф або переведення високосної секунди), активний лідер помилково вирішить, що його ліз продовжився, тоді як DCS на інших серверах уже вважатиме його протермінованим. Це гарантовано спричиняє split-brain.

### 2. Розбіжність точок таймлайну (Timeline Branching)
Під час промоушену репліка створює новий логічний таймлайн (наприклад, Timeline 2), записуючи спеціальну мітку `CHECKPOINT` у журнал WAL. Якщо старий лідер після відновлення повертається в мережу, його локальний журнал WAL на таймлайні 1 містить транзакції, яких немає на новому лідері. Спроба просто запустити потокову реплікацію завершиться помилкою несумісності історії.
Для безпечної інтеграції старого лідера назад у кластер застосовують утиліту `pg_rewind`:
1. `pg_rewind` сканує журнал WAL нового лідера і знаходить спільну точку розгалуження (англ. *fork point*).
2. Усі блоки даних, змінені старим лідером після моменту розгалуження, перезаписуються актуальними блоками з нового лідера.
3. Вузол підключається до нового лідера як звичайна репліка без необхідності повторного повного копіювання терабайтів даних (Base Backup).

### 3. Завислі клієнтські транзакції та інтеграція з пулом з'єднань (PgBouncer Pause)
Просте перемикання ролей на рівні бази даних є неповним без коректного управління активними клієнтськими TCP-з'єднаннями. Якщо клієнти продовжують надсилати запити в момент виборів, вони отримують помилки `Connection refused` або `Cannot execute INSERT in read-only transaction`.

Для забезпечення безшовного перемикання координатор взаємодіє з пулом з'єднань PgBouncer через адміністративний сокет:
1. Перед початком планового перемикання або промоушену координатор надсилає команду `PAUSE <database_name>;`. PgBouncer припиняє передачу нових запитів до бекенду СКБД, акумулюючи вхідні клієнтські пакети у внутрішньому буфері пам'яті (клієнти бачать лише невелике збільшення затримки відповіді без розриву сокета).
2. Координатор виконує промоушен репліки, переконується у відкритті режиму Read-Write і оновлює адресу бекенду в конфігурації PgBouncer.
3. Надсилається команда `RELOAD;` та `RESUME <database_name>;`. PgBouncer миттєво скидає накопичені запити на нового лідера. Клієнтські застосунки продовжують роботу без жодного перепідключення.

### 4. Errant-транзакції у світі MySQL та GTID
У кластерах MySQL на базі реплікації GTID критичною небезпекою є так звані блукаючі транзакції (англ. *Errant Transactions*). Якщо інженер або локальний скрипт випадково виконав модифікуючий запит (наприклад, `ANALYZE TABLE` або вставку технічного рядка) безпосередньо на репліці при вимкненому параметрі `read_only`, цій транзакції присвоюється локальний GTID, відсутній у журналі лідера.

Якщо таку репліку буде підвищено до лідера під час failover, інші репліки не зможуть підключитися до неї: механізм реплікації MySQL виявить пропущену транзакцію в ланцюгу і зупинить потік реплікації з фатальною помилкою. Сучасні координатори (такі як GitHub Orchestrator) перед промоушеном перевіряють множину `Executed_Gtid_Set` кандидата: вузли з errant-транзакціями автоматично дискваліфікуються з виборів до очищення некоректних транзакцій через ін'єкцію порожніх подій (`GTID_NEXT`).
