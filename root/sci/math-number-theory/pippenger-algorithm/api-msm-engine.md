# 📋 Специфікація та API високоефективного рушія MSM

Інтерфейс рушія мультискалярного множення (англ. *MSM Engine API*) визначає низькорівневий та високорівневий програмний контракт для виконання великомасштабних лінійних комбінацій точок еліптичних кривих `Q = ∑_{i=1}^n k_i P_i`. Рушій оптимізований для криптографічних протоколів нульового розголошення (zk-SNARKs, Groth16, PLONK, Halo2, Nova) та схем поліноміальних зобов'язань KZG на еліптичних кривих BN254, BLS12-381 та secp256k1.

Специфікація стандартизує бінарні структури представлення точок та скалярів у пам'яті, конфігурацію конвеєрів паралелізації, керування пам'яттю кошиків через арена-алокатори, контракти асинхронного виконання, двійкову серіалізацію, GLV-декомпозицію, обчислення з фіксованим базисом, пакетний мульти-MSM, телеметрію, оракульне тестування, інтеграцію з EVM precompiles, відображення Hugepages, FFI-зв'язування та апаратні бекенди (векторизація AVX-512 та прискорення NVIDIA CUDA).

## 1. Заголовні файли та базові типи даних

Вхідні та вихідні дані задаються у двійковому форматі, оптимізованому для прямого відображення у пам'яті (англ. *zero-copy memory layout*) та сумісному зі стандартами EIP-196 (BN254) та EIP-2537 (BLS12-381).

Усі 256-бітні та 384-бітні числа представляються масивами 64-бітних цілих чисел без знака у форматі Little-Endian:
* Елементи базового поля `F_p` зберігаються у канонічній формі Монтгомері `x̃ = x · R \pmod p`, де `R = 2^{256} \pmod p`.
* Скаляри з поля порядку групи `F_r` зберігаються у стандартному позиційному двійковому форматі або у формі Монтгомері (залежно від прапорця конфігурації).

:::tabs
```c
#ifndef MSM_ENGINE_H
#define MSM_ENGINE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди помилок виконання операцій MSM */
typedef enum {
    MSM_SUCCESS             =  0,  /* Успішне завершення обчислення */
    MSM_ERR_NULL_PTR        = -1,  /* Передано нульовий вказівник */
    MSM_ERR_INVALID_SIZE    = -2,  /* Некоректний розмір масиву (n == 0 або невідповідність довжин) */
    MSM_ERR_OUT_OF_MEMORY   = -3,  /* Недостатньо оперативної пам'яті для розміщення кошиків */
    MSM_ERR_INVALID_CURVE   = -4,  /* Непідтримуваний ідентифікатор еліптичної кривої */
    MSM_ERR_POINT_NOT_ON_EC = -5,  /* Вхідна точка не задовольняє рівняння кривої */
    MSM_ERR_BACKEND_FAILED  = -6,  /* Збій апаратного прискорювача (CUDA error / OpenCL error) */
    MSM_ERR_INVALID_CONFIG  = -7   /* Некоректні параметри конфігурації (неприпустима ширина вікна) */
} msm_status_t;

/* Ідентифікатор підтримуваних еліптичних кривих */
typedef enum {
    MSM_CURVE_BN254     = 1,   /* Крива BN254 (alt_bn128, Ethereum) */
    MSM_CURVE_BLS12_381 = 2,   /* Крива BLS12-381 (Zcash, Filecoin, Ethereum 2.0) */
    MSM_CURVE_SECP256K1 = 3    /* Крива secp256k1 (Bitcoin, EVM precompiles) */
} msm_curve_id_t;

/* Тип обчислювального бекенду */
typedef enum {
    MSM_BACKEND_CPU_SCALAR  = 0,  /* Базовий скалярний CPU-рушій (сумісний з будь-якою архітектурою) */
    MSM_BACKEND_CPU_AVX512  = 1,  /* Векторизований CPU-рушій AVX-512 IFMA (52-бітне множення) */
    MSM_BACKEND_GPU_CUDA    = 2   /* Графічний прискорювач NVIDIA CUDA */
} msm_backend_t;

/* 256-бітний елемент поля у формі Монтгомері (4 слова по 64 біти) */
typedef struct {
    uint64_t limbs[4];
} msm_fe256_t;

/* Точка еліптичної кривої в афінних координатах (x, y) */
typedef struct {
    msm_fe256_t x;
    msm_fe256_t y;
    bool is_infinity;
} msm_point_affine_t;

/* Проективна точка в координатах Якобі (X, Y, Z), де x = X/Z^2, y = Y/Z^3 */
typedef struct {
    msm_fe256_t X;
    msm_fe256_t Y;
    msm_fe256_t Z;
} msm_point_jacobian_t;

/* Конфігурація параметрів виконання MSM */
typedef struct {
    msm_curve_id_t curve;      /* Використовувана еліптична крива */
    msm_backend_t backend;     /* Обраний обчислювальний бекенд */
    uint32_t window_size;      /* Ширина вікна c (0 = автоматичний вибір за розміром n) */
    uint32_t num_threads;      /* Кількість паралельних потоків (0 = auto / CPU cores) */
    bool use_signed_digits;    /* Використовувати знакове wNAF-розбиття (зменшує кошики удвічі) */
    bool enable_radix_sort;    /* Увімкнути порозрядне групування точок для оптимізації кешу */
    void *custom_arena_buffer; /* Попередньо виділена пам'ять для кошиків (опціонально) */
    size_t custom_arena_size;  /* Розмір буфера арени у байтах */
} msm_config_t;

#ifdef __cplusplus
}
#endif

#endif /* MSM_ENGINE_H */
```
```cpp
#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <memory>
#include <expected>
#include <string_view>
#include <vector>
#include <future>

namespace msm {

/* Коди результатів та помилок MSM */
enum class Status : int32_t {
    Success           =  0,
    NullPointer       = -1,
    InvalidSize       = -2,
    OutOfMemory       = -3,
    InvalidCurve      = -4,
    PointNotOnCurve   = -5,
    BackendFailed     = -6,
    InvalidConfig     = -7
};

/* Підтримувані криві */
enum class CurveId : uint32_t {
    BN254     = 1,
    BLS12_381 = 2,
    Secp256k1 = 3
};

/* Апаратні бекенди */
enum class Backend : uint32_t {
    CpuScalar = 0,
    CpuAvx512 = 1,
    GpuCuda   = 2
};

/* 256-бітний елемент поля */
struct FieldElement256 {
    std::array<uint64_t, 4> limbs{};

    [[nodiscard]] constexpr bool is_zero() const noexcept {
        return (limbs[0] | limbs[1] | limbs[2] | limbs[3]) == 0;
    }
};

/* Афінна точка (x, y) */
struct PointAffine {
    FieldElement256 x{};
    FieldElement256 y{};
    bool is_infinity{true};

    static constexpr PointAffine infinity() noexcept {
        return PointAffine{{}, {}, true};
    }
};

/* Проективна точка в координатах Якобі (X, Y, Z) */
struct PointJacobian {
    FieldElement256 X{};
    FieldElement256 Y{};
    FieldElement256 Z{};

    [[nodiscard]] bool is_infinity() const noexcept {
        return Z.is_zero();
    }

    static constexpr PointJacobian infinity() noexcept {
        return PointJacobian{{}, {}, {}};
    }
};

/* Конфігураційний дескриптор рушія MSM */
struct Config {
    CurveId curve{CurveId::BN254};
    Backend backend{Backend::CpuScalar};
    uint32_t window_size{0};       // 0 = автоматичний розрахунок оптимального c
    uint32_t num_threads{0};       // 0 = апаратний максимум апаратних потоків
    bool use_signed_digits{true};  // Зменшує кількість кошиків удвічі
    bool enable_radix_sort{true};  // Оптимізація локальності L3-кешу процесора
    std::span<uint8_t> arena_buffer{};
};

} // namespace msm
```
:::

