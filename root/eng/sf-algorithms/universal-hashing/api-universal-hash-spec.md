# 📋 Специфікація інтерфейсу універсального хешування

Ця вставка містить формальну специфікацію програмного інтерфейсу (API) універсальних генераторів хеш-функцій, описує контракти методів, обмеження на параметри генерації зерен (seeds), семантику рехешування та гарантії безпеки виконання.

## 1. Архітектурний дизайн та філософія контракту

Програмний інтерфейс універсального хешування проектовано на основі чіткого розділення стану генератора випадкової хеш-функції та операції безпосереднього обчислення хеш-коду для вхідних даних. На відміну від класичних детермінованих хеш-функцій без стану, таких як MurmurHash або FNV-1a, універсальне хешування вимагає наявності захищеного контексту. Цей контекст ініціалізується під час створення екземпляра структури даних і зберігає випадково обрані коефіцієнти конкретної хеш-функції з 2-універсального сімейства.

Основними вимогами до архітектури даного API є забезпечення високої швидкості виконання обчислювальних операцій, гарантія покрокової потокобезпечності при паралельному доступі багатьох потоків виконання, підтримка прозорого рехешування при виявленні спроб атак, а також строга інкапсуляція внутрішнього стану для унеможливлення витоку зерен через сторонні канали вимірювання часу.

Контракт API розбивається на п'ять функціональних модулів:
1. **Модуль конфігурації та ініціалізації**: перевірка вхідних інваріантів, вибірка джерела криптографічної ентропії операційної системи та виділення пам'яті під контекст хешування.
2. **Модуль обчислення для скалярних типів**: високопродуктивне хешування 32-бітних та 64-бітних цілих чисел без виділення додаткової пам'яті.
3. **Модуль хешування векторів та байтових рядків**: обробка послідовностей довільної довжини за допомогою блокового поліноміального хешування або табуляції.
4. **Модуль моніторингу колізій та динамічного реседу (Reseeding)**: виявлення аномальних ланцюжків колізій та переініціалізація стану новими коефіцієнтами.
5. **Модуль деструкції та безпечного очищення пам'яті**: обнулення секретних зерен у пам'яті задля запобігання атак зчитування дампів (Core Dumps).

## 2. Специфікація типів даних та структур C API

У мові C інтерфейс виражається через непрозорий вказівник на структуру контексту `uh_context_t`, що забезпечує повну ізоляцію внутрішнього стану та сумісність із будь-якими динамічними компіляторами.

:::tabs
@tab C
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/**
 * @brief Перелік можливих статусових кодів помилок API хешування.
 */
typedef enum {
    UH_SUCCESS              =  0,  /**< Операція виконана успішно */
    UH_ERR_INVALID_PARAM    = -1,  /**< Некоректні параметри (нульові вказівники, m=0) */
    UH_ERR_ENTROPY_FAILURE  = -2,  /**< Помилка зчитування системного джерела ентропії */
    UH_ERR_OUT_OF_RANGE     = -3,  /**< Ключ перевищує допустимий простір U */
    UH_ERR_BAD_ALIGNMENT    = -4   /**< Невирівняна адреса буферу */
} uh_status_t;

/**
 * @brief Перелік доступних типів універсальних сімейств.
 */
typedef enum {
    UH_FAMILY_MODULAR_P61   = 1,   /**< Модульне сімейство над полем GF(2^61 - 1) */
    UH_FAMILY_MULTIPLY_SHIFT = 2,  /**< Множильно-зсувне сімейство Dietzfelbinger (mod 2^64) */
    UH_FAMILY_TABULATION_64  = 3   /**< Табульоване хешування (8x256 таблиці) */
} uh_family_type_t;

/**
 * @brief Структура конфігурації генератора універсальних хеш-функцій.
 */
typedef struct {
    uh_family_type_t family_type;  /**< Тип обраного сімейства */
    uint64_t num_buckets;          /**< Кількість бакетів (m). Для MultiplyShift має бути 2^M */
    uint64_t custom_seed;          /**< Явне зерно ентропії (якщо 0, зчитується з OS CSPRNG) */
    bool use_custom_seed;          /**< Прапор використання кастомного зерна */
} uh_config_t;

