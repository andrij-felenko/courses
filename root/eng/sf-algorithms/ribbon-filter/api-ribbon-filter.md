# 📋 Програмний інтерфейс та параметри стрічкового фільтра

Стрічковий фільтр (Ribbon Filter) надає компактний, детермінований інтерфейс для побудови, серіалізації та надшвидкої перевірки належності ключів у незмінних наборах даних. Документація нижче описує специфікацію публічного API бібліотеки стрічкового фільтра, структурні типи даних, коди повернення, двійковий формат збереження, діагностичні лічильники та параметри інтеграції у високонавантажені сховища даних на прикладі `RibbonFilterPolicy` у RocksDB.

## 1. Архітектурний контракт та інваріанти

Стрічковий фільтр реалізує контракт статичного фільтра відбитків (Static Approximate Membership Query, AMQ):
* **Незмінність (Immutability)**: після завершення фази побудови (Build) масив слотів переходить у стан «тільки для читання». Додавання або видалення окремих ключів без повної перебудови системи заборонено.
* **Відсутність хибнонегативних відповідей (Zero False Negatives)**: якщо ключ `K` було передано під час конструювання, функція перевірки належності гарантовано повертає `true`.
* **Контрольована ймовірність хибнопозитивних відповідей**: для будь-якого ключа `Q`, відсутнього у множині, ймовірність повернення `true` становить строго `2^(-r)`, де `r` — довжина відбитка в бітах.
* **Безпека потоків (Thread Safety)**: операції запиту `contains` є чистими функціями без побічних ефектів і можуть виконуватися паралельно з довільної кількості потоків без блокувань (Lock-Free Read Path).
* **Локальність доступу**: перевірка ключа вимагає зчитування лише одного неперервного діапазону з `w` слотів, що усуває множинні промахи кешу процесора.

## 2. Структури конфігурації та типи даних

### 2.1 Перелік статусів та кодів помилок `RibbonStatus`

Кожна операція конструювання, валідації та серіалізації повертає типізований статус виконання:

:::tabs
```c
#include <stdint.h>

typedef enum {
    RIBBON_OK                      =  0,  /* Успішне завершення операції */
    RIBBON_ERR_INVALID_ARGUMENT    = -1,  /* Некоректні параметри (нульовий вказівник, M < w) */
    RIBBON_ERR_UNRESOLVABLE_SYSTEM = -2,  /* Не вдалося розв'язати систему за ліміт спроб */
    RIBBON_ERR_OUT_OF_MEMORY       = -3,  /* Помилка виділення динамічної пам'яті */
    RIBBON_ERR_BUFFER_TOO_SMALL    = -4,  /* Буфер призначення замалий для серіалізації */
    RIBBON_ERR_CORRUPTED_DATA      = -5,  /* Пошкоджено магічне число або контрольну суму */
    RIBBON_ERR_UNSUPPORTED_VERSION = -6   /* Непідтримувана версія двійкового формату */
} RibbonStatus;
```
```cpp
#include <cstdint>

namespace ribbon {

enum class Status : std::int32_t {
    Ok                     =  0,  // Успішне завершення операції
    InvalidArgument        = -1,  // Некоректні вхідні аргументи
    UnresolvableSystem     = -2,  // Не вдалося розв'язати систему лінійних рівнянь
    OutOfMemory            = -3,  // Недостатньо оперативної пам'яті
    BufferTooSmall         = -4,  // Наданий буфер замалий для серіалізації
    CorruptedData          = -5,  // Пошкодження магічного числа або заголовка
    UnsupportedVersion     = -6   // Непідтримувана версія формату
};

} // namespace ribbon
```
:::