## 2. Специфікація функцій ядра MSM

API ядра надає повний набір функцій для ініціалізації конфігурації за замовчуванням, розрахунку вимог до оперативної пам'яті, синхронного обчислення лінійної комбінації та пакетної конвертації проміжних результатів.

### Сигнатури та опис інтерфейсу

Функція `msm_calculate_arena_size` повертає мінімальну кількість байтів, необхідну для виділення масивів кошиків `B_u` з урахуванням кількості паралельних потоків та ширини вікна:

```
ArenaSize = num_threads · (2^{c − 1} · sizeof(point_jacobian_t)) + Padding
```

Функція `msm_execute` є головною точкою входу. Вона валідує вхідні вказівники, автоматично підбирає ширину вікна `c` (якщо передано `window_size == 0`), розподіляє обчислення між потоками пулу, виконує зворотне накопичення та повертає точку в координатах Якобі.

:::tabs
```c
/**
 * Ініціалізація структури конфігурації значеннями за замовчуванням.
 * @param config Вказівник на структуру конфігурації.
 * @param curve  Ідентифікатор еліптичної кривої.
 */
void msm_config_init_default(msm_config_t *config, msm_curve_id_t curve);

/**
 * Розрахунок мінімального обсягу пам'яті арени для обробки n точок.
 * @param config Вказівник на конфігурацію.
 * @param n      Кількість вхідних точок.
 * @return Необхідний розмір буфера у байтах.
 */
size_t msm_calculate_arena_size(const msm_config_t *config, size_t n);

/**
 * Головна функція обчислення мультискалярного множення:
 * result = sum_{i=0}^{n-1} scalars[i] * points[i]
 *
 * @param result  Вказівник на вихідну точку в координатах Якобі.
 * @param points  Масив вхідних афінних точок базису розміром n.
 * @param scalars Масив 256-бітних скалярів розміром n.
 * @param n       Кількість пар (точка, скаляр).
 * @param config  Вказівник на параметри запуску (може бути NULL для дефолтних налаштувань).
 * @return Статус виконання (MSM_SUCCESS у разі успіху).
 */
msm_status_t msm_execute(
    msm_point_jacobian_t *result,
    const msm_point_affine_t *points,
    const msm_fe256_t *scalars,
    size_t n,
    const msm_config_t *config
);

/**
 * Пакетна конвертація масиву точок з координат Якобі в афінні координати
 * з використанням алгоритму Монтгомері (одна інверсія в полі).
 *
 * @param out_affine  Масив вихідних афінних точок розміром count.
 * @param in_jacobian Масив вхідних проективних точок розміром count.
 * @param count       Кількість конвертованих точок.
 * @param curve       Ідентифікатор кривої.
 * @return Статус виконання.
 */
msm_status_t msm_batch_to_affine(
    msm_point_affine_t *out_affine,
    const msm_point_jacobian_t *in_jacobian,
    size_t count,
    msm_curve_id_t curve
);
```
```cpp
namespace msm {

/**
 * Розрахунок мінімального обсягу пам'яті арени для заданого розміру задачі.
 */
[[nodiscard]] size_t calculate_arena_size(const Config& config, size_t n) noexcept;

/**
 * Високорівневий інтерфейс обчислення MSM за алгоритмом Піппенджера.
 *
 * @param points  Вхідний масив афінних точок базису.
 * @param scalars Вхідний масив скалярів однакової розмірності.
 * @param config  Конфігураційні параметри рушія.
 * @return Результуюча точка або код помилки (std::expected).
 */
[[nodiscard]] std::expected<PointJacobian, Status> execute(
    std::span<const PointAffine> points,
    std::span<const FieldElement256> scalars,
    const Config& config = Config{}
);

/**
 * Пакетне перетворення точок з координат Якобі в афінні координати.
 */
[[nodiscard]] std::expected<std::vector<PointAffine>, Status> batch_to_affine(
    std::span<const PointJacobian> in_jacobian,
    CurveId curve = CurveId::BN254
);

} // namespace msm
```
:::

