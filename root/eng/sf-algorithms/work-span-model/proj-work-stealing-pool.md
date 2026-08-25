# ⚙️ Реалізація пулу потоків із крадіжкою роботи (Work-Stealing)

Централізована черга задач у багатопотокових системах перетворюється на вузьке місце: коли сотні потоків одночасно намагаються отримати дрібнозернисті задачі з єдиної черги під м'ютексом, витрати на між'ядерну синхронізацію та інвалідацію кеш-ліній повністю знищують виграш від паралелізму. Алгоритм крадіжки роботи (англ. *work-stealing*) усуває цю проблему через повну децентралізацію: кожен потік володіє власною двобічною чергою (деком), працює локально за принципом стека (LIFO) і звертається до черг інших потоків лише тоді, коли вичерпав власну роботу.

---

## Архітектура та інваріанти децентралізованого шедулера

У моделі динамічного багатопотокового виконання (DAG) обчислення породжуються рекурсивно за принципом «розділяй і володарюй». Розподіл задач між потоками підпорядковується двом ключовим інваріантам:

1. **Локальні операції власника (Owner operations):**
   - Потік кладе нові задачі (породжені викликами `spawn`) на **дно** (bottom) власного дека.
   - Потік вибирає наступну задачу для виконання також із **дна** свого дека (порядок LIFO — Last-In, First-Out).
   - *Чому LIFO:* остання породжена задача оперує даними, які щойно були завантажені в локальний кеш L1/L2 процесора (максимальна часова й просторова локальність даних). Крім того, це відповідає природному порядку послідовного обходу дерева рекурсії в глибину (DFS).

2. **Операції крадіжки (Thief operations):**
   - Коли дек потоку стає порожнім, він випадковим чином обирає інший потік (жертву) і намагається вкрасти задачу з **вершини** (top) її дека (порядок FIFO — First-In, First-Out).
   - *Чому FIFO:* задачі біля вершини дека були створені найраніше — вони розташовані найближче до кореня дерева рекурсії та представляють великі піддерева обчислень (грубозернисту роботу). Одноразова крадіжка забезпечує злодія роботою на тривалий час, мінімізуючи частоту майбутніх між'ядерних звернень.

---

## Порівняння підходів: Work-Sharing проти Work-Stealing

В інженерії паралельних систем розрізняють два принципові класи динамічного планування:

| Характеристика | Розподіл роботи (Work-Sharing) | Крадіжка роботи (Work-Stealing) |
|---|---|---|
| **Ініціатор переміщення** | Завантажений потік, який створює задачу, намагається виштовхнути її іншим ядрам. | Вільний потік, у якого закінчилася робота, шукає та забирає задачі в інших. |
| **Накладні витрати при високому завантаженні** | Високі: кожна операція `spawn` спричиняє міжпотокову синхронізацію та пошук вільних ядер. | Мінімальні: власник кладе задачу в локальний стек без блокування та повідомлень. |
| **Локальність кешу** | Низька: підзадачі випадково розкидаються по різних ядрах, руйнуючи кеш L1/L2. | Максимальна: підзадачі виконуються тим самим ядром локально за принципом LIFO. |
| **Частота між'ядерних звернень** | Пропорційна загальній кількості задач у програмі (`O(T₁)`). | Пропорційна критичному шляху графа та кількості процесорів (`O(P · T_∞)`). |

---

## Реалізація на мовах C та C++

У наведеному прикладі реалізовано децентралізований пул потоків із підтримкою fork-join паралелізму на базі окремих двобічних черг для кожного робочого потоку.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <pthread.h>
#include <unistd.h>

#define DEQUE_CAPACITY 1024

typedef struct Task {
    void (*func)(void*);
    void *arg;
} Task;

typedef struct Deque {
    Task buffer[DEQUE_CAPACITY];
    int top;
    int bottom;
    pthread_mutex_t lock;
} Deque;

typedef struct ThreadPool {
    int num_threads;
    pthread_t *threads;
    Deque *deques;
    volatile bool running;
} ThreadPool;

typedef struct WorkerArgs {
    ThreadPool *pool;
    int worker_id;
} WorkerArgs;

