# ⚙️ Реалізація паралельного конвеєра обробки з протитиском і пулом воркерів

Конвеєрна архітектура в багатопотокових і розподілених сервісах вимагає надійної синхронізації між стадіями обробки. Головний виклик — забезпечити **активний протитиск** (англ. *backpressure*): швидкий постачальник даних не повинен переповнювати пам'ять, якщо проміжний фільтр працює повільніше.

Нижче наведено повноцінну реалізацію багатостадійного конвеєра телеметрії кібербезпеки:
* **Стадія 1 (Ingest/Parser):** розбирає сирі бінарні пакети подій, витягує ідентифікатор сесії та корисне навантаження.
* **Стадія 2 (Validator):** перевіряє цілісність полів, діапазони значень та відсікає пошкоджені записи.
* **Стадія 3 (Scorer):** обчислює показник загрози (Risk Score) на основі евристик безпеки.
* **Стадія 4 (Sink):** агрегує фінальні результати та записує валідні події до сховища.

Між кожною парою стадій розташовано **обмежений блокуючий канал** (Bounded Channel). Якщо буфер каналу заповнюється, потік попереднього фільтра автоматично блокується операційною системою через умовну змінну, запобігаючи вичерпанню пам'яті.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <memory>
#include <optional>
#include <chrono>
#include <string>
#include <atomic>

// ── Структури даних ────────────────────────────────────────────────────────
struct SecurityEvent {
    uint64_t event_id;
    std::string ip_address;
    uint16_t port;
    int payload_size;
    double risk_score{0.0};
    bool is_valid{true};
    std::chrono::steady_clock::time_point timestamp;
};

// ── 1. Обмежений потокобезпечний канал (Bounded Channel з протитиском) ─────
template <typename T>
class BoundedChannel {
public:
    explicit BoundedChannel(size_t capacity) : capacity_(capacity), closed_(false) {}

    // Відправка: блокує відправника, якщо черга заповнена (протитиск)
    bool push(T item) {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_not_full_.wait(lock, [this]() {
            return queue_.size() < capacity_ || closed_;
        });

        if (closed_) {
            return false;
        }

        queue_.push(std::move(item));
        cv_not_empty_.notify_one();
        return true;
    }

    // Отримання: блокує споживача, доки не з'явиться елемент
    std::optional<T> pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_not_empty_.wait(lock, [this]() {
            return !queue_.empty() || closed_;
        });

        if (queue_.empty() && closed_) {
            return std::nullopt;
        }

        T item = std::move(queue_.front());
        queue_.pop();
        cv_not_full_.notify_one();
        return item;
    }

    void close() {
        std::lock_guard<std::mutex> lock(mutex_);
        closed_ = true;
        cv_not_empty_.notify_all();
        cv_not_full_.notify_all();
    }

    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size();
    }

private:
    const size_t capacity_;
    std::queue<T> queue_;
    mutable std::mutex mutex_;
    std::condition_variable cv_not_empty_;
    std::condition_variable cv_not_full_;
    bool closed_;
};

// ── 2. Фільтри конвеєра ───────────────────────────────────────────────────

// Фільтр 1: Декодування та початковий розбір
void stage_parser(BoundedChannel<SecurityEvent>& in_chan,
                  BoundedChannel<SecurityEvent>& out_chan,
                  std::atomic<uint64_t>& parsed_count) {
    while (auto item = in_chan.pop()) {
        auto event = std::move(*item);
        // Імітація легкої роботи з парсингу
        std::this_thread::sleep_for(std::chrono::microseconds(100));
        parsed_count.fetch_add(1, std::memory_order_relaxed);
        
        if (!out_chan.push(std::move(event))) {
            break;
        }
    }
    out_chan.close();
}

// Фільтр 2: Валідація схеми та санітизація
void stage_validator(BoundedChannel<SecurityEvent>& in_chan,
                     BoundedChannel<SecurityEvent>& out_chan,
                     std::atomic<uint64_t>& dropped_count) {
    while (auto item = in_chan.pop()) {
        auto event = std::move(*item);
        
        // Перевірка діапазону портів та розміру корисного навантаження
        if (event.port == 0 || event.payload_size > 65535 || event.payload_size < 0) {
            dropped_count.fetch_add(1, std::memory_order_relaxed);
            continue; // Відкидаємо пошкоджений пакет
        }

        std::this_thread::sleep_for(std::chrono::microseconds(150));
        
        if (!out_chan.push(std::move(event))) {
            break;
        }
    }
    out_chan.close();
}

