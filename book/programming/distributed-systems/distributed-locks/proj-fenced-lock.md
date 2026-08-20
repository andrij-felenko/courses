# ⚙️ Розподілений замок з огорожею та сторожовим таймером

Розподілений замок не може гарантувати взаємне виключення у ненадійній мережі без активної участі самого ресурсу, який цей замок захищає. Якщо процес після отримання замка зависає в тривалій паузі збирача сміття чи стикається з мережевою затримкою, термін його оренди спливає на сервері, і замок передається іншому вузлу. Коли перший процес прокидається, він надсилає запізнілий запис, вважаючи, що досі володіє замком. Практична реалізація надійної системи розподіленого блокування вимагає трьох компонентів: координатора з монотонною видачею токенів огорожі, клієнта з фоновим сторожовим таймером подовження лізи та сховища, яке відкидає операції із застарілими токенами.

## Архітектура взаємодії компонентів

Надійне розподілене блокування спирається на тристоронній протокол, де кожна зі сторін має строго окреслену зону відповідальності:

1. **Координатор замків (Lock Coordinator)**:
   - Зберігає поточний стан замка, ідентифікатор активного власника та дедлайн лізи за монотонним системним таймером.
   - З кожним новим захопленням замка інкрементує монотонний 64-бітний лічильник епохи — **токен огорожі** (англ. *fencing token*).
   - Приймає запити на подовження лізи (`renew`) лише від того клієнта, чий токен збігається з поточним активним токеном, і лише до того, як сплив попередньо встановлений дедлайн.

2. **Спільне сховище (Fenced Resource Store)**:
   - Зберігає захищений стан системи (наприклад, баланс банківського рахунку, метадані таблиці або конфігурацію кластера).
   - Зберігає максимальне значення побаченого токена огорожі `highest_fencing_token`.
   - Приймає команду запису `write(client_id, token, data)` лише за умови `token >= highest_fencing_token`. У разі успіху фіксує нові дані та оновлює `highest_fencing_token = token`. Якщо ж `token < highest_fencing_token`, запис негайно відхиляється з помилкою `STALE_FENCING_TOKEN`.

