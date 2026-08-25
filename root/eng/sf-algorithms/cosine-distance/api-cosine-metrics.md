# 📋 Інтерфейс та C/C++ API векторних метрик

Цей документ визначає публічний програмний інтерфейс (API) та контракти бібліотеки векторних метрик для високонавантажених обчислювальних систем, векторних баз даних (Milvus, Qdrant, FAISS) та інфраструктур машинного навчання. Інтерфейс охоплює процедури обчислення косинусної відстані для щільних (Dense) та розріджених (Sparse) векторів, пакетну обробку матриць векторів (Batch Query-to-Matrix) та процедури L2-нормалізації.

## 1. Архітектурні принципи та контракти виклику

Програмний інтерфейс бібліотеки розроблено з дотриманням п'яти фундаментальних інженерних принципів, які забезпечують максимальну продуктивність та інтегровність у високомасштабовані системи:

1. **Нульове динамічне виділення пам'яті (Zero Heap Allocation):** Жодна з функцій API під час виконання обчислень не викликає процедури динамічного виділення пам'яті (`malloc`, `free`, `operator new`). Усі обчислення виконуються або у векторних регістрах процесора, або у стекових фреймах, або у заздалегідь виділених буферах пам'яті, що передаються клієнтом. Це повністю виключає фрагментацію пам'яті та паузи латентності, пов'язані з аллокатором.
2. **Абсолютна багатопотокова безпека (Thread Safety & Statelessness):** Усі функції є повністю чистими (Pure Functions) та безстатусними (Stateless). Вони не чіпають глобальних або статичних змінних. Ті самі матриці векторів індексу можна безпечно читати одночасно з необмеженої кількості робочих потоків у багатоядерних та NUMA-системах.
3. **Строга вимірність та тип даних:** Обчислення виконуються над дійсними числами з плаваючою комою одинарної точності `float` (32 біти, IEEE 754). Вимірності векторів `d` вимагаються якогось конкретного однакового розміру.
4. **Сумісність із масивами та вирівнювання (Memory Alignment):** Для досягнення пікової швидкості SIMD-інструкцій (AVX2 / AVX-512) буфери пам'яті векторів повинні бути вирівняні за межею 32 байти (для AVX2) або 64 байти (для AVX-512). Якщо дані передаються з невирівняної пам'яті, бібліотека виконує виклики через інструкції неформатованого завантаження (`_mm256_loadu_ps`), гарантуючи відсутність помилок сегментації (Segmentation Fault).
5. **Явна обробка виняткових станів:** Функції API не генерують C++ винятків (Noexcept contract) та не викликають апаратних переривань при зіткненні з некоректними даними (нульові вектори, порожні масиви, значення `NaN`). Замість цього кожна функція повертає чітко кодифікований статус виконання.

## 2. Публічний інтерфейс мовою C

Нижче наведено вміст заголовкового файла `vector_metrics.h`, який визначає C-інтерфейс бібліотеки.

