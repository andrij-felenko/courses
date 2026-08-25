# Специфікація API фільтра Блума

<preknowlist>
  * [Фільтр Блума](topic:sf-algorithms/bloom-filter)
</preknowlist>

Цей довідник надає вичерпну специфікацію поверхні програмування (API), структур даних, алгоритмічної складності, системних викликів POSIX, інструкцій процесора та бінарних форматів серіалізації для класичних, блочних, секційованих та масштабованих фільтрів Блума.

Документ орієнтований на розробників високопродуктивних систем інфраструктурного рівня, систем збереження даних (RocksDB, Apache Cassandra, LevelDB), мережевих проксі-серверів та висунутих edge-обчислень, які вимагають строгого контролю розміщення пам'яті, локальності процесорного кешу та потокобезпеки.

## 1. Контракти структур даних та фундаментальні інваріанти

Головним алгоритмічним інваріантом фільтра Блума є сувора незмінність розміру бітового вектору `num_bits` (`m`) та кількості застосовуваних хеш-функцій `num_hashes` (`k`) протягом усього терміну існування об'єкта. Будь-яке динамічне видозмінення цих двох параметрів після додавання ключа незворотно руйнує просторову індексацію і призводить до появи хибнонегативних відповідей (False Negative), що прямо порушує базову гарантію структури даних.

Коректне розміщення бітового вектору у пам'яті вимагає дотримання побітової індексації від молодшого біта до старшого у межах кожного байта (Little-Endian Bit Ordering). Біт з індексом `idx` розташовується в байті `idx / 8` на позиції `idx % 8`. Такий прямий порядок спрощує векторизовані операції маскування та прискорює сумаційні перевірки через інструкції `POPCNT`.

### 1.1 C API: Структура `bloom_filter_t`

У мові C11 класична реалізація фільтра Блума описується структурою `bloom_filter_t`. Динамічний масив `bits` виділяється у системному гіпі за допомогою викликів `aligned_alloc` або `posix_memalign` з обов'язковим вирівнюванням за межею 64 байтів. Це гарантує збіг меж масиву з фізичними кеш-лініями процесора та запобігає виникненню міжсторінкових розривам (Cache Line Split Access).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct {
    uint8_t *bits;       /* Динамічний бітовий масив з 64-байтовим вирівнюванням */
    size_t num_bits;     /* Загальна кількість бітів у векторі (m) */
    size_t num_hashes;   /* Кількість хеш-функцій (k) */
    size_t count;        /* Кількість успішно вставлених у фільтр елементів (n) */
} bloom_filter_t;
```
```cpp
#include <cstdint>
#include <vector>
#include <cstddef>

