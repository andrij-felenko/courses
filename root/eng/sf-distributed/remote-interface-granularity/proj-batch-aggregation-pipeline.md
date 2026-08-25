# ⚙️ Реалізація клієнтського мікробатчера та обгортки віддаленого фасаду

Коли окремі потоки клієнтського застосунку генерують безліч дрібних запитів до віддаленого сервісу (наприклад, перевірка цін товарів або завантаження профілів користувачів), пряме виконання кожного виклику через окремий сокет спричиняє вичерпання пулу з'єднань, блокування потоків та лавину мережевих кругових рейсів (RTT).

Для оптимізації застосовують **клієнтський мікробатчер (*Request Batcher / Coalescer*)**. Він надає потокам звичайний дрібнозернистий інтерфейс, але всередині накопичує запити в потокобезпечній черзі та скидає їх єдиним грубозернистим пакетом до віддаленого фасаду за двома взаємодоповнюючими критеріями:
1. **Критерій заповнення буфера:** кількість накопичених запитів досягла ліміту `MAX_BATCH_SIZE` (наприклад, 32 елементи);
2. **Критерій затримки (Time Window):** сплив максимальний час очікування `FLUSH_TIMEOUT_MS` (наприклад, 10 мс) з моменту надходження першого запиту в чергу.

Нижче наведено робочі реалізації конвеєра на C та C++.

---

### Архітектура конвеєра пакетування та синхронізація

Конвеєр складається з трьох ключових компонентів, що взаємодіють між собою:
* **Черга очікування (Pending Queue) з м'ютексом:** захищає буфер від одночасного запису кількома клієнтськими потоками і сигналізує фоновому потоку про появу нових даних через умовну змінну (*condition variable*).
* **Фоновий потік скидання (Worker Thread):** здійснює блокуюче очікування з таймаутом, вилучає сформований пакет за допомогою швидкого переміщення вказівників чи `std::move`, викликає віддалений фасад та демультиплексує результат.
* **Механізм асинхронного сповіщення:** передає результат обробки назад викликаючому потоку через `std::promise` / `std::future` у C++ або через індивідуальні умовні змінні в C.

---

### Реалізація конвеєра

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <stdbool.h>
#include <unistd.h>
#include <time.h>

#define MAX_BATCH_SIZE 8
#define FLUSH_TIMEOUT_MS 20

typedef struct {
    int item_id;
    int price_cents;
    int status_code; // 200 = OK, 404 = Not Found
} ItemResult;

typedef struct {
    int item_id;
    ItemResult result;
    bool completed;
    pthread_cond_t done_cond;
    pthread_mutex_t done_mutex;
} PendingRequest;

typedef struct {
    PendingRequest* queue[MAX_BATCH_SIZE];
    size_t count;
    pthread_mutex_t mutex;
    pthread_cond_t cond;
    bool running;
    pthread_t worker;
} RequestBatcher;

/* Імітація віддаленого фасаду: один мережевий рейс обробляє масив ID */
static void remote_facade_get_prices(const int* ids, size_t count, ItemResult* out_results) {
    /* Імітація затримки мережі (RTT = 15 мс) */
    struct timespec ts = {0, 15 * 1000000};
    nanosleep(&ts, NULL);

    for (size_t i = 0; i < count; ++i) {
        out_results[i].item_id = ids[i];
        if (ids[i] <= 0) {
            out_results[i].status_code = 404;
            out_results[i].price_cents = 0;
        } else {
            out_results[i].status_code = 200;
            out_results[i].price_cents = ids[i] * 100 + 99; // Умовна ціна
        }
    }
}

