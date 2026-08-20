# ⚙️ Реалізація високопродуктивного конвеєра фільтрації повідомлень

У високонавантажених розподілених системах брокери, маршрутизатори та сервісні шлюзи обробляють сотні тисяч і мільйони подій на секунду на один процесорний вузол. Якщо кожен фільтр повідомлень на гарячому шляху буде виділяти динамічну пам'ять у купі (heap allocation) для створення проміжних рядкових об'єктів або виконувати повну десеріалізацію тіла повідомлення, пропускна здатність вузла миттєво впаде на два порядки через фрагментацію пам'яті, постійний тиск на збирач сміття або блокування системного алокатора `malloc`.

Головна вимога до промислового рушія фільтрації — **нульове копіювання даних (Zero-Copy)** та **обчислення типізованих предикатів виключно над заголовками фіксованої структури**.

У цьому проєкті ми спроєктуємо та реалізуємо з нуля повнофункціональний, кешо-дружній рушій фільтрації повідомлень мовами C та C++. Рушій підтримує типізовані предикати (рядкові еквівалентності, префікси, числові діапазони, бітові маски), композитні логічні правила (`AND`, `OR`, `NOT`), конвеєрну обробку зі скороченим циклом обчислення (short-circuit) та збір детальних метрик продуктивності.

## Архітектурний дизайн та організація пам'яті

Для досягнення максимальної пропускної здатності (понад 10 000 000 перевірок на секунду на ядро) внутрішня архітектура рушія спирається на три фундаментальні принципи:

### 1. Незмінність та відсутність динамічних алокацій на гарячому шляху
Повідомлення, отримане з мережевого сокета, розміщується в безперервному буфері кадрів. Замість копіювання рядків у нові об'єкти `std::string` чи масиви `char*`, заголовок повідомлення зберігає лише посилання на байти всередині цього існуючого буфера:
* У C++ для цього використовується `std::string_view` (який займає рівно 16 байтів: 8 байтів покажчика на пам'ять + 8 байтів розміру) та `std::span<const uint8_t>` для сирого двійкового навантаження.
* У C застосовується пара з константного покажчика `const char*` та лічильника довжини `size_t`.

Корисне навантаження повідомлення (`payload`) розглядається як непрозорий масив байтів: рушій фільтрації взагалі не читає і не парсить його байти, залишаючи їх незайманими в пам'яті процесу або сторінковому кеші операційної системи.

### 2. Кешова локальність першого рівня (L1 Data Cache)
У мові C структура `MessageHeader` скомпонована у вигляді фіксованого масиву з 32 елементів. Такий масив займає менше 1 КБ пам'яті. Сучасні процесори вичитують дані з оперативної пам'яті лініями кешу по 64 байти. При послідовній перевірці заголовків усі метадані повідомлення вже знаходяться в надшвидкому кеші L1. Лінійний пошук за 5–10 заголовками виконується швидше, ніж звернення до хеш-таблиці, оскільки хеш-таблиця призводить до непередбачуваних стрибків за покажчиками та розривів кешу (*cache misses*).

### 3. Безпека типів без оверхеду (Tagged Union vs std::variant)
Значення заголовка може бути рядком, 64-бітним цілим числом зі знаком (`int64_t`), дробовим числом подвійної точності (`double`) або 64-бітовою маскою прапорців (`uint64_t`).
* У C ми використовуємо розмічене об'єднання `union` у поєднанні з переліком `ValueType`.
* У C++ використовується `std::variant`, який гарантує типобезпеку на етапі компіляції та відсутність динамічної пам'яті.

## Детальний розбір бінарного представлення структур у пам'яті

Розглянемо, як саме розміщуються в пам'яті структури даних заголовків та чому обрана схема забезпечує максимальну швидкодію.

У мові C розмічене об'єднання `HeaderValue` містить два обов'язкові компоненти: дискримінатор типу `ValueType` та об'єднання `union as`. На 64-бітній системі:
- Поле `type` (перелік `enum`) займає 4 байти.
- Компілятор додає 4 байти вирівнювання (padding), щоб наступне поле `union` починалося з адреси, кратної 8 байтам.
- Внутрішня анонімна структура `str` містить покажчик `const char*` (8 байтів) та довжину `size_t` (8 байтів), займаючи сумарно 16 байтів.
- Числові поля `int64_t`, `double` та `uint64_t` займають по 8 байтів і перекривають ту саму пам'ять.
- Загальний розмір `HeaderValue` становить рівно **24 байти**.

Структура `MessageHeader` поєднує покажчик на ключ `key` (8 байтів), довжину ключа `key_len` (8 байтів) та значення `val` (24 байти), займаючи рівно **40 байтів**.

Масив із 32 таких заголовків у структурі `Message` займає `32 · 40 = 1280` байтів. Коли повідомлення передається у функцію обробки фільтрів, увесь цей блок даних завантажується в процесорний кеш за 20 послідовних ліній кешу (по 64 байти). Це виключає звернення до повільної основної пам'яті DRAM під час виконання всього ланцюга перевірок.

На відміну від функцій стандартної бібліотеки мови C на зразок `strcmp()` або `strcpy()`, які вимагають наявності завершального нульового байта (`\0`), у мережевих протоколах (AMQP, HTTP/2, Kafka Wire Protocol) рядки передаються у вигляді зрізів (*slices*) фіксованої довжини. Використання функції `memcmp()` із явною довжиною дозволяє зіставляти рядки без необхідності мутувати буфер сокета чи додавати штучні нульові терминітори.

## Реалізація конвеєра фільтрації

Нижче наведено повні та ідіоматичні реалізації рушія фільтрації повідомлень.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#define MAX_HEADERS 32
#define MAX_FILTERS 16

/* Типи значень у заголовках повідомлення */
typedef enum {
    VAL_TYPE_STRING,
    VAL_TYPE_INT64,
    VAL_TYPE_DOUBLE,
    VAL_TYPE_BITMASK
} ValueType;

/* Типізоване значення заголовка (Zero-Copy для рядків) */
typedef struct {
    ValueType type;
    union {
        struct {
            const char* ptr;
            size_t len;
        } str;
        int64_t i64;
        double  f64;
        uint64_t mask;
    } as;
} HeaderValue;

/* Окремий заголовок: ключ + значення */
typedef struct {
    const char* key;
    size_t key_len;
    HeaderValue val;
} MessageHeader;

/* Структура повідомлення */
typedef struct {
    uint64_t message_id;
    MessageHeader headers[MAX_HEADERS];
    size_t header_count;
    const uint8_t* payload_ptr;
    size_t payload_len;
} Message;

/* Типи операцій порівняння предикатів */
typedef enum {
    OP_EQUALS_STRING,
    OP_PREFIX_STRING,
    OP_INT_GREATER_THAN,
    OP_INT_LESS_OR_EQUAL,
    OP_BITMASK_ALL_SET,
    OP_HEADER_EXISTS
} PredicateOp;

/* Політика при помилці (відсутнє поле, невідповідний тип) */
typedef enum {
    POLICY_DROP_ON_ERROR,
    POLICY_PASS_ON_ERROR,
    POLICY_DEAD_LETTER_ON_ERROR
} ErrorPolicy;

/* Результат обчислення фільтра */
typedef enum {
    FILTER_DECISION_PASS,
    FILTER_DECISION_DROP,
    FILTER_DECISION_DEAD_LETTER
} FilterDecision;

/* Структура предикату */
typedef struct {
    const char* target_header;
    size_t target_header_len;
    PredicateOp op;
    HeaderValue expected_val;
    bool invert_result; /* Для операції NOT */
} FilterPredicate;

/* Статистика роботи конвеєра */
typedef struct {
    uint64_t total_evaluated;
    uint64_t passed_count;
    uint64_t dropped_count;
    uint64_t dead_letter_count;
} PipelineMetrics;

/* Конвеєр фільтрів (ланцюг) */
typedef struct {
    FilterPredicate predicates[MAX_FILTERS];
    size_t predicate_count;
    ErrorPolicy error_policy;
    PipelineMetrics metrics;
} FilterPipeline;

/* Ініціалізація повідомлення */
void message_init(Message* msg, uint64_t id, const uint8_t* payload, size_t payload_len) {
    msg->message_id = id;
    msg->header_count = 0;
    msg->payload_ptr = payload;
    msg->payload_len = payload_len;
}

/* Додавання рядкового заголовка без копіювання байтів */
bool message_add_str_header(Message* msg, const char* key, const char* str_val) {
    if (msg->header_count >= MAX_HEADERS) return false;
    MessageHeader* h = &msg->headers[msg->header_count++];
    h->key = key;
    h->key_len = strlen(key);
    h->val.type = VAL_TYPE_STRING;
    h->val.as.str.ptr = str_val;
    h->val.as.str.len = strlen(str_val);
    return true;
}

/* Додавання числового заголовка int64 */
bool message_add_i64_header(Message* msg, const char* key, int64_t val) {
    if (msg->header_count >= MAX_HEADERS) return false;
    MessageHeader* h = &msg->headers[msg->header_count++];
    h->key = key;
    h->key_len = strlen(key);
    h->val.type = VAL_TYPE_INT64;
    h->val.as.i64 = val;
    return true;
}

/* Додавання бітової маски */
bool message_add_mask_header(Message* msg, const char* key, uint64_t mask) {
    if (msg->header_count >= MAX_HEADERS) return false;
    MessageHeader* h = &msg->headers[msg->header_count++];
    h->key = key;
    h->key_len = strlen(key);
    h->val.type = VAL_TYPE_BITMASK;
    h->val.as.mask = mask;
    return true;
}

/* Пошук заголовка за ключем (O(H)) */
static const HeaderValue* message_find_header(const Message* msg, const char* key, size_t key_len) {
    for (size_t i = 0; i < msg->header_count; ++i) {
        if (msg->headers[i].key_len == key_len &&
            memcmp(msg->headers[i].key, key, key_len) == 0) {
            return &msg->headers[i].val;
        }
    }
    return NULL;
}

/* Ініціалізація конвеєра */
void pipeline_init(FilterPipeline* pipe, ErrorPolicy policy) {
    pipe->predicate_count = 0;
    pipe->error_policy = policy;
    memset(&pipe->metrics, 0, sizeof(PipelineMetrics));
}

/* Додавання предикату до конвеєра */
bool pipeline_add_predicate(FilterPipeline* pipe, FilterPredicate pred) {
    if (pipe->predicate_count >= MAX_FILTERS) return false;
    pipe->predicates[pipe->predicate_count++] = pred;
    return true;
}

/* Оцінка окремого предикату над повідомленням */
static int evaluate_predicate(const FilterPredicate* pred, const Message* msg, bool* out_result) {
    const HeaderValue* actual = message_find_header(msg, pred->target_header, pred->target_header_len);

    if (pred->op == OP_HEADER_EXISTS) {
        *out_result = (actual != NULL) ^ pred->invert_result;
        return 0; /* Успішна оцінка */
    }

    if (!actual) {
        return -1; /* Помилка: заголовок відсутній */
    }

    bool matched = false;
    switch (pred->op) {
        case OP_EQUALS_STRING:
            if (actual->type != VAL_TYPE_STRING) return -1;
            matched = (actual->as.str.len == pred->expected_val.as.str.len) &&
                      (memcmp(actual->as.str.ptr, pred->expected_val.as.str.ptr, actual->as.str.len) == 0);
            break;

        case OP_PREFIX_STRING:
            if (actual->type != VAL_TYPE_STRING) return -1;
            if (actual->as.str.len < pred->expected_val.as.str.len) {
                matched = false;
            } else {
                matched = (memcmp(actual->as.str.ptr, pred->expected_val.as.str.ptr, pred->expected_val.as.str.len) == 0);
            }
            break;

        case OP_INT_GREATER_THAN:
            if (actual->type != VAL_TYPE_INT64) return -1;
            matched = (actual->as.i64 > pred->expected_val.as.i64);
            break;

        case OP_INT_LESS_OR_EQUAL:
            if (actual->type != VAL_TYPE_INT64) return -1;
            matched = (actual->as.i64 <= pred->expected_val.as.i64);
            break;

        case OP_BITMASK_ALL_SET:
            if (actual->type != VAL_TYPE_BITMASK) return -1;
            matched = ((actual->as.mask & pred->expected_val.as.mask) == pred->expected_val.as.mask);
            break;

        default:
            return -1;
    }

    *out_result = matched ^ pred->invert_result;
    return 0;
}

/* Прогін повідомлення крізь конвеєр із short-circuit логікою */
FilterDecision pipeline_process(FilterPipeline* pipe, const Message* msg) {
    pipe->metrics.total_evaluated++;

    for (size_t i = 0; i < pipe->predicate_count; ++i) {
        bool result = false;
        int status = evaluate_predicate(&pipe->predicates[i], msg, &result);

        if (status != 0) {
            /* Обробка ситуації помилки (missing header або type mismatch) */
            switch (pipe->error_policy) {
                case POLICY_DROP_ON_ERROR:
                    pipe->metrics.dropped_count++;
                    return FILTER_DECISION_DROP;
                case POLICY_PASS_ON_ERROR:
                    continue; /* Пропускаємо дефектне правило і йдемо далі */
                case POLICY_DEAD_LETTER_ON_ERROR:
                    pipe->metrics.dead_letter_count++;
                    return FILTER_DECISION_DEAD_LETTER;
            }
        }

        /* Якщо предикат повернув FALSE — негайне скидання (Short-Circuit) */
        if (!result) {
            pipe->metrics.dropped_count++;
            return FILTER_DECISION_DROP;
        }
    }

    pipe->metrics.passed_count++;
    return FILTER_DECISION_PASS;
}

int main(void) {
    FilterPipeline pipeline;
    pipeline_init(&pipeline, POLICY_DROP_ON_ERROR);

    /* Правило 1: Регіон повинен бути "EU" */
    FilterPredicate p1 = {
        .target_header = "region",
        .target_header_len = 6,
        .op = OP_EQUALS_STRING,
        .expected_val = { .type = VAL_TYPE_STRING, .as.str = { .ptr = "EU", .len = 2 } },
        .invert_result = false
    };
    pipeline_add_predicate(&pipeline, p1);

    /* Правило 2: Пріоритет > 3 */
    FilterPredicate p2 = {
        .target_header = "priority",
        .target_header_len = 8,
        .op = OP_INT_GREATER_THAN,
        .expected_val = { .type = VAL_TYPE_INT64, .as.i64 = 3 },
        .invert_result = false
    };
    pipeline_add_predicate(&pipeline, p2);

    /* Тестове повідомлення № 1 (відповідає всім умовам) */
    const char payload1[] = "{\"order_id\": 991, \"amount\": 450.00}";
    Message msg1;
    message_init(&msg1, 1001, (const uint8_t*)payload1, strlen(payload1));
    message_add_str_header(&msg1, "region", "EU");
    message_add_i64_header(&msg1, "priority", 5);

    /* Тестове повідомлення № 2 (чужий регіон "US" -> має бути відкинуте) */
    const char payload2[] = "{\"order_id\": 992, \"amount\": 120.00}";
    Message msg2;
    message_init(&msg2, 1002, (const uint8_t*)payload2, strlen(payload2));
    message_add_str_header(&msg2, "region", "US");
    message_add_i64_header(&msg2, "priority", 9);

    FilterDecision d1 = pipeline_process(&pipeline, &msg1);
    FilterDecision d2 = pipeline_process(&pipeline, &msg2);

    printf("Повідомлення #1001 результат: %s\n", d1 == FILTER_DECISION_PASS ? "PASS" : "DROP");
    printf("Повідомлення #1002 результат: %s\n", d2 == FILTER_DECISION_PASS ? "PASS" : "DROP");
    printf("Метрики конвеєра: всього=%lu, пропущено=%lu, відсіяно=%lu\n",
           pipeline.metrics.total_evaluated,
           pipeline.metrics.passed_count,
           pipeline.metrics.dropped_count);

    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <span>
#include <vector>
#include <memory>
#include <variant>
#include <optional>
#include <cstdint>
#include <cstring>

namespace messaging {

enum class ValueType {
    String,
    Int64,
    Double,
    Bitmask
};

/* Типізоване значення заголовка з підтримкою string_view (нульове копіювання) */
using HeaderValue = std::variant<std::string_view, int64_t, double, uint64_t>;

struct MessageHeader {
    std::string_view key;
    HeaderValue value;
};

/* Незмінне повідомлення з легкою структурою метаданих */
class Message {
public:
    Message(uint64_t id, std::span<const uint8_t> payload)
        : id_(id), payload_(payload) {}

    void add_header(std::string_view key, HeaderValue value) {
        headers_.push_back({key, std::move(value)});
    }

    [[nodiscard]] uint64_t id() const noexcept { return id_; }
    [[nodiscard]] std::span<const uint8_t> payload() const noexcept { return payload_; }
    [[nodiscard]] const std::vector<MessageHeader>& headers() const noexcept { return headers_; }

    [[nodiscard]] std::optional<HeaderValue> find_header(std::string_view key) const noexcept {
        for (const auto& [k, v] : headers_) {
            if (k == key) return v;
        }
        return std::nullopt;
    }

private:
    uint64_t id_;
    std::span<const uint8_t> payload_;
    std::vector<MessageHeader> headers_;
};

enum class FilterDecision {
    Pass,
    Drop,
    DeadLetter
};

enum class ErrorPolicy {
    DropOnError,
    PassOnError,
    DeadLetterOnError
};

/* Базовий інтерфейс окремого предикату */
class IPredicate {
public:
    virtual ~IPredicate() = default;
    [[nodiscard]] virtual std::optional<bool> evaluate(const Message& msg) const noexcept = 0;
};

/* Предикат суворої рядкової рівності */
class StringEqualsPredicate final : public IPredicate {
public:
    StringEqualsPredicate(std::string_view header_key, std::string_view expected_value, bool invert = false)
        : key_(header_key), expected_(expected_value), invert_(invert) {}

    [[nodiscard]] std::optional<bool> evaluate(const Message& msg) const noexcept override {
        auto val = msg.find_header(key_);
        if (!val.has_value()) return std::nullopt; // Заголовок відсутній

        if (const auto* str_ptr = std::get_if<std::string_view>(&*val)) {
            bool matches = (*str_ptr == expected_);
            return matches ^ invert_;
        }
        return std::nullopt; // Невідповідність типу
    }

private:
    std::string_view key_;
    std::string_view expected_;
    bool invert_;
};

/* Предикат порівняння цілих чисел (Greater Than) */
class IntGreaterThanPredicate final : public IPredicate {
public:
    IntGreaterThanPredicate(std::string_view header_key, int64_t threshold)
        : key_(header_key), threshold_(threshold) {}

    [[nodiscard]] std::optional<bool> evaluate(const Message& msg) const noexcept override {
        auto val = msg.find_header(key_);
        if (!val.has_value()) return std::nullopt;

        if (const auto* i_ptr = std::get_if<int64_t>(&*val)) {
            return (*i_ptr > threshold_);
        }
        return std::nullopt;
    }

private:
    std::string_view key_;
    int64_t threshold_;
};

/* Композитний логічний оператор AND над списком підпредикатів */
class AndCompositePredicate final : public IPredicate {
public:
    void add(std::unique_ptr<IPredicate> pred) {
        children_.push_back(std::move(pred));
    }

    [[nodiscard]] std::optional<bool> evaluate(const Message& msg) const noexcept override {
        for (const auto& child : children_) {
            auto res = child->evaluate(msg);
            if (!res.has_value()) return std::nullopt; // Помилка обчислення
            if (!*res) return false; // Short-circuit: один false зупиняє весь AND
        }
        return true;
    }

private:
    std::vector<std::unique_ptr<IPredicate>> children_;
};

/* Метрики продуктивності конвеєра */
struct PipelineMetrics {
    uint64_t total_evaluated{0};
    uint64_t passed{0};
    uint64_t dropped{0};
    uint64_t dead_lettered{0};
};

/* Конвеєр фільтрації з обробкою помилок та збором статистики */
class FilterPipeline {
public:
    explicit FilterPipeline(ErrorPolicy policy = ErrorPolicy::DropOnError)
        : policy_(policy) {}

    void add_stage(std::unique_ptr<IPredicate> predicate) {
        stages_.push_back(std::move(predicate));
    }

    FilterDecision process(const Message& msg) noexcept {
        ++metrics_.total_evaluated;

        for (const auto& stage : stages_) {
            auto result = stage->evaluate(msg);

            if (!result.has_value()) {
                switch (policy_) {
                    case ErrorPolicy::DropOnError:
                        ++metrics_.dropped;
                        return FilterDecision::Drop;
                    case ErrorPolicy::PassOnError:
                        continue;
                    case ErrorPolicy::DeadLetterOnError:
                        ++metrics_.dead_lettered;
                        return FilterDecision::DeadLetter;
                }
            }

            if (!*result) {
                ++metrics_.dropped;
                return FilterDecision::Drop;
            }
        }

        ++metrics_.passed;
        return FilterDecision::Pass;
    }

    [[nodiscard]] const PipelineMetrics& metrics() const noexcept { return metrics_; }

private:
    ErrorPolicy policy_;
    std::vector<std::unique_ptr<IPredicate>> stages_;
    PipelineMetrics metrics_;
};

} // namespace messaging

int main() {
    using namespace messaging;

    FilterPipeline pipeline(ErrorPolicy::DropOnError);

    // Додаємо стадію 1: region == "EU"
    pipeline.add_stage(std::make_unique<StringEqualsPredicate>("region", "EU"));

    // Додаємо стадію 2: priority > 3
    pipeline.add_stage(std::make_unique<IntGreaterThanPredicate>("priority", 3));

    // Створюємо тестове повідомлення № 1
    const std::string body1 = "{\"order_id\": 991, \"amount\": 450.00}";
    std::span<const uint8_t> span1(reinterpret_cast<const uint8_t*>(body1.data()), body1.size());
    Message msg1(1001, span1);
    msg1.add_header("region", std::string_view("EU"));
    msg1.add_header("priority", int64_t{5});

    // Створюємо тестове повідомлення № 2 (нецільовий регіон US)
    const std::string body2 = "{\"order_id\": 992, \"amount\": 120.00}";
    std::span<const uint8_t> span2(reinterpret_cast<const uint8_t*>(body2.data()), body2.size());
    Message msg2(1002, span2);
    msg2.add_header("region", std::string_view("US"));
    msg2.add_header("priority", int64_t{9});

    auto d1 = pipeline.process(msg1);
    auto d2 = pipeline.process(msg2);

    std::cout << "Повідомлення #1001 результат: " << (d1 == FilterDecision::Pass ? "PASS" : "DROP") << '\n';
    std::cout << "Повідомлення #1002 результат: " << (d2 == FilterDecision::Pass ? "PASS" : "DROP") << '\n';
    std::cout << "Метрики конвеєра: всього=" << pipeline.metrics().total_evaluated
              << ", пропущено=" << pipeline.metrics().passed
              << ", відсіяно=" << pipeline.metrics().dropped << '\n';

    return 0;
}
```
:::

## Покроковий аналіз виконання конвеєра над пам'яттю

Розглянемо детально, що відбувається в регістрах та пам'яті процесора під час обробки двох тестових повідомлень функцією `pipeline_process`:

### Фаза обробки повідомлення № 1001:
1. **Ініціалізація кадру:** повідомлення отримує покажчик на байтовий буфер корисного навантаження (`body1`). Жодного копіювання 35 байтів JSON не відбувається — у структуру `Message` записуються лише дві 64-бітні змінні: адреса пам'яті початку рядка та довжина 35.
2. **Додавання заголовків:** до масиву `headers` записується перший заголовок: ключ `"region"` (покажчик на статичну пам'ять рядкового літералу, довжина 6) та типізоване значення `std::string_view("EU")` (довжина 2). Наступним записується заголовок `"priority"` з цілочисельним значенням `5`.
3. **Виклик першої стадії конвеєра (`StringEqualsPredicate`):**
   - Рушій виконує пошук заголовка `"region"`. Перший же елемент масиву має `key_len == 6` та ідентичні байти.
   - Метод `evaluate` перевіряє тип значення: це `std::string_view`.
   - Виконується порівняння `memcmp("EU", "EU", 2) == 0`.
   - Результат стадії: `true`.
4. **Виклик другої стадії конвеєра (`IntGreaterThanPredicate`):**
   - Рушій сканує масив і знаходить заголовок `"priority"`.
   - Перевіряється тип `int64_t` та умова `5 > 3`.
   - Результат стадії: `true`.
5. **Фінальне рішення:** оскільки всі стадії повернули `true`, конвеєр інкрементує лічильник `passed` і повертає `FilterDecision::Pass`. Повідомлення передається робочому потоку бізнес-логіки.

### Фаза обробки повідомлення № 1002:
1. **Ініціалізація та пошук заголовка:** повідомлення містить заголовок `region="US"`.
2. **Виклик першої стадії:**
   - Пошук знаходить заголовок `"region"`.
   - `memcmp("US", "EU", 2)` повертає ненульове значення (невідповідність).
   - Метод `evaluate` повертає `false`.
3. **Механізм Short-Circuit (раннє переривання):**
   - Конвеєр фіксує значення `false` на стадії 1.
   - Цикл негайно переривається: друга стадія перевірки пріоритету (`priority > 3`) **взагалі не викликається**, заощаджуючи процесорні такти.
   - Лічильник `dropped` збільшується на 1, функція повертає `FilterDecision::Drop`. Пам'ять вхідного буфера негайно звільняється під наступний мережевий пакет сокета.

## Композиція складних булевих виразів (AST)

У промислових підписках правила рідко обмежуються простою кон'юнкцією `AND`. Споживачам часто потрібні складені логічні дерева з диз'юнкціями (`OR`) та запереченнями (`NOT`), наприклад:

```
(region == "EU" OR region == "UK") AND (priority >= 5 OR customer_tier == "VIP") AND NOT is_test
```

У наведеній реалізації на C++ інтерфейс `IPredicate` побудовано за патерном **Компоновщик (Composite)**. Клас `AndCompositePredicate` об'єднує довільний набір дочірніх предикатів, кожен з яких сам може бути іншим складеним вузлом (наприклад, `OrCompositePredicate`).

Обчислення такого дерева виконується рекурсивним спуском із дотриманням короткого замикання:
* Для вузла `AND`: якщо будь-який дочірній елемент повернув `false`, обчислення решти гілок миттєво зупиняється.
* Для вузла `OR`: якщо будь-який дочірній елемент повернув `true`, решта гілок ігнорується, а результат вважається істинним.
* Для вузла `NOT`: результат дочірнього предиката інвертується.

Оскільки всі поліморфні вузли дерева створюються один раз під час ініціалізації конвеєра і зберігаються за допомогою `std::unique_ptr<IPredicate>`, під час прогону повідомлень не виділяється жодного байта пам'яті.

## Батчевий конвеєр та амортизація системних викликів

Для досягнення пікової пропускної здатності на мережевих інтерфейсах 100GbE рушій фільтрації викликається не поодинці для кожного окремого повідомлення, а обробляє кадри пачками (*batches*):

```cpp
void process_batch(std::span<const Message> batch, std::vector<FilterDecision>& results) {
    results.resize(batch.size());
    for (size_t i = 0; i < batch.size(); ++i) {
        results[i] = process(batch[i]);
    }
}
```

Такий підхід дає три фундаментальні переваги:
1. **Інструкційне кешування (I-Cache):** під час виконання одного й того самого коду предикату над 64 повідомленнями поспіль інструкції функції `evaluate` постійно знаходяться в кеші L1i, усуваючи затримки декодування інструкцій.
2. **Амортизація системних викликів сокетів:** застосування `recvmmsg()` та `sendmmsg()` на рівні ОС дозволяє приймати та відправляти сотні пакетів за один перехід у простір ядра Linux, знижуючи накладні витрати на перемикання контексту.
3. **Ефективне передбачення переходів (Branch Prediction):** процесорний блок Branch Target Buffer (BTB) швидко навчається на однорідних потоках повідомлень, знижуючи штраф за хибне передбачення гілок до менш ніж 1% тактів.

## Обробка виняткових ситуацій та політики помилок

У реальних розподілених системах повідомлення часто надходять у некоректному або неповному стані: старий сервіс-продюсер публікує застарілу версію схеми без обов'язкового поля `tenant_id`, або невірно серіалізує пріоритет як рядок `"high"` замість числа `5`.

Рушій фільтрації повинен чітко розділяти два принципово різні стани:
1. **Штатний результат обчислення (Evaluation Result):** предикат успішно обчислений і повернув `true` (пропустити) або `false` (скинути).
2. **Помилка обчислення (Evaluation Error):** предикат не зміг виконатися через відсутність цільового заголовка або несумісність типів.

Для керування поведінкою системи в разі помилки обчислення в рушії реалізовано три взаємовиключні політики `ErrorPolicy`:

### 1. `DropOnError` (Сувора відмова)
Якщо заголовок відсутній або має некоректний тип, повідомлення негайно відкидається.
* *Переваги:* гарантує максимальну безпеку та ізоляцію. Споживач ніколи не отримає повідомлення з невалідними метаданими.
* *Сфера застосування:* мультитенантні системи, сервіси білінгу та контролю прав доступу, де пропуск некоректного повідомлення може призвести до витоку даних іншого клієнта.

### 2. `PassOnError` (М'який пропуск / Fail-Open)
Якщо правило не може бути обчислене, воно ігнорується, а конвеєр переходить до наступної стадії.
* *Переваги:* забезпечує зворотну сумісність при розгортанні нових фільтрів у неоднорідному середовищі, де частина продюсерів ще не оновила свій код.
* *Ризики:* споживач може отримати повідомлення, які не призначалися для його обробки, перекладаючи валідацію на рівень бізнес-коду.

### 3. `DeadLetterOnError` (Карантин / Аудит)
Повідомлення не відкидається мовчки, а позначається статусом `FilterDecision::DeadLetter` і перенаправляється в ізольовану мертву чергу (Dead Letter Queue, DLQ) разом із діагностичними метаданими (ім'я відсутнього заголовка, очікуваний тип, код помилки).
* *Переваги:* забезпечує 100% спостережуваність і дозволяє інженерам виявляти баги серіалізації на стороні продюсерів без зупинки основного конвеєра обробки.

## Порівняння профілів виділення пам'яті (Heap Profiling)

При профілюванні наївного рушія фільтрації (який створює копії рядків `std::string` та виділяє об'єкти на кожне повідомлення) інструментами **Valgrind Massif** або **jemalloc heap profiling** спостерігається інтенсивне виділення десятків гігабайтів тимчасової пам'яті на хвилину. Це призводить до блокувань глобальних м'ютексів алокатора glibc та фрагментації віртуального адресного простору процесу.

На противагу цьому, запропонований конвеєр Zero-Copy демонструє ідеально плоский профіль пам'яті:
* Під час ініціалізації виділяється фіксований пул структур правил (кілька кілобайтів).
* Під час безперервної обробки мільйонів повідомлень графік виділення оперативної пам'яті залишається на позначці **0 байтів/с**.
* Відсутність навантаження на підсистему пам'яті вивільняє пропускну здатність шини пам'яті DDR5/HBM виключно для потреб корисної бізнес-логіки споживачів.

## Виробничі пастки та оптимізація під екстремальні навантаження

Розгортання рушіїв фільтрації в реальних високопродуктивних системах вимагає врахування таких інженерних тонкощів:

### 1. Життєвий цикл пам'яті заголовків (Dangling Pointers)
Оскільки реалізація повністю покладається на `std::string_view` та сирі покажчики `const char*`, ці покажчики є валідними **лише доти, доки живе вхідний мережевий буфер сокета**.
* Якщо фільтр повертає `FilterDecision::Drop`, буфер сокета можна негайно перезаписувати новим пакетом — жодних витрат на виділення чи очищення пам'яті не було.
* Якщо фільтр повертає `FilterDecision::Pass`, і повідомлення має бути передане в асинхронну чергу іншого робочого потоку (наприклад, через lock-free кільцевий буфер), саме на цьому етапі споживач повинен здійснити глибоке копіювання (*materialization*) лише тих полів, які потрібні для подальшої бізнес-логіки.
Таке відкладене копіювання гарантує, що 95–99% відкинутих повідомлень не витратять жодного виклику системного алокатора `malloc`.

### 2. Динамічне оновлення конфігурацій без блокувань (Read-Copy-Update)
У мікросервісній архітектурі правила фільтрації часто змінюються на льоту: адміністратор додає новий фільтр орендаря або змінює версію схеми через REST API управління.

Використання звичайного блокуючого м'ютекса (`std::mutex` або `pthread_mutex_t`) для захисту вектора `stages_` є неприпустимим: за мільйона операцій на секунду захоплення м'ютекса робочими потоками спричинить катастрофічну деградацію через конкуренцію за кеш-лінії ядер CPU (*cache line bouncing*).

Найкращим архітектурним рішенням є патерн **Read-Copy-Update (RCU)** через атомарний розумний покажчик:

```cpp
class ThreadSafeFilterEngine {
public:
    FilterDecision process(const Message& msg) const {
        // Читачі отримують копію атомарного shared_ptr без жодних блокувань
        std::shared_ptr<const FilterPipeline> current = std::atomic_load(&pipeline_);
        return current->process(msg);
    }

    void update_rules(std::shared_ptr<const FilterPipeline> new_pipeline) {
        // Потік управління атомарно підміняє старий конвеєр новим
        std::atomic_store(&pipeline_, std::move(new_pipeline));
        // Старий конвеєр буде автоматично видалений, щойно його дочитає останній робочий потік
    }

private:
    std::shared_ptr<const FilterPipeline> pipeline_;
};
```

У цій моделі робочі потоки обробки читають незмінну конфігурацію конвеєра з нульовими накладними витратами на синхронізацію, а потік оновлення правил компілює новий об'єкт `FilterPipeline` у фоні й атомарно підміняє вказівник однією процесорною інструкцією `LOCK CMPXCHG`.

### 3. Векторизація SIMD для масового зіставляння бітових масок
Якщо система виконує фільтрацію подій за десятками типізованих прапорців (наприклад, права доступу користувача, дозволені канали доставки, підтримувані версії функцій), послідовна перевірка окремих бітів у циклі неефективна.

Використовуючи 256-бітні векторні інструкції **AVX2** (на архітектурі x86_64) або **ARM NEON**, рушій може оцінювати бітові маски одночасно для 4 або 8 повідомлень за один такт процесора за допомогою інструкцій побітового `_mm256_and_si256` та перевірки нульового результату `_mm256_testz_si256`. Це дозволяє масштабувати фільтрацію заголовків до десятків мільйонів подій на секунду на одному фізичному сервері.

### 4. Інтеграція в мережевий цикл обробки (Event Loop Integration)
У реальних проксі-серверах (на зразок Envoy або розширень NGINX) рушій фільтрації інтегрується безпосередньо в неблокуючий цикл подій (`epoll` у Linux або `kqueue` у FreeBSD/macOS). Під час отримання батчу з сокета через `recvmmsg()` фільтр викликається для кожного кадру ще до того, як кадр буде передано у внутрішній буфер черги споживача. Це дозволяє здійснювати раннє відсікання (*Early Drop*) на рівні мережевого стека, захищаючи пам'ять прикладного застосунку від будь-якого впливу стороннього трафіку.

### 5. Метрики та телеметрія для Prometheus
У промисловій експлуатації стан конвеєра фільтрації має безперервно експортуватися в систему моніторингу. Основні лічильники включають:
* `messages_evaluated_total`: загальна кількість подій, що надійшли на вхід фільтра.
* `messages_passed_total`: кількість подій, що успішно подолали всі стадії фільтрації.
* `messages_dropped_total`: кількість відкинутих подій (із розбивкою за мітками `reason="predicate_mismatch"` або `reason="error"`).
* `filter_evaluation_latency_nanoseconds`: гістограма розподілу тривалості обчислення предикатів.

Моніторинг співвідношення `passed / total` дозволяє черговим інженерам негайно помітити аномалії: якщо коефіцієнт пропуску раптово падає до нуля або зростає до 100%, це свідчить про помилку в оновленій конфігурації фільтра або зміну формату заголовків на стороні продюсерів.