/**
 * @brief Непрозорий контекст екземпляра універсальної хеш-функції.
 */
typedef struct uh_context uh_context_t;

/**
 * @brief Створення та ініціалізація нового екземпляра хеш-функції.
 *
 * @param[out] ctx_out Вказівник на створений контекст.
 * @param[in]  config  Структура параметрів ініціалізації.
 * @return uh_status_t Статус виконання операції.
 */
uh_status_t uh_create(uh_context_t **ctx_out, const uh_config_t *config);

/**
 * @brief Обчислення 64-бітного хеш-коду для 64-бітного цілого ключа.
 *
 * @param[in]  ctx   Контекст хеш-функції.
 * @param[in]  key   Вхідне 64-бітне значення ключа.
 * @param[out] hash  Результат хешування у діапазоні [0 .. m-1].
 * @return uh_status_t Статус виконання.
 */
uh_status_t uh_hash_uint64(const uh_context_t *ctx, uint64_t key, uint64_t *hash);

/**
 * @brief Обчислення хеш-коду для послідовності байтів (рядка).
 *
 * @param[in]  ctx   Контекст хеш-функції.
 * @param[in]  data  Вказівник на байтовий масив.
 * @param[in]  len   Довжина масиву в байтах.
 * @param[out] hash  Результат хешування у діапазоні [0 .. m-1].
 * @return uh_status_t Статус виконання.
 */
uh_status_t uh_hash_bytes(const uh_context_t *ctx, const void *data, size_t len, uint64_t *hash);

/**
 * @brief Генерація нової випадкової хеш-функції з того ж сімейства (reseed).
 *
 * @param[in,out] ctx Контекст для оновлення параметрів.
 * @return uh_status_t Статус виконання.
 */
uh_status_t uh_reseed(uh_context_t *ctx);

/**
 * @brief Звільнення ресурсів контексту та безпечне очищення зерен.
 *
 * @param[in] ctx Контекст для знищення.
 */
void uh_destroy(uh_context_t *ctx);
```
@tab C++
```cpp
#include <cstdint>
#include <cstddef>
#include <system_error>
#include <expected>
#include <span>
#include <memory>
#include <concepts>
#include <string_view>

namespace universal_hashing {

enum class ErrorCode {
    Success = 0,
    InvalidParameter,
    EntropyFailure,
    OutOfRange,
    BadAlignment
};

class UniversalHashCategory : public std::error_category {
public:
    [[nodiscard]] const char* name() const noexcept override {
        return "universal_hashing";
    }
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<ErrorCode>(ev)) {
            case ErrorCode::Success: return "Success";
            case ErrorCode::InvalidParameter: return "Invalid parameter provided";
            case ErrorCode::EntropyFailure: return "Failed to acquire system entropy";
            case ErrorCode::OutOfRange: return "Key out of domain range";
            case ErrorCode::BadAlignment: return "Data buffer bad alignment";
            default: return "Unknown error";
        }
    }
};

inline const UniversalHashCategory& category() noexcept {
    static UniversalHashCategory cat;
    return cat;
}

inline std::error_code make_error_code(ErrorCode e) noexcept {
    return {static_cast<int>(e), category()};
}

enum class FamilyType {
    ModularP61,
    MultiplyShift,
    Tabulation64
};

struct Config {
    FamilyType family{FamilyType::MultiplyShift};
    uint64_t num_buckets{1024};
    uint64_t custom_seed{0};
    bool use_custom_seed{false};
};

class IUniversalHasher {
public:
    virtual ~IUniversalHasher() = default;

    [[nodiscard]] virtual uint64_t hash(uint64_t key) const noexcept = 0;
    [[nodiscard]] virtual uint64_t hash(std::span<const std::byte> data) const noexcept = 0;
    virtual std::error_code reseed() noexcept = 0;
    [[nodiscard]] virtual uint64_t num_buckets() const noexcept = 0;
};

