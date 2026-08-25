# 📋 Інтерфейс та специфікація оракульної системи

Специфікація програмного контракту оракульного середовища: структури даних, сигнатури функцій, коди помилок, протокол реєстрації запитів та середовище виконання для абстрактних моделей обчислюваності.

---

## 1. Загальний огляд та архітектура контракту

Програмна специфікація оракульної системи призначена для забезпечення стандартизованого інтерфейсу взаємодії між виконавчими рушіями машин Тюринга та зовнішніми провайдерами знань (оракулами). У теоретичній інженерії обчислюваності створення чіткої межі розділення між алгоритмом та оракулом дозволяє тестувати різні математичні предмети (від скінченних таблиць до складних моделей формальної верифікації) без зміни внутрішнього коду машини.

Специфікація розроблена з урахуванням двох рівнів абстракції:
1. **Низькорівневий C ABI контракт**: Гарантує двосторонню сумісність на рівні бінарного коду, не залежить від конкретного компілятора і забезпечує просте інтегрування з мовами низького рівня.
2. **Високорівневий C++20 контракт**: Застосовує новітні засоби мови (компіляційні концепти, семантику переміщення, обгортки `std::expected` та смарт-вказівники) для забезпечення максимальної швидкодії та захисту від помилок управління пам'яттю.

Архітектура контракту гарантує дотримання принципу найменших привілеїв: рушій виконання має доступ до оракула виключно через метод зчитування (англ. *read-only query*), що унеможливлює випадкову модифікацію внутрішнього стану оракула під час обчислення.

---

## 2. Специфікація C ABI та C++20 контракту

С-інтерфейс визначає базові структури даних, коди повернення та функціональні вказівники для взаємодії з оракульними модулями, а C++20 контракт надає безпечні обгортки з `enum class` та смарт-вказівниками.

### 2.1 Коди помилок та типи оракулів

Для обробки виняткових ситуацій усі функції C ABI повертають цілочисельний статус типу `otm_status_t`. Значення `0` відповідає успішному виконанню, а від'ємні значення вказують на конкретні системні або логічні збої.

:::tabs
```c
typedef enum {
    OTM_SUCCESS              =  0,
    OTM_ERR_NULL_POINTER     = -1,
    OTM_ERR_OUT_OF_MEMORY    = -2,
    OTM_ERR_ORACLE_TIMEOUT   = -3,
    OTM_ERR_BOUNDS_EXCEEDED  = -4,
    OTM_ERR_INVALID_MACHINE  = -5
} otm_status_t;

typedef enum {
    ORACLE_TYPE_FINITE_SET,
    ORACLE_TYPE_COMPUTABLE_PREDICATE,
    ORACLE_TYPE_HALTING_ORACLE,
    ORACLE_TYPE_CUSTOM_CALLBACK
} oracle_type_t;
```
```cpp
enum class Status : int32_t {
    Success            =  0,
    ErrNullPointer     = -1,
    ErrOutOfMemory     = -2,
    ErrOracleTimeout   = -3,
    ErrBoundsExceeded  = -4,
    ErrInvalidMachine  = -5
};

enum class OracleType {
    FiniteSet,
    ComputablePredicate,
    HaltingOracle,
    CustomCallback
};
```
:::

Перелічення `oracle_type_t` (або `OracleType` у C++) визначає категорію провайдера:
- `ORACLE_TYPE_FINITE_SET`: Скінченна підмножина натуральних чисел, збережена у пам'яті у вигляді хеш-таблиці або бітового масиву. Припускає миттєву відповідь за час `O(1)`.
- `ORACLE_TYPE_COMPUTABLE_PREDICATE`: Детермінована функція-предикат, яка обчислює відповідь за фіксований алгоритм.
- `ORACLE_TYPE_HALTING_ORACLE`: Емуляція проблеми зупинки для заданого рівня ієрархії.
- `ORACLE_TYPE_CUSTOM_CALLBACK`: Зовнішня функція зворотного виклику (англ. *callback*), надана користувачем.

### 2.2 Структури реєстрації запитів та провайдера

Для протоколювання кожного звернення до оракула та подальшого обчислення функції використання `u(x)` застосовуються структури запиту та траси.

:::tabs
```c
/* Структура для запису одного оракульного запиту */
typedef struct {
    uint64_t query_value;    /* Число, надіслане оракулу */
    bool answer;             /* Відповідь: true (1) / false (0) */
    uint64_t step_timestamp; /* Крок обчислення, на якому зроблено запит */
} otm_query_entry_t;

/* Протокол журналювання запитів */
typedef struct {
    otm_query_entry_t *entries;
    size_t count;
    size_t capacity;
    uint64_t max_queried_value; /* Значення u(x) - 1 */
} otm_query_trace_t;

/* Структура Провайдера Оракула */
typedef struct oracle_provider {
    oracle_type_t type;
    void *user_data;
    bool (*query_func)(struct oracle_provider *self, uint64_t val, otm_status_t *err);
    void (*free_func)(struct oracle_provider *self);
} oracle_provider_t;
```
```cpp
struct QueryEntry {
    uint64_t query_value;
    bool answer;
    uint64_t step_timestamp;
};

struct QueryTrace {
    std::vector<QueryEntry> entries;
    uint64_t max_queried_value{0};

    [[nodiscard]] uint64_t get_use_bound() const noexcept {
        return entries.empty() ? 0 : max_queried_value + 1;
    }
};

class IOracleProvider {
public:
    virtual ~IOracleProvider() = default;
    [[nodiscard]] virtual bool contains(uint64_t value) const = 0;
    [[nodiscard]] virtual std::string_view get_type_name() const noexcept = 0;
};
```
:::