namespace sys {

struct bloom_filter_data {
    std::vector<std::uint8_t> bits; // Динамічний бітовий масив C++
    std::size_t num_bits{0};        // Кількість бітів m
    std::size_t num_hashes{0};      // Кількість хеш-функцій k
    std::size_t count{0};           // Кількість елементів n
};

} // namespace sys
```
:::

Кожне поле структури виконує строго визначену функцію в системній пам'яті:
* `bits`: вказівник на виділений буфер байтів. Кожен байт містить 8 послідовних бітів прапорців. Обсяг пам'яті у байтах становить (m + 7) / 8.
* `num_bits`: вираховується за математичною формулою `m = - (n * ln(p)) / (ln(2))^2` при ініціалізації структури.
* `num_hashes`: вираховується за формулою `k = (m / n) * ln(2)`.
* `count`: лічильник вставлених елементів, що використовується моніторингом для визначення актуального коефіцієнта заповнення бітового вектору `fill_ratio = count * k / num_bits`.

### 1.2 C++ API: RAII Клас `sys::bloom_filter`

У C++20 реалізація обгортається у RAII-клас `sys::bloom_filter`. Клас керує власним буфером пам'яті через `std::vector<std::uint8_t>`, забороняє операції неявного копіювання для запобігання випадковому дублюванню масиву розміром у сотні мегабайтів та підтримує семантику переміщення (Move Semantics).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Оголошення процедур C API для керування RAII-обгорткою */
void bloom_filter_init_raii(void **bits, size_t size);
void bloom_filter_free_raii(void *bits);
```
```cpp
#include <cstdint>
#include <span>
#include <vector>
#include <string_view>
#include <memory>

namespace sys {

class bloom_filter {
public:
    // Конструктор створює фільтр на основі очікуваної ємності n та бажаної помилки p
    explicit bloom_filter(std::size_t expected_elements, double false_positive_rate);
    
    // Заборона копіювання задля уникнення важких алокацій
    bloom_filter(const bloom_filter&) = delete;
    bloom_filter& operator=(const bloom_filter&) = delete;

    // Підтримка семантики переміщення
    bloom_filter(bloom_filter&&) noexcept = default;
    bloom_filter& operator=(bloom_filter&&) noexcept = default;
    ~bloom_filter() noexcept = default;

    // Вставка байтових ключів та рядкових представлень
    void add(std::span<const std::uint8_t> key) noexcept;
    void add(std::string_view key) noexcept;
    
    // Перевірка наявності ключів у фільтрі
    [[nodiscard]] bool contains(std::span<const std::uint8_t> key) const noexcept;
    [[nodiscard]] bool contains(std::string_view key) const noexcept;

    // Очищення структури та отримання метрик
    void clear() noexcept;
    [[nodiscard]] std::size_t size_in_bytes() const noexcept;
    [[nodiscard]] std::size_t element_count() const noexcept;
    [[nodiscard]] double current_false_positive_rate() const noexcept;

private:
    std::size_t num_bits_;
    std::size_t k_;
    std::size_t count_{0};
    std::vector<std::uint8_t> bits_;
};

} // namespace sys
```
:::

---

## 2. Повна специфікація функцій C та C++ API

### 2.1 Ініціалізація та керування пам'яттю

Функції ініціалізації обчислюють математично оптимальні параметри вектору та виділяють обсяг пам'яті. У разі виникнення помилки алокації C-функції повертають `false`, залишаючи структуру в обнуленому стані, а C++ викликає виняток `std::bad_alloc`.

Передумовою для успішного виконання є дотримання діапазонів аргументів: кількість елементів `n > 0`, а ймовірність помилки `p` перебуває в інтервалі від `0.0` до `1.0`. При некоректних аргументах система повертає `false` або викидає `std::invalid_argument`.

Алокація пам'яті вирівнюється за межею 64 байтів (розмір кеш-лінії сучасних процесорів x86_64 та ARM64). Це усуває проблему розщеплення кеш-ліній (Cache Line Split Unaligned Access). Коли масив бітів виділяється через стандартний `malloc`, адреса буфера може виявитися не парною 64 байтам. При виконанні побітової операції встановлення `bit_array[idx] |= mask` процесор змушений зчитувати дві сусідні кеш-лінії, якщо індекс потрапляє на межу сторінок, викликаючи блокування шини пам'яті (Bus Lock). Використання `aligned_alloc(64, size)` гарантує відсутність накладних витрат.

У разі нестачі оперативної пам'яті (OOM) під час ініціалізації вектору розміром у гігабайти C-функція `bloom_init` коректно звільняє всі проміжні ресурси, встановлює `filter->bits = NULL` і повертає `false`. Потоковий код зобов'язаний перевіряти це значення перед викликом `bloom_add`.

#### C та C++ API Ініціалізації

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * Автоматично обчислює m і k та ініціалізує фільтр Блума.
 * 
 * Контракт виконання:
 * - expected_elements мусить бути більшим за 0.
 * - fp_rate мусить перебувати у відкритому інтервалі (0.0, 1.0).
 * 
 * @param filter Вказівник на виділену користувачем структуру bloom_filter_t.
 * @param expected_elements Очікувана кількість ключів (n).
 * @param fp_rate Допустима ймовірність хибнопозитивного спрацьовування (p).
 * @return true при успішному виділенні пам'яті, false у разі помилки malloc/aligned_alloc.
 */
