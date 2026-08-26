# ⚙️ Рефакторинг потоконебезпечного модуля: від глобального буфера до reentrant і thread-safe

Цей інженерний практикум демонструє покроковий процес рефакторингу реального модуля синтаксичного аналізу логів і збору метрик: від початкового потоконебезпечного коду з глобальним статичним станом до чистих реентрабельних функцій, синхронізованих потокобезпечних контейнерів та високопродуктивних структур на базі локальної пам'яті потоку (Thread-Local Storage).

---

### Постановка інженерної задачі: парсер логів мережевого шлюзу

Уявімо високонавантажений мережевий сервіс, що обробляє потік подій від сотень клієнтів. Кожне повідомлення або запис у журналі подій надходить у текстовому форматі:

`"TIMESTAMP IP_ADDRESS HTTP_METHOD STATUS_CODE BYTES"`

Завдання модуля полягає у послідовному виділенні окремих лексем із рядка (розбиття за роздільниками), вилученні числових полів та оновленні загальної системної статистики: сумарної кількості переданих байтів та лічильника помилкових запитів (HTTP-коди зі значенням 400 і вище).

У класичному однопотоковому застосунку ця задача виглядає тривіальною. Проте, коли архітектура переходить на багатопотокову модель обробки запитів (пул потоків, де кожен робочий потік бере черговий рядок із черги завдань), наївна реалізація із внутрішнім збереженням стану миттєво руйнує цілісність даних і спричиняє аварійні збої пам'яті.

---

### Етап 1: Потоконебезпечна реалізація із глобальним і статичним станом

У першій версії коду розробник використав глобальні змінні для збереження накопичувальних метрик та внутрішній статичний вказівник для відстеження поточної позиції розбору між послідовними викликами функції:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Прихований статичний стан розбору та глобальні лічильники */
static char *g_last_token_ptr = NULL;
static unsigned long g_total_bytes = 0;
static unsigned long g_error_count = 0;

char *log_parser_next_token_unsafe(char *log_line, const char *delimiter) {
    if (log_line != NULL) {
        g_last_token_ptr = log_line;
    }
    if (g_last_token_ptr == NULL || *g_last_token_ptr == '\0') {
        return NULL;
    }

    char *start = g_last_token_ptr;
    char *end = strpbrk(start, delimiter);
    if (end != NULL) {
        *end = '\0';
        g_last_token_ptr = end + 1;
    } else {
        g_last_token_ptr = NULL;
    }
    return start;
}

void log_parser_record_metric_unsafe(int status_code, unsigned long bytes) {
    g_total_bytes += bytes;
    if (status_code >= 400) {
        g_error_count++;
    }
}
```
```cpp
#include <string_view>
#include <cstdint>

namespace unsafe_log {

static std::string_view g_remaining{};
static uint64_t g_total_bytes = 0;
static uint64_t g_error_count = 0;

std::string_view next_token(std::string_view log_line, char delimiter) {
    if (!log_line.empty()) {
        g_remaining = log_line;
    }
    if (g_remaining.empty()) {
        return {};
    }

    auto pos = g_remaining.find(delimiter);
    if (pos != std::string_view::npos) {
        auto token = g_remaining.substr(0, pos);
        g_remaining.remove_prefix(pos + 1);
        return token;
    } else {
        auto token = g_remaining;
        g_remaining = {};
        return token;
    }
}

void record_metric(int status_code, uint64_t bytes) {
    g_total_bytes += bytes;
    if (status_code >= 400) {
        ++g_error_count;
    }
}

} // namespace unsafe_log
```
:::

#### Механізм руйнування стану в багатопотоковому середовищі:

1. **Перегони даних у вказівнику розбору (Data Race on State Pointer):**
   Припустимо, Потік A починає обробку рядка `"2026-08-26 192.168.1.1 GET 200 1024"`. Він передає рядок у `next_token()`, і змінна `g_last_token_ptr` починає вказувати на залишок після мітки часу. У цей момент планувальник операційної системи перемикає контекст процесора на Потік B, який викликає `next_token("10.0.0.5 POST 500 256", " ")`. Змінна `g_last_token_ptr` перезаписується адресою пам'яті рядка Потоку B. Коли Потік A відновлює виконання і викликає функцію з аргументом `NULL`, він читає залишок чужого рядка замість свого. Якщо пам'ять рядка Потоку B тим часом була звільнена або розташована на стеку, програма негайно зазнає аварійного збою сегментації (Segmentation Fault).

2. **Втрачені оновлення спільних лічильників (Lost Updates on Shared Counters):**
   Операції додавання `g_total_bytes += bytes` та інкременту `g_error_count++` на рівні асемблерного коду складаються з трьох окремих інструкцій: читання з оперативної пам'яті в регістр процесора, додавання значення в АЛП, та запис оновленого регістра назад у пам'ять. Якщо два ядра процесора виконують цей цикл паралельно, одне ядро обов'язково затре результат іншого. У результаті системні метрики втрачають від 10% до 60% реальних подій під час навантажувального тестування.

---

### Етап 2: Рефакторинг у чисту реентрабельну функцію (Caller-Allocated Context)

Щоб зробити функцію розбору реентрабельною, ми повинні повністю усунути будь-який неконстантний статичний або глобальний стан. Відповідальність за збереження проміжного положення передається викликачу, який виділяє структуру контексту на власному стеку викликів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Контекст розбору, що живе виключно на стеку викликача */
typedef struct {
    char *cursor;
} LogParserContext;

void log_parser_context_init(LogParserContext *ctx, char *log_line) {
    if (ctx != NULL) {
        ctx->cursor = log_line;
    }
}

char *log_parser_next_token_r(LogParserContext *ctx, const char *delimiter) {
    if (ctx == NULL || ctx->cursor == NULL || *ctx->cursor == '\0') {
        return NULL;
    }

    char *start = ctx->cursor;
    char *end = strpbrk(start, delimiter);
    if (end != NULL) {
        *end = '\0';
        ctx->cursor = end + 1;
    } else {
        ctx->cursor = NULL;
    }
    return start;
}
```
```cpp
#include <string_view>
#include <optional>

class ReentrantLogTokenizer {
public:
    explicit ReentrantLogTokenizer(std::string_view line) noexcept 
        : remaining_(line) {}

    std::optional<std::string_view> next_token(char delimiter) noexcept {
        if (remaining_.empty()) {
            return std::nullopt;
        }

        auto pos = remaining_.find(delimiter);
        if (pos != std::string_view::npos) {
            auto token = remaining_.substr(0, pos);
            remaining_.remove_prefix(pos + 1);
            return token;
        }

        auto token = remaining_;
        remaining_ = {};
        return token;
    }

    [[nodiscard]] bool has_more() const noexcept {
        return !remaining_.empty();
    }

private:
    std::string_view remaining_{};
};
```
:::