using HasherPtr = std::unique_ptr<IUniversalHasher>;

[[nodiscard]] std::expected<HasherPtr, std::error_code> create_hasher(const Config& config) noexcept;

} // namespace universal_hashing
```
:::

## 3. Детальний аналіз інваріантів параметрів та контрактів методів

Розглянемо фундаментальні умови та обмеження, які гарантують працездатність API на системному рівні:

### 3.1. Метод створення контексту `uh_create` / `create_hasher`

Під час виклику методу створення система перевіряє наступні інваріанти конфігурації:
- **Значення `num_buckets` (кількість бакетів `m`)**: повинно бути строго більше за нуль (`m > 0`). Для сімейства `UH_FAMILY_MULTIPLY_SHIFT` вимагається, щоб `m` було ступенем двійки `m = 2ᴹ` (перевіряється через вираз `(m & (m - 1)) == 0`). У разі порушення цієї умови метод повертає код помилки `UH_ERR_INVALID_PARAM` (або `ErrorCode::InvalidParameter`).
- **Джерело ентропії (CSPRNG)**: якщо прапор `use_custom_seed` встановлено у значення `false`, система здійснює виклик системного генератора випадкових чисел:
  - На платформах Linux/Android: зчитування з `/dev/urandom` або системний виклик `getrandom()`.
  - На платформах Windows: виклик `BCryptGenRandom` з прапором `BCRYPT_USE_SYSTEM_PREFERRED_RNG`.
  Якщо системний генератор не відповідає або повертає помилку, метод повертає `UH_ERR_ENTROPY_FAILURE`.
- **Параметри зерен**:
  - Для модульного сімейства `H_{p,m}` параметр `a` гарантовано зсувається у діапазон `[1 .. p-1]` (значення `a = 0` є недопустимим, оскільки воно спрощує хеш-функцію до константи `h(x) = b mod m`).
  - Для множильно-зсувного сімейства параметр `a` модифікується побітовою операцією `a |= 1` для забезпечення непарності.

### 3.2. Метод обчислення хеш-коду `uh_hash_uint64` / `hash`

Даний метод є критичним за швидкістю і не виконує динамічного виділення пам'яті.
- **Вхідні дані**: 64-бітний ключ `key`.
- **Вихідні дані**: хеш-індекс `hash` у діапазоні `[0 .. m-1]`.
- **Потокобезпечність**: оскільки стан `uh_context_t` після ініціалізації не змінюється, виклик цього методу з різних потоків для одного і того ж контексту є повністю потокобезпечним без використання блокувань (lock-free / zero-overhead).

### 3.3. Процедура повторного вибору зерен `uh_reseed` / `reseed`

Процедура `reseed` застосовується для нейтралізації атак супротивника в режимі реального часу.
- **Тригери виклику**:
  1. Довжина будь-якого ланцюжка колізій у хеш-таблиці перевищує критичний поріг `K_THRESHOLD = 8`.
  2. Загальний коефіцієнт завантаження хеш-таблиці перевищує дозволений максимум `α > 1.5`.
- **Послідовність дій**:
  1. Зчитується нова порція ентропії із системного генератора CSPRNG.
  2. Оновлюються внутрішні коефіцієнти `a` та `b` контексту.
  3. Всі елементи хеш-таблиці перехешовуються за новими коефіцієнтами, а старі бакети очищаються.
- **Часова складність**: амортизована складність операції `reseed` на один елемент становить `O(1)`, проте разовий виклик потребує `O(n)` для переініціалізації всієї хеш-таблиці.

## 4. Специфікація обчислювальної складності та параметрів системних ресурсів

У нижченаведеній таблиці підсумовано параметри використання ресурсів центрального процесора та оперативної пам'яті для кожного реалізованого сімейства хеш-функцій.

| Сімейство хешування | Час ініціалізації `uh_create` | Час обчислення `uh_hash_uint64` | Обсяг пам'яті контексту | Інструкції CPU на один ключ | Потокобезпечність |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Modular Linear `GF(2⁶¹-1)`** | `O(1)` (16 байтів ентропії) | `O(1)` константний | 32 байти (`a, b, m, p`) | `IMUL`, `ADD`, `SHR`, `AND`, `MOD` | Повна (Read-only) |
| **Multiply-Shift (Dietzfelbinger)** | `O(1)` (8 байтів ентропії) | `O(1)` надшвидкий | 24 байти (`a, shift, mask`) | `IMUL` (64-біт), `SHR` (зсув) | Повна (Read-only) |
| **Simple Tabulation (64-bit)** | `O(1)` (2 КБ ентропії) | `O(1)` вибірка з кешу | 2048 байтів (8x256x8 B) | 8 вибірок з пам'яті, 7 `XOR` | Повна (Read-only) |

## 5. Гарантії безпеки виконання та захист від сторонніх каналів

Під час розробки високозахищених систем вимагається дотримання наступних інженерних норм:

1. **Очищення секретних зерен (Zeroization)**: Функція `uh_destroy` виконує не лише звільнення пам'яті `free()`, а й попередньо обнуляє вміст структури `uh_context_t` за допомогою виклику `explicit_bzero` або `SecureZeroMemory`. Це запобігає витоку секретних коефіцієнтів хешування у разі зчитування дампу пам'яті після аварійного завершення процесу.
2. **Захист від атак вимірювання часу (Timing Attack Resistance)**: Операції обчислення хешу для скалярних типів у модульному та множильно-зсувному сімействах виконуються за фіксовану кількість тактів процесора незалежно від значення вхідного ключа `key`. Відсутність розгалужень `if-else` та циклів у коді хешування унеможливлює вимірювання часу виконання для відновлення секретного зерна `a`.
3. **Обмеження доступу до стану (State Encapsulation)**: Зовнішній код не має прямого доступу до внутрішніх полів `a` та `b`. Будь-яка спроба зчитування зерен через сторонній API заборонена, що унеможливлює побудову супротивником логічної моделі хеш-функції.

## 6. Приклад клієнтського коду використання C та C++ API

Нижче наведено приклад інтеграції API у клієнтський код.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>

void client_example_c(void) {
    uh_config_t cfg = {
        .family_type = UH_FAMILY_MULTIPLY_SHIFT,
        .num_buckets = 2048,
        .use_custom_seed = false
    };

    uh_context_t *hasher = NULL;
    uh_status_t status = uh_create(&hasher, &cfg);
    if (status != UH_SUCCESS) {
        fprintf(stderr, "Помилка створення хешера: %d\n", status);
        return;
    }

    uint64_t key = 0xDEADBEEFCAFEBABEULL;
    uint64_t hash_val = 0;
    uh_hash_uint64(hasher, key, &hash_val);

    printf("Ключ 0x%llX -> Хеш-індекс: %llu\n", key, hash_val);

    uh_destroy(hasher);
}
```
@tab C++
```cpp
#include <iostream>

void client_example_cpp() {
    universal_hashing::Config cfg{
        .family = universal_hashing::FamilyType::MultiplyShift,
        .num_buckets = 2048,
        .use_custom_seed = false
    };

    auto hasher_res = universal_hashing::create_hasher(cfg);
    if (!hasher_res) {
        std::cerr << "Помилка створення хешера: " << hasher_res.error().message() << "\n";
        return;
    }

    const auto& hasher = *hasher_res;
    uint64_t key = 0xDEADBEEFCAFEBABEULL;
    uint64_t hash_val = hasher->hash(key);

    std::cout << "Ключ 0x" << std::hex << key << " -> Хеш-індекс: " << std::dec << hash_val << "\n";
}
```
:::

Один виклик методів створення контексту забезпечує просте інтегрування у виробничий код.
Взаємодія з клієнтським кодом відбувається через передачу конфігураційних структур та отримання валідних хеш-індексів. При використанні C++23 стандартного типом `std::expected` система гарантує безпечну обробку виняткових ситуацій без кидання винятків `throw`, що є важливим для авіонійного та вбудованого програмного забезпечення.