static void deque_init(Deque *q) {
    q->top = 0;
    q->bottom = 0;
    pthread_mutex_init(&q->lock, NULL);
}

static void deque_destroy(Deque *q) {
    pthread_mutex_destroy(&q->lock);
}

static bool deque_push_bottom(Deque *q, Task task) {
    pthread_mutex_lock(&q->lock);
    if (q->bottom - q->top >= DEQUE_CAPACITY) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }
    q->buffer[q->bottom % DEQUE_CAPACITY] = task;
    q->bottom++;
    pthread_mutex_unlock(&q->lock);
    return true;
}

static bool deque_pop_bottom(Deque *q, Task *out_task) {
    pthread_mutex_lock(&q->lock);
    if (q->bottom <= q->top) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }
    q->bottom--;
    *out_task = q->buffer[q->bottom % DEQUE_CAPACITY];
    pthread_mutex_unlock(&q->lock);
    return true;
}

static bool deque_steal_top(Deque *q, Task *out_task) {
    if (pthread_mutex_trylock(&q->lock) != 0) {
        return false;
    }
    if (q->top >= q->bottom) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }
    *out_task = q->buffer[q->top % DEQUE_CAPACITY];
    q->top++;
    pthread_mutex_unlock(&q->lock);
    return true;
}

static void* worker_loop(void *arg) {
    WorkerArgs *wargs = (WorkerArgs*)arg;
    ThreadPool *pool = wargs->pool;
    int id = wargs->worker_id;
    Deque *my_q = &pool->deques[id];

    unsigned int seed = (unsigned int)(id + 100);

    while (pool->running) {
        Task task;
        if (deque_pop_bottom(my_q, &task)) {
            task.func(task.arg);
            continue;
        }

        // Крадіжка роботи у випадково обраного сусіда
        bool stolen = false;
        if (pool->num_threads > 1) {
            int victim = rand_r(&seed) % pool->num_threads;
            if (victim != id) {
                if (deque_steal_top(&pool->deques[victim], &task)) {
                    task.func(task.arg);
                    stolen = true;
                }
            }
        }

        if (!stolen) {
            usleep(50); // Коротке очікування появи задач
        }
    }
    return NULL;
}

ThreadPool* pool_create(int num_threads) {
    ThreadPool *pool = (ThreadPool*)malloc(sizeof(ThreadPool));
    pool->num_threads = num_threads;
    pool->running = true;
    pool->threads = (pthread_t*)malloc(sizeof(pthread_t) * num_threads);
    pool->deques = (Deque*)malloc(sizeof(Deque) * num_threads);

    for (int i = 0; i < num_threads; ++i) {
        deque_init(&pool->deques[i]);
    }

    for (int i = 0; i < num_threads; ++i) {
        WorkerArgs *args = (WorkerArgs*)malloc(sizeof(WorkerArgs));
        args->pool = pool;
        args->worker_id = i;
        pthread_create(&pool->threads[i], NULL, worker_loop, args);
    }
    return pool;
}

void pool_destroy(ThreadPool *pool) {
    pool->running = false;
    for (int i = 0; i < pool->num_threads; ++i) {
        pthread_join(pool->threads[i], NULL);
        deque_destroy(&pool->deques[i]);
    }
    free(pool->threads);
    free(pool->deques);
    free(pool);
}
```
```cpp
#include <iostream>
#include <vector>
#include <deque>
#include <thread>
#include <atomic>
#include <mutex>
#include <functional>
#include <random>
#include <memory>
#include <optional>
#include <span>

class WorkStealingPool {
public:
    using Task = std::function<void()>;

    explicit WorkStealingPool(size_t num_threads = std::thread::hardware_concurrency())
        : running_(true), num_threads_(std::max<size_t>(1, num_threads)), deques_(num_threads_) {
        workers_.reserve(num_threads_);
        for (size_t i = 0; i < num_threads_; ++i) {
            workers_.emplace_back([this, i] { worker_loop(i); });
        }
    }

    ~WorkStealingPool() {
        running_.store(false, std::memory_order_release);
        for (auto &worker : workers_) {
            if (worker.joinable()) {
                worker.join();
            }
        }
    }

    void submit(Task task, size_t target_worker = 0) {
        size_t idx = target_worker % num_threads_;
        deques_[idx].push_bottom(std::move(task));
    }