## 3. Асинхронний інтерфейс та черга завдань

Для високонавантажених серверів прувінгу (ZK-Proof Generators) та конвеєризованої генерації доведень у фоновому режимі рушій надає асинхронний неблокуючий інтерфейс на основі черги завдань.

Користувач ініціалізує контекст черги `msm_async_queue_t`, відправляє завдання через `msm_async_submit` і отримує дескриптор `msm_task_handle_t`. Очікування завершення виконується через `msm_async_wait` або опитування статусу через `msm_async_poll`.

:::tabs
```c
/* Дескриптор асинхронної черги обчислень */
typedef struct msm_async_queue msm_async_queue_t;

/* Дескриптор асинхронного завдання */
typedef struct msm_task_handle msm_task_handle_t;

/**
 * Створення черги асинхронних завдань MSM.
 * @param num_workers Кількість фонових робочих потоків.
 * @return Вказівник на створену чергу або NULL у разі помилки.
 */
msm_async_queue_t* msm_async_queue_create(uint32_t num_workers);

/**
 * Відправка завдання MSM у неблокуючу чергу обчислень.
 */
msm_task_handle_t* msm_async_submit(
    msm_async_queue_t *queue,
    msm_point_jacobian_t *result,
    const msm_point_affine_t *points,
    const msm_fe256_t *scalars,
    size_t n,
    const msm_config_t *config
);

/**
 * Очікування завершення асинхронного завдання (блокуючий виклик).
 */
msm_status_t msm_async_wait(msm_task_handle_t *task);

/**
 * Неблокуюча перевірка готовності завдання.
 * @return true, якщо обчислення завершено.
 */
bool msm_async_poll(msm_task_handle_t *task);

/**
 * Знищення черги завдань та вивільнення ресурсів.
 */
void msm_async_queue_destroy(msm_async_queue_t *queue);
```
```cpp
namespace msm {

/* Неблокуюча черга завдань обчислення MSM */
class AsyncQueue {
public:
    explicit AsyncQueue(uint32_t num_workers = std::thread::hardware_concurrency());
    ~AsyncQueue();

    AsyncQueue(const AsyncQueue&) = delete;
    AsyncQueue& operator=(const AsyncQueue&) = delete;

    AsyncQueue(AsyncQueue&&) noexcept = default;
    AsyncQueue& operator=(AsyncQueue&&) noexcept = default;

    /**
     * Відправка асинхронного завдання, що повертає std::future.
     */
    [[nodiscard]] std::future<std::expected<PointJacobian, Status>> submit(
        std::span<const PointAffine> points,
        std::span<const FieldElement256> scalars,
        Config config = Config{}
    );

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace msm
```
:::

## 4. Специфікація двійкової серіалізації та валідації точок

У криптографічних протоколах точки еліптичної кривої передаються мережею або зчитуються з файлів довідника (CRS, англ. *Common Reference String*) у двох стандартизованих форматах:

1. **Незжатий формат (Uncompressed Binary Format)**:
   - Для кривої BN254 займає 64 байти: 32 байти координати `x` у форматі Big-Endian та 32 байти координати `y`.
   - Для кривої BLS12-381 G1 займає 96 байтів: 48 байтів координати `x` та 48 байтів координати `y`.
2. **Стиснений формат (Compressed Binary Format)**:
   - Зберігає лише координату `x` та 3 бітові прапорці у старшому байті:
     - `0x80 (Compression Flag)`: 1, якщо точка збережена у стисненому форматі.
     - `0x40 (Infinity Flag)`: 1, якщо точка є точкою на нескінченності `O` (усі інші байти нульові).
     - `0x20 (Sign Flag / Sort Flag)`: 1, якщо координата `y` є більшою за `(p - 1) / 2` (визначає вибір знаку кореня при відновленні `y = ±sqrt(x³ + b)`).

