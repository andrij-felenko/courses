# ⚙️ Реалізація швидкого шляху з атомарною підміною таблиць: Data Plane без блокувань та асинхронний Control Plane

У високонавантажених проксі-серверах, балансувальниках навантаження та L7-маршрутизаторах (таких як Envoy, NGINX чи Traefik) площина даних (Data Plane) обробляє сотні тисяч запитів за секунду на кожне процесорне ядро. Головною технічною вимогою до швидкого шляху (Fast Path) є мінімальна та передбачувана затримка обробки кожного запиту (суб-мікросекундний діапазон).

Використання традиційних м'ютексів виключного доступу (`pthread_mutex_t` або `std::mutex`) чи навіть замків читання-запису (`pthread_rwlock_t` або `std::shared_mutex`) для синхронізації таблиці маршрутизації між потоком прийому конфігурації (Control Plane) та робочими потоками обробки пакетів (Data Plane) призводить до катастрофічної деградації системи.

## Чому класичні замки руйнують продуктивність Data Plane

Коли кілька десятків процесорних потоків намагаються одночасно захопити навіть спільний замок читання (`read-lock`):

1. **Конфлікт ліній кешу (Cache Line Bouncing):** Захоплення `shared_mutex` вимагає атомарної модифікації внутрішнього лічильника читачів у спільній пам'яті. Усі процесорні ядра починають змагатися за володіння однією кеш-лінією `L1/L2`, що інвалідує кеші процесора через протокол когерентності (MESI/MOESI) і створює затримки в сотні тактів на кожне звернення.
2. **Блокування на час запису (Writer Starvation / Writer Blocking):** Коли площина управління отримує оновлення топології, потік запису намагається захопити ексклюзивний замок. Усі робочі ядра миттєво зупиняють маршрутизацію трафіку і переводяться ядром операційної системи в стан очікування (sleep/waitqueue). Затримка пакетів під час такого оновлення стрибає з 15 мікросекунд до 5–10 мілісекунд, викликаючи сплески таймаутів.

Розв'язанням цієї проблеми є патерн **незмінного зліпка (Immutable Snapshot) з атомарною підміною покажчика (Atomic Pointer Swap)**. Робочі потоки площини даних вичитують атомарний покажчик на поточний зліпок без жодного блокування, а потік управління повністю формує новий зліпок у фоновій пам'яті та публікує його однією атомарною інструкцією з бар'єром пам'яті `release-acquire`.

## Архітектура неблокуючої синхронізації

1. **Незмінний зліпок (`ConfigSnapshot`):** структура даних, що містить скомпільовану таблицю маршрутів та списки бекендів. Після створення зліпок ніколи не модифікується, що гарантує абсолютну безпеку паралельного читання багатьма потоками без будь-яких блокувань.
2. **Атомарний покажчик (`active_config`):** глобальний покажчик `std::atomic<ConfigSnapshot*>`, що вказує на актуальну версію конфігурації.
3. **Безпечне керування пам'яттю (Atomic Reference Counting):** кожен зліпок містить атомарний лічильник посилань. Робочий потік збільшує лічильник на час обробки запиту і зменшує після завершення. Потік управління після публікації нової версії відпускає своє посилання; коли останній робочий потік завершує роботу зі старим зліпком, пам'ять безпечно звільняється без витоків.

## Практична реалізація: C та ідіоматичний C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <pthread.h>
#include <unistd.h>

#define MAX_ROUTES 8
#define MAX_BACKENDS 4
#define MAX_NAME_LEN 32

typedef struct {
    char name[MAX_NAME_LEN];
    uint32_t weight;
    bool is_healthy;
} backend_t;

typedef struct {
    char path_prefix[MAX_NAME_LEN];
    backend_t backends[MAX_BACKENDS];
    size_t backend_count;
} route_rule_t;

typedef struct config_snapshot {
    uint64_t version;
    route_rule_t routes[MAX_ROUTES];
    size_t route_count;
    atomic_uint ref_count;
} config_snapshot_t;

/* Глобальний атомарний покажчик на активну конфігурацію */
static _Atomic(config_snapshot_t*) g_active_config = NULL;
static atomic_bool g_running = true;

config_snapshot_t* snapshot_create(uint64_t version) {
    config_snapshot_t* s = (config_snapshot_t*)malloc(sizeof(config_snapshot_t));
    if (!s) return NULL;
    s->version = version;
    s->route_count = 0;
    atomic_init(&s->ref_count, 1); /* 1 посилання утримує глобальний покажчик */
    return s;
}

void snapshot_add_route(config_snapshot_t* s, const char* prefix, backend_t* backends, size_t count) {
    if (s->route_count >= MAX_ROUTES) return;
    route_rule_t* r = &s->routes[s->route_count++];
    strncpy(r->path_prefix, prefix, MAX_NAME_LEN - 1);
    r->path_prefix[MAX_NAME_LEN - 1] = '\0';
    r->backend_count = (count > MAX_BACKENDS) ? MAX_BACKENDS : count;
    for (size_t i = 0; i < r->backend_count; i++) {
        r->backends[i] = backends[i];
    }
}