static void* batcher_worker(void* arg) {
    RequestBatcher* batcher = (RequestBatcher*)arg;

    while (true) {
        PendingRequest* local_batch[MAX_BATCH_SIZE];
        size_t batch_size = 0;

        pthread_mutex_lock(&batcher->mutex);
        while (batcher->running && batcher->count == 0) {
            pthread_cond_wait(&batcher->cond, &batcher->mutex);
        }

        if (!batcher->running && batcher->count == 0) {
            pthread_mutex_unlock(&batcher->mutex);
            break;
        }

        /* Очікуємо наповнення або таймауту */
        struct timespec deadline;
        clock_gettime(CLOCK_REALTIME, &deadline);
        deadline.tv_nsec += FLUSH_TIMEOUT_MS * 1000000;
        if (deadline.tv_nsec >= 1000000000) {
            deadline.tv_sec += 1;
            deadline.tv_nsec -= 1000000000;
        }

        while (batcher->count < MAX_BATCH_SIZE) {
            int res = pthread_cond_timedwait(&batcher->cond, &batcher->mutex, &deadline);
            if (res != 0) {
                break; // Сплив таймаут скидання
            }
        }

        /* Забираємо накопичені запити */
        batch_size = batcher->count;
        for (size_t i = 0; i < batch_size; ++i) {
            local_batch[i] = batcher->queue[i];
        }
        batcher->count = 0;
        pthread_mutex_unlock(&batcher->mutex);

        if (batch_size == 0) {
            continue;
        }

        /* Формуємо масив ID для віддаленого фасаду */
        int ids[MAX_BATCH_SIZE];
        ItemResult results[MAX_BATCH_SIZE];
        for (size_t i = 0; i < batch_size; ++i) {
            ids[i] = local_batch[i]->item_id;
        }

        /* Виконуємо 1 грубозернистий мережевий виклик */
        remote_facade_get_prices(ids, batch_size, results);

        /* Демультиплексуємо відповіді та сповіщаємо потоки */
        for (size_t i = 0; i < batch_size; ++i) {
            PendingRequest* req = local_batch[i];
            pthread_mutex_lock(&req->done_mutex);
            req->result = results[i];
            req->completed = true;
            pthread_cond_signal(&req->done_cond);
            pthread_mutex_unlock(&req->done_mutex);
        }
    }
    return NULL;
}

void batcher_init(RequestBatcher* batcher) {
    batcher->count = 0;
    batcher->running = true;
    pthread_mutex_init(&batcher->mutex, NULL);
    pthread_cond_init(&batcher->cond, NULL);
    pthread_create(&batcher->worker, NULL, batcher_worker, batcher);
}

void batcher_destroy(RequestBatcher* batcher) {
    pthread_mutex_lock(&batcher->mutex);
    batcher->running = false;
    pthread_cond_broadcast(&batcher->cond);
    pthread_mutex_unlock(&batcher->mutex);

    pthread_join(batcher->worker, NULL);
    pthread_mutex_destroy(&batcher->mutex);
    pthread_cond_destroy(&batcher->cond);
}

