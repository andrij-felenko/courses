# 📋 Інтерфейс бібліотеки LDPC-кодека

Цей документ містить повний довідник програмного інтерфейсу (API) високопродуктивної бібліотеки LDPC-кодування та декодування `libldpc`. Бібліотека надає C-сумісний ABI для системного та вбудованого програмування, а також ідіоматичний C++20 обгортковий інтерфейс для обробки потоків даних у сучасних телекомунікаційних застосунках, програмно-визначених радіосистемах (SDR) та флеш-контролерах.

## 1. Загальний огляд архітектури та принципи проєктування API

Бібліотека `libldpc` розроблена за принципом повної ізоляції стану, відсутності глобальних змінних та строгого дотримання модульності. Усі обчислення виконуються в контексті окремого об'єкта кодека (`ldpc_codec_t` у мові C або `class Codec` у мові C++), який утримує прекомпільовані списки суміжності графа Таннера, оптимізовані таблиці перестановок QC-LDPC та внутрішні робочі буфери для LLR-повідомлень.

Основними архітектурними принципами `libldpc` є:
1. **Стабільність ABI та C-сумісність:** Головний інтерфейс бібліотеки експортується як C-функції без спотворення імен (Name Mangling), що дозволяє використовувати її в проектах на мовах C, C++, Rust, Python, Go або Java через механізми FFI (Foreign Function Interface).
2. **Нульове копіювання даних (Zero-Copy):** Буфери інформаційних бітів та канальних LLR передаються через вказівники або `std::span`, що усуває зайві операції копіювання в пам'яті під час декодування високих потоків даних.
3. **Потокобезпека (Thread Safety):** Інтерфейс не має внутрішніх блокувань або взаємно виключних блокувальників (Mutexes). Якщо декілька потоків обробляють паралельні кадри, кожен потік створює власний екземпляр кодека або працює з окремим екземпляром контексту.
4. **Вирівнювання пам'яті під SIMD:** Усі внутрішні буфери повідомлень розраховані на 64-байтне вирівнювання (64-byte alignment), що є обов'язковою вимогою для прямих векторизованих інструкцій AVX-512 та ARM NEON.

При ініціалізації об'єкта кодека виконується преобчислення індексів суміжності для двочасткового графа. Це дозволяє уникнути будь-яких динамічних виділень пам'яті під час безпосереднього декодування кадрів, що є критично важливим для систем реального часу з жорсткими часовими обмеженнями (Hard Real-Time Systems).

## 2. Типи даних, переліки та константи

### 2.1. Перелік алгоритмів декодування (`ldpc_algo_t` / `Algorithm`)

Визначає математичний метод, який застосовується під час ітеративного декодування.

- `LDPC_ALGO_SUM_PRODUCT` (Sum-Product): Точний імовірнісний алгоритм з обчисленням функцій `tanh` та `arctanh`. Забезпечує максимальну теоретичну виправну спроможність, але є обчислювально найважчим. Рекомендується для еталонних програмних симуляцій та каналів із наднизьким SNR.
- `LDPC_ALGO_MIN_SUM` (Min-Sum): Простий та швидкий алгоритм, у якому нелінійні функції замінено на пошук мінімуму модулів входів. Зменшує складність обчислень у кілька разів. Ідеально підходить для високошвидкісних реалізацій на FPGA/ASIC.
- `LDPC_ALGO_NORMALIZED_MIN_SUM` (Normalized Min-Sum): Модифікація Min-Sum, у якій вихідне значення перевірочного вузла множиться на нормалізуючий коефіцієнт `norm_factor ∈ (0.7, 0.9)`. Компенсує системну переоцінку LLR, звужуючи програш відносно Sum-Product до менш ніж `0.05 дБ`. Є стандартом за замовчуванням у більшості промислових кодеків.
- `LDPC_ALGO_OFFSET_MIN_SUM` (Offset Min-Sum): Модифікація Min-Sum із відніманням константи зміщення `offset_factor`. Використовується в спеціалізованих контролерах SSD-накопичувачів.