:::tabs
```c
/* Формати двійкової серіалізації точок */
typedef enum {
    MSM_FORMAT_UNCOMPRESSED = 0,  /* Повний двійковий формат (x || y) */
    MSM_FORMAT_COMPRESSED   = 1   /* Стиснений формат (x + bit flags) */
} msm_serialization_format_t;

/**
 * Серіалізація точки еліптичної кривої у двійковий буфер.
 * @param out_bytes Буфер вихідних байтів (мінімум 64 або 32 байти для BN254).
 * @param point     Вхідна афінна точка.
 * @param format    Обраний формат серіалізації.
 * @param curve     Ідентифікатор кривої.
 */
msm_status_t msm_point_serialize(
    uint8_t *out_bytes,
    const msm_point_affine_t *point,
    msm_serialization_format_t format,
    msm_curve_id_t curve
);

/**
 * Десеріалізація та валідація точки з перевіркою належності підгрупі.
 */
msm_status_t msm_point_deserialize(
    msm_point_affine_t *point,
    const uint8_t *in_bytes,
    msm_serialization_format_t format,
    msm_curve_id_t curve
);
```
```cpp
namespace msm {

enum class SerializationFormat : uint32_t {
    Uncompressed = 0,
    Compressed   = 1
};

/**
 * Серіалізація афінної точки у вектор байтів.
 */
[[nodiscard]] std::expected<std::vector<uint8_t>, Status> serialize_point(
    const PointAffine& point,
    SerializationFormat format = SerializationFormat::Compressed,
    CurveId curve = CurveId::BN254
);

/**
 * Десеріалізація точки з перевіркою рівняння кривої.
 */
[[nodiscard]] std::expected<PointAffine, Status> deserialize_point(
    std::span<const uint8_t> in_bytes,
    SerializationFormat format = SerializationFormat::Compressed,
    CurveId curve = CurveId::BN254
);

} // namespace msm
```
:::

## 5. Таблиця конфігураційних параметрів та поведінка за замовчуванням

Параметри рушія керують балансом між використанням процесорного часу, паралелізмом та споживанням оперативної пам'яті:

| Поле конфігурації | Тип | За замовчуванням | Опис та допустимий діапазон значень |
| :--- | :--- | :--- | :--- |
| `curve` | `msm_curve_id_t` | `MSM_CURVE_BN254` | Визначає параметри кривої, модуль поля `p` та порядок підгрупи `r` |
| `backend` | `msm_backend_t` | `MSM_BACKEND_CPU_AVX512` | Обирає апаратний бекенд: скалярний CPU, векторизований AVX-512 або GPU |
| `window_size` | `uint32_t` | `0` (автовибір) | Ширина вікна `c ∈ [8, 20]`. При `0` обчислюється автоматично за розміром `n` |
| `num_threads` | `uint32_t` | `0` (автовибір) | Кількість паралельних потоків ОС. При `0` дорівнює кількості логічних ядер |
| `use_signed_digits` | `bool` | `true` | Вмикає знакове wNAF-розбиття скалярів (зменшує кількість кошиків удвічі) |
| `enable_radix_sort` | `bool` | `true` | Вмикає попереднє сортування за кошиками для усунення промахів L3-кешу |
| `custom_arena_buffer` | `void*` | `NULL` | Вказівник на попередньо виділений буфер арени пам'яті для пулу кошиків |
| `custom_arena_size` | `size_t` | `0` | Розмір буфера `custom_arena_buffer` у байтах |

## 6. Таблиця автоматичного вибору ширини вікна c та обсягу пам'яті

Якщо в конфігурації вказано `window_size = 0`, рушій обирає оптимальний параметр вікна `c` та обчислює кількість вікон `b = ⌈256 / c⌉` на основі аналітичної моделі складності Піппенджера:

| Діапазон розмірності `n` | Оптимальне вікно `c` | Кількість вікон `b` | Кількість кошиків на вікно | Пам'ять кошиків (Якобі) |
| :--- | :--- | :--- | :--- | :--- |
| `n < 4\,096` | `c = 10` бітів | `b = 26` вікон | `2⁹ = 512` кошиків | `49.1` КБ |
| `4\,096 ≤ n < 16\,384` | `c = 12` бітів | `b = 22` вікна | `2¹¹ = 2\,048` кошиків | `196.6` КБ |
| `16\,384 ≤ n < 65\,536` | `c = 13` бітів | `b = 20` вікон | `2¹² = 4\,096` кошиків | `393.2` КБ |
| `65\,536 ≤ n < 262\,144` | `c = 14` бітів | `b = 19` вікон | `2¹³ = 8\,192` кошики | `786.4` КБ |
| `262\,144 ≤ n < 1\,048\,576` | `c = 15` бітів | `b = 18` вікон | `2¹⁴ = 16\,384` кошики | `1.57` МБ |
| `1\,048\,576 ≤ n < 4\,194\,304` | `c = 16` бітів | `b = 16` вікон | `2¹⁵ = 32\,768` кошиків | `3.15` МБ |
| `n ≥ 4\,194\,304` | `c = 17` бітів | `b = 16` вікон | `2¹⁶ = 65\,536` кошиків | `6.29` МБ |

