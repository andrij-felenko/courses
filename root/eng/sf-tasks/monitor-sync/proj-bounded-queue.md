# ⚙️ Реалізація виробничої обмеженої блокувальної черги з таймаутами та завершенням

Шаблон виробника і споживача лежить в основі більшості високонавантажених сервісів, систем обробки потокового відео, черг завдань пулу потоків та мережевих конвеєрів. Якщо швидкість надходження завдань перевищує швидкість їх обробки, необмежена черга призводить до неконтрольованого зростання споживання оперативної пам'яті й аварійного падіння процесу через нестачу пам'яті (Out-Of-Memory).

Вирішенням є **обмежена блокувальна черга** (англ. *Bounded Blocking Queue*), яка встановлює жорсткий ліміт місткості, призупиняючи виробників при заповненні та споживачів при спустошенні буфера.

Нижче наведено повні виробничі реалізації обмеженої черги мовами C (на базі POSIX Threads) та C++ (на базі стандартних примітивів `<mutex>` і `<condition_variable>`), які підтримують коректне завершення роботи (*graceful shutdown*), неблокуючі спроби вставки та операції очікування за тайм-аутом.

## Реалізація мовами C та C++

:::tabs
```c
#include <pthread.h>
#include <stdbool.h>
#include <stdlib.h>
#include <time.h>
#include <errno.h>

typedef struct {
    void** buffer;
    size_t capacity;
    size_t head;
    size_t tail;
    size_t count;
    bool shutdown;

    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} bounded_queue_t;

bounded_queue_t* bqueue_create(size_t capacity) {
    if (capacity == 0) return NULL;

    bounded_queue_t* q = (bounded_queue_t*)malloc(sizeof(bounded_queue_t));
    if (!q) return NULL;

    q->buffer = (void**)malloc(sizeof(void*) * capacity);
    if (!q->buffer) {
        free(q);
        return NULL;
    }

    q->capacity = capacity;
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->shutdown = false;

    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    pthread_cond_init(&q->not_full, NULL);

    return q;
}

bool bqueue_push(bounded_queue_t* q, void* item) {
    pthread_mutex_lock(&q->lock);

    while (q->count == q->capacity && !q->shutdown) {
        pthread_cond_wait(&q->not_full, &q->lock);
    }

    if (q->shutdown) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }

    q->buffer[q->tail] = item;
    q->tail = (q->tail + 1) % q->capacity;
    q->count++;

    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
    return true;
}

bool bqueue_pop(bounded_queue_t* q, void** item) {
    pthread_mutex_lock(&q->lock);

    while (q->count == 0 && !q->shutdown) {
        pthread_cond_wait(&q->not_empty, &q->lock);
    }

    if (q->count == 0 && q->shutdown) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }

    *item = q->buffer[q->head];
    q->head = (q->head + 1) % q->capacity;
    q->count--;

    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->lock);
    return true;
}

bool bqueue_pop_timeout(bounded_queue_t* q, void** item, long timeout_ms) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_sec += timeout_ms / 1000;
    ts.tv_nsec += (timeout_ms % 1000) * 1000000;
    if (ts.tv_nsec >= 1000000000) {
        ts.tv_sec += 1;
        ts.tv_nsec -= 1000000000;
    }

    pthread_mutex_lock(&q->lock);

    while (q->count == 0 && !q->shutdown) {
        int rc = pthread_cond_timedwait(&q->not_empty, &q->lock, &ts);
        if (rc == ETIMEDOUT) {
            break;
        }
    }

    if (q->count == 0) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }

    *item = q->buffer[q->head];
    q->head = (q->head + 1) % q->capacity;
    q->count--;

    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->lock);
    return true;
}

void bqueue_shutdown(bounded_queue_t* q) {
    pthread_mutex_lock(&q->lock);
    q->shutdown = true;
    pthread_cond_broadcast(&q->not_empty);
    pthread_cond_broadcast(&q->not_full);
    pthread_mutex_unlock(&q->lock);
}

void bqueue_destroy(bounded_queue_t* q) {
    if (!q) return;

    bqueue_shutdown(q);

    pthread_mutex_destroy(&q->lock);
    pthread_cond_destroy(&q->not_empty);
    pthread_cond_destroy(&q->not_full);

    free(q->buffer);
    free(q);
}
```
```cpp
#include <mutex>
#include <condition_variable>
#include <vector>
#include <optional>
#include <chrono>
#include <stdexcept>
#include <utility>

template <typename T>
class BoundedQueue {
public:
    explicit BoundedQueue(size_t capacity)
        : capacity_(capacity), head_(0), tail_(0), count_(0), shutdown_(false) {
        if (capacity == 0) {
            throw std::invalid_argument("Capacity must be greater than zero");
        }
        buffer_.resize(capacity);
    }

    ~BoundedQueue() {
        shutdown();
    }

    BoundedQueue(const BoundedQueue&) = delete;
    BoundedQueue& operator=(const BoundedQueue&) = delete;

    bool push(T item) {
        std::unique_lock<std::mutex> lock(mutex_);
        not_full_.wait(lock, [this] {
            return count_ < capacity_ || shutdown_;
        });

        if (shutdown_) {
            return false;
        }

        buffer_[tail_] = std::move(item);
        tail_ = (tail_ + 1) % capacity_;
        ++count_;

        not_empty_.notify_one();
        return true;
    }

    std::optional<T> pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        not_empty_.wait(lock, [this] {
            return count_ > 0 || shutdown_;
        });

        if (count_ == 0 && shutdown_) {
            return std::nullopt;
        }

        T item = std::move(buffer_[head_]);
        head_ = (head_ + 1) % capacity_;
        --count_;

        not_full_.notify_one();
        return item;
    }

    template <typename Rep, typename Period>
    std::optional<T> pop_for(const std::chrono::duration<Rep, Period>& timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        bool acquired = not_empty_.wait_for(lock, timeout, [this] {
            return count_ > 0 || shutdown_;
        });

        if (!acquired || (count_ == 0 && shutdown_)) {
            return std::nullopt;
        }

        T item = std::move(buffer_[head_]);
        head_ = (head_ + 1) % capacity_;
        --count_;

        not_full_.notify_one();
        return item;
    }

    void shutdown() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (shutdown_) return;
            shutdown_ = true;
        }
        not_empty_.notify_all();
        not_full_.notify_all();
    }

    [[nodiscard]] size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return count_;
    }

    [[nodiscard]] bool empty() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return count_ == 0;
    }

private:
    const size_t capacity_;
    std::vector<T> buffer_;
    size_t head_;
    size_t tail_;
    size_t count_;
    bool shutdown_;

    mutable std::mutex mutex_;
    std::condition_variable not_empty_;
    std::condition_variable not_full_;
};
```
:::