bool bloom_init(bloom_filter_t *filter, size_t expected_elements, double fp_rate);

/**
 * Створює фільтр Блума з ручним специфікуванням точних параметрів m та k.
 * 
 * @param filter Вказівник на структуру фільтра.
 * @param num_bits Загальний розмір масиву в бітах (m).
 * @param num_hashes Кількість хеш-функцій (k).
 * @return true у разі успішної виділеної пам'яті, false при помилці.
 */
bool bloom_init_explicit(bloom_filter_t *filter, size_t num_bits, size_t num_hashes);

/**
 * Звільняє динамічний бітовий масив та скидає лічильники.
 * 
 * @param filter Вказівник на структуру фільтра Блума.
 */
void bloom_free(bloom_filter_t *filter);
```
```cpp
#include <memory>
#include <cstddef>

namespace sys {

class bloom_filter_factory {
public:
    // Фабричний метод створення фільтра з логуванням та обробкою винятків
    [[nodiscard]] static std::unique_ptr<bloom_filter> create(
        std::size_t capacity, 
        double target_fp_rate
    );

    // Створення фільтра з явним вказуванням розмірів вектору m і k
    [[nodiscard]] static std::unique_ptr<bloom_filter> create_explicit(
        std::size_t num_bits, 
        std::size_t num_hashes
    );
};

} // namespace sys
```
:::

---

### 2.2 Операції вставки та перевірки (Add / Contains)

Операція `bloom_add` модифікує бітовий вектору. Завдяки застосуванню оптимізації Кірша-Мітценмахера `g_i(x) = (h_1(x) + i * h_2(x)) mod m`, замість `k` незалежних викликів хешування обчислюється лише один 128-бітний хеш MurmurHash3_x64_128. Перші 64 біти хешу слугують як `h_1(x)`, а другі 64 біти — як `h_2(x)`.

Операція `bloom_contains` виконує рання зупинку (Early Exit): перевірка індексів виходить із циклу на першому ж нульовому біті `0`, що робить середній час виконання перевірки відсутнього ключа значно коротшим за `O(k)`. Наприклад, якщо бітовий вектору заповнений одиницями на 50%, імовірність знайти першу `0` вже на першому кроці становить 50%, а на двох кроках — 75%.

Для максимізації пропускної здатності при обробці великих масивів даних додавання ключів не вимагає переаллокації пам'яті, якщо кількість вставлених ключів перевищує розраховану ємність `n`. Проте перевищення `n` збільшує щільність одиниць у масиві, що призводить до поступового підвищення емпіричної ймовірності помилки вище за закладений поріг `p`.

#### C та C++ API Вставки та Перевірки

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * Додає ключ до фільтра Блума.
 * 
 * Часова складність: O(k).
 * Потокобезпека: Потрібне зовнішнє блокування запису (Write Lock).
 * 
 * @param filter Вказівник на ініціалізований фільтр Блума.
 * @param data Вказівник на буфер ключа.
 * @param len Довжина буфера в байтах.
 */
void bloom_add(bloom_filter_t *filter, const void *data, size_t len);

/**
 * Перевіряє наявність ключа у фільтрі.
 * 
 * Часова складність: O(k) в найгіршому випадку, O(1) пересічно завдяки раній зупинці.
 * Потокобезпека: Дозволяється паралельне зчитання декількома потоками без блокувань.
 * 
 * @param filter Вказівник на фільтр Блума.
 * @param data Вказівник на буфер ключа.
 * @param len Довжина ключа у байтах.
 * @return false якщо ключ ГАРАНТОВАНО відсутній; true якщо ключ ІМОВІРНО є.
 */
bool bloom_contains(const bloom_filter_t *filter, const void *data, size_t len);
```
```cpp
#include <string_view>
#include <span>
#include <cstdint>

namespace sys {

class bloom_filter_ops {
public:
    static void add(bloom_filter& bf, std::string_view key) noexcept {
        bf.add(std::span<const std::uint8_t>(reinterpret_cast<const std::uint8_t*>(key.data()), key.size()));
    }

    [[nodiscard]] static bool contains(const bloom_filter& bf, std::string_view key) noexcept {
        return bf.contains(std::span<const std::uint8_t>(reinterpret_cast<const std::uint8_t*>(key.data()), key.size()));
    }
};

} // namespace sys
```
:::

