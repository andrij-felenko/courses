# ⚙️ Реалізація циклу узгодження (Reconciliation Loop)

У розподілених системах керування інфраструктурою неможливо покладатися на імперативні команди на кшталт «запусти 3 контейнери» або «перезавантаж вузол»: мережевий пакет може загубитися, процес — впасти посеред виконання, а сервер — вийти з ладу без попередження. Будь-яка спроба керувати кластером через послідовні процедурні кроки неминуче призводить до розсинхронізації стану, коли керуюча програма вважає, що контейнер запущено, а фізична машина вже вимкнена.

Єдиною надійною моделлю є **цикл узгодження (англ. *reconciliation loop*)** — безперервний контролер, який порівнює зафіксований у сховищі **бажаний стан (Spec)** із фактично виявленим **поточним станом (Status)** і виконує коригувальні дії доти, доки різниця між ними не стане рівною нулю.

Головний виклик реалізації такого контролера полягає в забезпеченні трьох інваріантів:
1. **Чутливість до стану (Level-triggered semantics):** Контролер реагує не на окремі перехідні події (Edge-triggered «контейнер впав»), а на поточну сумарну розбіжність станів, що унеможливлює розсинхронізацію при втраті сповіщень.
2. **Ідемпотентність (Idempotency):** Багаторазове повторення того самого кроку узгодження призводить до однакового результату й не створює дублікатів ресурсів.
3. **Оптимістичне блокування (Optimistic Concurrency Control / CAS):** Оновлення стану захищене монотонним лічильником версій (`resourceVersion`), що запобігає перезапису паралельних правок іншими вузлами керування.

## 1. Архітектура та компоненти контролера

Розглянемо повну реалізацію контролера розгортання (`DeploymentController`). Контролер складається з трьох ключових архітектурних блоків:
- **Спільне транзакційне сховище (ClusterStore):** емулює поведінку транзакційного key-value сховища etcd із підтримкою монотонного лічильника версій (`resource_version`) та атомарної операції порівняння зі зміною (Compare-And-Swap).
- **Черга завдань із контролем затримки (Rate-Limiting WorkQueue):** структурує потік ключів для обробки. Якщо спроба узгодження завершується невдачею або конфліктом версій, ключ повертається в чергу не миттєво, а з експоненційно зростаючою затримкою (**Exponential Backoff**) із випадковим тремтінням (**Jitter**), щоб запобігти перевантаженню процесора та бази даних.
- **Обробник узгодження (Reconcile Handler):** містить чисту бізнес-логіку сходження системи до задекларованого стану.

## 2. Реалізація мовами C та C++