:::tabs
```c
#ifndef VECTOR_METRICS_H
#define VECTOR_METRICS_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Коди результатів виконання операцій векторних метрик.
 */
typedef enum {
    METRICS_SUCCESS              =  0,  /**< Успішне виконання операції */
    METRICS_ERROR_NULL_POINTER    = -1,  /**< Передано нулевий вказівник */
    METRICS_ERROR_INVALID_SIZE   = -2,  /**< Некоректна вимірність (size == 0) */
    METRICS_ERROR_SIZE_MISMATCH  = -3,  /**< Вимірності векторів не збігаються */
    METRICS_ERROR_ZERO_NORM      = -4,  /**< Вектор має нульову норму (||v|| < eps) */
    METRICS_ERROR_UNALIGNED_DATA = -5   /**< Дані не вирівняні під вимоги SIMD */
} MetricsStatus;

/**
 * @brief Структура для представлення розрідженого вектора у форматі Compressed Sparse.
 */
typedef struct {
    const size_t *indices;  /**< Посортований масив індексів ненульових елементів */
    const float  *values;   /**< Масив відповідних ненульових значень */
    size_t        nnz;      /**< Кількість ненульових елементів (Number of Non-Zeroes) */
} SparseVector;

/**
 * @brief Опції для конфігурації векторних обчислень.
 */
typedef struct {
    bool use_simd;          /**< Дозволити апаратне SIMD-прискорення (AVX2/NEON) */
    bool assume_normalized; /**< Прапорець: вважати вектори вже L2-нормалізованими */
    float zero_eps;         /**< Епсілон для перевірки ділення на нуль (за замовчуванням 1e-12f) */
} MetricsOptions;

/**
 * @brief Повертає дефолтні налаштування обчислень.
 */
MetricsOptions metrics_options_default(void);

/**
 * @brief Обчислює косинусну відстань між двома щільними векторами.
 *
 * @param[in]  u        Вказівник на перший вектор
 * @param[in]  v        Вказівник на другий вектор
 * @param[in]  size     Вимірність векторів (кількість елементів float)
 * @param[out] out_dist Вказівник для запису обчисленої відстані d_cos ∈ [0.0, 2.0]
 * @return MetricsStatus Код стану виконання
 */
MetricsStatus metrics_cosine_distance_dense(
    const float *u,
    const float *v,
    size_t size,
    float *out_dist
);

/**
 * @brief Обчислює косинусну відстань із додатковими опціями.
 */
MetricsStatus metrics_cosine_distance_dense_ext(
    const float *u,
    const float *v,
    size_t size,
    const MetricsOptions *opts,
    float *out_dist
);

/**
 * @brief Пакетне обчислення косинусної відстані від один запиту до N векторів матриці.
 *
 * @param[in]  query       Вектор запиту вимірності dim
 * @param[in]  matrix      Матриця векторів розміром [num_vectors x dim] у суцільній пам'яті
 * @param[in]  num_vectors Кількість векторів у матриці
 * @param[in]  dim         Вимірність кожного вектора
 * @param[out] out_dists   Масив розміром num_vectors для запису результатів
 * @return MetricsStatus Код стану виконання
 */
MetricsStatus metrics_cosine_distance_batch(
    const float *query,
    const float *matrix,
    size_t num_vectors,
    size_t dim,
    float *out_dists
);

/**
 * @brief Обчислює косинусну відстань між двома розрідженими векторами.
 */
MetricsStatus metrics_cosine_distance_sparse(
    const SparseVector *u,
    const SparseVector *v,
    float *out_dist
);

/**
 * @brief Виконує L2-нормалізацію вектора inplace: u = u / ||u||.
 *
 * @param[in,out] vector Вказівник на вектор
 * @param[in]     size   Вимірність вектора
 * @return MetricsStatus METRICS_SUCCESS або METRICS_ERROR_ZERO_NORM
 */
MetricsStatus metrics_l2_normalize(
    float *vector,
    size_t size
);

#ifdef __cplusplus
}
#endif

#endif /* VECTOR_METRICS_H */
```
```cpp
#ifndef VECTOR_METRICS_HPP
#define VECTOR_METRICS_HPP

#include <span>
#include <vector>
#include <expected>
#include <cstddef>
#include <cstdint>

namespace metrics {

/**
 * @brief Перелічуваний клас помилок векторного API у C++.
 */
enum class Status : int32_t {
    Success            =  0,
    NullPointer        = -1,
    InvalidSize        = -2,
    SizeMismatch       = -3,
    ZeroNorm           = -4,
    UnalignedData      = -5
};

/**
 * @brief Елемент розрідженого вектора (індекс-значення).
 */
struct SparseEntry {
    std::size_t index;
    float value;
};

/**
 * @brief Налаштування обчислення метрик.
 */
struct Options {
    bool use_simd{true};
    bool assume_normalized{false};
    float zero_eps{1e-12f};
};

/**
 * @brief Головний клас-сервіс для обчислення векторних метрик.
 */
class VectorMetrics {
public:
    VectorMetrics() = delete;

    /**
     * @brief Обчислює косинусну відстань між двома щільними векторами.
     * @param u Перший вектор
     * @param v Другий вектор
     * @param opts Додаткові опції обчислення
     * @return std::expected з обчисленою відстанню d_cos або кодом помилки Status
     */
    [[nodiscard]] static std::expected<float, Status> cosineDistance(
        std::span<const float> u,
        std::span<const float> v,
        const Options& opts = Options{}
    ) noexcept;

    /**
     * @brief Пакетне обчислення відстаней від запиту до матриці векторів.
     * @param query Вектор запиту (розмір dim)
     * @param matrix Суцільний масив векторів індексу (розмір num_vectors * dim)
     * @param num_vectors Кількість векторів
     * @param dim Вимірність
     * @param out_dists Буфер для запису результатів (розмір num_vectors)
     * @param opts Опції
     * @return Status::Success або відповідний код помилки
     */
    static Status cosineDistanceBatch(
        std::span<const float> query,
        std::span<const float> matrix,
        std::size_t num_vectors,
        std::size_t dim,
        std::span<float> out_dists,
        const Options& opts = Options{}
    ) noexcept;

    /**
     * @brief Обчислює косинусну відстань між розрідженими векторами.
     */
    [[nodiscard]] static std::expected<float, Status> cosineDistanceSparse(
        std::span<const SparseEntry> u,
        std::span<const SparseEntry> v,
        const Options& opts = Options{}
    ) noexcept;

    /**
     * @brief Нормалізує вектор inplace за нормою L2.
     */
    static Status l2Normalize(
        std::span<float> vector,
        float eps = 1e-12f
    ) noexcept;
};

} // namespace metrics

#endif // VECTOR_METRICS_HPP
```
:::