Кожен код помилки однозначно діагностує стан виконання:
* `RIBBON_OK`: операція завершилася успішно, результати валідні.
* `RIBBON_ERR_INVALID_ARGUMENT`: передано нульовий вказівник або кількість ключів дорівнює нулю.
* `RIBBON_ERR_UNRESOLVABLE_SYSTEM`: лінійна система виявилася несумісною за всі спроби зміни seed. Вимагає збільшення коефіцієнта надлишковості `overhead_percent`.
* `RIBBON_ERR_OUT_OF_MEMORY`: системний алокатор пам'яті повернув помилку при спробі виділення слотів.
* `RIBBON_ERR_BUFFER_TOO_SMALL`: вихідний масив байтів для серіалізації має розмір, менший за обчислений обсяг фільтра.
* `RIBBON_ERR_CORRUPTED_DATA`: бінарний образ містить недійсне магічне число `0x52494246` ("RIBF").
* `RIBBON_ERR_UNSUPPORTED_VERSION`: спроба відкрити структуру з версією формату, що перевищує поточну підтримувану бібліотекою.

### 2.2 Структура параметрів конструювання `RibbonOptions`

Конфігурація визначає точний баланс між обсягом пам'яті, швидкістю побудови та продуктивністю запитів:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint16_t width;                   /* Ширина вікна стрічки: 32, 64 або 128 бітів */
    uint8_t fingerprint_bits;         /* Довжина відбитка r у бітах: від 4 до 16 */
    uint8_t overhead_percent;         /* Коефіцієнт надлишковості слотів у відсотках */
    uint16_t max_retries;             /* Максимальна кількість спроб із новим seed */
    uint64_t initial_seed;            /* Початковий seed хешування */
    bool use_homogeneous_scaling;     /* Однорідне масштабування проти крайових ефектів */
    bool use_interleaved_layout;      /* Чергування слотів для кеш-ліній CPU */
} RibbonOptions;

void ribbon_options_init_default(RibbonOptions *opts);
```
```cpp
#include <cstdint>
#include <cstddef>

namespace ribbon {

struct Options {
    std::uint16_t width{64};                    // Ширина ковзного вікна стрічки (32, 64, 128)
    std::uint8_t fingerprint_bits{8};           // Кількість бітів відбитка r (4..16)
    std::uint8_t overhead_percent{5};           // Надлишковість слотів у відсотках (2..15%)
    std::uint16_t max_retries{10};              // Максимальна кількість спроб розв'язання
    std::uint64_t initial_seed{0x9e3779b97f4a7c15ULL}; // Початковий seed
    bool use_homogeneous_scaling{true};         // Усунення крайових ефектів
    bool use_interleaved_layout{false};         // Оптимізація кеш-ліній (Interleaved)
};

} // namespace ribbon
```
:::

Параметри конфігурації керують внутрішніми компромісами структури:
* `width`: ширина ковзного вікна матриці над полем `GF(2)`. Значення 64 є оптимальним для 64-бітних архітектур x86-64 та ARM64, оскільки дозволяє виконувати всі операції над стрічкою через поодинокі 64-бітні регістрові команди. При виборі `width = 32` побудова дещо прискорюється на застарілих 32-бітних процесорах, але вимагає збільшення оверхеду пам'яті до 12–15%. При `width = 128` оверхед знижується до 1%, але вимагає 128-бітних інструкцій.
* `fingerprint_bits`: довжина цільового відбитка `r`. Визначає ймовірність хибнопозитивної відповіді `FPR = 2^(-r)`. Для `r = 8` помилка становить `1/256 ≈ 0.39%`, для `r = 7` — `1/128 ≈ 0.78%`, для `r = 12` — `1/4096 ≈ 0.024%`.
* `overhead_percent`: надлишок кількості слотів `M` над кількістю ключів `N`. При `width = 64` значення 4–5% гарантує успішне розв'язання системи з першої спроби у понад 98% випадків.
* `use_homogeneous_scaling`: вмикає алгоритм неперервного відображення початкових зміщень, що розвантажує граничні комірки та знижує критичний поріг розв'язності.
* `use_interleaved_layout`: вмикає блочне чергування бітових площин, що пакує всі дані відбитка у межі однієї 64-байтної кеш-лінії процесора.

## 3. Інтерфейс побудови фільтра (Builder Interface)

### 3.1 Функція конструювання за числовими ключами

Створює розв'язаний стрічковий фільтр за наданим масивом 64-бітних цілих ключів:

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

typedef struct RibbonFilter RibbonFilter;

RibbonStatus ribbon_build(const RibbonOptions *opts,
                          const uint64_t *keys,
                          size_t num_keys,
                          RibbonFilter **out_filter);
```
```cpp
#include <span>
#include <cstdint>
#include <optional>
#include <memory>

namespace ribbon {

class Filter;

class Builder {
public:
    static std::optional<Filter> Build(std::span<const std::uint64_t> keys,
                                       const Options& options = {});
};

} // namespace ribbon
```
:::