## Інженерний аналіз ключових архітектурних рішень

### 1. Кільцевий буфер проти зв'язного списку
Використання суцільного масиву або вектора з кільцевою індексацією (`head` і `tail` по модулю `capacity`) має фундаментальні переваги перед зв'язними списками:
- **Нульове динамічне виділення пам'яті**: на гарячому шляху `push` та `pop` не викликаються функції `malloc`, `free`, `new` або `delete`. Усі структури виділяються одноразово під час ініціалізації монітора.
- **Просторова локальність кешу**: елементи розташовані послідовно в пам'яті, що забезпечує максимальну ефективність апаратного передзавантажувача процесора (*hardware prefetcher*) та мінімізує кількість промахів у кеш L1/L2.

### 2. Подвійна умовна змінна (not_empty та not_full)
Розділення очікування споживачів (`not_empty`) та виробників (`not_full`) на дві окремі умовні змінні є обов'язковим для усунення зайвої міжпотокової конкуренції:
- Коли виробник додає елемент, він будить **лише одного споживача** через `notify_one()` / `pthread_cond_signal(&not_empty)`.
- Інші виробники, заблоковані через брак місця, залишаються у стані спокою.
- Якби використовувалася одна спільна умовна змінна, довелося б викликати `broadcast()`, що спричиняло б шторм пробуджень (*thundering herd*) і неконтрольоване змагання за м'ютекс між десятками потоків.