#### Властивості та гарантії реентрабельного коду:
- **Повна ізоляція пам'яті:** Кожен потік створює власний екземпляр `LogParserContext` або `ReentrantLogTokenizer` у межах свого фрейму стека. Оскільки стеки різних потоків розташовані за неперетинними віртуальними адресами, жоден виклик не може пошкодити стан сусіднього потоку.
- **Безпека щодо сигналів (Async-Signal Safety):** Оскільки функція не використовує блокувань і не звертається до спільної пам'яті, її можна безпечно викликати всередині обробника асинхронного сигналу ОС (наприклад, `SIGINT` або `SIGALRM`), навіть якщо цей сигнал перервав інший виклик тієї самої функції.

---

### Етап 3: Потокобезпечний синхронізований агрегатор метрик (Encapsulated Locking)

Для збору загальних метрик кількома паралельними потоками стан необхідно інкапсулювати всередині об'єкта, захищеного замком взаємного виключення (м'ютексом). Щоб унеможливити витік незаблокованого стану, операція отримання знімка метрик повинна повертати узгоджену копію обох лічильників одночасно.

:::tabs
```c
#include <pthread.h>
#include <stdint.h>

typedef struct {
    pthread_mutex_t lock;
    uint64_t total_bytes;
    uint64_t error_count;
} ThreadSafeMetrics;

int metrics_init(ThreadSafeMetrics *m) {
    if (m == NULL) return -1;
    m->total_bytes = 0;
    m->error_count = 0;
    return pthread_mutex_init(&m->lock, NULL);
}

void metrics_record(ThreadSafeMetrics *m, int status_code, uint64_t bytes) {
    if (m == NULL) return;

    pthread_mutex_lock(&m->lock);
    m->total_bytes += bytes;
    if (status_code >= 400) {
        m->error_count++;
    }
    pthread_mutex_unlock(&m->lock);
}

void metrics_get_snapshot(ThreadSafeMetrics *m, uint64_t *out_bytes, uint64_t *out_errors) {
    if (m == NULL) return;

    pthread_mutex_lock(&m->lock);
    if (out_bytes != NULL) *out_bytes = m->total_bytes;
    if (out_errors != NULL) *out_errors = m->error_count;
    pthread_mutex_unlock(&m->lock);
}

void metrics_destroy(ThreadSafeMetrics *m) {
    if (m != NULL) {
        pthread_mutex_destroy(&m->lock);
    }
}
```
```cpp
#include <mutex>
#include <cstdint>

struct MetricsSnapshot {
    uint64_t total_bytes{0};
    uint64_t error_count{0};
};

class SynchronizedMetrics {
public:
    void record(int status_code, uint64_t bytes) {
        std::lock_guard<std::mutex> guard(mutex_);
        total_bytes_ += bytes;
        if (status_code >= 400) {
            ++error_count_;
        }
    }

    [[nodiscard]] MetricsSnapshot get_snapshot() const {
        std::lock_guard<std::mutex> guard(mutex_);
        return {total_bytes_, error_count_};
    }

private:
    mutable std::mutex mutex_{};
    uint64_t total_bytes_{0};
    uint64_t error_count_{0};
};
```
:::