#### Опис параметрів та поведінки:
* `opts`: вказівник на налаштування. Якщо передано `NULL`, автоматично застосовуються параметри за замовчуванням (`width = 64`, `fingerprint = 8`, `overhead = 5%`).
* `keys`: неперервний буфер вхідних ключів. Порядок елементів не має значення.
* `num_keys`: загальна кількість ключів (повинна бути `≥ 1`).
* `out_filter`: подвійний вказівник для повернення адреси створеного фільтра.

Функція виконує однопрохідне інкрементне виключення Гаусса над масивом опорних рядків `pivots`. У разі виникнення лінійної несумісності `0 = target` генератор змінює `seed` і повторює спробу до досягнення ліміту `max_retries`. При успішному завершенні виконується зворотна підстановка (Back-substitution), тимчасовий масив `pivots` вивільняється, а результуючий компактний масив `slots` закріплюється у пам'яті.

Пам'ять під масив `slots` виділяється з вирівнюванням за межею 64 байтів (розмір типової кеш-лінії сучасних процесорів x86-64 та ARM Cortex), що усуває міжлінійні розриви пам'яті під час швидкого читання.

### 3.2 Функція конструювання за байтовими рядками

Дозволяє створювати фільтр для ключів довільної довжини (наприклад, рядкових ідентифікаторів `std::string_view` або бінарних ключів записів бази даних):

:::tabs
```c
#include <stddef.h>

typedef struct {
    const void *data;
    size_t length;
} RibbonSlice;

RibbonStatus ribbon_build_bytes(const RibbonOptions *opts,
                                const RibbonSlice *slices,
                                size_t num_slices,
                                RibbonFilter **out_filter);
```
```cpp
#include <span>
#include <string_view>
#include <optional>

namespace ribbon {

class Filter;

class StringFilterBuilder {
public:
    static std::optional<Filter> Build(std::span<const std::string_view> keys,
                                       const Options& options = {});
};

} // namespace ribbon
```
:::

Кожен слайс транслюється у 64-бітне значення за допомогою швидкого некриптографічного алгоритму XXH3, після чого передається в ядро лінійного розв'язувача. Якщо два вхідні слайси містять ідентичний вміст, алгоритм автоматично пропускає повторні лінійні рівняння без збою побудови.

### 3.3 Звільнення пам'яті

Звільняє виділені ресурси та дескриптор фільтра:

:::tabs
```c
void ribbon_destroy(RibbonFilter *filter);
```
```cpp
namespace ribbon {

// У C++ вивільнення пам'яті відбувається автоматично в деструкторі ~Filter() за ідіомою RAII
class Filter {
public:
    ~Filter() noexcept = default;
};

} // namespace ribbon
```
:::

## 4. Інтерфейс перевірки запитів (Query Interface)

### 4.1 Одиночний точковий запит `contains`

Перевіряє ймовірну наявність ключа у множині:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

bool ribbon_contains(const RibbonFilter *filter, uint64_t key);
```
```cpp
#include <cstdint>
#include <string_view>