:::tabs
```c
typedef enum {
    LDPC_ALGO_SUM_PRODUCT        = 0, /* Точний алгоритм Sum-Product (з викликом tanh/arctanh) */
    LDPC_ALGO_MIN_SUM            = 1, /* Базовий алгоритм Min-Sum (швидкий, наближений) */
    LDPC_ALGO_NORMALIZED_MIN_SUM = 2, /* Нормалізований Min-Sum (помножений на коефіцієнт γ) */
    LDPC_ALGO_OFFSET_MIN_SUM     = 3  /* Min-Sum зі зміщенням (Offset Min-Sum) */
} ldpc_algo_t;
```
```cpp
enum class Algorithm : std::uint8_t {
    SumProduct        = 0,
    MinSum            = 1,
    NormalizedMinSum  = 2,
    OffsetMinSum      = 3
};
```
:::

### 2.2. Коди повернення та статусів (`ldpc_status_t` / `Status`)

Перелік статусів, які повертаються функціями створення кодека, кодування та декодування.

- `LDPC_SUCCESS` (0): Операція виконана успішно. При декодуванні це означає, що синдром дорівнює нулю (`H · c^T = 0`), і всі помилки виправлено.
- `LDPC_ERROR_MAX_ITERATIONS` (-1): Досягнуто граничний ліміт ітерацій `max_iterations`, але синдром не дорівнює нулю. Вихідне кодове слово може містити невиправлені помилки.
- `LDPC_ERROR_INVALID_PARAM` (-2): Передано некоректні аргументи (наприклад, `NULL`-вказівник або негативну довжину буфера).
- `LDPC_ERROR_INVALID_MATRIX` (-3): Матриця `H` є дегенеративною або містить порожні рядки чи стовпці.
- `LDPC_ERROR_OUT_OF_MEMORY` (-4): Помилка виділення динамічної пам'яті в системній купі (Heap).
- `LDPC_ERROR_BUFFER_TOO_SMALL` (-5): Розмір наданого користувачем вихідного буфера є меншим за довжину кодового блоку.

:::tabs
```c
typedef enum {
    LDPC_SUCCESS                   =  0, /* Операцію виконано успішно; синдром дорівнює нулю */
    LDPC_ERROR_MAX_ITERATIONS      = -1, /* Досягнуто ліміт ітерацій; кодове слово містить помилки */
    LDPC_ERROR_INVALID_PARAM       = -2, /* Передано некоректні параметри або NULL-вказівник */
    LDPC_ERROR_INVALID_MATRIX      = -3, /* Матриця H не задовольняє вимогам LDPC */
    LDPC_ERROR_OUT_OF_MEMORY       = -4, /* Помилка виділення динамічної пам'яті */
    LDPC_ERROR_BUFFER_TOO_SMALL    = -5  /* Розмір вихідного буфера недостатній */
} ldpc_status_t;
```
```cpp
enum class Status : std::int8_t {
    Success                  =  0,
    ErrorMaxIterations       = -1,
    ErrorInvalidParam        = -2,
    ErrorInvalidMatrix       = -3,
    ErrorOutOfMemory         = -4,
    ErrorBufferTooSmall      = -5
};
```
:::

### 2.3. Конфігураційна структура (`ldpc_config_t` / `Config`)

Визначає параметри побудови матриці `H` та налаштування режиму декодера.

Поля конфігурації мають наступне призначення:
- `num_v`: Загальна кількість символьних вузлів `n` (довжина кодового слова у бітах).
- `num_c`: Кількість перевірочних вузлів `m` (кількість рядків у матриці `H`).
- `h_matrix`: Вказівник на плоский масив елементів `GF(2)` розміром `num_c * num_v` у форматі Row-Major.
- `algo`: Обраний алгоритм декодування з переліку `ldpc_algo_t`.
- `max_iterations`: Верхній ліміт ітерацій для одного кадру (типове значення від 20 до 50).
- `norm_factor`: Коефіцієнт нормалізації для `LDPC_ALGO_NORMALIZED_MIN_SUM` (за замовчуванням `0.8f`).
- `offset_factor`: Константа зміщення для `LDPC_ALGO_OFFSET_MIN_SUM` (за замовчуванням `0.15f`).
- `llr_clip_val`: Поріг насичення LLR для запобігання чисельному переповненню типу `float` (за замовчуванням `20.0f`).

