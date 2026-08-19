# 📋 Специфікація API підрахункового фільтра Блума

Підрахунковий фільтр Блума (Counting Bloom Filter, CBF) — це ймовірнісна структура даних, що представляє множину елементів із підтримкою операцій додавання, перевірки належності та безпечного видалення.

Цей документ містить повний опис програмного інтерфейсу (API) бібліотеки CBF мовами C та C++, включаючи контракти функцій, інваріанти структури, алгебру об'єднання та перетину множин, спектральні оцінювачі частоти, інтерфейс підключення власних хеш-функцій (SPI), відображення пам'яті через `mmap`, атомарні lock-free варіанти API, статистичну діагностику, гарантії часової та просторової складності, формати бінарної серіалізації, математичні утиліти конфігурування, вимоги до вирівнювання пам'яті, наскрізні приклади використання, рецепти інтеграції, правила санітайзерів пам'яті, обмеження обробників сигналів (Signal Safety), прив'язку до NUMA-вузлів та бінарну сумісність C ABI.

## Інваріанти структури даних

Будь-яка коректна реалізація підрахункового фільтра Блума повинна суворо підтримувати такі фундаментальні інваріанти:

1. **Інваріант відсутності хибнонегативних відповідей (Zero False Negatives)**:
   Якщо елемент `x` було додано до фільтра за допомогою операції `insert(x)`, і після цього для нього не виконувалася операція `remove(x)` (а також не виконувалися помилкові операції видалення неіснуючих ключів), то будь-який виклик `contains(x)` **гарантовано повертає `true`**.

2. **Інваріант діапазону лічильників**:
   Для будь-якого індексу `i ∈ [0, capacity - 1]` значення лічильника `C[i]` є цілим числом у діапазоні:
   `0 ≤ C[i] ≤ 15` (для 4-бітної розрядності комірок).

3. **Інваріант насичення (Saturating Invariant)**:
   Якщо значення комірки досягло максимального порогу `15` (`0x0F`), воно фіксується у стані насичення. Така комірка більше не збільшується при операціях вставки і **ніколи не зменшується при операціях видалення**, що унеможливлює порушення інваріанта №1.

4. **Інваріант пам'яті**:
   Загальний розмір виділеного буфера лічильників у байтах строго дорівнює:
   `byte_size = ceil(capacity / 2) = (capacity + 1) / 2`.

---

## Загальні типи даних та коди повернення

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    CBF_SUCCESS              =  0, /* Операція виконана успішно */
    CBF_ERR_INVALID_PARAM    = -1, /* Некоректні вхідні параметри (NULL-вказівник, нульова ємність) */
    CBF_ERR_NO_MEMORY        = -2, /* Помилка виділення динамічної пам'яті алокатором */
    CBF_ERR_NOT_FOUND        = -3, /* Елемент гарантовано відсутній при спробі видалення */
    CBF_ERR_BUFFER_TOO_SMALL = -4, /* Наданий користувачем буфер замалий для серіалізації/експорту */
    CBF_ERR_CORRUPT_DATA     = -5, /* Пошкоджені бінарні дані або невідповідність контрольної суми */
    CBF_ERR_INCOMPATIBLE     = -6, /* Невідповідність розмірів або параметрів хешування при злитті */
    CBF_ERR_IO               = -7, /* Помилка дискового введення-виведення або mmap */
    CBF_WARN_SATURATED       =  1  /* Операція успішна, але лічильник досяг максимуму 15 */
} CbfStatus;

typedef struct CountingBloomFilter CountingBloomFilter;

/* Тип функції зворотного виклику для користувацького хешування */
typedef void (*CbfCustomHashFn)(const void *key, size_t len, uint32_t seed, uint32_t *h1, uint32_t *h2);
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <vector>
#include <expected>
#include <array>
#include <functional>
#include <filesystem>

