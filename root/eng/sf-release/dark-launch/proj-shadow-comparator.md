# ⚙️ Побудова асинхронного тіньового маршрутизатора та компаратора

Під час заміни критичних алгоритмів або підсистем обробки даних у високонавантажених бекенд-сервісах головний інженерний виклик полягає в гарантуванні абсолютної функціональної відповідності нової реалізації старому коду без створення ризиків для живих користувачів. Звичайне тестування на синтетичних тестових стендах часто пропускає рідкісні крайові випадки: специфічні комбінації параметрів запиту, нетипові кодування символів, переповнення числових типів на граничних балансах та неочікувані послідовності викликів у розподіленому середовищі.

Темний запуск (англ. *dark launch*) у формі патерну Scientist розв'язує цю проблему через паралельне виконання старої (контрольної) та нової (експериментальної або кандидатської) гілок коду на реальному продакшен-трафіку. Однак наївна реалізація у вигляді послідовного виклику обох функцій на головному робочому потоці порушує базовий закон експлуатаційної надійності: час обробки запиту клієнта подвоюється, а будь-яке зависання, витік пам'яті чи падіння з винятком у новому експериментальному коді негайно призводить до збою для живого користувача.

Щоб темний запуск був повністю безпечним і придатним для високонавантажених систем, архітектура повинна забезпечувати виконання трьох фундаментальних інваріантів:
1. **Інваріант нульової затримки для користувача:** контрольна версія виконується негайно і повертає відповідь клієнту без найменшого очікування результатів тіньового кандидата чи синхронізації з чергою.
2. **Інваріант повної ізоляції збоїв:** будь-яка помилка, аварійний виняток, зависання чи вичерпання ресурсів у тіньовому кандидаті перехоплюється у фоновому середовищі й жодним чином не впливає на статус або тіло відповіді клієнта.
3. **Інваріант захисту від перевантаження (англ. *bounded backpressure*):** тіньовий виконавець використовує фіксовану неблокуючу чергу; у разі сплеску трафіку або сповільнення кандидата надлишкові тіньові завдання безпечно відкидаються за політикою *drop-on-overflow*, не споживаючи зайву пам'ять і не створюючи зворотного тиску на головні робочі потоки сервісу.

## Архітектура фонового диспетчера та компаратора

Архітектура промислового тіньового рушія складається з чотирьох взаємопов'язаних рівнів обробки:

```
[ Клієнтський HTTP/gRPC запит ]
               │
               ▼
   [ Головний потік обробника ]
               │
               ├── 1. Виклик ControlFn (Синхронно) ──> Результат v1 ──> [ Відповідь клієнту ]
               │
               └── 2. Фільтр динамічного семплювання (xorshift64)
                               │
                      [ Семпл ухвалено ]
                               │
                               ▼
               [ Неблокуюча кільцева черга BoundedQueue ]
                               │
               ┌───────────────┴───────────────┐
         [ Черга вільна ]              [ Черга заповнена ]
               │                               │
               ▼                               ▼
       Пул потоків Worker               Drop (Метрика пропуску)
               │
               ├── 3. Виклик CandidateFn (Ізольовано в try/catch)
               │         │
               │         ▼
               │   Результат v2 (або помилка)
               │
               └── 4. Нормалізатор та диференційний компаратор
                         │
                         ├── Вилучення timestamp, UUID, hash-seed
                         ├── Звірка float з допуском |a - b| < ε
                         │
                         ▼
             [ Генератор телеметрії та Diff-логів ]
```

### 1. Фільтр швидкого семплювання на рівні процесора
Повне дублювання 100% трафіку не завжди потрібне і на пікових навантаженнях може перевантажити внутрішні залежності. Тіньовий диспетчер повинен підтримувати динамічне регулювання частки семплювання (англ. *sampling rate*) у діапазоні від 0.001% до 100%.

Щоб перевірка семплу на гарячому шляху (англ. *hot path*) не створювала міжядерної конкуренції за спільний стан генератора псевдовипадкових чисел у пам'яті (англ. *cache line bouncing*), використовують швидкі потоково-локальні генератори на базі алгоритму `xorshift64`. Цей алгоритм складається лише з трьох бітових зсувів та операцій XOR над 64-бітним регістром, що займає менше трьох наносекунд процесорного часу і не потребує блокування м'ютексів чи системних викликів.