// Фільтр 3: Оцінка рівня загроз (CPU-інтенсивний фільтр — вузьке місце)
void stage_scorer(BoundedChannel<SecurityEvent>& in_chan,
                  BoundedChannel<SecurityEvent>& out_chan,
                  std::atomic<uint64_t>& scored_count) {
    while (auto item = in_chan.pop()) {
        auto event = std::move(*item);
        
        // Розрахунок скорингу
        double score = 0.1;
        if (event.port == 22 || event.port == 3389) {
            score += 0.4; // Підозрілі адміністративні порти
        }
        if (event.payload_size > 4096) {
            score += 0.35;
        }
        event.risk_score = score;

        // Імітація складнішого аналізу
        std::this_thread::sleep_for(std::chrono::microseconds(400));
        scored_count.fetch_add(1, std::memory_order_relaxed);

        if (!out_chan.push(std::move(event))) {
            break;
        }
    }
    out_chan.close();
}

// Фільтр 4: Приймач результатів (Sink)
void stage_sink(BoundedChannel<SecurityEvent>& in_chan,
                std::atomic<uint64_t>& committed_count) {
    while (auto item = in_chan.pop()) {
        const auto& event = *item;
        committed_count.fetch_add(1, std::memory_order_relaxed);
        // Запис у сховище
        std::this_thread::sleep_for(std::chrono::microseconds(100));
    }
}