При паралельному виконанні на `T` потоках загальний обсяг пам'яті під кошики масштабується як `T · Пам'ять_кошиків`. Наприклад, для `n = 1\,048\,576` та 16 робочих потоків сумарний буфер арени складе `16 · 3.15 = 50.4` МБ.

## 7. Детальний опис кодів помилок та виняткових ситуацій

Кожен виклик API повертає детермінований числовий статус або `std::expected`:

1. `MSM_SUCCESS (0)`: Обчислення виконано коректно. Вихідна змінна `result` містить валідну точку еліптичної кривої.
2. `MSM_ERR_NULL_PTR (-1)`: Одному з обов'язкових аргументів (`result`, `points`, `scalars`) передано значення `NULL` (або порожній `std::span`).
3. `MSM_ERR_INVALID_SIZE (-2)`: Передано розмірність `n == 0` при очікуванні ненульового масиву або розмірності масивів `points` та `scalars` не збігаються.
4. `MSM_ERR_OUT_OF_MEMORY (-3)`: Системний алокатор або надана арена не змогли виділити необхідний обсяг пам'яті під масиви кошиків.
5. `MSM_ERR_INVALID_CURVE (-4)`: Вказано ідентифікатор кривої, не підтримуваний поточною компіляцією бібліотеки.
6. `MSM_ERR_POINT_NOT_ON_EC (-5)`: Перевірка валідності вхідних точок виявила точку, координати якої не задовольняють рівняння Вейєрштрасса `y² ≠ x³ + b \pmod p`.
7. `MSM_ERR_BACKEND_FAILED (-6)`: Апаратний прискорювач (GPU) повернув помилку виконання ядра CUDA або збій виділення пам'яті пристрою (CUDA Out of Memory).
8. `MSM_ERR_INVALID_CONFIG (-7)`: Вказано неприпустиму ширину вікна (наприклад, `window_size > 24`), яка призвела б до переповнення пам'яті.

## 8. Специфікація інтеграції GPU-прискорювача (NVIDIA CUDA)

При виборі бекенду `MSM_BACKEND_GPU_CUDA` рушій використовує асинхронний потік копіювання пам'яті та паралельні блоки ядер CUDA.

### Вимоги до розміщення даних у пам'яті GPU

1. **DMA-передача (Direct Memory Access)**: Вхідні масиви точок та скалярів у системній пам'яті повинні виділятися за допомогою `cudaHostAlloc` (Pinned Host Memory), що дозволяє досягти пікової швидкості копіювання по шині PCIe 4.0/5.0 (до 32–64 ГБ/с).
2. **Конфігурація сітки ядер (Grid & Block Layout)**:
   - Розмір блоку потоків: `threadsPerBlock = 256`.
   - Кількість блоків: `numBlocks = (n + threadsPerBlock - 1) / threadsPerBlock`.
   - Розподіл пам'яті Shared Memory на один мультипроцесор (SM): 48–96 КБ для локального накопичення кошиків.

:::tabs
```c
/* Конфігурація середовища виконання GPU CUDA */
typedef struct {
    int32_t device_id;         /* Ідентифікатор відеокарти (0, 1, ...) */
    void *cuda_stream;         /* Дескриптор потоку cudaStream_t */
    bool enable_p2p_access;    /* Дозволити прямий обмін між кількома GPU */
} msm_cuda_config_t;

/**
 * Ініціалізація GPU-контексту для кривої.
 */
msm_status_t msm_cuda_init_context(msm_cuda_config_t *cuda_cfg, msm_curve_id_t curve);

/**
 * Звільнення виділеної пам'яті на графічному процесорі.
 */
void msm_cuda_release_context(msm_cuda_config_t *cuda_cfg);
```
```cpp
namespace msm {

struct CudaConfig {
    int32_t device_id{0};
    void* cuda_stream{nullptr};
    bool enable_p2p_access{false};
};

class CudaContext {
public:
    explicit CudaContext(CudaConfig config, CurveId curve = CurveId::BN254);
    ~CudaContext();

    CudaContext(const CudaContext&) = delete;
    CudaContext& operator=(const CudaContext&) = delete;

    [[nodiscard]] Status synchronize() noexcept;
};

} // namespace msm
```
:::

## 9. Специфікація GLV-декомпозиції скалярів

Для еліптичних кривих з ефективним ендоморфізмом (зокрема, BN254 та secp256k1) API надає спеціалізовані методи для попередньої GLV-декомпозиції скалярів:

```
k_i = k_{i, 1} + k_{i, 2} · lambda \pmod r
```

Функція `msm_glv_decompose_scalars` розбиває вхідний масив із `n` скалярів на два масиви скалярів половинної довжини (по 128 бітів), після чого функція `msm_glv_execute` виконує розширене мультискалярне множення над базисом точок `P_i` та `phi(P_i)`.

:::tabs
```c
/**
 * Розклад масиву 256-бітних скалярів на дві половини за алгоритмом Бабая.
 * @param k1_out  Вихідний масив перших половин скалярів (128 бітів).
 * @param k2_out  Вихідний масив других половин скалярів (128 бітів).
 * @param scalars Вхідний масив 256-бітних скалярів розміром n.
 * @param n       Кількість скалярів.
 * @param curve   Ідентифікатор кривої.
 */
msm_status_t msm_glv_decompose_scalars(
    msm_fe256_t *k1_out,
    msm_fe256_t *k2_out,
    const msm_fe256_t *scalars,
    size_t n,
    msm_curve_id_t curve
);

/**
 * Виконання MSM з використанням попередньо обчисленого ендоморфізму GLV.
 */