:::tabs
```c
typedef struct {
    uint32_t num_v;             /* Загальна довжина кодового слова n (кількість VN) */
    uint32_t num_c;             /* Кількість перевірочних рівнянь m (кількість CN) */
    const uint8_t *h_matrix;    /* Плоский масив розміру (num_c * num_v) елементів GF(2) */
    
    ldpc_algo_t algo;           /* Обраний алгоритм декодування */
    uint32_t max_iterations;    /* Максимальна кількість ітерацій (за замовчуванням 50) */
    float norm_factor;          /* Множник для Normalized Min-Sum (типово 0.8f) */
    float offset_factor;        /* Зміщення для Offset Min-Sum (типово 0.15f) */
    float llr_clip_val;         /* Поріг насичення LLR для запобігання переповненню (типово 20.0f) */
} ldpc_config_t;
```
```cpp
struct Config {
    std::size_t num_v{0};
    std::size_t num_c{0};
    std::vector<std::uint8_t> h_matrix;
    Algorithm algo{Algorithm::NormalizedMinSum};
    std::uint32_t max_iterations{50};
    float norm_factor{0.8f};
    float offset_factor{0.15f};
    float llr_clip_val{20.0f};
};
```
:::

## 3. C-Інтерфейс (C API Header: `ldpc_codec.h`)

Нижче наведено заголовочний файл C API бібліотеки `libldpc`. Всі функції повертають статус `ldpc_status_t`, а вихідні дані заповнюються через передані вказівники.