namespace algorithms::data_structures {

enum class CbfError {
    InvalidParameter,
    OutOfMemory,
    ElementNotFound,
    BufferTooSmall,
    CorruptedData,
    IncompatibleParameters,
    IoError
};

enum class InsertResult {
    Inserted,
    InsertedWithSaturation
};

using CustomHashFn = std::function<std::pair<uint32_t, uint32_t>(std::string_view, uint32_t)>;

} // namespace algorithms::data_structures
```
:::

---

## 1. Управління життєвим циклом структури

### Створення фільтра

:::tabs
```c
CountingBloomFilter *cbf_create(size_t capacity, uint32_t num_hashes);
CountingBloomFilter *cbf_create_keyed(size_t capacity, uint32_t num_hashes, const uint8_t key[16]);
CountingBloomFilter *cbf_create_custom(size_t capacity, uint32_t num_hashes, CbfCustomHashFn hash_fn);
CountingBloomFilter *cbf_create_mmap(const char *filepath, size_t capacity, uint32_t num_hashes);
```
```cpp
explicit CountingBloomFilter::CountingBloomFilter(size_t capacity, uint32_t numHashes);
explicit CountingBloomFilter::CountingBloomFilter(size_t capacity, uint32_t numHashes, 
                                                 std::span<const uint8_t, 16> secretKey);
explicit CountingBloomFilter::CountingBloomFilter(size_t capacity, uint32_t numHashes, 
                                                 CustomHashFn customHash);