Описовий розбір полів структури `oracle_provider_t`:
- `type`: Визначає тип оракула з перелічення `oracle_type_t`.
- `user_data`: Вказівник на довільні користувацькі дані (наприклад, внутрішній масив або таблицю станів).
- `query_func`: Вказівник на функцію, яка приймає значення `val` і повертає булеву відповідь. Помилки виконання записуються у змінну `err`.
- `free_func`: Вказівник на функцію деструктора для очищення ресурсів `user_data`.

Політика управління пам'яттю C ABI гарантує, що модуль, який виділив об'єкт `oracle_provider_t`, відповідає за його звільнення через виклики `free_func` та `otm_oracle_destroy`. Траса `otm_query_trace_t` ініціалізується викликачем та автоматично розширюється за допомогою `realloc()` у разі вичерпання ємності `capacity`.

### 2.3 Сигнатури та опис функцій API

Нижче наведено основні функції управління оракульним середовищем.

:::tabs
```c
/**
 * @brief Створює новий екземпляр провайдера оракула на основі скінченного масиву.
 */
otm_status_t otm_oracle_create_finite(
    const uint64_t *elements,
    size_t count,
    oracle_provider_t **out_provider
);

/**
 * @brief Здійснює запит до оракула з автоматичним протоколюванням.
 */
otm_status_t otm_oracle_query(
    oracle_provider_t *provider,
    uint64_t query_val,
    otm_query_trace_t *trace,
    bool *out_answer
);

/**
 * @brief Обчислює точне значення функції використання u(x) за трасою.
 */
uint64_t otm_trace_get_use_bound(const otm_query_trace_t *trace);

/**
 * @brief Звільняє ресурси оракула.
 */
void otm_oracle_destroy(oracle_provider_t *provider);
```
```cpp
namespace otm {

class OracleFactory {
public:
    [[nodiscard]] static std::expected<std::shared_ptr<IOracleProvider>, Status>
    create_finite(std::span<const uint64_t> elements);
};

class OracleEngine {
public:
    [[nodiscard]] std::expected<bool, Status>
    query(IOracleProvider& provider, uint64_t query_val, QueryTrace& trace);
};

} // namespace otm
```
:::

**Механізм роботи `otm_oracle_query`**:
1. Функція здійснює вхідну перевірку аргументів: якщо `provider`, `trace` або `out_answer` дорівнюють `NULL`, повертається код `OTM_ERR_NULL_POINTER`.
2. Викликається внутрішній функціональний вказівник `provider->query_func(provider, query_val, &status)`.
3. Отримана булева відповідь фіксується в масиві `trace->entries`. Якщо розширити масив не вдається через брак пам'яті, повертається код `OTM_ERR_OUT_OF_MEMORY`.
4. Якщо значення `query_val` перевищує поточне `trace->max_queried_value`, це значення оновлюється: `trace->max_queried_value = query_val`.
5. Повертається статус `OTM_SUCCESS`.

---

## 3. Специфікація C++20 об'єктно-орієнтованого контракту

C++20 інтерфейс забезпечує строго типізований контракт на основі концептів (англ. *concepts*), шаблонів та смарт-вказівників.

```cpp
namespace otm {

template <typename T>
concept OracleProviderConcept = requires(T a, uint64_t val) {
    { a.contains(val) } -> std::same_as<bool>;
    { a.get_type_name() } -> std::convertible_to<std::string_view>;
};

struct ExecutionMetrics {
    uint64_t total_steps{0};
    uint64_t oracle_queries_count{0};
    uint64_t max_restraint_use{0};
    bool halted{false};
};

class MemoryBoundOracle final : public IOracleProvider {
private:
    std::vector<uint64_t> sorted_elements_;

public:
    explicit MemoryBoundOracle(std::vector<uint64_t> elements);
    [[nodiscard]] bool contains(uint64_t value) const override;
    [[nodiscard]] std::string_view get_type_name() const noexcept override {
        return "MemoryBoundOracle";
    }
};

class ExecutionEngine {
private:
    std::shared_ptr<IOracleProvider> oracle_;
    ExecutionMetrics metrics_;

public:
    explicit ExecutionEngine(std::shared_ptr<IOracleProvider> oracle)
        : oracle_(std::move(oracle)) {}

    [[nodiscard]] std::expected<ExecutionMetrics, otm_status_t>
    execute_machine(uint64_t machine_index, uint64_t input_x, uint64_t max_steps);
};

} // namespace otm
```