:::tabs
```c
/* ldpc_codec.h — C API для бібліотеки libldpc */
#ifndef LDPC_CODEC_H
#define LDPC_CODEC_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Непрозорий тип контексту кодека */
typedef struct ldpc_codec_s ldpc_codec_t;

/**
 * @brief Створює екземпляр LDPC-кодека та ініціалізує внутрішні графи Таннера.
 * @param config Вказівник на структуру конфігурації.
 * @param[out] codec_out Вказівник для повернення створеного контексту.
 * @return LDPC_SUCCESS у разі успіху, або код помилки.
 */
ldpc_status_t ldpc_codec_create(const ldpc_config_t *config, ldpc_codec_t **codec_out);

/**
 * @brief Звільняє всі ресурси, виділені для екземпляра кодека.
 * @param codec Контекст кодека.
 */
void ldpc_codec_destroy(ldpc_codec_t *codec);

/**
 * @brief Виконує систематичне кодування інформаційного вектора u у кодове слово c.
 * @param codec Контекст кодека.
 * @param info_bits Вхідний масив інформаційних бітів довжиною (n - m).
 * @param info_len Довжина вхідного масиву бітів.
 * @param[out] codeword_out Вихідний буфер для кодового слова довжиною n бітів.
 * @param codeword_len Розмір вихідного бувера.
 * @return LDPC_SUCCESS у разі успіху.
 */
ldpc_status_t ldpc_encode(const ldpc_codec_t *codec, 
                          const uint8_t *info_bits, size_t info_len,
                          uint8_t *codeword_out, size_t codeword_len);

/**
 * @brief Виконує ітеративне декодування вектора LLR каналу.
 * @param codec Контекст кодека.
 * @param channel_llr Вхідний масив дробових LLR довжиною n.
 * @param llr_len Довжина масиву LLR.
 * @param[out] decoded_bits_out Вихідний буфер для виправлених бітів (n бітів).
 * @param bits_len Розмір вихідного буфера.
 * @param[out] iters_performed Необов'язковий вказівник для повернення кількості виконаних ітерацій.
 * @return LDPC_SUCCESS у разі збіжності синдрому, або LDPC_ERROR_MAX_ITERATIONS.
 */
ldpc_status_t ldpc_decode(ldpc_codec_t *codec,
                          const float *channel_llr, size_t llr_len,
                          uint8_t *decoded_bits_out, size_t bits_len,
                          uint32_t *iters_performed);

/**
 * @brief Динамічно змінює параметри декодування без перестворення графа.
 * @param codec Контекст кодека.
 * @param algo Новий алгоритм декодування.
 * @param max_iterations Новий ліміт ітерацій.
 * @return LDPC_SUCCESS або код помилки.
 */
ldpc_status_t ldpc_codec_set_params(ldpc_codec_t *codec, ldpc_algo_t algo, uint32_t max_iterations);

/**
 * @brief Повертає текстовий опис коду помилки.
 * @param status Код статусу.
 * @return Рядок C із текстовим описом.
 */
const char* ldpc_status_to_string(ldpc_status_t status);

#ifdef __cplusplus
}
#endif

#endif /* LDPC_CODEC_H */
```
```cpp
// ldpc_codec.hpp — Ідіоматична C++20 обгортка для бібліотеки libldpc
#pragma once

#include <span>
#include <vector>
#include <string>
#include <memory>
#include <optional>
#include <expected>
#include <cstdint>

namespace ldpc {

enum class Algorithm : std::uint8_t {
    SumProduct        = 0,
    MinSum            = 1,
    NormalizedMinSum  = 2,
    OffsetMinSum      = 3
};

enum class Status : std::int8_t {
    Success                  =  0,
    ErrorMaxIterations       = -1,
    ErrorInvalidParam        = -2,
    ErrorInvalidMatrix       = -3,
    ErrorOutOfMemory         = -4,
    ErrorBufferTooSmall      = -5
};

struct Config {
    std::size_t num_v{0};
    std::size_t num_c{0};
    std::vector<std::uint8_t> h_matrix;
    
    Algorithm algo{Algorithm::NormalizedMinSum};
    std::uint32_t max_iterations{50};
    float norm_factor{0.8f};
    float offset_factor{0.15f};
    float llr_clip_val{20.0f};
};

struct DecodeResult {
    std::vector<std::uint8_t> bits;
    std::uint32_t iterations_used{0};
};

class Codec {
public:
    // Фабричний метод створення об'єкта кодека через std::expected
    [[nodiscard]] static std::expected<Codec, Status> create(const Config& config);

    Codec(Codec&&) noexcept = default;
    Codec& operator=(Codec&&) noexcept = default;

    Codec(const Codec&) = delete;
    Codec& operator=(const Codec&) = delete;

    ~Codec() = default;

    // Метод кодування систематичного блоку
    [[nodiscard]] std::expected<std::vector<std::uint8_t>, Status> encode(
        std::span<const std::uint8_t> info_bits) const;

    // Метод ітеративного декодування LLR
    [[nodiscard]] std::expected<DecodeResult, Status> decode(
        std::span<const float> channel_llr) const;

    // Динамічне оновлення конфігурації
    Status set_parameters(Algorithm algo, std::uint32_t max_iterations) noexcept;

    [[nodiscard]] std::size_t codeword_length() const noexcept { return num_v_; }
    [[nodiscard]] std::size_t parity_length() const noexcept { return num_c_; }
    [[nodiscard]] std::size_t info_length() const noexcept { return num_v_ - num_c_; }

private:
    explicit Codec(const Config& config);

    std::size_t num_v_{0};
    std::size_t num_c_{0};
    Config config_;
    
    class Impl;
    std::unique_ptr<Impl> impl_; // Pimpl ідіома для збереження ABI
};

[[nodiscard]] inline std::string to_string(Status status) {
    switch (status) {
        case Status::Success: return "Success";
        case Status::ErrorMaxIterations: return "Max iterations reached without syndrome convergence";
        case Status::ErrorInvalidParam: return "Invalid input parameters or nullptr";
        case Status::ErrorInvalidMatrix: return "Invalid sparse parity-check H matrix";
        case Status::ErrorOutOfMemory: return "Out of memory allocation error";
        case Status::ErrorBufferTooSmall: return "Output buffer is too small";
        default: return "Unknown status code";
    }
}

} // namespace ldpc
```
:::