---

## 3. Специфікація кеш-локального блочного фільтра (Blocked Bloom Filter API)

У системних середовищах із великими масивами пам'яті (від 100 МБ до десятків гігабайтів) класичний фільтр Блума створює суттєві затримки через `k` промахів кешу L3. Блочний фільтр Блума (Blocked Bloom Filter) усуває цю затримку шляхом розбиття вектору на масив 64-байтових блоків, кожен з яких строго вирівняний за межею кеш-лінії CPU.

Перший 64-бітний хеш `h_1(x)` визначає номер 64-байтового блоку у масиві. Процесор завантажує весь блок у L1-кеш за 1 такт шини. Другий хеш `h_2(x)` обчислює `k` бітових індексів всередині цього єдиного 64-байтового блоку (від 0 до 511 бітів).

Локалізація пам'яті гарантує, що при виконанні перевірки ключа кількість промахів кешу L3 дорівнює строго **1 промаху**, незалежно від кількості хеш-функцій `k`. Це забезпечує 3-5-разовий приріст продуктивності у СУБД RocksDB та ClickHouse.

Аналіз апаратної ефективності блочного фільтра виявляє важливий інженерний компроміс: обмеження `k` бітів рамками 511 бітів одного 64-байтового блоку дещо підвищує ймовірність локальних колізій усередині блоку. Емпірично це збільшує загальний рівень хибнопозитивних спрацьовувань приблизно на 10–15% порівняно з ідеально рівномірним класичним фільтром Блума того ж розміру, але компенсується багаторазовим прискоренням роботи процесора.

### C та C++ API Блочного фільтра

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct __attribute__((aligned(64))) {
    uint32_t buckets[16]; /* 16 слів * 32 біти = 512 бітів = 64 байти */
} bloom_block_t;

typedef struct {
    bloom_block_t *blocks; /* Вирівняний масив 64-байтових кеш-блоків */
    size_t num_blocks;     /* Загальна кількість блоків */
    size_t k;              /* Кількість бітів у блоці (зазвичай k = 8) */
} blocked_bloom_filter_t;

/**
 * Ініціалізує блочний фільтр Блума з вирівнюванням пам'яті aligned_alloc.
 */
bool blocked_bloom_init(blocked_bloom_filter_t *bf, size_t num_blocks, size_t k);

/**
 * Додає елемент у блочний фільтр за двома 64-бітними хешами.
 */
void blocked_bloom_add(blocked_bloom_filter_t *bf, uint64_t h1, uint64_t h2);

/**
 * Здійснює перевірку ключа з гарантією строго 1 промаху кешу L3.
 */
bool blocked_bloom_contains(const blocked_bloom_filter_t *bf, uint64_t h1, uint64_t h2);

/**
 * Звільняє пам'ять вирівняного вектору блоків.
 */
void blocked_bloom_free(blocked_bloom_filter_t *bf);
```
```cpp
#include <cstdint>
#include <vector>
#include <cstddef>

namespace sys {

class alignas(64) blocked_bloom_filter {
public:
    explicit blocked_bloom_filter(std::size_t num_blocks, std::size_t k_hashes);
    ~blocked_bloom_filter() noexcept;

    blocked_bloom_filter(const blocked_bloom_filter&) = delete;
    blocked_bloom_filter& operator=(const blocked_bloom_filter&) = delete;
    blocked_bloom_filter(blocked_bloom_filter&&) noexcept = default;
    blocked_bloom_filter& operator=(blocked_bloom_filter&&) noexcept = default;