msm_status_t msm_glv_execute(
    msm_point_jacobian_t *result,
    const msm_point_affine_t *points,
    const msm_fe256_t *k1,
    const msm_fe256_t *k2,
    size_t n,
    const msm_config_t *config
);
```
```cpp
namespace msm {

struct GlvDecomposedScalars {
    std::vector<FieldElement256> k1;
    std::vector<FieldElement256> k2;
};

/**
 * GLV-декомпозиція масиву скалярів.
 */
[[nodiscard]] std::expected<GlvDecomposedScalars, Status> glv_decompose_scalars(
    std::span<const FieldElement256> scalars,
    CurveId curve = CurveId::BN254
);

/**
 * Виконання комбінованого GLV-MSM.
 */
[[nodiscard]] std::expected<PointJacobian, Status> glv_execute(
    std::span<const PointAffine> points,
    std::span<const FieldElement256> k1,
    std::span<const FieldElement256> k2,
    const Config& config = Config{}
);

} // namespace msm
```
:::

## 10. Специфікація обчислень із фіксованим базисом (Fixed-Base MSM)

У багатьох сценаріях (наприклад, відкритий ключ довідника SRS або таблиця степенів генератора `G, [x]G, [x²]G, ...`) вхідний базис точок `P_1, ..., P_n` залишається незмінним для мільйонів послідовних доведень.

Рушій підтримує режим фіксованого базису (Fixed-Base MSM): функція `msm_fixed_base_table_create` один раз будує розширену таблицю кратних точок, що дозволяє зменшити кількість операцій додавання при кожному наступному виклику `msm_fixed_base_execute` у 2–3 рази.

:::tabs
```c
/* Контекст попередньо обчисленої таблиці фіксованого базису */
typedef struct msm_fixed_base_table msm_fixed_base_table_t;

/**
 * Створення таблиці попередніх обчислень для фіксованого набору точок.
 * @param points Масив точок базису розміром n.
 * @param n      Розмір базису.
 * @param window_size Ширина вікна попередніх обчислень (наприклад, 4 або 8 бітів).
 * @param curve  Ідентифікатор кривої.
 */
msm_fixed_base_table_t* msm_fixed_base_table_create(
    const msm_point_affine_t *points,
    size_t n,
    uint32_t window_size,
    msm_curve_id_t curve
);

/**
 * Прискорене обчислення MSM над фіксованим базисом.
 */
msm_status_t msm_fixed_base_execute(
    msm_point_jacobian_t *result,
    const msm_fixed_base_table_t *table,
    const msm_fe256_t *scalars,
    size_t n
);

/**
 * Звільнення пам'яті таблиці фіксованого базису.
 */
void msm_fixed_base_table_destroy(msm_fixed_base_table_t *table);
```
```cpp
namespace msm {

class FixedBaseTable {
public:
    explicit FixedBaseTable(
        std::span<const PointAffine> points,
        uint32_t window_size = 4,
        CurveId curve = CurveId::BN254
    );
    ~FixedBaseTable();

    FixedBaseTable(const FixedBaseTable&) = delete;
    FixedBaseTable& operator=(const FixedBaseTable&) = delete;

    FixedBaseTable(FixedBaseTable&&) noexcept = default;
    FixedBaseTable& operator=(FixedBaseTable&&) noexcept = default;