## 4. Детальний опис функцій та життєвого циклу об'єктів

### 4.1. Створення та ініціалізація кодека (`ldpc_codec_create` / `Codec::create`)

При виклику цієї функції відбувається валідація наданої перевірочної матриці `H`. Бібліотека сканує масив `h_matrix` розміром `num_c * num_v` та перевіряє наступні умови:
1. Матриця `H` не є дегенеративною (не містить повністю нульових рядків або стовпців).
2. Ступені кожного символьного та перевірочного вузла не перевищують допустимих меж.
3. Перевіряється відсутність паразитичних коротких циклів завдовжки 4 (Girth 4 Detection).

Після валідації будуються внутрішні списки суміжності для кожного перевірочного та символьного вузла, а також виділяється пам'ять під масиви повідомлень `msg_v2c` та `msg_c2v`. Пам'ять під списки ребер виділяється одним суцільним блоком, що виключає фрагментацію оперативної пам'яті.

У разі успіху створюється об'єкт кодека і повертається код `LDPC_SUCCESS`. Якщо пам'яті недостатньо, повертається `LDPC_ERROR_OUT_OF_MEMORY`.

### 4.2. Звільнення ресурсів (`ldpc_codec_destroy` / `Codec::~Codec`)

Функція `ldpc_codec_destroy` виділяє та звільняє всі внутрішні масиви графа Таннера та сам об'єкт `ldpc_codec_t`. При використанні C++20 обгортки `ldpc::Codec` знищення об'єкта виконується автоматично деструктором за принципом RAII при виході з області видимості.

### 4.3. Кодування даних (`ldpc_encode` / `Codec::encode`)

Функція прийняття рішення кодера бере на вхід масив інформаційних бітів `info_bits` довжиною `k = n - m`. Кодування виконується в систематичній формі: перші `k` бітів вихідного кодового слова `codeword_out` строго збігаються з вхідними бітами `info_bits`, а наступні `m` бітів обчислюються як паритетні біти перевірки на парність.

Якщо розмір вихідного буфера є меншим за `n`, функція негайно повертає статус `LDPC_ERROR_BUFFER_TOO_SMALL`.

Обчислення паритетних бітів спирається на структуру квазіциклічного розкладу `H = [A | B]`. Якщо підматриця `B` є нижньотрикутною, паритетні біти обчислюються прямою зворотною підстановкою за час `O(n)`.

### 4.4. Декодування зашумлених LLR (`ldpc_decode` / `Codec::decode`)

Головна робоча функція бібліотеки. Вона приймає масив аналогових LLR від радіоприймача `channel_llr` довжиною `n` бітів та виконує ітеративний обмін повідомленнями за обраним алгоритмом (Sum-Product, Min-Sum, Normalized Min-Sum).

Після кожної ітерації обчислюється синдром `s = H · ĉ^T (mod 2)`:
- Якщо `s == 0`, ітерації негайно припиняються, декодовані біти записуються в `decoded_bits_out`, а у вказівник `iters_performed` записується кількість фактично виконаних ітерацій. Функція повертає `LDPC_SUCCESS`.
- Якщо досягнуто `max_iterations` без збіжності синдрому, функція повертає `LDPC_ERROR_MAX_ITERATIONS`, записавши в `decoded_bits_out` найкраще поточне тверде рішення.

## 5. Приклади використання API у реальних програмах

Нижче наведено повні приклади використання C API та C++20 API у прикладних програмах.