### 3. Протокол безпечного завершення (Graceful Shutdown)
Завершення роботи черги — один із найскладніших крайових випадків у багатопотоковому програмуванні:
- Якщо просто знищити м'ютекс або звільнити пам'ять буфера, доки потоки сплять у `wait()`, виникає звернення до недійсної пам'яті (*use-after-free*) або системний збій ядра.
- У наведеній архітектурі метод `shutdown()` спочатку виставляє атомарний прапорець `shutdown_ = true` під захистом м'ютексу, а потім викликає `broadcast()` / `notify_all()` для **обох** умовних змінних.
- Розбуджені потоки виходять із циклів очікування: виробники негайно припиняють додавати нові завдання і повертають `false`, а споживачі продовжують забирати залишки даних із буфера (`count > 0`), доки черга повністю не спорожніє. Після спустошення споживачі безпечно отримують `std::nullopt` або `false` і завершують свої робочі цикли.

### 4. Неблокуючі операції (try_push та try_pop)
У графічних інтерфейсах користувача, обробниках мережевих переривань або задачах реального часу блокування потоку на невизначений час неприпустиме.
- Для таких сценаріїв інтерфейс розширюють методами `try_push()` та `try_pop()`.
- Вони використовують спробу взяття замка (`pthread_mutex_trylock` або `std::unique_lock` із параметром `std::try_to_lock`): якщо замок зайнятий або черга заповнена/порожня, метод негайно повертає керування з ознакою невдачі, не переходячи в режим сну.

### 5. Очищення залишків даних та запобігання витокам пам'яті
Якщо черга зберігає покажчики на динамічно виділені ресурси (як у версії для мови C з покажчиками `void*`), під час аварійного або примусового завершення роботи програми елементи, що залишилися в буфері, можуть бути втрачені.
- У промислових C-бібліотеках функція `bqueue_destroy` приймає необов'язковий покажчик на функцію вилучення елементів `void (*cleanup)(void*)`. Це гарантує виклик деструктора або `free()` для кожного залишкового вузла.
- У версії на C++ деструктори всіх невилучених об'єктів викликаються автоматично завдяки використанню `std::vector<T>` та механізму RAII під час знищення внутрішнього вектора.

### 6. Оптимізація вирівнювання кеш-ліній та запобігання фальшивому розділенню
У багатопроцесорних серверах із високою інтенсивністю звернень спільне розміщення змінних у межах одного 64-байтного рядка кешу процесора може спричиняти явище **фальшивого розділення** (*false sharing*).
- Змінні виробника (`tail`, `not_full`) та змінні споживача (`head`, `not_empty`) доцільно розміщувати у різних кеш-лініях за допомогою специфікатора `alignas(64)`.
- Це запобігає постійній інвалідації L1-кешу між процесорними ядрами під час паралельної роботи незалежних потоків.

### 7. Метрики продуктивності та профілювання черг
Під час навантажувального тестування черги в архітектурі MPMC (багато виробників, багато споживачів) ключовими показниками є:
- **Пропускна здатність** (*throughput*): кількість переданих елементів за секунду.
- **Хвостова затримка** (*tail latency P99/P99.9*): час очікування найбільш затриманих елементів, що виникає через нерівномірність планувальника або сплески конкуренції за м'ютекс.

### 8. Пакетна обробка (Batching) та межі застосування
Для максимального масштабування у навантажених системах застосовують патерн **пакетної передачі** (*batching*), коли виробник захоплює м'ютекс один раз для вставки пачки з `K` елементів, після чого надсилає `notify_all()` або кілька `notify_one()`. Це амортизує накладні витрати на захоплення замка.

Якщо ж затримка синхронізації критично важлива (наносекундний діапазон у високочастотному трейдингу HFT або ядрі аудіообробки реального часу), замість моніторів застосовують неблокуючі кільцеві буфери (*lock-free ring buffers*) на базі атомарних інструкцій без системних викликів ядра.