// ── Головна точка запуску конвеєра ─────────────────────────────────────────
int main() {
    const size_t TOTAL_EVENTS = 1000;
    const size_t BUFFER_CAPACITY = 64; // Обмежені буфери між стадіями

    // Створюємо канали між 4 стадіями
    BoundedChannel<SecurityEvent> chan_raw(BUFFER_CAPACITY);
    BoundedChannel<SecurityEvent> chan_parsed(BUFFER_CAPACITY);
    BoundedChannel<SecurityEvent> chan_validated(BUFFER_CAPACITY);
    BoundedChannel<SecurityEvent> chan_scored(BUFFER_CAPACITY);

    std::atomic<uint64_t> count_parsed{0};
    std::atomic<uint64_t> count_dropped{0};
    std::atomic<uint64_t> count_scored{0};
    std::atomic<uint64_t> count_committed{0};

    auto start_time = std::chrono::steady_clock::now();

    // Запускаємо потоки фільтрів
    std::thread th_parser(stage_parser, std::ref(chan_raw), std::ref(chan_parsed), std::ref(count_parsed));
    std::thread th_validator(stage_validator, std::ref(chan_parsed), std::ref(chan_validated), std::ref(count_dropped));
    std::thread th_scorer(stage_scorer, std::ref(chan_validated), std::ref(chan_scored), std::ref(count_scored));
    std::thread th_sink(stage_sink, std::ref(chan_scored), std::ref(count_committed));

    // Джерело (Producer): наповнює вхідний канал
    for (size_t i = 1; i <= TOTAL_EVENTS; ++i) {
        SecurityEvent ev;
        ev.event_id = i;
        ev.ip_address = "192.168.1." + std::to_string(i % 254 + 1);
        ev.port = (i % 20 == 0) ? 0 : (i % 5 == 0 ? 22 : 443); // Частина невалідних
        ev.payload_size = (i % 20 == 0) ? -10 : static_cast<int>(512 + (i * 37) % 8000);
        ev.timestamp = std::chrono::steady_clock::now();

        // Якщо вхідний канал переповнений, push блокується (протитиск)
        chan_raw.push(std::move(ev));
    }
    chan_raw.close();

    // Очікуємо завершення всіх стадій конвеєра
    th_parser.join();
    th_validator.join();
    th_scorer.join();
    th_sink.join();

    auto end_time = std::chrono::steady_clock::now();
    auto elapsed_ms = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count();

    std::cout << "=== Результати роботи конвеєра ===\n";
    std::cout << "Оброблено подій парсером:   " << count_parsed.load() << "\n";
    std::cout << "Відсіяно валідатором (збій): " << count_dropped.load() << "\n";
    std::cout << "Оцінено скорингом:          " << count_scored.load() << "\n";
    std::cout << "Записано в базу (Sink):     " << count_committed.load() << "\n";
    std::cout << "Загальний час виконання:    " << elapsed_ms << " мс\n";

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>

#define BUFFER_CAPACITY 64
#define TOTAL_EVENTS 1000

// ── Структура події ────────────────────────────────────────────────────────
typedef struct {
    uint64_t event_id;
    char ip_address[32];
    uint16_t port;
    int payload_size;
    double risk_score;
    bool is_valid;
} SecurityEvent;

// ── Обмежений кільцевий буфер (Bounded Queue на POSIX Threads) ────────────
typedef struct {
    SecurityEvent buffer[BUFFER_CAPACITY];
    size_t head;
    size_t tail;
    size_t count;
    bool closed;
    pthread_mutex_t mutex;
    pthread_cond_t cv_not_full;
    pthread_cond_t cv_not_empty;
} BoundedChannel;

void channel_init(BoundedChannel* chan) {
    chan->head = 0;
    chan->tail = 0;
    chan->count = 0;
    chan->closed = false;
    pthread_mutex_init(&chan->mutex, NULL);
    pthread_cond_init(&chan->cv_not_full, NULL);
    pthread_cond_init(&chan->cv_not_empty, NULL);
}

void channel_destroy(BoundedChannel* chan) {
    pthread_mutex_destroy(&chan->mutex);
    pthread_cond_destroy(&chan->cv_not_full);
    pthread_cond_destroy(&chan->cv_not_empty);
}

bool channel_push(BoundedChannel* chan, const SecurityEvent* item) {
    pthread_mutex_lock(&chan->mutex);
    while (chan->count == BUFFER_CAPACITY && !chan->closed) {
        pthread_cond_wait(&chan->cv_not_full, &chan->mutex);
    }

    if (chan->closed) {
        pthread_mutex_unlock(&chan->mutex);
        return false;
    }

    chan->buffer[chan->tail] = *item;
    chan->tail = (chan->tail + 1) % BUFFER_CAPACITY;
    chan->count++;

    pthread_cond_signal(&chan->cv_not_empty);
    pthread_mutex_unlock(&chan->mutex);
    return true;
}

bool channel_pop(BoundedChannel* chan, SecurityEvent* out_item) {
    pthread_mutex_lock(&chan->mutex);
    while (chan->count == 0 && !chan->closed) {
        pthread_cond_wait(&chan->cv_not_empty, &chan->mutex);
    }

    if (chan->count == 0 && chan->closed) {
        pthread_mutex_unlock(&chan->mutex);
        return false;
    }

    *out_item = chan->buffer[chan->head];
    chan->head = (chan->head + 1) % BUFFER_CAPACITY;
    chan->count--;

    pthread_cond_signal(&chan->cv_not_full);
    pthread_mutex_unlock(&chan->mutex);
    return true;
}

void channel_close(BoundedChannel* chan) {
    pthread_mutex_lock(&chan->mutex);
    chan->closed = true;
    pthread_cond_broadcast(&chan->cv_not_empty);
    pthread_cond_broadcast(&chan->cv_not_full);
    pthread_mutex_unlock(&chan->mutex);
}

// ── Контексти потоків конвеєра ─────────────────────────────────────────────
typedef struct {
    BoundedChannel* in_chan;
    BoundedChannel* out_chan;
    uint64_t stat_count;
} StageContext;

void* stage_parser(void* arg) {
    StageContext* ctx = (StageContext*)arg;
    SecurityEvent event;
    while (channel_pop(ctx->in_chan, &event)) {
        usleep(100); // 100 мкс роботи
        ctx->stat_count++;
        if (!channel_push(ctx->out_chan, &event)) {
            break;
        }
    }
    channel_close(ctx->out_chan);
    return NULL;
}

void* stage_validator(void* arg) {
    StageContext* ctx = (StageContext*)arg;
    SecurityEvent event;
    while (channel_pop(ctx->in_chan, &event)) {
        if (event.port == 0 || event.payload_size < 0 || event.payload_size > 65535) {
            ctx->stat_count++; // Рахуємо як відкинуті
            continue;
        }
        usleep(150);
        if (!channel_push(ctx->out_chan, &event)) {
            break;
        }
    }
    channel_close(ctx->out_chan);
    return NULL;
}

void* stage_scorer(void* arg) {
    StageContext* ctx = (StageContext*)arg;
    SecurityEvent event;
    while (channel_pop(ctx->in_chan, &event)) {
        double score = 0.1;
        if (event.port == 22 || event.port == 3389) {
            score += 0.4;
        }
        if (event.payload_size > 4096) {
            score += 0.35;
        }
        event.risk_score = score;
        usleep(400);
        ctx->stat_count++;
        if (!channel_push(ctx->out_chan, &event)) {
            break;
        }
    }
    channel_close(ctx->out_chan);
    return NULL;
}

void* stage_sink(void* arg) {
    StageContext* ctx = (StageContext*)arg;
    SecurityEvent event;
    while (channel_pop(ctx->in_chan, &event)) {
        usleep(100);
        ctx->stat_count++;
    }
    return NULL;
}

int main(void) {
    BoundedChannel chan_raw, chan_parsed, chan_validated, chan_scored;
    channel_init(&chan_raw);
    channel_init(&chan_parsed);
    channel_init(&chan_validated);
    channel_init(&chan_scored);

    StageContext ctx_parser = { &chan_raw, &chan_parsed, 0 };
    StageContext ctx_validator = { &chan_parsed, &chan_validated, 0 };
    StageContext ctx_scorer = { &chan_validated, &chan_scored, 0 };
    StageContext ctx_sink = { &chan_scored, NULL, 0 };

    pthread_t th_parser, th_validator, th_scorer, th_sink;
    pthread_create(&th_parser, NULL, stage_parser, &ctx_parser);
    pthread_create(&th_validator, NULL, stage_validator, &ctx_validator);
    pthread_create(&th_scorer, NULL, stage_scorer, &ctx_scorer);
    pthread_create(&th_sink, NULL, stage_sink, &ctx_sink);

    // Генерація подій
    for (size_t i = 1; i <= TOTAL_EVENTS; ++i) {
        SecurityEvent ev;
        ev.event_id = i;
        snprintf(ev.ip_address, sizeof(ev.ip_address), "192.168.1.%zu", (i % 254) + 1);
        ev.port = (i % 20 == 0) ? 0 : ((i % 5 == 0) ? 22 : 443);
        ev.payload_size = (i % 20 == 0) ? -10 : (int)(512 + (i * 37) % 8000);
        ev.risk_score = 0.0;
        ev.is_valid = true;

        channel_push(&chan_raw, &ev);
    }
    channel_close(&chan_raw);

    pthread_join(th_parser, NULL);
    pthread_join(th_validator, NULL);
    pthread_join(th_scorer, NULL);
    pthread_join(th_sink, NULL);

    printf("=== Результати роботи C-конвеєра ===\n");
    printf("Оброблено парсером:          %lu\n", ctx_parser.stat_count);
    printf("Відсіяно валідатором:        %lu\n", ctx_validator.stat_count);
    printf("Оцінено скорингом:           %lu\n", ctx_scorer.stat_count);
    printf("Збережено в базу (Sink):     %lu\n", ctx_sink.stat_count);

    channel_destroy(&chan_raw);
    channel_destroy(&chan_parsed);
    channel_destroy(&chan_validated);
    channel_destroy(&chan_scored);

    return 0;
}
```
:::

## Детальний аналіз архітектурних механізмів реалізації

Побудова стабільного багатопотокового конвеєра вимагає суворого дотримання дисципліни синхронізації, керування життєвим циклом пам'яті та захисту від взаємних блокувань.

### 1. Механіка обмеженого каналу (Bounded Channel) та нульовий процесорний polling

Головна небезпека наївних реалізацій черг між потоками — використання циклів активного очікування (англ. *busy spin* або `while (queue.empty()) {}`). Такий підхід завантажує процесорні ядра на 100%, створюючи колосальне теплове навантаження та витісняючи корисні робочі потоки з планувальника ОС.

У представленій реалізації синхронізація побудована на взаємодії м'ютекса (`std::mutex` / `pthread_mutex_t`) та двох взаємодоповнюючих умовних змінних (англ. *condition variables*):
* `cv_not_empty_`: служить для сповіщення споживача, що в каналі з'явився новий елемент. Якщо канал порожній, потік споживача переходить у стан глибокого сну (блокується ядром ОС), звільняючи процесор для інших задач.
* `cv_not_full_`: реалізує механізм **активного протитиску**. Якщо кількість елементів у черзі досягає `capacity_` (у нашому прикладі 64), спроба виклику `push()` блокує потік постачальника. Відправник засинає доти, доки споживач не викличе `pop()` і не звільнить хоча б один слот у буфері.

### 2. Захист від фіктивних пробуджень (Spurious Wakeups)

Стандарти POSIX Threads та C++ гарантують, що потік може вийти зі стану очікування умовної змінної навіть за відсутності виклику `signal()` або `notify_one()` (так зване фіктивне пробудження на рівні ядра через доставку сигналів чи внутрішні оптимізації контексту).

Тому перевірка стану черги **завжди** обгортається в предикатний цикл:
* У C++ використовується перевантаження методу `cv.wait(lock, predicate)`, який автоматично виконує перевірку умови в циклі `while (!predicate())`.
* У C реалізовано явний цикл `while (chan->count == BUFFER_CAPACITY && !chan->closed) { pthread_cond_wait(...); }`.

Якщо потік прокинувся фіктивно, але буфер усе ще заповнений, він негайно повертається в стан очікування без порушення інваріантів черги.

### 3. Протокол каскадного завершення (Graceful Shutdown Cascade)

Одна з найпоширеніших пасток у конвеєрних системах — некоректна зупинка потоків, яка призводить або до втрати залишків даних у чергах, або до вічного зависання (Deadlock) на заблокованих `pop()`.

У коді реалізовано протокол каскадного закриття «зверху-вниз»:
1. Коли головне джерело завершує генерацію подій, воно викликає `chan_raw.close()`. Метод `close()` встановлює атомарний прапорець `closed_ = true` та виконує широкомовне сповіщення `notify_all()` для обох умовних змінних.
2. Потік `stage_parser` прокидається. Його цикл `while (auto item = in_chan.pop())` вичитує всі залишки елементів, що вже знаходилися в черзі. Коли черга остаточно порожніє і виявляється закритим канал, `pop()` повертає `std::nullopt` (або `false` у C).
3. `stage_parser` виходить із робочого циклу і **самостійно викликає `out_chan.close()`**, передаючи сигнал завершення наступній стадії `stage_validator`.
4. Сигнал хвилею прокочується крізь увесь конвеєр: кожна стадія повністю дообробляє свій вхідний буфер, коректно закриває свій вихід і штатно завершує потік.
5. Головний потік виконує `join()` для всіх чотирьох потоків, гарантуючи 100% збереження оброблених даних без витоків дескрипторів та пам'яті.

### 4. Оптимізація пам'яті та уникнення False Sharing

У високопродуктивних C та C++ конвеєрах критичним фактором пропускної здатності є архітектура кеш-пам'яті процесора (L1/L2/L3 кеш-лінії розміром 64 байти). 

Коли два різні потоки (наприклад, потік запису в кінець черги та потік читання з голови черги) модифікують змінні `head` та `tail`, розташовані в одному 64-байтному блоці пам'яті, виникає ефект **помилкового розділення пам'яті** (англ. *False Sharing*). Ядра процесора змушені постійно інвалідувати кеш-лінії одне одного по шині когерентності (MESI протокол), знижуючи швидкість передачі даних у 5–10 разів.

Для запобігання цьому у промислових чергах індекси `head` і `tail` вирівнюють за межею кеш-лінії:

```cpp
struct alignas(64) AlignedHead {
    size_t head{0};
};

struct alignas(64) AlignedTail {
    size_t tail{0};
};
```

Це гарантує, що операції запису виробника не впливають на кеш читача споживача на апаратному рівні.

### 5. Замкові черги проти беззамкових (Lock-Free SPSC Ringbuffers)

У представленому коді використано класичний підхід на м'ютексах та умовних змінних (Lock-based Bounded Queue). Цей дизайн є універсальним: він підтримує довільну кількість паралельних виробників і споживачів (MPMC).

Проте для ультрашвидкісних конвеєрів із суворим з'єднанням «один виробник — один споживач» (Single Producer Single Consumer, SPSC) перемикання контексту ядра ОС при блокуванні м'ютекса (затримка 1–5 мікросекунд) стає відчутним оверхедом. У таких сценаріях застосовують беззамковий кільцевий буфер (Lock-Free SPSC) на основі атомарних змінних із моделлю пам'яті Acquire-Release:

```cpp
// Запис у Lock-Free SPSC буфер без м'ютексів
bool spsc_push(const SecurityEvent& item) {
    const size_t current_tail = tail_.load(std::memory_order_relaxed);
    const size_t current_head = head_.load(std::memory_order_acquire);

    if ((current_tail + 1) % CAPACITY == current_head) {
        return false; // Буфер переповнений (протитиск)
    }

    buffer_[current_tail] = item;
    tail_.store((current_tail + 1) % CAPACITY, std::memory_order_release);
    return true;
}
```

Модель `memory_order_release` гарантує, що дані події фізично записуються в буфер пам'яті до того, як оновлений індекс `tail_` стане видимим для потоку-споживача. Потік споживача за допомогою `memory_order_acquire` бачить узгоджений стан об'єкта без необхідності блокування системних замків.

### 6. Порівняння ідіоматичних підходів C++ та C

| Архітектурний аспект | Реалізація мовою C++ | Реалізація мовою C (POSIX) |
| :--- | :--- | :--- |
| **Управління пам'яттю та переміщення** | Семантика переміщення (`std::move`). Об'єкти `SecurityEvent` передаються за значенням без глибокого копіювання динамічних рядків. | Фіксований статичний буфер у кільцевій черзі. Структури копіюються через пряме копіювання пам'яті, що виключає динамічні алокації `malloc`/`free` на гарячому шляху. |
| **Захист м'ютексів (RAII)** | `std::unique_lock` автоматично звільняє м'ютекс при виході з області видимості або викиданні виключень, гарантуючи виключення витоку замків. | Ручний виклик `pthread_mutex_unlock` перед кожною точкою виходу `return`, що вимагає граничної уважності при рефакторингу. |
| **Сигналізація порожнього стану** | Повернення `std::optional<SecurityEvent>`. Відсутність значення явно сигналізує про закриття каналу. | Повернення булевого статусу успіху `bool` із записом результату через вихідний вказівник `SecurityEvent* out_item`. |
| **Інкапсуляція каналу** | Шаблонний клас `BoundedChannel<T>`, здатний працювати з довільними типами повідомлень. | Спеціалізована структура `BoundedChannel` із прямим вбудовуванням масиву подій. |

### 7. Масштабування до пулу воркерів на вузькому місці (MPSC / MPMC)

Якщо стадія 3 (Scorer) залишається вузьким місцем конвеєра через високу складність розрахунку ризику, архітектура дозволяє підключити до одного й того самого каналу `chan_validated` кілька паралельних потоків `stage_scorer`.

Оскільки внутрішні методи `push()` та `pop()` повністю захищені спільним м'ютексом і коректно розподіляють елементи через `cv_not_empty_.notify_one()`, черга підтримує патерн Multi-Producer Multi-Consumer (MPMC) без жодних змін у коді каналу. Кожен вільний потік-воркер вихоплює наступну подію, проводить незалежний розрахунок і записує результат у вихідний канал `chan_scored`.

### 8. Інваріанти безпеки та уникнення взаємних блокувань (Deadlocks)

У багатопотокових конвеєрах небезпека взаємного блокування (Deadlock) виникає, коли потоки намагаються захоплювати кілька замків у різному порядку або коли утворюється циклічна залежність між заповненими буферами.

Для гарантії математичної відсутності дедлоків у системі підтримуються три строгі інваріанти:
1. **Односпрямованість каналів (DAG Invariant):** Топологія з'єднання каналів і фільтрів є строго ациклічною. Жоден вихідний канал наступної стадії не з'єднується безпосередньо з входом попередньої без проміжної асинхронної буферизації через брокер або розрив контексту.
2. **Ізоляція замків (Single Lock per Operation):** Жоден метод черги не утримує свій м'ютекс під час виклику методів іншого каналу. Захоплення замка відбувається суворо локально всередині `push()` або `pop()`.
3. **Пріоритет сигналів закриття:** Метод `close()` гарантує пробудження всіх заблокованих потоків (`notify_all()`), що унеможливлює зависання потоків під час аварійної зупинки джерела даних.

### 9. Класифікація та обробка помилок на стадіях конвеєра

У промисловій експлуатації конвеєра всі можливі збої поділяються на три категорії з різними стратегіями реакції:
* **Транзиторні помилки (Transient Failures):** Короткочасна недоступність зовнішньої бази даних під час збагачення. Фільтр виконує локальний повтор (Retry) до 3 разів із наростаючою затримкою та випадковим тремтінням (Exponential Backoff with Jitter).
* **Отруйні повідомлення (Poison Pills):** Некоректні дані, які викликають збій парсингу. Фільтр перехоплює помилку, збільшує лічильник відкинутих повідомлень (`dropped_count`) та негайно переходить до наступного елемента черги без зупинки конвеєра.
* **Фатальні інфраструктурні аварії:** Вичерпання дискового простору або критична помилка сховища. Стадія ініціює каскадне закриття конвеєра через `close()` та записує стан чекпоїнту для наступного ручного відновлення.

### 10. Покроковий життєвий цикл повідомлення в оперативній пам'яті

Щоб уникнути прихованих витрат на виділення пам'яті, розглянемо повний шлях об'єкта `SecurityEvent` крізь чотири стадії:

1. **Генерація (Allocation & Framing):** Постачальник створює структуру на власному стеку. У C++ поле `std::string ip_address` використовує оптимізацію малих рядків (SSO — Small String Optimization), яка для рядків довжиною до 15 байтів зберігає байти безпосередньо всередині об'єкта без виклику системного алокатора `malloc`.
2. **Передача у вхідний канал (Move to Channel):** Виклик `chan_raw.push(std::move(ev))` передає володіння ресурсами в кінець черги. М'ютекс блокується на 20–40 наносекунд. Сигнал `cv_not_empty_.notify_one()` переводить потік парсера зі стану сну в чергу планувальника ОС.
3. **Обробка та зміна стану (In-place Transformation):** Потік парсера витягує об'єкт через `pop()`, модифікує його поля за місцем (in-place) без клонування пам'яті та передає в наступний канал.
4. **Фіксація та звільнення (Sink & Destruction):** Потік приймача (`stage_sink`) вичитує фінальний об'єкт, копіює необхідні поля у накопичувальний буфер сховища, після чого деструктор `~SecurityEvent()` звільняє ресурси на виході з блоку `while`.

### 11. Оптимізація індексації кільцевого буфера через бітову маску

У C-реалізації кільцевого буфера обчислення нового індексу здійснюється через операцію ділення за модулем:

:::tabs
```cpp
tail_ = (tail_ + 1) % BUFFER_CAPACITY;
```
```c
chan->tail = (chan->tail + 1) % BUFFER_CAPACITY;
```
:::

На процесорах архітектури x86-64 та ARM інструкція цілочисельного ділення `idiv` вимагає від 15 до 40 тактів процесора. Якщо місткість буфера `BUFFER_CAPACITY` обрана степенем двійки (`2^N = 64`), операцію ділення за модулем замінюють на побітове «І» з маскою `(BUFFER_CAPACITY - 1)`:

:::tabs
```cpp
static constexpr size_t BUFFER_CAPACITY = 64;
static constexpr size_t BUFFER_MASK = BUFFER_CAPACITY - 1;

// Швидка операція за 1 такт CPU:
tail_ = (tail_ + 1) & BUFFER_MASK;
```
```c
#define BUFFER_CAPACITY 64
#define BUFFER_MASK (BUFFER_CAPACITY - 1)

// Швидка операція за 1 такт CPU:
chan->tail = (chan->tail + 1) & BUFFER_MASK;
```
:::

Ця мікрооптимізація прискорює проходження критичної секції захоплення м'ютекса вдвічі, зменшуючи час утримання замка до кількох наносекунд на кожне повідомлення.

### 12. Вимірювання часу перебування в черзі проти часу виконання фільтра

Для детального профілювання конвеєра кожне повідомлення супроводжується часовою міткою `timestamp`. Це дозволяє розділити дві принципово різні складові затримки:
* **Час очікування в черзі (Queue Wait Time):** різниця між часом вилучення з каналу `t_pop` та часом відправки попереднім фільтром `t_push`. Зростання цього показника свідчить про перевантаження поточної стадії або дефіцит воркерів.
* **Чистий час виконання (Execution Time):** тривалість виконання алгоритму фільтра `t_finish - t_start`. Зростання цього часу свідчить про ускладнення алгоритму або затримки системних викликів.

### 13. Інтеграція з подієвим циклом (Event Loop) та неблокуючим I/O

У високонавантажених мережевих сервісах перша стадія конвеєра (Ingestion) зазвичай обслуговується не окремим блокуючим потоком, а асинхронним подієвим циклом ядра ОС (`epoll` у Linux, `kqueue` у BSD/macOS або `io_uring`).

Архітектурний патерн взаємодії між подієвим циклом та конвеєром:
1. **Неблокуюче зчитування із сокета:** Подієвий цикл epoll вичитує сирі байти з мережевої карти в користувацький буфер пам'яті через системний виклик `recv()` або кільце `io_uring`.
2. **Асинхронний handoff у конвеєр:** Потік epoll не має права виконувати важкі бізнес-обчислення чи блокуватися на черзі. Він викликає неблокуючу версію `try_push()` у вхідний канал `chan_raw`.
3. **Реакція на переповнення каналу (Backpressure у мережу):** Якщо `try_push()` повертає `false` (буфер конвеєра заповнений), потік epoll тимчасово вимикає подію `EPOLLIN` для цього клієнтського сокета. Ядро Linux перестає вичитувати TCP-пакети з мережевого стеку, вікно TCP Window зменшується до нуля (`Window = 0`), і клієнт на іншому кінці мережі призупиняє передачу даних на рівні протоколу TCP.
4. **Відновлення читання:** Коли фільтр парсера звільняє місце в `chan_raw`, він надсилає сигнал у подієвий цикл, який повертає прапорець `EPOLLIN` для сокета і відновлює споживання трафіку.

### 14. Модульне тестування та ін'єкція збоїв (Chaos Testing)

Головна перевага патерну «Канали та фільтри» для розробника — виняткова простота модульного тестування (Unit Testing).

Оскільки фільтр `stage_validator` або `stage_scorer` не має прямих залежностей від решти системи і взаємодіє виключно через інтерфейс каналу:
* **Ізольоване тестування бізнес-логіки:** Тестовий стенд створює екземпляр фільтра, передає йому тестовий вхідний канал `in_chan` та вихідний канал `out_chan`. Тест записує синтетичний пакет у `in_chan`, закриває канал і перевіряє точний стан повідомлення на виході з `out_chan`.
* **Ін'єкція збоїв та стрес-тестування:** Тестовий стенд може навмисно підставити сповільнений вихідний канал із місткістю `capacity = 1`, щоб перевірити, чи коректно фільтр переходить у стан очікування протитиску та чи не втрачає дані при раптовому виклику `close()`.
* **Тестування обробки отрути:** У вхідний канал подаються пошкоджені байти, після чого перевіряється, що фільтр збільшив лічильник помилок, відправив пакет у канал мертвої черги і не завершився аварійно, зберігши працездатність для наступних коректних пакетів.

### 15. Врахування NUMA-архітектури та прив'язка потоків (Thread Affinity)

На багатопроцесорних серверах із NUMA-архітектурою (Non-Uniform Memory Access) пам'ять фізично розподілена між сокетами процесора. Якщо потік-виробник (`stage_parser`) виконується на ядрі Socket 0, а потік-споживач (`stage_validator`) мігрує планувальником ОС на Socket 1, кожна операція запису та читання з каналу змушена проходити крізь міжпроцесорну шину (Intel UPI / AMD Infinity Fabric). Це збільшує затримку доступу до пам'яті з 50 наносекунд до 200–300 наносекунд та створює паразитне навантаження на міжсокетні лінки.

Для досягнення максимальної продуктивності в низьколатентних C та C++ конвеєрах застосовують апаратну фіксацію потоків:
1. **Прив'язка до ядер (Thread Pinning):** За допомогою системного виклику `pthread_setaffinity_np()` або `sched_setaffinity()` суміжні потоки конвеєра (`F_i` та `F_{i+1}`) жорстко закріплюються за сусідніми фізичними ядрами одного сокета, які ділять спільний L3-кеш процесора.
2. **NUMA-локальна алокація:** Пам'ять буфера каналу виділяється за допомогою бібліотеки `libnuma` (`numa_alloc_onnode()`) саме в тому вузлі пам'яті, до якого прив'язані відповідні потоки фільтрів.
3. **Результат:** Зниження міжядерної затримки передачі повідомлення між стадіями до менш ніж 80 наносекунд і повне усунення міжсокетного арбітражу пам'яті. У розподілених брокерах (таких як Kafka) аналогічний принцип реалізується через розбиття черг на партиції, кожна з яких закріплюється за окремим сокетом або мережевим потоком (Network Thread Affinity).