### 2. Кільцевий буфер фіксованого розміру з вирівнюванням кеш-ліній
Завдання на тіньову перевірку пакуються в легкозважену структуру, що містить глибоку копію вхідного запиту, отриманий результат контрольної гілки та заміряний час її виконання. Постановка в чергу виконується суворо без очікування: якщо ліміт вільних слотів вичерпано, черга не блокує потік, а негайно повертає статус відмови, що інкрементує лічильник скинутих тіньових завдань (англ. *drop counter*).

Для запобігання явищу помилкового спільного використання пам'яті (англ. *false sharing*) змінні індексів голови (`head`) та хвоста (`tail`) кільцевого буфера повинні бути вирівняні по межі 64 байтів (розмір типової лінії кешу процесорів x86-64 та ARM64) за допомогою атрибутів `alignas(64)` або `__attribute__((aligned(64)))`. Це гарантує, що запис у хвіст черги головним потоком не буде скидати з кешу L1 індекс голови, який активно вичитується фоновим потоком-обробником.

### 3. Фоновий пул обробників та контроль часових лімітів
Окремі фонові потоки вичитують завдання з черги, запускають кандидатську функцію, фіксують точний час виконання за монотонним таймером `CLOCK_MONOTONIC` і за потреби зупиняють виконання за таймаутом. Якщо кандидат викидає виняток чи повертає код помилки, формується відповідний запис аварійної телеметрії, але сам процес продовжує стабільну роботу.

У реальних системах для кандидата обов'язково встановлюють жорсткий сторожовий таймер (англ. *watchdog deadline*). Якщо кандидат потрапляє в нескінченний цикл або блокується на завислому мережевому виклику, потік не повинен залишатися заблокованим назавжди, виснажуючи доступні ресурси пулу.

### 4. Нормалізація та семантичне порівняння
Побайтова звірка вихідних структур (`memcmp`) у реальних розподілених системах практично завжди дає хибні спрацьовування. Причинами є динамічні часові мітки створення запису (`created_at`), згенеровані унікальні ідентифікатори (`UUID v4`), випадковий порядок ключів у геш-таблицях та похибки округлення дробових чисел у мікропроцесорних регістрах з різними інструкціями (наприклад, оптимізації FMA). Тому нормалізатор маскує службові поля й порівнює числові значення за формулою відносної або абсолютної похибки:

```text
|v1.amount - v2.amount| ≤ ε · max(1.0, |v1.amount|)
```

## Теорія черг та розрахунок місткості тіньового буфера

Щоб тіньовий диспетчер не відкидав корисні експерименти під час штатної роботи, розмір черги та кількість фонових потоків необхідно проєктувати за законами теорії масового обслуговування (модель `M/M/c/K`, де `M` — пуассонівський потік вхідних запитів з інтенсивністю `λ`, `c` — кількість паралельних робочих потоків, а `K` — гранична місткість буфера).

Нехай сервіс обробляє вхідний потік `λ = 10 000` запитів на секунду. Якщо частка тіньового семплювання налаштована на `s = 10%`, на тіньовий диспетчер надходить потік `λ_shadow = s · λ = 1 000` завдань на секунду.

Якщо середня тривалість виконання одного кандидата становить `T_cand = 2.5` мс, інтенсивність обслуговування одним потоком дорівнює:

```text
μ = 1 / T_cand = 1 / 0.0025 с = 400 завдань / с на потік.
```

Для стабільної роботи без накопичення черги коефіцієнт завантаження пулу `ρ` повинен задовольняти умову `ρ = λ_shadow / (c · μ) < 1.0`. Звідси мінімально необхідна кількість робочих потоків у пулі становить:

```text
c > λ_shadow / μ = 1000 / 400 = 2.5 потоки.
```