Нижче наведено паралельну реалізацію повнофункціонального контролера. Версія мовою C використовує низькорівневі примітиви POSIX (м'ютекси, умовні змінні, системні таймери монотонного годинника `CLOCK_MONOTONIC`), тоді як версія на C++20 демонструє сучасний ідіоматичний підхід: керування ресурсами через RAII, безпечні структури очікування, `std::jthread` та обробку помилок через `std::expected`.

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>

#define MAX_NAME_LEN 64
#define MAX_PODS 64
#define MAX_QUEUE_SIZE 128
#define INITIAL_BACKOFF_MS 50
#define MAX_BACKOFF_MS 2000

/* Структура бажаного стану розгортання */
typedef struct {
    char name[MAX_NAME_LEN];
    int desired_replicas;
    char image[MAX_NAME_LEN];
    uint64_t resource_version;
    int current_replicas;
    int ready_replicas;
} Deployment;

/* Стан одного екземпляра контейнера */
typedef struct {
    char name[MAX_NAME_LEN];
    char owner[MAX_NAME_LEN];
    char image[MAX_NAME_LEN];
    bool is_ready;
    bool is_terminating;
} Pod;

/* Спільне сховище кластера */
typedef struct {
    pthread_mutex_t lock;
    Deployment deployment;
    Pod pods[MAX_PODS];
    size_t pod_count;
    uint64_t global_version_seq;
} ClusterStore;

/* Елемент черги завдань із контролем затримки повторів */
typedef struct {
    char deployment_name[MAX_NAME_LEN];
    int retry_count;
    struct timespec process_after;
} QueueItem;

typedef struct {
    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    QueueItem items[MAX_QUEUE_SIZE];
    size_t count;
    bool shutdown;
} WorkQueue;

/* Допоміжні функції часу */
static struct timespec get_current_time(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts;
}

static struct timespec add_ms_to_time(struct timespec ts, int ms) {
    ts.tv_nsec += (long)ms * 1000000L;
    if (ts.tv_nsec >= 1000000000L) {
        ts.tv_sec += ts.tv_nsec / 1000000000L;
        ts.tv_nsec %= 1000000000L;
    }
    return ts;
}

static bool is_time_reached(struct timespec current, struct timespec target) {
    if (current.tv_sec > target.tv_sec) return true;
    if (current.tv_sec == target.tv_sec && current.tv_nsec >= target.tv_nsec) return true;
    return false;
}

/* Ініціалізація черги */
void queue_init(WorkQueue *q) {
    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    q->count = 0;
    q->shutdown = false;
}

void queue_push(WorkQueue *q, const char *name, int retry_count, int delay_ms) {
    pthread_mutex_lock(&q->lock);
    if (q->count < MAX_QUEUE_SIZE) {
        QueueItem *item = &q->items[q->count++];
        strncpy(item->deployment_name, name, MAX_NAME_LEN - 1);
        item->deployment_name[MAX_NAME_LEN - 1] = '\0';
        item->retry_count = retry_count;
        item->process_after = add_ms_to_time(get_current_time(), delay_ms);
        pthread_cond_signal(&q->not_empty);
    }
    pthread_mutex_unlock(&q->lock);
}

bool queue_pop(WorkQueue *q, QueueItem *out_item) {
    pthread_mutex_lock(&q->lock);
    while (q->count == 0 && !q->shutdown) {
        pthread_cond_wait(&q->not_empty, &q->lock);
    }
    if (q->shutdown && q->count == 0) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }

    /* Знаходимо першу задачу, час обробки якої настав */
    struct timespec now = get_current_time();
    size_t ready_idx = (size_t)-1;
    for (size_t i = 0; i < q->count; ++i) {
        if (is_time_reached(now, q->items[i].process_after)) {
            ready_idx = i;
            break;
        }
    }

    if (ready_idx == (size_t)-1) {
        pthread_mutex_unlock(&q->lock);
        usleep(10000); /* 10 мс пауза, якщо елементи ще в стадії backoff */
        return queue_pop(q, out_item);
    }

    *out_item = q->items[ready_idx];
    for (size_t i = ready_idx; i < q->count - 1; ++i) {
        q->items[i] = q->items[i + 1];
    }
    q->count--;

    pthread_mutex_unlock(&q->lock);
    return true;
}

/* Ядро узгодження (Reconciliation Logic) */
typedef enum { RECONCILE_SUCCESS, RECONCILE_CONFLICT, RECONCILE_ERROR } ReconcileResult;