namespace ribbon {

class Filter {
public:
    [[nodiscard]] bool Contains(std::uint64_t key) const noexcept;
    [[nodiscard]] bool Contains(std::string_view key) const noexcept;
};

} // namespace ribbon
```
:::

#### Властивості та інваріанти:
* Функція гарантовано повертає `true`, якщо ключ входив до початкового набору `S`.
* Для стороннього ключа повертає `false` із ймовірністю `1 - 2^(-r)`.
* Час виконання є строго детермінованим `O(1)` (близько 15–20 наносекунд).
* Відсутні блокування та виділення динамічної пам'яті, що забезпечує лінійну масштабованість при паралельному читанні з багатьох потоків.

### 4.2 Пакетний векторизований запит `contains_batch`

Виконує групову перевірку масиву ключів із використанням попереднього завантаження кешу:

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void ribbon_contains_batch(const RibbonFilter *filter,
                           const uint64_t *keys,
                           size_t count,
                           bool *out_results);
```
```cpp
#include <span>
#include <cstdint>
#include <vector>

namespace ribbon {

class Filter {
public:
    void ContainsBatch(std::span<const std::uint64_t> keys,
                       std::span<bool> out_results) const noexcept;
};

} // namespace ribbon
```
:::

Пакетна функція організує конвеєрне зчитування: під час обчислення скалярного добутку для поточного ключа процесор виконує попереднє кешування пам'яті для наступного ключа через інструкцію `_mm_prefetch`, що усуває затримки доступу до оперативної пам'яті.

## 5. Серіалізація та дискове збереження

Бібліотека підтримує двійкове збереження зі строгим вирівнюванням та десеріалізацію без копіювання:

:::tabs
```c
#include <stddef.h>

RibbonStatus ribbon_serialize(const RibbonFilter *filter,
                              void *buffer,
                              size_t buffer_size,
                              size_t *out_written_bytes);

RibbonStatus ribbon_open_zerocopy(const void *mapped_buffer,
                                  size_t buffer_size,
                                  RibbonFilter *out_filter);
```
```cpp
#include <span>
#include <cstdint>
#include <vector>
#include <optional>

namespace ribbon {

class Filter {
public:
    [[nodiscard]] std::vector<std::uint8_t> Serialize() const;
    static std::optional<Filter> OpenZeroCopy(std::span<const std::uint8_t> mapped_bytes);
};

} // namespace ribbon
```
:::

### Специфікація двійкового заголовка:
* Байти 0..3: магічне число `0x52494246` ("RIBF").
* Байти 4..5: версія формату (`0x0001`).
* Байти 6..7: ширина стрічки `w` (`uint16_t`).
* Байт 8: кількість бітів відбитка `r` (`uint8_t`).
* Байт 9: прапорці розміщення (0x01 = Homogeneous, 0x02 = Interleaved).
* Байти 10..11: вирівнювальне заповнення (0x0000).
* Байти 12..19: кількість ключів `N` (`uint64_t`).
* Байти 20..27: кількість слотів `M` (`uint64_t`).
* Байти 28..35: генераторний `seed` (`uint64_t`).
* Байти 36..36+M: корисне навантаження слотів `B[0..M-1]`.

Функція `OpenZeroCopy` перевіряє сигнатуру заголовка та налаштовує внутрішній вказівник безпосередньо на байти пам'яті в сторінковому кеші ОС, що усуває накладні витрати на виділення пам'яті під час відкриття файлів SSTable.

## 6. Діагностика, телеметрія та лічильники `RibbonStats`

Для моніторингу та профілювання роботи фільтра у продуктивних кластерах надається структура діагностики:

:::tabs
```c
#include <stddef.h>
#include <stdint.h>

typedef struct {
    size_t num_keys;              /* Кількість вхідних ключів */
    size_t num_slots;             /* Загальна кількість слотів */
    size_t memory_bytes;          /* Фактичний обсяг виділеної пам'яті */
    double bits_per_key;          /* Питома кількість бітів на один ключ */
    double theoretical_fpr;       /* Теоретична ймовірність помилки 2^(-r) */
    uint32_t retries_count;       /* Кількість спроб побудови зі зміною seed */
    double build_time_ms;         /* Час побудови у мілісекундах */
} RibbonStats;

RibbonStatus ribbon_get_stats(const RibbonFilter *filter, RibbonStats *out_stats);
```
```cpp
#include <cstddef>
#include <cstdint>

namespace ribbon {

struct Stats {
    std::size_t num_keys{0};
    std::size_t num_slots{0};
    std::size_t memory_bytes{0};
    double bits_per_key{0.0};
    double theoretical_fpr{0.0};
    std::uint32_t retries_count{0};
    double build_time_ms{0.0};
};

} // namespace ribbon
```
:::