#### Особливості коректної синхронізації:
- **Атомарний знімок стану (State Snapshot):** Метод `get_snapshot()` зчитує обидва поля (`total_bytes_` та `error_count_`) у межах одного захоплення замка. Якби клас надавав окремі методи `get_total_bytes()` та `get_error_count()`, спостерігач міг би зчитати оновлене значення байтів, але застаріле значення помилок, отримавши внутрішньо неузгоджену картину системи.
- **Гарантія визволення ресурсів через RAII:** У C++ використання `std::lock_guard` гарантує, що м'ютекс буде надійно звільнено навіть у разі виникнення винятку в критичній секції.

---

### Етап 4: Високопродуктивна оптимізація через локальну пам'ять потоку (TLS)

Коли кількість процесорних ядер сягає десятків або сотень, конкуренція за єдиний м'ютекс призводить до деградації продуктивності: ядра процесора витрачають більшість часу на очікування черги блокування та передачу кеш-ліній через шину когерентності (Cache Contention).

Найбільш продуктивне архітектурне рішення — повна ліквідація спільних блокувань шляхом виділення кожному потоку власного локального екземпляра лічильників через механізм **Thread-Local Storage (TLS)**:

:::tabs
```c
#include <stdint.h>

/* Локальні змінні потоку в секції TLS */
static _Thread_local uint64_t tls_thread_bytes = 0;
static _Thread_local uint64_t tls_thread_errors = 0;

void tls_metrics_record(int status_code, uint64_t bytes) {
    tls_thread_bytes += bytes;
    if (status_code >= 400) {
        tls_thread_errors++;
    }
}

void tls_metrics_get_local(uint64_t *out_bytes, uint64_t *out_errors) {
    if (out_bytes != NULL) *out_bytes = tls_thread_bytes;
    if (out_errors != NULL) *out_errors = tls_thread_errors;
}
```
```cpp
#include <cstdint>

namespace fast_metrics {

struct LocalCounters {
    uint64_t total_bytes{0};
    uint64_t error_count{0};
};

// Кожен потік володіє незалежним екземпляром структури
inline thread_local LocalCounters tls_counters{};

void record(int status_code, uint64_t bytes) noexcept {
    tls_counters.total_bytes += bytes;
    if (status_code >= 400) {
        ++tls_counters.error_count;
    }
}

[[nodiscard]] LocalCounters get_local() noexcept {
    return tls_counters;
}

} // namespace fast_metrics
```
:::

#### Механізм роботи та архітектурні висновки TLS:

У моделі пам'яті TLS кожна змінна `thread_local` отримує фіксоване зміщення всередині блоку керування потоком (Thread Control Block, TCB). Під час виконання адресація здійснюється безпосередньо через спеціальні сегментні регістри процесора (регістр `FS` на x86-64 або регістр `TPIDR_EL0` на архітектурі ARM64).

Завдяки цьому:
1. Оновлення метрики виконується як звичайна локальна інструкція запису в пам'ять за лічені такти процесора.
2. Процесорні кеші різних ядер не інвалідують один одного через між'ядерну шину, оскільки кожен потік змінює власні кеш-лінії.
3. Продуктивність збору метрик масштабується строго лінійно зі зростанням кількості процесорних ядер.
4. Періодичний збір загальносистемного підсумку може виконувати фоновий потік-координатор, опитуючи локальні лічильники зареєстрованих потоків.

---

### Підсумкова таблиця архітектурних компромісів

| Характеристика | Потоконебезпечна версія | Реентрабельна версія | Синхронізована версія (Замок) | Локальна версія (TLS) |
|---|---|---|---|---|
| **Розміщення стану** | Статична глобальна пам'ять | Стек викликача | Інкапсульований об'єкт | Локальна пам'ять потоку (TLS) |
| **Потокова безпека** | ❌ Фатальні гонки даних | ✅ За ізоляції стека | ✅ Повна потокова безпека | ✅ Повна ізоляція |
| **Реентрабельність** | ❌ Небезпечно | ✅ Безпечно в сигналах | ❌ Ризик дедлоку в сигналах | ✅ Повна реентрабельність |
| **Ціна синхронізації**| Нуль (але не працює) | Нуль | Накладні витрати на черги замка | Нуль (пряма адресація TCB) |
| **Масштабованість** | Відсутня | Ідеальна лінійна | Падає при високій конкуренції | Ідеальна лінійна |