:::tabs
```c
/* main.c — Приклад використання C API бібліотеки libldpc */
#include <stdio.h>
#include <stdlib.h>
#include "ldpc_codec.h"

int main(void) {
    /* Перевірочна матриця H (3x6) */
    const uint8_t h_mat[18] = {
        1, 1, 1, 0, 0, 0,
        0, 1, 0, 1, 1, 0,
        0, 0, 1, 0, 1, 1
    };

    ldpc_config_t cfg = {
        .num_v = 6,
        .num_c = 3,
        .h_matrix = h_mat,
        .algo = LDPC_ALGO_NORMALIZED_MIN_SUM,
        .max_iterations = 30,
        .norm_factor = 0.85f,
        .llr_clip_val = 15.0f
    };

    ldpc_codec_t *codec = NULL;
    ldpc_status_t st = ldpc_codec_create(&cfg, &codec);
    if (st != LDPC_SUCCESS) {
        fprintf(stderr, "Помилка створення кодека: %s\n", ldpc_status_to_string(st));
        return EXIT_FAILURE;
    }

    /* Інформаційні біти k = n - m = 6 - 3 = 3 */
    const uint8_t info_bits[3] = {1, 0, 1};
    uint8_t codeword[6] = {0};

    st = ldpc_encode(codec, info_bits, 3, codeword, 6);
    if (st != LDPC_SUCCESS) {
        fprintf(stderr, "Помилка кодування: %s\n", ldpc_status_to_string(st));
        ldpc_codec_destroy(codec);
        return EXIT_FAILURE;
    }

    /* Симуляція каналу з шумом: створення LLR (помилка у біті 1) */
    float rx_llr[6] = { -4.5f, +3.2f, -5.0f, +4.1f, +3.8f, -4.9f };

    uint8_t decoded[6] = {0};
    uint32_t iters = 0;
    st = ldpc_decode(codec, rx_llr, 6, decoded, 6, &iters);

    if (st == LDPC_SUCCESS) {
        printf("Успішне декодування за %u ітерацій!\n", iters);
        printf("Декодовані біти: ");
        for (int i = 0; i < 6; i++) {
            printf("%d ", decoded[i]);
        }
        printf("\n");
    } else {
        printf("Помилка декодування: %s\n", ldpc_status_to_string(st));
    }

    ldpc_codec_destroy(codec);
    return EXIT_SUCCESS;
}
```
```cpp
// main.cpp — Приклад використання C++20 API бібліотеки libldpc
#include <iostream>
#include <vector>
#include "ldpc_codec.hpp"

int main() {
    ldpc::Config cfg{
        .num_v = 6,
        .num_c = 3,
        .h_matrix = {
            1, 1, 1, 0, 0, 0,
            0, 1, 0, 1, 1, 0,
            0, 0, 1, 0, 1, 1
        },
        .algo = ldpc::Algorithm::NormalizedMinSum,
        .max_iterations = 30,
        .norm_factor = 0.85f
    };

    auto codec_result = ldpc::Codec::create(cfg);
    if (!codec_result.has_value()) {
        std::cerr << "Помилка створення кодека: " << ldpc::to_string(codec_result.error()) << '\n';
        return EXIT_FAILURE;
    }

    const auto& codec = codec_result.value();

    const std::vector<std::uint8_t> info_bits = {1, 0, 1};
    auto encode_res = codec.encode(info_bits);
    if (!encode_res) {
        std::cerr << "Помилка кодування\n";
        return EXIT_FAILURE;
    }

    // Симуляція зашумлених LLR від радіоприймача
    const std::vector<float> rx_llr = {-4.5f, +3.2f, -5.0f, +4.1f, +3.8f, -4.9f};

    auto decode_res = codec.decode(rx_llr);
    if (decode_res.has_value()) {
        const auto& result = decode_res.value();
        std::cout << "Успішно декодовано за " << result.iterations_used << " ітерацій!\n";
        std::cout << "Відновлені біти: ";
        for (auto b : result.bits) {
            std::cout << static_cast<int>(b) << ' ';
        }
        std::cout << '\n';
    } else {
        std::cout << "Декодування не збіглося: " << ldpc::to_string(decode_res.error()) << '\n';
    }

    return EXIT_SUCCESS;
}
```
:::