Діагностичні лічильники дозволяють інтегрувати метрики фільтра в системи телеметрії (Prometheus, OpenTelemetry, Grafana):
* `retries_count`: кількість спроб розв'язання системи. Якщо цей показник у середньому перевищує 1.2, це сигнал про необхідність збільшити `overhead_percent`.
* `build_time_ms`: час генерації фільтра. Дозволяє виявити затримки під час фази компактифікації у фонових потоках бази даних.
* `bits_per_key`: реальне споживання пам'яті на один збережений ключ.

## 7. Інтеграція у RocksDB: `RibbonFilterPolicy`

У системі зберігання RocksDB стрічковий фільтр є повноцінною заміною класичним фільтрам Блума і налаштовується через фабрику політик фільтрування `FilterPolicy`.

### Сигнатура фабричного виклику RocksDB C++ API

:::tabs
```c
/* RocksDB C-wrapper API declaration */
typedef struct rocksdb_filterpolicy_t rocksdb_filterpolicy_t;

rocksdb_filterpolicy_t* rocksdb_filterpolicy_create_ribbon(double bloom_equivalent_bits_per_key,
                                                           int bloom_before_level);
```
```cpp
#include "rocksdb/filter_policy.h"
#include <memory>

namespace ROCKSDB_NAMESPACE {

// Створення політики Ribbon Filter для RocksDB
std::shared_ptr<const FilterPolicy> NewRibbonFilterPolicy(
    double bloom_equivalent_bits_per_key,
    int bloom_before_level = 0);

} // namespace ROCKSDB_NAMESPACE
```
:::

### Опис конфігураційних параметрів:
* `bloom_equivalent_bits_per_key`: цільова якість фільтрації у термінах класичного фільтра Блума. Значення `10.0` відповідає ймовірності помилки ~1%, при цьому стрічковий фільтр займає лише ~7.0 бітів на ключ замість 10 бітів (економія 30% RAM/SSD).
* `bloom_before_level`: поріг перемикання рівнів LSM-дерева. Для рівнів менше за вказаний (наприклад, L0–L1) застосовується класичний фільтр Блума через високу частоту скидань із пам'яті (MemTable Flush). Для рівнів `≥ bloom_before_level` (L2–L6), де зберігається понад 95% даних, автоматично активується Ribbon Filter.

### Повний приклад налаштування RocksDB

:::tabs
```c
#include "rocksdb/c.h"

rocksdb_options_t* setup_c_rocksdb_ribbon() {
    rocksdb_options_t *opt = rocksdb_options_create();
    rocksdb_options_set_create_if_missing(opt, 1);
    
    rocksdb_block_based_table_options_t *table_opt = rocksdb_block_based_options_create();
    rocksdb_filterpolicy_t *ribbon = rocksdb_filterpolicy_create_ribbon(10.0, 2);
    rocksdb_block_based_options_set_filter_policy(table_opt, ribbon);
    rocksdb_block_based_options_set_format_version(table_opt, 5);
    
    rocksdb_options_set_block_based_table_factory(opt, table_opt);
    return opt;
}
```
```cpp
#include <rocksdb/db.h>
#include <rocksdb/options.h>
#include <rocksdb/table.h>
#include <rocksdb/filter_policy.h>

rocksdb::Options setup_rocksdb_ribbon() {
    rocksdb::Options options;
    options.create_if_missing = true;

    rocksdb::BlockBasedTableOptions table_options;
    table_options.filter_policy.reset(
        rocksdb::NewRibbonFilterPolicy(10.0, /*bloom_before_level=*/2)
    );
    table_options.cache_index_and_filter_blocks = true;
    table_options.pin_l0_filter_and_index_blocks_in_cache = true;
    table_options.format_version = 5;

    options.table_factory.reset(
        rocksdb::NewBlockBasedTableFactory(table_options)
    );
    options.max_background_jobs = 8;
    return options;
}
```
:::