    size_t worker_count() const noexcept {
        return num_threads_;
    }

private:
    struct alignas(64) ThreadDeque {
        std::deque<Task> tasks;
        mutable std::mutex lock;

        void push_bottom(Task task) {
            std::lock_guard<std::mutex> guard(lock);
            tasks.push_back(std::move(task));
        }

        std::optional<Task> pop_bottom() {
            std::lock_guard<std::mutex> guard(lock);
            if (tasks.empty()) {
                return std::nullopt;
            }
            Task t = std::move(tasks.back());
            tasks.pop_back();
            return t;
        }

        std::optional<Task> steal_top() {
            std::unique_lock<std::mutex> guard(lock, std::try_to_lock);
            if (!guard.owns_lock() || tasks.empty()) {
                return std::nullopt;
            }
            Task t = std::move(tasks.front());
            tasks.pop_front();
            return t;
        }
    };

    void worker_loop(size_t worker_id) {
        thread_local std::mt19937 rng(static_cast<uint32_t>(worker_id + 42));
        std::uniform_int_distribution<size_t> dist(0, num_threads_ - 1);

        while (running_.load(std::memory_order_acquire)) {
            if (auto task = deques_[worker_id].pop_bottom()) {
                (*task)();
                continue;
            }

            bool stolen = false;
            if (num_threads_ > 1) {
                size_t victim = dist(rng);
                if (victim != worker_id) {
                    if (auto task = deques_[victim].steal_top()) {
                        (*task)();
                        stolen = true;
                    }
                }
            }

            if (!stolen) {
                std::this_thread::yield();
            }
        }
    }

    std::atomic<bool> running_;
    size_t num_threads_;
    std::vector<ThreadDeque> deques_;
    std::vector<std::thread> workers_;
};
```
:::

---

## Приклад: Паралельне обчислення суми масиву (Fork-Join Reduction)

Покажемо, як децентралізований шедулер виконує рекурсивне обчислення суми масиву з логарифмічною глибиною `T_∞ = O(log N)`.

:::tabs
```c
typedef struct SumArgs {
    const int *arr;
    size_t start;
    size_t end;
    long long *result;
    pthread_mutex_t *sync_lock;
    int *pending_count;
} SumArgs;

void parallel_sum_task(void *raw_args);

void parallel_sum_task(void *raw_args) {
    SumArgs *args = (SumArgs*)raw_args;
    size_t len = args->end - args->start;

    // Базовий випадок (послідовне підсумовування при малому розмірі)
    if (len <= 1000) {
        long long local_sum = 0;
        for (size_t i = args->start; i < args->end; ++i) {
            local_sum += args->arr[i];
        }
        pthread_mutex_lock(args->sync_lock);
        *args->result += local_sum;
        (*args->pending_count)--;
        pthread_mutex_unlock(args->sync_lock);
        free(args);
        return;
    }

    size_t mid = args->start + len / 2;
    SumArgs *left_args = (SumArgs*)malloc(sizeof(SumArgs));
    left_args->arr = args->arr;
    left_args->start = args->start;
    left_args->end = mid;
    left_args->result = args->result;
    left_args->sync_lock = args->sync_lock;
    left_args->pending_count = args->pending_count;

    SumArgs *right_args = (SumArgs*)malloc(sizeof(SumArgs));
    right_args->arr = args->arr;
    right_args->start = mid;
    right_args->end = args->end;
    right_args->result = args->result;
    right_args->sync_lock = args->sync_lock;
    right_args->pending_count = args->pending_count;

    pthread_mutex_lock(args->sync_lock);
    (*args->pending_count) += 2;
    (*args->pending_count)--; // поточна задача завершена
    pthread_mutex_unlock(args->sync_lock);

    parallel_sum_task(left_args);
    parallel_sum_task(right_args);

    free(args);
}
```
```cpp
#include <numeric>
#include <future>