    void add_with_hashes(std::uint64_t h1, std::uint64_t h2) noexcept;
    [[nodiscard]] bool contains_with_hashes(std::uint64_t h1, std::uint64_t h2) const noexcept;

private:
    struct alignas(64) block {
        std::uint32_t words[16]{0};
    };
    
    std::size_t num_blocks_;
    std::size_t k_;
    block* blocks_{nullptr};
};

} // namespace sys
```
:::

---

## 4. Розширені інтерфейси: Секційований та Масштабований фільтри

### 4.1 Partitioned Bloom Filter (Секційований фільтр)

Секційований фільтр розбиває бітовий вектору розміром `m` на `k` виділених секцій розміром `s = m/k`. Кожна хеш-функція `h_i(x)` індексує біти строго всередині `i`-ї секції, усуваючи міждоменні колізії бітів та спрощуючи паралельне опитування на векторизованих SIMD-процесорах.

Секціонування усуває диспропорцію заповнення окремих ділянок вектору, яка виникає при звичайному випадковому хешуванні. Крім того, кожна з `k` секцій може оброблятися окремим векторним стрижнем у регістрах AVX-512 або ARM Neon.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

void partitioned_bloom_add(uint8_t *bits, size_t section_size_bits, size_t k, uint64_t h1, uint64_t h2) {
    for (size_t i = 0; i < k; i++) {
        size_t bit_in_section = (h1 + i * h2) % section_size_bits;
        size_t global_bit = i * section_size_bits + bit_in_section;
        bits[global_bit >> 3] |= (uint8_t)(1u << (global_bit & 7));
    }
}
```
```cpp
#include <span>
#include <cstdint>
#include <cstddef>

namespace sys {

void add_partitioned(std::span<std::uint8_t> bits, std::size_t section_bits,
                     std::size_t k, std::uint64_t h1, std::uint64_t h2) noexcept {
    for (std::size_t i = 0; i < k; ++i) {
        std::size_t bit_in_section = (h1 + i * h2) % section_bits;
        std::size_t global_bit = i * section_bits + bit_in_section;
        bits[global_bit >> 3] |= static_cast<std::uint8_t>(1u << (global_bit & 7));
    }
}

} // namespace sys
```
:::

---

### 4.2 Scalable Bloom Filter (Масштабований фільтр)

Масштабований фільтр динамічно розширює ємність шляхом додавання нових шарів F_0, F_1, ..., F_j. Кожен наступний шар створюється з подвоєним розміром `m_{j+1} = m_0 * S^j` та зменшеним коефіцієнтом помилки `p_{j+1} = p_0 * R^{j+1}`, де R належаить інтервалу від 0.8 до 0.9. Сумарна ймовірність помилки для всього ланцюжка шарів задовольняє нерівність сума(p_j) <= p_target.

Додавання елемента у масштабований фільтр завжди виконується у найновіший активний шар F_current. Перевірка наявності ключа опитує всі шари послідовно від F_0 до F_current і повертає `true`, якщо ключ знайдено хоча б в одному шарі.

:::tabs
```c
#include <stdbool.h>
#include <stddef.h>

typedef struct {
    bloom_filter_t *layers;
    size_t num_layers;
    double target_fp_rate;
} scalable_bloom_filter_t;

void scalable_bloom_add(scalable_bloom_filter_t *sbf, const void *key, size_t len);
bool scalable_bloom_contains(const scalable_bloom_filter_t *sbf, const void *key, size_t len);
```
```cpp
#include <vector>
#include <cstddef>
#include <string_view>

namespace sys {

class scalable_bloom_filter {
public:
    explicit scalable_bloom_filter(double target_fp_rate);
    void add(std::string_view key);
    [[nodiscard]] bool contains(std::string_view key) const noexcept;

private:
    std::vector<bloom_filter> layers_;
    double target_fp_;
};

} // namespace sys
```
:::

---

## 5. Безблокувальна потокобезпека та атомарні операції

Для високопродуктивних багатопотокових систем вставка бітів може виконуватися без застосування важких м'ютексів `pthread_mutex_t` або `std::mutex`. Використовуються атомарні побітові інструкції `atomic_fetch_or` у C11 та `std::atomic<uint8_t>::fetch_or` у C++.