3. **Клієнт блокування (Lock Client)**:
   - Запитує замок у координатора, отримує лізу на час `TTL` та унікальний токен огорожі.
   - Запускає фоновий потік-сторож (англ. *watchdog*), який періодично надсилає координатору сигнали подовження оренди з інтервалом `TTL / 3`.
   - Надає робочому потоку прапорець скасування (англ. *cancellation token*): якщо сторож не зміг подовжити лізу (через обрив зв'язку чи відмову координатора), робочий потік негайно інформується про необхідність перервати операцію.
   - Автоматично звільняє замок після завершення роботи через патерн RAII (в C++) або явну функцію звільнення (в C).

## Робоча реалізація: C та C++

Нижче наведено повні самодостатні реалізації координатора, захищеного сховища та клієнта, які симулюють реальний сценарій аварійної GC-паузи процесу та демонструють захист даних за допомогою огорожі.

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>

/* Отримання поточного монотонного часу в мілісекундах */
static uint64_t monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

/* ── 1. Координатор розподілених замків ───────────────────────────────────── */
typedef struct {
    pthread_mutex_t mtx;
    bool is_locked;
    char owner_id[32];
    uint64_t fencing_counter;
    uint64_t current_token;
    uint64_t lease_deadline_ms;
} lock_coordinator_t;

static void coordinator_init(lock_coordinator_t *coord) {
    pthread_mutex_init(&coord->mtx, NULL);
    coord->is_locked = false;
    coord->owner_id[0] = '\0';
    coord->fencing_counter = 0;
    coord->current_token = 0;
    coord->lease_deadline_ms = 0;
}

static bool coordinator_acquire(lock_coordinator_t *coord, const char *client_id,
                                uint64_t ttl_ms, uint64_t *out_token) {
    pthread_mutex_lock(&coord->mtx);
    uint64_t now = monotonic_ms();

    /* Якщо замок утримується, але строк лізи сплив — примусово звільняємо */
    if (coord->is_locked && now >= coord->lease_deadline_ms) {
        printf("[Координатор] Ліза клієнта '%s' спливла! Замок вилучено.\n", coord->owner_id);
        coord->is_locked = false;
    }

    if (!coord->is_locked) {
        coord->is_locked = true;
        snprintf(coord->owner_id, sizeof(coord->owner_id), "%s", client_id);
        coord->fencing_counter++;
        coord->current_token = coord->fencing_counter;
        coord->lease_deadline_ms = now + ttl_ms;
        *out_token = coord->current_token;
        printf("[Координатор] Замок надано '%s'. Токен огорожі = %llu, TTL = %llu мс\n",
               client_id, (unsigned long long)*out_token, (unsigned long long)ttl_ms);
        pthread_mutex_unlock(&coord->mtx);
        return true;
    }

    pthread_mutex_unlock(&coord->mtx);
    return false;
}

static bool coordinator_renew(lock_coordinator_t *coord, const char *client_id,
                              uint64_t token, uint64_t ttl_ms) {
    pthread_mutex_lock(&coord->mtx);
    uint64_t now = monotonic_ms();

    if (coord->is_locked &&
        strcmp(coord->owner_id, client_id) == 0 &&
        coord->current_token == token &&
        now < coord->lease_deadline_ms) {
        coord->lease_deadline_ms = now + ttl_ms;
        printf("[Координатор] Лізу подовжено для '%s' (токен %llu) ще на %llu мс\n",
               client_id, (unsigned long long)token, (unsigned long long)ttl_ms);
        pthread_mutex_unlock(&coord->mtx);
        return true;
    }

    pthread_mutex_unlock(&coord->mtx);
    return false;
}

static void coordinator_release(lock_coordinator_t *coord, const char *client_id, uint64_t token) {
    pthread_mutex_lock(&coord->mtx);
    if (coord->is_locked &&
        strcmp(coord->owner_id, client_id) == 0 &&
        coord->current_token == token) {
        coord->is_locked = false;
        printf("[Координатор] Клієнт '%s' добровільно звільнив замок (токен %llu).\n",
               client_id, (unsigned long long)token);
    }
    pthread_mutex_unlock(&coord->mtx);
}

/* ── 2. Спільне сховище з перевіркою огорожі ──────────────────────────────── */
typedef struct {
    pthread_mutex_t mtx;
    uint64_t highest_fencing_token;
    int data_value;
} fenced_storage_t;

static void storage_init(fenced_storage_t *st) {
    pthread_mutex_init(&st->mtx, NULL);
    st->highest_fencing_token = 0;
    st->data_value = 0;
}

static bool storage_write(fenced_storage_t *st, const char *client_id,
                          uint64_t token, int value) {
    pthread_mutex_lock(&st->mtx);
    printf("[Сховище] Запит на запис від '%s': значення = %d, токен = %llu. (Макс. токен = %llu)\n",
           client_id, value, (unsigned long long)token,
           (unsigned long long)st->highest_fencing_token);

    if (token >= st->highest_fencing_token) {
        st->highest_fencing_token = token;
        st->data_value = value;
        printf("[Сховище] ✓ УСПІХ! Запис від '%s' прийнято. Новий баланс = %d\n",
               client_id, value);
        pthread_mutex_unlock(&st->mtx);
        return true;
    } else {
        printf("[Сховище] ✗ ВІДХИЛЕНО! Застарілий токен %llu < %llu. Запис від '%s' заблоковано!\n",
               (unsigned long long)token, (unsigned long long)st->highest_fencing_token, client_id);
        pthread_mutex_unlock(&st->mtx);
        return false;
    }
}

/* ── 3. Клієнт блокування зі сторожовим таймером ──────────────────────────── */
typedef struct {
    lock_coordinator_t *coord;
    char client_id[32];
    uint64_t ttl_ms;
    uint64_t token;
    bool has_lock;
    bool stop_watchdog;
    pthread_t watchdog_thread;
} lock_client_t;

static void *watchdog_worker(void *arg) {
    lock_client_t *c = (lock_client_t *)arg;
    uint64_t interval_us = (c->ttl_ms / 3) * 1000;

    while (1) {
        usleep(interval_us);
        if (c->stop_watchdog) break;

        if (!coordinator_renew(c->coord, c->client_id, c->token, c->ttl_ms)) {
            printf("[Клієнт %s] Втрачено лізу під час подовження!\n", c->client_id);
            c->has_lock = false;
            break;
        }
    }
    return NULL;
}

static bool client_acquire(lock_client_t *c, lock_coordinator_t *coord,
                           const char *id, uint64_t ttl_ms) {
    c->coord = coord;
    snprintf(c->client_id, sizeof(c->client_id), "%s", id);
    c->ttl_ms = ttl_ms;
    c->has_lock = false;
    c->stop_watchdog = false;

    if (coordinator_acquire(coord, id, ttl_ms, &c->token)) {
        c->has_lock = true;
        pthread_create(&c->watchdog_thread, NULL, watchdog_worker, c);
        return true;
    }
    return false;
}

static void client_release(lock_client_t *c) {
    if (c->has_lock) {
        c->stop_watchdog = true;
        pthread_join(c->watchdog_thread, NULL);
        coordinator_release(c->coord, c->client_id, c->token);
        c->has_lock = false;
    }
}

/* ── Симуляція зіткнення через паузу процесу ──────────────────────────────── */
int main(void) {
    lock_coordinator_t coord;
    fenced_storage_t store;
    coordinator_init(&coord);
    storage_init(&store);

    printf("=== СТАРТ СИМУЛЯЦІЇ РОЗПОДІЛЕНОГО ЗАМКА З ОГОРОЖЕЮ ===\n\n");

    /* 1. Клієнт 1 бере замок з TTL = 1000 мс */
    lock_client_t client1;
    if (!client_acquire(&client1, &coord, "Клієнт-1", 1000)) {
        fprintf(stderr, "Не вдалося отримати замок для Клієнта-1\n");
        return 1;
    }

    /* 2. Клієнт 1 імітує GC-паузу / зависання: потік зупиняє роботу і НЕ оновлює лізу */
    printf("\n>>> Клієнт-1 зависає в GC-паузі на 2200 мс (сторож заблоковано)... <<<\n\n");
    client1.stop_watchdog = true; /* Імітація повної зупинки процесу разом зі сторожем */
    pthread_join(client1.watchdog_thread, NULL);
    usleep(2200 * 1000); /* Пауза довша за TTL */

    /* 3. Клієнт 2 намагається отримати замок і перехоплює його */
    lock_client_t client2;
    printf(">>> Клієнт-2 запитує замок після спливання лізи Клієнта-1... <<<\n");
    if (client_acquire(&client2, &coord, "Клієнт-2", 1000)) {
        /* Клієнт 2 успішно записує дані */
        storage_write(&store, client2.client_id, client2.token, 500);
        client_release(&client2);
    }

    /* 4. Клієнт 1 прокидається і намагається виконати запис зі старим токеном */
    printf("\n>>> Клієнт-1 прокинувся від паузи й надсилає запізнілий запис... <<<\n");
    bool ok = storage_write(&store, client1.client_id, client1.token, 999);
    if (!ok) {
        printf(">>> ОГОРОЖА ВРЯТУВАЛА СИСТЕМУ ВІД ПОРУШЕННЯ ЦІЛІСНОСТІ! <<<\n");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <mutex>
#include <optional>
#include <atomic>
#include <thread>
#include <format>
#include <cstdint>

using namespace std::chrono_literals;

/* ── 1. Координатор розподілених замків ───────────────────────────────────── */
class LockCoordinator {
public:
    struct GrantResult {
        uint64_t fencing_token;
        std::chrono::milliseconds ttl;
    };

    std::optional<GrantResult> acquire(std::string_view client_id, std::chrono::milliseconds ttl) {
        std::lock_guard<std::mutex> lock(mtx_);
        const auto now = std::chrono::steady_clock::now();

        if (is_locked_ && now >= lease_deadline_) {
            std::cout << std::format("[Координатор] Ліза клієнта '{}' спливла! Замок вилучено.\n", owner_id_);
            is_locked_ = false;
        }

        if (!is_locked_) {
            is_locked_ = true;
            owner_id_ = client_id;
            current_token_ = ++fencing_counter_;
            lease_deadline_ = now + ttl;
            std::cout << std::format("[Координатор] Замок надано '{}'. Токен огорожі = {}, TTL = {} мс\n",
                                     client_id, current_token_, ttl.count());
            return GrantResult{current_token_, ttl};
        }

        return std::nullopt;
    }

    bool renew(std::string_view client_id, uint64_t token, std::chrono::milliseconds ttl) {
        std::lock_guard<std::mutex> lock(mtx_);
        const auto now = std::chrono::steady_clock::now();

        if (is_locked_ && owner_id_ == client_id && current_token_ == token && now < lease_deadline_) {
            lease_deadline_ = now + ttl;
            std::cout << std::format("[Координатор] Лізу подовжено для '{}' (токен {}) ще на {} мс\n",
                                     client_id, token, ttl.count());
            return true;
        }
        return false;
    }

    void release(std::string_view client_id, uint64_t token) {
        std::lock_guard<std::mutex> lock(mtx_);
        if (is_locked_ && owner_id_ == client_id && current_token_ == token) {
            is_locked_ = false;
            std::cout << std::format("[Координатор] Клієнт '{}' добровільно звільнив замок (токен {}).\n",
                                     client_id, token);
        }
    }

private:
    std::mutex mtx_;
    bool is_locked_{false};
    std::string owner_id_;
    uint64_t fencing_counter_{0};
    uint64_t current_token_{0};
    std::chrono::steady_clock::time_point lease_deadline_;
};

/* ── 2. Спільне сховище з перевіркою токена огорожі ──────────────────────── */
template <typename T>
class FencedStorage {
public:
    bool write(std::string_view client_id, uint64_t token, const T& new_value) {
        std::lock_guard<std::mutex> lock(mtx_);
        std::cout << std::format("[Сховище] Запит на запис від '{}': значення = {}, токен = {}. (Макс. токен = {})\n",
                                 client_id, new_value, token, highest_token_);

        if (token >= highest_token_) {
            highest_token_ = token;
            data_ = new_value;
            std::cout << std::format("[Сховище] ✓ УСПІХ! Запис від '{}' прийнято. Новий баланс = {}\n",
                                     client_id, new_value);
            return true;
        }

        std::cout << std::format("[Сховище] ✗ ВІДХИЛЕНО! Застарілий токен {} < {}. Запис від '{}' заблоковано!\n",
                                 token, highest_token_, client_id);
        return false;
    }

    [[nodiscard]] T read() const {
        std::lock_guard<std::mutex> lock(mtx_);
        return data_;
    }

private:
    mutable std::mutex mtx_;
    uint64_t highest_token_{0};
    T data_{};
};

/* ── 3. RAII-обгортка розподіленого замка з автоматичним сторожем ─────────── */
class FencedLockGuard {
public:
    static std::optional<FencedLockGuard> try_acquire(LockCoordinator& coord,
                                                      std::string client_id,
                                                      std::chrono::milliseconds ttl) {
        auto grant = coord.acquire(client_id, ttl);
        if (!grant) return std::nullopt;

        return FencedLockGuard(coord, std::move(client_id), grant->fencing_token, grant->ttl);
    }

    ~FencedLockGuard() {
        if (active_.load()) {
            stop_requested_.store(true);
            if (watchdog_.joinable()) {
                watchdog_.join();
            }
            coord_.release(client_id_, token_);
            active_.store(false);
        }
    }

    FencedLockGuard(const FencedLockGuard&) = delete;
    FencedLockGuard& operator=(const FencedLockGuard&) = delete;

    FencedLockGuard(FencedLockGuard&& other) noexcept
        : coord_(other.coord_), client_id_(std::move(other.client_id_)),
          token_(other.token_), ttl_(other.ttl_), active_(other.active_.load()) {
        other.active_.store(false);
    }

    [[nodiscard]] uint64_t token() const noexcept { return token_; }
    [[nodiscard]] bool is_valid() const noexcept { return active_.load(); }

    /* Метод для симуляції зависання процесу без надсилання оновлень */
    void simulate_hang_stop_watchdog() {
        stop_requested_.store(true);
        if (watchdog_.joinable()) {
            watchdog_.join();
        }
    }

private:
    FencedLockGuard(LockCoordinator& coord, std::string client_id, uint64_t token, std::chrono::milliseconds ttl)
        : coord_(coord), client_id_(std::move(client_id)), token_(token), ttl_(ttl), active_(true) {
        watchdog_ = std::thread([this]() {
            const auto interval = ttl_ / 3;
            while (!stop_requested_.load()) {
                std::this_thread::sleep_for(interval);
                if (stop_requested_.load()) break;

                if (!coord_.renew(client_id_, token_, ttl_)) {
                    std::cout << std::format("[Клієнт {}] Втрачено лізу під час оновлення!\n", client_id_);
                    active_.store(false);
                    break;
                }
            }
        });
    }

    LockCoordinator& coord_;
    std::string client_id_;
    uint64_t token_;
    std::chrono::milliseconds ttl_;
    std::atomic<bool> active_{false};
    std::atomic<bool> stop_requested_{false};
    std::thread watchdog_;
};

/* ── Симуляція сценарію розщеплення замка ─────────────────────────────────── */
int main() {
    LockCoordinator coordinator;
    FencedStorage<int> storage;

    std::cout << "=== СТАРТ СИМУЛЯЦІЇ РОЗПОДІЛЕНОГО ЗАМКА З ОГОРОЖЕЮ (C++) ===\n\n";

    // 1. Клієнт 1 захоплює замок на 1000 мс
    auto lock1 = FencedLockGuard::try_acquire(coordinator, "Клієнт-1", 1000ms);
    if (!lock1) {
        std::cerr << "Помилка: не вдалося захопити замок для Клієнта-1\n";
        return 1;
    }
    const uint64_t token1 = lock1->token();

    // 2. Клієнт 1 зависає в тривалій паузі (зупиняємо потік сторожа)
    std::cout << "\n>>> Клієнт-1 зависає в GC-паузі на 2200 мс (сторож зупинено)... <<<\n\n";
    lock1->simulate_hang_stop_watchdog();
    std::this_thread::sleep_for(2200ms);

    // 3. Клієнт 2 перехоплює замок після спливання лізи Клієнта 1
    std::cout << ">>> Клієнт-2 запитує замок після спливання лізи Клієнта-1... <<<\n";
    {
        auto lock2 = FencedLockGuard::try_acquire(coordinator, "Клієнт-2", 1000ms);
        if (lock2) {
            storage.write("Клієнт-2", lock2->token(), 500);
        }
    } // lock2 автоматично звільняється в деструкторі

    // 4. Клієнт 1 прокидається і намагається виконати запізнілий запис
    std::cout << "\n>>> Клієнт-1 прокинувся від паузи й надсилає запізнілий запис... <<<\n";
    const bool success = storage.write("Клієнт-1", token1, 999);

    if (!success) {
        std::cout << ">>> ОГОРОЖА ВРЯТУВАЛА СИСТЕМУ ВІД ПОРУШЕННЯ ЦІЛІСНОСТІ! <<<\n";
    }

    return 0;
}
```
:::

## Покроковий аналіз виконання програми

Розглянемо вивід симуляції та внутрішню динаміку стану системи на кожному етапі:

```text
=== СТАРТ СИМУЛЯЦІЇ РОЗПОДІЛЕНОГО ЗАМКА З ОГОРОЖЕЮ ===

[Координатор] Замок надано 'Клієнт-1'. Токен огорожі = 1, TTL = 1000 мс

>>> Клієнт-1 зависає в GC-паузі на 2200 мс (сторож заблоковано)... <<<

>>> Клієнт-2 запитує замок після спливання лізи Клієнта-1... <<<
[Координатор] Ліза клієнта 'Клієнт-1' спливла! Замок вилучено.
[Координатор] Замок надано 'Клієнт-2'. Токен огорожі = 2, TTL = 1000 мс
[Сховище] Запит на запис від 'Клієнт-2': значення = 500, токен = 2. (Макс. токен = 0)
[Сховище] ✓ УСПІХ! Запис від 'Клієнт-2' прийнято. Новий баланс = 500
[Координатор] Клієнт 'Клієнт-2' добровільно звільнив замок (токен 2).

>>> Клієнт-1 прокинувся від паузи й надсилає запізнілий запис... <<<
[Сховище] Запит на запис від 'Клієнт-1': значення = 999, токен = 1. (Макс. токен = 2)
[Сховище] ✗ ВІДХИЛЕНО! Застарілий токен 1 < 2. Запис від 'Клієнт-1' заблоковано!
>>> ОГОРОЖА ВРЯТУВАЛА СИСТЕМУ ВІД ПОРУШЕННЯ ЦІЛІСНОСТІ! <<<
```

### Етап 1: Ініціалізація та надання першого замка
Клієнт-1 звертається до координатора із запитом на блокування з тайм-аутом `TTL = 1000` мс. Координатор встановлює дедлайн `now + 1000` мс і повертає `токен = 1`. Клієнт створює фоновий потік, який зобов'язується надсилати сигнали подовження лізи кожні 333 мс (`TTL / 3`).

### Етап 2: Зупинка процесу та втрата оренди
Клієнт-1 зазнає непередбачуваної затримки на 2200 мс. У реальному середовищі це може бути тривала пауза Stop-the-world збирача сміття у Java чи Go, інтенсивний скид сторінкового обміну пам'яті у swap-файл на повільний диск чи затримка віртуальної машини гіпервізором під час міграції. Оскільки потік сторожа заблоковано разом з основним процесом, жодних запитів на подовження не надходить. Через 1000 мс координатор фіксує спливання лізи.

### Етап 3: Перехоплення замка новим лідером
Клієнт-2 звертається до координатора у момент `t = 2200` мс. Координатор бачить, що попередня ліза спливла, анулює старе володіння, інкрементує лічильник епохи та надає Клієнту-2 новий замок із `токеном = 2`. Клієнт-2 успішно виконує запис у спільне сховище. Сховище фіксує значення `highest_fencing_token = 2` та встановлює новий баланс `500`. Після завершення операції Клієнт-2 коректно звільняє замок.

### Етап 4: Запізнілий запис і спрацьовування огорожі
Клієнт-1 нарешті прокидається. Його внутрішній стек викликів перебуває у точці відправлення результату: він не знає, що минуло понад дві секунди, і вважає замок чинним. Клієнт-1 відправляє команду запису значення `999` зі своїм старим `токеном = 1`. 

Сховище перевіряє умову: `1 < 2` (поточний максимальний токен). Оскільки токен запиту менший за вже зафіксований, операція негайно блокується з поверненням помилки. Баланс `500`, записаний Клієнтом-2, залишається неушкодженим.

## Інтеграція огорожі в реальні виробничі координатори

У промислових системах роль координатора замків та джерела монотонних токенів виконують розподілені консенсусні сервіси (etcd, Apache ZooKeeper, HashiCorp Consul). Розглянемо, які конкретно поля та механізми цих систем використовуються як токени огорожі.

### 1. etcd v3: Ревізії створення та лізи
В etcd версії 3 кожна зміна стану кластера отримує глобально монотонний 64-бітний номер ревізії (`revision`).

Для блокування використовується API конкурентності (`clientv3/concurrency`):
- Клієнт створює лізу з таймаутом: `lease, _ := cli.Grant(ctx, 10)`.
- Клієнт викликає `clientv3.KeepAlive()`, який відкриває двонаправлений gRPC-стрім для фонового оновлення лізи.
- Клієнт створює об'єкт м'ютекса: `m := concurrency.NewMutex(session, "/locks/leader")` і викликає `m.Lock(ctx)`.
- etcd створює ключ виду `/locks/leader/694d8021cb82c01d`, прив'язаний до лізи.

**Що виступає токеном огорожі**: поле `Header.Revision` або `CreateRevision` створеного ключа. Це монотонно зростаюче число, яке клієнт зобов'язаний витягти з відповіді `m.Header().Revision` та передати у свій SQL-запит чи RPC до бази даних.

### 2. Apache ZooKeeper: Послідовні ефемерні вузли
У ZooKeeper класичний алгоритм блокування реалізується через ефемерні послідовні вузли (англ. *Ephemeral Sequential znodes*):
- Клієнт створює вузол: `create("/locks/job-", EPHEMERAL_SEQUENTIAL)`.
- ZooKeeper створює запис виду `/locks/job-0000000034`.
- Клієнт отримує список усіх дочірніх вузлів у папці `/locks/`.
- Якщо створений клієнтом вузол має найменший номер серед усіх наявних — замок захоплено.
- Якщо ні — клієнт підписується (встановлює `Watcher`) на подію видалення вузла з безпосередньо попереднім номером (наприклад, вузол 34 підписується на вузол 33). Це повністю усуває проблему гримучої отари (англ. *thundering herd*), оскільки під час звільнення замка прокидається лише один черговий процес.

**Що виступає токеном огорожі**: суфікс порядкового номера вузла (наприклад, `34`) або монотонний номер транзакції ZooKeeper `zxid` (64-бітне число, де старші 32 біти — номер епохи лідера, а молодші — лічильник транзакцій).

### 3. Реляційні бази даних (PostgreSQL, MySQL)
У SQL-базах даних перевірка токена реалізується через умовний оператор `UPDATE` або транзакцію з блокуванням рядка:

```sql
-- Атомарне оновлення з перевіркою монотонного токена огорожі
UPDATE account_ledger
SET 
    balance = 500,
    last_fencing_token = 35,
    updated_at = NOW()
WHERE 
    account_id = 'ACC-98765'
    AND last_fencing_token < 35;
```

Якщо жоден рядок не оновився (`rows_affected == 0`), застосунок знає, що його токен застарів, і операція повинна бути скасована без повторних спроб.

### 4. NoSQL та документоорієнтовані бази (DynamoDB, MongoDB)
У розподілених Key-Value та NoSQL сховищах використовуються умовні вирази запису (англ. *Conditional Writes*):

```json
{
  "TableName": "AccountLedger",
  "Key": { "AccountId": { "S": "ACC-98765" } },
  "UpdateExpression": "SET Balance = :val, HighestToken = :tok",
  "ConditionExpression": "attribute_not_exists(HighestToken) OR HighestToken < :tok",
  "ExpressionAttributeValues": {
    ":val": { "N": "500" },
    ":tok": { "N": "35" }
  }
}
```

Якщо інший процес уже записав токен `35`, спроба виконати операцію з токеном `34` викличе виняток `ConditionalCheckFailedException`, що гарантує захист на рівні консенсусного рушія бази даних.

## Мережевий рівень: двонаправлені потоки та обриви зв'язку

У реальних клієнтських бібліотеках (наприклад, Go-драйвер etcd чи C++ SDK ZooKeeper) періодичне подовження лізи організовують не окремими HTTP-запитами, а через постійний двонаправлений мережевий потік (gRPC bidirectional stream або TCP-сесію).

Така схема має три суттєві переваги над періодичним REST/RPC-опитуванням:
1. **Зниження накладних витрат**: не потрібно на кожен запит подовження виконувати TLS-рукостискання та заново передавати заголовки автентифікації.
2. **Миттєве виявлення обриву з'єднання**: відправка кадрів `HTTP/2 PING` або перевірка стану TCP-сокета дає змогу клієнту дізнатися про розрив зв'язку за частки секунди, не чекаючи вичерпання повного таймауту лізи.
3. **Плавне перепідключення (Reconnection Backoff)**: якщо з'єднання з поточним вузлом кластера etcd обірвалося, клієнтська бібліотека негайно намагається підключитися до іншого вузла тієї ж Raft-групи. Якщо перепідключення вдалося здійснити до спливання строку лізи, сесія продовжується безшовно без втрати замка.

## Патерн виборів лідера на базі розподіленого замка

Розподілений замок із лізою є фундаментальним будівельним блоком для патерну **виборів активного лідера** (англ. *Leader Election*). У системі з багатьма однаковими копіями мікросервісу лише один екземпляр повинен виконувати роль координатора (наприклад, генерувати розклад завдань чи читати вхідний потік Kafka).

Життєвий цикл лідера складається з таких фаз:
1. **Змагання за лідерство**: усі вузли під час старту намагаються захопити спільний замок `/service/leader`. Переможець стає активним лідером і отримує токен епохи `E`. Решта вузлів стають пасивними репліками (англ. *standby*) і підписуються на подію звільнення замка.
2. **Утримання лідерства**: активний лідер запускає фоновий потік оновлення лізи. Доки ліза подовжується, лідер обробляє бізнес-логіку і додає токен `E` до всіх вихідних команд.
3. **Зниження рангу (Demotion / Resignation)**: якщо потік оновлення лізи повідомляє про збій зв'язку з координатором, активний лідер зобов'язаний негайно перевести свій стан у режим очікування (`standby`), зупинити всі фонові воркери та скасувати незавершені транзакції.
4. **Захист від незворотних зовнішніх дій**: якщо лідер повинен виконати дію над зовнішньою системою без підтримки токенів (наприклад, відправити HTTP POST у сторонній платіжний шлюз чи надіслати SMS), він зобов'язаний згенерувати **ключ ідемпотентності** на основі токена епохи: `Idempotency-Key: leader-epoch-35-tx-10042`. Якщо лідер зазнає паузи й операція повториться новим лідером з токеном 36, зовнішній шлюз або заблокує дублікат, або збереже чіткий слід операцій для подальшого аудиту.

## Методологія тестування хаосом (Chaos Engineering)

Перевірка коректності роботи розподіленого замка та огорожі вимагає спеціальних методів тестування, оскільки в штатному лабораторному середовищі стан перегонів виникає вкрай рідко.

У промисловій розробці застосовують такі підходи до верифікації (зокрема у фреймворку *Jepsen*):

1. **Впровадження штучних пауз процесів (SIGSTOP / SIGCONT)**:
   Тестовий скрипт надсилає процесу сигнал `kill -STOP <pid>` одразу після отримання замка. Процес «заморожується» на 15 секунд (довше за TTL лізи). За цей час інший потік встигає перехопити замок і виконати запис. Потім надсилається `kill -CONT <pid>`. Тест перевіряє, що розморожений процес отримує помилку відхилення від сховища і не пошкоджує дані.

2. **Емуляція мережевих розділень (Network Partitions через iptables / tc)**:
   За допомогою утиліти Linux `tc` (Traffic Control) на мережевому інтерфейсі симулюється затримка доставки пакетів у 5000 мс або повне блокування пакетів до координатора через правила `iptables -A INPUT -p tcp --dport 2379 -j DROP`. Тест верифікує, що клієнт вчасно активує прапорець переривання і не намагається виконувати операції в ізольованому стані.

3. **Стрес-тестування дискового вводу-виводу (I/O Injection)**:
   За допомогою утиліти `fio` або створення високого навантаження на swap штучно викликається зависання дискової підсистеми клієнта, щоб перевірити поведінку таймерів при витісненні сторінок пам'яті процесу.

## Відмінності системного дизайну у C та C++

Порівняння двох підходів до коду ілюструє різницю системного проектування на C та ідіоматичного сучасного C++:

1. **Керування пам'яттю та життєвим циклом (RAII)**:
   - У версії на C клієнт зобов'язаний вручну викликати `client_release()`, стежити за послідовністю викликів `pthread_join()` та коректно очищати м'ютекси. Помилка або передчасний вихід через `return` у будь-якій гілці обробки помилок призведе до мертвого блокування, витоку ресурсів чи неконтрольованого фонового потоку.
   - У версії на C++ клас `FencedLockGuard` реалізує патерн RAII: захоплення ресурсу відбувається в статичній фабриці `try_acquire()`, а зупинка сторожового потоку та повернення замка координатору гарантовано відбуваються в деструкторі при виході з області видимості (навіть у разі виникнення винятку). Конструктори копіювання видалені (`= delete`), що виключає випадкове дублювання володіння замком, а конструктор переміщення (`std::move`) дозволяє безпечно передавати володіння між контекстами виконання.

2. **Атомарні прапорці та моделі пам'яті (Memory Ordering)**:
   - У C++ координатор і клієнт використовують `std::atomic<bool>` для прапорців зупинки `stop_requested_` та валідності `active_`. Це гарантує коректні бар'єри пам'яті між робочим потоком і сторожовим потоком на рівні апаратних інструкцій процесора (acquire-release semantics) без необхідності блокувати м'ютекс при кожній перевірці статусу.
   - Часові інтервали строго типізовані через бібліотеку `<chrono>` (`std::chrono::milliseconds`, літерали `1000ms`, `2200ms`), що повністю виключає класичну системну помилку передачі мілісекунд у функцію, яка очікує мікросекунди або секунди.

## Інженерні підводні камені та типові помилки

При впровадженні розподілених замків у виробниче середовище слід уникати таких поширених пасток:

1. **Ігнорування статусу сторожа робочим потоком**:
   Найчастіша помилка розробників — запуск тривалої задачі без періодичної перевірки валідності замка. Якщо робочий процес завантажує великий масив даних, обробляє його протягом двох хвилин, а сторож втратив зв'язок із координатором на тридцятій секунді через мережевий збій, робочий потік не повинен сліпо продовжувати обчислення. Він зобов'язаний регулярно перевіряти стан прапорця скасування (`lock_guard.is_valid()`) і негайно переривати транзакцію, звільняючи ресурси.

2. **Скидання генератора токенів при перезапуску координатора**:
   Якщо координатор зберігає лічильник токенів виключно в оперативній пам'яті, його аварійний перезапуск призведе до обнулення лічильника (`token = 1`). Якщо сховище вже містить записи з токенами `100+`, система буде заблокована назавжди, відхиляючи всі нові легітимні транзакції. Токен огорожі координатора зобов'язаний бути персистентним (наприклад, номер транзакції в журналі WAL консенсусної групи Raft).

3. **Розрив між перевіркою токена та записом даних**:
   Категорично заборонено розділяти перевірку токена та збереження даних на два незалежні мережеві виклики (наприклад, спочатку виконати `GET /highest_token`, а потім окремий `POST /data`). Між цими викликами гарантовано виникне вікно для стану перегонів (*Race Condition*). Перевірка та запис мусять бути **єдиною неподільною атомарною операцією** на боці цільового сховища.

4. **Асинхронний злив дискових буферів (Page Cache Flushing)**:
   Якщо захищений ресурс — це файл на локальній чи мережевій файловій системі (NFS, CephFS), клієнт зобов'язаний викликати `fsync()` або відкривати дескриптор із прапорцем `O_SYNC` перед тим, як вважати операцію завершеною та відпускати замок. Інакше операційна система може затримати фізичний скид «брудних» сторінок кешу ядра на диск, і реальні байти потраплять у сховище вже після того, як ліза спливла, а новий клієнт почав записувати новий блок даних.