    [[nodiscard]] std::expected<PointJacobian, Status> execute(
        std::span<const FieldElement256> scalars
    ) const noexcept;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace msm
```
:::

## 11. Специфікація пакетного мульти-MSM (Batched Multi-MSM API)

У сучасних протоколах згортання (англ. *Folding Schemes*, зокрема Nova, SuperNova та Sangria) виникає потреба в одночасному обчисленні кількох незалежних мультискалярних множень `Q_1, ..., Q_K` над одним спільним набором точок базису `P_1, ..., P_n`:

```
Q_k = ∑_{i=1}^n s_{k, i} · P_i,   де k = 1, ..., K
```

Пакетний інтерфейс `msm_execute_batched` обробляє спільний базис точок за один прохід через пам'ять: точка `P_i` зчитується з оперативної пам'яті лише один раз і додається до відповідних кошиків усіх `K` незалежних задач. Це зменшує загальний трафік оперативної пам'яті у `K` разів, підвищуючи сумарну пропускну здатність системи на 70–85%.

:::tabs
```c
/**
 * Одночасне обчислення K незалежних мультискалярних множень над спільним базисом точок.
 * @param results    Масив із K вихідних точок у координатах Якобі.
 * @param points     Спільний масив із n афінних точок базису.
 * @param scalars_2d Двовимірний масив скалярів розміром K * n.
 * @param n          Кількість точок у базисі.
 * @param batch_size Кількість незалежних задач K.
 * @param config     Параметри конфігурації.
 */
msm_status_t msm_execute_batched(
    msm_point_jacobian_t *results,
    const msm_point_affine_t *points,
    const msm_fe256_t *scalars_2d,
    size_t n,
    size_t batch_size,
    const msm_config_t *config
);
```
```cpp
namespace msm {

/**
 * Пакетне виконання K мультискалярних множень над спільним базисом.
 */
[[nodiscard]] std::expected<std::vector<PointJacobian>, Status> execute_batched(
    std::span<const PointAffine> points,
    std::span<const std::vector<FieldElement256>> batch_scalars,
    const Config& config = Config{}
);

} // namespace msm
```
:::

## 12. Специфікація телеметрії та профілювання продуктивності

Для детального аналізу вузьких місць у конвеєрі доведень API надає інтерфейс збору апаратних метрик виконання. Структура `msm_telemetry_t` фіксує точний розподіл часу між фазами алгоритму Піппенджера, кількість виконаних операцій поля та показники утилізації пропускної здатності шини пам'яті.

:::tabs
```c
/* Структура метрик продуктивності виконання MSM */
typedef struct {
    double total_time_ms;          /* Загальний час виконання (мілісекунди) */
    double bucket_accum_time_ms;   /* Час заповнення кошиків (фаза 1) */
    double running_sum_time_ms;    /* Час зворотного зведення Running Sums (фаза 2) */
    double horner_time_ms;         /* Час міжвіконної агрегації Горнера (фаза 3) */
    uint64_t mixed_additions_cnt;  /* Кількість виконаних змішаних додавань */
    uint64_t jacobian_doublings_cnt;/* Кількість виконаних подвоєнь точок */
    double memory_bandwidth_gb_s;  /* Досягнута швидкість читання базису (ГБ/с) */
} msm_telemetry_t;

/**
 * Виконання MSM зі збором детальних метрик продуктивності.
 */
msm_status_t msm_execute_with_telemetry(
    msm_point_jacobian_t *result,
    const msm_point_affine_t *points,
    const msm_fe256_t *scalars,
    size_t n,
    const msm_config_t *config,
    msm_telemetry_t *telemetry
);
```
```cpp
namespace msm {

struct Telemetry {
    double total_time_ms{0.0};
    double bucket_accum_time_ms{0.0};
    double running_sum_time_ms{0.0};
    double horner_time_ms{0.0};
    uint64_t mixed_additions_cnt{0};
    uint64_t jacobian_doublings_cnt{0};
    double memory_bandwidth_gb_s{0.0};
};

struct ExecutionResult {
    PointJacobian point;
    Telemetry telemetry;
};

/**
 * Виконання MSM зі збором телеметрії.
 */
[[nodiscard]] std::expected<ExecutionResult, Status> execute_profiled(
    std::span<const PointAffine> points,
    std::span<const FieldElement256> scalars,
    const Config& config = Config{}
);

} // namespace msm
```
:::

## 13. Змінні оточення та налаштування конфігурації середовища

Поведінку рушія MSM під час виконання можна динамічно коригувати за допомогою стандартних змінних оточення операційної системи без потреби перекомпіляції бінарних модулів:

1. `MSM_NUM_THREADS`: Задає явну кількість робочих потоків пулу CPU (наприклад, `MSM_NUM_THREADS=32`). Якщо значення не задано, рушій автоматично виявляє кількість доступних логічних процесорів.
2. `MSM_FORCE_BACKEND`: Примусово вказує обчислювальний бекенд (`CPU_SCALAR`, `CPU_AVX512`, `GPU_CUDA`). Дозволяє вимкнути використання AVX-512 або GPU для діагностики та бенчмаркінгу.
3. `MSM_WINDOW_SIZE`: Перевизначає розмір вікна `c` (значення від 8 до 20). Корисно для ручного тюнінгу під специфічний розмір кешу процесора.
4. `MSM_RADIX_SORT`: Значення `0` або `1` — вмикає або вимикає попереднє сортування індексів за кошиками для аналізу впливу промахів кешу L3.
5. `MSM_CUDA_DEVICE_ID`: Задає числовий індекс цільового графічного адаптера (за замовчуванням `0`).

## 14. Інтерфейси сумісності з мовами вищого рівня (FFI Bindings)

C-сумісний інтерфейс `msm_execute` експортується як спільна динамічна бібліотека (`libmsm_engine.so` у Linux / `msm_engine.dll` у Windows) зі стандартною угодою про виклики `cdecl`.

Це дозволяє легко підключати рушій до високорівневих мов програмування:
* **Rust**: через декларацію `extern "C"` та генератор зв'язувань `bindgen` (пряма інтеграція з бібліотеками ARKworks та Bellman).
* **Go**: через механізм `cgo` (використовується в клієнтах Geth та бібліотеках прувінгу Gnark).
* **Python**: через модуль `ctypes` або розширення `cffi` для дослідницьких криптографічних прототипів.

## 15. Контракт інтеграції у верифікатори ZK-SNARK (Groth16 та PLONK)

У системах доведення з нульовим розголошенням рушій MSM виконує два принципово різних типи обчислень:

1. **Генерація доведення (Prover MSM)**: Масштабні задачі над базисом від `2¹⁶` до `2²⁶` точок. Тут критичною є пропускна здатність багатопотокового конвеєра Піппенджера, підтримка AVX-512 та ефективна утилізація L3-кешу.
2. **Верифікація доведення (Verifier MSM)**: Компактні лінійні комбінації над публічними входами розміром `l ≤ 100` точок (наприклад, обчислення точки зв'язування `∑_{i=0}^l v_i [L_i]` у верифікаторі Groth16). Для таких розмірностей оптимальним є вибір малого вікна `c = 4` або `c = 6` без запуску важкого пулу потоків, що мінімізує латентність відповіді валідатора смарт-контрактів.

## 16. Специфікація інтеграції з EVM Precompiles (EIP-196 та EIP-2537)

У віртуальній машині Ethereum (EVM) криптографічні операції над еліптичними кривими виконуються через спеціальні попередньо скомпільовані контракти (Precompiled Contracts):

1. **EIP-196 / EIP-197 (BN254)**:
   - Адреса `0x06`: Додавання точок у групі `G1` (газ: 150).
   - Адреса `0x07`: Скалярне множення точки `G1` (газ: 6000).
   - Адреса `0x08`: Перевірка спарювання (Pairing Check, газ: `45\,000 · k + 34\,000`).
2. **EIP-2537 (BLS12-381)**:
   - Адреса `0x0a`: Додавання точок `G1` (газ: 500).
   - Адреса `0x0b`: Скалярне множення точки `G1` (газ: 12000).
   - Адреса `0x0c`: Мультискалярне множення `G1 MSM` зі зниженою вартістю газу для великих `n`.

Рушій MSM надає сумісний бінарний адаптер `msm_evm_precompile_call`, який приймає сирий вхідний масив байтів calldata і записує результат у буфер returndata у суворій відповідності зі специфікаціями Ethereum.

:::tabs
```c
/**
 * Емуляція виклику EVM Precompile G1 MSM.
 * @param out_data   Буфер returndata (64 байти для BN254 або 96 байтів для BLS12-381).
 * @param in_data    Буфер calldata (послідовність пар точка || скаляр).
 * @param in_len     Розмір calldata у байтах.
 * @param curve      Ідентифікатор кривої.
 * @return 0 у разі успіху, ненульовий код помилки EVM revert.
 */
int32_t msm_evm_precompile_call(
    uint8_t *out_data,
    const uint8_t *in_data,
    size_t in_len,
    msm_curve_id_t curve
);
```
```cpp
namespace msm {

/**
 * Емуляція виклику EVM Precompile G1 MSM.
 */
[[nodiscard]] std::expected<std::vector<uint8_t>, Status> evm_precompile_call(
    std::span<const uint8_t> calldata,
    CurveId curve = CurveId::BN254
);

} // namespace msm
```
:::

## 17. Специфікація роботи з великими сторінками пам'яті (Hugepages)

Під час обробки масивів точок розмірністю понад `n = 2²⁰` стандартні 4-кілобайтні сторінки віртуальної пам'яті спричиняють часті промахи в буфері трансляції адрес (TLB, англ. *Translation Lookaside Buffer*). Це призводить до падіння швидкодії на 12–18%.

Рушій надає інтерфейс алокації базису точок у великих сторінках пам'яті Hugepages (2 МБ або 1 ГБ) через системні виклики `mmap` з прапорцем `MAP_HUGETLB` (Linux) або `VirtualAlloc` з `MEM_LARGE_PAGES` (Windows).

:::tabs
```c
/**
 * Виділення неперервного масиву точок з використанням Hugepages (2 МБ сторінки).
 * @param count Кількість точок базису.
 * @return Вказівник на вирівняну пам'ять або NULL у разі відсутності прав на Hugepages.
 */
msm_point_affine_t* msm_alloc_hugepages_points(size_t count);

/**
 * Звільнення пам'яті Hugepages.
 */
void msm_free_hugepages_points(msm_point_affine_t *ptr, size_t count);
```
```cpp
namespace msm {

/**
 * Алокатор точок на основі Hugepages.
 */
[[nodiscard]] std::unique_ptr<PointAffine[], void(*)(PointAffine*)> make_hugepage_points(size_t count);

} // namespace msm
```
:::

## 18. Специфікація оракульного тестування та валідації коректності

Для гарантії математичної точності та виявлення прихованих алгебраїчних помилок API включає функцію оракульної верифікації `msm_oracle_verify`. Вона зіставляє результат багатопотокового конвеєра з детермінованим наївним множенням методом «подвоєння-та-додавання» (Double-and-Add) над згенерованими випадковими псевдоскалярами.

:::tabs
```c
/**
 * Валідація результату MSM проти наївного еталонного оракула.
 * @return true, якщо координати точок повністю збігаються після приведення до афінної форми.
 */
bool msm_oracle_verify(
    const msm_point_jacobian_t *result,
    const msm_point_affine_t *points,
    const msm_fe256_t *scalars,
    size_t n,
    msm_curve_id_t curve
);
```
```cpp
namespace msm {

/**
 * Валідація результату MSM проти еталонного оракула.
 */
[[nodiscard]] bool verify_against_oracle(
    const PointJacobian& result,
    std::span<const PointAffine> points,
    std::span<const FieldElement256> scalars,
    CurveId curve = CurveId::BN254
) noexcept;

} // namespace msm
```
:::

## 19. Контракт пам'яті, вирівнювання та інваріанти виконання

При інтеграції рушія у виробничі криптографічні системи гарантуються такі архітектурні інваріанти:

1. **Незмінність вхідних даних (Immutability)**: Вхідні масиви `points` та `scalars` мають кваліфікатор `const` і залишаються незмінними протягом усього часу виконання.
2. **Потокобезпечність (Thread-Safety)**: Усі функції API є реентрабельними. Декілька потоків можуть одночасно викликати `msm_execute` над спільним базисом точок.
3. **Обробка нульових скалярів та нескінченності**: Точки з нульовими скалярами `k_i = 0` та точки на нескінченності автоматично ігноруються без виклику процедур додавання точок, що усуває ризик збоїв через ділення на нуль.
4. **Гарантія відсутності витоків пам'яті (Zero Leaks)**: Усі ресурси, виділені всередині рушія, гарантовано вивільняються при виході з функції (через ідіому RAII у C++ та парні виклики `free` у C).
5. **Вимоги до продуктивності (Latency & Throughput SLA)**: Для розмірності `n = 2²⁰` на кривій BN254 на сучасному 16-ядерному процесорі x86_64 час виконання операції `msm_execute` не повинен перевищувати 850 мілісекунд, а на прискорювачі NVIDIA RTX 4090 — не більше 45 мілісекунд.
6. **Вирівнювання пам'яті (Memory Alignment)**: Для забезпечення коректної роботи векторних інструкцій AVX-512 усі внутрішні буфери точок вирівнюються за межею 64 байти (`alignas(64)` у C++20 або `posix_memalign` у C).
7. **Тепловий пакет та енергоспоживання у дата-центрах**: При тривалому пакетному прувінгу рушій підтримує обмеження теплового пакета (TDP Clamping) через динамічне регулювання кількості активних потоків або затримок між пакетами для запобігання термальному троттлінгу процесорів (Thermal Throttling).