Для забезпечення експлуатаційного запасу на випадок короткочасних мікросплесків обирають `c = 4` потоки. При цьому коефіцієнт завантаження становить `ρ = 1000 / (4 · 400) = 0.625`.

Гранична місткість буфера `K` визначає ймовірність втрати завдання під час сплеску трафіку тривалістю `Δt = 100` мс. За цей час до буфера надходить `1000 · 0.1 = 100` завдань, а пул встигає обробити `1600 · 0.1 = 160` завдань. Встановлення місткості `K = 512` гарантує, що ймовірність відкидання завдань `P_drop` під час штатних коливань трафіку становитиме менше ніж `0.001%`.

## Безпека пам'яті під час міжпотокової передачі DTO

Під час передачі структур запитів та відповідей між головним потоком та фоновим пулом виникає важлива проблема володіння пам'яттю (англ. *ownership semantics*). У високонавантажених C++ сервісах часто використовують неволодіючі представлення пам'яті, такі як `std::string_view` або `std::span`, які посилаються на тимчасовий буфер сокета головного потоку.

Якщо передати `std::string_view` у тіньове завдання асинхронного потоку, виникає стан невизначеної поведінки (англ. *undefined behavior / use-after-free*): головний потік завершує обробку запиту клієнта, очищає буфер сокета або повторно використовує його для наступного TCP-пакета, тоді як фоновий потік намагається прочитати дані зі звільненої пам'яті.

Тому структура `ShadowTask` зобов'язана виконувати **глибоке копіювання** (англ. *deep copy*) усіх динамічних полів (використовуючи володіючі типи `std::string`, `std::vector` або виділені буфери фіксованої довжини `char[]` у C). Хоча копіювання створює невеликі накладні витрати на виділення пам'яті, воно гарантує повну ізоляцію життєвого циклу даних між потоками.

## Реалізація на мовах C та C++

Нижче наведено робочий промисловий приклад асинхронного диспетчера темного запуску та компаратора для розрахунку фінансових транзакцій двома мовами програмування.

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
#include <pthread.h>

#define QUEUE_CAPACITY 512
#define MAX_NAME_LEN 64
#define FLOAT_EPSILON 1e-6

/* Вхідні дані фінансового запиту */
typedef struct {
    uint64_t account_id;
    double amount;
    uint32_t currency_code;
    uint64_t client_timestamp_ms;
} TransactionRequest;

/* Результат обробки транзакції */
typedef struct {
    double base_fee;
    double tax_fee;
    double total_charged;
    uint32_t execution_node_id; /* Динамічне службове поле */
    bool is_successful;
} TransactionResult;

/* Сигнатура функції бізнес-логіки */
typedef TransactionResult (*ProcessingFn)(const TransactionRequest* req);

/* Опис окремого тіньового експерименту для черги */
typedef struct {
    char experiment_name[MAX_NAME_LEN];
    TransactionRequest request;
    TransactionResult control_result;
    uint64_t control_duration_us;
    ProcessingFn candidate_fn;
} ShadowTask;

/* Неблокуюча кільцева черга з м'ютексом та умовною змінною */
typedef struct {
    ShadowTask tasks[QUEUE_CAPACITY];
    size_t head;
    size_t tail;
    size_t count;
    size_t total_dropped;
    bool is_terminating;
    pthread_mutex_t lock;
    pthread_cond_t has_items;
} ShadowQueue;

static ShadowQueue g_queue;
static pthread_t g_worker_thread;

/* Отримання поточного монотонного часу в мікросекундах */
static uint64_t get_monotonic_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000ULL + (uint64_t)ts.tv_nsec / 1000ULL;
}