**Опис класів C++20**:
- `OracleProviderConcept`: Гарантує, що будь-який шаблонний клас, переданий у рушій виконання, реалізує метод `contains(uint64_t)` із поверненням `bool` та метод `get_type_name()`. Це виключає помилки компіляції при підключенні сторонніх оракулів.
- `IOracleProvider`: Абстрактний базовий клас для динамічного поліморфізму, коли тип оракула визначається під час виконання (англ. *runtime*).
- `MemoryBoundOracle`: Конкретна реалізація оракула на основі впорядкованого вектора `std::vector<uint64_t>`, що використовує бінарний пошук `std::binary_search` за час `O(log N)`.
- `ExecutionEngine`: Головний клас-інтерпретатор. Метод `execute_machine()` повертає об'єкт `std::expected<ExecutionMetrics, otm_status_t>`, що дозволяє обробляти помилки без використання винятків (англ. *zero-cost exception handling*).

---

## 4. Схема станів та таблиця відповідей

### 4.1 Специфікація станів виконання оракульної машини

Під час виконання програми управляючий автомат переходить між такими основними станами:

```
 [INIT] ──> [FETCH_INSTR] ──> [IS_QUERY_STATE?] ──ТАК──> [QUERY_ORACLE] ──> [LOG_TRACE]
                 ▲                  │                                           │
                 │                 НІ                                           │
                 │                  ▼                                           ▼
                 └───────── [EXECUTE_LOCAL] <───────────────────────────────────┘
                                    │
                              [HALT_STATE?] ──ТАК──> [TERMINATE_SUCCESS]
```

Опис переходів станів:
1. `INIT`: Ініціалізація стрічок, зсув голівки на початкову позицію.
2. `FETCH_INSTR`: Зчитування наступної інструкції з таблиці переходів.
3. `QUERY_ORACLE`: Машина записала значення `x` на стрічку запиту і перейшла в стан `q_query`. Оракул обчислює `χ_B(x)`.
4. `LOG_TRACE`: Запис результату у трасу, оновлення лічильника кроків та значення `u(x)`.
5. `TERMINATE_SUCCESS`: Досягнуто стану зупинки `q_halt`. Повернення метрик виконання.

### 4.2 Таблиця повернення кодів помилок та поведінки

| Код помилки | Назва константи | Причина виникнення | Рекомендована дія |
| :--- | :--- | :--- | :--- |
| `0` | `OTM_SUCCESS` | Операція виконана без помилок | Продовжити виконання |
| `-1` | `OTM_ERR_NULL_POINTER` | Передано `NULL` вказівник на оракул або трасу | Перевірити ініціалізацію об'єктів |
| `-2` | `OTM_ERR_OUT_OF_MEMORY` | Не вдалося виділити пам'ять під трасу `query_trace_t` | Звільнити пам'ять або зменшити ліміт |
| `-3` | `OTM_ERR_ORACLE_TIMEOUT` | Оракул-предикат вийшов за допустимий час обчислення | Перервати виконання або збільшити таймаут |
| `-4` | `OTM_ERR_BOUNDS_EXCEEDED` | Номер елемента запиту перевищує `UINT64_MAX` | Перевірити коректність запиту |
| `-5` | `OTM_ERR_INVALID_MACHINE` | Некоректний код інструкцій машини Тюринга | Перевірити таблицю переходів |

**Деталізація розв'язання помилок**:
- При виникненні `OTM_ERR_NULL_POINTER` викликувач має перевірити, чи був повернутий не-null вказівник після `otm_oracle_create_finite()`.
- При виникненні `OTM_ERR_ORACLE_TIMEOUT` виконавчий рушій перериває крок обчислення та реєструє неповний статус виконання у трасі.
- При виникненні `OTM_ERR_BOUNDS_EXCEEDED` машина гарантовано призупиняє запис на стрічку запиту, запобігаючи переповненню цілочисельного діапазону `uint64_t`.

---

## 5. Гарантії безпеки та інваріанти виконання

Під час розробки оракульних систем гарантуються такі фундаментальні інваріанти:

1. **Інваріант монотонності використання**: Траса запитів `otm_query_trace_t` гарантує, що значення `max_queried_value` монотонно не спадає при додаванні нових запитів: `max_queried_value_{s+1} = max(max_queried_value_s, query_val)`.
2. **Детермінізм відповіді (Функціональність)**: Оракул є детермінованою функцією. Для одного й того самого `query_val` значення відповіді `answer` є константним протягом усього обчислення.
3. **Обмеженість пам'яті (RAII)**: Створення об'єкта `IOracleProvider` у C++ гарантує автоматичне звільнення внутрішніх таблиць при виході об'єкта з області видимості.
4. **Потокобезпечність (Thread-Safety)**: Константні методи `contains()` є безпечними для паралельного виклику з багатьох потоків виконання, оскільки вони не модифікують внутрішній стан оракула (англ. *read-only access*).