/* Дрібнозернистий клієнтський метод: блокує лише свій потік до отримання результату */
ItemResult batcher_get_price(RequestBatcher* batcher, int item_id) {
    PendingRequest req;
    req.item_id = item_id;
    req.completed = false;
    pthread_mutex_init(&req.done_mutex, NULL);
    pthread_cond_init(&req.done_cond, NULL);

    pthread_mutex_lock(&batcher->mutex);
    while (batcher->count >= MAX_BATCH_SIZE) {
        /* Якщо буфер переповнений, чекаємо або форсуємо скидання */
        pthread_cond_signal(&batcher->cond);
        pthread_mutex_unlock(&batcher->mutex);
        usleep(1000);
        pthread_mutex_lock(&batcher->mutex);
    }
    batcher->queue[batcher->count++] = &req;
    pthread_cond_signal(&batcher->cond);
    pthread_mutex_unlock(&batcher->mutex);

    /* Очікуємо готовності свого результату */
    pthread_mutex_lock(&req.done_mutex);
    while (!req.completed) {
        pthread_cond_wait(&req.done_cond, &req.done_mutex);
    }
    pthread_mutex_unlock(&req.done_mutex);

    ItemResult res = req.result;
    pthread_mutex_destroy(&req.done_mutex);
    pthread_cond_destroy(&req.done_cond);
    return res;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <span>
#include <chrono>
#include <thread>
#include <future>
#include <mutex>
#include <condition_variable>
#include <expected>
#include <atomic>

struct ItemResult {
    int item_id{0};
    int price_cents{0};
};

enum class BatchError {
    NotFound,
    Timeout,
    NetworkFailure
};

struct PendingRequest {
    int item_id;
    std::promise<std::expected<ItemResult, BatchError>> promise;
};

class RemoteFacadeClient {
public:
    // Імітація одного мережевого RPC виклику до сервера
    static std::vector<std::expected<ItemResult, BatchError>>
    fetch_batch_prices(std::span<const int> item_ids) {
        // Мережевий RTT = 15 мс
        std::this_thread::sleep_for(std::chrono::milliseconds(15));

        std::vector<std::expected<ItemResult, BatchError>> results;
        results.reserve(item_ids.size());

        for (int id : item_ids) {
            if (id <= 0) {
                results.push_back(std::unexpected(BatchError::NotFound));
            } else {
                results.push_back(ItemResult{id, id * 100 + 99});
            }
        }
        return results;
    }
};

class MicroBatcher {
public:
    explicit MicroBatcher(size_t max_batch_size = 32,
                          std::chrono::milliseconds flush_timeout = std::chrono::milliseconds(10))
        : max_batch_size_(max_batch_size),
          flush_timeout_(flush_timeout),
          running_(true),
          worker_(&MicroBatcher::worker_loop, this) {}

    ~MicroBatcher() {
        {
            std::unique_lock<std::mutex> lock(mutex_);
            running_ = false;
        }
        cv_.notify_all();
        if (worker_.joinable()) {
            worker_.join();
        }
    }

    // Дрібнозернистий клієнтський інтерфейс: повертає std::future для одного товару
    std::future<std::expected<ItemResult, BatchError>> get_item_price(int item_id) {
        std::promise<std::expected<ItemResult, BatchError>> prom;
        auto fut = prom.get_future();

        {
            std::unique_lock<std::mutex> lock(mutex_);
            queue_.push_back(PendingRequest{item_id, std::move(prom)});
        }
        cv_.notify_one();
        return fut;
    }

private:
    void worker_loop() {
        while (true) {
            std::vector<PendingRequest> current_batch;

            {
                std::unique_lock<std::mutex> lock(mutex_);
                cv_.wait(lock, [this] {
                    return !running_ || !queue_.empty();
                });

                if (!running_ && queue_.empty()) {
                    break;
                }

                // Очікуємо наповнення буфера або таймауту
                cv_.wait_for(lock, flush_timeout_, [this] {
                    return queue_.size() >= max_batch_size_ || !running_;
                });

                if (queue_.empty()) {
                    continue;
                }

                size_t count = std::min(queue_.size(), max_batch_size_);
                current_batch.insert(current_batch.end(),
                                     std::make_move_iterator(queue_.begin()),
                                     std::make_move_iterator(queue_.begin() + count));
                queue_.erase(queue_.begin(), queue_.begin() + count);
            }

            if (current_batch.empty()) {
                continue;
            }

            // Формуємо список ідентифікаторів
            std::vector<int> ids;
            ids.reserve(current_batch.size());
            for (const auto& req : current_batch) {
                ids.push_back(req.item_id);
            }

            // 1 грубозернистий виклик через мережу
            auto results = RemoteFacadeClient::fetch_batch_prices(ids);

            // Демультиплексування та сповіщення конкретних потоків
            for (size_t i = 0; i < current_batch.size(); ++i) {
                current_batch[i].promise.set_value(results[i]);
            }
        }
    }

    size_t max_batch_size_;
    std::chrono::milliseconds flush_timeout_;
    std::vector<PendingRequest> queue_;
    std::mutex mutex_;
    std::condition_variable cv_;
    std::atomic<bool> running_;
    std::thread worker_;
};
```
:::

---

### Детальний аналіз інженерних рішень та обробки крайових випадків

#### 1. Балансування затримки та пропускної здатності (Latency vs Throughput Trade-off)
Клієнтський батчер додає штучну фіксовану затримку `flush_timeout_` (10–20 мс) для першого запиту в порожній черзі. Якщо потік запитів низький, окремий користувач сплачує цю затримку. Проте при зростанні навантаження (коли сотні потоків генерують паралельні виклики) черга досягає `max_batch_size_` за частки мілісекунди. Затримка очікування скидання падає майже до нуля, а сумарна пропускна здатність системи зростає у десятки разів, оскільки мережевий контролер та серверний фасад обробляють запити великими масивами.

#### 2. Модель пам'яті та усунення блокувань (Lock Contention & Memory Visibility)
Зверніть увагу на час утримання блокування: м'ютекс `mutex_` захоплюється виключно під час додавання елемента в чергу або переміщення буфера (`queue_.erase()`), що займає менше 50 наносекунд процесорного часу.

Сам мережевий виклик `fetch_batch_prices()` виконується **суворо поза критичною секцією** (`outside the lock`). Завдяки цьому, поки фоновий потік очікує на відповідь сокета протягом 15 мс RTT, клієнтські потоки можуть вільно наповнювати наступний пакет. Це повністю усуває блокування черги та запобігає явищу «стрибання кеш-ліній» (*cache line bouncing*) між ядрами процесора.

#### 3. Запобігання витокам пам'яті та коректне завершення роботи
У деструкторі `MicroBatcher` встановлюється прапорець `running_ = false`, після чого викликається `cv_.notify_all()`. Фоновий потік коректно завершує поточну ітерацію, обробляє залишок черги та завершує роботу через `worker_.join()`. У реалізації на C застосовується функція `batcher_destroy`, яка виконує аналогічний `broadcast` і чекає на `pthread_join`.

#### 4. Ізоляція збоїв за допомогою `std::expected`
У C++ реалізації використання типу `std::expected<ItemResult, BatchError>` гарантує, що помилка віддаленого сервера для одного конкретного `item_id` (наприклад, товар не знайдено або видалено) не призводить до аварійного винятку в інших паралельних потоках. Кожен викликаючий потік отримує свій власний статус і може самостійно вирішити: повторити запит, повернути помилку клієнту чи використати значення за замовчуванням.

#### 5. Механіка поширення помилок обриву мережі (Transport Error Propagation)
Якщо під час виклику `RemoteFacadeClient::fetch_batch_prices` стається критичний мережевий збій (таймаут сокета, знеструмлення сервера або скидання TCP RST), функція віддаленого клієнта не повинна кидати необроблений виняток. У такому сценарії клієнтський обробник повертає масив, де для кожного елемента встановлено `std::unexpected(BatchError::NetworkFailure)`. Завдяки цьому жоден клієнтський потік не зависає назавжди в очікуванні `std::future::get()`, а отримує явний статус збою і може перейти до механізму повтору (`root:sf-distributed/retries-backoff`).

#### 6. Обробка переповнення черги та зворотний тиск (Backpressure)
Якщо клієнтські потоки генерують запити швидше, ніж серверний фасад здатний їх обробляти, черга не повинна зростати нескінченно, поглинаючи оперативну пам'ять. У реалізації на C передбачено жорстке обмеження `MAX_BATCH_SIZE`: при переповненні буфера клієнтські потоки переходять у режим зворотного тиску (*backpressure*), примусово сповільнюючись через `usleep` та форсуючи скидання поточного пакета. У виробничих системах C++ чергу обмежують максимальним розміром `MAX_QUEUE_CAPACITY` (наприклад, 1024 елементи), повертаючи негайну помилку `BatchError::QueueOverflow`, якщо серверний фасад перевантажений.

#### 7. Профілювання та межі застосування клієнтського батчера
Клієнтський мікробатчер ідеально підходить для ідемпотентних операцій читання (вибірка метаданих, цін, наявності товарів) або масових асинхронних операцій запису (телеметрія, події аналітики). Його не слід застосовувати для критичних інтерактивних операцій, де клієнт вимагає субмілісекундного відгуку і не може дозволити собі очікування таймера `flush_timeout_`. На практиці цей підхід зменшує споживання дескрипторів сокетів у `MAX_BATCH_SIZE` разів та знижує навантаження на мережевий стек ядра ОС майже на 90%.