Оскільки побітова операція `OR` є комутативною та асоціативною, виклики виконуються з найшвидшим порядковим модифікатором пам'яті `memory_order_relaxed`, що повністю усуває бар'єри шини пам'яті (Memory Barriers) та забезпечує максимальну пропускну здатність паралельної вставки.

З точки зору архітектури процесора, атомарний виклик `fetch_or` на рівні системних інструкцій виливається у `LOCK OR [rdi], al` на x86_64 або комбінацію `LDREX/STREX` на ARM64. Оскільки операція модифікує лише один байт, міжпроцесорна когерентність кешу через протокол MESI оновлює лише одну кеш-лінію, не блокуючи виконання сусідніх потоків, якщо ті працюють з іншими байтами вектору.

При гонках сигналів у багатопроцесорних вузлах NUMA використання `memory_order_relaxed` гарантує атомарну цілісність кожного байта вектору, але не гарантує негайної видимості виставленого біта іншим ядрам без міжпроцесорного переривання IPI (Inter-Processor Interrupt). У базах даних це допустимо, оскільки затримка видимості у 10–20 наносекунд лише тимчасово підвищує ймовірність False Positive для паралельного зчитувача.

:::tabs
```c
#include <stdatomic.h>
#include <stdint.h>

/* Безблокувальне атомарне встановлення біта у C11 */
void bloom_set_bit_atomic(_Atomic uint8_t *bit_array, size_t bit_index) {
    _Atomic uint8_t *byte_ptr = &bit_array[bit_index >> 3];
    uint8_t mask = (uint8_t)(1u << (bit_index & 7));
    atomic_fetch_or_explicit(byte_ptr, mask, memory_order_relaxed);
}
```
```cpp
#include <atomic>
#include <vector>
#include <cstddef>

namespace sys {

// Безблокувальний атомарний фільтр у C++
class atomic_bloom_filter {
public:
    explicit atomic_bloom_filter(std::size_t num_bits)
        : bits_((num_bits + 7) / 8) {
        for (auto& b : bits_) b.store(0, std::memory_order_relaxed);
    }

    void set_bit_atomic(std::size_t bit_index) noexcept {
        std::size_t byte_idx = bit_index >> 3;
        std::uint8_t mask = static_cast<std::uint8_t>(1u << (bit_index & 7));
        bits_[byte_idx].fetch_or(mask, std::memory_order_relaxed);
    }

private:
    std::vector<std::atomic<std::uint8_t>> bits_;
};

} // namespace sys
```
:::

---

## 6. Мережевий бінарний формат серіалізації та Endianness

При збереженні бітового масиву у бінарний файл або передачі через мережевий протокол (gRPC, TCP socket) використовується вирівняна структура заголовка з фіксованим Big-Endian порядком байтів.

Формат специфікує перші 20 байтів файлу як фіксований заголовок:
1. `magic` (4 байти): магічне число `0x424C4F4F` (ASCII рядка `"BLOO"`).
2. `version` (4 байти): версія специфікації (поточна версія `0x0001`).
3. `num_bits` (8 байтів): 64-бітне ціле число розміру `m` у мережевому порядку байтів (Big-Endian).
4. `num_hashes` (4 байти): 32-бітне ціле число кількості хеш-функцій `k`.

Після заголовка розміщується суцільний масив байтів payload розміром (m + 7) / 8.

Утиліти серіалізації перевіряють магічне число `magic` перед зчитуванням масиву. Якщо магічне число не відповідає значенням `0x424C4F4F`, десеріалізатор відхиляє файл як пошкоджений, запобігаючи викликам зчитування пам'яті за межами виділеного буфера (Buffer Overflow Prevention). Конвертація байтів Little-Endian на x86_64 процесорах здійснюється інструкціями `BSWAP` чи утилітами `std::byteswap` / `htons`.

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                     Magic Header ("BLOO")                     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Version (0x0001)                       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                     Number of Bits m (64-bit)                 +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                   Number of Hashes k (32-bit)                 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      Payload Bits Array                       |
|                              ...                              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