static void snapshot_release(config_snapshot_t* s) {
    if (!s) return;
    if (atomic_fetch_sub_explicit(&s->ref_count, 1, memory_order_acq_rel) == 1) {
        /* Останній читач або потік управління звільнив зліпок */
        free(s);
    }
}

/* =========================================================================
   ШВИДКИЙ ШЛЯХ (Data Plane Worker): обробка запитів без м'ютексів
   ========================================================================= */
const char* data_plane_route_request(const char* request_path) {
    /* 1. Атомарно отримуємо поточний зліпок із семантикою acquire */
    config_snapshot_t* snap = atomic_load_explicit(&g_active_config, memory_order_acquire);
    if (!snap) return NULL;

    /* 2. Захоплюємо посилання на зліпок, щоб потік управління не звільнив пам'ять */
    atomic_fetch_add_explicit(&snap->ref_count, 1, memory_order_relaxed);

    const char* selected_backend = "503_SERVICE_UNAVAILABLE";

    /* 3. Пошук відповідного маршруту у незмінній структурі */
    for (size_t i = 0; i < snap->route_count; i++) {
        const route_rule_t* r = &snap->routes[i];
        if (strncmp(request_path, r->path_prefix, strlen(r->path_prefix)) == 0) {
            /* Обираємо перший здоровий бекенд */
            for (size_t j = 0; j < r->backend_count; j++) {
                if (r->backends[j].is_healthy) {
                    selected_backend = r->backends[j].name;
                    break;
                }
            }
            break;
        }
    }

    /* 4. Звільняємо посилання після завершення обробки */
    snapshot_release(snap);
    return selected_backend;
}

void* data_plane_worker(void* arg) {
    int worker_id = *(int*)arg;
    uint64_t processed = 0;

    while (atomic_load_explicit(&g_running, memory_order_relaxed)) {
        const char* target = data_plane_route_request("/api/v1/checkout");
        if (target) processed++;
        usleep(50); /* Імітація надходження наступного мережевого пакета */
    }
    printf("[Data Plane Worker %d] Завершено. Оброблено запитів: %llu\n", worker_id, (unsigned long long)processed);
    return NULL;
}

/* =========================================================================
   КОНТУР УПРАВЛІННЯ (Control Plane Thread): асинхронне оновлення
   ========================================================================= */
