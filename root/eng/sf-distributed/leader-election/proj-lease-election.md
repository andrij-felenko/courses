# ⚙️ Реалізація виборів лідера на базі ліз і фенсингових токенів

У розподілених архітектурах мікросервіси та воркери фонової обробки зазвичай розгортаються у вигляді кількох еквівалентних реплік (наприклад, трьох або п'яти подів у Kubernetes). Більшість запитів на читання та запис вони обробляють паралельно, проте виконання критичних монопольних операцій — періодичного білінгу, генерації звітів, координації перерозподілу розділів або міграції схем даних — вимагає призначення **рівно одного активного лідера**.

Цей практичний проєкт розбирає повну, промислову реалізацію клієнта виборів лідера на основі **механізму ліз (Lease-Based Leader Election)** та **монотонних фенсингових токенів (Fencing Tokens)**.

---

## 1. Архітектурна модель клієнта та скінченний автомат

Клієнт виборів лідера взаємодіє з розподіленим транзакційним координатором (аналогом etcd, Consul або Kubernetes Lease API) та реалізує скінченний автомат із трьома основними станами:

1. **`STANDBY` (Очікування / Кандидат):** Вузол є пасивним спостерігачем. Він не виконує монопольних фонових обов'язків, але повністю працездатний для обробки звичайного stateless-трафіку (наприклад, HTTP-запитів клієнтів). Вузол періодично намагається захопити лізу або встановлює тригер спостереження (Watch) на ключ лізи в координаторі.
2. **`LEADER` (Активний лідер):** Вузол успішно створив або перехопив ключ лізи в координаторі за допомогою атомарної операції Compare-And-Swap (CAS). Він отримує монотонний номер епохи (`fencing_token`), запускає фоновий потік оновлення лізи (Keep-Alive) та активує бізнес-задачі лідера, передаючи їм токен скасування (`cancellation_token`).
3. **`LEADER_LOST / RESIGNED` (Втрата лідерства або складання повноважень):** Якщо мережева затримка, збій зв'язку або локальна пауза виконання завадили поновити лізу до спливання дедлайну, клієнт негайно ініціює аварійне скасування бізнес-задач, дочікується зупинки корисного навантаження та повертається до стану `STANDBY`.

```
                  ┌────────────────────────┐
                  │        STANDBY         │
                  │  (періодичні спроби)   │
                  └───────────┬────────────┘
                              │
               Успішне захоплення лізи (CAS)
               Отримання fencing_token (e)
                              │
                              ▼
                  ┌────────────────────────┐
     ┌───────────►│         LEADER         │
     │            │  (виконання + KeepAlive)
     │            └───────────┬────────────┘
KeepAlive успішний            │
(оновлення лізи)              │ Таймаут оновлення лізи
     │                        │ або явний вихід (StepDown)
     └────────────────────────┴────────────┐
                                           ▼
                              ┌────────────────────────┐
                              │     LEADER_LOST        │
                              │  (аварійне скасування) │
                              └────────────┬───────────┘
                                           │
                                  Очищення ресурсів
                                           │
                                           ▼
                                    (повернення до
                                       STANDBY)
```

---

## 2. Розрахунок бюджету часу та інваріанти надійності

Надійність виборів лідера на базі ліз спирається на сувору математичну узгодженість чотирьох часових констант:

1. **`TTL` (Час життя лізи / Lease Duration):** Тривалість, на яку координатор резервує право власності за вузлом (наприклад, `TTL = 15` секунд). Якщо за цей час жодного поновлення не надійшло, координатор автоматично видаляє або звільняє ключ.
2. **`T_renew` (Інтервал поновлення / Renew Interval):** Періодичність, із якою активний лідер шле повідомлення серцебиття (Keep-Alive). Промисловим стандартом є вибір `T_renew <= TTL / 3`. При `TTL = 15` с інтервал надсилання становить `5` секунд. Це гарантує, що лідер має щонайменше дві спроби повторного запиту у разі втрати одиничного мережевого пакета.
3. **`T_deadline` (Дедлайн поновлення / Renew Deadline):** Внутрішній ліміт часу на очікування відповіді від координатора. Якщо за `T_deadline = TTL * 2 / 3` (наприклад, 10 секунд) лідер не отримав підтвердження від координатора, він **самостійно і негайно** позбавляє себе повноважень, не чекаючи, поки координатор скине його статус. Це створює 5-секундний захисний буфер безпеки на випадок затримки зупинки фонових потоків.
4. **`T_retry` (Період опитування претендентів / Retry Period):** Інтервал, з яким вузли у стані `STANDBY` надсилають запити на захоплення лізи (зазвичай `T_retry = TTL / 4` або 2–3 секунди).

Усі вимірювання інтервалів усередині процесу повинні використовувати строго **монотонний годинник** (`CLOCK_MONOTONIC` у POSIX, `std::chrono::steady_clock` у C++). Використання настінного календарного часу (`CLOCK_REALTIME` / `gettimeofday`) є критичною помилкою: якщо демон NTP скоригує час назад під час роботи лідера, різниця часів стане від'ємною або занадто великою, що спричинить передчасне скидання або помилкове утримання лідерства.

---

## 3. Програмна реалізація

Нижче наведено повні, самодостатні реалізації клієнта виборів лідера мовами C (стандарт POSIX) та C++ (сучасний C++20). Вони містять імітатор атомарного сховища ліз із перевіркою версій (Compare-And-Swap), життєвий цикл фонових потоків, обробку аварійної втрати лізи та захист цільового сховища за допомогою фенсингового токена.

:::tabs
```c
/* leader_elector.c - Промислова реалізація виборів лідера мовою C (POSIX) */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>
#include <errno.h>

/* --- Імітатор розподіленого координатора консенсусу (etcd / Consul) --- */

typedef struct {
    pthread_mutex_t lock;
    char leader_id[64];
    uint64_t fencing_token;    /* Монотонний лічильник епох (ревізія) */
    struct timespec expiry_ts; /* Момент закінчення лізи на монотонному годиннику */
    bool is_allocated;
} mock_coordinator_t;

static mock_coordinator_t g_coordinator = {
    .lock = PTHREAD_MUTEX_INITIALIZER,
    .leader_id = {0},
    .fencing_token = 0,
    .is_allocated = false
};

/* Отримати поточний час монотонного годинника в мілісекундах */
static int64_t get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000 + (ts.tv_nsec / 1000000);
}

/* Спроба атомарного захоплення лізи (Compare-And-Swap) */
static bool coordinator_try_acquire(const char* candidate_id, uint32_t ttl_ms, uint64_t* out_token) {
    pthread_mutex_lock(&g_coordinator.lock);
    int64_t now = get_monotonic_ms();
    int64_t expiry = (int64_t)g_coordinator.expiry_ts.tv_sec * 1000 + (g_coordinator.expiry_ts.tv_nsec / 1000000);

    bool can_acquire = false;
    if (!g_coordinator.is_allocated || now >= expiry) {
        /* Ліза вільна або прострочена -> захоплюємо */
        can_acquire = true;
    } else if (strcmp(g_coordinator.leader_id, candidate_id) == 0) {
        /* Вже є лідером -> поновлюємо */
        can_acquire = true;
    }

    if (can_acquire) {
        strncpy(g_coordinator.leader_id, candidate_id, sizeof(g_coordinator.leader_id) - 1);
        g_coordinator.fencing_token++;
        *out_token = g_coordinator.fencing_token;
        g_coordinator.is_allocated = true;

        int64_t new_expiry = now + ttl_ms;
        g_coordinator.expiry_ts.tv_sec = new_expiry / 1000;
        g_coordinator.expiry_ts.tv_nsec = (new_expiry % 1000) * 1000000;
    }

    pthread_mutex_unlock(&g_coordinator.lock);
    return can_acquire;
}

/* Поновлення наявної лізи (Keep-Alive) */
static bool coordinator_renew_lease(const char* leader_id, uint64_t token, uint32_t ttl_ms) {
    pthread_mutex_lock(&g_coordinator.lock);
    int64_t now = get_monotonic_ms();
    int64_t expiry = (int64_t)g_coordinator.expiry_ts.tv_sec * 1000 + (g_coordinator.expiry_ts.tv_nsec / 1000000);

    bool ok = false;
    if (g_coordinator.is_allocated &&
        now < expiry &&
        strcmp(g_coordinator.leader_id, leader_id) == 0 &&
        g_coordinator.fencing_token == token) {
        
        int64_t new_expiry = now + ttl_ms;
        g_coordinator.expiry_ts.tv_sec = new_expiry / 1000;
        g_coordinator.expiry_ts.tv_nsec = (new_expiry % 1000) * 1000000;
        ok = true;
    }
    pthread_mutex_unlock(&g_coordinator.lock);
    return ok;
}

/* Явне звільнення лізи (Graceful Resign) */
static void coordinator_resign(const char* leader_id, uint64_t token) {
    pthread_mutex_lock(&g_coordinator.lock);
    if (g_coordinator.is_allocated &&
        strcmp(g_coordinator.leader_id, leader_id) == 0 &&
        g_coordinator.fencing_token == token) {
        g_coordinator.is_allocated = false;
        memset(g_coordinator.leader_id, 0, sizeof(g_coordinator.leader_id));
    }
    pthread_mutex_unlock(&g_coordinator.lock);
}

/* --- Захищене сховище з перевіркою фенсингового токена --- */

typedef struct {
    pthread_mutex_t lock;
    uint64_t last_seen_token;
    int balance;
} mock_storage_t;

static mock_storage_t g_storage = {
    .lock = PTHREAD_MUTEX_INITIALIZER,
    .last_seen_token = 0,
    .balance = 1000
};

static bool storage_mutate(uint64_t token, int delta, const char* caller_id) {
    pthread_mutex_lock(&g_storage.lock);
    if (token < g_storage.last_seen_token) {
        printf("[%s] ВІДХИЛЕНО: Токен %lu застарілий! Останній прийнятий: %lu\n",
               caller_id, (unsigned long)token, (unsigned long)g_storage.last_seen_token);
        pthread_mutex_unlock(&g_storage.lock);
        return false;
    }
    g_storage.last_seen_token = token;
    g_storage.balance += delta;
    printf("[%s] УСПІХ: Мутація з токеном %lu прийнята. Баланс = %d\n",
           caller_id, (unsigned long)token, g_storage.balance);
    pthread_mutex_unlock(&g_storage.lock);
    return true;
}

/* --- Клієнтський модуль виборів лідера --- */

typedef struct {
    char node_id[64];
    uint32_t lease_ttl_ms;
    uint32_t renew_interval_ms;
    uint32_t retry_interval_ms;

    volatile bool running;
    volatile bool is_leading;
    volatile bool cancel_payload;
    uint64_t current_token;

    pthread_t election_thread;
    pthread_t payload_thread;
    pthread_mutex_t state_lock;
} leader_elector_t;

/* Фонова корисна робота активного лідера */
static void* leader_payload_worker(void* arg) {
    leader_elector_t* elector = (leader_elector_t*)arg;
    printf("[%s] Лідер розпочав виконання монопольних бізнес-задач.\n", elector->node_id);

    while (elector->running && elector->is_leading && !elector->cancel_payload) {
        /* Виконуємо транзакцію білінгу раз на 800 мс */
        storage_mutate(elector->current_token, 50, elector->node_id);
        usleep(800000);
    }

    printf("[%s] Лідер зупинив виконання бізнес-задач (cancel=%d).\n",
           elector->node_id, elector->cancel_payload);
    return NULL;
}

/* Основний цикл управління лідерством */
static void* election_loop(void* arg) {
    leader_elector_t* elector = (leader_elector_t*)arg;

    while (elector->running) {
        if (!elector->is_leading) {
            /* Стан STANDBY: пробуємо захопити лізу */
            uint64_t token = 0;
            if (coordinator_try_acquire(elector->node_id, elector->lease_ttl_ms, &token)) {
                pthread_mutex_lock(&elector->state_lock);
                elector->is_leading = true;
                elector->cancel_payload = false;
                elector->current_token = token;
                printf(">>> [%s] СТАВ ЛІДЕРОМ! Отримано Fencing Token = %lu <<<\n",
                       elector->node_id, (unsigned long)token);
                
                pthread_create(&elector->payload_thread, NULL, leader_payload_worker, elector);
                pthread_mutex_unlock(&elector->state_lock);
            } else {
                usleep(elector->retry_interval_ms * 1000);
            }
        } else {
            /* Стан LEADER: оновлюємо лізу (Keep-Alive) */
            usleep(elector->renew_interval_ms * 1000);

            if (!elector->running) break;

            if (!coordinator_renew_lease(elector->node_id, elector->current_token, elector->lease_ttl_ms)) {
                /* Втрата лізи через таймаут або збій */
                printf("!!! [%s] ВТРАТА ЛІДЕРСТВА: Не вдалося поновити лізу! !!!\n", elector->node_id);

                pthread_mutex_lock(&elector->state_lock);
                elector->is_leading = false;
                elector->cancel_payload = true;
                pthread_mutex_unlock(&elector->state_lock);

                pthread_join(elector->payload_thread, NULL);
            }
        }
    }

    if (elector->is_leading) {
        coordinator_resign(elector->node_id, elector->current_token);
        elector->is_leading = false;
        elector->cancel_payload = true;
        pthread_join(elector->payload_thread, NULL);
    }
    return NULL;
}

void leader_elector_init(leader_elector_t* elector, const char* id, uint32_t ttl_ms) {
    strncpy(elector->node_id, id, sizeof(elector->node_id) - 1);
    elector->lease_ttl_ms = ttl_ms;
    elector->renew_interval_ms = ttl_ms / 3;     /* Серцебиття раз на 1/3 TTL */
    elector->retry_interval_ms = ttl_ms / 4;
    elector->running = true;
    elector->is_leading = false;
    elector->cancel_payload = false;
    elector->current_token = 0;
    pthread_mutex_init(&elector->state_lock, NULL);
    pthread_create(&elector->election_thread, NULL, election_loop, elector);
}

void leader_elector_stop(leader_elector_t* elector) {
    elector->running = false;
    pthread_join(elector->election_thread, NULL);
    pthread_mutex_destroy(&elector->state_lock);
}

/* Демонстрація відмови лідера та захисту токеном */
int main(void) {
    printf("=== Старт кластера виборів лідера ===\n");
    leader_elector_t node_a, node_b;

    leader_elector_init(&node_a, "Вузол-A", 1500); /* TTL = 1.5 секунди */
    usleep(200000);
    leader_elector_init(&node_b, "Вузол-B", 1500);

    /* Даємо Вузлу-A попрацювати лідером 2.5 секунди */
    sleep(2);

    printf("\n--- Імітація аварійної GC-паузи / зависання Вузла-A на 3 секунди ---\n");
    /* Примусово блокуємо роботу Вузла-A (імітація freeze) */
    pthread_mutex_lock(&node_a.state_lock);
    sleep(3); /* Вузол-B за цей час перехопить лідерство і виконає мутацію */
    pthread_mutex_unlock(&node_a.state_lock);

    sleep(2);

    leader_elector_stop(&node_a);
    leader_elector_stop(&node_b);
    printf("=== Роботу кластера завершено ===\n");
    return 0;
}
```
```cpp
// leader_elector.cpp - Промислова реалізація виборів лідера на C++20
#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <mutex>
#include <atomic>
#include <memory>
#include <functional>
#include <optional>
#include <stop_token>

using namespace std::chrono_literals;

/* --- Імітатор розподіленого координатора консенсусу (etcd / Consul) --- */
class MockCoordinator {
public:
    struct LeaseGrant {
        uint64_t fencing_token;
        bool granted;
    };

    static MockCoordinator& instance() {
        static MockCoordinator inst;
        return inst;
    }

    LeaseGrant try_acquire(std::string_view candidate_id, std::chrono::milliseconds ttl) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto now = std::chrono::steady_clock::now();

        bool can_acquire = false;
        if (!is_allocated_ || now >= expiry_time_) {
            can_acquire = true;
        } else if (current_leader_ == candidate_id) {
            can_acquire = true;
        }

        if (can_acquire) {
            current_leader_ = candidate_id;
            fencing_token_++;
            is_allocated_ = true;
            expiry_time_ = now + ttl;
            return {fencing_token_, true};
        }
        return {0, false};
    }

    bool renew_lease(std::string_view leader_id, uint64_t token, std::chrono::milliseconds ttl) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto now = std::chrono::steady_clock::now();

        if (is_allocated_ && now < expiry_time_ &&
            current_leader_ == leader_id && fencing_token_ == token) {
            expiry_time_ = now + ttl;
            return true;
        }
        return false;
    }

    void resign(std::string_view leader_id, uint64_t token) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (is_allocated_ && current_leader_ == leader_id && fencing_token_ == token) {
            is_allocated_ = false;
            current_leader_.clear();
        }
    }

private:
    std::mutex mutex_;
    std::string current_leader_;
    uint64_t fencing_token_{0};
    std::chrono::steady_clock::time_point expiry_time_;
    bool is_allocated_{false};
};

/* --- Захищене цільове сховище з валідацією фенсингового токена --- */
class ProtectedStorage {
public:
    static ProtectedStorage& instance() {
        static ProtectedStorage inst;
        return inst;
    }

    bool mutate(uint64_t token, int delta, std::string_view caller_id) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (token < last_seen_token_) {
            std::cout << "[" << caller_id << "] ВІДХИЛЕНО: Токен " << token
                      << " застарілий! Чинний токен: " << last_seen_token_ << "\n";
            return false;
        }
        last_seen_token_ = token;
        balance_ += delta;
        std::cout << "[" << caller_id << "] УСПІХ: Мутація з токеном " << token
                  << " зафіксована. Баланс = " << balance_ << "\n";
        return true;
    }

private:
    std::mutex mutex_;
    uint64_t last_seen_token_{0};
    int balance_{1000};
};

/* --- Клієнтський клас управління життєвим циклом лідера --- */
class LeaderElector {
public:
    using PayloadFunc = std::function<void(std::stop_token, uint64_t)>;

    LeaderElector(std::string node_id, std::chrono::milliseconds lease_ttl, PayloadFunc payload)
        : node_id_(std::move(node_id)),
          lease_ttl_(lease_ttl),
          renew_interval_(lease_ttl / 3),
          retry_interval_(lease_ttl / 4),
          payload_func_(std::move(payload)) {
        
        election_thread_ = std::jthread([this](std::stop_token st) {
            run_election_loop(st);
        });
    }

    ~LeaderElector() {
        stop();
    }

    void stop() {
        if (election_thread_.joinable()) {
            election_thread_.request_stop();
            election_thread_.join();
        }
    }

    bool is_leader() const noexcept {
        return is_leading_.load(std::memory_order_relaxed);
    }

private:
    void run_election_loop(std::stop_token st) {
        while (!st.stop_requested()) {
            if (!is_leading_.load(std::memory_order_relaxed)) {
                // Стан STANDBY: намагаємося захопити лізу
                auto grant = MockCoordinator::instance().try_acquire(node_id_, lease_ttl_);
                if (grant.granted) {
                    current_token_ = grant.fencing_token;
                    is_leading_.store(true, std::memory_order_release);
                    std::cout << ">>> [" << node_id_ << "] СТАВ ЛІДЕРОМ! Fencing Token = "
                              << current_token_ << " <<<\n";

                    // Запускаємо корисну роботу лідера у фоновому потоці
                    payload_thread_ = std::jthread([this, token = current_token_](std::stop_token payload_st) {
                        if (payload_func_) {
                            payload_func_(payload_st, token);
                        }
                    });
                } else {
                    std::this_thread::sleep_for(retry_interval_);
                }
            } else {
                // Стан LEADER: оновлюємо лізу
                std::this_thread::sleep_for(renew_interval_);
                if (st.stop_requested()) break;

                bool renewed = MockCoordinator::instance().renew_lease(node_id_, current_token_, lease_ttl_);
                if (!renewed) {
                    std::cout << "!!! [" << node_id_ << "] ВТРАТА ЛІДЕРСТВА: Keep-Alive провалився! !!!\n";
                    is_leading_.store(false, std::memory_order_release);

                    // Зупиняємо бізнес-потік
                    if (payload_thread_.joinable()) {
                        payload_thread_.request_stop();
                        payload_thread_.join();
                    }
                }
            }
        }

        // Акуратне складання повноважень при завершенні роботи
        if (is_leading_.load(std::memory_order_relaxed)) {
            MockCoordinator::instance().resign(node_id_, current_token_);
            is_leading_.store(false, std::memory_order_release);
            if (payload_thread_.joinable()) {
                payload_thread_.request_stop();
                payload_thread_.join();
            }
        }
    }

    std::string node_id_;
    std::chrono::milliseconds lease_ttl_;
    std::chrono::milliseconds renew_interval_;
    std::chrono::milliseconds retry_interval_;
    PayloadFunc payload_func_;

    std::atomic<bool> is_leading_{false};
    uint64_t current_token_{0};

    std::jthread election_thread_;
    std::jthread payload_thread_;
};

/* --- Точка входу: демонстрація відмови та захисту токенами --- */
int main() {
    std::cout << "=== Запуск кластера виборів лідера (C++20) ===\n";

    auto business_logic = [](std::stop_token st, uint64_t token) {
        while (!st.stop_requested()) {
            ProtectedStorage::instance().mutate(token, 100, "АктивнийЛідер");
            std::this_thread::sleep_for(600ms);
        }
    };

    LeaderElector node_1("Вузол-1", 1200ms, business_logic);
    std::this_thread::sleep_for(200ms);
    LeaderElector node_2("Вузол-2", 1200ms, business_logic);

    // Вузол-1 захоплює лідерство і працює 2 секунди
    std::this_thread::sleep_for(2s);

    std::cout << "\n--- Імітація аварійного відключення Вузла-1 ---\n";
    node_1.stop(); // Вузол-1 зупиняється без поновлення лізи

    // Вузол-2 виявляє прострочення лізи та стає новим лідером
    std::this_thread::sleep_for(3s);

    std::cout << "=== Завершення роботи кластера ===\n";
    return 0;
}
```
:::

---

## 4. Детальний аналіз інженерних механізмів

### 1. Механіка атомарного оновлення лізи та захист від гонитви (Race Conditions)

У наведеній реалізації координатора операція оновлення лізи `renew_lease` обов'язково перевіряє не лише ім'я вузла `leader_id`, а й поточний номер фенсингового токена `fencing_token == token`. Це запобігає класичній аномалії відкладеного серцебиття:

- Вузол А утримував лізу з токеном `e = 1`.
- Вузол А потрапив у мережеву затримку, і пакет із запитом на оновлення завис у черзі маршрутизатора.
- Координатор анулював лізу через таймаут TTL і передав її Вузлу Б із токеном `e = 2`.
- Затриманий пакет від Вузла А раптово долітає до координатора.

Якби координатор перевіряв лише ім'я чи просте продовження часу, він міг би помилково поновити лізу для старого лідера. Обов'язкова валідація токена гарантує, що запит із застарілим номером `e = 1` негайно відхиляється, оскільки координатор уже перевів ревізію на значення `e = 2`.

### 2. Кооперативне скасування через `std::stop_token` проти примусового завершення

Зупинка фонового потоку лідера (`payload_thread`) під час втрати лідерства або штатного завершення процесу не повинна виконуватися через асинхронні системні виклики на кшталт `pthread_cancel` або `SIGKILL`. Примусове припинення потоку посеред виконання транзакції залишає відкритими м'ютекси, розриває сокети в непередбачуваному стані та може призвести до взаємного блокування (Deadlock) всього процесу.

Натомість використовується механізм **кооперативного скасування (Cooperative Cancellation)**:
1. Потік керування лідерством виставляє атомарний прапорець `is_leading = false` та надсилає сигнал скасування `request_stop()`.
2. Робочий потік бізнес-логіки перевіряє стан `st.stop_requested()` на кожній ітерації циклу та перед кожною операцією вводу-виводу.
3. Робочий потік завершує поточну неподільну дію, коректно закриває локальні транзакційні ресурси і виходить із функції.
4. Потік керування виконує синхронне очікування завершення через `join()`, гарантуючи, що жоден фоновий потік старого лідера більше не звернеться до зовнішнього сховища.

### 3. Модель пам'яті та бар'єри синхронізації

У C++20 версії прапорець `is_leading_` оголошено як `std::atomic<bool>`. При зміні стану використовується семантика `std::memory_order_release`, а при перевірці — `std::memory_order_acquire` (або `memory_order_relaxed` усередині циклу).

Це встановлює відношення **синхронізації пам'яті (Synchronizes-With)** між потоком обрання та робочим потоком: усі записи в змінні `current_token_` та супутні контекстні структури, виконані потоком виборів до встановлення `is_leading = true`, гарантовано стають видимими для робочого потоку без використання важких м'ютексів на гарячому шляху.

У C-реалізації для досягнення аналогічної коректності пам'яті використовується м'ютекс `state_lock`, який забезпечує повний апаратний бар'єр пам'яті (Memory Fence) під час модифікації та читання полів структури `leader_elector_t`.

### 4. Інтеграція фенсингового токена в реляційні та документні бази даних

У реальних виробничих системах захищене сховище (`ProtectedStorage`) зазвичай представлене базою даних PostgreSQL, MySQL або Amazon DynamoDB. Захист від зомбі-лідера на рівні SQL реалізується через умовні оператори `UPDATE` з оптимістичною перевіркою версії:

```sql
-- Таблиця стану координації білінгу
-- Стовпець last_fencing_token містить максимальний зареєстрований номер епохи

UPDATE billing_execution_state
SET 
    last_processed_id = 894520,
    last_fencing_token = 42,
    updated_at = NOW()
WHERE 
    service_name = 'payment-aggregator' 
    AND last_fencing_token <= 42;
```

Якщо старий зомбі-лідер прокинеться після глибокої паузи збирання сміття і спробує виконати такий запит зі своїм застарілим токеном `41`, умова `WHERE last_fencing_token <= 41` поверне `0` оновлених рядків (`Rows Affected = 0`). Прикладний код старого лідера негайно виявляє відхилення операції базою даних, перериває подальшу роботу та ініціює перезапуск власного циклу виборів.

В об'єктних сховищах типу Amazon S3 або Google Cloud Storage аналогічний захист реалізується за допомогою умовних заголовків `If-Match` з ETag або записом метаданих з монотонним номером версії, що унеможливлює перезапис свіжих результатів застарілими артефактами.

---

## 5. Альтернативні координатори: бази даних та NoSQL-сховища

Якщо в інфраструктурі немає виділеного кластера etcd чи ZooKeeper, вибори лідера можна реалізувати на базі наявної СКБД:

### 1. Консультативні блокування PostgreSQL (Advisory Locks)
PostgreSQL підтримує сесійні консультативні блокування рівня з'єднання:
```sql
-- Спроба захопити лідерство без блокування виклику (повертає true або false)
SELECT pg_try_advisory_lock(hashtext('payment-scheduler-leader'));
```
- **Як працює:** Якщо з'єднання з базою активне, блокування утримується. Якщо сервер-лідер падає, операційна система закриває TCP-сокет, PostgreSQL автоматично звільняє блокування, і інший вузол кластера успішно виконує `pg_try_advisory_lock`.
- **Обмеження:** Не має вбудованого механізму монотонного фенсингового токена (його слід вести в окремій таблиці) та вразливе до залипання з'єднань у пулах проксі (PgBouncer у режимі транзакцій не підтримує сесійні блокування).

### 2. Умовні записи DynamoDB з часом життя (Conditional Writes + TTL)
У хмарі AWS вибори лідера часто будують поверх Amazon DynamoDB:
```json
{
  "TableName": "LeaderLocks",
  "Item": {
    "LockKey": {"S": "billing-service"},
    "Owner": {"S": "pod-17"},
    "LeaseExpiry": {"N": "1710934850"},
    "FencingToken": {"N": "105"}
  },
  "ConditionExpression": "attribute_not_exists(LockKey) OR LeaseExpiry < :now OR Owner = :my_id"
}
```
Кожен запит на оновлення інкрементує `FencingToken` і встановлює новий `LeaseExpiry`. База даних виконує атомарну перевірку умови на рівні власного консенсусу (Multi-Paxos), гарантуючи єдиного власника лізи.

---

## 6. Порівняння протоколів поновлення: gRPC-стримінг проти HTTP-опитування

У сучасних розподілених координаторах зв'язок між клієнтом і сервером реалізується двома різними способами:

1. **Мультиплексований двоспрямований gRPC-потік (etcd `LeaseKeepAlive`):**
   Клієнт відкриває єдине довгоживуче HTTP/2 з'єднання. Оновлення лізи здійснюється відправкою 8-байтового ідентифікатора лізи у вже відкритий потік.
   - **Перевага:** Мінімальний накладний трафік (немає TCP-рукостискань та TLS-узгоджень на кожен запит). Затримка поновлення становить субмілісекунди.
   - **Пастка:** При розриві TCP-з'єднання (наприклад, скиданні сесії файрволом) клієнт повинен негайно перевизначити стан потоку і повторно підключитися до іншого вузла кластера etcd до вичерпання дедлайну `T_deadline`.

2. **Періодичні атомарні HTTP/REST-запити (Kubernetes Lease API, Consul HTTP API):**
   Клієнт відправляє стандартний `PUT` або `PATCH` запит із тілом маніфесту лізи, що містить поточний час оновлення (`renewTime`) та ідентифікатор власника (`holderIdentity`).
   - **Перевага:** Повна незалежність від стану окремого сокета; запит може бути відправлений через будь-який балансувальник або проксі.
   - **Пастка:** Значно вище навантаження на API-сервер координатора при великій кількості реплік сервісу.

---

## 7. Простеження аварійних сценаріїв у продакшені

Щоб побачити, як взаємодіють усі описані механізми під час реального інциденту, розглянемо покроковий хронометраж поведінки трьох вузлів сервісу обробки фінансових платежів у хмарі:

| Час (мс) | Вузол 1 (Лідер) | Координатор (etcd) | Вузол 2 (Стендбай) | База даних (Сховище) |
| :--- | :--- | :--- | :--- | :--- |
| **0** | Захопив лізу (TTL=15 с), токен `e=101`. Запустив обробку. | Створено ключ лізи. Власник: Вузол 1, епоха `101`. | Перейшов у стан `STANDBY`, слухає ключ. | `last_fencing_token = 101`. |
| **5000** | Надіслав Keep-Alive. | Лізу поновлено на 15 с (до 20 000 мс). | Очікує. | Приймає платежі з токеном `101`. |
| **7000** | Потрапив у глибоку GC-паузу (Stop-The-World на 18 с). | Очікує серцебиття. | Очікує. | Спокійний стан. |
| **10000** | Завислий (пропустив Keep-Alive на 10 000 мс). | Очікує (таймаут ще не вичерпано). | Очікує. | Спокійний стан. |
| **15000** | Завислий (пропустив другий Keep-Alive). | Очікує (дедлайн 20 000 мс). | Очікує. | Спокійний стан. |
| **20000** | Завислий. | **Таймаут TTL!** Ключ лізи видалено. Сповіщення надіслано підписникам. | Отримав подію видалення лізи. Негайно шле CAS `try_acquire`. | Спокійний стан. |
| **20050** | Завислий. | Прийняв запит Вузла 2. Видав лізу, токен `e=102`. | **Став лідером!** Токен `e=102`. Запустив обробку. | Спокійний стан. |
| **21000** | Завислий. | Отримує Keep-Alive від Вузла 2. | Виконує платіж TX-999 із токеном `102`. | **УСПІХ!** Записано `last_fencing_token = 102`. |
| **25000** | **Прокинувся від GC-паузи!** Локальний контекст ще містить `is_leading=true`. Шле відкладений платіж із токеном `101`. | Відхилив старий Keep-Alive від Вузла 1. | Працює штатно як лідер. | **ВІДХИЛЕНО!** Перевірка `101 < 102` заблокувала запис зомбі-лідера! |
| **25050** | Отримав відмову від БД та помилку від координатора. Викликав `request_stop()`, перейшов у `STANDBY`. | Утримує лізу Вузла 2. | Працює штатно. | Цілісність даних повністю збережена. |

Ця хронологія наочно демонструє, що лізи забезпечують автоматичне відновлення доступності (Liveness), тоді як фенсингові токени гарантують абсолютну безпеку та узгодженість даних (Safety).

---

## 8. Моніторинг та метрики здоров'я виборів лідера

У промисловій експлуатації кожен екземпляр сервісу експортує стандартний набір Prometheus-метрик для безперервного спостереження за станом виборів:

1. **`leader_election_master_status{name="billing"}` (Gauge: 0 або 1):** Показує, чи вважає даний конкретний екземпляр себе активним лідером. Сума цієї метрики по всіх подах кластера повинна бути **строго рівною 1**. Якщо сума дорівнює 0 — кластер не має лідера; якщо більше 1 — виникла аномалія подвійного лідерства, яка вимагає негайного сповіщення чергових інженерів.
2. **`leader_election_lease_renew_duration_seconds` (Histogram):** Затримка виконання запитів на поновлення лізи (Keep-Alive). Якщо 99-й перцентиль (p99) наближається до `T_renew`, це сигналізує про перевантаження координатора або проблеми мережі задовго до аварійного скидання лідерства.
3. **`leader_election_transitions_total` (Counter):** Загальна кількість змін лідерів у кластері. Швидке зростання лічильника вказує на наявність флапінгу або нестабільність мережевих підключень.

---

## 9. Стратегії тестування: від юніт-тестів до хаос-інжинірингу

Тестування коду виборів лідера вимагає багаторівневого підходу, оскільки звичайні юніт-тести не здатні відтворити асинхронні мережеві аномалії:

### 1. Модульне тестування з керованим віртуальним годинником
Скінченний автомат лідера тестують за допомогою мок-координатора та контрольованого ручного просування монотонного часу (Virtual Clock). Це дозволяє детерміністично перевірити:
- Спрацьовування таймауту `T_deadline` при ігноруванні Keep-Alive;
- Виклик функції `request_stop()` та коректне встановлення прапорця `cancel_payload`;
- Складання повноважень при виклику методу `stop()`.

### 2. Хаос-тестування на базі Jepsen та Chaos Mesh
У тестовому кластері Kubernetes запускають сценарії штучного внесення збоїв:
- **`Pod Network Partition`:** Ізоляція поточного лідера від API-сервера або etcd за допомогою правил `iptables`. Перевіряється, чи перехоплює стендбай-под лідерство рівно за час `LeaseDuration + RetryPeriod`.
- **`Process Freeze (SIGSTOP / SIGCONT)`:** Надсилання сигналу `SIGSTOP` процесу лідера на 20 секунд (імітація GC-паузи). Перевіряється, що після отримання `SIGCONT` відкладений запис старого лідера надійно блокується базою даних за допомогою фенсингового токена.
- **`Clock Skew Injection`:** Зсув системного настінного часу на окремих вузлах кластера на 5 хвилин уперед/назад для підтвердження повної незалежності коду від системного годинника `CLOCK_REALTIME`.

### 3. Інтеграція зі життєвим циклом контейнерів Kubernetes (`preStop` Hook)
Під час розгортання в Kubernetes або OpenShift планове виведення пода з експлуатації (Rolling Update, дренаж ноди) надсилає контейнеру сигнал `SIGTERM`, надаючи період пільгового завершення `terminationGracePeriodSeconds` (за замовчуванням 30 секунд):
1. Клієнтський обробник `SIGTERM` ініціює виклик `stop()`, який виставляє `cancel_payload = true`.
2. Робочий потік лідера завершує активну транзакцію впродовж 1–2 секунд.
3. Клієнт надсилає запит `coordinator_resign()`, видаляючи лізу в координаторі.
4. Стендбай-под негайно перехоплює лізу за 50–100 мілісекунд, забезпечуючи нульовий простій для бізнес-користувачів без очікування спливання TTL.

---

## 10. Практичні рекомендації для продакшену

1. **Захисний таймаут примусової зупинки (Hard Drain Timeout):** Якщо фоновий потік лідера не завершує виконання впродовж безпечного інтервалу `TTL / 3` після отримання сигналу `request_stop()`, процес повинен виконати аварійне самознищення (`std::terminate()` або `exit(1)`). При цьому всі пули відкритих з'єднань до бази даних скидаються, щоб жодна фонова транзакція не залишалася в стані очікування відповіді. Краще перезавантажити весь контейнер і дозволити оркестратору підняти чистий екземпляр, ніж ризикувати зависанням у стані розділеного мозку.
2. **Рандомізація інтервалів опитування (Jitter):** Щоб уникнути синхронних сплесків запитів до координатора від десятків стендбай-вузлів у момент звільнення лізи, до інтервалу `retry_interval` обов'язково додають випадкове тремтіння (Jitter) у діапазоні `±20%`:
   ```cpp
   auto jitter = std::chrono::milliseconds(dist(rng));
   std::this_thread::sleep_for(retry_interval_ + jitter);
   ```
3. **Експорт стану в ендпоінти готовності (Readiness Probes):** Стендбай-вузли повинні залишатися успішними для HTTP-трафіку користувачів, але повідомляти оркестратору про свій статус не-лідера через внутрішні теги стану.
4. **Облік мережевих збоїв:** У разі виникнення помилок мережевого з'єднання з координатором лідер повинен негайно вважати лізу втраченою. Наївне припущення «я лідер, бо мій таймер ще не сплив, хоча зв'язку з координатором немає» призводить до невідновної розбіжності даних.
5. **Обробка напіввідкритих TCP-з'єднань (TCP Half-Open):** Якщо мережевий кабель відключено без надсилання TCP FIN/RST, сокет клієнта може залишатися відкритим протягом хвилин за замовчуванням операційної системи. Клієнтський код лідера повинен обов'язково налаштовувати прапорці `TCP_USER_TIMEOUT` у Linux або встановлювати тайм-аути на рівні gRPC/HTTP-клієнта, які строго менші за `T_renew`.