:::tabs
```c
#include <stdint.h>
#include <arpa/inet.h>

typedef struct __attribute__((packed)) {
    uint32_t magic;      /* 0x424C4F4F ("BLOO") */
    uint32_t version;    /* Версія 1 */
    uint64_t num_bits;   /* Кількість бітів m у Big-Endian */
    uint32_t num_hashes; /* Кількість хеш-функцій k у Big-Endian */
} bloom_header_t;

void pack_bloom_header(bloom_header_t *hdr, uint64_t m, uint32_t k) {
    hdr->magic = htonl(0x424C4F4F);
    hdr->version = htonl(1);
    hdr->num_bits = __builtin_bswap64(m);
    hdr->num_hashes = htonl(k);
}
```
```cpp
#include <cstdint>
#include <bit>

struct alignas(4) bloom_header {
    std::uint32_t magic{0x424C4F4F};
    std::uint32_t version{1};
    std::uint64_t num_bits{0};
    std::uint32_t num_hashes{0};
};

[[nodiscard]] inline bloom_header serialize_header(std::uint64_t m, std::uint32_t k) noexcept {
    bloom_header hdr;
    if constexpr (std::endian::native == std::endian::little) {
        hdr.magic = std::byteswap(hdr.magic);
        hdr.version = std::byteswap(hdr.version);
        hdr.num_bits = std::byteswap(m);
        hdr.num_hashes = std::byteswap(k);
    } else {
        hdr.num_bits = m;
        hdr.num_hashes = k;
    }
    return hdr;
}
```
:::

---

## 7. Інтеграція з підсистемою eBPF Linux Kernel

У ядрі Linux (версії 5.16+) фільтр Блума інтегровано як рідний тип карти `BPF_MAP_TYPE_BLOOM_FILTER`. Карта використовується для швидкого відсіювання мережевих пакетів у драйверах XDP (eXpress Data Path) до моменту виділення об'єктів `sk_buff` у мережевому стеку ядра.

Розробники специфікують карту eBPF у системній секції `.maps`:
- `type`: `BPF_MAP_TYPE_BLOOM_FILTER`
- `key_size`: 0 (карти Блума не мають явних ключів значення)
- `value_size`: розмір елемента у байтах (наприклад `sizeof(uint32_t)` для IPv4 адрес)
- `max_entries`: очікувана кількість елементів `n`
- `map_extra`: параметр `k` хеш-функцій ядра

Системні виклики ядра для роботи з eBPF карткою:
* `bpf_map_push_elem(&bloom_map, &value, BPF_ANY)`: вставка елемента у фільтр ядра.
* `bpf_map_peek_elem(&bloom_map, &value)`: перевірка наявності елемента. Повертає `0` якщо елемент імовірно є, або `-ENOENT` якщо елемент гарантовано відсутній.

Використання карток Блума у програмах XDP дає змогу обробляти навантаження DDoS-атак зі швидкістю понад 14.8 мільйонів пакетів на секунду (10GbE Line Rate), оскільки пакети відсутніх заблокованих IP-адрес скидаються на рівні мережевої карти без залучення підсистем пам'яті ядра.

---

## 8. POSIX `mmap` та файлова персистентність

Для збереження фільтрів Блума розміром у гігабайти без зчитування файлу в пам'ять при старті процесу застосовується системний виклик `mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)`.

Особливості роботи з `mmap`:
1. **Подкачка сторінок (Page Faults)**: Операційна система підвантажує 4-кілобайтові сторінки файлу в оперативну пам'ять лише тоді, коли процесор звертається до відповідного індексу біта.
2. **Синхронізація (msync)**: Примусове вимивання брудних сторінок на SSD здійснюється системним викликом `msync(mapped_ptr, size, MS_ASYNC)`.
3. **Обробка сигналів SIGBUS та SIGSEGV**: Якщо розмір файлу на диску зменшиться іншим процесом під час роботи `mmap`, звернення до відсутньої сторінки викличе сигнал `SIGBUS`. Звернення за межі відображеного діапазону адреси викликає `SIGSEGV`. Система зобов'язана встановлювати обробник сигналів `sigaction` для безпечного перехоплення таких помилок.