long long parallel_reduce(std::span<const int> data, WorkStealingPool &pool) {
    constexpr size_t threshold = 1000;
    if (data.size() <= threshold) {
        return std::accumulate(data.begin(), data.end(), 0LL);
    }

    size_t mid = data.size() / 2;
    auto left_span = data.subspan(0, mid);
    auto right_span = data.subspan(mid);

    std::promise<long long> right_promise;
    auto right_future = right_promise.get_future();

    // Відправляємо праву частину в пул (spawn)
    pool.submit([right_span, &right_promise, &pool]() {
        right_promise.set_value(parallel_reduce(right_span, pool));
    });

    // Ліва частина виконується поточним потоком безпосередньо
    long long left_sum = parallel_reduce(left_span, pool);

    // Очікування результату правої гілки (sync)
    long long right_sum = right_future.get();

    return left_sum + right_sum;
}
```
:::

---

## Низькорівнева оптимізація та апаратні інваріанти

Під час розробки високопродуктивних планувальників із крадіжкою роботи необхідно враховувати специфіку апаратного когерентного кешу процесора:

1. **Хибне розділення кеш-ліній (False Sharing):**
   - Якщо структури `Deque` різних потоків розміщені в пам'яті щільно одна за одною, покажчики `bottom` і `top` сусідніх потоків потрапляють в одну 64-байтну лінію кешу L1/L2. Кожна зміна локального дека призводить до між'ядерних широкомовних повідомлень протоколу когерентності (MESI/MOESI invalidation storm).
   - *Виправлення:* вирівнювання структури черги кожного потоку за розміром кеш-лінії через `alignas(64)` або додавання неробочих байтів заповнення (padding).

2. **Гранулярність задач та поріг відсікання (Cutoff Threshold):**
   - Якщо розбивати масив аж до одиничних елементів (`len == 1`), накладні витрати на виділення пам'яті під об'єкт задачі, створення замикань та перемикання контексту перевищать корисну роботу в сотні разів.
   - *Виправлення:* зупиняти рекурсивний поділ на порозі, де послідовний час виконання базового блоку становить 10–50 мікросекунд (зазвичай `1000`–`5000` операцій).

3. **Безблокові черги Чейза — Лева (Chase-Lev Lock-Free Deque):**
   - У продакшн-рантаймах (Cilk, Intel TBB, Go Runtime) блокування м'ютексами замінюють на безблокову чергу Чейза — Лева. Власник дека змінює `bottom` за допомогою звичайних атомарних інструкцій `atomic_store_explicit` з упорядкуванням пам'яті `memory_order_release`, не використовуючи важких інструкцій із блокуванням шини (`LOCK CMPXCHG`). Дорогі операції CAS застосовуються лише злодіями або у крайовому випадку, коли в деку залишається рівно один елемент і виникає конкуренція між власником та злодієм.

4. **Ієрархічна крадіжка з урахуванням топології NUMA:**
   - На багатосокетних серверах звернення до пам'яті іншого сокета через міжпроцесорну шину (Intel UPI або AMD Infinity Fabric) займає у 2.5–3 рази більше часу, ніж локальне звернення.
   - *Виправлення:* дворівнева стратегія вибору жертви. Потік спочатку намагається вкрасти задачу в ядра, що розділяють спільний кеш L3 на тому ж сокеті (локальна крадіжка), і лише після кількох невдалих спроб звертається до черг віддалених сокетів.

5. **Стратегія відступу під час простою (Idle Backoff):**
   - Коли всі черги системи порожні, безперервні спроби крадіжки (активний спінінг) навантажують шину пам'яті та споживають зайву електроенергію.
   - *Виправлення:* застосування експоненційного відступу (Exponential Backoff): після кількох невдалих спроб потік виконує паузу `_mm_pause()`, потім передає квант часу через `sched_yield()` / `std::this_thread::yield()`, і врешті засинає на умовній змінній до появи нових задач від зовнішніх джерел.

6. **Бар'єри пам'яті та модель упорядкування (Memory Order):**
   - У безблокових реалізаціях операція запису нової задачі на дно дека обов'язково супроводжується бар'єром випуску (`memory_order_release`), що гарантує повну видимість записаних аргументів задачі в пам'яті до того, як покажчик `bottom` стане доступним для читання іншими ядрами.
   - Злодій, який читає вершину дека через `memory_order_acquire`, отримує узгоджений зріз пам'яті, що запобігає читанню частково ініціалізованих або застарілих дескрипторів задач.