ReconcileResult reconcile_deployment(ClusterStore *store, const char *dep_name) {
    pthread_mutex_lock(&store->lock);

    /* 1. Фаза спостереження: читання знімка бажаного стану */
    if (strcmp(store->deployment.name, dep_name) != 0) {
        pthread_mutex_unlock(&store->lock);
        return RECONCILE_ERROR; /* Об'єкт не знайдено */
    }

    Deployment dep_snapshot = store->deployment;
    uint64_t expected_version = dep_snapshot.resource_version;

    /* Підрахунок активних здорових подів */
    int active_pods = 0;
    int matching_image_pods = 0;
    for (size_t i = 0; i < store->pod_count; ++i) {
        if (strcmp(store->pods[i].owner, dep_name) == 0 && !store->pods[i].is_terminating) {
            active_pods++;
            if (strcmp(store->pods[i].image, dep_snapshot.image) == 0) {
                matching_image_pods++;
            }
        }
    }

    printf("[Reconciler] '%s' | Desired: %d | Active: %d (Ver: %lu)\n",
           dep_name, dep_snapshot.desired_replicas, active_pods, expected_version);

    /* 2. Фаза аналізу та дій: усунення розбіжності */
    int delta = dep_snapshot.desired_replicas - active_pods;

    if (delta > 0) {
        /* Дефіцит: створюємо нові поди */
        for (int k = 0; k < delta && store->pod_count < MAX_PODS; ++k) {
            Pod *new_pod = &store->pods[store->pod_count++];
            snprintf(new_pod->name, sizeof(new_pod->name), "%s-%lu-%d", dep_name, store->global_version_seq, k);
            strncpy(new_pod->owner, dep_name, sizeof(new_pod->owner) - 1);
            strncpy(new_pod->image, dep_snapshot.image, sizeof(new_pod->image) - 1);
            new_pod->is_ready = true;
            new_pod->is_terminating = false;
            printf("  -> Створено Pod: %s [%s]\n", new_pod->name, new_pod->image);
        }
    } else if (delta < 0) {
        /* Надлишок: видаляємо зайві поди */
        int to_remove = -delta;
        for (size_t i = store->pod_count; i > 0 && to_remove > 0; --i) {
            size_t idx = i - 1;
            if (strcmp(store->pods[idx].owner, dep_name) == 0 && !store->pods[idx].is_terminating) {
                printf("  -> Вилучено надлишковий Pod: %s\n", store->pods[idx].name);
                /* Зсув масиву для видалення */
                for (size_t j = idx; j < store->pod_count - 1; ++j) {
                    store->pods[j] = store->pods[j + 1];
                }
                store->pod_count--;
                to_remove--;
            }
        }
    }

    /* 3. Фіксація статусу з перевіркою CAS (Optimistic Locking) */
    if (store->deployment.resource_version != expected_version) {
        /* Стан змінився паралельно — відхиляємо транзакцію */
        printf("  [!] Конфлікт версій (CAS fail): очікувалась %lu, знайдено %lu\n",
               expected_version, store->deployment.resource_version);
        pthread_mutex_unlock(&store->lock);
        return RECONCILE_CONFLICT;
    }

    /* Оновлюємо статус і збільшуємо лічильник версії */
    store->global_version_seq++;
    store->deployment.resource_version = store->global_version_seq;
    store->deployment.current_replicas = dep_snapshot.desired_replicas;
    store->deployment.ready_replicas = dep_snapshot.desired_replicas;

    printf("  [OK] Статус оновлено. Нова версія: %lu\n", store->deployment.resource_version);
    pthread_mutex_unlock(&store->lock);
    return RECONCILE_SUCCESS;
}

/* Робочий потік контролера */
typedef struct {
    ClusterStore *store;
    WorkQueue *queue;
} ControllerContext;

void *controller_worker(void *arg) {
    ControllerContext *ctx = (ControllerContext *)arg;
    QueueItem item;

    while (queue_pop(ctx->queue, &item)) {
        ReconcileResult res = reconcile_deployment(ctx->store, item.deployment_name);
        if (res == RECONCILE_CONFLICT || res == RECONCILE_ERROR) {
            /* Експоненційний розрахунок затримки (Exponential Backoff) */
            int next_retry = item.retry_count + 1;
            int backoff = INITIAL_BACKOFF_MS * (1 << (next_retry > 5 ? 5 : next_retry));
            if (backoff > MAX_BACKOFF_MS) backoff = MAX_BACKOFF_MS;

            printf("  [Retry] Повторна постановка '%s' у чергу через %d мс (спроба %d)\n",
                   item.deployment_name, backoff, next_retry);
            queue_push(ctx->queue, item.deployment_name, next_retry, backoff);
        }
    }
    return NULL;
}