[[nodiscard]] static std::expected<CountingBloomFilter, CbfError> 
CountingBloomFilter::openMmap(const std::filesystem::path& path, size_t capacity, uint32_t numHashes);
```
:::

* **Призначення**: Створює та ініціалізує новий екземпляр підрахункового фільтра Блума в динамічній пам'яті або відображає файл на диску (`mmap`).
* **Параметри**:
  * `capacity` — загальна кількість 4-бітних комірок-лічильників (`m > 0`).
  * `num_hashes` — кількість хеш-функцій на один ключ (`k > 0`).
  * `key` / `secretKey` — 16 байтів криптографічної солі (SipHash-2-4).
  * `hash_fn` / `customHash` — вказівник на функцію користувацького хешування.
  * `filepath` / `path` — шлях до файлу на файловій системі для постійного збереження стану.
* **Повертає**: Вказівник на створену структуру `CountingBloomFilter` або `NULL` у разі нестачі пам'яті чи некоректних аргументів.
* **Складність**: Часова `O(m)`, просторова `O(m)` (виділяється `(m + 1) / 2` байтів).
* **Початковий стан**: Усі лічильники ініціалізуються нулями (`0`), лічильник активних елементів `count = 0`.
* **Передмови (Preconditions)**: `capacity > 0`, `num_hashes > 0`.
* **Післямови (Postconditions)**: Пам'ять обнулена, фільтр готовий до виконання операцій `insert`, `contains`, `remove`.

### Звільнення пам'яті

:::tabs
```c
void cbf_destroy(CountingBloomFilter *cbf);
```
```cpp
CountingBloomFilter::~CountingBloomFilter() = default;
```
:::

* **Призначення**: Звільняє всю оперативну пам'ять, виділену під буфер лічильників і керуючу структуру (або скидає зміни на диск через `msync` та розмонтовує `munmap`).
* **Параметри**:
  * `cbf` — вказівник на структуру фільтра (допускається передача `NULL`, виклик ігнорується).
* **Складність**: `O(1)`.

### Очищення фільтра

:::tabs
```c
CbfStatus cbf_clear(CountingBloomFilter *cbf);
```
```cpp
void CountingBloomFilter::clear() noexcept;
```
:::

* **Призначення**: Обнуляє всі лічильники фільтра, повертаючи структуру до початкового порожнього стану без повторного виділення пам'яті.
* **Параметри**:
  * `cbf` — вказівник на дійсний фільтр.
* **Повертає**: `CBF_SUCCESS` або `CBF_ERR_INVALID_PARAM`.
* **Складність**: `O(m / 2)` (заповнення буфера нулями через `memset`).

---

## 2. Базові операції над множиною

### Додавання елемента (Insert)

:::tabs
```c
CbfStatus cbf_insert(CountingBloomFilter *cbf, const void *key, size_t len);
```
```cpp
void CountingBloomFilter::insert(std::string_view key) noexcept;
void CountingBloomFilter::insert(std::span<const std::byte> data) noexcept;
```
:::

* **Призначення**: Додає ключ `key` довжиною `len` байтів до фільтра.
* **Параметри**:
  * `cbf` — вказівник на структуру фільтра.
  * `key` — вказівник на байтову послідовність ключа (не може бути `NULL`).
  * `len` — довжина ключа в байтах (`len > 0`).
* **Поведінка**: Обчислює `k` індексів за схемою Кірша-Міценмахера. Для кожного індексу зчитує значення лічильника: якщо воно менше 15, інкрементує його на 1. Збільшує внутрішній лічильник `count` на 1.
* **Повертає**:
  * `CBF_SUCCESS` — усі `k` комірок успішно інкрементовані без переповнення.
  * `CBF_WARN_SATURATED` — елемент додано, але щонайменше один лічильник досяг або вже мав значення 15 (заморожений).
  * `CBF_ERR_INVALID_PARAM` — некоректні вхідні дані.
* **Складність**: Часова `O(k + len)`, просторова `O(1)`.

### Перевірка належності (Lookup / Contains)

:::tabs
```c
bool cbf_contains(const CountingBloomFilter *cbf, const void *key, size_t len);
```
```cpp
[[nodiscard]] bool CountingBloomFilter::contains(std::string_view key) const noexcept;
[[nodiscard]] bool CountingBloomFilter::contains(std::span<const std::byte> data) const noexcept;
```
:::

* **Призначення**: Виконує ймовірнісну перевірку наявності ключа у множині.
* **Параметри**:
  * `cbf` — вказівник на структуру фільтра.
  * `key` — вказівник на ключ.
  * `len` — довжина ключа в байтах.
* **Поведінка**: Послідовно перевіряє `k` лічильників. Якщо знайдено хоча б один лічильник із нульовим значенням (`C[i] == 0`), негайно припиняє перевірку і повертає `false`. Якщо всі `k` лічильників строго більші за нуль (`C[i] > 0`), повертає `true`.
* **Повертає**:
  * `false` — елемент **гарантовано відсутній** у множині.
  * `true` — елемент **можливо присутній** (з контрольованою ймовірністю хибнопозитивного спрацьовування).
* **Складність**: Часова `O(k + len)` (у середньому швидше завдяки ранньому виходу при першому нулі), просторова `O(1)`.

### Видалення елемента (Remove)

:::tabs
```c
CbfStatus cbf_remove(CountingBloomFilter *cbf, const void *key, size_t len);
```
```cpp
bool CountingBloomFilter::remove(std::string_view key) noexcept;
bool CountingBloomFilter::remove(std::span<const std::byte> data) noexcept;
```
:::

* **Призначення**: Видаляє ключ із фільтра Блума.
* **Параметри**:
  * `cbf` — вказівник на структуру фільтра.
  * `key` — вказівник на ключ.
  * `len` — довжина ключа в байтах.
* **Поведінка**:
  1. Виконує перевірку `cbf_contains(cbf, key, len)`: якщо результат `false`, повертає `CBF_ERR_NOT_FOUND`.
  2. Обчислює `k` індексів: для кожної комірки зі значенням `1 ≤ C[i] < 15` зменшує лічильник на 1.
  3. Якщо комірка має значення `C[i] == 15` (насичена), її значення залишається незмінним.
  4. Зменшує загальний лічильник елементів `count` на 1.
* **Попередження**: Виклик функції для ключа, якого насправді немає у множині (але який дав хибне спрацьовування), може пошкодити лічильники інших дійсних ключів, спричинивши помилки False Negative!
* **Повертає**: `CBF_SUCCESS`, `CBF_ERR_NOT_FOUND` або `CBF_ERR_INVALID_PARAM` (у C++ `true` у разі успішного декременту, `false` якщо ключ не знайдено).
* **Складність**: Часова `O(k + len)`, просторова `O(1)`.

---

## 3. Алгебра множин: об'єднання та перетин фільтрів

Підрахунковий фільтр підтримує покомпонентні операції над сумісними структурами (фільтрами з однаковими `capacity` та `num_hashes`):

:::tabs
```c
CbfStatus cbf_union(CountingBloomFilter *dest, const CountingBloomFilter *src);
CbfStatus cbf_intersect(CountingBloomFilter *dest, const CountingBloomFilter *src);
```
```cpp
CountingBloomFilter& CountingBloomFilter::operator+=(const CountingBloomFilter& other);
[[nodiscard]] CountingBloomFilter CountingBloomFilter::intersectWith(const CountingBloomFilter& other) const;
```
:::

* **Об'єднання (Union)**: Для кожного індексу `i` обчислюється насичувана сума `C_dest[i] = min(15, C_dest[i] + C_src[i])`. Результат відповідає множині `S_dest ∪ S_src`.
* **Перетин (Intersection)**: Для кожного індексу `i` береться мінімум `C_dest[i] = min(C_dest[i], C_src[i])`. Результат представляє надмножину перетину `S_dest ∩ S_src`.
* **Вимоги до сумісності**: Обидва фільтри повинні мати однаковий розмір `capacity` та ідентичну схему хешування. У разі невідповідності повертається `CBF_ERR_INCOMPATIBLE`.

---

## 4. Спектральні оцінювачі та розширена діагностика

Підрахунковий фільтр Блума може використовуватися як Spectral Bloom Filter для оцінки частоти появи ключів (Minimum Estimator Саріель Коен та Йосі Матіаса):

:::tabs
```c
uint8_t cbf_estimate_frequency(const CountingBloomFilter *cbf, const void *key, size_t len);
CbfStatus cbf_counter_distribution(const CountingBloomFilter *cbf, uint64_t histogram[16]);
double cbf_saturation_rate(const CountingBloomFilter *cbf);
```
```cpp
[[nodiscard]] uint8_t CountingBloomFilter::estimateFrequency(std::string_view key) const noexcept;
[[nodiscard]] std::array<uint64_t, 16> CountingBloomFilter::counterDistribution() const noexcept;
[[nodiscard]] double CountingBloomFilter::saturationRate() const noexcept;
```
:::

* `cbf_estimate_frequency` / `estimateFrequency`: Обчислює мінімальне значення серед усіх `k` лічильників для ключа `key`: `f_est = min_{i} C[h_i(key)]`. Це значення є строгою верхньою оцінкою справжньої частоти елемента у потоці.
* `cbf_counter_distribution` / `counterDistribution`: Заповнює масив із 16 елементів гістограмою розподілу комірок (кількість комірок зі значеннями 0, 1, ..., 15).
* `cbf_saturation_rate` / `saturationRate`: Повертає частку заморожених комірок `C[i] == 15` відносно загальної ємності `capacity`.

---

## 5. Атомарний Lock-Free API для високопаралельних систем

Для систем обробки мережевих пакетів із сотнями робочих потоків (наприклад, DPDK Packet Processing Pipeline) бібліотека надає 8-бітний lock-free варіант фільтра, у якому кожна комірка представлена атомарним числом `std::atomic<uint8_t>`:

:::tabs
```c
/* Lock-Free C-інтерфейс (потребує C11 stdatomic.h) */
bool cbf_insert_atomic(CountingBloomFilter *cbf, const void *key, size_t len);
bool cbf_remove_atomic(CountingBloomFilter *cbf, const void *key, size_t len);
```
```cpp
// Lock-Free C++ інтерфейс
bool CountingBloomFilter::insertAtomic(std::string_view key) noexcept;
bool CountingBloomFilter::removeAtomic(std::string_view key) noexcept;
```
:::

* **Механізм роботи**: Кожна модифікація лічильника виконується за допомогою атомарного циклу `compare_exchange_weak` із семантикою `memory_order_relaxed`.
* **Перевага**: Повна відсутність блокувань (Zero Locks) та взаємних блокувань (Deadlocks) між паралельними ядрами процесора.
* **Ціна**: 8 бітів пам'яті на комірку (замість 4 бітів), оскільки апаратні процесори x86/ARM не підтримують атомарні інструкції на рівні окремих 4-бітних ніблів.

---

## 6. Інспекція стану структури

:::tabs
```c
uint8_t cbf_get_counter(const CountingBloomFilter *cbf, size_t index);
bool cbf_is_saturated(const CountingBloomFilter *cbf, size_t index);
size_t cbf_count(const CountingBloomFilter *cbf);
size_t cbf_capacity(const CountingBloomFilter *cbf);
size_t cbf_byte_size(const CountingBloomFilter *cbf);
```
```cpp
[[nodiscard]] uint8_t CountingBloomFilter::getCounter(size_t index) const noexcept;
[[nodiscard]] bool CountingBloomFilter::isSaturated(size_t index) const noexcept;
[[nodiscard]] size_t CountingBloomFilter::size() const noexcept;
[[nodiscard]] size_t CountingBloomFilter::capacity() const noexcept;
[[nodiscard]] size_t CountingBloomFilter::byteSize() const noexcept;
[[nodiscard]] bool CountingBloomFilter::empty() const noexcept;
```
:::

* `cbf_get_counter` / `getCounter`: Повертає поточне числове значення 4-бітної комірки (`0..15`) за заданим індексом.
* `cbf_is_saturated` / `isSaturated`: Повертає `true`, якщо лічильник за індексом досяг максимуму `15` і заморожений.
* `cbf_count` / `size`: Повертає поточну кількість активних елементів у фільтрі.
* `cbf_capacity` / `capacity`: Повертає загальну кількість комірок `m`.
* `cbf_byte_size` / `byteSize`: Повертає точний розмір виділеної пам'яті під лічильники в байтах.

---

## 7. Серіалізація та експорт бітових масивів

### Експорт бітового вектора (Bitmap Projection)

:::tabs
```c
CbfStatus cbf_export_bitmap(const CountingBloomFilter *cbf, uint8_t *bitmap, size_t bitmap_len);
```
```cpp
[[nodiscard]] std::vector<uint8_t> CountingBloomFilter::exportBitmap() const;
```
:::

* **Призначення**: Виконує швидку проєкцію CBF у класичний однобітовий фільтр Блума.
* **Поведінка**: Записує у вихідний буфер `bitmap` масив бітів, де біт `i` дорівнює `1`, якщо `C[i] > 0`, і `0`, якщо `C[i] == 0`.
* **Вимоги до розміру**: `bitmap_len >= (cbf->capacity + 7) / 8`.
* **Застосування**: Генерація компактних мережевих дайджестів у протоколі Summary Cache.

### Бінарна серіалізація та десеріалізація

:::tabs
```c
CbfStatus cbf_serialize(const CountingBloomFilter *cbf, void *buf, size_t buf_len, size_t *out_written);
CountingBloomFilter *cbf_deserialize(const void *buf, size_t buf_len);
```
```cpp
[[nodiscard]] std::vector<uint8_t> CountingBloomFilter::serialize() const;
[[nodiscard]] static std::expected<CountingBloomFilter, CbfError> 
CountingBloomFilter::deserialize(std::span<const std::byte> bytes);
```
:::

* **Формат бінарного кадру**:
  * Заголовок Magic (`4 байти`): `0x43424631` (`"CBF1"`).
  * `capacity` (`8 байтів`, uint64_t Little-Endian).
  * `num_hashes` (`4 байти`, uint32_t Little-Endian).
  * `count` (`8 байтів`, uint64_t Little-Endian).
  * `checksum` (`4 байти`, CRC32-IEEE 802.3 від масиву лічильників).
  * `payload` (`byte_size` байтів сирого масиву ніблів).

---

## 8. Організація пам'яті та бінарний макет (Memory Layout)

Пам'ять підрахункового фільтра розбивається на послідовність байтів, де кожен байт містить рівно два 4-бітних лічильники (нібли).

```text
Зміщення (байт):        0                   1                   2
                     ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐
Нібли лічильників:   │ C[1]    │ C[0]    │ C[3]    │ C[2]    │ C[5]    │ C[4]    │
                     │(bits4-7)│(bits0-3)│(bits4-7)│(bits0-3)│(bits4-7)│(bits0-3)│
                     └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
```

Для забезпечення максимальної швидкодії при роботі з SIMD-інструкціями та запобігання перетину меж кеш-рядків буфер пам'яті вирівнюється на 64-байтову межу (розмір лінії L1D-кешу x86-64 та ARM64) за допомогою `posix_memalign` або `std::aligned_alloc`.

У багатопроцесорних серверах із архітектурою NUMA (Non-Uniform Memory Access) виділення пам'яті під фільтр слід прив'язувати до локального вузла сокета через функцію `numa_alloc_onnode()` з бібліотеки `libnuma`. Це усуває транзитні запити міжпроцесорної шини UPI/Infinity Fabric і скорочує час затримки звернення до лічильників на 30–40%.

---

## 9. Математичні помічники розрахунку параметрів

Для спрощення конфігурації фільтра бібліотека надає допоміжні розрахункові функції:

:::tabs
```c
size_t cbf_optimal_capacity(size_t expected_elements, double target_fpr);
uint32_t cbf_optimal_hashes(size_t capacity, size_t expected_elements);
double cbf_estimate_fpr(size_t capacity, size_t active_elements, uint32_t num_hashes);
```
```cpp
[[nodiscard]] static size_t CountingBloomFilter::optimalCapacity(size_t expectedElements, double targetFpr) noexcept;
[[nodiscard]] static uint32_t CountingBloomFilter::optimalHashes(size_t capacity, size_t expectedElements) noexcept;
[[nodiscard]] static double CountingBloomFilter::estimateFpr(size_t capacity, size_t activeElements, uint32_t numHashes) noexcept;
```
:::

### Математичні формули розрахунку:

1. **Оптимальна кількість комірок `m_opt`**:
   Розраховує мінімальну кількість комірок `m` для заданої кількості елементів `n` та бажаної ймовірності хибнопозитивної відповіді `p`:

```text
m_opt = - (n · ln p) / (ln 2)² ≈ - (n · ln p) / 0.480453
```

2. **Оптимальна кількість хеш-функцій `k_opt`**:

```text
k_opt = (m / n) · ln 2 ≈ 0.693147 · (m / n)
```

3. **Оцінка поточної ймовірності помилки (FPR)**:

```text
FPR = ( 1 - e^(-k · n / m) )^k
```

---

## 10. Зведена таблиця конфігурації фільтра

У таблиці наведено стандартні інженерні параметри фільтра для різної цільової точності при збереженні `n = 1 000 000` ключів:

| Цільовий False Positive Rate `p` | Бітів на ключ `m/n` | Хеш-функцій `k` | Пам'ять CBF (4 біти) | Пам'ять Bloom (1 біт) | Ймовірність переповнення комірки |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **5.0%** (`0.05`) | 6.24 | 4 | 3.12 МБ | 0.78 МБ | `≈ 1.37 × 10⁻¹⁵` |
| **1.0%** (`0.01`) | 9.57 | 7 | 4.79 МБ | 1.20 МБ | `≈ 1.37 × 10⁻¹⁵` |
| **0.1%** (`0.001`) | 14.35 | 10 | 7.18 МБ | 1.79 МБ | `≈ 1.37 × 10⁻¹⁵` |
| **0.01%** (`0.0001`) | 19.14 | 13 | 9.57 МБ | 2.39 МБ | `≈ 1.37 × 10⁻¹⁵` |

---

## 11. Наскрізний приклад використання (Full Lifecycle Example)

Нижче продемонстровано повний цикл роботи з фільтром: ініціалізація, додавання ключів, перевірка, видалення та серіалізація:

:::tabs
```c
#include <stdio.h>
#include <string.h>