void control_plane_publish_update(uint64_t new_version, bool add_canary) {
    /* 1. Створюємо та наповнюємо новий зліпок повністю ізольовано */
    config_snapshot_t* new_snap = snapshot_create(new_version);
    if (!new_snap) return;

    backend_t backends[2] = {
        { .name = "srv-prod-primary:8080", .weight = 100, .is_healthy = true },
        { .name = "srv-prod-canary:8080",  .weight = 10,  .is_healthy = add_canary }
    };
    snapshot_add_route(new_snap, "/api/v1", backends, add_canary ? 2 : 1);

    /* 2. Атомарно замінюємо активний покажчик з бар'єром release */
    config_snapshot_t* old_snap = atomic_exchange_explicit(&g_active_config, new_snap, memory_order_acq_rel);

    printf("[Control Plane] Опубліковано зліпок v%llu (канарка: %s)\n",
           (unsigned long long)new_version, add_canary ? "Увімкнено" : "Вимкнено");

    /* 3. Звільняємо посилання старого зліпка від імені контролера */
    if (old_snap) {
        snapshot_release(old_snap);
    }
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <atomic>
#include <thread>
#include <chrono>
#include <span>

struct Backend {
    std::string endpoint;
    uint32_t weight{100};
    bool is_healthy{true};
};

struct RouteRule {
    std::string path_prefix;
    std::vector<Backend> backends;
};

// Незмінний зліпок конфігурації (Immutable Snapshot)
class ConfigSnapshot {
public:
    explicit ConfigSnapshot(uint64_t version, std::vector<RouteRule> routes)
        : version_(version), routes_(std::move(routes)) {}

    [[nodiscard]] uint64_t version() const noexcept { return version_; }

    [[nodiscard]] std::string_view match_route(std::string_view request_path) const noexcept {
        for (const auto& route : routes_) {
            if (request_path.starts_with(route.path_prefix)) {
                for (const auto& backend : route.backends) {
                    if (backend.is_healthy) {
                        return backend.endpoint;
                    }
                }
            }
        }
        return "503_SERVICE_UNAVAILABLE";
    }

private:
    uint64_t version_;
    std::vector<RouteRule> routes_;
};

// Маршрутизатор із розділеними площинами
class DecoupledRouter {
public:
    DecoupledRouter() = default;

    // =========================================================================
    // ШВИДКИЙ ШЛЯХ (Data Plane): нуль м'ютексів, потокобезпечно через shared_ptr
    // =========================================================================
    [[nodiscard]] std::string_view route_request(std::string_view path) const noexcept {
        // std::atomic_load для std::shared_ptr є потокобезпечним (C++20 std::atomic<std::shared_ptr<T>>)
        std::shared_ptr<const ConfigSnapshot> snap = std::atomic_load_explicit(&active_config_, std::memory_order_acquire);
        if (!snap) [[unlikely]] {
            return "500_NO_CONFIG";
        }
        return snap->match_route(path);
    }

    // =========================================================================
    // КОНТУР УПРАВЛІННЯ (Control Plane): фонова підготовка та атомарна заміна
    // =========================================================================
    void update_topology(uint64_t new_version, std::vector<RouteRule> new_routes) {
        // 1. Створюємо новий незмінний об'єкт у пам'яті
        auto candidate = std::make_shared<const ConfigSnapshot>(new_version, std::move(new_routes));

        // 2. Атомарно замінюємо покажчик з бар'єром пам'яті release-acquire
        std::atomic_store_explicit(&active_config_, candidate, std::memory_order_release);

        std::cout << "[Control Plane C++] Успішно оновлено конфігурацію до версії v" 
                  << new_version << "\n";
    }

private:
    std::shared_ptr<const ConfigSnapshot> active_config_{nullptr};
};
```
:::

## Детальний розбір синхронізації та бар'єрів пам'яті

### Семантика впорядкування Release-Acquire

Для коректної передачі даних між процесорними ядрами без використання повільних системних викликів ядра операційної системи застосовується парна семантика впорядкування пам'яті (Memory Ordering):

1. **`std::memory_order_release` на боці Control Plane:**
   Коли потік управління формує новий зліпок конфігурації `Candidate Snapshot B`, він записує в пам'ять десятки або сотні полів (назви адрес, масиви маршрутів, бітові маски прапорців здоров'я).
   Сучасні суперскалярні процесори (x86_64, ARM64) та оптимізуючі компілятори можуть перевпорядковувати операції запису в пам'ять задля прискорення. Бар'єр `release` гарантує:
   * Жоден запис у пам'ять, виконаний **до** бар'єра, не може бути винесений процесором **після** атомарного збереження покажчика.
   * Усі записи в структуру `Snapshot B` скидаються в кеш-ієрархію процесора до того, як покажчик `g_active_config` стане видимим для інших процесорних ядер.

2. **`std::memory_order_acquire` на боці Data Plane:**
   Коли робочий потік вичитує покажчик `g_active_config`, бар'єр `acquire` встановлює парний синхронізаційний зв'язок (synchronizes-with) з операцією `release`.
   * Жодне читання полів структури `Snapshot B` не може бути виконане процесором спекулятивно до завершення вичитування самого покажчика.
   * Робочий потік гарантовано бачить повністю сконструйований, цілісний та валідний об'єкт конфігурації.

### Порівняння стратегій утилізації пам'яті: Refcounting проти RCU та EBR

У наведеній реалізації використано атомарний підрахунок посилань (Atomic Reference Counting). У промислових системах надвисокої продуктивності застосовуються й інші неблокуючі стратегії звільнення пам'яті:

* **Epoch-Based Reclamation (EBR):** Система підтримує глобальний лічильник епох (0, 1, 2). Кожен робочий потік під час обробки пакета реєструє свій номер епохи. Пам'ять старого зліпка деалокується лише тоді, коли всі активні потоки перейшли в новіші епохи. Перевага EBR — повна відсутність атомарних операцій на шляху читання, що виключає навіть мінімальний оверхед `atomic_fetch_add`.
* **Ядерний RCU в Linux (Read-Copy-Update):** Робочий потік огортає критичну секцію викликами `rcu_read_lock()` та `rcu_read_unlock()`, які в просторі ядра є практично безкоштовними (відключення витіснення планувальника). Потік управління викликає `synchronize_rcu()`, що блокує потік оновлення до моменту, поки всі ядра не пройдуть точку перемикання контексту (Quiescent State).
* **Hazard Pointers:** Кожен робочий потік записує покажчик на об'єкт, який він зараз читає, у локальну комірку масиву захисних покажчиків (Hazard Pointer). Потік управління сканує цей масив перед видаленням об'єкта.

### Життєвий цикл пам'яті та захист від сплесків оновлень

Оскільки робочі потоки площини даних захоплюють посилання на зліпок перед початком пошуку маршруту, стара конфігурація `Snapshot A` продовжує безпечно існувати в пам'яті навіть тоді, коли площина управління вже послідовно опублікувала версії `Snapshot B`, `C` чи `D`.

Коли останній робочий потік, що обслуговував довгий запит на старій версії, завершує роботу і викликає `snapshot_release()`, лічильник посилань `ref_count` досягає нуля, і пам'ять структури деалокується.

У варіанті C++ цю логіку автоматично бере на себе механізм `std::shared_ptr` у поєднанні з підтримкою атомарних операцій над розумними покажчиками (`std::atomic<std::shared_ptr<T>>` у C++20), що усуває людський фактор ручного керування пам'яттю та виключає витоки ресурсів або виникнення висячих покажчиків (Dangling Pointers).