Для прискорення фонового підвантаження сторінок з NVMe SSD додатки викликають підказку ядра `madvise(mapped_ptr, size, MADV_WILLNEED)`, яка ініціює асинхронне зчитування блоків у кеш сторінок (Page Cache).

Паралельний запис у відображений через `mmap` бітовий масив з кількох процесів вимагає застосування прапорця `MAP_SHARED`. Якщо застосувати `MAP_PRIVATE`, зміни залишаться лише у локальних Copy-On-Write (COW) сторінках даного процесу і не будуть збережені у вихідному SSTable-файлі на диску.

---

## 9. Порівняльний аналіз суміжних ймовірнісних структур

При виборі архітектури системи розробник повинен оцінити характеристики фільтра Блума у зіставленні з найближчими альтернативами:

| Параметр порівняння | Classical Bloom | Counting Bloom | Cuckoo Filter | Ribbon Filter |
| :--- | :--- | :--- | :--- | :--- |
| **Видалення елементів** | ❌ Ні | ✅ Так | ✅ Так | ❌ Ні |
| **Витрата пам'яті (p=1%)** | 9.6 бітів/ел | 38.4 бітів/ел (4 біти/комірку) | 8.4 бітів/ел | **7.1 бітів/ел** |
| **Промахи кешу L3** | k промахів | k промахів | 2 промахи | 1-2 промахи |
| **Складність вставки** | O(k) | O(k) | O(1) амортизована | O(1) |
| **Складність побудови** | Потокова | Потокова | Потокова | Пакетна (Gaussian Elimination) |

Фільтр Блума залишається найбільш універсальним рішенням для потокових даних завдяки своїй простоті, відсутності процедур заміщення (Eviction) при додаванні елемента та надійності в багатопотокових середовищах.

---

## 10. Складність операцій та використання системних ресурсів

| Операція / Функція | Часова складність (Average) | Часова складність (Worst-case) | Просторова складність | Промахи кешу L3 |
| :--- | :--- | :--- | :--- | :--- |
| `bloom_init` | O(m) | O(m) | O(m) бітів | 0 (локальна алокація) |
| `bloom_add` | O(k) | O(k) | O(1) | до k промахів |
| `bloom_contains` | O(1) (рання зупинка) | O(k) | O(1) | від 1 до k промахів |
| `blocked_bloom_contains` | O(1) | O(k) | O(1) | **строго 1 промах** |
| `bloom_union` | O(m / 64) | O(m / 64) | O(1) | послідовний скан |

---

## 11. Довідник розрахунку параметрів (Reference Chart)

Таблиця для оцінки пам'яті при ємності n = 1 000 000 елементів (1M):

| p (False Positive) | m (Бітів) | k (Хеш-функцій) | Обсяг пам'яті (Байтів) |
| :--- | :--- | :--- | :--- |
| 5.0% | 6 235 224 | 4 | 779 403 Б (~761 КБ) |
| 1.0% | 9 585 058 | 7 | 1 198 133 Б (~1.17 МБ) |
| 0.1% | 14 377 588 | 10 | 1 797 199 Б (~1.75 МБ) |
| 0.01% | 19 170 117 | 13 | 2 396 265 Б (~2.34 МБ) |

Таблиця для оцінки пам'яті при ємності n = 100 000 000 елементів (100M):

| p (False Positive) | m (Бітів) | k (Хеш-функцій) | Обсяг пам'яті (Байтів) |
| :--- | :--- | :--- | :--- |
| 1.0% | 958 505 835 | 7 | 119 813 230 Б (~114 МБ) |
| 0.1% | 1 437 758 757 | 10 | 179 719 845 Б (~171 МБ) |