void demo_cbf_lifecycle(void) {
    /* 1. Розрахунок параметрів для 100 000 ключів із похибкою 1% */
    size_t cap = cbf_optimal_capacity(100000, 0.01);
    uint32_t k = cbf_optimal_hashes(cap, 100000);

    /* 2. Створення фільтра */
    CountingBloomFilter *filter = cbf_create(cap, k);
    if (!filter) return;

    /* 3. Додавання ключів */
    const char *key1 = "session_token_xyz_998";
    cbf_insert(filter, key1, strlen(key1));

    /* 4. Перевірка наявності */
    if (cbf_contains(filter, key1, strlen(key1))) {
        printf("Ключ знайдено!\n");
    }

    /* 5. Видалення ключа */
    cbf_remove(filter, key1, strlen(key1));

    /* 6. Звільнення пам'яті */
    cbf_destroy(filter);
}
```
```cpp
#include <iostream>
#include <string_view>

void demoCbfLifecycle() {
    // 1. Розрахунок параметрів для 100 000 ключів із похибкою 1%
    size_t cap = CountingBloomFilter::optimalCapacity(100'000, 0.01);
    uint32_t k = CountingBloomFilter::optimalHashes(cap, 100'000);

    // 2. Створення фільтра (RAII)
    CountingBloomFilter filter(cap, k);

    // 3. Додавання ключів
    std::string_view key1 = "session_token_xyz_998";
    filter.insert(key1);

    // 4. Перевірка наявності
    if (filter.contains(key1)) {
        std::cout << "Ключ знайдено!\n";
    }

    // 5. Видалення ключа
    filter.remove(key1);
}
```
:::

---

## 12. Практичні рецепти використання API

### Рецепт 1: Фільтр допуску в кеш (Cache Admission Filter)

Підрахунковий фільтр Блума ефективно захищає дорогий SSD/NVMe-кеш від запису одноразових об'єктів (One-Hit Wonders):

:::tabs
```c
/* Приклад логіки допуску на C */
bool should_admit_to_cache(CountingBloomFilter *filter, const char *url, size_t len) {
    if (cbf_contains(filter, url, len)) {
        /* Об'єкт запитується повторно -> допускаємо у постійний кеш */
        return true;
    }
    /* Перший запит -> реєструємо у фільтрі, але у кеш не записуємо */
    cbf_insert(filter, url, len);
    return false;
}
```
```cpp
// Приклад логіки допуску на C++
bool shouldAdmitToCache(CountingBloomFilter& filter, std::string_view url) {
    if (filter.contains(url)) {
        return true; // Повторний запит -> допускаємо у кеш
    }
    filter.insert(url); // Перший запит -> запам'ятовуємо у фільтрі
    return false;
}
```
:::

### Рецепт 2: Відстеження активних мережевих сесій

:::tabs
```c
/* Видалення сесії після закриття TCP FIN/RST */
void on_tcp_connection_closed(CountingBloomFilter *active_flows, const void *flow_key, size_t key_len) {
    cbf_remove(active_flows, flow_key, key_len);
}
```
```cpp
// Видалення сесії після закриття TCP FIN/RST
void onTcpConnectionClosed(CountingBloomFilter& activeFlows, std::string_view flowKey) {
    activeFlows.remove(flowKey);
}
```
:::

---

## 13. Обробка помилок та стратегія моніторингу насичення

При розробці високонадійних сервісів застосовують такі правила моніторингу:
1. **Відстеження частки насичених комірок**:
   Якщо метрика `saturated_counters / total_counters` перевищує `0.001%` (10⁻⁵), це свідчить про наявність важких колізій або нерівномірний розподіл вхідних ключів.
2. **Планова перебудова (Periodic Rebuilding)**:
   Для повного усунення накопичених заморожених комірок система може виконувати фонову генерацію нового екземпляра CBF із первинного сховища даних за схемою подвійної буферизації (Double Buffering) без зупинки основного сервісу.
3. **Коректність операцій видалення**:
   Будь-який виклик `remove()` повинен бути суворо узгоджений із транзакційним журналом або первинною базою даних для унеможливлення помилкового видалення неіснуючих записів.

---

## 14. Сумісність із санітайзерами пам'яті (ASan / TSan / MSan)

* **AddressSanitizer (ASan)**: Буфер лічильників виділяється суцільним блоком, тому побітові операції над ніблями не генерують помилок виходу за межі пам'яті (Heap Buffer Overflow), за умови дотримання границі `byte_size`.
* **ThreadSanitizer (TSan)**: При одночасній модифікації лічильників `2i` та `2i + 1` у неатомарному режимі TSan коректно фіксує Data Race на рівні спільного байта. Для усунення попереджень TSan у багатопотокових тестах слід використовувати атомарний інтерфейс (`cbf_insert_atomic`) або блокування м'ютексами.
* **MemorySanitizer (MSan)**: Оскільки `cbf_create` використовує `calloc` (або `memset(0)`), усі біти ініціалізуються нулями, що виключає хибні спрацьовування на невизначені значення.

---

## 15. Безпека у контексті переривань та обробників сигналів (Signal Safety)

Функції модифікації підрахункового фільтра Блума (`cbf_insert`, `cbf_remove`, `cbf_clear`) **не є безпечними для виклику в асинхронних обробниках сигналів POSIX (Not Async-Signal-Safe)**. Оскільки модифікація 4-бітного нібла вимагає неатомарної послідовності дій «читання-маска-запис», виклик цих функцій під час обробки сигналу `SIGINT` або `SIGTERM` може перервати виконання основного потоку на середині оновлення байта і призвести до невідновного пошкодження лічильників пам'яті.

---

## 16. Гарантії потокобезпеки (Thread Safety Contract)

* **Паралельне читання (Concurrent Readers)**: Функції `cbf_contains`, `cbf_get_counter`, `cbf_is_saturated` та константні методи C++ є повністю потокобезпечними для одночасного виклику з довільної кількості потоків виконання без блокувань (Lock-Free Read).
* **Паралельний запис (Concurrent Writers)**: Одночасний виклик `cbf_insert` або `cbf_remove` з кількох потоків **вимагає зовнішньої синхронізації** (наприклад, через `std::mutex` чи `pthread_mutex_t`), оскільки паралельна модифікація сусідніх ніблів в одному байті пам'яті призводить до неатомарного стану гонки (Bit Tearing).
* **Секціонована безпека**: Якщо екземпляр фільтра розбито на `S` незалежних секцій (Sharded CBF), паралельні потоки можуть модифікувати різні секції одночасно без взаємного блокування.

---

## 17. Бінарна сумісність C ABI та динамічне зв'язування

Бібліотека експортує чисті C-символи з угодою про виклики `cdecl` (або `stdcall` на Windows при відповідній конфігурації), що забезпечує пряму інтеграцію через FFI (Foreign Function Interface) у такі мови програмування:
* **Rust**: `libc::c_void`, `bindgen` безпосередньо генерує безпечні обгортки.
* **Python**: сумісність із модулями `ctypes` та `cffi`.
* **Go**: прямий виклик через пакет `CGO`.

Для уникнення колізій імен у великих проектах усі функції мають глобальний префікс `cbf_`, а структури визначені як непрозорі вказівники (Opaque Pointers), що дозволяє змінювати внутрішнє представлення пам'яті бібліотеки без порушення двійкової сумісності (ABI Stability).