/* Нормалізований компаратор результатів */
static bool compare_transaction_results(const TransactionResult* ctrl,
                                        const TransactionResult* cand,
                                        char* diff_buffer,
                                        size_t diff_buf_size) {
    if (ctrl->is_successful != cand->is_successful) {
        snprintf(diff_buffer, diff_buf_size, "Статус успішності різниться: ctrl=%d, cand=%d",
                 ctrl->is_successful, cand->is_successful);
        return false;
    }

    if (fabs(ctrl->base_fee - cand->base_fee) > FLOAT_EPSILON) {
        snprintf(diff_buffer, diff_buf_size, "Розбіжність base_fee: ctrl=%.6f, cand=%.6f",
                 ctrl->base_fee, cand->base_fee);
        return false;
    }

    if (fabs(ctrl->tax_fee - cand->tax_fee) > FLOAT_EPSILON) {
        snprintf(diff_buffer, diff_buf_size, "Розбіжність tax_fee: ctrl=%.6f, cand=%.6f",
                 ctrl->tax_fee, cand->tax_fee);
        return false;
    }

    if (fabs(ctrl->total_charged - cand->total_charged) > FLOAT_EPSILON) {
        snprintf(diff_buffer, diff_buf_size, "Розбіжність total_charged: ctrl=%.6f, cand=%.6f",
                 ctrl->total_charged, cand->total_charged);
        return false;
    }

    /* execution_node_id є недетермінованим вузловим маршрутом і маскується */
    return true;
}

/* Цикл фонового потоку-обробника */
static void* shadow_worker_routine(void* arg) {
    (void)arg;
    char diff_msg[256];

    while (true) {
        ShadowTask task;

        pthread_mutex_lock(&g_queue.lock);
        while (g_queue.count == 0 && !g_queue.is_terminating) {
            pthread_cond_wait(&g_queue.has_items, &g_queue.lock);
        }

        if (g_queue.is_terminating && g_queue.count == 0) {
            pthread_mutex_unlock(&g_queue.lock);
            break;
        }

        task = g_queue.tasks[g_queue.head];
        g_queue.head = (g_queue.head + 1) % QUEUE_CAPACITY;
        g_queue.count--;
        pthread_mutex_unlock(&g_queue.lock);

        /* Виконання експериментальної функції із заміром затримки */
        uint64_t cand_start_us = get_monotonic_us();
        TransactionResult cand_res = task.candidate_fn(&task.request);
        uint64_t cand_duration_us = get_monotonic_us() - cand_start_us;

        /* Порівняння результатів */
        bool is_match = compare_transaction_results(&task.control_result, &cand_res,
                                                     diff_msg, sizeof(diff_msg));

        if (is_match) {
            printf("[МЕТРИКА ЗБІГУ] Експеримент '%s' (Акаунт: %lu) | Час: ctrl=%lu мкс, cand=%lu мкс\n",
                   task.experiment_name, task.request.account_id,
                   task.control_duration_us, cand_duration_us);
        } else {
            fprintf(stderr, "[РОЗБІЖНІСТЬ!] Експеримент '%s' (Акаунт: %lu) -> %s\n",
                    task.experiment_name, task.request.account_id, diff_msg);
        }
    }
    return NULL;
}

/* Ініціалізація інфраструктури */
void shadow_system_init(void) {
    g_queue.head = 0;
    g_queue.tail = 0;
    g_queue.count = 0;
    g_queue.total_dropped = 0;
    g_queue.is_terminating = false;
    pthread_mutex_init(&g_queue.lock, NULL);
    pthread_cond_init(&g_queue.has_items, NULL);
    pthread_create(&g_worker_thread, NULL, shadow_worker_routine, NULL);
}

/* Зупинка системи та коректне звільнення ресурсів */
void shadow_system_shutdown(void) {
    pthread_mutex_lock(&g_queue.lock);
    g_queue.is_terminating = true;
    pthread_cond_broadcast(&g_queue.has_items);
    pthread_mutex_unlock(&g_queue.lock);

    pthread_join(g_worker_thread, NULL);
    pthread_mutex_destroy(&g_queue.lock);
    pthread_cond_destroy(&g_queue.has_items);
}