## 8. Зведена таблиця налаштувань та інженерних компромісів

| Конфігурація | Сфера застосування | Пам'ять (біт/ключ) | Оверхед над Шенноном | Швидкість побудови |
| :--- | :--- | :--- | :--- | :--- |
| `w=32, r=7` | 32-бітні embedded системи, кеш L1 | 7.91 біт | +13.0% | 5.1 млн ключів/с |
| `w=64, r=7` | **Стандарт для RocksDB L2+ (FPR ~ 0.78%)** | **7.28 біт** | **+4.0%** | **4.2 млн ключів/с** |
| `w=64, r=8` | **Стандартне сховище (FPR ~ 0.39%)** | **8.32 біт** | **+4.0%** | **4.2 млн ключів/с** |
| `w=128, r=8` | Екстремальна економія RAM (FPR ~ 0.39%) | 8.08 біт | +1.0% | 2.1 млн ключів/с |
| `w=64, r=12` | Високоточна аналітика (FPR ~ 0.024%) | 12.48 біт | +4.0% | 4.0 млн ключів/с |

## 9. Гарантії безпеки пам'яті та коректності багатопотокового доступу

Бібліотека стрічкового фільтра розроблялася з урахуванням суворих вимог до надійності промислового коду системного рівня:

### 1. Безпека одночасного доступу (Thread Safety & Concurrency)
* **Стан незмінності (Immutability)**: після завершення побудови екземпляр `RibbonFilter` є повністю незмінним. Усі поля структури та дані масиву `slots` отримують статус «тільки для читання».
* **Паралельні запити**: довільна кількість читацьких потоків може одночасно викликати функцію `ribbon_contains` для одного екземпляра фільтра без використання м'ютексів, спінлоків чи атомарних операцій (Lock-Free Read Operations).
* **Спільне використання через `mmap`**: кілька незалежних процесів операційної системи можуть одночасно відображати один і той самий файл фільтра за допомогою `ribbon_open_zerocopy`, поділяючи фізичні сторінки оперативної пам'яті без ризику виникнення стану перегонів (Data Races).

### 2. Захист від невизначеної поведінки (Undefined Behavior & Sanitizers)
* **Перевірка адресним санітайзером (AddressSanitizer / ASan)**: усі звернення до масиву слотів захищені математичним обмеженням діапазону `[start_pos, start_pos + width - 1]`. При конструюванні фільтра виділяється додатковий вирівнювальний хвіст (padding) розміром `width` байтів, що повністю унеможливлює вихід за межі виділеної пам'яті (Out-of-Bounds Read/Write) навіть під час векторизованих 64-бітних зчитувань на правому краю.
* **Санітайзер невизначеної поведінки (UBSan)**: операції побітових зсувів `mask >>= offset` суворо контролюються перевіркою `offset < 64`. Якщо маска повністю обнуляється, цикл завершується негайно, запобігаючи виконанню зсуву на 64 або більше бітів, що є невизначеною поведінкою у стандартах C11 та C++20.
* **Санітайзер пам'яті (MemorySanitizer / MSan)**: порожні комірки слотів під час зворотної підстановки явно ініціалізуються нулями (`0`), що запобігає читанню неініціалізованої пам'яті під час серіалізації або запитів.

## 10. Інтеграція з префіксними екстракторами (Prefix Extractors) у RocksDB

У багатьох прикладних сценаріях (наприклад, зберігання часових рядів, композитні первинні ключі `user_id:timestamp`) база даних виконує діапазонне сканування за префіксом (`Iterator::Seek("user_1024:")`).