## 3. Деталізація функцій та семантика аргументів

Розглянемо специфікацію та семантичні контракти кожної викликуваної процедури API.

### `metrics_cosine_distance_dense` (Поелементна косинусна відстань)
Призначена для обчислення косинусної відстані між двома щільними векторами.
- **Аргументи:**
  - `u`: Вказівник на перший масив `float`. Не повинен бути `NULL`.
  - `v`: Вказівник на другий масив `float`. Не повинен бути `NULL`.
  - `size`: Довжина векторів у елементах. Повинна бути більше 0.
  - `out_dist`: Вказівник на змінну `float`, куди буде записано результат.
- **Повертане значення:**
  - `METRICS_SUCCESS` (0): Обчислення пройшло успішно, результат лежить у діапазоні `[0.0, 2.0]`.
  - `METRICS_ERROR_NULL_POINTER` (-1): Один із вказівників дорівнює `NULL`.
  - `METRICS_ERROR_INVALID_SIZE` (-2): Передано `size == 0`.
  - `METRICS_ERROR_ZERO_NORM` (-4): Один із векторів має евклідову норму `||v|| < zero_eps`. У змінну `*out_dist` записується дефолтне значення `1.0f`.

### `metrics_cosine_distance_batch` (Пакетний пошук у матриці)
Оптимізована функція для векторних баз даних та пошукових систем. Вона обчислює відстані від одного вектора запиту `query` до `num_vectors` векторів, збережених у суцільному масиві `matrix` розміром `[num_vectors × dim]`.
- **Організація пам'яті:** Матриця повинна розкладатися за рядками (Row-Major Layout), де вектор з індексом `k` займає елементи від `matrix[k * dim]` до `matrix[(k + 1) * dim - 1]`.
- **Перевага пакетної обробки:** Завдяки локальності даних у L1/L2 кеші процесора вектор запиту `query` завантажується у векторні регістри CPU **один раз** і залишається там під час порівняння з десятками векторів матриці. Це зменшує навантаження на шину RAM та піднімає продуктивність обробки у 3–8 разів порівняно з послідовними поодинокими викликами.

### `metrics_cosine_distance_sparse` (Обробка розріджених векторів)
Призначена для роботи зі структурою `SparseVector` (формат CSR/COO).
- **Вимоги до даних:** Масив `indices` повинен бути **строго посортованим за зростанням** (`indices[0] < indices[1] < ... < indices[nnz-1]`). Це дозволяє застосовувати двопокажчиковий алгоритм перетину за лінійний час `O(nnz_u + nnz_v)`. Якщо масиви не посортовані, обчислення буде некоректним.