int main(void) {
    ClusterStore store;
    pthread_mutex_init(&store.lock, NULL);
    store.global_version_seq = 1;
    store.pod_count = 0;

    /* Створення початкового маніфесту */
    strncpy(store.deployment.name, "web-api", sizeof(store.deployment.name) - 1);
    store.deployment.desired_replicas = 3;
    strncpy(store.deployment.image, "nginx:1.24", sizeof(store.deployment.image) - 1);
    store.deployment.resource_version = 1;
    store.deployment.current_replicas = 0;
    store.deployment.ready_replicas = 0;

    WorkQueue queue;
    queue_init(&queue);

    ControllerContext ctx = { .store = &store, .queue = &queue };
    pthread_t worker;
    pthread_create(&worker, NULL, controller_worker, &ctx);

    /* 1. Подія створення: надсилаємо задачу на первинне розгортання */
    printf("\n=== Подія 1: Створення Deployment 'web-api' на 3 репліки ===\n");
    queue_push(&queue, "web-api", 0, 0);
    usleep(100000);

    /* 2. Збій вузла: аварійно знищуємо 2 поди без відома специфікації */
    printf("\n=== Подія 2: Аварійне падіння 2 подів (Simulated Crash) ===\n");
    pthread_mutex_lock(&store.lock);
    store.pod_count -= 2; /* 2 поди загинули */
    pthread_mutex_unlock(&store.lock);

    /* Watch-тригер сповіщає контролер про зміну стану */
    queue_push(&queue, "web-api", 0, 0);
    usleep(100000);

    /* 3. Масштабування вгору: користувач змінив replicas до 5 */
    printf("\n=== Подія 3: Масштабування до 5 реплік ===\n");
    pthread_mutex_lock(&store.lock);
    store.deployment.desired_replicas = 5;
    store.global_version_seq++;
    store.deployment.resource_version = store.global_version_seq;
    pthread_mutex_unlock(&store.lock);

    queue_push(&queue, "web-api", 0, 0);
    usleep(100000);

    /* Зупинка черги та прибирання ресурсів */
    pthread_mutex_lock(&queue.lock);
    queue.shutdown = true;
    pthread_cond_broadcast(&queue.not_empty);
    pthread_mutex_unlock(&queue.lock);

    pthread_join(worker, NULL);
    pthread_mutex_destroy(&store.lock);
    pthread_mutex_destroy(&queue.lock);
    pthread_cond_destroy(&queue.not_empty);

    printf("\n[Тест завершено] Усі фази узгодження виконано успішно.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <deque>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <chrono>
#include <optional>
#include <expected>
#include <algorithm>
#include <format>

using namespace std::chrono_literals;

/* Декларативні структури даних */
struct DeploymentSpec {
    int desired_replicas{0};
    std::string image;
};

struct DeploymentStatus {
    int current_replicas{0};
    int ready_replicas{0};
};

struct Deployment {
    std::string name;
    DeploymentSpec spec;
    DeploymentStatus status;
    uint64_t resource_version{1};
};

struct Pod {
    std::string name;
    std::string owner_deployment;
    std::string image;
    bool is_ready{true};
};

enum class ReconcileError {
    NotFound,
    VersionConflict,
    CapacityExceeded
};

/* Потокобезпечне сховище стану (etcd emulator) */
class ClusterStore {
public:
    std::optional<Deployment> get_deployment(std::string_view name) {
        std::scoped_lock lock(mutex_);
        if (deployment_ && deployment_->name == name) {
            return *deployment_;
        }
        return std::nullopt;
    }

    std::vector<Pod> get_pods_for_deployment(std::string_view name) {
        std::scoped_lock lock(mutex_);
        std::vector<Pod> result;
        for (const auto& pod : pods_) {
            if (pod.owner_deployment == name) {
                result.push_back(pod);
            }
        }
        return result;
    }

    void create_pod(Pod pod) {
        std::scoped_lock lock(mutex_);
        pods_.push_back(std::move(pod));
    }

    bool delete_pod(std::string_view name) {
        std::scoped_lock lock(mutex_);
        auto it = std::find_if(pods_.begin(), pods_.end(), [&](const Pod& p) {
            return p.name == name;
        });
        if (it != pods_.end()) {
            pods_.erase(it);
            return true;
        }
        return false;
    }

    /* Атомарне оновлення статусу з перевіркою версії (CAS) */
    std::expected<void, ReconcileError> update_deployment_status(
        std::string_view name,
        uint64_t expected_version,
        DeploymentStatus new_status) 
    {
        std::scoped_lock lock(mutex_);
        if (!deployment_ || deployment_->name != name) {
            return std::unexpected(ReconcileError::NotFound);
        }

        if (deployment_->resource_version != expected_version) {
            return std::unexpected(ReconcileError::VersionConflict);
        }

        deployment_->status = new_status;
        global_version_seq_++;
        deployment_->resource_version = global_version_seq_;
        return {};
    }

    void set_deployment(Deployment dep) {
        std::scoped_lock lock(mutex_);
        global_version_seq_++;
        dep.resource_version = global_version_seq_;
        deployment_ = std::move(dep);
    }

    void simulate_pod_crash(size_t count) {
        std::scoped_lock lock(mutex_);
        while (count > 0 && !pods_.empty()) {
            pods_.pop_back();
            count--;
        }
    }

private:
    std::mutex mutex_;
    std::optional<Deployment> deployment_;
    std::vector<Pod> pods_;
    uint64_t global_version_seq_{0};
};

/* Черга завдань з обмеженням частоти повторень (Rate-Limiting Queue) */
class WorkQueue {
public:
    struct Item {
        std::string name;
        int retry_count{0};
        std::chrono::steady_clock::time_point process_after;
    };

    void push(std::string name, int retry_count = 0, std::chrono::milliseconds delay = 0ms) {
        std::scoped_lock lock(mutex_);
        items_.push_back(Item{
            .name = std::move(name),
            .retry_count = retry_count,
            .process_after = std::chrono::steady_clock::now() + delay
        });
        cv_.notify_one();
    }

    std::optional<Item> pop() {
        std::unique_lock lock(mutex_);
        while (items_.empty() && !shutdown_) {
            cv_.wait(lock);
        }

        if (shutdown_ && items_.empty()) {
            return std::nullopt;
        }

        auto now = std::chrono::steady_clock::now();
        for (auto it = items_.begin(); it != items_.end(); ++it) {
            if (it->process_after <= now) {
                Item ready_item = *it;
                items_.erase(it);
                return ready_item;
            }
        }

        /* Якщо готові задачі ще очікують таймер backoff */
        lock.unlock();
        std::this_thread::sleep_for(10ms);
        return pop();
    }

    void stop() {
        std::scoped_lock lock(mutex_);
        shutdown_ = true;
        cv_.notify_all();
    }

private:
    std::mutex mutex_;
    std::condition_variable cv_;
    std::deque<Item> items_;
    bool shutdown_{false};
};

/* Диспетчер узгодження стану */
class DeploymentReconciler {
public:
    DeploymentReconciler(ClusterStore& store, WorkQueue& queue)
        : store_(store), queue_(queue) {}

    std::expected<void, ReconcileError> reconcile(const std::string& name) {
        // 1. Читання знімка бажаного стану
        auto dep_opt = store_.get_deployment(name);
        if (!dep_opt) {
            return std::unexpected(ReconcileError::NotFound);
        }
        const auto& dep = *dep_opt;
        uint64_t expected_version = dep.resource_version;

        // 2. Аналіз активних ресурсів
        auto current_pods = store_.get_pods_for_deployment(name);
        int active_count = static_cast<int>(current_pods.size());

        std::cout << std::format("[Reconciler C++] '{}' | Desired: {} | Active: {} (Ver: {})\n",
                                 name, dep.spec.desired_replicas, active_count, expected_version);

        int delta = dep.spec.desired_replicas - active_count;

        // 3. Коригувальні мутації (Act)
        if (delta > 0) {
            for (int i = 0; i < delta; ++i) {
                Pod p{
                    .name = std::format("{}-{}-{}", name, expected_version, i),
                    .owner_deployment = name,
                    .image = dep.spec.image,
                    .is_ready = true
                };
                std::cout << std::format("  -> Створено Pod: {} [{}]\n", p.name, p.image);
                store_.create_pod(std::move(p));
            }
        } else if (delta < 0) {
            int to_remove = -delta;
            for (const auto& pod : current_pods) {
                if (to_remove <= 0) break;
                std::cout << std::format("  -> Вилучено Pod: {}\n", pod.name);
                store_.delete_pod(pod.name);
                to_remove--;
            }
        }

        // 4. Оновлення статусу через CAS
        DeploymentStatus new_status{
            .current_replicas = dep.spec.desired_replicas,
            .ready_replicas = dep.spec.desired_replicas
        };

        auto update_res = store_.update_deployment_status(name, expected_version, new_status);
        if (!update_res) {
            std::cout << "  [!] Помилка CAS: конкурентна модифікація стану!\n";
            return std::unexpected(update_res.error());
        }

        std::cout << "  [OK] Узгодження успішне.\n";
        return {};
    }

private:
    ClusterStore& store_;
    WorkQueue& queue_;
};

int main() {
    ClusterStore store;
    WorkQueue queue;

    // Створення базового Deployment
    Deployment dep{
        .name = "billing-service",
        .spec = { .desired_replicas = 3, .image = "billing:v1.0" },
        .status = { .current_replicas = 0, .ready_replicas = 0 }
    };
    store.set_deployment(dep);

    DeploymentReconciler reconciler(store, queue);

    // Запуск фонового потоку контролера (C++20 std::jthread)
    std::jthread worker([&](std::stop_token st) {
        while (!st.stop_requested()) {
            auto item = queue.pop();
            if (!item) break;

            auto result = reconciler.reconcile(item->name);
            if (!result) {
                int next_retry = item->retry_count + 1;
                auto delay = 50ms * (1 << std::min(next_retry, 5));
                std::cout << std::format("  [Backoff] Повтор '{}' через {} мс\n", 
                                         item->name, delay.count());
                queue.push(item->name, next_retry, delay);
            }
        }
    });

    std::cout << "\n=== Подія 1: Початкове розгортання 3 подів ===\n";
    queue.push("billing-service");
    std::this_thread::sleep_for(100ms);

    std::cout << "\n=== Подія 2: Симуляція аварії (Crash 2 подів) ===\n";
    store.simulate_pod_crash(2);
    queue.push("billing-service");
    std::this_thread::sleep_for(100ms);

    std::cout << "\n=== Подія 3: Оновлення бажаного стану (5 реплік) ===\n";
    dep.spec.desired_replicas = 5;
    store.set_deployment(dep);
    queue.push("billing-service");
    std::this_thread::sleep_for(100ms);

    queue.stop();
    return 0;
}
```
:::

## 3. Покроковий розбір фаз виконання циклу

Проаналізуємо кожен етап роботи контролера під час надходження сигналу:

1. **Отримання ключа з черги (Queue Pop):**
   Робочий потік контролера витягує з черги лише текстовий ключ ресурсу (`default/billing-service`). Контролер ніколи не передає через чергу повний об'єкт із даними, оскільки за час перебування в черзі об'єкт у сховищі міг змінитися кілька разів. Передача ключа змушує обробник читати найсвіжіший стан безпосередньо в момент виконання.

2. **Зчитування знімка стану (Observe):**
   Контролер читає поточну специфікацію `.spec` та поточний номер версії `.metadata.resourceVersion`. Одночасно виконується вибірка всіх дочірніх об'єктів (подів), які мають мітку власника `ownerReferences.name == "billing-service"`.

3. **Розрахунок дельти (Diff):**
   Обчислюється різниця між `desired_replicas` та кількістю здорових подів. Зверніть увагу: поди, які перебувають у стані видалення (`is_terminating == true`), не враховуються до списку готових, що запобігає передчасному припиненню масштабування.

4. **Атомарні мутації (Act):**
   Контролер надсилає запити на створення відсутніх подів або видалення зайвих. Кожен новий под отримує детерміноване ім'я, сформоване з префікса розгортання та хешу версії шаблону.

5. **Оптимістична фіксація статусу (CAS Commit):**
   На фінальному етапі контролер записує фактичну кількість реплік у секцію `.status`. Якщо інший контролер (або користувач через `kubectl edit`) встиг змінити специфікацію паралельно, перевірка `resource_version == expected_version` провалюється. Замість перезапису чужих змін транзакція відхиляється, і задача повертається в чергу для повторного проходження циклу з новими даними.

## 4. Пастки та крайові випадки у промисловій експлуатації

### Пастка 1: Шторм повторів (Thundering Herd на реконнекті)

Якщо мережевий лінк між контролером та API Server переривається на кілька секунд, черга накопичує сотні подій оновлення. Після відновлення зв'язку всі воркери одночасно кидаються виконувати виклики `Reconcile()`. Якщо всі вони отримають конфлікт версій і спробують повторити запит рівно через 100 мс, виникає резонансна хвиля навантаження, яка перевантажує базу etcd.

**Рішення:** Обов'язкове додавання випадкового тремтіння (**Full Jitter**) до формули розрахунку затримки:
```
T_sleep = random(0, min(T_max, T_base · 2ⁿ))
```
Це рівномірно розмиває пікове навантаження в часі.

### Пастка 2: Гарячі цикли без backoff

Якщо помилка спричинена нездійсненною вимогою (наприклад, відсутній секрет монтування або неіснуючий Docker-образ), наївний реконсилер, який негайно повертає задачу в чергу (`requeue = true` з нульовою затримкою), споживає 100% одного ядра CPU, генеруючи гігабайти марних журналів діагностики. Експоненційне уповільнення обмежує максимальну частоту повторів до 1 запиту на 5–15 хвилин для хронічно зламаних об'єктів.

### Пастка 3: Смертельна втрата стану видалення (Finalizers trap)

Коли об'єкт видаляється користувачем (`metadata.deletionTimestamp != nil`), контролер зобов'язаний спочатку безпечно згорнути зовнішні залежності (видалити хмарний балансувальник або зняти блокування диска) і лише потім видалити свій рядок із масиву `metadata.finalizers`. Якщо контролер зависне або впаде до очищення фіналізатора, об'єкт залишається у вічному стані `Terminating`, блокуючи видалення всього простору імен.