### Принцип роботи префіксного фільтра
1. **Екстракція префікса**: перед додаванням запису в SSTable RocksDB витягує префікс ключа за допомогою налаштованого `SliceTransform` (наприклад, перші 8 байтів).
2. **Побудова фільтра за префіксами**: у стрічковий фільтр передаються не повні ключі, а виключно їхні префікси.
3. **Фільтрація операцій Seek**: під час виклику `Seek(target_key)` RocksDB витягує префікс шуканого ключа і перевіряє його наявність у стрічковому фільтрі. Якщо префікс відсутній, зчитування блоків даних із диска повністю скасовується.

Використання Ribbon Filter для префіксного індексування дозволяє заощадити гігабайти пам'яті у порівнянні з класичним Bloom Filter, оскільки кількість унікальних префіксів у базі даних зазвичай на порядки менша за загальну кількість ключів.

## 11. Розрахунок бюджету оперативної пам'яті для великих сховищ

Для точного планування апаратних ресурсів серверів баз даних застосовується формула розрахунку пам'яті блокового кешу:

```
RAM_Ribbon = (Total_Keys · (1 + overhead_percent / 100) · fingerprint_bits) / 8  [байтів]
```

### Порівняльний приклад для бази даних на 10 мільярдів ключів (`N = 10¹⁰`):
* **Класичний фільтр Блума** (1% помилки, 10.0 біт/ключ):
  `10 000 000 000 × 10 біт / 8 = 12.50 гігабайтів RAM`.
* **Стрічковий фільтр Ribbon Filter** (1% помилки, `w = 64`, `r = 7`, `overhead = 4%` → 7.28 біт/ключ):
  `10 000 000 000 × 7.28 біт / 8 = 9.10 гігабайтів RAM`.
* **Чиста економія пам'яті**: `12.50 - 9.10 = 3.40 гігабайти RAM` на кожному вузлі кластера.

У масштабах дата-центру з тисячами серверних вузлів перехід на Ribbon Filter вивільняє десятки терабайтів високошвидкісної пам'яті, які перенаправляються у кеш сторінок даних (Block Cache), суттєво підвищуючи загальний відсоток влучань (Cache Hit Ratio) та знижуючи середню затримку обробки запитів.

## 12. Рекомендації щодо міграції з Bloom на Ribbon

1. **Версія формату блоків**: Ribbon Filter підтримується у RocksDB починаючи з `format_version = 5`. При відкритті старіших SSTable-файлів версії 4 або нижче RocksDB автоматично виконує сумісне читання наявних фільтрів Блума, а нові таблиці під час компактифікації генерує у форматі Ribbon.
2. **Баланс CPU та пам'яті**: Перехід на стрічковий фільтр зменшує обсяг кешу індексів на 25–30%, але збільшує навантаження на процесор під час фонових компактифікацій на 5–10%. Рекомендується збільшувати `max_background_jobs` відповідно до кількості доступних ядер (наприклад, від 4 до 16 фонових воркерів).
3. **Гібридне налаштування**: Використання `bloom_before_level = 2` забезпечує оптимальний баланс: максимальну швидкість скидання MemTable на рівнях L0–L1 та максимальну економію пам'яті на рівнях L2–L6.
4. **Моніторинг промахів**: Рекомендується відстежувати лічильники `rocksdb.bloom.filter.useful` та `rocksdb.bloom.filter.full.positive` для контролю фактичної ефективності відсікання операцій дискового читання.
5. **Префіксне фільтрування**: При використанні префіксного пошуку (`prefix_extractor` у RocksDB) Ribbon Filter підтримує префіксні відбитки аналогічно до фільтрів Блума, скорочуючи операції дискового читання під час викликів `Iterator::Seek(prefix)`.
6. **Чекліст готовності до продакшну**: Перед масштабним розгортанням у промислових кластерах перевірте версію RocksDB (`>= 7.0`), виділіть достатню кількість фонових потоків для компактифікації (`max_background_jobs >= 4`) та переконайтеся у наявності апаратної підтримки інструкцій `POPCNT` та `TZCNT` на цільових серверах.