### `metrics_l2_normalize` (Векторна нормалізація)
Виконує модифікацію вектора на місці (Inplace): `v = v / ||v||`.
- **Семантика:** Після виконання нормалізації евклідова норма вектора стає строго `||v|| = 1.0f`. Це готує вектор до надшвидкісного обчислення косинусної відстані через скалярний добуток `d_cos = 1.0f - (u · v)`.

## 4. Таблиця кодифікації результатів та виняткових станів

У наступній таблиці зведено коди відповідей API, їхній математичний зміст та рекомендовану стратегію обробки у клієнтському коді:

| Код стану (C) | Код стану (C++) | Опис умови виникнення | Дія системи |
| :--- | :--- | :--- | :--- |
| `METRICS_SUCCESS` | `Status::Success` | Операцію виконано успішно, значення в межах `[0.0, 2.0]` | Повернути обчислене значення клієнту |
| `METRICS_ERROR_NULL_POINTER` | `Status::NullPointer` | Передано `NULL` або порожній `std::span` | Логувати помилку, відхилити виклик |
| `METRICS_ERROR_INVALID_SIZE` | `Status::InvalidSize` | Передано вимірність `size == 0` | Повернути помилку валідації аргументів |
| `METRICS_ERROR_SIZE_MISMATCH` | `Status::SizeMismatch` | Довжина вектора `u` не дорівнює довжині `v` | Зупинити обробку, виклики неузгоджені |
| `METRICS_ERROR_ZERO_NORM` | `Status::ZeroNorm` | Норма вектора `\|\|u\|\| < eps` (нульовий вектор) | Повернути дефолтну відстань 1.0 або обробити окремо |
| `METRICS_ERROR_UNALIGNED_DATA` | `Status::UnalignedData` | Увімкнено строге вирівнювання, але адреса не 32/64 byte | Перейти на скалярний фолбек або видати помилку |

## 5. Контракти безпеки пам'яті, багатопотоковості та FFI

1. **Багатопотокова безпека (Thread Safety):** Усі функції обчислення метрик є **чистими функціями (Pure Functions)**. Вони не читають і не модифікують глобальний або статичний стан. Одну й ту саму матрицю індексу можна безпечно читати одночасно з багатьох робочих потоків (Thread-Safe Concurrent Read).
2. **Гарантії відсутності витоків пам'яті:** Жодна з функцій C або C++ API не виконує динамічного виділення пам'яті на купі (`malloc` / `operator new`) під час виконання обчислень. Усі робочі регістри та буфери є або стековими, або передаються клієнтом через вихідні масиви (`out_dists`).
3. **FFI-інтеграція з іншими мовами (Python, Rust, Go):** Завдяки дотриманню стандарту ABI мови C, створена бібліотека `libvector_metrics.so` / `vector_metrics.dll` легко інтегрується у вищорівневі мови програмування без втрати продуктивності (NumPy / PyBind11 у Python, `bindgen` у Rust, `cgo` у Go).

## 6. Рекомендації щодо продуктивності та вирівнювання пам'яті

Для досягнення максимальної пропускної здатності на процесорах із підтримкою AVX2 або AVX-512 рекомендується дотримуватися таких практичних правил виклику:
- **Пакетні виклики:** Завжди віддавати перевагу виклику `metrics_cosine_distance_batch` замість серії послідовних викликів `metrics_cosine_distance_dense`, оскільки це мінімізує кількість інструкцій перезавантаження вектора запиту у YMM-регістри.
- **Попередня нормалізація:** Якщо вектори додаються у базу даних один раз, а шукаються мільйони разів, викликайте `metrics_l2_normalize` під час індексації. Це дозволяє вмикати прапорець `assume_normalized = true` у `MetricsOptions` та прискорювати обчислення удвічі.
- **Вирівнювання пам'яті:** Використовуйте функції системного виділення пам'яті з вирівнюванням `posix_memalign(&ptr, 32, size * sizeof(float))` або `std::aligned_alloc(32, size * sizeof(float))`.