/* Головна точка входу темного запуску */
TransactionResult run_with_dark_launch(const char* name,
                                       const TransactionRequest* req,
                                       ProcessingFn control_fn,
                                       ProcessingFn candidate_fn) {
    /* 1. Синхронний запуск контрольного рушія для клієнта */
    uint64_t ctrl_start_us = get_monotonic_us();
    TransactionResult ctrl_res = control_fn(req);
    uint64_t ctrl_duration_us = get_monotonic_us() - ctrl_start_us;

    /* 2. Неблокуюча спроба постановки в тіньову чергу */
    pthread_mutex_lock(&g_queue.lock);
    if (g_queue.count < QUEUE_CAPACITY) {
        ShadowTask* slot = &g_queue.tasks[g_queue.tail];
        strncpy(slot->experiment_name, name, MAX_NAME_LEN - 1);
        slot->experiment_name[MAX_NAME_LEN - 1] = '\0';
        slot->request = *req;
        slot->control_result = ctrl_res;
        slot->control_duration_us = ctrl_duration_us;
        slot->candidate_fn = candidate_fn;

        g_queue.tail = (g_queue.tail + 1) % QUEUE_CAPACITY;
        g_queue.count++;
        pthread_cond_signal(&g_queue.has_items);
    } else {
        g_queue.total_dropped++;
        /* Пропуск записується в лічильники без блокування виклику */
    }
    pthread_mutex_unlock(&g_queue.lock);

    /* 3. Клієнт негайно отримує перевірений результат */
    return ctrl_res;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <functional>
#include <chrono>
#include <cmath>
#include <optional>
#include <format>
#include <utility>

namespace shadow {

constexpr double kEpsilon = 1e-6;

/* Структури предметної області */
struct TransactionRequest {
    uint64_t account_id{0};
    double amount{0.0};
    uint32_t currency_code{980};
    uint64_t timestamp_ms{0};
};

struct TransactionResult {
    double base_fee{0.0};
    double tax_fee{0.0};
    double total_charged{0.0};
    uint32_t execution_node_id{0};
    bool is_successful{false};

    /* Канонічне порівняння з маскуванням службових полів */
    [[nodiscard]] bool matches(const TransactionResult& other) const noexcept {
        if (is_successful != other.is_successful) return false;
        if (std::abs(base_fee - other.base_fee) > kEpsilon) return false;
        if (std::abs(tax_fee - other.tax_fee) > kEpsilon) return false;
        if (std::abs(total_charged - other.total_charged) > kEpsilon) return false;
        return true;
    }
};

/* Шаблонний диспетчер експериментів на сучасному C++20 */
template <typename Request, typename Response>
class ScientistEngine {
public:
    using Handler = std::function<Response(const Request&)>;
    using Comparator = std::function<bool(const Response&, const Response&)>;

    explicit ScientistEngine(size_t max_queue_size = 512)
        : max_capacity_(max_queue_size),
          worker_thread_([this](std::stop_token st) { worker_loop(st); }) {}

    ~ScientistEngine() {
        worker_thread_.request_stop();
        cv_.notify_all();
    }

    ScientistEngine(const ScientistEngine&) = delete;
    ScientistEngine& operator=(const ScientistEngine&) = delete;

    /* Виконання темного запуску: синхронний контроль і асинхронний кандидат */
    Response evaluate(std::string_view name,
                      const Request& req,
                      Handler control_fn,
                      Handler candidate_fn,
                      Comparator comparator = [](const Response& a, const Response& b) {
                          return a.matches(b);
                      }) {
        // 1. Синхронний запуск контрольного рушія
        const auto t0 = std::chrono::steady_clock::now();
        Response control_res = control_fn(req);
        const auto t1 = std::chrono::steady_clock::now();
        const auto ctrl_us = std::chrono::duration_cast<std::chrono::microseconds>(t1 - t0).count();

        // 2. Неблокуюче планування тіньового завдання
        {
            std::lock_guard<std::mutex> lock(queue_mutex_);
            if (task_queue_.size() < max_capacity_) {
                task_queue_.push(ShadowTask{
                    .experiment_name = std::string(name),
                    .request = req,
                    .control_res = control_res,
                    .control_duration_us = static_cast<uint64_t>(ctrl_us),
                    .candidate_fn = std::move(candidate_fn),
                    .comparator = std::move(comparator)
                });
                cv_.notify_one();
            } else {
                dropped_count_++;
            }
        }

        // 3. Негайне повернення контрольного результату клієнту
        return control_res;
    }

    [[nodiscard]] size_t dropped_count() const noexcept {
        return dropped_count_.load();
    }

private:
    struct ShadowTask {
        std::string experiment_name;
        Request request;
        Response control_res;
        uint64_t control_duration_us;
        Handler candidate_fn;
        Comparator comparator;
    };

    void worker_loop(std::stop_token stop_token) {
        while (!stop_token.stop_requested()) {
            ShadowTask current_task;
            {
                std::unique_lock<std::mutex> lock(queue_mutex_);
                cv_.wait(lock, [this, &stop_token] {
                    return !task_queue_.empty() || stop_token.stop_requested();
                });

                if (stop_token.stop_requested() && task_queue_.empty()) {
                    break;
                }

                current_task = std::move(task_queue_.front());
                task_queue_.pop();
            }

            // Безпечне ізольоване виконання кандидата
            try {
                const auto t_start = std::chrono::steady_clock::now();
                Response candidate_res = current_task.candidate_fn(current_task.request);
                const auto t_end = std::chrono::steady_clock::now();
                const auto cand_us = std::chrono::duration_cast<std::chrono::microseconds>(
                    t_end - t_start).count();

                if (current_task.comparator(current_task.control_res, candidate_res)) {
                    std::cout << "[ЗБІГ] Експеримент '" << current_task.experiment_name
                              << "' | Час: ctrl=" << current_task.control_duration_us
                              << "us, cand=" << cand_us << "us\n";
                } else {
                    std::cerr << "[РОЗБІЖНІСТЬ] Експеримент '" << current_task.experiment_name
                              << "': дані відповідей не збігаються!\n";
                }
            } catch (const std::exception& ex) {
                std::cerr << "[ЗБІЙ КАНДИДАТА] Експеримент '" << current_task.experiment_name
                          << "' викинув виняток: " << ex.what() << "\n";
            } catch (...) {
                std::cerr << "[КРИТИЧНИЙ ЗБІЙ] Невідомий виняток у тіньовому кандидаті\n";
            }
        }
    }

    size_t max_capacity_;
    std::atomic<size_t> dropped_count_{0};
    std::queue<ShadowTask> task_queue_;
    std::mutex queue_mutex_;
    std::condition_variable cv_;
    std::jthread worker_thread_;
};

} // namespace shadow
```
:::

## Покрокове простеження життєвого циклу запиту

Розгляньмо послідовність дій під час проходження реального запиту через реалізований диспетчер:

1. **Етап 1: Вхід у точку маршрутизації.**
   Сервіс отримує фінансову транзакцію для акаунту `948102` на суму `1500.00` грн. Викликається функція `run_with_dark_launch` (або метод `evaluate` у C++).

2. **Етап 2: Синхронний контрольний розрахунок.**
   Головний потік викликає функцію `control_fn`. Перевірений алгоритм розраховує комісію `15.00` грн, податок `2.85` грн та підсумкову суму `1517.85` грн. Таймер фіксує тривалість операції: 42 мікросекунди.

3. **Етап 3: Неблокуюче планування тіньового завдання.**
   Головний потік захоплює м'ютекс черги на мікросекунду, перевіряє ліміт слотів і копіює дані запиту разом із контрольним результатом у вільну комірку `tasks[tail]`. Інформується умовна змінна `has_items`, м'ютекс звільняється, і контрольний результат `1517.85` грн негайно повертається клієнту. Загальний час затримки для клієнта збільшився менше ніж на 2 мікросекунди.

4. **Етап 4: Фонова обробка кандидатом.**
   Фоновий потік-робітник прокидається від сигналу умовної змінної, вилучає завдання з черги та викликає експериментальну кандидатську функцію `candidate_fn`. Кандидат використовує новий оптимізований алгоритм із векторними інструкціями. Таймер фіксує виконання за 18 мікросекунд (прискорення у 2.3 раза).

5. **Етап 5: Семантична диференційна перевірка.**
   Компаратор перевіряє отримані поля:
   * `is_successful`: збігається (`true` == `true`).
   * `base_fee`: `|15.000000 - 15.000000| = 0.0 < 10⁻⁶` (збіг).
   * `tax_fee`: `|2.850000 - 2.850000| = 0.0 < 10⁻⁶` (збіг).
   * `total_charged`: `|1517.850000 - 1517.850000| = 0.0 < 10⁻⁶` (збіг).
   * `execution_node_id`: у контролі дорівнює `104`, у кандидата — `208`. Оскільки це поле маскується як недетермінований мережевий маршрут, різниця ігнорується.

6. **Етап 6: Фіксація успіху в системі спостережуваності.**
   Компаратор формує позитивний метричний запис. Лічильник успішних збігів експерименту збільшується в базі часових рядів (Prometheus/StatsD), підтверджуючи коректність та прискорення нового коду на реальних транзакціях.

## Динамічне оновлення конфігурації без перезапуску

У промислових системах параметри темного запуску (відсоток семплювання `sample_rate`, поріг допустимої похибки `epsilon`, таймаут виконання `timeout_ms` та перелік маскованих полів) не повинні бути жорстко зашитими константами у бінарному файлі. Вони мають динамічно оновлюватися через зовнішні системи конфігурації (Consul, etcd, Apache ZooKeeper) на льоту.

Для безпечного зчитування налаштувань без блокування головного потоку застосовують патерн Read-Copy-Update (RCU) або атомарні покажчики `std::atomic<std::shared_ptr<const Config>>` у C++. Головний потік атомарно копіює покажчик на актуальну конфігурацію:

```cpp
struct ExperimentConfig {
    double sampling_rate{0.10};       // 10% семплювання
    double epsilon{1e-6};              // Точність порівняння
    uint32_t timeout_ms{50};           // Жорсткий ліміт виконання
    bool is_enabled{true};             // Головний перемикач
};

class DynamicConfigManager {
public:
    void update_config(ExperimentConfig new_cfg) {
        auto new_ptr = std::make_shared<const ExperimentConfig>(new_cfg);
        std::atomic_store(&active_config_, new_ptr);
    }

    [[nodiscard]] std::shared_ptr<const ExperimentConfig> get() const noexcept {
        return std::atomic_load(&active_config_);
    }

private:
    std::shared_ptr<const ExperimentConfig> active_config_{
        std::make_shared<const ExperimentConfig>()
    };
};
```

Це дозволяє інженеру в разі виявлення сплеску затримок у фоновому кандидаті знизити частку семплювання з 100% до 1% або повністю вимкнути експеримент однією командою в системі керування конфігурацією за лічені мілісекунди без перезапуску сервісу.

## Формат структурованого дампу розбіжностей

Коли компаратор виявляє невідповідність між контролем та кандидатом, запису простого повідомлення про помилку недостатньо для діагностики дефекту. Інженерній команді потрібен повний зріз стану для локального відтворення збою в налагоджувачі.

Компаратор генерує структурований JSON-документ і надсилає його в ізольовану чергу відхилень (англ. *dead-letter queue*):

```json
{
  "timestamp": "2026-08-20T01:35:00.102Z",
  "experiment": "transaction-fee-v2",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "request": {
    "account_id": 948102,
    "amount": 1500.00,
    "currency_code": 980
  },
  "control": {
    "duration_us": 42,
    "base_fee": 15.00,
    "tax_fee": 2.85,
    "total_charged": 1517.85
  },
  "candidate": {
    "duration_us": 18,
    "base_fee": 15.00,
    "tax_fee": 3.00,
    "total_charged": 1518.00
  },
  "diff": {
    "field": "tax_fee",
    "delta": 0.15,
    "reason": "Tax rounding method discrepancy (Bankers Rounding vs Floor)"
  }
}
```

Маючи такий структурований звіт, розробник може створити точковий модульний тест із зазначеними вхідними даними й виправити алгоритм округлення ще до того, як код кандидата побачить хоча б один живий користувач.

## Розбір виробничих пасток та крайових випадків

Під час впровадження тіньового виконання в промислову експлуатацію виникають чотири специфічні пастки, які необхідно враховувати при проєктуванні:

### Пастка 1: Вичерпання черги та шторм пропусків (Drop Storm)
Якщо експериментальний кандидат містить неоптимальний алгоритм (наприклад, квадратичну складність `O(N²)` на великих масивах даних) або виконує повільний мережевий виклик до бази даних, фоновий потік перестає встигати за темпом надходження вхідних запитів.

Місткість черги `QUEUE_CAPACITY` швидко вичерпується до 512 елементів. У цей момент диспетчер починає відкидати 100% тіньових завдань.
* **Правильна реакція системи:** збільшення лічильника `dropped_count` повинно викликати операційний алерт для чергових інженерів.
* **Неприпустима дія:** збільшувати розмір черги до нескінченності. Необмежена черга призведе до вичерпання всієї доступної оперативної пам'яті процесу (OOM-killer) та аварійного падіння сервісу.

### Пастка 2: Забруднення логів під час масштабних розбіжностей
Якщо в новому коді допущено грубу алгоритмічну помилку (наприклад, переплутано знак коефіцієнта чи валютний курс), кожне з 50 000 тіньових завдань щосекунди генеруватиме повідомлення про розбіжність. Такий потік повідомлень миттєво переповнить буфери лог-колекторів (Elasticsearch/Loki), призведе до дискового голодування та унеможливить аналіз інших системних інцидентів.

Для запобігання цьому компаратор повинен використовувати алгоритм обмеження частоти (англ. *token bucket rate limiter*): логувати не більше 10 детальних звітів про розбіжності на секунду з повним дампом аргументів, а для решти — лише інкрементувати лічильник у метриках StatsD.

### Пастка 3: Прокидання контексту розподіленого трасування
Коли головний потік створює тіньове завдання, ідентифікатори розподіленого трасування (OpenTelemetry `traceparent` та `baggage`) втрачаються, якщо їх явно не скопіювати в структуру завдання `ShadowTask`. У результаті спани тіньового виконання у фоновому потоці виглядають як ізольовані кореневі трейси без прив'язки до вхідного HTTP-запиту клієнта.

Щоб зберегти наскрізну видимість, структура завдання повинна містити копію контексту трасування, а фоновий потік повинен відкривати дочірній спан (англ. *child span*) із позначкою `shadow=true`, пов'язаний із батьківським спаном клієнтського запиту.

### Пастка 4: Коректне штатне завершення роботи (Graceful Shutdown)
Під час перезапуску або розгортання нової версії сервісу процес отримує сигнал `SIGTERM`. Якщо зупинити фоновий потік миттєво, незавершені тіньові завдання будуть втрачені, а виділена для них пам'ять може призвести до помилок під час фіналізації аллокаторів.

Реалізація повинна підтримувати двофазне завершення:
1. Спочатку виставляється прапорець `is_terminating = true`, і диспетчер припиняє прийом нових тіньових завдань від клієнтських викликів.
2. Потім викликається `pthread_join` (або деструктор `std::jthread`), який дозволяє фоновому потоку вичитати залишок накопичених завдань із черги протягом заданого ліміту часу (наприклад, 500 мс), після чого звільняє м'ютекси та завершує роботу.

## Інтеграція з конвеєром CI/CD та автоматичними воротами релізу

Отримані в результаті роботи диференційного компаратора метрики служать основою для автоматизації переходів між етапами міграції в конвеєрі неперервної доставки (CI/CD). Замість суб'єктивного ручного ухвалення рішень інженери налаштовують автоматичні функції придатності (англ. *fitness functions*).

Конвеєр щогодини виконує PromQL-запит до системи моніторингу:

```text
sum(rate(scientist_mismatches_total[24h])) / sum(rate(scientist_executions_total[24h])) == 0.0
```

Якщо за останні 24 години на понад 10 мільйонах запитів частка розбіжностей дорівнює точно `0.0000%`, а 99-й перцентиль затримки кандидата (`p99`) не перевищує показників контрольної гілки, конвеєр автоматично переводить прапорець функції на наступний етап — канарковий запуск на 1% реальних користувачів. Якщо ж виявлено бодай одну невідповідність бізнес-логіки, деплой блокується, а розробники отримують сповіщення з повним дампом відхилень для виправлення дефекту.