## 6. Налаштування під телекомунікаційні стандарти 5G NR, Wi-Fi 6 та DVB-S2X

Бібліотека `libldpc` розроблена для гнучкого застосування у різних стандартах зв'язку:

1. **Мобільний зв'язок 5G NR (3GPP TS 38.212):**
   Для роботи зі стандартами 5G NR конфігурація `ldpc_config_t` ініціалізується за допомогою однієї з двох базових матриць графа:
   - *Base Graph 1 (BG1):* Використовується для великих блоків (`n` до 8448 бітів) та високих швидкостей кодування (`R` від `1/3` до `22/24`). Матриця містить `m = 46` перевірочних рядків та `n = 68` стовпців у блоках зсуву `Z`.
   - *Base Graph 2 (BG2):* Використовується для малих блоків (`n` до 3840 бітів) та низьких швидкостей кодування (`R` від `1/5` до `2/3`).
   Параметр зсуву `Z` обирається з діапазону від 2 до 384, а підматриця розгортається у плоский масив `h_matrix`.

2. **Бездротові мережі Wi-Fi 6 / 7 (IEEE 802.11ax / 802.11be):**
   У стандарті Wi-Fi застосовуються три фіксовані довжини блоку: `n = 648`, `n = 1296` та `n = 1944` бітів. Співвідношення швидкостей кодування становить `1/2`, `2/3`, `3/4` та `5/6`. Матриця зсуву має розмір `Z = n / 24`. Оскільки латентність є критичною для бездротових пакетів, рекомендується встановлювати `max_iterations = 20` та використовувати нормалізований Min-Sum з `norm_factor = 0.75f`.

3. **Супутникове мовлення DVB-S2X:**
   У супутниковому мовленні використовуються великі кадри довжиною `n = 64800` бітів (Normal FECFRAME) або `n = 16200` бітів (Short FECFRAME). Оскільки сигнал із супутника часто знаходиться нижче рівня шуму, використовується точний алгоритм `LDPC_ALGO_SUM_PRODUCT` із кількістю ітерацій `max_iterations = 50`.

## 7. Рекомендації з інтеграції та інженерні застереження

1. **Динамічне масштабування параметрів:** У радіомодемах і розробці 5G протоколів налаштування каналу змінюються залежно від умов SNR. Замість перестворення об'єкта кодека функція `ldpc_codec_set_params` дозволяє динамічно зменшувати `max_iterations` при високому SNR для економії батареї або переключати алгоритм з Min-Sum на точний Sum-Product при зниженні рівня сигналу.
2. **LLR Clipping (Насичення LLR):** При передачі дуже сильних сигналів виникає ризик overflow у змішаних обчисленнях. Завжди налаштовуйте параметр `llr_clip_val = 15.0f` ... `20.0f` для автоматичного затискання амплітуди входів.
3. **Паралельна обробка пакетів:** При розробці мультипотокових обробників (наприклад, у конвеєрах GStreamer або модулях GNU Radio) рекомендується створювати окремий екземпляр `ldpc_codec_t` для кожного робочого потоку (Worker Thread). Це повністю виключає міжпотокові конфлікти за кеш пам'яті.
4. **Виділення пам'яті у сигнальних процесорах (DSP):** У вбудованих системах реального часу заборонено використовувати стандартний `malloc` під час обробки переривань. Усі екземпляри `ldpc_codec_t` мають створюватися під час фази ініціалізації системи (Boot/Startup Phase).
5. **Журналювання та діагностика:** Для відлагодження у процесі розробки рекомендується реєструвати кількість виконаних ітерацій. Якщо середнє значення ітерацій зростає з 4 до 25, це є вірним маркером погіршення стану фізичного радіоканалу або підвищення рівня завад.
